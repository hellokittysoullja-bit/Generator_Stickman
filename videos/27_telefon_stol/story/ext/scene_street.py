"""Сцена street (s09, 13.68–16.6): британская улица утром — ряд кирпичных домов с белыми окнами-«гильотинами»,
красная телефонная будка, справа налево проезжает красный двухэтажный автобус (колёса крутятся, кузов покачивается),
на тротуаре группа людей в спортивных костюмах (люди рилсов 23/25, person.py) разминается: бег на месте, потягивания.
Ни одной буквы и логотипа: табло автобуса и короб будки — пустые светлые панели."""
import math

import numpy as np

import lib
import person
from lib import (INK, W, H, blob, blur, cam, clamp, ease_io, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape,
                 smooth, svg)

_ST = {}
GROUND = 1010     # низ домов / дальний тротуар
ROAD0, ROAD1 = 1040, 1170
FEET = 1300


# ───────────────────────── фон
def sky():
    s = []
    lin_grad([(0, "#8fbfe6", 1), (.55, "#cfe2ee", 1), (1, "#ffe1bf", 1)], 0, 0, 0, 1, gid="gSkyS")
    s.append(f'<rect x="-500" y="-600" width="{W + 1000}" height="{GROUND + 600}" fill="url(#gSkyS)"/>')
    g = rad_grad([(0, "#fff6d8", .95), (.35, "#ffe9b0", .45), (1, "#ffe9b0", 0)], 120, 120, 520)
    s.append(f'<rect x="-500" y="-600" width="{W + 1000}" height="{GROUND + 600}" fill="url(#{g})"/>')
    for k, (x, y, r) in enumerate([(760, 150, 90), (-40, 300, 70), (1180, 330, 60)]):
        pts = []
        for j in range(16):
            a = 2 * math.pi * j / 16
            rr = r * (1 + 0.22 * math.sin(3 * a + k))
            pts.append((x + 1.9 * rr * math.cos(a), y + 0.7 * rr * math.sin(a)))
        s.append(shape(pts, "#ffffff", blob([(x - 2 * r, y + 10), (x + 2 * r, y + 4), (x + 2 * r, y + r), (x - 2 * r, y + r)], "#dfe8f2", .9),
                       w=3.6, seed=10 + k))
    return "".join(s)


def brick_tex(x0, y0, x1, y1, col, sd):
    """Кирпичная кладка: ряды и швы, чуть темнее/светлее отдельные кирпичи."""
    rs = np.random.RandomState(sd)
    s = []
    dark = lib.mul(col, (.82, .8, .82))
    lite = lib.mul(col, (1.1, 1.08, 1.06))
    y = y0 + 4
    row = 0
    while y < y1:
        s.append(f'<rect x="{f(x0)}" y="{f(y)}" width="{f(x1 - x0)}" height="2.2" fill="{dark}" opacity=".55"/>')
        off = 0 if row % 2 else 22
        for x in np.arange(x0 + off, x1, 44):
            s.append(f'<rect x="{f(x)}" y="{f(y - 15)}" width="2" height="15" fill="{dark}" opacity=".45"/>')
            v = rs.uniform()
            if v < .12:
                s.append(f'<rect x="{f(x + 3)}" y="{f(y - 14)}" width="38" height="12" fill="{dark}" opacity=".5"/>')
            elif v < .2:
                s.append(f'<rect x="{f(x + 3)}" y="{f(y - 14)}" width="38" height="12" fill="{lite}" opacity=".5"/>')
        y += 17
        row += 1
    return "".join(s)


