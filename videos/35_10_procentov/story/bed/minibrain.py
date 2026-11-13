"""Маленький мозг-персонаж для сцен sub и bed рилса 35: мозг рилсов 24–32 (brain_art, без ствола), лицо как в
scene_brain32 (большие белые глаза, маленькие зрачки), ручки-«лапша» с мультяшными кистями (scene_brain рилса 32).
Огоньки — светящиеся точки на извилинах (мозг «работает»). Рисуется в локальных координатах мозга (BCX, BCY);
draw() ставит его в мир трансформом."""
import math

import numpy as np

import brain_art
import lib
from brain_art import BCX, BCY
from lib import INK, band, blob, ellipse_pts, f, line, shape

SKIN, SKIN_SH = "#f4a6bb", "#d97f9c"
EYE_L, EYE_R = (BCX - 116, BCY + 14), (BCX - 30, BCY + 6)
SH_L, SH_R = (BCX - 150, BCY + 40), (BCX + 150, BCY + 30)
_ST = {}


def arm(S, Wr, bend, sd, sc=1.0):
    dx, dy = Wr[0] - S[0], Wr[1] - S[1]
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    C = ((S[0] + Wr[0]) / 2 + nx * bend, (S[1] + Wr[1]) / 2 + ny * bend)
    pts = [((1 - u) ** 2 * S[0] + 2 * (1 - u) * u * C[0] + u * u * Wr[0], (1 - u) ** 2 * S[1] + 2 * (1 - u) * u * C[1] + u * u * Wr[1])
           for u in np.linspace(0, 1, 9)]
    pl = band(pts, 26 * sc, 20 * sc, step=5, cap=False)
    sh = band([(x + 5 * sc, y + 3 * sc) for x, y in pts], 10 * sc, 8 * sc, step=5, cap=False)
    return shape(pl, SKIN, blob(sh, SKIN_SH, .85), w=3.6 * sc, seed=sd)


def sausage(pts, w0, w1):
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
    return [tuple(p) for p in L[::step]] + [tuple(L[-1])] + cap + [tuple(R[-1])] + [tuple(p) for p in R[::-step]]


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
    return shape(sausage(pts, wd, wd * .92), SKIN, "", w=3.0, seed=sd)


def toon_hand(x, y, ang, curl=0.0, sd=0, sc=1.0, spread=1.0):
    """Кисть: ладонь, три пальца и большой (сверху), запястье в (x, y), пальцы вдоль ang."""
    flip = math.cos(math.radians(ang)) < 0
    s = []
    palm = [(-6, -13), (14, -22), (36, -22), (50, -10), (52, 6), (42, 19), (18, 22), (-6, 12)]
    inner = blob([(-6, 6), (16, 13), (40, 11), (52, 6), (42, 19), (18, 22), (-6, 12)], SKIN_SH, .85)
    fs = []
    for k, (bx, by, fa, L) in enumerate([(46, -14, -14 * spread, 34), (50, -1, 0, 38), (46, 12, 14 * spread, 33)]):
        fs.append(finger((bx, by), fa, L, 15, curl, sd + 10 + k))
    s.append(finger((22, -18), -62 + 30 * curl, 26, 15, curl * 0.8, sd + 20))
    s.append(shape(palm, SKIN, inner, w=3.4, seed=sd + 1))
    s += fs
    rot = ang if not flip else ang - 180
    sx = -1 if flip else 1
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc * sx)} {f(sc)})">{"".join(s)}</g>'


