"""s17 (22.32–24.76, клип 22.12–24.96): утренняя кухня, средний план. Бодрый Дима (глаза широко) у столешницы;
будильник у кофеварки звенит — на «проснулся» (22.32) Дима шлёпает ладонью по кнопке, звон обрывается. Кофеварка
наливает кофе в кружку, на «кофе» (23.36) над кружкой пар (камера толкается), на «пахнет» (24.00) волны запаха текут
к носу — Дима блаженно жмурится и улыбается, голова чуть вверх."""
import math

import numpy as np

import flatlib as F
from flatlib import clamp, ease_io, ease_out, smooth

T_A = 22.12
T_PRO = F.word("проснулся", 22.0)
T_KOF = F.word("кофе", 23.0)
T_PAH = F.word("пахнет", 23.5)
HIP = np.array([500.0, 1262.0])
BS = 0.62
SLAP = T_PRO + 0.06


def cam(t):
    u = clamp((t - T_A) / 2.84)
    hit = F.bump(t, SLAP, .28)
    kof = F.bump(t, T_KOF + .02, .3)
    pah = smooth(T_PAH - .1, T_PAH + .8, t)
    cx = 665 - 20 * ease_io(u) + 30 * pah
    cy = 1100 - 50 * pah + 5 * F.kick(t, SLAP, 9, 7)
    s = 1.42 + .06 * ease_io(u) + .07 * hit + .04 * kof + .08 * pah
    r = .7 - .9 * ease_io(u) + .8 * F.kick(t, SLAP, 8, 5)
    return cx, cy, s, r


def frame(t):
    F.lib.DEFS.clear()
    c = cam(t)
    F.set_ink(c[2])
    w = F.room(t, clock=(7, 20), jars=False)
    # будильник: звенит до шлепка
    e = t - SLAP
    ring = 1.0 if e < 0 else 0.0
    press = clamp(1 - abs(e - .06) / .14) if -0.05 < e < 0.25 else 0.0
    sq = 1 - 0.12 * press
    al = F.alarm(F.ALARM_X, F.CT, F.ALARM_S, t, 7, 20, ring=ring, press=press, squash=sq, uid="a17")
    marks = F.alarm_marks(F.ALARM_X, F.CT, F.ALARM_S, t, ring)
    bx, by = F.alarm_top(F.ALARM_X, F.CT, F.ALARM_S)
    # ближняя рука: занесена над будильником → шлёп → отходит к стойке
    hover = np.array([bx - 66, by - 52 + 6 * math.sin(t * 9)])
    hit_p = np.array([bx - 60, by - 2 + 3 * press])
    rest = np.array([612.0, 1196.0])
    if e < -0.10:
        P = hover
    elif e < 0:
        P = hover + (hit_p - hover) * ease_io((e + 0.10) / 0.10) ** 1.4
    elif e < 0.35:
        P = hit_p
    else:
        P = hit_p + (rest - hit_p) * ease_io(clamp((e - .35) / .4))
    flat = e > -0.06 and e < .45
    hands = {"n": dict(kind="open", flip=-1, dir=(1, .1) if flat else ((1, .35) if e < 0 else (1, .12)), curl=(.05, .05, .08, .1) if flat else (.2, .25, .3, .35),
                       spread=.18, thumb=.3),
             "f": dict(kind="open", flip=-1, dir=(.1, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    arms = {"n": ("ik", tuple(P) if e < .35 else (P[0] - 30, P[1] - 4), -1), "f": ("ang", .14, .3)}
    # лицо
    pah = smooth(T_PAH + .25, T_PAH + .5, t)
    smell = smooth(T_KOF + .3, T_PAH + .3, t)
    ex = dict(lid=.95 - .1 * smell, look=(.7, .55) if e < .5 else (.75, .45 - .2 * smell), brows="up", mouth="smile" if pah < .5 else "smile",
              smile=.55 + .45 * smooth(SLAP, SLAP + .3, t), laugh=.95 * pah, hair=8 * F.bump(t, SLAP, .5) * F.osc(t, 5),
              closed=F.blink_at(t, 23.0, .16))
    head_ang = .06 - .16 * pah + .02 * F.osc(t, .8)
    dm = F.people.draw(dict(hip=tuple(HIP), scale=BS, lean=.08 - .04 * pah, feet={"n": ((HIP[0] + 16, HIP[1] + 376), 0.0),
                                                                                  "f": ((HIP[0] - 4, HIP[1] + 372), 0.0)},
                            arms=arms, hands=hands, expr=ex, head_ang=head_ang, hood=0, strings=(3 * F.osc(t, 1.3), 2 * F.osc(t, 1.1, 1))),
                       "dima")
    hx, hy = dm["head"]
    nose = (hx + 70 * BS * 1.0 + 6, hy + 50 * BS)
    # кофе
    a_pour, b_pour = T_PRO + .3, T_KOF - .02
    fill = ease_io(clamp((t - a_pour) / (b_pour - a_pour)))
    lamp = (0.5 + 0.5 * math.sin((t - a_pour) * 16)) if a_pour - .1 < t < b_pour + .1 else (1.0 if t >= b_pour else 0.0)
    objs = F.machine(lamp) + F.pour(t, a_pour, b_pour) + F.mug(fill, t) + F.steam(t, T_KOF, 1.0, 3, 170)
    objs += F.A37.shadow(F.ALARM_X, F.CT - 2, F.ALARM_S, .3) + al + marks
    objs += F.aroma(t, T_PAH, nose, 1.3)
    layers = dm.get("legs", "") + dm["arm_f"] + dm["body"] + dm["arm_n"]
    return F.compose(w, objs + layers, c)
