"""Кухня рилса 28 (как кухня рилса 26: плитка, полка с банками, красная кофеварка — но вечер: тёплая лампа-абажур,
тёмное окно с луной; столешница глубже, чтобы на ней читались лежащие предметы).
s13: рука Димы (горчичный рукав) приносит телефон и кладёт экраном вниз на столешницу у сахарницы на «кухню» (29.68).
s15: кот сидит у телефона, на «сторожит» (32.16) кладёт на него лапу и сторожит: глаза влево-вправо, ухо, огонёк.
s16: крупно кот у телефона смотрит в камеру и медленно моргает (до 38.1)."""
import math

import numpy as np

import cat
import hand
import lib
from lib import (DEFS, INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg, T)
from parts import sausage

_ST = {}
SKIN, SKIN_SH, SKIN_SH2, NAIL = hand.SKIN, hand.SKIN_SH, hand.SKIN_SH2, hand.NAIL
HOOD, HOOD_SH, FOLD = hand.HOOD, hand.HOOD_SH, hand.FOLD

BK, FR = 1100, 1330           # задний и передний край столешницы
MX0, MX1, MTOP, MBOT = 1620, 2220, 380, 1150
SUGAR = (640, 1215)           # низ-центр сахарницы
PH = (975, 1250)              # центр лежащего телефона
PH_L, PH_D = 290, 76          # длина и видимая глубина (ракурс)
CATP = (1265, 1262, 1.36)     # низ лап кота, масштаб
LAND = 29.68
PAW_T = 32.16


