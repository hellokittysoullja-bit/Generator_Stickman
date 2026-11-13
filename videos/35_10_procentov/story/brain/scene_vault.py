"""Сцена «сейф» рилса 35 (s11, s12): внутри мозга (розовая стена с извилинами) — тайная дверь-сейф с табличкой «90 %»
и огромным замком; мозг-персонаж (обычный, розовый) подкрадывается на цыпочках.
s11 «Никаких спрятанных девяноста» (18.7–20.7): крадётся к двери, на «спрятанных» замок дрожит, на «девяноста»
    мозг хватается за рычаг двери.
s12 «…процентов нет, и раскрывать там нечего» (20.7–22.85): на «нет» дверь распахивается (замок слетает) — за ней пусто:
    паутина и лампочка без света; на «нечего» вылетает моль, мозг разводит ручками."""
import math

import numpy as np

import body as B
import brain_art as BA
import lib
from body import FLOOR, SH_L, SH_R, Pose, face, rays, shadow, text
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape, smooth,
                 svg)
from scene_brain35 import char, hang, legs_for, lerp, word_t, y_for

_ST = {}
DX0, DX1, DY0, DY1 = 520, 900, 600, 1150      # проём двери
HINGE = DX1
LEVER = (566, 900)
LOCK_HUB = (710, 900)