def sash(x, y, w, h, sd, curtain=None):
    """Окно-«гильотина»: белая рама, две створки 2×2 стекла, подоконник, перемычка."""
    s = []
    s.append(shape(rect_pts(x - 10, y - 18, x + w + 10, y), "#e9e2d2", "", w=3.2, seed=sd))       # перемычка
    inner = ""
    glass = "#7f9fbf"
    for (gx, gy) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        px0 = x + 10 + gx * (w - 20) / 2
        py0 = y + 10 + gy * (h - 20) / 2
        inner += f'<rect x="{f(px0 + 3)}" y="{f(py0 + 3)}" width="{f((w - 20) / 2 - 6)}" height="{f((h - 20) / 2 - 6)}" fill="{glass}"/>'
        inner += blob([(px0 + 6, py0 + (h - 20) / 2 - 10), (px0 + (w - 20) / 2 - 10, py0 + 8), (px0 + (w - 20) / 2 - 3, py0 + 8),
                       (px0 + (w - 20) / 2 - 3, py0 + 18), (px0 + 18, py0 + (h - 20) / 2 - 3), (px0 + 6, py0 + (h - 20) / 2 - 3)], "#c9dcef", .8)
    if curtain:
        inner += blob([(x + 12, y + 12), (x + 34, y + 12), (x + 26, y + h * .5), (x + 14, y + h - 14), (x + 12, y + h - 14)], curtain)
        inner += blob([(x + w - 12, y + 12), (x + w - 34, y + 12), (x + w - 26, y + h * .5), (x + w - 14, y + h - 14), (x + w - 12, y + h - 14)], curtain)
    inner += f'<rect x="{f(x)}" y="{f(y + h / 2 - 5)}" width="{f(w)}" height="10" fill="#f6f2ea"/>'
    inner += f'<rect x="{f(x + w / 2 - 4)}" y="{f(y)}" width="8" height="{f(h)}" fill="#f6f2ea"/>'
    s.append(shape(rect_pts(x, y, x + w, y + h), "#f6f2ea", inner, w=3.6, seed=sd + 1))
    s.append(shape(rect_pts(x - 12, y + h, x + w + 12, y + h + 14), "#e9e2d2", "", w=3.2, seed=sd + 2))
    return "".join(s)


DOORS = ["#2d4f8a", "#1f2a2e", "#2f7a52", "#8a2f3a", "#e0b64a"]
BRICK = ["#b5543d", "#a84a3b", "#c26a4c", "#9c4636", "#b85e45"]


