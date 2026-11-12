"""Сцена tv (s02, s14, s15): телевизор крупно в тёмной комнате, холодное свечение, блик стекла; на экране карточки.
События экрана привязаны к общей таблице света timing23 (SWITCHES, PLAY_AT), чтобы свет комнаты совпал с экраном."""
import math

import numpy as np

import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, clip_rect, ease_in, ease_io, ease_out, f, line,
                 lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg, timing23)
from cards import CH, CW, card, card_spec

# экран в мире
SX0, SY0, SX1, SY1 = 52, 566, 1028, 1146
SW, SHh = SX1 - SX0, SY1 - SY0
SCX, SCY = (SX0 + SX1) / 2, (SY0 + SY1) / 2
# сетка на экране (локально)
GW, GH, PITCH, ROWY, GX0 = 224, 140, 246, (84, 246, 408), 34
SW_S02 = [s for s in timing23.SWITCHES if 1.2 < s < 2.9]       # 1.50 1.82 2.12 2.42
FLY = [s for s in timing23.SWITCHES if 23.0 < s < 24.8]        # 23.20 23.95 24.62
POP = 24.88                                                     # «три»
PLAY = timing23.PLAY_AT                                          # 25.72 «включает»
_STATIC = {}


def wall():
    s = []
    DEFS.append('<pattern id="pWall" width="96" height="150" patternUnits="userSpaceOnUse">'
                '<rect width="96" height="150" fill="#262a41"/>'
                '<rect x="0" width="2" height="150" fill="#2c3049"/><rect x="48" width="1.5" height="150" fill="#22263a"/>'
                '<path d="M24 40 L31 54 L24 68 L17 54Z" fill="#30354f"/><path d="M72 115 L79 129 L72 143 L65 129Z" fill="#30354f"/>'
                '</pattern>')
    s.append(f'<rect x="-500" y="-500" width="{W + 1000}" height="2000" fill="url(#pWall)"/>')
    # картина в рамке слева сверху (тёмная, ловит отсвет)
    fr = rect_pts(70, 150, 350, 400)
    inner = f'<rect x="60" y="140" width="300" height="270" fill="#4a3a5e"/>'
    inner += blob([(90, 380), (150, 290), (200, 330), (260, 250), (340, 380)], "#34284a")
    inner += f'<circle cx="270" cy="210" r="26" fill="#6c5a80"/>'
    s.append(shape(fr, "#3a2c2a", "", w=5, seed=11))
    s.append(shape(rect_pts(92, 172, 328, 378), "#4a3a5e", inner, w=3.4, seed=12))
    s.append(line([(210, 150), (210, 110)], 2.2, "#14121c", seed=13, taper=.2, wmin=.7))
    # провод от ТВ вниз
    s.append(line([(980, 1150), (990, 1200), (1000, 1260)], 5, "#0e0d14", taper=.1, wmin=.9, seed=14))
    return "".join(s)


def tv_body():
    s = []
    # ножки
    for x0, d in [(210, -1), (870, 1)]:
        s.append(shape([(x0 - 8, 1146, 1), (x0 + 8, 1146, 1), (x0 + 8 + 26 * d, 1206, 1), (x0 - 8 + 26 * d, 1206, 1)], "#16161e", w=3.4, seed=20 + x0))
    # корпус-рамка
    fr = rect_pts(36, 548, 1044, 1164, r=16)
    inner = f'<rect x="30" y="540" width="1020" height="630" fill="url(#gBezel)"/>'
    inner += blob([(36, 552), (1044, 552), (1044, 562), (36, 562)], "#3a3d52", .9)
    s.append(shape(fr, "#15151d", inner, w=5.2, seed=21))
    # светодиод
    s.append('<circle cx="540" cy="1156" r="3" fill="#ff4a3a" opacity=".85"/>')
    s.append(line([(SX0 - 2, SY1 + 2), (SX1 + 2, SY1 + 2)], 2.6, "#000", taper=.1, wmin=.8, seed=22))
    return "".join(s)


