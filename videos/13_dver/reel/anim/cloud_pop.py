"""Хук «Ты шёл и всё забыл?» (рилс 13): кот застыл в дверном проёме, над ним облачко мысли — и на «забы́л» оно лопается.

Рисунок один — gen/d1_doorway.png (1024×1536, координаты ниже ×2, сетка anim.grid 28.10). Хронометраж (голос с 0 с):
  0 – удар   облачко дышит и покачивается (на двойках), пузырьки под ним подрагивают — мысль ещё есть;
  −0,12 с    облачко раздувается перед ударом (замах);
  удар       ударный слог «забы́л»: пузырьки гаснут, облачко лопается — обрывки контура тушью разлетаются и тают,
             штрихи «пуф» вокруг, кот вздрагивает (squash_region), камера трясётся.
Камера — anim.hook_cam (стандарт 20). Ничего из прошлых рилсов: свой рисунок, своё событие."""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/d1_doorway.png"]
VERSION = 6
REEL_DIR = None

CLOUD_BOX = (590, 740, 1340, 1335)          # облачко с запасом (×2)
BUBBLES_BOX = (960, 1320, 1070, 1480)       # два пузырька под облачком
CLOUD_C = (962, 1040)
CLEAN = (440, 260, 1360, 700)              # чистая стена проёма над облачком (×2): ни линий, ни пятен
CAT = dict(center=(1000, 2020), axes=(520, 560), floor=2540)
HIT_FRAC = 0.55                              # «за-бы́л»: ударный второй слог
PRE = 0.12
_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"cloud_pop_v{VERSION}.npz")
    if os.path.exists(p):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    import upscale
    x2 = os.path.join(d, "d1_doorway_x2.png")
    if not os.path.exists(x2):
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = np.asarray(Image.open(x2).convert("RGB")).astype(np.float32)
    cloud = np.zeros(A.shape[:2], np.uint8)
    for m in anim.ink_objects(A, box=CLOUD_BOX, min_area=20000):
        cloud |= m
    bub = np.zeros(A.shape[:2], np.uint8)
    for m in anim.ink_objects(A, box=BUBBLES_BOX, min_area=300):
        bub |= m
    # Дыра (облачко и пузырьки) заполняется куском заведомо чистой стены из верха проёма (CLEAN), отражённым до
    # нужного размера (лист 28.10: сдвиг зерна переносил в дыру верх облачка, шум давал рябое пятно).
    hole = cv2.dilate(((cloud | bub) > 0).astype(np.uint8), np.ones((27, 27), np.uint8)) > 0
    x0, y0, x1, y1 = CLEAN
    patch = A[y0:y1, x0:x1]
    ys, xs = np.where(hole)
    hy0, hy1, hx0, hx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    reps = (-(-(hy1 - hy0) // patch.shape[0]) + 1, -(-(hx1 - hx0) // patch.shape[1]) + 1)
    tile = np.concatenate([np.concatenate([patch if (i + j) % 2 == 0 else patch[::-1] for j in range(reps[1])], 1)
                           for i in range(reps[0])], 0)[:hy1 - hy0, :hx1 - hx0]
    ring = cv2.dilate(hole.astype(np.uint8), np.ones((41, 41), np.uint8)).astype(bool) & ~hole
    tile = tile + (np.median(A[ring], axis=0) - np.median(patch.reshape(-1, 3), axis=0))   # яркость — как стена вокруг
    Asw = A.copy()
    sub = Asw[hy0:hy1, hx0:hx1]
    m = hole[hy0:hy1, hx0:hx1]
    sub[m] = tile[m]
    # шов мягкий; anim.fill_hole здесь не годится: на дыре в 700 px его сглаживание делит почти на ноль и даёт пятно
    a = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 3)[..., None]
    bg = A * (1 - a) + Asw * a
    A, bg = anim.paper_like(A), anim.paper_like(bg)
    out = dict(A=np.clip(A, 0, 255).astype(np.uint8), bg=np.clip(bg, 0, 255).astype(np.uint8), cloud=cloud, bub=bub)
    np.savez(p, **out)
    return out


def layers():
    global _L
    if _L is None:
        d = prepare()
        cl = anim.Layer.cut(d["A"], d["cloud"] > 0, pad=8, feather=1.0)
        cl.pivot = np.float32(CLOUD_C) - cl.origin
        bub = anim.Layer.cut(d["A"], d["bub"] > 0, pad=6, feather=1.0)
        ink = np.median(d["A"][d["cloud"] > 0].reshape(-1, 3), axis=0) if (d["cloud"] > 0).any() else np.float32((20, 20, 22))
        cat = np.zeros(d["A"].shape[:2], np.float32)
        cv2.ellipse(cat, CAT["center"], CAT["axes"], 0, 0, 360, 1.0, -1)
        _L = dict(d=d, cl=cl, bub=bub, ink=np.float32(np.minimum(ink, 40)), cat=cv2.GaussianBlur(cat, (0, 0), 45))
    return _L


def timing(ctx):
    w = ctx["words"]
    return dict(hit=w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]))


