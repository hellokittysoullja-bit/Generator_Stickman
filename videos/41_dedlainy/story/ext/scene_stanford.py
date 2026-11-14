"""Сцена study рилса 32 (s09, s10): опыт в Стэнфорде (Oppezzo, Schwartz 2014). Без букв и логотипов.
s09 «В Стэнфорде людей просили придумывать идеи» (14.56–16.56): солнечный двор — песочные арки с красной черепицей,
     пальмы, солнце; камера влетает к «Стэнфорде» (14.76); шесть разных студентов с блокнотами (пишут, грызут
     карандаш, оглядываются); на «придумывать» (16.08) над головами выскакивают пустые облачка мыслей.
s10 «сидя и на ходу» (16.56–18.3): кадр пополам — сверху тот же человек сидит за столом в комнате (на «сидя» 17.04
     половина подсвечивается), снизу — на беговой дорожке (на «ходу» 17.8 подсвечивается, лента поехала, он шагает).
Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import person
import study28 as st
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, clip_rect, ease_in, ease_io, ease_out, ellipse_pts, f,
                 line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg, T)

_ST = {}
FLY = 14.76         # «Стэнфорде»
IDEAS = 16.08       # «придумывать»
SIT = 17.04         # «сидя»
WALK = 17.80        # «ходу»
GROUND = 1070
SAND, SAND_SH, SAND_DK, ARCH_IN = "#ecc996", "#d4a96f", "#b58a55", "#6e4a33"
TILE, TILE_SH = "#c9563a", "#9e3f2a"

STUD = [
    dict(skin="#f0c4a0", hair="short", hair_c="#5a3a26", top="#2d55a8", low="#1f2b52", face=.15, stubble=True),
    dict(skin="#8a5a3c", hair="curly", hair_c="#2a1a14", top="#e07a2e", low="#3a3040", face=-.1),
    dict(skin="#f4d0b4", hair="ponytail", hair_c="#c8622a", top="#3a9a6a", low="#24484a", face=.2),
    dict(skin="#d9a07a", hair="bun", hair_c="#2a1a14", top="#7a4fb0", low="#2a2a3a", face=-.2, glasses=True),
    dict(skin="#e8b896", hair="bald", hair_c="#9a7a66", top="#c94a3f", low="#3a3f4c", face=.1, glasses=True, mustache=True),
    dict(skin="#f2c9a8", hair="bob", hair_c="#e0b050", top="#d9467a", low="#2a2a3a", face=.1),
]
# x, ступни y, масштаб, действие
CROWD = [(150, 1150, .56, "write"), (520, 1140, .55, "chew"), (870, 1150, .56, "write"),
         (320, 1250, .62, "look"), (700, 1250, .62, "write"), (960, 1262, .63, "chew")]
CROWD_SPEC = [1, 3, 5, 0, 2, 4]


# ═══════════════════════════════ s09: двор
def sky():
    s = []
    lin_grad([(0, "#4f9de6", 1), (.65, "#9fd0f4", 1), (1, "#f6ead0", 1)], 0, 0, 0, 1, gid="gSky32")
    s.append(f'<rect x="-700" y="-900" width="{W + 1400}" height="{GROUND + 900}" fill="url(#gSky32)"/>')
    g = rad_grad([(0, "#fff8d8", 1), (.25, "#fff1b0", .7), (1, "#fff1b0", 0)], 880, 170, 460, 460)
    s.append(f'<rect x="-700" y="-900" width="{W + 1400}" height="{GROUND + 900}" fill="url(#{g})"/>')
    # далёкие холмы
    s.append(shape([(-700, 900), (-300, 800), (100, 840), (500, 790), (900, 830), (1300, 780), (1780, 860), (1780, 960, 1), (-700, 960, 1)],
                   "#9cc08a", blob([(500, 790), (900, 830), (1300, 780), (1300, 960), (500, 960)], "#86ad76", .8), w=3.6, seed=2001))
    return "".join(s)


def arch_pts(x, y0, w, y1):
    """Проём арки: низ y1, верх полукругом с вершиной y0."""
    r = w / 2
    pts = [(x - r, y1, 1)]
    for k in range(9):
        a = math.pi + math.pi * k / 8
        pts.append((x + r * math.cos(a), y0 + r + r * math.sin(a)))
    pts.append((x + r, y1, 1))
    return pts


def tile_roof(pts, sd, rows):
    """Крыша красной черепицей: заливка + ряды полукруглых «чешуек» (линии), теневая полоса снизу."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    inner = ""
    for k in range(rows):
        y = y0 + (y1 - y0) * (k + 1) / (rows + 1)
        inner += line([(x0 - 40, y), (x1 + 40, y + 2)], 3.2, TILE_SH, taper=.05, wmin=.8, seed=sd + k, op=.9)
        for j, xx in enumerate(np.arange(x0 - 20 + (k % 2) * 22, x1 + 20, 44)):
            inner += line([(xx, y - 14), (xx + 4, y - 2)], 2.4, TILE_SH, taper=.3, wmin=.5, seed=sd + 50 + j % 7, op=.7)
    inner += blob([(x0 - 40, y1 - 16), (x1 + 40, y1 - 16), (x1 + 40, y1 + 4), (x0 - 40, y1 + 4)], TILE_SH, .9)
    inner += line([(x0 + 30, y0 + 10), (x0 + (x1 - x0) * .4, y0 + 8)], 5, "#e98a6a", seed=sd + 90, op=.8)
    return shape(pts, TILE, inner, w=4.6, seed=sd)


