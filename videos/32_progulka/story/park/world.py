"""Мир парка для s14–s16: те же слои, что в рилсе 26 (park.py), но свои деревья у дорожки — три дерева, мимо которых
идёт Дима (третье — там, где приходит идея), фонари и скамейка между ними. Шаг Димы — walk.py, кот — cat_walk.py."""
import math

import numpy as np

import lib
import park
from lib import blob, ellipse_pts

# деревья у дальнего края дорожки (мир): (x, высота, ширина кроны, зерно)
TREES = [(430.0, 880, 430, 11), (1051.0, 860, 400, 12), (1331.0, 900, 420, 13), (1611.0, 940, 450, 14), (2150.0, 870, 420, 15),
         (2520.0, 900, 430, 16)]
LAMPS = [760.0, 1880.0]
BENCH = 2330.0
park.LAMPS = LAMPS
park.BENCH = BENCH
park.EDGE_TREES = []


def ground(cx, cy, s, t):
    g = park.ground(cx, cy, s, t)
    x0, x1 = park.view(cx, s)
    o = [g]
    for tx, h, w, sd in TREES:
        if x0 - 900 < tx < x1:
            o.append(blob([(tx - 22, park.EDGE_Y), (tx + 22, park.EDGE_Y), (tx + 22 + 480, park.EDGE_Y + 300), (tx - 22 + 480, park.EDGE_Y + 304)],
                          park.SHADOW, .2))
    return "".join(o)


def props_back(cx, s, t):
    x0, x1 = park.view(cx, s)
    o = [park.props_back(cx, s, t)]
    for tx, h, w, sd in TREES:
        if x0 - 500 < tx < x1 + 500:
            o.append(park.tree(tx, park.EDGE_Y + 6, h, w, 1300 + sd, ink_w=4.4))
    return "".join(o)


def glow(x, y, r, col, op):
    g = lib.rad_grad([(0, col, op), (.45, col, op * .45), (1, col, 0)], x, y, r)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#{g})"/>'


def blink_flash(op):
    """Белая вспышка поверх кадра (экран)."""
    if op <= 0.003:
        return ""
    return f'<rect width="1080" height="1920" fill="#fffbe6" opacity="{op:.3f}"/>'


def ground_shadow(x, w, op=.28):
    return blob(ellipse_pts(x, 4, w, w * .14, 14), "#3a3f63", op, lib.blur(4))


def rs(*k):
    return np.random.RandomState(abs(park.hash_int(*k)) % (2 ** 31))


def sq(u):
    return math.sin(math.pi * u)


def to_screen(p, cam):
    cx, cy, s, rot = cam
    a = math.radians(rot)
    x, y = (p[0] - cx) * s, (p[1] - cy) * s
    return np.array([540 + x * math.cos(a) - y * math.sin(a), 960 + x * math.sin(a) + y * math.cos(a)])


def push(body, k, p, s2):
    """Экранный наезд всего кадра (фон и мир вместе — без расхождения слоёв): масштаб 1→s2 к точке p, p едет к центру."""
    if k <= 0:
        return body
    sc = 1 + (s2 - 1) * k
    tx = p[0] + (540 - p[0]) * k * .85
    ty = p[1] + (900 - p[1]) * k * .85
    return f'<g transform="translate({tx:.2f} {ty:.2f}) scale({sc:.4f}) translate({-p[0]:.2f} {-p[1]:.2f})">{body}</g>'