def house(x0, wd, k):
    """Дом террасы: три этажа, дверь с полукруглым окошком, ступенька, труба с горшками."""
    s = []
    top = 300 + (k % 2) * 20
    col = BRICK[k % len(BRICK)]
    # крыша (сланец) и труба
    s.append(shape([(x0 - 6, top + 30), (x0 + 20, top - 40), (x0 + wd - 20, top - 40), (x0 + wd + 6, top + 30)], "#5b6574",
                   blob([(x0 + wd * .5, top - 40), (x0 + wd - 20, top - 40), (x0 + wd + 6, top + 30), (x0 + wd * .6, top + 30)], "#48505d", .9) +
                   "".join(line([(x0 + 10, top - 20 + j * 16), (x0 + wd - 10, top - 20 + j * 16)], 2, "#48505d", taper=.1, wmin=.8, seed=k * 10 + j, op=.7) for j in range(4)),
                   w=4, seed=100 + k))
    cx = x0 + wd * (.72 if k % 2 else .25)
    s.append(shape(rect_pts(cx - 30, top - 110, cx + 30, top - 30), col, brick_tex(cx - 30, top - 110, cx + 30, top - 30, col, 300 + k) +
                   blob(rect_pts(cx + 6, top - 110, cx + 30, top - 30), lib.mul(col, (.8, .78, .82)), .9), w=4, seed=110 + k))
    s.append(shape(rect_pts(cx - 36, top - 124, cx + 36, top - 106), "#e9e2d2", "", w=3.2, seed=120 + k))
    for j, px in enumerate((cx - 16, cx + 14)):
        s.append(shape(rect_pts(px - 9, top - 150, px + 9, top - 124), "#c46a3a", "", w=3, seed=130 + k * 3 + j))
    # фасад
    inner = brick_tex(x0, top + 30, x0 + wd, GROUND, col, 200 + k)
    inner += blob([(x0 + wd - 40, top + 30), (x0 + wd, top + 30), (x0 + wd, GROUND), (x0 + wd - 40, GROUND)], lib.mul(col, (.82, .8, .86)), .8)
    s.append(shape([(x0, top + 30, 1), (x0 + wd, top + 30, 1), (x0 + wd, GROUND, 1), (x0, GROUND, 1)], col, inner, w=4.6, seed=140 + k))
    s.append(shape(rect_pts(x0 - 4, top + 24, x0 + wd + 4, top + 44), "#e9e2d2", "", w=3.4, seed=145 + k))
    # окна
    door_left = k % 2 == 0
    for fl, wy in enumerate([top + 90, top + 330]):
        for j in range(2):
            wx = x0 + 34 + j * (wd - 68) / 2 + 4
            s.append(sash(wx, wy, (wd - 68) / 2 - 22, 170 if fl == 0 else 180, 400 + k * 20 + fl * 5 + j,
                          curtain=["#f2d27a", "#d98a9a", "#9fc5a6"][(k + j + fl) % 3] if (k + j + fl) % 2 else None))
    # первый этаж: дверь + окно
    dx = x0 + (40 if door_left else wd - 150)
    dc = DOORS[k % len(DOORS)]
    s.append(shape([(dx - 14, GROUND - 270, 1), (dx + 124, GROUND - 270, 1), (dx + 124, GROUND, 1), (dx - 14, GROUND, 1)], "#e9e2d2", "", w=3.6, seed=150 + k))
    fan = [(dx, GROUND - 256)] + [(dx + 55 - 55 * math.cos(a), GROUND - 256 - 40 * math.sin(a)) for a in np.linspace(0, math.pi, 8)] + [(dx + 110, GROUND - 256)]
    s.append(shape(fan, "#9fbfdc", line([(dx + 55, GROUND - 256), (dx + 55, GROUND - 296)], 2.4, "#f6f2ea", seed=155 + k), w=3, seed=156 + k))
    dpan = "".join(f'<rect x="{f(dx + 14 + c * 46)}" y="{f(GROUND - 236 + r * 74)}" width="36" height="58" rx="3" fill="{lib.mul(dc, (.82, .82, .86))}"/>'
                   for r in range(3) for c in range(2))
    s.append(shape(rect_pts(dx, GROUND - 250, dx + 110, GROUND - 10), dc, dpan + f'<circle cx="{f(dx + 92)}" cy="{f(GROUND - 120)}" r="6" fill="#e8c46a"/>',
                   w=4, seed=160 + k))
    s.append(shape(rect_pts(dx - 20, GROUND - 12, dx + 130, GROUND + 6), "#d6d0c2", "", w=3.2, seed=165 + k))
    gx = x0 + (wd - 160 if door_left else 40)
    s.append(sash(gx, GROUND - 230, 120, 170, 470 + k * 3, curtain="#f2d27a" if k % 3 == 0 else None))
    return "".join(s)


def street_static():
    s = [sky()]
    wd = 300
    for k in range(6):
        s.append(house(-420 + k * wd, wd, k))
    # дальний тротуар, бордюр, дорога
    s.append(shape([(-500, GROUND, 1), (W + 500, GROUND, 1), (W + 500, ROAD0, 1), (-500, ROAD0, 1)], "#cfcac0", "", w=3.6, seed=20))
    s.append(shape([(-500, ROAD0, 1), (W + 500, ROAD0, 1), (W + 500, ROAD1, 1), (-500, ROAD1, 1)], "#5a5f6a",
                   blob([(-500, ROAD0 + 70), (W + 500, ROAD0 + 70), (W + 500, ROAD1), (-500, ROAD1)], "#50545e", .9), w=4, seed=21))
    for x in range(-500, W + 500, 160):
        s.append(f'<rect x="{x}" y="{ROAD0 + 62}" width="90" height="8" fill="#f2efe4"/>')
    # ближний тротуар: плиты
    s.append(shape([(-500, ROAD1, 1), (W + 500, ROAD1, 1), (W + 500, H + 400, 1), (-500, H + 400, 1)], "#d9d4ca",
                   "".join(line([(-500, y), (W + 500, y)], 2.2, "#bdb7aa", taper=.05, wmin=.9, seed=30 + i) for i, y in enumerate([1260, 1420, 1640, 1900])) +
                   "".join(line([(x, ROAD1), (x + (x - 540) * .5, H + 200)], 2.2, "#bdb7aa", taper=.05, wmin=.9, seed=40 + i)
                           for i, x in enumerate(range(-400, W + 500, 180))),
                   w=4, seed=22))
    s.append(shape([(-500, ROAD1 - 6, 1), (W + 500, ROAD1 - 6, 1), (W + 500, ROAD1 + 14, 1), (-500, ROAD1 + 14, 1)], "#ece8de", "", w=3.4, seed=23))
    return "".join(s)


