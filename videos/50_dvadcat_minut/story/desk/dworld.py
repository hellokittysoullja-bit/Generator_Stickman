"""Кухонная стойка Димы для рилса 50 «это на 20 минут»: окно с сменой света день → золотой → ночь (u 0..1), ноутбук
(рисуется кодом, крышка открывается/закрывается, на экране таймер или документ), кружки, бумажки, пар.
Мир (px) — как в world.py рилса 29: пол от 1590, столешница 1210–1250, плитка 1000–1210, полка с банками (170–560, y 960).
Ноутбук стоит на столешнице, x 470–780; Дима слева (таз x 300), кот справа (x 930)."""
import math

import numpy as np

import lib
import world as Wd
from lib import INK, blob, ellipse_pts, line, mix, rect_pts, shape, T, clamp, smooth

WIN = (440, 900, 240, 820)
CLOCK_XY = (300, 330)
LAMP_X = 700
LX0, LX1 = 570, 840                      # основание ноутбука
HINGE = 1216                             # линия петли (задний край основания)
SCR = (LX0 + 22, LX1 - 22)               # рамка экрана по x
SCR_H = 190


def tcol(u, day, gold, night):
    if u < .5:
        return mix(day, gold, u / .5)
    return mix(gold, night, (u - .5) / .5)


def bell(u):
    return max(0.0, 1 - abs(u - .5) / .3)


def night_k(u):
    return smooth(.55, .95, u)


def wall(u):
    w = tcol(u, "#f1dfb9", "#efc48e", "#e7cfa3")
    s = [f'<rect x="-1400" y="-1400" width="4200" height="{Wd.FLOOR + 1400}" fill="{w}"/>']
    lib.DEFS.append('<pattern id="pTile50" width="96" height="72" patternUnits="userSpaceOnUse">'
                    f'<rect width="96" height="72" fill="{Wd.TILE}"/><rect x="0" y="68" width="96" height="4" fill="{Wd.TILE_L}"/>'
                    f'<rect x="92" width="4" height="72" fill="{Wd.TILE_L}"/></pattern>')
    s.append(f'<rect x="-1400" y="1000" width="4200" height="{Wd.CT_TOP - 1000}" fill="url(#pTile50)"/>')
    s.append(line([(-1400, 1000), (2800, 1000)], 4, INK, taper=.05, wmin=.9, seed=900))
    s.append(shape(rect_pts(-1400, -40, 2800, -10), mix(w, "#000000", .12), "", w=3.6, seed=901))
    return "".join(s)


