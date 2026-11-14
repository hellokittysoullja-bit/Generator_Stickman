"""s14 (17.36–19.08, клип 17.16–19.28): утренняя кухня — красная кофеварка на столешнице, рядом тот же будильник.
Камера влетает хлёстом и медленно едет вдоль столешницы; на «будильник» (17.80) будильник подпрыгивает и садится с
отскоком (тряска камеры); на «кофеварки» (18.56) — наезд-удар на кофеварку с будильником, у будильника блик-звёздочка,
лампочка кофеварки мигает."""
import math

import flatlib as F
from flatlib import clamp, ease_io, ease_out, smooth

T_A = 17.16
T_BUD = F.word("будильник", 17.5)
T_KOF = F.word("кофеварки", 18.0)


def frame(t):
    F.lib.DEFS.clear()
    F.set_ink(cam_scale(t))
    w = F.room(t, clock=(7, 0))
    # будильник: прыжок на «будильник»
    e = t - T_BUD
    hop, sq, rot = 0.0, 1.0, 0.0
    if 0 <= e < 0.32:
        u = e / 0.32
        hop = 70 * 4 * u * (1 - u)
        sq = 1.06 - 0.06 * u if u < .2 else 1.0
        rot = -8 * math.sin(math.pi * u)
    elif e >= 0.32:
        v = e - 0.32
        sq = 1 - 0.16 * math.exp(-v * 9) * abs(math.cos(v * 26))
        rot = 3 * F.kick(t, T_BUD + .32, 7, 4)
    elif -0.08 < e < 0:
        sq = 1 - 0.1 * (1 + e / 0.08)              # присел перед прыжком
    al = F.alarm(F.ALARM_X, F.CT - hop, F.ALARM_S, t, 7, 0, squash=sq, rot=rot, uid="a14")
    sh = F.A37.shadow(F.ALARM_X, F.CT - 2, F.ALARM_S * (1 - .3 * clamp(hop / 70)), .3)
    # блик-звёздочка на «кофеварки»
    front = ""
    k = t - T_KOF
    if k >= -0.02:
        a = ease_out(clamp((k + .02) / .16), 3) * (1 - smooth(.55, .8, k))
        cx, cy = F.ALARM_X - F.ALARM_S * .62, F.CT - F.ALARM_S * 2.5
        front += F.star(cx, cy, 42 * a * (1 + .15 * math.sin(k * 20)), k * 1.6, op=clamp(a * 1.4))
        front += F.star(cx + 56, cy + 40, 17 * a, -k * 2, op=clamp(a * 1.4))
        for j in range(6):
            ang = j * math.pi / 3 + .3
            r0 = 40 + 30 * ease_out(clamp((k + .02) / .3))
            r1 = r0 + 26 * (1 - clamp(k / .5))
            front += F.line([(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)), (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))], 4,
                            "#f2c23a", seed=3100 + j, op=clamp(1 - k / .45))
    lamp = 0.5 + 0.5 * math.sin(max(0, k) * 18) if k > 0 else 0.0
    body = F.machine(lamp) + F.mug(0.0) + sh + al
    # камера: хлёст справа на входе, медленный дрейф влево; удар-наезд на «кофеварки»
    u = clamp((t - T_A) / 2.12)
    ww = F.whip_in(t, T_A, .24)
    z = ease_out(clamp((t - T_KOF + .04) / .2), 3)
    hit = F.bump(t, T_KOF + .14, .3)
    cx = 860 - 40 * ease_io(u) + 260 * ww - 40 * z
    cy = 1010 + 50 * z + 3 * F.kick(t, T_BUD + .32, 10, 6) * 4
    s = cam_scale(t)
    r = -1.6 * ww + 0.8 * math.sin(t * 1.1) - 1.0 * z * (1 - u)
    return F.compose(w, body, (cx, cy, s, r), front)


def cam_scale(t):
    u = clamp((t - T_A) / 2.12)
    z = ease_out(clamp((t - T_KOF + .04) / .2), 3)
    return 2.05 + 0.1 * u + 0.75 * z + 0.12 * F.bump(t, T_KOF + .14, .3)
