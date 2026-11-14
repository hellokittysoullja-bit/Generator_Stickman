"""Сцена «факт» рилса 42 (s07, s09): тёмно-синий фон (как fact рилса 39), всё — функция общего времени ролика t,
удары — по voice/words.json.
s07 «Знаешь, почему кажется, что тебя замечают все?» (10.1–13.3): кот-ведущий с указкой; на «почему» (10.8) из кончика
    указки выпрыгивает большой рукописный «?», на «кажется»/«замечают» рядом выскакивают маленькие «?», на «все?» (12.64)
    кот наклоняет голову к зрителю, «?» качается вместе с ним, камера толкает.
s09 «…вот и кажется, что остальные тоже» (15.0–17.3): три коллеги в ряд, каждый занят собой (пятно кофе на рубашке,
    растрёпанная чёлка, телефон), над каждым свой пузырь мыслей; на «остальные» (16.16) пузыри вспыхивают; панорама."""
import math

import numpy as np

import cat
import lib
import person
import study28 as st
from lib import (INK, W, H, back_out, band, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape,
                 smooth, svg, T, DEFS)

_ST = {}
WT = {}
FLOOR = 1290


def word_t(w, k=0):
    if not WT:
        for x in lib.words():
            WT.setdefault(x["word"].strip(",.:?!").lower(), []).append(x["start"])
    return WT[w][k]




# ───────────────────────── фон
WHY = word_t("почему")          # 10.8
KAZH = word_t("кажется")        # 11.2
ZAM = word_t("замечают")        # 12.16
ALL = word_t("все", 1)          # 12.64
OST = word_t("остальные")       # 16.16


def background():
    s = []
    lib.lin_grad([(0, "#1a2244", 1), (.55, "#26335f", 1), (1, "#2e3f74", 1)], 0, 0, 0, 1, gid="gWallF")
    lib.lin_grad([(0, "#33447a", 1), (1, "#1f2950", 1)], 0, 0, 0, 1, gid="gFloorF")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#gWallF)"/>')
    s.append(f'<rect x="-900" y="{FLOOR}" width="{W + 1800}" height="{H + 900}" fill="url(#gFloorF)"/>')
    rad_grad([(0, "#4e64a6", .75), (.6, "#3a4d8a", .28), (1, "#3a4d8a", 0)], 520, 760, 760, 700, gid="gSpotF")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#gSpotF)"/>')
    s.append(blob([(-900, FLOOR - 24), (W + 900, FLOOR - 24), (W + 900, FLOOR), (-900, FLOOR)], "#24305c"))
    s.append(line([(-900, FLOOR - 24), (W + 900, FLOOR - 24)], 2.6, INK, taper=.1, wmin=.8, seed=6, op=.8))
    s.append(line([(-900, FLOOR), (W + 900, FLOOR)], 4.5, INK, taper=.1, wmin=.8, seed=5))
    for k, y in enumerate([1380, 1520, 1720]):
        s.append(line([(-900, y), (W + 900, y + 6)], 2.4, "#1a2244", taper=.2, wmin=.6, seed=10 + k, op=.8))
    return "".join(s)


def dust(t):
    rs = np.random.RandomState(7)
    s = []
    for k in range(30):
        x0, y0 = rs.uniform(-200, W + 200), rs.uniform(-200, FLOOR - 40)
        sp, ph, r = rs.uniform(10, 26), rs.uniform(0, 6.28), rs.uniform(2.2, 4.5)
        x = x0 + 30 * math.sin(t * 0.6 + ph)
        y = (y0 - sp * (t - 10)) % (FLOOR + 160) - 180
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#c9d6ff" opacity="{.16 + .12 * math.sin(t * 2 + ph):.3f}"/>')
    return "".join(s)


def star(x, y, r, col="#ffe27a", sd=0, rot=0.0):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.32
        a = math.radians(rot + i * 45 - 90)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, col, "", w=max(1.6, r * 0.09), seed=sd)


def rays(x, y, e, sd, r=70, n=10, col="#ffe27a", dur=0.45, L0=60, w=10):
    if e < 0 or e > dur:
        return ""
    u = e / dur
    s = []
    for k in range(n):
        a = k * 2 * math.pi / n + .3
        r0 = r + 120 * ease_out(u)
        L = L0 * (1 - u)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))], w * (1 - .5 * u),
                      col, taper=.5, seed=sd + k))
    return "".join(s)


