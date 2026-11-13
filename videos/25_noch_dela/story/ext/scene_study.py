"""Сцена study (s07, s08, s09) — опыт Бейлорского университета (Техас), без букв и гербов.
s07: ночной кирпичный корпус университета (тот же, что в рилсе 24, перекрашен в ночь) под звёздным небом, кактусы,
     окна загораются одно за другим; наезд.
s08: комната лаборатории сна: человек сидит в кровати при ночнике и пишет список в блокноте (волнистые строки, не буквы);
     на тумбочке таймер, на «пять» (15.56) встаёт «5:00» и идёт вниз; на стене монитор сна с волной.
s09: две кровати: слева человек со списком засыпает первым на «быстрее» (18.56) — глаза дугами, Z; справа человек с
     листком галочек ворочается с открытыми глазами."""
import math

import numpy as np

import lib
import hand as penhand
import night_building as nb
import person
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, fill_d,
                 line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg)
from parts import sausage, sevenseg

FIVE = 15.56
ASLEEP = 18.56
_ST = {}

A = dict(skin="#e9c0a0", hair="short", hair_c="#5a3a26", face=0.0, brow_c="#3a2418")     # пишет список
B = dict(skin="#c99470", hair="bob", hair_c="#2a1a14", face=0.0, brow_c="#22140e")       # пишет про сделанное


# ═══════════════════════════════ s07: корпус ночью
BX = 200          # сдвиг корпуса рилса 24 к центру кадра


def sky07():
    s = []
    lin_grad([(0, "#0b1030", 1), (.55, "#1c2456", 1), (1, "#3a3a6e", 1)], 0, 0, 0, 1, gid="gSky7")
    s.append(f'<rect x="-600" y="-800" width="{W + 1200}" height="{nb.GBASE + 900}" fill="url(#gSky7)"/>')
    # млечная дымка
    s.append(blob([(-300, 260), (300, 40), (900, -200), (1400, -260), (1400, -120), (900, -40), (300, 200), (-300, 420)], "#5a5f9a", .22, blur(30)))
    # луна
    s.append(blob(ellipse_pts(860, 120, 150, 150, 18), "#fff4c8", .18, blur(30)))
    s.append(shape(ellipse_pts(860, 120, 78, 78, 18), "#f6efd2", blob(ellipse_pts(886, 140, 64, 64, 16), "#e2d8b4", .8) +
                   blob(ellipse_pts(838, 100, 13, 10, 10), "#d9cfa8") + blob(ellipse_pts(880, 150, 9, 7, 8), "#d9cfa8") +
                   blob(ellipse_pts(842, 156, 7, 6, 8), "#d9cfa8"), w=4.4, seed=900))
    # дальние холмы и деревья
    s.append(shape([(-600, nb.GBASE - 90), (-200, nb.GBASE - 170), (200, nb.GBASE - 120), (600, nb.GBASE - 200), (1000, nb.GBASE - 130),
                    (1600, nb.GBASE - 170), (1600, nb.GBASE + 40, 1), (-600, nb.GBASE + 40, 1)], "#1d2448", "", w=4, seed=901))
    rs = np.random.RandomState(3)
    for k in range(18):
        x = -300 + k * 100 + rs.uniform(-20, 20)
        r = rs.uniform(60, 95)
        y = nb.GBASE - 40 - rs.uniform(0, 50)
        s.append(shape(ellipse_pts(x, y, r, r * .85, 14, jitter=.08, seed=k), "#22304a" if k % 2 else "#1d2a42",
                       blob(ellipse_pts(x + r * .25, y + r * .3, r * .8, r * .55, 12), "#17213a", .8), w=4, seed=910 + k))
    return "".join(s)


def stars(t):
    rs = np.random.RandomState(11)
    s = []
    for k in range(70):
        x, y = rs.uniform(-400, W + 400), rs.uniform(-700, 520)
        if (x - 860) ** 2 + (y - 120) ** 2 < 130 ** 2:
            continue
        r = rs.uniform(1.6, 3.6)
        tw = 0.55 + 0.45 * math.sin(t * rs.uniform(3, 7) + k)
        if r > 3.0:   # крупные — четырёхлучевые искорки
            L = r * 3.2 * (0.7 + 0.3 * tw)
            s.append(f'<path d="M{f(x)} {f(y - L)} L{f(x + r * .5)} {f(y - r * .5)} L{f(x + L)} {f(y)} L{f(x + r * .5)} {f(y + r * .5)} '
                     f'L{f(x)} {f(y + L)} L{f(x - r * .5)} {f(y + r * .5)} L{f(x - L)} {f(y)} L{f(x - r * .5)} {f(y - r * .5)}Z" fill="#fff6d8" '
                     f'opacity="{.6 + .4 * tw:.3f}"/>')
        else:
            s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#e8ecff" opacity="{.35 + .55 * tw:.3f}"/>')
    return "".join(s)


