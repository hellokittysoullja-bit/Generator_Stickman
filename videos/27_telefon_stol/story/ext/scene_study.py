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
TX0, TX1 = 405, 675
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
        pose["arms_front"] = True
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
    # пятно солнца на полу
    s.append(blob([(400, 1300), (760, 1300), (860, 1560), (300, 1560)], "#ffe9c2", .35, blur(10)))
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
A_FEET = 452          # ступни A (сидит лицом вправо)
B_FEET = 628          # ступни B (лицом влево)
A_CH = 316
B_CH = 764


def seated_wide(t, ka, kb, poses, hands_a, hands_b, items_mid="", items_top="", frost=0.0):
    pa = dict(poses.get("A", {}))
    pb = dict(poses.get("B", {}))
    a_svg, _ = seat_person(A_SPEC, ka, A_FEET - 140 * SC_P * (1 - ka) * 0, FEET_Y, SC_P, hands_a, pa, sd=3000)
    b_svg, _ = seat_person(B_SPEC, kb, B_FEET, FEET_Y, SC_P, hands_b, pb, sd=4000)
    s = [chair(A_CH, 1, 300), chair(B_CH, -1, 320), table_back(), table_top(frost), table_frost(frost), items_mid, a_svg, b_svg, table_front(), items_top]
    return "".join(s)


def hands_on_table(side, t, ph=0.0):
    """Кисти лежат на столешнице (мир), чуть шевелятся."""
    if side == "A":
        return {"L": (482 + 3 * math.sin(t * 1.1 + ph), 1010), "R": (468 + 3 * math.sin(t * 1.3 + ph), 1032)}
    return {"R": (600 + 3 * math.sin(t * 1.2 + ph), 1010), "L": (614 + 3 * math.sin(t * 1.4 + ph), 1032)}


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


def s08(t):
    ka = sit_k(t, 15.20, 16.05)
    kb = sit_k(t, 15.95, 16.85)
    # руки: пока садятся — висят, потом ложатся на стол
    ua = smooth(16.05, 16.55, t)
    ub = smooth(16.85, 17.35, t)
    ha = lerp_hands(hang_hands("A", A_FEET, ka), hands_on_table("A", t), ua)
    hb = lerp_hands(hang_hands("B", B_FEET, kb), hands_on_table("B", t, 1), ub)
    # взгляды: сначала на стул, потом друг на друга, неловкая улыбка, кивок
    pa = dict(look=(0.2, 0.7) if t < 16.0 else (0.9, 0.0), mouth="flat" if t < 16.8 else "smile", blink=blink_at(t, 2.7, 0.4),
              head_tilt=-6 * (1 - ka) + 3 * math.sin(t * 1.6) * ka + 5 * math.exp(-max(t - 17.2, 0) * 3) * (t > 17.2), brow=.3,
              hmode={"L": "rest", "R": "rest"})
    pb = dict(look=(-0.2, 0.7) if t < 16.7 else (-0.9, 0.0), mouth="flat" if t < 17.4 else "smile", blink=blink_at(t, 3.1, 1.2),
              head_tilt=6 * (1 - kb) - 3 * math.sin(t * 1.4 + 1) * kb - 5 * math.exp(-max(t - 17.6, 0) * 3) * (t > 17.6), brow=.2,
              hmode={"L": "rest", "R": "rest"})
    items = cup(458, 1024, 500, steam_t=t) + cup(624, 1018, 520, steam_t=t + .3)
    art = _ST["room"] + plant(70, FLOOR_Y + 20, t, 600) + tripod_cam(985, FLOOR_Y + 40, t) + lamp(t)
    art += seated_wide(t, ka, kb, {"A": pa, "B": pb}, ha, hb, items_mid=items)
    u = clamp((t - 15.44) / 2.96)
    cm = cam(500 + 70 * (0.3 * u + 0.7 * ease_io(u)), 905, 1.10 + 0.03 * u, -0.5 + 0.9 * u)
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


