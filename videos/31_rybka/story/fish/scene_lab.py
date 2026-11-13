"""Сцена lab рилса 31: прямоугольный аквариум с рычажком у правой стенки и кормушкой на крышке, над ним настенные часы,
слева окно (день/ночь). Та же золотая рыбка (fish.py).
s09 — рыбка подплывает и носом нажимает рычажок на «нажимать» (13.04), на «едой» (14.08) из кормушки сыплются хлопья,
      рыбка ест.
s10 — часы: стрелки ускоренно крутятся сутки (за окном день→ночь→день) и встают на 8:00 на «время» (15.68); камера
      спускается к рыбке, которая уже ждёт у рычажка."""
import math

import numpy as np

import fish
import lib
from lib import (DEFS, INK, W, H, blob, blur, cam, clamp, clip_of, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad,
                 rect_pts, shape, smooth, spring, svg)

_ST = {}
TX0, TX1, TTOP, TBOT = 110, 970, 700, 1214     # аквариум (рамка)
WL = 762                                       # уровень воды
PIV = (946, 910)                               # ось рычажка
ARM = 92
A_REST, A_PRESS = 180.0, 156.0
FEED = (742, 880, 598, 700)                    # кормушка x0 x1 y0 y1
CHUTE = (812, 734)
CLK = (770, 340, 150)
WIN = (150, 120, 520, 560)
TPRESS, TFOOD = 13.04, 14.08
TSTOP = 15.68
FS = 0.85


# ─────────────────────────────── статика
def room():
    s = []
    DEFS.append('<pattern id="pWallL" width="90" height="90" patternUnits="userSpaceOnUse">'
                '<rect width="90" height="90" fill="#e5dcc0"/><rect x="0" width="26" height="90" fill="#ddd2b2"/>'
                '<path d="M58 30 l6 6 l-6 6 l-6 -6Z" fill="#d2c39e"/></pattern>')
    s.append(f'<rect x="-900" y="-1200" width="3000" height="{TBOT + 1300}" fill="url(#pWallL)"/>')
    # полка с книгами справа от окна, под часами — нет; рамка окна (небо рисуется динамически)
    x0, y0, x1, y1 = WIN
    _ST["clip_win"] = clip_of(rect_pts(x0, y0, x1, y1))
    # шкаф-тумба под аквариумом
    wood, wood_sh, wood_top = "#b97f4c", "#94603a", "#d39b62"
    s.append(shape([(-460, TBOT - 6, 1), (1540, TBOT - 6, 1), (1570, TBOT + 30, 1), (-490, TBOT + 30, 1)], wood_top, "", w=4.6, seed=31))
    s.append(shape(rect_pts(-490, TBOT + 30, 1570, TBOT + 62, 4), wood, blob(rect_pts(-490, TBOT + 50, 1570, TBOT + 62), wood_sh), w=4.6,
                   seed=32))
    inner = blob(rect_pts(1300, TBOT + 62, 1550, 2600), wood_sh, .9)
    s.append(shape(rect_pts(-460, TBOT + 62, 1540, 2600), wood, inner, w=5, seed=33))
    for k, (a, b) in enumerate([(30, 520), (560, 1050)]):
        s.append(shape(rect_pts(a, TBOT + 110, b, TBOT + 560, 10), "#c48a55", blob(rect_pts(a, TBOT + 520, b, TBOT + 560), wood_sh, .8), w=4.6,
                       seed=34 + k))
        s.append(shape(ellipse_pts(b - 50 if k == 0 else a + 50, TBOT + 330, 16, 16, 12), "#e2c08a", "", w=4, seed=36 + k))
    s.append(blob(rect_pts(TX0 + 20, TBOT - 10, TX1 + 20, TBOT + 8), "#3a2410", .35, blur(8)))
    # банка корма на тумбе слева
    jx = 40
    s.append(shape(rect_pts(jx - 40, TBOT - 120, jx + 40, TBOT - 4, 12), "#f2c23a",
                   blob(rect_pts(jx - 40, TBOT - 80, jx + 40, TBOT - 40), "#e85a3c") + blob(rect_pts(jx + 14, TBOT - 120, jx + 40, TBOT - 4), "#d39e22", .8),
                   w=4.2, seed=37))
    s.append(shape(rect_pts(jx - 44, TBOT - 140, jx + 44, TBOT - 116, 8), "#5aa05a", "", w=4, seed=38))
    return "".join(s)


