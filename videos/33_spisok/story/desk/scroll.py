"""Длинный список Димы (рилс 33): лист на столе (вид сбоку — узкая трапеция), свиток, свисающий с края стола лицом к
зрителю, рулон на конце, строки — волнистые серые каракули без читаемых слов, номера мелко слева (кодом).
Красивый вариант (pretty=True): цветные полосы-заголовки маркером, сердечки и звёздочки на полях, рамочка.
"""
import math

import numpy as np

import lib
from lib import INK, blob, ellipse_pts, line, shape

PAPER, PAPER_SH, PAPER_EDGE = "#fbf7ec", "#e6dfcd", "#d6cdb6"
SCRIB = "#6f6b7a"
HL = ["#ffe066", "#ff9fc0", "#9be39b", "#9fd0ff"]


def _rs(*k):
    return np.random.RandomState(sum((i + 1) * 7919 * int(v) for i, v in enumerate(k)) % (2 ** 31))


def scribble(x0, x1, y, seed, amp=4.0, w=3.0, col=SCRIB):
    """Волнистая строка-каракуля: петельки разной высоты, без букв."""
    rs = _rs(seed, 11)
    n = max(4, int((x1 - x0) / 9))
    pts = []
    for i in range(n + 1):
        u = i / n
        x = x0 + (x1 - x0) * u
        a = amp * (.55 + .45 * rs.uniform()) * (1 if i % 2 else -1)
        pts.append((x, y + a))
    return line(pts, w, col, taper=.25, wmin=.5, seed=seed)


def heart(x, y, r, col="#ff6f91", seed=0):
    pts = []
    for j in range(24):
        a = 2 * math.pi * j / 24
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + hx * r / 16, y + hy * r / 16))
    return shape(pts, col, "", w=2.2, seed=seed)


def star(x, y, r, col="#ffd23a", seed=0, rot=0.0):
    pts = []
    for j in range(10):
        a = math.radians(rot - 90 + j * 36)
        rr = r if j % 2 == 0 else r * .45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return shape(pts, col, "", w=2.2, seed=seed)


