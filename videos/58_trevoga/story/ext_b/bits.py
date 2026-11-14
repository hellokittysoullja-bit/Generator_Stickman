"""Рилс 58 группа B: общие мелочи сцен (облако одним контуром, молния, капля пота, штрихи-строки, худи)."""
import math

import dima
import lib
from lib import INK, blob, ellipse_pts, f, line, shape

C_CLOUD, C_CLOUD_SH, C_CLOUD_HI = "#6E6A8C", "#56527a", "#8a86a8"
C_BOLT = "#F2C84B"
C_PAPER, C_PAPER_SH = "#FBF8EE", "#e6e0cc"
C_PEN, C_PEN_CAP, C_PEN_CLIP = "#2F5FA8", "#1F3F73", "#9AA0A6"
C_TABLE, C_TABLE_EDGE, C_LEG = "#C99A62", "#A87B47", "#7A8288"
C_TIMER = "#E8892B"
HINK = "#2a2d30"


def cloud_pts(cx, cy, rx, ry, n=7, seed=0, ph=0.0, amp=0.2, flat=0.0, pts=72):
    """Контур облака одной фигурой: валики-«бугры» по кругу, низ чуть площе."""
    out = []
    for k in range(pts):
        a = 2 * math.pi * k / pts
        bump = abs(math.sin(n * a / 2 + ph + seed))
        r = 1 + amp * (bump ** 0.7 - 0.5) * 2 * 0.6
        x = math.cos(a) * rx * r
        y = math.sin(a) * ry * r
        if y > 0:
            y *= (1 - flat)
        out.append((cx + x, cy + y))
    return out


def cloud(cx, cy, rx, ry, k=1.0, seed=0, ph=0.0, n=7, face=False, dark=0.0, w=6, flat=0.35, bolt_glow=0.0):
    """Серо-фиолетовое облако (#6E6A8C) с тенью снизу и бликом сверху; dark 0..1 темнее."""
    pts = cloud_pts(cx, cy, rx * k, ry * k, n=n, seed=seed, ph=ph, flat=flat)
    col = lib.mix(C_CLOUD, "#3b3860", dark * .6)
    sh = lib.mix(C_CLOUD_SH, "#2a284a", dark * .6)
    hi = lib.mix(C_CLOUD_HI, "#5a5680", dark * .5)
    inner = blob([(cx - rx * k * 1.2, cy + ry * k * .15), (cx + rx * k * 1.2, cy + ry * k * .05), (cx + rx * k * 1.2, cy + ry * k * 1.2),
                  (cx - rx * k * 1.2, cy + ry * k * 1.2)], sh, 0.95)
    inner += blob(ellipse_pts(cx - rx * k * .3, cy - ry * k * .5, rx * k * .5, ry * k * .22, 14, rot=-8), hi, .9)
    o = shape(pts, col, inner, w=w, seed=seed + 17)
    if face:
        # хмурое лицо: брови-штрихи и маленький рот
        o += line([(cx - rx * k * .42, cy - ry * k * .1), (cx - rx * k * .12, cy + ry * k * .05)], 9, INK, seed=seed + 3)
        o += line([(cx + rx * k * .42, cy - ry * k * .1), (cx + rx * k * .12, cy + ry * k * .05)], 9, INK, seed=seed + 4)
        o += blob(ellipse_pts(cx - rx * k * .27, cy + ry * k * .17, 11, 12, 10), "#fff", 1) + blob(ellipse_pts(cx - rx * k * .25, cy + ry * k * .19, 5, 6, 8), INK)
        o += blob(ellipse_pts(cx + rx * k * .27, cy + ry * k * .17, 11, 12, 10), "#fff", 1) + blob(ellipse_pts(cx + rx * k * .25, cy + ry * k * .19, 5, 6, 8), INK)
    return o


def bolt_pts(x0, y0, x1, y1, w=70, seed=0):
    """Зигзаг молнии сверху (x0,y0) вниз (x1,y1): единый многоугольник."""
    n = 5
    spine = []
    for i in range(n + 1):
        u = i / n
        sx = x0 + (x1 - x0) * u + (w * .55 if i % 2 else -w * .55) * (1 if 0 < i < n else 0) * (1 - .15 * seed % 1)
        spine.append((sx, y0 + (y1 - y0) * u))
    left = [(p[0] - w * .5 * (1 - i / (n + .8)), p[1]) for i, p in enumerate(spine)]
    right = [(p[0] + w * .5 * (1 - i / (n + .8)), p[1]) for i, p in enumerate(spine)]
    tip = spine[-1]
    poly = [(q[0], q[1], 1) for q in left[:-1]] + [(tip[0], tip[1] + w * .4, 1)] + [(q[0], q[1], 1) for q in right[:-1][::-1]]
    return poly


