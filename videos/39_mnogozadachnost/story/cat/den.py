"""Ночная комната Димы рилса 32 (сцена desk): обои, окно на ночной город, настенные часы, пробковая доска с пустыми
стикерами, полка с книгами, письменный стол с настольной лампой, пустой лист, карандаш, кружки кофе.
Манера — как у 26–29 (живая тушь ink.py, плоский цвет + одна тень, тёплый свет слоями). Мир (px):
стена до FLOOR_Y=1330, стол — столешница y 1080–1150 (x от 350), Дима сидит слева лицом вправо (таз (230, 1262)).
Каждая функция возвращает SVG в мировых координатах; камера — снаружи (scene.py).
"""
import math

import numpy as np

import kitchen
import lib
import room
from lib import INK, T, blob, ellipse_pts, line, mix, rect_pts, shape

FLOOR_Y = 1330
WIN = (40.0, 250.0, 380.0, 800.0)
CLOCK = (600.0, 470.0, 96.0)
DESK_T, DESK_F = 1080.0, 1150.0       # столешница: задний край, передний край
DESK_X0 = 350.0
LAMP_B = (985.0, 1084.0)
SHEET = (572.0, 1112.0)               # центр листа на столе (боковой вид)
WALL, WALL_SH, WALL_ST = "#4d6170", "#3f5160", "#56697a"
WOOD, WOOD_SH, WOOD_HI, WOOD_DK = "#9a6238", "#74462a", "#b97c4d", "#56331d"


def rsd(*k):
    return room.rsd(*k)


# ═════════════════════════ стена ═════════════════════════
DAY_WALL = ("#cfe0d6", "#b6cbbf", "#dce9e1")


def wall(t, day=False):
    s = []
    W_, SH_, ST_ = DAY_WALL if day else (WALL, WALL_SH, WALL_ST)
    lib.DEFS.append('<pattern id="pWall32" width="90" height="120" patternUnits="userSpaceOnUse">'
                    f'<rect width="90" height="120" fill="{W_}"/><rect x="0" width="30" height="120" fill="{ST_}" opacity=".55"/>'
                    f'<path d="M60 18 l7 12 l-7 12 l-7 -12 Z M60 78 l7 12 l-7 12 l-7 -12 Z" fill="{SH_}" opacity=".7"/></pattern>')
    s.append(f'<rect x="-600" y="-600" width="2400" height="{FLOOR_Y + 600}" fill="url(#pWall32)"/>')
    # плинтус
    s.append(shape(rect_pts(-600, FLOOR_Y - 34, 1800, FLOOR_Y + 4), "#3a2a22", blob(rect_pts(-600, FLOOR_Y - 12, 1800, FLOOR_Y + 4), "#271b15", .9),
                   w=3.6, seed=4001))
    return "".join(s)


