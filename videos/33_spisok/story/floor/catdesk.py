"""Сцена cat рилса 33 (s17, s18): кот крупно на столе Димы вечером. Глаз камеры чуть выше столешницы (22 см),
стена за столом (WALL_Z 120) — размыта, столешница резкая; на столе — маленькая карточка «1. 2. 3.» с двумя зелёными
галочками и отпечатком лапы в третьем квадратике, кружка, карандаш. Всё в см и проекции ribbon.Cam."""
import math

import numpy as np

import kitchen
import lib
import ribbon
from floorbg import Room
from lib import INK, blob, line, mix, rect_pts, shape

DESK_Y = 30.0
DESK_FRONT = 38.0
WALL = 120.0
WOOD, WOOD_SH, WOOD_HI, WOOD_DK = "#9a6238", "#74462a", "#b97c4d", "#56331d"


def cam():
    return ribbon.Cam(f=1100, cx=540, cy=620)


def backdrop(c, t, drift=0.0):
    room = Room(c, floor_y=DESK_Y, mode="evening", wall_z=WALL)
    o = [room.wall(t), room.window(t, X0=-95 + drift, X1=-45 + drift, Y0=-95, Y1=-18), room.clock(38 + drift, -70, 19 * 30 + 10, 12 * 6, R=11)]
    # полка с книгами справа на стене
    k = c.k(WALL)
    y = c.p((0, -45, WALL))[1]
    x0, x1 = c.p((55 + drift, 0, WALL))[0], c.p((120 + drift, 0, WALL))[0]
    o.append(shape(rect_pts(x0, y, x1, y + 2 * k), WOOD_HI, blob(rect_pts(x0, y + 1.1 * k, x1, y + 2 * k), WOOD_SH, .9), w=.3 * k, seed=3500))
    xx = x0 + 3 * k
    rs = np.random.RandomState(3510)
    cols = ["#c44f3a", "#3f7a72", "#e0a93a", "#5f6fa8", "#8a5a8a", "#d8cfb8"]
    for j in range(8):
        w = rs.uniform(2.2, 3.4) * k
        h = rs.uniform(9, 13) * k
        o.append(shape(rect_pts(xx, y - h, xx + w, y), cols[j % 6], blob(rect_pts(xx + w * .65, y - h, xx + w, y), "#000000", .18), w=.25 * k, seed=3520 + j))
        xx += w + .3 * k
    g = lib.rad_grad([(0, "#ffcf80", .45), (.5, "#ffb060", .16), (1, "#ffb060", 0)], 860, 420, 900, 700)
    o.append(f'<rect x="-200" y="-200" width="1480" height="2400" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    return f'<g {lib.blur(4.5)}>{"".join(o)}</g>'


def desk(c, t):
    yb = c.p((0, DESK_Y, WALL))[1]
    yf = c.p((0, DESK_Y, DESK_FRONT))[1]
    k = c.k(DESK_FRONT)
    o = [blob(rect_pts(-200, yb, 1280, yf), WOOD_HI)]
    # волокна дерева — по перспективе к точке схода
    for j in range(-14, 15):
        X = j * 9.0 + 3
        a, b = c.p((X, DESK_Y, WALL)), c.p((X, DESK_Y, DESK_FRONT))
        o.append(line([tuple(a), tuple(b)], .12 * k, WOOD_SH, seed=3710 + j + 20, op=.35, taper=.2, wmin=.4))
    rs = np.random.RandomState(3740)
    for j in range(10):
        X, Z = rs.uniform(-60, 60), rs.uniform(45, 110)
        L = rs.uniform(6, 16)
        a, b = c.p((X, DESK_Y, Z)), c.p((X + .3, DESK_Y, Z - L))
        o.append(line([tuple(a), tuple(b)], .1 * c.k(Z), WOOD_SH, seed=3750 + j, op=.3, taper=.5, wmin=.3))
    # тёплый отсвет лампы на столе и тень у стены
    g = lib.rad_grad([(0, "#ffe6b0", .38), (1, "#ffe6b0", 0)], 700, yb + 140, 520, 160)
    o.append(f'<rect x="-200" y="{yb:.1f}" width="1480" height="{yf - yb:.1f}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    o.append(blob(rect_pts(-200, yb, 1280, yb + 18), "#3e2414", .35, lib.blur(6)))
    # передняя кромка и тёмное под столом
    o.append(shape(rect_pts(-200, yf, 1280, yf + 1400), "#7a4a2b", blob(rect_pts(-200, yf + 300, 1280, yf + 1400), "#6a3f24", .9), w=.3 * k, seed=3760))
    for j, (xa, xb) in enumerate(((-150, 330), (370, 850), (890, 1300))):
        o.append(shape(rect_pts(xa, yf + 4.6 * k, xb, yf + 16 * k, 6), WOOD, blob(rect_pts(xa, yf + 14.5 * k, xb, yf + 16 * k), WOOD_SH, .9),
                       w=.28 * k, seed=3770 + j))
        hx = (xa + xb) / 2
        o.append(shape(rect_pts(hx - 2.6 * k, yf + 9.4 * k, hx + 2.6 * k, yf + 10.6 * k, 6), "#d9c08a", "", w=.22 * k, seed=3780 + j))
    o.append(shape(rect_pts(-200, yf, 1280, yf + 3.2 * k), WOOD, blob(rect_pts(-200, yf + 2 * k, 1280, yf + 3.2 * k), WOOD_SH, .9) +
                   line([(-180, yf + .5 * k), (1260, yf + .5 * k)], .14 * k, WOOD_HI, seed=3709, op=.9), w=.34 * k, seed=3712))
    g2 = lib.lin_grad([(0, "#000000", .35), (1, "#000000", 0)], 0, 0, 0, 1)
    o.append(f'<rect x="-200" y="{yf + 3.2 * k:.1f}" width="1480" height="260" fill="url(#{g2})"/>')
    return "".join(o)


def mug(c, X, Z):
    x, y = c.p((X, DESK_Y, Z))
    k = c.k(Z) * 11 / 128
    return blob(lib.ellipse_pts(x + 6 * k, y + 1, 60 * k, 10 * k, 14), "#1a100a", .3) + kitchen.mug(x, y, k, 0, col="#3f7a72")


def pencil(c, X0, Z0, X1, Z1):
    a, b = c.p((X0, DESK_Y - .4, Z0)), c.p((X1, DESK_Y - .4, Z1))
    import den_pencil
    return den_pencil.pencil(tuple(a), tuple(b), .8 * c.k((Z0 + Z1) / 2))


# ─────────── карточка
CARD_W, CARD_H = 10.0, 8.6
CARD_S = 1.0
ROWS = (1.9, 4.3, 6.7)
DIGITS = {
    1: [[(.18, .3), (.5, 0), (.5, 1)]],
    2: [[(.04, .28), (.22, .02), (.52, .02), (.62, .28), (.42, .6), (.04, 1), (.66, 1)]],
    3: [[(.06, .1), (.3, 0), (.56, .08), (.58, .3), (.3, .46)], [(.3, .46), (.6, .6), (.6, .86), (.34, 1), (.04, .92)]],
}


class Card:
    def __init__(self, c, X0, Z0, rot=8.0, lift=0.0):
        self.c, self.X0, self.Z0, self.rot, self.lift = c, X0, Z0, math.radians(rot), lift

    def P(self, u, v):
        cr, sr = math.cos(self.rot), math.sin(self.rot)
        X = self.X0 + u * cr + v * sr
        Z = self.Z0 - (v * cr - u * sr)
        return tuple(self.c.p((X, DESK_Y - .12 - self.lift, Z)))

    def k(self):
        return self.c.k(self.Z0 - CARD_H / 2)

    def draw(self, t, ticks=(1, 1), paw=1.0, glow=0.0):
        k = self.k()
        pts = [self.P(0, 0) + (1,), self.P(CARD_W, 0) + (1,), self.P(CARD_W, CARD_H) + (1,), self.P(0, CARD_H) + (1,)]
        o = [blob([(p[0] + .5 * k, p[1] + .45 * k) for p in pts], "#2a160a", .3, lib.blur(3))]
        inner = blob([self.P(0, CARD_H - .9), self.P(CARD_W, CARD_H - .9), self.P(CARD_W, CARD_H), self.P(0, CARD_H)], "#e9dfc6", .9)
        o.append(shape(pts, "#fbf5e2", inner, w=.26 * k, seed=8000))
        for i, v in enumerate(ROWS):
            # цифра с точкой
            for st in DIGITS[i + 1]:
                o.append(line([self.P(.7 + q[0] * .9, v - .75 + q[1] * 1.5) for q in st], .3 * k, INK, seed=8010 + i, taper=.3, wmin=.5))
            d = self.P(1.85, v + .7)
            o.append(blob(lib.ellipse_pts(d[0], d[1], .17 * k, .15 * k, 8), INK))
            # квадратик
            bx = 2.6
            box = [self.P(bx, v - .8) + (1,), self.P(bx + 1.6, v - .8) + (1,), self.P(bx + 1.6, v + .8) + (1,), self.P(bx, v + .8) + (1,)]
            o.append(shape(box, "#ffffff", "", w=.22 * k, seed=8020 + i))
            # строка-каракуля
            o.append(line([self.P(5.0 + q * 4.2, v + .25 * math.sin(q * 9 + i)) for q in np.linspace(0, 1, 12)], .26 * k, "#8d8a94", seed=8030 + i,
                          taper=.4, wmin=.5))
            if i < 2 and ticks[i] > 0:
                u = ticks[i]
                tk = [(bx + .25, v - .05), (bx + .75, v + .6), (bx + 2.0, v - 1.3)]
                tp = [self.P(*tk[0]), self.P(*tk[1])]
                if u >= 1:
                    tp.append(self.P(*tk[2]))
                o.append(line(tp, .42 * k, "#2f9a4a", seed=8040 + i, taper=.25, wmin=.5))
            if i == 2 and paw > 0:
                o.append(self.paw_print(bx + .8, v, .78 * paw))
        if glow > 0:
            cc = self.P(CARD_W / 2, CARD_H / 2)
            g = lib.rad_grad([(0, "#fff2b0", .55 * glow), (1, "#fff2b0", 0)], cc[0], cc[1], 9 * k, 6 * k)
            o.append(f'<ellipse cx="{cc[0]:.1f}" cy="{cc[1]:.1f}" rx="{9 * k:.1f}" ry="{6 * k:.1f}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
        return "".join(o)

    def paw_print(self, u, v, a=1.0):
        k = self.k()
        col = "#2a2532"
        o = []
        c = self.P(u, v + .2)
        o.append(blob(lib.ellipse_pts(c[0], c[1], .55 * k * a, .36 * k * a, 12), col))
        for j, (du, dv) in enumerate([(-.62, -.5), (-.22, -.78), (.22, -.78), (.62, -.5)]):
            q = self.P(u + du, v + dv + .1)
            o.append(blob(lib.ellipse_pts(q[0], q[1], .19 * k * a, .15 * k * a, 8), col))
        return "".join(o)


_ = mix
