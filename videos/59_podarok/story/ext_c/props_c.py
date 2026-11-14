"""Предметы группы C рилса 59 (запасные, пока нет common/props.py): подарочная коробка, торт со свечой, корзина и шесть вещей.
Точка (x, y) — центр дна. Все заливки сплошные, тушь INK. Без букв и цифр."""
import math

import lib
from lib import INK, blob, ellipse_pts, f, line, rect_pts, shape

C_BOX, C_BOX_SH, C_LID, C_LID_SH = "#2FA8A2", "#23857F", "#3BBDB6", "#2A9791"
C_RIB, C_RIB_SH = "#F6C445", "#D9A22A"
C_CREAM, C_CREAM_SH = "#FBF6EA", "#E8DFC9"
C_SPONGE, C_SPONGE_SH = "#E9BC7C", "#C99857"
C_FROST, C_FROST_SH = "#F8B7CA", "#E48FAA"
C_BASKET, C_BASKET_SH, C_BASKET_DK = "#B98A50", "#946B36", "#5A3E1E"


def tf(inner, x, y, k=1.0, rot=0.0, sx=1.0, sy=1.0):
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k * sx:.4f} {k * sy:.4f})">{inner}</g>'


def bow(cx, cy, wob=0.0, k=1.0):
    """Бант: две петли, узел, два хвоста. wob — покачивание в градусах."""
    o = []
    o.append(shape([(cx - 20, cy), (cx - 40 * k, cy + 70 * k), (cx - 70 * k, cy + 96 * k), (cx - 4, cy + 22 * k)], C_RIB_SH, w=4, seed=71))
    o.append(shape([(cx + 20, cy), (cx + 40 * k, cy + 70 * k), (cx + 74 * k, cy + 90 * k), (cx + 4, cy + 22 * k)], C_RIB_SH, w=4, seed=72))
    L = [(cx - 14, cy - 4), (cx - 60 * k, cy - 70 * k, 1), (cx - 130 * k, cy - 80 * k), (cx - 150 * k, cy - 20 * k), (cx - 90 * k, cy + 18 * k)]
    R = [(cx + 14, cy - 4), (cx + 60 * k, cy - 70 * k, 1), (cx + 130 * k, cy - 80 * k), (cx + 150 * k, cy - 20 * k), (cx + 90 * k, cy + 18 * k)]
    for pts, sd in ((L, 73), (R, 74)):
        o.append(shape(pts, C_RIB, blob([(p[0] + (10 if pts is L else -10), p[1] + 10) for p in pts[2:]] + [(cx, cy + 8)], C_RIB_SH, .8), w=4.6, seed=sd))
    o.append(shape(ellipse_pts(cx, cy + 2, 30 * k, 26 * k, 14), C_RIB, blob(ellipse_pts(cx + 8, cy + 10, 20 * k, 14 * k, 10), C_RIB_SH), w=4.6, seed=75))
    return f'<g transform="rotate({f(wob)} {f(cx)} {f(cy + 20)})">{"".join(o)}</g>'


def gift_box(x, y, k=1.0, sx=1.0, sy=1.0, rot=0.0, wob=0.0, lid_up=0.0):
    """Коробка: тело 340×230, крышка шире, лента крест-накрест, бант."""
    o = []
    o.append(shape(rect_pts(-170, -230, 170, 0, 8), C_BOX, blob(rect_pts(70, -230, 170, 0), C_BOX_SH, .9), w=6, seed=61))
    o.append(shape(rect_pts(-34, -230, 34, 0), C_RIB, blob(rect_pts(14, -230, 34, 0), C_RIB_SH), w=4.6, seed=62))
    ly = -230 - lid_up
    o.append(shape(rect_pts(-190, ly - 74, 190, ly, 10), C_LID, blob(rect_pts(90, ly - 74, 190, ly), C_LID_SH, .9) + blob(rect_pts(-190, ly - 74, -120, ly - 56), "#6FD3CD", .8), w=6, seed=63))
    o.append(shape(rect_pts(-34, ly - 74, 34, ly), C_RIB, blob(rect_pts(14, ly - 74, 34, ly), C_RIB_SH), w=4.6, seed=64))
    o.append(bow(0, ly - 74, wob, 1.0))
    return tf("".join(o), x, y, k, rot, sx, sy)


