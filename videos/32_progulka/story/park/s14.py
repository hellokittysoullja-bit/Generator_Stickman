"""s14 (23.90–26.00, клип 23.70–26.20): дневной парк, Дима в горчичном худи шагом выходит на дорожку, телефон в ближней
руке экраном к зрителю; большой палец жмёт «пуск», на «двадцать» (25.12) таймер 20:00 вспыхивает и идёт, камера
коротко наезжает на телефон и лицо."""
import math

import numpy as np

import dima
import lib
import park
import phone
import walk
import world
from lib import clamp, ease_io, ease_out, smooth

T_A, T_B = 23.70, 26.20
T_GO = phone.T_GO
GROUND_SY = 1235.0


def pose(t):
    hip = walk.hip_at(t)
    # ближняя рука держит телефон перед грудью (цель в мире от таза, чуть качается с шагом)
    ph = walk.phase(t)
    tgt = hip + np.array([132.0, -58.0 + 4 * math.sin(2 * math.pi * ph * 2)])
    arms = walk.swing_arms(t, 0.34)
    arms["n"] = ("ik", tgt, -1)
    tap = smooth(24.80, 24.98, t) * (1 - smooth(25.06, 25.22, t))
    lit = smooth(T_GO, T_GO + 0.25, t)
    expr = dict(lid=0.5 + 0.35 * lit, look=(0.55, 0.75 - 0.2 * lit), brows="calm" if lit < .5 else "up",
                mouth="smile", hair=0)
    p = walk.pose(t, arms=arms, expr=expr, head_ang=0.16 - 0.04 * lit, lean=0.06)
    p["hands"] = {"n": "fist", "f": "fist"}
    p["hand_dir"] = {"n": (0.25, -1.0)}
    p["held"] = ("front", lambda Wr, d: phone.draw(Wr, d, t, tap))
    p["held_side"] = "n"
    return p


def camera(t):
    h = walk.hip_at(t, bob=False)
    # Дима входит слева: камера отстаёт, потом едет вровень
    sx = 330 + 120 * ease_io(clamp((t - T_A) / 1.1))
    s = 1.42 + 0.03 * (t - T_A)
    cx = h[0] + (540 - sx) / s
    cy = (960 - GROUND_SY) / s
    rot = 0.4 * math.sin(t * 1.6 + .3)
    return cx, cy, s, rot


def frame(t):
    lib.DEFS.clear()
    cx, cy, s, rot = camera(t)
    body = [park.backdrop(cx, cy, s, rot, t)]
    wb = [world.ground(cx, cy, s, t)]
    g, info = dima.draw(pose(t))
    wb.append(park.long_shadow(g, 0.0))
    wb.append(world.props_back(cx, s, t))
    wb.append(g)
    body.append(f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(wb)}</g>')
    body.append(park.foreground(cx, cy, s, rot, t))
    # наезд на телефон и лицо на «двадцать» (весь кадр, чтобы фон и мир не расходились)
    k = ease_out(clamp((t - (T_GO - 0.08)) / 0.30), 3)
    k *= 1 + 0.04 * math.exp(-6 * max(0, t - T_GO - 0.22)) * smooth(T_GO + 0.14, T_GO + 0.24, t)
    pc = world.to_screen(info["n"] + np.array([0.0, -40.0]), (cx, cy, s, rot))
    return lib.svg(world.push("".join(body), k, pc, 1.85))
