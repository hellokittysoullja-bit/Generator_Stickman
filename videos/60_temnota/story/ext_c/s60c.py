"""Рилс 60 «темнота», группа C: s02 (миф: глаз в темноте), s06 (правда: крест рвётся, галочка), s08 (макро: слеза, боль).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Букв и цифр нет. Глаз — тушь и сплошные заливки, один конструктор eye()
с разными параметрами (радужка, свет, вид), три разные композиции."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
from ink import sample  # noqa: E402
from lib import (INK, T, back_out, blob, blur, clamp, clip_of, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad,  # noqa: E402,F401
                 rrect, shape, smooth, spring)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def decay(t, t0, k=9.0, fr=22.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def path_of(S):
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in S) + "Z"


# ---------------------------------------------------------------- глаз
def eye_pts(cx, cy, w, h, o, lift=0.0):
    o = max(o, .05)
    xs = (-.3, -.05, .22)
    ku = (.30, .46, .38)
    kl = (.26, .36, .30)
    Lc = (cx - w / 2, cy + h * .04, 1)
    Rc = (cx + w / 2, cy - h * .03, 1)
    top, bot = [], []
    for x, a, b in zip(xs, ku, kl):
        yb = cy + h * b * (1 - lift)
        yt = yb + (cy - h * a - yb) * o
        top.append((cx + w * x, yt))
        bot.append((cx + w * x, yb))
    return [Lc] + top + [Rc] + bot[::-1], [Lc] + top + [Rc], [Lc] + bot + [Rc]


def veins(cx, cy, w, h, ic, amount, seed, col, wmul=1.0):
    if amount <= 0:
        return ""
    rs = np.random.RandomState(seed)
    out = []
    n = 16
    starts = []
    for k in range(n):
        side = k % 4
        if side == 0:
            p = (cx - w * .5 + rs.uniform(0, 40), cy + rs.uniform(-.12, .15) * h)
        elif side == 1:
            p = (cx + w * .5 - rs.uniform(0, 40), cy + rs.uniform(-.15, .1) * h)
        elif side == 2:
            p = (cx + rs.uniform(-.42, .42) * w, cy + h * .5)
        else:
            p = (cx + rs.uniform(-.4, .4) * w, cy - h * .52)
        starts.append(p)
    for k, p0 in enumerate(starts):
        th = k / n * .8
        pr = clamp((amount - th) * 3.2)
        if pr <= 0:
            continue
        a = math.atan2(ic[1] - p0[1], ic[0] - p0[0])
        L = math.hypot(ic[0] - p0[0], ic[1] - p0[1]) * rs.uniform(.55, .85)
        pts = [p0]
        for j in range(1, 7):
            u = j / 6 * pr
            aa = a + rs.uniform(-.35, .35)
            pts.append((p0[0] + math.cos(a) * L * u + rs.uniform(-12, 12), p0[1] + math.sin(a) * L * u + rs.uniform(-12, 12)))
        out.append(line(pts, (5.5 + 4.5 * amount) * wmul, col, taper=.8, wmin=.2, peak=.2, seed=40 + k))
        if pr > .5 and k % 2 == 0:
            q = pts[3]
            b = [q, (q[0] + math.cos(a + .8) * 60 * pr, q[1] + math.sin(a + .8) * 60 * pr), (q[0] + math.cos(a + .9) * 110 * pr, q[1] + math.sin(a + .9) * 110 * pr)]
            out.append(line(b, 3.5 * wmul, col, taper=.8, wmin=.2, peak=.2, seed=70 + k))
    return "".join(out)


def eye(cx, cy, w, h, o=1.0, look=(0, 0), lift=0.0, ir=100, pr=.42, cols=("#3a7ca5", "#6fb3d6", "#1d4a6b"), vein=0.0, vcol="#d65a54",
        sclera="#fbf6ee", shade="#dcd3c8", lashes=True, seed=1, inner="", w_ink=9.0, glint=True, wv=1.0, lash_len=1.0):
    pts, up, lo = eye_pts(cx, cy, w, h, o, lift)
    ic = (cx + look[0] * w * .13, cy + look[1] * h * .12 - h * .02)
    clip = clip_of(pts)
    # радужка
    rs = np.random.RandomState(seed)
    iris_pts = ellipse_pts(ic[0], ic[1], ir, ir, n=14, jitter=.015, seed=seed)
    spokes = []
    for k in range(34):
        a = k / 34 * 2 * math.pi + rs.uniform(-.1, .1)
        r0 = ir * pr * 1.05
        r1 = ir * rs.uniform(.72, .97)
        spokes.append(line([(ic[0] + math.cos(a) * r0, ic[1] + math.sin(a) * r0), (ic[0] + math.cos(a) * (r0 + r1) / 2, ic[1] + math.sin(a) * (r0 + r1) / 2),
                            (ic[0] + math.cos(a) * r1, ic[1] + math.sin(a) * r1)], 6 + 3 * (k % 3), cols[1] if k % 2 else cols[2], taper=.6, wmin=.3, seed=k + seed))
    iris = shape(iris_pts, cols[0], "".join(spokes), w=w_ink * .75, seed=seed + 3)
    pup = blob(ellipse_pts(ic[0], ic[1], ir * pr, ir * pr, n=12, jitter=.01, seed=seed), "#0e0c14")
    gl = ""
    if glint:
        gl = (blob(ellipse_pts(ic[0] - ir * .34, ic[1] - ir * .38, ir * .2, ir * .2, n=10), "#ffffff")
              + blob(ellipse_pts(ic[0] + ir * .26, ic[1] + ir * .3, ir * .09, ir * .09, n=8), "#ffffff"))
    S_up = sample(up, False, 3)
    lid_shadow = line(up, h * .16, shade, taper=0, wmin=1, seed=2)
    body = [f'<path d="{__import__("ink").fill_d(pts)}" fill="{sclera}"/>',
            f'<g clip-path="url(#{clip})">', lid_shadow, veins(cx, cy, w, h, ic, vein, seed + 9, vcol, wv), iris, pup, gl, inner, "</g>"]
    # контур век
    body.append(f'<path d="{__import__("ink").ink_closed(pts, w_ink * lib.INK_K[0], var=.3, weight=.55, seed=seed + 5)}" fill="{INK}"/>')
    la = ""
    if lashes:
        for k in range(11):
            u = (k + .5) / 11
            p = S_up[min(len(S_up) - 1, int(u * (len(S_up) - 1)))]
            dx = (p[0] - cx) / (w / 2)
            L = (46 + 40 * u ** 1.5) * lash_len * (.4 + .6 * o)
            ang = math.atan2(-1, dx * .8 + .1)
            e = (p[0] + math.cos(ang) * L, p[1] + math.sin(ang) * L)
            m = (p[0] + math.cos(ang) * L * .5 + dx * 6, p[1] + math.sin(ang) * L * .5 - 4)
            la += line([(p[0], p[1]), m, (e[0] + dx * 22, e[1] + 6)], 7.5, INK, taper=.6, wmin=.15, peak=.25, seed=k + seed)
    body.append(la)
    return "".join(body), ic, pts, up, lo, clip


def brow(cx, cy, w, ang=0.0, col="#3b2c2a", thick=34):
    pts = [(cx - w / 2, cy + 30 + 30 * ang), (cx - w * .2, cy - 10), (cx + w * .1, cy - 22 - 20 * ang), (cx + w / 2, cy + 10 - 40 * ang)]
    from lib import band
    b = band(pts, thick * .5, thick * .2, wmid=thick) if hasattr(lib, "band") else None
    return shape(b, col, w=6, seed=11)


# ---------------------------------------------------------------- рисованные значки
def stroke_bar(cx, cy, length, thick, rot, col, seed=0, s=1.0):
    pts = rrect(cx - length / 2, cy - thick / 2, cx + length / 2, cy + thick / 2, r=thick * .42)
    pts = T(pts, 0, 0, s, rot, cx, cy)
    return shape(pts, col, w=7, seed=seed)


def zigzag(p0, p1, n, amp, seed, u=1.0):
    rs = np.random.RandomState(seed)
    pts = [p0]
    for i in range(1, n + 1):
        k = i / n
        x = p0[0] + (p1[0] - p0[0]) * k
        y = p0[1] + (p1[1] - p0[1]) * k
        nx, ny = -(p1[1] - p0[1]), (p1[0] - p0[0])
        L = math.hypot(nx, ny) or 1
        a = amp * rs.uniform(.4, 1) * (1 if i % 2 else -1) * (1 - .3 * k)
        pts.append((x + nx / L * a, y + ny / L * a))
    m = max(2, int(len(pts) * u) + 1)
    sub = pts[:m]
    if u < 1 and m < len(pts):
        fr = (len(pts) * u) % 1
        a, b = pts[m - 1], pts[m]
        sub = pts[:m - 1] + [a, (a[0] + (b[0] - a[0]) * fr, a[1] + (b[1] - a[1]) * fr)]
    return sub


def spiky(cx, cy, r_in, r_out, n, rot, col, seed=0, s=1.0, w=6):
    rs = np.random.RandomState(seed)
    pts = []
    for i in range(n * 2):
        a = rot + i / (n * 2) * 2 * math.pi
        r = (r_out * rs.uniform(.75, 1.15) if i % 2 == 0 else r_in) * s
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r, 1))
    return shape(pts, col, w=w, seed=seed + 1)


def check_pts(cx, cy, s, u1, u2):
    a, b, c = (cx - 170 * s, cy + 10 * s), (cx - 50 * s, cy + 150 * s), (cx + 220 * s, cy - 150 * s)
    out = []
    if u1 > 0:
        out.append((a, (a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1)))
    if u2 > 0:
        out.append((b, (b[0] + (c[0] - b[0]) * u2, b[1] + (c[1] - b[1]) * u2)))
    return out


def torn_half(hl, th, seed):
    """Половина штриха в своих координатах: наружный конец скруглён (x = +hl/2), у разрыва (x = -hl/2) рваные зубцы."""
    rs = np.random.RandomState(seed)
    r = th / 2
    pts = [(-hl / 2, -r, 1)]
    for k in range(9):
        a = -math.pi / 2 + k / 8 * math.pi
        pts.append((hl / 2 - r + math.cos(a) * r, math.sin(a) * r))
    pts.append((-hl / 2, r, 1))
    n = 5
    for k in range(1, n):
        y = r - 2 * r * k / n
        pts.append((-hl / 2 + (rs.uniform(18, 34) if k % 2 else rs.uniform(-6, 4)), y, 1))
    return pts


def seg_bar(p, q, th, col, seed):
    cx, cy = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    if L < 4:
        return ""
    rot = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
    pts = rrect(cx - L / 2 - th * .3, cy - th / 2, cx + L / 2 + th * .3, cy + th / 2, r=th * .45)
    return shape(T(pts, 0, 0, 1, rot, cx, cy), col, w=7, seed=seed)


# ================================================================ s02: миф, глаз в темноте
T_ISP, T_ZR = wt(5), wt(6)        # 1.98, 2.52


def frame02(t):
    a = 1.3
    z = 1.0 + .2 * ease_io(clamp((t - a) / 2.1)) + .05 * ease_out(clamp((t - a) / .4))
    set_ink(z)
    shk = 20 * decay(t, T_ISP, 7, 21) + 26 * decay(t, T_ZR, 6.5, 19)
    o = []
    g = rad_grad([(0, "#243a66", 1), (.55, "#14203f", 1), (1, "#070a18", 1)], 540, 780, 900, 1000)
    o.append(f'<rect x="-700" y="-700" width="2500" height="3400" fill="url(#{g})"/>')
    # холодный свет вокруг глаза
    gl = rad_grad([(0, "#5f86c9", .55), (1, "#5f86c9", 0)], 540, 760, 520, 360)
    o.append(f'<ellipse cx="540" cy="760" rx="560" ry="400" fill="url(#{gl})"/>')
    # глаз: щурится, когда сгущается тьма
    cx, cy = 540, 760
    dark = ease_io(clamp((t - a) / (T_ISP - a + .1)))
    look = (.9 * math.sin((t - a) * 5.0) * (1 - .7 * dark), .35 * math.sin((t - a) * 7.3 + 1))
    o_lid = 1.0 - .22 * dark - .1 * decay(t, T_ISP, 9, 18) ** 2 * 0
    blinkk = math.exp(-((t - 2.28) / .05) ** 2) * .8 if t > 2.1 else 0
    o_lid = o_lid - blinkk
    # помутнение зрачка и трещина
    uc = ease_out(clamp((t - T_ISP) / .34))
    uk = ease_out(clamp((t - T_ISP - .04) / .3))
    ic0 = (cx + look[0] * 560 * .13, cy + look[1] * 520 * .12 - 10)
    inner = ""
    if uc > 0:
        cl = ellipse_pts(ic0[0], ic0[1], 40 + 112 * uc, 40 + 112 * uc, n=11, jitter=.08, seed=4)
        inner += blob(cl, "#8f95a6") + blob(ellipse_pts(ic0[0] + 14, ic0[1] + 8, (24 + 62 * uc), (24 + 62 * uc), n=9, jitter=.1, seed=8), "#6a7086")
    if uk > 0:
        main = zigzag((cx - 40, cy - 250), (cx + 90, cy + 260), 9, 62, 21, uk)
        br1 = zigzag((cx + 10, cy - 60), (cx + 330, cy - 120), 5, 38, 5, clamp(uk * 1.6 - .5))
        br2 = zigzag((cx + 40, cy + 70), (cx - 260, cy + 140), 5, 38, 9, clamp(uk * 1.6 - .6))
        for k, (pp, w_) in enumerate(((main, 13), (br1, 8), (br2, 8))):
            if len(pp) > 2:
                inner += line(pp, w_, "#14101c", taper=.4, wmin=.3, peak=.4, seed=60 + k)
    ey, ic, pts, up, lo, clip = eye(cx, cy, 860, 540, o_lid, look, 0, ir=135, pr=.42, cols=("#3b78b5", "#79b4e6", "#1c3f72"), vein=0.0, seed=7,
                                    sclera="#eaf0fa", shade="#b4c2dd", inner=inner, w_ink=10)
    # дрожь глаза при ударах
    o.append(f'<g transform="translate({shk * .5:.1f} {shk * .3:.1f})">{ey}</g>')
    # тьма смыкается: сплошные тёмные языки по краям + виньетка
    cl_ = ease_in(clamp((t - a) / (T_ISP - a + .35)), 1.6)
    vg = rad_grad([(0, "#000000", 0), (.45, "#000000", 0), (1, "#000000", .96)], 540, 780, 1100 - 300 * cl_, 1250 - 330 * cl_)
    o.append(f'<rect x="-700" y="-700" width="2500" height="3400" fill="url(#{vg})"/>')
    rs = np.random.RandomState(5)
    for k in range(9):
        ang = k / 9 * 2 * math.pi + .3
        r0 = 1080 - 330 * cl_ + 30 * math.sin(t * 3 + k)
        p = (540 + math.cos(ang) * r0 * 1.0, 780 + math.sin(ang) * r0 * 1.15)
        rr = 190 + 50 * rs.uniform(0, 1)
        o.append(blob(ellipse_pts(p[0], p[1], rr, rr * 1.1, n=9, jitter=.2, seed=k), "#04050c"))
    # красный крест
    uX = (t - T_ZR) / .2
    if uX > 0:
        s = 1 + 1.4 * (1 - back_out(clamp(uX), 1.9)) if uX < 1 else 1
        s = max(s, .1) if uX < 1 else 1
        s0 = back_out(clamp(uX), 2.2)
        ox, oy = shk * .8, shk * .5
        for k, (rot, dly) in enumerate(((45, 0), (-45, .07))):
            uu = clamp((t - T_ZR - dly) / .16)
            if uu > 0:
                o.append(stroke_bar(cx + ox, cy + 10 + oy, 880 * back_out(uu, 1.6), 78, rot, "#e03b3b", seed=30 + k))
    # очки с трещиной
    uG = (t - T_ZR - .1) / .45
    if uG > 0:
        sg = back_out(clamp(uG), 2.0)
        gx, gy = 540, 1100 + 20 * math.sin((t - T_ZR) * 6) * math.exp(-3 * (t - T_ZR))
        rot = -12 * (1 - sg) + 3 * decay(t, T_ZR + .3, 5, 10)
        gg = []
        for sgn in (-1, 1):
            lens = ellipse_pts(gx + sgn * 160, gy, 125, 115, n=14, jitter=.01, seed=sgn + 5)
            gg.append(shape(lens, "#bfe0ee", w=15, seed=10 + sgn))
        gg.append(line([(gx - 40, gy - 20), (gx, gy - 45), (gx + 40, gy - 20)], 15, INK, taper=0, wmin=1, seed=4))
        gg.append(line([(gx - 285, gy - 10), (gx - 370, gy - 60)], 14, INK, taper=.3, wmin=.5, seed=5))
        gg.append(line([(gx + 285, gy - 10), (gx + 370, gy - 60)], 14, INK, taper=.3, wmin=.5, seed=6))
        cr = ease_out(clamp((t - T_ZR - .25) / .22))
        for k, (pp, w_) in enumerate(((zigzag((gx + 225, gy - 100), (gx + 115, gy + 100), 6, 22, 3, cr), 9),
                                      (zigzag((gx + 172, gy - 15), (gx + 268, gy + 22), 3, 15, 6, cr), 6),
                                      (zigzag((gx + 160, gy + 8), (gx + 75, gy - 50), 3, 15, 8, cr), 6))):
            if len(pp) > 2:
                gg.append(line(pp, w_, INK, taper=.3, wmin=.4, seed=80 + k))
        o.append(f'<g transform="translate({gx} {gy}) rotate({rot:.2f}) scale({sg:.3f}) translate({-gx} {-gy})">{"".join(gg)}</g>')
    cam = lib.cam(540 + shk, 880 + shk * .6, z, 1.2 * decay(t, T_ISP, 6, 15) + 1.6 * decay(t, T_ZR, 5, 13))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ================================================================ s06: правда, крест стирается и рвётся, галочка
T_NE, T_POR = wt(25), wt(26)      # 8.613, 8.784


def frame06(t):
    a = 7.7
    # камера: наезд с разгоном к галочке
    ui = ease_in(clamp((t - a) / 1.9), 2.2)
    z = 1.0 + .45 * ui
    set_ink(z)
    shk = 18 * decay(t, T_NE, 7, 22) + 12 * decay(t, T_POR, 8, 25)
    o = []
    g = rad_grad([(0, "#fff6c9", 1), (.6, "#f8e7b0", 1), (1, "#efd596", 1)], 540, 840, 1000, 1000)
    o.append(f'<rect x="-700" y="-700" width="2500" height="3400" fill="url(#{g})"/>')
    # лучи солнца
    spin = t * .25
    for k in range(14):
        a0 = spin + k / 14 * 2 * math.pi
        a1 = a0 + .13
        pts = [(540, 840, 1), (540 + math.cos(a0) * 1700, 840 + math.sin(a0) * 1700, 1), (540 + math.cos(a1) * 1700, 840 + math.sin(a1) * 1700, 1)]
        o.append(blob(pts, "#fdf0bf"))
    cx, cy = 540, 830
    # взгляд следит за ластиком, потом облегчённо вверх
    uer = clamp((t - a) / (T_NE - a))
    look = (-.7 + 1.4 * uer, -.3 + .6 * uer) if t < T_NE else (0, -.15 * smooth(T_POR, T_POR + .4, t))
    happy = smooth(T_POR, T_POR + .35, t)
    ey, ic, pts, up, lo, clip = eye(cx, cy, 860, 620, 1.0 - .04 * math.exp(-((t - 8.3) / .07) ** 2) * 6 + .05 * happy, look, lift=.18 * happy, ir=160, pr=.38,
                                    cols=("#5f9a45", "#a6d36b", "#2f6a2f"), vein=0.0, seed=12, sclera="#fffaf0", shade="#e9dfcc", w_ink=11, lash_len=1.15)
    # бровь
    o.append(brow(cx + 10, cy - 400 - 12 * happy, 640, ang=-.4 * happy, thick=40))
    o.append(f'<g transform="translate({shk * .5:.1f} {shk * .3:.1f})">{ey}</g>')
    # крест мифа: штрих «\» стирает ластик, штрих «/» рвётся на «не»
    red = "#e03b3b"
    ox, oy = shk * .5, shk * .3
    L = 930
    # «\» (rot 45): виден, пока ластик не прошёл
    er = ease_io(clamp((t - (a + .02)) / (T_NE - a - .12)))
    # ластик движется вдоль штриха сверху-слева вниз-вправо
    s0 = (cx - 330, cy - 330)
    s1 = (cx + 330, cy + 330)
    ex, ey_ = s0[0] + (s1[0] - s0[0]) * er, s0[1] + (s1[1] - s0[1]) * er
    if er < 1:
        # полоса «\» — только часть впереди ластика
        rem = (1 - er)
        p_a = (ex, ey_)
        bar = seg_bar(p_a, (s1[0] + 40, s1[1] + 40), 80, red, 31)
        o.append(bar)
        # ластик (блок с рукавом) и крошки
        er_pts = rrect(-80, -48, 80, 48, r=22)
        er_g = shape(T(er_pts, ex, ey_, 1, 45 + 8 * math.sin(t * 22)), "#f3a3b6", w=8, seed=7)
        sl = shape(T(rrect(-80, -2, 80, 48, r=22), ex, ey_, 1, 45 + 8 * math.sin(t * 22)), "#4a79c9", w=0, ink=False)
        o.append(er_g + sl)
        for k in range(5):
            ph = (t * 3 + k * .37) % 1
            o.append(blob(ellipse_pts(ex - 60 + 45 * k - 100 * ph * 0, ey_ - 30 + 140 * ph, 9, 7, n=7, seed=k), "#f3a3b6"))
    # «/» (rot -45): цела до «не»
    if t < T_NE:
        bobk = 5 * math.sin(t * 30)
        o.append(stroke_bar(cx + ox, cy + oy + bobk * .3, L, 80, -45, red, seed=33))
    else:
        u = t - T_NE
        # штрих разорван посередине: две половины с рваным краем разлетаются вдоль себя и падают
        for sgn in (-1, 1):
            hl = L / 2 - 20
            d = hl / 2 + 14 + 300 * u + 900 * u * u
            px = cx + sgn * d * math.cos(math.radians(45)) + ox
            py = cy - sgn * d * math.sin(math.radians(45)) - 120 * u + 1500 * u * u + oy
            rot = (-45 if sgn > 0 else 135) + sgn * 70 * u
            if py < 1700:
                o.append(shape(T(torn_half(hl, 80, 70 + sgn), px, py, 1, rot), red, w=7, seed=40 + sgn))
        # вспышка разрыва: острые штрихи из центра
        if u < .3:
            for k in range(8):
                aa = k / 8 * 2 * math.pi + .4
                r0, r1 = 60 + 220 * u / .3, 150 + 300 * u / .3
                o.append(line([(cx + math.cos(aa) * r0, cy + math.sin(aa) * r0), (cx + math.cos(aa) * r1, cy + math.sin(aa) * r1)], 12, "#d4492f",
                              taper=.5, wmin=.2, seed=k + 3))
    # зелёная галочка из штрихов
    uc = t - T_POR
    if uc > -0.0:
        u1 = ease_out(clamp(uc / .13))
        u2 = ease_out(clamp((uc - .1) / .17))
        pulse = 1 + .1 * spring(uc - .28, 3.2, 6) if uc > .28 else 1
        cxk, cyk = cx - 20, cy + 20
        gcol = "#2fae5a"
        grp = []
        for k, (p, q) in enumerate(check_pts(cxk, cyk, 1.15 * pulse, u1, u2)):
            grp.append(seg_bar(p, q, 92, gcol, 50 + k))
        # блик на штрихе
        for k, (p, q) in enumerate(check_pts(cxk, cyk, 1.15 * pulse, u1, u2)):
            dx, dy = q[0] - p[0], q[1] - p[1]
            Ln = math.hypot(dx, dy) or 1
            nx, ny = dy / Ln, -dx / Ln
            grp.append(line([(p[0] + dx * .15 + nx * 20, p[1] + dy * .15 + ny * 20), (q[0] - dx * .15 + nx * 20, q[1] - dy * .15 + ny * 20)], 11, "#8be3a8",
                            taper=.3, wmin=.5, seed=90 + k))
        o.append("".join(grp))
        # колючки-искры вокруг
        if uc < .55:
            for k in range(10):
                aa = k / 10 * 2 * math.pi + .2
                uu = clamp(uc / .5)
                r0, r1 = 330 + 90 * ease_out(uu), 380 + 150 * ease_out(uu)
                lw = 11 * (1 - uu)
                if lw > 1:
                    o.append(line([(cxk + math.cos(aa) * r0, cyk + math.sin(aa) * r0), (cxk + math.cos(aa) * r1, cyk + math.sin(aa) * r1)], lw,
                                  "#f2b705" if k % 2 else "#2fae5a", taper=.5, wmin=.2, seed=k + 9))
    cx_c = cx + (-20) * ui * .8 + shk
    cam = lib.cam(cx_c, cy - 30 + 40 * ui + shk * .5, z, -.5 * ui + .8 * decay(t, T_NE, 6, 15))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ================================================================ s08: макро, слеза и боль
T_SLE, T_BOL = wt(31), wt(33)     # 11.227, 11.98


def skin_poly(S, ytop):
    pts = [(S[0][0] - 400, ytop)] + [tuple(p) for p in S] + [(S[-1][0] + 400, ytop)]
    return path_of(pts)


def frame08(t):
    a = 11.0
    ui = ease_io(clamp((t - a) / 1.7))
    z = 1.0 + .28 * ui
    set_ink(z)
    shk = 22 * decay(t, T_BOL, 6, 23) + 6 * decay(t, T_SLE + .5, 9, 20)
    o = []
    g = lib.lin_grad([(0, "#d99b7c", 1), (.5, "#eeb99a", 1), (1, "#f4c7a9", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="-700" y="-700" width="2500" height="3400" fill="url(#{g})"/>')
    cx, cy, w, h = 540, 790, 1440, 760
    pain = smooth(T_BOL - .05, T_BOL + .25, t)
    ve = .55 + .4 * smooth(a, T_BOL, t)
    o_lid = .62 - .17 * pain - .06 * math.exp(-((t - 11.55) / .12) ** 2) * 3
    look = (-.3 + .2 * math.sin((t - a) * 2.2), .35 + .1 * math.sin((t - a) * 3.1))
    pts, up, lo = eye_pts(cx, cy, w, h, o_lid)
    Su = sample(up, False, 4)
    Sl = sample(lo, False, 4)
    # веки-кожа вокруг
    o.append(f'<path d="{skin_poly(Su, -400)}" fill="#cf8f6f"/>')
    crease = [(p[0], p[1] - 90 - 60 * math.sin((p[0] - cx) / w * 3)) for p in Su[::max(1, len(Su) // 9)]]
    o.append(line(crease, 11, "#a86a54", taper=.5, wmin=.2, seed=3))
    o.append(f'<path d="{path_of([(Sl[0][0] - 400, 2200)] + [tuple(p) for p in Sl] + [(Sl[-1][0] + 400, 2200)])}" fill="#f1bf9f"/>')
    bag = [(p[0], p[1] + 70 + 25 * math.sin((p[0] - cx) / w * 3)) for p in Sl[::max(1, len(Sl) // 9)]]
    o.append(line(bag, 12, "#b9785d", taper=.5, wmin=.2, seed=6))
    # воспалённый край нижнего века
    red = mix("#e8a78a", "#d4574f", ve)
    ey, ic, pts, up, lo, clip = eye(cx, cy, w, h, o_lid, look, 0, ir=215, pr=.4, cols=("#8a5a2b", "#c99552", "#4b2c14"), vein=ve, vcol="#d1403f",
                                    sclera="#fbf0e6", shade="#e6cfc2", seed=22, w_ink=11, wv=1.5 + pain * .5, lash_len=1.5, glint=False)
    # блики окна на радужке (сплошные)
    gl = (blob(rrect(ic[0] - 140, ic[1] - 120, ic[0] - 40, ic[1] - 40, r=20), "#ffffff") + blob(ellipse_pts(ic[0] + 90, ic[1] + 90, 26, 26, n=8), "#ffffff"))
    ey = ey.replace("</g>", f"{gl}</g>", 1) if False else ey
    o.append(f'<g transform="translate({shk * .6:.1f} {shk * .35:.1f})">{ey}<g clip-path="url(#{clip})">{gl}</g></g>')
    o.append(line(lo, 24, red, taper=0, wmin=.9, seed=8))
    # слеза: линза воды на нижнем веке, потом капля катится по щеке
    ut = t - T_SLE
    if ut > 0:
        xs0 = cx - 90
        yl = np.interp(xs0, [p[0] for p in Sl], [p[1] for p in Sl])
        men = ease_out(clamp(ut / .35))
        sub = [p for p in Sl if abs(p[0] - xs0) < 320 * men]
        if len(sub) > 3:
            o.append(line([tuple(p) for p in sub], 26 * men, "#8fd0f2", taper=.4, wmin=.4, seed=3))
        uf = clamp((ut - .3) / .62)
        if uf > 0:
            fall = ease_in(uf, 1.7)
            ty = yl + 60 + 190 * fall
            tx = xs0 + 25 * math.sin(uf * 2.2)
            sz = 1.6 * (.6 + .4 * clamp(uf * 4)) * (1 - .15 * uf)
            drop = [(tx, ty - 80 * sz, 1), (tx + 44 * sz, ty - 4 * sz), (tx + 36 * sz, ty + 46 * sz), (tx, ty + 66 * sz), (tx - 36 * sz, ty + 46 * sz), (tx - 44 * sz, ty - 4 * sz)]
            # мокрая дорожка за каплей
            if fall > .02:
                o.append(line([(xs0 + 2, yl + 10), (xs0 + (tx - xs0) * .5 + 6, (yl + ty) / 2), (tx, ty - 40 * sz)], 30, "#9cd6f3", taper=.2, wmin=.55, peak=.9, seed=2))
            o.append(shape(drop, "#6fbfec", w=7, seed=15))
            o.append(blob(ellipse_pts(tx - 14 * sz, ty - 4 * sz, 9 * sz, 15 * sz, n=8), "#ffffff"))
        # блеск мокрого глаза
    # боль: колючие штрихи вокруг глаза
    ub = t - T_BOL
    if ub > 0:
        spots = [(cx - 330, cy - 330, 1.0, -.3), (cx - 120, cy - 400, .8, .2), (cx + 130, cy - 380, 1.1, .9), (cx + 340, cy - 320, .9, 1.6),
                 (cx + 360, cy + 300, .9, 3.0), (cx - 360, cy + 320, .85, 3.7), (cx + 120, cy + 380, .7, 4.4)]
        for k, (sx, sy, ss, rot) in enumerate(spots):
            uu = clamp((ub - .025 * k) / .22)
            if uu <= 0:
                continue
            life = 1 - smooth(.55, .85, ub)
            if life <= .01:
                continue
            sc = back_out(uu, 2.4) * ss * (.7 + .3 * life) * (1 + .08 * math.sin(t * 40 + k))
            o.append(spiky(sx + 6 * math.sin(t * 33 + k), sy + 5 * math.cos(t * 29 + k), 28, 96, 6, rot + t * 2, "#ffb21a" if k % 2 else "#ff5a36", seed=k + 3, s=sc))
        # красные «ножи» от уголков глаза
        for k, sgn in enumerate((-1, 1)):
            uu = ease_out(clamp(ub / .2))
            pts2 = zigzag((cx + sgn * 300, cy - 150), (cx + sgn * 430, cy - 300), 3, 26, 5 + k, uu)
            if len(pts2) > 2:
                o.append(line(pts2, 14, "#c2262e", taper=.4, wmin=.3, seed=20 + k))
    cam = lib.cam(cx + shk, cy + 140 * ui + shk * .6, z, 1.5 * decay(t, T_BOL, 6, 17) * 1.0)
    return f'<g transform="{cam}">{"".join(o)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    fn = {"s02": frame02, "s06": frame06, "s08": frame08}[sid]
    body = fn(t)
    return lib.svg(body)
