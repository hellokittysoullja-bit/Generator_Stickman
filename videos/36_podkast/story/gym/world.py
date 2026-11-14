"""Спортзал рилса 36 (сцена gym): светлые стены, серо-зелёный пол, окно (вечер), календарь-месяц на стене, стойка
с гантелями, напольный вентилятор, чёрная беговая дорожка с серой лентой, стойкой, пультом и поручнями.

Система дорожки (мир): верх ленты y = 0, x вправо (Дима бежит вправо, пульт справа). Пол у стены — y = 60,
низ ножек дорожки — y = 104. Манера — как кухня/комнаты рилсов 29–35: живая тушь, плоский цвет + одна тень."""
import math

import numpy as np

import lib
from lib import INK, T, blob, clamp, ellipse_pts, line, mix, rect_pts, shape

WALL, WALL_SH, PANEL, PANEL_SH = "#efe9dc", "#d9d0bd", "#cfdcd3", "#b3c4b8"
FLOOR_C, FLOOR_SH, FLOOR_L = "#9eac9a", "#86947f", "#8b9a87"
TM, TM_SH, TM_HI, BELT, BELT_SH = "#2c2d33", "#1b1c21", "#4a4c55", "#6c7076", "#575a60"
METAL, METAL_SH = "#c9ccd2", "#9a9ea8"
WALL_FOOT = 60
FLOOR_Y = 104
DECK = (-340, 196)          # лента по x
CAL = (-300, -560, 210)     # календарь: центр x, верх y, ширина
WIN = (60, 330, -1150, -640)
FAN = (430, FLOOR_Y)
RACK = (-640, WALL_FOOT + 40)


def wall():
    s = [f'<rect x="-1600" y="-2200" width="3600" height="{2200 + WALL_FOOT}" fill="{WALL}"/>']
    # нижняя панель стены и полоса-молдинг
    s.append(shape(rect_pts(-1600, -230, 2000, WALL_FOOT), PANEL, blob(rect_pts(-1600, -230, 2000, -200), PANEL_SH, .8), w=4.0, seed=3001))
    s.append(shape(rect_pts(-1600, -246, 2000, -228), "#f7f3ea", "", w=3.6, seed=3002))
    # мягкие пятна света от потолочных ламп
    for x in (-500, 300, 1100):
        g = lib.rad_grad([(0, "#fffaf0", .55), (1, "#fffaf0", 0)], x, -900, 420, 520)
        s.append(f'<rect x="{x - 460}" y="-1500" width="920" height="1300" fill="url(#{g})"/>')
    return "".join(s)


def floor():
    s = [shape(rect_pts(-1600, WALL_FOOT, 2000, 1400), FLOOR_C, "", w=4.0, seed=3010)]
    # резиновые плиты пола: швы в перспективе к точке схода над пультом
    vx = 60
    for i, x in enumerate(range(-1500, 2000, 230)):
        x2 = vx + (x - vx) * 3.2
        s.append(line([(x, WALL_FOOT + 4), (x2, 1400)], 2.2, FLOOR_L, taper=.05, wmin=.8, seed=3011 + i, op=.8))
    for i, y in enumerate((150, 300, 520, 820)):
        s.append(line([(-1600, y), (2000, y)], 2.2, FLOOR_L, taper=.05, wmin=.8, seed=3040 + i, op=.75))
    # плинтус
    s.append(shape(rect_pts(-1600, WALL_FOOT - 22, 2000, WALL_FOOT + 4), "#e7e1d3", blob(rect_pts(-1600, WALL_FOOT - 6, 2000, WALL_FOOT + 4), "#cfc7b6"),
                   w=3.6, seed=3050))
    return "".join(s)


