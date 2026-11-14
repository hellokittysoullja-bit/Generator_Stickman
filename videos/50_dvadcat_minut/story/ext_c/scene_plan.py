"""Сцена plan рилса 50: мысль Димы облаком, карта-план с зелёной дорожкой до флажка.
s08 (12.0–15.4): облако мысли, дорожка до флажка «20 мин» ровная, Дима (маленький, горчичное худи) идёт довольный; на «гладко»
(14.72) дорожка выравнивается и по ней проходит блик.
s09 (15.4–17.96): на «забываем» (15.52) на дорожке вырастают помехи: уведомление, кружка кофе, звонок, кот, «ещё одна вкладка»;
Дима спотыкается об уведомление, к «мешает» (17.17) дорожка раскручивается в длинную кривую змейку; отъезд камеры.
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat  # noqa: E402
import dima  # noqa: E402
import lib  # noqa: E402
from common import shake, speed_streaks, text, whip_in  # noqa: E402
from lib import (INK, blob, blur, clamp, cam, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts,
                 shape, smooth, spring, svg, T)
from scipy.interpolate import PchipInterpolator  # noqa: E402

dima.BS = 0.2
dima.LWK = 2.3
BS = dima.BS
LEG = (dima.THIGH + dima.SHIN) * BS
AHW = dima.AH * BS
TOEW = dima.TOE * BS * 1.22

_ST = {}
T_GLADKO = 14.72
T_FORGET = 15.52
T_MESH = 17.173
CLOUD = (540, 700, 510, 440)          # центр, полуоси
Y0 = 830.0                            # линия дорожки
X_START = 90.0
SPLIT_X = 640.0
FLAG0 = (950.0, Y0)
RIB_W = 62.0

# ───────────────────────── геометрия дорожки: прямая → змейка
WAY = [(SPLIT_X, Y0), (900, Y0), (900, 690), (300, 690), (300, 550), (900, 550), (900, 410), (470, 410)]


def fillet(way, r):
    out = [np.array(way[0], float)]
    for i in range(1, len(way) - 1):
        p0, p1, p2 = (np.array(way[j], float) for j in (i - 1, i, i + 1))
        a, b = p0 - p1, p2 - p1
        la, lb = np.linalg.norm(a), np.linalg.norm(b)
        a, b = a / la, b / lb
        rr = min(r, la * .45, lb * .45)
        s, e = p1 + a * rr, p1 + b * rr
        out.append(s)
        n = 10
        for k in range(1, n):
            u = k / n
            q = (1 - u) ** 2 * s + 2 * (1 - u) * u * p1 + u * u * e
            out.append(q)
        out.append(e)
    out.append(np.array(way[-1], float))
    return np.array(out)


def resample(P, n):
    d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    u = np.linspace(0, d[-1], n)
    return np.stack([np.interp(u, d, P[:, 0]), np.interp(u, d, P[:, 1])], 1), d[-1]


NT = 260
TAIL1, LEN1 = resample(fillet(WAY, 66), NT)
TAIL0 = np.stack([np.linspace(SPLIT_X, FLAG0[0], NT), np.full(NT, Y0)], 1)
HEAD = np.stack([np.linspace(X_START, SPLIT_X, 60, endpoint=False), np.full(60, Y0)], 1)


def morph_k(t):
    return ease_io(clamp((t - 16.15) / 1.1))


def wobble(x, t):
    """Неровность дорожки до «гладко»: медленная волна, на блике сглаживается слева направо."""
    sw = clamp((t - T_GLADKO) / 0.55)
    # фронт гладкости идёт слева направо
    front = X_START - 50 + sw * 1250
    k = smooth(front - 140, front + 40, x) if sw > 0 else 0.0
    a = 7.0 * (1 - k)
    return a * (math.sin(x / 62.0 + 0.4) + 0.45 * math.sin(x / 23.0 + 1.3))


def path_pts(t):
    k = morph_k(t)
    tail = TAIL0 + (TAIL1 - TAIL0) * k
    P = np.vstack([HEAD, tail])
    if k < 1:
        wb = np.array([wobble(x, t) for x in P[:, 0]]) * (1 - k)
        P = P.copy()
        P[:, 1] += wb
    return P


def tail_pt(fr, t):
    """Точка на хвосте дорожки по доле fr (0..1) и направление."""
    P = path_pts(t)[len(HEAD):]
    i = fr * (len(P) - 1)
    a = int(min(len(P) - 2, i))
    u = i - a
    p = P[a] * (1 - u) + P[a + 1] * u
    d = P[min(len(P) - 1, a + 2)] - P[max(0, a - 1)]
    return p, d / (np.linalg.norm(d) + 1e-9)


# ───────────────────────── облако и карта (статика)
def cloud_pts():
    cx, cy, rx, ry = CLOUD
    out = []
    n = 9
    for i in range(n):
        for k in range(8):
            a = 2 * math.pi * (i + k / 8) / n
            u = k / 8
            bump = math.sin(math.pi * u) ** 0.7
            r = 1 + 0.085 * bump
            q = (cx + rx * math.cos(a - math.pi / 2) * r, cy + ry * math.sin(a - math.pi / 2) * r)
            out.append(q + ((1,) if k == 0 else ()))
    return out


def background():
    s = []
    g = lin_grad([(0, "#9fd0e6", 1), (1, "#6fa4c6", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g})"/>')
    for k in range(14):
        x = -700 + k * 190
        s.append(blob(ellipse_pts(x, 140 + (k % 3) * 360, 90, 16, 12), "#ffffff", .14))
    for k in range(60):
        x = (k * 137) % 1000 + 30
        y = (k * 263) % 1900
        s.append(f'<circle cx="{x}" cy="{y}" r="{3 + k % 4}" fill="#ffffff" opacity=".12"/>')
    return "".join(s)


def cloud_static():
    cp = cloud_pts()
    s = []
    s.append(blob(T(cp, 14, 24), "#2c5775", .35, blur(10)))
    inner = blob(T(cp, 0, 0, 0.93, 0, 540, 700), "#ffffff", .0)
    s.append(shape(cp, "#fffaf0", "", w=7.5, seed=611, ink=False))
    # карта-бумага внутри
    mp = [(p[0], p[1]) + p[2:] for p in T(cp, 0, 0, 0.9, 0, 540, 700)]
    cid = lib.clip_of(mp)
    m = []
    g = lin_grad([(0, "#fff6dc", 1), (1, "#f3e6c2", 1)], 0, 0, 0, 1)
    m.append(f'<rect x="0" y="240" width="1080" height="940" fill="url(#{g})"/>')
    for x in range(60, 1060, 80):
        m.append(f'<path d="M{x} 250V1160" stroke="#e7d6ac" stroke-width="2" opacity=".6"/>')
    for y in range(280, 1160, 80):
        m.append(f'<path d="M40 {y}H1040" stroke="#e7d6ac" stroke-width="2" opacity=".6"/>')
    # деревья и кусты на карте
    for i, (x, y, sc) in enumerate([(150, 640, 1), (230, 960, .9), (420, 980, 1.1), (560, 1010, .8), (800, 990, 1), (990, 960, .9),
                                    (130, 460, .8), (990, 640, 1), (210, 380, .9), (860, 340, .8), (560, 520, .8), (140, 1050, .8)]):
        m.append(tree(x, y, sc, 640 + i))
    s.append(f'<g clip-path="url(#{cid})">{"".join(m)}</g>')
    s.append(f'<path d="{lib.ink_closed(mp, 6.5, seed=612)}" fill="{INK}"/>')
    s.append(shape(cp, "none", "", w=7.5, seed=611, ink=True, attrs='fill-opacity="0"'))
    # хвост мысли (кружки)
    for (x, y, r, sd) in [(340, 1190, 40, 620), (270, 1262, 27, 621), (226, 1318, 16, 622)]:
        s.append(shape(ellipse_pts(x, y, r, r, 16), "#fffaf0", "", w=5.4, seed=sd))
    return "".join(s)


def tree(x, y, sc, sd):
    o = []
    o.append(blob(ellipse_pts(x + 10 * sc, y + 4 * sc, 44 * sc, 10 * sc, 12), "#9a7a3a", .22))
    o.append(shape(rect_pts(x - 7 * sc, y - 36 * sc, x + 7 * sc, y + 2 * sc, 3), "#9a6a3a", "", w=3.4, seed=sd))
    o.append(shape(ellipse_pts(x, y - 66 * sc, 36 * sc, 40 * sc, 14), "#8cc56a",
                   blob(ellipse_pts(x + 10 * sc, y - 56 * sc, 26 * sc, 28 * sc, 12), "#6fae52", .9) +
                   blob(ellipse_pts(x - 12 * sc, y - 80 * sc, 10 * sc, 12 * sc, 8), "#b4e08c", .9), w=4, seed=sd + 1))
    return "".join(o)


# ───────────────────────── дорожка
def ribbon(P, t):
    n = len(P)
    # сгладить по длине, нормали
    T_ = np.gradient(P, axis=0)
    T_ /= np.linalg.norm(T_, axis=1, keepdims=True) + 1e-9
    N = np.stack([-T_[:, 1], T_[:, 0]], 1)
    w = RIB_W / 2
    L, R = P + N * w, P - N * w
    # скруглённые концы
    def cap(c, tn, nn, sgn):
        return [tuple(c + nn * w * math.cos(a) * sgn + tn * w * math.sin(a) * sgn) for a in np.linspace(0, math.pi, 8)[1:-1]]
    st = max(1, n // 120)
    Ls = [tuple(p) for p in L[::st]] + [tuple(L[-1])]
    Rs = [tuple(p) for p in R[::st]] + [tuple(R[-1])]
    end = cap(P[-1], T_[-1], N[-1], 1)
    beg = cap(P[0], T_[0], N[0], -1)
    poly = Ls + end + Rs[::-1] + beg
    # нижняя «толщина» дорожки
    low = [(p[0], p[1] + 9) for p in poly]
    s = []
    s.append(blob(low, "#3f8a45"))
    s.append(blob([(p[0] + 2, p[1] + 18) for p in poly], "#3a5a3a", .22, blur(4)))
    s.append(shape(poly, "#7fd06f", blob([(p[0], p[1] + 12) for p in Ls + end + Rs[::-1] + beg][:0] or poly, "#7fd06f"), w=5.0, seed=640))
    # светлая кромка сверху и тёмная снизу: две тонкие дорожки по краям
    s.append(line([tuple(p) for p in L[::st * 2]], 7, "#a8e68f", taper=.0, wmin=1, seed=641, op=.7))
    s.append(line([tuple(p) for p in R[::st * 2]], 6, "#52a85a", taper=.0, wmin=1, seed=642, op=.8))
    # пунктир
    d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    per, dash = 46.0, 24.0
    k = 0
    pos = 14.0
    while pos + dash < d[-1] - 10:
        a = int(np.searchsorted(d, pos))
        b = int(np.searchsorted(d, pos + dash))
        seg = [tuple(P[j]) for j in range(a, min(b + 1, n))]
        if len(seg) >= 2:
            s.append(line(seg, 6.5, "#fffbe6", taper=.1, wmin=.7, seed=650 + k, op=.95))
        pos += per
        k += 1
    return "".join(s)


def shine(P, t):
    """Блик на «гладко»: светлая полоса бежит по дорожке слева направо, за ней — искры."""
    u = clamp((t - T_GLADKO) / 0.6)
    if not (0 < u < 1):
        return ""
    x = X_START - 40 + u * 1000
    s = []
    for j in range(3):
        xx = x - j * 36
        h = 62 - j * 14
        s.append(f'<path d="M{f(xx)} {Y0 - h / 2}L{f(xx + 30)} {Y0 - h / 2}L{f(xx + 12)} {Y0 + h / 2}L{f(xx - 18)} {Y0 + h / 2}Z" '
                 f'fill="#ffffff" opacity="{.75 - j * .2:.2f}"/>')
    for j in range(5):
        a = u * 6 + j * 1.3
        px = x - 30 - j * 46
        py = Y0 - 50 - 18 * math.sin(a * 2.0) - (j % 2) * 20
        sz = 10 + 6 * math.sin(a * 3 + j)
        if px > X_START - 30:
            s.append(sparkle(px, py, sz, "#ffffff", .9 * (1 - j / 6)))
    return "".join(s)


def sparkle(x, y, r, col, op=1.0):
    d = f"M{f(x)} {f(y - r)}L{f(x + r * .26)} {f(y - r * .26)}L{f(x + r)} {f(y)}L{f(x + r * .26)} {f(y + r * .26)}L{f(x)} {f(y + r)}" \
        f"L{f(x - r * .26)} {f(y + r * .26)}L{f(x - r)} {f(y)}L{f(x - r * .26)} {f(y - r * .26)}Z"
    return f'<path d="{d}" fill="{col}" opacity="{op:.2f}"/>'


# ───────────────────────── флажок и «20 мин»
def flag(x, y, t, sc=1.0):
    wv = math.sin(t * 5.2) * 6
    wv2 = math.sin(t * 5.2 + 1.2) * 6
    s = []
    s.append(blob(ellipse_pts(x + 6, y + 6, 40 * sc, 10 * sc, 12), "#3a5a3a", .3))
    s.append(shape(ellipse_pts(x, y - 4, 26 * sc, 12 * sc, 12), "#9a6a3a", blob(ellipse_pts(x + 8 * sc, y, 14 * sc, 6 * sc, 8), "#7a4f27", .8), w=3.6, seed=660))
    s.append(shape(rect_pts(x - 4 * sc, y - 150 * sc, x + 4 * sc, y - 6 * sc, 3), "#e8dcc0", blob(rect_pts(x + 1 * sc, y - 150 * sc, x + 4 * sc, y - 6 * sc), "#b8a888"), w=3.4, seed=661))
    fl = [(x + 4 * sc, y - 148 * sc), (x + 40 * sc, y - 142 * sc + wv * sc), (x + 78 * sc, y - 130 * sc + wv2 * sc),
          (x + 62 * sc, y - 108 * sc + wv * sc * .6), (x + 78 * sc, y - 86 * sc + wv2 * sc), (x + 40 * sc, y - 92 * sc + wv * sc),
          (x + 4 * sc, y - 82 * sc)]
    s.append(shape(fl, "#ee4b3c", blob([(x + 4 * sc, y - 100 * sc), (x + 78 * sc, y - 100 * sc), (x + 78 * sc, y - 82 * sc), (x + 4 * sc, y - 82 * sc)], "#c43328", .85), w=3.8, seed=662))
    s.append(f'<circle cx="{f(x)}" cy="{f(y - 152 * sc)}" r="{f(7 * sc)}" fill="#f7c53a" stroke="{INK}" stroke-width="2.4"/>')
    return "".join(s)


def plate(x, y, t, sc=1.0, label="20 мин", hit=0.0):
    w, h = 190 * sc, 84 * sc
    s = []
    s.append(blob(rect_pts(x - w / 2 + 6, y - h / 2 + 10, x + w / 2 + 6, y + h / 2 + 10, 20 * sc), "#3a5a3a", .28, blur(5)))
    s.append(shape(rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 20 * sc), "#ffffff",
                   blob(rect_pts(x - w / 2, y + h * .12, x + w / 2, y + h / 2, 20 * sc), "#e3e8ef", .9), w=5, seed=670))
    s.append(text(x, y + 16 * sc, label, 44 * sc, "#2a3550"))
    return "".join(s)


# ───────────────────────── помехи
def notif(x, y, sc, t, tpop):
    e = t - tpop
    k = spring(e, 2.6, 6.5) if e > 0 else 0.0
    if k <= 0.001:
        return ""
    sy = max(0.01, k)
    w, h = 108, 62
    s = []
    s.append(blob(ellipse_pts(x + 4, y + 4, 46, 9, 12), "#3a5a3a", .3))
    cy = y - 26
    body = []
    body.append(blob(rect_pts(-w / 2 + 5, -h / 2 + 7, w / 2 + 5, h / 2 + 7, 14), "#2b3a30", .25, blur(3)))
    body.append(shape(rect_pts(-w / 2, -h / 2, w / 2, h / 2, 14), "#ffffff", blob(rect_pts(-w / 2, h * .1, w / 2, h / 2, 14), "#dfe6f0", .9), w=4.4, seed=680))
    body.append(shape(rect_pts(-w / 2 + 10, -h / 2 + 10, -w / 2 + 40, -h / 2 + 40, 8), "#4a90e2", "", w=3, seed=681))
    body.append(line([(-w / 2 + 50, -h / 2 + 14), (w / 2 - 12, -h / 2 + 14)], 5, "#8c97aa", seed=682))
    body.append(line([(-w / 2 + 50, -h / 2 + 30), (w / 2 - 26, -h / 2 + 30)], 5, "#c1c9d6", seed=683))
    bc = (w / 2 - 2, -h / 2 + 2)
    body.append(shape(ellipse_pts(bc[0], bc[1], 17, 17, 12), "#ee4033", "", w=3.4, seed=684))
    body.append(text(bc[0], bc[1] + 9, "1", 24, "#ffffff"))
    s.append(f'<g transform="translate({f(x)} {f(cy)}) scale({sy:.3f}) rotate({-5 * (1 - min(1, e * 3)):.2f})">{"".join(body)}</g>')
    return "".join(s)


def mug(x, y, sc, t, tpop):
    e = t - tpop
    k = spring(e, 2.4, 6.5) if e > 0 else 0.0
    if k <= 0.001:
        return ""
    s = []
    s.append(blob(ellipse_pts(x + 4, y + 4, 38, 8, 12), "#3a5a3a", .3))
    b = []
    cup = [(-30, -64, 1), (30, -64, 1), (28, -20), (22, -2), (0, 4), (-22, -2), (-28, -20)]
    b.append(shape(cup, "#f2f0ea", blob([(6, -64), (30, -64), (28, -20), (22, -2), (6, 2)], "#d2cfc6", .9), w=4.4, seed=690))
    b.append(shape(ellipse_pts(0, -64, 30, 8, 12), "#6b3d22", blob(ellipse_pts(-8, -64, 14, 4, 8), "#8a5530", .9), w=3.2, seed=691))
    hd = [(28, -52, 1), (46, -52), (52, -36), (44, -20), (26, -18, 1), (28, -26), (40, -30), (38, -40), (28, -42)]
    b.append(shape(hd, "#f2f0ea", "", w=3.8, seed=692))
    b.append(f'<path d="M-14 -34h18v16h-18z" fill="#e8453c" opacity="0"/>')
    b.append(shape(ellipse_pts(-4, -34, 11, 11, 10), "#e8453c", "", w=2.8, seed=693))
    b.append(shape(ellipse_pts(-4, -34, 4, 4, 8), "#f2f0ea", "", w=0.0, seed=694, ink=False))
    # пар
    for j in range(3):
        ph = t * 2.6 + j * 2.1
        xs = -14 + j * 14
        pts = [(xs + 3 * math.sin(ph), -70), (xs - 6 * math.sin(ph + 1), -92), (xs + 7 * math.sin(ph + 2), -112), (xs - 3 * math.sin(ph), -132)]
        b.append(line(pts, 5, "#ffffff", taper=.5, wmin=.1, seed=695 + j, op=.85))
    sc2 = 0.9
    s.append(f'<g transform="translate({f(x)} {f(y)}) scale({sc2 * k:.3f}) ">{"".join(b)}</g>')
    return "".join(s)


def phone(x, y, sc, t, tpop):
    e = t - tpop
    k = spring(e, 2.4, 6.5) if e > 0 else 0.0
    if k <= 0.001:
        return ""
    vib = math.sin(t * 60) * 3.0 if e > 0.1 else 0
    rot = math.sin(t * 52) * 4.0 if e > 0.1 else 0
    s = []
    s.append(blob(ellipse_pts(x + 4, y + 4, 34, 8, 12), "#3a5a3a", .3))
    b = []
    b.append(shape(rect_pts(-34, -118, 34, 0, 12), "#2a2f3c", blob(rect_pts(8, -118, 34, 0, 12), "#171a22", .9), w=4.4, seed=700))
    b.append(shape(rect_pts(-28, -108, 28, -12, 6), "#4ccb6e", blob(rect_pts(-28, -50, 28, -12, 6), "#36a857", .8), w=2.4, seed=701))
    b.append(shape(ellipse_pts(0, -84, 14, 14, 12), "#ffffff", "", w=2.0, seed=702, ink=False))
    # трубка-иконка
    hp = [(-8, -91), (-3, -92), (-1, -86), (-5, -83), (-1, -77), (4, -78), (7, -74), (3, -66), (-6, -70), (-11, -82)]
    b.append(shape(hp, "#4ccb6e", "", w=2, seed=703, ink=False))
    b.append(line([(-14, -42), (14, -42)], 5, "#ffffff", seed=704, op=.9))
    s.append(f'<g transform="translate({f(x + vib)} {f(y)}) rotate({rot:.2f}) scale({k:.3f})">{"".join(b)}</g>')
    # дуги звонка
    if e > 0.1:
        for j in range(2):
            ph = (t * 3.2 + j * .5) % 1.0
            for sg in (-1, 1):
                r = 52 + 30 * ph + j * 18
                a = math.radians(40)
                pts = [(x + sg * r * math.cos(-a + q * a * 2 / 4) * 1.0, y - 66 + r * math.sin(-a + q * a * 2 / 4) * 0.9) for q in range(5)]
                s.append(line(pts, 6 * (1 - ph) + 2, "#2a2f3c", taper=.4, wmin=.2, seed=705 + j, op=1 - ph))
    return "".join(s)


def tabwin(x, y, sc, t, tpop):
    e = t - tpop
    k = spring(e, 2.4, 6.5) if e > 0 else 0.0
    if k <= 0.001:
        return ""
    b = []
    b.append(blob(rect_pts(-72, -104, 74, 8, 12), "#2b3a30", .25, blur(3)))
    b.append(shape(rect_pts(-70, -112, 70, 0, 10), "#ffffff", blob(rect_pts(-70, -30, 70, 0, 10), "#e3e8ef", .9), w=4.4, seed=710))
    b.append(shape(rect_pts(-70, -112, 70, -84, 10), "#cfd7e6", "", w=4.0, seed=711))
    for j, col in enumerate(("#e8453c", "#f7c53a", "#4ccb6e")):
        b.append(shape(ellipse_pts(-54 + j * 16, -98, 5, 5, 8), col, "", w=1.6, seed=712 + j, ink=False))
    b.append(shape(rect_pts(-12, -118, 54, -90, 8), "#ffffff", "", w=3.4, seed=715))
    b.append(shape(rect_pts(58, -114, 74, -92, 5), "#e3e8ef", "", w=3.0, seed=716))
    b.append(text(66, -97, "+", 20, "#2a3550"))
    b.append(line([(-56, -64), (36, -64)], 7, "#9aa6ba", seed=717))
    b.append(line([(-56, -44), (6, -44)], 7, "#c1c9d6", seed=718))
    b.append(line([(-56, -24), (48, -24)], 7, "#c1c9d6", seed=719))
    s = [blob(ellipse_pts(x + 4, y + 4, 56, 9, 12), "#3a5a3a", .3)]
    s.append(f'<g transform="translate({f(x)} {f(y - 6)}) rotate({-4 * (1 - min(1, e * 3)):.2f}) scale({k:.3f})">{"".join(b)}</g>')
    return "".join(s)


def popdust(x, y, e):
    if not (0 < e < 0.5):
        return ""
    s = []
    u = e / 0.5
    for j in range(5):
        a = math.radians(200 + j * 35)
        r = 18 + 36 * ease_out(u, 2)
        s.append(f'<circle cx="{f(x + math.cos(a) * r)}" cy="{f(y - 6 + math.sin(a) * r * .5)}" r="{f(8 * (1 - u) + 1)}" fill="#fffaf0" opacity="{.8 * (1 - u):.2f}"/>')
    return "".join(s)


# ───────────────────────── Дима: походка, спотыкание, оправление
X0W = 172.0
STEP = 64.0
TC = 0.55
ST = 0.62
T0 = 12.0
K_TRIP = 7
T_JAM = T0 + K_TRIP * TC            # 15.85
OBST_X = 677.0                       # уведомление до пинка
T_CATCH = T_JAM + 0.5


def ground(x, t):
    return Y0 + wobble(x, t) * (1 - morph_k(t))


def contacts():
    C = []
    for k in range(-6, K_TRIP + 1):
        C.append([T0 + k * TC, "n" if k % 2 == 0 else "f", X0W + k * STEP, T0 + k * TC + ST])
    return C


C = contacts()
HIP_KEYS = [(c[0] + ST / 2, c[2] + 4) for c in C]
HIPX = PchipInterpolator(np.array([a for a, _ in HIP_KEYS]), np.array([b for _, b in HIP_KEYS]))


def hip_base(t):
    x = float(HIPX(min(t, HIP_KEYS[-1][0])))
    y = Y0 - (LEG * 0.86 + AHW)
    best = 9.0
    for c in C:
        dt = t - (c[0] + ST / 2)
        if abs(dt) < abs(best):
            best = dt
    y += 3.5 * math.cos(2 * math.pi * best / TC)
    return x, y


def planted(x, gy, hip):
    A = np.array([x, gy - AHW])
    reach = LEG * 0.985
    if np.linalg.norm(A - hip) <= reach:
        return A, 0.0
    toe = np.array([x + TOEW, gy])
    lo, hi = 0.0, 1.35
    for _ in range(30):
        m = (lo + hi) / 2
        A2 = toe + dima.rot(np.array([-TOEW, -AHW]), m)
        if np.linalg.norm(A2 - hip) > reach:
            lo = m
        else:
            hi = m
    return toe + dima.rot(np.array([-TOEW, -AHW]), hi), hi


def swing(A0, ph0, A1, u, lift=24.0):
    ux = (1 - math.cos(math.pi * u ** 1.2)) / 2
    x = A0[0] + (A1[0] - A0[0]) * ux - 10 * math.sin(math.pi * clamp(u * 1.5))
    y = A0[1] + (A1[1] - A0[1]) * u - lift * math.sin(math.pi * clamp(u * 1.05)) ** 1.2
    if u < .3:
        phi = ph0 + (0.45 - ph0) * smooth(0, .3, u)
    elif u < .85:
        phi = 0.45 + (-0.2 - 0.45) * smooth(.3, .85, u)
    else:
        phi = -0.2 * (1 - smooth(.85, 1.0, u))
    return np.array([x, y]), phi


# время после T_JAM: x цели «шаг-ловля» и покой
X_J = X0W + K_TRIP * STEP            # 620: застрявший носок
X_CATCH = 742.0
X_REST_N = 700.0


def walk_state(t):
    """Возвращает hip, feet {n,f}: (A, phi), lean, kind."""
    hx, hy = hip_base(t)
    hip = np.array([hx, hy])
    feet = {}
    lean = 0.14
    if t < T_JAM + 0.0:
        for side in ("n", "f"):
            cs = [c for c in C if c[1] == side and c[0] <= t + 3]
            prev = None
            nxt = None
            for c in C:
                if c[1] != side:
                    continue
                if c[0] <= t:
                    prev = c
                elif nxt is None:
                    nxt = c
            hipt = hip
            gy = lambda x: ground(x, t)
            if prev is not None and (t <= prev[3] or nxt is None):
                feet[side] = planted(prev[2], gy(prev[2]), hipt)
            else:
                prev = prev or [t - 1, side, nxt[2] - 2 * STEP, t - 0.4]
                A0, ph0 = planted(prev[2], gy(prev[2]), np.array([hx - 40, hy]))
                tgt = nxt[2]
                if nxt[0] == T_JAM:
                    tgt = X_J
                A1 = np.array([tgt, gy(tgt) - AHW])
                u = clamp((t - prev[3]) / (nxt[0] - prev[3]))
                feet[side], ph = swing(A0, ph0, A1, u)
                feet[side] = (feet[side], ph)
        return hip, feet, lean, "walk"
    return None


def stumble(t):
    """t >= T_JAM. Нога f (k=7, чётная? k=7 → 'f') застряла у уведомления; другая выбрасывается вперёд."""
    e = t - T_JAM
    gy = lambda x: ground(x, t)
    # положение таза: по инерции вперёд и вниз, потом выпрямление
    hx0, hy0 = hip_base(T_JAM)
    fall = ease_out(clamp(e / 0.42), 2.0)
    rec = ease_io(clamp((e - 0.55) / 0.75))
    hx = hx0 + 62 * fall + 26 * rec
    hy = hy0 + 30 * fall * (1 - rec) + 2 * math.sin(e * 6)
    hip = np.array([hx, hy])
    lean = 0.14 + (0.78 - 0.14) * fall * (1 - rec) - 0.06 * rec
    # застрявшая нога 'f' (k=7): стоит у препятствия, носок вверх; освобождается на 0.9 с и ставится рядом с «ловящей»
    xj = X_J
    free = ease_io(clamp((e - 0.95) / 0.5))
    fj_pos = np.array([xj + (X_REST_N - 38 - xj) * free, gy(xj) - AHW - 0.0])
    fj, phj = planted(xj, gy(xj), hip)
    if free > 0:
        a1 = np.array([X_REST_N - 38, gy(X_REST_N - 38) - AHW])
        pos, ph = swing(fj, phj, a1, free, 28)
        fj, phj = pos, ph
    else:
        phj = -0.35 * (1 - smooth(0.45, 0.6, e))
        fj = np.array([fj[0], fj[1] - 3 * math.sin(e * 20) * math.exp(-e * 6)])
    # ловящая нога 'n' (k=6 стояла на X0W+6*STEP=556 до T0+6TC+ST)
    xn = X0W + 6 * STEP
    t_lift = T0 + 6 * TC + ST - T_JAM          # 0.07
    u = clamp((e - t_lift) / (0.52 - t_lift))
    nA0, nph0 = planted(xn, gy(xn), np.array(hip_base(T0 + 6 * TC + ST)))
    nA1 = np.array([X_REST_N, gy(X_REST_N) - AHW])
    if e < t_lift:
        nA, nph = nA0, nph0
    elif u < 1:
        nA, nph = swing(nA0, nph0, nA1, u, 38)
    else:
        nA, nph = planted(X_REST_N, gy(X_REST_N), hip)
    feet = {"f": (fj, phj), "n": (nA, nph)}
    return hip, feet, lean, e


def dima_pose(t):
    if t < T_JAM:
        hip, feet, lean, _ = walk_state(t)
        e = 0.0
    else:
        hip, feet, lean, e = stumble(t)
    # руки
    cn = [c[0] for c in C if c[1] == "n"]
    tn = max([c for c in cn if c <= min(t, T_JAM)], default=cn[0])
    psi = 2 * math.pi * (min(t, T_JAM) - tn) / (2 * TC)
    arms = {}
    for s_, sg in (("n", 1), ("f", -1)):
        sw = -sg * math.cos(psi)
        arms[s_] = ("ang", 0.05 + 0.55 * sw, 0.35 + 0.2 * max(0, sw))
    hands = {"n": "fist", "f": "fist"}
    head_ang = -0.03
    expr = dict(lid=0.8, look=(0.45, 0.05), brows="up", mouth="grin", hair=0.0)
    if t >= T_JAM:
        fl = smooth(0.0, 0.16, e) * (1 - smooth(0.55, 1.0, e))
        wave = math.sin(e * 22)
        arms["n"] = ("ang", 0.2 + (2.5 + 0.35 * wave) * fl + 0.1 * (1 - fl), 0.5 - 0.3 * fl)
        arms["f"] = ("ang", 0.1 + (2.0 - 0.3 * wave) * fl, 0.6 - 0.35 * fl)
        up = smooth(0.0, 0.1, e)
        expr = dict(lid=1.0, look=(0.5, 0.55), brows="worry", mouth="gape", hair=-14 * math.exp(-e * 4) * math.sin(e * 20))
        head_ang = 0.12 * fl
        if e > 1.0:
            # выпрямился: вздох, взгляд вдаль на дорожку, рука к затылку
            k = smooth(1.0, 1.45, e)
            expr = dict(lid=0.5, look=(0.7, -0.1), brows="worry", mouth="flat", hair=0.0)
            sp_ = hip + np.array([0, 0])
            tx, ty = hip[0] - 10, hip[1] - (400 + 140) * BS - 28
            arms["n"] = ("ik", (tx + 40, ty + 20 * math.sin(e * 5)), -1) if False else ("ang", 0.2 + (2.9 - 0.2) * k, 0.6 + 1.3 * k)
            head_ang = -0.05 * k
    return dict(hip=hip, lean=lean, feet=feet, arms=arms, hands=hands, head_ang=head_ang, expr=expr,
                hood=0.0, strings=(-14 + 6 * math.sin(t * 5), 6))


# ───────────────────────── кадр
def static():
    if not _ST:
        _ST["bg"] = background()
        _ST["cloud"] = cloud_static()
        cat.static_parts()
        lib.static_done()


POP = {"notif": 15.62, "mug": 15.95, "phone": 16.3, "cat": 16.65, "tab": 16.98}
FR = {"notif": 0.12, "mug": 0.38, "phone": 0.50, "cat": 0.62, "tab": 0.78}


def kicked_notif(t):
    """Уведомление: стоит на дорожке, Дима пинает его носком в T_JAM (оно летит вперёд и встаёт дальше)."""
    p0, _ = tail_pt(FR["notif"], t)
    e = t - (T_JAM + 0.04)
    if e <= 0:
        return p0[0], p0[1], 0.0, 0.0
    # новая точка покоя: доля 0.30
    p1, _ = tail_pt(0.25, t)
    u = clamp(e / 0.55)
    x = p0[0] + (p1[0] - p0[0]) * u
    arc = -90 * 4 * u * (1 - u)
    return x, p0[1] + (p1[1] - p0[1]) * u + arc, 560 * min(1, u), e


def frame(sid, t):
    static()
    lib.dyn_begin()
    dx, wrot, wu = (0.0, 0.0, 1.0)
    if sid == "s08":
        dx, wrot, wu = whip_in(t, 12.0, 0.2, 700, 6)
    P = path_pts(t)
    k = morph_k(t)
    s = [_ST["bg"]]
    w = []
    # облако дышит
    br = 1 + 0.006 * math.sin(t * 2.0)
    w.append(f'<g transform="translate(540 700) scale({br:.4f}) translate(-540 -700)">{_ST["cloud"]}</g>')
    # заголовок
    th = 1 - smooth(16.15, 16.6, t)
    if th > 0:
        w.append(text(540, 392, "ИДЕАЛЬНЫЙ ПЛАН", 46, "#5a6b86", op=th))
    w.append(ribbon(P, t))
    w.append(shine(P, t))
    # старт
    w.append(shape(ellipse_pts(X_START + 18, Y0, 20, 20, 12), "#ffffff", "", w=4.4, seed=720))
    w.append(f'<circle cx="{f(X_START + 18)}" cy="{f(Y0)}" r="8" fill="#4a90e2"/>')
    # флажок и плашка едут по хвосту
    fp = P[-1]
    fsc = 1.0 - 0.28 * k
    w.append(flag(fp[0], fp[1] + 8, t, fsc))
    pl = (fp[0] - (46 if k < 0.5 else -60) * (1 - k) - 70 * k, fp[1] - 190 * fsc)
    w.append(plate(fp[0] - 110 * (1 - k) - 90 * k, fp[1] - 215 * fsc - 10 * (1 - k), t, 0.9 - 0.2 * k))
    # путевые точки: маленькие кружки на хвосте
    # помехи, отсортированные по y (дальние раньше)
    obs = []
    nx, ny, nz, ne = kicked_notif(t)
    obs.append((ny, notif(nx, ny, 1, t, POP["notif"]) + (popdust(nx, ny, t - POP["notif"]) if t < POP["notif"] + .5 else "")))
    for nm, fn in (("mug", mug), ("phone", phone), ("tab", tabwin)):
        p, _ = tail_pt(FR[nm], t)
        obs.append((p[1], fn(p[0], p[1], 1, t, POP[nm]) + popdust(p[0], p[1], t - POP[nm])))
    # кот сидит на дорожке
    pc, _ = tail_pt(FR["cat"], t)
    ec = t - POP["cat"]
    cs = 0.0
    if ec > 0:
        cs = 0.215 * spring(ec, 2.4, 6.5)
    if cs > 0.001:
        look = (-0.9, -0.1) if ec < 0.6 else (-0.6, 0.3)
        blink = 0.0
        for c, half in ((17.3, .07),):
            if c - half <= t <= c + half:
                blink = 1 - abs(t - c) / half
        tail = 7 * math.sin(t * 2.2) + 3 * math.sin(t * 3.7 + 1)
        cg = cat.draw(pc[0], pc[1] + 4, cs, t, look=look, blink=blink, tilt=-4 * math.sin(t * 1.3), tail=tail, paw="none", shadow=True)
        obs.append((pc[1], cg + popdust(pc[0], pc[1], ec)))
    for _, g_ in sorted(obs, key=lambda q: q[0]):
        w.append(g_)
    # Дима
    pose = dima_pose(t)
    hip = pose["hip"]
    gx = float(hip[0])
    g, _h = dima.draw(pose)
    w.append(blob(ellipse_pts(gx + 8, ground(gx, t) + 6, 62, 9, 14), "#2c4a30", .35))
    w.append(g)
    # звёздочки удивления на спотыкании
    if T_JAM < t < T_JAM + 0.5:
        e = t - T_JAM
        for j in range(5):
            a = math.radians(-60 - j * 28)
            r = 40 + 70 * ease_out(e / 0.5, 2)
            hxp, hyp = gx + 36, ground(gx, t) - 230
            w.append(line([(hxp + math.cos(a) * (r - 20), hyp + math.sin(a) * (r - 20)), (hxp + math.cos(a) * r, hyp + math.sin(a) * r)],
                          6 * (1 - e / 0.5) + 1.5, INK, taper=.5, seed=730 + j))
    # камера: следует за Димой, к отъезду — на всё облако
    fx = clamp(gx + 150, 470, 700)
    if sid == "s08":
        v = clamp((t - 12.0) / (15.4 - 12.0))
        sc_ = 1.3 + 0.25 * ease_io(v)
        cx_, cy_ = fx, 800
    else:
        v = clamp((t - 15.4) / (17.96 - 15.4))
        a = ease_io(clamp((v - 0.35) / 0.65))
        sc_ = 1.55 + (0.93 - 1.55) * a
        cx_, cy_ = fx + (540 - fx) * a, 800 + (700 - 800) * a
    sx, sy = shake(t, T_JAM + 0.02, 7)
    rot = 0.5 * math.sin(t * 0.8) + wrot
    s.append(f'<g transform="{cam(cx_ + sx, cy_ + sy, sc_, rot)}"><g transform="translate({f(dx)} 0)">{"".join(w)}</g></g>')
    s.append(speed_streaks(wu, 500))
    return svg("".join(s))
