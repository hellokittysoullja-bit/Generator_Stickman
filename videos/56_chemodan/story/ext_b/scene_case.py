"""Рилс 56 s07 (12.14–14.08), s08 (14.08–15.82), s09 (15.82–17.44): мягкий чемодан сбоку-спереди, один мир на три плана.
Общее время: молнии (два бегунка) идут навстречу, на «не» (13.07) встают; на «закрывался» (13.18) замок дёргается, чемодан раздувается, лезут рукав
и штанина; Дима с разбега садится на «сел» (14.46), сжатие, носки вылетают, отскок, снова сел (15.12); бегунки сходятся, на «закрылся» (16.77)
замок-замочек защёлкивается, блик; Дима выдыхает, под крышкой подрагивает бугор."""
import math

import numpy as np

import dima
import lib
import props
from lib import INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg
from props import TEAL, TEAL_D, TEAL_L, place

SEED = 7000
X0, X1 = 160.0, 920.0          # чемодан по x
FL = 1250.0                    # низ чемодана
SEAM = 1060.0                  # шов (верх основания)
LIDTOP = 944.0
CXC = (X0 + X1) / 2
XB, WB = 640.0, 150.0          # где вздулась крышка (бугор)
BS = 0.70


def lerp(a, b, u):
    return a + (b - a) * u


# ═════════════════════════ время событий ═════════════════════════
T_NO, T_JERK = 13.07, 13.18
T_SIT, T_UP, T_SIT2, T_SHUT = 14.46, 14.64, 15.12, 16.77


def sliders(t):
    """(sL, sR): положения бегунков. Идут навстречу, встают на «не», в s09 сходятся."""
    if t < T_NO:
        u = ease_out(clamp((t - 11.9) / 1.2), 1.8)
        sl, sr = lerp(200, 470, u), lerp(905, 800, u)
    else:
        sl, sr = 470, 800
        e = t - T_NO
        # дёрг назад-вперёд — не сходится
        sl += -22 * math.exp(-e * 9) * math.sin(e * 26) if e < 0.5 else 0
        sr += 14 * math.exp(-e * 9) * math.sin(e * 24) if e < 0.5 else 0
    if t > 15.85:
        u = ease_io(clamp((t - 15.85) / 0.9))
        sl = lerp(470, 618, u)
        sr = lerp(800, 664, u)
    return sl, sr


def gap_amp(t):
    return 1.45 * _gap_amp(t)


def _gap_amp(t):
    """Высота щели на пике бугра (px)."""
    if t < T_NO:
        return lerp(78, 62, ease_io(clamp((t - 11.9) / 1.15)))
    if t < T_SIT:
        # раздувается на «закрывался»
        return 62 + 20 * smooth(T_JERK, T_JERK + 0.25, t)
    # Дима сел: сжал
    e = t - T_SIT
    g = 16.0
    if t < T_UP:
        g = lerp(82, 16, ease_out(e / 0.15))
    elif t < T_SIT2:
        u = (t - T_UP) / (T_SIT2 - T_UP)
        g = 16 + 44 * math.sin(math.pi * clamp(u)) ** 1.2
    elif t < T_SIT2 + 0.3:
        g = 14 + 6 * math.exp(-(t - T_SIT2) * 12) * math.cos((t - T_SIT2) * 24)
    else:
        g = 13
    if t > 15.85:
        g = 13 * (1 - ease_io(clamp((t - 15.85) / 0.9)))
    return g


def hump_amp(t):
    if t < T_NO:
        return lerp(46, 40, ease_io(clamp((t - 11.9) / 1.15)))
    if t < T_SIT:
        return 40 + 26 * smooth(T_JERK, T_JERK + 0.25, t)
    e = t - T_SIT
    if t < T_UP:
        return lerp(66, 6, ease_out(e / 0.15))
    if t < T_SIT2:
        return 6 + 34 * math.sin(math.pi * clamp((t - T_UP) / (T_SIT2 - T_UP))) ** 1.2
    h = 6
    if t > 15.85:
        h = 6 * (1 - ease_io(clamp((t - 15.85) / 0.9)))
    # после защёлки — бугор изнутри «кот»: бежит по крышке
    if t > T_SHUT:
        e = t - T_SHUT
        h += 11 * smooth(0, 0.3, e) * (0.6 + 0.4 * math.sin(e * 17))
    return h


