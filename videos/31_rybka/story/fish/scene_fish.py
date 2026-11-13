"""Сцена fish рилса 31: круглый аквариум-шар с золотой рыбкой на деревянной тумбочке в уютной комнате (мягкий
тёплый свет лампы), на стене — картина и отрывной календарь.
s01 — хук: влёт камеры с кадра 0, рыбка уже плывёт по кругу, над водой пузырь-таймер «3».
s02 — таймер 3→2→1, лопается на «секунды» (2.4), рыбка замирает с пустыми глазами, «?», разворачивается.
s07 — «на самом деле»: рыбка хитрая, подмигивает на «деле» (9.72), искорки, кивает на «помнят» (10.84).
s08 — отъезд: календарь, листы месяцев слетают на «месяцами» (11.2–12.16), рыбка спокойно плавает и смотрит.
s11 — рыбка гордо с медалькой-ракушкой, большая зелёная галочка на «помнит» (17.32), пузыри."""
import math

import numpy as np

import fish
import lib
from lib import (DEFS, INK, W, H, blob, blur, cam, clamp, clip_of, ease_in, ease_io, ease_out, back_out, ellipse_pts, f, fill_d,
                 line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg, spring)

_ST = {}
BX, BY, R = 540, 880, 280
Y_OPEN = BY - 0.78 * R          # горло шара
Y_W = BY - 0.48 * R             # уровень воды
Y_BOT = BY + 0.93 * R           # дно шара (стоит на тумбочке)
TOP_Y = 1112                    # задний край столешницы тумбочки
EDGE_Y = 1152                   # передний край
TX, TY, TR = 560, 520, 92       # пузырь-таймер
CAL = (830, 230, 1100, 600)     # календарь на стене
MONTHS = ["ЯНВАРЬ", "ФЕВРАЛЬ", "МАРТ", "АПРЕЛЬ", "МАЙ", "ИЮНЬ", "ИЮЛЬ"]
FLY = [11.2, 11.44, 11.68, 11.92, 12.16]


def _arc_pts(a0, a1, step=8, r=R, cx=BX, cy=BY):
    n = max(2, int(abs(a1 - a0) / step))
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n + 1)]


A_OPEN = math.degrees(math.asin(-0.78))       # -51.3
A_BOT = math.degrees(math.asin(0.93))         # 68.4
A_W = math.degrees(math.asin(-0.48))          # -28.7


def bowl_pts():
    p = _arc_pts(A_OPEN, A_BOT)
    p[0] = p[0] + (1,)
    p[-1] = p[-1] + (1,)
    q = _arc_pts(180 - A_BOT, 180 - A_OPEN)
    q[0] = q[0] + (1,)
    q[-1] = q[-1] + (1,)
    return p + q


def water_pts():
    p = _arc_pts(A_W, A_BOT)
    p[0] = p[0] + (1,)
    p[-1] = p[-1] + (1,)
    q = _arc_pts(180 - A_BOT, 180 - A_W)
    q[0] = q[0] + (1,)
    q[-1] = q[-1] + (1,)
    return p + q


W_RX = R * math.cos(math.radians(A_W))
OP_RX = R * math.cos(math.radians(A_OPEN))


