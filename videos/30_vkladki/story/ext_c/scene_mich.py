"""Мичиган рилса 30 (агент C), опыт Rubinstein, Meyer, Evans (2001). Без букв и цифр.
s09 (16.8–19.36): осень, корпус из красного кирпича с колоннами, клёны в рыжих листьях; на «Мичигане» (17.12) порыв —
     листья срываются, камера влетает в большое окно: внутри люди за партами решают задачи.
s10 (18.96–21.05): две парты: слева человек хватает карточки разных цветов вперемешку (на «вперемешку» 19.2 карточка
     в руке мелькает цветами), справа человек решает по одной из ровной стопки и на «по одной» (20.24) кладёт готовую с
     галочкой.
s12 (23.16–25.76): профессор Майер — седой, в очках и пиджаке, у доски; на «профессора Майера» (23.76–24.72)
     поворачивается и указкой показывает на доске рабочий день — полоску от солнца к луне."""
import math

import numpy as np

import lib
import person
import study28 as st28
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg, T)

_ST = {}
TRIM = st28.TRIM
T_MICH = 17.12
T_MIX = 19.2
T_ONE = 20.24
T_PROF = 23.76
LEAF = ["#e8742a", "#d9461f", "#f2a93a", "#c2341c", "#e9c046"]


# ═══════════════════════════════ s09: корпус осенью
GX0, GX1, GTOP, GBASE = 70, 1010, 470, 1160
WIN = (486, 640, 594, 832)
WC = ((WIN[0] + WIN[2]) / 2, (WIN[1] + WIN[3]) / 2)
WK = (WIN[2] - WIN[0]) / W


def sky():
    s = []
    lin_grad([(0, "#6aa8dc", 1), (.65, "#b6d6ee", 1), (1, "#f1e2c4", 1)], 0, 0, 0, 1, gid="gSky30")
    s.append(f'<rect x="-700" y="-700" width="{W + 1400}" height="{GBASE + 800}" fill="url(#gSky30)"/>')
    g = rad_grad([(0, "#fff4d0", .9), (.3, "#ffe8b0", .5), (1, "#ffe8b0", 0)], 860, 200, 420, 420)
    s.append(f'<rect x="-700" y="-700" width="{W + 1400}" height="{GBASE + 800}" fill="url(#{g})"/>')
    # дальний лес — осенние кроны
    pts = [(-700, GBASE - 40)]
    for k in range(26):
        x = -700 + k * 100
        pts.append((x + 50, GBASE - 120 - 40 * math.sin(k * 1.7) - 20 * math.sin(k * 3.1)))
    pts += [(1900, GBASE - 40), (1900, GBASE + 10, 1), (-700, GBASE + 10, 1)]
    s.append(shape(pts, "#c98a4a", blob([(-700, GBASE - 60), (1900, GBASE - 60), (1900, GBASE + 10), (-700, GBASE + 10)], "#b07238", .8), w=3.6, seed=3501))
    return "".join(s)


def clouds(t):
    s = []
    for k, (x0, y, sc, sp) in enumerate([(120, 240, 1.0, 18), (640, 130, .8, 12), (-200, 390, .9, 15)]):
        x = x0 + sp * (t - 17)
        pts = []
        for i in range(14):
            a = 2 * math.pi * i / 14
            r = 1 + .18 * math.sin(5 * a + k)
            pts.append((x + 110 * sc * math.cos(a) * r, y + 40 * sc * math.sin(a) * r * (0.75 if math.sin(a) > 0 else 1)))
        s.append(shape(pts, "#ffffff", blob(ellipse_pts(x + 20 * sc, y + 22 * sc, 90 * sc, 16 * sc, 10), "#d8e8f5"), w=3.6, seed=3510 + k))
    return "".join(s)


