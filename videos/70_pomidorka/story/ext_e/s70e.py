"""Рилс 70 «помидорка», группа E — утро: таймер на две минуты, файл, кот спит.
s13 (22.50–24.70, хлёст): комната утром, Дима входит с кружкой, ставит её, берёт таймер двумя пальцами, хитро щурится, подносит к лицу;
    кот спит клубком на подоконнике в глубине.
s14 (24.70–27.50): циферблат крупно — пальцы доворачивают ручку на ломтик (щелчок на «минуты»), камера уходит вправо к ноутбуку,
    рука поднимает крышку, экран загорается пустой белой страницей, Дима облегчённо выдыхает, пальцы ложатся на клавиши.
s16 (29.70–31.70): общий план днём — Дима пишет в потоке; кот спит клубком в обнимку с таймером на краю стола; «кот» дёргает
    ухом, «спит» вздыхает, «рядом» Дима гладит кота одной рукой, не отрываясь от экрана.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, Дима — common/people.py, кот — common/cat.py,
таймер, ноутбук, кружка — common/props.py; здесь только хореография и камера. Надписей, букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from h70 import blinks, bump, decay, lerp, lerp2, set_ink, shake, sm, we, whip, wt  # noqa: E402
from lib import INK, blob, clamp, ease_out, ellipse_pts, line  # noqa: E402

SX, SY = R.SIT
BS = 1.0
SC = BS * people.HEIGHT["dima"]
FEET = {"n": ((SX + 300 * BS, R.FL - 52), 0.0), "f": ((SX + 250 * BS, R.FL - 50), 0.0)}
BG = "#e6dcc0"


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.setdefault("bags", False)            # утро: Дима свежий
    e.update(kw)
    return e


def dima_parts(e, arms, hands, pose="sit_desk", lean_add=0.0, head_add=0.0, x=SX, y=SY, feet=FEET):
    kw = dict(feet=feet, arms=arms, hands=hands, lean_add=lean_add, head_add=head_add)
    full = people.dima(x, y, BS, e, pose, **kw)
    parts = {k: people.dima(x, y, BS, e, pose, layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    return full, parts


def table_y(k):
    """Центр таймера, стоящего на столе (дно на середине глубины столешницы)."""
    return R.DESK_TOP - 42 - PR.TOMATO_RY * k


def type_hand(t, base, phase, k=SC, far=False, seed=0):
    """Кисть печатает: запястье чуть ходит, пальцы по очереди бьют по клавишам."""
    ph = t * 9.5 + phase
    W = (base[0] + 7 * math.sin(ph * .7), base[1] - 4 * abs(math.sin(ph)))
    curl = tuple(.35 + .25 * max(0.0, math.sin(ph + i * 1.7)) for i in range(4))
    return W, {"dir": (1, .32), "curl": curl, "thumb": .35, "spread": .12, "bend": .1}


# ═════════════════════════ s16: общий план днём ═════════════════════════
T_A16 = 29.70
T_KOT16, T_SPIT, T_RYAD = wt(92), wt(93), wt(94)       # 30.48 ухо, 30.77 вздох, 31.01 гладит
LAP16 = (R.LAPTOP[0] - 110, R.LAPTOP[1])
LAP16_K = .72
CAT16 = (1050.0, R.DESK_TOP - 28)                       # середина низа клубка на столешнице
CAT16_K = .86


def s16(t):
    sc = R.desk_scene(t, "day")
    lp = PR.laptop_pts(LAP16[0], LAP16[1], LAP16_K, 1.0, turn=.55)
    lines = clamp(.55 + (t - 29.5) * .16)
    lap = PR.laptop(LAP16[0], LAP16[1], LAP16_K, 1.0, "lines", lines=lines, t=t, seed=1, turn=.55)
    # кот клубком, обнял таймер передними лапами (таймер у его морды, лапы поверх)
    cx, cy = CAT16
    sigh = bump(t, T_SPIT - .05, .9)
    st = dict(breath=1.0 + 1.6 * sigh, ear=9 * bump(t, T_KOT16, .22) - 7 * bump(t, T_KOT16 + .2, .2), flame_e=.85 + .25 * math.sin(t * 3.1) + .2 * sigh,
              tail=4 * math.sin(t * 1.3), squint=.6 * sm(t, T_RYAD + .1, T_RYAD + .4))
    TK = .42
    tm = (cx - 250 * CAT16_K, cy - 40 * CAT16_K - 3 * sigh)
    timer = PR.tomato_timer(tm[0], tm[1], TK, -14 + 3 * sigh, wedge=.03 * (1 - clamp((t - 29.5) / 2.5)), shake=.6, leaf_swing=6 * math.sin(t * 2.2), t=t, seed=3)
    cat = CAT.curl(cx, cy, CAT16_K, st, t)
    # ближние лапы поверх таймера — копия кота, обрезанная по лапам
    pc = lib.uid("pw")
    lib.DEFS.append(f'<clipPath id="{pc}"><path d="{lib.fill_d(ellipse_pts(cx - 190 * CAT16_K, cy - 14 * CAT16_K, 44 * CAT16_K, 28 * CAT16_K, 16))}"/></clipPath>')
    paws_over = f'<g clip-path="url(#{pc})">{cat}</g>'
    shadow = blob(ellipse_pts(cx + 10, cy + 2, 150, 12, 16), "#7a5236", .25)
    # Дима печатает дальней рукой всё время; ближняя печатает, на «рядом» уходит гладить кота по голове и спине
    kc = lp["keys"]
    Wf, hf = type_hand(t, (kc[0] - 130, kc[1] - 26), 0.0)
    Wn0, hn0 = type_hand(t, (kc[0] - 85, kc[1] - 14), 1.9)
    go = sm(t, T_RYAD - .25, T_RYAD + .12)
    ph = max(0.0, t - (T_RYAD + .12))
    strokev = .5 - .5 * math.cos(2 * math.pi * ph / .8)            # ладонь по голове → по спине и обратно
    head_c = (cx - 60 * CAT16_K, cy - 150 * CAT16_K)
    back_c = (cx + 90 * CAT16_K, cy - 130 * CAT16_K)
    pet = lerp2(head_c, back_c, strokev * .9)
    Wpet = (pet[0] - 95 * SC, pet[1] + 8 - 6 * math.sin(2 * math.pi * ph / .8))
    Wn = lerp2(Wn0, Wpet, go)
    hn = hn0 if go < .5 else {"dir": (1, .16), "curl": (.12, .15, .2, .25), "thumb": .15, "spread": .16, "bend": .25}
    e = ex("focus", brows="calm", mouth="smile", smile=.55 + .15 * math.sin(t * 1.3), lid=.62, look=(.6, .5),
           closed=blinks(t, (30.1, 31.45)))
    full, parts = dima_parts(e, {"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, {"f": hf, "n": hn},
                             lean_add=.12 + .015 * math.sin(t * 2.3) + .05 * go, head_add=.04 + .02 * math.sin(t * 1.9))
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], lap, shadow, cat, timer, paws_over, parts["legs"], sc["desk_legs"],
             sc["chair_seat"], parts["pelvis"], parts["arm_f"], parts["body"], parts["arm_n"], sc["lamp"]]
    # слова пишутся: мелкие штрихи «мысли» не нужны — экран сам растёт; вздох кота — две дуги над спиной
    if sigh > .05:
        for j in (0, 1):
            q = clamp(sigh * 1.6 - j * .3)
            if q > 0:
                y0 = cy - 170 * CAT16_K - 30 * q - j * 22
                world.append(line([(cx - 10 + j * 30, y0), (cx + 20 + j * 30, y0 - 12), (cx + 50 + j * 30, y0)], 4, INK, taper=.5, wmin=.2,
                                  seed=880 + j, op=q * (1 - q) * 3.5 if q < 1 else 0))
    # камера: медленный откат, «дыхание»
    u = sm(t, T_A16 - .2, 31.9)
    s = lerp(1.1, 1.0, u) + .01 * math.sin(t * 2.1)
    ccx = lerp(735, 712, u) + 5 * math.sin(t * 1.4)
    ccy = lerp(990, 1020, u) + 4 * math.sin(t * 1.7)
    set_ink(s)
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(.5, -.3, u))}">{"".join(world)}</g>', BG


FRAMES = {"s16": s16}


# ═════════════════════════ s13: утро, входит с кружкой, берёт таймер двумя пальцами ═════════════════════════
T_A13 = 22.50
T_POT, T_TEP, T_STAV, T_TAIM = wt(69), wt(70), wt(72), wt(73)    # 22.53 входит, 23.49 кружку на стол, 24.05 берёт, 24.36 к лицу
HIP13_Y = R.FL - 52 - (people.LEG_LEN - 12) * SC
X13_IN, X13_STOP = -60.0, 420.0
T_WALK1 = 23.20
MUG13 = (745.0, R.DESK_TOP - 98)          # где встанет кружка (дно)
MUG_K = .62
TIM13 = (R.TIMER_DESK[0], table_y(.5))    # таймер на столе
TK13 = .5
CAT_SILL = (-185.0, R.WIN_TALL[3] - 2)     # кот клубком на подоконнике высокого окна
CAT_SILL_K = .42


def pinch_hand(W, d, k=SC):
    """Щепоть: указательный и большой держат хвостик, остальные поджаты."""
    return {"dir": d, "curl": (.45, .85, .9, .92), "thumb": .75, "spread": .04, "bend": .05}


def s13(t):
    sc = R.desk_scene(t, "day")
    # походка: от левого края к столу, на T_WALK1 встаёт
    wu = clamp((t - (T_A13 - .25)) / (T_WALK1 - (T_A13 - .25)))
    x = lerp(X13_IN, X13_STOP, 1 - (1 - wu) ** 1.6)
    if wu < 1:
        wk = people.walk_kw(x, HIP13_Y, BS, (x - X13_IN) / 470.0, stride=200.0, lift=50.0)
        feet, hip = wk["feet"], wk["hip"]
    else:
        feet, hip = people.stand_kw(x, HIP13_Y, BS)["feet"], (x, HIP13_Y + 3 * math.sin(t * 2.2))
    hx, hy = hip
    # ближняя рука: кружка у груди → ставит на стол (T_TEP) → отпускает → щепотью берёт таймер за хвостик → к лицу
    m_carry = (hx + 175 * SC, hy - 215 * SC + 6 * math.sin(t * 9) * (1 - wu))
    put = sm(t, T_TEP - .35, T_TEP + .05)
    mug_p = lerp2(m_carry, MUG13, put)
    mug_p = (mug_p[0], mug_p[1] - 30 * math.sin(math.pi * put))
    hc = (mug_p[0] + 88 * MUG_K, mug_p[1] - 70 * MUG_K)               # ручка кружки
    rel = sm(t, T_TEP + .08, T_TEP + .3)
    stem = PR.tomato_pts(TIM13[0], TIM13[1], TK13)["top"]
    grab = sm(t, T_TEP + .3, T_STAV - .05)                              # рука идёт к таймеру
    lift = sm(t, T_STAV + .05, T_TAIM + .2)
    face = (hx + 340 * SC, hy - 370 * SC)
    stem_up = lerp2((stem[0], stem[1] - 12), (face[0], face[1] + 40), lift)
    stem_up = (stem_up[0] + 4 * math.sin(t * 6) * lift, stem_up[1] - 18 * bump(t, T_STAV + .02, .25))
    d_pinch = (.25, 1.0)
    Wpinch = (stem_up[0] - 118 * SC * .25, stem_up[1] - 118 * SC * .97)
    W_mug = (hc[0] + 58 * SC, hc[1] + 26 * SC)
    if rel < 1:
        Wn = lerp2(W_mug, (W_mug[0] - 10, W_mug[1] - 60), rel)
        hn = {"kind": "none"} if rel < .5 else {"dir": (.6, .8), "curl": (.3, .3, .35, .4), "thumb": .3}
    else:
        Wn = lerp2((W_mug[0] - 10, W_mug[1] - 60), Wpinch, grab)
        hn = pinch_hand(Wn, d_pinch) if grab > .6 else {"dir": (.4, .9), "curl": (.3, .4, .5, .55), "thumb": .5}
    # дальняя рука: качается в шаге, потом опирается о спинку стула
    swing = .25 * math.sin(2 * math.pi * (x - X13_IN) / 470.0) * (1 - wu)
    arms = {"f": ("ang", .15 + swing, .25), "n": ("ik", Wn, -1)}
    # мимика: бодро → хитрый прищур на «ставит» → к лицу — прищур и полуулыбка
    sq = sm(t, T_STAV - .1, T_STAV + .25)
    e = ex("cheerful", look=(lerp(.45, .55, grab), lerp(0, .5, grab * (1 - lift))), closed=blinks(t, (22.95,)))
    if sq > 0:
        e = ex("smug", lid=lerp(.8, .38, sq), smile=.7, mouth="side", brows="one_up" if sq > .5 else "calm",
               look=(lerp(.55, .35, lift), lerp(.5, .05, lift)))
    lean = .05 + .06 * grab * (1 - lift) + .02 * math.sin(t * 2)
    full = people.dima(hx, hy, BS, e, None, feet=feet, arms=arms, hands={"f": {"curl": (.3, .35, .4, .45), "thumb": .3}, "n": hn},
                       lean_add=lean, head_add=.04 * math.sin(t * 2.6) - .05 * lift)
    body = people.dima(hx, hy, BS, e, None, feet=feet, arms=arms, hands={"n": hn}, lean_add=lean, head_add=.04 * math.sin(t * 2.6) - .05 * lift,
                       layers=("legs", "pelvis", "arm_f", "body"))["svg"]
    arm_n = people.dima(hx, hy, BS, e, None, feet=feet, arms=arms, hands={"n": hn}, lean_add=lean, head_add=.04 * math.sin(t * 2.6) - .05 * lift,
                        layers=("arm_n",))["svg"]
    # кружка (пар), хват за ручку
    steam = .8
    mug = PR.coffee_mug(mug_p[0], mug_p[1], MUG_K, 0, "white", 1.0, steam, t, seed=2)
    gb = gf = ""
    if rel < .5:
        gb, gf = people.handle_grip("dima", hc, k=SC * .62, side=1, seed=961)
    # таймер: на столе (тикает чуть), потом висит на хвостике в щепоти, качается
    swing_t = 9 * math.sin(2 * math.pi * 1.6 * (t - T_STAV)) * math.exp(-1.5 * max(0.0, t - T_STAV - .1)) * (lift > 0)
    if lift <= 0:
        tc = TIM13
        trot = 0.0
    else:
        a = math.radians(swing_t)
        L = (TIM13[1] - stem[1])
        tc = (stem_up[0] - math.sin(a) * L, stem_up[1] + math.cos(a) * L)
        trot = swing_t
    timer = PR.tomato_timer(tc[0], tc[1], TK13, trot, wedge=.0, shake=.5 if lift <= 0 else 0, leaf_swing=4 * math.sin(t * 3), t=t, seed=5)
    lap = PR.laptop(R.LAPTOP[0], R.LAPTOP[1], .72, 0.0, "dark", t=t, seed=1, turn=.55)
    # кот спит на подоконнике в глубине
    cat = CAT.curl(CAT_SILL[0], CAT_SILL[1], CAT_SILL_K, dict(breath=1.0, flame_e=.8, tail=3 * math.sin(t * 1.2)), t)
    world = [sc["bg"], cat, sc["chair_back"], sc["desk_top"], sc["chair_seat"], sc["desk_legs"], lap, body, gb, mug] + ([gf, arm_n, timer] if lift > .25 else [timer, gf, arm_n]) + [sc["lamp"]]
    # камера: хлёст, дрейф влево, лёгкий наезд на руки с таймером
    u = sm(t, T_A13 - .2, 24.9)
    z = sm(t, T_STAV, 24.9)
    s = lerp(.96, 1.04, u) + .26 * z
    ccx = lerp(350, 300, u) + 220 * z
    ccy = lerp(930, 900, u) - 170 * z
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.6, .4, u))}">{"".join(world)}</g>'
    return whip(g, t, T_A13), BG


FRAMES["s13"] = s13


# ═════════════════════════ s14: циферблат крупно → ноутбук, пустая страница ═════════════════════════
T_A14 = 24.70
T_NA, T_MIN14, T_PROS, T_OTKR, T_FILE = wt(74), wt(76), wt(78), wt(79), wt(80)   # 24.67, 24.95 щелчок, 25.57, 25.88, 26.46
TK14 = .55
TIM14 = (R.TIMER_DESK[0], table_y(TK14))
LAP_K = .72


def timer_grip(T, k, rot, side=-1, seed=0):
    """Пальцы обхватили таймер сбоку (ладонь за ним, пальцы и большой палец спереди по краю): (back, front, запястье)."""
    rr = math.radians(rot)
    lx, ly = side * (PR.TOMATO_RX - 52) * k, 22 * k
    cx = T[0] + lx * math.cos(rr) - ly * math.sin(rr)
    cy = T[1] + lx * math.sin(rr) + ly * math.cos(rr)
    b, f_ = people.grip_svg("dima", (cx, cy), 52 * k, side, k=k * 1.05, h=64, seed=930 + seed)
    return b, f_, (cx + side * 112 * k, cy + 40 * k)


def s14(t):
    sc = R.desk_scene(t, "day")
    # таймер: пальцы доворачивают ручку — клин растёт до тонкого ломтика, щелчок на «минуты»
    tw = sm(t, T_NA - .05, T_MIN14)
    wedge = PR.WEDGE_2 * tw + .004 * math.sin(t * 40) * (tw > 0) * (t < T_MIN14)
    click = bump(t, T_MIN14, .14)
    rot = -10 * tw + 10 * sm(t, T_MIN14, T_MIN14 + .12) - 3 * click
    rel = sm(t, T_MIN14 + .25, T_MIN14 + .45)
    T = (TIM14[0], TIM14[1] - 6 * click)
    timer = PR.tomato_timer(T[0], T[1], TK14, rot, wedge=wedge, shake=1.4 * (t > T_MIN14 + .1), leaf_swing=10 * math.sin(t * 3.3) + 14 * click,
                            t=t, seed=7)
    gb, gf, Wgrip = timer_grip(T, TK14, rot, side=-1)
    if rel >= .5:
        gb = gf = ""
    # ноутбук: крышка поднимается на «и просто», экран тёмный → на «файл» белая пустая страница
    lid = ease_out(clamp((t - (T_PROS - .1)) / (T_OTKR + .2 - (T_PROS - .1))), 2.2)
    page = sm(t, T_FILE - .06, T_FILE + .1)
    lp = PR.laptop_pts(R.LAPTOP[0], R.LAPTOP[1], LAP_K, lid, turn=.55)
    lap = PR.laptop(R.LAPTOP[0], R.LAPTOP[1], LAP_K, lid, "page" if page > .5 else "dark", t=t, seed=1, turn=.55, glow=page * (1 - .6 * sm(t, T_FILE + .2, T_FILE + .8)))
    # ближняя рука: держит таймер → к краю крышки → поднимает → пальцы на клавиши
    lt = lp["lid_top"]
    W_lid = (lt[0] - 120 * SC, lt[1] + 30 * SC)
    kc = lp["keys"]
    W_keys = (kc[0] - 110, kc[1] - 6)
    go_lid = sm(t, T_MIN14 + .3, T_PROS - .05)
    keys_u = sm(t, T_OTKR + .22, T_OTKR + .55)
    W_back = lerp2(Wgrip, (Wgrip[0] + 20, Wgrip[1] - 60), rel)
    Wn = lerp2(lerp2(W_back, W_lid, go_lid), W_keys, keys_u)
    if rel < .5:
        hn = {"kind": "none"}
    elif keys_u > .5:
        Wn, hn = type_hand(t, W_keys, .7) if t > T_OTKR + .6 else (Wn, {"dir": (1, .3), "curl": (.3, .3, .35, .4), "thumb": .3})
    else:
        hn = {"dir": (.85, -.4 * lid), "curl": (.55, .6, .62, .65), "thumb": .55}
    Wf = lerp2((SX + 170 * SC, SY - 50 * SC), (kc[0] - 180, kc[1] - 20), sm(t, T_FILE, T_FILE + .5))
    # лицо: сосредоточенно на таймер → на экран → облегчённый выдох
    rlf = sm(t, T_FILE + .05, T_FILE + .4)
    e = ex("focus", look=(lerp(.75, .6, go_lid), lerp(.7, .2, go_lid)), lid=.7, closed=blinks(t, (25.3,)))
    if rlf > 0:
        e = ex("relief", lid=lerp(.7, .45, rlf), smile=.75 * rlf, look=(.6, .25), mouth="o" if bump(t, T_FILE + .25, .55) > .3 else "smile",
               open=.25 * bump(t, T_FILE + .25, .55))
    full, parts = dima_parts(e, {"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, {"f": {"curl": (.3, .3, .35, .4), "thumb": .3, "dir": (1, .3)}, "n": hn},
                             lean_add=.1 + .05 * go_lid - .04 * rlf + .015 * math.sin(t * 2.2), head_add=.08 * (1 - go_lid) - .06 * rlf)
    # выдох: две мягкие дуги у рта
    puff = ""
    q = clamp((t - T_FILE - .2) / .6)
    if 0 < q < 1:
        hx, hy = full["head"]
        for j in (0, 1):
            x0 = hx + 150 + 50 * q + j * 16
            y0 = hy + 70 + j * 26
            puff += line([(x0, y0 - 14), (x0 + 18, y0), (x0, y0 + 14)], 4.5, "#8fa3b8", taper=.5, wmin=.2, seed=890 + j, op=math.sin(math.pi * q))
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], lap, parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"],
             parts["arm_f"], parts["body"], gb, timer, gf, parts["arm_n"], puff, sc["lamp"]]
    # камера: наезд на циферблат, щелчок — мини-удар; на «и просто» панорама вправо-вверх к ноутбуку и лицу
    dial = PR.tomato_pts(T[0], T[1], TK14, rot)["dial"]
    pan = sm(t, T_PROS - .15, T_OTKR + .35)
    z0 = lerp(4.0, 4.5, sm(t, T_A14 - .2, T_MIN14)) * (1 + .04 * click)
    s = lerp(z0, 1.62, ease_out(pan, 1.6)) + .02 * math.sin(t * 1.8)
    ccx = lerp(dial[0], 700, pan) + 6 * math.sin(t * 1.3)
    ccy = lerp(dial[1], 760, pan) + 5 * math.sin(t * 1.6)
    sx_, sy_ = shake(t, T_MIN14, 3)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx + sx_, ccy + sy_, s, lerp(-1.0, .6, pan))}">{"".join(world)}</g>'
    return g, BG


FRAMES["s14"] = s14


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
