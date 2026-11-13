"""Сцена calendar рилса 26.
s01 (хук): настенный календарь на обоях вечером. Влёт камеры с кадра 0 (1/1.4 → 1 за 0.22 с, перелёт 5 %, поворот −3° с
возвратом, размытие пока камера летит). Листы «АВГУСТ», «СЕНТЯБРЬ», «ОКТЯБРЬ» (все дни зачёркнуты) срываются со
спирали и улетают вбок один за другим; под последним встаёт «НОЯБРЬ» и качается; на «месяц» (1.04) удар камерой, и
дни ноября зачёркиваются красными крестиками один за другим.
s06: крупно недельный планер на стене; жёлтый стикер «ЗАВТРА» (рукопись Caveat) перепрыгивает на следующий день каждый
раз, как к нему подходит рука с ручкой — на «никогда» (8.36) и «работает» (9.04)."""
import datetime
import json
import math
import os

import numpy as np

import hand
import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg)

_ST = {}
RED, RED_SH, XRED = "#d8433a", "#a92f29", "#e0352b"
PAPER, PAPER_SH = "#fbf8f0", "#e6dccb"
MONTHS = [("АВГУСТ", 8), ("СЕНТЯБРЬ", 9), ("ОКТЯБРЬ", 10), ("НОЯБРЬ", 11)]
WD = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
PX0, PX1, PTOP, PBOT = 150, 930, 410, 1230
TEARS = [(-0.06, -1), (0.26, 1), (0.56, -1)]      # начало срыва листа, куда улетает (−1 влево)
FLY = 0.36
HIT = 1.04                                        # «месяц»
G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphs.json")))


