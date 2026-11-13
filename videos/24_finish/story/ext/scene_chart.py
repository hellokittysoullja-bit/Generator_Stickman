"""Сцена chart (s12, s13): две большие батарейки заряда на полке. Над левой — клетчатый финишный флажок, над правой —
маленький след босой ступни. s12: на «не финиш» (21.8) флажок тускнеет и обвисает, левая батарейка почти пустая,
мигает красным. s13: на «маленький шаг» (22.53) правая заряжается ячейка за ячейкой до упора, зеленеет и сияет,
след загорается золотом; на «обычный день» (23.68) рядом выскакивает листок календаря с числом (без букв)."""
import math

import numpy as np

import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, fill_d,
                 line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg)

NOT_FIN = 21.8
STEP = 22.53
DAY = 23.68
LX, RX = 300, 780
BY0, BY1, BW = 590, 1120, 250       # корпус батарейки: верх, низ, ширина
SHELF = 1120
_ST = {}


def level_left(t):
    base = 0.36 - 0.23 * smooth(NOT_FIN - 0.05, NOT_FIN + 0.5, t)
    return base + 0.015 * math.sin(t * 9)


def level_right(t):
    lo = 0.17 + 0.012 * math.sin(t * 5)
    u = clamp((t - STEP) / 0.75)
    return lo + (1.0 - lo) * ease_out(u, 2) if t > STEP else lo


def background():
    s = []
    lin_grad([(0, "#1f3644", 1), (.6, "#2c4f60", 1), (1, "#356172", 1)], 0, 0, 0, 1, gid="gWallC")
    s.append(f'<rect x="-500" y="-500" width="{W + 1000}" height="{SHELF + 500}" fill="url(#gWallC)"/>')
    rad_grad([(0, "#4f8195", .8), (.7, "#3a6475", .2), (1, "#3a6475", 0)], 540, 760, 620, 560, gid="gSpotC")
    s.append(f'<rect x="-500" y="-500" width="{W + 1000}" height="{SHELF + 500}" fill="url(#gSpotC)"/>')
    # обои: редкий ромб
    DEFS.append('<pattern id="pDia" width="120" height="120" patternUnits="userSpaceOnUse">'
                '<path d="M60 44 L70 60 L60 76 L50 60Z" fill="#3e6a7b" opacity=".55"/></pattern>')
    s.append(f'<rect x="-500" y="-500" width="{W + 1000}" height="{SHELF + 500}" fill="url(#pDia)"/>')
    # полка-столешница
    top = [(-300, SHELF - 6, 1), (W + 300, SHELF - 6, 1), (W + 300, SHELF + 34, 1), (-300, SHELF + 34, 1)]
    s.append(shape(top, "#c48a55", blob(rect_pts(-300, SHELF + 18, W + 300, SHELF + 34), "#9c6a3e"), w=4.6, seed=11))
    lin_grad([(0, "#7a4e2c", 1), (1, "#4f321c", 1)], 0, 0, 0, 1, gid="gFront")
    s.append(f'<rect x="-300" y="{SHELF + 34}" width="{W + 600}" height="1200" fill="url(#gFront)"/>')
    s.append(line([(-300, SHELF + 34), (W + 300, SHELF + 34)], 3.6, INK, taper=.1, wmin=.8, seed=12))
    for k, y in enumerate([SHELF + 160, SHELF + 330, SHELF + 520]):
        s.append(line([(-300, y), (W + 300, y + 8)], 2.4, "#3a2412", taper=.2, wmin=.6, seed=13 + k, op=.8))
    # картинка-рамка на стене слева сверху и розетка справа — обжитость
    s.append(shape(rect_pts(70, 120, 250, 260, 6), "#6b4a2c", "", w=4, seed=14))
    s.append(shape(rect_pts(88, 138, 232, 242), "#e6d7b8",
                   blob([(88, 242), (140, 180), (176, 214), (206, 170), (232, 242)], "#6fa38a") + blob(ellipse_pts(200, 166, 14, 14, 10), "#f2c45a"), w=3, seed=15))
    s.append(shape(rect_pts(950, 960, 1020, 1040, 10), "#e9e6df", blob(ellipse_pts(972, 1000, 6, 9, 8), "#555b66") +
                   blob(ellipse_pts(998, 1000, 6, 9, 8), "#555b66"), w=3.4, seed=16))
    return "".join(s)


def cell_color(lv):
    if lv < 0.26:
        return "#e5484d", "#b9323a"
    if lv < 0.6:
        return "#f0a43a", "#c47a1e"
    return "#4fd06f", "#2f9a4c"


