"""Рилс 55 s12 (27.6–29.3, клип 27.4–29.5): мозг крупно, вокруг него разомкнутое золотое кольцо-петля; концы тянутся друг к другу
(на «хочет», «его»), на «закрыть» (28.72) защёлкиваются, вспышка, искры, мозг светлеет и подпрыгивает."""
import math

import brain_art as ba
import lib
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
SNAP = 28.72
CX, CY = 540.0, 840.0
R = 350.0
BS = 1.12


def background(t):
    s = []
    g = lin_grad([(0, "#1f2747", 1), (.6, "#2c3a66", 1), (1, "#33457a", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="3000" height="3800" fill="url(#{g})"/>')
    g2 = rad_grad([(0, "#6276b8", .9), (.6, "#40538d", .35), (1, "#40538d", 0)], CX, CY, 760, 700)
    s.append(f'<rect x="-900" y="-900" width="3000" height="3800" fill="url(#{g2})"/>')
    return "".join(s)


def gap(t):
    if t < SNAP:
        u = clamp((t - 27.4) / (SNAP - 27.4))
        return 78 - 46 * u ** 1.4 + (1.5 + 3 * u) * math.sin(t * 25)
    e = t - SNAP
    return max(0.0, 32 * (1 - ease_out(clamp(e / 0.07), 2)))


def ends(t):
    """Концы кольца: углы (рад) левого и правого конца, щель наверху (−90°)."""
    g = math.radians(gap(t))
    return -math.pi / 2 - g / 2, -math.pi / 2 + g / 2


def ring(t):
    a_l, a_r = ends(t)
    # кольцо идёт от правого конца по часовой на 2π − щель до левого
    span = 2 * math.pi - (a_r - a_l)
    pts = []
    n = 90
    wob = 6 * math.sin(t * 9) * (1 - smooth(SNAP, SNAP + .3, t))
    for i in range(n + 1):
        a = a_r + span * i / n
        rr = R + wob * math.sin(a * 3 + t * 7) + (10 * math.exp(-max(t - SNAP, 0) * 7) * math.sin((t - SNAP) * 30) if t > SNAP else 0)
        pts.append((CX + rr * math.cos(a), CY + 0.96 * rr * math.sin(a)))
    s = [line(pts, 52, INK, taper=0, wmin=1, seed=810), line(pts, 38, "#f0b43c", taper=0, wmin=1, seed=811),
         line(pts[3:-3], 9, "#fff0b0", taper=.1, wmin=.5, seed=812)]
    return s, pts


def clasps(t, pts):
    """Шарик на правом конце и чашка на левом (в замкнутом виде шарик внутри чашки)."""
    a_l, a_r = ends(t)
    s = []
    pr = pts[0]
    pl = pts[-1]
    # чашка (левый конец): U-образная скоба, раскрыта в сторону щели
    ang_l = math.degrees(a_l + math.pi / 2)
    s.append(f'<g transform="translate({f(pl[0])} {f(pl[1])}) rotate({f(ang_l + 90)})">' +
             shape([(-30, -14, 1), (30, -14, 1), (30, 34, 1), (-30, 34, 1)], "#f6c85a", blob(rect_pts(-30, 18, 30, 34), "#d89a2a"), w=4.4, seed=820) +
             shape([(-17, -14, 1), (17, -14, 1), (17, 20, 1), (-17, 20, 1)], "#3a2a10", "", w=3, seed=821) + "</g>")
    ang_r = math.degrees(a_r + math.pi / 2)
    s.append(f'<g transform="translate({f(pr[0])} {f(pr[1])}) rotate({f(ang_r - 90)})">' +
             shape(ellipse_pts(0, 8, 26, 26, 14), "#ffe27a", blob(ellipse_pts(8, 16, 14, 12, 10), "#e8b83c"), w=4.4, seed=822) + "</g>")
    return s


def flash(t):
    e = t - SNAP
    if not 0 <= e < 0.7:
        return ""
    k = e / 0.7
    x, y = CX, CY - R
    s = []
    g = rad_grad([(0, "#fffbe0", min(1, 1.1 * (1 - k))), (.5, "#ffe58a", .5 * (1 - k)), (1, "#ffe58a", 0)], x, y, 260 + 200 * k, 260 + 200 * k)
    s.append(f'<rect x="{x - 700}" y="{y - 700}" width="1400" height="1400" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    # кольцо-волна по кадру
    s.append(f'<circle cx="{CX}" cy="{CY}" r="{R * (0.7 + 0.9 * ease_out(k))}" fill="none" stroke="#fff6c8" stroke-width="{16 * (1 - k) + 1}"/>')
    for j in range(14):
        a = math.radians(j * 360 / 14 + 8)
        r0, r1 = 50 + 120 * k, 110 + 280 * k
        s.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))],
                      13 * (1 - k) + 1.5, "#ffe58a", taper=.6, seed=830 + j))
    return "".join(s)


def stars(t):
    e = t - SNAP - 0.1
    if e < 0:
        return ""
    s = []
    for j in range(6):
        a = j * math.pi / 3 + 0.4
        k = back_out(clamp((e - j * 0.04) / 0.25), 2) * (1 - smooth(0.6, 1.0, e))
        if k <= 0.02:
            continue
        x = CX + (R + 70) * math.cos(a) * (1 + 0.2 * e)
        y = CY + (R + 70) * math.sin(a) * (1 + 0.2 * e)
        pts = []
        for i in range(10):
            r = 34 if i % 2 == 0 else 13
            aa = -math.pi / 2 + i * math.pi / 5
            pts.append((x + r * k * math.cos(aa), y + r * k * math.sin(aa), 1))
        s.append(shape(pts, "#ffe27a", "", w=3.2, seed=840 + j))
    return "".join(s)


def brain(t):
    sad = 0.65 * (1 - smooth(SNAP - 0.15, SNAP + 0.1, t)) + 0.0
    e = t - SNAP
    pop = 1.0
    if e > 0:
        pop = 1 + 0.09 * math.exp(-e * 8) * math.cos(e * 24)
    else:
        pop = 1 + 0.012 * math.sin(t * 7)
    glow = ""
    if e > 0:
        g = rad_grad([(0, "#ffd7a0", .6 * math.exp(-e * 1.2)), (1, "#ffd7a0", 0)], CX, CY, 420, 380)
        glow = f'<rect x="{CX - 500}" y="{CY - 500}" width="1000" height="1000" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    return glow + f'<g transform="translate({CX} {CY}) scale({BS * pop:.4f}) translate({-ba.BCX} {-ba.BCY})">{ba.brain(t, sad, stem=False)}</g>'


def camera(t):
    u = clamp((t - 27.4) / 2.1)
    sc = 1.12 + 0.20 * ease_io(u) + 0.06 * (1 - ease_out(clamp((t - 27.4) / 0.4)))
    rot = -1.5 * (1 - u) + 0.6 * math.sin(t * 1.4)
    ccx, ccy = CX, CY - 40 * u
    e = t - SNAP
    if e > 0:
        k = math.exp(-e * 6)
        sc *= 1 + 0.08 * k
        ccy += 16 * k * math.sin(e * 36)
        rot += 3.0 * k * math.sin(e * 24)
    return cam(ccx, ccy, sc, rot)


def frame(sid, t):
    lib.dyn_begin()
    r, pts = ring(t)
    s = [background(t)] + r + [brain(t)] + clasps(t, pts) + [flash(t), stars(t)]
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{camera(t)}">{"".join(s)}</g>')
