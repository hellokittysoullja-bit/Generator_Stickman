"""Дима днём за столом рилса 44 (агент room): s13 — подпёр подбородок ручкой и думает над блокнотом; на «думает»
(26.88) над головой появляется маленькое аккуратное облачко с Фудзи, на «Японию» (27.84) он кивает и записывает.
Мир — комната рилса 32/41 (den.py) в дневном свете (обои и окно day=True), стол, стул; Дима — people.py (как в 41).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import den  # noqa: E402
import dream  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
from ink import ellipse_pts  # noqa: E402
from lib import INK, back_out, blob, clamp, ease_io, ease_out, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!:").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


T_POET = wt("поэтому")         # 25.80
T_DUM = wt("думает")           # 26.88
T_HOCHU = wt("хочу")           # 27.48
T_JAP = wt("японию", 27.0)     # 27.84

den.DESK_X0 = 420.0
BS = 0.6
HIP = np.array([300.0, 1262.0])
NOTE = (640.0, 1080.0)          # блокнот на столе (центр нижней кромки)
_ST = {}


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def dima(t, arms, hands, expr, lean, head_ang):
    p = dict(hip=tuple(HIP), scale=BS, lean=lean, feet={"n": ((560, 1468), 0.0), "f": ((535, 1462), 0.0)}, arms=arms, hands=hands,
             expr=expr, head_ang=head_ang, hood=0.0, strings=(1.5 * osc(t, 1.1), 1.2 * osc(t, .9, 1)))
    return people.draw(p, "dima")


def notebook():
    """Открытый блокнот на столе (вид сбоку-сверху): две страницы домиком, пружина, клетка."""
    x, y = NOTE
    s = [blob([(x - 150, y + 4), (x + 150, y + 4), (x + 160, y + 14), (x - 160, y + 14)], "#3a2410", .25)]
    L = [(x - 150, y + 8, 1), (x - 130, y - 30), (x - 60, y - 34), (x - 4, y - 22, 1), (x - 2, y + 10, 1)]
    R = [(x + 2, y + 10, 1), (x + 4, y - 22, 1), (x + 60, y - 34), (x + 130, y - 30), (x + 150, y + 8, 1)]
    for k, pts in enumerate((L, R)):
        inner = blob([(x - 160, y), (x + 160, y), (x + 160, y + 12), (x - 160, y + 12)], "#d9d6cc", .8)
        for j in range(3):
            yy = y - 20 + j * 9
            inner += line([(x - 130 + 136 * k, yy), (x - 10 + 136 * k, yy)], 1.6, "#a9c3dc", seed=7910 + j + 5 * k, op=.8)
        s.append(shape(pts, "#fbfaf4", inner, w=3, seed=7900 + k))
    s.append(blob([(x - 160, y + 8), (x + 160, y + 8), (x + 158, y + 16), (x - 158, y + 16)], "#3f6e8a"))
    s.append(line([(x - 2, y - 12), (x + 2, y + 10)], 3, "#6f7484", seed=7920))
    return "".join(s)


def scribble(u):
    """Строчка на странице, пока он пишет (тонкая линия растёт)."""
    x, y = NOTE
    if u <= 0:
        return ""
    x0, x1 = x + 24, x + 24 + 100 * u
    pts = [(x0 + (x1 - x0) * k / 10, y - 18 + 2 * math.sin(k * 2.3)) for k in range(11)]
    return line(pts, 2.6, "#2f4f8a", seed=7930, taper=.2, wmin=.5)


def pen(a, b, seed=7940):
    """Ручка: синий корпус, колпачок с клипом, металлический наконечник. a — задний конец, b — кончик."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0]])
    h = 6.5
    P = lambda s_, v: (float((a + u * s_ + n * v)[0]), float((a + u * s_ + n * v)[1]))  # noqa: E731
    o = [shape([P(0, -h) + (1,), P(L * .84, -h) + (1,), P(L * .84, h) + (1,), P(0, h) + (1,)], "#3f63b8",
               blob([P(0, 1), P(L * .84, 1), P(L * .84, h), P(0, h)], "#2c4a8f", .9), w=2.6, seed=seed)]
    o.append(shape([P(L * .84, -h) + (1,), P(L, 0) + (1,), P(L * .84, h) + (1,)], "#c9ccd6", "", w=2.2, seed=seed + 1))
    o.append(shape([P(4, -h - 3) + (1,), P(L * .32, -h - 3) + (1,), P(L * .32, -h) + (1,), P(4, -h) + (1,)], "#2c4a8f", "", w=2, seed=seed + 2))
    return "".join(o)


def kw_hand():
    people.C = people.PAL["dima"]
    return dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])


def compose(inner, cam):
    cx, cy, s, r = cam
    sun = lib.rad_grad([(0, "#fff2c8", .45), (.5, "#ffe6a8", .15), (1, "#ffe6a8", 0)], 200, 520, 900, 900)
    g = (f'<g transform="{lib.cam(cx, cy, s, r)}">{inner}'
         f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{sun})" style="mix-blend-mode:screen"/></g>')
    vg = lib.rad_grad([(0, "#2a2418", 0), (.65, "#2a2418", 0), (1, "#2a2418", .3)], 540, 900, 1180, 1400)
    return lib.svg(f'<rect width="1080" height="1920" fill="#cfe0d6"/>{g}<rect width="1080" height="1920" fill="url(#{vg})"/>')


