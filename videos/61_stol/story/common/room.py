"""Комната взрослого Димы с ДВУМЯ столами (рилс 61 «стол», пишет группа E; берут B — дверь для s03, F — тёплый стол для s17/s18).

Подключение:  sys.path.insert(0, COMMON); import room as R   (COMMON = videos/61_stol/story/common; lib/ink рядом).
Мир шире кадра: x от −700 до 2200, y от −300 до 2200; камера накладывается снаружи (lib.cam). Дневной свет из окна, тёплая
настольная лампа на творческом столе. Букв и цифр нигде нет: наброски — линии и значки, стикеры — цветные квадраты.
Все функции возвращают строку SVG в мировых координатах (градиенты — динамические defs, вызывать после lib.dyn_begin()).

Вид спереди: стол — передняя кромка столешницы на DESK_TOP, видна полоса верха глубиной DESK_D (верх слегка сверху).
Предметы на столе ставить дном на линию y ∈ [DESK_TOP − DESK_D + 10, DESK_TOP − 6] (чем ниже — тем ближе к зрителю).

    FL=1560 пол под ногами (низ ножек), WALL_Y=1440 низ стены, DESK_TOP=960 передняя кромка столешниц, DESK_D=120 глубина верха
    CREATIVE=(−540, 380)  творческий стол у окна (слева)      CLEAN=(760, 1660) чистый стол у другой стены (справа)
    WIN=(−470, 200, 150, 780) окно над творческим столом      SKETCH_WALL=(170, 250, 420, 800) стена с набросками справа от окна
    LAMP=(170, DESK_TOP−70) дно настольной лампы на творческом столе, LAMP_POOL — центр и радиусы светового круга на столе
    MID_X=570  место крутящегося стула между столами (общий план); seat_y(bs) — высота сиденья под таз сидящего Димы масштаба bs
    DOOR=(1760, 300, 2120, WALL_Y) проём двери справа от чистого стола

    wall_floor()                         стена (шалфейная, обои-ёлочка), плинтус, пол-доски, круглый ковёр под стулом
    window(t, dim=0)                     окно: дневное небо, облака плывут, крыши и дерево; рама, подоконник, штора
    sketches(t, fly=0.0, seed_t=None)    наброски на стене (без букв): лампочка, спираль, ракета-штрих, звезда, волна, кот-силуэт; кнопки
                                          fly 0…1 — листы отрываются и взлетают веером (для «творческим» s14)
    sketch(x, y, w, h, rot, kind, seed)  один набросок (центр, размер, поворот), kind 0…5
    stickers(t, pop=0.0)                 цветные стикеры без надписей на стене у набросков
    desk(x0, x1, kind)                   стол: dict(back=задние ножки и верх, front=передняя кромка и ящики, legs=передние ножки)
                                          kind "creative" (тёплое дерево, царапины, кольца от кружек) | "clean" (светлое, гладкое)
    desk_lamp(on=1.0, flick=0.0, tilt=0) настольная лампа на творческом столе: dict(lamp=..., pool=...) — pool (небольшой круг света
                                          с чёткой формой) класть на стол ДО предметов, lamp — после
    clean_wall(t)                        над чистым столом: полка с тремя одинаковыми папками без надписей, рамка с волной, часы без цифр
    swivel_chair(x, seat_y, k=1.0, spin=0.0, side=1)  крутящийся стул: dict(base=крестовина и газлифт, seat=сиденье, back=спинка)
                                          spin — поворот в оборотах (0…1…): спинка сужается и меняет сторону, лучи крестовины бегут
    door(t, open_=1.0)                   проём двери: наличник, открытая створка, светлый коридор за ней (фигуру ставить между
                                          door_back() и door_front())
    door_back(t, open_) / door_front(open_)   слои двери: коридор и створка / наличник поверх фигуры
    creative_clutter(t, k, jump)         бардак на творческом столе из common/props.py (гора бумажек, кружки, провода, стикер); справа у лампы
                                          свободно под рисование; jump — подскок предметов от хлопка
    clean_top(t, checks, u)              чистый стол: закрытый ноутбук, ровная стопка, лист с чекбоксами (props.checklist) у левого края
    room_bg(t, lamp_on, flick, fly, pop, items=False)  весь фон: стена, окно, наброски, стикеры, полка, оба стола (items=True — с предметами),
                                          лампа; возвращает dict(bg=..., lamp=..., pool=..., creative=desk dict, clean=desk dict)
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
from lib import INK, blob, ellipse_pts, f, line, rect_pts, shape  # noqa: E402

FL = 1560.0
WALL_Y = 1440.0
DESK_TOP = 960.0
DESK_D = 120.0
DESK_TH = 36.0
CREATIVE = (-540.0, 380.0)
CLEAN = (760.0, 1660.0)
WIN = (-470.0, 200.0, 150.0, 780.0)
SKETCH_WALL = (170.0, 250.0, 420.0, 800.0)
LAMP = (170.0, DESK_TOP - 70.0)
LAMP_POOL = (230.0, DESK_TOP - 52.0, 150.0, 40.0)
MID_X = 570.0
DOOR = (1760.0, 300.0, 2120.0, WALL_Y)

WALL, WALL_SH, WALL_LN = "#a9bc9f", "#8fa486", "#7d9274"
FLOOR_A, FLOOR_B, FLOOR_LN = "#b07a4c", "#c38c5a", "#7a4d2c"
BASE_C = "#efe6d2"
W_CRE, W_CRE_SH, W_CRE_HI = "#b8733f", "#8a5128", "#d49260"
W_CLN, W_CLN_SH, W_CLN_HI = "#e9dcc4", "#c9b796", "#fbf2e0"


def rs(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


def seat_y(bs=1.0):
    """Высота таза сидящего Димы масштаба bs, чтобы ступни стояли на FL (голень 300, бедро горизонтально)."""
    return FL - 392.0 * bs


# ═════════════════════════ стена и пол ═════════════════════════
def wall_floor():
    o = []
    g = lib.lin_grad([(0, "#c3d2b6", 1), (.6, WALL, 1), (1, WALL_SH, 1)], 0, -300, 0, WALL_Y, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-400" width="3400" height="{f(WALL_Y + 400)}" fill="url(#{g})"/>')
    # обои: тонкие вертикальные полосы и мелкие веточки-ёлочки
    r = rs(3)
    for i in range(-10, 30):
        x = i * 110.0
        o.append(line([(x, -400), (x + 1.2, WALL_Y)], w=1.6, color=WALL_LN, taper=0.0, wmin=1, seed=40 + i, op=.28))
        for j in range(12):
            y = -340 + j * 150 + (55 if i % 2 else 0)
            cx = x + 55
            o.append(line([(cx, y + 18), (cx, y - 18)], w=1.6, color=WALL_LN, taper=.4, seed=300 + i * 13 + j, op=.32))
            o.append(line([(cx - 9, y + 4), (cx, y - 6), (cx + 9, y + 4)], w=1.5, color=WALL_LN, taper=.4, seed=600 + i * 13 + j, op=.32))
    del r
    # плинтус
    o.append(shape(rect_pts(-900, WALL_Y - 46, 2500, WALL_Y + 6), BASE_C, blob(rect_pts(-900, WALL_Y - 6, 2500, WALL_Y + 6), "#cdbfa5"), w=3.4, seed=70))
    gf = lib.lin_grad([(0, FLOOR_A, 1), (1, FLOOR_B, 1)], 0, WALL_Y, 0, 2200, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="{f(WALL_Y + 6)}" width="3400" height="{f(2200 - WALL_Y)}" fill="url(#{gf})"/>')
    ys = [WALL_Y + 6, 1500, 1580, 1680, 1800, 1950, 2140]
    for k, y in enumerate(ys[1:]):
        o.append(line([(-900, y), (2500, y)], w=3.0, color=FLOOR_LN, taper=0.0, wmin=1, seed=80 + k, op=.6))
    r = rs(5)
    for k, (ya, yb) in enumerate(zip(ys[:-1], ys[1:])):
        for j in range(6):
            x = r.uniform(-800, 2400)
            o.append(line([(x, ya), (x + r.uniform(-4, 4), yb)], w=2.4, color=FLOOR_LN, taper=0.0, wmin=1, seed=90 + k * 7 + j, op=.5))
    # круглый ковёр под стулом: терракота с кольцами
    cx, cy, rx, ry = MID_X, FL + 40, 420.0, 92.0
    o.append(blob(ellipse_pts(cx + 6, cy + 12, rx + 4, ry + 4, 30), "#4e2f18", .3))
    inner = ""
    for sc, col in ((.8, "#efc77a"), (.62, "#c8634a"), (.42, "#efc77a"), (.24, "#4f8a8b")):
        inner += shape(ellipse_pts(cx, cy, rx * sc, ry * sc, 26), col, ink=False)
    o.append(shape(ellipse_pts(cx, cy, rx, ry, 34), "#c8634a", inner, w=3.8, seed=120))
    return "".join(o)


# ═════════════════════════ окно ═════════════════════════
def _cloud(x, y, s, col, shade):
    o = blob(ellipse_pts(x, y, 100 * s, 22 * s, 16), shade)
    for dx, dy, rx, ry in ((-62, -4, 52, 24), (-6, -22, 64, 34), (56, -8, 56, 26), (104, 4, 34, 16)):
        o += blob(ellipse_pts(x + dx * s, y + dy * s - 8 * s, rx * s, ry * s, 14), col)
    return o


def window(t, dim=0.0):
    x0, y0, x1, y1 = WIN
    clip = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    v = []
    g = lib.lin_grad([(0, "#5d9fd8", 1), (.6, "#9ccbe9", 1), (1, "#f4e2bf", 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    v.append(f'<rect x="{f(x0 - 20)}" y="{f(y0 - 20)}" width="{f(x1 - x0 + 40)}" height="{f(y1 - y0 + 40)}" fill="url(#{g})"/>')
    for k, (bx, by, s, sp) in enumerate(((x0 + 80, y0 + 90, 1.0, 7), (x0 + 380, y0 + 170, .8, 5), (x0 + 220, y0 + 260, .6, 9))):
        xx = x0 - 160 + ((bx - x0 + 160 + sp * t) % (x1 - x0 + 320))
        v.append(_cloud(xx, by, s, "#ffffff", "#d9e8f4"))
    # дальние крыши и дерево
    roofs = [(x0 - 20, y1 - 150), (x0 + 60, y1 - 210, 1), (x0 + 150, y1 - 150, 1), (x0 + 170, y1 - 250, 1), (x0 + 300, y1 - 250, 1),
             (x0 + 310, y1 - 170, 1), (x0 + 420, y1 - 230, 1), (x0 + 560, y1 - 160, 1), (x1 + 20, y1 - 160), (x1 + 20, y1 + 20, 1), (x0 - 20, y1 + 20, 1)]
    v.append(shape(roofs, "#b9a4c4", w=2.6, seed=130, ink=False))
    for i in range(6):
        wx = x0 + 40 + i * 95
        v.append(blob(rect_pts(wx, y1 - 120, wx + 26, y1 - 86), "#f4d98c", .85))
    tx, ty = x0 + 470, y1 - 40
    v.append(shape(rect_pts(tx - 12, ty - 140, tx + 12, ty + 40), "#6b4a32", w=2.6, seed=131))
    sw = 6 * math.sin(t * 1.3)
    for k, (dx, dy, rr) in enumerate(((-60, -200, 80), (40, -230, 90), (0, -300, 80), (-90, -280, 60), (80, -160, 64))):
        v.append(shape(ellipse_pts(tx + dx + sw * (1 + k * .2), ty + dy, rr, rr * .9, 14, jitter=.06, seed=140 + k), "#6fa35e" if k % 2 else "#5b8f4f",
                       w=2.6, seed=150 + k))
    if dim > 0:
        v.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="#2a2a4a" opacity="{dim:.2f}"/>')
    o = [f'<g clip-path="url(#{clip})">{"".join(v)}</g>']
    fw = 28
    outer = [(x0 - fw, y0 - fw, 1), (x1 + fw, y0 - fw, 1), (x1 + fw, y1 + fw, 1), (x0 - fw, y1 + fw, 1)]
    o.append(f'<path d="{lib.fill_d(outer)}M{x0} {y0}H{x1}V{y1}H{x0}Z" fill="#f6efe0" fill-rule="evenodd"/>')
    o.append(f'<path d="{lib.ink_closed(outer, 4.4 * lib.INK_K[0], seed=980)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed([(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)], 3.6 * lib.INK_K[0], seed=981)}" fill="{INK}"/>')
    mx = (x0 + x1) / 2
    o.append(shape(rect_pts(mx - 8, y0, mx + 8, y1), "#f6efe0", w=3.0, seed=982))
    o.append(shape(rect_pts(x0, y0 + 230, x1, y0 + 246), "#f6efe0", w=3.0, seed=983))
    for k, (a, b) in enumerate((((x0 + 30, y0 + 200), (x0 + 130, y0 + 40)), ((mx + 40, y1 - 60), (mx + 160, y1 - 240)))):
        o.append(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="#ffffff" stroke-opacity=".22" stroke-width="{14 - k * 4}" stroke-linecap="round"/>')
    o.append(shape([(x0 - 54, y1 + 18, 1), (x1 + 54, y1 + 18, 1), (x1 + 46, y1 + 50, 1), (x0 - 46, y1 + 50, 1)], "#f6efe0",
                   blob(rect_pts(x0 - 54, y1 + 38, x1 + 54, y1 + 52), "#d6c8ac"), w=3.8, seed=985))
    # штора слева (одна, собрана)
    cx0, cx1 = x0 - 120, x0 + 10
    pts = [(cx0, y0 - 60, 1), (cx1, y0 - 60, 1), (cx1 - 20, y1 * .5 + y0 * .5), (cx1 - 40, y1 + 60, 1), (cx0, y1 + 80, 1)]
    inner = ""
    for k in range(3):
        fx = cx0 + (cx1 - cx0) * (k + .5) / 3
        inner += blob([(fx - 8, y0 - 60), (fx + 8, y0 - 60), (fx + 2, y1 + 80), (fx - 14, y1 + 80)], "#d9795e", .8)
    o.append(shape(pts, "#e8957a", inner, w=4.0, seed=171))
    o.append(shape(rect_pts(-940, y0 - 76, x1 + 70, y0 - 60, 6), "#7a5236", w=3.0, seed=172))
    return "".join(o)


# ═════════════════════════ наброски и стикеры ═════════════════════════
SKETCHES = [  # (cx, cy, w, h, rot, kind)
    (230.0, 300.0, 130.0, 150.0, -6.0, 0),
    (370.0, 320.0, 120.0, 140.0, 5.0, 1),
    (245.0, 475.0, 140.0, 110.0, 4.0, 2),
    (385.0, 490.0, 110.0, 130.0, -7.0, 3),
    (235.0, 630.0, 120.0, 110.0, -3.0, 4),
    (375.0, 650.0, 120.0, 100.0, 8.0, 5),
]
STICKERS = [(470.0, 280.0, "#f6d55c", -8.0), (310.0, 400.0, "#f29fb8", 6.0), (165.0, 560.0, "#8fd0c4", -5.0), (440.0, 410.0, "#f6d55c", 10.0),
            (170.0, 440.0, "#f6a65c", 4.0)]


def sketch(x, y, w, h, rot, kind, seed=0, pin=True):
    """Набросок на листе (центр x, y): каракули тушью и цветом, без букв."""
    sd = 2000 + seed * 31 + kind * 7
    hw, hh = w / 2, h / 2
    o = [blob(rect_pts(-hw + 5, -hh + 6, hw + 5, hh + 6), "#3b3020", .18)]
    o.append(shape([(-hw, -hh, 1), (hw, -hh, 1), (hw, hh - 10), (hw - 12, hh, 1), (-hw, hh, 1)], "#fbf5e6",
                   blob([(hw - 30, hh - 8), (hw, hh - 12), (hw - 12, hh)], "#e6dcc4"), w=2.6, seed=sd))
    s = min(w, h) / 120.0
    if kind == 0:      # лампочка с лучами
        o.append(shape(ellipse_pts(0, -12 * s, 26 * s, 28 * s, 14), "#f6d55c", w=2.4, seed=sd + 1))
        o.append(shape(rect_pts(-12 * s, 14 * s, 12 * s, 30 * s, 2), "#9aa0aa", w=2.2, seed=sd + 2))
        for i in range(7):
            a = math.radians(-180 + i * 30)
            o.append(line([(36 * s * math.cos(a), -12 * s + 36 * s * math.sin(a)), (50 * s * math.cos(a), -12 * s + 50 * s * math.sin(a))], w=2.6, seed=sd + 3 + i))
    elif kind == 1:    # спираль
        pts = [(math.cos(a) * a * 3.2 * s, math.sin(a) * a * 3.2 * s) for a in np.linspace(.3, 13, 40)]
        o.append(line(pts, w=2.8, color="#3b6fb0", taper=.3, seed=sd + 1))
    elif kind == 2:    # ракета-штрих
        o.append(shape([(-34 * s, 18 * s), (20 * s, -14 * s), (44 * s, -26 * s, 1), (30 * s, 0), (-26 * s, 30 * s)], "#e8735a", w=2.4, seed=sd + 1))
        for i in range(3):
            o.append(line([(-40 * s - i * 6 * s, 26 * s + i * 7 * s), (-60 * s - i * 6 * s, 34 * s + i * 7 * s)], w=2.4, color="#f2a23c", seed=sd + 2 + i))
    elif kind == 3:    # звезда и точки
        st = []
        for i in range(10):
            a = math.radians(-90 + i * 36)
            rr = (34 if i % 2 == 0 else 15) * s
            st.append((rr * math.cos(a), rr * math.sin(a), 1))
        o.append(shape(st, "#f6d55c", w=2.4, seed=sd + 1))
        for i in range(4):
            o.append(f'<circle cx="{f((-34 + 22 * i) * s)}" cy="{f(44 * s)}" r="{f(3.5 * s)}" fill="{INK}"/>')
    elif kind == 4:    # волна и солнце
        o.append(line([(-46 * s, 20 * s), (-24 * s, 4 * s), (0, 20 * s), (24 * s, 4 * s), (46 * s, 20 * s)], w=3.0, color="#3b8aa6", seed=sd + 1))
        o.append(shape(ellipse_pts(18 * s, -22 * s, 16 * s, 16 * s, 12), "#f2a23c", w=2.2, seed=sd + 2))
    else:              # кот-силуэт
        o.append(shape([(-30 * s, 30 * s, 1), (-26 * s, -6 * s), (-20 * s, -30 * s, 1), (-8 * s, -14 * s), (8 * s, -14 * s), (20 * s, -30 * s, 1),
                        (26 * s, -6 * s), (30 * s, 30 * s, 1)], "#3b4143", w=2.2, seed=sd + 1))
        o.append(f'<circle cx="{f(-10 * s)}" cy="{f(2 * s)}" r="{f(3.4 * s)}" fill="#9fd36a"/><circle cx="{f(10 * s)}" cy="{f(2 * s)}" r="{f(3.4 * s)}" fill="#9fd36a"/>')
        o.append(line([(30 * s, 26 * s), (46 * s, 10 * s), (44 * s, -10 * s)], w=3.0, color="#3b4143", seed=sd + 2))
        o.append(shape(ellipse_pts(44 * s, -16 * s, 5 * s, 8 * s, 8), "#f2a23c", w=1.6, seed=sd + 3))
    if pin:
        o.append(f'<circle cx="0" cy="{f(-hh + 9)}" r="7" fill="#d8483c" stroke="{INK}" stroke-width="2"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)})">{"".join(o)}</g>'


def sketches(t, fly=0.0):
    """Наброски на стене. fly 0…1: листы срываются по очереди и взлетают веером вверх-в стороны, кувыркаясь (кнопки остаются)."""
    o = []
    for i, (x, y, w, h, rot, kind) in enumerate(SKETCHES):
        u = lib.clamp((fly - i * .06) / .7)
        if u <= 0:
            sw = .8 * math.sin(t * 1.1 + i)
            o.append(sketch(x, y, w, h, rot + sw, kind, seed=i))
            continue
        o.append(f'<circle cx="{f(x)}" cy="{f(y - h / 2 + 9)}" r="7" fill="#d8483c" stroke="{INK}" stroke-width="2"/>')
        e = lib.ease_out(u, 2)
        ang = math.radians(-90 + (i - 2.5) * 26)
        dist = 380 * e
        px = x + dist * math.cos(ang) + (i - 2.5) * 30 * e
        py = y + dist * math.sin(ang) + 260 * u * u
        o.append(sketch(px, py, w * (1 + .25 * e), h * (1 + .25 * e), rot + (i - 2.5) * 70 * e, kind, seed=i, pin=False))
    return "".join(o)


def stickers(t, pop=0.0):
    o = []
    for i, (x, y, col, rot) in enumerate(STICKERS):
        sc = 1 + .25 * lib.clamp(pop - i * .1) * math.sin(math.pi * lib.clamp((pop - i * .1) / .5))
        pts = [(-26, -26, 1), (26, -26, 1), (26, 18), (16, 26, 1), (-26, 26, 1)]
        g = shape(pts, col, blob([(4, 26), (26, 18), (26, 26)], lib.mix(col, "#000000", .2)), w=2.4, seed=2600 + i)
        o.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot + 1.2 * math.sin(t * 1.4 + i))}) scale({sc:.3f})">{g}</g>')
    return "".join(o)


# ═════════════════════════ столы ═════════════════════════
def desk(x0, x1, kind="creative"):
    """Стол вид спереди: верх-полоса глубины DESK_D, толщина DESK_TH, ящики справа (творческий) / тонкая царга (чистый), ножки до FL."""
    c, sh, hi = (W_CRE, W_CRE_SH, W_CRE_HI) if kind == "creative" else (W_CLN, W_CLN_SH, W_CLN_HI)
    y = DESK_TOP
    sd = 3000 if kind == "creative" else 3100
    ins = 34.0
    back = []
    # задние ножки (видны между передними, короче — уходят за верх)
    for lx in ((x1 - ins - 60,) if kind == "creative" else (x0 + ins + 40, x1 - ins - 40)):
        back.append(shape(rect_pts(lx - 12, y - 10, lx + 12, FL - 70), sh, w=3.0, seed=sd + int(lx) % 97))
    # верх (вид слегка сверху)
    top = [(x0 + 22, y - DESK_D, 1), (x1 - 22, y - DESK_D, 1), (x1, y, 1), (x0, y, 1)]
    inner = blob([(x0 + 22, y - DESK_D), (x1 - 22, y - DESK_D), (x1 - 16, y - DESK_D + 18), (x0 + 26, y - DESK_D + 18)], sh, .35)
    if kind == "creative":
        r = rs(7)
        for i in range(5):     # царапины
            xa = r.uniform(x0 + 60, x1 - 160)
            ya = r.uniform(y - DESK_D + 30, y - 16)
            inner += line([(xa, ya), (xa + r.uniform(30, 80), ya + r.uniform(-4, 4))], w=1.8, color=sh, taper=.6, seed=sd + 10 + i, op=.7)
        for i, (cx, cy) in enumerate(((x0 + 170, y - 40), (x0 + 420, y - 78))):   # кольца от кружек
            inner += f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="34" ry="9" fill="none" stroke="#7a3f1c" stroke-opacity=".45" stroke-width="3"/>'
    else:
        inner += blob([(x0 + 120, y - DESK_D + 30), (x0 + 300, y - DESK_D + 30), (x0 + 250, y - 20), (x0 + 70, y - 20)], hi, .6)
    back.append(shape(top, hi if kind == "clean" else c, inner, w=3.8, seed=sd + 1))
    # передняя кромка
    front = [shape(rect_pts(x0, y, x1, y + DESK_TH), c, blob(rect_pts(x0, y + DESK_TH - 10, x1, y + DESK_TH), sh, .9), w=3.8, seed=sd + 2)]
    if kind == "creative":    # тумба с ящиками слева (справа под столом место для ног того, кто сидит на стуле MID_X)
        bx0, bx1 = x0 + 20, x0 + 270
        front.append(shape(rect_pts(bx0, y + DESK_TH, bx1, FL - 10), c, blob(rect_pts(bx1 - 40, y + DESK_TH, bx1, FL - 10), sh, .9), w=3.6, seed=sd + 3))
        for k in range(3):
            ya = y + DESK_TH + 16 + k * 180
            front.append(shape(rect_pts(bx0 + 16, ya, bx1 - 16, ya + 160), hi, blob(rect_pts(bx0 + 16, ya + 140, bx1 - 16, ya + 160), sh, .6), w=3.0, seed=sd + 4 + k))
            front.append(shape(rect_pts((bx0 + bx1) / 2 - 28, ya + 64, (bx0 + bx1) / 2 + 28, ya + 80, 6), "#3a3d46", w=2.4, seed=sd + 8 + k))
        legs = shape(rect_pts(x1 - ins - 16, y + DESK_TH, x1 - ins + 16, FL), c, blob(rect_pts(x1 - ins + 4, y + DESK_TH, x1 - ins + 16, FL), sh, .9), w=3.4, seed=sd + 12)
    else:                     # тонкие ножки и узкая царга
        front.append(shape(rect_pts(x0 + 30, y + DESK_TH, x1 - 30, y + DESK_TH + 26), sh, w=3.0, seed=sd + 3))
        legs = ""
        for k, lx in enumerate((x0 + ins, x1 - ins)):
            legs += shape([(lx - 14, y + DESK_TH, 1), (lx + 14, y + DESK_TH, 1), (lx + 9, FL, 1), (lx - 9, FL, 1)], c, blob(rect_pts(lx + 2, y + DESK_TH, lx + 14, FL), sh, .8),
                          w=3.2, seed=sd + 12 + k)
    shadow = blob(ellipse_pts((x0 + x1) / 2, FL + 4, (x1 - x0) / 2 + 30, 18, 20), "#4e2f18", .25)
    return dict(back=shadow + "".join(back), front="".join(front), legs=legs)


def desk_lamp(on=1.0, flick=0.0, tilt=0.0):
    """Настольная лампа на творческом столе (дно в LAMP), абажур-колокол смотрит вниз-вправо; свет — небольшой круг на столе
    с чётким краем (эллипс по форме проекции абажура), без огромного мягкого пятна."""
    lx, ly = LAMP
    o = [shape(ellipse_pts(lx, ly - 6, 50, 11, 16), "#3f6f7a", blob(ellipse_pts(lx + 12, ly - 3, 36, 6, 12), "#2c535c"), w=3.2, seed=3300)]
    j1 = (lx - 8, ly - 120)
    j2 = (lx - 70, ly - 210)
    o.append(line([(lx, ly - 10), j1], w=12, color="#4a8a96", taper=0.0, wmin=1, seed=3301))
    o.append(line([j1, j2], w=11, color="#4a8a96", taper=0.0, wmin=1, seed=3302))
    for p in (j1,):
        o.append(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="9" fill="#2c535c" stroke="{INK}" stroke-width="2.4"/>')
    hx, hy = j2
    a = math.radians(-28 + tilt)
    ca, sa = math.cos(a), math.sin(a)

    def H(x, y):
        return (hx + x * ca - y * sa, hy + x * sa + y * ca)
    head = [H(-14, -18) + (1,), H(26, -22) + (1,), H(40, 30), H(-80, 66, ) + (1,), H(-96, 34) + (1,)]
    u = lib.clamp(on)
    o.append(shape(head, lib.mix("#3f6f7a", "#4a8a96", .5), blob([H(-96, 34), H(-80, 66), H(40, 30), H(30, 20)], "#2c535c", .9), w=3.6, seed=3303))
    mouth = [H(-88, 52), H(-60, 62), H(28, 30), H(36, 28)]
    if u > .02:
        o.append(blob(mouth, lib.mix("#cdbf9a", "#fff3c8", u)))
        o.append(line(mouth, w=3.0, seed=3304))
    lamp_svg = f'<g transform="translate({f(2 * lx)} 0) scale(-1 1)">{"".join(o)}</g>'
    pool = ""
    if u > .02:
        px, py, rx, ry = LAMP_POOL
        a2 = u * (1 - .08 * flick)
        # чёткий круг света: заливка с ровным краем и тонкое тёплое кольцо, внутри чуть светлее к центру
        pool += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(rx)}" ry="{f(ry)}" fill="#ffe7a0" opacity="{.42 * a2:.3f}"/>'
        pool += f'<ellipse cx="{f(px + 6)}" cy="{f(py - 2)}" rx="{f(rx * .62)}" ry="{f(ry * .62)}" fill="#fff4cc" opacity="{.38 * a2:.3f}"/>'
        pool += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(rx)}" ry="{f(ry)}" fill="none" stroke="#f6c860" stroke-width="2.5" opacity="{.55 * a2:.3f}"/>'
        # узкий луч из абажура к кругу (чёткие края, слабая заливка)
        m0, m1 = H(-88, 52), H(36, 28)
        m0, m1 = (2 * lx - m0[0], m0[1]), (2 * lx - m1[0], m1[1])
        pool += f'<path d="M{f(m0[0])} {f(m0[1])}L{f(m1[0])} {f(m1[1])}L{f(px + rx * .92)} {f(py)}L{f(px - rx * .92)} {f(py)}Z" fill="#fff0b8" opacity="{.16 * a2:.3f}"/>'
    return dict(lamp=lamp_svg, pool=pool)


def clean_wall(t):
    """Над чистым столом: полка с тремя одинаковыми папками (без надписей), рамка с волной, круглые часы без цифр."""
    o = []
    sx0, sx1, sy = 860.0, 1360.0, 560.0
    for k in range(3):
        bx = sx0 + 60 + k * 70
        o.append(shape(rect_pts(bx, sy - 170, bx + 58, sy), ("#4f8a8b", "#4f8a8b", "#4f8a8b")[k], blob(rect_pts(bx + 40, sy - 170, bx + 58, sy), "#3a6a6b"), w=3.0, seed=3400 + k))
        o.append(f'<circle cx="{f(bx + 29)}" cy="{f(sy - 40)}" r="9" fill="#efe6d2" stroke="{INK}" stroke-width="2"/>')
    o.append(shape([(sx0 + 290, sy - 110, 1), (sx0 + 360, sy - 110, 1), (sx0 + 350, sy, 1), (sx0 + 300, sy, 1)], "#e8957a", w=2.8, seed=3405))
    for i in range(4):
        a = math.radians(-120 + i * 22)
        o.append(shape(ellipse_pts(sx0 + 325 + 40 * math.cos(a), sy - 120 + 40 * math.sin(a), 16, 26, 10, rot=math.degrees(a) + 90), "#6fa35e", w=2.2, seed=3406 + i))
    o.append(shape(rect_pts(sx0, sy, sx1, sy + 24), W_CLN, blob(rect_pts(sx0, sy + 14, sx1, sy + 24), W_CLN_SH), w=3.4, seed=3410))
    for bx in (sx0 + 40, sx1 - 40):
        o.append(shape([(bx - 10, sy + 24, 1), (bx + 10, sy + 24, 1), (bx + 10, sy + 70, 1)], W_CLN_SH, w=2.6, seed=3411 + int(bx) % 7))
    # рамка с волной
    fx0, fy0, fx1, fy1 = 1430.0, 360.0, 1620.0, 600.0
    o.append(shape(rect_pts(fx0, fy0, fx1, fy1), "#f8f2e4", blob(rect_pts(fx0, fy0, fx1, fy0 + 12), "#e3d8c0") +
                   line([(fx0 + 30, fy1 - 80), (fx0 + 70, fy1 - 120), (fx0 + 110, fy1 - 80), (fx0 + 150, fy1 - 120), (fx1 - 20, fy1 - 90)], w=4, color="#3b8aa6", seed=3420) +
                   shape(ellipse_pts(fx1 - 60, fy0 + 60, 22, 22, 12), "#f2a23c", w=2.2, seed=3421), w=6, seed=3422))
    # часы без цифр
    cx, cy, r = 1110.0, 230.0, 62.0
    o.append(shape(ellipse_pts(cx, cy, r + 8, r + 8, 26), "#4f8a8b", w=3.6, seed=3430))
    o.append(shape(ellipse_pts(cx, cy, r, r, 26), "#fbf5e6", w=3.0, seed=3431))
    for i in range(12):
        a = math.radians(i * 30)
        l0 = r * (.7 if i % 3 == 0 else .82)
        o.append(line([(cx + l0 * math.sin(a), cy - l0 * math.cos(a)), (cx + r * .92 * math.sin(a), cy - r * .92 * math.cos(a))], w=(4.4 if i % 3 == 0 else 2.6), taper=.2, seed=3432 + i))
    md = (t * 6.0) % 360
    for deg, L_, w_ in ((300.0, r * .5, 7.0), (md, r * .8, 4.6)):
        a = math.radians(deg)
        o.append(line([(cx, cy), (cx + L_ * math.sin(a), cy - L_ * math.cos(a))], w=w_, taper=.45, wmin=.3, seed=3450 + int(L_)))
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="6" fill="#c0583f" stroke="{INK}" stroke-width="2"/>')
    return "".join(o)


# ═════════════════════════ крутящийся стул ═════════════════════════
def swivel_chair(x, sy, k=1.0, spin=0.0, side=1):
    """Офисный стул: сиденье с центром в (x, sy) (таз сидящего чуть выше), газлифт, пятилучевая крестовина на колёсиках до FL.
    spin — оборотов: лучи крестовины поворачиваются, спинка (за сиденьем) сужается до ребра и появляется с другой стороны.
    side — с какой стороны спинка по умолчанию (−1 — слева, если человек смотрит вправо; +1 — справа)."""
    ph = spin * 2 * math.pi
    base_y = FL - 26 * k
    o_base = []
    o_base.append(blob(ellipse_pts(x, FL + 4, 210 * k, 18 * k, 18), "#3b2412", .28))
    for i in range(5):
        a = ph + i * 2 * math.pi / 5
        ex = x + 190 * k * math.cos(a)
        ey = base_y + 30 * k * math.sin(a)
        dep = math.sin(a)
        col = "#3a3d46" if dep > 0 else "#2a2c34"
        o_base.append(line([(x, base_y - 14 * k), (ex, ey)], w=16 * k, color=col, taper=0.0, wmin=1, seed=3500 + i))
        o_base.append(shape(ellipse_pts(ex, ey + 12 * k, 18 * k, 14 * k, 10), "#2a2c34", w=2.4, seed=3510 + i))
    o_base.append(shape(rect_pts(x - 14 * k, sy + 30 * k, x + 14 * k, base_y - 10 * k), "#9aa0aa", blob(rect_pts(x + 4 * k, sy + 30 * k, x + 14 * k, base_y - 10 * k), "#6e727c"), w=3.0, seed=3520))
    o_base.append(shape(rect_pts(x - 24 * k, base_y - 70 * k, x + 24 * k, base_y - 10 * k, 6), "#3a3d46", w=3.0, seed=3521))
    seat = shape([(x - 170 * k, sy - 6 * k), (x + 170 * k, sy - 6 * k), (x + 182 * k, sy + 18 * k, 1), (x + 160 * k, sy + 40 * k, 1), (x - 160 * k, sy + 40 * k, 1),
                  (x - 182 * k, sy + 18 * k, 1)], "#d8483c", blob(rect_pts(x - 180 * k, sy + 22 * k, x + 180 * k, sy + 42 * k), "#a8322a", .9), w=3.8, seed=3530)
    seat += shape(rect_pts(x - 40 * k, sy + 38 * k, x + 40 * k, sy + 58 * k, 4), "#2a2c34", w=2.6, seed=3531)
    # спинка за сиденьем: при spin 0 — вся видна по центру, на четверти оборота — ребром сбоку (side), на половине — снова по центру
    sn, cs = math.sin(ph) * side, abs(math.cos(ph))
    bx = x + sn * 150 * k
    bw = 150 * k * (.12 + .88 * cs)
    back = line([(x + sn * 110 * k, sy + 10 * k), (bx, sy - 150 * k)], w=14 * k, color="#3a3d46", taper=0.0, wmin=1, seed=3540)
    back += shape([(bx - bw, sy - 520 * k, 1), (bx + bw, sy - 520 * k, 1), (bx + bw * 1.06, sy - 170 * k, 1), (bx - bw * 1.06, sy - 170 * k, 1)], "#d8483c",
                  blob(rect_pts(bx + bw * .55, sy - 520 * k, bx + bw * 1.1, sy - 170 * k), "#a8322a", .9), w=3.8, seed=3541)
    return dict(base="".join(o_base), seat=seat, back=back)


# ═════════════════════════ дверь ═════════════════════════
def door_back(t, open_=1.0):
    """Коридор в проёме (тёплый светлый) и открытая створка внутрь комнаты (слева от проёма). Фигуру — после этого слоя."""
    x0, y0, x1, y1 = DOOR
    o = []
    g = lib.lin_grad([(0, "#fbe7c0", 1), (1, "#e9c995", 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    o.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="url(#{g})"/>')
    o.append(blob(rect_pts(x0, y1 - 160, x1, y1), "#d9b07a"))
    o.append(line([(x0, y1 - 160), (x1, y1 - 160)], w=3.0, seed=3600))
    # дальняя стена коридора: картина и вешалка
    o.append(shape(rect_pts(x0 + 200, y0 + 260, x0 + 320, y0 + 400), "#8fd0c4", w=3.2, seed=3601))
    o.append(line([(x0 + 70, y0 + 300), (x0 + 130, y0 + 300)], w=6, seed=3602))
    # створка: при open_ 1 — узкая полоса у левого края проёма (повёрнута к нам), при 0 — закрыта
    wv = (x1 - x0) * (1 - .82 * lib.clamp(open_))
    leaf = [(x0, y0, 1), (x0 + wv, y0 - 30 * open_, 1), (x0 + wv, y1 + 20 * open_, 1), (x0, y1, 1)]
    inner = shape(rect_pts(x0 + wv * .18, y0 + 60, x0 + wv * .82, y0 + 420), "#e7cfa6", ink=False) + shape(rect_pts(x0 + wv * .18, y0 + 520, x0 + wv * .82, y1 - 80), "#e7cfa6", ink=False)
    o.append(shape(leaf, "#f1dfbd", inner, w=3.6, seed=3603))
    o.append(f'<circle cx="{f(x0 + wv - 24)}" cy="{f((y0 + y1) / 2 + 40)}" r="10" fill="#c9a24a" stroke="{INK}" stroke-width="2.4"/>')
    return "".join(o)


def door_front(open_=1.0):
    """Наличник проёма поверх фигуры в двери."""
    x0, y0, x1, y1 = DOOR
    fw = 36
    outer = [(x0 - fw, y0 - fw, 1), (x1 + fw, y0 - fw, 1), (x1 + fw, y1, 1), (x0 - fw, y1, 1)]
    o = f'<path d="{lib.fill_d(outer)}M{x0} {y0}H{x1}V{y1}H{x0}Z" fill="#f6efe0" fill-rule="evenodd"/>'
    o += f'<path d="{lib.ink_closed(outer, 4.2 * lib.INK_K[0], seed=3610)}" fill="{INK}"/>'
    o += f'<path d="{lib.ink_closed([(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)], 3.4 * lib.INK_K[0], seed=3611)}" fill="{INK}"/>'
    o += blob(rect_pts(x1, y0, x1 + fw, y1), "#ddd0b6", .9)
    return o


def door(t, open_=1.0, figure=""):
    return door_back(t, open_) + figure + door_front(open_)


# ═════════════════════════ бардак творческого стола ═════════════════════════
def creative_clutter(t, k=1.0, jump=0.0):
    """Бардак творческого стола из common/props.py: гора бумажек слева, клубок проводов с зарядкой, две кружки с кольцом кофе,
    стикер, карандаш. Место справа (x 200…380 у лампы) свободно — там рисует Дима. jump — подскок предметов (хлопок ладонью), px."""
    import props as PR
    yb, yf = DESK_TOP - DESK_D + 30, DESK_TOP - 8
    j = -abs(jump)
    o = [PR.coffee_ring(60, yf - 34, 1.0, seed=1), PR.paper_pile(-330, yf - 10 + j * .6, 1.05, seed=3),
         PR.mug(-170, yb + 44 + j, .95, rot=-4 * (jump != 0), col="blue", coffee=True, seed=1),
         PR.cable_tangle(-90, yf - 26 + j * .4, .8, seed=2, t=t), PR.charger(10, yf - 36 + j * .5, .8, rot=-20),
         PR.sticky(-20, yb + 50 + j * .3, .8, rot=8, col="pink", seed=2, mark="star"),
         PR.mug(110, yf + j * 1.2, 1.0, rot=3 * (jump != 0), col="red", coffee=True, steam=.7, t=t, seed=2),
         PR.pencil(-250, yf - 6 + j, .8, rot=-6)]
    return "".join(o)


def clean_top(t, checks=0, u=0.0, k=1.0):
    """Чистый стол: закрытый ноутбук, одна ровная стопка, лист с чекбоксами (без букв) у левого края — под руку сидящему на MID_X."""
    import props as PR
    yb, yf = DESK_TOP - DESK_D + 30, DESK_TOP - 8
    o = [PR.laptop_closed(1180, yb + 50, 1.15), PR.paper_stack(1500, yb + 60, .9, n=5, seed=4, mess=0.0, sy=.4),
         PR.marker(1020, yf - 20, .7, rot=-8, col="#4F8A8B", cap=True),
         PR.checklist(890, yf - 52, 1.0 * k, rot=-3, checks=checks, u=u, seed=1, sy=.62)]
    return "".join(o)


# ═════════════════════════ весь фон ═════════════════════════
def room_bg(t, lamp_on=1.0, flick=0.0, fly=0.0, pop=0.0, win_dim=0.0, door_open=1.0, with_door=True, items=False):
    """Фон комнаты целиком без людей и предметов на столах. Порядок в клипе: bg → [предметы на столах, фигуры] → front-слои столов."""
    cr = desk(*CREATIVE, kind="creative")
    cl = desk(*CLEAN, kind="clean")
    lamp = desk_lamp(lamp_on, flick)
    o = ['<rect x="-1200" y="2100" width="4000" height="900" fill="#c38c5a"/>', wall_floor(), window(t, win_dim), sketches(t, fly), stickers(t, pop),
         clean_wall(t)]
    if with_door:
        o.append(door(t, door_open))
    o += [cr["back"], cr["front"], cr["legs"], cl["back"], cl["front"], cl["legs"]]
    if items:
        o += [lamp["pool"], creative_clutter(t), clean_top(t)]
    return dict(bg="".join(o), lamp=lamp["lamp"], pool=lamp["pool"], creative=cr, clean=cl)
