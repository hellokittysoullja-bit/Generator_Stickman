"""Сцена gym рилса 36: Дима на беговой дорожке. frame(sid, t) -> SVG 1080×1920 (t — общее время ролика).

s02 (1.45–3.30) — единственный поход в зал: еле перебирает ногами, красный, мокрый, язык набок; на «один» (2.40) на
календаре штампом встаёт одна зелёная галочка; на «раз» (2.80) повисает на поручнях без сил, ноги волочатся по ленте.
s13 (21.90–24.00) — тот же зал, теперь в наушниках: встаёт на ленту, на «теперь» (22.36) кладёт телефон на пульт,
на «любимый» (23.68) палец жмёт «играть», звуковые волны.
s14 (24.00–26.20) — бежит, смеётся от подкаста, ветер от вентилятора треплет волосы; на «дорожке» (25.44) лента
ускоряется. На календаре в s13/s14 — уже много галочек (теперь ходит).

Всё в системе дорожки (world.py): верх ленты y = 0. Бег — tread.Run (стопа на опоре едет с лентой)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dimax as dima  # noqa: E402
import lib  # noqa: E402
import tread  # noqa: E402
import world as Wd  # noqa: E402
from lib import clamp, ease_io, smooth, spring  # noqa: E402,F401

ONE, RAZ = 2.40, 2.80
TEPER, LUB = 22.36, 23.68
DOR = 25.44
CHECKS = [0, 2, 3, 5, 8, 9, 11, 14, 16, 17, 19, 22, 23]   # «теперь ходит»


def L(a, b, u):
    return np.array(a, float) + (np.array(b, float) - np.array(a, float)) * u


def toe_drag(tx, phi, jit=0.0):
    toe = np.array([tx, jit])
    return toe + dima.rot(np.array([-tread.TOEW, -tread.AHW]), phi), phi


def cam(cx, cy, s, rot):
    return lib.cam(cx, cy, s, rot)


def compose(world_back, dima_main, mid, arm_n, front, camv, screen=""):
    cx, cy, s, r = camv
    lib.INK_K[0] = 1.0
    o = [f'<rect width="1080" height="1920" fill="{Wd.WALL}"/>',
         f'<g transform="{cam(cx, cy, s, r)}">{world_back}{dima_main}{mid}{arm_n}{front}{Wd.ceiling_glow()}</g>', screen, Wd.vignette()]
    return lib.svg("".join(o))


_C = {}


def static_bg(key, cal):
    if key not in _C:
        lib.DEFS.clear()
        _C[key] = Wd.wall() + Wd.window(0) + Wd.floor() + Wd.rack()
        _C[key + "_cal"] = cal
        lib.static_done()
    lib.dyn_begin()
    return _C[key]


# ═════════════════════════════ s02 ═════════════════════════════
R02 = tread.Run(1.0, 3.8, lambda t: (0.36, 112.0), stance=0.7, lift=46.0, hx=-115.0, hip_k=0.83, bob=7.0, back=10.0)
GRIP_N, GRIP_F = (172.0, -196.0), (150.0, -212.0)     # руки свесились через поручни


def pose02(t):
    R = R02
    B = R.belt(t)
    hip = R.hip(t) - np.array([B, 0])
    feet = {}
    for s_ in ("n", "f"):
        A, ph = R.foot(s_, t, R.hip(t))
        feet[s_] = (np.array([A[0] - B, A[1]]), ph)
    psi = R.phase(t)
    arms_t = {}
    for s_, sg in (("n", 1), ("f", -1)):
        sw = sg * math.sin(psi)
        arms_t[s_] = hip + np.array([46 + 34 * sw, -86 + 8 * abs(sw)])
    h = smooth(RAZ - 0.18, RAZ + 0.12, t)
    lean = 0.42 + 0.56 * h
    hip_h = np.array([-112.0, -226.0]) + np.array([4 * math.sin(t * 9), 3 * math.sin(t * 7)]) * h
    # ноги волочатся: носки на ленте, дрожат от ленты
    dn = toe_drag(-282 + 6 * math.sin(t * 23), 1.05, -1.5 * abs(math.sin(t * 31)))
    df = toe_drag(-322 + 6 * math.sin(t * 19 + 1), 1.15, -1.5 * abs(math.sin(t * 27)))
    hipP = L(hip, hip_h, h)
    # провис на руках с отскоком
    if t > RAZ:
        e = t - RAZ
        hipP = hipP + np.array([0, 10 * math.exp(-e * 6) * math.sin(e * 22)])
    for s_, dd in (("n", dn), ("f", df)):
        A0, p0 = feet[s_]
        feet[s_] = (L(A0, dd[0], h), p0 + (dd[1] - p0) * h)
    arms = {}
    for s_, g in (("n", GRIP_N), ("f", GRIP_F)):
        arms[s_] = ("ik", L(arms_t[s_], g, smooth(RAZ - 0.16, RAZ + 0.06, t)), 1 if h > 0.5 else -1)
    sh = 0.5 * math.sin(t * 2.3)
    expr = dict(lid=0.18 + 0.1 * (1 - h), look=(0.45, 0.55 + 0.2 * h), brows="worry", mouth="tongue", red=1.0, sweat=1.0, sweat_t=t,
                hair=4 * math.sin(psi * 2) * (1 - h))
    return dict(hip=hipP, lean=lean, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"},
                hand_dir={"n": (0.15, 1.0), "f": (0.15, 1.0)} if h > 0.6 else {},
                head_ang=0.12 - 0.3 * h + 0.03 * sh, hood=3 * math.sin(psi * 2), strings=(-10 + 6 * math.sin(psi), 6 * math.cos(psi)),
                expr=expr, split=True)


def frame02(t):
    bg = static_bg("bg02", None)
    u = clamp((t - 1.25) / 2.25)
    s = 1.6 + 0.1 * (0.4 * u + 0.6 * ease_io(u))
    e = t - ONE
    if e > 0:
        s *= 1 + 0.035 * math.exp(-e * 7) * math.sin(min(e * 12, math.pi))
    cx, cy = -20 + 12 * u, -185 - 8 * u
    rot = -0.6 + 0.8 * u
    e2 = t - RAZ
    if e2 > 0:
        cy += 7 * math.exp(-e2 * 8) * math.sin(e2 * 40)
        rot += 0.6 * math.exp(-e2 * 6) * math.sin(e2 * 30)
    stamp = (9, clamp((t - ONE + 0.05) / 0.6)) if t > ONE - 0.05 else None
    back = bg + Wd.calendar(stamp=stamp) + Wd.tm_back(R02.belt(t), t, screen=1.0)
    p = pose02(t)
    main, arm_n, _ = dima.draw(p)
    front = Wd.tm_front()
    # поручень — за телом: Дима лежит на нём грудью, ближняя рука свешивается поверх
    return compose(back, main, Wd.tm_near_bar(), arm_n, front, (cx, cy, s, rot))


# ═════════════════════════════ s13 / s14 ═════════════════════════════
PHONE_AT = (162.0, -486.0, -14.0, 0.78)          # телефон на подставке пульта: центр, поворот, масштаб
RELAX = {"curl": (.35, .4, .45, .5), "thumb": .5, "spread": .12}


def phone_btn():
    x, y, r, k = PHONE_AT
    a = math.radians(r)
    dx, dy = 0, 118 * k * .16
    return np.array([x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a)])


def ear_world(p, r):
    """Мировая точка ближнего наушника по позе."""
    lean, ha = p["lean"], p.get("head_ang", 0.0)
    a = lean * .5 + ha
    q = dima.rot(np.array([-108.0, 12.0]), a) * dima.BS
    return r["head"] + q


def pose13(t):
    # шаг на ленту: ближняя нога приходит сзади-сверху, таз встаёт
    u = smooth(21.68, 21.95, t)
    hip = L((-170.0, -236.0), (-108.0, -260.0), smooth(21.68, 22.1, t))
    hip = hip + np.array([0, 4 * math.sin(t * 2.2)])
    a_n = L((-300.0, -70.0), (-58.0, -tread.AHW), u)
    a_n[1] -= 70 * math.sin(math.pi * u)
    feet = {"f": (np.array([-150.0, -tread.AHW]), 0.0), "n": (a_n, 0.5 * math.sin(math.pi * u))}
    lean = 0.08 + 0.16 * smooth(22.0, 22.3, t) * (1 - smooth(22.5, 22.8, t)) + 0.14 * smooth(23.25, 23.55, t)
    btn = phone_btn()
    # ближняя рука: держит телефон у груди → кладёт на пульт (22.36) → у поручня → тычет пальцем (23.68)
    chest = np.array([-30.0, -372.0])
    place = np.array([118.0, -470.0])
    rest = np.array([-10.0, -330.0])
    d_place = np.array([0.85, -0.5])
    d_tip = np.array([0.72, -0.7])
    d_tip = d_tip / np.linalg.norm(d_tip)
    tipw = btn - d_tip * 40
    hold = np.array([tipw[0] - 26, tipw[1] + 24])
    e = t - LUB
    poke = 0.0
    if e > -0.1:
        poke = math.sin(math.pi * clamp((e + 0.1) / 0.24)) if e < 0.14 else 0.0
    a1 = smooth(21.95, TEPER - 0.02, t)
    a2 = smooth(TEPER + 0.12, TEPER + 0.5, t)
    a3 = smooth(23.2, LUB - 0.12, t)
    W = L(chest, place, a1)
    W = L(W, rest, a2)
    W = L(W, hold, a3)
    W = W + d_tip * 14 * poke
    if t < TEPER + 0.12:
        hn = {"curl": (.55, .6, .65, .7), "thumb": .7, "spread": .05, "dir": d_place}
        hd = d_place if a1 > .5 else np.array([0.6, -0.8])
    elif t < 23.2:
        hn = dict(RELAX)
        hd = None
    else:
        hn = {"curl": (0.0, 1.0, 1.0, 1.0), "thumb": .95, "spread": .02, "bend": .02}
        hd = d_tip
    arms = {"n": ("ik", W), "f": ("ang", 0.12 + 0.04 * math.sin(t * 1.7), 0.35)}
    smile = t > LUB
    expr = dict(lid=0.55 + 0.25 * smile, look=(0.5, 0.35 if t < 22.5 or t > 23.1 else 0.1), brows="up" if smile else "calm",
                mouth="grin" if smile else "smile", phones=True, hair=3 * math.sin(t * 3))
    p = dict(hip=hip, lean=lean, feet=feet, arms=arms, hands={"n": hn, "f": dict(RELAX)},
             head_ang=0.12 - 0.12 * smooth(22.5, 22.9, t) + 0.1 * smooth(23.15, 23.45, t), hood=-6 * math.sin(math.pi * u),
             strings=(4 * math.sin(t * 2), 0), expr=expr, split=True)
    if hd is not None:
        p["hand_dir"] = {"n": hd}
    return p, W


def phone13(t, W):
    x, y, r, k = PHONE_AT
    a1 = smooth(21.95, TEPER - 0.02, t)
    e = t - LUB
    play = clamp((e + 0.02) / 0.12) if e > -0.02 else 0.0
    press = math.sin(math.pi * clamp((e + 0.06) / 0.2)) if -0.06 < e < 0.14 else 0.0
    if t < TEPER:
        # в руке: лежит в ладони, летит к подставке
        hx, hy = W[0] + 40, W[1] - 26
        px, py = hx + (x - hx) * smooth(.7, 1, a1), hy + (y - hy) * smooth(.7, 1, a1)
        rot = -40 + 24 * a1
        return Wd.phone(px, py, k, rot)
    eb = t - TEPER
    bounce = -10 * math.exp(-eb * 10) * abs(math.sin(eb * 26))
    return Wd.phone(x, y + bounce, k, r, play=play, press=press, t=t, waves=clamp(e / 0.25) if e > 0 else 0)


def frame13(t):
    bg = static_bg("bg13", None)
    u = clamp((t - 21.7) / 2.5)
    s = 1.5 + 0.06 * u
    cx, cy = -30 + 10 * u, -200
    rot = 0.5 - 0.6 * u
    z = smooth(23.0, 23.55, t)
    s = s + (2.35 - s) * z
    cx = cx + (70 - cx) * z
    cy = cy + (-470 - cy) * z
    e = t - LUB
    if e > 0:
        s *= 1 + 0.04 * math.exp(-e * 7) * math.sin(min(e * 12, math.pi))
    e0 = t - TEPER
    if e0 > 0:
        s *= 1 + 0.02 * math.exp(-e0 * 8) * math.sin(min(e0 * 12, math.pi))
    back = bg + Wd.calendar(checks=CHECKS) + Wd.fan(t, 0) + Wd.tm_back(0.0, t, screen=0.3 + 0.7 * clamp((t - LUB) / .3))
    p, W = pose13(t)
    main, arm_n, r = dima.draw(p)
    mid = Wd.tm_near_bar() + phone13(t, W)
    if t > LUB:
        ew = ear_world(p, r)
        mid += Wd.ear_waves(ew[0] - 14, ew[1], t, .9, clamp((t - LUB) / .3))
    return compose(back, main, mid, arm_n, Wd.tm_front(), (cx, cy, s, rot))


R14 = tread.Run(23.5, 26.7, lambda t: (0.21 - 0.035 * smooth(DOR - 0.12, DOR + 0.2, t), 188 + 50 * smooth(DOR - 0.12, DOR + 0.2, t)),
                hx=-110.0)


def pose14(t):
    R = R14
    B = R.belt(t)
    hip = R.hip(t) - np.array([B, 0])
    feet = {}
    for s_ in ("n", "f"):
        A, ph = R.foot(s_, t, R.hip(t))
        feet[s_] = (np.array([A[0] - B, A[1]]), ph)
    psi = R.phase(t)
    arms = {}
    for s_, sg in (("n", 1), ("f", -1)):
        sw = -sg * math.cos(psi)
        arms[s_] = ("ang", 0.08 + 0.85 * sw, 1.45 + 0.35 * max(0, sw) - 0.4 * max(0, -sw))
    vy = (R.hip(t)[1] - R.hip(t - .05)[1]) / .05
    sp = smooth(DOR - 0.1, DOR + 0.3, t)
    wind = 0.55 + 0.35 * sp + 0.18 * math.sin(t * 8.3) + 0.1 * math.sin(t * 13)
    laugh = 0.5 + 0.5 * math.sin(t * 9) > 0.35
    expr = dict(lid=0.5, look=(0.45, 0.0), brows="up", mouth="laugh" if laugh else "grin", phones=True, hair=clamp(vy * 0.03, -14, 14),
                wind=wind)
    return dict(hip=hip, lean=0.22 + 0.06 * sp, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"},
                head_ang=-0.08 + 0.05 * math.sin(t * 9), hood=clamp(-vy * 0.05, -16, 22) - 8 * wind,
                strings=(clamp(-vy * .04, -30, 30) - 30 * wind, clamp(vy * .05, -20, 30)), expr=expr, split=True)


def frame14(t):
    bg = static_bg("bg14", None)
    u = clamp((t - 23.8) / 2.6)
    s = 1.45 + 0.05 * ease_io(u)
    cx, cy = -40 + 110 * (0.3 * u + 0.7 * ease_io(u)), -200 + 6 * math.sin(t * 2)
    rot = -0.6 + 1.0 * u
    e = t - DOR
    if e > 0:
        s *= 1 + 0.035 * math.exp(-e * 6) * math.sin(min(e * 12, math.pi))
        cx += 6 * math.exp(-e * 6) * math.sin(e * 40)
    sp = smooth(DOR - 0.1, DOR + 0.3, t)
    back = bg + Wd.calendar(checks=CHECKS) + Wd.fan(t, 1) + Wd.tm_back(R14.belt(t), t, screen=1.0)
    p = pose14(t)
    main, arm_n, r = dima.draw(p)
    x, y, rr, k = PHONE_AT
    mid = Wd.tm_near_bar() + Wd.phone(x, y, k, rr, play=1, t=t, waves=1)
    ew = ear_world(p, r)
    mid += Wd.ear_waves(ew[0] - 14, ew[1], t, .9) + Wd.notes(ew[0] - 30, ew[1] - 30, t, .9)
    back += Wd.wind(t, 0.8 + 0.4 * sp, 360, -556)
    front = Wd.tm_front()
    if e > 0:
        # скоростные чёрточки у ленты после ускорения
        for i in range(4):
            ph = (t * 3 + i * .25) % 1
            yy = -10 - i * 7
            front += lib.line([(160 - ph * 400, yy), (100 - ph * 400, yy)], 3, "#ffffff", taper=.6, seed=3600 + i,
                              op=.7 * sp * math.sin(math.pi * ph))
    return compose(back, main, mid, arm_n, front, (cx, cy, s, rot))


def frame(sid, t):
    return {"s02": frame02, "s13": frame13, "s14": frame14}[sid](t)
