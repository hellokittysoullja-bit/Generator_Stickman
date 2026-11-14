"""Рилс 63 «кофе», группа D: ночь и кофе литрами.
s09 (17.4–19.55): ночная комната — Дима за столом с лампой, за ним пустая кровать (s63d_room.py).
s10 (19.55–21.5): «вместо» (19.59) подушка выскакивает и с хлопком становится кружкой, «сна» (20.17) кружки пружиной, «литрами»
                  (20.64) кофейник льёт бесконечной дугой, кружки башней вокруг Димы, гора качается, глаза-блюдца.
s11 (21.5–23.6):  спальня сверху, бессонница (s63d_bed.py).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Букв и цифр нет.
Дима и кот — common/people.py, предметы — common/props.py (пока нет — props рилса 62)."""
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(1, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
from lib import (INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, shape, smooth)  # noqa: E402,F401


def _load(name, fallback_reel):
    if os.path.exists(os.path.join(COMMON, name + ".py")):
        return importlib.import_module(name), True
    p = os.path.join(STORY, "..", "..", fallback_reel, "story", "common", name + ".py")
    spec = importlib.util.spec_from_file_location(name + "_fb", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, False


props, PROPS63 = _load("props", "62_meditaciya")

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


T_DRUGOE, T_DELO, T_PIT, T_KOFE = wt(45), wt(46), wt(48), wt(49)          # 17.44 18.30 18.96 19.25
T_VMESTO, T_SNA, T_LITR = wt(50), wt(51), wt(53)                          # 19.59 20.17 20.64
T_TOGDA, T_MESH, T_SPAT = wt(54), wt(56), wt(57)                          # 21.56 22.46 22.88


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def lerp(a, b, u):
    return a + (b - a) * u


def G(inner, x, y, sx=1.0, sy=None, rot=0.0):
    sy = sx if sy is None else sy
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.3f}) scale({sx:.4f} {sy:.4f})">{inner}</g>'


def mug(x, y, k, rot=0.0, col="red", t=0.0, steam=0.6, seed=0, handle=1):
    """Кружка кофе горы: k — в масштабе старой кружки 66×78 (common props.coffee_mug 110×130)."""
    inner = props.coffee_mug(0, 0, k=k * .6, rot=0, col=col, fill=1.0, steam=steam, t=t, seed=seed)
    return G(inner, x, y, handle, 1, rot)


MUGC = ("red", "white", "blue", "yellow", "green", "white")


def night_paper(seed=3):
    o = ['<rect x="-1400" y="-1400" width="3900" height="4800" fill="#1f2550"/>']
    g = lib.rad_grad([(0, "#2c3570", 1), (.7, "#222a5a", 1), (1, "#181d42", 1)], 540, 760, 1100, 1300)
    o.append(f'<rect x="-1400" y="-1400" width="3900" height="4800" fill="url(#{g})"/>')
    rs = np.random.RandomState(seed)
    for k in range(110):
        x, y = rs.uniform(-600, 1680), rs.uniform(-600, 1300)
        a = rs.uniform(0, 3.14)
        L = rs.uniform(10, 24)
        o.append(line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], 2.4, "#2a3166" if k % 2 else "#1a1f47", taper=.5, wmin=.3, seed=k))
    for (x, y, r) in ((140, 260, 16), (930, 170, 12), (330, 120, 10), (760, 330, 9), (1010, 610, 13), (60, 700, 10), (620, 90, 8)):
        o.append(props.star4(x, y, r, 1.0))
    o.append(props.moon(200, 470, 46, halo=.35))
    return "".join(o)


# ═════════════════════════════ s10: кофе литрами ═════════════════════════════
TABLE_Y = 1420.0
MK = 1.95                    # масштаб кружек горы
HIP = (560.0, 1600.0)
SC10 = 1.5


