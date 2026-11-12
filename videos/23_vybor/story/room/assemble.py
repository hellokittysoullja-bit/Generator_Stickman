"""Клипы сцены room рилса 23 «выбор»: мультиплан комнаты из проходов света + слои героев, numpy/OpenCV → ffmpeg.

    python3 assemble.py clip  --id s01 [--passes DIR] [--chars DIR] [--jobs 4]      # → ../clips/<id>.mp4
    python3 assemble.py sheet --id s01 [--n 6]                                       # лист кадров клипа (PNG)
    python3 assemble.py check --full DIR/full.exr --t T                              # сумма проходов против полного рендера

Кадр k клипа = время ролика t = t0 − pad + k/30 (s01 — с 0, s18 — до end), см. shots.json.
Комната: слой L (far, floor, sofa) = base_L + tv(t)·tv_L + flame(t)·flame_L (timing23.py), линии Freestyle в base.
Камера: окно [cx, cy, h] в пикселях кадра 0 (1080×1920) на t0 и t1 (cameras.json SVG-агента или CAM_DEFAULT ниже),
линейно по t (с продолжением в запасы pad). Окно уже/шире — это наезд: слой на расстоянии D масштабируется как при
движении камеры вперёд (D/(D−d)), поэтому стена отстаёт от дивана, а герои — от комнаты (параллакс).
Тени героев: Дима и кот заслоняют свет телевизора (маска альфы, сдвинутая от телевизора и размытая) и свет огонька
(альфа кота, раздутая от огонька), плюс мягкая контактная тень. Ореол огонька, свечение ярких мест, виньетка, sRGB.
Слои героев: chars/<id>/<слой>/NNNN.png (NNNN = k), в координатах кадра 0 с увеличением S (layout.json "scale",
по умолчанию по ширине PNG) и сдвигом "offset_px" (если отрисовано только окно).
"""
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, STORY)
import timing23 as timing  # noqa: E402

for extra in os.environ.get('NAPARNIK_PYLIB313', '').split(':'):
    if extra:
        sys.path.insert(0, extra)
import OpenEXR  # noqa: E402

W, H = 1080, 1920
FPS = 30
ROOM = ('far', 'floor', 'sofa')
LIGHTS = ('base', 'tv', 'flame')
DEFAULT_ORDER = ['L_dima', 'L_plaid', 'L_cat']
DEPTH_DEFAULT = {'far': 4.25, 'sofa': 3.85, 'floor': 2.75, 'L_dima': 3.75, 'L_plaid': 3.33, 'L_cat': 3.42}
# запасные окна камеры, если SVG-агент не дал cameras.json: [cx, cy, h] на t0 и t1
CAM_DEFAULT = {
    's01': [[540, 960, 1920], [470, 925, 1714]],
    's05': [[330, 860, 900], [345, 866, 860]],
    's06': [[880, 1010, 900], [880, 1005, 840]],
    's12': [[440, 950, 1350], [420, 925, 1150]],
    's13': [[320, 860, 820], [320, 860, 780]],
    's16': [[460, 1000, 1400], [455, 990, 1340]],
    's17': [[560, 980, 1920], [600, 990, 1700]],
    's18': [[880, 1010, 860], [880, 1010, 800]],
}
SHAKE = {'s13': [(20.56, 12.0, 0.4, 18.0)]}   # тряска: (время, амплитуда px выхода, затухание с, Гц)


def read_exr(path):
    ch = OpenEXR.File(path).parts[0].channels
    a = ch['RGBA'].pixels if 'RGBA' in ch else np.dstack([ch[k].pixels for k in 'RGBA'])
    return np.ascontiguousarray(a.astype(np.float32))


def srgb_to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


G = {}


