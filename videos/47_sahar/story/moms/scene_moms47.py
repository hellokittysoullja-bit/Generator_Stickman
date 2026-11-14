"""Сцены moms рилса 47 «сахарная гиперактивность»: s10 (стакан воды, сахар «0», кубики растворяются), s11 (ребёнок тихо
рисует, над мамой облачко-мысль «он носится», молнии только в нём), s12 (мама одёргивает, пузырь значками, ребёнок втянул
голову, хлопок). Люди — person.py (кисти из пяти пальцев), мама сидит у детского столика, ребёнок на высоком табурете.
Время — общее время ролика; удары на словах из voice/words.json."""
import math

import numpy as np

import lib
import person
import props
from c44 import hand_text, kick, pop, shake, wt
from lib import (INK, W, H, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rect_pts, shape, smooth,
                 svg)

_ST = {}
WALL, WALL_ST = "#f3e6cb", "#ecdcba"
FLOOR, FLOOR_L = "#c28a56", "#a9723f"
WOOD, WOOD_SH, WOOD_HI = "#c98a58", "#a8693f", "#dfa673"
PAPER = props.PAPER

T_SAHARA = wt("сахара")          # 17.76
T_KAZALOS = wt("казалось")       # 19.72
T_ACTIVNEE = wt("активнее")      # 20.92
T_CHASHE = wt("чаще")            # 22.12
T_ODERG = wt("одёргивали")       # 22.72


# ───────────────────────── общий фон
def wall_static(window=True):
    s = [f'<rect x="-400" y="-400" width="{W + 800}" height="1700" fill="{WALL}"/>']
    for k in range(-5, 14):
        s.append(f'<rect x="{k * 96}" y="-400" width="44" height="1700" fill="{WALL_ST}"/>')
    # плинтус и пол
    s.append(f'<rect x="-400" y="1180" width="{W + 800}" height="900" fill="{FLOOR}"/>')
    for k in range(0, 16):
        y = 1210 + k * 38
        s.append(f'<rect x="-400" y="{y}" width="{W + 800}" height="4" fill="{FLOOR_L}"/>')
    s.append(shape([(-400, 1150, 1), (1500, 1150, 1), (1500, 1184, 1), (-400, 1184, 1)], "#fbf5e6", "", w=4, seed=11))
    if window:
        X0, Y0, X1, Y1 = 770, 250, 1010, 640
        g = lin_grad([(0, "#8cc6ec", 1), (1, "#dff0f8", 1)], 0, Y0, 0, Y1, units="userSpaceOnUse")
        s.append(f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" fill="url(#{g})"/>')
        s.append(shape(ellipse_pts(900, 380, 34, 34, 14), "#ffd84a", "", w=3.2, seed=12))
        for k, (x, y, r) in enumerate([(820, 330, 22), (960, 480, 26)]):
            pts = [(x + 1.9 * r * (1 + .2 * math.sin(3 * a + k)) * math.cos(a), y + .7 * r * (1 + .2 * math.sin(3 * a + k)) * math.sin(a))
                   for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)]
            s.append(shape(pts, "#ffffff", "", w=2.6, seed=13 + k))
        fr = "#fbf5e6"
        for (a, b, c, d) in [(X0 - 22, Y0 - 22, X1 + 22, Y0 + 2), (X0 - 22, Y1 - 2, X1 + 22, Y1 + 22), (X0 - 22, Y0, X0 + 2, Y1), (X1 - 2, Y0, X1 + 22, Y1),
                             ((X0 + X1) / 2 - 7, Y0, (X0 + X1) / 2 + 7, Y1)]:
            s.append(shape(rect_pts(a, b, c, d), fr, "", w=3.4, seed=int(a + b)))
        s.append(shape([(X0 - 40, Y1 + 20, 1), (X1 + 40, Y1 + 20, 1), (X1 + 40, Y1 + 40, 1), (X0 - 40, Y1 + 40, 1)], "#f6f1e8", "", w=3.4, seed=17))
    return "".join(s)


# ───────────────────────── s10: стакан, сахар «0»
GX, G_TOP, G_BOT = 370, 740, 1150          # центр стакана, верх и дно
G_RIM_W, G_BOT_W = 160, 118                # полуширина сверху и снизу
WATER_Y = 830
TABLE_Y = 1160


def gw(y):
    return G_RIM_W + (G_BOT_W - G_RIM_W) * (y - G_TOP) / (G_BOT - G_TOP)


def cube_pts(a):
    d = a * .34
    front = [(-a / 2, -a / 2, 1), (a / 2, -a / 2, 1), (a / 2, a / 2, 1), (-a / 2, a / 2, 1)]
    top = [(-a / 2, -a / 2, 1), (a / 2, -a / 2, 1), (a / 2 + d, -a / 2 - d * .72, 1), (-a / 2 + d, -a / 2 - d * .72, 1)]
    side = [(a / 2, -a / 2, 1), (a / 2 + d, -a / 2 - d * .72, 1), (a / 2 + d, a / 2 - d * .72, 1), (a / 2, a / 2, 1)]
    return front, top, side


def cube(x, y, a, rot, melt=0.0, wet=0.0, sd=0):
    """Кубик сахара; melt 0..1 — оплавление (углы круглеют, форма «плывёт»); wet — подкраска водой."""
    if a < 3:
        return ""
    w = lambda c: mix(c, "#9fd3ee", wet * .5)   # noqa: E731
    if melt > .45:
        k = (melt - .45) / .55
        pts = ellipse_pts(0, 0, a * (.62 - .12 * k), a * (.5 - .1 * k), 12, jitter=.1, seed=sd + 3)
        pts = lib.T(pts, x, y, 1.0, rot)
        o = shape(pts, w("#fbfaf4"), blob(lib.T(ellipse_pts(a * .12, a * .1, a * .4, a * .3, 8), x, y, 1.0, rot), w("#dcd9cf"), .9),
                  w=max(1.6, 3.4 * (1 - k * .5)), seed=sd + 4)
        return o
    fr, tp, sd_ = cube_pts(a)
    o = shape(lib.T(sd_, x, y, 1.0, rot), w("#cfccc2"), "", w=3.6, seed=sd + 1)
    o += shape(lib.T(fr, x, y, 1.0, rot), w("#fbfaf4"), "", w=3.6, seed=sd + 2)
    o += shape(lib.T(tp, x, y, 1.0, rot), w("#ffffff"), "", w=3.6, seed=sd + 3)
    rs = np.random.RandomState(sd)
    for _ in range(7):
        gx, gy = rs.uniform(-a * .4, a * .4), rs.uniform(-a * .4, a * .4)
        px, py = lib.T([(gx, gy)], x, y, 1.0, rot)[0]
        o += f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(max(1.0, a * .035))}" fill="{w("#bdb9ad")}"/>'
    return o


