"""Сцена diaries (s10, s11).
s10: старое кирпичное университетское здание (белый портик, башенка, два красных флажка; без букв и гербов). Из
открытых окон вылетают дневники и падают в огромную стопку справа; над стопкой табло-счётчик крутится барабаном и
встаёт на «12 000» к «тысяч» (17.6).
s11: крупно раскрытые дневники на столе листаются, на страницах простые рисунки дней (человечек за столом, кружка,
маленький график…), без букв; камера едет вбок."""
import math

import numpy as np

import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, fill_d,
                 line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg)

STOP = 17.6
_ST = {}

BRICK, BRICK_SH, BRICK_DK, TRIM = "#b4523a", "#8f3c2b", "#6e2c20", "#f3ede1"
COVERS = ["#2f6db5", "#3f9a5c", "#c94a3f", "#d9a338", "#7a4fb0", "#2b8f97", "#e07a3a", "#4a5a8c"]

# ═══════════════════════════════ s10
GX0, GX1, GTOP, GBASE = 30, 650, 560, 1080       # фасад
WIN_ROWS = [(640, 740), (820, 920)]
WIN_X = [80, 175, 485, 580]
PX0, PX1 = 268, 412                               # портик
STX, SBASE, LH = 845, 1290, 17.0                  # стопка: центр, низ, толщина одного дневника
N0 = 14


def sky():
    s = []
    lin_grad([(0, "#7fb6e8", 1), (.6, "#b9dcf5", 1), (1, "#e6f2fa", 1)], 0, 0, 0, 1, gid="gSky")
    s.append(f'<rect x="-400" y="-400" width="{W + 800}" height="{GBASE + 500}" fill="url(#gSky)"/>')
    # дальние деревья за зданием
    rs = np.random.RandomState(3)
    for k in range(16):
        x = -60 + k * 80 + rs.uniform(-20, 20)
        r = rs.uniform(70, 110)
        y = GBASE - 40 - rs.uniform(0, 60)
        col = "#5f9a5a" if k % 2 else "#4f8a4e"
        s.append(shape(ellipse_pts(x, y, r, r * .85, 14, jitter=.08, seed=k), col,
                       blob(ellipse_pts(x + r * .25, y + r * .3, r * .8, r * .55, 12), "#3f7440", .8), w=4, seed=500 + k))
    return "".join(s)


def lawn():
    s = []
    lin_grad([(0, "#7cbf5e", 1), (1, "#5aa147", 1)], 0, 0, 0, 1, gid="gLawn")
    s.append(f'<rect x="-400" y="{GBASE - 6}" width="{W + 800}" height="{H}" fill="url(#gLawn)"/>')
    s.append(line([(-300, GBASE - 6), (W + 300, GBASE - 6)], 4, INK, taper=.1, wmin=.8, seed=9))
    # дорожка к порталу
    path = [(PX0 + 30, GBASE), (PX1 - 30, GBASE), (PX1 + 140, H + 300, 1), (PX0 - 140, H + 300, 1)]
    s.append(shape(path, "#e6d6b6", blob([(PX1 - 10, GBASE), (PX1 + 140, H + 300), (PX1 + 60, H + 300), (PX1 - 30, GBASE)], "#cdb894", .9), w=4, seed=12))
    # кустики вдоль фасада
    for k, x in enumerate([60, 150, 230, 450, 540, 620]):
        s.append(shape(ellipse_pts(x, GBASE + 10, 52, 34, 12, jitter=.1, seed=k), "#4d8f45",
                       blob(ellipse_pts(x + 14, GBASE + 22, 40, 20, 10), "#36703a", .9) + blob(ellipse_pts(x - 16, GBASE - 2, 16, 8, 8), "#8fcf72", .8),
                       w=4, seed=520 + k))
    # травинки
    rs = np.random.RandomState(5)
    for k in range(70):
        x, y = rs.uniform(-60, W + 60), rs.uniform(GBASE + 60, 1800)
        if PX0 - 160 < x < PX1 + 160 and y > GBASE:
            continue
        s.append(line([(x, y), (x + rs.uniform(-5, 5), y - rs.uniform(12, 22))], 3, "#3f7a36", taper=.6, seed=600 + k, op=.8))
    return "".join(s)


def brick_defs():
    DEFS.append(f'<pattern id="pBrick" width="64" height="32" patternUnits="userSpaceOnUse">'
                f'<rect width="64" height="32" fill="{BRICK}"/>'
                f'<path d="M0 15.5H64M0 31.5H64M20 0V15.5M52 16V32" stroke="{BRICK_SH}" stroke-width="2.4"/>'
                f'<rect x="4" y="3" width="12" height="4" fill="#c66a4f" opacity=".7"/><rect x="36" y="19" width="10" height="4" fill="#c66a4f" opacity=".6"/>'
                f'</pattern>')


