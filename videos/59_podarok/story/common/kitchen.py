"""Общая кухня рилса 59 «подарок» — ОДИН вид для групп E и F (s11, s12, s13, s14, s15). Пишет группа E.

Подключение (в сцене группы, рядом свой lib.py/ink.py с теми же помощниками, что у рилса 57):
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common")); import kitchen
Все функции возвращают строку SVG (мир кадра 1080×1920 до камеры), без собственной камеры, заливки сплошные, тушь — lib.INK.

    kitchen.static()                       задняя стена: плитка, окно слева, верхние шкафы, рейка, столешница y=1010, нижние шкафы,
                                           ПЛИТА С ДУХОВКОЙ справа (x 640…1040, корпус и пустая полость), пол y=1330+ (один раз на ролик)
    kitchen.oven_door(open_k)              дверца духовки, открывается вниз к зрителю (0 закрыта … 1 откинута); рисовать ПОСЛЕ Димы/лотка
    kitchen.oven_glow(open_k, t)           тёплый свет изнутри (рисовать до дверцы, после static)
    kitchen.table(x0, x1, back, front)     (ножки, крышка) стола: ножки — до Димы, крышка — после (как table_parts в рилсе 57)
    kitchen.light(t), kitchen.motes(t)     дневной луч из окна и пылинки
Константы: FLOOR_Y 1440, COUNTER_Y 1010, OVEN (x0 640, x1 1040, door_top 1075, hinge 1305, cav (x,y,w,h)), TABLE_BACK 1150, TABLE_FRONT 1215,
C_WALL, C_CAB, C_COUNTER, C_STEEL, C_FLOOR.
Дима стоит ЛИЦОМ к зрителю между столом (слева) и плитой (справа) на x≈520…560; руки с прихватками тянутся к дверце."""
import math

import numpy as np

import lib
from lib import blob, clamp, ellipse_pts, f, line, lin_grad, rect_pts, shape, smooth

INK = lib.INK
FLOOR_Y = 1440
COUNTER_Y = 1010
TABLE_BACK, TABLE_FRONT = 1150, 1215
C_WALL, C_TILE, C_CAB, C_COUNTER, C_FLOOR = "#EADFC6", "#F6F1E4", "#F8F2E6", "#C88A58", "#B58A5E"
C_STEEL, C_STEEL_SH = "#C4C9CF", "#9AA2AA"
C_TEAL = "#5E9B92"
OVEN = dict(x0=640, x1=1040, door_top=1075, hinge=1305, cav=(668, 1090, 344, 196))


