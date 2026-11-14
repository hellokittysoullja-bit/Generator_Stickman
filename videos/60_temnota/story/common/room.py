"""Комната взрослого Димы вечером (рилс 60, группы E и F): стена с обоями, пол, ковёр, кресло, торшер с дугой, столик с кружкой,
большое окно с далью (холмы, облака, горизонт, первые звёзды), шторы, подоконник с растением.

Один вид для всех клипов: подключение  sys.path.insert(0, COMMON); import room   (COMMON = videos/60_temnota/story/common; lib/ink рядом).
Мир — 1080×1920, камера накладывается снаружи (lib.cam). Единицы: Дима сидит в кресле при BS≈0.8 (таз в точке SEAT), ноги на полу FL.
Все функции возвращают строку SVG (мировые координаты); динамические defs (градиенты) создаются при каждом вызове — вызывать между lib.dyn_begin().

    FL=1440 (пол под ногами), WALL_Y=1330 (низ стены), WIN=(590,340,1030,1090) окно, SILL_Y=1100, HORIZON=790 (горизонт за окном, мир)
    SEAT=(330,1130) таз сидящего Димы, CHAIR_X, LAMP_X, LAMP_SHADE=(340,470)
    wall_floor()                          стена, плинтус, пол, ковёр (статика)
    window_view(t, par=0.0, zoom=1.0)     даль за стеклом (без рамы): par 0…1 — «вглубь»: дальние слои идут к зрителю слабее, ближние сильнее
    window_frame(t, curtains=True, plant=True)  рама со стёклами (блики), переплёт, подоконник, шторы, растение на подоконнике
    window(t, par=0.0, ...)               view + frame одним вызовом
    armchair(k=1.0)                       dict(back, seat, arm) — кресло в мире с точкой таза в SEAT (порядок: back, seat, [legs, body Димы], arm, [arm_n])
    floor_lamp(on=1.0)                    торшер: (стойка и абажур, свет-конус, пятно света на стене/полу/кресле) → dict(lamp, cone, pool)
    bloom(u)                              «тёплый круг» на слове: расходящееся кольцо света вокруг абажура, u 0…1
    side_table(t)                         столик с кружкой и паром (справа, у окна)
    room_static(t)                        wall_floor + side_table + кресло-back не входят: только фон (стена, пол, ковёр, окно-блоки собираются в клипе)
    gaze_dots(a, b, u, t)                 пунктир взгляда: точки от a к b, u 0…1 — сколько пути пройдено (круглые точки с лёгкой обводкой)
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
from lib import INK, blob, ellipse_pts, f, line, mix, rect_pts, shape  # noqa: E402
from ink import band  # noqa: E402

FL = 1440.0
WALL_Y = 1330.0
WIN = (590.0, 340.0, 1030.0, 1090.0)
SILL_Y = 1100.0
HORIZON = 790.0
SEAT = (330.0, 1130.0)
CHAIR_X = 330.0
LAMP_X = 96.0
LAMP_SHADE = (342.0, 470.0)

WALL_TOP, WALL_MID, WALL_BOT = "#6f6788", "#a08f86", "#c5ab8b"
FLOOR_C, FLOOR_SH, FLOOR_LN = "#8e6040", "#6d4529", "#4e301b"
BASE_C = "#e8dcc4"
CHAIR, CHAIR_SH, CHAIR_HI, CHAIR_DK = "#3f7075", "#2d5559", "#5f9296", "#234246"
WOOD, WOOD_SH, WOOD_HI = "#a8693f", "#7f4b2b", "#c88a58"
SHADE, SHADE_SH, SHADE_HI = "#f0cf8e", "#cba35c", "#fbe8bb"


def rs(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


# ═════════════════════════ стена и пол ═════════════════════════
def wall_floor():
    o = []
    g = lib.lin_grad([(0, WALL_TOP, 1), (.55, WALL_MID, 1), (1, WALL_BOT, 1)], 0, 0, 0, WALL_Y, units="userSpaceOnUse")
    o.append(f'<rect x="-400" y="-300" width="1900" height="{f(WALL_Y + 300)}" fill="url(#{g})"/>')
    # обои: широкие чуть светлее полосы и тонкие линии швов
    for i in range(-8, 24):
        x = i * 96.0
        if i % 2 == 0:
            o.append(f'<rect x="{f(x)}" y="-300" width="96" height="{f(WALL_Y + 300)}" fill="#ffffff" opacity=".045"/>')
        o.append(line([(x, -300), (x + 1.5, WALL_Y)], w=1.8, color="#4d4258", taper=0.0, wmin=1, seed=40 + i, op=.16))
    # плинтус
    o.append(shape(rect_pts(-400, WALL_Y - 40, 1500, WALL_Y + 6), BASE_C, blob(rect_pts(-400, WALL_Y - 4, 1500, WALL_Y + 6), "#c9bb9e"), w=3.4, seed=70))
    # пол
    gf = lib.lin_grad([(0, "#7d5236", 1), (1, "#a16f49", 1)], 0, WALL_Y, 0, 1920, units="userSpaceOnUse")
    o.append(f'<rect x="-400" y="{f(WALL_Y + 6)}" width="1900" height="{f(1920 - WALL_Y)}" fill="url(#{gf})"/>')
    ys = [WALL_Y + 6, 1388, 1458, 1540, 1636, 1750, 1880]
    for k, y in enumerate(ys[1:]):
        o.append(line([(-400, y), (1500, y)], w=3.2, color=FLOOR_LN, taper=0.0, wmin=1, seed=80 + k, op=.7))
    r = rs(5)
    for k, (ya, yb) in enumerate(zip(ys[:-1], ys[1:])):
        for j in range(5):
            x = r.uniform(-300, 1380)
            o.append(line([(x, ya), (x + r.uniform(-4, 4), yb)], w=2.6, color=FLOOR_LN, taper=0.0, wmin=1, seed=90 + k * 7 + j, op=.55))
    # ковёр под креслом: бирюзово-горчичный овал с полосами
    cx, cy, rx, ry = 380.0, 1600.0, 470.0, 118.0
    o.append(blob(ellipse_pts(cx + 8, cy + 14, rx + 4, ry + 4, 30), "#3e2a1a", .35))
    inner = ""
    for k, (sc, col) in enumerate(((.82, "#d9a94a"), (.66, "#4a8a86"), (.5, "#d9a94a"), (.34, "#8b4a55"))):
        inner += shape(ellipse_pts(cx, cy, rx * sc, ry * sc, 26), col, ink=False)
    o.append(shape(ellipse_pts(cx, cy, rx, ry, 34), "#5a8f8a", inner, w=4.0, seed=120))
    return "".join(o)


# ═════════════════════════ окно и даль ═════════════════════════
def _hills(x0, x1, base, amp, ph, sd, n=14):
    r = rs(sd)
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = base + amp * (math.sin(i * .9 + ph) * .6 + math.sin(i * 2.1 + ph * 1.7) * .25) + r.uniform(-amp * .08, amp * .08)
        pts.append((x, y))
    return pts + [(x1 + 60, 1300, 1), (x0 - 60, 1300, 1)]


def _cloud(x, y, s, col, shade):
    o = blob(ellipse_pts(x, y, 110 * s, 24 * s, 16), shade)
    for dx, dy, rx, ry in ((-70, -4, 58, 26), (-8, -22, 70, 38), (62, -8, 62, 28), (118, 4, 40, 18), (-120, 6, 34, 16)):
        o += blob(ellipse_pts(x + dx * s, y + dy * s - 8 * s, rx * s, ry * s, 14), col)
    o += blob(ellipse_pts(x - 4 * s, y + 8 * s, 118 * s, 14 * s, 14), shade, .55)
    return o


def window_view(t, par=0.0, zoom=1.0):
    """Даль: вечернее небо, облака, три слоя холмов, дальний лес и дом с огоньком, птицы, звёзды.
    par 0…1 — вглубь: слои расходятся от точки горизонта (ближние растут быстрее, дальние почти стоят)."""
    x0, y0, x1, y1 = WIN
    cx, cy = (x0 + x1) / 2, HORIZON
    clip = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o = []

    def L(depth, inner):
        """слой глубины depth (0 — небо, 1 — ближний) увеличивается вокруг (cx, cy) на 1 + par·depth·0.9"""
        s = 1 + par * depth * 0.9
        return f'<g transform="translate({f(cx * (1 - s))} {f(cy * (1 - s))}) scale({s:.4f})">{inner}</g>'

    g = lib.lin_grad([(0, "#1f2b66", 1), (.32, "#46509a", 1), (.6, "#9a86be", 1), (.8, "#f0a894", 1), (1, "#ffd8a0", 1)], 0, y0 - 60, 0, HORIZON + 30,
                     units="userSpaceOnUse")
    sky = f'<rect x="{f(x0 - 300)}" y="{f(y0 - 300)}" width="{f(x1 - x0 + 600)}" height="{f(HORIZON + 330 - y0)}" fill="url(#{g})"/>'
    # звёзды
    r = rs(9)
    st = ""
    for i in range(16):
        sx, sy = r.uniform(x0 - 40, x1 + 40), r.uniform(y0 - 20, y0 + 200)
        tw = .6 + .4 * math.sin(t * 2.2 + i * 1.7)
        st += f'<circle cx="{f(sx)}" cy="{f(sy)}" r="{f(1.6 + 1.6 * r.uniform())}" fill="#fff6dc" opacity="{tw:.2f}"/>'
    st += f'<circle cx="{f(x0 + 330)}" cy="{f(y0 + 150)}" r="5" fill="#fff4d0"/>'
    o.append(L(0.0, sky + st))
    # облака плывут медленно
    cl = ""
    for k, (bx, by, s, sp) in enumerate(((x0 + 60, y0 + 250, 1.35, 9), (x0 + 330, y0 + 360, 1.0, 6), (x0 + 120, y0 + 450, .8, 4), (x0 + 420, y0 + 170, .7, 8))):
        xx = x0 - 180 + ((bx - x0 + 180 + sp * t) % (x1 - x0 + 360))
        cl += _cloud(xx, by, s, "#f7d6c8" if by > y0 + 300 else "#c9b6dc", "#d9a8b4" if by > y0 + 300 else "#9d8fc4")
    o.append(L(0.18, cl))
    # дальние горы (дымка), потом холмы
    far = shape(_hills(x0 - 200, x1 + 200, HORIZON - 10, 36, 1.0, 11), "#8d86bd", ink=False)
    o.append(L(0.32, far))
    # дальний лес и дом с огоньком на гребне
    r2 = rs(14)
    forest = ""
    for i in range(26):
        tx = x0 - 40 + i * 20 + r2.uniform(-6, 6)
        forest += blob(ellipse_pts(tx, HORIZON - 4 + r2.uniform(-5, 3), r2.uniform(11, 17), r2.uniform(16, 24), 8), "#6b6aa8")
    forest += blob(rect_pts(x0 + 270, HORIZON - 26, x0 + 300, HORIZON - 2), "#5a5894")
    forest += blob([(x0 + 266, HORIZON - 26), (x0 + 285, HORIZON - 42), (x0 + 304, HORIZON - 26)], "#4c4a82")
    forest += blob(rect_pts(x0 + 281, HORIZON - 20, x0 + 291, HORIZON - 10), "#ffd36a")
    o.append(L(0.4, forest))
    mid = shape(_hills(x0 - 200, x1 + 200, HORIZON + 40, 44, 2.4, 12), "#5d6aa6", blob(rect_pts(x0 - 200, HORIZON + 130, x1 + 200, HORIZON + 300), "#4d5a96"), w=2.4, seed=140, ink=False)
    o.append(L(0.55, mid))
    near = shape(_hills(x0 - 220, x1 + 220, HORIZON + 110, 56, 4.0, 13), "#3f4a86",
                 blob(rect_pts(x0 - 220, HORIZON + 200, x1 + 220, HORIZON + 420), "#333d72"), w=2.6, seed=141)
    # озеро в ложбине: светлая лента
    lake = blob([(x0 + 150, HORIZON + 126), (x0 + 260, HORIZON + 118), (x0 + 330, HORIZON + 128), (x0 + 240, HORIZON + 140)], "#f0b79a")
    o.append(L(0.7, near + lake))
    # ближний склон с деревьями
    fg = shape(_hills(x0 - 240, x1 + 240, HORIZON + 230, 40, 5.5, 15), "#2a3260", blob(rect_pts(x0 - 240, HORIZON + 330, x1 + 240, HORIZON + 600), "#212852"),
               w=2.8, seed=142)
    for i, (tx, ty, ts) in enumerate(((x0 + 70, HORIZON + 240, 1.0), (x0 + 360, HORIZON + 250, 1.25), (x0 + 400, HORIZON + 236, .85))):
        fg += blob(rect_pts(tx - 4 * ts, ty - 30 * ts, tx + 4 * ts, ty + 6), "#1b2146")
        fg += shape(ellipse_pts(tx, ty - 62 * ts, 38 * ts, 46 * ts, 12, jitter=.07, seed=60 + i), "#1f2858", ink=False)
    o.append(L(0.95, fg))
    # птицы летят к горизонту
    bd = ""
    for k in range(4):
        u = (t * .08 + k * .21) % 1.0
        bx = x0 + 60 + (x1 - x0 - 120) * u + 20 * k
        by = HORIZON - 190 - 60 * u + 26 * k
        w = 12 * math.sin(t * 9 + k * 2)
        bd += line([(bx - 20, by - w), (bx, by + 5), (bx + 20, by - w)], w=3.0, color="#2a2d5c", taper=.5, seed=150 + k)
    o.append(L(0.45, bd))
    # тёплая дымка у горизонта
    gh = lib.rad_grad([(0, "#ffd9a8", .55), (1, "#ffd9a8", 0)], cx, HORIZON + 6, 340, 70)
    o.append(f'<ellipse cx="{f(cx)}" cy="{f(HORIZON + 6)}" rx="340" ry="70" fill="url(#{gh})"/>')
    return f'<g clip-path="url(#{clip})">{"".join(o)}</g>'


def window_frame(t, curtains=True, plant=True):
    x0, y0, x1, y1 = WIN
    o = []
    fw = 30
    outer = [(x0 - fw, y0 - fw, 1), (x1 + fw, y0 - fw, 1), (x1 + fw, y1 + fw, 1), (x0 - fw, y1 + fw, 1)]
    hole = f"M{x0} {y0}H{x1}V{y1}H{x0}Z"
    o.append(f'<path d="{lib.fill_d(outer)}{hole}" fill="#efe6d2" fill-rule="evenodd"/>')
    o.append(f'<path d="{lib.ink_closed(outer, 4.6 * lib.INK_K[0], seed=980)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed([(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)], 3.8 * lib.INK_K[0], seed=981)}" fill="{INK}"/>')
    o.append(blob([(x1, y0 - fw), (x1 + fw, y0 - fw), (x1 + fw, y1 + fw), (x1, y1)], "#cdbfa5"))
    mx, my = (x0 + x1) / 2, y0 + (y1 - y0) * .44
    for pts, sd in (([(mx - 8, y0), (mx + 8, y0), (mx + 8, y1), (mx - 8, y1)], 982), ([(x0, my - 8), (x1, my - 8), (x1, my + 8), (x0, my + 8)], 983)):
        o.append(shape([p + (1,) for p in pts], "#efe6d2", w=3.2, seed=sd))
    for k, (a, b) in enumerate([((x0 + 36, y0 + 190), (x0 + 150, y0 + 40)), ((x0 + 60, y0 + 270), (x0 + 210, y0 + 80)), ((mx + 50, y1 - 70), (mx + 170, y1 - 250))]):
        o.append(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="#ffffff" stroke-opacity=".13" stroke-width="{16 - k * 3}" stroke-linecap="round"/>')
    # подоконник
    sill = [(x0 - 64, y1 + 18, 1), (x1 + 64, y1 + 18, 1), (x1 + 56, y1 + 54, 1), (x0 - 56, y1 + 54, 1)]
    o.append(shape(sill, "#f3ead6", blob(rect_pts(x0 - 64, y1 + 40, x1 + 64, y1 + 56), "#cdbfa5"), w=4.2, seed=985))
    if plant:
        o.append(pot_plant(x0 + 56, y1 + 18, 1.0, t))
    if curtains:
        o.append(curtain(x0 - 30, y0 - 70, 96, y1 + 40, 1))
        o.append(curtain(x1 + 30, y0 - 70, 96, y1 + 40, -1))
    return "".join(o)


def curtain(x, y, w, h, side):
    """Штора у края окна: сборки-складки светлым и тёмным, ленточка-подхват."""
    o = []
    x_a, x_b = (x - w, x + 6) if side > 0 else (x - 6, x + w)
    pts = [(x_a, y, 1), (x_b, y, 1), (x_b - side * 10, y + h * .5), (x_b - side * 26, y + h, 1), (x_a, y + h + 30, 1)]
    inner = ""
    for k in range(4):
        fx = x_a + (x_b - x_a) * (k + .5) / 4
        inner += blob([(fx - 7, y), (fx + 7, y), (fx + 12 + side * 4, y + h), (fx - 6 + side * 4, y + h)], "#e3b46a", .85)
        inner += line([(fx, y), (fx + side * 4, y + h * .5), (fx + side * 6, y + h + 20)], w=3.0, color="#8d6420", taper=.7, seed=170 + k, op=.55)
    o.append(shape(pts, "#f0c880", inner, w=4.2, seed=171 if side > 0 else 172))
    band_y = y + h * .6
    o.append(shape(rect_pts(x_a - 2, band_y, x_b + 2, band_y + 18, 5), "#c0583f", w=3.0, seed=173))
    return "".join(o)


def pot_plant(x, y, k, t):
    r = rs(31)
    o = []
    for i in range(9):
        a = math.radians(-90 + (i - 4) * 19) + .06 * math.sin(t * .9 + i)
        L_ = (96 + 34 * r.uniform()) * k
        tip = (x + L_ * math.cos(a), y - 40 * k + L_ * math.sin(a))
        mid = (x + L_ * .5 * math.cos(a) - 8 * (i - 4) * .3, y - 40 * k + L_ * .5 * math.sin(a))
        o.append(shape(band([(x, y - 40 * k), mid, tip], 16 * k, 3, step=6), "#5fa05b" if i % 2 else "#4a8a52", w=2.6, seed=180 + i))
    o.append(shape([(x - 34 * k, y - 50 * k, 1), (x + 34 * k, y - 50 * k, 1), (x + 26 * k, y, 1), (x - 26 * k, y, 1)], "#c96b4a",
                   blob([(x + 10 * k, y - 50 * k), (x + 34 * k, y - 50 * k), (x + 26 * k, y), (x + 8 * k, y)], "#a54e32", .9), w=3.4, seed=190))
    return "".join(o)


# ═════════════════════════ кресло, торшер, столик ═════════════════════════
def armchair(k=1.0):
    """Кресло лицом вправо; таз сидящего — SEAT. Слои: back (спинка и ножки), seat (подушка), arm (ближний подлокотник, поверх бедра)."""
    sx, sy = SEAT

    def T_(pts):
        return [(sx + (p[0]) * k, sy + (p[1]) * k) + ((1,) if len(p) > 2 else ()) for p in pts]

    back_pts = T_([(-170, 30, 1), (-250, -70), (-292, -250), (-268, -470, 1), (-96, -470, 1), (-70, -250), (-70, 30, 1)])
    # спинка с наклоном: верх левее низа
    back_in = blob(T_([(-250, -70), (-292, -250), (-268, -470), (-228, -470), (-246, -250), (-206, -70)]), CHAIR_SH, .9)
    back = shape(back_pts, CHAIR, back_in, w=4.6, seed=200)
    wings = shape(T_([(-270, -250, 1), (-96, -250, 1), (-70, -230, 1), (-70, 10, 1), (-180, 10, 1), (-250, -40)]), CHAIR_HI,
                  blob(T_([(-96, -250), (-70, -230), (-70, 10), (-96, 10)]), CHAIR, .9), w=3.4, seed=201)
    legs = ""
    for lx, sd in ((-230, 210), (120, 211)):
        legs += shape(T_([(lx - 16, 120, 1), (lx + 16, 120, 1), (lx + 9, 262, 1), (lx - 9, 262, 1)]), WOOD, blob(T_([(lx + 4, 120), (lx + 16, 120), (lx + 9, 262), (lx + 2, 262)]), WOOD_SH, .8),
                       w=3.2, seed=sd)
    base = shape(T_([(-252, 40, 1), (170, 40, 1), (178, 124, 1), (-244, 124, 1)]), CHAIR_SH, w=4.2, seed=212)
    seat = shape(T_([(-190, -8, 1), (150, -22), (196, 24, 1), (176, 58, 1), (-196, 58, 1), (-214, 24, 1)]), CHAIR_HI,
                 blob(T_([(-190, 30), (196, 24), (176, 58), (-196, 58)]), CHAIR, .9), w=4.4, seed=213)
    arm = shape(T_([(-210, -46, 1), (150, -66), (190, -40, 1), (190, 30, 1), (-210, 30, 1)]), CHAIR, blob(T_([(-210, 6), (190, 4), (190, 30), (-210, 30)]), CHAIR_SH, .9) +
                blob(T_([(-200, -40), (140, -58), (150, -48), (-200, -28)]), CHAIR_HI, .9), w=4.4, seed=214)
    return dict(back=legs + base + back + wings, seat=seat, arm=arm)


def floor_lamp(on=1.0, flick=0.0):
    """Торшер с дугой: стойка у левой стены, дуга вправо, абажур висит над креслом. on 0…1 — яркость (0 — выключен).
    Возвращает dict(lamp=..., pool=..., cone=...): pool рисовать ДО фигур (свет на стене/ковре), cone — после, lamp — поверх."""
    sx, sy = LAMP_SHADE
    o = []
    # основание и стойка
    o.append(blob(ellipse_pts(LAMP_X + 4, 1428, 104, 22, 16), "#2b1d12", .35))
    o.append(shape(ellipse_pts(LAMP_X, 1418, 84, 18, 18), "#3a3d46", blob(ellipse_pts(LAMP_X + 14, 1424, 66, 12, 12), "#2a2c34", .9), w=4.0, seed=300))
    pts = [(LAMP_X, 1412), (LAMP_X, 900), (LAMP_X, 560), (LAMP_X + 10, 440), (LAMP_X + 70, 372), (LAMP_X + 160, 352), (sx - 40, 366), (sx - 6, 392), (sx, 410)]
    o.append(shape(band(pts, 18, 9, step=6, cap=False), "#8a8d96", blob([(LAMP_X + 4, 1412)], "#8a8d96"), w=3.4, seed=301))
    glow = on
    # абажур
    top_w, bot_w, hh = 54, 138, 112
    pts_s = [(sx - top_w, sy - 4, 1), (sx + top_w, sy - 4, 1), (sx + bot_w, sy + hh, 1), (sx - bot_w, sy + hh, 1)]
    col = lib.mix("#d6b072", SHADE, .3 + .7 * glow)
    shade_ = shape(pts_s, col, blob([(sx + 20, sy - 4), (sx + top_w, sy - 4), (sx + bot_w, sy + hh), (sx + 60, sy + hh)], SHADE_SH, .85) +
                   blob([(sx - top_w + 8, sy - 4), (sx - 20, sy - 4), (sx - 70, sy + hh), (sx - bot_w + 6, sy + hh)], SHADE_HI, .8 * glow), w=4.4, seed=302)
    bulb = ""
    if glow > .02:
        bulb = blob(ellipse_pts(sx, sy + hh - 2, bot_w - 10, 12, 16), "#fff3c8")
    o.append(shade_ + bulb)
    lamp = "".join(o)
    pool = cone = ""
    if glow > .02:
        a = glow * (1 - .06 * flick)
        # пятно на стене: тёплый эллипс вокруг абажура
        gp = lib.rad_grad([(0, "#ffd68a", .55 * a), (.5, "#ffc274", .24 * a), (1, "#ffb060", 0)], sx, sy + 120, 420, 360)
        pool += f'<ellipse cx="{f(sx)}" cy="{f(sy + 120)}" rx="420" ry="360" fill="url(#{gp})"/>'
        # пятно света на полу и ковре под креслом
        gf = lib.rad_grad([(0, "#ffd68a", .5 * a), (1, "#ffb060", 0)], sx + 40, 1560, 360, 90)
        pool += f'<ellipse cx="{f(sx + 40)}" cy="1560" rx="360" ry="90" fill="url(#{gf})"/>'
        # конус света вниз от абажура
        gc = lib.lin_grad([(0, "#ffe2a0", .5 * a), (1, "#ffd08a", .06 * a)], 0, sy + hh, 0, 1380, units="userSpaceOnUse")
        cone = f'<path d="M{f(sx - bot_w + 10)} {f(sy + hh)}L{f(sx + bot_w - 10)} {f(sy + hh)}L{f(sx + 330)} 1390L{f(sx - 250)} 1390Z" fill="url(#{gc})"/>'
    return dict(lamp=lamp, pool=pool, cone=cone)


def bloom(u, cx=None, cy=None, R=520.0):
    """«Тёплый круг света» на слове: светлый диск растёт от абажура с мягким краем и кольцом, потом оседает."""
    if not 0 < u < 1.3:
        return ""
    sx, sy = LAMP_SHADE
    cx = sx if cx is None else cx
    cy = sy + 150 if cy is None else cy
    e = 1 - (1 - min(1.0, u)) ** 3
    a = max(0.0, 1 - max(0.0, u - .55) / .75)
    r = R * (.25 + .75 * e)
    g = lib.rad_grad([(0, "#fff0b8", .65 * a), (.55, "#ffd070", .35 * a), (1, "#ffc060", 0)], cx, cy, r)
    o = f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="url(#{g})"/>'
    o += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .86)}" fill="none" stroke="#fff3c4" stroke-width="{f(10 * a + .1)}" opacity="{.7 * a:.2f}"/>'
    return o


def side_table(t, x=700.0):
    """Круглый столик у окна: ножка, столешница, кружка с паром, закрытая книга-стопка (без букв)."""
    y = FL - 6
    top = y - 250
    o = [blob(ellipse_pts(x + 6, y + 8, 78, 13, 14), "#2b1d12", .35)]
    o.append(shape([(x - 12, top + 14, 1), (x + 12, top + 14, 1), (x + 8, y - 12, 1), (x - 8, y - 12, 1)], WOOD, w=3.4, seed=400))
    o.append(shape(ellipse_pts(x, y - 8, 58, 12, 16), WOOD_SH, w=3.4, seed=401))
    o.append(shape(ellipse_pts(x, top + 8, 84, 16, 20), WOOD_HI, blob(ellipse_pts(x + 20, top + 12, 62, 10, 14), WOOD, .8), w=4.2, seed=402))
    o.append(shape(rect_pts(x - 86, top + 6, x + 86, top + 26, 5), WOOD, blob(rect_pts(x - 86, top + 18, x + 86, top + 26), WOOD_SH), w=3.4, seed=403))
    # кружка
    mx, my = x + 20, top + 4
    o.append(shape([(mx - 28, my - 54, 1), (mx + 28, my - 54, 1), (mx + 24, my, 1), (mx - 24, my, 1)], "#e9eef2", blob([(mx + 8, my - 54), (mx + 28, my - 54), (mx + 24, my), (mx + 6, my)], "#b9c6d0", .9), w=3.4, seed=404))
    o.append(shape(band([(mx + 28, my - 42), (mx + 52, my - 38), (mx + 46, my - 14), (mx + 26, my - 12)], 8, 8, step=5, cap=False), "#e9eef2", w=3.0, seed=405))
    o.append(blob(ellipse_pts(mx, my - 54, 28, 6, 12), "#8a4a2a"))
    for k in range(3):
        ph = (t * .5 + k * .33) % 1.0
        sxp = mx - 8 + 8 * k + 10 * math.sin(ph * 6 + k)
        o.append(line([(mx - 8 + 8 * k, my - 62), (sxp, my - 100 - 60 * ph), (sxp + 8 * math.sin(ph * 5), my - 130 - 100 * ph)], w=4.0, color="#f2e8dc", taper=.8, seed=410 + k, op=.7 * (1 - ph)))
    # две закрытые книги слева на столе (без букв)
    o.append(shape(rect_pts(x - 70, top - 28, x - 6, top + 4, 3), "#8c5a9a", blob(rect_pts(x - 70, top - 4, x - 6, top + 4), "#f3ead4"), w=3.0, seed=420))
    return "".join(o)


def gaze_dots(a, b, u, t, curve=0.0, n=14, r0=10.0):
    """Пунктир взгляда от a к b: n круглых точек, u 0…1 — сколько пути пройдено (точки зажигаются по порядку, голова светится)."""
    ax, ay = a
    bx, by = b
    o = []
    for i in range(n):
        s = (i + .5) / n
        if s > u + .02:
            break
        px = ax + (bx - ax) * s + curve * math.sin(math.pi * s)
        py = ay + (by - ay) * s - abs(curve) * .5 * math.sin(math.pi * s)
        age = clampf((u - s) * 6)
        rr = r0 * (.55 + .45 * s ** .6) * (.6 + .4 * age) * (1 + .1 * math.sin(t * 9 + i))
        o.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(rr + 2.2)}" fill="{INK}"/><circle cx="{f(px)}" cy="{f(py)}" r="{f(rr)}" fill="#fff2b4"/>')
    return "".join(o)


def clampf(x):
    return max(0.0, min(1.0, x))


def room_static():
    """Стена, пол, ковёр, окно в раме (без шторы-движения): статичный фон; свет и фигуры — поверх."""
    return wall_floor()