def text(x, y, txt, size, fill, font="IDB", weight=900, stroke=INK, sw=10, anchor="middle", shadow=True, extra=""):
    s = ""
    if shadow:
        s += (f'<text x="{f(x + size * .04)}" y="{f(y + size * .05)}" text-anchor="{anchor}" font-family="{font}" font-weight="{weight}" '
              f'font-size="{f(size)}" fill="{INK}">{txt}</text>')
    s += (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="{font}" font-weight="{weight}" font-size="{f(size)}" '
          f'fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}" paint-order="stroke" stroke-linejoin="round" {extra}>{txt}</text>')
    return s




def kick(t, t0, amp=1.0, k=8.0, w=24.0):
    """Затухающий толчок после t0 (0 до удара)."""
    e = t - t0
    if e <= 0:
        return 0.0
    return amp * math.exp(-e * k) * math.sin(min(e * w, math.pi) if w <= 0 else e * w)


# ───────────────────────── s07: кот-ведущий и «?»
CAT_X, CAT_Y, CAT_S = 680, FLOOR - 4, 1.75
QPOS = (330, 470)          # где встаёт большой «?»
PTR_L = 330


def paw_point(t):
    """Точка лапы (внутр. коорд. кота): машет указкой с первого кадра; на «почему» — выброс вверх (из указки вылетает
    «?»), на «все?» — стук."""
    base = np.array([724.0, 1112.0])
    calm = smooth(WHY, WHY + .3, t)
    wv = np.array([10 * math.sin(t * 7.5), 12 * math.sin(t * 7.5 + 1.2)]) * (1 - .6 * calm)
    e = t - (WHY - 0.14)
    thr = math.exp(-e * 3.2) * math.sin(min(e * 10, math.pi / 2)) if e > 0 else 0.0
    hit = t - (ALL - 0.04)
    tap = math.exp(-max(hit, 0) * 8) * (1 - abs(min(hit, 0)) / 0.1) if hit > -0.1 else 0.0
    P = base + wv + np.array([-30, -40]) * thr + np.array([-10, 22]) * tap
    return tuple(P)


def pointer_dir(t):
    a = -140 + 6 * math.sin(t * 7.5 + .4) * (1 - .6 * smooth(WHY, WHY + .3, t))
    e = t - (WHY - 0.14)
    if e > 0:
        a -= 14 * math.exp(-e * 4) * math.sin(min(e * 12, math.pi / 2))
    hit = t - (ALL - 0.04)
    if hit > -0.1:
        a += 10 * math.exp(-max(hit, 0) * 8) * (1 - abs(min(hit, 0)) / 0.1)
    return a


def pointer_tip_world(t):
    P = cat.to_world(paw_point(t), CAT_X, CAT_Y, CAT_S)
    a = math.radians(pointer_dir(t))
    return (P[0] + math.cos(a) * PTR_L, P[1] + math.sin(a) * PTR_L)


def pointer(t):
    P = cat.to_world(paw_point(t), CAT_X, CAT_Y, CAT_S)
    a = math.radians(pointer_dir(t))
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    a0 = (P[0] - ux * 40, P[1] - uy * 40)
    b = (P[0] + ux * PTR_L, P[1] + uy * PTR_L)
    w0, w1 = 10, 5.5
    poly = [(a0[0] + nx * w0, a0[1] + ny * w0, 1), (b[0] + nx * w1, b[1] + ny * w1, 1), (b[0] - nx * w1, b[1] - ny * w1, 1),
            (a0[0] - nx * w0, a0[1] - ny * w0, 1)]
    s = shape(poly, "#c98f5a", blob([(a0[0], a0[1]), (b[0], b[1]), (b[0] - nx * w1, b[1] - ny * w1), (a0[0] - nx * w0, a0[1] - ny * w0)],
                                    "#a8723f", .9), w=3.8, seed=720)
    tip = [(b[0] - ux * 30 + nx * 7.5, b[1] - uy * 30 + ny * 7.5, 1), (b[0] + ux * 6 + nx * 7.5, b[1] + uy * 6 + ny * 7.5), (b[0] + ux * 12, b[1] + uy * 12),
           (b[0] + ux * 6 - nx * 7.5, b[1] + uy * 6 - ny * 7.5), (b[0] - ux * 30 - nx * 7.5, b[1] - uy * 30 - ny * 7.5, 1)]
    s += shape(tip, "#e5383b", "", w=3.8, seed=721)
    return s


