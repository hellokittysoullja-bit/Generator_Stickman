"""Рилс 60 «темнота», группа E: s12 (окно и даль), s13 (взрослый Дима читает при торшере), s14 (стрелки часов, Дима смотрит в окно).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Комната — common/room.py, люди — common/people.py, книга — common/props.py."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, smooth, spring  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


T_INOGDA, T_VDAL = wt(52), wt(54)
T_CHITAET, T_LAMPE = wt(57), wt(59)
T_POLCHASA, T_SMOTRIT, T_OKNO = wt(62), wt(63), wt(65)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def lerp(a, b, u):
    return a + (b - a) * u


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink(t, times, dur=.16):
    v = 0.0
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


NO_HAND = {"kind": "none"}
BS = 0.8                     # Дима в кресле (room.SEAT)
BOOK_K = 1.25


# ═══════════════════════════════ Дима в кресле с книгой ═══════════════════════════════
def seated(t, *, book_c, book_rot, flip, expr, head_ang=0.0, lean=-.04, book_mode="open", hold=2, free_n=None):
    """Дима сидит в кресле, книга в руках (hold=2 — обе руки держат края; hold=1 — только ближняя, дальняя на подлокотнике).
    book_c — центр низа корешка книги, book_rot — наклон книги, flip — перелистывание (0…1).
    Возвращает (svg, head_xy)."""
    sx, sy = R.SEAT
    ch = R.armchair()
    feet = {"n": ((sx + 300, R.FL - 52), 0.0), "f": ((sx + 250, R.FL - 50), 0.0)}
    bw = 108 * BOOK_K
    a = math.radians(book_rot)
    ca, sa = math.cos(a), math.sin(a)
    bx, by = book_c

    def bp(x, y):                     # точка в системе книги -> мир
        return (bx + (x * ca - y * sa) * BOOK_K, by + (x * sa + y * ca) * BOOK_K)

    gL = bp(-104, -46)                # левый край страниц, чуть ниже середины
    gR = bp(104, -46)
    gk = BS * .95
    wrL = (gL[0] - 46 * gk, gL[1] + 6)
    wrR = (gR[0] + 40 * gk, gR[1] + 10)
    if hold == 2:
        arms = {"n": ("ik", wrL, -1), "f": ("ik", wrR, -1)}
    else:
        arms = {"n": ("ik", wrL, -1), "f": ("ik", free_n or (sx + 160, sy - 40), -1)}
    hands = {"n": NO_HAND, "f": NO_HAND if hold == 2 else dict(kind="open", flip=-1, dir=(1, .5), curl=(.5, .5, .5, .45), spread=.1, thumb=.5, bend=.1)}
    full = people.draw(dict(hip=(sx, sy), scale=BS * people.HEIGHT["dima"], lean=lean, feet=feet, arms=arms, hands=hands,
                            head_ang=head_ang, expr=expr, torso_k=1.0, hood=0.0, head_off=(0, 0)), "dima")
    o = [ch["back"], ch["seat"], full["legs"], ch["arm"], full["arm_f"], full.get("pelvis", ""), full["body"], full["arm_n"]]
    # книга и хват
    backL, frontL = people.grip_svg("dima", gL, 6 * BOOK_K, -1, k=gk, seed=930)
    backR, frontR = ("", "")
    if hold == 2:
        backR, frontR = people.grip_svg("dima", gR, 6 * BOOK_K, +1, k=gk, seed=960)
    if book_mode == "open":
        bk = PR.book_open(bx, by, BOOK_K, book_rot, flip=flip, seed=3)
    else:
        bk = PR.book_closed(bx, by, BOOK_K, book_rot)
    o.append(backL + backR + bk + frontL + frontR)
    return "".join(o), full["head"]


def room_bg(t, lamp_on=1.0, flick=0.0, par=0.0, with_clock=True, clock=None):
    lamp = R.floor_lamp(lamp_on, flick)
    o = [R.wall_floor(), R.window(t, par), R.side_table(t)]
    if with_clock:
        cx, cy, r = R.CLOCK
        md, hd = clock or (60.0, 300.0)
        o.append(R.wall_clock(cx, cy, r, md, hd))
    o.append(lamp["pool"])
    return "".join(o), lamp


# ═══════════════════════════════ s13: читает при торшере ═══════════════════════════════
def frame13(t):
    a = 20.8
    u = clamp((t - a) / 2.4)
    s = 1.0 + .1 * ease_io(u)
    cx = 420 - 30 * ease_io(u) + 6 * math.sin(t * 1.3)
    cy = 990 - 40 * ease_io(u) + 5 * math.sin(t * 1.1 + 1)
    rot = -.6 + .8 * ease_io(u)
    set_ink(s)
    glow_k = .7 + .3 * smooth(T_LAMPE - .05, T_LAMPE + .25, t)
    bg, lamp = room_bg(t, glow_k, flick=.5 + .5 * math.sin(t * 7))
    flip = clamp((t - (T_CHITAET - .05)) / .5)
    flip = ease_io(flip)
    brk = math.sin(t * 2.4) * 3
    look = (.62 + .18 * math.sin((t - a) * 3.1), .55)
    smile = .25 + .55 * smooth(T_LAMPE, T_LAMPE + .3, t)
    expr = dict(lid=.55, look=look, closed=blink(t, (21.25, 22.62)), brows="calm", mouth="smile", smile=smile)
    if T_CHITAET - .05 < t < T_CHITAET + .55:
        expr["look"] = (.4 + .4 * flip, .5)
    head_ang = .12 + .02 * math.sin(t * 1.7) - .04 * bump(t, T_CHITAET, .5)
    book_c = (570, 1022 + brk)
    fig, head = seated(t, book_c=book_c, book_rot=-16 + 2 * math.sin(t * 1.4), flip=flip, expr=expr, head_ang=head_ang)
    body = [bg, lamp["lamp"], fig, lamp["cone"]]
    body.append(R.bloom(clamp((t - T_LAMPE) / .55) * 1.0 if t > T_LAMPE else 0.0))
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(body)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    body = {"s13": frame13}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#2e2740"/>{body}')
