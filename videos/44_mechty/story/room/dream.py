"""Облако мечты рилса 44: пушистое белое облако с лёгкой голубой тенью, внутри — тёмно-синий вечер, гора Фудзи
со снежной шапкой, ветка сакуры, красные тории, низкое солнце у горизонта. Тот же мир продолжает план s02 (другой
агент рисует его изнутри облака). Лепестки сакуры — отдельной функцией (летят по кадру).
Всё в локальных координатах облака: центр (0, 0), полуоси rx, ry; картина внутри рисуется в «окне» 1000×700."""
import math

import numpy as np

import lib
from ink import ellipse_pts, fill_d, ink_closed
from lib import INK, blob, line, shape

CLOUD, CLOUD_SH, CLOUD_SH2 = "#ffffff", "#dbe8f6", "#c3d6ec"
SAKURA, SAKURA_SH, SAKURA_HI = "#f6b7c9", "#e48aa6", "#fde2ea"
TORII, TORII_SH = "#d8402e", "#a52b20"


def cloud_pts(rx, ry, n=12, wob=0.0, t=0.0, seed=0):
    """Контур облака: n выпуклых «бугров» по эллипсу (дуги по 4 точки), впадины между ними помечены углом —
    тушь рисует настоящие пушистые бугры, а не волнистый овал."""
    rs = np.random.RandomState(seed)
    amp = rs.uniform(.9, 1.15, n)
    ph = rs.uniform(0, 6.28, n)
    out = []
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        p0 = (rx * math.cos(a0), ry * math.sin(a0))
        p1 = (rx * math.cos(a1), ry * math.sin(a1))
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        nx, ny = mx / max(1e-6, math.hypot(mx, my)), my / max(1e-6, math.hypot(mx, my))
        bulge = L * .42 * amp[i] * (1 + wob * math.sin(t * 3.1 + ph[i]))
        out.append((p0[0], p0[1], 1))
        for k in (1, 2, 3):
            u = k / 4
            bx = p0[0] + (p1[0] - p0[0]) * u + nx * bulge * math.sin(math.pi * u)
            by = p0[1] + (p1[1] - p0[1]) * u + ny * bulge * math.sin(math.pi * u)
            out.append((bx, by))
    return out