# ─────────────────────────────── комната
def room():
    s = []
    wall = "#ecd6ae"
    DEFS.append('<pattern id="pWallF" width="96" height="96" patternUnits="userSpaceOnUse">'
                '<rect width="96" height="96" fill="#ecd6ae"/><rect x="0" width="30" height="96" fill="#e6cda1"/>'
                '<circle cx="63" cy="22" r="5" fill="#dcbf8f"/><circle cx="63" cy="70" r="5" fill="#dcbf8f"/></pattern>')
    s.append(f'<rect x="-900" y="-1200" width="3000" height="{TOP_Y + 1200}" fill="url(#pWallF)"/>')
    # картина с морем и парусником
    x0, y0, x1, y1 = 110, 290, 350, 520
    inner = f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#9fd0e4"/>'
    inner += blob([(x0, 440), (180, 425), (260, 445), (x1, 430), (x1, y1), (x0, y1)], "#4f93b8")
    inner += blob([(x0, 470), (200, 460), (300, 478), (x1, 468), (x1, y1), (x0, y1)], "#3d7aa0")
    inner += blob(ellipse_pts(300, 340, 26, 26, 14), "#ffe08a")
    inner += shape([(200, 435, 1), (250, 435, 1), (240, 452, 1), (210, 452, 1)], "#b5683a", "", w=3, seed=21)
    inner += shape([(226, 432, 1), (226, 360, 1), (262, 428, 1)], "#fbf6ea", "", w=3, seed=22)
    s.append(shape(rect_pts(x0, y0, x1, y1), "#9fd0e4", inner, w=4, seed=20))
    s.append(shape(rect_pts(x0 - 18, y0 - 18, x1 + 18, y1 + 18), "none", "", w=4.4, seed=23))
    fr = [(x0 - 18, y0 - 18, 1), (x1 + 18, y0 - 18, 1), (x1 + 18, y1 + 18, 1), (x0 - 18, y1 + 18, 1), (x0 - 18, y0 - 18, 1),
          (x0, y0, 1), (x0, y1, 1), (x1, y1, 1), (x1, y0, 1), (x0, y0, 1)]
    s.append(f'<path d="M{x0 - 18} {y0 - 18}H{x1 + 18}V{y1 + 18}H{x0 - 18}Z M{x0} {y0}V{y1}H{x1}V{y0}Z" fill="#b07a48" fill-rule="evenodd"/>')
    s.append(shape(rect_pts(x0 - 18, y0 - 18, x1 + 18, y1 + 18), "none", "", w=4.4, seed=24))
    s.append(shape(rect_pts(x0, y0, x1, y1), "none", "", w=3.4, seed=25))
    del fr
    # гвоздик календаря
    s.append(line([(965, 205), (965, 226)], 4, INK, seed=26))
    s.append(shape(ellipse_pts(965, 204, 7, 7, 8), "#8e95a5", "", w=2.6, seed=27))
    # тумбочка: столешница (видна сверху), кромка, корпус с ящиком
    wood, wood_sh, wood_top = "#b97f4c", "#94603a", "#d39b62"
    s.append(blob(rect_pts(-200, TOP_Y - 30, 1300, TOP_Y + 6), "#5a3a1c", .25, blur(14)))
    top = [(-460, TOP_Y, 1), (1540, TOP_Y, 1), (1570, EDGE_Y, 1), (-490, EDGE_Y, 1)]
    inner = "".join(line([(-490, TOP_Y + 10 + k * 11), (1570, TOP_Y + 12 + k * 11)], 2.2, "#bf8650", taper=.1, wmin=.7, seed=30 + k)
                    for k in range(3))
    s.append(shape(top, wood_top, inner, w=4.6, seed=31))
    s.append(shape(rect_pts(-490, EDGE_Y, 1570, EDGE_Y + 34, 4), wood, blob(rect_pts(-490, EDGE_Y + 22, 1570, EDGE_Y + 34), wood_sh), w=4.6,
                   seed=32))
    inner = blob(rect_pts(1400, EDGE_Y + 34, 1550, 2400), wood_sh, .9)
    inner += "".join(line([(x, EDGE_Y + 60), (x + 6, 2300)], 2.4, "#a06c3f", taper=.1, wmin=.7, seed=40 + k, op=.8)
                     for k, x in enumerate((-300, 60, 260, 610, 880, 1250)))
    s.append(shape(rect_pts(-460, EDGE_Y + 34, 1540, 2400), wood, inner, w=5, seed=33))
    s.append(shape(rect_pts(20, EDGE_Y + 80, 1060, EDGE_Y + 330, 10), "#c48a55",
                   blob(rect_pts(20, EDGE_Y + 290, 1060, EDGE_Y + 330), wood_sh, .8), w=4.6, seed=34))
    s.append(shape(rect_pts(470, EDGE_Y + 180, 610, EDGE_Y + 214, 16), "#e2c08a", blob(rect_pts(470, EDGE_Y + 200, 610, EDGE_Y + 214), "#b8925a"),
                   w=4, seed=35))
    # горшок с растением слева
    s.append(blob(ellipse_pts(160, TOP_Y + 22, 90, 14, 14), "#4a2c12", .3, blur(5)))
    for k, (a, L) in enumerate([(-120, 210), (-95, 250), (-70, 220), (-140, 170), (-50, 170)]):
        ar = math.radians(a)
        p0 = (160, TOP_Y - 70)
        p2 = (160 + L * math.cos(ar), TOP_Y - 70 + L * math.sin(ar))
        p1 = ((p0[0] + p2[0]) / 2 + 30 * math.cos(ar + 1.2), (p0[1] + p2[1]) / 2 + 30 * math.sin(ar + 1.2))
        s.append(shape(lib.band([p0, p1, p2], 16, 4, cap=True), "#5f9c58", line([p0, p1], 2.4, "#3f7a40", seed=60 + k), w=3.6, seed=61 + k))
    pot = [(98, TOP_Y - 84, 1), (222, TOP_Y - 84, 1), (206, TOP_Y + 20, 1), (114, TOP_Y + 20, 1)]
    s.append(shape(pot, "#d0704a", blob([(170, TOP_Y - 84), (222, TOP_Y - 84), (206, TOP_Y + 20), (170, TOP_Y + 20)], "#a9523a"), w=4.4,
                   seed=70))
    s.append(shape(rect_pts(90, TOP_Y - 98, 230, TOP_Y - 74, 6), "#e08458", "", w=4, seed=71))
    # лампа справа
    lx = 950
    s.append(blob(ellipse_pts(lx, TOP_Y + 26, 80, 12, 14), "#4a2c12", .3, blur(5)))
    s.append(shape(ellipse_pts(lx, TOP_Y + 14, 62, 16, 16), "#7b8494", blob(ellipse_pts(lx + 10, TOP_Y + 20, 52, 10, 12), "#5c6473"), w=4,
                   seed=80))
    s.append(shape(rect_pts(lx - 9, 960, lx + 9, TOP_Y + 8, 4), "#8e95a5", "", w=3.6, seed=81))
    shade = [(lx - 66, 816, 1), (lx + 66, 816, 1), (lx + 110, 968, 1), (lx - 110, 968, 1)]
    g = lin_grad([(0, "#fff3d6", 1), (1, "#f6d9a0", 1)], 0, 0, 0, 1)
    s.append(shape(shade, f"url(#{g})", blob([(lx + 20, 816), (lx + 66, 816), (lx + 110, 968), (lx + 40, 968)], "#ecc884", .9), w=4.6, seed=82))
    return "".join(s)


def light():
    g = rad_grad([(0, "#ffd890", .55), (.5, "#ffc070", .16), (1, "#ffc070", 0)], 940, 900, 1100, 1000)
    s = [f'<rect x="-900" y="-1200" width="3000" height="3800" fill="url(#{g})" style="mix-blend-mode:screen"/>']
    g2 = rad_grad([(0, "#000000", 0), (.62, "#000000", 0), (1, "#2a1606", .38)], 600, 820, 1200, 1500)
    s.append(f'<rect x="-900" y="-1200" width="3000" height="3800" fill="url(#{g2})"/>')
    return "".join(s)


