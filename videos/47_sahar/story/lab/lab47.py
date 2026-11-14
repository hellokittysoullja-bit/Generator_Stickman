"""Сцена lab рилса 47, планы s05 (7.6–9.6), s06 (9.6–11.1), s07 (11.1–12.6): «опыты, где никто не знал, что ели дети».
Лаборатория: длинный стол, за ним пятеро детей с одинаковыми стаканами, позади трое взрослых в белых халатах.
s05 — рука исследовательницы сверху капает пипеткой в стаканы по очереди, на «деле» (8.2) удар; табличка «опыт» качается.
s06 — ширма поднимается над стаканами, над головами взрослых выскакивают вопросительные знаки (9.8, 10.3).
s07 — крупно ребёнок спокойно пьёт, слева перечёркнутый кубик сахара, на «заводил» (11.84) шкала падает на «0».
Люди — person.py (кисти из пяти пальцев). Без букв нейросети: «опыт» и «?» — шрифт Caveat кодом, остальное — геометрия."""
import math

import lib
import person
from c44 import hand_text, kick, pop, shake, wt
from hands5 import hand5
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, mul, rad_grad,
                 rect_pts, shape, spring, svg)

_ST = {}
T_DELE = wt("деле")          # 8.2
T_ZNAL = wt("знал")          # 9.76
T_ELI = wt("ели")            # 10.32
T_ZAVOD = wt("заводил")      # 11.84
FLOOR = 1250
TOP_Y0, TOP_Y1, FRONT_Y1 = 1090, 1128, 1340      # столешница сзади/спереди, низ тумбы
KX = [150, 345, 540, 735, 930]
SC_K, SC_A = 0.5, 0.58
WALL, WALL_D = "#d9e8e0", "#c6d9cf"
WOOD, WOOD_D, WOOD_L = "#b98557", "#8f5f3a", "#d3a273"
WATER, WATER_D = "#a9d8ee", "#7fbcd9"
COAT, COAT_D = "#f6f4ee", "#d9d6cf"

KIDS = [
    dict(skin="#f1c4a2", hair="short", hair_c="#5a3a26", top="#e0a64a", low="#3b3f58", shoes="#3a3440", face=0.25, h=1.0, hw=1.08, brow_c="#3a2a22"),
    dict(skin="#e8b896", hair="ponytail", hair_c="#c8622a", top="#d8433a", low="#2c3140", shoes="#3a3440", face=0.2, h=1.0, hw=1.08, brow_c="#8a4a26"),
    dict(skin="#8a5a3c", hair="curly", hair_c="#1c1412", top="#3f6f9a", low="#4a4136", shoes="#3a3440", face=0.0, h=1.0, hw=1.1, brow_c="#1c1412"),
    dict(skin="#f4d0b4", hair="bun", hair_c="#2a1a14", top="#7a5a9a", low="#34404c", shoes="#3a3440", face=-0.2, h=1.0, hw=1.08, brow_c="#2a1a14"),
    dict(skin="#d9a07a", hair="short", hair_c="#1a1210", top="#5f8f5a", low="#2c3140", shoes="#3a3440", face=-0.25, h=1.0, hw=1.08, brow_c="#1a1210"),
]
ADULTS = [
    dict(x=247, spec=dict(skin="#efc3a2", hair="bob", hair_c="#2e2421", top=COAT, low="#2c3140", shoes="#3a2a22", face=0.3, h=0.95,
                          sleeve=COAT, collar="#9ec3d8", brow_c="#2a1e1a", glasses=True)),
    dict(x=637, spec=dict(skin="#d9a07a", hair="short", hair_c="#2a1a14", top=COAT, low="#34404c", shoes="#3a2a22", face=-0.3, h=1.0,
                          sleeve=COAT, collar="#e0a64a", brow_c="#2a1a14", beard="#2a1a14", bw=1.1)),
    dict(x=832, spec=dict(skin="#f2c9a8", hair="bun", hair_c="#8a8a90", top=COAT, low="#4a4136", shoes="#3a2a22", face=-0.2, h=0.92,
                          sleeve=COAT, collar="#d8433a", brow_c="#6a6a70", glasses=True)),
]


def ik(sh, tgt, L1=130, L2=120):
    dx, dy = tgt[0] - sh[0], tgt[1] - sh[1]
    L = max(abs(L1 - L2) + 1, min(L1 + L2 - 0.5, math.hypot(dx, dy)))
    base = math.degrees(math.atan2(dx, dy))
    c = clamp((L1 * L1 + L * L - L2 * L2) / (2 * L1 * L), -1, 1)
    d = math.degrees(math.acos(c))
    a1 = min((base - d, base + d), key=lambda a: abs(((a + 180) % 360) - 180))
    ex, ey = sh[0] + L1 * math.sin(math.radians(a1)), sh[1] + L1 * math.cos(math.radians(a1))
    a_f = math.degrees(math.atan2(tgt[0] - ex, tgt[1] - ey))
    return a1, a_f - a1


