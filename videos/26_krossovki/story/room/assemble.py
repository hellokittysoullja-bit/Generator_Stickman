"""Клипы сцены room рилса 26 «кроссовки» (код — из рилсов 23–25): мультиплан комнаты из проходов света + слои героев, numpy/OpenCV → ffmpeg.

    python3 assemble.py clip  --id s01 [--passes DIR] [--chars DIR] [--jobs 4]      # → ../clips/<id>.mp4
    python3 assemble.py sheet --id s01 [--n 6]                                       # лист кадров клипа (PNG)
    python3 assemble.py check --full DIR/full.exr --t T                              # сумма проходов против полного рендера

Кадр k клипа = время ролика t = t0 − pad + k/30 (s01 — с 0, s18 — до end), см. shots.json.
Комната: слой L (far, floor, sofa) = base_L·тон + K_TV·tv(t)·tv_L + flame(t)·flame_L + K_LAMP·lamp(t)·lamp_L (timing24.py),
линии Freestyle в base. tv — ночью свет ноутбука на коленях (проход телевизора 23-го слабее + своё свечение экрана);
lamp — вечером тёплый торшер за кадром слева (свой проход Blender, passes.py), тон base вечером теплее и темнее.
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
from multiprocessing import get_context

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import timing26 as timing  # noqa: E402

for extra in os.environ.get('NAPARNIK_PYLIB313', '').split(':'):
    if extra:
        sys.path.insert(0, extra)
import OpenEXR  # noqa: E402

W, H = 1080, 1920
FPS = 30
ROOM = ('far', 'floor', 'sofa')
LIGHTS = ('base', 'tv', 'flame', 'lamp')
K_TV, K_LAMP = 0.30, 0.42
EVE_TONE = np.float32([0.70, 0.64, 0.62])   # вечер: лунный base тише, торшер ведёт
LAP_PX = (128, 1078)                         # центр экрана ноутбука (кадр 0)
LAMP_PX = (-260, 640)
DEFAULT_ORDER = ['L_dima', 'L_plaid', 'L_cat', 'L_fx']
DEPTH_DEFAULT = {'far': 4.25, 'sofa': 3.85, 'floor': 2.75, 'L_dima': 3.75, 'L_plaid': 3.33, 'L_cat': 3.42}
# запасные окна камеры, если SVG-агент не дал cameras.json: [cx, cy, h] на t0 и t1
CAM_DEFAULT = {
    's02': [[540, 1030, 1680], [532, 1040, 1580]],
    's05': [[846, 1032, 830], [846, 1020, 770]],
    's13': [[604, 1012, 1730], [600, 1018, 1660]],
    's17': [[764, 1052, 1170], [764, 1046, 1070]],
}
SHAKE = {}   # тряска: (время, амплитуда px выхода, затухание с, Гц)
CLOCK = {'s02': '2115', 's05': '2115', 's13': '2115', 's17': '2115'}
NIGHT_TONE = EVE_TONE
# свет огонька прохода — у сидящего кота 24-го (987, 934); в s02 кот сидит левее и выше (на голенях лежащего Димы)
FLAME_SHIFT = {'s02': (-92.0, -124.0)}   # = flame26l.json − (987, 934)


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


SEG = {'2': 'abged', '1': 'bc', '4': 'fgbc', '0': 'abcdef', '3': 'abgcd', '5': 'afgcd'}
CLOCK_X = (281, 334, 410, 463)      # левые края цифр часов на полке в пикселях прохода far_base (OVER 2.2)


def evening_clock(a, text='2140'):
    """Вечерние планы: часы на полке показывают 21:40, а не ночные 01:47 (сегменты стираются и рисуются заново
    той же геометрией и цветом, двоеточие остаётся)."""
    y0, y1, x0, x1 = 1066, 1164, 274, 512
    reg = a[y0:y1, x0:x1]
    lum = reg[..., 0]
    hot = cv2.dilate((lum > 0.03).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    hot[:, 385 - x0:404 - x0] = False                     # двоеточие
    bg = np.median(reg[~(lum > 0.03)][:, :3], axis=0)
    reg[hot, :3] = bg
    k = 4
    big = np.zeros(((y1 - y0) * k, (x1 - x0) * k), np.float32)
    H_ = {'a': (1074, 1082), 'g': (1110, 1118), 'd': (1147, 1155)}
    V_ = {'f': (0, 1084, 1108), 'e': (0, 1120, 1145), 'b': (34, 1084, 1108), 'c': (34, 1120, 1145)}
    for ch, dx in zip(text, CLOCK_X):
        for sgm in SEG[ch]:
            if sgm in H_:
                ya, yb = H_[sgm]
                xa, xb = dx + 9, dx + 33
            else:
                o, ya, yb = V_[sgm]
                xa, xb = dx + o, dx + o + 8
            cv2.rectangle(big, ((xa - x0) * k, (ya - y0) * k), ((xb + 1 - x0) * k - 1, (yb + 1 - y0) * k - 1), 1.0, -1)
    cov = cv2.resize(big, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)[..., None]
    reg[..., :3] = reg[..., :3] * (1 - cov) + cov * np.float32([8.94, 1.07, 0.54])
    a[y0:y1, x0:x1] = reg
    return a


def load(passes_dir, chars_dir, clip):
    meta = json.load(open(os.path.join(passes_dir, 'passes.json')))
    over = meta['over']
    room = {}
    for L in ROOM:
        lines = read_exr(os.path.join(passes_dir, L + '_lines.exr'))
        la = lines[..., 3:4]
        for p in LIGHTS:
            a = read_exr(os.path.join(passes_dir, '%s_%s.exr' % (L, p)))
            if L == 'far' and p == 'base':
                a = evening_clock(a, CLOCK[clip])
            if p == 'flame' and clip in FLAME_SHIFT and any(FLAME_SHIFT[clip]):
                # огонёк кота не там, где у прохода: сдвиг света прохода
                M_ = np.float32([[1, 0, FLAME_SHIFT[clip][0] * over], [0, 1, FLAME_SHIFT[clip][1] * over]])
                a = cv2.warpAffine(a, M_, (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            if p == 'lamp':
                a = a * K_LAMP
            if p == 'base':
                a = lines + (1 - la) * a
            elif p == 'tv':
                a = a * K_TV
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
    b = min(G['end'], s['t1'] + G['pad'])
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
            if L == 'floor' and p == 'tv':
                c = c * 0.55     # экран ТВ светит вперёд-вверх на диван; пол у его ножек (тапки) — слабее
            acc[p] = c + (1 - al) * acc[p]
    clip = G['clip']
    tv, fl, lamp = timing.tv(t, clip), timing.flame(t, clip), timing.lamp(t, clip)
    tone = EVE_TONE
    cdy = 0.0
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
    tv_mul = fl_mul = base_mul = lamp_mul = 1.0
    _, S = affine(G['depths']['L_dima'], t)
    blockers = [hs[n][..., 3] for n in ('L_dima', 'L_cat') if n in hs]
    if blockers:
        al = np.maximum.reduce(blockers)
        if tv > 0:
            # ноутбук спереди-слева и ниже лица: тень уходит вправо-вверх на спинку дивана
            sh = np.float32([[1, 0, 34 * S], [0, 1, -26 * S]])
            tv_mul = 1 - 0.80 * cv2.GaussianBlur(cv2.warpAffine(al, sh, (W, H), borderValue=0), (0, 0), 14 * S)[..., None]
        if lamp > 0:
            # торшер слева сверху: тень вправо-вниз, мягкая
            sh = np.float32([[1, 0, 46 * S], [0, 1, 22 * S]])
            lamp_mul = 1 - 0.72 * cv2.GaussianBlur(cv2.warpAffine(al, sh, (W, H), borderValue=0), (0, 0), 18 * S)[..., None]
    fpx = lay.get('flame_px', G['meta'].get('flame_px'))
    if fpx:
        fpx = (fpx[0], fpx[1] + cdy)
    if 'L_cat' in hs and fpx:
        fp = to_out(fpx, Ms['L_cat'])
        ca = hs['L_cat'][..., 3].copy()
        cv2.circle(ca, (int(fp[0]), int(fp[1])), int(46 * S), 0.0, -1)
        g = 1.45
        Mg = np.float32([[g, 0, fp[0] * (1 - g)], [0, g, fp[1] * (1 - g)]])
        fl_mul = 1 - 0.85 * cv2.GaussianBlur(cv2.warpAffine(ca, Mg, (W, H), borderValue=0), (0, 0), 12 * S)[..., None]
    if hs:
        # контактная тень; у прыгающего кота — его альфа, опущенная на пол, слабее с высотой
        parts = []
        for n, h_ in hs.items():
            if n == 'L_fx':
                continue
            a_ = h_[..., 3]
            if n == 'L_cat' and cdy < 0:
                a_ = cv2.warpAffine(a_, np.float32([[1, 0, 0], [0, 1, -cdy * Ms[n][1, 1]]]), (W, H), borderValue=0) * (1 + cdy / 220)
            parts.append(a_)
        al = np.maximum.reduce(parts)
        Mc = np.float32([[1, 0, -4 * S], [0, 1, 16 * S]])
        base_mul = 1 - 0.38 * cv2.GaussianBlur(cv2.warpAffine(al, Mc, (W, H), borderValue=0), (0, 0), 22 * S)[..., None]
    img = (acc['base'] * tone + tv * acc['tv'] * tv_mul + fl * acc['flame'] * fl_mul + lamp * acc['lamp'] * lamp_mul) * base_mul
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
    if False:
        # свечение экрана ноутбука: холодный ореол в воздухе вокруг экрана
        lp_ = to_out(LAP_PX, Ms['L_plaid'])
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) if 'grid' not in G else G['grid']
        G['grid'] = (yy, xx)
        r2 = ((xx - lp_[0]) ** 2 + (yy - lp_[1]) ** 2) / (S * S)
        glow = tv * (0.06 * np.exp(-r2 / (2 * 150.0 ** 2)) + 0.05 * np.exp(-r2 / (2 * 55.0 ** 2)))
        img += glow[..., None] * np.float32([0.55, 0.72, 1.0])
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
    passes = opt('--passes', os.environ.get('ROOM24_PASSES', '/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/blender/p24all'))
    chars = opt('--chars', os.path.join(HERE, 'chars'))
    clip = opt('--id', 's01')
    if mode == 'clip':
        sj = json.load(open(os.path.join(STORY, 'shots.json')))
        G.update(shot={x['id']: x for x in sj['shots']}[clip], pad=sj['pad'], end=sj['end'])
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
        # spawn, а не fork: OpenCV с потоками после fork зависает (так застрял первый прогон s01)
        with get_context('spawn').Pool(jobs, initializer=init, initargs=(passes, chars, clip)) as pool:
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
