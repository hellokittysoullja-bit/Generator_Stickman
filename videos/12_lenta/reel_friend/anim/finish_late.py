"""Хук «Все успели, а ты?» (версия для второго аккаунта): кот пришёл к финишу, а ленточка уже порвана, все ушли.

Рисунок один — gen/k1_finish.png (1024×1536, координаты ниже ×2). Хронометраж (голос с 0 с):
  0 – удар   обрывки финишной ленты колышутся на ветру (поворот у столба, на двойках), трое вдали уходят — чуть
             меньше и выше с каждым шагом, сверху падает запоздалое конфетти (на единицах, кружит) — праздник уже кончился;
  удар       ударный слог последнего слова «ты́»: кот сникает (squash_region, одно поле), штрихи удара у головы,
             тряска камеры; последний листок конфетти ложится у лап.
Камера — anim.hook_cam (стандарт 20)."""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/k1_finish.png"]
VERSION = 1   # подготовка слоёв; правка движения кэш не трогает
REEL_DIR = None

TAPE_L = dict(poly=[(282, 1360), (560, 1430), (835, 1590), (815, 1672), (560, 1655), (282, 1495)], pivot=(282, 1428))
TAPE_R = dict(poly=[(1768, 1330), (1500, 1395), (1100, 1560), (885, 1552), (948, 1682), (1250, 1625), (1768, 1505)],
              pivot=(1768, 1418))
POST_L, POST_R = 296, 1754                               # внутренние края столбов (×2, по сетке)
PEOPLE_BOX = (770, 1060, 1330, 1320)
CAT = dict(center=(1000, 2320), axes=(560, 520), floor=2740)
HEAD = (1100, 1880)
HIT_FRAC = 0.45
CONFETTI = [  # (x ×2, задержка, где ложится по y ×2, вращение): в окне плана (x 440–1610), сверху вниз на дальнюю
    # землю у ленты, мимо головы кота (голова 820–1450 по x выше y 1750) — не ложится на шерсть (лист 28.10)
    (560, -0.35, 1700, 1.6), (1540, -0.15, 1680, -1.2), (720, 0.25, 1560, 2.1), (1380, 0.6, 1560, -1.7),
    (500, 0.9, 1720, 1.3), (1500, 1.2, 1700, -2.0)]
CONF_TOP = 900
_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"finish_late_v{VERSION}.npz")
    if os.path.exists(p):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    import upscale
    x2 = os.path.join(d, "k1_finish_x2.png")
    if not os.path.exists(x2):
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = np.asarray(Image.open(x2).convert("RGB")).astype(np.float32)
    tl = anim.cut_polygon(A, TAPE_L["poly"])
    tr = anim.cut_polygon(A, TAPE_R["poly"])
    tl[:, :POST_L] = 0                                    # столбы остаются рисунку: обрывки — только между столбами
    tr[:, POST_R:] = 0
    people = anim.ink_objects(A, box=PEOPLE_BOX, min_area=1500)
    pm = np.zeros(A.shape[:2], np.uint8)
    for m in people:
        pm |= m
    hole = cv2.dilate(((tl | tr | pm) > 0).astype(np.uint8), np.ones((21, 21), np.uint8)) > 0
    bg = anim.fill_hole(A, hole, grain_from="noise", feather=2)
    A, bg = anim.paper_like(A), anim.paper_like(bg)
    out = dict(A=np.clip(A, 0, 255).astype(np.uint8), bg=np.clip(bg, 0, 255).astype(np.uint8),
               tl=tl.astype(np.uint8), tr=tr.astype(np.uint8), people=pm)
    np.savez(p, **out)
    return out


def _confetti(w, h, seed):
    """Листок конфетти тушью по бумаге, как на земле рисунка: серый прямоугольник с контуром."""
    rng = np.random.default_rng(seed)
    pad = 6
    W_, H_ = w + 2 * pad, h + 2 * pad
    a = np.zeros((H_, W_), np.float32); a[pad:pad + h, pad:pad + w] = 1
    # серый, как конфетти на земле рисунка (палитра: тёплое — только кот и огонёк)
    rgb = np.ones((H_, W_, 3), np.float32) * np.float32(rng.uniform(178, 200))
    line = np.zeros((H_, W_), np.float32)
    cv2.rectangle(line, (pad, pad), (pad + w, pad + h), 1.0, 3, cv2.LINE_AA)
    rgb = rgb * (1 - line[..., None]) + np.float32((28, 28, 30)) * line[..., None]
    return anim.Layer(rgb, np.clip(a + line, 0, 1), (W_ / 2, H_ / 2))


