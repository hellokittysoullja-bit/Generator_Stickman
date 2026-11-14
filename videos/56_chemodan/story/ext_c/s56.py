"""Рилс 56, группа C: s10 s11 s12 s14 s15 s16. frame(sid, t) -> SVG 1080×1920."""
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
import suit as SU  # noqa: E402
from lib import (INK, back_out, blob, blur, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape,  # noqa: E402
                 smooth, spring, svg)

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


# ═══════════ общее: комната-фон, Дима, кот ═══════════
WALL, WALL_SH, FLOOR, FLOOR_SH = "#f0e2c8", "#e0cca8", "#c8955f", "#a97542"


def dima(hip, bs, lean, arms, hands, expr, feet=None, head_ang=0.0, head_off=(0, 0), torso_k=1.0):
    p = dict(hip=tuple(hip), scale=bs, lean=lean, torso_k=torso_k, feet=feet, arms=arms, hands=hands, expr=expr, head_ang=head_ang,
             head_off=head_off, hood=0.0, strings=(0, 0))
    return people.draw(p, "dima")


def open_hand(c=.2, d=(1, 0), spread=.2, thumb=.2, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(c, c, c, c * .9), spread=spread, thumb=thumb, bend=.1, k=k)


def cat_head(x, y, k, st, t, rot=0.0):
    """Голова кота (центр морды между глаз в (x, y)), масштаб k."""
    return (f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f}) translate(-836 -1072)">{Cat.head(st, t)}</g>')


def cstate(t, **kw):
    st = dict(look=(-.6, .1), turn=-.4, blink=0.0, ear=0, perk=0.0, tail=0.0, smile=0, tilt=0, flame_e=1.0)
    st.update(kw)
    return st


def zig(x, y, ang, L, w=7, seed=0, col=INK, n=4, amp=14):
    """Зигзаг-штрих звука (мяуканье, тряска)."""
    a = math.radians(ang)
    d = np.array([math.cos(a), math.sin(a)])
    nn = np.array([-d[1], d[0]])
    pts = [(x, y)] + [(x + d[0] * L * (i + 1) / n + nn[0] * amp * (1 if i % 2 == 0 else -1), y + d[1] * L * (i + 1) / n + nn[1] * amp * (1 if i % 2 == 0 else -1)) for i in range(n)]
    return line(pts, w, col, taper=.5, wmin=.25, seed=seed)


def arc_wave(cx, cy, r, a0, a1, w=7, seed=0, col=INK):
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 9)]
    return line(pts, w, col, taper=.5, wmin=.2, seed=seed)


def floor_bg(horizon=1180, light=1.0):
    o = blob(rect_pts(-200, -200, 1300, horizon), WALL)
    o += blob(rect_pts(-200, horizon, 1300, 2200), FLOOR)
    o += blob(rect_pts(-200, horizon - 40, 1300, horizon), WALL_SH, .8)
    o += line([(-200, horizon), (1300, horizon)], 5, "#7a5430", taper=0, wmin=1, seed=11)
    for i, y in enumerate((horizon + 120, horizon + 290, horizon + 480, horizon + 700)):
        o += line([(-200, y), (1300, y + 4)], 3, FLOOR_SH, taper=0, wmin=1, seed=20 + i, op=.8)
    return o


def window_light(x0, y0, x1, y1, op=.35):
    return blob([(x0, y0), (x0 + 220, y0), (x1 + 220, y1), (x1, y1)], "#fff6d8", op)


# ═════════════════════════════ s10 17.44–19.28 ═════════════════════════════
T_OKAZ, T_KOT = wt(43), wt(44)     # 17.968, 18.56
T_S10 = 17.44


def suit_s10(t):
    """Чемодан: дёргается, замок щёлкает на «оказался», крышка приоткрывается, на «кот» распахивается; возвращает (S, shake)."""
    if t < T_OKAZ:
        th = 0.0
    elif t < T_KOT - .12:
        th = 7 * ease_out((t - T_OKAZ) / .12, 2) + 1.5 * osc(t, 6)
    else:
        u = (t - (T_KOT - .12)) / .22
        th = 7 + 78 * ease_out(u, 2.2) + 7 * spring(t - T_KOT - .1, 3.2, 6) * (1 if t > T_KOT + .1 else 0)
    return th