def window(t, day=False):
    x0, y0, x1, y1 = WIN
    if day:
        sky = lib.lin_grad([(0, "#7cc3ea", 1), (.7, "#b5e0f4", 1), (1, "#dff2fa", 1)], 0, 0, 0, 1)
    else:
        sky = lib.lin_grad([(0, "#0e1430", 1), (.6, "#1d2a52", 1), (1, "#33406e", 1)], 0, 0, 0, 1)
    inner = [f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>']
    if day:
        # солнце и облака
        inner.append(blob(ellipse_pts(x0 + 250, y0 + 110, 62, 62, 18), "#fff3c0", .7))
        inner.append(blob(ellipse_pts(x0 + 250, y0 + 110, 44, 44, 18), "#ffe17a"))
        for k, (cx, cy, rr) in enumerate([(x0 + 90 + 14 * math.sin(t * .4), y0 + 200, 46), (x0 + 260 - 10 * math.sin(t * .3), y0 + 300, 38)]):
            cl = [(cx - rr * 1.6, cy + rr * .4), (cx - rr * 1.2, cy - rr * .3), (cx - rr * .5, cy - rr * .8), (cx + rr * .3, cy - rr * .6),
                  (cx + rr * 1.1, cy - rr * .2), (cx + rr * 1.6, cy + rr * .4)]
            inner.append(shape(cl, "#ffffff", blob([(cx - rr * 1.5, cy + rr * .15), (cx + rr * 1.5, cy + rr * .15), (cx + rr * 1.6, cy + rr * .4),
                                                    (cx - rr * 1.6, cy + rr * .4)], "#dcebf3"), w=3, seed=3260 + k))
    else:
        # луна и звёзды
        inner.append(blob(ellipse_pts(x0 + 250, y0 + 110, 46, 46, 18), "#f6ecc8"))
        inner.append(blob(ellipse_pts(x0 + 270, y0 + 96, 40, 42, 18), "#1d2a52"))
        rs = rsd(3201)
        for k in range(14):
            x, y = rs.uniform(x0 + 10, x1 - 10), rs.uniform(y0 + 20, y0 + 300)
            r = rs.uniform(2, 4) * (.75 + .25 * math.sin(t * 3 + k * 1.7))
            inner.append(blob(ellipse_pts(x, y, r, r, 6), "#f3ead0"))
    # дома: дальние тёмные, ближние с окнами
    far = [(x0 - 20, y1 - 330), (x0 + 60, y1 - 330), (x0 + 60, y1 - 390), (x0 + 140, y1 - 390), (x0 + 140, y1 - 300), (x0 + 220, y1 - 300),
           (x0 + 220, y1 - 420), (x0 + 290, y1 - 420), (x0 + 290, y1 - 340), (x1 + 20, y1 - 340), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)]
    inner.append(blob(far, "#9fb7c9" if day else "#1a2140"))
    if day:
        houses = [(x0 - 10, y1 - 250, 120, "#e3b48a"), (x0 + 120, y1 - 200, 110, "#d98f74"), (x0 + 240, y1 - 280, 120, "#e8d2a6")]
    else:
        houses = [(x0 - 10, y1 - 250, 120, "#252d52"), (x0 + 120, y1 - 200, 110, "#2c3560"), (x0 + 240, y1 - 280, 120, "#232b4e")]
    for i, (x, y, w, col) in enumerate(houses):
        inner.append(shape(rect_pts(x, y, x + w, y1 + 30), col, blob(rect_pts(x + w * .72, y, x + w, y1 + 30), "#000000" if day else "#1b2242",
                                                                       .15 if day else .8), w=3, seed=3210 + i))
        rs = rsd(3220, i)
        for r in range(6):
            for c in range(int(w // 34)):
                wx, wy = x + 12 + c * 34, y + 18 + r * 46
                if wy > y1:
                    continue
                lit = rs.uniform() < .45
                tw = 1.0 if not (lit and rs.uniform() < .2) else .7 + .3 * math.sin(t * 2.5 + i * 3 + r + c)
                col_w = ("#8fc3e0" if lit else "#5d7f99") if day else (mix("#2a2f55", "#ffc56a", tw) if lit else "#1e2546")
                inner.append(blob(rect_pts(wx, wy, wx + 18, wy + 26), col_w))
    fr = "#e8dcc6"
    mx, my = (x0 + x1) / 2, y0 + (y1 - y0) * .45
    inner.append(blob(rect_pts(mx - 10, y0, mx + 10, y1), fr) + blob(rect_pts(x0, my - 10, x1, my + 10), fr))
    s = [shape(rect_pts(x0 - 22, y0 - 22, x1 + 22, y1 + 22, 6), fr, blob(rect_pts(x1, y0 - 22, x1 + 22, y1 + 22), "#c8baa2", .9), w=4.6, seed=3230)]
    s.append(shape(rect_pts(x0, y0, x1, y1, 4), "#b5e0f4" if day else "#1d2a52", "".join(inner), w=4, seed=3231))
    # блики стекла
    for k, (a, b) in enumerate([((x0 + 26, y0 + 130), (x0 + 110, y0 + 40)), ((x0 + 40, y0 + 190), (x0 + 150, y0 + 80))]):
        s.append(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="#ffffff" stroke-opacity=".1" stroke-width="{12 - k * 4}" stroke-linecap="round"/>')
    # подоконник
    s.append(shape(rect_pts(x0 - 44, y1 + 16, x1 + 44, y1 + 46, 4), "#efe4d0", blob(rect_pts(x0 - 44, y1 + 34, x1 + 44, y1 + 46), "#cbbda4", .9),
                   w=4, seed=3232))
    s.append(room.pot(x1 - 70, y1 + 16, .9, 3240, leaves=6, col="#5f86a8"))
    # штора справа от окна (складки)
    cx0 = x1 + 30
    cur = [(cx0, y0 - 60), (cx0 + 70, y0 - 60), (cx0 + 82, y0 + 200), (cx0 + 64, y1 + 60), (cx0 + 96, FLOOR_Y - 60, 1), (cx0 + 6, FLOOR_Y - 60, 1),
           (cx0 + 14, y1)]
    inn = blob([(cx0 + 40, y0 - 60), (cx0 + 70, y0 - 60), (cx0 + 82, y0 + 200), (cx0 + 64, y1 + 60), (cx0 + 96, FLOOR_Y - 60), (cx0 + 56, FLOOR_Y - 60)],
               "#7d3b3b", .8)
    for k in range(3):
        xx = cx0 + 20 + k * 22
        inn += line([(xx, y0 - 40), (xx + 4, y0 + 300), (xx + 12, FLOOR_Y - 80)], 2.4, "#5e2b2b", seed=3250 + k, op=.8)
    s.append(shape(cur, "#a24f48", inn, w=4.2, seed=3249))
    s.append(shape(rect_pts(x0 - 70, y0 - 78, x1 + 150, y0 - 62, 6), "#3a2a22", "", w=3, seed=3248))
    return "".join(s)


# ═════════════════════════ часы ═════════════════════════
def clock(hour_a, min_a, jolt=0.0, tilt=0.0):
    """Настенные часы: углы стрелок в градусах от 12 по часовой; jolt — дрожь от щелчка, tilt — качание на гвозде."""
    cx, cy, r = CLOCK
    s = [blob(ellipse_pts(cx + 8, cy + 12, r + 12, r + 12, 28), "#0b0f1c", .35, lib.blur(6))]
    inner = blob(ellipse_pts(cx + r * .22, cy + r * .22, r, r, 28), "#e3d8bf", .9)
    for i in range(60):
        a = math.radians(i * 6 - 90)
        big = i % 5 == 0
        r0, r1 = (r * .86, r * (.68 if i % 15 == 0 else .74)) if big else (r * .86, r * .8)
        inner += line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], 6 if big else 2.2, INK,
                      taper=.1, wmin=.8, seed=3300 + i)
    g = [shape(ellipse_pts(cx, cy, r + 16, r + 16, 28), "#2f3a4e", blob(ellipse_pts(cx + 6, cy + 8, r + 10, r + 10, 28), "#232c3c", .8), w=4.8, seed=3290)]
    g.append(shape(ellipse_pts(cx, cy, r, r, 28), "#f7f0dc", inner, w=3.8, seed=3291))

    def hand(ang, L, w, tail, sd):
        a = math.radians(ang - 90)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        P = lambda u, v: (cx + ux * u + nx * v, cy + uy * u + ny * v)  # noqa: E731
        pts = [P(-tail, -w * .35), P(L * .15, -w / 2), P(L * .82, -w * .32), P(L, 0) + (1,), P(L * .82, w * .32), P(L * .15, w / 2), P(-tail, w * .35)]
        return shape(pts, "#2a2532", "", w=3.2, seed=sd)
    g.append(hand(hour_a, r * .5, 16, 14, 3310))
    g.append(hand(min_a, r * .76, 11, 18, 3311))
    g.append(shape(ellipse_pts(cx, cy, 9, 9, 12), "#d8483c", "", w=3, seed=3312))
    g.append(line([(cx - r * .62, cy - r * .2), (cx - r * .5, cy - r * .5), (cx - r * .22, cy - r * .64)], 6, "#ffffff", taper=.6, seed=3313, op=.7))
    jx = jolt * 3 * math.sin(jolt * 40)
    s.append(f'<g transform="translate({jx:.2f} 0) rotate({tilt:.2f} {cx} {cy - r - 14})">{"".join(g)}</g>')
    return "".join(s)


def clock_click(u, k=1.0):
    """Штрихи щелчка вокруг часов (u 0..1 — разлёт)."""
    if u <= 0 or u >= 1:
        return ""
    cx, cy, r = CLOCK
    o = []
    for j in range(8):
        a = math.radians(j * 45 + 22)
        r0, r1 = r + 26 + 30 * u, r + 46 + 52 * u
        o.append(line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], 7 * k, "#ffd36a",
                      seed=3330 + j, op=1 - u, taper=.3, wmin=.4))
    return "".join(o)


