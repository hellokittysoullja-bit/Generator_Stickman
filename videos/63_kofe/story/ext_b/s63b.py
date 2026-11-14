"""Рилс 63 «кофе», группа B — Дима с кружками: s04 (идёт в полный рост с кофе и водой, спотыкается, жонглирует, ловит),
s06 (кухня днём, одна обычная кружка, «Дима-изюм» лопается), s08 (диван, кофе и чай в ладонях как весы, чокается).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Люди и кот — ../common/people.py, cat.py; предметы — props.py (группа A),
комната — room.py (группа C); пока их нет — свои временные (`_mug`, фоны) в этом файле. Печатных букв и цифр нет."""
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
from lib import (INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth, spring)  # noqa: E402,F401

try:
    import props as PR  # noqa: E402
except ImportError:      # pragma: no cover
    PR = None

E = people.EXPR
C_COFFEE = "#4a2c1c"
C_WATER, C_WATER_SH, C_GLASS = "#7fc2ea", "#5aa6d6", "#e4f2f8"
C_TEA = "#c98a2e"


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


def shake2(t, t0, amp, k=9.0, fr=19.0):
    return amp * decay(t, t0, k, fr), amp * .7 * decay(t, t0 + .013, k, fr * 1.13)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


# ═════════════════════════════ кружка (временная, до props.py группы A) ═════════════════════════════
HANDLE = (44.0, -42.0)          # центр ручки в единицах кружки при handle=+1 (дно по центру, высота 78)


def _rot(p, deg):
    a = math.radians(deg)
    return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))


def handle_world(x, y, k, rot, hs):
    hx, hy = _rot((HANDLE[0] * hs, HANDLE[1]), rot)
    return x + hx * k, y + hy * k


def mug_at_handle(H, k, rot, hs):
    """Где дно кружки, если её ручка в точке H."""
    hx, hy = _rot((HANDLE[0] * hs, HANDLE[1]), rot)
    return H[0] - hx * k, H[1] - hy * k


def _mug(x, y, k=1.0, rot=0.0, kind="coffee", handle=1, steam=0.0, t=0.0, slosh=0.0, seed=0):
    """Кружка, (x, y) — центр дна, 66×78, ручка справа (handle=1) или слева (−1). kind: coffee — белая кружка с тёмным кофе
    и паром; water — прозрачная кружка-стакан с голубой водой; tea — белая чашка с янтарным чаем и ниточкой пакетика."""
    sd = 8800 + seed
    hs = handle
    o = []
    glass = kind == "water"
    body_c = C_GLASS if glass else ("#f3efe6" if kind == "tea" else "#eae4d6")
    sh_c = "#c9e2ee" if glass else "#cfc6b4"
    o.append(line([(hs * 30, -62), (hs * 54, -60), (hs * 58, -38), (hs * 30, -20)], 12, INK, taper=.0, wmin=1, seed=sd + 1))
    o.append(line([(hs * 30, -62), (hs * 52, -60), (hs * 55, -38), (hs * 30, -20)], 6.5, body_c, taper=.0, wmin=1, seed=sd + 2))
    body = [(-33, -76, 1), (-32, -30), (-30, -4), (-24, 0, 1), (24, 0, 1), (30, -4), (32, -30), (33, -76, 1)]
    inner = ""
    if glass:
        lvl = -60 + 8 * slosh
        inner += blob([(-40, lvl - 6 * slosh), (40, lvl + 6 * slosh), (40, 4), (-40, 4)], C_WATER)
        inner += blob([(-40, lvl + 10), (-16, lvl + 10), (-14, 4), (-40, 4)], C_WATER_SH)
        inner += line([(-36, lvl - 6 * slosh), (36, lvl + 6 * slosh)], 3.2, "#cfeefc", taper=.3, wmin=.4, seed=sd + 5)
        inner += line([(18 * hs, -68), (19 * hs, -14)], 5, "#ffffff", taper=.4, wmin=.3, seed=sd + 3)
    else:
        inner += blob([(18, -80), (40, -80), (40, 4), (14, 4)] if hs > 0 else [(-40, -80), (-18, -80), (-14, 4), (-40, 4)], sh_c)
        inner += line([(-20 * hs, -66), (-21 * hs, -20)], 5, "#ffffff", taper=.4, wmin=.3, seed=sd + 3)
    o.append(shape(body, body_c, inner, w=3.8, seed=sd))
    if not glass:
        o.append(shape(ellipse_pts(0, -76, 33, 9, 16), sh_c, "", w=3.2, seed=sd + 4))
        o.append(blob(ellipse_pts(0, -74.5, 27, 6.5, 14), C_COFFEE if kind == "coffee" else C_TEA))
        o.append(blob(ellipse_pts(-8, -76, 8, 2, 8), "#7A563C" if kind == "coffee" else "#e3ad55"))
        if kind == "tea":      # ниточка пакетика через край и ярлычок без букв
            o.append(line([(10, -76), (34 * -hs, -70), (36 * -hs, -48)], 2.2, "#efe9dc", taper=0, wmin=1, seed=sd + 7))
            o.append(shape(lib.rrect(36 * -hs - 9, -50, 36 * -hs + 9, -32, 3), "#e9d8a6", "", w=2.6, seed=sd + 8))
    else:
        o.append(line([(-33, -76), (0, -82), (33, -76)], 3.4, INK, taper=.3, wmin=.4, seed=sd + 6))
    if steam > 0.01:
        for j in range(3):
            ph = t * 2.6 + j * 2.1
            xs = -14 + 14 * j
            pts = [(xs + 8 * math.sin(ph + i * .9), -92 - 16 * i) for i in range(5)]
            o.append(line(pts, 4.0 * steam, "#a8acb4", taper=.8, wmin=.1, seed=sd + 10 + j))
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{"".join(o)}</g>'


