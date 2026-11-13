"""s04 (4.62–6.44, клип 4.42–6.64): низкий план у пола комнаты Димы, утро. Рулон списка катится с края стола вниз,
бумага разматывается петлями; на «пола» (5.96) рулон шлёпается об пол (пыль, тряска) и катится к зрителю, раскатывая
ленту по полу; кот, сидевший на полу слева, подпрыгивает от испуга (шерсть дыбом, глаза круглые, рот открыт).
Камера опускается за свитком с первого кадра."""
import math

import numpy as np

import cat_sit
import lib
import ribbon
from floorbg import Room
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, line, shape

T_A, T_B = 4.42, 6.64
T_SVIS, T_STOLA, T_POL = 4.76, 5.36, 5.96
X_P, W_P = 12.0, 30.0            # центр ленты по X и ширина бумаги, см
FY, DT, DZ = 45.0, -30.0, 150.0  # пол, верх столешницы, передняя кромка стола
CAT_X, CAT_Z = -21.0, 115.0


def pan(t):
    u = clamp((t - T_A) / (T_B - T_A))
    return 840 - 360 * (0.5 * u + 0.5 * ease_io(u))


def shake(t):
    if t < T_POL:
        return 0.0, 0.0
    a = 16 * math.exp(-9 * (t - T_POL))
    return a * math.sin((t - T_POL) * 62), a * .7 * math.cos((t - T_POL) * 51)


def roll_state(t):
    """(Y центра, Z центра, радиус, угол)."""
    if t < T_POL:
        u = clamp((t - T_A) / (T_POL - T_A))
        e = ease_in(u, 1.7)
        r = 6.6 - 1.4 * u
        y = (DT + 9) + (FY - r - DT - 9) * e
        z = 147 - 8 * ease_out(u, 2)
        ang = 9 * u + 4 * e
        return y, z, r, ang
    v = t - T_POL
    r = 5.2 - 0.9 * clamp(v / .7)
    z = 139 - 40 * ease_out(clamp(v / .62), 2.2)
    hop = 3.2 * abs(math.sin(clamp(v / .26) * math.pi)) * (v < .26)
    ang = 13 + (139 - z) / r
    return FY - r - hop, z, r, ang


def feed(t):
    return 22 * (t - T_A) + (10 * ease_in(clamp((t - T_STOLA) / (T_POL - T_STOLA)), 2) if t > T_STOLA else 0)


def strip(t, yR, zR, r):
    """Средняя линия: от кромки стола вниз петлями к рулону; после удара — вниз до пола и по полу к рулону."""
    top = np.array([X_P, DT - .2, DZ - .3])
    pts = [np.array([X_P, DT - 0.6, DZ - 3.0]), np.array([X_P, DT - .45, DZ - 1.0]), top]
    landed = t >= T_POL
    if not landed:
        end = np.array([X_P, yR - r * .2, zR + r * .95])
        H = end[1] - top[1]
        nl = max(1.0, H / 27.0)
        amp = 8.0 * clamp(H / 30)
        ph = -feed(t) * 0.42
        n = 260
        for i in range(1, n + 1):
            u = i / n
            env = max(0.0, math.sin(math.pi * min(1.0, u * 1.08))) ** .8 if u < .9 else max(0.0, math.sin(math.pi * .9 * 1.08)) ** .8 * (1 - u) / .1
            w = 2 * math.pi * nl * u + ph
            Y = top[1] + H * u - amp * env * math.sin(w)
            Z = top[2] + (end[2] - top[2]) * u - amp * env * (0.45 - math.cos(w)) * 1.9
            X = X_P + 1.6 * env * math.sin(w * .5 + 1)
            pts.append(np.array([X, Y, Z]))
        return np.array(pts)
    v = t - T_POL
    zF = 141.0
    H = FY - top[1]
    amp = 6.2 * math.exp(-7 * v) * math.cos(v * 16) + 1.3 * (1 - math.exp(-7 * v))
    ph = -feed(t) * 0.42
    n = 220
    for i in range(1, n + 1):
        u = i / n
        env = math.sin(math.pi * u) ** .8
        w = 2 * math.pi * 2.6 * u + ph
        Y = top[1] + H * u - amp * env * math.sin(w) - (0.4 if u > .995 else 0)
        Z = top[2] + (zF - top[2]) * u - amp * env * (0.55 - math.cos(w)) * 1.15
        Y = min(Y, FY - .15)
        pts.append(np.array([X_P, Y, Z]))
    # изгиб на пол и лента по полу к рулону
    for k in range(1, 7):
        a = k / 6 * math.pi / 2
        pts.append(np.array([X_P, FY - .15 - 2.4 * (1 - math.sin(a)) * 0, zF - 2.4 * math.sin(a) * 0 - 2.4 * (1 - math.cos(a)) * 0 - k * .35]))
    zz = zF - 2.2
    while zz > zR + .2:
        zz = max(zR, zz - 1.0)
        bump = 0.25 * math.sin(zz * .4)
        pts.append(np.array([X_P + .3 * math.sin(zz * .15), FY - .15 - abs(bump) * .2, zz]))
    return np.array(pts)