# ═════════════════════════ пробковая доска и полка ═════════════════════════
def board(t):
    x0, y0, x1, y1 = 700, 250, 1010, 520
    inner = []
    rs = rsd(3401)
    for k in range(70):
        x, y = rs.uniform(x0, x1), rs.uniform(y0, y1)
        inner.append(blob(ellipse_pts(x, y, 3, 2, 6), "#a87a48", .7))
    s = [shape(rect_pts(x0 - 16, y0 - 16, x1 + 16, y1 + 16, 4), "#7a5233", "", w=4, seed=3400)]
    s.append(shape(rect_pts(x0, y0, x1, y1), "#c8955e", "".join(inner), w=3, seed=3402))
    # пустые стикеры на кнопках (без букв)
    for k, (x, y, a, col) in enumerate([(760, 320, -6, "#f6e27a"), (880, 300, 4, "#f4a7b0"), (950, 420, -3, "#9fd3c7"), (790, 440, 7, "#f6e27a")]):
        n = blob(T(rect_pts(-46, -42, 46, 42, 3), x + 4, y + 6, 1, a), "#000000", .18)
        n += shape(T(rect_pts(-46, -42, 46, 42, 3), x, y, 1, a), col, blob(T([(-46, 20), (46, 18), (46, 42), (-46, 42)], x, y, 1, a), "#000000", .08), w=2.8,
                   seed=3410 + k)
        n += shape(ellipse_pts(x + 2 * math.sin(math.radians(a)), y - 34, 7, 7, 10), "#d8483c", "", w=2.2, seed=3420 + k)
        s.append(n)
    return "".join(s)


