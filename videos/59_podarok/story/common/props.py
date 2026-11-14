"""Общие предметы рилса 59 «подарок» — ОДИН вид для групп A…F (никто не рисует свои копии).

Подключение (в сцене группы, у которой рядом свой lib.py/ink.py):
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common")); import props
Функции возвращают строку SVG (мир кадра, 1080×1920), без собственной камеры. Точка (x, y) — ЦЕНТР ДНА предмета на опоре.
Единица k=1 — масштаб «Дима в полный рост» (BS 0.6; ладонь ≈ 47 px). На крупных планах предмет и кисть масштабируются ОДНИМ
коэффициентом. Заливки сплошные (без полупрозрачных фигур), тушь INK из lib; букв и цифр нигде нет.

    pie(x, y, k, state, rot, seed)   пирог в форме: state "whole" | "crooked" (осел набок, трещины, начинка вылезла) | "cut" (вырезан клин)
                                     ширина 190, высота ≈ 70; корка C_CRUST #C98A4B, начинка штрихами
    cake(x, y, k, candle, t)         двухъярусный торт со свечой (s02); candle 0…1 — рост пламени (0 — свечи нет ни пламени, ни стержня)
    bouquet(x, y, k, rot, seed)      букет: ромашки, тюльпаны, крафт-обёртка C_KRAFT #C9A877; ширина ≈ 120, высота ≈ 190 (точка — кончик обёртки)
    jar_flowers(x, y, k, seed)       банка с водой и цветами (ширина 70, высота ≈ 175 с цветами)
    giftbox(x, y, k, lid, rot)       подарочная коробка с бантом 120×100; lid 0…1 — крышка подпрыгнула
    basket(x, y, k, inside, sag)     плетёная корзина C_WICKER #B98A50, 170×110 без ручки (ручка вверх до 190); inside — SVG вещей,
                                     рисуются между задней стенкой и передней; sag 0…1 — просела
    basket_back / basket_front       те же части раздельно (вещи вставлять между)
    item(name, x, y, k, rot)         шесть вещей корзины, ОДИНАКОВЫЕ во всех клипах: book, sneaker, kettle, scarf, lamp, teddy
    ITEMS, ITEM_H                    имена и высоты при k=1
    spark(x, y, k, u)                четырёхлучевой блик, u 0…1 — жизнь вспышки
Константы цветов: C_CRUST, C_FILL, C_KRAFT, C_WICKER, C_BOX, C_RIBBON, C_DAISY, C_TULIP, C_LEAF."""
import math

import lib
from lib import blob, ellipse_pts, f, line, mix, rect_pts, shape

C_CRUST = "#C98A4B"
C_CRUST_SH = "#A8692F"
C_CRUST_HI = "#E0A867"
C_FILL = "#B8453C"           # вишнёвая начинка
C_FILL_SH = "#8F2F2C"
C_TIN = "#8D8F94"
C_TIN_SH = "#6E7075"
C_KRAFT = "#C9A877"
C_KRAFT_SH = "#A98A58"
C_WICKER = "#B98A50"
C_WICKER_SH = "#8F6535"
C_WICKER_IN = "#5E4026"
C_BOX = "#D9506B"
C_BOX_SH = "#AE3552"
C_RIBBON = "#F3C23B"
C_RIBBON_SH = "#C99A1E"
C_DAISY = "#FFFFFF"
C_DAISY_SH = "#E4E4DC"
C_DAISY_C = "#F2B632"
C_TULIP = "#E04A5A"
C_TULIP_SH = "#B8303F"
C_LEAF = "#5FA05B"
C_LEAF_SH = "#43803F"
C_CREAM = "#FFF1DC"
C_SPONGE = "#E9B98A"
C_PINK = "#E98FA6"
C_FLAME = "#FFB22E"
ITEMS = ("book", "sneaker", "kettle", "scarf", "lamp", "teddy")
ITEM_H = {"book": 84, "sneaker": 58, "kettle": 96, "scarf": 52, "lamp": 112, "teddy": 90}


def _tf(inner, x, y, k, rot=0.0):
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k:.5f})">{inner}</g>'


def _P(c, r, a, ry=None):
    """Точка эллипса: центр c=(x, y), радиусы r (и ry), угол a в градусах (0 — вправо, 90 — вниз)."""
    ry = r if ry is None else ry
    return (c[0] + r * math.cos(math.radians(a)), c[1] + ry * math.sin(math.radians(a)))


def _star(cx, cy, r, n, ratio, rot=0.0):
    pts = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * ratio
        a = math.radians(rot + 360 / (2 * n) * i)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