def qmark(x, y, size, rot, sc, sd, col="#ffcf3a"):
    """Рукописный «?» маркером: заливка, обводка тушью, тень."""
    if sc <= 0.01:
        return ""
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">'
            + text(0, size * .36, "?", size, col, font="Shantell", weight=800, sw=max(8, size * .055)) + "</g>")


def big_q(t):
    e = t - WHY
    if e < 0:
        return ""
    fly = 0.30
    u = clamp(e / fly)
    tip = pointer_tip_world(WHY)
    # дуга от кончика указки к месту, рост, кувырок
    x = tip[0] + (QPOS[0] - tip[0]) * ease_out(u, 2)
    y = tip[1] + (QPOS[1] - tip[1]) * ease_out(u, 2) - 160 * math.sin(math.pi * u) * (1 - u * .4)
    sc = 0.15 + 0.85 * ease_out(u, 2)
    rot = -200 * (1 - ease_out(u, 2.4)) + 8
    sq = 1.0
    if e > fly:                      # приземление: сплющило и отпружинило
        el = e - fly
        sq = 1 + 0.22 * math.exp(-el * 9) * math.cos(el * 26)
        y += 6 * math.sin((t - WHY) * 3.4)
        rot = 8 + 4 * math.sin(t * 2.6)
    ea = t - ALL                      # «все?» — качнулся вместе с котом
    if ea > 0:
        rot += 16 * (1 - math.exp(-ea * 7)) - 9 * math.exp(-ea * 5) * math.sin(ea * 20)
        sq *= 1 + 0.12 * math.exp(-ea * 7) * math.cos(ea * 24)
    body = qmark(0, 0, 420, 0, 1.0, 750)
    g = rad_grad([(0, "#ffe27a", .45), (.6, "#ffcf3a", .12), (1, "#ffcf3a", 0)], 0, 0, 240, 260)
    glow = f'<ellipse cx="0" cy="0" rx="260" ry="280" fill="url(#{g})"/>' if e > fly * .5 else ""
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc * sq)} {f(sc / max(sq, .5) ** .5)})">'
            f'{glow}{body}</g>')


def small_qs(t):
    s = []
    for k, (t0, x, y, size, r0) in enumerate([(KAZH, 640, 330, 170, -14), (ZAM, 130, 800, 150, 16)]):
        e = t - t0
        if e < 0:
            continue
        k_ = back_out(clamp(e / 0.28), 2.6)
        ea = t - ALL
        pulse = 1 + (0.25 * math.exp(-ea * 7) * math.cos(ea * 22) if ea > 0 else 0)
        yy = y + 10 * math.sin(t * 3.3 + k * 2)
        s.append(qmark(x, yy, size, r0 + 7 * math.sin(t * 2.4 + k), k_ * pulse, 760 + k, col="#ffffff" if k else "#ffe27a"))
    return "".join(s)