def lawn07():
    s = []
    lin_grad([(0, "#22402e", 1), (1, "#162a20", 1)], 0, 0, 0, 1, gid="gLawn7")
    s.append(f'<rect x="-600" y="{nb.GBASE - 6}" width="{W + 1200}" height="{H + 400}" fill="url(#gLawn7)"/>')
    s.append(line([(-600, nb.GBASE - 6), (W + 600, nb.GBASE - 6)], 4, INK, taper=.1, wmin=.8, seed=920))
    px0, px1 = nb.PX0 + BX, nb.PX1 + BX
    path = [(px0 + 30, nb.GBASE), (px1 - 30, nb.GBASE), (px1 + 170, H + 400, 1), (px0 - 170, H + 400, 1)]
    s.append(shape(path, "#7a7468", blob([(px1 - 10, nb.GBASE), (px1 + 170, H + 400), (px1 + 70, H + 400), (px1 - 30, nb.GBASE)], "#5e594f", .9),
                   w=4, seed=921))
    # свет из двери на дорожке
    s.append(blob([(px0 + 60, nb.GBASE), (px1 - 60, nb.GBASE), (px1 + 30, nb.GBASE + 260), (px0 - 30, nb.GBASE + 260)], "#ffd27a", .25, blur(20)))
    return "".join(s)


def saguaro(x, y, h, sd, arms=((0.45, -1, 0.35), (0.6, 1, 0.3))):
    """Кактус-сагуаро: ствол и руки-«колбаски» с рёбрами; (x, y) — низ ствола."""
    s = []
    wd = h * 0.17
    col, sh, rib = "#2a5a48", "#1f4638", "#183a2e"
    for k, (at, side, L) in enumerate(arms):
        by = y - h * at
        out = side * wd * 1.25
        pts = [(x + side * wd * .3, by + wd * .6), (x + out, by + wd * .6), (x + out + side * wd * .3, by - wd * .2), (x + out + side * wd * .3, by - h * L)]
        pl = sausage(pts, wd * .72, wd * .66)
        s.append(shape(pl, col, line([(x + out + side * wd * .3, by - wd * .1), (x + out + side * wd * .3, by - h * L + 10)], 3, rib, seed=sd + 5 + k, op=.9),
                       w=4.2, seed=sd + 10 + k))
    trunk = sausage([(x, y + 10), (x, y - h * .5), (x, y - h)], wd, wd * .92)
    inner = blob([(x + wd * .15, y + 10), (x + wd * .6, y + 10), (x + wd * .6, y - h), (x + wd * .15, y - h)], sh, .9)
    for k in (-0.25, 0.15):
        inner += line([(x + wd * k, y), (x + wd * k, y - h + 10)], 3, rib, seed=sd + 20 + int(k * 10), op=.9)
    s.append(shape(trunk, col, inner, w=4.6, seed=sd))
    # колючки-точки
    rs = np.random.RandomState(sd)
    for k in range(14):
        yy = y - rs.uniform(0.1, 0.95) * h
        xx = x + rs.choice([-1, 1]) * wd * .5
        s.append(f'<circle cx="{f(xx)}" cy="{f(yy)}" r="2.2" fill="#c9d9b0"/>')
    return "".join(s)


def lamp_post(x, y, sd):
    s = [shape(rect_pts(x - 7, y - 300, x + 7, y), "#2a2e40", "", w=3.4, seed=sd)]
    s.append(shape([(x - 26, y - 300, 1), (x + 26, y - 300, 1), (x + 18, y - 352, 1), (x - 18, y - 352, 1)], "#ffe7a0", "", w=3.4, seed=sd + 1))
    s.append(shape([(x - 34, y - 352, 1), (x + 34, y - 352, 1), (x, y - 380, 1)], "#2a2e40", "", w=3.4, seed=sd + 2))
    return "".join(s)


WINS = [(x, y0, y1) for (y0, y1) in nb.WIN_ROWS for x in nb.WIN_X] + [(340, 640, 740)]
WIN_ON = [13.55, 13.7, 14.05, 13.62, 14.3, 13.8, 14.55, 13.9, 14.15]


