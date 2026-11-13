"""Сцена desk рилса 33 «список на 27 пунктов»: планы s01, s03, s05, s08, s11. frame(sid, t) -> SVG 1080×1920
(t — общее время ролика). Мир — den.py (комната Димы, время суток den.set_tod), Дима — people.py (сидит слева
лицом вправо, таз (230, 1262)), список — scroll.py. Удары — на словах по voice/words.json.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import den  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
import scroll as Sc  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


T_SPISOK = wi(2)          # 0.80
T_DLIN = wi(10)           # 4.16
T_CHAS = wi(19)           # 7.28
T_NACH = wi(23)           # 8.28
T_DEN = wi(43)            # 16.40
T_NAPIS = wi(45)          # 17.04

BS = 0.6
HIP = np.array([230.0, 1262.0])
SX0, SX1 = 470.0, 650.0          # свиток у переднего края стола (x)


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def hook_zoom(t, t0=0.0, mx=0.4, dur=0.22, rot=-3.0):
    """Влёт (правила 28/29): масштаб 1/(1+mx) → 1.05 за dur, отскок к 1 за 0.3 с; поворот rot → +0.8 → 0."""
    u = (t - t0) / dur
    if u <= 0:
        return 1 / (1 + mx), rot
    if u < 1:
        e = ease_out(u, 3)
        return 1 / (1 + mx) + (1.05 - 1 / (1 + mx)) * e, rot * (1 - e) + .8 * e
    v = (t - t0 - dur) / 0.3
    if v < 1:
        e = ease_io(v)
        return 1.05 - .05 * e, .8 * (1 - e)
    return 1.0, 0.0


def punch(t, t0, amp=.08, up=.06, down=.35):
    if t < t0:
        return 0.0
    if t < t0 + up:
        return amp * ease_out((t - t0) / up, 2)
    return amp * (1 - ease_io(clamp((t - t0 - up) / down)))


def step12(t):
    """Рисованное — «на двойках» (12 в секунду)."""
    return math.floor(t * 12) / 12


# ═════════════════════════ Дима ═════════════════════════
def dima(t, arms, hands=None, expr=None, hip=None, lean=0.12, head_ang=0.0, feet=None, head_off=(0, 0)):
    hip = HIP if hip is None else np.array(hip, float)
    if feet is None:
        feet = {"n": ((450, 1468), 0.0), "f": ((425, 1462), 0.0)}
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=0.0, strings=(2 * osc(t, 1.3), 1.5 * osc(t, 1.1, 1)), head_off=head_off)
    return people.draw(p, "dima")


def kw_hand():
    people.C = people.PAL["dima"]
    return dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])


# ═════════════════════════ комната ═════════════════════════
def room_back(t, clock=(0.0, 0.0, 0.0, 0.0)):
    h, m, jolt, tilt = clock
    return "".join([den.wall(t), den.window(t), den.board(t), den.shelf(t), den.clock(h, m, jolt, tilt), den.floor()])


def clock_ang(hh, mm):
    return ((hh % 12) + mm / 60) * 30.0, mm * 6.0


def desk_world(t, d, clock, *, on_desk="", mid="", front="", lamp_on=0.0, under="", chair_dx=0.0):
    w = [room_back(t, clock)]
    w.append(room.chair(HIP[0] + chair_dx, HIP[1] + 4, 1, 2300))
    w.append(den.desk_back())
    w.append(d.get("legs", ""))
    w.append(den.desk_top())
    w.append(under)
    w.append(on_desk)
    w.append(den.lamp(t, lamp_on))
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(mid)
    w.append(d["arm_n"])
    w.append(front)
    return "".join(w)


def light(t, mode, on=0.0, u=0.0):
    """Свет слоями: день — солнечный косой луч из окна + мягкая виньетка; вечер — лампа и тёплое свечение."""
    o = []
    if mode in ("morning", "day"):
        warm = "#fff1c8" if mode == "morning" else "#fff8e0"
        g = lib.lin_grad([(0, warm, .5), (1, warm, 0)], 0, 0, 1, .4)
        beam = [(40, 250), (380, 250), (1100, 1330), (520, 1500)]
        o.append(f'<path d="{lib.fill_d([p + (1,) for p in beam])}" fill="url(#{g})" style="mix-blend-mode:screen" {lib.blur(26)}/>')
        g2 = lib.rad_grad([(0, "#000000", 0), (.55, "#000000", 0), (1, "#2a1c10", .32)], 560, 980, 1200, 1300)
        o.append(f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g2})"/>')
    else:
        if on > 0:
            o.append(f'<g transform="translate({den.LAMP_B[0] - 985:.1f} 0)">{den.lamp_cone(t, on)}</g>')
        warm = lib.rad_grad([(0, "#ffb070", .22 * (1 - u)), (1, "#ffb070", 0)], 210, 520, 900)
        o.append(f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{warm})" style="mix-blend-mode:screen"/>')
        o.append(den.glow(on) if on > 0 else "")
    return "".join(o)


def compose(world, cam, mode, front_screen="", on=0.0, u=0.0):
    cx, cy, s, r = cam
    set_ink(s)
    bg = "#7b929f" if mode in ("morning", "day") else "#2a3346"
    o = [f'<rect width="1080" height="1920" fill="{bg}"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{light(0, mode, on, u)}</g>', front_screen, vignette(mode)]
    return lib.svg("".join(o))


def vignette(mode):
    a = .3 if mode in ("morning", "day") else .45
    g = lib.rad_grad([(0, "#0a0c1e", 0), (.6, "#0a0c1e", 0), (1, "#0a0c1e", a)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def mug(t, x=760.0, y=1104.0, k=.44, col="#c44f3a", steam=True):
    return den.mug(x, y, k, col, fill="coffee", steam_t=t if steam else None)


# ═════════════════════════ список на столе и у края ═════════════════════════
def desk_list(t, hang_to, *, off=0.0, sway=0.0, pretty=False, roll=0.0, x0=SX0, x1=SX1, seed=500, top_lines=True, down=False, num0=1):
    """Лист на столешнице + загиб через передний край + свисающая часть до hang_to (мир, y)."""
    o = [Sc.on_desk(x0 - 40, x1 + 20, den.DESK_T + 14, den.DESK_F - 2, seed=seed + 20, pretty=pretty, lines=top_lines)]
    o.append(Sc.hanging(x0, x1, den.DESK_F + 2, hang_to, off=off, gap=34, seed=seed, sway=sway, t=t, pretty=pretty, roll=roll, down=down, num0=num0))
    o.append(Sc.front_bend(x0, x1, den.DESK_F - 4, seed=seed + 30))
    return "".join(o)


def speed_lines(cx, cy, r, t, n=4, seed=5000, col="#3a2a22", w=4.5):
    """Штрихи скорости вокруг руки (на двойках, мигают)."""
    o = []
    tt = step12(t)
    rs = np.random.RandomState(int(tt * 12) % 997 + seed)
    for j in range(n):
        a = rs.uniform(-2.6, -.3) if j % 2 else rs.uniform(.3, 1.2)
        r0 = r * rs.uniform(.9, 1.2)
        L = r * rs.uniform(.35, .6)
        p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        p1 = (cx + (r0 + L) * math.cos(a), cy + (r0 + L) * math.sin(a))
        o.append(line([p0, p1], w, col, seed=seed + j, taper=.3, wmin=.4))
    return "".join(o)


def writing_hand(t, base, rate=6.5, amp=26, seed=0):
    """Рука пишет: запястье дрожит по строке, кончик ручки на бумаге. Возвращает (запястье, ручка-svg, кончик)."""
    tt = t
    x = base[0] + amp * osc(tt, rate) + .4 * amp * osc(tt, rate * 2.3, 1)
    y = base[1] + 5 * osc(tt, rate * 2, .5)
    wr = np.array([x, y])
    tip = wr + np.array([58.0, 22.0])
    top = wr + np.array([-6.0, -64.0])
    return wr, tip, top


# ═════════════════════════ s01: хук — яростно пишет, лист уже свисает; удар на «список» ═════════════════════════
def s01(t):
    den.set_tod("morning")
    z, rot = hook_zoom(t, 0.0, .4, .22, -3.4)
    hit = punch(t, T_SPISOK, .1, .06, .4)
    k = ease_io(clamp(t / 1.5))
    s = 1.62 * z * (1 + .04 * k) * (1 + hit)
    sh = bump(t, T_SPISOK, .3)
    cam = (480 - 60 * (1 - z) + 10 * k + 6 * sh * osc(t, 13), 1000 + 50 * (1 - z) + 4 * sh * osc(t, 17, 1), s,
           rot + .4 * osc(t, .6) + 1.4 * sh * osc(t, 9))
    # рука пишет: запястье над листом, ручка в кулаке
    wr, tip, top = writing_hand(t, (488.0, 1060.0), rate=6.0, amp=22)
    jolt = sh
    expr = dict(lid=.78, look=(.62, .78), brows="det", mouth="grin", open=.5, closed=blink_at(t, 1.12, .12),
                hair=5 * osc(t, 6.0) + 6 * jolt, blush=.5)
    lean = .24 + .015 * osc(t, 6.0, 1)
    hd = (tip - wr) / np.linalg.norm(tip - wr)
    arms = {"n": ("ik", tuple(wr), -1), "f": ("ik", (446, 1102), -1)}
    hands = {"n": dict(kind="open", dir=tuple(hd), curl=(.82, .88, .92, .95), spread=.02, thumb=.85, bend=.05),
             "f": dict(kind="open", dir=(1, .25), curl=(.15, .2, .25, .3), spread=.1, thumb=.3)}
    d = dima(t, arms, hands, expr, lean=lean, head_ang=-.06 + .03 * osc(t, 6.0, 2))
    pen_svg = Sc.pen(tuple(top), tuple(tip), 11)
    # свиток: с каждой строкой бумага уходит вниз (прокрутка), на «список» — рывок вниз с отскоком
    drop = 0.0
    if t > T_SPISOK:
        v = t - T_SPISOK
        drop = 70 * (1 - math.exp(-9 * v) * math.cos(v * 20))
    off = 75 * t + drop
    hang = 1330 + 20 * osc(t, 1.4)
    sway = .25 * osc(t, 1.1) + .6 * bump(t, T_SPISOK, .4)
    lst = desk_list(t, hang + 250, off=off, sway=sway, seed=500, down=True, num0=14)
    # свежие строки на столешнице «бегут» к краю
    front = speed_lines(wr[0] + 30, wr[1] + 10, 70, t, n=4)
    for j in range(3):
        u = (t * 3 + j / 3) % 1
        px = wr[0] + 70 + 40 * u
        front += line([(px, 1040 - 30 * u), (px + 18, 1030 - 36 * u)], 4, "#3a2a22", seed=5100 + j, op=1 if u < .8 else 0)
    front += sweat(d["head"][0] + 60, d["head"][1] - 80, 1.0, (t * 1.3) % 1)
    w = desk_world(t, d, (*clock_ang(8, 5 + 10 * t), 0.0, 0.0), on_desk=mug(t, 790, 1100, .42) + lst, mid=pen_svg, front=front, lamp_on=0)
    return compose(w, cam, "morning")


def sweat(x, y, k, u):
    if u <= 0 or u >= 1:
        return ""
    yy = y + 46 * k * ease_in(u)
    r = 13 * k * min(1, u * 3)
    drop = [(x, yy - r * 2.2), (x + r, yy - r * .1), (x + r * .8, yy + r * .7), (x, yy + r), (x - r * .8, yy + r * .7), (x - r, yy - r * .1)]
    return shape(drop, "#bfe6fa", blob([(x - r * .4, yy - r * .6), (x - r * .1, yy - r * .9), (x - r * .1, yy - r * .2)], "#ffffff"), w=3, seed=3001)


def pen_fist(wr):
    """Ручка в кулаке (как при письме): кнопка выше запястья, стержень вниз-вправо."""
    wr = np.array(wr, float)
    tip = wr + np.array([58.0, 22.0])
    top = wr + np.array([-6.0, -64.0])
    hd = (tip - wr) / np.linalg.norm(tip - wr)
    return top, tip, dict(kind="open", dir=tuple(hd), curl=(.82, .88, .92, .95), spread=.02, thumb=.85, bend=.05)


# ═════════════════════════ s03: гордо поднимает список; на «длинный» рулон падает за край стола ═════════════════════════
def s03(t):
    den.set_tod("morning")
    td = T_DLIN
    k = ease_io(clamp((t - 2.9) / 1.92))
    hit = punch(t, td, .07, .05, .4)
    fall = clamp((t - td) / .7)
    s = (1.48 + .12 * k) * (1 + hit)
    sh = bump(t, td, .3)
    cam = (490 + 10 * k + 5 * sh * osc(t, 13), 990 - 10 * k + 40 * ease_io(fall) + 4 * sh * osc(t, 17), s, -.8 + 1.2 * k + 1.2 * sh * osc(t, 9))
    # руки поднимают лист со стола: 2.9 → 3.3 с перелётом, потом гордое покачивание
    lift = back_out(clamp((t - 2.9) / .42), 1.4)
    yt = 1060 - 230 * lift + 5 * osc(t, 1.6)
    xl, xr = 440.0, 680.0
    surpr = smooth(td - .02, td + .1, t)
    expr = dict(lid=.5 + .5 * surpr, look=(.75 - .25 * surpr, -.15 + 1.0 * surpr), brows="up", mouth="talk" if surpr > .5 else "smile",
                smile=1.0, open=.55 * surpr, closed=blink_at(t, 3.55, .14), hair=8 * bump(t, td, .4), blush=.4 * (1 - surpr))
    lean = .42 + .02 * osc(t, 1.6)
    arms = {"n": ("ik", (xr - 26, yt + 115 * lift + 40 * (1 - lift)), -1), "f": ("ik", (xl + 12, yt + 16), -1)}
    hold = dict(kind="open", dir=(.6, -.8), curl=(.86, .9, .92, .94), spread=.02, thumb=.8, bend=.05)
    hands = {"n": dict(hold, dir=(1, -.25)), "f": dict(hold, dir=(.4, -.9))}
    d = dima(t, arms, hands, expr, hip=(300, 1262), lean=lean, head_ang=-.08 - .05 * lift - .2 * surpr)
    # низ листа: рулон лежит на столе; на «длинный» соскальзывает за край и падает, разматываясь
    rr = 26.0
    if t < td:
        ry = 1098.0 - 2 * bump(t, 3.6, .3)
        spin = 0.0
    else:
        v = t - td
        ry = 1098.0 + 2600 * v * v + 120 * v
        spin = (ry - 1098) / 150
        rr = 26 - 8 * clamp(v / .6)
    sway = .15 * osc(t, 1.2) + .4 * sh
    sheet = Sc.hanging(xl, xr, yt, ry - rr * .6, off=0, gap=36, seed=610, sway=sway, t=t, roll=0, num0=1)
    roll = Sc.roll_svg((xl + xr) / 2 + sway * 30, ry, (xr - xl) / 2 + 6, rr, seed=640, spin=spin)
    front = ""
    if t > td:
        u = clamp((t - td) / .45)
        for j in range(3):
            x = xr + 30 + 26 * j
            front += line([(x, ry - 60 - 40 * j), (x, ry - 200 - 40 * j)], 4, "#3a2a22", seed=5300 + j, op=1 if u < .9 else 0, taper=.3, wmin=.4)
        front += sweat(d["head"][0] + 70, d["head"][1] - 90, 1.0, clamp((t - td - .05) / .6))
    w = desk_world(t, d, (*clock_ang(8, 20 + 5 * t), 0.0, 0.0), on_desk=mug(t, 820, 1100, .42) + sheet + roll, front=front, lamp_on=0,
                   chair_dx=70)
    return compose(w, cam, "morning")


def back_out(u, s=1.7):
    u = clamp(u) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


# ═════════════════════════ s05: час думает — щека на ладони, ручка во рту; часы 8→9; «?» на «начать» ═════════════════════════
def qmark(x, y, sc, rot):
    if sc <= 0:
        return ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({sc:.3f})">'
            f'<text x="8" y="10" text-anchor="middle" font-family="IDB" font-weight="900" font-size="300" fill="#1c1622">?</text>'
            f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="300" fill="#ffb43a" stroke="#1c1622" '
            f'stroke-width="9" paint-order="stroke" stroke-linejoin="round">?</text></g>')


def s05(t):
    den.set_tod("morning")
    tc, tn = T_CHAS, T_NACH
    k = ease_io(clamp((t - 6.24) / 2.76))
    s = (1.6 + .1 * k) * (1 + punch(t, tn, .06, .05, .4) + punch(t, tc, .03, .05, .3))
    cam = (430 - 10 * k, 880 + 10 * k, s, .6 - .9 * k + .8 * bump(t, tn, .3) * osc(t, 8))
    # часы: 8:00, на «час» стрелки прокручивают час за 0.42 с, щелчок
    sp = ease_io(clamp((t - tc) / .42))
    mins = 60 * sp + (t - tc - .42) * 2 * (t > tc + .42) + .3 * (t - 6.24)
    ha, ma = clock_ang(8, mins)
    jolt = bump(t, tc + .42, .3)
    tilt = 4 * math.exp(-5 * max(0, t - tc - .42)) * math.sin(max(0, t - tc - .42) * 22) if t > tc + .42 else 0.0
    glance = smooth(tc - .1, tc + .08, t) * (1 - smooth(tc + .75, tc + .95, t))
    surpr = smooth(tn - .03, tn + .1, t)
    chew = osc(t, 2.2)
    expr = dict(lid=.32 + .3 * glance + .55 * surpr, look=(.6 + .2 * glance, .5 - 1.1 * glance - .9 * surpr), brows="worry" if surpr < .5 else "up",
                mouth="flat", closed=max(blink_at(t, 6.9, .16), blink_at(t, 7.95, .14)), hair=7 * bump(t, tn, .4))
    lean, hang = .2 + .005 * chew, .12 + .015 * chew - .05 * surpr
    arms = {"n": ("ik", (326, 1052 - 4 * chew), -1), "f": ("ik", (470, 1110), -1)}
    hands = {"n": dict(kind="open", dir=(-.2, -1), curl=(.8, .85, .9, .92), spread=.02, thumb=.75),
             "f": dict(kind="open", dir=(1, .1), curl=(.2, .25, .3, .35), spread=.08, thumb=.4)}
    d = dima(t, arms, hands, expr, lean=lean, head_ang=hang)
    mouth = d["head"] + people.rot(np.array([80.0, 92.0]) * BS, lean * .5 + hang)
    ang = math.radians(-22 + 8 * chew - 25 * surpr)
    u = np.array([math.cos(ang), math.sin(ang)])
    pen_svg = Sc.pen(tuple(mouth + u * 120), tuple(mouth - u * 6), 10)
    hx, hy = d["head"]
    qs = back_out(clamp((t - tn) / .28), 2.2) if t > tn else 0
    q = qmark(hx + 30, hy - 190 - 8 * osc(t, 3), qs * (1 + .04 * osc(t, 5)), 10 * osc(t, 2.5) * clamp((t - tn) / .3) - 14 * (1 - clamp((t - tn) / .2)))
    lst = desk_list(t, 1600, off=0, sway=.15 * osc(t, .9), seed=500, num0=1)
    front = pen_svg + den.clock_click(clamp((t - tc - .42) / .3)) + q
    w = desk_world(t, d, (ha, ma, jolt, tilt), on_desk=mug(t, 800, 1100, .42) + lst, front=front, lamp_on=0)
    return compose(w, cam, "morning")


# ═════════════════════════ s08: вечер — Дима обмяк лицом на красивом списке, рука свисает ═════════════════════════
def s08(t):
    u = smooth(11.48, 13.34, t)
    den.set_tod("evening", u)
    den.LAMP_B = (830.0, 1084.0)
    k = ease_io(clamp((t - 11.48) / 1.86))
    s = 1.6 - .16 * k
    cam = (575 - 10 * k, 1000 + 5 * k, s, -.5 + .5 * k)
    br = osc(t, .45)
    lean = .88 + .012 * br
    expr = dict(lid=-1.25, look=(.3, .3), brows="tired", mouth="talk", open=.12 + .06 * br, smile=0, closed=0.0, hair=1.5 * br)
    th1 = -lean * .3 + .05 * osc(t, .45, 1)
    arms = {"n": ("ang", th1, 0.08), "f": ("ik", (690, 1106), -1)}
    hands = {"n": dict(kind="open", dir=(.05, 1), curl=(.35, .4, .45, .5), spread=.05, thumb=.4),
             "f": dict(kind="open", dir=(1, .1), curl=(.2, .25, .3, .35), spread=.1, thumb=.3)}
    d = dima(t, arms, hands, expr, hip=(250, 1262), lean=lean, head_ang=.42)
    lst = desk_list(t, 1600, off=0, sway=.1 * osc(t, .7), seed=700, pretty=True, num0=1)
    ha, ma = clock_ang(23, 40 + (t - 11.48) * 1.5)
    w = desk_world(t, d, (ha, ma, 0.0, 0.0), on_desk=mug(t, 950, 1100, .42, steam=False) + lst, lamp_on=1.0)
    return compose(w, cam, "evening", on=1.0, u=u)


# ═════════════════════════ s11: следующий день — смахивает свиток, берёт стикер, щёлкает ручкой ═════════════════════════
def sticky(x, y, k=1.0, seed=7300):
    """Блок жёлтых стикеров на столе (вид сбоку): верх + толщина пачки."""
    th = 14 * k
    top = [(x - 46 * k, y - 8 * k - th, 1), (x + 40 * k, y - 9 * k - th, 1), (x + 50 * k, y + 8 * k - th, 1), (x - 52 * k, y + 8 * k - th, 1)]
    side = [(x - 52 * k, y + 8 * k - th, 1), (x + 50 * k, y + 8 * k - th, 1), (x + 50 * k, y + 8 * k, 1), (x - 52 * k, y + 8 * k, 1)]
    inner = "".join(line([(x - 50 * k, y + 8 * k - th + j * th / 4), (x + 48 * k, y + 8 * k - th + j * th / 4)], 1.4, "#c9a63a", seed=seed + 5 + j, op=.9)
                    for j in (1, 2, 3))
    return (blob([(p[0] + 5, p[1] + 5) for p in side], "#3a2410", .25) + shape(side, "#f2cf4a", inner, w=3, seed=seed + 1) +
            shape(top, "#ffe066", blob([(x - 30 * k, y - 4 * k - th), (x + 20 * k, y - 5 * k - th), (x + 22 * k, y - 2 * k - th), (x - 28 * k, y - 1 * k - th)],
                                       "#fff3a8", .9), w=3, seed=seed))


def s11(t):
    den.set_tod("day")
    td, tn = T_DEN, T_NAPIS
    k = ease_io(clamp((t - 15.52) / 2.08))
    s = (1.45 + .2 * k) * (1 + punch(t, td, .05, .05, .35) + punch(t, tn, .05, .04, .3))
    sh = bump(t, td + .05, .3)
    cam = (470 + 15 * k + 5 * sh * osc(t, 13), 1010 - 10 * k, s, .5 - .8 * k + 1.0 * sh * osc(t, 9))
    # ближняя рука: на свитке → смах вправо → назад, поднимает ручку, щелчок
    sw0, sw1 = td - .12, td + .2
    if t < sw0:
        wr = np.array([480.0 + 6 * osc(t, 1.5), 1072.0])
    elif t < sw1:
        e = ease_io((t - sw0) / (sw1 - sw0))
        wr = np.array([480 + 175 * e, 1072 - 30 * math.sin(math.pi * e)])
    else:
        e = ease_io(clamp((t - sw1) / .4))
        wr = np.array([655 - 195 * e, 1072 - 80 * e])
    wr = wr + np.array([0, -6 * bump(t, tn, .2)])
    top, tip, hn = pen_fist(wr)
    click = bump(t, tn, .16)
    det = smooth(td - .3, td - .1, t)
    expr = dict(lid=.75, look=(.65, .45 - .3 * det), brows="det" if t < td + .3 else "up", mouth="smile", smile=.7 + .3 * det,
                closed=max(blink_at(t, 15.85, .15), blink_at(t, 17.25, .14)), hair=6 * bump(t, td, .35))
    # дальняя рука подтягивает стикер к себе
    pull = ease_io(clamp((t - (td + .25)) / .35))
    fw = (560 - 110 * pull, 1100)
    arms = {"n": ("ik", tuple(wr), -1), "f": ("ik", fw, -1)}
    hands = {"n": hn, "f": dict(kind="open", dir=(1, .2), curl=(.15, .2, .25, .3), spread=.1, thumb=.3)}
    d = dima(t, arms, hands, expr, lean=.16 + .2 * smooth(sw0 - .1, sw0 + .1, t) * (1 - smooth(sw1, sw1 + .3, t)), head_ang=-.04)
    pen_svg = Sc.pen(tuple(top), tuple(tip), 11, click=click)
    # свиток: улетает вправо после удара руки
    v = t - (td - .02)
    if v <= 0:
        gx, gy, gr = 0.0, 0.0, 0.0
    else:
        gx, gy, gr = 2200 * v * v + 300 * v, -120 * math.sin(min(v, .5) * math.pi) + 400 * v * v, 40 * v
    lst = desk_list(t, 1600, off=0, sway=.1 * osc(t, .9) + 2.5 * clamp(v * 3), seed=500, num0=1)
    lst = f'<g transform="translate({gx:.1f} {gy:.1f}) rotate({gr:.2f} 560 1110)">{lst}</g>'
    card = sticky(560 - 110 * pull + 70, 1106, 1.35)
    front = ""
    if 0 < v < .45 and gx > 220:
        for j in range(4):
            y = 1080 + j * 70
            x = SX0 - 50 + gx
            front += line([(x - 160, y), (x - 30, y)], 5, "#3a2a22", seed=5400 + j, op=1, taper=.3, wmin=.4)
    if t > tn:
        uu = clamp((t - tn) / .3)
        if uu < 1:
            for j in range(6):
                a = math.radians(-160 + j * 28)
                r0, r1 = 22 + 26 * uu, 40 + 40 * uu
                front += line([(top[0] + r0 * math.cos(a), top[1] + r0 * math.sin(a)), (top[0] + r1 * math.cos(a), top[1] + r1 * math.sin(a))], 5,
                              "#ffb43a", seed=5450 + j, taper=.3, wmin=.4)
    w = desk_world(t, d, (*clock_ang(10, 10 + 2 * t), 0.0, 0.0), on_desk=mug(t, 830, 1100, .42) + card + lst, mid=pen_svg, front=front, lamp_on=0)
    return compose(w, cam, "day")


SHOTS = {"s01": s01, "s03": s03, "s05": s05, "s08": s08, "s11": s11}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    den.LAMP_B = (985.0, 1084.0)
    return SHOTS[sid](t)