def window(t=0.0):
    x0, x1, y0, y1 = WIN
    sky = lib.lin_grad([(0, "#3d5d9c", 1), (.55, "#8c86b8", 1), (1, "#f2b98a", 1)], 0, 0, 0, 1)
    inner = f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>'
    inner += blob(ellipse_pts(x0 + 200, y0 + 150, 26, 26, 14), "#fbf2d8")
    for k, (x, y) in enumerate([(x0 + 60, y0 + 80), (x0 + 120, y0 + 200), (x0 + 230, y0 + 60)]):
        r = 3.5 + 1.0 * math.sin(t * 3 + k)
        inner += blob(ellipse_pts(x, y, r, r, 6), "#f6efd6")
    for k, (cx, cy, w) in enumerate([(x0 + 90, y0 + 300, 80), (x0 + 210, y0 + 340, 60)]):
        inner += blob(ellipse_pts(cx + 8 * math.sin(t * .3 + k), cy, w, 18, 12), "#f7d2b4", .85)
    roof = "#3a3f63"
    inner += blob([(x0 - 20, y1 - 120), (x0 + 50, y1 - 120), (x0 + 50, y1 - 190), (x0 + 130, y1 - 190), (x0 + 130, y1 - 140), (x0 + 190, y1 - 140),
                   (x0 + 190, y1 - 230), (x1 + 20, y1 - 230), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)], roof)
    for k, (x, y) in enumerate([(x0 + 64, y1 - 170), (x0 + 96, y1 - 170), (x0 + 210, y1 - 200), (x0 + 236, y1 - 160), (x0 + 150, y1 - 110),
                                (x0 + 18, y1 - 90)]):
        inner += blob(rect_pts(x, y, x + 16, y + 22), "#f6c86a")
    fr = "#f7f3ea"
    mx = (x0 + x1) / 2
    inner += blob(rect_pts(mx - 10, y0, mx + 10, y1), fr) + blob(rect_pts(x0, y0 + 190, x1, y0 + 206), fr)
    inner += blob([(x0, y0), (x0 + 60, y0), (x0 + 160, y1), (x0 + 100, y1)], "#ffffff", .12)
    s = [shape(rect_pts(x0, y0, x1, y1, 8), fr, inner, w=5, seed=3060)]
    s.append(shape(rect_pts(x0 - 24, y1 - 4, x1 + 24, y1 + 26, 6), fr, blob(rect_pts(x0 - 24, y1 + 14, x1 + 24, y1 + 26), "#ddd6c6"), w=4.2, seed=3061))
    return "".join(s)


def _check(cx, cy, r, sd, op=1.0, col="#2fa457"):
    pts = [(cx - r * .55, cy + r * .02), (cx - r * .12, cy + r * .45), (cx + r * .62, cy - r * .5)]
    return line(pts, r * .34, col, taper=.25, wmin=.45, seed=sd, op=op)


