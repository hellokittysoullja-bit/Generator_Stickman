"""Рилс 71 «два лагеря», группа E — три маленьких шага и поток.
s16 (28.30–29.36, хлёст): стол сбоку в три четверти, ноутбук экраном к Диме; «Открыть» поднимает крышку одним пальцем, «ноутбук» экран
    загорается, свет на лице, Дима моргает.
s17 (29.36–30.40): край кровати, Дима натягивает полосатый носок на одну ногу, шевелит пальцами, вторая нога босая, кивает.
s19 (31.50–32.74): Дима в потоке печатает, стакан наполовину пуст, на ногах оба носка; «идёт само» — меловая стена за спиной осыпается.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, Дима — common/people.py, предметы — common/props.py;
здесь только хореография и камера (ноутбук экраном к Диме и ступни без кроссовок — h71.py). Надписей, букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from h71 import bare_feet, blinks, bump, laptop_side, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
from lib import INK, blob, clamp, ease_out, ellipse_pts, line  # noqa: E402

BG = "#e6dcc0"
FRAMES = {}
SX, SY = R.SIT
FEET = {"n": ((SX + 300, R.FL - 52), 0.0), "f": ((SX + 250, R.FL - 50), 0.0)}
LAP = (690.0, R.DESK_TOP - 70)       # передний (к Диме) край ноутбука на столешнице
LAP_K = .82


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.setdefault("bags", False)
    e.update(kw)
    return e


def parts_of(e, pose, **kw):
    full = people.dima(SX, SY, 1.0, e, pose, **kw)
    parts = {k: people.dima(SX, SY, 1.0, e, pose, layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    return full, parts


def face_light(head, u):
    """Холодный свет экрана на лице: небольшое пятно у лица (не огромный овал)."""
    if u <= .01:
        return ""
    return PR.glow(head[0] + 60, head[1] + 10, 150, .5 * u, "#DDE8FF", ry=170)


def type_hand(t, base, phase):
    ph = t * 10.5 + phase
    W = (base[0] + 8 * math.sin(ph * .7), base[1] - 5 * abs(math.sin(ph)))
    curl = tuple(.35 + .25 * max(0.0, math.sin(ph + i * 1.7)) for i in range(4))
    return W, {"dir": (1, .32), "curl": curl, "thumb": .35, "spread": .12, "bend": .1}


# ═════════════════════════ s16: открыть ноутбук одним пальцем ═════════════════════════
T_A16 = 28.30
T_OTKR, T_NOUT = wt(87), wt(88)              # 28.37, 28.85


def s16(t):
    sc = R.desk34_scene(t)
    op = ease_out(clamp((t - (T_OTKR - .05)) / (T_NOUT - .02 - (T_OTKR - .05))), 1.8)
    on = sm(t, T_NOUT - .02, T_NOUT + .14)
    lp = laptop_side(LAP[0], LAP[1], LAP_K, op, on=on, lines=0.0, t=t, seed=1)
    lt = lp["lid_top"]
    # ближняя рука: указательный палец под край крышки → поднимает → на «ноутбук» отпускает, кисть ложится у корпуса
    rel = sm(t, T_NOUT + .05, T_NOUT + .3)
    W_lift = (lt[0] - 78, lt[1] + 34)
    W_rest = (LAP[0] - 60, LAP[1] - 20)
    W_start = (LAP[0] - 30, LAP[1] - 10)
    go = sm(t, T_A16 - .2, T_OTKR - .02)
    Wn = lerp2(lerp2(W_start, W_lift, go), W_rest, rel)
    hn = {"dir": (1, -.35), "curl": (0, .8, .85, .85), "spread": .05, "thumb": .6} if rel < .5 else {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}
    Wf = (LAP[0] - 150, LAP[1] - 14)
    surprise = bump(t, T_NOUT + .05, .55)
    e = ex("focus", look=(.65, lerp(.55, .2, op)), lid=lerp(.62, .9, surprise), closed=blinks(t, (T_NOUT + .28, T_NOUT + .52), .14),
           brows="up" if surprise > .3 else "det")
    full, parts = parts_of(e, "lid_finger", feet=FEET, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)},
                           hands={"f": {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}, "n": hn},
                           lean_add=.04 * go - .05 * surprise + .015 * math.sin(t * 2.4), head_add=.05 - .06 * surprise)
    light = face_light(full["head"], on)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"], parts["arm_f"],
             parts["body"], lp["svg"], parts["arm_n"], light]
    # камера: хлёст, короткий наезд на лицо в свете экрана; мини-толчок на вспышке экрана
    u = sm(t, T_A16 - .2, 29.56)
    s = lerp(1.42, 1.62, u) + .03 * bump(t, T_NOUT, .3)
    hx, hy = full["head"]
    ccx = lerp(600, hx + 200, u) + 4 * math.sin(t * 1.5)
    ccy = lerp(880, hy + 200, u) + 3 * math.sin(t * 1.9)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.6, .3, u))}">{"".join(world)}</g>'
    return whip(g, t, T_A16), BG


FRAMES["s16"] = s16


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
