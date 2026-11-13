"""Сцена box рилса 26 (s03, s04): тёмный угол прихожей у шкафа, обувная коробка в пыли, паутина, паучок на нитке.
s03: паучок спускается; на «кроссовки» (3.36) крышка приподнимается, из щели тёплый свет и новые кроссовки с биркой.
s04: на «лежат» (4.64) крышка опускается, на «коробке» (5.08) хлопок и облако пыли, паучок раскачивается от волны."""
import math

import numpy as np

import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg)

_ST = {}
LIFT_T, DROP_T, SLAM_T = 3.36, 4.64, 5.04
FLOOR = 1060
# коробка: передняя грань, верх (вид чуть сверху), правый бок
BX0, BX1, BY0, BY1 = 330, 900, 840, 1120
DX, DY = 90, -130          # глубина верха
CARD, CARD_SH, CARD_DK = "#a8743f", "#7f532a", "#5e3c1d"


def room():
    s = []
    lin_grad([(0, "#2b3042", 1), (1, "#3a3f52", 1)], 0, 0, 0, 1, gid="gWallD")
    s.append(f'<rect x="-1000" y="-1500" width="{W + 2000}" height="{FLOOR + 1500}" fill="url(#gWallD)"/>')
    # обои: тонкие полосы
    for k in range(-8, 26):
        x = k * 70
        s.append(line([(x, -1500), (x, FLOOR)], 3, "#323749", taper=.05, wmin=.9, seed=10 + k))
    # плинтус
    s.append(shape(rect_pts(-1000, FLOOR - 46, W + 1000, FLOOR), "#4b4036", blob(rect_pts(-1000, FLOOR - 14, W + 1000, FLOOR), "#3a3129"), w=4, seed=20))
    # пол — тёмные доски
    DEFS.append('<pattern id="pFloorD" width="300" height="70" patternUnits="userSpaceOnUse">'
                '<rect width="300" height="70" fill="#3d2b20"/><rect y="66" width="300" height="4" fill="#2a1d15"/>'
                '<rect x="180" width="4" height="70" fill="#2a1d15"/><path d="M0 30 C80 26 170 36 300 30" stroke="#33241b" stroke-width="3" fill="none"/></pattern>')
    s.append(f'<rect x="-1000" y="{FLOOR}" width="{W + 2000}" height="1500" fill="url(#pFloorD)"/>')
    s.append(line([(-1000, FLOOR), (W + 1000, FLOOR)], 4, INK, taper=.05, wmin=.9, seed=21))
    # полоса тёплого света из приоткрытой двери справа
    g = lin_grad([(0, "#ffce86", .0), (.5, "#ffce86", .32), (1, "#ffce86", .05)], 0, 0, 1, 0)
    s.append(f'<path d="M1180 -400 L1340 -400 L1340 {FLOOR} L1250 {FLOOR} L700 1700 L420 1700 L1180 {FLOOR}Z" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    # шкаф слева: боковина, дверь с ручкой
    inner = blob(rect_pts(220, -1500, 300, 1140), "#3b2618")
    inner += line([(196, -1500), (196, 1130)], 3, "#2a1a10", taper=.05, wmin=.9, seed=31)
    s.append(shape([(-600, -1500, 1), (300, -1500, 1), (300, 1150, 1), (-600, 1150, 1)], "#5a3a24", inner, w=5, seed=30))
    s.append(shape(rect_pts(150, 520, 178, 680, 10), "#b8a48a", blob(rect_pts(150, 600, 178, 680, 10), "#8d7a62"), w=3.4, seed=32))
    s.append(blob(rect_pts(-600, 1150, 330, 1190), "#1a120c", .6, blur(10)))
    # клубки пыли на полу
    for k, (x, y, r) in enumerate([(980, 1150, 22), (1040, 1120, 14), (250, 1230, 18)]):
        s.append(shape(ellipse_pts(x, y, r * 1.4, r, 10, jitter=.25, seed=k), "#7d7670",
                       "".join(line([(x - r + j * 7, y - r * .6), (x - r + j * 7 + 12, y + r * .4)], 1.6, "#a8a199", seed=40 + j) for j in range(5)),
                       w=2.4, seed=45 + k))
    return "".join(s)


def web():
    """Паутина в углу между шкафом и коробкой: радиальные нити и спираль."""
    s = []
    c = (300, 640)
    ends = [(300, 360), (420, 420), (560, 560), (540, 740), (470, 805), (330, 812), (300, 720)]
    for k, e in enumerate(ends):
        s.append(line([c, ((c[0] + e[0]) / 2 + 6, (c[1] + e[1]) / 2 + 8), e], 2.2, "#c7ccd8", taper=.2, wmin=.6, seed=100 + k))
    for r in (40, 80, 125, 170):
        pts = []
        for k, e in enumerate(ends):
            v = np.array(e) - np.array(c)
            L = np.linalg.norm(v)
            if L < r:
                continue
            p = np.array(c) + v / L * r
            pts.append((p[0], p[1] + 5))
        if len(pts) > 1:
            s.append(line(pts, 1.8, "#b3b9c7", taper=.2, wmin=.6, seed=120 + r))
    return "".join(s)


def box_body():
    s = []
    # тень коробки
    s.append(blob(rect_pts(BX0 - 10, BY1 - 20, BX1 + DX + 40, BY1 + 30), "#000", .5, blur(14)))
    side = [(BX1, BY0, 1), (BX1 + DX, BY0 + DY, 1), (BX1 + DX, BY1 + DY, 1), (BX1, BY1, 1)]
    s.append(shape(side, CARD_SH, blob([(BX1, BY1 - 40, 1), (BX1 + DX, BY1 + DY - 40, 1), (BX1 + DX, BY1 + DY, 1), (BX1, BY1, 1)], CARD_DK, .7),
                   w=4.6, seed=200))
    front = rect_pts(BX0, BY0, BX1, BY1)
    inner = blob(rect_pts(BX0, BY1 - 50, BX1, BY1), CARD_SH, .8)
    inner += line([(BX0 + 30, BY0 + 120), (BX0 + 210, BY0 + 116)], 3, CARD_SH, seed=201)
    # кружок-логотип без букв
    inner += blob(ellipse_pts(BX1 - 120, BY0 + 140, 44, 44, 16), "#e9e1d2")
    inner += blob(ellipse_pts(BX1 - 120, BY0 + 140, 30, 18, 12, rot=-20), "#c4473b")
    s.append(shape(front, CARD, inner, w=5, seed=202))
    return "".join(s)


def sneaker(x, y, sc, rot, sd, flip=1):
    """Новый кроссовок в профиль (носок вправо): белый верх, мятные полосы, шнурки, язычок, толстая подошва."""
    def P(pts):
        out = []
        a = math.radians(rot)
        for p in pts:
            px, py = p[0] * flip * sc, p[1] * sc
            out.append((x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)) + ((1,) if len(p) > 2 else ()))
        return out
    s = []
    sole = [(-150, 18), (-146, 52), (-110, 60), (60, 58), (140, 50), (162, 30), (160, 12), (40, 22), (-100, 16)]
    s.append(shape(P(sole), "#efe4cc", blob(P([(-146, 40), (-110, 48), (60, 46), (140, 40), (162, 30), (140, 50), (60, 58), (-110, 60), (-146, 52)]),
                                               "#cdb98f") + line(P([(-120, 34), (130, 30)]), 3, "#d9c9a6", seed=sd + 7), w=4.2, seed=sd))
    up = [(-148, 20), (-150, -40), (-130, -78), (-96, -84), (-70, -62), (-30, -60), (20, -40), (80, -16), (130, -4), (160, 12), (40, 22),
          (-100, 18)]
    inner = blob(P([(-150, 0), (160, 0), (160, 24), (-150, 24)]), "#dfe2e8", .9)
    inner += line(P([(-80, 8), (-30, -36), (0, -50)]), 11, "#3fb8a0", taper=.3, seed=sd + 1)
    inner += line(P([(-50, 12), (0, -22), (30, -32)]), 11, "#3fb8a0", taper=.3, seed=sd + 2)
    inner += blob(P([(-150, -40), (-130, -78), (-96, -84), (-110, -40), (-150, 10)]), "#3fb8a0")
    s.append(shape(P(up), "#fbfbf8", inner, w=4.6, seed=sd + 3))
    s.append(shape(P([(-94, -82), (-66, -104), (-44, -98), (-58, -64)]), "#f1f1ec", "", w=3.4, seed=sd + 4))
    s.append(shape(P([(-120, -76), (-78, -80), (-74, -66), (-114, -64)]), "#3a3f52", "", w=3, seed=sd + 5))
    for k in range(4):
        u = -56 + k * 28
        v = -60 + k * 11
        s.append(line(P([(u - 6, v - 4), (u + 16, v + 8)]), 5, "#9aa3b5", taper=.2, wmin=.6, seed=sd + 10 + k))
    s.append(line(P([(110, 4), (150, 14)]), 3, "#c9cdd6", seed=sd + 20))
    return "".join(s), P


