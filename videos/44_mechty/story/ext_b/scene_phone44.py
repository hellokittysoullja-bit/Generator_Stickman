"""Сцена phone рилса 44, план s14 (28.45–31.0, клип 28.25–31.2): «мешает доставка еды, значит…».
Крупно телефон в левой руке Димы (горчичный рукав снизу-слева): на экране приложение доставки — карточки бургера, пиццы,
лапши и большая оранжевая кнопка с корзинкой (только картинки, без букв). Карточки едут вверх (лента листается).
На «доставка» (29.12) правая рука тянется указательным к кнопке, кнопка подсвечивается; на «значит» (30.16) левая
рука опускает телефон и он переворачивается экраном вниз на стол, правая ладонь прихлопывает его сверху (30.46)."""
import math

import lib
from c44 import kick, shake, wt
from hands5 import hand5
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad,
                 rect_pts, shape, smooth, svg)
from parts import sausage

_ST = {}
T_DOST = wt("доставка")     # 29.12
T_ZN = wt("значит")         # 30.16
T_SLAP = T_ZN + 0.30
SKIN, SKIN_SH, SKIN_SH2 = "#ecc4a2", "#d39f83", "#bf8a74"
HOOD, HOOD_SH, FOLD = "#d4a23e", "#a97b25", "#6b4a12"
PW, PH = 400, 800            # телефон
PC = (520, 760)              # центр телефона в руке
TABLE_Y = 1170
FLAT = (540, 1290)           # где телефон ляжет
ORANGE, ORANGE_SH = "#f0782e", "#c95a1a"


# ───────────────────────── еда-иконки
def burger(x, y, k, sd):
    s = [shape([(x - 46 * k, y - 4 * k, 1), (x - 40 * k, y - 30 * k), (x, y - 46 * k), (x + 40 * k, y - 30 * k), (x + 46 * k, y - 4 * k, 1)], "#e5a04a",
               "".join(blob(ellipse_pts(x + dx * k, y - 26 * k, 3 * k, 2 * k, 6), "#fff3d0") for dx in (-20, 0, 18)), w=2.6, seed=sd)]
    s.append(shape([(x - 50 * k, y - 4 * k), (x + 50 * k, y - 4 * k), (x + 44 * k, y + 6 * k), (x + 30 * k, y + 2 * k), (x + 10 * k, y + 8 * k),
                    (x - 14 * k, y + 2 * k), (x - 44 * k, y + 6 * k)], "#6fbf4a", "", w=2.4, seed=sd + 1))
    s.append(shape(rect_pts(x - 46 * k, y + 4 * k, x + 46 * k, y + 18 * k, 6 * k), "#7a3f22", "", w=2.4, seed=sd + 2))
    s.append(shape([(x - 44 * k, y + 18 * k, 1), (x + 44 * k, y + 18 * k, 1), (x + 40 * k, y + 34 * k), (x - 40 * k, y + 34 * k)], "#e5a04a", "",
                   w=2.6, seed=sd + 3))
    return "".join(s)


def pizza(x, y, k, sd):
    pts = [(x - 44 * k, y - 30 * k, 1), (x + 44 * k, y - 30 * k, 1), (x, y + 40 * k, 1)]
    inner = blob([(x - 44 * k, y - 30 * k), (x + 44 * k, y - 30 * k), (x + 40 * k, y - 20 * k), (x - 40 * k, y - 20 * k)], "#d98a3a")
    for dx, dy in ((-16, -8), (14, -6), (0, 14)):
        inner += blob(ellipse_pts(x + dx * k, y + dy * k, 8 * k, 8 * k, 10), "#d8433a")
    return shape(pts, "#f6c74a", inner, w=2.6, seed=sd)


