"""Бумажная лента (свиток списка) в 3D для рилса 33: средняя линия ленты в мире (см), ширина — вдоль вектора B,
проекция камерой-дыркой. Лента режется на куски одной стороны (лицо / изнанка); на сгибах проекции сторона меняется,
поэтому кусок одной стороны не перекрывает сам себя. Куски рисуются от дальних к ближним, у лица — строки-каракули
(серые волнистые линии без букв) в координате бумаги s (длина от начала ленты), так что строки едут вместе с бумагой.
Рулон — цилиндр с осью вдоль B (торец — мультяшный эллипс со спиралью)."""
import math

import numpy as np

import lib
from lib import INK, blob, clip_of, line, shape

PAPER, PAPER_BACK, PAPER_SH = "#fbf7ec", "#e4dcc8", "#d9cfb6"
SCRIB = "#8d8a94"


class Cam:
    """Камера-дырка: глаз в (ex, ey, ez), смотрит вдоль +Z, Y вниз; экран — f, центр (cx, cy)."""

    def __init__(self, f=1100.0, cx=540.0, cy=960.0, eye=(0.0, 0.0, 0.0)):
        self.f, self.cx, self.cy = f, cx, cy
        self.eye = np.array(eye, float)

    def p(self, P):
        P = np.asarray(P, float) - self.eye
        z = np.maximum(P[..., 2], 1.0)
        return np.stack([self.cx + self.f * P[..., 0] / z, self.cy + self.f * P[..., 1] / z], -1)

    def k(self, Z):
        """px на см на глубине Z."""
        return self.f / max(1.0, Z - self.eye[2])


def arclen(P):
    return np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])


def resample(P, step=0.6):
    s = arclen(P)
    n = max(3, int(s[-1] / step))
    u = np.linspace(0, s[-1], n)
    return np.stack([np.interp(u, s, P[:, i]) for i in range(3)], 1)


def _scribbles(cam, P, s, T, B, W, s0, s1, ink_k, seed, gap=2.6, first=1.6):
    """Строки-каракули на куске [s0, s1]: у каждой строки точка-номер слева и волнистая линия своей длины."""
    out = []
    j0 = max(0, int(math.floor((s0 - first) / gap)))
    j1 = int(math.ceil((s1 - first) / gap))
    for j in range(j0, j1 + 1):
        sj = first + j * gap
        if sj < s0 - 1 or sj > s1 + 1:
            continue
        rs = np.random.RandomState(seed + j * 7)
        L = rs.uniform(.42, .74)
        x0 = -W / 2 + W * .2
        pts = []
        for q in np.linspace(0, 1, 14):
            u = x0 + q * W * L
            sw = sj + 0.32 * math.sin(q * 11 + j * 1.7) + 0.18 * math.sin(q * 23 + j)
            i = int(np.clip(np.searchsorted(s, sw), 1, len(s) - 1))
            a = (sw - s[i - 1]) / max(1e-6, s[i] - s[i - 1])
            a = min(1.0, max(0.0, a))
            pc = P[i - 1] * (1 - a) + P[i] * a
            pts.append(pc + B[i] * u)
        pr = cam.p(np.array(pts))
        zk = cam.k(float(np.mean(np.array(pts)[:, 2])))
        out.append(line([tuple(q) for q in pr], 0.55 * zk * ink_k, SCRIB, taper=.4, wmin=.5, seed=seed + j, op=.95))
        # номер-точка слева
        i = int(np.clip(np.searchsorted(s, sj), 1, len(s) - 1))
        pc = P[i] + B[i] * (-W / 2 + W * .1)
        c = cam.p(pc)
        r = 0.42 * zk
        out.append(blob(lib.ellipse_pts(c[0], c[1], r, r * .9, 8), "#6f6b78"))
    return "".join(out)


