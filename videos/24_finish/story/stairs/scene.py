"""Сцена stairs рилса 24: s01, s02, s05, s06. frame(sid, t) -> SVG 1080×1920 (t — общее время ролика).

Движение Димы — по опорам: у каждой ступни список касаний (время, точка, конец опоры). На опоре ступня стоит в мире
(не скользит; пятка поднимается, когда ноге не хватает длины, — перекат через носок), между опорами — дуга маха над
кромкой следующей ступени. Таз идёт по монотонному сплайну через точки над опорами, высота — от линии ступеней.
Ноги — двузвенная ИК, руки — от фазы ног или к цели (кубок)."""
import math
import os
import sys

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dima  # noqa: E402
import lib  # noqa: E402
import world as Wd  # noqa: E402
from lib import blob, clamp, ease_io, ease_out, f, smooth, spring  # noqa: E402

BS = dima.BS
LEG = (dima.THIGH + dima.SHIN) * BS
AHW = dima.AH * BS
TOEW, HEELW = dima.TOE * BS * 1.22, dima.HEEL * BS * 1.22

# ─── геометрия мира ───
F1 = Wd.Flight(0, 0, 12, 190, 120)               # первая лестница, ступени -14..11
F1_FIRST = -14
PX0, PY, PW = 12 * 190, -12 * 120, 3.4 * 190      # площадка: левый край, верх, ширина
F2 = Wd.Flight(PX0 + PW, PY - 150, 16, 170, 150)  # новая лестница, круче
F2_N = 16
CUP_X, CUP_SOLE = PX0 + 1.62 * 190, PY - Wd.DD / 2    # кубок на пьедестале
PED_H = 236.0
CUP_SC = 0.52
CUP_GRIP = (CUP_X, CUP_SOLE - PED_H - 80 * CUP_SC - 1)   # ножка кубка (точка хвата)
FLAG_X = PX0 + 2.55 * 190

DAY0 = 17                                         # число на ступени i: (DAY0 + i) % 30 + 1


def day_of(i):
    return (DAY0 + i) % 30 + 1


# ─── бег: касания ───
TC, ST = 0.2, 0.13


def run_plan(kind):
    """Касания обеих ступней и опорные точки таза для s01/s02 ('up1') и s06 ('up2')."""
    C = []      # (t, foot, x, sole, end)
    if kind == "up1":
        T_ARR = 1.42
        for k in range(F1_FIRST + 2, 12):
            t = T_ARR - (12 - k) * TC
            x, y = F1.contact(k)
            C.append([t, "n" if k % 2 == 0 else "f", x, y, t + ST])
        C.append([T_ARR, "n", PX0 + Wd.DX / 2 + .26 * 190, PY - Wd.DD / 2, 99.0])
        C.append([T_ARR + .19, "f", PX0 + Wd.DX / 2 + .26 * 190 + 128, PY - Wd.DD / 2, 99.0])
        hip_keys = [(c[0] + ST / 2, c[2]) for c in C[:-2]]
        x_stop = C[-2][2] + 74
        hip_keys += [(T_ARR + .07, C[-2][2] + 4), (T_ARR + .2, x_stop - 14), (T_ARR + .36, x_stop), (3.0, x_stop + 2)]
        stop_t = T_ARR + .3
    else:
        x_n0, x_f0 = PX0 + Wd.DX / 2 + .26 * 190, PX0 + Wd.DX / 2 + .26 * 190 + 128
        sole = PY - Wd.DD / 2
        C.append([-9.0, "n", x_n0, sole, 5.80])
        C.append([-9.0, "f", x_f0, sole, 5.93])
        C.append([5.98, "n", x_f0 + 170, sole, 5.98 + ST + .02])
        C.append([6.16, "f", PX0 + PW - 70, sole, 6.16 + ST])
        for j in range(F2_N):
            t = 6.34 + j * TC
            x, y = F2.contact(j)
            C.append([t, "n" if j % 2 == 0 else "f", x, y, t + ST])
        hip_keys = [(4.0, (x_n0 + x_f0) / 2 + 12), (5.80, (x_n0 + x_f0) / 2 + 14), (5.93, x_f0 + 10)]
        hip_keys += [(c[0] + ST / 2, c[2]) for c in C[2:]]
        hip_keys.append((hip_keys[-1][0] + 3, hip_keys[-1][1] + 3 / TC * 170))
        stop_t = None
    C.sort(key=lambda c: c[0])
    ts, xs = zip(*hip_keys)
    hip_x = PchipInterpolator(np.array(ts), np.array(xs))
    sup = sorted([(c[2], c[3]) for c in C], key=lambda p: p[0])
    sx = np.array([p[0] for p in sup])
    sy = np.array([p[1] for p in sup])
    return dict(C=C, hip_x=hip_x, sx=sx, sy=sy, stop_t=stop_t, kind=kind)


