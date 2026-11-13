"""Сцена clock (s01, хук): крупно электронные часы на тёмной полке ночью (слева — корешки книг, справа — край
растения в горшке). Красные сегментные цифры — кодом. Влёт камеры с кадра 0 (масштаб 1/1.4 → 1 за 0.22 с, перелёт 5 %,
поворот −3° с возвратом), на «полночь» (0.8) встаёт «00:00» с ударом камеры, потом минуты и часы бешено листаются к
«02:00» к концу клипа; свечение цифр мигает. Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
from lib import (DEFS, INK, W, H, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg)

MIDNIGHT = 0.80
RACE0, RACE1 = 1.00, 1.56
CX, CY = 540, 830                       # центр часов
BX0, BX1, BY0, BY1 = 112, 968, 470, 1030  # корпус
DX0, DX1, DY0, DY1 = 164, 916, 676, 968   # окно дисплея
SHELF = 1030
DW, DH, TH = 114, 210, 28                 # цифра: ширина, высота, толщина сегмента
SKEW = math.tan(math.radians(7))
LIT, LIT_HI, GHOST = "#ff2d22", "#ffb09a", "#3a0e12"
_ST = {}

SEGS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
        "8": "abcdefg", "9": "abcdfg"}


def seg_poly(name, ox, oy):
    """Шестиугольный сегмент цифры с наклоном (как у настоящего табло)."""
    g = TH * 0.55
    h2 = TH / 2
    mid = DH / 2
    if name in "agd":
        y = {"a": 0, "g": mid, "d": DH}[name]
        x0, x1 = g, DW - g
        pts = [(x0, y), (x0 + h2, y - h2), (x1 - h2, y - h2), (x1, y), (x1 - h2, y + h2), (x0 + h2, y + h2)]
    else:
        x = DW if name in "bc" else 0
        y0, y1 = (g, mid - g) if name in "bf" else (mid + g, DH - g)
        pts = [(x, y0), (x + h2, y0 + h2), (x + h2, y1 - h2), (x, y1), (x - h2, y1 - h2), (x - h2, y0 + h2)]
    return [(ox + px - (py - DH / 2) * SKEW, oy + py, 1) for px, py in pts]


def digit_x():
    gap, colon = 50, 60
    tot = 4 * DW + 2 * gap + colon + 2 * gap
    x0 = CX - tot / 2 + 6
    xs = [x0, x0 + DW + gap]
    cx = xs[1] + DW + gap + colon / 2
    xs += [cx + colon / 2 + gap, cx + colon / 2 + gap + DW + gap]
    return xs, cx


DXS, COLX = digit_x()
DTOP = (DY0 + DY1) / 2 - DH / 2


# ───────────────────────── что на табло
def shown(t):
    if t < MIDNIGHT:
        m = 23 * 60 + 57 + min(2, int(t / (MIDNIGHT / 3)))
    elif t < RACE0:
        m = 0
    elif t < RACE1:
        u = (t - RACE0) / (RACE1 - RACE0)
        m = int(round(120 * (u * u * (3 - 2 * u)) ** 0.9))
    else:
        m = 120
    m %= 24 * 60
    return f"{m // 60:02d}{m % 60:02d}"


def glow_k(t):
    """Яркость свечения: мигает; на «полночь» — вспышка; во время гонки — нервное мерцание."""
    rs = np.random.RandomState(int(t * 30 + 0.5) % 100000)
    k = 0.80 + 0.12 * math.sin(t * 23) + 0.08 * rs.uniform(-1, 1)
    if t >= MIDNIGHT:
        k += 0.55 * math.exp(-(t - MIDNIGHT) * 9)
    if RACE0 <= t < RACE1 + 0.05:
        k = 0.55 + 0.6 * rs.uniform(0, 1)
    if t >= RACE1:
        k += 0.5 * math.exp(-(t - RACE1) * 10)
    return clamp(k, 0.35, 1.4)


# ───────────────────────── статика
def wall():
    s = []
    lin_grad([(0, "#1d2140", 1), (.55, "#232a4e", 1), (1, "#1a1f3a", 1)], 0, 0, 0, 1, gid="gWallC")
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{SHELF + 600}" fill="url(#gWallC)"/>')
    # обои: редкий ромбик
    DEFS.append('<pattern id="pPaper" width="120" height="120" patternUnits="userSpaceOnUse">'
                '<path d="M60 18 L72 30 L60 42 L48 30Z M0 78 L12 90 L0 102 L-12 90Z M120 78 L132 90 L120 102 L108 90Z" fill="#2c345c" opacity=".55"/>'
                '</pattern>')
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{SHELF + 600}" fill="url(#pPaper)"/>')
    # лунный свет из окна — косой мягкий параллелограмм
    lin_grad([(0, "#6f86c8", .0), (.5, "#7b92d4", .30), (1, "#6f86c8", .0)], 0, 0, 1, 0, gid="gMoon")
    s.append(f'<path d="M-260 -200 L240 -200 L700 {SHELF} L200 {SHELF} Z" fill="url(#gMoon)" {blur(18)}/>')
    return "".join(s)


def shelf():
    s = []
    # верх полки и передняя кромка
    s.append(shape([(-600, SHELF - 6, 1), (W + 600, SHELF - 6, 1), (W + 600, SHELF + 22, 1), (-600, SHELF + 22, 1)], "#6b4a33",
                   blob(rect_pts(-600, SHELF + 8, W + 600, SHELF + 22), "#563a27"), w=4.6, seed=11))
    s.append(shape([(-600, SHELF + 22, 1), (W + 600, SHELF + 22, 1), (W + 600, SHELF + 92, 1), (-600, SHELF + 92, 1)], "#4b3222",
                   "".join(line([(-600, SHELF + 40 + k * 18), (W + 600, SHELF + 44 + k * 16)], 2.4, "#3a2618", seed=12 + k, op=.8) for k in range(3)),
                   w=4.8, seed=13))
    # тень под полкой и тёмная стена ниже
    lin_grad([(0, "#0e1022", 1), (1, "#161a33", 1)], 0, 0, 0, 1, gid="gUnder")
    s.append(f'<rect x="-600" y="{SHELF + 92}" width="{W + 1200}" height="1400" fill="url(#gUnder)"/>')
    # спинка дивана ниже полки — в темноте, сверху отсвет
    sofa = [(-600, SHELF + 640), (-200, SHELF + 540), (400, SHELF + 520), (900, SHELF + 530), (W + 600, SHELF + 600, 1), (W + 600, SHELF + 1400, 1), (-600, SHELF + 1400, 1)]
    s.append(shape(sofa, "#4a3a2a", blob([(-600, SHELF + 720), (W + 600, SHELF + 690), (W + 600, SHELF + 1400), (-600, SHELF + 1400)], "#352a1f", .9) +
                   line([(-300, SHELF + 590), (300, SHELF + 565), (900, SHELF + 575)], 5, "#6a543c", seed=19, op=.7), w=5.4, seed=18))
    # кронштейны
    for x in (40, 1040):
        s.append(shape([(x - 14, SHELF + 92, 1), (x + 14, SHELF + 92, 1), (x + 14, SHELF + 300, 1), (x - 14, SHELF + 240, 1)], "#2b2f45", "", w=4, seed=14 + x))
    return "".join(s)


def books():
    s = []
    rs = np.random.RandomState(21)
    x = -250
    cols = ["#6a3a4a", "#3c5a7a", "#7a6a3a", "#4a6a4c", "#5a4a7a", "#7a4a3a"]
    for k in range(7):
        w = rs.uniform(52, 78)
        h = rs.uniform(300, 420)
        lean = 0 if k < 6 else -10
        col = cols[k % len(cols)]
        pts = [(x, SHELF - 6, 1), (x + w, SHELF - 6, 1), (x + w + lean, SHELF - 6 - h, 1), (x + lean, SHELF - 6 - h, 1)]
        inner = blob([(x + w * .62, SHELF), (x + w, SHELF), (x + w + lean, SHELF - h - 10), (x + w * .62 + lean, SHELF - h - 10)], lib.mul(col, (.72, .72, .8)), .9)
        for j, yy in enumerate((0.12, 0.2, 0.84)):
            y = SHELF - 6 - h * (1 - yy)
            inner += line([(x + 4, y), (x + w - 4, y)], 4, lib.mul(col, (1.35, 1.3, 1.2)), taper=.1, wmin=.8, seed=30 + k * 3 + j, op=.8)
        s.append(shape(pts, col, inner, w=4.4, seed=40 + k))
        x += w + rs.uniform(0, 4)
    return "".join(s)


def clock_body():
    s = []
    # тень корпуса на полке
    s.append(blob(ellipse_pts(CX + 20, SHELF + 2, 470, 26, 16), "#0b0c18", .7, blur(10)))
    # ножки
    for x in (BX0 + 70, BX1 - 70):
        s.append(shape(rect_pts(x - 34, BY1 - 8, x + 34, SHELF - 4, 6), "#1b1a20", "", w=3.6, seed=50 + x))
    body = rect_pts(BX0, BY0, BX1, BY1, 46)
    inner = blob(rect_pts(BX0, BY0 + 470, BX1, BY1 + 10), "#1d1b22", .95)
    inner += blob([(BX1 - 60, BY0), (BX1 + 10, BY0), (BX1 + 10, BY1 + 10), (BX1 - 40, BY1 + 10)], "#18161c", .9)
    inner += line([(BX0 + 60, BY0 + 18), (BX1 - 80, BY0 + 18)], 7, "#5a5664", taper=.5, seed=52, op=.9)
    s.append(shape(body, "#2c2a33", inner, w=6.2, seed=53))
    # решётка динамика над табло
    for r in range(4):
        for c in range(22):
            x = BX0 + 150 + c * 26 + (13 if r % 2 else 0)
            y = BY0 + 70 + r * 26
            inner_d = blob(ellipse_pts(x, y, 6.5, 6.5, 8), "#141318")
            s.append(inner_d)
    s.append(line([(BX0 + 40, BY0 + 180), (BX1 - 40, BY0 + 180)], 3, "#1a1920", taper=.1, wmin=.9, seed=55, op=.9))
    # кнопки сверху
    for k, x in enumerate((BX0 + 160, BX0 + 260, BX1 - 200)):
        s.append(shape(rect_pts(x - 36, BY0 - 20, x + 36, BY0 + 6, 8), "#3b3844", line([(x - 24, BY0 - 12), (x + 22, BY0 - 12)], 4, "#6c6878", seed=60 + k, op=.8),
                       w=3.6, seed=61 + k))
    # окно дисплея
    win = rect_pts(DX0, DY0, DX1, DY1, 24)
    s.append(shape(rect_pts(DX0 - 14, DY0 - 14, DX1 + 14, DY1 + 14, 32), "#1a191e", "", w=3.6, seed=70))
    lin_grad([(0, "#1d080b", 1), (1, "#0f0406", 1)], 0, 0, 0, 1, gid="gDisp")
    s.append(f'<path d="{lib.fill_d(win)}" fill="url(#gDisp)"/>')
    # погасшие сегменты (видны слегка — как у настоящего табло)
    for ox in DXS:
        for n in "abcdefg":
            s.append(blob(seg_poly(n, ox, DTOP), GHOST))
    for dy in (-48, 48):
        s.append(blob(ellipse_pts(COLX - (dy * SKEW), (DY0 + DY1) / 2 + dy, 15, 15, 10), GHOST))
    # индикатор будильника справа внизу (точка)
    s.append(blob(ellipse_pts(DX1 - 40, DY1 - 30, 9, 9, 8), GHOST))
    return "".join(s)


def clock_glass():
    """Блик стекла и обводка окна — поверх цифр."""
    win = rect_pts(DX0, DY0, DX1, DY1, 24)
    c = lib.clip_of(win)
    s = [f'<g clip-path="url(#{c})">']
    s.append(blob([(DX0 + 40, DY0 - 10), (DX0 + 150, DY0 - 10), (DX0 + 40, DY1 + 10), (DX0 - 70, DY1 + 10)], "#ffffff", .06))
    s.append(blob([(DX0 + 190, DY0 - 10), (DX0 + 230, DY0 - 10), (DX0 + 120, DY1 + 10), (DX0 + 80, DY1 + 10)], "#ffffff", .045))
    s.append("</g>")
    s.append(f'<path d="{lib.ink_closed(win, 5, seed=71)}" fill="{INK}"/>')
    return "".join(s)


def cable():
    pts = [(BX1 - 40, BY1 - 40), (BX1 + 40, BY1 - 20), (BX1 + 60, SHELF - 8), (BX1 + 66, SHELF + 40), (BX1 + 56, SHELF + 200),
           (BX1 + 80, SHELF + 360)]
    return line(pts, 11, "#15141a", taper=.05, wmin=.9, seed=80) + line([(x - 2, y) for x, y in pts[2:]], 3, "#3a3844", taper=.3, seed=81, op=.8)


def build_static():
    if _ST:
        return _ST
    _ST["back"] = wall() + shelf() + books()
    _ST["clock"] = clock_body() + cable()
    _ST["glass"] = clock_glass()
    lib.static_done()
    return _ST


# ───────────────────────── живое
def plant(t):
    """Край растения справа: горшок и листья качаются от сквозняка."""
    s = []
    px, py = 1090, SHELF - 6
    pot = [(px - 150, py - 230, 1), (px + 150, py - 230, 1), (px + 120, py, 1), (px - 120, py, 1)]
    s.append(blob(ellipse_pts(px, py + 2, 150, 16, 12), "#0b0c18", .7, blur(6)))
    leaves = []
    for k, (a0, L, wd) in enumerate([(-150, 360, 70), (-125, 420, 80), (-105, 300, 62), (-165, 280, 56), (-85, 380, 66)]):
        a = math.radians(a0 + 4 * math.sin(t * 2.2 + k * 1.3))
        bx, by = px - 40 + k * 18, py - 220
        tip = (bx + math.cos(a) * L, by + math.sin(a) * L)
        nx, ny = -math.sin(a), math.cos(a)
        mid = (bx + math.cos(a) * L * .5, by + math.sin(a) * L * .5)
        pts = [(bx, by, 1), (mid[0] + nx * wd, mid[1] + ny * wd), (tip[0], tip[1], 1), (mid[0] - nx * wd * .8, mid[1] - ny * wd * .8)]
        col = "#2f6a4a" if k % 2 else "#3a7a52"
        inner = blob([(bx, by), (tip[0], tip[1]), (mid[0] - nx * wd * .8, mid[1] - ny * wd * .8)], "#24523a", .9)
        inner += line([(bx, by), (mid[0] + nx * 4, mid[1] + ny * 4), tip], 3.4, "#1f4632", seed=90 + k, op=.9)
        leaves.append(shape(pts, col, inner, w=4.4, seed=95 + k))
    s += leaves
    s.append(shape(pot, "#9a5a3a", blob([(px + 20, py - 230), (px + 150, py - 230), (px + 120, py), (px + 40, py)], "#7a4228", .9) +
                   blob(rect_pts(px - 160, py - 236, px + 160, py - 200), "#b06a44"), w=5, seed=99))
    s.append(shape(rect_pts(px - 162, py - 244, px + 162, py - 206, 8), "#a8603e", "", w=4.4, seed=100))
    return "".join(s)


def digits(t):
    txt = shown(t)
    k = glow_k(t)
    lit, core = [], []
    for ch, ox in zip(txt, DXS):
        for n in SEGS[ch]:
            p = seg_poly(n, ox, DTOP)
            lit.append(p)
    colon_on = (t < MIDNIGHT) or (RACE0 <= t < RACE1) or (int((t - MIDNIGHT) * 4) % 2 == 0)
    dots = []
    if colon_on:
        for dy in (-48, 48):
            dots.append(ellipse_pts(COLX - (dy * SKEW), (DY0 + DY1) / 2 + dy, 15, 15, 10))
    s = []
    allp = lit + dots
    # свечение: две ступени размытия (мерцает)
    g1 = "".join(blob(p, "#ff2a1a") for p in allp)
    s.append(f'<g opacity="{clamp(0.55 * k, 0, 1):.3f}" {blur(26)}>{g1}</g>')
    s.append(f'<g opacity="{clamp(0.75 * k, 0, 1):.3f}" {blur(9)}>{g1}</g>')
    # сами сегменты: яркое ядро со светлой серединой
    for p in allp:
        s.append(blob(p, LIT))
    for ch, ox in zip(txt, DXS):
        for n in SEGS[ch]:
            P = seg_poly(n, ox, DTOP)
            a, b = P[0], P[3]
            s.append(line([(a[0] + (b[0] - a[0]) * .18, a[1] + (b[1] - a[1]) * .18), (a[0] + (b[0] - a[0]) * .82, a[1] + (b[1] - a[1]) * .82)],
                          7, LIT_HI, taper=.6, wmin=.3, seed=7, op=clamp(.55 + .35 * (k - .8), .3, .95)))
    # индикатор будильника горит
    s.append(blob(ellipse_pts(DX1 - 40, DY1 - 30, 9, 9, 8), LIT))
    return "".join(s)


def room_glow(t):
    """Красный отсвет на стене и полке — мигает вместе с цифрами."""
    k = glow_k(t)
    g = rad_grad([(0, "#ff3a2a", .55), (.45, "#c41e1e", .22), (1, "#c41e1e", 0)], CX, CY + 40, 760, 560)
    g2 = rad_grad([(0, "#ff5a3a", .6), (1, "#ff5a3a", 0)], CX, SHELF + 4, 560, 60)
    return (f'<rect x="-600" y="-200" width="{W + 1200}" height="{SHELF + 300}" fill="url(#{g})" opacity="{clamp(.55 * k, 0, 1):.3f}" style="mix-blend-mode:screen"/>'
            f'<rect x="-600" y="{SHELF - 60}" width="{W + 1200}" height="140" fill="url(#{g2})" opacity="{clamp(.5 * k, 0, 1):.3f}" style="mix-blend-mode:screen"/>')


def pop_lines(t):
    """На «полночь» — короткие штрихи-«дзынь» из-за часов."""
    e = t - MIDNIGHT
    if e < 0 or e > 0.4:
        return ""
    s = []
    for k in range(9):
        a = math.pi + k * math.pi / 8
        a = -math.pi / 2 + (k - 4) * 0.33
        r0 = 470 + 180 * ease_out(e / .4)
        L = 70 * (1 - e / .4)
        x0, y0 = CX + math.cos(a) * r0, CY - 40 + math.sin(a) * r0 * .7
        s.append(line([(x0, y0), (x0 + math.cos(a) * L, y0 + math.sin(a) * L * .7)], 9, "#ff7a5a", taper=.5, seed=110 + k))
    return "".join(s)


def camera(t):
    # влёт: 1/1.4 → 1.05 (перелёт) за 0.22 с, затухающий возврат к 1; поворот −3° → +0.8° → 0
    if t < 0.22:
        u = ease_out(t / 0.22, 2.4)
        k = 1 / 1.4 + (1.05 - 1 / 1.4) * u
        rot = -3.0 + 3.8 * u
    else:
        e = t - 0.22
        k = 1 + 0.05 * math.exp(-e * 9) * math.cos(e * 15)
        rot = 0.8 * math.exp(-e * 8) * math.cos(e * 13)
    # удар на «полночь» и медленный наезд во время гонки
    hit = 0.0
    shx = shy = 0.0
    if t >= MIDNIGHT:
        e = t - MIDNIGHT
        hit = 0.07 * math.exp(-e * 10) * math.cos(e * 22)
        shx = 14 * math.exp(-e * 12) * math.sin(e * 70)
        shy = 9 * math.exp(-e * 12) * math.sin(e * 55 + 1)
    push = 0.10 * ease_io(clamp((t - 0.25) / 1.43))
    jit = 0.0
    if RACE0 <= t < RACE1:
        jit = 3 * math.sin(t * 90)
    s = 1.12 * (k + hit + push)
    return cam(CX + shx + jit, CY + 40 + shy, s, rot)


def frame(sid, t):
    st = build_static()
    lib.dyn_begin()
    art = st["back"] + room_glow(t) + plant(t) + st["clock"] + digits(t) + st["glass"] + pop_lines(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1a1f3a"/><g transform="{camera(t)}">{art}</g>')