def mug(x, y, k=1.0, rot=0.0, kind="coffee", handle=1, steam=0.0, t=0.0, slosh=0.0, seed=0):
    return _mug(x, y, k, rot, kind, handle, steam, t, slosh, seed)


def drops(cx, cy, t, t0, n, col, seed, spread=160.0, up=260.0, life=.55, r=9.0):
    """Капли-плеск: вылетают из (cx, cy) в момент t0, летят по параболам вниз (g), каждая — сплошная капля с бликом."""
    u = t - t0
    if u <= 0 or u > life:
        return ""
    rs = np.random.RandomState(seed)
    o = []
    for i in range(n):
        vx = rs.uniform(-1, 1) * spread
        vy = -rs.uniform(.5, 1.0) * up
        x, y = cx + vx * u * 2.2, cy + vy * u * 2.2 + 1600 * u * u
        rr = r * rs.uniform(.6, 1.15) * (1 - .4 * u / life)
        ang = math.degrees(math.atan2(vy * 2.2 + 3200 * u, vx * 2.2)) - 90
        pts = [(0, -rr * 1.9), (rr * .75, -rr * .2), (rr, rr * .4), (0, rr), (-rr, rr * .4), (-rr * .75, -rr * .2)]
        pts = [(x + _rot(p, ang)[0], y + _rot(p, ang)[1]) for p in pts]
        o.append(shape(pts, col, "", w=2.4, seed=seed + i))
    return "".join(o)


# ═════════════════════════════ s04: идёт с двумя кружками, спотыкается, жонглирует ═════════════════════════════
T4_HODIL, T4_DVUMYA, T4_KRUZH, T4_SRAZU = 6.30, 6.75, 7.12, 7.68
T4_REL_C, T4_REL_W = 7.15, 7.21          # отпустил кофе (ближняя рука), воду (дальняя)
T4_CATCH_C, T4_CATCH_W = 7.47, 7.70      # кофе ловит дальняя рука, воду — ближняя
SC4 = .74
G4 = 1585.0                              # пол (щиколотки)
HIP4 = G4 - (people.LEG_LEN - 12) * SC4 * people.HEIGHT["dima"]


