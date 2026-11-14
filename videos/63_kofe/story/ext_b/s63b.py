"""Рилс 63 «кофе», группа B — Дима с кружками: s04 (идёт в полный рост с кофе и водой, спотыкается, жонглирует, ловит),
s06 (кухня днём, одна обычная кружка, «Дима-изюм» лопается), s08 (диван, кофе и чай в ладонях как весы, чокается).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Люди и кот — ../common/people.py, cat.py; предметы — props.py (группа A),
комната — room.py (группа C); коридор s04 — свой (hallway). Печатных букв и цифр нет."""
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

import props as PR  # noqa: E402
import room as R  # noqa: E402

E = people.EXPR


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


# ═════════════════════════════ кружки из props.py (группа A) и хват ═════════════════════════════
MUG_HANDLE = (88.0, -70.0)       # центр ручки PR.coffee_mug (ручка справа, дно в (0, 0), высота 130)
TEA_HANDLE = (80.0, -60.0)       # центр ручки чашки PR.tea_cup
GLASS_MID = -70.0                # середина стакана PR.glass по высоте (хват обхватом)


def _rot(p, deg):
    a = math.radians(deg)
    return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))


def base_from_point(P, local, k, rot, hs):
    """Где дно предмета, если его точка local (при ручке справа) стоит в мире в P; hs=−1 — предмет отражён (ручка слева)."""
    hx, hy = _rot((local[0] * hs, local[1]), rot)
    return P[0] - hx * k, P[1] - hy * k


def _mirror(svg, x, hs):
    return svg if hs > 0 else f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{svg}</g>'


def cmug(x, y, k, rot=0.0, hs=1, **kw):
    """Кружка кофе PR.coffee_mug; hs=−1 — ручка слева (зеркально)."""
    return _mirror(PR.coffee_mug(x, y, k, rot * hs, **kw), x, hs)


def tcup(x, y, k, rot=0.0, hs=1, saucer=False, **kw):
    """Чашка чая PR.tea_cup; saucer=False — без блюдца (чашка в руке, блюдце срезано клипом по контуру чашки)."""
    svg = PR.tea_cup(0, 0, 1.0, 0, **kw)
    if not saucer:
        cid = lib.clip_of([(-70, -150), (100, -150), (100, -28), (54, -28), (46, -14), (28, -9), (-28, -9), (-46, -14), (-62, -44), (-70, -60)])
        svg = f'<g clip-path="url(#{cid})">{svg}</g>'
    svg = f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot * hs:.2f}) scale({k:.4f})">{svg}</g>'
    return _mirror(svg, x, hs)


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
    kmug = 1.05 * s
    kgl = .95 * s
    cc = "coffee"
    ww = "water"
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
    GR = 40 * kgl             # полуширина стакана
    GO = GR + 50 * s          # от запястья до центра стакана

    def obj(kind, P, rot, slosh=0.0, sd=0, steam=1.0):
        """Предмет по точке хвата P (кофе — центр ручки, вода — середина стакана)."""
        if kind == "coffee":
            bx, by = base_from_point(P, MUG_HANDLE, kmug, rot, -1)
            return cmug(bx, by, kmug, rot, -1, steam=steam, t=t, seed=sd)
        bx, by = base_from_point(P, (0.0, GLASS_MID), kgl, rot, 1)
        return PR.glass(bx, by, kgl, rot, fill=.85, t=t, splash=slosh, seed=sd)

    def mug_held(W, kind, slosh=0.0, far=False, sd=0, rot=0.0):
        if kind == "coffee":
            H = (W[0] + HO, W[1] - 4 * s)
            back, front = people.handle_grip("dima", H, k=s, side=-1, far=far, seed=960 + sd)
        else:
            H = (W[0] + GO, W[1] - 4 * s)
            back, front = people.grip_svg("dima", H, GR, -1, k=s * 1.1, seed=980 + sd)
        return back + obj(kind, H, rot, slosh, sd) + front

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
        mugs.append(("air", obj(cc, (hx, hy), rr, sd=1, steam=.4)))
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
        p0 = (hf_rel[0] + GO, hf_rel[1])
        p1 = (catch_w[0] + GO, catch_w[1])
        hx, hy, rr = people.juggle_arc(p0, p1, u, 420)
        mugs.append(("air", obj(ww, (hx, hy), -rr * .5, sd=2)))
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
        far_mug = mug_held(W_f, ww, slosh=.5 * trip, sd=2)
    if grip_f:
        far_mug = mug_held(W_f, cc, sd=1, rot=-6 * decay(t, T4_CATCH_C, 6, 2))
    if grip_n:
        near_mug = mug_held(W_n, ww, slosh=clamp((t - T4_CATCH_W) / .45) if t < T4_CATCH_W + .45 else 0.0, sd=2, rot=8 * decay(t, T4_CATCH_W, 6, 2))
    splash = drops(W_n[0] + GO, W_n[1] - 80 * s, t, T4_CATCH_W, 7, PR.C_WATER, 4100, spread=150, up=300)
    splash += drops(W_f[0] + HO + 40 * s, W_f[1] - 70 * s, t, T4_CATCH_C, 4, PR.C_COFFEE_DARK, 4200, spread=90, up=200, r=7)
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