def tank_back():
    """Задняя стенка, вода, грунт, растения сзади (статика)."""
    s = []
    inner_r = rect_pts(TX0 + 8, TTOP + 22, TX1 - 8, TBOT - 22)
    _ST["clip_tank"] = clip_of(inner_r)
    s.append(blob(inner_r, "#e9efe2"))
    wr = rect_pts(TX0 + 8, WL, TX1 - 8, TBOT - 22)
    g = lin_grad([(0, "#a7dfe8", 1), (0.6, "#7cc4d6", 1), (1, "#4f9ebd", 1)], 0, 0, 0, 1)
    inner = []
    for k, (x, a) in enumerate([(300, .35), (520, .28), (760, .3)]):
        inner.append(blob([(x - 40, WL), (x + 30, WL), (x + 110, TBOT), (x - 10, TBOT)], "#c6eef3", a))
    rs = np.random.RandomState(9)
    cols = ["#e8b07a", "#c97b5a", "#8fb8a0", "#f0d9a8", "#a99bc4", "#d98e6a", "#f3c98b"]
    inner.append(blob([(TX0, 1140), (400, 1128), (700, 1134), (TX1, 1124), (TX1, TBOT), (TX0, TBOT)], "#c99a6c"))
    for row, (y, n) in enumerate([(1140, 30), (1162, 34), (1184, 36)]):
        for i in range(n):
            x = TX0 + (TX1 - TX0) * (i + rs.uniform(0.1, 0.9)) / n
            rx, ry = rs.uniform(12, 19), rs.uniform(7, 11)
            c = cols[rs.randint(len(cols))]
            inner.append(shape(ellipse_pts(x, y + rs.uniform(-4, 4), rx, ry, 10, rot=rs.uniform(-20, 20)), c,
                               blob(ellipse_pts(x + rx * .25, y + ry * .45, rx * .8, ry * .45, 8), mix(c, "#5a3a2a", .25)), w=2.4,
                               seed=200 + row * 40 + i))
    rock = [(470, 1140), (478, 1082), (512, 1052), (556, 1048), (592, 1068), (608, 1110), (612, 1142)]
    inner.append(shape(rock, "#9aa3ad", blob([(556, 1048), (592, 1068), (608, 1110), (612, 1142), (566, 1142)], "#7b8490") +
                       blob(ellipse_pts(520, 1070, 16, 8, 8, rot=-30), "#c2c9d0"), w=4.2, seed=120))
    s.append(f'<g clip-path="url(#{_ST["clip_tank"]})">' + shape(wr, f"url(#{g})", "".join(inner), w=.1, ink=False) + "</g>")
    return "".join(s)


