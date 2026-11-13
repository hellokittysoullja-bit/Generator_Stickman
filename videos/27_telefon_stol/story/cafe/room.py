"""Уютное кафе вечером (сцена cafe рилса 27): деревянные панели, тёплая штукатурка, большое окно на вечернюю улицу,
гирлянда, лампа над столиком, полка с банками и растениями, бра, круглый деревянный столик, стулья, лавка у стены
(на ней сидит кот и лежит рюкзак Димы), пол из досок.

Мир — тот же, что у героев: столик — центр (540, 1150), пол перед столом y≈1470, стена с полом — y 1330.
Слои для параллакса: street (за окном, 0.72), wall (1.0 — стена, мебель, герои), front (1.25 — передний план).
Каждая функция возвращает SVG в мировых координатах; камера накладывается снаружи (scene.py).
Манера — как у 23–26: чистый контур живой линией (ink.py), плоский цвет с одной тенью, свет слоями.
"""
import math

import numpy as np

import lib
from lib import INK, blob, ellipse_pts, line, rect_pts, shape

WOOD, WOOD_SH, WOOD_HI, WOOD_DK = "#a8693f", "#7f4b2b", "#c88a58", "#5e3720"
PANEL, PANEL_SH, PANEL_HI = "#8a5534", "#6a3e24", "#a56b43"
PLASTER, PLASTER_SH = "#efcf9f", "#d9b07f"
FLOOR, FLOOR_SH, FLOOR_LN = "#9a6440", "#7a4a2e", "#5f3820"
TABLE = (540.0, 1150.0, 300.0, 62.0)          # центр, полуоси столешницы
FLOOR_Y = 1330.0
WIN = (70.0, 300.0, 470.0, 905.0)               # окно: x0, y0, x1, y1