CUBES = [  # x, время входа в воду, поворот, размер
    (332, 17.40, 12, 66),
    (398, 17.55, -9, 62),
    (366, 17.80, 6, 64),
]
FALL = 0.40
SINK = 0.55
MELT0, MELT = 0.45, 1.05      # пауза на дне до растворения, длительность растворения


def cube_state(i, t):
    x0, te, rot, a = CUBES[i]
    if t < te - FALL:
        return None
    tt = t - (te - FALL)
    if t < te:
        y = WATER_Y - 40 - 0.5 * 3300 * (te - t) ** 2 - 4
        return dict(x=x0 + 6 * math.sin(tt * 9), y=y - a * .4, rot=rot + 160 * (t - te), a=a, phase="air", melt=0, wet=0)
    q = t - te
    floor_y = G_BOT - 40 - a * .5 - i * 10
    u = clamp(q / SINK)
    y = WATER_Y + (floor_y - WATER_Y) * (1 - (1 - u) ** 2.2) - 4
    x = x0 + (18 - 12 * i) * u + 5 * math.sin(q * 6 + i)
    m = clamp((q - SINK - MELT0 + 0.2 * i) / MELT)
    size = a * (1 - ease_io(m)) ** .8
    return dict(x=x, y=y, rot=rot + 30 * u + 40 * m, a=size, phase="water", melt=m, wet=clamp(q / .3), t_in=q)