def arcade(x0, x1, top, sd, step=120):
    """Галерея: стена песчаника, ряд арок, крыша черепицей над ней."""
    s = []
    wall = [(x0, top, 1), (x1, top, 1), (x1, GROUND, 1), (x0, GROUND, 1)]
    inner = blob([(x0, GROUND - 40), (x1, GROUND - 40), (x1, GROUND), (x0, GROUND)], SAND_SH, .8)
    for k, x in enumerate(np.arange(x0 + step / 2, x1, step)):
        ap = arch_pts(x, top + 70, step * .62, GROUND - 2)
        inner += shape(ap, ARCH_IN, blob([(x - step * .31, top + 140), (x + step * .31, top + 140), (x + step * .31, GROUND), (x - step * .31, GROUND)],
                                         "#5a3a28", .8), w=3.4, seed=sd + 10 + k % 9)
        inner += line([(x - step * .38, top + 60), (x, top + 40), (x + step * .38, top + 60)], 3, SAND_DK, seed=sd + 30 + k % 9, op=.7)
        # колонна-капитель между арками
        cx = x + step / 2
        inner += blob(rect_pts(cx - 10, top + 96, cx + 10, top + 110), SAND_DK, .7)
    s.append(shape(wall, SAND, inner, w=4.6, seed=sd))
    roof = [(x0 - 30, top + 6, 1), (x0 + 10, top - 62, 1), (x1 - 10, top - 62, 1), (x1 + 30, top + 6, 1)]
    s.append(tile_roof(roof, sd + 100, 2))
    return "".join(s)


def main_hall():
    s = []
    x0, x1, top = 300, 780, 560
    wall = [(x0, top, 1), (x1, top, 1), (x1, GROUND, 1), (x0, GROUND, 1)]
    inner = blob([(x1 - 110, top), (x1, top), (x1, GROUND), (x1 - 110, GROUND)], SAND_SH, .85)
    for k in range(5):        # кладка — мягкие швы
        y = top + 60 + k * 70
        inner += line([(x0, y), (x1, y + 2)], 2, SAND_DK, taper=.1, wmin=.6, seed=2100 + k, op=.35)
    for k, x in enumerate((390, 540, 690)):
        ap = arch_pts(x, 820, 116, GROUND - 2)
        inner += shape(ap, ARCH_IN, blob([(x - 58, 900), (x + 58, 900), (x + 58, GROUND), (x - 58, GROUND)], "#5a3a28", .8), w=4, seed=2110 + k)
        inner += line([(x - 72, 832), (x - 40, 800), (x, 790), (x + 40, 800), (x + 72, 832)], 4, SAND_DK, seed=2120 + k, op=.8)
    for k, x in enumerate((370, 470, 610, 710)):          # верхние окна-арки
        ap = arch_pts(x, 640, 50, 730)
        inner += shape(ap, "#4a6a8a", blob([(x - 25, 690), (x + 25, 690), (x + 25, 730), (x - 25, 730)], "#3a5672", .8)
                       + line([(x - 12, 680), (x - 6, 664)], 3, "#cfe4ff", seed=2140 + k, op=.8), w=3.2, seed=2130 + k)
    # розетка-окно над входом (без надписей)
    inner += shape(ellipse_pts(540, 650, 42, 42, 18), "#4a6a8a", "".join(line([(540, 650), (540 + 40 * math.cos(a), 650 + 40 * math.sin(a))], 2.6, SAND_DK, seed=2150 + j)
                                                                     for j, a in enumerate(np.linspace(0, 2 * math.pi, 8, endpoint=False))), w=3.6, seed=2149)
    s.append(shape(wall, SAND, inner, w=5, seed=2101))
    roof = [(x0 - 40, top + 8, 1), (x0 + 60, top - 120, 1), (x1 - 60, top - 120, 1), (x1 + 40, top + 8, 1)]
    s.append(tile_roof(roof, 2160, 3))
    return "".join(s)