def windows_light(t):
    s, glow = [], []
    for k, (x, y0, y1) in enumerate(WINS):
        on = smooth(WIN_ON[k], WIN_ON[k] + 0.08, t)
        if on <= 0:
            continue
        x += BX
        fl = 1 + 0.04 * math.sin(t * 9 + k * 2)
        glow.append(f'<rect x="{x - 60}" y="{y0 - 40}" width="120" height="{y1 - y0 + 80}" fill="#ffc35a" opacity="{.55 * on * fl:.3f}" {blur(22)}/>')
        col = mix("#3a3f62", "#ffcf6a", on)
        inner = blob([(x - 31, y0 + 60), (x + 31, y0 + 20), (x + 31, y0 + 44), (x - 31, y0 + 84)], mix("#565c86", "#fff0b8", on), .9)
        inner += blob(rect_pts(x - 31, y1 - 22, x + 31, y1), mix("#3a3f62", "#e8a84a", on), .8)
        s.append(shape(rect_pts(x - 31, y0, x + 31, y1), col, inner, w=3.2, seed=930 + k))
        trim = lib.mul("#f3ede1", (0.5, 0.54, 0.78))
        s.append(line([(x, y0), (x, y1)], 3.2, trim, taper=.1, wmin=.9, seed=940 + k))
        s.append(line([(x - 31, (y0 + y1) / 2), (x + 31, (y0 + y1) / 2)], 3.2, trim, taper=.1, wmin=.9, seed=950 + k))
    return "".join(glow), "".join(s)


def s07(t):
    if "s07" not in _ST:
        nb.brick_defs()
        _ST["s07"] = (sky07(), f'<g transform="translate({BX} 0)">{nb.building()}</g>', lawn07())
    sk, bld, lawn = _ST["s07"]
    glow, panes = windows_light(t)
    # лампы-фонари у дорожки — тёплый свет мерцает
    lamps = ""
    for k, x in enumerate((nb.GX0 + BX - 50, nb.GX1 + BX + 50)):
        fl = 0.85 + 0.15 * math.sin(t * 13 + k * 3)
        lamps += f'<circle cx="{x}" cy="{nb.GBASE + 40 - 366}" r="80" fill="#ffd27a" opacity="{.45 * fl:.3f}" {blur(24)}/>'
        lamps += lamp_post(x, nb.GBASE + 40, 960 + k * 5)
    cacti = (saguaro(70, 1330, 560, 970) + saguaro(1000, 1290, 430, 980, ((0.5, -1, 0.3),)) + saguaro(250, 1200, 200, 990, ()))
    art = sk + stars(t) + glow + bld + panes + lawn + lamps + cacti
    u = clamp((t - 13.6) / 2.1)
    k = 0.5 * u + 0.5 * ease_io(u)
    return art, cam(540, 720 - 40 * k, 1.0 + 0.16 * k)


# ═══════════════════════════════ s08: лаборатория сна, пишет список
def lab_wall(shade=1.0):
    s = []
    lin_grad([(0, "#3e5560", 1), (1, "#33464f", 1)], 0, 0, 0, 1, gid="gLab")
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#gLab)"/>')
    # кафель в нижней половине стены
    DEFS.append('<pattern id="pTile" width="90" height="90" patternUnits="userSpaceOnUse"><rect width="90" height="90" fill="#46606a"/>'
                '<path d="M0 .5H90M.5 0V90" stroke="#2f434b" stroke-width="3"/></pattern>')
    s.append(f'<rect x="-600" y="700" width="{W + 1200}" height="{H}" fill="url(#pTile)"/>')
    s.append(shape(rect_pts(-600, 690, W + 600, 712), "#5a7680", "", w=3.6, seed=1001))
    return "".join(s)


def monitor(x, y, w, h, t, calm=0.0, sd=0):
    """Монитор сна на стене: волна бежит (без букв); calm 0..1 — волна становится медленной и ровной."""
    s = [shape(rect_pts(x - w / 2 - 14, y - h / 2 - 14, x + w / 2 + 14, y + h / 2 + 14, 12), "#2b3036", "", w=4.4, seed=sd)]
    s.append(shape(rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 6), "#0e2a26", "", w=3, seed=sd + 1))
    for j, (yy, col) in enumerate(((y - h * .2, "#5cf2a0"), (y + h * .2, "#ffd36a"))):
        pts = []
        for i in range(48):
            u = i / 47
            xx = x - w / 2 + 12 + (w - 24) * u
            fast = math.sin(u * 40 - t * 14 + j) * 0.6 + math.sin(u * 77 - t * 23) * 0.4
            slow = math.sin(u * 9 - t * 4 + j)
            a = (1 - calm) * fast + calm * slow
            pts.append((xx, yy + h * .13 * a))
        s.append(line(pts, 4, col, taper=.05, wmin=.9, seed=sd + 5 + j))
    s.append(line([(x - w / 2 + 6, y - h / 2 + 8), (x - w / 2 + 40, y - h / 2 + 8)], 3, "#ffffff", seed=sd + 9, op=.25))
    return "".join(s)


