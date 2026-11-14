"""s06 (7.55–10.10, клип 7.35–10.30): прихожая. Дима с сумкой на плече перед закрытой дверью. «Силой воли»
(7.36–8.00): кулаки сжаты, зажмурился, покраснел, дрожит от натуги, капля пота; «ходить» (8.16): один шаг к двери,
рука тянется к ручке и дрожит, не дотягивается; «получается» (9.20): сдувается — плечи вниз, лбом в дверь и медленно
сползает по ней на корточки. Камера — медленный наезд, мелкая тряска на натуге, к концу опускается за ним."""
import math

import numpy as np

import dima
import hall
import hero
import lib
from lib import clamp, ease_in, ease_io, smooth

T_A, T_B = 7.35, 10.30
T_STEP, T_DEFL = 8.16, 9.20
DOOR_X = hall.DOOR[0]


def strain_k(t):
    return smooth(7.30, 7.45, t) * (1 - smooth(8.05, 8.25, t))


def slide_u(t):
    return ease_in(clamp((t - (T_DEFL + 0.30)) / 0.75), 1.4)


def base_pose(t, lean):
    sk = strain_k(t)
    st = ease_io((t - T_STEP + 0.06) / 0.30)
    un = clamp((t - T_STEP + 0.06) / 0.24)
    nx = 152 + 62 * ease_io(un)
    ny = -hero.SOLE - 22 * math.sin(math.pi * un)
    uf = clamp((t - T_STEP + 0.04) / 0.26)
    fx = 92 + 52 * ease_io(uf)
    fy = -hero.SOLE - 16 * math.sin(math.pi * uf)
    hx = 118 + 50 * st
    sl = slide_u(t)
    defl = smooth(T_DEFL - 0.05, T_DEFL + 0.25, t)
    jit = sk * 2.6 * math.sin(t * 2 * math.pi * 17) + 1.6 * sk * math.sin(t * 2 * math.pi * 23 + 1)
    tremble2 = smooth(8.45, 8.7, t) * (1 - defl) * 1.6 * math.sin(t * 2 * math.pi * 14)
    hip_y = -(hero.SOLE + hero.LEG * (0.985 - 0.035 * defl)) - 10 * sk
    hip = np.array([hx - 50 * sl + jit, hip_y + (-(hero.SOLE + 92) - hip_y) * sl])
    eyes_open = sk < 0.5
    expr = dict(lid=(0.45 if t < T_DEFL else 0.25 - 0.1 * defl), look=(0.55, 0.05 + 0.3 * defl), brows="det" if t < T_DEFL else "worry",
                mouth="strain" if sk > .5 else ("flat" if t < T_DEFL else "tired"), shut=0.0 if eyes_open else 1.0, flush=max(sk, 0.6 * smooth(8.45, 8.8, t) * (1 - defl)),
                hair=8 * defl * math.exp(-3 * max(0, t - T_DEFL)) + 2 * sk * math.sin(t * 90))
    p = dict(hip=hip, lean=lean, feet={"f": (np.array([fx, fy]), 0.18 * math.sin(math.pi * uf)), "n": (np.array([nx, ny]), 0.2 * math.sin(math.pi * un))},
             hands={"n": "fist", "f": "fist"}, head_ang=0.03 * sk * math.sin(t * 70) + 0.25 * defl * (1 - sl * .4), hood=0, strings=(0, 0), expr=expr)
    shw = hip + np.array([math.sin(lean), -math.cos(lean)]) * 176
    # руки: кулаки у пояса на натуге → после шага ближняя тянется к ручке и дрожит → висят
    fist_n = hip + np.array([70.0, -40.0 - 30 * sk])
    reach = smooth(8.45, 8.95, t) * (1 - defl)
    knob = np.array(hall.KNOB) + np.array([-70.0, 4.0])
    tn = fist_n + (knob - fist_n) * reach * 0.85 + np.array([0, tremble2 * 2])
    hang_n = shw + np.array([30.0 + 40 * sl, 200.0 - 40 * sl])
    tn = tn + (hang_n - tn) * defl
    tf = hip + np.array([10.0, -50.0 - 20 * sk]) + (shw + np.array([0.0, 200.0]) - hip - np.array([10.0, -50.0])) * defl
    p["arms"] = {"n": ("ik", tn, -1), "f": ("ik", tf, -1)}
    if reach > 0.3:
        p["hands"] = {"n": ("open", 0.25), "f": "fist"}
        p["hand_dir"] = {"n": (1.0, 0.1)}
    if defl > 0.4:
        p["hands"] = {"n": ("open", 0.5), "f": ("open", 0.5)}
        p["hand_dir"] = {"n": (0.25, 1.0), "f": (0.25, 1.0)}
    p["over_torso"] = hero.bag_on_shoulder(6 * math.sin(math.pi * st) + 10 * sl, rot_extra=-14 * sl)
    return p


