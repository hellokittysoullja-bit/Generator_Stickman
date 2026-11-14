"""Тело мозга-персонажа рилса 35 (из рилса 32: ручки-«лапша» с мультяшными кистями, ножки в кедах, большие белые глаза)
и ночная комната. Цвет кожи ручек и ножек — COL (сцена ставит его на кадр: серый мозг — сероватые ручки)."""
import math

import numpy as np

import lib
from brain_art import BCX, BCY
from lib import INK, W, H, back_out, band, blob, blur, clamp, ease_in, ellipse_pts, f, line, lin_grad, mix, rad_grad, shape

FLOOR = 1160
PINK_SKIN, PINK_SH = "#f4a6bb", "#d97f9c"
GREY_SKIN, GREY_SH = "#c4b2c0", "#a08ca0"
COL = {"skin": PINK_SKIN, "sh": PINK_SH}


def set_skin(live):
    """live 0 — сероватая кожа (мозг «спит»), 1 — розовая."""
    COL["skin"] = mix(GREY_SKIN, PINK_SKIN, clamp(live))
    COL["sh"] = mix(GREY_SH, PINK_SH, clamp(live))


# ───────────────────────── фон: ночная комната (рилсы 24–32)
def background(warm=0.0):
    s = []
    sfx = "w" if warm else ""
    lin_grad([(0, mix("#1f2747", "#3a2a48", warm), 1), (.55, mix("#2c3a66", "#5a3c62", warm), 1), (1, mix("#33457a", "#6a4a72", warm), 1)],
             0, 0, 0, 1, gid=f"gWallB{sfx}")
    lin_grad([(0, mix("#3a4c82", "#5c4470", warm), 1), (1, mix("#25305a", "#3a2c50", warm), 1)], 0, 0, 0, 1, gid=f"gFloorB{sfx}")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#gWallB{sfx})"/>')
    s.append(f'<rect x="-900" y="{FLOOR}" width="{W + 1800}" height="{H + 600}" fill="url(#gFloorB{sfx})"/>')
    rad_grad([(0, mix("#5b6fae", "#c48aa0", warm), .9), (.6, mix("#40538d", "#7a5080", warm), .35), (1, "#40538d", 0)], 540, 640, 620, 560,
             gid=f"gSpotB{sfx}")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#gSpotB{sfx})"/>')
    s.append(line([(-800, FLOOR), (W + 800, FLOOR)], 4.5, INK, taper=.1, wmin=.8, seed=5))
    for k, y in enumerate([1240, 1360, 1520, 1730]):
        s.append(line([(-800, y), (W + 800, y + 6)], 2.4, "#1c2546", taper=.2, wmin=.6, seed=10 + k, op=.8))
    s.append(blob([(-800, FLOOR - 26), (W + 800, FLOOR - 26), (W + 800, FLOOR), (-800, FLOOR)], mix("#273260", "#40304e", warm)))
    s.append(line([(-800, FLOOR - 26), (W + 800, FLOOR - 26)], 2.6, INK, taper=.1, wmin=.8, seed=6, op=.8))
    return "".join(s)


def dust(t):
    rs = np.random.RandomState(4)
    s = []
    for k in range(26):
        x0, y0 = rs.uniform(-80, W + 80), rs.uniform(60, FLOOR - 40)
        sp, ph, r = rs.uniform(10, 26), rs.uniform(0, 6.28), rs.uniform(2.2, 4.5)
        x = x0 + 30 * math.sin(t * 0.6 + ph)
        y = (y0 - sp * (t - 10)) % (FLOOR - 60) + 30
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#c9d6ff" opacity="{.18 + .14 * math.sin(t * 2 + ph):.3f}"/>')
    return "".join(s)


def shadow(x, y, rx, op=.55):
    return blob(ellipse_pts(x, y, rx, rx * .16, 14), "#141b38", op, blur(8))


# ───────────────────────── поза
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
HIP_L = (BCX - 62, BCY + 104)
HIP_R = (BCX + 52, BCY + 108)
LEG = 186
EYE_L, EYE_R = (BCX - 116, BCY + 14), (BCX - 30, BCY + 6)