def nightlight(x, y, t, sd):
    fl = 1 + 0.04 * math.sin(t * 7) + 0.02 * math.sin(t * 19)
    s = [f'<ellipse cx="{x}" cy="{y}" rx="{f(330 * fl)}" ry="{f(300 * fl)}" fill="#ffb85a" opacity=".32" style="mix-blend-mode:screen" {blur(40)}/>']
    s.append(shape([(x - 18, y + 40, 1), (x + 18, y + 40, 1), (x + 30, y + 110, 1), (x - 30, y + 110, 1)], "#6a5a4a", "", w=3.6, seed=sd))
    s.append(shape([(x - 60, y + 40, 1), (x + 60, y + 40, 1), (x + 40, y - 40, 1), (x - 40, y - 40, 1)], "#ffd890",
                   blob([(x - 60, y + 40), (x + 60, y + 40), (x + 50, y + 10), (x - 50, y + 10)], "#f2b660", .8), w=4, seed=sd + 1))
    return "".join(s)


def nightstand(x0, x1, y, sd):
    s = [shape(rect_pts(x0, y, x1, y + 330), "#5a4636", blob(rect_pts(x1 - 40, y, x1, y + 330), "#46362a", .9) +
               line([(x0 + 20, y + 120), (x1 - 20, y + 120)], 3, "#3a2c22", seed=sd + 1) +
               blob(ellipse_pts((x0 + x1) / 2, y + 70, 20, 7, 8), "#2a1f18"), w=4.6, seed=sd)]
    s.append(shape(rect_pts(x0 - 12, y - 16, x1 + 12, y + 6), "#6e5644", "", w=4.2, seed=sd + 2))
    return "".join(s)


def timer_value(t):
    if t < FIVE:
        return " 000"
    secs = 300 - (t - FIVE - 0.25) * 6 if t > FIVE + 0.25 else 300
    secs = max(0, int(math.ceil(secs)))
    return f"{secs // 60:>2d}{secs % 60:02d}".replace(" ", " ")


def timer(x, y, t, sd):
    """Таймер на тумбочке: корпус, табло (семисегментные цифры), кольцо оставшегося времени."""
    s = []
    e = t - FIVE
    pop = 1 + (0.18 * math.exp(-e * 8) * math.cos(e * 26) if e > 0 else 0)
    w, h = 250, 150
    body = rect_pts(-w / 2, -h / 2, w / 2, h / 2, 24)
    inner = blob(rect_pts(-w / 2, h / 2 - 30, w / 2, h / 2 + 4), "#c9cfd8", .9)
    s.append(shape(body, "#e9edf2", inner, w=4.6, seed=sd))
    s.append(shape(rect_pts(-w / 2 + 18, -h / 2 + 18, w / 2 - 18, h / 2 - 34, 10), "#14221e", "", w=3.4, seed=sd + 1))
    v = timer_value(t)
    on = t >= FIVE
    txt = f"{v[1]}:{v[2:]}" if on else "0:00"
    lit = "#7dffb0" if on else "#2c5a44"
    digits, wd = sevenseg(txt, 0, 0, 30, 58, 9, lit, ghost="#1d3a30", glow=.9 if on else 0, skew=0.1)
    s.append(f'<g transform="translate({f(-wd / 2)} -40)">{digits}</g>')
    # кнопки
    for k, bx in enumerate((-60, 0, 60)):
        pressed = 6 if (k == 1 and 0 < e < 0.15) else 0
        s.append(shape(rect_pts(bx - 22, -h / 2 - 16 + pressed, bx + 22, -h / 2 + 2, 6), "#f08a5a" if k == 1 else "#b9c0cc", "", w=3.2, seed=sd + 3 + k))
    # полоска оставшегося времени
    if on:
        frac = max(0.0, (int(v[1]) * 60 + int(v[2:])) / 300)
        s.append(f'<rect x="{-w / 2 + 24}" y="{h / 2 - 24}" width="{f((w - 48) * frac)}" height="9" rx="4" fill="#5ce08f"/>')
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(pop)})">{"".join(s)}</g>'


def head(spec, pose, x, y, sc, rot=0.0, sd=0, electrodes=True):
    s = f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{person.face(spec, pose, sd)}'
    if electrodes:
        for k, (ex, ey) in enumerate(((-34, -70), (30, -74))):
            s += line([(ex, ey), (ex + 10 * (k * 2 - 1), ey - 60), (ex + 30 * (k * 2 - 1), ey - 200)], 3.4, ["#e85a5a", "#5a8ae8"][k], taper=.05, wmin=.9, seed=sd + 90 + k)
            s += shape(ellipse_pts(ex, ey, 8, 8, 8), "#f2f2f2", "", w=2.6, seed=sd + 95 + k)
    return s + "</g>"