# ───────────────────────── телефонная будка
RED = "#d8322c"
RED_SH = "#a8221f"


def booth(x, y):
    """Будка: x — левый край, y — низ. Ширина 190, высота 560, купол, пустой светлый короб под куполом."""
    s = []
    w, h = 190, 560
    s.append(blob(ellipse_pts(x + w / 2 + 30, y + 6, 140, 20, 14), "#7d7468", .5, blur(6)))
    s.append(shape(rect_pts(x - 8, y - 18, x + w + 8, y + 2), RED_SH, "", w=4, seed=600))
    body_in = blob(rect_pts(x + w - 34, y - h, x + w, y), RED_SH, .9)
    # стёкла: 3 × 6 мелких
    gx0, gy0, gw, gh = x + 32, y - h + 130, w - 64, h - 200
    body_in += f'<rect x="{f(gx0)}" y="{f(gy0)}" width="{f(gw)}" height="{f(gh)}" fill="#bcd3e0"/>'
    body_in += blob([(gx0, gy0 + gh * .6), (gx0 + gw, gy0 + gh * .1), (gx0 + gw, gy0 + gh * .3), (gx0, gy0 + gh * .85)], "#e6f0f6", .8)
    for c in range(1, 3):
        body_in += f'<rect x="{f(gx0 + c * gw / 3 - 3)}" y="{f(gy0)}" width="6" height="{f(gh)}" fill="{RED}"/>'
    for r in range(1, 6):
        body_in += f'<rect x="{f(gx0)}" y="{f(gy0 + r * gh / 6 - 3)}" width="{f(gw)}" height="6" fill="{RED}"/>'
    body_in += line([(gx0, gy0), (gx0 + gw, gy0), (gx0 + gw, gy0 + gh), (gx0, gy0 + gh), (gx0, gy0)], 3, INK, taper=.05, wmin=.9, seed=601)
    # короб без надписи
    body_in += shape(rect_pts(x + 22, y - h + 70, x + w - 22, y - h + 108, 4), "#f4f0e2", "", w=3, seed=602)
    body_in += f'<rect x="{f(x + w - 14)}" y="{f(y - h * .5)}" width="7" height="40" rx="3" fill="#9a1b18"/>'
    s.append(shape(rect_pts(x, y - h, x + w, y - 18), RED, body_in, w=5, seed=603))
    # купол
    dome = [(x - 10, y - h + 6, 1), (x - 6, y - h - 20), (x + w / 2, y - h - 62), (x + w + 6, y - h - 20), (x + w + 10, y - h + 6, 1)]
    s.append(shape(dome, RED, blob([(x + w / 2, y - h - 62), (x + w + 6, y - h - 20), (x + w + 10, y - h + 6), (x + w / 2 + 20, y - h + 6)], RED_SH, .9),
                   w=4.6, seed=604))
    s.append(shape(ellipse_pts(x + w / 2, y - h - 64, 14, 9, 10), RED, "", w=3, seed=605))
    s.append(blob(ellipse_pts(x + 40, y - h - 10, 24, 8, 8, rot=-20), "#ff8a7a", .8))
    return "".join(s)


# ───────────────────────── автобус
def wheel(cx, cy, r, ang, sd):
    s = [shape(ellipse_pts(cx, cy, r, r, 20), "#23252b", "", w=4, seed=sd)]
    s.append(shape(ellipse_pts(cx, cy, r * .55, r * .55, 16), "#b9bec6", blob(ellipse_pts(cx + 6, cy + 6, r * .45, r * .45, 12), "#8c919a", .8),
                   w=3, seed=sd + 1))
    for k in range(5):
        a = ang + k * 2 * math.pi / 5
        s.append(line([(cx + math.cos(a) * r * .14, cy + math.sin(a) * r * .14), (cx + math.cos(a) * r * .46, cy + math.sin(a) * r * .46)],
                      5, "#5c616b", taper=.1, wmin=.8, seed=sd + 2 + k))
    s.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .12)}" fill="#3a3d44"/>')
    return "".join(s)