def swell(t):
    """(sx, sy) раздувание чемодана вокруг низа: 13.18 → вздох, дрожь; Дима сжимает; отскоки."""
    sx = sy = 0.0
    if T_JERK <= t < T_SIT:
        e = t - T_JERK
        sx = 0.055 * (1 - math.exp(-e * 16)) + 0.012 * math.sin(e * 75) * math.exp(-e * 2.5)
        sy = 0.04 * (1 - math.exp(-e * 16)) + 0.012 * math.sin(e * 75 + 1) * math.exp(-e * 2.5)
    if t >= T_SIT:
        for c, k in ((T_SIT, 1.0), (T_SIT2, 0.45)):
            e = t - c
            if e > 0:
                a = k * math.exp(-e * 11) * math.cos(e * 30)
                sx += 0.075 * a
                sy -= 0.12 * a
        # между сиденьями чемодан распрямляется
        if T_UP <= t < T_SIT2:
            u = clamp((t - T_UP) / (T_SIT2 - T_UP))
            sy += 0.03 * math.sin(math.pi * u)
        if t >= T_SHUT:
            e = t - T_SHUT
            sx += 0.012 * math.sin(e * 46) * math.exp(-e * 2.2)
            sy += 0.012 * math.sin(e * 46 + 1.3) * math.exp(-e * 2.2)
    return sx, sy


def gap_fn(t):
    sl, sr = sliders(t)
    G, Hp = gap_amp(t), hump_amp(t)

    def gap(x):
        bump = math.exp(-(((x - XB) / WB) ** 2))
        m = smooth(sl - 30, sl + 70, x) * (1 - smooth(sr - 70, sr + 30, x))
        # у самых бегунков щель сужается плавно
        return G * (0.30 + 0.70 * bump) * m

    def hump(x):
        bump = math.exp(-(((x - XB) / (WB * 1.5)) ** 2))
        m = smooth(sl - 60, sl + 90, x) * (1 - smooth(sr - 90, sr + 60, x))
        return Hp * bump * m

    return gap, hump, sl, sr


def lid_polys(gap, hump):
    xs = [X0 + 40 + 40 * i for i in range(int((X1 - X0 - 80) / 40) + 1)]
    top = [(x, LIDTOP - gap(x) * 0.9 - hump(x)) for x in xs]
    bot = [(x, SEAM - gap(x)) for x in xs]
    pts = [(X0, SEAM, 1), (X0 - 3, LIDTOP + 44), (X0 + 12, LIDTOP + 6)] + top + [(X1 - 12, LIDTOP + 6), (X1 + 3, LIDTOP + 44), (X1, SEAM, 1)] + bot[::-1]
    return pts, top, bot


def base_poly():
    return [(X0 + 2, SEAM, 1), (X1 - 2, SEAM, 1), (X1 + 2, FL - 34), (X1 - 22, FL - 2), (X0 + 22, FL - 2), (X0 - 2, FL - 34)]


def zip_tape(pts, color):
    return line(pts, 12, color, taper=0.05, wmin=1.0, seed=SEED + 11, peak=.5)


def teeth_row(xs_, y_fn, up, color="#d7dbe4"):
    out = []
    for i, x in enumerate(xs_):
        y = y_fn(x)
        d = -1 if up else 1
        out.append(blob(rect_pts(x - 3.4, y, x + 3.4, y + d * 9, 1.2), color, 1.0))
    return "".join(out)


def clutter(t, gap, lid_top_pts):
    """Вещи в щели: цветная вязь, тёмная тень; клип — по форме щели."""
    pts = [(x, SEAM - gap(x) - 4) for x in range(int(X0) + 20, int(X1) - 19, 20)]
    pts = [(X0 + 20, SEAM + 2, 1)] + pts + [(X1 - 20, SEAM + 2, 1)]
    cid = lib.clip_of(pts)
    s = [blob([(X0, SEAM - 120), (X1, SEAM - 120), (X1, SEAM + 4), (X0, SEAM + 4)], "#2d2030")]
    cols = ["#c9503c", "#e0b04a", "#5f8a4e", "#a8648f", "#4d6fae", "#c9503c"]
    for i, c in enumerate(cols):
        x = 310 + i * 100 + 6 * math.sin(t * 5 + i)
        s.append(blob(ellipse_pts(x, SEAM - 28, 76, 52, 12, jitter=0.0), c))
        s.append(line([(x - 50, SEAM - 40), (x - 10, SEAM - 60), (x + 40, SEAM - 40)], 4, lib.mul(c, (.7, .7, .7)), seed=SEED + 30 + i, op=.8))
    return f'<g clip-path="url(#{cid})">{"".join(s)}</g>'


