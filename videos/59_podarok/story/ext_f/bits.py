"""Предметы и кухня группы F рилса 59: букет, пирог (целый / с вырезанным куском / кусок), банка с цветами, кухня, стол, звёзды.
Пока нет common/props.py и common/kitchen.py — свои, в тех же цветах брифа (корка #C98A4B, крафт #C9A877, плетёное #B98A50)."""
import math

import numpy as np

import lib
from lib import blob, ellipse_pts, line, rrect, shape

CRUST, CRUST_SH, CRUST_HI = "#C98A4B", "#a86d33", "#e0a964"
FILL, FILL_SH = "#d9a441", "#b9822a"
KRAFT, KRAFT_SH = "#C9A877", "#a98a58"
TIN, TIN_SH = "#b6babd", "#8f9498"
GREEN, GREEN_SH = "#5f9a52", "#437a3c"


def _rs(seed):
    return np.random.RandomState(seed)


# ═══════════════════════ цветы ═══════════════════════
def daisy(x, y, k, rot=0.0, seed=0):
    o = []
    for i in range(9):
        a = rot + i * 40.0
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        px, py = x + c * 24 * k, y + s_ * 24 * k
        o.append(shape(ellipse_pts(px, py, 17 * k, 8.5 * k, 10, rot=a), "#fbf7ee", "", w=2.6, seed=seed + i, var=.2))
    o.append(shape(ellipse_pts(x, y, 13 * k, 13 * k, 12), "#f2b632", blob(ellipse_pts(x + 3 * k, y + 4 * k, 8 * k, 7 * k, 8), "#d98f1f", .8), w=3, seed=seed + 20))
    return "".join(o)


def tulip(x, y, k, rot=0.0, col="#e2574c", col_sh="#bb3a33", seed=0):
    pts = [(-22, -34), (-8, -22, 1), (0, -46), (8, -22, 1), (22, -34), (26, 0), (14, 26), (-14, 26), (-26, 0)]
    pts = [(p[0] * k, p[1] * k) + ((1,) if len(p) > 2 else ()) for p in pts]
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(x + p[0] * c - p[1] * s_, y + p[0] * s_ + p[1] * c) + ((1,) if len(p) > 2 else ()) for p in pts]
    inner = blob([(x + (p[0] * c - p[1] * s_) * 1, y + (p[0] * s_ + p[1] * c)) for p in [(6 * k, -30 * k), (28 * k, -30 * k), (28 * k, 28 * k), (8 * k, 28 * k)]], col_sh, .85)
    return shape(pts, col, inner, w=3.2, seed=seed)


def bouquet(x, y, k=1.0, rot=0.0, sway=0.0):
    """Букет в крафте; (x, y) — место хвата рукой (низ обёртки), вверх — цветы. Высота ≈ 330 k, ширина цветов ≈ 230 k."""
    o = []
    seeds = [(-70, -250, 0), (-10, -300, 1), (62, -262, 2), (-38, -205, 3), (36, -208, 4)]
    stems = ""
    for i, (fx, fy, kind) in enumerate(seeds):
        stems += line([(0, -70), (fx * .35, (fy - 20) * .5), (fx, fy + 10)], 5.5, GREEN_SH, taper=.1, wmin=.9, seed=10 + i)
    o.append(stems)
    for (lx, ly, ang) in ((-60, -170, -35), (58, -160, 40)):
        o.append(shape(ellipse_pts(lx, ly, 38, 15, 12, rot=ang), GREEN, line([(lx - 26, ly + 8), (lx + 26, ly - 8)], 2, GREEN_SH, seed=40), w=3.2, seed=41 + int(lx)))
    for i, (fx, fy, kind) in enumerate(seeds):
        r_ = (i * 23) % 40 + sway * 6
        if kind in (0, 2):
            o.append(tulip(fx, fy, 1.15, rot=-10 + 20 * (kind == 2) + sway * 4, col=("#e2574c" if kind == 0 else "#ef8fa1"), col_sh=("#bb3a33" if kind == 0 else "#cc6a80"), seed=100 + i))
        else:
            o.append(daisy(fx, fy, 1.0 if kind == 1 else .9, rot=r_, seed=100 + i * 30))
    cone = [(-74, -150), (-20, -164), (30, -158), (78, -146), (36, 6), (-30, 6)]
    inner = blob([(8, -160), (86, -150), (44, 8), (4, 8)], KRAFT_SH, .85)
    inner += line([(-50, -146), (-16, -4)], 2.2, KRAFT_SH, seed=50, op=.9) + line([(30, -150), (20, -20)], 2.2, KRAFT_SH, seed=51, op=.9)
    o.append(shape(cone, KRAFT, inner, w=4.4, seed=52))
    o.append(shape([(-46, -92), (44, -90), (46, -74), (-44, -76)], "#8d6a3e", "", w=2.6, seed=53))
    o.append(shape([(-8, -94), (-34, -118, 1), (-16, -84), (6, -92), (30, -118, 1), (12, -80)], "#8d6a3e", "", w=2.4, seed=54))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k:.4f})">{"".join(o)}</g>'


