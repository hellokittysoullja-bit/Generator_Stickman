"""Комната Димы рилса 33 снизу, у пола (сцена floor): стена с обоями (палитра времени суток как у desk рилса 33),
окно, часы, плинтус, дощатый пол в перспективе, письменный стол (столешница видна снизу, ножка, тумба с ящиками).
Всё строится в 3D (см) и проецируется камерой ribbon.Cam: глаз в (0, 0, 0), пол Y = FLOOR, стена Z = WALL_Z."""
import math

import numpy as np

import lib
from lib import INK, blob, line, mix, rect_pts, shape

WALL_Z = 230.0
PAL_WALL = {"morning": ("#8ea4b0", "#7b929f", "#9ab0bb"), "evening": ("#5d6474", "#4c5262", "#666d7d"),
            "day": ("#93abb6", "#7f97a3", "#a0b7c1")}
WOOD, WOOD_SH, WOOD_HI, WOOD_DK = "#9a6238", "#74462a", "#b97c4d", "#56331d"
FLOOR_C = {"morning": ("#7a5238", "#5a3a26"), "evening": ("#5e3f2c", "#44301f"), "day": ("#7a5238", "#5a3a26")}


class Room:
    def __init__(self, cam, floor_y=45.0, desk_top=-30.0, desk_z=150.0, desk_x=(-17.0, 120.0), ped_x=60.0, mode="morning"):
        self.cam, self.fy, self.dt, self.dz, self.dx, self.px, self.mode = cam, floor_y, desk_top, desk_z, desk_x, ped_x, mode

    def P(self, X, Y, Z):
        return tuple(self.cam.p((X, Y, Z)))

    def quad(self, pts3, fill, inner="", w=0.32, seed=0, corners=True):
        z = np.mean([p[2] for p in pts3])
        pr = [self.P(*p) + ((1,) if corners else ()) for p in pts3]
        return shape(pr, fill, inner, w=w * self.cam.k(z), seed=seed, var=.2, weight=.4)

    # ─────────── стена
    def wall(self, t):
        a, b, c = PAL_WALL[self.mode]
        pid = "pWallF" + a[1:]
        k = self.cam.k(WALL_Z)
        pw, ph = 90 * k / 4.8, 120 * k / 4.8
        x0, y0 = self.P(0, 0, WALL_Z)
        lib.DEFS.append(f'<pattern id="{pid}" x="{x0:.1f}" y="{y0:.1f}" width="{pw:.2f}" height="{ph:.2f}" patternUnits="userSpaceOnUse">'
                        f'<rect width="{pw:.2f}" height="{ph:.2f}" fill="{a}"/><rect x="0" width="{pw / 3:.2f}" height="{ph:.2f}" fill="{c}" opacity=".55"/>'
                        f'<path d="M{pw * .667:.1f} {ph * .15:.1f} l{pw * .078:.1f} {ph * .1:.1f} l{-pw * .078:.1f} {ph * .1:.1f} l{-pw * .078:.1f} {-ph * .1:.1f} Z '
                        f'M{pw * .667:.1f} {ph * .65:.1f} l{pw * .078:.1f} {ph * .1:.1f} l{-pw * .078:.1f} {ph * .1:.1f} l{-pw * .078:.1f} {-ph * .1:.1f} Z" '
                        f'fill="{b}" opacity=".7"/></pattern>')
        yb = self.P(0, self.fy, WALL_Z)[1]
        s = [f'<rect x="-400" y="-1400" width="1880" height="{yb + 1400:.1f}" fill="url(#{pid})"/>']
        # плинтус
        s.append(self.quad([(-300, self.fy - 8, WALL_Z), (300, self.fy - 8, WALL_Z), (300, self.fy, WALL_Z), (-300, self.fy, WALL_Z)], "#3a2a22",
                           blob(rect_pts(-400, self.P(0, self.fy - 3, WALL_Z)[1], 1480, yb), "#271b15", .9), seed=4001))
        return "".join(s)

    def window(self, t, X0=-98.0, X1=-36.0, Y0=-160.0, Y1=-62.0):
        x0, y0 = self.P(X0, Y0, WALL_Z)
        x1, y1 = self.P(X1, Y1, WALL_Z)
        k = self.cam.k(WALL_Z)
        if self.mode == "evening":
            sky = lib.lin_grad([(0, "#1d2a52", 1), (.55, "#5a4a7a", 1), (1, "#e08a4a", 1)], 0, 0, 0, 1)
            hcol, wcol, lit = "#2a2a48", "#22223c", "#ffc56a"
        else:
            sky = lib.lin_grad([(0, "#7fb6e0", 1), (.7, "#bfe0ef", 1), (1, "#fbe6b8", 1)], 0, 0, 0, 1)
            hcol, wcol, lit = "#8a9cb4", "#7486a0", None
        inner = [f'<rect x="{x0 - 20:.1f}" y="{y0 - 20:.1f}" width="{x1 - x0 + 40:.1f}" height="{y1 - y0 + 40:.1f}" fill="url(#{sky})"/>']
        if self.mode != "evening":
            inner.append(blob(lib.ellipse_pts(x0 + (x1 - x0) * .7, y0 + (y1 - y0) * .62, 7 * k, 7 * k, 18), "#fff3c4"))
            for j, (cx, cy) in enumerate([(.25, .2), (.62, .28)]):
                X, Y = x0 + (x1 - x0) * cx, y0 + (y1 - y0) * cy
                inner.append(blob([(X - 9 * k, Y + 2 * k), (X - 5 * k, Y - 3 * k), (X, Y - 4 * k), (X + 6 * k, Y - 2 * k), (X + 9 * k, Y + 2 * k)], "#ffffff", .9))
        rs = np.random.RandomState(3220)
        hx = x0 - 10
        while hx < x1 + 10:
            w = rs.uniform(12, 20) * k
            h = rs.uniform(.18, .42) * (y1 - y0)
            inner.append(shape(rect_pts(hx, y1 - h, hx + w, y1 + 20), hcol, blob(rect_pts(hx + w * .7, y1 - h, hx + w, y1 + 20), wcol, .8),
                               w=.25 * k, seed=int(hx)))
            if True:
                for r in range(4):
                    for cc in range(int(w // (5 * k))):
                        if rs.uniform() < .4:
                            wx, wy = hx + 2 * k + cc * 5 * k, y1 - h + 3 * k + r * 6 * k
                            if wy < y1:
                                inner.append(blob(rect_pts(wx, wy, wx + 2.4 * k, wy + 3.2 * k), lit or "#c9daea"))
            hx += w
        fr = "#e8dcc6"
        mx = (x0 + x1) / 2
        my = y0 + (y1 - y0) * .45
        inner.append(blob(rect_pts(mx - 1.2 * k, y0, mx + 1.2 * k, y1), fr) + blob(rect_pts(x0, my - 1.2 * k, x1, my + 1.2 * k), fr))
        s = [shape(rect_pts(x0 - 2.6 * k, y0 - 2.6 * k, x1 + 2.6 * k, y1 + 2.6 * k, 4), fr, blob(rect_pts(x1, y0 - 2.6 * k, x1 + 2.6 * k, y1 + 2.6 * k),
                                                                                                    "#c8baa2", .9), w=.5 * k, seed=3230)]
        s.append(shape(rect_pts(x0, y0, x1, y1, 2), "#7fb6e0", "".join(inner), w=.45 * k, seed=3231))
        s.append(shape(rect_pts(x0 - 5 * k, y1 + 2 * k, x1 + 5 * k, y1 + 5.5 * k, 3), "#efe4d0", blob(rect_pts(x0 - 5 * k, y1 + 4 * k, x1 + 5 * k, y1 + 5.5 * k),
                                                                                                         "#cbbda4", .9), w=.45 * k, seed=3232))
        # штора
        cx0 = x1 + 4 * k
        yb = self.P(0, self.fy - 10, WALL_Z)[1]
        cur = [(cx0, y0 - 7 * k), (cx0 + 8 * k, y0 - 7 * k), (cx0 + 9.5 * k, y0 + 24 * k), (cx0 + 7.5 * k, y1 + 7 * k), (cx0 + 11 * k, yb, 1),
               (cx0 + 1 * k, yb, 1), (cx0 + 1.6 * k, y1)]
        inn = blob([(cx0 + 4.5 * k, y0 - 7 * k), (cx0 + 8 * k, y0 - 7 * k), (cx0 + 9.5 * k, y0 + 24 * k), (cx0 + 7.5 * k, y1 + 7 * k), (cx0 + 11 * k, yb),
                    (cx0 + 6.5 * k, yb)], "#7d3b3b", .8)
        for j in range(3):
            xx = cx0 + 2.3 * k + j * 2.5 * k
            inn += line([(xx, y0 - 5 * k), (xx + .5 * k, y0 + 35 * k), (xx + 1.4 * k, yb - 9 * k)], .28 * k, "#5e2b2b", seed=3250 + j, op=.8)
        s.append(shape(cur, "#a24f48", inn, w=.48 * k, seed=3249))
        s.append(shape(rect_pts(x0 - 8 * k, y0 - 9 * k, x1 + 17 * k, y0 - 7 * k, 3), "#3a2a22", "", w=.35 * k, seed=3248))
        return "".join(s)

    def clock(self, X, Y, hour_a, min_a, R=13.0):
        cx, cy = self.P(X, Y, WALL_Z)
        r = R * self.cam.k(WALL_Z)
        k = r / 96
        s = [blob(lib.ellipse_pts(cx + 8 * k, cy + 12 * k, r + 12 * k, r + 12 * k, 28), "#0b0f1c", .3, lib.blur(5))]
        inner = blob(lib.ellipse_pts(cx + r * .22, cy + r * .22, r, r, 28), "#e3d8bf", .9)
        for i in range(12):
            a = math.radians(i * 30 - 90)
            r0, r1 = r * .86, r * (.68 if i % 3 == 0 else .74)
            inner += line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], 6 * k, INK, taper=.1,
                          wmin=.8, seed=3300 + i)
        g = [shape(lib.ellipse_pts(cx, cy, r + 16 * k, r + 16 * k, 28), "#2f3a4e", blob(lib.ellipse_pts(cx + 6 * k, cy + 8 * k, r + 10 * k, r + 10 * k, 28),
                                                                                        "#232c3c", .8), w=4.8 * k, seed=3290)]
        g.append(shape(lib.ellipse_pts(cx, cy, r, r, 28), "#f7f0dc", inner, w=3.8 * k, seed=3291))

        def hand(ang, L, w, tail, sd):
            a = math.radians(ang - 90)
            ux, uy = math.cos(a), math.sin(a)
            nx, ny = -uy, ux

            def P(u, v):
                return (cx + ux * u + nx * v, cy + uy * u + ny * v)
            pts = [P(-tail, -w * .35), P(L * .15, -w / 2), P(L * .82, -w * .32), P(L, 0) + (1,), P(L * .82, w * .32), P(L * .15, w / 2), P(-tail, w * .35)]
            return shape(pts, "#2a2532", "", w=3.2 * k, seed=sd)
        g.append(hand(hour_a, r * .5, 16 * k, 14 * k, 3310))
        g.append(hand(min_a, r * .76, 11 * k, 18 * k, 3311))
        g.append(shape(lib.ellipse_pts(cx, cy, 9 * k, 9 * k, 12), "#d8483c", "", w=3 * k, seed=3312))
        return "".join(s + g)

    # ─────────── пол
    def floor(self, z_near=30.0):
        c, cl = FLOOR_C[self.mode]
        yb = self.P(0, self.fy, WALL_Z)[1]
        s = [f'<rect x="-400" y="{yb - 1:.1f}" width="1880" height="3000" fill="{c}"/>']
        for j in range(-30, 31):
            X = j * 11.0
            a = self.P(X, self.fy, WALL_Z)
            b = self.P(X, self.fy, z_near)
            if max(a[0], b[0]) < -200 or min(a[0], b[0]) > 1280:
                continue
            s.append(line([a, b], .22 * self.cam.k(80), cl, seed=3600 + j + 40, op=.75, taper=.1, wmin=.4))
        rs = np.random.RandomState(3660)
        for j in range(-30, 31):
            Z = WALL_Z - rs.uniform(10, 120)
            X = j * 11.0
            if Z < z_near:
                continue
            a, b = self.P(X, self.fy, Z), self.P(X + 11, self.fy, Z)
            s.append(line([a, b], .18 * self.cam.k(Z), cl, seed=3700 + j + 40, op=.6, taper=.1, wmin=.5))
        return "".join(s)

    # ─────────── стол
    def desk(self, t, ped=True):
        x0, x1 = self.dx
        z0, z1 = self.dz, WALL_Z
        yt, yb = self.dt, self.dt + 4.0
        fy = self.fy
        s = []
        # тень под столом на стене и полу
        s.append(blob([self.P(x0 + 6, yb, WALL_Z), self.P(x1, yb, WALL_Z), self.P(x1, fy, WALL_Z), self.P(x0 + 6, fy, WALL_Z)], "#0e0a12", .26, lib.blur(8)))
        s.append(blob([self.P(x0 + 4, fy, WALL_Z), self.P(x1, fy, WALL_Z), self.P(x1, fy, z0 + 4), self.P(x0 + 4, fy, z0 + 4)], "#0e0a12", .26, lib.blur(8)))
        # задняя ножка (слева у стены)
        s.append(self.quad([(x0 + 1, yb, z1 - 6), (x0 + 5, yb, z1 - 6), (x0 + 5, fy, z1 - 6), (x0 + 1, fy, z1 - 6)], WOOD_SH, "", seed=3705))
        # низ столешницы (виден снизу)
        s.append(self.quad([(x0, yb, z0), (x1, yb, z0), (x1, yb, z1), (x0, yb, z1)], WOOD_DK,
                           blob([self.P(x0, yb, z0 + 20), self.P(x1, yb, z0 + 20), self.P(x1, yb, z1), self.P(x0, yb, z1)], "#3e2414", .7), seed=3706))
        if ped:
            px = self.px
            # левая боковина тумбы
            s.append(self.quad([(px, yb, z0), (px, yb, z1), (px, fy, z1), (px, fy, z0)], WOOD_SH,
                               blob([self.P(px, yb, z0 + 30), self.P(px, yb, z1), self.P(px, fy, z1), self.P(px, fy, z0 + 30)], "#5a3520", .6), seed=3707))
            # фасад тумбы с ящиками
            inner = ""
            for j, (ya, yb2) in enumerate(((yb + 3, yb + 31), (yb + 34, fy - 4))):
                a, b = self.P(px + 3, ya, z0), self.P(x1 - 3, yb2, z0)
                inner += shape(rect_pts(a[0], a[1], b[0], b[1], 4), WOOD_HI, blob(rect_pts(a[0], b[1] - (b[1] - a[1]) * .12, b[0], b[1]), WOOD_SH, .8),
                               w=.28 * self.cam.k(z0), seed=3720 + j)
                h0, h1 = self.P(px + 12, (ya + yb2) / 2 - 1, z0), self.P(px + 26, (ya + yb2) / 2 + 1, z0)
                inner += shape(rect_pts(h0[0], h0[1], h1[0], h1[1], 5), "#d9c08a", "", w=.22 * self.cam.k(z0), seed=3730 + j)
            s.append(self.quad([(px, yb, z0), (x1, yb, z0), (x1, fy, z0), (px, fy, z0)], WOOD, inner, seed=3714))
        # передняя левая ножка
        s.append(self.quad([(x0 + 1, yb, z0), (x0 + 5, yb, z0), (x0 + 5, fy, z0), (x0 + 1, fy, z0)], WOOD,
                           blob([self.P(x0 + 3.6, yb, z0), self.P(x0 + 5, yb, z0), self.P(x0 + 5, fy, z0), self.P(x0 + 3.6, fy, z0)], WOOD_SH, .9), seed=3713))
        # передняя кромка столешницы
        s.append(self.quad([(x0, yt, z0), (x1, yt, z0), (x1, yb, z0), (x0, yb, z0)], WOOD,
                           blob([self.P(x0, yt + 2.6, z0), self.P(x1, yt + 2.6, z0), self.P(x1, yb, z0), self.P(x0, yb, z0)], WOOD_SH, .9) +
                           line([self.P(x0 + 6, yt + 1, z0), self.P(x1, yt + 1, z0)], .14 * self.cam.k(z0), WOOD_HI, seed=3709, op=.9), seed=3712))
        return "".join(s)

    def light(self, t):
        if self.mode == "evening":
            g = lib.rad_grad([(0, "#ffcf80", .38), (.5, "#ffb060", .14), (1, "#ffb060", 0)], 560, 760, 760, 620)
            g2 = lib.rad_grad([(0, "#000000", 0), (.55, "#000000", 0), (1, "#0a0c1e", .55)], 560, 900, 1200, 1300)
            return (f'<rect x="-400" y="-400" width="1880" height="2800" fill="url(#{g})" style="mix-blend-mode:screen"/>'
                    f'<rect x="-400" y="-400" width="1880" height="2800" fill="url(#{g2})"/>')
        # утро: луч из окна наискосок и тёплая заливка
        x0, y0 = self.P(-98, -160, WALL_Z)
        x1, y1 = self.P(-36, -62, WALL_Z)
        g = lib.lin_grad([(0, "#fff4cc", .32), (1, "#fff4cc", 0)], 0, 0, 1, 1)
        fl = .9 + .1 * math.sin(t * 1.3)
        beam = [(x0, y0), (x1, y0 + 40), (x1 + 900, y1 + 1300), (x0 + 520, y1 + 1500)]
        g2 = lib.rad_grad([(0, "#000000", 0), (.6, "#000000", 0), (1, "#1a1424", .35)], 540, 900, 1150, 1300)
        return (f'<path d="{lib.fill_d([p + (1,) for p in beam])}" fill="url(#{g})" opacity="{fl:.3f}" style="mix-blend-mode:screen" {lib.blur(18)}/>'
                f'<rect x="-400" y="-400" width="1880" height="2800" fill="url(#{g2})"/>')


_ = mix
