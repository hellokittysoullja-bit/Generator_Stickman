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
    """Передняя лапа кота тянется от плеча base к подушечке tip (мир): пушистая шерсть, округлая лапка с пальчиками."""
    from ink import band, fur
    d = (tip[0] - base[0], tip[1] - base[1])
    L = math.hypot(*d) + 1e-6
    ux, uy = d[0] / L, d[1] / L
    nx, ny = -uy, ux
    mid = ((base[0] + tip[0]) / 2 + nx * 16 * k, (base[1] + tip[1]) / 2 + ny * 16 * k)
    arm = band([base, mid, (tip[0] - ux * 18 * k, tip[1] - uy * 18 * k)], 64 * k, 50 * k, step=6, cap=False)
    arm = fur(arm, 6 * k, 5, seed=seed)
    o = [shape(arm, CAT.CAT, blob([(base[0] + nx * 22 * k, base[1] + ny * 22 * k), (tip[0] + nx * 18 * k, tip[1] + ny * 18 * k),
                                   (tip[0] + nx * 6 * k, tip[1] + ny * 6 * k), (base[0] + nx * 6 * k, base[1] + ny * 6 * k)], CAT.CAT_SH, .7),
               w=4.6 * k / .62, seed=seed)]
    # лапка: овал по направлению лапы, три пальчика по краю, светлые прядки
    ang = math.degrees(math.atan2(uy, ux))
    pp = ellipse_pts(tip[0], tip[1], 36 * k, 30 * k, 16, rot=math.radians(ang))
    o.append(shape(pp, CAT.CAT, blob(lib.T(ellipse_pts(tip[0], tip[1], 26 * k, 18 * k, 12), nx * 8 * k, ny * 8 * k), CAT.CAT_SH, .55),
                   w=4.4 * k / .62, seed=seed + 1))
    for j in (-1, 0, 1):
        a0 = (tip[0] + ux * 20 * k + nx * j * 13 * k, tip[1] + uy * 20 * k + ny * j * 13 * k)
        o.append(line([a0, (a0[0] + ux * 12 * k, a0[1] + uy * 12 * k)], 2.6, seed=seed + 5 + j))
    o.append(line([(tip[0] - ux * 30 * k + nx * 10 * k, tip[1] - uy * 30 * k + ny * 10 * k), (tip[0] - ux * 50 * k + nx * 14 * k, tip[1] - uy * 50 * k + ny * 14 * k)],
                  2.0, CAT.CAT_EDGE, seed=seed + 9, op=.8))
    return "".join(o)


def cat_left_paw(x, y, k, st, t, paw, paw_dx=82.0):
    """Кот (как cat.draw) тянет ЛЕВУЮ от зрителя переднюю лапу: туловище с лапами зеркалится вокруг оси кота (своя стоячая лапа
    этой стороны уходит в поднятую — третьей лапы нет), голова с загнутым левым ухом и хвост — как есть."""
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    o = [f'<g transform="rotate({st.get("tail", 0.0):.2f} {CAT.TAIL_PIVOT[0]} {CAT.TAIL_PIVOT[1]})">{CAT.tail_art()}{CAT.flame(t, 1.3, st.get("flame_e", 1.0))}</g>']
    sy = br * st.get("sy", 1.0)
    sx = st.get("sx", 1.0)
    o.append(f'<g transform="translate({CAT.CX} {CAT.CBOT}) scale({-sx:.4f} {sy:.4f}) translate({-CAT.CX} {-CAT.CBOT})">'
             f'{CAT.body(None, 0.0, paw, paw_dx)}</g>')
    hy = -(sy - 1) * (CAT.CBOT - CAT.NECK[1])
    o.append(f'<g transform="translate(0 {hy:.2f}) rotate({st.get("tilt", 0.0):.2f} {CAT.NECK[0]} {CAT.NECK[1]})">{CAT.head(st, t)}</g>')
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({st.get("rot", 0.0):.2f}) scale({k:.4f}) translate({-CAT.CX} {-CAT.CBOT})">{"".join(o)}</g>'


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
        if pu > .02:          # лапа на макушку: левая передняя поднимается (своя стоячая лапа не рисуется)
            cat = cat_left_paw(cx, cy, CAT_K, st, t, pu * (1 - .12 * min(1.0, tap)))
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


