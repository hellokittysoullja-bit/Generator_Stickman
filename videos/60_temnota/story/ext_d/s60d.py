"""Рилс 60 «темнота», группа D: s09 (Дима на подушке, глаза отдыхают), s10 (спит, мама включает лампу, комната заливается светом),
s11 (глаз в шезлонге с пледом). frame(sid, t) -> SVG 1080×1920, t — общее время ролика (как в ext_d рилса 59)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
_C60 = os.path.join(STORY, "common")
_C59 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "59_podarok", "story", "common")
sys.path.insert(0, HERE)
sys.path.insert(0, _C60 if os.path.exists(os.path.join(_C60, "lib.py")) else _C59)   # lib/ink/hand/people/props
import lib  # noqa: E402
from lib import (INK, back_out, blob, blur, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, rad_grad, rrect,  # noqa: E402,F401
                 shape, smooth, spring)

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def find(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after and w["word"].strip(".,!?").lower() == word:
            return w["start"]
    raise KeyError(word)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def lerp(a, b, u):
    return a + (b - a) * u


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def partial(pts, u, step=4.0):
    """Первые u долей ломаной (для «рисуется пером»)."""
    if u >= 1:
        return list(pts)
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tgt = L[-1] * clamp(u)
    out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= tgt:
            out.append(pts[i])
        else:
            r = (tgt - L[i - 1]) / max(1e-6, L[i] - L[i - 1])
            out.append((pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * r, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * r))
            break
    return out


def zzz(x, y, k, col="#5b6fb5", seed=0, op=1.0):
    """Значок сна «Z» тремя штрихами пера (пиктограмма, не надпись)."""
    a = 46 * k
    pts = [(x - a, y - a), (x + a, y - a), (x - a, y + a), (x + a, y + a)]
    o = []
    for i in range(3):
        o.append(line([pts[i], pts[i + 1]], 12 * k, col, taper=.15, wmin=.75, seed=seed + i, op=op))
    return "".join(o)


# ══════════════════════════════════════ s11: глаз в шезлонге ══════════════════════════════════════
T_OTDYH = find("отдых", 19.0)        # 19.06
T_GLAZAM = find("глазам", 18.0)      # 18.688
T_VAZH = find("важнее", 17.5)        # 17.96


def eye_creature(cx, cy, R, t, openk, look, skin="#efbf9f", skin_sh="#d49c7e", seed=11000, brow=0.0, rolled=0.0):
    """Глаз-существо: кожаное «лицо»-овал, в нём веко-миндалина. openk 0..1 (0 — закрыт дугой сна ‿), look — взгляд (-1..1)."""
    s = []
    rx, ry = R * 1.34, R * 1.14
    face = ellipse_pts(cx, cy, rx, ry, 20)
    s.append(shape(face, skin, blob(ellipse_pts(cx + rx * .12, cy + ry * .55, rx * 1.0, ry * .62, 18), skin_sh, .55)
                   + blob(ellipse_pts(cx - rx * .4, cy - ry * .55, rx * .28, ry * .16, 10), "#ffe3cc", .55), w=6.2, seed=seed))
    # румянец
    s.append(blob(ellipse_pts(cx - rx * .62, cy + ry * .42, 38, 22, 10), "#f0948f", .35))
    s.append(blob(ellipse_pts(cx + rx * .62, cy + ry * .42, 38, 22, 10), "#f0948f", .35))
    # миндалина века
    ex = R * 1.02
    h = R * .92 * openk
    droop = (1 - openk) * R * .20          # закрытый глаз — дуга ‿ вниз
    N = 17
    up, lo = [], []
    for i in range(N):
        u = -1 + 2 * i / (N - 1)
        sh = (1 - u * u) ** .85
        sk = (1 - u * u)
        up.append((cx + u * ex, cy - h * .62 * sh + droop * sk * 1.0 - R * .05 * u * u * (1 - openk)))
        lo.append((cx + u * ex, cy + h * .38 * sh + droop * sk * 1.0))
    almond = up + lo[::-1][1:-1]
    # внутри миндалины: белок, радужка, зрачок
    if openk > 0.03:
        cid = lib.clip_of(almond)
        ir = R * .53
        px = cx + look[0] * R * .30
        py = cy + look[1] * R * .20 + (1 - openk) * R * .10
        inner = [f'<g><path d="{lib.fill_d(almond)}" fill="#f7f3ec"/><g clip-path="url(#{cid})">']
        inner.append(blob(ellipse_pts(cx, cy - h * .5, ex * 1.1, h * .35, 14), "#d4cde0", .7))   # тень от верхнего века
        inner.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{ir:.1f}" fill="#3f9d94"/>')
        inner.append(f'<circle cx="{px:.1f}" cy="{py + ir * .22:.1f}" r="{ir * .78:.1f}" fill="#6cc5b4" opacity=".8"/>')
        for k in range(14):                                                    # лучики радужки
            a = 2 * math.pi * k / 14 + .2
            inner.append(f'<line x1="{px + math.cos(a) * ir * .38:.1f}" y1="{py + math.sin(a) * ir * .38:.1f}" '
                         f'x2="{px + math.cos(a) * ir * .93:.1f}" y2="{py + math.sin(a) * ir * .93:.1f}" stroke="#2c7b75" stroke-width="3" opacity=".6"/>')
        inner.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{ir * .17 + ir * .10 * (1 - openk):.1f}" fill="{INK}"/>' if False else
                     f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{ir * .44:.1f}" fill="{INK}"/>')
        inner.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{ir:.1f}" fill="none" stroke="{INK}" stroke-width="4.5"/>')
        inner.append(f'<circle cx="{px - ir * .30:.1f}" cy="{py - ir * .32:.1f}" r="{ir * .17:.1f}" fill="#ffffff"/>')
        inner.append(f'<circle cx="{px + ir * .26:.1f}" cy="{py + ir * .20:.1f}" r="{ir * .08:.1f}" fill="#ffffff" opacity=".9"/>')
        # тонкие бледные прожилки (здоровый глаз)
        for k, (a0, a1) in enumerate(((-2.7, -2.2), (2.9, 3.4), (-.4, .05))):
            xa, ya = cx + math.cos(a0) * ex * 1.05, cy + math.sin(a0) * h * .5
            inner.append(f'<path d="M{xa:.0f} {ya:.0f} Q{(xa + cx) / 2 - 10:.0f} {ya + 14:.0f} {xa + (cx - xa) * .42:.0f} {ya + 4:.0f}" '
                         f'stroke="#e8a0a0" stroke-width="2.4" fill="none" opacity=".5"/>')
        inner.append("</g></g>")
        s.append("".join(inner))
    # контур века
    s.append(line(up, 7.2, INK, taper=.35, wmin=.4, seed=seed + 3))
    s.append(line(lo, 4.6, INK, taper=.5, wmin=.3, seed=seed + 4, op=.9))
    if openk < .98:   # складка верхнего века
        crease = [(x, y - R * .22 * (0.4 + openk) - 6) for x, y in up[2:-2:2]]
        s.append(line(crease, 3.2, skin_sh, taper=.5, wmin=.3, seed=seed + 5, op=.9))
    # ресницы по верхнему краю (при закрытии — вниз-наружу, как у спящего)
    for i in range(2, N - 2, 2):
        x, y = up[i]
        u = (x - cx) / ex
        ang = math.radians(-90 + u * 55 + (1 - openk) * 25 * (1 if u > 0 else -1) * .0)
        ln = R * (.30 - .05 * abs(u)) * (1 - .15 * (1 - openk))
        dy = 1 if openk < .35 else -1          # закрытые — ресницы свисают
        if dy > 0:
            ang = math.radians(90 + u * 40)
            ln *= .8
        s.append(line([(x, y), (x + math.cos(ang) * ln * .55 + u * 5, y + math.sin(ang) * ln * .6),
                       (x + math.cos(ang) * ln * 1.0 + u * 14, y + math.sin(ang) * ln)], 4.6, INK, taper=.9, wmin=.1, seed=seed + 20 + i))
    # бровь
    by = cy - R * .86 - brow * 22
    s.append(line([(cx - R * 1.0, by + 16 - brow * 6), (cx - R * .3, by - 6), (cx + R * .45, by - 8 - brow * 6), (cx + R * 1.0, by + 12)],
                  16, "#7a4a2e", taper=.55, wmin=.2, seed=seed + 40))
    return "".join(s)


def steam(x, y, t, n=3, seed=0, h=190):
    o = []
    for i in range(n):
        ph = (t * .55 + i / n) % 1
        a = clamp(math.sin(math.pi * ph)) * .8
        xx = x + (i - 1) * 28
        pts = [(xx + 14 * math.sin(ph * 6 + i), y - h * ph * k - 4) for k in (0, .25, .5, .75, 1.0)]
        pts = [(xx + 14 * math.sin(ph * 5 + i + kk * 3), y - h * (ph * .6 + kk * .4)) for kk in (0, .25, .5, .75, 1.0)]
        o.append(line(pts, 11, "#ffffff", taper=.9, wmin=.1, seed=seed + i, op=a * .85))
    return "".join(o)


def plaid(pts, base, ln1, ln2, x0, x1, y0, y1, step=46):
    """Клетчатый плед: заливка pts + полосы в клетку, обрезка по контуру."""
    inner = []
    for x in range(int(x0), int(x1), step):
        inner.append(f'<rect x="{x}" y="{y0}" width="{step * .42:.0f}" height="{y1 - y0}" fill="{ln1}" opacity=".55"/>')
    for y in range(int(y0), int(y1), step):
        inner.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{step * .42:.0f}" fill="{ln1}" opacity=".55"/>')
    for x in range(int(x0) + 4, int(x1), step * 2):
        inner.append(f'<rect x="{x}" y="{y0}" width="5" height="{y1 - y0}" fill="{ln2}" opacity=".9"/>')
    for y in range(int(y0) + 4, int(y1), step * 2):
        inner.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="5" fill="{ln2}" opacity=".9"/>')
    return shape(pts, base, "".join(inner), w=5.6, seed=11300)


def bg11(t):
    s = []
    g = lib.lin_grad([(0, "#9fd8ee", 1), (.55, "#f7e3bd", 1), (1, "#fbd3a2", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-500" y="-500" width="2100" height="1850" fill="url(#{g})"/>')
    # солнце у горизонта, лучи
    sx, sy = 800, 1040
    gg = rad_grad([(0, "#fff6cf", 1), (.35, "#ffe6a0", .55), (1, "#ffe6a0", 0)], sx, sy, 420)
    s.append(f'<circle cx="{sx}" cy="{sy}" r="420" fill="url(#{gg})"/>')
    s.append(blob(ellipse_pts(sx, sy, 92, 92, 20), "#ffe58f"))
    # облачка
    for i, (cx_, cy_, w_) in enumerate(((140, 430, 110), (980, 300, 90), (330, 190, 70))):
        xx = cx_ + 12 * math.sin(t * .35 + i * 2)
        s.append(blob(ellipse_pts(xx, cy_, w_, w_ * .26, 14), "#ffffff", .9) + blob(ellipse_pts(xx + w_ * .4, cy_ - w_ * .16, w_ * .55, w_ * .26, 14), "#ffffff", .9))
    # море
    s.append(f'<rect x="-500" y="1075" width="2100" height="260" fill="#6cbdd6"/>')
    s.append(f'<rect x="-500" y="1075" width="2100" height="70" fill="#8fd6e6" opacity=".6"/>')
    s.append(line([(-500, 1076), (1600, 1076)], 4, INK, taper=.02, wmin=1, seed=11010, op=.7))
    for i in range(9):
        wx = -60 + i * 150 + 24 * math.sin(t * .8 + i)
        wy = 1110 + (i % 3) * 36
        s.append(line([(wx, wy), (wx + 36, wy - 8), (wx + 74, wy)], 5, "#ffffff", taper=.4, wmin=.3, seed=11020 + i, op=.7))
    # блик солнца на воде
    s.append(blob(ellipse_pts(sx, 1110, 70, 10, 12), "#fff2b8", .7))
    s.append(blob(ellipse_pts(sx + 10, 1150, 40, 7, 12), "#fff2b8", .6))
    # песок
    gs = lib.lin_grad([(0, "#f2d79e", 1), (1, "#d9b57a", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-500" y="1300" width="2100" height="900" fill="url(#{gs})"/>')
    s.append(line([(-500, 1300), (1600, 1308)], 5, INK, taper=.02, wmin=1, seed=11030, op=.85))
    rs = np.random.RandomState(7)
    for i in range(30):
        s.append(f'<circle cx="{rs.uniform(-100, 1180):.0f}" cy="{rs.uniform(1330, 1900):.0f}" r="{rs.uniform(2, 5):.1f}" fill="#b99358" opacity=".5"/>')
    return "".join(s)


def umbrella(t):
    """Пляжный зонт слева сверху: полосатый купол, жердь."""
    s = []
    x, y = 150, 560
    s.append(line([(x - 40, 1300), (x, y + 40)], 16, "#9a6a3c", taper=.02, wmin=1, seed=11050))
    s.append(line([(x - 40, 1300), (x, y + 40)], 5, "#c99562", taper=.02, wmin=1, seed=11051, op=.6))
    cols = ["#e9594f", "#fbf4e8"] * 3
    n = 6
    for i in range(n):
        a0 = math.radians(180 + 180 * i / n)
        a1 = math.radians(180 + 180 * (i + 1) / n)
        pts = [(x, y - 20), (x + 330 * math.cos(a0), y - 20 + 150 * math.sin(a0) + 80), (x + 330 * math.cos((a0 + a1) / 2), y - 20 + 168 * math.sin((a0 + a1) / 2) + 90),
               (x + 330 * math.cos(a1), y - 20 + 150 * math.sin(a1) + 80)]
        s.append(shape(pts, cols[i], "", w=5, seed=11060 + i))
    return "".join(s)


def deck_chair(t, cx, base):
    """Шезлонг, вид спереди: полосатая спинка, деревянные стойки и подлокотники, ножки на песке."""
    s = []
    W_ = 330
    top = base - 1150
    # тень на песке
    s.append(blob(ellipse_pts(cx, base + 24, 390, 30, 20), "#7b5a2c", .35, blur(8)))
    # задние стойки
    for sg in (-1, 1):
        s.append(line([(cx + sg * W_, top - 40), (cx + sg * (W_ + 30), base + 10)], 34, "#a86e3d", taper=.02, wmin=1, seed=11100 + sg))
        s.append(line([(cx + sg * W_ - 8 * sg, top - 40), (cx + sg * (W_ + 22), base)], 9, "#d09a62", taper=.02, wmin=1, seed=11103 + sg, op=.7))
    # полотно спинки (полосы)
    panel = [(cx - W_ + 6, top, 1), (cx + W_ - 6, top, 1), (cx + W_ + 4, top + 960, 1), (cx - W_ - 4, top + 960, 1)]
    stripes = []
    nstr = 9
    for i in range(nstr):
        x0 = cx - W_ + i * (2 * W_ / nstr)
        if i % 2 == 0:
            stripes.append(f'<rect x="{x0:.0f}" y="{top - 5}" width="{2 * W_ / nstr + 1:.0f}" height="900" fill="#e7f1f7" opacity=".95"/>')
        else:
            stripes.append(f'<rect x="{x0:.0f}" y="{top - 5}" width="{2 * W_ / nstr + 1:.0f}" height="900" fill="#e04b4b" opacity=".92"/>')
    stripes.append(f'<rect x="{cx - W_ - 5}" y="{top + 760}" width="{2 * W_ + 12}" height="260" fill="#6a3f1e" opacity=".14"/>')
    s.append(shape(panel, "#e7f1f7", "".join(stripes), w=6.2, seed=11110))
    # верхняя перекладина
    s.append(shape(rrect(cx - W_ - 40, top - 70, cx + W_ + 40, top - 6, 18), "#b9794a", blob(rrect(cx - W_ - 30, top - 66, cx + W_ + 30, top - 48, 8), "#e0a977", .6),
                   w=5.4, seed=11120))
    # передние ножки и перекладина
    for sg in (-1, 1):
        s.append(line([(cx + sg * (W_ - 40), base - 250), (cx + sg * (W_ + 70), base + 10)], 28, "#a86e3d", taper=.02, wmin=1, seed=11130 + sg))
    s.append(shape(rrect(cx - W_ - 20, base - 280, cx + W_ + 20, base - 238, 12), "#b9794a", "", w=5, seed=11140))
    return "".join(s)


def armrests(t, cx, base):
    s = []
    W_ = 330
    for sg in (-1, 1):
        x = cx + sg * (W_ + 8)
        s.append(shape(rrect(x - 26, base - 520, x + 26, base - 258, 14), "#b9794a", blob(rrect(x - 20, base - 516, x - 8, base - 262, 6), "#e0a977", .6),
                       w=5.2, seed=11150 + sg))
        s.append(shape(rrect(x - 52, base - 560, x + 52, base - 504, 20), "#c9884f", blob(rrect(x - 46, base - 556, x + 46, base - 538, 8), "#ecbf8c", .6),
                       w=5.2, seed=11154 + sg))
    return "".join(s)


def blanket_for(cx, base, breath, t):
    """Плед на коленях: клетка, свёрнутый край, бахрома по низу."""
    W_ = 330
    yt = base - 580
    edge = [(cx - 300, yt + 6), (cx - 160, yt + 56 - breath), (cx, yt + 74 - breath * 1.4), (cx + 160, yt + 52 - breath), (cx + 300, yt + 2)]
    body = edge + [(cx + 400, yt + 120, 1), (cx + 372, base - 220, 1), (cx + 280, base - 190), (cx - 280, base - 186), (cx - 372, base - 224, 1), (cx - 400, yt + 120, 1)]
    s = [plaid(body, "#cf5148", "#f0c892", "#7c2a2a", cx - 420, cx + 420, yt, base - 160, 52)]
    # складки
    for k, dx in enumerate((-190, -50, 120, 250)):
        s.append(line([(cx + dx, yt + 100 + 8 * k), (cx + dx + 12, yt + 250), (cx + dx - 6, yt + 400)], 3.4, "#7c2a2a", taper=.6, wmin=.2, seed=11200 + k, op=.45))
    # свёрнутый край пледа
    roll = [(cx - 310, yt - 8), (cx - 160, yt + 40 - breath), (cx, yt + 58 - breath * 1.4), (cx + 160, yt + 36 - breath), (cx + 310, yt - 12),
            (cx + 316, yt + 30), (cx + 160, yt + 80 - breath), (cx, yt + 100 - breath * 1.4), (cx - 160, yt + 84 - breath), (cx - 316, yt + 34)]
    s.append(shape(roll, "#e26c5e", blob([(cx - 300, yt + 2), (cx, yt + 40), (cx + 300, yt), (cx + 300, yt + 10), (cx, yt + 52), (cx - 300, yt + 14)], "#ffffff", .22),
                   w=5.4, seed=11210))
    # бахрома
    for i in range(14):
        x = cx - 270 + i * 41
        s.append(line([(x, base - 188), (x + 3, base - 150), (x - 3, base - 120)], 5.4, "#f0c892", taper=.5, wmin=.5, seed=11220 + i))
    return "".join(s)


def table_tea(t, x, base):
    """Столик и кружка чая, пар."""
    s = []
    top = base - 400
    s.append(blob(ellipse_pts(x, base + 20, 120, 14, 14), "#7b5a2c", .3, blur(5)))
    s.append(line([(x, top + 20), (x - 46, base + 6)], 15, "#a86e3d", taper=.02, wmin=1, seed=11400))
    s.append(line([(x, top + 20), (x + 46, base + 6)], 15, "#a86e3d", taper=.02, wmin=1, seed=11401))
    s.append(line([(x, top + 20), (x + 2, base + 6)], 12, "#b9794a", taper=.02, wmin=1, seed=11402))
    s.append(shape(ellipse_pts(x, top, 118, 22, 18), "#d79a62", blob(ellipse_pts(x - 20, top - 4, 78, 10, 12), "#f0c294", .6), w=5.4, seed=11410))
    # кружка
    mw, mh = 74, 100
    my = top - mh - 6
    mug = rrect(x - mw / 2, my, x + mw / 2, top - 6, 14)
    s.append(line([(x + mw / 2 - 4, my + 24), (x + mw / 2 + 40, my + 28), (x + mw / 2 + 40, my + 70), (x + mw / 2 - 4, my + 76)], 11, "#f5f1e6", taper=.1, wmin=.9, seed=11420))
    s.append(line([(x + mw / 2 - 4, my + 24), (x + mw / 2 + 40, my + 28), (x + mw / 2 + 40, my + 70), (x + mw / 2 - 4, my + 76)], 3.2, INK, taper=.1, wmin=.9, seed=11421))
    s.append(shape(mug, "#f5f1e6", blob(rrect(x - mw / 2, my + 40, x + mw / 2, my + 62), "#4aa8a0") + blob(rrect(x + mw / 2 - 18, my, x + mw / 2, top), "#d8d2c4", .7), w=5.4, seed=11422))
    s.append(blob(ellipse_pts(x, my + 4, mw / 2 - 5, 9, 14), "#a4592d"))
    s.append(steam(x, my - 2, t, 3, 11430))
    return "".join(s)


def check_mark(cx, cy, u, k=1.0):
    pts = [(cx - 60 * k, cy + 4 * k), (cx - 18 * k, cy + 48 * k), (cx + 70 * k, cy - 52 * k)]
    return line(partial(pts, u), 22 * k, "#2f9a4a", taper=.12, wmin=.7, seed=11500) + \
        line(partial([(cx - 58 * k, cy + 0), (cx - 18 * k, cy + 42 * k), (cx + 64 * k, cy - 48 * k)], u), 7 * k, "#7fd98c", taper=.2, wmin=.8, seed=11501, op=.8)


def frame11(t):
    t0 = 17.2
    u = clamp((t - t0) / 2.4)
    hit = t - T_OTDYH
    z = 1.04 + .17 * ease_io(u)
    set_ink(z)
    cxm = lerp(560, 540, ease_io(u)) + 7 * math.sin(t * 1.3)
    cym = lerp(1010, 930, ease_io(u)) + 5 * math.sin(t * 1.7)
    roll = 1.1 * math.sin(t * 1.1) + (-1.8 * smooth(T_OTDYH - .1, T_OTDYH + .35, t))
    base = 1560
    ecx, ecy, R = 540, 780, 225
    breath = 3.5 * math.sin(t * 2.0)
    # веко: полуприкрыт от удовольствия, на «глазам» приподнялось, на «отдых» закрылось
    openk = .62 + .06 * math.sin(t * 1.1)
    openk += .22 * smooth(T_VAZH - .1, T_VAZH + .2, t) * (1 - smooth(T_GLAZAM + .25, T_GLAZAM + .6, t))
    # медленное моргание
    for tb in (17.62, 18.33):
        openk -= .55 * bump(t, tb, .30)
    cl = smooth(T_OTDYH - .02, T_OTDYH + .26, t)
    openk = lerp(openk, 0.0, cl)
    # взгляд: на кружку (вправо-вниз) → на зрителя → закрыт
    lx = lerp(.85, .05, smooth(17.55, 18.1, t)) + .08 * math.sin(t * 1.9)
    ly = lerp(.35, .0, smooth(17.55, 18.1, t))
    brow = .5 * smooth(T_GLAZAM, T_GLAZAM + .3, t) * (1 - cl) + .6 * cl
    scn = [bg11(t), umbrella(t)]
    scn.append(deck_chair(t, ecx, base))
    scn.append(eye_creature(ecx, ecy + breath * .5, R, t, openk, (lx, ly), brow=brow))
    scn.append(blanket_for(ecx, base, breath, t))
    scn.append(armrests(t, ecx, base))
    scn.append(table_tea(t, 892, base - 20))
    # Z и галочка на «отдых»
    for i in range(3):
        ti = T_OTDYH + .08 + i * .24
        p = (t - ti) / 1.2
        if 0 < p < 1:
            x = ecx + 190 + 34 * i + 20 * math.sin(p * 4 + i)
            y = ecy - 300 - 90 * p - 50 * i
            sc = (.75 + .3 * i) * back_out(clamp(p * 4))
            scn.append(zzz(x, y, sc, "#4a63c0", 11600 + i * 4, op=clamp(1.4 - p) if p > .6 else 1))
    cu = clamp((t - (T_OTDYH + .22)) / .34)
    if cu > 0:
        sc = 1.35 * (1 + .12 * math.sin(clamp((t - T_OTDYH - .5) / .4) * math.pi))
        scn.append(check_mark(ecx - 240, ecy - 450, cu, sc * 1.1))
    if hit > 0 and hit < .5:   # мягкие искры довольства
        for i in range(6):
            a = i * math.pi / 3 + .3
            r0, r1 = 300 + 40 * hit * 2, 360 + 150 * hit * 2
            scn.append(line([(ecx + math.cos(a) * r0, ecy - 40 + math.sin(a) * r0 * .8), (ecx + math.cos(a) * r1, ecy - 40 + math.sin(a) * r1 * .8)],
                            8, "#ffd66b", taper=.6, wmin=.2, seed=11700 + i, op=1 - hit / .5))
    cam = lib.cam(cxm, cym, z, roll)
    return f'<g transform="{cam}">{"".join(scn)}</g>'


# ══════════════════════════════════════ общее для s09/s10: маленький Дима лёжа ══════════════════════════════════════
import people  # noqa: E402
import props  # noqa: E402

T_OTDYHAYUT = find("отдыхают", 12.5)     # 13.08
T_NEPRIYAT = find("неприятно", 13.5)     # 14.06
T_PROHODIT = find("проходит", 14.5)      # 14.86
T_VKL = find("включишь", 16.0)           # 16.53
T_SVET = find("свет", 16.8)              # 17.04


def kid_in_bed(hx, hy, scale, expr, rub=None, head_ang=0.0, rest_n=None, rest_f=None, lean=0.0, clip_y=1090.0):
    """Маленький Дима лежит в кровати, вид от изножья: голова на подушке (центр головы ≈ (hx, hy)), тело уходит под одеяло к зрителю.
    Руки поверх одеяла (rest_n/rest_f — куда лежат запястья), rub — ближняя рука несёт кулак к этой точке.
    Возвращает (тело, руки, info); одеяло кладёт сцена между ними."""
    sc = scale * people.HEIGHT["kid"]
    H = (hx - 24 * sc, hy + 560 * sc)
    arms = {"f": ("ang", 0.12, 0.1), "n": ("ang", -0.12, 0.1)} if rest_n is None else {"f": ("ik", rest_f, 1), "n": ("ik", rest_n, -1)}
    hands = {"n": dict(kind="open", curl=(.25, .3, .35, .4), thumb=.35, spread=.1), "f": dict(kind="open", curl=(.3, .35, .4, .45), thumb=.35, spread=.1)}
    if rub is not None:
        hands["n"] = dict(kind="open", curl=(.75, .8, .82, .85), thumb=.75, spread=.04)
    pose = dict(hip=H, scale=sc, lean=lean, feet=None, arms=arms, hands=hands, head_ang=head_ang, expr=expr, torso_k=1.0, hood=0.0,
                head_off=(0, 0), pelvis=False)
    o = people.draw(pose, "kid")
    hw = np.array(o["head"], float)
    hk = people.KID_HEAD_K * sc
    ang = lean * .5 + head_ang

    def hp(px, py):
        v = people.rot(np.array([px, py], float), ang)
        return (float(hw[0] + v[0] * hk), float(hw[1] + v[1] * hk))
    shut = expr.get("shut", 0.0)
    if shut > 0:
        C = people.PAL["kid"]
        g = []
        for (ex, ey, rx, ry), sd in ((people.K_EYE_F, 9050), (people.K_EYE_N, 9060)):
            g.append(blob(ellipse_pts(ex, ey, rx * 1.12, ry * 1.1, 16), C["SKIN"]))
            g.append(blob(ellipse_pts(ex, ey + ry * .25, rx * .95, ry * .55, 14), "#e0605c", .35 * expr.get("redeye", 0.0)))
            arc = [(ex - rx * .85, ey + ry * .05), (ex - rx * .3, ey + ry * .42), (ex + rx * .35, ey + ry * .42), (ex + rx * .85, ey + ry * .02)]
            g.append(people.line(arc, 5.6, INK, taper=.4, wmin=.35, seed=sd))
            for j, u in enumerate((-.55, -.15, .25, .62)):
                x0_ = ex + rx * u
                y0_ = ey + ry * (.42 - .55 * u * u)
                g.append(people.line([(x0_, y0_), (x0_ + u * 6, y0_ + 13)], 3.0, INK, taper=.8, wmin=.2, seed=sd + 2 + j))
        body_extra = f'<g transform="translate({hw[0]:.2f} {hw[1]:.2f}) rotate({math.degrees(ang):.3f}) scale({hk:.4f})">{"".join(g)}</g>'
    else:
        body_extra = ""
    info = dict(head=hp(10, -10), eye_n=hp(*people.K_EYE_N[:2]), eye_f=hp(*people.K_EYE_F[:2]), mouth=hp(66, 90), top=hp(0, -160), hk=hk)
    over = ""
    if rub is not None:      # предплечье выходит из-под одеяла (локоть под ним), кулак у глаза
        people.C = people.PAL["kid"]
        Wr = np.array(rub, float) / sc
        E = np.array((rub[0] - 70, clip_y + 230), float) / sc
        Sh = np.array((rub[0] + 60, clip_y + 520), float) / sc
        d = (Wr - E) / np.linalg.norm(Wr - E)
        arm = people.sleeve(Sh, E, Wr, False, 9070, "kid")
        arm += people.Hand.hand(Wr + d * 2, d, flip=-1, k=1.0, curl=(.8, .85, .88, .9), thumb=.8, spread=.03, bend=.1, seed=9080, nails=True, **people.hand_kw())
        cid = lib.clip_rect(-600, -600, 2400, 600 + clip_y)
        over = f'<g clip-path="url(#{cid})"><g transform="scale({sc:.5f})">{arm}</g></g>'
    return o["arm_f"] + o["body"] + body_extra + o["arm_n"], over, info


def quilt_front(x0, x1, ytop, yfront, ybot, seed=0, bodyk=1.0, breath=0.0, spread=60):
    """Одеяло на кровати, вид от изножья: верх — отворот у груди, бугор тела к зрителю, передняя свесь до низа."""
    c, csh, chi = props.C_QUILT, props.C_QUILT_SH, props.C_QUILT_HI
    cx = (x0 + x1) / 2
    W_ = x1 - x0
    top = [(x0 + 10, ytop + 20), (x0 + W_ * .2, ytop - 6 - breath), (cx, ytop - 14 - breath * 1.3), (x1 - W_ * .2, ytop - 6 - breath), (x1 - 10, ytop + 20)]
    pts = top + [(x1 + spread * .5, yfront, 1), (x1 + spread, ybot, 1), (x0 - spread, ybot, 1), (x0 - spread * .5, yfront, 1)]
    inner = blob([(x0 - spread * 1.2, yfront), (x1 + spread * 1.2, yfront), (x1 + spread * 1.2, ybot + 10), (x0 - spread * 1.2, ybot + 10)], csh)
    # бугор тела под одеялом
    inner += blob(ellipse_pts(cx + 6, (ytop + yfront) / 2 + 10, W_ * .26 * bodyk, (yfront - ytop) * .42, 16), chi, .55)
    for i in range(5):
        xx = x0 + W_ * (.12 + .19 * i)
        xb = cx + (xx - cx) * (1 + spread / W_ * 2)
        inner += line([(xx, ytop + 10), ((xx + xb) / 2, (ytop + yfront) / 2), (xb, yfront)], 7, props.C_QUILT_ST, taper=.2, wmin=.8, seed=seed + 20 + i, op=.85)
    for i in range(2):
        yy = ytop + (yfront - ytop) * (.38 + .3 * i)
        inner += line([(x0, yy + 10), (cx, yy - 12), (x1, yy + 10)], 3.2, csh, taper=.3, wmin=.5, seed=seed + 40 + i)
    inner += line([(x0 - spread * .5, yfront), (x1 + spread * .5, yfront)], 3.6, csh, taper=.2, wmin=.6, seed=seed + 50)
    o = shape(pts, c, inner, w=5.0, seed=seed)
    # белый отворот простыни у груди
    t2 = [(x0 + 4, ytop + 22), (x0 + W_ * .2, ytop - 2 - breath), (cx, ytop - 10 - breath * 1.3), (x1 - W_ * .2, ytop - 2 - breath), (x1 - 4, ytop + 22)]
    band_ = t2 + [(p[0], p[1] + 34) for p in t2[::-1]]
    o += shape(band_, "#f4ead6", blob([(p[0], p[1] + 22) for p in t2] + [(p[0], p[1] + 34) for p in t2[::-1]], "#dccdb0"), w=4.2, seed=seed + 5)
    return o


def pain_spikes(cx, cy, r, u, t, seed=0, col="#e0453c"):
    """Колючие штрихи боли вокруг глаза: зигзаги-лучи, дрожат."""
    if u <= .02:
        return ""
    o = []
    for i in range(7):
        a = -2.6 + i * .52 + .05 * math.sin(t * 9 + i)
        r0 = r * (1.05 + .06 * math.sin(t * 13 + i * 2))
        r1 = r0 + r * (.35 + .12 * (i % 2)) * u
        mid = (r0 + r1) / 2
        n = (-math.sin(a), math.cos(a))
        p0 = (cx + math.cos(a) * r0, cy + math.sin(a) * r0)
        pm = (cx + math.cos(a) * mid + n[0] * 12, cy + math.sin(a) * mid + n[1] * 12)
        p1 = (cx + math.cos(a) * r1, cy + math.sin(a) * r1)
        o.append(line([p0, pm, p1], 9, col, taper=.5, wmin=.25, seed=seed + i, op=min(1, u * 1.3)))
    return "".join(o)


def night_wall(x0, y0, x1, y1, seed=0):
    """Стена детской: светлые обои с ромбиками звёздочек (в цветах дня; ночь даёт вуаль)."""
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#c9d4ee"/>']
    rs = np.random.RandomState(5 + seed)
    for j in range(int((y1 - y0) / 150) + 1):
        for i in range(int((x1 - x0) / 150) + 1):
            x = x0 + i * 150 + (75 if j % 2 else 0) + rs.uniform(-10, 10)
            y = y0 + j * 150 + rs.uniform(-10, 10)
            o.append(props.star4(x, y, 13, 1.0).replace("#FFF3C4", "#e9eefb"))
    return "".join(o)


def zzz_rise(x, y, t, t_from, k=1.0, seed=0, n=3, period=1.1):
    o = []
    for i in range(n):
        ph = ((t - t_from) / period + i / n) % 1
        if t < t_from:
            ph = (i / n + (t - t_from) / period) % 1
        a = clamp(ph * 4) * clamp((1 - ph) * 3)
        xx = x + 60 * ph * k + 16 * math.sin(ph * 5 + i)
        yy = y - 200 * ph * k
        o.append(zzz(xx, yy, k * (.45 + .5 * ph), "#9fb3ff", seed + i * 4, op=a))
    return "".join(o)


# ══════════════════════════════════════ s09: Дима на подушке, глаза отдыхают ══════════════════════════════════════
def frame09(t):
    rel = t - 12.3
    # мимика по словам
    close = smooth(T_OTDYHAYUT - .02, T_OTDYHAYUT + .32, t)
    blink = bump(t, 12.62, .22)
    wince = smooth(T_NEPRIYAT - .08, T_NEPRIYAT + .14, t) * (1 - smooth(T_PROHODIT - .02, T_PROHODIT + .2, t))
    relief = smooth(T_PROHODIT, T_PROHODIT + .35, t)
    red = 1.0 - .45 * smooth(T_OTDYHAYUT, T_OTDYHAYUT + .8, t) - .55 * relief
    cc = max(blink, close)
    expr = {"lid": lerp(.22, -.35, clamp(cc / .6)), "shut": 1.0 if cc > .6 else 0.0, "look": (.15, -.25), "closed": 0.0, "redeye": clamp(red), "blush": .2 + .3 * relief,
            "brows": ("worry", "calm", clamp(.55 * close + .45 * relief)) if wince < .5 else "worry"}
    if wince > .5:
        expr["mouth"] = "wince"
        expr["brows"] = "worry"
    elif relief > .3:
        expr["mouth"] = "smile"
        expr["smile"] = relief
    else:
        expr["mouth"] = "flat"
    # потирает веко: ближняя рука поднимается к глазу, кулак ходит по кругу
    lift = smooth(T_NEPRIYAT - .24, T_NEPRIYAT + .06, t) * (1 - smooth(T_PROHODIT + .05, T_PROHODIT + .45, t))
    breath = 5 * math.sin(t * 2.4)
    hx, hy = 500.0, 760.0
    head_ang = -.16 - .06 * wince + .06 * relief + .02 * math.sin(t * 1.3)
    rest_n = rest_f = None
    _, _, inf0 = kid_in_bed(hx, hy, 2.0, dict(expr), None, head_ang, rest_n, rest_f)
    rub = None
    if lift > .001:
        ex, ey = inf0["eye_n"]
        ph = (t - T_NEPRIYAT) * 15
        tgt = (ex - 20 + 14 * math.cos(ph), ey + 95 + 10 * math.sin(ph))
        rub = (lerp(330, tgt[0], ease_io(lift)), lerp(1500, tgt[1], ease_io(lift)))
    body, arms_, inf = kid_in_bed(hx, hy, 2.0, expr, rub, head_ang, rest_n, rest_f)
    # камера: мягкий облёт лица
    z = 1.0 + .1 * ease_io(clamp(rel / 3.3))
    set_ink(z)
    cxm = 540 + 30 * math.cos(rel * 1.5) - 30 * ease_io(clamp(rel / 3.3))
    cym = 900 + 22 * math.sin(rel * 1.8) - 40 * ease_io(clamp(rel / 3.3))
    roll = -2.5 + 2.5 * ease_io(clamp(rel / 3.3)) + .7 * math.sin(rel * 1.3)
    scn = [night_wall(-400, -400, 1600, 700)]
    # изголовье кровати на стене, простыня
    scn.append(shape(rrect(-60, 160, 1140, 760, 60), props.C_WOOD, blob(rrect(-40, 180, 1120, 220, 14), props.C_WOOD_HI, .7) +
                     blob(rrect(-60, 640, 1140, 760, 10), props.C_WOOD_SH, .8), w=5.2, seed=9001))
    scn.append(shape([(-400, 600, 1), (1500, 600, 1), (1500, 2500, 1), (-400, 2500, 1)], "#eef0f6",
                     blob([(-400, 1700), (1500, 1700), (1500, 2500), (-400, 2500)], "#d3d8e6"), w=5.0, seed=9002))
    scn.append(blob(ellipse_pts(hx + 20, hy + 150, 470, 120, 18), "#9aa3bf", .45, blur(14)))
    scn.append(props.pillow(hx + 20, hy + 260, 5.2, -2.0, seed=1))
    scn.append(body)
    scn.append(quilt_front(60, 1020, 1075, 1720, 2300, seed=9100, breath=breath, spread=140))
    scn.append(arms_)
    # колючая боль вокруг глаз — тает на «проходит»
    pain = (1 - .35 * close) * (1 + .3 * bump(t, T_NEPRIYAT, .4)) * (1 - smooth(T_PROHODIT, T_PROHODIT + .45, t))
    for k_, key in enumerate(("eye_n", "eye_f")):
        ex, ey = inf[key]
        scn.append(pain_spikes(ex, ey, 105 if k_ == 0 else 85, clamp(pain), t, 9200 + 10 * k_))
    # выдох облегчения
    pu = clamp((t - T_PROHODIT - .05) / .7)
    if 0 < pu < 1:
        mx, my = inf["mouth"]
        for i in range(3):
            a = -1.15 + i * .28
            r0, r1 = 40 + 120 * pu, 90 + 170 * pu
            scn.append(line([(mx + math.cos(a) * r0, my + math.sin(a) * r0), (mx + math.cos(a + .08) * (r0 + r1) / 2, my + math.sin(a + .08) * (r0 + r1) / 2),
                             (mx + math.cos(a) * r1, my + math.sin(a) * r1)], 8, "#ffffff", taper=.6, wmin=.2, seed=9300 + i, op=.9 * (1 - pu)))
    # ночь: вуаль, лицо в лунном пятне
    scn.append(props.darkness(.5, "#0A0E26", holes=[(props.circle_d(hx + 20, hy + 120, 560, 520), .82)], blur_sd=90, box=(-500, -500, 1700, 2600)))
    scn.append(props.glow(hx - 200, hy - 360, 700, .35, "#b8c8ff"))
    cam = lib.cam(cxm, cym, z, roll)
    return f'<g transform="{cam}">{"".join(scn)}</g>'


# ══════════════════════════════════════ s10: спит, мама включает свет ══════════════════════════════════════
def pendant(x, y, on):
    """Потолочная лампа: шнур, колпак-колокол, лампочка."""
    o = [line([(x, -400), (x, y - 70)], 6, "#4a4458", taper=.02, wmin=1, seed=9500)]
    hc = mix(props.C_LAMP_SH, props.C_LAMP, clamp(on))
    o.append(shape([(x - 18, y - 74), (x + 18, y - 74), (x + 26, y - 50), (x - 26, y - 50)], props.C_METAL_SH, "", w=4, seed=9501))
    o.append(shape([(x - 26, y - 52, 1), (x - 74, y + 6), (x - 112, y + 40, 1), (x + 112, y + 40, 1), (x + 74, y + 6), (x + 26, y - 52, 1)], hc,
                   blob([(x + 30, y - 50), (x + 112, y + 40), (x + 70, y + 40), (x + 30, y - 20)], props.C_LAMP_SH, .5), w=5, seed=9502))
    o.append(shape(ellipse_pts(x, y + 52, 34, 26, 14), mix("#d8d0bc", props.C_LIGHT_HOT, clamp(on)), "", w=3.6, seed=9503))
    return "".join(o)


def doorway(t, light):
    x0, x1, y0, y1 = 712, 990, 470, 1200
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#f6d79a"/>']
    o.append(blob([(x0, y0), (x1, y0), (x1, y0 + 160), (x0, y0 + 60)], "#e8bd73", .7))
    o.append(blob([(x0, y1), (x1, y1), (x1 + 60, y1 + 120), (x0 - 120, y1 + 120)], "#f0c97e", .8))
    o.append(shape(rect_pts(x0 - 26, y0 - 26, x0, y1), "#e9e1d0", "", w=4.4, seed=9601))
    o.append(shape(rect_pts(x0 - 26, y0 - 26, x1 + 40, y0), "#e9e1d0", "", w=4.4, seed=9602))
    return "".join(o)


def rect_pts(x0, y0, x1, y1):
    return lib.rect_pts(x0, y0, x1, y1)


def frame10(t):
    rel = t - 15.2
    L = smooth(T_VKL + .04, T_VKL + .5, t)          # свет заливает комнату
    flash = bump(t, T_SVET - .04, .42)
    click = smooth(T_VKL - .03, T_VKL + .02, t)
    # камера: откат от спящего к общему плану
    u = ease_io(clamp((t - 15.22) / 1.25))
    z = lerp(1.9, 1.2, u) * (1 + .025 * flash)
    set_ink(z)
    cxm = lerp(380, 535, u) + 4 * math.sin(t * 1.4)
    cym = lerp(1020, 880, u) + 3 * math.sin(t * 1.9)
    roll = lerp(-3.0, 0.0, u) + .6 * math.sin(t * 1.1)
    floor_y = 1200
    scn = [night_wall(-500, -500, 1700, floor_y)]
    scn.append(f'<rect x="-500" y="{floor_y}" width="2200" height="1000" fill="#c79a6a"/>')
    for i in range(10):
        yy = floor_y + 40 + i * 62 + i * i * 4
        scn.append(line([(-500, yy), (1700, yy)], 3, "#a57a4e", taper=.05, wmin=.8, seed=9700 + i, op=.6))
    scn.append(shape(rrect(-500, floor_y - 30, 1700, floor_y + 2, 4), "#efe6d4", "", w=4, seed=9711))
    scn.append(shape(ellipse_pts(420, 1560, 400, 100, 22), "#7fae9a", blob(ellipse_pts(420, 1560, 330, 72, 20), "#a5cdb9"), w=4.4, seed=9720))
    scn.append(props.book_closed(640, 1600, 1.3, -12))
    scn.append(props.window(200, 760, 300, 400, "night", t, seed=3))
    scn.append(doorway(t, L))
    # мама в проёме: живое лицо, щёлкает выключателем
    sw = (676, 840)
    blink = bump(t, 15.85, .2) + bump(t, 17.3, .2)
    reach = smooth(T_VKL - .45, T_VKL - .12, t)
    mexpr = {"mouth": "smile", "smile": .55 + .45 * L, "lid": lerp(.6 + .2 * L, -.2, clamp(blink)), "brows": "calm" if L < .5 else "up",
             "look": (.4, .3 - .25 * L)}
    mx, mscale = 838.0, 0.56
    sc = mscale * people.HEIGHT["mama"]
    my = floor_y - 606 * sc
    finger = (sw[0] + 6, sw[1] + (6 if click > .5 else -10))
    tgt = (lerp(2 * mx - 830, 2 * mx - (finger[0] + 58), reach), lerp(my + 60, finger[1] + 14, reach))
    m = people.figure("mama", mx, my, mscale, mexpr, lean=-.05 * reach, head_ang=-.05,
                      arms={"n": ("ik", tgt, -1), "f": ("ang", .1, .2)},
                      hands={"n": dict(kind="open", curl=(0.0, .85, .88, .9), thumb=.75, spread=.05,
                                       dir=(lerp(.1, 1.0, reach), lerp(1.0, -.25, reach)))},
                      feet={"n": ((mx + 40 * sc, floor_y), 0.0), "f": ((mx - 50 * sc, floor_y - 4), 0.0)}, flip=True)
    scn.append(blob(ellipse_pts(mx - 10, floor_y + 8, 120, 16, 14), "#6b4a2a", .35, blur(6)))
    scn.append(props.wall_switch(sw[0], sw[1], 1.0, click))
    scn.append(m["svg"])
    # кровать от изножья: изголовье на стене, подушка, спящий, одеяло
    bx = 375
    scn.append(blob(ellipse_pts(bx, 1400, 360, 32, 18), "#4a3424", .45, blur(8)))
    scn.append(shape(rrect(bx - 300, 820, bx + 300, 1160, 44), props.C_WOOD, blob(rrect(bx - 286, 832, bx + 286, 862, 10), props.C_WOOD_HI, .7), w=5, seed=9730))
    for sg in (-1, 1):
        scn.append(shape(rrect(bx + sg * 310 - 24, 1290, bx + sg * 310 + 24, 1400, 8), props.C_WOOD_SH, "", w=4, seed=9735 + sg))
    scn.append(shape(rrect(bx - 290, 1040, bx + 290, 1190, 22), "#eef0f6", "", w=4.4, seed=9740))
    wake = smooth(T_SVET - .1, T_SVET + .3, t)
    kexpr = {"shut": 1.0 if wake < .5 else 0.0, "lid": .62, "look": (.2, -.6), "mouth": "smile", "smile": .5 + .5 * wake,
             "brows": "sleepy" if wake < .5 else "up", "blush": .5}
    breath = 3 * math.sin(t * 2.2)
    scn.append(props.pillow(bx - 10, 1076, 2.7, -2.0, seed=4))
    body, over, inf = kid_in_bed(bx - 6, 980 - breath * .3, 0.74, kexpr, None, -.12 + .08 * wake, clip_y=1100)
    scn.append(body)
    scn.append(quilt_front(bx - 280, bx + 280, 1090, 1300, 1385, seed=9800, breath=breath, spread=56))
    # спящие Z до света; на свету исчезают
    zop = 1 - smooth(T_VKL + .05, T_VKL + .3, t)
    if zop > .01:
        hx, hy = inf["top"]
        scn.append(f'<g opacity="{zop:.3f}">{zzz_rise(hx + 70, hy, t, 15.0, .8, 9900)}</g>')
    lx, ly = 470, 330
    scn.append(pendant(lx, ly, L))
    # свет: вуаль ночи с «дырой», которая растёт от лампы, — комната заливается тёплым светом
    r = 60 + 2600 * ease_out(L, 2)
    veil = .66 * (1 - .92 * L)
    holes = [(props.circle_d(200, 560, 170, 230), .55 * (1 - L)), ("M712 470H990V1310H600Z", .62 * (1 - L))]
    if L > 0:
        holes.append((props.circle_d(lx, ly + 60, r, r * .9), 1.0))
    scn.append(props.darkness(veil, "#0A0E26", holes=holes, blur_sd=40 + 120 * L, box=(-500, -500, 1700, 2400)))
    scn.append(props.glow(lx, ly + 60, 420 + 700 * L, clamp(L * .8 + .6 * flash), props.C_LIGHT))
    if L > .01:
        scn.append(props.glow(lx, ly + 52, 120 + 80 * flash, clamp(L + flash), props.C_LIGHT_HOT))
    # лучи на «свет»
    fr = clamp((t - (T_SVET - .06)) / .55)
    if 0 < fr < 1:
        for i in range(12):
            a = math.radians(15 + i * 13.6)
            r0, r1 = 110 + 160 * fr, 190 + 420 * ease_out(fr)
            scn.append(line([(lx + math.cos(a) * r0, ly + 60 + math.sin(a) * r0), (lx + math.cos(a) * r1, ly + 60 + math.sin(a) * r1)], 14, "#ffe9a8",
                            taper=.6, wmin=.2, seed=9950 + i, op=.95 * (1 - fr) ** .7))
    cam = lib.cam(cxm, cym, z, roll)
    return f'<g transform="{cam}">{"".join(scn)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    body = {"s09": frame09, "s10": frame10, "s11": frame11}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#f7e3bd"/>{body}')