def static():
    o = []
    o.append('<rect x="-1600" y="-2200" width="4400" height="3600" fill="#EADFC6"/>')
    o.append('<rect x="-1600" y="780" width="4400" height="560" fill="#F6F1E4"/>')
    for k in range(-24, 40):
        o.append(line([(k * 75, 780), (k * 75, 1330)], 2.2, "#D8CDB4", taper=.02, wmin=.95, seed=9000 + k, op=.8))
    for k in range(8):
        o.append(line([(-1600, 780 + k * 70), (2800, 780 + k * 70)], 2.2, "#D8CDB4", taper=.02, wmin=.95, seed=9100 + k, op=.8))
    o.append(shape(rect_pts(-1600, 770, 2800, 792), C_TEAL, blob(rect_pts(-1600, 784, 2800, 792), "#437A72"), w=3.6, seed=9150))
    # окно слева
    x0, y0, x1, y1 = 90, 250, 480, 700
    sky = lin_grad([(0, "#8EC9EE", 1), (1, "#D7EEF8", 1)], 0, 0, 0, 1)
    inn = f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="url(#{sky})"/>'
    inn += blob(ellipse_pts(180, 340, 46, 46, 18), "#FFF0A8") + blob(ellipse_pts(330, 420, 70, 22, 14), "#FFFFFF") + blob(ellipse_pts(250, 520, 56, 18, 14), "#FFFFFF")
    inn += blob([(x0 - 10, 640), (160, 620), (160, 570), (260, 570), (260, 630), (360, 610), (360, 540), (440, 540), (440, 620), (x1 + 10, 620),
                 (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)], "#8FB4C6")
    inn += blob(rect_pts(284, y0, 306, y1), C_TILE) + blob(rect_pts(x0, 440, x1, 462), C_TILE)
    o.append(shape(rect_pts(x0, y0, x1, y1, 8), C_TILE, inn, w=5, seed=9200))
    o.append(shape(rect_pts(x0 - 24, y1 - 2, x1 + 24, y1 + 26, 6), C_TILE, "", w=4.2, seed=9201))
    # верхние шкафы справа
    for k in range(3):
        xx = 640 + k * 150
        o.append(shape(rect_pts(xx, 200, xx + 146, 560, 6), "#D98C6A", blob(rect_pts(xx + 100, 200, xx + 146, 560), "#B9694C", .8) +
                       blob(rect_pts(xx + 14, 214, xx + 132, 546, 4), "#E5A083", .6), w=4.2, seed=9210 + k))
        o.append(shape(rect_pts(xx + 112 - 30 * (k % 2), 360, xx + 124 - 30 * (k % 2), 430, 4), "#EFE6D6", "", w=3, seed=9220 + k))
    # рейка с половником и лопаткой
    o.append(line([(560, 690), (1120, 690)], 8, INK, taper=.02, wmin=.95, seed=9230))
    o.append(line([(560, 690), (1120, 690)], 4, C_STEEL, taper=.02, wmin=.95, seed=9231))
    for k, (hx, col) in enumerate(((650, C_STEEL), (760, "#C28A52"), (1010, "#8FA8B0"))):
        o.append(line([(hx, 694), (hx, 780)], 6, INK, taper=.05, wmin=.9, seed=9240 + k))
        o.append(line([(hx, 694), (hx, 780)], 3, col, taper=.05, wmin=.9, seed=9250 + k))
        o.append(shape(ellipse_pts(hx, 806, 22, 28, 12), col, "", w=3.4, seed=9260 + k))
    # столешница и нижние шкафчики (кроме места плиты)
    o.append(shape(rect_pts(-1600, 1010, 2800, 1042), C_COUNTER, blob(rect_pts(-1600, 1030, 2800, 1042), "#A8693F"), w=4.6, seed=9270))
    o.append(shape(rect_pts(-1600, 1042, 2800, 1330), "#EFE6D6", "", w=4, seed=9271))
    for k in range(-8, 14):
        if OVEN["x0"] - 190 < k * 190 + 10 < OVEN["x1"]:
            continue
        o.append(shape(rect_pts(k * 190 + 10, 1062, k * 190 + 180, 1300, 6), C_CAB, blob(rect_pts(k * 190 + 130, 1062, k * 190 + 180, 1300), "#E4D8C2", .9),
                       w=3.2, seed=9280 + k))
        o.append(shape(rect_pts(k * 190 + 150, 1090, k * 190 + 160, 1130, 4), C_STEEL_SH, "", w=2.6, seed=9330 + k))
    # чайник слева на столешнице
    o.append(shape([(500, 1008, 1), (610, 1008, 1), (604, 920), (540, 892), (506, 930)], C_STEEL, blob([(580, 1008), (610, 1008), (604, 920), (580, 910)], C_STEEL_SH, .8),
                   w=3.8, seed=9340))
    o.append(shape(rect_pts(548, 884, 566, 898, 3), "#2f3340", "", w=3, seed=9341))
    # пол
    o.append(f'<rect x="-1600" y="1330" width="4400" height="1200" fill="{C_FLOOR}"/>')
    for k, y in enumerate(range(1380, 1740, 62)):
        o.append(line([(-1600, y), (2800, y + 2)], 2.6, "#8F6842", taper=.05, wmin=.9, seed=9350 + k, op=.8))
    o.append(shape(rect_pts(-1600, 1318, 2800, 1344), "#EFE6D6", "", w=4.2, seed=9360))
    o.append(_oven_body())
    return "".join(o)