def cat_shadow(t, gap):
    """Тёмная тень в щели (кот): силуэт с ушами и двумя бликами глаз, виден, когда щель раскрыта (отскок 14.64–15.12)."""
    g = gap(560)
    if t < T_UP - 0.02 or g < 18:
        return ""
    x, y = 556, SEAM - 4
    k = clamp((g - 18) / 28)
    pts = [(x - 60, y, 1), (x - 56, y - 22), (x - 40, y - 34), (x - 38, y - 54, 1), (x - 24, y - 40), (x + 10, y - 42), (x + 26, y - 56, 1), (x + 34, y - 36),
           (x + 54, y - 20), (x + 60, y, 1)]
    s = [blob(pts, "#0e0a12")]
    for dx in (-18, 22):
        s.append(blob(ellipse_pts(x + dx, y - 22, 6.5, 4.5 + 3 * k, 8), "#d7f06a", .95))
    return "".join(s)


def zipper_layer(t, gap, sl, sr, lid_pts):
    s = []
    xs = [X0 + 14 + 8 * i for i in range(int((X1 - X0 - 28) / 8) + 1)]
    # закрытые участки: зубцы замкнуты
    cl = [x for x in xs if x < sl or x > sr]
    s.append(line([(X0 + 10, SEAM - 6), (X1 - 10, SEAM - 6)], 3, "#1a2a33", taper=0.02, wmin=1, seed=SEED + 50, op=.0))
    # ленты по краям шва (тёмно-бирюзовые) — на открытой части раздвинуты
    top_edge = [(x, SEAM - gap(x)) for x in xs]
    s.append(zip_tape([(x, y + 7) for x, y in top_edge], TEAL_D))
    s.append(zip_tape([(x, SEAM - 6) for x in xs], TEAL_D))
    for x in cl:
        yy = SEAM - gap(x) * 0.5 - 4
        zig = 3.4 if int(x / 8) % 2 == 0 else -3.4
        s.append(blob(rect_pts(x - 3.2 + zig * 0.3, yy - 8, x + 3.2 + zig * 0.3, yy + 8, 1.2), "#dfe3ec"))
    op = [x for x in xs if sl + 14 < x < sr - 14]
    s.append(teeth_row(op[::1], lambda x: SEAM - gap(x) + 6, False))
    s.append(teeth_row(op[::1], lambda x: SEAM - 6, True))
    return "".join(s)


def slider(x, y, tilt, sd, flip=1, pull=24):
    """Бегунок с язычком-тягой, висящей вниз."""
    body = shape(rect_pts(x - 26, y - 20, x + 26, y + 18, 9), "#d9dde6", blob(rect_pts(x - 26, y + 4, x + 26, y + 18, 5), "#9aa1b2", .9) +
                 line([(x - 16, y - 12), (x + 8, y - 13)], 3, "#ffffff", seed=sd + 1, op=.9), w=3.8, seed=sd)
    p0 = (x + flip * 4, y + 16)
    p1 = (x + flip * 4 + tilt * 0.5, y + 16 + pull * 0.55)
    p2 = (x + flip * 4 + tilt, y + 16 + pull + 40)
    tab = shape(lib.band([p0, p1, p2], 22, 30, step=4, cap=True), "#c9cdd8", blob([(x - 2, y + 40), (x + 18, y + 40), (x + 18, y + 80), (x - 2, y + 80)], "#9aa1b2", .0), w=3.6, seed=sd + 2)
    return tab + body


def padlock(x, y, rot, open_k, sd):
    """Висячий замочек: корпус-латунь, дужка (открыта — поднята и сдвинута)."""
    lift = 22 * open_k
    shackle = lib.band([(x - 17, y - 14 - lift * .2), (x - 17, y - 34 - lift), (x - 2, y - 52 - lift), (x + 17, y - 34 - lift), (x + 17 + (14 * open_k), y - 14 - lift * .7)], 11, 11, step=3, cap=False)
    s = [shape(shackle, "#c9cdd8", "", w=3.4, seed=sd)]
    body = shape(rect_pts(x - 30, y - 16, x + 30, y + 40, 9), "#e0b04a", blob(rect_pts(x - 30, y + 22, x + 30, y + 40, 6), "#b98a2c", .9) +
                 line([(x - 22, y - 8), (x - 22, y + 24)], 4, "#fff0b0", seed=sd + 1, op=.9) + blob(ellipse_pts(x, y + 8, 6, 6, 8), "#3a2c10") +
                 blob([(x - 3, y + 8), (x + 3, y + 8), (x + 4, y + 24), (x - 4, y + 24)], "#3a2c10"), w=4.0, seed=sd + 2)
    return f'<g transform="rotate({f(rot)} {f(x)} {f(y - 40)})">{"".join(s)}{body}</g>'


