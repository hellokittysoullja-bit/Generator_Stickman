"""Кисть с пальцами (не варежка): ладонь, четыре пальца и большой, вид с тыла кисти. Строится в своих координатах:
запястье в (0, 0), кисть вдоль +x; потом поворачивается углом ang и ставится в (x, y). Контур — единый силуэт: пальцы
рисуются поверх ладони, а их основания закрывает заплатка цвета ладони без туши (нет линии «приклеенных» пальцев).
mode: rest — расслабленно, пальцы чуть врозь; open — раскрыта, пальцы веером; grip — пальцы согнуты (короче, костяшки);
point — указательный вытянут, остальные согнуты. thumb_up — большой палец со стороны −y (иначе +y)."""
import math

import numpy as np

import lib
from lib import blob, f, line, shape

FINGERS = [  # base_x, base_y, длина, толщина, базовый угол (веер)
    (37, -13.0, 30, 11.6, -9),
    (39, -4.0, 34, 12.0, -2),
    (38, 5.2, 31, 11.6, 5),
    (34, 13.4, 24, 10.4, 12),
]


def _sausage(pts, w0, w1):
    S = lib.sample(pts, False, 1.5)
    T = np.gradient(S, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    Wd = np.linspace(w0, w1, len(S))[:, None] / 2
    L, R = S + N * Wd, S - N * Wd
    end, tn, nn = S[-1], T[-1], N[-1]
    r = w1 / 2
    cap = [tuple(end + nn * r * math.cos(a) + tn * r * math.sin(a)) for a in np.linspace(0, math.pi, 9)[1:-1]]
    step = max(1, len(S) // 8)
    return [tuple(p) for p in L[::step]] + [tuple(L[-1])] + cap + [tuple(R[-1])] + [tuple(p) for p in R[::-step]]


def _finger(bx, by, ang, L, wd, curl, seg_k=(0.42, 0.32, 0.26)):
    pts = [(bx - 6 * math.cos(math.radians(ang)), by - 6 * math.sin(math.radians(ang))), (bx, by)]
    a, x, y = ang, bx, by
    for k in seg_k:
        x += L * k * math.cos(math.radians(a))
        y += L * k * math.sin(math.radians(a))
        pts.append((x, y))
        a += curl
    return pts


def hand5(x, y, ang, skin, shade, sd=0, sc=1.0, mode="rest", thumb_up=True, spread=1.0, ink_w=3.0, nails=True):
    flip = 1 if thumb_up else -1
    s = []
    fs = []
    tips = []
    for i, (bx, by, L, wd, fa) in enumerate(FINGERS):
        curl = 0.0
        LL = L
        a = fa * spread
        if mode == "open":
            a = fa * 2.2 * spread
            curl = -4
        elif mode == "rest":
            curl = 6
            LL = L * 0.92
        elif mode == "grip":
            curl = 34
            LL = L * 0.78
            a = fa * 0.5
        elif mode == "point":
            if i == 0:
                a, curl = -4, 0
            else:
                curl, LL, a = 52, L * 0.62, fa * 0.4
        pts = _finger(bx, by * flip, a * flip, LL, wd, curl * flip)
        fs.append(shape(_sausage(pts, wd, wd * .9), skin, blob(_sausage([(px, py + 2.2 * flip) for px, py in pts[1:]], wd * .42, wd * .36), shade, .55),
                        w=ink_w * 0.9, seed=sd + 10 + i))
        tips.append((pts[-1], pts[-2], wd))
    # большой палец: от края ладони у запястья наружу и вперёд
    th_a = (-58 if mode != "grip" else -28) * flip
    tpts = _finger(12, -13 * flip, th_a, 30, 13, (22 if mode != "open" else 10) * flip, seg_k=(0.45, 0.35, 0.2))
    thumb = shape(_sausage(tpts, 14, 11.5), skin, "", w=ink_w * 0.9, seed=sd + 20)
    palm = [(-2, -12 * flip), (10, -17 * flip), (28, -20.5 * flip), (40, -17.5 * flip), (44, -7 * flip), (44, 6 * flip), (40, 16 * flip),
            (28, 20 * flip), (10, 15.5 * flip), (-2, 11 * flip)]
    pin = blob([(4, 6 * flip), (30, 12 * flip), (44, 8 * flip), (42, 16 * flip), (30, 21 * flip), (10, 18 * flip), (0, 14 * flip)], shade, .7)
    s.append(thumb)
    s.append(shape(palm, skin, pin, w=ink_w, seed=sd + 1))
    order = [3, 2, 1, 0] if thumb_up else [0, 1, 2, 3]
    s += [fs[i] for i in order]
    # заплатка: закрывает основания пальцев внутри ладони (единый силуэт без линий-стыков)
    patch = [(3, -9 * flip), (12, -13.5 * flip), (28, -17 * flip), (37, -14.5 * flip), (40.5, -6 * flip), (40.5, 6 * flip), (36.5, 13 * flip),
             (28, 16.5 * flip), (10, 12.5 * flip), (3, 8 * flip)]
    s.append(blob(patch, skin))
    s.append(blob([(6, 4 * flip), (28, 10 * flip), (39, 8 * flip), (36.5, 13 * flip), (28, 16.5 * flip), (10, 12.5 * flip), (3, 8 * flip)], shade, .7))
    # костяшки — короткие штрихи, ногти на кончиках
    for i, (bx, by, L, wd, fa) in enumerate(FINGERS):
        s.append(line([(bx - 4, by * flip - 3), (bx - 1, by * flip + 1), (bx - 4, by * flip + 4)], ink_w * .55, shade, taper=.6, seed=sd + 40 + i, op=.8))
    if nails and mode in ("rest", "open", "point"):
        for i, (tip, prev, wd) in enumerate(tips):
            if mode == "point" and i > 0:
                continue
            dx, dy = tip[0] - prev[0], tip[1] - prev[1]
            a = math.degrees(math.atan2(dy, dx))
            s.append(f'<ellipse cx="{f(tip[0] - dx * .12)}" cy="{f(tip[1] - dy * .12)}" rx="{f(wd * .3)}" ry="{f(wd * .24)}" '
                     f'transform="rotate({f(a)} {f(tip[0] - dx * .12)} {f(tip[1] - dy * .12)})" fill="#ffffff" opacity=".45"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)}) scale({sc:.4f})">{"".join(s)}</g>'
