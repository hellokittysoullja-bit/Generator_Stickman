"""Бег Димы на беговой дорожке (рилс 36, сцена gym): план касаний бега рилса 26 (run/scene.py), но в системе ленты.

Мир бега («земля») едет вместе с лентой: точка ленты под стопой неподвижна в мире, таз уезжает вперёд со скоростью
ленты. Рисуем в системе дорожки: всё из мира сдвигается на −B(t) (B — путь ленты), поэтому таз стоит на месте, а
стопа на опоре едет назад вместе с лентой и не скользит по ней. Темп (шаг, длина шага) может меняться во времени —
лента ускоряется."""
import math

import numpy as np

import dimax as dima
from lib import clamp, smooth

BS = dima.BS
LEG = (dima.THIGH + dima.SHIN) * BS
AHW = dima.AH * BS
TOEW = dima.TOE * BS * 1.22


class Run:
    """cad(t) -> (TC — время шага, STEP — длина шага, мир); stance — доля опоры от шага; lift — высота маха стопы;
    hx — x таза в системе дорожки; hip_k — высота таза в долях ноги; bob — подпрыгивание таза."""

    def __init__(self, t0, t1, cad, stance=0.61, lift=118.0, hx=-80.0, hip_k=0.86, bob=12.0, back=30.0):
        self.cad, self.stance, self.lift, self.hx, self.hip_k, self.bob, self.back = cad, stance, lift, hx, hip_k, bob, back
        ts = np.arange(t0 - 3.0, t1 + 3.0, 1 / 600)
        v = np.array([cad(t)[1] / cad(t)[0] for t in ts])
        B = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(ts))])
        self.ts, self.B = ts, B
        C = []
        t, k = t0 - 2.6, 0
        while t < t1 + 2.0:
            tc, _ = cad(t)
            st = self.stance * tc
            C.append([t, "n" if k % 2 == 0 else "f", self.hx - 6 + self.belt(t + st / 2), 0.0, t + st, tc])
            t += tc
            k += 1
        self.C = C

    def belt(self, t):
        return float(np.interp(t, self.ts, self.B))

    def hip(self, t, bob=True):
        x = self.hx + self.belt(t)
        y = -(LEG * self.hip_k + AHW)
        if bob:
            best, tc = 9.0, 0.2
            for c in self.C:
                dt = t - (c[0] + (c[4] - c[0]) / 2)
                if abs(dt) < abs(best):
                    best, tc = dt, c[5]
            y += self.bob * math.cos(2 * math.pi * best / tc)
        return np.array([x, y])

    def planted(self, c, hip):
        A = np.array([c[2], c[3] - AHW])
        reach = LEG * 0.985
        if np.linalg.norm(A - hip) <= reach:
            return A, 0.0
        toe = np.array([c[2] + TOEW, c[3]])
        lo, hi = 0.0, 1.35
        for _ in range(30):
            m = (lo + hi) / 2
            A2 = toe + dima.rot(np.array([-TOEW, -AHW]), m)
            if np.linalg.norm(A2 - hip) > reach:
                lo = m
            else:
                hi = m
        return toe + dima.rot(np.array([-TOEW, -AHW]), hi), hi

    def foot(self, side, t, hip):
        cs = [c for c in self.C if c[1] == side]
        prev, nxt = cs[0], None
        for c in cs:
            if c[0] <= t:
                prev = c
            elif nxt is None:
                nxt = c
        if t <= prev[4] or nxt is None:
            return self.planted(prev, hip)
        t0, t1 = prev[4], nxt[0]
        u = clamp((t - t0) / (t1 - t0))
        A0, ph0 = self.planted(prev, self.hip(t0))
        A1 = np.array([nxt[2], nxt[3] - AHW])
        ux = (1 - math.cos(math.pi * u ** 1.3)) / 2
        x = A0[0] + (A1[0] - A0[0]) * ux - self.back * math.sin(math.pi * clamp(u * 1.5))
        y = A0[1] + (A1[1] - A0[1]) * u - self.lift * math.sin(math.pi * clamp(u * 1.08)) ** 1.3
        if u < .3:
            phi = ph0 + (0.75 - ph0) * smooth(0, .3, u)
        elif u < .85:
            phi = 0.75 + (-0.26 - 0.75) * smooth(.3, .85, u)
        else:
            phi = -0.26 * (1 - smooth(.85, 1.0, u))
        return np.array([x, y]), phi

    def phase(self, t):
        """Фаза руки: 0..2π за двойной шаг (от касания ближней ногой)."""
        cn = [c for c in self.C if c[1] == "n"]
        prev = cn[0]
        for c in cn:
            if c[0] <= t:
                prev = c
        return 2 * math.pi * (t - prev[0]) / (2 * prev[5])

    def to_tm(self, p, t):
        """Мир → система дорожки."""
        return np.array([p[0] - self.belt(t), p[1]])
