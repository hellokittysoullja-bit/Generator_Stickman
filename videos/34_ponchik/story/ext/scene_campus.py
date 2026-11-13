"""Сцена campus рилса 34 (s09): «В Америке девушкам в опыте…» (16.2–18.0). Американский университет днём: корпус из
красного кирпича с белым портиком (шесть колонн, фронтон, белые наличники окон, белая башенка с зелёной крышей),
широкие ступени, газон, деревья; справа флагшток — на «Америке» (16.44) флаг США взлетает по флагштоку и
разворачивается, дальше развевается (13 полос, синий крыж с белыми звёздами — без букв и логотипов). На «девушкам»
(17.04) справа по дорожке к ступеням входят три девушки (разные причёски и цвет кожи). Камера: медленный наезд.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import parts34 as P
import person
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, rad_grad,
                 rect_pts, shape, smooth, svg)

_ST = {}
AMER = P.wt("америке")          # 16.44
GIRLS = P.wt("девушкам")        # 17.04
GROUND = 1090                   # низ стены / верх ступеней
PLAZA = 1235                    # уровень площадки перед ступенями
BRICK, BRICK_SH, BRICK_DK = "#b8523a", "#97402c", "#7e3322"
WHITE, WHITE_SH = "#f6f2ea", "#d8d2c6"

GIRL_SPECS = [
    dict(skin="#8a5a3c", hair="curly", hair_c="#2a1a14", top="#d9467a", low="#2a2a3a", face=.3, lashes=True, shoes="#f2eee6"),
    dict(skin="#f4d0b4", hair="ponytail", hair_c="#c8622a", top="#3a9a6a", low="#24484a", face=.3, lashes=True, shoes="#3a3440"),
    dict(skin="#efc9a4", hair="bob", hair_c="#231a1c", top="#f0b43a", low="#3a3f6c", face=.3, lashes=True, shoes="#c94a3f"),
]


def sky():
    s = []
    lib.lin_grad([(0, "#5aa6ea", 1), (.6, "#a6d4f5", 1), (1, "#eef3f0", 1)], 0, 0, 0, 1, gid="gSky34")
    s.append(f'<rect x="-700" y="-900" width="{W + 1400}" height="{GROUND + 900}" fill="url(#gSky34)"/>')
    g = rad_grad([(0, "#fff8d8", 1), (.25, "#fff1b0", .7), (1, "#fff1b0", 0)], 930, 170, 420, 420)
    s.append(f'<rect x="-700" y="-900" width="{W + 1400}" height="{GROUND + 900}" fill="url(#{g})"/>')
    return "".join(s)


def sun(t):
    x, y = 930, 170
    s = []
    for k in range(12):
        a = k * math.pi / 6 + t * 0.35
        r0, r1 = 88, 126 + 10 * math.sin(t * 3 + k)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], 9, "#ffcf3a", taper=.4, seed=810 + k))
    s.append(shape(ellipse_pts(x, y, 68, 68, 24), "#ffd84a", blob(ellipse_pts(x + 14, y + 16, 58, 54, 18), "#f4b92e", .7) +
                   blob(ellipse_pts(x - 22, y - 24, 18, 11, 10, rot=-30), "#fff6c8", .9), w=4.6, seed=809))
    return "".join(s)


def clouds(t):
    s = []
    for k, (x0, y, sc, sp) in enumerate([(420, 150, .9, 16), (860, 260, .75, 11), (-150, 330, .8, 13)]):
        x = x0 + sp * (t - 16)
        pts = []
        for i in range(14):
            a = 2 * math.pi * i / 14
            r = 1 + .18 * math.sin(5 * a + k)
            pts.append((x + 110 * sc * math.cos(a) * r, y + 40 * sc * math.sin(a) * r * (0.75 if math.sin(a) > 0 else 1)))
        s.append(shape(pts, "#ffffff", blob(ellipse_pts(x + 20 * sc, y + 22 * sc, 90 * sc, 16 * sc, 10), "#d8e8f5"), w=3.6, seed=820 + k))
    return "".join(s)


def window(x, y, w, h, sd, arch=False):
    """Окно с белым наличником и переплётом 2×3, стекло голубое с бликом."""
    s = []
    s.append(shape(rect_pts(x - w / 2 - 10, y - 12, x + w / 2 + 10, y + h + 14), WHITE, blob(rect_pts(x - w / 2 - 10, y + h + 2, x + w / 2 + 10, y + h + 14), WHITE_SH),
                   w=3.4, seed=sd))
    glass = blob(rect_pts(x - w / 2, y, x + w / 2, y + h), "#7fb3d6")
    glass += blob([(x - w / 2, y + h * .55), (x - w / 2 + w * .5, y), (x - w / 2 + w * .8, y), (x - w / 2, y + h * .95)], "#a9d2ec", .8)
    glass += line([(x, y), (x, y + h)], 4, WHITE, taper=.05, wmin=.9, seed=sd + 2)
    for k in (1, 2):
        glass += line([(x - w / 2, y + h * k / 3), (x + w / 2, y + h * k / 3)], 4, WHITE, taper=.05, wmin=.9, seed=sd + 3 + k)
    s.append(shape(rect_pts(x - w / 2, y, x + w / 2, y + h), "#7fb3d6", glass, w=3.4, seed=sd + 1))
    s.append(shape(rect_pts(x - w / 2 - 14, y - 26, x + w / 2 + 14, y - 10), WHITE, "", w=3, seed=sd + 6))
    return "".join(s)


def brick_wall(x0, x1, y0, y1, sd):
    inner = blob([(x1 - 70, y0), (x1, y0), (x1, y1), (x1 - 70, y1)], BRICK_SH, .7)
    rs = np.random.RandomState(sd)
    for r, y in enumerate(np.arange(y0 + 22, y1, 30)):
        inner += line([(x0, y), (x1, y + 1)], 1.8, BRICK_DK, taper=.05, wmin=.7, seed=sd + r % 9, op=.45)
        off = (r % 2) * 32
        for x in np.arange(x0 + off + rs.uniform(0, 8), x1, 64):
            inner += line([(x, y), (x, y + 30)], 1.6, BRICK_DK, taper=.05, wmin=.7, seed=sd + 30 + int(x) % 7, op=.4)
    for k in range(18):
        bx, by = rs.uniform(x0, x1 - 60), y0 + 30 * rs.randint(0, int((y1 - y0) / 30))
        inner += blob(rect_pts(bx, by + 2, bx + 60, by + 28), "#c86a4e", .55)
    return shape([(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)], BRICK, inner, w=4.6, seed=sd + 99)


def column(x, y0, y1, w, sd):
    s = shape(rect_pts(x - w / 2, y0, x + w / 2, y1), WHITE,
              blob(rect_pts(x + w * .18, y0, x + w / 2, y1), WHITE_SH, .9) + line([(x - w * .18, y0 + 14), (x - w * .18, y1 - 14)], 2, WHITE_SH, seed=sd + 1, op=.8),
              w=3.6, seed=sd)
    s += shape(rect_pts(x - w / 2 - 10, y0 - 18, x + w / 2 + 10, y0), WHITE, blob(rect_pts(x - w / 2 - 10, y0 - 6, x + w / 2 + 10, y0), WHITE_SH), w=3.2, seed=sd + 2)
    s += shape(rect_pts(x - w / 2 - 10, y1, x + w / 2 + 10, y1 + 16), WHITE, blob(rect_pts(x - w / 2 - 10, y1 + 8, x + w / 2 + 10, y1 + 16), WHITE_SH), w=3.2,
               seed=sd + 3)
    return s


def building():
    s = []
    # башенка-купол за фронтоном
    s.append(shape(rect_pts(480, 300, 600, 470), WHITE, blob(rect_pts(560, 300, 600, 470), WHITE_SH) +
                   "".join(blob(rect_pts(492 + k * 36, 330, 514 + k * 36, 400, 10), "#5d7d95") for k in range(3)), w=4, seed=1301))
    s.append(shape([(470, 302), (540, 200), (610, 302)], "#5f9a7a", blob([(540, 200), (610, 302), (560, 302)], "#4a7d61"), w=4, seed=1302))
    s.append(line([(540, 200), (540, 150)], 5, INK, taper=.1, wmin=.8, seed=1303))
    s.append(shape(ellipse_pts(540, 150, 9, 9, 10), "#e8c24a", "", w=3, seed=1304))
    # крылья
    s.append(brick_wall(-300, 330, 560, GROUND, 1310))
    s.append(brick_wall(750, 1380, 560, GROUND, 1330))
    for k, x in enumerate((-180, -20, 140, 290)):
        s.append(window(x, 640, 80, 140, 1400 + k * 10))
        s.append(window(x, 860, 80, 140, 1450 + k * 10))
    for k, x in enumerate((790, 940, 1100, 1260)):
        s.append(window(x, 640, 80, 140, 1500 + k * 10))
        s.append(window(x, 860, 80, 140, 1550 + k * 10))
    for x0, x1, sd in ((-320, 340, 1600), (740, 1400, 1610)):
        s.append(shape(rect_pts(x0, 530, x1, 562), WHITE, blob(rect_pts(x0, 550, x1, 562), WHITE_SH), w=3.6, seed=sd))
        s.append(shape([(x0 - 10, 532, 1), (x0 + 30, 496, 1), (x1 - 30, 496, 1), (x1 + 10, 532, 1)], "#5b5f6e", blob(rect_pts(x0, 520, x1, 532), "#454856"), w=3.6, seed=sd + 1))
    # центральный корпус
    s.append(brick_wall(300, 780, 470, GROUND, 1620))
    # дверь и окна за колоннами
    s.append(shape(rect_pts(480, 860, 600, GROUND - 4, 6), "#6b3a26", blob(rect_pts(540, 860, 600, GROUND), "#552c1c") +
                   line([(540, 870), (540, GROUND - 8)], 3, INK, seed=1631, op=.8) + f'<circle cx="528" cy="980" r="5" fill="#e8c24a"/><circle cx="552" cy="980" r="5" fill="#e8c24a"/>',
                   w=4, seed=1630))
    s.append(shape([(470, 862), (540, 800), (610, 862)], WHITE, blob([(540, 800), (610, 862), (570, 862)], WHITE_SH), w=3.4, seed=1632))
    s.append(window(375, 680, 64, 120, 1640))
    s.append(window(705, 680, 64, 120, 1650))
    # фронтон и антаблемент
    s.append(shape(rect_pts(280, 556, 800, 600), WHITE, blob(rect_pts(280, 586, 800, 600), WHITE_SH) +
                   "".join(blob(rect_pts(296 + k * 34, 562, 312 + k * 34, 580), WHITE_SH, .8) for k in range(15)), w=4.2, seed=1660))
    s.append(shape([(262, 558, 1), (540, 430, 1), (818, 558, 1)], WHITE, blob([(540, 430), (818, 558), (640, 558)], WHITE_SH, .9) +
                   shape([(330, 540, 1), (540, 456, 1), (750, 540, 1)], "#ece6da", "", w=2.6, seed=1662), w=4.6, seed=1661))
    s.append(shape(ellipse_pts(540, 510, 22, 22, 14), "#ece6da", line([(540, 494), (540, 510), (552, 516)], 3, INK, seed=1664), w=3, seed=1663))
    for k, x in enumerate((318, 406, 494, 586, 674, 762)):
        s.append(column(x, 618, GROUND - 16, 40, 1700 + k * 5))
    return "".join(s)


def steps():
    s = []
    n = 5
    for k in range(n):
        y0 = GROUND + k * (PLAZA - GROUND) / n
        y1 = y0 + (PLAZA - GROUND) / n
        x0, x1 = 270 - k * 26, 810 + k * 26
        s.append(shape(rect_pts(x0, y0, x1, y1), "#ece4d6", blob(rect_pts(x0, y1 - 9, x1, y1), "#cfc6b6"), w=3.4, seed=1800 + k))
    return "".join(s)


def lawn():
    s = []
    s.append(f'<rect x="-700" y="{GROUND}" width="{W + 1400}" height="1400" fill="#7fbf5e"/>')
    s.append(line([(-700, GROUND), (W + 700, GROUND)], 4.4, INK, taper=.05, wmin=.9, seed=1901))
    s.append(blob([(-700, PLAZA - 6), (W + 700, PLAZA - 6), (W + 700, H + 600), (-700, H + 600)], "#e7dcc4"))
    s.append(line([(-700, PLAZA - 6), (W + 700, PLAZA - 6)], 3.6, INK, taper=.05, wmin=.9, seed=1902))
    for k in range(6):
        y = PLAZA + 50 + k * 60 + k * k * 8
        s.append(line([(-700, y), (W + 700, y + 3)], 2.2, "#cdbf9f", taper=.1, wmin=.7, seed=1910 + k, op=.8))
    rs = np.random.RandomState(19)
    for k in range(40):
        x, y = rs.uniform(-200, W + 200), rs.uniform(GROUND + 14, PLAZA - 20)
        if 240 < x < 840:
            continue
        s.append(line([(x, y), (x + 3, y - 12)], 2.4, "#5a9a42", seed=1920 + k % 9, op=.8))
    # кусты у ступеней
    for k, (x, sc) in enumerate(((200, 1.0), (880, 1.0))):
        s.append(shape(P.cloud_pts(x, GROUND + 10, 90 * sc, 46 * sc, 6, 1950 + k), "#4f9a46", blob(ellipse_pts(x + 20, GROUND + 30, 70, 20, 10), "#3d7c38"),
                       w=4, seed=1960 + k))
    return "".join(s)


def tree(x, y, h, t, sd, sc=1.0):
    sway = 4 * math.sin(t * 1.2 + sd)
    s = shape(lib.band([(x, y), (x + 4, y - h * .5), (x + 2 + sway * .3, y - h * .8)], 46 * sc, 26 * sc, step=6, cap=False), "#8a6238",
              blob(lib.band([(x + 12, y), (x + 14, y - h * .5), (x + 10, y - h * .8)], 16 * sc, 10 * sc, step=6, cap=False), "#6a4628", .9), w=4, seed=sd)
    for k, (dx, dy, r) in enumerate(((-90, -1.0, 120), (80, -1.05, 120), (0, -1.25, 140), (-40, -0.85, 100), (60, -0.82, 100))):
        cx, cy = x + dx * sc + sway * (1 + k * .2), y + h * dy
        s += shape(P.cloud_pts(cx, cy, r * sc, r * .8 * sc, 7, sd + 10 + k), "#5aaa4e" if k % 2 else "#4f9a46",
                   blob(ellipse_pts(cx + 30 * sc, cy + 34 * sc, r * .8 * sc, r * .45 * sc, 12), "#3d7c38", .85) +
                   blob(ellipse_pts(cx - 30 * sc, cy - 30 * sc, r * .35 * sc, r * .2 * sc, 10), "#7cc46a", .8), w=4, seed=sd + 20 + k)
    return s


# ═══════════════════════════════ флаг США
POLE_X, POLE_TOP, POLE_BOT = 110, 280, 1150
FL, FH = 310, 180


def flag(t):
    """Флаг на флагштоке: на «Америке» взлетает вверх (16.24–16.58), разворачивается и развевается волной."""
    rise = ease_out(clamp((t - (AMER - 0.2)) / 0.34), 3)
    unf = ease_out(clamp((t - (AMER - 0.05)) / 0.45), 2)
    y0 = POLE_TOP + 20 + (1 - rise) * 640
    L = FL * (0.25 + 0.75 * unf)
    amp = 22 * (1.6 - 0.6 * unf)
    ph = t * 7.5

    def pt(u, v):
        x = POLE_X + 8 + u * L
        y = y0 + v * FH * (1 - 0.12 * u * (1 - unf)) + amp * math.sin(3.4 * u - ph) * u + 30 * u * (1 - unf) * u
        x -= 8 * math.cos(3.4 * u - ph) * u
        return (x, y)

    us = np.linspace(0, 1, 22)
    s = []
    # полосы
    for i in range(13):
        v0, v1 = i / 13, (i + 1) / 13
        pts = [pt(u, v0) for u in us] + [pt(u, v1) for u in us[::-1]]
        s.append(f'<path d="{lib.fill_d(pts)}" fill="{"#c8283a" if i % 2 == 0 else "#ffffff"}"/>')
    # крыж
    uc, vc = 0.42, 7 / 13
    uu = np.linspace(0, uc, 12)
    pts = [pt(u, 0) for u in uu] + [pt(uc, v) for v in np.linspace(0, vc, 6)] + [pt(u, vc) for u in uu[::-1]]
    s.append(f'<path d="{lib.fill_d(pts)}" fill="#2a3f8f"/>')
    for r in range(5):
        for c in range(6 if r % 2 == 0 else 5):
            u = uc * (c + (0.5 if r % 2 == 0 else 1.0)) / 6.0
            v = vc * (r + 0.6) / 5.6
            x, y = pt(u, v)
            st = [(x + (7 if j % 2 == 0 else 2.8) * math.cos(math.radians(-90 + 36 * j)), y + (7 if j % 2 == 0 else 2.8) * math.sin(math.radians(-90 + 36 * j)))
                  for j in range(10)]
            s.append(f'<path d="M{" L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in st)}Z" fill="#ffffff"/>')
    # складки-тени по волне
    for k in range(1, 8):
        u = k / 8
        sl = math.cos(3.4 * u - ph)
        if sl > 0.3:
            pts = [pt(u - 0.03, v) for v in np.linspace(0, 1, 8)] + [pt(u + 0.03, v) for v in np.linspace(1, 0, 8)]
            s.append(f'<path d="{lib.fill_d(pts)}" fill="#1c1622" opacity="{0.16 * (sl - 0.3):.3f}"/>')
    outline = [pt(u, 0) for u in us] + [pt(1, v) for v in np.linspace(0, 1, 8)[1:]] + [pt(u, 1) for u in us[::-1]] + [pt(0, v) for v in np.linspace(1, 0, 8)[1:]]
    s.append(f'<path d="{lib.ink_closed(outline, 4.2, seed=2100)}" fill="{INK}"/>')
    return "".join(s)


def pole():
    s = shape(rect_pts(POLE_X - 7, POLE_TOP, POLE_X + 7, POLE_BOT), "#c9ced8", blob(rect_pts(POLE_X + 1, POLE_TOP, POLE_X + 7, POLE_BOT), "#9aa2b2"), w=3.4, seed=2200)
    s += shape(ellipse_pts(POLE_X, POLE_TOP - 6, 14, 14, 12), "#e8c24a", blob(ellipse_pts(POLE_X + 4, POLE_TOP - 2, 8, 8, 8), "#c9a030"), w=3.2, seed=2201)
    s += shape(rect_pts(POLE_X - 40, POLE_BOT - 6, POLE_X + 40, POLE_BOT + 24, 4), "#d8d2c6", "", w=3.4, seed=2202)
    return s


# ═══════════════════════════════ девушки
def girls(t):
    """Три девушки идут справа налево к ступеням (с «девушкам»), чуть врассыпную, у каждой свой шаг."""
    out = []
    e = t - (GIRLS - 0.35)
    for i, spec in enumerate(GIRL_SPECS):
        x0 = 1200 + i * 150
        v = 330 - i * 14
        x = x0 - v * max(0.0, e) - 40 * max(0.0, e) ** 2
        y = PLAZA + 48 + i * 22
        if x > 1500:
            continue
        ph = max(0.0, e) * 10.5 + i * 1.3
        pose = {"walk": ph, "look": (0.5, 0.0 if i != 1 else -0.2), "mouth": "smile", "brow": 0.4,
                "head_tilt": 3 * math.sin(ph + i), "blink": P.bump(t, 17.5 + i * 0.13, 0.14), "curl": {"L": .6, "R": .6}}
        sc = 0.6 + i * 0.02
        out.append((y, blob(ellipse_pts(x - 6, y + 6, 100 * sc, 14 * sc, 12), "#9a8a6a", .45, blur(4)) +
                    person.draw(spec, pose, x, y, sc, sd=2400 + i * 100, flip=True)))
    out.sort()
    return "".join(o for _, o in out)


def s09(t):
    art = [_ST["sky"], sun(t), clouds(t), _ST["trees_back"], _ST["building"], _ST["lawn"], _ST["steps"]]
    art.append(tree(-40, GROUND + 30, 520, t, 2500, 1.15))
    art.append(tree(1120, GROUND + 30, 480, t, 2550, 1.05))
    art.append(pole())
    art.append(flag(t))
    art.append(P.pop_lines(POLE_X + 160, 370, t - AMER, 150, 230, 7, col="#ffd23a", w=9, sd=2600))
    art.append(girls(t))
    # камера: медленный наезд с первого кадра + толчок на «Америке»
    u = clamp((t - 16.0) / 2.2)
    sc = 1.0 + 0.07 * ease_io(u) + 0.025 * P.kick(t, AMER, 6, 14) + 0.012 * P.kick(t, GIRLS, 6, 14)
    return "".join(art), cam(550 + 30 * u, 990 + 20 * u, sc, -0.6 + 0.9 * u)


def build_static():
    if _ST:
        return
    _ST["sky"] = sky()
    _ST["building"] = building()
    _ST["lawn"] = lawn()
    _ST["steps"] = steps()
    _ST["trees_back"] = (shape(P.cloud_pts(-200, 560, 240, 120, 9, 2700), "#6fae5a", "", w=4, seed=2701) +
                         shape(P.cloud_pts(1300, 560, 260, 120, 9, 2710), "#6fae5a", "", w=4, seed=2711))
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = s09(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#a6d4f5"/><g transform="{cm}">{art}</g>')
