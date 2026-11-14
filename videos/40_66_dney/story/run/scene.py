"""Сцена run рилса 40 «66 дней» (копия run рилса 26 с правками). Планы:
s01 (0–1.5) хук: утро, Дима бежит бодро, влёт камеры с кадра 0; на «девять» (0.96) над ним вспыхивает бейдж «9».
s15 (28.6–30.3): утро, Дима снова бежит; на «бежит» (29.2) ускоряется (шаг чаще и длиннее, наклон сильнее).
s17 (32.4–34.6): закат; на «кот» (33.52) сзади вбегает кот галопом, огонёк на хвосте сыплет искрами, на дорожке
     мелом «66» и финишная черта.
Мир — в «мировых» единицах, земля дорожки y = 0, x растёт вправо. Камера едет за тазом Димы. Всё, что стоит на
дорожке, — в слое 1.0 (ступня на опоре стоит в мире и не скользит); дальние слои — параллакс.
frame(t, sid) -> SVG 1080×1920 (t — общее время ролика). configure(sid) — до первого кадра."""
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
from lib import blob, clamp, ease_io, ease_out, ellipse_pts, f, line, shape, smooth  # noqa: E402

BS = dima.BS
LEG = (dima.THIGH + dima.SHIN) * BS
AHW = dima.AH * BS
TOEW = dima.TOE * BS * 1.22

# ─── планы ───
CONF = {
    "s01": dict(a=0.0, b=1.7, x0=400.0, mood="morning", acc=None, cat=None, badge=0.96, hook=True),
    "s15": dict(a=28.4, b=30.5, x0=900.0, mood="morning", acc=29.2, cat=None, badge=None, hook=False),
    "s17": dict(a=32.2, b=34.8, x0=400.0, mood="sunset", acc=None, cat=33.52, badge=None, hook=False),
}
C = dict(CONF["s01"])
SID = ["s01"]

TC0, ST0, STEP0 = 0.205, 0.125, 196.0      # шаг (с), опора (с), длина шага (мир)
TC1, STEP1 = 0.168, 226.0                  # после ускорения
V = STEP0 / TC0
PL = {}


def _cad(t):
    """Темп в момент t: (длительность шага, длина шага); ускорение за 0.35 с от слова."""
    if C["acc"] is None:
        return TC0, STEP0
    k = smooth(C["acc"] - 0.05, C["acc"] + 0.30, t)
    return TC0 + (TC1 - TC0) * k, STEP0 + (STEP1 - STEP0) * k


def _plan():
    T0 = C["a"]
    Cn = []
    # назад от T0 — ровный темп
    t, x = T0, C["x0"]
    back = []
    for k in range(1, 14):
        back.append([T0 - k * TC0, "n" if k % 2 == 0 else "f", C["x0"] - k * STEP0, 0.0, T0 - k * TC0 + ST0, TC0])
    Cn.extend(back[::-1])
    k = 0
    while t < C["b"] + 2.0:
        tc, st = _cad(t)
        Cn.append([t, "n" if k % 2 == 0 else "f", x, 0.0, t + ST0 * tc / TC0, tc])
        t += tc
        x += st
        k += 1
    hip_keys = [((c[0] + c[4]) / 2, c[2] + 6) for c in Cn]
    ts, xs = zip(*hip_keys)
    PL.clear()
    PL.update(C=Cn, hip_x=PchipInterpolator(np.array(ts), np.array(xs)))


def configure(sid):
    C.clear()
    C.update(CONF[sid])
    SID[0] = sid
    park.MOOD = C["mood"]
    if C["cat"]:
        dt = C["cat"] - 31.44
        Cat.T_IN = 31.44 + dt
        Cat.T_SETTLE = 32.12 + dt
        Cat.T_LOOK = (31.75 + dt, 32.05 + dt)
        Cat.T_BLINK = 32.42 + dt
        Cat._grid.clear()
    _plan()


configure("s01")