def ground():
    s = []
    s.append(f'<rect x="-700" y="{GROUND}" width="{W + 1400}" height="1400" fill="#eadcbf"/>')
    s.append(blob([(-700, GROUND), (W + 700, GROUND), (W + 700, GROUND + 26), (-700, GROUND + 26)], "#7fb35e"))
    s.append(line([(-700, GROUND), (W + 700, GROUND)], 4.4, INK, taper=.05, wmin=.9, seed=2201))
    s.append(line([(-700, GROUND + 26), (W + 700, GROUND + 26)], 3, "#5a8a42", taper=.05, wmin=.9, seed=2202))
    for k in range(7):
        y = GROUND + 70 + k * 70 + k * k * 6
        s.append(line([(-700, y), (W + 700, y + 4)], 2.4, "#cdbb94", taper=.1, wmin=.7, seed=2210 + k, op=.8))
    for k in range(-6, 14):
        x = 540 + k * 130
        s.append(line([(540 + (x - 540) * .35, GROUND + 30), (x, GROUND + 900)], 2.2, "#cdbb94", taper=.1, wmin=.7, seed=2230 + k % 9, op=.7))
    return "".join(s)


def palm(x, y, h, t, sd, lean=8):
    """Пальма: изогнутый ствол с кольцами, крона из девяти листьев-перьев; крона качается."""
    s = []
    sway = 3 * math.sin(t * 1.3 + sd)
    top = (x + lean * h / 100 + sway * 2, y - h)
    mid = (x + lean * h / 160, y - h * .5)
    pts = [(x, y), mid, top]
    tr = lib.band(pts, 34, 20, step=6, cap=False)
    inner = blob(lib.band([(p[0] + 8, p[1]) for p in pts], 12, 7, step=6, cap=False), "#7a5532", .9)
    for k in range(int(h / 34)):
        u = k / (h / 34)
        px = x + (top[0] - x) * u * u * .5 + (mid[0] - x) * 2 * u * (1 - u) * 0 + (top[0] - x) * u * .5
        py = y - h * u
        inner += line([(px - 14, py - 4), (px + 14, py + 2)], 2.6, "#6a4628", seed=sd + 10 + k % 9, op=.8)
    s.append(shape(tr, "#a77a4c", inner, w=4, seed=sd))
    fr = []
    for k in range(9):
        a = math.radians(-180 + k * 22.5 + 4 * math.sin(t * 1.7 + k + sd))
        L = h * (0.42 + 0.08 * (k % 2))
        droop = 0.55 * abs(math.cos(a))
        p0 = top
        p1 = (top[0] + math.cos(a) * L * .55, top[1] + math.sin(a) * L * .55 - L * .12)
        p2 = (top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * .6 + L * droop)
        # лист: ширина по средней линии
        S = lib.sample([p0, p1, p2], False, 5)
        Tg = np.gradient(S, axis=0)
        Tg /= np.linalg.norm(Tg, axis=1, keepdims=True) + 1e-9
        N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
        wd = np.sin(np.linspace(0, math.pi, len(S))) ** .7 * 26
        Lp, Rp = S + N * wd[:, None], S - N * wd[:, None]
        leaf = [tuple(p) for p in Lp] + [tuple(p) for p in Rp[::-1]]
        col = "#4f9a46" if k % 2 else "#5aaa4e"
        inner = blob([tuple(p) for p in Rp] + [tuple(p) for p in S[::-1]], "#3d7c38", .9)
        inner += line([tuple(p) for p in S], 2.4, "#2f6a2c", seed=sd + 40 + k, op=.9)
        fr.append(shape(leaf, col, inner, w=3.4, seed=sd + 20 + k))
    s.append("".join(fr))
    s.append(shape(ellipse_pts(top[0], top[1] + 6, 20, 16, 10), "#8a6238", "", w=3, seed=sd + 60))
    return "".join(s)


def birds(t):
    s = []
    for k, (x0, y0, v) in enumerate([(-100, 330, 160), (-260, 400, 140)]):
        x = x0 + v * (t - 14.3)
        y = y0 + 10 * math.sin(t * 2 + k)
        fl = 14 * math.sin(t * 14 + k)
        s.append(line([(x - 26, y - fl), (x - 10, y - 4), (x, y + 2), (x + 10, y - 4), (x + 26, y - fl)], 4.4, INK, taper=.5, wmin=.3, seed=2300 + k))
    return s and "".join(s)