def bus(x, bottom, t, travel):
    """Двухэтажный автобус, перед — слева (едет влево). x — передний край, длина 800, высота 480."""
    L, Hh = 800, 480
    rock = 2.0 * math.sin(t * 9) + 1.2 * math.sin(t * 13.7)
    y0 = bottom - 46 + rock * .5
    top = y0 - Hh
    s = []
    s.append(blob(ellipse_pts(x + L / 2, bottom + 4, L * .52, 18, 16), "#2a2c33", .45, blur(8)))
    inner = ""
    inner += blob([(x, y0 - 120), (x + L, y0 - 120), (x + L, y0), (x, y0)], RED_SH, .9)
    # окна верх/низ
    for row, (wy0, wy1) in enumerate([(top + 46, top + 176), (top + 250, top + 370)]):
        inner += f'<rect x="{f(x + 30)}" y="{f(wy0)}" width="{f(L - 60)}" height="{f(wy1 - wy0)}" fill="#2a3442" rx="10"/>'
        for k in range(6):
            px = x + 40 + k * (L - 80) / 6
            if row == 1 and k == 1:
                continue          # дверь
            inner += f'<rect x="{f(px + 6)}" y="{f(wy0 + 8)}" width="{f((L - 80) / 6 - 12)}" height="{f(wy1 - wy0 - 16)}" fill="#8fb1c8" rx="6"/>'
            inner += blob([(px + 12, wy1 - 20), (px + 60, wy0 + 12), (px + 84, wy0 + 12), (px + 30, wy1 - 12)], "#d6e6f0", .75)
    # дверь
    dx = x + 40 + (L - 80) / 6
    inner += f'<rect x="{f(dx + 6)}" y="{f(top + 250)}" width="{f((L - 80) / 6 - 12)}" height="{f(Hh - 250 - 4)}" fill="#2a3442" rx="6"/>'
    inner += f'<rect x="{f(dx + 14)}" y="{f(top + 262)}" width="{f((L - 80) / 12 - 14)}" height="{f(Hh - 290)}" fill="#8fb1c8" rx="4"/>'
    inner += f'<rect x="{f(dx + (L - 80) / 12 + 2)}" y="{f(top + 262)}" width="{f((L - 80) / 12 - 14)}" height="{f(Hh - 290)}" fill="#8fb1c8" rx="4"/>'
    # пояс между этажами, юбка
    inner += f'<rect x="{f(x)}" y="{f(top + 196)}" width="{L}" height="16" fill="{RED_SH}"/>'
    inner += f'<rect x="{f(x)}" y="{f(y0 - 40)}" width="{L}" height="40" fill="#2a2c33"/>'
    # табло маршрута — пустое
    inner += f'<rect x="{f(x + 10)}" y="{f(top + 8)}" width="150" height="30" rx="5" fill="#1f2228"/>'
    inner += f'<rect x="{f(x + 18)}" y="{f(top + 14)}" width="134" height="18" rx="3" fill="#3a3f48"/>'
    # фары
    inner += f'<circle cx="{f(x + 26)}" cy="{f(y0 - 66)}" r="14" fill="#fff4c8"/>'
    body = [(x + 18, top, 1), (x + L - 10, top, 1), (x + L, top + 14), (x + L, y0, 1), (x, y0, 1), (x, top + 22), (x + 6, top + 6)]
    s.append(shape(body, RED, inner, w=5.4, seed=700))
    # блик по крыше
    s.append(line([(x + 40, top + 22), (x + L - 40, top + 22)], 5, "#ff8a7a", taper=.2, seed=701, op=.85))
    # колёса с арками
    ang = -travel / 48.0
    for k, wx in enumerate((x + 150, x + L - 170)):
        s.append(f'<path d="M{f(wx - 66)} {f(y0)} A66 66 0 0 1 {f(wx + 66)} {f(y0)} Z" fill="#1a1c22"/>')
        s.append(wheel(wx, bottom - 46 + 2, 48, ang, 710 + k * 10))
    return "".join(s)


