"""Рукописная надпись произвольного текста тем же пером, что «кот» (`hand_kot.py`, рилс 60): штрихи Catmull-Rom,
нажим вниз толще, вверх и на связках тонко, наклон 13°, перо пишет по времени (по длине линии).
Рилс 78: «Ты слабак?» в хуке — маркер-росчерк, пишется за 0.3 с, крупно (bold — толщина пера сверх «кот»).
hand_text(text, t, t0, dur, x0, y0, size, ink) -> SVG; (x0, y0) — левый край и линия строки; text_width(text, size) — ширина.
Буквы в единицах строки: x-высота 60, заглавные и «б» ~94, низ строки y=0. Есть: Т ы с л а б к ? и пробел
(«к» — из `hand_kot.py`); новой буквы нет — KeyError, а не тихая подмена."""
import math

import numpy as np

from hand_kot import STROKES as _KOT, _cr, _poly

SLANT = math.tan(math.radians(13))

# глиф: (ширина, [штрихи]); каждый штрих — точки в единицах строки, от левого края буквы
_K = [[(x + 14, y) for x, y in st] for st in _KOT[:3]] + [[(x + 14, y) for x, y in _KOT[3][:6]]]
GLYPHS = {
    "Т": (70, [[(0, -84), (10, -90), (30, -91), (50, -92), (66, -96)],                       # шапка с лёгкой волной
               [(34, -91), (33, -60), (31, -28), (29, -6), (24, 0), (16, -2)]]),            # ножка с завитком внизу
    "ы": (68, [[(0, -6), (6, -30), (12, -60)],
               [(12, -60), (11, -30), (10, 0)],
               [(10, 0), (11, -24), (24, -32), (37, -26), (39, -12), (31, -2), (13, -1)],     # петля «ь»
               [(52, -60), (51, -32), (50, -6), (57, 0), (66, -6)]]),                        # палочка
    "с": (44, [[(38, -50), (30, -60), (15, -57), (5, -38), (4, -14), (14, 0), (29, 0), (42, -10)]]),
    "л": (58, [[(0, -2), (8, -4), (15, -22), (21, -46), (29, -60), (38, -58), (40, -30), (40, -6), (48, 0), (57, -8)]]),
    "а": (58, [[(35, -50), (25, -60), (11, -54), (3, -32), (5, -10), (15, 0), (27, -6), (35, -24), (39, -58)],
               [(39, -58), (38, -22), (40, -5), (48, 0), (57, -8)]]),
    "б": (52, [[(50, -98), (38, -92), (23, -82), (13, -62), (6, -36), (6, -12), (16, 0), (31, -2), (41, -16), (41, -38),
                (31, -52), (17, -50), (9, -40)]]),
    "к": (72, _K),
    "?": (50, [[(4, -78), (12, -93), (28, -98), (43, -88), (43, -70), (31, -56), (25, -42), (25, -24)]]),
    " ": (34, []),
}
DOT = {"?": (25, -3)}        # точка знака вопроса — отдельный кружок в конце буквы
GAP = 6                      # просвет между буквами


def _layout(text):
    """Штрихи всей строки подряд: (точки, толщина, номер штриха, точки-кружки). Неровность почерка — фиксированным зерном."""
    rs = np.random.RandomState(78 + len(text))
    segs, dots, x = [], [], 0.0
    for i, ch in enumerate(text):
        w, strokes = GLYPHS[ch]
        hk = 1.0 + rs.normal(0, .035)                      # буквы чуть разной высоты
        for st in strokes:
            q = []
            for (px, py) in st:
                yy = py * hk - .03 * (x + px) + rs.normal(0, .5)    # строка чуть ползёт вверх
                q.append((x + px - yy * SLANT + rs.normal(0, .5), yy))
            segs.append(_cr(q))
        if ch in DOT:
            dx, dy = DOT[ch]
            dots.append((len(segs) - 1, (x + dx - dy * SLANT, dy - .03 * (x + dx))))
        x += w + GAP
    return segs, dots, x - GAP


_C = {}


def path(text):
    if text in _C:
        return _C[text]
    segs, dots, width = _layout(text)
    P = np.vstack(segs)
    idx = np.concatenate([np.full(len(s), i) for i, s in enumerate(segs)])
    d = np.gradient(P, axis=0)
    down = d[:, 1] / (np.linalg.norm(d, axis=1) + 1e-9)
    w = 1.1 + 3.6 * np.clip(.15 + .9 * down, 0, 1) ** 1.6
    # сглаживание и сужение концов — внутри каждого штриха (иначе толщина перетекает через отрыв пера)
    for k in range(len(segs)):
        m = np.where(idx == k)[0]
        ww = np.convolve(np.pad(w[m], 3, mode="edge"), np.ones(7) / 7, "valid")
        n = len(m)
        a = min(6, n // 3)
        if a:
            ww[:a] *= np.linspace(.55, 1, a)
            ww[-a:] *= np.linspace(1, .5, a)
        w[m] = ww
    _C[text] = (P, w, idx, dots, width)
    return _C[text]


def text_width(text, size=1.0):
    return path(text)[4] * size


def hand_text(text, t, t0, dur, x0, y0, size=1.4, ink="#1d2448", bold=1.8, pen=False, op=1.0):
    """Надпись к моменту t: перо идёт по длине линии от t0 за dur секунд (dur<=0 — сразу целиком)."""
    if t < t0 or not text.strip():
        return ""
    P, W, idx, dots, _ = path(text)
    u = 1.0 if dur <= 0 else min(1.0, (t - t0) / dur)
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    n = max(2, int(np.searchsorted(L, L[-1] * u)))
    if u >= 1:
        n = len(P)
    Q = P[:n] * size + np.array([x0, y0])
    Wd = (W[:n] * bold + 1.6 * bold) * size        # маркер: и волосные линии не тоньше ~1.6 единицы × bold
    ids = idx[:n]
    o = []
    for k in np.unique(ids):
        m = ids == k
        if m.sum() < 2:
            continue
        o.append(f'<path d="{_poly(Q[m], Wd[m])}"/>')
        o.append(f'<circle cx="{Q[m][-1][0]:.1f}" cy="{Q[m][-1][1]:.1f}" r="{Wd[m][-1] / 2:.2f}"/>')
        o.append(f'<circle cx="{Q[m][0][0]:.1f}" cy="{Q[m][0][1]:.1f}" r="{Wd[m][0] / 2:.2f}"/>')
    for si, (dx, dy) in dots:          # точка появляется, когда дописан штрих перед ней
        if si < int(ids[-1]) or u >= 1:
            o.append(f'<circle cx="{x0 + dx * size:.1f}" cy="{y0 + dy * size:.1f}" r="{4.6 * size * bold:.2f}"/>')
    if pen and u < 1:
        tip = Q[-1]
        o.append(f'<g transform="translate({tip[0]:.1f} {tip[1]:.1f}) rotate(-58)">'
                 f'<path d="M0 0L14 -6L120 -10L124 0L120 10L14 6Z" fill="#2e3a6e" stroke="#151826" stroke-width="3"/>'
                 f'<path d="M0 0L14 -6L14 6Z" fill="#d8c48a" stroke="#151826" stroke-width="2"/></g>')
    opa = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<g fill="{ink}"{opa}>{"".join(o)}</g>'
