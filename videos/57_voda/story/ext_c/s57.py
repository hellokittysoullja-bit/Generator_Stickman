"""Рилс 57 «вода», группа C: s09 s10 s15 s16 s17 s18. frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Герои — people.py/cat.py/hand.py (Дима и кот рилсов 55–56, кот с нейтральной шерстью как look/hero.png), стакан, бутылка и миска — только
из ../common/props.py (общие для групп A, B, C)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
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


# ═════════════════════════════ рукописное «кот»: одно перо, неровный почерк ═════════════════════════════
_HW = {}


def _cr(pts, step=2.6):
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


def _oval(cx, cy, rx, ry, a0, a1, n=14):
    """Дуга «о» против часовой стрелки на экране: углы в градусах (0 — вправо, 90 — вверх), a1 > a0."""
    return [(cx + rx * math.cos(math.radians(a)), cy - ry * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


def kot_strokes():
    """Штрихи слова «кот» в локальных единицах (y вниз, база y=0, высота строчной ≈ 125): к — стойка и «ножки», о — овал с хвостом, который
    сам переходит в перекладину т, стойка т с росчерком. Почерк: наклон вправо, о ниже, т выше, каждая буква чуть сдвинута и повёрнута."""
    if "s" in _HW:
        return _HW["s"]
    rs = np.random.RandomState(57)
    S = []
    S.append([(20, -116), (15, -80), (10, -40), (11, -4), (13, 3)])                                       # стойка «к»
    S.append([(68, -108), (50, -86), (30, -66), (13, -54), (34, -40), (54, -18), (72, -5), (94, -14)])       # ножки «к» с хвостиком
    o = _oval(152, -57, 40, 56, 62, 62 + 400, 18)
    S.append(o + [(198, -84), (214, -92)])                                                                 # «о» с хвостиком
    S.append([(232, -108), (258, -118), (290, -113), (324, -121)])                                         # перекладина «т»
    S.append([(284, -116), (281, -78), (278, -38), (282, -5), (302, -10), (316, -24)])                       # стойка «т» с росчерком
    out = []
    for si, st in enumerate(S):
        slant = .17
        pts = [(x - y * slant + rs.normal(0, 1.4), y + rs.normal(0, 1.4) + .035 * x) for x, y in st]       # наклон + лёгкий «сползающий» базис
        out.append(_cr(pts))
    _HW["s"] = out
    return out


def _width(P, base=30.0):
    """Нажим: толще на «нисходящих» штрихах и в середине штриха, тонко на соединениях; шум от дрожи руки."""
    d = np.gradient(P, axis=0)
    ang = np.arctan2(d[:, 1], d[:, 0])
    nib = math.radians(-50)
    w = .55 + .45 * np.abs(np.sin(ang - nib))
    n = len(P)
    u = np.linspace(0, 1, n)
    w *= .35 + .65 * np.minimum(1, np.minimum(u * 6, (1 - u) * 5) ** .8)
    k = np.convolve(np.random.RandomState(n).normal(0, 1, n + 12), np.ones(13) / 13, "valid")[:n]
    return base * np.clip(w * (1 + .35 * k), .28, 1.0)


def _band_path(P, W):
    d = np.gradient(P, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    N = np.stack([-d[:, 1], d[:, 0]], 1)
    Lp = P + N * (W / 2)[:, None]
    Rp = P - N * (W / 2)[:, None]
    pts = [tuple(p) for p in Lp] + [tuple(p) for p in Rp[::-1]]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def marker_svg(tip, ang_deg, ln=330, col="#3d6f8c"):
    a = math.radians(ang_deg)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])
    T = np.array(tip, float)
    w = 34
    nib = [tuple(T), tuple(T + d * 40 + n * w * .3), tuple(T + d * 40 - n * w * .3)]
    o = lib.shape([q + (1,) for q in nib], "#2a2a34", "", w=3, seed=8801)
    body = [tuple(T + d * 40 + n * w * .5) + (1,), tuple(T + d * ln + n * w * .5) + (1,), tuple(T + d * ln - n * w * .5) + (1,), tuple(T + d * 40 - n * w * .5) + (1,)]
    sh = blob([tuple(T + d * 40 - n * w * .1), tuple(T + d * ln - n * w * .1), tuple(T + d * ln - n * w * .5), tuple(T + d * 40 - n * w * .5)], mix(col, "#000000", .2), .9)
    o += shape(body, col, sh, w=3.6, seed=8802)
    o += shape([tuple(T + d * 40 + n * w * .5) + (1,), tuple(T + d * 96 + n * w * .5) + (1,), tuple(T + d * 96 - n * w * .5) + (1,), tuple(T + d * 40 - n * w * .5) + (1,)],
               "#f0efe8", "", w=3.2, seed=8803)
    return o


def write_kot(t, t0, x0, y0, size=1.0, dur=(.10, .17, .22, .09, .12), gap=.025, col="#1c1622"):
    """«кот» рисуется пером с t0: штрихи один за другим, фломастер едет за остриём; после — упругий хлопок и искры."""
    S = kot_strokes()
    if t < t0 - .02:
        return ""
    o = []
    tt = t0
    tip = None
    for si, P in enumerate(S):
        a, b = tt, tt + dur[si]
        tt = b + gap
        u = clamp((t - a) / (b - a))
        if u <= 0:
            continue
        n = max(2, int(len(P) * u))
        Q = P[:n] * size + np.array([x0, y0])
        Wd = _width(P, 25.0 * size)[:n]
        o.append(f'<path d="{_band_path(Q, Wd)}" fill="{col}"/>')
        for e in (0, -1):
            if (e == 0 or u >= 1.0) and n > 2:
                c = Q[e]
                o.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{Wd[e] / 2:.1f}" fill="{col}"/>')
        if u < 1 and n > 3:
            tip = (Q[-1], Q[-1] - Q[-3])
    done = tt - gap
    if tip and t < done + .04:
        o.append(marker_svg(tuple(tip[0]), 52 + 6 * math.sin(t * 20)))
    e = t - done
    sc = 1.0
    cx_, cy_ = x0 + 150 * size, y0 - 60 * size
    if 0 < e < .5:
        sc = 1 + .07 * math.exp(-e * 9) * math.sin(min(e * 14, math.pi))
        for k in range(9):
            a_ = k * .7 + .2
            r_ = 40 + 150 * ease_out(clamp(e / .45))
            o.append(f'<circle cx="{cx_ + (210 * size + 30) * math.cos(a_) * (.55 + .45 * ease_out(clamp(e / .45))):.1f}" '
                     f'cy="{cy_ + (110 * size + 40) * math.sin(a_) * (.6 + .4 * ease_out(clamp(e / .45))):.1f}" r="{max(.5, 8 * (1 - e / .5)):.1f}" fill="#ffd070"/>')
    return f'<g transform="translate({cx_:.1f} {cy_:.1f}) scale({sc:.4f}) translate({-cx_:.1f} {-cy_:.1f})">{"".join(o)}</g>'


# ═════════════════════════════ общий фон ═════════════════════════════
def wall_floor(horizon, wall="#f1e2c6", wall_sh="#e2cca8", floor="#c8955f", floor_sh="#a97542", base="#7a5430"):
    o = blob(rrect(-300, -300, 1400, horizon), wall)
    o += blob(rrect(-300, horizon, 1400, 2300), floor)
    o += blob(rrect(-300, horizon - 46, 1400, horizon), wall_sh, 1)
    o += line([(-300, horizon), (1400, horizon)], 5, base, taper=0, wmin=1, seed=11)
    for i, y in enumerate((horizon + 110, horizon + 270, horizon + 460, horizon + 680)):
        o += line([(-300, y), (1400, y + 4)], 3, floor_sh, taper=0, wmin=1, seed=20 + i, op=.8)
    return o


def window(x0, y0, x1, y1, t=0.0):
    o = shape(rrect(x0 - 16, y0 - 16, x1 + 16, y1 + 16, 6), "#fdf8ec", "", w=5, seed=3301)
    sky = lib.lin_grad([(0, "#a9d8f2", 1), (1, "#dff1fa", 1)], 0, 0, 0, 1)
    o += f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{sky})"/>'
    cx = (x0 + x1) / 2
    o += blob(ellipse_pts(x0 + 60, y0 + 70, 34, 34, 14), "#fff1b0")
    o += blob(ellipse_pts(cx + 40 + 6 * math.sin(t * .6), y0 + 130, 70, 22, 14), "#ffffff")
    o += line([(cx, y0), (cx, y1)], 8, "#fdf8ec", taper=0, wmin=1, seed=3302) + line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], 8, "#fdf8ec", taper=0, wmin=1, seed=3303)
    o += shape(rrect(x0, y0, x1, y1, 2), "none", "", w=4, seed=3304)
    return o


def sofa(x0, x1, seat_y, floor_y, col="#5b8f8c"):
    sh = mix(col, "#000000", .22)
    hi = mix(col, "#ffffff", .16)
    back_top = seat_y - 330
    o = shape(rrect(x0 + 40, back_top, x1 - 40, seat_y + 40, 60), col, blob(rrect(x0 + 60, back_top + 24, x1 - 60, back_top + 150, 40), hi, .55), w=5.4, seed=3410)
    # подушки спинки
    mid = (x0 + x1) / 2
    o += line([(mid, back_top + 40), (mid, seat_y - 20)], 4, sh, taper=.2, wmin=.8, seed=3411)
    # сиденье
    o += shape(rrect(x0 + 24, seat_y - 40, x1 - 24, floor_y - 70, 44), mix(col, "#ffffff", .08),
               blob(rrect(x0 + 24, floor_y - 150, x1 - 24, floor_y - 70, 40), sh, .45), w=5.4, seed=3412)
    o += line([(mid, seat_y - 38), (mid, floor_y - 74)], 4, sh, taper=.2, wmin=.8, seed=3413)
    # подлокотники
    for (a, b, sd) in ((x0 - 20, x0 + 100, 3414), (x1 - 100, x1 + 20, 3415)):
        o += shape(rrect(a, seat_y - 170, b, floor_y - 50, 46), col, blob(rrect(a + 12, seat_y - 160, a + 36, floor_y - 70, 12), hi, .6), w=5.4, seed=sd)
    # ножки
    for xx in (x0 + 30, x1 - 30):
        o += shape(rrect(xx - 14, floor_y - 56, xx + 14, floor_y - 4, 5), "#7a5430", "", w=3.6, seed=3420 + int(xx))
    return o


# ═════════════════════════════ s17 33.2–35.2 ═════════════════════════════
T_NAPISHI, T_KOT = wt(85), wt(86)       # 33.48, 34.32
T_S17 = 33.2


def frame17(t):
    z = 1.38 + .12 * ease_io(clamp((t - 33.0) / 2.4)) + .03 * bump(t, T_KOT, .3)
    set_ink(z)
    FLOOR_Y = 1345
    o = [wall_floor(1230), window(110, 330, 400, 760, t), blob(ellipse_pts(540, FLOOR_Y + 30, 520, 40, 20), "#a8743d", .5)]
    o.append(sofa(20, 1060, 1135, FLOOR_Y))
    # растение справа сзади (простое): горшок и листья
    # Дима
    kick = bump(t, T_NAPISHI, .5)
    bob = 3 * math.sin(t * 4.2)
    hip = (310, 1080 + bob * .3)
    bs = .86
    hs = bs / .6
    wr_n = (508 + 18 * kick, 915 - 26 * kick + bob)
    exp = dict(lid=.92, look=(-.62, .06), closed=blink_of(t, (33.55, 34.7)), brows="calm" if kick < .2 else "up", mouth="smile", smile=1.0, blush=.35)
    d = dima(hip, bs, .04, {"n": ("ik", wr_n, -1), "f": ("ik", (470, 1010), -1)},
             {"n": open_hand(.8, (0.05, -1), .05, .75, flip=-1, k=1.0), "f": open_hand(.35, (1, .4), .15, .3)}, exp,
             feet={"n": ((560, 1342), 0.0), "f": ((505, 1346), 0.0)}, head_ang=-.03 + .04 * kick)
    o.append(d.get("legs", "") + d["arm_f"] + d["body"])
    bx, by = d["wrist"]["n"]
    bpos = (bx + 4, by + 46)
    o.append(PR.bottle(bpos[0], bpos[1], hs, .78, -4 + 5 * math.sin(t * 6) * (.4 + kick), 6 * math.sin(t * 9) * (.5 + kick), True, False))
    o.append(d["arm_n"])
    # кот справа
    CX_, CY_, CK = 800, 1138, .84
    up = ease_io(clamp((t - T_KOT + .05) / .3))
    st = cstate(t, look=(0.0 + .0, -.25 * up), turn=0.0, blink=blink_of(t, (33.9, 35.0)), ear=5 * bump(t, T_NAPISHI + .1, .4) + 4 * bump(t, T_KOT + .3, .4),
                perk=.25 * up, tail=7 * math.sin(t * 2.6), smile=1 if up > .5 else 0, flame_e=1.4 + .3 * math.sin(t * 9), tilt=2 * math.sin(t * 1.3))
    o.append(blob(ellipse_pts(CX_, CY_ + 6, 120 * CK / .84, 14, 14), mix("#5b8f8c", "#000000", .35)))
    o.append(Cat.draw(CX_, CY_, CK, st, t))
    o.append(sparks(t, CX_ + (995 - 836) * CK, CY_ + (1076 - 1306) * CK - 20, 6, 17))
    cam = lib.cam(610 + 20 * ease_io(clamp((t - 33.0) / 2.4)), 860 - 30 * ease_io(clamp((t - 33.0) / 2.4)), z, -.5 + .5 * ease_io(clamp((t - 33.0) / 2.4)))
    return f'<g transform="{cam}">{"".join(o)}{write_kot(t, T_KOT - .06, 560, 650, 0.95)}</g>'


# ═════════════════════════════ s18 35.2–37.1 ═════════════════════════════
T_VOS = wt(92)       # 36.06


def frame18(t):
    u = ease_io(clamp((t - 35.0) / 2.1))
    z = 1.75 - .62 * u
    set_ink(z)
    TOP_Y = 1160
    o = [wall_floor(1010, "#f4e6c8", "#e6d0aa"), window(660, 330, 960, 760, t)]
    bs = .72
    hs = bs / .6
    scr = math.sin(t * 9.5)
    hip = (330, 1190 + 2 * math.sin(t * 3))
    exp = dict(lid=.7, look=(.55, .15), closed=blink_of(t, (35.7, 36.9)), brows="det", mouth="flat", blush=.15)
    wr = (300 + 8 * scr, 706 + 6 * math.sin(t * 9.5 + 1))
    d = dima(hip, bs, .02, {"n": ("ik", wr, 1), "f": ("ik", (440, 1090), -1)}, {"n": open_hand(.55, (.85, -.35), .25, .3, flip=1, k=1.0), "f": open_hand(.3, (1, .2), .15, .3)}, exp,
             feet=None, head_ang=-.02 + .025 * scr)
    o.append(d["arm_f"] + d["body"] + d["arm_n"])
    # стол
    o.append(shape(rrect(-40, TOP_Y - 70, 1120, TOP_Y + 20, 10), "#d2a26a", blob(rrect(-40, TOP_Y - 70, 1120, TOP_Y - 40, 6), "#e0b883", .9), w=5, seed=3500))
    o.append(shape(rrect(-40, TOP_Y + 20, 1120, TOP_Y + 190, 6), "#b98350", blob(rrect(-40, TOP_Y + 20, 1120, TOP_Y + 60, 4), "#9a6a3c", .8), w=5, seed=3501))
    o.append(line([(-40, TOP_Y + 60), (1120, TOP_Y + 60)], 3, "#8d5f35", taper=0, wmin=1, seed=3502, op=.8))
    # восемь стаканов: «вздрагивают» на «восемь», волной слева направо
    for i in range(8):
        gx = 210 + i * 80
        ph = t - (T_VOS + .035 * i)
        jump = 0.0 if ph < 0 else 22 * math.exp(-ph * 9) * abs(math.sin(ph * 26))
        sl = 0.0 if ph < 0 else 14 * math.exp(-ph * 5) * math.sin(ph * 30)
        o.append(blob(ellipse_pts(gx + 6, TOP_Y - 40, 44, 7, 12), "#b98350", .8))
        o.append(PR.glass(gx, TOP_Y - 44 - jump, 1.1, .86, 1.5 * math.sin(ph * 28) * math.exp(-ph * 7) if ph > 0 else 0, sl, i % 3 == 0, seed=i))
    o.append(PR.bottle(850, TOP_Y - 40, 1.1, .7, 0, 2 * math.sin(t * 5), True, False, seed=3))
    # кот справа на столе
    st = cstate(t, look=(-.35, .1), turn=-.15, blink=blink_of(t, (35.4, 36.45)), ear=4 * bump(t, T_VOS, .4), perk=.1, tail=6 * math.sin(t * 2.2), smile=0,
                flame_e=1.2 + .2 * math.sin(t * 8))
    cxc, cyc = 945, TOP_Y - 50
    o.append(Cat.draw(cxc, cyc, .56, st, t))
    sh = 8 * u
    cam = lib.cam(380 + 195 * u, 930 + 90 * u, z, 1.0 * (1 - u) - .4 * bump(t, T_VOS, .35))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════════ s15 28.9–31.1: кот лакает ═════════════════════════════
T_MISKI = wt(78)          # 30.62


def frame15(t):
    u = clamp((t - 28.7) / 2.6)
    z = 1.05 + .42 * ease_io(u) + .12 * math.exp(-(t - 28.7) * 9)
    set_ink(z)
    o = [wall_floor(960, "#dcebe0", "#c6d9cd", "#c8955f", "#a97542"), window(700, 160, 980, 580, t)]
    k = 1.8
    base_y, bowl_by, bk = 1100, 1270, 2.4
    ph = 2 * math.pi * 2.4 * t
    cyc = .5 + .5 * math.sin(ph)
    drop = 1.9 + .65 * cyc if t > 28.74 else 1.9
    tongue = clamp((cyc - .5) / .3)
    rip = .45 + .55 * bump(t, T_MISKI, .6) + .35 * tongue
    st = cstate(t, look=(0, .9), turn=0.0, blink=.45, ear=6 * bump(t, T_MISKI, .4) + 2 * math.sin(t * 7), perk=0.0, tail=8 * math.sin(t * 3.2),
                smile=0, flame_e=1.5 + .4 * math.sin(t * 9), drop=drop, tongue=tongue, tilt=-2 * cyc)
    o.append(blob(ellipse_pts(540, base_y + 40, 330, 30, 20), "#7a5430", .55))
    o.append(PR.bowl(540, bowl_by, bk, .8, t, rip))
    o.append(Cat.draw(540, base_y, k, st, t))
    rimc = bowl_by - 56 * bk
    c = lib.clip_rect(0, rimc - 2, 1080, 800)
    o.append(f'<g clip-path="url(#{c})">{PR.bowl(540, bowl_by, bk, .8, t, rip)}</g>')
    fx, fy = 540 + (995 - 836) * k, base_y + (1076 - 1306) * k - 30
    o.append(sparks(t, fx, fy, 7, 23, 150))
    cam = lib.cam(540 + 10 * math.sin(t * 1.1), 900 + 60 * ease_io(u), z, 2.0 * (1 - ease_out(clamp((t - 28.7) / .5))) - .6 * u)
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════════ s16 31.1–33.2: вид сверху ═════════════════════════════
T_STAK = wt(84)           # 32.53


def top_glass(x, y, k=1.5, seed=0):
    r = PR.GLASS_W / 2 * k
    o = blob(ellipse_pts(x + 10, y + 12, r + 4, r + 4, 18), "#b88a55", .9)
    o += shape(ellipse_pts(x, y, r, r, 18), PR.C_GLASS, blob(ellipse_pts(x, y, r - 7, r - 7, 16), PR.C_GLASS_IN), w=3.4, seed=7000 + seed)
    o += line([(x - r * .62, y - r * .32), (x - r * .3, y - r * .68)], 5, PR.C_WHITE, taper=.5, wmin=.3, seed=7010 + seed)
    return o


def lying_glass(x, y, tilt, k=1.5, seed=0):
    return blob(ellipse_pts(x + 8, y + 14, PR.GLASS_H * k * .55, 22 * k, 16, rot=tilt - 90), "#b88a55", .9) + PR.glass(x, y, k, 0.0, tilt, 0, False, seed)


def cat_top(t, cx, cy, look=0.0):
    """Кот сверху: голова над мискй, спина, лапы, хвост с огоньком."""
    C_, SH, FU, ED = Cat.CAT, Cat.CAT_SH, Cat.CAT_FUR, Cat.CAT_EDGE
    br = 1 + .012 * math.sin(t * 2.4)
    o = []
    # хвост
    tw = 12 * math.sin(t * 2.2)
    tp = [(cx + 30, cy + 520), (cx + 150 + tw * .3, cy + 580), (cx + 250, cy + 520), (cx + 280, cy + 410 + tw), (cx + 240, cy + 330 + tw)]
    S = lib.sample(tp, False, 3.0)
    S = np.array(S)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = np.linspace(46, 22, len(S))
    Lp, Rp = S + N * Wd[:, None] / 2, S - N * Wd[:, None] / 2
    outline = [tuple(p) for p in Lp] + [tuple(S[-1] + Tg[-1] * 16)] + [tuple(p) for p in Rp[::-1]]
    o.append(shape(outline, C_, blob([tuple(p) for p in Rp] + [tuple(p) for p in (Rp + N * 0)[::-1]], SH, 0), w=4.8, seed=7100))
    tipx, tipy = S[-1]
    o.append(f'<g transform="translate({tipx - 995 + 6:.1f} {tipy - 1076 + 10:.1f})">{Cat.flame(t, 1.5, 1.4)}</g>')
    # тело
    body = ellipse_pts(cx, cy + 300 * br, 108, 185 * br, 20)
    hip = ellipse_pts(cx, cy + 400, 128, 105, 18)
    inner = blob(ellipse_pts(cx + 70, cy + 340, 70, 190, 14), SH, .85) + blob(ellipse_pts(cx - 30, cy + 300, 30, 150, 12), FU, .55)
    for i in range(6):
        yy = cy + 190 + 55 * i
        inner += line([(cx - 40 + 8 * (i % 2), yy), (cx - 22, yy + 26)], 2.6, ED, seed=7120 + i, op=.8)
    o.append(shape(hip, C_, "", w=4.8, seed=7101))
    o.append(shape(body, C_, inner, w=4.8, seed=7102))
    # передние лапы к миске
    for sx, sd in ((-1, 7103), (1, 7104)):
        o.append(shape(ellipse_pts(cx + sx * 84, cy + 100, 34, 70, 14), C_, blob(ellipse_pts(cx + sx * 96, cy + 110, 18, 50, 10), SH, .6), w=4.6, seed=sd))
    # голова: нагибается и опускается к воде
    dip = 12 * math.sin(2 * math.pi * 2.4 * t)
    hx, hy = cx, cy + 20 + dip * .6
    o.append(shape(ellipse_pts(hx, hy + 70, 78, 70, 16), C_, "", w=4.6, seed=7105))      # шея-загривок
    # уши: правое торчком, левое загнуто
    o.append(shape([(hx + 40, hy + 20), (hx + 120, hy - 50), (hx + 96, hy + 70, 1)], C_, blob([(hx + 62, hy + 24), (hx + 108, hy - 24), (hx + 90, hy + 50)], "#9b6150"), w=4.4, seed=7106))
    o.append(shape([(hx - 44, hy + 30), (hx - 116, hy + 8), (hx - 112, hy + 66), (hx - 76, hy + 80, 1)], C_, blob([(hx - 56, hy + 50), (hx - 88, hy + 42)], SH, .8), w=4.4, seed=7107))
    skull = ellipse_pts(hx, hy + 30, 78, 86, 18)
    o.append(shape(skull, C_, blob(ellipse_pts(hx + 34, hy + 40, 40, 70, 12), SH, .8) + blob(ellipse_pts(hx - 18, hy + 30, 20, 50, 10), FU, .6), w=4.8, seed=7108))
    o.append(line([(hx - 16, hy + 80), (hx - 8, hy + 20)], 3, ED, seed=7109, op=.8) + line([(hx + 10, hy + 84), (hx + 14, hy + 28)], 3, ED, seed=7110, op=.8))
    # мордочка и язык
    o.append(shape(ellipse_pts(hx, hy - 52, 34, 28, 12), C_, "", w=4.0, seed=7111))
    tg = clamp(math.sin(2 * math.pi * 2.4 * t + .6) * 1.4)
    if tg > .05:
        o.append(shape([(hx - 8, hy - 70), (hx + 8, hy - 70), (hx + 7, hy - 70 - 30 * tg), (hx, hy - 76 - 30 * tg), (hx - 7, hy - 70 - 30 * tg)], "#e8808c", "", w=2.6, seed=7112))
    for sx in (-1, 1):
        for j in range(3):
            o.append(line([(hx + sx * 28, hy - 50 + j * 7), (hx + sx * (80 + 8 * j), hy - 66 + j * 14)], 2, "#cfd5d6", seed=7130 + j + sx, op=.9))
    return "".join(o)


def frame16(t):
    u = clamp((t - 30.9) / 2.5)
    z = 1.12 - .1 * ease_io(u)
    set_ink(z)
    o = [blob(rrect(-400, -400, 1500, 2400), "#d3a066")]
    for i in range(-6, 14):
        x = i * 150 + 40
        o.append(line([(x, -400), (x, 2400)], 3, "#b98650", taper=0, wmin=1, seed=7200 + i, op=.8))
        for j, yy in enumerate(range(-300, 2300, 520)):
            o.append(line([(x - 8, yy + (i * 97) % 400), (x + 8, yy + (i * 97) % 400)], 3, "#a97542", taper=0, wmin=1, seed=7230 + i * 7 + j))
    BX, BY, BK = 540, 640, 2.3
    rip = .7 + .3 * math.sin(t * 6)
    R = 85 * BK
    o.append(blob(ellipse_pts(BX + 14, BY + 20, R + 10, R + 6, 22), "#a97542", .8))
    o.append(shape(ellipse_pts(BX, BY, R, R, 26), PR.C_BOWL, "", w=4.0, seed=7300))
    o.append(shape(ellipse_pts(BX, BY, R - 18, R - 18, 26), PR.C_BOWL_BAND, "", w=2.6, seed=7301))
    o.append(shape(ellipse_pts(BX, BY, R - 34, R - 34, 26), "#CDBA98", "", w=2.6, seed=7302))
    wat = ellipse_pts(BX, BY, R - 52, R - 52, 24)
    ins = blob(ellipse_pts(BX - 26, BY - 26, R * .45, R * .35, 14, rot=-30), PR.C_WATER_TOP)
    for j in range(3):
        uu = (t * 1.3 + j / 3) % 1.0
        rr = 24 + uu * (R - 90)
        ins += f'<ellipse cx="{BX}" cy="{BY - 40}" rx="{rr:.1f}" ry="{rr:.1f}" fill="none" stroke="#ffffff" stroke-width="{max(1.0, 5 * (1 - uu)):.1f}" opacity="1"/>' if uu < .85 else ""
    o.append(shape(wat, PR.C_WATER, ins, w=2.8, seed=7303))
    # стаканы вокруг
    o.append(top_glass(170, 470, 2.1, 1))
    o.append(top_glass(915, 905, 2.1, 2))
    o.append(top_glass(860, 1250, 2.0, 3))
    o.append(lying_glass(850, 330, 64, 2.0, 4))
    o.append(lying_glass(120, 1150, 100, 2.0, 5))
    # откатывающийся стакан: лежит осью по горизонтали и катится вверх на «стаканов»
    rolled = 170 * ease_out(clamp((t - T_STAK) / .7), 2.2)
    wob = 4 * math.sin((t - T_STAK) * 9) * math.exp(-max(0, t - T_STAK) * 3) if t > T_STAK else 0
    o.append(lying_glass(215, 1000 - rolled, 92 + wob, 2.0, 6))
    o.append(cat_top(t, BX, BY + 120, 0))
    sx = 6 * math.sin(t * .9)
    cam = lib.cam(540 + sx, 940 + 10 * math.sin(t * .7), z, 6 * math.sin(2 * math.pi * (t - 31.1) / 6))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════════ s09 14.7–16.5: облако-мысль ═════════════════════════════
T_NUZHNO = wt(38)         # 15.59


def qmark(x, y, s, seed=0, col=INK, w=9.0, op=1.0):
    pts = [(-20, -22), (-6, -40), (16, -36), (22, -16), (10, 2), (0, 14), (0, 26)]
    P = [(x + px * s, y + py * s) for px, py in pts]
    return line(P, w * s ** .5, col, taper=.35, wmin=.5, seed=7700 + seed, op=op) + blob(ellipse_pts(x, y + 50 * s, 5.5 * s, 5.8 * s, 8), col, op)


def cloud_pts(cx, cy, rx, ry, n=9, bump_=.2, ph=0.0):
    pts = []
    for i in range(n * 4):
        a = 2 * math.pi * i / (n * 4)
        r_ = 1 + bump_ * (1 if i % 4 in (1, 2) else -.2)
        pts.append((cx + rx * r_ * math.cos(a), cy + ry * r_ * math.sin(a)))
    return pts


def frame09(t):
    u = clamp((t - 14.5) / 2.2)
    z = 1.05 + .25 * ease_io(u) + .05 * math.exp(-(t - 14.5) * 7)
    set_ink(z)
    o = [wall_floor(1250, "#f3e4c4", "#e5cfa6"), window(40, 420, 280, 820, t)]
    bs = 1.0
    scr = math.sin(t * 10.5)
    hip = (410, 1390 + 3 * math.sin(t * 2.4))
    wob = bump(t, T_NUZHNO, .4)
    exp = dict(lid=.85, look=(.25, -.8), closed=blink_of(t, (15.0, 16.2)), brows=("worry", "up", clamp((t - 14.8) / .5)), mouth="flat", blush=0)
    wr = (hip[0] - 40 + 12 * scr, hip[1] - 676 + 8 * math.sin(t * 10.5 + 1))
    d = dima(hip, bs, .02, {"n": ("ik", wr, 1), "f": ("ik", (hip[0] + 130, hip[1] - 230), -1)},
             {"n": open_hand(.55, (.85, -.35), .25, .3, flip=1, k=1.0), "f": open_hand(.3, (1, .2), .15, .3)}, exp, feet=None,
             head_ang=-.03 + .03 * scr + .04 * wob)
    o.append(d["arm_f"] + d["body"] + d["arm_n"])
    # облако-мысль: вырастает на «Сколько», дрожит на «нужно»
    pop = back_out(clamp((t - 14.52) / .5), 1.5)
    sh = 7 * wob * math.sin(t * 60) if wob else 0.0
    ccx, ccy = 580 + sh, 300 + 6 * math.sin(t * 2.0)
    cl = []
    cl.append(shape(cloud_pts(ccx, ccy, 300, 175, 9, .17), "#fbfaf4", "", w=5.0, seed=7600))
    for i, (gk, gx, gl, sd) in enumerate(((1.25, 400, .72, 1), (1.9, 560, .78, 2), (2.6, 745, .85, 3))):
        gp = clamp((t - (14.78 + .13 * i)) / .3)
        if gp <= 0:
            continue
        sc_ = back_out(gp, 1.8)
        cl.append(PR.glass(gx, ccy + 125, gk * sc_, gl, 2.5 * math.sin(t * 5 + i), 5 * math.sin(t * 7 + 2 * i), False, seed=sd))
    for i, (qx, qy, qs) in enumerate(((330, ccy - 80, .8), (500, ccy - 100, 1.0), (665, ccy - 112, .85), (830, ccy - 40, .95))):
        qp = clamp((t - (14.9 + .1 * i)) / .25)
        if qp > 0:
            cl.append(qmark(qx + 5 * math.sin(t * 6 + i), qy + 6 * math.sin(t * 5 + i) - 4 * wob, qs * back_out(qp, 1.8), i, "#d8483c", 8.5))
    o.append(f'<g transform="translate({ccx:.1f} {ccy:.1f}) scale({pop:.4f}) translate({-ccx:.1f} {-ccy:.1f})">{"".join(cl)}</g>')
    # пузыри мысли к голове
    for i, (bx, by, br_) in enumerate(((610, 600, 32), (585, 662, 21), (570, 708, 13))):
        bp = clamp((t - (14.6 + .08 * i)) / .25)
        if bp > 0:
            o.append(shape(ellipse_pts(bx, by + 3 * math.sin(t * 3 + i), br_ * back_out(bp, 1.6), br_ * back_out(bp, 1.6), 12), "#fbfaf4", "", w=4.0, seed=7620 + i))
    cam = lib.cam(600 - 30 * ease_io(u), 640 + 70 * ease_io(u), z, 1.2 * math.sin(t * 2.2) + 2.0 * math.exp(-(t - 14.5) * 6) - 1.5 * wob)
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════════ s10 16.5–19.1: панорама ═════════════════════════════
GY = 1250                       # земля (стопы)
T_POG, T_DVIZH, T_CHEL = wt(41), wt(42), wt(45)         # 16.54, 17.27, 18.23
CAMK = [(16.3, 520), (17.0, 620), (17.35, 800), (18.2, 1700), (18.75, 2150), (19.3, 2420)]


def cam_x(t):
    from scipy.interpolate import PchipInterpolator
    if "pc" not in _HW:
        _HW["pc"] = PchipInterpolator([a for a, _ in CAMK], [b for _, b in CAMK])
    return float(_HW["pc"](clamp(t, 16.3, 19.3)))


def sky_bg(t, cx):
    g = lib.lin_grad([(0, "#86c5ee", 1), (.7, "#cfe9f6", 1), (1, "#eaf5ea", 1)], 0, 0, 0, 1)
    o = f'<rect width="1080" height="1500" fill="url(#{g})"/>'
    return o


def hill_layer(cx, par, y0, col, seed, amp=90):
    off = cx * (1 - par)
    pts = []
    for i in range(-3, 14):
        x = i * 420 + off - (off // 420) * 420 - 420
        pts.append((x, y0 - amp * (.5 + .5 * math.sin(i * 1.7 + seed))))
    P = [(p[0] - (cx - 540) * 0, p[1]) for p in pts]
    return blob(P + [(P[-1][0], 1500), (P[0][0], 1500)], col)


def tree(x, y, k, col="#5f9a52"):
    o = shape(rrect(x - 14 * k, y - 150 * k, x + 14 * k, y, 4 * k), "#7a5430", "", w=3.6, seed=int(x) % 997)
    o += shape(ellipse_pts(x, y - 220 * k, 90 * k, 100 * k, 14), col, blob(ellipse_pts(x + 30 * k, y - 200 * k, 52 * k, 70 * k, 10), mix(col, "#000000", .2), .9), w=4.4, seed=int(x) % 991)
    return o


def sun(x, y, t, r=120):
    o = ""
    for i in range(14):
        a = 2 * math.pi * i / 14 + t * .6
        l1, l2 = r * 1.18, r * (1.55 + .12 * math.sin(t * 7 + i))
        o += line([(x + l1 * math.cos(a), y + l1 * math.sin(a)), (x + l2 * math.cos(a), y + l2 * math.sin(a))], 11, "#f2a31c", taper=.4, wmin=.5, seed=7800 + i)
    o += shape(ellipse_pts(x, y, r, r, 20), "#ffd23c", blob(ellipse_pts(x + 26, y + 26, r * .8, r * .8, 14), "#f7b82a", .75), w=5.4, seed=7820)
    return o


def person(who, x, bs, hip_dy, arms, hands, expr, feet=None, lean=0.0, head_ang=0.0, torso_k=1.0):
    hip = (x, GY - 610 * bs * .985 * (torso_k * 0 + 1) + hip_dy)
    d = dima(hip, bs, lean, arms, hands, expr, feet=feet, head_ang=head_ang, torso_k=torso_k, who=who)
    return d, hip


def stand_feet(hip, bs, sp=26):
    return {"n": ((hip[0] + sp * bs, GY - 4), 0.0), "f": ((hip[0] - sp * bs, GY - 4), 0.0)}


def sweat(t, hx, hy, s, n=5, seed=3):
    rs = np.random.RandomState(seed)
    o = ""
    for i in range(n):
        per = rs.uniform(.55, .9)
        ph = rs.uniform(0, per)
        u = ((t + ph) % per) / per
        o += PR.droplet(hx + rs.uniform(-60, 60) * s + 30 * s * u * (1 if i % 2 else -1), hy + (rs.uniform(-30, 10) + 160 * u * u) * s, s * 1.2 * (1 - .3 * u), 10 * (1 if i % 2 else -1), seed=i)
    return o


def frame10(t):
    cx = cam_x(t)
    zk = clamp((t - 18.55) / .75)
    z = 1.0 + .58 * ease_io(zk) + .08 * math.exp(-(t - 16.3) * 8)
    set_ink(z)
    scn = []
    # дальние слои с параллаксом
    scn.append(sun(760 + cx * .5 - 540 * .5 + 0 - 40 + 0 * cx, 300, t, 130) if cx < 1800 else "")
    scn.append(hill_layer(cx, .35, 1010, "#a7d29a", 1.0, 120))
    scn.append(hill_layer(cx, .6, 1130, "#86bf78", 2.3, 80))
    for xx in range(-200, 4400, 560):
        if abs(xx - cx) < 1100:
            scn.append(tree(xx + 130, GY - 6, .9 + .15 * ((xx // 560) % 3), ["#5f9a52", "#6fa95a", "#4f8a4a"][(xx // 560) % 3]))
    scn.append(blob(rrect(-300, GY - 4, 4800, 2000), "#8cc47c"))
    scn.append(blob(rrect(-300, GY + 60, 4800, GY + 330), "#d9c498"))
    scn.append(line([(-300, GY + 60), (4800, GY + 60)], 4, "#a8925f", taper=0, wmin=1, seed=7900))
    for i in range(0, 4800, 210):
        scn.append(line([(i - 300, GY + 190), (i - 220, GY + 194)], 4, "#c1ab7c", taper=.3, wmin=.4, seed=7910 + i))
    # ── Дима: стоит и утирает пот → бежит трусцой
    jog_u = clamp((t - 16.95) / .45)
    dx_ = 420 + (t > 17.0) * 1500 * ease_in(clamp((t - 17.0) / 1.6), 1.25) * .0
    runx = 520 + 780 * ease_in(clamp((t - 16.9) / .5), 1.5) * .0
    x_d = 430 + max(0.0, t - 16.95) * 640 * ease_in(clamp((t - 16.95) / .4), 1.0) if t > 16.95 else 430
    bs = .62
    ph = 2 * math.pi * 2.6 * (t - 17.0)
    if t < 17.0:
        wip = ease_io(clamp((t - 16.3) / .25)) * (1 - ease_io(clamp((t - 16.95) / .1)))
        hip = (x_d, GY - 610 * bs * .985)
        wr = (hip[0] + 40 * bs - 40 * bs * math.sin(t * 9) * wip, hip[1] - 640 * bs + 6 * math.sin(t * 9))
        exp = dict(lid=.35, look=(.2, .2), closed=blink_of(t, (16.6,)) * .0, brows="worry", mouth="tired", flush=.5, blush=0)
        hips_ = hip
        arms = {"n": ("ik", (hip[0] + 90 * bs - 40 * bs * math.sin(t * 9) * wip, hip[1] - 560 * bs - 10 * bs * math.sin(t * 9)), 1), "f": ("ik", (hip[0] + 60 * bs, hip[1] + 330 * bs), -1)}
        hands = {"n": open_hand(.3, (1, -.2), .1, .3), "f": open_hand(.2, (0, 1), .1, .3, flip=-1)}
        dd = dima(hip, bs, .03, arms, hands, exp, feet=stand_feet(hip, bs), head_ang=.03 * math.sin(t * 9) * wip, who="dima")
        scn.append(blob(ellipse_pts(hip[0], GY + 14, 130, 14, 14), "#6a9a5c", .8))
        scn.append(dd.get("legs", "") + dd["arm_f"] + dd["body"] + dd["arm_n"])
        scn.append(sweat(t, hip[0] + 60 * bs, hip[1] - 560 * bs, bs * 1.1))
    else:
        bob = 10 * abs(math.sin(ph)) * bs
        hip = (x_d, GY - 610 * bs * .985 - bob)
        feet = {}
        for sd, off in (("n", 0.0), ("f", math.pi)):
            p_ = ph + off
            ax = hip[0] + 170 * bs * math.sin(p_) * 1.0
            lift = max(0.0, math.cos(p_)) * 190 * bs
            feet[sd] = ((ax, GY - 4 - lift), -.2 * max(0.0, math.cos(p_)))
        arms = {"n": ("ik", (hip[0] + 90 * bs + 150 * bs * math.sin(ph + math.pi), hip[1] - 250 * bs - 50 * bs * math.cos(ph)), 1),
                "f": ("ik", (hip[0] + 90 * bs + 150 * bs * math.sin(ph), hip[1] - 250 * bs + 50 * bs * math.cos(ph)), -1)}
        hands = {"n": open_hand(.7, (1, -.1), .05, .7), "f": open_hand(.7, (1, -.1), .05, .7)}
        exp = dict(lid=.65, look=(.5, .05), closed=0, brows="det", mouth="flat", flush=.35, blush=0)
        dd = dima(hip, bs, .2, arms, hands, exp, feet=feet, head_ang=.02, who="dima")
        scn.append(blob(ellipse_pts(hip[0] + 10, GY + 14, 150, 14, 14), "#6a9a5c", .8))
        scn.append(dd.get("legs", "") + dd["arm_f"] + dd["body"] + dd["arm_n"])
        scn.append(sweat(t, hip[0] - 40 * bs, hip[1] - 540 * bs, bs * 1.1, 6, 9))
        for i in range(4):
            yy = GY - 20 - i * 50 * bs
            scn.append(line([(hip[0] - 150 * bs - 60 - 40 * i, yy - 160 * bs), (hip[0] - 150 * bs - 150 - 30 * i, yy - 160 * bs)], 6, "#ffffff", taper=.6, wmin=.2, seed=7950 + i, op=1.0))
    # ── три разных человека
    def holder(who, x, bs_, glass_k, glass_level, expr, tk=1.0, side="n", bag=False):
        sp = 22
        bob = 2 * math.sin(t * 3.0 + x)
        hip = (x, GY - 610 * bs_ * .985 * tk - bob * .3)
        hip = (hip[0], GY - 600 * bs_)
        gap = clamp((t - (T_CHEL + .12 * (x > 2600) + .12 * (x > 2900))) / .5)
        raise_ = ease_io(gap)
        wr_ = (hip[0] + 130 * bs_ * 1.1, hip[1] - 300 * bs_ * tk * .95 - 20 * bs_ * math.sin(t * 5 + x) * .0)
        low_ = (hip[0] + 40 * bs_, hip[1] + 380 * bs_ * tk)
        arms = {"n": ("ik", wr_, -1), "f": ("ik", (hip[0] + 30 * bs_, hip[1] + 330 * bs_ * tk), -1)}
        hands = {"n": open_hand(.8, (.05, -1), .05, .75, flip=-1), "f": open_hand(.25, (0, 1), .1, .3, flip=-1)}
        if bag:
            arms = {"n": ("ik", low_, -1), "f": ("ik", wr_, -1)}
            hands = {"n": open_hand(.8, (0, 1), .05, .6, flip=-1), "f": open_hand(.8, (.05, -1), .05, .75, flip=-1)}
        dd = dima(hip, bs_, .0, arms, hands, expr, feet=stand_feet(hip, bs_, 20), torso_k=tk, who=who)
        out = [blob(ellipse_pts(hip[0], GY + 12, 110 * bs_ / .62, 12, 14), "#6a9a5c", .8), dd.get("legs", "") + dd["arm_f"] + dd["body"]]
        key = "f" if bag else "n"
        wrx, wry = dd["wrist"][key]
        gb = (wrx + 6 * bs_, wry + 40 * bs_)
        out.append(PR.glass(gb[0], gb[1], glass_k, glass_level, 2 * math.sin(t * 4 + x), 5 * math.sin(t * 6 + x), False, seed=int(x) % 7))
        if bag:
            bx_, by_ = dd["wrist"]["n"]
            out.append(f'<g transform="translate({bx_:.1f} {by_ + 6:.1f}) rotate({3 * math.sin(t * 3):.1f})">'
                       + shape(rrect(-52, 24, 52, 118, 14), "#a4473e", blob(rrect(-52, 24, 52, 50, 10), "#7e2f28", .9) + blob(ellipse_pts(0, 70, 8, 8, 8), "#f0d08a"), w=4.2, seed=8010)
                       + line([(-30, 28), (-20, -6), (0, -14), (20, -6), (30, 28)], 5, "#5a3a22", taper=.2, wmin=.8, seed=8011) + "</g>")
        out.append(dd["arm_n"])
        return "".join(out)

    people_on = t > 17.5
    if people_on:
        # высокий весёлый, бабушка с сумкой и маленьким стаканом, спортсмен
        scn.append(holder("friend", 1720, .72, 1.65, .6, dict(lid=1.0, look=(.2, 0.0), closed=blink_of(t, (18.6,)), brows="up", mouth="laugh", open=.5, smile=.8), tk=1.1))
        scn.append(holder("granny", 2090, .54, .72, .9, dict(lid=.9, look=(.25, .05), closed=blink_of(t, (18.9,)), mouth="smile", smile=.9), tk=.95, bag=True))
        scn.append(holder("sport", 2440, .64, 1.1, .75, dict(lid=.8, look=(.5, -.05), closed=blink_of(t, (19.0,)), brows="calm", mouth="grin", open=.3, smile=.9), tk=1.0))
    cam = lib.cam(cx + 20 * math.sin(t * 2) + 60 * ease_io(zk), 820 + 40 * ease_io(zk), z, 1.0 * math.sin(t * 3) * (t > 17.0))
    g_ = lib.lin_grad([(0, '#7cc0ec', 1), (.62, '#cfe9f6', 1), (1, '#eaf5ea', 1)], 0, 0, 0, 1)
    return f'<rect x="-300" y="-300" width="1680" height="2520" fill="url(#{g_})"/><g transform="{cam}">{"".join(scn)}</g>'


THIGH_SHIN = 610.0


def frame(sid, t):
    lib.dyn_begin()
    body = {"s09": frame09, "s10": frame10, "s15": frame15, "s16": frame16, "s17": frame17, "s18": frame18}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#e9d8bc"/>{body}')