def calendar(checks=(), stamp=None, x=None, k=1.0):
    """Календарь-месяц: красная шапка с кольцами, сетка 7×5 пустых клеток (без цифр и букв).
    checks — клетки с галочкой (индексы 0..34); stamp = (клетка, u) — галочка-штамп: u 0→1 — влетает крупной и садится."""
    cx, top, w = CAL
    cx = cx if x is None else x
    w *= k
    h = w * 1.18
    x0, y0 = cx - w / 2, top
    s = [blob(rect_pts(x0 + 8, y0 + 12, x0 + w + 8, y0 + h + 12, 6), "#000000", .1)]
    head_h = h * .2
    gx0, gy0 = x0 + w * .07, y0 + head_h + h * .06
    cw, ch = w * .86 / 7, (h - head_h - h * .12) / 5
    inner = blob(rect_pts(x0 - 10, y0 - 10, x0 + w + 10, y0 + head_h), "#d9534a")
    inner += blob(rect_pts(x0 - 10, y0 + head_h - 6, x0 + w + 10, y0 + head_h), "#b8443c")
    # вместо названия месяца — два светлых штриха-плашки
    inner += blob(rect_pts(cx - w * .22, y0 + head_h * .38, cx + w * .22, y0 + head_h * .62, 4), "#f3c8bf")
    for j in range(6):
        y = gy0 + j * ch
        inner += line([(gx0, y), (gx0 + 7 * cw, y)], 1.8, "#c9c0ae", taper=.02, wmin=.9, seed=3070 + j)
    for i in range(8):
        x = gx0 + i * cw
        inner += line([(x, gy0), (x, gy0 + 5 * ch)], 1.8, "#c9c0ae", taper=.02, wmin=.9, seed=3080 + i)
    # выходные — чуть розовее
    for j in range(5):
        for i in (5, 6):
            inner += blob(rect_pts(gx0 + i * cw + 2, gy0 + j * ch + 2, gx0 + (i + 1) * cw - 2, gy0 + (j + 1) * ch - 2), "#f6e4de")
    s.append(shape(rect_pts(x0, y0, x0 + w, y0 + h, 5), "#fbf8f1", inner, w=4.4, seed=3090))
    for i, rx in enumerate((x0 + w * .25, x0 + w * .75)):
        s.append(shape(ellipse_pts(rx, y0 - 2, 7, 11, 10), METAL, "", w=2.6, seed=3091 + i))
    s.append(line([(cx - 3, y0 - 30), (cx, y0 - 44)], 3, INK, seed=3093))
    s.append(blob(ellipse_pts(cx, y0 - 46, 5, 5, 8), "#9a9ea8"))
    for n in checks:
        i, j = n % 7, n // 7
        s.append(_check(gx0 + (i + .5) * cw, gy0 + (j + .5) * ch, min(cw, ch) * .78, 3100 + n))
    if stamp is not None:
        n, u = stamp
        if u > 0:
            i, j = n % 7, n // 7
            ccx, ccy = gx0 + (i + .5) * cw, gy0 + (j + .5) * ch
            sc = 1 + 1.6 * (1 - clamp(u / .45)) ** 2 if u < .45 else 1 + 0.18 * math.exp(-(u - .45) * 9) * math.sin((u - .45) * 30)
            r = min(cw, ch) * .78
            s.append(f'<g transform="translate({ccx:.1f} {ccy:.1f}) scale({sc:.3f}) translate({-ccx:.1f} {-ccy:.1f})">'
                     f'{_check(ccx, ccy, r * 1.1, 3150)}</g>')
            if .42 < u < 1.0:
                a = 1 - (u - .42) / .58
                for q in range(8):
                    ang = q * math.pi / 4 + .3
                    r0, r1 = r * (.75 + .6 * (u - .42)), r * (1.05 + .9 * (u - .42))
                    s.append(line([(ccx + r0 * math.cos(ang), ccy + r0 * math.sin(ang)), (ccx + r1 * math.cos(ang), ccy + r1 * math.sin(ang))],
                                  3.4, "#2fa457", taper=.3, seed=3160 + q, op=a))
    return "".join(s)


def dumbbell(x, y, k, col, sd):
    s = []
    s.append(shape(rect_pts(x - 24 * k, y - 5 * k, x + 24 * k, y + 5 * k, 3), METAL, "", w=2.6, seed=sd))
    for sx in (-1, 1):
        hx = x + sx * 28 * k
        hexp = [(hx + 13 * k * math.cos(a), y + 15 * k * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1] + math.pi / 6]
        hexp = [p + (1,) for p in hexp]
        s.append(shape(hexp, col, blob([(hx, y), (hx + 14 * k, y), (hx + 14 * k, y + 16 * k), (hx, y + 16 * k)], mix(col, "#000000", .3), .8),
                       w=3.0, seed=sd + 1 + sx))
    return "".join(s)


def rack():
    """Двухъярусная стойка с гантелями у стены (за дорожкой, слева)."""
    x, y = RACK
    s = []
    w, h = 420, 230
    for sx in (0, w):
        s.append(shape(rect_pts(x + sx - 8, y - h, x + sx + 8, y), TM, "", w=3.4, seed=3200 + sx))
    for j, yy in enumerate((y - h + 30, y - 90)):
        s.append(shape([(x - 14, yy, 1), (x + w + 14, yy, 1), (x + w + 4, yy + 18, 1), (x - 4, yy + 18, 1)], TM_HI,
                       blob(rect_pts(x - 14, yy + 10, x + w + 14, yy + 18), TM_SH), w=3.4, seed=3210 + j))
        cols = ["#d9534a", "#2fb3a8", "#e8a33b", "#5b77c9"] if j == 0 else ["#5b77c9", "#e8a33b", "#2fb3a8", "#d9534a"]
        for i, c in enumerate(cols):
            kk = (0.85 + 0.1 * i) * (1.0 if j == 0 else 1.15)
            s.append(dumbbell(x + 60 + i * 100, yy - 15 * kk, kk, c, 3220 + j * 10 + i * 2))
    s.append(blob(ellipse_pts(x + w / 2, y + 4, w * .6, 12, 14), "#000000", .12, lib.blur(4)))
    return "".join(s)


