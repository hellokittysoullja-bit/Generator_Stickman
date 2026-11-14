"""Рилс 59 группа C: s08 (13.5–16.5) корзина крупно на фоне вечернего окна; на «лежали» (14.76) в неё по одной падают шесть вещей
(лампа, чайник, книга, кроссовок, шарф, мишка — props.item из common/props.py), на «шесть» (15.24) шестая падает и корзина оседает;
Дима в углу тянется пальцами; камера сверху вниз с наездом, на каждом падении толчок."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props  # noqa: E402
from lib import INK, W, H, back_out, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, lin_grad, line, rect_pts, shape, svg  # noqa: E402

T0 = 13.3
BX, BY, BK = 540, 1090, 3.6                 # центр дна корзины и масштаб (172 px при k=1 → 620)
RIM = BY - 100 * BK                         # y обода
# вещь, x, низ (от обода вниз), поворот покоя, момент приземления; падение 0.36 с
ORDER = [("lamp", 410, 30, -8, 14.20), ("kettle", 660, 30, 5, 14.50), ("book", 440, 34, -12, 14.76),
         ("sneaker", 690, -12, 7, 14.98), ("scarf", 400, -2, -4, 15.12), ("teddy", 545, 4, 3, 15.24)]
FALL = 0.36
LAND = [o[4] for o in ORDER]
IK = 3.6


def lerp(a, b, u):
    return a + (b - a) * u


def rnd(i):
    return abs(math.sin(i * 12.9898) * 43758.5453) % 1.0


def window(t):
    o = []
    x0, y0, x1, y1 = 170, 30, 910, 640
    g = lin_grad([(0, "#3E3D82", 1), (.45, "#B5568F", 1), (.8, "#FF8E5E", 1), (1, "#FFC873", 1)], 0, 0, 0, 1, gid="sky")
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>')
    # звёзды
    for i in range(14):
        x = x0 + 30 + rnd(i) * (x1 - x0 - 60)
        y = y0 + 20 + rnd(i + 20) * 230
        r = 3 + 3 * rnd(i + 4) * (0.6 + 0.4 * math.sin(t * 3 + i))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#FFF3D6"/>')
    # солнце
    o.append(f'<circle cx="640" cy="{500:.0f}" r="92" fill="#FFE6A0"/><circle cx="640" cy="500" r="64" fill="#FFF4CC"/>')
    # облака плывут
    for i, (cy, sp, sz) in enumerate(((190, 22, 1.0), (330, 14, 1.4), (420, 30, .8))):
        cx = x0 - 200 + ((t * sp + i * 330) % (x1 - x0 + 400))
        col = ("#E9A0B8", "#F7B08A", "#FFC9A0")[i]
        o.append(blob(ellipse_pts(cx, cy, 120 * sz, 26 * sz, 18), col) + blob(ellipse_pts(cx - 50 * sz, cy - 22 * sz, 62 * sz, 24 * sz, 14), col) + blob(ellipse_pts(cx + 40 * sz, cy - 16 * sz, 70 * sz, 22 * sz, 14), col))
    # крыши города
    bl = [(x0, 640), (x0, 540), (230, 540), (230, 500), (300, 500), (300, 560), (360, 560), (360, 470), (440, 470), (440, 580), (520, 580), (520, 520), (580, 520), (580, 600), (700, 600), (700, 510), (790, 510), (790, 560), (860, 560), (860, 590), (x1, 590), (x1, 640)]
    o.append(blob(bl, "#3A2F55"))
    for (wx, wy) in ((250, 520), (390, 500), (410, 540), (730, 530), (770, 540), (550, 548)):
        o.append(f'<rect x="{wx}" y="{wy}" width="14" height="18" fill="#FFD36B"/>')
    # рама
    fr = "#F4ECDD"
    o.append(shape(rect_pts(x0 - 22, y0 - 22, x1 + 22, y0 + 6), fr, "", w=6, seed=11))
    o.append(shape(rect_pts(x0 - 22, y1 - 6, x1 + 22, y1 + 30), fr, blob(rect_pts(x0 - 22, y1 + 14, x1 + 22, y1 + 30), "#D9CFBB"), w=6, seed=12))
    o.append(shape(rect_pts(x0 - 22, y0 - 22, x0 + 8, y1 + 30), fr, "", w=6, seed=13))
    o.append(shape(rect_pts(x1 - 8, y0 - 22, x1 + 22, y1 + 30), fr, "", w=6, seed=14))
    o.append(shape(rect_pts(525, y0, 555, y1), fr, "", w=6, seed=15))
    o.append(shape(rect_pts(x0, 300, x1, 328), fr, "", w=6, seed=16))
    # шторы
    for sx, xa in ((-1, 70), (1, 1010)):
        pts = [(xa - sx * 120, -80), (xa + sx * 40, -80), (xa + sx * 40, 700), (xa + sx * 10, 740), (xa - sx * 40, 690), (xa - sx * 80, 730), (xa - sx * 120, 660)]
        o.append(shape(pts, "#7C2F4E", "".join(line([(xa - sx * (100 - 38 * j), -60), (xa - sx * (96 - 38 * j), 700)], 7, "#5F2039", taper=.1, wmin=.8, seed=20 + j) for j in range(3)), w=6, seed=17))
    return "".join(o)


def room(t):
    s = [f'<rect x="-700" y="-900" width="2500" height="2400" fill="#7B6286"/>']
    for k in range(-8, 20):  # обои: широкие полосы
        s.append(f'<rect x="{k * 120}" y="-900" width="60" height="2000" fill="#725A7C"/>')
    s.append(window(t))
    # пол и плинтус
    s.append(f'<rect x="-700" y="1010" width="2500" height="1500" fill="#8E5B3C"/>')
    s.append(shape(rect_pts(-700, 990, 1800, 1030), "#F1E6D2", blob(rect_pts(-700, 1014, 1800, 1030), "#D3C5AC"), w=6, seed=31))
    for k in range(-8, 14):
        s.append(line([(k * 180 - 40, 1030), (k * 180 - 140, 1900)], 4, "#5E3A25", taper=.1, wmin=.9, seed=40 + k))
    s.append(line([(-700, 1250), (1800, 1250)], 4, "#5E3A25", taper=.1, wmin=.9, seed=60))
    # пятно закатного света на полу (сплошная трапеция)
    return "".join(s)


def drop_state(i, t):
    """Положение вещи i в момент t: None — ещё не видна; (x, y, rot, sx, sy)."""
    name, rx, dyb, rrot, tl = ORDER[i]
    ts = tl - FALL
    ry = RIM + dyb
    if t < ts:
        return None
    if t < tl:
        u = (t - ts) / FALL
        e = ease_in(u, 2.0)
        x0 = rx + (-180 if i % 2 == 0 else 190)
        y0 = -520
        x = lerp(x0, rx, ease_out(u, 1.5))
        y = lerp(y0, ry, e)
        rot = lerp(-70 if i % 2 == 0 else 80, rrot, ease_out(u, 1.4)) + 6 * math.sin(u * 14)
        return x, y, rot, 1 + .06 * (1 - u), 1 - .06 * (1 - u)
    e = t - tl
    sq = math.exp(-e * 10) * math.cos(e * 40)
    return rx, ry - 14 * math.exp(-e * 9) * abs(math.sin(e * 26)) * (1.4 if i == 5 else 1), rrot, 1 + .12 * sq * (1.4 if i == 5 else 1), 1 - .14 * sq * (1.4 if i == 5 else 1)


def bump(t):
    """Толчок корзины: сумма затухающих ударов по приземлениям; шестой сильнее."""
    s = 0.0
    for i, tl in enumerate(LAND):
        e = t - tl
        if e > 0:
            s += (1.5 if i == 5 else .55) * math.exp(-e * 8) * math.cos(e * 30)
    return s


def sag(t):
    e = t - LAND[5]
    if e < 0:
        return 0.15 * sum(1 for tl in LAND[:5] if t > tl) / 5
    return lerp(.15, 1.0, ease_out(e / .35, 2))


def dima_hand(t):
    """Рука Димы в правом верхнем углу тянется к корзине: рукав горчичного худи, кисть открыта, пальцы шевелятся."""
    people.C = people.PAL["dima"]
    p = ease_io(clamp((t - T0) / 1.0))
    jerk = sum(math.exp(-(t - tl) * 9) * math.sin((t - tl) * 36) * (14 if i < 5 else 28) for i, tl in enumerate(LAND) if t > tl)
    wr = (lerp(1230, 985, p) + 8 * math.sin(t * 6) + jerk * .4, lerp(300, 340, p) - 6 * math.cos(t * 5) + jerk)
    el = (1300, 20)
    d = (-0.62, 0.78)
    nrm = math.hypot(*d)
    d = (d[0] / nrm, d[1] / nrm)
    wob = 0.5 + 0.5 * math.sin(t * 9)
    cur = (0.1 + .35 * wob, .2 + .3 * (1 - wob), .15 + .35 * wob, .3 + .3 * (1 - wob))
    o = []
    import numpy as np
    S, E, Wr = np.array((1500, -260.0)), np.array(el, float), np.array(wr, float)
    o.append(people.sleeve(S, E, Wr, False, 80, "dima"))
    o.append(people.hand_svg("dima", wr, d, k=1.55, flip=-1, curl=cur, spread=.3, thumb=.1, bend=.12, seed=720))
    return "".join(o)


def s08_frame(t):
    s = [room(t)]
    bs = bump(t)
    sg = sag(t)
    # тень под корзиной
    s.append("".join(blob(ellipse_pts(BX + 20, BY + 6, 360 * m, 44 * m, 22), "#4A2A18", .3 / 3) for m in (1.0, .86, .72)))
    inside = []
    for i in range(6):
        st = drop_state(i, t)
        if st is None:
            continue
        x, y, rot, sx, sy = st
        g = props.item(ORDER[i][0], 0, 0, IK, 0)
        inside.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({sx:.4f} {sy:.4f})">{g}</g>')
    body = props.basket_back(BX, BY, BK, sag=sg) + "".join(inside) + props.basket_front(BX, BY, BK, sag=sg)
    kx = 1 + .03 * bs * .5
    ky = 1 - .04 * bs * .5 - .05 * sg
    s.append(f'<g transform="translate({BX} {BY}) scale({kx:.4f} {ky:.4f}) translate({-BX} {-BY})">{body}</g>')
    # пыль и блики на приземлениях
    for i, tl in enumerate(LAND):
        e = t - tl
        if 0 < e < 0.45:
            u = e / .45
            for j in range(7):
                a = math.radians(180 + 180 * (j + .5) / 7)
                r = 40 + 190 * ease_out(u, 2) * (.7 + .3 * rnd(j + i))
                px, py = ORDER[i][1] + math.cos(a) * r * 1.2, RIM + 10 + math.sin(a) * r * .35
                rr = (14 + 12 * rnd(j * 3 + i)) * (1 - u) * (1.4 if i == 5 else 1)
                s.append(blob(ellipse_pts(px, py, rr, rr * .8, 9), "#FFF3E0"))
            if i == 5 and u < 0.8:
                s.append(props.spark(ORDER[i][1] + 190, RIM - 250, 3.2, u / .8))
                s.append(props.spark(ORDER[i][1] - 200, RIM - 120, 2.6, clamp((u - .1) / .7)))
    s.append(dima_hand(t))
    # камера: сверху вниз и наезд к корзине; толчок на падениях
    u = ease_io(clamp((t - T0) / 2.9))
    sc = lerp(1.0, 1.34, u)
    cx, cy = lerp(540, 540, u), lerp(620, 900, u)
    rot = lerp(-1.6, 1.0, u)
    for i, tl in enumerate(LAND):
        e = t - tl
        if e > 0:
            a = (.05 if i == 5 else .018) * math.exp(-e * 9)
            sc *= 1 + a
            cy += (30 if i == 5 else 10) * math.exp(-e * 9) * math.sin(e * 40)
            rot += (1.3 if i == 5 else .4) * math.exp(-e * 9) * math.sin(e * 33)
    return svg(f'<rect width="{W}" height="{H}" fill="#7B6286"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')


def frame(sid, t):
    lib.dyn_begin()
    return s08_frame(t)
