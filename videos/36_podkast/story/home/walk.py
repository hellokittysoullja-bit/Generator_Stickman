"""Шаг Димы (не бег): спокойная бодрая ходьба по дорожке слева направо, общая для планов s14–s16.

Касания чередуются (ближняя «n» — чётные, дальняя «f» — нечётные), между ними шаг TS. Опора одной ноги длится
TS + DS (двойная опора DS), мах — остальное. На опоре: удар пяткой с поднятым носком (перекат через пятку) →
стопа плоско стоит в мире (не скользит) → пятка отрывается, перекат через носок → отрыв носка. В махе стопа идёт
низко над землёй (просвет считается по подошве, не по лодыжке). Таз: ровная скорость, верх в середине одиночной
опоры, низ в двойной. Руки качаются против ног почти прямыми.
Мир: земля y = 0, x вправо; рисунок героя — dima.draw (масштаб dima.BS)."""
import math

import numpy as np

import dima
from lib import clamp, smooth

BS = dima.BS
LEG = (dima.THIGH + dima.SHIN) * BS        # 268.4
KS = 1.22
SOLE = ((66 - dima.AH) * KS + dima.AH) * BS   # подошва ниже лодыжки
HEELX = 74 * KS * BS
TOEX = 176 * KS * BS

TS = 0.52           # шаг, с
DS = 0.11           # двойная опора, с
STEP = 172.0        # длина шага, мир
V = STEP / TS
T0 = 22.0           # касание k=0 (ближняя)
HS_PHI = -0.26      # носок вверх на ударе пяткой
TO_PHI = 0.62       # носок вниз на отрыве
HIP_H = SOLE + LEG * 0.945
BOB = 6.0
REACH = LEG * 0.992


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


def contact(k):
    return T0 + k * TS, ("n" if k % 2 == 0 else "f"), k * STEP


def hip_at(t, bob=True):
    x = V * (t - T0) - 0.40 * STEP
    y = -HIP_H
    if bob:
        y += BOB * math.cos(2 * math.pi * (t - T0 - DS - (TS - DS) / 2) / TS) * -1
    return np.array([x, y])


def _pivot(P, local, phi):
    return P - rot(np.array(local), phi)


def heel_ankle(C, phi):
    return _pivot(np.array([C - HEELX, 0.0]), (-HEELX, SOLE), phi)


def toe_ankle(C, phi):
    return _pivot(np.array([C + TOEX, 0.0]), (TOEX, SOLE), phi)


def stance(tc, C, t, hip):
    """Лодыжка и угол стопы на опоре (t в [tc, tc + TS + DS])."""
    u = t - tc
    if u < 0.13:                                    # перекат через пятку
        phi = HS_PHI * (1 - smooth(0, 0.13, u))
        A = heel_ankle(C, phi)
        return A, phi
    phi_f = TO_PHI * smooth(TS - 0.18, TS + DS, u) ** 1.3   # пятка отрывается сама к концу опоры
    A = toe_ankle(C, phi_f)
    if np.linalg.norm(A - hip) > REACH:             # не дотягивается — перекат через носок дальше
        lo, hi = phi_f, 1.4
        for _ in range(30):
            m = (lo + hi) / 2
            if np.linalg.norm(toe_ankle(C, m) - hip) > REACH:
                lo = m
            else:
                hi = m
        phi_f = hi
        A = toe_ankle(C, phi_f)
    return A, phi_f


def sole_max_y(A, phi):
    return max((A + rot(np.array(p), phi))[1] for p in ((-HEELX, SOLE), (TOEX, SOLE), (TOEX * .5, SOLE)))


def foot_at(side, t):
    hip = hip_at(t)
    k = math.floor((t - T0) / TS)
    # последнее касание этой ноги не позже t
    kk = k if contact(k)[1] == side else k - 1
    tc, _, C = contact(kk)
    if t <= tc + TS + DS:
        return stance(tc, C, t, hip)
    t0 = tc + TS + DS
    tn, _, Cn = contact(kk + 2)
    A0, ph0 = stance(tc, C, t0, hip_at(t0))
    A1 = heel_ankle(Cn, HS_PHI)
    u = clamp((t - t0) / (tn - t0))
    ux = (1 - math.cos(math.pi * u)) / 2
    x = A0[0] + (A1[0] - A0[0]) * ux
    y = A0[1] + (A1[1] - A0[1]) * u - 26 * math.sin(math.pi * clamp(u * 1.15)) ** 1.1
    if u < 0.5:
        phi = ph0 * (1 - smooth(0, 0.5, u)) + 0.15 * math.sin(math.pi * u / 0.5) * 0
    else:
        phi = HS_PHI * smooth(0.55, 1.0, u)
    A = np.array([x, y])
    m = sole_max_y(A, phi)
    if m > -2 and 0.04 < u < 0.96:
        A[1] -= (m + 2) * min(1, min(u, 1 - u) / 0.08)
    return A, phi


def phase(t):
    """0..1 цикла от касания ближней ноги."""
    return ((t - T0) / (2 * TS)) % 1.0


def swing_arms(t, amp=0.40):
    ps = 2 * math.pi * (phase(t) - 0.06)
    c = math.cos(ps)
    out = {}
    for s_, sg in (("n", -1), ("f", 1)):
        sw = sg * c
        out[s_] = ("ang", 0.04 + amp * sw, 0.22 + 0.32 * max(0, sw) + 0.06 * max(0, -sw))
    return out


def pose(t, arms=None, expr=None, lean=0.07, head_ang=0.0, **kw):
    hip = hip_at(t)
    feet = {s: foot_at(s, t) for s in ("n", "f")}
    vy = (hip_at(t)[1] - hip_at(t - .04)[1]) / .04
    p = dict(hip=hip, lean=lean, feet=feet, arms=arms or swing_arms(t), hands={"n": "fist", "f": "fist"},
             head_ang=head_ang + 0.012 * math.sin(2 * math.pi * phase(t) * 2), hood=clamp(-vy * 0.06, -8, 10),
             strings=(clamp(-vy * .05, -14, 14) - 8, clamp(vy * .06, -12, 14)),
             expr=expr or dict(lid=0.6, look=(0.4, 0.0), brows="calm", mouth="smile", hair=clamp(vy * 0.04, -6, 6)))
    p.update(kw)
    return p