def tank_front():
    s = []
    # поверхность воды — полоса
    s.append(line([(TX0 + 10, WL), (TX1 - 10, WL)], 4, "#3d7f93", taper=.05, wmin=.9, seed=140))
    s.append(blob(rect_pts(TX0 + 10, WL - 2, TX1 - 10, WL + 8), "#c4ecf2"))
    s.append(line([(TX0 + 10, WL + 9), (TX1 - 10, WL + 9)], 2.6, "#5c9fb2", taper=.05, wmin=.9, seed=141))
    # стекло: блики
    for k, (x, w_) in enumerate([(190, 18), (230, 8), (880, 10)]):
        s.append(line([(x, TTOP + 60), (x + 70, TTOP + 300)], w_, "#ffffff", taper=.8, wmin=.2, seed=150 + k, op=.85))
    # рамка: верх и низ, рёбра
    s.append(shape(rect_pts(TX0 - 10, TTOP, TX1 + 10, TTOP + 22, 6), "#2f3a40", blob(rect_pts(TX0 - 10, TTOP, TX1 + 10, TTOP + 7), "#4c5a62"),
                   w=4.6, seed=160))
    s.append(shape(rect_pts(TX0 - 10, TBOT - 24, TX1 + 10, TBOT, 6), "#2f3a40", blob(rect_pts(TX0 - 10, TBOT - 24, TX1 + 10, TBOT - 17), "#4c5a62"),
                   w=4.6, seed=161))
    for k, x in enumerate((TX0, TX1)):
        s.append(shape(rect_pts(x - 8, TTOP + 18, x + 8, TBOT - 20), "#cfe5e8", "", w=3.8, seed=162 + k))
    # трубка от рычажка к кормушке (снаружи правой стенки)
    tube = [(TX1 + 8, PIV[1]), (TX1 + 34, PIV[1] - 10), (TX1 + 40, 760), (TX1 + 34, 660), (FEED[1] + 40, 640), (FEED[1], 650)]
    s.append(line(tube, 18, INK, taper=.02, wmin=.95, seed=170))
    s.append(line(tube, 10, "#9aa0ab", taper=.02, wmin=.95, seed=171))
    s.append(shape(ellipse_pts(TX1 + 14, PIV[1], 12, 16, 10), "#7b8494", "", w=3.4, seed=172))
    return "".join(s)


def weeds(t):
    s = []
    for base, h, n, seed in [((200, 1150), 300, 3, 800), ((300, 1150), 230, 2, 820), ((640, 1150), 200, 2, 840)]:
        for j in range(n):
            bx = base[0] + (j - (n - 1) / 2) * 24
            hh = h * (1 - 0.15 * abs(j - (n - 1) / 2))
            pts = []
            for i in range(7):
                u = i / 6
                sw = 18 * math.sin(t * 1.8 + j * 1.3 + base[0] * .01 + u * 2.4) * u ** 1.3
                pts.append((bx + sw + 16 * (j - (n - 1) / 2) * u, base[1] - hh * u))
            c = "#5aa05a" if j % 2 == 0 else "#4b8f4e"
            s.append(shape(lib.band(pts, 28, 6), c, line(pts[:6], 2.6, "#3a7440", seed=seed + 10 + j), w=3.6, seed=seed + j))
    return "".join(s)


# ─────────────────────────────── динамика
def daylight(h):
    """1 — день, 0 — ночь по часу суток h."""
    h = h % 24
    return smooth(5.5, 7.5, h) * (1 - smooth(18.5, 20.5, h))