def wallpaper(warm=1.0):
    DEFS.append('<pattern id="pWall" width="120" height="150" patternUnits="userSpaceOnUse">'
                '<rect width="120" height="150" fill="#d9bf98"/>'
                '<path d="M60 18 C72 40 72 58 60 75 C48 58 48 40 60 18Z M0 93 C12 115 12 133 0 150 M120 93 C108 115 108 133 120 150" fill="#cdb086"/>'
                '<circle cx="60" cy="112" r="5" fill="#c6a77c"/><circle cx="0" cy="37" r="5" fill="#c6a77c"/><circle cx="120" cy="37" r="5" fill="#c6a77c"/>'
                '</pattern>')
    s = [f'<rect x="-1600" y="-1600" width="{W + 3200}" height="{H + 3200}" fill="url(#pWall)"/>']
    g = rad_grad([(0, "#ffd590", .45), (.55, "#ffc070", .12), (1, "#ffc070", 0)], 330, 360, 1100, 1100)
    s.append(f'<rect x="-1600" y="-1600" width="{W + 3200}" height="{H + 3200}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    g2 = rad_grad([(0, "#000", 0), (.55, "#000", 0), (1, "#1a0e05", .55)], 540, 860, 1250, 1500)
    s.append(f'<rect x="-1600" y="-1600" width="{W + 3200}" height="{H + 3200}" fill="url(#{g2})"/>')
    return "".join(s)


def cross(cx, cy, r, u, sd):
    """Красный крестик от руки: два штриха, u 0..1 — сколько дописано."""
    if u <= 0:
        return ""
    s = []
    a1 = clamp(u / 0.5)
    p0, p1 = (cx - r, cy - r * 0.9), (cx + r * 0.95, cy + r)
    s.append(line([p0, (p0[0] + (p1[0] - p0[0]) * a1, p0[1] + (p1[1] - p0[1]) * a1)], 9, XRED, taper=.5, wmin=.35, seed=sd) if a1 > 0.05 else "")
    a2 = clamp((u - 0.5) / 0.5)
    q0, q1 = (cx + r * 0.9, cy - r), (cx - r * 0.95, cy + r * 0.9)
    s.append(line([q0, (q0[0] + (q1[0] - q0[0]) * a2, q0[1] + (q1[1] - q0[1]) * a2)], 9, XRED, taper=.5, wmin=.35, seed=sd + 1) if a2 > 0.05 else "")
    return "".join(s)


def days(m):
    first = datetime.date(2026, m, 1)
    n = ((first.replace(month=m + 1) if m < 12 else first.replace(year=2027, month=1)) - first).days
    col0 = first.weekday()
    rows = (col0 + n + 6) // 7
    return [(d, (col0 + d - 1) % 7, (col0 + d - 1) // 7) for d in range(1, n + 1)], rows


def cell(m, d):
    lst, rows = days(m)
    for dd, c, r in lst:
        if dd == d:
            cw = (PX1 - PX0 - 40) / 7
            rh = (1190 - 690) / rows
            return PX0 + 20 + cw * (c + .5), 690 + rh * (r + .5), rh
    raise KeyError


def page(name, m, crossed, sd):
    """Лист месяца в мировых координатах (без трансформа). crossed — функция дня → доля крестика."""
    s = []
    inner = blob(rect_pts(PX0 - 10, PTOP + 200, PX1 + 10, PBOT + 10), "#fff", 0)
    gid = lin_grad([(0, "#ffffff", 0), (1, "#d6c7a8", .35)], 0, 0, 0, 1)
    inner += f'<rect x="{PX0}" y="{PTOP}" width="{PX1 - PX0}" height="{PBOT - PTOP}" fill="url(#{gid})"/>'
    # шапка месяца
    inner += blob(rect_pts(PX0 - 10, PTOP - 10, PX1 + 10, PTOP + 196), RED)
    inner += blob(rect_pts(PX0 - 10, PTOP + 160, PX1 + 10, PTOP + 196), RED_SH)
    inner += (f'<text x="{(PX0 + PX1) / 2}" y="{PTOP + 140}" text-anchor="middle" font-family="IDB" font-weight="900" '
              f'font-size="{104 if len(name) < 8 else 92}" letter-spacing="2" fill="#fff6ea">{name}</text>')
    cw = (PX1 - PX0 - 40) / 7
    for k, w in enumerate(WD):
        inner += (f'<text x="{f(PX0 + 20 + cw * (k + .5))}" y="652" text-anchor="middle" font-family="IDB" font-weight="900" '
                  f'font-size="30" fill="{"#c9554c" if k >= 5 else "#8a7e72"}">{w}</text>')
    inner += line([(PX0 + 24, 672), (PX1 - 24, 672)], 2.4, "#c9bba3", taper=.05, wmin=.9, seed=sd + 3)
    lst, rows = days(m)
    rh = (1190 - 690) / rows
    for d, c, r in lst:
        x, y = PX0 + 20 + cw * (c + .5), 690 + rh * (r + .5)
        inner += (f'<text x="{f(x)}" y="{f(y + 18)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="50" '
                  f'fill="{"#c9554c" if c >= 5 else "#3a3330"}">{d}</text>')
    for d, c, r in lst:
        x, y = PX0 + 20 + cw * (c + .5), 690 + rh * (r + .5)
        inner += cross(x, y, min(rh, cw) * 0.36, crossed(d), sd * 50 + d)
    s.append(shape([(PX0, PTOP, 1), (PX1, PTOP, 1), (PX1, PBOT, 1), (PX0, PBOT, 1)], PAPER, inner, w=4.4, seed=sd))
    # дырочки под спиралью
    for k in range(13):
        x = PX0 + 40 + k * (PX1 - PX0 - 80) / 12
        s.append(blob(ellipse_pts(x, PTOP + 16, 7, 7, 10), "#5a3a2a"))
    return "".join(s)


def board():
    """Картонная планка сверху, верёвочка, гвоздь."""
    s = []
    s.append(line([(540, 214), (PX0 + 60, 360)], 4, "#6b5a46", taper=.1, wmin=.8, seed=31))
    s.append(line([(540, 214), (PX1 - 60, 360)], 4, "#6b5a46", taper=.1, wmin=.8, seed=32))
    s.append(shape(ellipse_pts(540, 210, 13, 13, 12), "#8b8f97", blob(ellipse_pts(536, 206, 5, 4, 8), "#d4d8de"), w=3.2, seed=33))
    inner = blob(rect_pts(PX0 - 30, 392, PX1 + 30, 420), "#5d2723")
    s.append(shape([(PX0 - 24, 340, 1), (PX1 + 24, 340, 1), (PX1 + 24, 412, 1), (PX0 - 24, 412, 1)], "#7a332d", inner, w=4.6, seed=34))
    return "".join(s)


def rings():
    s = []
    for k in range(13):
        x = PX0 + 40 + k * (PX1 - PX0 - 80) / 12
        s.append(line([(x - 4, PTOP + 18), (x - 9, PTOP - 4), (x - 3, PTOP - 22), (x + 6, PTOP - 14)], 7, "#3a3d44", taper=.15, wmin=.7, seed=40 + k))
        s.append(line([(x - 6, PTOP + 6), (x - 7, PTOP - 10)], 2.4, "#aab0bb", taper=.3, seed=60 + k))
    return "".join(s)


def stubs(n):
    """Рваные полоски бумаги, оставшиеся у спирали от сорванных листов."""
    if n <= 0:
        return ""
    s = []
    rs = np.random.RandomState(7 + n)
    for j in range(min(n, 3)):
        pts = [(PX0 + 4, PTOP - 2, 1), (PX1 - 4, PTOP - 2, 1)]
        x = PX1 - 4
        while x > PX0 + 10:
            pts.append((x, PTOP + 24 + j * 3 + rs.uniform(0, 10)))
            x -= rs.uniform(14, 30)
        pts.append((PX0 + 4, PTOP + 26, 1))
        s.append(shape(pts, mix(PAPER, PAPER_SH, .2 * j), "", w=2.6, seed=80 + j * 3 + n))
    return "".join(s)


def tear_xf(t, t0, side):
    """Трансформ летящего листа: отрыв (лист отгибается), потом полёт вбок с поворотом и переворотом."""
    e = t - t0
    if e < 0:
        return None, 0
    peel = ease_in(clamp(e / 0.09), 1.5)
    u = clamp((e - 0.06) / FLY)
    if u >= 1:
        return "gone", 1
    fly = ease_in(u, 1.6)
    px = PX1 if side < 0 else PX0              # отгибается от противоположного угла
    rot = side * (-14 * peel) + side * (-48 * fly)
    dx = side * (1500 * fly + 40 * peel)
    dy = -120 * math.sin(math.pi * min(u * 1.3, 1)) + 520 * fly * fly - 30 * peel
    sx = 1 - 0.55 * math.sin(math.pi * 0.5 * fly)
    xf = (f"translate({f(dx)} {f(dy)}) translate({px} {PTOP}) rotate({f(rot)}) scale({f(sx)} 1) translate({-px} {-PTOP})")
    return xf, u


def scraps(t, t0, side, sd):
    e = t - t0
    if e < 0.04 or e > 0.7:
        return ""
    rs = np.random.RandomState(sd)
    s = []
    for k in range(5):
        x0 = PX0 + 60 + rs.uniform(0, PX1 - PX0 - 120)
        vx, vy = side * rs.uniform(300, 900), rs.uniform(-700, -300)
        q = e - 0.04
        x, y = x0 + vx * q, PTOP + 10 + vy * q + 1600 * q * q
        r = rs.uniform(8, 15)
        a = rs.uniform(0, 360) + 900 * q * side
        s.append(shape(ellipse_pts(x, y, r, r * .55, 3, rot=a, seed=k), PAPER, "", w=2.2, seed=sd + k))
    return "".join(s)


def speed(t, t0, side):
    e = t - t0
    u = clamp((e - 0.1) / FLY)
    if u <= 0 or u >= 0.85:
        return ""
    s = []
    a = 1 - u / 0.85
    for k in range(4):
        y = 520 + k * 190 + 300 * u
        x = 540 + side * (300 + 900 * ease_in(u, 1.6)) - side * 120
        s.append(line([(x - side * 260 * a, y), (x - side * 40, y - 6)], 7 * a + 1, "#fff6e4", taper=.6, seed=90 + k))
    return "".join(s)


def nov_cross(d, t):
    st = HIT + 0.02 + (d - 1) * 0.045
    return clamp((t - st) / 0.09)


def frame01(t):
    s = []
    s.append(_ST["wall"])
    # тень календаря на стене
    sw = 6 * math.sin(t * 9) * math.exp(-max(0, t - HIT) * 3)
    s.append(blob([(PX0 + 30, PTOP, 1), (PX1 + 34, PTOP, 1), (PX1 + 40, PBOT + 34, 1), (PX0 + 36, PBOT + 30, 1)], "#2a1608", .38, blur(16)))
    s.append(board())
    n_torn = sum(1 for (t0, _) in TEARS if t - t0 > 0.05)
    # ноябрь: под стопкой; встаёт — покачивание на спирали после отрыва октября и удар на «месяц»
    swing = 0.0
    e = t - (TEARS[2][0] + 0.06)
    if e > 0:
        swing = 2.2 * math.exp(-e * 4) * math.sin(e * 14)
    lift = 0.0
    if t >= HIT:
        q = t - HIT
        lift = -14 * math.exp(-q * 9) * math.cos(q * 26)
    s.append(f'<g transform="rotate({f(swing)} 540 {PTOP}) translate(0 {f(lift)})">{_ST["nov_base"]}' +
             "".join(cross(cell(11, d)[0], cell(11, d)[1], min(cell(11, d)[2], (PX1 - PX0 - 40) / 7) * 0.36,
                           nov_cross(d, t), 11 * 50 + d) for d in range(1, 14)) + "</g>")
    # листы месяцев сверху вниз: последний сорванный лежит ниже
    for i in (2, 1, 0):
        t0, side = TEARS[i]
        xf, u = tear_xf(t, t0, side)
        if xf == "gone":
            continue
        pg = _ST[f"page{i}"]
        if xf is None:
            s.append(pg)
        else:
            s.append(f'<g transform="{xf}">{pg}</g>')
    s.append(stubs(n_torn))
    s.append(rings())
    for i, (t0, side) in enumerate(TEARS):
        s.append(scraps(t, t0, side, 300 + i * 10) + speed(t, t0, side))
    _ = sw
    return "".join(s)


def cam01(t):
    # влёт: 1/1.4 → 1.05 за 0.22 с, затем затухающий перелёт; поворот −3° → 0 с лёгким отскоком
    if t < 0.22:
        e = ease_out(t / 0.22, 3)
        s = 1 / 1.4 + (1.05 - 1 / 1.4) * e
        rot = -3.2 * (1 - e)
    else:
        q = t - 0.22
        s = 1 + 0.05 * math.exp(-q * 8) * math.cos(q * 16)
        rot = 0.9 * math.exp(-q * 6) * math.sin(q * 15)
    # удар на «месяц»
    if t >= HIT - 0.04:
        q = t - (HIT - 0.04)
        s *= 1 + 0.09 * (1 - math.exp(-q * 40)) * math.exp(-max(0, q - 0.06) * 3.2)
        rot += 1.2 * math.exp(-q * 7) * math.sin(q * 34)
    # медленный дрейф поверх
    s *= 1 + 0.025 * t
    cx = 540 + 10 * math.sin(t * 1.3)
    cy = 790 + 8 * t
    sh = 0.0
    if t >= HIT:
        q = t - HIT
        sh = 9 * math.exp(-q * 10) * math.sin(q * 70)
    return cam(cx + sh, cy, s, rot)


# ═══════════════════════════════ s06: недельный планер
ROW0, ROWH, NX0, NX1 = 330, 132, 160, 920
JUMPS = [8.36, 9.04]
NOTE_ROW0 = 1           # стикер стоит на «ВТ», прыгает на СР и ЧТ
NS = 230                # сторона стикера


def planner():
    s = []
    s.append(_ST["wall"])
    s.append(blob([(NX0 - 30, ROW0 - 110, 1), (NX1 + 46, ROW0 - 100, 1), (NX1 + 52, ROW0 + 7 * ROWH + 60, 1), (NX0 - 20, ROW0 + 7 * ROWH + 50, 1)],
                  "#2a1608", .38, blur(16)))
    inner = ""
    gid = lin_grad([(0, "#ffffff", 0), (1, "#d6c7a8", .3)], 0, 0, 0, 1)
    inner += f'<rect x="{NX0 - 60}" y="{ROW0 - 140}" width="{NX1 - NX0 + 120}" height="{7 * ROWH + 240}" fill="url(#{gid})"/>'
    inner += blob(rect_pts(NX0 - 50, ROW0 - 130, NX1 + 50, ROW0 - 38), "#3f7f8f")
    for k in range(7):
        y = ROW0 + k * ROWH
        if k >= 5:
            inner += blob(rect_pts(NX0 - 50, y, NX1 + 50, y + ROWH), "#f6e7e2")
        inner += line([(NX0 - 10, y + ROWH), (NX1 + 10, y + ROWH)], 2.6, "#c9bba3", taper=.05, wmin=.9, seed=500 + k)
        inner += (f'<text x="{NX0 + 52}" y="{y + ROWH / 2 + 17}" text-anchor="middle" font-family="IDB" font-weight="900" '
                  f'font-size="46" fill="{"#c9554c" if k >= 5 else "#4a4440"}">{WD[k]}</text>')
    inner += line([(NX0 + 112, ROW0 - 20), (NX0 + 112, ROW0 + 7 * ROWH - 6)], 3, "#e59a9a", taper=.05, wmin=.9, seed=520)
    # прошлый понедельник: дела нарисованы значками, зачёркнутая пустота — без букв
    y = ROW0 + ROWH / 2
    inner += line([(NX0 + 160, y), (NX0 + 300, y - 6), (NX0 + 420, y + 4)], 5, "#9aa0ad", taper=.4, seed=530)
    s.append(shape([(NX0 - 40, ROW0 - 120, 1), (NX1 + 40, ROW0 - 120, 1), (NX1 + 40, ROW0 + 7 * ROWH + 40, 1),
                    (NX0 - 40, ROW0 + 7 * ROWH + 40, 1)], PAPER, inner, w=4.6, seed=540))
    # магнит-кнопки сверху
    for k, x in enumerate((NX0 + 20, NX1 - 20)):
        s.append(shape(ellipse_pts(x, ROW0 - 92, 20, 20, 12), "#e2584a", blob(ellipse_pts(x - 6, ROW0 - 98, 7, 5, 8), "#f7a08f"), w=3.4, seed=550 + k))
    return "".join(s)


def zavtra(x, y, sc, rot, sqx=1.0, sqy=1.0, curl=0.0, sd=0):
    """Жёлтый стикер «ЗАВТРА»: центр (x, y). Буквы — контуры Caveat 600, синий маркер."""
    h = NS / 2
    inner = blob([(-h, h - 30, 1), (h, h - 34, 1), (h, h, 1), (-h, h, 1)], "#f2c84a", .8)
    gl = G["lines"][3]
    adv = sum(g["adv"] for g in gl)
    fs = (NS * 0.86) / adv * G["upm"]
    sc_ = fs / G["upm"]
    xx = -adv * sc_ / 2
    txt = ""
    for g in gl:
        if g["bounds"]:
            txt += f'<path d="{g["d"]}" transform="translate({f(xx)} {f(28)}) scale({sc_:.5f} {-sc_:.5f})" fill="#26356f"/>'
        xx += g["adv"] * sc_
    pts = [(-h, -h, 1), (h, -h, 1), (h, h - 26 * curl), (h - 22 * curl, h, 1), (-h, h, 1)]
    body = shape(pts, "#ffe066", inner + txt, w=3.6, seed=600 + sd)
    if curl > 0:
        body += shape([(h, h - 26 * curl, 1), (h - 22 * curl, h, 1), (h - 26 * curl, h - 30 * curl, 1)], "#e8bf3c", "", w=2.6, seed=610 + sd)
    sh = blob(rect_pts(-h + 12, -h + 16, h + 14, h + 18), "#2a1608", .3, blur(8))
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc * sqx)} {f(sc * sqy)})">{sh}{body}</g>')