# ───────────────────────────── пирог ─────────────────────────────

def pie(x, y, k=1.0, state="whole", rot=0.0, seed=0):
    """Пирог в форме (дно в (x, y)). whole — целый, crooked — осевший набок, cut — с вырезанным клином."""
    sd = 8100 + seed * 11
    RX, RY, TOP = 95.0, 19.0, -30.0
    crooked = state == "crooked"
    sag = 1.0 if crooked else 0.0
    # форма: низ (дно) и борт
    side = [(-RX + 8, 0, 1), (RX - 8, 0, 1), (RX, TOP + 2), (-RX, TOP + 2)]
    out = [shape(side, C_TIN, blob([(RX * .35, TOP), (RX, TOP), (RX - 8, 0), (RX * .3, 0)], C_TIN_SH), w=3.4, seed=sd)]
    # верх: купол корки (у crooked — перекошен: левая сторона просела)
    cy = TOP - 4
    top = []
    for i in range(20):
        a = 360 * i / 20
        px, py = _P((0, cy), RX - 4, a, RY + 6)
        dip = sag * (16 * max(0.0, -math.cos(math.radians(a))) ** 1.2 + 4 * math.sin(math.radians(a * 2)))
        top.append((px, py + dip - 2 * sag))
    if crooked:
        lump = [(-RX * .55, cy - 6, 0)]
    inner = blob(ellipse_pts(2, cy + 3, RX - 20, RY - 2, 18), C_FILL)
    inner += "".join(line([(-60 + 22 * j, cy - 4 + 3 * (j % 2)), (-48 + 22 * j, cy + 8)], 2.6, C_FILL_SH, taper=.2, wmin=.6, seed=sd + 50 + j) for j in range(6))
    # решётка корки: сплошные полосы
    for j in range(-3, 4):
        x0 = j * 30
        inner += line([(x0 - 24, cy - RY - 8), (x0 + 24, cy + RY + 12)], 11, C_CRUST, taper=0.0, wmin=1.0, seed=sd + 60 + j)
        inner += line([(x0 + 24, cy - RY - 8), (x0 - 24, cy + RY + 12)], 11, C_CRUST, taper=0.0, wmin=1.0, seed=sd + 70 + j)
    inner += line([(-RX + 12, cy + 6), (RX - 14, cy + 6 + 2 * sag)], 0.1, C_CRUST, seed=1)
    ring_o = ellipse_pts(0, cy + 1, RX - 3, RY + 5, 22)
    surf = shape(top, C_CRUST, inner, w=3.6, seed=sd + 1)
    if state == "cut":
        # клин вырезан спереди: видно дно формы и две стенки разреза с начинкой (вид чуть сверху)
        out.append(surf)
        c = (-2.0, cy + 2)
        p0 = _P((0, cy + 1), RX - 4, 36, RY + 5)
        p1 = _P((0, cy + 1), RX - 4, 100, RY + 5)
        D = 24.0
        out.append(shape([c, p0, (p0[0] + 2, p0[1] + D), (p1[0] - 2, p1[1] + D), p1], "#7B4E27",
                         blob([c, (p0[0], p0[1] + 6), (p1[0], p1[1] + 6)], "#5E3A1B"), w=3.2, seed=sd + 2))
        out.append(shape([c, p1, (p1[0], p1[1] + D * .8), (c[0], c[1] + D * .8)], C_FILL, blob([c, p1, (p1[0], p1[1] + 6), (c[0], c[1] + 6)], C_CRUST), w=2.8, seed=sd + 3))
        out.append(shape([c, p0, (p0[0], p0[1] + D * .8), (c[0], c[1] + D * .8)], C_FILL_SH, blob([c, p0, (p0[0], p0[1] + 6), (c[0], c[1] + 6)], C_CRUST_SH), w=2.8, seed=sd + 4))
    else:
        out.append(surf)
    if crooked:
        # трещины и вылезшая начинка на низкой стороне; перекос корпуса
        out.append(blob([(-RX + 4, TOP + 2), (-RX - 14, TOP + 20), (-RX - 4, TOP + 28), (-RX + 18, TOP + 12)], C_FILL))
        out.append(line([(-RX - 14, TOP + 20), (-RX - 4, TOP + 28), (-RX + 18, TOP + 12)], 2.6, C_FILL_SH, taper=.2, wmin=.5, seed=sd + 5))
        for j, (a, b) in enumerate((((-40, cy - 10), (-18, cy + 6)), ((20, cy - 14), (40, cy + 2)), ((-70, cy + 2), (-54, cy + 14)))):
            out.append(line([a, ((a[0] + b[0]) / 2 + 3, (a[1] + b[1]) / 2 - 2), b], 3.4, C_CRUST_SH, taper=.3, wmin=.4, seed=sd + 10 + j))
    if state != "cut":
        out.append(line([(-RX + 18, cy - 8), (-18, cy - RY - 2)], 5.0, C_CRUST_HI, taper=.5, wmin=.2, seed=sd + 6, peak=.5))
    return _tf("".join(out), x, y, k, rot + (-6.5 * sag))