def _shards(img, t, ink):
    """Обрывки контура облачка: дуги тушью разлетаются от центра и тают за 0,4 с."""
    if not 0 <= t < 0.4:
        return
    k = t / 0.4
    a = 1 - k
    rng = np.random.default_rng(13)
    for i in range(9):
        ang = 2 * math.pi * i / 9 + rng.uniform(-0.25, 0.25)
        r = 300 + 420 * anim.EASE_OUT(k) + rng.uniform(-40, 40)
        cx, cy = CLOUD_C[0] + r * math.cos(ang), CLOUD_C[1] + 0.75 * r * math.sin(ang)
        rad = int(70 * (1 - 0.5 * k) + rng.uniform(-10, 10))
        start = math.degrees(ang) + 90 + rng.uniform(-30, 30)
        lay = np.zeros(img.shape[:2], np.float32)
        x0, y0 = int(cx) - rad - 12, int(cy) - rad - 12
        if x0 < 0 or y0 < 0 or x0 + 2 * rad + 24 > img.shape[1] or y0 + 2 * rad + 24 > img.shape[0]:
            continue
        sub = lay[y0:y0 + 2 * rad + 24, x0:x0 + 2 * rad + 24]
        cv2.ellipse(sub, (rad + 12, rad + 12), (rad, rad), 0, start, start + 110, 1.0, 7, cv2.LINE_AA)
        sub = cv2.GaussianBlur(sub, (0, 0), 0.8) * a
        reg = img[y0:y0 + 2 * rad + 24, x0:x0 + 2 * rad + 24]
        reg[:] = reg * (1 - sub[..., None]) + ink * sub[..., None]


def frame(t, ctx):
    L = layers(); d = L["d"]; T = timing(ctx)
    cam = anim.hook_cam(t)
    th = t - T["hit"]
    img = d["bg"].astype(np.float32)
    if th >= 2 / 30:                                      # кот вздрагивает от «пуф», одним полем
        sq = 0.05 * anim.spring(th - 2 / 30, freq=3.6, damping=0.35) + 0.015 * (1 - math.exp(-(th - 2 / 30) / 0.15))
        img = anim.squash_region(img, L["cat"], CAT["floor"], CAT["center"][0], 1 - sq, 1 + 0.35 * sq)
    tq = anim.on_twos(t)
    if th < 0:
        # мысль ещё есть: облачко дышит и покачивается, пузырьки подрагивают; перед ударом — раздувается
        pre = anim.EASE_IO(min(1.0, max(0.0, (th + PRE) / PRE)))
        s = 1 + 0.05 * math.sin(2 * math.pi * 1.3 * tq + 0.6) + 0.13 * pre
        dy = -18 * math.sin(2 * math.pi * 0.8 * tq + 0.4)
        ang = 1.6 * math.sin(2 * math.pi * 0.6 * tq + 1.0)
        L["bub"].draw(img, L["bub"].home() + np.float32((0, 5 * math.sin(2 * math.pi * 1.7 * tq))))
        L["cl"].draw(img, L["cl"].home() + np.float32((0, dy)), ang, sx=s, sy=s * (1 - 0.03 * pre))
    else:
        _shards(img, anim.on_twos(th) if th > 0.12 else th, L["ink"])
        for spread, seed in (((200, 260), 51), ((280, 340), 52)):
            anim.impact_strokes(img, CLOUD_C, anim.on_twos(max(0.0, th)), r0=360, r1=520, n=4,
                                spread=spread, width=12, color=(24, 24, 26), seed=seed, life=0.3)
        if th >= 2 / 30:
            kk = math.exp(-(th - 2 / 30) / 0.12)
            cam["dx"] += 10 * kk * math.sin(th * 95); cam["dy"] += 12 * kk * math.cos(th * 77)
            cam["rot"] += 0.3 * kk * math.sin(th * 61)
    return img, cam
