"""Кухня Димы рилса 34 (из кухни рилса 29, перестроена под стол: Дима сидит за кухонным столом).
Исходно: кухня Димы рилса 29 (та же манера, что кухня рилсов 26/28 и кафе 27: живая тушь, плоский цвет + одна тень).

Мир (px): пол от y=1590, столешница — верх 1210, фасад 1250–1590 (x от −600 до 1240); над ней открытая полка (y 820,
x 60–540) с банками и пылью, справа навесной шкаф (x 600–1180, y 360–790), справа холодильник (x 1260–1620),
окно слева (x −560…−80), часы на стене (x 330, y 330), лампа-абажур сверху (x 520).
Свет: mode = 'night' (тёплая лампа, тёмное окно), 'morning' (солнце в окно, лучи), 'dark' (лампа выключена).
"""
import math

import numpy as np

import lib
from lib import INK, blob, ellipse_pts, line, mix, rect_pts, shape, T

FLOOR = 1330                            # стык стены и пола
CT_TOP, CT_FR = 1000, 1036              # кухонная столешница у стены (за столом)
TILE_Y0 = 790                           # фартук-кафель от TILE_Y0 до столешницы
SHELF = (-560, -170, 700)               # x0, x1, y доски (левее окна)
CUP = (840, 1340, 250, 640)            # навесной шкаф справа
FRIDGE = (1500, 1860, 300, 1340)
WIN = (40, 340, 300, 720)
CLOCK = (-300, 360, 80)
LAMP = (700, 0)
LAMP_Y = 520                            # низ шнура (верх абажура)
TABLE_T, TABLE_F = 1080.0, 1150.0       # кухонный стол: задний и передний край столешницы
TABLE_X0, TABLE_X1 = 350.0, 1400.0
CAL = (430, 420, 600, 640)              # календарик на стене: x0, y0, x1, y1

WALL, WALL_SH = "#e7cfa3", "#cdb083"
TILE, TILE_L = "#f1e2c2", "#cfb488"
WOOD, WOOD_SH, WOOD_D = "#c98f5a", "#a8723f", "#8a5a30"
FRONT, FRONT_SH = "#e9dcc4", "#c9b99c"
CAB, CAB_SH = "#9fc3b5", "#7ba393"
FRG, FRG_SH = "#eef1f2", "#c9d1d6"


def wall(mode):
    s = []
    w = WALL if mode != "morning" else "#f0dcb4"
    s.append(f'<rect x="-1400" y="-1400" width="4200" height="{FLOOR + 1400}" fill="{w}"/>')
    lib.DEFS.append('<pattern id="pTile29" width="96" height="72" patternUnits="userSpaceOnUse">'
                    f'<rect width="96" height="72" fill="{TILE}"/><rect x="0" y="68" width="96" height="4" fill="{TILE_L}"/>'
                    f'<rect x="92" width="4" height="72" fill="{TILE_L}"/></pattern>')
    s.append(f'<rect x="-1400" y="{TILE_Y0}" width="4200" height="{CT_TOP - TILE_Y0}" fill="url(#pTile29)"/>')
    s.append(line([(-1400, TILE_Y0), (2800, TILE_Y0)], 4, INK, taper=.05, wmin=.9, seed=900))
    # плинтус под потолком (карниз)
    s.append(shape(rect_pts(-1400, -40, 2800, -10), mix(w, "#000000", .12), "", w=3.6, seed=901))
    return "".join(s)


def window(mode, t=0.0):
    x0, x1, y0, y1 = WIN
    if mode == "morning":
        sky = lib.lin_grad([(0, "#8fc4ea", 1), (1, "#dff0f6", 1)], 0, 0, 0, 1)
    else:
        sky = lib.lin_grad([(0, "#141c38", 1), (1, "#2e4068", 1)], 0, 0, 0, 1)
    inner = f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>'
    if mode == "morning":
        inner += blob(ellipse_pts(x0 + 110, y0 + 150, 64, 64, 18), "#fff3c4")
        for k, (cx, cy) in enumerate([(x0 + 300, y0 + 120), (x0 + 380, y0 + 260)]):
            inner += blob(ellipse_pts(cx, cy, 70, 24, 12), "#ffffff", .9)
        roof = "#7f8fa8"
        win_c = "#b9d3e6"
    else:
        inner += blob(ellipse_pts(x0 + 350, y0 + 140, 40, 40, 16), "#f3ead0")
        for k, (x, y) in enumerate([(x0 + 80, y0 + 90), (x0 + 210, y0 + 210), (x0 + 120, y0 + 330), (x0 + 400, y0 + 300), (x0 + 300, y0 + 420)]):
            r = 4 + 1.2 * math.sin(t * 3 + k)
            inner += blob(ellipse_pts(x, y, r, r, 6), "#f3ead0")
        roof = "#121830"
        win_c = "#f2c46a"
    inner += blob([(x0 - 20, y1 - 220), (x0 + 120, y1 - 250), (x0 + 120, y1 - 300), (x0 + 270, y1 - 300), (x0 + 270, y1 - 230),
                   (x1 + 20, y1 - 260), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)], roof)
    for k, (x, y) in enumerate([(x0 + 150, y1 - 260), (x0 + 200, y1 - 260), (x0 + 320, y1 - 190), (x0 + 400, y1 - 200), (x0 + 60, y1 - 150)]):
        inner += blob(rect_pts(x, y, x + 26, y + 34), win_c)
    fr = "#efe6d6"
    mx = (x0 + x1) / 2
    inner += blob(rect_pts(mx - 14, y0, mx + 14, y1), fr) + blob(rect_pts(x0, (y0 + y1) / 2 - 14, x1, (y0 + y1) / 2 + 14), fr)
    s = [shape(rect_pts(x0, y0, x1, y1, 10), fr, inner, w=5, seed=906)]
    s.append(shape(rect_pts(x0 - 30, y1 - 4, x1 + 30, y1 + 36, 6), fr, blob(rect_pts(x0 - 30, y1 + 22, x1 + 30, y1 + 36), "#d6ccbb"), w=4.4, seed=907))
    # цветок в горшке на подоконнике
    px = x1 - 90
    s.append(shape([(px - 40, y1 - 4, 1), (px + 40, y1 - 4, 1), (px + 30, y1 - 70, 1), (px - 30, y1 - 70, 1)], "#c4673f",
                   blob([(px + 6, y1 - 70), (px + 30, y1 - 70), (px + 40, y1 - 4), (px + 10, y1 - 4)], "#9c4c2c", .9), w=4, seed=908))
    for k in range(5):
        a = -2.4 + k * 0.42
        s.append(line([(px, y1 - 70), (px + 80 * math.cos(a), y1 - 70 + 100 * math.sin(a))], 16, "#5f9a5a", taper=.6, seed=919 + k))
    return "".join(s)


def clock_wall(h, m, mode, k=1.0, x=None, y=None):
    """Часы на стене: h, m — время (h дробное не нужно: часовая считается от h+m/60)."""
    cx, cy, r = CLOCK
    cx = cx if x is None else x
    cy = cy if y is None else y
    r = r * k
    s = [blob(ellipse_pts(cx + 6, cy + 10, r + 8, r + 8, 24), "#000000", .12)]
    face = "#fbf6ea" if mode != "dark" else "#cfc8b8"
    inner = blob(ellipse_pts(cx + r * .2, cy + r * .2, r, r, 24), "#e7dfcd", .8)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        ln = .16 if i % 3 == 0 else .08
        inner += line([(cx + r * .82 * math.cos(a), cy + r * .82 * math.sin(a)), (cx + r * (.82 - ln) * math.cos(a), cy + r * (.82 - ln) * math.sin(a))],
                      5 * k if i % 3 == 0 else 3 * k, INK, taper=.1, wmin=.8, seed=960 + i)
    s.append(shape(ellipse_pts(cx, cy, r + 14 * k, r + 14 * k, 24), "#c44f3a", "", w=4.6, seed=950))
    s.append(shape(ellipse_pts(cx, cy, r, r, 24), face, inner, w=3.6, seed=951))
    ha = math.radians((h % 12 + m / 60) * 30 - 90)
    ma = math.radians(m * 6 - 90)
    s.append(line([(cx, cy), (cx + r * .48 * math.cos(ha), cy + r * .48 * math.sin(ha))], 10 * k, INK, taper=.3, wmin=.5, seed=970))
    s.append(line([(cx, cy), (cx + r * .72 * math.cos(ma), cy + r * .72 * math.sin(ma))], 7 * k, INK, taper=.3, wmin=.4, seed=971))
    s.append(blob(ellipse_pts(cx, cy, 8 * k, 8 * k, 10), "#c44f3a"))
    return "".join(s)