def notebook(x, y, w, h, ang, sd, prog=0.0):
    """Блокнот на спирали, страница пустая (линейки); prog — несколько каракуль-штрихов (не буквы)."""
    pts = [(-w / 2, -h / 2, 1), (w / 2, -h / 2, 1), (w / 2, h / 2, 1), (-w / 2, h / 2, 1)]
    inner = ""
    for k in range(4):
        yy = -h / 2 + h * (0.3 + 0.17 * k)
        inner += line([(-w / 2 + 8, yy), (w / 2 - 8, yy)], 1.6, "#9ab6d8", taper=.05, wmin=.9, seed=sd + k, op=.9)
    inner += blob([(w * .2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (w * .3, h / 2)], "#e9e4d4", .7)
    s = shape(pts, "#fbfaf4", inner, w=3, seed=sd + 10)
    for k in range(5):
        xx = -w / 2 + 12 + k * (w - 24) / 4
        s += f'<ellipse cx="{f(xx)}" cy="{f(-h / 2)}" rx="4" ry="7" fill="none" stroke="#6b7389" stroke-width="2.6"/>'
    s = shape([(-w / 2 - 4, -h / 2 + 2, 1), (w / 2 + 4, -h / 2 + 2, 1), (w / 2 + 4, h / 2 + 6, 1), (-w / 2 - 4, h / 2 + 6, 1)], "#2f6db5", "", w=3, seed=sd + 20) + s
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)})">{s}</g>'


def cloud_pts(x, y, rx, ry, n=7, sd=0):
    """Контур облачка из n круглых «булочек»: дуги между впадинами (впадины — углы)."""
    rs = np.random.RandomState(sd)
    pts = []
    for j in range(n):
        a0 = 2 * math.pi * j / n
        a1 = 2 * math.pi * (j + 1) / n
        bump = 0.2 + 0.06 * rs.uniform(-1, 1)
        for k in range(6):
            u = k / 6
            a = a0 + (a1 - a0) * u
            r = 1 + bump * math.sin(math.pi * u)
            pts.append((x + rx * math.cos(a) * r, y + ry * math.sin(a) * r) + ((1,) if k == 0 else ()))
    return pts


def thought(x, y, sc, sd):
    """Пустое облачко мысли с двумя пузырьками к голове (вниз-влево)."""
    if sc < 0.02:
        return ""
    w = 4 * max(sc, .5)
    s = shape(cloud_pts(x, y, 84 * sc, 50 * sc, 7, sd), "#ffffff", blob(ellipse_pts(x + 14 * sc, y + 24 * sc, 70 * sc, 22 * sc, 12), "#e6eef7", .9),
              w=w, seed=sd)
    s += shape(ellipse_pts(x - 40 * sc, y + 82 * sc, 15 * sc, 12 * sc, 10), "#ffffff", "", w=w * .8, seed=sd + 1)
    s += shape(ellipse_pts(x - 58 * sc, y + 110 * sc, 8 * sc, 7 * sc, 8), "#ffffff", "", w=w * .7, seed=sd + 2)
    return s


