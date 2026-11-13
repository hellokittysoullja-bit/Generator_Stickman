"""Спальня Димы рилса 35 (сцена bed): одна комната — ночь (s09), утро (s13), вечер (s17), крупно кот (s18).
Кровать вдоль кадра, изголовье слева, подушка, одеяло; над изголовьем бра со шнурком-выключателем; окно справа.
s09 (15.25–16.95): ночь, Дима спит, рот приоткрыт; над головой облачко-мысль, в нём мозг в огоньках; рука с одеяла
     тянется к шнурку бра, на «не выключается» (16.16) — щёлк, комната темнеет, а облачко светится как было.
s13 (22.85–24.45): утро, солнце в окне, Дима сладко спит (без мешков), кот сидит на одеяле; на «выспаться» (23.60)
     Дима садится и потягивается, улыбается.
s17 (28.95–32.1): вечер, Дима сидит и ложится; на «пораньше» (29.68) дёргает шнурок — тёплый ночник; камера уходит
     к подушке: там клубком спит кот (огонёк тлеет); на «кот» (30.60) — кот в кадре, на «спит» (31.52) дёргает ухом.
s18 (32.1–35.7): крупно кот на подушке приоткрывает глаза, смотрит в камеру, медленно моргает, огонёк разгорается.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import cat
import catcurl
import lib
import minibrain
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
CAT_POS = (232, 992, 0.5)        # клубок на подушке (s17/s18)

CLICK9 = 16.16
STRETCH = 23.60
DOWN17 = (28.80, 29.32)
CLICK17 = 29.68
CAT_T = 30.60
FLICK = 31.52


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
    hb = [(x0, FLOOR - 10, 1), (x0, 800), (x0 + 6, 760), ((x0 + x1) / 2, 744), (x1 - 6, 760), (x1, 800), (x1, FLOOR - 10, 1)]
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


# ───────────────────────── облачко-мысль
def thought(t, appear, flare):
    hx, hy = 520, 880
    cx, cy, rx, ry = 760, 560, 215, 160
    s = back_out(clamp(appear), 1.6)
    o = []
    g = rad_grad([(0, "#fff2b0", .7), (.5, "#ffe08a", .3), (1, "#ffd060", 0)], cx, cy, rx * 1.7, ry * 1.8)
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 1.7 * s:.1f}" ry="{ry * 1.8 * s:.1f}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    o.append(props.thought_cloud(cx, cy, rx, ry, (hx, hy), s=s, trail=clamp(appear * 1.5), seed=2700, t=t))
    if s > 0.3:
        bob = 6 * math.sin(t * 3.1)
        look = (math.sin(t * 2.3), 0.2 * math.sin(t * 1.7))
        o.append(minibrain.draw(cx + 10, cy + 10 + bob, 0.62 * s, t, look=look, lit=1.0 + 0.5 * flare, rot=4 * math.sin(t * 2), arms=False))
    return "".join(o)


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
        o.append(line(pts, 7 * sc + 2.5, "#3a4a8a", taper=.1, wmin=.8, seed=2800 + k))
    return "".join(o)


# ───────────────────────── планы
def blink_at(t, times, dur=0.16):
    b = 0.0
    for tb in times:
        u = (t - tb) / dur
        if 0 <= u <= 1:
            b = max(b, math.sin(math.pi * u))
    return b


def s09(t):
    br = 5 * math.sin(t * 2 * math.pi / 3.0)
    # рука: лежит на одеяле → тянется к бусине (15.55–16.0) → дёргает на 16.16 → медленно опускается
    rest = (620, 1000)
    tug = smooth(CLICK9 - 0.1, CLICK9, t) * (1 - smooth(CLICK9 + 0.05, CLICK9 + 0.25, t))
    bead = (BEAD0[0], BEAD0[1] + 34 * tug)
    reach = smooth(15.45, 16.0, t) * (1 - smooth(16.45, 16.95, t))
    tgt = (rest[0] + (bead[0] + 30 - rest[0]) * reach, rest[1] + (bead[1] + 50 - rest[1]) * reach)
    on = 1 - smooth(CLICK9 - 0.02, CLICK9 + 0.04, t)
    expr = {"closed": 1.0, "mouth": "gape", "open": 0.25 + 0.1 * math.sin(t * 2 * math.pi / 3.0), "bags": True, "brows": "calm",
            "hair": 2 * math.sin(t * 2)}
    d = dima(t, 1.0, expr, arm_n=tgt, hand_n={"kind": "open", "curl": tuple([.35 + .4 * reach] * 4), "spread": .1}, breath=br * .4)
    before, after = dima_layers(d, True)
    head_x = d["head"][0]
    o = [_ST["room_night"], lamp(on, t), _ST["bed_back"], pillow(), before, blanket(1.0, head_x), head_over(d, 1.0, expr), after, cord(bead, t)]
    o.append(zzz(t, d["head"][0] - 120, d["head"][1] - 90, 15.0))
    o.append(dark(0.42 + 0.2 * (1 - on)))
    o.append(lamp_glow(on))
    flare = math.exp(-max(0, t - CLICK9) * 3) * (t > CLICK9)
    o.append(thought(t, (t - 15.05) / 0.35 + 0.5, flare))
    # штрихи «щёлк» у бра
    e = t - CLICK9
    if 0 <= e < 0.35:
        o.append(props.burst(LAMP[0], LAMP[1] + 20, 1.0, e / 0.35, seed=2900, color="#f4ead0", n=6, r0=90, r1=140))
    u = clamp((t - 15.05) / 2.1)
    cx, cy, sc = 560 + 20 * u, 830 - 20 * u, 1.18 + 0.06 * ease_io(u)
    e = t - CLICK9
    if e > 0:
        kk = math.exp(-e * 8)
        sc *= 1 + 0.02 * kk
        cy += 5 * kk * math.sin(e * 45)
    return o, (cx, cy, sc, 0.5 * math.sin(t * 1.1))


def s13(t):
    up = smooth(STRETCH - 0.1, STRETCH + 0.3, t)
    arms = smooth(STRETCH + 0.05, STRETCH + 0.45, t) * (1 - 0.15 * smooth(24.2, 24.6, t))
    lie = 1 - up
    if t < STRETCH:
        expr = {"closed": 1.0, "mouth": "smile", "smile": .6, "bags": False, "brows": "calm", "hair": 2 * math.sin(t * 2)}
    elif t < STRETCH + 0.5:
        expr = {"laugh": 1.0, "mouth": "grin", "open": .9, "bags": False, "brows": "up", "hair": 8 * math.sin((t - STRETCH) * 18)}
    else:
        expr = {"lid": .45, "look": (.3, -.3), "mouth": "grin", "open": .5, "bags": False, "brows": "up",
                "closed": blink_at(t, [24.25]), "hair": 3 * math.sin(t * 6)}
    br = 4 * math.sin(t * 2 * math.pi / 3.0) * (1 - up)
    d = dima(t, lie, expr, arms_up=arms, breath=br)
    before, after = dima_layers(d, False, arms_back=arms > 0)
    head_x = d["head"][0] if lie > 0.5 else HIP[0]
    o = [_ST["room_day"], lamp(0, t), cord(BEAD0, t), _ST["bed_back"], pillow(), before, blanket(lie, d["head"][0]), head_over(d, lie, expr), after]
    # кот сидит на одеяле у ног, смотрит на Диму; на «выспаться» — радостный прищур
    happy = 1.0 if t > STRETCH + 0.15 else 0.0
    o.append(cat_sit(t, 1030, 952, 0.55, look=(-0.8, -0.3) if t < STRETCH else (-0.6, -0.6), happy=happy,
                     blink=blink_at(t, [23.1]), tilt=-6 + 4 * math.sin(t * 2)))
    o.append(sunbeams(t))
    if t < STRETCH:
        o.append(zzz(t, d["head"][0] + 40, d["head"][1] - 110, 22.0))
    # искорки бодрости
    e = t - STRETCH - 0.3
    if 0 <= e < 0.7:
        hx, hy = d["head"]
        for k in range(5):
            a = math.radians(-160 + k * 35)
            r = 150 + 110 * ease_out(e / 0.7)
            sc_ = math.sin(math.pi * e / 0.7)
            o.append(star(hx + math.cos(a) * r, hy + math.sin(a) * r, 18 * sc_ + 1, "#f2b43a", 2950 + k))
    u = clamp((t - 22.65) / 2.0)
    cx, cy, sc = 640 + 70 * ease_io(u), 830 - 40 * ease_io(u), 1.2 + 0.05 * u
    e = t - STRETCH
    if e > 0:
        kk = math.exp(-e * 7)
        sc *= 1 + 0.03 * kk * math.sin(min(e * 12, math.pi))
    return o, (cx, cy, sc, -0.5 + 0.8 * u)


def star(x, y, r, col, sd):
    pts = []
    for k in range(8):
        a = math.radians(k * 45 - 90)
        rr = r if k % 2 == 0 else r * 0.38
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return shape(pts, col, "", w=2.4, seed=sd)


def cat_sit(t, x, y, s, look=(0, 0), happy=0.0, blink=0.0, tilt=0.0):
    import cat2
    return cat2.draw(x, y, s, t, look=look, happy=happy, blink=blink, tilt=tilt, tail=4 * math.sin(t * 2.2), shadow=False)


def s17(t):
    a, b = DOWN17
    lie = smooth(a, b, t)
    tug = smooth(CLICK17 - 0.1, CLICK17, t) * (1 - smooth(CLICK17 + 0.05, CLICK17 + 0.25, t))
    bead = (BEAD0[0], BEAD0[1] + 34 * tug)
    rest = (620, 1000)
    reach = smooth(29.3, 29.6, t) * (1 - smooth(29.9, 30.4, t))
    tgt = (rest[0] + (bead[0] + 30 - rest[0]) * reach, rest[1] + (bead[1] + 50 - rest[1]) * reach)
    if t < b:
        expr = {"lid": .35, "look": (.6, .2), "mouth": "smile", "smile": .4, "bags": True, "brows": "calm", "closed": blink_at(t, [28.9])}
    else:
        cl = smooth(29.95, 30.12, t)
        expr = {"lid": .3, "look": (-.4, -.6), "mouth": "smile", "smile": .5, "bags": True, "brows": "calm", "closed": cl}
    on = smooth(CLICK17 - 0.02, CLICK17 + 0.06, t)
    br = 4 * math.sin(t * 2 * math.pi / 3.0) * lie
    d = dima(t, lie, expr, arm_n=tgt if lie > 0.5 else (HIP[0] + 40, HIP[1] - 60),
             hand_n={"kind": "open", "curl": tuple([.35 + .4 * reach] * 4), "spread": .1}, breath=br)
    before, after = dima_layers(d, lie > 0.5)
    o = [_ST["room_eve"], lamp(on, t), _ST["bed_back"], pillow()]
    o.append(curled(t, smolder=1.0))
    o += [before, blanket(lie, d["head"][0]), head_over(d, lie, expr), after, d["arm_n"] if lie < 0.5 else "", cord(bead, t)]
    o.append(dark(0.38 - 0.16 * on, "#1c1640"))
    o.append(lamp_glow(on * 0.85))
    e = t - CLICK17
    if 0 <= e < 0.35:
        o.append(props.burst(LAMP[0], LAMP[1] + 20, 1.0, e / 0.35, seed=2900, color="#7a5a20", n=6, r0=90, r1=140))
    # камера: на Диме → панорама к подушке и коту (к «кот»)
    p = ease_io(clamp((t - 29.95) / 0.65))
    cx = 760 - 40 * clamp((t - 28.75) / 1.2) + (290 - 720) * p
    cy = 820 + (935 - 820) * p
    sc = 1.18 + (1.62 - 1.18) * p + 0.06 * clamp((t - 30.6) / 1.7)
    e = t - CLICK17
    if e > 0:
        kk = math.exp(-e * 8)
        sc *= 1 + 0.02 * kk
    return o, (cx, cy, sc, 0.4 * math.sin(t * 0.9))


def curled(t, smolder=1.0, blink=1.0, look=(0, 0), flame_k=1.0, glow=0.0, head_lift=0.0):
    x, y, s = CAT_POS
    flick = 0.0
    e = t - FLICK
    if 0 <= e < 0.5:
        flick = -22 * math.sin(math.pi * clamp(e / 0.18)) * (1 if e < 0.18 else 0) - 10 * math.sin(math.pi * clamp((e - 0.18) / 0.16)) * (e >= 0.18)
    e2 = t - 33.0
    return catcurl.draw(x, y, s, t, blink=blink, look=look, flick=flick, smolder=smolder, flame_k=flame_k, glow=glow, head_lift=head_lift)


def s18(t):
    # глаза: спит → приоткрывает (32.3–32.9) → смотрит → медленное моргание (33.9–34.6) → снова смотрит
    op = smooth(32.25, 32.95, t)
    bl = 1 - 0.9 * op
    sb = (t - 33.9) / 0.75
    if 0 <= sb <= 1:
        bl = max(bl, 0.1 + 0.9 * math.sin(math.pi * sb))
    ign = smooth(32.6, 33.5, t)
    o = [_ST["room_eve"], lamp(1, t), _ST["bed_back"], pillow()]
    o.append(dark(0.2, "#1c1640"))
    o.append(lamp_glow(0.55))
    o.append(curled(t, smolder=1 - ign, blink=bl, look=(0.0, 0.15), flame_k=1.0 + 0.25 * ign, glow=ign, head_lift=0.6 * op))
    x, y, s = CAT_POS
    hx, hy = catcurl.HEAD_C
    wx = x + (hx - catcurl.BX) * s
    wy = y + (hy - catcurl.BY) * s
    u = clamp((t - 31.9) / 3.8)
    cx, cy = wx + 38 - 14 * u, wy + 62 - 8 * u
    sc = 4.0 + 0.4 * ease_io(u)
    return o, (cx, cy, sc, -0.6 + 0.8 * u)


def build_static(sid):
    if sid == "s18":
        lib.INK_K[0] = 0.55
    _ST["room_night"] = wall("night") + frame_art() + window("night", 0.0)
    _ST["room_day"] = wall("day") + frame_art() + window("day", 0.0)
    _ST["room_eve"] = wall("eve") + frame_art() + window("eve", 0.0)
    _ST["bed_back"] = bed_back()
    catcurl.static()
    cat.static_parts()
    minibrain.body()
    lib.static_done()


def frame(sid, t):
    if not _ST:
        build_static(sid)
    lib.dyn_begin()
    o, (cx, cy, sc, rot) = {"s09": s09, "s13": s13, "s17": s17, "s18": s18}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#2a2a3a"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(o)}</g>')