def noodles(x, y, k, sd):
    s = []
    for j in range(3):
        s.append(line([(x - 10 * k + j * 10 * k, y - 4 * k), (x - 14 * k + j * 12 * k, y - 40 * k)], 3 * k, "#7a5a3a", taper=.1, wmin=.8, seed=sd + 10 + j)
                 if j == 1 else "")
    s.append(line([(x + 6 * k, y - 2 * k), (x + 30 * k, y - 48 * k)], 4 * k, "#8a5a34", taper=.05, wmin=.9, seed=sd + 20))
    s.append(line([(x + 16 * k, y - 2 * k), (x + 40 * k, y - 44 * k)], 4 * k, "#8a5a34", taper=.05, wmin=.9, seed=sd + 21))
    s.append(shape(ellipse_pts(x, y - 2 * k, 42 * k, 10 * k, 14), "#f2d27a",
                   "".join(line([(x - 30 * k + j * 14 * k, y - 6 * k), (x - 24 * k + j * 14 * k, y + 4 * k)], 2 * k, "#d9a840", seed=sd + 30 + j) for j in range(5)),
                   w=2.4, seed=sd + 1))
    s.append(shape([(x - 44 * k, y, 1), (x + 44 * k, y, 1), (x + 30 * k, y + 34 * k), (x - 30 * k, y + 34 * k)], "#d8433a",
                   line([(x - 36 * k, y + 12 * k), (x + 36 * k, y + 12 * k)], 3 * k, "#f6e6d0", seed=sd + 2), w=2.6, seed=sd + 3))
    return "".join(s)


def cart(x, y, k, col="#ffffff"):
    s = [line([(x - 34 * k, y - 22 * k), (x - 22 * k, y - 22 * k), (x - 12 * k, y + 10 * k), (x + 26 * k, y + 10 * k), (x + 32 * k, y - 12 * k),
               (x - 18 * k, y - 12 * k)], 6 * k, col, taper=.05, wmin=.9, seed=1101)]
    for dx in (-6, 20):
        s.append(f'<circle cx="{f(x + dx * k)}" cy="{f(y + 20 * k)}" r="{f(5.5 * k)}" fill="{col}"/>')
    return "".join(s)


# ───────────────────────── телефон
def screen(t, glow):
    """Экран в координатах телефона (центр 0, 0)."""
    x0, y0, x1, y1 = -PW / 2 + 18, -PH / 2 + 22, PW / 2 - 18, PH / 2 - 22
    s = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#fff4e8"/>']
    s.append(blob(rect_pts(x0, y0, x1, y0 + 110), ORANGE))
    s.append(blob(rect_pts(x0 + 30, y0 + 50, x1 - 30, y0 + 86, 18), "#ffffff", .9))
    s.append(f'<circle cx="{f(x0 + 56)}" cy="{f(y0 + 68)}" r="9" fill="none" stroke="{ORANGE_SH}" stroke-width="4"/>')
    s.append(line([(x0 + 62, y0 + 74), (x0 + 70, y0 + 82)], 4, ORANGE_SH, seed=1110))
    scroll = 60 * ease_io(clamp((t - 28.25) / 0.9)) + 18 * math.sin(t * 1.3)
    c = lib.clip_rect(x0, y0 + 112, x1 - x0, 520)
    cards = []
    foods = [burger, pizza, noodles, burger]
    bump = 1 + 0.12 * math.exp(-max(0, t - T_DOST) * 7) * math.sin(max(0, t - T_DOST) * 22) * (t > T_DOST)
    for j in range(4):
        cy = y0 + 200 + j * 170 - scroll
        card = shape(rect_pts(x0 + 18, cy - 70, x1 - 18, cy + 70, 22), "#ffffff",
                     blob(rect_pts(x0 + 18, cy + 50, x1 - 18, cy + 70), "#efe3d4"), w=3, seed=1120 + j)
        card += f'<g transform="translate({f(x0 + 92)} {f(cy)}) scale({f(bump)})">{foods[j](0, 0, 0.95, 1130 + j * 10)}</g>'
        card += blob(rect_pts(x0 + 170, cy - 36, x1 - 60, cy - 16, 10), "#3a3330", .85)
        card += blob(rect_pts(x0 + 170, cy + 2, x1 - 120, cy + 16, 7), "#b9aea0")
        card += blob(rect_pts(x0 + 170, cy + 28, x0 + 230, cy + 46, 9), ORANGE)
        for st in range(5):
            card += blob(ellipse_pts(x0 + 250 + st * 16, cy + 37, 6, 6, 5), "#f2c232") if st < 4 else ""
        cards.append(card)
    s.append(f'<g clip-path="url(#{c})">{"".join(cards)}</g>')
    # кнопка заказа
    by = y1 - 80
    g = 1 + 0.06 * glow
    bc = mix(ORANGE, "#ffa45a", glow)
    s.append(f'<g transform="translate(0 {f(by)}) scale({f(g)})">' +
             shape(rect_pts(x0 + 36 - 0, -46, x1 - 36, 46, 40), bc, blob(rect_pts(x0 + 36, 20, x1 - 36, 46), ORANGE_SH, .8), w=3.4, seed=1150) +
             cart(0, -2, 1.3) + "</g>")
    if glow > 0.05:
        s.append(f'<ellipse cx="0" cy="{f(by)}" rx="{f(170 + 30 * glow)}" ry="{f(60 + 16 * glow)}" fill="none" stroke="#ffd2a0" '
                 f'stroke-width="{f(8 * glow)}"/>')
    return "".join(s)


