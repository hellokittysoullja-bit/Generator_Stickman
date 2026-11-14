"""Группа C рилса 46, сцена bars: s10 (20.0–23.3) и s11 (23.3–25.9). Надписи только кодом, коротко.
s10: столбики на кремовом листе. Слева «НОЧЬ БЕЗ СНА» (низкий), справа «2 НЕДЕЛИ ПО 6 ЧАСОВ»: он поднимается высоко,
     к концу медленно оседает, на «как после» (21.52) падает вровень с левым; между вершинами пунктир и знак «=».
s11: три человечка стоят с большими пальцами вверх и улыбкой; над ними шкала САМОЧУВСТВИЕ полная, рядом столбик ВНИМАНИЕ
     низкий; на «нормально» (24.96) вокруг людей вспыхивают звёздочки.
Всё — функция общего времени ролика t."""
import math

import lib
import person
import scene_brain as sb
import scene_lab46 as lab
import study28 as st
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad,
                 rect_pts, shape, smooth, svg)

_ST = {}
LIKE = 21.52       # «как после»
NORMAL = 24.96     # «нормально»
BASE = 990
BX = (300, 780)
BW = 250
LOW = 170
HIGH = 560


def text(x, y, s, size, fill="#3a3440", rot=0.0, sc=1.0, stroke="none", sw=0):
    return lab.text(x, y, s, size, fill, rot, sc, stroke, sw)


def crescent_icon(sd):
    return lab.crescent(-6, 0, 40, sd) + lab.star8(34, -30, .8, "#ffe27a")


def bed_icon(sd):
    s = shape(rect_pts(-52, -4, 52, 14, 4), "#8a5f3c", "", w=3, seed=sd)
    s += shape(rect_pts(-52, -34, -38, 30), "#8a5f3c", "", w=3, seed=sd + 1)
    s += shape(rect_pts(52, -4, 60, 30), "#8a5f3c", "", w=3, seed=sd + 2)
    s += shape(rect_pts(-34, -20, -6, -6, 6), "#f6f1e4", "", w=2.6, seed=sd + 3)
    s += shape(rect_pts(-6, -18, 52, 6, 6), "#3f7fd0", blob(rect_pts(20, -18, 52, 6, 6), "#2d62a8", .8), w=3, seed=sd + 4)
    s += text(6, -34, "6", 34, "#d9433a")
    return s


def badge(x, y, kind, t, sd, k=1.0):
    bob = 4 * math.sin(t * 2.2 + sd)
    ic = {"moon": crescent_icon, "bed": bed_icon}[kind](sd)
    s = shape(ellipse_pts(x, y + bob, 74, 74, 28), "#fbf8ee", blob(ellipse_pts(x + 10, y + bob + 12, 66, 64, 20), "#ece4d0", .8), w=4.4, seed=sd + 50)
    s += f'<g transform="translate({f(x)} {f(y + bob)})">{ic}</g>'
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(k)}) translate({f(-x)} {f(-y)})">{s}</g>'


def bar(x, hh, col, csh, sd):
    hh = max(hh, 3)
    s = blob(rect_pts(x - BW / 2 + 12, BASE - hh + 12, x + BW / 2 + 12, BASE), "#b9a27a", .45)
    inner = blob(rect_pts(x + BW * .18, BASE - hh, x + BW / 2, BASE), csh, .85)
    inner += blob(rect_pts(x - BW / 2 + 16, BASE - hh + 14, x - BW / 2 + 34, BASE - 14), "#ffffff", .35)
    return s + shape(rect_pts(x - BW / 2, BASE - hh, x + BW / 2, BASE, 10), col, inner, w=5, seed=sd)


def chart_bg():
    s = []
    lin_grad([(0, "#f6eedb", 1), (1, "#ead9b8", 1)], 0, 0, 0, 1, gid="gChart46")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#gChart46)"/>')
    for k in range(-6, 30):
        s.append(f'<rect x="-900" y="{-400 + k * 80}" width="{W + 1800}" height="2" fill="#d9c7a2" opacity=".6"/>')
    return "".join(s)


def arrow_down(x, y, k, sd):
    pts = [(0, 90), (-46, 30), (-18, 30), (-18, -60), (18, -60), (18, 30), (46, 30)]
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(k)})">{shape(pts, "#e0301f", "", w=4.4, seed=sd)}</g>'