def tag(x, y, sw, sd):
    """Бирка на верёвочке без букв: белый картон, красная полоса, штрихкод."""
    s = [line([(x, y), (x + 10 + sw * 0.4, y + 30), (x + 18 + sw, y + 52)], 2.4, "#e9e1d2", taper=.1, wmin=.8, seed=sd)]
    cx, cy = x + 18 + sw, y + 52
    pts = [(cx - 26, cy, 1), (cx + 26, cy, 1), (cx + 30, cy + 70, 1), (cx - 22, cy + 72, 1)]
    inner = blob(rect_pts(cx - 30, cy, cx + 32, cy + 16), "#d8433a")
    for k in range(7):
        inner += line([(cx - 14 + k * 5, cy + 34), (cx - 14 + k * 5, cy + 58)], 2.4 if k % 2 else 1.4, "#3a3330", taper=.05, wmin=.9, seed=sd + k)
    s.append(shape(pts, "#fbf8f0", inner, w=2.8, seed=sd + 9))
    s.append(blob(ellipse_pts(cx, cy + 6, 4, 4, 8), "#3a3330"))
    return "".join(s)


def opening(t, glow):
    """Внутренность коробки (видна, когда крышка поднята): тёмное нутро, бумага, кроссовки с биркой, тёплое сияние."""
    top = [(BX0, BY0, 1), (BX0, BY0 + DY, 1), (BX1 + DX, BY0 + DY, 1), (BX1, BY0, 1)]
    inner = blob(rect_pts(BX0 - 20, BY0 + DY - 100, BX1 + DX + 20, BY0 + 10), "#2a1a10")
    inner += blob(rect_pts(BX0 + DX, BY0 + DY, BX1 + DX, BY0 + DY + 30), "#1d120a")
    inner += blob([(BX0, BY0 + 10), (BX0 + 20, BY0 - 60), (BX0 + 120, BY0 - 40), (BX0 + 260, BY0 - 80), (BX0 + 400, BY0 - 50),
                   (BX1 - 60, BY0 - 90), (BX1 + DX, BY0 + DY - 20), (BX1 + DX, BY0 + 10)], "#e6dccb")
    b, _ = sneaker(BX0 + 440, BY0 - 14, 0.95, -5, 320)
    a, P = sneaker(BX0 + 200, BY0 + 2, 1.0, 3, 300)
    inner += b + a
    inner += blob([(BX0, BY0 + 10), (BX0 + 40, BY0 - 14), (BX0 + 110, BY0 - 2), (BX0 + 210, BY0 - 18), (BX0 + 330, BY0 - 4),
                   (BX0 + 450, BY0 - 20), (BX1 - 40, BY0 - 6), (BX1 + 10, BY0 - 16), (BX1 + 10, BY0 + 10)], "#efe6d6")
    sw = 6 * math.sin(t * 9)
    lx, ly = P([(-30, -58)])[0]
    inner += tag(lx, ly, sw, 340)
    g = rad_grad([(0, "#ffe2a0", .5 * glow), (1, "#ffb860", 0)], (BX0 + BX1) / 2 + 40, BY0 - 60, 420, 170)
    inner += f'<rect x="{BX0 - 40}" y="{BY0 + DY - 120}" width="{BX1 - BX0 + DX + 80}" height="{-DY + 160}" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    c = lib.clip_of(top)
    return f'<g clip-path="url(#{c})">{inner}</g>'


