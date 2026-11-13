"""Сцена note рилса 26.
s14: вечер, крупно жёлтый стикер на блоке у кухонной стойки. Рука Димы (горчичный рукав, хват из рилса 24/25) пишет
рукописью «в понедельник / после кофе / надеваю кроссовки» — буквы проявляются по ходу пера (скелеты Caveat 600,
glyphs.json). Дописал — рука уходит, камера хлёстом уезжает к кофеварке, ладонь шлёпает стикер на её панель на
«кроссовки» (27.24).
s15: утро, та же кухня в солнце: кофе льётся в кружку, на «кофе» (28.56) кружка полна и парит рядом со стикером; на
«кроссовки» (29.15) рука сверху выхватывает кроссовки из коробки на стойке."""
import json
import math
import os

import numpy as np

import hand
import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg, T)
from parts import sausage
from scene_box import sneaker, tag

G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphs.json")))
_ST = {}
INKC = "#26356f"
# стикер на блоке (мир s14)
NX0, NY0, NS = 170, 400, 760
FS = 106
SC = FS / G["upm"]
TX0 = NX0 + 60
BASES = [NY0 + 230, NY0 + 410, NY0 + 590]
SLOTS = [(25.30, 25.83), (25.90, 26.31), (26.38, 27.10)]
SLAP = 27.24
# кухня: стойка, кофеварка, коробка
CTR = 1180
MX0, MX1, MTOP = 1560, 2160, 360
STK = (1735, 560)       # центр стикера на кофеварке
STK_S = 0.36
SPOUT = (1905, 830)
MUG = (1905, CTR - 6)
BOX = (2320, 2860)
SKIN, SKIN_SH, SKIN_SH2, NAIL = hand.SKIN, hand.SKIN_SH, hand.SKIN_SH2, hand.NAIL
HOOD, HOOD_SH, FOLD = hand.HOOD, hand.HOOD_SH, hand.FOLD


# ─────────────────────────────── письмо (как scene_list рилса 25)
def build_lines():
    out = []
    for li in range(3):
        gl = G["lines"][li]
        x = TX0
        base = BASES[li]
        path, gls = [], []
        for gi, g in enumerate(gl):
            gls.append(dict(g=g, x=x))
            for st in g.get("strokes", []):
                for k, (px, py) in enumerate(st):
                    path.append((x + px * SC, base - py * SC, gi, k > 0))
            x += g["adv"] * SC
        P = np.array([(p[0], p[1]) for p in path])
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        down = np.array([p[3] for p in path[1:]])
        cum = np.concatenate([[0], np.cumsum(np.where(down, seg, seg * 0.4))])
        out.append(dict(path=path, P=P, cum=cum / cum[-1], gls=gls, base=base, x1=x))
    return out


L = build_lines()


def progress(li, t):
    a, b = SLOTS[li]
    u = clamp((t - a) / (b - a))
    return u * 0.85 + 0.15 * (u * u * (3 - 2 * u))


def tip_at(li, p):
    ln = L[li]
    i = int(np.searchsorted(ln["cum"], p, side="right")) - 1
    i = max(0, min(i, len(ln["P"]) - 2))
    c0, c1 = ln["cum"][i], ln["cum"][i + 1]
    q = 0 if c1 <= c0 else (p - c0) / (c1 - c0)
    x, y = ln["P"][i] + (ln["P"][i + 1] - ln["P"][i]) * q
    lift = 0.0 if ln["path"][i + 1][3] else math.sin(math.pi * q)
    return x, y, i, lift


def text_line(li, t, done=False):
    ln = L[li]
    a, b = SLOTS[li]
    if t <= a and not done:
        return ""
    p = 1.0 if done else progress(li, t)
    s = []
    if p >= 1:
        cur, i_now = len(ln["gls"]), len(ln["P"]) - 1
    else:
        _, _, i_now, _ = tip_at(li, p)
        cur = ln["path"][i_now][2]
    for gi, o in enumerate(ln["gls"]):
        g = o["g"]
        if not g["bounds"] or gi > cur:
            continue
        body = f'<path d="{g["d"]}" transform="translate({f(o["x"])} {ln["base"]}) scale({SC:.5f} {-SC:.5f})" fill="{INKC}"/>'
        if gi == cur and p < 1:
            pts = [(x, y, d) for (x, y, gg, d) in ln["path"][:i_now + 1] if gg == gi]
            tx, ty, _, _ = tip_at(li, p)
            pts.append((tx, ty, True))
            d = ""
            for k, (x, y, dn) in enumerate(pts):
                d += ("L" if (dn and k > 0) else "M") + f"{f(x)} {f(y)}"
            wpx = g["width"] * SC * 1.25
            mid = lib.uid("m")
            DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-600" y="-600" width="3400" height="3200">'
                        f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{f(wpx)}" stroke-linecap="round" stroke-linejoin="round"/></mask>')
            body = f'<g mask="url(#{mid})">{body}</g>'
        s.append(body)
    return "".join(s)


