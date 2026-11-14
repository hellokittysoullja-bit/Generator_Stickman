"""Рилс 62, группа D, s14 (22.5–24.3): комната, тёплый свет торшера; Дима в лотосе и кот рядом дышат в такт (грудь Димы и бока
кота одним ритмом), вокруг обоих одна тонкая волна-лента дыхания; «есть» (22.72) Дима мягко улыбается с закрытыми глазами,
«медитация» (23.34) кот переводит взгляд на него и щурится. Медленный наезд на обоих. Дима ≥ 50 % высоты кадра.
Люди и кот — common/people.py (B), предметы — common/props.py (A), комната — common/room.py (E); пока room.py рилса 62 нет —
стена и пол из room.py рилса 61 (без столов)."""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(1, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props  # noqa: E402
import s62d as D  # noqa: E402
from lib import clamp, ease_io, ease_out, smooth  # noqa: E402

ROOM62 = os.path.join(COMMON, "room.py")


def _load_room():
    if os.path.exists(ROOM62):
        import room
        return room, True
    p = os.path.join(STORY, "..", "..", "61_stol", "story", "common", "room.py")
    spec = importlib.util.spec_from_file_location("room61", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, False


R, IS62 = _load_room()

T_EST, T_MED = D.wt(53), D.wt(55)     # 22.72, 23.34
HIP = (430.0, 1330.0)                 # таз Димы на подушке
SC = 1.0
CATP = (884.0, 1655.0)                # кот: точка между задних лап (на полу)
CATK = 1.12


DX = -100.0                            # Дима и подушка левее центра уголка — справа место коту


def br(t):
    return D.breath(t)


def wave_loop(t, b, cx, cy, rx, ry, col="#e39a3e", w=6.0, seed=300):
    """Одна тонкая волна-лента вокруг обоих: замкнутая, волна бежит по кругу, лента дышит вместе с ними."""
    n = 220
    k = 1 + .025 * b
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        r = 1 + .022 * math.sin(9 * a - t * 2 * math.pi / D.BR_T * 1.5)
        pts.append((cx + math.cos(a) * rx * k * r, cy + math.sin(a) * ry * k * r))
    return lib.line(pts, w, col, taper=0, wmin=1, seed=seed)


def frame14(t):
    lib.dyn_begin()
    b = br(t)
    if IS62:
        rb = R.room_bg(t, "evening")
        o = [rb["bg"]]
        o.append(wave_loop(t, b, 640, 1150, 480, 590))
        o.append(R.cushion_layer(1.0 - .01 * b, dx=DX))
        hx, hy = R.seat(1.0 - .01 * b)
        hx += DX
    else:
        rb = {"front": ""}
        o = [R.wall_floor(), props.torch(975, 1470, k=1.75, on=1.0), wave_loop(t, b, 640, 1150, 480, 590),
             props.cushion(440, 1650, 1.5, sy=1.5)]
        hx, hy = 440.0, 1295.0
    # Дима: грудь поднимается на вдохе
    smile = smooth(T_EST - .05, T_EST + .35, t)
    ex = dict(people.EXPR["dima"]["soft"])
    ex["smile"] = .25 + .65 * smile
    kw = people.lotus_kw("sit", hx, hy, SC)
    fig = people.figure("dima", hx, hy - 5 * b, SC, ex, torso_k=1 + .022 * b, **kw)
    o.append(fig["svg"])
    # кот: бока дышат тем же ритмом (своё дыхание кота снято)
    own = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    tm = smooth(T_MED, T_MED + .35, t)
    sq = smooth(T_MED + .1, T_MED + .45, t)
    st = {"sy": (1 + .028 * b) / own, "sx": 1 - .008 * b, "turn": -.55 * tm, "look": (-.95 * tm, .12 * tm - .1 * (1 - tm)),
          "blink": .32 + .38 * sq, "tail": -6 + 4 * math.sin(t * .9), "tilt": -5 * tm}
    o.append(people.cat_svg(CATP[0], CATP[1], CATK, st, t))
    o.append(rb["front"])
    # камера: медленный наезд на обоих
    u = ease_io(clamp((t - 22.3) / 2.2))
    z = 1.0 + .13 * u
    lib.INK_K[0] = 1.0
    cx, cy = 610 + 10 * u, 1150 - 25 * u
    return lib.svg(f'<g transform="{lib.cam(cx, cy, z, .7 - .9 * u)}">{"".join(o)}</g>')