def back(t):
    if "back" not in _ST:
        _ST["back"] = "".join([den.wall(t, day=True), den.window(t, day=True), den.board(t), den.shelf(t), den.floor()])
        _ST["chair"] = room.chair(HIP[0], HIP[1] + 4, 1, 2300)
        _ST["desk_b"] = den.desk_back()
        _ST["desk_t"] = den.desk_top() + notebook()
        lib.static_done()
    return _ST["back"]


def s13(t):
    back(t)
    lib.dyn_begin()
    tj = T_JAP
    write = smooth(tj - .05, tj + .3, t)                 # рука уходит с подбородка к блокноту
    nod = bump(t, tj - .08, .3) + .6 * bump(t, tj + .28, .26)
    think = smooth(T_DUM - .4, T_DUM, t) * (1 - write)
    # глаза: смотрит в блокнот → на «думает» поднимает взгляд вверх (к облачку) → на «Японию» снова в блокнот
    look = (.55 - .25 * think, .45 - 1.2 * think + .1 * write)
    expr = dict(lid=.48 + .1 * think, look=look, brows="det" if think < .5 else "up", mouth="flat" if write < .5 else "smile", smile=.6,
                closed=max(blink_at(t, 25.95, .16), blink_at(t, 28.25, .14)), hair=2 * osc(t, 1.1) + 4 * nod)
    head_ang = .06 + .02 * osc(t, .5) - .1 * think + .12 * nod + .05 * write
    lean = .22 + .01 * osc(t, .45) + .05 * write
    # ближняя рука: кулак с ручкой под подбородком; потом пишет в блокноте
    chin = np.array([452.0, 1056.0]) + np.array([0, 6 * osc(t, .45)])
    wr_w = np.array([NOTE[0] + 10 + 50 * clamp((t - tj - .3) / .5) + 6 * osc(t, 7.5) * (t > tj + .3), NOTE[1] - 42])
    wr = chin + (wr_w - chin) * ease_io(write)
    hn = dict(kind="open", flip=1, dir=(.25 + .55 * write, -.97 + 1.5 * write), curl=(.85, .9, .92, .95), spread=.02, thumb=.1 + .8 * write, bend=.2)
    hf = dict(kind="open", flip=1, dir=(.95, .2), curl=(.3, .35, .4, .45), spread=.08, thumb=.4, bend=.15)
    d = dima(t, {"n": ("ik", tuple(wr), -1), "f": ("ik", (610, 1074), -1)}, {"n": hn, "f": hf}, expr, lean, head_ang)
    # ручка в кулаке: стоит вверх к подбородку → при письме кончиком в страницу
    w0 = d["wrist"]["n"]
    pa = w0 + np.array([30, 6]) + (np.array([66, -54]) - np.array([30, 6])) * write
    pb = w0 + np.array([40, -60]) + (np.array([40, 10]) - np.array([40, -60])) * write
    pn = pen(tuple(pa), tuple(pb))
    sc = scribble(clamp((t - tj - .3) / .5))
    # облачко с Фудзи: пузырьки от головы, облако аккуратно выпрыгивает на «думает»
    hx, hy = d["head"]
    cl = ""
    for k, (dx, dy, r, tk) in enumerate([(110, -130, 13, T_DUM - .2), (160, -200, 20, T_DUM - .1)]):
        kk = back_out(clamp((t - tk) / .2), 2.0)
        if kk > .02:
            cl += dream.puff(hx + dx, hy + dy + 3 * osc(t, 1, k), r * kk, 4720 + k * 10, t)
    kc = back_out(clamp((t - T_DUM) / .3), 1.8)
    if kc > .02:
        inside = f'<g transform="scale(.6)">{dream.scene_inside(t, 1000, 760, 0)}</g>'
        c = dream.cloud(t, 300, 240, inside, wob=.03, seed=4520)
        k = .5 * kc * (1 + .06 * bump(t, tj, .3))
        cl += f'<g transform="translate({hx + 250:.1f} {hy - 300:.1f}) scale({k:.4f}) rotate({1.2 * osc(t, .4):.2f})">{c}</g>'
    inner = (_ST["back"] + _ST["chair"] + _ST["desk_b"] + d.get("legs", "") + _ST["desk_t"] + sc + d["arm_f"] + d["body"] + pn + d["arm_n"] + cl)
    u = clamp((t - 25.45) / 3.2)
    s = 1.72 + .1 * ease_io(u) + .03 * bump(t, tj, .35)
    cam = (520 + 20 * u, 900 - 20 * u, s, -.5 + .7 * u)
    set_ink(s)
    return compose(inner, cam)


SHOTS = {"s13": s13}


def frame(sid, t):
    return SHOTS[sid](t)