# ───────────────────────────── торт ─────────────────────────────

def cake(x, y, k=1.0, candle=0.0, t=0.0, seed=0):
    """Двухъярусный торт со свечой (дно в (x, y), ширина 150, высота 130 + свеча 40)."""
    sd = 8300 + seed * 11
    out = []
    # плита-тарелка
    out.append(shape(ellipse_pts(0, -4, 98, 12, 24), "#F4EEE4", blob(ellipse_pts(0, -2, 80, 7, 20), "#E2D9C8"), w=3.0, seed=sd))
    # нижний ярус
    b1 = [(-75, -6, 1), (75, -6, 1), (76, -62), (-76, -62)]
    i1 = blob(rect_pts(30, -62, 78, -4), mix(C_SPONGE, "#000000", .12))
    i1 += blob(rect_pts(-80, -36, 80, -30), C_CREAM)
    out.append(shape(b1, C_SPONGE, i1, w=3.6, seed=sd + 1))
    # верх нижнего яруса, глазурь
    out.append(shape(ellipse_pts(0, -62, 76, 14, 22), C_PINK, blob(ellipse_pts(-4, -60, 58, 8, 18), mix(C_PINK, "#ffffff", .3)), w=3.4, seed=sd + 2))
    for j, (dx, h) in enumerate(((-58, 16), (-30, 24), (-4, 14), (24, 22), (52, 15))):
        out.append(shape([(dx - 11, -62, 1), (dx + 11, -62, 1), (dx + 9, -62 + h * .7), (dx, -62 + h), (dx - 9, -62 + h * .7)], C_PINK, "", w=2.8, seed=sd + 20 + j))
    # верхний ярус
    b2 = [(-48, -62, 1), (48, -62, 1), (49, -106), (-49, -106)]
    i2 = blob(rect_pts(18, -106, 50, -62), mix(C_SPONGE, "#000000", .12)) + blob(rect_pts(-50, -84, 50, -78), C_CREAM)
    out.append(shape(b2, C_SPONGE, i2, w=3.4, seed=sd + 3))
    out.append(shape(ellipse_pts(0, -106, 49, 10, 20), C_CREAM, blob(ellipse_pts(-3, -105, 36, 5, 16), "#FFFFFF"), w=3.2, seed=sd + 4))
    for j, dx in enumerate((-30, 0, 30)):   # вишенки
        out.append(shape(ellipse_pts(dx, -112, 8, 8, 10), "#C9283F", blob(ellipse_pts(dx - 2, -114, 2.4, 2.4, 8), "#FFFFFF"), w=2.6, seed=sd + 30 + j))
    if candle > 0.02:
        u = min(1.0, candle)
        ch = 40 * min(1.0, u * 1.6)
        out.append(shape([(-5, -112, 1), (5, -112, 1), (5, -112 - ch, 1), (-5, -112 - ch, 1)], "#7FC1E6",
                         "".join(line([(-5, -112 - ch * (.2 + .3 * q)), (5, -112 - ch * (.1 + .3 * q))], 3, "#FFFFFF", taper=0, wmin=1, seed=sd + 40 + q) for q in range(3)), w=2.8, seed=sd + 5))
        if candle > 0.25:
            fu = min(1.0, (candle - .25) / .5)
            fl = 22 * fu * (1 + .12 * math.sin(t * 22))
            sw = 3.5 * math.sin(t * 17)
            fy = -112 - ch - 2
            out.append(shape([(sw * .3, fy - fl, 1), (9 * fu, fy - fl * .35), (6 * fu, fy + 2), (-6 * fu, fy + 2), (-9 * fu, fy - fl * .35)], C_FLAME,
                             blob(ellipse_pts(0, fy - 4, 3.6 * fu, 7 * fu, 10), "#FFF3B0"), w=2.4, seed=sd + 6))
    return _tf("".join(out), x, y, k)


# ───────────────────────────── цветы ─────────────────────────────