def cat_s07(t):
    # взгляд: на «?» (вверх-влево), на «все?» — в камеру; голова наклоняется
    k_up = smooth(WHY + .05, WHY + .25, t) * (1 - smooth(ALL - .12, ALL + .05, t))
    look = (-0.78 * k_up + 0.1 * (1 - k_up), -0.7 * k_up + 0.05)
    blink = 0.0
    for c, half in ((10.36, 0.07), (11.9, 0.08), (12.95, 0.07)):
        if c - half <= t <= c + half:
            blink = 1 - abs(t - c) / half
    ea = t - ALL
    tilt = -4 * math.sin(t * 2.4)
    if ea > -0.05:
        u = max(ea + 0.05, 0)
        tilt = tilt * math.exp(-u * 6) + 10 * (1 - math.exp(-u * 9) * math.cos(u * 14))
    flick = 0.0
    for c in (WHY, ALL):
        e = t - c
        if 0 <= e < 0.5:
            flick += -14 * math.exp(-e * 9) * math.sin(e * 34)
    tail = 6 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1) + 9 * smooth(ALL - .1, ALL + .3, t)
    bob = 7 * math.exp(-max(ea, 0) * 6) * math.sin(max(ea, 0) * 20) if ea > 0 else 0
    X, Y = CAT_X, CAT_Y + bob
    s = []
    g = rad_grad([(0, "#7f95d6", .55), (.55, "#5a70b4", .22), (1, "#5a70b4", 0)], X + 40, Y - 260, 380, 340)
    s.append(f'<rect x="{f(X - 460)}" y="{f(Y - 720)}" width="1000" height="860" fill="url(#{g})"/>')
    s.append(blob(ellipse_pts(X + 30, Y + 2, 260, 28, 16), "#141b38", .55, blur(8)))
    fx, fy = cat.flame_world(X, Y, CAT_S, tail)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g2 = rad_grad([(0, "#ffb050", .42 * fl), (1, "#ffb050", 0)], fx, fy, 280, 280)
    s.append(f'<rect x="{f(fx - 300)}" y="{f(fy - 300)}" width="600" height="600" fill="url(#{g2})" style="mix-blend-mode:screen"/>')
    s.append(cat.draw(X, Y, CAT_S, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw="none", shadow=False))
    s.append(pointer(t))
    press = 0.5 * math.exp(-max(ea, 0) * 8) if ea > 0 else 0
    s.append(f'<g transform="translate({X - cat.CX * CAT_S:.2f} {Y - cat.CBOT * CAT_S:.2f}) scale({CAT_S:.4f})">'
             f'{cat.leg_left(paw_point(t), press)}</g>')
    return "".join(s)


def sparkles(t, sd=11, n=9, box=(90, 220, 990, 1100), skip=None):
    s = []
    rs = np.random.RandomState(sd)
    for k in range(n):
        x, y = rs.uniform(box[0], box[2]), rs.uniform(box[1], box[3])
        ph = rs.uniform(0, 6.28)
        if skip and skip(x, y):
            continue
        r = 9 + 8 * (0.5 + 0.5 * math.sin(t * 4 + ph))
        s.append(star(x, y, r, "#ffe27a", 730 + k, rot=t * 40 + ph * 20))
    return "".join(s)


def s07(t):
    s = [_ST["bg"], dust(t), sparkles(t, skip=lambda x, y: x > 560 and y > 760)]
    s.append(rays(QPOS[0], QPOS[1], t - (WHY + 0.3), 760, r=200, n=12, L0=80, w=12))
    s.append(rays(QPOS[0], QPOS[1], t - ALL, 780, r=230, n=10, L0=70, w=10, col="#ffffff"))
    s.append(small_qs(t))
    s.append(cat_s07(t))
    s.append(big_q(t))
    # камера: влёт с первого кадра, толчок на «почему», удар на «все?»
    t0 = 10.1
    u = ease_out(clamp((t - t0) / 0.45), 3)
    sc = 1.0 + 0.16 * (1 - u) + 0.04 * clamp((t - 10.6) / 2.7)
    cx, cy = 540 + 30 * (1 - u), 860 + 60 * (1 - u)
    rot = -2.4 * (1 - u) + 0.5 * math.sin(t * 1.1)
    sc *= 1 + kick(t, WHY + 0.28, 0.035, 8, 14)
    e = t - ALL
    if e > 0:
        kk = math.exp(-e * 7)
        sc *= 1 + 0.06 * kk
        cx += 14 * kk * math.sin(e * 47)
        cy += 12 * kk * math.sin(e * 39)
        rot += 1.4 * kk * math.sin(e * 31)
    return cam(cx, cy, sc, rot), "".join(s)