def pen_tip(t):
    a0 = SLOTS[0][0]
    if t < a0:
        u = ease_out(clamp((t - 25.04) / (a0 - 25.04)), 2.0)
        sx, sy = 860, 1280
        ex, ey = tip_at(0, 0)[:2]
        return sx + (ex - sx) * u, sy + (ey - sy) * u - 40 * math.sin(math.pi * u), 1.0 + 0.06 * (1 - u)
    for li, (a, b) in enumerate(SLOTS):
        if a <= t <= b:
            x, y, _, lift = tip_at(li, progress(li, t))
            return x, y, 1.0 + 0.03 * lift
        if li + 1 < len(SLOTS) and b < t < SLOTS[li + 1][0]:
            u = ease_io((t - b) / (SLOTS[li + 1][0] - b))
            sx, sy = tip_at(li, 1.0)[:2]
            ex, ey = tip_at(li + 1, 0.0)[:2]
            return sx + (ex - sx) * u, sy + (ey - sy) * u - 50 * math.sin(math.pi * u), 1.0 + 0.07 * math.sin(math.pi * u)
    e = t - SLOTS[-1][1]
    u = ease_in(clamp(e / 0.16), 1.5)
    sx, sy = tip_at(2, 1.0)[:2]
    return sx + 300 * u, sy + 700 * u, 1.0 + 0.07 * u


# ─────────────────────────────── стикер
def sticker(t, done, curl=0.0, sd=0):
    """Стикер в своих координатах (центр в 0,0, сторона NS): бумага, тень у клеевой полосы, текст."""
    h = NS / 2
    inner = blob([(-h, -h, 1), (h, -h, 1), (h, -h + 70, 1), (-h, -h + 70, 1)], "#f6d24e", .8)
    inner += blob([(-h, h - 60, 1), (h, h - 70, 1), (h, h, 1), (-h, h, 1)], "#f2c84a", .7)
    txt = "".join(text_line(i, t, done) for i in range(3))
    txt = f'<g transform="translate({-NX0 - h} {-NY0 - h})">{txt}</g>'
    pts = [(-h, -h, 1), (h, -h, 1), (h, h - 70 * curl), (h - 60 * curl, h, 1), (-h, h, 1)]
    body = shape(pts, "#ffe066", inner + txt, w=5, seed=800 + sd)
    if curl > 0.02:
        body += shape([(h, h - 70 * curl, 1), (h - 60 * curl, h, 1), (h - 74 * curl, h - 84 * curl, 1)], "#e8bf3c", "", w=3.6, seed=810 + sd)
    return body


def pad():
    """Блок стикеров под верхним листом: стопка жёлтых краёв, тень."""
    s = []
    h = NS / 2
    cx, cy = NX0 + h, NY0 + h
    s.append(blob(rect_pts(cx - h + 20, cy - h + 30, cx + h + 34, cy + h + 54), "#1a0e05", .45, blur(16)))
    s.append(shape(rect_pts(cx - h + 4, cy - h + 8, cx + h + 10, cy + h + 26), "#e8bf3c",
                   "".join(line([(cx - h, cy + h + 6 + k * 5), (cx + h + 12, cy + h + 4 + k * 5)], 2, "#c99f2a", seed=820 + k) for k in range(4)),
                   w=4.4, seed=825))
    return "".join(s)