# ═════════════════════════ s17: призыв — рукописное «кот» на чистой стене ═════════════════════════
T_A17 = 31.70
T_NAP, T_KOT = wt(95), wt(96)                     # 31.72 кот просыпается, 32.48 пишется «кот»
LAP17 = (R.LAPTOP[0] - 110, R.LAPTOP[1])           # тот же стол, что s16
CAT17 = (1050.0, R.DESK_TOP - 28)
CAT17_K = .86
KOT_T0, KOT_DUR = T_KOT - .02, .45                 # дописано к ~32.93 (звук «слово дописано» 32.95)
KOT_XY, KOT_SIZE = (730.0, 560.0), 1.75             # чистая стена над котом (room.CLEAN_WALL)


def s17(t):
    sc = R.desk_scene(t, "day")
    lap = PR.laptop(LAP17[0], LAP17[1], .72, 1.0, "lines", lines=.95, t=t, seed=1, turn=.55)
    # кот: спит клубком (как в s16) → «Напиши» просыпается, садится и поворачивает морду к зрителю через три четверти
    wake = sm(t, T_NAP + .02, T_NAP + .5)
    tu = sm(t, T_NAP + .3, T_NAP + .7)
    cx, cy = CAT17
    st = dict(sleep=1 - wake, blink=1.0 - sm(t, T_NAP + .1, T_NAP + .3) + blinks(t, (32.75,)), turn=lerp(-.7, 0.0, tu) + .06 * bump(t, T_NAP + .7, .3),
              look=(lerp(-.6, 0.0, tu), lerp(.2, 0.0, tu)), tail=7 * math.sin(t * 2.1), ear=6 * bump(t, T_KOT + .05, .3) + 2 * math.sin(t * 3.3),
              tilt=lerp(-6, 0, tu) + 5 * bump(t, T_KOT + .2, .5), perk=.6 * bump(t, T_KOT, .55), flame_e=1.0 + .6 * wake + .5 * bump(t, T_KOT + .3, .5),
              smile=1.0 if t > T_KOT + .3 else 0.0)
    cat = CAT.draw(cx, cy, CAT17_K, st, t)
    TK = .42
    timer = PR.tomato_timer(cx - 230 * CAT17_K, table_y(TK, 30), TK, -6, wedge=.012, shake=.5, leaf_swing=5 * math.sin(t * 2.4), t=t, seed=3)
    # Дима: откинулся от ноутбука, улыбается в камеру; ближняя рука лежит на столе, дальняя на клавишах
    nod = .05 * bump(t, wt(97), .42)
    e = ex("smile_cam", closed=blinks(t, (32.2,)), look=(lerp(.3, -.35, sm(t, T_A17 - .1, T_A17 + .25)), 0))
    kc = PR.laptop_pts(LAP17[0], LAP17[1], .72, 1.0, turn=.55)["keys"]
    arms = {"f": ("ik", (kc[0] - 150, kc[1] - 26), -1), "n": ("ik", (SX + 320 * SC, R.DESK_TOP - 40 + 3 * math.sin(t * 2)), -1)}
    hands = {"f": {"dir": (1, .35), "curl": (.3, .35, .4, .45), "thumb": .3}, "n": {"dir": (1, .25), "curl": (.25, .3, .35, .4), "thumb": .3}}
    full, parts = dima_parts(e, "sit_desk", arms=arms, hands=hands, lean_add=-.02 + .01 * math.sin(t * 2.3), head_add=-.06 - nod)
    kot = hand_kot.kot(t, KOT_T0, KOT_DUR, KOT_XY[0], KOT_XY[1], KOT_SIZE)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], lap, parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"],
             parts["arm_f"], parts["body"], parts["arm_n"], sc["lamp"], cat, timer, kot]
    # камера: хлёст, лёгкий наезд; мини-удар, когда слово дописано
    u = sm(t, T_A17 - .1, 33.2)
    z = lerp(1.06, 1.15, u) + .025 * bump(t, KOT_T0 + KOT_DUR, .35)
    ccx = lerp(765, 785, u)
    ccy = lerp(930, 880, u)
    set_ink(z)
    g = f'<g transform="{lib.cam(ccx, ccy, z, lerp(.6, -.3, u))}">{"".join(world)}</g>'
    return whip(g, t, T_A17, side=1), "#e6dcc0"


FRAMES["s17"] = s17


# ═════════════════════════ s18: петля к кадру хука s01 (тот же стол и ракурс, утро) ═════════════════════════
sys.path.insert(0, os.path.join(STORY, "ext_c"))
import s70c as C1  # noqa: E402  (только чтение: та же раскладка Димы за столом и место таймера, что у s01)