def flame(cx, cy, t, size=1.0, seed=0):
    fl = math.sin(t * 23 + seed) * .06 + math.sin(t * 37) * .04
    h = 70 * size * (1 + fl)
    w = 26 * size
    sw = 7 * math.sin(t * 17 + seed) * size
    o = [blob([(cx, cy), (cx - w, cy - h * .38), (cx - w * .25 + sw, cy - h * .85), (cx + sw * 1.4, cy - h, 1), (cx + w * .5 + sw, cy - h * .6), (cx + w, cy - h * .3)], "#FF9F1C")]
    o.append(blob([(cx, cy - 2), (cx - w * .55, cy - h * .3), (cx + sw * .6, cy - h * .72), (cx + w * .5, cy - h * .3)], "#FFE066"))
    o.append(blob(ellipse_pts(cx, cy - h * .2, w * .22, h * .12, 8), "#FFFFFF"))
    return "".join(o)


def cake(x, y, k=1.0, sx=1.0, sy=1.0, rot=0.0, flame_u=0.0, t=0.0):
    """Двухъярусный торт на блюде со свечой. flame_u 0…1 — рост огонька."""
    o = []
    o.append(shape(ellipse_pts(0, -12, 290, 40, 30), "#EFEAE0", blob(ellipse_pts(30, -4, 250, 26, 24), "#CFC8B8"), w=5.5, seed=81))
    # нижний ярус
    o.append(shape(rect_pts(-230, -190, 230, -20, 22), C_SPONGE, blob(rect_pts(110, -190, 230, -20), C_SPONGE_SH, .9) + "".join(
        line([(-200 + 70 * i, -118), (-170 + 70 * i, -108), (-140 + 70 * i, -120)], 3, C_SPONGE_SH, seed=90 + i) for i in range(7)), w=6, seed=82))
    drips = [(-244, -200), (-244, -170, 1), (-230, -120), (-210, -118), (-198, -200)]
    fr = [(-250, -200), (-250, -160), (-228, -150), (-200, -158), (-172, -198)]
    # glaze: волнистая глазурь по верху яруса
    gl = [(-236, -214), (236, -214), (240, -176), (210, -150), (196, -176), (150, -140), (120, -176), (66, -150), (36, -184), (-10, -140), (-52, -180), (-100, -146), (-140, -178), (-190, -140), (-228, -176)]
    o.append(shape(gl, C_FROST, blob(rect_pts(120, -214, 240, -150), C_FROST_SH, .8), w=6, seed=83))
    # верхний ярус
    o.append(shape(rect_pts(-140, -300, 140, -204, 16), C_SPONGE, blob(rect_pts(60, -300, 140, -204), C_SPONGE_SH, .9), w=6, seed=84))
    gl2 = [(-150, -316), (150, -316), (152, -276), (120, -246), (104, -280), (56, -240), (24, -282), (-30, -244), (-62, -282), (-108, -246), (-134, -278)]
    o.append(shape(gl2, C_FROST, blob(rect_pts(70, -316, 150, -244), C_FROST_SH, .8), w=6, seed=85))
    for i, cx in enumerate((-96, -30, 36, 100)):
        o.append(shape(ellipse_pts(cx, -322, 15, 13, 10), "#E0343C", blob(ellipse_pts(cx - 4, -326, 5, 4, 6), "#FF9AA0"), w=3.6, seed=95 + i))
    # свеча
    o.append(shape(rect_pts(-13, -420, 13, -318, 3), "#FDF3DD", "".join(blob(rect_pts(-13, -400 + 28 * j, 13, -386 + 28 * j), "#5BA7E8") for j in range(3)), w=4.4, seed=86))
    o.append(line([(0, -420), (0, -432)], 3, INK, seed=97))
    if flame_u > 0:
        s = min(1.0, flame_u)
        o.append(flame(0, -434, t, 1.35 * s, 2))
    return tf("".join(o), x, y, k, rot, sx, sy)


