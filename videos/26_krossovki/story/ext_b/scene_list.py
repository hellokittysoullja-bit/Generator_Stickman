"""Сцена list (s11): крупно листок на столе вечером. Рука Димы (горчичный рукав, хват из рилса 24, большой палец за
ручкой) пишет рукописью три строки «отчёт», «позвонить маме», «корм коту». Буквы — контуры Caveat 600 (list_glyphs.json),
каждая проявляется маской по ходу пера (скелет буквы), а не шторкой. Значки дел прилетают сверху к своей строке и,
когда перо начинает строку, превращаются в точку-маркер; к «листок» (24.28) лист заполнен."""
import json
import math
import os

import numpy as np

import hand
import icons
import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg)

G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "list_glyphs.json")))
FS = 128
SC = FS / G["upm"]
TX0 = 250
BASES = [700, 900, 1100]
SLOTS = [(22.82, 23.16), (23.24, 23.86), (23.96, 24.26)]   # письмо строк
ICON = ["report", "phone", "bowl"]
ICON_IN = [22.38, 22.52, 22.66]                              # прилёт значка (начало)
INKC = "#26356f"
ANG, HSC = -36, 1.12
_ST = {}


def build_lines():
    """Для каждой строки: буквы с x, штрихи пера в мире, общая длина и время каждой точки пути."""
    out = []
    for li, gl in enumerate(G["lines"]):
        x = TX0
        base = BASES[li]
        path = []          # (x, y, glyph_index, pen_down)
        gls = []
        for gi, g in enumerate(gl):
            gls.append(dict(g=g, x=x))
            for st in g.get("strokes", []):
                pts = [(x + px * SC, base - py * SC) for px, py in st]
                for k, p in enumerate(pts):
                    path.append((p[0], p[1], gi, k > 0))
            x += g["adv"] * SC
        P = np.array([(p[0], p[1]) for p in path])
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        # перелёт пера над бумагой «стоит» как 0.4 своей длины
        down = np.array([p[3] for p in path[1:]])
        cost = np.where(down, seg, seg * 0.4)
        cum = np.concatenate([[0], np.cumsum(cost)])
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


def text_line(li, t):
    """Готовые буквы целиком; текущая — под маской из пройденного пером пути (круглое перо толщиной штриха)."""
    ln = L[li]
    a, b = SLOTS[li]
    if t <= a:
        return ""
    p = progress(li, t)
    s = []
    if p >= 1:
        cur = len(ln["gls"])
        i_now = len(ln["P"]) - 1
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
            DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-600" y="-600" width="2400" height="3200">'
                        f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{f(wpx)}" stroke-linecap="round" stroke-linejoin="round"/></mask>')
            body = f'<g mask="url(#{mid})">{body}</g>'
        s.append(body)
    return "".join(s)


def pen_tip(t):
    """Кончик пера: въезд, ход по строкам, перелёт между строками, отъезд."""
    a0 = SLOTS[0][0]
    if t < a0:
        u = ease_out(clamp((t - 22.45) / (a0 - 22.45)), 2.2)
        sx, sy = 900, 1500
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
    u = ease_out(clamp(e / 0.7), 2)
    sx, sy = tip_at(2, 1.0)[:2]
    return sx + 220 * u, sy + 420 * u, 1.0 + 0.07 * u