def case_svg(t):
    gap, hump, sl, sr = gap_fn(t)
    lid_pts, top, bot = lid_polys(gap, hump)
    s = []
    s.append(clutter(t, gap, top))
    s.append(cat_shadow(t, gap))
    # основание
    bp = base_poly()
    g = lin_grad([(0, TEAL, 1), (1, TEAL_D, 1)], 0, 0, 0, 1)
    inner = line([(X0 + 40, FL - 40), (X1 - 40, FL - 40)], 4, TEAL_L, seed=SEED + 60, op=.6)
    inner += blob(rect_pts(X0, SEAM, X1, SEAM + 20), "#1f5a6c", .55)
    # ремни-стяжки на основании
    for bx in (300, 790):
        inner += blob(rect_pts(bx - 22, SEAM, bx + 22, FL), "#2a4a55", .95) + line([(bx - 22, SEAM), (bx - 22, FL)], 2.4, "#16313a", seed=SEED + 61 + bx % 7, op=.8)
    s.append(shape(bp, f"url(#{g})", inner, w=6.0, seed=SEED + 62))
    for sx_, a in ((X0 - 2, 1), (X1 + 2, -1)):
        s.append(shape([(sx_ - a * 4 * 0, FL - 70), (sx_ + a * 38, FL - 70), (sx_ + a * 34, FL + 4), (sx_ - a * 2, FL + 4)], "#27424c", "", w=4.4, seed=SEED + 63 + a))
    # крышка
    cid = lib.clip_of(lid_pts)
    g2 = lin_grad([(0, TEAL_L, 1), (.5, TEAL, 1), (1, TEAL_D, 1)], 0, 0, 0, 1)
    ribs = "".join(line([(x, LIDTOP - 80), (x + 2, SEAM)], 2.6, TEAL_D, seed=SEED + 70 + i, op=.35) for i, x in enumerate((210, 400, 480, 700, 860)))
    belts = "".join(blob(rect_pts(bx - 22, LIDTOP - 90, bx + 22, SEAM + 4), "#2a4a55", .95) +
                    line([(bx - 22, LIDTOP - 90), (bx - 22, SEAM)], 2.4, "#16313a", seed=SEED + 80 + bx % 7, op=.8) for bx in (300, 790))
    shine = line([(X0 + 40, LIDTOP + 14), (X1 - 40, LIDTOP + 12)], 6, "#a7e0ea", seed=SEED + 90, op=.55, taper=.5, wmin=.4)
    shade = blob([(X0, SEAM - 40), (X1, SEAM - 40), (X1, SEAM + 10), (X0, SEAM + 10)], "#1f5a6c", .4)
    s.append(shape(lid_pts, f"url(#{g2})", f'<g>{ribs}{belts}{shine}{shade}</g>', w=6.2, seed=SEED + 91))
    # ручка на крышке
    hy = LIDTOP - 0.9 * gap(CXC) - hump(CXC)
    s.append(shape(lib.band([(CXC - 62, hy + 4), (CXC - 52, hy - 28), (CXC + 52, hy - 28), (CXC + 62, hy + 4)], 20, 20, step=4, cap=False), "#2b2f3a",
                   line([(CXC - 46, hy - 32), (CXC + 46, hy - 32)], 3, "#6b7186", seed=SEED + 92, op=.8), w=3.6, seed=SEED + 93))
    s.append(zipper_layer(t, gap, sl, sr, lid_pts))
    # бегунки с замочком на левом
    yl = SEAM - gap(sl) * 0.5 - 4
    yr = SEAM - gap(sr) * 0.5 - 4
    swL = 8 * math.sin(t * 7.5) * math.exp(-max(t - T_NO, 0) * 1.0) if t > T_NO - 0.4 else 3 * math.sin(t * 9)
    swR = -6 * math.sin(t * 8.5 + 1) * math.exp(-max(t - T_NO, 0) * 1.0) if t > T_NO - 0.4 else -3 * math.sin(t * 9)
    jerk = math.exp(-(t - T_JERK) * 8) * math.sin((t - T_JERK) * 34) if t >= T_JERK else 0
    closing = t > 15.85
    # в s09 бегунки сходятся — язычки рядом, замок защёлкивается
    if closing:
        closeu = ease_io(clamp((t - 15.85) / 0.9))
        gapx = sr - sl
    s.append(slider(sr, yr, 8 + swR, SEED + 100, -1, 22))
    s.append(slider(sl, yl, -8 + swL, SEED + 110, 1, 22))
    # замок
    if t < T_SHUT - 0.6:
        s.append(padlock(sl + 8 + swL + 24 * jerk * 0.0, yl + 100, 14 * jerk + 10 * math.sin(t * 7), 1.0, SEED + 120))
    else:
        # висит на язычках, дужка закрывается на 16.77 (рывок вниз, «щёлк»)
        k = clamp((t - (T_SHUT - 0.18)) / 0.18)
        e = t - T_SHUT
        click = 6 * math.exp(-max(e, 0) * 12) * math.sin(max(e, 0) * 50) if e > 0 else 0
        s.append(padlock((sl + sr) / 2 + 2, yl + 94 + 8 * max(0, min(1, k)) * (1 if e < 0 else 0) + click, 4 * click, 1 - ease_in(k, 1.0), SEED + 120))
    return "".join(s), gap, hump, sl, sr


