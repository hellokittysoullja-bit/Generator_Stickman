"""Мозг рилса 24 (рилс 32: stem=False — без ствола, вместо него ножки) (сбоку, объём, извилины) — рисуется вокруг (BCX, BCY); сцена ставит его трансформом."""
import math

import numpy as np

from lib import blob, ellipse_pts, line, mix, shape

BCX, BCY = 400, 600


# ───────────────────────── мозг
def brain_outline():
    pts = []
    rs = np.random.RandomState(7)
    ph = rs.uniform(0, 6.28, 3)
    n = 44
    for i in range(n):
        a = 2 * math.pi * i / n
        rx, ry = 215, 150
        # чуть приплюснутый низ, лобная доля вперёд (влево)
        r = 1 + 0.035 * math.sin(9 * a + ph[0]) + 0.02 * math.sin(14 * a + ph[1])
        x = math.cos(a) * rx * r
        y = math.sin(a) * ry * r
        if y > 0:
            y *= 0.82
            x *= 1 - 0.08 * math.sin(a)
        if x < 0 and y < 0:
            x *= 1.04
        pts.append((BCX + x, BCY + y))
    return pts


CBL = [(BCX + 70, BCY + 100), (BCX + 150, BCY + 82), (BCX + 205, BCY + 110), (BCX + 200, BCY + 150), (BCX + 150, BCY + 170),
       (BCX + 90, BCY + 160), (BCX + 60, BCY + 130)]
STEM = [(BCX + 40, BCY + 110), (BCX + 100, BCY + 118), (BCX + 92, BCY + 200), (BCX + 82, BCY + 270, 1), (BCX + 40, BCY + 270, 1),
        (BCX + 48, BCY + 190)]


def gyri():
    """Извилины: петляющие борозды (меандр вдоль контура доли, концы загнуты крючком) — тёмная линия + светлая кромка."""
    rs = np.random.RandomState(12)
    s = []
    seeds = []
    for ring, (rx, ry, n) in enumerate([(178, 118, 9), (128, 82, 7), (76, 46, 4)]):
        a0 = rs.uniform(0, 6.28)
        for k in range(n):
            seeds.append((ring, rx, ry, a0 + 2 * math.pi * k / n + rs.uniform(-.15, .15)))
    for j, (ring, rx, ry, a) in enumerate(seeds):
        span = rs.uniform(0.38, 0.62) * (1.0 if ring < 2 else 1.3)
        amp = rs.uniform(7, 12)
        m = 18
        pts = []
        for i in range(m + 1):
            u = i / m
            aa = a + span * u
            w = amp * math.sin(u * math.pi * rs.uniform(2.2, 3.2) + j)
            rr = 1 + w / max(rx, 1)
            x, y = math.cos(aa) * rx * rr, math.sin(aa) * ry * rr
            if y > 0:
                y *= 0.85
            pts.append((BCX + x, BCY + y))
        # крючок на конце — внутрь
        ex, ey = pts[-1]
        ix, iy = BCX - ex, BCY - ey
        L = math.hypot(ix, iy) + 1e-6
        pts.append((ex + ix / L * 18 + rs.uniform(-6, 6), ey + iy / L * 18))
        s.append(line([(x + 1.5, y + 4) for x, y in pts], 4.0, "#ffdbe4", seed=200 + j, op=.6, taper=.6))
        s.append(line(pts, 5.4, "#a8466b", seed=300 + j, taper=.7, wmin=.15))
    # латеральная (сильвиева) борозда
    s.append(line([(BCX - 120, BCY + 60), (BCX - 40, BCY + 28), (BCX + 40, BCY + 22), (BCX + 110, BCY - 6)], 6.5, "#8e3358", seed=401))
    # центральная борозда сверху вниз
    s.append(line([(BCX + 10, BCY - 148), (BCX - 6, BCY - 90), (BCX + 14, BCY - 40), (BCX + 2, BCY + 10)], 5.5, "#8e3358", seed=402))
    return "".join(s)


def brain(t, sad, stem=True):
    s = []
    base = mix("#f6a9bc", "#c99aac", sad)
    shc = mix("#dd7e9b", "#a87a8d", sad)
    deep = mix("#b9587d", "#8b6276", sad)
    hi = mix("#ffd7e1", "#e4ccd6", sad)
    # стебель и мозжечок — сзади
    if stem:
        s.append(shape(STEM, mix("#e98fa8", "#b88c9c", sad),
                       blob([(BCX + 70, BCY + 112), (BCX + 100, BCY + 118), (BCX + 92, BCY + 200), (BCX + 82, BCY + 270), (BCX + 66, BCY + 270)], shc, .9),
                       w=4.6, seed=51))
    cb_inner = blob([(BCX + 90, BCY + 140), (BCX + 200, BCY + 130), (BCX + 200, BCY + 150), (BCX + 150, BCY + 170), (BCX + 90, BCY + 160)], deep, .55)
    for k in range(4):
        y = BCY + 105 + k * 16
        cb_inner += line([(BCX + 75 + k * 6, y), (BCX + 140, y - 6 + k * 2), (BCX + 198 - k * 4, y + 4 + k * 3)], 3.4, deep, seed=60 + k)
    s.append(shape(CBL, mix("#ef9bb0", "#bf93a3", sad), cb_inner, w=4.6, seed=52))
    # большие полушария
    pts = brain_outline()
    inner = []
    inner.append(blob([(BCX - 240, BCY + 30), (BCX - 60, BCY + 90), (BCX + 120, BCY + 40), (BCX + 240, BCY - 40),
                       (BCX + 240, BCY + 200), (BCX - 240, BCY + 200)], shc, .95))
    inner.append(blob([(BCX - 200, BCY + 120), (BCX + 60, BCY + 140), (BCX + 240, BCY + 60), (BCX + 240, BCY + 200),
                       (BCX - 200, BCY + 200)], deep, .55))
    inner.append(blob(ellipse_pts(BCX - 90, BCY - 85, 95, 42, 14, rot=-14), hi, .8))
    inner.append(gyri())
    inner.append(blob(ellipse_pts(BCX - 120, BCY - 98, 34, 13, 10, rot=-22), "#ffffff", .75))
    s.append(shape(pts, base, "".join(inner), w=6.2, seed=53))
    return "".join(s)


