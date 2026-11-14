"""Офис рилса 42: стена, окно с жалюзи на дневной город, белая доска со схемами (без букв) и стикерами, полка с
папками, перегородка с коллегой за ней, растения, офисное кресло, стол светлого дерева, серый ковролин.
Мир — как у den.py рилса 39: стена до FLOOR_Y=1330, столешница y 1080–1150 (x от 350), Дима сидит слева лицом вправо
(таз (230, 1262)). Функции возвращают SVG в мировых координатах; камера — в scene.py."""
import math

import numpy as np

import den
import lib
import room
from lib import INK, T, blob, ellipse_pts, line, mix, rect_pts, shape

FLOOR_Y = den.FLOOR_Y
# стол — светлое дерево (den.desk_top берёт цвета из модуля при вызове)
den.WOOD, den.WOOD_SH, den.WOOD_HI, den.WOOD_DK = "#c9a978", "#a2845a", "#dcc196", "#7a6040"

WALL, WALL_SH, WALL_LO = "#e3e4dc", "#cfd1c7", "#b9c4c4"
WIN = (30.0, 220.0, 400.0, 790.0)


def rsd(*k):
    return room.rsd(*k)


def wall(t):
    s = [f'<rect x="-600" y="-600" width="2400" height="{FLOOR_Y + 600}" fill="{WALL}"/>']
    # стыки панелей и нижняя панель стены
    for k, x in enumerate((470, 880, 1290)):
        s.append(line([(x, -300), (x + 2, FLOOR_Y - 300)], 2.0, WALL_SH, seed=5100 + k, op=.8, taper=.05, wmin=.9))
    s.append(blob(rect_pts(-600, FLOOR_Y - 300, 1800, FLOOR_Y), WALL_LO))
    s.append(shape(rect_pts(-600, FLOOR_Y - 312, 1800, FLOOR_Y - 296), "#d7dbd3", blob(rect_pts(-600, FLOOR_Y - 302, 1800, FLOOR_Y - 296), "#a9b3b2"),
                   w=3, seed=5110))
    s.append(shape(rect_pts(-600, FLOOR_Y - 30, 1800, FLOOR_Y + 4), "#5d6670", blob(rect_pts(-600, FLOOR_Y - 10, 1800, FLOOR_Y + 4), "#454c55", .9),
                   w=3.4, seed=5111))
    return "".join(s)