def load(passes_dir, chars_dir, clip):
    meta = json.load(open(os.path.join(passes_dir, 'passes.json')))
    over = meta['over']
    room = {}
    for L in ROOM:
        lines = read_exr(os.path.join(passes_dir, L + '_lines.exr'))
        la = lines[..., 3:4]
        for p in LIGHTS:
            a = read_exr(os.path.join(passes_dir, '%s_%s.exr' % (L, p)))
            if p == 'base':
                a = lines + (1 - la) * a
            else:
                a[..., :3] *= (1 - la)
                a[..., 3] = 0.0
            room[L, p] = a
    shots = {s['id']: s for s in json.load(open(os.path.join(STORY, 'shots.json')))['shots']}
    sj = json.load(open(os.path.join(STORY, 'shots.json')))
    cdir = os.path.join(chars_dir, clip)
    lay = {}
    for f in (os.path.join(chars_dir, 'layout.json'), os.path.join(cdir, 'layout.json')):
        if os.path.exists(f):
            lay.update(json.load(open(f)))
    cams = dict(CAM_DEFAULT)
    shake = dict(SHAKE)
    for f in (os.path.join(HERE, 'cameras.json'), os.path.join(chars_dir, 'cameras.json'), os.path.join(cdir, 'cameras.json')):
        if os.path.exists(f):
            cj = json.load(open(f))
            for k_, v in cj.get('cameras', cj).items():
                if isinstance(v, dict) and 't0' in v:
                    cams[k_] = [v['t0'], v['t1']]
                    if 'shake' in v:
                        sh = v['shake']
                        shake[k_] = [(sh['at'], sh['amp_px'], sh.get('decay_s', 0.45), sh.get('hz', 17.0))]
    depths = dict(DEPTH_DEFAULT)
    depths.update(meta.get('depths', {}))
    depths.update(lay.get('depths', {}))
    G.update(shake=shake, meta=meta, room=room, over=over, chars=cdir, lay=lay, cams=cams, depths=depths,
             shot=shots[clip], pad=sj['pad'], end=sj['end'], clip=clip)
    # предфильтр проходов под самое сильное уменьшение в этом клипе (дешевле, чем размывать каждый кадр)
    smin = min(layer_scale(depths[L], c[2], cams[clip][0][2], depths['L_dima']) for L in ROOM for c in cams[clip]) / over
    if smin < 0.85:
        for key in room:
            room[key] = cv2.GaussianBlur(room[key], (0, 0), 0.42 / smin)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    e = ((xx - W / 2) / (0.62 * W)) ** 2 + ((yy - H * 0.47) / (0.60 * H)) ** 2
    G['vignette'] = (1 - 0.42 * np.clip((e - 0.55) / 0.9, 0, 1) ** 1.5)[..., None].astype(np.float32)


def init(passes_dir, chars_dir, clip):
    cv2.setNumThreads(1)
    load(passes_dir, chars_dir, clip)


def clip_range():
    s = G['shot']
    a = 0.0 if s['id'] == 's01' else s['t0'] - G['pad']
    b = G['end'] if s['id'] == 's18' else s['t1'] + G['pad']
    return a, int(round((b - a) * FPS))


# ---------------------------------------------------------------- камера

def window(t):
    s = G['shot']
    (c0x, c0y, h0), (c1x, c1y, h1) = G['cams'][s['id']]
    u = (t - s['t0']) / max(1e-6, s['t1'] - s['t0'])
    cx, cy, h = c0x + (c1x - c0x) * u, c0y + (c1y - c0y) * u, h0 * (h1 / h0) ** u
    for (ts, amp, dec, hz) in G['shake'].get(s['id'], []):
        dt = t - ts
        if 0 <= dt < dec:
            k = amp * (1 - dt / dec) ** 2 * h / H   # амплитуда — в пикселях выхода
            cx += k * np.sin(dt * 2 * np.pi * hz)
            cy += k * np.cos(dt * 2 * np.pi * hz * 0.73)
    return cx, cy, h, h0


def layer_scale(depth, h, h0, dref=None):
    """Масштаб слоя (выход/кадр 0): наезд камерой вперёд, опорная глубина — Дима."""
    r = h0 / h
    dref = dref or G['depths']['L_dima']
    d = dref * (r - 1) / r
    return (H / h0) * depth / (depth - d)


def affine(depth, t, src_scale=1.0, offset=(0.0, 0.0)):
    cx, cy, h, h0 = window(t)
    S = layer_scale(depth, h, h0)
    return np.array([[S / src_scale, 0, (offset[0] - cx) * S + W / 2],
                     [0, S / src_scale, (offset[1] - cy) * S + H / 2]], np.float32), S


def apply(img, M, interp=cv2.INTER_LINEAR, border=cv2.BORDER_REPLICATE):
    return cv2.warpAffine(img, M, (W, H), flags=interp, borderMode=border)


def to_out(pt, M):
    return (M[0, 0] * pt[0] + M[0, 2], M[1, 1] * pt[1] + M[1, 2])