def pile_slots():
    """Места горы кружек: (x, y_дна, время появления, цвет, поворот, ручка, слой-башня). Строится от низа вверх."""
    S = []
    # ряд на столе — выскакивают пружиной на «сна»
    row0 = [(110, 0), (250, 1), (390, 2), (690, 3), (830, 4), (970, 5), (540, 6)]
    for i, (x, j) in enumerate(row0):
        tt = T_SNA + .05 * (j % 4) if j < 4 else T_LITR + .02 + .05 * (j - 4)
        S.append((x, TABLE_Y, tt, MUGC[j % 6], (-1) ** j * 3, 1 if j % 2 else -1, "c"))
    h = 78 * MK - 6            # кружка на кружке
    rows = [
        (TABLE_Y - h, [180, 320, 460, 620, 760, 900], "c"),
        (TABLE_Y - 2 * h, [250, 400, 690, 840], "c"),
        (TABLE_Y - 3 * h, [140, 280], "l"), (TABLE_Y - 3 * h, [900, 1030], "r"),
        (TABLE_Y - 4 * h, [210], "l"), (TABLE_Y - 4 * h, [960], "r"),
        (TABLE_Y - 5 * h, [160], "l"), (TABLE_Y - 5 * h, [920], "r"),
        (TABLE_Y - 6 * h, [220], "l"),
    ]
    n = 0
    for (y, xs, layer) in rows:
        for x in xs:
            tt = T_LITR + .1 + .05 * n
            S.append((x, y, tt, MUGC[(n + 2) % 6], 5 * math.sin(n * 2.3), 1 if n % 2 else -1, layer))
            n += 1
    return S


SLOTS = pile_slots()


def pile_top(t):
    """Высота центральной части горы (по которой цепляются руки Димы)."""
    top = TABLE_Y
    for (x, y, tt, *_r) in SLOTS:
        if 330 < x < 760 and t >= tt + .1:
            top = min(top, y - 78 * MK)
    return top


def drop_in(t, tt, h=170.0, dur=.1):
    """Кружка падает сверху на место: (dy, sx, sy)."""
    if t < tt:
        return None
    u = (t - tt) / dur
    if u < 1:
        return -h * (1 - ease_in(u, 2)), 1.0, 1.0
    sx, sy = props.squash(t, tt + dur, amp=.22, freq=3.2, damp=8)
    return 0.0, sx, sy


def puff(x, y, t, t0, seed=0, n=9, r0=40, r1=170):
    u = (t - t0) / .45
    if u <= 0 or u >= 1:
        return ""
    o = []
    for i in range(n):
        a = i / n * 2 * math.pi + .3
        ra, rb = r0 + (r1 - r0) * ease_out(u) * .6, r0 + (r1 - r0) * ease_out(u)
        o.append(line([(x + math.cos(a) * ra, y + math.sin(a) * ra), (x + math.cos(a) * rb, y + math.sin(a) * rb)], 9 * (1 - u) + 2, "#f6efe0",
                      taper=.6, wmin=.25, seed=seed + i))
    for i in range(5):
        a = i / 5 * 2 * math.pi + 1.1
        rr = (1 - u) * 34 + 6
        cx, cy = x + math.cos(a) * (40 + 70 * ease_out(u)), y + math.sin(a) * (30 + 50 * ease_out(u))
        o.append(shape(ellipse_pts(cx, cy, rr, rr * .85, 10), "#eef0f6", "", w=3.0, seed=seed + 30 + i))
    return "".join(o)