def note_pos(row):
    return NX0 + 310, ROW0 + row * ROWH + ROWH / 2


def note_state(t):
    """Где стикер: строка, прыжок дугой с поворотом, сжатие перед прыжком и при посадке, дрожь, когда близко перо."""
    row = NOTE_ROW0
    for j in JUMPS:
        if t >= j + 0.2:
            row += 1
    x, y = note_pos(row)
    rot, sqx, sqy = -3 + 2 * row, 1.0, 1.0
    for k, j in enumerate(JUMPS):
        e = t - j
        if -0.1 <= e < 0:            # замах: присел
            q = (e + 0.1) / 0.1
            sqx, sqy = 1 + 0.12 * q, 1 - 0.14 * q
            rot += 4 * math.sin(q * 20)
        elif 0 <= e < 0.2:           # полёт
            q = e / 0.2
            x0, y0 = note_pos(NOTE_ROW0 + k)
            x1, y1 = note_pos(NOTE_ROW0 + k + 1)
            x = x0 + (x1 - x0) * ease_io(q) + 40 * math.sin(math.pi * q)
            y = y0 + (y1 - y0) * ease_io(q) - 170 * math.sin(math.pi * q)
            rot = -3 + 2 * (NOTE_ROW0 + k) + 360 * ease_io(q) * 0 + 24 * math.sin(math.pi * q)
            sqx, sqy = 1 - 0.08 * math.sin(math.pi * q), 1 + 0.1 * math.sin(math.pi * q)
        elif 0.2 <= e < 0.5:         # посадка
            q = e - 0.2
            k_ = math.exp(-q * 12) * math.cos(q * 40)
            sqx, sqy = 1 + 0.14 * k_, 1 - 0.16 * k_
    # дрожь: когда перо близко (перед каждым прыжком и в конце, когда рука снова тянется)
    for j in JUMPS + [9.92]:
        e = t - (j - 0.32)
        if 0 <= e < 0.24:
            rot += 2.4 * math.sin(e * 70) * (e / 0.24)
    return x, y, rot, sqx, sqy


