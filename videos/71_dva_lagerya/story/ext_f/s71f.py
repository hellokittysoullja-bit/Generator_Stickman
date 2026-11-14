"""Рилс 71 «два лагеря», группа F — кот, облегчение, призыв.
s08 (12.92–14.30): кровать средним планом; «и дело» Дима поднимает голову из кокона, «не в лени» кокон сползает с плеч, выдох облегчения;
    на «лени» кот на подоконнике в глубине поднимает голову и дёргает ухом.
s13 (23.10–24.95): Дима сидит на полу у «стены», подбородок на кулаке; «Он нашёл» кот лапой подталкивает полосатый носок, «свой способ»
    Дима хитро прищуривается, кот садится и щурится.
s20 (32.74–34.48): кот на столе рядом с ноутбуком, Дима печатает позади; «кот» поворачивает морду, «смотрит» медленно щурится,
    «одобрительно» кивает, огонёк вспыхивает.
s21 (34.48–36.40, хлёст): призыв — Дима и кот на кровати смотрят на зрителя, на стене два флажка лагерей, пером пишется «кот».
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, Дима — common/people.py, кот — common/cat.py,
предметы — common/props.py, «кот» — common/hand_kot.py; здесь только хореография и камера. Надписей, букв и цифр нет (кроме «кот»)."""
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
from h71 import bare_feet, blinks, laptop_side, bump, decay, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
from lib import INK, blob, clamp, ease_out, ellipse_pts, line  # noqa: E402

BG = "#e6dcc0"
FRAMES = {}


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.setdefault("bags", False)
    e.update(kw)
    return e


def flame_world(x, y, k, tail_deg, sleep=0.0):
    """Где огонёк кота в мире (основание пламени) — для свечения поверх."""
    bx, by = CAT.FLAME_BASE
    px, py = CAT.TAIL_PIVOT
    a = math.radians(tail_deg + 14 * sleep)
    dx, dy = bx - px, by - py
    rx, ry = px + dx * math.cos(a) - dy * math.sin(a), py + dx * math.sin(a) + dy * math.cos(a)
    return x + (rx - CAT.CX) * k, y + (ry - CAT.CBOT) * k


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')


# ═════════════════════════ s20: кот на столе одобряет ═════════════════════════
T_A20 = 32.74
T_I20, T_KOT20, T_SMOT, T_ODOB = wt(98), wt(99), wt(100), wt(101)      # 32.68, 32.80, 33.08, 33.47
CAT20 = (1005.0, R.DESK_TOP + 6)          # кот на ближнем крае стола, ближе к камере (крупнее мира)
CAT20_K = 1.75
SX20, SY20 = R.SIT
FEET20 = {"n": ((SX20 + 300, R.FL - 52), 0.0), "f": ((SX20 + 250, R.FL - 50), 0.0)}
LAP20 = (565.0, R.DESK_TOP - 66)
LAP20_K = .74


def type_hand(t, base, phase):
    ph = t * 9.5 + phase
    W = (base[0] + 7 * math.sin(ph * .7), base[1] - 4 * abs(math.sin(ph)))
    curl = tuple(.35 + .25 * max(0.0, math.sin(ph + i * 1.7)) for i in range(4))
    return W, {"dir": (1, .32), "curl": curl, "thumb": .35, "spread": .12, "bend": .1}