def battery(cx, lv, t, bright=0.0, warn=0.0, seed=0, bolt=0.0):
    s = []
    x0, x1 = cx - BW / 2, cx + BW / 2
    # тень на полке
    s.append(blob(ellipse_pts(cx + 26, SHELF + 4, BW * .62, 18, 14), "#1a120a", .5, blur(5)))
    # клемма
    s.append(shape(rect_pts(cx - 48, BY0 - 40, cx + 48, BY0 + 12, 12), "#9aa4b2", blob(rect_pts(cx + 14, BY0 - 40, cx + 48, BY0 + 12), "#717b8a"), w=4.4, seed=seed + 1))
    # корпус: металл с бликом слева и тенью справа
    gid = lin_grad([(0, "#c9d1db", 1), (.18, "#f4f7fa", 1), (.5, "#dbe1e8", 1), (1, "#9aa4b2", 1)], 0, 0, 1, 0)
    inner = f'<rect x="{x0 - 5}" y="{BY0 - 5}" width="{BW + 10}" height="{BY1 - BY0 + 10}" fill="url(#{gid})"/>'
    inner += blob(rect_pts(x1 - 40, BY0, x1, BY1), "#7f8998", .5)
    inner += blob(rect_pts(x0, BY1 - 34, x1, BY1), "#7f8998", .55)
    s.append(shape(rect_pts(x0, BY0, x1, BY1, 36), "#dbe1e8", inner, w=5.6, seed=seed + 2))
    # окно с ячейками
    wx0, wx1, wy0, wy1 = x0 + 30, x1 - 30, BY0 + 34, BY1 - 40
    n, gap = 5, 12
    ch = (wy1 - wy0 - gap * (n + 1)) / n
    win = [blob(rect_pts(wx0, wy0, wx1, wy1, 20), "#1b2830")]
    c1, c2 = cell_color(lv)
    blink = 1.0
    if warn > 0:
        blink = 0.55 + 0.45 * (0.5 + 0.5 * math.cos(t * 2 * math.pi * 2.2))
        c1 = mix("#5a2226", c1, blink)
        c2 = mix("#3a1418", c2, blink)
    for k in range(n):
        yb = wy1 - gap - k * (ch + gap)
        fill = clamp(lv * n - k)
        win.append(blob(rect_pts(wx0 + gap, yb - ch, wx1 - gap, yb, 8), "#26353e"))
        if fill > 0.01:
            yt = yb - ch * fill
            win.append(shape(rect_pts(wx0 + gap, yt, wx1 - gap, yb, 8 if fill > .2 else 3), c1,
                             blob(rect_pts(wx1 - gap - 34, yt, wx1 - gap, yb), c2, .9) +
                             line([(wx0 + gap + 14, yt + 10), (wx1 - gap - 44, yt + 10)], 6, "#ffffff", taper=.3, seed=seed + 20 + k, op=.45 if fill > .4 else 0),
                             w=3, seed=seed + 30 + k, var=.12))
    s.append(shape(rect_pts(wx0, wy0, wx1, wy1, 20), "#1b2830", "".join(win), w=4.2, seed=seed + 3))
    # блик стекла окна
    s.append(line([(wx0 + 18, wy0 + 30), (wx0 + 18, wy0 + 150)], 7, "#ffffff", taper=.7, seed=seed + 4, op=.35))
    # молния зарядки
    if bolt > 0.01:
        cy = (wy0 + wy1) / 2
        sc = bolt
        pts = [(18, -78, 1), (-34, 10, 1), (-2, 10, 1), (-18, 78, 1), (36, -16, 1), (4, -16, 1)]
        pts = lib.T(pts, cx, cy, sc, 0, 0, 0)
        s.append(shape(pts, "#fff3a6", blob(lib.T([(10, -16), (36, -16), (-18, 78), (-6, 20)], cx, cy, sc, 0, 0, 0), "#ffd23a"), w=4.4, seed=seed + 5))
    return "".join(s)


def glow(cx, k, t):
    if k < 0.01:
        return ""
    pul = 1 + 0.06 * math.sin(t * 7)
    gid = rad_grad([(0, "#9dff9a", .75), (.45, "#4fd06f", .35), (1, "#4fd06f", 0)], cx, (BY0 + BY1) / 2, 300 * pul, 420 * pul)
    s = f'<rect x="{cx - 420}" y="{BY0 - 480}" width="840" height="1100" fill="url(#{gid})" opacity="{k:.3f}" style="mix-blend-mode:screen"/>'
    for j in range(10):
        a = -math.pi / 2 + (j - 4.5) * 0.33 + (0.0 if j % 2 else 0.12)
        ph = (t * 1.6 + j * 0.29) % 1
        r0 = 330 + 70 * ph
        L = 54 * (1 - ph) * k
        cy = (BY0 + BY1) / 2
        if L > 4:
            s += line([(cx + math.cos(a) * r0 * .7, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + L) * .7, cy + math.sin(a) * (r0 + L))],
                      8, "#c9ffb8", taper=.5, seed=40 + j)
    return s


