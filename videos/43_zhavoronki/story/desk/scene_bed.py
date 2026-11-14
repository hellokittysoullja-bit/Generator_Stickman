"""Спальня Димы рилса 43 (сцена bed, агент C; основа — scene_bed рилса 41): s05 (ночь, спит, на «неделю» на стене
семь чёрточек-дней, на «пять» будильник 5:00 звенит — Дима рывком садится с закрытыми глазами, волосы торчком),
s11 (ночь, Дима тащит себя из кровати за капюшон, второй рукой держится за подушку; «ломать» — рывок, «пять» —
будильник 5:00 подпрыгивает и звенит), s13 (утро, солнце, выспавшийся Дима потягивается, будильник 8:00 мягко
звенит на «восемь»). Будильник — clock/alarm.py рилса 37 (копия alarm.py), стоит на подоконнике; цифры — кодом.
Всё — функция общего времени ролика t."""
import importlib.util
import json
import math
import os


import numpy as np

import lib
import people
import props
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg)

_ST = {}
FLOOR = 1420
HIP = (760.0, 1000.0)
SC = 0.62
MAT = 1062                       # верх матраса
BED_X0, BED_X1 = 110, 1420
HEADB = (64, 128)                # изголовье x0..x1
PILLOW = (330, 1000, 240, 62)    # центр, полуоси
LAMP = (400, 540)                # бра
BEAD0 = (440, 770)               # бусина шнурка в покое


# ───────────────────────── комната
WALL = {"night": "#c9cfb8", "day": "#d8e2c6", "eve": "#d6d4bc"}


