"""Рилс 51, группа C: s09 облако (чувство без имени), s10/s11 Калифорния (карточки, слово «ЗЛОСТЬ»), s12 мозг (миндалина),
s14 рукописная строка и сжимающееся облако. frame(sid, t) -> SVG 1080x1920; t — общее время ролика (удары на словах words.json)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dima  # noqa: E402
import hw  # noqa: E402
import lib  # noqa: E402
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, mul, rad_grad,  # noqa: E402
                 rect_pts, shape, smooth, spring, lin_grad)

RED, RED_SH, RED_HI = "#d8392f", "#a3231f", "#ef6048"


def noise(t, a, b, c=0.0):
    return math.sin(t * a + c) * math.sin(t * b + c * 1.7)


# ───────────────────────── красное облако (злость без имени)
def cloud_pts(cx, cy, R, t, seed=0.0, n=54, squash=1.0, calm=0.0):
    k = 1.0 - 0.7 * calm
    pts = []
    n = 80
    for i in range(n):
        th = 2 * math.pi * i / n
        r = 1 + k * (0.13 * math.sin(3 * th + 1.5 * t + seed) + 0.09 * math.sin(5 * th - 2.3 * t + seed * 2) + 0.03 * math.sin(7 * th + 3.1 * t + seed * 3)
                     + 0.06 * math.sin(2 * th + 0.8 * t + seed))
        r += 0.045 * k * math.sin(6 * th + 1.0) ** 2
        pts.append((cx + R * r * math.cos(th), cy + R * r * math.sin(th) * squash))
    return pts


def angry_cloud(cx, cy, R, t, seed=0.0, squash=1.0, calm=0.0, lw=None, streaks=True):
    """Бесформенное облако: плоский красный, одна тень справа-снизу, пара свилей внутри, отростки-язычки."""
    lw = lw or (5.5 + R * 0.012)
    pts = cloud_pts(cx, cy, R, t, seed, squash=squash, calm=calm)
    inner = blob([(cx + R * 0.1, cy - R * 1.4), (cx + R * 1.6, cy - R * .5), (cx + R * 1.6, cy + R * 1.6), (cx - R * .6, cy + R * 1.6),
                  (cx + R * .45, cy + R * .3)], RED_SH, .95)
    inner += blob(ellipse_pts(cx - R * .38, cy - R * .42, R * .34, R * .2, 14, rot=-28), RED_HI, .85)
    if streaks:
        for j in range(4):
            ph = seed + j * 1.7 + t * (1.6 + .3 * j)
            a0 = j * 1.55 + 0.4
            sp = [(cx + R * (.15 + .5 * u) * math.cos(a0 + 1.9 * u + .25 * math.sin(ph + u * 3)),
                   cy + R * squash * (.15 + .5 * u) * math.sin(a0 + 1.9 * u + .25 * math.sin(ph + u * 3))) for u in np.linspace(0, 1, 9)]
            inner += line(sp, 4 + R * .006, "#7a1714", taper=.7, wmin=.2, seed=11 + j, op=.55)
    s = [shape(pts, RED, inner, w=lw, seed=21)]
    return "".join(s)


def sparks(cx, cy, R, t, n=7, seed=0.0):
    s = []
    for i in range(n):
        th = 2 * math.pi * i / n + seed
        ph = (t * 2.2 + i * .37) % 1.0
        if ph > .55:
            continue
        r0 = R * (1.05 + 0.25 * ph)
        x, y = cx + r0 * math.cos(th), cy + r0 * math.sin(th)
        L = 24 + R * .05
        d = (math.cos(th), math.sin(th))
        nn = (-d[1], d[0])
        zig = [(x, y), (x + d[0] * L * .4 + nn[0] * L * .25, y + d[1] * L * .4 + nn[1] * L * .25),
               (x + d[0] * L * .6 - nn[0] * L * .25, y + d[1] * L * .6 - nn[1] * L * .25), (x + d[0] * L, y + d[1] * L)]
        s.append(line(zig, 6 + R * .008, "#ffe36a", taper=.5, wmin=.3, seed=40 + i, op=1 - ph * 1.6))
    return "".join(s)


# ───────────────────────── Дима в профиль, стоя (local: земля y=0, x=0)
def dima_stand(t, mode, sc, x, y, scare=0.0):
    hipy = -(0.92 * (dima.THIGH + dima.SHIN) * dima.BS + dima.AH * dima.BS)
    A = -dima.AH * dima.BS
    br = math.sin(t * 2.4) * 1.2
    pose = dict(hip=(0.0, hipy + br), lean=-0.10 * (1 - scare) + 0.16 * scare,
                feet={"n": (np.array([22.0, A]), 0.0), "f": (np.array([-18.0, A]), 0.0)},
                arms={"n": ("ang", 0.10 - 0.9 * scare, 1.2 + 0.7 * scare), "f": ("ang", -0.05 - 0.7 * scare, 1.0 + 0.8 * scare)},
                hands={"n": "fist", "f": "fist"}, head_ang=-0.20 * (1 - scare) + 0.10 * scare, hood=3 * scare,
                expr=dict(lid=0.95, look=(0.25, -0.75 * (1 - scare) + 0.2 * scare), brows="worry", mouth="gape", hair=4 * math.sin(t * 5)))
    g, _ = dima.draw(pose)
    return f'<g transform="translate({f(x)} {f(y)}) scale({sc:.4f})">{g}</g>'


def s09(t):
    # слова: чувство 14.08, без 14.44, имени 14.72, оно 15.20, кажется 15.44, огромным 16.00, и 16.56, главным 16.72
    R = 190 + 14 * math.sin(t * 3.1)
    R += 70 * ease_out(clamp((t - 13.5) / 0.9)) * 0                       # плавное начало задаётся ниже
    base = 150 + 55 * smooth(13.5, 14.4, t)
    R = base
    R += 60 * spring(t - 14.44, 3.2, 6.0) * (1 if t >= 14.44 else 0)      # «без»: толчок
    R += 40 * spring(t - 14.72, 3.2, 6.0) * (1 if t >= 14.72 else 0)      # «имени»: ещё толчок
    R += 150 * smooth(14.8, 15.9, t)                                        # «кажется»: ползёт
    R += 420 * ease_out(clamp((t - 16.0) / 0.55), 2.2)                      # «огромным»: занимает экран
    R += 330 * ease_out(clamp((t - 16.72) / 0.6), 2)                        # «главным»
    cx = 540 + 18 * math.sin(t * 1.9)
    cy = 400 - 250 * smooth(15.6, 17.3, t) + 14 * math.sin(t * 2.3)
    z = 1.0 - 0.38 * ease_io(clamp((t - 16.1) / 1.4))
    scare = smooth(14.38, 14.7, t) * (1 - 0.3 * smooth(15.2, 15.9, t)) + 0.5 * smooth(15.95, 16.3, t)
    scare = clamp(scare)
    glow = rad_grad([(0, "#ff5a3a", .55), (.5, "#ff5a3a", .18), (1, "#ff5a3a", 0)], cx, cy, R * 2.6 + 200)
    bgl = lin_grad([(0, "#2f2c47", 1), (.55, "#4b3d5a", 1), (1, "#6a4c4c", 1)], 0, 0, 0, 1)
    body = [f'<rect x="-1500" y="-1500" width="{W + 3000}" height="{H + 3000}" fill="url(#{bgl})"/>',
            f'<rect x="-1500" y="-1500" width="{W + 3000}" height="{H + 3000}" fill="url(#{glow})"/>',
            f'<rect x="-1500" y="1250" width="{W + 3000}" height="1900" fill="#3a2b33"/>',
            f'<rect x="-1500" y="1250" width="{W + 3000}" height="10" fill="#241a22"/>']
    # пятно-тень на земле от облака
    body.append(blob(ellipse_pts(540, 1262, 260 + R * .5, 34 + R * .06, 24), "#140c12", .45, blur(10)))
    body.append(angry_cloud(cx, cy, R, t, seed=0.7, squash=0.9 + 0.1 * math.sin(t * 2.0)))
    body.append(sparks(cx, cy, R, t))
    body.append(dima_stand(t, "", 0.86, 540, 1250, scare))
    g = "".join(body)
    return f'<g transform="translate(540 1250) scale({z:.4f}) translate(-540 -1250)">{g}</g>'


import scene_cal  # noqa: E402

import scene_brain  # noqa: E402

import scene_note  # noqa: E402

FRAMES = {"s14": scene_note.s14, "s12": scene_brain.s12, "s09": s09, "s10": scene_cal.s10, "s11": scene_cal.s11}


def frame(sid, t):
    lib.dyn_begin()
    return lib.svg(FRAMES[sid](t))
