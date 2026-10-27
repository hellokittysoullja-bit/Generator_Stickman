"""Хук «Все счастливее тебя?»: над котом всплывают чужие счастливые карточки (свадьба, пляж, кубок, торт, вершина),
лента не кончается; на «тебя́» карточки рвутся вверх, кубок бьёт в кадр, кот сникает.

Рисунок один — gen/l1_feed.png (1024×1536, координаты ниже ×2). Карточки лежат на чистой бумаге и вырезаются сами
(anim.ink_objects), фон под ними — бумага (anim.fill_hole). Хронометраж (голос с 0 с):
  0 – удар   карточки плывут вверх каждая со своей скоростью и покачиванием (на двойках) — лента идёт с первого кадра;
  удар       ударный слог последнего слова: карточки срываются вверх с разгоном, средняя (кубок) прыгает на зрителя
             пружиной, кот сникает (squash_region), штрихи удара у головы, тряска камеры;
Камера — anim.hook_cam (стандарт 20).
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/l1_feed.png"]
VERSION = 6
REEL_DIR = None

CARDS_BOX_Y = 1790                                       # карточки выше этой строки (×2), ухо кота ниже
SPLIT = ((1025, 1020), (610, 1430))                      # кубок и торт касаются углами — делятся по ближайшему центру
CAT = dict(center=(1020, 2330), axes=(430, 520), floor=2790)
HIT_FRAC = 0.45                                          # ударный слог последнего слова: «те-бя́»
_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"feed_float_v{VERSION}.npz")
    if os.path.exists(p):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    import upscale
    x2 = os.path.join(d, "l1_feed_x2.png")
    if not os.path.exists(x2):
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = np.asarray(Image.open(x2).convert("RGB")).astype(np.float32)
    raw = anim.ink_objects(A, box=(0, 0, A.shape[1], CARDS_BOX_Y), min_area=3000)
    big = [m.copy() for m in raw if m.sum() >= 40000]
    for m in raw:                                         # тонкая рамка карточки — отдельный мелкий кусок: к её картинке
        if m.sum() >= 40000:
            continue
        cy, cx = np.argwhere(m).mean(0)
        for b in big:
            x, y, w, h = cv2.boundingRect(b.astype(np.uint8))
            if x - 120 <= cx <= x + w + 120 and y - 120 <= cy <= y + h + 120:
                b |= m; break
    found = big
    cards = []
    ys, xs = np.mgrid[0:A.shape[0], 0:A.shape[1]]
    for m in found:
        pts = np.argwhere(m)
        if pts[:, 0].mean() > 1750:                       # кусок кота у края коробки — не карточка
            continue
        a, b = SPLIT
        if m[a[1], a[0]] or m[b[1], b[0]]:                # слипшиеся кубок и торт
            da = (xs - a[0]) ** 2 + (ys - a[1]) ** 2; db = (xs - b[0]) ** 2 + (ys - b[1]) ** 2
            cards += [(m & (da < db)).astype(np.uint8), (m & (da >= db)).astype(np.uint8)]
        else:
            cards.append(m)
    for k, m in enumerate(cards):                         # карточка целиком, с серой заливкой внутри контура
        cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        f = np.zeros_like(m, dtype=np.uint8); cv2.drawContours(f, [cv2.convexHull(np.vstack(cs))], -1, 1, -1)   # оболочка всех кусков: рамка + картинка
        cards[k] = (f > 0) | (m > 0)
    union = np.zeros(A.shape[:2], np.uint8)
    for m in cards: union |= m
    bg = anim.fill_hole(A, cv2.dilate(union, np.ones((45, 45), np.uint8)) > 0, grain_from="noise", feather=2)   # с тенью под карточкой
    A, bg = anim.paper_like(A), anim.paper_like(bg)
    out = dict(A=np.clip(A, 0, 255).astype(np.uint8), bg=np.clip(bg, 0, 255).astype(np.uint8))
    for i, m in enumerate(cards):
        out[f"card{i}"] = m.astype(np.uint8)
    np.savez(p, **out)
    return out


def layers():
    global _L
    if _L is None:
        d = prepare()
        cards = []
        for k in sorted(x for x in d if x.startswith("card")):
            m = d[k] > 0
            lay = anim.Layer.cut(d["A"], m, pad=6, feather=1.0)
            cards.append(dict(lay=lay, home=lay.home(), i=len(cards)))
        cards.sort(key=lambda c: c["home"][1])            # сверху вниз
        mid = min(cards, key=lambda c: abs(c["home"][0] - 1024) + 0.3 * abs(c["home"][1] - 1000))
        m = np.zeros(d["A"].shape[:2], np.float32)
        cv2.ellipse(m, CAT["center"], CAT["axes"], 0, 0, 360, 1.0, -1)
        _L = dict(d=d, cards=cards, mid=mid, cat=cv2.GaussianBlur(m, (0, 0), 45))
    return _L


def timing(ctx):
    w = ctx["words"]
    return dict(hit=w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]))


def card_pos(c, t, T):
    """Сдвиг карточки (px ×2) и поворот: плывёт вверх с первого кадра, на ударе срывается вверх с разгоном."""
    i = int(c["home"][0] // 450) + 2 * int(c["home"][1] // 700)   # куски одной карточки плывут вместе
    tq = anim.on_twos(t)
    v = 70 + 18 * (i % 3)                                 # px/с вверх
    dy = -v * (t + 0.15)                                  # первый кадр — уже в движении
    dx = 14 * math.sin(2 * math.pi * 0.7 * tq + i * 1.7)
    ang = 2.2 * math.sin(2 * math.pi * 0.5 * tq + i * 2.3)
    th = t - T["hit"]
    if th > 0:
        dy -= 900 * th * th + 160 * th                    # срыв вверх с разгоном
    return dx, dy, ang


def frame(t, ctx):
    L = layers(); d = L["d"]; T = timing(ctx)
    cam = anim.hook_cam(t)
    th = t - T["hit"]
    img = d["bg"].astype(np.float32)
    if th >= 2 / 30:                                      # кот сникает от удара, одним полем
        sq = 0.06 * anim.spring(th - 2 / 30, freq=3.4, damping=0.35) + 0.025 * (1 - math.exp(-(th - 2 / 30) / 0.15))
        img = anim.squash_region(img, L["cat"], CAT["floor"], CAT["center"][0], 1 - sq, 1 + 0.35 * sq)
    for c in L["cards"]:
        dx, dy, ang = card_pos(c, t, T)
        sc, smear = 1.0, None
        if c is L["mid"] and th > 0:                      # кубок прыгает на зрителя пружиной, остальные уходят вверх
            sc = 1.0 + 0.32 * anim.spring(th, freq=2.6, damping=0.45) + 0.12 * (1 - math.exp(-th / 0.2))
            dy = card_pos(c, T["hit"], T)[1]
        else:
            _, dy0, _ = card_pos(c, t - 1 / 30, T)
            if abs(dy - dy0) > 10:
                smear = (0.0, float(dy - dy0))
        c["lay"].draw(img, c["home"] + np.float32((dx, dy)), ang, sx=sc, sy=sc, smear=smear)
    if th >= 0:
        for spread, seed in (((200, 260), 31), ((280, 340), 32)):
            anim.impact_strokes(img, (1020, 1880), anim.on_twos(max(0.0, th - 2 / 30)), r0=150, r1=280, n=3,
                                spread=spread, width=12, color=(24, 24, 26), seed=seed, life=0.3)
        if th >= 2 / 30:
            kk = math.exp(-(th - 2 / 30) / 0.12)
            cam["dx"] += 10 * kk * math.sin(th * 95); cam["dy"] += 12 * kk * math.cos(th * 77)
            cam["rot"] += 0.3 * kk * math.sin(th * 61)
    return img, cam