def s09(t):
    # телефон: несут сверху-справа, опускают, касание на PHONE_T, лёгкий отскок
    e = t - PHONE_T
    if e < 0:
        u = ease_out(clamp((t - 18.0) / (PHONE_T - 18.0)), 2.2)
        px = 760 + (PH_REST[0] - 760) * u
        py = 640 + (PH_REST[1] - 640) * u
        tilt = 16 * (1 - u)
        sq = SQT + 0.25 * (1 - u)
        lift = (1 - u)
    else:
        px, py = PH_REST
        py -= 6 * math.exp(-e * 10) * abs(math.sin(e * 22))
        tilt, sq, lift = 0.0, SQT, 0.0
    # рука: держит телефон до касания, после — раскрывается и уходит вверх-вправо
    rel = smooth(PHONE_T + 0.08, PHONE_T + 0.30, t)
    away = ease_in(clamp((t - PHONE_T - 0.30) / 0.55), 2)
    hx = px + 6 + 40 * rel + 380 * away
    hy = py - 18 - 34 * rel - 560 * away
    hang = 158 - 10 * rel
    hs = 1.15
    mode = "rest" if rel < 0.5 else "open"
    # фон: тот же общий план, люди сидят, смотрят на телефон
    look_a = (0.9, 0.4) if t > 18.6 else (0.9, 0.0)
    look_b = (-0.9, 0.4) if t > 18.7 else (-0.9, 0.0)
    pa = dict(look=look_a, mouth="flat" if t < PHONE_T + .2 else "o", blink=blink_at(t, 2.9, 0.2), head_tilt=4 * math.sin(t * 1.3), brow=.5 if t > PHONE_T else .2)
    pb = dict(look=look_b, mouth="smile" if t < PHONE_T else "flat", blink=blink_at(t, 3.3, 1.0), head_tilt=-4 * math.sin(t * 1.2), brow=.4 if t > PHONE_T else .2)
    jolt = 1.5 * math.exp(-max(e, 0) * 12) * math.sin(max(e, 0) * 50) * (e > 0)
    shadow = ""
    sh_a = 0.45 * (1 - 0.6 * lift)
    shadow = blob(ellipse_pts(PH_REST[0] + 10 + 30 * lift, PH_REST[1] + 10, 88 * (1 + .4 * lift), 16 * (1 + .4 * lift), 16, rot=PH_ANG), "#5a3a22", sh_a,
                  blur(4 + 8 * lift))
    ph = phone_flat(px, py, PH_ANG + tilt, 1.0, sq, sd=700)
    hand = hand5(hx, hy, hang, "#f0cfb4", "#d4a98a", sd=720, sc=hs, mode=mode, thumb_up=False, ink_w=3.0)
    arm = sleeve_arm(hx, hy, hang, 1.0, 740)
    items = cup(458, 1024, 500, steam_t=t) + cup(624, 1018, 520, steam_t=t + .3)
    art = _ST["room"] + plant(70, FLOOR_Y + 20, t, 600) + lamp(t)
    art += seated_wide(t, 1.0, 1.0, {"A": pa, "B": pb}, hands_on_table("A", t), hands_on_table("B", t, 1), items_mid=items + shadow,
                       items_top=ph + arm + hand)
    # удар касания: штрихи
    if 0 <= e < 0.3:
        for k in range(5):
            a = math.pi + (k - 2) * 0.35 - math.pi / 2
            r0 = 90 + 60 * ease_out(e / .3)
            L = 22 * (1 - e / .3)
            for sgn in (-1, 1):
                aa = -math.pi / 2 + sgn * (0.5 + k * 0.22)
                art += line([(PH_REST[0] + math.cos(aa) * r0 * 1.2, PH_REST[1] + math.sin(aa) * r0 * .5),
                             (PH_REST[0] + math.cos(aa) * (r0 + L) * 1.2, PH_REST[1] + math.sin(aa) * (r0 + L) * .5)], 4, INK, taper=.5,
                            seed=760 + k + (sgn > 0) * 10)
    u = clamp((t - 18.0) / 2.4)
    z = 2.05 + 0.35 * ease_io(u) + 0.04 * jolt
    cm = cam(552 + 6 * u, 952 + 30 * ease_io(u) + jolt * 2, z, 0.4 - 0.7 * u)
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
    items = cup(458, 1024, 500, steam_t=t, frost=fr) + cup(624, 1018, 520, steam_t=t + .3, frost=fr)
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
    cm = cam(585 + 10 * u, 905, 1.12 + 0.02 * u + jolt, 0.3 - 0.5 * u)
    return art, cm, ck


# ───────────────────────── s11: вид вдоль стола, стол растягивается
FOC = 920.0
HZ = 760.0          # горизонт (высота глаз)
EYE = 1.22          # высота камеры над полом, м
PX_M = 400.0        # единиц человека на метр


