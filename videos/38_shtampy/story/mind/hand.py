"""Кисть с пальцами для героев сцены cafe (Дима, друг): ладонь + 4 пальца по фалангам + большой палец.

Без «варежки» и двойных контуров: пальцы рисуются от мизинца к указательному (каждый поверх соседа — между ними
остаётся только край ближнего пальца), ладонь заливкой ложится ПОВЕРХ корней пальцев, тушь у ладони — только по бокам
(по линии костяшек её нет, корни пальцев под ладонью), большой палец — последним.

Система кисти: начало — запястье Wr, ось d — от запястья к пальцам, ось n — поперёк (flip меняет сторону большого
пальца). Единицы — L героя (голова ~300). Цвета и толщина туши — от вызывающего (shape_fn, line_fn, кожа).
"""
import math

import numpy as np

from ink import band, ellipse_pts

# корни пальцев (вдоль d, поперёк n), длина, толщина: указательный, средний, безымянный, мизинец
FING = [(70, -25, 66, 19.5), (76, -8, 72, 19.5), (74, 9, 67, 18.5), (66, 24, 54, 16.5)]
PALM = [(-4, -33), (30, -39), (60, -36), (74, -30), (82, -16), (84, 0), (82, 14), (77, 26), (66, 34), (36, 39), (4, 36)]
K0, K1 = 3, 8          # индексы PALM, между которыми — линия костяшек (без туши)


def _P(q):
    return (float(q[0]), float(q[1]))


def hand(Wr, d, *, shape_fn, line_fn, skin, skin_sh, skin_sh2, nail="#f1cdbd", flip=1, k=1.0,
         curl=(0, 0, 0, 0), spread=0.25, thumb=0.0, bend=0.12, seed=0, nails=True, show_thumb=True):
    """Раскрытая/жестикулирующая кисть.
    curl[i] 0 — палец прям, 1 — согнут к ладони (укорочен, видна складка); spread — веер пальцев (рад на край);
    thumb 0 — отведён, 1 — прижат к ладони; bend — лёгкий изгиб пальцев в плоскости (живость)."""
    Wr = np.array(Wr, float)
    d = np.array(d, float)
    d = d / (np.linalg.norm(d) + 1e-9)
    n = np.array([-d[1], d[0]]) * flip

    def tf(x, y):
        return Wr + d * x * k + n * y * k

    o = []
    # пальцы: мизинец → указательный
    for i in (3, 2, 1, 0):
        rx, ry, Lf, wf = FING[i]
        c = curl[i]
        a0 = spread * (ry / 25.0) * (1 - .6 * c)
        segs = [Lf * .44, Lf * .31, Lf * .25]
        segs = [s_ * (1 - .62 * c) for s_ in segs]
        p = np.array([rx - 16.0, ry * .95])
        dirv = np.array([math.cos(a0), math.sin(a0)])
        pts = [p.copy(), p + dirv * 16]
        p = pts[-1]
        ang = a0
        joints = []
        for j, sl in enumerate(segs):
            ang += bend * (j + 1) * .5 + c * .35
            p = p + np.array([math.cos(ang), math.sin(ang)]) * sl
            pts.append(p.copy())
            joints.append((p.copy(), ang))
        P_ = [_P(tf(*q)) for q in pts]
        outline = band(P_, wf * k, wf * .84 * k, step=2.5, cap=True)
        inner = ""
        # тень вдоль нижней (по n) стороны пальца
        sh = band(P_[1:], wf * .42 * k, wf * .3 * k, step=3, cap=False)
        sh = [(x + n[0] * wf * .3 * k, y + n[1] * wf * .3 * k) for x, y in sh]
        inner += f'<path d="{_fill(sh)}" fill="{skin_sh}" opacity=".75"/>'
        # складки на суставах
        for (q, a) in joints[:2]:
            dd = np.array([math.cos(a), math.sin(a)])
            nn = np.array([-dd[1], dd[0]])
            c0 = q - dd * 3
            inner += line_fn([_P(tf(*(c0 + nn * wf * .32))), _P(tf(*(c0 - dd * 2))), _P(tf(*(c0 - nn * wf * .26)))], 1.5, skin_sh2,
                             seed=seed + 40 + i * 3, op=.8)
        if c > .55:          # согнутый палец: складка-подушечка у кончика
            q, a = joints[-1]
            dd = np.array([math.cos(a), math.sin(a)])
            nn = np.array([-dd[1], dd[0]])
            inner += line_fn([_P(tf(*(q - dd * 9 + nn * wf * .38))), _P(tf(*(q - dd * 13))), _P(tf(*(q - dd * 9 - nn * wf * .38)))], 1.8,
                             skin_sh2, seed=seed + 60 + i)
        elif nails:
            q, a = joints[-1]
            dd = np.array([math.cos(a), math.sin(a)])
            nc = tf(*(q - dd * 6))
            ang = math.degrees(math.atan2(*(tf(*(q + dd)) - tf(*q))[::-1]))
            inner += f'<path d="{_fill(ellipse_pts(nc[0], nc[1], 6.2 * k, wf * .3 * k, 10, rot=ang))}" fill="{nail}"/>'
        o.append(shape_fn(outline, skin, inner, w=3.0, seed=seed + 1 + i))
    # ладонь: заливка поверх корней, тушь — по бокам
    pp = [_P(tf(*q)) for q in PALM]
    shade = [_P(tf(*q)) for q in [(-6, 14), (86, 10), (86, 44), (-6, 44)]]
    o.append(shape_fn(pp, skin, f'<path d="{_fill(shade)}" fill="{skin_sh}" opacity=".8"/>', w=3.4, seed=seed + 9, ink=False))
    o.append(line_fn(pp[:K0 + 1], 3.4, seed=seed + 11, taper=.3, wmin=.5))
    o.append(line_fn(pp[K1:], 3.4, seed=seed + 12, taper=.3, wmin=.5))
    # тыльные «лучики» сухожилий
    for j, y in enumerate((-16, 2, 18)):
        o.append(line_fn([_P(tf(22, y * .7)), _P(tf(54, y))], 1.4, skin_sh2, seed=seed + 20 + j, op=.55))
    if show_thumb:
        a = -0.95 + 0.75 * thumb
        base = np.array([16.0, -30.0])
        p1 = base + np.array([math.cos(a), math.sin(a)]) * 34
        a2 = a + .25 + .3 * thumb
        p2 = p1 + np.array([math.cos(a2), math.sin(a2)]) * 30
        a3 = a2 + .2
        p3 = p2 + np.array([math.cos(a3), math.sin(a3)]) * 20
        T = [_P(tf(*q)) for q in (base + np.array([-6, 8]), base, p1, p2, p3)]
        th = band(T, 27 * k, 19 * k, step=2.5, cap=True)
        inner = f'<path d="{_fill(band(T[1:4], 12 * k, 8 * k, step=3, cap=False))}" fill="{skin_sh}" opacity=".5"/>'
        inner += line_fn([_P(tf(*(p1 + np.array([-4, -9])))), _P(tf(*(p1 + np.array([-1, 0])))), _P(tf(*(p1 + np.array([-4, 9]))))], 1.5,
                         skin_sh2, seed=seed + 30, op=.8)
        if nails:
            dd = (p3 - p2) / np.linalg.norm(p3 - p2)
            nc = tf(*(p3 - dd * 4))
            ang = math.degrees(math.atan2(*(tf(*(p3 + dd)) - tf(*p3))[::-1]))
            inner += f'<path d="{_fill(ellipse_pts(nc[0], nc[1], 6.5 * k, 6 * k, 10, rot=ang))}" fill="{nail}"/>'
        o.append(shape_fn(th, skin, inner, w=3.0, seed=seed + 7))
    return "".join(o)