def jar(x, y, k=1.0, sway=0.0, seed=0):
    """Банка с цветами; (x, y) — центр дна."""
    o = []
    fl = [(-30, -250, 0), (4, -290, 1), (38, -246, 2), (-4, -226, 1)]
    for i, (fx, fy, kind) in enumerate(fl):
        sx = fx + sway * 14 * (fy / -250)
        o.append(line([(fx * .3, -70), ((fx * .3 + sx) / 2, fy * .5), (sx, fy + 10)], 5, GREEN_SH, taper=.1, wmin=.9, seed=60 + i))
    for i, (fx, fy, kind) in enumerate(fl):
        sx = fx + sway * 14 * (fy / -250)
        o.append(daisy(sx, fy, .8, rot=i * 17 + sway * 8, seed=200 + i * 30) if kind != 2 else tulip(sx, fy, 1.0, rot=sway * 6, seed=300))
    body = [(-52, -150), (52, -150), (60, -130), (62, -20), (50, 0), (-50, 0), (-62, -20), (-60, -130)]
    inner = blob([(-48, -90), (50, -90), (50, 0), (-48, 0)], "#a9d8f2", .55) + blob([(20, -140), (56, -130), (58, -10), (24, -4)], "#8fc4e0", .55)
    inner += line([(-42, -130), (-44, -30)], 3, "#f4fbff", seed=70, op=.95)
    o.append(shape(body, "#d3ebf7", inner, w=3.8, seed=71))
    o.append(shape([(-56, -154), (56, -154), (54, -140), (-54, -140)], "#bcd9ea", "", w=3, seed=72))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})">{"".join(o)}</g>'


# ═══════════════════════ пирог ═══════════════════════
RX, RY, TH = 150.0, 46.0, 44.0


def _pt(a, rx=RX, ry=RY):
    return (rx * math.cos(a), ry * math.sin(a))


def pie(x, y, k=1.0, cut=None, sag=1.0, wob=0.0):
    """Кривой осевший пирог; (x, y) — центр верхней корки. cut=(a0, a1) градусов (0 — вправо, 90 — к зрителю) — вырезанный кусок; None — целый."""
    o = []
    # жестяная форма
    side = [_pt(math.radians(a)) for a in np.linspace(0, 180, 22)]
    tinp = [(p[0] * 1.06, p[1] * 1.06 + 8) for p in side] + [(p[0] * 1.06, p[1] * 1.06 + 8 + TH) for p in side[::-1]]
    o.append(shape(tinp, TIN, blob([(0, 0), (RX * 1.1, 0), (RX * 1.1, TH + 80), (0, TH + 80)], TIN_SH, .8), w=4.2, seed=80))
    full = [math.radians(a) for a in np.linspace(0, 360, 60, endpoint=False)]
    rs = _rs(7)

    def crust_pt(a, dz=0.0):
        px, py = _pt(a, RX * .97, RY * .97)
        sg = sag * 16 * (.5 + .5 * math.cos(a - .25)) + wob
        return (px, py - 18 + sg + dz + rs.uniform(-1.5, 1.5) * 0)
    if cut:
        a0, a1 = math.radians(cut[0]), math.radians(cut[1])
        # внутренность формы под вырезом и торцы разреза
        floor_ = [(0, 8)] + [(_pt(a)[0] * .97, _pt(a)[1] * .97 + 10) for a in np.linspace(a0, a1, 10)]
        o.append(blob(floor_, "#d8b47c"))
        for a in (a0, a1):
            P = crust_pt(a)
            C0 = (0, -18 + sag * 8)
            face = [C0, P, (P[0], P[1] + 36), (0, C0[1] + 36)]
            o.append(shape(face, FILL, blob([C0, P, (P[0], P[1] + 10), (0, C0[1] + 10)], CRUST_SH, .95) +
                           "".join(line([(C0[0] + (P[0] - C0[0]) * u, C0[1] + (P[1] - C0[1]) * u + 14), (C0[0] + (P[0] - C0[0]) * u + 6, C0[1] + (P[1] - C0[1]) * u + 26)], 2.6, FILL_SH, seed=90 + int(u * 10)) for u in (.2, .45, .7, .9)), w=3.4, seed=81 + int(a * 7)))
        arc = [a for a in full if not (a0 <= a % (2 * math.pi) <= a1)]
        arc = sorted(arc, key=lambda a: (a - a1) % (2 * math.pi))
        top = [crust_pt(a) for a in arc] + [(0, -18 + sag * 8)]
    else:
        top = [crust_pt(a) for a in full]
    inner = blob([(-RX * .2, -RY * .2 - 14), (RX, -RY * .2 - 14), (RX, RY), (-RX * .2, RY)], CRUST_SH, .55)
    inner += blob(ellipse_pts(-40, -34, 70, 18, 10), CRUST_HI, .8)
    for a in np.linspace(0, 6.28, 16, endpoint=False):     # защипы по краю
        if cut and cut[0] - 8 <= math.degrees(a) <= cut[1] + 8:
            continue
        p = crust_pt(a)
        q = (p[0] * .88, p[1] * .88 - 2)
        inner += line([p, q], 3.2, CRUST_SH, seed=100 + int(a * 10), op=.9, taper=.3, wmin=.4)
    o.append(shape(top, CRUST, inner, w=4.6, seed=82))
    for i, (sx, sy, sl) in enumerate(((-50, -26, 50), (6, -18, 56), (-14, 4, 46))):        # прорези и начинка выглянула
        o.append(line([(sx, sy), (sx + sl * .6, sy + 8)], 4, "#6b3f1c", seed=120 + i, taper=.4, wmin=.5))
        o.append(line([(sx + 4, sy + 4), (sx + sl * .5, sy + 11)], 2.4, FILL, seed=125 + i))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})">{"".join(o)}</g>'


def piece(x, y, k=1.0, rot=0.0, flip=1):
    """Кусок пирога (клин, 40°): (x, y) — центр верхней грани, rot — поворот. Корка, торец с начинкой."""
    a0, a1 = math.radians(-20), math.radians(22)
    arc = [(RX * .94 * math.cos(a), RY * .94 * math.sin(a) * 1.6) for a in np.linspace(a0, a1, 8)]
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
