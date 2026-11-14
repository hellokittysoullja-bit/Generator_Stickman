"""«На самом деле»: совы и жаворонки (рилс 43).
s07 (10.16–12.5): экран разделён по диагонали на ночь (луна, звёзды) и утро (солнце, облака); на «сова» (11.12) на ночной
стороне на ветке выскакивает круглая сова; на «жаворонок» (11.92) на дневную сторону влетает жаворонок и поёт (ноты).
Влёт камеры с первого кадра, толчок на каждой птице.
s08 (12.5–14.72): спираль ДНК вращается; на «заложено» (13.12) в перекладинах загораются значки луны и солнца; на
«рождения» (13.84) внизу появляется люлька, в ней младенец в шапочке с ушками совы, качается. Медленный отъезд."""
import math

import numpy as np

import lib
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, rad_grad,
                 rect_pts, shape, smooth, spring, svg, T)

_ST = {}
OWL_T = 11.12     # «сова»
LARK_T = 11.92    # «жаворонок»
GENE_T = 13.12    # «заложено»
BORN_T = 13.84    # «рождения»
NIGHT, NIGHT2, DAY, DAY2 = "#16205a", "#2b3a86", "#9fd2f2", "#e9f6ff"


def back_pop(e, d=0.16, over=0.22):
    if e <= 0:
        return 0.0
    u = clamp(e / d)
    if u < 1:
        return 1.08 * ease_out(u, 2)
    ee = e - d
    return 1 + over * 0.36 * math.exp(-ee * 8) * math.cos(ee * 20 + 1.2)


def moon(cx, cy, r, sd, col="#fff1b8", sh="#e9d38a"):
    outer = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(math.radians(40), math.radians(320), 22)]
    inner = [(cx + r * 0.42 + r * 0.82 * math.cos(a), cy - r * 0.08 + r * 0.82 * math.sin(a))
             for a in np.linspace(math.radians(300), math.radians(60), 18)]
    pts = outer + inner
    return shape(pts, col, blob(ellipse_pts(cx - r * .45, cy + r * .3, r * .14, r * .1, 8), sh) +
                 blob(ellipse_pts(cx - r * .55, cy - r * .25, r * .1, r * .08, 8), sh), w=max(3, r * .07), seed=sd)


def sun(cx, cy, r, t, sd, rays=True):
    s = []
    if rays:
        for j in range(12):
            a = math.radians(t * 30 + j * 30)
            L = r * (0.42 + 0.12 * (j % 2))
            s.append(line([(cx + (r * 1.18) * math.cos(a), cy + (r * 1.18) * math.sin(a)),
                           (cx + (r * 1.18 + L) * math.cos(a), cy + (r * 1.18 + L) * math.sin(a))], max(4, r * .11), "#ffbf3a",
                          taper=.3, wmin=.5, seed=sd + j))
    s.append(shape(ellipse_pts(cx, cy, r, r, 26), "#ffd650", blob(ellipse_pts(cx + r * .25, cy + r * .25, r, r, 24), "#f5b836", .9) +
                   blob(ellipse_pts(cx - r * .4, cy - r * .42, r * .3, r * .17, 12, rot=-30), "#fff2b0", .9), w=max(3, r * .05), seed=sd + 20))
    return "".join(s)


def star(x, y, r, col, op=1.0):
    pts = []
    for j in range(8):
        a = j * math.pi / 4 - math.pi / 2
        q = r * (2.4 if j % 2 == 0 else 0.7)
        pts.append((x + q * math.cos(a), y + q * math.sin(a)))
    return blob(pts, col, op)


