"""Диван Димы рилса 44 «мечтает и ничего» (агент room): s01 (хук: вечер, Дима развалился на диване и мечтает, облако
растёт, влёт камеры), s04 (крупнее: в руке пустой пунктирный билет, на «нет» облако лопается).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика; удары — на словах voice/words.json.
Мир — вечерняя комната (world.py: den.py рилса 32 + фиолетовый диван рилса 42); Дима — people.py (лохматый, щетина,
мешки, горчичное худи) сидит, откинувшись на спинку, в 3/4 вправо; облако мечты — dream.py.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dream  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import world  # noqa: E402
from ink import ellipse_pts  # noqa: E402
from lib import INK, back_out, blob, clamp, ease_io, ease_out, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!:").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


T_DIMA = wt("дима")          # 0.16
T_KAZH = wt("каждый")        # 0.56
T_VECH = wt("вечер")         # 1.16
T_MECH = wt("мечтает")       # 1.44
T_BIL = wt("билета")         # 5.40
T_NET = wt("нет")            # 6.24

BS = 0.62
HIP = np.array([330.0, 1186.0])
_ST = {}


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def kick(t, t0, dur=.4, freq=2.2):
    u = t - t0
    if u <= 0 or u > dur:
        return 0.0
    return math.exp(-u * 9) * math.cos(2 * math.pi * freq * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def hook_cam(t, hit):
    """Влёт (правила 28–29): 1/1.42 → 1.055 за 0.22 с, отскок к 1, поворот +3.6° → −1° → 0; второй удар +10 % на hit."""
    T = 0.22
    if t < T:
        u = t / T
        z = 1 / 1.42 + (1.055 - 1 / 1.42) * ease_out(u, 3)
        rot = 3.6 * (1 - ease_out(u, 2)) - 1.0 * ease_out(u, 2)
    else:
        u = t - T
        z = 1 + .055 * math.exp(-u * 9) * math.cos(2 * math.pi * 2.2 * u)
        rot = -1.0 * math.exp(-u * 7) * math.cos(2 * math.pi * 1.8 * u)
    z *= 1 + .10 * max(0.0, kick(t, hit, .5, 1.6))
    return z, rot


def blur_px(t):
    return 6.0 * (1 - smooth(0.0, 0.2, t))


# ═════════════════════════════ Дима на диване ═════════════════════════════
def dima(t, arms, hands=None, expr=None, lean=-0.42, head_ang=-0.22, hip=None, breath=0.0):
    h = HIP if hip is None else hip
    p = dict(hip=tuple(h), scale=BS, lean=lean + .012 * breath, feet={"n": ((612, 1508), 0.05), "f": ((570, 1496), 0.05)}, arms=arms,
             hands=hands or {}, expr=expr or {}, head_ang=head_ang, hood=0.0, strings=(1.5 * osc(t, 1.1), 1.2 * osc(t, .9, 1)))
    return people.draw(p, "dima")


def world_back(t):
    if "back" not in _ST:
        _ST["back"] = world.room_back(0) + world.sofa_back()
        _ST["seat"] = world.sofa_seat()
        lib.static_done()
    return _ST["back"]


def compose(inner, cam, blur=0.0, front=""):
    cx, cy, s, r = cam
    g = f'<g transform="{lib.cam(cx, cy, s, r)}">{inner}</g>'
    if blur > .05:
        fid = lib.uid("bl")
        lib.DEFS.append(f'<filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="{blur:.2f}"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    vg = lib.rad_grad([(0, "#0a0c1e", 0), (.62, "#0a0c1e", 0), (1, "#0a0c1e", .42)], 540, 900, 1180, 1400)
    return lib.svg(f'<rect width="1080" height="1920" fill="#2b2a3a"/>{g}{front}<rect width="1080" height="1920" fill="url(#{vg})"/>')


def dreamy_expr(t, smile=1.0, look=(.35, -.85), closed=0.0, mouth="smile", open_=0.0):
    return dict(lid=.42, look=look, brows="up", mouth=mouth, smile=smile, open=open_, closed=closed, blush=.55 * smile, hair=2 * osc(t, 1.2))


# ═════════════════════════════ s01 — хук ═════════════════════════════
CL01 = (690.0, 470.0)      # центр облака мечты (мир)


def s01(t):
    world_back(t)
    lib.dyn_begin()
    hit = T_MECH
    z, rot = hook_cam(t, hit)
    # Дима: дышит, мечтательно покачивает головой, улыбка шире к «мечтает»
    br = osc(t, .55)
    sm = .75 + .25 * smooth(T_VECH, hit, t)
    expr = dreamy_expr(t, sm, look=(.42 + .05 * osc(t, .7), -.9), closed=blink_at(t, .95, .16))
    d = dima(t, {"n": ("ik", (440 + 6 * br, 1120 + 4 * br), -1), "f": ("ang", -2.5, -.6)},
             {"n": dict(kind="open", flip=1, dir=(.4, .9), curl=(.35, .4, .45, .5), spread=.1, thumb=.4, bend=.2)},
             expr, head_ang=-.24 + .03 * osc(t, .8) - .04 * bump(t, hit, .4), breath=br)
    # пузыри мысли: три кружка вылетают из головы, облако растёт; на «мечтает» — раздувается до края кадра
    hx, hy = d["head"]
    puffs = []
    for k, (x, y, r, tk) in enumerate([(hx + 120, hy - 150, 22, -.25), (hx + 210, hy - 260, 34, -.12), (hx + 320, hy - 380, 50, .0)]):
        kk = back_out(clamp((t - tk) / .22), 2.0)
        if kk > .02:
            puffs.append(dream.puff(x + 4 * osc(t, .9, k), y + 5 * osc(t, 1.1, k), r * kk * (1 + .05 * osc(t, 1.6, k)), 4700 + k * 10, t))
    grow = .52 + .3 * ease_out(clamp(t / 1.2), 2)
    swell = back_out(clamp((t - (hit - .08)) / .3), 1.4)
    sc = grow + (1.9 - grow) * swell
    rx, ry = 300 * sc, 240 * sc
    pan = 30 * t
    inside = dream.scene_inside(t, 1000, 780, pan)
    cl = dream.cloud(t, 300, 240, inside, wob=.05, seed=4500)
    cx = CL01[0] + 40 * swell
    cy = CL01[1] + 60 * swell
    cloud = f'<g transform="translate({cx:.1f} {cy:.1f}) scale({sc:.4f}) rotate({1.5 * osc(t, .4):.2f})">{cl}</g>'
    pet = dream.petals(t, 14, (-200, 100, 1300, 1500), seed=4600, k=1.0)
    inner = (_ST["back"] + _ST["seat"] + d.get("legs", "") + d["arm_f"] + d["body"] + d["arm_n"] + world.evening_light(t)
             + "".join(puffs) + cloud + pet)
    # камера: влёт к Диме и облаку, потом медленный наезд к облаку
    k = ease_io(clamp((t - .2) / 1.4))
    s = 1.18 * z * (1 + .06 * k)
    cam = (520 + 70 * k + 20 * (1 - z), 860 - 120 * k - 30 * (1 - z), s, rot + .3 * osc(t, .5))
    set_ink(s)
    return compose(inner, cam, blur=blur_px(t))


SHOTS = {"s01": s01}


def frame(sid, t):
    return SHOTS[sid](t)