# ─────────────────────────────── кухня
def kitchen():
    s = []
    wall, wall_sh = "#e3c99c", "#c9ab7b"
    s.append(f'<rect x="-1500" y="-2000" width="5600" height="{BK + 2000}" fill="{wall}"/>')
    DEFS.append('<pattern id="pTileE" width="110" height="80" patternUnits="userSpaceOnUse">'
                '<rect width="110" height="80" fill="#f2e1bd"/><rect x="0" y="76" width="110" height="4" fill="#cfb488"/>'
                '<rect x="106" width="4" height="80" fill="#cfb488"/></pattern>')
    s.append(f'<rect x="-1500" y="560" width="5600" height="{BK - 560}" fill="url(#pTileE)"/>')
    s.append(line([(-1500, 560), (4100, 560)], 4, INK, taper=.05, wmin=.9, seed=900))
    # окно: вечер, тёмное небо, луна, звёзды
    sky = lin_grad([(0, "#18223f", 1), (1, "#33466f", 1)], 0, 0, 0, 1)
    x0, x1, y0, y1 = 120, 600, -320, 470
    win = rect_pts(x0, y0, x1, y1, 12)
    inner = f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>'
    inner += blob(ellipse_pts(470, -170, 40, 40, 16), "#f3ead0")
    for k, (x, y) in enumerate([(200, -240), (330, -120), (240, 40), (520, 120), (420, 300), (180, 260)]):
        inner += blob(ellipse_pts(x, y, 4, 4, 6), "#f3ead0")
    # крыши домов напротив с тёплыми окнами
    inner += blob([(x0 - 20, 330), (220, 300), (220, 250), (360, 250), (360, 320), (x1 + 20, 290), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)],
                  "#141a30")
    for k, (x, y) in enumerate([(250, 280), (300, 280), (420, 360), (500, 340)]):
        inner += blob(rect_pts(x, y, x + 26, y + 34), "#f2c46a")
    inner += blob(rect_pts(345, y0, 375, y1), "#e6dccb") + blob(rect_pts(x0, 60, x1, 88), "#e6dccb")
    s.append(shape(win, "#efe6d6", inner, w=5, seed=906))
    s.append(shape(rect_pts(x0 - 26, y1 - 6, x1 + 26, y1 + 34, 6), "#efe6d6", "", w=4.4, seed=907))
    # полка с банками
    s.append(shape(rect_pts(1500, 140, 3000, 172, 4), "#a8794a", "", w=4.4, seed=911))
    for k, (x, hgt, col) in enumerate([(1620, 100, "#8ab6d6"), (2300, 120, "#e9c46a"), (2420, 90, "#9fc5a8"), (2520, 140, "#e07a5f"),
                                       (1060, 0, "")]):
        if not col:
            continue
        s.append(shape(rect_pts(x - 40, 140 - hgt, x + 40, 140, 14), col, blob(rect_pts(x - 40, 140 - hgt, x + 40, 140 - hgt + 24), "#c9c0b0"),
                       w=4, seed=912 + k))
    s.append(shape([(1830, 140, 1), (1950, 140, 1), (1970, 60, 1), (1810, 60, 1)], "#c4673f", "", w=4, seed=918))
    for k in range(5):
        a = -2.2 + k * 0.55
        s.append(line([(1890, 60), (1890 + 90 * math.cos(a), 60 + 110 * math.sin(a))], 18, "#5f9a5a", taper=.6, seed=919 + k))
    # рейлинг с утварью над столешницей (сдвинут вправо от ложечки сахарницы)
    s.append('<g transform="translate(70 0)">')
    s.append(shape(rect_pts(640, 662, 1120, 678, 6), "#b9bec8", blob(rect_pts(640, 672, 1120, 678), "#8e95a5"), w=3.6, seed=1700))
    for k, x in enumerate((660, 1100)):
        s.append(shape(ellipse_pts(x, 670, 14, 14, 10), "#9aa0ab", "", w=3.2, seed=1701 + k))
    # половник
    s.append(line([(760, 676), (754, 700)], 4, INK, seed=1703))
    s.append(shape(rect_pts(744, 698, 764, 900, 8), "#c9ced8", blob(rect_pts(756, 698, 764, 900), "#9aa0ab"), w=3.2, seed=1704))
    s.append(shape(ellipse_pts(754, 930, 46, 38, 16), "#c9ced8", blob(ellipse_pts(764, 940, 34, 28, 12), "#9aa0ab", .9), w=3.8, seed=1705))
    # лопатка деревянная
    s.append(line([(880, 676), (880, 700)], 4, INK, seed=1706))
    s.append(shape(rect_pts(870, 696, 890, 860, 8), "#c48a52", blob(rect_pts(882, 696, 890, 860), "#a06c3a"), w=3.2, seed=1707))
    s.append(shape([(856, 856, 1), (904, 856, 1), (912, 960), (880, 980), (848, 960)], "#c48a52",
                   blob([(884, 856), (904, 856), (912, 960), (884, 976)], "#a06c3a"), w=3.6, seed=1708))
    # венчик
    s.append(line([(1000, 676), (1000, 700)], 4, INK, seed=1709))
    s.append(shape(rect_pts(990, 696, 1010, 800, 8), "#3f9aa8", "", w=3.2, seed=1710))
    for k in (-1, -0.4, 0.4, 1):
        s.append(line([(1000 + k * 6, 800), (1000 + k * 34, 880), (1000 + k * 20, 940), (1000, 952)], 3.2, "#8e95a5", taper=.1, wmin=.8,
                      seed=1711 + int(k * 5)))
    s.append('</g>')
    # столешница сверху (глубина) и кромка
    top = "#c98f5a"
    tp = [(-1500, BK, 1), (4100, BK, 1), (4100, FR, 1), (-1500, FR, 1)]
    inner = "".join(line([(-1500, BK + 40 + k * 46), (4100, BK + 44 + k * 46)], 2.4, "#b27a48", taper=.1, wmin=.7, seed=1930 + k, op=.8)
                    for k in range(4))
    inner += blob(rect_pts(-1500, BK, 4100, BK + 22), "#a8723f", .7)
    s.append(shape(tp, top, inner, w=4.4, seed=910))
    s.append(shape(rect_pts(-1500, FR, 4100, FR + 34), "#a8723f", "", w=4.6, seed=909))
    front = "#e9dcc4"
    inner = "".join(line([(x, FR + 40), (x, 3400)], 4, mix(front, "#000000", .3), taper=.05, wmin=.9, seed=920 + k)
                    for k, x in enumerate(range(-1400, 4100, 520)))
    inner += "".join(shape(rect_pts(x + 230, FR + 120, x + 290, FR + 140, 8), "#b8b0a2", "", w=3, seed=930 + k)
                     for k, x in enumerate(range(-1400, 4100, 520)))
    s.append(shape(rect_pts(-1500, FR + 34, 4100, 3400), front, inner, w=5, seed=940))
    s.append(machine())
    return "".join(s)


