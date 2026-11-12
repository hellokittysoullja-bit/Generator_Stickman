"""Сборка кадров «Дима, 01:47»: мультиплан комнаты из проходов света + слои героев, numpy/OpenCV, поток в ffmpeg.

    python3 assemble.py anim  --passes DIR --chars DIR --out anim.mp4 [--frames 90] [--jobs 4]
    python3 assemble.py still --passes DIR --chars DIR --t 1.3 --out still.png
    python3 assemble.py check --passes DIR --full DIR/full.exr --t 1.3       # сумма проходов против полного рендера

Кадр t (всё в линейном цвете, альфа премультиплицирована):
  слой комнаты L = base_L + s(t)·screen_L + f(t)·flame_L, где s, f — timing.screen/flame;
  наезд: камера едет вперёд на d(t), слой на расстоянии D растёт в D/(D-d) раз вокруг оптической оси — так
  дальняя стена растёт медленнее дивана, а пол быстрее (параллакс); слои героев — на своих глубинах;
  тень героев: Дима заслоняет свет экрана, кот — свет огонька (маска из альфы слоя, раздутая от точки света
  и размытая), плюс мягкая контактная тень под всеми;
  затем свечение ярких мест (как Glare/Fog Glow компоновщика Blender), виньетка, sRGB.
"""
import json
import math
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timing  # noqa: E402

for extra in os.environ.get('NAPARNIK_PYLIB313', '').split(':'):
    if extra:
        sys.path.insert(0, extra)
import OpenEXR  # noqa: E402

W, H = 1080, 1920
ROOM = ('far', 'floor', 'sofa')            # снизу вверх
HEROES = ('L_dima', 'L_plaid', 'L_cat')    # снизу вверх, поверх комнаты
LIGHTS = ('base', 'screen', 'flame')


def read_exr(path):
    f = OpenEXR.File(path)
    ch = f.parts[0].channels
    if 'RGBA' in ch:
        a = ch['RGBA'].pixels
    else:
        a = np.dstack([ch[k].pixels for k in ('R', 'G', 'B', 'A')])
    return np.ascontiguousarray(a.astype(np.float32))


def srgb_to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


# ---------------------------------------------------------------- загрузка (один раз на процесс)

G = {}


def load(passes_dir, chars_dir):
    meta = json.load(open(os.path.join(passes_dir, 'passes.json')))
    over = meta['over']
    sig = 0.42 * over      # предфильтр под уменьшение в over раз (без лесенки и мерцания при наезде)
    room = {}
    for L in ROOM:
        lines = read_exr(os.path.join(passes_dir, L + '_lines.exr'))
        la = lines[..., 3:4]
        for p in LIGHTS:
            a = read_exr(os.path.join(passes_dir, '%s_%s.exr' % (L, p)))
            if p == 'base':
                a = lines + (1 - la) * a            # линии поверх света, как у Freestyle в полном кадре
            else:
                a[..., :3] *= (1 - la)              # свет экрана и огонька не высвечивает линии
                a[..., 3] = 0.0
            room[L, p] = cv2.GaussianBlur(a, (0, 0), sig)
    G.update(meta=meta, room=room, chars=chars_dir, over=over)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    e = ((xx - W / 2) / (0.62 * W)) ** 2 + ((yy - H * 0.47) / (0.60 * H)) ** 2
    G['vignette'] = (1 - 0.42 * np.clip((e - 0.55) / 0.9, 0, 1) ** 1.5)[..., None].astype(np.float32)


def init(passes_dir, chars_dir):
    cv2.setNumThreads(1)
    load(passes_dir, chars_dir)


# ---------------------------------------------------------------- геометрия наезда

def scale_for(depth, t):
    """Во сколько раз вырос слой на расстоянии depth, когда герои выросли в 1 + push(t)."""
    p = timing.push(t)
    dref = G['meta']['depths']['L_dima']
    d = dref * p / (1 + p)
    return depth / (depth - d)