def student_standing(i, t):
    x, y, sc, act = CROWD[i]
    spec = STUD[CROWD_SPEC[i]]
    ph = i * 1.37
    up = smooth(IDEAS + 0.05, IDEAS + 0.3, t)            # смотрят на облачко
    bl = (t * 0.8 + ph * .37) % 2.7
    blink = max(0.0, 1 - abs(bl - 1.3) / 0.07)
    nb_x, nb_y = 0, -395
    pose = {"no_legs": False, "legs": {"L": (3, 0), "R": (-3, 0)}, "blink": blink, "mouth": "flat", "brow": 0.3,
            "look": (0.2 * math.sin(t * .7 + ph), 0.6 - 1.5 * up), "head_tilt": 4 * math.sin(t * 1.1 + ph) - 6 * up}
    wph = t * 8 + ph
    if act == "write":
        pose["hand_target"] = {"L": (-52, -380), "R": (18 + 10 * math.sin(wph) * (1 - up), -400 + 4 * math.cos(wph * 1.3))}
        pose["curl"] = {"L": .2, "R": .75}
        pose["over_hand"] = {"R": lambda h, a: st.pencil_item(h, a, 0.9)}
    elif act == "chew":       # карандаш у рта, думает
        pose["hand_target"] = {"L": (-48, -384), "R": (30, -560 + 6 * math.sin(t * 6 + ph))}
        pose["curl"] = {"L": .2, "R": .8}
        pose["over_hand"] = {"R": lambda h, a: st.pencil_item(h, a, 0.9)}
        pose["mouth"] = "wavy"
        pose["look"] = (0.5, -0.6 - 0.4 * up)
    else:                     # оглядывается, держит блокнот обеими
        pose["hand_target"] = {"L": (-74, -392), "R": (74, -396)}
        pose["curl"] = {"L": .3, "R": .3}
        pose["look"] = (0.8 * math.sin(t * 1.6 + ph), 0.2 - 1.2 * up)
    if t > IDEAS + 0.2:
        pose["mouth"] = "o" if i % 2 else "smile"
        pose["brow"] = 1.0
    breath = 3 * math.sin(t * 2.1 + ph)
    yy = y + breath * sc * 0
    shadow = blob(ellipse_pts(x + 10, y + 6, 110 * sc, 16 * sc, 12), "#9a8a6a", .5, blur(5))
    body = person.draw(spec, dict(pose, no_arms=True), x, yy, sc, sd=3000 + i * 100)
    nb = f'<g transform="translate({f(x)} {f(yy)}) scale({sc:.4f})">{notebook(nb_x, nb_y, 150, 112, -8 + 3 * math.sin(t + ph), 3080 + i * 100)}</g>'
    arms = person.draw(spec, dict(pose, only_arms=True), x, yy, sc, sd=3000 + i * 100)
    # облачко над головой
    e = t - IDEAS - i * 0.05
    th = ""
    if e > 0:
        k = back_out(clamp(e / 0.28), 2.4) * (1 + 0.03 * math.sin(e * 6 + i))
        hx, hy = x + 80 * sc, y - 860 * sc - (70 if i < 3 else 0)
        th = thought(hx + 6 * math.sin(e * 2 + i), hy - 10 * e, k * 0.82 * sc / .6, 3090 + i * 100)
    return shadow + body + nb + arms, th


def s09(t):
    art = [_ST["sky"], st.sun(t), st.clouds(t), birds(t), _ST["hills_bld"]]
    art.append(palm(-20, GROUND + 10, 640, t, 2400, 10))
    art.append(palm(1090, GROUND + 10, 600, t, 2440, -12))
    art.append(palm(240, GROUND - 4, 420, t, 2480, 6))
    art.append(palm(850, GROUND - 4, 450, t, 2520, -8))
    art.append(_ST["ground"])
    ths = []
    for i in range(6):
        b, th = student_standing(i, t)
        art.append(b)
        ths.append(th)
    art += ths
    # «пинг» над облачками
    e = t - IDEAS
    if 0 < e < 0.4:
        for i in range(6):
            x, y, sc, _ = CROWD[i]
            art.append(st.pop_ring(x + 80 * sc, y - 860 * sc - (70 if i < 3 else 0), 90 * sc / .6, 58 * sc / .6, e - i * 0.05, 3500 + i))
    # камера: влёт с неба вниз к «Стэнфорде», дальше медленный наезд
    u = ease_out(clamp((t - 14.36) / (FLY + 0.08 - 14.36)), 3)
    cy = 700 + (860 - 700) * u
    sc = 0.8 + (1.04 - 0.8) * u
    rot = -5 * (1 - u)
    v = clamp((t - FLY) / 1.9)
    sc += 0.06 * ease_io(v)
    cy += 20 * v
    if t > FLY:
        e = t - FLY
        sc *= 1 + 0.025 * math.exp(-e * 7) * math.sin(min(e * 14, math.pi))
    e2 = t - IDEAS
    if e2 > 0:
        sc *= 1 + 0.02 * math.exp(-e2 * 6) * math.sin(min(e2 * 14, math.pi))
    return "".join(art), cam(540, cy, sc, rot + 0.5 * v), "#9fd0f4"


# ═══════════════════════════════ s10: сидя / на ходу
HERO = dict(skin="#f0c4a0", hair="short", hair_c="#5a3a26", top="#2d55a8", low="#1f2b52", face=.35, stubble=True)
P1 = (40, 160, 1040, 700)        # верхняя панель
P2 = (40, 730, 1040, 1270)       # нижняя