# ───────────────────────── люди
PEOPLE = [
    # задний ряд (мельче, выше по тротуару)
    dict(spec=dict(skin="#d9a07a", hair="bun", hair_c="#5a3020", top="#3a9a9a", track="#f4f1ea", low="#24484a", shoes="#f2f2f2", face=.1, zip=True, h=.9),
         x=470, y=1250, sc=.7, act="jog", ph=2.4),
    dict(spec=dict(skin="#f0c4a0", hair="short", hair_c="#5a3a26", top="#2d55a8", track="#f4f1ea", low="#1f2b52", shoes="#f2f2f2", face=-.2, stubble=True,
                   collar="#f0ece0", h=1.03), x=700, y=1250, sc=.7, act="stretch", ph=0.6),
    dict(spec=dict(skin="#c98e6a", hair="short", hair_c="#2a1a14", top="#e07a2e", track="#f4f1ea", low="#3a3040", shoes="#2a3040", face=.5, cap="#2a2f3a", h=1.0),
         x=930, y=1256, sc=.7, act="hips", ph=1.4),
    # передний ряд
    dict(spec=dict(skin="#e8b896", hair="bald", hair_c="#9a9aa6", top="#6c7486", track="#f4f1ea", low="#3a3f4c", shoes="#2a3040", face=.45, glasses=True,
                   mustache=True, bw=1.1, zip=True), x=330, y=1312, sc=.8, act="hips", ph=2.0),
    dict(spec=dict(skin="#f4d0b4", hair="ponytail", hair_c="#3a2418", top="#d9467a", track="#f4f1ea", low="#2a2a3a", shoes="#f2f2f2", face=.35, zip=True, h=.95),
         x=580, y=1318, sc=.8, act="jog", ph=0.0),
    dict(spec=dict(skin="#8a5a3c", hair="curly", hair_c="#2a1a14", top="#2f8a5a", track="#f4f1ea", low="#1f3a2c", shoes="#f2f2f2", face=-.4, zip=True, h=.93),
         x=830, y=1310, sc=.8, act="reach", ph=1.0),
]


def pose_for(p, t):
    a = p["act"]
    ph = p["ph"]
    if a == "jog":
        return dict(walk=t * 9.5 + ph, mouth="smile", look=(0.2, 0.0), blink=1.0 if (t * 0.9 + ph) % 3 < 0.08 else 0.0)
    if a == "reach":     # тянется вверх-в сторону, качаясь
        k = math.sin(t * 3 + ph)
        return dict(arms={"L": (-172 + 6 * k, -6), "R": (150 + 12 * k, 10)}, legs={"L": (4, 0), "R": (-4, 0)}, head_tilt=-6 * k,
                    mouth="smile", look=(0, -.4))
    if a == "sway":      # руки в стороны, круговые
        k = math.sin(t * 4 + ph)
        return dict(arms={"L": (-80 + 30 * k, -20), "R": (80 - 30 * k, 20)}, legs={"L": (-8, 0), "R": (8, 0)}, head_tilt=3 * k,
                    mouth="flat", look=(0.3, 0))
    if a == "hips":      # руки в боки, переминается, кивает
        k = math.sin(t * 3.2 + ph)
        return dict(arms={"L": (-42, 104), "R": (42, -104)}, legs={"L": (-6 + 6 * k, 0), "R": (6 + 6 * k, 0)}, head_tilt=4 * k,
                    mouth="smile", look=(.3 * (1 if k > 0 else -1), 0))
    if a == "stretch":   # обе руки вверх, на носках
        k = math.sin(t * 3.6 + ph)
        return dict(arms={"L": (-170 + 6 * k, 0), "R": (170 - 6 * k, 0)}, legs={"L": (-4, 0), "R": (4, 0)}, head_tilt=4 * k,
                    mouth="o" if k > .6 else "smile", look=(0, -.3))
    return {}