def cabinet():
    s = []
    top = [(-400, 1192, 1), (1480, 1192, 1), (1480, 1250, 1), (-400, 1250, 1)]
    inner = '<rect x="-400" y="1188" width="1880" height="70" fill="url(#gCabTop)"/>'
    s.append(shape(top, "#4b3c3a", inner, w=5, seed=30))
    front = [(-400, 1250, 1), (1480, 1250, 1), (1480, 1760, 1), (-400, 1760, 1)]
    inner = '<rect x="-400" y="1250" width="1880" height="520" fill="url(#gCabFront)"/>'
    for x in (-400, -40, 360, 720, 1080):
        inner += line([(x + 360, 1262), (x + 360, 1750)], 4, INK, taper=.2, wmin=.6, seed=31 + x)
    for x in (180, 540, 900):
        inner += shape(rect_pts(x - 50, 1420, x + 50, 1436, 6), "#7a6a66", w=2.6, seed=40 + x)
    inner += blob([(-400, 1250), (1480, 1250), (1480, 1290), (-400, 1290)], "#0e0b12", .45, blur(10))
    s.append(shape(front, "#3a2d2e", inner, w=5, seed=32))
    # отражение экрана на крышке тумбы
    s.append(f'<g id="tvrefl"><rect x="120" y="1196" width="840" height="46" rx="20" fill="#86a8ff" opacity=".22" {blur(14)}/></g>')
    # кружка справа и колонка слева
    s.append(shape([(930, 1100), (990, 1100), (986, 1196, 1), (934, 1196, 1)], "#3c4a6a",
                   blob([(960, 1100), (990, 1100), (986, 1196), (962, 1196)], "#26304a", .9), w=4.4, seed=50))
    s.append(shape(T_ellipse(960, 1100, 30, 8), "#1b2236", w=3.4, seed=51))
    s.append(line([(990, 1120), (1012, 1128), (1014, 1160), (988, 1170)], 6, "#3c4a6a", taper=.1, wmin=.9, seed=52))
    s.append(shape(rect_pts(80, 1080, 160, 1196, 10), "#1c1c26",
                   '<circle cx="120" cy="1150" r="24" fill="#2a2a38"/><circle cx="120" cy="1150" r="9" fill="#14141c"/>'
                   '<circle cx="120" cy="1106" r="9" fill="#2a2a38"/>', w=4.4, seed=53))
    # пол
    s.append(shape([(-400, 1760, 1), (1480, 1760, 1), (1480, 2300, 1), (-400, 2300, 1)], "#20182a",
                   "".join(line([(x, 1770), (x - 30, 1990)], 3, "#140e1c", seed=60 + x) for x in range(-360, 1480, 170)), w=4, seed=61))
    return "".join(s)