def lamp(mode, t=0.0, swing=0.0):
    x, _ = LAMP
    a = swing
    s = []
    cord_end = (x + (LAMP_Y + 60) * math.sin(a), LAMP_Y)
    s.append(line([(x, -60), cord_end], 4, INK, taper=.05, wmin=.9, seed=980))
    cx, cy = cord_end
    shade = T([(-90, 80), (-60, 0), (60, 0), (90, 80)], cx, cy, 1, math.degrees(-a), cx, cy)
    on = mode != "dark"
    bulb = "#fff4c8" if on else "#d8d2c0"
    s.append(shape(T(ellipse_pts(0, 84, 30, 22, 12), cx, cy, 1, math.degrees(-a), cx, cy), bulb, "", w=3.4, seed=981))
    s.append(shape(shade, "#2f6f63", blob(T([(30, 0), (60, 0), (90, 80), (40, 80)], cx, cy, 1, math.degrees(-a), cx, cy), "#225449", .9), w=4.6,
                   seed=982))
    s.append(shape(T(rect_pts(-16, -18, 16, 2, 4), cx, cy, 1, math.degrees(-a), cx, cy), "#225449", "", w=3.4, seed=983))
    return "".join(s)


def lamp_glow(mode):
    if mode == "night":
        g = lib.rad_grad([(0, "#ffd890", .5), (.5, "#ffbe6a", .2), (1, "#ffbe6a", 0)], 520, 360, 1200, 1100)
        g2 = lib.rad_grad([(0, "#000000", 0), (.55, "#000000", 0), (1, "#1a1030", .5)], 520, 800, 1500, 1500)
        return (f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
                f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g2})"/>')
    if mode == "dark":
        return ('<rect x="-1400" y="-1400" width="4200" height="4400" fill="#1d2550" opacity=".55" style="mix-blend-mode:multiply"/>')
    # утро: лучи из окна и тёплая заливка
    x0, x1, y0, y1 = WIN
    o = []
    for k, (dx, w) in enumerate([(0, 200), (260, 140)]):
        pts = [(x0 + 60 + dx, y0 + 60), (x0 + 60 + dx + w, y0 + 60), (x0 + 1500 + dx + w, FLOOR + 200), (x0 + 1500 + dx - 80, FLOOR + 200)]
        o.append(blob(pts, "#fff2c0", .22, 'style="mix-blend-mode:screen"'))
    g = lib.rad_grad([(0, "#fff0c8", .35), (1, "#fff0c8", 0)], -300, 600, 1400, 1200)
    o.append(f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    return "".join(o)


def counter():
    s = []
    tp = [(-1400, CT_TOP, 1), (1240, CT_TOP, 1), (1240, CT_FR, 1), (-1400, CT_FR, 1)]
    inner = "".join(line([(-1400, CT_TOP + 12 + k * 12), (1240, CT_TOP + 14 + k * 12)], 2.2, WOOD_SH, taper=.1, wmin=.7, seed=1930 + k, op=.8)
                    for k in range(2))
    s.append(shape(tp, WOOD, inner, w=4.4, seed=910))
    s.append(shape(rect_pts(-1400, CT_FR, 1240, CT_FR + 26), WOOD_SH, "", w=4.4, seed=909))
    inner = ""
    for k, x in enumerate(range(-1360, 1240, 400)):
        inner += line([(x, CT_FR + 30), (x, FLOOR)], 4, mix(FRONT, "#000000", .3), taper=.05, wmin=.9, seed=920 + k)
        inner += shape(rect_pts(x + 170, CT_FR + 90, x + 230, CT_FR + 108, 8), "#b8b0a2", "", w=3, seed=930 + k)
    inner += blob(rect_pts(-1400, FLOOR - 40, 1240, FLOOR), FRONT_SH, .9)
    s.append(shape(rect_pts(-1400, CT_FR + 26, 1240, FLOOR), FRONT, inner, w=5, seed=940))
    return "".join(s)


def floor(mode):
    col = "#b98d5f" if mode != "morning" else "#c99d6c"
    inner = "".join(line([(-1400, FLOOR + 60 + k * 90 + k * k * 8), (2800, FLOOR + 60 + k * 90 + k * k * 8)], 3, mix(col, "#000000", .25),
                         taper=.05, wmin=.9, seed=1500 + k, op=.8) for k in range(8))
    inner += blob(rect_pts(-1400, FLOOR, 2800, FLOOR + 40), "#000000", .12)
    return shape(rect_pts(-1400, FLOOR, 2800, 3600), col, inner, w=4.6, seed=1501)


# ─────────────────────────────── полка с пылью
def shelf(dust=1.0, wiped=0.0, wipe_x=(0.0, 0.0), jars=True):
    """dust — толщина слоя пыли (0..1); wiped — доля протёртой тряпкой полки; wipe_x — (x0, x1) чистой полосы пальцем."""
    x0, x1, y = SHELF
    s = []
    for k, bx in enumerate((x0 + 40, x1 - 40)):
        s.append(shape([(bx - 10, y + 20, 1), (bx + 10, y + 20, 1), (bx + 10, y + 70, 1), (bx - 30, y + 20, 1)], WOOD_SH, "", w=3.6, seed=1600 + k))
    if jars:
        for k, (x, hgt, col, lid) in enumerate([(x0 + 70, 110, "#e9c46a", "#c44f3a"), (x0 + 170, 140, "#9fc5a8", "#3f7a72"),
                                                (x0 + 270, 90, "#e07a5f", "#c9c0b0"), (x0 + 380, 120, "#8ab6d6", "#c44f3a")]):
            body = rect_pts(x - 40, y - hgt, x + 40, y, 14)
            inner = blob(rect_pts(x + 14, y - hgt, x + 40, y), mix(col, "#000000", .2), .9)
            inner += blob(rect_pts(x - 40, y - hgt * .55, x + 40, y - hgt * .3), "#f6efe0", .85)
            s.append(shape(body, col, inner, w=4, seed=1610 + k))
            s.append(shape(rect_pts(x - 44, y - hgt - 20, x + 44, y - hgt + 4, 6), lid, "", w=3.6, seed=1620 + k))
            if dust > 0:
                s.append(blob(rect_pts(x - 44, y - hgt - 24, x + 44, y - hgt - 16, 4), "#9a9284", .9 * dust))
    board = rect_pts(x0, y, x1, y + 24, 3)
    inner = blob(rect_pts(x0, y + 14, x1, y + 24), WOOD_SH, .9)
    s.append(shape(board, WOOD, inner, w=4.4, seed=1630))
    if dust > 0:
        # слой пыли сверху доски — серые комья, полоса там, где протёрто, чистая
        rs = np.random.RandomState(5)
        segs = []
        xs = np.linspace(x0 + 4, x1 - 4, 60)
        for i, xx in enumerate(xs[:-1]):
            if wiped > 0 and xx < x0 + (x1 - x0) * wiped:
                continue
            if wipe_x[1] > wipe_x[0] and wipe_x[0] - 4 < xx < wipe_x[1] + 4:
                continue
            segs.append((xx, xs[i + 1]))
        for (a, b) in segs:
            hh = 5 + 4 * rs.uniform()
            s.append(blob([(a, y + 1), (a, y - hh * dust), ((a + b) / 2, y - (hh + 3) * dust), (b, y - hh * dust), (b, y + 1)], "#9a9284"))
    return "".join(s)


# ─────────────────────────────── навесной шкаф
def cupboard(open_=0.0, inside=True, empty=False):
    """open_ 0..1 — правая дверца раскрывается к зрителю (петли справа): видна узкой, потом шире вправо."""
    x0, x1, y0, y1 = CUP
    mx = (x0 + x1) / 2
    s = [blob(rect_pts(x0 + 10, y1, x1 + 10, y1 + 26), "#000000", .12)]
    s.append(shape(rect_pts(x0, y0, x1, y1, 8), CAB, blob(rect_pts(x1 - 60, y0, x1, y1), CAB_SH, .9), w=5, seed=1700))
    if open_ > 0.02:
        # проём правой половины
        ix0, ix1, iy0, iy1 = mx + 6, x1 - 16, y0 + 16, y1 - 16
        inner = blob(rect_pts(ix0, iy0, ix1, iy1), "#3d3a44")
        inner += blob(rect_pts(ix0, (iy0 + iy1) / 2 - 8, ix1, (iy0 + iy1) / 2 + 8), "#6b6372")
        if inside and not empty:
            # всё «как попало»: кастрюля, пакеты, крышки
            inner += pot_side(ix0 + 80, (iy0 + iy1) / 2 - 8, .8, "#c44f3a")
            inner += bag(ix0 + 200, (iy0 + iy1) / 2 - 8, .8, "#e9c46a")
            inner += lid_side(ix0 + 130, iy1, .9, ang=-20)
            inner += bag(ix0 + 60, iy1, .75, "#8ab6d6")
            inner += pot_side(ix0 + 200, iy1, .7, "#3f7a72")
        s.append(shape(rect_pts(ix0, iy0, ix1, iy1, 4), "#3d3a44", inner, w=4, seed=1701))
        # дверца: ширина в проекции
        w = (ix1 - ix0) * (1 - open_) * 0.0 + 0
        dw = (x1 - mx) * (0.25 + 0.75 * open_) * 0.6
        dpts = [(x1, y0 - 6 * open_), (x1 + dw, y0 - 30 * open_), (x1 + dw, y1 + 30 * open_), (x1, y1 + 6 * open_)]
        s.append(shape(dpts, mix(CAB, "#ffffff", .12), blob([(x1, y0), (x1 + dw * .3, y0 - 10 * open_), (x1 + dw * .3, y1 + 10 * open_), (x1, y1)],
                                                         CAB_SH, .7), w=4.6, seed=1702))
        s.append(shape(rect_pts(x1 + dw * .8 - 8, (y0 + y1) / 2 - 40, x1 + dw * .8 + 8, (y0 + y1) / 2 + 40, 6), "#d9c7a0", "", w=3, seed=1703))
        _ = w
    else:
        s.append(shape(rect_pts(mx + 6, y0 + 16, x1 - 16, y1 - 16, 6), mix(CAB, "#ffffff", .1), "", w=4, seed=1704))
        s.append(shape(rect_pts(mx + 24, (y0 + y1) / 2 - 40, mx + 40, (y0 + y1) / 2 + 40, 6), "#d9c7a0", "", w=3, seed=1705))
    s.append(shape(rect_pts(x0 + 16, y0 + 16, mx - 6, y1 - 16, 6), mix(CAB, "#ffffff", .1), "", w=4, seed=1706))
    s.append(shape(rect_pts(mx - 40, (y0 + y1) / 2 - 40, mx - 24, (y0 + y1) / 2 + 40, 6), "#d9c7a0", "", w=3, seed=1707))
    return "".join(s)


# ─────────────────────────────── холодильник
def fridge(open_=0.0, light=1.0, magnets=True, foam=False):
    x0, x1, y0, y1 = FRIDGE
    s = [blob(rect_pts(x0 - 20, y1 - 10, x1 + 30, y1 + 20), "#000000", .18)]
    s.append(shape(rect_pts(x0, y0, x1, y1, 30), FRG, blob(rect_pts(x1 - 70, y0, x1, y1), FRG_SH, .9), w=5.2, seed=1800))
    split = y0 + 360
    if open_ > 0.02:
        ix0, ix1, iy0, iy1 = x0 + 22, x1 - 22, split + 22, y1 - 40
        inner = blob(rect_pts(ix0, iy0, ix1, iy1), "#f6fbff" if light > .5 else "#cfd6dc")
        for k in range(3):
            yy = iy0 + 160 + k * 200
            inner += blob(rect_pts(ix0, yy, ix1, yy + 10), "#bcd2de")
        inner += jar(ix0 + 90, iy0 + 160, .7, "#e07a5f") + jar(ix0 + 210, iy0 + 160, .55, "#9fc5a8")
        inner += bottle(ix0 + 270, iy0 + 360, .8) + jar(ix0 + 110, iy0 + 360, .6, "#e9c46a")
        if foam:
            for k, (fx, fy, r) in enumerate([(ix0 + 160, iy0 + 560, 30), (ix0 + 200, iy0 + 550, 22), (ix0 + 120, iy0 + 548, 20)]):
                inner += blob(ellipse_pts(fx, fy, r, r * .8, 12), "#ffffff")
        s.append(shape(rect_pts(ix0, iy0, ix1, iy1, 10), "#f6fbff", inner, w=4.4, seed=1801))
        dw = (x1 - x0) * (0.2 + 0.55 * open_)
        d = [(x1, split + 4), (x1 + dw, split - 30 * open_), (x1 + dw, y1 + 10 * open_), (x1, y1 - 20)]
        s.append(shape(d, FRG, blob([(x1, split), (x1 + dw * .25, split - 8), (x1 + dw * .25, y1), (x1, y1 - 20)], FRG_SH, .8), w=4.6, seed=1802))
        if light > .5:
            g = lib.rad_grad([(0, "#eaf6ff", .55), (1, "#eaf6ff", 0)], (ix0 + ix1) / 2, (iy0 + iy1) / 2, 520, 620)
            s.append(f'<rect x="{x0 - 500}" y="{split - 300}" width="{x1 - x0 + 1000}" height="1400" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    else:
        s.append(line([(x0 + 6, split), (x1 - 6, split)], 4.4, INK, taper=.05, wmin=.9, seed=1803))
        s.append(shape(rect_pts(x0 + 30, split + 60, x0 + 46, split + 300, 6), "#b8b0a2", "", w=3, seed=1804))
        if magnets:
            for k, (mx, my, c) in enumerate([(x0 + 120, split + 120, "#e9c46a"), (x0 + 210, split + 200, "#c44f3a"), (x0 + 150, split + 260, "#8ab6d6")]):
                s.append(shape(ellipse_pts(mx, my, 22, 22, 10), c, "", w=3, seed=1810 + k))
            s.append(shape([(x0 + 160, split + 120, 1), (x0 + 270, split + 112, 1), (x0 + 278, split + 250, 1), (x0 + 168, split + 256, 1)], "#fbf6ea",
                           "".join(line([(x0 + 180, split + 150 + j * 24), (x0 + 250, split + 146 + j * 24)], 2.4, "#9a9284", seed=1820 + j) for j in range(4)),
                           w=3, seed=1815))
    s.append(line([(x0 + 6, split), (x1 - 6, split)], 4.4, INK, taper=.05, wmin=.9, seed=1805))
    s.append(shape(rect_pts(x0 + 30, y0 + 180, x0 + 46, y0 + 320, 6), "#b8b0a2", "", w=3, seed=1806))
    return "".join(s)


def switch(on=True):
    x, y = -40, 1000
    s = [shape(rect_pts(x - 36, y - 50, x + 36, y + 50, 10), "#f6f1e6", blob(rect_pts(x + 10, y - 50, x + 36, y + 50), "#d8d0c0", .8), w=3.6, seed=1890)]
    ky = y - 14 if on else y + 14
    s.append(shape(rect_pts(x - 12, ky - 18, x + 12, ky + 18, 5), "#e6dfd0", "", w=3, seed=1891))
    return "".join(s)


# ─────────────────────────────── утварь (x, y — низ-центр)
def pot_side(x, y, k=1.0, col="#c44f3a", rot=0.0, lid=False, handle=True):
    def P(pts):
        return T(pts, x, y, k, rot)
    s = [blob(P(ellipse_pts(4, 2, 92, 12, 14)), "#000000", .18)]
    body = P([(-80, -110), (80, -110), (76, -18), (60, 0, 1), (-60, 0, 1), (-76, -18)])
    inner = blob(P([(30, -110), (80, -110), (76, -18), (60, 0), (36, 0)]), mix(col, "#000000", .25), .9)
    inner += line(P([(-60, -86), (-56, -30)]), 6, mix(col, "#ffffff", .45), seed=2001, op=.9)
    s.append(shape(body, col, inner, w=4.4, seed=2000))
    if handle:
        for sx in (-1, 1):
            s.append(shape(P(rect_pts(min(sx * 80, sx * 104), -98, max(sx * 80, sx * 104), -82, 6)), mix(col, "#000000", .3), "", w=3.4, seed=2002 + sx))
    rim = P(ellipse_pts(0, -110, 82, 16, 16))
    s.append(shape(rim, mix(col, "#ffffff", .1), blob(P(ellipse_pts(0, -108, 70, 10, 14)), "#3a2a2a" if not lid else mix(col, "#000000", .2)),
                   w=3.6, seed=2004))
    if lid:
        s.append(lid_side(0, 0, 1.0, _P=P, y_off=-112))
    return "".join(s)


def lid_side(x, y, k=1.0, ang=0.0, col="#b9bec8", _P=None, y_off=0.0):
    def P(pts):
        if _P is not None:
            return _P([(p[0], p[1] + y_off) + tuple(p[2:]) for p in pts])
        return T(pts, x, y, k, ang)
    s = [shape(P(ellipse_pts(0, -6, 88, 18, 16)), col, blob(P(ellipse_pts(14, -2, 74, 10, 14)), "#8e95a5", .9), w=4, seed=2010)]
    s.append(shape(P(rect_pts(-16, -40, 16, -18, 8)), "#2b2f3a", "", w=3.4, seed=2011))
    s.append(line(P([(-60, -14), (-20, -20)]), 4, "#ffffff", seed=2012, op=.85))
    return "".join(s)


def pan(x, y, k=1.0, rot=0.0):
    def P(pts):
        return T(pts, x, y, k, rot)
    s = [shape(P(rect_pts(70, -40, 260, -22, 9)), "#2b2f3a", "", w=3.6, seed=2020)]
    s.append(shape(P(ellipse_pts(0, -24, 90, 22, 16)), "#3f4554", blob(P(ellipse_pts(0, -26, 74, 15, 14)), "#23262e"), w=4.2, seed=2021))
    s.append(shape(P([(-90, -24), (90, -24), (80, 0), (-80, 0)]), "#3f4554", "", w=4, seed=2022))
    return "".join(s)


def bag(x, y, k=1.0, col="#e9c46a", rot=0.0):
    def P(pts):
        return T(pts, x, y, k, rot)
    body = P([(-50, 0, 1), (-56, -90), (-44, -150), (-30, -170), (30, -172), (46, -150), (56, -90), (50, 0, 1)])
    inner = blob(P([(10, -172), (46, -150), (56, -90), (50, 0), (16, 0)]), mix(col, "#000000", .22), .9)
    inner += blob(P(rect_pts(-34, -110, 34, -60, 6)), "#fbf6ea", .95)
    inner += line(P([(-24, -96), (22, -96)]), 3, "#9a9284", seed=2031) + line(P([(-24, -78), (10, -78)]), 3, "#9a9284", seed=2032)
    inner += line(P([(-40, -160), (40, -160)]), 3, mix(col, "#000000", .35), seed=2033, op=.8)
    return shape(body, col, inner, w=4.2, seed=2030)


def jar(x, y, k=1.0, col="#e07a5f", rot=0.0):
    def P(pts):
        return T(pts, x, y, k, rot)
    body = P(rect_pts(-40, -120, 40, 0, 14))
    inner = blob(P(rect_pts(14, -120, 40, 0)), mix(col, "#000000", .2), .9) + blob(P(rect_pts(-40, -70, 40, -40)), "#f6efe0", .85)
    s = [shape(body, col, inner, w=4, seed=2040)]
    s.append(shape(P(rect_pts(-44, -140, 44, -116, 6)), "#c9c0b0", "", w=3.6, seed=2041))
    return "".join(s)


def bottle(x, y, k=1.0, col="#5f9a5a", rot=0.0):
    def P(pts):
        return T(pts, x, y, k, rot)
    body = P([(-30, 0, 1), (-32, -130), (-14, -170), (-12, -210, 1), (12, -210, 1), (14, -170), (32, -130), (30, 0, 1)])
    inner = blob(P([(8, -200), (14, -170), (32, -130), (30, 0), (10, 0)]), mix(col, "#000000", .25), .9)
    inner += blob(P(rect_pts(-30, -110, 30, -60, 4)), "#fbf6ea", .95)
    return shape(body, col, inner, w=4, seed=2050)


def plate(x, y, k=1.0, rot=0.0):
    def P(pts):
        return T(pts, x, y, k, rot)
    return shape(P(ellipse_pts(0, -14, 90, 22, 16)), "#f6f3ec", blob(P(ellipse_pts(0, -16, 60, 12, 14)), "#e2dccf") +
                 blob(P(ellipse_pts(30, -10, 70, 10, 14)), "#d8d2c4", .7), w=4, seed=2060)


def box(x, y, k=1.0, part="all", flap=0.0):
    """Картонная коробка (вид спереди-сверху): part 'back' — задняя стенка и дальние клапаны, 'front' — передняя стенка
    и ближние клапаны (кот сидит между)."""
    def P(pts):
        return T(pts, x, y, k)
    c, csh, cd = "#c99a5e", "#a87a43", "#8a6233"
    s = []
    if part in ("back", "all"):
        s.append(shape(P([(-150, -200), (150, -200), (200, -250, 1), (-200, -250, 1)]), csh, "", w=4, seed=2070))
        s.append(shape(P([(-150, -200, 1), (150, -200, 1), (150, -140, 1), (-150, -140, 1)]), "#5d4126", "", w=3.6, seed=2071))
        s.append(shape(P([(150, -200), (196, -176 - 20 * flap), (190, -120, 1), (150, -140)]), cd, "", w=3.6, seed=2072))
    if part in ("front", "all"):
        s.append(blob(P(ellipse_pts(10, 4, 220, 18, 16)), "#000000", .22))
        inner = blob(P([(60, -140), (150, -140), (150, 0), (60, 0)]), csh, .9)
        inner += shape(P(rect_pts(-80, -96, 70, -66, 2)), "#d9b989", "", w=2.4, seed=2075)
        inner += line(P([(-150, -112), (150, -112)]), 3, cd, seed=2076, op=.8)
        s.append(shape(P(rect_pts(-150, -140, 150, 0)), c, inner, w=4.6, seed=2073))
        s.append(shape(P([(-150, -140), (-206, -112 + 16 * flap), (-196, -60, 1), (-150, -70)]), c, blob(P([(-150, -140), (-206, -112), (-196, -60), (-170, -70)]),
                                                                                                  csh, .6), w=4, seed=2074))
    return "".join(s)


def rag(x, y, k=1.0, rot=0.0, t=0.0, flap=0.0):
    """Мягкая тряпка-полотенце, скомканная в кулаке (центр комка в (x, y)); два угла свисают и колышутся."""
    def P(pts):
        return T(pts, x, y, k, rot)
    w = 7 * math.sin(t * 9) * (1 + flap)
    c, csh = "#bcd8ec", "#8fb6d4"
    s = []
    t1 = P([(-30, 30), (-50, 90 + w), (-30, 140 + w * 1.4, 1), (-6, 120 + w), (6, 40)])
    s.append(shape(t1, csh, line(P([(-34, 60), (-30, 120 + w)]), 3, "#d9675a", seed=2103, op=.9), w=3.6, seed=2104))
    t2 = P([(10, 34), (30, 100 - w), (56, 128 - w * 1.2, 1), (52, 70), (40, 30)])
    s.append(shape(t2, c, line(P([(26, 50), (44, 110 - w)]), 3, "#d9675a", seed=2105, op=.9), w=3.6, seed=2100))
    body = P([(-58, -20), (-30, -52), (10, -58), (50, -40), (64, -4), (50, 34), (10, 48), (-36, 42), (-62, 14)])
    inner = blob(P([(14, -56), (64, -4), (50, 34), (14, 48)]), csh, .8)
    inner += line(P([(-56, -6), (-20, -30), (30, -40)]), 3.4, "#d9675a", seed=2106, op=.9)
    inner += line(P([(-50, 20), (-6, 4), (46, 10)]), 3.4, "#d9675a", seed=2107, op=.9)
    s.append(shape(body, c, inner, w=4, seed=2101))
    s.append(line(P([(-30, -14), (-4, 2), (22, -10)]), 2.6, "#5d7f9c", seed=2102, op=.9))
    s.append(line(P([(-10, 24), (18, 18)]), 2.4, "#5d7f9c", seed=2108, op=.8))
    return "".join(s)


def sponge(x, y, k=1.0, rot=0.0):
    def P(pts):
        return T(pts, x, y, k, rot)
    s = [shape(P(rect_pts(-46, -10, 46, 30, 8)), "#e9c46a", blob(P(rect_pts(-46, 14, 46, 30)), "#c9a24a", .9), w=3.8, seed=2110)]
    s.append(shape(P(rect_pts(-46, -30, 46, -8, 6)), "#5f9a5a", "", w=3.6, seed=2111))
    for k2, (fx, fy, r) in enumerate([(-30, -36, 14), (0, -40, 18), (28, -34, 12)]):
        s.append(shape(P(ellipse_pts(fx, fy, r, r * .85, 10)), "#ffffff", "", w=2.6, seed=2112 + k2))
    return "".join(s)


def mug(x, y, k=1.0, rot=0.0, col="#3f7a72", shine=0.0, hs=1):
    """Кружка: (x, y) — низ-центр; ручка справа."""
    def P(pts):
        return T(pts, x, y, k, rot)
    s = []
    hd = P([(hs * 44, -96), (hs * 78, -94), (hs * 86, -60), (hs * 72, -32), (hs * 44, -30)])
    s.append(lib.line(hd, 17 * k, INK, seed=2121, taper=.05, wmin=.9))
    s.append(lib.line(hd, 9 * k, col, seed=2122, taper=.05, wmin=.9))
    body = P([(-50, -128), (50, -128), (48, -14), (36, 0, 1), (-36, 0, 1), (-48, -14)])
    inner = blob(P([(18, -128), (50, -128), (48, -14), (36, 0), (20, 0)]), mix(col, "#000000", .25), .9)
    inner += blob(P(ellipse_pts(-6, -66, 22, 20, 12)), "#f4ede0", .95)
    inner += blob(P([(-14, -70), (-6, -78), (2, -70), (-6, -58, 1)]), "#c44f3a")
    if shine > 0:
        # полоса блика пробегает по кружке
        sx = -70 + 140 * shine
        inner += blob(P([(sx - 10, -130), (sx + 14, -130), (sx - 6, 2), (sx - 30, 2)]), "#ffffff", .75)
    inner += line(P([(-36, -110), (-34, -30)]), 6, mix(col, "#ffffff", .5), seed=2124, op=.9)
    s.append(shape(body, col, inner, w=4.4, seed=2123))
    s.append(shape(P(ellipse_pts(0, -128, 50, 12, 16)), mix(col, "#ffffff", .2), blob(P(ellipse_pts(0, -127, 42, 8, 14)), "#2a2228"), w=3.4, seed=2125))
    return "".join(s)


def sparkle(x, y, r, a=0.0, col="#fff6c8"):
    pts = []
    for i in range(8):
        ang = a + i * math.pi / 4
        rr = r if i % 2 == 0 else r * .28
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang), 1))
    return shape(pts, col, "", w=3.2, seed=2130, var=.1)