def P(X, Y, Z):
    """Мир (м): X вправо, Y вниз от уровня глаз, Z вглубь → экран."""
    return (540 + FOC * X / Z, HZ + FOC * Y / Z)


def quad(pts3, cz):
    return [P(x, y, z + cz) + (1,) for x, y, z in pts3]


def s11(t):
    cz = 0.10 * ease_io(clamp((t - 22.52) / 2.4)) + 0.12 * smooth(FAR_T - 0.25, FAR_T + 0.3, t)
    stretch = smooth(FAR_T - 0.32, FAR_T + 0.30, t)
    over = 0.25 * math.exp(-max(t - FAR_T - 0.3, 0) * 5) * math.sin(max(t - FAR_T - 0.3, 0) * 12) * (t > FAR_T + 0.3)
    z_far = 2.35 + 5.6 * stretch + over + 0.04 * math.sin(t * 1.3)
    zb = z_far + 1.7                      # задняя стена
    zn = 1.25                             # ближний край стола
    fy = EYE                              # пол
    cy_ = EYE - 2.75                      # потолок
    xl, xr = -2.1, 2.1
    s = []
    # задняя стена с окном (то же окно на улицу)
    bw = [P(xl, cy_, zb + cz), P(xr, cy_, zb + cz), P(xr, fy, zb + cz), P(xl, fy, zb + cz)]
    s.append(blob(bw, WALL))
    # окно на задней стене
    w0, w1 = -0.75, 0.75
    wy0, wy1 = EYE - 2.15, EYE - 0.95
    win = [P(w0, wy0, zb + cz), P(w1, wy0, zb + cz), P(w1, wy1, zb + cz), P(w0, wy1, zb + cz)]
    sc_w = FOC / (zb + cz)
    ox, oy = win[0]
    # outside(): прямоугольник 330..750 × 330..900 → в окно
    kx = (win[1][0] - win[0][0]) / 420
    ky = (win[2][1] - win[0][1]) / 570
    c = lib.clip_of([p + (1,) for p in win])
    s.append(f'<g clip-path="url(#{c})"><g transform="translate({f(ox)} {f(oy)}) scale({kx:.5f} {ky:.5f}) translate(-330 -330)">{_ST["outside"]}</g></g>')
    fw = 0.07
    frame = [P(w0 - fw, wy0 - fw, zb + cz), P(w1 + fw, wy0 - fw, zb + cz), P(w1 + fw, wy1 + fw, zb + cz), P(w0 - fw, wy1 + fw, zb + cz)]
    d = lib.fill_d([p + (1,) for p in frame]) + lib.fill_d([p + (1,) for p in win[::-1]])
    s.append(f'<path d="{d}" fill="#fbf8f0" fill-rule="evenodd"/>')
    s.append(f'<path d="{lib.ink_closed([p + (1,) for p in frame], max(1.5, 4.0 * sc_w / 400), seed=1101)}" fill="{INK}"/>')
    mxw = (win[0][0] + win[1][0]) / 2
    s.append(f'<rect x="{f(mxw - 3 * sc_w / 400)}" y="{f(win[0][1])}" width="{f(6 * sc_w / 400)}" height="{f(win[2][1] - win[0][1])}" fill="#fbf8f0"/>')
    myw = (win[0][1] + win[2][1]) / 2
    s.append(f'<rect x="{f(win[0][0])}" y="{f(myw - 4 * sc_w / 400)}" width="{f(win[1][0] - win[0][0])}" height="{f(8 * sc_w / 400)}" fill="#fbf8f0"/>')
    # боковые стены, пол, потолок
    for X, col, seed in ((xl, "#e8dec8", 1110), (xr, "#e3d8c0", 1111)):
        wall = [P(X, cy_, 0.3 + cz), P(X, cy_, zb + cz), P(X, fy, zb + cz), P(X, fy, 0.3 + cz)]
        s.append(blob(wall, col))
        # панель снизу
        py_ = EYE - 0.62
        pan = [P(X, py_, 0.3 + cz), P(X, py_, zb + cz), P(X, fy, zb + cz), P(X, fy, 0.3 + cz)]
        s.append(blob(pan, PANEL))
        s.append(line([P(X, py_, 0.3 + cz), P(X, py_, zb + cz)], 4, INK, taper=.05, wmin=.6, seed=seed))
    ceil = [P(xl, cy_, 0.3 + cz), P(xr, cy_, 0.3 + cz), P(xr, cy_, zb + cz), P(xl, cy_, zb + cz)]
    s.append(blob(ceil, "#f6f1e6"))
    flr = [P(xl, fy, 0.3 + cz), P(xr, fy, 0.3 + cz), P(xr, fy, zb + cz), P(xl, fy, zb + cz)]
    s.append(blob(flr, "#c99a6b"))
    # доски пола — вдоль глубины
    for i, X in enumerate(np.linspace(xl, xr, 15)[1:-1]):
        s.append(line([P(X, fy, 0.3 + cz), P(X, fy, zb + cz)], 2.4, "#9c6c44", taper=.05, wmin=.5, seed=1120 + i, op=.75))
    # поперечные стыки досок и картины на стенах — через каждые 1.5 м (видно, как растёт глубина)
    for i, Z in enumerate(np.arange(1.0, 14.0, 1.5)):
        if Z > zb:
            break
        s.append(line([P(xl, fy, Z + cz), P(xr, fy, Z + cz)], 1.8, "#a8774d", taper=.05, wmin=.6, seed=1140 + i, op=.55))
        for X, sgn in ((xl, 1), (xr, -1)):
            if Z + 0.6 < zb and i % 2 == 1:
                fr_ = [P(X, EYE - 1.75, Z + cz), P(X, EYE - 1.75, Z + 0.6 + cz), P(X, EYE - 1.3, Z + 0.6 + cz), P(X, EYE - 1.3, Z + cz)]
                s.append(shape([p + (1,) for p in fr_], "#bfd8e8", "", w=max(1.4, 3.4 * FOC / (Z + cz) / 400), seed=1160 + i,
                               ink_color="#7a5634"))
    # углы комнаты — линии туши
    for a3, b3 in (((xl, fy, 0.3), (xl, fy, zb)), ((xr, fy, 0.3), (xr, fy, zb)), ((xl, cy_, 0.3), (xl, cy_, zb)), ((xr, cy_, 0.3), (xr, cy_, zb)),
                   ((xl, cy_, zb), (xl, fy, zb)), ((xr, cy_, zb), (xr, fy, zb)), ((xl, fy, zb), (xr, fy, zb))):
        s.append(line([P(a3[0], a3[1], a3[2] + cz), P(b3[0], b3[1], b3[2] + cz)], 3.6, INK, taper=.05, wmin=.6, seed=1180 + int(a3[2] * 10)))
    # человек напротив: за дальним краем стола, анфас
    zB = z_far + 0.5 + cz
    scB = FOC / zB / PX_M
    hipY = EYE - 0.47
    hx, hy = P(0.0, hipY, zB)
    B2 = dict(B_SPEC, face=0.0)
    lean = 1.0
    poseB = dict(look=(0, 0.2), mouth="flat", brow=.6, blink=blink_at(t, 3.0, .5), head_tilt=2 * math.sin(t * 1.4), legs={"L": (0, 0), "R": (0, 0)},
                 arms={"L": (-20, 30), "R": (20, -30)}, hmode={"L": "rest", "R": "rest"})
    # стул B
    chs = []
    seat = [P(-0.24, hipY + 0.06, zB + 0.05), P(0.24, hipY + 0.06, zB + 0.05)]
    chs.append(shape([P(-0.26, EYE - 1.25, zB + 0.25) + (1,), P(0.26, EYE - 1.25, zB + 0.25) + (1,), P(0.26, hipY, zB + 0.25) + (1,),
                      P(-0.26, hipY, zB + 0.25) + (1,)], "#b5845a", "", w=max(1.4, 3.6 * scB), seed=1200))
    s += chs
    hy_o = hy + 300 * scB * B_SPEC["h"]
    s.append(person.draw(B2, poseB, hx, hy_o, scB, sd=4000))
    # стол: ближний край → дальний
    ty = EYE - 0.74
    top = [P(-0.42, ty, zn + cz) + (1,), P(0.42, ty, zn + cz) + (1,), P(0.42, ty, z_far + cz) + (1,), P(-0.42, ty, z_far + cz) + (1,)]
    inner = ""
    for i, X in enumerate((-0.25, -0.05, 0.18, 0.33)):
        inner += line([P(X, ty, zn + cz), P(X + 0.02, ty, z_far + cz)], 2.2, WOOD_SH, taper=.3, wmin=.4, seed=1210 + i, op=.6)
    inner += blob([P(-0.42, ty, zn + cz), P(0.42, ty, zn + cz), P(0.42, ty, zn + 0.3 + cz), P(-0.42, ty, zn + 0.3 + cz)], WOOD_HI, .5)
    # торец дальнего края (кромка столешницы) — тонкая полоса
    s.append(shape(top, WOOD, inner, w=4.4, seed=1205))
    edge = [P(-0.42, ty, zn + cz) + (1,), P(0.42, ty, zn + cz) + (1,), P(0.42, ty + 0.04, zn + cz) + (1,), P(-0.42, ty + 0.04, zn + cz) + (1,)]
    s.append(shape(edge, WOOD_SH, "", w=3.6, seed=1206))
    fr = 1.0
    # кисти B на дальнем крае стола
    for k, X in enumerate((-0.16, 0.16)):
        q = P(X, ty, z_far - 0.06 + cz)
        s.append(hand5(q[0], q[1], 90 + (-12 if X < 0 else 12), B_SPEC["skin"], person.shade(B_SPEC["skin"]), sd=1230 + k, sc=0.95 * scB * 1.05,
                       mode="rest", thumb_up=X > 0, ink_w=3.0))
    # иней по краям столешницы
    rs = np.random.RandomState(11)
    for i in range(22):
        side_ = -0.41 if i % 2 == 0 else 0.41
        Z = zn + (z_far - zn) * rs.uniform(0, 1)
        q = P(side_, ty, Z + cz)
        s.append(crystal(q[0] - side_ * 8, q[1] - 3, 9 * FOC / (Z + cz) / 600, 1240 + i, .9))
    s.append(line([P(-0.41, ty, zn + cz), P(-0.41, ty, z_far + cz)], 4, "#f4fbff", taper=.1, wmin=.4, seed=1270, op=.8))
    s.append(line([P(0.41, ty, zn + cz), P(0.41, ty, z_far + cz)], 4, "#f4fbff", taper=.1, wmin=.4, seed=1271, op=.8))
    # чашки: ближняя (у A) и дальняя (у B, уезжает)
    for k, (X, Z) in enumerate(((-0.24, zn + 0.32), (0.22, z_far - 0.28))):
        q = P(X, ty, Z + cz)
        k_ = FOC / (Z + cz) / 400 * 1.25
        s.append(f'<g transform="translate({f(q[0])} {f(q[1])}) scale({k_:.4f}) translate(-500 -1000)">{cup(500, 1000, 1250 + k * 10, frost=fr)}</g>')
    # телефон посередине стола (тоже уезжает, но меньше — лежит ближе к A)
    zph = zn + 0.55 + (z_far - zn) * 0.18
    q = P(0.04, ty, zph + cz)
    kph = FOC / (zph + cz) / 400 * 1.2
    s.append(blob(ellipse_pts(q[0] + 6 * kph, q[1] + 6 * kph, 90 * kph, 14 * kph, 14), "#5a3a22", .4, blur(3)))
    s.append(f'<g transform="translate({f(q[0])} {f(q[1])})">{phone_flat(0, 0, 4, kph, 0.20 + 0.3 / (zph + cz), sd=1300)}</g>')
    # A на переднем плане: со спины, слева внизу (голова, плечи)
    za = 0.95 + cz
    scA = FOC / za / PX_M
    A2 = dict(A_SPEC, back=True, face=0.0)
    poseA = dict(legs={"L": (0, 0), "R": (0, 0)}, arms={"L": (10, 30), "R": (-10, -30)}, head_tilt=-3 + 2 * math.sin(t * 1.1))
    ax, ay = P(-0.42, EYE - 0.47, za)
    s.append(person.draw(A2, poseA, ax, ay + 300 * scA * A_SPEC["h"], scA, sd=3000))
    # «дальше»: штрихи скорости вдоль стола
    e = t - (FAR_T - 0.2)
    if 0 <= e < 0.7:
        a = math.sin(math.pi * e / 0.7)
        for k, X in enumerate((-0.6, -0.3, 0.3, 0.6)):
            z0 = 1.6 + e * 6 + k * 0.4
            p0, p1 = P(X, ty - 0.35 - 0.1 * k, z0 + cz), P(X, ty - 0.35 - 0.1 * k, z0 + 1.6 + cz)
            s.append(line([p0, p1], 6, "#ffffff", taper=.6, seed=1320 + k, op=.8 * a))
    u = clamp((t - 22.52) / 2.4)
    cm = cam(560 - 10 * u, 905 - 8 * u, 1.04 - 0.03 * ease_io(u), 0.2 - 0.4 * u)
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