PLANS = {}


def plan(kind):
    if kind not in PLANS:
        PLANS[kind] = run_plan(kind)
    return PLANS[kind]


def support_y(pl, x):
    return float(np.interp(x, pl["sx"], pl["sy"]))


def run_amount(pl, t):
    """1 — бег, 0 — стоит (для амплитуд и высоты таза)."""
    if pl["kind"] == "up1":
        return 1 - smooth(pl["stop_t"] - .2, pl["stop_t"] + .15, t)
    return smooth(5.78, 6.08, t)


def hip_at(pl, t, bob=True):
    x = float(pl["hip_x"](t))
    r = run_amount(pl, t)
    hh = LEG * (0.85 * r + 0.975 * (1 - r)) + AHW
    y = support_y(pl, x) - hh
    if bob and r > 0:
        # ниже всего в середине опоры, выше — в полёте
        ph = 0.0
        best = 9.0
        for c in pl["C"]:
            dt = t - (c[0] + ST / 2)
            if abs(dt) < abs(best):
                best = dt
        ph = 2 * math.pi * best / TC
        y += 11 * r * math.cos(ph)
    return np.array([x, y])


def foot_at(pl, side, t, hip):
    """Лодыжка и угол стопы ноги side в момент t."""
    cs = [c for c in pl["C"] if c[1] == side]
    prev = None
    nxt = None
    for c in cs:
        if c[0] <= t:
            prev = c
        elif nxt is None:
            nxt = c
    if prev is None:
        prev = cs[0]
    if t <= prev[4] or nxt is None:
        return planted(prev, hip)
    # мах от отрыва prev к касанию nxt
    t0, t1 = prev[4], nxt[0]
    u = clamp((t - t0) / (t1 - t0))
    hip0 = hip_at(pl, t0)
    A0, ph0 = planted(prev, hip0)
    A1 = np.array([nxt[2], nxt[3] - AHW])
    dy = A0[1] - A1[1]
    # путь: сначала вверх-назад (пятка к ягодице), затем вперёд над кромкой, мягкая посадка
    ux = u ** 1.55 * (3 - 2 * u) / (1 + 0.0) if False else (1 - math.cos(math.pi * u ** 1.25)) / 2
    x = A0[0] + (A1[0] - A0[0]) * ux - 34 * math.sin(math.pi * clamp(u * 1.6))
    lift = 58
    uy = smooth(0, .62, u)
    y = A0[1] + (A1[1] - A0[1]) * uy - lift * math.sin(math.pi * u) ** 1.1
    # угол: носок вниз после отрыва → стопа подтянута → чуть носок вверх перед касанием → ровно
    if u < .35:
        phi = ph0 + (0.55 - ph0) * smooth(0, .35, u)
    elif u < .82:
        phi = 0.55 + (-0.22 - 0.55) * smooth(.35, .82, u)
    else:
        phi = -0.22 * (1 - smooth(.82, 1.0, u))
    return np.array([x, y]), phi


def planted(c, hip):
    """Стопа на опоре: пятка и носок на ступени; если таз далеко — перекат через носок."""
    sole = c[3]
    A = np.array([c[2], sole - AHW])
    reach = LEG * 0.985
    if np.linalg.norm(A - hip) <= reach:
        return A, 0.0
    toe = np.array([c[2] + TOEW, sole])
    lo, hi = 0.0, 1.35
    for _ in range(30):
        m = (lo + hi) / 2
        A2 = toe + dima.rot(np.array([-TOEW, -AHW]), m)
        if np.linalg.norm(A2 - hip) > reach:
            lo = m
        else:
            hi = m
    return toe + dima.rot(np.array([-TOEW, -AHW]), hi), hi