def egg_timer(x, y, k=1.0, rot=0.0, ring=0.0, t=0.0):
    """Таймер-яйцо на столешнице (низ-центр), ring — звенит (дрожь + штрихи)."""
    jx = 5 * ring * math.sin(t * 70)
    def P(pts):
        return T(pts, x + jx, y, k, rot + 4 * ring * math.sin(t * 55))
    s = [blob(P(ellipse_pts(6, 0, 70, 12, 14)), "#000000", .2)]
    s.append(shape(P([(-64, -10), (-70, -70), (-50, -130), (0, -160), (50, -130), (70, -70), (64, -10), (0, 6)]), "#f6f1e3",
                   blob(P([(20, -150), (60, -120), (70, -60), (60, -10), (24, 0)]), "#ddd4c0", .9), w=4.4, seed=2140))
    s.append(shape(P([(-70, -74), (70, -74), (66, -50), (-66, -50)]), "#e9c46a", "".join(
        line(P([(-60 + j * 15, -74), (-60 + j * 15, -64)]), 2.4, INK, seed=2142 + j, taper=.1, wmin=.8) for j in range(9)), w=3.4, seed=2141))
    s.append(shape(P([(-6, -60), (6, -60), (0, -48, 1)]), "#c44f3a", "", w=2.4, seed=2151))
    if ring > 0.02:
        for j in range(3):
            for sx in (-1, 1):
                r = 96 + j * 22
                s.append(line([(x + sx * r * .8, y - 130), (x + sx * (r + 10), y - 90), (x + sx * r * .85, y - 50)], 5, INK, seed=2160 + j + sx * 5,
                              op=ring, taper=.4, wmin=.3))
    return "".join(s)


