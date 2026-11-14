"""Лист на стене рилса 38: белый лист на скотче, строки чёрным маркером от руки (шрифт CV — Caveat Bold, проявляется
слева направо по ходу маркера), зачёркивание красным маркером одной волнистой линией. Длинный вариант — лист до пола
с рулоном на конце. Маркер в руке — marker()."""
import math

import numpy as np
from PIL import ImageFont

import lib
from lib import INK, blob, ellipse_pts, line, rect_pts, shape

PAPER, PAPER_SH, PAPER_EDGE = "#fbf8f1", "#e6e0d2", "#d6cdb6"
RED = "#d8362e"
FS = 38.0
GAP = 56.0
LINES = ["покрасил стену", "поменял розетку", "положил плитку", "повесил лампу", "зашпаклевал угол", "покрасил батарею",
         "снял старые обои", "вынес мусор", "заделал щель", "покрасил окно", "постелил плёнку", "купил краску"]
_F = ImageFont.truetype("/home/user/Generator_Stickman/assets/fonts/Caveat-Variable.ttf", 100)
_F.set_variation_by_axes([700])


def text_w(s, fs=FS):
    return _F.getlength(s) * fs / 100.0


def tape(x, y, rot, seed):
    pts = [(-30, -12), (30, -12), (32, -4), (29, 2), (31, 12), (-30, 12), (-28, 4), (-31, -3)]
    g = shape(pts, "#efe6c4", blob([(-30, 4), (30, 4), (30, 12), (-30, 12)], "#ddd2aa", .8), w=2.4, seed=seed)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot})" opacity=".93">{g}</g>'


def handwrite(x, y, s, u, fs=FS, col="#1d1a22", seed=0):
    """Строка s от (x, y — базовая линия), проявлена на долю u ширины. Возвращает (svg, точка кончика маркера)."""
    if u <= 0:
        return "", (x, y - fs * .3)
    w = text_w(s, fs)
    c = lib.clip_rect(x - 6, y - fs * 1.2, w * u + 6, fs * 1.8)
    wob = 1.5 * math.sin(seed)
    t = (f'<g clip-path="url(#{c})"><text x="{x:.1f}" y="{y:.1f}" font-family="CV" font-weight="700" font-size="{fs:.1f}" '
         f'fill="{col}" transform="rotate({wob * .6:.2f} {x:.1f} {y:.1f})">{s}</text></g>')
    # кончик: по ходу строки, прыгает вверх-вниз по буквам
    tx = x + w * u
    ty = y - fs * (.28 + .22 * math.sin(u * 47 + seed))
    return t, (tx, ty)


def strike(x, y, s, u, fs=FS, seed=0):
    """Красная линия поперёк строки, проведена на долю u. Возвращает (svg, кончик)."""
    if u <= 0:
        return "", None
    w = text_w(s, fs) + 16
    n = 16
    pts = []
    for i in range(n + 1):
        q = i / n * u
        pts.append((x - 8 + w * q, y - fs * .3 + 3 * math.sin(q * 9 + seed) - 4 * q))
    return line(pts, 7, RED, taper=.15, wmin=.7, seed=4000 + seed), pts[-1]


def sheet(x0, y0, x1, y1, items, t=0.0, curl=True, seed=7000):
    """Лист x0..x1, y0..y1 со строками items: [(текст, проявлено u, зачёркнуто u)], строка i — на y0 + 70 + i*GAP.
    Возвращает (svg, кончики {('w'|'s', i): точка})."""
    o = []
    o.append(blob([(x0 + 8, y0 + 10, 1), (x1 + 10, y0 + 12, 1), (x1 + 12, y1 + 12, 1), (x0 + 10, y1 + 10, 1)], "#3a2410", .18))
    inner = blob([(x1 - 26, y0), (x1, y0), (x1, y1), (x1 - 26, y1)], PAPER_SH, .7)
    inner += line([(x0 + 32, y0 + 4), (x0 + 32, y1 - 4)], 2, "#f2b0b0", seed=seed + 2, op=.8)
    o.append(shape(rect_pts(x0, y0, x1, y1), PAPER, inner, w=3.6, seed=seed))
    tips = {}
    for i, (s, uw, us) in enumerate(items):
        y = y0 + 70 + i * GAP
        if y > y1 - 14:
            break
        tx, tip = handwrite(x0 + 42, y, s, uw, seed=i * 3.1)
        o.append(tx)
        tips[("w", i)] = tip
        sx, stip = strike(x0 + 42, y, s, us, seed=i)
        o.append(sx)
        if stip:
            tips[("s", i)] = stip
    o.append(tape(x0 + 6, y0 + 4, -28, seed + 10))
    o.append(tape(x1 - 6, y0 + 4, 26, seed + 11))
    return "".join(o), tips