# ═════════════════════════ корзина и шесть вещей ═════════════════════════
BW, BH_RIM, BDEPTH = 330.0, 56.0, 250.0   # полуширина устья, полувысота эллипса устья, глубина


def basket_back(x, y_rim, k, sy=1.0):
    """Задняя часть: тёмное нутро устья и задняя стенка. y_rim — центр эллипса устья."""
    o = []
    o.append(shape(ellipse_pts(0, 0, BW, BH_RIM, 34), C_BASKET_DK, "", w=6, seed=101))
    return tf("".join(o), x, y_rim, k, 0, 1, sy)


def basket_front(x, y_rim, k, sy=1.0, t=0.0, bulge=0.0):
    """Передняя стенка корзины (рисуется ПОВЕРХ вещей): плетёные пояса и передняя дуга ободка."""
    arc = [(BW * math.cos(a), BH_RIM * math.sin(a)) for a in [math.pi * i / 14 for i in range(15)]]
    bw2 = 250 + 22 * bulge
    body = arc + [(bw2 + 18, BDEPTH * .55, 0), (bw2 - 20, BDEPTH), (-bw2 + 20, BDEPTH), (-bw2 - 18, BDEPTH * .55, 0)]
    inner = ""
    for j in range(7):
        yy = 30 + 30 * j
        inner += blob([(-340, yy), (340, yy), (340, yy + 14), (-340, yy + 14)], C_BASKET_SH, .55)
        for i in range(-8, 9):
            xo = i * 46 + (23 if j % 2 else 0)
            inner += line([(xo - 10, yy - 12), (xo + 2, yy + 14)], 3.2, "#6B4A22", seed=110 + i + j * 7, op=.8)
    inner += blob(rect_pts(150, 0, 360, BDEPTH), C_BASKET_SH, .5)
    o = [shape(body, C_BASKET, inner, w=6.4, seed=102)]
    rim = [(BW * math.cos(a), BH_RIM * math.sin(a)) for a in [math.pi * i / 16 for i in range(17)]]
    o.append(line(rim, 26, "#8A5F2E", taper=0.1, wmin=.9, seed=103))
    o.append(line([(p[0], p[1] - 10) for p in rim], 5, "#D9AB6C", taper=.3, wmin=.4, seed=104, op=.9))
    o.append(line(rim, 4.4, INK, taper=.1, wmin=.9, seed=105, op=.9))
    return tf("".join(o), x, y_rim, k, 0, 1, sy)


# --- вещи (низ-центр в 0,0, рост вверх), размер ~ 200 px ---
def book():
    o = []
    o.append(shape(rect_pts(-96, -150, 96, 0, 6), "#3C6FB0", blob(rect_pts(-96, -150, -66, 0), "#2C558A", .9), w=6, seed=121))
    o.append(shape(rect_pts(-84, -138, 90, -10, 3), "#F7F1E1", "".join(line([(-76, -124 + 16 * j), (84, -124 + 16 * j)], 2.4, "#C9BFA6", seed=122 + j, op=.9) for j in range(8)), w=3.6, seed=123))
    o.append(shape(rect_pts(-96, -156, 90, -138, 4), "#3C6FB0", blob(rect_pts(-96, -156, 90, -150), "#6A97D2", .8), w=5.4, seed=124))
    o.append(shape([(30, -156), (46, -156), (46, -70), (38, -84), (30, -70)], "#E0494A", w=3.4, seed=125))
    o.append(shape(ellipse_pts(-30, -90, 20, 20, 12), "#F6C445", blob(ellipse_pts(-24, -84, 12, 12, 8), "#D9A22A"), w=3.6, seed=126))
    return "".join(o)