def flag(t, dim):
    """Клетчатый флажок на древке, воткнутом в клемму левой батарейки. dim: 0 — яркий, 1 — тусклый и обвисший."""
    s = []
    px, ptop, pbot = LX - 6, 300, BY0 - 38
    s.append(line([(px + 4, pbot), (px + 4, ptop)], 9, "#3a3f48", taper=.05, wmin=.95, seed=50))
    s.append(line([(px + 2, pbot - 6), (px + 2, ptop + 4)], 3, "#8a92a0", taper=.1, wmin=.8, seed=51, op=.8))
    s.append(shape(ellipse_pts(px + 4, ptop - 6, 10, 10, 10), mix("#ffd23a", "#8e8a7a", dim), "", w=3, seed=52))
    nx, ny = 5, 4
    Lc, Hc = 230, 150
    amp = 16 * (1 - 0.75 * dim)
    droop = 70 * dim

    def P(i, j):
        u, v = i / nx, j / ny
        wv = amp * math.sin(u * 3.4 - t * 6.5) * u
        x = px + 8 + u * Lc * (1 - 0.22 * dim * u)
        y = ptop + 6 + v * Hc + wv + droop * u * u + 6 * dim * u * v
        return (x, y)
    white, black = mix("#fbfbf7", "#9a9c9e", dim), mix("#1d1f24", "#4d5056", dim)
    cells = []
    for i in range(nx):
        for j in range(ny):
            q = [P(i, j) + (1,), P(i + 1, j) + (1,), P(i + 1, j + 1) + (1,), P(i, j + 1) + (1,)]
            # тень складки: тёмная полоса, где волна уходит вниз
            sh = 0.5 + 0.5 * math.cos((i + .5) / nx * 3.4 - t * 6.5)
            base = black if (i + j) % 2 else white
            col = mix(base, "#000000", 0.25 * sh * (1 - dim * .5))
            cells.append(f'<path d="M{f(q[0][0])} {f(q[0][1])}L{f(q[1][0])} {f(q[1][1])}L{f(q[2][0])} {f(q[2][1])}L{f(q[3][0])} {f(q[3][1])}Z" '
                         f'fill="{col}" stroke="{col}" stroke-width="1.2"/>')
    outline = [P(i, 0) for i in range(nx + 1)] + [P(nx, j) for j in range(1, ny + 1)] + [P(i, ny) for i in range(nx - 1, -1, -1)] + \
        [P(0, j) for j in range(ny - 1, 0, -1)]
    dense = []
    for k in range(len(outline)):
        a, b = outline[k], outline[(k + 1) % len(outline)]
        for q in np.linspace(0, 1, 4, endpoint=False):
            dense.append((a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q))
    s.append("".join(cells))
    s.append(f'<path d="{lib.ink_closed(dense, 4.6, seed=53)}" fill="{INK}"/>')
    return "".join(s)