def phone_front(t, glow):
    body = rect_pts(-PW / 2, -PH / 2, PW / 2, PH / 2, 56)
    inner = screen(t, glow)
    inner += blob(rect_pts(-46, -PH / 2 + 24, 46, -PH / 2 + 44, 10), "#1b1b22")
    s = shape(body, "#22222a", "", w=5, seed=1160)
    scr = lib.clip_of(rect_pts(-PW / 2 + 16, -PH / 2 + 18, PW / 2 - 16, PH / 2 - 18, 44))
    s += f'<g clip-path="url(#{scr})">{inner}</g>'
    s += line([(-PW / 2 + 40, -PH / 2 + 130), (-PW / 2 + 40, -PH / 2 + 300)], 8, "#ffffff", taper=.4, seed=1161, op=.35)
    return s


def phone_back():
    body = rect_pts(-PW / 2, -PH / 2, PW / 2, PH / 2, 56)
    inner = blob(rect_pts(-PW / 2, PH / 2 - 160, PW / 2, PH / 2), "#2a4a6a", .9)
    s = shape(body, "#3c6a92", inner, w=5, seed=1170)
    s += shape(rect_pts(-PW / 2 + 30, -PH / 2 + 30, -PW / 2 + 150, -PH / 2 + 170, 30), "#2a2a32",
               "".join(blob(ellipse_pts(-PW / 2 + 70 + dx, -PH / 2 + 70 + dy, 20, 20, 12), "#0e0e14") for dx, dy in ((0, 0), (40, 60))), w=3.4, seed=1171)
    return s


# ───────────────────────── руки
def _sleeve(wx, wy, ang, L=700, w0=150, w1=200, sd=0):
    """Рукав худи от запястья (wx, wy) назад по направлению ang+180, с резинкой-манжетой."""
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    bx, by = -c, -s_
    nx, ny = -s_, c

    def P(u, v):
        return (wx + bx * u + nx * v, wy + by * u + ny * v)
    sl = [P(40, -w0 / 2), P(L, -w1 / 2), P(L, w1 / 2), P(40, w0 / 2)]
    inner = blob([P(40, w0 * .15), P(L, w1 * .2), P(L, w1 / 2), P(40, w0 / 2)], HOOD_SH, .85)
    inner += line([P(160, -w0 * .2), P(420, -w0 * .1)], 4, FOLD, seed=sd + 1, op=.7)
    o = shape(sl, HOOD, inner, w=5, seed=sd + 2)
    cuff = [P(10, -w0 / 2 - 6), P(80, -w0 / 2 - 10), P(80, w0 / 2 + 10), P(10, w0 / 2 + 6)]
    o += shape(cuff, HOOD_SH, "".join(line([P(14, -w0 / 2 + 12 + k * w0 / 5), P(76, -w0 / 2 + 12 + k * w0 / 5)], 3, FOLD, seed=sd + 3 + k, op=.8)
                                        for k in range(5)), w=4.4, seed=sd + 9)
    return o


