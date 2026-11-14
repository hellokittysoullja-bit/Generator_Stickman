"""Сцена dream рилса 44 (s02, 1.44–3.75): внутри облака мечты (рамка-облако с пушистым белым краем и голубой тенью на
тёмно-синем вечернем фоне со звёздами) — Фудзи со снежной шапкой, солнце, сакура, красные тории, тропинка. Маленький
Дима (тот же герой, что в 40–41: лохматый, щетина, горчичное худи; рюкзак и фотоаппарат на шее) идёт по тропинке и
сияет; лепестки летят; на «Японию» (2.8) он подпрыгивает от счастья, вспыхивают блёстки, потом машет руками.
Камера: панорама вдоль тропинки за Димой и лёгкий наезд. Всё — функция общего времени ролика t."""
import math

import numpy as np

import dima40 as dima
import japan
import lib
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad,
                 shape, smooth, svg)

_ST = {}
JUMP = 2.80            # «Японию»
T_UP = 2.78            # отрыв
T_DOWN = 3.18          # приземление
GY = 1150.0            # земля тропинки под Димой (мир)
DK = 0.74              # масштаб Димы (его мир → наш)
CL = (540, 700, 520, 560)   # облако-рамка: центр, полуоси
BS = dima.BS
LEG = (dima.THIGH + dima.SHIN) * BS
AHW = dima.AH * BS

# походка (в единицах мира Димы): шаг 0.34 с, длина 130
TS, SL = 0.34, 130.0
V = SL / TS
X0 = 250.0 / DK        # таз Димы при t=1.24 (его мир)
T_STOP = 2.60          # перестаёт идти, готовится к прыжку


def hip_x(t):
    tt = min(t, T_STOP)
    x = X0 + V * (tt - 1.24)
    if t > T_STOP:
        x += V * 0.35 * (1 - math.exp(-(t - T_STOP) / 0.12)) * 0.12 / 1.0
    return x


def foot(side, t):
    """Лодыжка ноги side на походке: опора 60 % цикла стоит на месте, перенос — дуга."""
    T = 2 * TS
    off = 0.0 if side == "n" else TS
    k = math.floor((t - 1.24 - off) / T)
    c0 = 1.24 + off + k * T                  # касание текущего цикла
    st = 0.62 * T
    def plant(c):
        return hip_x(c + st * 0.5) + 6
    if t - c0 < st:
        return np.array([plant(c0), -AHW]), 0.0
    u = (t - c0 - st) / (T - st)
    a, b = plant(c0), plant(c0 + T)
    ux = (1 - math.cos(math.pi * u)) / 2
    y = -AHW - 60 * math.sin(math.pi * u) ** 1.2
    phi = 0.35 * math.sin(math.pi * clamp(u * 1.3)) - 0.15 * smooth(.7, 1, u)
    return np.array([a + (b - a) * ux, y]), phi


def walk_k(t):
    return 1 - smooth(T_STOP - 0.05, T_STOP + 0.06, t)


