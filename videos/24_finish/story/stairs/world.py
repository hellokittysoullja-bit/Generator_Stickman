"""Мир сцены stairs: сумеречное небо, облака слоями с параллаксом, лестница из гигантских блоков отрывного календаря,
площадка с кубком и флажком, новая лестница из тумана и дальние пролёты к новому флажку.

Мир: y вверх — отрицательный. Ступень — блок календаря: лицевая сторона — лист (переплёт с кольцами, красная шапка,
крупное число дня), верх — торец стопки листов (на нём стоит Дима), ниже листа — стопка страниц, уходящая в туман.
Глубина — косая проекция: верх ступени уходит на (DX, -DD)."""
import math

import numpy as np

import lib
from lib import INK, blob, ellipse_pts, f, line, shape

DX, DD = 34.0, 40.0
CARD_K = 1.32            # высота листа в долях подъёма

PAPER, PAPER_SH, PAGE_EDGE = "#f8f3e8", "#e2d6c0", "#d9ccb2"
HEAD_RED, HEAD_RED_SH, BIND = "#d8483c", "#ad3229", "#3b2c3a"
TREAD, TREAD_SH = "#efe4cc", "#d8c8a8"
SKY_INK = "#3a2f55"


class Flight:
    """Пролёт: n ступеней от (x0, y0) — левый передний верхний угол первой ступени; dirx = +1 вправо, -1 влево."""

    def __init__(self, x0, y0, n, D, R, dirx=1, day0=1, first=0):
        self.x0, self.y0, self.n, self.D, self.R, self.dirx, self.day0, self.first = x0, y0, n, D, R, dirx, day0, first

    def step(self, i):
        """левый край x, верх y, ширина"""
        if self.dirx > 0:
            return self.x0 + i * self.D, self.y0 - i * self.R, self.D
        return self.x0 - (i + 1) * self.D, self.y0 - i * self.R, self.D

    def contact(self, i, u=0.36):
        """точка опоры на средней глубине ступени i: (x лодыжки по подошве, y подошвы)"""
        x, y, w = self.step(i)
        if self.dirx > 0:
            return x + DX / 2 + u * w, y - DD / 2
        return x + DX / 2 + (1 - u) * w, y - DD / 2


def day_color(day):
    return HEAD_RED if day % 7 else "#d8483c"