def table10():
    o = [shape(lib.rect_pts(-700, TABLE_Y - 6, 1780, TABLE_Y + 70), props.C_WOOD,
               blob(lib.rect_pts(-700, TABLE_Y + 40, 1780, TABLE_Y + 70), props.C_WOOD_SH), w=5, seed=9400)]
    o.append(line([(-700, TABLE_Y + 8), (1780, TABLE_Y + 8)], 4, props.C_WOOD_HI, taper=.05, wmin=.8, seed=9401))
    fr = lib.rect_pts(-700, TABLE_Y + 70, 1780, TABLE_Y + 1400)
    inner = "".join(line([(-700, TABLE_Y + 70 + 120 * i), (1780, TABLE_Y + 70 + 120 * i)], 3, "#5e3e22", taper=.05, wmin=.8, seed=9410 + i)
                    for i in range(1, 9))
    inner += blob(lib.rect_pts(-700, TABLE_Y + 70, 1780, TABLE_Y + 120), "#4e331c")
    o.append(shape(fr, "#6e4a2a", inner, w=5, seed=9402))
    for x0 in (60, 620):
        o.append(shape(lib.rrect(x0, TABLE_Y + 170, x0 + 400, TABLE_Y + 380, 14), "#7c5531", "", w=4, seed=9420 + x0))
        o.append(shape(lib.rrect(x0 + 160, TABLE_Y + 250, x0 + 240, TABLE_Y + 280, 12), "#3a2a20", "", w=3, seed=9430 + x0))
    return "".join(o)