# ─────────────────────────────── аквариум
def bowl_back():
    """Стекло над водой, задний край горла, вода, галька, камень, ракушка (статично)."""
    s = []
    bp = bowl_pts()
    s.append(blob(ellipse_pts(BX + 20, Y_BOT + 6, 150, 18, 16), "#3a2410", .4, blur(7)))
    _ST["clip_bowl"] = clip_of(bp)
    # стекло: чуть светлее стены, голубоватое
    g = lin_grad([(0, "#f4f1e6", 1), (1, "#e3ecdf", 1)], 0, 0, 0, 1)
    s.append(blob(bp, f"url(#{g})"))
    # задняя половина горла
    s.append(line(_arc_pts(180, 360, 10, OP_RX + 6, BX, Y_OPEN) if False else
                  [(BX - OP_RX - 4, Y_OPEN), (BX - OP_RX * .6, Y_OPEN - 18), (BX, Y_OPEN - 24), (BX + OP_RX * .6, Y_OPEN - 18),
                   (BX + OP_RX + 4, Y_OPEN)], 5, "#8fb6bf", taper=.1, wmin=.8, seed=100))
    # вода
    wp = water_pts()
    _ST["clip_water"] = clip_of(wp)
    g = lin_grad([(0, "#a7dfe8", 1), (0.55, "#7cc4d6", 1), (1, "#4f9ebd", 1)], 0, 0, 0, 1)
    inner = []
    # лучи света в воде
    for k, (x, a) in enumerate([(380, .35), (520, .28), (660, .3)]):
        inner.append(blob([(x - 30, Y_W), (x + 30, Y_W), (x + 90, Y_BOT), (x + 10, Y_BOT)], "#c6eef3", a))
    # дальняя галька и камень
    rs = np.random.RandomState(5)
    cols = ["#e8b07a", "#c97b5a", "#8fb8a0", "#f0d9a8", "#a99bc4", "#d98e6a", "#f3c98b"]
    gr = []
    for row, (y, n) in enumerate([(1066, 18), (1088, 22), (1110, 24), (1132, 26)]):
        for i in range(n):
            x = BX - 260 + 520 * (i + rs.uniform(0.1, 0.9)) / n
            rx, ry = rs.uniform(13, 21), rs.uniform(8, 12)
            c = cols[rs.randint(len(cols))]
            gr.append(shape(ellipse_pts(x, y + rs.uniform(-4, 4), rx, ry, 10, rot=rs.uniform(-20, 20)), c,
                            blob(ellipse_pts(x + rx * .25, y + ry * .45, rx * .8, ry * .45, 8), mix(c, "#5a3a2a", .25)), w=2.6,
                            seed=200 + row * 40 + i))
    inner.append(blob([(BX - 300, 1074), (BX - 150, 1056), (BX, 1050), (BX + 150, 1056), (BX + 300, 1074), (BX + 300, 1200), (BX - 300, 1200)],
                      "#c99a6c"))
    inner += gr
    # камень-арка
    rock = [(456, 1080), (462, 1024), (492, 996), (532, 990), (566, 1006), (580, 1046), (584, 1084)]
    inner.append(shape(rock, "#9aa3ad", blob([(530, 990), (566, 1006), (580, 1046), (584, 1084), (540, 1084)], "#7b8490") +
                       blob(ellipse_pts(500, 1012, 16, 8, 8, rot=-30), "#c2c9d0"), w=4.2, seed=120))
    # ракушка
    sx, sy = 630, 1090
    sh = [(sx - 30, sy + 6), (sx - 26, sy - 14), (sx - 12, sy - 26), (sx, sy - 30), (sx + 12, sy - 26), (sx + 26, sy - 14), (sx + 30, sy + 6),
          (sx + 10, sy + 12, 1), (sx - 10, sy + 12, 1)]
    rib = "".join(line([(sx, sy + 10), (sx + 22 * a, sy - 22)], 2.4, "#c98a6a", seed=130 + k, taper=.2, wmin=.6)
                  for k, a in enumerate((-0.9, -0.45, 0, 0.45, 0.9)))
    inner.append(shape(sh, "#ffe0c8", rib, w=3.6, seed=131))
    s.append(f'<g clip-path="url(#{_ST["clip_bowl"]})">' + shape(wp, f"url(#{g})", "".join(inner), w=0.1, ink=False) + "</g>")
    return "".join(s)


def surface(t):
    """Поверхность воды — светлый эллипс с мелкой рябью."""
    s = []
    sp = ellipse_pts(BX, Y_W, W_RX - 2, 20, 28)
    rip = "".join(line([(BX - 160 + k * 110 + 14 * math.sin(t * 2 + k), Y_W + 4 + 5 * math.sin(t * 3 + k * 2)),
                        (BX - 110 + k * 110 + 14 * math.sin(t * 2 + k), Y_W + 6 + 5 * math.sin(t * 3 + k * 2))], 3, "#e9fbfd",
                       taper=.6, wmin=.3, seed=140 + k) for k in range(4))
    s.append(f'<g clip-path="url(#{_ST["clip_bowl"]})">' + shape(sp, "#c4ecf2", rip, w=3.2, seed=141, ink_color="#3d7f93") + "</g>")
    return "".join(s)


