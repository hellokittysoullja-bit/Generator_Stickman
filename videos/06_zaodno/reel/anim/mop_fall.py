"""Хук «Пошёл мыть полы.»: кот уже смотрит на цветок, а швабра у стены кренится и падает плашмя — удар на «полы».

Рисунок один — gen/d1_mop.png (вертикальный, 1024×1536; координаты ниже ×2). Швабра вырезается по грубому
многоугольнику (anim.cut_polygon: её тряпки касаются ведра, ink_objects слил бы их), под ней и под её тенью на стене —
бумага (anim.fill_hole). Кот вырезается сам (ink_objects) и кладётся поверх: упавшая швабра лежит у стены, дальше кота,
и уходит за него. Хронометраж (от «Пошёл», голос с 0 с):
  0 – начало падения   швабра чуть дрожит (на двойках) — предвестник; резкий наезд камеры;
  падение              поворот вокруг низа тряпок, путь ∝ t² (на единицах), смаз позади;
  удар                 ударная «ы» в «полы»: задержка 2 кадра, отскок пружиной, штрихи удара тушью, кот вздрагивает,
                       капля пота, тряска камеры.
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/d1_mop.png"]
VERSION = 4
REEL_DIR = None

MOP = [(140, 885), (215, 885), (222, 1040), (305, 2085), (330, 2195), (445, 2300), (452, 2405), (40, 2405), (52, 2300),
       (185, 2195), (225, 2085), (148, 1040)]                       # грубый контур швабры (×2), снят по сетке
SHADOW = (55, 900, 205, 2246)                                        # серая тень швабры на стене (×2)
FLOOR_LINE = ((0, 2254), (362, 2254))                               # линия стены и пола за шваброй (×2)
PIVOT = (330, 2392)                                                 # швабра падает вокруг правого низа тряпок
REST_TOP_Y = 2335                                                   # верх ручки в покое на полу (тряпки чуть приподнимают)
CAT_BOX = (950, 1450, 2048, 2760)
CAT = dict(center=(1500, 2150), axes=(520, 560), floor=2650)
SWEAT = (1100, 1720)                                                # капля у лба кота (×2)
_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"mop_fall_v{VERSION}.npz")
    if os.path.exists(p):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    import upscale
    x2 = os.path.join(d, "d1_mop_x2.png")
    if not os.path.exists(x2):
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = np.asarray(Image.open(x2).convert("RGB")).astype(np.float32)
    mop = anim.cut_polygon(A, MOP, grow=21, sure=11)
    hole = cv2.dilate(mop, np.ones((11, 11), np.uint8)) > 0
    x0, y0, x1, y1 = SHADOW; hole[y0:y1, x0:x1] = True
    # зерно — с чистой стены справа (выше пола) и с чистого пола ниже (у пола): шум «noise» был заметно грубее
    up = anim.fill_hole(A, hole, grain_from=(0, -560), feather=3)
    dn = anim.fill_hole(A, hole, grain_from=(-480, 0), feather=3)
    k = np.clip((np.arange(A.shape[0], dtype=np.float32) - 1925) / 25, 0, 1)[:, None, None]   # обод ведра с ~1955
    bg = up * (1 - k) + dn * k
    line = np.zeros(A.shape[:2], np.float32)               # линия пола под шваброй — тушью, как слева от неё
    cv2.line(line, FLOOR_LINE[0], FLOOR_LINE[1], 1.0, 4, cv2.LINE_AA)
    line = cv2.GaussianBlur(line, (0, 0), 0.8) * hole
    bg = bg * (1 - line[..., None]) + np.float32([30, 30, 32]) * line[..., None]
    cats = anim.ink_objects(A, box=CAT_BOX, min_area=40000)
    A, bg = anim.paper_like(A), anim.paper_like(bg)
    out = dict(A=np.clip(A, 0, 255).astype(np.uint8), bg=np.clip(bg, 0, 255).astype(np.uint8),
               mop=cv2.GaussianBlur(mop.astype(np.float32), (0, 0), 1.0),
               cat=cats[0].astype(np.float32) if cats else np.zeros(A.shape[:2], np.float32))
    np.savez(p, **out)
    return out


def _rest_angle(lay):
    """Угол (по часовой, градусы), при котором верх ручки ложится на пол: верх — самая высокая точка маски."""
    pts = np.argwhere(lay.a > 0.5)[:, ::-1].astype(np.float32)
    top = pts[np.argmin(pts[:, 1])] - lay.pivot
    best = 90.0
    for ang in np.arange(70.0, 100.0, 0.25):
        b = math.radians(ang)
        y = math.sin(b) * top[0] + math.cos(b) * top[1]
        if PIVOT[1] + y >= REST_TOP_Y:
            best = float(ang); break
    return best, top


def layers():
    global _L
    if _L is None:
        d = prepare()
        mop = anim.Layer.cut(d["A"], d["mop"] > 0.5, pad=6, feather=0)
        x0, y0 = mop.origin.astype(int); h, w = mop.a.shape
        mop.a = d["mop"][y0:y0 + h, x0:x0 + w]
        mop.pivot = np.float32(PIVOT) - mop.origin
        cat = anim.Layer.cut(d["A"], d["cat"] > 0.5, pad=6, feather=1.0)
        rest, top = _rest_angle(mop)
        body = np.zeros(d["A"].shape[:2], np.float32)
        cv2.ellipse(body, CAT["center"], CAT["axes"], 0, 0, 360, 1.0, -1)
        _L = dict(d=d, mop=mop, cat=cat, rest=rest, top=top, body=cv2.GaussianBlur(body, (0, 0), 50))
    return _L


def timing(ctx):
    w = ctx["words"]                                   # «Пошёл», «мыть», «полы.»
    hit = w[2][0] + 0.12                               # ударная «ы» в «полы»
    return dict(fall=hit - 0.42, hit=hit)


def angle_at(t, T, rest):
    if t < T["fall"]:
        tq = anim.on_twos(t)                           # предвестник: швабра дрожит у стены
        return 1.2 * math.sin(2 * math.pi * 3.0 * tq) * anim.clamp01((t - 0.15) / 0.3)
    if t < T["hit"]:
        return rest * anim.gravity((t - T["fall"]) / (T["hit"] - T["fall"]))
    th = t - T["hit"]
    if th < 2 / 30:                                    # задержка на ударе
        return rest
    return rest - 5.0 * abs(anim.spring(th - 2 / 30, freq=4.5, damping=0.35)) * math.exp(-(th - 2 / 30) / 0.25)


def frame(t, ctx):
    Lr = layers(); d = Lr["d"]; T = timing(ctx)
    cam = dict(dx=0.0, dy=0.0, zoom=1 / (1 + 0.12 * (1 - anim.SNAP(t / 0.30))), rot=0.0)
    img = d["bg"].astype(np.float32)
    mop = Lr["mop"]; home = mop.home()
    ang = angle_at(t, T, Lr["rest"])
    prev = angle_at(t - 1 / 30, T, Lr["rest"])
    b0, b1 = math.radians(prev), math.radians(ang)
    tx, ty = Lr["top"]
    vx = (math.cos(b1) * tx - math.sin(b1) * ty) - (math.cos(b0) * tx - math.sin(b0) * ty)
    vy = (math.sin(b1) * tx + math.cos(b1) * ty) - (math.sin(b0) * tx + math.cos(b0) * ty)
    fast = T["fall"] <= t < T["hit"]
    mop.draw(img, home, ang, smear=(0.35 * vx, 0.35 * vy) if fast and math.hypot(vx, vy) > 20 else None)
    th = t - T["hit"]
    sq = 0.0
    if th >= 2 / 30:                                   # кот вздрагивает от грохота — одним полем, не «желе»
        sq = 0.05 * anim.spring(th - 2 / 30, freq=4.2, damping=0.34)
    cat = Lr["cat"]
    if abs(sq) > 0.002:
        layer = np.zeros_like(img); a = np.zeros(img.shape[:2], np.float32)
        cat.draw(layer, cat.home()); x0, y0 = cat.origin.astype(int); h, w = cat.a.shape
        a[y0:y0 + h, x0:x0 + w] = cat.a
        layer = anim.squash_region(layer, Lr["body"], CAT["floor"], CAT["center"][0], 1 - sq, 1 + 0.5 * sq)
        a = anim.squash_region(a[..., None].repeat(3, -1), Lr["body"], CAT["floor"], CAT["center"][0], 1 - sq, 1 + 0.5 * sq)[..., 0]
        img = img * (1 - a[..., None]) + layer
    else:
        cat.draw(img, cat.home())
    if th >= 0:
        hit_pt = (home[0] + 650, PIVOT[1] - 40)        # видимая часть ручки между ведром и котом
        for spread, seed in (((200, 250), 5), ((290, 340), 6)):
            anim.impact_strokes(img, hit_pt, anim.on_twos(max(0.0, th - 2 / 30)), r0=120, r1=230, n=3,
                                spread=spread, width=12, color=(24, 24, 26), seed=seed, life=0.3)
        anim.sweat_drop(img, SWEAT, max(0.0, th - 0.05), size=34, fall=90, life=0.8)
        if th >= 2 / 30:
            k = math.exp(-(th - 2 / 30) / 0.12)
            cam["dx"] += 12 * k * math.sin(th * 95); cam["dy"] += 16 * k * math.cos(th * 77)
            cam["rot"] += 0.35 * k * math.sin(th * 61)
    return img, cam