def hip_at(t, bob=True):
    x = float(PL["hip_x"](t))
    y = -(LEG * 0.86 + AHW)
    if bob:
        best, tc = 9.0, TC0
        for c in PL["C"]:
            dt = t - (c[0] + c[4]) / 2
            if abs(dt) < abs(best):
                best, tc = dt, c[5]
        y += 12 * math.cos(2 * math.pi * best / tc)
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
    lift = 118 * (1 + 0.25 * (TC0 - prev[5]) / (TC0 - TC1))
    ux = (1 - math.cos(math.pi * u ** 1.3)) / 2
    x = A0[0] + (A1[0] - A0[0]) * ux - 30 * math.sin(math.pi * clamp(u * 1.5))
    y = A0[1] + (A1[1] - A0[1]) * u - lift * math.sin(math.pi * clamp(u * 1.08)) ** 1.3
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
    cn = [c for c in PL["C"] if c[1] == "n"]
    prev = max([c for c in cn if c[0] <= t], key=lambda c: c[0], default=cn[0])
    psi = 2 * math.pi * (t - prev[0]) / (2 * prev[5])
    acc = smooth(C["acc"] - 0.05, C["acc"] + 0.3, t) if C["acc"] else 0.0
    arms = {}
    for s_, sg in (("n", 1), ("f", -1)):
        sw = -sg * math.cos(psi)
        amp = 0.85 + 0.25 * acc
        arms[s_] = ("ang", 0.08 + amp * sw, 1.45 + 0.35 * max(0, sw) - 0.4 * max(0, -sw))
    vy = (hip_at(t)[1] - hip_at(t - .05)[1]) / .05
    k = smooth(C["cat"] + 0.18, C["cat"] + 0.48, t) if C["cat"] else 0.0
    look = (0.42 - 0.8 * k, -0.05 + 0.5 * k)
    lid = 0.72 + 0.1 * k
    brows = "up"
    if C["badge"]:
        # на «девять» глаза шире — гордость
        lid = 0.72 + 0.2 * smooth(C["badge"] - 0.05, C["badge"] + 0.15, t)
    return dict(hip=hip, lean=0.24 + 0.08 * acc, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"},
                head_ang=-0.06 + 0.10 * k - 0.03 * acc, hood=clamp(-vy * 0.05, -16, 22),
                strings=(clamp(-vy * .04, -30, 30) - 18, clamp(vy * .05, -20, 30)),
                expr=dict(lid=lid, look=look, brows=brows, mouth="grin", hair=clamp(vy * 0.035, -16, 16)))


# ─── камера ───
S0 = 1.50
DIMA_SX = 400.0          # экранный x таза
GROUND_SY = 1236.0       # экранный y земли (подошвы Димы)


def camera(t):
    h = (hip_at(t, bob=False) + hip_at(t + .1, bob=False)) / 2
    z = 1.0 + 0.045 * ease_io(clamp((t - C["a"]) / (C["b"] - C["a"])))
    s = S0 * z
    sx = DIMA_SX
    if C["cat"]:
        sx -= 30 * smooth(C["cat"] + 0.06, C["cat"] + 0.76, t)           # дать место коту справа
    if C["acc"]:
        sx += 50 * smooth(C["acc"], C["acc"] + 0.5, t)                    # ускорился — чуть обгоняет камеру
    cx = h[0] + (540 - sx) / s
    cy = (960 - GROUND_SY) / s + 4 * math.sin(t * 2.1)
    rot = 0.5 * math.sin(t * 1.7 + .4)
    return cx, cy, s, rot


def hook(t):
    """Влёт хука s01 поверх камеры: масштаб 1/(1+0.4) → 1 за 0.22 с с перелётом ~5 % и отскоком, поворот −3° → 0
    с лёгким перелётом. Возвращает (масштаб, поворот, сдвиг y)."""
    T = 0.22
    if t < T:
        u = t / T
        e = 1 - (1 - u) ** 2.2
        z = 1 / 1.4 + (1.05 - 1 / 1.4) * e
        r = -3.0 * (1 - e) + 0.6 * e
    else:
        d = t - T
        z = 1 + 0.05 * math.exp(-9 * d) * math.cos(2 * math.pi * 2.6 * d)
        r = 0.6 * math.exp(-8 * d) * math.cos(2 * math.pi * 2.0 * d)
    return z, r


def badge(t):
    """Бейдж «9» над Димой: на слове вспыхивает (пружина), лучи-вспышка, потом мягко покачивается."""
    tb = C["badge"]
    if t < tb - 0.02:
        return ""
    d = t - tb
    sc = lib.spring(d + 0.02, freq=2.6, damp=6.5) if d < 2 else 1.0
    sc = max(0.0, sc)
    x, y = 770.0, 330.0 + 4 * math.sin(t * 5)
    rot = -8 * math.exp(-5 * d) * math.cos(14 * d) + 4
    o = []
    # вспышка лучей
    if d < 0.45:
        u = d / 0.45
        for k in range(12):
            a = k * math.pi / 6 + 0.2
            r0, r1 = 120 + 160 * u, 170 + 230 * u
            wdt = 14 * (1 - u)
            p0 = (x + r0 * math.cos(a), y + r0 * math.sin(a))
            p1 = (x + r1 * math.cos(a), y + r1 * math.sin(a))
            o.append(line([p0, p1], wdt + 2, "#ffd84a", taper=.9, wmin=.1, seed=50 + k))
    body = []
    star = []
    for k in range(24):
        a = k * math.pi / 12
        rr = 128 if k % 2 == 0 else 112
        star.append((rr * math.cos(a), rr * math.sin(a)))
    body.append(blob([(p[0] + 8, p[1] + 10) for p in star], "#3a2a40", .25))
    body.append(shape(star, "#ff7a2e", blob(ellipse_pts(14, 14, 100, 100, 24), "#e85a1e", .9) +
                      blob(ellipse_pts(-40, -46, 40, 20, 12, rot=-35), "#ffb27a", .9), w=6, seed=60))
    body.append(shape(ellipse_pts(0, 0, 92, 92, 28), "#fff6e2", blob(ellipse_pts(10, 12, 80, 80, 24), "#f2e2c2", .9), w=4.4, seed=61))
    body.append(f'<text x="0" y="50" text-anchor="middle" font-family="IDB" font-weight="900" font-size="150" fill="#d8322c" '
                f'stroke="#1c1622" stroke-width="7" paint-order="stroke">9</text>')
    o.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sc:.4f})">{"".join(body)}</g>')
    return "".join(o)


