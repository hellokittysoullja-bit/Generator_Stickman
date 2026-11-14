"""Мелочи группы F рилса 59: кусок пирога в зубах кота (цвета как common/props.py), крошки, искры, передняя стойка."""
import math

import numpy as np

import lib
from lib import blob, ellipse_pts, line, rrect, shape

CRUST, CRUST_SH, CRUST_HI = "#C98A4B", "#A8692F", "#E0A867"
FILL, FILL_SH = "#B8453C", "#8F2F2C"
KRAFT, KRAFT_SH = "#C9A877", "#a98a58"
TIN, TIN_SH = "#b6babd", "#8f9498"
GREEN, GREEN_SH = "#5f9a52", "#437a3c"


def _rs(seed):
    return np.random.RandomState(seed)


RX, RY = 150.0, 46.0


def piece(x, y, k=1.0, rot=0.0, flip=1):
    """Кусок пирога (клин, 40°): (x, y) — центр верхней грани, rot — поворот. Корка, торец с начинкой."""
    a0, a1 = math.radians(-20), math.radians(22)
    arc = [(141.0 * 1.0 * math.cos(a), 43.0 * math.sin(a) * 1.6) for a in np.linspace(a0, a1, 8)]
    tip = (-RX * .08, 0)
    top = [tip] + arc
    o = []
    side = [arc[-1], arc[0], (arc[0][0], arc[0][1] + 34), (arc[-1][0], arc[-1][1] + 34)]
    o.append(shape([tip, arc[-1], (arc[-1][0], arc[-1][1] + 34), (tip[0], tip[1] + 30)], FILL,
                   "".join(line([(tip[0] + (arc[-1][0] - tip[0]) * u, tip[1] + 12 + (arc[-1][1] - tip[1]) * u), (tip[0] + (arc[-1][0] - tip[0]) * u + 4, tip[1] + 26 + (arc[-1][1] - tip[1]) * u)], 2.4, FILL_SH, seed=140 + int(u * 10)) for u in (.25, .5, .75)), w=3.2, seed=130))
    o.append(shape(side, CRUST_SH, "", w=3.2, seed=131))
    o.append(shape(top, CRUST, blob([(arc[2][0], arc[2][1] - 30), (arc[-1][0] + 6, arc[-1][1] - 30), (arc[-1][0] + 6, arc[-1][1] + 6), (arc[2][0], arc[2][1] + 6)], CRUST_SH, .6) +
                   line([(tip[0] + 40, 0), (arc[3][0] - 18, arc[3][1] * .6)], 3, "#6b3f1c", seed=132, op=.9), w=3.6, seed=133))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k * flip:.4f} {k:.4f})">{"".join(o)}</g>'


def crumbs(x, y, n=8, spread=60, k=1.0, seed=0, u=1.0):
    rs = _rs(seed)
    o = []
    for i in range(n):
        dx, dy = rs.uniform(-spread, spread), rs.uniform(-spread * .35, spread * .35)
        r = rs.uniform(3, 6.5) * k
        o.append(blob(ellipse_pts(x + dx * u, y + dy * u, r, r * .8, 6, rot=rs.uniform(0, 180)), CRUST if i % 3 else FILL))
    return "".join(o)


def spark(x, y, k, u, col="#ffd45e"):
    """Четырёхлучевая искра, u 0…1 — жизнь."""
    s = k * math.sin(math.pi * min(max(u, 0), 1))
    if s < .05:
        return ""
    pts = [(x, y - 30 * s), (x + 7 * s, y - 7 * s), (x + 30 * s, y), (x + 7 * s, y + 7 * s), (x, y + 30 * s), (x - 7 * s, y + 7 * s), (x - 30 * s, y), (x - 7 * s, y - 7 * s)]
    return shape(pts, col, "", w=2.6, seed=int(x + y) % 97, var=.1)


