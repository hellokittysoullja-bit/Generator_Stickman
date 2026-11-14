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
R02 = tread.Run(1.0, 3.8, lambda t: (0.36, 112.0), stance=0.7, lift=46.0, hx=-80.0, hip_k=0.83, bob=7.0, back=10.0)
GRIP_N, GRIP_F = (94.0, -425.0), (104.0, -452.0)


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
    lean = 0.42 + 0.36 * h
    hip_h = np.array([-118.0, -196.0]) + np.array([4 * math.sin(t * 9), 3 * math.sin(t * 7)]) * h
    # ноги волочатся: носки на ленте, дрожат от ленты
    dn = toe_drag(-236 + 6 * math.sin(t * 23), 1.05, -1.5 * abs(math.sin(t * 31)))
    df = toe_drag(-292 + 6 * math.sin(t * 19 + 1), 1.15, -1.5 * abs(math.sin(t * 27)))
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
        arms[s_] = ("ik", L(arms_t[s_], g, smooth(RAZ - 0.22, RAZ, t)))
    sh = 0.5 * math.sin(t * 2.3)
    expr = dict(lid=0.18 + 0.1 * (1 - h), look=(0.45, 0.55 + 0.2 * h), brows="worry", mouth="tongue", red=1.0, sweat=1.0, sweat_t=t,
                hair=4 * math.sin(psi * 2) * (1 - h))
    return dict(hip=hipP, lean=lean, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"},
                hand_dir={"n": (0.35, 1.0), "f": (0.35, 1.0)} if h > 0.6 else {},
                head_ang=0.12 + 0.42 * h + 0.03 * sh, hood=3 * math.sin(psi * 2), strings=(-10 + 6 * math.sin(psi), 6 * math.cos(psi)),
                expr=expr, split=True)


def frame02(t):
    bg = static_bg("bg02", None)
    u = clamp((t - 1.25) / 2.25)
    s = 1.5 + 0.1 * (0.4 * u + 0.6 * ease_io(u))
    e = t - ONE
    if e > 0:
        s *= 1 + 0.035 * math.exp(-e * 7) * math.sin(min(e * 12, math.pi))
    cx, cy = -40 + 12 * u, -205 - 8 * u
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
    return compose(back, main, Wd.tm_near_bar(), arm_n, front, (cx, cy, s, rot))


def frame(sid, t):
    return {"s02": frame02}[sid](t)
