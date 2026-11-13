"""Кот гордо шагает рядом с Димой (s16): тот же кот, что в рилсе 26 (cat.py: голова — ЛЕВОЕ от зрителя ухо загнуто,
зелёные глаза, по две оранжевые полоски на щеках; хвост завитком с огоньком), но не галоп, а шаг.

Шаг кошки — поочерёдный: задняя ближняя → передняя ближняя → задняя дальняя → передняя дальняя (фазы 0, .25, .5, .75),
опора 0.58 цикла, лапа на опоре стоит в мире (касание — под суставом в середине опоры), передние поднимаются высоко
(важная поступь). Нос и хвост задраны, на «гордо» (28.72) грудь колесом, глаза довольно прикрыты, огонёк вспыхивает.
Внутренние единицы — как у cat.py; мир = внутр. × CS, земля полосы — LANE_Y."""
import math

import numpy as np

import cat as C
import lib
import walk
from ink import ellipse_pts
from lib import blob, clamp, line, smooth

CS = 0.68
LANE_Y = 40.0
REL = 205.0                 # центр кота впереди таза Димы, мир
DUTY = 0.58
STRIDE = 236.0              # внутр. ед. за цикл
TC = STRIDE * CS / walk.V   # цикл, с
T_PROUD = 28.72
LEGS = {"hn": (0.00, "h", False), "fn": (0.25, "f", False), "hf": (0.50, "h", True), "ff": (0.75, "f", True)}


def X(t):
    return (walk.hip_at(t, bob=False)[0] + REL) / CS


def ph(t):
    return (t - 27.0) / TC


def body_at(t):
    p = ph(t) % 1.0
    th = math.radians(5.0)
    puff = smooth(T_PROUD - 0.05, T_PROUD + 0.18, t)
    y = -150 - 3.5 * math.cos(4 * math.pi * (p - 0.1)) - 6 * puff
    d = np.array([math.cos(th), -math.sin(th)])
    nd = np.array([math.sin(th), math.cos(th)])
    Cc = np.array([X(t), y])
    L = 150.0
    H = Cc - d * L / 2
    S = Cc + d * L / 2
    return dict(p=p, C=Cc, H=H, S=S, d=d, nd=nd, th=th, L=L, Jh=H + nd * 40 + d * 6, Jf=S + nd * 46 - d * 4, puff=puff)


def _t_of(phase):
    return 27.0 + phase * TC


def paw(leg, t):
    a, kind, _ = LEGS[leg]
    P = ph(t)
    c = math.floor(P - a)

    def stance(ci):
        t0 = _t_of(ci + a)
        t1 = _t_of(ci + a + DUTY)
        b = body_at((t0 + t1) / 2)
        J = b["Jh"] if kind == "h" else b["Jf"]
        return t0, t1, J[0] + (6 if kind == "f" else -2)

    t0, t1, x = stance(c)
    if t <= t1:
        return np.array([x, -C.ANK]), 0.0
    n0, n1, nx = stance(c + 1)
    u = clamp((t - t1) / (n0 - t1))
    ux = (1 - math.cos(math.pi * u)) / 2
    xx = x + (nx - x) * ux
    lift = 38 if kind == "f" else 26
    yy = -C.ANK - lift * math.sin(math.pi * u) ** 1.1
    if kind == "h":
        xx -= 14 * math.sin(math.pi * clamp(u * 1.6))
        rot = -0.18 * math.sin(math.pi * clamp(u * 1.2))
    else:
        rot = 0.32 * math.sin(math.pi * clamp(u * 1.2))
    return np.array([xx, yy]), rot


def tail_pts(b, t):
    """Хвост задран: от корня круто вверх, на конце завиток (по часовой), качается в такт шагу."""
    H, d, nd = b["H"], b["d"], b["nd"]
    up = -nd
    sway = math.sin(2 * math.pi * b["p"] * 2 - 0.6)
    base = H - d * 30 + up * 22
    ang = math.radians(32 + 4 * sway)
    pts = [base]
    for k, (s_, a_) in enumerate([(50, 0.0), (52, 0.42), (50, 0.85), (44, 1.25)]):
        a2 = ang + a_ + 0.05 * sway * k
        pts.append(pts[-1] + (-d * math.cos(a2) + up * math.sin(a2)) * s_)
    c0 = pts[-1]
    last = pts[-1] - pts[-2]
    a0 = math.atan2(last[1], last[0])
    r = 34.0
    cen = c0 + np.array([math.cos(a0 + math.pi / 2), math.sin(a0 + math.pi / 2)]) * r
    for k in range(1, 7):
        a = a0 - math.pi / 2 + k * 0.62
        pts.append(cen + np.array([math.cos(a), math.sin(a)]) * r * (1 - k * 0.06))
    return [(float(p[0]), float(p[1])) for p in pts]