def lamp_light():
    """Тёплый свет абажура (за кадром сверху) и мягкая тень к низу."""
    g = rad_grad([(0, "#ffd890", .5), (.55, "#ffbe6a", .18), (1, "#ffbe6a", 0)], 1000, 500, 1500, 1300)
    s = [f'<rect x="-1500" y="-2000" width="5600" height="5400" fill="url(#{g})" style="mix-blend-mode:screen"/>']
    g2 = rad_grad([(0, "#000000", 0), (.6, "#000000", 0), (1, "#2a1606", .35)], 1000, 700, 1700, 1700)
    s.append(f'<rect x="-1500" y="-2000" width="5600" height="5400" fill="url(#{g2})"/>')
    return "".join(s)


def machine():
    s = []
    body, body_sh = "#c9473d", "#9c3029"
    s.append(blob(rect_pts(MX0 + 30, MBOT - 20, MX1 + 60, MBOT + 20), "#1a0e05", .45, blur(14)))
    inner = blob(rect_pts(MX1 - 90, MTOP, MX1 + 10, MBOT), body_sh, .9)
    inner += blob(rect_pts(MX0, MTOP, MX1, MTOP + 30), mix(body, "#ffffff", .25), .9)
    s.append(shape(rect_pts(MX0, MTOP, MX1, MBOT, 46), body, inner, w=5.4, seed=950))
    s.append(shape(rect_pts(MX0 + 70, 790, MX1 - 70, MBOT - 40, 24), "#2b2730", blob(rect_pts(MX0 + 70, 790, MX1 - 70, 850), "#1c1920"),
                   w=4.6, seed=951))
    s.append(shape(rect_pts(MX0 + 50, MBOT - 110, MX1 - 50, MBOT - 50, 10), "#9aa0ab",
                   "".join(line([(x, MBOT - 104), (x, MBOT - 58)], 3, "#6d737e", taper=.05, wmin=.9, seed=960 + k) for k, x in
                           enumerate(range(MX0 + 90, MX1 - 60, 36))), w=4.4, seed=961))
    sx = (MX0 + MX1) / 2 + 40
    s.append(shape(rect_pts(sx - 90, 790, sx + 90, 822, 8), "#b9bec8", "", w=4, seed=962))
    s.append(shape([(sx - 30, 822, 1), (sx + 30, 822, 1), (sx + 14, 860, 1), (sx - 14, 860, 1)], "#9aa0ab", "", w=3.6, seed=963))
    for k in range(3):
        y = 490 + k * 82
        s.append(shape(ellipse_pts(MX1 - 120, y, 30, 30, 14), "#f1ece3", blob(ellipse_pts(MX1 - 114, y + 6, 22, 20, 10), "#d4ccbf"), w=3.6,
                       seed=970 + k))
    s.append(shape(ellipse_pts(MX1 - 120, 735, 11, 11, 10), "#7dff9a", "", w=2.6, seed=980))
    return "".join(s)