# ───────────────────────── стена внутри мозга
def interior():
    s = []
    g = lib.lin_grad([(0, "#5a2446", 1), (.6, "#7a3658", 1), (1, "#8a4062", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#{g})"/>')
    g2 = lib.lin_grad([(0, "#4a1d3a", 1), (1, "#2e1026", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="{FLOOR}" width="{W + 1800}" height="{H + 600}" fill="url(#{g2})"/>')
    rs = np.random.RandomState(5)
    # извилины на стене: мягкие петли (тень + свет)
    for k in range(34):
        x0, y0 = rs.uniform(-400, W + 400), rs.uniform(-300, FLOOR - 60)
        a = rs.uniform(0, 6.28)
        pts = []
        for i in range(9):
            u = i / 8
            r = 60 + 60 * u
            pts.append((x0 + math.cos(a + u * 3.2) * r + 50 * u, y0 + math.sin(a + u * 3.2) * r * .7))
        s.append(line([(x + 3, y + 6) for x, y in pts], 12, "#9a4a70", taper=.6, seed=20 + k, op=.55))
        s.append(line(pts, 11, "#4a1a38", taper=.6, seed=60 + k, op=.7))
    rr = rad_grad([(0, "#c06a8e", .5), (1, "#c06a8e", 0)], 700, 760, 700, 600)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#{rr})"/>')
    s.append(line([(-800, FLOOR), (W + 800, FLOOR)], 4.5, INK, taper=.1, wmin=.8, seed=5))
    for k, y in enumerate([1240, 1360, 1520]):
        s.append(line([(-800, y), (W + 800, y + 6)], 2.4, "#24091c", taper=.2, wmin=.6, seed=10 + k, op=.8))
    # рама проёма (стальная)
    s.append(shape(rect_pts(DX0 - 40, DY0 - 40, DX1 + 40, DY1 + 8, 18), "#8d97ad",
                   blob(rect_pts(DX1 - 10, DY0 - 40, DX1 + 40, DY1 + 8), "#68718a", .8) + blob(rect_pts(DX0 - 40, DY0 - 40, DX1 + 40, DY0 - 20), "#c3cad8", .8),
                   w=6, seed=30))
    for k in range(6):
        y = DY0 - 20 + k * (DY1 - DY0 + 20) / 5
        for x in (DX0 - 22, DX1 + 22):
            s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="6" fill="#5a6278" stroke="{INK}" stroke-width="2.4"/>')
    return "".join(s)


def closet(t, sway):
    """Пустота за дверью: тёмная ниша, задняя стенка, паутина, лампочка без света на проводе."""
    s = []
    s.append(f'<rect x="{DX0}" y="{DY0}" width="{DX1 - DX0}" height="{DY1 - DY0}" fill="#1c0c1a"/>')
    ix0, iy0, ix1, iy1 = DX0 + 60, DY0 + 60, DX1 - 60, DY1 - 70
    s.append(f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}" fill="#2c1428"/>')
    for (a, b) in (((DX0, DY0), (ix0, iy0)), ((DX1, DY0), (ix1, iy0)), ((DX0, DY1), (ix0, iy1)), ((DX1, DY1), (ix1, iy1))):
        s.append(line([a, b], 3, "#0e0510", taper=.1, wmin=.8, seed=int(a[0] + a[1])))
    s.append(blob([(DX0, DY1), (DX1, DY1), (ix1, iy1), (ix0, iy1)], "#3a1a34"))
    # пыль на полу ниши
    for k in range(5):
        s.append(blob(ellipse_pts(ix0 + 40 + k * 55, iy1 + 30, 18, 4, 8), "#5a3a52", .9))
    # паутина в двух углах
    for cx, cy, sx in ((DX0, DY0, 1), (DX1, DY0, -1)):
        R = 120
        for k in range(5):
            a = math.radians(4 + k * 20)
            s.append(line([(cx, cy), (cx + sx * math.cos(a) * R, cy + math.sin(a) * R)], 2.6, "#d8d2e0", taper=.1, wmin=.7, seed=700 + k + (sx > 0) * 9,
                          op=.9))
        for r in (40, 72, 104):
            pts = [(cx + sx * math.cos(math.radians(4 + k * 20)) * r * (1 - .08 * (k % 2)), cy + math.sin(math.radians(4 + k * 20)) * r * (1 - .08 * (k % 2)))
                   for k in range(5)]
            s.append(line(pts, 2.2, "#d8d2e0", taper=.1, wmin=.7, seed=720 + r + (sx > 0), op=.9))
    # лампочка на проводе, без света
    tx, ty = (DX0 + DX1) / 2, DY0
    a = math.radians(sway)
    bx, by = tx + math.sin(a) * 190, ty + math.cos(a) * 190
    s.append(line([(tx, ty), (bx, by)], 3.4, "#0b0408", taper=.05, wmin=.95, seed=740))
    s.append(f'<g transform="translate({f(bx)} {f(by)}) rotate({f(-sway)})">'
             + shape(rect_pts(-14, 0, 14, 26, 4), "#6b7389", "", w=3, seed=741)
             + shape(ellipse_pts(0, 58, 34, 36, 18), "#6d6878", blob(ellipse_pts(-10, 48, 9, 14, 8, rot=20), "#9a96a6", .9)
                     + line([(-10, 30), (-6, 54), (0, 46), (6, 54), (10, 30)], 2.6, "#3a3644", seed=742), w=3.6, seed=743) + "</g>")
    return "".join(s)


def door_face(sd=0):
    """Дверь-сейф в закрытом положении (мировые координаты проёма)."""
    s = []
    inner = blob(rect_pts(DX1 - 70, DY0, DX1, DY1), "#6b748c", .85)
    inner += blob(rect_pts(DX0, DY0, DX0 + 30, DY1), "#c9d0de", .8)
    inner += shape(rect_pts(DX0 + 34, DY0 + 34, DX1 - 34, DY1 - 34, 14), "#959fb5", blob(rect_pts(DX1 - 90, DY0 + 34, DX1 - 34, DY1 - 34), "#7a849c", .8),
                   w=4, seed=sd + 2)
    for x in (DX0 + 18, DX1 - 18):
        for k in range(7):
            y = DY0 + 22 + k * (DY1 - DY0 - 44) / 6
            inner += f'<circle cx="{f(x)}" cy="{f(y)}" r="5.5" fill="#5f6880" stroke="{INK}" stroke-width="2.2"/>'
    s.append(shape(rect_pts(DX0, DY0, DX1, DY1, 10), "#a9b2c6", inner, w=6, seed=sd))
    # табличка «90 %»
    px, py = (DX0 + DX1) / 2, DY0 + 120
    s.append(shape(rect_pts(px - 130, py - 62, px + 130, py + 62, 16), "#fbf3df", blob(rect_pts(px - 130, py + 34, px + 130, py + 62), "#e6d9bb", .9),
                   w=5, seed=sd + 5))
    s.append(text(px, py + 38, "90 %", 104, "#e2543f", sw=8, shadow=False))
    for x in (px - 112, px + 112):
        s.append(f'<circle cx="{f(x)}" cy="{f(py)}" r="5" fill="#8a8a8a" stroke="{INK}" stroke-width="2"/>')
    # штурвал
    hx, hy = LOCK_HUB
    for k in range(4):
        a = math.radians(45 * k + 22)
        s.append(line([(hx - math.cos(a) * 92, hy - math.sin(a) * 92), (hx + math.cos(a) * 92, hy + math.sin(a) * 92)], 14, "#4a5168", taper=.05,
                      wmin=.95, seed=sd + 10 + k))
    ring = ellipse_pts(hx, hy, 92, 92, 30)
    s.append(f'<path d="{lib.fill_d(ring)}" fill="none" stroke="{INK}" stroke-width="20"/>'
             f'<path d="{lib.fill_d(ring)}" fill="none" stroke="#7d869e" stroke-width="12"/>')
    s.append(shape(ellipse_pts(hx, hy, 30, 30, 16), "#c3cad8", "", w=4, seed=sd + 20))
    # рычаг
    lx, ly = LEVER
    s.append(shape(rect_pts(lx - 22, ly - 96, lx + 22, ly - 70, 6), "#5f6880", "", w=3.4, seed=sd + 30))
    s.append(shape(rect_pts(lx - 22, ly + 70, lx + 22, ly + 96, 6), "#5f6880", "", w=3.4, seed=sd + 31))
    s.append(shape(rect_pts(lx - 13, ly - 84, lx + 13, ly + 84, 12), "#d6a63c", blob(rect_pts(lx + 2, ly - 84, lx + 13, ly + 84), "#a87c22", .8), w=4,
                   seed=sd + 32))
    return "".join(s)


def door_back(sd=0):
    inner = blob(rect_pts(DX0, DY0, DX0 + 60, DY1), "#5e667c", .8)
    for k in range(4):
        y = DY0 + 80 + k * 130
        inner += line([(DX0 + 30, y), (DX1 - 30, y + 4)], 4, "#5e667c", seed=sd + 50 + k, op=.8)
    return shape(rect_pts(DX0, DY0, DX1, DY1, 10), "#8790a6", inner, w=6, seed=sd + 40)


def door(theta):
    """Дверь, открытая на theta градусов (петли справа): сжатие по X к петле + перспективный сдвиг."""
    c = math.cos(math.radians(theta))
    k = 0.10 * math.sin(math.radians(theta))
    # x' = H + (x - H)·c ;  y' = y + (x - H)·(−k) ... дальний край выше/ниже — лёгкая перспектива
    m = f"matrix({f(c)} {f(-k * (1 if c >= 0 else -1))} 0 1 {f(HINGE - HINGE * c)} {f(HINGE * k * (1 if c >= 0 else -1))})"
    body = door_face() if c >= 0 else door_back()
    s = f'<g transform="{m}">{body}</g>'
    # торец двери (толщина)
    th = 46 * abs(math.sin(math.radians(theta)))
    if th > 2:
        ex = HINGE + (DX0 - HINGE) * c
        sgn = 1 if c >= 0 else -1
        ey0 = DY0 - (DX0 - HINGE) * k * sgn
        ey1 = DY1 - (DX0 - HINGE) * k * sgn
        x2 = ex - th if c >= 0 else ex + th
        s = shape([(ex, ey0, 1), (x2, ey0 + 8, 1), (x2, ey1 - 8, 1), (ex, ey1, 1)], "#5f6880", "", w=4.4, seed=900) + s
    return s


def padlock(x, y, rot, open_=0.0, sd=0):
    """Огромный навесной замок: (x, y) — точка подвеса (верх дужки)."""
    s = []
    bw, bh = 210, 170
    sh = 110
    # дужка
    lift = 40 * open_
    pts = [(-62, sh - lift), (-62, 40 - lift), (-40, 4 - lift), (0, -6 - lift), (40, 4 - lift), (62, 40 - lift), (62, sh - lift)]
    s.append(line(pts, 36, INK, taper=.02, wmin=.98, seed=sd))
    s.append(line(pts, 24, "#b8c0d0", taper=.02, wmin=.98, seed=sd + 1))
    s.append(line([(p[0] - 6, p[1]) for p in pts[1:-1]], 6, "#e6eaf2", taper=.4, seed=sd + 2, op=.8))
    inner = blob(rect_pts(bw / 2 - 50, sh, bw / 2, sh + bh), "#b47a10", .8)
    inner += blob(rect_pts(-bw / 2, sh, -bw / 2 + 30, sh + bh), "#ffe08a", .8)
    inner += shape([(0, sh + 56), (16, sh + 70), (8, sh + 82, 1), (14, sh + 128, 1), (-14, sh + 128, 1), (-8, sh + 82, 1), (-16, sh + 70)], "#3a2a10", "",
                   w=2, seed=sd + 5)
    s.append(shape(rect_pts(-bw / 2, sh, bw / 2, sh + bh, 30), "#e8b02a", inner, w=6, seed=sd + 3))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)})">{"".join(s)}</g>'


def moth(x, y, sc, t, sd=0):
    flap = math.sin(t * 38)
    s = []
    for side in (-1, 1):
        wing = [(0, 0), (side * 50, -40), (side * 70, -10), (side * 58, 18), (side * 20, 14)]
        wing = [(p[0], p[1] * (0.35 + 0.65 * abs(flap))) for p in wing]
        s.append(shape(wing, "#c9b89a", blob([(side * 30, -14), (side * 52, -18), (side * 46, 4)], "#9f8d70", .8), w=3, seed=sd + (side > 0)))
    s.append(shape(ellipse_pts(0, 6, 9, 22, 12), "#7d6c52", "", w=2.6, seed=sd + 3))
    s.append(line([(-3, -14), (-14, -34)], 2.2, INK, seed=sd + 4))
    s.append(line([(3, -14), (14, -34)], 2.2, INK, seed=sd + 5))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)}) rotate({f(10 * math.sin(t * 7))})">{"".join(s)}</g>'


