"""Рилс 56 «чемодан», группа A: комната Димы днём, Дима ходит.
s01 (0–1.4): хук — Дима мечется между шкафом и пустым чемоданом, часы на стене без цифр, вещи летят, влёт камеры.
s02 (1.4–3.17): крупно будильник без цифр, звонок трясётся на «час» (1.50) и «выхода» (1.89), Дима хватается за голову, сгребает чемодан.
s04 (5.28–7.9): Дима швыряет три свитера (5.90, 6.16, 6.75) через плечо, четвёртый падает на голову.
s06 (10.47–12.14): Дима над полным чемоданом чешет затылок, облако-мысль с пустой плитой и знаком вопроса, лопается на «нет» (11.02).
s13 (22.92–24.68): светлый другой день, Дима с чашкой смотрит на календарь с обведённым днём, на «Дима» (23.96) кивает; чемодан пустой на кровати.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Дима — people.py (тот же, что в 55), комната — room56() (день, шкаф)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import base_d as D  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
from lib import (blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape, smooth,  # noqa: E402
                 svg, back_out, spring)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
T = {i: w["start"] for i, w in enumerate(WORDS)}
T_CHAS, T_VYHODA = T[5], T[7]
T_TRI, T_SVITERA, T_NA = T[16], T[17], T[18]
T_VDRUG, T_NET = T[26], T[28]
T_DIMA = T[55]
BS = 0.6
FLOOR_Y = 1440          # линия, на которой стоят подошвы
_ST = {}
INK = lib.INK
SWEATER_COLS = ["#d8453a", "#4f7fa8", "#6b9a6a", "#e1a43a", "#8a5a9a", "#c9744a"]


def rnd(k, a=0.0, b=1.0):
    x = math.sin(k * 127.1 + 311.7) * 43758.5453
    return a + (x - math.floor(x)) * (b - a)


def G(inner, tx=0.0, ty=0.0, s=1.0, rot=0.0, extra=""):
    return f'<g transform="translate({f(tx)} {f(ty)}) rotate({f(rot)}) scale({s:.5f})" {extra}>{inner}</g>'


def Gxy(inner, tx=0.0, ty=0.0, sx=1.0, sy=1.0, rot=0.0):
    return f'<g transform="translate({f(tx)} {f(ty)}) rotate({f(rot)}) scale({sx:.5f} {sy:.5f})">{inner}</g>'


def lerp(a, b, u):
    return a + (b - a) * u


def kf(t, keys):
    """Плавная интерполяция по ключам [(t, v...)] (smoothstep между соседними)."""
    if t <= keys[0][0]:
        return np.array(keys[0][1:], float)
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = ease_io(clamp((t - a[0]) / (b[0] - a[0])))
            return np.array(a[1:], float) * (1 - u) + np.array(b[1:], float) * u
    return np.array(keys[-1][1:], float)


# ═════════════════════════ одежда и вещи ═════════════════════════
def sweater(col, s=1.0, seed=0, squash=1.0, sleeve=0.0):
    """Свитер (центр 0,0, ширина ~230): тело, рукава, воротник-резинка, резинка снизу. sleeve — взмах рукавов."""
    dk, lt = mix(col, "#000000", .22), mix(col, "#ffffff", .28)
    sl = 22 * sleeve
    body = [(-52, -46, 1), (52, -46, 1), (58, 4), (60, 74, 1), (-60, 74, 1), (-58, 4)]
    lsl = [(-50, -42, 1), (-118 - sl, 22), (-132 - sl, 70, 1), (-98 - sl, 84, 1), (-84 - sl, 40), (-52, 14)]
    rsl = [(50, -42, 1), (118 + sl, 22), (132 + sl, 70, 1), (98 + sl, 84, 1), (84 + sl, 40), (52, 14)]
    o = []
    o.append(shape(lsl, col, blob([(-132 - sl, 70), (-98 - sl, 84), (-90 - sl, 56), (-118 - sl, 48)], dk, .9) + blob([(-132 - sl, 62), (-98 - sl, 76), (-96 - sl, 84), (-132 - sl, 70)], lt, .0), w=4.2, seed=seed + 1))
    o.append(shape(rsl, col, blob([(132 + sl, 70), (98 + sl, 84), (90 + sl, 56), (118 + sl, 48)], dk, .9), w=4.2, seed=seed + 2))
    inner = blob([(-60, -46), (60, -46), (60, 6), (-60, 6)], lt, .0)
    inner += blob([(18, -46), (60, -46), (60, 74), (30, 74)], dk, .75)
    inner += blob([(-60, 24), (60, 24), (60, 40), (-60, 40)], lt, .8)
    inner += blob([(-60, 54), (60, 54), (60, 74), (-60, 74)], dk, .9)
    for j in range(5):
        inner += line([(-50 + j * 22, 56), (-50 + j * 22, 72)], 2.4, mix(col, "#000000", .4), taper=.1, wmin=.8, seed=seed + 20 + j, op=.7)
    o.append(shape(body, col, inner, w=4.6, seed=seed + 3))
    o.append(shape(ellipse_pts(0, -46, 30, 12, 14), dk, blob(ellipse_pts(0, -44, 18, 6, 10), "#3a2a2a", .6), w=3.6, seed=seed + 4))
    o.append(line([(-30, -2), (-10, 6), (14, 0)], 2.6, dk, taper=.5, wmin=.3, seed=seed + 5, op=.7))
    return Gxy("".join(o), 0, 0, s, s * squash)


def tee(col, s=1.0, seed=0):
    dk = mix(col, "#000000", .2)
    body = [(-44, -40, 1), (44, -40, 1), (46, 70, 1), (-46, 70, 1)]
    ls = [(-42, -38, 1), (-88, -6, 1), (-70, 28, 1), (-44, 4)]
    rs = [(42, -38, 1), (88, -6, 1), (70, 28, 1), (44, 4)]
    o = [shape(ls, col, "", w=4, seed=seed + 1), shape(rs, col, "", w=4, seed=seed + 2)]
    o.append(shape(body, col, blob([(14, -40), (44, -40), (46, 70), (22, 70)], dk, .7), w=4.4, seed=seed + 3))
    o.append(shape(ellipse_pts(0, -40, 22, 9, 12), dk, "", w=3.2, seed=seed + 4))
    return G("".join(o), 0, 0, s)


def sock(col, s=1.0, seed=0):
    dk = mix(col, "#000000", .2)
    pts = [(-16, -40, 1), (16, -40, 1), (18, 20), (50, 36), (50, 62, 1), (-18, 62, 1), (-18, 20)]
    return G(shape(pts, col, blob(rect_pts(-18, -40, 18, -26), "#f4efe4") + blob([(-18, 50), (50, 50), (50, 62), (-18, 62)], dk, .8), w=4, seed=seed + 1), 0, 0, s)


def umbrella(s=1.0, seed=0):
    return ""


def item(kind, i, s=1.0, **kw):
    col = SWEATER_COLS[i % len(SWEATER_COLS)]
    if kind == "sw":
        return sweater(col, s, 7000 + i * 11, **kw)
    if kind == "tee":
        return tee(col, s, 7100 + i * 11)
    return sock(col, s, 7200 + i * 11)


def sweater_hat(col, s=1.0, seed=0, sway=0.0):
    """Свитер, упавший на голову: тело — шапкой, рукава висят по бокам лица."""
    dk = mix(col, "#000000", .22)
    o = []
    for sd in (-1, 1):
        sl = [(sd * 66, -20, 1), (sd * 108, -14, 1), (sd * (118 + 14 * sway), 120), (sd * (84 + 14 * sway), 134, 1), (sd * 62, 50)]
        o.append(shape(sl, col, blob([(sd * (118 + 14 * sway), 120), (sd * (84 + 14 * sway), 134), (sd * (80 + 10 * sway), 100), (sd * (112 + 12 * sway), 92)], dk, .9), w=4.2, seed=seed + sd + 5))
    body = [(-92, -2, 1), (-78, -56), (-34, -84), (34, -84), (78, -56), (92, -2, 1), (62, 14), (0, 20), (-62, 14)]
    inner = blob([(24, -84), (92, -2), (62, 14), (30, 14)], dk, .75) + blob([(-92, -8), (92, -8), (62, 14), (0, 20), (-62, 14)], dk, .9)
    inner += blob(rect_pts(-90, -34, 90, -20), mix(col, "#ffffff", .3), .85)
    o.append(shape(body, col, inner, w=4.6, seed=seed + 3))
    o.append(shape(ellipse_pts(0, -80, 26, 10, 12), dk, blob(ellipse_pts(0, -78, 14, 5, 10), "#2a1a1a", .7), w=3.4, seed=seed + 4))
    return G("".join(o), 0, 0, s)


# ═════════════════════════ комната (день) ═════════════════════════
def clock(cx, cy, r, t, jump=0.0, ring_shake=0.0):
    """Круглые настенные часы без цифр: засечки штрихами, стрелки; jump — рывок минутной стрелки."""
    o = [blob(ellipse_pts(cx + 6, cy + 10, r + 4, r + 4, 24), "#2a1408", .22)]
    face = ellipse_pts(cx, cy, r, r, 28)
    inner = blob(ellipse_pts(cx - r * .15, cy - r * .2, r * .8, r * .8, 20), "#ffffff", .5)
    for k in range(12):
        a = math.radians(k * 30 - 90)
        r0 = r * (.74 if k % 3 else .66)
        inner += line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r * .88 * math.cos(a), cy + r * .88 * math.sin(a))], 4.4 if k % 3 == 0 else 3,
                      INK, taper=.1, wmin=.9, seed=8100 + k)
    o.append(shape(face, "#fbf6ea", inner, w=6, seed=8099))
    ha = math.radians(-60 + jump * 1.2)
    ma = math.radians(-90 + 330 + jump * 2.0 + 20 * math.sin(t * 5) * ring_shake)
    o.append(line([(cx, cy), (cx + r * .5 * math.cos(ha), cy + r * .5 * math.sin(ha))], 9, INK, taper=.15, wmin=.8, seed=8200))
    o.append(line([(cx, cy), (cx + r * .72 * math.cos(ma), cy + r * .72 * math.sin(ma))], 6, INK, taper=.15, wmin=.8, seed=8201))
    o.append(shape(ellipse_pts(cx, cy, 8, 8, 10), "#d6322c", "", w=3, seed=8202))
    return "".join(o)


def wardrobe(variant="mess"):
    """Шкаф у левого края комнаты (x −60…390). mess — дверцы нараспашку, видны вещи; tidy — закрыт."""
    X0, X1, Y0, Y1 = -60, 320, 330, 1334
    o = []
    o.append(shape(rect_pts(X0, Y0, X1, Y1), "#b5834f", blob(rect_pts(X1 - 26, Y0, X1, Y1), "#8f6238", .85), w=5, seed=8300))
    o.append(blob(ellipse_pts(220, Y1 + 8, 220, 14, 14), "#2a1408", .3))
    if variant == "tidy":
        for k, (a, b) in enumerate(((X0 + 14, 130), (130, X1 - 28))):
            o.append(shape(rect_pts(a, Y0 + 20, b, Y1 - 20), "#c99a64",
                           blob(rect_pts(a + 20, Y0 + 44, b - 20, Y1 - 44), "#d4a872", .9) + blob(rect_pts(b - 26, Y0 + 20, b, Y1 - 20), "#a87a48", .6), w=4.4, seed=8310 + k))
        o.append(shape(rect_pts(112, 800, 124, 900, 5), "#5e3720", "", w=3, seed=8320))
        o.append(shape(rect_pts(138, 800, 150, 900, 5), "#5e3720", "", w=3, seed=8321))
        return "".join(o)
    inner = [blob(rect_pts(X0 + 18, Y0 + 18, X1 - 30, Y1 - 18), "#6f4a34")]
    inner.append(blob(rect_pts(X0 + 18, Y0 + 18, X1 - 30, Y0 + 70), "#5a3a28"))
    # полки и стопки
    for k, sy in enumerate((700, 960, 1200)):
        inner.append(blob(rect_pts(X0 + 18, sy, X1 - 30, sy + 14), "#a8794a"))
        inner.append(blob(rect_pts(X0 + 18, sy + 14, X1 - 30, sy + 24), "#4a2f20", .8))
        for j, x in enumerate(range(10, 330, 78)):
            hh = 36 + (k * 13 + j * 17) % 40
            col = SWEATER_COLS[(k * 2 + j) % 6]
            inner.append(shape(rect_pts(x, sy - hh, x + 70, sy, 5), col, blob(rect_pts(x, sy - hh * .5, x + 70, sy - hh * .5 + 6), mix(col, "#ffffff", .3), .8), w=3.4, seed=8400 + k * 10 + j))
    # штанга с вешалками
    inner.append(line([(X0 + 18, 440), (X1 - 30, 440)], 9, "#8b8d98", taper=.05, wmin=.95, seed=8350))
    for j, x in enumerate((10, 70, 130, 190, 250, 310)):
        col = SWEATER_COLS[(j * 5 + 1) % 6]
        inner.append(line([(x, 440), (x, 462), (x - 26, 478), (x + 26, 478), (x, 462)], 3, "#8b8d98", taper=.1, wmin=.9, seed=8360 + j))
        inner.append(shape([(x - 34, 476, 1), (x + 34, 476, 1), (x + 40, 630), (x - 40, 630)], col, blob([(x + 12, 476), (x + 34, 476), (x + 40, 630), (x + 18, 630)], mix(col, "#000000", .25), .8), w=3.6, seed=8370 + j))
    o.append(shape(rect_pts(X0 + 18, Y0 + 18, X1 - 30, Y1 - 18), "#6f4a34", "".join(inner[1:]), w=4.4, seed=8301))
    return "".join(o)


def calendar(cx, cy, s=1.0, t=0.0, mark_u=1.0):
    """Настенный календарь без цифр: шапка, сетка клеток штрихами, один день обведён, самолётик (штрихи)."""
    o = []
    W_, H_ = 250, 290
    inner = blob(rect_pts(-W_ / 2, -H_ / 2, W_ / 2, -H_ / 2 + 66), "#e0614e")
    inner += blob(rect_pts(-W_ / 2, -H_ / 2 + 60, W_ / 2, -H_ / 2 + 66), "#b84434", .9)
    for k in range(7):
        x = -W_ / 2 + 22 + k * 34
        inner += blob(rect_pts(x - 6, -H_ / 2 + 76, x + 8, -H_ / 2 + 84, 3), "#9aa0b0", .9)
    for r_ in range(5):
        for c in range(7):
            x, y = -W_ / 2 + 24 + c * 34, -H_ / 2 + 108 + r_ * 36
            inner += blob(rect_pts(x - 9, y - 3, x + 9, y + 3, 2), "#b4b8c6", .95)
    o.append(shape(rect_pts(-W_ / 2, -H_ / 2, W_ / 2, H_ / 2, 8), "#fffdf6", inner, w=5, seed=8500))
    o.append(shape(ellipse_pts(-70, -H_ / 2 + 8, 7, 7, 8), "#a0a4b4", "", w=2.6, seed=8501))
    o.append(shape(ellipse_pts(70, -H_ / 2 + 8, 7, 7, 8), "#a0a4b4", "", w=2.6, seed=8502))
    # обведённый день (красный овал, рисуется от руки) в 4-й строке, 5-й клетке
    ox, oy = -W_ / 2 + 24 + 4 * 34, -H_ / 2 + 108 + 3 * 36
    n = max(2, int(24 * mark_u))
    ring = [(ox + 26 * math.cos(-1.5 + a), oy + 20 * math.sin(-1.5 + a)) for a in np.linspace(0, 2 * math.pi * 1.04 * mark_u, n)]
    if mark_u > .05:
        o.append(line(ring, 6, "#d6322c", taper=.1, wmin=.8, seed=8503))
    # самолётик (штрихи) над обведённым днём
    if mark_u > .9:
        px, py = ox + 6, oy - 52 - 6 * math.sin(t * 3)
        o.append(line([(px - 26, py + 10), (px + 28, py - 8)], 5, "#2f6bd6", taper=.15, wmin=.7, seed=8504))
        o.append(line([(px + 28, py - 8), (px - 6, py + 24), (px - 8, py + 8)], 5, "#2f6bd6", taper=.15, wmin=.7, seed=8505))
        o.append(line([(px - 26, py + 10), (px - 40, py - 6)], 4, "#2f6bd6", taper=.15, wmin=.7, seed=8506))
    return G("".join(o), cx, cy, s)


def room56(variant="mess"):
    """Статика комнаты: дневная стена с окном (D.room_static при DAY), поверх — шкаф, часы, календарь (в tidy)."""
    D.DAY[0] = True
    base = D.room_static()
    o = [base]
    # закрыть полку и картину (они левее окна) шкафом; стену рядом оставить
    o.append(wardrobe(variant))
    o.append('<rect x="-1600" y="2300" width="4400" height="1600" fill="#8a6a52"/>')
    o.append(window_sun(0, .8))
    return "".join(o)


def window_sun(t, k=1.0):
    """Мягкий дневной луч из окна на пол (смешение screen)."""
    pts = [(700, 520), (1120, 520), (1560, 1480), (900, 1480)]
    g = lib.lin_grad([(0, "#fff3c4", .0), (.3, "#fff3c4", .35 * k), (1, "#fff3c4", .06 * k)], 0, 0, 0, 1)
    return f'<path d="{lib.fill_d(pts)}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def sun_motes(t, n=22, box=(700, 560, 1250, 1380)):
    rs = np.random.RandomState(11)
    o = []
    for i in range(n):
        x0, y0 = rs.uniform(box[0], box[2]), rs.uniform(box[1], box[3])
        sp, ph, r = rs.uniform(8, 20), rs.uniform(0, 6.28), rs.uniform(2.2, 4.4)
        y = box[1] + (y0 - box[1] - sp * t) % (box[3] - box[1])
        x = x0 + 16 * math.sin(t * .7 + ph)
        a = (0.55 + 0.35 * math.sin(t * 2.2 + ph)) * smooth(box[1], box[1] + 80, y) * (1 - smooth(box[3] - 100, box[3], y))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#fff6d8" opacity="{a * .8:.2f}"/>')
    return "".join(o)


# ═════════════════════════ чемодан ═════════════════════════
def suitcase(x, y, k=1.0, lid=1.0, fill=0.0, squash=1.0, t=0.0, bulge=0.0, flap=0.0, shake=0.0, closed=0.0):
    """Чемодан (вид спереди, низ — y): тёмно-красный корпус, золотые уголки, замок; крышка стоит сзади (lid 1) и показывает подкладку.
    fill 0 — пустой, 1 — полный (из него торчат вещи), squash — сжатие корпуса по высоте."""
    o = []
    W_ = 170
    o.append(blob(ellipse_pts(0, 8, W_ + 30, 16, 18), "#2a1408", .3))
    shell, shell_dk = "#2e8c96", "#1f6670"
    lin_, lin_dk = "#f7e6d4", "#e0c8ae"
    # крышка (подкладкой к нам)
    if lid > .02:
        lh = 250 * lid
        lp = [(-W_ + 14, -118, 1), (W_ - 14, -118, 1), (W_ - 8, -118 - lh, 1), (-W_ + 8, -118 - lh, 1)]
        li = [(-W_ + 36, -138, 1), (W_ - 36, -138, 1), (W_ - 30, -118 - lh + 24, 1), (-W_ + 30, -118 - lh + 24, 1)]
        inn = blob(li, lin_)
        inn += blob([(-W_ + 36, -138), (W_ - 36, -138), (W_ - 34, -170), (-W_ + 34, -170)], lin_dk, .7)
        inn += blob(rect_pts(-W_ + 56, -118 - lh * .55, W_ - 56, -118 - lh * .55 + 26, 4), "#8a6a56", .9)
        inn += blob(rect_pts(-W_ + 56, -118 - lh * .8, W_ - 56, -118 - lh * .8 + 22, 4), "#8a6a56", .9)
        inn += blob(rect_pts(-80, -118 - lh * .38, 80, -118 - lh * .3, 3), "#c9b790", .9)
        o.append(shape(lp, shell, inn, w=5, seed=8600))
    # внутренняя часть корпуса (подкладка сверху, перспектива)
    tray = [(-W_ + 10, -118, 1), (W_ - 10, -118, 1), (W_ - 26, -146, 1), (-W_ + 26, -146, 1)]
    o.append(shape(tray, lin_, blob([(-W_ + 26, -146), (W_ - 26, -146), (W_ - 16, -132), (-W_ + 16, -132)], lin_dk, .8), w=4.2, seed=8602))
    # содержимое
    if fill > .02:
        for j in range(6):
            col = SWEATER_COLS[(j * 5 + 2) % 6]
            cxj = -110 + j * 44 + (rnd(j + 3) - .5) * 20
            cyj = -128 - 34 * fill * (1 + .4 * math.sin(j * 1.7)) - bulge * 20
            o.append(G(sweater(col, .5 + .12 * (j % 2), 8700 + j * 7, sleeve=.3 * math.sin(t * 5 + j)), cxj, cyj, 1.0, (rnd(j + 9) - .5) * 40))
        # торчащий рукав и штанина
        o.append(G(sweater("#4f7fa8", .45, 8760, sleeve=0), W_ - 40, -150 - 30 * fill, 1.0, 38))
    # передняя стенка (сжатие по y вокруг низа)
    fh = 118 * squash
    fw = W_ * (1 + .03 * bulge)
    fr = [(-fw, -fh, 1), (fw, -fh, 1), (fw, 0, 1), (-fw, 0, 1)]
    inn = blob([(-fw, -fh * .3), (fw, -fh * .3), (fw, 0), (-fw, 0)], shell_dk, .75)
    inn += blob(rect_pts(-fw + 14, -fh * .66, fw - 14, -fh * .66 + 7), "#c9ced8", .9)
    inn += blob(rect_pts(fw - 70, -fh, fw - 40, 0), shell_dk, .5)
    for j in range(-3, 4):
        inn += line([(j * fw / 3.6, -fh + 8), (j * fw / 3.6, -8)], 4, shell_dk, taper=.05, wmin=.95, seed=8640 + j, op=.9)
    o.append(shape(fr, shell, inn, w=5, seed=8603))

    for sx in (-1, 1):
        o.append(shape([(sx * fw, -fh, 1), (sx * (fw - 34), -fh, 1), (sx * (fw - 34), -fh + 30, 1), (sx * fw, -fh + 44, 1)], "#c9ced8", "", w=3.4, seed=8610 + sx))
        o.append(shape([(sx * fw, 0, 1), (sx * (fw - 34), 0, 1), (sx * (fw - 34), -30, 1), (sx * fw, -44, 1)], "#c9ced8", "", w=3.4, seed=8612 + sx))
    o.append(shape(rect_pts(-26, -fh * .78, 26, -fh * .78 + 34, 7), "#c9ced8", blob(rect_pts(-16, -fh * .78 + 8, 16, -fh * .78 + 24, 3), "#7a808e", .9), w=3.6, seed=8620))
    for sx in (-1, 1):
        o.append(shape(ellipse_pts(sx * (W_ - 36), 14, 14, 14, 10), "#3a3e4c", "", w=3, seed=8630 + sx))
    return Gxy("".join(o), x + shake, y, k, k)


# ═════════════════════════ Дима стоя ═════════════════════════
def hand_spec(curl=.25, d=None, thumb=None, k=1.0):
    h = dict(kind="open", flip=1, dir=(1, .35), curl=(curl, curl, curl, curl * .9), spread=.04 + .12 * (1 - curl), thumb=curl if thumb is None else thumb, bend=.1, k=k)
    if d:
        h["dir"] = d
    return h


def stand(t, x, *, lean=.04, ha=0.0, expr=None, n_t=None, f_t=None, hands=None, run=0.0, ph=0.0, bob=0.0, torso_k=1.0, head_off=(0, 0), sn=None, sf=None,
          sx=1.0, hip_dy=0.0, crouch=0.0):
    """Дима стоит/бежит на месте с пола FLOOR_Y; run — размах шага (0 — стоит), ph — фаза шага. Возвращает dict слоёв people.draw + 'x'."""
    e = dict(lid=.9, look=(.5, .1), brows="worry", mouth="flat", flush=.0)
    if expr:
        e.update(expr)
    hy = 1108 + bob + hip_dy + 60 * crouch - 40 * (1 - min(1.0, run * 3))
    shx = x + 240 * math.sin(lean) + 6
    feet = {}
    for side, off in (("n", 0.0), ("f", .5)):
        c = math.sin(2 * math.pi * (ph + off))
        lift = max(0.0, math.cos(2 * math.pi * (ph + off))) * run
        ax = x + (18 if side == "n" else -22) + c * 62 * run
        ay = FLOOR_Y - (6 if side == "f" else 0) - 54 * lift * (1 if run > 0 else 0)
        feet[side] = ((ax, ay), -.5 * lift if run > 0 else 0.0)
    n_t = n_t or (x + 40, 960)
    f_t = f_t or (x - 40, 960)
    sn = sn if sn is not None else (-1 if n_t[0] >= shx else 1)
    sf = sf if sf is not None else (-1 if f_t[0] >= shx else 1)
    arms = {"n": ("ik", n_t, sn), "f": ("ik", f_t, sf)}
    hands = hands or {"n": hand_spec(.35), "f": hand_spec(.35)}
    p = dict(hip=(x, hy), scale=BS, lean=lean, torso_k=torso_k, feet=feet, arms=arms, hands=hands, expr=e, head_ang=ha, head_off=head_off, hood=0.0, strings=(0, 0))
    d = people.draw(p, "dima")
    d["x"] = x
    d["sx"] = sx
    return d


def flipx(s, x, sx):
    """Отражение/сжатие героя по горизонтали вокруг его бёдер (разворот), sx −1…1."""
    if abs(sx - 1) < 1e-3:
        return s
    return f'<g transform="translate({f(x * (1 - sx))} 0) scale({sx:.4f} 1)">{s}</g>'


def dima_layers(d):
    sx, x = d["sx"], d["x"]
    return (flipx(d.get("legs", ""), x, sx), flipx(d["arm_f"], x, sx), flipx(d["body"], x, sx), flipx(d["arm_n"], x, sx))


def wrist_w(d, side, x_):
    """Запястье в мире с учётом разворота."""
    w = d["wrist"][side]
    return (d["x"] + (w[0] - d["x"]) * d["sx"], w[1])


def head_w(d):
    h = d["head"]
    return (d["x"] + (h[0] - d["x"]) * d["sx"], h[1])


# ═════════════════════════ значки ═════════════════════════
def stress_marks(x, y, t, k=1.0, col="#e8452c", r0=150):
    o = []
    for i, ang in enumerate((-150, -110, -70, -30)):
        a = math.radians(ang)
        j = 7 * math.sin(t * 26 + i * 2.1)
        a0, a1 = r0 + j, r0 + 60 + j * 1.5
        o.append(line([(x + a0 * math.cos(a), y + a0 * math.sin(a)), (x + a1 * math.cos(a), y + a1 * math.sin(a))], 11 * k, col, taper=.5, wmin=.2, seed=9100 + i, peak=.5))
    return "".join(o)


def sweat_drop(x, y, t, seed, s=1.0):
    ph = (t * 1.5 + seed * 0.41) % 1.0
    a = math.sin(ph * math.pi) ** .6
    dy = ph * 110 * s
    d = [(0, -34), (10, -12, 1), (14, 4), (0, 14), (-14, 4), (-10, -12, 1)]
    d = [(p[0] * s + x, p[1] * s + y + dy) + ((1,) if len(p) > 2 else ()) for p in d]
    if a < .15:
        return ""
    return shape(d, "#a8dcf5", blob([(x - 2 * s, y + dy - 4 * s), (x + 8 * s, y + dy + 2 * s), (x, y + dy + 10 * s)], "#ffffff", .8), w=3.4 * s, seed=seed + 3)


def dust(t, t0, x, y, n=7, dur=.5):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return ""
    o = []
    for i in range(n):
        a = -math.pi * (i + .5) / n
        r = 20 + 90 * ease_out(u)
        o.append(f'<circle cx="{x + r * math.cos(a) * 1.3:.1f}" cy="{y + r * math.sin(a) * .6:.1f}" r="{(10 * (1 - u) + 2):.1f}" fill="#f1e7d8"/>')
    return "".join(o)


def speed_lines(x, y, t, k=1.0, dirx=-1):
    o = []
    for i in range(3):
        yy = y + (i - 1) * 54 + 6 * math.sin(t * 40 + i)
        o.append(line([(x, yy), (x + dirx * (90 + 30 * i) * k, yy + 4)], 7, "#8f8a7e", taper=.9, wmin=.05, seed=9300 + i, peak=.1, op=.8))
    return "".join(o)


def world(t, items_back, dm, cam, *, variant="mess", mid="", front="", held="", sun=1.0, motes=True, suit=""):
    """Слои: комната → чемодан → вещи сзади → Дима (ноги, дальняя рука, тело, предмет в руке, ближняя рука) → вещи спереди."""
    D.set_ink(cam[2])
    if variant not in _ST:
        _ST[variant] = room56(variant)
    lg, af, bd, an = dima_layers(dm) if dm else ("", "", "", "")
    w = [_ST[variant], suit, items_back, mid, lg, af, bd, held, an, front]
    if motes:
        w.append(sun_motes(t))
    return f'<g transform="{lib.cam(*cam)}">{"".join(w)}</g>'


def whip(out, t, t0, dist=260):
    wp = ease_out(clamp(1 - (t - t0) / .32), 2)
    if wp > .02:
        fid = "whip1"
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{f(70 * wp)} 0"/></filter>')
        return f'<g filter="url(#{fid})" transform="translate({f(-dist * wp)} 0)">{out}</g>'
    return out


# ═════════════════════════ s01 ═════════════════════════
SUIT_X, SUIT_Y = 905, 1472


def frame01(t):
    base_z = 1.14
    if t < .22:
        z = base_z / 1.4 + (base_z - base_z / 1.4) * ease_out(t / .22, 3)
    else:
        z = base_z + .06 * ease_io(clamp((t - .22) / 1.4))
    rot = -3.2 * (1 - ease_out(t / .45, 2.5)) + .5 * math.sin(t * 9) * math.exp(-t * 1.5)
    # маршрут: от шкафа к чемодану и обратно, разворот в крайних точках
    per = 0.78
    ph = (t / per + .1) % 1.0
    x = 560 + 160 * math.sin(2 * math.pi * (t / per) - 1.2)
    vx = math.cos(2 * math.pi * (t / per) - 1.2)
    sx = math.tanh(vx * 3.2)
    run = 1.0
    stride = t * 3.9
    bob = -16 * abs(math.sin(2 * math.pi * stride))
    lean = .2 * max(0.0, sx) + .1 * sx * 0 - .05
    ha = .1 * math.sin(t * 20)
    flail = math.sin(t * 2 * math.pi * 4.2)
    # руки: ближняя обнимает ворох у груди, дальняя машет
    n_t = (x + 190, 940 + 26 * flail)
    f_t = (x + 20, 590 - 50 * flail)
    expr = dict(lid=.95, look=(.55 * sx, .25), brows="worry", mouth="talk", open=.55 + .3 * math.sin(t * 17), smile=0, flush=.4 * smooth(0, 1, t), hair=3.5 * math.sin(t * 31))
    d = stand(t, x, lean=lean, ha=ha, expr=expr, n_t=n_t, f_t=f_t, hands={"n": hand_spec(.6, (.8, -.2)), "f": hand_spec(.15, (.4, -1))}, run=run, ph=stride, bob=bob, sx=sx if abs(sx) > .05 else .05)
    # вещи летят из шкафа в чемодан с промахами: свой «фонтан» каждые 0.11 с
    fl, fb = [], []
    for i in range(24):
        t0 = i * .105 - .25 + (rnd(i) - .5) * .05
        u = t - t0
        dur = .95
        if u < 0 or u > dur:
            continue
        a = u / dur
        x0, y0 = 200 + rnd(i + 5) * 110, 700 + rnd(i + 9) * 260
        tx = 760 + rnd(i + 2) * 520
        px = x0 + (tx - x0) * ease_out(a, 1.2)
        py = y0 - 240 * math.sin(math.pi * a) * (.6 + rnd(i + 4) * .8) + 360 * a * a * (rnd(i + 7) * .6 + .4)
        kind = ("sw", "tee", "sock", "sw", "tee")[i % 5]
        g_ = G(item(kind, i, .62 + .18 * rnd(i + 1)), px, py, 1.0, 600 * a * (1 if i % 2 else -1) + rnd(i) * 60)
        fb.append(g_)
    sx_ = sx
    front = "".join(fl)
    suit = suitcase(SUIT_X, SUIT_Y, 1.3, lid=1.0, fill=0.0, t=t)
    # хлопок часов: минутная стрелка прыгает
    ck = clock(445, 430, 56, t, jump=t * 40, ring_shake=0)
    held = ""
    hp = head_w(d)
    ex = stress_marks(hp[0], hp[1] - 20, t, r0=170) + "".join(sweat_drop(hp[0] + dx * (1 if sx_ >= 0 else -1), hp[1] - 80 + k * 30, t, k + 1, 1.3) for k, dx in enumerate((-125, 135)))
    cam = (650 + 20 * math.sin(t * 5) * math.exp(-t), 1150, z, rot)
    if "clock" not in _ST:
        pass
    out = world(t, "".join(fb), d, cam, mid=ck, front=front + ex, suit=suit)
    return out


# ═════════════════════════ s02 ═════════════════════════
def alarm(cx, cy, r, t, ring, wobble=0.0):
    """Будильник без цифр: круглый корпус, два звонка с молоточком, ножки; стрелка прыгает; ring 0..1 — сила тряски."""
    shake = ring * (7 * math.sin(t * 2 * math.pi * 17) + 3 * math.sin(t * 2 * math.pi * 29))
    o = []
    o.append(blob(ellipse_pts(cx + 10, cy + r + 30, r * 1.0, 20, 20), "#2a1408", .3))
    # ножки
    for sx in (-1, 1):
        o.append(shape([(cx + sx * r * .55, cy + r * .84, 1), (cx + sx * r * .92, cy + r * 1.16, 1), (cx + sx * r * .76, cy + r * 1.2, 1), (cx + sx * r * .42, cy + r * .92, 1)], "#b8394a", "", w=5, seed=8800 + sx))
    # звонки (две половинки-купола), молоточек между
    for sx in (-1, 1):
        bx = cx + sx * r * .62
        by = cy - r * .84 - ring * 6 * math.sin(t * 60 + sx)
        dome = [(bx - sx * 0, by + 40 * 0)]
        pts = [(bx + r * .42 * math.cos(math.radians(a)), by + r * .34 * math.sin(math.radians(a))) for a in range(180, 361, 20)] + [(bx + r * .42, by + 8, 1), (bx - r * .42, by + 8, 1)]
        pts = [(p[0], p[1]) + ((1,) if len(p) > 2 else ()) for p in pts]
        o.append(shape(pts, "#e6b955", blob([(bx, by - r * .34), (bx + r * .42, by), (bx + r * .42, by + 8), (bx, by + 8)], "#c4932d", .8) +
                       blob(ellipse_pts(bx - r * .15, by - r * .15, r * .14, r * .07, 8), "#fff6d0", .8), w=5, seed=8810 + sx))
        o.append(line([(bx, by + 8), (cx + sx * r * .26, cy - r * .94)], 5, INK, taper=.05, wmin=.95, seed=8812 + sx))
    hm_a = 28 * math.sin(t * 2 * math.pi * 21) * ring
    o.append(line([(cx, cy - r * 1.02), (cx + 4 * hm_a / 28 * 6, cy - r * 1.32)], 6, INK, taper=.05, wmin=.95, seed=8820))
    o.append(shape(ellipse_pts(cx + 4 * hm_a / 28 * 6, cy - r * 1.36, 17, 17, 12), "#8b8d98", "", w=4, seed=8821))
    # корпус
    body = ellipse_pts(cx, cy, r, r, 36)
    o.append(shape(body, "#d9475a", blob(ellipse_pts(cx + r * .1, cy + r * .1, r * .98, r * .98, 24), "#b8394a", .9) + blob(ellipse_pts(cx - r * .2, cy - r * .3, r * .55, r * .3, 16), "#f07a86", .8), w=7, seed=8830))
    face = ellipse_pts(cx, cy, r * .78, r * .78, 32)
    inn = ""
    for k in range(12):
        a = math.radians(k * 30 - 90)
        r0 = r * .78 * (.78 if k % 3 else .68)
        inn += line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r * .78 * .92 * math.cos(a), cy + r * .78 * .92 * math.sin(a))], 8 if k % 3 == 0 else 5, INK, taper=.1, wmin=.9, seed=8840 + k)
    o.append(shape(face, "#fbf6ea", blob(ellipse_pts(cx - r * .2, cy - r * .25, r * .5, r * .4, 14), "#ffffff", .5) + inn, w=5.4, seed=8839))
    # стрелки: минутная прыгает на 30° рывками, часовая тоже
    jp = math.floor(t * 5) % 12
    jf = (t * 5) % 1.0
    ma = math.radians(-90 + 30 * (jp + ease_out(clamp(jf * 4), 3)))
    ha = math.radians(-70 + 6 * (jp))
    o.append(line([(cx, cy), (cx + r * .38 * math.cos(ha), cy + r * .38 * math.sin(ha))], 16, INK, taper=.15, wmin=.8, seed=8860))
    o.append(line([(cx, cy), (cx + r * .6 * math.cos(ma), cy + r * .6 * math.sin(ma))], 11, INK, taper=.15, wmin=.8, seed=8861))
    o.append(shape(ellipse_pts(cx, cy, 14, 14, 10), "#d6322c", "", w=3.4, seed=8862))
    return G("".join(o), shake, 0)


def ring_lines(cx, cy, r, t, ring):
    """Дуги звука вокруг звонков."""
    o = []
    if ring < .05:
        return ""
    for sx in (-1, 1):
        for j in range(3):
            ph = (t * 9 + j * .33 + (0 if sx < 0 else .17)) % 1.0
            rr = r * (.25 + .6 * ph)
            ang0, ang1 = (150, 220) if sx < 0 else (-40, 30)
            bx, by = cx + sx * r * .62, cy - r * .9
            pts = [(bx + rr * 1.4 * math.cos(math.radians(a)) + sx * 40, by + rr * 1.1 * math.sin(math.radians(a))) for a in np.linspace(ang0, ang1, 7)]
            o.append(line(pts, 9 * (1 - ph * .6), "#e8452c", taper=.5, wmin=.2, seed=8900 + j + (5 if sx > 0 else 0), peak=.5, op=ring))
    return "".join(o)


def frame02(t):
    r1 = ease_out(clamp(1 - (t - T_CHAS) / .75), 2) * (t >= T_CHAS)
    r2 = ease_out(clamp(1 - (t - T_VYHODA) / .75), 2) * (t >= T_VYHODA)
    ring = clamp(r1 * 1.0 + r2 * 1.0, 0, 1) if t >= T_CHAS else 0.0
    u = clamp((t - 1.2) / 2.2)
    z = 1.02 + .20 * ease_in(u, 1.4) + .06 * math.exp(-(t - T_CHAS) * 7) * (t >= T_CHAS) + .06 * math.exp(-(t - T_VYHODA) * 7) * (t >= T_VYHODA)
    shake = (10 * math.sin(t * 61) * (r1 + r2), 8 * math.sin(t * 53 + 1) * (r1 + r2))
    D.set_ink(z)
    cam = lib.cam(560 + 40 * u + shake[0], 1000 - 60 * u + shake[1], z, 1.4 * math.sin(t * 2.3) + 2.2 * (r1 + r2) * math.sin(t * 40))
    o = []
    # фон: стена, полка внизу, слева виден край шкафа
    o.append(f'<rect x="-600" y="-400" width="2400" height="2800" fill="#c4dad4"/>')
    for k in range(-5, 12):
        o.append(f'<rect x="{k * 130}" y="-400" width="22" height="2800" fill="#a3c2bd" opacity=".35"/>')
    o.append(f'<rect x="-600" y="1230" width="2400" height="1200" fill="#9c7656"/>')
    o.append(shape(rect_pts(-600, 1216, 1800, 1246), "#efe6d6", "", w=4, seed=8950))
    # тумбочка со столешницей под часами
    o.append(shape(rect_pts(-40, 1190, 1120, 1260, 8), "#c88a58", blob(rect_pts(-40, 1236, 1120, 1260), "#a8693f", .85), w=5, seed=8951))
    o.append(blob(ellipse_pts(300, 1230, 160, 14, 14), "#2a1408", .25))
    acx, acy, ar = 560, 760, 330
    pop = 1 + .05 * math.sin(t * 2 * math.pi * 6) * ring
    o.append(G(alarm(0, 0, ar, t, ring), acx, acy, pop))
    o.append(ring_lines(acx, acy, ar * 1.0, t, ring))
    # Дима в нижнем правом углу: голова и плечи крупно, хватается за голову (с 1.5), сгребает чемодан (с 1.89)
    gr = smooth(T_CHAS - .08, T_CHAS + .2, t)
    gb = smooth(T_VYHODA - .02, T_VYHODA + .25, t)
    dx0 = 840 + 20 * math.sin(t * 2 * math.pi * 6) * ring
    hx, hy = dx0, 1390 - 18 * gr
    # более крупный Дима: свой масштаб, рисуем целиком и режем кадром
    sc = 1.55
    lean = .08 - .06 * gr
    he = (dx0 - 80 * 0, 0)
    expr = dict(lid=.55 + .45 * gr, look=(.2, .3), brows="worry" if gr > .3 else "tired", mouth="talk" if gr > .2 else "tired", open=.8 * gr, smile=0, flush=.5 * gr,
                hair=4 * math.sin(t * 40) * ring, closed=.0)
    hhx = dx0
    p = dict(hip=(dx0, 1760), scale=BS * sc, lean=lean, torso_k=1.0, feet=None, arms={"n": ("ik", (hhx - 40 + 10 * math.sin(t * 50) * gr, lerp(1600, 1215, gr)), 1),
                                                                                     "f": ("ik", (hhx - 120, lerp(1640, 1180, gr)), 1)},
             hands={"n": hand_spec(.9, (.1, -1), k=1.55), "f": hand_spec(.9, (.3, -1), k=1.55)}, expr=expr, head_ang=.04 * math.sin(t * 30) * ring, head_off=(0, 0), hood=0, strings=(0, 0))
    d = people.draw(p, "dima")
    o.append(d["arm_f"] + d["body"] + d["arm_n"])
    # чемодан влетает сверху слева (его сгребли со шкафа) на «выхода»
    sw_ = smooth(T_VYHODA - .05, T_VYHODA + .35, t)
    if t > T_VYHODA - .05:
        sx_ = lerp(-300, 190, ease_out(sw_, 2.2))
        sy_ = lerp(-200, 1250, ease_out(sw_, 1.8))
        rot_ = lerp(-80, -6, ease_out(sw_, 2.0)) + 6 * math.sin((t - T_VYHODA) * 25) * math.exp(-(t - T_VYHODA) * 4)
        o.append(G(suitcase(0, 0, 1.25, lid=0, fill=0, t=t), sx_, sy_, 1.0, rot_))
        # рука Димы тянет за ручку
    o.append(dust(t, T_VYHODA + .3, 250, 1210, 6, .5))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════ s04 ═════════════════════════
THROWS = [T_TRI, T_SVITERA, T_NA]


def frame04(t):
    # запястье ближней руки: ключи (время, x, y): замах назад к шкафу, бросок вперёд над головой
    keys = [(5.28, 650, 1000), (5.55, 610, 960), (5.66, 470, 870), (T_TRI - .08, 625, 590), (T_TRI + .02, 830, 660), (T_TRI + .08, 690, 850),
            (T_SVITERA - .12, 470, 870), (T_SVITERA - .06, 625, 590), (T_SVITERA + .02, 830, 660), (T_SVITERA + .16, 700, 850), (T_NA - .23, 470, 870),
            (T_NA - .07, 625, 590), (T_NA + .02, 830, 660), (T_NA + .3, 680, 920), (7.0, 650, 1000), (8.2, 650, 1000)]
    wr = kf(t, keys)
    # дальняя рука — хватает вторую порцию, машет в такт
    fk = [(5.28, 560, 990), (5.62, 480, 880), (5.9, 600, 700), (6.16, 480, 880), (6.4, 640, 760), (6.75, 480, 870), (7.1, 610, 960), (7.6, 640, 990), (8.2, 640, 990)]
    fw = kf(t, fk)
    x = 600 + 8 * math.sin(t * 5) * (t < 7)
    lean = lerp(-.12, .22, clamp((wr[0] - 450) / 380))
    hit = [math.exp(-(t - T0) * 9) for T0 in THROWS if t >= T0]
    pulse = sum(hit)
    # четвёртый свитер падает на голову
    t_fall = 7.0
    fall = clamp((t - t_fall) / .22)
    on_head = t >= t_fall + .22
    sad = smooth(7.2, 7.5, t)
    expr = dict(lid=.95 - .2 * sad, look=(.3, .3), brows="worry" if t < 7.2 else "tired", mouth="talk" if t < 7.2 else "flat", open=.5 + .4 * math.sin(t * 22), smile=0, flush=.3, hair=2.5 * math.sin(t * 31) * (1 if t < 7.1 else 0))
    # после падения свитера руки опускаются, Дима моргает
    sn_hand = hand_spec(.8, (.2, -1))
    sf_hand = hand_spec(.7, (.2, -1))
    d = stand(t, x, lean=lean + .03 * pulse, ha=.06 * math.sin(t * 7), expr=expr, n_t=(wr[0], wr[1]), f_t=(fw[0], fw[1]), hands={"n": sn_hand, "f": sf_hand}, run=0.12 if t < 7 else 0, ph=t * 5.2,
              bob=-8 * pulse)
    # свитера в воздухе (дуга вправо за кадр) и в руке до броска
    held = ""
    fly = []
    for i, T0 in enumerate(THROWS):
        u = t - T0
        col_i = [0, 1, 2][i]
        if -.26 < u < 0:
            pass
        if u >= 0 and u < .8:
            p0 = np.array([820.0, 640.0])
            p1 = np.array([1230.0, 300.0 + 50 * i])
            a = u / .8
            px = p0[0] + (p1[0] - p0[0]) * ease_out(a, 1.1)
            py = p0[1] + (p1[1] - p0[1]) * a - 250 * math.sin(math.pi * a * .9) + 220 * a * a
            fly.append(G(sweater(SWEATER_COLS[(col_i * 2) % 6], .9, 7400 + i * 11, sleeve=math.sin(u * 30) * .8), px, py, 1.0, -420 * ease_out(a, 1.3) + 20 * i))
    # свитер в ближней руке между захватом и броском
    for i, T0 in enumerate(THROWS):
        win = (T0 - .28, T0 + .02) if i != 0 else (T0 - .3, T0 + .02)
        if win[0] <= t < T0 + .0:
            w0 = wrist_w(d, "n", x)
            held = G(sweater(SWEATER_COLS[(i * 2) % 6], .72, 7500 + i, sleeve=.8 * math.sin(t * 40)), w0[0] + 30, w0[1] - 12, 1.0, 28 * math.sin(t * 20) + 20)
    # четвёртый на голове
    hp = head_w(d)
    head_sw = ""
    if t >= t_fall:
        if not on_head:
            hy = lerp(hp[1] - 700, hp[1] - 120, ease_in(fall, 1.6))
            head_sw = G(sweater(SWEATER_COLS[1], .86, 7600, sleeve=.4), hp[0] + 10, hy, 1.0, lerp(-60, 8, fall))
        else:
            u = t - (t_fall + .22)
            sq = 1 + .12 * math.exp(-u * 8) * math.sin(u * 40)
            head_sw = G(sweater_hat(SWEATER_COLS[1], .92, 7600, sway=math.sin(u * 5) * math.exp(-u * 2) + .2 * math.sin(u * 40) * math.exp(-u * 6)), hp[0] + 4, hp[1] - 76 + 6 * (sq - 1) * 40, 1.0, 0)
    front = "".join(fly) + head_sw + dust(t, t_fall + .22, hp[0], hp[1] + 130, 5, .4)
    ex = ""
    if t < 7.0:
        ex = speed_lines(x - 110, 860, t, .8, -1) if pulse > .2 else ""
    # у шкафа сыплются вещи после бросков (на пол)
    cam = (520 + 130 * ease_io(clamp((t - 5.28) / 2.6)) + 6 * pulse * math.sin(t * 50), 1215 - 10 * pulse, 1.22 + .05 * ease_io(clamp((t - 5.28) / 2.6)) + .02 * pulse, -1.2 + .9 * math.sin(t * 2.2))
    # открытый чемодан сзади справа вне кадра: ничего. Разбросанные вещи у ног:
    floor_stuff = ""
    for i, T0 in enumerate((T_TRI, T_SVITERA, T_NA, 7.0)):
        if t > T0 + .5:
            floor_stuff += G(sock(SWEATER_COLS[(i + 3) % 6], .8, 7700 + i), 330 + 60 * i, FLOOR_Y + 10, 1.0, 80 * i - 40)
    return world(t, floor_stuff, d, cam, held=held, front=front + ex)


# ═════════════════════════ s06 ═════════════════════════
def question_mark(t, x, y, s=1.0, wob=0.0):
    R = 46 * s
    pts = [(x + R * math.cos(a), y + R * math.sin(a)) for a in np.linspace(math.pi, 2.5 * math.pi, 14)] + [(x + R * .15, y + R * 1.15), (x, y + R * 1.5)]
    pts = [(p[0], p[1]) for p in pts]
    o = line(pts, 22 * s, INK, taper=.05, wmin=.9, seed=9500)
    o += shape(ellipse_pts(x, y + R * 1.5 + 36 * s, 15 * s, 15 * s, 10), "#d6322c", "", w=3, seed=9501)
    return o


def hob(cx, cy, s=1.0):
    """Пустая плита сверху (в перспективе): четыре конфорки-кольца и ручки, ничего на них не стоит."""
    o = []
    top = [(-130, -70, 1), (130, -70, 1), (160, 70, 1), (-160, 70, 1)]
    inner = ""
    for (px, py) in ((-64, -22), (64, -22), (-84, 36), (84, 36)):
        inner += blob(ellipse_pts(px, py, 44, 22, 18), "#2f323c")
        inner += blob(ellipse_pts(px, py, 28, 13, 16), "#5b5f6e")
        inner += blob(ellipse_pts(px, py, 11, 5, 10), "#2f323c")
    o.append(shape(top, "#d9dde6", inner + blob([(-160, 60), (160, 60), (160, 70), (-160, 70)], "#a8adbb", .9), w=5, seed=9510))
    o.append(shape(rect_pts(-160, 70, 160, 112, 4), "#c8ccd8", blob(rect_pts(-160, 98, 160, 112), "#9096a8", .8), w=4.4, seed=9511))
    for k, x in enumerate((-100, -34, 34, 100)):
        o.append(shape(ellipse_pts(x, 92, 15, 15, 12), "#e8ebf2", line([(x, 92), (x + 8, 84)], 3.4, INK, seed=9520 + k), w=3.6, seed=9515 + k))
    return G("".join(o), cx, cy, s)


def cloud_pts(cx, cy, rx, ry, n=9, seed=0):
    pts = []
    hw = math.pi / n
    for k in range(n):
        ac = 2 * math.pi * k / n
        for da, rr, cor in ((-hw, 0.88, 1), (-hw * .55, 1.08, 0), (0, 1.14 + 0.03 * math.sin(k * 2.3 + seed), 0), (hw * .55, 1.08, 0)):
            a = ac + da
            pts.append((cx + rx * rr * math.cos(a), cy + ry * rr * math.sin(a)) + ((1,) if cor else ()))
    return pts


def thought_cloud(cx, cy, rx, ry, inner, sx=1.0, sy=1.0, rot=0.0, seed=1):
    cl = cloud_pts(0, 0, rx, ry, 9, seed)
    cid = lib.clip_of(cl)
    body = blob(rect_pts(-rx * 1.4, -ry * 1.5, rx * 1.4, ry * 1.5), "#f4f1ff")
    body += blob(rect_pts(-rx * 1.4, ry * .35, rx * 1.4, ry * 1.5), "#dcd8f2", .8)
    art = shape(cl, "#f4f1ff", f'<g clip-path="url(#{cid})">{body}{inner}</g>', w=7, seed=9300 + seed)
    return f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({sx:.4f} {sy:.4f})">{art}</g>'


def bubbles(x0, y0, x1, y1, k):
    o = []
    for j, (fr, r_) in enumerate([(.18, 20), (.45, 31), (.76, 44)]):
        u = clamp(k * 3 - j * .6)
        if u <= 0:
            continue
        px, py = x0 + (x1 - x0) * fr, y0 + (y1 - y0) * fr
        o.append(shape(ellipse_pts(px, py, r_ * back_out(u, 2), r_ * back_out(u, 2), 14), "#f4f1ff", "", w=4.6, seed=9400 + j))
    return "".join(o)


def frame06(t):
    x = 650
    scratch = math.sin(t * 2 * math.pi * 5.5)
    shrug = smooth(T_NET + .2, T_NET + .5, t)
    u_s = 1 - shrug
    lean = .09 + .03 * math.sin(t * 2.4)
    ha = .05 + .04 * scratch * u_s
    hpn = (x + 110, 740)
    # дальняя рука чешет затылок (запястье у затылка, колеблется), ближняя висит; после лопания — оба плеча вверх
    ex_ = (hpn[0] - 140 + 22 * scratch, hpn[1] - 40 + 12 * abs(scratch))
    n_t = (x + 80 + shrug * 80, 960 - shrug * 150)
    f_t = (ex_[0] * u_s + (x - 190) * shrug, ex_[1] * u_s + (770) * shrug)
    expr = dict(lid=.82, look=(.6, .55 - .9 * shrug), brows="det" if t < T_NET else "up", mouth="flat" if t < T_NET else "talk", open=.2 * shrug, smile=0, flush=.15, hair=2 * math.sin(t * 20) * u_s)
    d = stand(t, x, lean=lean, ha=ha, expr=expr, n_t=n_t, f_t=f_t, hands={"n": hand_spec(.4 - .2 * shrug), "f": hand_spec(.85 * u_s + .1 * shrug, (.4, -1))},
              bob=-14 * shrug * math.exp(-(t - T_NET - .2) * 3) * 0 + 5 * math.sin(t * 2 * math.pi * 1.2), torso_k=1.0 - .04 * shrug)
    hp = head_w(d)
    appear = smooth(T_VDRUG - .05, T_VDRUG + .38, t)
    burst = t >= T_NET
    bu = clamp((t - T_NET) / .5)
    cl = ""
    if appear > .02 and not burst:
        sc = .85 + .15 * back_out(appear, 2.0)
        bx, by = hp[0] + 30, hp[1] - 330
        jig = 1 + .03 * math.sin(t * 22) * smooth(T_NET - .5, T_NET, t)
        inner = hob(0, 40, 1.35) + G(question_mark(t, 0, 0, 1.0), 12, -150, 1.0, 6 * math.sin(t * 4))
        inner = G(hob(0, 55, 1.0), 0, 0) + G(question_mark(t, 0, 0, .8), 0, -105, 1.0, 6 * math.sin(t * 4))
        cl = bubbles(hp[0] + 10, hp[1] - 130, bx - 20, by + 190 * sc, appear)
        cl += thought_cloud(bx, by, 235 * sc, 195 * sc, inner, (1 + .06 * math.sin(t * 22) * smooth(T_NET - .4, T_NET, t)) * sc / sc, (1 - .04 * math.sin(t * 22) * smooth(T_NET - .4, T_NET, t)), 2 * math.sin(t * 3), 3)
    if burst and bu < 1:
        bx, by = hp[0] + 30, hp[1] - 330
        for i in range(10):
            a = i / 10 * 2 * math.pi + .3
            r_ = 60 + 330 * ease_out(bu, 2.2)
            px, py = bx + r_ * math.cos(a) * 1.15, by + r_ * math.sin(a) * .95 + 120 * bu * bu
            rr_ = 52 * (1 - bu * .8)
            cl += shape(ellipse_pts(px, py, rr_, rr_ * .85, 12), "#f4f1ff", "", w=4.6, seed=9600 + i)
        cl += G(question_mark(t, 0, 0, .8), bx + 230 * bu, by - 105 + 520 * bu * bu, 1.0, 40 * bu)
        # хлопок: звёздочка-«пуф»
        for i in range(8):
            a = i / 8 * 2 * math.pi
            cl += line([(bx + 70 * math.cos(a), by + 70 * math.sin(a)), (bx + (70 + 120 * (1 - bu)) * math.cos(a), by + (70 + 120 * (1 - bu)) * math.sin(a))], 10, "#e8b64a", taper=.7, wmin=.1, seed=9650 + i, op=1 - bu)
    # полный чемодан перед Димой, вещи торчат
    suit = suitcase(940, 1472, 1.3, lid=1.0, fill=1.0, t=t, bulge=.5 + .2 * math.sin(t * 3))
    pz = 1.0 + .2 * ease_io(clamp((t - 10.3) / 1.9))
    cam = (700 - 40 * ease_io(clamp((t - 10.3) / 1.9)), 1090 - 40 * ease_io(clamp((t - 10.3) / 1.9)), 1.1 + .12 * ease_io(clamp((t - 10.3) / 1.9)), .8 * math.sin(t * 1.8) + 1.2 * math.exp(-(t - T_NET) * 8) * (t >= T_NET) * math.sin(t * 40))
    return world(t, "", d, cam, front=cl, suit=suit)


# ═════════════════════════ s13 ═════════════════════════
def cup(x, y, k=1.0, t=0.0, tilt=0.0):
    """Чашка с паром (рукой держат за ручку)."""
    o = []
    body = [(-38, -70, 1), (38, -70, 1), (34, -8), (22, 0, 1), (-22, 0, 1), (-34, -8)]
    o.append(shape(body, "#f3ede2", blob([(10, -70), (38, -70), (34, -8), (22, 0), (8, 0)], "#d8d0c0", .9) + blob(rect_pts(-38, -50, 38, -36), "#3f7a72", .9), w=4.2, seed=3210))
    o.append(line([(36, -56), (66, -52), (64, -22), (30, -18)], 7, INK, taper=.1, wmin=.8, seed=3211))
    o.append(line([(36, -56), (66, -52), (64, -22), (30, -18)], 3, "#f3ede2", taper=.1, wmin=.8, seed=3212))
    o.append(blob(ellipse_pts(0, -70, 38, 8, 12), "#6b3f26"))
    for k_, dx in enumerate((-18, 2, 22)):
        ph = t * 1.3 + k_ * 1.7
        pts = [(dx + 8 * math.sin(ph + j * .8), -90 - j * 22) for j in range(6)]
        o.append(line(pts, 5, "#f4f1ea", taper=.8, wmin=.1, seed=3220 + k_, peak=.4))
    return G("".join(o), x, y, k, tilt)


def bed(x, y):
    """Кровать сбоку-спереди: рама, матрас, подушка, плед."""
    o = [blob(ellipse_pts(x + 20, y + 8, 340, 16, 20), "#2a1408", .3)]
    o.append(shape(rect_pts(x - 330, y - 150, x + 330, y - 50), "#e8d9b8", blob(rect_pts(x - 330, y - 80, x + 330, y - 50), "#cdbb94", .8), w=5, seed=9700))
    o.append(shape(rect_pts(x - 340, y - 56, x + 340, y), "#a8693f", blob(rect_pts(x - 340, y - 14, x + 340, y), "#7f4b2b", .8), w=5, seed=9701))
    o.append(shape(rect_pts(x - 320, y - 50, x - 290, y + 20, 4), "#8a5a38", "", w=4, seed=9702))
    o.append(shape(rect_pts(x + 290, y - 50, x + 320, y + 20, 4), "#8a5a38", "", w=4, seed=9703))
    o.append(shape(rect_pts(x - 320, y - 190, x - 150, y - 140, 20), "#fffdf6", blob(rect_pts(x - 320, y - 160, x - 150, y - 140, 8), "#e1dcea", .8), w=4.4, seed=9704))
    o.append(shape(rect_pts(x - 120, y - 170, x + 330, y - 100, 8), "#6d96c8", blob(rect_pts(x - 120, y - 120, x + 330, y - 100), "#4f78a8", .8) +
                   "".join(line([(x - 60 + j * 90, y - 168), (x - 60 + j * 90, y - 102)], 3, "#8fb2dc", taper=.1, wmin=.8, seed=9710 + j, op=.8) for j in range(5)), w=4.6, seed=9705))
    return "".join(o)


def frame13(t):
    T0 = 22.72
    u = clamp((t - T0) / 2.2)
    x = 790
    nod_t = T_DIMA
    nod = math.exp(-(t - nod_t) * 5) * math.sin((t - nod_t) * 2 * math.pi * 3.0) if t >= nod_t else 0.0
    ha = .03 * math.sin(t * 1.4) + .14 * nod
    lean = .04 + .04 * nod
    # чашка в ближней руке на уровне груди; подносит ко рту на паре моментов
    sip = smooth(23.3, 23.6, t) * (1 - smooth(23.8, 23.95, t))
    hand_n = (x + 110 - 10 * sip, 965 - 100 * sip)
    f_t = (x - 20, 960)
    expr = dict(lid=.78, look=(.7, -.3), brows="calm", mouth="smile", smile=.5 + .4 * smooth(nod_t - .1, nod_t + .2, t), flush=0.0, blush=.3, closed=.0)
    d = stand(t, x, lean=lean, ha=ha, expr=expr, n_t=hand_n, f_t=f_t, hands={"n": hand_spec(.7, (.2, -1)), "f": hand_spec(.35)}, bob=3 * math.sin(t * 1.6), sx=-1)
    wr = wrist_w(d, "n", x)
    held = cup(wr[0] + 6, wr[1] + 34, 1.0, t, 0)
    # календарь на стене слева от окна, самолётик, красный овал рисуется на «Дима»/после
    markp = smooth(T0 + .5, T0 + 1.0, t)
    cal = calendar(440, 740, .95, t, mark_u=clamp(markp))
    clk = clock(445, 430, 56, t, jump=0.0)
    # чемодан раскрытый пустой на кровати справа
    bd = bed(1200, 1440)
    sc = suitcase(1260, 1262, .66, lid=.9, fill=0.0, t=t)
    cam = (740 + 40 * u, 1180, 1.12 + .08 * ease_io(u), -.9 * (1 - u))
    D.set_ink(cam[2])
    if "tidy" not in _ST:
        _ST["tidy"] = room56("tidy")
    lg, af, bdy, an = dima_layers(d)
    parts = [_ST["tidy"], clk, cal, bd, sc, lg, af, bdy, held, an, sun_motes(t)]
    out = f'<g transform="{lib.cam(*cam)}">{"".join(parts)}</g>'
    return whip(out, t, T0)


# ═════════════════════════ вход ═════════════════════════
def frame(sid, t):
    if not _ST.get("init"):
        D.DAY[0] = True
        _ST["mess"] = room56("mess")
        _ST["tidy"] = room56("tidy")
        lib.static_done()
        _ST["init"] = True
    lib.dyn_begin()
    body = {"s01": frame01, "s02": frame02, "s04": frame04, "s06": frame06, "s13": frame13}[sid](t)
    return svg(f'<rect width="1920" height="1920" fill="#2a1f2a"/>{body}')