def foreground():
    """Дима со спины (через плечо): затылок лохматый, ухо, капюшон и плечи горчичного худи — в ночи, контровой холодный
    свет экрана по верхним краям."""
    s = []
    HAIR, HAIR_SH, HOOD, HOOD_SH, SKIN = "#2f2130", "#1d1420", "#5c4a2c", "#3e311e", "#7a5a5c"
    # плечи и капюшон
    sh = [(-60, 2000, 1), (-60, 1800), (60, 1730), (200, 1700), (330, 1712), (470, 1700), (600, 1730), (720, 1800), (780, 2000, 1)]
    inner = blob([(-60, 1800), (60, 1730), (200, 1700), (330, 1712), (470, 1700), (600, 1730), (720, 1800), (720, 1760), (330, 1690), (-60, 1770)], "#8ea6e0", .35)
    inner += blob([(380, 1760), (720, 1800), (780, 2000), (420, 2000)], HOOD_SH, .8)
    inner += line([(240, 1800), (260, 1880), (250, 1960)], 4, "#1c1520", seed=81, op=.7)
    inner += line([(470, 1780), (500, 1860)], 3.6, "#1c1520", seed=82, op=.6)
    s.append(shape(sh, HOOD, inner, w=6, seed=80))
    hood = [(150, 1740), (190, 1660), (330, 1640), (470, 1662), (510, 1740), (420, 1770), (330, 1760), (240, 1772)]
    s.append(shape(hood, HOOD_SH, line([(200, 1720), (330, 1690), (460, 1716)], 3.4, "#1c1520", seed=84, op=.8), w=5.4, seed=83))
    # шея
    s.append(shape([(270, 1600), (390, 1600), (395, 1690), (265, 1690)], SKIN, blob([(270, 1600), (390, 1600), (390, 1650), (270, 1650)], "#4a3440", .8), w=4.6, seed=85))
    # ухо справа
    ear = [(468, 1480), (500, 1470), (512, 1510), (498, 1560), (470, 1570)]
    s.append(shape(ear, SKIN, blob([(480, 1490), (500, 1500), (490, 1550), (476, 1550)], "#4a3440", .8), w=4.4, seed=86))
    # затылок: крупные неровные пряди (как у Димы — лохматые «перья»), не пила
    loc = [(-172, 60), (-196, 14, 1), (-170, -10), (-214, -70, 1), (-160, -88), (-178, -168, 1), (-110, -150),
           (-96, -232, 1), (-40, -176), (10, -262, 1), (46, -180), (110, -236, 1), (118, -160), (194, -176, 1),
           (168, -98), (226, -64, 1), (178, -20), (206, 30, 1), (172, 60)]
    pts = [(330 + x * 0.92, 1530 + y * 0.92) + tuple(p[2:]) for p in loc for x, y in [p[:2]]]
    pts += [(500, 1600), (440, 1650), (330, 1664), (220, 1650), (160, 1600)]
    inner = blob([(150, 1520), (330, 1600), (510, 1520), (520, 1680), (140, 1680)], HAIR_SH, .9)
    for i, st in enumerate([[(250, 1340), (280, 1420), (296, 1520)], [(400, 1330), (372, 1420), (372, 1520)],
                            [(180, 1440), (222, 1500), (236, 1590)], [(470, 1440), (440, 1510), (446, 1600)],
                            [(330, 1300), (336, 1400)], [(150, 1380), (196, 1430)], [(500, 1380), (470, 1420)]]):
        inner += line(st, 4, "#120b14", seed=90 + i, op=.85)
    s.append(shape(pts, HAIR, inner, w=6, seed=87, id="fgHair"))
    # контровой холодный свет: полумесяц по верхнему краю
    c = lib.clip_of(pts)
    s.append(f'<g clip-path="url(#{c})"><path d="{lib.fill_d(pts)}" fill="#9cb6ff" opacity=".55"/>'
             f'<path d="{lib.fill_d(pts)}" transform="translate(6 22)" fill="{HAIR}" {blur(5)}/>'
             f'<path d="{lib.fill_d(pts)}" transform="translate(10 40)" fill="{HAIR}"/></g>')
    s.append(f'<path d="{lib.ink_closed(pts, 6, seed=87)}" fill="{INK}"/>')
    return "".join(s)


def T_ellipse(cx, cy, rx, ry):
    return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]


def static_defs():
    lin_grad([(0, "#22232e", 1), (.08, "#15151d", 1), (1, "#0e0e14", 1)], gid="gBezel")
    lin_grad([(0, "#2c2836", 1), (.4, "#5e5c78", 1), (1, "#4a3d40", 1)], gid="gCabTop")
    lin_grad([(0, "#3a2d30", 1), (1, "#1c1520", 1)], gid="gCabFront")
    lin_grad([(0, "#141c38", 1), (1, "#0a0f20", 1)], gid="gScreenBg")
    lin_grad([(0, "#ffffff", .10), (.35, "#ffffff", .03), (.36, "#ffffff", 0), (1, "#ffffff", 0)], 0, 0, 1, 1, gid="gGlass")
    rad_grad([(0, "#000", 0), (.75, "#000", 0), (1, "#000", .35)], SW / 2, SHh / 2, SW * .62, SHh * .7, gid="gVig")