def _speed4(t):
    if t < T4_KRUZH:
        return 255.0
    if t < 7.32:        # спотыкается — тело проносит вперёд
        return 255 + 230 * math.sin(math.pi * (t - T4_KRUZH) / .2)
    return 255 * (1 - smooth(7.32, 8.05, t)) + 40


def _x4(t, t0=5.95):
    n = max(1, int((t - t0) * 120))
    dt = (t - t0) / n
    return 230.0 + sum(_speed4(t0 + (i + .5) * dt) for i in range(n)) * dt


def _hold4(t, x):
    """Цели запястий (n — ближняя, кофе; f — дальняя, вода) в держании до броска / после ловли."""
    s = SC4
    lift = ease_out(clamp((t - T4_DVUMYA) / .22), 3) + .12 * decay(t, T4_DVUMYA + .18, 7, 3)
    n = (x + (215 + 150 * lift) * s, HIP4 - (215 + 120 * lift) * s)
    f = (x + (265 + 150 * lift) * s, HIP4 - (250 + 130 * lift) * s)
    return n, f


def s04(t):
    lib.dyn_begin()
    s = SC4
    x = _x4(t)
    stride = 230.0
    phase = (x - 230.0) / (2 * stride * s * people.HEIGHT["dima"])
    wk = people.walk_kw(x, HIP4, s, phase, stride=stride, lift=70 if t < T4_KRUZH else 95)
    # спотыкается: ближний носок цепляется, корпус клонится вперёд с пружиной обратно
    trip = math.exp(-3.2 * max(0.0, t - 7.28)) * ease_out(clamp((t - T4_KRUZH) / .14), 2) if t > T4_KRUZH else 0.0
    lean = .07 + .03 * math.sin(2 * math.pi * phase * 2) + .28 * trip
    hip = (wk["hip"][0] + 30 * trip, wk["hip"][1] + 22 * trip)
    # ── кружки: держит, бросает, ловит
    hn, hf = _hold4(t, x)
    kmug = 1.75 * s
    cc = dict(kind="coffee", handle=-1, steam=1.0)
    ww = dict(kind="water", handle=-1)
    mugs = []          # (svg, draw_after) — после тела
    hands = {}
    grip_n = grip_f = None
    xr_c, xr_w = _x4(T4_REL_C), _x4(T4_REL_W)
    # точки броска (ручки у кистей в момент броска) и ловли
    hn_rel = (_hold4(T4_REL_C, xr_c)[0][0] + 40 * s, _hold4(T4_REL_C, xr_c)[0][1] - 40 * s)
    hf_rel = (_hold4(T4_REL_W, xr_w)[1][0] + 40 * s, _hold4(T4_REL_W, xr_w)[1][1] - 40 * s)
    catch_c = (_x4(T4_CATCH_C) + 440 * s, HIP4 - 540 * s)       # кофе ловит дальняя рука повыше
    catch_w = (_x4(T4_CATCH_W) + 470 * s, HIP4 - 470 * s)       # воду — ближняя
    HO = 46 * s * 1.15        # от запястья до центра ручки

    def mug_held(W, kind_kw, slosh=0.0, far=False, sd=0, rot=0.0):
        H = (W[0] + HO, W[1] - 4 * s)
        mx, my = mug_at_handle(H, kmug, rot, -1)
        back, front = people.handle_grip("dima", H, k=s, side=-1, far=far, seed=960 + sd)
        return back + mug(mx, my, kmug, rot, t=t, slosh=slosh, seed=sd, **kind_kw) + front

    # кофе
    if t < T4_REL_C:
        W = (hn[0] - 30 * s * trip, hn[1] - 60 * s * trip)
        tn = W
        mugs.append(("n", mug_held(W, cc, sd=1)))
        hands["n"] = {"kind": "none"}
    elif t < T4_CATCH_C:
        u = (t - T4_REL_C) / (T4_CATCH_C - T4_REL_C)
        p0 = (hn_rel[0] + HO, hn_rel[1])
        p1 = (catch_c[0] + HO, catch_c[1])
        hx, hy, rr = people.juggle_arc(p0, p1, u, 330)
        mx, my = mug_at_handle((hx, hy), kmug, rr, -1)
        mugs.append(("air", mug(mx, my, kmug, rr, t=t, seed=1, **dict(cc, steam=.5))))
    else:
        W = catch_c if t < T4_CATCH_C + .05 else None
        mugs.append(("f", None))
    # вода
    if t < T4_REL_W:
        W = (hf[0] - 30 * s * trip, hf[1] - 60 * s * trip)
        mugs.append(("f", mug_held(W, ww, slosh=.6 * trip, far=False, sd=2)))
        hands["f"] = {"kind": "none"}
    elif t < T4_CATCH_W:
        u = (t - T4_REL_W) / (T4_CATCH_W - T4_REL_W)
        p0 = (hf_rel[0] + HO, hf_rel[1])
        p1 = (catch_w[0] + HO, catch_w[1])
        hx, hy, rr = people.juggle_arc(p0, p1, u, 420)
        mx, my = mug_at_handle((hx, hy), kmug, -rr, -1)
        mugs.append(("air", mug(mx, my, kmug, -rr, t=t, slosh=math.sin(u * 9), seed=2, **ww)))
    # ── руки: держат / тянутся к кружкам в полёте / ловят и опускают к груди
    tg = {}
    # ближняя (кофе → потом вода)
    if t < T4_REL_C:
        tg["n"] = (hn[0] - 30 * s * trip, hn[1] - 60 * s * trip)
    elif t < T4_CATCH_W:
        # подбросил вверх и тянется к будущей точке ловли воды
        a = ease_out(clamp((t - T4_REL_C) / .12), 2)
        up = (hn_rel[0] + 90 * s, hn_rel[1] - 220 * s)
        u2 = smooth(T4_CATCH_W - .3, T4_CATCH_W, t)
        tg["n"] = tuple(np.array(hn_rel) * (1 - a) + np.array(up) * a * (1 - u2) + np.array(catch_w) * a * u2 + np.array([0, 0]) * 0)
        if a < 1 and u2 == 0:
            tg["n"] = tuple(np.array(hn_rel) * (1 - a) + np.array(up) * a)
        hands["n"] = {"dir": (.35, -1), "spread": .45, "curl": (.05, .05, .1, .15), "thumb": .1}
    else:
        dn = smooth(T4_CATCH_W + .08, T4_CATCH_W + .5, t)
        hold = _hold4(t, x)[0]
        bounce = 26 * s * decay(t, T4_CATCH_W, 8, 2.5)
        tg["n"] = (catch_w[0] * (1 - dn) + hold[0] * dn, catch_w[1] * (1 - dn) + (hold[1] - 40 * s) * dn + bounce)
        hands["n"] = {"kind": "none"}
        grip_n = (tg["n"], ww, "n")
    # дальняя (вода → потом кофе)
    if t < T4_REL_W:
        tg["f"] = (hf[0] - 30 * s * trip, hf[1] - 60 * s * trip)
    elif t < T4_CATCH_C:
        a = ease_out(clamp((t - T4_REL_W) / .1), 2)
        u2 = smooth(T4_CATCH_C - .22, T4_CATCH_C, t)
        up = (hf_rel[0] + 70 * s, hf_rel[1] - 200 * s)
        tg["f"] = tuple(np.array(hf_rel) * (1 - a) + (np.array(up) * (1 - u2) + np.array(catch_c) * u2) * a)
        hands["f"] = {"dir": (.3, -1), "spread": .45, "curl": (.05, .05, .1, .15), "thumb": .1}
    else:
        dn = smooth(T4_CATCH_C + .3, T4_CATCH_C + .75, t)
        hold = _hold4(t, x)[1]
        bounce = 22 * s * decay(t, T4_CATCH_C, 8, 2.5)
        tg["f"] = (catch_c[0] * (1 - dn) + hold[0] * dn, catch_c[1] * (1 - dn) + (hold[1] - 30 * s) * dn + bounce)
        hands["f"] = {"kind": "none"}
        grip_f = (tg["f"], cc, "f")
    arms = {k: ("ik", v, -1) for k, v in tg.items()}
    # мимика
    if t < T4_KRUZH:
        ex = dict(E["dima"]["focus"], look=(.55, .35))
        ex["closed"] = blink_of(t, [6.48], .16)
    elif t < T4_SRAZU:
        lk_y = -.85 + .4 * smooth(7.35, 7.6, t)
        ex = dict(E["dima"]["scared"], look=(.35, lk_y))
    elif t < 7.95:
        ex = dict(E["dima"]["grimace_ok"])
    else:
        ex = dict(E["dima"]["relief"])
        ex["closed"] = blink_of(t, [8.2], .16)
    ha = -.14 * smooth(T4_KRUZH, T4_KRUZH + .15, t) * (1 - smooth(7.75, 8.0, t)) + .05 * math.sin(2 * math.pi * phase * 2)
    fig = people.figure("dima", hip[0], hip[1], s, ex, lean=lean, head_ang=ha, arms=arms, hands=hands, feet=wk["feet"],
                        layers=("legs", "pelvis", "arm_f", "body"))
    near_arm = people.figure("dima", hip[0], hip[1], s, ex, lean=lean, head_ang=ha, arms=arms, hands=hands, feet=wk["feet"],
                             layers=("arm_n",))
    W_n, W_f = fig["wrist"]["n"], fig["wrist"]["f"]
    # перерисовать держания по настоящим запястьям (ИК могло не дотянуться)
    far_mug = near_mug = ""
    air = [m[1] for m in mugs if m[0] == "air"]
    if t < T4_REL_C:
        near_mug = mug_held(W_n, cc, sd=1)
    if t < T4_REL_W:
        far_mug = mug_held(W_f, ww, slosh=.6 * trip, sd=2)
    if grip_f:
        far_mug = mug_held(W_f, cc, sd=1, rot=-6 * decay(t, T4_CATCH_C, 6, 2))
    if grip_n:
        near_mug = mug_held(W_n, ww, slosh=1.2 * decay(t, T4_CATCH_W, 4, 2.2), sd=2, rot=8 * decay(t, T4_CATCH_W, 6, 2))
    splash = drops(W_n[0] + HO + 40 * s, W_n[1] - 70 * s, t, T4_CATCH_W, 9, C_WATER, 4100, spread=150, up=300)
    splash += drops(W_f[0] + HO + 40 * s, W_f[1] - 70 * s, t, T4_CATCH_C, 4, C_COFFEE, 4200, spread=90, up=200, r=7)
    # хлопки ловли: короткие штрихи
    pops = ""
    for tc, W in ((T4_CATCH_C, W_f), (T4_CATCH_W, W_n)):
        u = (t - tc) / .22
        if 0 < u < 1:
            for i in range(5):
                th = -2.6 + i * .45
                r0, r1 = 90 + 50 * u, 130 + 80 * u
                c = (W[0] + HO + 40 * s, W[1] - 40 * s)
                pops += line([(c[0] + math.cos(th) * r0, c[1] + math.sin(th) * r0), (c[0] + math.cos(th) * r1, c[1] + math.sin(th) * r1)],
                             7, INK, seed=4300 + i, taper=.5, wmin=.2, op=1)
    world = [hallway(t), fig["svg"], far_mug, near_arm["svg"], near_mug, "".join(air), splash, pops]
    # камера: панорама за Димой слева направо, тряска на ловле
    cx = 560 + (x - 230) * .78
    sx, sy = shake2(t, T4_CATCH_C, 9)
    sx2, sy2 = shake2(t, T4_CATCH_W, 16)
    sx3, sy3 = shake2(t, T4_KRUZH + .04, 8)
    z = 1.02 - .02 * clamp((t - 6.0) / 2.4) + .03 * bump(t, T4_CATCH_W, .4)
    set_ink(1.0)
    cam = lib.cam(cx - sx - sx2 - sx3, 1000 - sy - sy2 - sy3 - 30 * bump(t, 7.3, .6), z, .8 * math.sin((t - 6) * 1.3) - 1.2 * bump(t, T4_KRUZH, .4))
    return lib.svg(f'<rect width="1080" height="1920" fill="#e9dcc4"/><g transform="{cam}">{"".join(world)}</g>')