def s20(t):
    sc = R.desk_scene(t, "day")
    lp = laptop_side(LAP20[0], LAP20[1], LAP20_K, 1.0, on=1.0, lines=clamp(.6 + (t - 32.5) * .15), t=t, seed=1)
    kc = lp["keys"]
    Wf, hf = type_hand(t, (kc[0] - 70, kc[1] + 2), 0.0)
    Wn, hn = type_hand(t, (kc[0] - 20, kc[1] + 10), 1.9)
    e = ex("focus_smile" if "focus_smile" in people.EXPR["dima"] else "focus", look=(.6, .45), lid=.62, closed=blinks(t, (33.2, 34.3)))
    kw = dict(feet=FEET20, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, hands={"f": hf, "n": hn},
              lean_add=.12 + .015 * math.sin(t * 2.3), head_add=.04 + .02 * math.sin(t * 1.9))
    with bare_feet("sock", "sock"):
        parts = {k: people.dima(SX20, SY20, 1.0, e, "type", layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    # кот: смотрит в камеру → «кот» поворачивает морду к Диме (через три четверти) → «смотрит» медленно щурится → «одобрительно» кивок,
    # огонёк вспыхивает и снова горит мягко
    tu = sm(t, T_KOT20 - .04, T_KOT20 + .3)
    sq = sm(t, T_SMOT, T_SMOT + .38) * (1 - .55 * sm(t, T_ODOB + .5, T_ODOB + .75))
    nod = bump(t, T_ODOB + .02, .5)
    flare = bump(t, T_ODOB + .12, .75)
    tail = -13 + 5 * math.sin(t * 2.2) + 8 * nod
    st = dict(turn=lerp(.15, -.75, tu), look=(lerp(.1, -.85, tu), lerp(0.0, .15, tu)), tilt=lerp(0, -6, tu) + 3 * math.sin(t * 1.6),
              blink=max(.62 * sq, blinks(t, (32.62,))), smile=1.0 if sq > .4 else 0.0, drop=.32 * nod, tail=tail,
              ear=-6 * bump(t, T_KOT20, .25) + 2 * math.sin(t * 3.1), flame_e=1.0 + 1.4 * flare, perk=.3 * bump(t, T_KOT20, .4))
    cx, cy = CAT20
    cat = CAT.draw(cx, cy, CAT20_K, st, t)
    fx, fy = flame_world(cx, cy, CAT20_K, tail)
    fl = PR.glow(fx, fy - 50, 70 + 50 * flare, .45 + .5 * flare, "#ffb347") + PR.sparkles(fx, fy - 70, .9, flare, t, seed=7, n=4, r=70)
    shadow = blob(ellipse_pts(cx, cy + 2, 180, 14, 16), "#7a5236", .25)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"],
             parts["arm_f"], parts["body"], lp["svg"], parts["arm_n"], shadow, cat, fl]
    # камера: лёгкий наезд на кота, мини-подскок на кивке
    u = sm(t, T_A20 - .2, 34.68)
    s = lerp(1.02, 1.13, u) + .01 * math.sin(t * 2)
    ccx = lerp(770, 792, u) + 4 * math.sin(t * 1.4)
    ccy = lerp(850, 790, u) + 3 * math.sin(t * 1.7) + 6 * nod
    set_ink(s)
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(.4, -.3, u))}">{"".join(world)}</g>', BG


FRAMES["s20"] = s20


# ═════════════════════════ s21: призыв — кровать, флажки лагерей, рукописное «кот» ═════════════════════════
T_A21 = 34.48
T_NAP21, T_IZ, T_KAK, T_LAG = wt(102), wt(103), wt(104), wt(106)      # 34.56, 35.09, 35.24, 35.64
KOT_T0, KOT_DUR = 35.2, .6                                              # дописано на 35.8 (звук level_up)
DIMA21 = (1560.0, R.DR_BED_TOP - 8)
FEET21 = {"n": ((1560 + 300, R.FL - 52), 0.0), "f": ((1560 + 250, R.FL - 50), 0.0)}
CAT21 = (2110.0, R.DR_BED_TOP - 30)
CAT21_K = .95
KOT21 = (1925.0, 760.0, 1.32)            # чистая стена DR_CLEAN над котом, между флажками