def sneaker():
    o = []
    sole = [(-120, -26), (110, -26), (122, -12, 1), (110, 0), (-110, 0), (-122, -12, 1)]
    o.append(shape(sole, "#F4F1EA", blob(rect_pts(-120, -8, 120, 0), "#CFC8BA"), w=5.4, seed=131))
    up = [(-118, -26), (-114, -100), (-100, -126), (-62, -122), (-36, -100), (-6, -84), (40, -66), (96, -52), (118, -36), (118, -26)]
    o.append(shape(up, "#E0494A", blob([(-118, -60), (118, -60), (118, -26), (-118, -26)], "#B93438", .75), w=5.8, seed=132))
    o.append(shape([(60, -62), (118, -40), (118, -26), (50, -26)], "#F4F1EA", w=4.4, seed=133))
    o.append(shape([(-118, -100), (-100, -128), (-62, -124), (-60, -96), (-118, -92)], "#B93438", w=4.4, seed=134))
    for i in range(3):
        a = (-30 + 28 * i, -98 + 12 * i)
        o.append(line([(a[0] - 10, a[1] - 4), (a[0] + 14, a[1] + 8)], 7, "#FFFFFF", seed=135 + i, taper=.2, wmin=.8))
        o.append(line([(a[0] - 10, a[1] - 4), (a[0] + 14, a[1] + 8)], 2.2, INK, seed=140 + i, taper=.2, wmin=.8, op=.7))
    o.append(shape([(-4, -84), (22, -92), (44, -78), (40, -62), (10, -66)], "#F4F1EA", w=3.6, seed=138))
    return "".join(o)


def teapot():
    o = []
    o.append(shape([(-84, -20), (-96, -80), (-72, -140, 1), (0, -156), (72, -140, 1), (96, -80), (84, -20)], "#F2C14E", blob([(40, -150), (96, -80), (84, -20), (30, -20)], "#D9A12E", .9) + blob(ellipse_pts(-44, -100, 14, 30, 10, rot=15), "#FFE9A6"), w=6, seed=151))
    o.append(shape(rect_pts(-84, -26, 84, 0, 8), "#D9A12E", w=5, seed=152))
    o.append(shape([(-66, -140), (0, -168), (66, -140)], "#F9D677", w=5, seed=153))
    o.append(shape(ellipse_pts(0, -176, 16, 14, 10), "#B6352F", w=4.4, seed=154))
    o.append(shape([(92, -96), (124, -140), (156, -164, 1), (142, -178), (110, -150), (88, -122)], "#F2C14E", w=5, seed=155))
    o.append(line([(-82, -120), (-142, -120), (-146, -50), (-84, -52)], 17, INK, seed=156, taper=.15, wmin=.9))
    o.append(line([(-82, -120), (-142, -120), (-146, -50), (-84, -52)], 9, "#3B2F2A", seed=157, taper=.15, wmin=.9))
    return "".join(o)


def scarf():
    o = []
    pts = [(-130, -70), (-70, -96), (0, -78), (70, -100), (132, -76), (136, -20), (70, -2), (0, -22), (-70, 0), (-132, -22)]
    inner = "".join(blob([(-130 + 62 * i - 6, -110), (-130 + 62 * i + 12, -110), (-130 + 62 * i + 12, 10), (-130 + 62 * i - 6, 10)], "#FBF1D8", .95) for i in range(0, 5, 2))
    o.append(shape(pts, "#D64550", inner, w=6, seed=161))
    for i in range(7):
        xx = -120 + 40 * i
        o.append(line([(xx, -4), (xx + 4, 20), (xx - 2, 34)], 7, "#D64550", seed=165 + i, taper=.3, wmin=.7))
        o.append(line([(xx, -4), (xx + 4, 20), (xx - 2, 34)], 2.2, INK, seed=175 + i, taper=.3, wmin=.7, op=.8))
    return "".join(o)


