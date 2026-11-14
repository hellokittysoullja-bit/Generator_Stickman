"""Рилс 58 группа B: s05 (6.9–8.7) комната Димы днём: Дима сгорблен над конспектом; на 7.6 с подоконника (справа) прыгает кот,
садится на стол рядом и поворачивается к зрителю, огонёк на хвосте качается. Камера: дрейф к коту."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bits  # noqa: E402
import cat  # noqa: E402
import dima  # noqa: E402
import fxprops as fp  # noqa: E402
import lib  # noqa: E402
from lib import H, W, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, rad_grad, rect_pts, shape, smooth, spring, svg  # noqa: E402

SEED = 5000
T_JUMP = 7.52
T_FLY = 0.44
T_LAND = T_JUMP + T_FLY
SILL = (1015, 846)
LAND = (775, 1178)
DESK_Y = 1118


def lerp(a, b, u):
    return a + (b - a) * u


def room(t):
    s = []
    g = lin_grad([(0, "#f4e4c8", 1), (1, "#ebd3ac", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-600" width="2300" height="1500" fill="url(#{g})"/>')
    for x in range(-400, 1500, 210):
        s.append(f'<rect x="{x}" y="-600" width="90" height="1500" fill="#efd9b6"/>')
    s.append(f'<rect x="-600" y="880" width="2300" height="1200" fill="#c9965f"/>')
    for i, y in enumerate((960, 1180, 1480, 1800)):
        s.append(line([(-600, y), (1700, y + 5)], 3, "#a97542", taper=0, wmin=1, seed=SEED + 3 + i, op=.8))
    s.append(line([(-600, 880), (1700, 880)], 6, "#7a5430", taper=0, wmin=1, seed=SEED + 2))
    # окно справа: небо, облако, рама, подоконник
    x0, y0, x1, y1 = 720, 300, 1230, 770
    s.append(shape(rect_pts(x0 - 18, y0 - 18, x1 + 18, y1 + 18, 6), "#fdf8ec", "", w=5.5, seed=SEED + 10))
    sky = lin_grad([(0, "#a9d8f2", 1), (1, "#e2f2fa", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{sky})"/>')
    s.append(blob(ellipse_pts(x0 + 90, y0 + 90, 40, 40, 14), "#fff1b0"))
    s.append(blob(ellipse_pts(900 + 8 * math.sin(t * .6), 470, 100, 30, 14), "#ffffff") + blob(ellipse_pts(960 + 8 * math.sin(t * .6), 445, 60, 28, 14), "#ffffff"))
    s.append(line([(970, y0), (970, y1)], 10, "#fdf8ec", taper=0, wmin=1, seed=SEED + 11))
    s.append(shape(rect_pts(x0, y0, x1, y1, 2), "none", "", w=4.2, seed=SEED + 12))
    s.append(shape(rect_pts(x0 - 50, y1 + 18, x1 + 60, y1 + 62, 6), "#e8d3a8",
                   blob([(x0 - 50, y1 + 48), (x1 + 60, y1 + 48), (x1 + 60, y1 + 62), (x0 - 50, y1 + 62)], "#c8aa78"), w=5, seed=SEED + 13))
    # лучи света из окна на стол
    s.append(f'<path d="M 760 800 L 1000 800 L 640 1200 L 300 1200 Z" fill="#fff7d8" opacity=".30"/>')
    return "".join(s)


def desk():
    s = []
    top = [(-80, DESK_Y, 1), (1160, DESK_Y, 1), (1230, 1200, 1), (-150, 1200, 1)]
    s.append(shape(top, bits.C_TABLE, blob([(-150, 1160), (1230, 1160), (1230, 1200), (-150, 1200)], "#b98a52", .9) +
                   "".join(line([(-60 + i * 260, DESK_Y + 20), (-100 + i * 262, 1190)], 2.5, "#b98a52", taper=.2, wmin=.7, seed=SEED + 20 + i, op=.8) for i in range(6)),
                   w=5.5, seed=SEED + 19))
    s.append(shape(rect_pts(-150, 1200, 1230, 1262), bits.C_TABLE_EDGE, "", w=5.5, seed=SEED + 30))
    for k, x in enumerate((20, 960)):
        s.append(shape(rect_pts(x, 1262, x + 66, 1900), bits.C_LEG, blob([(x + 40, 1262), (x + 66, 1262), (x + 66, 1900), (x + 40, 1900)], "#5f676d", .9), w=5, seed=SEED + 31 + k))
    s.append(blob(rect_pts(-150, 1262, 1230, 1900), "#6b4524", .42))
    return "".join(s)


def notebook(t, bounce):
    """Раскрытый конспект: бумага, корешок, строки-штрихи по обеим страницам."""
    y = DESK_Y + 30 + bounce
    s = []
    pg = [(130, y + 4, 1), (330, y - 36, 1), (360, y + 124, 1), (110, y + 134, 1)]
    pg2 = [(330, y - 36, 1), (535, y - 2, 1), (560, y + 140, 1), (360, y + 124, 1)]
    s.append(shape(pg, bits.C_PAPER, blob([(300, y), (330, y - 36), (360, y + 124), (320, y + 126)], bits.C_PAPER_SH, .9), w=4.6, seed=SEED + 40))
    s.append(shape(pg2, bits.C_PAPER, blob([(330, y - 36), (360, y - 28), (380, y + 124), (360, y + 124)], bits.C_PAPER_SH, .9), w=4.6, seed=SEED + 41))
    for i in range(5):
        yy = y + 8 + i * 22
        s.append(line([(148 + i * 3, yy - i * 1.5), (310, yy - 24 - i * 1)], 3.4, bits.HINK, taper=.3, wmin=.5, seed=SEED + 50 + i, peak=.5, op=.9))
        s.append(line([(372, yy - 24), (522, yy - 4)], 3.4, bits.HINK, taper=.3, wmin=.5, seed=SEED + 60 + i, peak=.5, op=.9))
    return "".join(s)


def hand_flat(x, y, ang=0.0, k=1.0, sd=0, flip=1):
    """Кисть, лежащая на странице: ладонь-тыл и четыре пальца-колбаски (вид сверху-спереди)."""
    o = []
    pts = [(-40, -10), (-20, -34), (30, -36), (62, -18), (66, 16), (40, 36), (-20, 34), (-44, 14)]
    o.append(shape(pts, dima.SKIN, blob([(-44, 14), (-20, 34), (40, 36), (66, 16), (30, 18)], dima.SKIN_SH, .9), w=4.6, seed=sd))
    for j in range(4):
        fy = -26 + j * 17
        fp_ = [(60, fy - 8), (104, fy - 8 + j * 1.5), (112, fy + 1 + j), (100, fy + 8 + j), (60, fy + 8)]
        o.append(shape(fp_, dima.SKIN, blob([(60, fy + 3), (104, fy + 4 + j), (100, fy + 8 + j), (60, fy + 8)], dima.SKIN_SH, .85), w=3.8, seed=sd + 3 + j))
    o.append(line([(-20, -20), (24, -22)], 2.4, dima.SKIN_SH2, seed=sd + 9, op=.7))
    tr = f'translate({f(x)} {f(y)}) rotate({f(ang)}) scale({f(k * flip)} {f(k)})'
    return f'<g transform="{tr}">{"".join(o)}</g>'


def forearm(a, b, w0=92, w1=70, sd=0):
    pts = lib.band([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 20), b], w0, w1, step=6, cap=True)
    return shape(pts, dima.HOOD, blob(lib.band([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 40), b], 40, 30, step=6, cap=True), dima.HOOD_SH, .8) +
                 line([(a[0] + 30, a[1] + 30), ((a[0] + b[0]) / 2 + 10, (a[1] + b[1]) / 2 + 40)], 3.4, dima.FOLD, seed=sd + 1, op=.7), w=5.2, seed=sd)


def cat_st(t):
    st = cat.__dict__.get("_x", None)
    flip = t - T_LAND
    look = (0.0, 0.0)
    turn = 0.0
    if t < T_JUMP:
        turn, look = -0.75, (-0.8, 0.35)
    elif t < T_LAND + 0.2:
        turn, look = -0.6, (-0.7, 0.3)
    else:
        u = ease_io(clamp((t - T_LAND - 0.2) / 0.35))
        turn, look = lerp(-0.6, 0.05, u), (lerp(-0.7, 0.0, u), lerp(0.3, 0.0, u))
    tilt = 0.0
    if t > T_LAND + 0.55:
        tilt = 7 * ease_io(clamp((t - T_LAND - 0.55) / 0.3))          # склонил голову
    blink = 0.0
    for tb in (7.18, 8.34):
        d = abs(t - tb)
        if d < .09:
            blink = 1 - d / .09
    ear = 0.6 * math.sin(t * 9) if (T_LAND + 0.2 < t < T_LAND + 0.6) else 0.0
    return dict(look=look, turn=turn, blink=blink, ear=ear, perk=0.0, tail=7 * math.sin(t * 3.4) + (18 if T_JUMP - .3 < t < T_LAND else 0), smile=0,
                tilt=tilt, flame_e=1.0 + .25 * math.sin(t * 5), drop=0.0)


def cat_pose(t):
    """(x, y, k, squash_x, squash_y, rot) кота по времени: сидит на подоконнике → присел → полёт → посадка → сидит на столе."""
    ks, kl = 0.52, 0.84
    if t < T_JUMP - 0.2:
        return SILL[0], SILL[1], ks, 1.0, 1.0, 0.0
    if t < T_JUMP:                                            # присел перед прыжком
        u = (t - (T_JUMP - 0.2)) / 0.2
        return SILL[0], SILL[1], ks, 1 + .12 * u, 1 - .22 * u, -3 * u
    if t < T_LAND:
        u = (t - T_JUMP) / T_FLY
        x = lerp(SILL[0], LAND[0], ease_io(u) * .35 + u * .65)
        y = lerp(SILL[1], LAND[1], u) - 360 * 4 * u * (1 - u)
        sx, sy = 1 - .08 * math.sin(math.pi * u), 1 + .17 * math.sin(math.pi * u)
        k = lerp(ks, kl, ease_out(u))
        return x, y, k, sx, sy, -22 * math.sin(math.pi * u) * (1 if u < .5 else .6) + 14 * u
    e = t - T_LAND
    sq = math.exp(-e * 11) * math.cos(e * 30) * 0.26
    return LAND[0], LAND[1], kl, 1 + sq * .8, 1 - sq, 0.0


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    s = [room(t)]
    e = t - T_LAND
    land_bump = (math.exp(-e * 12) * math.sin(e * 35) * 7) if e > 0 else 0.0
    # кот на подоконнике до прыжка рисуется за столом
    cx, cy, k, sx, sy, rot = cat_pose(t)
    st = cat_st(t)
    cat_svg = (f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({sx:.4f} {sy:.4f}) translate({f(-cx)} {f(-cy)})">'
               f'{cat.draw(cx, cy, k, st, t)}</g>')
    in_air = T_JUMP <= t < T_LAND
    if t < T_LAND:
        s.append(cat_svg)               # подоконник и полёт — позади Димы
    flinch = (smooth(T_LAND, T_LAND + .1, t) * (1 - smooth(T_LAND + .25, T_LAND + .8, t))) if t > T_LAND else 0.0
    read = 0.5 + 0.5 * math.sin(t * 2.6)
    HO = (410, 820)
    HS = 1.55
    hy = 70 - 22 * flinch + 4 * math.sin(t * 2.0)
    expr = {"lid": 0.42 + .4 * flinch, "look": (lerp(.25, .75, read) if flinch < .05 else lerp(.2, 1.0, flinch), 0.55 - .6 * flinch),
            "brows": "worry" if flinch < .1 else "up", "mouth": "tired" if flinch < .1 else "gape", "hair": 2 * math.sin(t * 4)}
    dima.LWK = 0.82
    hd = dima.head(expr)
    cc = lib.clip_rect(-600, -600, 3000, 600 + 1262)
    s.append(f'<g clip-path="url(#{cc})"><g transform="translate({HO[0] - 10} {HO[1] - 55}) scale({HS})">{bits.hood_body(SEED + 100)}</g></g>')
    s.append(f'<g transform="translate({HO[0] + 66 - 14 * flinch} {HO[1] + hy}) rotate({17 - 12 * flinch:.2f}) scale({HS})">{hd}</g>')
    s.append(desk())
    fl = 10 * math.sin(t * 3.1)
    arms = [notebook(t, land_bump),
            forearm((60, 1020), (180, DESK_Y + 70 + land_bump), 104, 74, SEED + 200),
            hand_flat(196, DESK_Y + 92 + land_bump, -4, .85, SEED + 210),
            forearm((640, 1020), (516 + fl * .5, DESK_Y + 76 + land_bump), 104, 74, SEED + 220),
            hand_flat(504 + fl * .5, DESK_Y + 98 + land_bump, 190, .85, SEED + 230, flip=-1)]
    s.append(f'<g transform="translate(110 0)">{"".join(arms)}</g>')
    if t >= T_LAND:
        s.append(cat_svg)
        s.append(fp.dust(LAND[0], LAND[1] + 12, e / .45, 6, 150, 40, SEED + 300, "#fff6e0", 26))
    # ── камера: дрейф к коту; небольшая встряска при посадке
    u = clamp((t - 6.7) / 2.2)
    sc = lerp(1.0, 1.32, ease_io(u))
    cxx = lerp(560, 740, ease_io(u))
    cyy = lerp(990, 1040, ease_io(u))
    rot = lerp(1.4, -0.8, u)
    if e > 0:
        kk = math.exp(-e * 10)
        cyy += 14 * kk * math.sin(e * 45)
        sc *= 1 + .02 * kk
    return svg(f'<rect width="{W}" height="{H}" fill="#7a5430"/><g transform="{cam(cxx, cyy, sc, rot)}">{"".join(s)}</g>')