def s10(t):
    # левый столбик: выскакивает с первого кадра и замирает низко
    u = clamp((t - 19.70) / 0.55)
    hl = LOW * (ease_out(u, 3) + 0.06 * math.sin(math.pi * u) * (u < 1))
    # правый: взлетает высоко, к «как после» оседает, на «как после» падает вровень с левым
    v = clamp((t - 19.74) / 0.7)
    hr = HIGH * (ease_out(v, 3) + 0.05 * math.sin(math.pi * v) * (v < 1))
    if t > 20.56:
        hr = HIGH - 70 * ease_io(clamp((t - 20.56) / (LIKE - 20.56)))
    drop = ease_in(clamp((t - LIKE) / 0.3), 1.8) if t > LIKE else 0.0
    if t > LIKE:
        hr = (HIGH - 70) + (LOW - (HIGH - 70)) * drop
        e = t - LIKE - 0.3
        if e > 0:
            hr = LOW + 22 * math.exp(-e * 8) * math.sin(e * 24)
    s = [_ST["bg"], line([(80, BASE), (1000, BASE)], 7, INK, taper=.05, wmin=.9, seed=5001)]
    # заголовок со стрелкой вверх («внимание»)
    kk = back_out(clamp((t - 19.72) / 0.3), 2.4)
    s.append(f'<g transform="translate(540 250) scale({f(kk)})">{text(0, 0, "ВНИМАНИЕ", 92, "#3a3440", sc=1)}'
             f'{shape([(-300, 30, 1), (-300, -50), (-330, -28), (-300, -70), (-270, -28), (-300, -50, 1)], "#4cc46f", "", w=3.6, seed=5002)}</g>')
    # пунктир уровня «ночь без сна» через весь лист появляется на «как после»
    s.append(bar(BX[0], hl, "#6a7fd0", "#4a5fb0", 5010))
    s.append(bar(BX[1], hr, "#f0a53a", "#c9822a", 5020))
    yl = BASE - LOW
    kline = smooth(LIKE + 0.2, LIKE + 0.55, t)
    if kline > .01:
        x0, x1 = BX[0] + BW / 2, BX[0] + BW / 2 + (BX[1] - BW / 2 - BX[0] - BW / 2) * kline
        n = int((x1 - x0) / 36)
        for i in range(n):
            a = x0 + i * 36
            s.append(line([(a, yl), (a + 22, yl)], 6, "#2f6db5", taper=.1, wmin=.8, seed=5030 + i))
        if kline > .95:
            e = t - LIKE - 0.55
            k2 = back_out(clamp(e / 0.25), 2.8)
            s.append(f'<g transform="translate(540 {f(yl - 6)}) scale({f(k2)})">{shape(ellipse_pts(0, 0, 54, 54, 24), "#fbf8ee", "", w=4.4, seed=5060)}{text(0, 22, "=", 70, "#e0301f")}</g>')
    # красная стрелка вниз у правого на падении
    if LIKE - 0.02 < t < LIKE + 0.7:
        e = t - LIKE
        k = back_out(clamp(e / .2), 2.4) * (1 - ease_in(clamp((e - .45) / .25)))
        s.append(arrow_down(BX[1] + 220, BASE - 400 + 160 * ease_out(clamp(e / .3)), k, 5070))
    # значки и подписи
    kb = back_out(clamp((t - 19.78) / 0.3), 2.2)
    s.append(badge(BX[0], BASE + 92, "moon", t, 5100, kb))
    s.append(badge(BX[1], BASE + 92, "bed", t, 5160, kb))
    kc = back_out(clamp((t - 19.84) / 0.3), 2.2)
    for x, l1, l2 in ((BX[0], "НОЧЬ", "БЕЗ СНА"), (BX[1], "2 НЕДЕЛИ", "ПО 6 ЧАСОВ")):
        s.append(f'<g transform="translate({x} 0) scale({f(kc)}) translate({-x} 0)">{text(x, BASE + 220, l1, 46)}{text(x, BASE + 268, l2, 46)}</g>')
    # камера: влёт с первого кадра, толчок на падении
    uu = clamp((t - 19.8) / 3.7)
    scl = 1.0 + 0.07 * ease_io(uu)
    cy = 930 - 10 * uu
    rot = 1.0 - 1.6 * uu
    e = t - LIKE
    if e > 0:
        scl *= 1 + 0.05 * math.exp(-e * 6) * math.sin(min(e * 14, math.pi))
        cy += 12 * math.exp(-e * 8) * math.sin(e * 50)
    return "".join(s), cam(540, cy, scl, rot)


