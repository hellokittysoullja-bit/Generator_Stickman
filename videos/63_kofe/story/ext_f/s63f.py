"""Рилс 63 «кофе», группа F: s15 (кухонный пол: кот подходит к кружке кофе, нюхает, морщит нос, отворачивается),
s16 (кот крупно три четверти лакает молоко из блюдца, поднимает морду, облизывается), s17 (призыв: Дима и кот смотрят на
зрителя, пером пишется «кот»).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Дима — common/people.py, кот — common/cat.py (+ ext_f/catf.py: нюх,
морщится, поворот затылком, облизывается), предметы — common/props.py, кухня — common/room.py, «кот» — common/hand_kot.py.
Печатных букв и цифр нет; единственная надпись — рукописное «кот» (s17)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import catf  # noqa: E402
import hand_kot  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, line, shape  # noqa: E402,F401
from ink import ellipse_pts  # noqa: E402

try:
    import room as ROOM  # noqa: E402
except ImportError:          # пока группа C не положила room.py
    ROOM = None

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
EX = people.EXPR["dima"]


def wt(i):
    return WORDS[i]["start"]


T_KOT15 = wt(76)      # «кот» 30.58
T_KOFE = wt(78)       # «кофе» 31.01
T_PRI = wt(80)        # «притрагивается» 31.41
T_HVAT = wt(82)       # «хватает» 32.76
T_MOL = wt(84)        # «молока» 33.56
T_NAP = wt(85)        # «Напиши» 34.48
T_KOT = wt(86)        # «кот» 35.30 (звук «слово дописано» — 35.60)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def decay(t, t0, k=9.0, fr=20.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def shake(t, t0, amp, k=9.0, fr=19.0):
    return amp * decay(t, t0, k, fr), amp * .7 * decay(t, t0 + .013, k, fr * 1.13)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blinks(t, times, dur=.16):
    v = 0.0
    for tb in times:
        u = (t - tb) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def whip(g, t, t_in=None, t_out=None, amp=280.0, blur=30.0, dur=.2, side=1):
    """Хлёст: на входе план приезжает сбоку с размытием по x."""
    dx, b = 0.0, 0.0
    if t_in is not None:
        e = ease_out(clamp((t - t_in) / dur), 2)
        dx += side * amp * (1 - e)
        b += blur * (1 - e)
    if t_out is not None:
        e = ease_in(clamp((t - t_out) / dur), 2)
        dx -= side * amp * e
        b += blur * e
    g = f'<g transform="translate({dx:.1f} 0)">{g}</g>'
    if b > .5:
        fid = lib.uid("wb")
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{b:.1f} 0"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return g


def milk_drops(t, x, y, k, t0, seed=0):
    """Брызги молока от язычка: 2–3 сплошные белые капли вылетают дугой и падают обратно (t0 — момент шлепка)."""
    e = t - t0
    if e < 0 or e > .28:
        return ""
    o = []
    for j in range(3):
        a = -1.9 + .6 * j + .2 * math.sin(seed * 3.1 + j)
        v = (120 + 40 * j) * k
        px = x + math.cos(a) * v * e * 1.4
        py = y + math.sin(a) * v * e * 1.4 + 900 * k * e * e
        r = (5 - j) * k * (1 - e / .4)
        o.append(shape(ellipse_pts(px, py, r, r * 1.2, 8), catf.MILK, "", w=1.8, seed=900 + j))
    return "".join(o)


# ═════════════════════════════ s16: кот лакает молоко ═════════════════════════════
S16_A = 32.2
C16 = (560.0, 1400.0)            # точка между задних лап
K16 = 2.05
SAUCER16 = (520.0, 1468.0)       # центр дна блюдца (перед котом, чуть левее: три четверти)
KS16 = 1.9
LAP_F = 3.4                      # шлепков в секунду
T_UP = T_MOL - .02               # поднимает морду
T_LICK = T_MOL + .36


def s16(t):
    raise_u = sm(t, T_UP, T_UP + .32)
    ph = LAP_F * (t - S16_A)
    cyc = .5 + .5 * math.sin(2 * math.pi * ph - math.pi / 2)        # 0 — голова выше, 1 — язык в молоке
    lap_w = 1 - raise_u
    drop = (1.62 + .34 * cyc) * lap_w
    tongue = clamp((cyc - .55) / .3) * lap_w if raise_u < .3 else 0.0
    lick = clamp((t - T_LICK) / .42)
    lick2 = clamp((t - T_LICK - .5) / .4)
    lk = lick if lick < 1 else lick2
    squint = sm(t, T_LICK + .1, T_LICK + .3)
    turn = .5 - .12 * raise_u
    st = dict(turn=turn, body_turn=-.35, look=(-.3 * lap_w, .95 * lap_w + .1 * (1 - lap_w)), blink=.5 * lap_w + blinks(t, (33.2,)) * lap_w,
              ear=1.5 * math.sin(t * 2.2) + 4 * bump(t, T_HVAT, .3), tail=6 * math.sin(t * 1.6), flame_e=1.2 + .2 * math.sin(t * 6),
              drop=drop, crouch=lap_w, tongue=tongue, tilt=-3 * cyc * lap_w + 4 * raise_u - 3 * bump(t, T_LICK + .2, .5), head_dx=-26 * lap_w,
              lick=lk if 0 < lk < 1 else 0.0, squint=squint, milk=sm(t, T_UP + .2, T_UP + .35), smile=1.0 if t > T_LICK + 1.0 else 0.0)
    ripple = .6 * lap_w + .3 + .5 * bump(t, T_HVAT, .5)
    sx, sy = SAUCER16
    bg = "#f1d9b0"
    o = [f'<rect x="-400" y="-400" width="1880" height="2720" fill="{bg}"/>']
    o.append(blob(ellipse_pts(C16[0] + 30, C16[1] + 40, 360, 70, 22), "#e2c491"))                    # мягкая тень пола под котом
    set_ink(1.25)
    o.append(PR.milk_saucer(sx, sy, KS16, t, ripple, lick=tongue))
    o.append(catf.draw_f(C16[0], C16[1] - 80 * raise_u, K16, st, t))
    rim = sy - 24 * KS16
    c = lib.clip_rect(-400, rim, 1880, 900)
    o.append(f'<g clip-path="url(#{c})">{PR.milk_saucer(sx, sy, KS16, t, ripple, lick=tongue)}</g>')
    # брызги на каждом шлепке
    hx = C16[0] - 26 * K16 + 22 * catf._fx(turn) * 0 + 10
    if lap_w > .5:
        n = math.floor(ph)
        o.append(milk_drops(t, hx - 30, rim - 4, 1.4, S16_A + (n + .5) / LAP_F, seed=n))
    # камера: очень медленный наезд на морду, лёгкий дрейф
    u = sm(t, S16_A, 34.6)
    z = 1.36 + .12 * u
    cx = 600 - 10 * u
    cy = 1465 - 330 / z - 70 * raise_u
    set_ink(z * 1.25)
    return f'<g transform="{lib.cam(cx, cy, z, .8 - 1.2 * u)}">{"".join(o)}</g>', bg


FRAMES = {"s16": s16}


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body = FRAMES[sid](t)
    bg = "#d9c9a8"
    if isinstance(body, tuple):
        body, bg = body
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')


# ═════════════════════════════ s15: кухонный пол — кот и кофе ═════════════════════════════
S15_A = 29.95
MUG15 = (370.0, 1575.0)          # дно кружки на полу
KM15 = 1.9
C15_Y = 1530.0                   # лапы кота
K15 = 1.95
X_STOP = 790.0
T_STOP = T_KOT15 + .02


def cat15_x(t):
    if t < T_STOP:          # шагает справа с постоянной скоростью, у остановки тормозит
        u = clamp((t - S15_A) / (T_STOP - S15_A))
        return X_STOP + 520 * (1 - u) ** 1.35
    return X_STOP + 26 * ease_out(clamp((t - T_PRI - .05) / .25), 2) + 30 * sm(t, T_PRI + .55, T_PRI + .95)


def s15(t):
    x = cat15_x(t)
    walking = t < T_STOP + .08
    ph = 2.2 * (t - S15_A)
    lean = sm(t, T_KOFE - .3, T_KOFE + .05) * (1 - ease_out(clamp((t - T_PRI - .04) / .14), 2))   # тянется к кружке → отдёргивает
    rec = ease_out(clamp((t - T_PRI - .04) / .14), 2) * (1 - sm(t, T_PRI + .35, T_PRI + .7))       # отпрянул назад
    sniff = max(bump(t, T_KOFE, .16), bump(t, T_KOFE + .17, .16), bump(t, T_KOFE + .33, .14)) * (t < T_PRI)
    wr = sm(t, T_PRI - .02, T_PRI + .1) * (1 - sm(t, T_PRI + .9, 32.3))
    away = sm(t, T_PRI + .32, T_PRI + .78)                                                         # отворачивается: 0 → 3/4 со спины
    turn = -.35 * lean + 1.75 * away
    st = dict(turn=turn, body_turn=.55 * sm(t, T_PRI + .42, T_PRI + .9),
              look=(-.9 * (1 - away), .35 * lean - .3 * away), blink=blinks(t, (30.3,)) + .0,
              ear=2 * math.sin(t * 3.1), perk=.6 * bump(t, T_STOP, .4) + .3 * lean,
              tail=6 * math.sin(t * 2.6) + 22 * decay(t, T_PRI + .05, 6, 5.5) - 10 * sm(t, T_PRI + .5, 32.0),
              flame_e=1.1 + .2 * math.sin(t * 7) + .8 * bump(t, T_PRI + .05, .35),
              head_dx=-50 * lean + 34 * rec, drop=.85 * lean - .15 * rec, tilt=-12 * lean + 9 * rec + 6 * away, sniff=sniff, wrinkle=wr,
              rot=-5 * lean + 3 * rec, paw=sm(t, T_PRI + .55, T_PRI + .7), paw_shake=(t - T_PRI) * 7 if t > T_PRI + .6 else 0.0)
    if walking:
        st["walk"] = ph
        st["rot"] = 1.8 * math.sin(2 * math.pi * ph) * clamp((T_STOP - t) / .15)
    bob = abs(math.sin(math.pi * ph)) * 8 if walking else 0.0
    r = ROOM.kitchen_floor(t, "morning")
    o = [r["bg"]]
    set_ink(1.2)
    o.append(blob(ellipse_pts(MUG15[0] + 10, MUG15[1] + 4, 125, 20, 16), "#9c6b3e", .6))
    o.append(blob(ellipse_pts(x + 30, C15_Y + 6, 230, 34, 18), "#9c6b3e", .55))
    steam = 1.0 + .35 * bump(t, T_KOFE, .5)
    o.append(PR.coffee_mug(MUG15[0], MUG15[1], KM15, col="white", fill=.9, steam=steam, t=t, seed=15))
    o.append(catf.draw_f(x, C15_Y - bob, K15, st, t))
    o.append(r["front"])
    # камера: панорама за котом, наезд на морду к «притрагивается», тряска на отдёргивании
    u1 = sm(t, S15_A, T_STOP + .2)
    u2 = sm(t, T_KOFE - .4, T_PRI + .1)
    z = 1.02 + .3 * u2 - .06 * sm(t, T_PRI + .4, 32.6)
    hx, hy = catf.head_world(x, C15_Y, K15, st)
    cx = (880 - 220 * u1) * (1 - u2) + (hx * .72 + MUG15[0] * .28) * u2
    cy = 1240 * (1 - u2) + (hy + 60) * u2
    cx += 70 * sm(t, T_PRI + .3, 32.4)
    dx, dy = shake(t, T_PRI + .04, 10)
    set_ink(z * 1.2)
    g = f'<g transform="{lib.cam(cx + dx, cy + dy, z, -.8 + 1.4 * u1 - 1.0 * u2)}">{"".join(o)}</g>'
    return whip(g, t, t_in=S15_A, dur=.22), "#c8915c"


FRAMES["s15"] = s15


# ═════════════════════════════ s17: призыв, рукописное «кот» ═════════════════════════════
S17_A = 34.15
DS17 = 1.0
HIP17 = (ROOM.K_DIMA[0] - 40, ROOM.K_FLOOR - (people.LEG_LEN - 12) * DS17 * people.HEIGHT["dima"]) if ROOM else (430, 1000)
MUG_HC = (-89.0, -70.0)                   # центр ручки зеркальной кружки от центра дна (ед. кружки)
CAT17 = (945.0, ROOM.K_TABLE[2] - 40 if ROOM else 1060)
K17 = .9
KOT_T0, KOT_DUR = T_KOT - .02, .32        # дописано к 35.60 (звук «слово дописано»)
KOT_XY, KOT_SIZE = (842.0, 672.0), 1.3   # чистая стена между полкой/шкафами (низ 578/560) и плиткой (верх 690)


def held_mug(W, rot, t, k=1.0, seed=0):
    """Кружка кофе в ближней руке за ручку: пальцы в ручке, большой палец сверху (как в s01/s18 группы C)."""
    hc = (MUG_HC[0] * k, MUG_HC[1] * k)
    mug = f'<g transform="scale(-1 1)">{PR.coffee_mug(0, 0, k, 0, "white", .8, 0.0, t, seed=seed)}</g>'
    back, front = people.handle_grip("dima", hc, k=DS17, side=-1, seed=960 + seed)
    wl = (hc[0] - 70 * DS17, hc[1] + 6 * DS17)
    return f'<g transform="translate({W[0]:.2f} {W[1]:.2f}) rotate({rot:.3f}) translate({-wl[0]:.2f} {-wl[1]:.2f})">{back}{mug}{front}</g>'


def s17(t):
    hx0, hy0 = HIP17
    nod = .06 * bump(t, T_NAP + .05, .45) + .05 * bump(t, T_KOT + .25, .45)
    breath = math.sin(2 * math.pi * (t - S17_A) / 2.4)
    ex = dict(EX["friendly"], look=(.05, 0), closed=blinks(t, (34.9, 35.95)), open=.5 + .15 * bump(t, T_KOT + .3, .5))
    kw = people.stand_kw(hx0, hy0, DS17)
    W = (hx0 + 228 * DS17, hy0 - 285 * DS17 + 6 * breath - 18 * bump(t, T_NAP + .1, .5))
    far = ("ik", (hx0 + 200 * DS17, ROOM.K_TABLE[2] - 46), -1)
    arms = {"n": ("ik", W, -1), "f": far}
    hands = {"n": {"kind": "none"}, "f": {"dir": (1, .25), "curl": (.25, .3, .35, .4), "thumb": .3}}
    fig = people.figure("dima", hx0, hy0, DS17, ex, lean=-.02, head_ang=-nod, arms=arms, hands=hands, layers=("legs", "pelvis", "arm_f", "body"), **kw)
    arm = people.figure("dima", hx0, hy0, DS17, ex, lean=-.02, head_ang=-nod, arms=arms, hands={"n": {"kind": "none"}}, layers=("arm_n",), **kw)
    cup = held_mug(arm["wrist"]["n"], -4 + 3 * math.sin(t * 1.3), t, seed=17)
    # кот: сначала смотрит на Диму, на «Напиши» поворачивает морду к зрителю через три четверти; на «кот» ушки торчком, огонёк вспыхивает
    tu = sm(t, T_NAP - .02, T_NAP + .3)
    turn = -.85 * (1 - tu) + .06 * bump(t, T_NAP + .3, .3)
    st = dict(turn=turn, look=(-.85 * (1 - tu), -.2 * (1 - tu)), blink=blinks(t, (34.3, 35.75)), tail=7 * math.sin(t * 2.1), ear=2 * math.sin(t * 3.3),
              tilt=-5 * (1 - tu) + 2.5 * math.sin(t * 1.2) + 4 * bump(t, T_KOT + .1, .5), perk=.6 * bump(t, T_KOT, .55),
              flame_e=1.1 + .7 * bump(t, T_KOT + .1, .5), smile=1.0 if t > T_KOT + .3 else 0.0)
    r = ROOM.kitchen(t, "day", clock=PR.clock_hm(13, 5))
    o = [r["bg"], fig["svg"], r["table"], arm["svg"], cup]
    set_ink(1.2)
    o.append(blob(ellipse_pts(CAT17[0] + 6, CAT17[1] - 2, 120, 12, 14), lib.mul(ROOM.LIGHTWOOD, (.82, .82, .82))))
    o.append(catf.draw_f(CAT17[0], CAT17[1], K17, st, t))
    o.append(r["front"])
    o.append(hand_kot.kot(t, KOT_T0, KOT_DUR, KOT_XY[0], KOT_XY[1], KOT_SIZE))
    u = sm(t, S17_A + .1, 36.3)
    z = 1.14 + .12 * u + .03 * bump(t, KOT_T0 + KOT_DUR, .35)
    cx = 690 + 10 * u
    cy = 900 - 30 * u
    set_ink(z)
    g = f'<g transform="{lib.cam(cx, cy, z, .6 - .9 * u)}">{"".join(o)}</g>'
    return whip(g, t, t_in=S17_A, dur=.22), "#efe2c6"


FRAMES["s17"] = s17