def bowl_front():
    """Контур стекла, передний край горла, блики (статично)."""
    s = []
    bp = bowl_pts()
    # толщина стекла: светлая кайма по внутреннему краю
    s.append(f'<g clip-path="url(#{_ST["clip_bowl"]})">' +
             f'<path d="{lib.ink_closed(bp, 16, var=.1, weight=.2, seed=150)}" fill="#e9f7f9"/></g>')
    s.append(f'<path d="{lib.ink_closed(bp, 6.0, seed=151)}" fill="{INK}"/>')
    # горло: кольцо стекла
    rim = ellipse_pts(BX, Y_OPEN, OP_RX + 10, 24, 24)
    s.append(f'<path d="M{BX - OP_RX - 10} {Y_OPEN} A{OP_RX + 10} 24 0 0 0 {BX + OP_RX + 10} {Y_OPEN} '
             f'L{BX + OP_RX - 4} {Y_OPEN} A{OP_RX - 4} 14 0 0 1 {BX - OP_RX + 4} {Y_OPEN}Z" fill="#dff2f4"/>')
    s.append(f'<path d="{lib.ink_closed(rim, 4.6, seed=152)}" fill="{INK}"/>')
    s.append(line([(BX - OP_RX + 6, Y_OPEN + 2), (BX - OP_RX * .5, Y_OPEN + 13), (BX, Y_OPEN + 15), (BX + OP_RX * .5, Y_OPEN + 13),
                   (BX + OP_RX - 6, Y_OPEN + 2)], 3, "#7fa7b2", taper=.3, wmin=.5, seed=153))
    # донышко-подставка
    s.append(line([(BX - R * .37 + 6, Y_BOT - 8), (BX, Y_BOT - 2), (BX + R * .37 - 6, Y_BOT - 8)], 3.4, "#7fa7b2", seed=154))
    # блики
    s.append(line(_arc_pts(196, 238, 4, R * .84), 18, "#ffffff", taper=.8, wmin=.15, seed=155, op=.92))
    s.append(line(_arc_pts(160, 182, 4, R * .86), 9, "#ffffff", taper=.8, wmin=.2, seed=156, op=.85))
    s.append(f'<circle cx="{f(BX - R * .45)}" cy="{f(BY - R * .62)}" r="9" fill="#ffffff"/>')
    s.append(line(_arc_pts(-20, 30, 4, R * .9), 7, "#ffffff", taper=.8, wmin=.2, seed=157, op=.7))
    return "".join(s)


def weed(t, base, h, n, seed, lean=0.0, k_amp=1.0):
    s = []
    for j in range(n):
        bx = base[0] + (j - (n - 1) / 2) * 22
        hh = h * (1 - 0.18 * abs(j - (n - 1) / 2))
        pts = []
        for i in range(7):
            u = i / 6
            sw = (18 * math.sin(t * 1.9 + j * 1.3 + u * 2.4) + lean * 40 * u) * u ** 1.3 * k_amp
            pts.append((bx + sw + 14 * (j - (n - 1) / 2) * u, base[1] - hh * u))
        c = "#5aa05a" if j % 2 == 0 else "#4b8f4e"
        s.append(shape(lib.band(pts, 26, 6), c, line(pts[:6], 2.6, "#3a7440", seed=seed + 10 + j), w=3.6, seed=seed + j))
    return "".join(s)


def bubbles(t, x0, y0, n=6, period=0.42, speed=170, seed=0, top=None, r0=7):
    top = Y_W + 14 if top is None else top
    s = []
    rs = np.random.RandomState(seed)
    off = rs.uniform(0, period, 1)[0]
    for i in range(-int((y0 - top) / speed / period) - 2, 1):
        k0 = math.floor((t - off) / period) + i
        tb = off + k0 * period
        e = t - tb
        if e < 0:
            continue
        rr = np.random.RandomState(abs(int(k0)) % 10000 + seed)
        y = y0 - speed * e
        if y < top:
            continue
        x = x0 + 10 * math.sin(e * 6 + rr.uniform(0, 6)) + rr.uniform(-10, 10)
        r = r0 * rr.uniform(0.6, 1.3) * min(1, e * 6)
        if r < 1.5:
            continue
        s.append(fish.bubble(x, y, r, lw=2.6, seed=400 + int(k0) % 50))
    return "".join(s)


# ─────────────────────────────── таймер, календарь, «?», галочка
def timer(t, digit, prog, sc=1.0, bob=0.0):
    """Пузырь-таймер: круглый «секундомер» в пузыре; prog — доля оставшегося времени (кольцо)."""
    x, y, r = TX, TY + bob, TR * sc
    s = [f'<g transform="translate({f(x)} {f(y)}) rotate({f(4 * math.sin(t * 2.3))})">']
    s.append(shape(rect_pts(-16, -r - 30, 16, -r - 6, 5), "#e85a3c", "", w=3.6, seed=500))
    s.append(shape(rect_pts(-28, -r - 44, 28, -r - 26, 7), "#f07a52", "", w=3.6, seed=501))
    s.append(shape(ellipse_pts(0, 0, r, r, 24), "#e3f6fa", blob(ellipse_pts(r * .18, r * .25, r * .85, r * .7, 18), "#c8ebf3"), w=5,
                   seed=502))
    # кольцо оставшегося времени
    rr = r * 0.8
    if prog > 0.003:
        a1 = -90 + 360 * prog
        la = 1 if prog > 0.5 else 0
        x1, y1 = rr * math.cos(math.radians(a1)), rr * math.sin(math.radians(a1))
        if prog > 0.997:
            s.append(f'<circle r="{f(rr)}" fill="none" stroke="#f0763e" stroke-width="{f(r * .13)}"/>')
        else:
            s.append(f'<path d="M0 {f(-rr)} A{f(rr)} {f(rr)} 0 {la} 1 {f(x1)} {f(y1)}" fill="none" stroke="#f0763e" '
                     f'stroke-width="{f(r * .13)}" stroke-linecap="round"/>')
    fs = r * 1.22
    s.append(f'<text x="0" y="{f(fs * .36)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="{f(fs)}" '
             f'fill="#1f2a44">{digit}</text>')
    s.append(f'<circle cx="{f(-r * .48)}" cy="{f(-r * .5)}" r="{f(r * .16)}" fill="#ffffff"/>')
    s.append(line([(-r * .78, -r * .1), (-r * .7, -r * .42), (-r * .45, -r * .7)], 6, "#ffffff", taper=.6, wmin=.2, seed=503))
    s.append("</g>")
    return "".join(s)