def window(h):
    x0, y0, x1, y1 = WIN
    d = daylight(h)
    s = []
    sky_top = mix("#1a2348", "#79bde6", d)
    sky_bot = mix("#2c3a68", "#bfe4f4", d)
    dusk = math.exp(-((h % 24 - 19.5) ** 2) / 1.2) + math.exp(-((h % 24 - 6.5) ** 2) / 1.2)
    sky_bot = mix(sky_bot, "#f2a868", clamp(dusk * .7))
    g = lin_grad([(0, sky_top, 1), (1, sky_bot, 1)], 0, 0, 0, 1)
    inner = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>']
    # солнце по дуге днём, луна ночью
    hs = h % 24
    if 5 < hs < 21:
        u = (hs - 5) / 16
        sx, sy = x0 + 40 + (x1 - x0 - 80) * u, y1 - 60 - 300 * math.sin(math.pi * u)
        inner.append(shape(ellipse_pts(sx, sy, 34, 34, 16), "#ffd75a", "", w=3.4, seed=500))
    hm = (hs - 17) % 24
    if hm < 14:
        u = hm / 14
        mx, my = x0 + 40 + (x1 - x0 - 80) * u, y1 - 70 - 280 * math.sin(math.pi * u)
        inner.append(shape(ellipse_pts(mx, my, 28, 28, 16), "#f3ead0", blob(ellipse_pts(mx + 12, my - 6, 22, 24, 14), sky_top), w=3.2,
                           seed=501))
    if d < 0.6:
        for k, (x, y) in enumerate([(200, 170), (330, 240), (450, 160), (260, 330), (480, 300), (380, 420)]):
            r = 4 * (1 - d / 0.6)
            inner.append(blob(ellipse_pts(x, y, r, r, 6), "#f3ead0"))
    # дома напротив
    roofs = mix("#1c2340", "#8ea3b8", d)
    inner.append(blob([(x0, 470), (220, 450), (220, 410), (330, 410), (330, 460), (x1, 440), (x1, y1), (x0, y1)], roofs))
    wc = mix("#f2c46a", "#c9d6e0", d)
    for k, (x, y) in enumerate([(250, 430), (290, 430), (380, 480), (450, 470)]):
        inner.append(blob(rect_pts(x, y, x + 22, y + 28), wc))
    inner.append(blob(rect_pts((x0 + x1) / 2 - 12, y0, (x0 + x1) / 2 + 12, y1), "#efe6d6"))
    inner.append(blob(rect_pts(x0, (y0 + y1) / 2 - 10, x1, (y0 + y1) / 2 + 12), "#efe6d6"))
    s.append(shape(rect_pts(x0, y0, x1, y1, 8), "#efe6d6", "".join(inner), w=5, seed=502))
    s.append(shape(rect_pts(x0 - 26, y1 - 6, x1 + 26, y1 + 30, 6), "#efe6d6", "", w=4.4, seed=503))
    # шторы
    for k, (a, b) in enumerate([(x0 - 70, x0 + 30), (x1 - 30, x1 + 70)]):
        pts = [(a, y0 - 40, 1), (b, y0 - 40, 1), (b - 10 + 8 * k, y1 + 60), (a + 10, y1 + 70, 1)]
        s.append(shape(pts, "#d9a640", line([((a + b) / 2, y0), ((a + b) / 2 + 6, y1 + 50)], 3, "#b8862c", seed=505 + k), w=4.4, seed=504 + k))
    s.append(shape(rect_pts(x0 - 100, y0 - 56, x1 + 100, y0 - 40, 6), "#8e6a44", "", w=4, seed=508))
    return "".join(s)


def clock(t, h, spin=0.0, ding=None):
    """Настенные часы: деревянный обод, кремовый циферблат, цифры 12/3/6/9 кодом, часовая/минутная/секундная стрелки."""
    cx, cy, r = CLK
    s = [blob(ellipse_pts(cx + 10, cy + 14, r + 14, r + 14, 24), "#4a2c12", .25, blur(8))]
    s.append(shape(ellipse_pts(cx, cy, r + 16, r + 16, 28), "#a8703f", blob(ellipse_pts(cx + 10, cy + 12, r + 4, r + 4, 24), "#8a5a30"), w=5,
                   seed=600))
    s.append(shape(ellipse_pts(cx, cy, r - 6, r - 6, 28), "#fbf4e2", blob(ellipse_pts(cx + 18, cy + 28, r - 20, r - 30, 24), "#efe4c8"),
                   w=4, seed=601))
    for k in range(60):
        a = math.radians(k * 6 - 90)
        r0 = r - 20 if k % 5 == 0 else r - 14
        w_ = 5 if k % 5 == 0 else 2.4
        s.append(line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + (r - 8) * math.cos(a), cy + (r - 8) * math.sin(a))], w_, INK,
                      taper=.05, wmin=.9, seed=610 + k))
    for n_, k in (("12", 0), ("3", 3), ("6", 6), ("9", 9)):
        a = math.radians(k * 30 - 90)
        rr = r - 52
        s.append(f'<text x="{f(cx + rr * math.cos(a))}" y="{f(cy + rr * math.sin(a) + 19)}" text-anchor="middle" font-family="IDB" '
                 f'font-weight="900" font-size="54" fill="#2b2a33">{n_}</text>')
    ah = math.radians((h % 12) * 30 - 90)
    am = math.radians((h % 1) * 360 - 90)
    # след стрелок при быстром вращении (непрозрачный бледный веер)
    if spin > 0.05:
        span = min(170, spin * 2.2)
        a0 = math.degrees(am) - span
        pts = [(cx, cy)] + [(cx + (r - 30) * math.cos(math.radians(a)), cy + (r - 30) * math.sin(math.radians(a)))
                            for a in np.linspace(a0, math.degrees(am), 12)]
        s.append(blob(pts, "#e6dcc4"))
        span2 = min(90, spin * 0.2)
        a0 = math.degrees(ah) - span2
        pts = [(cx, cy)] + [(cx + (r - 70) * math.cos(math.radians(a)), cy + (r - 70) * math.sin(math.radians(a)))
                            for a in np.linspace(a0, math.degrees(ah), 8)]
        if span2 > 2:
            s.append(blob(pts, "#e3d8bd"))
    for a, L, wd, c, sd in ((ah, r - 72, 15, "#2b2a33", 640), (am, r - 30, 10, "#2b2a33", 641)):
        tip = (cx + L * math.cos(a), cy + L * math.sin(a))
        back = (cx - 22 * math.cos(a), cy - 22 * math.sin(a))
        s.append(line([back, tip], wd, c, taper=.3, wmin=.45, seed=sd, peak=.3))
    asec = math.radians((math.floor(t * 1.0) * 6 + 6 * ease_out(clamp((t % 1) / 0.12))) - 90) if spin < 0.05 else am * 3
    s.append(line([(cx - 30 * math.cos(asec), cy - 30 * math.sin(asec)), (cx + (r - 22) * math.cos(asec), cy + (r - 22) * math.sin(asec))],
                  4, "#d6342c", taper=.05, wmin=.8, seed=642))
    s.append(shape(ellipse_pts(cx, cy, 12, 12, 12), "#d6342c", "", w=3, seed=643))
    if ding is not None and 0 <= ding < 0.4:
        u = ding / 0.4
        for k in range(10):
            a = math.radians(k * 36 + 18)
            r0 = r + 30 + 40 * ease_out(u)
            r1 = r0 + 50 * (1 - u)
            s.append(line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], 10 * (1 - u) + 2,
                          INK, taper=.5, seed=650 + k))
    return "".join(s)


