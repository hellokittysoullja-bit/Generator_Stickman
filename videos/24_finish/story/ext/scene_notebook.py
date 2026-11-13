"""Сцена notebook (s15): крупно страница блокнота в клетку на столе. Рука Димы (горчичный рукав) въезжает и пишет
рукописью строку «позвонил клиенту» по буквам ~26.9–28.4 (буквы — контуры Caveat 600 из hand_glyphs.json, каждая
проявляется по ходу пера), на «сегодня» (28.76) ставит в квадратик жирную зелёную галочку; лёгкий наезд."""
import json
import math
import os

import numpy as np

import lib
import hand
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, fill_d,
                 line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg)

G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_glyphs.json")))
FS = 114
SC = FS / G["upm"]
TX0, BASE = 206, 790          # начало строки, базовая линия
W0, W1 = 26.9, 28.4           # письмо
CHECK0, CHECK1 = 28.70, 28.92  # галочка: «сегодня» 28.76
INKC = "#26356f"
BOX = (108, 724, 164, 780)    # квадратик слева от строки
CHK = [(116, 748), (128, 760), (140, 774), (160, 742), (178, 712), (196, 688)]
ANG, HSC = -36, 1.32
_ST = {}


def layout():
    """x и время каждой буквы: время пропорционально ширине, пробел — короткая пауза пера в воздухе."""
    out, x = [], TX0
    for g in G["glyphs"]:
        b = g["bounds"]
        if b:
            gx0, gx1 = x + b[0] * SC, x + b[2] * SC
            gy0, gy1 = BASE - b[3] * SC, BASE - b[1] * SC
        else:
            gx0 = gx1 = x + g["adv"] * SC * .5
            gy0 = gy1 = BASE - 30
        out.append(dict(g=g, x=x, gx0=gx0, gx1=gx1, gy0=gy0, gy1=gy1, w=max(gx1 - gx0, 1.0) if b else 0.0))
        x += g["adv"] * SC
    tot = sum(max(o["w"], 0) + (34 if not o["g"]["bounds"] else 0) for o in out)
    t = W0
    for o in out:
        dur = (W1 - W0) * ((o["w"] if o["g"]["bounds"] else 34) / tot)
        o["t0"], o["t1"] = t, t + dur
        t += dur
    return out


L = layout()


def pen_tip(t):
    """Где кончик ручки: подъезд к строке, ход по буквам (петли вверх-вниз по высоте буквы), переход к квадратику,
    галочка, уход."""
    if t < W0:
        u = ease_out(clamp((t - 26.3) / (W0 - 26.3)), 2.2)
        sx, sy = 760, 1040
        ex, ey = L[0]["gx0"], BASE - 30
        return sx + (ex - sx) * u, sy + (ey - sy) * u - 40 * math.sin(math.pi * u), 1.0 + 0.06 * (1 - u)
    if t < W1:
        for i, o in enumerate(L):
            if o["t0"] <= t < o["t1"]:
                q = (t - o["t0"]) / (o["t1"] - o["t0"])
                if not o["g"]["bounds"]:
                    x = L[i - 1]["gx1"] + (L[i + 1]["gx0"] - L[i - 1]["gx1"]) * q
                    return x, BASE - 34 - 10 * math.sin(math.pi * q), 1.03
                x = o["gx0"] + (o["gx1"] - o["gx0"]) * q
                lo, hi = o["gy1"], max(o["gy0"], BASE - 70)
                y = lo + (hi - lo) * (0.5 + 0.5 * math.sin(q * 2 * math.pi * 1.4 + i * 1.3))
                return x, y, 1.0
        return L[-1]["gx1"], BASE - 30, 1.0
    if t < CHECK0:   # перо поднимается и перелетает к квадратику
        u = ease_io((t - W1) / (CHECK0 - W1))
        sx, sy = L[-1]["gx1"], BASE - 30
        ex, ey = CHK[0]
        return sx + (ex - sx) * u, sy + (ey - sy) * u - 70 * math.sin(math.pi * u), 1.0 + 0.08 * math.sin(math.pi * u)
    if t < CHECK1:
        u = (t - CHECK0) / (CHECK1 - CHECK0)
        p = check_pts(u)
        return p[-1][0], p[-1][1], 1.0
    e = t - CHECK1
    u = ease_out(clamp(e / 0.8), 2)
    ex, ey = CHK[-1]
    return ex + 260 * u, ey + 520 * u - 30 * math.sin(math.pi * min(u, 1)), 1.0 + 0.07 * u