def lid(dust_k):
    """Крышка (в своих координатах, задний край у y = BY0 + DY): верх в пыли, передняя полоса, бок."""
    s = []
    o = 14
    ft = [(BX0 - o, BY0 - 32, 1), (BX1 + o, BY0 - 32, 1), (BX1 + o, BY0 + 36, 1), (BX0 - o, BY0 + 36, 1)]
    top = [(BX0 - o, BY0 - 32, 1), (BX1 + o, BY0 - 32, 1), (BX1 + DX + o, BY0 + DY - 40, 1), (BX0 + DX - o, BY0 + DY - 40, 1)]
    side = [(BX1 + o, BY0 - 32, 1), (BX1 + DX + o, BY0 + DY - 40, 1), (BX1 + DX + o, BY0 + DY + 26, 1), (BX1 + o, BY0 + 36, 1)]
    s.append(shape(side, CARD_SH, "", w=4.4, seed=400))
    rs = np.random.RandomState(4)
    dust = blob([(BX0 + 30, BY0 - 40), (BX1 - 20, BY0 - 44), (BX1 + DX - 10, BY0 + DY - 30), (BX0 + DX + 20, BY0 + DY - 30)],
                mix(CARD, "#b8b0a6", .75 * dust_k), 1, blur(6))
    for k in range(70):
        u, v = rs.uniform(0, 1), rs.uniform(0, 1)
        x = BX0 + (BX1 - BX0) * u + DX * v
        y = BY0 - 36 + (DY - 4) * v
        dust += blob(ellipse_pts(x, y, 2.5, 2, 6), "#d6d0c8" if k % 3 else "#8f877e", dust_k)
    s.append(shape(top, mix(CARD, "#c9a070", .25), dust, w=4.6, seed=401))
    s.append(shape(ft, CARD, blob(rect_pts(BX0 - o, BY0 + 18, BX1 + o, BY0 + 36), CARD_SH, .8) +
                   blob(rect_pts(BX0 - o, BY0 - 32, BX1 + o, BY0 - 24), mix(CARD, "#b8b0a6", .6 * dust_k)), w=4.8, seed=402))
    return "".join(s)


