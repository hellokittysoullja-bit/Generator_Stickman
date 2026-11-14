"""Рилс 60 «темнота», группа B: s03 (лампа гаснет, книга, нырок под одеяло), s05 (мама в проёме грозит пальцем),
s07 (маленький Дима трёт глаза и зевает при фонарике). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Люди — только ../common/people.py, предметы — ../common/props.py. Печатных букв и цифр нет."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
from lib import (INK, back_out, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, rrect, shape,  # noqa: E402,F401
                 smooth, spring)

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def decay(t, t0, k=9.0, fr=22.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def open_hand(c=.2, d=(1, 0), spread=.2, thumb=.2, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(c, c, c, c * .9), spread=spread, thumb=thumb, bend=.1, k=k)


def fist(d=(1, 0), flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(.97, .97, .97, .95), spread=.04, thumb=.85, bend=.05, k=k)


def point_hand(d, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(0.0, .92, .92, .92), spread=.05, thumb=.75, bend=.05, k=k)


def person(who, hip, s, expr, arms, hands, lean=0.0, head_ang=0.0, head_off=(0, 0), feet=None):
    p = dict(hip=tuple(hip), scale=s * people.HEIGHT.get(who, 1.0), lean=lean, torso_k=1.0, feet=feet, arms=arms, hands=hands, expr=expr,
             head_ang=head_ang, head_off=head_off, hood=0.0, strings=(0, 0))
    return people.draw(p, who)


def lin(stops, x1=0, y1=0, x2=0, y2=1):
    return lib.lin_grad(stops, x1, y1, x2, y2)


# ═════════════════════════════ детская (общий фон s03 / s07) ═════════════════════════════
WALL = "#7686bd"
WALL_SH = "#5d6ca3"
FLOOR = "#8a6a50"


def nursery_wall(x0=-500, x1=1700, y_floor=1290, win_x=900, win_y=760, win_w=330, win_h=420, t=0.0):
    g = lin([(0, "#6c7bb2", 1), (1, "#8796c8", 1)])
    o = [f'<rect x="{x0}" y="-600" width="{x1 - x0}" height="{y_floor + 600}" fill="url(#{g})"/>']
    # обои: ряды звёздочек-ромбиков без букв
    for j in range(9):
        for i in range(int((x1 - x0) / 150) + 1):
            x = x0 + 40 + i * 150 + (75 if j % 2 else 0)
            y = -520 + j * 190
            if y > y_floor - 60:
                continue
            o.append(blob([(x, y - 11), (x + 7, y), (x, y + 11), (x - 7, y)], "#9aa8d6", .8))
    # плинтус и пол
    o.append(blob(rect_pts(x0, y_floor, x1, 2600), FLOOR))
    for k in range(6):
        o.append(line([(x0, y_floor + 40 + k * 70), (x1, y_floor + 44 + k * 70)], 2.4, "#6e5240", taper=0, wmin=1, seed=40 + k, op=.7))
    o.append(shape(rect_pts(x0, y_floor - 26, x1, y_floor + 4), "#e9e1d0", "", w=3.6, seed=31))
    o.append(PR.window(win_x, win_y, win_w, win_h, "night", t, seed=3))
    return "".join(o)


def nightstand(x, y_floor, k=1.0):
    o = [shape(rrect(x - 90 * k, y_floor - 200 * k, x + 90 * k, y_floor - 10 * k, 6), PR.C_WOOD, blob(rect_pts(x - 90 * k, y_floor - 60 * k, x + 90 * k, y_floor), PR.C_WOOD_SH), w=4.0, seed=51)]
    o.append(line([(x - 80 * k, y_floor - 120 * k), (x + 80 * k, y_floor - 118 * k)], 3.0, PR.C_WOOD_SH, taper=.1, wmin=.8, seed=52))
    o.append(shape(ellipse_pts(x, y_floor - 150 * k, 9 * k, 7 * k, 10), "#e9c27a", "", w=2.4, seed=53))
    o.append(shape(rrect(x - 104 * k, y_floor - 222 * k, x + 104 * k, y_floor - 196 * k, 6), PR.C_WOOD_HI, "", w=4.0, seed=54))
    return "".join(o)


# ═════════════════════════════ s03: лампа гаснет, книга, нырок ═════════════════════════════
T_DIMA, T_CHIT, T_POD, T_ODEY = wt(7), wt(10), wt(11), wt(12)     # 3.26, 3.98, 4.30, 4.507
S03_FLOOR = 1290
BED_X, BED_K = 640, 1.55
MATT_Y = S03_FLOOR - 118 * BED_K


def book_turn(bx, by, k, u, rot=0.0):
    """Книга раскрывается: u 0 — закрыта (обложкой к зрителю, узкая), 1 — раскрыта страницами к зрителю."""
    if u < .5:
        sx = 1 - 1.5 * u            # обложка «складывается» при повороте
        inner = PR.book_back(0, 0, 1.0, 0.0, PR.C_RED_COVER)
        return f'<g transform="translate({f(bx)} {f(by)}) rotate({f(rot)}) scale({k * max(.32, sx) * .62:.4f} {k:.4f})">{inner}</g>'
    sx = .25 + .75 * ease_out((u - .5) * 2)
    inner = PR.book_open(0, 0, 1.0, 0.0, flip=0.0, seed=2, cover=PR.C_RED_COVER)
    return f'<g transform="translate({f(bx)} {f(by)}) rotate({f(rot)}) scale({k * sx:.4f} {k:.4f})">{inner}</g>'


def frame03(t):
    a = 3.0
    pan = ease_io(clamp((t - a) / 2.1))
    pull = ease_io(clamp((t - (T_ODEY + .1)) / .5))
    z = 1.24 + .06 * pan - .14 * pull
    set_ink(z)
    lamp = 1.0 - smooth(T_DIMA + .02, T_DIMA + .1, t)                     # щёлк — гаснет за 2–3 кадра
    flick = .25 * bump(t, T_DIMA + .12, .12)                               # нить ещё раз мигнула
    lamp = max(lamp, flick)
    o = [nursery_wall(t=t, win_x=930, win_y=840)]
    o.append(nightstand(110, S03_FLOOR, 1.1))
    o.append(PR.lamp_desk(100, S03_FLOOR - 222 * 1.1, 1.25, on=lamp))
    o.append(PR.bed(BED_X, S03_FLOOR, BED_K))
    o.append(PR.pillow(310, MATT_Y + 4, 1.25, -8, seed=1))
    # маленький Дима сидит, спиной к подушке, ноги под одеялом
    dive = ease_in(clamp((t - (T_ODEY - .06)) / .26), 1.6)
    s = .86
    sc = s * people.HEIGHT["kid"]
    hip = (372 + 70 * dive, MATT_Y - 6 + 150 * dive)
    open_u = clamp((t - (T_CHIT - .06)) / .3)
    # книга: до «читал» — закрыта у груди, на «читал» раскрывается
    bk = 1.05
    bx = hip[0] + 255 - 20 * dive
    by = hip[1] - 40 - 30 * open_u + 6 * math.sin(t * 3)
    page_w = 100 * bk * (.25 + .75 * ease_out(clamp((open_u - .5) * 2))) if open_u >= .5 else 100 * bk * max(.32, 1 - 1.5 * open_u) * .62
    gy = by - 62 * bk
    gk = sc * 1.45
    R = 16 * gk
    cN = (bx - page_w + R - 4, gy + 6)
    cF = (bx + page_w - R + 4, gy - 4)
    wN = (cN[0] - (R + 52 * gk), cN[1] + 6)
    wF = (cF[0] + (R + 52 * gk), cF[1] + 6)
    look = (.75, .45) if open_u > .4 else (.6, .1 + .3 * lamp)
    expr = dict(lid=.95 if lamp > .5 else .75 + .2 * bump(t, T_DIMA + .1, .4), brows="up" if lamp < .5 else "calm",
                mouth="grin" if open_u > .5 else ("talk" if lamp < .5 else "smile"), open=.35, smile=.8, look=look,
                closed=blink_of(t, (3.12, 4.2)))
    if dive > .05:
        expr.update(lid=1.0, brows="up", mouth="grin", look=(.4, -.3))
    arms = {"n": ("ik", wN, -1), "f": ("ik", wF, -1)}
    hands = {"n": {"kind": "none"}, "f": {"kind": "none"}}
    kid = person("kid", hip, s, expr, arms, hands, lean=.04 + .5 * dive, head_ang=-.06 + .1 * open_u - .2 * dive + .02 * math.sin(t * 4),
                 head_off=(0, 3 * math.sin(t * 5)))
    gb_n, gf_n = people.grip_svg("kid", cN, R, -1, k=gk, h=60, seed=910)
    gb_f, gf_f = people.grip_svg("kid", cF, R, +1, k=gk * .96, h=60, seed=930)
    cover = back_out(clamp((t - (T_ODEY - .02)) / .24), 1.5)
    if cover < .9:
        kk = [kid["arm_f"], kid.get("pelvis", ""), kid["body"], gb_f + gb_n, book_turn(bx, by, bk, open_u), gf_f, kid["arm_n"] + gf_n]
        cid = lib.clip_rect(-600, -800, 2400, MATT_Y + 800)
        o.append(f'<g clip-path="url(#{cid})">{"".join(kk)}</g>')
    # одеяло на ногах; на «одеялом» оно взлетает и накрывает с головой
    o.append(PR.blanket(720, MATT_Y + 14, 1.0, 760, 120, seed=1, col="quilt", bump=1.0))
    if cover > 0.01:
        breath = 1 + .025 * math.sin((t - T_ODEY) * 7)
        o.append(PR.blanket(470 + 60 * cover, MATT_Y + 16, 1.0, 420 + 120 * cover, 400 * cover * breath, seed=4, col="quilt"))
    lit = clamp((t - (T_ODEY + .2)) / .15)          # под одеялом щёлкнул фонарик: свет из-под края
    # ночь: вуаль, пока горит лампа — слабая
    holes = [(PR.circle_d(100, S03_FLOOR - 400, 520 * lamp + 1, 420 * lamp + 1), lamp), (lib_rect_d(930 - 160, 840 - 410, 930 + 160, 840 - 10), .8),
             (PR.circle_d(430, 820, 300, 360), .45)]
    if lit > 0:
        holes.append((PR.circle_d(700, MATT_Y + 10, 260, 90), .9 * lit))
    o.append(PR.darkness(op=.25 + .4 * (1 - lamp), holes=holes, box=(-600, -700, 1800, 2700)))
    o.append(PR.glow(100, S03_FLOOR - 330, 420, .55 * lamp))
    if lit > 0:
        o.append(PR.glow(720, MATT_Y + 4, 260, .7 * lit * (1 + .1 * math.sin(t * 13)), ry=70))
        o.append(PR.beam(760, MATT_Y + 2, 6, 300, 26, .55 * lit, 1.2, core=False))
    shake = 8 * decay(t, T_ODEY + .18, 8, 20)
    cx = 470 + 230 * pan + shake
    cy = 900 + 40 * pan + 60 * pull
    cam = lib.cam(cx, cy, z, -.8 + 1.2 * pan + .8 * decay(t, T_ODEY + .18, 7, 14))
    return f'<g transform="{cam}">{"".join(o)}</g>'


def lib_rect_d(x0, y0, x1, y1):
    return f"M{f(x0)} {f(y0)}H{f(x1)}V{f(y1)}H{f(x0)}Z"


def frame(sid, t):
    lib.dyn_begin()
    fn = {"s03": frame03}[sid]
    return lib.svg(fn(t))