def roll(cx, cy, hw, r, spin=0.0, seed=7600):
    """Рулон бумаги (горизонтальный цилиндр) лицом к зрителю."""
    body = [(cx - hw, cy - r, 1), (cx + hw, cy - r, 1), (cx + hw + r * .25, cy), (cx + hw, cy + r, 1), (cx - hw, cy + r, 1), (cx - hw - r * .25, cy)]
    inner = blob([(cx - hw - 20, cy + r * .25), (cx + hw + 20, cy + r * .25), (cx + hw + 20, cy + r + 4), (cx - hw - 20, cy + r + 4)], PAPER_SH, .95)
    inner += blob([(cx - hw - 20, cy - r * .62), (cx + hw + 20, cy - r * .62), (cx + hw + 20, cy - r * .38), (cx - hw - 20, cy - r * .38)], "#ffffff", .8)
    for k in range(3):
        ph = (spin * 2.2 + k * .33) % 1.0
        yy = cy - r + 2 * r * ph
        inner += line([(cx - hw + 30, yy), (cx + hw - 40, yy + 1)], 2.0, "#5a5660", seed=seed + 10 + k, op=.7 * math.sin(math.pi * ph))
        inner += line([(cx - hw + 30, yy + 2), (cx + hw - 50, yy + 3)], 2.6, RED, seed=seed + 20 + k, op=.6 * math.sin(math.pi * ph))
    o = [shape(body, PAPER, inner, w=3.8, seed=seed)]
    ex = cx + hw
    sp = []
    for j in range(28):
        a = spin * 6 + j * .55
        rr = r * (.85 - j * .028)
        sp.append((ex + rr * .25 * math.cos(a), cy + rr * math.sin(a)))
    o.append(shape(ellipse_pts(ex, cy, r * .27, r, 16), PAPER_EDGE, "", w=3.2, seed=seed + 1))
    o.append(line(sp, 2.2, "#9a9080", seed=seed + 2, taper=.3, wmin=.5))
    return "".join(o)


def marker(top, tip, w=17.0, ink_col="#1d1a22", seed=7700):
    """Толстый маркер от top (торец) к tip (пишущий конец): корпус белый, колпачок-торец и кончик цвета чернил."""
    a, b = np.array(top, float), np.array(tip, float)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0]])
    h = w / 2

    def P(s_, v):
        return tuple(a + u * s_ + n * v)

    o = []
    o.append(shape([P(-4, -h * .9) + (1,), P(18, -h * .9) + (1,), P(18, h * .9) + (1,), P(-4, h * .9) + (1,)], ink_col, "", w=2.6, seed=seed))
    body = [P(18, -h) + (1,), P(L - 26, -h) + (1,), P(L - 26, h) + (1,), P(18, h) + (1,)]
    o.append(shape(body, "#f2efe8", blob([P(18, h * .25), P(L - 26, h * .25), P(L - 26, h), P(18, h)], "#d4cfc4") +
                   blob([P(30, -h * .6), P(L * .55, -h * .6), P(L * .55, -h * .1), P(30, -h * .1)], ink_col, .9), w=2.8, seed=seed + 1))
    o.append(shape([P(L - 26, -h) + (1,), P(L - 8, -h * .55) + (1,), P(L - 8, h * .55) + (1,), P(L - 26, h) + (1,)], "#bdb7aa", "", w=2.6, seed=seed + 2))
    o.append(shape([P(L - 9, -h * .45), P(L + 2, -h * .2), P(L + 3, h * .25), P(L - 9, h * .45)], ink_col, "", w=2.2, seed=seed + 3))
    return "".join(o)


_ = INK