def glass_group(t):
    s = []
    # задняя кромка и стенки (фон стакана — светлый, без прозрачности)
    body = [(GX - G_RIM_W, G_TOP, 1), (GX + G_RIM_W, G_TOP, 1), (GX + G_BOT_W, G_BOT - 10, 1), (GX + G_BOT_W - 12, G_BOT + 8),
            (GX - G_BOT_W + 12, G_BOT + 8), (GX - G_BOT_W, G_BOT - 10, 1)]
    wob = 3 * math.sin(t * 7) * math.exp(-max(0, t - 17.5) * 1.2)
    s.append(shape(ellipse_pts(GX, G_TOP, G_RIM_W, 26, 20), "#dcecf2", "", w=3.4, seed=101))
    inner = ""
    wl = [(GX - gw(WATER_Y), WATER_Y, 1), (GX + gw(WATER_Y), WATER_Y, 1), (GX + G_BOT_W, G_BOT - 10, 1), (GX + G_BOT_W - 12, G_BOT + 8),
          (GX - G_BOT_W + 12, G_BOT + 8), (GX - G_BOT_W, G_BOT - 10, 1)]
    g = lin_grad([(0, "#8ed0f0", 1), (1, "#5aa7d8", 1)], 0, WATER_Y, 0, G_BOT, units="userSpaceOnUse")
    inner += f'<path d="{lib.fill_d(wl)}" fill="url(#{g})"/>'
    wclip = lib.clip_of(wl)
    s.append(shape(body, "#eef7fa", inner, w=0.01, seed=102, ink=False))
    # кубики в воде (обрезаны водой)
    cubs = ""
    for i in range(3):
        st = cube_state(i, t)
        if st and st["phase"] == "water":
            cubs += cube(st["x"], st["y"], st["a"], st["rot"], st["melt"], st["wet"], sd=40 + i * 7)
            # крошки при растворении
            if st["melt"] > 0.02:
                rs = np.random.RandomState(7 + i)
                for k in range(11):
                    ang = rs.uniform(0, 2 * math.pi)
                    life = clamp((st["melt"] - 0.05 * k / 3) * 1.25)
                    if 0 < life < 1:
                        r = st["a"] * .4 + 70 * life * rs.uniform(.5, 1)
                        px = st["x"] + r * math.cos(ang)
                        py = st["y"] + r * math.sin(ang) * .6 - 55 * life
                        rr = 6 * (1 - life) + 2
                        cubs += f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(rr)}" fill="#f4fbff"/>'
    s.append(f'<g clip-path="url(#{wclip})">{cubs}</g>')
    # поверхность воды
    surf = ellipse_pts(GX, WATER_Y, gw(WATER_Y), 22, 20)
    s.append(shape(surf, "#aee0f7", "", w=3.0, seed=103))
    # круги от падения кубиков
    for i in range(3):
        te = CUBES[i][1]
        q = t - te
        if 0 < q < .9:
            u = q / .9
            rx, ry = 34 + 90 * ease_out(u), 7 + 14 * ease_out(u)
            cx = CUBES[i][0]
            s.append(f'<ellipse cx="{f(cx)}" cy="{f(WATER_Y + 2)}" rx="{f(rx)}" ry="{f(ry)}" fill="none" stroke="#ffffff" '
                     f'stroke-width="{f(5 * (1 - u) + 1)}" opacity="{f(1 - u)}"/>')
            # брызги — капли по дугам
            for k in range(7):
                ang = math.radians(-160 + 24 * k)
                v = 330 + 40 * ((k * 5) % 3)
                px = cx + v * math.cos(ang) * q * .5
                py = WATER_Y - 6 - v * math.sin(-ang) * q + 0.5 * 1500 * q * q
                if py < WATER_Y + 4 and q < .55:
                    s.append(shape(ellipse_pts(px, py, 8 * (1 - q), 10 * (1 - q), 8), "#bfe6fa", "", w=2.2, seed=300 + k + i * 9))
    # кубики в воздухе (поверх всего, обрезаются линией воды при входе)
    air = ""
    for i in range(3):
        st = cube_state(i, t)
        if st and st["phase"] == "air":
            air += cube(st["x"], st["y"], st["a"], st["rot"], 0, 0, sd=40 + i * 7)
    s.append(air)
    # передняя кромка, стенки, блики
    s.append(line([(GX - G_RIM_W, G_TOP), (GX - G_BOT_W, G_BOT - 10)], 6, INK, taper=.1, wmin=.8, seed=110))
    s.append(line([(GX + G_RIM_W, G_TOP), (GX + G_BOT_W, G_BOT - 10)], 6, INK, taper=.1, wmin=.8, seed=111))
    s.append(line([(GX - G_BOT_W, G_BOT - 10), (GX - G_BOT_W + 12, G_BOT + 8), (GX, G_BOT + 14), (GX + G_BOT_W - 12, G_BOT + 8), (GX + G_BOT_W, G_BOT - 10)],
                  6, INK, taper=.1, wmin=.8, seed=112))
    s.append(line([(GX - G_RIM_W + 4, G_TOP + 10), (GX - G_RIM_W + 10, G_TOP + 22), (GX, G_TOP + 28), (GX + G_RIM_W - 10, G_TOP + 22),
                   (GX + G_RIM_W - 4, G_TOP + 10)], 4, INK, taper=.15, wmin=.7, seed=113))
    s.append(blob([(GX - G_RIM_W + 10, G_TOP + 70), (GX - G_RIM_W + 22, G_TOP + 70), (GX - G_BOT_W + 24, G_TOP + 230), (GX - G_BOT_W + 14, G_TOP + 230)],
                  "#ffffff"))
    s.append(blob([(GX + G_RIM_W - 22, G_TOP + 90), (GX + G_RIM_W - 14, G_TOP + 90), (GX + G_BOT_W - 18, G_TOP + 200), (GX + G_BOT_W - 26, G_TOP + 200)],
                  "#ffffff"))
    return f'<g transform="translate(0 {f(wob)})">{"".join(s)}</g>'


def sign_pose(t):
    """Табличка падает сверху на стол с отскоком; возвращает (смещение по y, поворот, сжатие)."""
    te = 17.52
    if t < te:
        q = te - t
        return -(0.5 * 2600 * q * q), -6 * q * 2, 1.0
    q = t - te
    bounce = -26 * abs(math.sin(q * 11)) * math.exp(-q * 5.5)
    sq = 1 - 0.06 * math.exp(-q * 12) * math.cos(q * 20)
    return bounce, 3 * math.exp(-q * 4) * math.sin(q * 16), sq


SX0, SX1, SY0 = 640, 900, 790


