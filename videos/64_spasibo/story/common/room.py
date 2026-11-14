"""Комната Димы рилса 64 «спасибо» (пишет группа C; берут все). Основа — common/room.py рилсов 63, 61, 62.

Подключение:  sys.path.insert(0, COMMON); import room as R   (COMMON = videos/64_spasibo/story/common; lib рядом).
Мир кадра 1080×1920, камера снаружи (lib.cam(cx, cy, s)); мир шире кадра: x −1600…3400, y −600…2400.
Букв и цифр нигде нет: корешки книг пустые, картинка на стене — горы штрихом. Свет — плоскими пятнами с чёткой формой
(небольшой круг лампы под абажуром, днём — полоса солнца формы окна), без огромных мягких овалов.
Все функции возвращают строку SVG в мировых координатах (градиенты — динамические defs, вызывать после lib.dyn_begin()).

РЕЖИМЫ: mode="evening" (s01, s03, s04: лампа горит, окно тёмно-синее с луной и огнями домов, стена приглушённая)
        mode="day"     (s13, s14, s16–s18: лампа выключена, окно голубое, полоса солнца формы окна на стене и полу)

СТОЛ (s01, s03, s04, s13, s18) — Дима сидит СЛЕВА от стола в профиль-3/4 вправо, колени под столешницей, стол справа от него
(вид спереди, верх слегка сверху), под столешницей — ящик (DRAWER), справа на столе — лампа.
    desk_scene(t, mode, drawer=0.0, lamp_swing=0.0, chair_tilt=0.0) -> dict:
        bg     — стена, окно, полка, пол, ковёр (класть первым)
        chair_back / chair_front — спинка стула (ДО Димы) и сиденье с ножками (после ног Димы, до тела — как в 61: legs → seat → body)
        desk   — столешница, царга, ящик (выдвинут на drawer 0…1), ножки (класть ПОСЛЕ туловища Димы, ДО его ближней руки)
        pool   — небольшой круг света лампы на столешнице (после desk, до предметов на столе); днём пусто
        lamp   — лампа (после предметов)
        inside — (x0, y0, x1, y1) видимая внутренность выдвинутого ящика (класть открытку внутрь: clip lib.clip_rect)
        drawer_front — передняя панель ящика отдельно (если предмет в ящике надо положить ПОД неё: inside → предмет → drawer_front;
                       в desk панель уже есть, повторно класть только поверх предмета)
    FL=1560 пол (низ ножек), WALL_Y=1440 низ стены, DESK_TOP=960 передняя кромка столешницы, DESK_D=120 глубина верха
    DESK_X=(560, 1340) столешница: предметы на столе — дном на y ∈ [DESK_TOP − DESK_D + 10, DESK_TOP − 6] (ниже — ближе)
    DRAWER=(760, 1090, 996, 1086)  ящик в царге под столешницей (x0, x1, y0, y1), ручка по центру
    LAMP=(1100, DESK_TOP − 60)  дно лампы; круг света LAMP_POOL=(1000, DESK_TOP − 52, 120, 28) — небольшой, чёткий край
    SIT=(330, seat_y(1.0))  таз сидящего Димы (bs=1.0); seat_y(bs) — для другого масштаба; ступни на FL на x≈SIT+300
    CAT_DESK — где кот сидит/приземляется на столе: (980, DESK_TOP − 40) (лапы на этой линии), CAT_FLOOR=(1420, FL − 6) — кот на полу
    камеры (ОДИН ракурс s01 и s18 — петля): CAM_DESK_CLOSE=(650, 780, 1.35)  стол крупно: лицо, руки, открытка, край стола
                                          CAM_DESK_MID=(720, 920, 1.12)   стол средний план: Дима до колен, ящик, лампа
                                          CAM_DESK_LOW=(800, 1090, 0.96)  ракурс ниже: Дима на стуле, стол, пол с котом
        («ракурс ниже» — сцена рисуется той же, камера опускается и смотрит шире; perspective_low=True у desk_scene
         приподнимает видимый верх столешницы чуть меньше, чтобы ощущалось ниже)

ОКНО В ПОЛНЫЙ РОСТ (s14) — то же окно, что слева в комнате: высокое, от WIN_TALL[1] до подоконника WIN_TALL[3].
    window_scene(t, mode="day", sway=1.0) -> dict(bg, front)  bg — стена, окно с деревьями (качаются, sway), пол; front — штора справа
    WIN_TALL=(−700, 150, −120, 1150) окно (x0, y0, x1, y1)   STAND=(−240, 1560) где стоит Дима (ступни на FL), лицом к окну/зрителю
    CAM_WIN=(−330, 900, 0.95)  Дима в полный рост у окна ≈ 60 % кадра

ДИВАН (s16, s17) — справа в той же комнате: диван анфас, подлокотник справа, чистая стена над правой половиной.
    sofa_scene(t, mode="day") -> dict(bg, sofa, front)  bg — стена, торшер-столбик слева, пол; sofa — диван (ДО Димы: спинка и
        сиденье); front — передний валик правого подлокотника (после Димы, если его рука/кот перекрывается); кот на подлокотнике —
        лапами на ARM_TOP.
    SOFA=(2250, 1560, 1.2) центр низа дивана; SOFA_SEAT=1190 верх подушек сиденья; sofa_hip(bs) — таз сидящего Димы;
    SOFA_DIMA=(2120, sofa_hip(1.0)) таз Димы; ARM_TOP=(2676, 1008) верх правого подлокотника (центр)
    CLEAN_WALL=(2420, 260, 3000, 680) — ЧИСТАЯ стена над подлокотником для рукописного «кот»: ни предметов, ни теней, ни солнца
    CAM_SOFA=(2330, 1000, 1.0)  общий план дивана (Дима ≈ 50 % кадра)
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
from lib import INK, blob, ellipse_pts, f, line, rect_pts, shape  # noqa: E402

# ─────────────── общие размеры ───────────────
FL = 1560.0
WALL_Y = 1440.0
DESK_TOP = 960.0
DESK_D = 120.0
DESK_TH = 36.0
DESK_X = (560.0, 1340.0)
DRAWER = (760.0, 1090.0, DESK_TOP + DESK_TH, DESK_TOP + DESK_TH + 90.0)
LAMP = (1100.0, DESK_TOP - 60.0)
LAMP_POOL = (1000.0, DESK_TOP - 52.0, 120.0, 28.0)
WIN_DESK = (700.0, 150.0, 1180.0, 640.0)
CAT_DESK = (980.0, DESK_TOP - 40.0)
CAT_FLOOR = (1420.0, FL - 6.0)
CAM_DESK_CLOSE = (650.0, 780.0, 1.35)
CAM_DESK_MID = (720.0, 920.0, 1.12)
CAM_DESK_LOW = (800.0, 1090.0, 0.96)
# окно в полный рост
WIN_TALL = (-700.0, 150.0, -120.0, 1150.0)
STAND = (-240.0, FL)
CAM_WIN = (-330.0, 900.0, 0.95)
# диван
SOFA = (2250.0, FL, 1.2)
SOFA_SEAT = 1190.0
ARM_TOP = (2676.0, 1008.0)
CLEAN_WALL = (2420.0, 260.0, 3000.0, 680.0)
CAM_SOFA = (2330.0, 1000.0, 1.0)


def seat_y(bs=1.0):
    """Таз сидящего на стуле Димы масштаба bs: ступни на FL (голень 300, бедро горизонтально) — как в 61."""
    return FL - 392.0 * bs


def sofa_hip(bs=1.0):
    """Таз Димы, сидящего на подушке дивана (сиденье ниже стула: колени выше таза)."""
    return SOFA_SEAT - 10.0 * bs


SIT = (330.0, seat_y(1.0))
SOFA_DIMA = (2120.0, sofa_hip(1.0))

WOOD, WOOD_SH, WOOD_HI = "#b27c4c", "#8a5b32", "#ce9a68"
DESKW, DESKW_SH, DESKW_HI = "#c48a52", "#94633a", "#dcaa72"

MODES = {
    "evening": dict(wall="#7e7aa0", wall_hi="#958fb2", wall_sh="#625e84", wall_ln="#6d6990", base="#a7a2c0", base_sh="#837ea3",
                    floor="#7a5236", floor_b="#5e3e28", floor_ln="#43291a", rug=("#a8503f", "#d8a45a", "#3f6f7a"), shelf=WOOD_SH,
                    sky=("#141a3c", "#26306a", "#4a4f8c"), shadow="#2a2440", shade_k=(.86, .86, .9)),
    "day": dict(wall="#e6dcc0", wall_hi="#f1e9d2", wall_sh="#d2c6a6", wall_ln="#d8cdb0", base="#f4eedf", base_sh="#d6ccb4",
                floor="#c8915c", floor_b="#b07a48", floor_ln="#8a5b34", rug=("#c8634a", "#efc77a", "#4f8a8b"), shelf=WOOD,
                sky=("#6fb2ec", "#acd8f5", "#e6f4fb"), shadow="#6e4a2c", shade_k=(1, 1, 1)),
}


def rs(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


def _M(mode):
    return MODES["evening" if mode == "evening" else "day"]


# ═════════════════════════ стена и пол ═════════════════════════
def wall_floor(mode="evening"):
    """Стена (крашеная, лёгкие вертикальные полосы обоев), плинтус, пол-доски. Тянется на весь мир."""
    M = _M(mode)
    o = []
    g = lib.lin_grad([(0, M["wall_sh"], 1), (.35, M["wall"], 1), (1, M["wall_hi"], 1)], 0, -600, 0, WALL_Y, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="-600" width="5000" height="{f(WALL_Y + 600)}" fill="url(#{g})"/>')
    for i in range(-16, 34):
        x = i * 140.0
        o.append(line([(x, -600), (x + 1.5, WALL_Y - 40)], w=1.8, color=M["wall_ln"], taper=0.0, wmin=1, seed=40 + i, op=.55))
    o.append(shape(rect_pts(-1600, WALL_Y - 46, 3400, WALL_Y + 6), M["base"], blob(rect_pts(-1600, WALL_Y - 8, 3400, WALL_Y + 6), M["base_sh"]),
                   w=3.4, seed=70))
    gf = lib.lin_grad([(0, M["floor"], 1), (1, M["floor_b"], 1)], 0, WALL_Y, 0, 2400, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="{f(WALL_Y + 6)}" width="5000" height="{f(2400 - WALL_Y)}" fill="url(#{gf})"/>')
    ys = [WALL_Y + 6, 1500, 1580, 1680, 1810, 1970, 2170, 2400]
    for k, y in enumerate(ys[1:-1]):
        o.append(line([(-1600, y), (3400, y)], w=3.0, color=M["floor_ln"], taper=0.0, wmin=1, seed=80 + k, op=.6))
    r = rs(5)
    for k, (ya, yb) in enumerate(zip(ys[:-1], ys[1:])):
        for j in range(9):
            x = r.uniform(-1500, 3300)
            o.append(line([(x, ya), (x + r.uniform(-4, 4), yb)], w=2.4, color=M["floor_ln"], taper=0.0, wmin=1, seed=90 + k * 11 + j, op=.5))
    return "".join(o)


def rug(cx, cy, rx, ry, mode="evening", seed=0):
    """Круглый полосатый коврик на полу (вид чуть сверху)."""
    M = _M(mode)
    c0, c1, c2 = M["rug"]
    inner = ""
    for sc, col in ((.8, c1), (.6, c0), (.4, c1), (.22, c2)):
        inner += shape(ellipse_pts(cx, cy, rx * sc, ry * sc, 26), col, ink=False)
    return blob(ellipse_pts(cx + 6, cy + 12, rx + 4, ry + 4, 30), M["shadow"], .25) + shape(ellipse_pts(cx, cy, rx, ry, 34), c0, inner, w=3.8, seed=120 + seed)


# ═════════════════════════ окно ═════════════════════════
def _tree(x, y, h, sway, t, seed, col="#5f9a52", sh="#477a3c", trunk="#6e4a2c"):
    """Дерево за окном: ствол и пушистая крона, крона качается (sway)."""
    a = .04 * sway * math.sin(t * 1.9 + seed) + .015 * sway * math.sin(t * 4.3 + seed * 2)
    tx, ty = x + math.sin(a) * h * .9, y - math.cos(a) * h * .9
    o = line([(x, y), ((x + tx) / 2, (y + ty) / 2 + 6), (tx, ty)], 16 * h / 300, trunk, taper=.5, wmin=.4, seed=seed)
    pts = []
    for i in range(14):
        th = 2 * math.pi * i / 14
        rr = h * (.36 + .05 * math.sin(i * 2.7 + seed))
        pts.append((tx + math.cos(th) * rr * 1.05, ty - h * .12 + math.sin(th) * rr * .9))
    inner = blob([(tx + p[0] * .0 + (p[0] - tx) * .55 + h * .1, p[1] + h * .1) for p in pts], sh, .9)
    return o + shape(pts, col, inner, w=3.0, seed=seed + 1)


def window(x0, y0, x1, y1, mode, t=0.0, seed=0, sway=0.6, curtain="#c96f4a", sill=True):
    """Окно с рамой, крестовиной, подоконником и шторами. Вечер — тёмно-синее небо, луна, звёзды-штрихи, силуэты домов с огнями
    окон (тёплые квадраты без всяких знаков); день — голубое небо, облака плывут от t, деревья качаются (sway)."""
    M = _M(mode)
    sd = 7300 + seed
    fr = 18
    ix0, iy0, ix1, iy1 = x0 + fr, y0 + fr, x1 - fr, y1 - fr
    w, h = ix1 - ix0, iy1 - iy0
    sky = M["sky"]
    g = lib.lin_grad([(0, sky[0], 1), (.6, sky[1], 1), (1, sky[2], 1)], 0, 0, 0, 1)
    inner = f'<path d="M{f(ix0 - 5)} {f(iy0 - 5)}H{f(ix1 + 5)}V{f(iy1 + 5)}H{f(ix0 - 5)}Z" fill="url(#{g})"/>'
    r = rs(sd)
    if mode == "evening":
        for i in range(9):
            sx = ix0 + 24 + r.uniform(0, w - 48)
            sy = iy0 + 20 + r.uniform(0, h * .42)
            tw = .55 + .45 * math.sin(t * 2.4 + i * 1.7)
            L = 7 + (i % 3) * 2
            inner += line([(sx - L, sy), (sx + L, sy)], 2.6, "#f6efc8", taper=.5, wmin=.3, seed=sd + 10 + i, op=tw)
            inner += line([(sx, sy - L), (sx, sy + L)], 2.6, "#f6efc8", taper=.5, wmin=.3, seed=sd + 30 + i, op=tw)
        mx, my, mr = ix1 - w * .28, iy0 + h * .2, max(24.0, w * .1)
        inner += shape(ellipse_pts(mx, my, mr, mr, 22), "#fbf1c8", blob(ellipse_pts(mx + mr * .5, my - mr * .1, mr * .85, mr * .95, 18), sky[1]),
                       w=2.6, seed=sd + 70)
        # дома с тёплыми окнами
        hb = iy1 - h * .3
        for j in range(5):
            bx0 = ix0 - 10 + j * w / 4.2
            bx1 = bx0 + w / 4.6
            by = hb + (j % 3) * h * .06
            inner += blob(rect_pts(bx0, by, bx1, iy1 + 8), "#1b2146")
            for a in range(2):
                for b in range(3):
                    if (a + b + j) % 3 == 0:
                        continue
                    wx = bx0 + 14 + a * (bx1 - bx0 - 28) * .55
                    wy = by + 16 + b * 34
                    if wy + 18 < iy1:
                        inner += blob(rect_pts(wx, wy, wx + 16, wy + 18), "#f2c66a")
    else:
        inner += shape(ellipse_pts(ix0 + w * .26, iy0 + h * .2, w * .09, w * .09, 20), "#fff0a8", "", w=2.4, seed=sd + 41)
        for j in range(3):
            cx = ix0 + ((j * 173 + t * 14 + sd) % (w + 160)) - 80
            cy = iy0 + h * (.15 + .14 * j)
            cw = w * (.3 + .06 * (j % 2))
            pts = [(cx - cw / 2, cy + 12)] + [(cx - cw / 2 + cw * i / 5, cy - 14 - 14 * math.sin(i * 1.9 + j)) for i in range(6)] + [(cx + cw / 2, cy + 12)]
            inner += blob(pts, "#ffffff")
        hh = h * .55
        inner += _tree(ix0 + w * .2, iy1 + 30, hh, sway, t, sd + 80)
        inner += _tree(ix0 + w * .78, iy1 + 30, hh * .82, sway, t, sd + 90, col="#6faa5c", sh="#548a44")
        inner += blob([(ix0 - 5, iy1 + 5, 1), (ix0 - 5, iy1 - h * .06), (ix1 + 5, iy1 - h * .09), (ix1 + 5, iy1 + 5, 1)], "#7fae5e")
    frame = "#efe7d6" if mode != "evening" else "#c9c2d8"
    out = [shape(rect_pts(x0, y0, x1, y1), frame, "", w=4.4, seed=sd)]
    out.append(shape(rect_pts(ix0, iy0, ix1, iy1), sky[1], inner, w=3.4, seed=sd + 1))
    xm, ym = (x0 + x1) / 2, iy0 + h * .42
    out.append(blob(rect_pts(xm - 7, iy0, xm + 7, iy1), frame) + line([(xm - 7, iy0), (xm - 7, iy1)], 2.6, INK, seed=sd + 2)
               + line([(xm + 7, iy0), (xm + 7, iy1)], 2.6, INK, seed=sd + 3))
    out.append(blob(rect_pts(ix0, ym - 7, ix1, ym + 7), frame) + line([(ix0, ym - 7), (ix1, ym - 7)], 2.6, INK, seed=sd + 4)
               + line([(ix0, ym + 7), (ix1, ym + 7)], 2.6, INK, seed=sd + 5))
    if sill:
        out.append(shape(lib.rrect(x0 - 30, y1, x1 + 30, y1 + 24, 5), lib.mul(frame, (.95, .95, .95)),
                         blob(rect_pts(x0 - 34, y1 + 13, x1 + 34, y1 + 28), lib.mul(frame, (.8, .8, .82))), w=3.4, seed=sd + 6))
    if curtain:
        cur = curtain if mode != "evening" else lib.mul(curtain, (.72, .66, .8))
        sw = 3.0 * math.sin(t * .8 + seed)
        for sgn, cx in ((-1, x0 - 4), (1, x1 + 4)):
            pts = [(cx - sgn * 6, y0 - 26, 1), (cx + sgn * 78, y0 - 18), (cx + sgn * (66 + sw), y0 * .4 + y1 * .6), (cx + sgn * 86, y1 + 40, 1),
                   (cx - sgn * 8, y1 + 40, 1)]
            fold = line([(cx + sgn * 30, y0), (cx + sgn * (40 + sw * .5), y1 + 30)], 5, lib.mul(cur, (.78, .78, .78)), taper=.4, wmin=.3,
                        seed=sd + 8 + int(sgn + 1))
            out.append(shape(pts, cur, fold, w=3.4, seed=sd + 9 + int(sgn + 1)))
        out.append(shape(lib.rrect(x0 - 50, y0 - 40, x1 + 50, y0 - 24, 6), WOOD_SH, "", w=3.0, seed=sd + 14))
    return "".join(out)


def _sun_quad(A, U, V, col, col2, inset=.06):
    """Полоса солнца формы окна: четыре стекла (A — угол, U вдоль ширины, V вдоль высоты), крестовина — тень, чёткие края."""
    A, U, V = np.array(A, float), np.array(U, float), np.array(V, float)
    o = []
    for (u0, u1) in ((0.0, .47), (.53, 1.0)):
        for (v0, v1) in ((0.0, .4), (.47, 1.0)):
            pts = [tuple(A + U * u0 + V * v0) + (1,), tuple(A + U * u1 + V * v0) + (1,), tuple(A + U * u1 + V * v1) + (1,), tuple(A + U * u0 + V * v1) + (1,)]
            o.append(blob(pts, col))
            q = [tuple(A + U * (u0 + .03) + V * (v0 + inset)) + (1,), tuple(A + U * (u1 - .03) + V * (v0 + inset)) + (1,),
                 tuple(A + U * (u1 - .03) + V * (v0 + inset + .1)) + (1,), tuple(A + U * (u0 + .03) + V * (v0 + inset + .1)) + (1,)]
            o.append(blob(q, col2))
    return "".join(o)


def sun_patches(mode):
    """Днём: полоса солнца формы высокого окна на стене справа от него (за Димой у стола) и пятно на полу. Вечером пусто."""
    if mode == "evening":
        return ""
    o = _sun_quad((-40, 260), (330, 40), (60, 760), "#f6e7bf", "#fbf0d2", inset=.05)
    o += _sun_quad((-560, 1475), (520, -10), (300, 80), "#d9a66e", "#e2b37c", inset=.08)
    return o


# ═════════════════════════ мебель у стола ═════════════════════════
def shelf(x0, x1, y, mode="evening", seed=0, books=True, plant=True, t=0.0):
    """Полка на стене: доска на кронштейнах, книги с ПУСТЫМИ корешками (цветные полосы), горшок с растением."""
    M = _M(mode)
    k = M["shade_k"]
    o = []
    if books:
        r = rs(300 + seed)
        x = x0 + 30
        cols = ["#c8553d", "#4f8a8b", "#e0b04a", "#5a6fb0", "#8a5b9a", "#6aa36a", "#d98a4a"]
        for i in range(7):
            bw = r.uniform(26, 42)
            bh = r.uniform(110, 150)
            lean = -10.0 if i == 6 else 0.0
            c = lib.mul(cols[i % len(cols)], k)
            pts = [(x, y, 1), (x + bw, y, 1), (x + bw + lean * .0, y - bh, 1), (x + lean, y - bh, 1)]
            if lean:
                pts = lib.T([(x, y, 1), (x + bw, y, 1), (x + bw, y - bh, 1), (x, y - bh, 1)], 0, 0, 1, 14, x + bw, y)
            o.append(shape(pts, c, blob(rect_pts(x + bw - 8, y - bh - 4, x + bw + 4, y + 4), lib.mul(c, (.78, .78, .78))) +
                           line([(x + 5, y - bh * .78), (x + bw - 5, y - bh * .78)], 2.6, lib.mul(c, (.7, .7, .7)), taper=0, wmin=1, seed=330 + i),
                           w=3.0, seed=310 + i + seed))
            x += bw + 3
    if plant:
        px = x1 - 80
        ph = 0.04 * math.sin(t * 1.3)
        leaves = ""
        for i, a in enumerate((-60, -30, -5, 20, 45, 70)):
            aa = math.radians(a - 90 + 6 * math.sin(t * 1.3 + i))
            L = 95 + 18 * (i % 2)
            tip = (px + math.cos(aa) * L, y - 72 + math.sin(aa) * L)
            mid = (px + math.cos(aa) * L * .5 + math.cos(aa + 1.5) * 16, y - 72 + math.sin(aa) * L * .5 + math.sin(aa + 1.5) * 16)
            mid2 = (px + math.cos(aa) * L * .5 - math.cos(aa + 1.5) * 16, y - 72 + math.sin(aa) * L * .5 - math.sin(aa + 1.5) * 16)
            leaves += shape([(px, y - 72, 1), mid, tip + (1,), mid2], lib.mul("#6aa35a", k), line([(px, y - 72), tip], 2.0, lib.mul("#4a7f3c", k),
                                                                                               seed=360 + i), w=2.8, seed=350 + i)
        del ph
        o.append(leaves)
        o.append(shape([(px - 52, y - 84, 1), (px + 52, y - 84, 1), (px + 40, y, 1), (px - 40, y, 1)], lib.mul("#d0704a", k),
                       blob(rect_pts(px - 60, y - 84, px + 60, y - 66), lib.mul("#a8553a", k)), w=3.2, seed=340 + seed))
    o.append(shape(rect_pts(x0, y, x1, y + 20), M["shelf"], blob(rect_pts(x0, y + 12, x1, y + 20), WOOD_SH), w=3.4, seed=320 + seed))
    for bx in (x0 + 50, x1 - 50):
        o.append(shape([(bx - 8, y + 20, 1), (bx + 8, y + 20, 1), (bx + 8, y + 64, 1), (bx - 8, y + 30, 1)], "#555a66", "", w=2.4, seed=325 + int(bx) % 7))
    return "".join(o)


def wall_picture(cx, cy, w, h, mode="evening", seed=0):
    """Картинка в рамке без букв: горы и солнце штрихом."""
    k = _M(mode)["shade_k"]
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    inner = blob(rect_pts(x0, y0, x1, y1), lib.mul("#f4ead2", k))
    inner += blob([(x0, y1, 1), (x0 + w * .3, y0 + h * .35, 1), (x0 + w * .5, y0 + h * .6, 1), (x0 + w * .72, y0 + h * .3, 1), (x1, y1, 1)],
                  lib.mul("#7fa4b8", k))
    inner += blob(ellipse_pts(x0 + w * .78, y0 + h * .22, w * .08, w * .08, 14), lib.mul("#f2b65a", k))
    return shape(rect_pts(x0 - 14, y0 - 14, x1 + 14, y1 + 14), lib.mul(WOOD_SH, k), "", w=3.2, seed=400 + seed) + shape(rect_pts(x0, y0, x1, y1), "#f4ead2", inner,
                                                                                                                     w=2.6, seed=401 + seed)


def chair(x, sy, k=1.0, tilt=0.0, mode="evening"):
    """Деревянный стул сбоку (Дима сидит лицом вправо): спинка слева за тазом. (x, sy) — таз сидящего; сиденье чуть ниже таза.
    tilt — откинулся (градусы, + назад): стул встаёт на задние ножки, поворот вокруг задней ножки на полу.
    dict(back — спинка (ДО Димы), seat — сиденье и ножки (после ног Димы, до тела))."""
    kk = _M(mode)["shade_k"]
    c, sh, hi = lib.mul(WOOD, kk), lib.mul(WOOD_SH, kk), lib.mul(WOOD_HI, kk)
    seat = sy + 24 * k
    bx0 = x - 120 * k
    pivot = (bx0 + 10 * k, FL)

    def P(pts):
        return lib.T(pts, 0, 0, 1, -tilt, pivot[0], pivot[1])
    back = []
    back.append(shape(P([(bx0 - 6 * k, seat, 1), (bx0 + 18 * k, seat, 1), (bx0 + 6 * k, seat - 400 * k, 1), (bx0 - 22 * k, seat - 396 * k, 1)]), c,
                      blob(P(rect_pts(bx0 - 30 * k, seat - 400 * k, bx0 - 10 * k, seat)), sh, .8), w=3.4, seed=500))
    back.append(shape(P(lib.rrect(bx0 - 30 * k, seat - 390 * k, bx0 + 30 * k, seat - 250 * k, 10 * k)), hi, blob(P(rect_pts(bx0 + 10 * k, seat - 390 * k, bx0 + 30 * k,
                                                                                                                             seat - 250 * k)), c, .8),
                      w=3.2, seed=501))
    front = []
    front.append(shape(P(lib.rrect(bx0 - 20 * k, seat - 6 * k, x + 170 * k, seat + 26 * k, 8 * k)), c, blob(P(rect_pts(bx0 - 20 * k, seat + 16 * k, x + 170 * k,
                                                                                                                       seat + 26 * k)), sh), w=3.4, seed=502))
    for i, lx in enumerate((bx0, x + 150 * k)):
        front.append(shape(P([(lx - 10 * k, seat + 26 * k, 1), (lx + 10 * k, seat + 26 * k, 1), (lx + 8 * k, FL, 1), (lx - 8 * k, FL, 1)]), c,
                           blob(P(rect_pts(lx + 2 * k, seat + 26 * k, lx + 10 * k, FL)), sh), w=3.0, seed=503 + i))
    front.append(line(P([(bx0 + 4 * k, seat + 170 * k), (x + 146 * k, seat + 170 * k)]), 7 * k, sh, taper=0, wmin=1, seed=506))
    return dict(back="".join(back), seat="".join(front))


def desk_lamp(on=1.0, swing=0.0, mode="evening"):
    """Настольная лампа на столе: основание, изогнутая стойка, абажур-колокол смотрит вниз-влево (к открытке).
    swing — угол качания абажура (градусы; толчок от хлопка ящика — сцена задаёт затухающее колебание).
    Свет — небольшой круг на столешнице с ЧЁТКИМ краем, сдвигается вместе с абажуром; узкий конус слабой заливкой."""
    lx, ly = LAMP
    kk = _M(mode)["shade_k"]
    col, col_sh, col_hi = lib.mul("#3f6f7a", kk), lib.mul("#2c535c", kk), lib.mul("#5a95a2", kk)
    o = [shape(ellipse_pts(lx, ly - 6, 56, 13, 16), col, blob(ellipse_pts(lx + 14, ly - 2, 40, 7, 12), col_sh), w=3.2, seed=3300)]
    j1 = (lx + 6, ly - 150)
    a = math.radians(swing)
    arm = (-90.0, -60.0)
    j2 = (j1[0] + arm[0] * math.cos(a * .5) - arm[1] * math.sin(a * .5), j1[1] + arm[0] * math.sin(a * .5) + arm[1] * math.cos(a * .5))
    o.append(line([(lx, ly - 10), (lx + 10, ly - 80), j1], w=13, color=col_hi, taper=0.0, wmin=1, seed=3301))
    o.append(line([j1, j2], w=12, color=col_hi, taper=0.0, wmin=1, seed=3302))
    o.append(f'<circle cx="{f(j1[0])}" cy="{f(j1[1])}" r="10" fill="{col_sh}" stroke="{INK}" stroke-width="2.6"/>')
    hx, hy = j2
    ang = math.radians(24 + swing)
    ca, sa = math.cos(ang), math.sin(ang)

    def H(x, y):
        return (hx + x * ca - y * sa, hy + x * sa + y * ca)
    head = [H(-20, -16) + (1,), H(20, -16) + (1,), H(70, 70) + (1,), H(-70, 70) + (1,)]
    o.append(shape(head, col, blob([H(20, -16), H(70, 70), H(30, 70), H(0, -16)], col_sh, .85), w=3.6, seed=3303))
    u = lib.clamp(on)
    mouth = ellipse_pts(*H(0, 70), 70, 14, 20)
    mouth = [((p[0] - H(0, 70)[0]) * ca - (p[1] - H(0, 70)[1]) * sa * 1 + H(0, 70)[0], (p[0] - H(0, 70)[0]) * sa + (p[1] - H(0, 70)[1]) * ca + H(0, 70)[1])
             for p in mouth]
    o.append(shape(mouth, lib.mix("#c9bd9c", "#fff3c8", u), "", w=2.8, seed=3304))
    pool = ""
    if u > .02:
        px, py, rx, ry = LAMP_POOL
        m = H(0, 70)
        px = px + (m[0] - (LAMP[0] - 64)) * .9
        # чёткий круг света: ровная заливка, светлее к центру ступенькой, тонкое тёплое кольцо
        pool += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(rx)}" ry="{f(ry)}" fill="#ffe7a0" opacity="{.5 * u:.3f}"/>'
        pool += f'<ellipse cx="{f(px + 6)}" cy="{f(py - 2)}" rx="{f(rx * .6)}" ry="{f(ry * .6)}" fill="#fff4cc" opacity="{.45 * u:.3f}"/>'
        pool += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(rx)}" ry="{f(ry)}" fill="none" stroke="#f6c860" stroke-width="2.5" opacity="{.6 * u:.3f}"/>'
        m0, m1 = H(-66, 72), H(66, 72)
        pool += (f'<path d="M{f(m0[0])} {f(m0[1])}L{f(m1[0])} {f(m1[1])}L{f(px + rx * .95)} {f(py)}L{f(px - rx * .95)} {f(py)}Z" '
                 f'fill="#fff0b8" opacity="{.14 * u:.3f}"/>')
    return dict(lamp="".join(o), pool=pool)


def desk(mode="evening", drawer=0.0, seed=0):
    """Стол вид спереди: верх-полоса глубины DESK_D, торец, царга с ящиком (drawer 0…1 — выдвинут к зрителю), ножки до FL.
    Возвращает dict(top, front, legs, inside, drawer_front): inside — прямоугольник видимой внутренности ящика."""
    kk = _M(mode)["shade_k"]
    c, sh, hi = lib.mul(DESKW, kk), lib.mul(DESKW_SH, kk), lib.mul(DESKW_HI, kk)
    x0, x1 = DESK_X
    y = DESK_TOP
    sd = 3000 + seed
    ins = 36.0
    top = [(x0 + 24, y - DESK_D, 1), (x1 - 24, y - DESK_D, 1), (x1, y, 1), (x0, y, 1)]
    inner = blob([(x0 + 24, y - DESK_D), (x1 - 24, y - DESK_D), (x1 - 18, y - DESK_D + 18), (x0 + 28, y - DESK_D + 18)], sh, .35)
    r = rs(7 + seed)
    for i in range(4):
        xa = r.uniform(x0 + 80, x1 - 200)
        ya = r.uniform(y - DESK_D + 30, y - 16)
        inner += line([(xa, ya), (xa + r.uniform(40, 90), ya + r.uniform(-3, 3))], w=1.8, color=sh, taper=.6, seed=sd + 10 + i, op=.6)
    top_svg = shape(top, c, inner, w=3.8, seed=sd + 1)
    # задние ножки (видны между передними)
    back_legs = ""
    for i, lx in enumerate((x0 + ins + 60, x1 - ins - 60)):
        back_legs += shape(rect_pts(lx - 11, y + DESK_TH, lx + 11, FL - 60), sh, w=3.0, seed=sd + 20 + i)
    front = [shape(rect_pts(x0, y, x1, y + DESK_TH), c, blob(rect_pts(x0, y + DESK_TH - 10, x1, y + DESK_TH), sh, .9), w=3.8, seed=sd + 2)]
    # царга (узкая доска под столешницей) по всей ширине, кроме ящика
    dx0, dx1, dy0, dy1 = DRAWER
    front.append(shape(rect_pts(x0 + 20, y + DESK_TH, x1 - 20, dy1 + 6), lib.mul(c, (.94, .94, .94)), blob(rect_pts(x0 + 20, dy1 - 6, x1 - 20, dy1 + 6), sh, .8),
                       w=3.2, seed=sd + 3))
    # ящик: проём (тёмный), выдвинутый ящик — боковины и дно внутри видны, передняя панель ниже и чуть крупнее
    u = lib.clamp(drawer)
    front.append(blob(rect_pts(dx0, dy0, dx1, dy1), lib.mul(sh, (.55, .55, .55))))
    pull = 70.0 * u
    s = 1 + .06 * u
    cxm = (dx0 + dx1) / 2
    fx0, fx1 = cxm - (dx1 - dx0) / 2 * s, cxm + (dx1 - dx0) / 2 * s
    fy0, fy1 = dy0 + pull * .55, dy1 + pull * .55 + (dy1 - dy0) * (s - 1)
    inside = None
    if u > .01:
        # внутренность: дно светлого дерева, боковины в перспективе, задняя стенка
        bx = [(dx0 + 8, dy0 + 6, 1), (dx1 - 8, dy0 + 6, 1), (fx1 - 10, fy0 + 4, 1), (fx0 + 10, fy0 + 4, 1)]
        front.append(shape(bx, lib.mul(DESKW_HI, (kk[0] * .9, kk[1] * .88, kk[2] * .85)),
                           blob([(dx0 + 8, dy0 + 6), (dx1 - 8, dy0 + 6), (dx1 - 8, dy0 + 6 + 10 * u), (dx0 + 8, dy0 + 6 + 10 * u)], sh, .7), w=2.8, seed=sd + 4))
        for sgn, (a, b) in ((-1, ((dx0 + 8, dy0 + 6), (fx0 + 10, fy0 + 4))), (1, ((dx1 - 8, dy0 + 6), (fx1 - 10, fy0 + 4)))):
            side = [(a[0], a[1], 1), (b[0], b[1], 1), (b[0], b[1] + 18, 1), (a[0], a[1] + 12, 1)]
            front.append(shape(side, hi, "", w=2.4, seed=sd + 6 + sgn))
        inside = (dx0 + 14, dy0 + 6, dx1 - 14, fy0 + 4)
    df = [shape(rect_pts(fx0, fy0, fx1, fy1), hi, blob(rect_pts(fx0, fy1 - 10, fx1, fy1), sh, .7), w=3.2, seed=sd + 8)]
    hw = 34 * s
    df.append(shape(lib.rrect(cxm - hw, (fy0 + fy1) / 2 - 8, cxm + hw, (fy0 + fy1) / 2 + 8, 7), "#3a3d46", blob(rect_pts(cxm - hw, (fy0 + fy1) / 2 + 2, cxm + hw,
                                                                                                                    (fy0 + fy1) / 2 + 8), "#22252c"),
                    w=2.4, seed=sd + 9))
    drawer_front = "".join(df)
    legs = ""
    for i, lx in enumerate((x0 + ins, x1 - ins)):
        legs += shape([(lx - 15, y + DESK_TH, 1), (lx + 15, y + DESK_TH, 1), (lx + 11, FL, 1), (lx - 11, FL, 1)], c, blob(rect_pts(lx + 3, y + DESK_TH, lx + 15, FL), sh, .8),
                      w=3.2, seed=sd + 12 + i)
    shadow = blob(ellipse_pts((x0 + x1) / 2, FL + 4, (x1 - x0) / 2 + 30, 16, 20), _M(mode)["shadow"], .3)
    return dict(top=top_svg, front="".join(front) + drawer_front, legs=shadow + back_legs + legs, inside=inside, drawer_front=drawer_front)


def desk_scene(t, mode="evening", drawer=0.0, lamp_swing=0.0, chair_tilt=0.0, lamp_on=None, sit=None, bs=1.0):
    """Угол комнаты со столом. Порядок слоёв в клипе:
    bg → chair_back → [Дима: legs] → chair_seat → [Дима: pelvis, arm_f, body] → desk → pool → [предметы на столе, ближняя рука] → lamp.
    sit — таз Димы (по умолчанию SIT), стул ставится под него."""
    o = [wall_floor(mode)]
    o.append(sun_patches(mode))
    o.append(window(*WIN_TALL, mode, t, seed=1, sway=.7))
    o.append(window(*WIN_DESK, mode, t, seed=2, sway=.5, curtain=""))
    o.append(wall_picture(470, 430, 150, 120, mode, seed=1))
    o.append(shelf(1260, 1600, 560, mode, seed=1, t=t))
    o.append(rug(520, FL + 70, 430, 90, mode))
    sx, sy = sit or SIT
    ch = chair(sx, sy, bs, chair_tilt, mode)
    on = (1.0 if mode == "evening" else 0.0) if lamp_on is None else lamp_on
    lp = desk_lamp(on, lamp_swing, mode)
    d = desk(mode, drawer)
    return dict(bg="".join(o), chair_back=ch["back"], chair_seat=ch["seat"], desk=d["legs"] + d["top"] + d["front"], pool=lp["pool"], lamp=lp["lamp"],
                inside=d["inside"], drawer_front=d["drawer_front"])


# ═════════════════════════ окно в полный рост ═════════════════════════
def window_scene(t, mode="day", sway=1.0):
    """Стена с высоким окном: Дима стоит у окна в полный рост (STAND). bg — стена, окно с деревьями, полоса солнца, пол; front — пусто
    (штора у окна уже в bg; Диму ставить после bg)."""
    o = [wall_floor(mode), sun_patches(mode), window(*WIN_TALL, mode, t, seed=1, sway=sway)]
    o.append(rug(-300, FL + 80, 380, 80, mode, seed=3))
    return dict(bg="".join(o), front="")


# ═════════════════════════ диван ═════════════════════════
def sofa(x, y, k=1.0, mode="day", seed=0, col="#4a6fa5"):
    """Диван анфас: спинка, две подушки сиденья, подлокотники, ножки. (x, y) — низ ножек, центр.
    dict(back — спинка, подушки, левый подлокотник; arm_r — правый подлокотник (класть после Димы, если надо перекрыть))."""
    kk = _M(mode)["shade_k"]
    c = lib.mul(col, kk)
    sh = lib.mul(c, (.8, .8, .82))
    hi = lib.mix(c, "#ffffff", .18)
    W = 820 * k
    x0, x1 = x - W / 2, x + W / 2
    seat = y - 310 * k
    o = [blob(ellipse_pts(x, y + 4, W / 2 + 40, 18, 20), _M(mode)["shadow"], .3)]
    for lx in (x0 + 50 * k, x1 - 50 * k):
        o.append(shape(rect_pts(lx - 14 * k, y - 50 * k, lx + 14 * k, y), lib.mul(WOOD_SH, kk), "", w=2.8, seed=600 + seed + int(lx) % 9))
    o.append(shape(lib.rrect(x0 + 60 * k, seat - 330 * k, x1 - 60 * k, seat + 30 * k, 40 * k), c,
                   blob(lib.rrect(x0 + 60 * k, seat - 120 * k, x1 - 60 * k, seat + 30 * k, 30 * k), sh, .7)
                   + line([(x, seat - 310 * k), (x + 4, seat - 40 * k)], 3.0, sh, taper=.3, wmin=.4, seed=610 + seed), w=4.2, seed=611 + seed))
    o.append(shape(lib.rrect(x0 + 40 * k, y - 120 * k, x1 - 40 * k, y - 40 * k, 16 * k), sh, "", w=3.6, seed=612 + seed))
    for i, (a, b) in enumerate(((x0 + 70 * k, x - 4), (x + 4, x1 - 70 * k))):
        o.append(shape(lib.rrect(a, seat - 40 * k, b, y - 110 * k, 26 * k), hi, blob(lib.rrect(a, seat + 40 * k, b, y - 110 * k, 20 * k), c, .8),
                       w=3.6, seed=620 + seed + i))
    arm = []
    for i, (a, b) in enumerate(((x0, x0 + 110 * k), (x1 - 110 * k, x1))):
        a_svg = shape(lib.rrect(a, seat - 150 * k, b, y - 44 * k, 36 * k), c, blob(lib.rrect(a, seat - 20 * k, b, y - 44 * k, 30 * k), sh, .8)
                      + blob(lib.rrect(a + 10 * k, seat - 146 * k, b - 10 * k, seat - 110 * k, 18 * k), hi, .8), w=4.0, seed=630 + seed + i)
        arm.append(a_svg)
    return dict(back="".join(o) + arm[0], arm_r=arm[1])


def floor_lamp(x, y, k=1.0, mode="day", on=0.0):
    """Торшер у дивана: тонкая стойка, абажур-цилиндр; свет (если on) — только короткий чёткий веер вниз-вверх у абажура."""
    kk = _M(mode)["shade_k"]
    o = [shape(ellipse_pts(x, y - 6, 60, 12, 16), lib.mul("#4a4f5c", kk), "", w=3.0, seed=700)]
    o.append(line([(x, y - 10), (x + 2, y - 760 * k)], 10, lib.mul("#5a606e", kk), taper=0, wmin=1, seed=701))
    top = y - 760 * k
    o.append(shape([(x - 70 * k, top - 120 * k, 1), (x + 70 * k, top - 120 * k, 1), (x + 95 * k, top + 20 * k, 1), (x - 95 * k, top + 20 * k, 1)],
                   lib.mix(lib.mul("#e8c98a", kk), "#fff3c8", on), blob(rect_pts(x + 40 * k, top - 130 * k, x + 100 * k, top + 30 * k), lib.mul("#c9a866", kk), .5),
                   w=3.4, seed=702))
    return "".join(o)


def side_table(x, y, mode="day"):
    """Круглый столик у дивана (кружку/мобильник ставит сцена дном на y − 300)."""
    kk = _M(mode)["shade_k"]
    c = lib.mul(WOOD, kk)
    o = [shape(rect_pts(x - 10, y - 290, x + 10, y), lib.mul(WOOD_SH, kk), "", w=2.8, seed=720)]
    o.append(shape(ellipse_pts(x, y - 4, 60, 12, 14), lib.mul(WOOD_SH, kk), "", w=2.6, seed=721))
    o.append(shape(ellipse_pts(x, y - 300, 120, 26, 22), c, blob(ellipse_pts(x + 10, y - 294, 110, 20, 20), lib.mul(WOOD_HI, kk), .6), w=3.2, seed=722))
    return "".join(o)


def sofa_scene(t, mode="day"):
    """Угол с диваном. Порядок: bg → sofa → [Дима сидит, кот на коленях] → front (правый подлокотник) → [кот на подлокотнике, «кот»].
    Над правым подлокотником CLEAN_WALL — чистая стена (ни картинок, ни солнца, ни теней): там пишется «кот»."""
    o = [wall_floor(mode)]
    # картина над ЛЕВОЙ половиной дивана и торшер слева — чистая стена справа остаётся пустой
    o.append(wall_picture(1960, 520, 260, 190, mode, seed=5))
    o.append(floor_lamp(1600, FL, 1.0, mode, on=0.0))
    o.append(side_table(1700, FL, mode))
    o.append(rug(2250, FL + 90, 560, 95, mode, seed=7))
    sf = sofa(SOFA[0], SOFA[1], SOFA[2], mode)
    return dict(bg="".join(o), sofa=sf["back"], front=sf["arm_r"])