def hold_hand():
    """Левая рука держит телефон снизу: ладонь за телефоном, большой палец на левом крае рамки, кончики четырёх пальцев
    выглядывают из-за правого края, запястье и рукав уходят вниз. Возвращает (сзади телефона, спереди) в координатах
    телефона."""
    back, front = [], []
    for j, yy in enumerate((70, 150, 225, 292)):
        pts = [(PW / 2 - 70, yy + 8), (PW / 2 + 6, yy), (PW / 2 + 30, yy - 4)]
        back.append(shape(sausage(pts, 50 - 3 * j, 46 - 4 * j), SKIN, blob(sausage([(p[0], p[1] + 9) for p in pts], 20, 16), SKIN_SH, .7),
                          w=4, seed=1200 + j))
    palm = [(-PW / 2 + 20, PH / 2 - 160), (PW / 2 - 20, PH / 2 - 110), (PW / 2 - 40, PH / 2 + 60), (90, PH / 2 + 150), (-90, PH / 2 + 150),
            (-PW / 2 + 10, PH / 2 + 40)]
    back.append(_sleeve(0, PH / 2 + 190, -95, sd=1230))
    back.append(shape(palm, SKIN, blob([(PW / 2 - 40, PH / 2 + 60), (90, PH / 2 + 150), (40, PH / 2 + 40), (PW / 2 - 30, PH / 2 - 40)], SKIN_SH, .8),
                      w=4.6, seed=1210))
    th = [(-PW / 2 - 20, PH / 2 + 20), (-PW / 2 - 6, PH / 2 - 110), (-PW / 2 + 22, PH / 2 - 210)]
    front.append(shape(sausage(th, 66, 54), SKIN, blob(sausage([(p[0] - 12, p[1]) for p in th], 26, 22), SKIN_SH, .8), w=4.4, seed=1220))
    front.append(shape(ellipse_pts(-PW / 2 + 18, PH / 2 - 200, 14, 19, 10, rot=15), "#f6dccb", "", w=2, seed=1221))
    return "".join(back), "".join(front)


def point_svg(sd=1300):
    """Кисть с вытянутым указательным, вид сбоку: запястье в (0, 0), палец вдоль +x."""
    o = []
    # три поджатых пальца — бугорки снизу кулака
    for j in range(3):
        y = 8 + j * 26
        o.append(shape(sausage([(80, y), (112, y + 2), (122, y + 10)], 34, 32), SKIN, "", w=3.6, seed=sd + j))
    fist = [(-10, -48), (60, -60), (118, -44), (130, -10), (120, 40), (80, 74), (10, 64), (-14, 30)]
    o.append(shape(fist, SKIN, blob([(10, 40), (80, 56), (120, 40), (80, 74), (10, 64)], SKIN_SH, .8), w=4.2, seed=sd + 5))
    idx = [(96, -34), (170, -40), (232, -42)]
    o.append(shape(sausage(idx, 38, 32), SKIN, blob(sausage([(p[0], p[1] + 9) for p in idx], 14, 11), SKIN_SH, .7), w=3.8, seed=sd + 6))
    o.append(shape(ellipse_pts(222, -48, 10, 7, 10), "#f6dccb", "", w=1.8, seed=sd + 7))
    th = [(36, -42), (72, -52), (100, -50)]
    o.append(shape(sausage(th, 34, 30), SKIN, blob(sausage([(40, -36), (98, -44)], 12, 10), SKIN_SH, .6), w=3.6, seed=sd + 8))
    o.append(line([(150, -56), (152, -26)], 2.4, SKIN_SH2, seed=sd + 9, op=.8))
    return "".join(o)


def palm_svg(sd=1350):
    """Раскрытая ладонь сверху (тыл кисти): запястье в (0, 0), пальцы вдоль +x, большой палец к −y."""
    o = []
    for j, (y, L) in enumerate(((-36, 120), (-12, 132), (12, 126), (34, 104))):
        o.append(shape(sausage([(80, y), (80 + L * .55, y + j * 2 - 3), (80 + L, y + j * 4 - 6)], 32, 28), SKIN,
                       blob(sausage([(84, y + 7), (80 + L, y + j * 4 + 2)], 12, 10), SKIN_SH, .6), w=3.6, seed=sd + j))
    th = [(30, -50), (70, -86), (110, -100)]
    o.append(shape(sausage(th, 38, 30), SKIN, "", w=3.8, seed=sd + 5))
    pal = [(-10, -50), (60, -58), (104, -48), (108, 50), (60, 58), (-10, 46)]
    o.append(shape(pal, SKIN, blob([(-10, 20), (104, 26), (108, 50), (60, 58), (-10, 46)], SKIN_SH, .8), w=4.2, seed=sd + 6))
    for j, y in enumerate((-36, -12, 12, 34)):
        o.append(line([(96, y - 8), (102, y), (96, y + 8)], 2.4, SKIN_SH2, seed=sd + 10 + j, op=.8))
    return "".join(o)