def leaves(t):
    """Листья летят по ветру через кадр (экран)."""
    o = []
    rs = np.random.RandomState(7)
    for k in range(9):
        x0, y0 = rs.uniform(-100, 1300), rs.uniform(-300, 1100)
        sp = rs.uniform(260, 420)
        x = (x0 - sp * t) % 1500 - 200
        y = y0 + 140 * ((t * 0.5 + k * 0.37) % 3) + 30 * math.sin(t * 3 + k)
        if y > 1250:
            continue
        r = rs.uniform(0, 360) + 260 * t * (1 if k % 2 else -1)
        sc = rs.uniform(0.8, 1.3)
        col = ["#e0a23a", "#d9682e", "#9cc76a", "#c9a23a"][k % 4]
        pts = [(-20 * sc, 0, 1), (-6 * sc, -10 * sc), (20 * sc, 0, 1), (-6 * sc, 10 * sc)]
        o.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(r)}) scale(1 {f(0.5 + 0.5 * abs(math.sin(t * 6 + k)))})">'
                 f'{shape(pts, col, line([(-18 * sc, 0), (18 * sc, 0)], 2, "#8a5a2a", seed=80 + k, op=.7), w=2.6, seed=70 + k)}</g>')
    return "".join(o)


def chalk66(cx, s):
    """s17: финишная черта мелом поперёк дорожки и «66» мелом на дорожке (мир, впереди по ходу)."""
    x0 = C["x0"] + 2260.0
    o = []
    x0v, x1v = park.view(cx, s)
    if not (x0v - 400 < x0 < x1v + 400):
        return ""
    # черта: шашечки
    for j in range(6):
        y0 = park.PATH_Y0 + j * (park.PATH_Y1 - park.PATH_Y0) / 6
        y1 = y0 + (park.PATH_Y1 - park.PATH_Y0) / 6
        for i in range(2):
            if (i + j) % 2 == 0:
                o.append(blob([(x0 + i * 26 + (y0 + 72) * .25, y0), (x0 + (i + 1) * 26 + (y0 + 72) * .25, y0),
                               (x0 + (i + 1) * 26 + (y1 + 72) * .25, y1), (x0 + i * 26 + (y1 + 72) * .25, y1)], "#fbf6ea", .9))
    o.append(f'<g transform="translate({f(x0 - 330)} {f(park.PATH_Y1 - 26)}) skewX(-24) scale(1 .62)">'
             f'<text x="0" y="0" font-family="IDB" font-weight="900" font-size="170" fill="#fbf6ea" opacity=".85">66</text></g>')
    return "".join(o)


def frame(t, sid=None):
    if sid and sid != SID[0]:
        configure(sid)
    lib.DEFS.clear()
    cx, cy, s, rot = camera(t)
    body = []
    body.append(park.backdrop(cx, cy, s, rot, t))
    wb = [park.ground(cx, cy, s, t)]
    if SID[0] == "s17":
        wb.append(chalk66(cx, s))
    p = dima_pose(t)
    g, _ = dima.draw(p)
    cs = Cat.state(t, hip_at(t, bob=False)[0], V) if (C["cat"] and t >= C["cat"] - 0.05) else None
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
    if C["mood"] == "sunset":
        body.append(park.sunset_grade())
    else:
        body.append(leaves(t))
    if C["badge"]:
        body.append(badge(t))
    out = "".join(body)
    if C["hook"]:
        z, r = hook(t)
        out = f'<g transform="translate(540 960) rotate({r:.3f}) scale({z:.5f}) translate(-540 -960)">{out}</g>'
        out = f'<rect x="0" y="0" width="1080" height="1920" fill="#bfdcea"/>' + out
    return lib.svg(out)
