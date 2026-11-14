"""Мечта рилса 44 «Япония»: Фудзи со снежной шапкой, сакура, красные тории, солнце, лепестки, облако-рамка.
Всё рисуется в координатах, которые задаёт вызывающий (сцена мечты s02, облачко-экран мозга s06, облачко в рамке
блокнота s11/s12). Манера — как у сцен 40–41: тушь с нажимом (lib.shape/line), плоский цвет и одна тень."""
import math

import numpy as np

import lib
from lib import INK, blob, blur, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape

SAK, SAK_SH, SAK_HI = "#f7b8cc", "#e58aa8", "#ffdbe6"
TORII, TORII_SH, TORII_BK = "#e0402e", "#b02a1e", "#2b2230"
FUJI, FUJI_SH, SNOW, SNOW_SH = "#7d8fd0", "#5d6fb2", "#ffffff", "#d6def5"


# ───────────────────────── облако с пушистым краем
def cloud_pts(cx, cy, rx, ry, n=11, bump=0.16, ph=0.0, m=8, wob=0.0):
    """Контур облака: эллипс, по краю n полукруглых «пуфов» (каждый — дуга из m точек, между пуфами — впадина-угол)."""
    pts = []
    for i in range(n):
        a0 = ph + 2 * math.pi * i / n
        a1 = ph + 2 * math.pi * (i + 1) / n
        # впадина — угол
        pts.append((cx + rx * math.cos(a0), cy + ry * math.sin(a0), 1))
        for k in range(1, m):
            u = k / m
            a = a0 + (a1 - a0) * u
            r = 1 + bump * (1 + 0.25 * math.sin(i * 2.3 + wob)) * math.sin(math.pi * u) ** 0.7
            pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return pts


def puff_cloud(cx, cy, rx, ry, sd=0, n=9, bump=0.18, ph=0.3, col="#ffffff", sh="#cfe0f6", w=5.0):
    """Отдельное пушистое облачко с голубой тенью снизу-справа."""
    pts = cloud_pts(cx, cy, rx, ry, n, bump, ph)
    inner = blob(cloud_pts(cx + rx * .22, cy + ry * .42, rx * .95, ry * .7, n, bump, ph + .2), sh, .95)
    inner += blob(ellipse_pts(cx - rx * .38, cy - ry * .32, rx * .32, ry * .18, 12, rot=-12), "#ffffff", .9)
    return shape(pts, col, inner, w=w, seed=sd)


# ───────────────────────── предметы мечты
def sun(x, y, r, t=0.0, sd=0):
    s = []
    g = rad_grad([(0, "#fff4c4", .95), (.4, "#ffe08a", .45), (1, "#ffe08a", 0)], x, y, r * 3.2, r * 3.2)
    s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 3.2)}" fill="url(#{g})"/>')
    for k in range(10):
        a = k * math.pi / 5 + 0.15 * math.sin(t * 1.3)
        r0 = r * (1.3 + 0.06 * math.sin(t * 4 + k))
        s.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r * 1.75 * math.cos(a), y + r * 1.75 * math.sin(a))],
                      r * 0.16, "#ffc94a", taper=.5, wmin=.3, seed=sd + 10 + k))
    s.append(shape(ellipse_pts(x, y, r, r, 26), "#ffd85a", blob(ellipse_pts(x + r * .3, y + r * .3, r * .8, r * .75, 18), "#ffbf3a", .9) +
                   blob(ellipse_pts(x - r * .38, y - r * .4, r * .28, r * .16, 10, rot=-30), "#fff6c8", .9), w=r * 0.07, seed=sd))
    return "".join(s)