def rsd(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


# ═════════════════════════ за окном: вечерняя улица ═════════════════════════
def street(t):
    o = []
    g = lib.lin_grad([(0, "#2b3566", 1), (.45, "#5b4f8a", 1), (.75, "#c9799a", 1), (1, "#f0a77e", 1)], 0, 120, 0, 900, units="userSpaceOnUse")
    o.append(f'<rect x="-300" y="0" width="1100" height="1200" fill="url(#{g})"/>')
    o.append(f'<circle cx="360" cy="330" r="7" fill="#fff6dc" opacity=".9"/>')
    # дома через улицу
    houses = [(-120, 470, 150, "#4a3f6e"), (40, 520, 130, "#574a7c"), (170, 440, 170, "#463c68"), (350, 500, 150, "#54477a"),
              (500, 470, 160, "#4b406f")]
    for i, (x, y, w, col) in enumerate(houses):
        o.append(shape([(x, y, 1), (x + w, y, 1), (x + w, 1100, 1), (x, 1100, 1)], col,
                       blob([(x + w * .7, y), (x + w, y), (x + w, 1100), (x + w * .7, 1100)], "#3b3259", .8), w=3.2, seed=900 + i))
        o.append(shape([(x - 6, y - 14, 1), (x + w + 6, y - 14, 1), (x + w + 6, y + 4, 1), (x - 6, y + 4, 1)], "#3a3058", w=2.6, seed=910 + i))
        rs = rsd(31, i)
        for r in range(6):
            for c in range(int(w // 44)):
                wx, wy = x + 16 + c * 44, y + 26 + r * 66
                lit = rs.uniform() < .55
                tw = 1.0
                if lit and rs.uniform() < .15:
                    tw = .75 + .25 * math.sin(t * 3 + i * 7 + r * 3 + c)
                col_w = lib.mix("#3a3058", "#ffc56a", tw) if lit else "#2f2850"
                o.append(shape([(wx, wy, 1), (wx + 24, wy, 1), (wx + 24, wy + 36, 1), (wx, wy + 36, 1)], col_w,
                               blob([(wx, wy + 22), (wx + 24, wy + 18), (wx + 24, wy + 36), (wx, wy + 36)], "#f59d4a", .6) if lit else "",
                               w=2.0, seed=920 + i * 50 + r * 7 + c))
    # дерево у тротуара (силуэт) и фонарь
    for k, (x, y, r) in enumerate([(240, 690, 95), (170, 740, 70), (310, 745, 75)]):
        o.append(blob(ellipse_pts(x, y, r, r * .8, 14, jitter=.08, seed=40 + k), "#2c2a4c"))
    o.append(blob([(232, 760), (248, 760), (252, 1000), (228, 1000)], "#262343"))
    gl = lib.rad_grad([(0, "#ffe2a0", .9), (.3, "#ffbf6a", .35), (1, "#ff9f4a", 0)], 420, 640, 150)
    o.append(f'<circle cx="420" cy="640" r="150" fill="url(#{gl})"/>')
    o.append(blob([(414, 650), (426, 650), (428, 1000), (412, 1000)], "#2a2645"))
    o.append(shape([(398, 626), (442, 626), (434, 652), (406, 652)], "#3a3256", blob(ellipse_pts(420, 646, 12, 6, 8), "#fff0c4"), w=2.4, seed=960))
    # тротуар, проезжающая машина (огни)
    o.append(blob([(-300, 860), (800, 860), (800, 1200), (-300, 1200)], "#3d3560"))
    o.append(blob([(-300, 860), (800, 860), (800, 876), (-300, 876)], "#5d5288"))
    cx = -200 + ((t * 160) % 1000)
    o.append(blob([(cx, 840), (cx + 150, 840), (cx + 170, 870), (cx - 10, 870)], "#2a2442"))
    o.append(f'<circle cx="{cx + 160:.1f}" cy="858" r="7" fill="#fff4cc"/><circle cx="{cx - 2:.1f}" cy="858" r="5" fill="#ff5a4a"/>')
    return "".join(o)


def window_frame(t):
    x0, y0, x1, y1 = WIN
    o = []
    fw = 26
    outer = [(x0 - fw, y0 - fw, 1), (x1 + fw, y0 - fw, 1), (x1 + fw, y1 + fw, 1), (x0 - fw, y1 + fw, 1)]
    hole = f"M{x0} {y0}H{x1}V{y1}H{x0}Z"
    o.append(f'<path d="{lib.fill_d(outer)}{hole}" fill="{WOOD}" fill-rule="evenodd"/>')
    o.append(f'<path d="{lib.ink_closed(outer, 4.6 * lib.INK_K[0], seed=980)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed([(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)], 3.8 * lib.INK_K[0], seed=981)}" fill="{INK}"/>')
    o.append(blob([(x1, y0 - fw), (x1 + fw, y0 - fw), (x1 + fw, y1 + fw), (x1, y1)], WOOD_SH, .9))
    o.append(blob([(x0 - fw, y1), (x1 + fw, y1), (x1 + fw, y1 + fw), (x0 - fw, y1 + fw)], WOOD_SH, .7))
    mx, my = (x0 + x1) / 2, y0 + (y1 - y0) * .42
    for pts, sd in (([(mx - 8, y0), (mx + 8, y0), (mx + 8, y1), (mx - 8, y1)], 982), ([(x0, my - 8), (x1, my - 8), (x1, my + 8), (x0, my + 8)], 983)):
        o.append(shape([p + (1,) for p in pts], WOOD, blob([pts[1], pts[2], (pts[2][0] - 6, pts[2][1]), (pts[1][0] - 6, pts[1][1])], WOOD_SH, .8),
                       w=3.2, seed=sd))
    # блики стекла
    for k, (a, b) in enumerate([((x0 + 30, y0 + 120), (x0 + 120, y0 + 20)), ((x0 + 50, y0 + 180), (x0 + 170, y0 + 50)),
                                ((mx + 40, y1 - 60), (mx + 150, y1 - 190))]):
        o.append(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="#ffffff" stroke-opacity=".12" stroke-width="{14 - k * 3}" stroke-linecap="round"/>')
    # подоконник
    sill = [(x0 - 46, y1 + 14, 1), (x1 + 46, y1 + 14, 1), (x1 + 40, y1 + 44, 1), (x0 - 40, y1 + 44, 1)]
    o.append(shape(sill, WOOD_HI, blob([(x0 - 46, y1 + 32), (x1 + 46, y1 + 32), (x1 + 46, y1 + 46), (x0 - 46, y1 + 46)], WOOD_SH, .9), w=4.2,
                   seed=985))
    # на подоконнике: свеча в банке и суккулент
    o.append(candle(x0 + 70, y1 + 14, t))
    o.append(pot(x1 - 80, y1 + 14, 1.0, 990))
    return "".join(o)


def candle(x, y, t):
    o = []
    gl = lib.rad_grad([(0, "#ffd98a", .55), (1, "#ffb050", 0)], x, y - 60, 90)
    o.append(f'<circle cx="{x}" cy="{y - 60}" r="90" fill="url(#{gl})"/>')
    jar = [(x - 30, y - 70), (x + 30, y - 70), (x + 32, y, 1), (x - 32, y, 1)]
    o.append(shape(jar, "#f3c27a", blob([(x - 26, y - 34), (x + 28, y - 34), (x + 30, y), (x - 30, y)], "#fff1d2", .9) +
                   blob([(x + 14, y - 70), (x + 32, y - 70), (x + 32, y), (x + 18, y)], "#d9933f", .6), w=3.4, seed=1001))
    fl = 3 * math.sin(t * 11) + 2 * math.sin(t * 17)
    o.append(blob([(x - 6, y - 38), (x + fl * .3, y - 66 + fl), (x + 6, y - 38), (x, y - 32)], "#ffcf5a"))
    o.append(blob([(x - 3, y - 39), (x, y - 54 + fl * .5), (x + 3, y - 39)], "#fff6d8"))
    return "".join(o)


def pot(x, y, k, seed, leaves=7, col="#c96b4a"):
    o = []
    rs = np.random.RandomState(seed)
    for i in range(leaves):
        a = math.radians(-90 + (i - leaves / 2 + .5) * 24 + rs.uniform(-6, 6))
        L = (54 + rs.uniform(-8, 14)) * k
        bx, by = x, y - 46 * k
        tip = (bx + math.cos(a) * L, by + math.sin(a) * L)
        nrm = (-math.sin(a), math.cos(a))
        mid = (bx + math.cos(a) * L * .5, by + math.sin(a) * L * .5)
        lf = [(bx, by), (mid[0] + nrm[0] * 12 * k, mid[1] + nrm[1] * 12 * k), (tip[0], tip[1], 1), (mid[0] - nrm[0] * 12 * k, mid[1] - nrm[1] * 12 * k)]
        o.append(shape(lf, "#6aa457" if i % 2 else "#5b944c", line([(bx, by), tip], 1.6, "#3f6f36", seed=seed + 30 + i, op=.8), w=3.0,
                       seed=seed + i))
    pt = [(x - 34 * k, y - 50 * k, 1), (x + 34 * k, y - 50 * k, 1), (x + 26 * k, y, 1), (x - 26 * k, y, 1)]
    o.append(shape(pt, col, blob([(x + 10 * k, y - 50 * k), (x + 34 * k, y - 50 * k), (x + 26 * k, y), (x + 6 * k, y)], lib.mul(col, (.78, .75, .75)), .9) +
                   blob([(x - 36 * k, y - 50 * k), (x + 36 * k, y - 50 * k), (x + 36 * k, y - 40 * k), (x - 36 * k, y - 40 * k)], lib.mul(col, (.85, .8, .8))),
                   w=3.4, seed=seed + 20))
    return "".join(o)


# ═════════════════════════ стена ═════════════════════════
def wall(t):
    o = []
    g = lib.lin_grad([(0, "#c99a6c", 1), (.35, PLASTER, 1), (1, "#e6bd88", 1)], 0, 0, 0, 1000, units="userSpaceOnUse")
    o.append(f'<rect x="-400" y="-400" width="1900" height="1400" fill="url(#{g})"/>')
    # тёплое пятно от лампы и бра на стене
    for (x, y, r, a) in [(540, 560, 520, .55), (980, 560, 260, .5)]:
        gl = lib.rad_grad([(0, "#fff0c8", a), (.5, "#ffd89a", a * .45), (1, "#ffcf8a", 0)], x, y, r)
        o.append(f'<rect x="{x - r}" y="{y - r}" width="{2 * r}" height="{2 * r}" fill="url(#{gl})"/>')
    # фактура штукатурки
    rs = rsd(7)
    for i in range(60):
        x, y = rs.uniform(-300, 1400), rs.uniform(-200, 940)
        o.append(line([(x, y), (x + rs.uniform(10, 30), y + rs.uniform(-4, 4))], 1.6, PLASTER_SH, seed=1100 + i, op=.5))
    # панели снизу
    o.append(shape([(-400, 940, 1), (1500, 940, 1), (1500, FLOOR_Y + 40, 1), (-400, FLOOR_Y + 40, 1)], PANEL,
                   blob([(-400, 940), (1500, 940), (1500, 966), (-400, 966)], PANEL_SH, .9), w=4, seed=1200))
    for k in range(-4, 13):
        x = k * 150 + 20
        o.append(shape([(x + 14, 990, 1), (x + 136, 990, 1), (x + 136, FLOOR_Y - 20, 1), (x + 14, FLOOR_Y - 20, 1)], PANEL_HI,
                       blob([(x + 14, 990), (x + 136, 990), (x + 136, 1006), (x + 14, 1006)], PANEL_SH, .8) +
                       blob([(x + 120, 990), (x + 136, 990), (x + 136, FLOOR_Y), (x + 120, FLOOR_Y)], PANEL_SH, .7), w=2.8, seed=1210 + k))
    o.append(shape([(-400, 924, 1), (1500, 924, 1), (1500, 950, 1), (-400, 950, 1)], WOOD_HI,
                   blob([(-400, 940), (1500, 940), (1500, 950), (-400, 950)], WOOD_SH, .9), w=3.6, seed=1201))
    o.append(shape([(-400, FLOOR_Y - 22, 1), (1500, FLOOR_Y - 22, 1), (1500, FLOOR_Y, 1), (-400, FLOOR_Y, 1)], WOOD_DK, w=3.4, seed=1202))
    # картина: чашка с паром и сердечком (без букв)
    px0, py0, px1, py1 = 640, 360, 840, 600
    o.append(shape([(px0, py0, 1), (px1, py0, 1), (px1, py1, 1), (px0, py1, 1)], WOOD_DK, w=4, seed=1300))
    o.append(shape([(px0 + 16, py0 + 16, 1), (px1 - 16, py0 + 16, 1), (px1 - 16, py1 - 16, 1), (px0 + 16, py1 - 16, 1)], "#f2dfbd",
                   blob([(px0 + 16, py1 - 80), (px1 - 16, py1 - 70), (px1 - 16, py1 - 16), (px0 + 16, py1 - 16)], "#e6a76a", .9), w=3, seed=1301))
    cx_, cy_ = (px0 + px1) / 2, py1 - 92
    o.append(shape([(cx_ - 48, cy_ - 44), (cx_ + 48, cy_ - 44), (cx_ + 40, cy_ + 20), (cx_ - 40, cy_ + 20)], "#3f7a72",
                   blob([(cx_ + 14, cy_ - 44), (cx_ + 48, cy_ - 44), (cx_ + 40, cy_ + 20), (cx_ + 18, cy_ + 20)], "#2f5d57", .9), w=3, seed=1302))
    o.append(shape(ellipse_pts(cx_ + 56, cy_ - 16, 16, 18, 10), "none", w=3, seed=1303))
    for k in range(2):
        wv = 6 * math.sin(t * 2 + k)
        o.append(line([(cx_ - 14 + k * 26, cy_ - 54), (cx_ - 22 + k * 26 + wv, cy_ - 84), (cx_ - 10 + k * 26, cy_ - 116)], 3, "#c7895a",
                      seed=1304 + k))
    o.append(blob([(cx_ - 8, cy_ - 150), (cx_, cy_ - 140), (cx_ + 8, cy_ - 150), (cx_, cy_ - 128)], "#d8483c"))
    o.append(shape([(cx_ - 14, cy_ - 152), (cx_ - 2, cy_ - 160), (cx_, cy_ - 150), (cx_ + 2, cy_ - 160), (cx_ + 14, cy_ - 152), (cx_, cy_ - 132, 1)],
                   "#d8483c", w=2.6, seed=1305))
    # полка с банками, кружками и свисающим растением
    o.append(shelf(t))
    # бра справа
    o.append(sconce(980, 560))
    return "".join(o)


def shelf(t):
    o = []
    y = 730
    o.append(shape([(590, y, 1), (1120, y, 1), (1120, y + 22, 1), (590, y + 22, 1)], WOOD_HI, blob([(590, y + 12), (1120, y + 12), (1120, y + 22),
                                                                                               (590, y + 22)], WOOD_SH, .9), w=3.6, seed=1400))
    for k, x in enumerate((640, 1060)):
        o.append(shape([(x - 8, y + 22, 1), (x + 8, y + 22, 1), (x + 8, y + 60, 1), (x - 30, y + 22, 1)], WOOD_DK, w=3, seed=1401 + k))
    # банки с зёрнами
    for k, (x, h, col) in enumerate([(660, 96, "#6b4a2e"), (730, 76, "#8a5a33"), (796, 110, "#5a3a24")]):
        jar = [(x - 30, y - h, 1), (x + 30, y - h, 1), (x + 30, y, 1), (x - 30, y, 1)]
        inner = blob([(x - 30, y - h * .6), (x + 30, y - h * .62), (x + 30, y), (x - 30, y)], col)
        rs = rsd(70, k)
        for j in range(14):
            bx, by = x + rs.uniform(-22, 22), y - rs.uniform(6, h * .55)
            inner += blob(ellipse_pts(bx, by, 5, 3.5, 6, rot=rs.uniform(0, 180)), "#3b2416", .8)
        inner += blob([(x + 14, y - h), (x + 30, y - h), (x + 30, y), (x + 18, y)], "#ffffff", .25)
        o.append(shape(jar, "#e9e1d0", inner, w=3.2, seed=1410 + k))
        o.append(shape([(x - 34, y - h - 18, 1), (x + 34, y - h - 18, 1), (x + 34, y - h, 1), (x - 34, y - h, 1)], "#b8834f", w=3, seed=1420 + k))
    # стопка кружек
    for k in range(3):
        cy = y - 30 - k * 34
        o.append(shape([(880, cy - 30), (944, cy - 30), (938, cy + 2, 1), (886, cy + 2, 1)], ["#e85f4f", "#f2e6cf", "#4f8ea0"][k],
                       blob([(924, cy - 30), (944, cy - 30), (938, cy + 2), (928, cy + 2)], "#000000", .15), w=3, seed=1430 + k))
    # горшок со свисающими плетями
    x = 1010
    o.append(pot(x, y, .9, 1450, leaves=3, col="#e3d3b2"))
    for v in range(3):
        sway = 6 * math.sin(t * 1.3 + v)
        pts = [(x - 20 + v * 20, y - 6), (x - 26 + v * 22 + sway * .3, y + 60), (x - 18 + v * 18 + sway * .7, y + 130 + v * 30),
               (x - 30 + v * 20 + sway, y + 190 + v * 40)]
        o.append(line(pts, 3.2, "#3f6f36", seed=1460 + v, taper=.3, wmin=.4))
        for j, u in enumerate(np.linspace(.15, 1, 5)):
            i = min(int(u * 3), 2)
            a, b = np.array(pts[i]), np.array(pts[min(i + 1, 3)])
            p = a + (b - a) * (u * 3 - i)
            s_ = 1 if j % 2 else -1
            lf = [(p[0], p[1]), (p[0] + s_ * 14, p[1] - 4), (p[0] + s_ * 24, p[1] + 6, 1), (p[0] + s_ * 10, p[1] + 12)]
            o.append(shape(lf, "#6aa457" if j % 2 else "#5b944c", "", w=2.4, seed=1470 + v * 10 + j))
    return "".join(o)


def sconce(x, y):
    o = []
    o.append(shape([(x - 14, y - 70, 1), (x + 14, y - 70, 1), (x + 14, y - 30, 1), (x - 14, y - 30, 1)], "#b08a4a", w=3, seed=1500))
    sh = [(x - 50, y - 30), (x + 50, y - 30), (x + 34, y + 40, 1), (x - 34, y + 40, 1)]
    o.append(shape(sh, "#f6e3b5", blob([(x - 50, y - 30), (x + 50, y - 30), (x + 46, y - 14), (x - 46, y - 14)], "#ffffff", .5), w=3.4, seed=1501))
    o.append(blob(ellipse_pts(x, y + 42, 30, 8, 10), "#fff4d2"))
    return "".join(o)


# ═════════════════════════ лампа над столом, гирлянда ═════════════════════════
def pendant(t, x=540.0, y=560.0):
    sw = 1.2 * math.sin(t * 1.1)
    o = []
    gl = lib.rad_grad([(0, "#fff3d0", .55), (.4, "#ffd890", .22), (1, "#ffcc80", 0)], x, y + 200, 420, 300)
    o.append(f'<ellipse cx="{x}" cy="{y + 260}" rx="420" ry="360" fill="url(#{gl})"/>')
    g = []
    g.append(line([(x, -300), (x, y - 80)], 3.4, "#2a2228", seed=1600, taper=.05, wmin=.9))
    g.append(shape([(x - 14, y - 90, 1), (x + 14, y - 90, 1), (x + 12, y - 60, 1), (x - 12, y - 60, 1)], "#b08a4a", w=3, seed=1601))
    sh = [(x - 26, y - 64), (x + 26, y - 64), (x + 70, y - 10), (x + 96, y + 20, 1), (x - 96, y + 20, 1), (x - 70, y - 10)]
    g.append(shape(sh, "#2f5d57", blob([(x + 10, y - 64), (x + 26, y - 64), (x + 96, y + 20), (x + 40, y + 20)], "#244944", .9) +
                   line([(x - 60, y - 6), (x - 20, y - 50)], 2.4, "#4b8a80", seed=1603, op=.8), w=4, seed=1602))
    g.append(blob(ellipse_pts(x, y + 20, 96, 14, 14), "#ffe9b0"))
    g.append(blob(ellipse_pts(x, y + 24, 30, 16, 10), "#fffbe8"))
    o.append(f'<g transform="rotate({sw:.3f} {x} -300)">{"".join(g)}</g>')
    return "".join(o)


GARLAND = [((-200, 150), (360, 300), (700, 180)), ((700, 180), (980, 300), (1400, 140))]


def _garland_pts():
    pts = []
    for a, m, b in GARLAND:
        for u in np.linspace(0, 1, 40, endpoint=False):
            x = (1 - u) ** 2 * a[0] + 2 * (1 - u) * u * m[0] + u * u * b[0]
            y = (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * m[1] + u * u * b[1]
            pts.append((x, y))
    return pts


def garland(t, dy=0.0):
    pts = [(x, y + dy + 3 * math.sin(t * 1.2 + x * .01)) for x, y in _garland_pts()]
    o = [line(pts, 3.0, "#2a2228", seed=1700, taper=.05, wmin=.9)]
    cols = ["#ffd36a", "#ffb04a", "#fff0b0", "#ff8a5a"]
    for i in range(2, len(pts) - 1, 4):
        x, y = pts[i]
        tw = .78 + .22 * math.sin(t * (2.2 + (i % 5) * .4) + i)
        c = cols[(i // 4) % 4]
        gl = lib.rad_grad([(0, c, .6 * tw), (1, c, 0)], x, y + 18, 46)
        o.append(f'<circle cx="{x:.1f}" cy="{y + 18:.1f}" r="46" fill="url(#{gl})"/>')
        o.append(blob([(x - 4, y), (x + 4, y), (x + 4, y + 8), (x - 4, y + 8)], "#3a3036"))
        o.append(shape(ellipse_pts(x, y + 19, 9, 12, 10), lib.mix("#c98a40", c, tw), blob(ellipse_pts(x - 2, y + 15, 3, 5, 6), "#fffbe8"), w=2.2,
                       seed=1710 + i))
    return "".join(o)


# ═════════════════════════ мебель ═════════════════════════
def floor():
    o = []
    o.append(blob([(-500, FLOOR_Y), (1600, FLOOR_Y), (1600, 2600), (-500, 2600)], FLOOR))
    vx, vy = 540, 600
    for k in range(-14, 15):
        xb = 540 + k * 130
        x0 = vx + (xb - vx) * (FLOOR_Y - vy) / (2600 - vy)
        o.append(line([(x0, FLOOR_Y), (xb, 2600)], 2.4, FLOOR_LN, seed=1800 + k, op=.7, taper=.1, wmin=.7))
    for k, y in enumerate((1380, 1470, 1590, 1740, 1930)):
        o.append(line([(-500, y), (1600, y)], 1.6, FLOOR_SH, seed=1830 + k, op=.45))
    gl = lib.rad_grad([(0, "#ffd99a", .35), (1, "#ffcf8a", 0)], 540, 1420, 520, 200)
    o.append(f'<ellipse cx="540" cy="1420" rx="520" ry="200" fill="url(#{gl})"/>')
    # ковёр под столом
    rug = [(170, 1400), (910, 1400), (1010, 1560, 1), (70, 1560, 1)]
    o.append(shape(rug, "#b4473c", blob([(150, 1500), (950, 1500), (1010, 1560), (70, 1560)], "#8f3530", .8) +
                   line([(210, 1420), (870, 1420), (950, 1540), (130, 1540), (210, 1420)], 3, "#e0b46a", seed=1851, op=.9), w=4, seed=1850))
    return "".join(o)


def chair(x, seat_y, facing, seed, tone=1.0):
    """Деревянный стул в профиль: спинка за спиной героя (facing +1 — сидит лицом вправо)."""
    s = facing
    col = lib.mul(WOOD, (tone, tone, tone))
    o = []
    bx = x - s * 120
    back = [(bx - 18, seat_y + 10, 1), (bx - 24, seat_y - 360), (bx - 8, seat_y - 390), (bx + 14, seat_y - 380), (bx + 18, seat_y + 10, 1)]
    o.append(shape(back, col, blob([(bx + 4 * s, seat_y - 380), (bx + 18, seat_y - 380), (bx + 18, seat_y), (bx + 4 * s, seat_y)], WOOD_SH, .8),
                   w=4.2, seed=seed))
    for k, yy in enumerate((seat_y - 300, seat_y - 210)):
        rail = [(bx - 14, yy - 14, 1), (bx + s * 60 + 10, yy - 12, 1), (bx + s * 60 + 10, yy + 12, 1), (bx - 14, yy + 14, 1)]
        if s < 0:
            rail = [(bx + 14, yy - 14, 1), (bx - 70, yy - 12, 1), (bx - 70, yy + 12, 1), (bx + 14, yy + 14, 1)]
        o.append(shape(rail, col, "", w=3.4, seed=seed + 1 + k))
    seat = [(x - 150, seat_y - 4, 1), (x + 130, seat_y - 4, 1), (x + 140, seat_y + 26, 1), (x - 150, seat_y + 26, 1)]
    if s < 0:
        seat = [(x - 130, seat_y - 4, 1), (x + 150, seat_y - 4, 1), (x + 150, seat_y + 26, 1), (x - 140, seat_y + 26, 1)]
    o.append(shape(seat, WOOD_HI, blob([(x - 160, seat_y + 12), (x + 160, seat_y + 12), (x + 160, seat_y + 30), (x - 160, seat_y + 30)], WOOD_SH, .9),
                   w=4, seed=seed + 4))
    for k, lx in enumerate((x - 130, x + 110) if s > 0 else (x - 110, x + 130)):
        leg = [(lx - 10, seat_y + 24, 1), (lx + 10, seat_y + 24, 1), (lx + 8 + (lx - x) * .06, 1478, 1), (lx - 8 + (lx - x) * .06, 1478, 1)]
        o.append(shape(leg, col, blob([(lx + 2, seat_y + 24), (lx + 10, seat_y + 24), (lx + 8, 1478), (lx + 2, 1478)], WOOD_SH, .8), w=3.4,
                       seed=seed + 6 + k))
    return "".join(o)


def bench(t):
    """Лавка у стены за столом: спинка с подушкой; сиденье за столешницей."""
    o = []
    x0, x1, y = 330, 790, 1110
    o.append(shape([(x0, y - 150, 1), (x1, y - 150, 1), (x1, y + 40, 1), (x0, y + 40, 1)], WOOD,
                   blob([(x0, y - 150), (x1, y - 150), (x1, y - 132), (x0, y - 132)], WOOD_HI, .9) +
                   "".join(line([(x0 + 10, y - 150 + k * 46), (x1 - 10, y - 150 + k * 46)], 2, WOOD_SH, seed=1900 + k, op=.8) for k in range(1, 4)),
                   w=4.2, seed=1901))
    cush = [(x0 + 20, y - 128), (x1 - 20, y - 128), (x1 - 10, y - 30), (x0 + 10, y - 30)]
    o.append(shape(cush, "#c0704e", blob([(x0 + 20, y - 70), (x1 - 20, y - 70), (x1 - 10, y - 30), (x0 + 10, y - 30)], "#9c5238", .9) +
                   line([((x0 + x1) / 2, y - 124), ((x0 + x1) / 2, y - 34)], 2.2, "#7e4029", seed=1903, op=.8), w=3.8, seed=1902))
    seat = [(x0 - 20, y - 30, 1), (x1 + 20, y - 30, 1), (x1 + 20, y, 1), (x0 - 20, y, 1)]
    o.append(shape(seat, WOOD_HI, blob([(x0 - 20, y - 14), (x1 + 20, y - 14), (x1 + 20, y), (x0 - 20, y)], WOOD_SH, .9), w=4, seed=1904))
    return "".join(o)


def backpack(x, y, k=1.0, open_=0.0, zip_u=1.0, flap=0.0):
    """Рюкзак (тёмно-оливковый) стоит на лавке: x, y — низ центра. open_ — горловина раскрыта (0..1),
    zip_u — доля застёгнутой молнии (1 — застёгнут)."""
    def T(p):
        return (x + p[0] * k, y + p[1] * k) + ((1,) if len(p) > 2 else ())
    o = []
    body = [(-70, 0, 1), (-78, -80), (-70, -150), (-40, -178), (40, -178), (70, -150), (78, -80), (70, 0, 1)]
    o.append(shape([T(p) for p in body], "#5f6b45", blob([T(p) for p in [(30, -178), (80, -150), (80, 0), (36, 0)]], "#4a5436", .9) +
                   line([T((-50, -150)), T((-56, -60))], 2.2, "#3e472d", seed=1951, op=.8), w=4.4, seed=1950))
    # передний карман
    pk = [(-52, -10, 1), (-56, -70), (56, -70), (52, -10, 1)]
    o.append(shape([T(p) for p in pk], "#6c7a4f", blob([T(p) for p in [(20, -70), (56, -70), (52, -10), (24, -10)]], "#56623e", .9) +
                   line([T((-50, -60)), T((50, -60))], 2.4, "#c9b98a", seed=1953), w=3.6, seed=1952))
    # молния по верху: дуга, бегунок
    arc = [T((-62, -140)), T((-36, -172)), T((0, -180)), T((36, -172)), T((62, -140))]
    if open_ > 0.02:
        gap = 30 * open_
        mouth = [T((-56, -146)), T((-30, -172 - gap * .3)), T((0, -180 - gap * .4)), T((30, -172 - gap * .3)), T((56, -146)), T((30, -160 + gap * .2)),
                 T((0, -164 + gap * .4)), T((-30, -160 + gap * .2))]
        o.append(shape(mouth, "#20221a", "", w=3.4, seed=1955))
    o.append(line(arc, 3.0, "#c9b98a", seed=1956, op=.9, taper=.1, wmin=.8))
    # бегунок молнии: идёт по дуге от правого края к левому по мере застёгивания
    u = 1 - zip_u
    i = u * 4
    j = min(int(i), 3)
    a, b = np.array(arc[j][:2]), np.array(arc[j + 1][:2])
    pz = a + (b - a) * (i - j)
    o.append(shape(ellipse_pts(pz[0], pz[1], 8 * k, 6 * k, 8), "#d8d0b4", w=2.4, seed=1957))
    o.append(shape([(pz[0] - 4 * k, pz[1] + 4 * k), (pz[0] + 4 * k, pz[1] + 4 * k), (pz[0] + 3 * k, pz[1] + 24 * k, 1), (pz[0] - 3 * k, pz[1] + 24 * k, 1)],
                   "#d8d0b4", w=2.2, seed=1958))
    # ручка сверху
    o.append(line([T((-24, -178)), T((0, -206)), T((24, -178))], 6, "#3e472d", seed=1959, taper=.1, wmin=.8))
    return "".join(o)


def table_top(cx=540.0, cy=1150.0, rx=300.0, ry=62.0):
    o = []
    th = 26
    edge = [(cx - rx, cy), (cx - rx * .7, cy + ry * .72), (cx, cy + ry), (cx + rx * .7, cy + ry * .72), (cx + rx, cy), (cx + rx, cy + th),
            (cx + rx * .7, cy + ry * .72 + th), (cx, cy + ry + th), (cx - rx * .7, cy + ry * .72 + th), (cx - rx, cy + th)]
    o.append(shape(edge, WOOD_SH, blob([(cx + rx * .3, cy + ry), (cx + rx, cy), (cx + rx, cy + th + 10), (cx + rx * .3, cy + ry + th + 10)], WOOD_DK, .7),
                   w=4.4, seed=2000))
    top = ellipse_pts(cx, cy, rx, ry, 28)
    inner = blob(ellipse_pts(cx - rx * .25, cy - ry * .3, rx * .55, ry * .4, 16), WOOD_HI, .7)
    for k, (dy, a, b) in enumerate([(-30, -.7, .4), (-6, -.85, .75), (20, -.6, .9), (40, -.3, .5)]):
        inner += line([(cx + rx * a, cy + dy), (cx + rx * (a + b) / 2, cy + dy + 4), (cx + rx * b, cy + dy - 2)], 1.8, WOOD_SH, seed=2010 + k, op=.6)
    inner += blob(ellipse_pts(cx + rx * .35, cy + ry * .3, rx * .5, ry * .45, 14), WOOD_SH, .35)
    o.append(shape(top, WOOD, inner, w=4.6, seed=2001))
    return "".join(o)


def table_leg(cx=540.0, cy=1150.0):
    o = []
    col = [(cx - 26, cy + 60, 1), (cx + 26, cy + 60, 1), (cx + 22, 1440, 1), (cx - 22, 1440, 1)]
    o.append(shape(col, WOOD_DK, blob([(cx + 4, cy + 60), (cx + 26, cy + 60), (cx + 22, 1440), (cx + 4, 1440)], "#45281a", .8), w=4, seed=2050))
    foot = ellipse_pts(cx, 1460, 120, 26, 16)
    o.append(shape(foot, WOOD_DK, blob(ellipse_pts(cx + 20, 1468, 110, 18, 12), "#45281a", .8), w=4, seed=2051))
    return "".join(o)


def cup(x, y, k=1.0, col="#f3ede2", band_col="#3f7a72", latte=True, steam_t=None, handle=1, heart=True):
    """Чашка капучино на блюдце: x, y — центр дна блюдца на столе (мир)."""
    def T(p):
        return (x + p[0] * k, y + p[1] * k) + ((1,) if len(p) > 2 else ())
    o = []
    sau = ellipse_pts(x, y, 66 * k, 15 * k, 16)
    o.append(shape(sau, col, blob(ellipse_pts(x, y + 4 * k, 60 * k, 9 * k, 12), "#d6cfc2", .9), w=3.4, seed=2100))
    o.append(blob(ellipse_pts(x + 6 * k, y + 2 * k, 50 * k, 10 * k, 12), "#000000", .08))
    # ручка
    hx = 44 * handle
    hd = [T((hx - 4 * handle, -64)), T((hx + 22 * handle, -66)), T((hx + 28 * handle, -46)), T((hx + 14 * handle, -26)), T((hx - 6 * handle, -24))]
    o.append(line(hd, 8.5, INK, seed=2101, taper=.1, wmin=.8))
    o.append(line(hd, 4.5, col, seed=2102, taper=.1, wmin=.8))
    body = [T((-46, -82)), T((46, -82)), T((40, -30)), T((24, -6)), T((-24, -6)), T((-40, -30))]
    inner = blob([T(p) for p in [(14, -82), (50, -82), (40, -30), (24, -6), (6, -6)]], "#d8cfc0", .9)
    inner += blob([T(p) for p in [(-48, -64), (48, -64), (46, -52), (-46, -52)]], band_col)
    o.append(shape(body, col, inner, w=3.8, seed=2103))
    rim = ellipse_pts(x, y - 82 * k, 46 * k, 11 * k, 16)
    rin = blob(ellipse_pts(x, y - 81 * k, 40 * k, 8 * k, 14), "#b07a4c" if latte else "#4a2c1c")
    if latte and heart:
        hx_, hy_ = x, y - 81 * k
        rin += blob([(hx_ - 12 * k, hy_ - 3 * k), (hx_ - 6 * k, hy_ - 6 * k), (hx_, hy_ - 3 * k), (hx_ + 6 * k, hy_ - 6 * k), (hx_ + 12 * k, hy_ - 3 * k),
                     (hx_, hy_ + 5 * k, 1)], "#f6ecdc")
    o.append(shape(rim, col, rin, w=3.2, seed=2104))
    if steam_t is not None:
        for j in range(2):
            ph = steam_t * .9 + j * .5
            u = ph % 1.0
            a = math.sin(math.pi * u)
            sx = x + (-12 + j * 22) * k
            pts = [(sx, y - 96 * k - u * 40 * k), (sx + 10 * k * math.sin(ph * 6), y - 130 * k - u * 50 * k),
                   (sx - 6 * k * math.sin(ph * 5), y - 166 * k - u * 60 * k)]
            o.append(line(pts, 5 * k, "#ffffff", seed=2110 + j, op=.45 * a, taper=.3, wmin=.2))
    return "".join(o)


def phone(x, y, k=1.0, glow=0.0, buzz=(0.0, 0.0), ang=-24.0, squash=0.42, lift=0.0):
    """Телефон лежит экраном вниз на столе: план 150×300 (повёрнут на ang в плоскости стола), сжат по вертикали
    (наклон столешницы), видна тонкая боковая грань; glow — свет экрана, выбивающийся из-под краёв (уведомление)."""
    o = []
    gx, gy = x + buzz[0], y + buzz[1] - lift
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def T(p, dz=0.0):
        X, Y = p[0] * k, p[1] * k
        return (gx + X * c - Y * s, gy + (X * s + Y * c) * squash + dz)
    th = 8 * k
    if glow > 0.01:
        gl = lib.rad_grad([(0, "#e6f4ff", min(1, 1.1 * glow)), (.4, "#a8d2ff", .6 * glow), (1, "#7fb6ff", 0)], gx, gy + th, 230 * k, 110 * k)
        o.append(f'<ellipse cx="{gx}" cy="{gy + th + lift}" rx="{230 * k}" ry="{110 * k}" fill="url(#{gl})"/>')
    R = [(-75, -150), (75, -150), (75, 150), (-75, 150)]
    # тень на столе
    o.append(blob([T(p, th + 4 * k + lift) for p in [(-70, -140), (80, -140), (80, 156), (-70, 156)]], "#3a2416", .28))
    # боковая грань: нижний контур плана, вытянутый вниз на толщину
    pts = [T(p) for p in R]
    low = sorted(range(4), key=lambda i: pts[i][1])[2:]
    hull = []
    for i in range(4):
        hull.append(pts[i])
    side = []
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        if i in low or (i + 1) % 4 in low:
            pass
    # грань — многоугольник: весь план, сдвинутый вниз, объединённый с планом (рисуется под корпусом)
    ext = [T(p, th) for p in R]
    edge_col = lib.mix("#2c2e36", "#bfe2ff", min(1.0, glow * 1.2))
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        a2, b2 = ext[i], ext[(i + 1) % 4]
        o.append(f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}L{b2[0]:.1f} {b2[1]:.1f}L{a2[0]:.1f} {a2[1]:.1f}Z" fill="{edge_col}"/>')
    o.append(f'<path d="{lib.ink_closed(_hull(pts + ext), 3.6 * lib.INK_K[0], seed=2199)}" fill="{INK}"/>')
    # корпус (скруглённый)
    rr = 22
    body = []
    for (cx_, cy_, a0) in [(75 - rr, -150 + rr, -90), (75 - rr, 150 - rr, 0), (-75 + rr, 150 - rr, 90), (-75 + rr, -150 + rr, 180)]:
        for j in range(4):
            a = math.radians(a0 + j * 30)
            body.append(T((cx_ + rr * math.cos(a), cy_ + rr * math.sin(a))))
    inner = blob([T(p) for p in [(-80, -160), (80, -160), (80, -40), (-80, 30)]], "#3b3e4a", .9)
    inner += f'<path d="M{T((-40, 150))[0]:.1f} {T((-40, 150))[1]:.1f}L{T((75, 20))[0]:.1f} {T((75, 20))[1]:.1f}" stroke="#ffffff" stroke-opacity=".10" stroke-width="{14 * k:.1f}"/>'
    cam_m = [T(p) for p in [(-58, -132), (-6, -132), (-6, -70), (-58, -70)]]
    inner += lib.shape(cam_m, "#1c1d23", blob(ellipse_pts(*T((-32, -114)), 12 * k, 12 * k * squash, 10), "#4a5070") +
                       blob(ellipse_pts(*T((-32, -86)), 12 * k, 12 * k * squash, 10), "#4a5070") +
                       blob(ellipse_pts(*T((-34, -116)), 4 * k, 4 * k * squash, 6), "#9aa6d0"), w=2.2, seed=2202)
    o.append(lib.shape(body, "#2a2c34", inner, w=3.4, seed=2201))
    return "".join(o)


def _hull(P):
    P = sorted(set((round(p[0], 2), round(p[1], 2)) for p in P))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return [q + (1,) for q in lo[:-1] + up[:-1]]


def zip_pos(x, y, k, zip_u):
    """Где бегунок молнии рюкзака (для кисти, которая его тянет)."""
    arc = [(-62, -140), (-36, -172), (0, -180), (36, -172), (62, -140)]
    u = (1 - zip_u) * 4
    j = min(int(u), 3)
    a, b = np.array(arc[j], float), np.array(arc[j + 1], float)
    p = a + (b - a) * (u - j)
    return np.array([x + p[0] * k, y + p[1] * k])


# ═════════════════════════ вход (хук s01): дверь, колокольчик, стойка с кофемашиной ═════════════════════════
DOOR = (30.0, 250.0, 350.0, 1330.0)


def entrance(t, theta, bell):
    """Стена у входа; дверь (петли слева) открыта на угол theta (0 — закрыта, 90° — к стене), за ней улица."""
    o = []
    g = lib.lin_grad([(0, "#c99a6c", 1), (.35, PLASTER, 1), (1, "#e6bd88", 1)], 0, 0, 0, 1000, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-800" width="3000" height="1800" fill="url(#{g})"/>')
    for (x, y, r, a) in [(560, 420, 560, .5), (1150, 520, 300, .45)]:
        gl = lib.rad_grad([(0, "#fff0c8", a), (.5, "#ffd89a", a * .45), (1, "#ffcf8a", 0)], x, y, r)
        o.append(f'<rect x="{x - r}" y="{y - r}" width="{2 * r}" height="{2 * r}" fill="url(#{gl})"/>')
    o.append(shape([(-600, 940, 1), (1800, 940, 1), (1800, 3200, 1), (-600, 3200, 1)], PANEL,
                   blob([(-600, 940), (1800, 940), (1800, 966), (-600, 966)], PANEL_SH, .9), w=4, seed=5000))
    for k in range(-5, 13):
        x = k * 150 + 20
        o.append(shape([(x + 14, 990, 1), (x + 136, 990, 1), (x + 136, 3200, 1), (x + 14, 3200, 1)], PANEL_HI,
                       blob([(x + 120, 990), (x + 136, 990), (x + 136, 3200), (x + 120, 3200)], PANEL_SH, .7), w=2.8, seed=5010 + k))
    o.append(shape([(-600, 924, 1), (1800, 924, 1), (1800, 950, 1), (-600, 950, 1)], WOOD_HI, w=3.6, seed=5001))
    # проём двери и улица
    x0, y0, x1, y1 = DOOR
    clip = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o.append(f'<g clip-path="url(#{clip})"><g transform="translate({x0 - 60} {y0 - 180})">{street(t)}</g></g>')
    fw = 30
    outer = [(x0 - fw, y0 - fw, 1), (x1 + fw, y0 - fw, 1), (x1 + fw, y1 + 300, 1), (x0 - fw, y1 + 300, 1)]
    o.append(f'<path d="{lib.fill_d(outer)}M{x0} {y0}H{x1}V{y1 + 300}H{x0}Z" fill="{WOOD_DK}" fill-rule="evenodd"/>')
    o.append(f'<path d="{lib.ink_closed(outer, 4.6 * lib.INK_K[0], seed=5020)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed([(x0, y0, 1), (x1, y0, 1), (x1, y1 + 300, 1), (x0, y1 + 300, 1)], 3.8 * lib.INK_K[0], seed=5021)}" fill="{INK}"/>')
    # тёплый свет из кафе на пороге улицы
    gl = lib.rad_grad([(0, "#ffd99a", .35), (1, "#ffd99a", 0)], (x0 + x1) / 2, y1, 300, 140)
    o.append(f'<ellipse cx="{(x0 + x1) / 2}" cy="{y1}" rx="300" ry="140" fill="url(#{gl})"/>')
    # дверное полотно: петли слева, при открытии свободный край идёт к нам (выше, ниже) и влево
    th = math.radians(theta)
    w = (x1 - x0) * math.cos(th)
    ex = x0 + w
    grow = 70 * math.sin(th)
    pts = [(x0, y0, 1), (ex, y0 - grow, 1), (ex, y1 + 300 + grow, 1), (x0, y1 + 300, 1)]

    def L(u, v):
        xa = x0 + (ex - x0) * u
        ya = y0 - grow * u
        yb = y1 + 300 + grow * u
        return (xa, ya + (yb - ya) * v)
    gl_pts = [L(.16, .06), L(.84, .06), L(.84, .5), L(.16, .5)]
    inner = blob([L(0, 0), L(.2, 0), L(.2, 1), L(0, 1)], WOOD_SH, .8)
    gl_in = f'<g clip-path="url(#{lib.clip_of(gl_pts)})"><g transform="translate({x0 - 60 - (1 - math.cos(th)) * 200:.1f} {y0 - 180})">{street(t)}</g></g>'
    inner += lib.shape(gl_pts, "#3a3058", gl_in + blob([gl_pts[0], gl_pts[1], (gl_pts[1][0], gl_pts[1][1] + 40), (gl_pts[0][0], gl_pts[0][1] + 60)],
                                                       "#ffffff", .1), w=3.4, seed=5031)
    hx, hy = L(.88, .58)
    inner += lib.shape(ellipse_pts(hx, hy, 9 * max(.3, math.cos(th)) + 3, 9, 10), "#d9b56a", w=2.4, seed=5032)
    if abs(ex - x0) > 6:
        o.append(lib.shape(pts, WOOD, inner, w=4.6, seed=5030))
    # колокольчик над дверью
    bx, by = (x0 + x1) / 2 + 60, y0 - 50
    ang = bell
    o.append(lib.line([(bx, y0 - 90), (bx, by - 20)], 3, "#2a2228", seed=5040))
    c = math.radians(ang)
    tip = (bx + math.sin(c) * 46, by - 20 + math.cos(c) * 46)
    bell_pts = [(bx - 6, by - 20), (bx + 6, by - 20), (bx + 26, by + 16), (bx - 26, by + 16)]
    o.append(f'<g transform="rotate({-ang:.2f} {bx} {by - 20})">' + lib.shape(bell_pts, "#e2b24a", blob([(bx + 6, by - 20), (bx + 26, by + 16),
                                                                                                        (bx + 10, by + 16)], "#b8862e", .9), w=3, seed=5041) +
             f'<circle cx="{bx}" cy="{by + 22}" r="6" fill="#b8862e"/></g>')
    if abs(bell) > 4:
        for j, sx in enumerate((-1, 1)):
            o.append(lib.line([(bx + sx * 40, by - 10), (bx + sx * 56, by - 20)], 3.4, INK, seed=5045 + j, op=min(1, abs(bell) / 20)))
            o.append(lib.line([(bx + sx * 42, by + 8), (bx + sx * 62, by + 6)], 3.4, INK, seed=5047 + j, op=min(1, abs(bell) / 20)))
    _ = tip
    # справа — стойка: полки с чашками, кофемашина
    o.append(shape([(860, 520, 1), (1500, 520, 1), (1500, 542, 1), (860, 542, 1)], WOOD_HI, w=3.4, seed=5050))
    o.append(shape([(860, 700, 1), (1500, 700, 1), (1500, 722, 1), (860, 722, 1)], WOOD_HI, w=3.4, seed=5051))
    for k, x in enumerate(range(900, 1480, 70)):
        col = ["#e85f4f", "#f2e6cf", "#4f8ea0", "#e3b14a"][k % 4]
        o.append(shape([(x, 470), (x + 50, 470), (x + 46, 520, 1), (x + 4, 520, 1)], col, w=3, seed=5060 + k))
        if k % 2 == 0:
            o.append(shape([(x - 4, 610), (x + 52, 610), (x + 52, 700, 1), (x - 4, 700, 1)], "#e9e1d0",
                           blob([(x - 4, 650), (x + 52, 646), (x + 52, 700), (x - 4, 700)], "#6b4a2e"), w=3, seed=5080 + k))
    mx, my = 1010, 920
    o.append(shape([(mx - 150, my - 170, 1), (mx + 150, my - 170, 1), (mx + 160, my, 1), (mx - 160, my, 1)], "#c9483a",
                   blob([(mx + 60, my - 170), (mx + 150, my - 170), (mx + 160, my), (mx + 70, my)], "#9e3329", .9) +
                   blob([(mx - 150, my - 170), (mx + 150, my - 170), (mx + 150, my - 140), (mx - 150, my - 140)], "#d8d6d0"), w=4.4, seed=5100))
    for k, gx in enumerate((mx - 70, mx + 60)):
        o.append(shape([(gx - 26, my - 110), (gx + 26, my - 110), (gx + 18, my - 84, 1), (gx - 18, my - 84, 1)], "#cfcdc6", w=3, seed=5110 + k))
    sw = 6 * math.sin(t * 5)
    for j in range(2):
        u = (t * .8 + j * .5) % 1
        o.append(lib.line([(mx + 120, my - 150 - 40 * u), (mx + 128 + sw, my - 200 - 50 * u), (mx + 116, my - 250 - 60 * u)], 6, "#ffffff",
                          seed=5120 + j, op=.5 * math.sin(math.pi * u)))
    o.append(shape([(760, my, 1), (1700, my, 1), (1700, my + 30, 1), (760, my + 30, 1)], WOOD_HI, w=4, seed=5130))
    o.append(shape([(770, my + 30, 1), (1700, my + 30, 1), (1700, 3200, 1), (770, 3200, 1)], WOOD,
                   blob([(770, my + 30), (1700, my + 30), (1700, my + 60), (770, my + 60)], WOOD_SH, .9), w=4, seed=5131))
    return "".join(o)