def lid_state(t):
    """Подъём передней кромки (px) и поворот: подъём на 3.36 с перелётом, дрожь, опускание к 5.04, хлопок."""
    if t < LIFT_T - 0.08:
        return 0.0, 0.0
    if t < DROP_T:
        e = t - (LIFT_T - 0.08)
        up = 130 * (1 - math.exp(-e * 9) * math.cos(e * 22))
        jit = 3 * math.sin(t * 31) + 2 * math.sin(t * 17)
        return up + jit, -2.5 + 1.2 * math.sin(t * 6)
    if t < SLAM_T:
        e = (t - DROP_T) / (SLAM_T - DROP_T)
        h0 = 130 + 3 * math.sin(DROP_T * 31) + 2 * math.sin(DROP_T * 17)
        u = ease_in(e, 2.4) if e > 0.25 else 0.08 * e / 0.25
        return h0 * (1 - u), -2.5 * (1 - u)
    e = t - SLAM_T
    return max(0.0, 16 * math.exp(-e * 10) * abs(math.sin(e * 26))), 0.0


def puffs(t):
    """Хлопок крышки: клубы пыли вылетают из щели по всей кромке и в стороны, растут и тают (сжимаются)."""
    e = t - SLAM_T
    if e < 0 or e > 1.0:
        return ""
    s = []
    rs = np.random.RandomState(9)
    cl = []
    for k in range(16):
        u = rs.uniform(-0.1, 1.15)
        x0 = BX0 + (BX1 + DX - BX0) * u
        y0 = BY0 + 10 + (DY * clamp(u - 0.9) * 2 if u > 0.9 else 0) + rs.uniform(-10, 20)
        side = -1 if u < 0.45 else 1
        x = x0 + side * rs.uniform(60, 190) * (1 - math.exp(-e * 5))
        y = y0 - rs.uniform(30, 160) * (1 - math.exp(-e * 4)) + 20 * e
        life = rs.uniform(0.55, 0.95)
        r = rs.uniform(40, 74) * math.sin(math.pi * clamp(e / life)) ** 0.6
        if r < 4:
            continue
        col = mix("#cfc6b8", "#e2dbcf", rs.uniform(0, 1))
        cl.append((x, y, r, col, k))
    for x, y, r, col, k in cl:
        s.append(shape(ellipse_pts(x, y, r, r * .8, 14, jitter=.06, seed=k), col, "", w=2.2, seed=500 + k, var=.15))
    for x, y, r, col, k in cl:
        s.append(blob(ellipse_pts(x - r * .2, y - r * .28, r * .5, r * .3, 10), "#f3eee6", .95))
    for k in range(18):
        x = rs.uniform(BX0 - 60, BX1 + 140)
        y = BY0 - 20 - rs.uniform(0, 240) * min(1, e * 3) + 60 * e * e
        r = 3.2 * (1 - e)
        s.append(blob(ellipse_pts(x + 30 * e * (1 if k % 2 else -1), y, r, r, 6), "#d6d0c8"))
    return "".join(s)