def _daisy(cx, cy, r, rot, seed):
    pet = []
    n = 9
    for i in range(n * 2):
        a = math.radians(rot + 180 / n * i)
        rr = r if i % 2 == 0 else r * .52
        pet.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    s = shape(pet, C_DAISY, blob(ellipse_pts(cx + r * .22, cy + r * .24, r * .7, r * .55, 10), C_DAISY_SH), w=2.6, seed=seed)
    s += shape(ellipse_pts(cx, cy, r * .32, r * .32, 10), C_DAISY_C, blob(ellipse_pts(cx + r * .08, cy + r * .1, r * .18, r * .15, 8), "#D9961A"), w=2.2, seed=seed + 1)
    return s


def _tulip(cx, cy, r, rot, seed):
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def T(px, py):
        return (cx + px * ca - py * sa, cy + px * sa + py * ca)
    cup = [T(-r * .62, -r * .45), T(-r * .3, -r * 1.2), T(0, -r * .62), T(r * .3, -r * 1.2), T(r * .62, -r * .45), T(r * .58, r * .2), T(0, r * .72), T(-r * .58, r * .2)]
    inner = blob([T(r * .12, -r * .6), T(r * .62, -r * .45), T(r * .58, r * .2), T(0, r * .72)], C_TULIP_SH)
    s = shape([(p[0], p[1], 1) if i in (1, 3) else p for i, p in enumerate(cup)], C_TULIP, inner, w=2.8, seed=seed)
    s += line([T(-r * .3, -r * .3), T(-r * .38, r * .22)], 3.2, mix(C_TULIP, "#ffffff", .5), taper=.5, wmin=.3, seed=seed + 1)
    return s


def _leaf(x0, y0, x1, y1, w, col, seed):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    L = math.hypot(nx, ny) or 1
    nx, ny = nx / L * w, ny / L * w
    return shape([(x0, y0, 1), (mx + nx, my + ny), (x1, y1, 1), (mx - nx, my - ny)], col, line([(x0, y0), (x1, y1)], 2.2, mix(col, "#000000", .3), taper=.3, wmin=.5, seed=seed), w=2.6, seed=seed + 1)


def bouquet(x, y, k=1.0, rot=0.0, seed=0):
    """Букет в крафт-обёртке (точка — кончик конуса), цветы сверху, ширина ≈ 120, высота ≈ 190."""
    sd = 8500 + seed * 11
    out = []
    # листья и стебли за цветами
    for j, (ex, ey) in enumerate(((-52, -150), (-30, -176), (34, -178), (56, -146), (0, -186))):
        out.append(line([(ex * .35, -96), (ex, ey + 22)], 4.2, C_LEAF_SH, taper=.2, wmin=.8, seed=sd + j))
    out.append(_leaf(-18, -104, -62, -142, 13, C_LEAF, sd + 10))
    out.append(_leaf(18, -104, 64, -138, 13, C_LEAF, sd + 12))
    out.append(_leaf(-4, -108, -22, -170, 10, C_LEAF_SH, sd + 14))
    # цветы
    out.append(_tulip(-40, -158, 22, -14, sd + 20))
    out.append(_tulip(44, -154, 21, 12, sd + 22))
    out.append(_daisy(0, -176, 25, 6, sd + 24))
    out.append(_daisy(-58, -126, 19, 22, sd + 26))
    out.append(_daisy(60, -122, 19, -8, sd + 28))
    out.append(_tulip(6, -140, 19, 4, sd + 30))
    # обёртка-конус
    cone = [(0, 0, 1), (54, -112, 1), (30, -126), (-30, -126), (-54, -112, 1)]
    ci = blob([(8, 0), (54, -112), (30, -126), (-4, -126)], C_KRAFT_SH)
    ci += line([(-34, -118), (-6, -10)], 2.4, C_KRAFT_SH, taper=.4, wmin=.4, seed=sd + 40)
    ci += line([(-14, -122), (6, -20)], 2.4, mix(C_KRAFT, "#ffffff", .3), taper=.4, wmin=.4, seed=sd + 41)
    out.append(shape(cone, C_KRAFT, ci, w=3.6, seed=sd + 42))
    # завязка: бечёвка и бантик
    out.append(line([(-36, -88), (0, -80), (36, -88)], 4.0, "#7A5A3A", taper=.1, wmin=.8, seed=sd + 43))
    out.append(shape([(0, -82), (-18, -96), (-20, -76)], "#E0527A", "", w=2.4, seed=sd + 44))
    out.append(shape([(0, -82), (18, -96), (20, -76)], "#E0527A", "", w=2.4, seed=sd + 45))
    out.append(shape(ellipse_pts(0, -82, 5, 5, 8), "#B8304F", "", w=2.2, seed=sd + 46))
    return _tf("".join(out), x, y, k, rot)


