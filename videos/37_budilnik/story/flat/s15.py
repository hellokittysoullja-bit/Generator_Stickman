"""s15 (19.08–20.72, клип 18.88–20.92): дом в разрезе, вид сбоку, наша квартира — средний этаж: слева комната с диваном
(Дима спит под красным пледом в клетку), посередине коридор, справа далеко кухня с красной кофеваркой и будильником.
Этажи соседей выше и ниже — приглушённые. На «другом конце квартиры» (19.16–20.40) от дивана к будильнику по полу
рисуется пунктир шагов — дугами, шаг за шагом, в конце стрелка и блик у будильника. Камера с первого кадра отъезжает
от дивана на всю квартиру.

Мир: пол квартиры y = 0, потолок y = −820, квартира x 0…2400."""
import math

import numpy as np

import flatlib as F
import lib
from flatlib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth

T_A, T_B = 18.88, 20.92
T_DR = F.word("другом", 19.0)
T_END = 20.40
FW, CEIL, SLAB = 2400.0, -820.0, 70.0
FLOOR_H = -CEIL + SLAB            # высота этажа
CUT, CUT_SH = "#7a6656", "#5f4e42"
SOFA = (120, 640)                 # x0, x1 дивана
AL = (2160.0, -300.0)             # будильник на столешнице (центр низа)
MACH_X = 2330.0
P0 = (440.0, -16.0)               # начало пунктира (у дивана)


def ink_k(s):
    return 1.0 / max(1.0, s) ** 0.62 if s >= 1 else 1.0 / s ** 0.72


# ───────────────────────────── соседи и здание
def neighbor_floor(y0, k):
    """Этаж соседей: приглушённые комнаты с окном и силуэтами мебели (y0 — пол этажа)."""
    rs = np.random.RandomState(500 + k)
    s = []
    cols = ["#b7b5c4", "#c2b8aa", "#aebdb8"]
    xs = [0, 760, 1600, FW]
    for j in range(3):
        a, b = xs[j], xs[j + 1]
        s.append(blob(rect_pts(a, y0 + CEIL, b, y0), mix(cols[(j + k) % 3], "#8a8aa0", .25)))
        wx = a + (b - a) * rs.uniform(.25, .45)
        s.append(shape(rect_pts(wx, y0 - 640, wx + 220, y0 - 330, 6), "#d9e4ea", blob(rect_pts(wx + 104, y0 - 640, wx + 116, y0 - 330), "#9aa6b4"),
                       w=3.6, seed=510 + k * 7 + j))
        kind = (j + k) % 3
        fc = "#8f8a9c"
        if kind == 0:      # шкаф
            fx = a + 60
            s.append(shape(rect_pts(fx, y0 - 560, fx + 200, y0, 6), fc, blob(rect_pts(fx + 98, y0 - 560, fx + 102, y0), "#6f6a7c"), w=3.6,
                           seed=520 + k * 7 + j))
        elif kind == 1:    # стол со стулом
            fx = b - 380
            s.append(shape(rect_pts(fx, y0 - 280, fx + 260, y0 - 250, 4), fc, "", w=3.4, seed=530 + k * 7 + j))
            for lx in (fx + 20, fx + 230):
                s.append(shape(rect_pts(lx, y0 - 250, lx + 14, y0), fc, "", w=3, seed=540 + k * 7 + j + int(lx) % 5))
        else:              # кровать
            fx = a + 80
            s.append(shape(rect_pts(fx, y0 - 200, fx + 420, y0 - 70, 16), fc, blob(rect_pts(fx, y0 - 200, fx + 90, y0 - 150, 12), "#b3aec0"),
                           w=3.6, seed=550 + k * 7 + j))
        if j < 2:
            s.append(blob(rect_pts(b - 20, y0 + CEIL, b + 20, y0 - 600), CUT))
    s.append(blob(rect_pts(-200, y0 + CEIL, FW + 200, y0 + CEIL + 1), "#000000", 0))
    g = lib.lin_grad([(0, "#2a2840", .42), (1, "#2a2840", .42)], 0, 0, 0, 1)
    s.append(f'<rect x="0" y="{y0 + CEIL:.0f}" width="{FW:.0f}" height="{-CEIL:.0f}" fill="url(#{g})"/>')
    return "".join(s)