def run_pose(pl, t):
    hip = hip_at(pl, t)
    feet = {s: foot_at(pl, s, t, hip) for s in ("n", "f")}
    r = run_amount(pl, t)
    # руки: в противофазе ногам — фаза от касаний ближней ноги (назад до упора — в момент её касания)
    cn = [c[0] for c in pl["C"] if c[1] == "n"]
    tn = max([c for c in cn if c <= t], default=cn[0])
    psi = 2 * math.pi * (t - tn) / (2 * TC)
    arms = {}
    for s_, sg in (("n", 1), ("f", -1)):
        sw = -sg * math.cos(psi)              # +1 — рука впереди
        th = 0.05 + 0.92 * sw * r
        bend = 1.5 + 0.35 * max(0, sw) * r - 0.45 * max(0, -sw) * r
        arms[s_] = ("ang", th, bend)
    vy = (hip_at(pl, t, True)[1] - hip_at(pl, t - .05, True)[1]) / .05
    return dict(hip=hip, lean=0.36 * r + 0.06, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"},
                head_ang=-0.12 * r, hood=clamp(-vy * 0.05, -16, 22), strings=(clamp(-vy * .04, -30, 30) - 18 * r, clamp(vy * .05, -20, 30)),
                expr=dict(lid=0.55, look=(0.42, -0.05), brows="det", mouth="pant", hair=clamp(vy * 0.035, -16, 16)))


# ─── кубок в руке ───
def held_cup(tilt=0.0, glow=0.0):
    def fn(Wr, d):
        g = Wr + np.array([60.0, 0.0])          # ножка проходит сквозь кулак (кулак смотрит вперёд)
        return (f'<g transform="translate({g[0]:.2f} {g[1]:.2f}) rotate({tilt:.2f}) scale({1 / BS:.4f})">'
                f'{Wd.cup(CUP_SC, glow)}</g>')
    return fn


def mix_pt(a, b, u):
    return np.array(a, float) + (np.array(b, float) - np.array(a, float)) * u


def pose_s012(t):
    """s01/s02: бег вверх, остановка на площадке, хватает кубок на «повышению» (1.6) и вскидывает над головой."""
    pl = plan("up1")
    p = run_pose(pl, t)
    T_GRAB, T_UP = 1.62, 2.02
    if t < 1.36:
        return p, None
    hip = p["hip"]
    sh = hip + np.array([math.sin(p["lean"]), -math.cos(p["lean"])]) * dima.TORSO * BS
    reach = smooth(1.36, T_GRAB, t)
    up = ease_out(clamp((t - T_GRAB - .04) / (T_UP - T_GRAB - .04)), 3)
    grip = np.array(CUP_GRIP)
    # рука до хвата: запястье к ножке (кулак смотрит вперёд, ножка в 60 L от запястья)
    w_grab = grip - np.array([60 * BS, 0])
    w_over = sh + np.array([20, -236])
    # рука, бегущая → к кубку → вверх
    ang = p["arms"]["f"]
    shf = sh - np.array([math.cos(p["lean"]), math.sin(p["lean"])]) * 14 * BS
    E0 = shf + np.array([math.sin(ang[1]), math.cos(ang[1])]) * dima.UPPER * BS
    w_run = E0 + dima.rot(np.array([math.sin(ang[1]), math.cos(ang[1])]), -ang[2]) * dima.FORE * BS
    tgt = mix_pt(w_run, w_grab, ease_io(reach))
    if up > 0:
        ov = 1 + 0.06 * math.sin(math.pi * clamp((t - T_UP) / .3)) * (t > T_UP)
        tgt = mix_pt(w_grab, shf + (w_over - shf) * ov, up)
    p["arms"]["f"] = ("ik", tgt, -1)
    p["hand_dir"] = {"f": np.array([1.0, 0.0])}
    p["hands"]["f"] = ("open", smooth(T_GRAB - .1, T_GRAB, t)) if t < T_GRAB else "fist"
    p["held_side"] = "f"
    # ближняя рука — кулак «yes!» у груди после хвата
    fp = smooth(T_GRAB, T_GRAB + .25, t)
    if fp > 0:
        a = p["arms"]["n"]
        p["arms"]["n"] = ("ang", a[1] * (1 - fp) + (-0.15) * fp, a[2] * (1 - fp) + 2.25 * fp)
    p["lean"] = p["lean"] * (1 - up) - 0.10 * up + 0.12 * reach * (1 - up)
    p["head_ang"] = -0.18 * up
    if t >= T_GRAB - .02:
        p["held"] = ("behind", held_cup(-6 * (1 - up) + 4 * math.sin(t * 7) * up, glow=up))
    e = p["expr"]
    e["look"] = (0.45, 0.25) if t < T_GRAB else (0.3, -0.55 * up)
    if up > .25:
        e.update(mouth="grin", brows="up", lid=0.8)
    elif t >= T_GRAB:
        e.update(mouth="pant", brows="up", lid=0.75)
    return p, ("hand" if t >= T_GRAB - .02 else None)