def cloud(cx, cy, sc, sd):
    pts = [(cx - 120 * sc, cy + 30 * sc, 1)]
    for (dx, dy, r) in ((-90, 0, 50), (-30, -40, 64), (50, -30, 56), (110, 6, 44)):
        for a in np.linspace(math.pi * 1.05, math.pi * 1.95, 5):
            pts.append((cx + (dx + r * math.cos(a)) * sc, cy + (dy + r * math.sin(a)) * sc))
    pts.append((cx + 150 * sc, cy + 30 * sc, 1))
    return shape(pts, "#ffffff", blob([(cx - 130 * sc, cy + 10 * sc), (cx + 160 * sc, cy + 10 * sc), (cx + 160 * sc, cy + 40 * sc),
                                       (cx - 130 * sc, cy + 40 * sc)], "#dbe9f5"), w=4, seed=sd)


# ─────────────────────────────── сова
OWL_B, OWL_SH, OWL_BELLY = "#8a6a4a", "#6c5036", "#e8d2a8"


def owl(cx, cy, sc, t, blink=0.0, look=(0.0, 0.0), flap=0.0, sd=1300):
    """Круглая сова, центр тела (cx, cy), ступни на cy + 150·sc."""
    g = []
    # крылья (за телом, машут на выскакивании)
    for side in (-1, 1):
        a = side * (8 + 34 * flap)
        wing = [(0, -60), (side * 40, -40), (side * 62, 20), (side * 52, 90), (side * 24, 120), (side * 8, 60)]
        mv = lambda q: T([(p[0] + side * 86, p[1] + 10) for p in q], 0, 0, 1.0, a, side * 90, -40)
        wing = mv(wing)
        g.append(shape(wing if side > 0 else wing[::-1], OWL_SH, blob(mv([(side * 20, 40), (side * 50, 60), (side * 40, 100), (side * 14, 90)]),
                                                                       "#56402a"), w=4.4, seed=sd + 1 + side))
    # тело-яйцо с ушками
    body = [(-118, 30), (-112, -60), (-96, -118), (-110, -176, 1), (-58, -142), (0, -150), (58, -142), (110, -176, 1), (96, -118),
            (112, -60), (118, 30), (96, 104), (40, 142), (-40, 142), (-96, 104)]
    inner = blob([(30, -150), (118, -80), (118, 40), (90, 110), (40, 142), (70, 30)], OWL_SH, .9)
    inner += blob(ellipse_pts(0, 64, 70, 76, 20), OWL_BELLY)
    for r in range(3):
        for c in range(3 - (r % 2)):
            x = -34 + c * 34 + (17 if r % 2 else 0)
            y = 30 + r * 30
            inner += line([(x - 10, y), (x, y + 8), (x + 10, y)], 3.2, "#b89566", taper=.3, wmin=.4, seed=sd + 10 + r * 3 + c)
    g.append(shape(body, OWL_B, inner, w=5.4, seed=sd + 4))
    # лицевые диски
    for side in (-1, 1):
        g.append(shape(ellipse_pts(side * 46, -66, 48, 46, 18), "#f1e1c0", blob(ellipse_pts(side * 46 + 8, -60, 42, 38, 16), "#e2cca2", .8),
                       w=3.6, seed=sd + 6 + side))
    # глаза
    for side in (-1, 1):
        ex, ey = side * 46, -66
        if blink < 0.9:
            ry = 34 * (1 - blink)
            ey2 = ey + 34 * blink * 0.4
            eye = ellipse_pts(ex, ey2, 34, max(3, ry), 18)
            pup = (f'<circle cx="{f(ex + look[0] * 9)}" cy="{f(ey2 + look[1] * 8)}" r="{f(min(17, ry * .55))}" fill="{INK}"/>'
                   f'<circle cx="{f(ex + look[0] * 9 - 6)}" cy="{f(ey2 + look[1] * 8 - 7)}" r="5" fill="#ffffff"/>')
            g.append(shape(eye, "#ffc93a", blob(ellipse_pts(ex + 8, ey2 + 10, 28, ry * .7, 14), "#f0a92a", .8) + pup, w=4, seed=sd + 8 + side))
        else:
            g.append(line([(ex - 30, ey + 8), (ex, ey + 16), (ex + 30, ey + 8)], 5, seed=sd + 9 + side))
    # брови-перья
    for side in (-1, 1):
        g.append(line([(side * 12, -104), (side * 50, -116), (side * 90, -100)], 6, "#4a3420", taper=.4, wmin=.3, seed=sd + 12 + side))
    # клюв
    g.append(shape([(-14, -42, 1), (14, -42, 1), (0, -8, 1)], "#f39a2a", blob([(2, -42), (14, -42), (0, -8)], "#d07818"), w=3.4, seed=sd + 14))
    # лапки
    for side in (-1, 1):
        for k in (-1, 0, 1):
            g.append(line([(side * 34 + k * 12, 136), (side * 34 + k * 16, 156)], 7, "#f39a2a", taper=.2, wmin=.6, seed=sd + 20 + k + side * 3))
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({sc:.4f})">{"".join(g)}</g>'


