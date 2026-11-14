"""Рилс 58 группа B: s08 (12.4–15.4) 2D-метафора «рабочая память»: стол с табличкой-значком (схема мозга, без букв) и стопкой
задач-листков; на «занимают» (12.52) сверху падают серые тревожные облака и заваливают полстола, на «память» (13.36) стол
прогибается, на «решаешь» (14.54) последний листок зажат облаками. Камера: сверху вниз, наезд к зажатому листку."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import brain_art  # noqa: E402
import fxprops as fp  # noqa: E402
import lib  # noqa: E402
import props  # noqa: E402
from lib import H, W, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rect_pts, shape, smooth, spring, svg  # noqa: E402

SEED = 8000
T_FALL0 = 12.52
T_SAG = 13.36
T_JAM = 14.54
TOP_Y, FRONT_Y = 1030, 1180          # дальний и передний край столешницы (без прогиба)
X0, X1 = 60, 1020
FLOOR = 1560
SHEET_K = 3.3


def lerp(a, b, u):
    return a + (b - a) * u


def sag_amt(t):
    """Прогиб столешницы в px: на «память» проседает с лёгким отскоком, на «решаешь» ещё чуть."""
    if t < T_SAG:
        return 0.0
    return 52 * spring(t - T_SAG, 2.2, 6.0) + 16 * smooth(T_JAM - .1, T_JAM + .5, t)


def sag_at(x, a):
    u = (x - (X0 + X1) / 2) / ((X1 - X0) / 2)
    return a * max(0.0, 1 - u * u)


def background():
    g = lin_grad([(0, "#e9eef2", 1), (1, "#d5dde4", 1)], 0, 0, 0, 1)
    s = [f'<rect x="-600" y="-900" width="2300" height="{FLOOR + 900}" fill="url(#{g})"/>']
    for x in range(-500, 1600, 230):
        s.append(f'<rect x="{x}" y="-900" width="95" height="{FLOOR + 900}" fill="#dde4ea"/>')
    s.append(f'<rect x="-600" y="{FLOOR}" width="2300" height="900" fill="#cba070"/>')
    s.append(line([(-600, FLOOR), (1700, FLOOR)], 5, "#7a5430", taper=0, wmin=1, seed=SEED + 1))
    for i, y in enumerate((FLOOR + 90, FLOOR + 250, FLOOR + 470)):
        s.append(line([(-600, y), (1700, y + 4)], 3, "#a97542", taper=0, wmin=1, seed=SEED + 2 + i, op=.8))
    return "".join(s)


def desk(a):
    """Парта (палитра props): столешница с прогибом a, торец, ножки изгибаются."""
    s = []
    n = 14
    xs = [X0 + (X1 - X0) * i / n for i in range(n + 1)]
    fr = [(x, FRONT_Y + sag_at(x, a)) for x in xs]
    bk = [(x + (20 if i == 0 else -20 if i == n else 0) * 0, TOP_Y + sag_at(x, a * .75)) for i, x in enumerate(xs)]
    # ножки (сзади)
    for k, lx in enumerate((X0 + 54, X1 - 54)):
        top_y = FRONT_Y + sag_at(lx, a) + 18
        bow = (-1 if k == 0 else 1) * a * .35
        pts = [(lx - 8, top_y, 1), (lx + 8, top_y, 1), (lx + 8 + bow, (top_y + FLOOR) / 2), (lx + 8, FLOOR, 1), (lx - 8, FLOOR, 1), (lx - 8 + bow, (top_y + FLOOR) / 2)]
        s.append(shape(pts, props.C_DESK_LEG, blob([(lx + 2, top_y), (lx + 8, top_y), (lx + 8, FLOOR), (lx + 2, FLOOR)], "#5f676d", .9), w=4.6, seed=SEED + 10 + k))
        s.append(shape(rect_pts(lx - 24, FLOOR - 9, lx + 24, FLOOR, 2), "#5F666C", "", w=3.6, seed=SEED + 12 + k))
    s.append(shape([(X0 + 80, FRONT_Y + 230 + sag_at(540, a * .5)), (X1 - 80, FRONT_Y + 230 + sag_at(540, a * .5)), (X1 - 80, FRONT_Y + 246 + sag_at(540, a * .5)),
                    (X0 + 80, FRONT_Y + 246 + sag_at(540, a * .5))], props.C_DESK_LEG, "", w=3.6, seed=SEED + 14))
    # торец (передняя панель)
    edge = fr + [(x, y + 40) for x, y in fr[::-1]]
    s.append(shape(edge, props.C_DESK_END, blob([(p[0], p[1] + 28) for p in fr] + [(p[0], p[1] + 40) for p in fr[::-1]], mix(props.C_DESK_END, "#000000", .2)), w=5.2, seed=SEED + 15))
    # поверхность
    top = [(X0, FRONT_Y + sag_at(X0, a), 1)] + fr[1:-1] + [(X1, FRONT_Y + sag_at(X1, a), 1), (X1 - 40, bk[-1][1], 1)] + bk[-2:0:-1] + [(X0 + 40, bk[0][1], 1)]
    ti = line([(X0 + 120, TOP_Y + 50), (X0 + 520, TOP_Y + 56)], 3.0, mix(props.C_DESK, "#8a6538", .5), taper=.4, wmin=.5, seed=SEED + 16, peak=.5)
    ti += line([(X0 + 300, TOP_Y + 110), (X1 - 60, TOP_Y + 100)], 3.0, mix(props.C_DESK, "#8a6538", .5), taper=.4, wmin=.5, seed=SEED + 17, peak=.5)
    ti += blob([(X1 - 260, FRONT_Y), (X1, FRONT_Y), (X1 - 40, TOP_Y), (X1 - 240, TOP_Y)], mix(props.C_DESK, "#8a6538", .25))
    s.append(shape(top, props.C_DESK, ti, w=5.0, seed=SEED + 18))
    return "".join(s)


def plaque(t, a):
    """Табличка «рабочая память»: бумажно-белая плашка на ножке-стойке, на ней схема мозга (без букв)."""
    px = 905
    py = TOP_Y + 40 + sag_at(px, a * .75)
    shake = 0.0
    if t > T_SAG:
        e = t - T_SAG
        shake = 7 * math.exp(-e * 5) * math.sin(e * 38)
    s = []
    s.append(shape([(px - 8, py, 1), (px + 8, py, 1), (px + 8, py - 150, 1), (px - 8, py - 150, 1)], "#9AA0A6", "", w=4, seed=SEED + 20))
    s.append(shape(rect_pts(px - 40, py - 12, px + 40, py + 2, 2), "#7A8288", "", w=3.6, seed=SEED + 21))
    cy = py - 270
    frm = rect_pts(px - 190, cy - 130, px + 190, cy + 130, 14)
    inner = blob(rect_pts(px - 160, cy - 104, px + 160, cy + 104, 8), "#ffffff")
    inner += blob([(px + 100, cy - 104), (px + 160, cy - 104), (px + 160, cy + 104), (px + 80, cy + 104)], "#e8eef4")
    bs = 0.55
    bg = brain_art.brain(0, 0, stem=False)
    inner += f'<g transform="translate({px} {cy + 4}) scale({bs}) translate({-brain_art.BCX} {-brain_art.BCY})">{bg}</g>'
    s.append(f'<g transform="rotate({shake:.2f} {px} {py})">' + shape(frm, "#2C3E66", inner, w=6, seed=SEED + 22) + "</g>")
    return "".join(s)


# ─────────── облака
# x, посадочная высота центра (над столешницей), k, вид, момент старта падения, зерно
CLOUDS = [
    (200, -118, 3.3, 1, 12.52), (410, -110, 3.0, 1, 12.60), (300, -250, 2.9, 0, 12.72),
    (130, -105, 2.8, 0, 12.84), (470, -230, 3.1, 1, 12.96), (250, -360, 2.6, 1, 13.08),
]
FALL_SEC = 0.5


def cloud_state(i, t):
    x, dy, k, kind, ts = CLOUDS[i]
    land = ts + FALL_SEC
    if t < ts:
        return None
    if t < land:
        u = (t - ts) / FALL_SEC
        y_t = lerp(-480, dy, ease_in(u, 2.0))
        sq = 1.0 + 0.08 * u
        return x, y_t, k, kind, 1 - .05 * u, 1 + .06 * u
    e = t - land
    sq = math.exp(-e * 10) * math.cos(e * 26) * .22
    return x, dy, k, kind, 1 + sq, 1 - sq


def cloud_svg(i, t, a, extra_dx=0.0, extra_dy=0.0):
    st = cloud_state(i, t)
    if st is None:
        return ""
    x, dy, k, kind, sx, sy = st
    x += extra_dx
    # посадка на столешницу: высота опоры = столешница + прогиб
    base = TOP_Y + 40 + sag_at(x, a * .8)
    y = base + dy + extra_dy
    # облако высотой ry·k: «подошва» остаётся на месте при сжатии
    ryk = {0: 22, 1: 34, 2: 46}[kind] * k
    cg = props.anx_cloud(0, 0, k, kind, t, SEED + i * 7)
    return f'<g transform="translate({f(x)} {f(y)}) scale({sx:.4f} {sy:.4f})">{cg}</g>'


def sheet(x, dy, rot, t, a, fill=1.0, sd=0, k=SHEET_K, lines=6):
    y = TOP_Y + 48 + dy + sag_at(x, a * .8)
    return props.paper_sheet(x, y, k, fill=fill, rot=rot, t=t, lines=lines, seed=sd)


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    a = sag_amt(t)
    s = [background(), desk(a)]
    # стопка листков справа от кучи облаков; последний — со сдвигом
    jam = smooth(T_JAM - .12, T_JAM + .45, t)
    slide = smooth(T_SAG, T_SAG + .5, t)
    s.append(plaque(t, a))
    s.append(sheet(740, 0, -7 + 4 * slide, t, a, 1.0, 1))
    s.append(sheet(748, -6, 5 - 3 * slide, t, a, 1.0, 2))
    s.append(sheet(735 - 90 * slide, -12, -3 + 6 * slide, t, a, 0.8, 3))
    # последний листок задачи: сверху стопки, на «решаешь» его зажимают облака
    wob = 2.5 * math.sin(t * 38) * jam
    s.append(sheet(690 + wob - 30 * jam, -20 - 4 * jam, 4 - 9 * jam, t, a, 1.0, 4, lines=5))
    # облака падают и копятся слева
    shift = {0: 0, 1: 0}
    for i in range(len(CLOUDS)):
        ex = 0.0
        ey = 0.0
        if t > T_JAM - .1:   # куча оползает вправо и давит
            ex = [95, 120, 70, 80, 150, 60][i] * jam
            ey = [0, 0, 30, 0, 40, 90][i] * jam
        s.append(cloud_svg(i, t, a, ex, ey))
        e = t - (CLOUDS[i][4] + FALL_SEC)
        if 0 < e < .35:
            s.append(fp.dust(CLOUDS[i][0], TOP_Y + 60 + sag_at(CLOUDS[i][0], a), e / .35, 5, 110, 24, SEED + 200 + i, "#e9e6f2", 22))
    # справа налетает облако, зажимает с другой стороны
    if t > T_JAM - .35:
        u = clamp((t - (T_JAM - .35)) / .6)
        cx = lerp(1250, 880, ease_out(u, 2.4))
        cy = TOP_Y + 60 - 120 + sag_at(cx, a) + 6 * math.sin(t * 9)
        s.append(f'<g transform="translate({f(cx)} {f(cy)})">{props.anx_cloud(0, 0, 3.1, 1, t, SEED + 91)}</g>')
        s.append(props.anx_cloud(860 - 40 * jam + 0, TOP_Y - 330 + 330 * ease_io(clamp((t - T_JAM + .1) / .7)) - 230, 3.0, 2, t, SEED + 92, flash=0) if False else "")
    # метки давления: короткие штрихи вокруг листка
    if jam > .3:
        for j in range(6):
            ang = math.radians(210 + j * 20 + 6 * math.sin(t * 20 + j))
            cx0, cy0 = 640, TOP_Y - 70
            r0 = 150
            s.append(line([(cx0 + r0 * math.cos(ang), cy0 + r0 * math.sin(ang)), (cx0 + (r0 - 38) * math.cos(ang), cy0 + (r0 - 38) * math.sin(ang))],
                          6, "#2a2d30", taper=.5, wmin=.3, seed=SEED + 300 + j, op=.4 + .5 * jam))
    # камера: сверху вниз, наезд к листку
    u = clamp((t - 12.2) / 3.2)
    sc = lerp(0.9, 1.7, ease_io(u) ** 1.2)
    cyy = lerp(700, 980, ease_io(clamp(u * 1.1)))
    cxx = lerp(540, 650, ease_io(u))
    rot = lerp(-1.0, 1.2, u)
    kk = math.exp(-(t - T_SAG) * 7) if t > T_SAG else 0
    cyy += 16 * kk * math.sin((t - T_SAG) * 40) if t > T_SAG else 0
    return svg(f'<rect width="{W}" height="{H}" fill="#d5dde4"/><g transform="{cam(cxx, cyy, sc, rot)}">{"".join(s)}</g>')