def pose_s05(t):
    """s05: стоит на площадке, кубок свисает в руке; на отъезде задирает голову к новой лестнице."""
    pl = plan("up1")
    p = run_pose(pl, 3.0)
    hip = p["hip"].copy()
    breathe = math.sin(t * 2.6) * 2.5
    hip[1] += breathe
    p["hip"] = hip
    look = ease_out(clamp((t - 5.08) / .45), 3)
    p["lean"] = 0.05 - 0.16 * look
    p["arms"]["n"] = ("ang", 0.18 - 0.1 * look, 0.35)
    p["arms"]["f"] = ("ang", -0.05, 0.25 + 0.2 * look)
    p["hand_dir"] = {"n": np.array([1.0, 0.0])}
    p["held"] = ("behind", held_cup(10 + 3 * math.sin(t * 3.1), 0.0))
    p["head_ang"] = 0.16 * (1 - look) - 0.55 * look
    p["hood"] = 6 * look
    p["strings"] = (-10 * look, 0)
    p["expr"] = dict(lid=0.25 + 0.6 * look, look=(0.25 + 0.15 * look, 0.35 - 0.95 * look), brows="tired" if look < .3 else "worry",
                     mouth="flat" if look < .3 else "gape", hair=3 * look)
    return p


def pose_s06(t):
    pl = plan("up2")
    p = run_pose(pl, t)
    st = 1 - smooth(5.8, 6.0, t)
    if st > 0:
        p["expr"].update(look=(0.3, -0.7), brows="worry")
    p["expr"].update(mouth="pant", brows="det")
    return p


# ─── кубок лежит (s06) ───
def dropped_cup(t):
    x = PX0 + 1.0 * 190
    roll = 90 + 10 * math.exp(-(t - 5.8) * 2.5) * math.sin((t - 5.8) * 11)
    dx = 30 * (1 - math.exp(-(t - 5.8) * 3))
    return (f'<g transform="translate({x + dx:.2f} {CUP_SOLE - 34:.2f}) rotate({roll:.2f})">{Wd.cup(CUP_SC)}</g>')


# ─── камера ───
def cam_s01(t):
    pl = plan("up1")
    h = hip_at(pl, t, bob=False)
    hs = hip_at(pl, t + .08, bob=False)
    h = (h + hs) / 2
    u = clamp(t / 0.22)
    z = (1 / 1.42) + (1 - 1 / 1.42) * ease_out(u, 3)
    z *= 1 + 0.05 * math.sin(math.pi * clamp((t - .17) / .28)) * (t > .17)
    s = 1.72 * z
    rot = -3.4 * (1 - ease_out(clamp(t / .3), 2)) + 0.6 * math.sin(t * 3.1)
    sx, sy = 470 + 40 * (1 - z), 800
    cx = h[0] + 20 + (540 - sx) / s
    cy = h[1] - 30 + (960 - sy) / s
    return cx, cy, s, rot


def cam_s02(t):
    cx0, cy0, s0, r0 = cam_s01(min(t, 1.48))
    p, _ = pose_s012(t)
    goal = (np.array([CUP_X - 70, CUP_GRIP[1] - 150]) + np.array(p["hip"]) * 0 + np.array([0, 0]))
    u = ease_io(clamp((t - 1.42) / .9))
    s = s0 + (s0 * 1.32 - s0) * u
    tgt = np.array([PX0 + 190 * 1.0, PY - 620])
    c = mix_pt((cx0, cy0), tgt, u)
    hit = 0.035 * math.exp(-(t - 1.62) * 9) * math.sin((t - 1.62) * 40) * (t > 1.62)
    return c[0], c[1] + hit * 300, s * (1 + abs(hit)), r0 * (1 - u) + 0.8 * math.sin(t * 2.3) * u