def fingers_over(x, y, ang, n=4, length=34, wd=16, sc=1.0, skin="#e9c0a0", sd=0):
    """Пальцы, лежащие на краю листа спереди (хват): n «сосисок» от (x, y) вдоль ang, чуть веером."""
    s = []
    for k in range(n):
        off = (k - (n - 1) / 2) * wd * 0.95
        a = math.radians(ang)
        nx, ny = -math.sin(a), math.cos(a)
        bx, by = x + nx * off * sc, y + ny * off * sc
        L = length * (1 - 0.12 * abs(k - (n - 1) / 2)) * sc
        pts = [(bx, by), (bx + math.cos(a) * L * .5, by + math.sin(a) * L * .5), (bx + math.cos(a) * L, by + math.sin(a) * L)]
        s.append(shape(sausage(pts, wd * sc, wd * .9 * sc), skin, "", w=2.8 * sc, seed=sd + k))
    return "".join(s)


def pad08(t):
    """Блокнот на коленях; строки-волны появляются по ходу пера. Возвращает (svg, кончик пера в мире)."""
    cx, cy, rot = 560, 1100, -6
    pw, ph = 270, 196
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def P(u, v):
        return (cx + u * c - v * sn, cy + u * sn + v * c)
    s = []
    s.append(shape([P(-pw / 2 - 10, -ph / 2 - 10) + (1,), P(pw / 2 + 10, -ph / 2 - 10) + (1,), P(pw / 2 + 10, ph / 2 + 10) + (1,),
                    P(-pw / 2 - 10, ph / 2 + 10) + (1,)], "#c4473f", "", w=4.4, seed=1100))
    s.append(shape([P(-pw / 2, -ph / 2) + (1,), P(pw / 2, -ph / 2) + (1,), P(pw / 2, ph / 2) + (1,), P(-pw / 2, ph / 2) + (1,)], "#f4f1e6",
                   "".join(line([P(-pw / 2 + 10, -ph / 2 + 36 + k * 40), P(pw / 2 - 10, -ph / 2 + 36 + k * 40)], 2, "#a9c2dc", taper=.05, wmin=.9,
                                seed=1110 + k, op=.9) for k in range(4)), w=3.6, seed=1101))
    # строки списка: точка + волнистая «запись»
    W0, W1 = 15.30, 17.95
    nl = 4
    per = (W1 - W0) / nl
    tip = None
    for k in range(nl):
        t0 = W0 + k * per
        if t < t0:
            break
        q = clamp((t - t0) / (per * 0.85))
        y = -ph / 2 + 28 + k * 40
        s.append(shape(ellipse_pts(*P(-pw / 2 + 26, y), 5, 5, 8), "#2a3a6a", "", ink=False))
        x0, x1 = -pw / 2 + 44, -pw / 2 + 44 + [160, 190, 130, 175][k]
        n = max(2, int(30 * q))
        pts = [P(x0 + (x1 - x0) * i / 29, y + 6 * math.sin(i * 1.9 + k) * (1 if i % 3 else .4)) for i in range(n)]
        s.append(line(pts, 4.2, "#2a3a6a", taper=.2, wmin=.5, seed=1120 + k))
        if q < 1:
            tip = pts[-1]
        else:
            tip = pts[-1]
            if t < t0 + per:
                u = (t - t0 - per * 0.85) / (per * 0.15)
                nxt = P(x0, y + 40)
                tip = (tip[0] + (nxt[0] - tip[0]) * u, tip[1] + (nxt[1] - tip[1]) * u - 12 * math.sin(math.pi * u))
    if tip is None:
        tip = P(-pw / 2 + 44, -ph / 2 + 30)
    return "".join(s), tip, P