def jar_flowers(x, y, k=1.0, seed=0):
    """Стеклянная банка с водой и небольшим букетом (дно в (x, y))."""
    sd = 8700 + seed * 11
    out = []
    out.append(line([(-6, -78), (-18, -138)], 3.6, C_LEAF_SH, taper=.2, wmin=.8, seed=sd))
    out.append(line([(4, -78), (14, -146)], 3.6, C_LEAF_SH, taper=.2, wmin=.8, seed=sd + 1))
    out.append(line([(0, -78), (-2, -150)], 3.6, C_LEAF_SH, taper=.2, wmin=.8, seed=sd + 2))
    out.append(_leaf(-6, -92, -34, -118, 8, C_LEAF, sd + 3))
    out.append(_leaf(8, -90, 36, -112, 8, C_LEAF, sd + 5))
    out.append(_tulip(-22, -146, 15, -12, sd + 7))
    out.append(_daisy(14, -154, 16, 8, sd + 9))
    out.append(_daisy(-2, -160, 13, 20, sd + 11))
    body = [(-34, -86, 1), (34, -86, 1), (36, -8), (28, 0, 1), (-28, 0, 1), (-36, -8)]
    inner = blob(rect_pts(-40, -58, 40, 4), "#BFE3F2") + blob(rect_pts(-40, -58, 40, -54), "#E6F5FB")
    inner += blob([(14, -86), (36, -86), (36, -8), (28, 0), (14, 0)], "#A9D2E6")
    # стебли внутри воды
    inner += line([(-6, -62), (-3, -10)], 3, C_LEAF_SH, taper=.1, wmin=.8, seed=sd + 13) + line([(4, -62), (6, -10)], 3, C_LEAF_SH, taper=.1, wmin=.8, seed=sd + 14)
    out.append(shape(body, "#DCEFF9", inner, w=3.2, seed=sd + 15))
    out.append(line([(-26, -80), (-27, -22)], 4.5, "#FFFFFF", taper=.5, wmin=.3, seed=sd + 16, peak=.5))
    return _tf("".join(out), x, y, k)


# ───────────────────────────── коробка ─────────────────────────────

def giftbox(x, y, k=1.0, lid=0.0, rot=0.0, seed=0):
    """Подарочная коробка с бантом. lid 0…1 — крышка и бант подпрыгнули вверх (до 34 px)."""
    sd = 8900 + seed * 11
    out = []
    W, H = 60.0, 74.0
    body = [(-W, 0, 1), (W, 0, 1), (W, -H, 1), (-W, -H, 1)]
    bi = blob(rect_pts(W * .45, -H, W + 2, 0), C_BOX_SH) + blob(rect_pts(-12, -H, 12, 0), C_RIBBON)
    bi += blob(rect_pts(8, -H, 12, 0), C_RIBBON_SH)
    out.append(shape(body, C_BOX, bi, w=3.8, seed=sd))
    # крышка
    ly = -H - 34 * max(0.0, min(1.0, lid)) * 1.0
    lidp = [(-W - 5, ly + 2, 1), (W + 5, ly + 2, 1), (W + 5, ly - 24, 1), (-W - 5, ly - 24, 1)]
    li = blob(rect_pts(W * .45, ly - 24, W + 7, ly + 3), C_BOX_SH) + blob(rect_pts(-12, ly - 24, 12, ly + 3), C_RIBBON) + blob(rect_pts(8, ly - 24, 12, ly + 3), C_RIBBON_SH)
    out.append(shape(lidp, C_BOX, li, w=3.8, seed=sd + 1))
    # бант
    by = ly - 24
    out.append(shape([(0, by, 1), (-34, by - 26), (-42, by - 8), (-22, by + 2)], C_RIBBON, blob([(0, by), (-22, by - 6), (-26, by - 2)], C_RIBBON_SH), w=3.0, seed=sd + 2))
    out.append(shape([(0, by, 1), (34, by - 26), (42, by - 8), (22, by + 2)], C_RIBBON, blob([(0, by), (22, by - 6), (26, by - 2)], C_RIBBON_SH), w=3.0, seed=sd + 3))
    out.append(shape(ellipse_pts(0, by - 3, 9, 8, 10), C_RIBBON, blob(ellipse_pts(2, by - 1, 5, 4, 8), C_RIBBON_SH), w=2.8, seed=sd + 4))
    out.append(line([(-2, by + 4), (-14, by + 22)], 5, C_RIBBON, taper=.2, wmin=.5, seed=sd + 5))
    out.append(line([(3, by + 4), (16, by + 20)], 5, C_RIBBON, taper=.2, wmin=.5, seed=sd + 6))
    out.append(line([(-W + 12, -H + 12), (-W + 12, -H + 52)], 5, mix(C_BOX, "#ffffff", .4), taper=.5, wmin=.3, seed=sd + 7, peak=.5))
    return _tf("".join(out), x, y, k, rot)