def fuji(cx, base, w, h, sd=0):
    """Гора: вершина (cx, base−h), подошва шириной w; снежная шапка с зубчатым краем; тень справа."""
    top = base - h
    hw = w / 2
    crater = w * 0.07
    pts = [(cx - hw, base, 1), (cx - hw * .55, base - h * .28), (cx - hw * .26, base - h * .66), (cx - crater, top, 1),
           (cx - crater * .3, top + h * .025), (cx + crater * .35, top + h * .01), (cx + crater, top, 1), (cx + hw * .26, base - h * .66),
           (cx + hw * .55, base - h * .28), (cx + hw, base, 1)]
    inner = blob([(cx + crater * .2, top - 10), (cx + hw + 40, base), (cx + hw * .15, base), (cx + hw * .05, base - h * .5)], FUJI_SH, .9)
    # снег: зубцы вниз
    sy = top + h * 0.34
    snow = [(cx - crater - 30, top - 30, 1), (cx + crater + 30, top - 30, 1)]
    zig = []
    nz = 7
    for k in range(nz + 1):
        u = k / nz
        x = cx + hw * 0.62 * (0.5 - u) * -2 * 0.5 * 2 * -1
        x = cx - hw * .31 + hw * .62 * u
        y = sy + (h * 0.11 if k % 2 else -h * 0.02) + h * 0.03 * math.sin(k * 1.7)
        zig.append((x, y, 1) if k % 2 == 0 else (x, y))
    snow = [(cx - crater - 20, top - 40, 1), (cx + crater + 20, top - 40, 1)] + [(cx + hw * .5, sy - h * .06)] + zig[::-1] + [(cx - hw * .5, sy - h * .06)]
    sn_in = blob([(cx + crater * .3, top - 20), (cx + hw * .5, sy), (cx + hw * .1, sy + h * .1), (cx + crater * .1, top + h * .1)], SNOW_SH, .95)
    inner += shape(snow, SNOW, sn_in, w=max(2.2, w * 0.0045), seed=sd + 2)
    # лёгкие гряды-морщины
    for k, (u0, u1) in enumerate([(.42, .6), (.62, .8)]):
        x0 = cx - hw * u1 * .9
        inner += line([(x0, base - h * (1 - u1) * .9), (x0 + hw * .12, base - h * (1 - u0) * .9)], max(2, w * .004), FUJI_SH, seed=sd + 5 + k, op=.8)
    return shape(pts, FUJI, inner, w=max(2.6, w * 0.006), seed=sd)


def torii(x, base, h, sd=0, sway=0.0):
    """Ворота-тории: два красных столба, верхняя изогнутая балка (тёмная накладка), нижняя балка; без таблички-надписи."""
    s = []
    w = h * 0.95
    pw = h * 0.085
    lw = max(2.4, h * 0.016)
    for k, px in enumerate((x - w * .36, x + w * .36)):
        s.append(shape([(px - pw * .5, base - h * .78, 1), (px + pw * .5, base - h * .78, 1), (px + pw * .62, base, 1), (px - pw * .62, base, 1)],
                       TORII, blob([(px + pw * .05, base - h * .8), (px + pw * .7, base - h * .8), (px + pw * .7, base), (px + pw * .1, base)], TORII_SH, .9),
                       w=lw, seed=sd + k))
        s.append(shape(rect_pts(px - pw * .72, base - h * .06, px + pw * .72, base + h * .015, 2), TORII_BK, "", w=lw * .8, seed=sd + 3 + k))
    # нижняя балка (нуки)
    s.append(shape(rect_pts(x - w * .48, base - h * .66, x + w * .48, base - h * .59, 2), TORII, blob(rect_pts(x - w * .48, base - h * .62, x + w * .48, base - h * .59), TORII_SH, .9),
                   w=lw, seed=sd + 5))
    # средняя стойка (гакудзука, пустая)
    s.append(shape(rect_pts(x - pw * .35, base - h * .82, x + pw * .35, base - h * .66), TORII, "", w=lw * .8, seed=sd + 6))
    # верхняя балка: красная (симаги) + тёмная изогнутая (касаги) с загнутыми концами
    s.append(shape([(x - w * .52, base - h * .8, 1), (x + w * .52, base - h * .8, 1), (x + w * .5, base - h * .87, 1), (x - w * .5, base - h * .87, 1)],
                   TORII, blob([(x - w * .52, base - h * .83), (x + w * .52, base - h * .83), (x + w * .52, base - h * .8), (x - w * .52, base - h * .8)], TORII_SH, .9),
                   w=lw, seed=sd + 7))
    kas = [(x - w * .62, base - h * 1.0, 1), (x - w * .5, base - h * .95), (x, base - h * .925), (x + w * .5, base - h * .95), (x + w * .62, base - h * 1.0, 1),
           (x + w * .58, base - h * .9, 1), (x + w * .45, base - h * .87), (x, base - h * .855), (x - w * .45, base - h * .87), (x - w * .58, base - h * .9, 1)]
    s.append(shape(kas, TORII_BK, blob([(x - w * .5, base - h * .93), (x + w * .3, base - h * .915), (x + w * .3, base - h * .9), (x - w * .5, base - h * .91)], "#4a3e52", .9),
                   w=lw, seed=sd + 8))
    return "".join(s)


