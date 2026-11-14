"""Мозг рилса 38 (сцена mind, s07): мозг рилсов 24–32 (brain_art), ручки и кисти из scene_brain рилса 32, лицо (большие
белые глаза с маленькими зрачками) из scene_brain32 рилса 32 — перенесены как есть; добавлены прищур (squint) и печать."""
import math

import numpy as np

import lib
from brain_art import BCX, BCY
from lib import INK, band, blob, clamp, ellipse_pts, f, line, shape

SKIN, SKIN_SH, SKIN_HI = "#f4a6bb", "#d97f9c", "#ffd3de"
EYE_L, EYE_R = (BCX - 116, BCY + 14), (BCX - 30, BCY + 6)


class Pose:
    """Где мозг: центр (x, y), масштаб, поворот, сплющивание."""
    def __init__(self, x, y, sc=1.0, rot=0.0, sq=1.0):
        self.x, self.y, self.sc, self.rot, self.sq = x, y, sc, rot, sq

    def tf(self):
        return (f"translate({f(self.x)} {f(self.y)}) rotate({f(self.rot)}) scale({f(self.sc / self.sq ** .5)} {f(self.sc * self.sq)}) "
                f"translate({-BCX} {-BCY})")

    def pt(self, lx, ly):
        x, y = (lx - BCX) * self.sc / self.sq ** .5, (ly - BCY) * self.sc * self.sq
        a = math.radians(self.rot)
        return (self.x + x * math.cos(a) - y * math.sin(a), self.y + x * math.sin(a) + y * math.cos(a))


SH_L = (BCX - 140, BCY + 92)
SH_R = (BCX + 128, BCY + 96)


def arm(S, Wr, bend, sd, sc=1.0):
    """Ручка-«лапша» от плеча S до запястья Wr; bend — выгиб локтя (px, + наружу вправо от направления)."""
    dx, dy = Wr[0] - S[0], Wr[1] - S[1]
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    C = ((S[0] + Wr[0]) / 2 + nx * bend, (S[1] + Wr[1]) / 2 + ny * bend)
    pts = [((1 - u) ** 2 * S[0] + 2 * (1 - u) * u * C[0] + u * u * Wr[0], (1 - u) ** 2 * S[1] + 2 * (1 - u) * u * C[1] + u * u * Wr[1])
           for u in np.linspace(0, 1, 9)]
    pl = band(pts, 26 * sc, 20 * sc, step=5, cap=False)
    sh = band([(x + 5 * sc, y + 3 * sc) for x, y in pts], 10 * sc, 8 * sc, step=5, cap=False)
    return shape(pl, SKIN, blob(sh, SKIN_SH, .85), w=3.6 * sc, seed=sd)


def sausage(pts, w0, w1, n=24):
    """Контур пальца: гладкая средняя линия, толщина w0 → w1, кончик — полукруг (без острия)."""
    S = lib.sample(pts, False, 2.0)
    T = np.gradient(S, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    Wd = np.linspace(w0, w1, len(S))[:, None] / 2
    L, R = S + N * Wd, S - N * Wd
    end, tn, nn = S[-1], T[-1], N[-1]
    r = w1 / 2
    cap = [tuple(end + nn * r * math.cos(a) + tn * r * math.sin(a)) for a in np.linspace(0, math.pi, 9)[1:-1]]
    step = max(1, len(S) // 8)
    out = [tuple(p) for p in L[::step]] + [tuple(L[-1])] + cap + [tuple(R[-1])] + [tuple(p) for p in R[::-step]]
    return out


def finger(base, ang, L, wd, curl, sd):
    pts = [base]
    a = ang
    seg = L / 3
    x, y = base
    for k in range(3):
        a += curl * 30
        x += seg * math.cos(math.radians(a))
        y += seg * math.sin(math.radians(a))
        pts.append((x, y))
    pl = sausage(pts, wd, wd * .92)
    return shape(pl, SKIN, "", w=3.0, seed=sd)


def toon_hand(x, y, ang, curl=0.0, sd=0, sc=1.0, spread=1.0):
    """Мультяшная кисть: ладонь, три пальца и большой (четыре пальца), запястье в (x, y), пальцы вдоль ang.
    Большой палец всегда сверху. curl 0..1 — пальцы сжимаются (хват)."""
    flip = math.cos(math.radians(ang)) < 0
    a = ang if not flip else ang
    s = []
    palm = [(-6, -13), (14, -22), (36, -22), (50, -10), (52, 6), (42, 19), (18, 22), (-6, 12)]
    inner = blob([(-6, 6), (16, 13), (40, 11), (52, 6), (42, 19), (18, 22), (-6, 12)], SKIN_SH, .85)
    fs = []
    for k, (bx, by, fa, L) in enumerate([(46, -14, -14 * spread, 34), (50, -1, 0, 38), (46, 12, 14 * spread, 33)]):
        fs.append(finger((bx, by), fa, L, 15, curl, sd + 10 + k))
    thumb = finger((22, -18), -62 + 30 * curl, 26, 15, curl * 0.8, sd + 20)
    s.append(thumb)
    s.append(shape(palm, SKIN, inner, w=3.4, seed=sd + 1))
    s += fs
    sy = -1 if flip else 1
    rot = a if not flip else a - 180
    sx = -1 if flip else 1
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc * sx)} {f(sc)})">{"".join(s)}</g>'


