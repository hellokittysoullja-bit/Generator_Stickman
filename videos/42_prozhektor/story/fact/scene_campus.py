"""Сцена «кампус» рилса 42 (s10, 16.9–19.4): «В Корнелле студентов отправляли…». Вечер: старое университетское
здание из серого камня с квадратной часовой башней и острой крышей, окна горят тёплым, фонари, первые звёзды, месяц.
С первого кадра: камера наезжает, звёзды мерцают, фонари дрожат, студенты идут к двери. На «Корнелле» (17.32) у дорожки
из земли выскакивает вывеска «КОРНЕЛЛ» (буквы кодом) со вспышкой; камера доезжает к ней. Всё — функция времени ролика t."""
import math

import numpy as np

import lib
import person
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad,
                 rect_pts, shape, svg)

_ST = {}
KORN = 17.32
GROUND = 1150
STONE, STONE_SH, STONE_DK = "#a9a39a", "#8a847d", "#6c675f"
ROOF, ROOF_SH = "#4a4f63", "#363a4b"
LIT, LIT2 = "#ffd27a", "#ffb84a"
TX = 540                          # ось башни


def sky():
    s = []
    g = lin_grad([(0, "#141a3e", 1), (.45, "#3a2f6a", 1), (.75, "#9a4f78", 1), (1, "#f09a5c", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-800" y="-900" width="{W + 1600}" height="{GROUND + 900}" fill="url(#{g})"/>')
    s.append(shape([(860, 150), (900, 120), (944, 128), (912, 140), (896, 170), (906, 206), (938, 222), (896, 222), (862, 196)],
                   "#fff4cf", "", w=3.4, seed=6001))       # месяц
    g2 = rad_grad([(0, "#fff4cf", .35), (1, "#fff4cf", 0)], 900, 175, 160, 160)
    s.append(f'<rect x="700" y="0" width="400" height="360" fill="url(#{g2})"/>')
    return "".join(s)


def stars(t):
    rs = np.random.RandomState(21)
    s = []
    for k in range(34):
        x, y = rs.uniform(-200, 1280), rs.uniform(-100, 560)
        if abs(x - TX) < 150 and y > 40:
            continue
        ph = rs.uniform(0, 6.3)
        r = rs.uniform(2, 4.5) * (0.7 + 0.5 * (0.5 + 0.5 * math.sin(t * 5 + ph)))
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#fff6d8"/>')
    return "".join(s)


def window(x, y, w, h, sd, lit=True, arch=True, t=0.0):
    r = w / 2
    pts = [(x - r, y + h, 1)]
    if arch:
        for k in range(9):
            a = math.pi + math.pi * k / 8
            pts.append((x + r * math.cos(a), y + r + r * math.sin(a) * 1.25))
    else:
        pts += [(x - r, y, 1), (x + r, y, 1)]
    pts.append((x + r, y + h, 1))
    col = mix(LIT, "#ffe6a8", 0.5 + 0.5 * math.sin(t * 3 + sd)) if lit else "#3d4466"
    inner = blob(rect_pts(x - r, y + h * .6, x + r, y + h), LIT2 if lit else "#30365a", .8)
    inner += line([(x, y), (x, y + h)], 3, STONE_DK, taper=.05, wmin=.9, seed=sd + 1)
    inner += line([(x - r, y + h * .5), (x + r, y + h * .5)], 3, STONE_DK, taper=.05, wmin=.9, seed=sd + 2)
    return shape(pts, col, inner, w=3.4, seed=sd)


def glow(x, y, r, col=LIT, a=.45):
    g = rad_grad([(0, col, a), (1, col, 0)], x, y, r, r)
    return f'<rect x="{f(x - r)}" y="{f(y - r)}" width="{f(2 * r)}" height="{f(2 * r)}" fill="url(#{g})"/>'


def stone_lines(x0, y0, x1, y1, sd):
    s = ""
    for k, y in enumerate(np.arange(y0 + 40, y1, 46)):
        s += line([(x0, y), (x1, y + 2)], 1.8, STONE_DK, taper=.1, wmin=.6, seed=sd + k, op=.35)
        off = 30 if k % 2 else 0
        for j, x in enumerate(np.arange(x0 + 20 + off, x1, 90)):
            s += line([(x, y - 46), (x, y)], 1.6, STONE_DK, taper=.1, wmin=.6, seed=sd + 100 + k * 20 + j, op=.25)
    return s


def wing(x0, x1, top, sd, t):
    s = []
    inner = blob(rect_pts(x0, GROUND - 60, x1, GROUND + 4), STONE_SH, .8) + stone_lines(x0, top, x1, GROUND, sd + 300)
    s.append(shape(rect_pts(x0, top, x1, GROUND + 4), STONE, inner, w=4.6, seed=sd))
    # крыша-скат и слуховые окна
    s.append(shape([(x0 - 14, top + 4, 1), (x0 + 40, top - 110, 1), (x1 - 40, top - 110, 1), (x1 + 14, top + 4, 1)], ROOF,
                   blob([((x0 + x1) / 2, top - 110), (x1 - 40, top - 110), (x1 + 14, top + 4), ((x0 + x1) / 2, top + 4)], ROOF_SH, .9), w=4.4, seed=sd + 1))
    n = max(2, int((x1 - x0) / 120))
    for r, (yy, hh) in enumerate(((top + 50, 120), (top + 230, 140))):
        for k in range(n):
            x = x0 + (x1 - x0) * (k + .5) / n
            lit = (k * 3 + r + sd) % 4 != 0
            if lit:
                s.append(glow(x, yy + hh / 2, 90, LIT, .35))
            s.append(window(x, yy, 54, hh, sd + 20 + r * 10 + k, lit, True, t))
    return "".join(s)


def tower(t):
    s = []
    x0, x1, top = TX - 120, TX + 120, 300
    inner = blob(rect_pts(TX + 50, top, x1, GROUND + 4), STONE_SH, .85) + stone_lines(x0, top, x1, GROUND, 6400)
    s.append(shape(rect_pts(x0, top, x1, GROUND + 4), STONE, inner, w=5, seed=6401))
    # верх: карниз с зубцами и острая крыша с флюгером
    s.append(shape(rect_pts(x0 - 18, top - 26, x1 + 18, top + 8, 3), STONE, blob(rect_pts(x0 - 18, top - 4, x1 + 18, top + 8), STONE_SH, .9), w=4.4, seed=6402))
    for k in range(5):
        xx = x0 - 18 + k * 66
        s.append(shape(rect_pts(xx, top - 56, xx + 30, top - 24, 2), STONE, "", w=3.4, seed=6410 + k))
    s.append(shape([(x0 - 6, top - 56, 1), (TX, top - 290, 1), (x1 + 6, top - 56, 1)], ROOF,
                   blob([(TX, top - 290), (x1 + 6, top - 56), (TX + 10, top - 56)], ROOF_SH, .9), w=4.8, seed=6420))
    s.append(line([(TX, top - 290), (TX, top - 350)], 5, INK, taper=.1, wmin=.9, seed=6421))
    fl = 18 * math.sin(t * 1.5)
    s.append(shape([(TX, top - 350, 1), (TX + 40, top - 340 + fl * .2), (TX, top - 326, 1)], "#d8b04a", "", w=3, seed=6422))
    # часы без цифр: метки и стрелки
    cy = top + 130
    s.append(glow(TX, cy, 130, "#fff1c0", .4))
    s.append(shape(ellipse_pts(TX, cy, 82, 82, 28), "#fbf3dc", blob(ellipse_pts(TX + 14, cy + 10, 70, 70, 20), "#e8dcbc", .7), w=5, seed=6430))
    for k in range(12):
        a = math.radians(k * 30)
        s.append(line([(TX + 62 * math.sin(a), cy - 62 * math.cos(a)), (TX + 72 * math.sin(a), cy - 72 * math.cos(a))], 4, INK, taper=.1, wmin=.8, seed=6440 + k))
    a1 = math.radians(150 + (t - 16.9) * 40)
    a2 = math.radians(225 + (t - 16.9) * 4)
    s.append(line([(TX, cy), (TX + 54 * math.sin(a1), cy - 54 * math.cos(a1))], 5, INK, taper=.3, seed=6460))
    s.append(line([(TX, cy), (TX + 36 * math.sin(a2), cy - 36 * math.cos(a2))], 8, INK, taper=.3, seed=6461))
    s.append(f'<circle cx="{TX}" cy="{f(cy)}" r="6" fill="{INK}"/>')
    # высокие окна башни
    for k, yy in enumerate((cy + 130,)):
        s.append(glow(TX, yy + 70, 110, LIT, .35))
        s.append(window(TX, yy, 70, 150, 6470 + k * 5, True, True, t))
    # вход: стрельчатая арка, дверь открыта, тёплый свет изнутри
    ay0, ay1 = GROUND - 230, GROUND + 2
    arch = [(TX - 70, ay1, 1), (TX - 70, ay0 + 70), (TX - 50, ay0 + 22), (TX, ay0, 1), (TX + 50, ay0 + 22), (TX + 70, ay0 + 70), (TX + 70, ay1, 1)]
    s.append(shape([(x * 1.0 + (x - TX) * .25, y - 16) for x, y, *_ in arch], STONE_SH, "", w=4.4, seed=6480))
    s.append(glow(TX, GROUND - 80, 200, LIT, .55))
    s.append(shape(arch, "#ffe3a0", blob(rect_pts(TX - 70, GROUND - 90, TX + 70, ay1), "#ffcf7a", .9), w=4.4, seed=6481))
    s.append(shape([(TX - 70, ay1, 1), (TX - 70, ay0 + 70), (TX - 40, ay0 + 44), (TX - 40, ay1 + 10, 1)], "#6e4123", "", w=3.4, seed=6482))
    s.append(shape([(TX + 70, ay1, 1), (TX + 70, ay0 + 70), (TX + 40, ay0 + 44), (TX + 40, ay1 + 10, 1)], "#6e4123", "", w=3.4, seed=6483))
    return "".join(s)


def ground():
    s = []
    g = lin_grad([(0, "#2f5a3e", 1), (1, "#1d3a2a", 1)], 0, 0, 0, 1)
    s.append(shape(rect_pts(-800, GROUND, W + 800, H + 600), f"url(#{g})", "", w=4.4, seed=6500))
    s.append(shape([(TX - 70, GROUND + 2, 1), (TX + 70, GROUND + 2, 1), (TX + 340, H + 300, 1), (TX - 340, H + 300, 1)], "#c9b48c",
                   blob([(TX, GROUND), (TX + 70, GROUND), (TX + 340, H + 300), (TX + 80, H + 300)], "#ad9a74", .8), w=4, seed=6501))
    g2 = rad_grad([(0, "#ffd27a", .4), (1, "#ffd27a", 0)], TX, GROUND + 40, 260, 120)
    s.append(f'<rect x="{TX - 260}" y="{GROUND - 80}" width="520" height="240" fill="url(#{g2})"/>')
    return "".join(s)


def tree(x, y, h, t, sd):
    sway = 2.5 * math.sin(t * 1.2 + sd)
    s = [blob(ellipse_pts(x + 14, y + 4, h * .3, h * .05, 14), "#0f2018", .5, blur(5))]
    trunk = [(x - 14, y, 1), (x - 9, y - h * .45), (x + sway, y - h * .62), (x + 11 + sway, y - h * .45), (x + 16, y, 1)]
    s.append(shape(trunk, "#5a3e2a", "", w=4, seed=sd))
    cx, cy = x + sway * 2, y - h * .72
    for k, (dx, dy, r, c) in enumerate([(-h * .2, h * .08, h * .22, "#2f5a44"), (h * .2, h * .06, h * .21, "#2a5040"), (0, -h * .12, h * .27, "#356450")]):
        pts = []
        for i in range(16):
            a = 2 * math.pi * i / 16
            rr = 1 + .1 * math.sin(4 * a + sd + k)
            pts.append((cx + dx + r * math.cos(a) * rr, cy + dy + r * .85 * math.sin(a) * rr))
        s.append(shape(pts, c, blob(ellipse_pts(cx + dx + r * .3, cy + dy + r * .35, r * .7, r * .45, 12), "#1f4030", .85), w=4, seed=sd + 20 + k))
    return "".join(s)


def lamp(x, t, sd):
    y = GROUND + 120
    fl = 0.9 + 0.1 * math.sin(t * 11 + sd) * math.sin(t * 7)
    s = [glow(x, y - 300, 170 * fl, "#ffe1a0", .5)]
    s.append(shape(rect_pts(x - 6, y - 290, x + 6, y), "#2a2d3a", "", w=3, seed=sd))
    s.append(shape([(x - 26, y - 300, 1), (x + 26, y - 300, 1), (x + 18, y - 350, 1), (x - 18, y - 350, 1)], "#fff0b8", "", w=3.6, seed=sd + 1))
    s.append(shape([(x - 32, y - 350, 1), (x + 32, y - 350, 1), (x, y - 378, 1)], "#2a2d3a", "", w=3.4, seed=sd + 2))
    return "".join(s)


STUD = [
    dict(skin="#f0c4a0", hair="short", hair_c="#5a3a26", top="#c94a3f", low="#2a2f4a", face=.75),
    dict(skin="#8a5a3c", hair="curly", hair_c="#2a1a14", top="#3a8ac8", low="#2a2a3a", face=.75),
    dict(skin="#f4d0b4", hair="ponytail", hair_c="#c8622a", top="#e8b23a", low="#24384a", face=-.75),
]


def students(t):
    s = []
    for i, (x0, v, y, sc) in enumerate([(120, 120, GROUND + 70, .36), (-60, 140, GROUND + 110, .4), (980, -125, GROUND + 90, .38)]):
        x = x0 + v * (t - 16.9)
        ph = (t - 16.9) * 8.5 + i * 1.7
        s.append(blob(ellipse_pts(x, y + 3, 50, 8, 12), "#0f2018", .5, blur(4)))
        s.append(person.draw(STUD[i], {"walk": ph, "look": (0.6 if v > 0 else -0.6, 0), "mouth": "smile", "curl": {"L": .5, "R": .5}},
                             x, y, sc, sd=6600 + i * 100))
    return "".join(s)


SIGN = (540, 870)


def sign(t):
    e = t - (KORN - 0.06)
    if e < 0:
        return ""
    x, y = SIGN
    rise = back_out(clamp(e / 0.3), 2.0)
    wob = 4 * math.exp(-e * 5) * math.sin(e * 22)
    w, h = 400, 120
    s = []
    s.append(rays(0, 0, e, 6700))
    for k, px in enumerate((-140, 140)):          # кронштейны
        s.append(shape(rect_pts(px - 8, -h / 2 - 40, px + 8, -h / 2), "#3a3040", "", w=3, seed=6710 + k))
    inner = blob(rect_pts(-w / 2, 10, w / 2, h / 2), "#6e1f24", .9) + line([(-w / 2 + 18, -h / 2 + 14), (w / 2 - 18, -h / 2 + 14)], 3, "#c9a36a", taper=.1, wmin=.8, seed=6721, op=.9)
    board = '<g>' + shape(rect_pts(-w / 2, -h / 2, w / 2, h / 2, 10), "#8f2a2f", inner, w=5, seed=6720)
    board += shape(rect_pts(-w / 2 - 10, -h / 2 - 16, w / 2 + 10, -h / 2 + 2, 6), "#c9a36a", "", w=3.6, seed=6722)
    board += (f'<text x="0" y="22" text-anchor="middle" font-family="IDB" font-weight="900" font-size="66" fill="#fbf1d8" '
              f'letter-spacing="2">КОРНЕЛЛ</text>') + "</g>"
    s.append(board)
    # пятно света снизу
    g = rad_grad([(0, "#ffe1a0", .5), (1, "#ffe1a0", 0)], 0, 0, 320, 190)
    sp = f'<rect x="-320" y="-190" width="640" height="380" fill="url(#{g})"/>'
    return (f'<g transform="translate({f(x)} {f(y)})">{sp}<g transform="scale({f(max(rise, .01))}) rotate({f(wob)} 0 0)">'
            + "".join(s) + "</g></g>")


def rays(x, y, e, sd, r=250, n=12, dur=0.45):
    if e < 0 or e > dur:
        return ""
    u = e / dur
    s = []
    for k in range(n):
        a = k * 2 * math.pi / n + .2
        r0 = r + 110 * ease_out(u)
        L = 70 * (1 - u)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0 * .7), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L) * .7)],
                      11 * (1 - .5 * u), "#ffe27a", taper=.5, seed=sd + k))
    return "".join(s)


