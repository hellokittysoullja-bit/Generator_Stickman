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


def frame(sid, t):
    lib.dyn_begin()
    body = {"s11": frame11}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#f7e3bd"/>{body}')
