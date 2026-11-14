"""s10/s11: Калифорния. Светлая комната-лаборатория, за окном солнце, пальма, море; учёный в белом халате показывает карточки со злыми
смайлами (кодом), трое людей за столом смотрят; на «словами» (21.28) человек говорит слово в облачке «ЗЛОСТЬ» (рукописно, кодом).
Одна камера на оба плана (cam_cal), мир общий: t — время ролика."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hw  # noqa: E402
import lib  # noqa: E402
import person  # noqa: E402
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, mul, rad_grad,  # noqa: E402
                 rect_pts, shape, smooth, spring)

_ST = {}
WIN0 = (90, 150, 990, 760)     # окно, как нарисован вид
WIN = (90, 100, 990, 600)      # окно на стене: x0, y0, x1, y1
DY = 600 - 760
TABLE_Y = 985
PF_Y = 1252                    # ступни людей за столом (стол их закрывает по пояс)
SCI_Y = 1430
PX = [630, 815, 1000]
SKIN = ["#f0c4a0", "#c98e6a", "#e8b896"]
SPECS = [dict(skin="#f0c4a0", hair="bob", hair_c="#7a3b22", top="#3f8f8a", low="#454b5c", face=-.5, h=.95),
         dict(skin="#c98e6a", hair="curly", hair_c="#241612", top="#c4553b", low="#3a3f4c", face=-.35, h=.95),
         dict(skin="#e8b896", hair="short", hair_c="#4a3a2e", top="#5b6fa8", low="#2f3446", face=-.3, h=.95, glasses=True)]
SCI = dict(skin="#ecc4a2", hair="short", hair_c="#8a8d98", top="#f6f6f8", low="#3a4150", face=.55, glasses=True, mustache=True, h=1.0, sleeve="#f6f6f8")
SC_SCI = 1.0


# ───────────────────────── окно с видом
def palm(t, x, y, sc=1.0):
    s = []
    sway = 0.05 * math.sin(t * 1.3)
    top = (x + 40 + 60 * sway * 3, y - 300 * sc)
    trunk = lib.band([(x, y), (x + 25 * sc, y - 120 * sc), (x + 10 * sc + 40 * sway, y - 220 * sc), top], 26 * sc, 14 * sc, step=6, wmid=20 * sc, cap=False)
    s.append(shape(trunk, "#9a6a44", blob([(x + 6, y), (x + 30, y - 100), (x + 24, y - 220), (top[0] + 6, top[1])], "#7a4f30", .8), w=3.6, seed=5))
    for k in range(5):
        yy = y - 50 - k * 50
        s.append(line([(x + 2 + 20 * sc * k / 5 - 12, yy), (x + 24 + 20 * sc * k / 5 + 8, yy + 6)], 3, "#6a4426", seed=9 + k, op=.7))
    for i in range(7):
        a = -150 + i * 50 + 6 * math.sin(t * 1.7 + i) + sway * 120
        r = math.radians(a)
        L = (150 + 20 * (i % 2)) * sc
        d = (math.cos(r), math.sin(r))
        nn = (-d[1], d[0])
        droop = 55 * sc * (1 if math.cos(r) > -0.3 and True else 1) * abs(math.cos(r)) ** .5
        p0 = top
        pm = (p0[0] + d[0] * L * .55 + nn[0] * 0, p0[1] + d[1] * L * .55 - 20 * sc)
        p1 = (p0[0] + d[0] * L, p0[1] + d[1] * L + droop)
        pts = [p0, (pm[0] + nn[0] * 20 * sc, pm[1] + nn[1] * 20 * sc - 10), p1, (pm[0] - nn[0] * 16 * sc, pm[1] - nn[1] * 16 * sc + 4)]
        s.append(shape(pts, "#3f9d57" if i % 2 else "#4aac62", blob([p0, pts[3], p1], "#2f7a44", .9), w=3.4, seed=30 + i))
    s.append(shape(ellipse_pts(top[0] - 10, top[1] + 8, 14, 14, 10), "#7a4f30", w=3, seed=60))
    s.append(shape(ellipse_pts(top[0] + 12, top[1] + 12, 12, 12, 10), "#7a4f30", w=3, seed=61))
    return "".join(s)


def view(t):
    x0, y0, x1, y1 = WIN0
    sky = lin_grad([(0, "#7fc8ee", 1), (1, "#e8f6f8", 1)], 0, 0, 0, 1)
    s = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{sky})"/>']
    gl = rad_grad([(0, "#fff6c0", .9), (.4, "#ffe888", .3), (1, "#ffe888", 0)], 770, 330, 300)
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{gl})"/>')
    # солнце с лучами
    for k in range(14):
        a = math.radians(k * 360 / 14 + t * 14)
        c, sn = math.cos(a), math.sin(a)
        s.append(blob([(770 + c * 104 - sn * 12, 330 + sn * 104 + c * 12), (770 + c * 150 * (1 + .1 * math.sin(t * 3 + k)), 330 + sn * 150 * (1 + .1 * math.sin(t * 3 + k))),
                       (770 + c * 104 + sn * 12, 330 + sn * 104 - c * 12)], "#ffd23f", .95))
    s.append(shape(ellipse_pts(770, 330, 92, 92, 28), "#ffd84a", blob(ellipse_pts(790, 350, 92, 92, 24), "#f2b92c", .8)
                   + blob(ellipse_pts(740, 296, 26, 14, 10, rot=-35), "#fff3b0", .9), w=4.6, seed=70))
    # облака
    for i, (cx, cy, r, sp) in enumerate([(300, 280, 58, 14), (560, 210, 44, 9), (880, 480, 40, 11)]):
        x = x0 - 100 + ((cx - x0 + 100 + sp * t) % (x1 - x0 + 200))
        s.append(blob(ellipse_pts(x, cy, r * 1.9, r * .6, 16), "#ffffff", .95) + blob(ellipse_pts(x - r * .5, cy - r * .35, r, r * .6, 14), "#ffffff", .95)
                 + blob(ellipse_pts(x + r * .5, cy - r * .25, r * .8, r * .5, 14), "#ffffff", .95))
    # холмы и море
    s.append(blob([(x0, 560), (260, 500), (480, 540), (700, 480), (x1, 540), (x1, 640), (x0, 640)], "#6fae8a"))
    s.append(blob([(x0, 590), (330, 540), (600, 580), (x1, 560), (x1, 660), (x0, 660)], "#4f9a74"))
    s.append(f'<rect x="{x0}" y="620" width="{x1 - x0}" height="{y1 - 620}" fill="#3a9fd0"/>')
    for k in range(5):
        for j in range(4):
            wx = x0 + ((j * 260 + k * 90 + t * (24 + k * 6)) % (x1 - x0 + 120)) - 60
            wy = 640 + k * 24
            s.append(line([(wx, wy), (wx + 26, wy - 6), (wx + 54, wy)], 4, "#d4effa", taper=.4, wmin=.5, seed=100 + j * 7 + k, op=.8))
    s.append(f'<rect x="{x0}" y="{y1 - 52}" width="{x1 - x0}" height="52" fill="#e9c98f"/>')
    s.append(palm(t, 290, y1 - 8, 1.25))
    return f'<g clip-path="url(#cw)"><g transform="translate(0 {DY})">{"".join(s)}</g></g>'


def build_static():
    if _ST:
        return
    x0, y0, x1, y1 = WIN
    DEFS.append(f'<clipPath id="cw"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>')
    wall = lin_grad([(0, "#f3e6c8", 1), (1, "#e9d6b0", 1)], 0, 0, 0, 1)
    s = [f'<rect x="-1500" y="-1500" width="{W + 3000}" height="{PF_Y + 1500}" fill="url(#{wall})"/>']
    # низ стены — панель
    s.append(f'<rect x="-1500" y="720" width="{W + 3000}" height="600" fill="#d9c397"/>')
    s.append(f'<rect x="-1500" y="716" width="{W + 3000}" height="10" fill="#b79c6c"/>')
    # пол
    fl = lin_grad([(0, "#b98a5e", 1), (1, "#8f6640", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="1250" width="{W + 3000}" height="1500" fill="url(#{fl})"/>')
    for k in range(9):
        yy = 1250 + k * k * 9 + 8
        s.append(f'<rect x="-1500" y="{yy}" width="{W + 3000}" height="4" fill="#7a5532" opacity=".5"/>')
    s.append(f'<rect x="-1500" y="1244" width="{W + 3000}" height="10" fill="#6a4628"/>')
    _ST["back"] = "".join(s)
    # рама окна
    fr = []
    for (a, b, c, d) in ((x0 - 22, y0 - 22, x1 + 22, y0 + 4), (x0 - 22, y1 - 6, x1 + 22, y1 + 26), (x0 - 22, y0, x0 + 4, y1), (x1 - 4, y0, x1 + 22, y1),
                         (535, y0, 557, y1)):
        fr.append(shape(rect_pts(a, b, c, d), "#faf5ea", w=4.6, seed=int(a + b)))
    fr.append(shape(rect_pts(x0 - 40, y1 + 20, x1 + 40, y1 + 48), "#efe4cc", blob(rect_pts(x0 - 40, y1 + 38, x1 + 40, y1 + 48), "#d8c8a4", .9), w=4.6, seed=33))
    _ST["frame"] = "".join(fr)
    # стол и мелочи на нём
    tb = [shape(rect_pts(470, TABLE_Y, 1180, TABLE_Y + 30, 6), "#c58b55", blob(rect_pts(390, TABLE_Y + 16, 1180, TABLE_Y + 30), "#a26c3c", .9), w=5, seed=81),
          shape(rect_pts(480, TABLE_Y + 30, 1170, 1264), "#a8723f", blob(rect_pts(400, TABLE_Y + 30, 1170, TABLE_Y + 46), "#8a5a30", .8)
                + blob(rect_pts(1010, TABLE_Y + 30, 1170, 1264), "#8a5a30", .55), w=5, seed=82)]
    for xx in (700, 860):
        tb.append(line([(xx, TABLE_Y + 50), (xx, 1240)], 3, "#7a4f2a", seed=int(xx), op=.5))
    # блокнот, кружка
    tb.append(shape(rect_pts(470, TABLE_Y - 14, 590, TABLE_Y + 8, 3), "#ffffff", line([(480, TABLE_Y - 6), (570, TABLE_Y - 6)], 2.5, "#9ab", seed=3), w=3.4, seed=84))
    tb.append(shape(rect_pts(720, TABLE_Y - 44, 770, TABLE_Y + 4, 8), "#e8e8ee", blob(rect_pts(748, TABLE_Y - 44, 770, TABLE_Y + 4), "#c4c6d2", .9), w=3.6, seed=85))
    tb.append(line([(770, TABLE_Y - 34), (786, TABLE_Y - 30), (786, TABLE_Y - 12), (770, TABLE_Y - 10)], 4, seed=86))
    tb.append(shape(rect_pts(900, TABLE_Y - 24, 990, TABLE_Y + 6, 4), "#7a8aa8", w=3.4, seed=87))
    _ST["table"] = "".join(tb)
    # световое пятно из окна на полу
    lg = lin_grad([(0, "#fff6c8", .4), (1, "#fff6c8", 0)], 0, 0, 0, 1)
    _ST["beam"] = blob([(140, 1256), (860, 1256), (1100, 1700), (-120, 1700)], f"url(#{lg})", 1.0)
    lib.static_done()


# ───────────────────────── карточки со смайлами
def smiley(kind, cx, cy, r, t=0.0):
    """Злое лицо-смайлик кодом: 0 — хмурый, 1 — красный с оскалом, 2 — зубы и жилка."""
    fillc = ["#ffcf3c", "#f0653f", "#d8392f"][kind]
    sh = ["#e0a82a", "#c84a2a", "#a3231f"][kind]
    s = [shape(ellipse_pts(cx, cy, r, r, 28), fillc, blob(ellipse_pts(cx + r * .22, cy + r * .24, r, r, 24), sh, .85), w=5.4, seed=300 + kind)]
    for sd in (-1, 1):
        ex = cx + sd * r * .38
        ey = cy - r * .1
        s.append(shape(ellipse_pts(ex, ey + r * .06, r * .17, r * .2, 12), "#ffffff", f'<circle cx="{f(ex - sd * r * .02)}" cy="{f(ey + r * .1)}" r="{f(r * .08)}" fill="{INK}"/>', w=3.4, seed=310 + sd))
        s.append(line([(ex - sd * r * .26, ey - r * (.3 - .12 * kind * .5 + sd * 0) - sd * r * .0), (ex + sd * r * .24, ey - r * (.02 + .2 * (kind > 0)) - r * .12 * (kind == 0))][::1 if sd > 0 else -1], 9, "#2a1410", taper=.4, wmin=.5, seed=320 + sd))
    if kind == 0:
        s.append(line([(cx - r * .38, cy + r * .5), (cx, cy + r * .42), (cx + r * .38, cy + r * .5)], 8, seed=330, taper=.3, wmin=.5))
    else:
        mouth = [(cx - r * .46, cy + r * .5), (cx - r * .2, cy + r * .36), (cx + r * .2, cy + r * .36), (cx + r * .46, cy + r * .5), (cx + r * .2, cy + r * .66), (cx - r * .2, cy + r * .66)]
        s.append(shape(mouth, "#4a1414", "".join(f'<rect x="{f(cx - r * .4 + k * r * .16)}" y="{f(cy + r * .36)}" width="{f(r * .12)}" height="{f(r * .3)}" fill="#fff"/>' for k in range(6))
                       if kind == 2 else f'<rect x="{f(cx - r * .4)}" y="{f(cy + r * .36)}" width="{f(r * .8)}" height="{f(r * .1)}" fill="#fff"/>', w=4.4, seed=331))
    if kind == 2:
        s.append(line([(cx + r * .5, cy - r * .74), (cx + r * .6, cy - r * .56), (cx + r * .46, cy - r * .5), (cx + r * .58, cy - r * .34)], 5, "#7a1410", seed=340, taper=.3))
    return "".join(s)


def card(kind, cx, cy, w, h, rot, sk=1.0):
    g = (f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({sk:.4f} 1)">'
         + blob(rect_pts(-w / 2 + 14, -h / 2 + 16, w / 2 + 14, h / 2 + 16, 14), "#3a2410", .28, blur(6))
         + shape(rect_pts(-w / 2, -h / 2, w / 2, h / 2, 14), "#fffdf6", blob(rect_pts(w / 2 - 40, -h / 2, w / 2, h / 2, 6), "#efe6cf", .8), w=6, seed=350 + kind)
         + smiley(kind, 0, -8, w * .34) + "</g>")
    return g


def hand_pos(arm_a1, arm_a2, sc, x, y):
    """Кисть ближней (R) руки учёного: та же формула, что person.arm()."""
    sh_w = 74 * SCI.get("bw", 1.0)
    p0 = (sh_w - 10, -520 + 18)
    e, h = person.limb(p0, arm_a1 + 6, 130, arm_a2, 120)
    return (x + h[0] * sc, y + h[1] * sc)


def sci(t):
    """Учёный: заходит слева с шагом, останавливается, правая рука поднимает карточку на «показывали» (18.48)."""
    u = ease_out(clamp((t - 17.0) / 0.75), 2.4)
    x = -120 + 320 * u
    moving = u < 0.995
    ph = (t - 17.0) * 11.0
    up = spring(t - 18.40, 2.2, 7.0) if t > 18.40 else 0.0
    up = clamp(up, 0, 1.15)
    a1 = 18 + 110 * up
    a2 = 8 + 34 * up
    pose = dict(arms={"R": (a1, a2), "L": (14 + 4 * math.sin(t * 2.0), -10)}, mouth="o" if 18.4 < t < 19.9 and int(t * 5) % 2 == 0 else "flat",
                brow=0.2, look=(0.6, 0.0), head_tilt=1.5 * math.sin(t * 1.6))
    if moving:
        pose["walk"] = ph
        pose["arms"] = {"R": (a1 - 6 * math.sin(ph), a2), "L": (14, -10)}
    pose["legs"] = {"L": (3, 0), "R": (-3, 0)}
    bob = 0 if moving else 3 * math.sin(t * 2.1)
    body = person.draw(SCI, pose, x, SCI_Y + bob, SC_SCI, sd=900)
    hx, hy = hand_pos(a1, a2, SC_SCI, x, SCI_Y + bob)
    return body, (hx, hy), up


def ppl_front(t, k):
    """Человек за столом k: взгляд на карточку, реакции на «показывали» (18.48), «злые» (19.04), «лица» (19.44)."""
    x = PX[k]
    ph = k * 1.7
    react = [smooth(18.48 + .03 * k, 18.7 + .03 * k, t), smooth(19.04, 19.24, t), smooth(19.44, 19.64, t)]
    brow = 0.6 * react[0] + 0.8 * react[1]
    lean = (-10 * react[1] - 6 * react[2]) if k != 1 else (6 * react[1])
    blink = 1.0 if (int(t * 1.1 + ph) % 4 == 0 and (t * 1.1 + ph) % 1 < .12) else 0.0
    mouth = "flat"
    if react[0] > .5 and k == 0:
        mouth = "o"
    if k == 2 and react[2] > .5:
        mouth = "frown"
    if k == 1:
        mouth = "o" if (20.3 < t < 21.3 and int(t * 6) % 2 == 0) else ("frown" if t > 19.3 else "flat")
    pose = dict(arms={"L": (10, -8), "R": (-10, 8)}, mouth=mouth, brow=brow, look=(-0.7, -0.1 + 0.2 * react[1]), blink=blink,
                head_tilt=(2.5 * math.sin(t * 1.4 + ph) + (6 * math.sin(t * 7 + ph) * smooth(20.9, 21.4, t) * (1 if k != 1 else 0)) + lean * .6))
    # кивки на слове (20.45–22.2): остальные кивают
    if k != 1:
        nod = smooth(21.2, 21.5, t) * (0.5 + 0.5 * math.sin((t - 21.3) * 9))
        pose["head_tilt"] += 7 * nod
    yb = 3 * math.sin(t * 2.2 + ph) - 4 * react[0] * math.sin((t - 18.48) * 9) * (1 - smooth(18.7, 19.1, t))
    spec = dict(SPECS[k])
    return person.draw(spec, pose, x + lean, PF_Y + yb, spec["h"], sd=100 * (k + 1))


def bubble(t, cx, cy, w, h, tail_to, sc):
    """Облачко речи с рамкой; сверху «ЗЛОСТЬ» пишется пером (word-time в Line)."""
    s = (blob(rect_pts(cx - w / 2 + 10, cy - h / 2 + 14, cx + w / 2 + 10, cy + h / 2 + 14, 40), "#3a2410", .22, blur(6))
         + shape(rect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 40), "#fffdf8", blob(rect_pts(cx - w / 2, cy + h / 2 - 30, cx + w / 2, cy + h / 2), "#efe6d0", .85), w=6, seed=400)
         + shape([(cx - 30, cy + h / 2 - 6), (tail_to[0], tail_to[1]), (cx + 26, cy + h / 2 - 6)], "#fffdf8", w=6, seed=401))
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({sc:.4f}) translate({f(-cx)} {f(-cy)})">{s}</g>'


_WORD = {}


def word_line():
    if "l" not in _WORD:
        _WORD["l"] = hw.Line("ЗЛОСТЬ", 138, 0, 0, "#b3241c", span=(20.78, 21.30), center=True, wk=1.3)
    return _WORD["l"]


def cam_cal(t):
    """Одна камера на s10+s11: общий план с лёгким наездом, на 20.2–20.6 уходит к говорящему и облачку."""
    a = ease_io(clamp((t - 17.2) / 2.9))
    s0 = 1.0 + 0.08 * a
    cx0, cy0 = 560 + 20 * a, 900
    b = ease_io(clamp((t - 20.0) / 0.55))
    c = smooth(21.7, 22.2, t)
    s = s0 + (1.52 - s0) * b + 0.04 * c
    cx = cx0 + (740 - cx0) * b
    cy = cy0 + (700 - cy0) * b
    rot = -0.6 + 1.1 * a - 1.0 * b
    shake = 0
    return cx, cy, s, rot


def body(t):
    build_static()
    out = [_ST["back"], view(t), _ST["frame"], _ST["beam"]]
    for k in (0, 1, 2):
        out.append(ppl_front(t, k))
    out.append(_ST["table"])
    sbody, (hx, hy), up = sci(t)
    out.append(sbody)
    # карточка в руке: 3 вида сменяются на «показывали» 18.48, «злые» 19.04, «лица» 19.44 (переворот по x)
    if t > 18.36:
        kind = 0 if t < 19.04 else (1 if t < 19.44 else 2)
        tt = {0: 19.04, 1: 19.04, 2: 19.44}[kind]
        flip = 1.0
        if t >= 19.04 and t < 19.04 + .18:
            flip = abs(math.cos(math.pi * (t - 19.04) / .18 * .5 + .0)) if False else abs(math.cos(math.pi * (t - 19.04) / .18))
        if t >= 19.44 and t < 19.44 + .18:
            flip = abs(math.cos(math.pi * (t - 19.44) / .18))
        pop = 0.55 + 0.45 * back_out(clamp((t - 18.40) / 0.32), 2.2)
        sw = 1 + .05 * math.sin(t * 7) * smooth(18.4, 18.8, t)
        cw, ch = 330, 410
        out.append(f'<g transform="translate({f(hx + 44)} {f(hy - 190)}) scale({pop * sw:.4f}) translate({f(-hx - 44)} {f(-hy + 190)})">'
                   + card(kind, hx + 44, hy - 190, cw, ch, -7 + 3 * math.sin(t * 5), flip) + "</g>")
        # рука поверх карточки (кисть) — малая, чтобы пальцы держали край
        out.append(person.hand((hx + 4, hy - 4), 17 * SC_SCI * 1.25, SCI["skin"], 777))
    # облачко слова (s11): растёт на «называли» (20.45), слово пишется 20.78–21.30, пульс на «словами» (21.28)
    if t > 20.4:
        grow = back_out(clamp((t - 20.4) / 0.3), 1.8)
        pulse = 1 + 0.07 * math.sin(clamp((t - 21.28) / 0.35, 0, 1) * math.pi) * (1 if t > 21.28 else 0)
        bx, by = 830, 430
        out.append(bubble(t, bx, by, 480, 190, (PX[1] + 6, 585), grow * pulse))
        wl = word_line()
        out.append(f'<g transform="translate({f(bx)} {f(by + 46)}) scale({grow * pulse:.4f})">{wl.svg(t)}</g>')
    return "".join(out), cam_cal(t)


def s10(t):
    b, c = body(t)
    return f'<g transform="{cam(*c)}">{b}</g>'


s11 = s10