def window(u, t=0.0):
    x0, x1, y0, y1 = WIN
    sky = lib.lin_grad([(0, tcol(u, "#8fc4ea", "#f0a05a", "#141c38"), 1), (1, tcol(u, "#dff0f6", "#fde2a8", "#2e4068"), 1)], 0, 0, 0, 1)
    inner = f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>'
    # солнце: день — высоко слева, золотой час — низко, ночью уходит; луна приходит
    sun_a = 1 - smooth(.55, .8, u)
    if sun_a > .01:
        sx = x0 + 120 + 110 * smooth(0, .6, u)
        sy = y0 + 150 + 230 * smooth(0, .7, u)
        col = tcol(min(u * 1.6, 1.0), "#fff3c4", "#ffc766", "#ffc766")
        r = 62 + 22 * smooth(.2, .6, u)
        inner += blob(ellipse_pts(sx, sy, r + 22, r + 22, 20), col, .28 * sun_a)
        inner += blob(ellipse_pts(sx, sy, r, r, 20), col, sun_a)
    for k, (cx, cy) in enumerate([(x0 + 300 - 40 * u, y0 + 130), (x0 + 380 - 30 * u, y0 + 250)]):
        inner += blob(ellipse_pts(cx, cy, 70, 24, 12), tcol(u, "#ffffff", "#ffe0b8", "#4a5782"), .9)
    nk = night_k(u)
    if nk > .01:
        inner += blob(ellipse_pts(x0 + 350, y0 + 140, 40, 40, 16), "#f3ead0", nk)
        for k, (x, y) in enumerate([(x0 + 80, y0 + 90), (x0 + 210, y0 + 210), (x0 + 120, y0 + 330), (x0 + 400, y0 + 300), (x0 + 300, y0 + 420)]):
            r = 4 + 1.2 * math.sin(t * 3 + k)
            inner += blob(ellipse_pts(x, y, r, r, 6), "#f3ead0", nk)
    roof = tcol(u, "#7f8fa8", "#8a6a62", "#121830")
    win_c = tcol(max(0.0, (u - .45) / .55), "#b9d3e6", "#f2c46a", "#f2c46a") if u > .45 else "#b9d3e6"
    inner += blob([(x0 - 20, y1 - 220), (x0 + 120, y1 - 250), (x0 + 120, y1 - 300), (x0 + 270, y1 - 300), (x0 + 270, y1 - 230),
                   (x1 + 20, y1 - 260), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)], roof)
    for k, (x, y) in enumerate([(x0 + 150, y1 - 260), (x0 + 200, y1 - 260), (x0 + 320, y1 - 190), (x0 + 400, y1 - 200), (x0 + 60, y1 - 150)]):
        inner += blob(rect_pts(x, y, x + 26, y + 34), win_c)
    fr = "#efe6d6"
    mx = (x0 + x1) / 2
    inner += blob(rect_pts(mx - 14, y0, mx + 14, y1), fr) + blob(rect_pts(x0, (y0 + y1) / 2 - 14, x1, (y0 + y1) / 2 + 14), fr)
    s = [shape(rect_pts(x0, y0, x1, y1, 10), fr, inner, w=5, seed=906)]
    s.append(shape(rect_pts(x0 - 30, y1 - 4, x1 + 30, y1 + 36, 6), fr, blob(rect_pts(x0 - 30, y1 + 22, x1 + 30, y1 + 36), "#d6ccbb"), w=4.4, seed=907))
    px = x1 - 90
    s.append(shape([(px - 40, y1 - 4, 1), (px + 40, y1 - 4, 1), (px + 30, y1 - 70, 1), (px - 30, y1 - 70, 1)], "#c4673f",
                   blob([(px + 6, y1 - 70), (px + 30, y1 - 70), (px + 40, y1 - 4), (px + 10, y1 - 4)], "#9c4c2c", .9), w=4, seed=908))
    sw = 3 * math.sin(t * 1.3)
    for k in range(5):
        a = -2.4 + k * 0.42
        s.append(line([(px, y1 - 70), (px + 80 * math.cos(a) + sw * (k - 2) * .4, y1 - 70 + 100 * math.sin(a))], 16, "#5f9a5a", taper=.6, seed=919 + k))
    return "".join(s)


def counter():
    s = []
    tp = [(-1400, Wd.CT_TOP, 1), (2400, Wd.CT_TOP, 1), (2400, Wd.CT_FR, 1), (-1400, Wd.CT_FR, 1)]
    inner = "".join(line([(-1400, Wd.CT_TOP + 12 + k * 12), (2400, Wd.CT_TOP + 14 + k * 12)], 2.2, Wd.WOOD_SH, taper=.1, wmin=.7, seed=1930 + k, op=.8)
                    for k in range(2))
    s.append(shape(tp, Wd.WOOD, inner, w=4.4, seed=910))
    s.append(shape(rect_pts(-1400, Wd.CT_FR, 2400, Wd.CT_FR + 26), Wd.WOOD_SH, "", w=4.4, seed=909))
    inner = ""
    for k, x in enumerate(range(-1360, 2400, 400)):
        inner += line([(x, Wd.CT_FR + 30), (x, Wd.FLOOR)], 4, mix(Wd.FRONT, "#000000", .3), taper=.05, wmin=.9, seed=920 + k)
        inner += shape(rect_pts(x + 170, Wd.CT_FR + 90, x + 230, Wd.CT_FR + 108, 8), "#b8b0a2", "", w=3, seed=930 + k)
    inner += blob(rect_pts(-1400, Wd.FLOOR - 40, 2400, Wd.FLOOR), Wd.FRONT_SH, .9)
    s.append(shape(rect_pts(-1400, Wd.CT_FR + 26, 2400, Wd.FLOOR), Wd.FRONT, inner, w=5, seed=940))
    return "".join(s)