def s21(t):
    sc = R.day_room(t)
    F1, F2 = R.DR_FLAGS
    # Дима: сидит на краю кровати, улыбается зрителю; «какого» — ближней рукой на жёлтый флажок, «лагеря» — на синий
    p1 = sm(t, T_KAK - .22, T_KAK + .02) * (1 - sm(t, T_LAG - .3, T_LAG - .12))
    p2 = sm(t, T_LAG - .2, T_LAG + .04) * (1 - sm(t, 36.2, 36.5))
    hx, hy = DIMA21
    rest_n = (hx + 250, hy - 40 + 3 * math.sin(t * 2))
    tgt1 = (hx + 235, hy - 410)          # кисть у плеча, палец вверх-вправо на жёлтый флажок
    tgt2 = (hx + 255, hy - 340)          # палец вправо-вверх на синий: рука не заходит на слово «кот»
    Wn = lerp2(rest_n, tgt1, p1) if p1 >= p2 else lerp2(rest_n, tgt2, p2)
    pt = max(p1, p2)
    fl = F1 if p1 >= p2 else F2
    tg_ = tgt1 if p1 >= p2 else tgt2
    hand_pt = {"dir": (fl[0] - tg_[0], fl[1] + 40 - tg_[1]),
               "curl": (0.0, .85, .9, .92), "thumb": .7, "spread": .05}
    hn = hand_pt if pt > .45 else {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}
    look = (lerp(-.1, -.35, sm(t, T_A21 - .2, T_A21 + .2)), 0.0)
    if pt > .3:
        look = (.35 if p1 >= p2 else .8, -.75)
    e = ex("smile_cam", look=look, closed=blinks(t, (34.9, 36.25)))
    arms = {"f": ("ik", (hx + 200, hy - 30), -1), "n": ("ik", Wn, -1)}
    hands = {"f": {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}, "n": hn}
    with bare_feet("sock", "sock"):         # оба носка уже надеты (s17, s19)
        dima = people.dima(hx, hy, 1.0, e, None, feet=FEET21, arms=arms, hands=hands, lean_add=-.03 + .015 * math.sin(t * 2.1) - .04 * pt,
                           head_add=-.05 - .1 * pt + .02 * math.sin(t * 1.7))["svg"]
    # кот: смотрит на Диму → «Напиши» поворачивает морду к зрителю, ухо, хвост; когда слово дописано — щурится
    tu = sm(t, T_NAP21 - .02, T_NAP21 + .3)
    done = sm(t, KOT_T0 + KOT_DUR, KOT_T0 + KOT_DUR + .25)
    tail = -6 + 7 * math.sin(t * 2.3)
    st = dict(turn=lerp(-.7, 0.0, tu), look=(lerp(-.8, 0.0, tu), lerp(.1, -.05, tu)), tilt=lerp(-6, 0, tu) + 5 * bump(t, KOT_T0 + KOT_DUR, .5),
              blink=max(blinks(t, (35.05,)), .5 * done), smile=1.0 if done > .3 or tu > .8 else 0.0, tail=tail,
              ear=6 * bump(t, T_NAP21 + .05, .3) + 2 * math.sin(t * 3.3), perk=.5 * bump(t, T_NAP21, .5), flame_e=1.0 + .5 * done)
    cat = CAT.draw(CAT21[0], CAT21[1], CAT21_K, st, t)
    kot = hand_kot.kot(t, KOT_T0, KOT_DUR, KOT21[0], KOT21[1], KOT21[2])
    world = [sc["bg"], sc["desk"], sc["stand"], sc["bed"], kot, dima, cat, sc["front"]]
    # камера: хлёст, лёгкий наезд к перу и котам; мини-удар, когда слово дописано
    u = sm(t, T_A21 - .1, 36.6)
    z = lerp(1.0, 1.08, u) + .025 * bump(t, KOT_T0 + KOT_DUR, .35)
    ccx = lerp(1900, 1915, u) + 4 * math.sin(t * 1.3)
    ccy = lerp(1000, 960, u) + 3 * math.sin(t * 1.6)
    set_ink(z)
    g = f'<g transform="{lib.cam(ccx, ccy, z, lerp(.5, -.3, u))}">{"".join(world)}</g>'
    return whip(g, t, T_A21, side=1), BG


FRAMES["s21"] = s21


# ═════════════════════════ s08: «и дело не в лени» — кокон сползает с плеч ═════════════════════════
T_A08 = 12.92
T_I08, T_DELO, T_NE08, T_LENI = wt(37), wt(38), wt(39), wt(41)       # 12.94, 13.02, 13.31, 13.48
COC08 = (660.0, R.BM_SIT[1] + 380)       # дно кокона (Дима сидит на краю кровати, ступни на полу)
CAT08 = (250.0, R.BM_SILL[1] + 4)
CAT08_K = .82