def branch(x0, y0, x1, y1, t, sd):
    s = []
    sw = 4 * math.sin(t * 1.3)
    pts = [(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 14), (x1, y1 + sw)]
    band = lib.band(pts, 44, 18, step=6, cap=True)
    s.append(shape(band, "#5c3e26", blob(lib.band([(p[0], p[1] + 10) for p in pts], 20, 8, step=6, cap=False), "#47301c"), w=4.6, seed=sd))
    for k, (u, ang, sz) in enumerate(((0.35, -40, 1.0), (0.62, 30, .9), (0.85, -25, .8), (0.5, 150, .85))):
        bx = x0 + (x1 - x0) * u
        by = y0 + (y1 - y0) * u - 10 + sw * u
        a = math.radians(ang + 6 * math.sin(t * 2 + k))
        tip = (bx + 70 * sz * math.cos(a), by + 70 * sz * math.sin(a))
        nx, ny = -math.sin(a) * 24 * sz, math.cos(a) * 24 * sz
        mid = ((bx + tip[0]) / 2, (by + tip[1]) / 2)
        leaf = [(bx, by, 1), (mid[0] + nx, mid[1] + ny), (tip[0], tip[1], 1), (mid[0] - nx, mid[1] - ny)]
        s.append(shape(leaf, "#2f6a4a", line([(bx, by), tip], 2.6, "#1f4a32", seed=sd + 10 + k), w=3.6, seed=sd + 5 + k))
    return "".join(s)


# ─────────────────────────────── жаворонок
LARK, LARK_SH, LARK_BELLY = "#b07d4a", "#8a5c32", "#f4e2c0"