# ═════════════════════════ РИЛС 34: стол, коробка пончиков, пончик, календарик, тарелка, сельдерей ═════════════════════════
# Общие предметы для сцен kitchen и cat: кот берёт kitchen_bg + table_back/table_top + donut_box и compose.
TWOOD, TWOOD_SH, TWOOD_HI, TWOOD_DK = "#b37647", "#8a5532", "#cf9461", "#5e3720"
BOX, BOX_SH, BOX_IN, BOX_IN_SH = "#f4a7bb", "#d97f99", "#f8c9d4", "#e59ab0"
DOUGH, DOUGH_SH = "#d99a55", "#b27236"
GLAZE = {"pink": ("#f27fa5", "#d95f88"), "choc": ("#6b3b25", "#4f2918"), "white": ("#fbf3e6", "#e2d6c2")}
SPRINKLES = ("#4fb3d9", "#f2d24b", "#7cc46a", "#ffffff", "#e8563f", "#a77bd6")


def kitchen_bg(t=0.0, mode="night", cal=None, extra=""):
    """Вечерняя кухня за столом (мир рилса 34): стена с кафелем, окно, полка, шкафчик, столешница у стены, пол, лампа.
    cal — SVG календарика (по умолчанию — пустой, без крестиков); extra — что ещё повесить на стену/столешницу."""
    s = [wall(mode), window(mode, t), counter(), floor(mode), cupboard(0.0)]
    s.append(counter_things())
    s.append(cal if cal is not None else calendar([0.0] * 7))
    s.append(extra)
    s.append(lamp(mode, t, .012 * math.sin(t * 1.3)))
    return "".join(s)