def motes(t, glow):
    """Пылинки в тёплом свете над открытой коробкой и в луче от двери — медленно плывут."""
    s = []
    rs = np.random.RandomState(12)
    for k in range(26):
        x0, y0 = rs.uniform(300, 1150), rs.uniform(360, 1050)
        x = x0 + 30 * math.sin(t * rs.uniform(.5, 1.2) + k)
        y = y0 - 18 * t + 20 * math.cos(t * rs.uniform(.4, 1) + k)
        r = rs.uniform(1.6, 3.6)
        inbox = abs(x - 650) < 330 and BY0 - 300 < y < BY0
        if inbox and glow > 0.1:
            s.append(blob(ellipse_pts(x, y, r + 1, r + 1, 6), "#ffe9b8"))
        elif x > 900:
            s.append(blob(ellipse_pts(x, y, r, r, 6), "#e8cf9f"))
    return "".join(s)


def spider(t):
    """Паучок на нитке: спускается (s03), качается после хлопка (s04). Возвращает SVG."""
    ax = 770
    yb = 470 + 150 * ease_io(clamp((t - 3.08) / 1.5)) + 8 * math.sin(t * 4.2)
    ang = 0.0
    if t > SLAM_T + 0.03:
        e = t - SLAM_T - 0.03
        ang = 9 * math.exp(-e * 1.3) * math.sin(e * 5.2)
    ang += 2 * math.sin(t * 1.7)
    L = yb + 400
    a = math.radians(ang)
    x, y = ax + L * math.sin(a), -400 + L * math.cos(a)
    s = [line([(ax, -400), (x, y - 14)], 1.8, "#c7ccd8", taper=.05, wmin=.9, seed=600)]
    legs = ""
    for side in (-1, 1):
        for k in range(4):
            ph = math.sin(t * 9 + k * 1.3) * 6
            bx, by = x + side * 10, y - 6 + k * 8
            kx, ky = bx + side * (30 + k * 3), by - 20 + k * 8 + ph * 0.4
            ex, ey = kx + side * (12 + k * 2), ky + 28 + ph
            legs += line([(bx, by), (kx, ky), (ex, ey)], 4.2, "#15121a", taper=.4, wmin=.4, seed=610 + k + side * 10)
    s.append(f'<g transform="rotate({f(-ang * 0.6)} {f(x)} {f(y)})">{legs}' +
             shape(ellipse_pts(x, y + 8, 19, 22, 14), "#211c27", blob(ellipse_pts(x - 6, y + 2, 6, 8, 8), "#4a4258"), w=3, seed=620) +
             shape(ellipse_pts(x, y - 14, 13, 11, 12), "#211c27", "", w=2.8, seed=621) +
             blob(ellipse_pts(x - 6, y - 16, 6, 6.5, 10), "#fff") + blob(ellipse_pts(x + 6, y - 16, 6, 6.5, 10), "#fff") +
             blob(ellipse_pts(x - 5 + 1.5 * math.sin(t * 2), y - 15, 2.2, 2.2, 8), INK) +
             blob(ellipse_pts(x + 7 + 1.5 * math.sin(t * 2), y - 15, 2.2, 2.2, 8), INK) + "</g>")
    return "".join(s)