def wall(tod):
    o = []
    g = lin_grad([(0, lib.mul(WALL[tod], (.9, .92, .9)), 1), (.6, WALL[tod], 1), (1, lib.mul(WALL[tod], (1.03, 1.03, 1.02)), 1)], 0, -400, 0, FLOOR,
                 units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-900" width="3200" height="{FLOOR + 900}" fill="url(#{g})"/>')
    st = lib.mul(WALL[tod], (.93, .95, .93))
    for k in range(-9, 26):
        x = k * 96
        o.append(line([(x, -900), (x, FLOOR)], 3.0, st, seed=2000 + k, taper=.02, wmin=.9, op=.9))
        for j in range(-8, 15):
            y = j * 110 + (k % 2) * 55
            o.append(blob([(x + 48, y - 9), (x + 55, y), (x + 48, y + 9), (x + 41, y)], st, .9))
    # плинтус и пол
    o.append(shape(rect_pts(-900, FLOOR - 34, 2300, FLOOR), "#efe7d6", blob(rect_pts(-900, FLOOR - 12, 2300, FLOOR), "#d6cbb4"), w=4, seed=2050))
    o.append(shape(rect_pts(-900, FLOOR, 2300, 2600), "#b98a5e",
                   "".join(line([(-900, FLOOR + 50 + k * 70), (2300, FLOOR + 56 + k * 70)], 2.6, "#9a6e45", taper=.1, wmin=.7, seed=2060 + k, op=.8)
                           for k in range(10)), w=4.4, seed=2059))
    return "".join(o)


WIN = (790, 250, 1090, 620)


def window(tod, t):
    x0, y0, x1, y1 = WIN
    o = []
    clip = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    if tod == "night":
        g = lin_grad([(0, "#0d1640", 1), (1, "#28407a", 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    elif tod == "day":
        g = lin_grad([(0, "#7fc0ea", 1), (1, "#d8eef6", 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    else:
        g = lin_grad([(0, "#3b2f6e", 1), (.55, "#c0607a", 1), (1, "#f4a35a", 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    sky = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>']
    if tod == "night":
        sky.append(shape(ellipse_pts(x1 - 90, y0 + 90, 38, 38, 20), "#f7f0cf", blob(ellipse_pts(x1 - 72, y0 + 80, 30, 34, 16), "#16224f"),
                         w=2.6, seed=2101, ink=False))
        rs = np.random.RandomState(3)
        for k in range(9):
            sx, sy = rs.uniform(x0 + 20, x1 - 20), rs.uniform(y0 + 20, y0 + 200)
            r = 3 + 2 * (0.5 + 0.5 * math.sin(t * 5 + k))
            sky.append(f'<circle cx="{f(sx)}" cy="{f(sy)}" r="{f(r)}" fill="#fff6c8"/>')
    elif tod == "day":
        sun = (x0 + 100, y0 + 110)
        for k in range(10):
            a = math.radians(k * 36 + t * 30)
            sky.append(line([(sun[0] + math.cos(a) * 62, sun[1] + math.sin(a) * 62), (sun[0] + math.cos(a) * 92, sun[1] + math.sin(a) * 92)],
                            6, "#ffc93a", taper=.3, wmin=.5, seed=2110 + k))
        sky.append(shape(ellipse_pts(sun[0], sun[1], 50, 50, 20), "#ffd84a", blob(ellipse_pts(sun[0] - 12, sun[1] - 14, 22, 18, 12), "#fff3a8"),
                         w=3.4, seed=2109, ink_color="#d08a10"))
        for j, (cx, cy, s) in enumerate([(x1 - 90 - 12 * math.sin(t * .3), y0 + 90, .9), (x0 + 220 + 10 * math.sin(t * .2), y0 + 200, .6)]):
            sky.append(shape(props.cloud_pts(cx, cy, 70 * s, 26 * s, 7), "#ffffff", "", w=2.6, seed=2120 + j))
    else:
        sun = (x0 + 140, y1 - 40)
        sky.append(blob(ellipse_pts(sun[0], sun[1], 70, 70, 20), "#ffd27a"))
    # дома напротив
    houses = [(x0 - 20, 130, 150), (x0 + 120, 120, 220), (x0 + 250, 110, 120)]
    hc = {"night": ("#1d2550", "#ffe08a"), "day": ("#c98e6c", "#9cc4dc"), "eve": ("#5a3d5e", "#ffcf7a")}[tod]
    for j, (hx, hw, hh) in enumerate(houses):
        top = y1 - hh
        b = blob([(hx, top), (hx + hw, top), (hx + hw, y1 + 10), (hx, y1 + 10)], hc[0])
        for r in range(3):
            for c in range(2):
                wx, wy = hx + 22 + c * 52, top + 26 + r * 56
                if wy + 30 < y1 and (tod != "night" or (j + r + c) % 2 == 0):
                    b += blob(rect_pts(wx, wy, wx + 26, wy + 32), hc[1])
        sky.append(b)
    o.append(f'<g clip-path="url(#{clip})">{"".join(sky)}</g>')
    fr = "#f4efe4"
    m = 22
    o.append(shape([(x0 - m, y0 - m, 1), (x1 + m, y0 - m, 1), (x1 + m, y1 + m, 1), (x0 - m, y1 + m, 1), (x0 - m, y0 - m, 1),
                    (x0, y0, 1), (x0, y1, 1), (x1, y1, 1), (x1, y0, 1), (x0, y0, 1)], fr, w=3.8, seed=2140))
    xm = (x0 + x1) / 2
    o.append(shape(rect_pts(xm - 9, y0, xm + 9, y1), fr, "", w=3.2, seed=2141))
    o.append(shape(rect_pts(x0 - 50, y1 + m, x1 + 50, y1 + m + 28, 4), "#ece4d4",
                   blob(rect_pts(x0 - 50, y1 + m + 16, x1 + 50, y1 + m + 28), "#cfc4ae"), w=3.6, seed=2143))
    o.append(props.curtain(x0 - 70, y0 - 50, y1 + 60, 90, t, col="#6f8fbf", seed=2150, side=1))
    o.append(props.curtain(x1 + 70, y0 - 50, y1 + 60, 90, t + 1, col="#6f8fbf", seed=2160, side=-1))
    return "".join(o)


def frame_art():
    """Полка с книгами и картинка над изголовьем слева (обжито)."""
    o = []
    o.append(shape(rect_pts(-260, 380, -40, 600, 6), "#9a6a3e", shape(rect_pts(-238, 402, -62, 578, 4), "#e9dcc0",
                   blob([(-238, 540), (-180, 470), (-130, 520), (-62, 460), (-62, 578), (-238, 578)], "#8fb59a") +
                   blob(ellipse_pts(-110, 450, 18, 18, 10), "#f2b43a"), w=3, seed=2201), w=4.2, seed=2200))
    return "".join(o)


def bed_back():
    """Изголовье и матрас (то, что за Димой)."""
    o = []
    x0, x1 = HEADB
    hb = [(x0, FLOOR - 10, 1), (x0, 800, 1), (x0 + 9, 770), ((x0 + x1) / 2, 750), (x1 - 9, 770), (x1, 800, 1), (x1, FLOOR - 10, 1)]
    o.append(shape(hb, "#a8693f", blob([(x1 - 22, 750), (x1 + 4, 750), (x1 + 4, FLOOR), (x1 - 22, FLOOR)], "#7f4b2b", .9) +
                   blob([(x0, 750), (x0 + 14, 750), (x0 + 14, FLOOR), (x0, FLOOR)], "#c88a58", .9), w=5, seed=2300))
    o.append(blob(ellipse_pts((x0 + x1) / 2, 780, 14, 8, 10), "#c88a58"))
    # матрас и рама
    o.append(shape(rect_pts(BED_X0, MAT, BED_X1, MAT + 130, 26), "#f1ece0", blob(rect_pts(BED_X0, MAT + 90, BED_X1, MAT + 130), "#d9d1c0"),
                   w=4.6, seed=2310))
    o.append(shape(rect_pts(BED_X0 - 10, MAT + 120, BED_X1 + 10, MAT + 190, 10), "#a8693f",
                   blob(rect_pts(BED_X0 - 10, MAT + 165, BED_X1 + 10, MAT + 190), "#7f4b2b", .9) +
                   line([(BED_X0 + 20, MAT + 140), (BED_X1 - 20, MAT + 140)], 2.4, "#c88a58", seed=2312, op=.8), w=4.8, seed=2311))
    for lx in (BED_X0 + 30, BED_X1 - 60):
        o.append(shape(rect_pts(lx, MAT + 188, lx + 34, FLOOR - 4, 4), "#7f4b2b", "", w=4, seed=2320 + lx % 7))
    o.append(blob(rect_pts(BED_X0 + 40, FLOOR - 16, BED_X1, FLOOR + 6, 8), "#3a2412", .25, blur(10)))
    return "".join(o)


def pillow(dent=0.0):
    cx, cy, rx, ry = PILLOW
    pts = [(cx - rx, cy + 10), (cx - rx + 20, cy - ry + 6), (cx - rx * .4, cy - ry - 6), (cx + rx * .2, cy - ry + 8 * dent),
           (cx + rx * .7, cy - ry - 2), (cx + rx, cy - ry + 18), (cx + rx + 6, cy + 14), (cx + rx - 14, cy + ry), (cx, cy + ry + 6),
           (cx - rx + 14, cy + ry - 2)]
    inner = blob([(cx - rx, cy + 20), (cx + rx, cy + 20), (cx + rx, cy + ry + 10), (cx - rx, cy + ry + 10)], "#dcd6ca", .9)
    inner += line([(cx - rx * .5, cy - 10), (cx - rx * .3, cy + 6)], 2.4, "#cfc8ba", seed=2402, op=.9)
    inner += line([(cx + rx * .4, cy - 20), (cx + rx * .55, cy - 4)], 2.4, "#cfc8ba", seed=2403, op=.9)
    return shape(pts, "#f8f5ee", inner, w=4.8, seed=2400)


QUILT, QUILT_SH, QUILT_ST = "#6f9bc8", "#557fae", "#9cc0e2"


def blanket(lie, head_x):
    """Одеяло: lie 1 — укрыт до подбородка, 0 — сидит, одеяло на коленях. Левый край — по подбородку или у пояса."""
    hx, hy = HIP
    ex = (head_x + 50) * lie + (hx - 150) * (1 - lie)
    ty = hy - 96 * lie - 18 * (1 - lie)
    kx, ky = hx + 260, hy - 100 - 30 * (1 - lie)
    top = [(ex, ty + 40 * lie + 6), (ex + 40, ty + 10 * lie - 4), ((ex + kx) / 2, ty - 8 + 6 * (1 - lie)), (kx - 40, ky + 6), (kx, ky), (kx + 60, ky + 14),
           (hx + 470, hy - 70), (hx + 560, hy - 40), (BED_X1 + 30, MAT + 10)]
    pts = top + [(BED_X1 + 30, MAT + 132, 1), (ex + 20 - 60 * lie, MAT + 140), (ex - 6 - 70 * lie, MAT + 40)]
    inner = blob([(ex - 20, MAT + 60), (BED_X1 + 40, MAT + 50), (BED_X1 + 40, MAT + 150), (ex - 20, MAT + 150)], QUILT_SH, .9)
    for k in range(9):
        x = ex + 60 + k * 90
        inner += line([(x, ty - 40), (x + 30, MAT + 140)], 2.6, QUILT_ST, seed=2500 + k, op=.8, taper=.1, wmin=.8)
    inner += line([(kx - 30, ky + 30), (kx + 40, hy - 10), (kx + 70, hy + 40)], 3, QUILT_SH, seed=2520, op=.9)
    o = [shape(pts, QUILT, inner, w=5, seed=2510)]
    # отворот пододеяльника вдоль верхнего края слева
    cuff_top = top[:4]
    cuff = cuff_top + [(p[0], p[1] + 34) for p in cuff_top[::-1]]
    o.append(shape(cuff, "#f8f5ee", blob([(p[0], p[1] + 22) for p in cuff_top] + [(p[0], p[1] + 40) for p in cuff_top[::-1]], "#dcd6ca", .9),
                   w=4.0, seed=2530))
    return "".join(o)


def lamp(on, t):
    """Бра над изголовьем: абажур, на шнурке — бусина. on 0..1 — свет (тёплое ядро абажура)."""
    x, y = LAMP
    o = []
    o.append(shape(rect_pts(x - 14, y - 70, x + 14, y - 30, 4), "#b08a4a", w=3.2, seed=2600))
    o.append(line([(x, y - 30), (x, y - 14)], 6, "#8a6a34", seed=2601))
    sh = [(x - 66, y - 14), (x + 66, y - 14), (x + 46, y + 70, 1), (x - 46, y + 70, 1)]
    col = mix("#e8d9b6", "#ffe9a8", on)
    o.append(shape(sh, col, blob([(x - 66, y - 14), (x + 66, y - 14), (x + 60, y + 4), (x - 60, y + 4)], mix("#d4c39c", "#fff6d8", on), .9),
                   w=3.6, seed=2602))
    o.append(blob(ellipse_pts(x, y + 72, 40, 9, 12), mix("#cdbd96", "#fff8dc", on)))
    return "".join(o)


def cord(bead, t):
    x, y = LAMP
    top = (x + 28, y + 64)
    mid = ((top[0] + bead[0]) / 2 + 4 * math.sin(t * 2), (top[1] + bead[1]) / 2)
    o = line([top, mid, bead], 3.0, "#5a4632", taper=.05, wmin=.9, seed=2610)
    o += shape(ellipse_pts(bead[0], bead[1] + 8, 9, 12, 10), "#d8b25a", "", w=2.6, seed=2611)
    return o


def lamp_glow(on, big=1.0):
    if on <= 0.01:
        return ""
    x, y = LAMP
    g = rad_grad([(0, "#fff0c0", .75 * on), (.35, "#ffd98a", .38 * on), (1, "#ffc060", 0)], x, y + 160, 620 * big, 520 * big)
    return f'<rect x="-900" y="-900" width="3200" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def dark(op, col="#0b1236"):
    return f'<rect x="-900" y="-900" width="3200" height="3400" fill="{col}" opacity="{op:.3f}"/>'


def sunbeams(t):
    x0, y0, x1, y1 = WIN
    g = lin_grad([(0, "#fff6d0", .45), (1, "#fff6d0", 0)], x1, y0, 400, 1100, units="userSpaceOnUse")
    pts = [(x0 + 20, y0 + 40), (x1 - 10, y0 + 20), (560, 1180), (90, 1150)]
    sway = 0.04 * math.sin(t * 1.2)
    return f'<path d="{lib.fill_d(pts)}" fill="url(#{g})" opacity="{.6 + sway:.3f}" {blur(14)} style="mix-blend-mode:screen"/>'


# ───────────────────────── Дима
def dima(t, lie, expr, arm_n=None, arms_up=0.0, hand_n=None, breath=0.0, side=-1):
    """lie 1 — лежит на спине (голова слева на подушке), 0 — сидит. arm_n — цель ближней руки (мир) или None (под одеялом).
    arms_up 0..1 — потягивание: обе руки вверх за головой."""
    lean = -math.pi / 2 * lie - 0.08 * (1 - lie)
    hip = (HIP[0], HIP[1] + breath)
    if arms_up > 0:
        u = arms_up
        # руки вверх «буквой V» за головой: ближняя вверх-вперёд, дальняя вверх-назад, локти чуть согнуты
        an = 0.62 * math.pi + (math.pi - 0.62 - 0.62 * math.pi) * u
        af = 0.62 * math.pi + (math.pi + 0.5 - 0.62 * math.pi) * u
        arms = {"n": ("ang", an, 0.35 * (1 - u) + 0.12), "f": ("ang", af, -0.35 * (1 - u) - 0.12)}
        hands = {"n": {"kind": "open", "spread": .5, "curl": (.1, .1, .1, .15)}, "f": {"kind": "open", "spread": .5}}
    else:
        # тянется дальней рукой (она за головой и под одеялом у плеча — без рук поперёк лица); ближняя под одеялом
        tgt = arm_n if arm_n is not None else (hip[0] - 120, hip[1] + 10)
        near = (hip[0] + 130, hip[1] - 40)
        arms = {"f": ("ik", tgt, side), "n": ("ik", near, -1)}
        hands = {"f": hand_n or {"kind": "open"}, "n": {"kind": "open", "dir": (1, 0.35), "curl": (.3, .3, .35, .4)}}
    pose = dict(hip=hip, scale=SC, lean=lean, feet=None, pelvis=False, arms=arms, hands=hands, head_ang=lean * 0.22, expr=expr)
    return people.draw(pose)


def head_over(d, lie, expr):
    """Голова поверх одеяла (лёжа одеяло натянуто до подбородка и закрывает шею и плечи)."""
    if lie < 0.3:
        return ""
    lean = -math.pi / 2 * lie - 0.08 * (1 - lie)
    hx, hy = d["head"]
    return (f'<g transform="translate({hx:.2f} {hy:.2f}) scale({SC}) rotate({math.degrees(lean * 0.72):.3f})">'
            f'{people.dima_head(expr)}</g>')


def dima_layers(d, arm_visible, arms_back=False):
    """(до одеяла, после одеяла). Руки при потягивании — за головой."""
    before = (d["arm_n"] if arms_back else "") + d["body"]
    if arms_back or arm_visible:
        before = d["arm_f"] + before
    return before, ""


def zzz(t, x, y, t0=0.0):
    o = []
    for k in range(3):
        ph = ((t - t0) / 1.8 + k / 3) % 1
        sc = back_out(clamp(ph / 0.25), 2) * (1 - ease_in(clamp((ph - 0.8) / 0.2), 2)) * (0.6 + 0.5 * ph)
        if sc < 0.03:
            continue
        cx = x + 90 * ph + 10 * math.sin(ph * 9 + k)
        cy = y - 170 * ph
        r = 18 * sc
        pts = [(cx - r, cy - r), (cx + r, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
        o.append(line(pts, 7 * sc + 2.5, "#dfe6ff", taper=.1, wmin=.8, seed=2800 + k))
    return "".join(o)


# ───────────────────────── планы
def blink_at(t, times, dur=0.16):
    b = 0.0
    for tb in times:
        u = (t - tb) / dur
        if 0 <= u <= 1:
            b = max(b, math.sin(math.pi * u))
    return b




def moonbeam(op=1.0):
    x0, y0, x1, y1 = WIN
    g = lin_grad([(0, "#c4d2ff", .42 * op), (1, "#c4d2ff", .04 * op)], x1, y0, 500, 1200, units="userSpaceOnUse")
    pts = [(x0 + 20, y0 + 120), (x1 - 20, y1 - 20), (1000, 1180), (380, 1160)]
    return f'<path d="{lib.fill_d(pts)}" fill="url(#{g})" {blur(18)} style="mix-blend-mode:screen"/>'


# ═════════════════════════ рилс 43: слова, будильник, надписи ═════════════════════════
HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


T_NEDELYU = wt("неделю")          # 7.04
T_PYAT1 = wt("пять", 7.5)         # 8.04
T_LOMAT = wt("ломать")            # 19.80
T_PYAT2 = wt("пять", 20.5)        # 20.96
T_VOSEM = wt("восемь")            # 24.60

_sp = importlib.util.spec_from_file_location("alarm43", os.path.join(HERE, "alarm.py"))
AL = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(AL)

SILL_Y = WIN[3] + 22               # верх подоконника
ALX, ALS = 965.0, 62.0             # будильник на подоконнике: центр по x, радиус корпуса


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def kick(t, t0, dur=.5, freq=2.2, damp=8.0):
    u = t - t0
    if u <= 0 or u > dur:
        return 0.0
    return math.exp(-u * damp) * math.sin(2 * math.pi * freq * u)


def shake(t, t0, amp, dur=.45, fr=17.0):
    u = t - t0
    if u < 0 or u > dur:
        return 0.0, 0.0, 0.0
    e = math.exp(-u * 7) * amp
    return e * math.sin(u * fr * 6.28), e * .8 * math.sin(u * fr * 5.1 + 1), e * .06 * math.sin(u * fr * 4.3 + 2)


def alarm_on_sill(t, hh, mm, ring=0.0, hop=0.0, uid="a43", x=None):
    ALX = globals()["ALX"] if x is None else x
    cy = SILL_Y - 1.27 * ALS
    o = [AL.shadow(ALX, SILL_Y + 2, ALS, .3)]
    o.append(AL.alarm(ALX, cy - hop, size=ALS, hh=hh, mm=mm, ring=ring, t=t, squash=1 - .08 * max(0.0, -hop) / 20, uid=uid))
    if ring > 0.02:
        o.append(AL.ring_marks(ALX, cy - hop, ALS, t, ring, INK, seed=4400))
    return "".join(o)


def label(x, y, txt, sc, rot=-6, fill="#ffd23f", sh="#e0a92a", sd=4500):
    """Плашка-стикер с цифрами (шрифт IDB) — время кодом."""
    if sc <= 0.02:
        return ""
    w = 40 * len(txt) + 70
    hgt = 120
    body = shape(rect_pts(-w / 2, -hgt / 2, w / 2, hgt / 2, 28), fill, blob(rect_pts(-w / 2, hgt / 2 - 22, w / 2, hgt / 2), sh, .9), w=5.5, seed=sd)
    tx = (f'<text x="0" y="28" text-anchor="middle" font-family="IDB" font-size="84" fill="{INK}" '
          f'stroke="{INK}" stroke-width="1.6">{txt}</text>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sc:.4f})">{body}{tx}</g>'


def pop(t, t0, dur=.24, amp=1.8):
    return back_out(clamp((t - t0) / dur), amp)


def tally(t, t0, x, y):
    """Листок на скотче, на «неделю» на нём одна за другой семь чёрточек-дней (пятая — поперёк первых четырёх)."""
    o = []
    o.append(blob(rect_pts(x - 118, y - 82, x + 128, y + 96, 6), "#2a2418", .22, blur(6)))
    sheet = [(x - 120, y - 88, 1), (x + 118, y - 92, 1), (x + 122, y + 86, 1), (x - 116, y + 90, 1)]
    o.append(shape(sheet, "#fbf6e8", line([(x - 96, y - 46), (x + 98, y - 50)], 2.2, "#cfc6b0", seed=4601, op=.8) +
                   blob([(x - 120, y + 64), (x + 122, y + 60), (x + 122, y + 90), (x - 116, y + 90)], "#ece3cc", .9), w=4.2, seed=4600))
    for k, (tx, ty) in enumerate(((x - 30, y - 104), (x + 34, y - 106))):
        o.append(shape([(tx - 30, ty, 1), (tx + 30, ty - 3, 1), (tx + 31, ty + 22, 1), (tx - 29, ty + 25, 1)], "#e9e2c2", "", w=2.2, seed=4610 + k))
    strokes = []
    for k in range(4):
        sx = x - 80 + k * 30
        strokes.append([(sx, y - 26), (sx + 2, y + 50)])
    strokes.append([(x - 100, y + 34), (x + 32, y - 14)])
    for k in range(2):
        sx = x + 62 + k * 30
        strokes.append([(sx, y - 26), (sx + 2, y + 50)])
    for k, (a, b) in enumerate(strokes):
        u = clamp((t - (t0 + k * .065)) / .07)
        if u <= 0:
            continue
        e = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
        o.append(line([a, ((a[0] + e[0]) / 2 + 1.5, (a[1] + e[1]) / 2), e], 9, "#d23a2c", taper=.25, wmin=.6, seed=4620 + k))
    return "".join(o)


def bed_core(t, d, lie, expr, before, *, room, extra_back="", pil_dx=0.0, front=""):
    o = [room, lamp(0, t), _ST["bed_back"]]
    o.append(f'<g transform="translate({pil_dx:.2f} 0)">{pillow()}</g>')
    o.append(before)
    o.append(blanket(lie, d["head"][0]))
    o.append(head_over(d, lie, expr))
    o.append(front)
    return o


# ═════════════════════════ s05 — неделя в пять: спит → звонок → рывком сел ═════════════════════════
def s05(t):
    tr = T_PYAT1
    up = clamp((t - (tr + .06)) / .17)
    lie = 1 - back_out(up, 1.4) if up > 0 else 1.0
    br = 5 * math.sin(t * 2 * math.pi / 3.2)
    awake = up > 0
    expr = {"closed": 1.0, "bags": True, "hair": 1.5 * math.sin(t * 1.2)}
    if not awake:
        expr.update(mouth="flat", brows="calm")
    else:
        expr.update(mouth="gape", open=.5 + .4 * bump(t, tr + .1, .4), brows="up", wild=clamp(up * 1.3),
                    hair=10 * kick(t, tr + .2, .6, 3.0, 6))
    d = dima(t, lie, expr, breath=br * .4 * (1 - up))
    before, _ = dima_layers(d, lie < .5)
    o = bed_core(t, d, lie, expr, before, room=_ST["room_night"])
    o.insert(1, tally(t, T_NEDELYU, 560, 330))
    ring = clamp((t - tr) / .03)
    hop = 26 * bump(t, tr, .22) + 10 * bump(t, tr + .25, .18)
    al = alarm_on_sill(t, 4, 59.3 + .7 * clamp((t - 6.44) / (tr - 6.44)), ring=ring, hop=hop)
    o.insert(2, al)
    o.append(dark(0.36, "#0b1236"))
    o.append(moonbeam(.7))
    if not awake:
        o.append(zzz(t, d["head"][0] + 30, d["head"][1] - 110, 5.9))
    # будильник светится поверх ночи (корпус и цифры — читаемы), надпись 5:00 выскакивает на «пять»
    o.append(f'<g opacity="{.55 * ring:.3f}">{al}</g>' if ring > 0 else "")
    o.append(label(ALX - 10, SILL_Y - 270, "5:00", 1.05 * pop(t, tr), rot=-7 + 3 * kick(t, tr, .6, 3.0, 5)))
    # камера: медленный наезд на спящего, на звонке — тряска и рывок вслед за Димой
    u = clamp((t - 6.44) / 1.6)
    g = ease_io(clamp((t - (tr + .05)) / .3))
    sx, sy, sr = shake(t, tr, 16)
    cx = 660 + 15 * u + 90 * g + sx
    cy = 905 - 10 * u - 60 * g + sy
    sc = (1.36 + .05 * u + .08 * g) * (1 + .04 * bump(t, tr, .3))
    return o, (cx, cy, sc, -.4 + .5 * u + sr)


# ═════════════════════════ s11 — тащит себя из кровати за капюшон, держится за подушку ═════════════════════════
def tug(t, t0, amp):
    e = t - t0
    if e <= 0:
        return 0.0
    if e < .09:
        return amp * ease_out(e / .09, 2)
    return amp * (.25 + .75 * math.exp(-(e - .09) * 5))


def s11(t):
    tg = tug(t, T_LOMAT, .34) + tug(t, T_LOMAT + .55, .14) + tug(t, T_PYAT2, .3)
    strain = .012 * math.sin(t * 31) * (1 - clamp(tg * 3))
    lie = .66 - tg + strain
    lean = -math.pi / 2 * lie - 0.08 * (1 - lie)
    hip = np.array(HIP)
    expr = {"closed": 1.0, "bags": True, "red": .6, "brows": "worry", "mouth": "sheep", "smile": -.25 + .2 * clamp(tg * 2),
            "wild": .35, "hair": 4 * math.sin(t * 9) + 8 * kick(t, T_LOMAT, .6, 3, 6)}
    probe = people.draw(dict(hip=tuple(hip), scale=SC, lean=lean, feet=None, pelvis=False, expr=expr, head_ang=lean * .22,
                             arms={"f": ("ik", (500, 600), 1), "n": ("ik", (470, 968), -1)}))
    head = probe["head"]
    hood = hip + SC * people.rot(np.array([-60.0, -380.0]), lean)
    pull = clamp(tg * 2.2)
    fist = head + np.array([-70.0 - 20 * pull, -175.0 - 45 * pull]) + np.array([5 * math.sin(t * 29), 3 * math.sin(t * 23)]) * (1 - pull)
    pil_dx = 34 * clamp(tg * 2.5)
    grab = np.array([455.0 + pil_dx, 985.0])
    pose = dict(hip=tuple(hip), scale=SC, lean=lean, feet=None, pelvis=False, expr=expr, head_ang=lean * .22,
                arms={"f": ("ik", tuple(fist + np.array([0, 30])), 1), "n": ("ik", tuple(grab), 1)},
                hands={"f": dict(kind="open", dir=(0.15, 1.0), flip=1, curl=(.95, .97, .97, .93), spread=0, thumb=.9, bend=0, front=True),
                       "n": dict(kind="open", dir=(-.3, 1.0), flip=-1, curl=(.75, .8, .82, .85), spread=.05, thumb=.7, bend=.1)})
    d = people.draw(pose)
    # капюшон тянется от шеи сзади вверх за голову к кулаку (за головой), кулак — поверх
    C = people.PAL["dima"]
    nrm = np.array([-(fist - hood)[1], (fist - hood)[0]])
    nrm = nrm / np.linalg.norm(nrm)
    wb = 46
    a, b = hood + nrm * wb, hood - nrm * wb
    c1, c2 = fist + nrm * 16 + np.array([0, 18]), fist - nrm * 16 + np.array([0, 18])
    mid = (hood + fist) / 2
    pts = [tuple(a) + (1,), tuple(mid + nrm * 26), tuple(c1) + (1,), tuple(c2) + (1,), tuple(mid - nrm * 22), tuple(b) + (1,)]
    folds = "".join(line([tuple(hood + nrm * k * 14), tuple(fist + np.array([0, 20]) + nrm * k * 5)], 2.4, C["FOLD"], seed=4701 + k, op=.8)
                    for k in (-1, 1))
    stretch = shape(pts, C["TOP_SH"], folds, w=4.4, seed=4700)
    before = d["arm_f"] + stretch + d["body"]
    front = d.get("hand_f", "") + d["arm_n"]
    o = bed_core(t, d, lie, expr, before, room=_ST["room_night"], pil_dx=pil_dx, front=front)
    ring = clamp((t - T_PYAT2) / .03)
    hop = 30 * bump(t, T_PYAT2, .22) + 12 * bump(t, T_PYAT2 + .25, .18)
    al = alarm_on_sill(t, 4, 59.4 + .6 * clamp((t - 19.24) / (T_PYAT2 - 19.24)), ring=ring, hop=hop)
    o.insert(1, al)
    # рывок — штрихи у кулака
    e = t - T_LOMAT
    if 0 < e < .3:
        u = e / .3
        for k in range(3):
            up = np.array([-.3, -1.0]) / 1.044
            q = fist + people.rot(up, (k - 1) * .6) * (50 + 50 * u)
            r = fist + people.rot(up, (k - 1) * .6) * (80 + 70 * u)
            o.append(line([tuple(q), tuple(r)], 7 * (1 - u) + 1.5, INK, taper=.3, wmin=.4, seed=4710 + k))
    o.append(dark(0.36, "#0b1236"))
    o.append(moonbeam(.7))
    o.append(f'<g opacity="{.55 * ring:.3f}">{al}</g>' if ring > 0 else "")
    o.append(label(ALX - 10, SILL_Y - 270, "5:00", 1.05 * pop(t, T_PYAT2), rot=-7 + 3 * kick(t, T_PYAT2, .6, 3.0, 5)))
    u = clamp((t - 19.24) / 2.26)
    sx, sy, sr = shake(t, T_LOMAT, 14)
    sx2, sy2, sr2 = shake(t, T_PYAT2, 16)
    cx = 660 + 30 * ease_io(u) + sx + sx2
    cy = 900 - 15 * u + sy + sy2
    sc = (1.42 + .06 * u) * (1 + .035 * bump(t, T_LOMAT, .3) + .04 * bump(t, T_PYAT2, .3))
    return o, (cx, cy, sc, .5 - .7 * u + sr + sr2)


# ═════════════════════════ s13 — утро, 8:00: выспался, потягивается и улыбается ═════════════════════════
def s13(t):
    tv = T_VOSEM
    st = clamp((t - 23.24) / .55)
    arms = .5 + .5 * back_out(st, 1.3) - .1 * smooth(tv + .1, tv + .6, t)
    arms += .04 * math.sin(t * 5.2) * st
    eyes_open = smooth(23.85, 24.1, t)
    look = smooth(tv + .02, tv + .2, t)
    expr = {"closed": 1.0, "laugh": .8 * eyes_open, "bags": False, "brows": "calm" if look < .5 else "up",
            "mouth": "grin" if eyes_open > .5 else "smile", "smile": .9, "open": .4 + .5 * bump(t, tv, .45), "hair": 2 * math.sin(t * 3)}
    lie = -.03 * st + .02 * math.sin(t * 2.6)
    d = dima(t, lie, expr, arms_up=clamp(arms, .05, 1.1))
    before, _ = dima_layers(d, True, arms_back=True)
    o = bed_core(t, d, lie, expr, before, room=_ST["room_night"])
    ring = .45 * clamp((t - tv) / .03) * (1 - smooth(tv + .55, tv + .75, t))
    hop = 12 * bump(t, tv, .22)
    al = alarm_on_sill(t, 7, 59.3 + .7 * clamp((t - 23.24) / (tv - 23.24)), ring=ring, hop=hop, x=1062)
    o.insert(1, al)
    o.insert(1, "")
    o.append(sunbeams(t))
    o.append(label(1010, SILL_Y - 300, "8:00", 1.05 * pop(t, tv), rot=6 - 3 * kick(t, tv, .6, 3.0, 5), fill="#9fe07a", sh="#6fbf4f"))
    u = clamp((t - 23.24) / 2.06)
    k = ease_io(u)
    pk = bump(t, tv, .3)
    cx = 770 + 25 * k
    cy = 860 - 20 * k
    sc = (1.32 + .12 * (.4 * u + .6 * k)) * (1 + .045 * pk)
    return o, (cx, cy, sc, -.5 + .8 * u + .4 * pk * math.sin(t * 40))


def build_static(sid):
    tod = {"s05": "night", "s11": "night", "s13": "day"}.get(sid, "night")
    _ST["room_night"] = wall(tod) + frame_art() + window(tod, 0.0)
    _ST["bed_back"] = bed_back()
    lib.static_done()


def frame(sid, t):
    if not _ST:
        build_static(sid)
    lib.dyn_begin()
    o, (cx, cy, sc, rot) = {"s05": s05, "s11": s11, "s13": s13}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#2a2a3a"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(o)}</g>')