def block(x, y, w, R, day, seed, rise=0.0, tint=None, side=False, ink_w=4.2, num=True, col_len=3.6, star=False):
    """Блок-ступень. rise — сдвиг вниз (вырастает из тумана). tint (цвет, доля) — дымка дальних пролётов."""
    y = y + rise
    ch = R * CARD_K

    def c(h):
        return lib.mix(h, tint[0], tint[1]) if tint else h

    def K(pts):
        return [(p[0], p[1], 1) for p in pts]

    o = []
    # стопка страниц ниже листа (уходит в туман)
    col = lib.rect_pts(x, y + ch - 4, x + w, y + ch + R * col_len)
    lines = "".join(f'<rect x="{f(x)}" y="{f(y + ch + 6 + k * 11)}" width="{f(w)}" height="2.2" fill="{c(PAGE_EDGE)}"/>'
                    for k in range(int(R * col_len / 11)))
    o.append(shape(col, c(PAPER_SH), lines + blob(K([(x + w * .78, y + ch), (x + w, y + ch), (x + w, y + ch + R * col_len),
                                                     (x + w * .78, y + ch + R * col_len)]), c("#cdbfa4"), .9),
                   w=ink_w * .9, seed=seed + 1, ink_color=c(INK)))
    # боковая грань (видна у пролёта влево)
    if side:
        sd = K([(x + w, y), (x + w + DX, y - DD), (x + w + DX, y + ch + R * col_len - DD), (x + w, y + ch + R * col_len)])
        o.append(shape(sd, c("#cbb898"), "".join(f'<path d="M{f(x + w)} {f(y + 14 + k * 11)} l{f(DX)} {f(-DD)}" stroke="{c(PAGE_EDGE)}" '
                                                   f'stroke-width="2" fill="none"/>' for k in range(int((ch + R * col_len) / 11))),
                       w=ink_w * .9, seed=seed + 2, ink_color=c(INK)))
    # верх: торец стопки
    top = K([(x, y), (x + w, y), (x + w + DX, y - DD), (x + DX, y - DD)])
    tl = "".join(f'<path d="M{f(x + DX * u)} {f(y - DD * u)} L{f(x + w + DX * u)} {f(y - DD * u)}" stroke="{c(TREAD_SH)}" '
                 f'stroke-width="1.6" fill="none"/>' for u in (.3, .55, .8))
    o.append(shape(top, c(TREAD), tl + blob(K([(x, y), (x + w, y), (x + w + DX * .2, y - DD * .2), (x + DX * .2, y - DD * .2)]), c(BIND), .85),
                   w=ink_w, seed=seed + 3, ink_color=c(INK)))
    # лист: шапка и страница
    card = lib.rect_pts(x, y, x + w, y + ch)
    hh = ch * .26
    inner = blob(lib.rect_pts(x - 2, y - 2, x + w + 2, y + 9), c(BIND))
    inner += blob(lib.rect_pts(x - 2, y + 9, x + w + 2, y + hh), c(HEAD_RED))
    inner += blob(lib.rect_pts(x - 2, y + hh - 7, x + w + 2, y + hh), c(HEAD_RED_SH), .9)
    inner += blob(K([(x + w * .82, y + hh), (x + w + 2, y + hh), (x + w + 2, y + ch + 2), (x + w * .86, y + ch + 2)]), c(PAPER_SH), .55)
    # оторванные корешки прежних дней под переплётом
    rs = np.random.RandomState(seed)
    stub = [(x, y + 9)]
    k = 0
    xx = x
    while xx < x + w - 6:
        xx += rs.uniform(6, 13)
        stub.append((min(xx, x + w), y + 9 + rs.uniform(4, 9) * (k % 2 == 0)))
        k += 1
    stub += [(x + w, y + 9), (x + w, y + 9)]
    inner += blob(stub, c("#fbf8f0"), .95)
    if num:
        fs = min(w * .62, (ch - hh) * .72)
        red = day % 7 == 0
        inner += (f'<text x="{f(x + w * .48)}" y="{f(y + hh + (ch - hh) * .5 + fs * .36)}" text-anchor="middle" font-family="IDB" '
                  f'font-weight="900" font-size="{f(fs)}" fill="{c("#c8372d" if red else "#2a2230")}" letter-spacing="-2">{day}</text>')
    if star:
        inner += shape(star_pts(x + w * .5, y + hh + (ch - hh) * .5, (ch - hh) * .3), c("#f2c14e"), w=3.4, seed=seed + 9)
    o.append(shape(card, c(PAPER), inner, w=ink_w, seed=seed + 4, ink_color=c(INK)))
    # кольца переплёта поверх кромки
    nr = max(2, int(w / 46))
    for r in range(nr):
        rx = x + w * (r + .5) / nr
        o.append(f'<path d="M{f(rx - 6)} {f(y + 6)} C{f(rx - 7)} {f(y - 14)} {f(rx + 9)} {f(y - 16)} {f(rx + 8)} {f(y + 2)}" '
                 f'stroke="{c("#2a2230")}" stroke-width="{f(5.6 * ink_w / 4.2)}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{f(rx - 6)} {f(y + 6)} C{f(rx - 7)} {f(y - 14)} {f(rx + 9)} {f(y - 16)} {f(rx + 8)} {f(y + 2)}" '
                 f'stroke="{c("#b9b6c4")}" stroke-width="{f(2.6 * ink_w / 4.2)}" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def star_pts(cx, cy, r, rot=0.0):
    pts = []
    for k in range(10):
        a = math.radians(rot - 90 + k * 36)
        rr = r if k % 2 == 0 else r * .45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a), 1))
    return pts