def body_svg(b):
    """Тело кота (как cat.body_svg) с грудью колесом: передне-нижние точки выдвигаются вперёд-вверх на puff."""
    H, S, d, nd = b["H"], b["S"], b["d"], b["nd"]
    up = -nd
    k = b["puff"]
    mid = (H + S) / 2 + up * 6
    ch = d * 16 * k + up * 6 * k
    pts = [H - d * 70 + nd * 10, H - d * 62 + up * 44, H - d * 20 + up * 70, mid + up * 76, S + up * 70 + d * 10,
           S + up * 56 + d * 60 + ch * .6, S + d * 88 + nd * 12 + ch, S + d * 58 + nd * 62 + ch * .8, S + nd * 70 - d * 10, mid + nd * 66,
           H + nd * 64 + d * 10, H + nd * 50 - d * 52]
    inner = blob([tuple(H + nd * 70 - d * 80), tuple(S + nd * 80 + d * 90), tuple(S + nd * 20 + d * 90), tuple(mid + nd * 18),
                  tuple(H + nd * 10 - d * 80)], C.CAT_SH, .85)
    inner += blob([tuple(S + up * 70 - d * 30), tuple(S + up * 80 + d * 30), tuple(S + up * 40 + d * 40), tuple(mid + up * 52)], C.CAT_FUR, .55)
    # светлая шерсть груди (грудка колесом)
    inner += blob([tuple(S + d * 60 + up * 30 + ch), tuple(S + d * 92 + nd * 10 + ch), tuple(S + d * 56 + nd * 56 + ch), tuple(S + d * 34 + nd * 10)],
                  C.CAT_FUR, .45 + .25 * k)
    for i, (u, v) in enumerate([(-.2, .5), (.15, .55), (.45, .4), (.0, -.2), (.6, -.1)]):
        p = mid + d * b["L"] * u * .7 + up * 40 * v
        inner += line([tuple(p), tuple(p + d * -10 + nd * 12)], 2.2, C.CAT_EDGE, seed=624 + i, op=.8)
    for i in range(3):
        p = S + d * (70 + 6 * i) + nd * (10 + 14 * i) + ch
        inner += line([tuple(p), tuple(p - d * 10 + nd * 6)], 2.2, C.CAT_EDGE, seed=640 + i, op=.8)
    return lib.shape(pts, C.CAT, inner, w=5, seed=620)


def tail_svg(tp):
    S = np.array(tp)
    pts = lib.band(tp, 50, 24, step=3, cap=True)
    inner = blob(lib.band(tp[:5], 22, 12, step=5), C.CAT_SH, .7)
    inner += line(tp[1:8], 2.4, C.CAT_EDGE, seed=637, op=.7)
    return lib.shape(pts, C.CAT, inner, w=4.8, seed=636), S[-1], S[-1] - S[-2]


def glow_flame(tip, k, t):
    g = lib.rad_grad([(0, "#ffe9a0", .7), (.4, "#ffb347", .3), (1, "#ff9a3a", 0)], tip[0], tip[1] - 40 * k, 120 * k)
    return f'<circle cx="{tip[0]:.1f}" cy="{tip[1] - 40 * k:.1f}" r="{120 * k:.1f}" fill="url(#{g})"/>'


def sparks(tip, t, k):
    o = []
    for j in range(14):
        rs = np.random.RandomState(500 + j)
        life = rs.uniform(.35, .6)
        t0 = rs.uniform(0, life)
        age = (t - T_PROUD + t0) % life
        if t < T_PROUD - 0.05:
            continue
        u = age / life
        p = (tip[0] + rs.uniform(-20, 20) - 60 * u * rs.uniform(.3, 1.2), tip[1] - 50 * k - 140 * u * rs.uniform(.6, 1.1))
        r = rs.uniform(5, 9) * (1 - u)
        if r < .8:
            continue
        o.append(blob(ellipse_pts(p[0], p[1], r, r, 8), "#ffb347" if u > .4 else "#ffe27a"))
    return "".join(o)


def draw(t):
    b = body_at(t)
    o = []
    for k in ("hf", "ff"):
        A, rot = paw(k, t)
        J = b["Jh"] if k[0] == "h" else b["Jf"]
        o.append(C.leg_svg(J, A, rot, k[0], True, 700 + (0 if k[0] == "h" else 20)))
    tp = tail_pts(b, t)
    to, tip, tdir = tail_svg(tp)
    o.append(to)
    o.append(body_svg(b))
    A, rot = paw("hn", t)
    o.append(C.leg_svg(b["Jh"], A, rot, "h", False, 740))
    o.append(C.haunch(b))
    A, rot = paw("fn", t)
    o.append(C.leg_svg(b["Jf"], A, rot, "f", False, 760))
    # голова: нос задран
    hc = b["S"] + b["d"] * 64 + (-b["nd"]) * 128 + b["d"] * 10 * b["puff"]
    hc = hc + np.array([0, 3 * math.sin(2 * math.pi * b["p"] * 2 - 1.0)])
    hrot = -10 - 6 * b["puff"] + 1.5 * math.sin(2 * math.pi * b["p"] * 2)
    # глаза: довольно прикрыты; на «гордо» закрыты дугами, потом снова прищур
    shut = smooth(T_PROUD, T_PROUD + 0.08, t) * (1 - smooth(29.30, 29.42, t))
    blink = 0.38 + 0.62 * shut
    if shut > 0.5:
        blink = 1.0
    o.append(f'<g transform="translate({hc[0]:.2f} {hc[1]:.2f}) rotate({hrot:.2f})">{C.head((0.6, -0.4), blink, t)}</g>')
    fk = 1.1 + 0.55 * b["puff"] + 0.08 * math.sin(t * 11)
    fk *= 1 + 0.25 * math.exp(-6 * max(0, t - T_PROUD)) * smooth(T_PROUD - .03, T_PROUD + .05, t)
    o.append(glow_flame(tip, fk, t) if b["puff"] > 0.02 else "")
    o.append(C.flame(tuple(tip), tdir, t, fk))
    o.append(sparks(tip, t, fk))
    return f'<g transform="translate(0 {LANE_Y}) scale({CS})">{"".join(o)}</g>', b