def pop(t, t0):
    """Пузырь лопнул: штрихи-лучи и капли разлетаются (0.3 с)."""
    e = t - t0
    if e < 0 or e > 0.34:
        return ""
    u = e / 0.34
    s = []
    for k in range(10):
        a = math.radians(k * 36 + 10)
        r0 = TR * (0.7 + 0.9 * ease_out(u))
        r1 = r0 + 70 * (1 - u)
        s.append(line([(TX + r0 * math.cos(a), TY + r0 * math.sin(a)), (TX + r1 * math.cos(a), TY + r1 * math.sin(a))], 12 * (1 - u) + 2,
                      INK, taper=.5, seed=510 + k))
    for k in range(8):
        a = math.radians(k * 45 + 25)
        d = TR * (0.6 + 1.6 * ease_out(u))
        rr = 13 * (1 - u) + 2
        s.append(shape(ellipse_pts(TX + d * math.cos(a), TY + d * math.sin(a) + 120 * u * u, rr, rr, 8), "#c8ebf3", "", w=3, seed=520 + k))
    return "".join(s)


def question(t, t0, x, y, size=240):
    e = t - t0
    if e < 0:
        return ""
    sc = back_out(clamp(e / 0.22), 2.2)
    rot = 7 * math.sin(e * 5) * math.exp(-e * 1.5) + 3 * math.sin(e * 2.2)
    return (f'<g transform="translate({f(x)} {f(y + 6 * math.sin(e * 3))}) rotate({f(rot)}) scale({f(sc)})">'
            f'<text x="0" y="{f(size * .36)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="{size}" '
            f'fill="#fff8e6" stroke="{INK}" stroke-width="16" stroke-linejoin="round" paint-order="stroke">?</text></g>')


def cal_page(k, x0, y0, x1, y1, seed=0):
    """Лист календаря месяца k: красная шапка с названием, сетка чисел."""
    s = []
    w, h = x1 - x0, y1 - y0
    inner = blob(rect_pts(x0, y0, x1, y0 + h * .26), "#d9463a")
    inner += blob(rect_pts(x0, y1 - 18, x1, y1), "#e9e2d2")
    fs = min(52, w / (len(MONTHS[k]) * 0.68))
    inner += (f'<text x="{f((x0 + x1) / 2)}" y="{f(y0 + h * .13 + fs * .36)}" text-anchor="middle" font-family="IDB" font-weight="900" '
              f'font-size="{f(fs)}" fill="#fff8ee">{MONTHS[k]}</text>')
    start = (k * 3 + 2) % 7
    n = 31 if k in (0, 2, 4, 6) else (28 if k == 1 else 30)
    cw = (w - 30) / 7
    rh = (h * .7 - 30) / 6
    for d in range(1, n + 1):
        i = start + d - 1
        col, row = i % 7, i // 7
        cx = x0 + 15 + cw * (col + .5)
        cy = y0 + h * .26 + 20 + rh * (row + .5)
        c = "#d9463a" if col >= 5 else "#2b2a33"
        inner += (f'<text x="{f(cx)}" y="{f(cy + 9)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="24" '
                  f'fill="{c}">{d}</text>')
    s.append(shape(rect_pts(x0, y0, x1, y1, 4), "#fbf7ee", inner, w=4, seed=seed))
    return "".join(s)


def calendar(t, nflown):
    """Отрывной календарь: подложка, кольца, стопка листов; слетевшие листы улетают вправо, кувыркаясь."""
    x0, y0, x1, y1 = CAL
    s = []
    s.append(blob(rect_pts(x0 + 10, y0 + 14, x1 + 12, y1 + 16, 6), "#5a3a1c", .25, blur(8)))
    s.append(shape(rect_pts(x0 - 10, y0 - 14, x1 + 10, y1 + 10, 8), "#7a5233", "", w=4.4, seed=600))
    # стопка: ниже — следующий месяц, сверху — текущий
    cur = min(len(MONTHS) - 1, nflown)
    s.append(blob(rect_pts(x0 + 4, y0 + 10, x1 + 4, y1 + 6), "#d9d0bc"))
    s.append(cal_page(cur, x0, y0 + 6, x1, y1, seed=610 + cur))
    # шапка с кольцами
    s.append(shape(rect_pts(x0 - 10, y0 - 22, x1 + 10, y0 + 14, 6), "#c0392f", "", w=4.4, seed=601))
    for k in range(6):
        x = x0 + 26 + k * (x1 - x0 - 52) / 5
        s.append(shape(rect_pts(x - 6, y0 - 4, x + 6, y0 + 26, 6), "#c9ced8", "", w=3, seed=602 + k))
    return "".join(s)