def blossom_puffs(cx, cy, rx, ry, sd, n=7):
    rs = np.random.RandomState(sd)
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n + rs.uniform(-.3, .3)
        r = rs.uniform(.35, .62)
        out.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a), rx * rs.uniform(.42, .58), ry * rs.uniform(.42, .58)))
    out.append((cx, cy, rx * .6, ry * .6))
    return out


def sakura(x, base, sc=1.0, sd=0, t=0.0):
    """Дерево сакуры: ствол с ветками (коричневый, тень справа), крона — слитые розовые пуфы с тенью снизу и цветками."""
    s = []
    trunk = [(x - 22 * sc, base, 1), (x - 16 * sc, base - 120 * sc), (x - 34 * sc, base - 210 * sc), (x - 70 * sc, base - 270 * sc),
             (x - 52 * sc, base - 282 * sc), (x - 14 * sc, base - 236 * sc), (x + 6 * sc, base - 300 * sc), (x + 26 * sc, base - 296 * sc),
             (x + 18 * sc, base - 220 * sc), (x + 64 * sc, base - 268 * sc), (x + 80 * sc, base - 254 * sc), (x + 26 * sc, base - 170 * sc),
             (x + 20 * sc, base - 100 * sc), (x + 28 * sc, base, 1)]
    s.append(shape(trunk, "#7a4a34", blob([(x + 4 * sc, base - 300 * sc), (x + 90 * sc, base - 260 * sc), (x + 30 * sc, base), (x + 6 * sc, base)], "#5c3424", .9),
                   w=4.4 * sc, seed=sd))
    sw = 4 * sc * math.sin(t * 1.6 + sd)
    cx, cy = x + 6 * sc + sw, base - 330 * sc
    puffs = blossom_puffs(cx, cy, 230 * sc, 150 * sc, sd + 3, 8)
    # общий силуэт кроны = объединение пуфов: рисуем заливку, потом тушь только по внешнему краю (каждый пуф с тушью, а
    # поверх — те же пуфы без туши, сжатые на толщину линии: внутренние линии исчезают, остаётся внешний контур)
    ink_l = []
    for k, (px, py, rx, ry) in enumerate(puffs):
        ink_l.append(shape(cloud_pts(px, py, rx, ry, 7, .12, k), SAK, "", w=4.6 * sc, seed=sd + 20 + k))
    fill_l = []
    for k, (px, py, rx, ry) in enumerate(puffs):
        fill_l.append(blob(cloud_pts(px, py, rx - 3.2 * sc, ry - 3.2 * sc, 7, .12, k), SAK))
    sh_l = []
    for k, (px, py, rx, ry) in enumerate(puffs):
        if py > cy - 20 * sc:
            sh_l.append(blob(ellipse_pts(px + rx * .2, py + ry * .45, rx * .8, ry * .45, 12), SAK_SH, .85))
    hi_l = []
    rs = np.random.RandomState(sd + 9)
    for k, (px, py, rx, ry) in enumerate(puffs):
        if py < cy + 10 * sc:
            hi_l.append(blob(ellipse_pts(px - rx * .25, py - ry * .3, rx * .35, ry * .2, 10, rot=-15), SAK_HI, .9))
    flw = []
    for k in range(16):
        px = cx + rs.uniform(-200, 200) * sc
        py = cy + rs.uniform(-120, 110) * sc
        flw.append(flower(px, py, 9 * sc, rs.uniform(0, 70)))
    canopy_clip = lib.clip_of(cloud_pts(cx, cy, 300 * sc, 230 * sc, 9, .1, 0))
    s.append("".join(ink_l) + "".join(fill_l) + "".join(sh_l) + "".join(hi_l) + "".join(flw))
    return "".join(s)