def s08(t):
    if "s08" not in _ST:
        bg = lab_wall()
        bg += nightstand(-60, 230, 980, 1200) + nightstand(780, 1060, 980, 1210)
        # кровать: изголовье и подушка
        bg += shape(rect_pts(250, 600, 830, 1000, 30), "#8c96a8", blob(rect_pts(780, 600, 830, 1000), "#6f788a", .9) +
                    line([(280, 640), (800, 640)], 4, "#b4bccb", seed=1220, op=.8), w=5, seed=1221)
        bg += shape(ellipse_pts(540, 860, 260, 110, 18), "#dde4ef", blob(ellipse_pts(570, 900, 230, 70, 14), "#bcc7d8", .9), w=4.6, seed=1222)
        _ST["s08"] = bg
    s = [_ST["s08"]]
    s.append(monitor(780, 400, 300, 170, t, 0.0, 1230))
    s.append(nightlight(90, 880, t, 1240))
    s.append(timer(905, 905, t, 1250))
    # тело: пижама, плечи
    top, top_sh = "#5b7fb5", "#465f8c"
    torso = [(380, 1010), (400, 930), (470, 900), (610, 900), (680, 930), (700, 1010), (720, 1200, 1), (360, 1200, 1)]
    s.append(shape(torso, top, blob([(560, 900), (680, 930), (700, 1010), (720, 1200), (600, 1200)], top_sh, .9) +
                   line([(540, 910), (540, 1080)], 3, "#3b5482", seed=1260, op=.8), w=5, seed=1261))
    s.append(shape([(505, 900), (540, 935), (575, 900), (560, 892), (540, 912), (520, 892)], "#e9edf3", "", w=3.2, seed=1262))
    # одеяло на ногах — к зрителю шире
    blank = [(250, 1150), (400, 1120), (700, 1120), (840, 1150), (980, 1600, 1), (100, 1600, 1)]
    s.append(shape(blank, "#d8deea", blob([(700, 1120), (840, 1150), (980, 1600), (760, 1600), (680, 1300)], "#b4bfd2", .9) +
                   line([(380, 1250), (430, 1500)], 4, "#aab5c8", seed=1270, op=.8) + line([(640, 1240), (700, 1520)], 4, "#aab5c8", seed=1271, op=.8),
                   w=5.2, seed=1272))
    # голова: дышит, смотрит в блокнот, моргает
    bl = 0.0
    for tb in (15.95, 17.2):
        if tb < t < tb + 0.16:
            bl = math.sin(math.pi * (t - tb) / 0.16)
    hy = 790 + 3 * math.sin(t * 2.4)
    tilt = -4 + 2 * math.sin(t * 1.3)
    s.append(head(A, {"look": (0.2, 1.4), "blink": 0.25 + bl * 0.71, "mouth": "flat", "brow": 0.2}, 540, hy, 1.22, tilt, 1300))
    # левая рука: локоть на одеяле, кисть держит блокнот слева
    pad, tip, P = pad08(t)
    lw = P(-145, 24)
    s.append(person.tube((395, 950), (330, 1080), (lw[0] - 10, lw[1] + 14), 46, 40, 32, top, 1280))
    s.append(blob(ellipse_pts(lw[0] - 6, lw[1] + 6, 26, 30, 10), A["skin"]))   # ладонь под блокнотом
    s.append(pad)
    s.append(fingers_over(lw[0] + 6, lw[1] - 4, -6, 4, 30, 16, 1.15, A["skin"], 1290))
    # правая рука с ручкой: кончик пера в tip
    ang = -48 + 4 * math.sin(t * 3)
    sc = 0.34
    hand_svg = penhand.draw(tip[0], tip[1], ang, sc, 1310, 0.0, sleeve=False)
    wr = penhand._P([(300, 40)], ang)[0]
    wx, wy = tip[0] + wr[0] * sc, tip[1] + wr[1] * sc
    s.append(person.tube((685, 950), (780, 1100), (wx + 6, wy + 4), 46, 40, 34, top, 1320))
    s.append(hand_svg)
    art = "".join(s)
    u = clamp((t - 15.3) / 2.7)
    return art, cam(600, 960 + 10 * u, 1.10 + 0.10 * ease_io(u), 0.5 - 0.6 * u)


# ═══════════════════════════════ s09: две кровати
def zee(x, y, sz, op, sd):
    pts = [(x - sz, y - sz, 1), (x + sz, y - sz, 1), (x - sz, y + sz, 1), (x + sz, y + sz, 1)]
    return (f'<g opacity="{op:.3f}">' + line(pts, sz * .55, INK, taper=.05, wmin=.9, seed=sd) +
            line(pts, sz * .32, "#dfe9ff", taper=.05, wmin=.9, seed=sd + 1) + "</g>")