# ═════════════════════════════ ОБЛАКА ═════════════════════════════
def cloud_pts(cx, cy, w, h, seed):
    """Облако — объединение кругов: нижний ряд и шапки сверху; контур — дуги, не лежащие внутри соседних кругов,
    по углу вокруг центра; низ срезан ровно (основание облака)."""
    rs = np.random.RandomState(seed)
    base = cy + h * .35
    C = []
    nb = rs.randint(4, 6)
    for k in range(nb):
        u = (k + .5) / nb
        r = h * rs.uniform(.42, .55)
        C.append((cx - w / 2 + w * u, base - r * .55, r))
    for k in range(rs.randint(2, 4)):
        u = rs.uniform(.25, .75)
        r = h * rs.uniform(.6, .85) * (1 - abs(u - .5))
        C.append((cx - w / 2 + w * u, base - h * .55 - r * .25, r * 1.25))
    x0 = min(x - r for x, y, r in C)
    x1 = max(x + r for x, y, r in C)
    out = []
    for u in np.linspace(0, 1, 160):
        x = x0 + (x1 - x0) * (1 - math.cos(math.pi * u)) / 2
        yy = base
        for (xc, yc, r) in C:
            if abs(x - xc) < r:
                yy = min(yy, yc - math.sqrt(r * r - (x - xc) ** 2))
        out.append((x, yy))
    return [(x0, base, 1)] + out[1:-1] + [(x1, base, 1)]


def cloud(cx, cy, w, h, seed, body, under, top_hi, ink_c=SKY_INK, ink_w=3.2, op=1.0):
    pts = cloud_pts(cx, cy, w, h, seed)
    inner = blob([(cx - w, cy + h * .05), (cx + w, cy + h * .05), (cx + w, cy + h), (cx - w, cy + h)], under, .95)
    inner += blob([(cx - w * .5, cy - h * 1.2), (cx + w * .1, cy - h * 1.4), (cx - w * .1, cy - h * .5), (cx - w * .55, cy - h * .3)], top_hi, .55)
    g = shape(pts, body, inner, w=ink_w, seed=seed + 5, ink=ink_w > 0, ink_color=ink_c)
    return f'<g opacity="{op:.3f}">{g}</g>' if op < 1 else g


LAYERS = {
    # p — параллакс, cell — сетка, w/h — размер, цвета (тело, низ, блик), ink
    "far": dict(p=0.12, cell=520, w=(260, 460), h=(60, 110), col=("#7e6aa6", "#b07a9a", "#9a88c2"), ink=0, dens=.8),
    "mid": dict(p=0.38, cell=640, w=(320, 560), h=(80, 140), col=("#a48cc4", "#e7a08e", "#c7b5e2"), ink=2.6, dens=.75),
    "near": dict(p=1.55, cell=900, w=(380, 640), h=(90, 150), col=("#cbb7df", "#f2b7a0", "#e8dcf2"), ink=3.6, dens=.33),
}


def cloud_layer(name, cam_xy, s, rot, view_half):
    """Облака слоя в его координатах: камера (cx*p, cy*p), масштаб 1+(s-1)*p. view_half — полуразмер окна в мире."""
    L = LAYERS[name]
    p = L["p"]
    sl = 1 + (s - 1) * p if p < 1 else s * (1 + (p - 1) * .5)
    cx, cy = cam_xy[0] * p, cam_xy[1] * p
    hx, hy = 540 / sl + 700, 960 / sl + 400
    c = L["cell"]
    out = []
    for i in range(int(math.floor((cx - hx) / c)), int(math.floor((cx + hx) / c)) + 1):
        for j in range(int(math.floor((cy - hy) / c)), int(math.floor((cy + hy) / c)) + 1):
            rs = np.random.RandomState((i * 7919 + j * 104729 + sum(map(ord, name)) * 37) % 2**31)
            if rs.uniform() > L["dens"]:
                continue
            x = (i + rs.uniform(.1, .9)) * c
            y = (j + rs.uniform(.1, .9)) * c
            w = rs.uniform(*L["w"])
            h = rs.uniform(*L["h"])
            out.append(cloud(x, y, w, h, abs(i * 31 + j * 17) % 9000 + 11, *L["col"], ink_w=L["ink"]))
    return f'<g transform="{lib.cam(cx, cy, sl, rot)}">{"".join(out)}</g>'


# ═════════════════════════════ КУБОК И ФЛАЖОК ═════════════════════════════
GOLD, GOLD_SH, GOLD_HI, WOOD = "#f2c14e", "#c98f2a", "#fff1b4", "#5a3a2a"