def build_static():
    if _STATIC:
        return _STATIC
    static_defs()
    _STATIC["bg"] = wall()
    _STATIC["tv"] = tv_body()
    _STATIC["cab"] = cabinet()
    _STATIC["fg"] = foreground()
    lib.static_done()
    return _STATIC


def glass():
    s = [f'<rect x="0" y="0" width="{SW}" height="{SHh}" fill="url(#gVig)"/>',
         f'<rect x="0" y="0" width="{SW}" height="{SHh}" fill="url(#gGlass)"/>']
    # отражение окна комнаты — мягкое пятно справа сверху
    s.append(f'<path d="M700 30 L860 30 L840 230 L690 230Z" fill="#c8d6ff" opacity=".045" {blur(10)}/>')
    s.append(f'<path d="M772 30 L780 30 L764 230 L756 230Z" fill="#000" opacity=".05" {blur(4)}/>')
    return "".join(s)


def topbar():
    return ('<rect x="34" y="26" width="34" height="26" rx="7" fill="#e8413a"/><path d="M46 32 L58 39 L46 46Z" fill="#fff"/>'
            '<rect x="88" y="34" width="60" height="10" rx="5" fill="#2a3352"/><rect x="160" y="34" width="44" height="10" rx="5" fill="#2a3352"/>'
            '<rect x="216" y="34" width="52" height="10" rx="5" fill="#2a3352"/>'
            '<circle cx="890" cy="39" r="13" fill="#2a3352"/><circle cx="930" cy="39" r="13" fill="#f0a24a"/>')


def sel_frame(x, y, w, h, r=12, sc=1.0, op=1.0):
    cx, cy = x + w / 2, y + h / 2
    return (f'<g transform="translate({f(cx)} {f(cy)}) scale({sc:.4f}) translate({f(-cx)} {f(-cy)})" opacity="{op:.3f}">'
            f'<rect x="{f(x - 9)}" y="{f(y - 9)}" width="{f(w + 18)}" height="{f(h + 18)}" rx="{r + 6}" fill="none" stroke="#9fc2ff" stroke-width="10" opacity=".35" {blur(5)}/>'
            f'<rect x="{f(x - 6)}" y="{f(y - 6)}" width="{f(w + 12)}" height="{f(h + 12)}" rx="{r + 4}" fill="none" stroke="#ffffff" stroke-width="5"/></g>')


def jerk(u):
    """рывок сетки: быстро, с маленьким перелётом (0..1 за ~0.16 с)."""
    if u <= 0:
        return 0.0
    return back_out(clamp(u / 0.16), 1.4)


# ───────────── s02: сетка листается рывками, рамка прыгает
SEL02 = [(1, 1), (0, 2), (2, 1), (1, 2), (0, 1)]


def screen_s02(t):
    off = sum(jerk(t - s) for s in SW_S02)
    k = sum(1 for s in SW_S02 if t >= s)
    s = []
    for r, y in enumerate(ROWY):
        for c in range(-1, 9):
            idx = r * 31 + c + 7
            x = GX0 + (c - off) * PITCH
            if x > SW + 10 or x + GW < -10:
                continue
            kd, pal = card_spec(idx)
            s.append(card(x, y, GW, GH, kd, pal, t, bar=(.2 + .6 * ((idx * 37) % 10) / 10) if idx % 3 == 0 else None))
    # рамка: прыжок к новой клетке за 0.09 с
    a = SEL02[max(0, k - 1)] if k else SEL02[0]
    b = SEL02[k] if k < len(SEL02) else SEL02[-1]
    if k:
        u = ease_out(clamp((t - SW_S02[k - 1]) / 0.09))
        a, b = SEL02[k - 1], SEL02[k]
        r_ = a[0] + (b[0] - a[0]) * u
        c_ = a[1] + (b[1] - a[1]) * u
        punch = 1 + 0.06 * math.exp(-max(0, t - SW_S02[k - 1]) * 18)
    else:
        r_, c_ = SEL02[0]
        punch = 1.0
    x = GX0 + c_ * PITCH
    y = ROWY[0] + r_ * (ROWY[1] - ROWY[0])
    s.append(sel_frame(x, y, GW, GH, sc=punch))
    return "".join(s)