def counter_things():
    """На столешнице у стены: чайник, банка, бутылка масла, разделочная доска (без надписей)."""
    s = []
    # разделочная доска, прислонённая к кафелю
    s.append(shape(rect_pts(118, 840, 268, 1000, 30), "#d9a066", blob(rect_pts(220, 840, 268, 1000), "#b98048", .9) +
                   shape(ellipse_pts(193, 872, 14, 14, 10), "#7a5a3a", "", w=2.6, seed=3402), w=4, seed=3401))
    # чайник
    x, y = 960, CT_TOP
    s.append(blob(ellipse_pts(x, y + 2, 92, 10, 14), "#000000", .15))
    body = [(x - 80, y, 1), (x + 80, y, 1), (x + 72, y - 70), (x + 40, y - 120), (x - 40, y - 120), (x - 72, y - 70)]
    s.append(shape(body, "#e8563f", blob([(x + 20, y - 120), (x + 40, y - 120), (x + 72, y - 70), (x + 80, y), (x + 34, y)], "#c13f2c", .9) +
                   line([(x - 50, y - 80), (x - 40, y - 104)], 6, "#ff9a84", seed=3404), w=4.4, seed=3403))
    s.append(shape([(x - 80, y - 60), (x - 140, y - 110), (x - 128, y - 118), (x - 74, y - 84)], "#e8563f", "", w=3.6, seed=3405))
    s.append(shape(rect_pts(x - 50, y - 132, x + 50, y - 116, 6), "#c13f2c", "", w=3.4, seed=3406))
    s.append(line([(x - 40, y - 132), (x - 20, y - 176), (x + 20, y - 176), (x + 40, y - 132)], 7, INK, seed=3407, taper=.1, wmin=.8))
    # банка и бутылка
    s.append(jar(1110, CT_TOP, .9, "#9fc5a8"))
    s.append(bottle(1200, CT_TOP, .9, "#e9c46a"))
    return "".join(s)


