"""Хук «Лежал и устал.»: сверху на лежащего кота падает тяжёлый конверт несделанного, удар — на «устал».

Рисунки: А — gen/u1_floor.png (кот лежит, устал; маленький конверт справа убирается — груз приходит сверху),
Б — gen/u4_envelope_on_back.png (конверт на спине, кот зажмурился, облачка пыли по бокам; тот же рисунок).
Слои снимаются один раз и лежат в кэше рилса (.cache/anim): конверт целиком (низ, спрятанный за шерстью,
достроен бумагой и контуром), облачка пыли, Б без облачек (под ними — пиксели А).

Хронометраж (от начала «Лежал», голос с 0 с):
  0 – вход    кот лежит и дышит (на двойках); на спине растёт тень того, что сейчас упадёт, — сначала тень, потом
              предмет (зритель ждёт удара раньше, чем видит конверт);
  вход – удар конверт влетает сверху: тяжесть (путь ∝ t²), доворот до своего угла, смаз позади (на единицах);
  удар        ударная гласная «устал»: Б; задержка на ударе 2 кадра; кот и конверт сплющиваются и отскакивают пружиной;
              облачка пыли вылетают из-под боков и тают; штрихи удара тушью; тряска камеры.
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/u1_floor.png", "gen/u4_envelope_on_back.png"]
VERSION = 7
REEL_DIR = None

# разметка (×2 к рисунку 1531 px)
ENV = np.float32([(412.5, 527.5), (902.5, 445), (1107.5, 617.5), (545, 665)]) * 2   # углы конверта на Б: Л, В, П, Н
FUR_OVER_ENV = [(600, 626), (690, 598), (800, 584), (1000, 584), (1100, 604), (1108, 618), (545, 668), (556, 650)]   # рисунок 1531 px
SMALL_ENV = (1170 * 2, 535 * 2, 1420 * 2, 620 * 2)       # маленький конверт на А (x0, y0, x1, y1)
PUFFS = [(150 * 2, 690 * 2, 330 * 2, 800 * 2), (1185 * 2, 640 * 2, 1350 * 2, 750 * 2)]   # облачка пыли на Б
FLOOR_Y = 830 * 2
DROP = 1150                                            # путь конверта до спины (×2): начинает чуть выше кадра
PUFF_SHIFT = [(400, 40), (-300, 60)]                   # облачка ближе к коту: вертикальный кадр уже рисунка
BODY = dict(center=(1320, 1380), axes=(1150, 420))      # кот с конвертом на Б: сплющивается от пола

_L = None


def _cache():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    return d


def _x2(rel):
    import upscale
    p = os.path.join(_cache(), os.path.basename(rel).replace(".png", "_x2.png"))
    if not os.path.exists(p):
        a = np.asarray(Image.open(os.path.join(REEL_DIR, rel)).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(p)
    return np.asarray(Image.open(p).convert("RGB")).astype(np.float32)


def _paper(img):
    """Бумага рисунка -> крем рилса (как prepare_src в reel.py), тем же цветом у обоих рисунков."""
    import canvas
    col, share = canvas.paper_color(img)
    return canvas.retint(img, col) if canvas.is_paper(col, share) else img


def prepare():
    p = os.path.join(_cache(), f"envelope_fall_v{VERSION}.npz")
    if os.path.exists(p):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    A = _x2(SOURCES[0]); B = _x2(SOURCES[1])
    H, W = A.shape[:2]
    # А без маленького конверта: бумага вокруг него, тем же зерном
    x0, y0, x1, y1 = SMALL_ENV
    ring = np.zeros((H, W), bool); ring[y0 - 30:y1 + 30, x0 - 30:x1 + 30] = True; ring[y0:y1, x0:x1] = False
    paper = np.median(A[ring], axis=0)
    hf = A - cv2.GaussianBlur(A, (0, 0), 2)
    clean_y = 60                                       # зерно чистой бумаги — с верхнего края листа, где ничего нет
    A[y0:y1, x0:x1] = paper + hf[clean_y:clean_y + (y1 - y0), x0:x1] * 0.9
    # конверт: четырёхугольник Б; что внутри него тёмное (шерсть перед нижним краем) — бумага конверта + контур
    quad = np.zeros((H, W), np.uint8); cv2.fillPoly(quad, [np.int32(ENV)], 1)
    L = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0]
    env_paper = np.median(B[(quad > 0) & (L > 200)], axis=0)
    # шерсть кота перед нижним краем конверта: узкая полоса вдоль края (снята по сетке); внутри неё всё не белое —
    # кончики шерсти, их место занимает бумага конверта. Кляксы и клапан лежат выше полосы и не трогаются.
    fur_band = np.zeros((H, W), np.uint8)
    cv2.fillPoly(fur_band, [np.int32(np.float32(FUR_OVER_ENV) * 2)], 1)
    left = np.zeros((H, W), bool); left[:, :690 * 2] = True        # слева в полосе клякса: тушь (L<45) остаётся
    hidden = (fur_band > 0) & (L < 215) & (~left | (L > 45))
    hidden = cv2.dilate(hidden.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    hidden &= quad > 0
    env = B.copy()
    hfB = B - cv2.GaussianBlur(B, (0, 0), 2)
    clean_hf = np.zeros_like(hfB); qy0 = int(ENV[:, 1].min()); qh = int(ENV[:, 1].max()) - qy0 + 40
    clean_hf[qy0 - 20:qy0 - 20 + qh] = hfB[60:60 + qh]                  # зерно чистой бумаги с верха листа
    env[hidden] = env_paper + clean_hf[hidden] * 0.6
    line = np.zeros((H, W), np.float32)
    cv2.polylines(line, [np.int32(ENV[[0, 3, 2]])], False, 1.0, 9, cv2.LINE_AA)
    line = cv2.GaussianBlur(line, (0, 0), 1.0) * hidden.astype(np.float32)
    env = env * (1 - line[..., None]) + np.float32([22, 22, 24]) * line[..., None]
    outer = np.zeros((H, W), np.uint8)
    c = ENV.mean(0); grown = c + (ENV - c) * 1.012
    cv2.fillPoly(outer, [np.int32(grown)], 1)
    env_a = cv2.GaussianBlur(outer.astype(np.float32), (0, 0), 1.0)
    # Б без облачек: под ними — пиксели А (рисунок тот же; там бумага, хвост и лапа)
    Bc = B.copy(); puff_m = np.zeros((H, W), np.float32)
    for (px0, py0, px1, py1) in PUFFS:
        Lr = L[py0:py1, px0:px1]
        lightgrey = (Lr > 150) & (Lr < 246)            # облачко — светло-серая заливка с серым контуром
        m = cv2.morphologyEx(lightgrey.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        keep = np.zeros_like(m)
        for k in range(1, n):
            if st[k, cv2.CC_STAT_AREA] > 1500: keep |= (lab == k).astype(np.uint8)
        keep = cv2.dilate(keep, np.ones((11, 11), np.uint8))
        puff_m[py0:py1, px0:px1] = np.maximum(puff_m[py0:py1, px0:px1], keep.astype(np.float32))
    puff_m = cv2.GaussianBlur(puff_m, (0, 0), 2.0)
    Bc = B * (1 - puff_m[..., None]) + A * puff_m[..., None]
    A, B, Bc, env = _paper(A), _paper(B), _paper(Bc), _paper(env)
    out = dict(A=np.clip(A, 0, 255).astype(np.uint8), B=np.clip(B, 0, 255).astype(np.uint8),
               Bc=np.clip(Bc, 0, 255).astype(np.uint8), env=np.clip(env, 0, 255).astype(np.uint8),
               env_a=env_a.astype(np.float32), puff_a=puff_m.astype(np.float32))
    np.savez(p, **out)
    return out


def layers():
    global _L
    if _L is None:
        d = prepare()
        env = anim.Layer.cut(d["env"], d["env_a"] > 0.02, pad=6, feather=0)
        x0, y0 = env.origin.astype(int); h, w = env.a.shape
        env.a = d["env_a"][y0:y0 + h, x0:x0 + w]
        env.pivot = np.float32(ENV.mean(0)) - env.origin
        puffs = []
        for (px0, py0, px1, py1) in PUFFS:
            m = np.zeros_like(d["puff_a"]); m[py0:py1, px0:px1] = d["puff_a"][py0:py1, px0:px1]
            lay = anim.Layer.cut(d["B"], m > 0.02, pad=4, feather=0)
            lx, ly = lay.origin.astype(int); lh, lw = lay.a.shape
            lay.a = m[ly:ly + lh, lx:lx + lw]
            # облачко растёт из-под бока кота: опора — край, ближний к телу
            side = 1.0 if (px0 + px1) / 2 > ENV[:, 0].mean() else 0.0
            lay.pivot = np.float32((lw * (1 - side), lh * 0.8))
            puffs.append((lay, -1 if side == 0 else 1))
        body = np.zeros(d["A"].shape[:2], np.float32)
        cv2.ellipse(body, tuple(map(int, BODY["center"])), tuple(map(int, BODY["axes"])), 0, 0, 360, 1.0, -1)
        _L = dict(d=d, env=env, puffs=puffs, body=cv2.GaussianBlur(body, (0, 0), 60))
    return _L


def timing(ctx):
    w = ctx["words"]                                   # «Лежал», «и», «устал.»
    hit = w[2][0] + 0.13                               # ударная «а» в «устал»
    return dict(shadow=0.05, enter=hit - 0.40, hit=hit)


def frame(t, ctx):
    Lr = layers(); d = Lr["d"]; T = timing(ctx)
    cam = dict(dx=0.0, dy=0.0, zoom=1.0, rot=0.0)
    cam["zoom"] *= 1 / (1 + 0.12 * (1 - anim.SNAP(t / 0.30)))   # резкий наезд с первого кадра
    env = Lr["env"]; home = env.home()
    if t < T["hit"]:
        tq = anim.on_twos(t)
        img = d["A"].astype(np.float32)
        br = 0.006 * math.sin(2 * math.pi * 0.7 * tq)       # дыхание усталого кота, на двойках
        img = anim.squash_region(img, Lr["body"], FLOOR_Y, BODY["center"][0], 1 + br, 1 - br * 0.4)
        # тень того, что падает: темнее и меньше по мере приближения
        u_s = anim.clamp01((t - T["shadow"]) / (T["hit"] - T["shadow"]))
        sh = np.zeros(img.shape[:2], np.float32)
        ax = (int(560 * (1.5 - 0.5 * u_s)), int(150 * (1.5 - 0.5 * u_s)))
        cv2.ellipse(sh, (int(home[0]), int(home[1] + 90)), ax, -6, 0, 360, 1.0, -1)
        sh = cv2.GaussianBlur(sh, (0, 0), 70 - 45 * u_s)
        img *= 1 - (0.12 + 0.30 * u_s ** 2) * u_s * sh[..., None]
        if t >= T["enter"]:                                 # конверт влетает сверху — на единицах
            u = anim.clamp01((t - T["enter"]) / (T["hit"] - T["enter"]))
            drop = DROP * (1 - anim.gravity(u))
            ang = -16 * (1 - anim.EASE_OUT(u))
            pos = home + (40 * (1 - u), -drop)
            v_prev = DROP * (1 - anim.gravity(max(0.0, u - 1 / 30 / (T["hit"] - T["enter"]))))
            env.draw(img, pos, ang, smear=(0.0, float(min(40.0, (v_prev - drop) * 0.5))))
        return img, cam
    th = t - T["hit"]
    tq = th if th < 0.2 else anim.on_twos(th)
    s = anim.spring(max(0.0, tq - 2 / 30), freq=4.0, damping=0.3)
    img = d["Bc"].astype(np.float32)
    if abs(s) > 0.002:
        img = anim.squash_region(img, Lr["body"], FLOOR_Y, BODY["center"][0], 1 - 0.09 * s, 1 + 0.05 * s)
    tp = anim.on_twos(max(0.0, th - 1 / 30))                # пыль: вылетает из-под боков, растёт, уходит, тает
    if tp < 0.7:
        g = anim.EASE_OUT(tp / 0.35)
        fade = 1 - anim.clamp01((tp - 0.2) / 0.5)
        for (lay, side), sh_ in zip(Lr["puffs"], PUFF_SHIFT):
            hp = lay.home() + sh_
            lay.draw(img, hp + (side * 90 * anim.EASE_OUT(tp / 0.6), -40 * anim.EASE_OUT(tp / 0.6)),
                     0.0, 0.5 + 0.9 * g, 0.5 + 0.9 * g, opacity=fade)
    for spread, seed in (((200, 245), 3), ((295, 340), 4)):
        anim.impact_strokes(img, (home[0], home[1] - 40), anim.on_twos(max(0.0, th - 2 / 30)), r0=360, r1=500, n=3,
                            spread=spread, width=16, color=(24, 24, 26), seed=seed, life=0.30)
    if th >= 2 / 30:
        k = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 14 * k * math.sin(th * 95); cam["dy"] += 18 * k * math.cos(th * 77)
        cam["rot"] += 0.4 * k * math.sin(th * 61)
    cam["zoom"] *= 1 + 0.06 * max(0.0, anim.spring(th, freq=3.0, damping=0.45)) + 0.03
    return img, cam