def room_top(t):
    x0, y0, x1, y1 = P1
    s = []
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#ead6b4"/>')
    s.append(blob([(x0, 600), (x1, 600), (x1, y1), (x0, y1)], "#b98a5a"))
    s.append(line([(x0, 600), (x1, 600)], 4, INK, taper=.05, wmin=.9, seed=4001))
    for k in range(4):
        s.append(line([(x0, 625 + k * 22), (x1, 627 + k * 22)], 2, "#9a6e44", taper=.1, wmin=.7, seed=4002 + k, op=.7))
    # окно (день за окном) и полка
    wpts = [(90, 210, 1), (330, 210, 1), (330, 470, 1), (90, 470, 1)]
    inner = blob(rect_pts(90, 210, 330, 470), "#a6d4f5") + blob([(90, 470), (150, 400), (200, 440), (260, 380), (330, 430), (330, 470)], "#8fbf7a")
    s.append(shape(wpts, "#a6d4f5", inner + line([(210, 210), (210, 470)], 5, "#f3ede1", taper=.05, wmin=.9, seed=4011), w=4.6, seed=4010))
    s.append(shape(rect_pts(80, 468, 340, 486), "#f3ede1", "", w=3.6, seed=4012))
    s.append(shape(rect_pts(760, 300, 1000, 318), "#9a6438", "", w=3.4, seed=4013))
    for k, (x, h, c) in enumerate([(780, 70, "#e2543f"), (812, 86, "#2f6db5"), (846, 64, "#3a9a6a"), (874, 80, "#d9a338")]):
        s.append(shape(rect_pts(x, 300 - h, x + 28, 300), c, blob(rect_pts(x + 16, 300 - h, x + 28, 300), lib.mul(c, (.8, .8, .85)), .8), w=3, seed=4014 + k))
    s.append(shape(ellipse_pts(950, 280, 30, 22, 12), "#c96b4a", "", w=3, seed=4020))
    s.append(blob(ellipse_pts(950, 250, 34, 22, 10), "#5aaa4e"))
    return "".join(s)


def chair_side(x, seat_y, floor):
    s = []
    c, csh = "#6b4a2e", "#4a3020"
    s.append(shape(rect_pts(x - 70, seat_y - 230, x - 50, floor), c, "", w=3.4, seed=4101))      # спинка-ножка
    s.append(shape(rect_pts(x - 80, seat_y - 230, x - 40, seat_y - 120, 8), "#8a5f3c", "", w=3.4, seed=4102))
    s.append(shape(rect_pts(x + 50, seat_y, x + 66, floor), c, "", w=3, seed=4103))
    s.append(shape(rect_pts(x - 80, seat_y - 6, x + 80, seat_y + 16, 6), "#8a5f3c", blob(rect_pts(x - 80, seat_y + 6, x + 80, seat_y + 16), csh, .8),
                   w=3.6, seed=4104))
    return "".join(s)


def desk_side(x, top, floor):
    s = []
    s.append(shape(rect_pts(x + 220, top, x + 236, floor), "#7a5532", "", w=3, seed=4201))
    s.append(shape(rect_pts(x - 20, top, x - 4, floor), "#7a5532", "", w=3, seed=4202))
    s.append(shape(rect_pts(x - 40, top - 16, x + 260, top + 6, 4), "#c99a62", blob(rect_pts(x - 40, top - 2, x + 260, top + 6), "#a87c4c"),
                   w=3.6, seed=4203))
    # лампа, кружка, лист
    s.append(shape([(x + 120, top - 18, 1), (x + 210, top - 22, 1), (x + 214, top - 14, 1), (x + 120, top - 12, 1)], "#fbfaf4", "", w=2.6, seed=4204))
    s.append(shape(rect_pts(x + 30, top - 58, x + 66, top - 16, 6), "#e2543f", blob(rect_pts(x + 50, top - 58, x + 66, top - 16), "#b8402e"), w=3, seed=4205))
    return "".join(s)