def hallway(t, x0=-400, x1=2600):
    """Коридор: тёплая стена с панелями, двери, вешалка, плинтус, деревянный пол с дорожкой. Без надписей."""
    o = []
    o.append(f'<rect x="{x0}" y="0" width="{x1 - x0}" height="{G4 - 40}" fill="#efdcbc"/>')
    o.append(f'<rect x="{x0}" y="{G4 - 520}" width="{x1 - x0}" height="480" fill="#d9b98c"/>')
    o.append(line([(x0, G4 - 520), (x1, G4 - 520)], 5, INK, seed=5001, taper=.05, wmin=.6))
    for i, xx in enumerate(range(x0 + 80, x1, 260)):
        o.append(shape(lib.rrect(xx, G4 - 480, xx + 210, G4 - 90, 10), "#d3b081", "", w=3.0, seed=5010 + i))
    for i, xx in enumerate((150, 1250, 2350)):
        door = lib.rrect(xx, 420, xx + 380, G4 - 40, 0)
        o.append(shape(lib.rrect(xx - 26, 394, xx + 406, G4 - 40, 0), "#f6ecd8", "", w=4.2, seed=5100 + i))
        o.append(shape(door, "#b9875a", blob(lib.rrect(xx + 20, 450, xx + 180, G4 - 70, 8), "#a87749"), w=4.6, seed=5110 + i))
        o.append(shape(lib.rrect(xx + 40, 480, xx + 340, 900, 8), "#c39466", "", w=3.0, seed=5120 + i))
        o.append(shape(lib.rrect(xx + 40, 960, xx + 340, G4 - 120, 8), "#c39466", "", w=3.0, seed=5130 + i))
        o.append(shape(ellipse_pts(xx + 340, 1020, 16, 16, 12), "#e3b84a", "", w=3.0, seed=5140 + i))
    # вешалка с курткой и шарфом между дверями
    hx = 780
    o.append(shape(lib.rrect(hx - 160, 560, hx + 160, 590, 10), "#8c5f3a", "", w=3.6, seed=5200))
    o.append(shape([(hx - 110, 590), (hx - 40, 600), (hx - 20, 980), (hx - 150, 1000), (hx - 160, 700)], "#6d8fb3",
                   blob([(hx - 110, 640), (hx - 70, 640), (hx - 80, 980), (hx - 140, 990)], "#58789a"), w=4.2, seed=5201))
    o.append(shape([(hx + 50, 590), (hx + 90, 596), (hx + 84, 900), (hx + 56, 910)], "#d2513f", "", w=3.6, seed=5202))
    o.append(shape(ellipse_pts(1880, 760, 120, 120, 20), "#f6ecd8", blob(ellipse_pts(1860, 740, 80, 80, 16), "#cfe3ea"), w=4.4, seed=5210))
    # пол и плинтус
    o.append(f'<rect x="{x0}" y="{G4 - 40}" width="{x1 - x0}" height="600" fill="#b98f62"/>')
    o.append(shape([(x0, G4 - 52), (x1, G4 - 52), (x1, G4 - 28), (x0, G4 - 28)], "#f3e6cc", "", w=3.4, seed=5300))
    for i in range(14):
        yy = G4 + 10 + i * 46
        o.append(line([(x0, yy), (x1, yy)], 2.4, "#8f6a44", seed=5310 + i, taper=.1, wmin=.4))
    o.append(shape([(x0, G4 - 10), (x1, G4 - 10), (x1, G4 + 70), (x0, G4 + 70)], "#b0473d",
                   blob([(x0, G4 + 4), (x1, G4 + 4), (x1, G4 + 16), (x0, G4 + 16)], "#d1704f"), w=3.6, seed=5320))
    return "".join(o)


def frame(sid, t):
    return {"s04": s04}[sid](t)
