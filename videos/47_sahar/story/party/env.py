"""Рилс 47, сцена party: комната праздника (статика: стена, пол, ковёр, окно, стол с торчной скатертью, торт, кусок, сахар, гирлянда)
и динамические детали (шары, пламя свечи, конфетти, молнии-искры). Координаты мира = экран при камере 1:1; мир шире кадра (x −600…1700)."""
import math

import numpy as np

import lib
from lib import INK, blob, blur, clamp, ellipse_pts, f, line, mix, mul, rect_pts, shape, smooth

FLOOR_Y = 1232                       # низ стены, дальше пол
TB_X0, TB_X1, TB_TOP = 20, 450, 1000  # стол: левый-правый край, верх
CAKE_X = 235
SLICE_X = 382
SUGAR_X = 85
WALL, WALL_SH, WALL_HI = "#f2d3ae", "#e6bd92", "#f9e4c8"
WOOD, WOOD_SH = "#c78b56", "#a8703f"
COL = ["#e8505b", "#f2b632", "#4aa3df", "#7bc67e", "#b56ad6", "#f08a4b"]


def wall_floor():
    s = []
    s.append(f'<rect x="-700" y="-200" width="2600" height="{FLOOR_Y + 200}" fill="{WALL}"/>')
    # полосы обоев
    for k in range(-6, 16):
        x = k * 150
        s.append(f'<rect x="{x}" y="-200" width="75" height="{FLOOR_Y + 200}" fill="{WALL_HI}" opacity=".55"/>')
    # тёплый свет сверху / тёмный низ стены
    g = lib.lin_grad([(0, "#ffffff", 0.0), (1, "#b9774b", 0.28)], 0, 0, 0, 1)
    s.append(f'<rect x="-700" y="500" width="2600" height="{FLOOR_Y - 500}" fill="url(#{g})"/>')
    # плинтус
    s.append(f'<rect x="-700" y="{FLOOR_Y - 34}" width="2600" height="34" fill="#fff3e0"/>')
    s.append(f'<rect x="-700" y="{FLOOR_Y - 34}" width="2600" height="6" fill="#e6d3b6"/>')
    s.append(f'<rect x="-700" y="{FLOOR_Y - 3}" width="2600" height="5" fill="{INK}" opacity=".85"/>')
    # пол
    s.append(f'<rect x="-700" y="{FLOOR_Y}" width="2600" height="1000" fill="{WOOD}"/>')
    gg = lib.lin_grad([(0, "#5a2d12", 0.38), (0.25, "#5a2d12", 0.0)], 0, 0, 0, 1)
    s.append(f'<rect x="-700" y="{FLOOR_Y}" width="2600" height="1000" fill="url(#{gg})"/>')
    for k in range(-6, 16):                       # доски в перспективе
        x0 = k * 220
        s.append(f'<path d="M{x0} {FLOOR_Y} L{x0 + (x0 - 540) * 1.15:.0f} 1960" stroke="{WOOD_SH}" stroke-width="5" fill="none" opacity=".75"/>')
    for yy, k in ((1262, 1.0), (1330, 1.0), (1440, 1.0), (1600, 1.0), (1800, 1.0)):
        s.append(f'<rect x="-700" y="{yy}" width="2600" height="3" fill="{WOOD_SH}" opacity=".6"/>')
    return "".join(s)


def rug():
    s = []
    cx, cy = 560, 1330
    s.append(blob(ellipse_pts(cx + 10, cy + 14, 560, 108, 28), "#3a1e0c", .25, blur(10)))
    s.append(shape(ellipse_pts(cx, cy, 540, 100, 28), "#8fc1d8", blob(ellipse_pts(cx, cy + 14, 480, 74, 24), "#6fa6c4", .55), w=5, seed=60))
    s.append(shape(ellipse_pts(cx, cy, 420, 72, 24), "#fbe7a8", w=3.6, seed=61))
    s.append(shape(ellipse_pts(cx, cy, 300, 48, 20), "#e9788a", w=3.2, seed=62))
    for k in range(18):                           # бахрома-ромбики по кольцу
        a = k * 2 * math.pi / 18
        x, y = cx + 360 * math.cos(a), cy + 60 * math.sin(a)
        s.append(f'<rect x="{f(x - 7)}" y="{f(y - 7)}" width="14" height="14" fill="#8fc1d8" transform="rotate(45 {f(x)} {f(y)})"/>')
    return "".join(s)