def calendar(marks, x=None, k=1.0, split=0.0, fall=0.0, seed=3500):
    """Календарик-лист (7 клеток: 4 + 3) без букв. marks[i] 0..1 — прорисовка красного крестика в клетке i.
    split 0..1 — лист разламывается по зигзагу пополам (половинки разъезжают и поворачиваются);
    fall 0..1 — крестики осыпаются вниз. x = (x0, y0, x1, y1), по умолчанию CAL."""
    x0, y0, x1, y1 = x or CAL
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    zig = [(cx + 10 * k, y0 - 4), (cx - 16 * k, y0 + h * .2), (cx + 14 * k, y0 + h * .38), (cx - 12 * k, y0 + h * .56), (cx + 16 * k, y0 + h * .76),
           (cx - 8 * k, y1 + 4)]
    cells = []
    gx0, gy0 = x0 + w * .07, y0 + h * .3
    cw, ch = w * .86 / 4, h * .3
    for i in range(7):
        r, c = divmod(i, 4)
        ox = gx0 + c * cw + (cw / 2 if r == 1 else 0)
        oy = gy0 + r * ch
        cells.append((ox, oy, ox + cw, oy + ch))

    def sheet(side):
        o = []
        if side == 0:
            o.append(blob(rect_pts(x0 + 8, y0 + 10, x1 + 8, y1 + 10, 6), "#000000", .14))
        inner = blob(rect_pts(x0, y0, x1, y0 + h * .2), "#d8483c")
        inner += blob(rect_pts(x0, y0 + h * .17, x1, y0 + h * .2), "#b23a30")
        for k2, rx in enumerate((x0 + w * .3, x1 - w * .3)):
            inner += shape(ellipse_pts(rx, y0 + h * .06, 7 * k, 7 * k, 10), "#f6f1e6", "", w=2.4, seed=seed + 10 + k2)
        for i, (a0, b0, a1, b1) in enumerate(cells):
            inner += f'<rect x="{a0:.1f}" y="{b0:.1f}" width="{a1 - a0:.1f}" height="{b1 - b0:.1f}" fill="none" stroke="#b9ad98" stroke-width="{2.6 * k:.2f}"/>'
        return o, inner

    def marks_svg(dy_fall):
        o = []
        for i, m in enumerate(marks):
            if m <= 0.01:
                continue
            a0, b0, a1, b1 = cells[i]
            pad = (a1 - a0) * .18
            p, q = (a0 + pad, b0 + pad), (a1 - pad, b1 - pad)
            p2, q2 = (a1 - pad, b0 + pad), (a0 + pad, b1 - pad)
            u1, u2 = clamp_(m * 2), clamp_(m * 2 - 1)
            dy = dy_fall * (1 + .35 * (i % 3)) * (h * 1.6)
            rot_ = dy_fall * (40 + 25 * (i % 4)) * (1 if i % 2 else -1)
            ccx, ccy = (a0 + a1) / 2, (b0 + b1) / 2
            g = ""
            if u1 > 0:
                g += line([p, (p[0] + (q[0] - p[0]) * u1, p[1] + (q[1] - p[1]) * u1)], 7 * k, "#d42a2a", taper=.25, wmin=.5, seed=seed + 30 + i)
            if u2 > 0:
                g += line([p2, (p2[0] + (q2[0] - p2[0]) * u2, p2[1] + (q2[1] - p2[1]) * u2)], 7 * k, "#d42a2a", taper=.25, wmin=.5, seed=seed + 40 + i)
            o.append(f'<g transform="translate(0 {dy:.1f}) rotate({rot_:.1f} {ccx:.1f} {ccy:.1f})">{g}</g>')
        return "".join(o)

    page = rect_pts(x0, y0, x1, y1, 6)
    if split <= 0.001:
        o, inner = sheet(0)
        o.append(shape(page, "#fbf6ea", inner, w=4 * k, seed=seed))
        o.append(shape(ellipse_pts(cx, y0 - 2, 9 * k, 9 * k, 10), "#3f7a72", "", w=2.6, seed=seed + 2))
        o.append(marks_svg(fall))
        return "".join(o)
    # разлом: левая и правая половины по зигзагу
    left = [(x0 - 40, y0 - 40)] + zig[::1] + [(x0 - 40, y1 + 40)]
    left = [(x0 - 40, y0 - 40), (zig[0][0], y0 - 40)] + zig + [(zig[-1][0], y1 + 40), (x0 - 40, y1 + 40)]
    right = [(x1 + 40, y0 - 40), (zig[0][0], y0 - 40)] + zig + [(zig[-1][0], y1 + 40), (x1 + 40, y1 + 40)]
    o = []
    _, inner = sheet(1)
    e = split
    for side, poly, sg in ((0, left, -1), (1, right, 1)):
        c = lib.clip_of(poly)
        dx, dy, rr = sg * 26 * k * e, 30 * k * e * (1 if side else .6), sg * 9 * e
        body = (f'<g clip-path="url(#{c})"><path d="{lib.fill_d(page)}" fill="#fbf6ea"/>{inner}</g>')
        ink_poly = [p for p in page]
        g = f'<g clip-path="url(#{c})"><path d="{lib.ink_closed(ink_poly, 4 * k * lib.INK_K[0], seed=seed)}" fill="{INK}"/></g>'
        g += line(zig, 4 * k, INK, taper=.05, wmin=.9, seed=seed + 5 + side)
        o.append(f'<g transform="translate({dx:.1f} {dy:.1f}) rotate({rr:.2f} {cx:.1f} {y0:.1f})">{body}{g}</g>')
    o.append(marks_svg(fall))
    return "".join(o)


