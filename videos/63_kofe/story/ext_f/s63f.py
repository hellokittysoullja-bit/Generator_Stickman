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