def with_hands(spec, x, y, sc, hands, pose, sd):
    """Человек стоит ступнями в (x, y); hands {'L'/'R': (x, y) мира} — кисти ставятся обратной кинематикой."""
    S = sc * spec.get("h", 1.0)
    sh_w = 74 * spec.get("bw", 1.0)
    shs = {"L": (-sh_w + 10, -502), "R": (sh_w - 10, -502)}
    arms = {}
    for side, tw in hands.items():
        tl = ((tw[0] - x) / S, (tw[1] - y) / S)
        a, b = ik(shs[side], tl)
        sign = -1 if side == "L" else 1
        arms[side] = (a - sign * 6, b)
    pose = dict(pose)
    pose["arms"] = arms
    pose["near_front"] = True
    return person.draw(spec, pose, x, y, sc, sd=sd)


# ───────────────────────── предметы
def glass(x, yb, level=0.62, k=1.0, tilt=0.0, liquid=WATER, sd=1, tag=False):
    """Стакан: низ по центру в (x, yb). Не прозрачный: светлое стекло, жидкость плоским цветом, блик."""
    w_t, w_b, h = 31 * k, 24 * k, 86 * k
    body = [(-w_t, -h, 1), (w_t, -h, 1), (w_b, 0, 1), (-w_b, 0, 1)]
    yl = -h * level
    wl = w_b + (w_t - w_b) * (1 - level)
    liq = [(-wl, yl, 1), (wl, yl, 1), (w_b, 0, 1), (-w_b, 0, 1)]
    inner = blob(liq, liquid)
    inner += blob([(-wl, yl), (wl, yl), (wl, yl + 7 * k), (-wl, yl + 7 * k)], mul(liquid, (.88, .9, .95)))
    inner += blob([(w_t * .35, -h), (w_t, -h), (w_b, 0), (w_b * .4, 0)], mul(liquid, (.92, .94, .98)), .0)
    inner += line([(-w_t + 9 * k, -h + 12 * k), (-w_b + 8 * k, -12 * k)], 4 * k, "#ffffff", taper=.4, wmin=.3, seed=sd + 5)
    s = shape(body, "#e9f4f8", inner, w=3.8, seed=sd)
    rim = shape(ellipse_pts(0, -h, w_t, 6 * k, 14), "#f5fbfd", "", w=3.0, seed=sd + 1)
    return f'<g transform="translate({f(x)} {f(yb)}) rotate({f(tilt)})">{s}{rim}</g>'


def drop(x, y, r, col="#d6ecf7"):
    pts = [(x, y - r * 1.9, 1), (x + r * .85, y - r * .2), (x + r, y + r * .5), (x, y + r * 1.1), (x - r, y + r * .5), (x - r * .85, y - r * .2)]
    return shape(pts, col, line([(x - r * .4, y - r * .2), (x - r * .35, y + r * .4)], 2, "#ffffff", seed=int(x) + 3), w=2.6, seed=int(x * 3) % 997)


def pipette(x, y, squeeze=0.0):
    """Пипетка: резиновая груша сверху, стеклянная трубка вниз, носик в (x, y)."""
    s = []
    tube_top = y - 150
    s.append(shape([(x - 7, tube_top, 1), (x + 7, tube_top, 1), (x + 6, y - 14, 1), (x + 2.5, y, 1), (x - 2.5, y, 1), (x - 6, y - 14, 1)], "#e9f4f8",
                   blob([(x - 6, y - 70), (x + 6, y - 70), (x + 6, y - 14), (x + 2.5, y), (x - 2.5, y), (x - 6, y - 14)], "#e6b25a"), w=3.0, seed=410))
    sq = 1 - 0.16 * squeeze
    bulb = [(x - 6, tube_top + 2, 1), (x - 21 * sq, tube_top - 18), (x - 24 * sq, tube_top - 60), (x - 12 * sq, tube_top - 90), (x, tube_top - 96),
            (x + 12 * sq, tube_top - 90), (x + 24 * sq, tube_top - 60), (x + 21 * sq, tube_top - 18), (x + 6, tube_top + 2, 1)]
    s.append(shape(bulb, "#d8433a", blob([(x + 6, tube_top), (x + 21 * sq, tube_top - 18), (x + 24 * sq, tube_top - 60), (x + 12 * sq, tube_top - 90), (x + 4, tube_top - 70)],
                                         "#a82c28", .9)
                   + line([(x - 12 * sq, tube_top - 70), (x - 14 * sq, tube_top - 40)], 4, "#ffb3a8", taper=.4, seed=412), w=3.4, seed=411))
    s.append(shape(rect_pts(x - 11, tube_top - 2, x + 11, tube_top + 10), "#f2f2ee", "", w=2.8, seed=413))
    return "".join(s)