def arm(S, Wr, bend, sd, sc=1.0):
    dx, dy = Wr[0] - S[0], Wr[1] - S[1]
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    C = ((S[0] + Wr[0]) / 2 + nx * bend, (S[1] + Wr[1]) / 2 + ny * bend)
    pts = [((1 - u) ** 2 * S[0] + 2 * (1 - u) * u * C[0] + u * u * Wr[0], (1 - u) ** 2 * S[1] + 2 * (1 - u) * u * C[1] + u * u * Wr[1])
           for u in np.linspace(0, 1, 9)]
    pl = band(pts, 26 * sc, 20 * sc, step=5, cap=False)
    sh = band([(x + 5 * sc, y + 3 * sc) for x, y in pts], 10 * sc, 8 * sc, step=5, cap=False)
    return shape(pl, COL["skin"], blob(sh, COL["sh"], .85), w=3.6 * sc, seed=sd)


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
    return shape(sausage(pts, wd, wd * .92), COL["skin"], "", w=3.0, seed=sd)


PALM = [(-6, -13), (14, -22), (36, -22), (50, -10), (52, 6), (42, 19), (18, 22), (-6, 12)]


def toon_hand(x, y, ang, curl=0.0, sd=0, sc=1.0, spread=1.0, thumb_curl=None):
    """Кисть: ладонь, три пальца и большой; запястье в (x, y), пальцы вдоль ang; большой палец сверху."""
    flip = math.cos(math.radians(ang)) < 0
    s = []
    inner = blob([(-6, 6), (16, 13), (40, 11), (52, 6), (42, 19), (18, 22), (-6, 12)], COL["sh"], .85)
    fs = [finger((bx, by), fa, L, 15, curl, sd + 10 + k)
          for k, (bx, by, fa, L) in enumerate([(46, -14, -14 * spread, 34), (50, -1, 0, 38), (46, 12, 14 * spread, 33)])]
    tc = curl * 0.8 if thumb_curl is None else thumb_curl
    s.append(finger((22, -18), -62 + 30 * curl, 26, 15, tc, sd + 20))
    s.append(shape(PALM, COL["skin"], inner, w=3.4, seed=sd + 1))
    s += fs
    rot = ang if not flip else ang - 180
    sx = -1 if flip else 1
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc * sx)} {f(sc)})">{"".join(s)}</g>'


def thumbs_up(x, y, sd=0, sc=1.0, mirror=False):
    """Кулак с поднятым большим пальцем: запястье в (x, y), кулак правее, палец вверх."""
    s = []
    fist = [(-8, -20), (30, -24), (54, -16), (60, 4), (56, 26), (30, 32), (-6, 22)]
    inner = blob([(-6, 12), (30, 20), (56, 14), (56, 26), (30, 32), (-6, 22)], COL["sh"], .85)
    # пальцы, свёрнутые в кулак — три «сосиски» поперёк
    for k in range(3):
        yy = -10 + k * 13
        inner += line([(30, yy + 2), (52, yy), (58, yy + 5)], 3.0, INK, seed=sd + 40 + k, taper=.6)
    thumb = sausage([(20, -18), (22, -40), (24, -64)], 17, 16)
    s.append(shape(thumb, COL["skin"], "", w=3.2, seed=sd + 20))
    s.append(shape(fist, COL["skin"], inner, w=3.6, seed=sd + 1))
    sx = -1 if mirror else 1
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc * sx)} {f(sc)})">{"".join(s)}</g>'


# ───────────────────────── ножки и кеды
def shoe(F, face, sc, sd):
    up = [(-20, -6), (8, -10), (24, 2), (42, 12), (46, 26, 1), (-24, 26, 1), (-27, 10)]
    inner = blob([(-30, 17), (50, 17), (50, 30), (-30, 30)], "#ff8a3d")
    inner += blob([(-8, 4), (18, -2), (34, 10), (20, 12), (0, 10)], "#3d7fe0")
    inner += line([(4, -6), (14, 2)], 2.6, INK, seed=sd + 3)
    s = shape(up, "#f6f3ec", inner, w=3.4, seed=sd)
    return f'<g transform="translate({f(F[0])} {f(F[1])}) scale({f(face * sc)} {f(sc)})">{s}</g>'


