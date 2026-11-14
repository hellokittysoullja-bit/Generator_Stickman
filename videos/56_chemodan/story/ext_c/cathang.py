"""Кот висит за шкирку (анфас, тот же кот, что cat.py): тело вытянуто вниз, передние лапы и задние болтаются, хвост свисает, огонёк на кончике.
draw(x, y, k, st, t) — (x, y) — точка захвата (шкирка), k — масштаб. st: swing (град, поворот всего кота вокруг захвата), lag (запаздывание лап),
shake (0..1: отряхивается — быстрые колебания), sq (сжатие по X), + состояния головы cat.head (turn, look, blink, ear, perk, smile, tilt), flame_e, head_rot."""
import math

import numpy as np

import cat as Cat
import lib
from ink import band, ellipse_pts, fur
from lib import INK, blob, line, shape

CAT, CAT_SH, CAT_FUR, CAT_EDGE = Cat.CAT, Cat.CAT_SH, Cat.CAT_FUR, Cat.CAT_EDGE
PAD = "#e8823a"
HEAD_Y = 178.0          # центр морды ниже захвата


def paw_front(sx, ang, ln, seed, t):
    """Передняя лапа: свисает из плеча; ang — раскачка (град)."""
    x0, y0 = sx * 74, 268
    a = math.radians(ang)
    ex, ey = x0 + math.sin(a) * ln + sx * 8, y0 + math.cos(a) * ln
    pts = [(x0, y0), ((x0 + ex) / 2 + sx * 5, (y0 + ey) / 2), (ex, ey)]
    o = shape(band(pts, 44, 36, step=4, cap=True), CAT, "", w=4.4, seed=seed)
    pw = ellipse_pts(ex + sx * 2, ey + 16, 24, 20, 12, rot=ang * .5)
    o += shape(pw, CAT, blob(ellipse_pts(ex + sx * 2, ey + 22, 14, 11, 10), PAD) + line([(ex - 6, ey + 6), (ex - 6, ey + 24)], 2, seed=seed + 3) +
               line([(ex + 6 + sx, ey + 6), (ex + 6 + sx, ey + 24)], 2, seed=seed + 4), w=4.4, seed=seed + 1)
    return o


def leg_hind(sx, ang, seed):
    x0, y0 = sx * 50, 505
    a = math.radians(ang)
    knee = (x0 + sx * 22 + math.sin(a) * 24, y0 + 62)
    foot = (x0 + math.sin(a) * 66 + sx * 6, y0 + 52 + math.cos(a) * 112)
    pts = [(x0, y0), knee, foot]
    o = shape(band(pts, 58, 34, step=4, cap=True), CAT, blob(ellipse_pts(x0 + sx * 12, y0 + 14, 18, 28, 8), CAT_SH, .5), w=4.6, seed=seed)
    fp = ellipse_pts(foot[0] + sx * 6, foot[1] + 14, 36, 22, 12, rot=sx * 12 + ang * .4)
    o += shape(fp, CAT, blob(ellipse_pts(foot[0] + sx * 8, foot[1] + 20, 20, 12, 10), PAD) +
               "".join(line([(foot[0] + dx, foot[1] + 4), (foot[0] + dx, foot[1] + 18)], 2, seed=seed + 7 + i) for i, dx in enumerate((-8, 6, 20))), w=4.6, seed=seed + 2)
    return o


def tail(t, swing2, energy):
    S0 = [(34, 520), (74, 566), (104, 630), (96, 700), (70, 744), (74, 786)]
    pts = [(p[0] + swing2 * (p[1] - 520) / 270 * 22, p[1]) for p in S0]
    o = shape(band(pts, 44, 18, step=4, cap=True), CAT, "", w=4.8, seed=7001)
    tip = pts[-1]
    fl = f'<g transform="translate({tip[0]:.1f} {tip[1] + 4:.1f}) scale(1 1) translate(-{Cat.FLAME_BASE[0]} -{Cat.FLAME_BASE[1]})">{Cat.flame(t, 1.2, energy)}</g>'
    return o + fl


def draw(x, y, k, st, t):
    sw = st.get("swing", 0.0)
    lag = st.get("lag", 0.0)
    sh = st.get("shake", 0.0)
    sq = st.get("sq", 1.0)
    fe = st.get("flame_e", 1.0)
    o = []
    o.append(tail(t, lag * .8, fe))
    o.append(leg_hind(-1, -10 - 22 * lag, 7100))
    o.append(leg_hind(1, 12 + 22 * lag, 7110))
    bd = [(-62, 232), (-84, 310), (-98, 400), (-84, 490), (-46, 546), (46, 546), (84, 490), (98, 400), (84, 310), (62, 232)]
    bp = fur(bd, 8, 6, seed=71)
    inner = blob([(40, 205), (98, 300), (100, 540), (40, 560), (60, 380)], CAT_SH, .9)
    inner += blob([(-44, 250), (0, 236), (44, 250), (40, 440), (0, 480), (-40, 440)], CAT_FUR, .6)
    for i, s_ in enumerate([[(-20, 290), (-14, 320)], [(16, 296), (10, 330)], [(0, 340), (2, 380)], [(-26, 380), (-20, 414)], [(24, 390), (18, 420)]]):
        inner += line(s_, 2.2, CAT_EDGE, seed=7120 + i, op=.85)
    o.append(shape(bp, CAT, inner, w=5, seed=7130))
    o.append(paw_front(-1, 8 + 20 * lag, 118 - 8 * sh, 7140, t))
    o.append(paw_front(1, -6 - 20 * lag, 124 - 8 * sh, 7150, t))
    # кожа, вытянутая к кулаку
    cone = [(-76, 116, 1), (-30, 44), (0, -34, 1), (30, 44), (76, 116, 1)]
    o.insert(0, shape(cone, CAT, blob([(10, -20), (76, 116), (20, 116)], CAT_SH, .8) + line([(-14, 90), (-4, 30)], 2, CAT_EDGE, seed=7160) +
                      line([(14, 90), (6, 30)], 2, CAT_EDGE, seed=7161), w=4.4, seed=7162))
    hs = dict(st)
    o.append(f'<g transform="translate(0 {HEAD_Y}) rotate({st.get("head_rot", 0.0):.2f} 0 20) translate(-836 -1072)">{Cat.head(hs, t)}</g>')
    return (f'<g transform="translate({x:.2f} {y:.2f}) rotate({sw:.2f}) scale({k * sq:.4f} {k:.4f})">{"".join(o)}</g>')