# ─────────────────────────────── кухня
def kitchen(night):
    s = []
    wall = "#3c4a63" if night else "#f1e2c4"
    tile, tile_l = ("#33405a", "#46557a") if night else ("#e4d1ad", "#fbf1dc")
    s.append(f'<rect x="-1500" y="-1500" width="5600" height="{CTR + 1500}" fill="{wall}"/>')
    DEFS.append(f'<pattern id="pTile{int(night)}" width="110" height="80" patternUnits="userSpaceOnUse">'
                f'<rect width="110" height="80" fill="{tile_l}"/><rect x="0" y="76" width="110" height="4" fill="{tile}"/>'
                f'<rect x="106" width="4" height="80" fill="{tile}"/></pattern>')
    s.append(f'<rect x="-1500" y="220" width="5600" height="{CTR - 220}" fill="url(#pTile{int(night)})"/>')
    s.append(line([(-1500, 220), (4100, 220)], 4, INK, taper=.05, wmin=.9, seed=900))
    # окно с утренним/ночным небом над стойкой слева от кофеварки
    sky = lin_grad([(0, "#13203d" if night else "#8fd0f5", 1), (1, "#2c3d66" if night else "#e8f6ff", 1)], 0, 0, 0, 1)
    win = rect_pts(1000, -420, 1440, 160, 12)
    inner = f'<rect x="980" y="-440" width="480" height="620" fill="url(#{sky})"/>'
    if night:
        inner += blob(ellipse_pts(1340, -300, 34, 34, 14), "#f3ead0")
        for k, (x, y) in enumerate([(1080, -330), (1200, -240), (1120, -120), (1380, -60)]):
            inner += blob(ellipse_pts(x, y, 4, 4, 6), "#f3ead0")
    else:
        inner += blob(ellipse_pts(1120, -270, 60, 60, 16), "#fff4c6")
        inner += shape(ellipse_pts(1300, -140, 90, 40, 12, jitter=.1, seed=3), "#ffffff", "", w=3, seed=905)
    inner += blob(rect_pts(1210, -420, 1230, 160), "#d9d2c4") + blob(rect_pts(1000, -150, 1440, -130), "#d9d2c4")
    s.append(shape(win, "#e9e1d2", inner, w=5, seed=906))
    s.append(shape(rect_pts(980, 150, 1460, 190, 6), "#e9e1d2", "", w=4.4, seed=907))
    # полка с банками и цветком
    s.append(shape(rect_pts(1500, 120, 3300, 150, 4), "#b98a5a" if not night else "#6b4a30", "", w=4.4, seed=911))
    for k, (x, hgt, col) in enumerate([(2300, 120, "#e9c46a"), (2420, 90, "#9fc5a8"), (2520, 140, "#e07a5f"), (1620, 100, "#8ab6d6")]):
        if night:
            col = mix(col, "#2a3550", .55)
        s.append(shape(rect_pts(x - 40, 120 - hgt, x + 40, 120, 14), col, blob(rect_pts(x - 40, 120 - hgt, x + 40, 120 - hgt + 24), "#c9c0b0"),
                       w=4, seed=912 + k))
    pc = "#c4673f" if not night else "#6a3e2c"
    s.append(shape([(2830, 120, 1), (2950, 120, 1), (2970, 40, 1), (2810, 40, 1)], pc, "", w=4, seed=918))
    for k in range(5):
        a = -2.2 + k * 0.55
        s.append(line([(2890, 40), (2890 + 90 * math.cos(a), 40 + 110 * math.sin(a))], 18, "#5f9a5a" if not night else "#2e4a3a", taper=.6, seed=919 + k))
    # стойка
    top = "#c98f5a" if not night else "#7a5232"
    s.append(shape(rect_pts(-1500, CTR - 40, 4100, CTR + 30), top, blob(rect_pts(-1500, CTR + 6, 4100, CTR + 30), mix(top, "#000000", .25)),
                   w=5, seed=910))
    front = "#e9dcc4" if not night else "#4b5670"
    inner = "".join(line([(x, CTR + 34), (x, 3000)], 4, mix(front, "#000000", .3), taper=.05, wmin=.9, seed=920 + k)
                    for k, x in enumerate(range(-1400, 4100, 520)))
    inner += "".join(shape(rect_pts(x + 230, CTR + 120, x + 290, CTR + 140, 8), "#b8b0a2", "", w=3, seed=930 + k)
                     for k, x in enumerate(range(-1400, 4100, 520)))
    s.append(shape(rect_pts(-1500, CTR + 30, 4100, 3000), front, inner, w=5, seed=940))
    # свет
    if night:
        g = rad_grad([(0, "#ffd08a", .5), (.6, "#ffb860", .15), (1, "#ffb860", 0)], 1300, 500, 1300, 1100)
    else:
        g = rad_grad([(0, "#fff1c0", .55), (.6, "#ffe2a0", .2), (1, "#ffe2a0", 0)], 1150, -100, 1700, 1500)
    s.append(f'<rect x="-1500" y="-1500" width="5600" height="4500" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    if not night:
        # косые солнечные полосы от окна
        g2 = lin_grad([(0, "#fff3c8", .45), (1, "#fff3c8", 0)], 0, 0, 1, 1)
        s.append(f'<path d="M1000 160 L1440 160 L2300 {CTR - 40} L1560 {CTR - 40}Z" fill="url(#{g2})" style="mix-blend-mode:screen"/>')
    # кофеварка
    s.append(machine(night))
    return "".join(s)


def machine(night):
    s = []
    body, body_sh = ("#c9473d", "#9c3029") if not night else ("#8e3a36", "#6a2826")
    s.append(blob(rect_pts(MX0 + 30, CTR - 60, MX1 + 60, CTR - 20), "#1a0e05", .5, blur(14)))
    inner = blob(rect_pts(MX1 - 90, MTOP, MX1 + 10, CTR), body_sh, .9)
    inner += blob(rect_pts(MX0, MTOP, MX1, MTOP + 30), mix(body, "#ffffff", .25), .9)
    s.append(shape(rect_pts(MX0, MTOP, MX1, CTR - 40, 46), body, inner, w=5.4, seed=950))
    # ниша
    s.append(shape(rect_pts(MX0 + 70, 780, MX1 - 70, CTR - 80, 24), "#2b2730", blob(rect_pts(MX0 + 70, 780, MX1 - 70, 840), "#1c1920"),
                   w=4.6, seed=951))
    # поддон
    s.append(shape(rect_pts(MX0 + 50, CTR - 110, MX1 - 50, CTR - 50, 10), "#9aa0ab",
                   "".join(line([(x, CTR - 104), (x, CTR - 58)], 3, "#6d737e", taper=.05, wmin=.9, seed=960 + k) for k, x in
                           enumerate(range(MX0 + 90, MX1 - 60, 36))), w=4.4, seed=961))
    # группа и носик
    s.append(shape(rect_pts(SPOUT[0] - 90, 780, SPOUT[0] + 90, 812, 8), "#b9bec8", "", w=4, seed=962))
    s.append(shape([(SPOUT[0] - 30, 812, 1), (SPOUT[0] + 30, 812, 1), (SPOUT[0] + 14, SPOUT[1], 1), (SPOUT[0] - 14, SPOUT[1], 1)], "#9aa0ab", "",
                   w=3.6, seed=963))
    # кнопки справа и лампочка
    for k in range(3):
        y = 470 + k * 82
        s.append(shape(ellipse_pts(2040, y, 30, 30, 14), "#f1ece3", blob(ellipse_pts(2046, y + 6, 22, 20, 10), "#d4ccbf"), w=3.6, seed=970 + k))
    return "".join(s)


def lamp(t, night):
    on = 0.5 + 0.5 * math.sin(t * 5)
    col = mix("#2e6b3a", "#7dff9a", on) if night else "#7dff9a"
    return shape(ellipse_pts(2040, 715, 11, 11, 10), col, "", w=2.6, seed=980)


def mug(fill, t):
    x, y = MUG
    s = [blob(ellipse_pts(x + 10, y - 2, 120, 18, 14), "#1a0e05", .4, blur(6))]
    s.append(line([(x + 92, y - 170), (x + 150, y - 160), (x + 156, y - 90), (x + 96, y - 60)], 22, INK, taper=.05, wmin=.9, seed=990))
    s.append(line([(x + 92, y - 170), (x + 150, y - 160), (x + 156, y - 90), (x + 96, y - 60)], 13, "#3f9aa8", taper=.05, wmin=.9, seed=991))
    inner = blob(rect_pts(x + 40, y - 220, x + 110, y), "#2f7c88", .9)
    inner += blob(rect_pts(x - 70, y - 210, x - 50, y - 30), "#7cc9d4", .9)
    s.append(shape([(x - 100, y - 230, 1), (x + 100, y - 230, 1), (x + 92, y - 12), (x + 80, y, 1), (x - 80, y, 1), (x - 92, y - 12)],
                   "#3f9aa8", inner, w=5, seed=992))
    # кофе сверху (вид чуть сверху): тёмный эллипс с пенкой
    top = ellipse_pts(x, y - 230, 100, 20, 18)
    lvl = clamp(fill)
    inner = blob(ellipse_pts(x, y - 230 + 18 * (1 - lvl), 92 * (0.6 + 0.4 * lvl), 15, 16), "#5a3218" if lvl > 0.02 else "#1f3a40")
    if lvl > 0.5:
        inner += blob(ellipse_pts(x - 10, y - 232, 60 * lvl, 9, 12), "#b9875a", .9)
    s.append(shape(top, "#1f3a40", inner, w=4, seed=993))
    return "".join(s)


def pour(t):
    """Струйка из носика в кружку: 28.0–28.5."""
    a, b = 27.95, 28.5
    if t < a or t > b + 0.12:
        return ""
    top = SPOUT[1]
    bot = MUG[1] - 232
    u0 = clamp((t - a) / 0.1)
    u1 = clamp((t - b) / 0.12)
    y0 = top + (bot - top) * u1
    y1 = top + (bot - top) * u0
    if y1 - y0 < 4:
        return ""
    wob = 2 * math.sin(t * 40)
    return line([(SPOUT[0] + wob, y0), (SPOUT[0] - wob, (y0 + y1) / 2), (SPOUT[0], y1)], 12, "#5a3218", taper=.15, wmin=.7, seed=995)


def steam(t, k0):
    """Пар над кружкой: три волнистые струйки, текут вверх; появляются к «кофе»."""
    if t < 28.4:
        return ""
    a = clamp((t - 28.4) / 0.3)
    s = []
    for k in range(3):
        x0 = MUG[0] - 45 + k * 45
        ph = t * 3.2 + k * 2.1
        pts = []
        n = 7
        for j in range(n):
            v = j / (n - 1)
            pts.append((x0 + 22 * math.sin(ph - v * 5) * (0.4 + v), MUG[1] - 260 - 230 * v * a - 10 * k))
        s.append(line(pts, 11 * a, "#ffffff", taper=.8, wmin=.15, seed=k0 + k, peak=.35))
    return "".join(s)


def press_hand(x, y, sc, rot, squash=0.0):
    """Ладонь тыльной стороной к нам, пальцы вверх: прижимает стикер (правая рука, большой палец слева). Рукав снизу."""
    s = []
    P = lambda pts: T(pts, x, y, sc, rot)
    # рукав
    s.append(shape(P([(-120, 170, 1), (110, 160, 1), (190, 700, 1), (-170, 720, 1)]), HOOD,
                   blob(P([(40, 170), (110, 160), (190, 700), (60, 700)]), HOOD_SH, .9) +
                   line(P([(-60, 260), (-20, 420), (-40, 600)]), 4, FOLD, seed=1010, op=.7), w=5.2, seed=1011))
    s.append(shape(P([(-126, 140, 1), (114, 128, 1), (122, 196, 1), (-120, 206, 1)]), HOOD_SH,
                   "".join(line(P([(-100 + k * 40, 146), (-100 + k * 40, 200)]), 2.6, FOLD, seed=1020 + k, op=.8) for k in range(6)),
                   w=4.6, seed=1012))
    # большой палец слева
    th = sausage(P([(-70, 70), (-120, 20), (-150, -40)]), 54 * sc, 44 * sc)
    s.append(shape(th, SKIN, "", w=4.4, seed=1030))
    tx, ty = P([(-150, -40)])[0]
    s.append(shape(ellipse_pts(tx + 2, ty + 8, 14 * sc, 11 * sc, 10, rot=-50 + rot), NAIL, "", w=2.2, seed=1031))
    # пальцы
    fl = 1 - 0.12 * squash
    fingers = [(-64, 132, 44), (-21, 150, 46), (22, 140, 44), (62, 108, 38)]
    for k, (fx, L_, w_) in enumerate(fingers):
        tip = (fx + (k - 1.5) * 6, -L_ * fl)
        sp = sausage(P([(fx, 30), (fx + (k - 1.5) * 3, -L_ * fl * 0.5), tip]), w_ * sc, w_ * 0.9 * sc)
        inner = line(P([(fx - w_ * .3, -L_ * fl * 0.45), (fx + w_ * .3, -L_ * fl * 0.45)]), 2.4, SKIN_SH2, seed=1040 + k, op=.8)
        inner += line(P([(fx - w_ * .25, -L_ * fl * 0.78), (fx + w_ * .25, -L_ * fl * 0.78)]), 2.2, SKIN_SH2, seed=1050 + k, op=.7)
        s.append(shape(sp, SKIN, inner, w=4.2, seed=1060 + k))
        nx, ny = P([(tip[0], tip[1] + w_ * 0.42)])[0]
        s.append(shape(ellipse_pts(nx, ny, w_ * 0.3 * sc, w_ * 0.36 * sc, 10, rot=rot), NAIL, "", w=2, seed=1070 + k))
    # тыльная сторона ладони
    back = [(-92, 6), (-40, -8), (20, -10), (86, 2), (100, 56), (86, 150), (0, 162), (-90, 156), (-104, 70)]
    inner = blob(P([(40, 0), (96, 60), (90, 150), (30, 154)]), SKIN_SH, .9)
    for k in range(4):
        fx = fingers[k][0]
        inner += line(P([(fx - 10, 6), (fx, -2), (fx + 10, 6)]), 2.6, SKIN_SH2, seed=1080 + k, op=.8)
    inner += line(P([(-30, 40), (-20, 120)]), 2.4, SKIN_SH2, seed=1090, op=.6)
    inner += line(P([(20, 40), (14, 120)]), 2.4, SKIN_SH2, seed=1091, op=.6)
    s.append(shape(P(back), SKIN, inner, w=5, seed=1092))
    return "".join(s)


# ─────────────────────────────── s14
def frame14(t):
    s = []
    # фаза письма: стол-стойка ночью крупно, блок стикеров; после хлёста — кофеварка
    whip0, whip1 = 27.12, 27.22
    pan = ease_io(clamp((t - whip0) / (whip1 - whip0)))
    # мир: блок стикеров стоит на стойке слева от кофеварки — по x 170..930 при y 400..1160 (вид сверху на стол)
    # Для простоты — две «комнаты»: стол (сверху) и кофеварка (спереди), склеенные хлёстом.
    if t < (whip0 + whip1) / 2:
        s.append(_ST["desk"])
        s.append(pad())
        h = NS / 2
        lift = 0.0
        s.append(f'<g transform="translate({NX0 + h} {NY0 + h - lift})">{sticker(t, False, 0.25 + 0.05 * math.sin(t * 3))}</g>')
        x, y, lft = pen_tip(t)
        ang = -36 + 3 * math.sin(t * 2.3) - 4 * (lft - 1)
        s.append(f'<g transform="translate({f(x + 26 * lft)} {f(y + 34 * lft)}) scale(1.15)" opacity=".28" filter="url(#fShH)">{hand.hand(ang, 7)}</g>')
        s.append(f'<g transform="translate({f(x)} {f(y)}) scale({f(1.15 * lft)})">{hand.hand(ang, 7)}</g>')
        u = clamp((t - 25.04) / 2.1)
        cx = 560 + 40 * ease_io(u) + 220 * pan
        cy = 760 + 70 * ease_io(u) - 40 * pan
        sc = 1.22 + 0.1 * (0.4 * u + 0.6 * ease_io(u))
        rot = -2 + 1 * u + 4 * pan
        return "".join(s), cam(cx, cy, sc, rot), pan
    s.append(_ST["kit_n"])
    s.append(lamp(t, True))
    s.append(mug(0.0, t))
    # стикер летит к панели и шлёпается
    e = t - SLAP
    sx, sy = STK
    if e < 0:
        q = clamp((t - 27.17) / (SLAP - 27.17))
        k = ease_out(q, 2)
        cxs, cys = sx - 260 * (1 - k), sy + 380 * (1 - k)
        scs = STK_S * (1.5 - 0.5 * k)
        rs = -14 * (1 - k)
        sq = 0.0
    else:
        cxs, cys, rs = sx, sy, -3
        sq = math.exp(-e * 14) * math.cos(e * 40)
        scs = STK_S
    curl = clamp(0.1 + 0.5 * max(0, sq))
    s.append(blob([(cxs - NS / 2 * scs + 10, cys - NS / 2 * scs + 14, 1), (cxs + NS / 2 * scs + 14, cys - NS / 2 * scs + 14, 1),
                   (cxs + NS / 2 * scs + 14, cys + NS / 2 * scs + 16, 1), (cxs - NS / 2 * scs + 10, cys + NS / 2 * scs + 16, 1)], "#1a0e05", .35, blur(7)))
    s.append(f'<g transform="translate({f(cxs)} {f(cys)}) rotate({f(rs)}) scale({f(scs * (1 + 0.06 * sq))} {f(scs * (1 - 0.06 * sq))})">'
             f'{_ST["note_done"] if curl < 0 else sticker(t, True, curl)}</g>')
    # ладонь: приходит со стикером, прижимает, уходит вниз
    if e < 0.4:
        if e < 0:
            hx, hy = cxs + 10, cys + 90
        else:
            k = ease_in(clamp((e - 0.12) / 0.28), 2)
            hx, hy = sx + 10 + 60 * k, sy + 90 + 900 * k
        s.append(press_hand(hx, hy, 0.95, -6 + (8 * clamp(e / 0.4) if e > 0 else 0), max(0, sq)))
    # удар — короткие штрихи вокруг стикера
    if 0 <= e < 0.22:
        a = 1 - e / 0.22
        for k in range(8):
            ang = k * math.pi / 4 + 0.3
            r0 = 170 + 90 * ease_out(e / .22)
            s.append(line([(sx + math.cos(ang) * r0, sy + math.sin(ang) * r0),
                           (sx + math.cos(ang) * (r0 + 50 * a), sy + math.sin(ang) * (r0 + 50 * a))], 8 * a + 1, "#fff4c8", taper=.5, seed=1100 + k))
    q = t - 27.18
    sc = 1.22 + 0.08 * clamp(q / 1.1)
    cx, cy = 1810 - 60 * (1 - pan), 660
    rot = 2 - 2 * pan + 0.8 * math.sin(t * 1.3)
    if e >= 0:
        k = math.exp(-e * 10)
        cx += 10 * k * math.sin(e * 60)
        cy += 8 * k * math.sin(e * 50 + 1)
        sc *= 1 + 0.03 * k
    return "".join(s), cam(cx, cy, sc, rot), 1 - pan


def desk():
    """Стол вечером, вид сверху: дерево, тёплое пятно лампы, кружка-подставка и телефон по краям."""
    s = []
    DEFS.append('<pattern id="pWoodN" width="420" height="140" patternUnits="userSpaceOnUse">'
                '<rect width="420" height="140" fill="#8a5a34"/>'
                '<path d="M0 30 C120 22 260 40 420 28 M0 78 C140 86 280 66 420 82 M0 118 C110 110 300 126 420 114" fill="none" stroke="#734824" stroke-width="3"/>'
                '<rect y="138" width="420" height="2" fill="#5c3818"/></pattern>')
    s.append('<rect x="-800" y="-800" width="2700" height="3400" fill="url(#pWoodN)"/>')
    g = rad_grad([(0, "#ffd890", .5), (.6, "#ffb860", .16), (1, "#ffb860", 0)], 520, 700, 900, 900)
    s.append(f'<rect x="-800" y="-800" width="2700" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    # телефон экраном вниз у края стола
    s.append(blob(rect_pts(1000, 140, 1250, 620), "#1a0e05", .4, blur(10)))
    s.append(shape(rect_pts(980, 120, 1220, 600, 34), "#2b2f3a", blob(rect_pts(1000, 140, 1200, 580, 26), "#20242e"), w=4.6, seed=1200))
    return "".join(s)


# ─────────────────────────────── s15
def fist(x, y, sc, rot):
    """Кулак тыльной стороной (правая рука, рукой вниз): держит задники кроссовок. Рукав уходит вверх."""
    s = []
    P = lambda pts: T(pts, x, y, sc, rot)
    s.append(shape(P([(-110, -150, 1), (110, -160, 1), (170, -900, 1), (-160, -900, 1)]), HOOD,
                   blob(P([(40, -150), (110, -160), (170, -900), (60, -900)]), HOOD_SH, .9) +
                   line(P([(-50, -260), (-20, -480), (-40, -700)]), 4, FOLD, seed=1310, op=.7), w=5.2, seed=1311))
    s.append(shape(P([(-118, -118, 1), (116, -126, 1), (120, -196, 1), (-116, -190, 1)]), HOOD_SH,
                   "".join(line(P([(-96 + k * 40, -124), (-96 + k * 40, -186)]), 2.6, FOLD, seed=1320 + k, op=.8) for k in range(6)),
                   w=4.6, seed=1312))
    # согнутые пальцы: ряд «колбасок» поперёк, костяшками к нам
    for k in range(4):
        fx = -66 + k * 44
        pts = [(fx - 20, 34, 1), (fx + 20, 34, 1), (fx + 22, 92), (fx, 108), (fx - 22, 92)]
        s.append(shape(P(pts), SKIN, blob(P([(fx - 22, 80), (fx + 22, 80), (fx, 108)]), SKIN_SH, .9), w=4.2, seed=1330 + k))
    back = [(-96, -110, 1), (96, -116, 1), (104, -20), (96, 46), (40, 60), (-40, 60), (-100, 40), (-106, -30)]
    inner = blob(P([(40, -110), (96, -116), (104, -20), (96, 46), (40, 60)]), SKIN_SH, .9)
    for k in range(4):
        fx = -66 + k * 44
        inner += line(P([(fx - 12, 36), (fx, 46), (fx + 12, 36)]), 2.6, SKIN_SH2, seed=1340 + k, op=.8)
    inner += line(P([(-30, -70), (-24, 10)]), 2.4, SKIN_SH2, seed=1350, op=.6)
    s.append(shape(P(back), SKIN, inner, w=5, seed=1351))
    # большой палец сбоку слева, прижат
    th = sausage(P([(-96, -40), (-122, 10), (-104, 58)]), 50 * sc, 42 * sc)
    s.append(shape(th, SKIN, "", w=4.2, seed=1352))
    return "".join(s)


def box15():
    """Коробка на стойке без крышки (крышка прислонена к стене), бумага внутри."""
    s = []
    x0, x1 = BOX
    y1 = CTR - 40
    y0 = y1 - 300
    s.append(blob(rect_pts(x0 + 20, y1 - 20, x1 + 50, y1 + 10), "#1a0e05", .45, blur(12)))
    # крышка у стены
    s.append(shape([(x0 + 60, y0 - 220, 1), (x1 + 20, y0 - 250, 1), (x1 + 40, y0 + 40, 1), (x0 + 60, y0 + 60, 1)], "#a8743f",
                   blob(ellipse_pts(x1 - 120, y0 - 90, 44, 44, 16), "#e9e1d2") + blob(ellipse_pts(x1 - 120, y0 - 90, 30, 18, 12, rot=-20), "#c4473b"),
                   w=4.6, seed=1400))
    s.append(shape([(x0, y0, 1), (x1, y0, 1), (x1 + 50, y0 - 70, 1), (x0 + 50, y0 - 70, 1)], "#3a2414", "", w=4, seed=1401))
    return "".join(s), (x0, x1, y0, y1)


def box15_front(empty_t):
    x0, x1 = BOX
    y1 = CTR - 40
    y0 = y1 - 300
    s = []
    s.append(shape([(x0, y0 + 10), (x0 + 60, y0 - 30), (x0 + 200, y0 - 10), (x0 + 330, y0 - 44), (x1 - 20, y0 - 20), (x1 + 30, y0 - 50),
                    (x1, y0 + 20, 1), (x0, y0 + 20, 1)], "#f3ece0", "", w=3, seed=1402))
    s.append(shape([(x1, y0, 1), (x1 + 50, y0 - 70, 1), (x1 + 50, y1 - 70, 1), (x1, y1, 1)], "#7f532a", "", w=4.6, seed=1403))
    s.append(shape(rect_pts(x0, y0, x1, y1), "#a8743f", blob(rect_pts(x0, y1 - 46, x1, y1), "#7f532a", .8) +
                   blob(ellipse_pts(x1 - 120, y0 + 120, 44, 44, 16), "#e9e1d2") + blob(ellipse_pts(x1 - 120, y0 + 120, 30, 18, 12, rot=-20), "#c4473b"),
                   w=5, seed=1404))
    return "".join(s)


GRAB = 29.15


def frame15(t):
    s = [_ST["kit_d"], lamp(t, False)]
    fill = ease_io(clamp((t - 28.0) / 0.5))
    s.append(pour(t))
    s.append(mug(fill, t))
    s.append(steam(t, 1500))
    s.append(f'<g transform="translate({STK[0]} {STK[1]}) rotate(-3) scale({STK_S})">{_ST["note_done"]}</g>')
    # кроссовки: стоят в коробке, на «кроссовки» их выдёргивает рука вверх
    bx, by_ = _ST["box_back"]
    s.append(_ST["box_back_svg"])
    x0, x1, y0, y1 = by_
    e = t - GRAB
    hx = (x0 + x1) / 2 - 10
    if e < 0:
        # рука влетает сверху к коробке (с 28.95)
        q = ease_in(clamp((t - 28.93) / (GRAB - 28.93)), 1.6)
        hy = -500 + (y0 - 90 + 500) * q
        lift = 0.0
    else:
        lift = 1100 * ease_in(clamp((e - 0.06) / 0.34), 1.8) - 30 * math.sin(math.pi * clamp(e / 0.06))
        hy = y0 - 90 - lift
    # кроссовки: задник в кулаке — висят носками вниз, качаются
    sw = 0.0 if e < 0 else 10 * math.sin(e * 12) * math.exp(-e * 2)
    if e < 0:
        a, _ = sneaker(x0 + 190, y0 + 20, 1.0, -2, 1500)
        b, P = sneaker(x0 + 330, y0 + 4, 1.0, 4, 1520)
        clip = lib.clip_rect(x0 - 600, -3000, x1 - x0 + 1200, y0 + 3010)
        s.append(f'<g clip-path="url(#{clip})">{a}{b}</g>')
        s.append(box15_front(t))
        if t > 28.93:
            s.append(fist(hx, hy, 0.95, 0))
    else:
        a, _ = sneaker(hx - 22, hy + 96 + 140, 0.95, 96 + sw, 1500)
        b, P = sneaker(hx + 26, hy + 90 + 140, 0.95, 84 + sw * 1.2, 1520)
        c2 = lib.clip_rect(x0 - 2000, -4000, x1 - x0 + 4000, y1 - 20 + 4000)
        s.append(f'<g clip-path="url(#{c2})">{a}{b}</g>')
        s.append(box15_front(t))
        s.append(fist(hx, hy, 0.95, sw * 0.2))
    # бумага вылетает из коробки
    if 0 < e < 0.7:
        rs = np.random.RandomState(5)
        for k in range(5):
            px = (x0 + x1) / 2 + rs.uniform(-200, 200) + rs.uniform(-1, 1) * 400 * e
            py = y0 - 20 - 900 * e + 1800 * e * e + rs.uniform(-30, 30)
            r = rs.uniform(18, 30)
            s.append(shape(ellipse_pts(px, py, r, r * .6, 5, rot=rs.uniform(0, 360) + 400 * e, jitter=.3, seed=k), "#f3ece0", "", w=2.6, seed=1600 + k))
    # камера: быстрый наезд на кружку и стикер, потом к коробке
    u = clamp((t - 27.92) / 0.35)
    sc = 0.78 + 0.22 * ease_out(u, 3)
    cx = 1830 + 30 * u
    cy = 720
    k = smooth(28.8, 29.12, t)
    cx += (2330 - 1830) * k
    cy += (560 - 720) * k
    sc *= 1 - 0.1 * k
    rot = 1.5 - 1.5 * u + 1.0 * k
    if e >= 0:
        cy -= 120 * ease_out(clamp(e / 0.5), 2)
        kk = math.exp(-e * 8)
        cx += 8 * kk * math.sin(e * 55)
    if t >= 28.56:
        q = t - 28.56
        sc *= 1 + 0.035 * math.exp(-q * 6) * math.sin(min(q * 14, math.pi))
    return "".join(s), cam(cx, cy, sc, rot)


def frame(sid, t):
    if not _ST:
        DEFS.append('<filter id="fShH" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                    '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
        _ST["desk"] = desk()
        _ST["kit_n"] = kitchen(True)
        _ST["kit_d"] = kitchen(False)
        _ST["note_done"] = sticker(99, True, 0.12)
        bb, geo = box15()
        _ST["box_back_svg"], _ST["box_back"] = bb, (None, geo)
        lib.static_done()
    lib.dyn_begin()
    if sid == "s14":
        art, cm, pan = frame14(t)
        bl = ""
        k = math.sin(math.pi * clamp((t - 27.12) / 0.1))
        if k > 0.05:
            i = f"wb{int(k * 20)}"
            DEFS.append(f'<filter id="{i}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{f(40 * k)} {f(3 * k)}"/></filter>')
            bl = f' filter="url(#{i})"'
        bg = "#8a5a34" if t < 27.17 else "#3c4a63"
        return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g{bl}><g transform="{cm}">{art}</g></g>')
    art, cm = frame15(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#f1e2c4"/><g transform="{cm}">{art}</g>')