# ───────────────────────────── корзина ─────────────────────────────

def _basket_geo():
    return dict(TW=86.0, BW=68.0, H=100.0, RY=16.0)


def basket_back(x, y, k=1.0, sag=0.0, seed=0):
    """Задняя часть: ручка и тёмное нутро за вещами."""
    sd = 9100 + seed * 11
    g = _basket_geo()
    TW, H, RY = g["TW"], g["H"] - 8 * sag, g["RY"]
    out = []
    # ручка — арка
    hp = [(-TW + 6, -H), (-TW + 2, -H - 52), (-30, -H - 88), (0, -H - 96), (30, -H - 88), (TW - 2, -H - 52), (TW - 6, -H)]
    out.append(line(hp, 12, C_WICKER_SH, taper=0.0, wmin=1.0, seed=sd))
    out.append(line(hp, 6, C_WICKER, taper=0.0, wmin=1.0, seed=sd + 1))
    out.append(shape(ellipse_pts(0, -H, TW, RY, 24), C_WICKER_IN, "", w=3.4, seed=sd + 2))
    return _tf("".join(out), x, y, k)


def basket_front(x, y, k=1.0, sag=0.0, seed=0):
    sd = 9200 + seed * 11
    g = _basket_geo()
    TW, BW, H, RY = g["TW"], g["BW"], g["H"] - 8 * sag, g["RY"]
    out = []
    body = [(-TW, -H, 1), (TW, -H, 1), (BW, 0, 1), (-BW, 0, 1)]
    # плетение: ряды кирпичиков
    inner = blob([(TW * .35, -H), (TW + 2, -H), (BW + 2, 0), (BW * .3, 0)], C_WICKER_SH)
    rows = 6
    for r in range(rows):
        yy = -H + (r + 1) * H / (rows + 0.3)
        out_ = lib.mix(C_WICKER, C_WICKER_SH, .0)
        inner += line([(-TW - 4, yy), (TW + 4, yy)], 3.2, C_WICKER_SH, taper=0.0, wmin=1.0, seed=sd + 40 + r)
        for c in range(-6, 7):
            xx = c * 15 + (7.5 if r % 2 else 0)
            inner += line([(xx, yy - H / (rows + .3)), (xx, yy)], 2.6, C_WICKER_SH, taper=.1, wmin=.7, seed=sd + 60 + r * 20 + c, op=.9)
    out.append(shape(body, C_WICKER, inner, w=3.8, seed=sd))
    # передний край ободка
    rim = [(-TW - 3, -H - 6, 1), (TW + 3, -H - 6, 1), (TW + 3, -H + 8, 1), (-TW - 3, -H + 8, 1)]
    out.append(shape(rim, C_WICKER, blob(rect_pts(TW * .4, -H - 6, TW + 4, -H + 9), C_WICKER_SH), w=3.4, seed=sd + 1))
    return _tf("".join(out), x, y, k)


def basket(x, y, k=1.0, inside="", sag=0.0, seed=0):
    """Корзина целиком. inside — SVG вещей в МИРОВЫХ координатах кадра (рисуются между задней и передней стенкой)."""
    return basket_back(x, y, k, sag, seed) + inside + basket_front(x, y, k, sag, seed)


# ───────────────────────────── шесть вещей ─────────────────────────────