def s08(t):
    sc = R.bed_mid(t)
    # Дима: голова поникла под капюшоном → «и дело» выпрямляется, лицо светлеет → «не в лени» одеяло сползает с плеч до пояса, выдох
    up = sm(t, T_I08 - .05, T_DELO + .2)
    sag = .05 + .33 * ease_out(clamp((t - (T_NE08 - .05)) / (T_LENI + .32 - (T_NE08 - .05))), 2.2)
    sag += .012 * math.sin(t * 7) * (sag < .37)
    rel = sm(t, T_LENI - .05, T_LENI + .3)
    if rel > .02:
        e = ex("relief71" if "relief71" in people.EXPR["dima"] else "relief_day", closed=lerp(0, .75, bump(t, T_LENI + .2, .7)), look=(.2, .05))
    elif up > .4:
        e = ex("hope" if "hope" in people.EXPR["dima"] else "surprise_day", look=(.3, -.1), closed=blinks(t, (13.12,)))
    else:
        e = ex("gloom", look=(.3, .6), cover=.35 * (1 - up))
    coc = people.dima_cocoon(COC08[0], COC08[1], 1.0, squash=.22 * (1 - up) + .05 * bump(t, T_LENI + .05, .3), sag=sag, expr=e, hood=True, t=t,
                             feet=1.0, roll=20 * sag, hold=sm(t, T_NE08 + .12, T_LENI + .3))
    # выдох: две мягкие дуги у рта
    puff = ""
    q = clamp((t - T_LENI - .12) / .6)
    if 0 < q < 1:
        hx, hy = coc["head"]
        for j in (0, 1):
            x0 = hx + 140 + 50 * q + j * 16
            y0 = hy + 60 + j * 26
            puff += line([(x0, y0 - 14), (x0 + 18, y0), (x0, y0 + 14)], 4.5, "#8fa3b8", taper=.5, wmin=.2, seed=890 + j, op=math.sin(math.pi * q))
    # кот на подоконнике дремлет сидя (голова опущена) → «лени» поднимает голову, дёргает ухом, смотрит на Диму
    wk = sm(t, T_LENI - .05, T_LENI + .3)
    st = dict(sleep=lerp(.85, 0.0, wk), blink=lerp(1.0, 0.0, sm(t, T_LENI, T_LENI + .2)) + blinks(t, (14.25,)), turn=lerp(.2, .55, wk),
              look=(lerp(0, .8, wk), .1), ear=-10 * bump(t, T_LENI + .12, .18) + 7 * bump(t, T_LENI + .3, .16), perk=.4 * bump(t, T_LENI + .1, .5),
              tail=4 * math.sin(t * 1.6), flame_e=.8 + .4 * wk)
    cat = CAT.draw(CAT08[0], CAT08[1], CAT08_K, st, t)
    world = [sc["bg"], cat, sc["bed"], coc["svg"], puff, sc["front"]]
    # камера: лёгкий отъезд и мягкий подъём
    u = sm(t, T_A08 - .2, 14.5)
    s = lerp(1.12, 1.02, u) + .006 * math.sin(t * 2.1)
    ccx = lerp(600, 580, u) + 4 * math.sin(t * 1.5)
    ccy = lerp(1010, 950, u) + 3 * math.sin(t * 1.8)
    set_ink(s)
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.5, .3, u))}">{"".join(world)}</g>', BG


FRAMES["s08"] = s08


# ═════════════════════════ s13: на полу у стены, кот подталкивает носок ═════════════════════════
T_A13 = 23.10
T_ON, T_NASH, T_SVOI, T_SPOS = wt(73), wt(74), wt(75), wt(76)          # 23.23, 23.48, 23.82, 24.14
HIP13 = (1290.0, R.FL - 72)
FEET13 = {"n": ((1290 + 300, R.FL - 50), .05), "f": ((1290 + 265, R.FL - 48), .05)}
CAT13_K = .85
CAT13_X0, CAT13_X1 = 1900.0, 1820.0          # кот на переднем плане (ближе к камере, ниже линии ступней)
CAT13_Y = R.FL + 70
SOCK13_0, SOCK13_1 = (1715.0, R.FL + 52), (1590.0, R.FL + 40)