def items_out(t, gap):
    """Рукав и штанина, вылезшие из щели и свисающие по передней стенке; при посадке Димы втягиваются."""
    if t < T_JERK + 0.05 or t >= T_UP:
        return ""
    u = ease_out(clamp((t - T_JERK - 0.05) / 0.35), 2)
    if t >= T_SIT:
        u *= 1 - ease_in(clamp((t - T_SIT) / 0.12), 1.0)
    if u <= 0:
        return ""
    wob = math.sin(t * 9) * 0.9
    s = []
    # рукав
    sx, sy = 536, SEAM - gap(536) * 0.5 - 6
    pts = [(sx, sy), (sx - 10 * u, sy + 40 * u), (sx - 30 * u + 3 * wob, sy + 86 * u), (sx - 22 * u + 6 * wob, sy + 124 * u)]
    s.append(shape(lib.band(pts, 62, 56, step=5, cap=True), "#c9503c", line([(sx - 14 * u, sy + 20 * u), (sx - 24 * u, sy + 90 * u)], 3, "#8f2f22", seed=SEED + 130, op=.8), w=4.6, seed=SEED + 131))
    cx_, cy_ = pts[-1]
    s.append(shape(rect_pts(cx_ - 30, cy_ - 8, cx_ + 28, cy_ + 20, 6), "#8f2f22", "".join(line([(cx_ - 26 + k * 10, cy_ - 6), (cx_ - 26 + k * 10, cy_ + 18)], 1.8, "#5f1f16", seed=SEED + 132 + k, op=.7) for k in range(1, 6)), w=3.8, seed=SEED + 133))
    # штанина
    tx, ty = 716, SEAM - gap(716) * 0.5 - 6
    pts = [(tx, ty), (tx + 10 * u, ty + 44 * u), (tx + 26 * u + 3 * wob, ty + 96 * u), (tx + 20 * u - 5 * wob, ty + 136 * u)]
    s.append(shape(lib.band(pts, 74, 66, step=5, cap=True), "#4d6fae", line([(tx + 14 * u, ty + 20 * u), (tx + 28 * u, ty + 100 * u)], 3, "#2c4577", seed=SEED + 134, op=.8), w=4.6, seed=SEED + 135))
    ex, ey = pts[-1]
    s.append(shape(rect_pts(ex - 36, ey - 6, ex + 34, ey + 14, 5), "#33528c", line([(ex - 32, ey + 2), (ex + 30, ey + 2)], 2, "#8fa6d4", seed=SEED + 136, op=.8), w=3.8, seed=SEED + 137))
    return "".join(s)


def socks(t):
    """Носки вылетают из щели на 14.50, 14.60, 14.72 и 15.16 (тот же рывок на втором сидении)."""
    s = []
    launches = [(14.50, 500, -420, -560, 380), (14.60, 580, -520, -430, -300), (14.72, 440, -300, -380, 520), (15.16, 620, -380, -330, 300)]
    for i, (t0, x0, vx, vy, spin) in enumerate(launches):
        e = t - t0
        if e < 0 or e > 1.1:
            continue
        x = x0 + vx * e * 0.5 + 0.0
        y = SEAM - 20 + vy * e * 0.55 + 1250 * e * e * 0.5 * 0.6
        if y > FL - 24 and e > 0.1:
            y = FL - 24 - 18 * abs(math.sin((e - 0.1) * 14)) * math.exp(-(e - 0.1) * 4)
            spin = 0
        rot = spin * e if spin else 12 * math.sin(e * 8)
        col = ["#f2ede0", "#e0b04a", "#c9ced8", "#f2ede0"][i]
        s.append(place(props.sock(col, SEED + 140 + i * 4, ["#c9503c", "#4d6fae", "#c9503c", "#5f8a4e"][i]), x, y, rot, 0.95))
    return "".join(s)


# ═════════════════════════ Дима ═════════════════════════
HIPSIT = (748.0, 912.0)
SEATY = LIDTOP - 6


