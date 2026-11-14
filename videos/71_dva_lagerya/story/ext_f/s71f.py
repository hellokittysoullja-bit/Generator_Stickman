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
from h71 import blinks, bump, decay, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
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


def laptop_to_dima(x, y, k, open_, t, lines=0.0, glow=0.0):
    """Ноутбук экраном к Диме (Дима слева): {svg, keys}. ВРЕМЕННО — до общего ноутбука в props."""
    lp = PR.laptop_pts(x, y, k, open_, turn=.55)
    svg = PR.laptop(x, y, k, open_, "lines" if lines > 0 else "dark", lines=lines, t=t, seed=1, turn=.55, glow=glow)
    return dict(svg=svg, keys=lp["keys"])


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')


# ═════════════════════════ s20: кот на столе одобряет ═════════════════════════
T_A20 = 32.74
T_I20, T_KOT20, T_SMOT, T_ODOB = wt(98), wt(99), wt(100), wt(101)      # 32.68, 32.80, 33.08, 33.47
CAT20 = (985.0, R.DESK_TOP + 6)          # кот на ближнем крае стола, ближе к камере (крупнее мира)
CAT20_K = 1.75
SX20, SY20 = R.SIT
FEET20 = {"n": ((SX20 + 300, R.FL - 52), 0.0), "f": ((SX20 + 250, R.FL - 50), 0.0)}
LAP20 = (640.0, R.DESK_TOP - 46)
LAP20_K = .7


def type_hand(t, base, phase):
    ph = t * 9.5 + phase
    W = (base[0] + 7 * math.sin(ph * .7), base[1] - 4 * abs(math.sin(ph)))
    curl = tuple(.35 + .25 * max(0.0, math.sin(ph + i * 1.7)) for i in range(4))
    return W, {"dir": (1, .32), "curl": curl, "thumb": .35, "spread": .12, "bend": .1}


def s20(t):
    sc = R.desk_scene(t, "day")
    lp = laptop_to_dima(LAP20[0], LAP20[1], LAP20_K, 1.0, t, lines=clamp(.6 + (t - 32.5) * .15))
    kc = lp["keys"]
    Wf, hf = type_hand(t, (kc[0] - 120, kc[1] - 18), 0.0)
    Wn, hn = type_hand(t, (kc[0] - 70, kc[1] - 8), 1.9)
    e = ex("focus_smile" if "focus_smile" in people.EXPR["dima"] else "focus", look=(.6, .45), lid=.62, closed=blinks(t, (33.2, 34.3)))
    kw = dict(feet=FEET20, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, hands={"f": hf, "n": hn},
              lean_add=.12 + .015 * math.sin(t * 2.3), head_add=.04 + .02 * math.sin(t * 1.9))
    parts = {k: people.dima(SX20, SY20, 1.0, e, "sit_desk", layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
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
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], lp["svg"], parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"],
             parts["arm_f"], parts["body"], parts["arm_n"], shadow, cat, fl]
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
    tgt2 = (hx + 290, hy - 380)          # палец вправо-вверх на синий: рука не заходит на слово «кот»
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