def window(x, y0, y1, open_=False, seed=0):
    w = 62
    s = []
    fr = rect_pts(x - w / 2 - 8, y0 - 8, x + w / 2 + 8, y1 + 8)
    s.append(shape(fr, TRIM, "", w=3.6, seed=seed))
    glass = rect_pts(x - w / 2, y0, x + w / 2, y1)
    if open_:
        inner = blob(rect_pts(x - w / 2, y0, x + w / 2, y1), "#2a2238") + blob(rect_pts(x - w / 2, y0, x + w / 2, y0 + 30), "#43354f")
        s.append(shape(glass, "#2a2238", inner, w=3.2, seed=seed + 1))
        # распахнутая створка
        s.append(shape([(x + w / 2, y0, 1), (x + w / 2 + 26, y0 + 10, 1), (x + w / 2 + 26, y1 - 6, 1), (x + w / 2, y1, 1)], "#9cc7ec",
                       line([(x + w / 2 + 8, y0 + 18), (x + w / 2 + 8, y1 - 18)], 4, "#ffffff", seed=seed + 3, op=.7), w=3, seed=seed + 2))
    else:
        inner = blob(rect_pts(x - w / 2, y0, x + w / 2, y1), "#7fa9d8") + \
            blob([(x - w / 2, y0 + 40), (x + w / 2, y0 + 8), (x + w / 2, y0 + 30), (x - w / 2, y0 + 62)], "#c9e2f7", .8)
        s.append(shape(glass, "#7fa9d8", inner, w=3.2, seed=seed + 1))
        s.append(line([(x, y0), (x, y1)], 3.2, TRIM, taper=.1, wmin=.9, seed=seed + 4))
        s.append(line([(x - w / 2, (y0 + y1) / 2), (x + w / 2, (y0 + y1) / 2)], 3.2, TRIM, taper=.1, wmin=.9, seed=seed + 5))
    # подоконник и замковый камень
    s.append(shape(rect_pts(x - w / 2 - 14, y1 + 8, x + w / 2 + 14, y1 + 20), TRIM, "", w=3, seed=seed + 6))
    s.append(shape([(x - 12, y0 - 22, 1), (x + 12, y0 - 22, 1), (x + 8, y0 - 6, 1), (x - 8, y0 - 6, 1)], TRIM, "", w=2.6, seed=seed + 7))
    return "".join(s)


OPEN_WIN = [(80, 640, 740), (580, 640, 740), (175, 820, 920), (485, 820, 920), (340, 820, 920)]


def building():
    s = []
    # тень на газоне
    s.append(blob([(GX0 + 20, GBASE), (GX1 + 60, GBASE), (GX1 + 140, GBASE + 46), (GX0 + 60, GBASE + 46)], "#3c7a36", .6, blur(6)))
    # крыша
    roof = [(GX0 - 16, GTOP), (GX0 + 60, GTOP - 80), (GX1 - 60, GTOP - 80), (GX1 + 16, GTOP)]
    s.append(shape(roof, "#4a4f63", blob([(GX0 + 60, GTOP - 80), (GX1 - 60, GTOP - 80), (GX1 - 50, GTOP - 66), (GX0 + 50, GTOP - 66)], "#6a7088") +
                   "".join(line([(GX0 + 40 + k * 60, GTOP - 4), (GX0 + 70 + k * 60, GTOP - 76)], 2.4, "#363a4c", seed=700 + k, op=.8) for k in range(10)),
                   w=4.6, seed=31))
    # трубы
    for x in (110, 570):
        s.append(shape(rect_pts(x - 18, GTOP - 120, x + 18, GTOP - 60), BRICK, blob(rect_pts(x + 4, GTOP - 120, x + 18, GTOP - 60), BRICK_SH),
                       w=3.6, seed=32 + x))
        s.append(shape(rect_pts(x - 24, GTOP - 130, x + 24, GTOP - 116), TRIM, "", w=3, seed=34 + x))
    # фасад кирпичом
    fac = rect_pts(GX0, GTOP, GX1, GBASE)
    inner = f'<rect x="{GX0}" y="{GTOP}" width="{GX1 - GX0}" height="{GBASE - GTOP}" fill="url(#pBrick)"/>'
    inner += blob([(GX1 - 70, GTOP), (GX1, GTOP), (GX1, GBASE), (GX1 - 40, GBASE)], BRICK_DK, .35)
    inner += blob(rect_pts(GX0, GTOP, GX1, GTOP + 26), BRICK_DK, .45)
    s.append(shape(fac, BRICK, inner, w=5, seed=35))
    # белые пояса и карниз
    s.append(shape(rect_pts(GX0 - 18, GTOP - 10, GX1 + 18, GTOP + 14), TRIM, blob(rect_pts(GX0 - 18, GTOP + 6, GX1 + 18, GTOP + 14), "#cfc6b4"), w=4, seed=36))
    s.append(shape(rect_pts(GX0 - 6, 776, GX1 + 6, 790), TRIM, "", w=3.2, seed=37))
    s.append(shape(rect_pts(GX0 - 10, GBASE - 40, GX1 + 10, GBASE), "#d9cfbd", blob(rect_pts(GX0 - 10, GBASE - 14, GX1 + 10, GBASE), "#b9ae99"), w=4, seed=38))
    # окна
    k = 0
    for (y0, y1) in WIN_ROWS:
        for x in WIN_X:
            op = any(abs(ox - x) < 2 and abs(oy - y0) < 2 for ox, oy, _ in OPEN_WIN)
            s.append(window(x, y0, y1, op, seed=800 + k * 10))
            k += 1
    # портик: фронтон, колонны, дверь
    s.append(shape([(PX0 - 30, GTOP + 70), (340, GTOP - 10), (PX1 + 30, GTOP + 70)], TRIM,
                   blob([(PX0 + 10, GTOP + 60), (340, GTOP + 16), (PX1 - 10, GTOP + 60)], "#e3dccd"), w=4.4, seed=40))
    s.append(shape(rect_pts(PX0 - 30, GTOP + 70, PX1 + 30, GTOP + 92), TRIM, "", w=4, seed=41))
    s.append(shape(rect_pts(PX0 - 10, GTOP + 92, PX1 + 10, GBASE - 40), "#a2462f", blob(rect_pts(PX0 - 10, GTOP + 92, PX1 + 10, GTOP + 130), "#7a3324", .8), w=3.6, seed=42))
    s.append(window(340, 640, 740, False, seed=880))
    door = [(310, GBASE - 40, 1), (310, 860), (340, 832), (370, 860), (370, GBASE - 40, 1)]
    s.append(shape([(312, 820, 1), (368, 820, 1), (368, 920, 1), (312, 920, 1)], BRICK, "", ink=False))
    s.append(shape(door, "#5a3524", blob([(340, 832), (370, 860), (370, GBASE - 40), (348, GBASE - 40)], "#3f2418") +
                   line([(340, 840), (340, GBASE - 44)], 2.6, "#2a160e", seed=43), w=3.6, seed=44))
    for x in (PX0 - 2, PX0 + 34, PX1 - 34, PX1 + 2):
        col = rect_pts(x - 12, GTOP + 92, x + 12, GBASE - 40)
        s.append(shape(col, TRIM, blob(rect_pts(x + 3, GTOP + 92, x + 12, GBASE - 40), "#d4cbb8") +
                       line([(x - 4, GTOP + 100), (x - 4, GBASE - 48)], 2, "#cfc6b4", seed=45 + x), w=3.4, seed=46 + x))
        s.append(shape(rect_pts(x - 17, GTOP + 88, x + 17, GTOP + 100), TRIM, "", w=3, seed=47 + x))
        s.append(shape(rect_pts(x - 17, GBASE - 52, x + 17, GBASE - 40), TRIM, "", w=3, seed=48 + x))
    # ступени
    for j in range(3):
        s.append(shape(rect_pts(PX0 - 40 - j * 12, GBASE - 40 + j * 14, PX1 + 40 + j * 12, GBASE - 26 + j * 14), "#ece4d4", "", w=3.2, seed=49 + j))
    # башенка
    s.append(shape(rect_pts(290, 400, 390, GTOP - 10), TRIM, blob(rect_pts(360, 400, 390, GTOP - 10), "#d6cdb9"), w=4.4, seed=50))
    s.append(shape([(304, 400, 1), (304, 352), (340, 316), (376, 352), (376, 400, 1)], "#3d4058", "", w=3.4, seed=51))  # арка-проём
    s.append(shape(rect_pts(280, 392, 400, 408), TRIM, "", w=3.4, seed=52))
    s.append(shape(rect_pts(296, 300, 384, 316), TRIM, "", w=3.4, seed=53))
    s.append(shape([(300, 300, 1), (340, 190, 1), (380, 300, 1)], "#4a4f63", blob([(340, 190), (380, 300), (350, 300)], "#33374a"), w=4, seed=54))
    s.append(shape(ellipse_pts(340, 186, 8, 8, 10), "#e8c35a", "", w=2.6, seed=55))
    return "".join(s)