def pose(t):
    sk = strain_k(t)
    defl = smooth(T_DEFL - 0.05, T_DEFL + 0.30, t)
    lean0 = 0.04 + 0.05 * sk
    if defl <= 0:
        return base_pose(t, lean0)
    # лбом к двери: подбираем наклон, чтобы лоб касался двери (с перехода)
    target = DOOR_X - 50
    lo, hi = 0.0, 1.2
    for _ in range(14):
        m = (lo + hi) / 2
        hd = base_pose(t, m)["hip"] + (dima.draw(base_pose(t, m))[1]["head"] - base_pose(t, m)["hip"])
        if hd[0] < target:
            lo = m
        else:
            hi = m
    lean = lean0 + (lo - lean0) * defl
    return base_pose(t, lean)


def camera(t):
    u = (t - T_A) / (T_B - T_A)
    sk = strain_k(t)
    sl = slide_u(t)
    s = 1.62 + 0.16 * ease_io(u)
    cx = 210 + 30 * u + sk * 3.5 * math.sin(t * 2 * math.pi * 13)
    cy = -430 + 90 * sl + sk * 3.5 * math.sin(t * 2 * math.pi * 11 + 2)
    return cx, cy, s, sk * 0.5 * math.sin(t * 2 * math.pi * 9)


def frame(t):
    lib.DEFS.clear()
    dima.set_palette(dima.HOODIE)
    p = pose(t)
    g, info = dima.draw(p)
    hd = info["head"]
    mid = f'<ellipse cx="{p["hip"][0] + 30:.1f}" cy="4" rx="150" ry="18" fill="#3a2418" opacity=".28"/>' + g
    fg = []
    # капля пота: появляется на натуге, стекает по виску
    a = smooth(7.45, 7.55, t) * (1 - smooth(9.0, 9.2, t))
    if a > 0:
        u = clamp((t - 7.5) / 1.4)
        fg.append(hero.sweat(hd[0] + 58, hd[1] - 12 + 70 * ease_in(u), k=1.15, op=a))
    sk = strain_k(t)
    if sk > 0.2:                        # штрихи натуги у головы
        for j, (dx, dy, ang) in enumerate([(-80, -90, -140), (70, -100, -40), (-90, -20, 180)]):
            r0 = 72 + 10 * math.sin(t * 40 + j)
            aa = math.radians(ang)
            x0, y0 = hd[0] + math.cos(aa) * r0, hd[1] + math.sin(aa) * r0
            fg.append(hero.line([(x0, y0), (x0 + math.cos(aa) * 26, y0 + math.sin(aa) * 26)], 4.2, hero.INK, seed=3100 + j, op=sk))
    defl = smooth(T_DEFL - 0.05, T_DEFL + 0.3, t)
    if defl > 0 and t < T_DEFL + 0.8:   # выдох-облачко
        u = clamp((t - T_DEFL) / 0.6)
        op = math.sin(math.pi * u) * .8
        fg.append(lib.blob(lib.ellipse_pts(hd[0] + 70 + 30 * u, hd[1] + 40 + 10 * u, 16 + 22 * u, 10 + 12 * u, 12), "#ffffff", op))
    return hall.frame(t, cam=camera(t), mid=mid, fg="".join(fg))
