"""Хук «Веришь в «потом»?»: башня из карточек «потом» уже качается, кот тянется положить ещё одну, и на «по́том»
верхние карточки срываются и летят вниз — удар на «по́» слова «потом».

Рисунок один — gen/p1_tower.png (вертикальный 1024×1536; координаты ниже ×2). Башню не вырезаем: она стоит на чистой
бумаге, поэтому качается полем смещений (поворот вокруг основания, сила — мягкая маска башни и верхней карточки в лапе):
под ней нечего достраивать, а лапа, держащая карточку, едет вместе с ней. Кот вздрагивает на ударе полем смещений
(squash_region), слетающие карточки — отдельные слои, нарисованные кодом так же, как на рисунке (белые, тонкий контур),
падают с ускорением, у пола отскакивают и ложатся плашмя. Хронометраж (голос с 0 с):
  0 – удар    башня в крене дрожит на двойках, размах растёт — предвестник; резкий наезд камеры;
  удар        ударный слог «по́» в «потом»: башню бросает вправо, карточки срываются, штрихи удара, капля пота, тряска;
  после       башня качается назад пружиной, карточки долетают до пола и остаются лежать.
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/p1_tower.png"]
VERSION = 2
REEL_DIR = None

PIVOT = (1600.0, 2735.0)                                    # основание башни (×2)
TOWER_BOX = (1290, 600, 1920, 2780)                         # башня целиком: x0, y0, x1, y1
CARD_BOX = (1090, 600, 1500, 880)                           # верхняя карточка в лапе: лапа едет с ней
BODY = dict(center=(720, 1900), axes=(560, 860), floor=2690)
CARD_FROM = (1330, 740)                                     # откуда срываются карточки
CARD_FLOOR = 2715                                           # уровень, на который карточки ложатся
ARM_TOP, ARM_BOTTOM = 850, 1380                              # рука от лапы вниз: вес смещения плавно падает до нуля
SWEAT = (610, 1170)
LEAN = 1.3                                                  # первый кадр — уже середина действия: башня в крене (градусы)
_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    x2 = os.path.join(d, "p1_tower_x2.png")
    if not os.path.exists(x2):
        import upscale
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = anim.paper_like(np.asarray(Image.open(x2).convert("RGB")).astype(np.float32))
    h, w = A.shape[:2]
    m = np.zeros((h, w), np.float32)
    x0, y0, x1, y1 = TOWER_BOX; m[y0:y1, x0:x1] = 1
    x0, y0, x1, y1 = CARD_BOX; m[y0:y1, x0:x1] = 1
    wgt = cv2.GaussianBlur(m, (0, 0), 20)
    ys0 = np.arange(h, dtype=np.float32)[:, None]
    ramp = np.clip((ARM_BOTTOM - ys0) / (ARM_BOTTOM - ARM_TOP), 0, 1) * (np.arange(w)[None, :] < 1300)   # рука тянется за
    wgt = np.maximum(wgt, cv2.GaussianBlur(ramp.astype(np.float32), (0, 0), 20) * (np.arange(w)[None, :] > 1040))  # карточкой плавно
    body = np.zeros((h, w), np.float32)
    cv2.ellipse(body, BODY["center"], BODY["axes"], 0, 0, 360, 1.0, -1)
    body = cv2.GaussianBlur(body, (0, 0), 50)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    return dict(A=A, wgt=wgt, body=body, xs=xs, ys=ys)


def layers():
    global _L
    if _L is None:
        _L = prepare()
    return _L


def timing(ctx):
    w = ctx["words"]                                        # «Веришь в «потом»?» — «потом» последнее слово
    return dict(hit=w[-1][0] + 0.12)                        # ударное «о» первого слога «по́том»


def tower_angle(t, T):
    """Угол башни (градусы, по часовой: вершина вправо)."""
    hit = T["hit"]
    if t < hit:
        u = clamp(t / hit)
        tq = anim.on_twos(t)
        return LEAN + (0.2 + 0.5 * u) * math.sin(2 * math.pi * 2.1 * tq)
    th = t - hit
    if th < 2 / 30:                                         # задержка на ударе
        return LEAN + 2.6
    return LEAN + 2.6 * anim.spring(th - 2 / 30, freq=2.3, damping=0.25)


def clamp(u):
    return min(1.0, max(0.0, u))


def _cards(T):
    """Карточки, сорванные ударом: старт у верха башни, у каждой своя скорость, вращение, высота пола."""
    rng = np.random.default_rng(7)
    out = []
    for i in range(6):
        out.append(dict(x0=CARD_FROM[0] + rng.uniform(-40, 130), y0=CARD_FROM[1] + rng.uniform(-30, 120) + 50 * i,
                        vx=rng.uniform(80, 330), vy=rng.uniform(-980, -420), spin=rng.uniform(260, 620) * rng.choice([-1, 1]),
                        a0=rng.uniform(-25, 25), sc=rng.uniform(0.8, 1.15), delay=0.03 * i,
                        floor=CARD_FLOOR - rng.uniform(0, 50), rest=rng.uniform(-9, 9)))
    return out


def draw_card(img, cx, cy, ang, sc, ink=(28, 28, 32), paper=(252, 250, 245)):
    pts = np.float32([(-150, -20), (112, -48), (152, 24), (-110, 52)]) * sc
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    p = np.int32(np.stack([pts[:, 0] * c - pts[:, 1] * s + cx, pts[:, 0] * s + pts[:, 1] * c + cy], 1) * 16)
    cv2.fillPoly(img, [p], paper, cv2.LINE_AA, shift=4)
    cv2.polylines(img, [p], True, ink, max(3, int(5 * sc)), cv2.LINE_AA, shift=4)
    return img


def card_state(c, th):
    """Положение карточки через th секунд после удара: полёт по параболе, отскок у пола, лежит плашмя."""
    g = 3200.0
    t = max(0.0, th - c["delay"])
    x = c["x0"] + c["vx"] * t
    y = c["y0"] + c["vy"] * t + 0.5 * g * t * t
    ang = c["a0"] + c["spin"] * t
    if y >= c["floor"]:
        tf = (-c["vy"] + math.sqrt(c["vy"] ** 2 + 2 * g * (c["floor"] - c["y0"]))) / g   # момент касания пола
        vyf = c["vy"] + g * tf
        tb = t - tf                                              # после касания: один короткий отскок, дальше лежит
        x = c["x0"] + c["vx"] * (tf + 0.25 * tb) if tb < 0.35 else c["x0"] + c["vx"] * (tf + 0.0875)
        hb = max(0.0, -0.22 * vyf * tb - 0.5 * g * tb * tb) if tb < 0.35 else 0.0
        y = c["floor"] - hb
        k = clamp(tb / 0.35)
        ang = (c["a0"] + c["spin"] * tf) * (1 - k) + c["rest"] * k
    return x, y, ang


def frame(t, ctx):
    L = layers(); T = timing(ctx); A = L["A"]
    cam = dict(dx=0.0, dy=0.0, zoom=1 / (1 + 0.12 * (1 - anim.SNAP(t / 0.30))), rot=0.0)
    th = t - T["hit"]
    theta = math.radians(tower_angle(t, T)) * L["wgt"]                  # угол в каждой точке: башня и карточка в лапе
    dx, dy = L["xs"] - PIVOT[0], L["ys"] - PIVOT[1]
    c, s = np.cos(-theta), np.sin(-theta)
    mx = (PIVOT[0] + dx * c - dy * s).astype(np.float32)
    my = (PIVOT[1] + dx * s + dy * c).astype(np.float32)
    img = cv2.remap(A, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if th >= 2 / 30:                                                    # кот вздрагивает от грохота — одним полем
        sq = 0.045 * anim.spring(th - 2 / 30, freq=4.2, damping=0.34)
        img = anim.squash_region(img, L["body"], BODY["floor"], BODY["center"][0], 1 - sq, 1 + 0.5 * sq)
    if th >= 0:
        for c_ in _cards(T):
            x, y, ang = card_state(c_, th)
            draw_card(img, x, y, ang, c_["sc"])
        for spread, seed in (((200, 260), 11), ((290, 350), 12)):
            anim.impact_strokes(img, (CARD_FROM[0] + 40, CARD_FROM[1] - 40), anim.on_twos(max(0.0, th - 2 / 30)), r0=110, r1=250,
                                n=3, spread=spread, width=12, color=(24, 24, 26), seed=seed, life=0.3)
        img = anim.sweat_drop(img, SWEAT, max(0.0, th - 0.05), size=36, fall=110, life=0.85)
        if th >= 2 / 30:
            k = math.exp(-(th - 2 / 30) / 0.12)
            cam["dx"] += 12 * k * math.sin(th * 95); cam["dy"] += 16 * k * math.cos(th * 77)
            cam["rot"] += 0.35 * k * math.sin(th * 61)
    return img, cam
