"""Кот спит калачиком (рилс 33, s10): тот же кот, что cat_sit (голова, уши — ЛЕВОЕ от зрителя загнуто, по две
оранжевые полоски на щеках, закрытые глаза-дуги), тело — пушистый овал лёжа, передние лапки под подбородком, хвост
обвивает тело спереди, огонёк на кончике притушен (меньше и темнее). Дыхание — бока поднимаются.
Внутренние координаты cat_sit; draw(x, y, s, t) ставит точку (900, 1310) (низ тела по центру) в (x, y)."""
import math

import cat_sit
import lib
from ink import ellipse_pts, fill_d, fur, ink_closed, sample
from lib import INK, blob, clip_of, line, shape

CAT, CAT_SH, CAT_FUR, CAT_EDGE = cat_sit.CAT, cat_sit.CAT_SH, cat_sit.CAT_FUR, cat_sit.CAT_EDGE
BX, BY = 900.0, 1310.0
HEAD_C = (836.0, 1068.0)
HEAD_TO = (738.0, 1176.0)
HEAD_ROT = -14.0


def body():
    pts = [(700, 1300), (690, 1250), (716, 1190), (790, 1140), (900, 1122), (1010, 1132), (1088, 1170), (1118, 1230), (1104, 1290),
           (1060, 1318, 1), (740, 1318, 1)]
    bp = fur(pts, 7, 7, seed=31)
    inner = blob([(690, 1262), (1120, 1250), (1120, 1320), (690, 1320)], CAT_SH, .85)
    inner += blob([(800, 1150), (900, 1134), (1000, 1144), (960, 1172), (860, 1176)], CAT_FUR, .6)
    # бедро задней лапы
    inner += line([(1000, 1290), (990, 1236), (1020, 1196), (1070, 1190)], 3.6, INK, seed=301, taper=.5, wmin=.2)
    inner += blob([(1004, 1200), (1066, 1192), (1100, 1236), (1090, 1290), (1010, 1292), (998, 1240)], CAT_SH, .35)
    for i, st in enumerate([[(850, 1160), (858, 1176)], [(910, 1150), (914, 1168)], [(960, 1160), (956, 1178)], [(880, 1196), (888, 1212)]]):
        inner += line(st, 2.2, CAT_EDGE, seed=310 + i, op=.85)
    return shape(bp, CAT, inner, w=5, seed=320)


def tail():
    C = [(1060, 1286), (1112, 1290), (1150, 1262), (1166, 1218), (1158, 1178), (1136, 1150)]
    S = sample(C, False, 3.0)
    import numpy as np
    n = len(S)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = 42 + (18 - 42) * np.linspace(0, 1, n) ** 1.1
    L, R = S + N * Wd[:, None] / 2, S - N * Wd[:, None] / 2
    tip = S[-1] + Tg[-1] * Wd[-1] * .45
    outline = [tuple(p) for p in L] + [tuple(tip)] + [tuple(p) for p in R[::-1]]
    sh = blob([(1150, 1140), (1200, 1140), (1200, 1300), (1120, 1300)], CAT_SH, .8)
    o = [f'<path d="{fill_d(outline)}" fill="{CAT}"/>']
    c = clip_of(outline)
    o.append(f'<g clip-path="url(#{c})">{sh}</g>')
    o.append(f'<path d="{ink_closed(outline, 4.8, seed=330)}" fill="{INK}"/>')
    for i, k in enumerate(range(int(n * .15), int(n * .85), int(n * .14))):
        p = S[k] - N[k] * Wd[k] * .15
        q = p + Tg[k] * 12
        o.append(line([tuple(p), tuple(q)], 2, CAT_EDGE, seed=336 + i, op=.8))
    return "".join(o), tuple(tip), tuple(Tg[-1])


def paws():
    o = []
    for k, (px, py) in enumerate([(688, 1296), (758, 1302)]):
        foot = ellipse_pts(px, py, 32, 20, 12, rot=-8)
        o.append(shape(foot, CAT, blob(ellipse_pts(px + 4, py + 6, 24, 12, 10), CAT_SH, .5), w=4.4, seed=340 + k))
        for j in (-1, 0, 1):
            o.append(line([(px - 14 + j * 9 + 14, py - 6), (px - 14 + j * 9 + 14, py + 8)], 2, seed=343 + k * 3 + j, op=.9))
    return "".join(o)