def s10(t):
    s = [_ST["sky"], stars(t), _ST["bld_l"], _ST["bld_r"], tower(t), _ST["ground"],
         tree(-30, GROUND + 40, 520, t, 6800), tree(1110, GROUND + 50, 560, t, 6830),
         lamp(150, t, 6860), lamp(930, t, 6870), students(t), sign(t)]
    # камера: наезд с первого кадра, к вывеске после «Корнелле»
    u = ease_out(clamp((t - 16.9) / 0.5), 3)
    v = ease_io(clamp((t - KORN) / 0.7))
    sc = 1.0 + 0.1 * u + 0.42 * v + 0.03 * clamp((t - 18.0) / 1.4)
    cx = 540
    cy = 760 + 60 * u + (900 - 820) * v
    rot = -1.5 * (1 - u) + 0.6 * v + 0.3 * math.sin(t * 1.3)
    e = t - KORN
    if e > 0:
        sc *= 1 + 0.03 * math.exp(-e * 8) * math.sin(min(e * 14, math.pi))
    return cam(cx, cy, sc, rot), "".join(s)


def build_static():
    _ST["sky"] = sky()
    _ST["bld_l"] = wing(-260, TX - 110, 560, 6100, 0.0)
    _ST["bld_r"] = wing(TX + 110, 1340, 560, 6200, 0.0)
    _ST["ground"] = ground()
    lib.static_done()


def frame(sid, t):
    if not _ST:
        build_static()
    lib.dyn_begin()
    tr, body = s10(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1d3a2a"/><g transform="{tr}">{body}</g>')