def lever(a, glow=0.0):
    px, py = PIV
    kx, ky = px + ARM * math.cos(math.radians(a)), py + ARM * math.sin(math.radians(a))
    s = [shape(rect_pts(px - 4, py - 34, px + 18, py + 34, 6), "#7b8494", "", w=3.6, seed=700)]
    s.append(line([(px, py), (kx, ky)], 20, INK, taper=.02, wmin=.95, seed=701))
    s.append(line([(px, py), (kx, ky)], 11, "#c9ced8", taper=.02, wmin=.95, seed=702))
    s.append(shape(ellipse_pts(px, py, 11, 11, 10), "#9aa0ab", "", w=3, seed=703))
    s.append(shape(ellipse_pts(kx, ky, 22, 22, 14), "#e0412f", blob(ellipse_pts(kx + 6, ky + 7, 15, 13, 10), "#b42d22") +
                   f'<circle cx="{f(kx - 7)}" cy="{f(ky - 8)}" r="5" fill="#ffb4a2"/>', w=4, seed=704))
    return "".join(s), (kx, ky)


def feeder(t, lamp, shake=0.0):
    x0, x1, y0, y1 = FEED
    dx = shake * 4 * math.sin(t * 70)
    s = [f'<g transform="translate({f(dx)} 0)">']
    s.append(shape([(CHUTE[0] - 22, y1 - 4, 1), (CHUTE[0] + 22, y1 - 4, 1), (CHUTE[0] + 12, CHUTE[1], 1), (CHUTE[0] - 12, CHUTE[1], 1)],
                   "#c9ced8", "", w=3.6, seed=710))
    s.append(shape(rect_pts(x0, y0, x1, y1, 14), "#f2c23a", blob(rect_pts(x1 - 34, y0, x1, y1), "#d39e22", .9) +
                   blob(rect_pts(x0 + 18, y0 + 22, x0 + 74, y0 + 64, 8), "#fff3c8"), w=4.6, seed=711))
    for k in range(4):
        s.append(blob(ellipse_pts(x0 + 30 + k * 12, y0 + 44 + (k % 2) * 6, 6, 4, 6, rot=k * 40), ["#e85a3c", "#c97b3a", "#f08a3c", "#a5502a"][k]))
    s.append(shape(rect_pts(x0 - 8, y0 - 18, x1 + 8, y0 + 4, 6), "#e85a3c", "", w=4, seed=712))
    lc = mix("#7a2a20", "#5ee06a", lamp)
    s.append(shape(ellipse_pts(x1 - 54, y0 + 40, 14, 14, 12), lc, f'<circle cx="{f(x1 - 58)}" cy="{f(y0 + 36)}" r="4" fill="#ffffff"/>' if lamp > .5 else "",
                   w=3.4, seed=713))
    s.append("</g>")
    if shake > 0.05:
        for k in range(3):
            yy = y0 + 20 + k * 30
            s.append(line([(x0 - 16, yy), (x0 - 40, yy - 6)], 5 * shake, INK, taper=.5, seed=715 + k))
            s.append(line([(x1 + 16, yy), (x1 + 40, yy - 6)], 5 * shake, INK, taper=.5, seed=718 + k))
    return "".join(s)