def check_pts(u):
    S = lib.sample(CHK, False, 3)
    n = max(2, int(len(S) * clamp(u)))
    return [tuple(p) for p in S[:n]]


def paper():
    s = []
    DEFS.append('<filter id="fShH" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
    # стол
    DEFS.append('<pattern id="pWoodN" width="400" height="130" patternUnits="userSpaceOnUse">'
                '<rect width="400" height="130" fill="#a8703f"/>'
                '<path d="M0 28 C120 20 260 38 400 26 M0 72 C140 80 280 62 400 76 M0 112 C110 104 300 120 400 108" fill="none" stroke="#8c5a2e" stroke-width="3"/>'
                '<rect y="128" width="400" height="2" fill="#6f4522"/></pattern>')
    s.append(f'<rect x="-300" y="-300" width="{W + 600}" height="{H + 600}" fill="url(#pWoodN)"/>')
    # блокнот: тень, обрез страниц под листом, лист в клетку
    P0 = (60, 250)
    s.append(blob(rect_pts(P0[0] + 18, P0[1] + 24, W + 260, H + 300), "#3a210f", .45, blur(12)))
    s.append(shape(rect_pts(P0[0] - 14, P0[1] - 6, W + 240, H + 300, 14), "#2f6db5", "", w=5, seed=301))
    s.append(shape(rect_pts(P0[0] - 2, P0[1] + 8, W + 230, H + 300, 6), "#efe7d2", "", w=3, seed=302))
    pg = rect_pts(P0[0], P0[1], W + 220, H + 300, 4)
    DEFS.append('<pattern id="pGrid" x="60" y="250" width="44" height="44" patternUnits="userSpaceOnUse">'
                '<path d="M0 0.5H44M0.5 0V44" stroke="#b9d0ea" stroke-width="1.6" fill="none"/></pattern>')
    inner = f'<rect x="{P0[0]}" y="{P0[1]}" width="{W + 200}" height="{H}" fill="url(#pGrid)"/>'
    inner += line([(P0[0] + 2, 250 + 44 * 3), (P0[0] + 2, H + 200)], 1, "#b9d0ea", op=0)
    gid = lin_grad([(0, "#ffffff", .0), (1, "#c9bfa8", .35)], 0, 0, 0, 1)
    inner += f'<rect x="{P0[0]}" y="{P0[1]}" width="{W + 200}" height="{H}" fill="url(#{gid})"/>'
    s.append(shape(pg, "#fbfaf4", inner, w=4.2, seed=303))
    # поле: красная линия
    s.append(line([(196 - 104, P0[1] + 60), (196 - 104, H + 300)], 2.6, "#e58f8f", taper=.05, wmin=.9, seed=304, op=.9))
    # пружина сверху
    for k in range(13):
        x = 120 + k * 76
        s.append(shape(ellipse_pts(x, P0[1] + 34, 12, 12, 10), "#4a3a2c", "", w=2.4, seed=310 + k))
        s.append(line([(x - 6, P0[1] + 34), (x - 2, P0[1] - 26), (x + 14, P0[1] - 30), (x + 12, P0[1] + 20)], 7, "#9aa4b2", taper=.1, wmin=.8, seed=330 + k))
        s.append(line([(x - 4, P0[1] - 18), (x + 6, P0[1] - 24)], 2.4, "#e9eef4", taper=.3, seed=350 + k))
    # квадратик под галочку — нарисован ручкой заранее
    x0, y0, x1, y1 = BOX
    s.append(line([(x0, y0), (x1 + 1, y0 + 1)], 4.6, INKC, taper=.4, wmin=.5, seed=360))
    s.append(line([(x1, y0 - 2), (x1 - 1, y1 + 1)], 4.6, INKC, taper=.4, wmin=.5, seed=361))
    s.append(line([(x1 + 2, y1), (x0 - 1, y1 - 1)], 4.6, INKC, taper=.4, wmin=.5, seed=362))
    s.append(line([(x0, y1 + 2), (x0 + 1, y0 - 2)], 4.6, INKC, taper=.4, wmin=.5, seed=363))
    # кружка кофе у верхнего угла и ластик — обжитость
    s.append(blob(ellipse_pts(970, 130, 110, 110, 18), "#3a210f", .4, blur(8)))
    s.append(shape(ellipse_pts(950, 110, 104, 104, 18), "#e9e4dc", blob(ellipse_pts(950, 110, 82, 82, 16), "#6b3d22") +
                   blob(ellipse_pts(930, 92, 26, 12, 10, rot=-20), "#8c5634"), w=4.6, seed=370))
    return "".join(s)


def text(t):
    out = []
    for o in L:
        g = o["g"]
        if not g["bounds"] or t <= o["t0"]:
            continue
        q = clamp((t - o["t0"]) / (o["t1"] - o["t0"]))
        body = f'<path d="{g["d"]}" transform="translate({f(o["x"])} {BASE}) scale({SC:.5f} {-SC:.5f})" fill="{INKC}"/>'
        if q < 1:
            c = lib.clip_rect(o["gx0"] - 6, o["gy0"] - 10, (o["gx1"] - o["gx0"] + 12) * q, o["gy1"] - o["gy0"] + 20)
            body = f'<g clip-path="url(#{c})">{body}</g>'
        out.append(body)
    return "".join(out)


def check(t):
    if t < CHECK0:
        return ""
    u = clamp((t - CHECK0) / (CHECK1 - CHECK0))
    pts = check_pts(u)
    if len(pts) < 3:
        return ""
    s = [line([(x + 2, y + 3) for x, y in pts], 23, "#1f7a34", taper=.25, wmin=.45, seed=380, peak=.35),
         line(pts, 21, "#34b553", taper=.25, wmin=.45, seed=381, peak=.35),
         line([(x - 3, y - 3) for x, y in pts[2:-2]], 5, "#9ce8a6", taper=.6, seed=382, op=.8)]
    if t > CHECK1:   # искорки радости вокруг галочки
        e = t - CHECK1
        a_ = math.exp(-e * 2.2)
        for k in range(7):
            ang = -math.pi / 2 + (k - 3) * 0.5
            r0 = 70 + 60 * ease_out(e / .5)
            Lr = 30 * a_
            cx, cy = 150, 728
            if Lr > 3:
                s.append(line([(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0), (cx + math.cos(ang) * (r0 + Lr), cy + math.sin(ang) * (r0 + Lr))],
                              7, "#34b553", taper=.5, seed=390 + k))
    return "".join(s)


def frame(sid, t):
    if not _ST:
        _ST["paper"] = paper()
        lib.static_done()
    lib.dyn_begin()
    x, y, lift = pen_tip(t)
    # дрожь пера при письме
    if W0 < t < W1:
        y += 1.5 * math.sin(t * 61)
    curl = smooth(CHECK0 - 0.05, CHECK0 + 0.05, t) * (1 - smooth(CHECK1, CHECK1 + 0.2, t))
    ang = ANG + 3 * math.sin(t * 2.3) - 4 * (lift - 1)
    shadow = (f'<g transform="translate({f(x + 26 * lift)} {f(y + 34 * lift)}) scale({f(HSC)})" opacity=".28" filter="url(#fShH)">'
              f'{hand.hand(ang, 7)}</g>')
    hnd = f'<g transform="translate({f(x)} {f(y)}) scale({f(HSC * lift)})">{hand.hand(ang, 7, curl)}</g>'
    art = _ST["paper"] + text(t) + check(t) + shadow + hnd
    lin = clamp((t - 26.4) / 3.36)
    u = 0.4 * lin + 0.6 * ease_io(lin)
    cm = cam(526, 820 - 10 * u, 1.18 + 0.10 * u, -1.2 + 0.6 * u)
    return svg(f'<rect width="{W}" height="{H}" fill="#a8703f"/><g transform="{cm}">{art}</g>')