def sign_group(t):
    dy, rot, sq = sign_pose(t)
    w, h = SX1 - SX0, TABLE_Y - SY0 - 8
    cx, by = (SX0 + SX1) / 2, TABLE_Y - 8
    s = []
    # подпорки
    s.append(shape([(SX0 + 40, by - 10, 1), (SX0 + 70, by - 10, 1), (SX0 + 56, by + 22, 1), (SX0 + 24, by + 22, 1)], WOOD_SH, "", w=3.6, seed=201))
    s.append(shape([(SX1 - 70, by - 10, 1), (SX1 - 40, by - 10, 1), (SX1 - 24, by + 22, 1), (SX1 - 56, by + 22, 1)], WOOD_SH, "", w=3.6, seed=202))
    card = rect_pts(SX0, SY0, SX1, by, 14)
    inner = blob(rect_pts(SX0 + 18, SY0 + 18, SX1 - 4, by - 4, 8), "#efe4cc") if False else ""
    s.append(shape(card, "#fffdf4", inner, w=5.4, seed=203))
    s.append(shape(rect_pts(SX0 + 14, SY0 + 14, SX1 - 14, by - 14, 8), "none", "", w=3.4, seed=204, ink_color="#d8433a"))
    # значок кубика с перечёркивающей чертой — «сахар»
    s.append(cube(cx - 8, SY0 + 62, 50, 8, 0, 0, sd=900))
    s.append(hand_text(cx, SY0 + 145, "сахар", 70, INK, weight=700, rot=-2))
    # «0» ставится на слове «сахара»
    k = pop(t, T_SAHARA - 0.02, dur=0.09, over=.35, k0=0.0)
    if t >= T_SAHARA - 0.02:
        z = max(k, 0.0)
        s.append(f'<g transform="translate({f(cx)} {f(by - 52)}) scale({f(z)}) rotate({f(-4 + 4 * smooth(T_SAHARA, T_SAHARA + .25, t))})">'
                 + hand_text(0, 0, "0", 190, "#d8433a", stroke="#fffdf4", sw=12, weight=700) + "</g>")
        q = (t - T_SAHARA) / 0.5
        s.append(props.burst(cx, by - 110, 1.2, q, seed=910, color="#d8433a", n=8, r0=120, r1=170))
    else:
        s.append(hand_text(cx, by - 52, "?", 170, "#c9b9a0", weight=700, rot=-4))
    # блик на карточке
    return (f'<g transform="translate({f(cx)} {f(by)}) rotate({f(rot)}) scale(1 {f(sq)}) translate({f(-cx)} {f(-by)}) translate(0 {f(dy)})">'
            + "".join(s) + "</g>")


def table_s10():
    s = []
    g = lin_grad([(0, "#d9985f", 1), (1, "#c98a58", 1)], 0, TABLE_Y, 0, 1300, units="userSpaceOnUse")
    s.append(f'<rect x="-400" y="{TABLE_Y}" width="{W + 800}" height="700" fill="url(#{g})"/>')
    for k in range(6):
        y = TABLE_Y + 40 + k * 46
        s.append(f'<rect x="-400" y="{y}" width="{W + 800}" height="3" fill="{WOOD_SH}" opacity=".5"/>')
    s.append(f'<rect x="-400" y="{TABLE_Y - 4}" width="{W + 800}" height="9" fill="{INK}"/>')
    s.append(f'<rect x="-400" y="{TABLE_Y + 5}" width="{W + 800}" height="12" fill="{WOOD_HI}"/>')
    return "".join(s)


def sugar_bowl():
    """Сахарница слева у края кадра: оттуда «пришли» кубики."""
    x, y = 120, TABLE_Y - 4
    s = []
    body = [(x - 70, y - 90, 1), (x + 70, y - 90, 1), (x + 60, y - 10), (x + 30, y, 1), (x - 30, y, 1), (x - 60, y - 10)]
    s.append(shape(body, "#f8f3e6", blob([(x + 20, y - 90), (x + 70, y - 90), (x + 60, y - 10), (x + 30, y)], "#e3dccb", .9), w=4.6, seed=501))
    s.append(shape(rect_pts(x - 80, y - 110, x + 80, y - 86, 8), "#f8f3e6", "", w=4.4, seed=502))
    for k, (cxx, cyy, a, r) in enumerate([(-30, -128, 36, 8), (14, -134, 38, -6), (-4, -160, 34, 14)]):
        s.append(cube(x + cxx, y + cyy, a, r, sd=600 + k))
    return "".join(s)


def shadow_s10():
    return f'<ellipse cx="{GX + 12}" cy="{TABLE_Y + 22}" rx="{G_BOT_W + 60}" ry="22" fill="#8e5a36" opacity=".45" {blur(9)}/>'


def frame10(t):
    if "w10" not in _ST:
        _ST["w10"] = wall_static()
        lib.static_done()
    lib.dyn_begin()
    body = _ST["w10"] + table_s10() + sugar_bowl() + shadow_s10() + glass_group(t) + sign_group(t)
    return body


def cam10(t):
    u = clamp((t - 17.2) / 2.1)
    k, rot = kick(t, [T_SAHARA], 0.035, 11)
    sc = 1.12 + 0.18 * ease_io(u)
    sx, sy = shake(t, T_SAHARA, 5, 9)
    return cam(540 + 10 * u + sx, 950 + 4 * u + sy, sc * k, -1.2 + 1.6 * u + rot)


# ───────────────────────── люди за столиком (s11, s12)
MOM = dict(skin="#efc3a2", hair="bun", hair_c="#5a3322", top="#c9524a", low="#34425e", shoes="#3a2a22", face=.72, h=1.0, brow_c="#3a2218",
           sleeve="#c9524a", collar="#f6ecd8")
KID = dict(skin="#f3c9a8", hair="short", hair_c="#d09a3c", top="#4aa3c4", low="#3d4b86", shoes="#c9524a", face=-.72, h=1.0, hw=1.22, bw=.9,
           stripes="#f2f2e6", brow_c="#8a5a1c")
MOM_S, KID_S = 0.95, 0.72
MOM_FEET, MOM_FLOOR = 433, 1268
KID_FEET, KID_FLOOR = 729, 1204


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


def seat_person(spec, feet_x, floor_y, sc, hands, pose, sd=0):
    pose = dict(pose)
    dr = 1 if spec["face"] >= 0 else -1
    S = sc * spec.get("h", 1.0)
    a1 = 90
    pose["legs"] = {"L": (a1, a1), "R": (a1, a1)}
    ox = feet_x - dr * 140 * S
    oy = floor_y + 138 * S
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
    return person.draw(spec, pose, ox, oy, sc, sd=sd), (ox, oy)