def warp(img, k, src_scale, interp=cv2.INTER_LINEAR):
    px, py = G['meta']['principal_px']
    s = k / src_scale
    M = np.array([[s, 0, px * (1 - k)], [0, s, py * (1 - k)]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=interp, borderMode=cv2.BORDER_REPLICATE)


def warp_point(pt, k):
    px, py = G['meta']['principal_px']
    return (px + k * (pt[0] - px), py + k * (pt[1] - py))


# ---------------------------------------------------------------- герои

def hero(name, f):
    d = os.path.join(G['chars'], name)
    if not os.path.isdir(d):
        return None
    path = os.path.join(d, '%04d.png' % f)
    while not os.path.exists(path) and f > 0:      # заглушка: кадров может быть меньше
        f -= 1
        path = os.path.join(d, '%04d.png' % f)
    if not os.path.exists(path):
        return None
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    rgb = srgb_to_lin(im[..., 2::-1].astype(np.float32) / 255.0)
    a = im[..., 3:4].astype(np.float32) / 255.0
    return np.dstack([rgb * a, a]).astype(np.float32)


def shadow_from(alpha, light_px, grow, blur):
    """Тень слоя от точечного света: альфа, раздутая от точки света (дальше от света — шире), размытая."""
    lx, ly = light_px
    M = np.array([[grow, 0, lx * (1 - grow)], [0, grow, ly * (1 - grow)]], np.float32)
    m = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    return cv2.GaussianBlur(m, (0, 0), blur)


# ---------------------------------------------------------------- кадр

def room_stacks(t, ks=None):
    """Три стопки комнаты (base, screen, flame) в кадре 1080×1920, слои сложены по альфе base."""
    over = G['over']
    acc = {p: np.zeros((H, W, 3), np.float32) for p in LIGHTS}
    for L in ROOM:
        k = scale_for(G['meta']['depths'][L], t) if ks is None else ks
        b = warp(G['room'][L, 'base'], k, over)
        a = b[..., 3:4]
        for p in LIGHTS:
            c = b[..., :3] if p == 'base' else warp(G['room'][L, p], k, over)[..., :3]
            acc[p] = c + (1 - a) * acc[p]
    return acc


def frame(f, t=None, heroes=True, post=True, push_on=True):
    if t is None:
        t = f / timing.FPS
    tt = t if push_on else 0.0
    st = room_stacks(tt)
    s, fl = timing.screen(t), timing.flame(t)
    meta = G['meta']
    hs = {}
    if heroes:
        for n in HEROES:
            im = hero(n, f)
            if im is not None:
                hs[n] = warp(im, scale_for(meta['depths'][n], tt), 1.0, cv2.INTER_LANCZOS4)
                hs[n] = np.clip(hs[n], 0, None)
    screen_mul = flame_mul = base_mul = 1.0
    if 'L_dima' in hs:
        sp = warp_point(meta['screen_px'], scale_for(meta['depths']['L_dima'], tt))
        screen_mul = 1 - 0.85 * shadow_from(hs['L_dima'][..., 3], sp, 1.35, 16)[..., None]
    if 'L_cat' in hs:
        fp = warp_point(meta['flame_px'], scale_for(meta['depths']['L_cat'], tt))
        flame_mul = 1 - 0.85 * shadow_from(hs['L_cat'][..., 3], fp, 1.45, 12)[..., None]
    if hs:
        al = np.maximum.reduce([h[..., 3] for h in hs.values()])
        M = np.float32([[1, 0, -4], [0, 1, 16]])
        cont = cv2.GaussianBlur(cv2.warpAffine(al, M, (W, H), borderValue=0), (0, 0), 22)
        base_mul = 1 - 0.38 * cont[..., None]
    img = (st['base'] * base_mul + s * st['screen'] * screen_mul * base_mul
           + fl * st['flame'] * flame_mul * base_mul)
    for n in HEROES:
        if n in hs:
            h = hs[n]
            img = h[..., :3] + (1 - h[..., 3:4]) * img
    if post:
        bright = np.clip(img - 0.9, 0, None)
        small = cv2.resize(bright, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        g1 = cv2.GaussianBlur(small, (0, 0), 6)
        g2 = cv2.GaussianBlur(small, (0, 0), 22)
        glow = cv2.resize(0.6 * g1 + 0.9 * g2, (W, H), interpolation=cv2.INTER_LINEAR)
        img = img + 0.45 * glow
        img = img * G['vignette']
    return img


def to8(img):
    return (lin_to_srgb(img) * 255 + 0.5).astype(np.uint8)


def job(f):
    return f, to8(frame(f)).tobytes()


# ---------------------------------------------------------------- режимы

def main():
    argv = sys.argv[1:]
    mode = argv[0]

    def opt(n, d=None):
        return argv[argv.index(n) + 1] if n in argv else d
    passes = opt('--passes', os.path.join(HERE, 'passes'))
    chars = opt('--chars', os.path.join(HERE, 'chars'))
    if mode == 'still':
        load(passes, chars)
        t = float(opt('--t', '1.3'))
        f = int(round(t * timing.FPS))
        t0 = time.time()
        im = to8(frame(f, t))
        print('STILL %.2f s' % (time.time() - t0))
        cv2.imwrite(opt('--out', 'still.png'), im[..., ::-1])
    elif mode == 'check':
        load(passes, chars)
        t = float(opt('--t', '1.3'))
        ours = to8(frame(int(round(t * 30)), t, heroes=False, post=False, push_on=False)).astype(np.float32)
        full = read_exr(opt('--full'))
        full = cv2.resize(cv2.GaussianBlur(full, (0, 0), 0.42 * G['over']), (W, H), interpolation=cv2.INTER_LINEAR)
        ref = to8(full[..., :3]).astype(np.float32)
        d = np.abs(ours - ref)
        print('CHECK mean |diff| = %.3f /255, p99 = %.1f, max = %.0f, share >8: %.4f'
              % (d.mean(), np.percentile(d, 99), d.max(), (d.max(axis=2) > 8).mean()))
        dm = np.clip(d.max(axis=2) * 8, 0, 255).astype(np.uint8)
        cv2.imwrite(opt('--diff', 'check_diff.png'), dm)
    elif mode == 'anim':
        n = int(opt('--frames', '90'))
        jobs = int(opt('--jobs', str(os.cpu_count() or 4)))
        out = opt('--out', os.path.join(HERE, 'anim.mp4'))
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                               '-s', '%dx%d' % (W, H), '-framerate', str(timing.FPS), '-i', '-',
                               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', opt('--crf', '16'),
                               '-preset', 'slow', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
        t0 = time.time()
        with Pool(jobs, initializer=init, initargs=(passes, chars)) as pool:
            t1 = time.time()
            for f, buf in pool.imap(job, range(n), chunksize=1):
                ff.stdin.write(buf)
        ff.stdin.close()
        ff.wait()
        dt = time.time() - t1
        print('ANIM %d frames: load %.1f s, frames %.1f s (%.3f s/frame wall, %d jobs); forecast 1200 frames: %.1f min'
              % (n, t1 - t0, dt, dt / n, jobs, (dt / n * 1200 + (t1 - t0)) / 60))


if __name__ == '__main__':
    main()
