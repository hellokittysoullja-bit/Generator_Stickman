"""Сцена brain (s05, s06, s12): тот же мозг, что в рилсе 24, с маленькими мультяшными ручками (контур, четыре пальца)
и стикеры-дела со значками (без букв).
s05: держит пачку стикеров; на «держит» (11.4) выскакивают ещё три — один падает на пачку, два он хватает руками.
s06: жонглирует стикерами; один выскальзывает, на «забыл» (13.08) рука вытягивается и ловит его в последний момент, пот.
s12: раскрывает руки — стикеры падают в коробку, облегчённо выдыхает, перелетает в гамак; последние стикеры, брошенные
из гамака, падают в коробку на «держать» (26.0). Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import brain_art
import icons
from brain_art import BCX, BCY
from lib import (DEFS, INK, W, H, back_out, band, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg)

FLOOR = 1160
SKIN, SKIN_SH, SKIN_HI = "#f4a6bb", "#d97f9c", "#ffd3de"
HOLD = 11.40      # «держит»
CATCH = 13.08     # «забыл»
DROP = 24.95      # руки раскрываются
REST = 26.00      # «держать»
_ST = {}

STACK = [("yellow", "envelope"), ("pink", "cart"), ("blue", "laptop"), ("green", "tooth"), ("orange", "receipt"),
         ("yellow", "phone"), ("pink", "trash"), ("blue", "calendar")]


# ───────────────────────── фон (как в рилсе 24, комната ночью)
def background(warm=0.0):
    s = []
    sfx = "w" if warm else ""
    lin_grad([(0, mix("#1f2747", "#2a2440", warm), 1), (.55, mix("#2c3a66", "#3c3560", warm), 1), (1, mix("#33457a", "#4a4070", warm), 1)],
             0, 0, 0, 1, gid=f"gWallB{sfx}")
    lin_grad([(0, "#3a4c82", 1), (1, "#25305a", 1)], 0, 0, 0, 1, gid=f"gFloorB{sfx}")
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{FLOOR + 600}" fill="url(#gWallB{sfx})"/>')
    s.append(f'<rect x="-600" y="{FLOOR}" width="{W + 1200}" height="{H}" fill="url(#gFloorB{sfx})"/>')
    rad_grad([(0, mix("#5b6fae", "#8a6aa0", warm), .9), (.6, "#40538d", .35), (1, "#40538d", 0)], 540, 640, 620, 560, gid=f"gSpotB{sfx}")
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{FLOOR + 600}" fill="url(#gSpotB{sfx})"/>')
    s.append(line([(-400, FLOOR), (W + 400, FLOOR)], 4.5, INK, taper=.1, wmin=.8, seed=5))
    for k, y in enumerate([1240, 1360, 1520, 1730]):
        s.append(line([(-400, y), (W + 400, y + 6)], 2.4, "#1c2546", taper=.2, wmin=.6, seed=10 + k, op=.8))
    s.append(blob([(-400, FLOOR - 26), (W + 400, FLOOR - 26), (W + 400, FLOOR), (-400, FLOOR)], "#273260"))
    s.append(line([(-400, FLOOR - 26), (W + 400, FLOOR - 26)], 2.6, INK, taper=.1, wmin=.8, seed=6, op=.8))
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


# ───────────────────────── мозг и ручки
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


def brain_with_arms(pose, wl, wr, al, ar, curl_l, curl_r, bend_l=-40, bend_r=40, sd=0, back_items="", hand_items=""):
    """Мозг, ручки к запястьям wl/wr, кисти под углами al/ar. back_items — между ручками и кистями (то, что держат)."""
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    s = [arm(SL, wl, bend_l, sd + 1, pose.sc), arm(SR, wr, bend_r, sd + 2, pose.sc)]
    s.append(f'<g transform="{pose.tf()}">{_ST["brain"]}</g>')
    s.append(back_items)
    s.append(toon_hand(wl[0], wl[1], al, curl_l, sd + 30, pose.sc * 1.3))
    s.append(toon_hand(wr[0], wr[1], ar, curl_r, sd + 60, pose.sc * 1.3))
    s.append(hand_items)
    return "".join(s)


def shadow(x, y, rx, op=.55):
    return blob(ellipse_pts(x, y, rx, rx * .16, 14), "#141b38", op, blur(8))


def sweat(x, y, sc, op=1.0):
    pts = [(0, -26, 1), (10, -6), (13, 6), (7, 16), (-7, 16), (-13, 6), (-10, -6)]
    inner = blob(ellipse_pts(-4, 4, 3.5, 6, 8, rot=20), "#ffffff", .9)
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})" opacity="{op:.3f}">{shape(pts, "#8fd3ff", inner, w=3.2, seed=500)}</g>'


def effort_lines(cx, cy, r, t, a0=-2.4, n=3, col="#e9eeff"):
    s = []
    for k in range(n):
        ph = (t * 2.4 + k / n) % 1
        a = a0 + k * 0.42
        r0 = r + 30 * ph
        L = 34 * (1 - ph)
        s.append(line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + L), cy + math.sin(a) * (r0 + L))], 7, col,
                      taper=.5, seed=170 + k))
    return "".join(s)


# ───────────────────────── s05: держит пачку, хватает новые
P05 = (540, 560)
STK = (540, 850)       # центр пачки


def s05(t):
    br = 1 + 0.012 * math.sin(t * 2.6)
    e = t - HOLD
    jolt = 0.05 * math.exp(-max(e, 0) * 7) * math.cos(max(e, 0) * 26) if e > 0 else 0.0
    pose = Pose(P05[0], P05[1] - 6 * math.sin(t * 2.6), 1.0 * br, 2 * math.sin(t * 1.7), 1 - jolt)
    # пачка: n стикеров, немного вразнобой; качается
    n = 5
    wob = 3 * math.sin(t * 3.1) + 5 * math.exp(-max(e - .1, 0) * 4) * math.sin(max(e - .1, 0) * 18) * (e > .1)
    items = []
    # новые: A — сам падает на пачку, L и R — хватают руки
    landA = HOLD + 0.32
    nA = 1 if t >= landA else 0
    gotL = HOLD + 0.62     # левая рука схватила
    backL = HOLD + 0.95    # положила на пачку
    gotR = HOLD + 0.72
    backR = HOLD + 1.05
    nn = n + nA + (1 if t >= backL else 0) + (1 if t >= backR else 0)
    order = STACK[:5] + [("orange", "trash"), ("green", "phone"), ("blue", "tooth")]
    for k in range(nn):
        col, ic = order[k]
        y = STK[1] - k * 14
        rot = wob * (0.4 + k * 0.15) + [-4, 3, -2, 5, -3, 2, -5, 4][k % 8]
        x = STK[0] + [0, 6, -8, 4, -5, 7, -3, 2][k % 8] + wob * k * 0.8
        items.append(icons.sticky(x, y, col, ic, rot, 0.9, sd=900 + k * 37, shadow=(k == 0)))
    top_y = STK[1] - nn * 14
    flying, carried = [], []
    # A: выскакивает снизу из-за края кадра, перелетает и плюхается на пачку
    if HOLD - 0.05 <= t < landA:
        u = (t - HOLD + 0.05) / (landA - HOLD + 0.05)
        x = 780 + (STK[0] - 780) * u
        y = 1500 + (top_y - 1500) * u - 520 * math.sin(math.pi * u)
        flying.append(icons.sticky(x, y, "orange", "trash", 300 * u, 0.9, sd=1500))
    # L и R: выскакивают и зависают в верхней точке, руки хватают
    def pop(t0, x0, y0, x1, y1, col, ic, sd, sgn):
        if t < t0:
            return None
        u = clamp((t - t0) / 0.3)
        x = x0 + (x1 - x0) * ease_out(u, 2)
        y = y0 + (y1 - y0) * ease_out(u, 2.2)
        rot = sgn * (40 * (1 - u) + 6 * math.sin(t * 5))
        return x, y, rot
    gL = pop(HOLD - 0.02, -120, 1400, 270, 700, "green", "phone", 1600, -1)
    gR = pop(HOLD + 0.06, 1200, 1350, 810, 680, "blue", "tooth", 1700, 1)
    # кисти: обе держат пачку по бокам, потом левая/правая выбрасываются за стикерами
    hold_l, hold_r = (STK[0] - 150, STK[1] - 6), (STK[0] + 150, STK[1] - 6)
    wl, al, cl = hold_l, 4, 0.15
    wr, ar, cr = hold_r, 176, 0.15

    def reach(t_go, t_got, t_back, home, target, top):
        if t < t_go:
            return home, 0.15, False
        if t < t_got:
            u = ease_out((t - t_go) / (t_got - t_go), 2.5)
            p = (home[0] + (target[0] - home[0]) * u, home[1] + (target[1] - home[1]) * u)
            return p, 0.15 * (1 - u), False
        if t < t_back:
            u = ease_io((t - t_got) / (t_back - t_got))
            p = (target[0] + (top[0] - target[0]) * u, target[1] + (top[1] - target[1]) * u - 60 * math.sin(math.pi * u))
            return p, 0.2, True
        return home, 0.15, False
    tl = (STK[0] - 40, top_y - 10)
    tr = (STK[0] + 40, top_y - 24)
    if gL:
        p, cl, carry = reach(HOLD + 0.30, gotL, backL, hold_l, (gL[0] - 135, gL[1] + 4), (tl[0] - 135, tl[1]))
        wl = p
        al = 0
        if t < gotL:
            flying.append(icons.sticky(gL[0], gL[1], "green", "phone", gL[2], 0.9, sd=1600))
        elif t < backL:
            carried.append(icons.sticky(wl[0] + 135, wl[1] - 4, "green", "phone", -6, 0.9, sd=1600))
    if gR:
        p, cr, carry = reach(HOLD + 0.40, gotR, backR, hold_r, (gR[0] + 135, gR[1] + 4), (tr[0] + 135, tr[1]))
        wr = p
        ar = 180
        if t < gotR:
            flying.append(icons.sticky(gR[0], gR[1], "blue", "tooth", gR[2], 0.9, sd=1700))
        elif t < backR:
            carried.append(icons.sticky(wr[0] - 135, wr[1] - 4, "blue", "tooth", 6, 0.9, sd=1700))
    pose_sh = shadow(540, FLOOR + 30, 220)
    pops = ""
    if 0 < e < 0.35:   # «дзынь» на выскок
        for k in range(6):
            a = -math.pi / 2 + (k - 2.5) * 0.5
            r0 = 300 + 120 * ease_out(e / .35)
            L = 40 * (1 - e / .35)
            pops += line([(540 + math.cos(a) * r0, 600 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + L), 600 + math.sin(a) * (r0 + L))],
                         8, "#ffe27a", taper=.5, seed=180 + k)
    eff = effort_lines(540, 540, 250, t) if t > HOLD + .5 else ""
    art = pose_sh + brain_with_arms(pose, wl, wr, al, ar, cl, cr, -50, 50, back_items="".join(items) + "".join(carried), hand_items="".join(flying)) + pops + eff
    u = (t - 10.0) / 2.5
    return art, cam(540, 790 - 10 * u, 1.40 + 0.10 * ease_io(u), -0.6 + 0.8 * u)


# ───────────────────────── s06: жонглирует, роняет, ловит
P06 = (540, 520)
HL, HR = (370, 880), (710, 880)
JUG = [("yellow", "envelope"), ("pink", "cart"), ("blue", "laptop"), ("green", "tooth")]
CYC = 0.72
SLIP = 12.62
SLIP_K = 2


def jug_pos(k, t):
    """Каскад: из левой руки высокой дугой в правую, из правой низом обратно в левую."""
    ph = ((t - 12.0) / CYC + k / 4) % 1
    if ph < 0.72:
        u = ph / 0.72
        x = HL[0] + 40 + (HR[0] - HL[0] - 80) * u
        y = HL[1] - 40 - 330 * 4 * u * (1 - u)
        rot = -200 * u
    else:
        u = (ph - 0.72) / 0.28
        x = HR[0] - 40 - (HR[0] - HL[0] - 80) * u
        y = HR[1] - 40 + 30 * math.sin(math.pi * u)
        rot = -200 + 200 * u
    return x, y, rot, ph


def s06(t):
    br = 1 + 0.012 * math.sin(t * 2.6)
    e = t - CATCH
    jolt = 0.06 * math.exp(-max(e, 0) * 7) * math.cos(max(e, 0) * 24) if e > 0 else 0.0
    lean = 0.0
    if t > SLIP:
        lean = 9 * smooth(SLIP + .1, CATCH, t) * (1 - smooth(CATCH + .2, CATCH + .8, t))
    pose = Pose(P06[0] + 30 * lean / 9, P06[1] - 8 * abs(math.sin(t * 8.7)) * (t < SLIP), 1.0 * br, lean + 2 * math.sin(t * 1.9), 1 - jolt)
    items, hand_items = [], []
    # руки подбрасывают: подскок на каждом броске
    def bob(side):
        best = 0.0
        for k in range(4):
            ph = ((t - 12.0) / CYC + k / 4) % 1
            d = ph if side == "L" else ph - 0.72
            if 0 <= d < 0.12:
                best = max(best, math.sin(math.pi * d / 0.12))
        return best
    gather = smooth(SLIP + 0.02, SLIP + 0.28, t)
    wl = (HL[0], HL[1] - 50 * bob("L") * (1 - gather))
    wr = (HR[0], HR[1] - 40 * bob("R") * (t < SLIP))
    al, ar, cl, cr = -15, 195, 0.35, 0.35
    # стикеры
    for k, (col, ic) in enumerate(JUG):
        if k == SLIP_K and t >= SLIP - 0.25:
            continue
        x, y, rot, ph = jug_pos(k, min(t, SLIP))
        if t > SLIP:   # остальные — в левую руку пачкой
            slot = [0, 1, None, 2][k]
            tx, ty, tr = HL[0] + 70, HL[1] - 40 - slot * 14, [-6, 4, 0, -3][k]
            x, y, rot = x + (tx - x) * gather, y + (ty - y) * gather, rot + (tr - rot) * gather
        items.append(icons.sticky(x, y, col, ic, rot, 0.78, sd=2000 + k * 41, shadow=False))
    # выскальзывающий
    col, ic = JUG[SLIP_K]
    t_s0 = SLIP - 0.25
    if t >= t_s0:
        x0, y0, r0, _ = jug_pos(SLIP_K, t_s0)

        def fall(e):
            return x0 + 160 * e, y0 - 150 * e + 1500 * e * e * 0.5, r0 + 420 * e
        ec = CATCH - t_s0
        fx, fy, fr = fall(ec)
        tgt = (fx + 118, fy + 4)
        if t < CATCH:
            cpos = fall(t - t_s0)
        # правая рука: бросается следом, догоняет на «забыл» и подтягивает стикер обратно
        if t >= SLIP:
            if t < CATCH:
                u = ease_in((t - SLIP) / (CATCH - SLIP), 1.5)
                wr = (HR[0] + (tgt[0] - HR[0]) * u, HR[1] + (tgt[1] - HR[1]) * u)
                cr, ar = 0.0, 185 - 5 * u
            else:
                back = ease_io((t - CATCH - 0.18) / 0.6)
                home = (HR[0] + 60, HR[1] - 30)
                wr = (tgt[0] + (home[0] - tgt[0]) * back, tgt[1] + (home[1] - tgt[1]) * back)
                cr, ar = 0.25, 180
                rot = -8 + 14 * math.exp(-(t - CATCH) * 7) * math.sin((t - CATCH) * 30)
                cpos = (wr[0] - 118, wr[1] - 4, rot)
        st = icons.sticky(cpos[0], cpos[1], col, ic, cpos[2], 0.78, sd=2000 + SLIP_K * 41, shadow=False)
        items.append(st)
        if SLIP < t < CATCH:   # штрихи скорости за падающим
            for k in range(3):
                hand_items.append(line([(cpos[0] - 30 + k * 30, cpos[1] - 80), (cpos[0] - 36 + k * 30, cpos[1] - 140)], 6, "#e9eeff", taper=.5, seed=210 + k, op=.8))
    # пот: появляется, когда стикер выскальзывает, слетает на «забыл»
    sw = ""
    if t > SLIP + 0.1:
        a_ = smooth(SLIP + 0.1, SLIP + 0.25, t)
        px, py = pose.pt(BCX + 120, BCY - 150)
        if t < CATCH:
            sw = sweat(px + 10, py - 10 + 30 * (t - SLIP), 2.2 * a_)
        else:
            ee = t - CATCH
            sw = sweat(px + 10 + 420 * ee, py + 6 - 500 * ee + 1500 * ee * ee, 2.2, 1 - smooth(0.45, 0.6, ee))
    # «уф» после поимки
    phew = ""
    if CATCH + 0.25 < t:
        ee = t - CATCH - 0.25
        a_ = smooth(0, .15, ee) * (1 - smooth(.5, .7, ee))
        for k in range(3):
            y = 500 + k * 28
            x = 300 - 50 * ease_out(ee / .6)
            phew += line([(x, y), (x - 60, y - 6 + k * 6)], 7, "#e9eeff", taper=.5, seed=190 + k, op=a_)
    art = (shadow(540, FLOOR + 30, 220) + brain_with_arms(pose, wl, wr, al, ar, cl, cr, -40, 50, back_items="".join(items),
                                                           hand_items="".join(hand_items)) + sw + phew)
    csh = 0.0
    if e > 0:
        csh = 12 * math.exp(-e * 9) * math.sin(e * 60)
    u = (t - 12.1) / 1.9
    fol = smooth(SLIP, CATCH, t) * (1 - 0.6 * smooth(CATCH + .2, CATCH + .8, t))
    return art, cam(560 + csh + 30 * fol, 800 + 0.6 * csh + 120 * fol, 1.36 + 0.05 * u)


# ───────────────────────── s12: роняет в коробку, выдыхает, гамак
BOX = (350, 1170)      # низ-центр коробки
BOXW, BOXH = 330, 210
P12 = (370, 520)
HAM = (805, 780)       # центр гамака
HOOK_L, HOOK_R = (540, 470), (1080, 470)
FALL = [("yellow", "envelope"), ("pink", "cart"), ("blue", "laptop"), ("green", "tooth"), ("orange", "receipt"), ("yellow", "phone")]
TOSS0, TOSS1 = 25.62, REST


def box_back():
    x, y = BOX
    s = []
    s.append(shadow(x + 20, y + 6, 210, .6))
    back = [(x - BOXW / 2 + 30, y - BOXH - 40, 1), (x + BOXW / 2 + 30, y - BOXH - 40, 1), (x + BOXW / 2, y - BOXH, 1), (x - BOXW / 2, y - BOXH, 1)]
    s.append(shape(back, "#7a5233", "", w=4, seed=600))
    # внутренняя задняя стенка
    s.append(shape([(x - BOXW / 2 + 30, y - BOXH - 40, 1), (x + BOXW / 2 + 30, y - BOXH - 40, 1), (x + BOXW / 2 + 30, y - 60, 1), (x - BOXW / 2 + 30, y - 60, 1)],
                   "#6a4428", "", w=3.6, seed=601))
    # клапаны сзади
    s.append(shape([(x - BOXW / 2 + 30, y - BOXH - 40, 1), (x + BOXW / 2 + 30, y - BOXH - 40, 1), (x + BOXW / 2 + 10, y - BOXH - 120, 1),
                    (x - BOXW / 2 + 50, y - BOXH - 120, 1)], "#c08a55", blob([(x - BOXW / 2 + 40, y - BOXH - 60), (x + BOXW / 2 + 20, y - BOXH - 60),
                                                                          (x + BOXW / 2 + 30, y - BOXH - 40), (x - BOXW / 2 + 30, y - BOXH - 40)], "#a07040", .8),
                   w=4, seed=602))
    return "".join(s)


def box_front():
    x, y = BOX
    s = []
    front = [(x - BOXW / 2, y - BOXH, 1), (x + BOXW / 2, y - BOXH, 1), (x + BOXW / 2, y, 1), (x - BOXW / 2, y, 1)]
    inner = blob([(x + BOXW / 2 - 60, y - BOXH), (x + BOXW / 2, y - BOXH), (x + BOXW / 2, y), (x + BOXW / 2 - 40, y)], "#a8743f", .9)
    inner += line([(x - 30, y - BOXH + 4), (x - 26, y - 4)], 3, "#9a6a3a", seed=611, op=.8)
    inner += blob(rect_pts(x - 70, y - BOXH, x + 10, y - BOXH + 34), "#d9b47a", .9)   # скотч
    s.append(shape(front, "#c48d52", inner, w=5, seed=610))
    side = [(x + BOXW / 2, y - BOXH, 1), (x + BOXW / 2 + 30, y - BOXH - 40, 1), (x + BOXW / 2 + 30, y - 40, 1), (x + BOXW / 2, y, 1)]
    s.append(shape(side, "#9a6a3a", "", w=4.4, seed=612))
    # передний клапан откинут вперёд
    s.append(shape([(x - BOXW / 2, y - BOXH, 1), (x + BOXW / 2, y - BOXH, 1), (x + BOXW / 2 - 16, y - BOXH + 70, 1), (x - BOXW / 2 + 16, y - BOXH + 70, 1)],
                   "#d49d60", line([(x - 120, y - BOXH + 40), (x + 100, y - BOXH + 40)], 3, "#b07a42", seed=614, op=.7), w=4.4, seed=613))
    return "".join(s)


def hammock(t, load):
    """Гамак на крюках; load — насколько он прогнулся (0 — пустой, 1 — мозг лежит), с покачиванием."""
    sway = 6 * math.sin(t * 2.0)
    sag = 70 + 70 * load
    L, R = (HAM[0] - 215, HAM[1] - 40), (HAM[0] + 215, HAM[1] - 40)
    s = []
    s.append(line([HOOK_L, L], 5, "#d9c9a0", taper=.1, wmin=.9, seed=620) + line([HOOK_R, R], 5, "#d9c9a0", taper=.1, wmin=.9, seed=621))
    for p in (HOOK_L, HOOK_R):
        s.append(shape(ellipse_pts(p[0], p[1], 10, 10, 10), "#8a8f9e", "", w=3, seed=622 + p[0]))
    top = [(L[0] + (R[0] - L[0]) * u + sway * math.sin(math.pi * u), L[1] + sag * 0.55 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 9)]
    bot = [(L[0] + (R[0] - L[0]) * u + sway * math.sin(math.pi * u), L[1] + sag * math.sin(math.pi * u) + 26 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 9)]
    pts = [(top[0][0], top[0][1], 1)] + top[1:-1] + [(top[-1][0], top[-1][1], 1)] + bot[::-1][1:-1]
    inner = ""
    for k in range(1, 8):
        u = k / 8
        inner += line([(top[k][0], top[k][1]), (bot[k][0], bot[k][1] + 6)], 3, "#b85a3a", taper=.1, wmin=.8, seed=630 + k, op=.8)
    inner += blob([(p[0], p[1] + 10) for p in bot[1:-1]] + [(p[0], p[1] - 4) for p in bot[::-1][1:-1]], "#a94a30", .7)
    return "".join(s), shape(pts, "#e2734a", inner, w=4.4, seed=640), bot


def s12(t):
    items_box, flying = [], []
    # стикеры: держит пачку до DROP, потом падают в коробку
    for k, (col, ic) in enumerate(FALL):
        held = (P12[0] + [0, 6, -8, 4, -5, 7][k], 860 - k * 14)
        rest = (BOX[0] + [-80, 50, -20, 80, -45, 25][k], BOX[1] - BOXH + 30 - [0, 10, 26, 18, 40, 30][k])
        rrot = [-14, 22, -6, 30, 8, -24][k]
        t0 = DROP + 0.04 * k
        if t < t0:
            flying.append(icons.sticky(held[0] + 3 * math.sin(t * 3), held[1], col, ic, [-4, 3, -2, 5, -3, 2][k], 0.86, sd=3000 + k * 43, shadow=False))
            continue
        e = t - t0
        T = 0.36
        if e < T:
            u = e / T
            x = held[0] + (rest[0] - held[0]) * u
            y = held[1] + (rest[1] - held[1]) * u * u
            rot = [-4, 3, -2, 5, -3, 2][k] + (rrot - [-4, 3, -2, 5, -3, 2][k]) * u + 60 * math.sin(math.pi * u) * (1 if k % 2 else -1)
            st = icons.sticky(x, y, col, ic, rot, 0.86, sd=3000 + k * 43, shadow=False)
            (items_box if y > BOX[1] - BOXH - 120 else flying).append(st)
        else:
            b = 12 * math.exp(-(e - T) * 10) * abs(math.sin((e - T) * 22))
            items_box.append(icons.sticky(rest[0], rest[1] - b, col, ic, rrot, 0.86, sd=3000 + k * 43, shadow=False))
    # мозг: держит → раскрывает руки → выдох → прыжок в гамак → лежит
    jump0, jump1 = 25.40, 25.85
    br = 1 + 0.012 * math.sin(t * 2.6)
    if t < jump0:
        ex = smooth(DROP + .1, DROP + .35, t) * (1 - smooth(25.3, 25.4, t))
        pose = Pose(P12[0], P12[1] - 6 * math.sin(t * 2.6) + 14 * ex, br, 2 * math.sin(t * 1.7), 1 - 0.07 * ex)
        opn = smooth(DROP - .05, DROP + .12, t)
        wl = (P12[0] - 120 - 60 * opn, 860 - 10 - 40 * opn)
        wr = (P12[0] + 120 + 60 * opn, 860 - 10 - 40 * opn)
        al, ar = 8 - 70 * opn, 172 + 70 * opn
        cl = cr = 0.75 * (1 - opn)
        bl, brd = -50, 50
        load = 0.0
        tossed = None
    else:
        u = clamp((t - jump0) / (jump1 - jump0))
        uu = ease_io(u)
        x = P12[0] + (HAM[0] - P12[0]) * uu
        y = P12[1] + (HAM[1] - 40 - P12[1]) * uu - 230 * math.sin(math.pi * u)
        sc = 1.0 + (0.74 - 1.0) * uu
        rot = -12 * uu + 20 * math.sin(math.pi * u)
        land = 0.0
        if t > jump1:
            el = t - jump1
            land = 0.10 * math.exp(-el * 6) * math.cos(el * 18)
        pose = Pose(x, y + 6 * math.sin(t * 2.0) * (t > jump1), sc * br, rot + 3 * math.sin(t * 2.0) * (t > jump1), 1 - land)
        # ручки: в прыжке раскинуты, в гамаке — заложены за «голову» (вверх-влево)
        rel = smooth(jump1, jump1 + .3, t)
        a1 = pose.pt(BCX - 240, BCY + 40)
        a2 = pose.pt(BCX + 240, BCY + 10)
        r1 = pose.pt(BCX - 225, BCY - 70)
        r2 = pose.pt(BCX + 215, BCY - 90)
        wl = (a1[0] + (r1[0] - a1[0]) * rel, a1[1] + (r1[1] - a1[1]) * rel)
        wr = (a2[0] + (r2[0] - a2[0]) * rel, a2[1] + (r2[1] - a2[1]) * rel)
        al, ar = 200 - 150 * rel, -20 + 160 * rel
        cl, cr = 0.2 + 0.4 * rel, 0.3 + 0.3 * rel
        bl, brd = -30, 40
        load = smooth(jump1 - 0.05, jump1 + 0.1, t) * (1 + 0.25 * math.exp(-max(t - jump1, 0) * 5) * math.cos(max(t - jump1, 0) * 18))
    # два последних стикера — в правой руке до броска из гамака
    late = []
    for j, (col, ic, rr, rest) in enumerate([("green", "trash", 16, (BOX[0] + 10, BOX[1] - BOXH - 30)), ("pink", "calendar", -20, (BOX[0] - 60, BOX[1] - BOXH - 40))]):
        tt0 = TOSS0 + 0.05 * j
        if t < tt0:
            hx, hy = (wr[0] - 70 + j * 14, wr[1] - 30 - j * 12)
            late.append(icons.sticky(hx, hy, col, ic, rr * .3 + 6 * math.sin(t * 4), 0.86, sd=3500 + j * 43, shadow=False))
        else:
            e = t - tt0
            T = TOSS1 - tt0
            if e < T:
                u = e / T
                start = (HAM[0] + 40, HAM[1] - 120)
                x = start[0] + (rest[0] - start[0]) * u
                y = start[1] + (rest[1] - start[1]) * u - 380 * math.sin(math.pi * u)
                st = icons.sticky(x, y, col, ic, -540 * u, 0.86, sd=3500 + j * 43, shadow=False)
                (items_box if u > 0.8 else late).append(st)
            else:
                b = 14 * math.exp(-(e - T) * 10) * abs(math.sin((e - T) * 22))
                items_box.append(icons.sticky(rest[0], rest[1] - b, col, ic, rr, 0.86, sd=3500 + j * 43, shadow=False))
    ropes, ham, bot = hammock(t, load)
    sh = shadow(pose.x, FLOOR + 30, 200 * pose.sc) if t < jump0 + .2 else ""
    # выдох облегчения: завиток пара у лобной доли
    puff = ""
    e = t - (DROP + 0.12)
    if 0 < e < 0.7:
        a_ = smooth(0, .12, e) * (1 - smooth(.45, .7, e))
        px, py = pose.pt(BCX - 150, BCY - 150)
        for k in range(3):
            r = 22 + 26 * ease_out(e / .7) + k * 14
            cx_, cy_ = px - 20 - 30 * ease_out(e / .7) - k * 14, py - 30 - 110 * ease_out(e / .7) - k * 34
            puff += shape(ellipse_pts(cx_, cy_, r, r * .7, 12), "#e9eeff", "", w=3, seed=700 + k)
        puff = f'<g opacity="{a_:.3f}">{puff}</g>'
    # «уф»: лёгкие штрихи-лучики над гамаком после приземления на «держать»
    calm = ""
    if t > REST:
        e = t - REST
        a_ = clamp(e / .12) * (1 - smooth(.5, .8, e))
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.45
            r0 = 160 + 80 * ease_out(e / .6)
            calm += line([(BOX[0] + math.cos(a) * r0, BOX[1] - 200 + math.sin(a) * r0 * .6),
                          (BOX[0] + math.cos(a) * (r0 + 36), BOX[1] - 200 + math.sin(a) * (r0 + 36) * .6)], 7, "#ffe27a", taper=.5, seed=720 + k, op=a_)
    body = brain_with_arms(pose, wl, wr, al, ar, cl, cr, bl, brd, back_items="", hand_items="".join(flying) + "".join(late))
    in_ham = t >= jump1 - 0.08
    art = sh + _ST["box_back"] + "".join(items_box) + _ST["box_front"] + ropes
    if in_ham:
        # мозг лежит в гамаке: передняя кромка ткани поверх нижней части мозга
        cp = [(-600, -600, 1), (W + 600, -600, 1), (W + 600, bot[-1][1], 1)] + [(x, y - 4) for x, y in bot[::-1]] + [(-600, bot[0][1], 1)]
        c = lib.clip_of(cp)
        art += f'<g clip-path="url(#{c})">{body}</g>' + ham
    else:
        art += ham + body
    art += puff + calm
    u = clamp((t - 24.7) / 2.18)
    return art, cam(580 + 10 * u, 800 + 10 * u, 1.0 - 0.06 * ease_io(u), 0.4 - 0.6 * u)


def build_static():
    if _ST:
        return
    _ST["bg"] = background()
    _ST["bgw"] = background(0.6)
    _ST["brain"] = brain_art.brain(0, 0)
    _ST["box_back"] = box_back()
    _ST["box_front"] = box_front()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    fn = {"s05": s05, "s06": s06, "s12": s12}[sid]
    art, cm = fn(t)
    bg = _ST["bgw"] if sid == "s12" else _ST["bg"]
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{bg}{dust(t)}{art}</g>')