def people(t):
    s = []
    for i, p in enumerate(PEOPLE):
        pose = pose_for(p, t)
        bob = 0.0
        if p["act"] == "stretch":
            bob = -10 * (0.5 + 0.5 * math.sin(t * 3.6 + p["ph"]))
        s.append(blob(ellipse_pts(p["x"] + 14, p["y"] + 10, 120 * p["sc"], 18 * p["sc"], 14), "#8d8578", .55, blur(5)))
        s.append(person.draw(p["spec"], pose, p["x"], p["y"] + bob, p["sc"], sd=1000 + i * 100))
    return "".join(s)


def postbox(x, y):
    """Красный почтовый столб-«пиллар» на переднем плане: x — центр, y — низ; щель и табличка без букв."""
    s = [blob(ellipse_pts(x + 40, y + 6, 120, 16, 14), "#7d7468", .5, blur(6))]
    w, h = 120, 330
    body_in = blob(rect_pts(x + w * .2, y - h, x + w * .5, y), RED_SH, .9)
    body_in += f'<rect x="{f(x - w * .5)}" y="{f(y - h + 60)}" width="{w}" height="26" fill="#1f2228"/>'
    body_in += f'<rect x="{f(x - 40)}" y="{f(y - h + 110)}" width="80" height="12" rx="4" fill="#1a1c22"/>'
    body_in += shape(rect_pts(x - 34, y - h + 150, x + 34, y - h + 200, 4), "#f4f0e2", "", w=2.6, seed=652)
    body_in += blob(rect_pts(x - w * .38, y - h + 20, x - w * .26, y - 20), "#ff8a7a", .6)
    s.append(shape(rect_pts(x - w / 2, y - h, x + w / 2, y), RED, body_in, w=5, seed=650))
    s.append(shape(rect_pts(x - w / 2 - 10, y - 26, x + w / 2 + 10, y), "#1f2228", "", w=4, seed=653))
    cap = [(x - w / 2 - 10, y - h + 4, 1), (x - w / 2 - 6, y - h - 20), (x, y - h - 44), (x + w / 2 + 6, y - h - 20), (x + w / 2 + 10, y - h + 4, 1)]
    s.append(shape(cap, RED, blob([(x, y - h - 44), (x + w / 2 + 6, y - h - 20), (x + w / 2 + 10, y - h + 4), (x + 10, y - h + 4)], RED_SH, .9),
                   w=4.6, seed=654))
    return "".join(s)


def leaves(t):
    s = []
    rs = np.random.RandomState(9)
    for k in range(7):
        x0, y0 = rs.uniform(-100, 1200), rs.uniform(-100, 700)
        x = x0 - 120 * (t - 13.68) + 30 * math.sin(t * 2 + k)
        y = y0 + 220 * (t - 13.68)
        r = rs.uniform(-1, 1) * 120 + 200 * t
        col = ["#e0a23a", "#d9682e", "#c9a23a"][k % 3]
        pts = [(x - 16, y), (x, y - 8), (x + 16, y), (x, y + 8)]
        s.append(f'<g transform="rotate({f(r)} {f(x)} {f(y)})">{shape(pts, col, "", w=2.4, seed=670 + k)}</g>')
    return "".join(s)


def s09(t):
    travel = 560 * (t - 13.68)
    xb = 640 - travel
    art = _ST["street"] + bus(xb, ROAD1 - 10, t, travel) + leaves(t) + booth(10, 1300) + people(t) + postbox(1000, 1660)
    # утренний свет слева
    g = _ST["light"]
    art += f'<rect x="-500" y="-600" width="{W + 1000}" height="{H + 1200}" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    u = clamp((t - 13.68) / 2.92)
    cm = cam(540 + 60 * (0.3 * u + 0.7 * ease_io(u)), 980, 1.05 + 0.04 * u, 0.4 - 0.8 * u)
    return art, cm


def frame(sid, t):
    if not _ST:
        _ST["street"] = street_static()
        _ST["light"] = rad_grad([(0, "#ffd9a0", .35), (.5, "#ffcf90", .12), (1, "#ffcf90", 0)], 80, 300, 1200, 1000)
        lib.static_done()
    lib.dyn_begin()
    art, cm = s09(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#d9d4ca"/><g transform="{cm}">{art}</g>')