def window(t, blinds=0.55):
    """Окно на дневной город, жалюзи опущены на долю blinds (сверху), ламели приоткрыты — полосы света."""
    x0, y0, x1, y1 = WIN
    sky = lib.lin_grad([(0, "#86c6ec", 1), (.7, "#bfe3f5", 1), (1, "#e2f3fa", 1)], 0, 0, 0, 1)
    inner = [f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>']
    for k, (cx, cy, rr) in enumerate([(x0 + 100 + 12 * math.sin(t * .4), y0 + 260, 44), (x0 + 280 - 9 * math.sin(t * .3), y0 + 330, 34)]):
        cl = [(cx - rr * 1.6, cy + rr * .4), (cx - rr * 1.2, cy - rr * .3), (cx - rr * .5, cy - rr * .8), (cx + rr * .3, cy - rr * .6),
              (cx + rr * 1.1, cy - rr * .2), (cx + rr * 1.6, cy + rr * .4)]
        inner.append(shape(cl, "#ffffff", blob([(cx - rr * 1.5, cy + rr * .15), (cx + rr * 1.5, cy + rr * .15), (cx + rr * 1.6, cy + rr * .4),
                                                (cx - rr * 1.6, cy + rr * .4)], "#dcebf3"), w=3, seed=5260 + k))
    far = [(x0 - 20, y1 - 300), (x0 + 50, y1 - 300), (x0 + 50, y1 - 380), (x0 + 130, y1 - 380), (x0 + 130, y1 - 260), (x0 + 210, y1 - 260),
           (x0 + 210, y1 - 420), (x0 + 290, y1 - 420), (x0 + 290, y1 - 320), (x1 + 20, y1 - 320), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)]
    inner.append(blob(far, "#a7bccb"))
    for i, (x, y, w, col) in enumerate([(x0 - 10, y1 - 230, 120, "#e3b48a"), (x0 + 125, y1 - 190, 110, "#d98f74"), (x0 + 250, y1 - 260, 130, "#e8d2a6")]):
        inner.append(shape(rect_pts(x, y, x + w, y1 + 30), col, blob(rect_pts(x + w * .72, y, x + w, y1 + 30), "#000000", .14), w=3, seed=5210 + i))
        rs = rsd(5220, i)
        for r in range(6):
            for c in range(int(w // 34)):
                wx, wy = x + 12 + c * 34, y + 18 + r * 46
                if wy > y1:
                    continue
                inner.append(blob(rect_pts(wx, wy, wx + 18, wy + 26), "#8fc3e0" if rs.uniform() < .45 else "#5d7f99"))
    # жалюзи: ламели до низа шторки, между ними щели неба
    yb = y0 + (y1 - y0) * blinds
    sl = []
    y = y0 - 4
    k = 0
    while y < yb:
        sl.append(blob(rect_pts(x0 - 6, y, x1 + 6, y + 15), "#f1f2ec"))
        sl.append(blob(rect_pts(x0 - 6, y + 10, x1 + 6, y + 15), "#c9ccc2"))
        sl.append(line([(x0 - 6, y + 15.5), (x1 + 6, y + 15.5)], 1.6, "#8f948c", seed=5300 + k, op=.8, taper=.05, wmin=.9))
        y += 22
        k += 1
    sl.append(shape(rect_pts(x0 - 8, yb - 4, x1 + 8, yb + 12, 3), "#e6e7e0", "", w=2.6, seed=5290))
    for j, xx in enumerate((x0 + 90, x1 - 90)):
        sl.append(line([(xx, y0 - 10), (xx, yb)], 1.6, "#9aa09a", seed=5295 + j, op=.8, taper=.05, wmin=.9))
    inner.append("".join(sl))
    # шнур жалюзи
    cord = [(x1 - 24, y0 - 10), (x1 - 22, yb + 140 + 4 * math.sin(t * 1.3))]
    fr = "#e8e8e2"
    s = [shape(rect_pts(x0 - 22, y0 - 22, x1 + 22, y1 + 22, 6), fr, blob(rect_pts(x1, y0 - 22, x1 + 22, y1 + 22), "#c6c8bf", .9), w=4.6, seed=5230)]
    s.append(shape(rect_pts(x0, y0, x1, y1, 4), "#bfe3f5", "".join(inner), w=4, seed=5231))
    s.append(line(cord, 2.4, "#7d817a", seed=5240, taper=.05, wmin=.9))
    s.append(shape(ellipse_pts(cord[1][0], cord[1][1] + 8, 6, 10, 10), "#d9dad3", "", w=2.2, seed=5241))
    for k, (a, b) in enumerate([((x0 + 26, y1 - 40), (x0 + 110, y1 - 130)), ((x0 + 50, y1 - 20), (x0 + 160, y1 - 120))]):
        s.append(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="#ffffff" stroke-opacity=".12" stroke-width="{12 - k * 4}" stroke-linecap="round"/>')
    s.append(shape(rect_pts(x0 - 40, y1 + 16, x1 + 40, y1 + 44, 4), "#eceee6", blob(rect_pts(x0 - 40, y1 + 32, x1 + 40, y1 + 44), "#c9ccc2", .9),
                   w=4, seed=5232))
    s.append(room.pot(x0 + 70, y1 + 16, .8, 5245, leaves=5, col="#e0e0d8"))
    return "".join(s)


def light_stripes(t, blinds=0.55, a=.13):
    """Полосы солнца сквозь ламели на стене справа от окна (наискосок вниз)."""
    x0, y0, x1, y1 = WIN
    yb = y0 + (y1 - y0) * blinds
    o = []
    y = y0 + 8
    while y < yb:
        p = [(x1 + 30, y + 40), (x1 + 420, y + 220), (x1 + 420, y + 230), (x1 + 30, y + 49)]
        o.append(blob(p, "#fff6d8", a))
        y += 22
    p = [(x1 + 30, yb + 40), (x1 + 420, yb + 220), (x1 + 420, y1 + 300), (x1 + 30, y1 + 70)]
    o.append(blob(p, "#fff6d8", a * .9))
    return f'<g style="mix-blend-mode:screen">{"".join(o)}</g>'


def whiteboard(t):
    x0, y0, x1, y1 = 520, 270, 870, 540
    s = [blob(rect_pts(x0 + 8, y0 + 10, x1 + 12, y1 + 14, 6), "#000000", .12)]
    inner = blob([(x1 - 120, y0), (x1, y0), (x1, y0 + 120)], "#ffffff", .8)
    # схема маркерами: столбики, стрелка, кружки — без букв
    for k, (bx, h, col) in enumerate([(560, 70, "#3b6fd0"), (600, 110, "#3b6fd0"), (640, 90, "#3b6fd0"), (680, 150, "#d8483c")]):
        inner += line([(bx, y1 - 40), (bx, y1 - 40 - h)], 14, col, seed=5400 + k, taper=.05, wmin=.9, op=.85)
    inner += line([(545, y1 - 34), (705, y1 - 34)], 3, INK, seed=5410, taper=.05, wmin=.9)
    inner += line([(560, y1 - 130), (600, y1 - 170), (640, y1 - 150), (690, y1 - 215)], 4, "#2f9a5a", seed=5411, taper=.1, wmin=.8)
    inner += line([(676, y1 - 210), (692, y1 - 218), (690, y1 - 200)], 4, "#2f9a5a", seed=5412, taper=.1, wmin=.8)
    for k, (cx, cy) in enumerate([(760, 320), (820, 390)]):
        inner += line([(cx + 26 * math.cos(a), cy + 22 * math.sin(a)) for a in np.linspace(0, 6.1, 14)], 3.4, "#3b6fd0", seed=5420 + k)
    inner += line([(786, 334), (806, 372)], 3, "#3b6fd0", seed=5425)
    inner += line([(560, 300), (620, 302)], 3.4, "#9aa1ae", seed=5426) + line([(560, 318), (640, 318)], 3.4, "#9aa1ae", seed=5427)
    s.append(shape(rect_pts(x0 - 14, y0 - 14, x1 + 14, y1 + 14, 6), "#b8bdc2", blob(rect_pts(x1, y0 - 14, x1 + 14, y1 + 14), "#8f969c", .9), w=4, seed=5401))
    s.append(shape(rect_pts(x0, y0, x1, y1, 2), "#fbfbf8", inner, w=3, seed=5402))
    # полочка с маркерами
    s.append(shape(rect_pts(x0 + 40, y1 + 14, x1 - 40, y1 + 26, 3), "#9aa1a7", "", w=2.6, seed=5403))
    for k, (mx, col) in enumerate([(640, "#d8483c"), (690, "#3b6fd0"), (740, INK)]):
        s.append(shape(rect_pts(mx, y1 + 4, mx + 40, y1 + 14, 4), "#f4f4f0", blob(rect_pts(mx + 28, y1 + 4, mx + 40, y1 + 14, 3), col), w=2.2, seed=5430 + k))
    # стикеры на доске и рядом
    for k, (x, y, a, col) in enumerate([(830, 470, 6, "#f6e27a"), (915, 300, -5, "#f4a7b0"), (930, 395, 4, "#9fd3c7"), (905, 480, -3, "#f6e27a")]):
        n = blob(T(rect_pts(-34, -32, 34, 32, 3), x + 4, y + 5, 1, a), "#000000", .15)
        n += shape(T(rect_pts(-34, -32, 34, 32, 3), x, y, 1, a + 2 * math.sin(t * 1.7 + k) * (k == 1)), col,
                   blob(T([(-34, 14), (34, 12), (34, 32), (-34, 32)], x, y, 1, a), "#000000", .07) +
                   line(T([(-20, -8), (16, -9)], x, y, 1, a), 2.6, "#7a6a50", seed=5450 + k, op=.6) +
                   line(T([(-20, 4), (6, 3)], x, y, 1, a), 2.6, "#7a6a50", seed=5460 + k, op=.6), w=2.6, seed=5440 + k)
        s.append(n)
    return "".join(s)


def shelf(t):
    """Полка с цветными папками и коробкой над перегородкой."""
    y = 530
    x0, x1 = 980, 1420
    s = [shape(rect_pts(x0, y, x1, y + 18), "#d4d6cf", blob(rect_pts(x0, y + 10, x1, y + 18), "#a8aba3", .9), w=3.4, seed=5500)]
    for k, x in enumerate((1010, 1380)):
        s.append(shape([(x - 7, y + 18, 1), (x + 7, y + 18, 1), (x + 7, y + 50, 1), (x - 24, y + 18, 1)], "#8f948c", w=3, seed=5501 + k))
    cols = ["#3b6fd0", "#d8483c", "#3aa86b", "#e0a93a", "#3b6fd0", "#8a5a8a"]
    x = 1000
    for k, col in enumerate(cols):
        w = 34
        h = 118 - 6 * (k % 3)
        inn = blob(rect_pts(x + w * .66, y - h, x + w, y), "#000000", .16)
        inn += shape(ellipse_pts(x + w * .45, y - h * .3, 7, 7, 10), "#f4f2ea", "", w=2, seed=5520 + k)
        inn += blob(rect_pts(x + 6, y - h + 14, x + w - 8, y - h + 40, 3), "#f4f2ea", .9)
        s.append(shape(rect_pts(x, y - h, x + w, y), col, inn, w=2.8, seed=5510 + k))
        x += w + 3
    s.append(shape(rect_pts(1230, y - 70, 1330, y), "#c9a46a", blob(rect_pts(1300, y - 70, 1330, y), "#000000", .15) +
                   line([(1230, y - 52), (1330, y - 52)], 2, "#8f6f3a", seed=5531, op=.8), w=3, seed=5530))
    return "".join(s)


def tall_plant(t, x=468.0, y=1080.0, k=1.0):
    """Сансевиерия в кадке за столом: листья-мечи над столешницей, покачиваются."""
    o = []
    rs = np.random.RandomState(5600)
    for i in range(7):
        a = math.radians(-90 + (i - 3) * 9 + rs.uniform(-4, 4)) + .015 * math.sin(t * 1.1 + i)
        L = (330 + rs.uniform(-60, 60)) * k
        nrm = np.array([-math.sin(a), math.cos(a)])
        b = np.array([x + (i - 3) * 8 * k, y])
        tip = b + np.array([math.cos(a), math.sin(a)]) * L
        m = b + (tip - b) * .5
        w = 26 * k
        lf = [tuple(b + nrm * w * .6), tuple(m + nrm * w), tuple(tip) + (1,), tuple(m - nrm * w), tuple(b - nrm * w * .6)]
        col = "#4f8a4a" if i % 2 else "#5f9a52"
        inn = blob([tuple(b), tuple(m - nrm * w), tuple(tip), tuple(m)], "#3d6e3b", .5)
        inn += line([tuple(b + (tip - b) * .2 + nrm * 6), tuple(b + (tip - b) * .45 - nrm * 4)], 3, "#cfe08a", seed=5610 + i, op=.6)
        inn += line([tuple(b + (tip - b) * .55 + nrm * 5), tuple(b + (tip - b) * .75 - nrm * 3)], 3, "#cfe08a", seed=5620 + i, op=.6)
        o.append(shape(lf, col, inn, w=3.4, seed=5630 + i))
    return "".join(o)


def colleague(t, x=1120.0, y=860.0, k=1.0, turn=0.0):
    """Коллега за перегородкой: затылок, плечи в голубой рубашке, монитор перед ним (сидит спиной к нам, чуть вправо)."""
    o = []
    # монитор
    mx = x + 150 * k
    o.append(shape(rect_pts(mx - 10 * k, y - 220 * k, mx + 170 * k, y - 80 * k, 6), "#2b2e38",
                   blob(rect_pts(mx + 2 * k, y - 208 * k, mx + 158 * k, y - 92 * k, 4), "#bcd6ee") +
                   blob(rect_pts(mx + 14 * k, y - 196 * k, mx + 90 * k, y - 186 * k, 3), "#6f8fb8"), w=3.4, seed=5700))
    o.append(shape(rect_pts(mx + 70 * k, y - 80 * k, mx + 90 * k, y - 20 * k), "#3c4150", "", w=2.6, seed=5701))
    # плечи и спина
    bob = 3 * math.sin(t * 1.4)
    sh = [(x - 120 * k, y + 40 * k), (x - 110 * k, y - 60 * k + bob), (x - 60 * k, y - 96 * k + bob), (x + 60 * k, y - 96 * k + bob),
          (x + 112 * k, y - 60 * k + bob), (x + 124 * k, y + 40 * k)]
    o.append(shape(sh, "#7fa6d6", blob([(x + 20 * k, y - 96 * k), (x + 112 * k, y - 60 * k), (x + 124 * k, y + 40 * k), (x + 40 * k, y + 40 * k)],
                                        "#5f86b8", .8) + line([(x, y - 90 * k + bob), (x + 4 * k, y + 30 * k)], 2.2, "#4f73a0", seed=5703, op=.7),
                   w=4, seed=5702))
    # шея и голова (затылок, тёмные волосы, ухо справа)
    hx, hy = x + 6 * k + 10 * turn * k, y - 170 * k + bob
    o.append(shape(rect_pts(hx - 26 * k, hy + 40 * k, hx + 26 * k, hy + 90 * k, 8), "#d9a98a", "", w=3, seed=5704))
    o.append(shape(ellipse_pts(hx + 58 * k, hy + 10 * k, 16 * k, 22 * k, 10), "#e5b896", "", w=3, seed=5705))
    head = ellipse_pts(hx, hy, 62 * k, 72 * k, 22)
    o.append(shape(head, "#3a2a24", blob(ellipse_pts(hx + 22 * k, hy + 10 * k, 40 * k, 60 * k, 16), "#2a1d18", .7) +
                   line([(hx - 30 * k, hy - 40 * k), (hx - 10 * k, hy - 10 * k)], 2.4, "#5a4238", seed=5707, op=.8) +
                   line([(hx + 10 * k, hy - 52 * k), (hx + 22 * k, hy - 20 * k)], 2.4, "#5a4238", seed=5708, op=.8), w=4, seed=5706))
    return "".join(o)


def partition(t, x0=880.0, y0=870.0, x1=1600.0, y1=1090.0):
    """Перегородка рабочего места за столом (тканевая, в рамке)."""
    inner = blob(rect_pts(x0, y0 + 30, x1, y1), "#6f8798", .5)
    rs = rsd(5800)
    for k in range(60):
        x, y = rs.uniform(x0, x1), rs.uniform(y0, y1)
        inner += blob(ellipse_pts(x, y, 2, 1.5, 6), "#5f7787", .6)
    o = [shape(rect_pts(x0, y0, x1, y1), "#7f97a8", inner, w=3.4, seed=5801)]
    o.append(shape(rect_pts(x0 - 10, y0 - 14, x1, y0 + 4, 4), "#cfd2cc", blob(rect_pts(x0 - 10, y0 - 4, x1, y0 + 4), "#a3a8a2", .9), w=3.2, seed=5802))
    o.append(shape(rect_pts(x0 - 12, y0 - 14, x0 + 6, y1, 3), "#cfd2cc", "", w=3, seed=5803))
    # пришпиленный листок-график на перегородке
    o.append(shape(T(rect_pts(-40, -50, 40, 50, 2), x0 + 120, y0 + 100, 1, -4), "#fbfbf6",
                   line(T([(-26, 20), (-6, 0), (8, 10), (26, -24)], x0 + 120, y0 + 100, 1, -4), 3, "#3b6fd0", seed=5810), w=2.6, seed=5811))
    o.append(shape(ellipse_pts(x0 + 118, y0 + 56, 6, 6, 10), "#d8483c", "", w=2, seed=5812))
    return "".join(o)


def floor():
    s = [blob([(-600, FLOOR_Y), (1800, FLOOR_Y), (1800, 2800), (-600, 2800)], "#8a8f93")]
    vx, vy = 540, 700
    for k in range(-14, 16):
        xb = 540 + k * 150
        x0 = vx + (xb - vx) * (FLOOR_Y - vy) / (2800 - vy)
        s.append(line([(x0, FLOOR_Y), (xb, 2800)], 2.0, "#767b80", seed=5900 + k + 20, op=.6, taper=.1, wmin=.7))
    for k, y in enumerate((1400, 1520, 1690)):
        s.append(line([(-600, y), (1800, y)], 2.0, "#767b80", seed=5950 + k, op=.5, taper=.05, wmin=.8))
    return "".join(s)


def office_chair(x, seat_y, sq=0.0, seed=5980):
    """Офисное кресло в профиль: спинка за спиной (слева), сиденье, газлифт, крестовина на колёсиках. sq — просадка при
    плюхе (0..1): сиденье опускается, спинка качается."""
    o = []
    dy = 18 * sq
    sy = seat_y + dy
    # крестовина и колёса
    base_y = 1462
    for k, (dx, w) in enumerate([(-130, 1), (130, 1), (-60, .8), (70, .8)]):
        o.append(line([(x, base_y - 8), (x + dx, base_y + 2)], 13 * w, "#2b2e38", seed=seed + k, taper=.05, wmin=.9))
        o.append(shape(ellipse_pts(x + dx, base_y + 12, 14 * w, 14 * w, 12), "#1f2129", "", w=2.6, seed=seed + 10 + k))
    o.append(shape(rect_pts(x - 10, sy + 34, x + 10, base_y - 4, 3), "#8f969c", blob(rect_pts(x + 2, sy + 34, x + 10, base_y - 4), "#6c7278", .9), w=3,
                   seed=seed + 20))
    o.append(shape(rect_pts(x - 22, sy + 24, x + 22, sy + 50, 4), "#2b2e38", "", w=3, seed=seed + 21))
    # стойка спинки и спинка
    bx = x - 118
    o.append(line([(x - 40, sy + 30), (bx + 10, sy + 20), (bx + 18, sy - 150)], 14, "#2b2e38", seed=seed + 22, taper=.05, wmin=.9))
    rk = -4 * sq
    back = T([(-30, -400, 1), (40, -404, 1), (50, -200), (36, -110, 1), (-24, -106, 1), (-36, -220)], bx, sy, 1, rk)
    o.append(shape(back, "#3b4250", blob(T([(16, -400), (40, -404), (50, -200), (36, -110), (20, -110)], bx, sy, 1, rk), "#2b313c", .9) +
                   line(T([(-14, -370), (-20, -240), (-10, -130)], bx, sy, 1, rk), 2.4, "#56607a", seed=seed + 24, op=.8), w=4.2, seed=seed + 23))
    seat = [(x - 150, sy - 6, 1), (x + 130, sy - 8, 1), (x + 150, sy + 22, 1), (x - 150, sy + 30, 1)]
    o.append(shape(seat, "#3b4250", blob([(x - 160, sy + 12), (x + 160, sy + 10), (x + 160, sy + 34), (x - 160, sy + 34)], "#2b313c", .9), w=4,
                   seed=seed + 25))
    return "".join(o)


def office_back(t, blinds=0.55):
    return "".join([wall(t), window(t, blinds), light_stripes(t, blinds), whiteboard(t), shelf(t), floor()])
