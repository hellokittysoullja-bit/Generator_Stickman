"""Сцена study рилса 27 (s08–s11): исследование в Англии (Przybylski, Weinstein 2012). Светлая комната, в окне —
кирпичные дома террасы и красная телефонная будка вдали; маленький стол, две чашки, двое незнакомых взрослых
(person.py с кистями из пяти пальцев — hands5.py).
s08 (15.44–18.40) двое садятся друг напротив друга, лёгкая панорама.
s09 (18.00–20.40) крупно край стола: рука исследователя в белом рукаве кладёт чёрный телефон к «телефон» (19.40).
s10 (20.00–22.92) разговаривают, телефон на столе; сцена холодеет, термометр тепла на стене падает на «холоднее» (21.947),
     на столе и чашках иней.
s11 (22.52–24.92) вид вдоль стола из-за плеча: стол растягивается, человек напротив уезжает вдаль на «дальше» (23.92).
Ни одной буквы. Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import person
import scene_street as st
from hands5 import hand5
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
PHONE_T = 19.40      # «телефон»
COLD_T = 21.947      # «холоднее»
FAR_T = 23.92        # «дальше»

FLOOR_Y = 1250       # низ задней стены
FEET_Y = 1268        # где стоят ступни сидящих
TOP_B, TOP_F = 1000, 1046      # стол: задний и передний край столешницы
TX0, TX1 = 375, 705
SC_P = 0.95

WALL = "#efe6d3"
WALL_SH = "#e2d6bd"
PANEL = "#cfdccb"
PANEL_SH = "#b8c8b4"
WOOD = "#c79466"
WOOD_SH = "#a8774d"
WOOD_HI = "#ddb084"

# ───────────────────────── люди
A_SPEC = dict(skin="#f1c7a6", hair="bob", hair_c="#8a3f22", top="#2f8f8a", low="#3b3f58", shoes="#5a3a2a", face=.72, h=.96,
              sleeve="#2f8f8a", collar="#f4efe2", brow_c="#6a2e18")
B_SPEC = dict(skin="#c48a64", hair="bald", hair_c="#c9c4bd", top="#33467a", low="#4a4136", shoes="#2a2420", face=-.72, glasses=True,
              beard="#d9d4cc", bw=1.08, h=1.02, brow_c="#e0dbd3")


def ik(sh, tgt, L1=130, L2=120):
    """Двухзвенная рука: плечо sh → кисть tgt (локальные координаты человека). Углы как в person.limb (0 — вниз)."""
    dx, dy = tgt[0] - sh[0], tgt[1] - sh[1]
    L = max(abs(L1 - L2) + 1, min(L1 + L2 - 0.5, math.hypot(dx, dy)))
    base = math.degrees(math.atan2(dx, dy))
    c = clamp((L1 * L1 + L * L - L2 * L2) / (2 * L1 * L), -1, 1)
    d = math.degrees(math.acos(c))
    a1 = min((base - d, base + d), key=lambda a: abs(((a + 180) % 360) - 180))
    ex, ey = sh[0] + L1 * math.sin(math.radians(a1)), sh[1] + L1 * math.cos(math.radians(a1))
    a_f = math.degrees(math.atan2(tgt[0] - ex, tgt[1] - ey))
    return a1, a_f - a1


def seat_person(spec, k, feet_x, floor_y, sc, hands=None, pose=None, sd=0, rot=0.0):
    """Человек садится: k 0 — стоит, 1 — сидит (бедро горизонтально, голень вертикально), ступни стоят на месте.
    hands — {'L': (x, y) мир, 'R': ...} куда положить кисти (решается IK), иначе руки висят."""
    pose = dict(pose or {})
    dr = 1 if spec["face"] >= 0 else -1
    S = sc * spec.get("h", 1.0)
    a1 = 90 * k
    pose["legs"] = {"L": (a1, a1), "R": (a1, a1)}
    foot_y = min(-20.0, -300 + 140 * math.cos(math.radians(a1)) + 140)
    ox = feet_x - dr * 140 * math.sin(math.radians(a1)) * S
    oy = floor_y - (foot_y + 22) * S
    if hands:
        sh_w = 74 * spec.get("bw", 1.0)
        shs = {"L": (-sh_w + 10, -502), "R": (sh_w - 10, -502)}
        arms = {}
        for side, tw in hands.items():
            tl = ((tw[0] - ox) / S, (tw[1] - oy) / S)
            a, b = ik(shs[side], tl)
            sign = -1 if side == "L" else 1
            arms[side] = (a - sign * 6, b)
        pose["arms"] = arms
        pose["near_front"] = True
    g = person.draw(spec, pose, ox, oy, sc, sd=sd)
    if rot:
        g = f'<g transform="rotate({f(rot)} {f(feet_x)} {f(floor_y)})">{g}</g>'
    return g, (ox, oy, S)


def mouth_talk(t, t0, t1, rate=7.0, ph=0.0):
    if not (t0 <= t < t1):
        return None
    v = math.sin((t - t0) * rate * 2 * math.pi / 2 + ph) + 0.5 * math.sin((t - t0) * 17 + ph)
    return "o" if v > 0.35 else ("flat" if v > -0.6 else "smile")


def blink_at(t, period, ph):
    u = (t + ph) % period
    return 1.0 if u < 0.09 else 0.0


# ───────────────────────── комната (вид сбоку)
def outside():
    """Вид из окна: небо, ряд кирпичных домов террасы (scene_street.house уменьшенные), красная будка вдали."""
    s = []
    lin_grad([(0, "#a9cdea", 1), (.7, "#dbeaf3", 1), (1, "#f6efe0", 1)], 0, 0, 0, 1, gid="gSkyW")
    s.append(f'<rect x="300" y="300" width="480" height="620" fill="url(#gSkyW)"/>')
    for k, (x, y, r) in enumerate([(430, 380, 34), (690, 360, 28)]):
        pts = [(x + 1.9 * r * (1 + .2 * math.sin(3 * a + k)) * math.cos(a), y + .7 * r * (1 + .2 * math.sin(3 * a + k)) * math.sin(a))
               for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)]
        s.append(shape(pts, "#ffffff", "", w=2.6, seed=20 + k))
    # дальний ряд домов: исходник 300×(≈700) в масштабе 0.36
    houses = "".join(st.house(-420 + k * 300, 300, k) for k in range(6))
    s.append(f'<g transform="translate(250 512) scale(0.36) translate(0 -300)">{houses}</g>')
    # тротуар и улица
    s.append(f'<rect x="300" y="768" width="480" height="40" fill="#cfcac0"/>')
    s.append(f'<rect x="300" y="806" width="480" height="120" fill="#6a6f78"/>')
    s.append(line([(300, 806), (780, 806)], 3, INK, taper=.05, wmin=.9, seed=31))
    # будка вдали (справа), рядом дерево
    s.append(f'<g transform="translate(640 800) scale(0.36) translate(0 0)">{st.booth(0, 0)}</g>')
    tr = [(574, 800, 1), (580, 700), (586, 800, 1)]
    s.append(shape(tr, "#6b4a32", "", w=2.6, seed=40))
    s.append(shape(ellipse_pts(580, 680, 46, 52, 14, jitter=.08, seed=3), "#6fa35a",
                   blob(ellipse_pts(596, 696, 36, 36, 12), "#53844a", .9), w=3, seed=41))
    return "".join(s)


def window():
    s = []
    x0, y0, x1, y1 = 330, 330, 750, 900
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    s.append(f'<g clip-path="url(#{c})">{outside()}</g>')
    # переплёт «гильотина»: 2 створки, по 2×2 стекла
    fr = "#fbf8f0"
    s.append(f'<rect x="{x0}" y="{(y0 + y1) / 2 - 9}" width="{x1 - x0}" height="18" fill="{fr}"/>')
    s.append(f'<rect x="{(x0 + x1) / 2 - 7}" y="{y0}" width="14" height="{y1 - y0}" fill="{fr}"/>')
    for k in (1,):
        pass
    s.append(line([(x0, (y0 + y1) / 2 - 9), (x1, (y0 + y1) / 2 - 9)], 2.6, INK, taper=.05, wmin=.9, seed=50))
    s.append(line([(x0, (y0 + y1) / 2 + 9), (x1, (y0 + y1) / 2 + 9)], 2.6, INK, taper=.05, wmin=.9, seed=51))
    s.append(line([((x0 + x1) / 2 - 7, y0), ((x0 + x1) / 2 - 7, y1)], 2.4, INK, taper=.05, wmin=.9, seed=52))
    s.append(line([((x0 + x1) / 2 + 7, y0), ((x0 + x1) / 2 + 7, y1)], 2.4, INK, taper=.05, wmin=.9, seed=53))
    # блики на стекле
    for (gx, gy) in [(x0 + 20, y0 + 30), (x1 - 150, (y0 + y1) / 2 + 40)]:
        s.append(blob([(gx, gy + 120), (gx + 70, gy), (gx + 100, gy), (gx + 30, gy + 120)], "#ffffff", .35))
    # рама
    frame = rect_pts(x0 - 26, y0 - 26, x1 + 26, y1 + 26)
    hole = rect_pts(x0, y0, x1, y1)
    d = lib.fill_d(frame) + lib.fill_d(hole[::-1])
    s.append(f'<path d="{d}" fill="{fr}" fill-rule="evenodd"/>')
    s.append(f'<path d="{lib.ink_closed(frame, 4.6, seed=54)}" fill="{INK}"/>')
    s.append(f'<path d="{lib.ink_closed(hole, 3.6, seed=55)}" fill="{INK}"/>')
    s.append(blob(rect_pts(x1 + 2, y0 - 20, x1 + 26, y1 + 26), "#e4dccb", .9))
    # подоконник
    s.append(shape(rect_pts(x0 - 46, y1 + 22, x1 + 46, y1 + 46, 4), "#fbf8f0", blob(rect_pts(x0 - 46, y1 + 36, x1 + 46, y1 + 46), "#e4dccb"),
                   w=3.6, seed=56))
    # шторы
    for side in (-1, 1):
        xc = x0 - 70 if side < 0 else x1 + 70
        pts = [(xc - 52, y0 - 60), (xc + 52, y0 - 60), (xc + 40 + side * 6, (y0 + y1) / 2), (xc + 58, y1 + 120, 1), (xc - 58, y1 + 120, 1),
               (xc - 40 + side * 6, (y0 + y1) / 2)]
        inner = "".join(line([(xc + dx, y0 - 50), (xc + dx * 1.15, y1 + 110)], 2.6, "#b9c9dc", seed=60 + int(dx) + side, op=.9) for dx in (-22, 4, 28))
        inner += blob([(xc + 10, y0 - 60), (xc + 52, y0 - 60), (xc + 58, y1 + 120), (xc + 20, y1 + 120)], "#c9d7e8", .9)
        s.append(shape(pts, "#e3ebf4", inner, w=3.8, seed=64 + side))
    s.append(shape(rect_pts(x0 - 150, y0 - 74, x1 + 150, y0 - 60, 6), "#9a7a58", "", w=3, seed=68))
    return "".join(s)


def picture(x0, y0, x1, y1, sd):
    inner = blob(rect_pts(x0, y0, x1, y1), "#bfd8e8")
    inner += blob([(x0, y1 - 40), (x0 + 60, y1 - 80), (x0 + 110, y1 - 50), (x1, y1 - 90), (x1, y1), (x0, y1)], "#7fae7a")
    inner += blob([(x0, y1 - 20), (x0 + 80, y1 - 44), (x1, y1 - 30), (x1, y1), (x0, y1)], "#5f8f5e")
    inner += f'<circle cx="{f(x1 - 36)}" cy="{f(y0 + 34)}" r="16" fill="#ffe08a"/>'
    s = shape(rect_pts(x0 - 14, y0 - 14, x1 + 14, y1 + 14), "#b07d4f", "", w=4, seed=sd)
    s += shape(rect_pts(x0, y0, x1, y1), "#bfd8e8", inner, w=3, seed=sd + 1)
    return s


def plant(x, y, t, sd):
    s = [blob(ellipse_pts(x + 16, y + 4, 80, 12, 12), "#6f5a44", .35, blur(5))]
    rs = np.random.RandomState(sd)
    leaves = []
    for k in range(9):
        a = -math.pi / 2 + (k - 4) * 0.28 + rs.uniform(-.1, .1)
        L = rs.uniform(150, 230)
        sw = 3 * math.sin(t * 1.3 + k)
        bx, by = x + rs.uniform(-12, 12), y - 120
        tx, ty = bx + math.cos(a) * L + sw, by + math.sin(a) * L
        mx, my = (bx + tx) / 2, (by + ty) / 2
        nx, ny = -(ty - by) / L, (tx - bx) / L
        pts = [(bx, by, 1), (mx + nx * 26, my + ny * 26), (tx, ty, 1), (mx - nx * 26, my - ny * 26)]
        col = ["#5f9a52", "#4f8a48", "#6fae5e"][k % 3]
        leaves.append(shape(pts, col, line([(bx, by), (mx, my), (tx, ty)], 2.2, "#3d6e3a", seed=sd + 30 + k, op=.8), w=3, seed=sd + k))
    s += leaves
    pot = [(x - 62, y - 130, 1), (x + 62, y - 130, 1), (x + 48, y, 1), (x - 48, y, 1)]
    s.append(shape(pot, "#d9744e", blob([(x + 10, y - 130), (x + 62, y - 130), (x + 48, y), (x + 14, y)], "#b85a3a", .9), w=4, seed=sd + 20))
    s.append(shape(rect_pts(x - 70, y - 146, x + 70, y - 122, 4), "#e08a62", "", w=3.6, seed=sd + 21))
    return "".join(s)


def tripod_cam(x, y, t):
    """Камера исследователей на штативе в углу: лампочка записи мигает."""
    s = []
    for dx in (-60, 0, 54):
        s.append(line([(x, y - 330), (x + dx, y)], 7, "#3a3d46", taper=.05, wmin=.85, seed=80 + dx))
    s.append(shape(rect_pts(x - 70, y - 400, x + 50, y - 320, 10), "#2b2e36",
                   blob(rect_pts(x - 70, y - 352, x + 50, y - 320, 8), "#1d1f25") + line([(x - 58, y - 388), (x + 30, y - 388)], 3, "#5a5f6c", seed=86),
                   w=4, seed=84))
    s.append(shape(rect_pts(x - 112, y - 392, x - 66, y - 330, 8), "#3a3d46", "", w=3.6, seed=85))
    s.append(shape(ellipse_pts(x - 118, y - 361, 14, 30, 12), "#1a1c22", blob(ellipse_pts(x - 121, y - 370, 4, 9, 8), "#8aa0c8", .9), w=3, seed=87))
    on = 1.0 if (t * 1.25) % 1 < 0.55 else 0.25
    s.append(f'<circle cx="{f(x + 34)}" cy="{f(y - 410)}" r="9" fill="{mix("#5a2020", "#ff3b30", on)}" stroke="{INK}" stroke-width="2.6"/>')
    return "".join(s)


def room_static():
    s = []
    s.append(f'<rect x="-400" y="-400" width="{W + 800}" height="{FLOOR_Y + 400}" fill="{WALL}"/>')
    # вертикальные полосы-обои (едва заметно)
    for k in range(-6, 22):
        s.append(f'<rect x="{k * 70}" y="-400" width="28" height="{FLOOR_Y - 400 + 400 - 210}" fill="{WALL_SH}" opacity=".35"/>')
    # панели снизу и бордюр
    s.append(f'<rect x="-400" y="{FLOOR_Y - 230}" width="{W + 800}" height="230" fill="{PANEL}"/>')
    for k in range(-4, 16):
        x = k * 120 + 30
        s.append(shape(rect_pts(x, FLOOR_Y - 196, x + 96, FLOOR_Y - 46, 6), PANEL, blob(rect_pts(x + 70, FLOOR_Y - 196, x + 96, FLOOR_Y - 46), PANEL_SH, .8),
                       w=2.6, seed=100 + k))
    s.append(shape(rect_pts(-400, FLOOR_Y - 244, W + 400, FLOOR_Y - 226), "#f7f1e4", "", w=3.4, seed=120))
    s.append(shape(rect_pts(-400, FLOOR_Y - 26, W + 400, FLOOR_Y + 2), "#f7f1e4", "", w=3.4, seed=121))
    # мягкий свет из окна на стену
    g = rad_grad([(0, "#fff8e6", .8), (1, "#fff8e6", 0)], 540, 640, 560, 480)
    s.append(f'<rect x="-400" y="-400" width="{W + 800}" height="{FLOOR_Y + 400}" fill="url(#{g})"/>')
    s.append(window())
    s.append(picture(90, 470, 220, 590, 140))
    s.append(picture(880, 520, 980, 640, 150))
    # пол: доски
    lin_grad([(0, "#c08b5d", 1), (1, "#d4a476", 1)], 0, 0, 0, 1, gid="gFloorS")
    s.append(f'<rect x="-400" y="{FLOOR_Y}" width="{W + 800}" height="{H}" fill="url(#gFloorS)"/>')
    for i, y in enumerate([1290, 1350, 1430, 1540, 1690, 1880]):
        s.append(line([(-400, y), (W + 400, y)], 2.6, "#9c6c44", taper=.05, wmin=.9, seed=130 + i, op=.8))
    for i, x in enumerate(range(-300, W + 400, 160)):
        s.append(line([(x, FLOOR_Y), (x + (x - 540) * 1.2, H + 100)], 2.2, "#a8774d", taper=.05, wmin=.9, seed=140 + i, op=.55))
    s.append(blob(rect_pts(-400, FLOOR_Y, W + 400, FLOOR_Y + 30), "#a8774d", .45))
    return "".join(s)


def chair(x, dr, sd):
    """Стул сбоку: сиденье, ножки, спинка с той стороны, куда человек сидит спиной (dr — куда смотрит)."""
    s = []
    seat_y = 1124
    xb = x - dr * 70          # спинка сзади
    xf = x + dr * 92
    col, sh = "#b5845a", "#8f6340"
    for k, lx in enumerate((xb, xf)):
        s.append(shape(rect_pts(min(lx, lx + 16) - 8, seat_y + 10, max(lx, lx + 16) + 8, FEET_Y + (4 if k else -4)), sh, "", w=3.2, seed=sd + k))
    post = rect_pts(xb - 9, seat_y - 300, xb + 9, seat_y + 12)
    s.append(shape(post, col, blob(rect_pts(xb + 2, seat_y - 300, xb + 9, seat_y + 12), sh, .8), w=3.4, seed=sd + 5))
    # перекладины спинки
    for j, yy in enumerate((seat_y - 280, seat_y - 210)):
        a, b = (xb, xb + dr * 40)
        s.append(shape(rect_pts(min(a, b) - 6, yy, max(a, b) + 6, yy + 22, 6), col, "", w=3, seed=sd + 8 + j))
    seat = [(min(xb, xf) - 14, seat_y, 1), (max(xb, xf) + 14, seat_y, 1), (max(xb, xf) + 14, seat_y + 20, 1), (min(xb, xf) - 14, seat_y + 20, 1)]
    s.append(shape(seat, col, blob(rect_pts(min(xb, xf) - 14, seat_y + 10, max(xb, xf) + 14, seat_y + 20), sh), w=3.6, seed=sd + 3))
    return "".join(s)


def table_back():
    """Дальние ножки стола (за людьми не прячутся — они у дальнего края)."""
    s = []
    for k, x in enumerate((TX0 + 34, TX1 - 34)):
        s.append(shape(rect_pts(x - 10, TOP_F, x + 10, FLOOR_Y + 6), WOOD_SH, "", w=3.2, seed=200 + k))
    return "".join(s)


def table_top(frost=0.0):
    s = []
    top = [(TX0 + 20, TOP_B, 1), (TX1 - 20, TOP_B, 1), (TX1, TOP_F, 1), (TX0, TOP_F, 1)]
    inner = blob([(TX0 + 20, TOP_B), (TX1 - 20, TOP_B), (TX1 - 8, TOP_B + 20), (TX0 + 10, TOP_B + 20)], WOOD_HI, .7)
    for k in range(3):
        y = TOP_B + 12 + k * 11
        inner += line([(TX0 + 30 + k * 8, y), (TX1 - 40 - k * 6, y + 2)], 1.8, WOOD_SH, taper=.4, seed=210 + k, op=.6)
    s.append(shape(top, WOOD, inner, w=4.2, seed=205))
    s.append(shape(rect_pts(TX0, TOP_F, TX1, TOP_F + 24), WOOD_SH, blob(rect_pts(TX0, TOP_F + 14, TX1, TOP_F + 24), "#8a5f3c", .8), w=3.8, seed=206))
    return "".join(s)


def table_front():
    s = []
    for k, x in enumerate((TX0 + 16, TX1 - 16)):
        s.append(shape(rect_pts(x - 12, TOP_F + 22, x + 12, FEET_Y + 4), WOOD, blob(rect_pts(x + 2, TOP_F + 22, x + 12, FEET_Y + 4), WOOD_SH, .9),
                       w=3.4, seed=220 + k))
    return "".join(s)


def cup(x, y, sd, steam_t=None, frost=0.0):
    """Чашка с блюдцем на столе: x — центр, y — низ."""
    s = []
    s.append(shape(ellipse_pts(x, y, 46, 10, 16), "#fbf8f0", blob(ellipse_pts(x + 6, y + 3, 40, 7, 12), "#d9d2c2"), w=3, seed=sd))
    body = [(x - 30, y - 50, 1), (x + 30, y - 50, 1), (x + 26, y - 14), (x + 14, y - 4), (x - 14, y - 4), (x - 26, y - 14)]
    s.append(shape([(x + 26, y - 42), (x + 46, y - 40), (x + 48, y - 24), (x + 26, y - 18), (x + 26, y - 26), (x + 38, y - 28), (x + 38, y - 36),
                    (x + 26, y - 36)], "#f2ece0", "", w=3, seed=sd + 1))
    s.append(shape(body, "#f6f1e6", blob([(x + 6, y - 50), (x + 30, y - 50), (x + 26, y - 14), (x + 14, y - 4), (x + 4, y - 4)], "#ddd4c2", .9) +
                   f'<rect x="{f(x - 30)}" y="{f(y - 40)}" width="60" height="8" fill="#5aa0a0" opacity=".9"/>', w=3.2, seed=sd + 2))
    s.append(shape(ellipse_pts(x, y - 50, 30, 7, 14), "#8a5a34", blob(ellipse_pts(x - 6, y - 51, 14, 3, 8), "#b07a4a", .9), w=2.8, seed=sd + 3))
    if steam_t is not None:
        a = 1 - frost
        for k in range(2):
            ph = (steam_t * 0.7 + k * 0.5) % 1
            yy = y - 64 - ph * 60
            xx = x - 10 + k * 18 + 6 * math.sin(steam_t * 3 + k)
            s.append(line([(xx, yy + 30), (xx + 8, yy + 15), (xx - 4, yy), (xx + 4, yy - 14)], 4, "#ffffff", taper=.6, seed=sd + 10 + k,
                          op=.65 * a * math.sin(math.pi * ph)))
    if frost > 0.01:
        s.append(frost_rim([(x - 30, y - 50), (x, y - 56), (x + 30, y - 50)], frost, sd + 30))
        s.append(frost_rim([(x - 44, y + 2), (x, y + 10), (x + 44, y + 2)], frost * .8, sd + 31))
        s.append(crystal(x - 16, y - 30, 8 * frost, sd + 32, frost))
        s.append(crystal(x + 14, y - 22, 6 * frost, sd + 33, frost))
    return "".join(s)


def cups(t, frost=0.0):
    out = ""
    for (x, y, sd, ph) in ((508, 1014, 500, 0.0), (574, 1010, 520, 0.3)):
        c = cup(0, 0, sd, steam_t=t + ph, frost=frost)
        out += f'<g transform="translate({x} {y}) scale(0.84)">{c}</g>'
    return out


# ───────────────────────── иней
def crystal(x, y, r, sd, a=1.0):
    if r < 0.5:
        return ""
    s = []
    for k in range(3):
        ang = math.radians(k * 60 + sd * 7)
        dx, dy = math.cos(ang) * r, math.sin(ang) * r
        s.append(line([(x - dx, y - dy), (x + dx, y + dy)], max(1.6, r * .22), "#ffffff", taper=.3, wmin=.4, seed=sd + k, op=.95 * a))
    return "".join(s)


def frost_rim(pts, a, sd):
    return line(pts, 5, "#f4fbff", taper=.3, wmin=.5, seed=sd, op=.9 * clamp(a))


def table_frost(a, sd=900):
    """Иней по краю столешницы: светлая рваная кромка + звёздочки-кристаллы."""
    if a <= 0.01:
        return ""
    s = []
    rs = np.random.RandomState(sd)
    # кромка по переднему и заднему краю
    for (y, k) in ((TOP_F - 3, 0), (TOP_B + 4, 1)):
        x0 = TX0 + (0 if k == 0 else 20)
        x1 = TX1 - (0 if k == 0 else 20)
        n = 26
        pts = [(x0 + (x1 - x0) * i / n, y + (-1 if k == 0 else 1) * (3 + 5 * rs.uniform()) * a) for i in range(n + 1)]
        s.append(line(pts, 6, "#f4fbff", taper=.1, wmin=.6, seed=sd + k, op=.85 * a))
    for i in range(14):
        x = rs.uniform(TX0 + 20, TX1 - 20)
        y = TOP_F - 6 if rs.uniform() < .55 else TOP_B + 8
        y += rs.uniform(-4, 4)
        r = rs.uniform(4, 9) * smooth(i / 14 * 0.6, i / 14 * 0.6 + 0.4, a)
        s.append(crystal(x, y, r, sd + 10 + i, a))
    # уголки — веточки инея
    for (cx, cy, dx) in ((TX0 + 6, TOP_F - 6, 1), (TX1 - 6, TOP_F - 6, -1)):
        L = 40 * a
        s.append(line([(cx, cy), (cx + dx * L, cy - L * .5)], 3.4, "#ffffff", taper=.4, seed=sd + 40 + dx, op=.9 * a))
        s.append(line([(cx + dx * L * .5, cy - L * .25), (cx + dx * L * .6, cy - L * .7)], 2.6, "#ffffff", taper=.4, seed=sd + 42 + dx, op=.9 * a))
    return "".join(s)


# ───────────────────────── телефон (лежит экраном вниз на столешнице)
SQT = 0.30           # сжатие плоскости столешницы


def tplane(pts, cx, cy, ang, sc=1.0, sq=SQT):
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    out = []
    for p in pts:
        x, y = p[0] * sc, p[1] * sc
        out.append((cx + x * c - y * s_, cy + (x * s_ + y * c) * sq) + ((1,) if len(p) > 2 and p[2] else ()))
    return out


def phone_flat(cx, cy, ang, sc=1.0, sq=SQT, sd=0, lift=0.0):
    """Обычный чёрный телефон, лежит экраном вниз: тыл с блоком камер, бортик. lift — висит над столом (тень отдельно)."""
    L, Wd = 150, 74
    s = []
    body = rect_pts(-L / 2, -Wd / 2, L / 2, Wd / 2, 13)
    th = 7 * sc
    side = [(x, y + th) + ((1,) if len(p) > 2 else ()) for p, (x, y) in zip(body, [q[:2] for q in tplane(body, cx, cy, ang, sc, sq)])]
    s.append(shape(side, "#0c0d11", "", w=3.2 * sc ** .5, seed=sd + 1))
    inner = blob(tplane([(-L / 2, Wd * .1), (L / 2, Wd * .2), (L / 2, Wd / 2), (-L / 2, Wd / 2)], cx, cy, ang, sc, sq), "#14161c", .9)
    inner += blob(tplane([(-L * .40, -Wd * .34), (L * .25, -Wd * .34), (L * .15, -Wd * .24), (-L * .42, -Wd * .24)], cx, cy, ang, sc, sq), "#56607a", .8)
    s.append(shape(tplane(body, cx, cy, ang, sc, sq), "#23262f", inner, w=3.6 * sc ** .5, seed=sd + 2))
    blk = tplane(rect_pts(-L / 2 + 10, -Wd / 2 + 9, -L / 2 + 46, -Wd / 2 + 45, 8), cx, cy, ang, sc, sq)
    s.append(shape(blk, "#30343f", "", w=2.6 * sc ** .5, seed=sd + 3))
    for k, (px, py) in enumerate([(-L / 2 + 20, -Wd / 2 + 19), (-L / 2 + 36, -Wd / 2 + 19), (-L / 2 + 20, -Wd / 2 + 35)]):
        q = tplane([(px, py)], cx, cy, ang, sc, sq)[0]
        r = 6.5 * sc
        s.append(shape(ellipse_pts(q[0], q[1], r, max(2.0, r * sq * 1.6), 10), "#0b0c10", "", w=2 * sc ** .5, seed=sd + 4 + k))
    return "".join(s)


# ───────────────────────── термометр тепла
def thermo(x, y0, y1, level, t, sd=950):
    """Настенный термометр на дощечке: колба внизу, шкала-риски без цифр, сверху сердечко. level 0..1."""
    s = []
    s.append(blob(rect_pts(x - 52 + 8, y0 - 120 + 10, x + 52 + 8, y1 + 96 + 10, 26), "#9c8a6c", .35, blur(6)))
    s.append(shape(rect_pts(x - 52, y0 - 120, x + 52, y1 + 96, 26), "#f3e3c3",
                   blob(rect_pts(x + 20, y0 - 120, x + 52, y1 + 96), "#e0caa2", .9), w=4.2, seed=sd))
    col = mix("#4f8fe0", "#e2453c", clamp(level * 1.25 - 0.1))
    # сердечко сверху: тёплое → голубое
    hx, hy = x, y0 - 64
    warm = clamp(level * 1.4 - 0.2)
    pts = [(hx, hy + 30, 1), (hx - 34, hy - 2), (hx - 30, hy - 26), (hx - 12, hy - 32), (hx, hy - 18, 1), (hx + 12, hy - 32), (hx + 30, hy - 26),
           (hx + 34, hy - 2)]
    beat = 1 + 0.06 * math.sin(t * 7) * warm
    pts = [(hx + (p[0] - hx) * beat, hy + (p[1] - hy) * beat) + p[2:] for p in pts]
    s.append(shape(pts, mix("#9cc4f0", "#ef5a6a", warm), blob(ellipse_pts(hx - 14, hy - 16, 8, 5, 8, rot=-30), "#ffffff", .7), w=3.6, seed=sd + 1))
    # трубка
    tw = 26
    tube = rect_pts(x - tw / 2, y0, x + tw / 2, y1, tw / 2)
    s.append(shape(tube, "#fbfdff", "", w=3.8, seed=sd + 2))
    lev_y = y1 - (y1 - y0 - 18) * clamp(level)
    s.append(f'<rect x="{f(x - 7)}" y="{f(lev_y)}" width="14" height="{f(y1 - lev_y + 30)}" rx="7" fill="{col}"/>')
    s.append(line([(x - 6, y0 + 14), (x - 6, y1 - 10)], 3, "#ffffff", taper=.2, seed=sd + 3, op=.7))
    for k in range(9):
        yy = y0 + 30 + k * (y1 - y0 - 50) / 8
        s.append(line([(x + tw / 2 + 6, yy), (x + tw / 2 + (24 if k % 2 == 0 else 14), yy)], 3.4, INK, taper=.1, wmin=.8, seed=sd + 10 + k))
    s.append(shape(ellipse_pts(x, y1 + 34, 40, 40, 18), col, blob(ellipse_pts(x - 12, y1 + 22, 10, 8, 8), "#ffffff", .6), w=4.2, seed=sd + 4))
    return "".join(s)


# ───────────────────────── общий кадр сидящих (s08, s10)
A_FEET = 425          # ступни A (сидит лицом вправо)
B_FEET = 655          # ступни B (лицом влево)
A_CH = 290
B_CH = 790


def seated_wide(t, ka, kb, poses, hands_a, hands_b, items_mid="", items_top="", frost=0.0, fa=A_FEET, fb=B_FEET):
    pa = dict(poses.get("A", {}))
    pb = dict(poses.get("B", {}))
    a_svg, _ = seat_person(A_SPEC, ka, fa, FEET_Y, SC_P, hands_a, pa, sd=3000)
    b_svg, _ = seat_person(B_SPEC, kb, fb, FEET_Y, SC_P, hands_b, pb, sd=4000)
    s = [chair(A_CH, 1, 300), chair(B_CH, -1, 320), table_back(), table_top(frost), table_frost(frost), items_mid, a_svg, b_svg, table_front(), items_top]
    return "".join(s)


def hands_on_table(side, t, ph=0.0):
    """Кисти лежат на столешнице (мир), чуть шевелятся."""
    if side == "A":
        return {"L": (428 + 3 * math.sin(t * 1.1 + ph), 1012), "R": (414 + 3 * math.sin(t * 1.3 + ph), 1034)}
    return {"R": (652 + 3 * math.sin(t * 1.2 + ph), 1012), "L": (666 + 3 * math.sin(t * 1.4 + ph), 1034)}


def lerp_hands(h0, h1, u):
    out = {}
    for k in h1:
        a, b = h0[k], h1[k]
        out[k] = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u - 40 * math.sin(math.pi * u))
    return out


def hang_hands(who, ox_feet, k):
    """Кисти висят вдоль тела (для перехода к столу), в мире."""
    dr = 1 if who == "A" else -1
    hx = ox_feet - dr * 140 * SC_P * math.sin(math.radians(90 * k))
    hy = FEET_Y - 330 * SC_P + 20
    return {"L": (hx - 30 + dr * 10, hy), "R": (hx + 30 + dr * 10, hy)}


def sit_k(t, t0, t1):
    u = clamp((t - t0) / (t1 - t0))
    k = ease_io(u)
    if t > t1:
        e = t - t1
        k = 1 - 0.03 * math.exp(-e * 6) * math.sin(e * 18)     # лёгкий «плюх» на стуле
    return clamp(k, 0, 1.05)


def walk_in(t, t0, t1, x0, x1):
    """Подходит к столу: x ступней и фаза шага (None — стоит)."""
    u = clamp((t - t0) / (t1 - t0))
    x = x0 + (x1 - x0) * (u * (2 - u) if u < 1 else 1)
    return x, ((t - t0) * 10.0 if u < 1 else None)


def s08(t):
    fa, wa = walk_in(t, 15.05, 15.78, A_FEET - 220, A_FEET)
    fb, wb = walk_in(t, 15.30, 16.18, B_FEET + 240, B_FEET)
    ka = sit_k(t, 15.80, 16.50)
    kb = sit_k(t, 16.22, 16.95)
    # руки: пока садятся — висят, потом ложатся на стол
    ua = smooth(16.45, 16.95, t)
    ub = smooth(16.95, 17.45, t)
    ha = lerp_hands(hang_hands("A", A_FEET, ka), hands_on_table("A", t), ua)
    hb = lerp_hands(hang_hands("B", B_FEET, kb), hands_on_table("B", t, 1), ub)
    # взгляды: сначала на стул, потом друг на друга, неловкая улыбка, кивок
    pa = dict(look=(0.2, 0.7) if t < 16.0 else (0.9, 0.0), mouth="flat" if t < 16.8 else "smile", blink=blink_at(t, 2.7, 0.4), walk=wa,
              head_tilt=-6 * (1 - ka) + 3 * math.sin(t * 1.6) * ka + 5 * math.exp(-max(t - 17.2, 0) * 3) * (t > 17.2), brow=.3,
              hmode={"L": "rest", "R": "rest"})
    pb = dict(look=(-0.2, 0.7) if t < 16.7 else (-0.9, 0.0), mouth="flat" if t < 17.4 else "smile", blink=blink_at(t, 3.1, 1.2), walk=wb,
              head_tilt=6 * (1 - kb) - 3 * math.sin(t * 1.4 + 1) * kb - 5 * math.exp(-max(t - 17.6, 0) * 3) * (t > 17.6), brow=.2,
              hmode={"L": "rest", "R": "rest"})
    items = cups(t)
    art = _ST["room"] + plant(70, FLOOR_Y + 20, t, 600) + tripod_cam(985, FLOOR_Y + 40, t) + lamp(t)
    art += seated_wide(t, ka, kb, {"A": pa, "B": pb}, ha if ua > 0 else None, hb if ub > 0 else None, items_mid=items, fa=fa, fb=fb)
    u = clamp((t - 15.44) / 2.96)
    cm = cam(505 + 70 * (0.3 * u + 0.7 * ease_io(u)), 905, 1.52 + 0.05 * u, -0.5 + 0.9 * u)
    return art, cm


def lamp(t):
    """Подвесная лампа под потолком — слегка качается."""
    a = 1.4 * math.sin(t * 1.1)
    px, py = 540, -300
    L = 470
    x = px + math.sin(math.radians(a)) * L
    y = py + math.cos(math.radians(a)) * L
    s = [line([(px, py), (x, y)], 3.4, INK, taper=.05, wmin=.9, seed=70)]
    g = rad_grad([(0, "#fff3c8", .6), (1, "#fff3c8", 0)], x, y + 50, 160, 110)
    s.append(f'<ellipse cx="{f(x)}" cy="{f(y + 50)}" rx="170" ry="120" fill="url(#{g})"/>')
    shade_ = [(x - 18, y, 1), (x + 18, y, 1), (x + 78, y + 64, 1), (x - 78, y + 64, 1)]
    s.append(shape(shade_, "#2f7f78", blob([(x + 4, y), (x + 18, y), (x + 78, y + 64), (x + 20, y + 64)], "#246660", .9), w=3.8, seed=71))
    s.append(shape(ellipse_pts(x, y + 66, 26, 9, 12), "#fff3c8", "", w=2.6, seed=72))
    return "".join(s)


# ───────────────────────── s09: крупно — рука кладёт телефон
PH_REST = (548, 1032)     # где телефон ляжет (центр, мир)
PH_ANG = -8


def sleeve_arm(wx, wy, ang, sc, sd):
    """Белый рукав халата исследователя от кисти вверх-вправо за кадр + манжета."""
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    # рукав идёт от запястья назад (противоположно направлению кисти) и вверх
    bx, by = wx - dx * 40 * sc, wy - dy * 40 * sc
    pts = [(bx, by), (bx - dx * 140 * sc + 60 * sc, by - 180 * sc), (bx - dx * 200 * sc + 160 * sc, by - 520 * sc)]
    pl = lib.band(pts, 92 * sc, 112 * sc, step=6, cap=False)
    inner = blob(lib.band([(x + 22 * sc, y) for x, y in pts], 40 * sc, 50 * sc, step=6, cap=False), "#d5dbe4", .9)
    inner += line([(bx - dx * 60 * sc + 20 * sc, by - 60 * sc), (bx - dx * 120 * sc + 70 * sc, by - 260 * sc)], 3 * sc, "#c2c9d4", seed=sd + 4, op=.9)
    s = shape(pl, "#f7f8fb", inner, w=4.2 * sc ** .6, seed=sd)
    # манжета: синяя рубашка выглядывает
    cuff = lib.band([(wx - dx * 52 * sc, wy - dy * 52 * sc), (wx - dx * 30 * sc, wy - dy * 30 * sc)], 70 * sc, 64 * sc, step=3, cap=False)
    s += shape(cuff, "#8fb6e6", blob(lib.band([(wx - dx * 52 * sc + 10 * sc, wy - dy * 52 * sc), (wx - dx * 30 * sc + 10 * sc, wy - dy * 30 * sc)],
                                              30 * sc, 28 * sc, step=3, cap=False), "#6f97c8", .9), w=3.4 * sc ** .6, seed=sd + 2)
    return s


# камера крупного плана: над столом, смотрит вниз на 28°
CH, CD, CTH, CF, CCY = 0.38, 0.40, 28.0, 1400.0, 880.0
_cs, _cc = math.sin(math.radians(CTH)), math.cos(math.radians(CTH))


def PC(X, Y, Z):
    """Мир крупного плана (м): X вправо, Y вниз (0 — столешница), Z от переднего края вглубь → (x, y, глубина)."""
    ry, rz = Y + CH, Z + CD
    d = ry * _cs + rz * _cc
    sy = ry * _cc - rz * _sn
    return (540 + CF * X / d, CCY + CF * sy / d, d)


_sn = _cs


def phone3d(cx, h, cz, yaw, roll=0.0, sd=0):
    """Телефон экраном вниз в перспективе: центр (cx, −h над столом, cz) м, поворот yaw вокруг вертикали, крен roll вокруг
    длинной оси. Размеры внутри — в мм."""
    L, Wd, TH = 155.0, 75.0, 9.0
    cyw, syw = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    sr, cr = math.sin(math.radians(roll)), math.cos(math.radians(roll))

    def M(u, v, w=0.0):
        vv = v * cr
        y = -h + (w + v * sr) / 1000
        X = cx + (u * cyw - vv * syw) / 1000
        Z = cz + (u * syw + vv * cyw) / 1000
        return PC(X, y, Z)[:2]

    def mp(pts, w=0.0):
        return [M(p[0], p[1], w) + ((1,) if len(p) > 2 and p[2] else ()) for p in pts]

    body = rect_pts(-L / 2, -Wd / 2, L / 2, Wd / 2, 11)
    s = []
    s.append(shape(mp(body, TH), "#0c0d11", "", w=4.2, seed=sd + 1))
    inner = blob(mp([(-L / 2, Wd * .12, 1), (L / 2, Wd * .2, 1), (L / 2, Wd / 2, 1), (-L / 2, Wd / 2, 1)]), "#15171d", .9)
    inner += blob(mp([(-L * .42, -Wd * .36, 1), (L * .22, -Wd * .36, 1), (L * .12, -Wd * .25, 1), (-L * .44, -Wd * .25, 1)]), "#5a6480", .75)
    s.append(shape(mp(body), "#23262f", inner, w=4.6, seed=sd + 2))
    blk = mp(rect_pts(-L / 2 + 8, -Wd / 2 + 7, -L / 2 + 40, -Wd / 2 + 39, 7))
    s.append(shape(blk, "#30343f", "", w=3.2, seed=sd + 3))
    for k, (pu, pv) in enumerate([(-L / 2 + 16, -Wd / 2 + 15), (-L / 2 + 32, -Wd / 2 + 15), (-L / 2 + 16, -Wd / 2 + 31)]):
        ring = [M(pu + 5.5 * math.cos(a), pv + 5.5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
        hi = [M(pu - 2 + 1.8 * math.cos(a), pv - 2 + 1.4 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        s.append(shape(ring, "#0b0c10", blob(hi, "#8a98b8", .9), w=2.6, seed=sd + 4 + k))
    q = M(-L / 2 + 32, -Wd / 2 + 31)
    s.append(f'<circle cx="{f(q[0])}" cy="{f(q[1])}" r="5" fill="#e8e2c8"/>')
    end = M(L / 2 - 12, 0.0)
    mid = M(0.0, 0.0)
    return "".join(s), end, mid


def cup3d(X, Z, sd, steam_t=None):
    """Чашка с блюдцем на столе в перспективе крупного плана."""
    s = []
    def ring(r, y, n=24, cx=X, cz=Z):
        return [PC(cx + r * math.cos(a), y, cz + r * math.sin(a))[:2] for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]
    sau = ring(0.075, 0)
    s.append(blob([(x + 6, y + 8) for x, y in sau], "#7a5234", .35, blur(4)))
    s.append(shape(sau, "#fbf8f0", blob(ring(0.05, 0), "#e6dfd0", .9), w=3.6, seed=sd))
    top = ring(0.042, -0.072)
    bot = ring(0.034, -0.004)
    pts = np.array(top + bot)
    hull = _hull(pts)
    # ручка — справа
    hp = [PC(X + 0.042 + 0.022 * math.cos(a), -0.040 + 0.020 * math.sin(a), Z)[:2] for a in np.linspace(-math.pi / 2, math.pi / 2, 9)]
    s.append(line(hp, 11, INK, taper=.05, wmin=.9, seed=sd + 1))
    s.append(line(hp, 6, "#f2ece0", taper=.05, wmin=.9, seed=sd + 2))
    band = ring(0.0425, -0.050) + ring(0.041, -0.040)[::-1]
    s.append(shape([tuple(p) + (1,) for p in hull], "#f6f1e6",
                   blob([tuple(p) for p in pts[len(top) // 2:len(top)]] + [tuple(p) for p in pts[len(top) + len(bot) // 2:][::-1]], "#ddd4c2", .0) +
                   line(ring(0.0425, -0.046)[:13], 9, "#5aa0a0", taper=.05, wmin=.9, seed=sd + 5, op=.9), w=3.6, seed=sd + 3))
    s.append(shape(top, "#f6f1e6", blob(ring(0.036, -0.066), "#8a5a34") + blob(ring(0.02, -0.066, cx=X - 0.008, cz=Z + 0.006), "#b07a4a", .8),
                   w=3.2, seed=sd + 4))
    if steam_t is not None:
        c = PC(X, -0.075, Z)
        for k in range(2):
            ph = (steam_t * 0.7 + k * 0.5) % 1
            yy = c[1] - 20 - ph * 90
            xx = c[0] - 14 + k * 26 + 8 * math.sin(steam_t * 3 + k)
            s.append(line([(xx, yy + 40), (xx + 10, yy + 20), (xx - 5, yy), (xx + 5, yy - 18)], 5, "#ffffff", taper=.6, seed=sd + 10 + k,
                          op=.6 * math.sin(math.pi * ph)))
    return "".join(s)


def _hull(P_):
    pts = sorted(map(tuple, P_))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def sleeve_to(edge_pt, wrist, w0, w1, col, shd, sd, cuff=None):
    """Рукав от края кадра до запястья (полоса с тенью), по желанию — манжета у кисти."""
    pts = [edge_pt, ((edge_pt[0] * 2 + wrist[0]) / 3, (edge_pt[1] * 2 + wrist[1]) / 3 + 10), wrist]
    pl = lib.band(pts, w0, w1, step=6, cap=False)
    inner = blob(lib.band([(x, y + w1 * .22) for x, y in pts], w0 * .5, w1 * .45, step=6, cap=False), shd, .9)
    s = shape(pl, col, inner, w=4.6, seed=sd)
    if cuff:
        dx, dy = wrist[0] - pts[1][0], wrist[1] - pts[1][1]
        L = math.hypot(dx, dy) + 1e-6
        c0 = (wrist[0] - dx / L * w1 * .5, wrist[1] - dy / L * w1 * .5)
        s += shape(lib.band([c0, wrist], w1 * 1.04, w1 * 1.0, step=3, cap=False), cuff[0], blob(lib.band([(c0[0], c0[1] + w1 * .2), (wrist[0], wrist[1] + w1 * .2)],
                                                                                                      w1 * .45, w1 * .4, step=3, cap=False), cuff[1], .9), w=4, seed=sd + 1)
    return s


def closeup_bg():
    """Фон крупного плана: стена с панелями и окно — размыто (глубина резкости)."""
    room = f'<g transform="translate(540 300) scale(1.9) translate(-540 -720)">{_ST["room"]}</g>'
    return f'<g {blur(7)}>{room}</g>'


def table3d():
    s = []
    top = [PC(x, 0, z)[:2] + (1,) for x, z in ((-0.62, 0.0), (0.62, 0.0), (0.62, 0.80), (-0.62, 0.80))]
    inner = ""
    rs = np.random.RandomState(4)
    for k in range(9):
        z = 0.06 + k * 0.085
        pts = [PC(x, 0, z + 0.006 * math.sin(x * 9 + k))[:2] for x in np.linspace(-0.6, 0.6, 12)]
        inner += line(pts, 2.2, WOOD_SH, taper=.4, wmin=.3, seed=1500 + k, op=.45)
    inner += blob([PC(x, 0, z)[:2] + (1,) for x, z in ((-0.62, 0.55), (0.62, 0.62), (0.62, 0.80), (-0.62, 0.80))], WOOD_HI, .45)
    s.append(shape(top, WOOD, inner, w=5, seed=1490))
    # передняя кромка (толщина столешницы)
    fe = [PC(x, y, 0)[:2] + (1,) for x, y in ((-0.62, 0), (0.62, 0), (0.62, 0.03), (-0.62, 0.03))]
    s.append(shape(fe, WOOD_SH, "", w=4.4, seed=1491))
    return "".join(s)


def s09(t):
    e = t - PHONE_T
    if e < 0:
        u = ease_out(clamp((t - 17.95) / (PHONE_T - 17.95)), 2.0)
        cx = 0.30 + (0.02 - 0.30) * u
        cz = 0.34 + (0.12 - 0.34) * u
        h = 0.20 * (1 - u) ** 1.3
        yaw = 24 * (1 - u) - 6
        roll = -16 * (1 - u)
    else:
        cx, cz, yaw, roll = 0.02, 0.12, -6.0, 0.0
        h = -0.0 + 0.004 * math.exp(-e * 10) * abs(math.sin(e * 22))
    ph_svg, end, mid = phone3d(cx, h, cz, yaw, roll, sd=1520)
    # рука: держит телефон за правый короткий край; после касания пальцы раскрываются, рука уходит вверх-вправо
    rel = smooth(PHONE_T + 0.06, PHONE_T + 0.26, t)
    away = ease_in(clamp((t - PHONE_T - 0.26) / 0.62), 2.0)
    ang = math.degrees(math.atan2(mid[1] - end[1], mid[0] - end[0]))
    depth = PC(cx, -h, cz)[2]
    hs = CF * 0.19 / depth / 82
    # запястье: от края телефона назад вдоль его оси на ~длину кисти
    k_back = 64 * hs
    wx = end[0] - math.cos(math.radians(ang)) * k_back
    wy = end[1] - math.sin(math.radians(ang)) * k_back - 16 * hs
    wx += 30 * rel + 520 * away
    wy -= 46 * rel + 700 * away
    hs *= 1 + 0.12 * away
    mode = "grip" if rel < 0.4 else ("rest" if rel < 0.8 else "open")
    hand = hand5(wx, wy, ang + 8 * rel, "#f0cfb4", "#d4a98a", sd=1560, sc=hs, mode=mode, thumb_up=True, ink_w=1.15)
    sleeve = sleeve_to((wx + 520, wy - 760), (wx - math.cos(math.radians(ang)) * 6 * hs, wy - math.sin(math.radians(ang)) * 6 * hs),
                       120 * hs / 2.2, 96 * hs / 2.2, "#f7f8fb", "#d5dbe4", 1580, cuff=("#8fb6e6", "#6f97c8"))
    # тень телефона на столе
    sc_ = PC(cx + 0.02 + 0.25 * h, 0, cz + 0.02 + 0.3 * h)
    shadow = blob(ellipse_pts(sc_[0], sc_[1], 200 * (1 + 1.5 * h), 60 * (1 + 1.5 * h), 18, rot=yaw * .5), "#6b4426", .42 * (1 - 2.2 * h), blur(6 + 30 * h))
    # руки участников по бокам стола (рукава из-за края кадра)
    arms = ""
    for (X, Z, col, shd, skin, side, sd, ph) in ((-0.36, 0.30, "#2f8f8a", person.shade("#2f8f8a"), A_SPEC["skin"], -1, 1600, 0.0),
                                                  (-0.30, 0.52, "#2f8f8a", person.shade("#2f8f8a"), A_SPEC["skin"], -1, 1620, 0.7),
                                                  (0.40, 0.34, "#33467a", person.shade("#33467a"), B_SPEC["skin"], 1, 1640, 1.1),
                                                  (0.33, 0.56, "#33467a", person.shade("#33467a"), B_SPEC["skin"], 1, 1660, 1.9)):
        X2 = X + 0.004 * math.sin(t * 1.3 + ph)
        wr = PC(X2, -0.012, Z)
        k_ = CF * 0.19 / wr[2] / 82
        edge = (-140 if side < 0 else 1220, wr[1] + 150 * k_ * 0.3)
        a_ = math.degrees(math.atan2(wr[1] - edge[1], wr[0] - edge[0])) + (-10 if side < 0 else 10) * 0
        arms += sleeve_to(edge, wr[:2], 70 * k_, 58 * k_, col, shd, sd)
        twitch = 4 * math.exp(-max(t - PHONE_T, 0) * 6) * (t > PHONE_T) * (1 if side < 0 else -1)
        arms += hand5(wr[0], wr[1], a_ + twitch, skin, person.shade(skin), sd=sd + 5, sc=k_, mode="rest", thumb_up=side > 0, ink_w=1.4)
    bg = closeup_bg()
    art = bg + table3d() + cup3d(-0.24, 0.55, 1680, steam_t=t) + cup3d(0.22, 0.60, 1700, steam_t=t + .4) + shadow + arms + ph_svg + sleeve + hand
    # касание: штрихи-удар
    if 0 <= e < 0.32:
        c = PC(0.02, 0, 0.12)
        for k in range(8):
            aa = -math.pi * (0.04 + 0.92 * k / 7)
            r0 = 230 + 120 * ease_out(e / .32)
            L = 46 * (1 - e / .32)
            art += line([(c[0] + math.cos(aa) * r0, c[1] + math.sin(aa) * r0 * .42), (c[0] + math.cos(aa) * (r0 + L), c[1] + math.sin(aa) * (r0 + L) * .42)],
                        7, INK, taper=.5, seed=1720 + k)
    u = clamp((t - 18.0) / 2.4)
    jolt = math.exp(-max(e, 0) * 12) * math.sin(max(e, 0) * 50) * (e > 0)
    c = PC(0.02, 0, 0.12)
    cm = cam(540 + (c[0] - 540) * 0.5 * u, 900 + (c[1] - 900) * 0.45 * ease_io(u) + 3 * jolt, 1.0 + 0.10 * ease_io(u) + 0.01 * jolt, 0.6 - 1.0 * u)
    return art, cm


# ───────────────────────── s10: разговор холодеет
def cold_k(t):
    return 0.25 * smooth(20.6, 21.9, t) + 0.75 * smooth(COLD_T - 0.05, COLD_T + 0.35, t)


def thermo_level(t):
    lv = 0.84 - 0.12 * smooth(20.8, 21.9, t) + 0.012 * math.sin(t * 5)
    if t >= COLD_T:
        e = t - COLD_T
        drop = clamp(spring(e * 1.0, 1.4, 5.0))
        lv = lv + (0.16 - lv) * drop
    return lv


def s10(t):
    ck = cold_k(t)
    fr = smooth(COLD_T, COLD_T + 0.6, t)
    # A говорит до 21.0, B — 21.0–21.9; после — оба замолкают, улыбки гаснут, косятся на телефон
    ma = mouth_talk(t, 19.9, 20.98, 6.5)
    mb = mouth_talk(t, 21.02, 21.9, 6.0, 1.0)
    after = t > COLD_T + 0.15
    hA = hands_on_table("A", t)
    if 20.0 <= t < 21.0:          # A жестикулирует ближней рукой
        g = math.sin(math.pi * clamp((t - 20.0) / 1.0))
        hA["R"] = (hA["R"][0] + 30 * g, hA["R"][1] - 120 * g + 16 * math.sin(t * 9) * g)
    hB = hands_on_table("B", t, 1)
    if 21.0 <= t < 21.9:
        g = math.sin(math.pi * clamp((t - 21.0) / 0.9))
        hB["L"] = (hB["L"][0] - 26 * g, hB["L"][1] - 110 * g + 14 * math.sin(t * 8) * g)
    ph_look = smooth(COLD_T + .1, COLD_T + .4, t)
    pa = dict(look=(0.9 - 0.5 * ph_look, 0.5 * ph_look), mouth=ma or ("flat" if after else "smile"), blink=blink_at(t, 2.6, 0.7),
              head_tilt=3 * math.sin(t * 2.0) * (1 - ph_look), brow=.2 + .5 * ph_look,
              hmode={"L": "rest", "R": "open" if 20.0 <= t < 21.0 else "rest"})
    pb = dict(look=(-0.9 + 0.5 * ph_look, 0.5 * ph_look), mouth=mb or ("flat" if after else "smile"), blink=blink_at(t, 3.0, 1.4),
              head_tilt=-3 * math.sin(t * 1.8) * (1 - ph_look), brow=.2 + .5 * ph_look,
              hmode={"L": "open" if 21.0 <= t < 21.9 else "rest", "R": "rest"})
    shiver = 2.0 * fr * math.sin(t * 40)
    items = cups(t, fr)
    items += blob(ellipse_pts(PH_REST[0] + 10, PH_REST[1] + 10, 88, 16, 16, rot=PH_ANG), "#5a3a22", .45, blur(4))
    items += phone_flat(PH_REST[0], PH_REST[1], PH_ANG, 1.0, SQT, sd=700)
    art = _ST["room"] + plant(70, FLOOR_Y + 20, t, 600) + lamp(t)
    art += thermo(968, 430, 880, thermo_level(t), t)
    body = seated_wide(t, 1.0, 1.0, {"A": pa, "B": pb}, hA, hB, items_mid=items, frost=fr)
    art += f'<g transform="translate({f(shiver)} 0)">{body}</g>'
    # пар изо рта, когда похолодало
    if t > COLD_T + 0.2:
        for k, (mx, my, d) in enumerate([(392, 790, 1), (690, 784, -1)]):
            ph = ((t - COLD_T - 0.2) * 0.9 + k * 0.45) % 1
            a = math.sin(math.pi * ph) * 0.7
            x = mx + d * 40 * ph
            y = my - 26 * ph
            art += blob(ellipse_pts(x, y, 16 + 20 * ph, 10 + 12 * ph, 12), "#ffffff", a * .8)
    # снежинки — пара штук плывут сверху после удара
    if t > COLD_T:
        rs = np.random.RandomState(5)
        for k in range(10):
            x0, sp = rs.uniform(250, 900), rs.uniform(60, 110)
            y = 560 + sp * (t - COLD_T) * 1.5 + rs.uniform(-80, 80)
            x = x0 + 20 * math.sin(t * 2 + k)
            art += crystal(x, y, 7 * smooth(COLD_T, COLD_T + .3, t), 980 + k, .9)
    u = clamp((t - 20.0) / 2.92)
    jolt = 0.012 * math.exp(-max(t - COLD_T, 0) * 6) * (t > COLD_T)
    cm = cam(600 + 10 * u, 900, 1.48 + 0.03 * u + jolt, 0.3 - 0.5 * u)
    return art, cm, ck


# ───────────────────────── s11: вид вдоль стола, стол растягивается
FOC = 940.0
HZ = 700.0          # горизонт (высота глаз) на экране
EYE = 1.42          # высота камеры над полом, м (чуть выше сидящих — стол виден сверху)
PX_M = 400.0        # единиц человека на метр
TBL_H = 0.76        # высота столешницы


def P(X, Y, Z):
    """Мир (м): X вправо, Y вниз от уровня глаз, Z вглубь → экран."""
    return (540 + FOC * X / Z, HZ + FOC * Y / Z)


def Q(*pts3):
    """Многоугольник по точкам (X, Y, Z) — все вершины углы (без сглаживания)."""
    return [P(*p) + (1,) for p in pts3]


def poly(pts3, fill, op=1.0):
    return blob(Q(*pts3), fill, op)


def s11(t):
    cz = 0.12 * ease_io(clamp((t - 22.52) / 2.4)) + 0.18 * smooth(FAR_T - 0.25, FAR_T + 0.35, t)
    stretch = smooth(FAR_T - 0.34, FAR_T + 0.30, t)
    e_ = max(t - FAR_T - 0.30, 0)
    over = 0.30 * math.exp(-e_ * 5) * math.sin(e_ * 12) * (t > FAR_T + 0.30)
    z_far = 2.25 + 6.2 * stretch + over + 0.03 * math.sin(t * 1.3)
    zb = z_far + 1.6                      # задняя стена
    zn = 1.30                             # ближний край стола
    z0 = 0.35                             # ближняя граница стен (за кадром)
    fy = EYE                              # пол
    cy_ = EYE - 2.8                       # потолок
    xl, xr = -1.9, 1.9
    Z = lambda z: z + cz                  # камера отъезжает: всё дальше на cz
    s = []
    # потолок, стены, пол
    s.append(poly([(xl, cy_, Z(z0)), (xr, cy_, Z(z0)), (xr, cy_, Z(zb)), (xl, cy_, Z(zb))], "#f6f1e6"))
    for X, col in ((xl, "#ece2cc"), (xr, "#e6dbc3")):
        s.append(poly([(X, cy_, Z(z0)), (X, cy_, Z(zb)), (X, fy, Z(zb)), (X, fy, Z(z0))], col))
        s.append(poly([(X, EYE - 0.95, Z(z0)), (X, EYE - 0.95, Z(zb)), (X, fy, Z(zb)), (X, fy, Z(z0))], PANEL))
        s.append(line([P(X, EYE - 0.95, Z(z0)), P(X, EYE - 0.95, Z(zb))], 4, INK, taper=.05, wmin=.5, seed=1101 + (X > 0)))
    s.append(poly([(xl, fy, Z(z0)), (xr, fy, Z(z0)), (xr, fy, Z(zb)), (xl, fy, Z(zb))], "#c99a6b"))
    for i, X in enumerate(np.linspace(xl, xr, 13)[1:-1]):
        s.append(line([P(X, fy, Z(z0)), P(X, fy, Z(zb))], 2.4, "#9c6c44", taper=.05, wmin=.5, seed=1120 + i, op=.75))
    # поперечные стыки досок и картины на стенах через каждые 1.4 м — видно, как растёт глубина
    for i, zz in enumerate(np.arange(1.0, 16.0, 1.4)):
        if zz > zb - 0.05:
            break
        s.append(line([P(xl, fy, Z(zz)), P(xr, fy, Z(zz))], 1.8, "#a8774d", taper=.05, wmin=.6, seed=1140 + i, op=.55))
        if i % 2 == 1 and zz + 0.7 < zb:
            for X in (xl, xr):
                kk = FOC / Z(zz) / 400
                fr_ = Q((X, EYE - 2.05, Z(zz)), (X, EYE - 2.05, Z(zz + 0.7)), (X, EYE - 1.5, Z(zz + 0.7)), (X, EYE - 1.5, Z(zz)))
                inn = blob(Q((X, EYE - 1.75, Z(zz)), (X, EYE - 1.85, Z(zz + 0.35)), (X, EYE - 1.7, Z(zz + 0.7)), (X, EYE - 1.5, Z(zz + 0.7)),
                             (X, EYE - 1.5, Z(zz))), "#7fae7a")
                s.append(shape(fr_, "#bfd8e8", inn, w=max(1.6, 5 * kk), seed=1160 + i + (X > 0) * 20))
    # задняя стена с окном (то же окно на улицу, что в общем плане)
    s.append(poly([(xl, cy_, Z(zb)), (xr, cy_, Z(zb)), (xr, fy, Z(zb)), (xl, fy, Z(zb))], WALL))
    s.append(poly([(xl, EYE - 0.95, Z(zb)), (xr, EYE - 0.95, Z(zb)), (xr, fy, Z(zb)), (xl, fy, Z(zb))], PANEL))
    w0, w1 = -0.72, 0.72
    wy0, wy1 = EYE - 2.35, EYE - 1.05
    win = Q((w0, wy0, Z(zb)), (w1, wy0, Z(zb)), (w1, wy1, Z(zb)), (w0, wy1, Z(zb)))
    kw = FOC / Z(zb) / 400
    ox, oy = win[0][:2]
    kx = (win[1][0] - win[0][0]) / 420
    ky = (win[2][1] - win[0][1]) / 570
    c = lib.clip_of(win)
    s.append(f'<g clip-path="url(#{c})"><g transform="translate({f(ox)} {f(oy)}) scale({kx:.5f} {ky:.5f}) translate(-330 -330)">{_ST["outside"]}</g></g>')
    fw = 0.07
    frame = Q((w0 - fw, wy0 - fw, Z(zb)), (w1 + fw, wy0 - fw, Z(zb)), (w1 + fw, wy1 + fw, Z(zb)), (w0 - fw, wy1 + fw, Z(zb)))
    d = lib.fill_d(frame) + lib.fill_d(win[::-1])
    s.append(f'<path d="{d}" fill="#fbf8f0" fill-rule="evenodd"/>')
    s.append(f'<path d="{lib.ink_closed(frame, max(1.4, 5 * kw), seed=1191)}" fill="{INK}"/>')
    mxw = (win[0][0] + win[1][0]) / 2
    myw = (win[0][1] + win[2][1]) / 2
    s.append(f'<rect x="{f(mxw - 7 * kw)}" y="{f(win[0][1])}" width="{f(14 * kw)}" height="{f(win[2][1] - win[0][1])}" fill="#fbf8f0"/>')
    s.append(f'<rect x="{f(win[0][0])}" y="{f(myw - 9 * kw)}" width="{f(win[1][0] - win[0][0])}" height="{f(18 * kw)}" fill="#fbf8f0"/>')
    # углы комнаты — тушью
    for a3, b3 in (((xl, fy, z0), (xl, fy, zb)), ((xr, fy, z0), (xr, fy, zb)), ((xl, cy_, z0), (xl, cy_, zb)), ((xr, cy_, z0), (xr, cy_, zb)),
                   ((xl, cy_, zb), (xl, fy, zb)), ((xr, cy_, zb), (xr, fy, zb)), ((xl, fy, zb), (xr, fy, zb)), ((xl, EYE - 0.95, zb), (xr, EYE - 0.95, zb))):
        s.append(line([P(a3[0], a3[1], Z(a3[2])), P(b3[0], b3[1], Z(b3[2]))], 3.6, INK, taper=.05, wmin=.6, seed=1180 + int(a3[2] * 10) + int(a3[1] * 7)))
    # человек напротив: стул, сам человек (анфас), за дальним краем стола
    zB = z_far + 0.42
    scB = FOC / Z(zB) / PX_M
    ty = EYE - TBL_H
    kB = FOC / Z(zB) / 400
    s.append(shape(Q((-0.22, EYE - 0.95, Z(zB + 0.22)), (0.22, EYE - 0.95, Z(zB + 0.22)), (0.22, EYE - 0.47, Z(zB + 0.22)), (-0.22, EYE - 0.47, Z(zB + 0.22))),
                   "#b5845a", "", w=max(1.4, 4.4 * kB), seed=1200))
    hx, hy = P(0.0, EYE - 0.47, Z(zB))
    B2 = dict(B_SPEC, face=0.0)
    poseB = dict(look=(0, 0.25), mouth="flat", brow=.6, blink=blink_at(t, 3.0, .5), head_tilt=2 * math.sin(t * 1.4), legs={"L": (0, 0), "R": (0, 0)},
                 arms={"L": (14, 0), "R": (-14, 0)})
    fe = P(0, ty, Z(z_far))
    cB = lib.clip_rect(-2000, -4000, 5000, 4000 + fe[1] + 2)
    s.append(f'<g clip-path="url(#{cB})">{person.draw(B2, poseB, hx, hy + 300 * scB * B_SPEC["h"], scB, sd=4000)}</g>')
    # тень под столом и ножки
    s.append(blob(Q((-0.46, fy, Z(zn)), (0.46, fy, Z(zn)), (0.46, fy, Z(z_far)), (-0.46, fy, Z(z_far))), "#6b4a32", .35))
    for k, (X, zz) in enumerate(((-0.37, z_far - 0.05), (0.37, z_far - 0.05), (-0.37, zn + 0.05), (0.37, zn + 0.05))):
        kk = FOC / Z(zz) / 400
        p0, p1 = P(X, ty + 0.03, Z(zz)), P(X, fy, Z(zz))
        wd = 11 * kk
        s.append(shape([(p0[0] - wd, p0[1], 1), (p0[0] + wd, p0[1], 1), (p1[0] + wd, p1[1], 1), (p1[0] - wd, p1[1], 1)], WOOD_SH, "",
                       w=max(1.4, 3.6 * kk ** .5), seed=1215 + k))
    # стол: столешница от ближнего края до дальнего
    top = Q((-0.42, ty, Z(zn)), (0.42, ty, Z(zn)), (0.42, ty, Z(z_far)), (-0.42, ty, Z(z_far)))
    inner = ""
    for i, X in enumerate((-0.27, -0.08, 0.14, 0.31)):
        inner += line([P(X, ty, Z(zn)), P(X + 0.02, ty, Z(z_far))], 2.2, WOOD_SH, taper=.3, wmin=.4, seed=1210 + i, op=.6)
    inner += blob(Q((-0.42, ty, Z(zn)), (0.42, ty, Z(zn)), (0.42, ty, Z(zn + 0.35)), (-0.42, ty, Z(zn + 0.35))), WOOD_HI, .5)
    s.append(shape(top, WOOD, inner, w=4.4, seed=1205))
    s.append(blob(Q((-0.42, ty, Z(zn)), (0.42, ty, Z(zn)), (0.42, ty + 0.035, Z(zn)), (-0.42, ty + 0.035, Z(zn))), WOOD_SH))
    s.append(line([P(-0.42, ty + 0.035, Z(zn)), P(0.42, ty + 0.035, Z(zn))], 4, INK, taper=.05, wmin=.8, seed=1208))
    # кромка дальнего края — за ней сидит B
    s.append(line([P(-0.42, ty, Z(z_far)), P(0.42, ty, Z(z_far))], max(1.6, 4 * kB), INK, taper=.05, wmin=.8, seed=1207))
    # кисти B на дальнем крае стола
    for k, X in enumerate((-0.15, 0.15)):
        q = P(X, ty, Z(z_far - 0.07))
        s.append(hand5(q[0], q[1], 90 + (14 if X < 0 else -14), B_SPEC["skin"], person.shade(B_SPEC["skin"]), sd=1230 + k, sc=scB * 0.86,
                       mode="rest", thumb_up=X < 0, ink_w=3.0))
    # иней по краям столешницы
    rs = np.random.RandomState(11)
    for i in range(24):
        side_ = -0.40 if i % 2 == 0 else 0.40
        zz = zn + (z_far - zn) * rs.uniform(0, 1)
        q = P(side_, ty, Z(zz))
        s.append(crystal(q[0] - side_ * 10, q[1] - 2, 11 * FOC / Z(zz) / 700, 1240 + i, .9))
    s.append(line([P(-0.405, ty, Z(zn)), P(-0.405, ty, Z(z_far))], 5, "#f4fbff", taper=.1, wmin=.3, seed=1270, op=.85))
    s.append(line([P(0.405, ty, Z(zn)), P(0.405, ty, Z(z_far))], 5, "#f4fbff", taper=.1, wmin=.3, seed=1271, op=.85))
    # чашки: ближняя (у A) стоит, дальняя (у B) уезжает с ним
    for k, (X, zz) in enumerate(((-0.25, zn + 0.30), (0.20, z_far - 0.26))):
        q = P(X, ty, Z(zz))
        k_ = FOC / Z(zz) / 400 * 1.15
        s.append(f'<g transform="translate({f(q[0])} {f(q[1])}) scale({k_:.4f})">{cup(0, 0, 1250 + k * 10, frost=1.0)}</g>')
    # телефон между ними, ближе к A (уезжает меньше)
    zph = zn + 0.50 + (z_far - zn) * 0.16
    q = P(0.05, ty, Z(zph))
    kph = FOC / Z(zph) / 400 * 1.15
    s.append(blob(ellipse_pts(q[0] + 6 * kph, q[1] + 6 * kph, 80 * kph, 14 * kph, 14), "#5a3a22", .4, blur(3)))
    s.append(phone_flat(q[0], q[1], 3, kph, 0.30, sd=1300))
    # A на переднем плане: со спины, слева внизу; ниже лопаток — спинка стула
    za = 0.70 + 0.4 * cz            # A едет вместе с камерой (лишь чуть отстаёт)
    scA = FOC / za / PX_M
    A2 = dict(A_SPEC, back=True, face=0.0)
    poseA = dict(legs={"L": (0, 0), "R": (0, 0)}, arms={"L": (4, 0), "R": (-4, 0)}, head_tilt=-4 + 2 * math.sin(t * 1.1))
    ax, ay = P(-0.40, EYE - 0.47, za)
    s.append(person.draw(A2, poseA, ax, ay + 300 * scA * A_SPEC["h"], scA, sd=3000))
    # «дальше»: штрихи скорости вдоль стола
    e = t - (FAR_T - 0.25)
    if 0 <= e < 0.75:
        a = math.sin(math.pi * e / 0.75)
        for k, X in enumerate((-0.75, -0.5, 0.5, 0.75)):
            zz = 1.8 + e * 7 + k * 0.5
            yy = ty - 0.45 - 0.12 * (k % 2)
            s.append(line([P(X, yy, Z(zz)), P(X, yy, Z(zz + 1.8))], 7, "#ffffff", taper=.6, seed=1320 + k, op=.85 * a))
    u = clamp((t - 22.52) / 2.4)
    cm = cam(555 - 8 * u, 930 - 6 * u, 1.0 - 0.02 * ease_io(u), 0.2 - 0.4 * u)
    return "".join(s), cm


def build_static():
    if _ST:
        return
    _ST["room"] = room_static()
    _ST["outside"] = outside()
    lib.static_done()


def tint(ck):
    """Похолодание: умножение на голубой и частичное обесцвечивание (по всему кадру, после камеры)."""
    if ck <= 0.005:
        return ""
    return (f'<rect width="{W}" height="{H}" fill="#6f8fc4" opacity="{0.42 * ck:.3f}" style="mix-blend-mode:color"/>'
            f'<rect width="{W}" height="{H}" fill="#bcd2f2" opacity="{0.55 * ck:.3f}" style="mix-blend-mode:multiply"/>')


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    ck = 0.0
    if sid == "s08":
        art, cm = s08(t)
    elif sid == "s09":
        art, cm = s09(t)
    elif sid == "s10":
        art, cm, ck = s10(t)
    else:
        art, cm = s11(t)
        ck = 1.0
    return svg(f'<rect width="{W}" height="{H}" fill="{WALL}"/><g transform="{cm}">{art}</g>{tint(ck)}')