def point_hand(t):
    """Правая рука снизу-справа: указательный к кнопке (29.12), отдёргивается; после переворота — ладонь прихлопывает."""
    btn = (PC[0] + 40, PC[1] + PH / 2 - 100)
    u = ease_out(clamp((t - T_DOST + 0.25) / 0.4), 3) if t > T_DOST - 0.25 else 0.0
    ang = -140.0
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    tip_off = (232 * c - (-42) * s_ * 1, 232 * s_ + (-42) * c)
    hover = (btn[0] - tip_off[0] * 1.15 + 30, btn[1] - tip_off[1] * 1.15 + 40)
    rest = (1300, 1700)
    x, y = rest[0] + (hover[0] - rest[0]) * u, rest[1] + (hover[1] - rest[1]) * u
    y += 5 * math.sin(t * 9) * u
    if t > 29.8:
        r = ease_in(clamp((t - 29.8) / 0.3), 2)
        x, y = x + (1400 - x) * r, y + (1800 - y) * r
    out = ""
    if t < 30.15:
        out = _sleeve(x, y, ang, sd=1330) + f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)}) scale(1.15)">{point_svg()}</g>'
    if t > T_ZN + 0.02:
        a = ease_out(clamp((t - T_ZN - 0.02) / (T_SLAP - T_ZN - 0.02)), 2)
        pang = -165.0
        x = 1350 + (FLAT[0] + 200 - 1350) * a
        y = 900 + (FLAT[1] - 30 - 900) * a
        if t > T_SLAP:
            q = t - T_SLAP
            y += -5 * math.exp(-q * 10) * math.sin(q * 30)
        out += _sleeve(x, y, pang, sd=1360) + f'<g transform="translate({f(x)} {f(y)}) rotate({f(pang)}) scale(1.2)">{palm_svg()}</g>'
    return out