def chair_mom():
    s = []
    s.append(shape([(188, 880, 1), (214, 880, 1), (222, 1150, 1), (190, 1150, 1)], WOOD_SH, "", w=4.2, seed=701))
    s.append(shape([(176, 900, 1), (230, 896, 1), (232, 930, 1), (176, 934, 1)], WOOD_SH, "", w=3.6, seed=702))
    s.append(shape([(190, 1136, 1), (470, 1136, 1), (470, 1160, 1), (190, 1160, 1)], WOOD, "", w=4.2, seed=703))
    for x in (200, 450):
        s.append(shape([(x, 1160, 1), (x + 22, 1160, 1), (x + 22, 1268, 1), (x, 1268, 1)], WOOD_SH, "", w=4, seed=704 + x))
    return "".join(s)


def stool_kid():
    s = []
    for x in (770, 874):
        s.append(shape([(x, 1124, 1), (x + 20, 1124, 1), (x + 24, 1268, 1), (x - 2, 1268, 1)], WOOD_SH, "", w=4, seed=720 + x))
    s.append(shape([(776, 1212, 1), (884, 1212, 1), (884, 1224, 1), (776, 1224, 1)], WOOD_SH, "", w=3.2, seed=730))
    s.append(shape([(738, 1102, 1), (918, 1102, 1), (918, 1126, 1), (738, 1126, 1)], WOOD, "", w=4.2, seed=731))
    s.append(shape(rect_pts(742, 1084, 914, 1104, 8), "#e8825a", "", w=3.6, seed=732))        # подушка
    return "".join(s)


TT = [(380, 960), (790, 960), (810, 1030), (360, 1030)]


def table_legs():
    s = []
    for x in (388, 768):
        s.append(shape([(x, 1062, 1), (x + 24, 1062, 1), (x + 24, 1268, 1), (x, 1268, 1)], WOOD_SH, "", w=4.2, seed=740 + x))
    return "".join(s)


def table_top():
    s = []
    s.append(shape([(TT[0][0], TT[0][1], 1), (TT[1][0], TT[1][1], 1), (TT[2][0], TT[2][1], 1), (TT[3][0], TT[3][1], 1)], WOOD_HI, "", w=4.4, seed=750))
    s.append(shape([(360, 1030, 1), (810, 1030, 1), (810, 1062, 1), (360, 1062, 1)], WOOD, "", w=4.4, seed=751))
    return "".join(s)


# лист бумаги: углы (u, v) → мир
PQ = [(552, 972), (738, 972), (752, 1022), (540, 1022)]


def pmap(u, v):
    x0 = PQ[0][0] + (PQ[3][0] - PQ[0][0]) * v
    x1 = PQ[1][0] + (PQ[2][0] - PQ[1][0]) * v
    y = PQ[0][1] + (PQ[3][1] - PQ[0][1]) * v
    return x0 + (x1 - x0) * u, y


def scribble():
    """Рисунок ребёнка: солнце, трава, домик — одной непрерывной траекторией (u, v, цвет)."""
    pts = []
    for k in range(40):                                  # солнце по спирали
        a = k / 39 * 2 * math.pi * 1.4
        r = .13 + .02 * k / 39
        pts.append((.30 + r * .75 * math.cos(a), .40 + r * math.sin(a), "#e8a812"))
    for k in range(8):                                   # лучи
        a = k / 8 * 2 * math.pi
        pts.append((.30 + .24 * .75 * math.cos(a), .40 + .24 * math.sin(a), "#e8a812"))
        pts.append((.30 + .34 * .75 * math.cos(a), .40 + .34 * math.sin(a), "#e8a812"))
    for k in range(24):                                  # трава
        pts.append((.08 + k * .036, .86 + .06 * (-1) ** k, "#3e9a4a"))
    for (u, v) in [(.62, .78), (.62, .50), (.78, .36), (.92, .50), (.92, .78), (.62, .78)]:   # домик
        pts.append((u, v, "#d8433a"))
    for k in range(18):
        a = k / 17 * 2 * math.pi
        pts.append((.78 + .05 * math.cos(a), .62 + .08 * math.sin(a), "#2f6fb8"))
    return pts


SCR = scribble()
SCR_T0, SCR_RATE = 18.0, 15.0           # с какого момента и сколько точек в секунду


def scr_index(t):
    return clamp((t - SCR_T0) * SCR_RATE, 0, len(SCR) - 1)


def paper_group(t, jump=0.0):
    s = []
    s.append(shape([(PQ[0][0], PQ[0][1], 1), (PQ[1][0], PQ[1][1], 1), (PQ[2][0], PQ[2][1], 1), (PQ[3][0], PQ[3][1], 1)], "#fffdf4", "", w=3.2, seed=760))
    idx = scr_index(t)
    n = int(idx)
    # непрерывные куски одного цвета
    start = 0
    for k in range(1, n + 2):
        if k > n + 1 or k >= len(SCR) or SCR[k][2] != SCR[start][2] or k == n + 1:
            end = min(k, n + 1)
            seg = SCR[start:end]
            if k == n + 1 and n + 1 < len(SCR):
                a, b = SCR[n], SCR[min(n + 1, len(SCR) - 1)]
                fr = idx - n
                seg = seg + [(a[0] + (b[0] - a[0]) * fr, a[1] + (b[1] - a[1]) * fr, a[2])]
            if len(seg) >= 2:
                s.append(line([pmap(u, v) for u, v, _ in seg], 4.2, seg[0][2], taper=0.05, wmin=.9, seed=770 + start))
            start = k
            if k >= n + 1:
                break
    return f'<g transform="translate(0 {f(-jump)})">{"".join(s)}</g>'