def flags(t):
    s = []
    for k, (x, ytop) in enumerate([(90, GTOP - 200), (590, GTOP - 200)]):
        s.append(line([(x, GTOP - 8), (x, ytop - 6)], 6, "#6c6f7e", taper=.1, wmin=.9, seed=60 + k))
        s.append(shape(ellipse_pts(x, ytop - 8, 6, 6, 8), "#e8c35a", "", w=2.4, seed=62 + k))
        pts_top, pts_bot = [], []
        L, Hh = 96, 56
        for i in range(9):
            u = i / 8
            dy = 9 * math.sin(u * 4.2 - t * 7.5 + k) * u
            pts_top.append((x + u * L, ytop + dy + 4 * u))
            pts_bot.append((x + u * L * .96, ytop + Hh + dy + 2 * u))
        poly = pts_top + pts_bot[::-1]
        sh = [(px, py + 2) for px, py in pts_top[4:]]
        inner = "".join(line([(x + u * L, ytop + 6 + 9 * math.sin(u * 4.2 - t * 7.5 + k) * u) for u in np.linspace(.3, 1, 5)],
                             4, "#a8241f", seed=64 + k, op=.6) for _ in [0])
        s.append(shape(poly, "#d8322b", inner, w=3.4, seed=66 + k))
    return "".join(s)


def clouds(t):
    s = []
    for k, (x0, y, sc, sp) in enumerate([(120, 180, 1.0, 14), (760, 120, 1.3, 9), (980, 330, .8, 18), (-200, 360, .9, 12)]):
        x = x0 + sp * (t - 15)
        pts = []
        for i in range(14):
            a = 2 * math.pi * i / 14
            r = 1 + .18 * math.sin(5 * a + k)
            pts.append((x + 110 * sc * math.cos(a) * r, y + 40 * sc * math.sin(a) * r * (0.75 if math.sin(a) > 0 else 1)))
        s.append(shape(pts, "#ffffff", blob(ellipse_pts(x + 20 * sc, y + 22 * sc, 90 * sc, 16 * sc, 10), "#d8e8f5"), w=3.6, seed=70 + k))
    return "".join(s)


