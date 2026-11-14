"""Сцена study рилса 41 (s11, 18.08–20.64): Массачусетс, Кембридж (опыт Ariely, Wertenbroch 2002). Без букв и логотипов.
Светлое университетское здание с портиком из колонн и большим куполом, по бокам крылья с окнами, широкая лестница,
лужайка, деревья по краям, на переднем плане река с яликом под парусом. День.
С первого кадра: камера наезжает к зданию, облака и птицы летят, деревья качаются, по реке бегут блики, ялик плывёт.
На «Массачусетсе» (18.16) купол вспыхивает солнечным бликом (звезда-вспышка и полоса света по куполу).
На «вычитывать» (19.76) по ступеням поднимаются четыре студента со стопками листов в руках (вошли с краёв к 19.5).
Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import person
import scene_stanford as sf
import study28 as st
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg, T)

_ST = {}
GLINT = 18.16        # «Массачусетсе»
READ = 19.76         # «вычитывать»
STONE, STONE_SH, STONE_DK, STONE_HI = "#f1ece0", "#d6cfbf", "#b9b0a0", "#fffaf0"
DOME, DOME_SH = "#dcdcd6", "#b8b9b4"
LAWN = 1112          # низ лестницы
STEP_TOP = 986       # верх лестницы (площадка портика)
NSTEP = 6
BANK = 1236          # берег реки
CXB = 540


# ───────────────────────── небо
def sky():
    s = []
    g = lin_grad([(0, "#5aa6ea", 1), (.55, "#a6d4f5", 1), (1, "#eef3ea", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-700" y="-900" width="{W + 1400}" height="{BANK + 900}" fill="url(#{g})"/>')
    g2 = rad_grad([(0, "#fff8d8", 1), (.25, "#fff1b0", .6), (1, "#fff1b0", 0)], 150, 160, 460, 460)
    s.append(f'<rect x="-700" y="-900" width="{W + 1400}" height="{BANK + 900}" fill="url(#{g2})"/>')
    s.append(shape(ellipse_pts(150, 160, 70, 70, 24), "#ffe27a", blob(ellipse_pts(166, 178, 56, 52, 18), "#ffd04e", .8), w=4.2, seed=5001))
    return "".join(s)


def clouds(t):
    s = []
    for k, (x0, y, sc, sp) in enumerate([(420, 150, 1.0, 14), (900, 300, .75, 10), (-160, 330, .8, 12)]):
        x = x0 + sp * (t - 17.9)
        pts = []
        for i in range(14):
            a = 2 * math.pi * i / 14
            r = 1 + .18 * math.sin(5 * a + k)
            pts.append((x + 110 * sc * math.cos(a) * r, y + 40 * sc * math.sin(a) * r * (0.75 if math.sin(a) > 0 else 1)))
        s.append(shape(pts, "#ffffff", blob(ellipse_pts(x + 20 * sc, y + 22 * sc, 90 * sc, 16 * sc, 10), "#d8e8f5"), w=3.6, seed=5010 + k))
    return "".join(s)


def birds(t):
    s = []
    for k, (x0, y0, v) in enumerate([(-80, 260, 170), (-220, 330, 150), (1150, 380, -140)]):
        x = x0 + v * (t - 17.9)
        y = y0 + 8 * math.sin(t * 2 + k)
        fl = 12 * math.sin(t * 14 + k)
        s.append(line([(x - 22, y - fl), (x - 8, y - 3), (x, y + 2), (x + 8, y - 3), (x + 22, y - fl)], 4, INK, taper=.5, wmin=.3, seed=5020 + k))
    return "".join(s)


# ───────────────────────── здание
def window(x, y, w, h, sd, arch=False):
    pts = rect_pts(x - w / 2, y, x + w / 2, y + h, 3) if not arch else sf.arch_pts(x, y, w, y + h)
    inner = blob(rect_pts(x - w / 2, y + h * .55, x + w / 2, y + h), "#4f6f94", .9)
    inner += line([(x, y + 4), (x, y + h)], 2.6, STONE_HI, taper=.05, wmin=.9, seed=sd + 1)
    inner += line([(x - w / 2, y + h * .5), (x + w / 2, y + h * .5)], 2.6, STONE_HI, taper=.05, wmin=.9, seed=sd + 2)
    inner += line([(x - w * .3, y + h * .38), (x - w * .1, y + h * .12)], 3, "#d9ecff", seed=sd + 3, op=.85)
    return shape(pts, "#6d8db2", inner, w=3.2, seed=sd)


def wing(x0, x1, top, sd):
    s = []
    wall = rect_pts(x0, top, x1, STEP_TOP + 4)
    inner = blob(rect_pts(x0, STEP_TOP - 40, x1, STEP_TOP + 4), STONE_SH, .8)
    for k in range(4):
        inner += line([(x0, top + 70 + k * 80), (x1, top + 72 + k * 80)], 1.8, STONE_DK, taper=.1, wmin=.6, seed=sd + k, op=.35)
    s.append(shape(wall, STONE, inner, w=4.6, seed=sd))
    n = max(2, int((x1 - x0) / 90))
    for r, (yy, hh) in enumerate(((top + 60, 96), (top + 210, 120))):
        for k in range(n):
            x = x0 + (x1 - x0) * (k + .5) / n
            s.append(window(x, yy, 46, hh, sd + 20 + r * 10 + k, arch=(r == 1)))
    # карниз
    s.append(shape(rect_pts(x0 - 10, top - 26, x1 + 10, top + 6, 3), STONE, blob(rect_pts(x0 - 10, top - 6, x1 + 10, top + 6), STONE_SH, .9), w=4.2, seed=sd + 60))
    return "".join(s)


def dome_pts(cx, cy, r, ry):
    return [(cx + r * math.cos(a), cy - ry * math.sin(a)) + ((1,) if k in (0, 16) else ()) for k, a in enumerate(np.linspace(0, math.pi, 17))]


def building():
    s = []
    # крылья
    s.append(wing(-140, 305, 660, 5100))
    s.append(wing(775, 1220, 660, 5200))
    # барабан купола
    s.append(shape(rect_pts(330, 452, 750, 604, 4), STONE,
                   blob(rect_pts(640, 452, 750, 604), STONE_SH, .85) + "".join(
                       blob(rect_pts(360 + k * 54, 486, 380 + k * 54, 586), STONE_SH, .75) for k in range(8)), w=4.6, seed=5300))
    s.append(shape(rect_pts(318, 440, 762, 462, 4), STONE, blob(rect_pts(318, 454, 762, 462), STONE_SH, .9), w=4.2, seed=5301))
    # купол
    dp = dome_pts(CXB, 444, 226, 200)
    inner = blob([(CXB + 60, 250), (CXB + 240, 300), (CXB + 240, 450), (CXB + 40, 450)], DOME_SH, .9)
    for k in range(-3, 4):        # рёбра купола
        x = CXB + k * 64
        top_y = 444 - 200 * math.sqrt(max(0, 1 - ((x - CXB) / 226) ** 2))
        inner += line([(CXB + k * 10, 250), (x, top_y + 30), (x + k * 6, 444)], 2.6, DOME_SH, taper=.2, wmin=.6, seed=5310 + k, op=.8)
    inner += line([(CXB - 170, 380), (CXB - 130, 300), (CXB - 70, 262)], 10, "#f6f6f2", taper=.6, seed=5320, op=.9)
    s.append(shape(dp, DOME, inner, w=5.4, seed=5302))
    # фонарик на макушке
    s.append(shape(rect_pts(CXB - 34, 214, CXB + 34, 252, 6), STONE, blob(rect_pts(CXB + 8, 214, CXB + 34, 252), STONE_SH, .9), w=3.8, seed=5330))
    s.append(shape(dome_pts(CXB, 216, 34, 24), DOME, "", w=3.6, seed=5331))
    # портик: антаблемент, колонны, площадка
    s.append(shape(rect_pts(250, 604, 830, 676, 3), STONE,
                   blob(rect_pts(250, 652, 830, 676), STONE_SH, .9) + line([(260, 630), (820, 632)], 2.6, STONE_DK, taper=.1, wmin=.7, seed=5340, op=.7),
                   w=4.8, seed=5341))
    s.append(blob(rect_pts(270, 676, 810, 968), "#7f8a96"))      # тень в глубине портика
    s.append(shape(rect_pts(270, 676, 810, 968), "#9aa4ae", blob(rect_pts(270, 676, 810, 730), "#77818c", .9) + "".join(
        window(330 + k * 140, 760, 54, 150, 5350 + k) for k in range(4)), w=3, seed=5349))
    for k in range(8):
        x = 286 + k * 72.5
        col = rect_pts(x - 17, 690, x + 17, 960, 2)
        inner = blob(rect_pts(x + 4, 690, x + 17, 960), STONE_SH, .95)
        inner += line([(x - 6, 700), (x - 6, 950)], 2, STONE_DK, taper=.1, wmin=.7, seed=5360 + k, op=.5)
        inner += line([(x + 1, 700), (x + 1, 950)], 2, STONE_DK, taper=.1, wmin=.7, seed=5370 + k, op=.5)
        s.append(shape(col, STONE, inner, w=3.6, seed=5380 + k))
        s.append(shape(rect_pts(x - 25, 676, x + 25, 692, 3), STONE, "", w=3.2, seed=5390 + k))     # капитель
        s.append(shape(rect_pts(x - 23, 958, x + 23, 972, 2), STONE, "", w=3, seed=5400 + k))       # база
    s.append(shape(rect_pts(240, 968, 840, STEP_TOP + 2, 2), STONE, blob(rect_pts(240, 980, 840, STEP_TOP + 2), STONE_SH, .9), w=4, seed=5410))
    return "".join(s)


def step_y(k):
    return STEP_TOP + (LAWN - STEP_TOP) * k / NSTEP


def stairs():
    s = []
    for k in range(NSTEP):
        y0, y1 = step_y(k), step_y(k + 1)
        x0, x1 = 230 - k * 22, 850 + k * 22
        s.append(shape(rect_pts(x0, y0, x1, y1 + 1), STONE, blob(rect_pts(x0, y0 + (y1 - y0) * .55, x1, y1 + 1), STONE_SH, .9), w=3.4, seed=5420 + k))
    return "".join(s)


def lawn():
    s = []
    s.append(shape(rect_pts(-700, STEP_TOP - 10, W + 700, BANK + 10), "#8cc160",
                   blob(rect_pts(-700, BANK - 30, W + 700, BANK + 10), "#79ad50", .9), w=4.2, seed=5500))
    s.append(shape([(330, LAWN, 1), (750, LAWN, 1), (900, BANK + 8, 1), (180, BANK + 8, 1)], "#e9dcc0",
                   blob([(560, LAWN), (750, LAWN), (900, BANK + 8), (620, BANK + 8)], "#d9c9a6", .8), w=3.6, seed=5501))
    rs = np.random.RandomState(6)
    for k in range(30):
        x, y = rs.uniform(-200, 1280), rs.uniform(LAWN + 10, BANK - 10)
        if 160 < x < 920:
            continue
        s.append(line([(x, y), (x + rs.uniform(-4, 4), y - rs.uniform(10, 18))], 2.8, "#5f9a40", taper=.6, wmin=.2, seed=5510 + k))
    return "".join(s)


def tree(x, y, h, t, sd):
    sway = 2.5 * math.sin(t * 1.2 + sd)
    s = [blob(ellipse_pts(x + 14, y + 4, h * .32, h * .05, 14), "#4f7a34", .5, blur(5))]
    trunk = [(x - 16, y, 1), (x - 10, y - h * .45), (x + sway, y - h * .62), (x + 12 + sway, y - h * .45), (x + 18, y, 1)]
    s.append(shape(trunk, "#8a5e38", blob([(x + 4, y), (x + 18, y), (x + 12 + sway, y - h * .45), (x + 4 + sway, y - h * .5)], "#6c4628", .9), w=4, seed=sd))
    cx, cy = x + sway * 2, y - h * .72
    for k, (dx, dy, r, c) in enumerate([(-h * .2, h * .08, h * .22, "#5aa04a"), (h * .2, h * .06, h * .21, "#4f9442"), (0, -h * .12, h * .27, "#62ab50")]):
        pts = sf.cloud_pts(cx + dx, cy + dy, r, r * .85, 8, sd + 10 + k)
        s.append(shape(pts, c, blob(ellipse_pts(cx + dx + r * .3, cy + dy + r * .35, r * .7, r * .45, 12), "#3f7e36", .85), w=4, seed=sd + 20 + k))
    return "".join(s)


def river(t):
    s = []
    g = lin_grad([(0, "#6fb2de", 1), (1, "#3f86c0", 1)], 0, 0, 0, 1)
    s.append(shape(rect_pts(-700, BANK, W + 700, H + 600), f"url(#{g})", blob(rect_pts(-700, BANK, W + 700, BANK + 22), "#8fc6e8", .9), w=4.6, seed=5600))
    rs = np.random.RandomState(8)
    for k in range(26):
        x0, y = rs.uniform(-300, 1380), rs.uniform(BANK + 50, 1900)
        x = (x0 + 40 * (t - 17.9) * (1 + (k % 3) * .3)) % 1700 - 320
        L = rs.uniform(40, 110) * (0.7 + 0.3 * math.sin(t * 3 + k))
        s.append(line([(x, y), (x + L * .5, y - 3), (x + L, y)], 3.4, "#d9f0ff", taper=.6, wmin=.2, seed=5610 + k, op=.9))
    return "".join(s)


def sailboat(t):
    x = 640 + 40 * (t - 17.9)
    y = 1450 + 6 * math.sin(t * 2.2)
    rk = 3 * math.sin(t * 2.2 + .5)
    hull = [(-90, 0, 1), (90, 0, 1), (64, 32), (-60, 32)]
    sail = [(-4, -16, 1), (-4, -220, 1), (80, -30, 1)]
    sail2 = [(-14, -24, 1), (-14, -170, 1), (-80, -30, 1)]
    g = shape(sail2, "#f6f2e6", blob([(-14, -110), (-14, -24), (-60, -30)], "#ddd6c4", .9), w=3.4, seed=5650)
    g += line([(-8, 4), (-8, -236)], 5, INK, taper=.05, wmin=.9, seed=5651)
    g += shape(sail, "#ffffff", blob([(-4, -120), (-4, -16), (60, -30)], "#e4e0d4", .9) + line([(-4, -150), (40, -60)], 2.4, "#d7493f", seed=5653, op=.9), w=3.6, seed=5652)
    g += shape(hull, "#d7493f", blob([(-90, 16), (90, 16), (64, 32), (-60, 32)], "#a93228", .9), w=4, seed=5654)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rk)}) scale(.62)">{g}</g>'


# ───────────────────────── блик купола
def glint(t):
    e = t - GLINT
    s = []
    if -0.05 < e < 0.9:
        # полоса света сползает по куполу слева направо
        u = clamp((e + 0.05) / 0.5)
        c = lib.clip_of(dome_pts(CXB, 444, 226, 200))
        bx = CXB - 300 + 600 * ease_out(u)
        band = [(bx - 40, 220), (bx + 30, 220), (bx - 50, 460), (bx - 120, 460)]
        a = 1 - smooth(0.55, 0.9, e)
        s.append(f'<g clip-path="url(#{c})">{blob(band, "#ffffff", .75 * a)}</g>')
    if 0 <= e < 0.75:
        k = back_out(clamp(e / 0.14), 2.6) * (1 - smooth(0.4, 0.75, e))
        x, y = CXB - 120, 300
        r = 120 * k
        if r > 2:
            pts = []
            for j in range(8):
                a = math.radians(j * 45 - 90 + 20 * e)
                rr = r if j % 2 == 0 else r * 0.22
                pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
            g = rad_grad([(0, "#fffbe6", .9 * k), (1, "#fff3b0", 0)], x, y, 220 * k + 1, 220 * k + 1)
            s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(230 * k)}" fill="url(#{g})"/>')
            s.append(shape(pts, "#fff7c8", blob(ellipse_pts(x, y, r * .2, r * .2, 10), "#ffffff"), w=3.4, seed=5700))
            for j in range(6):
                a = math.radians(j * 60 + 30)
                r0, r1 = r * 0.55 + 30 * e, r * 0.9 + 60 * e
                s.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 6 * k + 1, "#ffcf3a",
                              taper=.5, seed=5710 + j))
    return "".join(s)


# ───────────────────────── студенты со стопками листов
STUD = [
    dict(skin="#f0c4a0", hair="short", hair_c="#5a3a26", top="#2d55a8", low="#1f2b52", face=.35, stubble=True),
    dict(skin="#8a5a3c", hair="curly", hair_c="#2a1a14", top="#e07a2e", low="#3a3040", face=.35),
    dict(skin="#f4d0b4", hair="ponytail", hair_c="#c8622a", top="#3a9a6a", low="#24484a", face=-.35),
    dict(skin="#d9a07a", hair="bun", hair_c="#2a1a14", top="#7a4fb0", low="#2a2a3a", face=-.35, glasses=True),
]
# старт (x, ступни y), конец (x, y), время входа
PATHS = [((120, BANK - 20), (420, step_y(1)), 19.05), ((10, BANK - 30), (330, step_y(3)), 19.25),
         ((960, BANK - 24), (655, step_y(1)), 19.12), ((1070, BANK - 30), (750, step_y(3)), 19.32)]
SC = 0.27


def paper_stack(x, y, n, sd):
    """Стопка листов в руках (координаты человека): n листов, уголки чуть вразнобой."""
    s = []
    for k in range(n):
        dx = [0, 6, -5, 7, -3, 4, -6, 2][k % 8]
        yy = y + 40 - k * 15
        s.append(shape(rect_pts(x - 92 + dx, yy - 18, x + 92 + dx, yy, 2), "#fbfaf4" if k % 2 else "#ecE8da".lower(),
                       blob(rect_pts(x + 56 + dx, yy - 18, x + 92 + dx, yy), "#dedbd0", .8), w=4, seed=sd + k))
    top = y + 40 - (n - 1) * 15 - 18
    s.append(line([(x - 60, top + 6), (x + 40, top + 6)], 3, "#9ab6d8", taper=.1, wmin=.7, seed=sd + 20, op=.8))
    return "".join(s)


def student(i, t):
    (x0, y0), (x1, y1), te = PATHS[i]
    spec = STUD[i]
    T1 = te + 1.55
    u = clamp((t - te) / (T1 - te))
    if t < te - 0.4:
        return "", -1
    x = x0 + (x1 - x0) * u
    # ступни: по газону — по прямой, на лестнице — по ступенькам (подъём рывком на каждой)
    ylin = y0 + (y1 - y0) * u
    if ylin < LAWN + 2:
        kf = (LAWN - ylin) / (LAWN - STEP_TOP) * NSTEP
        k0 = math.floor(kf)
        fr = kf - k0
        yk = LAWN - (LAWN - STEP_TOP) * (k0 + smooth(0.55, 0.95, fr)) / NSTEP
        y = yk
    else:
        y = ylin
    walking = 0 < u < 1
    ph = (t - te) * 10 + i
    pose = {"look": (0.5 if spec["face"] > 0 else -0.5, -0.3), "mouth": "smile" if t > READ + 0.1 else "flat", "brow": 0.4,
            "head_tilt": 2 * math.sin(ph * .5), "blink": max(0.0, 1 - abs((t * 0.9 + i * .6) % 2.4 - 1.2) / 0.08)}
    if walking:
        pose["walk"] = ph
    pose["hand_target"] = {"L": (-100, -335), "R": (100, -335)}
    pose["curl"] = {"L": .4, "R": .4}
    body = person.draw(spec, dict(pose, no_arms=True), x, y, SC, sd=6000 + i * 100)
    bob = -8 * abs(math.cos(ph)) if walking else 0
    stack = f'<g transform="translate({f(x)} {f(y)}) scale({SC:.4f})">{paper_stack(0, -352 + bob, 8, 6080 + i * 100)}</g>'
    arms = person.draw(spec, dict(pose, only_arms=True), x, y, SC, sd=6000 + i * 100)
    sh = blob(ellipse_pts(x + 6, y + 4, 90 * SC, 14 * SC, 12), "#6f8a5a" if y > LAWN else "#a59d8c", .5, blur(3))
    return sh + body + stack + arms, y


def build_static():
    if _ST:
        return
    _ST["sky"] = sky()
    _ST["bld"] = building()
    _ST["stairs"] = stairs()
    _ST["lawn"] = lawn()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art = [_ST["sky"], clouds(t), birds(t), _ST["lawn"], _ST["bld"], glint(t), _ST["stairs"]]
    art.append(tree(-30, BANK - 10, 560, t, 5800))
    art.append(tree(1110, BANK - 10, 600, t, 5840))
    studs = sorted((student(i, t) for i in range(4)), key=lambda p: p[1])
    art += [s for s, _ in studs]
    art.append(river(t))
    art.append(sailboat(t))
    # камера: наезд к зданию с первого кадра (наш хлёст — сборщик), толчок на блике, к лестнице на «вычитывать»
    u = clamp((t - 17.88) / (20.84 - 17.88))
    cx = 540
    cy = 800 + 90 * ease_io(u)
    sc = 1.1 + 0.3 * (0.35 * u + 0.65 * ease_io(u))
    e = t - GLINT
    if e > 0:
        k = math.exp(-e * 7)
        sc *= 1 + 0.03 * k * math.sin(min(e * 14, math.pi))
    e2 = t - READ
    if e2 > 0:
        sc *= 1 + 0.015 * math.exp(-e2 * 6) * math.sin(min(e2 * 14, math.pi))
    rot = -0.8 + 0.9 * u
    return svg(f'<rect width="{W}" height="{H}" fill="#3f86c0"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(art)}</g>')