def bolt(x0, y0, x1, y1, w=70, seed=0, u=1.0):
    """Молния #F2C84B с чёрной обводкой; u 0→1 — вырастает сверху вниз."""
    if u <= 0:
        return ""
    yy = y0 + (y1 - y0) * min(1, u)
    pts = bolt_pts(x0, y0, x0 + (x1 - x0) * min(1, u), yy, w, seed)
    inner = blob([(p[0] + w * .18, p[1]) for p in pts[:len(pts) // 2]] + [(p[0], p[1]) for p in pts[len(pts) // 2:][::-1]], "#d9a62a", .55)
    return shape(pts, C_BOLT, inner, w=6, seed=seed + 5, var=.15)


def sweat(x, y, k=1.0, rot=0.0):
    pts = [(0, -46, 1), (22, -6), (30, 18), (18, 40), (0, 46), (-18, 40), (-30, 18), (-22, -6)]
    pp = lib.T(pts, x, y, k, rot)
    return shape(pp, "#bfe3f6", blob(lib.T([(6, 0), (24, 14), (16, 36), (4, 38)], x, y, k, rot), "#8fc4e2", .9) +
                 blob(lib.T(ellipse_pts(-12, 14, 4, 10, 8), x, y, k, rot), "#ffffff"), w=4, seed=int(x + y) % 997, var=.12)


def scribbles(x0, y0, x1, n, k=1.0, seed=0, gap=34, color=HINK, w=5.0, width_k=0.0):
    """Штрихи-«строки» без букв (неровные, разной длины и наклона): первые floor(n*k) полностью, следующая частично."""
    o = []
    for i in range(n):
        u = lib.clamp(k * n - i)
        if u <= 0:
            continue
        L = (x1 - x0) * (0.55 + 0.45 * abs(math.sin(i * 2.3 + seed)))
        y = y0 + i * gap + 3 * math.sin(i * 1.7 + seed)
        m = int(10 + L / 22)
        pts = []
        for j in range(m + 1):
            uu = j / m
            if uu > u:
                break
            pts.append((x0 + uu * L, y + 6 * math.sin(uu * 11 + i * 1.9 + seed) * (0.5 + 0.5 * math.sin(i)) - uu * 4 + 4 * math.sin(uu * 27 + i)))
        if len(pts) >= 2:
            o.append(line(pts, w, color, taper=.3, wmin=.5, seed=seed + i * 7, peak=.5))
    return "".join(o)


def hood_body(sd=0):
    """Шея и худи под головой (в L-единицах головы) — как в рилсе 57 s12."""
    s = []
    hood = [(-230, 90), (-300, 150), (-340, 260), (-310, 380), (-160, 400), (-60, 250)]
    s.append(shape(hood, dima.HOOD_SH, blob([(-300, 260), (-240, 180), (-170, 220), (-200, 360)], dima.HOOD_SH2, .9), w=5.4, seed=sd + 1))
    neck = [(-70, 60), (82, 66), (96, 220), (84, 280), (-80, 280), (-86, 200)]
    s.append(shape(neck, dima.SKIN, blob([(-86, 60), (-10, 110), (-20, 190), (-86, 200)], dima.SKIN_SH, .9) +
                   blob([(10, 140), (92, 150), (96, 210), (20, 220)], dima.SKIN_SH2, .45), w=5.4, seed=sd + 2))
    body = [(-470, 520), (-430, 300), (-330, 208), (-190, 176), (-92, 168), (-40, 176), (20, 184), (80, 178), (130, 176), (210, 176),
            (360, 212), (460, 300), (500, 520)]
    inner = blob([(250, 176), (460, 300), (500, 520), (200, 520), (300, 300)], dima.HOOD_SH, .8)
    inner += lib.line([(-300, 300), (-200, 330), (-150, 420)], 4, dima.FOLD, seed=sd + 4, op=.8) + lib.line([(260, 290), (320, 340), (330, 440)], 4, dima.FOLD, seed=sd + 5, op=.8)
    s.append(shape(body, dima.HOOD, inner, w=5.6, seed=sd + 3))
    for k, x0 in enumerate((-30, 46)):
        pts = [(x0, 262), (x0 - 6 + 4 * k, 330), (x0 - 2, 400)]
        s.append(lib.line(pts, 7, "#efe8da", taper=.2, wmin=.8, seed=sd + 10 + k) + lib.line(pts, 2.4, INK, taper=.2, wmin=.8, seed=sd + 12 + k, op=.7))
    return "".join(s)


import dima  # noqa
from lib import shape, blob, line, f  # noqa


def hand_flat(x, y, ang=0.0, k=1.0, sd=0, flip=1):
    """Кисть, лежащая на странице: ладонь-тыл и четыре пальца-колбаски (вид сверху-спереди)."""
    o = []
    pts = [(-40, -10), (-20, -34), (30, -36), (62, -18), (66, 16), (40, 36), (-20, 34), (-44, 14)]
    o.append(shape(pts, dima.SKIN, blob([(-44, 14), (-20, 34), (40, 36), (66, 16), (30, 18)], dima.SKIN_SH, .9), w=4.6, seed=sd))
    for j in range(4):
        fy = -26 + j * 17
        fp_ = [(60, fy - 8), (104, fy - 8 + j * 1.5), (112, fy + 1 + j), (100, fy + 8 + j), (60, fy + 8)]
        o.append(shape(fp_, dima.SKIN, blob([(60, fy + 3), (104, fy + 4 + j), (100, fy + 8 + j), (60, fy + 8)], dima.SKIN_SH, .85), w=3.8, seed=sd + 3 + j))
    o.append(line([(-20, -20), (24, -22)], 2.4, dima.SKIN_SH2, seed=sd + 9, op=.7))
    tr = f'translate({f(x)} {f(y)}) rotate({f(ang)}) scale({f(k * flip)} {f(k)})'
    return f'<g transform="{tr}">{"".join(o)}</g>'


def forearm(a, b, w0=92, w1=70, sd=0):
    pts = lib.band([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 20), b], w0, w1, step=6, cap=True)
    return shape(pts, dima.HOOD, blob(lib.band([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 40), b], 40, 30, step=6, cap=True), dima.HOOD_SH, .8) +
                 line([(a[0] + 30, a[1] + 30), ((a[0] + b[0]) / 2 + 10, (a[1] + b[1]) / 2 + 40)], 3.4, dima.FOLD, seed=sd + 1, op=.7), w=5.2, seed=sd)
