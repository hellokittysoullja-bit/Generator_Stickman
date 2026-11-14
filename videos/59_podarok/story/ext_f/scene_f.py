"""Рилс 59 «подарок», группа F: s12 (мама крупно), s13 (кот крадёт кусок), s15 (объятие). frame(sid, t) -> SVG 1080×1920, t — общее время ролика."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bits as B  # noqa: E402
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rrect, shape, spring  # noqa: E402,F401

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def mixv(a, b, u):
    return a + (b - a) * u


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def open_hand(c=.2, d=(1, 0), spread=.2, thumb=.2, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(c, c, c, c * .9), spread=spread, thumb=thumb, bend=.1, k=k)


NONE = dict(kind="none")


def fig(who, hip, bs, lean, arms, hands, expr, feet=None, head_ang=0.0, flip=False, torso_k=1.0, head_off=(0, 0), head_k=1.0):
    """Человек; flip — смотрит влево (цели рук задаются в мире, отражение внутри). Возвращает слои (строки в мире) и запястья в мире."""
    hx = hip[0]
    M = (lambda p: (2 * hx - p[0], p[1])) if flip else (lambda p: p)
    arms2 = {}
    for s_, a in arms.items():
        arms2[s_] = (a[0], M(a[1])) + tuple(a[2:]) if a[0] == "ik" else a
    feet2 = None
    if feet:
        feet2 = {s_: (M(v[0]), v[1]) for s_, v in feet.items()}
    pose = dict(hip=tuple(hip), scale=bs, lean=lean, torso_k=torso_k, feet=feet2, arms=arms2, hands=hands, expr=expr, head_ang=head_ang,
                head_off=head_off, head_k=head_k, hood=0.0, strings=(0, 0))
    d = people.draw(pose, who)
    wrap = (lambda s: f'<g transform="translate({2 * hx:.2f} 0) scale(-1 1)">{s}</g>') if flip else (lambda s: s)
    d2 = {k: wrap(v) for k, v in d.items() if isinstance(v, str)}
    d2["wrist"] = {k: M(v) for k, v in d["wrist"].items()}
    d2["elbow"] = {k: M(v) for k, v in d["elbow"].items()}
    d2["head"] = M(d["head"])
    return d2


def hold(wx, wy, R, side, k, who, h=None, seed=0, flip=False):
    """Пальцы вокруг предмета: (wx, wy) — центр хвата; возвращает (задняя часть, передняя)."""
    people.C = people.PAL[who]
    kw = people.hand_kw()
    kw.pop("nail", None)
    return Hand.grip((wx, wy), R, side, k=k, seed=seed, h=h, **kw)


def spark_ring(t, cx, cy, t0, n=7, rad=300, k=1.3):
    o = ""
    for i in range(n):
        ang = i / n * 2 * math.pi + .5
        dly = (i % 3) * .07
        u = (t - t0 - dly) / .7
        if 0 < u < 1:
            r = rad * (.7 + .5 * u)
            o += B.spark(cx + r * math.cos(ang), cy + r * math.sin(ang) * .85, k, u)
    return o


# ═══════════════════════════════ s12: мама крупно ═══════════════════════════════
def frame12(t):
    T_MAMA, T_PLAK, T_SCH = wt(WORDS_IDX["Мама"]), wt(WORDS_IDX["плакала"]), wt(WORDS_IDX["счастья"])
    z = 1.22 + .2 * ease_io(clamp((t - 22.32) / 2.1))
    set_ink(1.2 * z)
    cx, cy = 590 - 40 * ease_io(clamp((t - 22.3) / 2.2)) + 14 * math.sin(t * 1.3), 930 - 20 * ease_io(clamp((t - 22.3) / 2.2))
    scn = [B.kitchen(t, glow=0)]
    # стол-столешница позади Димы справа, на нём пирог
    scn.append(B.table(560, 1500, 1030, 110, legs=False))
    scn.append(B.pie(1000, 1060, .5, cut=None, sag=1.0))
    # ── Дима на заднем плане (смотрит влево, держит букет, потом руки у груди)
    bsd = .5
    dhip = (830, 1090)
    give = clamp((t - (T_MAMA - .35)) / .3)
    G0 = (690, 905)
    rel = ease_io(clamp((t - T_MAMA) / .5))
    dar = (G0[0] + 120 * rel, G0[1] + 50 * rel)
    dima_arms = {"n": ("ik", (G0[0] + 12 + 80 * rel, G0[1] + 20 + 220 * rel), -1), "f": ("ik", (dhip[0] - 40, dhip[1] + 100), -1)}
    dexp = dict(lid=.95, look=(-.5, .1), closed=blink_of(t, (22.9, 23.7)), brows="up", mouth="smile", smile=.6 + .4 * ease_io(clamp((t - T_SCH) / .3)), blush=.5)
    dhands = {"n": NONE if rel < .6 else open_hand(.3, (-1, .6), .1, .3, flip=-1, k=bsd * 1.6), "f": open_hand(.3, (-1, .3), .1, .3, flip=-1, k=bsd * 1.6)}
    dd = fig("dima", dhip, bsd, -.03, dima_arms, dhands, dexp, feet=None, head_ang=-.04 + .03 * math.sin(t * 2), flip=True)
    scn.append(dd["arm_f"] + dd["body"])
    # ── мама
    bs = 1.05
    hip = (370 + 4 * math.sin(t * 1.9), 1335)
    pre = clamp((t - (T_MAMA - .12)) / .22)
    grab = ease_io(clamp((t - T_MAMA) / .32))
    chest = ease_io(clamp((t - T_MAMA - .25) / .55))
    # точка хвата букета: до передачи у Димы, потом едет к груди мамы
    Gx = mixv(mixv(G0[0], 770, 0), 655, chest) if False else G0[0] + (655 - G0[0]) * chest
    Gy = G0[1] + (1160 - G0[1]) * chest - 70 * bump(t, T_MAMA + .1, .5)
    if t < T_MAMA:
        marm = ("ik", (hip[0] + 170 * bs, hip[1] - 150 * bs + 60 * pre), -1)
    else:
        marm = ("ik", (Gx + 30, Gy + 14), -1)
    sob = .6 * ease_io(clamp((t - T_PLAK + .1) / .5)) * (1 - ease_io(clamp((t - T_SCH) / .25)))
    tw = ease_io(clamp((t - T_PLAK + .05) / .45))
    joy = ease_io(clamp((t - T_SCH + .02) / .28))
    lift = ease_io(clamp((t - T_MAMA) / .2))
    mexp = dict(lid=1.0 - .1 * joy, look=(.55, .35 - .5 * chest), closed=blink_of(t, (22.75, 23.4)), laugh=.0 + .9 * joy, tears=.0 * tw, tw=tw, tph=t,
                brows="up" if (t < T_PLAK or joy > .5) else "worry", mouth="talk" if joy < .3 else "grin", open=(.15 + .35 * sob + 0.5 * joy) if t >= T_MAMA else .55 * (1 - lift) + .15, smile=.2 + .8 * joy,
                blush=1.0)
    ma = {"n": marm, "f": ("ik", (hip[0] + 30 * bs, hip[1] + 330 * bs), -1)}
    mh = {"n": NONE, "f": open_hand(.5, (.4, 1), .1, .5, k=bs)}
    ha = -.07 * (1 - joy) + .12 * joy + .03 * math.sin(t * 9) * sob
    dm = fig("mama", hip, bs, .04, ma, mh, mexp, feet=None, head_ang=ha, head_k=1.4)
    scn.append(dm["arm_f"] + dm["body"])
    # букет: в руке Димы → в руке мамы
    people.C = people.PAL["mama"]
    wx, wy = dm["wrist"]["n"]
    bk_rot = -8 + 10 * chest + 2 * math.sin(t * 2.2)
    if t < T_MAMA + .05:
        gk = bsd * 1.5
        bkx, bky = G0
        bk = B.bouquet(bkx, bky, .5, -22 + 6 * math.sin(t * 3))
        bk_pos = (bkx, bky)
        scn.append(bk)
        bg, fg = hold(bkx, bky, 24, -1, bsd * 1.3, "dima", seed=950)
    else:
        bk_pos = (Gx, Gy)
        sc = .5 + .55 * chest
        scn.append(f'<g>{B.bouquet(Gx, Gy, sc, bk_rot, sway=math.sin(t * 5) * .3)}</g>')
    scn.append(dm["arm_n"])
    if t >= T_MAMA + .05:
        bg, fg = hold(Gx - 6, Gy, 30, 1, 1.25, "mama", seed=960)
        scn.append(bg + fg)
    scn.append(B.counter_front(-400, 1500, 1395))
    scn.append(spark_ring(t, 470, 760, T_SCH - .05, 8, 360, 1.5))
    cam = lib.cam(cx, cy, z, 1.1 * math.sin(t * 1.1) + 1.4 * bump(t, T_PLAK, .4))
    return f'<g transform="{cam}">{"".join(scn)}</g>'


# ═══════════════════════════════ s13: кот крадёт кусок ═══════════════════════════════
CK = .75
T_LAND, T_BITE, T_RUN = 24.64, 24.72, 25.10
PIE = (560, 1050)
TABLE_Y = 1108


def cat_state(t):
    """x, y (низ кота), поворот, масштаб X/Y, голова вниз, поворот морды, взгляд, уши торчком, есть ли кусок во рту."""
    x, y, rot, sx, sy = 610.0, TABLE_Y, 0.0, 1.0, 1.0
    drop, turn, look, perk, has = 0.0, 0.0, (0.0, 0.2), 0.0, False
    if t < 24.40:
        return None
    if t < T_LAND:                           # прыжок снизу слева на стол
        u = (t - 24.40) / (T_LAND - 24.40)
        x = 450 + 160 * ease_out(u, 1.5)
        y = 1560 + (TABLE_Y - 1560) * u - 330 * math.sin(math.pi * u) ** 1.0
        sy, sx = 1.14 - .1 * u, .93 + .06 * u
        rot = -10 * (1 - u)
        look = (.3, .5 - u)
        perk = 1.0
    else:
        q = spring(t - T_LAND, 4.2, 9)       # посадка: сжатие и отпружинил
        sy = 1 - .22 * (1 - q) * math.exp(-(t - T_LAND) * 3)
        sx = 1 + .12 * (1 - q) * math.exp(-(t - T_LAND) * 3)
        sy = 1 - .16 * math.exp(-(t - T_LAND) * 9) * math.cos((t - T_LAND) * 28) if t < T_LAND + .3 else 1.0
        sx = 2 - sy if t < T_LAND + .3 else 1.0
        look = (.2, .8)
        drop = ease_io(clamp((t - T_BITE) / .2)) * (1 - ease_io(clamp((t - T_BITE - .26) / .22)))
        turn = .4
        has = t > T_BITE + .22
        if t > T_BITE + .46:                 # вскинул голову: взгляд на маму, глаза «я ничего»
            turn = -.8 * ease_io(clamp((t - T_BITE - .46) / .12))
            look = (-1.0, -.1)
            perk = 1.0
        if t >= T_RUN:
            u = clamp((t - T_RUN) / .9)
            x = 610 + 1700 * ease_in(u, 1.7)
            hop = abs(math.sin(math.pi * (u * 3.2 + .1)))
            y = TABLE_Y - 150 * hop * (1 if x < 2150 else 0) + (max(0, x - 2150) * 1.4)
            rot = 12 + 6 * math.sin(t * 25)
            turn, look = .9, (1.0, 0.0)
            sy, sx = 1 + .12 * (hop > .5), 1 - .08 * (hop > .5)
            drop = 0.0
    return dict(x=x, y=y, rot=rot, sx=sx, sy=sy, drop=drop, turn=turn, look=look, perk=perk, has=has)


def mouth_world(c):
    return (c["x"] + 22 * c["turn"] * CK, c["y"] + (1128 - Cat.CBOT + 70 * c["drop"]) * CK * c["sy"])


def cat_draw(t, c):
    st = dict(look=c["look"], turn=c["turn"], blink=blink_of(t, (24.95, 25.5)), ear=3 * math.sin(t * 20) * (t > T_RUN), perk=c["perk"], tail=18 * math.sin(t * 9) + (30 if t >= T_RUN else 0),
              tilt=-6 * c["turn"], drop=c["drop"], flame_e=1.3, smile=0)
    o = Cat.draw(0, 0, 1.0, st, t)       # в локальных единицах 0,0 = (CX, CBOT)
    extra = ""
    if c["has"]:
        extra += B.piece(836 + 22 * c["turn"] + 4, 1136 + 70 * c["drop"], .5, 14, 1)
    if t > T_BITE + .22:
        extra += B.crumbs(836 + 22 * c["turn"], 1146 + 70 * c["drop"], 6, 40, 1.1, seed=3)
    # звёздочки удивления над кабаном: штрихи, без букв
    if T_BITE + .46 < t < T_BITE + .9:
        u = (t - T_BITE - .46) / .44
        for i, a in enumerate((-60, -30, 0, 30, 60)):
            r0, r1 = 90 + 40 * u, 150 + 70 * u
            ca, sa = math.sin(math.radians(a)), -math.cos(math.radians(a))
            extra += line([(836 + 24 * c["turn"] + r0 * ca, 960 + r0 * sa * .6), (836 + 24 * c["turn"] + r1 * ca, 960 + r1 * sa * .6)], 7, "#e2574c", taper=.5, wmin=.3, seed=900 + i, op=1 - u * .6)
    inner = f'{o}<g transform="translate({-Cat.CX} {-Cat.CBOT})">{extra}</g>'
    return (f'<g transform="translate({c["x"]:.1f} {c["y"]:.1f}) rotate({c["rot"]:.2f}) scale({CK * c["sx"]:.4f} {CK * c["sy"]:.4f})">{inner}</g>')


def crumb_field(t, seed=5):
    rs = np.random.RandomState(seed)
    o = ""
    for i in range(16):
        te = rs.uniform(T_BITE + .2, 25.85)
        if t < te:
            continue
        c = cat_state(te)
        mx, my = mouth_world(c)
        vx, vy = rs.uniform(-60, 60), rs.uniform(-120, -20)
        dt = t - te
        x, y = mx + vx * dt, my + vy * dt + 900 * dt * dt
        gy = rs.uniform(TABLE_Y - 40, TABLE_Y + 10)
        if y > gy:
            x, y = mx + vx * math.sqrt(max(0, 2 * (gy - my) / 900)) * .6 + vx * .2, gy
        r = rs.uniform(3.5, 6.5)
        o += blob(ellipse_pts(x, y, r, r * .8, 6, rot=i * 30), B.CRUST if i % 3 else B.FILL)
    return o


def frame13(t):
    c = cat_state(t)
    catx = c["x"] if c else 610
    cx = 540 + clamp((catx - 610) * .62, 0, 1100) * ease_io(clamp((t - T_RUN + .12) / .5)) if t >= T_RUN else 540
    cx = 540 + 12 * math.sin(t * 1.2) + (cx - 540)
    z = 1.4 + .06 * ease_io(clamp((t - 24.1) / 1.2))
    set_ink(z)
    scn = [B.kitchen(t, -500, 2600)]
    # зрители за столом
    bs = .7
    mh, dh = (250, 1020), (830, 1020)
    seen = (t >= 24.40)
    cat_x = c["x"] if c else 600
    gasp = ease_io(clamp((t - T_BITE - .3) / .2)) if seen else 0.0
    mexp = dict(lid=1.0, look=(.7, .2 + .3 * gasp), closed=blink_of(t, (24.6, 25.6)) + .0, brows="up", mouth="talk" if gasp < .4 else "laugh", open=.35 + .6 * gasp, smile=.9, blush=.9,
                laugh=0.0 if gasp < .6 else .9 * (t > T_RUN))
    mama = fig("mama", mh, bs, .02, {"n": ("ik", (mh[0] + 130 * bs, mh[1] - 340 * bs * (1 + .15 * gasp)), -1), "f": ("ik", (mh[0] + 20, mh[1] + 140), -1)}, {"n": open_hand(.4, (.3, -1), .1, .5, k=bs * 1.0), "f": NONE}, mexp, head_ang=.04 * math.sin(t * 3) + .08 * gasp)
    dexp = dict(lid=1.0, look=(-.5, .2), closed=blink_of(t, (24.8,)), brows="up", mouth="talk", open=.2 + .7 * gasp, smile=.6, blush=.6, flush=.0)
    dima = fig("dima", dh, bs, -.02, {"n": ("ik", (dh[0] - 130 * bs, dh[1] - 340 * bs * (1 + .1 * gasp)), -1), "f": ("ik", (dh[0], dh[1] + 140), -1)}, {"n": open_hand(.5, (-.3, -1), .1, .4, flip=-1, k=bs * 1.0), "f": NONE}, dexp, head_ang=-.03 - .06 * gasp, flip=True)
    scn.append(mama["arm_f"] + mama["body"] + mama["arm_n"])
    scn.append(dima["arm_f"] + dima["body"] + dima["arm_n"])
    scn.append(B.table(-400, 2500, 1010, 120, legs=False))
    # пирог: до кражи целый; потом с вырезом
    cut = (8, 54) if t > T_BITE + .18 else None
    scn.append(B.pie(PIE[0], PIE[1], .95, cut=cut, sag=1.0))
    scn.append(B.jar(380, 1080, .8, sway=.25 * math.sin(t * 2)))
    if c is not None:
        scn.append(cat_draw(t, c))
        # кусок: пока не взят — на пироге
    if c is not None and not c["has"] and T_BITE <= t <= T_BITE + .22:
        u = (t - T_BITE) / .22
        mx, my = mouth_world(c)
        scn.append(B.piece(PIE[0] + 100 + (mx - PIE[0] - 100) * u, PIE[1] + 44 + (my - PIE[1] - 44) * u, .6, 12, 1))
    if c is not None and t < T_RUN and t > T_LAND:      # пыль на посадке
        u = (t - T_LAND) / .35
        if 0 < u < 1:
            for i, s_ in enumerate((-1, 1)):
                scn.append(blob(ellipse_pts(c["x"] + s_ * (50 + 70 * u), TABLE_Y + 8, 22 * (1 - u * .5), 12 * (1 - u * .5), 8), "#f6ecd8"))
    scn.append(crumb_field(t))
    cam = lib.cam(cx, 930, z, .5 * math.sin(t * 1.5) + 1.5 * bump(t, T_RUN, .3))
    return f'<g transform="{cam}">{"".join(scn)}</g>'


WORDS_IDX = {w["word"].strip(".,!?"): i for i, w in enumerate(WORDS)}


def frame(sid, t):
    lib.dyn_begin()
    body = {"s12": frame12, "s13": frame13}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#f3e3c3"/>{body}')
