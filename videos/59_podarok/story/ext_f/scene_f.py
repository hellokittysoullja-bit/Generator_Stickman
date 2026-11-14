"""Рилс 59 «подарок», группа F: s12 (мама крупно), s13 (кот крадёт кусок), s15 (объятие). frame(sid, t) -> SVG 1080×1920, t — общее время ролика."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bits as B  # noqa: E402
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rrect, shape, spring  # noqa: E402,F401

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def mixv(a, b, u):
    return a + (b - a) * u


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def open_hand(c=.2, d=(1, 0), spread=.2, thumb=.2, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(c, c, c, c * .9), spread=spread, thumb=thumb, bend=.1, k=k)


NONE = dict(kind="none")


def fig(who, hip, bs, lean, arms, hands, expr, feet=None, head_ang=0.0, flip=False, torso_k=1.0, head_off=(0, 0), head_k=1.0):
    """Человек; flip — смотрит влево (цели рук задаются в мире, отражение внутри). Возвращает слои (строки в мире) и запястья в мире."""
    hx = hip[0]
    M = (lambda p: (2 * hx - p[0], p[1])) if flip else (lambda p: p)
    arms2 = {}
    for s_, a in arms.items():
        arms2[s_] = (a[0], M(a[1])) + tuple(a[2:]) if a[0] == "ik" else a
    feet2 = None
    if feet:
        feet2 = {s_: (M(v[0]), v[1]) for s_, v in feet.items()}
    pose = dict(hip=tuple(hip), scale=bs, lean=lean, torso_k=torso_k, feet=feet2, arms=arms2, hands=hands, expr=expr, head_ang=head_ang,
                head_off=head_off, head_k=head_k, hood=0.0, strings=(0, 0))
    d = people.draw(pose, who)
    wrap = (lambda s: f'<g transform="translate({2 * hx:.2f} 0) scale(-1 1)">{s}</g>') if flip else (lambda s: s)
    d2 = {k: wrap(v) for k, v in d.items() if isinstance(v, str)}
    d2["wrist"] = {k: M(v) for k, v in d["wrist"].items()}
    d2["elbow"] = {k: M(v) for k, v in d["elbow"].items()}
    d2["head"] = M(d["head"])
    return d2


def hold(wx, wy, R, side, k, who, h=None, seed=0, flip=False):
    """Пальцы вокруг предмета: (wx, wy) — центр хвата; возвращает (задняя часть, передняя)."""
    people.C = people.PAL[who]
    kw = people.hand_kw()
    kw.pop("nail", None)
    return Hand.grip((wx, wy), R, side, k=k, seed=seed, h=h, **kw)


def spark_ring(t, cx, cy, t0, n=7, rad=300, k=1.3):
    o = ""
    for i in range(n):
        ang = i / n * 2 * math.pi + .5
        dly = (i % 3) * .07
        u = (t - t0 - dly) / .7
        if 0 < u < 1:
            r = rad * (.7 + .5 * u)
            o += B.spark(cx + r * math.cos(ang), cy + r * math.sin(ang) * .85, k, u)
    return o


# ═══════════════════════════════ s12: мама крупно ═══════════════════════════════
def frame12(t):
    T_MAMA, T_PLAK, T_SCH = wt(WORDS_IDX["Мама"]), wt(WORDS_IDX["плакала"]), wt(WORDS_IDX["счастья"])
    z = 1.22 + .2 * ease_io(clamp((t - 22.32) / 2.1))
    set_ink(1.2 * z)
    cx, cy = 590 - 40 * ease_io(clamp((t - 22.3) / 2.2)) + 14 * math.sin(t * 1.3), 930 - 20 * ease_io(clamp((t - 22.3) / 2.2))
    scn = [B.kitchen(t, glow=0)]
    # стол-столешница позади Димы справа, на нём пирог
    scn.append(B.table(560, 1500, 1030, 110, legs=False))
    scn.append(B.pie(1000, 1060, .5, cut=None, sag=1.0))
    # ── Дима на заднем плане (смотрит влево, держит букет, потом руки у груди)
    bsd = .5
    dhip = (830, 1090)
    give = clamp((t - (T_MAMA - .35)) / .3)
    G0 = (690, 905)
    rel = ease_io(clamp((t - T_MAMA) / .5))
    dar = (G0[0] + 120 * rel, G0[1] + 50 * rel)
    dima_arms = {"n": ("ik", (G0[0] + 12 + 80 * rel, G0[1] + 20 + 220 * rel), -1), "f": ("ik", (dhip[0] - 40, dhip[1] + 100), -1)}
    dexp = dict(lid=.95, look=(-.5, .1), closed=blink_of(t, (22.9, 23.7)), brows="up", mouth="smile", smile=.6 + .4 * ease_io(clamp((t - T_SCH) / .3)), blush=.5)
    dhands = {"n": NONE if rel < .6 else open_hand(.3, (-1, .6), .1, .3, flip=-1, k=bsd * 1.6), "f": open_hand(.3, (-1, .3), .1, .3, flip=-1, k=bsd * 1.6)}
    dd = fig("dima", dhip, bsd, -.03, dima_arms, dhands, dexp, feet=None, head_ang=-.04 + .03 * math.sin(t * 2), flip=True)
    scn.append(dd["arm_f"] + dd["body"])
    # ── мама
    bs = 1.05
    hip = (370 + 4 * math.sin(t * 1.9), 1335)
    pre = clamp((t - (T_MAMA - .12)) / .22)
    grab = ease_io(clamp((t - T_MAMA) / .32))
    chest = ease_io(clamp((t - T_MAMA - .25) / .55))
    # точка хвата букета: до передачи у Димы, потом едет к груди мамы
    Gx = mixv(mixv(G0[0], 770, 0), 655, chest) if False else G0[0] + (655 - G0[0]) * chest
    Gy = G0[1] + (1160 - G0[1]) * chest - 70 * bump(t, T_MAMA + .1, .5)
    if t < T_MAMA:
        marm = ("ik", (hip[0] + 170 * bs, hip[1] - 150 * bs + 60 * pre), -1)
    else:
        marm = ("ik", (Gx + 30, Gy + 14), -1)
    sob = .6 * ease_io(clamp((t - T_PLAK + .1) / .5)) * (1 - ease_io(clamp((t - T_SCH) / .25)))
    tw = ease_io(clamp((t - T_PLAK + .05) / .45))
    joy = ease_io(clamp((t - T_SCH + .02) / .28))
    lift = ease_io(clamp((t - T_MAMA) / .2))
    mexp = dict(lid=1.0 - .1 * joy, look=(.55, .35 - .5 * chest), closed=blink_of(t, (22.75, 23.4)), laugh=.0 + .9 * joy, tears=.0 * tw, tw=tw, tph=t,
                brows="up" if (t < T_PLAK or joy > .5) else "worry", mouth="talk" if joy < .3 else "grin", open=(.15 + .35 * sob + 0.5 * joy) if t >= T_MAMA else .55 * (1 - lift) + .15, smile=.2 + .8 * joy,
                blush=1.0)
    ma = {"n": marm, "f": ("ik", (hip[0] + 30 * bs, hip[1] + 330 * bs), -1)}
    mh = {"n": NONE, "f": open_hand(.5, (.4, 1), .1, .5, k=bs)}
    ha = -.07 * (1 - joy) + .12 * joy + .03 * math.sin(t * 9) * sob
    dm = fig("mama", hip, bs, .04, ma, mh, mexp, feet=None, head_ang=ha, head_k=1.4)
    scn.append(dm["arm_f"] + dm["body"])
    # букет: в руке Димы → в руке мамы
    people.C = people.PAL["mama"]
    wx, wy = dm["wrist"]["n"]
    bk_rot = -8 + 10 * chest + 2 * math.sin(t * 2.2)
    if t < T_MAMA + .05:
        gk = bsd * 1.5
        bkx, bky = G0
        bk = B.bouquet(bkx, bky, .5, -22 + 6 * math.sin(t * 3))
        bk_pos = (bkx, bky)
        scn.append(bk)
        bg, fg = hold(bkx, bky, 24, -1, bsd * 1.3, "dima", seed=950)
    else:
        bk_pos = (Gx, Gy)
        sc = .5 + .55 * chest
        scn.append(f'<g>{B.bouquet(Gx, Gy, sc, bk_rot, sway=math.sin(t * 5) * .3)}</g>')
    scn.append(dm["arm_n"])
    if t >= T_MAMA + .05:
        bg, fg = hold(Gx - 6, Gy, 30, 1, 1.25, "mama", seed=960)
        scn.append(bg + fg)
    scn.append(B.counter_front(-400, 1500, 1395))
    scn.append(spark_ring(t, 470, 760, T_SCH - .05, 8, 360, 1.5))
    cam = lib.cam(cx, cy, z, 1.1 * math.sin(t * 1.1) + 1.4 * bump(t, T_PLAK, .4))
    return f'<g transform="{cam}">{"".join(scn)}</g>'


WORDS_IDX = {w["word"].strip(".,!?"): i for i, w in enumerate(WORDS)}


def frame(sid, t):
    lib.dyn_begin()
    body = {"s12": frame12}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#f3e3c3"/>{body}')
