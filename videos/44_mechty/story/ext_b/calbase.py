"""Общий настенный календарь рилса 40 (по образцу scene_calendar рилса 26): лист месяца в любом прямоугольнике,
галочки-штампы, стена. Всё в мировых координатах; размеры листа 26-го (780×820) масштабируются под коробку."""
import calendar as _cal
import math

import numpy as np

import lib
from lib import (DEFS, INK, W, H, blob, blur, clamp, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts,
                 shape)

PAPER, PAPER_SH = "#fbf8f0", "#e6dccb"
CHECK, CHECK_SH = "#df3a2c", "#a8261c"
WD = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
# месяц: (название, год, номер, цвет шапки, тень шапки)
MONTHS = {
    3: ("МАРТ", 2027, 3, "#d8433a", "#a92f29"),
    4: ("АПРЕЛЬ", 2027, 4, "#2f8c8c", "#1f6668"),
    5: ("МАЙ", 2027, 5, "#4f9a3e", "#37732b"),
}


def wallpaper():
    """Стена комнаты Димы: шалфейные обои в узкую полоску с веточкой, тёплый свет лампы сверху-слева."""
    if not any('id="pWall40"' in d for d in DEFS):
        DEFS.append('<pattern id="pWall40" width="96" height="140" patternUnits="userSpaceOnUse">'
                    '<rect width="96" height="140" fill="#b9c7a8"/>'
                    '<rect x="44" width="8" height="140" fill="#aebd9c"/>'
                    '<path d="M20 30 C26 40 26 52 20 62 C14 52 14 40 20 30Z M76 100 C82 110 82 122 76 132 C70 122 70 110 76 100Z" fill="#a3b391"/>'
                    '</pattern>')
    s = [f'<rect x="-2600" y="-2600" width="{W + 5200}" height="{H + 5200}" fill="url(#pWall40)"/>']
    g = rad_grad([(0, "#ffe2a8", .5), (.55, "#ffd08a", .14), (1, "#ffd08a", 0)], 300, 300, 1200, 1200)
    s.append(f'<rect x="-2600" y="-2600" width="{W + 5200}" height="{H + 5200}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    g2 = rad_grad([(0, "#000", 0), (.5, "#000", 0), (1, "#14200f", .5)], 540, 860, 1300, 1550)
    s.append(f'<rect x="-2600" y="-2600" width="{W + 5200}" height="{H + 5200}" fill="url(#{g2})"/>')
    return "".join(s)


class Sheet:
    """Лист месяца в коробке (x0, y0, x1, y1)."""

    def __init__(self, month, box, sd=0):
        self.name, self.year, self.m, self.hc, self.hs = MONTHS[month]
        self.x0, self.y0, self.x1, self.y1 = box
        self.k = (self.y1 - self.y0) / 820.0
        self.sd = sd
        first, n = _cal.monthrange(self.year, self.m)
        self.n = n
        self.col0 = first
        self.rows = (first + n + 6) // 7
        k = self.k
        self.cw = (self.x1 - self.x0 - 40 * k) / 7
        self.gy0, self.gy1 = self.y0 + 280 * k, self.y0 + 790 * k
        self.rh = (self.gy1 - self.gy0) / self.rows

    def cell(self, d):
        c, r = (self.col0 + d - 1) % 7, (self.col0 + d - 1) // 7
        return self.x0 + 20 * self.k + self.cw * (c + .5), self.gy0 + self.rh * (r + .5)

    def rcheck(self):
        return min(self.rh, self.cw) * 0.4

    def page(self, empty=()):
        """Статика листа: бумага, шапка, дни недели, числа. empty — дни, обведённые пунктиром (ничего)."""
        k, x0, y0, x1, y1 = self.k, self.x0, self.y0, self.x1, self.y1
        s = []
        gid = lin_grad([(0, "#ffffff", 0), (1, "#d6c7a8", .35)], 0, 0, 0, 1)
        inner = f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="url(#{gid})"/>'
        inner += blob(rect_pts(x0 - 10, y0 - 10, x1 + 10, y0 + 196 * k), self.hc)
        inner += blob(rect_pts(x0 - 10, y0 + 160 * k, x1 + 10, y0 + 196 * k), self.hs)
        fs = (104 if len(self.name) < 6 else 96) * k
        inner += (f'<text x="{f((x0 + x1) / 2)}" y="{f(y0 + 140 * k)}" text-anchor="middle" font-family="IDB" font-weight="900" '
                  f'font-size="{f(fs)}" letter-spacing="{f(3 * k)}" fill="#fff6ea">{self.name}</text>')
        for c, w in enumerate(WD):
            inner += (f'<text x="{f(x0 + 20 * k + self.cw * (c + .5))}" y="{f(y0 + 242 * k)}" text-anchor="middle" font-family="IDB" '
                      f'font-weight="900" font-size="{f(30 * k)}" fill="{"#c9554c" if c >= 5 else "#8a7e72"}">{w}</text>')
        inner += line([(x0 + 24 * k, y0 + 262 * k), (x1 - 24 * k, y0 + 262 * k)], 2.4 * k + .6, "#c9bba3", taper=.05, wmin=.9,
                      seed=self.sd + 3)
        for d in range(1, self.n + 1):
            x, y = self.cell(d)
            c = (self.col0 + d - 1) % 7
            inner += (f'<text x="{f(x)}" y="{f(y + 17 * k)}" text-anchor="middle" font-family="IDB" font-weight="900" '
                      f'font-size="{f(48 * k)}" fill="{"#c9554c" if c >= 5 else "#3a3330"}">{d}</text>')
        s.append(shape([(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)], PAPER, inner, w=4.4 * max(k, .7), seed=self.sd))
        for j in range(13):
            x = x0 + 40 * k + j * (x1 - x0 - 80 * k) / 12
            s.append(blob(ellipse_pts(x, y0 + 16 * k, 7 * k, 7 * k, 10), "#5a3a2a"))
        return "".join(s)

    def board(self):
        """Планка сверху, верёвочка и гвоздь."""
        k, x0, x1, y0 = self.k, self.x0, self.x1, self.y0
        cx = (x0 + x1) / 2
        s = []
        ny = y0 - 196 * k
        s.append(line([(cx, ny + 4 * k), (x0 + 60 * k, y0 - 50 * k)], 4 * k + 1, "#6b5a46", taper=.1, wmin=.8, seed=self.sd + 31))
        s.append(line([(cx, ny + 4 * k), (x1 - 60 * k, y0 - 50 * k)], 4 * k + 1, "#6b5a46", taper=.1, wmin=.8, seed=self.sd + 32))
        s.append(shape(ellipse_pts(cx, ny, 13 * k, 13 * k, 12), "#8b8f97", blob(ellipse_pts(cx - 4 * k, ny - 4 * k, 5 * k, 4 * k, 8), "#d4d8de"),
                       w=3.2 * k + .6, seed=self.sd + 33))
        inner = blob(rect_pts(x0 - 30, y0 - 18 * k, x1 + 30, y0 + 10 * k), mix(self.hs, "#000000", .35))
        s.append(shape([(x0 - 24 * k, y0 - 70 * k, 1), (x1 + 24 * k, y0 - 70 * k, 1), (x1 + 24 * k, y0 + 2 * k, 1), (x0 - 24 * k, y0 + 2 * k, 1)],
                       mix(self.hs, "#5a1f1a", .25), inner, w=4.6 * k + .6, seed=self.sd + 34))
        return "".join(s)

    def rings(self):
        k, x0, x1, y0 = self.k, self.x0, self.x1, self.y0
        s = []
        for j in range(13):
            x = x0 + 40 * k + j * (x1 - x0 - 80 * k) / 12
            s.append(line([(x - 4 * k, y0 + 18 * k), (x - 9 * k, y0 - 4 * k), (x - 3 * k, y0 - 22 * k), (x + 6 * k, y0 - 14 * k)], 7 * k + .8,
                          "#3a3d44", taper=.15, wmin=.7, seed=self.sd + 40 + j))
            s.append(line([(x - 6 * k, y0 + 6 * k), (x - 7 * k, y0 - 10 * k)], 2.4 * k + .4, "#aab0bb", taper=.3, seed=self.sd + 60 + j))
        return "".join(s)

    def shadow(self, dx=30, dy=34, op=.36):
        x0, y0, x1, y1 = self.x0, self.y0, self.x1, self.y1
        return blob([(x0 + dx * .8, y0, 1), (x1 + dx, y0, 1), (x1 + dx * 1.2, y1 + dy, 1), (x0 + dx, y1 + dy * .9, 1)], "#1d2412", op, blur(16))

    def full(self):
        return self.shadow() + self.board() + self.page() + self.rings()


def check_pts(x, y, r, rot=0.0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    P = [(-0.66, -0.06, 0), (-0.42, 0.18, 0), (-0.16, 0.5, 1), (0.22, -0.02, 0), (0.74, -0.66, 0)]
    return [(x + r * (px * c - py * s), y + r * (px * s + py * c)) + ((1,) if k else ()) for px, py, k in P]


def check(x, y, r, e, sd, color=CHECK, wk=0.17, pop=True):
    """Галочка-штамп: e — секунды с удара (None/<0 — нет). Влетает крупной (×1.7) и садится с отскоком за 0.12 с,
    от удара — четыре коротких штриха (сужаются, не прозрачнеют)."""
    if e is None or e < 0:
        return ""
    rs = np.random.RandomState(sd)
    rot = rs.uniform(-9, 7)
    sc = 1.0
    if pop:
        if e < 0.05:
            sc = 1.7 - 0.7 * ease_out(e / 0.05, 2)
        else:
            q = e - 0.05
            sc = 1 - 0.12 * math.exp(-q * 22) * math.sin(q * 60)
    rr = r * sc
    out = [line(check_pts(x, y, rr, rot), rr * wk * 2, color, taper=.45, wmin=.42, seed=sd, peak=.42)]
    if pop and 0.015 < e < 0.16:
        a = 1 - (e - 0.015) / 0.145
        for j in range(4):
            ang = math.radians(-60 + j * 40 + rs.uniform(-8, 8))
            d0, d1 = r * (1.05 + 0.6 * (1 - a)), r * (1.35 + 0.7 * (1 - a))
            out.append(line([(x + d0 * math.cos(ang) + r * .1, y + d0 * math.sin(ang) - r * .3),
                             (x + d1 * math.cos(ang) + r * .1, y + d1 * math.sin(ang) - r * .3)], r * .16 * a + 1, color,
                            taper=.5, seed=sd + j))
    return "".join(out)


def dashed_ring(x, y, r, sd, color="#9a8f84", w=3.0, ph=0.0):
    """Пунктирный кружок вокруг пустой клетки."""
    out = []
    n = 12
    for j in range(n):
        a0 = 2 * math.pi * j / n + ph
        a1 = a0 + 2 * math.pi / n * 0.55
        pts = [(x + r * math.cos(a0 + (a1 - a0) * u), y + r * math.sin(a0 + (a1 - a0) * u)) for u in (0, .5, 1)]
        out.append(line(pts, w, color, taper=.3, wmin=.5, seed=sd + j))
    return "".join(out)


_ = (INK, H, clamp)