def leg(Hp, F, sc, face=-1, sd=0):
    Hp, F = np.array(Hp, float), np.array(F, float)
    L = LEG * sc
    d = F - Hp
    dist = np.linalg.norm(d) + 1e-6
    if dist > L * 0.995:
        F = Hp + d / dist * L * 0.995
        d = F - Hp
        dist = L * 0.995
    a = L / 2
    hh = math.sqrt(max(a * a - (dist / 2) ** 2, 0))
    n = np.array([-d[1], d[0]]) / dist
    if n[0] * face < 0:
        n = -n
    K = (Hp + F) / 2 + n * hh
    pts = [tuple(Hp), tuple((Hp + K) / 2), tuple(K), tuple((K + F) / 2), tuple(F)]
    pl = band(pts, 30 * sc, 24 * sc, step=4, wmid=27 * sc, cap=True)
    sh = band([(x + 5 * sc, y) for x, y in pts], 11 * sc, 8 * sc, step=4, wmid=10 * sc, cap=False)
    return shape(pl, COL["skin"], blob(sh, COL["sh"], .85), w=3.6 * sc, seed=sd) + shoe((F[0], F[1] - 4 * sc), face, sc * 1.05, sd + 5)


def stand_legs(pose, sc, t=0.0, step=0.0, sd=1200):
    """Стоит на полу (FLOOR): ступни под бёдрами; step — шаг на месте (фаза, рад)."""
    hl, hr = pose.pt(*HIP_L), pose.pt(*HIP_R)
    g = FLOOR - 26
    lift_l = 40 * max(0.0, math.sin(step)) if step else 0.0
    lift_r = 40 * max(0.0, -math.sin(step)) if step else 0.0
    fl = (hl[0] - 14, g - lift_l)
    fr = (hr[0] + 12, g - lift_r)
    return leg(hr, fr, sc, -1, sd) + leg(hl, fl, sc, -1, sd + 20)


# ───────────────────────── лицо (локальные координаты мозга)
def eye(x, y, k, open_=1.0, look=(0, 0), lid_col="#f6a9bc", brow=0.0, brow_tilt=0.0, wink=False, sd=0, brow_col="#5a3550"):
    s = []
    if wink:
        s.append(line([(x - 26, y + 6), (x - 8, y - 8), (x + 10, y - 8), (x + 26, y + 6)], 7, INK, taper=.4, wmin=.35, seed=sd + 880))
        return "".join(s)
    if open_ < 0.08:
        s.append(line([(x - 26, y + 2), (x - 10, y + 12), (x + 10, y + 12), (x + 26, y + 2)], 6.5, INK, taper=.4, wmin=.35, seed=sd + 880))
        s.append(line([(x - 18, y + 14), (x - 22, y + 22)], 2.6, INK, taper=.5, seed=sd + 884))
        return "".join(s)
    ry = 36
    e = ellipse_pts(x, y, 29, ry, 18)
    px, py = x + look[0] * 10, y + look[1] * 12
    inner = f'<circle cx="{f(px)}" cy="{f(py)}" r="9.5" fill="{INK}"/><circle cx="{f(px - 3)}" cy="{f(py - 3.5)}" r="3" fill="#ffffff"/>'
    lid = 1 - open_
    if lid > 0.02:
        yb = y - ry - 2 + (2 * ry + 4) * lid
        inner += f'<rect x="{x - 34}" y="{y - ry - 6}" width="68" height="{f(yb - (y - ry - 6))}" fill="{lid_col}"/>'
        inner += line([(x - 32, yb), (x, yb + 3), (x + 32, yb)], 4.4, INK, seed=sd + 890)
    s.append(shape(e, "#ffffff", inner, w=4.4, seed=sd + 886))
    if brow:
        by = y - ry - 16 - 8 * brow
        tl = brow_tilt * (-1 if k == 0 else 1)
        s.append(line([(x - 22, by + 4 - 8 * tl), (x, by - 4 * brow), (x + 20, by + 2 + 8 * tl)], 5.5, brow_col, taper=.4, wmin=.4, seed=sd + 892))
    return "".join(s)