def sugar():
    """Сахарница: белый фаянс с синими цветочками, крышка с шишечкой и прорезью, ложечка."""
    x, y = SUGAR
    s = [blob(ellipse_pts(x + 14, y + 4, 128, 20, 16), "#1a0e05", .35, blur(6))]
    # ложечка за крышкой
    s.append(line([(x + 50, y - 200), (x + 82, y - 262)], 12, INK, taper=.05, wmin=.9, seed=1801))
    s.append(line([(x + 50, y - 200), (x + 82, y - 262)], 6, "#c9ced8", taper=.05, wmin=.9, seed=1802))
    s.append(shape(ellipse_pts(x + 86, y - 272, 12, 17, 12, rot=25), "#c9ced8", "", w=3, seed=1803))
    body = [(x - 112, y - 150), (x - 118, y - 90), (x - 98, y - 26), (x - 60, y, 1), (x + 60, y, 1), (x + 98, y - 26), (x + 118, y - 90),
            (x + 112, y - 150)]
    inner = blob([(x + 40, y - 160), (x + 120, y - 160), (x + 120, y), (x + 50, y)], "#d8dde6", .9)
    inner += blob([(x - 96, y - 140), (x - 80, y - 140), (x - 70, y - 40), (x - 86, y - 40)], "#ffffff", .9)
    for k, (cx, cy) in enumerate([(x - 50, y - 90), (x + 10, y - 70), (x + 66, y - 104), (x - 10, y - 126)]):
        for j in range(5):
            a = j * 2 * math.pi / 5 + k
            inner += blob(ellipse_pts(cx + 11 * math.cos(a), cy + 11 * math.sin(a), 7, 7, 8), "#3a6fc0")
        inner += blob(ellipse_pts(cx, cy, 5, 5, 8), "#f2c23a")
    s.append(shape(body, "#f6f3ec", inner, w=5, seed=1804))
    lid = ellipse_pts(x, y - 152, 122, 24, 20)
    s.append(shape(lid, "#eef0f4", blob(ellipse_pts(x + 30, y - 146, 90, 14, 14), "#d8dde6", .9), w=4.6, seed=1805))
    s.append(shape(ellipse_pts(x, y - 176, 24, 18, 14), "#f6f3ec", blob(ellipse_pts(x + 8, y - 172, 16, 12, 10), "#d8dde6"), w=4, seed=1806))
    s.append(line([(x + 36, y - 162), (x + 60, y - 160)], 4, INK, seed=1807))
    return "".join(s)


def phone_lying(cx, cy, rot=0.0, lift=0.0):
    """Телефон экраном вниз на столешнице (вид спереди-сверху): верхняя грань — тёмная спинка с камерой, видна кромка."""
    L, D = PH_L, PH_D
    th = 13
    s = []
    if lift < 0.5:
        s.append(blob(ellipse_pts(cx + 8, cy + D / 2 + 6, L / 2 + 10, 12, 16), "#1a0e05", .4 * (1 - lift * 2), blur(6)))
    P = lambda pts: T(pts, cx, cy - lift * 140, 1.0, rot)
    edge = [(-L / 2, -D / 2 + 10), (L / 2, -D / 2 + 10), (L / 2, D / 2 + th - 8, 1), (L / 2 - 14, D / 2 + th, 1), (-L / 2 + 14, D / 2 + th, 1),
            (-L / 2, D / 2 + th - 8, 1)]
    s.append(shape(P(edge), "#565c6c", "", w=4.2, seed=1820))
    top = P(rect_pts(-L / 2, -D / 2, L / 2, D / 2, 18))
    inner = blob(P([(-L / 2, D / 2 - 12), (L / 2, D / 2 - 12), (L / 2, D / 2), (-L / 2, D / 2)]), "#232733", .9)
    inner += line(P([(-L / 2 + 40, -D / 2 + 14), (L / 2 - 70, -D / 2 + 12)]), 4, "#6b7388", seed=1821, op=.9)
    s.append(shape(top, "#353a48", inner, w=4.4, seed=1822))
    # блок камеры у левого края
    s.append(shape(P(rect_pts(-L / 2 + 16, -D / 2 + 12, -L / 2 + 74, -D / 2 + 46, 10)), "#2a2e3a", "", w=3, seed=1823))
    for k, (u, v) in enumerate([(-L / 2 + 31, -D / 2 + 22), (-L / 2 + 55, -D / 2 + 22), (-L / 2 + 31, -D / 2 + 37)]):
        s.append(shape(P(ellipse_pts(u, v, 8, 6, 10)), "#14161d", blob(P(ellipse_pts(u - 2, v - 1, 3, 2, 6)), "#8fa0c8"), w=2.2, seed=1824 + k))
    return "".join(s)


