"""Сцена moms рилса 47, план s09 (14.6–17.4, клип 14.4–17.6): «Мамам говорили, что ребёнок выпил сладкий напиток».
Комната: слева мама слушает, у неё рука у подбородка; со стены динамик, из него идут волны и облачко-реплика со стаканом розового
напитка и кубиками (без букв). Справа за столом ребёнок пьёт обычную воду, на стакане бирка с кубиком сахара. На «сладкий» (16.4)
мама кивает, значок в облачке подпрыгивает. Люди — person.py, обратная кинематика рук — lab47.with_hands."""
import math

import lib
import props
from c44 import hand_text, kick, pop, wt
from lab47 import KIDS, glass, kid_pose, sugar_cube, with_hands
from lib import (INK, W, H, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, rect_pts, shape, svg)

_ST = {}
T_MAM = wt("Мамам")        # 14.64
T_GOV = wt("говорили")     # 14.96
T_VYP = wt("выпил")        # 16.08
T_SLAD = wt("сладкий")     # 16.4
T_NAP = wt("напиток")      # 16.8
FLOOR = 1250
TOP_Y0, TOP_Y1 = 1090, 1128
KX = 790
WALL, WALL_D = "#f1e3cc", "#e5d2b4"
WOOD, WOOD_D, WOOD_L = "#b98557", "#8f5f3a", "#d3a273"
MOM = dict(skin="#e8b896", hair="ponytail", hair_c="#5a3a26", top="#e09a52", low="#3b4a6a", shoes="#3a2a22", face=0.5, h=1.0, sleeve="#e09a52",
           collar="#fbe6c8", brow_c="#4a2e20")
PINK = "#f3a0b8"
MX = 280
SC_M, SC_K = 0.8, 0.6


