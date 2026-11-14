"""Рилс 58 группа B: s02 (1.4–2.7) крупно трясущиеся руки Димы: ручка зажата пальцами и дробно стучит по зачётке; на «руки» (1.92)
дрожь усиливается, капелька пота. Камера: наезд на руки + мелкая тряска."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import bits  # noqa: E402
import hand  # noqa: E402
import lib  # noqa: E402
import props  # noqa: E402
from lib import H, W, blob, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, rect_pts, shape, smooth, svg  # noqa: E402

SEED = 2000
T_HANDS = 1.92


def lerp(a, b, u):
    return a + (b - a) * u


def desk_bg():
    s = [f'<rect x="-600" y="-600" width="2300" height="3200" fill="{props.C_DESK}"/>']
    for i, y in enumerate(range(-500, 2700, 215)):
        s.append(line([(-600, y), (1700, y + 5)], 4, props.C_DESK_END, taper=0, wmin=1, seed=SEED + i, op=.85))
        for j in range(3):
            x = -300 + ((i * 331 + j * 677) % 1900)
            s.append(line([(x, y), (x, y + 215)], 3, props.C_DESK_END, taper=0, wmin=1, seed=SEED + 40 + i * 3 + j, op=.7))
        s.append(line([(-300 + (i * 97) % 1600, y + 70), (-100 + (i * 97) % 1600, y + 82)], 2.6, "#b98a52", taper=.5, wmin=.5, seed=SEED + 90 + i, op=.8))
    return "".join(s)


def tremor(t, amp, sd=0.0):
    """Дрожь: сумма высоких частот с неровной огибающей."""
    a = amp * (0.75 + 0.25 * math.sin(t * 7.3 + sd))
    return (a * (0.6 * math.sin(t * 52 + sd) + 0.4 * math.sin(t * 33 + 2 * sd + 1.0)),
            a * (0.6 * math.sin(t * 47 + 1.7 + sd) + 0.4 * math.sin(t * 29 + sd * .6)))


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    boost = 1 + 1.4 * smooth(T_HANDS - 0.05, T_HANDS + 0.12, t) * (1 - 0.3 * smooth(T_HANDS + .5, T_HANDS + 1.1, t))
    amp = 5.0 * boost
    s = [desk_bg()]
    bx, by = 470, 1030
    book_t = tremor(t, amp * .35, 3)
    # тень зачётки
    s.append(lib.blob(ellipse_pts(bx + 30, by + 300, 250, 62, 20), "#6b4524", .28, lib.blur(14)))
    # стук: ручка бьёт по обложке ~9 раз в секунду, на «руки» чаще
    fr = 8.5 + 3.5 * smooth(T_HANDS - .1, T_HANDS + .1, t)
    ph = (t * fr) % 1.0
    tap = max(0.0, math.sin(math.pi * min(1.0, ph / 0.62))) ** 1.4          # 0 — над обложкой, 1 — ударил
    tapd = 34 * (1 - tap)                                                   # высота над обложкой
    kick = (1 - tap) * 0 + (1.0 if ph < 0.18 else 0.0)
    book_jit = 3.0 * (1 if ph < 0.22 else 0) * boost
    s.append(f'<g transform="translate({f(book_t[0] * .6)} {f(book_t[1] * .6 + book_jit)})">{props.gradebook(bx, by, 8.0, rot=-5)}</g>')
    # левая рука придерживает зачётку слева-снизу (дрожит)
    lt = tremor(t, amp * .9, 1)
    hk, hang = 1.9, -24
    hx, hy = 150 + lt[0], 1170 + lt[1]
    wx_, wy_ = hx - 44 * hk * math.cos(math.radians(hang)) + 14, hy - 44 * hk * math.sin(math.radians(hang))
    s.append(bits.forearm((-160 + lt[0], 1440 + lt[1]), (wx_, wy_), 190, 130, SEED + 100))
    s.append(bits.hand_flat(hx, hy, hang, hk, SEED + 110))
    # правая рука с ручкой: кончик на обложке (x, y) + дрожь, ручка идёт вверх-вправо
    pt = tremor(t, amp * 1.1, 5)
    tip = (430 + pt[0], 1040 - tapd * 1.0 + pt[1] * .6)
    ang = -34 + 3.5 * math.sin(t * 52) * boost + 5 * (1 - tap)
    sc = 1.7
    wr = hand._P([(300, 40)], ang)[0]
    s.append(hand.draw(tip[0], tip[1], ang, sc, SEED + 200, 0.5, sleeve=True))
    # штрихи дрожи вокруг кисти и ручки
    vib = clamp(0.35 + 0.65 * (boost - 1) / 1.4)
    for j in range(5):
        a = math.radians(-58 - 90 + j * 26 + 12 * math.sin(t * 40 + j))
        r0 = 205 + 10 * j
        cxv, cyv = tip[0] + 300 * sc * math.cos(math.radians(ang)) * .8, tip[1] + 300 * sc * math.sin(math.radians(ang)) * .8
        x0, y0 = cxv + r0 * math.cos(a), cyv + r0 * math.sin(a)
        s.append(line([(x0, y0), (x0 + 34 * math.cos(a), y0 + 34 * math.sin(a))], 7 * vib, "#2a2d30", taper=.5, wmin=.3, seed=SEED + 300 + j, op=.55 + .4 * vib))
    # капелька пота на «руки»
    e = t - T_HANDS
    if e > 0:
        u = clamp(e / 0.9)
        s.append(bits.sweat(820 + 20 * u, 760 + 360 * u * u + 10, 1.5 * (1 - .2 * u), rot=10))
    # камера
    u = clamp((t - 1.2) / 1.7)
    sc_c = lerp(1.0, 1.22, ease_io(u))
    cx_, cy_ = lerp(540, 600, u), lerp(1060, 1020, u)
    sh = tremor(t, 6.0 * boost, 9)
    rot = 0.5 * math.sin(t * 38) * boost
    return svg(f'<rect width="{W}" height="{H}" fill="{props.C_DESK}"/><g transform="{cam(cx_ + sh[0], cy_ + sh[1], sc_c, rot)}">{"".join(s)}</g>')