def _oven_body():
    """Корпус плиты: стальные бока, панель с ручками-кругами, чёрная полость духовки (дверца рисуется отдельно)."""
    X0, X1 = OVEN["x0"], OVEN["x1"]
    cx, cy, cw, ch = OVEN["cav"]
    o = [shape(rect_pts(X0 - 10, 1010, X1 + 10, 1330, 8), C_STEEL, blob(rect_pts(X1 - 50, 1010, X1 + 10, 1330), C_STEEL_SH, .8), w=4.4, seed=9500)]
    # конфорки сверху: две тёмные плоскости на столешнице
    for k, bx in enumerate((X0 + 90, X1 - 90)):
        o.append(shape(ellipse_pts(bx, 1004, 78, 12, 14), "#4a4650", blob(ellipse_pts(bx, 1004, 44, 6, 12), "#2f2b33"), w=3.4, seed=9505 + k))
    # панель с четырьмя ручками
    o.append(shape(rect_pts(X0 + 8, 1040, X1 - 8, 1086, 5), "#E4E7EA", "", w=3.2, seed=9510))
    for k in range(4):
        kx = X0 + 62 + k * 92
        o.append(shape(ellipse_pts(kx, 1063, 17, 17, 14), "#3d3a44", blob(ellipse_pts(kx - 4, 1059, 6, 6, 8), "#6f6b78"), w=3, seed=9520 + k))
        o.append(line([(kx, 1063), (kx + 7, 1054)], 4, "#EDE6D8", taper=0, wmin=1, seed=9530 + k))
    # полость
    o.append(shape(rect_pts(cx, cy, cx + cw, cy + ch, 5), "#2b2630", "", w=4.4, seed=9540))
    for k in range(2):
        yy = cy + 66 + k * 62
        o.append(line([(cx + 10, yy), (cx + cw - 10, yy)], 5, "#7B7682", taper=.02, wmin=.95, seed=9550 + k))
    # ножки-цоколь
    o.append(shape(rect_pts(X0, 1300, X1, 1330, 4), "#7e8590", "", w=3.4, seed=9560))
    return "".join(o)


def oven_glow(open_k, t=0.0):
    """Тёплый свет полости: растёт, пока дверца открыта; рисовать сразу после static(), до лотка и дверцы."""
    if open_k <= 0.02:
        return ""
    cx, cy, cw, ch = OVEN["cav"]
    a = clamp(open_k) * (0.9 + 0.1 * math.sin(t * 9))
    g = lin_grad([(0, "#F6A44E", 1), (1, "#E0652B", 1)], 0, 0, 0, 1)
    o = [f'<rect x="{cx + 3}" y="{cy + 3}" width="{cw - 6}" height="{ch - 6}" rx="4" fill="url(#{g})" opacity="{a:.2f}"/>']
    for k in range(2):
        yy = cy + 66 + k * 62
        o.append(f'<path d="M{cx + 10} {yy} L{cx + cw - 10} {yy}" stroke="#B5451F" stroke-width="5" opacity="{a:.2f}"/>')
    return "".join(o)