# ═════════════════════════════ s06: кухня днём, одна обычная кружка, «Дима-изюм» ═════════════════════════════
T6_OBYCH, T6_CHASHKA, T6_KOFE, T6_POCHTI, T6_NE, T6_SUSHIT, T6_ORG = 9.60, 10.16, 10.53, 10.95, 11.33, 11.48, 11.82
T6_POP = 11.40
SC6 = 1.12


def dashed(pts, w, dash=26.0, gap=16.0, seed=0, col=INK):
    """Пунктир по ломаной: короткие штрихи тушью, просветы — бумага."""
    P = np.array(pts, float)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    o, d, i = [], 0.0, 0
    while d < seg[-1]:
        a, b = d, min(d + dash, seg[-1])
        q = [tuple(np.array([np.interp(v, seg, P[:, 0]), np.interp(v, seg, P[:, 1])])) for v in np.linspace(a, b, 4)]
        o.append(line(q, w, col, seed=seed + i, taper=.35, wmin=.4))
        d += dash + gap
        i += 1
    return "".join(o)


def raisin(cx, cy, k, u, burst, t, seed=6100):
    """Пунктирный «Дима-изюм»: сморщенная голова с вихрами, глаза-точки, губы волной, морщины. u — проявление 0..1 (растёт пружиной),
    burst 0..1 — лопается: контур раздувается и рвётся на штрихи, летящие наружу."""
    if u <= 0 or burst >= 1:
        return ""
    o = []
    if burst <= 0:
        kk = k * u
        n = 40
        pts = []
        for i in range(n + 1):
            a = 2 * math.pi * i / n
            r = 120 * (1 + .09 * math.sin(7 * a + 1.3) + .05 * math.sin(13 * a)) * kk
            pts.append((cx + r * math.cos(a) * .86, cy + r * math.sin(a)))
        o.append(blob([(cx + (p[0] - cx) * 1.12, cy + (p[1] - cy) * 1.12) for p in pts], "#fbf6ea"))
        o.append(dashed(pts, 6.5 * min(1.0, kk / k + .2), 22 * kk, 13 * kk, seed))
        # вихры
        for j, (x0, h) in enumerate(((-40, 60), (0, 75), (38, 55))):
            o.append(blob([(cx + (x0 - 6) * kk, cy - 100 * kk), (cx + (x0 + 8) * kk, cy - (112 + h) * kk), (cx + (x0 + 34) * kk, cy - 100 * kk)], "#fbf6ea"))
            o.append(dashed([(cx + x0 * kk, cy - 105 * kk), (cx + (x0 + 8) * kk, cy - (105 + h) * kk), (cx + (x0 + 26) * kk, cy - 112 * kk)], 5.0,
                            14 * kk, 9 * kk, seed + 40 + 7 * j))
        # морщины
        for j, (yy, ww) in enumerate(((-60, 60), (40, 70), (75, 50))):
            o.append(dashed([(cx - ww * kk, cy + yy * kk), (cx - ww * .3 * kk, cy + (yy + 8) * kk), (cx + ww * .3 * kk, cy + (yy - 6) * kk),
                             (cx + ww * kk, cy + (yy + 4) * kk)], 4.0, 12 * kk, 9 * kk, seed + 60 + 9 * j))
        for ex in (-34, 34):
            o.append(f'<circle cx="{cx + ex * kk:.1f}" cy="{cy - 12 * kk:.1f}" r="{7 * kk:.1f}" fill="{INK}"/>')
        # пузырьки-мыслинки к голове Димы
        return "".join(o)
    # лопается: 22 штриха разлетаются, укорачиваясь
    for i in range(22):
        a = 2 * math.pi * i / 22 + .2
        r0 = (120 + 220 * ease_out(burst, 2)) * k
        L = 34 * k * (1 - burst)
        if L < 1:
            continue
        p0 = (cx + r0 * math.cos(a) * .9, cy + r0 * math.sin(a))
        p1 = (cx + (r0 + L) * math.cos(a) * .9, cy + (r0 + L) * math.sin(a))
        o.append(line([p0, p1], 7 * (1 - .5 * burst), INK, seed=seed + 200 + i, taper=.4, wmin=.3))
    return "".join(o)