def _flakes():
    rs = np.random.RandomState(31)
    out = []
    for i in range(28):
        out.append(dict(vx=rs.uniform(-130, 250), vy=rs.uniform(20, 220), dl=rs.uniform(0, 0.22), c=["#e85a3c", "#f08a3c", "#c97b3a",
                                                                                                          "#f2c23a", "#a5502a"][i % 5],
                        rot=rs.uniform(0, 360), sp=rs.uniform(-300, 300), sz=rs.uniform(10, 15), sink=rs.uniform(70, 160),
                        ph=rs.uniform(0, 6), surf=WL + rs.uniform(2, 14)))
    return out


FL = _flakes()


def flake_pos(k, t):
    p = FL[k]
    e = t - TFOOD - p["dl"]
    if e < 0:
        return None
    x, y = CHUTE[0], CHUTE[1] - 6
    vx, vy = p["vx"], p["vy"]
    # полёт до воды
    g = 900.0
    # время касания воды: y + vy e + g e²/2 = surf
    a, b, c = g / 2, vy, y - p["surf"]
    te = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    if e < te:
        return x + vx * e, y + vy * e + g * e * e / 2, p["rot"] + p["sp"] * e
    x1, y1 = x + vx * te, p["surf"]
    e2 = e - te
    yy = y1 + p["sink"] * (1 - math.exp(-e2 * 2.6))
    xx = x1 + vx * 0.5 * (1 - math.exp(-e2 * 3)) + 8 * math.sin(e2 * 3 + p["ph"])
    return xx, yy, p["rot"] + p["sp"] * te + 40 * math.sin(e2 * 2 + p["ph"])


def flakes(t, bites):
    s = []
    for k in range(len(FL)):
        q = flake_pos(k, t)
        if q is None:
            continue
        gone = False
        for tb, mpos in bites:
            if t >= tb:
                qb = flake_pos(k, tb)
                if qb and math.dist(qb[:2], mpos) < 48:
                    gone = True
        if gone:
            continue
        x, y, r = q
        p = FL[k]
        z = p["sz"]
        pts = [(x - z, y - z * .4, 1), (x + z * .3, y - z * .6, 1), (x + z, y + z * .2, 1), (x - z * .2, y + z * .6, 1)]
        pts = lib.T(pts, 0, 0, 1, r, x, y)
        s.append(shape(pts, p["c"], "", w=2.6, seed=900 + k))
    return "".join(s)


def overlay(d):
    if d > 0.995:
        return ""
    return f'<rect x="-900" y="-1200" width="3000" height="4000" fill="#0f1733" opacity="{f(0.52 * (1 - d))}"/>'


