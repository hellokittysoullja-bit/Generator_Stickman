"""s16 (28.00–30.06, клип 27.80–30.26): низкий план на уровне кота — кот гордо шагает рядом с ногами Димы (Дима
идёт тем же шагом, видны ноги и низ худи), нос и хвост с огоньком задраны; на «гордо» (28.72) грудь колесом,
глаза довольно закрыты, огонёк вспыхивает ярче, искры. Камера едет вбок вровень с котом."""
import math

import numpy as np

import cat_walk
import dima
import lib
import park
import walk
import world
from lib import clamp, ease_io, smooth

T_A, T_B = 27.80, 30.26
GROUND_SY = 1185.0


def camera(t):
    cxw = walk.hip_at(t, bob=False)[0] + cat_walk.REL
    s = 2.30 + 0.05 * ease_io(clamp((t - T_A) / (T_B - T_A)))
    sx = 640 - 20 * ease_io(clamp((t - T_A) / (T_B - T_A)))
    cx = cxw + (540 - sx) / s
    cy = (960 - GROUND_SY) / s + 2.5 * math.sin(t * 2.2)
    rot = 0.3 * math.sin(t * 1.4 + .7)
    return cx, cy, s, rot


def frame(t):
    lib.DEFS.clear()
    cam = camera(t)
    cx, cy, s, rot = cam
    body = [park.backdrop(cx, cy, s, rot, t)]
    wb = [world.ground(cx, cy, s, t)]
    p = walk.pose(t, expr=dict(lid=.9, look=(.4, .6), brows="up", mouth="grin", hair=0), head_ang=.1)
    g, _ = dima.draw(p)
    cg, b = cat_walk.draw(t)
    wb.append(park.long_shadow(g, 0.0))
    wb.append(park.long_shadow(cg, cat_walk.LANE_Y))
    wb.append(world.props_back(cx, s, t))
    wb.append(g)
    wb.append(cg)
    body.append(f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(wb)}</g>')
    body.append(park.foreground(cx, cy, s, rot, t))
    k = 0.05 * smooth(cat_walk.T_PROUD - .04, cat_walk.T_PROUD + .1, t) * (1 - 0.6 * smooth(29.0, 30.2, t))
    if k > 0:
        pc = world.to_screen(np.array([b["S"][0] * cat_walk.CS, -150.0]), cam)
        return lib.svg(f'<g transform="translate({pc[0]:.1f} {pc[1]:.1f}) scale({1 + k:.4f}) translate({-pc[0]:.1f} {-pc[1]:.1f})">'
                       f'{"".join(body)}</g>')
    return lib.svg("".join(body))