def building():
    s = []
    s.append(blob([(GX0 + 20, GBASE), (GX1 + 40, GBASE), (GX1 + 120, GBASE + 50), (GX0 + 80, GBASE + 50)], "#7a6a40", .45, blur(6)))
    # крыша — серый сланец, карниз
    roof = [(GX0 - 24, GTOP), (GX0 + 60, GTOP - 110), (GX1 - 60, GTOP - 110), (GX1 + 24, GTOP)]
    rin = blob([(GX0 + 60, GTOP - 110), (GX1 - 60, GTOP - 110), (GX1 - 50, GTOP - 92), (GX0 + 50, GTOP - 92)], "#7d8796")
    for k in range(5):
        y = GTOP - 20 - k * 20
        rin += line([(GX0 - 10 + k * 16, y), (GX1 + 10 - k * 16, y)], 3, "#454c58", seed=3520 + k, op=.7)
    s.append(shape(roof, "#5f6876", rin, w=4.6, seed=3521))
    # слуховые окошки на крыше
    for k, x in enumerate((260, 820)):
        s.append(shape([(x - 40, GTOP - 10, 1), (x - 40, GTOP - 70), (x, GTOP - 100), (x + 40, GTOP - 70), (x + 40, GTOP - 10, 1)], TRIM,
                       blob(rect_pts(x - 22, GTOP - 66, x + 22, GTOP - 16), "#7fa9d8"), w=3.6, seed=3525 + k))
    fac = rect_pts(GX0, GTOP, GX1, GBASE)
    inner = f'<rect x="{GX0}" y="{GTOP}" width="{GX1 - GX0}" height="{GBASE - GTOP}" fill="url(#pBrick)"/>'
    inner += blob([(GX1 - 80, GTOP), (GX1, GTOP), (GX1, GBASE), (GX1 - 40, GBASE)], st28.BRICK_DK, .35)
    inner += blob(rect_pts(GX0, GTOP, GX1, GTOP + 26), st28.BRICK_DK, .45)
    s.append(shape(fac, st28.BRICK, inner, w=5, seed=3530))
    s.append(shape(rect_pts(GX0 - 18, GTOP - 10, GX1 + 18, GTOP + 14), TRIM, blob(rect_pts(GX0 - 18, GTOP + 6, GX1 + 18, GTOP + 14), "#cfc6b4"), w=4, seed=3531))
    s.append(shape(rect_pts(GX0 - 10, GBASE - 40, GX1 + 10, GBASE), "#d9cfbd", blob(rect_pts(GX0 - 10, GBASE - 14, GX1 + 10, GBASE), "#b9ae99"), w=4, seed=3532))
    for k, x in enumerate([140, 250, 830, 940]):
        s.append(st28.win(x, 560, 680, seed=3540 + k * 10))
        s.append(st28.win(x, 790, 910, seed=3580 + k * 10))
    # портик с колоннами вокруг большого окна
    PX0, PX1 = 360, 720
    s.append(shape([(PX0 - 30, 560), (540, 486), (PX1 + 30, 560)], TRIM, blob([(PX0 + 10, 552), (540, 506), (PX1 - 10, 552)], "#e3dccd"), w=4.4, seed=3600))
    s.append(shape(rect_pts(PX0 - 30, 560, PX1 + 30, 584), TRIM, "", w=4, seed=3601))
    s.append(shape(ellipse_pts(540, 536, 16, 16, 12), "#d9cfbd", blob(ellipse_pts(540, 536, 8, 8, 8), "#b9ae99"), w=2.6, seed=3602))
    x0, y0, x1, y1 = WIN
    s.append(shape(rect_pts(x0 - 16, y0 - 16, x1 + 16, y1 + 16, 4), TRIM, blob(rect_pts(x0 - 16, y1, x1 + 16, y1 + 16), "#d6cdb9"), w=4, seed=3603))
    s.append(shape(rect_pts(x0 - 26, y1 + 16, x1 + 26, y1 + 30), TRIM, "", w=3.4, seed=3604))
    for x in (PX0, PX0 + 56, PX1 - 56, PX1):
        col = rect_pts(x - 15, 584, x + 15, GBASE - 40)
        s.append(shape(col, TRIM, blob(rect_pts(x + 4, 584, x + 15, GBASE - 40), "#d4cbb8") +
                       line([(x - 5, 594), (x - 5, GBASE - 50)], 2, "#cfc6b4", seed=3605 + x), w=3.4, seed=3606 + x))
        s.append(shape(rect_pts(x - 21, 580, x + 21, 594), TRIM, "", w=3, seed=3607 + x))
        s.append(shape(rect_pts(x - 21, GBASE - 54, x + 21, GBASE - 40), TRIM, "", w=3, seed=3608 + x))
    door = [(500, GBASE - 40, 1), (500, 950), (540, 918), (580, 950), (580, GBASE - 40, 1)]
    s.append(shape(door, "#5a3524", blob([(540, 918), (580, 950), (580, GBASE - 40), (548, GBASE - 40)], "#3f2418") +
                   line([(540, 926), (540, GBASE - 44)], 2.6, "#2a160e", seed=3610), w=3.6, seed=3611))
    for j in range(3):
        s.append(shape(rect_pts(PX0 - 40 - j * 14, GBASE - 40 + j * 14, PX1 + 40 + j * 14, GBASE - 26 + j * 14), "#ece4d4", "", w=3.2, seed=3612 + j))
    return "".join(s)


def ground():
    s = []
    lin_grad([(0, "#8fae4a", 1), (1, "#6f8f36", 1)], 0, 0, 0, 1, gid="gGrass30")
    s.append(f'<rect x="-700" y="{GBASE - 6}" width="{W + 1400}" height="{H + 700}" fill="url(#gGrass30)"/>')
    s.append(line([(-600, GBASE - 6), (W + 600, GBASE - 6)], 4, INK, taper=.1, wmin=.8, seed=3620))
    path = [(470, GBASE + 2), (610, GBASE + 2), (820, H + 400, 1), (260, H + 400, 1)]
    s.append(shape(path, "#d9cfbd", blob([(600, GBASE), (820, H + 400), (700, H + 400), (580, GBASE)], "#c2b79f", .9), w=4, seed=3621))
    rs = np.random.RandomState(30)
    for k in range(70):       # опавшие листья на траве
        x, y = rs.uniform(-300, W + 300), rs.uniform(GBASE + 30, 1900)
        if 330 < x < 760 and rs.rand() < .8:
            continue
        r = rs.uniform(7, 13) * (0.7 + 0.5 * (y - GBASE) / 700)
        s.append(blob(ellipse_pts(x, y, r, r * .55, 8, rot=rs.uniform(0, 180)), LEAF[k % 5]))
    return "".join(s)


def leaf_pts(x, y, r, rot):
    """Кленовый лист: три больших лопасти и две малых, у каждой — зубцы, между ними выемки; черешок вниз."""
    lobes = [(-90, 1.0), (-35, .86), (-145, .86), (25, .55), (155, .55)]
    lobes.sort(key=lambda q: q[0])
    pts = []
    angs = [q[0] for q in lobes]
    for i, (a, L) in enumerate(lobes):
        for da, rr, sharp in ((-16, .62, 0), (-9, .8, 1), (0, 1.0, 1), (9, .8, 1), (16, .62, 0)):
            aa = math.radians(a + da)
            pts.append((r * L * rr * math.cos(aa), r * L * rr * math.sin(aa)) + ((1,) if sharp else ()))
        nxt = angs[(i + 1) % len(angs)] + (360 if i == len(angs) - 1 else 0)
        mid = math.radians((a + nxt) / 2)
        rm = .16 if i == len(angs) - 1 else .34
        pts.append((r * rm * math.cos(mid), r * rm * math.sin(mid)))
    return T(pts, x, y, 1.0, rot)


def leaf(x, y, r, rot, col, sd, flip=1.0):
    pts = leaf_pts(0, 0, r, 0)
    pts = [(p[0] * flip,) + tuple(p[1:]) for p in pts]
    pts = T(pts, x, y, 1.0, rot)
    a = math.radians(rot)
    vein = line([(x, y), (x - math.sin(a) * r * .9, y + math.cos(a) * r * .9)], max(1.2, r * .07), lib.mul(col, (.7, .6, .6)), seed=sd, taper=.3)
    return shape(pts, col, "", w=max(1.6, r * .09), seed=sd) + vein