def run_pose(t, sit_dy=0.0):
    """Бег с левого края, прыжок, посадка; потом отскок и снова посадка; сидит. Возвращает pose словарём и (hip, squash_pivot)."""
    T0 = 13.88
    FLY0 = 14.20
    ankle_floor = FL - 58
    hip_run_y = ankle_floor - 392
    if t < FLY0:
        u = (t - T0) / (FLY0 - T0)
        x = lerp(-210, 560, ease_in(u, 1.25) * 0.4 + u * 0.6)
        th = (t - T0) * 2 * math.pi / 0.30
        bob = 22 * abs(math.sin(th))
        hip = (x, hip_run_y - bob + 8)
        feet = {}
        for k, side in enumerate(("n", "f")):
            ph = th + math.pi * k
            ax = hip[0] + 150 * math.cos(ph) + 20
            ay = ankle_floor - 140 * max(0, -math.sin(ph))
            feet[side] = ((ax, ay), 0.35 * math.sin(ph))
        arms = {"n": ("ik", (hip[0] + 40 + 150 * math.sin(th), hip[1] - 80 + 60 * math.cos(th))),
                "f": ("ik", (hip[0] + 40 - 150 * math.sin(th), hip[1] - 80 - 60 * math.cos(th)))}
        return dict(hip=hip, lean=0.34, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"}, state="run", head=0.0, expr_k="panic"), hip
    if t < T_SIT:
        u = (t - FLY0) / (T_SIT - FLY0)
        hip = (lerp(560, HIPSIT[0], u), lerp(hip_run_y + 8, HIPSIT[1], u) - 190 * 4 * u * (1 - u))
        a1 = ankle_floor
        feet = {"n": ((hip[0] + lerp(120, 250, u), min(a1, hip[1] + lerp(290, 262, u))), 0.5 * (1 - u)),
                "f": ((hip[0] + lerp(40, 210, u), min(a1, hip[1] + lerp(250, 270, u))), 0.2)}
        arms = {"n": ("ik", (hip[0] + lerp(60, 160, u), hip[1] - lerp(-60, 10, u) - 150 * (1 - u))),
                "f": ("ik", (hip[0] + lerp(30, 120, u), hip[1] - 120 * (1 - u) - 40))}
        return dict(hip=hip, lean=lerp(0.34, 0.22, u), feet=feet, arms=arms, hands={"n": "fist", "f": "fist"}, state="fly", head=0.0, expr_k="panic"), hip
    # посадка: до T_UP сидит, T_UP..T_SIT2 отскок вверх, T_SIT2.. сидит
    hy = HIPSIT[1]
    state = "sit"
    if T_UP <= t < T_SIT2:
        u = (t - T_UP) / (T_SIT2 - T_UP)
        hy = HIPSIT[1] - 170 * 4 * u * (1 - u) * (1.0)
        state = "bounce"
    hip = (HIPSIT[0], hy + sit_dy)
    ank_y = min(ankle_floor, hip[1] + 270)
    feet = {"n": ((hip[0] + 250, ank_y), 0.0), "f": ((hip[0] + 200, ank_y), 0.0)}
    if state == "bounce":
        u = (t - T_UP) / (T_SIT2 - T_UP)
        feet = {"n": ((hip[0] + 230 - 40 * math.sin(math.pi * u), ank_y - 20 * math.sin(math.pi * u)), 0.5 * math.sin(math.pi * u)),
                "f": ((hip[0] + 190, ank_y - 30 * math.sin(math.pi * u)), 0.3 * math.sin(math.pi * u))}
        arms = {"n": ("ik", (hip[0] - 150, hip[1] - 230 * math.sin(math.pi * u) - 20)), "f": ("ik", (hip[0] + 230, hip[1] - 250 * math.sin(math.pi * u) - 40))}
    else:
        sag = smooth(15.3, 15.9, t)
        arms = {"n": ("ik", (hip[0] + 210, hip[1] + 20)), "f": ("ik", (hip[0] + 150, hip[1] + 10))}
    return dict(hip=hip, lean=0.18 if state == "sit" else 0.05, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"}, state=state, head=0.0, expr_k="sit"), hip


def dima_svg(t):
    pose, hip = run_pose(t)
    st = pose.pop("state")
    pose.pop("expr_k")
    mouth, brows, lid = "pant", "worry", 0.85
    if st == "run":
        mouth, brows, lid = "pant", "strain", 0.8
    elif st == "fly":
        mouth, brows, lid = "gape", "up", 1.0
    elif st == "sit":
        e = t - (T_SIT if t < T_SIT2 else T_SIT2)
        mouth, brows, lid = ("strain", "strain", 0.5) if t < 15.5 else (("strain", "worry", 0.45) if t < 16.7 else ("relief", "glad", 0.35))
        if t >= 16.77:
            mouth, brows, lid = "relief", "glad", 0.3
        if t < T_SIT + 0.25:
            mouth, brows, lid = "gape", "up", 1.0
    elif st == "bounce":
        mouth, brows, lid = "gape", "up", 1.0
    wob = math.sin(t * 5.0)
    pose["expr"] = {"lid": lid, "look": (0.9, 0.3), "brows": brows, "mouth": mouth, "hair": 4 * math.sin(t * 9) + (10 if st in ("fly", "bounce") else 0)}
    pose["head_ang"] = 0.05 * wob - (0.12 if st == "sit" and t > 16.7 else 0)
    pose["hood"] = 6 * math.sin(t * 8) if st != "sit" else 2
    pose["strings"] = (4 * math.sin(t * 6), 2)
    dima.BS = BS
    dima.LWK = 1.15
    g, _ = dima.draw(pose)
    # сжатие и отскок тела (вокруг точки посадки)
    sq = 0.0
    for c, k in ((T_SIT, 1.0), (T_SIT2, 0.55)):
        e = t - c
        if e > 0:
            sq += k * math.exp(-e * 10) * math.cos(e * 28)
    if T_UP <= t < T_SIT2:  # растянут в полёте вверх
        u = (t - T_UP) / (T_SIT2 - T_UP)
        sq -= 0.10 * math.sin(math.pi * u)
    px, py = HIPSIT[0], SEATY
    return f'<g transform="translate({f(px)} {f(py)}) scale({1 + 0.10 * sq:.4f} {1 - 0.17 * sq:.4f}) translate({f(-px)} {f(-py)})">{g}</g>', sq


def relief_puffs(t):
    """Выдох с облегчением после защёлки: облачка у рта Димы."""
    e = t - (T_SHUT + 0.12)
    if not 0 < e < 0.7:
        return ""
    k = e / 0.7
    s = []
    hx, hy = HIPSIT[0] + 62, HIPSIT[1] - 365
    for j in range(4):
        r = (16 + 14 * j) * (0.5 + k)
        s.append(blob(ellipse_pts(hx + 70 * k + j * 40 * k, hy + 10 - 24 * k * (1 + j * .3), r, r * .8, 10), "#fff8ea", .9 * (1 - k)))
        s.append(blob(ellipse_pts(hx + 70 * k + j * 40 * k, hy + 10 - 24 * k * (1 + j * .3), r, r * .8, 10), "#e6d6b4", .25 * (1 - k)))
    return "".join(s)


# ═════════════════════════ фон, эффекты, камера ═════════════════════════
def background(t):
    s = []
    g = lin_grad([(0, "#f3e6cb", 1), (1, "#e6d1a8", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="-1500" width="4200" height="{1500 + 1196}" fill="url(#{g})"/>')
    for x in range(-1400, 2500, 110):
        s.append(f'<rect x="{x}" y="-1500" width="46" height="{1500 + 1196}" fill="#dcc79c" opacity=".3"/>')
    # окно: тёплый свет
    gl = rad_grad([(0, "#fff6d8", .55), (1, "#fff6d8", 0)], 700, 520, 800, 700)
    s.append(f'<rect x="-1500" y="-1500" width="4200" height="3200" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
    # плинтус
    s.append(blob(rect_pts(-1500, 1150, 2700, 1200), "#f7f2e6"))
    s.append(line([(-1500, 1150), (2700, 1150)], 4, INK, taper=.02, wmin=1, seed=SEED + 200))
    # пол
    gf = lin_grad([(0, "#c9a06c", 1), (1, "#a97f4f", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="1200" width="4200" height="1900" fill="url(#{gf})"/>')
    s.append(line([(-1500, 1200), (2700, 1200)], 5, INK, taper=.02, wmin=1, seed=SEED + 201))
    for k in range(1, 12):
        y = 1200 + k * 70 + k * k * 2
        s.append(line([(-1500, y), (2700, y + 4)], 3, "#8c6238", taper=.05, wmin=.9, seed=SEED + 210 + k, op=.5))
    for k in range(-8, 14):
        s.append(line([(k * 300 + (k % 3) * 70, 1200), (k * 300 - 50 + (k % 3) * 70, 3000)], 2.6, "#8c6238", taper=.05, wmin=.9, seed=SEED + 240 + abs(k), op=.4))
    s.append(props.shadow(CXC + 20, FL + 6, 440, 34, .5, 12))
    return "".join(s)


def impact_fx(t):
    s = []
    for c, k in ((T_SIT, 1.0), (T_SIT2, 0.6)):
        e = t - c
        if 0 < e < 0.4:
            kk = e / 0.4
            x, y = HIPSIT[0] - 90, LIDTOP - 6
            s.append(props.burst(x, y, kk, 12, 70 * k + 40, 200 * k + 80, 10 * k + 4, "#fff4c2", SEED + 300 + int(c * 10), a0=190, spread=200))
            s.append(props.dust(x - 80, FL - 6, kk, 6, 240 * k + 60, 36, SEED + 320, rmax=26))
    # хруст: зигзаг-трещины на крышке слева от Димы
    e = t - T_SIT
    if 0 < e < 0.55:
        kk = clamp(e / 0.12)
        a = 1 - clamp((e - 0.3) / 0.25)
        for j, (x0, y0) in enumerate(((596, LIDTOP + 18), (660, LIDTOP + 30))):
            pts = [(x0, y0), (x0 - 18, y0 + 14), (x0 - 4, y0 + 28), (x0 - 24, y0 + 46)]
            n = max(2, int(len(pts) * kk))
            s.append(line(pts[:n], 5, "#1c1622", taper=.2, wmin=.4, seed=SEED + 340 + j, op=a))
    return "".join(s)


def lid_sparks(t):
    """Блик на замке и искры на защёлке (16.77)."""
    e = t - T_SHUT
    s = []
    sl, sr = sliders(t)
    mx = (sl + sr) / 2
    if 0 < e < 0.45:
        k = e / 0.45
        s.append(props.glint(mx + 8, SEAM + 20, k, 58))
        s.append(props.burst(mx + 8, SEAM + 40, k, 10, 50, 130, 9, "#fff4c2", SEED + 360))
    # лёгкий блик-скольжение по крышке при закрытии
    return "".join(s)


def camera(t, sid):
    if sid == "s07":
        u = ease_io(clamp((t - 11.94) / 2.34))
        sc = lerp(1.7, 2.0, u)
        ccx, ccy = lerp(570, 620, u), lerp(1040, 1060, u)
        rot = lerp(-3.0, 1.4, u) + 0.6 * math.sin(t * 2.2)
        for c, a, f_ in ((T_NO, 1.2, 30), (T_JERK, 2.5, 36)):
            e = t - c
            if e > 0:
                k = math.exp(-e * 8)
                ccx += 14 * a * k * math.sin(e * f_)
                ccy += 10 * a * k * math.cos(e * f_ * 0.8)
                rot += 1.4 * a * k * math.sin(e * 24)
                sc *= 1 + 0.03 * a * k
        if t >= T_JERK:
            e = t - T_JERK
            ccx += 4 * math.sin(e * 70) * math.exp(-e * 1.2)
            ccy += 3 * math.sin(e * 83) * math.exp(-e * 1.2)
        return cam(ccx, ccy, sc, rot)
    if sid == "s08":
        u = ease_io(clamp((t - 13.88) / 2.14))
        sc = lerp(0.95, 1.42, u)
        ccx = lerp(420, 700, u)
        ccy = lerp(960, 960, u)
        rot = lerp(2.0, -1.2, u) + 0.4 * math.sin(t * 2.0)
        for c, a in ((T_SIT, 1.0), (T_SIT2, 0.6)):
            e = t - c
            if e > 0:
                k = math.exp(-e * 8)
                sc *= 1 + 0.06 * a * k
                ccy += 22 * a * k * math.sin(e * 40)
                rot += 2.6 * a * k * math.sin(e * 26)
        return cam(ccx, ccy, sc, rot)
    # s09: предельно крупно молния и замок, после защёлки отъезд к Диме
    a = 15.62
    u = ease_io(clamp((t - a) / 1.15))
    sl, sr = sliders(t)
    mx = (sl + sr) / 2
    sc = lerp(2.9, 3.4, ease_io(clamp((t - a) / 1.2)))
    ccx, ccy = mx + 10, SEAM + 10
    rot = lerp(-3.5, 2.0, u) + 0.7 * math.sin(t * 2.4)
    e = t - T_SHUT
    if e > 0:
        k = math.exp(-e * 9)
        sc *= 1 + 0.07 * k
        ccy += 14 * k * math.sin(e * 44)
        rot += 2.8 * k * math.sin(e * 30)
        w = ease_io(clamp((e - 0.30) / 0.72))
        sc = lerp(sc, 0.98, w)
        ccx = lerp(ccx, 640, w)
        ccy = lerp(ccy, 930, w)
        rot = lerp(rot, -0.6, w)
    return cam(ccx, ccy, sc, rot)


def frame(sid, t):
    lib.dyn_begin()
    s = [background(t)]
    sx, sy = swell(t)
    cs, gap, hump, sl, sr = case_svg(t)
    s.append(f'<g transform="translate({f(CXC)} {f(FL)}) scale({1 + sx:.4f} {1 + sy:.4f}) translate({f(-CXC)} {f(-FL)})">{cs}{items_out(t, gap)}</g>')
    s.append(socks(t))
    if sid != "s07":
        dsv, sq = dima_svg(t)
        s.append(dsv)
        s.append(relief_puffs(t))
    s.append(impact_fx(t))
    s.append(lid_sparks(t))
    return svg(f'<rect width="{W}" height="{H}" fill="#e6d1a8"/><g transform="{camera(sid, t) if False else camera(t, sid)}">{"".join(s)}</g>')
