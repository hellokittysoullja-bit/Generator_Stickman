"""Сцена kitchen рилса 34 «сорвался — гулять так гулять»: планы s01 s02 s03 s04 s06 s14 s15.
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика). Мир — world.py (кухня рилса 29, перестроенная под стол,
коробка пончиков, календарик), Дима сидит слева лицом вправо (people.py из рилсов 27/32, таз (230, 1262)).
Удары — на словах по voice/words.json."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
import world as Wd  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


BS = 0.6
HIP = np.array([230.0, 1262.0])
FEET = {"n": ((450, 1468), 0.0), "f": ((425, 1462), 0.0)}


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def dima(t, arms, hands=None, expr=None, hip=None, lean=0.12, head_ang=0.0, feet=None):
    hip = HIP if hip is None else np.array(hip, float)
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet or FEET, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=0.0, strings=(2 * osc(t, 1.3), 1.5 * osc(t, 1.1, 1)))
    return people.draw(p, "dima")


def table_world(t, d, *, cal=None, on_table="", mid="", front="", back_extra=""):
    """Слои: кухня, стул, задние ножки стола, ноги Димы, столешница, предметы, дальняя рука, тело, mid, ближняя рука, front."""
    w = [Wd.kitchen_bg(t, cal=cal, extra=back_extra)]
    w.append(room.chair(HIP[0], HIP[1] + 4, 1, 2300))
    w.append(Wd.table_back())
    w.append(d.get("legs", ""))
    w.append(Wd.table_top())
    w.append(on_table)
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(mid)
    w.append(d["arm_n"])
    w.append(front)
    return "".join(w)


def test(t):
    set_ink(1.3)
    d = dima(t, {"n": ("ik", (520, 1110), -1), "f": ("ik", (482, 1112), -1)},
             {"n": dict(kind="open", dir=(1, .1)), "f": dict(kind="open", dir=(1, .12))}, dict(lid=.4, look=(.6, .3), mouth="flat"))
    on = Wd.plate(520, 1128, .8) + Wd.donut_box(800, 1124, .85, lid=.12, glow=1)
    w = table_world(t, d, on_table=on)
    return Wd.compose(w, (560, 880, 1.3, 0), t)


SHOTS = {"test": test}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