def maple(x, y, h, sd, t, gust):
    """Клён: ствол и крона из рыжих пятен-облаков, качается; gust 0..1 — сила порыва (крона клонится вправо)."""
    s = []
    sway = 6 * math.sin(t * 1.6 + sd) + 26 * gust
    trunk = lib.band([(x, y + 4), (x + sway * .1, y - h * .45), (x + sway * .3, y - h * .7)], h * .09, h * .05, step=6, cap=True)
    tin = blob(lib.band([(x + h * .025, y), (x + h * .025 + sway * .1, y - h * .45), (x + h * .02 + sway * .3, y - h * .7)], h * .04, h * .02, step=6, cap=False), "#4a2e1e", .9)
    s.append(shape(trunk, "#6b4430", tin, w=4, seed=sd))
    for k, (dx, ang) in enumerate([(-1, -40), (1, 35)]):
        bx, by = x + sway * .15, y - h * .5
        ex, ey = bx + dx * h * .22 + sway * .4, by - h * .25
        s.append(line([(bx, by), (ex, ey)], h * .035, INK, taper=.3, seed=sd + 2 + k))
        s.append(line([(bx, by), (ex, ey)], h * .02, "#6b4430", taper=.3, seed=sd + 4 + k))
    cx, cy = x + sway * .5, y - h * .85
    blobs = [(-0.32, 0.05, .30), (0.30, 0.02, .30), (0, -0.22, .34), (-0.18, -0.4, .24), (0.2, -0.38, .25), (0, 0.12, .28)]
    for k, (u, v, r) in enumerate(blobs):
        bx, by = cx + u * h + sway * .2 * (v + .5), cy + v * h
        rr = r * h
        pts = []
        for i in range(16):
            a = 2 * math.pi * i / 16
            q = 1 + .12 * math.sin(5 * a + k * 1.3 + sd) + .05 * math.sin(t * 3 + i + k)
            pts.append((bx + rr * q * math.cos(a), by + rr * .86 * q * math.sin(a)))
        col = LEAF[(k + sd) % 5]
        inner = blob(ellipse_pts(bx + rr * .25, by + rr * .3, rr * .8, rr * .55, 12), lib.mul(col, (.8, .7, .7)), .85)
        inner += blob(ellipse_pts(bx - rr * .3, by - rr * .35, rr * .35, rr * .2, 10), mix(col, "#ffffff", .3), .8)
        s.append(shape(pts, col, inner, w=4, seed=sd + 10 + k))
    return "".join(s)


def flying_leaves(t, gust_t, n, seed, area, wind=1.0, scale=1.0):
    """Листья летят: до порыва — редкие медленные, после порыва — рой сорванных с крон вправо-вверх, потом вниз."""
    rs = np.random.RandomState(seed)
    s = []
    for k in range(n):
        x0, y0 = rs.uniform(*area[0]), rs.uniform(*area[1])
        start = gust_t + rs.uniform(-0.05, 0.35) if k >= n // 4 else gust_t - 1.0 + rs.uniform(-.6, .3)
        e = t - start
        if e < 0:
            continue
        vx = rs.uniform(500, 1100) * wind if k >= n // 4 else rs.uniform(40, 120)
        vy = -rs.uniform(150, 420) if k >= n // 4 else rs.uniform(60, 120)
        x = x0 + vx * e * (1 - 0.25 * e) + 30 * math.sin(e * 6 + k)
        y = y0 + vy * e + 220 * e * e
        r = rs.uniform(22, 36) * scale
        rot = rs.uniform(0, 360) + e * rs.uniform(200, 600)
        flip = math.cos(e * rs.uniform(5, 11) + k)
        if abs(flip) < .15:
            flip = .15 if flip >= 0 else -.15
        s.append(leaf(x, y, r, rot, LEAF[k % 5], 3700 + k, flip))
    return "".join(s)


# ─── аудитория (координаты 1080×1920, внутри окна)
FLOOR_I = 1000