def room():
    s = []
    g = lin_grad([(0, "#c9b79a", 1), (1, "#e5d6b8", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{TABLE_Y + 600}" fill="url(#{g})"/>')
    for k in range(-8, 24):
        s.append(f'<rect x="{k * 80}" y="-600" width="30" height="{TABLE_Y + 600}" fill="#bba889" opacity=".35"/>')
    gl = rad_grad([(0, "#fff0c8", .6), (1, "#fff0c8", 0)], 760, 400, 700, 600)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{TABLE_Y + 600}" fill="url(#{gl})"/>')
    # стол
    top = [(-600, TABLE_Y, 1), (W + 600, TABLE_Y, 1), (W + 600, H + 600, 1), (-600, H + 600, 1)]
    inner = "".join(line([(-600, TABLE_Y + 40 + k * 90 + k * k * 8), (W + 600, TABLE_Y + 30 + k * 90 + k * k * 8)], 3, "#8a5a34", taper=.1, wmin=.8,
                         seed=1400 + k, op=.6) for k in range(9))
    inner += blob(rect_pts(-600, TABLE_Y, W + 600, TABLE_Y + 24), "#c88a58")
    s.append(shape(top, "#a8693f", inner, w=5, seed=1410))
    # кружка у края
    mx, my = 140, TABLE_Y + 70
    s.append(blob(ellipse_pts(mx + 20, my + 6, 90, 18, 14), "#2a1608", .3, blur(6)))
    s.append(shape([(mx - 70, my - 170, 1), (mx + 70, my - 170, 1), (mx + 64, my, 1), (mx - 64, my, 1)], "#e85f4f",
                   blob([(mx + 20, my - 170), (mx + 70, my - 170), (mx + 64, my), (mx + 20, my)], "#c04a3c", .9), w=4.4, seed=1420))
    s.append(shape([(mx - 70, my - 140), (mx - 118, my - 130), (mx - 120, my - 70), (mx - 66, my - 50), (mx - 66, my - 72), (mx - 98, my - 84),
                    (mx - 98, my - 120), (mx - 70, my - 118)], "#e85f4f", "", w=3.6, seed=1421))
    return "".join(s)


def phone_state(t):
    """Возвращает (cx, cy, sy, rot, scale): переворот вокруг горизонтальной оси до плоского лежания на столе."""
    if t < T_ZN - 0.04:
        bob = 6 * math.sin(t * 1.9)
        return PC[0] + 4 * math.sin(t * 1.3), PC[1] + bob, 1.0, -3 + 1.2 * math.sin(t * 1.1), 1.0
    u = clamp((t - T_ZN + 0.04) / 0.32)
    e = u ** 1.15
    ang = math.pi * e
    sy = math.cos(ang) if u < 1 else -1.0
    # плоское лежание: высота сжата до 0.3 в конце
    if sy < 0:
        sy = max(sy, -0.3) if u < 1 else -0.3
        sy = -min(0.3, -sy)
    cx = PC[0] + (FLAT[0] - PC[0]) * e
    cy = PC[1] + (FLAT[1] - PC[1]) * e - 140 * math.sin(math.pi * e)
    rot = -3 + 9 * e
    sc = 1 - 0.12 * e
    if t > T_SLAP:
        q = t - T_SLAP
        cy += 10 * math.exp(-q * 12) * math.sin(q * 34)
    return cx, cy, sy, rot, sc


def frame14(t):
    s = [_ST["room"]]
    cx, cy, sy, rot, sc = phone_state(t)
    glow = smooth(T_DOST + 0.1, T_DOST + 0.3, t) * (1 - smooth(29.8, 30.0, t))
    hold_out = ease_in(clamp((t - T_ZN + 0.06) / 0.14), 2)
    if sy > 0:
        body = phone_front(t, glow)
    else:
        body = phone_back()
    if sy < 0:
        s.append(blob(ellipse_pts(cx + 10, cy + 30, PW * sc * .62, 34, 16), "#2a1608", .35, blur(10)))
    tf = f"translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({f(sc)} {f(sc * sy)})"
    hb, hf = _ST["hold"]
    if hold_out < 1:
        hx, hy = -120 * hold_out, 900 * hold_out
        htf = f"translate({f(PC[0] + hx)} {f(PC[1] + hy + 6 * math.sin(t * 1.9))}) rotate({f(-3 - 20 * hold_out)})"
        s.append(f'<g transform="{htf}">{hb}</g>')
    s.append(f'<g transform="{tf}">{body}</g>')
    if hold_out < 1:
        s.append(f'<g transform="{htf}">{hf}</g>')
    s.append(point_hand(t))
    # удар о стол — штрихи
    if T_SLAP <= t < T_SLAP + 0.3:
        u = (t - T_SLAP) / 0.3
        for j, a in enumerate((-160, -130, -50, -20)):
            r0, r1 = 260 + 60 * u, 320 + 90 * u
            ar = math.radians(a)
            s.append(line([(FLAT[0] + r0 * math.cos(ar), FLAT[1] + 30 + r0 * math.sin(ar) * .5),
                           (FLAT[0] + r1 * math.cos(ar), FLAT[1] + 30 + r1 * math.sin(ar) * .5)], 9 * (1 - u) + 2, INK, taper=.5, seed=1500 + j))
    return "".join(s)


def cam14(t):
    u = clamp((t - 28.25) / 2.95)
    k1, r1 = kick(t, [T_DOST], 0.03, 10)
    k2, r2 = kick(t, [T_ZN], 0.05, 9)
    dx, dy = shake(t, T_SLAP, 14, 9, 60)
    flip = ease_io(clamp((t - T_ZN) / 0.5))
    cy = 860 + (1080 - 860) * flip
    sc = (1.0 + 0.08 * ease_io(clamp(u / 0.6))) * (1 - 0.06 * flip)
    return cam(560 + dx, cy + dy, sc * k1 * k2, r1 + r2 + 0.8 - 1.4 * u)


def frame(sid, t):
    if not _ST:
        lib.DEFS.clear()
        _ST["room"] = room()
        _ST["hold"] = hold_hand()
        lib.static_done()
    lib.dyn_begin()
    return svg(f'<rect width="{W}" height="{H}" fill="#d8c8a8"/><g transform="{cam14(t)}">{frame14(t)}</g>')


_ = INK