def top_scene(t):
    x0, y0, x1, y1 = P1
    floor = 640
    hx, seat = 400, 520
    s = [room_top(t)]
    sc = 0.5
    Y = floor - 10 + 0          # ступни сидящего (ноги согнуты: стопы на −160·sc)
    Y = seat + 300 * sc         # бёдра на сиденье
    s.append(chair_side(hx - 10, seat + 4, floor))
    sigh = math.sin(t * 1.4)
    bl = (t * 0.9) % 2.3
    pose = {"legs": {"L": (88, 86), "R": (92, 92)}, "look": (0.6, -0.5 + 0.15 * sigh), "brow": -0.4, "mouth": "frown",
            "head_tilt": 6 + 4 * sigh, "blink": max(0.0, 1 - abs(bl - 1.2) / 0.08),
            "hand_target": {"L": (150, -330), "R": (196 + 6 * math.sin(t * 9), -328 - 10 * abs(math.sin(t * 9)))},
            "curl": {"L": .2, "R": .75}, "over_hand": {"R": lambda h, a: st.pencil_item(h, a, 0.9)}}
    body = person.draw(HERO, dict(pose, no_arms=True), hx, Y, sc, sd=4300)
    arms = person.draw(HERO, dict(pose, only_arms=True), hx, Y, sc, sd=4300)
    s.append(body)
    s.append(desk_side(hx + 60, Y - 340 * sc + 8, floor))
    s.append(arms)
    # на «сидя»: «застрял» — облачко с каракулей-клубком над головой
    e = t - SIT
    if e > 0:
        k = back_out(clamp(e / 0.25), 2.2)
        cx, cy = hx + 150, Y - 860 * sc
        s.append(thought(cx, cy, 0.62 * k, 4400))
        if k > 0.3:
            pts = [(cx - 4 + 22 * math.cos(a * 2.3) * (1 + a / 9), cy - 6 + 14 * math.sin(a * 2.3) * (1 + a / 9)) for a in np.linspace(0, 8, 30)]
            s.append(line([(p[0] * 1, p[1]) for p in pts], 3.4, "#6b7389", taper=.2, wmin=.6, seed=4401, op=1))
    return "".join(s)


def gym_bot(t):
    x0, y0, x1, y1 = P2
    s = []
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#d4e6ec"/>')
    for k in range(6):
        s.append(f'<rect x="{x0 + 40 + k * 170}" y="{y0}" width="60" height="{y1 - y0}" fill="#c5dbe3"/>')
    s.append(blob([(x0, 1180), (x1, 1180), (x1, y1), (x0, y1)], "#8f9db0"))
    s.append(line([(x0, 1180), (x1, 1180)], 4, INK, taper=.05, wmin=.9, seed=4501))
    # окно с деревьями — «на ходу» идёт мимо
    wpts = [(700, 790, 1), (990, 790, 1), (990, 1010, 1), (700, 1010, 1)]
    inner = blob(rect_pts(700, 790, 990, 1010), "#a6d4f5") + blob(ellipse_pts(780, 960, 60, 50, 12), "#5aaa4e") + blob(ellipse_pts(900, 980, 70, 46, 12), "#4f9a46")
    s.append(shape(wpts, "#a6d4f5", inner + line([(845, 790), (845, 1010)], 5, "#f3ede1", taper=.05, wmin=.9, seed=4511), w=4.6, seed=4510))
    return "".join(s)


def treadmill(t, run):
    s = []
    x0, x1, top = 170, 760, 1150
    s.append(blob(ellipse_pts((x0 + x1) / 2, 1186, 330, 16, 14), "#4a5060", .45, blur(5)))
    deck = rect_pts(x0, top, x1, top + 36, 18)
    off = run
    inner = ""
    for k in range(-1, 16):
        x = x0 + 20 + ((k * 46 - off) % (46 * 15))
        if x < x1 - 20:
            inner += line([(x, top + 4), (x - 6, top + 14)], 3, "#5a6070", taper=.1, wmin=.7, seed=4520 + k % 7)
    inner += blob(rect_pts(x0, top + 20, x1, top + 36), "#2a2f3a")
    s.append(shape(deck, "#3a3f4c", inner, w=4.2, seed=4530))
    for k, xx in enumerate((x0 + 18, x1 - 18)):
        a = -run / 16
        s.append(shape(ellipse_pts(xx, top + 18, 14, 14, 10), "#9aa3b2", line([(xx - 12 * math.cos(a), top + 18 - 12 * math.sin(a)),
                                                                              (xx + 12 * math.cos(a), top + 18 + 12 * math.sin(a))], 2.6, INK, seed=4540 + k), w=2.6, seed=4542 + k))
    s.append(shape(rect_pts(x0 - 10, top + 30, x1 + 10, top + 46, 6), "#6b7389", "", w=3, seed=4545))
    # стойка и пульт (без надписей)
    s.append(line([(x1 - 30, top + 6), (x1 + 20, 900)], 18, "#6b7389", taper=.05, wmin=.95, seed=4550))
    s.append(line([(x1 + 20, 912), (x1 - 160, 938)], 12, "#9aa3b2", taper=.05, wmin=.95, seed=4551))
    s.append(shape([(x1 - 20, 880, 1), (x1 + 70, 864, 1), (x1 + 80, 914, 1), (x1 - 10, 930, 1)], "#3a3f4c",
                   blob([(x1 - 6, 884), (x1 + 60, 872), (x1 + 66, 906), (x1, 916)], "#5fd3a0" if run > 0 else "#4a6a70"), w=3.6, seed=4552))
    return "".join(s)