def fan(t, on=1.0, x=None):
    """Напольный вентилятор справа от дорожки, дует влево (на Диму): решётка в профиль-¾, лопасти крутятся."""
    fx, fy = FAN
    fx = fx if x is None else x
    hy = fy - 560
    s = [blob(ellipse_pts(fx, fy + 6, 110, 14, 14), "#000000", .14, lib.blur(4))]
    s.append(shape(ellipse_pts(fx, fy - 6, 96, 22, 14), "#e9e9ee", blob(ellipse_pts(fx + 10, fy, 90, 14, 12), "#c4c6cf"), w=4, seed=3300))
    s.append(shape(rect_pts(fx - 9, hy + 40, fx + 9, fy - 20), METAL, blob(rect_pts(fx + 2, hy + 40, fx + 9, fy - 20), METAL_SH), w=3.4, seed=3301))
    # мотор сзади
    s.append(shape(ellipse_pts(fx + 50, hy, 46, 52, 14), "#e9e9ee", blob(ellipse_pts(fx + 64, hy + 12, 34, 40, 12), "#c4c6cf"), w=4.2, seed=3302))
    # лопасти за решёткой (эллипс — круг под углом)
    rx, ry = 64, 150
    cx = fx - 6
    bl = ""
    ang0 = t * 21 * on
    for i in range(3):
        a = ang0 + i * 2 * math.pi / 3
        pts = []
        for u in np.linspace(-0.42, 0.42, 7):
            pts.append((cx + rx * .86 * math.cos(a + u) * .35, hy + ry * .86 * math.sin(a + u)))
        bl += blob([(cx, hy)] + pts, "#8fc6e8", .9)
    if on > 0.3:
        bl += blob(ellipse_pts(cx, hy, rx * .32, ry * .82, 20), "#bfe0f4", .35)
    cage = ellipse_pts(cx, hy, rx * .38, ry, 24)
    s.append(shape(cage, "#f4f6f9", bl, w=4.4, seed=3303))
    for i in range(5):
        e = [(cx + rx * .38 * (i - 2) / 2.6 * .8, hy - ry * math.sqrt(max(0, 1 - ((i - 2) / 2.6) ** 2))),
             (cx + rx * .38 * (i - 2) / 2.6 * .8, hy + ry * math.sqrt(max(0, 1 - ((i - 2) / 2.6) ** 2)))]
        s.append(line(e, 1.6, "#9ea2ad", taper=.05, wmin=.8, seed=3310 + i, op=.85))
    s.append(blob(ellipse_pts(cx, hy, 9, 14, 10), "#9ea2ad"))
    return "".join(s)


def wind(t, on, x0=330, y0=-560, k=1.0):
    """Струйки ветра от вентилятора влево (к Диме): белые волнистые штрихи плывут и тают."""
    if on <= 0:
        return ""
    s = []
    for i in range(6):
        ph = (t * 1.6 + i * .17) % 1.0
        y = y0 + (i - 2.5) * 46 * k + 10 * math.sin(i * 2.1)
        xa = x0 - ph * 420
        L = 120 + 30 * (i % 2)
        pts = [(xa - L * j / 6, y + 9 * math.sin(j * 1.2 + t * 6 + i)) for j in range(7)]
        a = on * math.sin(math.pi * ph) * .85
        s.append(line(pts, 4.4 * k, "#ffffff", taper=.7, wmin=.1, seed=3330 + i, op=a))
    return "".join(s)


# ─────────────────────────────── беговая дорожка
CON = [(150, -488), (128, -540), (138, -556), (300, -590), (326, -556), (314, -500), (282, -478)]