def shelf(t):
    y = 660
    x0, x1 = 680, 1120
    s = [shape(rect_pts(x0, y, x1, y + 20), WOOD_HI, blob(rect_pts(x0, y + 10, x1, y + 20), WOOD_SH, .9), w=3.6, seed=3500)]
    for k, x in enumerate((720, 1060)):
        s.append(shape([(x - 8, y + 20, 1), (x + 8, y + 20, 1), (x + 8, y + 56, 1), (x - 26, y + 20, 1)], WOOD_DK, w=3, seed=3501 + k))
    cols = ["#c44f3a", "#3f7a72", "#e0a93a", "#5f6fa8", "#8a5a8a", "#d8cfb8", "#4f8ea0"]
    x = 712
    rs = rsd(3510)
    for k in range(9):
        w = rs.uniform(18, 30)
        h = rs.uniform(70, 104)
        lean = 0 if k != 6 else -14
        col = cols[k % len(cols)]
        pts = T(rect_pts(0, -h, w, 0), x, y, 1, lean, 0, 0) if lean == 0 else T(rect_pts(0, -h, w, 0), x + 8, y, 1, lean)
        inn = blob(T(rect_pts(w * .65, -h, w, 0), x, y, 1, 0) if lean == 0 else T(rect_pts(w * .65, -h, w, 0), x + 8, y, 1, lean), "#000000", .18)
        inn += blob(T(rect_pts(0, -h * .8, w, -h * .72), x, y, 1, 0) if lean == 0 else T(rect_pts(0, -h * .8, w, -h * .72), x + 8, y, 1, lean),
                    "#f2e6c8", .7)
        s.append(shape(pts, col, inn, w=2.8, seed=3520 + k))
        x += w + (2 if k != 5 else 12)
    # стопка книг лёжа и кактус
    for k in range(3):
        s.append(shape(rect_pts(960 + k * 4, y - 22 - k * 20, 1060 - k * 6, y - k * 20), ["#3f7a72", "#e0a93a", "#c44f3a"][k], "", w=2.8, seed=3540 + k))
    s.append(room.pot(1010, y - 62, .6, 3550, leaves=4, col="#d8cfb8"))
    return "".join(s)


