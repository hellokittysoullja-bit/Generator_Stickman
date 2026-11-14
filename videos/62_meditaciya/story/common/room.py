"""Комната Димы для медитации (рилс 62 «медитация», пишет группа E; берут B — s10, D — s14, F — s15/s17/s18).

Подключение:  sys.path.insert(0, COMMON); import room as R   (COMMON = videos/62_meditaciya/story/common; lib/props рядом).
Основа — common/room.py рилса 61 (стена, пол-доски, окно, торшер из props). Мир шире кадра: x от −500 до 1600, y от −300 до 2300;
камера — снаружи (lib.cam). Букв и цифр нигде нет: книги — цветные корешки, картинка — горы и солнце.
Все функции возвращают строку SVG в мировых координатах (градиенты — динамические defs, вызывать после lib.dyn_begin()).

Уголок медитации: окно слева, торшер справа, полка над головой Димы, монстера в горшке у окна, коврик и круглая подушка по центру.
Режим mode: "evening" — синий вечер в окне, торшер горит (небольшое пятно света на полу и трапеция на стене с чёткими краями,
без огромных мягких овалов), свечка на полке горит; "morning" — дневное небо, торшер выключен, на полу СОЛНЕЧНАЯ ПОЛОСА формы окна
(четыре стекла с тенью крестовины, чёткие края).

    WALL_Y=1380  низ стены (плинтус), ниже пол
    CUSH=(540, 1650), CUSH_K=1.5, CUSH_H=1.5  подушка-пуф: центр дна, масштаб (Ø 450), высота ×1.5 (верх ≈ 1470)
    seat(sy=1) -> (x, y)          таз Димы в лотосе на подушке (people.figure(..., x, y, s≈1.0, **people.lotus_kw(...)))
                                  таз выше верха подушки на 175: скрещённые голени лежат на подушке, её бок виден под ними.
                                  Дима масштаба 1.0 в лотосе: от y−730 (макушка) до y+245 (ступни) ≈ 975 px (51 % кадра при s=1)
    MAT=(540, 1655)               центр коврика
    WIN=(130, 1050, 420, 620)     окно: центр низа рамы, ширина, высота
    LAMP=(950, 1470, 1.75)        торшер: дно и масштаб (абажур ≈ y 790…850)
    SHELF=(330, 760, 400)         полка: левый и правый край, высота доски
    CAM_WIDE=(540, 1060, 1.0)     камера общего плана (cx, cy, s): Дима ≈ 51 %, окно, торшер, полка в кадре
    CAM_MID=(560, 980, 1.22)      средний план (Дима ≈ 62 %, лицо и колени)

    wall_floor(mode)              стена (краска одна, свет режима), плинтус, пол-доски
    window(t, mode)               окно вечер/утро (props.window), облака-звёзды живут от t
    sun_strip(t)                  утренняя полоса солнца на полу: четыре стекла формы окна с крестовиной (чёткие края, сплошной цвет)
    lamp(mode, flick=0)           торшер; вечером — свет: трапеция на стене над абажуром и пятно на полу (возвращает dict(light, lamp))
    shelf(t, mode)                полка: книги без надписей, свеча (вечером горит), поющая чаша, суккулент; картинка с горами над
    plant(t, sway=0)              монстера в горшке у окна (листья качаются от t и толчка sway)
    mat_layer()                   коврик (props.mat)
    cushion_layer(sy=1, dx=0)     подушка (props.cushion), sy — сплющивание при приземлении
    room_bg(t, mode, flick, sway) всё, кроме подушки и людей: dict(bg=стена…коврик, light=свет торшера поверх стены,
                                  front=передний лист монстеры (поверх Димы не мешает — он слева у края))
    scene(t, mode, figure="", sy=1, flick=0, sway=0)  целиком: bg + подушка + figure + front
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import props as PR  # noqa: E402
from lib import INK, blob, ellipse_pts, f, line, rect_pts, shape  # noqa: E402

WALL_Y = 1380.0
CUSH = (540.0, 1650.0)
CUSH_K = 1.5
CUSH_H = 1.5
MAT = (540.0, 1655.0)
WIN = (130.0, 1050.0, 420.0, 620.0)
LAMP = (950.0, 1470.0, 1.75)
SHELF = (330.0, 760.0, 400.0)
CAM_WIDE = (540.0, 1060.0, 1.0)
CAM_MID = (560.0, 980.0, 1.22)

PAINT = {"evening": ("#8e98b8", "#7a83a3", "#6c7594"), "morning": ("#cfdbe4", "#b9c8d4", "#a9b9c6")}
FLOOR = {"evening": ("#9a6a44", "#ab7a50", "#6a4228"), "morning": ("#c8915c", "#d6a06a", "#8a5b34")}
BASE_C = {"evening": "#d9d0c0", "morning": "#f3ede0"}


def rs(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


def seat(sy=1.0):
    """Таз Димы на подушке (sy — сплющивание подушки)."""
    top = CUSH[1] - 80 * CUSH_K * CUSH_H * sy
    return CUSH[0], top - 175


# ═════════════════════════ стена и пол ═════════════════════════
def wall_floor(mode="evening"):
    w0, w1, w2 = PAINT[mode]
    o = []
    g = lib.lin_grad([(0, w1, 1), (.55, w0, 1), (1, w2, 1)], 0, -300, 0, WALL_Y, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="-1400" width="4800" height="{f(WALL_Y + 1400)}" fill="url(#{g})"/>')
    # тонкие панели-рейки внизу стены (без узора-шума)
    for i in range(-8, 24):
        x = i * 96.0
        o.append(line([(x, 1010), (x + .8, WALL_Y - 40)], w=2.0, color=w2, taper=0.0, wmin=1, seed=40 + i, op=.55))
    o.append(shape(rect_pts(-900, 996, 2500, 1012), lib.mix(w0, "#ffffff", .25), w=2.6, seed=60))
    bc = BASE_C[mode]
    o.append(shape(rect_pts(-900, WALL_Y - 42, 2500, WALL_Y + 6), bc, blob(rect_pts(-900, WALL_Y - 8, 2500, WALL_Y + 6), lib.mul(bc, (.86, .86, .86))),
                   w=3.4, seed=70))
    fa, fb, fl = FLOOR[mode]
    gf = lib.lin_grad([(0, fa, 1), (1, fb, 1)], 0, WALL_Y, 0, 2300, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="{f(WALL_Y + 6)}" width="4800" height="{f(2400 - WALL_Y)}" fill="url(#{gf})"/>')
    ys = [WALL_Y + 6, 1385, 1455, 1545, 1660, 1810, 2000, 2240]
    for k, y in enumerate(ys[1:]):
        o.append(line([(-900, y), (2500, y)], w=3.0, color=fl, taper=0.0, wmin=1, seed=80 + k, op=.6))
    r = rs(5)
    for k, (ya, yb) in enumerate(zip(ys[:-1], ys[1:])):
        for j in range(6):
            x = r.uniform(-700, 1800)
            o.append(line([(x, ya), (x + r.uniform(-4, 4), yb)], w=2.4, color=fl, taper=0.0, wmin=1, seed=90 + k * 7 + j, op=.5))
    return "".join(o)


# ═════════════════════════ окно и солнце ═════════════════════════
def window(t, mode="evening"):
    x, y, w, h = WIN
    return PR.window(x, y, w, h, mode="evening" if mode == "evening" else "day", t=t, seed=3, curtain=True)


def _win_quad():
    """Параллелограмм солнечного пятна на полу: A — от левого нижнего угла окна, u — вдоль ширины окна, v — вдоль высоты."""
    A = np.array([-90.0, 1690.0])
    U = np.array([300.0, 0.0])
    V = np.array([250.0, 220.0])
    return A, U, V


def sun_strip(t=0.0):
    """Утреннее солнце на полу: четыре стекла окна (крестовина — тень), чёткие края, сплошной тёплый цвет."""
    fa = FLOOR["morning"][1]
    col = lib.mix(fa, "#ffe6a8", .62)
    col2 = lib.mix(fa, "#fff2cc", .8)
    A, U, V = _win_quad()
    o = []
    breath = .01 * math.sin(t * .9)
    for (u0, u1) in ((0.0, .47), (.53, 1.0)):
        for (v0, v1) in ((0.0, .43), (.5, 1.0)):
            pts = [tuple(A + U * u0 + V * v0) + (1,), tuple(A + U * u1 + V * v0) + (1,), tuple(A + U * u1 + V * v1) + (1,), tuple(A + U * u0 + V * v1) + (1,)]
            o.append(blob(pts, col))
            # блик на ближнем крае стекла
            q = [tuple(A + U * (u0 + .02) + V * (v1 - .1 - breath)) + (1,), tuple(A + U * (u1 - .02) + V * (v1 - .1 - breath)) + (1,),
                 tuple(A + U * (u1 - .02) + V * (v1 - .04)) + (1,), tuple(A + U * (u0 + .02) + V * (v1 - .04)) + (1,)]
            o.append(blob(q, col2))
    # пылинки в утреннем воздухе над пятном (крошечные точки, живут от t)
    for i in range(7):
        px = 140 + 70 * i + 18 * math.sin(t * .7 + i * 1.9)
        py = 1260 + 40 * ((i * 37) % 5) - 22 * math.sin(t * .5 + i)
        o.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="3.2" fill="#fff6d8"/>')
    return "".join(o)


# ═════════════════════════ торшер ═════════════════════════
def lamp(mode="evening", flick=0.0):
    """Торшер справа. Вечером — свет с чёткими краями: трапеция на стене над абажуром (свет из открытого верха) и небольшое
    пятно на полу под ним. Возвращает dict(light=свет (класть после стены, до предметов), lamp=торшер)."""
    x, y, k = LAMP
    on = 1.0 if mode == "evening" else 0.0
    on *= 1.0 - .08 * flick
    lt = ""
    if on > 0:
        w0 = PAINT[mode][0]
        top = y - 388 * k
        wc = lib.mix(w0, "#e2c48e", min(1.0, .9 * on))      # тёплый свет на холодной стене: явный кремовый, а не серая смесь
        wc2 = lib.mix(w0, "#f6e2ae", min(1.0, .95 * on))
        lt += blob([(x - 70 * k, top, 1), (x + 70 * k, top, 1), (x + 112 * k, top - 92 * k, 1), (x - 112 * k, top - 92 * k, 1)], wc)
        lt += blob([(x - 50 * k, top, 1), (x + 50 * k, top, 1), (x + 74 * k, top - 52 * k, 1), (x - 74 * k, top - 52 * k, 1)], wc2)
        fl = lib.mix(FLOOR[mode][1], "#ffd98a", .4 * on)
        lt += blob(ellipse_pts(x - 10, y + 6, 150, 34, 24), fl)
        # свет под абажуром на стене (небольшой веер вниз с чёткими краями)
        bot = y - 330 * k
        lt += blob([(x - 52 * k, bot, 1), (x + 52 * k, bot, 1), (x + 80 * k, bot + 70 * k, 1), (x - 80 * k, bot + 70 * k, 1)], lib.mix(w0, "#dcc08e", .75 * on))
    return dict(light=lt, lamp=PR.lamp_floor(x, y, k, on=on, seed=2))


# ═════════════════════════ полка и картинка ═════════════════════════
def _book(x, y, w, h, col, tilt=0.0, seed=0):
    sh = lib.mul(col, (.78, .78, .8))
    pts = [(-w / 2, -h, 1), (w / 2, -h, 1), (w / 2, 0, 1), (-w / 2, 0, 1)]
    inner = blob(rect_pts(w / 2 - w * .3, -h, w / 2, 0), sh) + blob(rect_pts(-w / 2, -h * .82, w / 2, -h * .76), lib.mix(col, "#f6e7c4", .5))
    inner += blob(rect_pts(-w / 2, -h * .22, w / 2, -h * .16), lib.mix(col, "#f6e7c4", .5))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(tilt)})">{shape(pts, col, inner, w=3.0, seed=seed)}</g>'


def shelf(t, mode="evening"):
    x0, x1, y = SHELF
    o = []
    # картинка над полкой: горы и солнце (без букв)
    px, py, pw, ph = 545.0, 230.0, 200.0, 150.0
    inner = blob(rect_pts(px - pw / 2, py - ph / 2, px + pw / 2, py + ph / 2), "#f3e3c3")
    inner += blob(ellipse_pts(px + 40, py - 20, 22, 22, 14), "#f2a65c")
    inner += shape([(px - pw / 2 - 4, py + ph / 2 + 4, 1), (px - 50, py - 10, 1), (px - 10, py + 30, 1), (px + 30, py - 2, 1), (px + pw / 2 + 4, py + 50, 1),
                    (px + pw / 2 + 4, py + ph / 2 + 4, 1)], "#6f9a8b", w=2.4, seed=301)
    o.append(shape(rect_pts(px - pw / 2 - 16, py - ph / 2 - 16, px + pw / 2 + 16, py + ph / 2 + 16), "#c7a374",
                   blob(rect_pts(px - pw / 2 - 16, py + ph / 2, px + pw / 2 + 16, py + ph / 2 + 16), "#a58252"), w=3.4, seed=300))
    o.append(shape(rect_pts(px - pw / 2, py - ph / 2, px + pw / 2, py + ph / 2), "#f3e3c3", inner, w=2.8, seed=302))
    # кронштейны и доска
    for bx in (x0 + 50, x1 - 50):
        o.append(shape([(bx - 8, y), (bx + 8, y), (bx + 8, y + 70), (bx - 8, y + 54)], "#4b505e", w=2.6, seed=310 + int(bx)))
    o.append(shape(rect_pts(x0, y - 4, x1, y + 22, 3), "#b27c4c", blob(rect_pts(x0, y + 10, x1, y + 22), "#8a5b32"), w=3.4, seed=320))
    # книги без надписей
    bx = x0 + 30
    for i, (w, h, col, tl) in enumerate(((30, 120, "#c8553d", 0), (26, 104, "#4a6fa5", 0), (34, 128, "#5c9a78", 0), (28, 110, "#d4a23e", 12))):
        o.append(_book(bx + w / 2 + (8 if tl else 0), y - 4, w, h, col, tilt=tl, seed=330 + i))
        bx += w + 2
    # поющая чаша на подставке
    cx = 560.0
    o.append(shape([(cx - 52, y - 46, 1), (cx + 52, y - 46, 1), (cx + 40, y - 14), (cx + 16, y - 4, 1), (cx - 16, y - 4, 1), (cx - 40, y - 14)], "#c9a24a",
                   blob([(cx - 60, y - 30), (cx + 60, y - 30), (cx + 60, y), (cx - 60, y)], "#a8842e") +
                   line([(cx - 40, y - 38), (cx - 10, y - 36)], 3.0, "#f2d77e", seed=342, op=.9), w=3.2, seed=340))
    o.append(shape(ellipse_pts(cx, y - 46, 52, 8, 16), "#7a5a1c", w=2.4, seed=341))
    # свеча (вечером горит маленьким язычком) и суккулент
    sx = 668.0
    o.append(shape(rect_pts(sx - 16, y - 70, sx + 16, y - 4, 4), "#f4ecdc", blob(rect_pts(sx + 6, y - 70, sx + 16, y - 4), "#ddd0b8"), w=2.8, seed=350))
    o.append(line([(sx, y - 70), (sx + 1, y - 80)], 2.4, INK, seed=351))
    if mode == "evening":
        fl = 1 + .08 * math.sin(t * 13) + .05 * math.sin(t * 7.3)
        sway = 2.0 * math.sin(t * 5.1)
        fpts = [(sx, y - 76, 1), (sx + 7 * fl, y - 88 * 1), (sx + sway, y - 76 - 26 * fl, 1), (sx - 7 * fl, y - 88)]
        o.append(shape(fpts, "#f6c24a", blob(ellipse_pts(sx, y - 84, 3.4, 6 * fl, 8), "#fff3c6"), w=2.0, seed=352))
    gx = 728.0
    o.append(shape([(gx - 22, y - 44, 1), (gx + 22, y - 44, 1), (gx + 16, y - 4, 1), (gx - 16, y - 4, 1)], "#c8634a", w=2.6, seed=360))
    for j, (dx, h) in enumerate(((-12, 30), (0, 40), (12, 28))):
        o.append(shape(ellipse_pts(gx + dx, y - 44 - h / 2, 9, h / 2, 10), "#6fa35e", w=2.2, seed=361 + j))
    return "".join(o)


# ═════════════════════════ монстера ═════════════════════════
def _leaf(x, y, L, ang, col, seed, cuts=3):
    """Лист монстеры: сердце с вырезами, черешок от (x, y) под углом ang (градусы, 0 — вправо)."""
    a = math.radians(ang)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])
    base = np.array([x, y]) + d * L * .55
    pts = []
    for i in range(25):
        th = -math.pi + 2 * math.pi * i / 24
        r = L * .5 * (1 - .18 * math.cos(th))
        p = base + d * (r * math.cos(th) * .95) + n * (r * math.sin(th) * .78)
        pts.append(tuple(p))
    sh = lib.mul(col, (.8, .84, .8))
    inner = blob([tuple(base - n * L * .5 - d * L), tuple(base + d * L), tuple(base - n * L * .02 + d * L)], sh, .9)
    for c in range(cuts):
        for sg in (-1, 1):
            q = base + d * (L * (-.22 + .2 * c)) + n * sg * L * .3
            q2 = base + d * (L * (-.18 + .2 * c)) + n * sg * L * .48
            inner += line([tuple(q), tuple(q2)], 7, PAINT_LEAF_GAP[0], taper=.2, wmin=.5, seed=seed + 10 + c * 2 + (sg > 0))
    inner += line([tuple(base - d * L * .45), tuple(base + d * L * .42)], 2.4, lib.mul(col, (.7, .74, .7)), seed=seed + 30, op=.8)
    o = line([(x, y), tuple(base - d * L * .42)], 7, "#4f7f45", taper=.2, wmin=.6, seed=seed + 1)
    o += shape(pts, col, inner, w=3.2, seed=seed)
    return o


PAINT_LEAF_GAP = ["#8e98b8"]


def plant(t, sway=0.0, mode="evening"):
    PAINT_LEAF_GAP[0] = PAINT[mode][0]
    x, y = 105.0, 1520.0
    o = []
    for j, (ang, L, col) in enumerate(((-140, 230, "#4f8a4a"), (-105, 260, "#5c9a52"), (-70, 240, "#4f8a4a"), (-40, 200, "#68a85c"), (-160, 190, "#68a85c"))):
        s = (3.0 + j * .6) * math.sin(t * (.8 + .13 * j) + j) + sway * (1 - .15 * j)
        o.append(_leaf(x + 6 * (j - 2), y - 150, L, ang + s, col, 400 + j * 40))
    # горшок
    o.append(shape([(x - 90, y - 170, 1), (x + 90, y - 170, 1), (x + 70, y, 1), (x - 70, y, 1)], "#d9795e",
                   blob([(x + 30, y - 170), (x + 100, y - 170), (x + 80, y), (x + 40, y)], "#b85e45") +
                   blob(rect_pts(x - 100, y - 150, x + 100, y - 134), "#b85e45"), w=3.6, seed=480))
    o.append(shape(rect_pts(x - 100, y - 186, x + 100, y - 158, 4), "#e48b6e", w=3.2, seed=481))
    return "".join(o)


# ═════════════════════════ коврик, подушка, сборка ═════════════════════════
def mat_layer():
    return PR.mat(MAT[0], MAT[1], 1.35, w=640, col="#6fa58a")


def cushion_layer(sy=1.0, dx=0.0):
    return PR.cushion(CUSH[0] + dx, CUSH[1], CUSH_K, sy=CUSH_H * sy)


def room_bg(t, mode="evening", flick=0.0, sway=0.0):
    """Фон уголка без подушки и людей: dict(bg, front). Порядок в клипе: bg → подушка → Дима → front."""
    lp = lamp(mode, flick)
    o = [f'<rect x="-1600" y="2200" width="4800" height="1400" fill="{FLOOR[mode][1]}"/>', wall_floor(mode), lp["light"], window(t, mode), shelf(t, mode)]
    if mode == "morning":
        o.append(sun_strip(t))
    o += [lp["lamp"], plant(t, sway, mode), mat_layer()]
    return dict(bg="".join(o), front="")


def scene(t, mode="evening", figure="", sy=1.0, flick=0.0, sway=0.0):
    r = room_bg(t, mode, flick, sway)
    return r["bg"] + cushion_layer(sy) + figure + r["front"]