def tm_back(belt_x, t=0.0, screen=0.0):
    """Всё, что за Димой: дальний поручень, стойка, пульт, мотор, лента (сдвиг ленты belt_x — слотки едут влево)."""
    x0, x1 = DECK
    s = []
    s.append(blob(ellipse_pts((x0 + x1) / 2 + 40, FLOOR_Y + 2, 420, 20, 16), "#000000", .2, lib.blur(6)))
    # дальний поручень (выше и короче — дальше от зрителя)
    s.append(line([(222, -500), (150, -470), (66, -432), (50, -404)], 15, TM_SH, taper=.05, wmin=.9, seed=3400))
    s.append(line([(66, -432), (50, -404)], 22, "#1e1f24", taper=.05, wmin=.9, seed=3401))
    # стойка
    up = [(282, -486), (322, -490), (354, 10, 1), (300, 14, 1)]
    s.append(shape(up, TM, blob([(306, -486), (322, -490), (354, 10), (328, 12)], TM_SH, .9) +
                   line([(290, -440), (316, -20)], 3, TM_HI, seed=3403, op=.8), w=4.4, seed=3402))
    # пульт: корпус и наклонная панель с экраном (только огоньки и значки, без букв)
    inner = blob([(128, -540), (300, -590), (326, -556), (314, -500), (150, -488)], TM_SH, .5)
    s.append(shape(CON, TM, inner, w=4.6, seed=3404))
    scr = [(152, -536), (290, -574), (304, -548), (166, -510)]
    sc_in = blob(scr, "#16304a")
    if screen > 0:
        for i in range(6):
            hgt = (10 + 14 * (0.5 + 0.5 * math.sin(t * 7 + i * 1.3))) * screen
            bx = 180 + i * 18
            by = -520 - (bx - 166) * .27
            sc_in += blob([(bx, by), (bx + 10, by - 2.7), (bx + 10 - .27 * 0, by - 2.7 - hgt), (bx, by - hgt)], "#5fe3a0", .9)
        hx, hy = 272, -556
        sc_in += blob([(hx, hy + 8), (hx - 9, hy - 1), (hx - 5, hy - 7), (hx, hy - 3), (hx + 5, hy - 7), (hx + 9, hy - 1)], "#ff6b6b",
                      .6 + .4 * abs(math.sin(t * 6)))
    s.append(shape(scr, "#16304a", sc_in, w=3.2, seed=3405))
    # кнопки на нижней кромке
    for i, (bx, col) in enumerate([(200, "#e8a33b"), (230, "#2fb3a8"), (262, "#d9534a")]):
        s.append(shape(ellipse_pts(bx, -497 - (bx - 150) * .1, 9, 5, 10), col, "", w=2.2, seed=3406 + i))
    # подставка-полочка под телефон на пульте
    s.append(shape([(142, -540), (176, -548), (180, -536), (146, -528)], TM_HI, "", w=3, seed=3410))
    # моторный кожух спереди
    hood = [(176, -32), (240, -46), (326, -40), (350, -10), (352, 52, 1), (176, 52, 1)]
    s.append(shape(hood, TM, blob([(260, -46), (326, -40), (350, -10), (352, 52), (300, 52)], TM_SH, .8) +
                   line([(196, -18), (320, -26)], 2.4, TM_HI, seed=3412, op=.8), w=4.6, seed=3411))
    # лента: верх виден узкой полосой, слотки едут влево
    belt = [(x0, -30, 1), (x1, -30, 1), (x1, 6, 1), (x0, 6, 1)]
    off = belt_x % 34.0
    bi = blob(rect_pts(x0 - 10, -30, x1 + 10, -18), BELT_SH, .9)
    for j in range(-2, int((x1 - x0) / 34) + 3):
        xx = x0 + j * 34 - off
        bi += line([(xx + 8, -30), (xx, 6)], 2.2, BELT_SH, taper=.05, wmin=.8, seed=3420 + (j % 9), op=.9)
    s.append(shape(belt, BELT, bi, w=3.4, seed=3419))
    # задний ролик
    s.append(shape(ellipse_pts(x0 - 6, -6, 26, 26, 14), TM, blob(ellipse_pts(x0 - 2, 0, 18, 18, 12), TM_SH), w=3.6, seed=3430))
    return "".join(s)


