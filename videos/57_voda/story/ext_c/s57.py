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


def frame(sid, t):
    lib.dyn_begin()
    body = {"s17": frame17, "s18": frame18}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#e9d8bc"/>{body}')