# ─────────────────────────────── рука, кладущая телефон (правая, со спины кисти, пальцы от нас)
def lay_hand(x, y, sc, rot, fsq=0.8, curl=0.0):
    """Кисть тыльной стороной к зрителю, пальцы вперёд (от нас, вверх по экрану, в ракурсе fsq), большой палец слева,
    рукав уходит вниз-вправо за кадр. (x, y) — середина костяшек."""
    s = []

    def P(pts, sy=1.0):
        return T([(p[0], p[1] * sy) + tuple(p[2:]) for p in pts], x, y, sc, rot)
    # рукав (длинный, за кадр)
    sl = [(-118, 150, 1), (108, 140, 1), (420, 1300, 1), (-60, 1360, 1)]
    s.append(shape(P(sl), HOOD, blob(P([(40, 150), (108, 140), (420, 1300), (180, 1330)]), HOOD_SH, .9) +
                   line(P([(-40, 280), (30, 600), (60, 900)]), 4, FOLD, seed=1010, op=.7) +
                   line(P([(60, 320), (150, 560)]), 3.4, FOLD, seed=1013, op=.6), w=5.2, seed=1011))
    s.append(shape(P([(-126, 116, 1), (114, 106, 1), (122, 176, 1), (-120, 186, 1)]), HOOD_SH,
                   "".join(line(P([(-100 + k * 40, 122), (-100 + k * 40, 180)]), 2.6, FOLD, seed=1020 + k, op=.8) for k in range(6)),
                   w=4.6, seed=1012))
    # большой палец слева, вдоль края телефона
    th = sausage(P([(-80, 50), (-118, 10), (-136, -34)], fsq + .2), 50 * sc, 40 * sc)
    s.append(shape(th, SKIN, "", w=4.4, seed=1030))
    # пальцы вперёд (в ракурсе), кончики загибаются за дальний край
    fl = fsq * (1 - 0.25 * curl)
    fingers = [(-62, 118, 42), (-20, 134, 44), (22, 126, 42), (60, 98, 36)]
    for k, (fx, L_, w_) in enumerate(fingers):
        tip = (fx + (k - 1.5) * 5, -L_)
        sp = sausage(P([(fx, 20), (fx + (k - 1.5) * 2.5, -L_ * 0.5), tip], fl), w_ * sc, w_ * 0.9 * sc)
        inner = line(P([(fx - w_ * .3, -L_ * 0.45), (fx + w_ * .3, -L_ * 0.45)], fl), 2.4, SKIN_SH2, seed=1040 + k, op=.8)
        s.append(shape(sp, SKIN, inner, w=4.2, seed=1060 + k))
        nx, ny = P([(tip[0], tip[1] + w_ * 0.5)], fl)[0]
        s.append(shape(ellipse_pts(nx, ny, w_ * 0.3 * sc, w_ * 0.28 * sc, 10, rot=rot), NAIL, "", w=2, seed=1070 + k))
    back = [(-92, 6), (-40, -6), (20, -8), (86, 2), (100, 50), (88, 130), (0, 140), (-90, 136), (-104, 64)]
    inner = blob(P([(40, 0), (96, 56), (90, 130), (30, 136)]), SKIN_SH, .9)
    for k in range(4):
        fx = fingers[k][0]
        inner += line(P([(fx - 10, 6), (fx, -2), (fx + 10, 6)]), 2.6, SKIN_SH2, seed=1080 + k, op=.8)
    inner += line(P([(-30, 40), (-20, 110)]), 2.4, SKIN_SH2, seed=1090, op=.6)
    inner += line(P([(20, 40), (14, 110)]), 2.4, SKIN_SH2, seed=1091, op=.6)
    s.append(shape(P(back), SKIN, inner, w=5, seed=1092))
    return "".join(s)