def sugar_cube(cx, cy, k, sd=1, rot=0.0):
    """Кубик сахара в изометрии: верх светлее, левая грань белая, правая в тени, зёрнышки."""
    a = 62 * k
    top = [(cx, cy - a * 1.0, 1), (cx + a * .9, cy - a * .5, 1), (cx, cy, 1), (cx - a * .9, cy - a * .5, 1)]
    left = [(cx - a * .9, cy - a * .5, 1), (cx, cy, 1), (cx, cy + a * 1.0, 1), (cx - a * .9, cy + a * .5, 1)]
    right = [(cx, cy, 1), (cx + a * .9, cy - a * .5, 1), (cx + a * .9, cy + a * .5, 1), (cx, cy + a * 1.0, 1)]
    dots = ""
    for i, (u, v) in enumerate([(.2, .3), (.6, .2), (.4, .7), (.8, .6), (.15, .8)]):
        dots += f'<circle cx="{f(cx - a * .9 + a * .9 * u)}" cy="{f(cy - a * .5 + a * .5 * (u + v) * .9)}" r="{f(2.2 * k)}" fill="#d8d2c4"/>'
    s = shape(left, "#fbfaf6", dots, w=3.4, seed=sd) + shape(right, "#d9d6cf", "", w=3.4, seed=sd + 1) + shape(top, "#ffffff", "", w=3.4, seed=sd + 2)
    return f'<g transform="rotate({f(rot)} {f(cx)} {f(cy)})">{s}</g>'


