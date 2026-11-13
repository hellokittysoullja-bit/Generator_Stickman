"""s18 (31.90–34.10, клип 31.70–34.30): кот сидит на парковой скамейке рядом с пустым белым листом (петля к началу
ролика); смотрит на лист, на «пустым листом» (32.88) кладёт на него лапу и поворачивается к зрителю, огонёк качается.
Камера медленно отъезжает с первого кадра. Скамейка — спереди, сиденье видно чуть сверху (лист лежит на нём)."""
import math

import numpy as np

import cat_sit
import lib
import park
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape, smooth

T_A, T_B = 31.70, 34.30
T_PAW = 32.88
WOOD, WOOD_SH, WOOD_HI, IRON = "#b9774a", "#8b5535", "#d39563", "#33343c"
CATX, CATY, CATS = 712.0, 1166.0, 1.72


def bg(t):
    cx = 2600 - 10 * (t - T_A)
    s = 1.15
    cy = (960 - 1180) / s
    o = [park.backdrop(cx, cy, s, 0, t)]
    o.append(f'<g transform="{lib.cam(cx, cy, s, 0)}">{park.ground(cx, cy, s, t)}</g>')
    return f'<g {lib.blur(2.4)}>{"".join(o)}</g>'


def bench_back():
    o = []
    for sx in (-1, 1):                         # стойки спинки
        x = 540 + sx * 400
        o.append(shape(lib.rect_pts(x - 14, 760, x + 14, 1130, 5), IRON, blob(lib.rect_pts(x + 2, 760, x + 14, 1130), "#22232a", .9),
                       w=3.6, seed=5000 + sx))
    for k in range(3):                         # доски спинки
        y = 790 + k * 82
        o.append(shape(lib.rect_pts(90, y, 990, y + 62, 10), WOOD,
                       blob(lib.rect_pts(90, y + 42, 990, y + 62), WOOD_SH, .9) + blob(lib.rect_pts(110, y + 8, 960, y + 16, 4), WOOD_HI, .7) +
                       line([(300 + k * 90, y + 22), (360 + k * 90, y + 26)], 2.2, WOOD_SH, seed=5010 + k, op=.8) +
                       line([(720 - k * 60, y + 30), (790 - k * 60, y + 27)], 2.2, WOOD_SH, seed=5020 + k, op=.8), w=4.0, seed=5030 + k))
    return "".join(o)


def bench_seat():
    o = []
    # тень под скамейкой и ножки
    o.append(blob(ellipse_pts(540, 1470, 520, 40, 18), "#2f3a2a", .25, lib.blur(10)))
    for sx in (-1, 1):
        x = 540 + sx * 400
        o.append(shape([(x - 18, 1200, 1), (x - 26, 1462, 1), (x + 4, 1462, 1), (x + 18, 1200, 1)], IRON, "", w=3.6, seed=5040 + sx))
        o.append(shape(lib.rect_pts(x - 36, 1452, x + 22, 1468, 4), IRON, "", w=3, seed=5045 + sx))
    # сиденье: верх (видно сверху) и передний край
    top = [(80, 1108, 1), (1000, 1108, 1), (1028, 1196, 1), (52, 1196, 1)]
    inner = ""
    for k in range(3):
        y0, y1 = 1108 + k * 30, 1108 + k * 30 + 24
        inner += blob([(80 - k * 9, y0), (1000 + k * 9, y0), (1000 + k * 9 + 8, y1), (80 - k * 9 - 8, y1)], WOOD if k % 2 == 0 else "#c27f50")
        inner += blob([(80 - k * 9, y1), (1000 + k * 9 + 8, y1), (1000 + k * 9 + 10, y1 + 6), (80 - k * 9 - 10, y1 + 6)], WOOD_SH, .95)
        inner += line([(240 + k * 140, y0 + 10), (330 + k * 140, y0 + 12)], 2, WOOD_SH, seed=5050 + k, op=.7)
    o.append(shape(top, WOOD, inner, w=4.2, seed=5060))
    o.append(shape(lib.rect_pts(48, 1194, 1032, 1226, 6), WOOD_SH, blob(lib.rect_pts(60, 1198, 1020, 1205, 3), WOOD, .8), w=4.2, seed=5061))
    return "".join(o)


def sheet(t, press):
    """Пустой белый лист на сиденье слева от кота; под лапой чуть проминается."""
    dy = 2 * press
    pts = [(330, 1124 + dy * .3, 1), (536, 1116 + dy, 1), (556, 1178 + dy, 1), (340, 1190 + dy * .3, 1)]
    o = [blob([(p[0] + 8, p[1] + 8) for p in pts], "#4a2e1c", .25, lib.blur(3))]
    inner = blob([(330, 1124), (404, 1122), (396, 1190), (340, 1190)], "#eef0f4", .9)
    o.append(shape(pts, "#fbfaf6", inner, w=3.2, seed=5070))
    # загнутый уголок
    o.append(shape([(536, 1116 + dy, 1), (520, 1122 + dy), (542, 1134 + dy, 1)], "#e6e4dd", "", w=2.4, seed=5071))
    return "".join(o)


def frame(t):
    lib.DEFS.clear()
    z = 1.12 - 0.12 * ease_io(clamp((t - T_A) / (T_B - T_A)))
    reach = smooth(T_PAW - 0.22, T_PAW, t)
    press = math.exp(-8 * max(0, t - T_PAW)) * smooth(T_PAW - .03, T_PAW + .02, t)
    # лапа: от покоя дугой вверх и на лист
    rest = np.array(cat_sit.PAW_REST, float)
    tgt = np.array([cat_sit.CX + (458 - CATX) / CATS, cat_sit.CBOT + (1150 - CATY) / CATS])
    P = rest + (tgt - rest) * ease_out(reach, 2) + np.array([0, -38 * math.sin(math.pi * reach)])
    P = P + np.array([0, 3 * press])
    turn = smooth(T_PAW + 0.05, T_PAW + 0.35, t)
    look = (-0.75 * (1 - turn) + 0.05 * turn, 0.55 * (1 - turn) - 0.05 * turn)
    tilt = -7 * (1 - turn) + 3 * turn * smooth(T_PAW + .3, T_PAW + .7, t) + 1.2 * math.sin(t * 1.4)
    blink = 0.0
    for tb in (32.40, 33.95):
        if abs(t - tb) < .09:
            blink = min(1, 1.7 * (1 - abs(t - tb) / .09))
    tail = 7 * math.sin(t * 2.2 + .5) - 2
    flick = -9 * math.exp(-9 * max(0, t - 31.75)) * math.sin(max(0, t - 31.75) * 30)
    cat = cat_sit.draw(CATX, CATY, CATS, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick,
                       paw=tuple(P) if reach > 0 else None, press=press, shadow=False)
    shadow = blob(ellipse_pts(CATX + 20, CATY - 2, 190, 22, 16), "#3a2010", .3, lib.blur(6))
    body = bg(t) + bench_back() + bench_seat() + sheet(t, press) + shadow + cat
    return lib.svg(f'<g transform="translate(540 1000) scale({z:.4f}) translate(-540 -1000)">{body}</g>')


_ = INK