def pen_path(t):
    """Кончик ручки: подход к стикеру справа снизу, отдёрнулась после прыжка, снова к новому месту."""
    keys = [(7.64, 820, 760), (8.30, 615, 575), (8.40, 655, 610), (8.52, 710, 660),
            (8.98, 615, 705), (9.10, 670, 760), (9.26, 725, 820), (9.96, 622, 835)]
    for (a, x0, y0), (b, x1, y1) in zip(keys, keys[1:]):
        if a <= t <= b:
            u = (t - a) / (b - a)
            u = ease_out(u, 2.2) if b - a > 0.2 else ease_io(u)
            return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    return keys[-1][1], keys[-1][2]


def frame06(t):
    s = [_ST["planner"]]
    x, y, rot, sqx, sqy = note_state(t)
    curl = 0.4 + 0.25 * math.sin(t * 5)
    s.append(zavtra(x, y, 1.0, rot, sqx, sqy, curl))
    # следы: где стикер был (бледный клей)
    # рука с ручкой
    px, py = pen_path(t)
    ang = -38 + 3 * math.sin(t * 2.7)
    s.append(f'<g transform="translate({f(px + 24)} {f(py + 30)}) scale(1.05)" opacity=".26" filter="url(#fShH)">{hand.hand(ang, 7)}</g>')
    s.append(hand.draw(px, py, ang, 1.05, 7))
    # «вжух» у стикера в прыжке
    for j in JUMPS:
        e = t - j
        if 0.02 < e < 0.26:
            a = 1 - e / 0.26
            for k in range(3):
                bx, by = note_pos(NOTE_ROW0 + JUMPS.index(j))
                s.append(line([(bx - 140 + k * 30, by - 40 - k * 50), (bx - 200 + k * 30, by - 20 - k * 50)], 7 * a + 1, INK,
                              taper=.6, seed=700 + k))
    return "".join(s)


