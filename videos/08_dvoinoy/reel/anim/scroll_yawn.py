"""Хук «Рилс тебе длинный?»: кот на диване зевает, а лента в телефоне листается рывками с первого кадра; на «дли́нный»
палец срывается в быстрый пролёт ленты, кот клюёт головой в зевке.

Владелец 26.10 по рилсу 07: «в самом начале чуть-чуть совсем динамичнее». Поэтому здесь движение с первого кадра
сразу в двух местах (лента уже на середине рывка, голова кота «дышит» зевком) и камера влетает резче: наезд 18 % за
0,25 с с маленьким перелётом и поворотом, в 07 было 12 % за 0,3 с без перелёта.

Рисунок один — gen/q1_sofa.png (1024×1536, координаты ниже ×2). Экран телефона на рисунке пустой и светлый: лента
рисуется кодом в плоском «экране» (карточки без букв: превью и две серые полоски) и кладётся перспективой в
четырёхугольник экрана, только на светлые пиксели — лапа, держащая телефон, и рамка остаются поверх. Кот — поле
смещений (squash_region), без вырезания.
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/q1_sofa.png"]
VERSION = 2
REEL_DIR = None

SCREEN = np.float32([(700, 1205), (870, 1193), (940, 1515), (776, 1550)])   # TL, TR, BR, BL экрана (×2), сняты по сетке
FEED_W, FEED_H = 340, 720                                                    # плоский экран ленты, px
CARD_H, CARD_GAP = 236, 18
HEAD = dict(center=(720, 860), axes=(300, 270), floor=1180)                  # голова и плечи: «клюёт» в зевке
_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    x2 = os.path.join(d, "q1_sofa_x2.png")
    if not os.path.exists(x2):
        import upscale
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = anim.paper_like(np.asarray(Image.open(x2).convert("RGB")).astype(np.float32))
    h, w = A.shape[:2]
    poly = np.zeros((h, w), np.uint8)
    cv2.fillPoly(poly, [SCREEN.astype(np.int32)], 1)
    lum = A.mean(axis=2)
    light = (lum > 200) & (A[..., 2] < A[..., 0] + 4)                       # светлый тёплый экран, не серая рамка
    m = (poly > 0) & light
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)
    head = np.zeros((h, w), np.float32)
    cv2.ellipse(head, HEAD["center"], HEAD["axes"], 0, 0, 360, 1.0, -1)
    head = cv2.GaussianBlur(head, (0, 0), 45)
    H = cv2.getPerspectiveTransform(np.float32([(0, 0), (FEED_W, 0), (FEED_W, FEED_H), (0, FEED_H)]), SCREEN)
    return dict(A=A, mask=mask, head=head, H=H, tint=A[m > 0].mean(axis=0) if m.any() else np.float32([250, 244, 228]))


def layers():
    global _L
    if _L is None:
        _L = prepare()
    return _L


def timing(ctx):
    w = ctx["words"]                                     # «Рилс тебе длинный?» — «длинный» последнее слово
    return dict(hit=w[-1][0] + 0.07)                     # ударное «и» первого слога «дли́нный»


FLICK = 0.36                                             # рывок пальца раз в 0.36 с: лента едет на карточку и встаёт


def scroll_at(t, T):
    """Сдвиг ленты (px плоского экрана): рывки на карточку; на ударе — пролёт на четыре карточки, потом реже."""
    step = CARD_H + CARD_GAP
    t0 = t + 0.12                                        # первый кадр — уже середина рывка
    hit = T["hit"]
    if t < hit:
        n, u = divmod(t0, FLICK)
        return step * (n + anim.EASE_OUT(min(1.0, u / 0.24)))
    n_hit = (hit + 0.12) // FLICK + 1
    th = t - hit
    fly = 4 * step * anim.EASE_OUT(min(1.0, th / 0.55))
    after = 0.0
    if th > 0.8:
        n2, u2 = divmod(th - 0.8, 0.7)
        after = step * (n2 + anim.EASE_OUT(min(1.0, u2 / 0.3)))
    return step * n_hit + fly + after


def draw_feed(off, tint):
    """Лента: карточки без букв — серое превью с треугольником «играть» и две полоски под ним."""
    bg = np.empty((FEED_H, FEED_W, 3), np.float32); bg[:] = tint
    step = CARD_H + CARD_GAP
    k0 = int(off // step) - 1
    for k in range(k0, k0 + 6):
        y = k * step - off + 10
        if y > FEED_H or y + CARD_H < 0:
            continue
        x0, x1 = 18, FEED_W - 18
        shade = 0.93 + 0.05 * ((k * 37) % 3) / 2
        cv2.rectangle(bg, (x0, int(y)), (x1, int(y + CARD_H)), (236, 231, 220), -1, cv2.LINE_AA)
        cv2.rectangle(bg, (x0 + 10, int(y + 10)), (x1 - 10, int(y + 150)), tuple(float(c * shade) for c in (150, 146, 140)), -1, cv2.LINE_AA)
        cx, cy = (x0 + x1) // 2, int(y + 80)
        cv2.fillPoly(bg, [np.int32([(cx - 16, cy - 20), (cx - 16, cy + 20), (cx + 20, cy)])], (250, 248, 242), cv2.LINE_AA)
        cv2.rectangle(bg, (x0 + 10, int(y + 168)), (x1 - 60, int(y + 184)), (170, 166, 158), -1, cv2.LINE_AA)
        cv2.rectangle(bg, (x0 + 10, int(y + 198)), (x1 - 120, int(y + 212)), (190, 186, 178), -1, cv2.LINE_AA)
        cv2.rectangle(bg, (x0, int(y)), (x1, int(y + CARD_H)), (60, 60, 66), 3, cv2.LINE_AA)
    return bg


def frame(t, ctx):
    L = layers(); T = timing(ctx); A = L["A"]
    hit = T["hit"]; th = t - hit
    # камера: резкий влёт с маленьким перелётом и поворотом — динамичнее, чем в 07 (владелец 26.10)
    snap = 1 / (1 + 0.18 * (1 - anim.SNAP(t / 0.25)))
    over = 1 + 0.022 * anim.spring(t - 0.25, freq=3.2, damping=0.45) if t >= 0.25 else 1.0
    cam = dict(dx=0.0, dy=0.0, zoom=snap * over, rot=-1.1 * (1 - anim.EASE_OUT(min(1.0, t / 0.4))))
    img = A.copy()
    # кот: зевок «дышит» с первого кадра, на ударе голова клюёт вниз и пружинит
    sq = 0.012 * math.sin(2 * math.pi * 1.6 * anim.on_twos(t))
    if th >= 0:
        sq += 0.09 * anim.spring(th, freq=3.4, damping=0.32)
    if abs(sq) > 0.001:
        img = anim.squash_region(img, L["head"], HEAD["floor"], HEAD["center"][0], 1 - sq, 1 + 0.4 * sq)
    # лента в телефоне
    off = scroll_at(t, T)
    v = abs(off - scroll_at(t - 1 / 30, T))              # px за кадр: смаз только когда лента летит
    feed = draw_feed(off, L["tint"])
    k = int(min(45, v * 0.6))
    if k >= 3:
        feed = cv2.blur(feed, (1, k))
    h, w = A.shape[:2]
    warped = cv2.warpPerspective(feed, L["H"], (w, h), flags=cv2.INTER_LINEAR)
    m = L["mask"][..., None]
    img = img * (1 - m) + warped * m
    if th >= 0:
        for spread, seed in (((180, 250), 21), ((290, 360), 22)):
            anim.impact_strokes(img, (820, 1180), anim.on_twos(max(0.0, th - 2 / 30)), r0=120, r1=230, n=3,
                                spread=spread, width=11, color=(24, 24, 26), seed=seed, life=0.3)
        if th >= 2 / 30:
            kk = math.exp(-(th - 2 / 30) / 0.12)
            cam["dx"] += 10 * kk * math.sin(th * 95); cam["dy"] += 13 * kk * math.cos(th * 77)
            cam["rot"] += 0.3 * kk * math.sin(th * 61)
    return img, cam