def floor(u):
    col = "#b98d5f"
    inner = "".join(line([(-1400, Wd.FLOOR + 60 + k * 90 + k * k * 8), (2800, Wd.FLOOR + 60 + k * 90 + k * k * 8)], 3, mix(col, "#000000", .25),
                         taper=.05, wmin=.9, seed=1500 + k, op=.8) for k in range(8))
    inner += blob(rect_pts(-1400, Wd.FLOOR, 2800, Wd.FLOOR + 40), "#000000", .12)
    return shape(rect_pts(-1400, Wd.FLOOR, 2800, 3600), col, inner, w=4.6, seed=1501)


# ─────────────────────────────── мелочи на столешнице
def paper_ball(x, y, k=1.0, seed=0):
    rs = np.random.RandomState(seed)
    pts = []
    for i in range(11):
        a = i / 11 * 2 * math.pi
        r = 26 * k * (1 + .22 * rs.uniform(-1, 1))
        pts.append((x + r * math.cos(a), y - 24 * k + r * .92 * math.sin(a)))
    inner = blob([(x + 8 * k, y - 50 * k), (x + 30 * k, y - 22 * k), (x + 14 * k, y + 2 * k), (x - 4 * k, y - 20 * k)], "#ddd5c4", .9)
    inner += line([(x - 20 * k, y - 30 * k), (x - 2 * k, y - 18 * k), (x + 14 * k, y - 34 * k)], 2.2, "#8a8374", seed=seed + 1, op=.9)
    inner += line([(x - 10 * k, y - 8 * k), (x + 8 * k, y - 14 * k)], 2.2, "#8a8374", seed=seed + 2, op=.9)
    return shape(pts, "#f6f1e6", inner, w=3.4, seed=seed + 3)


def sheet(x, y, k=1.0, rot=0.0, seed=0):
    pts = T([(-70, 0), (70, -5), (86, 14), (-56, 19)], x, y, k, rot)
    ln = "".join(line(T([(-52 + 4 * j, 5 + j * 0.0), (50 + 4 * j, 2)], x, y, k, rot)[:2], 2, "#9a9284", seed=seed + j) for j in range(1))
    return shape(pts, "#fbf8f0", ln, w=3.2, seed=seed + 7)


def steam(x, y, t, k=1.0):
    o = []
    for j in range(3):
        ph = (t * .7 + j / 3) % 1
        px = x + (j - 1) * 20 * k + 10 * math.sin(ph * 6 + j)
        py = y - 150 * k - 90 * ph
        pts = [(px - 6 * math.sin(ph * 5 + j), py + 60), (px + 8 * math.sin(ph * 5 + j + 1), py + 30), (px, py)]
        o.append(line(pts, 5 * k, "#ffffff", taper=.8, wmin=.1, seed=2200 + j, op=.6 * math.sin(math.pi * ph)))
    return "".join(o)