def s06(t):
    lib.dyn_begin()
    s = SC6
    hx, hy = R.K_DIMA
    br = math.sin(2 * math.pi * (t - 9.4) / 2.1)
    kmug = 1.15
    tbl = R.K_TABLE[2] - 40
    HO = 46 * s * 1.15
    # фазы руки с кружкой: 0 — держит у груди, отпивает, ставит, отпускает, щупает щёку, опускает
    sip = smooth(9.5, 9.82, t) * (1 - smooth(10.12, 10.42, t))
    put = smooth(10.18, 10.5, t)
    rel = smooth(T6_SUSHIT - .06, T6_SUSHIT + .14, t) * (1 - smooth(12.2, 12.6, t))
    ha = -.13 * sip + .02 * br + .06 * smooth(T6_POCHTI, T6_POCHTI + .3, t) * (1 - smooth(T6_SUSHIT, T6_SUSHIT + .2, t)) \
        - .05 * bump(t, T6_ORG, .35) + .05 * rel
    lean = .03 + .02 * br - .04 * sip
    # сначала фигура без рук, чтобы знать, где лицо
    ex = {}
    if t < 9.62:
        ex = dict(E["dima"]["doubt"], look=(.75, .4))
    elif t < 10.2:
        ex = dict(E["dima"]["relief"], lid=.25, look=(.6, .3))
    elif t < T6_POCHTI:
        ex = dict(E["dima"]["doubt"], look=(.5, .1))
        ex["closed"] = blink_of(t, [10.62], .16)
    elif t < T6_SUSHIT:
        ex = dict(E["dima"]["surprise"], brows="worry", look=(.55, -.85))
    elif t < T6_ORG:
        ex = dict(E["dima"]["doubt"], look=(-.2, .25), mouth="o", open=.15)
    elif t < 12.02:
        ex = dict(E["dima"]["surprise"], look=(.1, 0))
    else:
        ex = dict(E["dima"]["smug"], look=(-.15, .05))
    probe = people.figure("dima", hx, hy + 4 * br, s, ex, lean=lean, head_ang=ha, layers=("body",))
    hd = np.array(probe["head"])
    ang = lean * .5 + ha
    mouth = hd + np.array(_rot((64 * s, 92 * s), math.degrees(ang)))
    cheek = hd + np.array(_rot((-6 * s, 66 * s), math.degrees(ang)))
    # кружка: ручка слева (hs=−1), на столе / у груди / у рта
    rest_base = (hx + 300, tbl)
    rest_H = base_from_point((0, 0), (0, 0), 1, 0, 1)
    rest_H = (rest_base[0] - 88 * kmug, rest_base[1] - 70 * kmug)
    chest_H = (hx + 250, hy - 360)
    sip_rot = -38.0
    sip_H = (mouth[0] + 70 * s, mouth[1] + 50 * s)
    if t < 10.18:
        a = smooth(9.45, 9.6, t)
        H = tuple(np.array(chest_H) * (1 - sip) + np.array(sip_H) * sip)
        rot = sip_rot * ease_io(sip)
        del a
    else:
        H = tuple(np.array(chest_H) * (1 - put) + np.array(rest_H) * put)
        rot = 0.0
        if put >= 1:
            H = rest_H
    mb = base_from_point(H, MUG_HANDLE, kmug, rot, -1)
    on_table = put >= 1
    W_mug = (H[0] - HO, H[1] + 4 * s)
    # ближняя рука: держит кружку → на «сушит» к щеке, похлопывает → опускает на стол
    pat = .5 + .5 * math.sin(2 * math.pi * (t - T6_SUSHIT) * 3.2) if rel > .9 else 0.0
    W_cheek = (cheek[0] - 4 * s, cheek[1] + 118 * s + 10 * s * pat)
    W_rest = (hx + 160, tbl - 10)
    if t < T6_SUSHIT + .5:
        Wn = tuple(np.array(W_mug) * (1 - rel) + np.array(W_cheek) * rel)
    else:
        dn = smooth(12.2, 12.6, t)
        Wn = tuple(np.array(W_cheek) * (1 - dn) + np.array(W_rest) * dn) if rel < 1 or dn > 0 else W_cheek
    holding = rel < .5
    arms = {"f": ("ik", (hx + 120 * s, tbl - 20), -1), "n": ("ik", Wn, -1)}
    hands = {"f": {"dir": (1, .25), "curl": (.35, .35, .4, .45), "thumb": .35}}
    if holding:
        hands["n"] = {"kind": "none"}
    else:
        hands["n"] = {"dir": (.05, -1), "spread": .12, "curl": (.12, .12, .15, .2), "thumb": .15, "flip": 1}
    fig = people.figure("dima", hx, hy + 4 * br, s, ex, lean=lean, head_ang=ha, arms=arms, hands=hands,
                        layers=("pelvis", "arm_f", "body"))
    near = people.figure("dima", hx, hy + 4 * br, s, ex, lean=lean, head_ang=ha, arms=arms, hands=hands, layers=("arm_n",))
    Wn_real = near["wrist"]["n"]
    steam = .35 + .65 * smooth(10.4, 10.8, t)
    if holding:
        H2 = (Wn_real[0] + HO, Wn_real[1] - 4 * s) if not on_table else H
        mb = base_from_point(H2, MUG_HANDLE, kmug, rot, -1)
        back, front = people.handle_grip("dima", H2, k=s, side=-1, seed=961)
        mugsvg = back + cmug(mb[0], mb[1], kmug, rot, -1, fill=.8 - .25 * smooth(9.7, 10.1, t), steam=steam * (1 - sip), t=t, seed=3) + front
    else:
        mugsvg = cmug(mb[0], mb[1], kmug, 0, -1, fill=.55, steam=steam, t=t, seed=3)
    k_ = R.kitchen(t, "day")
    # мысль: пузырьки от головы и пунктирный изюм; лопается на «не» (11.40)
    bub_c = (hd[0] + 290 * s, hd[1] - 30 * s)
    ru = spring(t - T6_POCHTI, 2.4, 6.0) if t > T6_POCHTI else 0.0
    bu = clamp((t - T6_POP) / .28) if t > T6_POP else 0.0
    thought = raisin(bub_c[0], bub_c[1], .72, ru, bu, t)
    if T6_POCHTI < t < T6_POP + .05:
        for j, (fx, fy, r) in enumerate(((.25, .25, 10), (.45, .5, 14), (.65, .72, 18))):
            a = clamp((t - T6_POCHTI - .05 * j) / .12)
            if a > 0:
                px_ = hd[0] + 150 * s + (bub_c[0] - 120 - hd[0] - 150 * s) * fx
                py_ = hd[1] - 120 * s + (bub_c[1] - hd[1] + 120 * s) * fx
                o_ = lib.circle_d(px_, py_, r * a) if hasattr(lib, "circle_d") else None
                thought += shape(ellipse_pts(px_, py_, r * a, r * a, 12), "#f6f1e6", "", w=3.4, seed=6300 + j)
    # «порядок»: на «организм» — две искры-штриха у бровей
    spark = ""
    u = (t - T6_ORG) / .35
    if 0 < u < 1:
        for i in range(3):
            th = -1.9 + i * .4
            c = hd + np.array([40 * s, -150 * s])
            r0, r1 = 40 + 40 * u, 70 + 60 * u
            spark += line([(c[0] + math.cos(th) * r0, c[1] + math.sin(th) * r0), (c[0] + math.cos(th) * r1, c[1] + math.sin(th) * r1)], 7, INK,
                          seed=6400 + i, taper=.5, wmin=.2)
    world = [k_["bg"], fig["svg"], k_["table"]]
    if on_table:
        world.append(mugsvg)
    world.append(near["svg"])
    if not on_table:
        world.append(mugsvg)
    world += [thought, spark, k_["front"]]
    # камера: медленный дрейф вправо и наезд на лицо
    u = clamp((t - 9.45) / 3.4)
    z = 1.28 + .3 * ease_io(u) + .04 * bump(t, T6_ORG, .4)
    cx = 600 + 40 * u
    cy = 840 - 110 * ease_io(u)
    sx, sy = shake2(t, T6_POP, 7)
    set_ink(z)
    cam = lib.cam(cx - sx, cy - sy, z, .5 * math.sin((t - 9.4) * .8))
    return lib.svg(f'<rect width="1080" height="1920" fill="#efe2c6"/><g transform="{cam}">{"".join(world)}</g>')