def tm_front(belt_x=0.0):
    """Ближний борт дорожки (перед подошвами), корпус под лентой и ножки."""
    x0, x1 = DECK
    s = []
    for i, fx in enumerate((x0 + 20, x1 - 30)):
        s.append(shape(rect_pts(fx - 18, 40, fx + 18, FLOOR_Y), TM_SH, "", w=3.4, seed=3440 + i))
        s.append(shape(rect_pts(fx - 26, FLOOR_Y - 10, fx + 26, FLOOR_Y + 2, 3), "#3a3b42", "", w=3, seed=3442 + i))
    body = [(x0 - 26, 6, 1), (x1 + 20, 6, 1), (x1 + 20, 50, 1), (x0 - 16, 50), (x0 - 30, 30)]
    s.append(shape(body, TM, blob([(x0 - 30, 34), (x1 + 20, 34), (x1 + 20, 50), (x0 - 16, 50)], TM_SH, .9), w=4.4, seed=3445))
    # борт с резиновой полосой (наступать)
    s.append(shape(rect_pts(x0 - 22, 2, x1 + 18, 22, 4), "#3a3b42", blob(rect_pts(x0 - 22, 2, x1 + 18, 9), "#55575f") +
                   "".join(line([(x0 + k * 22, 12), (x0 + k * 22 + 10, 12)], 2, "#25262b", seed=3450 + k % 9, op=.8)
                           for k in range(int((x1 - x0) / 22))), w=3.6, seed=3446))
    # торцевая заглушка сзади
    s.append(shape([(x0 - 40, -8), (x0 - 18, -10), (x0 - 14, 40), (x0 - 40, 36)], "#3a3b42", "", w=3.4, seed=3447))
    return "".join(s)


def tm_near_bar():
    """Ближний поручень: от пульта назад к Диме, на конце мягкая ручка."""
    s = []
    s.append(line([(236, -486), (160, -452), (74, -414), (58, -386)], 18, TM, taper=.05, wmin=.9, seed=3460))
    s.append(line([(232, -492), (160, -460), (80, -424)], 4, TM_HI, taper=.1, wmin=.6, seed=3461, op=.8))
    grip = [(120, -446), (64, -420), (52, -392), (64, -384), (78, -408), (128, -432)]
    s.append(shape(grip, "#1e1f24", "".join(line([(120 - k * 12, -444 + k * 5.5), (124 - k * 12, -434 + k * 5)], 1.8, "#3a3b42", seed=3463 + k)
                                               for k in range(5)), w=3.6, seed=3462))
    return "".join(s)


