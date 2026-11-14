"""Чемодан рилса 56 (группа C): мягкий чемодан-раскладушка в косой проекции (камера выше и спереди), крышка на шарнире сзади.
Suit(cx, by, W, D, Hb, e).  e — угол камеры (32° — вид спереди сверху, 90° — строго сверху); th — угол крышки (0 закрыта, 90 стоит,
180 лежит раскрытой назад). Слои: back() — нутро и крышка, front() — передняя стенка с молнией. Внутри — «горка» вещей."""
import math

import numpy as np

import lib
from lib import INK, blob, clamp, ellipse_pts, line, rrect, shape

BODY, BODY_SH, BODY_HI, BODY_DK = "#3f8f94", "#2d6d73", "#74bcbb", "#245c62"
LID, LID_SH = "#47999a", "#33777c"
LINING, LINING_SH = "#f1e4c6", "#dcc79a"
DARK = "#2b2530"
METAL, METAL_SH = "#e2ddd2", "#a8a398"


class Suit:
    def __init__(s, cx, by, W=700.0, D=300.0, Hb=230.0, e=32.0, th=0.0, lid_t=34.0, clothes=True):
        s.cx, s.by, s.W, s.D, s.Hb, s.th, s.lid_t = cx, by, W, D, Hb, th, lid_t
        s.e = math.radians(e)
        s.c, s.s = math.cos(s.e), math.sin(s.e)
        s.clothes = clothes

    def P(s, x, y, z):
        return (s.cx + x, s.by - (z * s.c + y * s.s))

    def lidp(s, x, v, h):
        th = math.radians(s.th)
        return s.P(x, s.D - v * math.cos(th) + h * math.sin(th), s.Hb + v * math.sin(th) + h * math.cos(th))

    def outer_visible(s):
        return math.sin(s.e - math.radians(s.th)) > 0.02

    # ───────── нутро ─────────
    def interior(s, inset=22.0, floor=None):
        W, D, Hb = s.W / 2, s.D, s.Hb
        quad = [s.P(-W + inset, inset, Hb) + (1,), s.P(W - inset, inset, Hb) + (1,), s.P(W - inset, D - inset, Hb) + (1,), s.P(-W + inset, D - inset, Hb) + (1,)]
        rim = [s.P(-W, 0, Hb) + (1,), s.P(W, 0, Hb) + (1,), s.P(W, D, Hb) + (1,), s.P(-W, D, Hb) + (1,)]
        o = shape(rim, BODY_DK, "", w=5, seed=3001)
        inner = ""
        if s.clothes:
            cid_items = []
            for i, (fx, fy, r, col, h) in enumerate([(-.62, .55, .17, "#d6584a", 28), (-.28, .72, .21, "#e8b640", 34), (.12, .6, .2, "#5b86c0", 30),
                                                    (.5, .74, .2, "#8bb56a", 32), (.66, .42, .14, "#c06c9a", 22), (-.55, .28, .13, "#f0eadc", 20)]):
                px, py = s.P(fx * W, fy * (D - 2 * inset) + inset, Hb + h)
                rx, ry = r * s.W * .55, r * s.W * .36
                cid_items.append(blob(ellipse_pts(px, py, rx, ry, 14), col) +
                                 line([(px - rx * .5, py - ry * .2), (px, py - ry * .5), (px + rx * .5, py - ry * .2)], 3, lib.mul(col, (.7, .7, .75)), seed=3010 + i, op=.9))
            inner = "".join(cid_items)
        o += shape(quad, floor or DARK, inner, w=4.2, seed=3002)
        return o

    # ───────── крышка ─────────
    def lid(s):
        W, D, t = s.W / 2, s.D, s.lid_t
        pts = lambda h, v0, v1: [s.lidp(-W, v0, h) + (1,), s.lidp(W, v0, h) + (1,), s.lidp(W, v1, h) + (1,), s.lidp(-W, v1, h) + (1,)]
        o = ""
        edge = [s.lidp(-W, D, 0) + (1,), s.lidp(W, D, 0) + (1,), s.lidp(W, D, t) + (1,), s.lidp(-W, D, t) + (1,)]
        if s.outer_visible():
            o += shape(edge, LID_SH, "", w=4.6, seed=3101)
            ridges = ""
            for k in range(1, 6):
                x = -W + k * (2 * W / 6)
                ridges += line([s.lidp(x, 18, t), s.lidp(x, D - 18, t)], 3.4, LID_SH, seed=3110 + k, op=.9)
            o += shape(pts(t, 0, D), LID, ridges, w=5, seed=3102)
            # блик
            o += blob([s.lidp(-W * .8, D * .62, t), s.lidp(-W * .2, D * .62, t), s.lidp(-W * .25, D * .8, t), s.lidp(-W * .8, D * .8, t)], BODY_HI, .35)
        else:
            lin = pts(0, 0, D)
            stripes = "".join(line([s.lidp(-W + 30, D * k / 5, 0), s.lidp(W - 30, D * k / 5, 0)], 2.6, LINING_SH, seed=3120 + k, op=.8) for k in range(1, 5))
            o += shape(edge, LID_SH, "", w=4.6, seed=3101)
            o += shape(lin, LINING, stripes, w=5, seed=3103)
        return o

    # ───────── передняя стенка ─────────
    def front(s, zip_pull=0.0):
        W, Hb = s.W / 2, s.Hb
        r = 22
        fr = [s.P(-W, 0, Hb), s.P(W, 0, Hb), s.P(W, 0, 0), s.P(-W, 0, 0)]
        x0, y0, x1, y1 = fr[0][0], fr[0][1], fr[1][0], fr[2][1]
        o = ""
        # колёса
        for sx in (-1, 1):
            wx = s.cx + sx * (W - 70)
            o += shape(ellipse_pts(wx, y1 + 6, 34, 26, 12), "#2a2630", blob(ellipse_pts(wx - 6, y1 + 2, 14, 10, 8), "#58516a", .8), w=4, seed=3200 + sx)
        ridges = ""
        for k in range(1, 7):
            x = x0 + k * (x1 - x0) / 7
            ridges += line([(x, y0 + 36), (x, y1 - 26)], 7, BODY_SH, seed=3210 + k, op=.9, taper=.3, wmin=.7)
            ridges += line([(x + 8, y0 + 40), (x + 8, y1 - 30)], 3, BODY_HI, seed=3220 + k, op=.7, taper=.3, wmin=.7)
        shade = blob([(x0, y1 - 60), (x1, y1 - 60), (x1, y1), (x0, y1)], BODY_SH, .55)
        o += shape(rrect(x0, y0, x1, y1, r), BODY, ridges + shade, w=5.6, seed=3230)
        # молния по ободу: зубчики
        zy = y0 + 14
        teeth = line([(x0 + 22, zy), (x1 - 22, zy)], 9, "#1b4348", seed=3240, taper=0.1, wmin=.9)
        for k in range(0, int((x1 - x0 - 50) / 16)):
            xx = x0 + 28 + k * 16
            teeth += line([(xx, zy - 5), (xx + 5, zy + 5)], 2.2, METAL, seed=3250 + k, op=.95, taper=.1, wmin=.9)
        o += teeth
        # бегунок и замок
        px = x0 + 90 + zip_pull
        o += shape(rrect(px - 18, zy - 14, px + 18, zy + 26, 6), METAL, blob([(px - 18, zy + 8), (px + 18, zy + 8), (px + 18, zy + 26), (px - 18, zy + 26)], METAL_SH, .8),
                   w=3.6, seed=3260)
        o += shape(ellipse_pts(px, zy + 46, 11, 14, 10), METAL, "", w=3.2, seed=3261)
        lx = s.cx
        o += shape(rrect(lx - 34, zy - 18, lx + 34, zy + 40, 10), "#d7a23a", blob([(lx - 34, zy + 18), (lx + 34, zy + 18), (lx + 34, zy + 40), (lx - 34, zy + 40)], "#a9771f", .7),
                   w=4, seed=3262)
        o += shape(ellipse_pts(lx, zy + 12, 8, 8, 8), "#6e4a12", "", w=2.4, seed=3263)
        # углы-накладки
        for sx in (-1, 1):
            cx_ = x1 - 4 if sx > 0 else x0 + 4
            o += blob([(cx_, y1 - 70), (cx_ - sx * 40, y1 - 70), (cx_ - sx * 40, y1), (cx_, y1)], BODY_DK, .9)
        return o

    def lid_closed_over(s):
        return s.lid() if s.outer_visible() else ""
