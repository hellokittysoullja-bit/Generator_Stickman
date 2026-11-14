"""Рукописное «кот» живым пером (рилс 60, s17): строчные прописные буквы, как пишут ручкой в тетради.
«к» — палочка и петелька-завиток с ножкой, «о» с соединением сверху (петелька выхода), «т» прописная — три палочки с арками (как «m»),
наклон ~15°, нажим: вниз толще, вверх и на связках тонко; перо пишет по времени.
kot(t, t0, dur, x0, y0, size) -> SVG (мир). Ключевые точки — в единицах строки: x-высота 60, низ строки y=0."""
import math

import numpy as np

# штрихи пера по порядку; переход между штрихами — без отрыва (точка конца = точка начала), острый угол
STROKES = [
    # к: подход снизу и палочка вниз
    [(-14, -4), (-6, -20), (2, -44), (8, -60)],
    [(8, -60), (6, -30), (3, 0)],
    # возврат по палочке вверх и петелька-завиток плеча
    [(3, 0), (5, -24), (12, -32), (24, -46), (34, -58), (40, -56), (36, -46), (24, -36), (14, -32)],
    # ножка «к» вниз вправо с хвостиком-связкой
    [(14, -32), (22, -24), (30, -10), (38, -1), (46, 0), (54, -6), (62, -22), (72, -44), (84, -58)],
    # «о»: от верха против часовой, замыкается наверху, маленькая петелька выхода
    [(84, -58), (72, -56), (62, -42), (60, -20), (66, -4), (78, 1), (90, -6), (96, -24), (95, -44), (88, -57), (82, -58), (80, -50), (88, -46),
     (100, -50), (110, -58)],
    # «т» прописная: палочка, арка, палочка, арка, палочка с выходом
    [(110, -58), (112, -40), (111, -18), (109, 0)],
    [(109, 0), (111, -30), (116, -50), (126, -60), (136, -58), (142, -46), (142, -22), (141, 0)],
    [(141, 0), (143, -30), (148, -50), (158, -60), (168, -58), (174, -46), (174, -20), (176, -6), (184, 0), (194, -2), (204, -10)],
]
SLANT = math.tan(math.radians(13))


def _cr(pts, step=1.6):
    P = np.array(pts, float)
    P = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(3, int(np.linalg.norm(p2 - p1) / step))
        for s_ in np.linspace(0, 1, n, endpoint=False):
            out.append(.5 * (2 * p1 + (-p0 + p2) * s_ + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s_ * s_ + (-p0 + 3 * p1 - 3 * p2 + p3) * s_ ** 3))
    out.append(P[-2])
    return np.array(out)


_C = {}


def path():
    """Все штрихи подряд: (точки, толщина, номер штриха). Неровность почерка — фиксированным зерном (одинаково в каждом кадре)."""
    if "p" in _C:
        return _C["p"]
    rs = np.random.RandomState(60)
    segs = []
    for si, st in enumerate(STROKES):
        q = []
        for j, (x, y) in enumerate(st):
            # буквы разной высоты и строка чуть ползёт вверх
            hk = {0: 1.0, 1: 1.0, 2: 1.06, 3: 1.0, 4: .92, 5: 1.04, 6: 1.08, 7: 1.0}[si]
            yy = y * hk - .05 * x + rs.normal(0, .5)
            q.append((x - yy * SLANT + rs.normal(0, .5), yy))
        segs.append(_cr(q))
    P = np.vstack(segs)
    idx = np.concatenate([np.full(len(s), i) for i, s in enumerate(segs)])
    d = np.gradient(P, axis=0)
    down = d[:, 1] / (np.linalg.norm(d, axis=1) + 1e-9)
    w = 1.1 + 3.6 * np.clip(.15 + .9 * down, 0, 1) ** 1.6       # тонкое перо: вверх ~1.1, вниз до ~4.7 единиц
    w = np.convolve(w, np.ones(7) / 7, "same")
    w[:8] *= np.linspace(.4, 1, 8)
    w[-14:] *= np.linspace(1, .25, 14)
    _C["p"] = (P, w, idx)
    return _C["p"]


def _poly(Q, W):
    d = np.gradient(Q, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    N = np.stack([-d[:, 1], d[:, 0]], 1)
    L, R = Q + N * (W / 2)[:, None], Q - N * (W / 2)[:, None]
    pp = [tuple(p) for p in L] + [tuple(p) for p in R[::-1]]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pp) + "Z"


def kot(t, t0, dur, x0, y0, size=2.0, col="#1d2448", pen=True):
    if t < t0:
        return ""
    P, W, idx = path()
    u = min(1.0, (t - t0) / dur)
    # перо идёт ровно по длине линии, на острых углах чуть медлит
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    n = max(3, int(np.searchsorted(L, L[-1] * u)))
    o = []
    Q = P[:n] * size + np.array([x0, y0])
    Wd = W[:n] * size
    ids = idx[:n]
    for k in np.unique(ids):     # штрих за штрихом: на поворотах пера нет «перемычек» от смещения нормалей
        m = ids == k
        if m.sum() < 2:
            continue
        o.append(f'<path d="{_poly(Q[m], Wd[m])}" fill="{col}"/>')
        o.append(f'<circle cx="{Q[m][-1][0]:.1f}" cy="{Q[m][-1][1]:.1f}" r="{Wd[m][-1] / 2:.2f}" fill="{col}"/>')
        o.append(f'<circle cx="{Q[m][0][0]:.1f}" cy="{Q[m][0][1]:.1f}" r="{Wd[m][0] / 2:.2f}" fill="{col}"/>')
    if pen and u < 1:
        tip = Q[-1]
        ang = -58
        o.append(f'<g transform="translate({tip[0]:.1f} {tip[1]:.1f}) rotate({ang})">'
                 f'<path d="M0 0L14 -6L120 -10L124 0L120 10L14 6Z" fill="#2e3a6e" stroke="#151826" stroke-width="3"/>'
                 f'<path d="M0 0L14 -6L14 6Z" fill="#d8c48a" stroke="#151826" stroke-width="2"/>'
                 f'<path d="M60 -9L100 -9" stroke="#8fa0d8" stroke-width="3" stroke-linecap="round"/></g>')
    return "".join(o)