def paper():
    s = []
    DEFS.append('<filter id="fShH" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
    DEFS.append('<pattern id="pWoodL" width="420" height="140" patternUnits="userSpaceOnUse">'
                '<rect width="420" height="140" fill="#8a5a34"/>'
                '<path d="M0 30 C120 22 260 40 420 28 M0 78 C140 86 280 66 420 82 M0 118 C110 110 300 126 420 114" fill="none" stroke="#734824" stroke-width="3"/>'
                '<rect y="138" width="420" height="2" fill="#5c3818"/></pattern>')
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#pWoodL)"/>')
    # тёплое пятно лампы
    g = rad_grad([(0, "#ffd890", .55), (.6, "#ffb860", .18), (1, "#ffb860", 0)], 520, 760, 900, 900)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    # листок: тень, сам лист в линейку, поле
    sh = [(150, 320), (1030, 320), (1030, 1600), (150, 1600)]
    s.append(blob([(x + 20, y + 26) for x, y in sh], "#2a1608", .45, blur(14)))
    inner = ""
    for k in range(13):
        y = 400 + k * 100
        inner += line([(140, y + 8), (1040, y + 8)], 2.2, "#b6cde6", taper=.05, wmin=.9, seed=400 + k)
    inner += line([(160, 320), (160, 1600)], 2.4, "#e59a9a", taper=.05, wmin=.9, seed=420)
    gid = lin_grad([(0, "#ffffff", 0), (1, "#d9cdb0", .35)], 0, 0, 0, 1)
    inner += f'<rect x="100" y="280" width="1000" height="1360" fill="url(#{gid})"/>'
    s.append(shape([(150, 320, 1), (1030, 320, 1), (1030, 1600, 1), (150, 1600, 1)], "#fbf9f2", inner, w=4.2, seed=430))
    # кружка чая и угол телефона — обжитость
    s.append(blob(ellipse_pts(1010, 190, 112, 112, 18), "#2a1608", .4, blur(9)))
    s.append(shape(ellipse_pts(990, 170, 104, 104, 18), "#e2584a", blob(ellipse_pts(990, 170, 82, 82, 16), "#a8662e") +
                   blob(ellipse_pts(970, 152, 26, 12, 10, rot=-20), "#c98a4e"), w=4.6, seed=440))
    s.append(shape(rect_pts(-60, 1500, 160, 1940, 30), "#2b2f3a", blob(rect_pts(-40, 1530, 140, 1900, 14), "#1b2030"), w=4.6, seed=441))
    return "".join(s)


def bullet(li, t):
    a = SLOTS[li][0]
    if t < a - 0.05:
        return ""
    k = back_out(clamp((t - a + 0.05) / 0.18), 2.4)
    x, y = TX0 - 46, BASES[li] - 26
    return shape(ellipse_pts(x, y, 11 * k, 11 * k, 10), INKC, "", w=2, seed=500 + li)


def flying_icon(li, t):
    """Значок дела прилетает сверху по дуге на свою строку и ждёт; когда перо начинает строку, он сжимается в точку-маркер
    (с искорками) — дело превращается в строку."""
    t0 = ICON_IN[li]
    a = SLOTS[li][0]
    if t < t0:
        return ""
    bx, by = TX0 - 46, BASES[li] - 26
    hx, hy = TX0 + 120, BASES[li] - 50
    sx, sy = [900, 380, 760][li], -300
    T = 0.32
    u = clamp((t - t0) / T)
    if t < a:
        x = sx + (hx - sx) * ease_out(u, 2)
        y = sy + (hy - sy) * ease_in(u, 1.4)
        rot = 70 * (1 - u) * (1 if li % 2 else -1)
        land = max(t - t0 - T, 0)
        sc = 2.2 * (1 + 0.18 * math.exp(-land * 10) * math.cos(land * 30) * (u >= 1))
        rot += 4 * math.sin(t * 7 + li) * (u >= 1)
        return icons.icon(ICON[li], x, y, sc, rot, 600 + li * 20)
    e = t - a
    k = 1 - ease_in(clamp(e / 0.16), 1.5)
    if k <= 0.02:
        if e < 0.4:
            s = ""
            for j in range(6):
                ang = j * math.pi / 3 + li
                r0 = 30 + 70 * ease_out(e / .4)
                L_ = 22 * (1 - e / .4)
                s += line([(bx + math.cos(ang) * r0, by + math.sin(ang) * r0), (bx + math.cos(ang) * (r0 + L_), by + math.sin(ang) * (r0 + L_))],
                          6, "#f0a83a", taper=.5, seed=620 + j)
            return s
        return ""
    x = bx + (hx - bx) * k
    y = by + (hy - by) * k
    return icons.icon(ICON[li], x, y, 2.2 * k, 0, 600 + li * 20)


def frame(sid, t):
    if not _ST:
        _ST["paper"] = paper()
        lib.static_done()
    lib.dyn_begin()
    x, y, lift = pen_tip(t)
    curl = 0.0
    ang = ANG + 3 * math.sin(t * 2.3) - 4 * (lift - 1)
    shadow = (f'<g transform="translate({f(x + 26 * lift)} {f(y + 34 * lift)}) scale({f(HSC)})" opacity=".28" filter="url(#fShH)">'
              f'{hand.hand(ang, 7)}</g>')
    hnd = f'<g transform="translate({f(x)} {f(y)}) scale({f(HSC * lift)})">{hand.hand(ang, 7, curl)}</g>'
    txt = "".join(text_line(i, t) + bullet(i, t) for i in range(3))
    ic = "".join(flying_icon(i, t) for i in range(3))
    art = _ST["paper"] + txt + ic + shadow + hnd
    lin = clamp((t - 22.5) / 2.6)
    u = 0.4 * lin + 0.6 * ease_io(lin)
    cm = cam(600, 900 - 10 * u, 1.24 + 0.08 * u, -2.0 + 0.8 * u)
    return svg(f'<rect width="{W}" height="{H}" fill="#8a5a34"/><g transform="{cm}">{art}</g>')