def flying_pages(t):
    x0, y0, x1, y1 = CAL
    s = []
    for k, tf in enumerate(FLY):
        e = t - tf
        if e < -0.08 or e > 0.9:
            continue
        if e < 0:
            # лист чуть приподнимается у низа перед отрывом
            continue
        u = e / 0.9
        dx = 560 * ease_out(u, 2) + 40 * math.sin(e * 9)
        dy = -160 * math.sin(min(1, u * 1.6) * math.pi / 2) + 520 * u * u
        rot = 30 * ease_out(u, 2) + 160 * u * u
        sxx = 0.55 + 0.45 * math.cos(e * 11)
        cx, cy = (x0 + x1) / 2, y0 + 6
        s.append(f'<g transform="translate({f(cx + dx)} {f(cy + dy)}) rotate({f(rot)}) scale({f(sxx)} 1) translate({f(-cx)} {f(-cy)})">'
                 + cal_page(k, x0, y0 + 6, x1, y1, seed=620 + k) + "</g>")
        if e < 0.25:
            a = 1 - e / 0.25
            for j in range(3):
                yy = y0 + 80 + j * 90
                s.append(line([(x1 + 20 + 20 * j, yy), (x1 + 20 + 20 * j + 70 * a, yy - 30 * a)], 7 * a + 1, INK, taper=.5,
                              seed=640 + j + k * 3))
    return "".join(s)


def check_mark(t, t0, x, y, sz):
    e = t - t0
    if e < 0:
        return ""
    pts = [(x - sz * .45, y), (x - sz * .1, y + sz * .38), (x + sz * .55, y - sz * .5)]
    L1 = math.dist(pts[0], pts[1])
    L2 = math.dist(pts[1], pts[2])
    u = clamp(e / 0.2) * (L1 + L2)
    if u <= L1:
        q = [pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * u / L1, pts[0][1] + (pts[1][1] - pts[0][1]) * u / L1)]
    else:
        v = (u - L1) / L2
        q = [pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * v, pts[1][1] + (pts[2][1] - pts[1][1]) * v)]
    d = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in q)
    pulse = 1 + 0.12 * math.exp(-max(0, e - 0.2) * 7) * math.sin(max(0, e - 0.2) * 18)
    s = [f'<g transform="translate({f(x)} {f(y)}) scale({f(pulse)}) translate({f(-x)} {f(-y)})">']
    s.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{f(sz * .27)}" stroke-linecap="round" stroke-linejoin="round"/>')
    s.append(f'<path d="{d}" fill="none" stroke="#4cc25a" stroke-width="{f(sz * .17)}" stroke-linecap="round" stroke-linejoin="round"/>')
    if len(q) == 3 or u > L1 * 0.6:
        hl = [(pts[0][0] + 6, pts[0][1] - 8), (pts[1][0] + 2, pts[1][1] + sz * .38 * 0 - 14)]
        s.append(f'<path d="M{f(hl[0][0])} {f(hl[0][1])} L{f(hl[1][0])} {f(hl[1][1])}" fill="none" stroke="#9cf0a2" '
                 f'stroke-width="{f(sz * .045)}" stroke-linecap="round"/>')
    s.append("</g>")
    return "".join(s)


def sparkles(t, t0, pts, life=1.2, base=26):
    s = []
    for k, (x, y, d) in enumerate(pts):
        e = t - t0 - d
        if e < 0 or e > life:
            continue
        sc = back_out(clamp(e / 0.18), 2.5) * (1 - smooth(life - 0.25, life, e))
        if sc < 0.03:
            continue
        r = base * sc * (1 + 0.15 * math.sin(e * 14 + k))
        s.append(fish.sparkle(x, y - 20 * e, r, rot=e * 90 + k * 20, color="#ffe066" if k % 2 == 0 else "#fff3b0", lw=3.2, seed=700 + k))
    return "".join(s)


# ─────────────────────────────── планы
def scene_layers(t, fish_svg_back="", fish_svg_front="", extra_in_water="", cal_n=0):
    """Комната + календарь + шар; рыбка (сзади/спереди водоросли) клипуется по шару."""
    s = [_ST["room"], calendar(t, cal_n)]
    s.append(_ST["bowl_back"])
    cb = _ST["clip_bowl"]
    s.append(f'<g clip-path="url(#{cb})">')
    s.append(weed(t, (410, 1080), 250, 3, 800, lean=-0.3))
    s.append(fish_svg_back)
    s.append(bubbles(t, 452, 1050, seed=3))
    s.append(weed(t + 0.7, (690, 1100), 200, 2, 820, lean=0.3, k_amp=0.8))
    s.append(fish_svg_front)
    s.append(extra_in_water)
    s.append("</g>")
    s.append(surface(t))
    s.append(_ST["bowl_front"])
    return "".join(s)


def lw_for(sc, cam_s, px=7.0):
    return px / (sc * cam_s)