def building():
    s = []
    # небо и земля
    sky = lib.lin_grad([(0, "#8fc4ea", 1), (1, "#e6f4fa", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-4000" y="-6000" width="10400" height="6000" fill="url(#{sky})"/>')
    s.append(blob(ellipse_pts(-500, -2600, 120, 120, 18), "#fff3c4"))
    for (cx, cy, w) in ((-700, -1900, 240), (3000, -2300, 300), (2900, -1300, 200), (-800, -900, 180)):
        s.append(shape(ellipse_pts(cx, cy, w, w * .32, 14, jitter=.08, seed=int(cx) % 50), "#ffffff", "", w=3.4, seed=600 + int(cy) % 97))
    s.append(f'<rect x="-4000" y="{2 * FLOOR_H:.0f}" width="10400" height="3000" fill="#8fb36a"/>')
    s.append(line([(-4000, 2 * FLOOR_H), (6400, 2 * FLOOR_H)], 4, INK, taper=.05, wmin=.9, seed=601))
    for k, x in enumerate((-900, -400, 2900, 3400)):
        s.append(shape(ellipse_pts(x, 2 * FLOOR_H - 150, 230, 190, 16, jitter=.1, seed=k), "#6f9a52",
                       blob(ellipse_pts(x + 60, 2 * FLOOR_H - 110, 160, 120, 12), "#5a8442", .9), w=4, seed=610 + k))
        s.append(shape(rect_pts(x - 26, 2 * FLOOR_H - 60, x + 26, 2 * FLOOR_H), "#8a5a34", "", w=3.4, seed=620 + k))
    # стены здания (разрез) — от земли до крыши
    top = -3 * FLOOR_H + SLAB
    s.append(blob(rect_pts(-80, top, FW + 80, 2 * FLOOR_H), CUT))
    # этажи соседей
    for k, y0 in enumerate((-2 * FLOOR_H, -FLOOR_H, FLOOR_H, 2 * FLOOR_H)):
        s.append(neighbor_floor(y0, k))
    # перекрытия
    for y0 in (-2 * FLOOR_H, -FLOOR_H, 0, FLOOR_H, 2 * FLOOR_H):
        s.append(blob(rect_pts(-80, y0, FW + 80, y0 + SLAB), CUT_SH))
    # крыша
    s.append(shape([(-140, top, 1), (FW + 140, top, 1), (FW + 60, top - 120, 1), (-60, top - 120, 1)], "#8a4a3a",
                   blob([(-140, top - 30), (FW + 140, top - 30), (FW + 140, top), (-140, top)], "#6a382c", .9), w=5, seed=630))
    s.append(shape(rect_pts(1800, top - 300, 1920, top - 110, 4), "#9a5a44", "", w=4, seed=631))
    # контур здания
    s.append(line([(-80, top), (-80, 2 * FLOOR_H)], 6, INK, taper=.02, wmin=.9, seed=632))
    s.append(line([(FW + 80, top), (FW + 80, 2 * FLOOR_H)], 6, INK, taper=.02, wmin=.9, seed=633))
    return "".join(s)


# ───────────────────────────── наша квартира
def flat_rooms(t):
    s = []
    # комната
    s.append(blob(rect_pts(0, CEIL, 800, 0), "#e9d3b0"))
    s.append(blob(rect_pts(0, -150, 800, 0), "#d9bf96", .9))
    s.append(shape(rect_pts(250, -680, 560, -380, 8), "#bfe0f2", blob(ellipse_pts(330, -600, 26, 26, 12), "#fff3c4") +
                   blob(rect_pts(398, -680, 412, -380), "#efe6d6") + blob(rect_pts(250, -536, 560, -524), "#efe6d6"), w=4, seed=700))
    s.append(sofa())
    # коридор
    s.append(blob(rect_pts(840, CEIL, 1560, 0), "#b9d0c4"))
    for x in np.arange(860, 1560, 46):
        s.append(blob(rect_pts(x, CEIL, x + 6, -170), "#9ab5a8", .55))
    s.append(blob(rect_pts(840, -170, 1560, 0), "#f1e6cf"))
    s.append(shape(rect_pts(1000, -560, 1240, 0), "#c99566", blob(rect_pts(1200, -560, 1240, 0), "#a8774c", .8), w=4, seed=710))
    s.append(shape(rect_pts(1330, -600, 1470, -500, 3), "#7a5236", blob(rect_pts(1342, -588, 1458, -512), "#a8d4ea"), w=3.4, seed=711))
    s.append(shape(rect_pts(840, -10, 1560, 0), "#6f8f9e", "", w=2.4, seed=712))
    # кухня
    s.append(blob(rect_pts(1600, CEIL, FW, 0), "#f0dcb4"))
    lib.DEFS.append('<pattern id="pTile15" width="60" height="44" patternUnits="userSpaceOnUse"><rect width="60" height="44" fill="#f1e2c2"/>'
                    '<rect y="41" width="60" height="3" fill="#cfb488"/><rect x="57" width="3" height="44" fill="#cfb488"/></pattern>')
    s.append(f'<rect x="1600" y="-520" width="{FW - 1600:.0f}" height="220" fill="url(#pTile15)"/>')
    s.append(shape(rect_pts(1650, -780, 1900, -560, 8), "#bfe0f2", blob(ellipse_pts(1720, -720, 22, 22, 10), "#fff3c4") +
                   blob(rect_pts(1770, -780, 1780, -560), "#efe6d6"), w=4, seed=720))
    s.append(shape(rect_pts(1960, -780, FW - 20, -600, 6), "#9fc3b5", blob(rect_pts(2170, -780, 2176, -600), "#7ba393"), w=4, seed=721))
    s.append(shape(rect_pts(1640, -300, FW, -282), "#c98f5a", "", w=3.6, seed=722))
    s.append(shape(rect_pts(1640, -282, FW, 0), "#e9dcc4", "".join(line([(x, -276), (x, -6)], 3, "#c9b99c", seed=723 + k, taper=.05, wmin=.9)
                                                                    for k, x in enumerate((1840, 2040, 2240))), w=4, seed=724))
    # кофеварка и будильник
    mx = MACH_X
    s.append(shape(rect_pts(mx - 70, -490, mx + 70, -300, 16), "#c9473d", blob(rect_pts(mx + 40, -490, mx + 70, -300), "#9c3029", .9) +
                   blob(rect_pts(mx - 44, -400, mx + 44, -316, 8), "#2b2730"), w=3.6, seed=730))
    s.append(F.Wd.mug(mx, -312, .34, col="#3f9aa8"))
    s.append(F.alarm(AL[0], AL[1], 46, t, 7, 0, uid="a15"))
    # перегородки с дверными проёмами (разрез)
    for x in (800, 1560):
        s.append(blob(rect_pts(x, CEIL, x + 40, -640), CUT))
        s.append(blob(rect_pts(x - 4, -640, x + 44, -626), CUT_SH))
    s.append(blob(rect_pts(-80, CEIL, 0, 0), CUT))
    s.append(blob(rect_pts(FW, CEIL, FW + 80, 0), CUT))
    # тёплый утренний свет в квартире
    g = lib.rad_grad([(0, "#fff1c8", .35), (1, "#fff1c8", 0)], 1200, -500, 1500, 700)
    s.append(f'<rect x="0" y="{CEIL:.0f}" width="{FW:.0f}" height="{-CEIL:.0f}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def sofa():
    x0, x1 = SOFA
    s = []
    s.append(shape(rect_pts(x0, -300, x1, -110, 26), "#4f7fa0", blob(rect_pts(x0, -170, x1, -110), "#3d6683", .9), w=4.4, seed=740))
    s.append(shape(rect_pts(x0 - 20, -220, x0 + 60, -40, 18), "#5d8db0", "", w=4, seed=741))
    s.append(shape(rect_pts(x1 - 60, -220, x1 + 20, -40, 18), "#5d8db0", "", w=4, seed=742))
    s.append(shape(rect_pts(x0 + 40, -150, x1 - 40, -60, 14), "#5d8db0", "", w=4, seed=743))
    for x in (x0 + 30, x1 - 40):
        s.append(shape(rect_pts(x, -40, x + 14, 0), "#3a2c22", "", w=2.6, seed=744 + x % 7))
    # подушка, Дима под пледом (голова на подушке)
    s.append(shape(ellipse_pts(x0 + 120, -170, 70, 34, 14, rot=-8), "#f4f1ea", "", w=3.6, seed=745))
    s.append(shape(ellipse_pts(x0 + 150, -206, 40, 34, 14), "#ecc4a2", "", w=3.4, seed=746))
    s.append(shape([(x0 + 128, -236, 1), (x0 + 150, -260), (x0 + 172, -240), (x0 + 196, -250), (x0 + 186, -214), (x0 + 130, -220)], "#5a3826",
                   "", w=3.2, seed=747))
    pid = "plaid15"
    lib.DEFS.append(f'<pattern id="{pid}" width="48" height="48" patternUnits="userSpaceOnUse"><rect width="48" height="48" fill="#c4553f"/>'
                    '<rect y="17" width="48" height="14" fill="#a5432f"/><rect x="17" width="14" height="48" fill="#a5432f"/>'
                    '<rect y="22" width="48" height="4" fill="#e8b85a"/><rect x="22" width="4" height="48" fill="#e8b85a"/></pattern>')
    pl = [(x0 + 170, -200), (x0 + 260, -232), (x0 + 360, -214), (x1 - 40, -200), (x1 - 10, -150), (x1 - 30, -110, 1), (x0 + 150, -110, 1),
          (x0 + 140, -160)]
    s.append(shape(pl, "#c4553f", f'<rect x="{x0}" y="-300" width="{x1 - x0}" height="200" fill="url(#{pid})"/>', w=4, seed=748))
    return "".join(s)


# ───────────────────────────── пунктир шагов
def steps_path():
    """Дуги шагов по полу от дивана к кухне, потом вверх на столешницу к будильнику."""
    xs = np.linspace(P0[0], 2020, 13)
    arcs = []
    for a, b in zip(xs[:-1], xs[1:]):
        arcs.append([(a + (b - a) * u, -16 - 46 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 9)])
    # последний прыжок-стрелка на столешницу к будильнику
    a, b = (2020.0, -16.0), (AL[0] - 70, AL[1] - 40)
    arcs.append([(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u - 120 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 13)])
    return arcs


ARCS = steps_path()


def steps(t, k):
    u = clamp((t - T_DR) / (T_END - T_DR))
    n = len(ARCS)
    pos = n * ease_io(u) ** 0.9
    s = []
    for i, arc in enumerate(ARCS):
        f = clamp(pos - i)
        if f <= 0:
            break
        m = max(2, int(len(arc) * f + .5))
        pts = arc[:m]
        # пунктир: короткие куски по дуге
        P = np.array(pts)
        seg = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
        L = seg[-1]
        dash, gap = 26.0 * k, 18.0 * k
        d0 = 0.0
        while d0 < L:
            d1 = min(L, d0 + dash)
            q = [tuple(np.interp(dd, seg, P[:, 0]) for _ in (0,)) for dd in ()]
            q = [(float(np.interp(dd, seg, P[:, 0])), float(np.interp(dd, seg, P[:, 1]))) for dd in np.linspace(d0, d1, 4)]
            s.append(line(q, 9 * k, "#e2483a", taper=.2, wmin=.6, seed=800 + i, op=1.0))
            d0 = d1 + gap
        # след стопы в начале каждой дуги (на полу)
        x0, y0 = arc[0]
        if i < n - 1:
            s.append(blob(ellipse_pts(x0 + 8, y0 + 6, 20 * k, 7 * k, 10), "#e2483a", .9))
        if f < 1:
            continue
    # стрелка в конце
    if pos >= n - .02:
        arc = ARCS[-1]
        (xa, ya), (xb, yb) = arc[-2], arc[-1]
        ang = math.atan2(yb - ya, xb - xa)
        L = 46 * k
        for sgn in (-1, 1):
            a2 = ang + math.pi + sgn * .55
            s.append(line([(xb, yb), (xb + L * math.cos(a2), yb + L * math.sin(a2))], 10 * k, "#e2483a", taper=.2, wmin=.6, seed=820 + sgn))
    return "".join(s)


# ───────────────────────────── кадр
def cam(t):
    u = ease_io(clamp((t - T_A - .05) / (T_END + .2 - T_A)))
    ww = F.whip_in(t, T_A, .22)
    s0, s1 = 1.15, 0.47
    s = s0 * (s1 / s0) ** u
    cx = 420 + (1245 - 420) * u + 260 * ww
    cy = -360 + (-330 + 360) * u
    r = -1.4 * (1 - u) + .4 * math.sin(t * 1.2)
    return cx, cy, s, r


def frame(t):
    lib.DEFS.clear()
    cx, cy, s, r = cam(t)
    lib.INK_K[0] = ink_k(s)
    k = lib.INK_K[0]
    w = building() + flat_rooms(t)
    front = steps(t, k)
    # блик у будильника, когда пунктир дошёл
    e = t - T_END
    if e > -.05:
        a = ease_out(clamp((e + .05) / .18), 3)
        front += F.star(AL[0] - 50, AL[1] - 140, 80 * a * (1 + .12 * math.sin(e * 18)), e * 1.5)
    # Z над спящим
    for j in range(3):
        ph = (t * .6 + j / 3) % 1
        zx, zy = SOFA[0] + 190 + 50 * ph + 10 * math.sin(ph * 6 + j), -260 - 160 * ph
        sz = 26 + 26 * ph
        op = math.sin(math.pi * ph)
        zz = [(zx - sz / 2, zy - sz / 2), (zx + sz / 2, zy - sz / 2), (zx - sz / 2, zy + sz / 2), (zx + sz / 2, zy + sz / 2)]
        front += f'<g opacity="{op:.3f}">' + line(zz, 7 * k, "#3d4f7a", taper=.05, wmin=.9, seed=900 + j) + "</g>"
    o = ['<rect width="1080" height="1920" fill="#cfe6f2"/>', f'<g transform="{lib.cam(cx, cy, s, r)}">{w}{front}</g>', F.vignette()]
    return lib.svg("".join(o))


_ = (smooth, mix, ease_out)