def rows(x0, x1, ytop, ybot, off, gap, seed, num0=1, pretty=False, numbers=True, wscale=1.0, down=False):
    """Строки списка в полосе [ytop, ybot]: строка i стоит на ytop + 34 + i*gap − off (off — прокрутка)."""
    o = []
    if down:      # бумага едет вниз: сверху новые строки, номера растут вверх (строка 1 ушла ниже всех)
        top_n = num0 + int(off // gap)
        sub = off % gap
    i0 = 0 if down else max(0, int((off - 40) // gap))
    i = i0
    while True:
        y = (ytop + 34 - gap + i * gap + sub) if down else (ytop + 34 + i * gap - off)
        if y > ybot + gap:
            break
        if y > ytop - gap:
            n = (top_n - i + 1) if down else num0 + i
            if n < 1:
                i += 1
                continue
            rs = _rs(seed, n)
            i_ = i
            i = n - 1
            nx = x0 + 10 * wscale
            if pretty and i % 5 == 0:
                o.append(blob([(x0 + 6, y - gap * .42), (x1 - 8, y - gap * .46), (x1 - 10, y + gap * .3), (x0 + 8, y + gap * .34)],
                              HL[(i // 5) % 4], .85))
                o.append(scribble(x0 + 22 * wscale, x0 + (x1 - x0) * rs.uniform(.55, .8), y, seed * 100 + i, amp=gap * .14, w=3.6 * wscale,
                                  col="#3d3a48"))
            else:
                if numbers:
                    o.append(f'<text x="{nx:.1f}" y="{y + gap * .2:.1f}" font-family="IDB" font-weight="700" font-size="{gap * .48:.1f}" '
                             f'fill="#8a8494">{n}.</text>')
                xs = x0 + (36 if numbers else 14) * wscale
                xe = x0 + (x1 - x0) * rs.uniform(.62, .94)
                o.append(scribble(xs, xe, y, seed * 100 + i, amp=gap * .12, w=2.6 * wscale))
                if pretty and i % 3 == 1:
                    hx = x1 - 18 * wscale
                    o.append(heart(hx, y - 2, 9 * wscale, "#ff6f91", seed=seed + i) if i % 2 else star(hx, y - 2, 11 * wscale, seed=seed + i))
            i = i_
        i += 1
    return "".join(o)


def hanging(x0, x1, ytop, ybot, *, off=0.0, gap=34.0, seed=500, sway=0.0, t=0.0, pretty=False, roll=0.0, num0=1, curl_top=True,
            border=False, wscale=1.0, down=False):
    """Свиток, висящий лицом к зрителю от ytop (край стола или руки) до ybot; края чуть волнятся; roll — радиус рулона
    на нижнем конце (0 — конец свободный, с лёгким загибом)."""
    L = max(1.0, ybot - ytop)
    n = max(6, int(L / 40))

    def ex(v, side):
        y = ytop + L * v
        w = sway * v * v * 30 + 3 * math.sin(v * 9 + t * 2.4 + side) * min(1, v * 4)
        return y, w

    left, right = [], []
    for j in range(n + 1):
        v = j / n
        y, w = ex(v, 0)
        left.append((x0 + w, y))
        y, w = ex(v, 1.3)
        right.append((x1 + w, y))
    pts = left + right[::-1]
    c = lib.clip_of(pts)
    inner = [blob([(x1 - 16, ytop), (x1 + 4, ytop), (x1 + 4 + sway * 30, ybot), (x1 - 16 + sway * 30, ybot)], PAPER_SH, .9)]
    sh = sway * 30
    inner.append(rows(x0 + sh * .3, x1 + sh * .3, ytop, ybot, off, gap, seed, num0=num0, pretty=pretty, wscale=wscale, down=down))
    if border:
        inner.append(line([(x0 + 6, ytop - 10), (x0 + 6, ybot + 10)], 3, "#ff8fb0", seed=seed + 7))
        inner.append(line([(x1 - 6, ytop - 10), (x1 - 6, ybot + 10)], 3, "#ff8fb0", seed=seed + 8))
    o = [blob([(p[0] + 10, p[1] + 6) for p in pts], "#1a100a", .18)]
    o.append(f'<path d="{lib.fill_d(pts)}" fill="{PAPER}"/><g clip-path="url(#{c})">{"".join(inner)}</g>')
    o.append(f'<path d="{lib.ink_open(left, 3.6 * lib.INK_K[0], taper=.1, wmin=.7, seed=seed + 1)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_open(right, 3.6 * lib.INK_K[0], taper=.1, wmin=.7, seed=seed + 2)}" fill="{INK}"/>')
    bx0, bx1 = left[-1][0], right[-1][0]
    if roll > 1:
        o.append(roll_svg((bx0 + bx1) / 2, ybot, (bx1 - bx0) / 2 + 6, roll, seed + 3, spin=t * 0))
    else:
        o.append(line([(bx0, ybot), ((bx0 + bx1) / 2, ybot + 4), (bx1, ybot - 2)], 3.6, INK, taper=.1, wmin=.7, seed=seed + 4))
    return "".join(o)


def roll_svg(cx, cy, hw, r, seed=0, spin=0.0):
    """Рулон бумаги лицом к зрителю (горизонтальный цилиндр): центр (cx, cy), полуширина hw, радиус r; spin — угол спирали."""
    body = [(cx - hw, cy - r, 1), (cx + hw, cy - r, 1), (cx + hw + r * .25, cy), (cx + hw, cy + r, 1), (cx - hw, cy + r, 1), (cx - hw - r * .25, cy)]
    inner = blob([(cx - hw - 20, cy + r * .25), (cx + hw + 20, cy + r * .25), (cx + hw + 20, cy + r + 4), (cx - hw - 20, cy + r + 4)], PAPER_SH, .95)
    inner += blob([(cx - hw - 20, cy - r * .62), (cx + hw + 20, cy - r * .62), (cx + hw + 20, cy - r * .38), (cx - hw - 20, cy - r * .38)], "#ffffff", .8)
    for k in range(3):
        ph = (spin * 2.2 + k * .33) % 1.0
        yy = cy - r + 2 * r * ph
        inner += line([(cx - hw + 10, yy), (cx + hw - 10, yy + 1)], 2.0, SCRIB, seed=seed + 10 + k, op=.55 * math.sin(math.pi * ph))
    o = [shape(body, PAPER, inner, w=3.8, seed=seed)]
    # торец со спиралью
    ex = cx + hw
    sp = []
    for j in range(28):
        a = spin * 6 + j * .55
        rr = r * (.85 - j * .028)
        sp.append((ex + rr * .25 * math.cos(a), cy + rr * math.sin(a)))
    o.append(shape(ellipse_pts(ex, cy, r * .27, r, 16), PAPER_EDGE, "", w=3.2, seed=seed + 1))
    o.append(line(sp, 2.2, "#9a9080", seed=seed + 2, taper=.3, wmin=.5))
    return "".join(o)


def on_desk(x0, x1, yb, yf, seed=520, pretty=False, lines=True, tilt=0.0):
    """Лист на столешнице (вид сбоку): трапеция от заднего края yb до переднего yf; строки — короткие штрихи."""
    pts = [(x0 + 18, yb, 1), (x1 - 4, yb - tilt, 1), (x1 + 8, yf, 1), (x0 - 8, yf, 1)]
    inner = blob([(x0 - 10, yf - 8), (x1 + 10, yf - 8), (x1 + 10, yf + 2), (x0 - 10, yf + 2)], PAPER_SH, .9)
    if lines:
        rs = _rs(seed, 3)
        rowsn = max(2, int((yf - yb) / 9))
        for r_ in range(rowsn):
            v = (r_ + .7) / (rowsn + .4)
            y = yb + (yf - yb) * v
            xa = x0 + 24 - 26 * v
            xe = xa + (x1 - x0 - 50) * rs.uniform(.5, .95)
            if pretty and r_ % 2 == 0:
                inner += blob([(xa - 4, y - 3), (xe, y - 3), (xe, y + 3), (xa - 4, y + 3)], HL[r_ % 4], .9)
            inner += line([(xa, y), ((xa + xe) / 2, y + .8), (xe, y)], 1.8, SCRIB, seed=seed + r_, op=.85, taper=.2, wmin=.5)
    return blob([(p[0] + 6, p[1] + 5) for p in pts], "#3a2410", .22) + shape(pts, PAPER, inner, w=3, seed=seed)


def front_bend(x0, x1, y, seed=530, sway=0.0):
    """Загиб бумаги через передний край столешницы (короткая дуга)."""
    pts = [(x0 - 8, y - 6), (x1 + 8, y - 6), (x1 + 6 + sway, y + 30), (x0 + sway, y + 30)]
    inner = blob([(x0 - 10, y - 8), (x1 + 10, y - 8), (x1 + 10, y + 4), (x0 - 10, y + 4)], "#ffffff", .9)
    inner += blob([(x0 - 10, y + 14), (x1 + 10, y + 14), (x1 + 10, y + 32), (x0 - 10, y + 32)], PAPER_SH, .9)
    return shape(pts, PAPER, inner, w=3.4, seed=seed)


def pen(a, b, w=10.0, seed=3960, col="#3b6fc4", click=0.0):
    """Шариковая ручка от a (кнопка) к b (стержень). click 0..1 — кнопка утоплена."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0]])
    h = w / 2
    P = lambda s_, v: tuple(a + u * s_ + n * v)  # noqa: E731
    bt = 10 + 9 * (1 - click)
    o = [shape([P(-bt + 10, -h * .5) + (1,), P(12, -h * .5) + (1,), P(12, h * .5) + (1,), P(-bt + 10, h * .5) + (1,)], "#e8e2d4", "", w=2.2, seed=seed)]
    body = [P(10, -h) + (1,), P(L * .8, -h) + (1,), P(L * .8, h) + (1,), P(10, h) + (1,)]
    o.append(shape(body, col, blob([P(10, h * .2), P(L * .8, h * .2), P(L * .8, h), P(10, h)], lib.mix(col, "#000000", .25)) +
                   blob([P(14, -h * .7), P(L * .75, -h * .7), P(L * .75, -h * .35), P(14, -h * .35)], "#ffffff", .35), w=2.6, seed=seed + 1))
    o.append(line([P(14, -h - 2), P(L * .35, -h - 3), P(L * .38, -h + 1)], 3.2, "#c9c4b8", seed=seed + 4, taper=.1, wmin=.8))
    o.append(shape([P(L * .8, -h) + (1,), P(L * .97, -h * .3) + (1,), P(L * .97, h * .3) + (1,), P(L * .8, h) + (1,)], "#d8d2c4", "", w=2.4, seed=seed + 2))
    o.append(blob(ellipse_pts(*P(L, 0), 2.4, 2.4, 6), INK))
    return "".join(o)