def cam_s05(t):
    a = np.array([PX0 + 250, PY - 420])
    b = np.array([PX0 + 820, PY - 980])
    u = clamp((t - 4.72) / .5)
    e = 1 - (1 - u) ** 3.2
    ov = 0.05 * math.sin(math.pi * clamp((t - 5.05) / .4)) * (t > 5.05)
    s = 1.55 * (1 + 0.04 * clamp((t - 4.52) / .2)) * (1 - e) + 0.5 * e
    s *= 1 - ov
    c = mix_pt(a, b, ease_out(u, 2.4))
    c[1] -= 70 * smooth(5.2, 6.2, t)
    rot = -1.5 * (1 - e) + 1.2 * e * math.sin(math.pi * clamp((t - 4.72) / .9))
    return c[0], c[1], s, rot


def cam_s06(t):
    pl = plan("up2")
    h = (hip_at(pl, t, bob=False) + hip_at(pl, t + .1, bob=False)) / 2
    s = 1.12 + 0.05 * smooth(5.8, 7.8, t)
    sx, sy = 400, 960
    cx = h[0] + (540 - sx) / s
    cy = h[1] + (960 - sy) / s
    return cx, cy, s, 0.8 * math.sin(t * 2.7) - 1.2


CAMS = {"s01": cam_s01, "s02": cam_s02, "s05": cam_s05, "s06": cam_s06}


# ─── фон ───
def sky(cy, t):
    alt = clamp(-cy / 6000, 0, 1)
    g = lib.lin_grad([(0, "#20235a", 1), (0.38 + .1 * alt, "#4b3f86", 1), (0.72 + .1 * alt, "#a76a96", 1), (1.0, "#ee9a6e", 1)],
                     0, 0, 0, 1920, units="userSpaceOnUse")
    o = [f'<rect x="-200" y="-200" width="1480" height="2320" fill="url(#{g})"/>']
    rs = np.random.RandomState(5)
    for k in range(70):
        x, y = rs.uniform(0, 1080), rs.uniform(0, 900)
        y = (y - cy * 0.015) % 1100 - 60
        a = 0.5 + 0.5 * math.sin(t * rs.uniform(1.5, 3.5) + k)
        r = rs.uniform(1.2, 3.0)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#fff6e0" opacity="{(0.35 + 0.5 * a) * (1 - y / 1100):.2f}"/>')
    # тёплое сияние у горизонта
    g2 = lib.rad_grad([(0, "#ffd29a", .55), (1, "#ffd29a", 0)], 540, 2050 + cy * 0.04, 1100, 520)
    o.append(f'<rect x="-200" y="-200" width="1480" height="2320" fill="url(#{g2})"/>')
    return "".join(o)


FOG = "#c2a8cc"


def fog_band(flight, idx, rise_fn=None):
    """Туман под пролётом: облака с контуром, закрывающие низ стопок страниц."""
    o = []
    for i in idx:
        x, y, w = flight.step(i)
        rr = rise_fn(i) if rise_fn else 0
        rs = np.random.RandomState(1000 + i * 13 + int(flight.R))
        o.append(Wd.cloud(x + w * .5 + rs.uniform(-30, 30), y + flight.R * 4.15 + rr * .25, w * 2.6, flight.R * 1.05, 3000 + i * 7 + int(flight.R),
                          "#d3bfe0", "#f0b9a4", "#efe6f6", ink_w=3.4))
    return "".join(o)


def col_fade(x, y, w, R, rise=0.0):
    g = lib.lin_grad([(0, FOG, 0), (1, FOG, 1)])
    yy = y + rise + R * 2.6
    return f'<rect x="{f(x - 1)}" y="{f(yy)}" width="{f(w + Wd.DX + 2)}" height="{f(R * 2.1)}" fill="url(#{g})"/>'


def stairs1(view):
    o = []
    x0v, x1v, y0v, y1v = view
    for i in range(F1_FIRST, 12):
        x, y, w = F1.step(i)
        if x > x1v + 50 or x + w < x0v - 300 or y > y1v + 200 or y + 6 * F1.R < y0v:
            continue
        o.append(Wd.block(x, y, w, F1.R, day_of(i), 100 + i * 11 + 500))
        o.append(col_fade(x, y, w, F1.R))
    # площадка
    o.append(Wd.block(PX0, PY, PW, F1.R, day_of(12), 7000, side=True, num=True))
    o.append(col_fade(PX0, PY, PW, F1.R))
    return "".join(o)


