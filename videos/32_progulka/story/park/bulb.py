"""Большая лампочка-идея над головой: стекло-груша, цоколь с резьбой, нить; горит с лучами-штрихами вокруг."""
import math

import lib
from lib import INK, blob, ellipse_pts, line, shape


def draw(x, y, r, lit, rays, t):
    """(x, y) — центр колбы, r — радиус; lit 0..1 — накал; rays 0..1 — длина лучей."""
    o = []
    if lit > 0:
        g = lib.rad_grad([(0, "#fff6b8", .95 * lit), (.35, "#ffe36a", .55 * lit), (1, "#ffd24a", 0)], x, y, r * (2.6 + 1.2 * rays))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * (2.6 + 1.2 * rays):.1f}" fill="url(#{g})"/>')
    if rays > 0:
        n = 12
        for k in range(n):
            a = k * 2 * math.pi / n + 0.12 + 0.03 * math.sin(t * 9 + k)
            if 0.35 * math.pi < a % (2 * math.pi) < 0.65 * math.pi:
                continue           # вниз, к голове, лучей нет
            L0 = r * 1.28
            L1 = r * (1.28 + (0.55 + 0.18 * (k % 2)) * rays + 0.05 * math.sin(t * 13 + k * 2))
            p0 = (x + L0 * math.cos(a), y + L0 * math.sin(a))
            p1 = (x + L1 * math.cos(a), y + L1 * math.sin(a))
            o.append(line([p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), p1], r * .16, "#f2a81e", taper=.7, wmin=.25, seed=3100 + k))
    # колба: груша, сужается к цоколю
    glass = []
    for k in range(25):
        a = math.radians(-215 + k * (250 / 24))
        glass.append((x + r * math.cos(a), y + r * math.sin(a)))
    glass = [(x - r * .46, y + r * 1.18)] + glass + [(x + r * .46, y + r * 1.18)]
    col = lib.mix("#e9eef2", "#ffe45a", lit)
    inner = blob(ellipse_pts(x + r * .25, y + r * .25, r * .7, r * .8, 14), lib.mix("#c9d3db", "#ffc93a", lit), .8)
    inner += blob(ellipse_pts(x - r * .42, y - r * .38, r * .18, r * .32, 10, rot=30), "#ffffff", .85)
    # нить
    fil = [(x - r * .3, y + r * 1.1), (x - r * .26, y + r * .2), (x - r * .14, y - r * .08), (x, y + r * .08), (x + r * .14, y - r * .08),
           (x + r * .26, y + r * .2), (x + r * .3, y + r * 1.1)]
    inner += line(fil, r * .05, lib.mix("#7a6a50", "#fff8d8", lit), taper=.1, wmin=.6, seed=3150)
    if lit > .3:
        inner += line(fil[1:-1], r * .12, "#ffffff", taper=.1, wmin=.6, seed=3151, op=.6 * lit)
    o.append(shape(glass, col, inner, w=r * .075, seed=3160))
    # цоколь
    yb = y + r * 1.12
    for k in range(3):
        yy = yb + k * r * .17
        o.append(shape(lib.rect_pts(x - r * .5, yy, x + r * .5, yy + r * .2, r * .07), "#a9adb5",
                       blob(lib.rect_pts(x + r * .1, yy, x + r * .5, yy + r * .2), "#7d818c", .9), w=r * .05, seed=3170 + k))
    o.append(shape([(x - r * .3, yb + r * .52), (x + r * .3, yb + r * .52), (x + r * .14, yb + r * .7), (x - r * .14, yb + r * .7)], "#3d3f48",
                   w=r * .05, seed=3180))
    return "".join(o)


_ = INK