def dust(cam, t, x, z):
    """Клубы пыли при ударе: плотные, растут и сжимаются до нуля (без полупрозрачности)."""
    v = t - T_POL
    if v < 0 or v > .55:
        return ""
    o = []
    k = cam.k(z)
    for j, (dx, sz, dl) in enumerate([(-1, 1.0, 0), (1, .9, .03), (-1, .7, .07), (1, .65, .05), (-1, .5, .1)]):
        w = clamp((v - dl) / .45)
        if w <= 0 or w >= 1:
            continue
        R = sz * 5.2 * math.sin(math.pi * w) ** .7 * k
        cx = x + dx * (W_P / 2 + 2 + 9 * ease_out(w, 2) * (1 + j * .25)) * k
        cy = cam.p((0, FY - 1.5 - 4 * ease_out(w, 2) * (j % 3) * .5, z))[1]
        pts = []
        for q in range(30):
            a = q / 30 * 2 * math.pi
            rr = R * (0.8 + 0.2 * abs(math.sin(2.5 * a + j)))
            pts.append((cx + rr * math.cos(a), cy - R * .25 + rr * .75 * math.sin(a)))
        o.append(shape(pts, "#efe6d4", blob(lib.ellipse_pts(cx + R * .2, cy + R * .25, R * .7, R * .45, 8), "#d6c9b0"), w=.3 * k, seed=910 + j))
    return "".join(o)


def impact_lines(cam, t, x, y, k):
    v = t - T_POL
    if v < 0 or v > .28:
        return ""
    u = v / .28
    o = []
    for j, a in enumerate((-160, -135, -110, -70, -45, -20)):
        ar = math.radians(a)
        r0, r1 = (W_P / 2 + 3 + 6 * u) * k, (W_P / 2 + 8 + 9 * u) * k
        o.append(line([(x + r0 * math.cos(ar), y + r0 * math.sin(ar) * .7), (x + r1 * math.cos(ar), y + r1 * math.sin(ar) * .7)],
                      .9 * k * (1 - u * .6), INK, seed=930 + j, taper=.4, wmin=.3))
    return "".join(o)


