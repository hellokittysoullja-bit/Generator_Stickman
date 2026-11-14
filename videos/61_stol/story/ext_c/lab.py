"""Рилс 61 «стол», группа C: две комнаты эксперимента в Миннесоте (Vohs 2013) — ОДНА комната, один стол, одна камера,
разное наполнение. tidy — белые стены, ровная стопка, растение, полка с книгами по росту; messy — та же комната, но коробки,
разбросанные листы, кружки, кривые стопки книг, провод, стикеры и наброски на стене. За окном — зима: снег, ёлки, снежинки.
Без флагов, вывесок, букв и цифр (листы — только штрихи).

Мир 1080×1920 (камера — снаружи, lib.cam). Порядок слоёв в клипе:
    back(t, kind)            стена, окно, полка, картина/наброски, пол, задние ножки стола, всё, что за человеком
    [кресло-спинка, человек]
    desk_top(kind)           столешница (поверх таза человека) — предметы на столе кладутся после неё
    desk_front()             передняя кромка и ножки стола (поверх всего на столе ниже кромки нет)
    clutter_front(t)         коробки на полу у переднего края (только messy)
Константы: TOP_BACK (задний край столешницы), TOP_FRONT (передний край), DESK_X0, DESK_X1, FLOOR_Y, WIN.
"""
import math

import numpy as np

import lib
import props as PR
from lib import INK, blob, ellipse_pts, f, line, mix, rect_pts, rrect, shape

WALL_Y = 1400.0          # низ стены (пол за столом)
FLOOR_Y = 1680.0         # пол у переднего края кадра (ножки стола)
TOP_BACK, TOP_FRONT = 1078.0, 1150.0
DESK_X0, DESK_X1 = 96.0, 1000.0
APRON = 54.0
WIN = (70.0, 300.0, 460.0, 860.0)

WALL_T, WALL_B = "#e4ebe8", "#cfdad8"       # прохладная белая стена
WOOD, WOOD_SH, WOOD_HI, WOOD_DK = "#c99a66", "#a87a49", "#e2b985", "#7f5734"
FLOOR_C, FLOOR_LN = "#9aa6ae", "#6f7c86"
CARD, CARD_SH, CARD_HI, TAPE = "#c9965c", "#a2733f", "#ddb07a", "#e8d9a6"
SX = 740.0            # стопка на аккуратном столе
PAGE, PAGE_SH, PAGE_LN = "#fbf6ea", "#e3dccb", "#a49c8a"