def _book(sd):
    W, H = 64.0, 84.0
    out = []
    out.append(shape([(-W / 2, 0, 1), (W / 2, 0, 1), (W / 2, -H, 1), (-W / 2, -H, 1)], "#3E8E8A",
                     blob(rect_pts(-W / 2, -H, -W / 2 + 10, 0), "#2B6E6A") + blob(rect_pts(W / 2 - 8, -H, W / 2 + 2, 0), "#2F7773"), w=3.6, seed=sd))
    out.append(blob(rect_pts(W / 2 - 3, -H + 5, W / 2 + 8, -4), "#FFFDF3"))
    out.append(line([(W / 2 + 6, -H + 6), (W / 2 + 6, -5)], 2.2, INK_L, taper=0, wmin=1, seed=sd + 1))
    out.append(shape(ellipse_pts(2, -H * .55, 15, 15, 12), "#F3C23B", blob(ellipse_pts(5, -H * .55 + 2, 8, 8, 10), "#D9A220"), w=2.6, seed=sd + 2))
    out.append(line([(-16, -H + 14), (20, -H + 14)], 3.0, "#F3E3A0", taper=0, wmin=1, seed=sd + 3))
    out.append(line([(-16, -12), (20, -12)], 3.0, "#F3E3A0", taper=0, wmin=1, seed=sd + 4))
    out.append(shape([(14, -H, 1), (22, -H, 1), (22, -H + 26), (18, -H + 20), (14, -H + 26)], "#D9506B", "", w=2.2, seed=sd + 5))
    return "".join(out)


def _sneaker(sd):
    out = []
    sole = [(-50, -6, 1), (48, -6, 1), (54, -14), (50, -2, 1), (-50, 0, 1), (-54, -8)]
    up = [(-50, -8, 1), (-50, -46), (-36, -56), (-16, -50), (6, -42), (30, -30), (50, -22), (54, -10, 1)]
    out.append(shape(up, "#3F6FD1", blob([(-6, -42), (30, -30), (50, -22), (54, -10), (-6, -10)], "#3459A8") +
                     blob([(28, -30), (50, -22), (54, -10), (24, -10)], "#F1F1F1"), w=3.6, seed=sd))
    out.append(shape([(-54, -4, 1), (56, -4, 1), (56, -16, 1), (-54, -16, 1)], "#F6F6F2", blob(rect_pts(-54, -8, 56, -4), "#D7D7CF"), w=3.4, seed=sd + 1))
    for j in range(4):
        out.append(line([(-6 + 8 * j, -44 + 3 * j), (-2 + 8 * j, -34 + 3 * j)], 3.0, "#F6F6F2", taper=.1, wmin=.8, seed=sd + 5 + j))
    out.append(shape([(-50, -50, 1), (-30, -58, 1), (-26, -42), (-46, -34)], "#2F58B5", "", w=2.6, seed=sd + 4))
    return "".join(out)


def _kettle(sd):
    out = []
    out.append(shape([(30, -42), (62, -76, 1), (70, -70, 1), (44, -30)], "#D8503F", "", w=3.2, seed=sd + 1))
    out.append(shape([(-44, -78), (-66, -46), (-60, -30), (-42, -50)], "#2B2B2E", "", w=3.0, seed=sd + 2))
    body = ellipse_pts(0, -36, 44, 36, 20) + []
    out.append(shape([(-34, 0, 1), (34, 0, 1), (46, -20), (46, -50), (30, -72), (-30, -72), (-46, -50), (-46, -20)], "#D8503F",
                     blob([(14, -72), (30, -72), (46, -50), (46, -20), (34, 0), (14, 0)], "#AE3A2D"), w=3.8, seed=sd))
    out.append(line([(-34, -62), (-40, -30)], 5, "#F0A394", taper=.5, wmin=.3, seed=sd + 3, peak=.5))
    out.append(shape([(-22, -72, 1), (22, -72, 1), (16, -84), (-16, -84)], "#B8382A", "", w=3.0, seed=sd + 4))
    out.append(shape(ellipse_pts(0, -92, 7, 7, 10), "#2B2B2E", "", w=2.4, seed=sd + 5))
    out.append(line([(-30, -34), (30, -34)], 3, "#F3E3A0", taper=0, wmin=1, seed=sd + 6))
    return "".join(out)


def _scarf(sd):
    out = []
    cols = ["#7D5BA6", "#F3C23B"]
    body = [(-44, 0, 1), (44, 0, 1), (46, -34), (-46, -34)]
    inner = "".join(blob(rect_pts(-46 + 22 * j, -36, -46 + 22 * j + 8, 2), cols[1]) for j in range(5))
    out.append(shape(body, cols[0], inner, w=3.6, seed=sd))
    out.append(shape([(-44, -34, 1), (44, -34, 1), (36, -50), (-36, -50)], mix(cols[0], "#ffffff", .15),
                     "".join(blob(rect_pts(-46 + 22 * j + 4, -52, -46 + 22 * j + 12, -32), cols[1]) for j in range(4)), w=3.4, seed=sd + 1))
    out.append(shape([(30, -6, 1), (58, -6, 1), (62, 22), (36, 24)], cols[0], blob(rect_pts(40, -6, 48, 24), cols[1]), w=3.2, seed=sd + 2))
    for j in range(5):
        out.append(line([(38 + j * 5, 22), (38 + j * 5 + 1, 32)], 2.6, cols[0], taper=0.2, wmin=.7, seed=sd + 10 + j))
    return "".join(out)


