"""s15 (26.00–28.00, клип 25.80–28.20): Дима идёт шагом, камера едет вбок, деревья у дорожки проплывают (первое,
второе); у третьего на «третьего» (27.08) над головой выскакивает большая лампочка и загорается, на «дерева» (27.52)
вспышка, лучи, толчок камеры; Дима сияет — глаза шире, брови вверх, улыбка во весь рот, тёплый свет на лице."""
import math

import numpy as np

import bulb
import dima
import lib
import park
import walk
import world
from lib import back_out, clamp, ease_io, smooth

T_A, T_B = 25.80, 28.20
T_ON, T_FLASH = 27.08, 27.52
GROUND_SY = 1318.0


def small_phone(Wr, d):
    """Телефон в кулаке ребром (опущен, рука качается)."""
    d = np.array(d, float) / np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    c = np.array(Wr) + d * 70 - n * 6
    pts = [tuple(c - d * 40 - n * 72), tuple(c + d * 40 - n * 72), tuple(c + d * 40 + n * 72), tuple(c - d * 40 + n * 72)]
    return lib.shape([p + (1,) for p in pts], "#2c2f3a", "", w=4.0, seed=930)


def pose(t):
    beam = smooth(T_ON, T_ON + 0.2, t)
    wow = smooth(T_FLASH - 0.05, T_FLASH + 0.12, t)
    expr = dict(lid=0.6 + 0.4 * beam, look=(0.45 - 0.2 * beam, -0.05 - 0.55 * beam), brows="up" if beam > .4 else "calm",
                mouth="grin" if wow > .5 else "smile", hair=0)
    p = walk.pose(t, expr=expr, head_ang=0.02 - 0.12 * beam, lean=0.07 - 0.03 * beam)
    p["held"] = ("behind", small_phone)
    p["held_side"] = "n"
    return p


def camera(t):
    h = walk.hip_at(t, bob=False)
    sx = 400 + 40 * ease_io(clamp((t - T_A) / (T_B - T_A)))
    s = 1.40 + 0.03 * (t - T_A)
    cx = h[0] + (540 - sx) / s
    cy = (960 - GROUND_SY) / s + 3 * math.sin(t * 2.3)
    rot = 0.35 * math.sin(t * 1.5 + 1.1)
    return cx, cy, s, rot


def frame(t):
    lib.DEFS.clear()
    cam = camera(t)
    cx, cy, s, rot = cam
    body = [park.backdrop(cx, cy, s, rot, t)]
    wb = [world.ground(cx, cy, s, t)]
    g, info = dima.draw(pose(t))
    wb.append(park.long_shadow(g, 0.0))
    wb.append(world.props_back(cx, s, t))
    gi = len(wb)
    wb.append(g)
    hd = info["head"]
    if t >= T_ON - 0.02:
        u = t - T_ON
        sc = back_out(clamp(u / 0.22), 2.2)
        lit = smooth(T_ON + 0.02, T_ON + 0.14, t) * (0.85 + 0.15 * smooth(T_FLASH, T_FLASH + .1, t))
        rays = 0.5 * smooth(T_ON + 0.08, T_ON + 0.3, t) + 0.5 * smooth(T_FLASH - 0.02, T_FLASH + 0.12, t)
        rays *= 1 + 0.35 * math.exp(-5 * max(0, t - T_FLASH)) * smooth(T_FLASH - .02, T_FLASH + .05, t)
        bob = 6 * math.sin((t - T_ON) * 7)
        bx, by = hd[0] + 6, hd[1] - 228 + bob
        r = 82 * max(sc, 0.01)
        # тёплый свет на голову и плечи
        wb.insert(gi, bulb.halo(bx, by, 82 * max(sc, .01), lit, rays))
        wb.insert(gi, world.glow(hd[0], hd[1] - 60, 330, "#ffe27a", 0.45 * lit))   # свет за героем, не поверх
        wb.append(f'<g transform="translate({bx:.1f} {by:.1f}) scale({max(sc, .01):.4f}) translate({-bx:.1f} {-by:.1f})">'
                  f'{bulb.draw(bx, by, 82, lit, rays, t, halo=False)}</g>')
        _ = r
    body.append(f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(wb)}</g>')
    body.append(park.foreground(cx, cy, s, rot, t))
    fl = 0.42 * math.exp(-9 * max(0, t - T_FLASH)) * smooth(T_FLASH - 0.03, T_FLASH, t)
    body.append(world.blink_flash(fl))
    k = 0.10 * smooth(T_FLASH - 0.04, T_FLASH + 0.08, t) * (1 - 0.4 * smooth(T_FLASH + .1, T_B, t))
    pc = world.to_screen(hd + np.array([0, -120.0]), cam)
    return lib.svg(world.push("".join(body), k / 0.85 if k else 0, pc, 1.85) if False else push_small(body, k, pc))


def push_small(body, k, pc):
    if k <= 0:
        return "".join(body)
    sc = 1 + k
    return f'<g transform="translate({pc[0]:.1f} {pc[1]:.1f}) scale({sc:.4f}) translate({-pc[0]:.1f} {-pc[1]:.1f})">{"".join(body)}</g>'