def pieces(cam, P, W, B=None, seed=7000, ink_w=0.34, writing=True, s_offset=0.0, face_col=PAPER, back_col=PAPER_BACK,
           shade=None, item_depth=None):
    """Лента по средней линии P (N×3, см). Возвращает список (глубина, svg) — сортировка снаружи вместе с другими
    предметами. B — вектор ширины (по умолчанию X). s_offset — координата бумаги в начале P."""
    P = np.asarray(P, float)
    if len(P) < 3:
        return []
    n = len(P)
    if B is None:
        B = np.tile(np.array([1.0, 0, 0]), (n, 1))
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.cross(T, B)
    V = cam.eye[None, :] - P
    face = np.sum(N * V, 1) > 0
    s = arclen(P) + s_offset
    # куски одной стороны
    cuts = [0] + [i for i in range(1, n) if face[i] != face[i - 1]] + [n - 1]
    runs = [(cuts[k], cuts[k + 1], bool(face[cuts[k]])) for k in range(len(cuts) - 1)]
    out = []
    for (a, b, fc) in runs:
        if b - a < 1:
            continue
        idx = np.arange(a, b + 1)
        Lp = cam.p(P[idx] - B[idx] * W / 2)
        Rp = cam.p(P[idx] + B[idx] * W / 2)
        poly = [tuple(Lp[0]) + (1,)] + [tuple(q) for q in Lp[1:-1]] + [tuple(Lp[-1]) + (1,), tuple(Rp[-1]) + (1,)] + \
               [tuple(q) for q in Rp[-2:0:-1]] + [tuple(Rp[0]) + (1,)]
        zm = float(np.mean(P[idx, 2]))
        zk = cam.k(zm)
        col = face_col if fc else back_col
        inner = ""
        if fc and writing:
            inner += _scribbles(cam, P, s, T, B, W, s[a], s[b], 1.0, seed)
        if shade is not None:
            inner += shade(idx, fc, P, Lp, Rp)
        sv = shape(poly, col, inner, w=ink_w * zk, seed=seed + a, var=.18, weight=.35)
        depth = item_depth if item_depth is not None else float(np.mean(np.linalg.norm(P[idx] - cam.eye, axis=1)))
        out.append((depth, sv))
    return out


def roll(cam, C, r, W, ang, seed=7500, B=np.array([1.0, 0, 0]), cap_side=-1, squash=1.0, ink_w=0.34):
    """Рулон: ось вдоль B, центр C (см), радиус r, поворот ang (рад) — по нему крутится спираль торца и строки.
    cap_side — какой торец показать (-1 — левый). Рисуется как боковой силуэт + торец-эллипс."""
    C = np.asarray(C, float)
    zk = cam.k(C[2])
    a = cam.p(C - B * W / 2)
    b = cam.p(C + B * W / 2)
    R = r * zk
    Ry = R * squash
    ux = (b - a) / (np.linalg.norm(b - a) + 1e-9)
    ny = np.array([-ux[1], ux[0]])
    if ny[1] < 0:
        ny = -ny
    pts = [tuple(a - ny * Ry) + (1,), tuple(b - ny * Ry) + (1,), tuple(b + ny * Ry) + (1,), tuple(a + ny * Ry) + (1,)]
    inner = blob([tuple(a + ny * Ry * .35), tuple(b + ny * Ry * .35), tuple(b + ny * Ry), tuple(a + ny * Ry)], PAPER_SH, .9)
    inner += blob([tuple(a - ny * Ry * .55), tuple(b - ny * Ry * .55), tuple(b - ny * Ry * .25), tuple(a - ny * Ry * .25)], "#ffffff", .6)
    # строки на рулоне бегут при вращении
    for j in range(4):
        ph = (ang * 0.9 + j * math.pi / 2) % (2 * math.pi)
        if ph > math.pi:
            continue
        v = -math.cos(ph)
        rs = np.random.RandomState(seed + j)
        L = rs.uniform(.45, .7)
        p0 = a + (b - a) * .2 + ny * Ry * v * .9
        p1 = a + (b - a) * (.2 + L * .75) + ny * Ry * v * .9
        out_w = 0.5 * zk * math.sin(ph) + .2
        inner += line([tuple(p0), tuple((p0 + p1) / 2 + ny * 2 * math.sin(j)), tuple(p1)], out_w, SCRIB, seed=seed + 10 + j, op=.9)
    o = [shape(pts, PAPER, inner, w=ink_w * zk, seed=seed, var=.18)]
    # торец
    e = a if cap_side < 0 else b
    rx = R * .42
    cap = lib.ellipse_pts(e[0], e[1], rx, Ry, 20)
    sp = []
    for q in np.linspace(0, 1, 40):
        rr = .15 + .8 * q
        th = ang + q * 2.6 * 2 * math.pi
        sp.append((e[0] + rx * rr * math.cos(th), e[1] + Ry * rr * math.sin(th)))
    o.append(shape(cap, "#f3ecdc", line(sp, 0.22 * zk, "#b8ae98", seed=seed + 30, taper=.2, wmin=.6) +
                   blob(lib.ellipse_pts(e[0], e[1], rx * .16, Ry * .16, 8), "#c9bea6"), w=ink_w * zk, seed=seed + 31))
    return "".join(o)


_ = (INK, clip_of)