# ─────────────────────────────── s13
def frame13(t):
    s = [_ST["kit"], _ST["sugar"]]
    e = t - LAND
    # путь телефона: от нижнего правого угла к месту у сахарницы, плавно опускается
    if e < 0:
        u = clamp((t - 26.6) / (LAND - 26.6))
        k = ease_io(u) * 0.75 + 0.25 * u
        p0, p1, p2 = np.array([1420.0, 1820.0]), np.array([1180.0, 980.0]), np.array([PH[0], PH[1]])
        q = (1 - k) ** 2 * p0 + 2 * (1 - k) * k * p1 + k * k * p2
        # над местом зависает и опускается
        drop = smooth(LAND - 0.45, LAND, t)
        cx, cy = q
        cy = cy - 70 * (1 - drop) * smooth(LAND - 0.9, LAND - 0.45, t)
        rot = -14 * (1 - k) + 4 * math.sin(t * 2.4) * (1 - drop)
        lift = 0.0
        ph = phone_lying(cx, cy, rot)
        hx, hy, hrot = cx + 70, cy + 40, rot - 6
        hand_a = lay_hand(hx, hy, 0.92, hrot, curl=0.0)
        s.append(ph)
        s.append(hand_a)
    else:
        # приземлился: лёгкий отскок, рука отпускает и уходит к зрителю (вниз-вправо)
        b = 6 * math.exp(-e * 12) * math.sin(e * 40)
        s.append(phone_lying(PH[0], PH[1] - max(0, b), 0.0))
        if e < 0.9:
            k = ease_in(clamp((e - 0.08) / 0.62), 2)
            hx, hy = PH[0] + 70 + 420 * k, PH[1] + 40 + 900 * k
            s.append(lay_hand(hx, hy, 0.92 + 0.25 * k, -6 + 12 * k, curl=clamp(e / 0.15)))
        if e < 0.3:
            a = 1 - e / 0.3
            for k in range(6):
                sx = -1 if k < 3 else 1
                yy = PH[1] + 30 - (k % 3) * 22
                x0 = PH[0] + sx * (PH_L / 2 + 16 + 40 * ease_out(e / .3))
                s.append(line([(x0, yy), (x0 + sx * 46 * a, yy - 6 * (k % 3))], 6 * a + 1, INK, taper=.5, seed=1100 + k))
    s.append(_ST["light"])
    u = clamp((t - 26.81) / 3.76)
    cx = 960 - 50 * ease_io(u)
    cy = 1060 + 30 * ease_io(u)
    sc = 1.2 + 0.1 * u
    rot = -1.5 + 1.5 * u
    if e >= 0:
        kk = math.exp(-e * 9)
        cy += 6 * kk * math.sin(e * 50)
        sc *= 1 + 0.02 * kk
    return "".join(s), cam(cx, cy, sc, rot)


# ─────────────────────────────── s15 / s16: кот
def paw_on_phone(t):
    """Точка левой передней лапы (внутр. коорд. кота): подъём → дуга → ложится на телефон к PAW_T, чуть прижимает."""
    x, y, sc = CATP
    tgt_w = (PH[0] + PH_L / 2 - 52, PH[1] - 6)
    tgt = cat.to_int(tgt_w, x, y, sc)
    rest = cat.PAW_REST
    a0 = PAW_T - 0.34
    u = clamp((t - a0) / (PAW_T - a0))
    k = ease_io(u)
    px = rest[0] + (tgt[0] - rest[0]) * k
    py = rest[1] + (tgt[1] - rest[1]) * k - 46 * math.sin(math.pi * u) ** 1.2
    press = 0.0
    if t >= PAW_T:
        e = t - PAW_T
        press = math.exp(-e * 10) * abs(math.sin(e * 30))
        py += 3 * press
        # похлопывает ещё раз
        if 0.55 < e < 0.95:
            v = (e - 0.55) / 0.4
            py -= 14 * math.sin(math.pi * v)
    return (px, py), press