# ═════════════════════════ пол ═════════════════════════
def floor():
    s = [blob([(-600, FLOOR_Y), (1800, FLOOR_Y), (1800, 2800), (-600, 2800)], "#6e4a32")]
    vx, vy = 540, 700
    for k in range(-14, 16):
        xb = 540 + k * 140
        x0 = vx + (xb - vx) * (FLOOR_Y - vy) / (2800 - vy)
        s.append(line([(x0, FLOOR_Y), (xb, 2800)], 2.4, "#4f3220", seed=3600 + k + 20, op=.7, taper=.1, wmin=.7))
    rug = [(-60, 1420), (900, 1420), (1010, 1600, 1), (-160, 1600, 1)]
    s.append(shape(rug, "#3f6e8a", blob([(-160, 1520), (1010, 1520), (1010, 1600), (-160, 1600)], "#2f5670", .8) +
                   line([(-30, 1440), (870, 1440), (960, 1580), (-120, 1580), (-30, 1440)], 3, "#e0c08a", seed=3651, op=.8), w=4, seed=3650))
    return "".join(s)


# ═════════════════════════ стол ═════════════════════════
def desk_back():
    """Задние ножки стола (за ногами Димы)."""
    s = []
    for k, x in enumerate((400, 1120)):
        s.append(shape(rect_pts(x - 14, DESK_F, x + 14, FLOOR_Y + 70), WOOD_SH, "", w=3.4, seed=3700 + k))
    return "".join(s)


def desk_top():
    s = []
    x0, x1 = DESK_X0, 1400
    top = [(x0 + 20, DESK_T, 1), (x1, DESK_T, 1), (x1, DESK_F, 1), (x0, DESK_F, 1)]
    inner = blob([(x0, DESK_T + 52), (x1, DESK_T + 52), (x1, DESK_F), (x0, DESK_F)], mix(WOOD_HI, "#000000", .08), .9)
    for k, y in enumerate((DESK_T + 20, DESK_T + 42)):
        inner += line([(x0 + 60, y), (x0 + 300, y + 2), (x1, y - 1)], 1.6, WOOD_SH, seed=3710 + k, op=.45)
    s.append(shape(top, WOOD_HI, inner, w=4.2, seed=3711))
    s.append(shape(rect_pts(x0, DESK_F, x1, DESK_F + 30), WOOD, blob(rect_pts(x0, DESK_F + 18, x1, DESK_F + 30), WOOD_SH, .9), w=4, seed=3712))
    # тумба с ящиками справа и передняя ножка слева
    s.append(shape(rect_pts(x0 + 14, DESK_F + 30, x0 + 46, FLOOR_Y + 110), WOOD, blob(rect_pts(x0 + 32, DESK_F + 30, x0 + 46, FLOOR_Y + 110), WOOD_SH, .9),
                   w=3.6, seed=3713))
    tx0 = 780
    s.append(shape(rect_pts(tx0, DESK_F + 30, x1, FLOOR_Y + 110), WOOD, blob(rect_pts(tx0, DESK_F + 30, tx0 + 22, FLOOR_Y + 110), WOOD_SH, .6), w=4,
                   seed=3714))
    for k, (y0, y1) in enumerate(((DESK_F + 48, DESK_F + 170), (DESK_F + 186, DESK_F + 300))):
        s.append(shape(rect_pts(tx0 + 24, y0, x1 - 20, y1, 4), WOOD_HI, blob(rect_pts(tx0 + 24, y1 - 14, x1 - 20, y1), WOOD_SH, .8), w=3, seed=3720 + k))
        s.append(shape(rect_pts(tx0 + 110, (y0 + y1) / 2 - 7, tx0 + 170, (y0 + y1) / 2 + 7, 7), "#d9c08a", "", w=2.4, seed=3730 + k))
    return "".join(s)