def ceiling_glow():
    g = lib.rad_grad([(0, "#fff6e0", .35), (1, "#fff6e0", 0)], 0, -700, 900, 900)
    return f'<rect x="-1600" y="-2200" width="3600" height="3600" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def vignette():
    g = lib.rad_grad([(0, "#20180c", 0), (.62, "#20180c", 0), (1, "#20180c", .34)], 540, 860, 1150, 1380)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def phone(cx, cy, k=1.0, rot=0.0, play=0.0, press=0.0, t=0.0, waves=0.0):
    """Чёрный телефон лицом к зрителю: на экране только значки — микрофон сверху, кружок с треугольником «играть».
    play 0→1 — нажато (кнопка светлеет, вокруг кольцо), press — кнопка вдавлена, waves — звуковые волны вокруг."""
    w, h = 64 * k, 118 * k
    o = []
    body = rect_pts(-w / 2, -h / 2, w / 2, h / 2, 12 * k)
    sc = rect_pts(-w / 2 + 6 * k, -h / 2 + 12 * k, w / 2 - 6 * k, h / 2 - 12 * k, 6 * k)
    bg = mix("#1b2a44", "#2a4c7a", play)
    inner = blob(sc, bg)
    # микрофон
    mx, my = 0, -h * .22
    inner += f'<rect x="{mx - 7 * k:.1f}" y="{my - 15 * k:.1f}" width="{14 * k:.1f}" height="{24 * k:.1f}" rx="{7 * k:.1f}" fill="#e9eef7"/>'
    inner += line([(mx - 11 * k, my), (mx - 10 * k, my + 9 * k), (mx, my + 14 * k), (mx + 10 * k, my + 9 * k), (mx + 11 * k, my)], 2.6 * k,
                  "#e9eef7", taper=.05, wmin=.9, seed=3501)
    inner += line([(mx, my + 14 * k), (mx, my + 20 * k)], 2.6 * k, "#e9eef7", taper=.05, wmin=.9, seed=3502)
    # кнопка «играть»
    bx, by = 0, h * .16
    br = 18 * k * (1 - .12 * press)
    inner += blob(ellipse_pts(bx, by, br + 4 * k * play, br + 4 * k * play, 18), "#5fe3a0", .35 * play)
    inner += blob(ellipse_pts(bx, by, br, br, 18), mix("#e9eef7", "#5fe3a0", play))
    tri = [(bx - 6 * k, by - 9 * k, 1), (bx + 10 * k, by, 1), (bx - 6 * k, by + 9 * k, 1)]
    tri = [(p[0] - bx, p[1] - by) for p in tri]
    tri = [(bx + p[0] * (1 - .12 * press), by + p[1] * (1 - .12 * press), 1) for p in tri]
    inner += blob(tri, "#1b2a44")
    # полоска прогресса (без букв)
    inner += blob(rect_pts(-w * .34, h * .34, w * .34, h * .34 + 3 * k), "#5d6b85")
    inner += blob(rect_pts(-w * .34, h * .34, -w * .34 + w * .68 * (0.05 + 0.1 * play), h * .34 + 3 * k), "#5fe3a0")
    inner += blob([(-w / 2, -h / 2), (-w / 2 + 18 * k, -h / 2), (w / 2, h / 2 - 40 * k), (w / 2, h / 2)], "#ffffff", .06)
    o.append(shape(body, "#16161a", shape(sc, bg, inner, w=1.6 * k, seed=3504, ink=False), w=3.6 * k, seed=3503))
    o.append(blob(rect_pts(-8 * k, -h / 2 + 4 * k, 8 * k, -h / 2 + 7 * k, 1.5 * k), "#3a3a44"))
    g = "".join(o)
    out = f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({rot:.2f})">{g}</g>'
    if waves > 0:
        for side in (-1, 1):
            for j in range(3):
                ph = (t * 1.3 + j / 3) % 1.0
                r = (46 + 70 * ph) * k
                a = waves * math.sin(math.pi * ph)
                pts = [(cx + side * (w * .55 + r * .5 * math.cos(q)), cy + h * .05 + r * math.sin(q)) for q in np.linspace(-.7, .7, 7)]
                out += line(pts, 4.6 * k, "#2fb3a8", taper=.5, wmin=.2, seed=3520 + j + side, op=a)
    return out


def ear_waves(x, y, t, k=1.0, amt=1.0):
    """Звуковые дуги у наушника (слева от головы — у ближнего уха)."""
    o = ""
    for j in range(3):
        ph = (t * 1.2 + j / 3) % 1.0
        r = (30 + 50 * ph) * k
        a = amt * math.sin(math.pi * ph) * .9
        pts = [(x - r * math.cos(q), y + r * math.sin(q)) for q in np.linspace(-.8, .8, 7)]
        o += line(pts, 4.2 * k, "#2fb3a8", taper=.5, wmin=.2, seed=3540 + j, op=a)
    return o


def notes(x, y, t, k=1.0, amt=1.0):
    """Нотки уплывают вверх-назад от наушника."""
    o = ""
    for j in range(3):
        ph = (t * .7 + j / 3) % 1.0
        nx, ny = x - 60 * ph * k - 20 * j * k, y - 120 * ph * k
        a = amt * math.sin(math.pi * ph)
        if a <= 0.02:
            continue
        g = blob(ellipse_pts(nx, ny, 9 * k, 7 * k, 10, rot=-20), "#2fb3a8")
        g += line([(nx + 8 * k, ny - 2 * k), (nx + 8 * k, ny - 30 * k), (nx + 18 * k, ny - 24 * k)], 3.4 * k, "#2fb3a8", taper=.1, wmin=.8,
                  seed=3550 + j)
        o += f'<g opacity="{a:.3f}">{g}</g>'
    return o