def grip(C, R, side, *, shape_fn, line_fn, skin, skin_sh, skin_sh2, k=1.0, seed=0, nails=True, h=None):
    """Пальцы, обхватившие предмет (чашку, телефон) спереди: C — центр захвата, R — полуширина предмета,
    side +1 — кисть справа от предмета (пальцы идут влево), −1 — слева. h — высота захвата (по умолчанию 4 пальца).
    Возвращает (задняя часть — ладонь за предметом, передняя — пальцы поверх)."""
    C = np.array(C, float)
    hh = (h if h is not None else 74) * k
    back = []
    palm = [(C[0] + side * (R - 6 * k), C[1] - hh * .55), (C[0] + side * (R + 40 * k), C[1] - hh * .62), (C[0] + side * (R + 58 * k), C[1]),
            (C[0] + side * (R + 44 * k), C[1] + hh * .6), (C[0] + side * (R - 6 * k), C[1] + hh * .55)]
    back.append(shape_fn(palm, skin, f'<path d="{_fill([(p[0], p[1] + hh * .3) for p in palm])}" fill="{skin_sh}" opacity=".7"/>', w=3.4,
                         seed=seed))
    front = []
    ys = np.linspace(-hh * .36, hh * .36, 4)
    lens = [.78, .86, .8, .62]
    for i in (3, 2, 1, 0):
        y = C[1] + ys[i]
        x0 = C[0] + side * (R + 22 * k)
        x1 = C[0] + side * (R - R * 2 * lens[i] * .55)
        pts = [(x0, y + 2 * k), (C[0] + side * R * .95, y - 1 * k), ((x0 + x1) / 2 - side * 6 * k, y + 1.5 * k), (x1, y + 5 * k)]
        wf = (18.5 if i < 3 else 16) * k
        outline = band(pts, wf, wf * .84, step=2.5, cap=True)
        inner = f'<path d="{_fill([(p[0], p[1] + wf * .28) for p in band(pts[1:], wf * .4, wf * .3, step=3, cap=False)])}" fill="{skin_sh}" opacity=".7"/>'
        for j in (1, 2):
            q = pts[j]
            inner += line_fn([(q[0], q[1] - wf * .32), (q[0] - side * 2 * k, q[1]), (q[0], q[1] + wf * .3)], 1.4, skin_sh2, seed=seed + 20 + i * 2 + j,
                             op=.75)
        if nails:
            q = pts[-1]
            inner += f'<path d="{_fill(ellipse_pts(q[0] + side * 5 * k, q[1], 5.5 * k, wf * .28, 8))}" fill="#f1cdbd"/>'
        front.append(shape_fn(outline, skin, inner, w=3.0, seed=seed + 1 + i))
    # большой палец сверху за краем
    tp = [(C[0] + side * (R + 30 * k), C[1] - hh * .5), (C[0] + side * (R + 8 * k), C[1] - hh * .66), (C[0] + side * (R - 18 * k), C[1] - hh * .7)]
    back.append(shape_fn(band(tp, 24 * k, 18 * k, step=2.5, cap=True), skin, "", w=3.0, seed=seed + 8))
    return "".join(back), "".join(front)


def _fill(pts):
    from ink import fill_d
    return fill_d(pts)