def rs(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


def _tf(inner, x, y, k=1.0, rot=0.0):
    return f'<g transform="translate({f(x)} {f(y)}) rotate({rot:.3f}) scale({k:.4f})">{inner}</g>'


# ═════════════════════════ окно: зима ═════════════════════════
def fir(x, y, h, seed):
    """Ёлка: три яруса с белыми шапками снега, ствол. (x, y) — низ ствола."""
    o = [shape(rect_pts(x - h * .05, y - h * .12, x + h * .05, y), "#5b3d28", w=2.2, seed=seed)]
    for k in range(3):
        yb = y - h * (.1 + .27 * k)
        wb = h * (.42 - .1 * k)
        yt = yb - h * .42
        tier = [(x - wb, yb, 1), (x - wb * .55, yb - h * .1), (x, yt, 1), (x + wb * .55, yb - h * .1), (x + wb, yb, 1)]
        sn = blob([(x - wb * .45, yb - h * .2), (x, yt + 2), (x + wb * .45, yb - h * .2), (x + wb * .2, yb - h * .16), (x - wb * .15, yb - h * .19)], "#f6fbff")
        sn += blob([(x - wb, yb), (x - wb * .4, yb - h * .05), (x + wb * .2, yb - h * .02), (x + wb, yb), (x + wb * .3, yb + 4)], "#eaf3fb")
        o.append(shape(tier, "#2f6b4e" if k % 2 == 0 else "#2a5f45", sn, w=2.6, seed=seed + 1 + k))
    return "".join(o)


def window(t):
    x0, y0, x1, y1 = WIN
    clip = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o = [f'<g clip-path="url(#{clip})">']
    g = lib.lin_grad([(0, "#a9c6e0", 1), (.7, "#d9e7f2", 1), (1, "#eef4f8", 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>')
    o.append(blob(ellipse_pts(x0 + 300, y0 + 110, 46, 46, 20), "#f8f4e6", .9))
    # дальний лес и холм в снегу
    far = [(x0 - 20, 690)] + [(x0 + i * 30, 670 - 18 * math.sin(i * 1.3) - 10 * (i % 2)) for i in range(15)] + [(x1 + 20, 700, 1), (x1 + 20, 900, 1), (x0 - 20, 900, 1)]
    o.append(blob(far, "#7e9db5"))
    o.append(blob([(x0 - 20, 735), (x0 + 120, 712), (x0 + 260, 726), (x1 + 20, 706), (x1 + 20, 900), (x0 - 20, 900)], "#f2f7fb"))
    o.append(line([(x0 - 20, 736), (x0 + 120, 713), (x0 + 260, 727), (x1 + 20, 707)], 3, "#b9cad8", seed=901))
    for x, yb, h, sd in ((120, 740, 150, 910), (210, 760, 210, 920), (340, 745, 170, 930), (420, 770, 230, 940), (285, 800, 120, 950)):
        o.append(fir(x, yb, h, sd))
    o.append(blob([(x0 - 20, 800), (x0 + 200, 780), (x1 + 20, 795), (x1 + 20, 900), (x0 - 20, 900)], "#f8fbfd"))
    # снегопад: падает и качается (живое с первого кадра)
    r = rs(77)
    for i in range(46):
        sx, sy, sp, sz = r.uniform(x0, x1), r.uniform(0, 600), r.uniform(60, 120), r.uniform(3, 7)
        yy = y0 + (sy + sp * t) % (y1 - y0 + 20) - 10
        xx = sx + 10 * math.sin(t * 1.6 + i)
        o.append(f'<circle cx="{f(xx)}" cy="{f(yy)}" r="{f(sz)}" fill="#ffffff"/>')
    o.append("</g>")
    fw = 26
    outer = [(x0 - fw, y0 - fw, 1), (x1 + fw, y0 - fw, 1), (x1 + fw, y1 + fw, 1), (x0 - fw, y1 + fw, 1)]
    hole = f"M{x0} {y0}H{x1}V{y1}H{x0}Z"
    o.append(f'<path d="{lib.fill_d(outer)}{hole}" fill="#f7f7f2" fill-rule="evenodd"/>')
    o.append(f'<path d="{lib.ink_closed(outer, 4.4 * lib.INK_K[0], seed=980)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed([(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)], 3.6 * lib.INK_K[0], seed=981)}" fill="{INK}"/>')
    mx = (x0 + x1) / 2
    my = y0 + (y1 - y0) * .42
    for pts, sd in (([(mx - 7, y0), (mx + 7, y0), (mx + 7, y1), (mx - 7, y1)], 982), ([(x0, my - 7), (x1, my - 7), (x1, my + 7), (x0, my + 7)], 983)):
        o.append(shape([p + (1,) for p in pts], "#f7f7f2", w=3.0, seed=sd))
    for k, (a, b) in enumerate([((x0 + 30, y0 + 170), (x0 + 130, y0 + 40)), ((mx + 40, y1 - 60), (mx + 150, y1 - 230))]):
        o.append(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="#ffffff" stroke-opacity=".35" stroke-width="{14 - k * 4}" stroke-linecap="round"/>')
    # иней в нижних углах стёкол
    for cx in (x0, mx + 7):
        o.append(blob([(cx, y1), (cx, y1 - 40), (cx + 30, y1 - 22), (cx + 70, y1 - 8), (cx + 110, y1)], "#ffffff", .8))
    sill = [(x0 - 52, y1 + 16, 1), (x1 + 52, y1 + 16, 1), (x1 + 44, y1 + 46, 1), (x0 - 44, y1 + 46, 1)]
    o.append(shape(sill, "#f7f7f2", blob(rect_pts(x0 - 52, y1 + 34, x1 + 52, y1 + 46), "#d6dcd8"), w=4.0, seed=985))
    return "".join(o)


# ═════════════════════════ мелкие предметы комнаты ═════════════════════════
def page(cx, cy, w, h, rot=0.0, seed=0, lines=4, col=None, persp=.48):
    """Лист на столе — общий props.paper (штрихи, без букв), сплющен persp."""
    return PR.paper(cx, cy, 1.0, rot, w, h, seed, "lines" if lines else "blank", persp)


def stack(cx, cy, n=6, w=180, rot=0.0, spread=0.0, seed=0, misalign=0.0):
    """Ровная стопка (props.paper_stack): misalign 0…1 — листы съехали (до щелчка), 0 — под линейку."""
    return PR.paper_stack(cx, cy, w / 130, n, seed, misalign, .45)


def pencil(x0, y0, x1, y1, seed=0, col=None):
    a = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    return PR.pencil((x0 + x1) / 2, (y0 + y1) / 2, L / 160, a)


def mug(x, y, k=1.0, col="blue", rot=0.0, seed=0, steam=0.0, t=0.0, tipped=False):
    return PR.mug(x, y, k, rot, col, True, steam, t, 1, seed)


def ring_stain(x, y, r=34, seed=0):
    return PR.coffee_ring(x, y, r / 35, 0, seed)


def book(x, y, w, h, col, rot=0.0, seed=0, lie=False):
    """Книга корешком к зрителю: стоит (lie=False, (x, y) — низ середины) или лежит плашмя (w — длина, h — толщина)."""
    inner = blob(rect_pts(-w / 2, -h, -w / 2 + w * .18, 0), mix(col, "#000000", .2), .8)
    inner += line([(-w / 2 + w * .3, -h * .22), (w / 2 - w * .3, -h * .22)], 2.6, mix(col, "#ffffff", .55), taper=.1, seed=seed + 1)
    if lie:
        inner = blob(rect_pts(-w / 2, -h * .4, w / 2, 0), mix(col, "#000000", .18), .8)
        inner += blob(rect_pts(w / 2 - 10, -h + 3, w / 2 - 3, -3), PAGE)
    return _tf(shape(rect_pts(-w / 2, -h, w / 2, 0, 3), col, inner, w=2.8, seed=seed), x, y, 1, rot)


def box(x, y, w, h, rot=0.0, seed=0, open_=False, d=0.42):
    """Картонная коробка 3/4: перед, бок справа, крышка; скотч. (x, y) — низ середины переда."""
    hw = w / 2
    dd = w * d * .5
    front = [(-hw, -h, 1), (hw, -h, 1), (hw, 0, 1), (-hw, 0, 1)]
    side = [(hw, -h, 1), (hw + dd, -h - dd * .6, 1), (hw + dd, -dd * .6, 1), (hw, 0, 1)]
    top = [(-hw, -h, 1), (-hw + dd, -h - dd * .6, 1), (hw + dd, -h - dd * .6, 1), (hw, -h, 1)]
    o = shape(side, CARD_SH, w=3.0, seed=seed + 1)
    o += shape(front, CARD, blob(rect_pts(-hw, -h * .25, hw, 0), CARD_SH, .5) + blob(rect_pts(-14, -h, 14, -h * .55), TAPE, .9), w=3.2, seed=seed)
    if open_:
        o += shape([(-hw, -h, 1), (-hw - dd * .2, -h - dd * 1.1, 1), (-hw + dd * .7, -h - dd * 1.3, 1), (-hw + dd, -h - dd * .6, 1)], CARD_HI, w=2.6, seed=seed + 4)
        o += shape(top, "#6e4a28", w=2.6, seed=seed + 2)
        o += shape([(hw, -h, 1), (hw + dd * 1.3, -h - dd * .2, 1), (hw + dd * 1.8, -h - dd * .9, 1), (hw + dd, -h - dd * .6, 1)], CARD_HI, w=2.6, seed=seed + 5)
    else:
        o += shape(top, CARD_HI, blob([(-6 + dd * .5, -h - dd * .3 - 12), (6 + dd * .5, -h - dd * .3 - 12), (14, -h), (-14, -h)], TAPE, .9), w=3.0, seed=seed + 2)
    return _tf(o, x, y, 1, rot)


def plant(x, y, k, t, seed=31):
    r = rs(seed)
    o = []
    for i in range(11):
        a = math.radians(-90 + (i - 5) * 15) + .05 * math.sin(t * 1.1 + i)
        L_ = (120 + 50 * r.uniform()) * k
        tip = (x + L_ * math.cos(a), y - 70 * k + L_ * math.sin(a))
        mid = (x + L_ * .5 * math.cos(a) - 6 * (i - 5) * .3, y - 70 * k + L_ * .55 * math.sin(a))
        o.append(shape(lib.band([(x, y - 66 * k), mid, tip], 20 * k, 3, step=6), "#5fa05b" if i % 2 else "#3f8a50", w=2.6, seed=180 + i))
    o.append(shape([(x - 46 * k, y - 76 * k, 1), (x + 46 * k, y - 76 * k, 1), (x + 34 * k, y, 1), (x - 34 * k, y, 1)], "#f2f2ee",
                   blob([(x + 14 * k, y - 76 * k), (x + 46 * k, y - 76 * k), (x + 34 * k, y), (x + 12 * k, y)], "#d2d6d3", .9), w=3.4, seed=190))
    return "".join(o)


def sticky(x, y, col, rot, seed):
    return PR.sticky(x, y, .7, rot, col, seed, "lines")


def sketch(x, y, w, h, rot, seed, kind=0):
    return PR.wall_sketch(x + w / 2, y + h / 2, w / 150, rot, seed, ("spiral", "graph", "house", "rocket")[kind % 4])


def cable(pts_base, seed, t=0.0):
    pts = [(x + 2 * math.sin(t * 2 + i), y) for i, (x, y) in enumerate(pts_base)]
    return PR.cable(pts, seed=seed)


# ═════════════════════════ стена, полка, пол ═════════════════════════
def wall_floor(kind):
    o = []
    g = lib.lin_grad([(0, WALL_T, 1), (1, WALL_B, 1)], 0, 0, 0, WALL_Y, units="userSpaceOnUse")
    o.append(f'<rect x="-500" y="-400" width="2100" height="{f(WALL_Y + 400)}" fill="url(#{g})"/>')
    # дневной свет из окна: светлая трапеция на стене справа от окна (чёткая, не мягкий овал)
    o.append(blob([(470, 330), (640, 380), (640, 1000), (470, 880)], "#ffffff", .22))
    # панель внизу стены и плинтус
    o.append(shape(rect_pts(-500, WALL_Y - 260, 1600, WALL_Y - 250), "#b8c6c4", w=2.4, seed=60))
    o.append(blob(rect_pts(-500, WALL_Y - 250, 1600, WALL_Y), "#c3cfcd"))
    o.append(shape(rect_pts(-500, WALL_Y - 26, 1600, WALL_Y + 4), "#f2f2ee", w=3.2, seed=61))
    gf = lib.lin_grad([(0, "#8a96a0", 1), (1, "#aab5bc", 1)], 0, WALL_Y, 0, 2200, units="userSpaceOnUse")
    o.append(f'<rect x="-500" y="{f(WALL_Y + 4)}" width="2100" height="1000" fill="url(#{gf})"/>')
    for k, y in enumerate((1470, 1560, 1680, 1830, 2010)):
        o.append(line([(-500, y), (1600, y)], 2.6, FLOOR_LN, taper=0, wmin=1, seed=70 + k, op=.45))
    # потолочный край и плафон
    o.append(shape(rect_pts(-500, -400, 1600, 120), "#f4f6f4", blob(rect_pts(-500, 100, 1600, 120), "#dfe5e3"), w=3.4, seed=62))
    return "".join(o)


def shelf(kind, t, x0=610.0, x1=1000.0, y=640.0):
    o = []
    o.append(shape(rect_pts(x0, y, x1, y + 22), WOOD, blob(rect_pts(x0, y + 14, x1, y + 22), WOOD_SH), w=3.2, seed=300))
    for xx in (x0 + 40, x1 - 40):
        o.append(shape([(xx - 8, y + 22, 1), (xx + 8, y + 22, 1), (xx + 8, y + 70, 1), (xx - 30, y + 22, 1)], "#9aa3a8", w=2.4, seed=301 + int(xx) % 7))
    if kind == "tidy":
        cols = ("#3f6fb0", "#3f6fb0", "#5c9a78", "#5c9a78", "#c2493d", "#c2493d", "#d9a94a")
        x = x0 + 30
        for i, c in enumerate(cols):
            o.append(book(x + 17, y, 34, 150 - (i // 2) * 12, c, 0, seed=310 + i))
            x += 36
        o.append(plant(x1 - 70, y, .55, t, seed=33))
    else:
        o.append(book(x0 + 50, y, 34, 140, "#3f6fb0", 0, 330))
        o.append(book(x0 + 84, y - 2, 34, 120, "#d9a94a", 14, 331))
        o.append(book(x0 + 138, y - 4, 34, 150, "#c2493d", -24, 332))
        o.append(book(x0 + 220, y, 150, 30, "#5c9a78", -2, 333, lie=True))
        o.append(book(x0 + 228, y - 30, 130, 28, "#8b4a55", 4, 334, lie=True))
        o.append(box(x1 - 70, y, 110, 90, 3, 335, open_=True))
        o.append(page(x0 + 230, y - 74, 70, 50, 20, 336, lines=2, persp=.6))
    return "".join(o)


def frame_pic(x, y, w, h, rot=0.0):
    """Картина в рамке: горы и солнце (без букв)."""
    inner = blob([(0, h), (w * .3, h * .45), (w * .5, h * .7), (w * .72, h * .3), (w, h)], "#6f9bb8")
    inner += blob([(w * .2, h * .58), (w * .3, h * .45), (w * .4, h * .58)], "#ffffff")
    inner += f'<circle cx="{f(w * .78)}" cy="{f(h * .25)}" r="{f(h * .1)}" fill="#f2c84a"/>'
    o = shape(rect_pts(-12, -12, w + 12, h + 12), "#3a3236", w=3.0, seed=340)
    o += shape(rect_pts(0, 0, w, h), "#e9f1f4", inner, w=2.6, seed=341)
    return _tf(o, x, y, 1, rot)


def back(t, kind):
    """Всё за человеком: стена, окно, полка, картина / наброски, пол, задние ножки стола, кресло-спинка не входит."""
    o = [wall_floor(kind), window(t)]
    if kind == "tidy":
        o.append(frame_pic(640, 300, 260, 190, 0))
        o.append(shelf(kind, t))
    else:
        o.append(frame_pic(640, 300, 260, 190, -4))
        for (x, y, w, h, r, s, kd) in ((560, 230, 100, 130, -8, 400, 0), (930, 250, 110, 140, 7, 401, 1), (900, 440, 96, 120, -5, 402, 2),
                                       (560, 430, 90, 110, 6, 403, 1)):
            o.append(sketch(x, y, w, h, r, s, kd))
        for i, (x, y, c, r) in enumerate(((700, 520, "yellow", -6), (760, 545, "pink", 8), (520, 600, "green", 4), (980, 590, "yellow", -10),
                                          (840, 530, "blue", 5))):
            o.append(sticky(x, y, c, r, 420 + i))
        o.append(shelf(kind, t))
        # коробки у стены на полу за столом
        o.append(box(980, WALL_Y + 30, 170, 150, 0, 440))
        o.append(box(990, WALL_Y - 120, 130, 110, -4, 441, open_=True))
        o.append(box(150, WALL_Y + 40, 150, 120, 3, 442, open_=True))
        o.append(cable([(700, WALL_Y - 26), (690, WALL_Y + 20), (740, WALL_Y + 50), (800, WALL_Y + 30), (760, WALL_Y + 10), (720, WALL_Y + 60)], 443, t))
    # задние ножки стола
    for xx in (DESK_X0 + 50, DESK_X1 - 50):
        o.append(shape(rect_pts(xx - 14, TOP_BACK + 20, xx + 14, WALL_Y + 60), WOOD_DK, w=3.0, seed=450 + int(xx) % 5))
    return "".join(o)


def chair_back(x, y, rot=0.0, k=1.0):
    """Спинка офисного кресла за человеком: (x, y) — середина сиденья."""
    o = shape(rrect(-120, -330, 120, -60, 40), "#3f4d6a", blob(rrect(40, -320, 118, -66, 30), "#2f3a52", .9), w=3.6, seed=470)
    o += shape(rect_pts(-16, -60, 16, 10), "#2a2f3a", w=2.6, seed=471)
    o += shape(rrect(-140, -10, 140, 30, 14), "#3f4d6a", w=3.2, seed=472)
    return _tf(o, x, y, k, rot)


def desk_top(kind):
    """Столешница вид чуть сверху: задний край TOP_BACK, передний TOP_FRONT, передняя кромка APRON."""
    x0, x1 = DESK_X0, DESK_X1
    top = [(x0 + 30, TOP_BACK, 1), (x1 - 30, TOP_BACK, 1), (x1, TOP_FRONT, 1), (x0, TOP_FRONT, 1)]
    inner = ""
    r = rs(5)
    for i in range(6):
        yy = TOP_BACK + (TOP_FRONT - TOP_BACK) * (i + .5) / 6
        xa = x0 + r.uniform(60, 300)
        inner += line([(xa, yy), (xa + r.uniform(140, 380), yy + r.uniform(-1, 1))], 2.0, WOOD_SH, taper=.4, seed=480 + i, op=.6)
    inner += blob([(x0 + 30, TOP_BACK), (x1 - 30, TOP_BACK), (x1 - 26, TOP_BACK + 8), (x0 + 30, TOP_BACK + 8)], WOOD_HI, .8)
    return shape(top, WOOD, inner, w=3.6, seed=481)


def desk_front():
    x0, x1 = DESK_X0, DESK_X1
    o = []
    for xx in (x0 + 26, x1 - 26):
        o.append(shape(rect_pts(xx - 20, TOP_FRONT + APRON - 4, xx + 20, FLOOR_Y), WOOD_SH,
                       blob(rect_pts(xx + 6, TOP_FRONT + APRON, xx + 20, FLOOR_Y), WOOD_DK, .7), w=3.4, seed=490 + int(xx) % 7))
    ap = rect_pts(x0, TOP_FRONT, x1, TOP_FRONT + APRON)
    o.append(shape(ap, WOOD_SH, blob(rect_pts(x0, TOP_FRONT + APRON - 12, x1, TOP_FRONT + APRON), WOOD_DK, .7) +
                   blob(rect_pts(x0, TOP_FRONT, x1, TOP_FRONT + 6), WOOD_HI, .7), w=3.8, seed=495))
    # ящик с ручкой
    o.append(shape(rect_pts(x1 - 300, TOP_FRONT + 10, x1 - 70, TOP_FRONT + APRON - 10, 4), WOOD, w=2.6, seed=496))
    o.append(shape(rrect(x1 - 210, TOP_FRONT + 22, x1 - 160, TOP_FRONT + 32, 5), "#8a8f96", w=2.0, seed=497))
    return "".join(o)


def floor_shadow():
    return blob([(DESK_X0 - 20, FLOOR_Y + 6), (DESK_X1 + 20, FLOOR_Y + 6), (DESK_X1 - 60, FLOOR_Y - 30), (DESK_X0 + 60, FLOOR_Y - 30)], "#5b6670", .35)


def under_desk():
    """Тень под столом (тёмная ниша между ножками)."""
    return blob([(DESK_X0 + 40, TOP_FRONT + APRON, 1), (DESK_X1 - 40, TOP_FRONT + APRON, 1), (DESK_X1 - 50, WALL_Y + 70, 1), (DESK_X0 + 50, WALL_Y + 70, 1)],
                "#7d8a92", .45)


def clutter_front(t):
    """Только messy: коробка и скомканный лист на полу перед столом, провод свисает со столешницы."""
    o = [cable([(820, TOP_FRONT + 10), (830, TOP_FRONT + 120), (800, TOP_FRONT + 260), (850, TOP_FRONT + 400), (900, FLOOR_Y - 10)], 500, t)]
    o.append(box(260, FLOOR_Y + 40, 220, 170, -3, 501, open_=True))
    for i, (x, y, r) in enumerate(((560, FLOOR_Y + 10, 34), (650, FLOOR_Y - 40, 26), (470, FLOOR_Y - 60, 24))):
        o.append(shape(ellipse_pts(x, y, r, r * .78, 11, jitter=.2, seed=3 + i), PAGE,
                       line([(x - r * .6, y - 4), (x, y + 6), (x + r * .5, y - 8)], 2.4, PAGE_LN, seed=503 + i), w=2.6, seed=502 + i * 3))
    o.append(page(760, FLOOR_Y - 20, 200, 150, -18, 506, lines=4, persp=.4))
    o.append(book(640, FLOOR_Y + 30, 190, 34, "#3f6fb0", 4, 507, lie=True))
    o.append(book(650, FLOOR_Y - 4, 170, 30, "#d9a94a", -5, 508, lie=True))
    return "".join(o)


def desk_items_tidy(t, misalign=0.0, shine=0.0):
    """Аккуратный стол: растение слева, ровная стопка, карандаш параллельно, закрытый блокнот справа."""
    o = [plant(190, TOP_BACK + 40, .9, t)]
    o.append(stack(SX, TOP_BACK + 50, n=5, w=140, seed=520, misalign=misalign))
    o.append(pencil(640 + 30 * misalign, TOP_FRONT - 16, 860 - 20 * misalign, TOP_FRONT - 16 - 34 * misalign, seed=530))
    o.append(book(925, TOP_BACK + 46, 120, 24, "#3f6fb0", 0, 540, lie=True))
    if shine > 0:
        for i in range(5):
            a = math.radians(-160 + i * 35)
            r0, r1 = 120 + 30 * shine, 150 + 60 * shine
            cx, cy = SX, TOP_BACK - 40
            o.append(line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a) * .7), (cx + r1 * math.cos(a), cy + r1 * math.sin(a) * .7)], 5.0, "#f2b53a",
                          taper=.5, seed=550 + i, op=1 - shine ** 2))
    return "".join(o)


def desk_items_messy(t):
    """Стол-бардак: коробка, кривые стопки книг, разбросанные листы, две кружки с кольцом кофе, провод, стикеры."""
    o = [ring_stain(620, TOP_FRONT - 22, 30, 600)]
    o.append(box(220, TOP_BACK + 50, 200, 150, -2, 601, open_=True))
    o.append(page(470, TOP_FRONT - 34, 150, 110, 18, 602, lines=4))
    o.append(page(360, TOP_FRONT - 20, 150, 110, -24, 603, lines=3))
    o.append(page(760, TOP_FRONT - 30, 150, 110, -8, 604, lines=4))
    o.append(book(900, TOP_BACK + 40, 170, 30, "#c2493d", -3, 605, lie=True))
    o.append(book(905, TOP_BACK + 12, 150, 28, "#5c9a78", 5, 606, lie=True))
    o.append(book(895, TOP_BACK - 14, 160, 26, "#d9a94a", -6, 607, lie=True))
    o.append(mug(380, TOP_BACK + 46, .95, "red", 0, 608, steam=1.0, t=t))
    o.append(cable([(980, TOP_BACK + 30), (900, TOP_BACK + 60), (820, TOP_FRONT - 20), (760, TOP_FRONT - 4), (700, TOP_FRONT - 30), (820, TOP_FRONT + 10)], 609, t))
    o.append(sticky(560, TOP_BACK + 18, "yellow", -12, 610))
    o.append(page(560, TOP_FRONT - 10, 140, 100, 34, 611, lines=3))
    o.append(page(250, TOP_FRONT - 12, 140, 100, 12, 612, lines=4))
    o.append(mug(980, TOP_FRONT - 8, .85, "blue", 0, 613))
    o.append(ring_stain(300, TOP_BACK + 30, 26, 614))
    o.append(pencil(700, TOP_BACK + 34, 600, TOP_BACK + 50, seed=615))
    return "".join(o)