def flower(x, y, r, rot=0.0, col="#ffffff", core="#e8678f"):
    """Цветок сакуры: пять лепестков-капель с выемкой."""
    out = []
    for k in range(5):
        a = math.radians(rot + k * 72)
        px, py = x + r * .7 * math.cos(a), y + r * .7 * math.sin(a)
        out.append(blob(ellipse_pts(px, py, r * .55, r * .42, 8, rot=math.degrees(a)), col, .95))
    out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * .28)}" fill="{core}"/>')
    return "".join(out)


def petal(x, y, r, rot, sd, flip=1.0):
    """Падающий лепесток: капля с выемкой; flip — поворот вокруг оси (сжатие по x)."""
    pts = [(0, -r, 1), (r * .7, -r * .4), (r * .6, r * .5), (0, r * .9), (-r * .6, r * .5), (-r * .7, -r * .4)]
    pts[0] = (0, -r * .55, 1)
    pts = [(0, -r * .5, 1), (r * .35, -r * .95), (r * .75, -r * .3), (r * .55, r * .5), (0, r * .9), (-r * .55, r * .5), (-r * .75, -r * .3),
           (-r * .35, -r * .95)]
    sh = shape(pts, "#f9c3d3", blob([(0, -r * .2), (r * .8, -r * .2), (r * .6, r * .6), (0, r)], "#ec97b2", .9), w=max(1.6, r * .16), seed=sd)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(max(.15, abs(flip)))} 1)">{sh}</g>'


def petals(t, box, n, sd, size=(10, 16), speed=(60, 120), wind=90):
    """Лепестки, летящие по диагонали сквозь box=(x0, y0, x1, y1) (бесконечный цикл по времени)."""
    x0, y0, x1, y1 = box
    rs = np.random.RandomState(sd)
    out = []
    for k in range(n):
        px, py = rs.uniform(x0, x1), rs.uniform(y0, y1)
        vy = rs.uniform(*speed)
        vx = wind * rs.uniform(.6, 1.2)
        ph = rs.uniform(0, 6.28)
        r = rs.uniform(*size)
        x = x0 + (px - x0 + vx * t + 26 * math.sin(t * 2.1 + ph)) % (x1 - x0)
        y = y0 + (py - y0 + vy * t) % (y1 - y0)
        out.append(petal(x, y, r, 40 * math.sin(t * 2.4 + ph) + ph * 50, sd + 100 + k, math.cos(t * 3.1 + ph)))
    return "".join(out)


def mini_dream(t, sd=0, torii_on=True):
    """Маленькая картинка мечты в коробке 0..600 × 0..400 (для облачка-экрана и рамки блокнота): небо, солнце, Фудзи,
    холм, ветка сакуры слева, тории справа. Вызывающий сам обрезает её формой облака."""
    s = []
    g = lin_grad([(0, "#9fd0f2", 1), (.7, "#d9eefa", 1), (1, "#ffe6cc", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-40" y="-40" width="680" height="480" fill="url(#{g})"/>')
    s.append(sun(470, 110, 34, t, sd + 1))
    s.append(fuji(300, 330, 520, 230, sd + 10))
    s.append(shape([(-40, 300), (120, 286), (300, 300), (480, 284), (660, 296), (660, 460, 1), (-40, 460, 1)], "#9fd07c",
                   blob([(-40, 340), (660, 330), (660, 460), (-40, 460)], "#86bd64", .9), w=3.2, seed=sd + 20))
    if torii_on:
        s.append(torii(500, 340, 130, sd + 30))
    s.append(sakura(80, 400, 0.52, sd + 40, t))
    return "".join(s)
