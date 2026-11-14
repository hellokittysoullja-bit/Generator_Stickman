"""Рукописные строки кодом: контуры Caveat 600 (hand_glyphs.json, собирает hand_build.py) проявляются маской по ходу пера.
Line(text, size, x, base, color, word_t=[(t0,t1) на слово]) — перо идёт по словам в их время; svg(t) — буквы; tip(t) — кончик пера;
pencil(x, y, ang) — карандаш в точке (рисуется кодом, без руки)."""
import json
import math
import os

import numpy as np

import lib
from lib import DEFS, INK, blob, clamp, f, line, shape

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "hand_glyphs.json")))
IDX = {"".join(g["ch"] for g in gl): i for i, gl in enumerate(G["lines"])}


class Line:
    def __init__(self, text, size, x, base, color, word_t=None, span=None, center=False, wk=1.25):
        gl = G["lines"][IDX[text]]
        self.sc = size / G["upm"]
        self.color, self.base, self.wk = color, base, wk
        total = sum(g["adv"] for g in gl) * self.sc
        self.x0 = x - total / 2 if center else x
        self.w = total
        path, self.gls, wi = [], [], 0
        xx = self.x0
        for gi, g in enumerate(gl):
            if g["ch"] == " ":
                wi += 1
            self.gls.append(dict(g=g, x=xx, wi=wi))
            for st in g.get("strokes", []):
                for k, (px, py) in enumerate(st):
                    path.append((xx + px * self.sc, base - py * self.sc, gi, k > 0, wi))
            xx += g["adv"] * self.sc
        self.path = path
        P = np.array([(p[0], p[1]) for p in path])
        self.P = P
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        down = np.array([p[3] for p in path[1:]])
        cost = np.where(down, seg, seg * 0.4)
        cum = np.concatenate([[0], np.cumsum(cost)])
        self.cum = cum / cum[-1]
        nw = wi + 1
        if word_t is None:
            a, b = span
            word_t = None
            self.T, self.C = [a, b], [0.0, 1.0]
        else:
            T, C = [], []
            for k in range(nw):
                ii = [i for i, p in enumerate(path) if p[4] == k]
                cs, ce = self.cum[ii[0]], self.cum[ii[-1]]
                ts, te = word_t[k]
                if T and ts < T[-1]:
                    ts = T[-1]
                T += [ts, max(te, ts + 0.02)]
                C += [cs, ce]
            C[-1] = 1.0
            self.T, self.C = T, C
        self.t_start, self.t_end = self.T[0], self.T[-1]

    def progress(self, t):
        return float(np.interp(t, self.T, self.C))

    def tip(self, t):
        p = self.progress(t)
        i = int(np.searchsorted(self.cum, p, side="right")) - 1
        i = max(0, min(i, len(self.P) - 2))
        c0, c1 = self.cum[i], self.cum[i + 1]
        q = 0 if c1 <= c0 else (p - c0) / (c1 - c0)
        x, y = self.P[i] + (self.P[i + 1] - self.P[i]) * q
        lift = 0.0 if self.path[i + 1][3] else math.sin(math.pi * q)
        return x, y, i, lift

    def svg(self, t, color=None):
        if t <= self.t_start:
            return ""
        color = color or self.color
        p = self.progress(t)
        if t >= self.t_end or p >= 1:
            cur, i_now, p = len(self.gls), len(self.P) - 1, 1.0
        else:
            _, _, i_now, _ = self.tip(t)
            cur = self.path[i_now][2]
        s = []
        for gi, o in enumerate(self.gls):
            g = o["g"]
            if not g["bounds"] or gi > cur:
                continue
            body = f'<path d="{g["d"]}" transform="translate({f(o["x"])} {f(self.base)}) scale({self.sc:.5f} {-self.sc:.5f})" fill="{color}"/>'
            if gi == cur and p < 1:
                pts = [(x, y, d) for (x, y, gg, d, _) in self.path[:i_now + 1] if gg == gi]
                tx, ty, _, _ = self.tip(t)
                pts.append((tx, ty, True))
                d = ""
                for k, (x, y, dn) in enumerate(pts):
                    d += ("L" if (dn and k > 0) else "M") + f"{f(x)} {f(y)}"
                mid = lib.uid("m")
                DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-900" y="-900" width="3000" height="4000">'
                            f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{f(g["width"] * self.sc * self.wk)}" '
                            f'stroke-linecap="round" stroke-linejoin="round"/></mask>')
                body = f'<g mask="url(#{mid})">{body}</g>'
            s.append(body)
        return "".join(s)


def pencil(x, y, ang=-52, sc=1.0, sd=0):
    """Карандаш остриём в (x, y); ang — угол оси от острия к ластику (градусы, -52 = вверх-вправо)."""
    a = math.radians(ang)
    u = (math.cos(a), math.sin(a))
    n = (-u[1], u[0])

    def P(d, w):
        return (x + (u[0] * d + n[0] * w) * sc, y + (u[1] * d + n[1] * w) * sc)
    s = []
    s.append(shape([P(0, 0), P(52, -12), P(52, 12)], "#e9c79a", blob([P(0, 0), P(52, 0), P(52, 12)], "#c9a272", .9), w=3.4, seed=sd + 1))
    s.append(shape([P(0, 0), P(15, -3.6), P(15, 3.6)], "#3a3440", w=2.2, seed=sd + 2))
    s.append(shape([P(52, -13), P(230, -13), P(230, 13), P(52, 13)], "#e8b43a", blob([P(52, 2), P(230, 2), P(230, 13), P(52, 13)], "#c4912a", .85)
                   + line([P(60, -4), P(222, -4)], 3, "#f4d27a", seed=sd + 3, op=.7), w=4, seed=sd + 4))
    s.append(shape([P(230, -13), P(246, -13), P(246, 13), P(230, 13)], "#b8bcc6", w=3, seed=sd + 5))
    s.append(shape([P(246, -12), P(272, -11), P(272, 11), P(246, 12)], "#e88a8a", blob([P(246, 2), P(272, 2), P(272, 11), P(246, 12)], "#c46a6a", .8), w=3.4, seed=sd + 6))
    return "".join(s)