def oven_door(open_k):
    """Дверца: шарнир внизу y=hinge. open_k 0 — стоит на полости (окно, ручка-перекладина), 1 — откинута к зрителю (видна внутренняя сторона-серый квадрат,
    ближний край ниже шарнира). Промежуточные — трапеция: ближний край спускается по дуге, ширина растёт (перспектива)."""
    k = clamp(open_k)
    X0, X1, H = OVEN["x0"], OVEN["x1"], OVEN["hinge"]
    a = k * math.pi / 2
    near_y = H - (H - OVEN["door_top"]) * math.cos(a) + 96 * math.sin(a)
    grow = 26 * math.sin(a)
    pts = [(X0 - 6, H, 1), (X1 + 6, H, 1), (X1 + 6 + grow, near_y, 1), (X0 - 6 - grow, near_y, 1)]
    inner = ""
    if k < .5:
        # внешняя сторона: стальная, окно и ручка
        ww = 1 - 2 * k * .5
        wy0 = near_y + (H - near_y) * .16
        wy1 = near_y + (H - near_y) * .66
        inner += blob([(X0 + 34, wy0), (X1 - 34, wy0), (X1 - 34, wy1), (X0 + 34, wy1)], "#3b3643")
        inner += blob([(X0 + 56, wy0 + 14), (X0 + 130, wy0 + 14), (X0 + 96, wy1 - 14), (X0 + 56, wy1 - 14)], "#5b5566", .9)
        inner += line([(X0 + 40, near_y + (H - near_y) * .08), (X1 - 40, near_y + (H - near_y) * .08)], 9, INK, taper=.02, wmin=.95, seed=9570)
        inner += line([(X0 + 40, near_y + (H - near_y) * .08), (X1 - 40, near_y + (H - near_y) * .08)], 4.5, "#E9EBEE", taper=.02, wmin=.95, seed=9571)
    else:
        inner += blob([(X0 + 20, H - 6), (X1 - 20, H - 6), (X1 - 20 + grow, near_y - 8), (X0 + 20 - grow, near_y - 8)], "#AEB4BC", .9)
        inner += line([(X0 + 26, near_y - 14), (X1 - 26 + grow, near_y - 14)], 6, "#7B828B", taper=.02, wmin=.95, seed=9572)
    return shape(pts, C_STEEL, inner, w=4.6, seed=9575)


def table(x0=40, x1=1100, back=TABLE_BACK, front=TABLE_FRONT):
    """Кухонный стол спереди-чуть-сверху: (ножки, крышка+фартук)."""
    legs = []
    for k, x in enumerate((x0 + 40, x1 - 40)):
        legs.append(shape([(x - 20, front + 40, 1), (x + 20, front + 40, 1), (x + 14, FLOOR_Y + 40, 1), (x - 14, FLOOR_Y + 40, 1)], "#A8693F",
                          blob([(x + 4, front + 40), (x + 20, front + 40), (x + 14, FLOOR_Y + 40), (x + 4, FLOOR_Y + 40)], "#7F4B2B", .8), w=3.8, seed=9400 + k))
    top = []
    top.append(shape([(x0 + 30, back, 1), (x1 - 30, back, 1), (x1 + 20, front, 1), (x0 - 20, front, 1)], "#E3B27A",
                     "".join(line([(x0, back + 10 + k * 16), (x1, back + 10 + k * 16)], 2, "#C98F56", taper=.1, wmin=.8, seed=9420 + k, op=.7) for k in range(3)), w=4.4, seed=9410))
    top.append(shape([(x0 - 20, front, 1), (x1 + 20, front, 1), (x1 + 20, front + 50, 1), (x0 - 20, front + 50, 1)], "#BD7F4C",
                     blob(rect_pts(x0 - 20, front + 32, x1 + 20, front + 50), "#8F5A33", .8), w=4.6, seed=9411))
    return "".join(legs), "".join(top)


def light(t=0.0):
    g = lin_grad([(0, "#FFF3C4", .0), (.3, "#FFF3C4", .22), (1, "#FFF3C4", .05)], 0, 0, 0, 1)
    return f'<path d="M90 250 L480 250 L1000 1330 L420 1330 Z" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def motes(t, box=(140, 300, 900, 1250), n=24, seed=11):
    rs = np.random.RandomState(seed)
    o = []
    for i in range(n):
        x0, y0 = rs.uniform(box[0], box[2]), rs.uniform(box[1], box[3])
        sp, ph, r = rs.uniform(10, 24), rs.uniform(0, 6.28), rs.uniform(2.2, 4.4)
        y = box[1] + (y0 - box[1] - sp * t) % (box[3] - box[1])
        x = x0 + 16 * math.sin(t * .7 + ph)
        a = (0.55 + 0.35 * math.sin(t * 2.2 + ph)) * smooth(box[1], box[1] + 80, y) * (1 - smooth(box[3] - 100, box[3], y))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#fff6d8" opacity="{a * .8:.2f}"/>')
    return "".join(o)
