"""Сцена stacks рилса 32 (s11, s12): итог опыта Стэнфорда — две стопки лампочек-идей на кремовом листе.
Слева под стопкой — значок «стул» (сидя), справа — «шагающие ноги» (на ходу). Лампочки по три в ряд.
s11 «На ходу идей выходило примерно на» (18.3–20.2): значки выскакивают, на «идей» (18.88) лампочки начинают падать
     сверху и складываться (каждая загорается, приземлившись), правая стопка растёт быстрее: 5 рядов слева, 6 справа.
s12 «шестьдесят процентов больше» (20.2–21.96): на «шестьдесят» (20.24) правая стопка выстреливает вверх ещё на два ряда
     (8 рядов: ровно в 1,6 раза выше левой), пунктир от верха левой показывает разницу, большая надпись «+60 %» бьёт
     с перелётом и звёздочкой; на «больше» (21.36) надпись пульсирует.
Высота стопки = число рядов × шаг (лампочки касаются друг друга): 8 / 5 = 1,6. Всё — от общего времени ролика t."""
import math

import lib
import scene_brain32 as b32
import study28 as st
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad,
                 mix, rad_grad, rect_pts, shape, smooth, svg)

_ST = {}
IDEI = 18.88       # «идей»
SHOT = 20.24       # «шестьдесят»
MORE = 21.36       # «больше»
BASE = 1075
XL, XR = 300, 770
BS = 0.556                   # масштаб лампочки
PITCH = 180 * BS            # высота лампочки (колба 62 + цоколь 118) — ряды касаются
DX = 66                     # три в ряд: −DX, 0, +DX
ROWS_L, ROWS_R0, ROWS_R = 5, 6, 8


