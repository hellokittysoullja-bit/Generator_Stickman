"""Сцена brain (s08, s09): мультяшный мозг (сбоку, объём и тень, без лица) и стеклянная колба-шкала с жидкостью
«дофамин» (значок-капля на колбе, без букв). По дорожке к мозгу прыжками едет подарок — шкала растёт и светится
(до 12.9). s09: подарок встаёт, на «пришла» (13.92) крышка отлетает, внутри звёздочка; шкала падает почти в ноль
к «нет» (15.36), свечение гаснет, мозг вздрагивает. Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, fill_d,
                 line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg)

ARRIVE = 12.95      # подарок доехал
OPEN = 13.92        # «пришла»
EMPTY = 15.36       # «нет»
BCX, BCY = 400, 600  # центр большого мозга
FX, FY0, FY1, FR = 850, 380, 1060, 92   # колба: центр x, верх, низ (дно — полукруг), радиус
FLOOR = 1010
_ST = {}


# ───────────────────────── уровень дофамина
def level(t):
    if t < OPEN + 0.03:
        u = ease_io((t - 10.25) / (ARRIVE - 10.25))
        lv = 0.12 + 0.80 * u
        if t > ARRIVE - 0.3:   # у верха: лёгкое «подрагивание» в ожидании
            lv += 0.012 * math.sin(t * 19) * smooth(ARRIVE - 0.3, ARRIVE, t)
        return lv
    u = clamp((t - OPEN - 0.03) / (EMPTY - OPEN - 0.03))
    top = 0.92
    return top - (top - 0.05) * (u ** 1.6) if u < 1 else 0.05 + 0.006 * math.sin((t - EMPTY) * 9) * math.exp(-(t - EMPTY) * 3)


def glow(t):
    lv = level(t)
    g = clamp((lv - 0.1) / 0.82)
    if t > OPEN:
        g *= 1 - smooth(OPEN, EMPTY + 0.1, t) * 0.95
    return g


# ───────────────────────── фон
def background():
    s = []
    lin_grad([(0, "#1f2747", 1), (.55, "#2c3a66", 1), (1, "#33457a", 1)], 0, 0, 0, 1, gid="gWallB")
    lin_grad([(0, "#3a4c82", 1), (1, "#25305a", 1)], 0, 0, 0, 1, gid="gFloorB")
    s.append(f'<rect x="-400" y="-400" width="{W + 800}" height="{FLOOR + 400}" fill="url(#gWallB)"/>')
    s.append(f'<rect x="-400" y="{FLOOR}" width="{W + 800}" height="{H - FLOOR + 600}" fill="url(#gFloorB)"/>')
    # мягкое пятно света за мозгом и за колбой
    rad_grad([(0, "#5b6fae", .9), (.6, "#40538d", .35), (1, "#40538d", 0)], BCX, BCY, 470, 420, gid="gSpotB")
    s.append(f'<rect x="-400" y="-400" width="{W + 800}" height="{FLOOR + 400}" fill="url(#gSpotB)"/>')
    # линия пола и пара досок
    s.append(line([(-100, FLOOR), (W + 100, FLOOR)], 4.5, INK, taper=.1, wmin=.8, seed=5))
    for k, y in enumerate([1090, 1210, 1370, 1580]):
        s.append(line([(-100, y), (W + 100, y + 6)], 2.4, "#1c2546", taper=.2, wmin=.6, seed=10 + k, op=.8))
    # плинтус
    s.append(blob([(-100, FLOOR - 26), (W + 100, FLOOR - 26), (W + 100, FLOOR), (-100, FLOOR)], "#273260"))
    s.append(line([(-100, FLOOR - 26), (W + 100, FLOOR - 26)], 2.6, INK, taper=.1, wmin=.8, seed=6, op=.8))
    return "".join(s)


def dust(t):
    """Пылинки в луче: медленно плывут — фон живой с первого кадра."""
    rs = np.random.RandomState(4)
    s = []
    for k in range(26):
        x0, y0 = rs.uniform(-50, W + 50), rs.uniform(80, FLOOR - 40)
        sp, ph, r = rs.uniform(10, 26), rs.uniform(0, 6.28), rs.uniform(2.2, 4.5)
        x = x0 + 30 * math.sin(t * 0.6 + ph)
        y = (y0 - sp * (t - 10)) % (FLOOR - 60) + 40
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#c9d6ff" opacity="{.18 + .14 * math.sin(t * 2 + ph):.3f}"/>')
    return "".join(s)


# ───────────────────────── дорожка
P0, PC, P1 = (520, 1640), (150, 1250), (BCX - 90, 1062)


def road_pt(u):
    u = clamp(u)
    x = (1 - u) ** 2 * P0[0] + 2 * (1 - u) * u * PC[0] + u * u * P1[0]
    y = (1 - u) ** 2 * P0[1] + 2 * (1 - u) * u * PC[1] + u * u * P1[1]
    return x, y


def road():
    s = []
    us = np.linspace(-0.15, 1.08, 60)
    C = []
    for u in us:
        if u < 0:
            a, b = road_pt(0), road_pt(0.02)
            C.append((a[0] + (a[0] - b[0]) * (-u / 0.02), a[1] + (a[1] - b[1]) * (-u / 0.02)))
        elif u > 1:
            a, b = road_pt(1), road_pt(0.98)
            C.append((a[0] + (a[0] - b[0]) * ((u - 1) / 0.02), a[1] + (a[1] - b[1]) * ((u - 1) / 0.02)))
        else:
            C.append(road_pt(u))
    C = np.array(C)
    T = np.gradient(C, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    wd = np.interp(us, [-0.15, 1.08], [260, 110])
    L = C + N * wd[:, None] / 2
    R = C - N * wd[:, None] / 2
    poly = [tuple(p) for p in L] + [tuple(p) for p in R[::-1]]
    sh = [(x + 0, y + 10) for x, y in poly]
    s.append(blob(sh, "#1b2347", .9))
    inner = blob([tuple(p) for p in (C - N * wd[:, None] * .5)] + [tuple(p) for p in (C - N * wd[:, None] * .18)][::-1], "#7d6fb0", .9)
    s.append(shape(poly, "#9a8fd0", inner, w=4.2, seed=31))
    _ST["road_c"] = C
    _ST["road_u"] = us
    return "".join(s)


def road_lights(t):
    """Огоньки по середине дорожки перед подарком загораются друг за другом, пока он едет."""
    C, us = _ST["road_c"], _ST["road_u"]
    s = []
    gp = gift_u(t)
    for k, u in enumerate(np.linspace(0.05, 1.0, 12)):
        x, y = road_pt(u)
        sc = 1.15 - 0.4 * u
        on = smooth(gp - 0.02, gp + 0.10, u) * (1 - smooth(gp + 0.30, gp + 0.45, u))  # волна света впереди подарка
        on = max(on, 0.0) * (1 - smooth(OPEN + 0.2, EMPTY, t))
        col = mix("#cbc4ef", "#ffe58a", on)
        s.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(12 * sc)}" ry="{f(5 * sc)}" fill="{col}"/>')
        if on > 0.05:
            s.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(30 * sc)}" ry="{f(14 * sc)}" fill="#ffd45a" opacity="{.5 * on:.3f}" {blur(6)}/>')
    return "".join(s)


# ───────────────────────── мозг
def brain_outline():
    pts = []
    rs = np.random.RandomState(7)
    ph = rs.uniform(0, 6.28, 3)
    n = 44
    for i in range(n):
        a = 2 * math.pi * i / n
        rx, ry = 215, 150
        # чуть приплюснутый низ, лобная доля вперёд (влево)
        r = 1 + 0.035 * math.sin(9 * a + ph[0]) + 0.02 * math.sin(14 * a + ph[1])
        x = math.cos(a) * rx * r
        y = math.sin(a) * ry * r
        if y > 0:
            y *= 0.82
            x *= 1 - 0.08 * math.sin(a)
        if x < 0 and y < 0:
            x *= 1.04
        pts.append((BCX + x, BCY + y))
    return pts


CBL = [(BCX + 70, BCY + 100), (BCX + 150, BCY + 82), (BCX + 205, BCY + 110), (BCX + 200, BCY + 150), (BCX + 150, BCY + 170),
       (BCX + 90, BCY + 160), (BCX + 60, BCY + 130)]
STEM = [(BCX + 40, BCY + 110), (BCX + 100, BCY + 118), (BCX + 92, BCY + 200), (BCX + 82, BCY + 270, 1), (BCX + 40, BCY + 270, 1),
        (BCX + 48, BCY + 190)]


def gyri():
    """Извилины: петляющие борозды (меандр вдоль контура доли, концы загнуты крючком) — тёмная линия + светлая кромка."""
    rs = np.random.RandomState(12)
    s = []
    seeds = []
    for ring, (rx, ry, n) in enumerate([(178, 118, 9), (128, 82, 7), (76, 46, 4)]):
        a0 = rs.uniform(0, 6.28)
        for k in range(n):
            seeds.append((ring, rx, ry, a0 + 2 * math.pi * k / n + rs.uniform(-.15, .15)))
    for j, (ring, rx, ry, a) in enumerate(seeds):
        span = rs.uniform(0.38, 0.62) * (1.0 if ring < 2 else 1.3)
        amp = rs.uniform(7, 12)
        m = 18
        pts = []
        for i in range(m + 1):
            u = i / m
            aa = a + span * u
            w = amp * math.sin(u * math.pi * rs.uniform(2.2, 3.2) + j)
            rr = 1 + w / max(rx, 1)
            x, y = math.cos(aa) * rx * rr, math.sin(aa) * ry * rr
            if y > 0:
                y *= 0.85
            pts.append((BCX + x, BCY + y))
        # крючок на конце — внутрь
        ex, ey = pts[-1]
        ix, iy = BCX - ex, BCY - ey
        L = math.hypot(ix, iy) + 1e-6
        pts.append((ex + ix / L * 18 + rs.uniform(-6, 6), ey + iy / L * 18))
        s.append(line([(x + 1.5, y + 4) for x, y in pts], 4.0, "#ffdbe4", seed=200 + j, op=.6, taper=.6))
        s.append(line(pts, 5.4, "#a8466b", seed=300 + j, taper=.7, wmin=.15))
    # латеральная (сильвиева) борозда
    s.append(line([(BCX - 120, BCY + 60), (BCX - 40, BCY + 28), (BCX + 40, BCY + 22), (BCX + 110, BCY - 6)], 6.5, "#8e3358", seed=401))
    # центральная борозда сверху вниз
    s.append(line([(BCX + 10, BCY - 148), (BCX - 6, BCY - 90), (BCX + 14, BCY - 40), (BCX + 2, BCY + 10)], 5.5, "#8e3358", seed=402))
    return "".join(s)


def brain(t, sad):
    s = []
    base = mix("#f6a9bc", "#c99aac", sad)
    shc = mix("#dd7e9b", "#a87a8d", sad)
    deep = mix("#b9587d", "#8b6276", sad)
    hi = mix("#ffd7e1", "#e4ccd6", sad)
    # стебель и мозжечок — сзади
    s.append(shape(STEM, mix("#e98fa8", "#b88c9c", sad),
                   blob([(BCX + 70, BCY + 112), (BCX + 100, BCY + 118), (BCX + 92, BCY + 200), (BCX + 82, BCY + 270), (BCX + 66, BCY + 270)], shc, .9),
                   w=4.6, seed=51))
    cb_inner = blob([(BCX + 90, BCY + 140), (BCX + 200, BCY + 130), (BCX + 200, BCY + 150), (BCX + 150, BCY + 170), (BCX + 90, BCY + 160)], deep, .55)
    for k in range(4):
        y = BCY + 105 + k * 16
        cb_inner += line([(BCX + 75 + k * 6, y), (BCX + 140, y - 6 + k * 2), (BCX + 198 - k * 4, y + 4 + k * 3)], 3.4, deep, seed=60 + k)
    s.append(shape(CBL, mix("#ef9bb0", "#bf93a3", sad), cb_inner, w=4.6, seed=52))
    # большие полушария
    pts = brain_outline()
    inner = []
    inner.append(blob([(BCX - 240, BCY + 30), (BCX - 60, BCY + 90), (BCX + 120, BCY + 40), (BCX + 240, BCY - 40),
                       (BCX + 240, BCY + 200), (BCX - 240, BCY + 200)], shc, .95))
    inner.append(blob([(BCX - 200, BCY + 120), (BCX + 60, BCY + 140), (BCX + 240, BCY + 60), (BCX + 240, BCY + 200),
                       (BCX - 200, BCY + 200)], deep, .55))
    inner.append(blob(ellipse_pts(BCX - 90, BCY - 85, 95, 42, 14, rot=-14), hi, .8))
    inner.append(gyri())
    inner.append(blob(ellipse_pts(BCX - 120, BCY - 98, 34, 13, 10, rot=-22), "#ffffff", .75))
    s.append(shape(pts, base, "".join(inner), w=6.2, seed=53))
    return "".join(s)


# ───────────────────────── колба
def flask_pts(pad=0.0):
    """Пробирка: прямые бока (с промежуточными точками — сплайн не выгибается), плоский верх под кантом, дно — полукруг."""
    r = FR + pad
    ytop, ybot = FY0 + 40, FY1 - FR
    pts = [(FX - r, ytop, 1)]
    for v in np.linspace(0, 1, 6)[1:-1]:
        pts.append((FX - r, ytop + (ybot - ytop) * v))
    for k in range(0, 13):
        a = math.pi * k / 12
        pts.append((FX - r * math.cos(a), ybot + r * math.sin(a)))
    for v in np.linspace(1, 0, 6)[1:-1]:
        pts.append((FX + r, ytop + (ybot - ytop) * v))
    pts.append((FX + r, ytop, 1))
    return pts


def flask_back():
    s = []
    # подставка
    s.append(blob(ellipse_pts(FX + 10, FLOOR + 74, 150, 22, 14), "#141b38", .8, blur(5)))
    st = [(FX - 140, FLOOR + 20), (FX + 140, FLOOR + 20), (FX + 150, FLOOR + 66, 1), (FX - 150, FLOOR + 66, 1)]
    s.append(shape(st, "#8a5a3a", blob([(FX - 150, FLOOR + 50), (FX + 150, FLOOR + 50), (FX + 150, FLOOR + 66), (FX - 150, FLOOR + 66)], "#6b4128", .9),
                   w=4.4, seed=71))
    # стойки держателя
    for x in (FX - 120, FX + 120):
        s.append(shape(rect_pts(x - 9, FY0 + 330, x + 9, FLOOR + 24), "#9c6a45", blob(rect_pts(x + 2, FY0 + 330, x + 9, FLOOR + 24), "#6b4128", .9),
                       w=3.4, seed=72 + x))
    return "".join(s)


def flask_glass_bg():
    pts = flask_pts()
    lin_grad([(0, "#5e6fa8", 1), (.5, "#7184bd", 1), (1, "#4f5f98", 1)], 0, 0, 1, 0, gid="gGlass")
    return f'<path d="{fill_d(pts)}" fill="url(#gGlass)"/>'


def liquid(t):
    lv = level(t)
    g = glow(t)
    pts = flask_pts()
    c = lib.clip_of(pts)
    y_top = FY1 - (FY1 - FY0 - 50) * lv
    # поверхность с волной
    sl = []
    for k in range(17):
        x = FX - FR - 10 + k * (2 * FR + 20) / 16
        y = y_top + 6 * math.sin(k * 0.9 + t * 7.5) * (0.4 + 0.6 * g) + 3 * math.sin(k * 1.7 - t * 4)
        sl.append((x, y))
    body = sl + [(FX + FR + 10, FY1 + 20, 1), (FX - FR - 10, FY1 + 20, 1)]
    col = mix("#d68a2a", "#ffc23a", g)
    col2 = mix("#b06a1e", "#ff9a26", g)
    hi = mix("#e8b060", "#fff1a8", g)
    s = [f'<g clip-path="url(#{c})">']
    s.append(blob(body, col))
    right = [(x, y) for x, y in sl if x >= FX + 34]
    s.append(blob([(FX + 34, right[0][1] + 2, 1)] + right[1:-1] + [(FX + FR + 10, right[-1][1], 1), (FX + FR + 10, FY1 + 20, 1), (FX + 40, FY1 + 20, 1)],
                  col2, .9))
    # пузырьки
    rs = np.random.RandomState(9)
    for k in range(14):
        x0 = FX + rs.uniform(-FR + 20, FR - 20)
        sp = rs.uniform(90, 170)
        ph = rs.uniform(0, 1)
        span = FY1 - y_top
        if span < 30:
            continue
        y = FY1 - 20 - ((t * sp / span + ph) % 1) * (span - 10)
        r = rs.uniform(4, 9) * (0.5 + 0.5 * g)
        x = x0 + 5 * math.sin(t * 5 + k)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="none" stroke="{hi}" stroke-width="2.6"/>')
    # светлая кромка поверхности
    s.append(line(sl[1:-1], 7, hi, taper=.4, wmin=.5, seed=81))
    s.append(line(sl[1:-1], 2.6, INK, taper=.2, wmin=.6, seed=82, op=.8))
    s.append("</g>")
    return "".join(s), y_top


def flask_front(t):
    pts = flask_pts()
    s = []
    # деления шкалы слева
    for k in range(6):
        y = FY1 - 40 - k * 105
        L = 46 if k % 2 == 0 else 28
        s.append(line([(FX - FR + 8, y), (FX - FR + 8 + L, y)], 4.2, "#e9eeff", taper=.2, wmin=.7, seed=90 + k, op=.95))
    # блики стекла
    s.append(line([(FX - FR + 30, FY0 + 70), (FX - FR + 28, FY1 - FR - 20)], 11, "#ffffff", taper=.7, seed=95, op=.55))
    s.append(line([(FX + FR - 22, FY0 + 90), (FX + FR - 22, FY0 + 260)], 6, "#ffffff", taper=.7, seed=96, op=.45))
    # кант горлышка
    lip = [(FX - FR - 18, FY0 + 22), (FX + FR + 18, FY0 + 22), (FX + FR + 18, FY0 + 46, 1), (FX - FR - 18, FY0 + 46, 1)]
    s.append(f'<path d="{lib.ink_closed(pts, 6, seed=97)}" fill="{INK}"/>')
    s.append(shape(lip, "#8fa1d8", line([(FX - FR - 6, FY0 + 30), (FX + FR, FY0 + 30)], 4, "#ffffff", seed=98, op=.7), w=4.6, seed=99))
    # хомут держателя
    clamp_ = rect_pts(FX - 128, FY0 + 330, FX + 128, FY0 + 362, 6)
    s.append(shape(clamp_, "#b07c52", blob(rect_pts(FX - 128, FY0 + 350, FX + 128, FY0 + 362), "#7a4c2e", .9), w=4.2, seed=100))
    # значок: круглая бирка с каплей-молекулой
    bx, by = FX + 6, FY0 + 170
    g = glow(t)
    s.append(shape(ellipse_pts(bx, by, 50, 50, 18), "#f7f2e8", blob(ellipse_pts(bx + 10, by + 14, 46, 40, 14), "#ddd3c2", .8), w=4.4, seed=101))
    drop = [(bx, by - 32, 1), (bx + 20, by - 4), (bx + 24, by + 12), (bx + 12, by + 28), (bx - 12, by + 28), (bx - 24, by + 12), (bx - 20, by - 4)]
    s.append(shape(drop, mix("#d68a2a", "#ff9f1c", g), blob(ellipse_pts(bx - 8, by + 4, 6, 10, 8, rot=20), "#ffe7a6", .9), w=3.4, seed=102))
    return "".join(s)


def flask_glow(t, y_top):
    g = glow(t)
    if g < 0.01:
        return ""
    pul = 1 + 0.08 * math.sin(t * 6)
    gid = rad_grad([(0, "#ffd65a", .75), (.45, "#ffb02a", .35), (1, "#ff9a1c", 0)], FX, (y_top + FY1) / 2, 260 * pul, 420 * pul)
    return (f'<rect x="{FX - 400}" y="{FY0 - 300}" width="800" height="{FY1 - FY0 + 600}" fill="url(#{gid})" opacity="{g:.3f}" '
            f'style="mix-blend-mode:screen"/>')


def rays(t, g):
    """Лучики вокруг колбы, когда шкала высоко (тот же рисованный штрих)."""
    if g < 0.25:
        return ""
    s = []
    for k in range(8):
        a = -math.pi / 2 + (k - 3.5) * 0.36
        ph = (t * 1.8 + k * 0.37) % 1
        r0 = 150 + 50 * ph
        L = 46 * (1 - ph) * g
        cx, cy = FX, FY0 + 180
        x0, y0 = cx + math.cos(a) * r0, cy + math.sin(a) * r0 * 1.4
        x1, y1 = cx + math.cos(a) * (r0 + L), cy + math.sin(a) * (r0 + L) * 1.4
        if L > 4:
            s.append(line([(x0, y0), (x1, y1)], 7, "#ffe27a", taper=.5, seed=110 + k))
    return "".join(s)


# ───────────────────────── подарок
def gift_u(t):
    u = clamp((t - 10.0) / (ARRIVE - 10.0))
    return 1 - (1 - u) ** 1.35


def gift(t):
    u = gift_u(t)
    x, y = road_pt(u)
    sc = 1.25 - 0.32 * u
    s = []
    # прыжки по дороге
    hops = 9
    ph = u * hops
    hop = abs(math.sin(math.pi * ph)) * (1 - smooth(0.93, 1.0, u))
    lift = 46 * hop * sc
    # приземление: сплющивание
    land = math.exp(-((ph % 1) * 9)) * (1 - smooth(0.93, 1.0, u))
    if t > ARRIVE:   # встал и пружинит
        e = t - ARRIVE
        land = 0.6 * math.exp(-e * 6) * math.cos(e * 22)
    sq = 1 - 0.12 * land
    st = 1 + 0.10 * land
    tilt = 6 * math.sin(math.pi * ph * 2) * (1 - smooth(0.9, 1.0, u))
    # подарок «ждёт» — подпрыгивает от нетерпения перед открытием
    if ARRIVE + 0.25 < t < OPEN:
        e = (t - ARRIVE - 0.25) / (OPEN - ARRIVE - 0.25)
        lift += 14 * abs(math.sin(e * math.pi * 3)) * sc
    # тень
    s.append(blob(ellipse_pts(x + 6, y + 4, 92 * sc * (1 - .35 * hop), 20 * sc * (1 - .35 * hop), 14), "#141b38", .7, blur(4)))
    inner = gift_box(t)
    s.append(f'<g transform="translate({f(x)} {f(y - lift)}) rotate({f(tilt)}) scale({f(sc * st)} {f(sc * sq)})">{inner}</g>')
    return "".join(s)


GW_, GH_, GD = 150, 112, 46   # ширина, высота коробки, глубина (верх-право)


def gift_box(t):
    """Коробка в 3/4: фронт, правый бок, крышка (отдельно — улетает на «пришла»), лента, бант. Начало координат — низ-центр фронта."""
    s = []
    x0, x1, y0, y1 = -GW_ / 2, GW_ / 2, -GH_, 0
    dx, dy = GD * .75, -GD * .55
    red, red_sh, red_dk = "#e8474f", "#b8303b", "#8e2230"
    gold, gold_sh = "#ffd04a", "#d99a1c"
    opened = t >= OPEN
    # бок
    side = [(x1, y0, 1), (x1 + dx, y0 + dy, 1), (x1 + dx, y1 + dy, 1), (x1, y1, 1)]
    s.append(shape(side, red_sh, blob([(x1 + 14, y0 + dy * .3), (x1 + 26, y0 + dy * .75), (x1 + 26, y1 + dy * .75), (x1 + 14, y1 + dy * .3)], gold_sh), w=4, seed=121))
    # верх (виден, когда крышки нет — тёмное нутро)
    if opened:
        top = [(x0, y0, 1), (x1, y0, 1), (x1 + dx, y0 + dy, 1), (x0 + dx, y0 + dy, 1)]
        s.append(shape(top, "#5a1620", blob([(x0, y0), (x1, y0), (x1 + dx * .4, y0 + dy * .4), (x0 + dx * .4, y0 + dy * .4)], "#3a0c14"), w=4, seed=122))
        s.append(star(t))
    # фронт
    front = [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]
    fin = blob([(x0, y1 - 22), (x1, y1 - 30), (x1, y1), (x0, y1)], red_sh, .8) + \
        blob([(-14, y0), (14, y0), (14, y1), (-14, y1)], gold) + blob([(6, y0), (14, y0), (14, y1), (6, y1)], gold_sh) + \
        line([(x0 + 10, y0 + 12), (x0 + 10, y1 - 30)], 5, "#ff8a8f", seed=124, op=.8)
    s.append(shape(front, red, fin, w=4.4, seed=123))
    s.append(line([(-14, y0 + 2), (-14, y1 - 2)], 2.6, INK, taper=.1, wmin=.8, seed=125, op=.85))
    s.append(line([(14, y0 + 2), (14, y1 - 2)], 2.6, INK, taper=.1, wmin=.8, seed=126, op=.85))
    # крышка
    lid = lid_art(red, red_sh, gold, gold_sh)
    if not opened:
        s.append(lid)
    else:
        e = t - OPEN
        # крышка отлетает вверх-влево с вращением и падает за кадр
        lx = -950 * e
        ly = -380 * e + 700 * e * e
        rot = -260 * e
        if ly < 600:
            s.append(f'<g transform="translate({f(lx)} {f(ly)}) rotate({f(rot)} 0 {y0 - 20})">{lid}</g>')
        s.append(pop_lines(e))
    return "".join(s)


def lid_art(red, red_sh, gold, gold_sh):
    x0, x1, y0 = -GW_ / 2 - 10, GW_ / 2 + 10, -GH_
    dx, dy = GD * .75, -GD * .55
    s = []
    rim_f = [(x0, y0 - 24, 1), (x1, y0 - 24, 1), (x1, y0 + 6, 1), (x0, y0 + 6, 1)]
    rim_s = [(x1, y0 - 24, 1), (x1 + dx, y0 - 24 + dy, 1), (x1 + dx, y0 + 6 + dy, 1), (x1, y0 + 6, 1)]
    topf = [(x0, y0 - 24, 1), (x1, y0 - 24, 1), (x1 + dx, y0 - 24 + dy, 1), (x0 + dx, y0 - 24 + dy, 1)]
    cxm = (x0 + x1) / 2
    s.append(shape(rim_s, red_sh, "", w=4, seed=131))
    s.append(shape(topf, "#f2666d", blob([(cxm - 14, y0 - 24), (cxm + 14, y0 - 24), (cxm + 14 + dx, y0 - 24 + dy), (cxm - 14 + dx, y0 - 24 + dy)], gold) +
                   blob([(x0, y0 - 24), (x1, y0 - 24), (x1 + dx * .3, y0 - 24 + dy * .3), (x0 + dx * .3, y0 - 24 + dy * .3)], "#ff8a8f", .6), w=4, seed=132))
    s.append(shape(rim_f, red, blob([(-14, y0 - 24), (14, y0 - 24), (14, y0 + 6), (-14, y0 + 6)], gold) + blob([(x0, y0 - 4), (x1, y0 - 4), (x1, y0 + 6), (x0, y0 + 6)], red_sh, .8),
                   w=4.2, seed=133))
    # бант: две петли и хвостики
    bx, by = dx / 2, y0 - 24 + dy / 2
    for sg in (-1, 1):
        loop = [(bx, by), (bx + sg * 30, by - 40), (bx + sg * 58, by - 34), (bx + sg * 54, by - 8), (bx + sg * 22, by + 2)]
        s.append(shape(loop, gold, blob([(bx + sg * 10, by - 6), (bx + sg * 40, by - 18), (bx + sg * 50, by - 10), (bx + sg * 22, by + 2)], gold_sh, .9),
                       w=3.8, seed=140 + sg))
    s.append(shape(ellipse_pts(bx, by - 4, 13, 11, 10), "#ffe27a", "", w=3.6, seed=143))
    return "".join(s)


def star(t):
    e = t - OPEN
    k = back_out(clamp(e / 0.32), 2.2)
    y = -GH_ - 40 - 150 * ease_out(e / 0.4) + 6 * math.sin(e * 6)
    sc = 0.25 + 0.75 * k
    rot = 20 * math.sin(e * 3)
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 74 if i % 2 == 0 else 33
        pts.append((r * math.cos(a), r * math.sin(a), 1))
    inner = blob([(0, -4), (60, 6), (44, 72), (0, 44)], "#e6a81c", .8) + blob(ellipse_pts(-18, -20, 13, 7, 8, rot=-30), "#ffffff", .8)
    return f'<g transform="translate(18 {f(y)}) rotate({f(rot)}) scale({f(sc)})">{shape(pts, "#ffd84a", inner, w=4.6, seed=150)}</g>'


def pop_lines(e):
    if e > 0.45:
        return ""
    s = []
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.42
        r0 = 70 + 160 * ease_out(e / 0.45)
        L = 50 * (1 - e / 0.45)
        cx, cy = 18, -GH_ - 60
        s.append(line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + L), cy + math.sin(a) * (r0 + L))],
                      7, "#ffe58a", taper=.5, seed=160 + k))
    return "".join(s)


# ───────────────────────── сборка
def build_static():
    if _ST.get("done"):
        return _ST
    _ST["bg"] = background()
    _ST["road"] = road()
    _ST["fback"] = flask_back()
    _ST["fglass"] = flask_glass_bg()
    _ST["done"] = True
    lib.static_done()
    return _ST


def frame(sid, t):
    st = build_static()
    lib.dyn_begin()
    g = glow(t)
    sad = smooth(EMPTY - 0.5, EMPTY + 0.25, t) * 0.75
    # мозг: дыхание, предвкушение (лёгкие подскоки, пока растёт шкала), вздрагивание на «нет»
    br = 1 + 0.012 * math.sin(t * 2.6)
    bdy = -8 * g * abs(math.sin(t * 5.2)) * (1 - smooth(OPEN - 0.1, OPEN + 0.3, t))
    sh = 0.0
    if t > EMPTY - 0.04:
        e = t - EMPTY + 0.04
        sh = 16 * math.exp(-e * 7) * math.sin(e * 55)
    sq = 1.0
    if t > EMPTY - 0.04:
        e = t - EMPTY + 0.04
        sq = 1 - 0.06 * math.exp(-e * 6) * math.cos(e * 30)
    btf = f"translate({f(BCX + sh)} {f(BCY + 140 + bdy)}) scale({f(1.14 * br / sq ** .5)} {f(1.14 * br * sq)}) translate({-BCX} {-(BCY + 140)})"
    bglow = ""
    if g > 0.02:
        gid = rad_grad([(0, "#ffcf6a", .55), (.6, "#ff9e4a", .18), (1, "#ff9e4a", 0)], BCX, BCY, 330, 260)
        bglow = f'<rect x="-200" y="200" width="1200" height="900" fill="url(#{gid})" opacity="{g * .9:.3f}" style="mix-blend-mode:screen"/>'
    # тень мозга на полу
    bshadow = blob(ellipse_pts(BCX + 50, FLOOR + 40, 150 * (1 + .1 * math.sin(t * 2.6)), 22, 14), "#141b38", .55, blur(8))
    liq, y_top = liquid(t)
    # «дзынь»-штрихи у мозга, пока он предвкушает
    zing = ""
    if g > 0.3 and t < OPEN + 0.2:
        for k in range(3):
            ph = (t * 2.2 + k / 3) % 1
            a = -2.3 + k * 0.45
            r0 = 250 + 40 * ph
            L = 40 * (1 - ph)
            cx, cy = BCX - 10, BCY - 10
            zing += line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0 * .8), (cx + math.cos(a) * (r0 + L), cy + math.sin(a) * (r0 + L) * .8)],
                         7, "#ffe27a", taper=.5, seed=170 + k)
    # «капли пота» / тусклые черты после «нет»: три штриха испуга над мозгом
    jolt = ""
    if t > EMPTY - 0.04:
        e = t - EMPTY + 0.04
        a_ = clamp(e / 0.12) * (1 - smooth(0.5, 0.75, e))
        if a_ > 0.02:
            for k, (dx, dy, ang) in enumerate([(-150, -200, -120), (0, -235, -90), (150, -200, -60)]):
                a = math.radians(ang)
                x0, y0 = BCX + dx, BCY + dy
                L = 34 * a_
                jolt += line([(x0, y0), (x0 + math.cos(a) * L, y0 + math.sin(a) * L)], 7, "#e9eeff", taper=.5, seed=180 + k)
    art = (st["bg"] + dust(t) + st["road"] + road_lights(t) + bshadow + st["fback"] + flask_glow(t, y_top) + st["fglass"] + liq +
           flask_front(t) + rays(t, g) + f'<g transform="{btf}">{brain(t, sad)}</g>' + bglow + zing + jolt + gift(t))
    if sid == "s08":
        u = ease_io((t - 10.4) / 2.7)
        cm = cam(580, 806 + 4 * u, 1.17 + 0.08 * u)
    else:
        csh = 0.0
        if t > EMPTY - 0.04:
            e = t - EMPTY + 0.04
            csh = 9 * math.exp(-e * 8) * math.sin(e * 60)
        u = (t - 12.7) / 3.4
        cm = cam(580 + csh, 810 + 2 * u, 1.25 + 0.02 * u)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{art}</g>')