# ───────────────────────── s11
SPECS = [dict(st.STUDENTS[0]), dict(st.STUDENTS[2]), dict(st.STUDENTS[3])]
for _sp in SPECS:
    _sp["face"] = 0.0
PX = [200, 540, 880]
FLOORY = 1195
PSC = 0.70


def thumb_up(h, a, skin, sd, bob=0.0):
    """Кулак с поднятым большим пальцем на конце предплечья (координаты человека): кулак за запястьем, палец вверх."""
    d = (math.cos(math.radians(a)), math.sin(math.radians(a)))
    cx, cy = h[0] + d[0] * 40, h[1] + d[1] * 40
    sh = person.shade(skin)
    fist = ellipse_pts(cx, cy, 46, 40, 18, rot=a)
    inner = blob(ellipse_pts(cx + 12, cy + 12, 38, 30, 14, rot=a), sh, .7)
    for k in range(3):
        yy = cy - 18 + k * 18
        inner += line([(cx + 6, yy), (cx + 32, yy + 2)], 3, "#8a6a56", taper=.4, seed=sd + 5 + k, op=.9)
    out = shape(fist, skin, inner, w=3.6, seed=sd)
    pts = [(cx + 2, cy - 24), (cx + 4, cy - 52 + bob), (cx + 5, cy - 80 + bob)]
    out += shape(sb.sausage(pts, 30, 26), skin, blob([(cx + 12, cy - 30), (cx + 16, cy - 76 + bob), (cx + 9, cy - 80 + bob)], sh, .7), w=3.4, seed=sd + 1)
    return out


def gauge_h(x0, x1, y, k, t):
    """Горизонтальная шкала самочувствия: заполняется до k (0..1), смайлик на конце."""
    h = 70
    s = [text((x0 + x1) / 2 - 90, y - 30, "САМОЧУВСТВИЕ", 52)]
    inner = ""
    if k > .01:
        xe = x0 + (x1 - x0) * k
        inner += blob(rect_pts(x0 - 4, y - 4, xe, y + h + 4), "#4cc46f")
        inner += blob(rect_pts(x0 - 4, y + h * .55, xe, y + h + 4), "#2f9a52", .8)
        inner += line([(x0 + 12, y + 16), (xe - 14, y + 16)], 5, "#ffffff", taper=.1, wmin=.8, seed=5300, op=.7)
    s.append(shape(rect_pts(x0, y, x1, y + h, 34), "#f3f1ea", inner, w=5.2, seed=5301))
    # смайлик
    sx, sy = x1 + 62, y + h / 2
    kk = back_out(clamp((t - 23.55) / 0.3), 2.4) * (1 + 0.04 * math.sin(t * 5))
    face = shape(ellipse_pts(0, 0, 54, 54, 24), "#ffd84a", blob(ellipse_pts(10, 10, 46, 44, 18), "#f0b92e", .6), w=4.6, seed=5310)
    face += shape(ellipse_pts(-18, -10, 6, 8, 8), INK, "", w=1, seed=5311) + shape(ellipse_pts(18, -10, 6, 8, 8), INK, "", w=1, seed=5312)
    face += line([(-26, 12), (0, 34), (26, 12)], 5, INK, taper=.3, wmin=.6, seed=5313)
    s.append(f'<g transform="translate({f(sx)} {f(sy)}) scale({f(kk)})">{face}</g>')
    return "".join(s)


def gauge_v(x, top, bot, k, t):
    wd = 100
    inner = ""
    h = bot - top
    lv = bot - h * k
    inner += blob(rect_pts(x - wd / 2 - 4, lv, x + wd / 2 + 4, bot + 4), "#ff6a4a")
    inner += blob([(x + 10, lv), (x + wd / 2 + 4, lv), (x + wd / 2 + 4, bot + 4), (x + 10, bot + 4)], "#d0452e", .85)
    for q in range(1, 5):
        yy = top + h * q / 5
        inner += line([(x + wd / 2 - 34, yy), (x + wd / 2 - 4, yy)], 3.2, INK, taper=.1, wmin=.8, seed=5400 + q, op=.7)
    return text(x, top - 30, "ВНИМАНИЕ", 44) + shape(rect_pts(x - wd / 2, top, x + wd / 2, bot, 40), "#f3f1ea", inner, w=5.2, seed=5410)