def pose(t):
    """Поза Димы (мир Димы, земля y=0)."""
    hx = hip_x(t)
    stand_y = -(LEG * 0.9 + AHW)
    wk = walk_k(t)
    T = 2 * TS
    psi = 2 * math.pi * (t - 1.24) / T
    bob = 8 * math.cos(2 * psi) * wk
    hy = stand_y + bob
    lean = 0.10 * wk
    feet = {}
    for s in ("n", "f"):
        feet[s] = foot(s, min(t, T_STOP))
    # стойка: ступни расходятся под тазом
    fs = {"n": hx + 34, "f": hx - 30}
    for s in ("n", "f"):
        if wk < 1:
            A0, p0 = feet[s]
            A1 = np.array([fs[s], -AHW])
            feet[s] = (A0 + (A1 - A0) * (1 - wk), p0 * wk)
    arms = {}
    hands = {"n": "fist", "f": "fist"}
    for s_, sg in (("n", 1), ("f", -1)):
        sw = -sg * math.cos(psi)
        arms[s_] = ("ang", 0.05 + 0.5 * sw * wk, 0.55 + 0.3 * max(0, sw))
    hood, hair = 0.0, 0.0
    vy = 0.0
    # подготовка, прыжок, приземление, радость
    if t > T_STOP:
        crouch = smooth(T_STOP, T_UP, t) * (1 - smooth(T_UP, T_UP + 0.05, t))
        hy += 70 * crouch
        lean += 0.22 * crouch
        for s_ in ("n", "f"):
            k = smooth(T_STOP, T_UP, t)
            arms[s_] = ("ang", arms[s_][1] * (1 - k) - 0.7 * k, arms[s_][2] * (1 - k) + 0.3 * k)
    if T_UP <= t < T_DOWN:
        u = (t - T_UP) / (T_DOWN - T_UP)
        hgt = 230 * 4 * u * (1 - u)
        vy = -230 * 4 * (1 - 2 * u) / (T_DOWN - T_UP)
        hy -= hgt
        tuck = math.sin(math.pi * u)
        for s in ("n", "f"):
            A = np.array([fs[s] + (8 if s == "n" else -8), -AHW - hgt + 120 * tuck])
            feet[s] = (A, 0.5 * tuck)
        up = ease_out(clamp(u / 0.3))
        arms["n"] = ("ang", -0.7 + (1.35 + 0.7) * up, 1.6 * up)
        arms["f"] = ("ang", -0.7 + (-2.55 + 0.7) * up, 0.2 * up)
        hands = {"n": ("open", 0.0), "f": ("open", 0.0)}
        lean = 0.0
    if t >= T_DOWN:
        e = t - T_DOWN
        sq = 46 * math.exp(-e * 9) * math.sin(min(e * 20, math.pi))
        hop = 0.0
        if e > 0.3:                       # пружинит от радости
            hop = 34 * abs(math.sin((e - 0.3) * 2 * math.pi / 0.42))
        hy += sq - hop
        for s in ("n", "f"):
            feet[s] = (np.array([fs[s], -AHW - hop]), 0.0)
        wv = math.sin((e) * 2 * math.pi / 0.42)
        arms["n"] = ("ang", 1.35 + 0.1 * wv, 1.6 + 0.25 * wv)
        arms["f"] = ("ang", -2.55 - 0.12 * wv, 0.2 + 0.2 * wv)
        hands = {"n": ("open", 0.0), "f": ("open", 0.0)}
        vy = -hop * 3 if hop else 0
    hip = np.array([hx, hy])
    joy = smooth(JUMP - 0.1, JUMP + 0.05, t)
    blink = 0.0
    expr = dict(lid=0.86 + 0.14 * joy, look=(0.45, -0.2 - 0.05 * joy), brows="up", mouth="grin",
                hair=clamp(vy * 0.03 + 3 * math.sin(t * 9) * wk, -18, 18))
    return dict(hip=hip, lean=lean, feet=feet, arms=arms, hands=hands, head_ang=-0.05 - 0.12 * joy,
                hood=clamp(-vy * 0.03, -16, 22), strings=(-14 + 6 * math.sin(psi) * wk, clamp(vy * .03, -20, 30)),
                expr=expr, back=backpack(t), front=camera_neck(t, vy))


def backpack(t):
    """Рюкзак за спиной (туловище: таз (0,0), вверх −y, вперёд +x; L-ед.)."""
    s = []
    body = [(-118, -390), (-196, -380), (-252, -330), (-262, -170), (-246, -120), (-150, -116), (-108, -150)]
    inner = blob([(-262, -230), (-150, -240), (-150, -116), (-262, -116)], "#2c6c74", .9)
    pk = [(-250, -250), (-176, -252), (-170, -150), (-250, -142)]
    inner += shape(pk, "#3f9aa3", blob([(-250, -190), (-170, -194), (-170, -150), (-250, -142)], "#2c6c74", .9) +
                   line([(-246, -236), (-180, -238)], 3, "#e8e0cc", seed=519, op=.9), w=4.4, seed=518)
    inner += line([(-200, -372), (-224, -300), (-226, -260)], 3, "#2a5a60", seed=517, op=.8)
    s.append(shape(body, "#4aa6ae", inner, w=5.2, seed=516))
    # верхняя ручка
    s.append(line([(-176, -384), (-160, -416), (-136, -404)], 9, "#2c6c74", taper=.1, wmin=.9, seed=515))
    return "".join(s)


