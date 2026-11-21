"""Кривые и тушь для SVG-сцены: сплайн через точки, контур переменной толщины ЗАЛИВКОЙ.

Точка — (x, y) или (x, y, 1): единица = угол (касательные не сглаживаются).
fill_d(pts)        — гладкий путь для заливки (кубические Безье, векторно).
ink_closed(pts, w) — кольцо туши вокруг замкнутой фигуры: толщина «дышит» и толще на теневой стороне.
ink_open(pts, w)   — штрих: тонкий на концах, утолщение в середине (как кисть/перо).
"""
import math

import numpy as np


def _pts(pts):
    P, C = [], []
    for p in pts:
        P.append((float(p[0]), float(p[1])))
        C.append(len(p) > 2 and bool(p[2]))
    return np.array(P), C


def _beziers(pts, closed, tension=0.5):
    P, C = _pts(pts)
    n = len(P)

    def tan_out(k):
        if C[k] or (not closed and k == 0):
            return (P[(k + 1) % n] - P[k]) * 2 * tension * 0.6
        return (P[(k + 1) % n] - P[(k - 1) % n]) * tension

    def tan_in(k):
        if C[k] or (not closed and k == n - 1):
            return (P[k] - P[(k - 1) % n]) * 2 * tension * 0.6
        return (P[(k + 1) % n] - P[(k - 1) % n]) * tension

    segs = []
    for i in (range(n) if closed else range(n - 1)):
        a, b = i, (i + 1) % n
        segs.append((P[a], P[a] + tan_out(a) / 3, P[b] - tan_in(b) / 3, P[b]))
    return segs


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def fill_d(pts, closed=True):
    segs = _beziers(pts, closed)
    d = [f"M{f(segs[0][0][0])} {f(segs[0][0][1])}"]
    for _, c1, c2, b in segs:
        d.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(b[0])} {f(b[1])}")
    if closed:
        d.append("Z")
    return "".join(d)


def sample(pts, closed=True, step=2.5):
    out = []
    for a, c1, c2, b in _beziers(pts, closed):
        L = np.linalg.norm(c1 - a) + np.linalg.norm(c2 - c1) + np.linalg.norm(b - c2)
        m = max(2, int(L / step))
        t = np.linspace(0, 1, m, endpoint=False)[:, None]
        q = ((1 - t) ** 3) * a + 3 * ((1 - t) ** 2) * t * c1 + 3 * (1 - t) * t * t * c2 + t ** 3 * b
        out.append(q)
    if not closed:
        out.append(np.array([_beziers(pts, closed)[-1][3]]))
    S = np.vstack(out)
    # убрать совпадающие подряд
    keep = np.ones(len(S), bool)
    keep[1:] = np.linalg.norm(np.diff(S, axis=0), axis=1) > 1e-3
    return S[keep]


