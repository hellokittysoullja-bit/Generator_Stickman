"""Места рилса 63 «кофе» (пишет группа C; берут все). Основа — common/room.py рилсов 62 и 61.

Подключение:  sys.path.insert(0, COMMON); import room as R   (COMMON = videos/63_kofe/story/common; lib/props рядом).
Мир кадра 1080×1920, камера снаружи (lib.cam(cx, cy, s)); мир шире кадра: x −900…2000, y −600…2600.
Букв и цифр нигде нет: банки и книги — цветные, часы — props.clock (только стрелки). Свет — плоскими пятнами с чёткой формой
(полоса солнца формы окна, круг лампы), без огромных мягких овалов. Все функции возвращают строку SVG в мировых координатах
(градиенты — динамические defs, вызывать после lib.dyn_begin()). Порядок в клипе: bg → люди → front.

КУХНЯ (s01, s03, s06, s12, s13, s17, s18)  — kitchen(t, mode, clock=(ah, am), items=..., rack_mug=False) -> dict(bg, table, front)
    mode: "morning" (утро, персиковое небо — хук и петля), "day" (день), "grey" (серое утро, тучи, стена холоднее),
          "sunny" (солнечное утро: полоса солнца формы окна на стене и на столе, чёткие края)
    K_FLOOR=1640  низ стены (пол ниже)          K_COUNTER=1060 верх задней столешницы (сушилка, кофейник ставятся на неё)
    K_TABLE=(130, 1010, 1250, 120)  стол Димы перед ним: x0, x1, передняя кромка y, глубина верха (верх виден сверху).
        Предметы на столе — дном на y ∈ [K_TABLE[2] − 110, K_TABLE[2] − 8] (ниже — ближе).
        table — ножки + крышка (класть ПОСЛЕ Димы: стол стоит перед ним); предметы на столе — после table.
    K_DIMA=(470, 1330)  таз стоящего Димы (people.figure(..., x, y, s≈1.0)): голова ≈ 560…870, крышка стола закрывает ноги.
    K_WIN=(60, 250, 420, 760)  окно (x0, y0, x1, y1)     K_CLOCK=(640, 250, 1.0)  часы на стене (центр, масштаб)
    K_RACK=(860, K_COUNTER)  сушилка на задней столешнице (низ, центр); rack_mug=True — кружка вверх дном в сушилке
    K_POT=(1120, K_COUNTER)  место кофейника на задней столешнице (кофейник ставит сцена из props)
    CAM_K_WIDE=(540, 960, 1.0)   общий план кухни (Дима ≈ 55 % высоты кадра вместе с краем стола)
    CAM_K_MID=(520, 860, 1.3)    средний план (лицо, руки, стол)
    CAM_K_FACE=(520, 760, 1.75)  наезд на лицо
    table_crack(u, seed)   трещина-«пустыня» по столешнице: u 0…1 — сколько пробежала (штрих тушью)

КОМНАТА С ДИВАНОМ ДНЁМ (s08)  — living(t) -> dict(bg, front)
    L_FLOOR=1560  низ стены     SOFA=(540, 1560, 1.0)  диван: центр низа, масштаб; верх сиденья L_SEAT_Y=1300
    L_DIMA=(540, 1290)  таз сидящего Димы (бёдра вперёд по сиденью, голени вниз, ступни на пол y≈1600)
    front — передний подлокотник не нужен (диван анфас), поэтому front = подушка у края + торшер не перекрывает. CAM_L=(540, 1000, 1.0)

НОЧНАЯ КОМНАТА СО СТОЛОМ (s09, s10)  — night_room(t, lamp_on=1.0, flick=0.0, clock=(ah, am)) -> dict(bg, pool, desk, front)
    N_FLOOR=1600   N_DESK=(150, 1150, 1210, 130)  стол: x0, x1, передняя кромка, глубина верха (Дима сидит ЗА столом, лицом к нам)
    N_DIMA=(560, 1330)  таз сидящего Димы за столом      N_LAMP=(920, N_DESK[2] − 70)  дно настольной лампы на столе
    N_BED=(40, 1600)  пустая кровать позади слева (сбоку, ножки на полу), N_WIN=(640, 170, 1000, 620) окно с луной
    pool — небольшой круг света лампы с чёткой формой (на стол, ДО предметов); desk — стол (ПОСЛЕ Димы); front — лампа
    CAM_N=(540, 980, 1.0)

СПАЛЬНЯ НОЧЬЮ  — два ракурса:
    bed_top(t, glow=0.0)  -> dict(bg, blanket_fn)  вид СВЕРХУ (s11): пол-доски сверху, кровать вдоль кадра (изголовье вверху),
        тумбочка слева у изголовья, полоса лунного света формы окна по полу и одеялу (чёткие края).
        B_TOP_BED=(540, 980, 600, 1300) центр кровати, ширина, длина; подушка у изголовья y≈420…560; Дима лежит на спине
        головой на подушке (голова ≈ (540, 500)); B_TOP_STAND=(110, 470) центр тумбочки (часы, кружка — сцена).
        quilt(t, crumple, y_top) — одеяло сверху, crumple 0…1 комкается складками (класть ПОСЛЕ туловища Димы)
    bed_side(t, warm=1.0) -> dict(bg, front)  вид СБОКУ (s14): кровать сбоку (изголовье слева), тумбочка с маленькой
        лампой (тёплый круг с чётким краем), окно с луной. B_SIDE_BED=(560, 1500, 1.55) ножки и масштаб (матрас y≈1317);
        B_SIDE_STAND=(80, 1500) тумбочка (верх y≈1240), B_SIDE_WIN=(760, 230, 1040, 700). CAM_B_SIDE=(540, 1060, 1.0)

КУХОННЫЙ ПОЛ КРУПНО (s15, s16)  — kitchen_floor(t, mode="morning") -> dict(bg, front)
    низкая камера: нижние шкафы с цоколем, плинтус, доски пола в перспективе, пятно солнца формы окна на полу.
    KF_FLOOR=1000 линия цоколя/пола (дальше — пол до низа кадра), KF_SPOT=(300, 1500) центр мест для кружки/блюдца/кота
    (кот стоит лапами на y 1350…1650 — чем ниже, тем ближе), CAM_KF=(540, 960, 1.0)
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

# ─────────────── кухня ───────────────
K_FLOOR = 1640.0
K_COUNTER = 1060.0
K_TABLE = (130.0, 1010.0, 1250.0, 120.0)
K_DIMA = (470.0, 1330.0)
K_WIN = (60.0, 250.0, 420.0, 760.0)
K_CLOCK = (640.0, 250.0, 1.0)
K_RACK = (860.0, K_COUNTER)
K_POT = (1120.0, K_COUNTER)
CAM_K_WIDE = (540.0, 960.0, 1.0)
CAM_K_MID = (520.0, 860.0, 1.3)
CAM_K_FACE = (520.0, 760.0, 1.75)
# ─────────────── комната с диваном ───────────────
L_FLOOR = 1560.0
SOFA = (540.0, 1560.0, 1.0)
L_SEAT_Y = 1300.0
L_DIMA = (540.0, 1290.0)
CAM_L = (540.0, 1000.0, 1.0)
# ─────────────── ночная комната ───────────────
N_FLOOR = 1600.0
N_DESK = (150.0, 1150.0, 1210.0, 130.0)
N_DIMA = (560.0, 1330.0)
N_LAMP = (920.0, N_DESK[2] - 70.0)
N_BED = (40.0, 1600.0)
N_WIN = (640.0, 170.0, 1000.0, 620.0)
CAM_N = (540.0, 980.0, 1.0)
# ─────────────── спальня ───────────────
B_TOP_BED = (540.0, 980.0, 600.0, 1300.0)
B_TOP_STAND = (110.0, 470.0)
B_SIDE_BED = (560.0, 1500.0, 1.55)
B_SIDE_STAND = (80.0, 1500.0)
B_SIDE_WIN = (760.0, 230.0, 1040.0, 700.0)
CAM_B_SIDE = (540.0, 1060.0, 1.0)
# ─────────────── кухонный пол ───────────────
KF_FLOOR = 1000.0
KF_SPOT = (300.0, 1500.0)
CAM_KF = (540.0, 960.0, 1.0)

WOOD, WOOD_SH, WOOD_HI = "#b27c4c", "#8a5b32", "#ce9a68"
LIGHTWOOD, LIGHTWOOD_SH, LIGHTWOOD_HI = "#d8b07c", "#b48a58", "#ecc995"

# режимы кухни: стена, плитка, шкафы, пол, небо (верх, середина, низ)
KMODE = {
    "morning": dict(wall="#f2dfbf", wall_sh="#e2caa2", tile="#f7efdf", tile_ln="#dccdb0", cab="#6fa3a0", cab_sh="#55827f", cab_hi="#8fc0bc",
                    floor="#c8915c", floor_ln="#8a5b34", sky=("#f6b98c", "#f8d3a8", "#fbe8cc"), sun="#ffe2a0"),
    "day": dict(wall="#efe2c6", wall_sh="#ddcca8", tile="#f6f1e4", tile_ln="#d8cdb4", cab="#6fa3a0", cab_sh="#55827f", cab_hi="#8fc0bc",
                floor="#c8915c", floor_ln="#8a5b34", sky=("#7fb8e8", "#b7dbf2", "#eaf4f8"), sun="#fff0b0"),
    "grey": dict(wall="#d4d0c6", wall_sh="#bdb8ad", tile="#e2ded4", tile_ln="#c3beb2", cab="#7f9796", cab_sh="#667b7a", cab_hi="#9aaeac",
                 floor="#a88a6c", floor_ln="#6e5640", sky=("#8f97a3", "#a9b0ba", "#c3c8cf"), sun=None),
    "sunny": dict(wall="#f6e4bf", wall_sh="#e6cfa2", tile="#fbf3e2", tile_ln="#e0d0ae", cab="#6fa8a3", cab_sh="#558680", cab_hi="#93c8c1",
                  floor="#d09a62", floor_ln="#8f5f36", sky=("#6fb2ec", "#acd8f5", "#e6f4fb"), sun="#ffe9a6"),
}


def rs(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


def _clock(x, y, k, ah, am, seed=0):
    """Часы без цифр и делений — props.clock (группа A); пока его нет — свои: обод, циферблат, две стрелки."""
    fn = getattr(PR, "clock", None)
    if fn is not None:
        return fn(x, y, 90.0 * k, ah, am, seed=seed)
    r = 74 * k
    o = shape(ellipse_pts(x, y, r, r, 28), "#d9534a", blob(ellipse_pts(x + r * .12, y + r * .12, r, r, 28), "#b13f37"), w=4.2, seed=900 + seed)
    o += shape(ellipse_pts(x, y, r * .8, r * .8, 26), "#fbf6ea", "", w=3.0, seed=901 + seed)
    for a, L, w in ((ah, .42, 9), (am, .64, 6)):
        rad = math.radians(a - 90)
        o += line([(x, y), (x + math.cos(rad) * r * L, y + math.sin(rad) * r * L)], w * k, INK, taper=.3, wmin=.5, seed=902 + seed + int(w))
    o += blob(ellipse_pts(x, y, 7 * k, 7 * k, 10), INK)
    return o


# ═════════════════════════ окно с режимами ═════════════════════════
def window(x0, y0, x1, y1, mode, t=0.0, seed=0, curtain="#e9b96a"):
    """Окно (рамка, крестовина, подоконник, шторы): небо режима, облака плывут от t; ночью — луна и звёзды."""
    sd = 7300 + seed
    fr = 18
    ix0, iy0, ix1, iy1 = x0 + fr, y0 + fr, x1 - fr, y1 - fr
    if mode == "night":
        sky = ("#0e1330", "#1e2756", "#33407a")
    else:
        sky = KMODE[mode]["sky"]
    g = lib.lin_grad([(0, sky[0], 1), (.55, sky[1], 1), (1, sky[2], 1)], 0, 0, 0, 1)
    inner = f'<path d="M{f(ix0)} {f(iy0)}H{f(ix1)}V{f(iy1)}H{f(ix0)}Z" fill="url(#{g})"/>'
    w, h = ix1 - ix0, iy1 - iy0
    if mode == "night":
        for i in range(8):
            sx = ix0 + 30 + (i * 97 + sd) % int(max(60, w - 60))
            sy = iy0 + 26 + (i * 61 + sd // 3) % int(max(40, h * .45))
            inner += PR.star4(sx, sy, 7 + (i % 3) * 2, .6 + .4 * math.sin(t * 2.2 + i * 1.7))
        mx, my, mr = ix1 - w * .3, iy0 + h * .22, max(26.0, w * .12)
        inner += shape(ellipse_pts(mx, my, mr, mr, 22), "#fbf1c8", blob(ellipse_pts(mx + mr * .45, my - mr * .1, mr * .88, mr * .95, 18), "#e5d9a5"),
                       w=2.6, seed=sd + 70)
        inner += blob([(ix0 - 5, iy1 + 5, 1)] + [(ix0 + w * i / 6, iy1 - h * (.12 + .05 * ((i * 7) % 3))) for i in range(7)] + [(ix1 + 5, iy1 + 5, 1)],
                      "#141a3c")
    else:
        if mode == "morning":
            inner += shape(ellipse_pts(ix0 + w * .3, iy1 - h * .28, w * .13, w * .13, 20), "#ffd27a", "", w=2.4, seed=sd + 40)
        if mode in ("day", "sunny"):
            inner += shape(ellipse_pts(ix0 + w * .25, iy0 + h * .22, w * .1, w * .1, 20), "#fff0a8", "", w=2.4, seed=sd + 41)
        cl = "#ffffff" if mode != "grey" else "#d7dbe1"
        n_cl = 3 if mode != "grey" else 5
        for j in range(n_cl):
            cx = ix0 + ((j * 173 + t * 14 + sd) % (w + 160)) - 80
            cy = iy0 + h * (.18 + .17 * j)
            cw = w * (.26 + .06 * (j % 2)) * (1.3 if mode == "grey" else 1)
            pts = [(cx - cw / 2, cy + 12)] + [(cx - cw / 2 + cw * i / 5, cy - 14 - 14 * math.sin(i * 1.9 + j)) for i in range(6)] + [(cx + cw / 2, cy + 12)]
            inner += blob(pts, cl)
        # крыши за окном внизу
        roof = "#9fb0bf" if mode != "grey" else "#8c939c"
        if mode == "morning":
            roof = "#c99a8a"
        inner += blob([(ix0 - 5, iy1 + 5, 1), (ix0 - 5, iy1 - h * .16, 1), (ix0 + w * .22, iy1 - h * .16, 1), (ix0 + w * .22, iy1 - h * .26, 1),
                       (ix0 + w * .5, iy1 - h * .26, 1), (ix0 + w * .5, iy1 - h * .13, 1), (ix0 + w * .72, iy1 - h * .13, 1), (ix0 + w * .72, iy1 - h * .22, 1),
                       (ix1 + 5, iy1 - h * .22, 1), (ix1 + 5, iy1 + 5, 1)], roof)
        if mode == "grey":   # капли дождя по стеклу — короткие штрихи
            for i in range(14):
                rx = ix0 + 20 + (i * 53 + sd) % int(w - 30)
                ry = iy0 + ((i * 89 + t * 260) % h)
                inner += line([(rx, ry), (rx - 3, ry + 22)], 3.0, "#eef2f6", taper=.5, wmin=.3, seed=sd + 100 + i)
    frame = "#ede6d8"
    out = [shape(rect_pts(x0, y0, x1, y1), frame, "", w=4.4, seed=sd)]
    out.append(shape(rect_pts(ix0, iy0, ix1, iy1), sky[1], inner, w=3.4, seed=sd + 1))
    xm, ym = (x0 + x1) / 2, iy0 + h * .46
    out.append(blob(rect_pts(xm - 6, iy0, xm + 6, iy1), frame) + line([(xm - 6, iy0), (xm - 6, iy1)], 2.6, INK, seed=sd + 2)
               + line([(xm + 6, iy0), (xm + 6, iy1)], 2.6, INK, seed=sd + 3))
    out.append(blob(rect_pts(ix0, ym - 6, ix1, ym + 6), frame) + line([(ix0, ym - 6), (ix1, ym - 6)], 2.6, INK, seed=sd + 4)
               + line([(ix0, ym + 6), (ix1, ym + 6)], 2.6, INK, seed=sd + 5))
    out.append(shape(lib.rrect(x0 - 26, y1, x1 + 26, y1 + 22, 5), "#dcd3c0", blob(rect_pts(x0 - 30, y1 + 12, x1 + 30, y1 + 26), "#b9af98"), w=3.4, seed=sd + 6))
    if curtain:
        sw = 1.5 * math.sin(t * .8)
        for sgn, cx in ((-1, x0 - 4), (1, x1 + 4)):
            pts = [(cx - sgn * 4, y0 - 20, 1), (cx + sgn * 70, y0 - 12), (cx + sgn * (60 + sw), y1 * .6 + y0 * .4), (cx + sgn * 78, y1 + 14, 1), (cx - sgn * 6, y1 + 14, 1)]
            out.append(shape(pts, curtain, line([(cx + sgn * 28, y0), (cx + sgn * 38, y1)], 5, lib.mul(curtain, (.8, .8, .8)), taper=.4, wmin=.3,
                                                seed=sd + 8 + int(sgn + 1)), w=3.4, seed=sd + 9 + int(sgn + 1)))
        out.append(shape(lib.rrect(x0 - 40, y0 - 34, x1 + 40, y0 - 20, 6), "#8a5b32", "", w=3.0, seed=sd + 14))
    return "".join(out)


def _sun_quad(A, U, V, col, col2, inset=.06):
    """Полоса солнца формы окна: четыре стекла (A — угол, U вдоль ширины, V вдоль высоты), крестовина — тень, чёткие края."""
    A, U, V = np.array(A, float), np.array(U, float), np.array(V, float)
    o = []
    for (u0, u1) in ((0.0, .47), (.53, 1.0)):
        for (v0, v1) in ((0.0, .43), (.5, 1.0)):
            pts = [tuple(A + U * u0 + V * v0) + (1,), tuple(A + U * u1 + V * v0) + (1,), tuple(A + U * u1 + V * v1) + (1,), tuple(A + U * u0 + V * v1) + (1,)]
            o.append(blob(pts, col))
            q = [tuple(A + U * (u0 + .03) + V * (v0 + inset)) + (1,), tuple(A + U * (u1 - .03) + V * (v0 + inset)) + (1,),
                 tuple(A + U * (u1 - .03) + V * (v0 + inset + .1)) + (1,), tuple(A + U * (u0 + .03) + V * (v0 + inset + .1)) + (1,)]
            o.append(blob(q, col2))
    return "".join(o)


# ═════════════════════════ КУХНЯ ═════════════════════════
def _jar(x, y, w, h, col, lid, seed):
    """Банка без надписей: стекло с цветным содержимым, крышка."""
    o = shape(lib.rrect(x - w / 2, y - h, x + w / 2, y, 10), "#e6eef0",
              blob(lib.rrect(x - w / 2, y - h * .72, x + w / 2, y, 8), col) + blob(rect_pts(x + w * .18, y - h, x + w * .32, y), "#ffffff", .0)
              + line([(x - w * .3, y - h * .85), (x - w * .3, y - h * .25)], 4, "#ffffff", taper=.4, wmin=.3, seed=seed + 2), w=3.0, seed=seed)
    o += shape(lib.rrect(x - w / 2 - 4, y - h - 18, x + w / 2 + 4, y - h + 2, 5), lid, "", w=3.0, seed=seed + 1)
    return o


def _plate(x, y, r, tilt, seed, col="#f4f1ea", rim="#8fb3d6"):
    """Тарелка на ребре (в сушилке): эллипс, наклон tilt."""
    return shape(ellipse_pts(x, y, r * .26, r, 22, rot=tilt), col, blob(ellipse_pts(x, y, r * .17, r * .78, 18, rot=tilt), lib.mix(col, rim, .35)),
                 w=3.0, seed=seed)


def rack(x, y, k=1.0, mug=False, t=0.0):
    """Сушилка для посуды на столешнице: решётка-корзина, две тарелки на ребре; mug=True — кружка вверх дном на штырьке."""
    o = []
    w, h = 230 * k, 90 * k
    for i, dx in enumerate((-60, -20, 20)):
        o.append(_plate(x + dx * k, y - h - 50 * k, 78 * k, 8 - 4 * i, 960 + i))
    bas = lib.rrect(x - w / 2, y - h, x + w / 2, y, 12 * k)
    inner = ""
    for i in range(1, 7):
        xx = x - w / 2 + w * i / 7
        inner += line([(xx, y - h), (xx, y)], 3.0 * k, "#7a8794", taper=.0, wmin=1, seed=970 + i)
    inner += line([(x - w / 2, y - h * .5), (x + w / 2, y - h * .5)], 3.0 * k, "#7a8794", taper=.0, wmin=1, seed=978)
    o.append(shape(bas, "#c4ccd4", inner, w=3.4, seed=979))
    if mug:
        mx, my = x + 80 * k, y - h + 6 * k
        o.append(line([(mx, my), (mx, my - 120 * k)], 5 * k, "#7a8794", taper=0, wmin=1, seed=981))
        o.append(_mug_upside(mx, my - 4 * k, k * .9, seed=982))
    return "".join(o)


def _mug_upside(x, y, k, seed=0, col="#d0553f", sh="#9e3a2a"):
    """Кружка вверх дном (дно сверху, ручка справа), низ на y. Без надписей."""
    o = shape([(x - 44 * k, y, 1), (x + 44 * k, y, 1), (x + 40 * k, y - 96 * k, 1), (x - 40 * k, y - 96 * k, 1)], col,
              blob([(x + 14 * k, y), (x + 50 * k, y), (x + 46 * k, y - 100 * k), (x + 12 * k, y - 100 * k)], sh), w=3.6, seed=seed)
    o += line([(x + 42 * k, y - 22 * k), (x + 72 * k, y - 30 * k), (x + 72 * k, y - 62 * k), (x + 41 * k, y - 72 * k)], 11 * k, INK, taper=.1, wmin=.8, seed=seed + 1)
    o += line([(x + 44 * k, y - 26 * k), (x + 66 * k, y - 32 * k), (x + 66 * k, y - 60 * k), (x + 43 * k, y - 68 * k)], 6 * k, col, taper=.1, wmin=.8, seed=seed + 2)
    o += shape(ellipse_pts(x, y - 96 * k, 40 * k, 9 * k, 16), lib.mul(col, (.85, .85, .85)), "", w=2.6, seed=seed + 3)
    return o


def _plant_pot(x, y, k, t, seed):
    o = []
    for j in range(5):
        a = math.radians(-90 + (j - 2) * 26 + 4 * math.sin(t * .9 + j))
        L = (70 + 18 * (j % 2)) * k
        p0 = (x, y - 50 * k)
        p1 = (x + math.cos(a) * L, y - 50 * k + math.sin(a) * L)
        nx, ny = -math.sin(a), math.cos(a)
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        o.append(shape([p0 + (1,), (mid[0] + nx * 16 * k, mid[1] + ny * 16 * k), p1 + (1,), (mid[0] - nx * 16 * k, mid[1] - ny * 16 * k)], "#5c9a52",
                       line([p0, p1], 2.2, "#3f6f3a", seed=seed + 20 + j), w=2.6, seed=seed + j))
    o.append(shape([(x - 34 * k, y - 56 * k, 1), (x + 34 * k, y - 56 * k, 1), (x + 26 * k, y, 1), (x - 26 * k, y, 1)], "#d9795e",
                   blob([(x + 8 * k, y - 56 * k), (x + 34 * k, y - 56 * k), (x + 26 * k, y), (x + 12 * k, y)], "#b85e45"), w=3.0, seed=seed + 10))
    return "".join(o)


def kitchen_wall(t, mode="morning", clock=(300.0, 0.0)):
    """Стена кухни: краска, фартук-плитка, окно, часы, верхние шкафы, полка с банками."""
    m = KMODE[mode]
    o = []
    g = lib.lin_grad([(0, m["wall"], 1), (1, m["wall_sh"], 1)], 0, -600, 0, K_COUNTER, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="-1400" width="4800" height="{f(K_FLOOR + 1400)}" fill="url(#{g})"/>')
    # фартук-плитка между столешницей и верхними шкафами
    o.append(f'<rect x="-1600" y="700" width="4800" height="{f(K_COUNTER - 700)}" fill="{m["tile"]}"/>')
    for k in range(-20, 40):
        o.append(line([(k * 80, 700), (k * 80, K_COUNTER)], 2.2, m["tile_ln"], taper=.02, wmin=.95, seed=1000 + k, op=.9))
    for k in range(1, 5):
        o.append(line([(-1600, 700 + k * 72), (2800, 700 + k * 72)], 2.2, m["tile_ln"], taper=.02, wmin=.95, seed=1080 + k, op=.9))
    o.append(shape(rect_pts(-1600, 690, 2800, 708), m["cab"], blob(rect_pts(-1600, 700, 2800, 708), m["cab_sh"]), w=3.2, seed=1090))
    o.append(window(*K_WIN, mode, t, seed=11))
    o.append(_plant_pot(150, K_WIN[3] + 2, 1.0, t, 1100))
    o.append(_clock(K_CLOCK[0], K_CLOCK[1], K_CLOCK[2], clock[0], clock[1], seed=3))
    # верхние шкафы справа
    for i, (x0, x1) in enumerate(((800, 1060), (1070, 1330), (1340, 1600))):
        y0, y1 = 140, 560
        inner = blob(rect_pts(x1 - 26, y0, x1, y1), m["cab_sh"]) + blob(rect_pts(x0 + 16, y0 + 16, x0 + 26, y1 - 16), m["cab_hi"])
        o.append(shape(rect_pts(x0, y0, x1, y1), m["cab"], inner, w=4.0, seed=1110 + i))
        o.append(shape(lib.rrect(x0 + 24, y1 - 90, x0 + 38, y1 - 30, 6), "#c4ccd4", "", w=2.4, seed=1120 + i))
    # открытая полка с банками между окном и шкафами — над часами не мешает
    sy = 560.0
    o.append(shape(rect_pts(560, sy, 760, sy + 18), WOOD, blob(rect_pts(560, sy + 10, 760, sy + 18), WOOD_SH), w=3.2, seed=1130))
    o.append(_jar(600, sy, 46, 78, "#6b4630", "#d0553f", 1140))     # кофе в зёрнах — тёмное
    o.append(_jar(660, sy, 42, 64, "#e8c35a", "#5c9a78", 1150))     # макароны — жёлтое
    o.append(_jar(714, sy, 40, 70, "#c97a4a", "#4f78b5", 1160))     # чай — рыжее
    return "".join(o)


def kitchen_counter(t, mode="morning", rack_mug=False):
    """Задняя столешница с нижними шкафами вдоль стены, сушилка, пол."""
    m = KMODE[mode]
    o = []
    # пол
    o.append(f'<rect x="-1600" y="{f(K_FLOOR)}" width="4800" height="1400" fill="{m["floor"]}"/>')
    for k, y in enumerate((K_FLOOR + 30, K_FLOOR + 90, K_FLOOR + 180, K_FLOOR + 310, K_FLOOR + 480, K_FLOOR + 700)):
        o.append(line([(-1600, y), (2800, y)], 3.0, m["floor_ln"], taper=0, wmin=1, seed=1200 + k, op=.55))
    r = rs(12)
    for j in range(22):
        x = r.uniform(-800, 1900)
        y0 = K_FLOOR + r.choice([0, 30, 90, 180, 310, 480])
        o.append(line([(x, y0), (x + r.uniform(-4, 4), y0 + r.uniform(40, 120))], 2.4, m["floor_ln"], taper=0, wmin=1, seed=1220 + j, op=.45))
    # нижние шкафы
    y0, y1 = K_COUNTER + 30, K_FLOOR - 30
    for i, (x0, x1) in enumerate(((560, 820), (830, 1090), (1100, 1360), (1370, 1630))):
        inner = blob(rect_pts(x1 - 26, y0, x1, y1), m["cab_sh"]) + blob(rect_pts(x0 + 14, y0 + 14, x0 + 24, y1 - 14), m["cab_hi"])
        o.append(shape(rect_pts(x0, y0, x1, y1), m["cab"], inner, w=4.0, seed=1300 + i))
        o.append(shape(lib.rrect(x0 + 100, y0 + 40, x0 + 160, y0 + 54, 6), "#c4ccd4", "", w=2.4, seed=1310 + i))
    o.append(shape(rect_pts(560, y1, 1630, K_FLOOR), lib.mul(m["cab_sh"], (.8, .8, .8)), "", w=3.0, seed=1320))
    # столешница
    o.append(shape(rect_pts(540, K_COUNTER - 6, 1660, K_COUNTER + 30), LIGHTWOOD, blob(rect_pts(540, K_COUNTER + 16, 1660, K_COUNTER + 30), LIGHTWOOD_SH),
                   w=3.8, seed=1330))
    o.append(rack(K_RACK[0], K_RACK[1] - 4, 1.0, mug=rack_mug, t=t))
    return "".join(o)


def kitchen_sun(mode):
    """Солнечная полоса формы окна на стене справа от окна (только sunny; утром и днём солнца на стене нет)."""
    m = KMODE[mode]
    if not m["sun"]:
        return ""
    if mode != "sunny":
        return ""
    u = .7
    col = lib.mix(m["tile"], m["sun"], u)
    col2 = lib.mix(m["tile"], "#fff8e0", u + .15)
    col_w = lib.mix(m["wall"], m["sun"], u)
    o = _sun_quad((470, 640), (300, -40), (110, 380), col_w if mode != "sunny" else col, col2)
    return o


def table(x0=None, x1=None, y=None, d=None, seed=0):
    """Стол Димы перед ним: крышка (верх виден сверху), торец, ножки до пола. Класть ПОСЛЕ Димы."""
    tx0, tx1, ty, td = K_TABLE
    x0 = tx0 if x0 is None else x0
    x1 = tx1 if x1 is None else x1
    y = ty if y is None else y
    d = td if d is None else d
    sd = 1400 + seed
    o = []
    for lx in (x0 + 40, x1 - 70):
        o.append(shape(rect_pts(lx, y + 30, lx + 34, K_FLOOR + 60), WOOD_SH, blob(rect_pts(lx + 20, y + 30, lx + 34, K_FLOOR + 60), lib.mul(WOOD_SH, (.8, .8, .8))),
                       w=3.6, seed=sd + int(lx)))
    top = [(x0, y, 1), (x0 + 30, y - d, 1), (x1 - 30, y - d, 1), (x1, y, 1)]
    r = rs(sd)
    inner = blob(rect_pts(x0, y - 14, x1, y + 2), lib.mul(LIGHTWOOD, (.94, .94, .94)))
    for j in range(4):
        yy = y - d * (.2 + .2 * j) + r.uniform(-5, 5)
        xa = x0 + r.uniform(40, 300)
        inner += line([(xa, yy), (xa + r.uniform(160, 360), yy + r.uniform(-3, 3))], 2.6, LIGHTWOOD_HI, taper=.4, wmin=.3, seed=sd + 10 + j)
    o.append(shape(top, LIGHTWOOD, inner, w=4.2, seed=sd + 5))
    o.append(shape(rect_pts(x0, y, x1, y + 30), LIGHTWOOD_SH, blob(rect_pts(x0, y + 18, x1, y + 32), lib.mul(LIGHTWOOD_SH, (.85, .85, .85))), w=4.0, seed=sd + 6))
    return "".join(o)


def table_sun(mode):
    """Солнце формы окна на столешнице (sunny) — класть после table, до предметов."""
    if mode != "sunny":
        return ""
    col = lib.mix(LIGHTWOOD, "#ffe9a6", .55)
    col2 = lib.mix(LIGHTWOOD, "#fff8e0", .7)
    y = K_TABLE[2]
    A = (180.0, y - 104)
    return _sun_quad(A, (260, 0), (60, 94), col, col2, inset=.1)


def table_crack(u, seed=0, x=600.0, y=None):
    """Трещина-«пустыня» по столешнице: ломаная тушью с ответвлениями, бежит слева направо на u 0…1."""
    if u <= 0.01:
        return ""
    y = K_TABLE[2] - 50 if y is None else y
    r = rs(77 + seed)
    pts = [(x - 260, y + 10)]
    for i in range(1, 9):
        pts.append((x - 260 + 520 * i / 8, y + 10 + r.uniform(-22, 22) - 6 * i))
    n = max(2, int(round(1 + u * 8)))
    o = [line(pts[:n], 5.5, INK, taper=.35, wmin=.25, seed=1500 + seed)]
    for i in range(2, n, 2):
        a = pts[i]
        b = (a[0] + r.uniform(-30, 30), a[1] + (34 if i % 4 else -30))
        o.append(line([a, ((a[0] + b[0]) / 2 + 6, (a[1] + b[1]) / 2), b], 3.4, INK, taper=.6, wmin=.15, seed=1510 + seed + i))
    return "".join(o)


def kitchen(t, mode="morning", clock=(300.0, 0.0), rack_mug=False):
    """Кухня целиком: dict(bg — стена, окно, задняя столешница; table — стол перед Димой (+ солнце на нём); front — пусто)."""
    bg = kitchen_wall(t, mode, clock) + kitchen_sun(mode) + kitchen_counter(t, mode, rack_mug)
    return dict(bg=bg, table=table() + table_sun(mode), front="")


# ═════════════════════════ КОМНАТА С ДИВАНОМ ═════════════════════════
def sofa(x, y, k=1.0, seed=0, col="#4a6fa5"):
    """Диван анфас: спинка, две подушки сиденья, подлокотники, ножки. (x, y) — низ ножек, центр. Сиденье сверху y−260·k."""
    sd = 1600 + seed
    sh = lib.mul(col, (.78, .78, .82))
    hi = lib.mix(col, "#ffffff", .25)
    o = []
    for lx in (-380, 340):
        o.append(shape(rect_pts(x + lx * k, y - 40 * k, x + (lx + 40) * k, y), WOOD_SH, "", w=3.0, seed=sd + int(lx)))
    o.append(shape(lib.rrect(x - 400 * k, y - 560 * k, x + 400 * k, y - 200 * k, 40 * k), col, blob(rect_pts(x - 400 * k, y - 300 * k, x + 400 * k, y - 200 * k), sh),
                   w=4.6, seed=sd + 1))
    for i, (a, b) in enumerate(((-340, -5), (5, 340))):
        o.append(shape(lib.rrect(x + a * k, y - 520 * k, x + b * k, y - 300 * k, 30 * k), hi, blob(rect_pts(x + a * k, y - 330 * k, x + b * k, y - 300 * k), col),
                       w=3.6, seed=sd + 2 + i))
    o.append(shape(lib.rrect(x - 380 * k, y - 290 * k, x + 380 * k, y - 40 * k, 26 * k), col, blob(rect_pts(x - 380 * k, y - 130 * k, x + 380 * k, y - 40 * k), sh),
                   w=4.4, seed=sd + 4))
    for i, (a, b) in enumerate(((-370, -5), (5, 370))):
        o.append(shape(lib.rrect(x + a * k, y - 300 * k, x + b * k, y - 220 * k, 22 * k), hi, "", w=3.4, seed=sd + 5 + i))
    for i, sx in enumerate((-1, 1)):
        x0 = x + sx * 380 * k
        x1 = x + sx * 470 * k
        o.append(shape(lib.rrect(min(x0, x1), y - 400 * k, max(x0, x1), y - 40 * k, 30 * k), col,
                       blob(rect_pts(min(x0, x1), y - 140 * k, max(x0, x1), y - 40 * k), sh), w=4.4, seed=sd + 8 + i))
    return "".join(o)


def living(t):
    """Комната с диваном днём: стена, картина без букв, окно справа, торшер (выкл.), монстера, ковёр, диван. dict(bg, front)."""
    o = []
    wall = "#e9d9bd"
    g = lib.lin_grad([(0, "#f1e3c9", 1), (1, "#dcc9a6", 1)], 0, -400, 0, L_FLOOR, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="-1400" width="4800" height="{f(L_FLOOR + 1400)}" fill="url(#{g})"/>')
    o.append(shape(rect_pts(-1600, L_FLOOR - 40, 2800, L_FLOOR + 6), "#f3ede0", blob(rect_pts(-1600, L_FLOOR - 8, 2800, L_FLOOR + 6), "#d6cfc0"), w=3.4, seed=1700))
    o.append(f'<rect x="-1600" y="{f(L_FLOOR + 6)}" width="4800" height="1400" fill="#c8915c"/>')
    for k, y in enumerate((L_FLOOR + 40, L_FLOOR + 120, L_FLOOR + 240, L_FLOOR + 420)):
        o.append(line([(-1600, y), (2800, y)], 3.0, "#8a5b34", taper=0, wmin=1, seed=1710 + k, op=.55))
    o.append(window(840, 260, 1220, 900, "day", t, seed=21, curtain="#e9b96a"))
    # картина над диваном: море и солнце (без букв)
    px, py, pw, ph = 470.0, 470.0, 300.0, 210.0
    inner = blob(rect_pts(px - pw / 2, py - ph / 2, px + pw / 2, py + ph / 2), "#cfe6f0")
    inner += blob(ellipse_pts(px + 70, py - 30, 26, 26, 14), "#f2a65c")
    inner += blob([(px - pw / 2 - 4, py + 20), (px - 40, py + 6), (px + 40, py + 22), (px + pw / 2 + 4, py + 10), (px + pw / 2 + 4, py + ph / 2 + 4),
                   (px - pw / 2 - 4, py + ph / 2 + 4)], "#4a86b5")
    o.append(shape(rect_pts(px - pw / 2 - 18, py - ph / 2 - 18, px + pw / 2 + 18, py + ph / 2 + 18), "#c7a374",
                   blob(rect_pts(px - pw / 2 - 18, py + ph / 2, px + pw / 2 + 18, py + ph / 2 + 18), "#a58252"), w=3.4, seed=1720))
    o.append(shape(rect_pts(px - pw / 2, py - ph / 2, px + pw / 2, py + ph / 2), "#cfe6f0", inner, w=2.8, seed=1721))
    # торшер слева (выключен)
    o.append(PR.lamp_floor(-80, L_FLOOR, 1.7, on=0.0, seed=4))
    # ковёр
    o.append(shape(ellipse_pts(540, L_FLOOR + 130, 560, 90, 30), "#c8634a", blob(ellipse_pts(540, L_FLOOR + 130, 470, 64, 30), "#e08a5e"), w=3.6, seed=1730))
    o.append(sofa(*SOFA[:2], SOFA[2]))
    # подушка-думка у левого подлокотника
    o.append(shape([(170, L_SEAT_Y - 10, 1), (300, L_SEAT_Y - 40), (290, L_SEAT_Y - 170, 1), (160, L_SEAT_Y - 150)], "#e9b96a",
                   line([(190, L_SEAT_Y - 60), (280, L_SEAT_Y - 100)], 3, "#c99a4a", seed=1741), w=3.6, seed=1740))
    o.append(_plant_pot(1010, L_FLOOR - 4, 2.0, t, 1750))
    return dict(bg="".join(o), front="")


# ═════════════════════════ НОЧНАЯ КОМНАТА СО СТОЛОМ ═════════════════════════
NIGHT_WALL, NIGHT_WALL_SH, NIGHT_FLOOR = "#2c3466", "#222a56", "#1f2448"


def side_bed(x, y, k=1.0, seed=0, quilt="#c8553d", quilt_sh="#9a3b2b", crumple=0.0, empty=True):
    """Кровать сбоку: ножки на (x, y), изголовье слева. Матрас сверху y − 118·k. Пустая — подушка и ровное одеяло."""
    sd = 1800 + seed
    o = [PR.bed(x, y, k, seed=seed)]
    top = y - 118 * k
    o.append(shape(lib.rrect(x - 250 * k, top - 54 * k, x - 120 * k, top + 4 * k, 22 * k), "#f2e6cf",
                   blob(rect_pts(x - 250 * k, top - 12 * k, x - 120 * k, top + 4 * k), "#d6c4a3"), w=3.4, seed=sd + 1))
    cr = crumple
    qpts = [(x - 120 * k, top + 10 * k, 1), (x - 112 * k, top - 22 * k - 18 * cr * k), (x + 40 * k, top - 30 * k - 30 * cr * k), (x + 140 * k, top - 20 * k + 10 * cr * k),
            (x + 270 * k, top - 18 * k), (x + 286 * k, top + 70 * k, 1), (x - 120 * k, top + 70 * k, 1)]
    o.append(shape(qpts, quilt, blob(rect_pts(x - 130 * k, top + 34 * k, x + 290 * k, top + 72 * k), quilt_sh)
                   + line([(x - 40 * k, top - 10 * k), (x + 30 * k, top + 30 * k)], 3 * k, quilt_sh, seed=sd + 3)
                   + line([(x + 120 * k, top - 8 * k), (x + 170 * k, top + 26 * k)], 3 * k, quilt_sh, seed=sd + 4), w=3.8, seed=sd + 2))
    return "".join(o)


def night_room(t, lamp_on=1.0, flick=0.0, clock=(15.0, 30.0)):
    """Ночная комната: тёмно-синяя стена, окно с луной, часы за полночь, пустая кровать позади слева, стол перед Димой и лампа.
    dict(bg, pool, desk, front): bg → Дима → desk → pool → предметы → front(лампа)."""
    o = []
    g = lib.lin_grad([(0, "#353e74", 1), (1, NIGHT_WALL_SH, 1)], 0, -400, 0, N_FLOOR, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="-1400" width="4800" height="{f(N_FLOOR + 1400)}" fill="url(#{g})"/>')
    o.append(shape(rect_pts(-1600, N_FLOOR - 36, 2800, N_FLOOR + 6), "#3c4580", "", w=3.2, seed=1900))
    o.append(f'<rect x="-1600" y="{f(N_FLOOR + 6)}" width="4800" height="1400" fill="{NIGHT_FLOOR}"/>')
    for k, y in enumerate((N_FLOOR + 40, N_FLOOR + 120, N_FLOOR + 240)):
        o.append(line([(-1600, y), (2800, y)], 3.0, "#14183a", taper=0, wmin=1, seed=1910 + k, op=.7))
    o.append(window(*N_WIN, "night", t, seed=31, curtain="#4b3b6e"))
    o.append(_clock(330, 330, 1.0, clock[0], clock[1], seed=7))
    # пустая кровать позади слева
    o.append(side_bed(N_BED[0], N_BED[1], 1.25, seed=3, quilt="#5a5f9a", quilt_sh="#40457a"))
    # стул за столом (спинка видна за Димой)
    cx = N_DIMA[0]
    o.append(shape(lib.rrect(cx - 150, 940, cx + 150, 1290, 26), "#3d3a52", blob(rect_pts(cx + 100, 940, cx + 150, 1290), "#2c2a3d"), w=4.0, seed=1930))
    lp = desk_lamp(lamp_on, flick)
    return dict(bg="".join(o), desk=table(N_DESK[0], N_DESK[1], N_DESK[2], N_DESK[3], seed=7), pool=lp["pool"], front=lp["lamp"], wall_light=lp["wall"])


def desk_lamp(on=1.0, flick=0.0):
    """Настольная лампа на ночном столе (props.lamp_desk) и её свет: небольшой эллипс на столе с ЧЁТКИМ краем + веер на стене.
    Если в props есть своя lamp_desk с кругом света — берётся она."""
    x, y = N_LAMP
    on = max(0.0, on * (1 - .1 * flick))
    pool = ""
    wall = ""
    if on > 0.02:
        c1 = lib.mix(LIGHTWOOD, "#ffe7a3", .65 * on)
        c2 = lib.mix(LIGHTWOOD, "#fff6d8", .8 * on)
        pool = blob(ellipse_pts(x - 120, y + 20, 230, 50, 30), c1) + blob(ellipse_pts(x - 110, y + 20, 140, 30, 26), c2)
    lamp = PR.lamp_desk(x, y, 1.6, on=on, tilt=-12, seed=5)
    return dict(pool=pool, lamp=lamp, wall=wall)


# ═════════════════════════ СПАЛЬНЯ: ВИД СВЕРХУ ═════════════════════════
def quilt(t, crumple=0.0, y_top=760.0, seed=0, col="#5a6fb0", sh="#41528c", breath=0.0):
    """Одеяло, вид сверху: от y_top до низа кровати. crumple 0…1 — складки и сбитый край; breath — подъём на вдохе (мм)."""
    x, y, w, L = B_TOP_BED
    x0, x1, y1 = x - w / 2 + 14, x + w / 2 - 14, y + L / 2 - 20
    r = rs(31 + seed)
    cr = crumple
    pts = [(x0 - 10 * cr, y_top + 20 * cr, 1)]
    for i in range(1, 6):
        pts.append((x0 + (x1 - x0) * i / 6, y_top - 10 * breath + (r.uniform(-30, 30) + 25 * math.sin(i * 2.1)) * cr))
    pts += [(x1 + 16 * cr, y_top + 30 * cr, 1), (x1 + 30 * cr, y1 - 60 * cr), (x1, y1, 1), (x0, y1, 1), (x0 - 24 * cr, y1 - 120 * cr)]
    inner = blob(rect_pts(x0 - 40, y_top - 40, x0 + 40, y1 + 20), sh)
    for i in range(3):
        yy = y_top + 160 + i * 230
        inner += line([(x0 + 40, yy + 10 * cr * math.sin(i)), (x1 - 40, yy - 20 * cr * math.cos(i * 1.3))], 3.4, sh, taper=.3, wmin=.4, seed=2000 + i)
    for i in range(int(round(cr * 5))):
        a = (x0 + 60 + r.uniform(0, w - 160), y_top + 80 + r.uniform(0, L * .55))
        b = (a[0] + r.uniform(-90, 90), a[1] + r.uniform(40, 120))
        inner += line([a, ((a[0] + b[0]) / 2 + 20, (a[1] + b[1]) / 2), b], 4.0, sh, taper=.5, wmin=.2, seed=2010 + i)
    # отворот у верхнего края (простыня)
    turn = [(x0 - 6 * cr, y_top + 20 * cr, 1), (x1 + 10 * cr, y_top + 24 * cr, 1), (x1 + 10 * cr, y_top + 70, 1), (x0 - 6 * cr, y_top + 66, 1)]
    return shape(pts, col, inner, w=4.2, seed=2020 + seed) + shape(turn, "#f2ece0", "", w=3.4, seed=2021 + seed)


def bed_top(t, glow=0.0):
    """Спальня ночью сверху: пол, коврик, кровать с подушкой, тумбочка (часы/кружку ставит сцена), лунная полоса формы окна.
    dict(bg — всё до Димы; moon — лунная полоса (класть ПОСЛЕ одеяла — свет лежит поверх); quilt — функция одеяла)."""
    x, y, w, L = B_TOP_BED
    o = [f'<rect x="-1600" y="-1400" width="4800" height="5000" fill="#232a52"/>']
    for i in range(-10, 24):   # доски пола сверху — вертикальные полосы
        xx = i * 110.0
        o.append(line([(xx, -800), (xx, 2800)], 3.0, "#181d40", taper=0, wmin=1, seed=2100 + i, op=.8))
    r = rs(21)
    for j in range(30):
        xx = r.randint(-10, 24) * 110.0
        yy = r.uniform(-600, 2600)
        o.append(line([(xx, yy), (xx + 110, yy)], 2.6, "#181d40", taper=0, wmin=1, seed=2140 + j, op=.7))
    o.append(shape(lib.rrect(x - 420, y + 380, x + 420, y + 820, 40), "#4a3f6e", blob(lib.rrect(x - 360, y + 420, x + 360, y + 780, 30), "#5b4f82"), w=3.6, seed=2180))
    # рама кровати, изголовье сверху
    o.append(shape(lib.rrect(x - w / 2 - 30, y - L / 2 - 70, x + w / 2 + 30, y + L / 2 + 26, 16), WOOD, blob(rect_pts(x + w / 2, y - L / 2 - 70, x + w / 2 + 30, y + L / 2 + 26), WOOD_SH),
                   w=4.4, seed=2190))
    o.append(shape(rect_pts(x - w / 2 - 30, y - L / 2 - 70, x + w / 2 + 30, y - L / 2 - 20), WOOD_SH, "", w=3.6, seed=2191))
    o.append(shape(lib.rrect(x - w / 2, y - L / 2, x + w / 2, y + L / 2, 18), "#e9e2d2", blob(rect_pts(x + w / 2 - 30, y - L / 2, x + w / 2, y + L / 2), "#cfc6b2"), w=3.8, seed=2192))
    # подушка
    o.append(shape(lib.rrect(x - 200, y - L / 2 + 40, x + 200, y - L / 2 + 230, 50), "#f4ecdc",
                   blob(lib.rrect(x - 200, y - L / 2 + 180, x + 200, y - L / 2 + 230, 30), "#d9ccb2")
                   + line([(x - 120, y - L / 2 + 110), (x - 60, y - L / 2 + 140)], 3, "#d9ccb2", seed=2194), w=3.8, seed=2193))
    # тумбочка слева у изголовья (верх)
    sx, sy = B_TOP_STAND
    o.append(shape(lib.rrect(sx - 120, sy - 120, sx + 120, sy + 120, 10), WOOD, blob(rect_pts(sx + 90, sy - 120, sx + 120, sy + 120), WOOD_SH), w=4.0, seed=2195))
    o.append(shape(lib.rrect(sx - 100, sy - 100, sx + 100, sy + 100, 8), WOOD_HI, "", w=2.6, seed=2196))
    # лунная полоса формы окна (окно — за верхним краем кадра справа): чёткие края, по полу и кровати
    moon = _sun_quad((900, 360), (170, 30), (-40, 460), "#38447f", "#43508f", inset=.05)
    return dict(bg="".join(o), moon=moon)


# ═════════════════════════ СПАЛЬНЯ: ВИД СБОКУ ═════════════════════════
def bed_side(t, warm=1.0):
    """Спальня сбоку ночью: стена (тёплый свет ночника), окно с луной, тумбочка с лампой-ночником, кровать сбоку (изголовье слева).
    dict(bg — до Димы (кровать с подушкой, без одеяла), front — одеяло рисует сцена; light — круг ночника на стене)."""
    x, y, k = B_SIDE_BED
    o = []
    wall = lib.mix("#2c3466", "#7a5a6a", .35 * warm)
    g = lib.lin_grad([(0, lib.mix(wall, "#000000", .1), 1), (1, wall, 1)], 0, -400, 0, y, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="-1400" width="4800" height="{f(y + 1400)}" fill="url(#{g})"/>')
    o.append(f'<rect x="-1600" y="{f(y)}" width="4800" height="1400" fill="#3a2f44"/>')
    for kk, yy in enumerate((y + 40, y + 120, y + 240, y + 400)):
        o.append(line([(-1600, yy), (2800, yy)], 3.0, "#261e30", taper=0, wmin=1, seed=2200 + kk, op=.7))
    o.append(shape(rect_pts(-1600, y - 34, 2800, y + 6), lib.mix(wall, "#ffffff", .12), "", w=3.0, seed=2210))
    o.append(window(*B_SIDE_WIN, "night", t, seed=41, curtain="#5b4a7e"))
    # ночник на тумбочке: тёплый веер на стене с чёткими краями
    sx, sy = B_SIDE_STAND
    top = sy - 260
    if warm > 0.02:
        o.append(blob(ellipse_pts(sx, top + 2, 150, 22, 24), lib.mix(WOOD_HI, "#ffe7a3", .5 * warm)))
    o.append(shape(rect_pts(sx - 130, top, sx + 130, sy), WOOD, blob(rect_pts(sx + 96, top, sx + 130, sy), WOOD_SH)
                   + line([(sx - 110, top + 120), (sx + 90, top + 120)], 3, WOOD_SH, seed=2221), w=4.0, seed=2220))
    o.append(shape(lib.rrect(sx - 14, top + 50, sx + 14, top + 66, 5), "#c4ccd4", "", w=2.2, seed=2222))
    o.append(PR.lamp_desk(sx - 40, top, 1.15, on=warm, tilt=0, seed=6))
    o.append(PR.bed(x, y, k, seed=9))
    mt = y - 118 * k
    o.append(shape(lib.rrect(x - 255 * k, mt - 66 * k, x - 100 * k, mt + 4 * k, 26 * k), "#f2e6cf",
                   blob(rect_pts(x - 255 * k, mt - 16 * k, x - 100 * k, mt + 4 * k), "#d6c4a3"), w=3.6, seed=2230))
    return dict(bg="".join(o), front="")


def side_quilt(t, breath=0.0, crumple=0.0, seed=0, col="#c8553d", sh="#9a3b2b", body=None):
    """Одеяло на кровати сбоку (B_SIDE_BED): холм над телом (body — x центра холма), breath 0…1 — вдох поднимает холм."""
    x, y, k = B_SIDE_BED
    mt = y - 118 * k
    bx = x + 40 * k if body is None else body
    hh = (70 + 14 * breath) * k
    pts = [(x - 130 * k, mt + 8 * k, 1), (x - 120 * k, mt - 40 * k), (bx - 120 * k, mt - hh * .9), (bx, mt - hh - 10 * crumple * k), (bx + 140 * k, mt - hh * .7),
           (x + 270 * k, mt - 30 * k), (x + 292 * k, mt + 74 * k, 1), (x - 130 * k, mt + 74 * k, 1)]
    inner = blob(rect_pts(x - 140 * k, mt + 36 * k, x + 300 * k, mt + 76 * k), sh)
    inner += line([(bx - 60 * k, mt - hh * .6), (bx + 20 * k, mt + 10 * k)], 3.4 * k, sh, seed=2240 + seed)
    inner += line([(bx + 110 * k, mt - hh * .5), (bx + 160 * k, mt + 20 * k)], 3.4 * k, sh, seed=2241 + seed)
    return shape(pts, col, inner, w=4.0, seed=2242 + seed)


# ═════════════════════════ КУХОННЫЙ ПОЛ КРУПНО ═════════════════════════
def kitchen_floor(t, mode="morning"):
    """Низкая камера у пола кухни: нижние шкафы с цоколем, плинтус, доски пола в перспективе, пятно солнца формы окна.
    dict(bg, front) — front пуст (кот и предметы ставятся сценой на пол y ≥ KF_FLOOR+150)."""
    m = KMODE[mode]
    o = [f'<rect x="-1600" y="-1400" width="4800" height="5000" fill="{m["floor"]}"/>']
    # нижние шкафы: дверцы до KF_FLOOR − 70, цоколь до KF_FLOOR
    y0, y1 = -600.0, KF_FLOOR - 70
    for i, (x0, x1) in enumerate(((-600, -60), (-50, 490), (500, 1040), (1050, 1590))):
        inner = blob(rect_pts(x1 - 40, y0, x1, y1), m["cab_sh"]) + blob(rect_pts(x0 + 22, y0, x0 + 36, y1 - 22), m["cab_hi"])
        inner += shape(rect_pts(x0 + 70, y0 + 60, x1 - 70, y1 - 70), lib.mix(m["cab"], m["cab_sh"], .3), "", w=3.0, seed=2300 + i)
        o.append(shape(rect_pts(x0, y0, x1, y1), m["cab"], inner, w=4.4, seed=2310 + i))
        o.append(shape(lib.rrect(x0 + 120, y0 + 680, x0 + 220, y0 + 704, 8), "#c4ccd4", "", w=2.8, seed=2320 + i))
    o.append(shape(rect_pts(-1600, y1, 2800, KF_FLOOR), lib.mul(m["cab_sh"], (.72, .72, .72)), "", w=3.6, seed=2330))
    # пол в перспективе: линии досок сходятся к точке схода над кадром
    vx, vy = 540.0, -900.0
    for i in range(-12, 14):
        xb = 540 + i * 210.0
        xa = vx + (xb - vx) * (KF_FLOOR - vy) / (2400 - vy)
        o.append(line([(xa, KF_FLOOR), (xb, 2400)], 3.2, m["floor_ln"], taper=0, wmin=1, seed=2340 + i, op=.6))
    for j, yy in enumerate((KF_FLOOR + 90, KF_FLOOR + 230, KF_FLOOR + 430, KF_FLOOR + 720)):
        o.append(line([(-1600, yy), (2800, yy)], 2.6, m["floor_ln"], taper=0, wmin=1, seed=2370 + j, op=.35))
    if m["sun"]:
        u = .55 if mode == "sunny" else .35
        o.append(_sun_quad((140, 1180), (560, 0), (-160, 420), lib.mix(m["floor"], m["sun"], u), lib.mix(m["floor"], "#fff8e0", u + .15), inset=.08))
    return dict(bg="".join(o), front="")