def face(awake, look=(0.0, 0.0), mouth="snore", t=0.0, brow=0.0, blink=0.0):
    """awake 0 — спит (дуги), 1 — глаза открыты. blink — веко опускается на открытый глаз."""
    s = []
    if awake < 0.5:
        for k, (x, y) in enumerate((EYE_L, EYE_R)):
            s.append(line([(x - 26, y + 2), (x - 10, y + 12), (x + 10, y + 12), (x + 26, y + 2)], 6.5, INK, taper=.4, wmin=.35, seed=880 + k))
            s.append(line([(x - 18, y + 14), (x - 22, y + 22)], 2.6, INK, taper=.5, seed=884 + k))
    else:
        op = clamp((awake - 0.5) / 0.08)
        ry = 36 * (0.55 + 0.45 * op)
        for k, (x, y) in enumerate((EYE_L, EYE_R)):
            e = ellipse_pts(x, y, 29, ry, 18)
            px, py = x + look[0] * 10, y + look[1] * 12
            inner = f'<circle cx="{f(px)}" cy="{f(py)}" r="9.5" fill="{INK}"/><circle cx="{f(px - 3)}" cy="{f(py - 3.5)}" r="3" fill="#ffffff"/>'
            if blink > 0.02:
                yb = y - ry - 2 + (2 * ry + 4) * blink
                inner += f'<rect x="{x - 32}" y="{y - ry - 4}" width="64" height="{f(yb - (y - ry - 4))}" fill="#f6a9bc"/>'
                inner += line([(x - 30, yb), (x, yb + 3), (x + 30, yb)], 4, INK, seed=890 + k)
            s.append(shape(e, "#ffffff", inner, w=4.4, seed=886 + k))
            if brow:
                by = y - ry - 16 - 8 * brow
                s.append(line([(x - 22, by + 4), (x, by - 4 * brow), (x + 20, by + 2)], 5.5, "#8e3358", taper=.4, wmin=.4, seed=892 + k))
    mx, my = BCX - 72, BCY + 74
    if mouth == "snore":
        r = 7 + 3 * math.sin(t * 2.6)
        s.append(shape(ellipse_pts(mx, my, r * .9, r, 12), "#7a2a40", "", w=3, seed=895))
    elif mouth == "o":
        s.append(shape(ellipse_pts(mx, my, 14, 18, 14), "#7a2a40", blob(ellipse_pts(mx, my + 8, 8, 6, 10), "#e2543f"), w=3.4, seed=895))
    else:          # улыбка с открытым ртом
        pts = [(mx - 30, my - 8, 1), (mx + 30, my - 10, 1), (mx + 20, my + 12), (mx, my + 20), (mx - 20, my + 12)]
        s.append(shape(pts, "#7a2a40", blob([(mx - 14, my + 8), (mx + 14, my + 6), (mx + 8, my + 18), (mx - 8, my + 18)], "#e2543f"), w=3.6, seed=895))
    # румянец
    s.append(blob(ellipse_pts(BCX - 160, BCY + 56, 20, 10, 10), "#f07a98", .55))
    return "".join(s)