def scene_inside(t, w=1000.0, h=760.0, pan=0.0):
    """Мечта внутри облака: окно с центром (0, 0) шириной w, высотой h. pan — сдвиг панорамы (px)."""
    o = []
    x0, y0 = -w / 2, -h / 2
    sky = lib.lin_grad([(0, "#1c2a5c", 1), (.55, "#3d4f8f", 1), (.82, "#c9879a", 1), (1, "#f2b38a", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="{x0 - 60:.0f}" y="{y0 - 60:.0f}" width="{w + 120:.0f}" height="{h + 120:.0f}" fill="url(#{sky})"/>')
    # звёзды
    rs = np.random.RandomState(4401)
    for k in range(22):
        x, y = rs.uniform(x0, x0 + w), rs.uniform(y0, y0 + h * .35)
        r = rs.uniform(1.8, 3.4) * (0.75 + .25 * math.sin(t * 4 + k))
        o.append(blob(ellipse_pts(x, y, r, r, 6), "#fff6d8", .9))
    # солнце у горизонта (садится за гору)
    sx, sy = x0 + w * .74 - pan * .2, y0 + h * .58
    g = lib.rad_grad([(0, "#ffe2a0", .9), (.4, "#ffc07a", .45), (1, "#ffb07a", 0)], sx, sy, 190, 150)
    o.append(f'<rect x="{x0 - 60:.0f}" y="{y0:.0f}" width="{w + 120:.0f}" height="{h:.0f}" fill="url(#{g})"/>')
    o.append(blob(ellipse_pts(sx, sy, 46, 46, 18), "#ffe7a8"))
    # Фудзи: синий конус, снежная шапка с зубцами
    fx, fb = -pan * .35, y0 + h * .78
    top = fb - h * .5
    mt = [(fx - w * .62, fb + 40, 1), (fx - w * .2, top + h * .2), (fx - w * .07, top + 6), (fx + w * .07, top + 6), (fx + w * .2, top + h * .2),
          (fx + w * .62, fb + 40, 1)]
    snow = [(fx - w * .16, top + h * .17), (fx - w * .07, top + 6), (fx + w * .07, top + 6), (fx + w * .16, top + h * .17), (fx + w * .11, top + h * .22),
            (fx + w * .06, top + h * .16), (fx + w * .02, top + h * .23), (fx - w * .03, top + h * .15), (fx - w * .08, top + h * .22),
            (fx - w * .12, top + h * .16)]
    inner = blob([(fx, top), (fx + w * .62, fb + 40), (fx + w * .1, fb + 40)], "#3a4f86", .55)
    inner += shape(snow, "#f7f9ff", blob([(fx, top), (fx + w * .16, top + h * .17), (fx + w * .11, top + h * .22), (fx + w * .02, top + h * .1)],
                                          "#c8d6ee", .9), w=3.2, seed=4410)
    o.append(shape(mt, "#5b74b0", inner, w=4.2, seed=4411))
    # дальний холм и озеро
    o.append(shape([(x0 - 80, fb + 30), (x0 + w * .3, fb - 10), (x0 + w * .7, fb + 10), (x0 + w + 80, fb - 20), (x0 + w + 80, y0 + h + 80, 1),
                    (x0 - 80, y0 + h + 80, 1)], "#2f5a5a", blob([(x0 - 80, fb + 60), (x0 + w + 80, fb + 50), (x0 + w + 80, y0 + h + 80),
                                                                (x0 - 80, y0 + h + 80)], "#244848", .8), w=3.8, seed=4412))
    # тории справа
    tx, tb = x0 + w * .78 - pan * .6, fb + 70
    th = h * .34
    for k, px in enumerate((tx - 62, tx + 62)):
        o.append(shape([(px - 10, tb, 1), (px - 8, tb - th, 1), (px + 8, tb - th, 1), (px + 10, tb, 1)], TORII,
                       blob([(px + 2, tb), (px + 2, tb - th), (px + 8, tb - th), (px + 10, tb)], TORII_SH, .9), w=3.2, seed=4420 + k))
    o.append(shape([(tx - 100, tb - th * .78, 1), (tx + 100, tb - th * .78, 1), (tx + 100, tb - th * .7, 1), (tx - 100, tb - th * .7, 1)], TORII,
                   "", w=3, seed=4423))
    o.append(shape([(tx - 122, tb - th - 4), (tx - 60, tb - th + 6), (tx + 60, tb - th + 6), (tx + 122, tb - th - 4, 1), (tx + 116, tb - th + 16, 1),
                    (tx - 116, tb - th + 16, 1)], TORII, blob([(tx - 120, tb - th + 8), (tx + 120, tb - th + 8), (tx + 116, tb - th + 16),
                                                               (tx - 116, tb - th + 16)], TORII_SH, .9), w=3.4, seed=4424))
    o.append(shape([(tx - 132, tb - th - 22), (tx - 60, tb - th - 8), (tx + 60, tb - th - 8), (tx + 132, tb - th - 22, 1), (tx + 126, tb - th - 6, 1),
                    (tx - 126, tb - th - 6, 1)], "#2b1d22", "", w=3, seed=4425))
    # сакура слева: ствол и шапка цветов
    bx, bb = x0 + w * .16 - pan * .8, y0 + h + 30
    trunk = [(bx - 22, bb, 1), (bx - 14, bb - 160), (bx - 50, bb - 260), (bx - 40, bb - 268), (bx - 2, bb - 190), (bx + 34, bb - 290),
             (bx + 46, bb - 282), (bx + 16, bb - 170), (bx + 22, bb, 1)]
    o.append(shape(trunk, "#5a3a32", blob([(bx + 4, bb), (bx + 8, bb - 170), (bx + 22, bb - 160), (bx + 22, bb)], "#3e2620", .8), w=3.6, seed=4430))
    for k, (cx, cy, r) in enumerate([(-60, -300, 90), (40, -330, 100), (-10, -380, 84), (110, -280, 70), (-120, -250, 66)]):
        sw = 4 * math.sin(t * 1.7 + k)
        pts = cloud_pts(r * 1.05, r * .82, n=7, seed=4440 + k)
        pts = [(bx + cx + sw + p[0], bb + cy + p[1]) + tuple(p[2:]) for p in pts]
        inn = blob([(bx + cx - r, bb + cy + r * .1), (bx + cx + r * 1.1, bb + cy), (bx + cx + r * 1.1, bb + cy + r), (bx + cx - r, bb + cy + r)],
                   SAKURA_SH, .8)
        rs2 = np.random.RandomState(4450 + k)
        for j in range(5):
            qx, qy = bx + cx + sw + rs2.uniform(-r * .6, r * .6), bb + cy + rs2.uniform(-r * .5, r * .2)
            inn += blob(ellipse_pts(qx, qy, 8, 6, 8), SAKURA_HI, .95)
        o.append(shape(pts, SAKURA, inn, w=3.2, seed=4460 + k))
    return "".join(o)


def cloud(t, rx, ry, inside="", wob=0.04, seed=4500, ink_w=5.2):
    """Облако с центром (0, 0): белый пушистый край (кольцо) и окно с мечтой внутри.
    Кольцо — сам контур облака, окно — тот же контур, сжатый на ~13 %; тень голубая по низу кольца."""
    outer = cloud_pts(rx, ry, wob=wob, t=t, seed=seed)
    win = cloud_pts(rx * .86, ry * .82, n=12, wob=wob * .6, t=t + 1.3, seed=seed + 1)
    o = []
    c_out = lib.clip_of(outer)
    sh = blob([(-rx * 1.3, ry * .35), (rx * 1.3, ry * .25), (rx * 1.3, ry * 1.3), (-rx * 1.3, ry * 1.3)], CLOUD_SH, .95)
    sh += blob(ellipse_pts(rx * .2, ry * 1.05, rx * 1.1, ry * .45, 18), CLOUD_SH2, .8)
    o.append(f'<path d="{fill_d(outer)}" fill="{CLOUD}"/><g clip-path="url(#{c_out})">{sh}</g>')
    if inside:
        c_in = lib.clip_of(win)
        o.append(f'<g clip-path="url(#{c_in})">{inside}</g>')
        o.append(f'<path d="{ink_closed(win, 3.6 * lib.INK_K[0], seed=seed + 2)}" fill="{CLOUD_SH2}"/>')
    o.append(f'<path d="{ink_closed(outer, ink_w * lib.INK_K[0], seed=seed + 3)}" fill="{INK}"/>')
    return "".join(o)


def puff(x, y, r, seed, t=0.0):
    """Маленький пузырь-облачко мысли."""
    pts = cloud_pts(r, r * .86, n=6, wob=.05, t=t, seed=seed)
    pts = [(x + p[0], y + p[1]) + tuple(p[2:]) for p in pts]
    inner = blob([(x - r * 1.4, y + r * .25), (x + r * 1.4, y + r * .15), (x + r * 1.4, y + r * 1.4), (x - r * 1.4, y + r * 1.4)], CLOUD_SH, .9)
    return shape(pts, CLOUD, inner, w=4.2, seed=seed + 7)


def petal(x, y, s, rot, seed):
    pts = [(0, -12), (7, -8), (9, 2), (4, 11), (0, 8, 1), (-4, 11), (-9, 2), (-7, -8)]
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    P = [(x + (p[0] * c - p[1] * sn) * s, y + (p[0] * sn + p[1] * c) * s) + tuple(p[2:]) for p in pts]
    inner = blob([(x + (0 * c - 4 * sn) * s, y + (0 * sn + 4 * c) * s), (x + (9 * c - 2 * sn) * s, y + (9 * sn + 2 * c) * s),
                  (x + (4 * c - 11 * sn) * s, y + (4 * sn + 11 * c) * s)], SAKURA_SH, .7)
    return shape(P, SAKURA, inner, w=2.2 * s, seed=seed)


def petals(t, n, box, seed=4600, k=1.0, wind=(-160.0, 90.0)):
    """n лепестков летят по box=(x0, y0, x1, y1) ветром, кружатся; положение — от общего времени t (зациклено)."""
    x0, y0, x1, y1 = box
    rs = np.random.RandomState(seed)
    o = []
    for j in range(n):
        px, py = rs.uniform(x0, x1), rs.uniform(y0, y1)
        sp = rs.uniform(.7, 1.3)
        ph = rs.uniform(0, 6.28)
        s = rs.uniform(1.3, 2.4) * k
        x = (px - x0 + wind[0] * sp * t) % (x1 - x0) + x0 + 26 * math.sin(t * 2.2 + ph)
        y = (py - y0 + wind[1] * sp * t) % (y1 - y0) + y0 + 14 * math.sin(t * 3.1 + ph)
        o.append(petal(x, y, s, (t * 160 * sp + ph * 57) % 360, seed + j))
    return "".join(o)