# ═════════════════════════════ s08: диван, кофе и чай в ладонях как весы, чокается ═════════════════════════════
T8_DEN, T8_NE, T8_VAZH, T8_CHAYA = 15.82, 16.27, 16.72, 16.84
T8_CLINK = 17.02
SC8 = 1.05


def s08(t):
    lib.dyn_begin()
    s = SC8
    x, y = R.L_DIMA
    x -= 90
    br = math.sin(2 * math.pi * (t - 15.2) / 2.0)
    shrug = bump(t, T8_CHAYA - .04, .5)
    y_ = y + 3 * br - 16 * shrug
    km, kt = 1.0 * s, 1.05 * s
    # чаши-весы: кофе (ближняя рука) и чай (дальняя) поочерёдно вверх-вниз, на «не важнее» — ровно, на «чая» — сходятся и чокаются
    wv = smooth(T8_DEN - .1, T8_DEN + .1, t) * (1 - smooth(T8_NE - .05, T8_NE + .25, t))
    sway = 70 * wv * math.sin(2 * math.pi * (t - T8_DEN) * 2.1)
    level_bounce = 18 * decay(t, T8_NE + .2, 6, 2.2)
    meet = smooth(T8_CHAYA, T8_CLINK, t) * (1 - smooth(17.25, 17.55, t) * .55)
    lift = 40 * shrug
    cof = np.array([x + 270 * s, y_ - 250 * s - sway * s + level_bounce * s - lift * s])        # дно кружки кофе
    tea = np.array([x + 490 * s, y_ - 280 * s + sway * s - level_bounce * s - lift * s])        # дно чашки чая (без блюдца)
    # чокаются: края кружек сходятся до касания
    gap_x = (tea[0] - 62 * kt) - (cof[0] + 55 * km)
    cof = cof + np.array([gap_x * .5 * meet, -60 * s * meet])
    tea = tea - np.array([gap_x * .5 * meet, 60 * s * meet - 18 * s * meet])
    rot_c = 6 * meet - 4 * wv * math.sin(2 * math.pi * (t - T8_DEN) * 2.1)
    rot_t = -6 * meet
    Hc = np.array(cof) + np.array(_rot((-MUG_HANDLE[0], MUG_HANDLE[1]), rot_c)) * km
    Ht = np.array(tea) + np.array(_rot((-TEA_HANDLE[0], TEA_HANDLE[1]), rot_t)) * kt
    HO = 46 * s * 1.15
    arms = {"n": ("ik", (Hc[0] - HO, Hc[1] + 4 * s), -1), "f": ("ik", (Ht[0] - HO, Ht[1] + 4 * s), -1)}
    hands = {"n": {"kind": "none"}, "f": {"kind": "none"}}
    feet = {"n": ((x + 330 * s, R.L_FLOOR + 40), 0.0), "f": ((x + 270 * s, R.L_FLOOR + 30), 0.0)}
    if t < T8_DEN:
        ex = dict(E["dima"]["doubt"], look=(.75, .45))
    elif t < T8_NE:
        ph = math.sin(2 * math.pi * (t - T8_DEN) * 2.1)
        ex = dict(E["dima"]["focus"], look=(.7 + .2 * ph, .4 - .2 * ph))
    elif t < T8_CHAYA:
        ex = dict(E["dima"]["surprise"], look=(.6, .3))
        ex["closed"] = blink_of(t, [16.5], .15)
    elif t < T8_CLINK + .05:
        ex = dict(E["dima"]["shrug"], look=(.6, .1))
    else:
        ex = dict(E["dima"]["cheerful"], look=(.5, .1))
    ha = .03 * br + .12 * shrug - .05 * bump(t, T8_CLINK, .3)
    kw = dict(lean=-.04 - .03 * shrug, head_ang=ha, arms=arms, hands=hands, feet=feet)
    back_fig = people.figure("dima", x, y_, s, ex, layers=("legs", "pelvis", "arm_f", "body"), **kw)
    near = people.figure("dima", x, y_, s, ex, layers=("arm_n",), **kw)
    Wf, Wn = back_fig["wrist"]["f"], near["wrist"]["n"]
    # предметы по настоящим запястьям
    Ht2 = (Wf[0] + HO, Wf[1] - 4 * s)
    tb = base_from_point(Ht2, TEA_HANDLE, kt, rot_t, -1)
    bk, fr = people.handle_grip("dima", Ht2, k=s, side=-1, far=True, seed=971)
    tea_svg = bk + tcup(tb[0], tb[1], kt, rot_t, -1, steam=1.0, t=t, seed=2) + fr
    Hc2 = (Wn[0] + HO, Wn[1] - 4 * s)
    cb = base_from_point(Hc2, MUG_HANDLE, km, rot_c, -1)
    bk, fr = people.handle_grip("dima", Hc2, k=s, side=-1, seed=972)
    cof_svg = bk + cmug(cb[0], cb[1], km, rot_c, -1, fill=.8, steam=1.0, t=t, seed=4) + fr
    ring = ""
    u = (t - T8_CLINK) / .35
    if 0 < u < 1:
        ring = PR.clink((cb[0] + 55 * km + tb[0] - 62 * kt) / 2, min(cb[1] - 120 * km, tb[1] - 90 * kt) - 10, 1.3, u, seed=3)
    rb = R.living(t)
    world = [rb["bg"], back_fig["svg"], tea_svg, near["svg"], cof_svg, ring, rb["front"]]
    # камера: откат и лёгкий дрейф вверх, толчок на звоне
    u = clamp((t - 15.2) / 2.4)
    z = 1.2 - .17 * ease_out(u, 2) + .03 * bump(t, T8_CLINK, .35)
    sx, sy = shake2(t, T8_CLINK, 7)
    set_ink(z)
    cam = lib.cam(600 - sx, 1000 - 70 * u - sy, z, -.4 * math.sin((t - 15.2) * .9))
    return lib.svg(f'<rect width="1080" height="1920" fill="#e9d9bd"/><g transform="{cam}">{"".join(world)}</g>')


def frame(sid, t):
    return {"s04": s04, "s06": s06, "s08": s08}[sid](t)