def layers():
    global _L
    if _L is None:
        d = prepare()
        tl = anim.Layer.cut(d["A"], d["tl"] > 0, pad=6, feather=1.0)
        tr = anim.Layer.cut(d["A"], d["tr"] > 0, pad=6, feather=1.0)
        for lay, t in ((tl, TAPE_L), (tr, TAPE_R)):       # опора — у столба, а не центр рамки
            lay.pivot = np.float32(t["pivot"]) - lay.origin
        pe = anim.Layer.cut(d["A"], d["people"] > 0, pad=6, feather=1.0)
        cat = np.zeros(d["A"].shape[:2], np.float32)
        cv2.ellipse(cat, CAT["center"], CAT["axes"], 0, 0, 360, 1.0, -1)
        conf = [_confetti(70 + 10 * (k % 3), 40 + 6 * (k % 2), k) for k in range(len(CONFETTI))]
        _L = dict(d=d, tl=tl, tr=tr, pe=pe, cat=cv2.GaussianBlur(cat, (0, 0), 45), conf=conf)
    return _L


def timing(ctx):
    w = ctx["words"]
    return dict(hit=w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]))


def frame(t, ctx):
    L = layers(); d = L["d"]; T = timing(ctx)
    cam = anim.hook_cam(t)
    th = t - T["hit"]
    img = d["bg"].astype(np.float32)
    if th >= 2 / 30:                                      # кот сникает от удара, одним полем
        sq = 0.06 * anim.spring(th - 2 / 30, freq=3.4, damping=0.35) + 0.03 * (1 - math.exp(-(th - 2 / 30) / 0.15))
        img = anim.squash_region(img, L["cat"], CAT["floor"], CAT["center"][0], 1 - sq, 1 + 0.35 * sq)
    tq = anim.on_twos(t)
    # трое уходят вдаль: с первого кадра чуть меньше и выше, шагом (покачивание на двойках)
    walk = 0.12 + t
    s = 1 - 0.05 * walk
    bob = 4 * abs(math.sin(2 * math.pi * 1.6 * tq))
    L["pe"].draw(img, L["pe"].home() + np.float32((0, -18 * walk - bob)), 0.0, sx=s, sy=s)
    # обрывки ленты колышутся у столбов (ветер, затухание нет — праздник кончился, а ветер остался)
    for lay, sgn, ph in ((L["tl"], -1, 0.0), (L["tr"], 1, 1.3)):
        ang = sgn * (2.4 * math.sin(2 * math.pi * 0.9 * tq + ph) + 1.0 * math.sin(2 * math.pi * 2.1 * tq + ph))
        lay.draw(img, lay.home(), ang)
    # запоздалое конфетти: падает сверху окна плана, кружит и ложится
    for k, (x, delay, land, spin) in enumerate(CONFETTI):
        u = t - delay
        if u < 0:
            continue
        dur = 1.1
        fall = land - CONF_TOP
        v = min(1.0, u / dur)
        y = CONF_TOP + fall * anim.gravity(v)
        xx = x + 60 * math.sin(2 * math.pi * 1.1 * v + k) * (1 - v)
        ang = 180 * spin * v + 20 * math.sin(2 * math.pi * 1.7 * v + k)
        flip = 1 - 0.7 * abs(math.sin(2 * math.pi * 1.4 * v + k)) * (1 - v)
        smear = None
        if v < 1:
            smear = (0.0, float(fall * (anim.gravity(min(1, (u + 1 / 30) / dur)) - anim.gravity(v)) * 0.5))
        fade = 1.0 - max(0.0, (v - 0.75) / 0.25)          # долетел до дальней земли — растаял, а не висит в воздухе
        if fade > 0:
            L["conf"][k].draw(img, (xx, y), ang, sx=1.0, sy=flip, smear=smear, opacity=fade)
    if th >= 0:
        for spread, seed in (((200, 260), 41), ((280, 340), 42)):
            anim.impact_strokes(img, HEAD, anim.on_twos(max(0.0, th - 2 / 30)), r0=170, r1=300, n=3,
                                spread=spread, width=12, color=(24, 24, 26), seed=seed, life=0.3)
        if th >= 2 / 30:
            kk = math.exp(-(th - 2 / 30) / 0.12)
            cam["dx"] += 10 * kk * math.sin(th * 95); cam["dy"] += 12 * kk * math.cos(th * 77)
            cam["rot"] += 0.3 * kk * math.sin(th * 61)
    return img, cam