# ───────────────────────── комната
def background():
    s = []
    g = lin_grad([(0, "#cfe1d8", 1), (1, "#e4efe8", 1)], 0, -400, 0, FLOOR, units="userSpaceOnUse")
    s.append(f'<rect x="-500" y="-500" width="{W + 1000}" height="{FLOOR + 500}" fill="url(#{g})"/>')
    for x in range(-500, W + 500, 100):
        s.append(f'<rect x="{x}" y="-500" width="3" height="{FLOOR + 500}" fill="{WALL_D}"/>')
    for y in range(-500, FLOOR, 100):
        s.append(f'<rect x="-500" y="{y}" width="{W + 1000}" height="3" fill="{WALL_D}"/>')
    # плинтус и пол
    s.append(shape(rect_pts(-500, FLOOR - 26, W + 500, FLOOR + 8), "#a8b8ae", "", w=3.2, seed=701))
    gf = lin_grad([(0, "#a88a66", 1), (1, "#7e6446", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-500" y="{FLOOR + 8}" width="{W + 1000}" height="1200" fill="url(#{gf})"/>')
    for i, y in enumerate([1390, 1470, 1580, 1720, 1900]):
        s.append(line([(-500, y), (W + 500, y)], 2.6, "#5f4a30", taper=.05, wmin=.9, seed=720 + i, op=.8))
    for i, x in enumerate(range(-300, W + 300, 260)):
        s.append(line([(x + (i % 2) * 90, 1360), (x + (i % 2) * 90 - 90, 1960)], 2.4, "#5f4a30", taper=.05, wmin=.9, seed=740 + i, op=.55))
    # плакат слева: таблица цветных клеток
    px0, py0 = 40, 380
    cells = ""
    cols = ["#e0a64a", "#d8433a", "#3f6f9a", "#5f8f5a", "#7a5a9a", "#2f8f8a", "#d98a4a"]
    for r in range(4):
        for c in range(5):
            cells += blob(rect_pts(px0 + 16 + c * 46, py0 + 18 + r * 44, px0 + 16 + c * 46 + 38, py0 + 18 + r * 44 + 36), cols[(r * 3 + c * 2) % 7])
    s.append(blob(rect_pts(px0 + 8, py0 + 10, px0 + 258, py0 + 214), "#2a1608", .18, blur(8)))
    s.append(shape(rect_pts(px0, py0, px0 + 246, py0 + 204), "#fbf9f2", cells, w=3.6, seed=750))
    # полка справа с колбами
    sx0, sy = 760, 600
    s.append(shape(rect_pts(sx0, sy, 1130, sy + 22), WOOD, blob(rect_pts(sx0, sy + 13, 1130, sy + 22), WOOD_D), w=3.4, seed=760))
    for i, (x, c, kind) in enumerate([(810, "#d8433a", "flask"), (885, "#5f8f5a", "tube"), (960, "#e0a64a", "flask"), (1040, "#3f6f9a", "tube")]):
        if kind == "flask":
            pts = [(x - 11, sy - 90, 1), (x + 11, sy - 90, 1), (x + 12, sy - 50, 1), (x + 36, sy - 6, 1), (x - 36, sy - 6, 1), (x - 12, sy - 50, 1)]
            s.append(shape(pts, "#e9f4f8", blob([(x - 12, sy - 40), (x + 12, sy - 40), (x + 36, sy - 6), (x - 36, sy - 6)], c), w=3.2, seed=770 + i))
        else:
            s.append(shape(rect_pts(x - 14, sy - 120, x + 14, sy - 4, 8), "#e9f4f8", blob(rect_pts(x - 14, sy - 60, x + 14, sy - 4, 8), c), w=3.2, seed=770 + i))
    # потолочная лампа-линия
    s.append(shape(rect_pts(200, -30, 880, 6, 6), "#fffbe8", "", w=3.2, seed=780))
    return "".join(s)


def sign(t):
    """Табличка «ОПЫТ» на двух цепочках; качается от удара."""
    hx, hy = 540, 300
    amp = 2.2 * math.sin(t * 1.9) + (7.5 * math.exp(-(t - T_DELE) * 4.5) * math.sin((t - T_DELE) * 17) if t >= T_DELE else 0.0)
    cx, cy, w, h = 540, 470, 400, 120
    chains = line([(hx - 150, hy), (cx - 150, cy - h / 2 + 2)], 5, "#6a737a", taper=.05, wmin=.9, seed=790) + \
        line([(hx + 150, hy), (cx + 150, cy - h / 2 + 2)], 5, "#6a737a", taper=.05, wmin=.9, seed=791)
    plate = shape(rect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 14), "#fbf9f2",
                  blob(rect_pts(cx - w / 2 + 10, cy + h / 2 - 22, cx + w / 2 - 10, cy + h / 2 - 8, 6), "#e2dccd") +
                  blob(ellipse_pts(cx - w / 2 + 34, cy - h / 2 + 22, 8, 8, 10), "#9aa4a8") + blob(ellipse_pts(cx + w / 2 - 34, cy - h / 2 + 22, 8, 8, 10), "#9aa4a8"),
                  w=4.6, seed=792)
    txt = hand_text(cx + 22, cy + 30, "ОПЫТ", 104, "#1f4b5a", weight=700)
    flask = shape([(cx - 160, cy - 30, 1), (cx - 146, cy - 30, 1), (cx - 146, cy - 8), (cx - 128, cy + 28, 1), (cx - 178, cy + 28, 1), (cx - 160, cy - 8)], "#e9f4f8",
                  blob([(cx - 170, cy + 6), (cx - 136, cy + 6), (cx - 128, cy + 28), (cx - 178, cy + 28)], "#d8433a"), w=3.0, seed=793)
    return f'<g transform="rotate({f(amp)} {hx} {hy})">{chains}{plate}{flask}{txt}</g>'


def bench_top():
    s = []
    top = [(-60, TOP_Y0, 1), (W + 60, TOP_Y0, 1), (W + 100, TOP_Y1, 1), (-100, TOP_Y1, 1)]
    s.append(shape(top, WOOD_L, blob([(-60, TOP_Y0), (W + 60, TOP_Y0), (W + 70, TOP_Y0 + 8), (-70, TOP_Y0 + 8)], "#e6bd90", .8), w=4.4, seed=801))
    s.append(shape(rect_pts(-100, TOP_Y1, W + 100, TOP_Y1 + 24), WOOD_D, "", w=4.0, seed=802))
    return "".join(s)


def bench_front():
    s = []
    y0, y1 = TOP_Y1 + 24, FRONT_Y1
    s.append(shape(rect_pts(-100, y0, W + 100, y1), WOOD, blob(rect_pts(-100, y1 - 30, W + 100, y1), WOOD_D, .9), w=4.4, seed=810))
    for k in range(6):
        x0 = -40 + k * 190
        s.append(shape(rect_pts(x0, y0 + 22, x0 + 170, y1 - 26, 6), WOOD_L, blob(rect_pts(x0 + 8, y0 + 32, x0 + 162, y0 + 44), "#e6bd90", .7) +
                       blob(rect_pts(x0 + 128, y0 + 22, x0 + 170, y1 - 26), WOOD_D, .35), w=3.4, seed=820 + k))
        s.append(shape(rect_pts(x0 + 62, y0 + 46, x0 + 108, y0 + 58, 5), "#6a737a", "", w=2.6, seed=840 + k))
    s.append(blob(rect_pts(-100, y1, W + 100, y1 + 26), "#3a2a16", .3, blur(9)))
    return "".join(s)


# ───────────────────────── люди
def kid_pose(i, t, calm=False):
    ph = i * 1.37
    blink = 1.0 if ((t + ph) % 3.1) < 0.09 else 0.0
    return dict(look=(0.2 * math.sin(t * 1.1 + ph) + (0.35 if i < 2 else -0.2), 0.25), mouth="smile" if calm else "flat", blink=blink,
                head_tilt=2.4 * math.sin(t * 2.0 + ph), brow=.1, hmode={"L": "rest", "R": "rest"})


def kid(i, t, hands=None, **kw):
    x = KX[i]
    bob = 1.6 * math.sin(t * 2.6 + i * 1.1)
    hl = (x - 44, TOP_Y0 - 14 + bob * .3)
    hr = (x + 40, TOP_Y0 - 14 - bob * .3)
    h = {"L": hl, "R": hr}
    if hands:
        h.update(hands)
    pose = kid_pose(i, t, **{k: v for k, v in kw.items() if k == "calm"})
    if "pose" in kw:
        pose.update(kw["pose"])
    return with_hands(KIDS[i], x, FLOOR - 4 + bob, SC_K, h, pose, 5000 + i * 300)


def adult(j, t, hands=None, pose_extra=None):
    a = ADULTS[j]
    x, spec = a["x"], a["spec"]
    y = FLOOR - 34
    ph = j * 1.9
    blink = 1.0 if ((t + ph) % 3.4) < 0.09 else 0.0
    pose = dict(look=(0.15 * math.sin(t * 1.3 + ph) + (0.3 if j == 0 else -0.1), 0.3), mouth="flat", blink=blink,
                head_tilt=2.0 * math.sin(t * 1.6 + ph), brow=.1, hmode={"L": "rest", "R": "rest"})
    if pose_extra:
        pose.update(pose_extra)
    S = SC_A * spec.get("h", 1.0)
    # руки: вдоль тела спрятаны за детьми; по умолчанию сложены у пояса
    hd = {"L": (x - 22, y - 205 * S), "R": (x + 22, y - 205 * S)}
    if hands:
        hd.update(hands)
    return with_hands(spec, x, y, SC_A, hd, pose, 7000 + j * 300)


def sleeve_arm(x0, y0, hx, hy, t):
    """Рука в белом рукаве сверху (за кадром) держит пипетку; рукав из person.tube."""
    mx, my = (x0 + hx) / 2 + 30, (y0 + hy) / 2 - 10
    s = person.tube((x0, y0), (mx, my), (hx, hy - 4), 56, 50, 40, COAT, 600)
    s += shape(rect_pts(hx - 24, hy - 16, hx + 24, hy + 0, 6), COAT_D, "", w=3.0, seed=610)
    return s


GX = [x + 58 for x in KX]      # стакан стоит справа от ребёнка
TIP_Y = 996


def pipette_group(tx, ty, squeeze, ang=20.0):
    """Рука с пипеткой: носик в (tx, ty), всё повёрнуто на ang вокруг носика; рукав уходит за верх кадра."""
    pip = pipette(0, 0, squeeze)
    sleeve = person.tube((60, -900), (30, -500), (-8, -176), 74, 66, 52, COAT, 600)
    cuff = shape(rect_pts(-34, -232, 18, -196, 6), COAT_D, "", w=3.0, seed=610)
    hnd = hand5(-12, -166, 90, "#efc3a2", person.shade("#efc3a2"), 650, sc=1.0, mode="grip", thumb_up=False, ink_w=3.2)
    return f'<g transform="translate({f(tx)} {f(ty)}) rotate({f(ang)}) scale(1.35)">{pip}{sleeve}{cuff}{hnd}</g>'


# ───────────────────────── s05
GLASS_Y = TOP_Y1 - 6
# время капли в стакан i; удар — на «деле»
DROP_T = [T_DELE - 0.42, T_DELE, T_DELE + 0.42, T_DELE + 0.84, T_DELE + 1.26]


def pip_x(t):
    """Пипетка переезжает к стакану i, на капле стоит."""
    ks = [(DROP_T[0] - 0.9, GX[0] - 150)]
    for i in range(5):
        ks.append((DROP_T[i] - 0.22 if i else DROP_T[0] - 0.3, GX[i]))
        ks.append((DROP_T[i] + 0.1, GX[i]))
    ks.append((DROP_T[4] + 0.75, GX[4] + 140))
    if t <= ks[0][0]:
        return ks[0][1]
    for (ta, xa), (tb, xb) in zip(ks, ks[1:]):
        if t <= tb:
            return xa + (xb - xa) * ease_io((t - ta) / (tb - ta)) if tb > ta else xb
    return ks[-1][1]


def levels(t):
    out = []
    for i in range(5):
        k = clamp((t - DROP_T[i] - 0.2) / 0.3)
        out.append(0.55 + 0.05 * k)
    return out


def frame_s05(t):
    s = [_ST["bg"], sign(t)]
    for j in (0, 1, 2):
        s.append(adult(j, t))
    for i in range(5):
        s.append(kid(i, t, calm=False))
    s.append(_ST["top"])
    lv = levels(t)
    for i in range(5):
        s.append(glass(GX[i], GLASS_Y, lv[i], 1.0, sd=100 + i * 10))
    # капли, круги на воде и брызги
    for i in range(5):
        q = t - DROP_T[i]
        gx = GX[i]
        top_y = GLASS_Y - 86 * lv[i]
        if -0.3 <= q < 0:
            u = (q + 0.3) / 0.3
            s.append(drop(gx, TIP_Y + 8 + (top_y - 14 - TIP_Y) * u * u, 8 + 2 * (1 - u)))
        if 0 <= q < 0.5:
            u = q / 0.5
            rr = 20 + 26 * ease_out(u)
            if u < .98:
                s.append(f'<ellipse cx="{f(gx)}" cy="{f(top_y)}" rx="{f(rr)}" ry="{f(rr * .22)}" fill="none" stroke="#ffffff" stroke-width="{f(3.4 * (1 - u))}" '
                         f'opacity="{f(1 - u)}"/>')
            if u < .9:
                for k in range(5):
                    a = -math.pi / 2 + (k - 2) * 0.5
                    d = 50 * ease_out(u)
                    s.append(f'<circle cx="{f(gx + math.cos(a) * d * .7)}" cy="{f(top_y - 8 + math.sin(a) * d + 60 * u * u)}" r="{f(4.4 * (1 - u))}" '
                             f'fill="#d6ecf7" stroke="{INK}" stroke-width="2" opacity="{f(1 - u)}"/>')
    sq = 0.0
    for i in range(5):
        q = t - DROP_T[i]
        if -0.2 < q < 0.08:
            sq = max(sq, 1 - abs(q + 0.06) / 0.14)
    s.append(pipette_group(pip_x(t), TIP_Y + 3 * math.sin(t * 8), sq))
    return "".join(s)


def cam05(t):
    u = clamp((t - 7.4) / 2.4)
    k, rot = kick(t, [T_DELE], 0.04, 11)
    cx = 0.45 * pip_x(t) + 0.55 * 540
    sc = 1.42 + 0.3 * ease_io(u)
    return cam(cx, 1010 - 30 * u, sc * k, rot + 1.4 - 2.2 * u)


# ───────────────────────── s06
def screen_up(t):
    """Ширма-гармошка: поднимается за стаканами с перелётом."""
    u = clamp((t - 9.42) / 0.34)
    return ease_out(u, 3) + 0.06 * math.sin(clamp((t - 9.76) / 0.3) * math.pi) * (1 - clamp((t - 9.76) / 0.3)) * 3


def screen_shape(up):
    yb = TOP_Y1 + 20
    yt0 = 975
    h = (yb - yt0)
    ytop = yb - h * clamp(up, 0, 1.08)
    s = []
    n = 12
    x0, x1 = -60, W + 60
    pw = (x1 - x0) / n
    for k in range(n):
        xa, xb = x0 + k * pw, x0 + (k + 1) * pw
        col = "#e9d8b4" if k % 2 == 0 else "#d4bf92"
        col_sh = "#cdb685"
        pts = [(xa, ytop, 1), (xb, ytop + (3 if k % 2 == 0 else -3), 1), (xb, yb, 1), (xa, yb + (3 if k % 2 == 0 else -3), 1)]
        shade_part = blob([(xa + pw * .5, ytop), (xb, ytop), (xb, yb), (xa + pw * .5, yb)], col_sh, .55) if k % 2 == 0 else ""
        s.append(shape(pts, col, shade_part, w=3.6, seed=900 + k))
    s.append(shape(rect_pts(x0, ytop - 4, x1, ytop + 12), "#8f5f3a", "", w=3.4, seed=920))
    s.append(shape(rect_pts(x0, yb - 8, x1, yb + 8), "#8f5f3a", "", w=3.4, seed=921))
    return "".join(s)


def qmark(x, y, t, t0, sd, size=150, rot=-6):
    k = pop(t, t0, 0.12, 0.32)
    if k <= 0.01:
        return ""
    yy = y - 10 * ease_out((t - t0) / 0.3) + 4 * math.sin(t * 7 + sd)
    return (f'<g transform="translate({f(x)} {f(yy)}) scale({k:.3f}) translate({-x} {f(-yy)})">'
            + hand_text(x, yy, "?", size, "#f2c232", stroke=INK, sw=14, weight=700, rot=rot + 5 * math.sin(t * 6 + sd)) + "</g>")


def frame_s06(t):
    s = [_ST["bg"], sign(t)]
    for j in (0, 1, 2):
        x = ADULTS[j]["x"]
        hands = None
        pe = {}
        t_q = [T_ZNAL + 0.02, T_ZNAL + 0.08, T_ELI + 0.0][j]
        if t > t_q:
            pe = dict(mouth="o" if j != 1 else "frown", brow=0.8, look=(0.0, -0.2))
        if False:
            # рука к голове: чешет затылок
            y = FLOOR - 34
            S = SC_A * ADULTS[0]["spec"]["h"]
            hands = {"R": (x + 44 * S + 6 * math.sin(t * 17), y - 600 * S + 4 * math.cos(t * 17)), }
        s.append(adult(j, t, hands, pe))
    for i in range(5):
        s.append(kid(i, t, calm=False))
    s.append(_ST["top"])
    for i in range(5):
        s.append(glass(GX[i], GLASS_Y, 0.6, 1.0, sd=100 + i * 10))
    up = screen_up(t)
    # руки-стрелки не нужны: ширма закрывает стаканы
    s.append(screen_shape(up))
    qs = [(ADULTS[0]["x"] + 70, 700, T_ZNAL, 1, 160), (ADULTS[1]["x"] + 66, 700, T_ZNAL + 0.06, 2, 150), (ADULTS[2]["x"] - 10, 690, T_ELI, 3, 160),
          (ADULTS[0]["x"] - 40, 740, T_ELI + 0.12, 4, 110)]
    for x, y, t0, sd, sz in qs:
        s.append(qmark(x, y, t, t0, sd, sz, rot=-8 if sd % 2 else 8))
    return "".join(s)


def cam06(t):
    u = clamp((t - 9.4) / 1.9)
    k, rot = kick(t, [T_ZNAL, T_ELI], 0.032, 13)
    return cam(540 + 10 * math.sin(u * 3), 1000 - 20 * u, (1.34 + 0.08 * u) * k, rot - 0.5 + 0.9 * u)


# ───────────────────────── s07
KID_I = 2


def gauge(t, cx, cy):
    """Шкала-полукруг: тиканье, стрелка с перелётом падает на «0»; цифра «0» крупно."""
    appear = pop(t, 11.38, 0.12, 0.2) * 0.85
    if appear <= 0.01:
        return ""
    R = 120
    s = []
    for k in range(9):
        a = math.pi * (1 - k / 8)
        col = ["#5f8f5a", "#5f8f5a", "#a8b84a", "#e0a64a", "#e0a64a", "#d98a4a", "#d8433a", "#d8433a", "#d8433a"][k]
        r0, r1 = R - 26, R
        s.append(line([(cx + math.cos(a) * r0, cy - math.sin(a) * r0), (cx + math.cos(a) * r1, cy - math.sin(a) * r1)], 11, col, taper=.05, wmin=.9, seed=1100 + k))
    base = shape(ellipse_pts(cx, cy, R + 24, R + 24, 28), "#fbf9f2", "", w=4.4, seed=1120)
    # нижнюю половину круга закрывает плашка цвета стены
    inner = shape([(cx - R - 24, cy, 1), (cx + R + 24, cy, 1), (cx + R + 24, cy + 70, 1), (cx - R - 24, cy + 70, 1)], "#fbf9f2", "", w=4.4, seed=1121)
    # положение: 0 — влево, 1 — вправо
    if t < T_ZAVOD:
        v = 0.78 + 0.07 * math.sin(t * 19) + 0.03 * math.sin(t * 37)
    else:
        q = t - T_ZAVOD
        v = 0.78 * (1 - clamp(q / 0.07)) if q < 0.07 else 0.0
        v += 0.0 + max(0.0, 0.1 * math.exp(-(q - 0.07) * 14) * math.cos((q - 0.07) * 40)) if q >= 0.07 else 0.0
        v = max(0.0, v)
    a = math.pi * (1 - v)
    nx, ny = cx + math.cos(a) * (R - 12), cy - math.sin(a) * (R - 12)
    needle = line([(cx, cy), (nx, ny)], 9, INK, taper=.1, wmin=.7, seed=1130)
    hub = shape(ellipse_pts(cx, cy, 15, 15, 12), "#d8433a", "", w=3.4, seed=1131)
    out = base + inner + "".join(s) + needle + hub
    z = pop(t, T_ZAVOD + 0.05, 0.12, 0.3) if t >= T_ZAVOD else 0.0
    zero = ""
    if z > 0.01:
        zx, zy = cx, cy + 66
        zero = (f'<g transform="translate({f(zx)} {f(zy)}) scale({z:.3f}) translate({-zx} {-zy})">'
                + hand_text(zx, zy + 30, "0", 130, "#d8433a", stroke="#fbf9f2", sw=12, weight=700) + "</g>")
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({appear:.3f}) translate({-cx} {-cy})">{out}</g>{zero}'


def cube_card(t, cx, cy):
    appear = pop(t, 11.14, 0.12, 0.22) * 0.8
    if appear <= 0.01:
        return ""
    wob = 3.5 * math.sin(t * 3.1)
    card = shape(rect_pts(cx - 130, cy - 130, cx + 130, cy + 130, 16), "#fbf9f2", "", w=4.4, seed=1200)
    cube = sugar_cube(cx, cy - 6, 1.25, 1210, rot=0)
    # красный крест рисуется кистью
    u1 = clamp((t - 11.42) / 0.14)
    u2 = clamp((t - 11.54) / 0.14)
    x_ = ""
    if u1 > 0:
        x_ += line([(cx - 92, cy - 92), (cx - 92 + 184 * u1, cy - 92 + 184 * u1)], 20, "#d8433a", taper=.08, wmin=.85, seed=1220) if u1 > .05 else ""
    if u2 > 0:
        x_ += line([(cx + 92, cy - 92), (cx + 92 - 184 * u2, cy - 92 + 184 * u2)], 20, "#d8433a", taper=.08, wmin=.85, seed=1221) if u2 > .05 else ""
    pin = shape(ellipse_pts(cx, cy - 130, 11, 11, 10), "#d8433a", "", w=3.0, seed=1230)
    return (f'<g transform="translate({f(cx)} {f(cy)}) scale({appear:.3f}) rotate({f(wob)}) translate({-cx} {-cy})">{card}{cube}{x_}{pin}</g>')


def frame_s07(t):
    s = [_ST["bg"], sign(t)]
    for j in (0, 1, 2):
        s.append(adult(j, t, None, dict(mouth="flat")))
    # соседи
    for i in range(5):
        if i == KID_I:
            continue
        s.append(kid(i, t, calm=True))
    x = KX[KID_I]
    # ребёнок пьёт: цикл поднять-держать-опустить, после «заводил» сидит смирно
    cyc = (t - 10.98)
    if t < T_ZAVOD - 0.2:
        q = clamp(cyc / 0.5)
        lift = ease_io(q) if cyc < 0.5 else (1.0 if cyc < 0.95 else 1 - ease_io((cyc - 0.95) / 0.35))
        lift = clamp(lift)
    else:
        lift = 1 - ease_io(clamp((t - (T_ZAVOD - 0.2)) / 0.3))
    gx = (x + 58) + (x + 22 - (x + 58)) * lift
    gy = (GLASS_Y) + (985 - GLASS_Y) * lift
    tilt = -24 * lift
    pose = dict(mouth="smile" if lift < .2 else "flat", brow=0.0, look=(0.0, 0.2 + 0.2 * lift), head_tilt=2 + 3 * lift)
    hr = (gx - 4, gy - 40)
    s.append(kid(KID_I, t, hands={"R": hr, "L": (x - 52, TOP_Y0 - 16)}, calm=True, pose=pose))
    s.append(_ST["top"])
    for i in range(5):
        if i != KID_I:
            s.append(glass(GX[i], GLASS_Y, 0.58, 1.0, sd=100 + i * 10))
    s.append(glass(gx, gy, 0.55 - 0.15 * lift, 1.0, tilt, sd=100 + KID_I * 10))
    s.append(cube_card(t, 395, 640))
    s.append(gauge(t, 685, 650))
    return "".join(s)


def cam07(t):
    u = clamp((t - 10.9) / 1.9)
    k, rot = kick(t, [T_ZAVOD], 0.035, 12)
    sc = 1.7 + 0.4 * ease_io(u)
    return cam(540 + 5 * math.sin(t * 2), 850 + 60 * u, sc * k, rot + 0.8 - 1.4 * u)


def frame(sid, t):
    if not _ST:
        lib.DEFS.clear()
        _ST["bg"] = background()
        _ST["top"] = bench_top() + bench_front()
        lib.static_done()
    lib.dyn_begin()
    if sid == "s05":
        body, c = frame_s05(t), cam05(t)
    elif sid == "s06":
        body, c = frame_s06(t), cam06(t)
    else:
        body, c = frame_s07(t), cam07(t)
    return svg(f'<rect width="{W}" height="{H}" fill="{WALL}"/><g transform="{c}">{body}</g>')


_ = (ease_in, mix, rad_grad, spring, shake)