def window():
    x0, y0, x1, y1 = 800, 330, 1060, 760
    s = []
    s.append(shape(rect_pts(x0 - 18, y0 - 18, x1 + 18, y1 + 18, 6), "#fff6e6", w=5, seed=70))
    g = lib.lin_grad([(0, "#8fd0f2", 1), (1, "#d9f1fb", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>')
    s.append(blob(ellipse_pts(900, 470, 70, 28, 12), "#ffffff", .95) + blob(ellipse_pts(960, 450, 52, 24, 12), "#ffffff", .95))
    s.append(blob(ellipse_pts(960, 690, 190, 60, 14), "#8fcf79"))
    s.append(f'<rect x="{(x0 + x1) // 2 - 4}" y="{y0}" width="8" height="{y1 - y0}" fill="#fff6e6"/>')
    s.append(f'<rect x="{x0}" y="{(y0 + y1) // 2 - 4}" width="{x1 - x0}" height="8" fill="#fff6e6"/>')
    s.append(f'<path d="{lib.ink_closed(rect_pts(x0, y0, x1, y1), 4.4, seed=71)}" fill="{INK}"/>')
    # шторы
    for sx, xx in ((-1, x0 - 40), (1, x1 + 40)):
        pts = [(xx - 50, 300), (xx + 50, 300), (xx + 56 * sx, 600), (xx + 40 * sx, 800), (xx - 50, 800)]
        s.append(shape(pts, "#f08a9a", line([(xx - 10, 310), (xx - 14, 790)], 3, "#c9626f", seed=74) + line([(xx + 20, 310), (xx + 26, 790)], 3, "#c9626f", seed=75), w=4.4, seed=72 + sx))
    s.append(line([(x0 - 120, 300), (x1 + 120, 300)], 9, "#8a5a36", taper=.1, wmin=.9, seed=73))
    return "".join(s)


def picture(x, y, w, h, seed, col):
    s = [shape(rect_pts(x, y, x + w, y + h, 4), "#fff6e6", w=4.4, seed=seed)]
    s.append(f'<rect x="{x + 14}" y="{y + 14}" width="{w - 28}" height="{h - 28}" fill="{col}"/>')
    s.append(blob(ellipse_pts(x + w * .5, y + h * .62, w * .28, h * .2, 10), mul(col, (1.15, 1.1, .9))))
    s.append(blob(ellipse_pts(x + w * .34, y + h * .34, w * .09, w * .09, 10), "#fff2a8"))
    return "".join(s)


def table_back():
    """Ножки (дальние тёмнее) — до кота."""
    s = []
    x0, x1 = TB_X0, TB_X1
    for xx, k, c in ((x0 + 86, .8, WOOD_SH), (x1 - 86, .8, WOOD_SH)):
        s.append(shape([(xx - 12, TB_TOP + 70), (xx + 12, TB_TOP + 70), (xx + 9, 1286, 1), (xx - 9, 1286, 1)], mul(c, (.82, .8, .82)), w=3.6, seed=int(xx)))
    for xx in (x0 + 26, x1 - 26):
        s.append(shape([(xx - 18, TB_TOP + 60), (xx + 18, TB_TOP + 60), (xx + 14, 1318, 1), (xx - 14, 1318, 1)], WOOD,
                       blob([(xx + 4, TB_TOP + 60), (xx + 18, TB_TOP + 60), (xx + 14, 1318), (xx + 2, 1318)], WOOD_SH, .8), w=4.4, seed=int(xx) + 3))
    return "".join(s)


def under_shadow():
    return blob(ellipse_pts((TB_X0 + TB_X1) / 2, 1296, 236, 26, 18), "#2a1408", .38, blur(7))


def table_top():
    """Скатерть: верхняя плоскость и фартук с фестонами."""
    x0, x1 = TB_X0, TB_X1
    s = []
    top = [(x0 + 18, TB_TOP - 24), (x1 - 18, TB_TOP - 24), (x1 + 16, TB_TOP + 4, 1), (x0 - 16, TB_TOP + 4, 1)]
    s.append(shape(top, "#fffaf0", blob([(x0 + 160, TB_TOP - 24), (x1 - 18, TB_TOP - 24), (x1 + 16, TB_TOP + 4), (x0 + 120, TB_TOP + 4)], "#efe3cd", .7), w=4.4, seed=80))
    # фартук
    ap = [(x0 - 16, TB_TOP + 4, 1), (x1 + 16, TB_TOP + 4, 1), (x1 + 16, TB_TOP + 62, 1)]
    n = 10
    for k in range(n):
        xa = x1 + 16 - (x1 - x0 + 32) * (k + 0.5) / n
        ap.append((xa, TB_TOP + 84))
        xb = x1 + 16 - (x1 - x0 + 32) * (k + 1) / n
        ap.append((xb, TB_TOP + 60, 1))
    ap[-1] = (x0 - 16, TB_TOP + 62, 1)
    stripes = ""
    for k in range(0, 22):
        stripes += f'<rect x="{x0 - 16 + k * 22}" y="{TB_TOP}" width="11" height="120" fill="#e8505b" opacity=".9"/>'
    s.append(shape(ap, "#fffaf0", stripes + blob([(x1 - 120, TB_TOP + 4), (x1 + 16, TB_TOP + 4), (x1 + 16, TB_TOP + 84), (x1 - 150, TB_TOP + 84)], "#6a4a2a", .12), w=4.4, seed=81))
    return "".join(s)


def cake_static(y=TB_TOP - 24):
    """Торт на тарелке: низ y — плоскость стола."""
    cx = CAKE_X
    s = []
    s.append(blob(ellipse_pts(cx + 6, y + 6, 134, 15, 16), "#3a2410", .25, blur(3)))
    s.append(shape(ellipse_pts(cx, y - 2, 126, 15, 18), "#ffffff", blob(ellipse_pts(cx + 14, y + 2, 100, 10, 14), "#e2d6c2", .8), w=4, seed=90))
    # нижний ярус
    b1 = [(cx - 100, y - 10, 1), (cx + 100, y - 10, 1), (cx + 100, y - 86, 1), (cx - 100, y - 86, 1)]
    layers = (f'<rect x="{cx - 104}" y="{y - 86}" width="208" height="30" fill="#f6d9a0"/>'
              f'<rect x="{cx - 104}" y="{y - 56}" width="208" height="9" fill="#fff4de"/>'
              f'<rect x="{cx - 104}" y="{y - 47}" width="208" height="28" fill="#c98a54"/>'
              f'<rect x="{cx - 104}" y="{y - 19}" width="208" height="9" fill="#fff4de"/>'
              f'<rect x="{cx + 46}" y="{y - 90}" width="60" height="90" fill="#6a3a1a" opacity=".16"/>')
    s.append(shape(b1, "#f6d9a0", layers, w=4.6, seed=91))
    # верхний ярус
    b2 = [(cx - 68, y - 86, 1), (cx + 68, y - 86, 1), (cx + 68, y - 148, 1), (cx - 68, y - 148, 1)]
    l2 = (f'<rect x="{cx - 72}" y="{y - 148}" width="144" height="26" fill="#c98a54"/>'
          f'<rect x="{cx - 72}" y="{y - 122}" width="144" height="8" fill="#fff4de"/>'
          f'<rect x="{cx - 72}" y="{y - 114}" width="144" height="28" fill="#f6d9a0"/>'
          f'<rect x="{cx + 30}" y="{y - 150}" width="44" height="66" fill="#6a3a1a" opacity=".16"/>')
    s.append(shape(b2, "#f6d9a0", l2, w=4.6, seed=92))
    # глазурь с потёками на верхнем ярусе и на нижнем
    gl = [(cx - 74, y - 150, 1), (cx + 74, y - 150, 1), (cx + 74, y - 138, 1)]
    for k in range(7):
        xa = cx + 74 - 148 * (k + 0.5) / 7
        gl.append((xa, y - 108 + (k % 3) * 14))
        gl.append((cx + 74 - 148 * (k + 1) / 7, y - 136, 1))
    gl[-1] = (cx - 74, y - 138, 1)
    s.append(shape(gl, "#fff7ee", blob([(cx + 30, y - 150), (cx + 74, y - 150), (cx + 74, y - 120), (cx + 40, y - 126)], "#f3dcdd", .8), w=4, seed=93))
    gl2 = [(cx - 106, y - 88, 1), (cx + 106, y - 88, 1), (cx + 106, y - 74, 1)]
    for k in range(9):
        gl2.append((cx + 106 - 212 * (k + 0.5) / 9, y - 50 + (k * 5 % 3) * 12))
        gl2.append((cx + 106 - 212 * (k + 1) / 9, y - 72, 1))
    gl2[-1] = (cx - 106, y - 74, 1)
    s.append(shape(gl2, "#f7a9bc", blob([(cx + 40, y - 88), (cx + 106, y - 88), (cx + 106, y - 62), (cx + 50, y - 70)], "#e07c96", .7), w=4, seed=94))
    # клубника и ягоды
    for k, (dx, dy) in enumerate(((-44, 0), (-14, -6), (18, -4), (46, 0))):
        px, py = cx + dx, y - 150 + dy
        s.append(shape([(px - 13, py - 2, 1), (px + 13, py - 2, 1), (px + 8, py - 22), (px, py - 28), (px - 8, py - 22)], "#e2364a" if k % 2 == 0 else "#c4223d",
                       blob([(px + 3, py - 2), (px + 13, py - 2), (px + 8, py - 22)], "#a01a30", .7) + line([(px - 4, py - 14), (px - 3, py - 10)], 2, "#ffe4b0", seed=95 + k), w=3.4, seed=96 + k))
        s.append(blob([(px - 8, py - 28), (px, py - 36), (px + 8, py - 28), (px, py - 25)], "#4f9a4a"))
    # свеча
    s.append(shape([(cx - 6, y - 150, 1), (cx + 6, y - 150, 1), (cx + 6, y - 208, 1), (cx - 6, y - 208, 1)], "#fff2d8",
                   f'<rect x="{cx - 8}" y="{y - 190}" width="16" height="8" fill="#e8505b"/><rect x="{cx - 8}" y="{y - 172}" width="16" height="8" fill="#e8505b"/><rect x="{cx - 8}" y="{y - 154}" width="16" height="8" fill="#e8505b"/>', w=3.4, seed=97))
    return "".join(s)


def candle_flame(t, x=CAKE_X, y=TB_TOP - 24 - 208):
    w1 = 3 * math.sin(t * 19) + 2 * math.sin(t * 31 + 1)
    pts = [(x - 9, y - 2), (x - 11, y - 18), (x - 4 + w1 * .3, y - 34), (x + w1, y - 52, 1), (x + 5, y - 30), (x + 11, y - 16), (x + 8, y - 2), (x, y + 3)]
    o = blob(ellipse_pts(x, y - 20, 34, 44, 14), "#ffd86a", .28, blur(8))
    o += shape(pts, "#ffb02e", blob([(x - 4, y - 2), (x - 3, y - 18), (x + w1 * .5, y - 32), (x + 4, y - 16), (x + 4, y - 2)], "#fff3b0"), w=2.6, seed=98)
    return o


def cube(x, y, k, rot=0.0, seed=0):
    """Кубик сахара (изометрия): низ в (x, y), ребро ~k."""
    a = 0.866
    top = [(0, -k * 2), (k * a, -k * 1.5), (0, -k), (-k * a, -k * 1.5)]
    left = [(-k * a, -k * 1.5), (0, -k), (0, 0), (-k * a, -k * .5)]
    right = [(0, -k), (k * a, -k * 1.5), (k * a, -k * .5), (0, 0)]
    T = lambda pts: [(x + p[0], y + p[1], 1) for p in pts]  # noqa: E731
    g = (shape(T(left), "#e9e4dc", w=2.8, seed=seed) + shape(T(right), "#d3cdc2", w=2.8, seed=seed + 1) + shape(T(top), "#ffffff", w=2.8, seed=seed + 2))
    for j in range(3):
        g += f'<circle cx="{f(x + (j - 1) * k * .3)}" cy="{f(y - k * 1.5 + (j % 2) * 3)}" r="1.6" fill="#cfc8bb"/>'
    return f'<g transform="rotate({rot:.1f} {f(x)} {f(y - k)})">{g}</g>'


def sugar_bowl(x, y, sd=0):
    s = []
    s.append(blob(ellipse_pts(x + 4, y + 4, 62, 9, 12), "#3a2410", .22, blur(3)))
    bowl = [(x - 64, y - 28, 1), (x + 64, y - 28, 1), (x + 52, y - 4), (x + 30, y + 2), (x - 30, y + 2), (x - 52, y - 4)]
    s.append(shape(bowl, "#cfe6f2", line([(x - 50, y - 20), (x - 40, y - 4)], 3.4, "#ffffff", seed=410, op=.9) + blob([(x + 30, y - 28), (x + 64, y - 28), (x + 52, y - 4), (x + 30, y + 2)], "#9dc4d8", .6), w=4, seed=411))
    s.append(shape(ellipse_pts(x, y - 28, 64, 8, 14), "#e5f2f8", w=3.6, seed=412))
    # горка кубиков над краем: задний ряд, потом передний
    for k, (dx, dy, kk, r) in enumerate([(-30, -24, 17, 6), (4, -30, 17, -4), (36, -22, 17, 8), (-14, -46, 17, -6), (22, -50, 17, 5), (4, -70, 17, 2)]):
        s.append(cube(x + dx, y + dy, kk, r, 400 + k * 4))
    return "".join(s)


def cake_slice(x, y, sd=0):
    """Кусок торта на тарелке: вид сбоку-сверху, клин."""
    s = []
    s.append(blob(ellipse_pts(x + 6, y + 6, 68, 10, 14), "#3a2410", .22, blur(3)))
    s.append(shape(ellipse_pts(x, y - 2, 62, 10, 16), "#ffffff", blob(ellipse_pts(x + 8, y + 1, 46, 6, 10), "#e2d6c2", .8), w=3.6, seed=420))
    wedge = [(x - 38, y - 6, 1), (x + 40, y - 12, 1), (x + 40, y - 70, 1), (x - 38, y - 70, 1)]
    layers = (f'<rect x="{x - 44}" y="{y - 70}" width="90" height="24" fill="#f6d9a0"/>'
              f'<rect x="{x - 44}" y="{y - 46}" width="90" height="7" fill="#fff4de"/>'
              f'<rect x="{x - 44}" y="{y - 39}" width="90" height="22" fill="#c98a54"/>'
              f'<rect x="{x - 44}" y="{y - 17}" width="90" height="7" fill="#fff4de"/>')
    s.append(shape(wedge, "#f6d9a0", layers, w=3.8, seed=421))
    gl = [(x - 40, y - 72, 1), (x + 42, y - 72, 1), (x + 42, y - 60, 1), (x + 28, y - 46), (x + 14, y - 62, 1), (x, y - 50), (x - 14, y - 62, 1), (x - 28, y - 48), (x - 40, y - 60, 1)]
    s.append(shape(gl, "#f7a9bc", w=3.4, seed=422))
    s.append(shape([(x - 8, y - 74, 1), (x + 8, y - 74, 1), (x + 6, y - 92), (x, y - 98), (x - 6, y - 92)], "#e2364a", blob([(x + 2, y - 74), (x + 8, y - 74), (x + 6, y - 92)], "#a01a30", .7), w=3, seed=423))
    return "".join(s)


def table_props():
    y = TB_TOP - 24
    s = []
    # бумажные стаканчики и колпак на дальнем краю стола
    for k, (xx, c) in enumerate(((440, "#4aa3df"), (462, "#f2b632"))):
        s.append(shape([(xx - 14, y - 2, 1), (xx + 14, y - 2, 1), (xx + 10, y - 40, 1), (xx - 10, y - 40, 1)], c, line([(xx - 4, y - 32), (xx - 6, y - 8)], 3, "#ffffff", seed=430 + k, op=.7), w=3.6, seed=431 + k))
    s.append(shape([(150, y - 2, 1), (192, y - 2, 1), (170, y - 74)], "#b56ad6", blob([(176, y - 2), (192, y - 2), (172, y - 70)], "#8a47a8", .8) +
                   blob(ellipse_pts(166, y - 36, 5, 5, 8), "#fff2a8") + blob(ellipse_pts(176, y - 18, 5, 5, 8), "#fff2a8"), w=3.6, seed=432))
    s.append(blob(ellipse_pts(170, y - 76, 10, 10, 10), "#f2b632"))
    return "".join(s)


def bunting(t):
    """Гирлянда флажков: два провисающих шнура; флажки чуть качаются."""
    s = []
    for (xa, ya, xb, yb, sag, sd) in ((-300, 150, 760, 120, 120, 500), (560, 120, 1500, 160, 110, 520)):
        pts = []
        n = 14
        for k in range(n + 1):
            u = k / n
            pts.append((xa + (xb - xa) * u, ya + (yb - ya) * u + sag * 4 * u * (1 - u)))
        s.append(line(pts, 3.6, INK, taper=.1, wmin=.9, seed=sd))
        for k in range(n):
            u = (k + .5) / n
            x, y = pts[k][0], pts[k][1]
            x2, y2 = pts[k + 1][0], pts[k + 1][1]
            mx, my = (x + x2) / 2, (y + y2) / 2
            sw = 5 * math.sin(t * 2.3 + k * .8 + sd)
            tri = [(x + 4, y + 2, 1), (x2 - 4, y2 + 2, 1), (mx + sw, my + 74)]
            c = COL[(k + sd // 20) % 6]
            s.append(shape(tri, c, blob([(mx, my), (x2 - 4, y2 + 2), (mx + sw, my + 74)], mul(c, (.8, .8, .85)), .55), w=3.2, seed=sd + 10 + k))
    return "".join(s)


def balloon(x, y, r, col, t, ph, string_to, sd, tilt=0.0):
    """Шар: овал с узелком, блик и нить до string_to (рука / стол)."""
    bx = x + 7 * math.sin(t * 1.7 + ph)
    by = y + 6 * math.sin(t * 1.3 + ph * 1.4)
    pts = [(bx, by - r * 1.18), (bx + r * .8, by - r * .7), (bx + r * .98, by - r * .05), (bx + r * .6, by + r * .82), (bx, by + r * 1.12, 1),
           (bx - r * .6, by + r * .82), (bx - r * .98, by - r * .05), (bx - r * .8, by - r * .7)]
    s = []
    mid = ((bx + string_to[0]) / 2 + 14 * math.sin(t * 2 + ph), (by + r * 1.15 + string_to[1]) / 2)
    s.append(line([(bx, by + r * 1.2), mid, string_to], 2.6, "#4a3a36", taper=.2, wmin=.8, seed=sd + 5))
    inner = blob([(bx + r * .35, by - r * 1.1), (bx + r * .98, by - r * .1), (bx + r * .6, by + r * .85), (bx, by + r * 1.1), (bx + r * .1, by)], mul(col, (.78, .76, .82)), .8)
    inner += blob(ellipse_pts(bx - r * .42, by - r * .5, r * .13, r * .26, 8, rot=25), "#ffffff", .85)
    s.append(shape(pts, col, inner, w=4.2, seed=sd))
    s.append(shape([(bx - 8, by + r * 1.18, 1), (bx + 8, by + r * 1.18, 1), (bx, by + r * 1.05)], mul(col, (.85, .8, .85)), w=2.4, seed=sd + 1))
    return "".join(s)


def balloon_clusters(t):
    s = []
    anchors = (((20, 1000), [(-30, 600, 62, 0), (70, 540, 66, 1), (150, 650, 58, 2)]),
               ((1180, 1290), [(1120, 700, 64, 3), (1230, 650, 60, 4), (1170, 800, 56, 5)]))
    k = 0
    for (ax, ay), bl in anchors:
        for (x, y, r, ci) in bl:
            s.append(balloon(x, y, r, COL[ci % 6], t, k * 1.3, (ax, ay), 600 + k * 7))
            k += 1
    return "".join(s)


def confetti(t, t0, n=46, area=(-100, 1300), top=120, fall=520, seed=5, life=1e9, dens=1.0):
    """Конфетти, падающее после t0: куски, вращаются; позиции из ГПСЧ (детерминированно)."""
    if t < t0:
        return ""
    rs = np.random.RandomState(seed)
    s = []
    for k in range(n):
        x0 = rs.uniform(*area)
        y0 = top + rs.uniform(-300, 300)
        v = fall * rs.uniform(.7, 1.3)
        ph = rs.uniform(0, 6.28)
        wd, ht = rs.uniform(10, 18), rs.uniform(5, 9)
        c = COL[k % 6]
        e = t - t0
        y = (y0 + v * e) % 1900 - 80 if life > 1e8 else y0 + v * e
        x = x0 + 40 * math.sin(e * 3 + ph)
        if life < 1e8 and (e > life or y > 1700):
            continue
        a = e * rs.uniform(200, 500) + ph * 60
        s.append(f'<rect x="{f(x - wd / 2)}" y="{f(y - ht / 2)}" width="{f(wd)}" height="{f(ht)}" fill="{c}" transform="rotate({f(a)} {f(x)} {f(y)})"/>')
    return "".join(s)


def bolt(cx, cy, k, rot, col="#ffd93a", sd=0):
    pts = [(0, -40), (16, -40), (4, -10), (22, -10), (-10, 42), (-2, 8), (-20, 8)]
    pts = [(cx + (p[0] * math.cos(math.radians(rot)) - p[1] * math.sin(math.radians(rot))) * k,
            cy + (p[0] * math.sin(math.radians(rot)) + p[1] * math.cos(math.radians(rot))) * k, 1) for p in pts]
    return shape(pts, col, "", w=3.4, seed=sd)


def spark4(x, y, r, col="#fff3a0", rot=0.0):
    pts = []
    for i in range(8):
        rad = r if i % 2 == 0 else r * .3
        a = i * math.pi / 4 + math.radians(rot) - math.pi / 2
        pts.append((x + rad * math.cos(a), y + rad * math.sin(a), 1))
    return shape(pts, col, "", w=2.6, seed=int(x + y) % 997)


_ = (clamp, mix, smooth)