# ---------------------------------------------------------------- герои

def hero(name, k):
    d = os.path.join(G['chars'], name)
    if not os.path.isdir(d):
        return None
    kk = k
    path = os.path.join(d, '%04d.png' % kk)
    while not os.path.exists(path) and kk > 0:
        kk -= 1
        path = os.path.join(d, '%04d.png' % kk)
    if not os.path.exists(path):
        return None
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    rgb = srgb_to_lin(im[..., 2::-1].astype(np.float32) / 255.0)
    a = im[..., 3:4].astype(np.float32) / 255.0
    return np.dstack([rgb * a, a]).astype(np.float32)


def frame(k, heroes=True, post=True, t=None):
    if t is None:
        a, _ = clip_range()
        t = a + k / FPS
    over = G['over']
    acc = {p: np.zeros((H, W, 3), np.float32) for p in LIGHTS}
    for L in ROOM:
        M, _ = affine(G['depths'][L], t, over)
        b = apply(G['room'][L, 'base'], M)
        al = b[..., 3:4]
        for p in LIGHTS:
            c = b[..., :3] if p == 'base' else apply(G['room'][L, p], M)[..., :3]
            acc[p] = c + (1 - al) * acc[p]
    tv, fl = timing.tv(t), timing.flame(t)
    lay = G['lay']
    hs, Ms = {}, {}
    if heroes:
        for n in lay.get('order', DEFAULT_ORDER):
            im = hero(n, k)
            if im is None:
                continue
            sc = lay.get('scale', {}).get(n) if isinstance(lay.get('scale'), dict) else lay.get('scale')
            sc = sc or im.shape[1] / W
            off = lay.get('offset_px', {}).get(n, (0, 0)) if isinstance(lay.get('offset_px'), dict) \
                else (lay.get('offset_px') or (0, 0))
            M, _ = affine(G['depths'].get(n, G['depths']['L_dima']), t, sc, off)
            Ms[n] = M
            hs[n] = np.clip(apply(im, M, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT), 0, None)
    tv_mul = fl_mul = base_mul = 1.0
    blockers = [hs[n][..., 3] for n in ('L_dima', 'L_cat') if n in hs]
    _, S = affine(G['depths']['L_dima'], t)
    if blockers:
        al = np.maximum.reduce(blockers)
        # телевизор спереди-слева и ниже глаз: тень уходит вправо-вверх на спинку и стену
        sh = np.float32([[1, 0, 34 * S], [0, 1, -26 * S]])
        tv_mul = 1 - 0.80 * cv2.GaussianBlur(cv2.warpAffine(al, sh, (W, H), borderValue=0), (0, 0), 14 * S)[..., None]
    fpx = lay.get('flame_px', G['meta'].get('flame_px'))
    if 'L_cat' in hs and fpx:
        fp = to_out(fpx, Ms['L_cat'])
        ca = hs['L_cat'][..., 3].copy()
        cv2.circle(ca, (int(fp[0]), int(fp[1])), int(46 * S), 0.0, -1)
        g = 1.45
        Mg = np.float32([[g, 0, fp[0] * (1 - g)], [0, g, fp[1] * (1 - g)]])
        fl_mul = 1 - 0.85 * cv2.GaussianBlur(cv2.warpAffine(ca, Mg, (W, H), borderValue=0), (0, 0), 12 * S)[..., None]
    if hs:
        al = np.maximum.reduce([h[..., 3] for h in hs.values()])
        Mc = np.float32([[1, 0, -4 * S], [0, 1, 16 * S]])
        base_mul = 1 - 0.38 * cv2.GaussianBlur(cv2.warpAffine(al, Mc, (W, H), borderValue=0), (0, 0), 22 * S)[..., None]
    img = (acc['base'] + tv * acc['tv'] * tv_mul + fl * acc['flame'] * fl_mul) * base_mul
    for n in lay.get('order', DEFAULT_ORDER):
        if n in hs:
            h_ = hs[n]
            img = h_[..., :3] + (1 - h_[..., 3:4]) * img
    if heroes and fpx and 'L_cat' in Ms:
        fp = to_out(fpx, Ms['L_cat'])
        R = int(260 * S)
        x0, y0 = int(fp[0]) - R, int(fp[1]) - R
        xs = np.arange(max(0, x0), min(W, x0 + 2 * R), dtype=np.float32)
        ys = np.arange(max(0, y0), min(H, y0 + 2 * R), dtype=np.float32)
        if len(xs) and len(ys):
            r2 = ((xs[None, :] - fp[0]) ** 2 + (ys[:, None] - fp[1]) ** 2) / (S * S)
            halo = fl * (0.10 * np.exp(-r2 / (2 * 70.0 ** 2)) + 0.22 * np.exp(-r2 / (2 * 22.0 ** 2)))
            img[int(ys[0]):int(ys[-1]) + 1, int(xs[0]):int(xs[-1]) + 1] += halo[..., None] * np.float32([1.0, 0.42, 0.10])
    if post:
        bright = np.clip(img - 0.9, 0, None)
        small = cv2.resize(bright, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        glow = cv2.resize(0.6 * cv2.GaussianBlur(small, (0, 0), 6) + 0.9 * cv2.GaussianBlur(small, (0, 0), 22),
                          (W, H), interpolation=cv2.INTER_LINEAR)
        img = (img + 0.45 * glow) * G['vignette']
    return img


def to8(img):
    return (lin_to_srgb(img) * 255 + 0.5).astype(np.uint8)


def job(k):
    return k, to8(frame(k)).tobytes()


def main():
    argv = sys.argv[1:]
    mode = argv[0]

    def opt(n, d=None):
        return argv[argv.index(n) + 1] if n in argv else d
    passes = opt('--passes', os.environ.get('ROOM23_PASSES', os.path.join(HERE, 'passes')))
    chars = opt('--chars', os.path.join(HERE, 'chars'))
    clip = opt('--id', 's01')
    if mode == 'clip':
        load(passes, chars, clip)
        a, n = clip_range()
        jobs = int(opt('--jobs', '4'))
        out = opt('--out', os.path.join(STORY, 'clips', clip + '.mp4'))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        G.clear()
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                               '-s', '%dx%d' % (W, H), '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264',
                               '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow', '-movflags', '+faststart', out],
                              stdin=subprocess.PIPE)
        t0 = time.time()
        with Pool(jobs, initializer=init, initargs=(passes, chars, clip)) as pool:
            for k, buf in pool.imap(job, range(n), chunksize=1):
                ff.stdin.write(buf)
        ff.stdin.close()
        ff.wait()
        dt = time.time() - t0
        print('CLIP %s: %d frames (t %.2f..%.2f) %.1f s, %.3f s/frame' % (clip, n, a, a + n / FPS, dt, dt / n))
    elif mode == 'sheet':
        load(passes, chars, clip)
        a, n = clip_range()
        m = int(opt('--n', '6'))
        ks = [int(round(i * (n - 1) / (m - 1))) for i in range(m)]
        ims = [cv2.resize(to8(frame(k)), (270, 480), interpolation=cv2.INTER_AREA) for k in ks]
        cv2.imwrite(opt('--out', os.path.join(HERE, 'sheet_%s.png' % clip)), np.hstack(ims)[..., ::-1])
        print('SHEET', clip, ['%.2f' % (a + k / FPS) for k in ks])
    elif mode == 'frame':
        load(passes, chars, clip)
        a, n = clip_range()
        t = float(opt('--t', str(a)))
        k = int(round((t - a) * FPS))
        cv2.imwrite(opt('--out', os.path.join(HERE, 'frame_%s.png' % clip)), to8(frame(k, t=t))[..., ::-1])
    elif mode == 'check':
        load(passes, chars, 's01')
        t = float(opt('--t', '1.0'))
        G['cams']['s01'] = [[540, 960, 1920], [540, 960, 1920]]
        ours = to8(frame(0, heroes=False, post=False, t=t)).astype(np.float32)
        full = read_exr(opt('--full'))
        full = cv2.resize(cv2.GaussianBlur(full, (0, 0), 0.42 * G['over']), (W, H), interpolation=cv2.INTER_LINEAR)
        ref = to8(full[..., :3]).astype(np.float32)
        d = np.abs(ours - ref)
        b = np.abs(cv2.GaussianBlur(ours, (0, 0), 3) - cv2.GaussianBlur(ref, (0, 0), 3))
        print('CHECK mean %.3f /255 (after 3px blur %.3f, signed %+.3f), p99 %.1f'
              % (d.mean(), b.mean(), (ours - ref).mean(), np.percentile(d, 99)))


if __name__ == '__main__':
    main()