def classroom_back():
    s = []
    lin_grad([(0, "#f1e4c6", 1), (1, "#e6d3ad", 1)], 0, 0, 0, 1, gid="gWallM")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR_I + 900}" fill="url(#gWallM)"/>')
    lin_grad([(0, "#b9824e", 1), (1, "#a0693c", 1)], 0, 0, 0, 1, gid="gFloorM")
    s.append(f'<rect x="-900" y="{FLOOR_I}" width="{W + 1800}" height="{H + 900}" fill="url(#gFloorM)"/>')
    for k in range(-6, 16):
        x = 540 + k * 110
        s.append(line([(540 + (x - 540) * .35, FLOOR_I), (540 + (x - 540) * 2.6, H + 400)], 2.4, "#8a5a32", taper=.1, wmin=.8, seed=3800 + k, op=.7))
    s.append(line([(-900, FLOOR_I), (W + 900, FLOOR_I)], 4, INK, taper=.05, wmin=.9, seed=3820))
    s.append(blob(rect_pts(-900, FLOOR_I - 34, W + 900, FLOOR_I), "#c9a77a"))
    # доска: меловые фигуры-задачи (без букв)
    s.append(shape(rect_pts(250, 300, 830, 640, 6), "#2f5a46", blob(rect_pts(250, 560, 830, 640), "#284e3d", .6) +
                   blob([(270, 320), (420, 320), (300, 520)], "#3a6c55", .5), w=5, seed=3830))
    s.append(shape(rect_pts(236, 290, 844, 304), "#a87c4c", "", w=3.2, seed=3831))
    s.append(shape(rect_pts(236, 636, 844, 656), "#a87c4c", "", w=3.2, seed=3832))
    for k, x in enumerate([360, 540, 720]):
        c = ["#ffb3a0", "#9fd0ff", "#c8f0a0"][k]
        s.append(line([(x - 50, 420), (x + 50, 418), (x + 52, 500), (x - 48, 502), (x - 50, 418)], 6, c, taper=.1, wmin=.7, seed=3840 + k))
        s.append(line([(x - 28, 460), (x + 28, 460)], 6, "#eef4ea", taper=.3, seed=3845 + k))
    # окна с клёнами
    for k, x in enumerate([60, 1020]):
        tree = "".join(blob(ellipse_pts(x - 30 + dx, 560 + dy, 70, 56, 14), LEAF[(i + k) % 5]) for i, (dx, dy) in enumerate([(-30, 0), (40, -30), (10, 40)]))
        s.append(shape(rect_pts(x - 110, 260, x + 110, 760, 4), "#a8d2f0",
                       blob(rect_pts(x - 110, 660, x + 110, 760), "#8fae4a") + blob(rect_pts(x - 40, 600, x - 20, 700), "#6b4430") + tree +
                       blob([(x - 110, 420), (x + 110, 300), (x + 110, 360), (x - 110, 480)], "#ffffff", .45), w=5, seed=3860 + k))
        s.append(line([(x, 260), (x, 760)], 5, TRIM, taper=.05, wmin=.9, seed=3870 + k))
        s.append(shape(rect_pts(x - 124, 760, x + 124, 780), TRIM, "", w=3.2, seed=3872 + k))
    s.append(shape(ellipse_pts(540, 190, 52, 52, 24), "#fbf8ee", blob(ellipse_pts(548, 198, 48, 48, 18), "#e6dfcc", .7), w=5, seed=3880))
    return "".join(s)


def classroom(t):
    s = [_ST["cls_back"], st28.clock_hands(t)]
    n = 0
    for r, (yb, sc, xs, dw) in enumerate(st28.ROWS):
        depth = dw * .30
        floor = yb + depth + 320 * sc
        for j, x in enumerate(xs):
            spec = st28.STUDENTS[(n * 4 + 1) % len(st28.STUDENTS)]
            ph = n * 1.7
            body, arms = st28.student(spec, x, yb, sc, t, ph, 1500 + n * 100)
            s.append(body)
            s.append(st28.desk_surface(x, yb, dw, depth, 1400 + n * 10))
            prog = clamp((t - 17.2 - n * 0.13) / 2.2) * 7 + 1
            s.append(st28.paper(x + dw * .02, yb + depth * .58, dw * .40, depth * .62, prog, sd=n))
            s.append(arms)
            s.append(st28.desk_front(x, yb, dw, depth, floor, 1450 + n * 10))
            n += 1
    return "".join(s)


def s09(t):
    gust = smooth(T_MICH - .05, T_MICH + .25, t) * (1 - 0.6 * smooth(T_MICH + .6, T_MICH + 1.6, t))
    # камера: 16.8 мягкий наезд на фасад (движение с кадра 0), удар на «Мичигане», 17.45–18.15 влёт в окно, дальше — внутри
    zin = ease_in(clamp((t - 17.45) / 0.7), 2.2) * 0.35 + 0.65 * ease_io(clamp((t - 17.45) / 0.7))
    s_end = 1.05 / WK
    if zin < 1:
        s0 = 0.98 + 0.10 * ease_out(clamp((t - 16.8) / 0.65), 2)
        e = t - T_MICH
        if e > 0:
            s0 *= 1 + 0.03 * math.exp(-e * 7) * math.sin(min(e * 14, math.pi))
        S = s0 * (s_end / s0) ** zin
        c0 = (540, 880)
        k = (1 - s0 / S) / (1 - s0 / s_end) if S > s0 + 1e-6 else 0.0
        cx = c0[0] + (WC[0] - c0[0]) * k
        cy = c0[1] + (WC[1] - c0[1]) * k
        inside = f'<g transform="translate({WIN[0]} {f(WC[1] - H * WK / 2)}) scale({WK:.6f})">{classroom(t)}</g>'
        cl = lib.clip_rect(WIN[0], WIN[1], WIN[2] - WIN[0], WIN[3] - WIN[1])
        glare = blob([(WIN[0], WIN[1] + 60), (WIN[2], WIN[1] + 10), (WIN[2], WIN[1] + 40), (WIN[0], WIN[1] + 90)], "#ffffff", .35 * (1 - zin))
        art = (_ST["sky"] + clouds(t) + _ST["ground"] + _ST["bld"] + f'<g clip-path="url(#{cl})">{inside}{glare}</g>' +
               shape(rect_pts(*WIN), "none", "", w=3.6, seed=3999) +
               maple(20, GBASE + 150, 520, 3900, t, gust) + maple(1070, GBASE + 120, 480, 3950, t, gust) +
               flying_leaves(t, T_MICH, 64, 7, ((-150, 1150), (480, 1000)), 1.0, 1.0))
        return art, cam(cx, cy, S, 0.8 * (1 - zin) - 0.6 * gust * (1 - zin)), "#9cc8ee"
    u = clamp((t - 18.15) / 1.4)
    inside = classroom(t)
    # залетевшие с ветром листья ещё кружат перед камерой
    lv = flying_leaves(t, T_MICH + 0.75, 6, 11, ((-300, 100), (200, 600)), 1.2, 2.2)
    return inside + lv, cam(540, 940 - 30 * u, 1.05 + 0.09 * (0.5 * u + 0.5 * ease_io(u)), -0.5 * u), "#e6d3ad"


# ═══════════════════════════════ s10: две парты
CARD_C = ["#e2543f", "#3f6fb5", "#3cbf63", "#e8b23a", "#7a4fb0"]
DESKS = [(330, 300), (755, 300)]      # (x, ширина)
YB10, SC10 = 1010, 0.95


def card(x, y, w, h, col, rot, sd, check=0.0, shape_k=0, done=False):
    """Карточка задачи: цветная рамка, белое поле с фигурой-задачей (без букв); check — зелёная галочка (0..1)."""
    s = []
    inner = blob(rect_pts(x - w / 2 + w * .1, y - h / 2 + h * .14, x + w / 2 - w * .1, y + h / 2 - h * .14, 4), "#fbf8ee")
    k = ["circle", "tri", "square", "star"][shape_k % 4]
    inner += st28.mini_shape(k, x - w * .18, y, h * .18, col, sd + 3)
    inner += f'<rect x="{f(x + w * .02)}" y="{f(y - h * .05)}" width="{f(w * .26)}" height="{f(h * .1)}" rx="2" fill="#9aa6c4"/>'
    if done:
        inner += blob(rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2), "#ffffff", .25)
    s.append(shape(rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 6), col, inner, w=3.2, seed=sd))
    out = f'<g transform="rotate({f(rot)} {f(x)} {f(y)})">{"".join(s)}</g>'
    if check > 0.01:
        c = back_out(clamp(check), 2.4)
        cx, cy = x + w * .22, y - h * .05
        pts = [(cx - 26 * c, cy), (cx - 8 * c, cy + 18 * c), (cx + 30 * c, cy - 26 * c)]
        out += line(pts, 15 * max(c, .3), INK, taper=.15, wmin=.7, seed=sd + 7) + line(pts, 9 * max(c, .3), "#3cbf63", taper=.15, wmin=.7, seed=sd + 8)
    return out


