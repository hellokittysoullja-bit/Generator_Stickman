"""Хук «Ждёшь идеала?»: кот замер с карандашом над пустым листом, и ещё один скомканный лист уже летит в гору таких же;
на «иде́ала» он падает в кучу, отскакивает и ложится, кот вздрагивает. Карандаш дрожит над листом с первого кадра.

Стандарт 20 (владелец 26.10): камера — anim.hook_cam (влёт как в рилсе 08), рисунок движется уже на первом кадре —
ком в полёте (на рисунке он и нарисован падающим, со штрихами скорости), карандаш дрожит.

Рисунок один — gen/i1_blank.png (1024×1536, координаты ниже ×2). Ком и его штрихи скорости вырезаются сами
(anim.ink_objects: они стоят отдельно на бумаге), под ними — бумага (anim.fill_hole). Кот и карандаш — поле смещений.
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/i1_blank.png"]
VERSION = 4
REEL_DIR = None

BALL_BOX = (1400, 100, 1900, 900)                    # ком и штрихи над ним (×2)
BALL_CENTER = (1637.0, 642.0)                        # центр кома на рисунке
LAND = (1690.0, 2185.0)                              # ложится на верх кучи справа от стола
PENCIL = dict(x0=700, x1=870, y0=1540, y1=1960)      # карандаш: дрожит сильнее к кончику
BODY = dict(center=(860, 1450), axes=(560, 560), floor=2000)
_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"ball_fall_v{VERSION}.npz")
    if os.path.exists(p):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    x2 = os.path.join(d, "i1_blank_x2.png")
    if not os.path.exists(x2):
        import upscale
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = np.asarray(Image.open(x2).convert("RGB")).astype(np.float32)
    objs = anim.ink_objects(A, box=BALL_BOX, min_area=200)
    ball = max(objs, key=lambda o: o.sum())
    lines = np.zeros_like(ball)
    for o in objs:
        if o is not ball:
            lines |= o
    hole = cv2.dilate((ball | lines).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
    ys_, xs_ = np.nonzero(hole)                      # вся полоса полёта — бумагой: по контурам оставался призрак штрихов
    hole[max(0, ys_.min() - 20):ys_.max() + 20, max(0, xs_.min() - 20):xs_.max() + 20] = True
    bg = anim.fill_hole(A, hole, grain_from=(0, 320), feather=3)   # (dy, dx): зерно с бумаги левее
    h, w = A.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    pen = np.zeros((h, w), np.float32)
    P = PENCIL; pen[P["y0"]:P["y1"], P["x0"]:P["x1"]] = np.linspace(0, 1, P["y1"] - P["y0"], dtype=np.float32)[:, None]
    pen = cv2.GaussianBlur(pen, (0, 0), 12)
    body = np.zeros((h, w), np.float32)
    cv2.ellipse(body, BODY["center"], BODY["axes"], 0, 0, 360, 1.0, -1)
    body = cv2.GaussianBlur(body, (0, 0), 45)
    A, bg = anim.paper_like(A), anim.paper_like(bg)
    out = dict(A=np.clip(A, 0, 255).astype(np.uint8), bg=np.clip(bg, 0, 255).astype(np.uint8),
               ball=ball.astype(np.uint8), lines=lines.astype(np.uint8), pen=pen, body=body)
    np.savez(p, **out)
    return out


def layers():
    global _L
    if _L is None:
        d = prepare()
        ball = anim.Layer.cut(d["A"], d["ball"] > 0, pad=6, feather=1.0)
        ball.pivot = np.float32(BALL_CENTER) - ball.origin
        lines = anim.Layer.cut(d["A"], d["lines"] > 0, pad=6, feather=1.0)
        h, w = d["A"].shape[:2]
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        _L = dict(d=d, ball=ball, lines=lines, xs=xs, ys=ys)
    return _L


def timing(ctx):
    w = ctx["words"]                                  # «Ждёшь идеала?» — «идеала» второе слово, ударное «е» второго слога
    s, e = w[1]
    return dict(hit=s + 0.35 * (e - s))


def ball_at(t, T):
    """Центр кома и его поворот: падение с ускорением (уже летит на первом кадре), удар, отскок пружиной, лёг."""
    hit = T["hit"]
    if t < hit:
        u = t / hit
        y = BALL_CENTER[1] + (LAND[1] - BALL_CENTER[1]) * (0.35 * u + 0.65 * anim.gravity(u))   # летит с начальной скоростью
        x = BALL_CENTER[0] + (LAND[0] - BALL_CENTER[0]) * u
        return x, y, 220.0 * t, True
    th = t - hit
    if th < 2 / 30:
        return LAND[0], LAND[1], 220.0 * hit, False
    b = 70.0 * abs(anim.spring(th - 2 / 30, freq=3.0, damping=0.45))      # подпрыгнул и успокоился
    return LAND[0] + 18.0 * anim.EASE_OUT(min(1.0, th / 0.5)), LAND[1] - b, 220.0 * hit + 40.0 * anim.EASE_OUT(min(1.0, th / 0.5)), False


def frame(t, ctx):
    L = layers(); d = L["d"]; T = timing(ctx)
    cam = anim.hook_cam(t)                             # влёт как в рилсе 08 (стандарт 20)
    th = t - T["hit"]
    img = d["bg"].astype(np.float32)
    # карандаш дрожит над листом с первого кадра (на двойках): страх первой линии
    tq = anim.on_twos(t)
    amp = 5.0 if th < 0 else 5.0 + 9.0 * math.exp(-max(0.0, th) / 0.2)
    dx = amp * math.sin(2 * math.pi * 7.0 * tq) * d["pen"]
    img = cv2.remap(img, L["xs"] - dx, L["ys"], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # кот вздрагивает на ударе — одним полем, не «желе»
    if th >= 2 / 30:
        sq = 0.04 * anim.spring(th - 2 / 30, freq=4.2, damping=0.34)
        if abs(sq) > 0.002:
            img = anim.squash_region(img, d["body"], BODY["floor"], BODY["center"][0], 1 - sq, 1 + 0.5 * sq)
    # ком: летит, бьётся о кучу, ложится; штрихи скорости летят с ним и гаснут к удару
    x, y, ang, flying = ball_at(t, T)
    ball, lines = L["ball"], L["lines"]
    px, py, _, _ = ball_at(t - 1 / 30, T)
    vy = y - py
    if flying:
        off = np.float32([x - BALL_CENTER[0], y - BALL_CENTER[1]])
        lines.draw(img, lines.home() + off, 0.0, opacity=max(0.0, 1.0 - t / max(0.05, T["hit"])))
    home = ball.home() + np.float32([x - BALL_CENTER[0], y - BALL_CENTER[1]])
    ball.draw(img, home, ang, smear=(0.0, 0.35 * vy) if flying and abs(vy) > 20 else None)
    if th >= 0:
        for spread, seed in (((200, 250), 31), ((290, 340), 32)):
            anim.impact_strokes(img, (LAND[0], LAND[1] + 60), anim.on_twos(max(0.0, th - 2 / 30)), r0=130, r1=240, n=3,
                                spread=spread, width=12, color=(24, 24, 26), seed=seed, life=0.3)
        if th >= 2 / 30:
            k = math.exp(-(th - 2 / 30) / 0.12)
            cam["dx"] += 10 * k * math.sin(th * 95); cam["dy"] += 14 * k * math.cos(th * 77)
            cam["rot"] += 0.3 * k * math.sin(th * 61)
    return img, cam