# ─── дневники
def diary_side(cx, cy, w, col, rot=0.0, seed=0):
    """Дневник сбоку-спереди в стопке: обложка сверху, обрез страниц, корешок слева."""
    hh = LH
    pts = [(-w / 2, -hh / 2, 1), (w / 2, -hh / 2, 1), (w / 2, hh / 2, 1), (-w / 2, hh / 2, 1)]
    pts = lib.T(pts, cx, cy, 1, rot, 0, 0)
    inner = []
    pg = lib.T([(-w / 2 + 16, -hh / 2 + 4), (w / 2 - 3, -hh / 2 + 4), (w / 2 - 3, hh / 2 - 3), (-w / 2 + 16, hh / 2 - 3)], cx, cy, 1, rot, 0, 0)
    inner.append(blob([p + (1,) for p in pg], "#f6efdc"))
    for j in (1, 2):
        yy = -hh / 2 + 4 + j * (hh - 7) / 3
        inner.append(line(lib.T([(-w / 2 + 20, yy), (w / 2 - 6, yy)], cx, cy, 1, rot, 0, 0), 1.2, "#cdbf9f", taper=.1, wmin=.8, seed=seed + j))
    sp = lib.T([(-w / 2, -hh / 2), (-w / 2 + 16, -hh / 2), (-w / 2 + 16, hh / 2), (-w / 2, hh / 2)], cx, cy, 1, rot, 0, 0)
    inner.append(blob([p + (1,) for p in sp], lib.mul(col, (.78, .78, .8))))
    return shape(pts, col, "".join(inner), w=2.8, seed=seed, var=.15)


def stack_layout():
    rs = np.random.RandomState(21)
    L = []
    for i in range(80):
        L.append((rs.uniform(-14, 14), rs.uniform(-2.2, 2.2), COVERS[(i * 5 + 3) % len(COVERS)], rs.uniform(280, 316)))
    return L


SPAWN0, SPAWN_DT, SPAWN_N, FLY = 15.1, 0.072, 32, 0.62


def flights():
    rs = np.random.RandomState(8)
    out = []
    for i in range(SPAWN_N):
        ox, oy0, oy1 = OPEN_WIN[i % len(OPEN_WIN)]
        out.append(dict(t0=SPAWN0 + i * SPAWN_DT, x0=ox + 10, y0=(oy0 + oy1) / 2, col=COVERS[(i * 3 + 1) % len(COVERS)],
                        spin=rs.uniform(-420, 420), arc=rs.uniform(90, 200), seed=i))
    return out


def landed(t):
    return sum(1 for fl in _ST["fl"] if t >= fl["t0"] + FLY)


def stack(t):
    n = N0 + landed(t)
    s = []
    # тень
    s.append(blob(ellipse_pts(STX + 20, SBASE + 8, 210, 26, 14), "#2f6a2c", .55, blur(6)))
    lay = _ST["lay"]
    for i in range(n):
        dx, rot, col, w = lay[i]
        y = SBASE - LH / 2 - i * LH
        bounce = 0.0
        if i >= N0:   # только что упавший — пружинит
            fl = _ST["fl"][i - N0]
            e = t - fl["t0"] - FLY
            if e < 0.3:
                bounce = -6 * math.exp(-e * 14) * math.cos(e * 40)
                rot += 5 * math.exp(-e * 12)
        s.append(diary_side(STX + dx, y + bounce, w, col, rot, seed=900 + i))
    return "".join(s)


def flying(t):
    s = []
    for fl in _ST["fl"]:
        e = t - fl["t0"]
        if e < 0 or e >= FLY:
            continue
        u = e / FLY
        i = _ST["fl"].index(fl)
        tx, ty = STX + _ST["lay"][N0 + i][0], SBASE - LH / 2 - (N0 + i) * LH
        x = fl["x0"] + (tx - fl["x0"]) * u
        y = fl["y0"] + (ty - fl["y0"]) * u - fl["arc"] * 4 * u * (1 - u)
        sc = 0.45 + 0.55 * ease_io(u)
        rot = fl["spin"] * (1 - u) + _ST["lay"][N0 + i][1] * u
        # дневник раскрыт и машет страницами в полёте, к стопке закрывается
        flap = math.sin(e * 26 + fl["seed"]) * (1 - smooth(.6, .95, u))
        s.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{book_fly(fl["col"], flap, fl["seed"])}</g>')
        # штрихи скорости позади
        if u < 0.8:
            vx, vy = tx - fl["x0"], (ty - fl["y0"]) - fl["arc"] * 4 * (1 - 2 * u)
            L = math.hypot(vx, vy) + 1e-6
            ux, uy = vx / L, vy / L
            for j in (-1, 1):
                ox, oy = -uy * 16 * j, ux * 16 * j
                s.append(line([(x + ox - ux * 40, y + oy - uy * 40), (x + ox - ux * 90, y + oy - uy * 90)], 4, "#ffffff", taper=.6, seed=fl["seed"] + 30 + j, op=.8))
    return "".join(s)