def lark(cx, cy, sc, t, flap_ph, beak=0.0, sd=1500):
    """Маленький жаворонок в профиль, смотрит влево; центр тела (cx, cy). Крылья острые, машут от плеча."""
    g = []
    wa = math.sin(flap_ph)
    sh = (4, -34)
    wing0 = [(-14, -30), (30, -44), (96, -70), (156, -86, 1), (112, -46), (50, -18), (6, -14)]

    def wing(k):
        return T(wing0, 0, 0, 1.0, (-58 + 8 * k) * wa - 6 + 4 * k, sh[0], sh[1])
    fw = wing(0)
    g.append(shape(fw, LARK_SH, "", w=3.6, seed=sd))
    # хвост-клин
    g.append(shape([(56, -22), (132, -40, 1), (142, -12, 1), (64, 6)], LARK_SH, line([(74, -12), (134, -26)], 2.6, "#6a4424", seed=sd + 2),
                   w=3.6, seed=sd + 1))
    # тело с головой одним силуэтом и хохолком
    body = [(-92, -34), (-84, -58), (-64, -70), (-44, -88, 1), (-38, -64), (0, -50), (44, -36), (72, -14), (52, 20), (6, 34),
            (-44, 30), (-76, 8)]
    inner = blob([(-80, 0), (-40, 8), (20, 14), (52, 20), (6, 34), (-44, 30)], LARK_BELLY)
    for k in range(4):
        inner += blob(ellipse_pts(-44 + k * 18, 16 + (k % 2) * 7, 3.5, 5.5, 6), "#a07040")
    inner += blob([(-36, -60), (10, -50), (50, -32), (20, -34)], LARK_SH, .8)
    inner += line([(-80, -30), (-60, -26), (-46, -16)], 3, "#7a5030", seed=sd + 5)
    g.append(shape(body, LARK, inner, w=4.4, seed=sd + 3))
    g.append(f'<circle cx="-68" cy="-44" r="8" fill="{INK}"/><circle cx="-71" cy="-47" r="2.8" fill="#fff"/>')
    op = 14 * beak
    g.append(shape([(-90, -44), (-128, -38 - op), (-90, -30)], "#e8a43a", "", w=3, seed=sd + 6))
    g.append(shape([(-90, -30), (-124, -28 + op * .6), (-88, -20)], "#c8862a", "", w=3, seed=sd + 7))
    nw = wing(1)
    g.append(shape(nw, LARK, blob(T([(60, -48), (150, -84), (112, -46), (60, -30)], 0, 0, 1.0, (-50) * wa - 2, sh[0], sh[1]), LARK_SH, .9) +
                   line(T([(20, -32), (100, -58)], 0, 0, 1.0, (-50) * wa - 2, sh[0], sh[1]), 2.6, "#6a4424", seed=sd + 9), w=4, seed=sd + 8))
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({sc:.4f})">{"".join(g)}</g>'


def note(x, y, sc, rot, sd, col="#ffd650", double=False):
    """Нота: жёлтая с контуром тушью — читается и на ночи, и на дне."""
    def parts(c, k):
        g = [blob(ellipse_pts(0, 0, 18 + k, 13 + k, 12, rot=-24), c),
             line([(15, -4), (16, -78)], 6 + 2 * k, c, taper=.02, wmin=.95, seed=sd)]
        if double:
            g.append(blob(ellipse_pts(50, -10, 18 + k, 13 + k, 12, rot=-24), c))
            g.append(line([(65, -14), (66, -88)], 6 + 2 * k, c, taper=.02, wmin=.95, seed=sd + 1))
            g.append(line([(16, -78), (66, -88)], 12 + 2 * k, c, taper=.02, wmin=.95, seed=sd + 2))
        else:
            g.append(line([(16, -78), (34, -60), (36, -42)], 8 + 2 * k, c, taper=.3, wmin=.5, seed=sd + 3))
        return "".join(g)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sc:.4f})">{parts(INK, 5)}{parts(col, 0)}</g>'


# ─────────────────────────────── s07
DIAG = lambda x: 1340 - x * 0.95      # граница: выше — ночь