def tip_pos(t):
    i = scr_index(t)
    n = int(i)
    a = SCR[n]
    b = SCR[min(n + 1, len(SCR) - 1)]
    fr = i - n
    return pmap(a[0] + (b[0] - a[0]) * fr, a[1] + (b[1] - a[1]) * fr)


def glass_small(x, y, t, jump=0.0):
    y -= jump
    pts = [(x - 36, y - 80, 1), (x + 36, y - 80, 1), (x + 28, y, 1), (x - 28, y, 1)]
    wl = [(x - 34, y - 56, 1), (x + 34, y - 56, 1), (x + 28, y, 1), (x - 28, y, 1)]
    inner = blob(wl, "#79c0e8")
    return (shape(pts, "#e6f3f7", inner, w=3.8, seed=780) + shape(ellipse_pts(x, y - 56, 34, 6, 12), "#aee0f7", "", w=2.4, seed=781)
            + blob([(x - 26, y - 72), (x - 20, y - 72), (x - 18, y - 12), (x - 23, y - 12)], "#ffffff"))


# ───────────────────────── молния
BOLT = [(10, -64, 1), (-22, 6, 1), (-3, 6, 1), (-16, 66, 1), (24, -10, 1), (4, -10, 1), (22, -64, 1)]


def bolt(x, y, k, rot=0.0, sd=0):
    return shape(lib.T(BOLT, x, y, k, rot), "#ffd23a", "", w=4 * max(.6, k * 1.3), seed=sd)


# ───────────────────────── s11
def mom_pose_hands(t, extra=None):
    return {"L": (470, 988), "R": (528 + 4 * math.sin(t * 2.2), 992)}


def draw_people(t, mom_pose, mom_hands, kid_pose, kid_hands, kid_tip=None):
    body_m, _ = seat_person(MOM, MOM_FEET, MOM_FLOOR, MOM_S, mom_hands, mom_pose, sd=3000)
    body_k, _ = seat_person(KID, KID_FEET, KID_FLOOR, KID_S, kid_hands, kid_pose, sd=4000)
    return body_m, body_k


def kid_drawing(t, calm_until=1e9):
    """Ребёнок рисует: рука с карандашом ведёт по листу, голова склонена, моргает."""
    tip = tip_pos(min(t, calm_until))
    hand_t = (tip[0] + 30, tip[1] - 42)
    hands = {"L": hand_t, "R": (700, 1004)}
    pose = dict(look=(-0.55, 0.9), mouth="smile" if (t % 4.0) > 2.6 else "flat", blink=1.0 if (t % 3.1) < 0.09 else 0.0,
                head_tilt=-8 + 2 * math.sin(t * 1.5), brow=-.1, hmode={"L": "grip", "R": "rest"}, head_dy=6 + 2 * math.sin(t * 3))
    return pose, hands, tip, hand_t


def crayon(tip, hand_t):
    x0, y0 = hand_t
    return line([(x0 + 4, y0 + 2), (tip[0], tip[1])], 8, "#d8433a", taper=.05, wmin=.9, seed=790) + \
        f'<circle cx="{f(tip[0])}" cy="{f(tip[1])}" r="2.6" fill="#d8433a"/>'


def cloud_content(t, cx, cy, rx, ry, intensity):
    """Внутри облачка: бегущий мини-ребёнок, линии скорости, молнии и «он носится!»."""
    o = []
    o.append(f'<rect x="{cx - rx * 2:.1f}" y="{cy - ry * 2:.1f}" width="{rx * 4:.1f}" height="{ry * 4:.1f}" fill="#efe7d4"/>')
    o.append(blob(ellipse_pts(cx - rx * .06, cy - ry * .12, rx * 1.0, ry * .95, 24), PAPER))
    sp = 4.6 + 3.2 * intensity
    px = cx + (rx * .52) * math.sin(t * sp)
    dirn = 1 if math.cos(t * sp) >= 0 else -1
    py = cy + ry * .30 - 16 * abs(math.sin(t * sp * 2.1))
    # линии скорости позади
    for k in range(4):
        yy = py - 150 + k * 44
        xx = px - dirn * (90 + 14 * k)
        o.append(line([(xx, yy), (xx - dirn * (60 + 20 * ((k * 3) % 3)), yy + 2)], 5, "#9a8f7a", taper=.6, wmin=.3, seed=800 + k))
    # молнии вокруг бегущего
    nb = 2 + int(4 * intensity)
    for k in range(nb):
        ph = t * (6 + k) + k * 1.7
        if math.sin(ph) > -0.3:
            bx = cx + (k - (nb - 1) / 2) * rx * .55 / max(1, nb / 3) + 14 * math.sin(ph * 2)
            by = cy - ry * .18 + (k % 2) * ry * .32 + 8 * math.cos(ph)
            o.append(bolt(bx, by, .62 + .22 * ((k + 1) % 2), rot=(k - 2) * 9 + 8 * math.sin(ph), sd=810 + k))
    lib.INK_K[0] = 2.7
    spec = dict(KID, face=.8 * dirn, hw=1.1)
    ph = t * (sp * 3.2)
    o.append(person.draw(spec, dict(walk=ph, look=(.4 * dirn, 0), mouth="o", brow=.5), px, py + 36, 0.255, sd=5000))
    lib.INK_K[0] = 1.0
    o.append(hand_text(cx, cy + ry * .78, "он носится!", 58, "#d8433a", weight=700, rot=-2 + 2 * math.sin(t * 6)))
    return "".join(o)


