"""Сцена steps рилса 44: раскрытый блокнот в клетку на столе, вид сверху; рука Димы (горчичный рукав, хват из рилса 26,
карандаш) рисует ход «мечта → препятствие → план».
s10 (19.4–21.55): рука с карандашом подъезжает; на «простой ход» (20.68–21.36) рисует три пустые рамки сверху вниз,
     соединённые стрелками (живой линией, линия идёт за грифелем).
s11 (21.55–23.9): на «мечта» (21.68) в первой рамке вырастает облачко с Фудзи и сакурой; камера едет ко второй рамке,
     на «препятствие» (23.08) туда с грохотом падает кирпичная стена — пыль, крошки, блокнот вздрагивает.
s12 (23.9–25.65): камера к третьей рамке: там появляются точка-старт, маленькая стена и Фудзи; на «план» (24.4) рука
     рисует пунктирную стрелку-маршрут, которая обходит стену и упирается в Фудзи; на «случай» (25.12) — зелёная галочка.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import hand26 as hand
import japan
import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, rad_grad,
                 rect_pts, shape, smooth, svg)

_ST = {}
PX0, PY0, PX1, PY1 = 90, 140, 990, 1520          # лист блокнота
FR = [(260, 250, 820, 540), (260, 670, 820, 960), (260, 1090, 820, 1380)]
GRAPH = "#34353f"
DREAM = 21.68
WALL = 23.08
PLAN = 24.40
CHECK = 25.12
HS = 0.78               # масштаб руки


# ───────────────────────── живые штрихи
def wobble(pts, sd, amp=2.2, step=14):
    """Уплотнить ломаную и чуть покачать (рука)."""
    rs = np.random.RandomState(sd)
    out = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / step))
        for k in range(n):
            u = k / n
            out.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u))
    out.append(pts[-1])
    ph = rs.uniform(0, 6.28, 2)
    res = []
    for i, (x, y) in enumerate(out):
        res.append((x + amp * math.sin(i * 0.37 + ph[0]), y + amp * math.sin(i * 0.29 + ph[1])))
    return res


def rect_stroke(r, sd):
    x0, y0, x1, y1 = r
    rs = np.random.RandomState(sd)
    j = lambda: rs.uniform(-4, 4)
    pts = [(x0 + 4, y0 + j()), (x1 + 6, y0 + j()), (x1 + j(), y0 - 2), (x1 + j(), y1 + 6), (x1 + 2, y1 + j()), (x0 - 4, y1 + j()),
           (x0 + j(), y1 + 2), (x0 + j(), y0 - 6), (x0 + 30, y0 + 3)]
    return wobble(pts, sd, 1.6)


def arrow_strokes(x, y0, y1, sd):
    shaft = wobble([(x, y0), (x + 3, (y0 + y1) / 2), (x, y1)], sd, 1.2, 10)
    head = wobble([(x - 26, y1 - 30), (x, y1 + 2), (x + 26, y1 - 30)], sd + 1, 1.0, 8)
    return [shaft, head]


def cum(pts):
    P = np.array(pts, float)
    d = np.linalg.norm(np.diff(P, axis=0), axis=1)
    return P, np.concatenate([[0], np.cumsum(d)])


def partial(pts, u):
    """Начало ломаной до доли u длины и точка конца."""
    P, c = cum(pts)
    if u <= 0:
        return [], tuple(P[0])
    L = c[-1] * min(1.0, u)
    i = int(np.searchsorted(c, L, side="right")) - 1
    i = max(0, min(i, len(P) - 2))
    q = (L - c[i]) / max(c[i + 1] - c[i], 1e-6)
    e = P[i] + (P[i + 1] - P[i]) * q
    return [tuple(p) for p in P[:i + 1]] + [tuple(e)], tuple(e)


def pencil_line(pts, sd, w=6.0, col=GRAPH):
    if len(pts) < 2:
        return ""
    return line(pts, w, col, taper=.08, wmin=.75, seed=sd, peak=.5)


# ───────────────────────── план письма s10
def build_plan():
    strokes = []         # (t0, t1, pts, seed)
    T = [(20.50, 20.80), (20.83, 20.92, 20.94), (20.97, 21.20), (21.22, 21.31, 21.33), (21.35, 21.56)]
    strokes.append((T[0][0], T[0][1], rect_stroke(FR[0], 11), 11))
    a = arrow_strokes(540, FR[0][3] + 16, FR[1][1] - 14, 20)
    strokes.append((T[1][0], T[1][1], a[0], 20))
    strokes.append((T[1][1] + 0.005, T[1][2], a[1], 21))
    strokes.append((T[2][0], T[2][1], rect_stroke(FR[1], 12), 12))
    a = arrow_strokes(540, FR[1][3] + 16, FR[2][1] - 14, 30)
    strokes.append((T[3][0], T[3][1], a[0], 30))
    strokes.append((T[3][1] + 0.005, T[3][2], a[1], 31))
    strokes.append((T[4][0], T[4][1], rect_stroke(FR[2], 13), 13))
    return strokes


STROKES = build_plan()


def frames_drawn(t):
    s = []
    tip = None
    for t0, t1, pts, sd in STROKES:
        if t <= t0:
            continue
        u = clamp((t - t0) / (t1 - t0))
        pp, e = partial(pts, u)
        s.append(pencil_line(pp, sd))
        if u < 1:
            tip = e
    return "".join(s), tip


def tip_s10(t):
    """Где грифель: подъезд → письмо по штрихам (между штрихами — перелёт) → уход."""
    _, tip = frames_drawn(t)
    if tip is not None:
        return np.array(tip), 0.0
    first = STROKES[0]
    if t <= first[0]:
        a0 = np.array([1350.0, 1900.0])
        a1 = np.array(first[2][0])
        u = ease_io(clamp((t - 19.25) / 1.1))
        p = a0 + (a1 - a0) * u
        p = p + np.array([10 * math.sin(t * 6), 8 * math.sin(t * 7.3)]) * smooth(19.9, 20.3, t) * (1 - smooth(20.4, 20.5, t))
        lift = 1.0 - smooth(20.3, 20.5, t)
        return p, lift
    for (a0, a1, p0, _), (b0, b1, p1, _) in zip(STROKES[:-1], STROKES[1:]):
        if a1 <= t <= b0:
            u = ease_io(clamp((t - a1) / max(b0 - a1, 1e-3)))
            e0, e1 = np.array(p0[-1]), np.array(p1[0])
            return e0 + (e1 - e0) * u, 0.5 * math.sin(math.pi * u)
    last = STROKES[-1]
    e0 = np.array(last[2][-1])
    u = ease_in(clamp((t - last[1]) / 0.55), 1.6)
    return e0 + (np.array([1380.0, 1500.0]) - e0) * u, smooth(last[1], last[1] + 0.15, t)


# ───────────────────────── план s12: пунктирная стрелка
ROUTE = None


def route():
    global ROUTE
    if ROUTE is None:
        pts = [(330, 1300), (360, 1220), (420, 1160), (500, 1132), (580, 1128), (650, 1150), (700, 1200), (722, 1240)]
        # сгладить сплайном
        P = lib.sample(pts, False, 3.0)
        ROUTE = [tuple(p) for p in P]
    return ROUTE


ROUTE_T = (PLAN, 24.98)


def dashed(pts, u, sd):
    """Пунктир: видимые куски по 26 px через 16, только до доли u."""
    P, c = cum(pts)
    L = c[-1] * u
    s = []
    k = 0
    a = 0.0
    while a < L:
        b = min(a + 26, L)
        i0 = int(np.searchsorted(c, a))
        i1 = int(np.searchsorted(c, b))
        seg = [tuple(P[min(i0, len(P) - 1)])] + [tuple(p) for p in P[i0:i1]]
        pe, _ = partial(pts, b / c[-1])
        seg.append(pe[-1])
        if len(seg) >= 2:
            s.append(line(seg, 7, "#c0392b", taper=.15, wmin=.7, seed=sd + k % 9))
        a += 42
        k += 1
    return "".join(s)


def route_drawn(t):
    if t <= ROUTE_T[0]:
        return "", None
    u = clamp((t - ROUTE_T[0]) / (ROUTE_T[1] - ROUTE_T[0]))
    u = u * 0.85 + 0.15 * ease_io(u)
    pts = route()
    s = dashed(pts, u, 700)
    _, e = partial(pts, u)
    if u >= 1:
        # наконечник
        x, y = pts[-1]
        px, py = pts[-8]
        a = math.atan2(y - py, x - px)
        L = 34
        hp = [(x - L * math.cos(a - .5), y - L * math.sin(a - .5)), (x + 4 * math.cos(a), y + 4 * math.sin(a)),
              (x - L * math.cos(a + .5), y - L * math.sin(a + .5))]
        k = clamp((t - ROUTE_T[1]) / 0.06)
        hpp, _ = partial(hp, k)
        s += line(hpp, 8, "#c0392b", taper=.1, wmin=.8, seed=720)
        return s, None
    return s, e


def tip_s12(t):
    _, e = route_drawn(t)
    if e is not None:
        return np.array(e), 0.0
    p0 = np.array(route()[0])
    if t <= ROUTE_T[0]:
        a0 = np.array([1350.0, 1800.0])
        u = ease_io(clamp((t - 23.85) / 0.5))
        return a0 + (p0 - a0) * u, 1 - smooth(24.25, 24.4, t)
    e0 = np.array(route()[-1])
    u = ease_in(clamp((t - ROUTE_T[1] - 0.06) / 0.5), 1.6)
    return e0 + (np.array([1400.0, 1750.0]) - e0) * u, smooth(ROUTE_T[1], ROUTE_T[1] + 0.12, t)


# ───────────────────────── содержимое рамок
def dream_cloud(t):
    """Рамка 1: облачко мечты с Фудзи, вырастает на «мечта»."""
    k = back_out(clamp((t - (DREAM - 0.06)) / 0.3), 2.0)
    if k < 0.02:
        return ""
    x0, y0, x1, y1 = FR[0]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 4 * math.sin(t * 2.2)
    rx, ry = 200, 108
    rim = japan.cloud_pts(0, 0, rx + 20, ry + 18, 11, .16, .3)
    win = japan.cloud_pts(0, 0, rx - 4, ry - 6, 11, .09, .3)
    s = [shape(rim, "#ffffff", blob(japan.cloud_pts(24, 30, rx + 6, ry + 4, 11, .16, .3), "#d6e5f7", .95) +
               blob(japan.cloud_pts(-16, -16, rx, ry, 11, .16, .3), "#ffffff"), w=4.6, seed=800)]
    c = lib.clip_of(win)
    sc = 0.62
    pic = f'<g transform="translate({f(-300 * sc)} {f(-210 * sc)}) scale({sc})">{japan.mini_dream(t, 810)}</g>'
    pic += japan.petals(t, (-rx, -ry, rx, ry), 5, 820, (6, 9), (40, 70), 50)
    s.append(f'<g clip-path="url(#{c})">{pic}</g>')
    s.append(f'<path d="{lib.ink_closed(win, 3.4, seed=801)}" fill="{INK}"/>')
    # искорки при появлении
    e = t - DREAM
    if 0 <= e < 0.45:
        u = e / 0.45
        for j in range(8):
            a = j * math.pi / 4 + .2
            r0, r1 = 240 + 60 * u, 270 + 110 * u
            s.append(line([(r0 * math.cos(a), r0 * math.sin(a) * .6), (r1 * math.cos(a), r1 * math.sin(a) * .6)], 9 * (1 - u) + 2, "#ffcf3a",
                          taper=.6, seed=830 + j))
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({f(k)})">{"".join(s)}</g>'


def brick_wall(x0, y0, x1, y1, sd, rows=5, lw=4.6):
    """Кирпичная стена (x0..x1, y0..y1): кирпичи вразбежку, швы, тень справа-снизу у каждого."""
    s = []
    h = (y1 - y0) / rows
    inner = blob(rect_pts(x0 - 10, y0 - 10, x1 + 10, y1 + 10), "#efe2c8")
    rs = np.random.RandomState(sd)
    for r in range(rows):
        yy0 = y0 + r * h
        bw = (x1 - x0) / 3.5
        off = 0 if r % 2 == 0 else -bw / 2
        x = x0 + off
        k = 0
        while x < x1:
            a, b = max(x, x0) + 3, min(x + bw, x1) - 3
            if b - a > 8:
                col = ["#d0603a", "#c45634", "#d96d45"][(r + k) % 3]
                inner += shape(rect_pts(a, yy0 + 3, b, yy0 + h - 3, 3), col,
                               blob(rect_pts(a, yy0 + h * .62, b, yy0 + h - 3), "#a8442a", .9) +
                               blob(rect_pts(a + 4, yy0 + 6, b - 4, yy0 + 10), "#f0956c", .7), w=lw * .55, seed=sd + r * 10 + k)
            x += bw
            k += 1
    s.append(shape(rect_pts(x0, y0, x1, y1, 4), "#efe2c8", inner, w=lw, seed=sd + 99))
    return "".join(s)


def wall_f2(t):
    """Рамка 2: стена падает сверху и с грохотом встаёт на нижнюю линию рамки."""
    x0, y0, x1, y1 = FR[1]
    wx0, wx1, wy1 = 375, 705, y1 - 14
    hh = 205
    T0 = WALL - 0.17
    if t < T0:
        return ""
    if t < WALL:
        u = (t - T0) / 0.17
        dy = -(y1 - y0 + 60) * (1 - u * u)
        sq = 0.0
    else:
        e = t - WALL
        dy = 0.0
        sq = 0.12 * math.exp(-e * 10) * math.cos(e * 30)
    h = hh * (1 - sq)
    wy0 = wy1 - h
    ww = (wx1 - wx0) * (1 + sq * 0.5)
    cx = (wx0 + wx1) / 2
    c = lib.clip_rect(x0 + 6, y0 + 6, x1 - x0 - 12, y1 - y0 - 12)
    s = [blob(rect_pts(cx - ww / 2 + 10, wy1 - 4, cx + ww / 2 + 14, wy1 + 8), "#7d6a52", .35, blur(4)) if t >= WALL else "",
         brick_wall(cx - ww / 2, wy0 + dy, cx + ww / 2, wy1 + dy, 900)]
    if t < WALL:          # следы скорости
        for j in range(4):
            xx = cx - ww / 2 + 40 + j * (ww - 80) / 3
            s.append(line([(xx, wy0 + dy - 30), (xx, wy0 + dy - 120)], 6, "#9aa3b8", taper=.7, seed=910 + j))
    out = f'<g clip-path="url(#{c})">{"".join(s)}</g>'
    # пыль и крошки после удара
    e = t - WALL
    if 0 <= e < 0.9:
        u = e / 0.9
        for j in range(6):
            side = -1 if j < 3 else 1
            k = j % 3
            px = cx + side * (ww / 2 + 10 + 60 * ease_out(u) * (1 + k * .5))
            py = wy1 - 16 - 30 * k * ease_out(u)
            r = (24 + 10 * k) * back_out(clamp(u / 0.25)) * (1 - smooth(0.55, 1, u))
            if r > 2:
                out += japan.puff_cloud(px, py, r * 1.2, r, 930 + j, n=6, bump=.3, col="#efe6d6", sh="#cfc2aa", w=3)
        rs = np.random.RandomState(4)
        for j in range(7):
            vx, vy = rs.uniform(-420, 420), rs.uniform(-620, -300)
            px = cx + rs.uniform(-80, 80) + vx * e
            py = wy0 + 30 + vy * e + 1500 * e * e
            if py > wy1 - 6:
                continue
            sz = rs.uniform(9, 16)
            out += f'<g transform="translate({f(px)} {f(py)}) rotate({f(e * 600 * (1 if j % 2 else -1))})">' + \
                shape(rect_pts(-sz, -sz * .6, sz, sz * .6, 2), "#c45634", "", w=2.6, seed=940 + j) + "</g>"
        # линии удара
        if e < 0.3:
            for j, (ax, ay, bx, by) in enumerate([(-1, -.4, -1.6, -.7), (1, -.4, 1.6, -.7), (-1, .1, -1.7, .05), (1, .1, 1.7, .05)]):
                r0 = ww / 2 + 30 + 40 * e / 0.3
                s0 = (cx + ax * r0, wy0 + h * 0.5 + ay * 120)
                s1 = (cx + bx * r0 * .9, wy0 + h * .5 + by * 140)
                out += line([s0, s1], 10 * (1 - e / .3) + 2, GRAPH, taper=.5, seed=960 + j)
    return out


def plan_f3(t):
    """Рамка 3: старт-точка, маленькая стена, маленькая Фудзи — проявляются перед «план»."""
    s = []
    k1 = back_out(clamp((t - 23.98) / 0.2), 2.4)
    k2 = back_out(clamp((t - 24.06) / 0.2), 2.4)
    k3 = back_out(clamp((t - 24.14) / 0.2), 2.4)
    if k2 > 0.02:
        g = brick_wall(-62, -150, 62, 0, 1000, rows=4, lw=3.8)
        s.append(f'<g transform="translate(560 1350) scale({f(k2)})">{g}</g>')
    if k3 > 0.02:
        g = japan.fuji(0, 0, 200, 130, 1010)
        g += blob(rect_pts(-100, 0, 100, 4), GRAPH)
        s.append(f'<g transform="translate(745 1350) scale({f(k3)})">{g}</g>')
    if k1 > 0.02:
        g = shape(ellipse_pts(0, 0, 18, 18, 16), "#c0392b", blob(ellipse_pts(-5, -5, 6, 5, 8), "#ff8a70", .9), w=3.4, seed=1020)
        s.append(f'<g transform="translate(330 1306) scale({f(k1)})">{g}</g>')
    return "".join(s)


def check(t):
    e = t - (CHECK - 0.06)
    if e < 0:
        return ""
    pts = wobble([(712, 1150), (752, 1196), (838, 1092)], 1100, 1.0, 8)
    u = clamp(e / 0.16)
    pp, _ = partial(pts, ease_out(u, 2))
    pop = 1 + 0.18 * math.exp(-max(e - 0.16, 0) * 9) * math.sin(min(max(e - 0.16, 0) * 18, math.pi)) if e > 0.16 else 1
    s = line(pp, 34, INK, taper=.1, wmin=.85, seed=1101) + line(pp, 24, "#3cb34a", taper=.1, wmin=.85, seed=1101)
    if u >= 1:
        s += line([(p[0] - 4, p[1] - 6) for p in pts[: len(pts) // 2]], 6, "#9be89f", taper=.4, seed=1102, op=.9)
    g = f'<g transform="translate(775 1145) scale({f(pop)}) translate(-775 -1145)">{s}</g>'
    if 0.16 < e < 0.6:
        v = (e - 0.16) / 0.44
        for j in range(7):
            a = -math.pi * (0.1 + 0.8 * j / 6)
            r0, r1 = 90 + 60 * v, 120 + 110 * v
            g += line([(775 + r0 * math.cos(a), 1145 + r0 * math.sin(a)), (775 + r1 * math.cos(a), 1145 + r1 * math.sin(a))], 9 * (1 - v) + 2,
                      "#ffcf3a", taper=.6, seed=1110 + j)
    return g


# ───────────────────────── стол, блокнот, рука
def desk():
    s = []
    DEFS.append('<pattern id="pWood44" width="420" height="140" patternUnits="userSpaceOnUse">'
                '<rect width="420" height="140" fill="#9a663a"/>'
                '<path d="M0 30 C120 22 260 40 420 28 M0 78 C140 86 280 66 420 82 M0 118 C110 110 300 126 420 114" fill="none" stroke="#83522c" stroke-width="3"/>'
                '<rect y="138" width="420" height="2" fill="#6a421f"/></pattern>')
    s.append('<rect x="-900" y="-900" width="2900" height="3700" fill="url(#pWood44)"/>')
    g = rad_grad([(0, "#ffe2a8", .45), (.6, "#ffc070", .14), (1, "#ffc070", 0)], 520, 760, 1000, 1000)
    s.append(f'<rect x="-900" y="-900" width="2900" height="3700" fill="url(#{g})"/>')
    return "".join(s)


def notebook():
    s = []
    s.append(blob(rect_pts(PX0 + 18, PY0 + 24, PX1 + 22, PY1 + 30, 18), "#3a2210", .45, blur(14)))
    # нижние листы — стопка
    s.append(shape(rect_pts(PX0 + 6, PY0 + 8, PX1 + 8, PY1 + 12, 14), "#ece4d0", "", w=4, seed=40))
    inner = ""
    for x in range(PX0 + 30, PX1, 40):
        inner += f'<rect x="{x}" y="{PY0}" width="2" height="{PY1 - PY0}" fill="#c9d8ec"/>'
    for y in range(PY0 + 70, PY1, 40):
        inner += f'<rect x="{PX0}" y="{y}" width="{PX1 - PX0}" height="2" fill="#c9d8ec"/>'
    inner += f'<rect x="{PX0 + 70}" y="{PY0}" width="3" height="{PY1 - PY0}" fill="#f0a8a8"/>'
    inner += blob(rect_pts(PX1 - 60, PY0, PX1, PY1), "#efe6d2", .6)
    s.append(shape(rect_pts(PX0, PY0, PX1, PY1, 12), "#fbf8ef", inner, w=4.6, seed=41))
    # пружина сверху
    for k, x in enumerate(range(PX0 + 50, PX1 - 20, 62)):
        s.append(blob(ellipse_pts(x, PY0 + 22, 10, 10, 10), "#3a3440"))
        s.append(line([(x - 2, PY0 + 24), (x + 4, PY0 - 18), (x + 18, PY0 - 22), (x + 16, PY0 + 6)], 7, "#9aa0ae", taper=.1, wmin=.9, seed=50 + k % 7))
        s.append(line([(x - 2, PY0 + 24), (x + 4, PY0 - 18), (x + 18, PY0 - 22), (x + 16, PY0 + 6)], 2.4, "#5d6372", taper=.1, wmin=.9, seed=60 + k % 7))
    # карандашная стружка и ластик на столе
    s.append(shape(rect_pts(PX1 + 30, 300, PX1 + 110, 350, 8), "#f08ea0", blob(rect_pts(PX1 + 30, 330, PX1 + 110, 350), "#d46b80", .9), w=3.6, seed=70))
    return "".join(s)


def hand_at(tip, lift, t):
    x, y = tip
    ang = -38 + 3 * math.sin(t * 2.3) - 8 * lift
    sc = HS * (1 + 0.08 * lift)
    sh = (f'<g transform="translate({f(x + 22 + 30 * lift)} {f(y + 30 + 40 * lift)}) scale({f(HS)})" opacity=".28" filter="url(#fShH44)">'
          f'{hand.hand(ang, 7)}</g>')
    return sh + f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{hand.hand(ang, 7)}</g>'


# ───────────────────────── кадры
def s10(t):
    lines, _ = frames_drawn(t)
    tip, lift = tip_s10(t)
    art = notebook() + lines + hand_at(tip, lift, t)
    u = clamp((t - 19.2) / 2.55)
    scl = 0.86 + 0.06 * (0.35 * u + 0.65 * ease_io(u))
    ty = tip[1] if tip[1] < 1500 else 1500
    cy = 830 + 0.12 * (ty - 830) * smooth(20.3, 20.6, t)
    cx = 545 + 8 * math.sin(t * 0.9)
    return art, cam(cx, cy, scl, -0.5 + 0.7 * u)


def s11(t):
    lines, _ = frames_drawn(t)
    art = notebook() + lines + dream_cloud(t) + wall_f2(t)
    tip, lift = tip_s10(t)
    if t < 21.95:
        art += hand_at(tip, lift, t)
    # камера: к первой рамке на «мечта», потом ко второй
    zin = ease_io(clamp((t - 21.4) / 0.4))
    pan = ease_io(clamp((t - 22.2) / 0.75))
    cy = 870 + (440 - 870) * zin + (800 - 440) * pan
    scl = 0.92 + (1.28 - 0.92) * zin + 0.04 * pan + 0.02 * clamp((t - 23.0) / 1)
    cx = 545
    rot = 0.4 * math.sin(t * 1.1)
    e = t - WALL
    if e > 0:
        k = math.exp(-e * 7)
        cy += 16 * k * math.sin(e * 55)
        cx += 12 * k * math.sin(e * 47 + 1)
        rot += 1.2 * k * math.sin(e * 40)
        scl *= 1 + 0.04 * k * math.sin(min(e * 16, math.pi))
    return art, cam(cx, cy, scl, rot)


def s12(t):
    lines, _ = frames_drawn(t)
    r, _ = route_drawn(t)
    art = notebook() + lines + dream_cloud(t) + wall_f2(t) + plan_f3(t) + r + check(t)
    tip, lift = tip_s12(t)
    if t > 23.85 and t < 25.6:
        art += hand_at(tip, lift, t)
    pan = ease_io(clamp((t - 23.7) / 0.55))
    cy = 800 + (1215 - 800) * pan
    scl = 1.32 + 0.06 * clamp((t - 24.2) / 1.6)
    cx = 545 + 15 * pan
    e = t - CHECK
    if e > 0:
        scl *= 1 + 0.035 * math.exp(-e * 6) * math.sin(min(e * 16, math.pi))
    return art, cam(cx, cy, scl, -0.3 + 0.5 * math.sin(t * 0.8))


def build_static():
    if _ST:
        return
    DEFS.append('<filter id="fShH44" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
    _ST["desk"] = desk()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s10": s10, "s11": s11, "s12": s12}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#8a5a34"/><g transform="{cm}">{_ST["desk"]}{art}</g>')