# ───────────────────────── s09: три коллеги, каждый думает о своём
FEET = 1440
COLS = [
    dict(x=205, spec=dict(skin="#f0c4a0", hair="short", hair_c="#5a3a26", top="#9cc9ea", low="#2f3a55", face=.4, collar="#ffffff",
                          shoes="#3a2a24", stubble=True)),
    dict(x=560, spec=dict(skin="#f4d0b4", hair="bob", hair_c="#c8622a", top="#5fb07a", low="#33384a", face=-.15, messy=True,
                          shoes="#5a2a3a")),
    dict(x=915, spec=dict(skin="#a8704c", hair="curly", hair_c="#2a1a14", top="#e07a2e", low="#2a2a3a", face=-.4, glasses=True,
                          shoes="#2a2a30")),
]
BUB = [(235, 420), (560, 390), (885, 420)]       # центры пузырей (мир)


def stain(y0, sw):
    """Пятно кофе на рубашке с подтёками (координаты человека)."""
    x, y = -26, y0 + 112
    pts = []
    for i in range(16):
        a = 2 * math.pi * i / 16
        r = 34 * (1 + .22 * math.sin(3 * a + 1) + .12 * math.sin(7 * a))
        pts.append((x + r * math.cos(a) * 1.15, y + r * math.sin(a)))
    s = blob(pts, "#7a4a2a", .95)
    s += blob(ellipse_pts(x - 6, y - 6, 18, 12, 10), "#8e5a34", .9)
    s += blob(ellipse_pts(x + 40, y + 42, 9, 9, 8), "#7a4a2a", .95) + blob(ellipse_pts(x - 34, y + 30, 6, 6, 8), "#7a4a2a", .95)
    s += line([(x + 8, y + 30), (x + 10, y + 58)], 9, "#7a4a2a", taper=.6, wmin=.4, seed=1601)
    # пуговицы рубашки и планка
    s += line([(0, y0 + 30), (2, y0 + 210)], 2.4, "#6f9cc2", taper=.1, wmin=.8, seed=1602, op=.9)
    for k in range(4):
        s += f'<circle cx="{f(-6)}" cy="{f(y0 + 60 + k * 46)}" r="4.2" fill="#ffffff" stroke="{INK}" stroke-width="1.6"/>'
    return s


def bubble(cx, cy, w, h, to, content, sc, sd, flash=0.0):
    """Пузырь мыслей: облако с кочками + три кружка к голове; content — в координатах центра облака."""
    if sc <= 0.01:
        return ""
    pts = []
    n = 18
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + .07 * math.cos(n / 2 * a * 2) + .03 * math.sin(5 * a + sd)
        pts.append((w / 2 * math.cos(a) * r, h / 2 * math.sin(a) * r))
    bumps = []
    for i in range(n):
        a0 = 2 * math.pi * i / n
        for j in range(3):
            a = a0 + 2 * math.pi / n * j / 3
            bul = 1 + .09 * math.sin(math.pi * j / 3 + .5)
            bumps.append((w / 2 * math.cos(a) * bul, h / 2 * math.sin(a) * bul))
    fill = mix("#fbf6ea", "#fff3b8", flash)
    s = []
    if flash > 0.01:
        g = rad_grad([(0, "#ffe27a", .75 * flash), (.6, "#ffcf3a", .3 * flash), (1, "#ffcf3a", 0)], 0, 0, w * .85, h * .9)
        s.append(f'<ellipse cx="0" cy="0" rx="{f(w * .85)}" ry="{f(h * .9)}" fill="url(#{g})"/>')
    s.append(blob([(x + 10, y + 14) for x, y in bumps], "#0c1028", .4, blur(8)))
    s.append(shape(bumps, fill, blob([(x, y) for x, y in bumps if y > h * .05] or [(0, 0)], "#e9dfc6", .0), w=4.6, seed=sd))
    s.append(content)
    out = f'<g transform="translate({f(cx)} {f(cy)}) scale({f(sc)})">{"".join(s)}</g>'
    # кружки-хвостик к голове
    tail = []
    for k, (u, r) in enumerate([(.3, 18), (.55, 13), (.78, 9)]):
        x = cx + (to[0] - cx) * u
        y = cy + h / 2 * .7 + (to[1] - cy - h / 2 * .7) * u
        rr = r * clamp(sc * 1.4 - k * .2)
        if rr > 1:
            tail.append(shape(ellipse_pts(x, y, rr, rr, 12), fill, "", w=3.4, seed=sd + 10 + k))
    return "".join(tail) + out


