"""Хук «Тебе трудно решить?»: кот сидит на подушке перед телевизором, а сетка фильмов на экране листается рывками с
первого кадра — ряд за рядом, выбора всё больше; на «реши́ть» пульт срывается в быстрый пролёт на много рядов, кот
роняет голову и пружинит, лента крутится дальше без него.

Рисунок один — gen/v1_tv.png (1024×1536, координаты ниже ×2, сняты по сетке). Экран на рисунке — сетка пустых плашек:
она перерисовывается кодом в прямоугольнике экрана (плашки-«афиши» без букв: светлая рамка, серая картинка с горой и
солнцем, треугольник «играть»), рамка телевизора остаётся рисунком. Кот — поле смещений (squash_region). Камера —
anim.hook_cam (стандарт 20).
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/v1_tv.png"]
VERSION = 1
REEL_DIR = None

SCR = (166, 458, 1888, 1468)                       # внутренняя светлая часть экрана (×2): x0, y0, x1, y1
COLS, TILE_W, TILE_H, GAP_X, GAP_Y = 4, 376, 254, 40, 44
HEAD = dict(center=(1190, 1880), axes=(330, 300), floor=2420)   # голова и плечи кота
FLICK = 0.34                                        # рывок пульта: лента на ряд вниз раз в 0.34 с
_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    x2 = os.path.join(d, "v1_tv_x2.png")
    if not os.path.exists(x2):
        import upscale
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = anim.paper_like(np.asarray(Image.open(x2).convert("RGB")).astype(np.float32))
    h, w = A.shape[:2]
    x0, y0, x1, y1 = SCR
    scr = A[y0:y1, x0:x1]
    bg = np.median(scr.reshape(-1, 3), axis=0)                     # серый фон экрана между плашками
    tile = np.percentile(scr.reshape(-1, 3), 95, axis=0)           # светлая плашка
    head = np.zeros((h, w), np.float32)
    cv2.ellipse(head, HEAD["center"], HEAD["axes"], 0, 0, 360, 1.0, -1)
    head = cv2.GaussianBlur(head, (0, 0), 45)
    m = np.zeros((h, w), np.float32); m[y0:y1, x0:x1] = 1
    return dict(A=A, bg=bg.astype(np.float32), tile=tile.astype(np.float32), head=head,
                mask=cv2.GaussianBlur(m, (0, 0), 1.2)[..., None])


def layers():
    global _L
    if _L is None:
        _L = prepare()
    return _L


def timing(ctx):
    w = ctx["words"]                                     # «Тебе трудно решить?» — «решить» последнее слово
    return dict(hit=w[-1][0] + 0.45 * (w[-1][1] - w[-1][0]))   # ударное «и» второго слога «реши́ть»


def scroll_at(t, T):
    """Сдвиг сетки вверх (px экрана ×2): рывки на ряд; на ударе — пролёт на пять рядов, потом листается дальше реже."""
    step = TILE_H + GAP_Y
    t0 = t + 0.12                                        # первый кадр — уже середина рывка
    hit = T["hit"]
    if t < hit:
        n, u = divmod(t0, FLICK)
        return step * (n + anim.EASE_OUT(min(1.0, u / 0.22)))
    n_hit = (hit + 0.12) // FLICK + 1
    th = t - hit
    fly = 5 * step * anim.EASE_OUT(min(1.0, th / 0.6))
    after = 0.0
    if th > 0.85:
        n2, u2 = divmod(th - 0.85, 0.6)
        after = step * (n2 + anim.EASE_OUT(min(1.0, u2 / 0.28)))
    return step * n_hit + fly + after


def draw_grid(off, L):
    x0, y0, x1, y1 = SCR
    W, H = x1 - x0, y1 - y0
    img = np.empty((H, W, 3), np.float32); img[:] = L["bg"]
    step = TILE_H + GAP_Y
    left = (W - (COLS * TILE_W + (COLS - 1) * GAP_X)) // 2
    k0 = int(off // step) - 1
    for k in range(k0, k0 + 6):
        y = k * step - off + 70
        if y > H or y + TILE_H < 0:
            continue
        for c in range(COLS):
            x = left + c * (TILE_W + GAP_X)
            seed = (k * 7 + c * 13) % 5
            shade = 0.80 + 0.04 * seed
            cv2.rectangle(img, (x, int(y)), (x + TILE_W, int(y + TILE_H)), tuple(float(v) for v in L["tile"]), -1, cv2.LINE_AA)
            px0, py0, px1, py1 = x + 16, int(y + 16), x + TILE_W - 16, int(y + TILE_H - 16)
            cv2.rectangle(img, (px0, py0), (px1, py1), tuple(float(v * shade) for v in L["tile"]), -1, cv2.LINE_AA)
            hill = np.int32([(px0, py1), (px0 + 90 + 20 * seed, py0 + 110), (px0 + 190, py1 - 40), (px1 - 80, py0 + 90 + 10 * seed), (px1, py1)])
            cv2.fillPoly(img, [hill], tuple(float(v * (shade - 0.14)) for v in L["tile"]), cv2.LINE_AA)
            cv2.circle(img, (px1 - 50, py0 + 46), 22, tuple(float(v * (shade + 0.08)) for v in L["tile"]), -1, cv2.LINE_AA)
            cx, cy = (px0 + px1) // 2, (py0 + py1) // 2
            cv2.fillPoly(img, [np.int32([(cx - 22, cy - 28), (cx - 22, cy + 28), (cx + 30, cy)])], (250, 248, 242), cv2.LINE_AA)
            cv2.rectangle(img, (x, int(y)), (x + TILE_W, int(y + TILE_H)), (110, 110, 116), 4, cv2.LINE_AA)
    return img


def frame(t, ctx):
    L = layers(); T = timing(ctx); A = L["A"]
    hit = T["hit"]; th = t - hit
    cam = anim.hook_cam(t)
    img = A.copy()
    # кот: голова чуть клюёт в такт рывкам с первого кадра, на ударе роняет голову и пружинит
    sq = 0.010 * math.sin(2 * math.pi * 1.4 * anim.on_twos(t))
    if th >= 0:
        sq += 0.09 * anim.spring(th, freq=3.2, damping=0.33)
    if abs(sq) > 0.001:
        img = anim.squash_region(img, L["head"], HEAD["floor"], HEAD["center"][0], 1 - sq, 1 + 0.4 * sq)
    off = scroll_at(t, T)
    v = abs(off - scroll_at(t - 1 / 30, T))
    g = draw_grid(off, L)
    k = int(min(51, v * 0.5))
    if k >= 3:
        g = cv2.blur(g, (1, k))
    x0, y0, x1, y1 = SCR
    full = img.copy(); full[y0:y1, x0:x1] = g
    img = img * (1 - L["mask"]) + full * L["mask"]
    if th >= 0:
        for spread, seed in (((200, 260), 31), ((280, 340), 32)):
            anim.impact_strokes(img, (1200, 1820), anim.on_twos(max(0.0, th - 2 / 30)), r0=250, r1=380, n=3,
                                spread=spread, width=12, color=(24, 24, 26), seed=seed, life=0.3)
        img = anim.sweat_drop(img, (1430, 1740), max(0.0, th - 0.05), size=34, fall=100, life=0.85)
        if th >= 2 / 30:
            kk = math.exp(-(th - 2 / 30) / 0.12)
            cam["dx"] += 10 * kk * math.sin(th * 95); cam["dy"] += 13 * kk * math.cos(th * 77)
            cam["rot"] += 0.3 * kk * math.sin(th * 61)
    return img, cam