def light():
    g = rad_grad([(0, "#fff0c8", .35), (1, "#fff0c8", 0)], 340, 340, 900, 900)
    s = [f'<rect x="-900" y="-1200" width="3000" height="4000" fill="url(#{g})" style="mix-blend-mode:screen"/>']
    g2 = rad_grad([(0, "#000000", 0), (.6, "#000000", 0), (1, "#2a1606", .36)], 560, 800, 1200, 1500)
    s.append(f'<rect x="-900" y="-1200" width="3000" height="4000" fill="url(#{g2})"/>')
    return "".join(s)


def layers(t, h, fish_svg, lever_a, lamp, shake=0.0, spin=0.0, ding=None, bites=()):
    s = [_ST["room"], window(h), clock(t, h, spin, ding), _ST["tank_back"]]
    lv, knob = lever(lever_a)
    fl = flakes(t, bites) if bites else ""
    s.append(f'<g clip-path="url(#{_ST["clip_tank"]})">' + weeds(t) + lv + fl + fish_svg + "</g>")
    s.append(_ST["tank_front"])
    s.append(feeder(t, lamp, shake))
    s.append(_ST["light"])
    s.append(overlay(daylight(h)))
    return "".join(s), knob


def lw_for(sc, cs, px=7.0):
    return px / (sc * cs)


# ─────────────────────────────── s09
def fish09(t):
    """Положение рыбки в s09: (x, y, rot, face, look, mouth_open, swim)."""
    contact = (743, 906)
    if t < 12.95:
        u = ease_io(clamp((t - 12.0) / 0.95))
        x = 330 + (contact[0] - 8 - 330) * u
        y = 1000 + (contact[1] - 6 - 1000) * u - 30 * math.sin(math.pi * u)
        return x, y, -6 * math.sin(math.pi * u), 1.0, (0.8, 0.1), None, 1.2
    if t < TPRESS + 0.18:
        u = clamp((t - 12.95) / (TPRESS + 0.18 - 12.95))
        k = ease_io(u)
        x = contact[0] - 8 + 18 * k
        y = contact[1] - 6 + 36 * k
        return x, y, 14 * k, 1.0, (0.8, 0.4), 0.0, 0.9
    if t < TFOOD:
        u = ease_io(clamp((t - TPRESS - 0.18) / 0.4))
        x = contact[0] + 10 - 60 * u
        y = contact[1] + 30 - 30 * u + 6 * math.sin(t * 3)
        return x, y, 14 - 32 * u, 1.0, (0.4 + 0.2 * u, -0.9 * u), None, 0.7
    u = ease_io(clamp((t - TFOOD) / 0.3))
    x = 693 - 4 * u + 4 * math.sin(t * 4)
    y = 936 - 62 * u
    m = 0.2
    for tb in (14.42, 14.62):
        e = t - tb
        if -0.1 < e < 0.12:
            m = max(m, 1 - abs(e) / 0.11 if e < 0 else 1 - e / 0.12)
    return x, y, -18 + 2 * u, 1.0, (0.6, -0.5), clamp(m), 1.0