def icon_shirt(t, fl):
    sp = 1 + .25 * fl
    s = shape([(-80, -64), (-34, -84), (-18, -70), (18, -70), (34, -84), (80, -64), (98, -20), (66, -8), (60, 84, 1), (-60, 84, 1), (-66, -8),
               (-98, -20)], "#9cc9ea", blob([(20, -70), (80, -64), (98, -20), (66, -8), (60, 84), (24, 84)], "#7fb0d6", .9), w=4.2, seed=1611)
    s += shape([(-18, -70), (0, -46), (18, -70), (10, -78), (-10, -78)], "#ffffff", "", w=3, seed=1612)
    pts = []
    for i in range(14):
        a = 2 * math.pi * i / 14
        r = 26 * sp * (1 + .25 * math.sin(3 * a + 1) + .1 * math.sin(6 * a))
        pts.append((8 + r * math.cos(a) * 1.1, 10 + r * math.sin(a)))
    s += shape(pts, "#7a4a2a", blob(ellipse_pts(2, 4, 12, 8, 8), "#9a643c", .9), w=2.6, seed=1613)
    s += shape(ellipse_pts(36 * sp, 40 * sp, 6, 7, 8), "#7a4a2a", "", w=2, seed=1614)
    return s


def icon_hair(t, fl):
    s = shape(ellipse_pts(0, 6, 62, 70, 18), "#f4d0b4", blob(ellipse_pts(26, 14, 40, 60, 12), "#e2b796", .8), w=4.2, seed=1621)
    s += shape([(-66, 6), (-64, -40), (-30, -72), (20, -76), (60, -50), (66, 0), (44, -30), (10, -40), (-30, -34)], "#c8622a",
               blob([(10, -76), (60, -50), (66, 0), (44, -30)], "#a24d1f", .9), w=4, seed=1622)
    for k, (bx, by, dx, dy) in enumerate([(-40, -60, -40, -46), (-8, -74, -10, -58), (22, -72, 30, -56), (50, -52, 50, -30), (-14, -40, 16, 34)]):
        wig = 1 + .25 * fl * math.sin(t * 30 + k)
        pts = [(bx, by), (bx + dx * .5 * wig + 6, by + dy * .5 * wig), (bx + dx * wig, by + dy * wig)]
        s += shape(band(pts, 18, 3, step=4), "#c8622a", "", w=3, seed=1630 + k)
    for k, x in enumerate((-22, 22)):
        s += shape(ellipse_pts(x, 14, 13, 16, 12), "#ffffff", f'<circle cx="{f(x)}" cy="{f(8)}" r="6" fill="{INK}"/>', w=3, seed=1640 + k)
    s += line([(-14, 46), (-4, 42), (6, 48), (16, 44)], 3.4, seed=1645)
    return s


def icon_phone(t, fl):
    s = st.phone_up(0, 0, 1.25, -8 + 4 * math.sin(t * 3), 1.0, 1650)
    for k in range(3):                              # уведомления-сердечки выскакивают
        e = (t * 1.3 + k / 3) % 1.0
        y = -60 - 70 * e
        r = 12 * (1 - e) + 4
        s += shape([(46 + k * 10, y + r * .6), (46 + k * 10 - r, y - r * .2), (46 + k * 10 - r * .5, y - r * .9), (46 + k * 10, y - r * .45),
                    (46 + k * 10 + r * .5, y - r * .9), (46 + k * 10 + r, y - r * .2)], "#ff5a6e", "", w=2.4, seed=1660 + k)
    s += shape(ellipse_pts(34, -64, 15 * (1 + .3 * fl), 15 * (1 + .3 * fl), 12), "#e5383b", "", w=2.6, seed=1670)
    return s