def pedestal(t, empty=False):
    x, y = CUP_X, CUP_SOLE
    o = []
    body = [(x - 54, y, 1), (x + 54, y, 1), (x + 46, y - PED_H + 22), (x + 60, y - PED_H + 12), (x + 60, y - PED_H, 1), (x - 60, y - PED_H, 1),
            (x - 60, y - PED_H + 12), (x - 46, y - PED_H + 22)]
    inner = blob([(x + 18, y), (x + 60, y), (x + 60, y - PED_H), (x + 22, y - PED_H)], "#5d3f8c", .9)
    inner += blob(lib.rect_pts(x - 62, y - PED_H, x + 62, y - PED_H + 12), "#e0b450")
    inner += Wd.shape(Wd.star_pts(x - 4, y - PED_H * .48, 26), Wd.GOLD, w=3, seed=77)
    o.append(Wd.shape(body, "#7b58b0", inner, w=4.2, seed=78))
    return "".join(o)


def stairs2(view, rise_fn, tint=None):
    o = []
    x0v, x1v, y0v, y1v = view
    for j in range(F2_N):
        x, y, w = F2.step(j)
        rr = rise_fn(j)
        if rr > 2500 or x > x1v + 50 or x + w < x0v - 300 or y + rr > y1v + 200 or y + rr + 6 * F2.R < y0v:
            continue
        o.append(Wd.block(x, y, w, F2.R, day_of(13 + j), 9000 + j * 13, rise=rr))
        o.append(col_fade(x, y, w, F2.R, rr))
    o.append(fog_band(F2, range(F2_N), rise_fn))
    return "".join(o)


# дальние пролёты к новой цели (слой с параллаксом)
FAR_P = 0.15
# экранные координаты в кадре s06 на 7.12 (флажок «цель») → координаты слоя
FAR_REF_T = 7.12
FAR_FL_SCR = [  # (левый край первой ступени x, верх y, n, D, R, dir)
    (850, 720, 7, 72, 46, -1),
]
FAR_FLAG_SCR = (290, 400)


def _far_w(p):
    cx, cy, s, rot = cam_s06(FAR_REF_T)
    sl = 1 + (s - 1) * FAR_P
    return np.array([cx * FAR_P, cy * FAR_P]) + (np.array(p, float) - np.array([540.0, 960.0])) / sl


FAR_FLIGHTS = [tuple(_far_w((x, y))) + (n, D, R, dr) for (x, y, n, D, R, dr) in FAR_FL_SCR]
FAR_FLAG = tuple(_far_w(FAR_FLAG_SCR))


def far_layer(cam, t, rise_t, flag_pop):
    cx, cy, s, rot = cam
    sl = 1 + (s - 1) * FAR_P
    o = []
    tint = ("#8f7fb8", 0.5)
    for n_f, (x0, y0, n, D, R, dr) in enumerate(FAR_FLIGHTS):
        fl = Wd.Flight(x0, y0, n, D, R, dr)
        a = smooth(rise_t + n_f * .12, rise_t + n_f * .12 + .5, t)
        if a <= 0:
            continue
        rr = (1 - ease_out(a, 3)) * 900
        for i in (range(n) if dr > 0 else range(n - 1, -1, -1)):
            x, y, w = fl.step(i)
            o.append(Wd.block(x, y, w, R, day_of(13 + F2_N + i), 20000 + n_f * 100 + i, rise=rr, tint=tint, side=dr < 0, ink_w=2.6,
                              col_len=1.8))
        for i in range(0, n, 3):
            x, y, w = fl.step(i)
            o.append(Wd.cloud(x + w / 2, y + R * 2.9 + rr * .3, w * 3.4, R * 1.1, 21000 + n_f * 50 + i, "#b9a2d2", "#e2a59a", "#e2d6ef",
                              ink_w=2.4))
        # площадки между пролётами
    fx, fy = FAR_FLAG
    if smooth(rise_t + .3, rise_t + .8, t) > 0:
        rr = (1 - ease_out(smooth(rise_t + .3, rise_t + .8, t), 3)) * 900
        o.append(Wd.block(fx - 70, fy, 140, 46, 1, 22000, tint=tint, num=False, star=True, ink_w=2.6, col_len=2.2, rise=rr))
        o.append(Wd.cloud(fx, fy + 46 * 3.0 + rr * .3, 380, 60, 22100, "#b9a2d2", "#e2a59a", "#e2d6ef", ink_w=2.4))
    tf = lib.cam(cx * FAR_P, cy * FAR_P, sl, rot)
    back = f'<g transform="{tf}">{"".join(o)}</g>'
    o = []
    if flag_pop > 0:
        sp = clamp(spring(max(0.0, t - FLAG_T), 2.4, 6.0) if flag_pop >= 1 else flag_pop, 0, 1.3)
        glow = lib.rad_grad([(0, "#fff0b8", .85), (1, "#fff0b8", 0)], fx + 30, fy - 150, 200)
        o.append(f'<circle cx="{fx + 30:.1f}" cy="{fy - 150:.1f}" r="{200 * min(1, sp):.1f}" fill="url(#{glow})"/>')
        o.append(Wd.flag(fx - 10, fy - Wd.DD / 2 + 8, 175, t, seed=960, sc=0.9, pop=sp))
        # искры при появлении
        if t > FLAG_T:
            k = clamp((t - FLAG_T) / .6)
            for m in range(8):
                a = m * math.pi / 4 + .3
                rr = 60 + 170 * ease_out(k, 2)
                px, py = fx + 30 + math.cos(a) * rr, fy - 150 + math.sin(a) * rr
                o.append(f'<g opacity="{1 - k:.2f}">' + Wd.shape(Wd.star_pts(px, py, 16 * (1 - k * .5), m * 20), "#fff1b4", w=2.4, seed=m)
                         + "</g>")
    return back, f'<g transform="{tf}">{"".join(o)}</g>'