# ───────────── s14 / s15: лишние улетают, остаются три; раскрытие первой
GRID = [(r, c) for r in range(3) for c in range(4)]
BATCH = {(0, 0): 0, (0, 1): 0, (0, 2): 0, (0, 3): 0, (1, 1): 1, (1, 3): 1, (2, 2): 1, (2, 0): 2}
KEEP = {(1, 0): 0, (2, 1): 1, (1, 2): 2}
LEFT = (2, 3)
BIG_W, BIG_H = 290, 181
BIG_Y = (SHh - BIG_H) / 2
BIG_X = [(SW - 3 * BIG_W - 2 * 26) / 2 + i * (BIG_W + 26) for i in range(3)]
KEEP_ART = {0: ("car", ("#ff9a5a", "#ffd27a", "#5a3b7a", "#2c2150")),
            1: ("sea", ("#6a7dff", "#b8c4ff", "#2a2f7a", "#141844")),
            2: ("forest", ("#9be15d", "#e9ffb8", "#2f7d4a", "#164a2a"))}


def gspec(r, c):
    if (r, c) in KEEP:
        return KEEP_ART[KEEP[(r, c)]]
    return card_spec(r * 31 + c + 40)


def fly(r, c, t, t0, seed):
    """карточка улетает от центра экрана с ускорением и поворотом; None — уже за экраном."""
    x, y = GX0 + c * PITCH, ROWY[r]
    u = t - t0
    if u <= 0:
        return x, y, 0.0, 1.0
    rs = np.random.RandomState(seed)
    dx, dy = x + GW / 2 - SW / 2, y + GH / 2 - SHh / 2
    n = math.hypot(dx, dy) + 1e-6
    dx, dy = dx / n, dy / n
    dx += rs.uniform(-.25, .25)
    dy += rs.uniform(-.25, .25) - .15
    # маленький замах назад, затем разгон
    back = -14 * math.sin(clamp(u / 0.08) * math.pi)
    d = back + 4200 * max(0.0, u - 0.04) ** 2 + 1100 * max(0.0, u - 0.04)
    rot = rs.uniform(14, 30) * (1 if dx > 0 else -1) * ease_in(clamp(u / 0.35))
    return x + dx * d, y + dy * d, rot, 1 + 0.15 * ease_in(clamp(u / 0.4))


def keep_pos(r, c, t):
    i = KEEP[(r, c)]
    x0, y0 = GX0 + c * PITCH, ROWY[r]
    u = ease_io(clamp((t - (FLY[1] + 0.16)) / 0.5))
    x = x0 + (BIG_X[i] - x0) * u
    y = y0 + (BIG_Y - y0) * u
    w = GW + (BIG_W - GW) * u
    h = GH + (BIG_H - GH) * u
    return x, y, w, h