# ───────────────────────── s11
def sneak_pose(t, x, sc, stepph, freeze=0.0):
    bob = -16 * abs(math.sin(stepph)) * (1 - freeze)
    return Pose(x, y_for(sc) - 22 + bob, sc, -5 + 3 * math.sin(stepph) * (1 - freeze), 1 + 0.02 * math.cos(2 * stepph))


def s11(t):
    hid = word_t("спрятанных")       # 19.20
    ninety = word_t("девяноста")     # 19.72
    sc = 0.9
    # крадётся: шаги на цыпочках, на «спрятанных» замирает, потом последний шаг и хватает рычаг
    freeze = smooth(hid - 0.02, hid + 0.06, t) * (1 - smooth(hid + 0.3, hid + 0.42, t))
    prog = smooth(18.5, hid, t) * 0.7 + smooth(hid + 0.35, ninety - 0.05, t) * 0.3
    x = 230 + (340 - 230) * prog
    stepph = (t - 18.5) * 2 * math.pi / 0.6
    walk = 1 - freeze
    if t > ninety - 0.05:
        walk = 0.0
    pose = sneak_pose(t, x, sc, stepph * (walk > 0) + 0.0, 1 - walk)
    lift_l = 46 * max(0.0, math.sin(stepph)) * walk
    lift_r = 46 * max(0.0, -math.sin(stepph)) * walk
    legs = legs_for(pose, lift_l=lift_l + 10, lift_r=lift_r + 10, live=1.0)
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    # ручки «крадущегося»: подняты перед грудью, кисти свисают
    wl = (SL[0] - 30 * sc, SL[1] - 70 * sc + 6 * math.sin(stepph))
    wr = (SR[0] + 60 * sc, SR[1] - 80 * sc - 6 * math.sin(stepph))
    al, ar, cl, cr = 70, 60, 0.35, 0.35
    grab = smooth(ninety - 0.12, ninety + 0.04, t)
    wr = lerp(wr, (LEVER[0] - 50, LEVER[1] + 10), grab)
    ar = ar + (0 - ar) * grab
    cr = 0.35 + 0.5 * grab
    look = (0.9, -0.1) if freeze < 0.5 else (1.0, 0.3)
    fc = face(1.0 if freeze < 0.5 else 1.0, look, "flat" if freeze < 0.5 else "o", t, brow=0.5 + 0.6 * freeze, brow_tilt=0.4 * freeze, blush=0.4)
    # замок дрожит на «спрятанных» и ещё на «девяноста»
    e1, e2 = t - hid, t - ninety
    rot = 0.0
    if e1 > 0:
        rot += 9 * math.exp(-e1 * 4) * math.sin(e1 * 48)
    if e2 > 0:
        rot += 6 * math.exp(-e2 * 5) * math.sin(e2 * 52)
    rot += 1.2 * math.sin(t * 2.2)
    art = [_ST["int"], door(0), padlock(LOCK_HUB[0], LOCK_HUB[1] - 40, rot, sd=600)]
    art.append(rays(LOCK_HUB[0], LOCK_HUB[1] + 150, e1, 640, r=150, n=10, col="#ffe27a", dur=0.4, L0=40))
    art.append(shadow(pose.x, FLOOR + 6, 140))
    B.set_skin(1.0)
    art.append(char(pose, {}, fc, wl, wr, al, ar, cl, cr, 40, -40, legs, 1.0, pink=True))
    if freeze > 0.3:
        px, py = pose.pt(BCX + 60, BCY - 200)
        art.append(text(px, py, "!", 110, "#ffe27a", sw=8))
    u = clamp((t - 18.5) / 2.4)
    s = 1.06 + 0.16 * ease_io(u) + B.ease_kick(e1, 0.03)
    return "".join(art), cam(500 + 110 * ease_io(u), 820 + 10 * u, s, 0.8 - 1.2 * u)