def camera_neck(t, vy):
    """Ремень лямки рюкзака через плечо и фотоаппарат на ремешке на груди (качается)."""
    s = []
    # лямка рюкзака на плече
    s.append(shape([(-40, -432), (10, -428), (40, -300), (60, -190), (30, -186), (8, -296), (-30, -404)], "#2c6c74",
                   line([(0, -400), (30, -290), (44, -200)], 2.4, "#1d4a50", seed=521, op=.8), w=4, seed=520))
    sw = clamp(vy * 0.02, -14, 14) + 4 * math.sin(t * 7.0)
    cx, cy = 104 + sw * .3, -262 + abs(sw) * .4
    s.append(line([(26, -420), (70, -340), (cx - 30, cy - 34)], 4.5, "#3a3440", taper=.1, wmin=.9, seed=522))
    s.append(line([(70, -424), (110, -350), (cx + 20, cy - 36)], 4.5, "#3a3440", taper=.1, wmin=.9, seed=523))
    g = (f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(sw * 0.6)})">' +
         shape([(-46, -32, 1), (46, -32, 1), (46, 30, 1), (-46, 30, 1)], "#3a3f52",
               blob([(-46, 6), (46, 6), (46, 30), (-46, 30)], "#262a38", .9) +
               blob([(-34, -32), (-10, -32), (-10, -18), (-34, -18)], "#c9cfdd", .95), w=4.2, seed=524) +
         shape(ellipse_pts(18, 0, 26, 26, 18), "#262a38", blob(ellipse_pts(18, 0, 15, 15, 14), "#6aa3d8") +
               blob(ellipse_pts(12, -6, 5, 4, 8), "#ffffff", .9), w=3.6, seed=525) +
         shape([(-28, -32, 1), (-28, -44, 1), (-6, -44, 1), (-6, -32, 1)], "#3a3f52", "", w=3, seed=526) + "</g>")
    s.append(g)
    return "".join(s)


