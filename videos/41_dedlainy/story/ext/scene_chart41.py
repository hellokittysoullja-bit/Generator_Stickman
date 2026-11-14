"""Сцена chart рилса 41 (s14 24.45–26.3, s15 26.3–28.1): итог опыта MIT на кремовом листе. Без букв.
Две одинаковые стопки листов-текстов: слева — один срок в конце (под ней значок: полоска из трёх недель с одним
большим красным флажком в конце), справа — ровные сроки (полоска с тремя маленькими зелёными флажками).
s14: с первого кадра над каждой стопкой ходит красный карандаш-корректор; на «ровными» (24.56) значки выскакивают;
     на «ошибок» (25.44) из верхних листов вылетают красные кружки найденных ошибок и складываются в два столбика над
     стопками (слева 4, справа 5).
s15: на «больше» (26.4) правый столбик выстреливает вверх до 8 кружков (вдвое выше левого, как в опыте: 136 ошибок
     против ~70); на «вовремя» (27.48) над правой стопкой будильник и большая зелёная галочка-штамп, над левой —
     будильник с красным крестиком (дрожит). Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg, T)

_ST = {}
EVEN = 24.56         # «ровными»
ERR = 25.44          # «ошибок»
MORE = 26.40         # «больше»
ONTIME = 27.48       # «вовремя»
XL, XR = 290, 790
BASE = 1120          # низ стопок
NSHEET = 9
SH_H = 15            # толщина листа в стопке
TOP = BASE - NSHEET * SH_H          # верх стопки (передняя кромка верхнего листа)
COL0 = TOP - 84      # центр нижнего кружка столбика
PITCH = 60
N_L, N_R0, N_R = 4, 5, 8
CLOCK_Y = 345
RED, RED_D, PINK = "#e5383b", "#a91f25", "#ffe3e0"
GREEN, GREEN_D = "#3cbf63", "#258a45"


def bg():
    s = []
    lin_grad([(0, "#f6eedb", 1), (1, "#ead9b8", 1)], 0, 0, 0, 1, gid="gChart41")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#gChart41)"/>')
    for k in range(-6, 34):
        s.append(f'<rect x="-900" y="{-400 + k * 80}" width="{W + 1800}" height="2" fill="#dccbaa"/>')
    s.append(line([(40, BASE + 4), (1040, BASE + 4)], 7, INK, taper=.05, wmin=.9, seed=7001))
    return "".join(s)


# ───────────────────────── стопка листов
def stack(x, sd):
    s = [blob(ellipse_pts(x + 14, BASE + 6, 200, 16, 16), "#8f7650", .35, blur(6))]
    for k in range(NSHEET):
        y1 = BASE - k * SH_H
        dx = [0, 5, -4, 6, -2, 4, -5, 2, 0][k]
        s.append(shape(rect_pts(x - 170 + dx, y1 - SH_H, x + 170 + dx, y1, 2), "#fbfaf4" if k % 2 else "#efebdf",
                       blob(rect_pts(x + 120 + dx, y1 - SH_H, x + 170 + dx, y1), "#dcd8cb", .8), w=3.2, seed=sd + k))
    # верхний лист — сверху в лёгкой перспективе, «строки» серыми штрихами
    top = [(x - 170, TOP, 1), (x + 170, TOP, 1), (x + 136, TOP - 74, 1), (x - 136, TOP - 74, 1)]
    inner = ""
    for j in range(5):
        y = TOP - 60 + j * 12
        x0 = x - 118 + j * 6
        x1 = x + 112 - j * 6 - (40 if j == 4 else 0)
        inner += line([(x0, y), (x1, y + 1)], 3.2, "#9a9488", taper=.1, wmin=.7, seed=sd + 20 + j, op=.9)
    inner += blob([(x + 90, TOP - 70), (x + 128, TOP - 70), (x + 160, TOP), (x + 110, TOP)], "#e9e5d8", .9)
    s.append(shape(top, "#fdfcf6", inner, w=3.6, seed=sd + 30))
    return "".join(s)


def pencil(x, y, ang, sd):
    """Красный карандаш-корректор: острие в (x, y), корпус уходит вверх-вправо под углом ang."""
    p = [(0, 0, 1), (16, -30), (30, -24, 1), (14, 6, 1)]
    body = [(16, -30, 1), (100, -190, 1), (114, -183, 1), (30, -24, 1)]
    g = shape(body, RED, blob([(23, -27), (107, -187), (114, -183), (30, -24)], RED_D, .9), w=3.4, seed=sd)
    g += shape(p, "#f3d9a8", blob([(0, 0), (8, -16), (14, -12)], RED_D), w=3, seed=sd + 1)
    g += shape([(100, -190, 1), (114, -183, 1), (124, -204, 1), (110, -211, 1)], "#f2a7b8", "", w=3, seed=sd + 2)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)})">{g}</g>'


def pencils(t):
    s = []
    for k, x in enumerate((XL, XR)):
        a = (t - 24.2) * (5.2 + 0.7 * k) + k * 1.7
        px = x - 60 + 110 * (0.5 + 0.5 * math.sin(a * 0.55))
        py = TOP - 46 + 14 * math.sin(a * 1.1) - 6 * abs(math.sin(a * 3.1))
        away = smooth(ERR - 0.1, ERR + 0.15, t)
        px += 60 * away
        py -= 300 * ease_in(away)
        if away > 0.98:
            continue
        s.append(pencil(px, py, 6 * math.sin(a * 2) - 4, 7100 + k * 10))
    return "".join(s)


def week_strip(x, y, even, t, sd, k):
    """Значок: полоска из трёх недель (по 5 клеток) и флажки — один большой красный в конце или три зелёных."""
    if k <= 0.01:
        return ""
    s = [shape(rect_pts(x - 150, y - 34, x + 150, y + 34, 16), "#fffdf6", blob(rect_pts(x - 150, y + 14, x + 150, y + 34), "#ece4d0", .8),
               w=4, seed=sd)]
    for c in range(15):
        cx0 = x - 138 + c * 18.4
        s.append(shape(rect_pts(cx0, y - 10, cx0 + 15, y + 12, 2), "#e9e1cd", "", w=2, seed=sd + 1 + c))
    for w_ in (1, 2):
        xx = x - 138 + w_ * 5 * 18.4 - 2
        s.append(line([(xx, y - 18), (xx, y + 20)], 3, "#9a8a6a", taper=.05, wmin=.9, seed=sd + 20 + w_))
    flags = [(x - 138 + 15 * 18.4 - 9, 1.5, RED, RED_D)] if not even else [(x - 138 + (w_ + 1) * 5 * 18.4 - 9, 0.9, GREEN, GREEN_D) for w_ in range(3)]
    for j, (fx, sc, c, cd) in enumerate(flags):
        wv = 3 * math.sin(t * 6 + j)
        pole = [(fx, y + 8), (fx, y - 58 * sc)]
        cloth = [(fx, y - 58 * sc, 1), (fx + 34 * sc, y - 50 * sc + wv), (fx + 30 * sc, y - 38 * sc + wv), (fx, y - 32 * sc, 1)]
        s.append(line(pole, 4 * sc + 1, INK, taper=.05, wmin=.9, seed=sd + 30 + j))
        s.append(shape(cloth, c, blob([(fx, y - 44 * sc), (fx + 32 * sc, y - 44 * sc + wv), (fx + 30 * sc, y - 38 * sc + wv), (fx, y - 32 * sc)], cd, .8),
                       w=2.8, seed=sd + 40 + j))
    g = "".join(s)
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(k)}) translate({f(-x)} {f(-y)})">{g}</g>'


# ───────────────────────── кружки ошибок
def err_mark(x, y, r, sd, sq=1.0):
    """Красный кружок корректора вокруг найденной ошибки: бледная заливка, серая «строка» внутри, обвод маркером."""
    inner = line([(x - r * .6, y - 5), (x + r * .6, y - 4)], 5, "#8a8478", taper=.1, wmin=.8, seed=sd + 1)
    wv = [(x - r * .6 + r * 1.2 * k / 8, y + 9 + (4 if k % 2 else -1)) for k in range(9)]
    inner += line(wv, 3.4, RED, taper=.1, wmin=.7, seed=sd + 2)
    g = shape(ellipse_pts(x, y, r * 1.18, r, 18), PINK, inner, w=7.5, seed=sd, ink_color=RED)
    g += blob(ellipse_pts(x - r * .55, y - r * .55, r * .18, r * .1, 8, rot=-30), "#ffffff", .9)
    if sq != 1.0:
        g = f'<g transform="translate({f(x)} {f(y + r)}) scale({f(1 / sq ** .5)} {f(sq)}) translate({f(-x)} {f(-y - r)})">{g}</g>'
    return g


def schedule():
    out = []
    for i in range(N_L):
        out.append(("L", i, ERR + 0.08 + i * 0.17))
    for i in range(N_R0):
        out.append(("R", i, ERR + 0.02 + i * 0.12))
    for i in range(N_R0, N_R):
        out.append(("R", i, MORE + 0.02 + (i - N_R0) * 0.06))
    return out


SCHED = schedule()


def marks(t):
    s = []
    for j, (col, i, tl) in enumerate(SCHED):
        x = (XL if col == "L" else XR) + (4 if i % 2 else -4)
        y = COL0 - i * PITCH
        shot = tl >= MORE
        dur = 0.34 if not shot else 0.16
        e = t - (tl - dur)
        if e < 0:
            continue
        if t < tl:
            u = e / dur
            if shot:            # выстрел: из-под верха столбика вверх
                y0 = COL0 - (N_R0 - 1) * PITCH
                yy = y0 + (y - y0) * ease_out(u)
                xx = x
            else:               # вылет из верхнего листа по дуге
                sx = x + (-60 if i % 2 else 60)
                sy = TOP - 40
                xx = sx + (x - sx) * u
                yy = sy + (y - sy) * u - 160 * math.sin(math.pi * u) * (1 - 0.3 * i / 8)
            sq = 1 + 0.15 * math.sin(math.pi * u)
            s.append(err_mark(xx, yy, 36, 7300 + j * 7, sq))
        else:
            el = t - tl
            sq = 1 - 0.22 * math.exp(-el * 14) * math.cos(el * 30)
            s.append(err_mark(x, y, 36, 7300 + j * 7, sq))
        # хлопок на появлении из листа
        if not shot and 0 <= e < 0.25:
            u = e / 0.25
            sx = x + (-60 if i % 2 else 60)
            for k in range(5):
                a = -math.pi * (0.15 + 0.7 * k / 4)
                r0 = 20 + 40 * ease_out(u)
                s.append(line([(sx + math.cos(a) * r0, TOP - 50 + math.sin(a) * r0), (sx + math.cos(a) * (r0 + 22 * (1 - u)), TOP - 50 + math.sin(a) * (r0 + 22 * (1 - u)))],
                              5 * (1 - u) + 1, RED, taper=.5, seed=7600 + j * 5 + k))
    # выстрел: штрихи скорости
    e = t - MORE
    if 0 <= e < 0.4:
        u = e / 0.4
        for k in range(4):
            xx = XR - 75 + k * 50
            y0 = COL0 - N_R * PITCH + 40 - 60 * u
            s.append(line([(xx, y0 + 140 * (1 - u)), (xx, y0)], 8 * (1 - u) + 2, "#ffcf3a", taper=.6, seed=7700 + k))
    return "".join(s)


# ───────────────────────── будильники, галочка, крестик
def alarm(x, y, sc, t, sd, ring=0.0):
    g = []
    sh = 3 * ring * math.sin(t * 60)
    for side in (-1, 1):
        bx, by = side * 52, -62
        g.append(shape(ellipse_pts(bx, by, 26, 18, 12, rot=side * 35), "#f2b43a", blob(ellipse_pts(bx + 4, by + 6, 18, 9, 10, rot=side * 35), "#c98a26", .9),
                       w=3.6, seed=sd + (side > 0)))
    for side in (-1, 1):
        g.append(line([(side * 40, 54), (side * 54, 78)], 7, INK, taper=.1, wmin=.9, seed=sd + 3 + (side > 0)))
    face = ellipse_pts(0, 0, 76, 76, 28)
    inner = blob(ellipse_pts(14, 16, 64, 62, 22), "#e7e0cf", .9)
    for k in range(12):
        a = math.radians(k * 30)
        r0, r1 = (52, 64) if k % 3 == 0 else (57, 64)
        inner += line([(math.cos(a) * r0, math.sin(a) * r0), (math.cos(a) * r1, math.sin(a) * r1)], 4 if k % 3 == 0 else 2.6, INK, taper=.1, wmin=.8,
                      seed=sd + 10 + k)
    am = math.radians(-90 + (t - 24) * 40)
    ah = math.radians(-90 + 300 + (t - 24) * 4)
    inner += line([(0, 0), (math.cos(ah) * 30, math.sin(ah) * 30)], 7, INK, taper=.2, wmin=.8, seed=sd + 30)
    inner += line([(0, 0), (math.cos(am) * 48, math.sin(am) * 48)], 5, INK, taper=.2, wmin=.8, seed=sd + 31)
    inner += f'<circle cx="0" cy="0" r="6" fill="{INK}"/>'
    g.append(shape(face, "#fffaf0", inner, w=5.4, seed=sd + 40))
    ring_ = shape(ellipse_pts(0, 0, 86, 86, 28), "#d64535", "", w=5, seed=sd + 42)
    return f'<g transform="translate({f(x + sh)} {f(y)}) scale({f(sc)})">{ring_}{"".join(g)}</g>'


def check(x, y, sc, sd):
    pts = [(-70, -6, 1), (-40, -36, 1), (-14, -8, 1), (50, -80, 1), (82, -50, 1), (-14, 52, 1)]
    g = shape(pts, GREEN, blob([(-14, 30), (82, -50), (82, -40), (-14, 52), (-70, -6), (-64, 0)], GREEN_D, .9) +
              line([(-56, -10), (-40, -26)], 5, "#9ff0b8", seed=sd + 1, op=.9), w=6, seed=sd)
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)}) rotate(-6)">{g}</g>'


def cross(x, y, sc, sd):
    a = [(-60, -40, 1), (-40, -60, 1), (0, -20, 1), (40, -60, 1), (60, -40, 1), (20, 0, 1), (60, 40, 1), (40, 60, 1), (0, 20, 1), (-40, 60, 1),
         (-60, 40, 1), (-20, 0, 1)]
    g = shape(a, RED, blob([(20, 0), (60, 40), (40, 60), (0, 20), (-40, 60), (-60, 40), (-20, 0), (-10, 10), (10, 10)], RED_D, .7), w=5.5, seed=sd)
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)}) rotate(4)">{g}</g>'


def verdict(t):
    s = []
    e = t - ONTIME
    # будильники выскакивают чуть раньше слова (на «сдавали»), знаки бьют на «вовремя»
    for k, x in enumerate((XL, XR)):
        ka = back_out(clamp((t - 27.04 - k * 0.06) / 0.28), 2.2)
        if ka <= 0.01:
            continue
        ring = math.exp(-max(e, 0) * 3) if (k == 1 and e > 0) else 0.0
        shake = 0.0
        if k == 0 and e > 0.05:
            shake = 6 * math.exp(-(e - 0.05) * 4) * math.sin((e - 0.05) * 40)
        s.append(alarm(x + shake, CLOCK_Y, ka * 0.95, t, 7800 + k * 50, ring))
    if e >= 0:
        # зелёная галочка-штамп: падает сверху крупной, бьёт, пыль-кольцо
        u = clamp(e / 0.16)
        sc = 1.9 - 0.9 * ease_in(u) if e < 0.16 else 1 + 0.08 * math.exp(-(e - 0.16) * 8) * math.sin((e - 0.16) * 30)
        s.append(check(XR + 96, CLOCK_Y + 24, sc * 1.2, 7900))
        if 0.12 < e < 0.6:
            uu = (e - 0.12) / 0.48
            for k in range(8):
                a = k * math.pi / 4 + .3
                r0 = 110 + 90 * ease_out(uu)
                s.append(line([(XR + 40 + math.cos(a) * r0, CLOCK_Y + 30 + math.sin(a) * r0),
                               (XR + 40 + math.cos(a) * (r0 + 34 * (1 - uu)), CLOCK_Y + 30 + math.sin(a) * (r0 + 34 * (1 - uu)))],
                              8 * (1 - uu) + 1.5, GREEN_D, taper=.5, seed=7950 + k))
        # красный крестик над левыми часами — чуть позже
        e2 = e - 0.08
        if e2 >= 0:
            u2 = clamp(e2 / 0.16)
            sc2 = 1.7 - 0.7 * ease_in(u2) if e2 < 0.16 else 1 + 0.06 * math.exp(-(e2 - 0.16) * 8) * math.sin((e2 - 0.16) * 30)
            s.append(cross(XL + 6, CLOCK_Y + 6, sc2 * 1.15, 7980))
    return "".join(s)


def build_static():
    if _ST:
        return
    _ST["bg"] = bg()
    _ST["stacks"] = stack(XL, 7010) + stack(XR, 7050)
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    s = [_ST["bg"]]
    s.append(_ST["stacks"])
    for k, (x, even) in enumerate(((XL, False), (XR, True))):
        kk = back_out(clamp((t - (24.3 if k == 0 else EVEN) + 0.04) / 0.26), 2.2)
        s.append(week_strip(x, BASE - 58, even, t, 7200 + k * 60, kk))
    s.append(pencils(t))
    s.append(marks(t))
    s.append(verdict(t))
    # камера: s14 — наезд с первого кадра; s15 — почти статика, толчки на «больше» и «вовремя»
    u = clamp((t - 24.25) / (26.3 - 24.25))
    sc = 1.1 + 0.1 * (0.4 * u + 0.6 * ease_io(u))
    cx, cy = 540, 880 - 30 * ease_io(clamp((t - 25.6) / 1.2))
    rot = -0.6 + 0.6 * u + 0.25 * math.sin(t * 0.9)
    for t0, amp in ((ERR, 0.02), (MORE, 0.035), (ONTIME, 0.05)):
        e = t - t0
        if e > 0:
            kk = math.exp(-e * 7)
            sc *= 1 + amp * kk * math.sin(min(e * 14, math.pi))
            cy += 8 * kk * math.sin(e * 46) * (amp > 0.03)
    return svg(f'<rect width="{W}" height="{H}" fill="#f0e4c8"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')