# ───────────────────────── s12
def s12(t):
    no = word_t("нет")               # 20.88
    nothing = word_t("нечего")       # 22.20
    sc = 0.9
    e, em = t - no, t - nothing
    # дверь: перед «нет» тянет, на «нет» распахивается с отскоком
    if e < 0:
        theta = 4 * smooth(no - 0.25, no, t) + 1.5 * math.sin(t * 30) * smooth(no - 0.2, no, t)
    else:
        theta = 112 - 112 * math.exp(-e * 7) * math.cos(e * 11)
        theta = min(theta, 128)
    jump = B.ease_kick(e, 1.0, 10, 5)
    x = 340 - 30 * smooth(no, no + 0.25, t)
    br = math.sin(t * 2.4)
    pose = Pose(x, y_for(sc) - 22 - 30 * jump + 4 * br, sc, -5 + 4 * jump, 1 - 0.05 * jump)
    legs = legs_for(pose, lift_l=10, lift_r=10, live=1.0)
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    wl0, wr0, al0, ar0 = hang(pose, t)
    # до «нет» держится за рычаг (рычаг едет с дверью), после — ручки вскинуты от неожиданности, потом разводит
    ex = HINGE + (LEVER[0] - HINGE) * math.cos(math.radians(theta))
    if e < 0:
        wr = (ex - 50, LEVER[1] + 10)
        ar, cr = 0, 0.85
    else:
        startle = smooth(0, 0.12, e) * (1 - smooth(0.6, 0.9, e))
        wr = lerp((ex - 50, LEVER[1] + 10), (SR[0] + 90 * sc, SR[1] - 120 * sc), smooth(0, 0.15, e))
        wr = lerp(wr, wr0, smooth(0.6, 0.9, e) * (1 - smooth(nothing - 0.15, nothing + 0.05, t)))
        ar, cr = -40 * startle + ar0 * (1 - startle), 0.1
    wl = lerp(wl0, (SL[0] - 90 * sc, SL[1] - 120 * sc), smooth(0, 0.15, e) * (1 - smooth(0.6, 0.9, e))) if e > 0 else wl0
    al, cl = 230 if 0 < e < 0.8 else al0, 0.1
    shr = smooth(nothing - 0.12, nothing + 0.12, t)
    if shr > 0:
        upl = (SL[0] - 110 * sc, SL[1] - 90 * sc)
        upr = (SR[0] + 90 * sc, SR[1] - 100 * sc)
        wl, wr = lerp(wl, upl, shr), lerp(wr, upr, shr)
        al, ar = al + (205 - al) * shr, ar + (-25 - ar) * shr
    look = (1.0, -0.1) if e < 0.3 else ((0.9, -0.5) if em < 0 else (-0.6 + 0.3 * smooth(0, .4, em), -0.6))
    mouth = "flat" if e < 0 else ("o" if em < 0 else "wobbly")
    fc = face(1.0, look, mouth, t, brow=0.5 + 0.5 * smooth(0, .1, e), brow_tilt=0.7 * shr, blush=0.4)
    # замок: на «нет» дужка отщёлкивается, замок падает и подскакивает на полу
    if e < 0:
        lock = padlock(LOCK_HUB[0], LOCK_HUB[1] - 40, 3 * math.sin(t * 30) * smooth(no - 0.2, no, t), sd=600)
    else:
        floor_y = FLOOR - 282
        y0 = LOCK_HUB[1] - 40
        tl = (-(-260) + math.sqrt(260 ** 2 + 4 * 2600 * (floor_y - y0))) / (2 * 2600)
        if e < tl:
            fx = LOCK_HUB[0] - 120 * e / tl
            fy = y0 - 260 * e + 2600 * e * e
            rot = -14 * e / tl
        else:
            el = e - tl
            fx = LOCK_HUB[0] - 120 - 20 * clamp(el / 0.3)
            fy = floor_y - 40 * abs(math.sin(el * 10)) * math.exp(-el * 7)
            rot = -14 + 8 * math.exp(-el * 6) * math.sin(el * 22)
        lock = padlock(fx, fy, rot, open_=1.0, sd=600)
    sway = 14 * math.exp(-max(e, 0) * 1.5) * math.sin(max(e, 0) * 5) + 3 * math.sin(t * 2)
    art = [_ST["int"], closet(t, sway)]
    if theta < 90:
        art.append(door(theta))
    # моль на «нечего»: вылетает из ниши к зрителю, зигзагом
    if em > -0.1:
        u = clamp((em + 0.1) / 0.75)
        mx = 720 - 420 * ease_in(u, 1.3) + 40 * math.sin(em * 14)
        my = 900 - 480 * u + 50 * math.sin(em * 9)
        art.append(moth(mx, my, 0.9 + 1.4 * u, t, 980))
        if u < 1:
            for k in range(3):
                art.append(blob(ellipse_pts(mx + 30 + k * 26 * (1 - u), my + 30 + k * 18, 5 - k, 5 - k, 8), "#d8cbb4", .8 - .2 * k))
    art.append(shadow(pose.x, FLOOR + 6, 140))
    B.set_skin(1.0)
    art.append(char(pose, {}, fc, wl, wr, al, ar, cl, cr, 40, -40, legs, 1.0, pink=True))
    if theta >= 90:
        art.append(door(theta))
    art.append(lock)
    art.append(rays(720, 860, e, 990, r=260, n=12, col="#ffe9b0", dur=0.4, L0=60, w=9))
    u = clamp((t - 20.5) / 2.35)
    s = 1.04 + 0.03 * u + B.ease_kick(e, 0.06, 16, 7)
    cy = 820 + B.ease_kick(e, 14, 40, 8)
    return "".join(art), cam(525 + 20 * u, cy, s, -0.4 + 0.8 * u)


def build_static():
    if _ST.get("ok"):
        return
    BA.init()
    _ST["int"] = interior()
    lib.static_done()
    _ST["ok"] = 1


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s11": s11, "s12": s12}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#3a1630"/><g transform="{cm}">{art}</g>')
