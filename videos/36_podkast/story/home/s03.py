"""s03 (3.30–4.85, клип 3.10–5.05): вечер, прихожая. Дима в куртке, с сумкой на плече, делает шаг к двери и на
«Каждый вечер» (3.52) берётся за ручку; на «находилась» (4.28) за окном справа от двери начинается ливень (тучи,
косые струи, капли на стекле, комната чуть холоднее), Дима замирает с рукой на ручке и косится на окно.
Камера — дрейф вправо (к окну) и лёгкий наезд."""
import math

import numpy as np

import dima
import hall
import hero
import lib
from lib import clamp, ease_io, ease_out, smooth

T_A, T_B = 3.10, 5.05
T_GRAB, T_RAIN = 3.52, 4.28


def pose(t):
    st = ease_io((t - T_A) / 0.36)
    hx = 112 + 66 * st
    # шаг: ближняя нога вперёд, потом подтягивается дальняя
    un = clamp((t - T_A) / 0.26)
    nx = 150 + 70 * ease_io(un)
    ny = -hero.SOLE - 26 * math.sin(math.pi * un)
    uf = clamp((t - T_A - 0.16) / 0.24)
    fx = 82 + 70 * ease_io(uf)
    fy = -hero.SOLE - 20 * math.sin(math.pi * uf)
    freeze = smooth(T_RAIN + 0.05, T_RAIN + 0.22, t)
    expr = dict(lid=0.55 + 0.35 * freeze, look=(0.45 + 0.5 * freeze, -0.05 - 0.35 * freeze), brows="worry" if freeze > .5 else "det",
                mouth="gape" if freeze > .6 else "flat", hair=4 * math.sin(math.pi * un) - 6 * freeze * math.exp(-8 * max(0, t - T_RAIN - .1)))
    bob = -7 * math.sin(math.pi * st) + 2 * math.sin(t * 4)
    p = hero.stand(hx, fx, nx, dy=bob, lean=0.06 + 0.04 * smooth(T_GRAB - .2, T_GRAB, t) - 0.07 * freeze, expr=expr,
                   head_ang=-0.08 * freeze + 0.02 * math.sin(t * 3))
    p["feet"] = {"f": (np.array([fx, fy]), 0.18 * math.sin(math.pi * uf)), "n": (np.array([nx, ny]), 0.2 * math.sin(math.pi * un))}
    # рука к ручке: от бока — к ручке двери (3.36–3.58), держит
    knob = np.array(hall.KNOB) + np.array([-34.0, 6.0])
    side = np.array([hx + 50, -330.0])
    ur = ease_out((t - T_GRAB + 0.17) / 0.24, 2.5)
    tgt = side + (knob - side) * ur
    # замер: рука на ручке чуть дёргается
    tgt[0] += -3 * freeze * math.sin((t - T_RAIN) * 40) * math.exp(-6 * max(0, t - T_RAIN - .05))
    p["arms"] = {"n": ("ik", tgt, -1), "f": ("ik", np.array([hx - 40, -380.0]), -1)}
    p["hands"] = {"n": ("open", 0.15 + 0.75 * smooth(T_GRAB - 0.04, T_GRAB + 0.06, t)), "f": "fist"}
    p["hand_dir"] = {"n": (1.0, 0.15)}
    sw = 26 * math.sin(math.pi * st) * math.cos(t * 7) + 6 * math.sin(t * 5)
    p["over_torso"] = hero.bag_on_shoulder(sw)
    p["hood"] = 4 * math.sin(t * 8) * (1 - st)
    return p


def camera(t):
    u = (t - T_A) / (T_B - T_A)
    cx = 290 + 50 * u + 95 * ease_io((t - T_RAIN + 0.1) / 0.6)
    s = 1.52 + 0.08 * u + 0.025 * smooth(T_RAIN, T_RAIN + 0.12, t) * math.exp(-3 * max(0, t - T_RAIN - .12))
    cy = -405 + 6 * math.sin(t * 2)
    return cx, cy, s, 0.4 * math.sin(t * 1.3)


def frame(t):
    lib.DEFS.clear()
    dima.set_palette(dima.JACKET)
    rain = smooth(T_RAIN - 0.04, T_RAIN + 0.3, t)
    g, info = dima.draw(pose(t))
    mid = f'<ellipse cx="{info["head"][0]:.1f}" cy="4" rx="150" ry="18" fill="#3a2418" opacity=".28"/>' + g
    # холодный свет ливня из окна
    x0, y0, x1, y1 = hall.WIN
    fg = ""
    if rain > 0:
        gl = lib.rad_grad([(0, "#9fb6e8", .30 * rain), (1, "#9fb6e8", 0)], (x0 + x1) / 2, (y0 + y1) / 2, 520, 620)
        fg = f'<ellipse cx="{(x0 + x1) / 2}" cy="{(y0 + y1) / 2}" rx="520" ry="620" fill="url(#{gl})"/>'
    tint = f'<rect width="1080" height="1920" fill="#2a3a6a" opacity="{0.09 * rain:.3f}"/>' if rain > 0 else ""
    out = hall.frame(t, cam=camera(t), rain=rain, mid=mid, fg=fg, screen_fg=tint)
    dima.set_palette(dima.HOODIE)
    return out