def s07_world(t):
    s = []
    # день — весь фон, ночь — треугольник сверху-слева
    g = lin_grad([(0, DAY2, 1), (1, DAY, 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-700" y="-700" width="2500" height="3300" fill="url(#{g})"/>')
    s.append(sun(900, 720, 110, t, 1200))
    s.append(cloud(360, 1230, 0.9, 1220))
    s.append(cloud(960, 1050, 0.7, 1221))
    # холмы дня
    s.append(shape([(-700, 1500), (200, 1400), (700, 1330), (1200, 1290), (1800, 1300), (1800, 2600, 1), (-700, 2600, 1)], "#8bc46a",
                   blob([(700, 1380), (1800, 1330), (1800, 1420), (700, 1440)], "#76ad58", .9), w=4.4, seed=1230))
    ng = lin_grad([(0, NIGHT, 1), (1, NIGHT2, 1)], 0, 0, 1, 1)
    npts = [(-700, -700, 1), (1800, -700, 1), (1800, DIAG(1800), 1), (-700, DIAG(-700), 1)]
    nin = ""
    for k, (x, y, r) in enumerate(((120, 180, 6), (420, 120, 5), (620, 260, 4), (80, 520, 4), (300, 760, 5), (760, 120, 6),
                                   (520, 520, 4), (170, 980, 4), (880, 260, 3.5), (40, 760, 3.5))):
        tw = 0.6 + 0.4 * math.sin(t * (3 + k % 3) + k)
        nin += star(x, y, r * (0.8 + 0.3 * tw), "#fff4c8", 0.5 + 0.5 * tw)
    nin += moon(700, 230, 84, 1240)
    s.append(shape(npts, f"url(#{ng})", nin, w=0, seed=1241, ink=False))
    s.append(line([(-700, DIAG(-700)), (1800, DIAG(1800))], 8, INK, taper=.02, wmin=.95, seed=1242))
    # ветка и сова
    s.append(branch(-60, 760, 470, 700, t, 1250))
    e = t - OWL_T + 0.04
    if e > 0:
        k = back_pop(e)
        dy = 120 * (1 - min(1, e / 0.16))
        flap = math.exp(-e * 4) * abs(math.sin(e * 14))
        blink = 0.0
        for c, hl in ((11.9, .07), (12.55, .07)):
            if c - hl <= t <= c + hl:
                blink = 1 - abs(t - c) / hl
        look = (0.6 * smooth(LARK_T, LARK_T + 0.25, t), 0.4 * smooth(LARK_T, LARK_T + 0.25, t))
        s.append(owl(250, 560 + dy, 1.05 * k, t, blink, look, flap))
        if e < 0.35:
            for j in range(5):
                a = math.radians(-160 + j * 35)
                r0 = 210 + 260 * e
                s.append(line([(250 + r0 * math.cos(a), 560 + r0 * math.sin(a)), (250 + (r0 + 60) * math.cos(a), 560 + (r0 + 60) * math.sin(a))],
                              10 * (1 - e / 0.35) + 1, "#fff4c8", taper=.4, seed=1260 + j))
    # перед совой ветка спереди не нужна: ступни на ветке
    # жаворонок
    e = t - LARK_T + 0.08
    if e > 0:
        u = ease_out(clamp(e / 0.32), 3)
        lx = 1280 + (680 - 1280) * u
        ly = 1140 + (1020 - 1140) * u - 60 * math.sin(math.pi * u) + 10 * math.sin(t * 7)
        sing = clamp((e - 0.3) / 0.1)
        beak = sing * (0.5 + 0.5 * math.sin(t * 22))
        s.append(lark(lx, ly, 1.6, t, t * 2 * math.pi * 5.5, beak))
        if e > 0.3:
            for j in range(4):
                ee = (e - 0.3) - j * 0.18
                if ee <= 0:
                    continue
                ph = ee % 1.2
                nx = lx - 260 - ph * 120 - j * 10
                ny = ly - 110 - ph * 200 + 30 * math.sin(ph * 6 + j)
                sc = min(1, ph / 0.12) * (1 - smooth(0.9, 1.2, ph)) * (1.05 - 0.1 * j)
                if sc > 0.05:
                    s.append(note(nx, ny, sc * 1.1, -14 + 12 * math.sin(ph * 5 + j), 1280 + j * 5, "#ffd650", double=(j % 2 == 1)))
    return "".join(s)


def s07_cam(t):
    t0 = 9.96
    e0 = t - t0
    if e0 < 0.22:
        u = ease_out(e0 / 0.22, 3)
        sc = 0.72 + (1.05 - 0.72) * u
        rot = 3 * (1 - u)
    else:
        e = e0 - 0.22
        sc = 1 + 0.05 * math.exp(-e * 9) * math.cos(e * 15)
        rot = -0.6 * math.exp(-e * 7) * math.sin(e * 16)
    cx, cy = 540, 880
    # толчок к сове, потом к жаворонку
    ko = smooth(OWL_T - 0.05, OWL_T + 0.25, t) * (1 - smooth(LARK_T - 0.05, LARK_T + 0.3, t))
    kl = smooth(LARK_T - 0.05, LARK_T + 0.3, t)
    cx += -60 * ko + 40 * kl
    cy += -60 * ko + 40 * kl
    sc *= 1 + 0.04 * ko + 0.04 * kl
    for hit in (OWL_T, LARK_T):
        e = t - hit
        if e >= 0:
            k = math.exp(-e * 8)
            sc *= 1 + 0.06 * k * min(1, e / 0.04)
            cy += 8 * k * math.sin(e * 40)
    return cx, cy, sc, rot


# ─────────────────────────────── s08: ДНК и люлька
HX, HY0, HY1 = 540, 110, 850     # ось спирали
AMP, PERIOD = 225, 440.0
RUNG_COL = ["#e8574a", "#3a8fd8", "#f2b83a", "#4bb06a"]


def helix(t):
    ph = t * 2.2
    ys = np.arange(HY0, HY1 + 1, 6.0)

    def xs(y, off):
        return HX + AMP * np.sin(2 * math.pi * (y - HY0) / PERIOD + ph + off)

    def zs(y, off):
        return np.cos(2 * math.pi * (y - HY0) / PERIOD + ph + off)

    back, front, rungs = [], [], []
    # нити кусками по глубине
    for off, col, colsh in ((0.0, "#7b5cd6", "#5c40b0"), (math.pi, "#e0559a", "#b83a78")):
        x, z = xs(ys, off), zs(ys, off)
        seg, cur = [], None
        for i in range(len(ys)):
            fr = z[i] > 0
            if cur is None or fr != cur:
                if seg:
                    (front if cur else back).append((seg, col if cur else colsh))
                seg = [(x[i - 1], ys[i - 1])] if i else []
                cur = fr
            seg.append((x[i], ys[i]))
        (front if cur else back).append((seg, col if cur else colsh))
    n = 12
    for j in range(n):
        y = HY0 + 30 + j * (HY1 - HY0 - 60) / (n - 1)
        xa, xb = float(xs(y, 0)), float(xs(y, math.pi))
        za = float(zs(y, 0))
        rungs.append((j, y, xa, xb, za))
    return back, front, rungs


def strand(seg, col, w, sd):
    if len(seg) < 5:
        return ""
    pts = lib.band(seg, w, w, step=4, cap=False)
    return shape(pts, col, line([(p[0] - w * .18, p[1]) for p in seg[1:-1]], w * .22, "#ffffff", seed=sd + 1, op=.35), w=4.4, seed=sd)


def icon_badge(cx, cy, kind, sc, t, sd):
    g = []
    if kind == "moon":
        g.append(shape(ellipse_pts(0, 0, 46, 46, 20), "#1f2a6a", "", w=4.4, seed=sd))
        g.append(moon(4, 0, 28, sd + 2))
    else:
        g.append(shape(ellipse_pts(0, 0, 46, 46, 20), "#fff4d0", "", w=4.4, seed=sd))
        g.append(sun(0, 0, 20, t, sd + 2))
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({sc:.4f})">{"".join(g)}</g>'


def cradle(cx, by, sc, ang, t, blink, sd=1700):
    """Люлька-качалка (вид сбоку), низ дуги (cx, by); ang — наклон качания."""
    g = []
    # дуга-полозья
    g.append(line([(-190, -20), (-100, 18), (0, 30), (100, 18), (190, -20)], 16, "#7e4e28", taper=.05, wmin=.9, seed=sd))
    for x in (-110, 110):
        g.append(line([(x, 14), (x * 0.95, -60)], 12, "#7e4e28", taper=.05, wmin=.9, seed=sd + 1 + (x > 0)))
    # корпус
    body = [(-170, -230, 1), (-140, -250), (-120, -232), (-120, -170), (120, -170), (150, -176), (170, -150, 1), (160, -60, 1),
            (-160, -60, 1)]
    inner = blob([(40, -200), (180, -200), (180, -50), (60, -50)], "#b07a44", .9)
    for k in range(5):
        inner += line([(-130 + k * 62, -160), (-128 + k * 62, -66)], 3.4, "#8a5a2e", seed=sd + 10 + k, op=.8)
    # младенец: голова в шапочке-сове, видна над бортом
    baby = []
    hx, hy = -20, -236
    baby.append(shape(ellipse_pts(hx, hy + 6, 66, 60, 20), "#f6d2b4", blob(ellipse_pts(hx + 22, hy + 14, 50, 48, 16), "#e8b898", .8) +
                      blob(ellipse_pts(hx - 30, hy + 26, 12, 8, 8), "#f09a8a", .6) + blob(ellipse_pts(hx + 26, hy + 26, 12, 8, 8), "#f09a8a", .6),
                      w=4.2, seed=sd + 20))
    # шапочка: купол с ушками-перьями и глазками совы
    cap = [(hx - 72, hy + 2), (hx - 70, hy - 40), (hx - 80, hy - 96, 1), (hx - 40, hy - 66), (hx, hy - 72), (hx + 40, hy - 66),
           (hx + 80, hy - 96, 1), (hx + 70, hy - 40), (hx + 72, hy + 2), (hx + 40, hy - 14), (hx - 40, hy - 14)]
    capin = blob([(hx + 20, hy - 72), (hx + 80, hy - 60), (hx + 72, hy + 4), (hx + 30, hy - 14)], OWL_SH, .85)
    for side in (-1, 1):
        capin += blob(ellipse_pts(hx + side * 28, hy - 42, 15, 14, 12), "#f1e1c0")
        capin += f'<circle cx="{f(hx + side * 28)}" cy="{f(hy - 42)}" r="7" fill="{INK}"/>'
    capin += blob([(hx - 6, hy - 30), (hx + 6, hy - 30), (hx, hy - 18)], "#f39a2a")
    baby.append(shape(cap, OWL_B, capin, w=4.4, seed=sd + 21))
    # лицо: спит / моргает
    for side in (-1, 1):
        ex = hx + side * 22
        if blink > 0.5:
            baby.append(line([(ex - 10, hy + 12), (ex, hy + 18), (ex + 10, hy + 12)], 3.6, seed=sd + 30 + side))
        else:
            baby.append(f'<circle cx="{f(ex)}" cy="{f(hy + 12)}" r="7" fill="{INK}"/><circle cx="{f(ex - 2)}" cy="{f(hy + 9)}" r="2.2" fill="#fff"/>')
    baby.append(line([(hx - 10, hy + 38), (hx, hy + 44), (hx + 10, hy + 38)], 3.4, seed=sd + 33))
    g.append("".join(baby))
    # одеяльце поверх
    g.append(shape([(-116, -150), (-70, -186), (40, -180), (130, -190), (130, -150), (-116, -140)], "#9fd2f2",
                   blob([(30, -186), (130, -194), (130, -150), (30, -150)], "#7fb6dc"), w=3.8, seed=sd + 40))
    g.append(shape(body, "#d39a5c", inner, w=5, seed=sd + 3))
    # звёздочка на боку люльки
    g.append(star(-20, -112, 9, "#ffd650"))
    return f'<g transform="translate({f(cx)} {f(by)}) rotate({f(ang)}) scale({sc:.4f})">{"".join(g)}</g>'


def s08_world(t):
    s = [_ST["bg8"]]
    # мягкий свет за спиралью
    back, front, rungs = helix(t)
    for k, (seg, col) in enumerate(back):
        s.append(strand(seg, col, 40, 1400 + k))
    gl = smooth(GENE_T - 0.05, GENE_T + 0.3, t)
    for j, y, xa, xb, za in rungs:
        col = RUNG_COL[j % 4]
        x0, x1 = min(xa, xb), max(xa, xb)
        if x1 - x0 > 16:
            s.append(shape(rect_pts(x0, y - 11, x1, y + 11, 9), col, blob(rect_pts(x0, y + 2, x1, y + 11), lib.mul(col, (.8, .8, .85))),
                           w=3.4, seed=1450 + j))
    for k, (seg, col) in enumerate(front):
        s.append(strand(seg, col, 40, 1480 + k))
    # значки луны и солнца — на «заложено», по очереди сверху вниз
    for j, y, xa, xb, za in rungs:
        if j % 2:
            continue
        e = t - GENE_T - 0.05 * (j // 2)
        if e <= -0.02:
            continue
        kind = "moon" if (j // 2) % 2 == 0 else "sun"
        k = back_pop(e + 0.02, 0.14, 0.3)
        if k <= 0.02:
            continue
        sx = HX + (xa + xb - 2 * HX) * 0.0
        if e < 0.3:
            r = 50 + 140 * e
            s.append(f'<circle cx="{f(sx)}" cy="{f(y)}" r="{f(r)}" fill="none" stroke="#fff4c8" stroke-width="{f(10 * (1 - e / 0.3) + 1)}"/>')
        s.append(icon_badge(sx, y, kind, 1.2 * k, t, 1500 + j * 10))
    # люлька: появляется на «рождения» и качается
    e = t - BORN_T + 0.04
    if e > 0:
        k = back_pop(e, 0.18, 0.25)
        ang = 7 * math.sin((t - BORN_T) * 3.4) * min(1, e / 0.3)
        blink = 1.0 if (int((t - BORN_T) * 10) % 9) < 6 and t > BORN_T + 0.5 else 0.0
        s.append(f'<ellipse cx="540" cy="{f(1152)}" rx="{f(230 * k)}" ry="18" fill="#3a2a5a" opacity=".25"/>')
        s.append(cradle(540, 1146 + 60 * (1 - min(1, e / 0.18)), 1.1 * k, ang, t, blink))
    return "".join(s)


def s08_cam(t):
    v = clamp((t - 12.3) / 2.62)
    sc = 1.16 - 0.18 * ease_io(v)
    cx, cy = 540, 760 + 100 * ease_out(v, 2)
    rot = 0.4 * math.sin(t * 0.8)
    for hit in (GENE_T, BORN_T):
        e = t - hit
        if e >= 0:
            k = math.exp(-e * 8)
            sc *= 1 + 0.045 * k * min(1, e / 0.04)
            cy += 7 * k * math.sin(e * 40)
    return cx, cy, sc, rot


def bg8():
    g = rad_grad([(0, "#fff7e6", 1), (.6, "#f3e2c4", 1), (1, "#e2c9a2", 1)], 540, 700, 1300, 1500)
    s = [f'<rect x="-900" y="-900" width="2900" height="3700" fill="url(#{g})"/>']
    # полутоновые точки по углам, чтобы фон не был пустым
    for k in range(60):
        x = -400 + (k * 173) % 1900
        y = -300 + (k * 311) % 2600
        if abs(x - 540) < 330 and y < 1250 or y > 1140:
            continue
        s.append(blob(ellipse_pts(x, y, 7, 7, 8), "#e6cfa6"))
    s.append(f'<rect x="-900" y="1150" width="2900" height="1600" fill="#d9bf94"/>')
    s.append(line([(-900, 1150), (2000, 1150)], 4.4, INK, taper=.02, wmin=.95, seed=1600))
    return "".join(s)


def frame(sid, t):
    if not _ST:
        _ST["bg8"] = bg8()
        lib.static_done()
    lib.dyn_begin()
    if sid == "s07":
        body = s07_world(t)
        cx, cy, sc, rot = s07_cam(t)
        bg = DAY
    else:
        body = s08_world(t)
        cx, cy, sc, rot = s08_cam(t)
        bg = "#f3e2c4"
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cam(cx, cy, sc, rot)}">{body}</g>')