# ═══════════════════════ кухня ═══════════════════════
def kitchen(t, x0=-500, x1=2400, horizon=1180, glow=0.0):
    """Фон кухни (тёплый день): стена, плитка, шкафчики, окно, столешница слева, пол. Низ стены — horizon."""
    o = []
    o.append(blob(rrect(x0, -300, x1, horizon, 0), "#f3e3c3"))
    o.append(blob(rrect(x0, horizon - 40, x1, horizon, 0), "#e0cba5", 1))
    # плитка-фартук
    o.append(blob(rrect(x0, 600, x1, 860, 0), "#e9f1ef"))
    for xx in range(int(x0), int(x1), 90):
        o.append(line([(xx, 600), (xx, 860)], 2, "#c5d6d2", taper=0, wmin=1, seed=400 + xx % 50, op=.9))
    for yy in (665, 730, 795):
        o.append(line([(x0, yy), (x1, yy + 3)], 2, "#c5d6d2", taper=0, wmin=1, seed=420 + yy % 50, op=.9))
    # верхние шкафы
    for i, cx0 in enumerate(range(-400, 2300, 330)):
        if 560 < cx0 < 1000 and False:
            continue
        o.append(shape(rrect(cx0, 90, cx0 + 310, 520, 10), "#6fa7a2", blob(rrect(cx0 + 160, 90, cx0 + 310, 520, 8), "#5b918c", .85) +
                       blob(rrect(cx0 + 22, 118, cx0 + 288, 492, 8), "#7db5b0", 1), w=4.4, seed=430 + i))
        o.append(line([(cx0 + 22, 118), (cx0 + 288, 118), (cx0 + 288, 492), (cx0 + 22, 492), (cx0 + 22, 118)], 3, "#4f8782", seed=440 + i, taper=0, wmin=1, op=.9))
        o.append(shape(rrect(cx0 + 134, 470, cx0 + 176, 490, 4), "#f1e6cf", "", w=3, seed=450 + i))
    # окно
    wx0, wy0, wx1, wy1 = 1180, 200, 1500, 600
    o.append(shape(rrect(wx0 - 16, wy0 - 16, wx1 + 16, wy1 + 16, 6), "#fdf8ec", "", w=5, seed=460))
    sky = lib.lin_grad([(0, "#bfe4f6", 1), (1, "#f2f8ef", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="url(#{sky})"/>')
    o.append(blob(ellipse_pts(wx0 + 80, wy0 + 90, 40, 40, 14), "#fff1b0") + blob(ellipse_pts(1340 + 8 * math.sin(t * .6), wy0 + 160, 76, 24, 14), "#ffffff"))
    o.append(line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], 8, "#fdf8ec", taper=0, wmin=1, seed=461) + line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], 8, "#fdf8ec", taper=0, wmin=1, seed=462))
    o.append(shape(rrect(wx0, wy0, wx1, wy1, 2), "none", "", w=4, seed=463))
    # шторка
    o.append(shape([(wx0 - 24, wy0 - 30), (wx0 + 70, wy0 - 30), (wx0 + 40, wy1 + 20), (wx0 - 30, wy1 + 20)], "#e9a56a", blob([(wx0 + 20, wy0 - 30), (wx0 + 70, wy0 - 30), (wx0 + 40, wy1 + 20), (wx0 + 8, wy1 + 20)], "#cf8450", .85), w=4, seed=464))
    # столешница слева со шкафами
    o.append(shape(rrect(x0, 860, 600, 900, 6), "#b98a50", blob(rrect(x0, 880, 600, 900, 4), "#9a6f3a", .9), w=4.4, seed=470))
    o.append(shape(rrect(x0, 900, 590, horizon + 60, 0), "#6fa7a2", blob(rrect(300, 900, 590, horizon + 60, 0), "#5b918c", .8), w=4.4, seed=471))
    for xx in (x0 + 90, 130, 390):
        o.append(line([(xx, 940), (xx, horizon + 20)], 3, "#4f8782", taper=0, wmin=1, seed=472 + int(xx) % 11, op=.9))
        o.append(shape(rrect(xx + 14, 950, xx + 30, 1000, 4), "#f1e6cf", "", w=3, seed=480 + int(xx) % 17))
    # пол
    o.append(blob(rrect(x0, horizon, x1, 2300, 0), "#c8955f"))
    o.append(line([(x0, horizon), (x1, horizon)], 5, "#7a5430", taper=0, wmin=1, seed=490))
    for i, yy in enumerate((horizon + 110, horizon + 270, horizon + 470, horizon + 700)):
        o.append(line([(x0, yy), (x1, yy + 4)], 3, "#a97542", taper=0, wmin=1, seed=500 + i, op=.8))
    return "".join(o)


def counter_front(x0, x1, y):
    return shape(rrect(x0, y, x1, 2200, 0), "#6fa7a2", blob(rrect(x0, y + 40, x1, y + 60, 0), "#5b918c", .9), w=4.6, seed=560) + shape(rrect(x0 - 10, y - 30, x1 + 10, y + 10, 6), "#b98a50", blob(rrect(x0, y - 8, x1, y + 10, 4), "#9a6f3a", .9), w=4.6, seed=561)


def table(x0, x1, ytop=1010, depth=120, sag=0, legs=True):
    """Стол спереди-сверху: столешница-плоскость (ytop…ytop+depth), передняя планка, ножки. Скатерть в клетку без цифр."""
    o = []
    for xx in ((x0 + 60, x1 - 120) if legs else ()):
        o.append(shape(rrect(xx, ytop + depth + 40, xx + 56, 1760, 4), "#9a6f3a", blob(rrect(xx + 28, ytop + depth + 40, xx + 56, 1760, 3), "#7f5a2e", .9), w=4.4, seed=520 + int(xx) % 13))
    o.append(shape(rrect(x0, ytop, x1, ytop + depth, 8), "#f6ecd8", blob(rrect(x0, ytop + depth * .55, x1, ytop + depth, 6), "#e8d9ba", .8), w=4.6, seed=530))
    for i in range(int(x0), int(x1), 120):
        o.append(line([(i, ytop + 8), (i - 24, ytop + depth - 6)], 3, "#e2a08a", taper=0, wmin=1, seed=540 + i % 29, op=.75))
    o.append(line([(x0 + 8, ytop + depth * .5), (x1 - 8, ytop + depth * .5)], 3, "#e2a08a", taper=0, wmin=1, seed=541, op=.75))
    o.append(shape(rrect(x0 + 10, ytop + depth, x1 - 10, ytop + depth + 74, 6), "#b98a50", blob(rrect(x0 + 10, ytop + depth + 44, x1 - 10, ytop + depth + 74, 4), "#9a6f3a", .9), w=4.4, seed=531))
    return "".join(o)


def counter_front(x0, x1, y):
    """Передняя стойка кухни (цвета common/kitchen.py): закрывает таз мамы на крупном плане."""
    o = shape(rrect(x0, y, x1, 2300, 0), "#F8F2E6", blob(rrect(x0, y + 40, x1, y + 62, 0), "#E6DCC8", .9), w=4.6, seed=560)
    for i, xx in enumerate(range(int(x0) + 150, int(x1), 300)):
        o += line([(xx, y + 14), (xx, 1900)], 3, "#C9BFA6", taper=0, wmin=1, seed=565 + i, op=.9)
    o += shape(rrect(x0 - 10, y - 34, x1 + 10, y + 8, 6), "#C88A58", blob(rrect(x0, y - 10, x1, y + 8, 4), "#A56F3E", .9), w=4.6, seed=561)
    return o