def cup(sc=1.0, glow=0.0, seed=900):
    """Кубок в своих координатах: точка хвата — ножка (0,0), основание вниз до y=+70, чаша вверх до y=-150 (×sc)."""
    def S(pts):
        return [(x * sc, y * sc) + tuple(p[2:]) for p in pts for (x, y) in [p[:2]]]

    o = []
    if glow > 0:
        g = lib.rad_grad([(0, "#fff3c0", .9 * glow), (1, "#fff3c0", 0)], 0, -90 * sc, 190 * sc)
        o.append(f'<circle cx="0" cy="{f(-90 * sc)}" r="{f(190 * sc)}" fill="url(#{g})"/>')
    base = S([(-46, 44, 1), (46, 44, 1), (52, 80, 1), (-52, 80, 1)])
    o.append(shape(base, WOOD, blob(S([(10, 44), (52, 44), (52, 80), (16, 80)]), "#3e271c", .8) +
                   blob(S([(-26, 54), (22, 54), (22, 70), (-26, 70)]), GOLD), w=3.6 * sc, seed=seed))
    stem = S([(-30, 44, 1), (30, 44, 1), (22, 30), (8, 18), (9, -26), (-9, -26), (-8, 18), (-22, 30)])
    o.append(shape(stem, GOLD, blob(S([(2, 40), (30, 44), (8, 18), (6, -26), (2, -26)]), GOLD_SH, .9), w=3.6 * sc, seed=seed + 1))
    for sg in (-1, 1):
        hd = S([(sg * 44, -126), (sg * 90, -128), (sg * 100, -100), (sg * 86, -70), (sg * 44, -60), (sg * 46, -76), (sg * 76, -82),
                (sg * 82, -104), (sg * 72, -114), (sg * 46, -110)])
        o.append(shape(hd if sg > 0 else hd[::-1], GOLD, "", w=3.4 * sc, seed=seed + 2 + sg))
    bowl = S([(-62, -150, 1), (62, -150, 1), (58, -100), (40, -56), (12, -32), (-12, -32), (-40, -56), (-58, -100)])
    o.append(shape(bowl, GOLD, blob(S([(14, -150), (62, -150), (40, -56), (10, -32)]), GOLD_SH, .9) +
                   blob(S([(-44, -140), (-30, -140), (-24, -70), (-36, -80)]), GOLD_HI, .95) +
                   shape(star_pts(0, -98 * sc, 22 * sc), "#fff6d0", w=2.2 * sc, seed=seed + 6), w=4.0 * sc, seed=seed + 5))
    o.append(blob(S([(-62, -156), (62, -156), (62, -146), (-62, -146)]), GOLD_SH, .9))
    o.append(line(S([(-60, -150), (60, -150)]), 3.4 * sc, INK, seed=seed + 7, taper=.2, wmin=.7))
    return "".join(o)


def flag(x, y, h, t, seed=950, sc=1.0, pop=1.0, color="#e2483a"):
    """Флажок: древко из (x, y) вверх на h, полотнище колышется (волна по t)."""
    if pop <= 0:
        return ""
    top = y - h * pop
    o = [shape(lib.rect_pts(x - 5 * sc, top, x + 5 * sc, y), "#6b5442", blob(lib.rect_pts(x + 1 * sc, top, x + 5 * sc, y), "#4a3a2e", .8),
               w=3.2 * sc, seed=seed)]
    o.append(shape(ellipse_pts(x, top - 6 * sc, 10 * sc, 10 * sc, 10), GOLD, w=2.8 * sc, seed=seed + 1))
    L = 130 * sc
    pts_top, pts_bot = [], []
    for k in range(9):
        u = k / 8
        wv = math.sin(t * 9 - u * 5) * 9 * sc * u
        pts_top.append((x + 4 * sc + L * u, top + 6 * sc + wv + 18 * sc * u))
        pts_bot.append((x + 4 * sc + L * u * .96, top + 82 * sc + wv - 18 * sc * u))
    pts = [(*pts_top[0], 1)] + pts_top[1:-1] + [(*pts_top[-1], 1)] + [(*pts_bot[-1], 1)] + pts_bot[-2:0:-1] + [(*pts_bot[0], 1)]
    cxs = x + L * .38
    inner = shape(star_pts(cxs, top + 44 * sc + math.sin(t * 9 - 1.9) * 4 * sc, 18 * sc), "#fff3d6", w=2.0 * sc, seed=seed + 3)
    inner += blob([(x, top + 60 * sc), (x + L, top + 40 * sc), (x + L, top + 90 * sc), (x, top + 90 * sc)], lib.mul(color, (.75, .75, .8)), .8)
    o.append(shape(pts, color, inner, w=3.4 * sc, seed=seed + 2))
    return "".join(o)