def frame10(t):
    sh = props.shake(t, T_LITR, amp=16, dur=.45, seed=3)
    sh2 = props.shake(t, T_VMESTO + .02, amp=7, dur=.3, seed=5)
    # камера: откат с разгоном от подушки к общему плану, качание
    u = ease_in(clamp((t - 19.35) / 1.55), 2.2)
    z = lerp(1.32, .97, u)
    lib.INK_K[0] = 1.0 / z ** .5
    cx = lerp(420, 540, u) + sh[0] + sh2[0]
    cy = lerp(1150, 1010, u) + sh[1] + sh2[1]
    sway = smooth(T_LITR, T_LITR + .5, t)
    roll = lerp(1.5, -.6, u) + 2.2 * sway * math.sin((t - T_LITR) * 2 * math.pi * .9)
    o = [night_paper()]
    # кофейник влетает сверху справа
    pot_u = ease_out(clamp((t - (T_LITR - .12)) / .3), 3)
    pot_x, pot_y = lerp(1300, 790, pot_u), lerp(-150, 360, pot_u) + 6 * math.sin(t * 7)
    pot_rot = lerp(-10, -48, pot_u) + 2 * math.sin(t * 5)
    pot_svg = props.coffee_pot(pot_x, pot_y, 1.15, -pot_rot, t)
    tip = props.pot_spout(pot_x, pot_y, 1.15, -pot_rot)
    # Дима: тусклый → глаза-блюдца
    wide = smooth(T_LITR - .02, T_LITR + .14, t)
    jolt = props.squash(t, T_LITR, amp=.35, freq=3.4, damp=7)[1] if t >= T_LITR else 1.0
    blink = bump(t, 19.9, .2)
    trem = 0.08 * wide * math.sin(t * 47)
    ex = {"brows": "up" if wide > .5 else "tired", "mouth": "wobble" if wide > .5 else "tired", "lid": lerp(.36, 1.0, wide) * (1 - blink),
          "look": (trem + lerp(-.3, .05, wide), .1 + trem * .7), "scale_n": 1 + .55 * wide * jolt, "scale_f": 1 + .5 * wide * jolt, "hair": 6 * wide}
    # руки: на столе → цепляются за верх горы
    pt = pile_top(t)
    climb = clamp((TABLE_Y - pt) / (2 * 78 * MK))
    ys = lerp(TABLE_Y - 10, pt + 14, climb)
    tgt_f = (lerp(300, 420, climb), ys)
    tgt_n = (lerp(780, 680, climb), ys - 6)
    fig = people.figure("dima", HIP[0], HIP[1] - 18 * climb, SC10, ex, lean=0.0, head_ang=-.04 + .02 * math.sin(t * 3),
                        arms={"f": ("ik", tgt_f, 1), "n": ("ik", tgt_n, -1)}, hands={"f": {"kind": "none"}, "n": {"kind": "none"}})
    o.append(fig["svg"])
    o.append(table10())
    # подушка → кружка
    pp = (300.0, TABLE_Y)
    if t < T_VMESTO + .08:
        dy = props.hop(t, T_VMESTO - .1, h=120, dur=.2)
        s = 1.0 + .25 * smooth(T_VMESTO - .1, T_VMESTO + .08, t)
        o.append(props.pillow(pp[0], pp[1] + dy, 1.9 * s, -4 + 20 * smooth(T_VMESTO - .1, T_VMESTO + .08, t), seed=2))
    else:
        sx, sy = props.pop(t, T_VMESTO + .06, amp=.35)
        o.append(G(mug(0, 0, MK, 0, "blue", t, .7, seed=40, handle=1), pp[0], pp[1], sx, sy))
    # гора кружек: центральная часть и две качающиеся башни
    layers = {"c": [], "l": [], "r": []}
    for i, (x, y, tt, col, rot, hd, layer) in enumerate(SLOTS):
        if i < 7 and tt < T_LITR:          # ряд на столе выскакивает пружиной
            if t < tt:
                continue
            sx, sy = props.pop(t, tt, amp=.38)
            layers[layer].append(G(mug(0, 0, MK, rot, col, t, .6, seed=50 + i, handle=hd), x, y, sx, sy))
            continue
        d = drop_in(t, tt)
        if d is None:
            continue
        dy, sx, sy = d
        layers[layer].append(G(mug(0, 0, MK, rot, col, t, .5, seed=50 + i, handle=hd), x, y + dy, sx, sy))
    sw = sway * math.sin((t - T_LITR) * 2 * math.pi * 1.1)
    o.append(f'<g transform="rotate({.8 * sw:.3f} 540 {TABLE_Y})">{"".join(layers["c"])}</g>')
    o.append(f'<g transform="rotate({-2.6 * sw:.3f} 230 {TABLE_Y})">{"".join(layers["l"])}</g>')
    o.append(f'<g transform="rotate({2.6 * sw:.3f} 960 {TABLE_Y})">{"".join(layers["r"])}</g>')
    # кисти поверх: пальцы цепляются за край горы (или лежат на столе)
    for side, flip in (("f", 1), ("n", 1)):
        Wr = np.array(fig["wrist"][side])
        E = np.array(fig["elbow"][side])
        d = Wr - E
        d = d / np.linalg.norm(d)
        dd = d * (1 - climb) + np.array([0.0, 1.0]) * climb
        dd = dd / np.linalg.norm(dd)
        o.append(people.hand_svg("dima", tuple(Wr), tuple(dd), k=SC10, flip=flip, curl=(.55, .6, .62, .66), spread=.12, thumb=.45, bend=.15,
                                 seed=9500 + (0 if side == "f" else 30)))
    o.append(puff(pp[0], pp[1] - 90, t, T_VMESTO + .03, seed=9600))
    # кофейник и бесконечная струя в верх правой башни
    o.append(pot_svg)
    if t > T_LITR + .02:
        tops = [(x, y) for (x, y, tt, *_r) in SLOTS if x > 860 and t >= tt + .1]
        tx, ty = min(tops, key=lambda p: p[1]) if tops else (830, TABLE_Y)
        ang = math.radians(2.6 * sw)
        rx, ry = tx - 960, ty - 78 * MK - TABLE_Y
        tx2 = 960 + rx * math.cos(ang) - ry * math.sin(ang)
        ty2 = TABLE_Y + rx * math.sin(ang) + ry * math.cos(ang)
        o.append(props.pour_stream(tip[0], tip[1], tx2, ty2 + 8, t, w=18, seed=97, bend=.15))
    body = "".join(o)
    return f'<g transform="{lib.cam(cx, cy, z, roll)}">{body}</g>'


def frame(sid, t):
    lib.dyn_begin()
    if sid == "s10":
        body = frame10(t)
    elif sid == "s09":
        import s63d_room
        body = s63d_room.frame09(t)
    else:
        import s63d_bed
        body = s63d_bed.frame11(t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#1f2550"/>{body}')