def paper(cx, cy, rot, kind, sc=1.0, sd=0):
    """Листок в руках лежащего: kind='list' — точки и строки-волны, 'done' — строки с зелёными галочками."""
    s = []
    w, h = 200, 150
    body = [(-w / 2, -h / 2, 1), (w / 2, -h / 2, 1), (w / 2, h / 2, 1), (-w / 2, h / 2, 1)]
    inner = ""
    for k in range(3):
        y = -h / 2 + 34 + k * 40
        if kind == "list":
            inner += f'<circle cx="{-w / 2 + 22}" cy="{y}" r="5" fill="#2a3a6a"/>'
            inner += line([(-w / 2 + 38 + i * 10, y + 4 * math.sin(i * 1.9 + k)) for i in range(11 - k * 2)], 3.6, "#2a3a6a", taper=.2, wmin=.5, seed=sd + 10 + k)
        else:
            inner += line([(-w / 2 + 14, y + 2), (-w / 2 + 22, y + 10), (-w / 2 + 38, y - 10)], 6, "#2f9a4a", taper=.2, wmin=.6, seed=sd + 20 + k)
            inner += line([(-w / 2 + 50 + i * 10, y + 4 * math.sin(i * 1.7 + k)) for i in range(11 - k)], 3.6, "#2a3a6a", taper=.2, wmin=.5, seed=sd + 30 + k)
    s.append(shape(body, "#f6f3ea", inner, w=3.6, seed=sd))
    return f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({f(sc)})">{"".join(s)}</g>'


def bed09(cx, t, spec, pose, paper_kind, sd, sleep=0.0, toss=0.0, head_rot=0.0, top="#5b7fb5"):
    """Кровать сверху-спереди: изголовье, подушка, голова на подушке, плечи, одеяло до груди, руки с листком на одеяле."""
    s = []
    s.append(shape(rect_pts(cx - 230, 560, cx + 230, 760, 26), "#8c96a8", blob(rect_pts(cx + 180, 560, cx + 230, 760), "#6f788a", .9), w=5, seed=sd))
    s.append(shape(rect_pts(cx - 220, 720, cx + 220, 1700), "#c9d1df", "", w=4.6, seed=sd + 1))      # матрас-простыня
    s.append(shape(ellipse_pts(cx, 790, 190, 80, 16), "#e2e8f2", blob(ellipse_pts(cx + 20, 820, 170, 50, 14), "#c3cddd", .9), w=4.4, seed=sd + 2))
    bx = cx + toss * 14
    # плечи под одеялом
    sh = [(bx - 150, 1000), (bx - 120, 920), (bx - 50, 895), (bx + 50, 895), (bx + 120, 920), (bx + 150, 1000), (bx + 160, 1060, 1), (bx - 160, 1060, 1)]
    s.append(shape(sh, top, blob([(bx + 30, 895), (bx + 120, 920), (bx + 150, 1000), (bx + 160, 1060), (bx + 60, 1060)], lib.mul(top, (.8, .8, .86)), .9),
                   w=4.6, seed=sd + 3))
    s.append(head(spec, pose, bx + toss * 6, 800, 0.98, head_rot, sd + 10, electrodes=True))
    # одеяло: верхний край волной, складки, шевелится при ворочании
    by = 1010 + 6 * toss
    edge = [(cx - 240, by + 20 + 10 * toss), (cx - 120, by - 6 - 8 * toss), (cx, by + 4), (cx + 120, by - 4 + 10 * toss), (cx + 240, by + 16 - 8 * toss)]
    bl = [(edge[0][0], edge[0][1], 1)] + edge[1:-1] + [(edge[-1][0], edge[-1][1], 1), (cx + 250, 1720, 1), (cx - 250, 1720, 1)]
    inner = blob([(cx + 120, by), (cx + 240, by + 16), (cx + 250, 1720), (cx + 120, 1720), (cx + 80, 1300)], "#9fb0c8", .8)
    inner += line([(cx - 120 + 20 * toss, by + 60), (cx - 80 + 30 * toss, by + 340)], 4, "#8fa0ba", seed=sd + 5, op=.8)
    inner += line([(cx + 40 - 20 * toss, by + 120), (cx + 70 - 10 * toss, by + 400)], 4, "#8fa0ba", seed=sd + 6, op=.8)
    inner += blob(rect_pts(cx - 260, by - 20, cx + 260, by + 34), "#f0f3f8", .9)          # отворот
    s.append(shape(bl, "#c6d2e6", inner, w=5, seed=sd + 7))
    s.append(line([(cx - 236, by + 50), (cx, by + 46), (cx + 236, by + 50)], 3.4, "#9fb0c8", seed=sd + 8, op=.9))
    # руки поверх одеяла и листок
    drop = sleep
    pcx, pcy = bx, 1120 + 50 * drop
    prot = -4 + 14 * drop + 3 * toss
    ps = paper(pcx, pcy, prot, paper_kind, 1.0, sd + 30)
    c, sn = math.cos(math.radians(prot)), math.sin(math.radians(prot))
    L = (pcx - 100 * c - 10 * (-sn), pcy - 100 * sn + 10 * c)
    R = (pcx + 100 * c - 10 * (-sn), pcy + 100 * sn + 10 * c)
    skin = spec["skin"]
    s.append(person.tube((bx - 130, 960), (bx - 190, 1100), (L[0] - 22, L[1] + 8), 40, 36, 30, top, sd + 40))
    s.append(person.tube((bx + 130, 960), (bx + 190, 1100), (R[0] + 22, R[1] + 8), 40, 36, 30, top, sd + 41))
    s.append(blob(ellipse_pts(L[0] - 14, L[1] + 4, 22, 26, 10), skin) + blob(ellipse_pts(R[0] + 14, R[1] + 4, 22, 26, 10), skin))
    s.append(ps)
    s.append(fingers_over(L[0] - 14, L[1] - 2, prot - 4, 4, 26 * (1 - .25 * drop), 13, 1.0, skin, sd + 50))
    s.append(fingers_over(R[0] + 14, R[1] - 2, prot + 184, 4, 26 * (1 - .25 * drop), 13, 1.0, skin, sd + 60))
    return "".join(s)