def frame01(t):
    # камера-влёт: 1/(1+0.4) → 1 за 0.22 с с перелётом 5 %, поворот −3° → 0, удар +8 % на «рыбки»
    base_s, cx, cy = 1.22, 540, 900
    if t < 0.22:
        m = 1 / 1.4 + (1.05 - 1 / 1.4) * ease_out(t / 0.22, 3)
        rot = -3.2 + 3.9 * ease_out(t / 0.22, 3)
    else:
        e = t - 0.22
        m = 1 + 0.05 * math.exp(-e * 9) * math.cos(e * 14)
        rot = 0.7 * math.exp(-e * 8) * math.cos(e * 12)
    hit = 1.2
    if t >= hit:
        e = t - hit
        m *= 1 + 0.08 * math.exp(-e * 7) * min(1, e / 0.05)
    m *= 1 + 0.025 * t
    sc = base_s * m
    cx += 30 * (1 - ease_out(clamp(t / 0.22)))
    cy += 50 * (1 - ease_out(clamp(t / 0.22)))
    # рыбка по кругу (с кадра 0 на скорости)
    th = math.pi - 2 * math.pi * (t + 0.08) / 1.5
    fx = 540 + 150 * math.cos(th)
    fy = 925 + 52 * math.sin(th)
    depth = math.sin(th)
    fsc = 0.70 + 0.09 * depth
    face = clamp(depth * 2.4, -1, 1)
    vy = -52 * math.cos(th)
    rot = clamp(vy * 0.06, -10, 10) * (1 if face >= 0 else -1)
    fsvg = fish.draw(fx, fy, fsc, t, face=face, rot=rot, swim=1.3, freq=2.6, look=(0.6, -0.1), lw=lw_for(fsc, sc))
    fsvg += bubbles(t, *fish.nose(fx, fy, fsc, face), n=3, period=0.3, speed=150, seed=11, r0=6) if t > 0.4 else ""
    art = scene_layers(t, fsvg if depth < 0 else "", fsvg if depth >= 0 else "")
    bob = 8 * math.sin(t * 3.2)
    art += timer(t, "3", 1.0, sc=1 + 0.04 * math.sin(t * 6), bob=bob)
    art += _ST["light"]
    return art, cam(cx, cy, sc, rot)


def frame02(t):
    T3, T2, T1, TP = 2.16, 2.26, 2.33, 2.40
    TQ, TT = 2.48, 2.72
    # камера: наезд, толчок на «секунды»
    u = clamp((t - 1.2) / (TP - 1.2))
    sc = 1.86 + 0.2 * ease_io(u)
    cx, cy = 548, 800 + 10 * ease_io(u)
    rot = -0.8 + 0.8 * u
    if t >= TP:
        e = t - TP
        sc *= 1 + 0.08 * math.exp(-e * 8) * min(1, e / 0.04)
        cy += 7 * math.exp(-e * 10) * math.sin(e * 50)
        sc *= 1 + 0.02 * (e / 0.75)
        cy += 30 * ease_io(clamp(e / 0.5))
    if T3 <= t < T3 + 0.2:
        sc *= 1 + 0.025 * math.sin((t - T3) / 0.2 * math.pi)
    # рыбка
    frozen = smooth(TP, TP + 0.06, t)
    blank = smooth(TP, TP + 0.08, t)
    turn = ease_io(clamp((t - TT) / 0.11))
    face = 1 - 2 * turn
    fx = 548 - 90 * ease_in(clamp((t - TT - 0.1) / 0.5), 1.6)
    fy = 846 + 10 * math.sin(t * 2.2) * (1 - frozen) - 18 * math.sin(math.pi * clamp((t - TT) / 0.2))
    ph = (min(t, TP) * 1.4 + max(0, t - TP) * (0.05 if t < TT else 1.2)) * 2 * math.pi
    swim = 0.55 * (1 - frozen) + 0.05 + 0.6 * smooth(TT, TT + 0.2, t)
    look = (0.15, -0.85) if t < TP else (0.0, 0.0)
    mo = 0.2 + 0.2 * math.sin(t * 5.3) if t < TP else 0.55
    fsc = 0.8
    fsvg = fish.draw(fx, fy, fsc, t, face=face, swim=swim, ph=ph, look=look, blank=blank, mouth_open=mo,
                     brow=-0.7 * blank, lw=lw_for(fsc, sc))
    if t < TP:
        fsvg += bubbles(t, *fish.nose(fx, fy, fsc, face), n=3, period=0.45, speed=120, seed=12, r0=6)
    art = scene_layers(t, "", fsvg)
    # таймер
    if t < TP:
        if t < T3:
            dg, prog = "3", 1.0 - 0.04 * ((t - 1.2) / (T3 - 1.2))
        elif t < T2:
            dg, prog = "3", 0.96 - 0.3 * (t - T3) / (T2 - T3)
        elif t < T1:
            dg, prog = "2", 0.66 - 0.33 * (t - T2) / (T1 - T2)
        else:
            dg, prog = "1", 0.33 - 0.33 * (t - T1) / (TP - T1)
        tk = min([abs(t - x) for x in (T3, T2, T1)] + [9])
        sp = 1 + (0.22 if t >= T3 else 0) * math.exp(-max(0, min(t - T3 if t < T2 else (t - T2 if t < T1 else t - T1), 1)) * 14)
        sp *= 1 + 0.05 * smooth(TP - 0.05, TP, t)
        del tk
        art += timer(t, dg, prog, sc=sp, bob=6 * math.sin(t * 3.2))
    art += pop(t, TP)
    art += question(t, TQ, TX - 10, TY - 30, 230)
    art += _ST["light"]
    return art, cam(cx, cy, sc, rot)


