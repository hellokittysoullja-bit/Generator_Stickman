"""Сцена brain рилса 41 (s10, 16.0–18.08): мозг рилсов 24–32 (brain_art без ствола, ручки scene_brain, ножки в кедах
scene_brain32) в тёмных очках лежит в гамаке между двумя столбами в солнечном саду; справа огромные песочные часы.
С первого кадра: гамак качается, ножки болтаются, облака плывут, песок сыплется вниз.
На «кажется» (16.0) мозг лениво машет правой ручкой; на «полно» (17.4) песок в часах пересыпается обратно наверх
(струя и песчинки летят вверх, верх снова полный), мозг кивает — очки съезжают на кончик — и подмигивает.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import brain_art
import lib
import scene_brain as sb
import scene_brain32 as b32
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg, T)

_ST = {}
SEEM = 16.0          # «кажется»
FULL = 17.4          # «полно»
GROUND = 1190
POST_L, POST_R = 140, 640
POST_TOP = 470
HG_X = 838           # ось песочных часов
HG_TOP, HG_NECK, HG_BOT = 480, 815, 1150
EYE_L, EYE_R = b32.EYE_L, b32.EYE_R
SAND, SAND_SH, SAND_HI = "#f0c25a", "#d39a32", "#ffe08a"


# ───────────────────────── фон: солнечный сад
def background():
    s = []
    g = lin_grad([(0, "#8fcbec", 1), (.55, "#bfe2f2", 1), (1, "#fbe6bf", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-700" width="{W + 1200}" height="{GROUND + 700}" fill="url(#{g})"/>')
    gs = rad_grad([(0, "#fff6c8", .95), (.35, "#fff1b0", .45), (1, "#fff1b0", 0)], 170, 250, 420, 420)
    s.append(f'<rect x="-600" y="-700" width="{W + 1200}" height="{GROUND + 700}" fill="url(#{gs})"/>')
    s.append(shape(ellipse_pts(170, 250, 86, 86, 28), "#ffe27a", blob(ellipse_pts(196, 276, 62, 58, 20), "#ffd04e", .9), w=4.4, seed=11))
    # дальние холмы и кусты
    hill = [(-600, 1010, 1), (-200, 950), (150, 990), (420, 930), (760, 985), (1060, 940), (1700, 1000, 1), (1700, GROUND + 4, 1), (-600, GROUND + 4, 1)]
    s.append(shape(hill, "#a9d18a", blob([(-600, 1080), (1700, 1060), (1700, GROUND + 4), (-600, GROUND + 4)], "#95c276", .9), w=4.2, seed=12))
    for k, (x, y, r) in enumerate([(-40, 1060, 110), (520, 1050, 90), (1100, 1040, 120)]):
        s.append(shape(ellipse_pts(x, y, r, r * .62, 18), "#6faa58", blob(ellipse_pts(x + r * .25, y + r * .2, r * .7, r * .4, 14), "#5a9446", .9),
                       w=4.2, seed=20 + k))
    # трава
    s.append(shape(rect_pts(-600, GROUND, W + 600, H + 400), "#8cc160",
                   blob(rect_pts(-600, GROUND, W + 600, GROUND + 26), "#7aae4f", .9), w=4.6, seed=30))
    rs = np.random.RandomState(5)
    for k in range(60):
        x, y = rs.uniform(-80, W + 80), rs.uniform(GROUND + 40, 1820)
        h = rs.uniform(14, 26)
        s.append(line([(x, y), (x + rs.uniform(-6, 6), y - h)], 3.2, "#5f9a40", taper=.6, wmin=.2, seed=40 + k))
    return "".join(s)


def clouds(t):
    s = []
    for k, (x0, y, sc, sp) in enumerate([(380, 200, 1.0, 9), (860, 330, 0.75, 13), (-120, 420, 0.6, 11)]):
        x = x0 + sp * (t - 15.8)
        body = [(-130, 30, 1), (-120, 0), (-90, -24), (-50, -50), (0, -60), (50, -46), (86, -20), (120, 4), (132, 30, 1)]
        pts = T(body, x, y, sc)
        s.append(shape(pts, "#ffffff", blob(T([(-120, 18), (120, 18), (132, 30), (-130, 30)], x, y, sc), "#e2f0f8", .9), w=3.6, seed=60 + k))
    return "".join(s)


def posts():
    s = []
    for k, x in enumerate((POST_L, POST_R)):
        s.append(blob(ellipse_pts(x + 10, GROUND + 8, 60, 12, 14), "#4f7a34", .55, blur(5)))
        s.append(shape(rect_pts(x - 20, POST_TOP, x + 20, GROUND + 6, 6), "#9a6a3e",
                       blob(rect_pts(x + 6, POST_TOP, x + 20, GROUND + 6), "#7a5030", .9) + line([(x - 8, POST_TOP + 40), (x - 6, GROUND - 30)], 3, "#c08a58", seed=70 + k, op=.8),
                       w=4.4, seed=72 + k))
        s.append(shape(ellipse_pts(x, POST_TOP, 22, 8, 12), "#b07a48", "", w=3.4, seed=74 + k))
    return "".join(s)


# ───────────────────────── песочные часы
def hw_top(v):
    """Полуширина стекла верхней колбы; v — 0 у горлышка, 1 у крышки."""
    return 13 + 96 * math.sin(math.pi / 2 * min(1.0, v / 0.62)) - 20 * smooth(0.8, 1.0, v)


def glass_pts():
    n = 14
    right, left = [], []
    for i in range(n + 1):                         # верх: от крышки к горлышку
        v = 1 - i / n
        y = HG_NECK - (HG_NECK - HG_TOP) * v
        right.append((HG_X + hw_top(v), y))
    for i in range(1, n + 1):                      # низ: от горлышка ко дну
        v = i / n
        y = HG_NECK + (HG_BOT - HG_NECK) * v
        right.append((HG_X + hw_top(v), y))
    left = [(2 * HG_X - x, y) for x, y in right[::-1]]
    return right + left


def sand_amount(t):
    """Доля песка вверху: сыплется вниз → на «полно» взлетает обратно → снова тонкая струйка вниз."""
    a0 = 0.6 - 0.07 * clamp((t - 15.6) / (FULL - 15.6))
    if t < FULL:
        return a0
    u = ease_io(clamp((t - FULL) / 0.6))
    a1 = a0 + (0.96 - a0) * u
    return a1 - 0.03 * clamp((t - 18.1) / 0.5)


def hourglass(t):
    a = sand_amount(t)
    up = FULL <= t < FULL + 0.62
    down = not up
    s = []
    s.append(blob(ellipse_pts(HG_X + 16, GROUND + 6, 160, 18, 16), "#4f7a34", .5, blur(6)))
    gp = glass_pts()
    inner = []
    # верхний песок: от горлышка до уровня; ямка воронки, когда сыплется вниз
    htop = (HG_NECK - HG_TOP - 30) * a
    yl = HG_NECK - htop
    dip = 16 if down else -10
    surf = [(HG_X - 200, yl), (HG_X - 60, yl + 2), (HG_X, yl + dip), (HG_X + 60, yl + 2), (HG_X + 200, yl)]
    inner.append(shape(surf + [(HG_X + 200, HG_NECK + 4, 1), (HG_X - 200, HG_NECK + 4, 1)], SAND,
                       blob([(HG_X + 30, yl), (HG_X + 200, yl), (HG_X + 200, HG_NECK), (HG_X + 20, HG_NECK)], SAND_SH, .85) +
                       line([(HG_X - 110, yl + 10), (HG_X - 40, yl + 8)], 4, SAND_HI, seed=101, op=.9), w=3.6, seed=100))
    # нижний песок: горка
    ab = max(0.04, 1.0 - a - 0.02)
    hb = (HG_BOT - HG_NECK - 30) * ab
    yb = HG_BOT - hb
    peak = 30 if down else 8
    mound = [(HG_X - 200, yb + 14), (HG_X - 90, yb + 6), (HG_X, yb - peak), (HG_X + 90, yb + 6), (HG_X + 200, yb + 14)]
    inner.append(shape(mound + [(HG_X + 200, HG_BOT + 6, 1), (HG_X - 200, HG_BOT + 6, 1)], SAND,
                       blob([(HG_X + 20, yb), (HG_X + 200, yb), (HG_X + 200, HG_BOT), (HG_X + 30, HG_BOT)], SAND_SH, .85), w=3.6, seed=110))
    # струя и песчинки
    rs = np.random.RandomState(9)
    if down:
        on = 1 - smooth(FULL - 0.02, FULL, t) if t < FULL else smooth(FULL + 0.65, FULL + 0.9, t)
        if on > 0.05:
            inner.append(line([(HG_X, HG_NECK - 6), (HG_X + 1, yb - peak + 4)], 6 * on + 1, SAND_SH, taper=.05, wmin=.8, seed=120))
            for k in range(8):
                ph = (t * 2.2 + k / 8) % 1
                y = HG_NECK + (yb - peak - HG_NECK) * ph
                inner.append(f'<circle cx="{f(HG_X + rs.uniform(-5, 5))}" cy="{f(y)}" r="3.4" fill="{SAND_SH}"/>')
    else:
        e = t - FULL
        k_on = smooth(0, 0.06, e) * (1 - smooth(0.5, 0.62, e))
        inner.append(line([(HG_X, yb - peak), (HG_X, yl - dip + 6)], 8 * k_on + 1, SAND_SH, taper=.05, wmin=.8, seed=121))
        for k in range(16):
            ph = (e * 3.4 + k / 16) % 1
            y = (yb - 10) + (yl - (yb - 10)) * ph
            x = HG_X + rs.uniform(-1, 1) * (8 + 40 * math.sin(math.pi * ph) * (abs(y - HG_NECK) > 40))
            inner.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(3.2 + 1.6 * rs.uniform())}" fill="{SAND_SH}"/>')
    # блики стекла
    inner.append(line([(HG_X - 74, HG_TOP + 60), (HG_X - 88, HG_TOP + 150), (HG_X - 72, HG_TOP + 240)], 9, "#ffffff", taper=.6, seed=130, op=.85))
    inner.append(line([(HG_X - 78, HG_NECK + 110), (HG_X - 92, HG_NECK + 200), (HG_X - 78, HG_NECK + 270)], 9, "#ffffff", taper=.6, seed=131, op=.85))
    s.append(shape(gp, "#e6f5fb", "".join(inner), w=5, seed=140))
    # крышки и стойки
    for k, (y0, y1) in enumerate(((HG_TOP - 52, HG_TOP + 2), (HG_BOT - 2, HG_BOT + 52))):
        s.append(shape(rect_pts(HG_X - 138, y0, HG_X + 138, y1, 14), "#a5703f",
                       blob(rect_pts(HG_X - 138, (y0 + y1) / 2 + 6, HG_X + 138, y1), "#86552c", .9) +
                       line([(HG_X - 110, y0 + 12), (HG_X + 50, y0 + 12)], 4, "#cf9a62", seed=150 + k, op=.9), w=5, seed=152 + k))
    for k, x in enumerate((HG_X - 116, HG_X + 116)):
        s.append(shape(rect_pts(x - 13, HG_TOP, x + 13, HG_BOT, 8), "#b47c48",
                       blob(rect_pts(x + 3, HG_TOP, x + 13, HG_BOT), "#8c5a30", .9), w=4.2, seed=160 + k))
        for j, yy in enumerate((HG_TOP + 120, HG_NECK, HG_BOT - 120)):
            s.append(shape(ellipse_pts(x, yy, 20, 12, 12), "#b47c48", blob(ellipse_pts(x + 6, yy + 3, 12, 8, 10), "#8c5a30", .9), w=3.6, seed=170 + k * 5 + j))
    # волшебство на «полно»: звёздочки над часами
    e = t - FULL
    if 0 <= e < 0.7:
        u = e / 0.7
        for k, (dx, dy, r0) in enumerate([(-130, -400, 22), (140, -360, 18), (10, -450, 26)]):
            sc_ = back_out(clamp(u / 0.3), 2.2) * (1 - smooth(0.6, 1.0, u))
            if sc_ > 0.03:
                s.append(star(HG_X + dx, HG_NECK + dy + 40, r0 * sc_, "#ffd34e", 190 + k, rot=40 * u))
    return "".join(s)


def star(x, y, r, col, sd, rot=0.0):
    pts = []
    for k in range(8):
        a = math.radians(rot + k * 45 - 90)
        rr = r if k % 2 == 0 else r * 0.38
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return shape(pts, col, "", w=2.8, seed=sd)


# ───────────────────────── гамак
def hammock(t, sway):
    sag = 140
    L = (POST_L + 70 + sway, 640)
    R = (POST_R - 64 + sway, 636)
    ropes = ""
    for k, (p, q) in enumerate((((POST_L, POST_TOP + 14), L), ((POST_R, POST_TOP + 14), R))):
        ropes += line([p, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 12), q], 5.5, "#7a5a3a", taper=.1, wmin=.9, seed=200 + k)
        for j in range(3):      # шнуры веером к краю ткани
            qq = (q[0] + (j - 1) * 12 * (1 if k == 0 else -1), q[1] + (j - 1) * 14)
            ropes += line([((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 12), qq], 3, "#7a5a3a", taper=.1, wmin=.9, seed=205 + k * 3 + j)
    top = [(L[0] + (R[0] - L[0]) * u, L[1] + (R[1] - L[1]) * u + sag * 0.5 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 11)]
    bot = [(L[0] + (R[0] - L[0]) * u, L[1] + (R[1] - L[1]) * u + sag * math.sin(math.pi * u) + 34 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 11)]
    pts = [(top[0][0], top[0][1], 1)] + top[1:-1] + [(top[-1][0], top[-1][1], 1)] + bot[::-1][1:-1]
    inner = ""
    for k in range(1, 10):     # полоски ткани
        if k % 2:
            inner += blob([top[k], top[k + 1], bot[k + 1], bot[k]], "#f2c84a", .95)
    inner += blob([(p[0], p[1] + 12) for p in bot[1:-1]] + [(p[0], p[1] - 4) for p in bot[::-1][1:-1]], "#b8452e", .55)
    fabric = shape(pts, "#e2603f", inner, w=4.6, seed=240)
    # изнанка ткани за мозгом: от верхней кромки сзади до передней — без просветов неба
    back = [(L[0] + (R[0] - L[0]) * u, L[1] + (R[1] - L[1]) * u + sag * 0.12 * math.sin(math.pi * u) - 30 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 11)]
    bpts = [(back[0][0], back[0][1], 1)] + back[1:-1] + [(back[-1][0], back[-1][1], 1)] + top[::-1][1:-1]
    ropes += shape(bpts, "#b8452e", blob([(p[0], p[1] + 30) for p in back] + top[::-1], "#9c3826", .6), w=4.2, seed=241)
    return ropes, fabric, top, bot


# ───────────────────────── лицо: глаза по отдельности, очки
def eye(x, y, look, blink, sd):
    if blink > 0.6:          # подмигнул: закрытый глаз — дуга с ресничкой
        return (line([(x - 28, y - 8), (x - 10, y - 22), (x + 10, y - 22), (x + 28, y - 8)], 7, INK, taper=.4, wmin=.35, seed=sd + 7) +
                line([(x - 22, y - 14), (x - 32, y - 24)], 3.4, INK, taper=.5, seed=sd + 8))
    ry = 36
    px, py = x + look[0] * 10, y + look[1] * 12
    inner = f'<circle cx="{f(px)}" cy="{f(py)}" r="9.5" fill="{INK}"/><circle cx="{f(px - 3)}" cy="{f(py - 3.5)}" r="3" fill="#ffffff"/>'
    if blink > 0.02:
        yb = y - ry - 2 + (2 * ry + 4) * blink
        inner += f'<rect x="{x - 32}" y="{y - ry - 4}" width="64" height="{f(yb - (y - ry - 4))}" fill="#f6a9bc"/>'
        inner += line([(x - 30, yb), (x, yb + 3), (x + 30, yb)], 4, INK, seed=sd + 4)
    return shape(ellipse_pts(x, y, 29, ry, 18), "#ffffff", inner, w=4.4, seed=sd)


def glasses(d):
    """Тёмные очки в локальных координатах мозга, опущены на d."""
    s = []
    for k, (x, y) in enumerate((EYE_L, EYE_R)):
        y += d
        pts = rect_pts(x - 41, y - 33, x + 41, y + 33, 26)
        g = lin_grad([(0, "#3a4566", 1), (1, "#141824", 1)], 0, 0, 0, 1)
        inner = line([(x - 22, y + 20), (x + 14, y - 22)], 7, "#8fa3d8", taper=.4, seed=260 + k, op=.8)
        inner += line([(x - 4, y + 24), (x + 24, y - 8)], 4, "#8fa3d8", taper=.4, seed=262 + k, op=.6)
        s.append(shape(pts, f"url(#{g})", inner, w=6.5, seed=264 + k))
    yb = (EYE_L[1] + EYE_R[1]) / 2 + d - 12
    s.append(line([(EYE_L[0] + 40, yb + 2), ((EYE_L[0] + EYE_R[0]) / 2, yb - 6), (EYE_R[0] - 40, yb)], 6.5, INK, taper=.1, wmin=.9, seed=268))
    s.append(line([(EYE_R[0] + 40, EYE_R[1] + d - 18), (EYE_R[0] + 120, EYE_R[1] + d - 34)], 7, INK, taper=.1, wmin=.9, seed=269))
    return "".join(s)


def face(t, d, wink):
    s = []
    look = (-0.35, -0.6) if d > 20 else (-0.2, 0.0)
    s.append(eye(*EYE_L, look, wink, 280))
    s.append(eye(*EYE_R, look, 0.0, 285))
    if d > 20:
        k = clamp((d - 20) / 12)
        for j, (x, y) in enumerate((EYE_L, EYE_R)):
            by = y - 52 - 10 * k - (6 if (j == 1 and wink > .3) else 0)
            s.append(line([(x - 22, by + 4), (x, by - 5), (x + 20, by + 2)], 5.5, "#8e3358", taper=.4, wmin=.4, seed=290 + j))
    s.append(glasses(d))
    # улыбка-ухмылка
    mx, my = BCX - 64, BCY + 94
    sm = 4 * math.sin(t * 2.0)
    s.append(line([(mx - 30, my - 6), (mx - 4, my + 12 + sm * .2), (mx + 26, my - 2 - 8 * wink)], 6, "#7a2a40", taper=.4, wmin=.4, seed=295))
    s.append(blob(ellipse_pts(BCX - 160, BCY + 56, 20, 10, 10), "#f07a98", .55))
    return "".join(s)


# ───────────────────────── кадр
def scene(t):
    sway = 10 * math.sin((t - 15.8) * 1.7)
    ropes, fabric, top, bot = hammock(t, sway)
    # мозг лежит в ткани; кивок на «полно» — очки съезжают
    nod = 0.0
    e = t - (FULL - 0.18)
    if e > 0:
        nod = 7 * math.sin(math.pi * clamp(e / 0.32))
    br = math.sin((t - 15.8) * 2 * math.pi / 2.2)
    px = 392 + sway * 0.9
    py = 584 + 5 * br + 4 * math.sin((t - 15.8) * 1.7 + 1)
    pose = sb.Pose(px, py, 0.86 * (1 + 0.01 * br), -9 + 2 * math.sin((t - 15.8) * 1.7) + nod)
    d = 32 * ease_out(clamp((t - (FULL - 0.12)) / 0.2))
    wink = 0.0
    for c, half in ((FULL + 0.32, 0.16),):
        if abs(t - c) < half:
            wink = 1.0 if abs(t - c) < half * 0.55 else (1 - (abs(t - c) - half * 0.55) / (half * 0.45))
    # ручки: левая за головой; правая лениво машет на «кажется»
    rel_l = pose.pt(BCX - 228, BCY - 60)
    rest_r = pose.pt(BCX + 214, BCY - 92)
    wave_k = smooth(SEEM - 0.15, SEEM + 0.12, t) * (1 - smooth(16.95, 17.2, t))
    up_r = pose.pt(BCX + 250, BCY - 260)
    wr = (rest_r[0] + (up_r[0] - rest_r[0]) * wave_k, rest_r[1] + (up_r[1] - rest_r[1]) * wave_k)
    ar_rest, ar_up = 140, -70 + 22 * math.sin((t - SEEM) * 7.5)
    ar = ar_rest + (ar_up - ar_rest) * wave_k
    cr = 0.6 * (1 - wave_k)
    body = sb.brain_with_arms(pose, rel_l, wr, 50, ar, 0.6, cr, -30, 40)
    body = body.replace(f'<g transform="{pose.tf()}">{_ST["brain"]}</g>',
                        f'<g transform="{pose.tf()}">{_ST["brain"]}{face(t, d, wink)}</g>')
    # ножки болтаются через край ткани
    sc = pose.sc
    hl, hr = pose.pt(*b32.HIP_L), pose.pt(*b32.HIP_R)
    swing = math.sin((t - 15.8) * 3.1)
    fl = (hl[0] + 70 + 16 * swing, hl[1] + 110)
    fr = (hr[0] + 60 - 16 * swing, hr[1] + 100)
    legs = b32.leg(hl, fl, sc, 1, 1200) + b32.leg(hr, fr, sc, 1, 1220)
    # мозг виден выше нижней кромки ткани
    cp = [(-600, -600, 1), (W + 600, -600, 1), (W + 600, bot[-1][1], 1)] + [(x, y - 4) for x, y in bot[::-1]] + [(-600, bot[0][1], 1)]
    c = lib.clip_of(cp)
    shadow = blob(ellipse_pts(392 + sway, GROUND + 6, 230, 18, 16), "#4f7a34", .45, blur(6))
    art = [shadow, _ST["posts"], ropes, f'<g clip-path="url(#{c})">{body}</g>', fabric, legs]
    return "".join(art)


def build_static():
    if _ST:
        return
    _ST["bg"] = background()
    _ST["brain"] = brain_art.brain(0, 0, stem=False)
    _ST["posts"] = posts()
    sb._ST["brain"] = _ST["brain"]
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art = scene(t)
    u = clamp((t - 15.8) / 2.48)
    cx, cy = 556 - 6 * u, 885 - 12 * ease_io(u)
    scl = 1.16 + 0.06 * (0.4 * u + 0.6 * ease_io(u))
    e = t - FULL
    if e > 0:
        k = math.exp(-e * 7)
        scl *= 1 + 0.04 * k * math.sin(min(e * 14, math.pi))
        cy += 7 * k * math.sin(e * 44)
    rot = 0.5 * math.sin(t * 1.1)
    return svg(f'<rect width="{W}" height="{H}" fill="#8cc160"/><g transform="{cam(cx, cy, scl, rot)}">'
               f'{_ST["bg"]}{clouds(t)}{hourglass(t)}{art}</g>')