def schedule():
    """[(колонка, ряд, позиция в ряду, время приземления)]."""
    out = []
    for i in range(ROWS_L * 3):
        out.append(("L", i // 3, i % 3, IDEI + 0.07 + i * 0.075))
    for i in range(ROWS_R0 * 3):
        out.append(("R", i // 3, i % 3, IDEI + 0.02 + i * 0.062))
    for i in range((ROWS_R - ROWS_R0) * 3):
        out.append(("R", ROWS_R0 + i // 3, i % 3, SHOT + 0.03 + i * 0.032))
    return out


SCHED = schedule()


def bulb_pos(col, row, side):
    x = (XL if col == "L" else XR) + (side - 1) * DX + (4 if row % 2 else -4)
    y = BASE - row * PITCH - 118 * BS
    tilt = (5 if (row + side) % 2 else -5) if side != 1 else 2 * (1 if row % 2 else -1)
    return x, y, tilt


def falling(col, row, side, tl, t, sd):
    x, y, tilt = bulb_pos(col, row, side)
    shot = tl >= SHOT
    if not shot:
        dur = 0.36
        e = t - (tl - dur)
        if e < 0:
            return ""
        if t < tl:
            u = e / dur
            yy = -260 + (y + 260) * u * u           # свободное падение
            rot = tilt + 40 * (1 - u) * (side - 1 if side != 1 else 0.5)
            sq = 1 + 0.12 * u
            on = 0.0
        else:
            el = t - tl
            yy = y
            rot = tilt
            sq = 1 - 0.18 * math.exp(-el * 14) * math.cos(el * 30)
            on = smooth(0, 0.08, el)
    else:            # выстрел: лампочка вылетает из-под верха стопки вверх с перелётом
        e = t - tl
        if e < 0:
            return ""
        k = back_out(clamp(e / 0.22), 2.2)
        top0 = BASE - ROWS_R0 * PITCH - 118 * BS + PITCH
        yy = top0 + (y - top0) * k
        rot = tilt * k
        sq = 1 + 0.15 * math.exp(-e * 10)
        on = smooth(0.05, 0.15, e)
    pv = yy + 118 * BS
    g = b32.bulb(x, yy, on, BS, sd, t, run=False)
    g = f'<g transform="translate({f(x)} {f(pv)}) rotate({f(rot)}) scale({f(1 / sq ** .5)} {f(sq)}) translate({f(-x)} {f(-pv)})">{g}</g>'
    return g


def icon_chair(t, sd):
    w = 3 * math.sin(t * 2.4)
    s = shape(rect_pts(-34, -48, -20, 44), "#8a5f3c", "", w=3, seed=sd)
    s += shape(rect_pts(-36, -4, 30, 10, 4), "#a8723f", "", w=3, seed=sd + 1)
    s += shape(rect_pts(20, 8, 30, 44), "#8a5f3c", "", w=2.6, seed=sd + 2)
    s += shape(rect_pts(-40, -56, -14, -20, 6), "#c98f5a", "", w=3, seed=sd + 3)
    return f'<g transform="rotate({f(w)} 0 40)">{s}</g>'


def icon_legs(t, sd):
    """Шагающие ноги сбоку: брюки и кеды, шагают по кругу."""
    ph = t * 7
    s = ""
    for k, sgn in enumerate((1, -1)):
        a = 26 * math.sin(ph) * sgn
        kn = 18 * max(0, math.sin(ph + (0 if sgn > 0 else math.pi)))
        hip = (0, -40)
        r = math.radians(a)
        knee = (hip[0] + 42 * math.sin(r), hip[1] + 42 * math.cos(r))
        r2 = math.radians(a - kn)
        foot = (knee[0] + 40 * math.sin(r2), knee[1] + 40 * math.cos(r2))
        col = "#1f2b52" if k == 0 else "#2d3d72"
        s += line([hip, knee, foot], 16, col, taper=.05, wmin=.9, seed=sd + k)
        s += shape([(foot[0] - 10, foot[1] - 6, 1), (foot[0] + 18, foot[1] - 6), (foot[0] + 22, foot[1] + 6, 1), (foot[0] - 12, foot[1] + 6, 1)],
                   "#f6f3ec", blob([(foot[0] - 12, foot[1] + 2), (foot[0] + 22, foot[1] + 2), (foot[0] + 22, foot[1] + 6), (foot[0] - 12, foot[1] + 6)],
                                   "#ff8a3d"), w=2.6, seed=sd + 5 + k)
    s += shape(rect_pts(-14, -54, 14, -34, 6), "#1f2b52", "", w=2.6, seed=sd + 9)
    return f'<g transform="translate(0 4)">{s}</g>'


def badge(x, y, kind, t, sd, k):
    if k <= 0.01:
        return ""
    bob = 4 * math.sin(t * 2.2 + (kind == "legs"))
    ic = icon_chair(t, sd) if kind == "chair" else icon_legs(t, sd)
    s = shape(ellipse_pts(x, y + bob, 66, 66, 28), "#fbf8ee", blob(ellipse_pts(x + 10, y + bob + 12, 58, 56, 20), "#ece4d0", .8), w=4.4, seed=sd + 50)
    s += f'<g transform="translate({f(x)} {f(y + bob)})">{ic}</g>'
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(k)}) translate({f(-x)} {f(-y)})">{s}</g>'


def big_text(t):
    """«+60 %» кодом: удар с перелётом и тряской на «шестьдесят», пульс на «больше»."""
    e = t - SHOT - 0.08
    if e < 0:
        return ""
    k = back_out(clamp(e / 0.24), 2.8)
    sc = 1.55 - 0.55 * k if e < 0.24 else 1.0
    sc *= 1 + 0.03 * math.sin(e * 3)
    em = t - MORE
    if em > 0:
        sc *= 1 + 0.16 * math.exp(-em * 5) * math.sin(min(em * 12, math.pi))
    sx = 6 * math.exp(-e * 12) * math.sin(e * 60)
    x, y = 540 + sx, 170
    txt = "+60 %"
    rot = -6 + 2 * math.sin(e * 2)
    s = (f'<text x="7" y="9" text-anchor="middle" font-family="IDB" font-weight="900" font-size="172" fill="{INK}">{txt}</text>'
         f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="172" fill="#3cbf63" stroke="{INK}" '
         f'stroke-width="10" paint-order="stroke" stroke-linejoin="round">{txt}</text>')
    return f'<g transform="translate({f(x)} {f(y + 64)}) rotate({f(rot)}) scale({f(sc)})">{s}</g>'


def star_fx(t):
    e = t - SHOT - 0.16
    if e < 0:
        return ""
    x, y = 950, 150
    sc = back_out(clamp(e / 0.3), 2.6) * (1 + 0.05 * math.sin(e * 5))
    em = t - MORE
    spin = 0.0
    if em > 0:
        sc *= 1 + 0.2 * math.exp(-em * 5) * math.sin(min(em * 12, math.pi))
        spin = 72 * ease_out(clamp(em / 0.4))
    s = [st.star(x, y + 4 * math.sin(e * 3), sc * 1.25, 12 * math.sin(e * 2.5) + (1 - clamp(e / .3)) * -80 + spin, 5230)]
    for t0 in (SHOT + 0.16, MORE):
        ee = t - t0
        if 0 <= ee < 0.5:
            for k in range(8):
                a = k * math.pi / 4 + .2
                r0 = 80 + 110 * ease_out(ee / .5)
                L = 36 * (1 - ee / .5)
                s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))], 8, "#ffcf3a",
                              taper=.5, seed=5240 + k))
    # искорки вокруг надписи
    if e > 0.3:
        for k in range(4):
            ph = (e * 0.9 + k / 4) % 1
            sx, sy = 600 + (k - 1.5) * 190, 40 + (k % 2) * 230 - 20 * ph
            r = 14 * math.sin(math.pi * ph)
            s.append(blob([(sx, sy - r), (sx + r * .3, sy - r * .3), (sx + r, sy), (sx + r * .3, sy + r * .3), (sx, sy + r), (sx - r * .3, sy + r * .3),
                           (sx - r, sy), (sx - r * .3, sy - r * .3)], "#ffcf3a"))
    return "".join(s)


