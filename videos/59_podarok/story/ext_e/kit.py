"""Рилс 59 «подарок», группа E: s11 (кухня: тесто, духовка, кривой пирог) и s14 (Дима и кот, пером «кот»).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Люди и кот — common/people.py, предметы — common/props.py, кухня — common/kitchen.py."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, COMMON)
import kitchen as K  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, rect_pts, shape, smooth, svg  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
T = {i: w["start"] for i, w in enumerate(WORDS)}
INK = lib.INK
FL = 1440.0
BS = 0.6
_ST = {}


def lerp(a, b, u):
    return a + (b - a) * u


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def rnd(i, a=0.0, b=1.0):
    return a + (b - a) * ((math.sin(i * 12.9898 + 4.1) * 43758.5453) % 1.0)


def hand_spec(curl=.25, d=(1, .35), thumb=None, k=1.0, flip=1):
    return dict(kind="open", flip=flip, dir=d, curl=(curl, curl, curl, curl * .9), spread=.04 + .12 * (1 - curl), thumb=curl if thumb is None else thumb,
                bend=.1, k=k)


def whip(out, t, t0, dist=260):
    wp = ease_out(clamp(1 - (t - t0) / .14), 2)
    if wp > .02:
        lib.DEFS.append(f'<filter id="whip1" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{f(70 * wp)} 0"/></filter>')
        return f'<g filter="url(#whip1)" transform="translate({f(-dist * wp)} 0)">{out}</g>'
    return out


# ───────────────────────── Дима: поза в «правой» системе, разворот sx ─────────────────────────
def dima_pose(x, *, lean=.05, ha=0.0, expr=None, n_t, f_t, hands=None, run=0.0, ph=0.0, bob=0.0, hip_dy=0.0, torso_k=1.0, sn=None, sf=None):
    e = dict(lid=.9, look=(.5, .1), brows="calm", mouth="flat", flush=.0)
    if expr:
        e.update(expr)
    hy = 1108 + bob + hip_dy
    shx = x + 240 * BS / .6 * math.sin(lean) + 6
    feet = {}
    for side, off in (("n", 0.0), ("f", .5)):
        c = math.sin(2 * math.pi * (ph + off))
        lift = max(0.0, math.cos(2 * math.pi * (ph + off))) * run
        ax = x + (18 if side == "n" else -22) + c * 62 * run
        ay = FL - (6 if side == "f" else 0) - 54 * lift * (1 if run > 0 else 0)
        feet[side] = ((ax, ay), -.5 * lift if run > 0 else 0.0)
    sn = sn if sn is not None else (-1 if n_t[0] >= shx else 1)
    sf = sf if sf is not None else (-1 if f_t[0] >= shx else 1)
    p = dict(hip=(x, hy), scale=BS, lean=lean, torso_k=torso_k, feet=feet, arms={"n": ("ik", n_t, sn), "f": ("ik", f_t, sf)},
             hands=hands or {"n": hand_spec(.35), "f": hand_spec(.35)}, expr=e, head_ang=ha, head_off=(0, 0), hood=0.0, strings=(0, 0))
    d = people.draw(p, "dima")
    d["x"] = x
    return d


def flip_g(s, x, sx):
    if abs(sx - 1) < 1e-3:
        return s
    return f'<g transform="translate({f(x * (1 - sx))} 0) scale({sx:.4f} 1)">{s}</g>'


def head_xy(d, ha, lean, lx, ly, k=BS):
    a = lean * .5 + ha
    ca, sa = math.cos(a), math.sin(a)
    return (d["head"][0] + k * (lx * ca - ly * sa), d["head"][1] + k * (lx * sa + ly * ca))


FLOUR = "#F7F4EC"


def flour_on(d, ha, lean, amount=1.0, seed=0):
    """Мука: мазки на худи, на щеке и на лбу (сплошные светлые пятна без обводки, в той же системе, что и поза)."""
    o = []
    hx, hy = d["x"], 1108
    for i in range(int(9 * amount)):
        a = rnd(i + seed, 0, 6.28)
        cx = hx + 150 * math.sin(lean) + rnd(i + 3 + seed, -62, 70)
        cy = hy - 150 + rnd(i + 9 + seed, -70, 105)
        o.append(blob(ellipse_pts(cx, cy, rnd(i + 5, 7, 18), rnd(i + 8, 5, 11), 8, rot=math.degrees(a)), FLOUR))
    for (lx, ly, rx_, ry_) in ((20, 62, 26, 12), (86, 52, 18, 9), (-10, -88, 22, 8)):
        cx, cy = head_xy(d, ha, lean, lx, ly)
        o.append(blob(ellipse_pts(cx, cy, rx_ * BS, ry_ * BS, 8), FLOUR))
    for side in ("n", "f"):
        w = d["wrist"][side]
        o.append(blob(ellipse_pts(w[0] - 8, w[1] - 10, 16, 10, 8), FLOUR))
    return "".join(o)


def puff(t, t0, x, y, n=9, k=1.0, dur=.45):
    """Облачко муки: светлые кружки разлетаются и оседают."""
    u = (t - t0) / dur
    if not 0 <= u <= 1:
        return ""
    o = []
    for i in range(n):
        a = math.radians(-160 + 140 * rnd(i + 3))
        v = 150 * k * (.4 + .9 * rnd(i + 8))
        px = x + v * math.cos(a) * ease_out(u)
        py = y + v * math.sin(a) * ease_out(u) * .7 + 90 * u * u
        r = (7 + 9 * rnd(i + 11)) * (1 - .55 * u) * k
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="{FLOUR}"/>')
    return "".join(o)


# ───────────────────────── предметы стола ─────────────────────────
def dough(x, y, sq=0.0, k=1.0):
    """Тесто: кремовый ком на столе; sq 0…1 — приплюснут (шире и ниже)."""
    rx, ry = 78 * (1 + .22 * sq) * k, 46 * (1 - .36 * sq) * k
    o = blob(ellipse_pts(x + 6, y + 6, rx * 1.02, 12 * k, 14), "#9c6a3a", .0)
    o += shape(ellipse_pts(x, y - ry * .7, rx, ry, 18), "#F0DDB0", blob(ellipse_pts(x + rx * .25, y - ry * .5, rx * .7, ry * .7, 14), "#DEC48D", .9) +
               blob(ellipse_pts(x - rx * .3, y - ry * 1.05, rx * .35, ry * .22, 10), "#FFF4D6", .9), w=3.8, seed=7701)
    for i in range(7):
        o += blob(ellipse_pts(x + rnd(i, -rx * .8, rx * .8), y - ry * .8 + rnd(i + 4, -ry * .4, ry * .5), rnd(i + 2, 4, 8), rnd(i + 6, 2.5, 5), 7), FLOUR)
    return o


def flour_sack(x, y, k=1.0):
    pts = [(-52, 0, 1), (52, 0, 1), (60, -60), (54, -118), (-54, -118), (-60, -60)]
    inner = blob([(18, -118), (54, -118), (60, -60), (52, 0), (18, 0)], "#DCCFB4", .9) + blob(rect_pts(-60, -80, 60, -44), "#6FA3C7")
    inner += blob(ellipse_pts(0, -62, 26, 20, 12), "#F7F4EC")                      # круглая бирка без букв
    o = shape(pts, "#EFE6D2", inner, w=3.6, seed=7710)
    o += shape([(-54, -118, 1), (54, -118, 1), (44, -146), (-46, -146)], "#E3D8BF", blob([(10, -146), (44, -146), (54, -118), (10, -118)], "#CFC2A4"), w=3.4, seed=7711)
    return f'<g transform="translate({f(x)} {f(y)}) scale({k:.3f})">{o}</g>'


def table_stuff(t, hit_u):
    sh = 3 * math.sin(t * 60) * hit_u
    o = []
    o.append(flour_sack(34, 1008, 1.0))
    o.append(props.jar_flowers(138, 1012 + sh, 1.0, seed=2))
    return "".join(o)


def static_world():
    if "kit" in _ST:
        return
    _ST["kit"] = K.static()
    _ST["tl"], _ST["tt"] = K.table(-480, 310, 990, 1060)
    lib.static_done()
    _ST["init"] = True


# ───────────────────────── s11 ─────────────────────────
T_SAM, T_ISP, T_KRIV = T[52], T[53], T[54]       # 20.80, 21.10, 21.48
S11_T0 = 20.64


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def pie_state(t):
    """0 — купол, 1 — осел набок (на «кривой»)."""
    return smooth(T_KRIV - .02, T_KRIV + .16, t)


def frame11(t):
    static_world()
    # — время —
    turn = ease_io(seg(t, 20.83, 20.99))
    sx = lerp(-1.0, 1.0, turn)
    walk = ease_io(seg(t, 20.80, 21.05))
    X = lerp(430, 548, walk)
    run = .55 * math.sin(math.pi * seg(t, 20.80, 21.08)) if 20.8 < t < 21.08 else 0.0
    ph = (t - 20.8) * 3.2
    door = ease_out(seg(t, 20.94, 21.1), 2)
    reach = seg(t, 21.0, 21.12)
    pull = ease_in(seg(t, 21.10, 21.30), 1.6)       # лоток выезжает к нему
    lift = ease_io(seg(t, 21.28, 21.50))
    # — ритм теста до 20.9: удары на 20.50 и 20.80 —
    def press(t_):
        u = (t_ - 20.725) / .3
        v = u - math.floor(u)
        return (math.sin(math.pi * min(1.0, v / .5)) if v < .5 else 0.0)
    pr = press(t) if t < 20.9 else 0.0
    hit_dt = t - T_SAM
    hit_u = math.exp(-hit_dt * 10) if hit_dt >= 0 and t < 21.3 else 0.0
    # — Дима —
    left_phase = sx < 0
    dough_x, dough_y = 232.0, 1038.0
    if left_phase:
        sq = max(pr * .6, hit_u)
        fy = dough_y - 62 + 50 * pr + 24 * hit_u * 0
        tn = (2 * X - (dough_x + 18), fy)               # в «правой» системе цель зеркалится относительно X
        tf = (2 * X - (dough_x - 40), fy - 4 + 10 * pr)
        lean = .2 + .06 * pr
        ha = .05 - .06 * pr
        ex = dict(lid=.8, look=(-.4, .6), brows="up" if hit_dt > -.1 else "calm", mouth="grin" if t > 20.7 else "smile", smile=.9, laugh=.0)
        hands = {"n": hand_spec(.82, (0, 1)), "f": hand_spec(.82, (0, 1))}
        d = dima_pose(X, lean=lean, ha=ha, expr=ex, n_t=tn, f_t=tf, hands=hands, run=0.0, bob=-8 * pr, hip_dy=14)
    else:
        # тянет пирог из духовки (приседает, лотком к себе), потом поднимает на грудь
        crouch = (smooth(21.04, 21.14, t) - ease_io(seg(t, 21.28, 21.46))) * .55
        pie_x = lerp(830, lerp(716, X + 200, lift), pull)
        pie_y = lerp(1236, lerp(1292, 990, lift), pull)
        tn = (pie_x - 70, pie_y - 8)
        tf = (pie_x + 82, pie_y + 6)
        lean = .08 + .34 * crouch / .55
        sh_ = smooth(T_KRIV, T_KRIV + .12, t)
        pr_o = seg(t, 21.62, 21.82)
        ex = dict(lid=.9 - .08 * sh_ + .1 * pr_o, look=(.25 + .3 * pr_o, .9 * (1 - pr_o) * (1 if t < 21.7 else 0) + .0), brows="up" if t > T_KRIV - .05 else "worry",
                  mouth="flat" if t < 21.4 else ("talk" if t < 21.7 else "grin"), open=.25, smile=.2 + .8 * pr_o, blush=.5 * pr_o)
        ha = .06 - .14 * pr_o + .05 * sh_ * (1 - pr_o)
        hands = {"n": hand_spec(.6, (1, 0), flip=1), "f": hand_spec(.5, (1, 0), flip=1)}
        d = dima_pose(X, lean=lean, ha=ha, expr=ex, n_t=tn, f_t=tf, hands=hands, run=run, ph=ph, hip_dy=90 * crouch / .55 * .35, sn=-1, sf=1)
    o = [_ST["kit"], K.light(t), K.oven_glow(door, t)]
    # пирог в духовке (пока не вытянули)
    ps = pie_state(t)
    st = "crooked" if ps > .5 else "whole"
    # стол и тесто
    o.append(_ST["tl"] + _ST["tt"])
    o.append(table_stuff(t, hit_u))
    dsq = max(pr * .6, hit_u * .9)
    o.append(dough(dough_x, dough_y, dsq if t < 20.95 else .15))
    o.append(puff(t, T_SAM, dough_x, dough_y - 40, 11, 1.2))
    o.append(puff(t, 20.50, dough_x, dough_y - 40, 7, .8))
    in_oven = t < 21.1
    if door > .05 and in_oven:
        o.append(props.pie(lerp(840, 830, 0), 1252, 1.0, "whole"))
    o.append(K.oven_door(door))
    legs, af, bd, an = d.get("legs", ""), d["arm_f"], d["body"], d["arm_n"]
    fl_ = flour_on(d, ha, lean if left_phase else lean)
    group = legs + af + bd + fl_
    o.append(flip_g(group, X, sx))
    if not in_oven:
        sag = ps
        pk = lerp(1.0, 1.75, ease_io(seg(t, 21.12, 21.5)))
        o.append(props.pie(pie_x, pie_y + 10, pk, st))
        if ps > 0:
            o.append(steam(t, pie_x, pie_y - 60 * pk, .8))
    o.append(flip_g(an, X, sx))
    o.append(puff(t, 21.12, 760, 1250, 8, .9))
    z = lerp(1.22, 1.3, ease_io(seg(t, 20.44, 22.7)))
    cx = lerp(340, 640, ease_io(seg(t, 20.84, 21.3)))
    cy = 1090
    cam = (cx, cy, z, .8 * math.sin(t * 1.3) + 1.4 * math.exp(-(t - T_KRIV) * 7) * (t >= T_KRIV) * math.sin((t - T_KRIV) * 38))
    set_ink(z)
    return whip(f'<g transform="{lib.cam(*cam)}">{"".join(o)}{K.motes(t, seed=5)}</g>', t, S11_T0)


def steam(t, x, y, k=1.0):
    o = []
    for i in range(3):
        u = ((t * .9 + i * .33) % 1.0)
        sy = y - 100 * u
        o.append(line([(x - 30 + 30 * i + 8 * math.sin(u * 6 + i), sy), (x - 26 + 30 * i - 8 * math.sin(u * 6 + i), sy - 36)], 7 * (1 - u) + 2, "#FFFFFF", taper=.6, wmin=.3, seed=i + 5, op=.9 * (1 - u)))
    return "".join(o)


def frame(sid, t):
    lib.dyn_begin()
    body = {"s11": frame11}[sid](t)
    return svg(f'<rect width="1080" height="1920" fill="#2a1f2a"/>{body}')