def thought(t, cx, cy, rx, ry, src, tp0, extra_k=1.0, intensity=0.0, rot=0.0):
    """Облачко-мысль: появляется (кружки-след, потом облако) с перелётом, пульсирует на толчках."""
    e = t - tp0
    if e < 0:
        return ""
    o = []
    dx, dy = src[0] - cx, src[1] - cy
    for j, (u, r) in enumerate([(.9, 14), (.78, 22), (.66, 32)]):
        if e < .05 + .06 * (2 - j):
            continue
        x, y = cx + dx * u, cy + dy * u
        o.append(shape(ellipse_pts(x, y, r, r * .86, 12), PAPER, "", w=4.0, seed=830 + j))
    k = pop(t, tp0 + .16, dur=.14, over=.16, k0=0.0) * extra_k
    if k > 0.03:
        pts = props.cloud_pts(cx, cy, rx, ry, 9, k, phase=.3 + .03 * math.sin(t * 2))
        inner = cloud_content(t, cx, cy, rx * k, ry * k, intensity) if k > .5 else ""
        o.append(f'<g transform="rotate({f(rot)} {f(cx)} {f(cy)})">' + shape(pts, PAPER, inner, w=5.0, seed=840) + "</g>")
    return "".join(o)


def frame11(t):
    if "w11" not in _ST:
        _ST["w11"] = wall_static()
        _ST["tbl"] = chair_mom() + stool_kid() + table_legs() + table_top()
        lib.static_done()
    lib.dyn_begin()
    kp, kh, tip, hand_t = kid_drawing(t)
    hl = (470 + 3 * math.sin(t * 1.4), 990)
    # мама: смотрит на ребёнка, брови вверх, на «казалось» и «активнее» — вздрагивает
    surprised = smooth(19.4, 19.8, t)
    mp = dict(look=(.9, .25), mouth="o" if t > T_KAZALOS - .05 else "flat", blink=1.0 if (t % 3.3) < 0.09 else 0.0,
              head_tilt=2 + 3 * smooth(T_ACTIVNEE - .1, T_ACTIVNEE + .3, t), brow=.15 + .6 * surprised, hmode={"L": "rest", "R": "rest"})
    mh = {"L": hl, "R": (528 + 3 * math.sin(t * 2.2), 992)}
    bm, bk = draw_people(t, mp, mh, kp, kh)
    s = [_ST["w11"], _ST["tbl"], glass_small(480, 960, t), paper_group(t), bm, bk, crayon(tip, hand_t)]
    # облачко над мамой
    k1, _ = kick(t, [T_KAZALOS, T_ACTIVNEE], 0.05, 9)
    inten = clamp((t - 18.95) * .4) * .4 + .6 * smooth(T_ACTIVNEE - .2, T_ACTIVNEE + .5, t)
    s.append(f'<g transform="translate(470 420) scale({k1:.4f}) translate(-470 -420)">'
             + thought(t, 470, 420, 285, 200, (352, 745), 18.92, 1.0, inten, rot=-1.5 * math.sin(t * 2.4)) + "</g>")
    return "".join(s)


def cam11(t):
    u = clamp((t - 18.9) / 2.9)
    k, rot = kick(t, [T_KAZALOS, T_ACTIVNEE], 0.012, 12)
    return cam(510 + 60 * u, 800 + 10 * u, (1.30 + .08 * ease_io(u)) * k, -.8 + 1.6 * u + rot)


# ───────────────────────── s12
SLAM0 = T_ODERG - 0.02


def mute_icon(x, y, k, t):
    """Значок «тихо»: динамик с перечёркнутыми волнами и красная косая черта."""
    s = []
    sp = [(-48, -20, 1), (-18, -20, 1), (22, -52, 1), (22, 52, 1), (-18, 20, 1), (-48, 20, 1)]
    s.append(shape(lib.T(sp, x, y, k), "#4a5a70", "", w=5, seed=870))
    for j, r in enumerate((30, 56)):
        pts = [(x + k * (36 + 10 * j + 14 * math.cos(math.pi * (i / 8 - .5))), y + k * (-(26 + 18 * j) + 2 * (26 + 18 * j) * i / 8)) for i in range(9)]
        s.append(line(pts, 6, "#4a5a70", taper=.2, wmin=.5, seed=880 + j))
    s.append(line([(x - 70 * k, y - 66 * k), (x + 78 * k, y + 70 * k)], 11, "#d8433a", taper=.05, wmin=.8, seed=890))
    return "".join(s)


def hlop_star(x, y, u, sd=0):
    """Звезда-«хлопок» (без букв) и лучи: u 0..1."""
    if u <= 0 or u >= 1:
        return ""
    r0, r1 = 26 + 70 * ease_out(u, 2), 48 + 110 * ease_out(u, 2)
    pts = []
    n = 12
    for i in range(2 * n):
        a = math.pi * i / n + .2
        r = r1 if i % 2 == 0 else r0
        pts.append((x + r * math.cos(a), y + r * math.sin(a) * .75, 1))
    sc = 1 - clamp((u - .6) / .4)
    pts = [((p[0] - x) * sc + x, (p[1] - y) * sc + y, 1) for p in pts]
    return shape(pts, "#ffd23a", blob([(x - 30 * sc, y - 20), (x + 30 * sc, y - 20), (x, y + 24 * sc)], "#fff4b0", .9), w=5, seed=sd)