SPEC_L = dict(skin="#f2c9a8", hair="curly", hair_c="#7a4a2a", top="#e07a2e", low="#3a3040", face=.25)
SPEC_R = dict(skin="#a8704c", hair="short", hair_c="#2a1a14", top="#2f8a8a", low="#1f3a2c", face=-.2, glasses=True)


def chaos_person(t, x, yb, sc):
    """Слева: хватает карточки вперемешку — правая рука держит карточку, которая мелькает цветами, левая шарит по столу,
    голова мечется, брови домиком, рот волной, капля пота."""
    e = t - T_MIX
    flash = clamp((t - 19.12) / 0.8) * (1 - smooth(19.95, 20.1, t))
    grab = 0.5 + 0.5 * math.sin(t * 9.5)
    look_x = 0.7 * math.sin(t * 7.3) + 0.3 * math.sin(t * 13)
    pose = {"no_legs": True,
            "hand_target": {"L": (-50 - 45 * grab, -300 + 10 * math.sin(t * 11))},
            "arms": {"R": (52 + 8 * math.sin(t * 6), 100 + 14 * math.sin(t * 6 + 1) + 12 * flash)},
            "curl": {"L": 0.2 + 0.5 * grab, "R": 0.7},
            "look": (look_x, 0.3),
            "brow": -0.8, "mouth": "wavy",
            "head_tilt": 7 * math.sin(t * 5.1)}
    idx = int((t - 18.9) * (13 if flash > .1 else 3)) % 5
    w, h = 108, 78

    def held(hn, a):
        ar = math.radians(a)
        return card(hn[0] + math.cos(ar) * 62, hn[1] + math.sin(ar) * 62, w, h, CARD_C[idx], a + 90 + 8 * math.sin(t * 8), 4000 + idx, shape_k=idx)
    pose["in_hand"] = {"R": held}
    spec = dict(SPEC_L)
    spec["face"] = .25 + .15 * math.sin(t * 6.1)
    feet = yb + 330 * sc
    breath = 3 * math.sin(t * 4.2)
    body = person.draw(spec, dict(pose, no_arms=True), x, feet + breath * sc, sc, sd=4100)
    arms = person.draw(spec, dict(pose, only_arms=True), x, feet + breath * sc, sc, sd=4100)
    # капля пота у виска
    hx, hy = x + 70 * sc, feet - 640 * sc + breath * sc
    dy = 30 * ((t * 1.3) % 1)
    sweat = shape([(hx, hy + dy - 22), (hx + 11, hy + dy + 2), (hx, hy + dy + 12), (hx - 11, hy + dy + 2)], "#9fd8ff",
                  blob(ellipse_pts(hx - 3, hy + dy - 1, 3, 5, 8), "#ffffff"), w=2.6, seed=4150)
    return body, arms, sweat, flash


def calm_person(t, x, yb, sc):
    """Справа: решает по одной — пишет на карточке перед собой, на «по одной» кладёт её на стопку готовых."""
    move = smooth(T_ONE - 0.32, T_ONE, t)
    back = smooth(T_ONE + 0.25, T_ONE + 0.6, t)
    wph = t * 7.5
    jx, jy = (8 * math.sin(wph) + 4 * math.sin(wph * 2.3), 3 * math.cos(wph * 1.3))
    write = 1 - move
    # правая рука (на экране справа): пишет → несёт карточку к стопке готовых → возвращается к стопке задач
    rx = (40 + jx * write) * (1 - move) + 85 * move
    ry = (-300 + jy * write) * (1 - move) + (-322) * move - 50 * math.sin(math.pi * move)
    rx = rx * (1 - back) + 40 * back
    ry = ry * (1 - back) + -300 * back
    pose = {"no_legs": True,
            "hand_target": {"R": (rx, ry), "L": (-70, -300)},
            "curl": {"L": 0.15, "R": 0.75},
            "look": (0.4 * move + 0.05 * math.sin(t), 0.8 - 0.2 * move),
            "brow": 0.3, "mouth": "smile",
            "head_tilt": -3 + 2 * math.sin(t * .8) + 4 * move,
            "blink": max(0.0, 1 - abs((t % 2.7) - 1.3) / 0.07)}
    if t < T_ONE - 0.32 or back > .99:
        pose["over_hand"] = {"R": lambda h, a: st28.pencil_item(h, a, 1.0)}
    elif t < T_ONE:
        def carry(h, a):
            ar = math.radians(a)
            return card(h[0] + math.cos(ar) * 40, h[1] + math.sin(ar) * 40, 90, 64, "#3f6fb5", -2 + 7 * move, 4640, shape_k=1)
        pose["in_hand"] = {"R": carry}
    feet = yb + 330 * sc
    breath = 2 * math.sin(t * 2.2)
    body = person.draw(SPEC_R, dict(pose, no_arms=True), x, feet + breath * sc, sc, sd=4200)
    arms = person.draw(SPEC_R, dict(pose, only_arms=True), x, feet + breath * sc, sc, sd=4200)
    return body, arms, move, back, (rx, ry), feet + breath * sc