def face(look=(0.0, 0.0), blink=0.0, mouth="smile", closed=False):
    s = []
    if closed:
        for k, (x, y) in enumerate((EYE_L, EYE_R)):
            s.append(line([(x - 26, y + 2), (x - 10, y + 12), (x + 10, y + 12), (x + 26, y + 2)], 6.5, INK, taper=.4, wmin=.35, seed=880 + k))
    else:
        for k, (x, y) in enumerate((EYE_L, EYE_R)):
            ry = 36
            e = ellipse_pts(x, y, 29, ry, 18)
            px, py = x + look[0] * 10, y + look[1] * 12
            inner = f'<circle cx="{f(px)}" cy="{f(py)}" r="9.5" fill="{INK}"/><circle cx="{f(px - 3)}" cy="{f(py - 3.5)}" r="3" fill="#ffffff"/>'
            if blink > 0.02:
                yb = y - ry - 2 + (2 * ry + 4) * blink
                inner += f'<rect x="{x - 32}" y="{y - ry - 4}" width="64" height="{f(yb - (y - ry - 4))}" fill="#f6a9bc"/>'
                inner += line([(x - 30, yb), (x, yb + 3), (x + 30, yb)], 4, INK, seed=890 + k)
            s.append(shape(e, "#ffffff", inner, w=4.4, seed=886 + k))
    mx, my = BCX - 72, BCY + 74
    if mouth == "smile":
        pts = [(mx - 30, my - 8, 1), (mx + 30, my - 10, 1), (mx + 20, my + 12), (mx, my + 20), (mx - 20, my + 12)]
        s.append(shape(pts, "#7a2a40", blob([(mx - 14, my + 8), (mx + 14, my + 6), (mx + 8, my + 18), (mx - 8, my + 18)], "#e2543f"), w=3.6, seed=895))
    elif mouth == "sleep":
        s.append(line([(mx - 16, my + 2), (mx, my + 8), (mx + 16, my + 2)], 4.4, INK, seed=896))
    s.append(blob(ellipse_pts(BCX - 160, BCY + 56, 20, 10, 10), "#f07a98", .55))
    return "".join(s)


LIGHTS = [(-150, -60), (-90, -112), (-20, -128), (60, -110), (130, -70), (170, 0), (110, 40), (30, -40), (-60, -20), (-130, 10),
          (80, -20), (150, 80)]


def lights(t, glow=1.0, seed=0):
    """Огоньки на мозге: тёплые точки с ореолом, мерцают вразнобой, но ни один не гаснет совсем."""
    s, core = [], []
    rs = np.random.RandomState(31 + seed)
    for k, (dx, dy) in enumerate(LIGHTS):
        ph = rs.uniform(0, 6.28)
        sp = rs.uniform(3.5, 6.5)
        v = 0.62 + 0.38 * math.sin(t * sp + ph)
        x, y = BCX + dx, BCY + dy
        r = (9 + 5 * v) * glow
        col = ["#ffe066", "#ffd27a", "#fff3a0", "#ffc457"][k % 4]
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 2.6)}" fill="{col}" opacity="{.35 * v:.3f}" {lib.blur(6)}/>')
        core.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{col}"/><circle cx="{f(x - r * .3)}" cy="{f(y - r * .3)}" r="{f(r * .4)}" fill="#ffffff"/>')
    return "".join(s) + "".join(core)


def body():
    if "b" not in _ST:
        _ST["b"] = brain_art.brain(0.0, 0.0, stem=False)
    return _ST["b"]


def draw(x, y, sc, t, wave=None, look=(0, 0), blink=0.0, mouth="smile", closed=False, lit=None, rot=0.0, arms=True):
    """Мозг: центр (BCX, BCY) → (x, y), масштаб sc. wave — фаза взмаха правой ручки (None — ручки опущены)."""
    o = []
    SL, SR = SH_L, SH_R
    if arms:
        wl = (BCX - 250, BCY + 110)
        if wave is None:
            wr = (BCX + 210, BCY + 150)
            ar = 70
        else:
            a = math.radians(-60 + 28 * math.sin(wave))
            wr = (SR[0] + 160 * math.cos(a) + 40, SR[1] + 160 * math.sin(a))
            ar = -80 + 30 * math.sin(wave)
        o.append(arm(SL, wl, -30, 701))
        o.append(arm(SR, wr, 40 if wave is not None else 30, 702))
    o.append(body())
    if lit is not None:
        o.append(lights(t, lit))
    o.append(face(look, blink, mouth, closed))
    if arms:
        o.append(toon_hand(wl[0], wl[1], 160, 0.3, 730, 1.3))
        o.append(toon_hand(wr[0], wr[1], ar, 0.0, 760, 1.3, spread=1.3 if wave is not None else 1.0))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sc:.4f}) translate({-BCX} {-BCY})">{"".join(o)}</g>'