def screen_s14(t, sel=None, expand=0.0, press=1.0):
    s = []
    for (r, c) in GRID:
        if (r, c) in KEEP or (r, c) == LEFT:
            continue
        b = BATCH[(r, c)]
        x, y, rot, sc = fly(r, c, t, FLY[b] + 0.012 * c, r * 10 + c)
        if x > SW + 400 or x < -GW - 400 or y > SHh + 300 or y < -GH - 300:
            continue
        kd, pal = gspec(r, c)
        s.append(card(x, y, GW, GH, kd, pal, t, rot=rot, scale=sc))
    # последняя лишняя: на «три» вспыхивает и исчезает
    if t < POP + 0.14:
        r, c = LEFT
        x, y = GX0 + c * PITCH, ROWY[r]
        u = t - POP
        if u < 0:
            sc = 1.0
        elif u < 0.05:
            sc = 1 + 0.1 * (u / 0.05)
        else:
            sc = 1.1 * (1 - ease_in(clamp((u - 0.05) / 0.09), 2))
        if sc > 0.02:
            kd, pal = gspec(r, c)
            s.append(card(x, y, GW, GH, kd, pal, t, scale=sc))
    if POP <= t < POP + 0.32:
        u = (t - POP) / 0.32
        cx, cy = GX0 + LEFT[1] * PITCH + GW / 2, ROWY[LEFT[0]] + GH / 2
        for k in range(8):
            a = k * math.pi / 4 + .3
            r0, r1 = 40 + 120 * ease_out(u), 70 + 150 * ease_out(clamp(u * 1.6))
            if r1 - r0 < 4:
                continue
            s.append(line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
                          7 * (1 - u) + 1, "#ffffff", taper=.5, wmin=.3, seed=500 + k))
    # три остающиеся
    order = sorted(KEEP, key=lambda rc: KEEP[rc])
    for rc in order[::-1] if expand > 0 else order:
        i = KEEP[rc]
        x, y, w, h = keep_pos(*rc, t)
        kd, pal = KEEP_ART[i]
        rr = 10
        sc = 1.0
        if i == 0:
            sc = press
            if expand > 0:
                e = expand
                x, y, w, h = x + (0 - x) * e, y + (0 - y) * e, w + (SW - w) * e, h + (SHh - h) * e
                rr = 10 * (1 - e)
        elif expand > 0:
            x += 900 * ease_in(clamp(expand * 1.4), 2) * (1 if i else -1)
        extra = {}
        if kd == "car":
            extra["drive"] = -70 + 46 * max(0.0, t - PLAY - 0.2)
        s.append(card(x, y, w, h, kd, pal, t, r=rr, scale=sc, **extra))
        if i == 0 and sel is not None and expand < 0.6:
            s.append(sel_frame(x, y, w, h, sc=sel[0] * sc, op=sel[1] * clamp(1 - expand * 2)))
    return "".join(s)


def play_icon(t):
    u = t - (PLAY + 0.40)
    if u <= 0:
        return ""
    sc = back_out(clamp(u / 0.22), 2.2) * (1 + 0.02 * math.sin(u * 5))
    cx, cy = SW / 2, SHh / 2
    return (f'<g transform="translate({f(cx)} {f(cy)}) scale({sc:.4f})">'
            f'<circle r="74" fill="#05070f" opacity=".25" {blur(8)} cy="6"/>'
            f'<circle r="68" fill="#ffffff" opacity=".92"/>'
            f'<path d="M-20 -32 Q-24 -36 -18 -36 L34 -4 Q38 0 34 4 L-18 36 Q-24 36 -20 32Z" fill="#14182a" transform="translate(6 0)"/></g>')