def lamp(t, on=1.0):
    bx, by = LAMP_B
    s = []
    s.append(blob(ellipse_pts(bx - 10, by + 4, 70, 12, 14), "#1a100a", .35, lib.blur(4)))
    s.append(shape([(bx - 66, by, 1), (bx + 66, by, 1), (bx + 56, by - 22), (bx - 56, by - 22)], "#2f6f63",
                   blob([(bx + 20, by - 22), (bx + 56, by - 22), (bx + 66, by), (bx + 26, by)], "#225449", .9), w=4, seed=3800))
    j1 = (bx + 10, by - 26)
    j2 = (bx + 50, by - 240)
    j3 = (bx - 120, by - 330)
    for a, b, sd in ((j1, j2, 3801), (j2, j3, 3802)):
        s.append(line([a, b], 17, INK, taper=.02, wmin=.95, seed=sd))
        s.append(line([a, b], 9, "#3d8a7c", taper=.02, wmin=.95, seed=sd + 10))
    s.append(shape(ellipse_pts(*j2, 13, 13, 10), "#225449", "", w=3, seed=3803))
    # абажур: смотрит вниз-влево на лист
    ang = 32
    shade = T([(-26, -20), (30, -20), (78, 60), (-78, 60)], j3[0], j3[1] + 20, 1, ang, j3[0], j3[1] + 20)
    s.append(shape(T(ellipse_pts(0, 62, 66, 16, 14), j3[0], j3[1] + 20, 1, ang, j3[0], j3[1] + 20), "#fff6d0" if on > .5 else "#cfc6b0", "", w=3,
                   seed=3804))
    s.append(shape(shade, "#2f6f63", blob(T([(8, -20), (30, -20), (78, 60), (30, 60)], j3[0], j3[1] + 20, 1, ang, j3[0], j3[1] + 20), "#225449", .9) +
                   line(T([(-50, 40), (-14, -12)], j3[0], j3[1] + 20, 1, ang, j3[0], j3[1] + 20), 2.4, "#5fae9c", seed=3806, op=.8), w=4, seed=3805))
    return "".join(s)


def lamp_cone(t, on=1.0):
    """Тёплый конус света от абажура на стол (screen)."""
    if on <= 0:
        return ""
    fl = 1 + .015 * math.sin(t * 7.3) + .01 * math.sin(t * 13)
    g = lib.lin_grad([(0, "#fff0c0", .42 * on * fl), (1, "#ffd890", 0)], 0, 0, 0, 1)
    pts = [(840, 790), (900, 830), (760, 1150), (380, 1150)]
    return f'<path d="{lib.fill_d([p + (1,) for p in pts])}" fill="url(#{g})" style="mix-blend-mode:screen" {lib.blur(14)}/>'


def glow(on=1.0):
    g = lib.rad_grad([(0, "#ffd890", .55 * on), (.45, "#ffbe6a", .2 * on), (1, "#ffbe6a", 0)], 760, 1000, 900, 760)
    g2 = lib.rad_grad([(0, "#000000", 0), (.5, "#000000", 0), (1, "#0a0c1e", .55)], 700, 1000, 1300, 1300)
    return (f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
            f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g2})"/>')