def _lamp(sd):
    out = []
    out.append(shape(ellipse_pts(0, -6, 30, 7, 14), "#6A6F7A", blob(ellipse_pts(0, -4, 22, 3.5, 12), "#4E525B"), w=3.0, seed=sd))
    out.append(line([(0, -8), (-4, -52), (6, -84)], 6, "#4E525B", taper=0.0, wmin=1.0, seed=sd + 1))
    out.append(shape([(-14, -86, 1), (14, -86, 1), (34, -112, 1), (-34, -112, 1)], "#F2C94C", blob([(8, -86), (14, -86), (34, -112), (14, -112)], "#D9A826"), w=3.4, seed=sd + 2))
    out.append(shape(ellipse_pts(0, -112, 34, 7, 16), "#FFF1B0", "", w=2.8, seed=sd + 3))
    out.append(line([(-14, -104), (-6, -90)], 3.6, "#FFF3C4", taper=.5, wmin=.3, seed=sd + 4))
    return "".join(out)


def _teddy(sd):
    BR, BRS, SN = "#A8744A", "#845631", "#E8CFA8"
    out = []
    out.append(shape(ellipse_pts(-20, -6, 14, 9, 10), BR, "", w=3.0, seed=sd + 1))
    out.append(shape(ellipse_pts(20, -6, 14, 9, 10), BR, "", w=3.0, seed=sd + 2))
    out.append(shape(ellipse_pts(0, -32, 28, 30, 18), BR, blob(ellipse_pts(16, -30, 14, 24, 12), BRS) + blob(ellipse_pts(0, -26, 14, 17, 12), SN), w=3.6, seed=sd))
    out.append(shape(ellipse_pts(-28, -44, 9, 13, 10, rot=-26), BR, "", w=3.0, seed=sd + 3))
    out.append(shape(ellipse_pts(28, -44, 9, 13, 10, rot=26), BR, "", w=3.0, seed=sd + 4))
    out.append(shape(ellipse_pts(-16, -78, 9, 9, 10), BR, blob(ellipse_pts(-16, -77, 4.5, 4.5, 8), SN), w=3.0, seed=sd + 5))
    out.append(shape(ellipse_pts(16, -78, 9, 9, 10), BR, blob(ellipse_pts(16, -77, 4.5, 4.5, 8), SN), w=3.0, seed=sd + 6))
    out.append(shape(ellipse_pts(0, -64, 24, 22, 18), BR, blob(ellipse_pts(11, -62, 12, 18, 10), BRS), w=3.6, seed=sd + 7))
    out.append(shape(ellipse_pts(0, -56, 11, 8, 12), SN, "", w=2.6, seed=sd + 8))
    out.append(shape(ellipse_pts(0, -60, 4, 3, 8), "#3A2A22", "", w=1.6, seed=sd + 9))
    for sx in (-8, 8):
        out.append(blob(ellipse_pts(sx, -70, 2.8, 3.2, 8), "#2B2B2E"))
    out.append(line([(0, -57), (0, -53), (-4, -50)], 2.2, "#3A2A22", taper=.2, wmin=.6, seed=sd + 10))
    out.append(shape([(-12, -44, 1), (12, -44, 1), (8, -38), (0, -34), (-8, -38)], "#D9506B", "", w=2.4, seed=sd + 11))
    return "".join(out)


INK_L = lib.INK
_ITEM_FN = {"book": _book, "sneaker": _sneaker, "kettle": _kettle, "scarf": _scarf, "lamp": _lamp, "teddy": _teddy}


def item(name, x, y, k=1.0, rot=0.0, seed=0):
    """Одна из шести вещей корзины (дно в (x, y)); размер при k=1 одинаков во всех клипах (ITEM_H)."""
    return _tf(_ITEM_FN[name](9400 + ITEMS.index(name) * 100 + seed), x, y, k, rot)


def spark(x, y, k=1.0, u=1.0, col="#FFD54A"):
    """Четырёхлучевой блик (u 0…1)."""
    r = 26 * max(0.0, min(1.0, math.sin(u * math.pi)))
    if r < 1:
        return ""
    pts = [(0, -r), (r * .2, -r * .2), (r, 0), (r * .2, r * .2), (0, r), (-r * .2, r * .2), (-r, 0), (-r * .2, -r * .2)]
    return _tf(blob([(a, b, 1) for a, b in pts], col), x, y, k)