def frame10(t):
    # камера: наезд на щель, отскок на «кот»
    pre = clamp((t - 17.24) / (T_KOT - 17.24))
    z = 1.12 + .2 * ease_io(pre) + .07 * bump(t, T_OKAZ, .25)
    z += -.07 * bump(t, T_KOT, .3) + (0.05 * (1 - ease_out((t - T_KOT) / .5, 2)) if t > T_KOT else 0) - .12 * smooth(T_KOT + .1, T_KOT + .7, t)
    shake = 0.0
    if t < T_KOT:
        amp = 7 + 11 * smooth(17.24, T_OKAZ, t)
        shake = amp * osc(t, 9.5)
    sx = shake
    sy = -abs(6 * osc(t, 4.7)) if t < T_OKAZ else -3 * abs(osc(t, 11))
    BY, CX = 1300, 720
    S = SU.Suit(CX, BY, W=600, D=260, Hb=210, e=32, th=suit_s10(t), clothes=True)
    set_ink(z)
    body = [floor_bg(1000), window_light(560, 0, 100, 1000)]
    body.append(blob(ellipse_pts(CX, BY + 20, 340, 30, 20), "#5a3a1c", .35))
    rec = smooth(T_KOT - .02, T_KOT + .4, t)
    lean = .30 - .52 * rec + .02 * osc(t, 7) * (1 - rec)
    hip = (260 - 22 * rec, 868 - 18 * rec)
    bs = .75
    shn = (hip[0] + 5 * bs - 220 * rec * .3, hip[1] - 400 * bs * (1 - .02 * rec))
    exp = dict(lid=.7 + .25 * rec, look=(.7, .5), brows="worry" if rec < .1 else "up", mouth="flat" if rec < .1 else "talk", open=.9 * rec + .2, flush=.1)
    ph = lambda a, b: (a[0] + (b[0] - a[0]) * rec, a[1] + (b[1] - a[1]) * rec)
    tn = ph((520, 1010 + 8 * math.sin(t * 12)), (shn[0] + 250, shn[1] - 40))
    tf = ph((470, 985), (shn[0] + 200, shn[1] - 120))
    feet = {"n": (ph((350, 1296), (322, 1296)), 0.0), "f": (ph((250, 1300), (222, 1300)), 0.0)}
    d = dima(hip, bs, lean, {"n": ("ik", tn, -1), "f": ("ik", tf, -1)},
             {"n": open_hand(.1 + .1 * (1 - rec), (1, -.3), .3, .1), "f": open_hand(.1, (1, -.3), .3, .1)}, exp, feet=feet, head_ang=.06 - .25 * rec)
    body.append(d.get("legs", "") + d["arm_f"] + d["body"])
    body.append(f'<g transform="translate({sx:.2f} {sy:.2f})">')
    if S.th > 2:
        body.append(S.interior(22))
    if S.th >= 35:
        body.append(S.lid())
    if S.th > 20:
        rise = (ease_out(clamp((t - T_KOT + .02) / .3), 2.6) + .04 * spring(t - T_KOT - .3, 2.6, 6) * clamp((t - T_KOT - .3) * 9)) if t > T_KOT - .02 else 0
        ch_y = 1215 - 285 * clamp(rise, 0, 1.06)
        glare = smooth(T_KOT + .3, T_KOT + .55, t)
        st = cstate(t, look=(-1.0, .35), turn=-.65 * (.4 + .6 * glare), blink=.5 * glare + .9 * (1 - smooth(T_KOT, T_KOT + .18, t)), ear=-5 * glare)
        cid = lib.clip_rect(0, 0, 1080, BY - 20)
        body.append(f'<g clip-path="url(#{cid})">{cat_head(CX + 20, ch_y + 30, 1.3, st, t, rot=-5 + 10 * glare)}</g>')
    body.append(S.front(zip_pull=0))
    if S.th < 35:
        body.append(S.lid())
    if T_S10 - .2 <= t < T_KOT - .06:
        ph_ = (t * 4.6) % 1
        L0, L1 = 30 + 70 * ph_, 60 + 110 * ph_
        for sgn in (-1, 1):
            for k in range(3):
                a_ = math.radians(-90 + sgn * (28 + 24 * k))
                cx0 = CX + sgn * 340 if sgn > 0 else CX + 40
                body.append(line([(cx0 + L0 * math.cos(a_), 930 + L0 * math.sin(a_)), (cx0 + L1 * math.cos(a_), 930 + L1 * math.sin(a_))],
                                 8 * (1 - ph_) + 2, INK, seed=3300 + k + (sgn > 0) * 4, taper=.5))
    body.append("</g>")
    if T_OKAZ <= t < T_OKAZ + .22:
        u = (t - T_OKAZ) / .22
        for k in range(7):
            a = math.radians(-170 + 26 * k)
            r = 40 + 90 * ease_out(u)
            x, y = CX + sx + r * math.cos(a), 1110 + r * math.sin(a) * .7
            body.append(line([(x, y), (x + 36 * math.cos(a) * (1 - u), y + 36 * math.sin(a) * (1 - u))], 7 * (1 - u) + 1, "#ffd24a", seed=3400 + k, taper=.4))
    body.append(d["arm_n"])
    kk = ease_io(pre) * (1 - smooth(T_KOT, T_KOT + .5, t))
    ccx, ccy = 590 + 70 * kk - 70 * smooth(T_KOT, T_KOT + .6, t), 920 + 80 * kk
    return f'<g transform="{lib.cam(ccx + sx * .3, ccy + sy * .3, z, 2.0 * bump(t, T_KOT, .4))}">{"".join(body)}</g>'


# ═════════════════════════════ диспетчер ═════════════════════════════
def frame(sid, t):
    lib.dyn_begin()
    body = {"s10": frame10}[sid](t)
    return svg(f'<rect width="1080" height="1920" fill="#e9d8bc"/>{body}')