FLAG_T = 7.12


def view_rect(cx, cy, s):
    return (cx - 640 / s, cx + 640 / s, cy - 1060 / s, cy + 1060 / s)


def speed_lines(t, k, rot):
    """Линии скорости по краям кадра (летят вниз-влево — Дима мчится вверх-вправо)."""
    if k <= 0:
        return ""
    rs = np.random.RandomState(int(t * 30) % 997)
    o = []
    for m in range(14):
        side = m % 2
        x = rs.uniform(10, 260) if side == 0 else rs.uniform(820, 1070)
        y = rs.uniform(80, 1250)
        L = rs.uniform(90, 220) * k
        a = math.radians(-58)
        x2, y2 = x - math.cos(a) * L, y - math.sin(a) * L
        o.append(lib.line([(x, y), (x2, y2)], rs.uniform(2.5, 5), "#fff7ea", taper=.5, wmin=.05, seed=m + int(t * 30), op=.55 * k))
    return "".join(o)


def frame(sid, t):
    lib.DEFS.clear()
    cam = CAMS[sid](t)
    cx, cy, s, rot = cam
    v = view_rect(cx, cy, s)
    body = [sky(cy, t)]
    body.append(Wd.cloud_layer("far", (cx, cy), s, rot, None))
    flag_pop = 0.0
    rise_far = 99.0
    rise_fn = (lambda j: 9999)
    if sid == "s05":
        rise_far = 4.98

        def rise_fn(j):
            u = clamp((t - (4.80 + j * .05)) / .42)
            return (1 - ease_out(u, 3)) * 1100 + 260 * math.exp(-u * 4) * 0 if u < 1 else 0.0
    elif sid == "s06":
        rise_far = -9
        flag_pop = 1.0 if t >= FLAG_T else 0.0

        def rise_fn(j):
            return 0.0
    fb, ff = far_layer(cam, t, rise_far, flag_pop)
    body.append(fb)
    body.append(Wd.cloud_layer("mid", (cx, cy), s, rot, None))
    body.append(ff)
    wb = [stairs1(v)]
    wb.append(fog_band(F1, range(F1_FIRST, 13)))
    if sid in ("s05", "s06"):
        wb.append(stairs2(v, rise_fn))
    wb.append(pedestal(t))
    held = None
    if sid in ("s01", "s02"):
        p, held = pose_s012(t)
        if held is None:
            wb.append(f'<g transform="translate({CUP_GRIP[0]:.2f} {CUP_GRIP[1]:.2f})">{Wd.cup(CUP_SC, 0.35 + 0.25 * math.sin(t * 6))}</g>')
    elif sid == "s05":
        p = pose_s05(t)
    else:
        p = pose_s06(t)
        wb.append(dropped_cup(t))
    wb.append(Wd.flag(FLAG_X, PY - Wd.DD / 2, 420, t, seed=950, sc=1.0))
    if sid == "s06" and t < 6.3:
        pass
    g, _ = dima.draw(p)
    wb.append(g)
    body.append(f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(wb)}</g>')
    if sid == "s01":
        pass
    elif sid == "s06":
        pass
    return lib.svg("".join(body))