def person_fig(i, t):
    x = PX[i]
    ph = i * 1.3
    up = ease_out(clamp((t - 23.1 - i * 0.07) / 0.3), 2)       # руки взлетают вверх
    bob = 7 * math.sin(t * 7 + ph)
    br = math.sin(t * 2.3 + ph)
    bl = (t * .8 + ph * .4) % 2.8
    sad = 0
    wob = 5 * math.sin(t * 7 + ph) * up
    aR = (8 + (46 - 8) * up + wob, -6 + (104 + 6) * up)
    aL = (-8 + (-46 + 8) * up - wob, 6 + (-104 - 6) * up)
    pose = {"legs": {"L": (3, 0), "R": (-3, 0)}, "mouth": "smile", "brow": 0.5 + 0.4 * (t > NORMAL),
            "look": (0.1 * math.sin(t + ph), 0.0), "head_tilt": 4 * math.sin(t * 1.5 + ph) + 3 * (i - 1), "blink": max(0.0, 1 - abs(bl - 1.3) / 0.07),
            "arms": {"L": aL, "R": aR}, "curl": {"L": .9, "R": .9},
            "over_hand": {"L": lambda h, a, sd=7000 + i * 100: thumb_up(h, a, SPECS[i]["skin"], sd, bob * .5),
                          "R": lambda h, a, sd=7050 + i * 100: thumb_up(h, a, SPECS[i]["skin"], sd, bob * .5)}}
    jump = -10 * abs(math.sin(t * 3.5 + ph)) * (t > NORMAL) * 0
    shadow = blob(ellipse_pts(x + 8, FLOORY + 6, 120, 18, 14), "#9a8a6a", .5, blur(5))
    body = person.draw(SPECS[i], dict(pose, no_arms=True), x, FLOORY + 2 * br + jump, PSC, sd=7200 + i * 100)
    arms = person.draw(SPECS[i], dict(pose, only_arms=True), x, FLOORY + 2 * br + jump, PSC, sd=7200 + i * 100)
    return shadow + body + arms


def s11(t):
    s = [_ST["bg"]]
    s.append(line([(-200, FLOORY + 4), (1280, FLOORY + 4)], 5, INK, taper=.05, wmin=.9, seed=5500))
    # шкала самочувствия: заполняется с кадра 0
    gk = ease_out(clamp((t - 23.12) / 0.55), 2) * (1 + 0.0)
    s.append(gauge_h(90, 650, 300, min(1.0, gk), t))
    ak = 0.22 * ease_out(clamp((t - 23.2) / 0.5), 3)
    ak += 0.01 * math.sin(t * 6)
    s.append(gauge_v(880, 190, 470, ak, t))
    for i in (0, 2, 1):
        s.append(person_fig(i, t))
    # звёздочки на «нормально»
    e = t - NORMAL
    if e > 0:
        for j in range(10):
            a = j * 2 * math.pi / 10 + .3
            rx, ry = 480, 330
            sx, sy = 540 + math.cos(a) * rx * (1 + .1 * math.sin(e * 3 + j)), 900 + math.sin(a) * ry
            k = back_out(clamp((e - j * 0.025) / 0.25)) * (0.85 + 0.2 * math.sin(e * 8 + j))
            if k > .05:
                s.append(lab.star8(sx, sy, 1.5 * k, "#ffcf3a", j * 17 + e * 90))
        if e < 0.5:
            for j in range(10):
                a = j * math.pi / 5
                r0 = 80 + 160 * ease_out(e / .5)
                s.append(line([(540 + math.cos(a) * r0 * 2, 700 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + 24 * (1 - e / .5)) * 2, 700 + math.sin(a) * (r0 + 24 * (1 - e / .5)))],
                              7, "#ffcf3a", taper=.5, seed=5600 + j))
    uu = clamp((t - 23.1) / 2.8)
    scl = 1.0 + 0.06 * ease_io(uu)
    cy = 870 + 10 * uu
    if e > 0:
        scl *= 1 + 0.045 * math.exp(-e * 6) * math.sin(min(e * 14, math.pi))
        cy += 8 * math.exp(-e * 8) * math.sin(e * 50)
    return "".join(s), cam(540, cy, scl, 0.8 - 1.3 * uu)


def build_static():
    if _ST:
        return
    _ST["bg"] = chart_bg()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s10": s10, "s11": s11}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#f0e4c8"/><g transform="{cm}">{art}</g>')
