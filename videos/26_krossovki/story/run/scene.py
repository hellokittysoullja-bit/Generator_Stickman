"""Сцена run рилса 26 (план s16, 29.88–32.68): утренний парк, Дима бежит по дорожке слева направо, камера едет рядом;
на «кот» (31.44) сзади вбегает кот галопом и бежит рядом, огонёк на хвосте сыплет искрами.

Мир — в «мировых» единицах, земля дорожки y = 0, x растёт вправо. Камера едет за тазом Димы. Всё, что стоит на
дорожке (Дима, кот, фонари и скамейка у её края, пятна света и тени), — в слое 1.0: ступня на опоре стоит в мире,
поэтому не скользит. Дальние слои (кусты, деревья, лес) — параллакс.
frame(t) -> SVG 1080×1920 (t — общее время ролика)."""
import math
import os
import sys

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import dima  # noqa: E402
import lib  # noqa: E402
import park  # noqa: E402
from lib import clamp, ease_io, ease_out, smooth  # noqa: E402

BS = dima.BS
LEG = (dima.THIGH + dima.SHIN) * BS
AHW = dima.AH * BS
TOEW = dima.TOE * BS * 1.22

T_START = 29.68
T_END = 32.88
T_CAT = 31.44

# ─── бег Димы по ровному: касания ───
TC, ST, STEP = 0.205, 0.125, 196.0      # шаг (с), опора (с), длина шага (мир)
V = STEP / TC                           # скорость, мир/с
X0 = 0.0


def _plan():
    C = []
    for k in range(-12, 40):
        t = T_START + k * TC
        C.append([t, "n" if k % 2 == 0 else "f", X0 + k * STEP, 0.0, t + ST])
    hip_keys = [(c[0] + ST / 2, c[2] + 6) for c in C]
    ts, xs = zip(*hip_keys)
    return dict(C=C, hip_x=PchipInterpolator(np.array(ts), np.array(xs)))


PL = _plan()


def hip_at(t, bob=True):
    x = float(PL["hip_x"](t))
    y = -(LEG * 0.86 + AHW)
    if bob:
        best = 9.0
        for c in PL["C"]:
            dt = t - (c[0] + ST / 2)
            if abs(dt) < abs(best):
                best = dt
        y += 12 * math.cos(2 * math.pi * best / TC)
    return np.array([x, y])


def planted(c, hip):
    A = np.array([c[2], c[3] - AHW])
    reach = LEG * 0.985
    if np.linalg.norm(A - hip) <= reach:
        return A, 0.0
    toe = np.array([c[2] + TOEW, c[3]])
    lo, hi = 0.0, 1.35
    for _ in range(30):
        m = (lo + hi) / 2
        A2 = toe + dima.rot(np.array([-TOEW, -AHW]), m)
        if np.linalg.norm(A2 - hip) > reach:
            lo = m
        else:
            hi = m
    return toe + dima.rot(np.array([-TOEW, -AHW]), hi), hi


def foot_at(side, t, hip):
    cs = [c for c in PL["C"] if c[1] == side]
    prev, nxt = cs[0], None
    for c in cs:
        if c[0] <= t:
            prev = c
        elif nxt is None:
            nxt = c
    if t <= prev[4] or nxt is None:
        return planted(prev, hip)
    t0, t1 = prev[4], nxt[0]
    u = clamp((t - t0) / (t1 - t0))
    A0, ph0 = planted(prev, hip_at(t0))
    A1 = np.array([nxt[2], nxt[3] - AHW])
    # мах: пятка к ягодице (вверх-назад), потом колено вперёд, стопа выносится и мягко ставится
    ux = (1 - math.cos(math.pi * u ** 1.3)) / 2
    x = A0[0] + (A1[0] - A0[0]) * ux - 30 * math.sin(math.pi * clamp(u * 1.5))
    y = A0[1] + (A1[1] - A0[1]) * u - 118 * math.sin(math.pi * clamp(u * 1.08)) ** 1.3
    if u < .3:
        phi = ph0 + (0.75 - ph0) * smooth(0, .3, u)
    elif u < .85:
        phi = 0.75 + (-0.26 - 0.75) * smooth(.3, .85, u)
    else:
        phi = -0.26 * (1 - smooth(.85, 1.0, u))
    return np.array([x, y]), phi


def dima_pose(t):
    hip = hip_at(t)
    feet = {s: foot_at(s, t, hip) for s in ("n", "f")}
    cn = [c[0] for c in PL["C"] if c[1] == "n"]
    tn = max([c for c in cn if c <= t], default=cn[0])
    psi = 2 * math.pi * (t - tn) / (2 * TC)
    arms = {}
    for s_, sg in (("n", 1), ("f", -1)):
        sw = -sg * math.cos(psi)
        arms[s_] = ("ang", 0.08 + 0.85 * sw, 1.45 + 0.35 * max(0, sw) - 0.4 * max(0, -sw))
    vy = (hip_at(t)[1] - hip_at(t - .05)[1]) / .05
    # взгляд: вперёд; когда кот рядом — вниз на кота и шире улыбка
    k = smooth(31.62, 31.92, t)
    look = (0.42 - 0.8 * k, -0.05 + 0.5 * k)
    return dict(hip=hip, lean=0.24, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"},
                head_ang=-0.06 + 0.10 * k, hood=clamp(-vy * 0.05, -16, 22),
                strings=(clamp(-vy * .04, -30, 30) - 18, clamp(vy * .05, -20, 30)),
                expr=dict(lid=0.72 + 0.1 * k, look=look, brows="up", mouth="grin", hair=clamp(vy * 0.035, -16, 16)))


# ─── камера ───
S0 = 1.50
DIMA_SX = 400.0          # экранный x таза
GROUND_SY = 1236.0       # экранный y земли (подошвы Димы)


def camera(t):
    h = (hip_at(t, bob=False) + hip_at(t + .1, bob=False)) / 2
    z = 1.0 + 0.045 * ease_io(clamp((t - T_START) / (T_END - T_START)))
    s = S0 * z
    shift = -30 * smooth(31.5, 32.2, t)            # дать место коту справа
    sx = DIMA_SX + shift
    cx = h[0] + (540 - sx) / s
    cy = (960 - GROUND_SY) / s + 4 * math.sin(t * 2.1)
    rot = 0.5 * math.sin(t * 1.7 + .4)
    return cx, cy, s, rot


def frame(t):
    lib.DEFS.clear()
    cx, cy, s, rot = camera(t)
    body = []
    body.append(park.backdrop(cx, cy, s, rot, t))
    wb = [park.ground(cx, cy, s, t)]
    p = dima_pose(t)
    g, _ = dima.draw(p)
    cs = Cat.state(t, hip_at(t, bob=False)[0], V) if t >= T_CAT - 0.05 else None
    cg = Cat.draw(cs, t) if cs else ""
    wb.append(park.long_shadow(g, 0.0))
    if cs:
        wb.append(park.long_shadow(cg, Cat.LANE_Y))
    wb.append(park.props_back(cx, s, t))
    wb.append(g)
    if cs:
        wb.append(Cat.sparks(cs, t))
        wb.append(cg)
    body.append(f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(wb)}</g>')
    body.append(park.foreground(cx, cy, s, rot, t))
    return lib.svg("".join(body))