def frame07(t):
    TW, TN = 9.72, 10.84
    u = clamp((t - 8.9) / 2.1)
    sc = 2.45 + 0.2 * ease_io(u)
    cx, cy = 492 + 14 * ease_io(u), 868 + 4 * u
    rot = 0.8 - 1.4 * u
    if t >= TW:
        e = t - TW
        sc *= 1 + 0.035 * math.exp(-e * 8) * min(1, e / 0.04)
    if t >= TN - 0.05:
        e = t - TN + 0.05
        cy += 8 * math.exp(-e * 9) * math.sin(e * 30)
    fx = 548 + 22 * ease_io(u)
    fy = 884 + 8 * math.sin(t * 2.3)
    wink = smooth(TW - 0.1, TW, t) * (1 - smooth(TW + 0.24, TW + 0.36, t))
    nod = math.sin(math.pi * clamp((t - (TN - 0.08)) / 0.24)) if t > TN - 0.08 else 0.0
    frot = -4 + 12 * nod
    fsc = 0.8
    fsvg = fish.draw(fx, fy, fsc, t, face=1, rot=frot, swim=0.5, freq=1.3, look=(0.55, 0.15), lid=0.42 - 0.1 * nod, wink=wink,
                     mouth="grin", brow=0.9, lw=lw_for(fsc, sc))
    fsvg += bubbles(t, *fish.nose(fx, fy, fsc, 1), n=3, period=0.55, speed=110, seed=17, r0=6)
    art = scene_layers(t, "", fsvg)
    sp = [(fx + 150, fy - 110, 0.0), (fx - 90, fy - 140, 0.05), (fx + 170, fy + 40, 0.1), (fx - 180, fy - 20, 0.14),
          (fx + 40, fy - 175, 0.08)]
    art += sparkles(t, TW, sp, life=1.25, base=22)
    art += _ST["light"]
    return art, cam(cx, cy, sc, rot)


def frame08(t):
    u = clamp((t - 10.6) / 0.62)
    k = ease_io(u)
    sc = 2.3 + (1.1 - 2.3) * k
    sc *= 1 - 0.03 * clamp((t - 11.2) / 1.2)
    cx = 560 + (700 - 560) * k + 10 * clamp((t - 11.2) / 1.2)
    cy = 852 + (850 - 852) * k
    rot = -0.6 + 0.6 * k
    for tf in FLY:
        if t >= tf:
            e = t - tf
            sc *= 1 + 0.012 * math.exp(-e * 10) * min(1, e / 0.04)
    # рыбка спокойно плывёт вправо-влево по шару и смотрит на календарь
    p = (t - 10.6) / 1.8
    fx = 545 + 70 * math.sin(p * 2.0 - 0.3)
    fy = 880 - 16 * math.sin(p * 3.0)
    face = 1.0
    fsc = 0.8
    look = (0.65, -0.7) if t > 11.05 else (0.4, -0.2)
    lk = smooth(10.9, 11.15, t)
    look = (0.4 + (0.75 - 0.4) * lk, -0.2 + (-0.75 + 0.2) * lk)
    fsvg = fish.draw(fx, fy, fsc, t, face=face, rot=-6 * lk, swim=0.6, freq=1.2, look=look, lw=lw_for(fsc, sc))
    fsvg += bubbles(t, *fish.nose(fx, fy, fsc, face), n=3, period=0.5, speed=120, seed=19, r0=6)
    nfl = sum(1 for x in FLY if t >= x)
    art = scene_layers(t, "", fsvg, cal_n=nfl) + flying_pages(t)
    art += _ST["light"]
    return art, cam(cx, cy, sc, rot)


def frame11(t):
    TC = 17.32
    u = clamp((t - 16.3) / 1.9)
    sc = 2.02 + 0.12 * ease_io(u)
    cx, cy = 516 + 10 * u, 858
    rot = -1 + 1.6 * u
    if t >= TC:
        e = t - TC
        sc *= 1 + 0.06 * math.exp(-e * 7) * min(1, e / 0.05)
        cy += 6 * math.exp(-e * 10) * math.sin(e * 45)
    # рыбка вплывает гордо, грудь колесом, на «помнит» — глаза-дуги от удовольствия
    k = ease_out(clamp((t - 16.3) / 0.5))
    fx = 470 + 40 * k + 6 * math.sin(t * 2)
    fy = 880 - 8 * math.sin(t * 2.4)
    happy = 1.0 if TC - 0.04 <= t < TC + 0.4 else 0.0
    puff = 1 + 0.05 * math.exp(-max(0, t - TC) * 5) * (t >= TC)
    fsc = 0.8 * puff
    fsvg = fish.draw(fx, fy, fsc, t, face=1, rot=-9, swim=0.7, freq=1.5, look=(0.5, -0.15), lid=0.5, happy=happy, mouth="smile", brow=0.5,
                     medal=smooth(16.3, 16.5, t), lw=lw_for(fsc, sc))
    fsvg += bubbles(t, *fish.nose(fx, fy, fsc, 1, -9), n=3, period=0.32, speed=150, seed=23, r0=7)
    art = scene_layers(t, "", fsvg)
    art += bubbles(t + 0.2, 700, 1040, period=0.3, speed=200, seed=29, r0=8)
    cxk, cyk = 648, 640
    art += check_mark(t, TC, cxk, cyk, 160)
    art += sparkles(t, TC + 0.18, [(cxk + 120, cyk - 110, 0), (cxk - 120, cyk - 120, 0.05), (cxk + 130, cyk + 80, 0.1)], life=0.85, base=22)
    art += _ST["light"]
    return art, cam(cx, cy, sc, rot)


def frame(sid, t):
    if not _ST:
        _ST["room"] = room()
        _ST["bowl_back"] = bowl_back()
        _ST["bowl_front"] = bowl_front()
        _ST["light"] = light()
        lib.static_done()
    lib.dyn_begin()
    fn = {"s01": frame01, "s02": frame02, "s07": frame07, "s08": frame08, "s11": frame11}[sid]
    art, cm = fn(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#ecd6ae"/><g transform="{cm}">{art}</g>')


_unused = (H, fill_d, spring, ease_in)