def cam06(t):
    u = clamp((t - 7.64) / 2.32)
    s = 1.5 + 0.12 * (0.4 * u + 0.6 * ease_io(u))
    _, ny, _, _, _ = note_state(t)
    cy = 640 + 0.55 * (ny - 528)
    rot = -1.2 + 1.4 * u
    for j in JUMPS:
        q = t - j - 0.18
        if q >= 0:
            s *= 1 + 0.035 * math.exp(-q * 8) * math.sin(min(q * 18, math.pi))
    return cam(505 - 6 * u, cy, s, rot)


def frame(sid, t):
    if not _ST:
        DEFS.append('<filter id="fShH" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                    '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
        _ST["wall"] = wallpaper()
        for i in range(3):
            _ST[f"page{i}"] = page(MONTHS[i][0], MONTHS[i][1], lambda d: 1.0, 10 + i)
        _ST["nov_base"] = page("НОЯБРЬ", 11, lambda d: 0.0, 13)
        _ST["planner"] = planner()
        lib.static_done()
    lib.dyn_begin()
    if sid == "s01":
        art, cm = frame01(t), cam01(t)
        bl = ""
        if t < 0.2:
            sd = 5 * (1 - t / 0.2) ** 1.5
            if sd > 0.3:
                bl = f' filter="url(#zb{int(sd * 10)})"'
                DEFS.append(f'<filter id="zb{int(sd * 10)}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{sd:.2f}"/></filter>')
        return svg(f'<rect width="{W}" height="{H}" fill="#cdb086"/><g transform="{cm}"><g{bl}>{art}</g></g>')
    art, cm = frame06(t), cam06(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#cdb086"/><g transform="{cm}">{art}</g>')
