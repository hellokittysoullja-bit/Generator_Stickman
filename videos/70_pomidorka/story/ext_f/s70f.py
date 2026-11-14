"""Рилс 70 «помидорка», группа F — кот, призыв, петля.
s08 (12.16–14.20): ночной стол, Дима головой на руках; кот запрыгивает (12.3), шагает и трогает макушку лапой, «совсем» (12.85)
    поворачивается к таймеру, «не в нём» (13.17–13.6) отталкивает таймер — тот катится к краю и замирает; Дима поднимает голову,
    удивлённо смотрит на кота; кот садится и смотрит на зрителя.
s17 (31.70–33.00, хлёст): призыв — Дима и кот на столе смотрят на зрителя, кот просыпается и поворачивает морду, на чистой стене над
    котом пером пишется «кот» (common/hand_kot.py).
s18 (33.00–34.90): петля к кадру хука s01 — тот же стол и ракурс «стол крупно» (room.CAM_DESK_CLOSE), утром; лапа кота крутит таймер,
    клин сжимается в ломтик, Дима с улыбкой смотрит на зрителя.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, Дима — common/people.py, кот — common/cat.py,
таймер и ноутбук — common/props.py, «кот» — common/hand_kot.py; здесь только хореография и камера."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(0, os.path.join(STORY, "ext_e"))
import cat as CAT  # noqa: E402
import hand_kot  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from h70 import blinks, bump, decay, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
from lib import INK, blob, clamp, ease_out, ellipse_pts, line, shape  # noqa: E402

SX, SY = R.SIT
BS = 1.0
SC = BS * people.HEIGHT["dima"]
FEET = {"n": ((SX + 300 * BS, R.FL - 52), 0.0), "f": ((SX + 250 * BS, R.FL - 50), 0.0)}


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.update(kw)
    return e


def dima_parts(e, pose, layers_order=("legs", "pelvis", "arm_f", "body", "arm_n"), **kw):
    kw = dict(feet=FEET, **kw)
    full = people.dima(SX, SY, BS, e, pose, **kw)
    parts = {k: people.dima(SX, SY, BS, e, pose, layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    return full, parts


def table_y(k, back=0.0):
    """Центр таймера, стоящего на столе (back — насколько дальше от передней кромки)."""
    return R.DESK_TOP - 42 - back - PR.TOMATO_RY * k


def cat_paw(base, tip, k, seed=4600):
    """Левая (от зрителя) передняя лапа кота тянется в сторону: от плеча base к подушечке tip (мир)."""
    from ink import band
    mid = ((base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2 - 18 * k)
    arm = band([base, mid, tip], 58 * k, 46 * k, step=4, cap=False)
    o = [shape(arm, CAT.CAT, blob([(base[0], base[1] + 10 * k), (tip[0], tip[1] + 8 * k), (tip[0], tip[1] + 16 * k), (base[0], base[1] + 22 * k)],
                                  CAT.CAT_SH, .6), w=4.6 * k / .62, seed=seed)]
    pp = ellipse_pts(tip[0], tip[1], 26 * k, 22 * k, 12)
    o.append(shape(pp, CAT.CAT, "", w=4.4 * k / .62, seed=seed + 1))
    o.append(blob(ellipse_pts(tip[0] - 6 * k, tip[1] + 4 * k, 10 * k, 8 * k, 8), "#e8823a"))
    for kk in (-8, 6):
        o.append(line([(tip[0] + kk * k, tip[1] - 16 * k), (tip[0] + (kk + 3) * k, tip[1] - 5 * k)], 2.2, seed=seed + 5 + kk))
    return "".join(o)


# ═════════════════════════ s08: кот будит Диму и отталкивает таймер ═════════════════════════
T_A08 = 12.16
T_JUMP0, T_LAND = 12.02, 12.42                          # присед → толчок → приземление (whoosh 12.3 — полёт)
T_DELO, T_SOVS, T_NE, T_NEM = wt(38), wt(40), wt(41), wt(43)   # 12.37, 12.85, 13.17, 13.4
CAT_K = .74
CAT_LAND = (1150.0, R.DESK_TOP - 22)
CAT_TOUCH = (965.0, R.DESK_TOP - 18)
CAT_PUSH = (990.0, R.DESK_TOP - 18)
TK08 = .5
TIM08 = (1095.0, table_y(TK08, 0))
TIM_EDGE = (R.DESK_X[1] - PR.TOMATO_RX * TK08 - 4, table_y(TK08, 0))
T_ROLL0, T_ROLL1 = T_NE + .2, T_NEM + .45


def roll_x(t):
    u = clamp((t - T_ROLL0) / (T_ROLL1 - T_ROLL0))
    return lerp(TIM08[0], TIM_EDGE[0], 1 - (1 - u) ** 2.4), u


def s08(t):
    sc = R.desk_scene(t, "night")
    # таймер: стоит и тикает → толчок лапой → катится (поворот по пройденному пути) → у самого края качается и замирает
    x, ru = roll_x(t)
    dist = x - TIM08[0]
    rot = math.degrees(dist / (PR.TOMATO_RY * TK08)) * .55
    wob = 0.0
    if t > T_ROLL1:
        wob = 9 * decay(t, T_ROLL1, 5.0, 2.4)
        rot = rot + wob
    tilt_y = -4 * abs(math.sin(math.radians(rot))) if 0 < ru < 1 else 0.0
    timer = PR.tomato_timer(x, TIM08[1] + tilt_y, TK08, rot % 360 if ru < 1 else rot, wedge=PR.WEDGE_25 * .72, shake=1.6 if t < T_ROLL0 else .3,
                            leaf_swing=8 * math.sin(t * 4) + 18 * bump(t, T_ROLL1 - .05, .5), t=t, seed=2)
    lap = PR.laptop(R.LAPTOP[0], R.LAPTOP[1], .72, 1.0, "dark", t=t, seed=1, turn=.55)
    # Дима: голова на руках → «не в нём» поднимает голову, удивлённо смотрит на кота
    up = sm(t, T_NEM - .05, T_NEM + .4) * .55
    e = ex("sink", closed=1.0 - sm(t, T_SOVS - .1, T_SOVS + .1) * .0)
    if t > T_DELO + .25:            # проснулся от касания: глаза приоткрыты
        e = ex("sink", lid=.35, look=(.6, .3))
    if up > .05:
        e = ex("surprise", look=(.8, -.1), lid=lerp(.5, 1.0, up / .55), closed=blinks(t, (13.95,)))
    tap = bump(t, T_DELO + .3, .22) + bump(t, T_DELO + .43, .2)
    lay = people.LAYERS_ARMS_UNDER if up < .3 else ("legs", "pelvis", "arm_f", "body", "arm_n")
    kw = dict(feet=FEET, u_pose=("sit_desk", up), lean_add=.015 * math.sin(t * 1.9) - .03 * tap, head_add=.03 * tap)
    parts = {k: people.dima(SX, SY, BS, e, "head_arms", layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    full = people.dima(SX, SY, BS, e, "head_arms", **kw)
    dima_up = "".join(parts[k] for k in lay if k not in ("legs",))
    # кот: присед на полу → прыжок на стол → шаги влево к голове → лапа на макушку → поворот к таймеру → толчок → садится, смотрит на нас
    cst = dict(look=(-.6, .1), blink=blinks(t, (13.0, 13.85)), tail=8 * math.sin(t * 2.4), ear=2 * math.sin(t * 3.3), flame_e=1.0 + .3 * math.sin(t * 5))
    paw_svg = ""
    if t < T_LAND + .06:
        ju = clamp((t - T_JUMP0) / (T_LAND + .06 - T_JUMP0))
        cat = people.cat_jump((1330.0, R.FL - 6), CAT_LAND, CAT_K, ju, t, dict(cst, look=(-.5, -.4)), height=260.0)
    else:
        wu = sm(t, T_LAND + .04, T_DELO + .16)
        step = sm(t, T_SOVS + .02, T_NE + .02)
        cx = lerp(lerp(CAT_LAND[0], CAT_TOUCH[0], wu), CAT_PUSH[0], step)
        cy = CAT_LAND[1]
        turn_t = sm(t, T_SOVS - .02, T_SOVS + .2)            # к таймеру (вправо)
        turn_c = sm(t, T_NEM + .3, T_NEM + .62)               # к зрителю
        st = dict(cst, turn=lerp(lerp(-.7, .75, turn_t), 0.0, turn_c), look=(lerp(lerp(-.7, .8, turn_t), 0.0, turn_c), lerp(.3, .2, turn_t) * (1 - turn_c)),
                  tilt=lerp(-7, 5, turn_t) * (1 - turn_c) + 4 * bump(t, T_NEM + .7, .5))
        if wu < 1 or step > 0 and step < 1:
            st["walk"] = (t - T_LAND) / .42
        push = bump(t, T_NE + .1, .35)
        if push > .02:
            st["paw"] = push
            st["paw_dx"] = 95.0
        if turn_c > .5:
            st["smile"] = 1.0
        cat = CAT.draw(cx, cy - 3 * abs(math.sin(t * 7)) * (wu < 1), CAT_K, st, t)
        # лапа на макушку Димы (левая от зрителя): поднимается, два лёгких касания, опускается
        pu = sm(t, T_DELO + .17, T_DELO + .3) * (1 - sm(t, T_SOVS - .04, T_SOVS + .1))
        if pu > .02:
            hx, hy = full["head"]
            base = (cx - 22 * CAT_K, cy - 70 * CAT_K)
            top = (hx + 120, hy - 60 + 10 * tap)
            tip = lerp2((base[0] - 30, base[1] + 30), top, pu)
            paw_svg = cat_paw(base, tip, CAT_K)
    shadow = blob(ellipse_pts(roll_x(t)[0], R.DESK_TOP - 40, 52, 8, 12), "#20182e", .25)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], lap, parts["legs"], sc["desk_legs"], sc["chair_seat"],
             dima_up, sc["lamp"], shadow, timer, cat, paw_svg]
    # камера: откат, мини-тряска на прыжке, панорама за катящимся таймером
    u = sm(t, T_A08 - .2, 14.4)
    pan = sm(t, T_ROLL0, T_ROLL1 + .2)
    s = lerp(1.32, 1.16, u)
    ccx = lerp(lerp(860, 830, u), 960, pan) + 4 * math.sin(t * 1.6)
    ccy = lerp(860, 900, u) + 4 * math.sin(t * 1.3)
    sx_, sy_ = shake(t, T_LAND, 7)
    sx2, sy2 = shake(t, T_ROLL1, 4)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx + sx_ + sx2, ccy + sy_ + sy2, s, lerp(.8, -.5, u))}">{"".join(world)}</g>'
    return g, "#2a2440"


FRAMES = {"s08": s08}


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
