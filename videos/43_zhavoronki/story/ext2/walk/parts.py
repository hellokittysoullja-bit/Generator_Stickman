"""Общие детали 2D-сцен рилса 25: палец-«сосиска» с круглым кончиком и семисегментные цифры."""
import math

import numpy as np

import lib
from lib import blob, ellipse_pts

SEGS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
        "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}


def sausage(pts, w0, w1):
    """Контур пальца: гладкая средняя линия, толщина w0 → w1, кончик — полукруг (без острия)."""
    S = lib.sample(pts, False, 2.0)
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


def seg_poly(name, ox, oy, dw, dh, th, skew=0.12):
    g = th * 0.55
    h2 = th / 2
    mid = dh / 2
    if name in "agd":
        y = {"a": 0, "g": mid, "d": dh}[name]
        x0, x1 = g, dw - g
        pts = [(x0, y), (x0 + h2, y - h2), (x1 - h2, y - h2), (x1, y), (x1 - h2, y + h2), (x0 + h2, y + h2)]
    else:
        x = dw if name in "bc" else 0
        y0, y1 = (g, mid - g) if name in "bf" else (mid + g, dh - g)
        pts = [(x, y0), (x + h2, y0 + h2), (x + h2, y1 - h2), (x, y1), (x - h2, y1 - h2), (x - h2, y0 + h2)]
    return [(ox + px - (py - dh / 2) * skew, oy + py, 1) for px, py in pts]


def sevenseg(text, x, y, dw, dh, th, lit, ghost=None, gap=None, glow=0.0, glow_col=None, skew=0.12):
    """Строка цифр и «:» слева-сверху в (x, y). Возвращает SVG (свечение — размытая копия под цифрами)."""
    gap = th * 1.3 if gap is None else gap
    lit_p, ghost_p = [], []
    cx = x
    for ch in text:
        if ch == ":":
            for dy in (-dh * 0.2, dh * 0.2):
                p = ellipse_pts(cx + th * 0.6 - dy * skew, y + dh / 2 + dy, th * 0.5, th * 0.5, 10)
                lit_p.append(p)
            cx += th * 1.2 + gap
            continue
        on = SEGS.get(ch, "")
        for n in "abcdefg":
            (lit_p if n in on else ghost_p).append(seg_poly(n, cx, y, dw, dh, th, skew))
        cx += dw + gap
    s = []
    if ghost:
        s += [blob(p, ghost) for p in ghost_p]
    if glow > 0:
        g = "".join(blob(p, glow_col or lit) for p in lit_p)
        s.append(f'<g opacity="{min(1, glow):.3f}" {lib.blur(max(3, th * 0.6))}>{g}</g>')
    s += [blob(p, lit) for p in lit_p]
    return "".join(s), cx - gap
