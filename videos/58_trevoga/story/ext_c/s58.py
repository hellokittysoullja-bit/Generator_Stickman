"""Рилс 58 «тревога», группа C: s07 s09 s11 s12 s16 s17. frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Герои — people.py/cat.py/hand.py (Дима и кот рилсов 55–56, кот с нейтральной шерстью как look/hero.png), стакан, бутылка и миска — только
из ../common/props.py (общие для групп A, B, C)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
from lib import (INK, back_out, blob, blur, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rrect, shape,  # noqa: E402,F401
                 smooth, spring)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def dima(hip, bs, lean, arms, hands, expr, feet=None, head_ang=0.0, head_off=(0, 0), torso_k=1.0, who="dima"):
    p = dict(hip=tuple(hip), scale=bs, lean=lean, torso_k=torso_k, feet=feet, arms=arms, hands=hands, expr=expr, head_ang=head_ang,
             head_off=head_off, hood=0.0, strings=(0, 0))
    return people.draw(p, who)


def open_hand(c=.2, d=(1, 0), spread=.2, thumb=.2, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(c, c, c, c * .9), spread=spread, thumb=thumb, bend=.1, k=k)


def cstate(t, **kw):
    st = dict(look=(0, 0), turn=0.0, blink=0.0, ear=0, perk=0.0, tail=0.0, smile=0, tilt=0, flame_e=1.0)
    st.update(kw)
    return st


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def sparks(t, fx, fy, n=7, seed=11, rise=120):
    rs = np.random.RandomState(seed)
    o = []
    for i in range(n):
        per = rs.uniform(.9, 1.5)
        ph = rs.uniform(0, per)
        u = ((t + ph) % per) / per
        o.append(f'<circle cx="{fx + rs.uniform(-14, 14) + 18 * math.sin(u * 5 + i):.1f}" cy="{fy - rise * u - 12:.1f}" r="{4 * (1 - u) + 1:.1f}" fill="#ffd070"/>')
    return "".join(o)


def zig(x, y, ang, L, w=7, seed=0, col=INK, n=4, amp=14):
    a = math.radians(ang)
    d = np.array([math.cos(a), math.sin(a)])
    nn = np.array([-d[1], d[0]])
    pts = [(x, y)] + [(x + d[0] * L * (i + 1) / n + nn[0] * amp * (1 if i % 2 == 0 else -1),
                       y + d[1] * L * (i + 1) / n + nn[1] * amp * (1 if i % 2 == 0 else -1)) for i in range(n)]
    return line(pts, w, col, taper=.5, wmin=.25, seed=seed)


def partial(pts, u, step=4.0):
    if u <= 0:
        return []
    P = lib.sample(pts, False, step)
    n = max(2, int(len(P) * min(u, 1.0)))
    return [tuple(p_) for p_ in P[:n]]


# ═════════════════════════════ рукописное «кот»: одно перо, слитный курсив ═════════════════════════════
_HW = {}


def _cr(pts, step=2.4):
    """Catmull-Rom через точки, равномерно по длине."""
    P = np.array(pts, float)
    P = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(3, int(np.linalg.norm(p2 - p1) / step))
        for s in np.linspace(0, 1, n, endpoint=False):
            out.append(.5 * (2 * p1 + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2])
    return np.array(out)


def _arc(cx, cy, rx, ry, a0, a1, n=16):
    """Дуга овала: углы в градусах (0 — вправо, 90 — вверх), a1 > a0 — против часовой на экране."""
    return [(cx + rx * math.cos(math.radians(a)), cy - ry * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


def kot_strokes():
    """Слово «кот» строчными, курсивом, одной непрерывной линией (как пишут не отрывая пера): петля-стойка «к» с косой ручкой, «о» с
    входным и выходным соединением, «т» с тремя дугами («m»). Наклон вправо ~17°, буквы разной высоты (о ниже, к выше, т ниже), базовая
    линия ползёт вверх, в конце росчерк-подчёркивание отдельным штрихом. Координаты: y вниз, база y=0, x-высота ≈ 96."""
    if "s" in _HW:
        return _HW["s"]
    rs = np.random.RandomState(58)
    k = [(-18, -4), (-4, -36), (8, -84), (18, -122), (24, -134), (22, -112), (16, -66), (11, -26), (10, 4)]          # петля вверх, стойка вниз
    k += [(16, -22), (30, -42), (46, -66), (58, -82), (66, -88), (60, -74), (46, -56), (30, -40), (20, -28)]       # косая ручка: вверх и обратно к стойке
    k += [(30, -20), (44, -8), (56, 2), (66, 0), (78, -14), (90, -34)]                                              # нога и выходной штрих
    o = _arc(124, -44, 28, 46, 80, 80 + 380, 20)
    k += [(100, -66)] + [(x, y) for x, y in o[1:]] + [(150, -66), (166, -50)]
    k += [(172, -30), (176, -6), (184, 2), (190, -30), (196, -66), (204, -86), (212, -80), (214, -40), (216, -4), (222, 0), (228, -30), (234, -66), (244, -86),
          (252, -78), (254, -38), (258, -4), (266, 1), (282, -10), (298, -26)]
    pts = []
    for x, y in k:
        sc = 1.0 if x < 100 else (.93 if x < 170 else .96)
        pts.append((x - y * .30 + rs.normal(0, 1.1), y * sc + rs.normal(0, 1.1) - .045 * x))
    S1 = _cr(pts)
    S2 = _cr([(-14, 26), (60, 30), (160, 26), (240, 14), (318, 0)])                                       # подчёркивание-росчерк
    _HW["s"] = [S1, S2]
    return _HW["s"]


def _width(P, base=22.0):
    """Нажим: широкая линия на нисходящих и тонкая на восходящих (перо под наклоном), плавно по длине, дрожь руки."""
    d = np.gradient(P, axis=0)
    ang = np.arctan2(d[:, 1], d[:, 0])
    nib = math.radians(62)
    w = .38 + .62 * np.abs(np.sin(ang - nib))
    n = len(P)
    u = np.linspace(0, 1, n)
    w *= .3 + .7 * np.minimum(1, np.minimum(u * 18, (1 - u) * 10) ** .8)
    k = np.convolve(np.random.RandomState(n).normal(0, 1, n + 16), np.ones(17) / 17, "valid")[:n]
    w = np.convolve(np.pad(w, 4, mode="edge"), np.ones(9) / 9, "valid")
    return base * np.clip(w * (1 + .3 * k), .22, 1.0)


def _band_path(P, W):
    d = np.gradient(P, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    N = np.stack([-d[:, 1], d[:, 0]], 1)
    Lp = P + N * (W / 2)[:, None]
    Rp = P - N * (W / 2)[:, None]
    pts = [tuple(p) for p in Lp] + [tuple(p) for p in Rp[::-1]]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def marker_svg(tip, ang_deg, ln=300, col="#3d6f8c"):
    a = math.radians(ang_deg)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])
    T = np.array(tip, float)
    w = 30
    nib = [tuple(T), tuple(T + d * 38 + n * w * .3), tuple(T + d * 38 - n * w * .3)]
    o = lib.shape([q + (1,) for q in nib], "#2a2a34", "", w=3, seed=8801)
    body = [tuple(T + d * 38 + n * w * .5) + (1,), tuple(T + d * ln + n * w * .5) + (1,), tuple(T + d * ln - n * w * .5) + (1,), tuple(T + d * 38 - n * w * .5) + (1,)]
    sh = blob([tuple(T + d * 38 - n * w * .1), tuple(T + d * ln - n * w * .1), tuple(T + d * ln - n * w * .5), tuple(T + d * 38 - n * w * .5)], mix(col, "#000000", .2), .9)
    o += shape(body, col, sh, w=3.6, seed=8802)
    o += shape([tuple(T + d * 38 + n * w * .5) + (1,), tuple(T + d * 92 + n * w * .5) + (1,), tuple(T + d * 92 - n * w * .5) + (1,), tuple(T + d * 38 - n * w * .5) + (1,)],
               "#f0efe8", "", w=3.2, seed=8803)
    return o


def write_kot(t, t0, x0, y0, size=1.0, dur=(.78, .16), col="#1c1622"):
    """«кот» пишется пером с t0: слитная линия с нажимом, фломастер едет за остриём; после — упругий хлопок и искры."""
    S = kot_strokes()
    if t < t0 - .02:
        return ""
    o = []
    tt = t0
    tip = None
    for si, P in enumerate(S):
        a, b = tt, tt + dur[si]
        tt = b + (.06 if si == 0 else 0)
        u = clamp((t - a) / (b - a))
        u = ease_io(u) * .35 + u * .65
        if u <= 0:
            continue
        n = max(2, int(len(P) * u))
        Q = P[:n] * size + np.array([x0, y0])
        Wd = _width(P, 21.0 * size if si == 0 else 11.0 * size)[:n]
        o.append(f'<path d="{_band_path(Q, Wd)}" fill="{col}"/>')
        for e in (0, -1):
            if (e == 0 or u >= 1.0) and n > 2:
                c = Q[e]
                o.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{Wd[e] / 2:.1f}" fill="{col}"/>')
        if u < 1 and n > 3:
            tip = (Q[-1], Q[-1] - Q[-3])
    done = tt
    if tip and t < done:
        o.append(marker_svg(tuple(tip[0]), 55 + 6 * math.sin(t * 20)))
    e = t - done
    sc = 1.0
    cx_, cy_ = x0 + 150 * size, y0 - 50 * size
    if 0 < e < .5:
        sc = 1 + .05 * math.exp(-e * 9) * math.sin(min(e * 14, math.pi))
        for kk in range(9):
            a_ = kk * .7 + .2
            ez = ease_out(clamp(e / .45))
            o.append(f'<circle cx="{cx_ + (210 * size + 30) * math.cos(a_) * (.55 + .45 * ez):.1f}" '
                     f'cy="{cy_ + (110 * size + 40) * math.sin(a_) * (.6 + .4 * ez):.1f}" r="{max(.5, 8 * (1 - e / .5)):.1f}" fill="#ffd070"/>')
    return f'<g transform="translate({cx_:.1f} {cy_:.1f}) scale({sc:.4f}) translate({-cx_:.1f} {-cy_:.1f})">{"".join(o)}</g>'