def frame(sid, t):
    if not _ST:
        _ST["room"] = room() + web()
        _ST["body"] = box_body()
        _ST["lid"] = lid(1.0)
        _ST["lid2"] = lid(0.35)
        lib.static_done()
    lib.dyn_begin()
    up, rot = lid_state(t)
    glow = clamp(up / 90)
    s = [_ST["room"], _ST["body"]]
    if up > 2:
        s.append(opening(t, glow))
    # крышка: передняя кромка поднимается, крышка поворачивается вокруг заднего края
    piv = ((BX0 + BX1 + DX) / 2, BY0 + DY - 40)
    sy = 1 - up / 300
    lid_svg = _ST["lid"] if t < SLAM_T else _ST["lid2"]
    s.append(f'<g transform="translate(0 {f(-up * 0.55)}) rotate({f(rot)} {f(piv[0])} {f(piv[1])}) translate({f(piv[0])} {f(piv[1])}) '
             f'scale(1 {f(sy)}) translate({f(-piv[0])} {f(-piv[1])})">{lid_svg}</g>')
    s.append(puffs(t))
    s.append(motes(t, glow))
    s.append(spider(t))
    # камера
    if sid == "s03":
        u = clamp((t - 3.08) / 1.76)
        sc = 1.22 + 0.16 * (0.4 * u + 0.6 * ease_io(u))
        cx, cy, r = 650 + 20 * u, 790 - 30 * u, -1.0 + 0.6 * u
        if t > LIFT_T:
            q = t - LIFT_T
            sc *= 1 + 0.03 * math.exp(-q * 6) * math.sin(min(q * 14, math.pi))
    else:
        u = clamp((t - 4.44) / 1.92)
        sc = 1.42 + 0.05 * u
        cx, cy, r = 690 - 25 * u, 820 + 10 * math.sin(t * 1.4), 1.6 - 0.5 * u
        if t > SLAM_T:
            q = t - SLAM_T
            k = math.exp(-q * 9)
            cx += 12 * k * math.sin(q * 60)
            cy += 9 * k * math.sin(q * 47 + 1)
            sc *= 1 + 0.04 * k
    vig = rad_grad([(0, "#000", 0), (.6, "#000", 0), (1, "#05060c", .6)], 540, 900, 900, 1300)
    return svg(f'<rect width="{W}" height="{H}" fill="#2b3042"/><g transform="{cam(cx, cy, sc, r)}">{"".join(s)}</g>'
               f'<rect width="{W}" height="{H}" fill="url(#{vig})"/>')