def clamp_(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def table_back(hip_x=230.0):
    """Задние ножки кухонного стола (за ногами Димы)."""
    s = []
    for k, x in enumerate((470, 1300)):
        s.append(shape(rect_pts(x - 13, TABLE_F, x + 13, FLOOR + 70), TWOOD_SH, "", w=3.4, seed=3600 + k))
    return "".join(s)


def table_top(front_legs=True):
    """Столешница кухонного стола (вид чуть сверху) с царгой и передними ножками."""
    s = []
    x0, x1 = TABLE_X0, TABLE_X1
    top = [(x0 + 20, TABLE_T, 1), (x1, TABLE_T, 1), (x1, TABLE_F, 1), (x0, TABLE_F, 1)]
    inner = blob([(x0, TABLE_T + 52), (x1, TABLE_T + 52), (x1, TABLE_F), (x0, TABLE_F)], mix(TWOOD_HI, "#000000", .07), .9)
    for k, y in enumerate((TABLE_T + 18, TABLE_T + 40)):
        inner += line([(x0 + 70, y), (x0 + 330, y + 2), (x1, y - 1)], 1.6, TWOOD_SH, seed=3610 + k, op=.45)
    s.append(shape(top, TWOOD_HI, inner, w=4.2, seed=3611))
    s.append(shape(rect_pts(x0, TABLE_F, x1, TABLE_F + 34), TWOOD, blob(rect_pts(x0, TABLE_F + 22, x1, TABLE_F + 34), TWOOD_SH, .9), w=4, seed=3612))
    if front_legs:
        for k, lx in enumerate((x0 + 30, x1 - 70)):
            s.append(shape(rect_pts(lx, TABLE_F + 34, lx + 34, FLOOR + 140), TWOOD,
                           blob(rect_pts(lx + 20, TABLE_F + 34, lx + 34, FLOOR + 140), TWOOD_SH, .9), w=3.6, seed=3613 + k))
    return "".join(s)


def table_shadow(x, w, op=.22):
    """Мягкая тень предмета на столешнице (x — центр, w — полуширина)."""
    return blob(ellipse_pts(x + 8, TABLE_F - 26, w, 12, 14), "#3a1a08", op, lib.blur(3))


# ─────────────────────────────── пончик
def donut(x, y, r=42.0, kind="pink", tilt=0.55, rot=0.0, bite=0.0, bite_ang=-30.0, seed=3700, sprinkle_seed=None):
    """Пончик (x, y — центр, r — радиус). tilt — сплюснутость (0.55 — вид сверху-сбоку, 0.75 — почти анфас).
    bite 0..1 — откушенный полукруг со стороны bite_ang (градусы от оси x, в плоскости рисунка)."""
    ry = r * tilt
    sid = seed
    glz, glz_sh = GLAZE[kind]
    o = []
    side = ellipse_pts(0, r * .16 * (1 - tilt) + 3, r, ry, 20)
    top = ellipse_pts(0, 0, r, ry, 20)
    hole = ellipse_pts(0, -ry * .08, r * .3, ry * .3, 14)
    gl = []
    for j in range(40):
        th = 2 * math.pi * j / 40
        rr = .86 + .06 * math.sin(th * 5 + sid) + .04 * math.sin(th * 9)
        gl.append((r * rr * math.cos(th), ry * rr * math.sin(th) - ry * .05))
    inner = blob([(p[0], p[1] + ry * .25) for p in top], DOUGH_SH, .9)
    inner += blob(gl, glz)
    inner += blob([(p[0] + r * .06, p[1] + ry * .1) for p in gl[20:35]] + [(0, ry * .3)], glz_sh, .6)
    inner += blob(ellipse_pts(-r * .38, -ry * .45, r * .22, ry * .12, 10), "#ffffff", .45)
    if kind != "white":
        rs = np.random.RandomState(sprinkle_seed if sprinkle_seed is not None else sid)
        for j in range(16 if kind == "pink" else 8):
            th = rs.uniform(0, 2 * math.pi)
            rr = rs.uniform(.45, .78)
            px, py = r * rr * math.cos(th), ry * rr * math.sin(th) - ry * .05
            a = rs.uniform(0, math.pi)
            ln = r * .09
            col = SPRINKLES[j % len(SPRINKLES)] if kind == "pink" else "#f6efe0"
            inner += f'<line x1="{px - ln * math.cos(a):.1f}" y1="{py - ln * math.sin(a) * tilt:.1f}" x2="{px + ln * math.cos(a):.1f}" ' \
                     f'y2="{py + ln * math.sin(a) * tilt:.1f}" stroke="{col}" stroke-width="{r * .07:.1f}" stroke-linecap="round"/>'
    else:
        inner += line([(-r * .5, -ry * .2), (-r * .1, ry * .3), (r * .3, -ry * .1), (r * .6, ry * .2)], r * .06, "#e8c48a", seed=sid + 3, op=.9)
    g = [blob(side, DOUGH_SH)]
    g.append(shape(top, DOUGH, inner, w=3.6, seed=sid))
    g.append(shape(hole, "#7a4a22", blob(ellipse_pts(0, ry * .06, r * .3, ry * .22, 12), "#a06a32"), w=3.0, seed=sid + 1))
    body = "".join(g)
    if bite > 0.01:
        m = lib.uid("m")
        a = math.radians(bite_ang)
        bx, by = r * 1.02 * math.cos(a), ry * 1.02 * math.sin(a)
        br = r * .55 * min(1, bite * 1.4)
        holes = "".join(f'<circle cx="{bx + br * .55 * math.cos(a + d):.1f}" cy="{by + br * .55 * math.sin(a + d) * tilt:.1f}" r="{br * .62:.1f}" fill="black"/>'
                        for d in (-.9, -.3, .3, .9))
        lib.DEFS.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="{-3 * r}" y="{-3 * r}" width="{6 * r}" height="{6 * r}">'
                        f'<rect x="{-3 * r}" y="{-3 * r}" width="{6 * r}" height="{6 * r}" fill="white"/>'
                        f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{br:.1f}" fill="black"/>{holes}</mask>')
        # след укуса: светлое тесто по краю выреза (рисуется под маской как кольцо)
        crumb = blob(ellipse_pts(bx, by, br + r * .09, (br + r * .09) * .9, 16), "#f3d6a4")
        body = f'<g>{crumb}{body}</g>'
        body = f'<g mask="url(#{m})">{body}</g>' + _bite_edge(bx, by, br, a, r, tilt, sid)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">{body}</g>'


def _bite_edge(bx, by, br, a, r, tilt, sid):
    """Контур укуса: зубчатая дуга тушью внутри пончика (только там, где он есть)."""
    pts = []
    for j in range(13):
        d = -1.25 + 2.5 * j / 12
        rr = br * (1.0 + .1 * math.sin(j * 2.2))
        pts.append((bx - rr * math.cos(a + d) * 1.0 + 0, by - rr * math.sin(a + d)))
    # оставить только точки внутри эллипса пончика
    keep = [p for p in pts if (p[0] / r) ** 2 + (p[1] / (r * tilt)) ** 2 < 1.02]
    if len(keep) < 2:
        return ""
    return line(keep, 3.2, INK, taper=.2, wmin=.5, seed=sid + 9)


# ─────────────────────────────── коробка пончиков
BOX_W, BOX_HF, BOX_D = 300.0, 62.0, 54.0       # ширина, высота передней стенки, глубина верха в проекции


def box_slots():
    """Центры гнёзд пончиков (локально, от низа-центра передней стенки): задний ряд 0..2, передний 3..5."""
    out = []
    for row, (yy, rr) in enumerate(((-BOX_HF - BOX_D * .62, 36.0), (-BOX_HF - BOX_D * .2, 40.0))):
        for c in range(3):
            out.append(((c - 1) * 92.0, yy, rr))
    return out


DEFAULT_DONUTS = ["choc", "pink", "white", "pink", "white", "choc"]


def donut_box(x, y, k=1.0, lid=0.0, donuts=None, glow=0.0, t=0.0, seed=3800, lid_jump=0.0, crumbs=0.0):
    """Розовая коробка пончиков без надписей. (x, y) — низ-центр передней стенки на столе.
    lid 0 — закрыта, 1 — распахнута (≈105°); donuts — список из 6 видов ('pink'|'choc'|'white'|None) по гнёздам
    (задний ряд 0..2, передний 3..5); glow 0..1 — тёплое сияние из щели/изнутри; lid_jump — подскок крышки (px)."""
    if donuts is None:
        donuts = DEFAULT_DONUTS
    W2, HF, D = BOX_W / 2, BOX_HF, BOX_D
    th = math.radians(105 * lid)
    hinge = -HF - D
    fe_y = hinge + D * math.cos(th) - 129 * math.sin(th) - lid_jump
    o = []
    o.append(blob(ellipse_pts(10, 4, W2 + 22, 14, 16), "#3a1a08", .25, lib.blur(3)))
    # задняя стенка/внутренность (видна, когда крышка открыта)
    if lid > 0.02:
        inside = [(-W2 + 8, hinge + 2, 1), (W2 - 8, hinge + 2, 1), (W2 - 4, -HF, 1), (-W2 + 4, -HF, 1)]
        inner = blob([(-W2, hinge), (W2, hinge), (W2, hinge + 16), (-W2, hinge + 16)], BOX_IN_SH, .9)
        for i, (sx, sy, rr) in enumerate(box_slots()):
            inner += blob(ellipse_pts(sx, sy + 6, rr * 1.05, rr * .5, 14), "#d98ba1", .7)
        o.append(shape(inside, "#f1b6c6", inner, w=3.4, seed=seed + 1))
        for i, (sx, sy, rr) in enumerate(box_slots()):
            kd = donuts[i] if i < len(donuts) else None
            if kd:
                o.append(donut(sx, sy, rr, kd, .5, seed=seed + 20 + i))
    # передняя стенка
    front = rect_pts(-W2, -HF, W2, 0, 3)
    inner = blob(rect_pts(-W2, -18, W2, 0), BOX_SH, .9)
    inner += line([(-W2 + 14, -HF + 12), (W2 - 14, -HF + 12)], 2.2, "#ffd3de", taper=.1, wmin=.8, seed=seed + 3, op=.9)
    o.append(shape(front, BOX, inner, w=4.4, seed=seed + 2))
    # крышка
    if lid <= 0.02 and lid_jump <= 0.01:
        o.append(shape([(-W2, hinge, 1), (W2, hinge, 1), (W2 + 4, -HF, 1), (-W2 - 4, -HF, 1)], BOX,
                       blob([(-W2, hinge), (W2, hinge), (W2, hinge + 10), (-W2, hinge + 10)], "#f9c3d0", .9), w=4.2, seed=seed + 4))
        o.append(line([(-W2 - 4, -HF), (W2 + 4, -HF)], 3.4, INK, taper=.05, wmin=.9, seed=seed + 5))
    else:
        out_side = fe_y > hinge          # свободный край ниже петли — видна наружная сторона
        q = [(-W2 - 2, hinge, 1), (W2 + 2, hinge, 1), (W2 + 6, fe_y, 1), (-W2 - 6, fe_y, 1)]
        if out_side:
            o.append(shape(q, BOX, blob([(-W2, fe_y - 8), (W2, fe_y - 8), (W2, fe_y), (-W2, fe_y)], BOX_SH, .8), w=4.2, seed=seed + 4))
        else:
            lip = [(-W2 - 6, fe_y, 1), (W2 + 6, fe_y, 1), (W2 + 6, fe_y - 12, 1), (-W2 - 6, fe_y - 12, 1)]
            o.append(shape(q, BOX_IN, blob([(-W2, hinge - 18), (W2, hinge - 18), (W2, hinge), (-W2, hinge)], BOX_IN_SH, .9), w=4.2, seed=seed + 4))
            o.append(shape(lip, BOX, "", w=3.4, seed=seed + 6))
    if glow > 0.01:
        gy = hinge if lid > .1 else -HF
        g = lib.rad_grad([(0, "#fff2b0", .85 * glow), (.4, "#ffd27a", .45 * glow), (1, "#ffc060", 0)], 0, gy - 10, W2 * 1.5, 120)
        o.append(f'<rect x="{-W2 * 2}" y="{gy - 260}" width="{W2 * 4}" height="380" fill="url(#{g})" style="mix-blend-mode:screen"/>')
        if lid < .3:
            o.append(line([(-W2 + 10, -HF - 2), (W2 - 10, -HF - 2)], 4, "#fff6c8", taper=.2, wmin=.4, seed=seed + 7, op=min(1, glow * 1.4)))
    if crumbs > 0:
        rs = np.random.RandomState(seed)
        for j in range(int(14 * crumbs)):
            cx_, cy_ = rs.uniform(-W2 - 60, W2 + 80), rs.uniform(-6, 10)
            o.append(blob(ellipse_pts(cx_, cy_, 4 + 3 * rs.uniform(), 3, 6), "#c98a45" if j % 3 else SPRINKLES[j % 6]))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})">{"".join(o)}</g>'