def colleague(i, t):
    c = COLS[i]
    spec = dict(c["spec"])
    x = c["x"]
    ph = i * 1.9
    blink = max(0.0, 1 - abs(((t + ph * .37) % 2.7) - 1.3) / 0.07)
    if i == 0:          # трёт пятно, смотрит вниз
        rub = 14 * math.sin(t * 16)
        pose = {"look": (0.1, 1.0), "brow": 0.9, "mouth": "frown", "head_tilt": 8 + 2 * math.sin(t * 2),
                "hand_target": {"R": (62 + rub * .6, -360 + 3 * math.cos(t * 16)), "L": (-96, -300)}, "curl": {"R": 0.2, "L": 0.4},
                "on_torso": stain}
    elif i == 1:        # приглаживает чёлку, глаза вверх
        pat = 10 * math.sin(t * 9)
        pose = {"look": (0.0, -1.0), "brow": -0.6, "mouth": "o", "head_tilt": -5 + 2 * math.sin(t * 2.3),
                "hand_target": {"L": (-112, -330 + pat * .3), "R": (112, -330 - pat * .3)}, "curl": {"L": 0.5, "R": 0.5}}
        spec["messy_t"] = t
    else:               # листает телефон
        sc_ = 4 * math.sin(t * 6)
        pose = {"look": (0.3, 1.0), "brow": 0.2, "mouth": "smile", "head_tilt": -7 + 2 * math.sin(t * 1.7),
                "hand_target": {"R": (-14, -420), "L": (-100, -300)}, "curl": {"R": 0.55, "L": 0.4},
                "over_hand": {"R": lambda h, a: st.phone_up(h[0] - 6, h[1] - 54 + sc_ * .3, .95, -8, 1.0, 1690)}}
    pose["blink"] = blink
    breath = 3 * math.sin(t * 2.2 + ph)
    y = FEET + breath
    body = person.draw(spec, dict(pose, no_arms=True), x, y, 1.0, sd=1700 + i * 100)
    arms = person.draw(spec, dict(pose, only_arms=True), x, y, 1.0, sd=1700 + i * 100)
    sh = blob(ellipse_pts(x, FEET + 4, 130, 18, 14), "#141b38", .55, blur(8))
    g = rad_grad([(0, "#6a80c8", .5), (.6, "#4a5fa0", .18), (1, "#4a5fa0", 0)], x, FEET - 420, 300, 520)
    light = f'<rect x="{f(x - 320)}" y="{f(FEET - 960)}" width="640" height="1040" fill="url(#{g})"/>'
    return light + sh + body + arms


def s09(t):
    s = [_ST["bg"], dust(t)]
    for i in range(3):
        s.append(colleague(i, t))
    ICONS = [icon_shirt, icon_hair, icon_phone]
    heads = [(COLS[i]["x"] + COLS[i]["spec"]["face"] * 6, FEET - 624 - 110) for i in range(3)]
    for i in range(3):
        t_in = 15.0 + i * 0.16
        e = t - t_in
        sc = back_out(clamp(e / 0.32), 2.2) if e > 0 else 0.0
        ef = t - (OST + i * 0.07)
        fl = math.exp(-ef * 2.2) * clamp(ef / 0.06) if ef > 0 else 0.0
        pop = 1 + (0.2 * math.exp(-ef * 7) * math.sin(min(ef * 16, math.pi)) if ef > 0 else 0)
        cx, cy = BUB[i]
        cy += 8 * math.sin(t * 2.4 + i * 2)
        content = f'<g transform="scale({f(1 + .06 * math.sin(t * 3 + i))})">{ICONS[i](t, fl)}</g>'
        s.append(bubble(cx, cy, 310, 240, heads[i], content, sc * pop, 1800 + i * 20, fl))
        s.append(rays(cx, cy, ef, 1850 + i * 20, r=150, n=10, L0=60, w=9, dur=0.45))
    # камера: панорама вдоль ряда слева направо, толчок на «остальные»
    u = clamp((t - 15.0) / 2.3)
    sc = 1.1 + 0.03 * u
    cx = 440 + 200 * (0.35 * u + 0.65 * ease_io(u))
    cy = 860
    rot = -0.8 + 1.2 * u
    sc *= 1 + kick(t, OST, 0.04, 7, 14)
    return cam(cx, cy, sc, rot), "".join(s)


def build_static():
    _ST["bg"] = background()
    cat.static_parts()
    lib.static_done()


def frame(sid, t):
    if not _ST:
        build_static()
    lib.dyn_begin()
    tr, body = {"s07": s07, "s09": s09}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1a2244"/><g transform="{tr}">{body}</g>')