# ───────────── сборка кадра
def frame(sid, t):
    st = build_static()
    lib.dyn_begin()
    flash = timing23.switch_flash(t)
    tvl = timing23.tv(t)
    film = smooth(PLAY, PLAY + 0.5, t)
    if sid == "s02":
        content = screen_s02(t)
        a, b = 1.24, 2.84
        u = ease_io((t - a) / (b - a))
        fx, fy, s_ = SCX, SCY + 10, 1.0 + 0.07 * u
    elif sid == "s14":
        content = screen_s14(t)
        u = (t - 22.44) / 2.8
        fx, fy, s_ = SCX + 4 * u, SCY + 10, 1.0 + 0.012 * u
    else:
        selu = t - 25.04
        sel = None
        if selu > 0:
            sel = (back_out(clamp(selu / 0.2), 2.0) * 0 + 1 + 0.25 * (1 - ease_out(clamp(selu / 0.2))), clamp(selu / 0.06))
        pu = t - PLAY
        press = 1.0
        if 0 <= pu < 0.08:
            press = 1 - 0.07 * ease_out(pu / 0.08)
        elif pu >= 0.08:
            press = 0.93 + 0.07 * back_out(clamp((pu - 0.08) / 0.18), 2)
        expand = ease_io(clamp((t - (PLAY + 0.08)) / 0.42))
        content = screen_s14(t, sel=sel, expand=expand, press=press) + play_icon(t)
        # камера: наезд на первую карточку, затем к центру раскрытого экрана
        c0x, c0y = SX0 + BIG_X[0] + BIG_W / 2, SY0 + BIG_Y + BIG_H / 2
        a = ease_io(clamp((t - 24.84) / (PLAY - 24.84)))
        b = ease_io(clamp((t - PLAY - 0.05) / 0.55))
        fx = SCX + (c0x - SCX) * a
        fy = SCY + 10 + (c0y - SCY - 10) * a
        fx += (SCX - fx) * b
        fy += (SCY - fy) * b
        s_ = 1.0 + 0.22 * a
        s_ += (1.03 - s_) * b
    cm = cam(fx, fy, s_)
    fg_cam = cam(fx, fy - 30 * (s_ - 1) * 10, s_ ** 2.4)
    sc = clip_rect(SX0, SY0, SW, SHh, 6)
    glow_c = mix("#7ea6ff", "#ffb27a", film * 0.55)
    gl = lib.rad_grad([(0, glow_c, 1), (.45, glow_c, .45), (1, glow_c, 0)], SCX, SCY - 20, 780, 640)
    gl2 = lib.rad_grad([(0, glow_c, 1), (1, glow_c, 0)], SCX, 1250, 560, 120)
    glow_op = clamp(0.30 * tvl, 0, 0.6)
    body = [f'<g transform="{cm}">', st["bg"],
            f'<rect x="-500" y="-500" width="2080" height="2900" fill="url(#{gl})" opacity="{glow_op:.3f}" style="mix-blend-mode:screen"/>',
            st["cab"],
            f'<rect x="-400" y="1188" width="1880" height="120" fill="url(#{gl2})" opacity="{clamp(.35 * tvl, 0, .7):.3f}" style="mix-blend-mode:screen"/>',
            st["tv"],
            f'<g clip-path="url(#{sc})"><g transform="translate({SX0} {SY0})">',
            f'<rect x="0" y="0" width="{SW}" height="{SHh}" fill="url(#gScreenBg)"/>',
            topbar() if sid != "s15" or t < PLAY + 0.3 else "",
            content,
            f'<rect x="0" y="0" width="{SW}" height="{SHh}" fill="#dfe8ff" opacity="{0.07 * flash:.3f}"/>',
            glass(), "</g></g>",
            "</g>"]
    if sid == "s15":
        # затылок не пропадает: наезд уносит его вниз за край кадра (параллакс), после наезда он уже за кадром
        a = ease_in(clamp((t - 24.84) / (PLAY - 24.84)), 1.6)
        fg_cam = f"translate(0 {900 * a:.2f}) " + cam(SCX - 40 * a, SCY + 10, (1.0 + 0.22 * a) ** 2.4)
        if a < 0.999:
            body.append(f'<g transform="{fg_cam}">{st["fg"]}</g>')
    else:
        body.append(f'<g transform="{fg_cam}">{st["fg"]}</g>')
    return svg("".join(body))


if __name__ == "__main__":
    import sys
    open("/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/tv_test.svg", "w").write(frame(sys.argv[1], float(sys.argv[2])))