def bot_scene(t):
    s = [gym_bot(t)]
    go = smooth(WALK - 0.05, WALK + 0.2, t)
    run = max(0.0, t - WALK) * 260
    s.append(treadmill(t, run))
    sc = 0.5
    X, Y = 470, 1150
    if t < WALK - 0.05:
        pose = {"look": (0.4, -0.2), "mouth": "flat", "brow": 0.2, "head_tilt": 2 * math.sin(t * 2),
                "blink": max(0.0, 1 - abs((t * 0.9 + .7) % 2.3 - 1.2) / 0.08)}
    else:
        ph = (t - WALK) * 11 + 0.3
        pose = {"walk": ph, "look": (0.6, 0), "mouth": "smile", "brow": 0.6, "head_tilt": 3 * math.sin(ph),
                "blink": max(0.0, 1 - abs((t * 0.9 + .7) % 2.3 - 1.2) / 0.08)}
    s.append(person.draw(HERO, pose, X, Y + 2, sc, sd=4600))
    # на «ходу»: облачко с лампочками-идеями
    e = t - WALK
    if e > 0:
        k = back_out(clamp(e / 0.25), 2.2)
        cx, cy = X + 190, Y - 760 * sc
        s.append(thought(cx, cy, 0.62 * k, 4700))
        if k > 0.3:
            import scene_brain32 as b32
            for j, dx in enumerate((-30, 10, 48)):
                on = smooth(0.1 + j * 0.08, 0.2 + j * 0.08, e)
                s.append(b32.bulb(cx + dx * k, cy - 8, on, 0.2 * k, 4710 + j * 30, t, run=False))
    return "".join(s)


def panel(rect, content, hi, dim, sd):
    x0, y0, x1, y1 = rect
    c = clip_rect(x0, y0, x1 - x0, y1 - y0, 28)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = 1 + 0.025 * hi
    s = []
    if hi > 0.01:
        g = rad_grad([(0, "#ffe27a", .0), (.86, "#ffe27a", .0), (.93, "#ffd23a", .75 * hi), (1, "#ffd23a", 0)], cx, cy, (x1 - x0) * .58, (y1 - y0) * .62)
        s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f((x1 - x0) * .6)}" ry="{f((y1 - y0) * .64)}" fill="url(#{g})"/>')
    body = f'<g clip-path="url(#{c})">{content}'
    if dim > 0.01:
        body += f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#1c2033" opacity="{0.38 * dim:.3f}"/>'
    body += "</g>"
    s.append(body)
    col = mix("#2a2430", "#ffc21a", hi)
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="28" fill="none" stroke="{col}" stroke-width="{f(8 + 6 * hi)}"/>')
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({f(k)}) translate({f(-cx)} {f(-cy)})">{"".join(s)}</g>'


def s10(t):
    h1 = smooth(SIT - 0.03, SIT + 0.12, t) * (1 - smooth(WALK - 0.05, WALK + 0.1, t))
    h2 = smooth(WALK - 0.03, WALK + 0.12, t)
    p1 = 0.0 if t < SIT else math.exp(-(t - SIT) * 6) * math.sin(min((t - SIT) * 14, math.pi))
    p2 = 0.0 if t < WALK else math.exp(-(t - WALK) * 6) * math.sin(min((t - WALK) * 14, math.pi))
    bg = [f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="#f3e9d2"/>']
    for k in range(-6, 30):
        bg.append(f'<rect x="-600" y="{-400 + k * 80}" width="{W + 1200}" height="2" fill="#dccaa4" opacity=".7"/>')
    art = "".join(bg) + panel(P1, top_scene(t), h1 + 0.6 * p1, h2, 4800) + panel(P2, bot_scene(t), h2 + 0.6 * p2, h1, 4900)
    u = clamp((t - 16.36) / 2.14)
    sc = 1.0 + 0.045 * (0.4 * u + 0.6 * ease_io(u))
    return art, cam(540, 715 + 10 * u, sc, 0.4 - 0.7 * u), "#f3e9d2"


def build_static():
    if _ST:
        return
    _ST["sky"] = sky()
    _ST["hills_bld"] = arcade(-420, 330, 790, 2050) + arcade(750, 1500, 790, 2070, 120) + main_hall()
    _ST["ground"] = ground()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm, bg = {"s09": s09, "s10": s10}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cm}">{art}</g>')
