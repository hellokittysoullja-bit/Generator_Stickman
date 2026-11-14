"""Сцена chart рилса 50: график исследования Buehler 1994.
s10 (17.96–21.0): «В Канаде» (18.04) значок кленового листа, студенты-человечки в шапках, «диплом» (19.88) выскакивает диплом,
столбик «думали: 34 дня» растёт на «тридцать четыре» (20.48–21.2).
s11 (21.0–24.04): «писали в среднем» студенты потеют, на «пятьдесят шесть» (22.85–23.6) вырастает второй столбик «вышло: 56»
выше первого, удар-наезд на пике, красная стрелка разницы «+22 дня».
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика)."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
from common import punch, shake, speed_streaks, text, whip_in  # noqa: E402
from lib import (INK, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, rad_grad, rect_pts, shape, smooth,
                 spring, svg)

_ST = {}
BASE = 1150.0
PXD = 8.6                        # пикселей на день
B1 = (190, 380)
B2 = (470, 660)
CARD = (70, 300, 1010, 1260)
BLUE, BLUE_D, BLUE_L = "#4a90e2", "#2f6bb8", "#8fbcf2"
RED, RED_D, RED_L = "#ee5a3c", "#bf3a22", "#ff9a7a"


def background():
    s = []
    g = lin_grad([(0, "#f3c98a", 1), (1, "#e6a862", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g})"/>')
    for x in range(-760, 1900, 130):
        s.append(f'<rect x="{x}" y="-800" width="46" height="3600" fill="#ecb878" opacity=".8"/>')
    lg = rad_grad([(0, "#fff0c8", .5), (1, "#ffd890", 0)], 300, 300, 1300, 1300)
    s.append(f'<rect x="-800" y="-800" width="2700" height="3600" fill="url(#{lg})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def card_static():
    x0, y0, x1, y1 = CARD
    s = []
    s.append(blob(rect_pts(x0 + 16, y0 + 26, x1 + 16, y1 + 26, 40), "#4a2a10", .35, blur(14)))
    s.append(shape(rect_pts(x0, y0, x1, y1, 40), "#fffdf6", blob(rect_pts(x1 - 60, y0, x1, y1, 40), "#f1e8d2", .9), w=6, seed=801))
    s.append(text(540, y0 + 74, "ДНЕЙ НА ДИПЛОМ", 44, "#5a6b86"))
    for v in (0, 10, 20, 30, 40, 50, 60):
        y = BASE - v * PXD
        if v:
            s.append(line([(130, y), (1000, y)], 2.4, "#e3dcc6", taper=.0, wmin=1, seed=810 + v, op=.9))
        s.append(text(112, y + 9, str(v), 26, "#a9a28c", anchor="end"))
    return "".join(s)


def maple(x, y, r):
    P = [(0, -1), (0.22, -0.55), (0.55, -0.7), (0.45, -0.25), (0.95, -0.35), (0.72, 0.05), (0.98, 0.25), (0.35, 0.4), (0.4, 0.62),
         (0.06, 0.52), (0.06, 1.0), (-0.06, 1.0), (-0.06, 0.52), (-0.4, 0.62), (-0.35, 0.4), (-0.98, 0.25), (-0.72, 0.05),
         (-0.95, -0.35), (-0.45, -0.25), (-0.55, -0.7), (-0.22, -0.55)]
    return [(x + px * r, y + py * r, 1) for px, py in P]


def badge(t, tp):
    e = t - tp
    k = spring(e, 2.2, 6.0) if e > 0 else 0.0
    if k <= 0.001:
        return ""
    cx, cy = 190, 500
    b = []
    b.append(blob(ellipse_pts(5, 8, 84, 84, 16), "#4a2a10", .3, blur(4)))
    b.append(shape(ellipse_pts(0, 0, 84, 84, 18), "#ffffff", blob(ellipse_pts(14, 18, 70, 66, 14), "#e3e8ef", .9), w=5.4, seed=820))
    b.append(shape(maple(0, 4, 54), "#e4352b", blob([(0, -50), (26, -30), (40, 10), (6, 40), (4, 50)], "#b7231b", .8), w=3.6, seed=821))
    return f'<g transform="translate({cx} {cy}) rotate({-8 * (1 - min(1, e * 3)):.2f}) scale({k:.3f})">{"".join(b)}</g>'


def student(x, y, s, t, col, mood, ph, pop):
    """Студент в квадратной шапке; mood 0 бодрый (подпрыгивает), 1 вспотел, 2 поник."""
    k = spring(pop, 2.4, 6.0) if pop > 0 else 0.0
    if k <= 0.001:
        return ""
    jump = 0.0
    if mood == 0:
        jump = -16 * abs(math.sin(t * 5.5 + ph)) * smooth(0, .25, pop)
    sag = 10 * (mood == 2)
    b = []
    b.append(blob(ellipse_pts(0, 2, 50, 9, 12), "#3a2a10", .3))
    for sx in (-1, 1):
        b.append(shape(rect_pts(sx * 22 - 12, -34, sx * 22 + 12, 0, 6), "#454b5c", "", w=3.6, seed=830 + sx))
        b.append(shape(ellipse_pts(sx * 24 + 4, -2, 17, 8, 10), "#f7f5f0", "", w=3.0, seed=832 + sx))
    body = [(-40, -36), (-42, -96 + sag), (-24, -124 + sag), (24, -124 + sag), (42, -96 + sag), (40, -36)]
    b.append(shape(body, col, blob([(14, -124), (42, -96), (40, -36), (10, -36)], lib.mix(col, "#000000", .25), .6), w=4.4, seed=834))
    for sx in (-1, 1):
        wave = math.sin(t * 7 + ph) * 8 if mood == 1 else 0
        arm = [(sx * 40, -112 + sag), (sx * 56, -80 + sag + wave), (sx * 50, -52 + sag)]
        b.append(line(arm, 16, col, taper=.1, wmin=.9, seed=836 + sx))
        b.append(line(arm, 3, INK, taper=.1, wmin=.9, seed=838 + sx, op=.0))
        b.append(shape(ellipse_pts(arm[-1][0], arm[-1][1] + 4, 9, 9, 8), "#ecc4a2", "", w=2.8, seed=840 + sx))
    hy = -164 + sag
    b.append(shape(ellipse_pts(0, hy, 38, 40, 14), "#ecc4a2", blob([(10, hy - 40), (38, hy), (20, hy + 40), (0, hy + 38)], "#d39f83", .7), w=4.2, seed=842))
    for ex in (-14, 14):
        b.append(f'<circle cx="{ex}" cy="{hy - 2}" r="5.4" fill="{INK}"/>')
    if mood == 0:
        b.append(line([(-12, hy + 14), (0, hy + 24), (12, hy + 14)], 3.6, seed=844))
    elif mood == 1:
        b.append(line([(-12, hy + 20), (-4, hy + 15), (4, hy + 21), (12, hy + 16)], 3.4, seed=845))
        d = (t * 2.2 + ph) % 1.0
        b.append(blob([(34, hy - 20 + d * 30), (40, hy - 6 + d * 30), (34, hy + 2 + d * 30), (28, hy - 6 + d * 30)], "#8fd0f2", 1 - d * .6))
    else:
        b.append(line([(-10, hy + 22), (0, hy + 14), (10, hy + 22)], 3.4, seed=846))
        b.append(line([(-22, hy - 14), (-8, hy - 20)], 3.6, seed=847))
        b.append(line([(22, hy - 14), (8, hy - 20)], 3.6, seed=848))
    # шапка
    b.append(shape([(-34, hy - 36), (0, hy - 50), (34, hy - 36), (0, hy - 22)], "#2b2f3a", blob([(0, hy - 22), (34, hy - 36), (30, hy - 33), (0, hy - 17)], "#171a22", .9), w=3.6, seed=850))
    b.append(shape(rect_pts(-22, hy - 30, 22, hy - 16, 4), "#2b2f3a", "", w=3.0, seed=851))
    b.append(line([(0, hy - 36), (30, hy - 34), (32, hy - 14)], 3.0, "#f7c53a", seed=852))
    return f'<g transform="translate({f(x)} {f(y + jump)}) scale({s * k:.3f})">{"".join(b)}</g>'


def diploma(x, y, t, tp):
    e = t - tp
    k = spring(e, 2.4, 6.0) if e > 0 else 0.0
    if k <= 0.001:
        return ""
    b = []
    b.append(shape(rect_pts(-46, -22, 46, 22, 8), "#fff6dc", blob(rect_pts(-46, 6, 46, 22, 8), "#e8d9b0", .9), w=4, seed=860))
    for sx in (-1, 1):
        b.append(shape(rect_pts(sx * 46 - 7, -26, sx * 46 + 7, 26, 5), "#f0e0b0", "", w=3.6, seed=861 + sx))
    b.append(line([(-28, -6), (26, -6)], 4, "#b9ad88", seed=863))
    b.append(line([(-20, 8), (14, 8)], 4, "#b9ad88", seed=864))
    b.append(shape(ellipse_pts(24, 10, 11, 11, 10), "#ee4b3c", "", w=2.6, seed=865))
    return f'<g transform="translate({f(x)} {f(y - 10 * math.sin(t * 4))}) rotate({-6 * math.sin(t * 3):.2f}) scale({k:.3f})">{"".join(b)}</g>'


def bar(x0, x1, val, col, dk, lt, shk=(0, 0), label="", name="", sd=0):
    h = val * PXD
    if h < 2:
        return ""
    top = BASE - h
    s = []
    s.append(blob(rect_pts(x0 + 12, top + 14, x1 + 12, BASE + 8, 18), "#4a2a10", .22, blur(6)))
    inner = blob(rect_pts(x1 - 54, top - 4, x1 + 4, BASE + 4), dk, .85)
    inner += blob(rect_pts(x0 + 18, top + 12, x0 + 40, BASE - 10, 8), lt, .55)
    s.append(shape(rect_pts(x0, top, x1, BASE, 16), col, inner, w=5.4, seed=870 + sd))
    return "".join(s)


def num(x, y, v, size, col, op=1.0):
    return text(x, y, str(int(round(v))), size, col, op=op)


def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        _ST["card"] = card_static()
        lib.static_done()
    lib.dyn_begin()
    dx, wrot, wu = (0.0, 0.0, 1.0)
    if sid == "s10":
        dx, wrot, wu = whip_in(t, 17.96, 0.2, 700, -6)
    w = [_ST["card"]]
    # ось появляется слева направо
    au = ease_out(clamp((t - 17.9) / 0.5), 3)
    w.append(line([(130, BASE), (130 + 870 * au, BASE)], 6, INK, taper=.05, wmin=.9, seed=880))
    w.append(line([(130, BASE - 600 * au), (130, BASE)], 5, INK, taper=.05, wmin=.9, seed=881))
    # значок и студенты
    w.append(badge(t, 18.04))
    cols = ["#e4673a", "#3aa0a0", "#8a62c8"]
    mood = 0
    if t > 21.84:
        mood = 1
    if t > 23.3:
        mood = 2
    for i, (sx, ph, tp) in enumerate([(430, 0.0, 18.48), (545, 1.7, 18.58), (660, 3.1, 18.68)]):
        w.append(student(sx, 610, 0.95, t, cols[i], mood, ph, t - tp))
    # диплом над группой
    w.append(diploma(830, 560, t, 19.88))
    # столбик 1
    g1 = ease_out(clamp((t - 20.4) / 0.62), 3)
    g1 = g1 + 0.06 * math.sin(clamp((t - 20.4) / 0.62) * math.pi) * (1 if g1 > 0.6 else 0)
    v1 = 34 * clamp(g1, 0, 1.06)
    w.append(bar(B1[0], B1[1], v1, BLUE, BLUE_D, BLUE_L, sd=0))
    xm1 = (B1[0] + B1[1]) / 2
    if v1 > 6:
        top1 = BASE - v1 * PXD
        w.append(num(xm1, top1 + 100, v1, 100, "#ffffff"))
        if v1 > 28:
            w.append(text(xm1, top1 + 150, "дня", 42, "#dcebff"))
    la = smooth(20.8, 21.1, t)
    if la > 0:
        w.append(text(xm1, BASE + 62, "думали", 42, BLUE_D, op=la))
    # столбик 2
    g2 = ease_out(clamp((t - 22.853) / 0.55), 3)
    ov = 0.05 * math.sin(clamp((t - 22.853) / 0.55) * math.pi) if g2 > 0.7 else 0
    v2 = 56 * clamp(g2 + ov, 0, 1.06)
    if 22.2 < t < 22.9:
        # пунктирный контур будущего столбика
        a = smooth(22.2, 22.6, t) * .6
        w.append(f'<rect x="{B2[0]}" y="{BASE - 56 * PXD}" width="{B2[1] - B2[0]}" height="{56 * PXD}" rx="16" fill="none" stroke="{RED}" '
                 f'stroke-width="5" stroke-dasharray="16 14" opacity="{a * (1 - smooth(22.8, 22.9, t)):.2f}"/>')
    if v2 > 0:
        w.append(bar(B2[0], B2[1], v2, RED, RED_D, RED_L, sd=1))
    xm2 = (B2[0] + B2[1]) / 2
    if v2 > 6:
        top2 = BASE - v2 * PXD
        w.append(num(xm2, top2 + 100, v2, 100, "#ffffff"))
        if v2 > 48:
            w.append(text(xm2, top2 + 150, "дня", 42, "#ffe0d6"))
    lb = smooth(23.2, 23.5, t)
    if lb > 0:
        w.append(text(xm2, BASE + 62, "вышло", 42, RED_D, op=lb))
    # разница: пунктир от верха первого, стрелка вверх до верха второго, подпись
    if t > 23.4:
        u = ease_out(clamp((t - 23.4) / 0.4), 3)
        y1, y2 = BASE - 34 * PXD, BASE - 56 * PXD
        w.append(f'<path d="M{B1[1] + 6} {y1}H{760}" stroke="{INK}" stroke-width="4" stroke-dasharray="14 12" fill="none" opacity="{u:.2f}"/>')
        w.append(f'<path d="M{B2[1] + 6} {y2}H{760}" stroke="{INK}" stroke-width="4" stroke-dasharray="14 12" fill="none" opacity="{u:.2f}"/>')
        ya = y1 + (y2 - y1) * u
        w.append(line([(730, y1), (730, ya + 6)], 18, "#e8281a", taper=.0, wmin=1, seed=890))
        if u > 0.3:
            hd = [(730, ya - 14), (702, ya + 30), (758, ya + 30)]
            w.append(shape(hd, "#e8281a", "", w=4.6, seed=891))
    e2 = t - 23.7
    if e2 > 0:
        k = spring(e2, 2.4, 6.0)
        w.append(f'<g transform="translate(880 {BASE - 45 * PXD}) scale({k:.3f})">'
                 + text(0, 0, "+22", 110, "#e8281a", stroke="#ffffff", sw=10)
                 + text(0, 62, "дня", 52, "#e8281a", stroke="#ffffff", sw=8) + '</g>')
    # камера
    if sid == "s10":
        v = clamp((t - 17.96) / 3.04)
        sc_, cx_, cy_ = 1.05 + 0.1 * ease_io(v), 540 + 20 * v, 790
    else:
        v = clamp((t - 21.0) / 3.04)
        sc_, cx_, cy_ = 1.12 + 0.08 * ease_io(v), 560, 800 + 30 * v
        sc_ *= punch(t, 23.36, 0.07, 6.0)
    sx, sy = shake(t, 23.36, 9) if sid == "s11" else (0, 0)
    body = f'<g transform="{cam(cx_ + sx, cy_ + sy, sc_, wrot + 0.5 * math.sin(t))}"><g transform="translate({f(dx)} 0)">{_ST["bg"]}{"".join(w)}</g></g>'
    return svg(body + speed_streaks(wu, 520))