def _normals(S, closed):
    if closed:
        T = np.roll(S, -1, 0) - np.roll(S, 1, 0)
    else:
        T = np.gradient(S, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    return np.stack([-T[:, 1], T[:, 0]], 1)


def _noise(n, seed, scale=0.06):
    rs = np.random.RandomState(seed)
    k = max(3, int(n * scale))
    ctrl = rs.uniform(-1, 1, k + 3)
    x = np.linspace(0, k, n)
    i = np.floor(x).astype(int)
    t = x - i
    t = t * t * (3 - 2 * t)
    return ctrl[i] * (1 - t) + ctrl[i + 1] * t


def _poly(L, R):
    pts = np.vstack([L, R[::-1]])
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"


LIGHT = np.array([-0.45, -0.9])  # свет сверху-слева: теневая сторона — низ и право
LIGHT /= np.linalg.norm(LIGHT)


def ink_closed(pts, w=5.0, var=0.28, weight=0.45, seed=1, step=2.5):
    S = sample(pts, True, step)
    N = _normals(S, True)
    # наружная нормаль: по знаку площади
    area = 0.5 * np.sum(S[:, 0] * np.roll(S[:, 1], -1) - np.roll(S[:, 0], -1) * S[:, 1])
    if area > 0:
        N_out = -N
    else:
        N_out = N
    shade = np.clip(-(N_out @ LIGHT), 0, 1)  # 1 — нормаль от света
    W = w * (1 + var * _noise(len(S), seed)) * (1 - weight * 0.5 + weight * shade)
    W = np.maximum(W, w * 0.35)
    S2 = np.vstack([S, S[:2]])
    N2 = np.vstack([N, N[:2]])
    W2 = np.concatenate([W, W[:2]])
    return _poly(S2 + N2 * W2[:, None] / 2, S2 - N2 * W2[:, None] / 2)


def ink_open(pts, w=4.0, taper=0.5, wmin=0.15, var=0.15, seed=2, step=2.0, peak=0.5):
    """Штрих с нажимом: толщина = w в «пике» (peak — где по длине), к концам падает до w*wmin."""
    S = sample(pts, False, step)
    if len(S) < 3:
        return ""
    N = _normals(S, False)
    d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    u = d / max(d[-1], 1e-6)
    left = np.clip(u / max(peak, 1e-3), 0, 1)
    right = np.clip((1 - u) / max(1 - peak, 1e-3), 0, 1)
    prof = np.minimum(left, right)
    prof = np.sin(prof * math.pi / 2) ** taper
    W = w * (wmin + (1 - wmin) * prof) * (1 + var * _noise(len(S), seed))
    # круглые концы: добавить полукруг из 4 точек не обязательно — концы сходятся к острию
    return _poly(S + N * W[:, None] / 2, S - N * W[:, None] / 2)


def ellipse_pts(cx, cy, rx, ry, n=12, rot=0.0, jitter=0.0, seed=0):
    rs = np.random.RandomState(seed)
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    out = []
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for t in a:
        j = 1 + jitter * rs.uniform(-1, 1)
        x, y = rx * math.cos(t) * j, ry * math.sin(t) * j
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def fur(pts, depth=10, every=3, seed=0, closed=True):
    """Пушистый край: между исходными точками вставляет зубцы-пряди наружу."""
    S = sample(pts, closed, step=4)
    N = _normals(S, closed)
    area = 0.5 * np.sum(S[:, 0] * np.roll(S[:, 1], -1) - np.roll(S[:, 0], -1) * S[:, 1])
    N_out = -N if area > 0 else N
    rs = np.random.RandomState(seed)
    out = []
    step_n = max(3, int(every))
    for i in range(0, len(S), step_n):
        p = S[i]
        out.append((p[0], p[1]))
        j = i + step_n // 2
        if j < len(S):
            q = S[j] + N_out[j] * depth * rs.uniform(0.5, 1.2)
            # прядь чуть наклонена «по шерсти» (вниз)
            q = q + np.array([0, depth * 0.25])
            out.append((q[0], q[1], 1))
    return out


def band(pts, w0, w1, step=6.0, wmid=None, cap=True):
    """Контур «колбаски» вдоль средней линии (хвост, палец): толщина w0 в начале → w1 в конце."""
    S = sample(pts, False, step)
    N = _normals(S, False)
    u = np.linspace(0, 1, len(S))
    if wmid is None:
        W = w0 + (w1 - w0) * u
    else:
        W = np.where(u < 0.5, w0 + (wmid - w0) * u * 2, wmid + (w1 - wmid) * (u - 0.5) * 2)
    L = S + N * W[:, None] / 2
    R = S - N * W[:, None] / 2
    out = [tuple(p) for p in L]
    if cap:
        T = S[-1] - S[-2]
        T = T / (np.linalg.norm(T) + 1e-9)
        out.append(tuple(S[-1] + T * W[-1] * 0.45))
    out += [tuple(p) for p in R[::-1]]
    return out
