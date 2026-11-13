"""s18 (27.40–29.30, клип 27.20–29.30): петля к началу. Кот сидит на столе Димы, лапа на маленькой карточке
«1. 2. 3.»; справа по столу лежит длинный свиток Димы и свисает с края стола. Кот смотрит на свиток; на «длиннее»
(27.84) свиток ещё раз разматывается вниз (рулон падает за край кадра петлями, бумага на столе ползёт к краю), кот
поворачивается к зрителю и довольно щурится. Камера медленно отъезжает с первого кадра."""
import math

import numpy as np

import catdesk
import cat_sit
import lib
import ribbon
from lib import blob, clamp, ease_in, ease_io, smooth

T_A, T_B = 27.20, 29.30
T_DL = 27.84
X_S, W_S = 13.5, 14.0
DY = catdesk.DESK_Y
ZF = catdesk.DESK_FRONT - .4


def feed(t):
    v = max(0.0, t - T_DL + .06)
    return 6 * (t - T_A) + 70 * ease_in(clamp(v / .55), 1.6) + 40 * max(0.0, v - .55)


def roll_y(t):
    v = t - T_DL + .06
    base = DY + 20
    if v <= 0:
        return base + 1.2 * math.sin(t * 5)
    return base + 0.5 * 980 * v * v


def strip(t):
    yR = roll_y(t)
    pts = []
    for z in np.arange(112, ZF, -.8):
        pts.append(np.array([X_S + 1.2 * math.sin(z * .05), DY - .08, z]))
    for k in range(1, 6):
        a = k / 5 * math.pi / 2
        pts.append(np.array([X_S, DY - .08 + .9 * (1 - math.cos(a)) + .9 * math.sin(a) * 0, ZF - .9 * math.sin(a)]))
    top = pts[-1]
    H = yR - top[1]
    n = max(40, int(H * 2.5))
    nl = max(.8, H / 24)
    amp = min(5.5, H * .12) * (1 if t > T_DL else .35)
    ph = -feed(t) * .5
    for i in range(1, n + 1):
        u = i / n
        env = max(0.0, math.sin(math.pi * min(1.0, u * 1.08))) ** .8 if u < .9 else max(0.0, math.sin(math.pi * .9 * 1.08)) ** .8 * (1 - u) / .1
        w = 2 * math.pi * nl * u + ph
        Y = top[1] + H * u - amp * env * math.sin(w)
        Z = top[2] - amp * env * (0.45 - math.cos(w)) * 1.6 - 1.5 * u
        Z = min(Z, ZF - .2)
        pts.append(np.array([X_S, Y, Z]))
    return np.array(pts), yR


def frame(t):
    lib.DEFS.clear()
    u = clamp((t - T_A) / (T_B - T_A))
    c = catdesk.cam()
    bg = catdesk.backdrop(c, t, -2 * u)
    dk = catdesk.desk(c, t)
    mug = catdesk.mug(c, -24, 95)
    pen = catdesk.pencil(c, -30, 64, -19, 58)
    P, yR = strip(t)
    P = ribbon.resample(P, .45)
    items = ribbon.pieces(c, P, W_S, seed=7200, s_offset=-feed(t))
    rc = np.array([X_S, yR, ZF - 4])
    items.append((float(np.linalg.norm(rc)) - 3, ribbon.roll(c, rc, 3.6, W_S, feed(t) / 3.6, seed=7700, cap_side=-1)))
    items.sort(key=lambda q: -q[0])
    scroll = "".join(q[1] for q in items)
    # кот
    x, y = c.p((-4.0, DY, 58.0))
    s = c.k(58.0) * 31 / 366
    # карточка: точка (8.4, 2.1) — под левой (от зрителя) передней лапой, чуть впереди
    px, py = x + (808 - cat_sit.CX) * s, y + 6 * s
    Zt = 1100 * DY / (py - c.cy)
    Xt = (px - c.cx) * Zt / 1100
    rot = math.radians(-6)
    card = catdesk.Card(c, Xt - 8.4 * math.cos(rot) - 2.1 * math.sin(rot), Zt + (2.1 * math.cos(rot) - 8.4 * math.sin(rot)), rot=-6)
    cd = card.draw(t)
    tx, ty = card.P(8.4, 2.1)
    P_paw = (cat_sit.CX + (tx - x) / s, cat_sit.CBOT + (ty - y) / s)
    turn = smooth(T_DL + .08, T_DL + .4, t)
    sq = smooth(T_DL + .35, T_DL + .6, t)
    look = (0.8 * (1 - turn) + 0.02 * turn, 0.45 * (1 - turn) - 0.05 * turn + .25 * (1 - turn) * smooth(T_DL - .1, T_DL + .1, t))
    tilt = 6 * (1 - turn) - 5 * turn + 1.2 * math.sin(t * 1.4)
    blink = .58 * sq
    for tb in (27.5,):
        if abs(t - tb) < .09:
            blink = max(blink, min(1, 1.7 * (1 - abs(t - tb) / .09)))
    tail = 6 * math.sin(t * 2.2 + .5) - 2
    flick = -9 * math.exp(-9 * max(0, t - T_DL - .1)) * math.sin(max(0, t - T_DL - .1) * 30) * (t > T_DL + .1)
    shadow = blob(lib.ellipse_pts(x + 30 * s, y - 2, 175 * s, 20 * s, 16), "#2a160a", .32, lib.blur(6))
    cat = cat_sit.draw(x, y, s, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw=P_paw, press=0.0, shadow=False,
                       smile=sq)
    world = bg + dk + mug + pen + scroll + cd + shadow + cat
    z = 1.14 - 0.16 * (0.45 * u + 0.55 * ease_io(u))
    return lib.svg(f'<g transform="translate(540 430) scale({z:.4f}) translate(-560 -730)">{world}</g>')