def book_fly(col, flap, seed):
    """Летящий дневник: корешок по центру, две «крыльями» раскрытые половинки (раскрытие flap)."""
    s = []
    op = 0.25 + 0.75 * abs(flap)
    for sg in (-1, 1):
        k = 0.35 + 0.65 * op
        cover = [(0, -42, 1), (sg * 120 * k, -50 + 14 * (1 - k), 1), (sg * 120 * k, 44 - 8 * (1 - k), 1), (0, 42, 1)]
        pages = [(0, -36), (sg * 108 * k, -42 + 12 * (1 - k)), (sg * 108 * k, 36 - 6 * (1 - k)), (0, 36)]
        s.append(shape(cover, col if sg < 0 else lib.mul(col, (.85, .85, .88)), "", w=3.4, seed=seed * 2 + (sg > 0)))
        s.append(shape([p + (1,) for p in pages], "#fbf5e6", "".join(
            line([(sg * 14, -20 + j * 16), (sg * 96 * k, -24 + j * 16 + 6 * (1 - k))], 2, "#c9d6ec", taper=.1, wmin=.8, seed=seed + j)
            for j in range(4)), w=2.4, seed=seed * 2 + 7 + (sg > 0)))
    return "".join(s)


# ─── табло
PNX, PNY, PNW, PNH = 840, 330, 404, 168


def counter_value(t):
    u = clamp((t - 15.72) / (STOP - 15.72))
    return 12000 * (1 - (1 - u) ** 2.4)


def odometer(t):
    v = counter_value(t)
    s = []
    pop = 0.0
    if t > STOP - 0.02:
        e = t - STOP + 0.02
        pop = math.exp(-e * 5) * math.sin(min(e * 18, math.pi)) if e < math.pi / 18 else math.exp(-e * 5) * 0.0
        pop = 0.14 * math.exp(-e * 6) * (1 if e < .5 else 0) * math.cos(e * 14)
    sc = 1 + pop
    # тень и корпус
    body = []
    body.append(blob(rect_pts(PNX - PNW / 2 + 12, PNY - PNH / 2 + 16, PNX + PNW / 2 + 12, PNY + PNH / 2 + 16, 24), "#21406a", .35, blur(6)))
    body.append(shape(rect_pts(PNX - PNW / 2, PNY - PNH / 2, PNX + PNW / 2, PNY + PNH / 2, 26), "#2c3150",
                      blob(rect_pts(PNX - PNW / 2, PNY + PNH / 2 - 26, PNX + PNW / 2, PNY + PNH / 2), "#1f2340"), w=5.4, seed=81))
    # окна цифр
    fs = 112
    cw, gap = 62, 30
    cols = 5
    total = cols * cw + gap
    x0 = PNX - total / 2
    for i in range(cols):
        p = cols - 1 - i
        cx = x0 + i * cw + (gap if i >= 2 else 0) + cw / 2
        cl = lib.clip_rect(cx - cw / 2 + 3, PNY - PNH / 2 + 22, cw - 6, PNH - 44, 8)
        body.append(f'<rect x="{f(cx - cw / 2 + 3)}" y="{PNY - PNH / 2 + 22}" width="{cw - 6}" height="{PNH - 44}" rx="8" fill="#171a2e"/>')
        q = v / 10 ** p
        d = int(math.floor(q)) % 10
        if p == 0:
            off = q - math.floor(q)
        else:
            low = (v % 10 ** p) / 10 ** p
            off = clamp((low - 0.9) / 0.1)
        if p > 0 and q < 0.9:
            continue
        g = []
        step = fs * 1.05
        for dd, yy in ((d, -off * step), ((d + 1) % 10, step - off * step)):
            g.append(f'<text x="{f(cx)}" y="{f(PNY + fs * .36 + yy)}" text-anchor="middle" font-family="IDB" font-weight="900" '
                     f'font-size="{fs}" fill="{"#ffd84a" if t >= STOP - 0.02 else "#ffe9a8"}">{dd}</text>')
        body.append(f'<g clip-path="url(#{cl})">{"".join(g)}</g>')
        body.append(blob(rect_pts(cx - cw / 2 + 3, PNY - PNH / 2 + 22, cx + cw / 2 - 3, PNY - PNH / 2 + 46), "#000000", .25))
    # винтики
    for dx in (-PNW / 2 + 20, PNW / 2 - 20):
        body.append(f'<circle cx="{f(PNX + dx)}" cy="{PNY}" r="5" fill="#8a90b4"/>')
    s.append(f'<g transform="translate({PNX} {PNY}) scale({f(sc)}) translate({-PNX} {-PNY})">{"".join(body)}</g>')
    if t > STOP - 0.02:   # вспышка и искры на «12 000»
        e = t - STOP + 0.02
        a_ = math.exp(-e * 3)
        for k in range(10):
            ang = 2 * math.pi * k / 10 + .2
            r0 = 230 + 120 * ease_out(e / .5)
            L = 44 * a_
            if L > 3:
                s.append(line([(PNX + math.cos(ang) * r0, PNY + math.sin(ang) * r0 * .55),
                               (PNX + math.cos(ang) * (r0 + L), PNY + math.sin(ang) * (r0 + L) * .55)], 8, "#ffd84a", taper=.5, seed=90 + k))
    return "".join(s)


def build_static10():
    if _ST.get("s10"):
        return
    brick_defs()
    _ST["sky"] = sky()
    _ST["lawn"] = lawn()
    _ST["bld"] = building()
    _ST["lay"] = stack_layout()
    _ST["fl"] = flights()
    _ST["s10"] = True
    lib.static_done()


# ═══════════════════════════════ s11 — раскрытые дневники
PEN = "#26356f"