def wall10():
    s = []
    lin_grad([(0, "#f1e4c6", 1), (1, "#e6d3ad", 1)], 0, 0, 0, 1, gid="gWallT")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{1300 + 900}" fill="url(#gWallT)"/>')
    lin_grad([(0, "#b9824e", 1), (1, "#a0693c", 1)], 0, 0, 0, 1, gid="gFloorT")
    fl = 1300
    s.append(f'<rect x="-900" y="{fl}" width="{W + 1800}" height="{H + 900}" fill="url(#gFloorT)"/>')
    for k in range(-8, 18):
        x = 540 + k * 120
        s.append(line([(540 + (x - 540) * .7, fl), (540 + (x - 540) * 2.2, H + 400)], 2.4, "#8a5a32", taper=.1, wmin=.8, seed=4300 + k, op=.7))
    s.append(line([(-900, fl), (W + 900, fl)], 4, INK, taper=.05, wmin=.9, seed=4320))
    s.append(blob(rect_pts(-900, fl - 34, W + 900, fl), "#c9a77a"))
    # окно с клёном между ними, часы
    x = 540
    tree = "".join(blob(ellipse_pts(x - 10 + dx, 520 + dy, 90, 70, 14), LEAF[i % 5]) for i, (dx, dy) in enumerate([(-50, 0), (50, -40), (20, 50), (-60, 70)]))
    s.append(shape(rect_pts(x - 150, 300, x + 150, 760, 4), "#a8d2f0", blob(rect_pts(x - 150, 670, x + 150, 760), "#8fae4a") +
                   blob(rect_pts(x - 20, 580, x + 4, 700), "#6b4430") + tree + blob([(x - 150, 440), (x + 150, 330), (x + 150, 390), (x - 150, 500)], "#ffffff", .4),
                   w=5, seed=4330))
    s.append(line([(x, 300), (x, 760)], 5, TRIM, taper=.05, wmin=.9, seed=4331))
    s.append(shape(rect_pts(x - 166, 760, x + 166, 782), TRIM, "", w=3.2, seed=4332))
    s.append(shape(ellipse_pts(x, 190, 50, 50, 24), "#fbf8ee", blob(ellipse_pts(x + 8, 198, 46, 46, 18), "#e6dfcc", .7), w=5, seed=4333))
    return "".join(s)


def messy_cards(t, x, y, flash):
    """Рассыпанные карточки разных цветов на левой парте; на «вперемешку» подскакивают и перемешиваются."""
    rs = np.random.RandomState(41)
    s = []
    for k in range(7):
        bx, by = x + rs.uniform(-120, 120), y + rs.uniform(-22, 28)
        rot = rs.uniform(-35, 35)
        hop = 0.0
        if flash > 0.01:
            ph = (t * 6 + k * .37) % 1
            hop = 26 * flash * math.sin(math.pi * ph)
            rot += 40 * flash * math.sin(t * 9 + k)
            bx += 22 * flash * math.sin(t * 7 + k * 2)
        s.append(card(bx, by - hop, 82, 58, CARD_C[k % 5], rot, 4400 + k, shape_k=k))
    return "".join(s)


def s10(t):
    s = [_ST["wall10"]]
    depth = 300 * .30
    fl = 1300
    xl, xr = DESKS[0][0], DESKS[1][0]
    bodyL, armsL, sweat, flash = chaos_person(t, xl - 10, YB10, SC10)
    bodyR, armsR, move, back, rh, feetR = calm_person(t, xr + 10, YB10, SC10)
    # левая парта
    s.append(bodyL)
    s.append(st28.desk_surface(xl, YB10, 320, depth, 4500))
    s.append(messy_cards(t, xl - 10, YB10 + depth * .5, flash))
    s.append(armsL)
    s.append(st28.desk_front(xl, YB10, 320, depth, fl, 4510))
    s.append(sweat)
    # правая парта: ровная стопка задач одного цвета, готовые — справа с галочками
    s.append(bodyR)
    s.append(st28.desk_surface(xr, YB10, 320, depth, 4600))
    blue = "#3f6fb5"
    sx, sy = xr - 105, YB10 + depth * .55
    for k in range(6):
        s.append(card(sx, sy - k * 5, 82, 58, blue, -4, 4610 + k, shape_k=k))
    dx, dy = xr + 112, YB10 + depth * .56
    ndone = 2 + (1 if t >= T_ONE else 0)
    for k in range(2):
        s.append(card(dx, dy - k * 5, 82, 58, blue, 5 - 3 * k, 4630 + k, check=1.0, shape_k=k + 2, done=True))
    # текущая карточка: перед человеком, потом летит в руке к готовым
    if t < T_ONE - 0.32:
        s.append(card(xr + 5, YB10 + depth * .6, 90, 64, blue, -2, 4640, shape_k=1))
    elif t < T_ONE:
        pass                    # карточка в руке (calm_person)
    else:
        e = t - T_ONE
        bounce = 6 * math.exp(-e * 12) * abs(math.sin(e * 30))
        s.append(card(dx, dy - 10 - bounce, 90, 64, blue, 5, 4640, check=clamp(e / 0.22), shape_k=1, done=False))
        if e < 0.35:
            for k in range(6):
                a = k * math.pi / 3 + .3
                r0 = 60 + 50 * ease_out(e / .35)
                L = 24 * (1 - e / .35)
                s.append(line([(dx + math.cos(a) * r0, dy - 10 + math.sin(a) * r0 * .7), (dx + math.cos(a) * (r0 + L), dy - 10 + math.sin(a) * (r0 + L) * .7)],
                              6, "#3cbf63", taper=.5, seed=4650 + k))
    s.append(armsR)
    s.append(st28.desk_front(xr, YB10, 320, depth, fl, 4660))
    _ = ndone
    u = clamp((t - 18.96) / 2.09)
    push = 0.025 * math.exp(-max(t - T_ONE, 0) * 6) * (t > T_ONE) + 0.02 * math.exp(-max(t - T_MIX, 0) * 6) * (t > T_MIX)
    shake = 4 * flash * math.sin(t * 47)
    return "".join(s), cam(540 + 14 * ease_io(u) + shake, 960 - 10 * u, 1.42 + 0.05 * ease_io(u) + push, 0.5 - 0.9 * u), "#e6d3ad"


# ═══════════════════════════════ s12: профессор у доски
BOARD = (20, 540, 1060, 1180)       # x0, y0, x1, y1
BAR = (190, 860, 520, 940)          # полоска рабочего дня на доске
PROF = dict(skin="#efc7a6", hair="short", hair_c="#dcdce2", top="#6b5442", low="#3a3440", face=-.3, glasses=True, mustache=True,
            jacket="#b8433a", brow_c="#cfcfd6", bw=1.08, h=1.0)


def board(t, fill):
    x0, y0, x1, y1 = BOARD
    s = []
    s.append(shape(rect_pts(x0, y0, x1, y1, 6), "#2f5a46", blob(rect_pts(x0, y1 - 90, x1, y1), "#284e3d", .6) +
                   blob([(x0 + 20, y0 + 20), (x0 + 260, y0 + 20), (x0 + 60, y0 + 300)], "#3a6c55", .45) +
                   "".join(line([(x0 + 80 + k * 210, y0 + 60 + 40 * (k % 2)), (x0 + 200 + k * 210, y0 + 52 + 40 * (k % 2))], 4, "#5f8f78", seed=4700 + k, op=.8)
                           for k in range(4)), w=5, seed=4710))
    s.append(shape(rect_pts(x0 - 14, y0 - 14, x1 + 14, y0 + 2), "#a87c4c", "", w=3.2, seed=4711))
    s.append(shape(rect_pts(x0 - 18, y1 - 4, x1 + 18, y1 + 18), "#a87c4c", blob(rect_pts(x0 - 18, y1 + 8, x1 + 18, y1 + 18), "#8a5a36"), w=3.2, seed=4712))
    s.append(shape(rect_pts(x0 + 120, y1 - 16, x0 + 170, y1 - 2, 3), "#f4f1ea", "", w=2.4, seed=4713))
    s.append(shape(rect_pts(x0 + 190, y1 - 16, x0 + 230, y1 - 2, 3), "#ffd0d0", "", w=2.4, seed=4714))
    # полоска рабочего дня мелом: солнце слева, луна справа, деления
    bx0, by0, bx1, by1 = BAR
    if fill > 0.001:
        xf = bx0 + (bx1 - bx0) * fill
        s.append(blob(rect_pts(bx0 + 4, by0 + 4, xf, by1 - 4), "#e9d79a"))
        for k in range(int((xf - bx0) / 22)):       # меловая штриховка
            xx = bx0 + 10 + k * 22
            s.append(line([(xx, by1 - 8), (xx + 16, by0 + 8)], 3, "#f6edc8", taper=.2, seed=4720 + k, op=.9))
    s.append(line([(bx0, by0), (bx1, by0 + 2), (bx1 + 2, by1), (bx0 - 2, by1 - 1), (bx0, by0)], 7, "#f1f4ee", taper=.05, wmin=.7, seed=4730))
    for k in range(1, 8):
        xx = bx0 + (bx1 - bx0) * k / 8
        s.append(line([(xx, by1 - 4), (xx, by1 + 22)], 5, "#f1f4ee", taper=.3, seed=4740 + k))
    # солнце мелом
    sx, sy = bx0 + 40, by0 - 100
    s.append(line([(sx + 34 * math.cos(a), sy + 34 * math.sin(a)) for a in np.linspace(0, 6.5, 22)], 6, "#ffe27a", taper=.1, wmin=.7, seed=4750))
    for k in range(8):
        a = k * math.pi / 4 + 0.2 * math.sin(t * 2)
        s.append(line([(sx + 46 * math.cos(a), sy + 46 * math.sin(a)), (sx + 64 * math.cos(a), sy + 64 * math.sin(a))], 5, "#ffe27a", taper=.4, seed=4751 + k))
    # луна мелом
    mx, my = bx1 - 30, by0 - 100
    outer = [(mx + 40 * math.cos(a), my + 40 * math.sin(a)) for a in np.linspace(math.radians(60), math.radians(300), 18)]
    inner = [(mx + 18 + 32 * math.cos(a), my - 4 + 32 * math.sin(a)) for a in np.linspace(math.radians(260), math.radians(100), 14)]
    s.append(blob(outer + inner, "#c8d8ff", .9))
    s.append(blob(ellipse_pts(mx - 22, my + 8, 5, 4, 8), "#9fb4e0") + blob(ellipse_pts(mx - 14, my - 18, 4, 3, 8), "#9fb4e0"))
    for k, (ax, ay) in enumerate([(mx + 60, my - 30), (mx - 50, my + 30)]):
        s.append(line([(ax - 8, ay), (ax + 8, ay)], 4, "#c8d8ff", seed=4762 + k) + line([(ax, ay - 8), (ax, ay + 8)], 4, "#c8d8ff", seed=4764 + k))
    return "".join(s)


def wall12():
    s = []
    lin_grad([(0, "#efe0c0", 1), (1, "#e3cfa6", 1)], 0, 0, 0, 1, gid="gWall12")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{1480 + 900}" fill="url(#gWall12)"/>')
    lin_grad([(0, "#b9824e", 1), (1, "#a0693c", 1)], 0, 0, 0, 1, gid="gFloor12")
    s.append(f'<rect x="-900" y="1480" width="{W + 1800}" height="{H + 900}" fill="url(#gFloor12)"/>')
    s.append(line([(-900, 1480), (W + 900, 1480)], 4, INK, taper=.05, wmin=.9, seed=4800))
    s.append(blob(rect_pts(-900, 1446, W + 900, 1480), "#c9a77a"))
    # часы без цифр и рамка с мелким рисунком мозга (без букв)
    s.append(shape(ellipse_pts(300, 410, 56, 56, 24), "#fbf8ee", blob(ellipse_pts(308, 418, 50, 50, 18), "#e6dfcc", .7) +
                   "".join(blob(ellipse_pts(300 + 42 * math.cos(k * math.pi / 6), 410 + 42 * math.sin(k * math.pi / 6), 3, 3, 6), "#5a5f6e") for k in range(12)) +
                   line([(300, 410), (300, 374)], 5, INK, taper=.3, seed=4820) + line([(300, 410), (326, 424)], 6, INK, taper=.3, seed=4821), w=5, seed=4822))
    s.append(shape(rect_pts(560, 330, 700, 470, 4), "#7a5236", blob(rect_pts(574, 344, 686, 456), "#fbf3e0") +
                   blob(ellipse_pts(630, 400, 36, 28, 14), "#f2a7b8") + line([(630, 374), (626, 426)], 3, "#c46a80", seed=4823) +
                   line([(604, 392), (618, 404), (606, 416)], 3, "#c46a80", seed=4824) + line([(656, 392), (642, 404), (654, 416)], 3, "#c46a80", seed=4825),
                   w=4, seed=4826))
    # стол профессора справа: стопка книг, кружка
    s.append(shape(rect_pts(760, 1250, 1180, 1290, 4), "#9a6a3e", blob(rect_pts(760, 1276, 1180, 1290), "#7a5232"), w=4, seed=4810))
    s.append(shape(rect_pts(780, 1290, 1160, 1480), "#a87c4c", blob(rect_pts(980, 1290, 1160, 1480), "#8a5a36", .8), w=4, seed=4811))
    for k, (h_, c) in enumerate([(30, "#3f6fb5"), (26, "#e2543f"), (34, "#3cbf63")]):
        y = 1250 - sum([30, 26, 34][:k + 1])
        s.append(shape(rect_pts(830 + k * 6, y, 1000 - k * 4, y + h_, 3), c, blob(rect_pts(830 + k * 6, y + h_ * .6, 1000 - k * 4, y + h_), lib.mul(c, (.8, .8, .85)), .9),
                       w=3, seed=4812 + k))
    return "".join(s)


def prof(t):
    """Профессор: до T_PROF — спиной (пишет у доски), поворот за 0.22 с (сжатие по ширине), дальше лицом, указка на полоску."""
    turn = (t - T_PROF) / 0.18
    sx = 1.0
    back = t < T_PROF + 0.09
    if 0 <= turn <= 1:
        sx = max(0.5, abs(math.cos(math.pi * turn)))
    spec = dict(PROF)
    x, y, sc = 770, 1560, 1.32
    tip_target = None
    if back:
        spec["back"] = True
        spec["face"] = 0.0
        wph = t * 6
        pose = {"legs": {"L": (4, 0), "R": (-4, 0)},
                "hand_target": {"L": (-200 + 18 * math.sin(wph), -560 + 12 * math.cos(wph * 1.3))},
                "curl": {"L": 0.8, "R": .3}}
        pose["over_hand"] = {"L": lambda h, a: line([(h[0] - 6, h[1] - 14), (h[0] - 26, h[1] - 30)], 9, "#f4f1ea", taper=.1, wmin=.9, seed=4900)}
    else:
        e = t - T_PROF - 0.09
        # указка: поднимается и ведёт по полоске от солнца к луне (24.0–24.8), постукивает на «Майера» (24.28)
        lift = ease_out(clamp(e / 0.35), 3)
        run = ease_io(clamp((t - 24.05) / 0.75))
        bx0, by0, bx1, by1 = BAR
        tx = bx0 + 20 + (bx1 - bx0) * 0.3 * run
        ty = (by0 + by1) / 2 + 10 * math.exp(-max(t - 24.28, 0) * 10) * math.sin(max(t - 24.28, 0) * 40) * (t > 24.28)
        tip_target = (tx, ty)
        # кисть (координаты человека): вверх-влево, к доске
        pose = {"legs": {"L": (6, 0), "R": (-4, 0)},
                "arms": {"L": (-8 - 20 * lift - 4 * math.sin(t * 2), -8 - 80 * lift + 6 * math.sin(t * 2.3))},
                "curl": {"L": 0.85, "R": 0.3},
                "look": (-0.7 * (1 - smooth(24.9, 25.3, t)) + 0.1, -0.2), "brow": 0.2,
                "mouth": "smile" if t > 24.3 else "o",
                "head_tilt": -6 * lift + 3 * math.sin(t * 1.2)}
        spec["face"] = -0.35 + 0.25 * smooth(24.9, 25.4, t)

        def pointer(h, a):
            # от кисти к точке на доске (мировые → координаты человека)
            px = (tip_target[0] - x) / (sc * spec["h"])
            py = (tip_target[1] - y) / (sc * spec["h"])
            dx, dy = px - h[0], py - h[1]
            L = math.hypot(dx, dy) + 1e-6
            ux, uy = dx / L, dy / L
            L = min(L, 420)
            p0 = (h[0] - ux * 30, h[1] - uy * 30)
            p1 = (h[0] + ux * L * lift, h[1] + uy * L * lift)
            return (line([p0, p1], 12, INK, taper=.05, wmin=.6, seed=4910) + line([p0, p1], 6.5, "#c48a52", taper=.05, wmin=.6, seed=4911) +
                    line([(p1[0] - ux * 14, p1[1] - uy * 14), p1], 7, "#f4f1ea", taper=.05, wmin=.8, seed=4912))
        pose["in_hand"] = {"L": pointer}
    body = person.person(spec, pose, 4950)
    g = f'<g transform="translate({f(x)} {f(y)}) scale({sc * sx:.4f} {sc:.4f})">{body}</g>'
    return g, tip_target


def s12(t):
    fill = ease_io(clamp((t - 24.05) / 0.75))
    s = [_ST["wall12"], board(t, fill)]
    p, tip = prof(t)
    s.append(p)
    if tip is not None and t > 24.28:
        e = t - 24.28
        if e < 0.3:
            for k in range(6):
                a = k * math.pi / 3 + .4
                r0 = 30 + 40 * ease_out(e / .3)
                L = 20 * (1 - e / .3)
                s.append(line([(tip[0] + math.cos(a) * r0, tip[1] + math.sin(a) * r0), (tip[0] + math.cos(a) * (r0 + L), tip[1] + math.sin(a) * (r0 + L))],
                              6, "#ffe27a", taper=.5, seed=4960 + k))
    u = clamp((t - 23.16) / 2.6)
    e = t - T_PROF
    push = 0.03 * math.exp(-max(e, 0) * 5) * math.sin(min(max(e, 0) * 10, math.pi))
    return "".join(s), cam(530 + 25 * ease_io(u), 900 + 10 * u, 1.42 + 0.08 * (0.4 * u + 0.6 * ease_io(u)) + push, -0.6 + 1.0 * u), "#e3cfa6"


# ═══════════════════════════════ кадр
def build_static():
    if _ST:
        return
    st28.brick_defs()
    _ST["sky"] = sky()
    _ST["ground"] = ground()
    _ST["bld"] = building()
    _ST["cls_back"] = classroom_back()
    _ST["wall10"] = wall10()
    _ST["wall12"] = wall12()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm, bg = {"s09": s09, "s10": s10, "s12": s12}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cm}">{art}</g>')
