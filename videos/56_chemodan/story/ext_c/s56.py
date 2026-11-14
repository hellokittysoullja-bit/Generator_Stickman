"""Рилс 56, группа C: s10 s11 s12 s14 s15 s16. frame(sid, t) -> SVG 1080×1920."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import cathang as CatH  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import suit as SU  # noqa: E402
LINING_C = SU.LINING_SH
from lib import (INK, back_out, blob, blur, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rrect, shape,  # noqa: E402
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
    o = blob(rrect(-200, -200, 1300, horizon), WALL)
    o += blob(rrect(-200, horizon, 1300, 2200), FLOOR)
    o += blob(rrect(-200, horizon - 40, 1300, horizon), WALL_SH, .8)
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


# ═════════════════════════════ s11 19.28–20.80 ═════════════════════════════
T_KOTA, T_DOST = wt(45), wt(46)      # 19.28, 19.984


def frame11(t):
    BY, CX = 1300, 720
    S = SU.Suit(CX, BY, W=600, D=260, Hb=210, e=32, th=92, clothes=True)
    z = 1.14 + .05 * bump(t, T_DOST, .35)
    set_ink(z)
    body = [floor_bg(1000), window_light(560, 0, 100, 1000)]
    body.append(blob(ellipse_pts(CX, BY + 20, 340, 30, 20), "#5a3a1c", .35))
    # захват и подъём
    reach = ease_io(clamp((t - 19.08) / .36))                    # рука тянется к коту
    pull = ease_out(clamp((t - 19.52) / (T_DOST - 19.52)), 2.4)  # вытаскивает
    Gx = 740 - 40 * pull + 6 * math.sin(t * 20) * (1 - pull) * clamp((t - 19.5) * 6)
    Gy = 720 - 290 * pull
    hang = t - T_DOST
    swing = 0.0
    if hang > 0:
        swing = 14 * math.exp(-hang * 2.4) * math.sin(hang * 9.5)
    shk = smooth(20.18, 20.26, t) * (1 - smooth(20.58, 20.7, t))
    shake_a = shk * 7 * math.sin(t * 2 * math.pi * 15)
    turn_away = smooth(20.6, 20.95, t)
    lag = (-.8 * math.exp(-hang * 2.2) * math.sin(hang * 9.5 - .9)) if hang > 0 else 0.0
    lag += shk * .5 * math.sin(t * 2 * math.pi * 15 + 1)
    # состояние кота
    ang = smooth(19.3, 19.6, t)
    flick = 1.0 + .7 * math.sin(t * 17) * smooth(20.0, 20.2, t) * (1 - turn_away) - .5 * bump(t, 20.35, .2)
    cs = cstate(t, look=(-1.0 + 1.8 * turn_away, .25 - .5 * turn_away), turn=-.6 + 1.5 * turn_away, blink=.38 + .38 * turn_away + (.5 if (20.22 < t < 20.58 and int(t * 15) % 2 == 0) else 0),
                ear=-6 - 4 * shk, perk=0, smile=0, flame_e=max(.25, flick), tilt=0)
    cs.update(swing=swing + shake_a, lag=lag, shake=shk, sq=1 - .07 * shk * math.sin(t * 2 * math.pi * 15 + .6), head_rot=-8 * ang + 12 * turn_away * 1.2 + 6 * shk * math.sin(t * 2 * math.pi * 15))
    CH = CatH.draw(Gx, Gy, .72 + .18 * (1 - pull), cs, t)
    # Дима: из позы s10 (руки вверх) тянется за котом
    hip = (250 + 50 * reach, 866 + 4 * reach)
    lean = -.22 + .52 * reach - .04 * pull
    bs = .75
    shn = (hip[0] + 100 * reach, hip[1] - 290)
    target = (Gx - 28, Gy - 22)
    tn = ((shn[0] + 250) * (1 - reach) + target[0] * reach, (shn[1] - 40) * (1 - reach) + (target[1] + 8) * reach)
    tf = ((shn[0] + 200) * (1 - reach) + (hip[0] + 300) * reach, (shn[1] - 120) * (1 - reach) + (hip[1] - 120) * reach)
    strain = bump(t, 19.7, .6) + .5 * smooth(T_DOST, T_DOST + .1, t) * (1 - smooth(T_DOST + .2, T_DOST + .5, t))
    wince = smooth(20.2, 20.3, t) * (1 - smooth(20.6, 20.7, t))
    exp = dict(lid=.8 - .25 * strain, look=(.8, -.1 + .2 * reach), brows="worry" if t < 19.4 else ("det" if t > 19.9 else "worry"),
               mouth="grin" if t > T_DOST + .02 else "flat", open=.3, flush=.15 * strain, closed=.65 * wince)
    feet = {"n": ((350 + 40 * reach, 1296), 0.0), "f": ((250 + 30 * reach, 1300), 0.0)}
    d = dima(hip, bs, lean, {"n": ("ik", tn, -1), "f": ("ik", tf, -1)},
             {"n": dict(open_hand(.9, (.55, 1), .02, .9, k=.55)), "f": open_hand(.3, (1, 0), .2, .2)}, exp, feet=feet, head_ang=.06 - .1 * reach)
    body.append(d.get("legs", "") + d["arm_f"] + d["body"])
    body.append(S.interior(22))
    body.append(S.lid())
    cid = lib.clip_rect(0, 0, 1080, BY - 20)
    body.append(f'<g clip-path="url(#{cid})">{CH}</g>')
    body.append(S.front(zip_pull=0))
    body.append(d["arm_n"])
    # пушинки на отряхивании
    if 20.18 < t < 20.72:
        for k_ in range(10):
            a_ = k_ * 2.4 + t * 3
            r_ = 120 + 60 * ((t * 6 + k_ * .37) % 1)
            x_ = Gx + (r_ * 1.2) * math.cos(a_) * (1 if k_ % 2 else -1) * .9
            y_ = Gy + 330 + 120 * math.sin(a_)
            body.append(line([(x_, y_), (x_ + 14 * math.cos(a_), y_ + 8)], 4, "#6c6688", seed=7300 + k_, taper=.5))
    kk = ease_io(clamp((t - 19.08) / 1.6))
    return f'<g transform="{lib.cam(600 + 20 * kk, 930 - 20 * kk, z, 1.2 * bump(t, T_DOST, .3) - .4 * kk)}">{"".join(body)}</g>'


# ═════════════════════════════ s12 20.80–22.92 ═════════════════════════════
T_PASP, T_OSTAL, T_POLKE = wt(48), wt(51), wt(53)     # 20.8, 21.56, 22.16
WALL2, WALL2_SH = "#ecd6ae", "#d9bf90"
BURG, BURG_SH, GOLD = "#7c1f30", "#561220", "#e0b04a"


def passport(x, y, w, h, glint=0.0, tilt=0.0):
    """Паспорт стоит на полке (x — центр, y — низ): бордовая обложка, золотой кружок-герб, без букв."""
    x0, y0 = x - w / 2, y - h
    o = shape(rrect(x0, y0, x0 + w, y, 8), BURG, blob([(x0, y0), (x0 + 22, y0), (x0 + 22, y), (x0, y)], BURG_SH, .9) +
              blob([(x0 + w - 14, y0), (x0 + w, y0), (x0 + w, y), (x0 + w - 14, y)], "#9a3346", .5), w=5.4, seed=9100)
    o += line([(x0 + 36, y0 + 24), (x0 + w - 22, y0 + 24), (x0 + w - 22, y - 24), (x0 + 36, y - 24), (x0 + 36, y0 + 24)], 3.4, GOLD, seed=9101, taper=0, wmin=1)
    cx, cy = x + 8, y0 + h * .44
    o += shape(ellipse_pts(cx, cy, 60, 60, 20), GOLD, blob(ellipse_pts(cx, cy, 46, 46, 18), BURG, 1) + blob(ellipse_pts(cx, cy, 22, 22, 14), GOLD, 1), w=4, seed=9102)
    for k in range(12):
        a = k * math.pi / 6
        o += line([(cx + 30 * math.cos(a), cy + 30 * math.sin(a)), (cx + 42 * math.cos(a), cy + 42 * math.sin(a))], 3, GOLD, seed=9110 + k, taper=.3)
    o += blob(ellipse_pts(cx, cy, 8, 8, 10), BURG)
    o += blob(rrect(x - 40, y - 62, x + 56, y - 46, 5), GOLD)
    o += blob(rrect(x - 28, y0 + 12, x + 44, y0 + 18, 3), GOLD, 1)
    if glint > 0:
        g = glint
        gx, gy = cx - 30, cy - 34
        r = 62 * g
        o += blob([(gx, gy - r), (gx + r * .16, gy - r * .16), (gx + r, gy), (gx + r * .16, gy + r * .16), (gx, gy + r), (gx - r * .16, gy + r * .16),
                   (gx - r, gy), (gx - r * .16, gy - r * .16)], "#fffbe8")
    return o


def keys(x, y, sway):
    """Связка ключей на крючке: кольцо и три ключа (кружок-головка, стержень, бородка)."""
    o = shape(rrect(x - 26, y - 14, x + 26, y + 12, 8), "#8a5a38", "", w=4, seed=9200)
    o += blob(ellipse_pts(x, y + 4, 9, 9, 8), "#4a2e18")
    ring_c = (x + sway * .3, y + 56)
    o += shape(ellipse_pts(ring_c[0], ring_c[1], 26, 30, 14), "#cfcfd6", blob(ellipse_pts(ring_c[0], ring_c[1], 17, 21, 12), WALL2), w=4, seed=9201)
    for i, (dx, ang, col, ln) in enumerate([(-30, -14, "#c9a642", 150), (0, 2, "#b9bcc8", 170), (32, 16, "#d8863a", 140)]):
        a = math.radians(ang + sway * (1 + i * .3))
        sx, sy = ring_c[0] + dx * .4, ring_c[1] + 26
        ex, ey = sx + ln * math.sin(a), sy + ln * math.cos(a)
        shaft = band_pts((sx, sy), (ex, ey), 14)
        o += shape(shaft, col, "", w=3.8, seed=9210 + i)
        o += shape(ellipse_pts(sx, sy, 20, 20, 12), col, blob(ellipse_pts(sx, sy, 8, 8, 8), WALL2), w=3.8, seed=9220 + i)
        # бородка
        d_ = np.array([ex - sx, ey - sy])
        d_ /= np.linalg.norm(d_)
        nn = np.array([d_[1], -d_[0]])
        tb = [(ex - d_[0] * 36 + nn[0] * 7, ey - d_[1] * 36 + nn[1] * 7, 1), (ex - d_[0] * 36 + nn[0] * 28, ey - d_[1] * 36 + nn[1] * 28, 1),
              (ex - d_[0] * 20 + nn[0] * 28, ey - d_[1] * 20 + nn[1] * 28, 1), (ex - d_[0] * 20 + nn[0] * 7, ey - d_[1] * 20 + nn[1] * 7, 1)]
        o += shape(tb, col, "", w=3.2, seed=9230 + i)
    return o


def band_pts(a, b, w):
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]]) * w / 2
    return [tuple(a + n) + (1,), tuple(b + n) + (1,), tuple(b - n) + (1,), tuple(a - n) + (1,)]


def plant(x, y):
    o = ""
    for i, (dx, ang, ln, col) in enumerate([(-30, -30, 130, "#5e9a52"), (-8, -8, 160, "#6fae5c"), (14, 14, 150, "#528f48"), (34, 34, 120, "#6fae5c")]):
        a = math.radians(ang)
        tip = (x + dx + math.sin(a) * ln * .7, y - 60 - math.cos(a) * ln)
        leaf = [(x + dx, y - 56, 1), (x + dx - 24, y - 56 - ln * .5), (tip[0], tip[1], 1), (x + dx + 24, y - 56 - ln * .5)]
        o += shape(leaf, col, line([(x + dx, y - 56), tip], 2, "#3e7438", seed=9300 + i), w=3.8, seed=9310 + i)
    pot = [(x - 54, y - 70, 1), (x + 54, y - 70, 1), (x + 40, y, 1), (x - 40, y, 1)]
    o += shape(pot, "#c5694a", blob([(x + 10, y - 70), (x + 54, y - 70), (x + 40, y), (x + 10, y)], "#a4503a", .7), w=4.8, seed=9320)
    return o


def hall_bg(t, zb):
    """Дальний план: коридор с входной дверью и Димой, тащащим чемодан к двери (резкость мягко сбита)."""
    o = blob(rrect(-300, -300, 1500, 2300), "#e8d9bd")
    o += blob(rrect(-300, 1120, 1500, 2300), "#b88a5a")
    o += line([(-300, 1120), (1500, 1120)], 5, "#7a5430", taper=0, wmin=1, seed=9400)
    dx0, dx1, dy0 = 900, 1180, 420
    o += shape(rrect(dx0 - 22, dy0 - 20, dx1 + 22, 1120, 6), "#6e4528", "", w=5, seed=9401)
    o += shape(rrect(dx0, dy0, dx1, 1120, 4), "#9a6a42", blob(rrect(dx0 + 36, dy0 + 50, dx1 - 36, dy0 + 320, 6), "#85582f") + blob(rrect(dx0 + 36, dy0 + 390, dx1 - 36, 1060, 6), "#85582f"),
               w=5, seed=9402)
    o += shape(ellipse_pts(dx0 + 40, 800, 16, 16, 10), "#e0b04a", "", w=3.6, seed=9403)
    o += blob([(dx0 + 10, 1108, 1), (dx1 - 10, 1108, 1), (dx1 - 10, 1120, 1), (dx0 + 10, 1120, 1)], "#fff3cf")
    u = clamp((t - 20.6) / 2.5)
    hx = 560 + 300 * u
    ph = (t - 20.6) * 2 * math.pi * 1.8
    bs = .52
    hip = (hx, 1124 - 540 * bs)
    def foot(p_):
        return ((hip[0] + 62 * bs * math.sin(p_) * 1.5, 1120 - max(0, math.cos(p_)) * 26 * bs * 2), 0.0)
    feet = {"n": foot(ph), "f": foot(ph + math.pi)}
    exp = dict(lid=.6, look=(.7, .1), brows="tired", mouth="flat")
    sw_ = math.sin(ph + .4) * .12
    hand_t = (hx - 130, hip[1] + 50 + 10 * sw_)
    d = dima(hip, bs, .2, {"n": ("ik", hand_t, -1), "f": ("ang", .3 * math.sin(ph), .3)},
             {"n": dict(open_hand(.9, (-1, .5), .05, .8, k=.9)), "f": open_hand(.3, (0, 1), .2, .2)}, exp, feet=feet, head_ang=.05)
    sc = SU.Suit(hx - 200, 1128, W=170, D=80, Hb=120, e=20, th=0)
    o += f'<g {blur(2.2)}>'
    o += line([(hx - 200 + 40, 1128 - 120 * .94 - 10), hand_t], 5, "#2a262e", seed=9410, taper=0, wmin=1)
    o += sc.front() + sc.lid()
    o += d["legs"] + d["arm_f"] + d["body"] + d["arm_n"]
    o += "</g>"
    return o


def frame12(t):
    push = ease_io(clamp((t - T_OSTAL + .08) / .42))
    z = 1.0 + .05 * ease_io(clamp((t - 20.6) / 1.0)) + .3 * push + .02 * bump(t, T_POLKE, .3)
    zb = 1 + (z - 1) * .4
    set_ink(z)
    bg = f'<g transform="{lib.cam(560, 860, zb, 0)}">{hall_bg(t, zb)}</g>'
    fg = []
    EDGE = -200
    fg.append(blob([(-1000, -400, 1), (EDGE, -400, 1), (EDGE, 2400, 1), (-1000, 2400, 1)], WALL2))
    fg.append(blob([(-900, -400, 1), (-450, -400, 1), (EDGE - 20, 1200, 1), (-620, 1200, 1)], "#f6e6bd"))        # луч из окна
    fg.append(blob([(EDGE - 40, -400, 1), (EDGE, -400, 1), (EDGE, 2400, 1), (EDGE - 40, 2400, 1)], "#cdb07c"))
    fg.append(line([(EDGE, -400), (EDGE, 2400)], 6, INK, taper=0, wmin=1, seed=9501))
    # картина: холмы и солнце без букв
    fg.append(shape(rrect(-760, 430, -500, 650, 6), "#8a5a38", "", w=5, seed=9540))
    fg.append(shape(rrect(-740, 450, -520, 630, 3), "#bfe0e6", blob(ellipse_pts(-590, 520, 28, 28, 14), "#f5c24b") +
                    blob([(-740, 630, 1), (-740, 570, 1), (-670, 540), (-590, 580), (-520, 560, 1), (-520, 630, 1)], "#6fae5c"), w=3.4, seed=9541))
    fg.append(blob([(-1000, 1118, 1), (EDGE, 1118, 1), (EDGE, 1196, 1), (-1000, 1196, 1)], "#5a3a1c"))
    fg.append(shape(rrect(-1020, 1106, EDGE + 10, 1166, 3), "#b57c44", blob([(-1020, 1106, 1), (EDGE + 10, 1106, 1), (EDGE + 10, 1118, 1), (-1020, 1118, 1)], "#d9a468"), w=5.4, seed=9510))
    for bx in (-700, -340):
        fg.append(shape([(bx, 1166, 1), (bx + 62, 1166, 1), (bx + 4, 1290, 1)], "#8d5a2c", "", w=4.4, seed=9520 + bx))
    fg.append(plant(-800, 1106))
    gl = clamp(1 - abs((t - T_POLKE - .15) / .3)) if abs(t - T_POLKE - .15) < .3 else 0
    fg.append(passport(-370, 1106, 236, 330, glint=gl))
    fg.append(keys(-560, 790, 6 * math.sin(t * 1.6) + 12 * bump(t, T_OSTAL, .6) * math.sin((t - T_OSTAL) * 18)))
    rs = np.random.RandomState(4)
    for i in range(30):
        x0, y0 = rs.uniform(-850, -220), rs.uniform(420, 1080)
        sp, ph_, r = rs.uniform(8, 22), rs.uniform(0, 6.28), rs.uniform(2.4, 5)
        yy = y0 - sp * (t - 20.6) + 10 * math.sin(t * 1.3 + ph_)
        fg.append(f'<circle cx="{x0 + 14 * math.sin(t * .8 + ph_):.1f}" cy="{yy:.1f}" r="{r:.1f}" fill="#fffbea"/>')
    if t > T_POLKE:
        e = t - T_POLKE
        for i in range(26):
            r_ = np.random.RandomState(i + 90)
            ang = math.radians(r_.uniform(-150, -30))
            sp = r_.uniform(160, 420)
            x_ = -370 + r_.uniform(-110, 110) + sp * math.cos(ang) * e * .5
            y_ = 1100 + sp * math.sin(ang) * e + 120 * e * e
            if y_ < 1110:
                fg.append(f'<circle cx="{x_:.1f}" cy="{y_:.1f}" r="{r_.uniform(2.6, 6) * (1 - clamp(e / .9) * .6):.1f}" fill="#fffbea"/>')
    fgs = f'<g transform="{lib.cam(-120 - 70 * push, 900 + 20 * push, z, -.6 * (1 - push) + 0.6 * push)}">{"".join(fg)}</g>'
    return bg + fgs


# ═════════════════════════════ s14 24.68–26.54 ═════════════════════════════
T_CHEM, T_ZA, T_DEN = wt(57), wt(58), wt(59)    # 24.68, 25.173, 25.312
SW_BLUE, SW_BLUE_SH = "#4f7bb0", "#3a5f8f"


def fall(t, T, dur=.26):
    """0 (высоко над кадром, большой) → 1 (лёг) с отскоком: возвращает (scale, shadow_k, squash)."""
    t_l = T + .06
    if t < t_l - dur:
        return None
    u = clamp((t - (t_l - dur)) / dur)
    sc = 1 + .34 * (1 - ease_in(u, 2.2))
    sh = ease_in(u, 2.2)
    sq = 0.0
    if t > t_l:
        e = t - t_l
        sq = math.exp(-e * 9) * math.sin(e * 28) * .06
    return sc, sh, sq


def shadow_pts(cx, cy, w, h, off):
    return rrect(cx - w / 2 + off, cy - h / 2 + off * 1.3, cx + w / 2 + off, cy + h / 2 + off * 1.3, 18)


def sweater(cx, cy, sc, sq, tt, rot=0.0):
    w, h = 300, 250
    o = ""
    body = rrect(-w / 2, -h / 2, w / 2, h / 2, 22)
    inner = blob(rrect(-w / 2, h / 2 - 54, w / 2, h / 2, 6), SW_BLUE_SH, .9)            # резинка низа
    for k in range(1, 12):
        x = -w / 2 + k * w / 12
        inner += line([(x, h / 2 - 50), (x, h / 2 - 6)], 2.4, "#2f4e78", seed=9600 + k, op=.8)
    inner += blob([(-w / 2, -h / 2), (-w / 2 + 70, -h / 2), (-w / 2 + 70, h / 2 - 54), (-w / 2, h / 2 - 54)], SW_BLUE_SH, .5)   # сложенный рукав
    inner += line([(-w / 2 + 70, -h / 2 + 10), (-w / 2 + 74, h / 2 - 56)], 3, "#2f4e78", seed=9640)
    inner += blob(ellipse_pts(w / 2 - 70, -h / 2 + 6, 56, 20, 12), "#2f4e78")                    # ворот
    inner += blob(ellipse_pts(w / 2 - 70, -h / 2 + 6, 40, 11, 12), "#355c8c")
    for k in range(4):                                                                         # косичка-вязка
        inner += line([(-w / 2 + 110 + k * 26, -h / 2 + 50), (-w / 2 + 120 + k * 26, h / 2 - 70)], 2.2, "#6d98cc", seed=9650 + k, op=.9)
    o += shape(body, SW_BLUE, inner, w=5, seed=9660)
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f}) scale({sc * (1 + sq):.4f} {sc * (1 - sq):.4f})">{o}</g>'


def umbrella(cx, cy, sc, sq, tt, rot=0.0):
    L, w = 560, 96
    o = ""
    body = [(-w * .42, -L / 2 + 12, 1), (w * .42, -L / 2 + 12, 1), (w * .5, L / 2 - 90), (w * .3, L / 2 - 70, 1), (-w * .3, L / 2 - 70, 1), (-w * .5, L / 2 - 90)]
    inner = blob([(w * .1, -L / 2), (w * .5, -L / 2), (w * .5, L / 2 - 70), (w * .1, L / 2 - 70)], "#25305a", .6)
    for k in range(3):
        x = -w * .3 + k * w * .3
        inner += line([(x, -L / 2 + 30), (x + 4, L / 2 - 90)], 2.6, "#5a6aa0", seed=9700 + k, op=.8)
    o += shape(body, "#3a4a80", inner, w=5, seed=9710)
    o += shape([(-w * .6, -40, 1), (w * .6, -40, 1), (w * .6, -4, 1), (-w * .6, -4, 1)], "#e8dfc8", "", w=3.6, seed=9711)
    o += shape([(-6, -L / 2 - 20, 1), (6, -L / 2 - 20, 1), (5, -L / 2 + 14, 1), (-5, -L / 2 + 14, 1)], "#a8a8b4", "", w=3, seed=9712)
    hook = [(0, L / 2 - 72), (0, L / 2 - 20), (18, L / 2 + 10), (50, L / 2 + 8), (66, L / 2 - 14), (58, L / 2 - 36)]
    o += line(hook, 20, INK, seed=9713, taper=.05, wmin=.95)
    o += line(hook, 12, "#7a4a2a", seed=9714, taper=.05, wmin=.95)
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f}) scale({sc * (1 + sq):.4f} {sc * (1 - sq):.4f})">{o}</g>'


def mesh_pocket(cx, cy, w, h):
    o = shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 12), "#f6efdc", "", w=4.4, seed=9800)
    for k in range(1, 9):
        x = cx - w / 2 + k * w / 9
        o += line([(x, cy - h / 2 + 6), (x, cy + h / 2 - 6)], 2.2, "#b4a784", seed=9810 + k, op=.9, taper=.2, wmin=.8)
    for k in range(1, 7):
        y = cy - h / 2 + k * h / 7
        o += line([(cx - w / 2 + 6, y), (cx + w / 2 - 6, y)], 2.2, "#b4a784", seed=9830 + k, op=.9, taper=.2, wmin=.8)
    return o


def passport_flat(cx, cy, sc, rot=0.0, w=200, h=280):
    """Паспорт сверху: бордовая обложка с кружком-гербом."""
    o = shape(rrect(-w / 2, -h / 2, w / 2, h / 2, 8), BURG, blob([(-w / 2, -h / 2), (-w / 2 + 20, -h / 2), (-w / 2 + 20, h / 2), (-w / 2, h / 2)], BURG_SH, .9), w=5, seed=9100)
    o += line([(-w / 2 + 34, -h / 2 + 22), (w / 2 - 20, -h / 2 + 22), (w / 2 - 20, h / 2 - 22), (-w / 2 + 34, h / 2 - 22), (-w / 2 + 34, -h / 2 + 22)], 3, GOLD, seed=9101, taper=0, wmin=1)
    o += shape(ellipse_pts(6, -16, 52, 52, 18), GOLD, blob(ellipse_pts(6, -16, 40, 40, 16), BURG) + blob(ellipse_pts(6, -16, 19, 19, 12), GOLD), w=3.6, seed=9102)
    for k in range(12):
        a = k * math.pi / 6
        o += line([(6 + 26 * math.cos(a), -16 + 26 * math.sin(a)), (6 + 36 * math.cos(a), -16 + 36 * math.sin(a))], 2.6, GOLD, seed=9120 + k, taper=.3)
    o += blob(rrect(-36, 66, 48, 82, 4), GOLD)
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f}) scale({sc:.4f})">{o}</g>'


def arm_from_below(wr, d_ang, k_hand, sleeve_len=900, curl=.2, thumb=.3, spread=.2, press=0.0):
    """Предплечье Димы в горчичном рукаве снизу кадра до запястья wr, кисть с пальцами (вид сверху)."""
    people.C = people.PAL["dima"]
    a = math.radians(d_ang)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])
    Wr = np.array(wr, float)
    st = Wr - d * sleeve_len
    top, sh = people.C["TOP"], people.C["TOP_SH"]
    arm = [tuple(st + n * 84) + (1,), tuple(Wr + n * 66 - d * 6) + (1,), tuple(Wr - n * 66 - d * 6) + (1,), tuple(st - n * 84) + (1,)]
    inner = blob([tuple(st - n * 30), tuple(Wr - n * 14), tuple(Wr - n * 66), tuple(st - n * 84)], sh, .8)
    for i in range(3):
        c = Wr - d * (150 + i * 150)
        inner += line([tuple(c + n * 80), tuple(c + d * 10), tuple(c - n * 62)], 3, people.C["FOLD"], seed=9900 + i, op=.8, peak=.4)
    o = shape(arm, top, inner, w=5.4, seed=9910)
    cuff = [tuple(Wr - d * 70 + n * 70) + (1,), tuple(Wr + n * 62) + (1,), tuple(Wr - n * 62) + (1,), tuple(Wr - d * 70 - n * 70) + (1,)]
    rib = "".join(line([tuple(Wr - d * (60 - k * 10) + n * 66), tuple(Wr - d * (60 - k * 10) - n * 66)], 2, people.C["TOP_SH2"], seed=9920 + k, op=.8) for k in range(5))
    o += shape(cuff, sh, rib, w=4.6, seed=9921)
    kw = people.hand_kw()
    o += Hand.hand(Wr + d * 2, d, flip=1, k=k_hand, curl=(curl, curl, curl, curl * .9), spread=spread, thumb=thumb, bend=.1, seed=9930, nails=True, **kw)
    return o


def frame14(t):
    z = 1.0 + .1 * ease_io(clamp((t - 24.48) / 2.0))
    set_ink(z)
    CXs, BYs = 540, 1130
    S = SU.Suit(CXs, BYs, W=780, D=320, Hb=0, e=90, th=180, clothes=False)
    W2 = S.W / 2
    o = [blob(rrect(-300, -300, 1400, 2300), "#d9c19a")]
    # пол с досками (вид сверху)
    for i in range(0, 2400, 190):
        o.append(line([(-300, i - 300), (1400, i - 300)], 3, "#bda47c", taper=0, wmin=1, seed=9000 + i))
    # тень чемодана на полу
    o.append(blob(rrect(CXs - W2 - 6, BYs - 2 * S.D - 10, CXs + W2 + 26, BYs + 40, 30), "#b89d72"))
    # две половины: крышка (верх) и корпус (низ), по шву — молния
    lid = [S.P(-W2, S.D, 0) + (1,), S.P(W2, S.D, 0) + (1,), S.P(W2, 2 * S.D, 0) + (1,), S.P(-W2, 2 * S.D, 0) + (1,)]
    bod = [S.P(-W2, 0, 0) + (1,), S.P(W2, 0, 0) + (1,), S.P(W2, S.D, 0) + (1,), S.P(-W2, S.D, 0) + (1,)]
    shell = lambda pts: shape([(p[0], p[1], 1) for p in pts], SU.BODY, "", w=5.6, seed=9000 + int(pts[0][1]))
    ylo, ymid, yhi = BYs, BYs - S.D, BYs - 2 * S.D
    o.append(shape(rrect(CXs - W2, yhi, CXs + W2, ylo, 34), SU.BODY, "", w=6, seed=9001))
    ins = 26
    for (ya, yb, sd) in ((yhi, ymid, 1), (ymid, ylo, 2)):
        o.append(shape(rrect(CXs - W2 + ins, ya + (ins if sd == 1 else 6), CXs + W2 - ins, yb - (6 if sd == 1 else ins), 14), SU.LINING,
                       "".join(line([(CXs - W2 + ins + 30, ya + 60 + k * 70), (CXs + W2 - ins - 30, ya + 60 + k * 70)], 2.4, LINING_C, seed=9020 + k + sd * 9, op=.7) for k in range(3)),
                       w=4.4, seed=9010 + sd))
    # шов с молнией
    o.append(line([(CXs - W2 + 14, ymid), (CXs + W2 - 14, ymid)], 10, "#1b4348", seed=9030, taper=0, wmin=1))
    for k in range(int((2 * W2 - 40) / 16)):
        xx = CXs - W2 + 24 + k * 16
        o.append(line([(xx, ymid - 5), (xx + 6, ymid + 5)], 2.2, SU.METAL, seed=9040 + k, taper=.1, wmin=.9))
    o.append(shape(rrect(CXs + W2 - 100, ymid - 22, CXs + W2 - 56, ymid + 22, 8), SU.METAL, "", w=3.6, seed=9031))
    # поперечные ремни корпуса
    for xs in (CXs - 230, CXs + 230):
        pass
    o.append(shape(rrect(CXs - W2 + ins, ymid + 40, CXs + W2 - ins, ymid + 58, 4), "#c9b27c", "", w=3.2, seed=9050))
    # сетчатый карман на крышке
    pk = (CXs - 40, ymid - 150, 330, 230)
    o.append(mesh_pocket(pk[0], pk[1], pk[2], pk[3]))
    fix = ease_io(clamp((t - 25.62) / .4))
    # вещи
    items = []
    fs = fall(t, T_CHEM)
    sw_c = (CXs - 150, ymid + 160)
    if fs:
        sc, shk, sq = fs
        items.append(("sw", sc, shk, sq, sw_c))
    fu = fall(t, T_ZA)
    um_c = (CXs + 270, ymid + 166)
    fp = fall(t, T_DEN)
    for kind, fx, c in (("sw", fs, sw_c), ("um", fu, um_c)):
        if not fx:
            continue
        sc, shk, sq = fx
        off = 10 + 38 * (1 - shk)
        if kind == "sw":
            o.append(blob(shadow_pts(c[0], c[1], 300, 250, off), "#cdb98c"))
            o.append(sweater(c[0], c[1], sc, sq, t, rot=1.2 * (1 - shk) + 2.6 * (1 - fix)))
        else:
            o.append(blob(shadow_pts(c[0], c[1], 100, 560, off), "#cdb98c"))
            o.append(umbrella(c[0], c[1], sc, sq, t, rot=-1.5 * (1 - shk) - 2.0 * (1 - fix)))
    # паспорт: сверху в карман (ложится на карман и чуть заходит внутрь)
    pcx, pcy = pk[0] + 6, pk[1] - 14
    if fp:
        sc, shk, sq = fp
        slide = ease_out(clamp((t - (T_DEN + .06)) / .22), 2.4)
        py = pcy - 60 * (1 - slide)
        off = 10 + 30 * (1 - shk)
        o.append(blob(shadow_pts(pcx, py, 200, 280, off), "#cdb98c"))
        o.append(passport_flat(pcx, py, sc * (1 + sq), rot=-2 * (1 - shk)))
        # карман поверх нижней части паспорта
        if shk > .99:
            o.append(f'<g clip-path="url(#{lib.clip_rect(pk[0] - pk[2] / 2, pcy + 70 - 60 * (1 - slide) * 0 + 20, pk[2], 200)})">{mesh_pocket(pk[0], pk[1], pk[2], pk[3])}</g>')
    # рука поправляет
    hand_u = clamp((t - 25.55) / .4)
    if t > 25.45:
        k_ = ease_io(clamp((t - 25.45) / .45)) * (1 - ease_io(clamp((t - 26.2) / .34)))
        wy = BYs + 250 - 300 * k_
        wx = sw_c[0] + 120 - 40 * math.sin(t * 9) * k_ * .4
        o.append(arm_from_below((wx, wy), -90 + 6 * math.sin(t * 6) * k_, 1.35, curl=.15))
    return (f'<g transform="{lib.cam(540 + 6 * math.sin(t * 1.3), 870, z, -1.2 + 1.6 * clamp((t - 24.48) / 2.0))}">'
            f'<g transform="translate(540 820) scale(1.14) translate(-540 -820)">{"".join(o)}</g></g>')


# ═════════════════════════════ s15 26.54–28.18 ═════════════════════════════
T_SP = wt(64)                       # 26.544
CHECK_T = [26.54, 27.10, 27.70]
ROW_Y = [560, 740, 920, 1100, 1280]


def partial(pts, u, step=4.0):
    if u <= 0:
        return []
    P = lib.sample(pts, False, step)
    n = max(2, int(len(P) * min(u, 1.0)))
    return [tuple(p_) for p_ in P[:n]]


def squiggle(x0, y, ln, seed, amp=11):
    rs = np.random.RandomState(seed)
    pts = []
    x = x0
    k = 0
    while x < x0 + ln:
        pts.append((x, y + rs.uniform(-amp, amp) * (1 if k % 2 else .7)))
        x += rs.uniform(18, 34)
        k += 1
    pts.append((x0 + ln, y + rs.uniform(-4, 4)))
    return pts


def pencil_svg(tip, ang_deg, ln=440):
    """Карандаш: графит в tip, тело уходит назад под углом."""
    a = math.radians(ang_deg)
    d = np.array([math.cos(a), math.sin(a)])        # от кончика назад
    n = np.array([-d[1], d[0]])
    T = np.array(tip, float)
    w = 24
    wood = [tuple(T), tuple(T + d * 50 + n * w * .5), tuple(T + d * 50 - n * w * .5)]
    body = [tuple(T + d * 50 + n * w * .5) + (1,), tuple(T + d * (ln - 28) + n * w * .5) + (1,), tuple(T + d * (ln - 28) - n * w * .5) + (1,), tuple(T + d * 50 - n * w * .5) + (1,)]
    o = shape([q + (1,) for q in wood], "#f0d3a0", "", w=3.4, seed=9950)
    o += blob([tuple(T), tuple(T + d * 17 + n * w * .17), tuple(T + d * 17 - n * w * .17)], "#3a3a44")
    o += shape(body, "#f2b53a", blob([tuple(T + d * 50 - n * w * .1), tuple(T + d * (ln - 28) - n * w * .1), tuple(T + d * (ln - 28) - n * w * .5), tuple(T + d * 50 - n * w * .5)], "#d4952a", .9), w=3.6, seed=9951)
    o += shape([tuple(T + d * (ln - 28) + n * w * .5) + (1,), tuple(T + d * (ln - 8) + n * w * .5) + (1,), tuple(T + d * (ln - 8) - n * w * .5) + (1,), tuple(T + d * (ln - 28) - n * w * .5) + (1,)], "#e87a86", "", w=3.2, seed=9952)
    o += shape([tuple(T + d * (ln - 32) + n * w * .5) + (1,), tuple(T + d * (ln - 28) + n * w * .5) + (1,), tuple(T + d * (ln - 28) - n * w * .5) + (1,), tuple(T + d * (ln - 32) - n * w * .5) + (1,)], "#bdbdc8", "", w=2.4, seed=9953)
    return o


def frame15(t):
    rise = ease_io(clamp((t - 27.78) / .5))
    z = 1.02 + .13 * rise
    set_ink(z)
    o = [blob(rrect(-300, -300, 1400, 2300, 0), "#b9895a")]
    for i in range(0, 2400, 210):
        o.append(line([(-300, i - 300), (1400, i - 300)], 3, "#a17447", taper=0, wmin=1, seed=9000 + i, op=.9))
    sh_off = 16 + 30 * rise
    PX0, PX1, PY0, PY1 = 90, 990, 300, 1500
    o.append(blob(rrect(PX0 + sh_off, PY0 + sh_off, PX1 + sh_off, PY1 + sh_off, 0), "#8f6a43"))
    paper = rrect(PX0, PY0, PX1, PY1, 14)
    lines_ = "".join(line([(PX0 + 6, y), (PX1 - 6, y)], 2.4, "#b9d3e6", taper=0, wmin=1, seed=9100 + y) for y in range(PY0 + 210, PY1, 62))
    lines_ += line([(PX0 + 220, PY0 + 4), (PX0 + 220, PY1 - 4)], 3.2, "#e58a8a", taper=0, wmin=1, seed=9099)
    o.append(shape(paper, "#fbf6e6", lines_, w=5, seed=9098))
    for hy in (420, 900, 1380):
        o.append(blob(ellipse_pts(PX0 + 70, hy, 22, 22, 12), "#b9895a") + line([(PX0 + 50, hy - 10), (PX0 + 90, hy - 10)], 2, "#8f6a43", seed=hy))
    # заголовок: чемоданчик и волна
    t_h = clamp((t - 26.30) / .3)
    o.append(shape(rrect(PX0 + 290, PY0 + 62, PX0 + 380, PY0 + 128, 10), "#3f8f94", line([(PX0 + 290, PY0 + 80), (PX0 + 380, PY0 + 80)], 3, "#245c62", seed=9120), w=4.4, seed=9121)
             + line([(PX0 + 318, PY0 + 62), (PX0 + 318, PY0 + 44), (PX0 + 352, PY0 + 44), (PX0 + 352, PY0 + 62)], 5, INK, seed=9122, taper=0, wmin=1))
    hp = partial(squiggle(PX0 + 410, PY0 + 98, 360, 5, amp=15), t_h)
    if len(hp) > 1:
        o.append(line(hp, 12, INK, seed=9123, taper=.1, wmin=.8))
    # строки списка
    for i, y in enumerate(ROW_Y):
        cx = PX0 + 120
        o.append(shape(rrect(cx - 34, y - 34, cx + 34, y + 34, 8), "#fffdf4", "", w=4.4, seed=9200 + i))
        u = clamp((t - (26.34 + .08 * i)) / .24)
        sp = partial(squiggle(PX0 + 260, y + 2, [470, 380, 520, 300, 420][i], 20 + i), u)
        if len(sp) > 1:
            o.append(line(sp, 9, INK, seed=9210 + i, taper=.1, wmin=.8))
        # маленькая иконка-значок (кружок, треугольник, квадрат) вместо текста
    # галочки и зачёркивание
    tip_pos = None
    for i, Tc in enumerate(CHECK_T):
        y = ROW_Y[i]
        cx = PX0 + 120
        tick = [(cx - 22, y + 2), (cx - 6, y + 24), (cx + 34, y - 36), (cx + 38, y - 40)]
        u = clamp((t - Tc) / .2)
        tp = partial(tick, u)
        if len(tp) > 1:
            o.append(line(tp, 14, "#1f8a4a", seed=9300 + i, taper=.1, wmin=.9))
            o.append(blob(ellipse_pts(cx, y, 44, 44, 12), "#9fe0b4", .0)) if False else None
        # зачёрк карандашом
        us = clamp((t - (Tc + .26)) / .24)
        sg = partial([(PX0 + 252, y + 3), (PX0 + 252 + [470, 380, 520][i] * .5, y - 5), (PX0 + 252 + [470, 380, 520][i] + 10, y + 2)], us)
        if len(sg) > 1:
            o.append(line(sg, 6, "#4a4a55", seed=9310 + i, taper=.1, wmin=.9))
        if Tc <= t < Tc + .5:
            tip_pos = (tp[-1] if us <= 0 and len(tp) > 1 else (sg[-1] if len(sg) > 1 else (cx, y)))
    # рука с карандашом
    if t < 28.0:
        base = (PX0 + 120, ROW_Y[0])
        if t < 26.54:
            tgt = (PX0 + 150, ROW_Y[0] - 30)
        else:
            idx = 0 if t < 27.0 else (1 if t < 27.6 else 2)
            nxt = {0: (PX0 + 120 + 10, ROW_Y[0]), 1: (PX0 + 130, ROW_Y[1]), 2: (PX0 + 130, ROW_Y[2])}
            tgt = nxt[idx]
        # плавный переезд между строками
        tp_ = [(PX0 + 150, ROW_Y[0] - 30), (PX0 + 120, ROW_Y[0]), (PX0 + 120, ROW_Y[1]), (PX0 + 120, ROW_Y[2])]
        tt = [26.34, 26.54, 27.10, 27.70]
        if t <= tt[0]:
            tip = tp_[0]
        elif t >= 27.9:
            u_ = ease_io(clamp((t - 27.9) / .3))
            tip = (tp_[3][0] + 500 * u_, tp_[3][1] + 600 * u_)
        else:
            j = 0
            while j < 3 and t > tt[j + 1]:
                j += 1
            if j == 3:
                tip = tp_[3]
            else:
                u_ = ease_io(clamp((t - tt[j] - .3) / .2)) if j >= 1 else ease_io(clamp((t - tt[j]) / .2))
                if j >= 1:
                    tip = (tp_[j][0] + (tp_[j + 1][0] - tp_[j][0]) * u_, tp_[j][1] + (tp_[j + 1][1] - tp_[j][1]) * u_)
                else:
                    tip = (tp_[j][0] + (tp_[j + 1][0] - tp_[j][0]) * u_, tp_[j][1] + (tp_[j + 1][1] - tp_[j][1]) * u_)
        # во время зачёркивания кончик идёт по линии
        wig = 5 * math.sin(t * 30)
        tip = (tip[0] + wig * .3, tip[1] + wig * .2)
        ang = 30.0
        d = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
        o.append(pencil_svg(tip, ang, 420))
        wrist = np.array(tip) + d * 300
        dh = -d
        people.C = people.PAL["dima"]
        kw = people.hand_kw()
        sleeve_dir = d
        Wr = wrist + d * 150
        st = Wr + d * 1100
        n_ = np.array([-d[1], d[0]])
        arm = [tuple(st + n_ * 74) + (1,), tuple(Wr + n_ * 62) + (1,), tuple(Wr - n_ * 62) + (1,), tuple(st - n_ * 74) + (1,)]
        arm_s = shape(arm, people.C["TOP"], blob([tuple(st - n_ * 26), tuple(Wr - n_ * 14), tuple(Wr - n_ * 62), tuple(st - n_ * 74)], people.C["TOP_SH"], .8), w=5.4, seed=9910)
        cuff = [tuple(Wr + d * 70 + n_ * 70) + (1,), tuple(Wr + n_ * 62) + (1,), tuple(Wr - n_ * 62) + (1,), tuple(Wr + d * 70 - n_ * 70) + (1,)]
        arm_s += shape(cuff, people.C["TOP_SH"], "", w=4.6, seed=9921)
        hand_svg = Hand.hand(Wr - d * 4, dh, flip=1, k=1.95, curl=(.72, .7, .72, .6), spread=.03, thumb=.8, bend=.1, seed=9930, nails=True, **kw)
        o.append(arm_s + hand_svg)
    return (f'<g transform="{lib.cam(540 + 4 * math.sin(t * 1.7), 900 - 90 * rise, z, -1.5 + 1.2 * rise - 1.5 * rise)}">{"".join(o)}</g>')


# ═════════════════════════════ s16 28.18–31.1 ═════════════════════════════
T_KOT16 = 28.34        # начало рукописного «кот» (по брифу 28.40: слово дописано к его концу)
T_CHAS = wt(73)        # 30.66
T_JUMP = 30.42
_HW = {}


def letters():
    """Штрихи «кот» в нормированном квадрате букв (почерк: наклон, неровная база, разный размер, не геометрия)."""
    if _HW:
        return _HW["l"]
    rs = np.random.RandomState(56)
    ang = np.linspace(.95, .95 + 2 * math.pi + .42, 11)
    oo = [(.5 + .43 * math.cos(a) * (1 - .05 * (a - .95) / 6.7), .56 - .46 * math.sin(a) * (1 - .04 * (a - .95) / 6.7)) for a in ang]
    L = [
        [[(.14, -.02), (.10, .30), (.07, .68), (.10, 1.04), (.16, 1.02)],
         [(.70, .06), (.50, .26), (.26, .46), (.10, .58), (.30, .64), (.52, .80), (.70, 1.00), (.90, .98), (1.08, .86)]],
        [[(.86, .26)] + oo[1:] + [(.94, .22), (1.06, .26), (1.16, .38)]],
        [[(.00, .10), (.30, .04), (.62, .10), (.98, .02), (1.04, .10)], [(.50, .06), (.46, .50), (.50, .96), (.62, 1.02)]],
    ]
    out = []
    for li, strokes in enumerate(L):
        rot = [-5, 3, -4][li]
        sc = [(.96, 1.0), (1.04, .92), (1.0, 1.06)][li]
        base = [-.05, .06, -.02][li]
        o_ = []
        for st in strokes:
            pts = []
            for (x, y) in st:
                x += rs.normal(0, .014)
                y += rs.normal(0, .014)
                pts.append((x * sc[0], y * sc[1] + base))
            c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            pts = [(.5 + (x - .5) * c - (y - .5) * sn + (1 - y) * .16, .5 + (x - .5) * sn + (y - .5) * c) for x, y in pts]
            o_.append(pts)
        out.append(o_)
    _HW["l"] = out
    return out


def write_kot16(t, x0, y0, H_=230, Wd=150, gap=34):
    """Рукописное «кот» маркером: неровный штрих с нажимом, маркер едет за остриём; подчёркивание-росчерк и искры."""
    if t < T_KOT16 - .02:
        return ""
    o = []
    seg = [(0, .0), (0, .0)]
    t0 = T_KOT16
    durs = [[.08, .16], [.24], [.12, .09]]
    starts = []
    tt = t0
    for li, ds in enumerate(durs):
        row = []
        for d_ in ds:
            row.append((tt, tt + d_))
            tt += d_ + .012
        starts.append(row)
        tt += .035
    tip = None
    total = 3 * Wd + 2 * gap
    for li, strokes in enumerate(letters()):
        lx = x0 + li * (Wd + gap) + [0, 10, -4][li]
        for si, st in enumerate(strokes):
            a, b = starts[li][si]
            u = clamp((t - a) / (b - a))
            if u <= 0:
                continue
            P = partial([(lx + px * Wd, y0 + py * H_) for px, py in st], u)
            if len(P) < 2:
                continue
            o.append(line(P, 28, "#1c1622", taper=.18, wmin=.5, seed=7400 + li * 5 + si, peak=.4))
            if u < 1:
                tip = (P[-1], (P[-1][0] - P[-2][0], P[-1][1] - P[-2][1]))
    tu = starts[-1][-1][1] + .02
    us = clamp((t - tu) / .2)
    if us > 0:
        ux0, ux1 = x0 - 6, x0 + total + 10
        pts = [(ux0 + (ux1 - ux0) * v, y0 + H_ + 52 - 20 * math.sin(v * 3.0) + 5 * math.sin(v * 9)) for v in np.linspace(0, 1, 9)]
        Pp = partial(pts, us)
        if len(Pp) > 1:
            o.append(line(Pp, 20, "#f08a2a", taper=.3, wmin=.45, seed=7500))
            tip = (Pp[-1], (1, 0))
    if tip and t < tu + .24:
        (px, py), (dx, dy) = tip
        a_ = 52
        d = np.array([math.cos(math.radians(a_)), -math.sin(math.radians(a_))])
        n = np.array([-d[1], d[0]])
        T = np.array([px, py])
        w_ = 26
        ln = 250
        body = [tuple(T + d * 50 + n * w_ / 2) + (1,), tuple(T + d * ln + n * w_ / 2) + (1,), tuple(T + d * ln - n * w_ / 2) + (1,), tuple(T + d * 50 - n * w_ / 2) + (1,)]
        o.append(shape([tuple(T) + (1,), tuple(T + d * 50 + n * w_ / 2 * .8) + (1,), tuple(T + d * 50 - n * w_ / 2 * .8) + (1,)], "#2a2a34", "", w=3, seed=7600))
        o.append(shape(body, "#e0527e", blob([tuple(T + d * 50 - n * 2), tuple(T + d * ln - n * 2), tuple(T + d * ln - n * w_ / 2), tuple(T + d * 50 - n * w_ / 2)], "#a8335a", .9), w=3.6, seed=7601))
        o.append(shape([tuple(T + d * (ln - 8) + n * w_ / 2) + (1,), tuple(T + d * (ln + 30) + n * w_ / 2) + (1,), tuple(T + d * (ln + 30) - n * w_ / 2) + (1,), tuple(T + d * (ln - 8) - n * w_ / 2) + (1,)], "#2a2a34", "", w=3, seed=7602))
    # искры после последнего росчерка
    e = t - (tu + .2)
    if e > 0:
        for k in range(8):
            a_ = k * .8 + .3
            r_ = 36 + 120 * ease_out(clamp(e / .5))
            if e < .55:
                x_ = x0 + total / 2 + (total / 2 + 40) * math.cos(a_) * (.6 + .4 * ease_out(clamp(e / .5)))
                y_ = y0 + H_ / 2 + (H_ / 2 + 70) * math.sin(a_) * (.6 + .4 * ease_out(clamp(e / .5))) - 20
                o.append(f'<circle cx="{x_:.1f}" cy="{y_:.1f}" r="{max(0.5, 9 * (1 - e / .55)):.1f}" fill="#ffd070"/>')
    ee = t - T_KOT16
    sc = 1 + .05 * math.exp(-ee * 8) * math.sin(min(ee * 12, math.pi)) if ee >= 0 else 1
    cx_, cy_ = x0 + total / 2, y0 + H_ / 2
    return f'<g transform="translate({cx_:.1f} {cy_:.1f}) scale({sc:.4f}) translate({-cx_:.1f} {-cy_:.1f})">{"".join(o)}</g>'


def frame16(t):
    BY, CX = 1330, 740
    ZIN = ease_io(clamp((t - 27.98) / .75))
    ZOUT = ease_io(clamp((t - 30.36) / .6))
    z = 1.0 + .34 * ZIN - .34 * ZOUT + .03 * bump(t, T_KOT16, .3) + .04 * bump(t, T_CHAS, .3)
    set_ink(z)
    th_open = 0.0
    if t > 30.5:
        u = t - 30.5
        th_open = 96 * ease_out(clamp(u / .24), 2.2) + 7 * spring(u - .2, 2.8, 5) * (1 if u > .2 else 0)
    S = SU.Suit(CX, BY, W=560, D=260, Hb=210, e=32, th=th_open, clothes=False)
    body = [floor_bg(1000), window_light(560, 0, 100, 1000)]
    body.append(blob(ellipse_pts(CX, BY + 20, 330, 28, 20), "#5a3a1c"))
    # Дима
    pan = smooth(T_CHAS - .05, T_CHAS + .22, t)
    smile = 1 - pan
    bob = 3 * math.sin(t * 5)
    hip = (300 - 40 * pan, 872 + bob * .4)
    bs = .75
    lean = .06 - .1 * pan
    look_back = smooth(28.0, 28.35, t) * (1 - pan)
    exp = dict(lid=.8 + .15 * pan, look=(.1 - .5 * look_back * 0 + (-.5 * pan), .1), brows="worry" if pan > .3 else "up" if look_back > .5 else "calm",
               mouth="grin" if pan < .1 else "laugh", open=.5 + .5 * pan, smile=1, blush=.3, closed=0.0)
    shn = (hip[0] + 5 * bs, hip[1] - 400 * bs)
    pat = .5 + .5 * math.sin(t * 6)
    tn = (520 + (shn[0] + 230 - 520) * pan, 1010 + (shn[1] - 120 - 1010) * pan)
    tf = (hip[0] + 100 + 8 * pat * (1 - pan), hip[1] - 70 + (shn[1] - 130 - hip[1] + 70) * pan)
    feet = {"n": ((350 - 20 * pan, 1326), 0.0), "f": ((250 - 20 * pan, 1330), 0.0)}
    d = dima(hip, bs, lean, {"n": ("ik", tn, -1), "f": ("ik", tf, -1)},
             {"n": open_hand(.15, (1, .2), .25, .2), "f": open_hand(.5, (1, .5), .1, .5)}, exp, feet=feet, head_ang=-.02 + .1 * look_back * (1 - pan))
    body.append(d.get("legs", "") + d["arm_f"] + d["body"])
    # паспорт торчит из кармана худи
    if t < T_JUMP + .5:
        pp = (hip[0] + 78, hip[1] - 62)
        body.append(f'<g transform="translate({pp[0]:.1f} {pp[1]:.1f}) rotate(-8)">' + shape(rrect(-26, -52, 26, 20, 4), BURG, line([(-14, -40), (14, -40)], 3, GOLD, seed=9701) +
                                                                                              blob(ellipse_pts(0, -22, 11, 11, 10), GOLD), w=3.4, seed=9700) + "</g>")
    # чемодан и кот
    body.append(S.interior(22, floor="#e9dab8") if th_open > 2 else "")
    if th_open >= 35:
        body.append(S.lid())
    body.append(S.front())
    if th_open < 35:
        body.append(S.lid())
    # кот сидит на крышке довольный, прыгает на «час»
    ju = clamp((t - T_JUMP) / .42)
    top_y = BY - (244 * S.c + 130 * S.s)
    cxp = CX + 20
    if ju <= 0:
        cp = (cxp, top_y + 2)
        crot = 0.0
    else:
        arc = math.sin(math.pi * ease_out(ju, 1.4)) * 230
        cp = (cxp + 520 * ease_io(ju), top_y - arc + 190 * ease_in(ju, 2.2) - 190 * ease_in(ju, 2.2) * 0 + 60 * ease_in(ju, 3))
        crot = 25 * ju
    if ju < 1.0 or True:
        blinkc = Cat_blink16(t)
        st = cstate(t, look=(0.0, .05), turn=0.0, blink=blinkc, ear=5 * bump(t, 29.2, .4), perk=.2, tail=6 * osc(t, .55) + 2 * osc(t, 1.4), smile=1, tilt=0,
                    flame_e=1.5 + .3 * math.sin(t * 9))
        if cp[0] < 1250:
            sh_ = blob(ellipse_pts(cp[0], cp[1] + 8, 110 * (1 - .5 * min(1, ju * 2)), 12, 14), "#1d4a4e") if ju <= 0 else ""
            body.append(sh_ + f'<g transform="rotate({crot:.2f} {cp[0]:.1f} {cp[1]:.1f})">{Cat.draw(cp[0], cp[1], .62, st, t)}</g>')
    body.append(d["arm_n"])
    # искры огонька
    fx, fy = cp[0] + (995 - 836) * .62, cp[1] + (1076 - 1306) * .62 - 30
    rs = np.random.RandomState(11)
    for i in range(7):
        per = rs.uniform(.9, 1.5)
        ph = rs.uniform(0, per)
        u = ((t + ph) % per) / per
        body.append(f'<circle cx="{fx + rs.uniform(-14, 14) + 18 * math.sin(u * 5 + i):.1f}" cy="{fy - 120 * u - 12:.1f}" r="{4 * (1 - u) + 1:.1f}" fill="#ffd070"/>')
    cam = lib.cam(640 + 110 * (ZIN - ZOUT), 880 - 70 * (ZIN - ZOUT), z, -.6 + .9 * ZIN - .9 * ZOUT + 1.2 * bump(t, T_CHAS, .3))
    return f'<g transform="{cam}">{"".join(body)}</g>' + write_kot16(t, 535, 330)


def Cat_blink16(t):
    for (a, dur) in ((28.9, .14), (29.9, .14), (30.9, .12)):
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


# ═════════════════════════════ диспетчер ═════════════════════════════
def frame(sid, t):
    lib.dyn_begin()
    body = {"s10": frame10, "s11": frame11, "s12": frame12, "s14": frame14, "s15": frame15, "s16": frame16}[sid](t)
    return svg(f'<rect width="1080" height="1920" fill="#e9d8bc"/>{body}')