T_A18 = 33.00
T_POM18, T_TEB, T_TOZH, T_NEP = wt(98), wt(99), wt(100), wt(101)      # 33.0 лапа крутит, 33.49–33.92 клин сжимается, 33.95 взгляд
TK18 = C1.TK
TIM18 = (R.HOLD[0] - 10, C1.table_y(TK18))
PAW_CLICKS = [33.05, 33.3, 33.52, 33.72, 33.9]


def s18(t):
    sc = R.desk_scene(t, "day")
    # лапа кота входит справа, цепляет бок таймера и толкает вниз — таймер проворачивается щелчками, клин тает до ломтика
    n_done = sum(1 for a in PAW_CLICKS if t >= a)
    ph = 0.0
    for a in PAW_CLICKS:
        ph += ease_out(clamp((t - a) / .12), 2)
    w0 = PR.WEDGE_25 * .5
    wedge = lerp(w0, PR.WEDGE_2, ph / len(PAW_CLICKS))
    rot = -8 * sum(bump(t, a, .2) for a in PAW_CLICKS) + 2 * math.sin(t * 3)
    click = max(bump(t, a, .1) for a in PAW_CLICKS)
    T = (TIM18[0], TIM18[1] - 5 * click)
    leaf = 12 * math.sin(2 * math.pi * 2.1 * t) + 10 * click + 16 * decay(t, PAW_CLICKS[-1] + .1, 4, 2.5)
    timer = PR.tomato_timer(T[0], T[1], TK18, rot, wedge=wedge, shake=1.0, leaf_swing=leaf, t=t, seed=1)
    tp = PR.tomato_pts(T[0], T[1], TK18, rot)
    paw_in = sm(t, T_A18 - .25, T_A18 + .05) * (1 - sm(t, 34.2, 34.55))
    paw_svg = ""
    if paw_in > .01:
        # кончик лапы ходит по правому боку: сверху вниз на каждом щелчке
        cyc = 0.0
        for a in PAW_CLICKS:
            cyc = max(cyc, bump(t, a + .05, .22))
        rx, ry = tp["right"]
        tip = (rx - 30 + 90 * (1 - paw_in), ry - 70 + 70 * cyc)
        base = (rx + 240, ry - 250 + 30 * cyc)
        paw_svg = cat_paw(base, tip, 1.05, seed=4700)
    # Дима: смотрит на таймер с улыбкой → «не помогает» переводит взгляд на зрителя
    up = sm(t, T_NEP - .02, T_NEP + .25)
    e = ex("relief_day", look=(lerp(.7, -.35, up), lerp(.45, 0.0, up)), smile=lerp(.6, 1.0, up), lid=lerp(.5, .72, up),
           closed=blinks(t, (33.4, 34.75)))
    wn = (T[0] - 250, R.DESK_TOP - 40)
    hands = {"f": {"kind": "none"}, "n": {"curl": (.3, .35, .4, .45), "thumb": .4, "dir": (1, .3)}}
    full, parts = C1.dima_layers(e, {"f": ("ang", 0.25, 0.2), "n": ("ik", wn, -1)}, hands,
                                 lean_add=.1 + .02 * math.sin(t * 2.6) - .04 * up, head_add=.08 - .08 * up + .02 * math.sin(t * 2.0))
    lap = PR.laptop(R.LAPTOP[0], R.LAPTOP[1], .72, 1.0, "lines", lines=.95, t=t, seed=1, turn=.55)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], lap, parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"],
             parts["arm_f"], parts["body"], timer, parts["arm_n"], sc["lamp"], paw_svg]
    # камера: «стол крупно» s01, ровный откат к кадру 0 хука (1/1.4 и занос), чтобы петля сошлась
    cx0, cy0, s0 = R.CAM_DESK_CLOSE
    u = sm(t, T_A18 - .2, 35.1)
    s = s0 * lerp(1.04, 1 / 1.4, u)
    cx = cx0 + 50 * u + 3 * math.sin(t * 1.7)
    cy = cy0 + 2 * math.sin(t * 1.3)
    set_ink(s)
    g = f'<g transform="{lib.cam(cx, cy, s, 2.0 * u)}">{"".join(world)}</g>'
    return g, "#e6dcc0"


FRAMES["s18"] = s18


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