# ─────────────────────────────── тарелка с салатом, сельдерей, салфетка
def plate(x, y, k=1.0, salad=1.0, donut_kind=None, seed=3900):
    """Тарелка на столе (x, y — низ-центр); salad 0..1 — горка листьев салата; donut_kind — пончик на тарелке."""
    o = [blob(ellipse_pts(x + 6, y + 2, 112 * k, 14 * k, 16), "#3a1a08", .22, lib.blur(3))]
    o.append(shape(ellipse_pts(x, y - 14 * k, 110 * k, 26 * k, 20), "#f4f1ea", blob(ellipse_pts(x, y - 12 * k, 74 * k, 15 * k, 16), "#dcd6ca", .9) +
                   blob(ellipse_pts(x + 40 * k, y - 4 * k, 70 * k, 12 * k, 16), "#d2cbbd", .6), w=3.8, seed=seed))
    if salad > 0.01:
        rs = np.random.RandomState(seed)
        for j in range(5):
            lx = x + (j - 2) * 30 * k + rs.uniform(-6, 6) * k
            ly = y - 20 * k - abs(j - 2) * -3 * k
            a = rs.uniform(-30, 30) + (j - 2) * 18
            leaf = T([(-34, 0), (-26, -30), (-6, -48), (16, -44), (34, -20), (30, 4)], lx, ly, k * (0.9 + .1 * (j % 2)) * salad, a)
            col = "#7cc46a" if j % 2 else "#5ea84e"
            o.append(shape(leaf, col, line(T([(-20, -2), (0, -24), (20, -30)], lx, ly, k * salad, a), 2.2, "#3f7f35", seed=seed + 20 + j, op=.8),
                           w=3.2, seed=seed + 10 + j))
    if donut_kind:
        o.append(donut(x, y - 34 * k, 46 * k, donut_kind, .5, seed=seed + 40))
    return "".join(o)


def celery(base, tip, w=16.0, bite=0.0, seed=3950):
    """Стебель сельдерея от base (низ, в кулаке) к tip (листья); bite — укороченный откушенный конец (0..1)."""
    bx, by = base
    tx, ty = tip
    L = math.hypot(tx - bx, ty - by)
    ux, uy = (tx - bx) / L, (ty - by) / L
    nx, ny = -uy, ux
    L2 = L * (1 - .3 * bite)
    ex, ey = bx + ux * L2, by + uy * L2
    body = [(bx + nx * w * .5, by + ny * w * .5), (ex + nx * w * .45, ey + ny * w * .45), (ex - nx * w * .5, ey - ny * w * .5),
            (bx - nx * w * .55, by - ny * w * .55)]
    inner = blob([(bx + nx * w * .1, by + ny * w * .1), (ex + nx * w * .1, ey + ny * w * .1), (ex - nx * w * .5, ey - ny * w * .5),
                  (bx - nx * w * .55, by - ny * w * .55)], "#8cc06a", .9)
    for j in (-.2, .15):
        inner += line([(bx + nx * w * j, by + ny * w * j), (ex + nx * w * j, ey + ny * w * j)], 1.8, "#6a9e4a", seed=seed + 3 + int(j * 10), op=.8)
    o = [shape(body, "#b5dc8a", inner, w=3.2, seed=seed)]
    if bite < .5:
        for j, (d, s_) in enumerate(((-.5, 1.0), (0.0, 1.2), (.5, .9))):
            lx, ly = ex + ux * 18 * s_ + nx * 16 * d, ey + uy * 18 * s_ + ny * 16 * d
            leaf = T([(-12, 4), (-14, -12), (0, -22), (14, -12), (12, 4)], lx, ly, 1.1, math.degrees(math.atan2(uy, ux)) + 90 + d * 40)
            o.append(shape(leaf, "#7cc46a", "", w=2.6, seed=seed + 10 + j))
    else:
        o.append(shape(ellipse_pts(ex, ey, w * .55, w * .3, 10, rot=math.degrees(math.atan2(uy, ux)) + 90), "#d9f0b6", "", w=2.4, seed=seed + 20))
    return "".join(o)


def napkin(x, y, k=1.0, rot=0.0, crumple=0.0, seed=3980):
    pts = [(-40, -30), (-6, -38 + 10 * crumple), (40, -32), (34 - 8 * crumple, 4), (40, 30), (-4, 36 - 8 * crumple), (-40, 30), (-30 + 6 * crumple, 0)]
    return shape(T(pts, x, y, k, rot), "#f6f1e6", blob(T([(0, 0), (40, -32), (34, 4), (40, 30)], x, y, k, rot), "#ddd5c4", .8), w=3, seed=seed)


# ─────────────────────────────── свет и сборка кадра
def glow34(mode="night", cx=700.0, cy=760.0):
    """Тёплый свет лампы над столом + тёмные углы (вечер)."""
    g = lib.rad_grad([(0, "#ffd890", .5), (.45, "#ffbe6a", .18), (1, "#ffbe6a", 0)], cx, cy, 1000, 900)
    g2 = lib.rad_grad([(0, "#000000", 0), (.5, "#000000", 0), (1, "#1a1030", .5)], cx, cy + 200, 1300, 1300)
    return (f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
            f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g2})"/>')


def lamp_cone34(t, cx=700.0):
    fl = 1 + .015 * math.sin(t * 7.3) + .01 * math.sin(t * 13)
    g = lib.lin_grad([(0, "#fff0c0", .34 * fl), (1, "#ffd890", 0)], 0, 0, 0, 1)
    pts = [(cx - 70, LAMP_Y + 80), (cx + 70, LAMP_Y + 80), (cx + 420, TABLE_F), (cx - 420, TABLE_F)]
    return f'<path d="{lib.fill_d([p + (1,) for p in pts])}" fill="url(#{g})" style="mix-blend-mode:screen" {lib.blur(16)}/>'


def vignette34():
    g = lib.rad_grad([(0, "#2a1408", 0), (.62, "#2a1408", 0), (1, "#2a1408", .42)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def compose(world_svg, cam, t=0.0, front="", screen="", cone=True):
    """cam = (cx, cy, s, rot): точка мира (cx, cy) — в центр кадра. Толщина туши подстраивается под масштаб."""
    cx, cy, s, r = cam
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62
    o = ['<rect width="1080" height="1920" fill="#e7cfa3"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world_svg}{lamp_cone34(t) if cone else ""}{glow34()}{front}</g>', screen, vignette34()]
    return lib.svg("".join(o))
