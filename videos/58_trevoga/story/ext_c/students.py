"""Студенты Чикаго рилса 58: разные люди (рост, телосложение, причёска, очки, кепка, цвет кожи и одежды), сидят за партами анфас/в 3/4.
Основа — person.py рилса 55 (контур тушью, cel-тень). Парта и билеты — общие props.py (ладонь/масштаб как у Димы). Без флагов и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import lib  # noqa: E402
import person  # noqa: E402
import props as PR  # noqa: E402
from lib import blob, clamp, f, line, mix, rect_pts, shape  # noqa: E402

BASE = dict(skin="#e8bd98", hair="short", hair_c="#3a2a22", top="#6a7a98", low="#3a3a48", shoes="#2a2020", face=0.15)
CAST = {
    "a": dict(skin="#efc7a4", hair="ponytail", hair_c="#7a4a2a", top="#c8563f", sleeve="#c8563f", collar="#f2e6c8", face=.25, bw=.86, h=.97),
    "b": dict(skin="#8a5a3c", hair="curly", hair_c="#1e1612", top="#3f7a6a", sleeve="#3f7a6a", face=-.2, bw=1.05, h=1.04, hw=1.04),
    "c": dict(skin="#e3b894", hair="short", hair_c="#c8a04a", top="#4a5a8a", sleeve="#4a5a8a", glasses=True, face=.3, bw=.98, stripes="#7a8ab8"),
    "d": dict(skin="#d9a67f", hair="bun", hair_c="#2a2020", top="#e0b84a", sleeve="#e0b84a", face=-.3, bw=.82, h=.94),
    "e": dict(skin="#f0cfb0", hair="bald", hair_c="#7a6a5a", top="#8a4a58", sleeve="#8a4a58", mustache=True, face=.2, bw=1.14, h=1.06, hw=1.08, collar="#f2e6c8"),
    "f": dict(skin="#b07a55", hair="bob", hair_c="#2a1a14", top="#5a4a78", sleeve="#5a4a78", face=-.15, bw=.9, h=1.0, glasses=True),
    "g": dict(skin="#eac3a0", hair="short", hair_c="#4a3426", top="#2f3a46", sleeve="#2f3a46", cap="#c85a3a", face=.3, bw=1.0, h=1.02, zip=True),
    "h": dict(skin="#f2d2b8", hair="curly", hair_c="#a8622c", top="#7aa064", sleeve="#7aa064", face=.1, bw=.9, h=.95),
    "i": dict(skin="#6f4a34", hair="short", hair_c="#15100e", top="#d8d2c4", sleeve="#d8d2c4", face=-.25, bw=1.08, h=1.05, stubble=True),
    "j": dict(skin="#e8bd98", hair="ponytail", hair_c="#1c1a1a", top="#c8a0c0", sleeve="#c8a0c0", face=.2, bw=.84, h=.96, collar="#ffffff"),
    "k": dict(skin="#d9a67f", hair="short", hair_c="#5a3a26", top="#4a8aa8", sleeve="#4a8aa8", face=-.1, bw=1.0, h=1.0, stripes="#7ab0c8"),
    "l": dict(skin="#f3d6bc", hair="bob", hair_c="#c8863a", top="#a8465a", sleeve="#a8465a", glasses=True, face=.25, bw=.9, h=.98),
}
MOODS = {
    "calm": dict(mouth="smile", brow=-.15, look=(.0, .1)),
    "glad": dict(mouth="smile", brow=-.4, look=(.0, .05)),
    "tense": dict(mouth="wavy", brow=.9, look=(.3, .25)),
    "grim": dict(mouth="frown", brow=.7, look=(.2, .3)),
    "write": dict(mouth="flat", brow=.2, look=(0, .75)),
    "wonder": dict(mouth="o", brow=-.3, look=(-.2, .1)),
}


def spec(key, face=None):
    s = dict(BASE, arms_front=True)
    s.update(CAST[key])
    if face is not None:
        s["face"] = face
    return s


def desk_surface(x, edge_y, sc, w=440):
    """Столешница ЗА студентом (виден край слева-справа от него) + ножки; передняя панель — рисуется поверх студента."""
    return PR.desk(x, edge_y, sc * .9, w * sc, legs_to=edge_y + 330 * sc, seed=int(x) % 17)


def desk_panel(x, edge_y, sc, w=440):
    k = sc * .9
    hw = w * sc / 2
    o = shape(rect_pts(x - hw, edge_y - 2, x + hw, edge_y + 112 * sc, 3), PR.C_DESK_END,
              lib.blob(rect_pts(x - hw, edge_y + 80 * sc, x + hw, edge_y + 112 * sc), mix(PR.C_DESK_END, "#000000", .22)), w=3.4 * k, seed=8300 + int(x) % 31)
    o += blob(rect_pts(x - hw, edge_y - 2, x + hw, edge_y + 12 * sc), mix(PR.C_DESK, "#ffffff", .0))
    return o


def student(key, x, edge_y, sc, mood="calm", t=0.0, ph=0.0, arms=None, face=None, write=0.0, blink_t=(), tilt=0.0, up=0.0, w=440, flip=False, extra_mood=None, shrug=0.0):
    """Студент за партой: (x, edge_y) — середина передней кромки парты, sc — масштаб (1 ≈ Дима ростом 750 px)."""
    sp = spec(key, face)
    m = dict(MOODS[mood])
    if extra_mood:
        m.update(extra_mood)
    bl = 0.0
    for a in blink_t:
        u_ = (t - a) / .14
        if 0 < u_ < 1:
            bl = math.sin(math.pi * u_)
    sway = math.sin(t * 1.7 + ph)
    # руки на парте: плечо-локоть-кисть вперёд-к центру; на «письме» правая рука водит туда-сюда
    wr = math.sin(t * 13 + ph) * write
    ar = arms or {"R": (34 + 5 * up + 10 * shrug, -118 + 4 * up + 6 * shrug + 9 * wr), "L": (-34 - 5 * up - 10 * shrug, 118 - 4 * up - 6 * shrug)}
    pose = dict(arms=ar, look=m["look"], blink=bl, mouth=m["mouth"], brow=m["brow"], head_tilt=tilt + 1.4 * sway - 1.2 * write)
    origin_y = edge_y + 300 * sc * sp.get("h", 1.0)
    o = [desk_surface(x, edge_y, sc, w)]
    cid = lib.clip_rect(x - 600 * sc, edge_y - 2400, 1200 * sc, 2400 + 70 * sc)
    o.append(f'<g clip-path="url(#{cid})">' + person.draw(sp, pose, x, origin_y, sc, 600 + ord(key[0]) * 7, flip) + "</g>")
    o.append(desk_panel(x, edge_y, sc, w))
    return "".join(o)