def face(open_=1.0, look=(0.0, 0.0), mouth="smile", t=0.0, brow=0.0, brow_tilt=0.0, lid_col="#f6a9bc", wink_r=False, blush=0.55,
         open_r=None, brow_col="#5a3550"):
    s = []
    for k, (x, y) in enumerate((EYE_L, EYE_R)):
        o = open_ if (k == 0 or open_r is None) else open_r
        s.append(eye(x, y, k, o, look, lid_col, brow, brow_tilt, wink=(k == 1 and wink_r), sd=k, brow_col=brow_col))
    mx, my = BCX - 72, BCY + 74
    if mouth == "snore":
        r = 7 + 3 * math.sin(t * 2.6)
        s.append(shape(ellipse_pts(mx, my, r * .9, r, 12), "#6a2a40", "", w=3, seed=895))
    elif mouth == "o":
        s.append(shape(ellipse_pts(mx, my, 14, 18, 14), "#6a2a40", blob(ellipse_pts(mx, my + 8, 8, 6, 10), "#e2543f"), w=3.4, seed=895))
    elif mouth == "flat":
        s.append(line([(mx - 18, my + 2), (mx, my + 4), (mx + 18, my)], 5, INK, taper=.4, wmin=.4, seed=896))
    elif mouth == "wobbly":      # виноватая волнистая улыбка
        s.append(line([(mx - 24, my + 4), (mx - 12, my - 2), (mx, my + 4), (mx + 12, my - 2), (mx + 24, my + 4)], 5, INK, taper=.4, wmin=.4,
                      seed=897))
    elif mouth == "grin":        # широкая улыбка с зубами
        pts = [(mx - 36, my - 10, 1), (mx + 34, my - 12, 1), (mx + 22, my + 14), (mx, my + 22), (mx - 22, my + 14)]
        inner = blob([(mx - 16, my + 10), (mx + 16, my + 8), (mx + 8, my + 20), (mx - 8, my + 20)], "#e2543f")
        inner += blob([(mx - 36, my - 14), (mx + 34, my - 16), (mx + 30, my - 2), (mx - 32, my)], "#ffffff")
        s.append(shape(pts, "#6a2a40", inner, w=3.8, seed=895))
    else:                        # улыбка с открытым ртом
        pts = [(mx - 30, my - 8, 1), (mx + 30, my - 10, 1), (mx + 20, my + 12), (mx, my + 20), (mx - 20, my + 12)]
        s.append(shape(pts, "#6a2a40", blob([(mx - 14, my + 8), (mx + 14, my + 6), (mx + 8, my + 18), (mx - 8, my + 18)], "#e2543f"), w=3.6, seed=895))
    if blush > 0.02:
        s.append(blob(ellipse_pts(BCX - 160, BCY + 56, 20, 10, 10), "#f07a98", blush))
        s.append(blob(ellipse_pts(BCX + 8, BCY + 50, 17, 9, 10), "#f07a98", blush * .8))
    return "".join(s)


def sweat(x, y, sc):
    pts = [(0, -26, 1), (10, -6), (13, 6), (7, 16), (-7, 16), (-13, 6), (-10, -6)]
    inner = blob(ellipse_pts(-4, 4, 3.5, 6, 8, rot=20), "#ffffff", .9)
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{shape(pts, "#8fd3ff", inner, w=3.2, seed=500)}</g>'


def star(x, y, r, col="#ffe27a", sd=0, rot=0.0):
    """Четырёхлучевая искра с тушью."""
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.32
        a = math.radians(rot + i * 45 - 90)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, col, "", w=max(1.6, r * 0.09), seed=sd)


def rays(x, y, e, sd, r=70, n=8, col="#ffe27a", dur=0.4, L0=40, w=8):
    if e < 0 or e > dur:
        return ""
    u = e / dur
    s = []
    for k in range(n):
        a = k * 2 * math.pi / n + .3
        r0 = r + 80 * back_out(u, 1.2) if u < 1 else r + 80
        L = L0 * (1 - u)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))], w, col, taper=.5,
                      seed=sd + k))
    return "".join(s)


def text(x, y, txt, size, fill, stroke=INK, sw=10, anchor="middle", shadow=True, extra=""):
    s = ""
    if shadow:
        s += (f'<text x="{f(x + size * .04)}" y="{f(y + size * .05)}" text-anchor="{anchor}" font-family="IDB" font-weight="900" '
              f'font-size="{f(size)}" fill="{INK}">{txt}</text>')
    s += (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="IDB" font-weight="900" font-size="{f(size)}" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{f(sw)}" paint-order="stroke" stroke-linejoin="round" {extra}>{txt}</text>')
    return s


def ease_kick(e, amp, freq=16, damp=7):
    """Затухающий толчок после события (e — секунды после удара)."""
    if e <= 0:
        return 0.0
    return amp * math.exp(-e * damp) * math.sin(min(e * freq, math.pi))


__all__ = ["ease_in", "rad_grad"]