def frame09(t):
    sc = 1.36 + 0.06 * ease_io(clamp((t - 12.0) / 2.75))
    cx, cy = 590 + 20 * clamp((t - 12.0) / 2.75), 880
    rot = -0.6 + 0.8 * clamp((t - 12.0) / 2.75)
    for tt, a in ((TPRESS, 0.05), (TFOOD, 0.035)):
        if t >= tt:
            e = t - tt
            sc *= 1 + a * math.exp(-e * 8) * min(1, e / 0.04)
            cy += 6 * a / 0.05 * math.exp(-e * 10) * math.sin(e * 45)
    x, y, r, face, look, mo, sw = fish09(t)
    # рычажок: нажат носом, потом пружиной назад
    if t < TPRESS:
        la = A_REST
    elif t < TPRESS + 0.18:
        la = A_REST + (A_PRESS - A_REST) * ease_out(clamp((t - TPRESS) / 0.12))
    else:
        e = t - TPRESS - 0.18
        la = A_PRESS + (A_REST - A_PRESS) * spring(e, 3.0, 7.0)
    lamp = smooth(TPRESS + 0.02, TPRESS + 0.1, t)
    shake = smooth(13.75, 13.85, t) * (1 - smooth(TFOOD, TFOOD + 0.06, t))
    bites = []
    for tb in (14.42, 14.62):
        xb, yb, rb, fb, _, _, _ = fish09(tb)
        bites.append((tb, fish.nose(xb, yb, FS, fb, rb)))
    fsvg = fish.draw(x, y, FS, t, face=face, rot=r, swim=sw, freq=2.0, look=look, mouth_open=mo, lw=lw_for(FS, sc),
                     brow=0.0)
    art, _ = layers(t, 8.0 + (t - 12.0) / 3600, fsvg, la, lamp, shake, bites=bites)
    if TPRESS <= t < TPRESS + 0.3:
        e = (t - TPRESS) / 0.3
        kx, ky = PIV[0] + ARM * math.cos(math.radians(A_PRESS)), PIV[1] + ARM * math.sin(math.radians(A_PRESS))
        for k in range(5):
            a = math.radians(200 + k * 35)
            r0 = 34 + 30 * ease_out(e)
            art += line([(kx + r0 * math.cos(a), ky + r0 * math.sin(a)), (kx + (r0 + 30 * (1 - e)) * math.cos(a),
                                                                          ky + (r0 + 30 * (1 - e)) * math.sin(a))], 7 * (1 - e) + 1.5,
                        INK, taper=.5, seed=960 + k)
    return art, cam(cx, cy, sc, rot)


# ─────────────────────────────── s10
def hour10(t):
    u = clamp((t - 14.35) / (TSTOP - 14.35))
    k = u * u * (3 - 2 * u)
    k = 0.15 * u + 0.85 * k
    h = 8.0 + 24.0 * k
    if t > TSTOP:
        e = t - TSTOP
        h = 32.0 + 0.035 * math.exp(-e * 9) * math.sin(e * 34)
    dh = 24.0 / (TSTOP - 14.35) * (0.15 + 0.85 * 6 * u * (1 - u)) if t < TSTOP else 0.0
    return h, dh


def frame10(t):
    h, dh = hour10(t)
    spin = dh * 360 / 30.0   # градусов минутной стрелки за кадр
    # камера: часы и окно, после остановки — вниз к рыбке
    k = ease_io(clamp((t - 15.86) / 0.5))
    sc = 1.72 + 0.08 * clamp((t - 14.35) / 1.3)
    cx = 650 + 10 * clamp((t - 14.35) / 1.3)
    cy = 440
    sc = sc + (1.66 - sc) * k
    cx = cx + (700 - cx) * k
    cy = cy + (880 - cy) * k
    rot = 0.8 - 0.8 * clamp((t - 14.35) / 2.3)
    if t >= TSTOP:
        e = t - TSTOP
        sc *= 1 + 0.05 * math.exp(-e * 8) * min(1, e / 0.04)
        cy += 6 * math.exp(-e * 10) * math.sin(e * 45)
    # рыбка ждёт у рычажка: нетерпеливо виляет, смотрит на рычажок
    fx = 700 + 6 * math.sin(t * 3.1)
    fy = 912 + 8 * math.sin(t * 4.3)
    look = (0.85, 0.15) if t < TSTOP else (0.5, -0.6) if t < 16.2 else (0.9, 0.2)
    fsvg = fish.draw(fx, fy, FS, t, face=1.0, rot=-4 + 4 * math.sin(t * 2), swim=1.0, freq=2.6, look=look, lw=lw_for(FS, sc),
                     mouth_open=0.25 + 0.25 * math.sin(t * 7))
    art, _ = layers(t, h, fsvg, A_REST, 0.0, spin=spin, ding=(t - TSTOP) if t >= TSTOP else None)
    return art, cam(cx, cy, sc, rot)


def frame(sid, t):
    if not _ST:
        _ST["room"] = room()
        _ST["tank_back"] = tank_back()
        _ST["tank_front"] = tank_front()
        _ST["light"] = light()
        lib.static_done()
    lib.dyn_begin()
    art, cm = (frame09 if sid == "s09" else frame10)(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#e5dcc0"/><g transform="{cm}">{art}</g>')


_unused = (H, ellipse_pts, rad_grad)