def cat_state(t):
    """Взгляд, наклон, хвост, ухо, моргания по времени (s15 → s16 непрерывно)."""
    look = (0.0, 0.0)
    tilt = 0.0
    blink = 0.0
    # s15: до лапы кот смотрит на телефон, после — сторожит: влево, вправо, в камеру
    if t < 33.0:
        k = smooth(31.55, 31.8, t)
        look = (-0.9 * k + 0.3 * (1 - k), 0.5 * k)
        tilt = -4 * k
        g = smooth(32.45, 32.62, t) - smooth(32.9, 33.05, t)
        look = (look[0] * (1 - g) + 0.95 * g, look[1] * (1 - g) + 0.1 * g)
        tilt = tilt * (1 - g) + 3 * g
    if t >= 32.9:
        k = smooth(32.9, 33.2, t)
        look = (0.95 * (1 - k) - 0.05 * k, 0.1 * (1 - k))
        tilt = 3 * (1 - k) + 0 * k
    if t >= 33.4:
        k = smooth(33.4, 33.7, t)
        look = (-0.05 * (1 - k), 0.0)
        tilt = 2.5 * k * (1 - smooth(37.2, 37.8, t)) + 1.0 * math.sin((t - 33.4) * 0.9) * k
    # моргания: обычное в s15, медленные в s16
    for c, half, hold in ((31.95, 0.07, 0.0), (35.2, 0.42, 0.32), (37.15, 0.36, 0.22)):
        a = c - half
        if a <= t <= c + hold + half:
            if t < c:
                blink = ease_io((t - a) / half)
            elif t < c + hold:
                blink = 1.0
            else:
                blink = 1 - ease_io((t - c - hold) / half)
    tail = 5 * math.sin(t * 1.9) + 2.5 * math.sin(t * 3.3 + 1)
    flick = 0.0
    for c in (32.75, 34.6, 36.6):
        e = t - c
        if 0 <= e < 0.5:
            flick += -14 * math.exp(-e * 9) * math.sin(e * 34) * (1 if e < 0.3 else 1)
    return dict(look=look, tilt=tilt, blink=blink, tail=tail, flick=flick)


def frame_cat(sid, t):
    s = [_ST["kit"], _ST["sugar"], phone_lying(PH[0], PH[1])]
    x, y, sc = CATP
    st = cat_state(t)
    P, press = paw_on_phone(t)
    s.append(_ST["light"])
    # огонёк светит тёплым пятном на стену и столешницу (под котом — кот остаётся чёрным)
    fx, fy = cat.flame_world(x, y, sc, st["tail"])
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g = rad_grad([(0, "#ffb050", .34 * fl), (1, "#ffb050", 0)], fx, fy, 300, 300)
    s.append(f'<rect x="{f(fx - 320)}" y="{f(fy - 320)}" width="640" height="640" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(cat.draw(x, y, sc, t, paw=P, press=press, **st))
    if sid == "s15":
        u = clamp((t - 31.6) / 2.5)
        cx, cy = 1175 + 20 * ease_io(u), 1010 + 15 * ease_io(u)
        scc = 1.42 + 0.1 * u
        rot = 1.2 - 1.0 * u
        e = t - PAW_T
        if e >= 0:
            kk = math.exp(-e * 8)
            scc *= 1 + 0.04 * kk * math.sin(min(e * 12, math.pi))
            cy += 5 * kk * math.sin(e * 45)
    else:
        u = clamp((t - 33.69) / (38.1 - 33.69))
        hc = cat.to_world((836, 1090), x, y, sc)
        cx = hc[0] + 10 + 30 * u
        cy = hc[1] + 150 - 20 * u
        scc = 2.05 + 0.3 * (0.4 * u + 0.6 * ease_io(u))
        rot = -0.8 + 1.4 * u
    return "".join(s), cam(cx, cy, scc, rot)


def frame(sid, t):
    if not _ST:
        _ST["kit"] = kitchen()
        _ST["sugar"] = sugar()
        _ST["light"] = lamp_light()
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    if sid == "s13":
        art, cm = frame13(t)
    else:
        art, cm = frame_cat(sid, t)
    return svg(f'<rect width="{W}" height="{H}" fill="#e3c99c"/><g transform="{cm}">{art}</g>')