# ───────────────────────── мир мечты
def night_bg():
    s = []
    g = lin_grad([(0, "#141a3a", 1), (.6, "#22305e", 1), (1, "#2c3a6c", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#{g})"/>')
    return "".join(s)


def stars(t):
    rs = np.random.RandomState(31)
    s = []
    for k in range(46):
        x, y = rs.uniform(-300, W + 300), rs.uniform(-400, H + 300)
        r = rs.uniform(2, 5)
        tw = 0.55 + 0.45 * math.sin(t * rs.uniform(2, 5) + k)
        if k % 5 == 0:
            pts = []
            for i in range(8):
                rr = r * (2.4 if i % 2 == 0 else 0.7) * (0.7 + 0.3 * tw)
                a = i * math.pi / 4
                pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
            s.append(blob(pts, "#fff3c0"))
        else:
            s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * (0.6 + 0.4 * tw))}" fill="#dfe6ff"/>')
    return "".join(s)


def landscape(t):
    s = []
    g = lin_grad([(0, "#8fc9f0", 1), (.45, "#c9e6f6", 1), (.7, "#ffe6cf", 1), (1, "#ffd6c0", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-100" y="0" width="1300" height="1400" fill="url(#{g})"/>')
    s.append(japan.sun(820, 330, 62, t, 600))
    for k, (x0, y, sc, sp) in enumerate([(240, 260, 0.9, 14), (700, 470, 0.6, 10)]):
        x = x0 + sp * (t - 1.2)
        s.append(japan.puff_cloud(x, y, 110 * sc, 44 * sc, 610 + k, n=7, bump=.28, w=3.6))
    s.append(japan.fuji(560, 900, 1080, 520, 620))
    # дальние холмы
    s.append(shape([(-100, 880), (120, 846), (330, 880), (560, 860), (800, 890), (1040, 850), (1200, 880), (1200, 1000, 1), (-100, 1000, 1)], "#8cc8a0",
                   blob([(-100, 910), (1200, 910), (1200, 1000), (-100, 1000)], "#76b48c", .9), w=4, seed=630))
    # луг
    s.append(shape([(-100, 940), (300, 920), (700, 930), (1200, 915), (1200, 1500, 1), (-100, 1500, 1)], "#a6d67e",
                   blob([(-100, 1180), (1200, 1150), (1200, 1500), (-100, 1500)], "#8fc466", .9), w=4.4, seed=631))
    # тропинка: широкая внизу, сужается к воротам
    path = [(-100, 1120), (300, 1112), (560, 1104), (720, 1060), (800, 990), (840, 972), (870, 972), (850, 1000), (790, 1090),
            (640, 1180), (300, 1200), (-100, 1210)]
    s.append(shape(path, "#f0d9a8", blob([(-100, 1176), (640, 1158), (790, 1080), (850, 1000), (870, 972), (840, 1110), (640, 1220), (-100, 1220)],
                                         "#dcbf86", .9) +
                   "".join(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(r)}" ry="{f(r * .5)}" fill="#cfae72"/>'
                           for x, y, r in [(80, 1160, 9), (240, 1176, 7), (420, 1150, 8), (610, 1130, 6), (760, 1050, 5)]), w=4.2, seed=632))
    s.append(japan.torii(860, 990, 300, 640))
    # кустики и цветы
    rs = np.random.RandomState(8)
    for k in range(24):
        x, y = rs.uniform(-60, 1140), rs.uniform(960, 1260)
        if 1080 < y < 1230:
            continue
        s.append(japan.flower(x, y, rs.uniform(7, 11), rs.uniform(0, 70), "#ffffff" if k % 3 else "#ffe27a", "#f0a33a"))
    s.append(japan.sakura(150, 1010, 1.15, 650, t))
    return "".join(s)


def front_grass(t):
    rs = np.random.RandomState(5)
    s = []
    for k in range(30):
        x, y = rs.uniform(-60, 1140), rs.uniform(1225, 1300)
        h = rs.uniform(18, 30)
        s.append(line([(x, y), (x + rs.uniform(-6, 6) + 4 * math.sin(t * 3 + k), y - h)], 3.4, "#5e9a40", taper=.6, wmin=.2, seed=660 + k))
    return "".join(s)


def sparkles(t):
    if t < JUMP - 0.04:
        return ""
    e = t - (JUMP - 0.04)
    s = []
    hx = hip_x(t) * DK
    cx, cy = hx + 20, GY - 330
    for k in range(12):
        a = k * 2 * math.pi / 12 + 0.3
        rr = 150 + 230 * ease_out(clamp(e / 0.45)) + 20 * math.sin(e * 5 + k)
        x, y = cx + rr * math.cos(a) * 1.05, cy + rr * math.sin(a) * 0.95
        sc = back_out(clamp((e - (k % 3) * .04) / 0.22), 2.4) * (0.85 + 0.2 * math.sin(e * 10 + k)) * (1 - smooth(1.0, 1.15, e))
        if sc < 0.05:
            continue
        r = (26 if k % 2 == 0 else 17) * sc
        pts = []
        for i in range(8):
            rad = r if i % 2 == 0 else r * 0.32
            aa = i * math.pi / 4 + e * 2
            pts.append((x + rad * math.cos(aa), y + rad * math.sin(aa), 1))
        s.append(shape(pts, "#ffe05a" if k % 3 else "#ffffff", "", w=3.0, seed=700 + k))
    # вспышка-лучи на отрыве
    if e < 0.35:
        u = e / 0.35
        for k in range(10):
            a = k * math.pi / 5 + 0.1
            r0, r1 = 120 + 160 * u, 170 + 220 * u
            s.append(line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], 12 * (1 - u) + 2,
                          "#fff2a0", taper=.8, wmin=.1, seed=730 + k))
    # мелкие блёстки дождиком
    rs = np.random.RandomState(12)
    for k in range(18):
        x0 = cx + rs.uniform(-300, 300)
        y0 = cy + rs.uniform(-260, 60)
        y = y0 + 160 * e
        k2 = clamp(e / 0.15) * (1 - smooth(0.8, 1.1, e))
        if k2 < .05:
            continue
        r = rs.uniform(4, 8) * k2 * (0.6 + 0.4 * math.sin(e * 14 + k))
        s.append(f'<rect x="{f(x0 - r)}" y="{f(y - r)}" width="{f(2 * r)}" height="{f(2 * r)}" fill="{["#ffe05a", "#ffffff", "#ff9ec0"][k % 3]}" '
                 f'transform="rotate(45 {f(x0)} {f(y)})"/>')
    return "".join(s)


def scene(t):
    cx0, cy0, rx, ry = CL
    rim_out = japan.cloud_pts(cx0, cy0, rx + 40, ry + 40, 13, .1, .2)
    rim_in = japan.cloud_pts(cx0, cy0, rx - 12, ry - 12, 13, .07, .2)
    s = []
    # тень облака-рамки и сама рамка
    s.append(blob([(x + 14, y + 22) for x, y, *_ in rim_out], "#0c1028", .45, blur(10)))
    rim_inner = blob(japan.cloud_pts(cx0 + 40, cy0 + 60, rx + 30, ry + 30, 13, .1, .2), "#cfe0f6", .95)
    rim_inner += blob(japan.cloud_pts(cx0 - 40, cy0 - 50, rx + 10, ry + 10, 13, .1, .2), "#ffffff")
    s.append(shape(rim_out, "#ffffff", rim_inner, w=6.0, seed=800))
    # окно мечты
    c = lib.clip_of(rim_in)
    p = pose(t)
    g, _ = dima.draw(p)
    hx = hip_x(t)
    sh_k = 1 - 0.5 * clamp((GY - (GY + p["hip"][1] * DK + (LEG * 0.9 + AHW) * DK)) / 150)
    dshadow = blob(ellipse_pts(hx * DK + 8, GY + 4, 120 * sh_k, 16 * sh_k, 16), "#6b8a4a", .45, blur(4))
    dim = f'<g transform="translate(0 {f(GY)}) scale({DK})">{g}</g>'
    inside = landscape(t) + dshadow + dim + japan.petals(t, (-80, 120, 1180, 1300), 16, 900, (11, 17), (70, 130), 110) + sparkles(t) + front_grass(t)
    s.append(f'<g clip-path="url(#{c})">{inside}</g>')
    s.append(f'<path d="{lib.ink_closed(rim_in, 4.4, seed=801)}" fill="{INK}"/>')
    # пушистые клочки по краю окна (облако «дышит»)
    for k in range(5):
        a = k * 2 * math.pi / 5 + 0.6
        px, py = cx0 + (rx + 30) * math.cos(a), cy0 + (ry + 30) * math.sin(a)
        r = 46 + 6 * math.sin(t * 2 + k)
        s.append(japan.puff_cloud(px + 6 * math.sin(t * 1.4 + k), py, r * 1.2, r * .8, 820 + k, n=6, bump=.3, w=4.4))
    return "".join(s)


def build_static():
    if _ST:
        return
    _ST["bg"] = night_bg()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    u = clamp((t - 1.24) / 2.71)
    hx = hip_x(t) * DK
    cx = 500 + (hx - 185) * 0.4 + 20 * ease_io(u)
    cy = 790 - 20 * ease_io(u)
    scl = 1.16 + 0.08 * (0.35 * u + 0.65 * ease_io(u))
    e = t - JUMP
    if e > 0:
        k = math.exp(-e * 6)
        scl *= 1 + 0.035 * k * math.sin(min(e * 14, math.pi))
        cy += 6 * k * math.sin(e * 40)
    rot = 0.6 * math.sin(t * 1.3)
    return svg(f'<rect width="{W}" height="{H}" fill="#1a2248"/><g transform="{cam(cx, cy, scl, rot)}">'
               f'{_ST["bg"]}{stars(t)}{scene(t)}</g>')