def guide(t):
    """Пунктир от верха левой стопки к правой и скобка разницы (после выстрела)."""
    k = smooth(SHOT + 0.25, SHOT + 0.55, t)
    if k <= 0.01:
        return ""
    y = BASE - ROWS_L * PITCH
    x0, x1 = XL + 110, XL + 110 + (XR + 120 - XL - 110) * k
    s = []
    n = int((x1 - x0) / 30)
    for i in range(n):
        a = x0 + i * 30
        s.append(line([(a, y), (a + 18, y)], 5, "#2f6db5", taper=.1, wmin=.8, seed=5300 + i))
    if k > 0.95:
        y1 = BASE - ROWS_R * PITCH
        kk = smooth(SHOT + 0.55, SHOT + 0.75, t)
        xb = XR + 124
        yb = y + (y1 - y) * kk
        s.append(line([(xb, y), (xb + 16, y), (xb + 16, yb), (xb, yb)], 5, "#2f6db5", taper=.05, wmin=.9, seed=5340))
    return "".join(s)


def scene(t):
    s = [_ST["bg"]]
    if t < 18.4:      # база чертится слева направо с первого кадра
        s.append(line([(60, BASE), (60 + 960 * max(0.03, ease_out(clamp((t - 18.08) / 0.32))), BASE)], 7, INK, taper=.05, wmin=.9, seed=5401))
    else:
        s.append(_ST["base"])
    # стопки (лампочки, что уже упали, — сзади летящих)
    stack_sq = 1.0
    e = t - SHOT
    if e > 0:
        stack_sq = 1 + 0.05 * math.exp(-e * 7) * math.sin(e * 25)
    L, R = [], []
    for j, (col, row, side, tl) in enumerate(SCHED):
        b = falling(col, row, side, tl, t, 5500 + j * 30)
        (L if col == "L" else R).append(b)
    s.append("".join(L))
    s.append(f'<g transform="translate(0 {BASE}) scale(1 {f(stack_sq)}) translate(0 {-BASE})">{"".join(R)}</g>')
    s.append(guide(t))
    for i, (x, kind) in enumerate(((XL, "chair"), (XR, "legs"))):
        k = back_out(clamp((t - 18.06 - i * 0.1) / 0.26), 2.2)
        s.append(badge(x, BASE + 84, kind, t, 5600 + i * 60, k))
    # выстрел: штрихи скорости вверх из правой стопки
    if 0 <= e < 0.35:
        u = e / 0.35
        for k in range(5):
            xx = XR - 100 + k * 50
            y0 = BASE - ROWS_R0 * PITCH - 40 * u
            s.append(line([(xx, y0 + 90 * (1 - u)), (xx, y0 - 40)], 8 * (1 - u) + 2, "#ffcf3a", taper=.6, seed=5700 + k))
    s.append(big_text(t))
    s.append(star_fx(t))
    u = clamp((t - 18.1) / 4.06)
    sc = 1.0 + 0.05 * (0.4 * u + 0.6 * ease_io(u))
    cx, cy = 540 + 8 * u, 910 - 6 * u
    if e > 0:
        sc *= 1 + 0.045 * math.exp(-e * 6) * math.sin(min(e * 14, math.pi))
        cy += 10 * math.exp(-e * 9) * math.sin(e * 50)
    em = t - MORE
    if em > 0:
        sc *= 1 + 0.02 * math.exp(-em * 6) * math.sin(min(em * 14, math.pi))
    return "".join(s), cam(cx, cy, sc, 0.4 - 0.7 * u)


def build_static():
    if _ST:
        return
    s = []
    lin_grad([(0, "#f6eedb", 1), (1, "#ead9b8", 1)], 0, 0, 0, 1, gid="gChart32")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#gChart32)"/>')
    for k in range(-6, 30):
        s.append(f'<rect x="-900" y="{-400 + k * 80}" width="{W + 1800}" height="2" fill="#d9c7a2" opacity=".6"/>')
    _ST["bg"] = "".join(s)
    _ST["base"] = line([(60, BASE), (1020, BASE)], 7, INK, taper=.05, wmin=.9, seed=5401)
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = scene(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#f0e4c8"/><g transform="{cm}">{art}</g>')