def cat(cam, t):
    k = cam.k(CAT_Z)
    s = k * 30 / 366
    x, y = cam.p((CAT_X, FY, CAT_Z))
    tj = T_POL + .03
    scare = smooth_step(tj - .02, tj + .05, t)
    puff = scare
    # прыжок
    v = t - tj
    hop, sy = 0.0, 1.0
    if 0 < v < .5:
        u = v / .5
        hop = 24 * k * 4 * u * (1 - u)
        sy = 1 + .08 * math.sin(math.pi * u)
    elif .5 <= v < .7:
        sy = 1 - .1 * math.sin(math.pi * (v - .5) / .2)
    yR = roll_state(t)[0]
    ry = clamp((yR - DT) / (FY - DT))
    look = (0.55, -0.85 + 0.9 * ry) if t < tj else (0.25, -0.15)
    blink = 0.0
    if abs(t - 4.95) < .09:
        blink = min(1, 1.7 * (1 - abs(t - 4.95) / .09))
    tilt = (6 * math.sin(t * 1.7) - 4) * (1 - scare) + 4 * scare * math.sin(t * 40) * math.exp(-4 * max(0, v))
    tail = (6 * math.sin(t * 2.3) - 2) * (1 - scare) + (-14) * scare
    flick = -9 * math.exp(-9 * max(0, t - 4.5)) * math.sin(max(0, t - 4.5) * 30) * (t > 4.5)
    sh_k = 1 - .45 * clamp(hop / (24 * k))
    shadow = blob(lib.ellipse_pts(x + 14 * s, y + 2, 170 * s * sh_k, 20 * s * sh_k, 16), "#1a0e05", .35, lib.blur(5))
    c = cat_sit.draw(x, y - hop, s, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, scare=scare, puff=puff, mouth=scare,
                     shadow=False, flame_k=1.3 + .3 * scare)
    c = f'<g transform="translate({x:.1f} {y - hop:.1f}) scale(1 {sy:.4f}) translate({-x:.1f} {-(y - hop):.1f})">{c}</g>'
    marks = ""
    if 0 < v < .55:
        u = v / .55
        hx, hy = x, y - hop - 400 * s
        for j, a in enumerate((-125, -90, -55)):
            ar = math.radians(a)
            r0, r1 = (40 + 30 * u) * s, (90 + 50 * u) * s
            marks += line([(hx + r0 * math.cos(ar), hy + r0 * math.sin(ar)), (hx + r1 * math.cos(ar), hy + r1 * math.sin(ar))], 7 * s * (1 - .5 * u), INK,
                          seed=950 + j, taper=.4, wmin=.3)
    return shadow + c + marks


def smooth_step(a, b, x):
    return lib.smooth(a, b, x)


def frame(t):
    lib.DEFS.clear()
    sx, sy = shake(t)
    cam = ribbon.Cam(f=1700, cx=540 + sx, cy=pan(t) + sy)
    room = Room(cam, floor_y=FY, desk_top=DT, desk_z=DZ, desk_x=(-17.0, 140.0), ped_x=62.0, mode="morning")
    bg = [room.wall(t), room.window(t), room.clock(42, -128, 8 * 30 + 15 * (t - T_A), 30 * 6 + 360 * (t - T_A) / 2.2), room.floor(), room.desk(t)]
    yR, zR, r, ang = roll_state(t)
    P = strip(t, yR, zR, r)
    P = ribbon.resample(P, .5)
    items = ribbon.pieces(cam, P, W_P, seed=7000, s_offset=-feed(t) + 40)
    sq = 1.0
    if t >= T_POL:
        sq = 1 - .28 * math.exp(-14 * (t - T_POL)) * math.cos((t - T_POL) * 30)
    C = np.array([X_P, yR + (1 - sq) * r, zR])
    rsv = ribbon.roll(cam, C, r, W_P, ang, squash=sq, cap_side=-1)
    rshadow = ""
    if True:
        gap = clamp((FY - (yR + r)) / 40)
        cx, cy = cam.p((X_P, FY, zR))
        kk = cam.k(zR)
        rshadow = blob(lib.ellipse_pts(cx, cy, (W_P * .55) * kk * (1 - .4 * gap), 2.4 * kk * (1 - .5 * gap), 16), "#1a0e05", .3 * (1 - .6 * gap), lib.blur(4))
    items.append((float(np.linalg.norm(C - cam.eye)) - r - .5, rshadow + rsv))
    items.sort(key=lambda q: -q[0])
    rx, ry_ = cam.p((X_P, FY - .5, zR))
    fx = dust(cam, t, rx, zR) + impact_lines(cam, t, rx, ry_, cam.k(zR))
    body = "".join(bg) + "".join(q[1] for q in items) + fx + cat(cam, t) + room.light(t)
    return lib.svg(body)


_ = (ease_io, INK)