def dim_flame(t, base, k=1.0):
    bx, by = base
    w1 = 2.4 * math.sin(t * 9) + 1.6 * math.sin(t * 15 + 1)
    w2 = 2.6 * math.sin(t * 11 + 2)
    P = [(-18, 4), (-20, -12), (-12, -26 + w2 * .3), (-9 + w1 * .3, -38), (-2, -32), (3 + w1 * .6, -56 + w2 * .5, 1), (10, -36), (17, -42 + w1 * .3, 1),
         (20, -24), (18, -8), (12, 4), (0, 8)]

    def tf(q):
        return (bx + q[0] * k, by + q[1] * k) + ((1,) if len(q) > 2 else ())
    o = shape([tf(q) for q in P], "#c9652e", blob([tf((q[0] * .62, q[1] * .62 + 3) + q[2:]) for q in P], "#e99a4a"), w=3.2, seed=350,
              ink_color="#6a2610", var=.2)
    o += blob([tf(q) for q in [(-5, 3), (-3, -12), (2, -22), (5, -11), (4, 3)]], "#f6c47a")
    return o


def draw(x, y, s, t, breath=None, head_dy=0.0):
    br = (0.5 + 0.5 * math.sin(t * 2 * math.pi / 2.3)) if breath is None else breath
    o = [blob(ellipse_pts(905, 1318, 250, 26, 18), "#1a0e05", .3, lib.blur(6))]
    sy = 1 + 0.045 * br
    sx = 1 + 0.012 * br
    tl, tip, tg = tail()
    fb = (tip[0] + 2, tip[1] + 2)
    o.append(tl)
    o.append(dim_flame(t, fb))
    o.append(f'<g transform="translate({BX} {BY}) scale({sx:.4f} {sy:.4f}) translate({-BX} {-BY})">{body()}</g>')
    o.append(paws())
    # голова: прижата к лапкам, чуть наклонена; дыхание приподнимает её немного
    hy = -6 * br + head_dy
    hg = cat_sit.head_static() + cat_sit.ears(0.0) + cat_sit.face_static() + cat_sit.eyes((0, 0), 1.0)
    hx, hyy = HEAD_TO[0] - HEAD_C[0], HEAD_TO[1] - HEAD_C[1] + hy
    o.append(f'<g transform="translate({hx:.2f} {hyy:.2f}) rotate({HEAD_ROT} {HEAD_C[0]} {HEAD_C[1]})">{hg}</g>')
    return f'<g transform="translate({x - BX * s:.2f} {y - BY * s:.2f}) scale({s:.4f})">{"".join(o)}</g>'


def head_top(x, y, s, t):
    """Мировая точка над головой (для Z)."""
    return (x + (HEAD_TO[0] + 40 - BX) * s, y + (HEAD_TO[1] - 120 - BY) * s)


def zzz(x, y, s, t, t0):
    """Три «Z» поднимаются по очереди от головы, растут и сжимаются у верха (без прозрачности)."""
    o = []
    for j in range(3):
        u = (t - t0 - j * .43) / 1.3
        if u <= 0:
            continue
        u = u % 1.0
        sc = s * (0.55 + 0.75 * u) * min(1.0, u / .12) * (1 - lib.smooth(.82, 1.0, u))
        if sc <= 0.01:
            continue
        cx = x - (10 + 110 * u - 18 * math.sin(u * 6 + j)) * s
        cy = y - 260 * u * s
        w, h, th = 52 * sc, 56 * sc, 13 * sc
        P = [(0, 0, 1), (w, 0, 1), (w, th, 1), (th * 1.7, h - th, 1), (w, h - th, 1), (w, h, 1), (0, h, 1), (0, h - th, 1), (w - th * 1.7, th, 1), (0, th, 1)]
        rot = math.radians(-10 + 8 * math.sin(u * 5 + j))
        cr, sr = math.cos(rot), math.sin(rot)
        Q = [(cx + (p[0] - w / 2) * cr - (p[1] - h / 2) * sr, cy + (p[0] - w / 2) * sr + (p[1] - h / 2) * cr, 1) for p in P]
        o.append(shape(Q, "#f4efe2", "", w=3.6 * sc, seed=360 + j, var=.15))
    return "".join(o)