def doodle(kind, seed):
    """Рисунок дня на странице (локально: страница 0..360 × 0..440), ручка + пара цветных пятен маркера."""
    s = []
    L = lambda pts, w=4.2, col=PEN, sd=0: s.append(line(pts, w, col, taper=.5, wmin=.35, seed=seed * 50 + sd))
    if kind == "desk":
        s.append(blob(rect_pts(150, 250, 290, 262), "#f2b45a", .9))
        L([(60, 262), (320, 262)], 5, sd=1)                          # стол
        L([(90, 262), (90, 360)], sd=2); L([(290, 262), (290, 360)], sd=3)
        L([(160, 250), (170, 190), (270, 190), (270, 250)], sd=4)     # ноутбук
        L([(150, 252), (290, 252)], sd=5)
        s.append(f'<circle cx="112" cy="138" r="30" fill="none" stroke="{PEN}" stroke-width="4.2"/>')   # голова
        L([(112, 168), (106, 260)], sd=6)                             # тело
        L([(110, 196), (150, 220), (178, 236)], sd=7)                 # рука к клавиатуре
        L([(106, 258), (150, 262), (148, 330)], sd=8)                 # нога на стуле
        L([(70, 280), (130, 280)], sd=9); L([(76, 280), (72, 350)], sd=10)  # стул
        L([(102, 136), (104, 140)], 5, sd=11); L([(122, 136), (124, 140)], 5, sd=12)
        L([(104, 152), (112, 156), (120, 152)], 3.4, sd=13)
    elif kind == "mug":
        s.append(blob([(120, 200), (240, 200), (232, 330), (128, 330)], "#9fd0e8", .8))
        L([(118, 196), (126, 332), (234, 332), (242, 196)], 5, sd=1)
        L([(116, 196), (244, 196)], 5, sd=2)
        L([(242, 226), (282, 230), (284, 280), (236, 296)], 4.6, sd=3)
        for k, x in enumerate((150, 182, 214)):
            L([(x, 180), (x - 12, 150), (x + 4, 120), (x - 8, 90)], 3.4, sd=4 + k)
        L([(80, 352), (290, 352)], 4, sd=8)
    elif kind == "chart":
        L([(70, 90), (70, 350), (310, 350)], 5, sd=1)
        for k, (x, h) in enumerate([(110, 50), (160, 90), (210, 130), (260, 200)]):
            s.append(blob(rect_pts(x - 18, 350 - h, x + 18, 348), "#7cc576", .9))
            L([(x - 18, 348), (x - 18, 350 - h), (x + 18, 350 - h), (x + 18, 348)], 4, sd=2 + k)
        L([(96, 280), (160, 230), (212, 200), (290, 120)], 4.6, "#d9433a", sd=8)
        L([(266, 118), (292, 118), (292, 144)], 4.6, "#d9433a", sd=9)
    elif kind == "sun":
        s.append(blob(ellipse_pts(180, 190, 60, 60, 16), "#ffd45a", .9))
        s.append(f'<circle cx="180" cy="190" r="60" fill="none" stroke="{PEN}" stroke-width="4.4"/>')
        for k in range(10):
            a = 2 * math.pi * k / 10
            L([(180 + math.cos(a) * 80, 190 + math.sin(a) * 80), (180 + math.cos(a) * 110, 190 + math.sin(a) * 110)], 4, sd=2 + k)
        L([(160, 182), (162, 186)], 5, sd=20); L([(198, 182), (200, 186)], 5, sd=21)
        L([(158, 206), (180, 220), (202, 206)], 4, sd=22)
        L([(60, 360), (130, 330), (200, 350), (300, 320)], 4, "#3f9a5c", sd=23)
    elif kind == "steps":
        for k in range(4):
            x0, y0 = 70 + k * 60, 340 - k * 60
            L([(x0, y0), (x0 + 60, y0), (x0 + 60, y0 - 60)], 4.6, sd=1 + k)
        s.append(f'<circle cx="290" cy="80" r="20" fill="none" stroke="{PEN}" stroke-width="4"/>')
        L([(290, 100), (284, 150)], sd=10); L([(284, 150), (268, 186)], sd=11); L([(284, 150), (300, 184)], sd=12)
        L([(288, 116), (264, 130)], sd=13); L([(288, 116), (316, 104)], sd=14)
        L([(316, 104), (320, 70)], 3.6, "#d9433a", sd=15)
        s.append(blob([(320, 70, 1), (348, 78, 1), (320, 88, 1)], "#d9433a"))
    elif kind == "plant":
        s.append(blob([(130, 260), (230, 260), (218, 350), (142, 350)], "#e08a5a", .85))
        L([(126, 258), (140, 352), (220, 352), (234, 258), (126, 258)], 4.6, sd=1)
        L([(180, 258), (178, 190), (184, 120)], 4.4, "#2f7a3a", sd=2)
        for k, (a, b) in enumerate([((178, 210), (130, 180)), ((180, 180), (232, 150)), ((182, 140), (140, 100))]):
            s.append(blob([a, ((a[0] + b[0]) / 2, b[1] - 18), b, ((a[0] + b[0]) / 2, a[1] + 6)], "#7cc576", .9))
            L([a, ((a[0] + b[0]) / 2, b[1] - 18), b], 3.6, "#2f7a3a", sd=4 + k)
            L([b, ((a[0] + b[0]) / 2, a[1] + 6), a], 3.6, "#2f7a3a", sd=8 + k)
    return "".join(s)