def s13(t):
    sc = R.day_room(t)
    # кот: входит шагом справа → «нашёл» лапа толкает носок влево → садится и довольно щурится
    walk = sm(t, T_A13 - .25, T_NASH - .12)
    cx = lerp(CAT13_X0 + 120, CAT13_X1, walk)
    push = bump(t, T_NASH - .02, .42)
    slide = ease_out(clamp((t - (T_NASH + .08)) / .35), 2.4)
    sit = sm(t, T_SVOI, T_SVOI + .35)
    pleased = sm(t, T_SPOS, T_SPOS + .3)
    st = dict(turn=lerp(-.6, -.2, sit), look=(lerp(-.8, -.5, sit), lerp(.5, .1, sit)), tilt=lerp(-8, 4, sit) + 2 * math.sin(t * 1.5),
              blink=max(.6 * pleased, blinks(t, (23.35,))), smile=1.0 if pleased > .3 else 0.0, tail=-14 + 6 * math.sin(t * 2.4),
              ear=4 * math.sin(t * 3.3) - 6 * bump(t, T_NASH + .1, .2), flame_e=1.0 + .3 * pleased, sy=1 - .04 * push)
    if walk < 1:
        st["walk"] = (t - T_A13) / .42
        st["rot"] = 2.0 * math.sin(2 * math.pi * (t - T_A13) / .42)
    if push > .02:
        st["paw"] = push
        st["paw_dx"] = -85.0
    cat = CAT.draw(cx, CAT13_Y - 4 * abs(math.sin(math.pi * (t - T_A13) / .42)) * (walk < 1), CAT13_K, st, t)
    sx_, sy_ = lerp2(SOCK13_0, SOCK13_1, slide)
    sock = PR.striped_sock(sx_, sy_ - 6 * bump(t, T_NASH + .1, .3), .62, -6 * bump(t, T_NASH + .1, .35) + 4 * slide, seed=3)
    # Дима: сидит на полу, подбородок на кулаке, скучает → носок подъехал: смотрит на него → хитрый прищур, уголок рта вверх
    see = sm(t, T_NASH + .2, T_NASH + .45)
    sly = sm(t, T_SVOI - .05, T_SVOI + .3)
    if sly > .05:
        e = ex("sly", lid=lerp(.7, .36, sly), smile=lerp(.2, .8, sly), look=(.55, .55), closed=0.0)
    else:
        e = ex("gloom", look=(lerp(.3, .6, see), lerp(.1, .6, see)), lid=lerp(.45, .75, see), closed=blinks(t, (23.05,)))
    hx, hy = HIP13
    lift = .06 * sly
    kw = dict(feet=FEET13, lean_add=-.04 * see - lift + .01 * math.sin(t * 2.1), head_add=.05 * see + .02 * math.sin(t * 1.7))
    hd = people.dima(hx, hy, 1.0, e, "chin_fist", **kw)["head"]
    kw["arms"] = {"n": ("ik", (hd[0] + 40, hd[1] + 250 - 10 * sly), -1)}
    dima = people.dima(hx, hy, 1.0, e, "chin_fist", **kw)["svg"]
    shadow = blob(ellipse_pts(cx, CAT13_Y + 4, 120, 10, 14), "#6e4a2c", .25) + blob(ellipse_pts(hx + 120, R.FL - 4, 300, 14, 16), "#6e4a2c", .22)
    world = [sc["bg"], sc["desk"], sc["stand"], sc["bed"], shadow, dima, sock, cat, sc["front"]]
    # камера: низко у пола, лёгкий наезд от кота к лицу Димы
    u = sm(t, T_A13 - .2, 25.15)
    s = lerp(1.26, 1.34, u) + .008 * math.sin(t * 2)
    ccx = lerp(1590, 1545, u) + 4 * math.sin(t * 1.4)
    ccy = lerp(1385, 1370, u) + 3 * math.sin(t * 1.7)
    set_ink(s)
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(.6, -.2, u))}">{"".join(world)}</g>', BG


FRAMES["s13"] = s13