def foot(t, gold):
    """Маленький след босой ступни над правой батарейкой, покачивается; при заряде — золотой и с ореолом."""
    cx, cy = RX + 8, 400 + 10 * math.sin(t * 2.4)
    rot = 14 + 4 * math.sin(t * 1.7)
    sc = 1 + 0.18 * gold * (1 + 0.1 * math.sin(t * 6))
    col = mix("#e9a47a", "#ffd23a", gold)
    sh = mix("#c97e57", "#e8a81c", gold)
    s = []
    if gold > 0.02:
        gid = rad_grad([(0, "#fff2a0", .9), (.5, "#ffd23a", .4), (1, "#ffd23a", 0)], cx, cy, 170, 190)
        s.append(f'<rect x="{cx - 220}" y="{cy - 240}" width="440" height="480" fill="url(#{gid})" opacity="{gold:.3f}" style="mix-blend-mode:screen"/>')
    sole = [(0, -40), (24, -30), (30, 0), (22, 34), (24, 62), (10, 80), (-12, 76), (-20, 50), (-14, 16), (-26, -12), (-22, -34)]
    g = [shape(sole, col, blob([(10, -30), (30, 0), (22, 34), (24, 62), (10, 80), (6, 40)], sh, .8), w=4, seed=60)]
    for k, (x, y, r) in enumerate([(-22, -56, 11), (-4, -66, 9), (12, -64, 8), (25, -56, 7), (34, -44, 6)]):
        g.append(shape(ellipse_pts(x, y, r, r * 1.1, 10), col, "", w=3.2, seed=61 + k))
    s.append(f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({f(1.25 * sc)})">{"".join(g)}</g>')
    return "".join(s)


def calendar(t):
    if t < DAY - 0.02:
        return ""
    e = t - DAY + 0.02
    k = back_out(clamp(e / 0.32), 2.4)
    cx, cy = 1000, 990
    rot = 8 - 5 * k + 1.5 * math.sin(e * 3)
    s = []
    g = []
    g.append(blob(rect_pts(-80 + 12, -96 + 14, 80 + 12, 100 + 14, 10), "#14232c", .5, blur(5)))
    pg = rect_pts(-80, -96, 80, 100, 10)
    inner = blob(rect_pts(-80, -96, 80, -46), "#e5484d") + blob(rect_pts(-80, -60, 80, -46), "#b9323a")
    inner += blob([(40, 100), (80, 60), (80, 100)], "#d8d2c4")
    inner += f'<text x="0" y="{f(52)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="104" fill="#26303a">14</text>'
    g.append(shape(pg, "#fbf8f1", inner, w=4.4, seed=70))
    for x in (-40, 40):
        g.append(shape(rect_pts(x - 7, -112, x + 7, -80, 7), "#9aa4b2", "", w=3, seed=71 + x))
    # загнутый уголок
    g.append(shape([(40, 100, 1), (80, 60, 1), (60, 96, 1)], "#e9e3d4", "", w=3, seed=73))
    s.append(f'<g transform="translate({cx} {cy}) rotate({f(rot)}) scale({f(max(k, .01))})">{"".join(g)}</g>')
    return "".join(s)


def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        lib.static_done()
    lib.dyn_begin()
    dim = smooth(NOT_FIN - 0.05, NOT_FIN + 0.45, t)
    warn = smooth(NOT_FIN, NOT_FIN + 0.3, t)
    lr = level_right(t)
    full = smooth(STEP + 0.55, STEP + 0.85, t)
    # батарейки пружинят: левая «оседает» на «не финиш», правая подпрыгивает, когда заполнилась
    lsq = 1 - 0.05 * math.exp(-max(0, t - NOT_FIN) * 5) * math.sin(max(0, t - NOT_FIN) * 16) if t > NOT_FIN else 1.0
    rjump = 0.0
    rsq = 1.0
    if t > STEP + 0.72:
        e = t - STEP - 0.72
        rjump = 26 * math.exp(-e * 5) * abs(math.sin(e * 12))
        rsq = 1 + 0.05 * math.exp(-e * 6) * math.cos(e * 18)
    breathe = 1 + 0.006 * math.sin(t * 2.2)
    bolt_r = (smooth(STEP - 0.02, STEP + 0.15, t) * (1 - smooth(STEP + 1.2, STEP + 1.6, t)))
    bolt_l = 0.0
    if NOT_FIN - 1.6 < t < NOT_FIN + 0.15:   # левая пытается зарядиться — молния мерцает и гаснет
        bolt_l = 0.6 * (0.5 + 0.5 * math.sin(t * 13)) * (1 - smooth(NOT_FIN - 0.1, NOT_FIN + 0.15, t))
    L = (f'<g transform="translate({LX} {SHELF}) scale({f(breathe / lsq ** .5)} {f(breathe * lsq)}) translate({-LX} {-SHELF})">'
         f'{battery(LX, level_left(t), t, warn=warn, seed=100, bolt=bolt_l)}</g>')
    R = (f'<g transform="translate(0 {f(-rjump)}) translate({RX} {SHELF}) scale({f(breathe / rsq ** .5)} {f(breathe * rsq)}) translate({-RX} {-SHELF})">'
         f'{battery(RX, lr, t, seed=200, bolt=bolt_r)}</g>')
    art = _ST["bg"] + glow(RX, full, t) + flag(t, dim) + L + R + foot(t, full) + calendar(t)
    if sid == "s12":
        u = (t - 19.7) / 2.86
        sh = 0.0
        if t > NOT_FIN:
            e = t - NOT_FIN
            sh = 7 * math.exp(-e * 7) * math.sin(e * 50)
        cm = cam(540 + sh, 800 - 10 * u, 1.17 + 0.03 * u)
    else:
        lin = clamp((t - 22.16) / 2.76)
        u = 0.35 * lin + 0.65 * ease_io(lin)
        cm = cam(540 + 170 * u, 792 - 2 * u, 1.20 + 0.18 * u)
    return svg(f'<rect width="{W}" height="{H}" fill="#2c4f60"/><g transform="{cm}">{art}</g>')