def page_lines(x0, y0, w, h, seed, side):
    s = []
    for k in range(1, 13):
        y = y0 + k * h / 13
        s.append(line([(x0 + 16, y), (x0 + w - 16, y)], 1.6, "#bfd0ea", taper=.1, wmin=.9, seed=seed + k, op=.9))
    xm = x0 + (w - 34 if side > 0 else 34)
    s.append(line([(xm, y0 + 6), (xm, y0 + h - 6)], 1.8, "#efa3a3", taper=.1, wmin=.9, seed=seed + 40, op=.9))
    return "".join(s)


PW, PH = 380, 470   # страница


def open_diary(cx, cy, rot, col, left, right, flip=None, seed=0, tflip=0.0):
    """Раскрытый дневник: обложка-подложка, две страницы с лёгким изгибом к корешку, тень в сгибе.
    flip — (u, front_kind, back_kind): страница справа переворачивается справа налево (u 0..1)."""
    s = []
    # тень на столе
    s.append(blob(rect_pts(-PW - 30 + 18, -PH / 2 - 20 + 26, PW + 30 + 18, PH / 2 + 26 + 26, 20), "#3a1f10", .45, blur(10)))
    s.append(shape(rect_pts(-PW - 30, -PH / 2 - 22, PW + 30, PH / 2 + 26, 18), col,
                   blob(rect_pts(-PW - 30, PH / 2 + 4, PW + 30, PH / 2 + 26), lib.mul(col, (.75, .75, .8))), w=4.6, seed=seed))
    # пачки страниц (видимые обрезы)
    for sg in (-1, 1):
        for j in range(3):
            pts = [(sg * 6, -PH / 2 + 8 - j * 0), (sg * (PW + 8 - j * 3), -PH / 2 + 4 + j * 4), (sg * (PW + 8 - j * 3), PH / 2 + 8 + j * 4), (sg * 6, PH / 2 + 14)]
            s.append(shape([p + (1,) for p in pts], "#efe6cf", "", w=2.0, seed=seed + 10 + j + (sg > 0) * 5))
    for sg, kind in ((-1, left), (1, right)):
        x0 = -PW if sg < 0 else 0
        pts = [(x0, -PH / 2 + 10, 1), (x0 + PW, -PH / 2 + 10, 1), (x0 + PW, PH / 2, 1), (x0, PH / 2, 1)]
        if sg < 0:
            pts = [(-PW, -PH / 2, 1), (-PW * .5, -PH / 2 - 6), (0, -PH / 2 + 12, 1), (0, PH / 2 + 10, 1), (-PW * .5, PH / 2 + 2), (-PW, PH / 2 - 4, 1)]
        else:
            pts = [(0, -PH / 2 + 12, 1), (PW * .5, -PH / 2 - 6), (PW, -PH / 2, 1), (PW, PH / 2 - 4, 1), (PW * .5, PH / 2 + 2), (0, PH / 2 + 10, 1)]
        inner = page_lines(x0, -PH / 2, PW, PH, seed + 100 + (sg > 0) * 50, sg)
        inner += f'<g transform="translate({x0 + 10} {-PH / 2 + 20})">{doodle(kind, seed + (sg > 0))}</g>' if kind else ""
        # тень к сгибу
        gid = lib.lin_grad([(0, "#6b5536", .45), (1, "#6b5536", 0)], 0, 0, -sg * 1, 0)
        inner += f'<rect x="{0 if sg > 0 else -60}" y="{-PH}" width="60" height="{2 * PH}" fill="url(#{gid})"/>'
        s.append(shape(pts, "#fdf8ec", inner, w=3.2, seed=seed + 20 + (sg > 0)))
    if flip is not None:
        u, fk, bk = flip
        # переворачиваемая страница: ширина = PW·cos(πu), видна лицевая (правая) или оборот (левая); тень к сгибу
        c = math.cos(math.pi * u)
        wv = PW * abs(c)
        lift = math.sin(math.pi * u)
        sg = 1 if c >= 0 else -1
        x1 = sg * wv
        top_bend = -40 * lift
        pts = [(0, -PH / 2 + 12, 1), (x1 * .5, -PH / 2 - 6 + top_bend), (x1, -PH / 2 + top_bend * .6, 1), (x1, PH / 2 - 4 + top_bend * .3, 1),
               (x1 * .5, PH / 2 + 2 + top_bend * .5), (0, PH / 2 + 10, 1)]
        kind = fk if sg > 0 else bk
        x0 = 0 if sg > 0 else -PW
        inner = page_lines(x0, -PH / 2, PW, PH, seed + 300, sg)
        if kind:
            inner += f'<g transform="translate({x0 + 10} {-PH / 2 + 20})">{doodle(kind, seed + 7)}</g>'
        inner_g = f'<g transform="scale({f(max(abs(c), .02))} 1)">{inner}</g>'
        shade = f'<rect x="-{PW}" y="{-PH}" width="{2 * PW}" height="{2 * PH}" fill="#7a6648" opacity="{.35 * lift:.3f}"/>'
        # тень, которую страница отбрасывает на нижнюю
        s.append(blob([(0, -PH / 2 + 14), (x1 + sg * 30 * lift, -PH / 2 + 30), (x1 + sg * 30 * lift, PH / 2 + 14), (0, PH / 2 + 12)], "#5a4428", .25 * lift, blur(8)))
        s.append(shape(pts, "#fdf8ec" if sg > 0 else "#f6eedb", inner_g + shade, w=3.2, seed=seed + 40))
    # корешок-сгиб
    s.append(line([(0, -PH / 2 + 12), (0, PH / 2 + 10)], 3.4, INK, taper=.3, wmin=.5, seed=seed + 50, op=.8))
    # ляссе-ленточка
    s.append(shape([(-6, PH / 2 + 8, 1), (6, PH / 2 + 8, 1), (8, PH / 2 + 80, 1), (0, PH / 2 + 66, 1), (-8, PH / 2 + 80, 1)], "#d9433a", "", w=2.6, seed=seed + 60))
    return f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)})">{"".join(s)}</g>'