def background():
    s = []
    g = lin_grad([(0, "#f6ead6", 1), (1, "#ecdcc0", 1)], 0, -400, 0, FLOOR, units="userSpaceOnUse")
    s.append(f'<rect x="-500" y="-500" width="{W + 1000}" height="{FLOOR + 500}" fill="url(#{g})"/>')
    for x in range(-500, W + 500, 90):
        s.append(f'<rect x="{x}" y="-500" width="30" height="{FLOOR + 500}" fill="{WALL_D}" opacity=".55"/>')
    s.append(shape(rect_pts(-500, FLOOR - 26, W + 500, FLOOR + 8), "#fbf4e6", "", w=3.2, seed=1301))
    gf = lin_grad([(0, "#a88a66", 1), (1, "#7e6446", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-500" y="{FLOOR + 8}" width="{W + 1000}" height="1200" fill="url(#{gf})"/>')
    for i, y in enumerate([1390, 1470, 1580, 1720, 1900]):
        s.append(line([(-500, y), (W + 500, y)], 2.6, "#5f4a30", taper=.05, wmin=.9, seed=1320 + i, op=.8))
    # ковёр
    s.append(shape([(-60, 1300, 1), (700, 1300, 1), (760, 1480, 1), (-120, 1480, 1)], "#c9554c", blob([(-60, 1330), (700, 1330), (710, 1350), (-70, 1350)], "#e07a62", .8)
                   + line([(-40, 1420), (730, 1420)], 6, "#f2d7a8", seed=1340, op=.9), w=4.0, seed=1341))
    # окно слева
    wx0, wy0, wx1, wy1 = 110, 450, 380, 860
    s.append(shape(rect_pts(wx0, wy0, wx1, wy1), "#9fcdea", blob(ellipse_pts(310, 540, 36, 36, 14), "#ffd84a") + blob(rect_pts(wx0, 770, wx1, wy1), "#7fae6a")
                   + blob(rect_pts(wx0, 600, wx1, 700), "#d6ecf6", .0), w=5.0, seed=1350))
    s.append(shape(rect_pts((wx0 + wx1) / 2 - 7, wy0, (wx0 + wx1) / 2 + 7, wy1), "#fbf4e6", "", w=3.2, seed=1351))
    s.append(shape(rect_pts(wx0, 640, wx1, 654), "#fbf4e6", "", w=3.2, seed=1352))
    s.append(shape(rect_pts(wx0 - 30, wy1, wx1 + 30, wy1 + 28), "#fbf4e6", "", w=3.6, seed=1353))
    # картина справа
    s.append(blob(rect_pts(838, 478, 1040, 640), "#2a1608", .2, blur(8)))
    s.append(shape(rect_pts(828, 460, 1030, 618), "#fbf9f2", blob([(838, 590), (900, 520), (950, 570), (1000, 510), (1020, 590), (1020, 608), (838, 608)], "#7fae6a")
                   + blob(ellipse_pts(970, 500, 18, 18, 10), "#ffd84a"), w=5.0, seed=1360))
    return "".join(s)


def table():
    s = []
    top = [(500, TOP_Y0, 1), (W + 100, TOP_Y0, 1), (W + 120, TOP_Y1, 1), (480, TOP_Y1, 1)]
    s.append(shape(top, WOOD_L, blob([(500, TOP_Y0), (W + 100, TOP_Y0), (W + 105, TOP_Y0 + 8), (495, TOP_Y0 + 8)], "#e6bd90", .8), w=4.4, seed=1401))
    s.append(shape(rect_pts(480, TOP_Y1, W + 120, TOP_Y1 + 26), WOOD_D, "", w=4.0, seed=1402))
    for k, x in enumerate((540, 1010)):
        s.append(shape(rect_pts(x - 14, TOP_Y1 + 26, x + 14, FLOOR + 40), WOOD, blob(rect_pts(x + 2, TOP_Y1 + 26, x + 14, FLOOR + 40), WOOD_D, .7), w=3.6, seed=1410 + k))
    s.append(blob(ellipse_pts(790, FLOOR + 50, 330, 22, 18), "#3a2a16", .28, blur(8)))
    return "".join(s)


def speaker(t):
    cx, cy = 540, 330
    s = [line([(cx, -200), (cx, cy - 70)], 9, "#6a737a", taper=.05, wmin=.9, seed=1500)]
    s.append(shape(rect_pts(cx - 64, cy - 72, cx + 64, cy + 66, 16), "#4a5460", blob(rect_pts(cx + 20, cy - 72, cx + 64, cy + 66, 16), "#363e48", .8), w=4.6, seed=1501))
    for k, r in enumerate((46, 30, 14)):
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{"#252b33" if k % 2 == 0 else "#7a8590"}" stroke="{INK}" stroke-width="3"/>')
    pulse = 1 + 0.08 * math.sin(t * 22) if T_MAM - 0.1 < t < T_NAP + 0.8 else 1
    s.append(f'<g transform="translate({cx} {cy}) scale({pulse:.3f}) translate({-cx} {-cy})"><circle cx="{cx}" cy="{cy}" r="9" fill="#d8433a" stroke="{INK}" stroke-width="3"/></g>')
    # звуковые волны
    for j in range(3):
        ph = ((t * 2.4) + j / 3) % 1.0
        if not (T_MAM - 0.05 < t < T_NAP + 0.9):
            continue
        r = 100 + 150 * ph
        pts = [(cx + r * math.cos(a), cy + 20 + r * math.sin(a)) for a in [math.radians(40 + 100 * k / 10) for k in range(11)]]
        s.append(line(pts, 7 * (1 - ph) + 1.5, "#e0a64a", taper=.5, wmin=.3, seed=1510 + j))
    return "".join(s)


def reply(t):
    """Облачко-реплика со стаканом розового напитка и двумя кубиками; на «сладкий» значок подпрыгивает."""
    k = pop(t, T_MAM + 0.2, 0.14, 0.2)
    if k <= 0.02:
        return ""
    cx, cy = 560, 560
    bub = props.speech_bubble(cx, cy, 190, 118, (cx - 10, 408), s=k, seed=1600)
    j = max(0.0, math.exp(-(t - T_SLAD) * 9) * math.cos((t - T_SLAD) * 26)) if t >= T_SLAD else 0.0
    jump = -26 * abs(j)
    sc = 1 + 0.18 * (j if j > 0 else 0)
    inner = glass(cx - 48, cy + 62, 0.7, 1.15, 0, PINK, sd=1610)
    inner += sugar_cube(cx + 64, cy + 20, 0.62, 1620, rot=-8)
    inner += sugar_cube(cx + 112, cy + 36, 0.5, 1630, rot=10)
    # искры вокруг на «сладкий»
    sp = ""
    if t >= T_SLAD and t < T_SLAD + 0.5:
        u = (t - T_SLAD) / 0.5
        for i in range(6):
            a = i * math.pi / 3 + 0.3
            sp += line([(cx + math.cos(a) * (95 + 40 * u), cy + 10 + math.sin(a) * (75 + 30 * u)),
                        (cx + math.cos(a) * (125 + 50 * u), cy + 10 + math.sin(a) * (100 + 36 * u))], 5 * (1 - u), "#f2c232", taper=.5, wmin=.3, seed=1640 + i)
    return (bub + f'<g transform="translate({f(cx)} {f(cy + 60)}) scale({sc:.3f}) translate({-cx} {f(-(cy + 60) + jump)})">{inner}</g>' + sp)


def tag(gx, gy, t, k):
    """Бирка на нитке, надетой на стакан: розовая, с кубиком сахара; качается."""
    if k <= 0.02:
        return ""
    ang = 10 * math.sin(t * 5.5) * (1 + 1.2 * math.exp(-max(0, t - T_SLAD) * 6) * (1 if t > T_SLAD else 0)) + 6
    ax, ay = gx + 26, gy - 80
    body = shape([(-34, 10, 1), (34, 10, 1), (34, 98, 1), (-34, 98, 1), (-34, 10, 1)], "#fbf9f2", "", w=3.6, seed=1700)
    body = shape([(-30, 0, 1), (30, 0, 1), (40, 14, 1), (40, 96, 1), (-40, 96, 1), (-40, 14, 1)], "#f9c6d3",
                 blob(ellipse_pts(0, 20, 6, 6, 8), "#fbf9f2") + sugar_cube(0, 66, 0.4, 1710), w=3.6, seed=1700)
    string = line([(0, 0), (0, 6)], 3, INK, seed=1720)
    return (f'<g transform="translate({f(ax)} {f(ay)}) scale({k * .8:.3f}) rotate({f(ang)})">{string}<g transform="translate(0 10)">{body}</g></g>'
            + line([(gx - 26, gy - 80), (gx, gy - 78), (gx + 28, gy - 80)], 4, INK, taper=.2, seed=1730))


def frame09(t):
    s = [_ST["bg"], speaker(t)]
    # мама
    nodq = t - T_SLAD
    nod = 0.0
    if nodq >= 0:
        nod = 8 * math.exp(-nodq * 5) * math.sin(nodq * 24)
    hear = t > T_MAM + 0.1
    looking = (0.7, -0.4) if t < T_VYP - 0.1 else (0.9, 0.2)
    mpose = dict(look=looking, mouth="o" if (hear and t < T_SLAD) else "smile", blink=1.0 if (t % 3.0) < 0.09 else 0.0,
                 head_tilt=3 + 2.5 * math.sin(t * 2.0) + nod, brow=0.35 if t < T_SLAD else 0.0, hmode={"L": "rest", "R": "grip"})
    S = SC_M
    y = FLOOR - 4 + 2 * math.sin(t * 2.4)
    hands = {"R": (MX + 62 * S * 0.5 + 8, y - 548 * S + 2 * math.sin(t * 3)), "L": (MX - 40 * S, y - 235 * S)}
    s.append(with_hands(MOM, MX, y, SC_M, hands, mpose, 8000))
    # ребёнок
    q = t - T_VYP
    lift = 0.0
    if q >= 0:
        lift = ease_io(clamp(q / 0.3)) if q < 0.9 else 1 - ease_io((q - 0.9) / 0.4)
    gx = (KX + 58) + (KX + 22 - (KX + 58)) * lift
    gy = (TOP_Y1 - 6) + (985 - (TOP_Y1 - 6)) * lift
    tilt = -22 * lift
    kp = kid_pose(0, t, calm=True)
    kp.update(dict(look=(-0.6, 0.2), mouth="flat" if lift > .2 else "smile", head_tilt=-2 + 3 * lift))
    kb = 1.6 * math.sin(t * 2.6)
    ky = FLOOR - 4 + kb
    s.append(with_hands(dict(KIDS[0], face=-0.3), KX, ky, SC_K, {"L": (KX - 44, TOP_Y0 - 14), "R": (gx - 4, gy - 40)}, kp, 8500))
    s.append(table())
    s.append(glass(gx, gy, 0.6 - 0.12 * lift, 1.0, tilt, sd=1800))
    s.append(tag(gx, gy, t, pop(t, 14.55, 0.14, 0.25, 0.0) if t > 14.45 else 0.0))
    s.append(reply(t))
    return "".join(s)


def cam09(t):
    u = clamp((t - 14.4) / 3.2)
    k, rot = kick(t, [T_SLAD], 0.035, 12)
    cx = 500 + 60 * ease_io(u)
    sc = 1.32 + 0.14 * ease_io(u)
    return cam(cx, 980, sc * k, rot + 1.2 - 2.0 * u)


def frame(sid, t):
    if not _ST:
        lib.DEFS.clear()
        _ST["bg"] = background()
        lib.static_done()
    lib.dyn_begin()
    return svg(f'<rect width="{W}" height="{H}" fill="{WALL}"/><g transform="{cam09(t)}">{frame09(t)}</g>')


_ = (hand_text, ease_out)