def lamp():
    o = []
    o.append(shape(ellipse_pts(0, -12, 74, 14, 14), "#3F8F5A", w=5, seed=181))
    o.append(shape([(-18, -14), (-14, -150), (14, -150), (18, -14)], "#4CA36B", blob(rect_pts(4, -150, 18, -14), "#357F4D"), w=5, seed=182))
    o.append(shape(ellipse_pts(0, -150, 24, 20, 10), "#4CA36B", w=4.4, seed=183))
    o.append(shape([(-56, -160), (56, -160), (96, -260, 1), (-96, -260, 1)], "#FBE6A2", blob([(30, -160), (56, -160), (96, -260), (60, -260)], "#E9C971", .8) + blob([(-70, -230), (-40, -230), (-34, -200), (-60, -200)], "#FFF5CC", .8), w=6, seed=184))
    o.append(line([(-92, -262), (92, -262)], 5, INK, seed=185, taper=.2, wmin=.9))
    return "".join(o)


def teddy():
    br, bd = "#A8714A", "#855536"
    o = []
    for sx_ in (-1, 1):
        o.append(shape(ellipse_pts(sx_ * 84, -218, 34, 34, 12), br, shape(ellipse_pts(sx_ * 84, -214, 16, 16, 10), "#E8B89A", w=0, ink=False), w=5.4, seed=191 + sx_))
    o.append(shape([(-104, -120), (-72, -30), (-40, 0), (40, 0), (72, -30), (104, -120), (60, -150), (-60, -150)], br, blob([(40, -150), (104, -120), (72, -30), (40, 0)], bd, .8), w=6, seed=193))
    o.append(shape(ellipse_pts(0, -76, 46, 54, 14), "#E8C9A4", w=4.6, seed=194))
    o.append(shape(ellipse_pts(-102, -88, 22, 40, 10, rot=25), br, w=5, seed=195))
    o.append(shape(ellipse_pts(102, -88, 22, 40, 10, rot=-25), br, w=5, seed=196))
    o.append(shape(ellipse_pts(-52, -8, 34, 24, 10), br, w=5, seed=197))
    o.append(shape(ellipse_pts(52, -8, 34, 24, 10), br, w=5, seed=198))
    o.append(shape(ellipse_pts(0, -200, 92, 78, 22), br, blob(ellipse_pts(30, -178, 76, 54, 14, rot=-8), bd, .55), w=6.4, seed=199))
    o.append(shape(ellipse_pts(0, -176, 40, 30, 14), "#E8C9A4", w=4.6, seed=200))
    o.append(shape(ellipse_pts(0, -186, 13, 9, 8), "#3B2F2A", w=3, seed=201))
    o.append(line([(0, -178), (0, -164), (-14, -156)], 3.2, INK, seed=202))
    o.append(line([(0, -164), (14, -156)], 3.2, INK, seed=203))
    for sx_ in (-1, 1):
        o.append(shape(ellipse_pts(sx_ * 36, -218, 11, 13, 8), INK, blob(ellipse_pts(sx_ * 32, -222, 3.6, 3.6, 6), "#FFFFFF"), w=1, seed=204))
    o.append(shape([(-20, -132), (0, -122), (20, -132), (34, -118), (0, -108), (-34, -118)], "#D64550", w=4.4, seed=205))
    return "".join(o)


ITEMS = {"book": book, "sneaker": sneaker, "teapot": teapot, "scarf": scarf, "lamp": lamp, "teddy": teddy}
ITEM_H = {"book": 156, "sneaker": 128, "teapot": 178, "scarf": 100, "lamp": 262, "teddy": 270}


def item(name, x, y, k=1.0, rot=0.0, sx=1.0, sy=1.0):
    return tf(ITEMS[name](), x, y, k, rot, sx, sy)