# ─────────────────────────────── ноутбук
def _txt(x, y, s, size, fill="#ffffff", weight=400, anchor="middle", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {extra}>{s}</text>')


def screen_timer(t, pill_pop=0.0, press=0.0, label="20 мин", digits="20:00", btn="СТАРТ", ring=1.0, mode="timer"):
    """Содержимое экрана (мир): приложение-таймер. Область 250×162 в x 580..830, y 1040..1202 (центр 705, 1121)."""
    cx, cy = 705, 1118
    o = [f'<rect x="570" y="1030" width="270" height="180" fill="#1d2744"/>']
    o.append(_txt(705, 1062, "ТАЙМЕР", 13, "#8fa0c8", 700))
    o.append(f'<circle cx="{cx}" cy="{cy}" r="52" fill="none" stroke="#33426b" stroke-width="9"/>')
    circ = 2 * math.pi * 52
    o.append(f'<circle cx="{cx}" cy="{cy}" r="52" fill="none" stroke="{"#7fd28a" if press < .5 else "#ffd166"}" stroke-width="9" stroke-linecap="round" '
             f'stroke-dasharray="{circ * ring:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>')
    sc = 1 + .08 * press
    o.append(f'<g transform="translate({cx} {cy + 12}) scale({sc:.3f}) translate({-cx} {-(cy + 12)})">{_txt(cx, cy + 12, digits, 33, "#ffffff", 700)}</g>')
    k = 1 + .35 * pill_pop
    px, py = 705, 1186
    o.append(f'<g transform="translate({px} {py}) scale({k:.3f}) translate({-px} {-py})">'
             f'<rect x="{px - 38}" y="{py - 13}" width="76" height="26" rx="13" fill="#ffd166"/>{_txt(px, py + 6, label, 15, "#2a2740", 700)}</g>')
    o.append(_txt(610, 1196, btn, 11, "#7fd28a" if press < .5 else "#ffd166", 700, "middle"))
    return "".join(o)


def screen_doc(t, lines=6.0, chip="20:00", chip_col="#7fd28a", scroll=0.0):
    """Экран-документ: серые строки текста растут по мере печати; фишка таймера в углу."""
    o = [f'<rect x="570" y="1030" width="270" height="180" fill="#e9eef7"/>']
    o.append(f'<rect x="570" y="1030" width="270" height="16" fill="#c7d0e2"/>')
    for i, c in enumerate(("#e0605a", "#e9b44a", "#5fb86b")):
        o.append(f'<circle cx="{580 + i * 12}" cy="1038" r="3.4" fill="{c}"/>')
    o.append(f'<rect x="588" y="1054" width="170" height="10" rx="3" fill="#2f3b5c"/>')
    n = int(lines)
    frac = lines - n
    for i in range(n + 1):
        y = 1078 + i * 16 - scroll
        if y < 1052 or y > 1196:
            continue
        w = 214 if i % 4 != 3 else 120
        if i == n:
            w = w * frac
        if w < 4:
            continue
        o.append(f'<rect x="588" y="{y:.1f}" width="{w:.1f}" height="7" rx="3" fill="#9aa6c0"/>')
    if int(t * 2.2) % 2 == 0:
        yy = 1078 + n * 16 - scroll
        if 1052 < yy < 1196:
            o.append(f'<rect x="{588 + (214 if n % 4 != 3 else 120) * frac + 3:.1f}" y="{yy - 3:.1f}" width="3" height="13" fill="#2f3b5c"/>')
    o.append(f'<rect x="768" y="1050" width="66" height="22" rx="11" fill="#1d2744"/>')
    o.append(_txt(801, 1066, chip, 13, chip_col, 700))
    return "".join(o)


def laptop(open_=1.0, screen="", glow=0.0):
    """open_ 0..1: крышка (сжимается по y вокруг петли). Основание — вид чуть сверху, клавиши видны."""
    body_col, body_sh = "#cfd4dc", "#a3aab6"
    top = [(LX0 + 24, HINGE - 2), (LX1 - 24, HINGE - 2), (LX1 + 2, HINGE + 18), (LX0 - 2, HINGE + 18)]
    keys = ""
    for r in range(3):
        for c in range(13):
            kx0 = LX0 + 34 + c * 20 - r * 3
            ky0 = HINGE + 2 + r * 5.5
            keys += blob(rect_pts(kx0, ky0, kx0 + 15, ky0 + 3.6, 1.4), "#7b8494")
    keys += blob(rect_pts(LX0 + 130, HINGE + 12, LX0 + 190, HINGE + 15, 1.4), "#7b8494")
    base = shape(top, body_col, keys, w=3.6, seed=3500)
    front = shape([(LX0 - 2, HINGE + 18, 1), (LX1 + 2, HINGE + 18, 1), (LX1 + 4, HINGE + 28), (LX0 - 4, HINGE + 28)], body_sh, "", w=3.8, seed=3501)
    o = [blob(ellipse_pts((LX0 + LX1) / 2 + 6, HINGE + 36, 140, 8, 14), "#000000", .2)]
    if open_ > .02:
        k = open_
        x0, x1 = SCR
        lid = rect_pts(x0, HINGE - SCR_H, x1, HINGE, 10)
        cid = lib.clip_rect(x0 + 10, HINGE - SCR_H + 10, x1 - x0 - 20, SCR_H - 12, 4)
        inner = f'<g clip-path="url(#{cid})">{screen}</g>'
        if glow > 0:
            inner += blob(rect_pts(x0, HINGE - SCR_H, x1, HINGE), "#ffffff", .0)
        lidsvg = shape(lid, "#2b2f3a", inner, w=4.4, seed=3502)
        # шарнир внизу крышки, чуть выступает
        o.append(f'<g transform="translate(0 {HINGE}) scale(1 {k:.4f}) translate(0 {-HINGE})">{lidsvg}</g>')
    o.append(base)
    o.append(front)
    if open_ <= .02:
        o.append(shape([(LX0 + 10, HINGE - 10), (LX1 - 10, HINGE - 10), (LX1 + 2, HINGE + 2), (LX0 - 2, HINGE + 2)], "#d9dde4", "", w=3.6, seed=3503))
    return "".join(o)


# ─────────────────────────────── свет
def overlay(u, lamp_on=True):
    o = []
    gk = bell(u)
    if gk > .01:
        g = lib.rad_grad([(0, "#ffd890", .5), (.6, "#ffb860", .2), (1, "#ffb860", 0)], 640, 700, 1100, 1000)
        o.append(f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" opacity="{gk:.3f}" style="mix-blend-mode:screen"/>')
        o.append(f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="#ff9d4d" opacity="{.22 * gk:.3f}" style="mix-blend-mode:multiply"/>')
    nk = night_k(u)
    if nk > .01:
        g = lib.rad_grad([(0, "#ffd890", .5), (.5, "#ffbe6a", .2), (1, "#ffbe6a", 0)], LAMP_X, 360, 1200, 1100)
        g2 = lib.rad_grad([(0, "#000000", 0), (.55, "#000000", 0), (1, "#1a1030", .5)], LAMP_X, 800, 1500, 1500)
        o.append(f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="#3b4278" opacity="{.5 * nk:.3f}" style="mix-blend-mode:multiply"/>')
        o.append(f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" opacity="{nk:.3f}" style="mix-blend-mode:screen"/>')
        o.append(f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g2})" opacity="{nk:.3f}"/>')
    return "".join(o)


def room(t, u, clock=(14, 0), mugs=(), balls=(), sheets=(), steam_at=None):
    Wd.LAMP = (LAMP_X, 0)
    o = [wall(u), window(u, t), Wd.clock_wall(clock[0], clock[1], "night" if u > .6 else "day", 1.0, *CLOCK_XY), counter(), floor(u),
         Wd.shelf(0.0, 1.0, (0, 0)), Wd.lamp("night" if u > .6 else "dark", t, 0.0)]
    for (x, col, ph) in mugs:
        o.append(Wd.mug(x, 1236, .55, 0, col=col))
    for (x, sd) in balls:
        o.append(paper_ball(x, 1232, .8, sd))
    for (x, rot, sd) in sheets:
        o.append(sheet(x, 1222, .9, rot, sd))
    if steam_at is not None:
        o.append(steam(steam_at, 1236 - 70, t, .8))
    return "".join(o)