# ═════════════════════════ предметы на столе ═════════════════════════
def sheet_side(x=None, y=None, k=1.0):
    """Лист бумаги на столе в боковом виде (тонкий ромб в перспективе)."""
    x = SHEET[0] if x is None else x
    y = SHEET[1] if y is None else y
    pts = [(x - 110 * k, y - 12 * k, 1), (x + 96 * k, y - 14 * k, 1), (x + 120 * k, y + 16 * k, 1), (x - 128 * k, y + 16 * k, 1)]
    return (blob([(p[0] + 6, p[1] + 5) for p in pts], "#3a2410", .25) +
            shape(pts, "#fbf8f0", blob([(x - 128 * k, y + 8 * k), (x + 120 * k, y + 8 * k), (x + 120 * k, y + 16 * k), (x - 128 * k, y + 16 * k)],
                                      "#e3dccb", .9), w=3, seed=3900))


def pencil(a, b, w=11.0, seed=3910):
    """Карандаш от a (тупой конец с ластиком) к b (острие)."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0]])
    h = w / 2
    P = lambda s_, v: tuple(a + u * s_ + n * v)  # noqa: E731
    er = L * .1
    tip = L * .82
    body = [P(er, -h) + (1,), P(tip, -h) + (1,), P(tip, h) + (1,), P(er, h) + (1,)]
    out = [shape([P(0, -h) + (1,), P(er, -h) + (1,), P(er, h) + (1,), P(0, h) + (1,)], "#e8a0a8", "", w=2.6, seed=seed)]
    out.append(shape([P(er - 3, -h - 1) + (1,), P(er + 6, -h - 1) + (1,), P(er + 6, h + 1) + (1,), P(er - 3, h + 1) + (1,)], "#c9c2b0", "", w=2.2, seed=seed + 1))
    out.append(shape(body, "#f2b33a", blob([P(er + 6, 0), P(tip, 0), P(tip, h), P(er + 6, h)], "#d4902a"), w=2.6, seed=seed + 2))
    out.append(shape([P(tip, -h) + (1,), P(L, 0) + (1,), P(tip, h) + (1,)], "#efd2a6", blob([P(L * .94, -h * .3), P(L, 0), P(L * .94, h * .3)], "#3a3036"),
                     w=2.4, seed=seed + 3))
    return "".join(out)


def mug(x, y, k, col, fill=None, steam_t=None, rot=0.0, ring=False):
    """Кружка сбоку (kitchen.mug): fill — None (пустая, тёмное дно) / 'coffee'. steam_t — пар."""
    o = [blob(ellipse_pts(x + 8 * k, y + 2, 56 * k, 10 * k, 12), "#1a100a", .3)]
    o.append(kitchen.mug(x, y, k, rot, col=col))
    if fill == "coffee":
        o.append(blob(T(ellipse_pts(0, -128, 42, 8, 14), x, y, k, rot), "#5a3220"))
        o.append(blob(T(ellipse_pts(-10, -129, 16, 3, 8), x, y, k, rot), "#8a5636", .9))
    elif ring:
        o.append(blob(T(ellipse_pts(0, -127, 34, 5, 12), x, y, k, rot), "#5a3220", .8))
    if steam_t is not None:
        o.append(steam(x, y - 140 * k, k, steam_t))
    return "".join(o)


def steam(x, y, k, t, op=1.0):
    o = []
    for j in range(3):
        ph = t * .9 + j * .37
        u = ph % 1.0
        a = math.sin(math.pi * u) * op
        sx = x + (-22 + j * 22) * k
        pts = [(sx, y - u * 40 * k), (sx + 9 * k * math.sin(ph * 6 + j), y - 50 * k - u * 60 * k),
               (sx - 6 * k * math.sin(ph * 5 + j) + 8 * k, y - 100 * k - u * 70 * k)]
        o.append(line(pts, 9 * k, "#fff6e6", seed=3950 + j, op=.6 * a, taper=.5, wmin=.2))
    return "".join(o)


MUGS = [(752.0, 1104.0, .44, "#c44f3a", "e"), (812.0, 1116.0, .46, "#e0a93a", "e"), (700.0, 1100.0, .4, "#5f6fa8", "e")]