def frame12(t):
    if "w12" not in _ST:
        _ST["w12"] = wall_static()
        _ST["tbl"] = chair_mom() + stool_kid() + table_legs() + table_top()
        lib.static_done()
    lib.dyn_begin()
    # рука мамы: замах от стола вверх, дрожит наверху, удар по столу на «одёргивали»
    up = (500, 676)
    dn = (540, 1000)
    a = ease_io(clamp((t - 21.4) / .55))
    hx = 528 + (up[0] - 528) * a
    hy = 992 + (up[1] - 992) * a
    if t > 21.95 and t < SLAM0:
        hx += 5 * math.sin(t * 38)
        hy += 4 * math.sin(t * 31)
        wind = smooth(SLAM0 - .3, SLAM0, t)
        hy -= 26 * wind                      # подъём перед ударом
    if t >= SLAM0:
        q = (t - SLAM0)
        d = clamp(q / .07)
        hx, hy = up[0] + (dn[0] - up[0]) * d, (up[1] - 26) + (dn[1] - up[1] + 26) * d ** 1.6 + 8 * math.exp(-q * 12) * math.sin(q * 40) * (1 if q > .07 else 0)
    slam = max(0.0, t - SLAM0)
    jump = 0.0 if t < SLAM0 + .07 else 9 * math.exp(-(t - SLAM0 - .07) * 12) * abs(math.cos((t - SLAM0 - .07) * 30))
    # мама строгая
    mp = dict(look=(.9, .1), mouth="o" if t > 21.9 else "flat", blink=0.0, head_tilt=3 + 4 * smooth(21.7, 22.2, t), brow=-.6 if t > 21.7 else .3,
              hmode={"L": "rest", "R": "open"}, hang={"R": -20 if t < SLAM0 else 0})
    mh = {"L": (470, 990), "R": (hx, hy)}
    # ребёнок: до удара рисует, после — втянул голову, замер
    scared = smooth(SLAM0 - .02, SLAM0 + .12, t)
    kp, kh, tip, hand_t = kid_drawing(t, calm_until=SLAM0 - .02)
    if scared > 0:
        kp = dict(kp, head_dy=6 + 34 * scared + 2 * math.sin(t * 40) * scared * math.exp(-slam * 3), head_tilt=-8 + 14 * scared, mouth="wavy",
                  look=(.9, .6), brow=.9 * scared + (-.1) * (1 - scared), blink=1.0 if scared > .5 and slam < .55 else kp["blink"])
        kh = {"L": (hand_t[0] - 10 * scared, hand_t[1] + 8 * scared), "R": (700 - 40 * scared, 1004 - 8 * scared)}
    bm, bk = draw_people(t, mp, mh, kp, kh)
    s = [_ST["w12"], _ST["tbl"], glass_small(480, 960, t, jump), paper_group(t, jump * .8), bm, bk, crayon(tip, hand_t)]
    # пузырь «тихо» значками
    bt = 21.78
    if t >= bt:
        kb = pop(t, bt, dur=.14, over=.2) * (1 + 0.12 * math.exp(-slam * 9) * math.cos(slam * 30) if t >= SLAM0 else 1)
        bx, by = 560, 470
        wob = 2.5 * math.sin(t * 8) if t < SLAM0 else 0
        s.append(f'<g transform="translate({f(bx)} {f(by)}) rotate({f(wob)}) scale({f(kb)}) translate({f(-bx)} {f(-by)})">'
                 + props.speech_bubble(bx, by, 230, 150, (402, 742), 1.0, 920)
                 + mute_icon(bx - 62, by + 6, 1.3, t)
                 + hand_text(bx + 130, by + 50, "!!", 150, "#d8433a", weight=700, rot=6) + "</g>")
    # хлопок
    if t >= SLAM0 + .06:
        q = (t - SLAM0 - .06) / .5
        s.append(hlop_star(560, 985, q, sd=930))
        s.append(props.burst(560, 990, 1.0, clamp((t - SLAM0 - .06) / .4), seed=940, n=9, r0=110, r1=170))
    return "".join(s)


def cam12(t):
    k, rot = kick(t, [SLAM0 + .06], 0.045, 13)
    sx, sy = shake(t, SLAM0 + .06, 12, 8)
    drift = (t - 21.4) * 4
    return cam(530 + sx + drift * .3, 830 + sy, 1.32 * k + 0.004 * (t - 21.4), rot - .5)


def frame(sid, t):
    if sid == "s10":
        return svg(f'<rect width="{W}" height="{H}" fill="{WALL}"/><g transform="{cam10(t)}">{frame10(t)}</g>')
    if sid == "s11":
        return svg(f'<rect width="{W}" height="{H}" fill="{WALL}"/><g transform="{cam11(t)}">{frame11(t)}</g>')
    return svg(f'<rect width="{W}" height="{H}" fill="{WALL}"/><g transform="{cam12(t)}">{frame12(t)}</g>')


_ = (ease_out, smooth, blob)