DIARIES = [  # центр, поворот, обложка, левая, правая, (время листания, лицевая, оборот, следующая правая)
    (260, 230, -7, "#7a4fb0", "plant", "sun", None),
    (1500, 330, 5, "#e07a3a", "chart", "steps", None),
    (300, 1560, 4, "#2b8f97", "mug", "steps", None),
    (580, 860, -4, "#2f6db5", "desk", "mug", (18.0, "mug", "chart", "sun")),
    (1400, 1240, 3, "#3f9a5c", "steps", "plant", (19.3, "plant", "desk", "chart")),
]


def desk():
    s = []
    DEFS.append('<pattern id="pWood" width="420" height="140" patternUnits="userSpaceOnUse">'
                '<rect width="420" height="140" fill="#b9814f"/>'
                '<path d="M0 30 C120 22 260 40 420 28 M0 76 C140 84 280 66 420 80 M0 118 C110 110 300 126 420 114" fill="none" stroke="#9a6638" stroke-width="3"/>'
                '<path d="M60 52 C90 48 120 56 150 50" fill="none" stroke="#a87244" stroke-width="2"/>'
                '<rect y="138" width="420" height="2" fill="#7f522c"/></pattern>')
    s.append(f'<rect x="-600" y="-600" width="3600" height="3200" fill="url(#pWood)"/>')
    rad_grad([(0, "#ffe2a8", .35), (1, "#ffe2a8", 0)], 1300, 700, 1400, 900, gid="gDeskL")
    s.append('<rect x="-600" y="-600" width="3600" height="3200" fill="url(#gDeskL)"/>')
    # обжитые мелочи: кружка, ручка, стикеры, скрепки
    s.append(shape(ellipse_pts(1060, 820, 82, 82, 18), "#e9e4dc", blob(ellipse_pts(1060, 820, 64, 64, 16), "#6b3d22") +
                   blob(ellipse_pts(1044, 806, 22, 10, 10, rot=-20), "#8c5634"), w=4.4, seed=900))
    s.append(shape([(1138, 806), (1172, 802), (1178, 838), (1140, 838)], "#e9e4dc", "", w=4, seed=901))
    s.append(shape(rect_pts(860, 1340, 1010, 1480, 4), "#ffe27a", blob(rect_pts(860, 1460, 1010, 1480), "#e8c45a"), w=3.4, seed=902))
    s.append(shape(rect_pts(1760, 1640, 1900, 1780, 4), "#9fe0c8", "", w=3.4, seed=903))
    s.append(shape(ellipse_pts(1120, 1700, 110, 110, 18), "#f2efe6", blob(ellipse_pts(1120, 1700, 88, 88, 16), "#d9d2c2"), w=4, seed=906))
    return "".join(s)


def build_static11():
    if _ST.get("s11"):
        return
    _ST["desk"] = desk()
    _ST["s11"] = True
    lib.static_done()


# ═══════════════════════════════ кадр
def frame(sid, t):
    if sid == "s10":
        build_static10()
        lib.dyn_begin()
        art = _ST["sky"] + clouds(t) + _ST["lawn"] + _ST["bld"] + flags(t) + stack(t) + flying(t) + odometer(t)
        u = ease_io((t - 15.7) / 2.4)
        cm = cam(545, 860 - 50 * u, 0.93 + 0.08 * u)
        return svg(f'<rect width="{W}" height="{H}" fill="#9cc8ee"/><g transform="{cm}">{art}</g>')
    build_static11()
    lib.dyn_begin()
    parts = [_ST["desk"]]
    for (cx, cy, rot, col, lk, rk, fl) in DIARIES:
        flip = None
        right = rk
        if fl:
            tf, fk, bk, nxt = fl
            u = clamp((t - tf) / 0.62)
            u = u * u * (3 - 2 * u)
            if 0 < u < 1:
                flip = (u, fk, bk)
                right = nxt
            elif u >= 1:
                lk, right = bk, nxt
        # дневник чуть «дышит» — страницы подрагивают от сквозняка
        parts.append(open_diary(cx, cy + 3 * math.sin(t * 2 + cx), rot, col, lk, right, flip, seed=int(cx) // 10))
    lin = clamp((t - 17.7) / 2.4)
    u = 0.45 * lin + 0.55 * ease_io(lin)
    cm = cam(620 + 760 * u, 900 + 300 * u, 1.24 - 0.03 * math.sin(math.pi * u))
    return svg(f'<rect width="{W}" height="{H}" fill="#b9814f"/><g transform="{cm}">{"".join(parts)}</g>')