def s09(t):
    if "s09" not in _ST:
        _ST["s09"] = lab_wall() + nightstand(460, 620, 900, 1400)
    s = [_ST["s09"]]
    calm = smooth(ASLEEP, ASLEEP + 0.8, t)
    s.append(monitor(540, 330, 320, 180, t, calm, 1410))
    s.append(nightlight(540, 800, t, 1420))
    # слева: сонный, на «быстрее» засыпает
    sl = smooth(ASLEEP - 0.12, ASLEEP + 0.1, t)
    droop = 0.35 + 0.25 * (0.5 + 0.5 * math.sin(t * 3.0))   # веки тяжелеют
    blinkA = max(sl, droop * (1 - sl))
    if t < ASLEEP - 0.12 and 18.0 < t < 18.2:
        blinkA = max(blinkA, math.sin(math.pi * (t - 18.0) / .2))
    poseA = {"look": (0.0, -0.4), "blink": 1.0 if sl > 0.6 else blinkA * 0.9, "mouth": "flat" if sl < .5 else "o", "brow": -0.3}
    s.append(bed09(270, t, A, poseA, "list", 1500, sleep=sl, head_rot=-8 * sl + 1.5 * math.sin(t * 2) * (1 - sl)))
    # справа: не спит, ворочается, глаза бегают
    toss = math.sin((t - 17.6) * 2.4) * smooth(17.7, 18.3, t)
    toss += 1.2 * math.exp(-max(t - 19.6, 0) * 3) * math.sin(max(t - 19.6, 0) * 9) * (t > 19.6)
    look = (math.sin(t * 2.1) * .9, -0.2 + .5 * math.sin(t * 1.3))
    bB = 0.0
    for tb in (18.9, 20.3):
        if tb < t < tb + 0.14:
            bB = math.sin(math.pi * (t - tb) / 0.14)
    poseB = {"look": look, "blink": bB * .96, "mouth": "wavy", "brow": 1.0}
    s.append(bed09(810, t, B, poseB, "done", 1600, toss=toss, head_rot=6 * toss, top="#6a9a6a"))
    # Z над засыпающим
    if t > ASLEEP:
        for k in range(4):
            ph = ((t - ASLEEP) * 0.7 - k * 0.27)
            if ph < 0:
                continue
            ph %= 1.08
            op = smooth(0, .12, ph) * (1 - smooth(.75, 1.05, ph))
            x = 360 + 90 * ph + 18 * math.sin(ph * 6 + k)
            y = 700 - 330 * ph
            s.append(zee(x, y, 16 + 22 * ph, op, 1700 + k * 3))
    # «ворочается» — штрихи у правого
    if t > 18.0:
        for k in range(2):
            ph = (t * 1.6 + k * .5) % 1
            x0 = 1010 + 20 * ph
            s.append(line([(x0, 820 + k * 70), (x0 + 30, 805 + k * 70 + 6 * math.sin(ph * 6))], 6, "#e9eeff", taper=.5, seed=1720 + k,
                          op=(1 - ph) * .9))
    art = "".join(s)
    u = clamp((t - 17.6) / 3.8)
    return art, cam(540 + 6 * math.sin(u * 3), 940, 1.22 + 0.05 * u)


def frame(sid, t):
    if "base" not in _ST:
        _ST["base"] = True
        if sid == "s07":
            s07(t)
        elif sid == "s08":
            s08(t)
        else:
            s09(t)
        lib.static_done()
    lib.dyn_begin()
    art, cm = {"s07": s07, "s08": s08, "s09": s09}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1a2030"/><g transform="{cm}">{art}</g>')
