"""Кот галопом для сцены run: тот же кот, что в 24–25 (голова, уши — левое от зрителя загнуто, зелёные глаза, по две
оранжевые полоски на щеках, хвост завитком с огоньком), тело в профиль вправо.

Галоп (как у кошки): задние лапы ставятся почти вместе (0.00 / 0.07 цикла), спина собрана → толчок, вытянутый полёт
→ передние (0.48 / 0.55), спина собирается, задние выносятся под живот → собранный полёт. Длина спины, наклон и
высота корпуса — от фазы. Лапа на опоре стоит в мире (точка касания = под суставом в середине опоры), между
опорами — дуга маха. Скорость кота: догоняет Диму сзади и сбрасывает до его скорости; частота шагов растёт со
скоростью, доля опоры падает — лапы не тянутся длиннее ноги.
Рисунок — во «внутренних» единицах (голова ~186, как у кота 24), в мир — масштаб CS, земля полосы — LANE_Y."""
import math

import numpy as np

import lib
from dima import ik2
from ink import ellipse_pts, fill_d, fur, ink_closed
from lib import INK, blob, clamp, line, shape, smooth

CAT, CAT_SH, CAT_FUR, CAT_EDGE = "#3a3646", "#211e29", "#56506a", "#6c6688"
FAR_K = (0.78, 0.78, 0.84)
CS = 0.62
LANE_Y = 36.0
T_IN = 31.44
T_SETTLE = 32.12
REL_END = 255.0           # центр кота относительно таза Димы, мир (в конце)
VR = 1250.0               # скорость догона, мир/с

SEG_F = (64.0, 60.0)      # передняя лапа: предплечье, кисть
SEG_H = (68.0, 64.0)      # задняя: голень, плюсна
ANK = 13.0                # высота «щиколотки» над землёй на опоре
LEGS = {  # фаза касания, сустав (f — передний), ближняя?
    "hf": (0.00, "h", False), "hn": (0.07, "h", True), "ff": (0.48, "f", False), "fn": (0.55, "f", True)}

_grid = {}


def _rel_v(t):
    if t < T_SETTLE - 0.46:
        return VR
    u = clamp((t - (T_SETTLE - 0.46)) / 0.46)
    return VR * (1 - u * u * (3 - 2 * u))


def _build(dima_v):
    key = round(dima_v, 3)
    if key in _grid:
        return _grid[key]
    ts = np.arange(T_IN - 1.2, 33.2, 1 / 1200)
    vr = np.array([_rel_v(t) for t in ts])
    # rel(t): интеграл, привязан к REL_END в T_SETTLE
    rel = np.concatenate([[0], np.cumsum((vr[1:] + vr[:-1]) / 2 * np.diff(ts))])
    rel += REL_END - np.interp(T_SETTLE, ts, rel)
    v = dima_v + vr
    Tg = np.clip(0.29 - (v - 900) * 0.00008, 0.20, 0.29)
    ph = np.concatenate([[0], np.cumsum((1 / Tg[1:] + 1 / Tg[:-1]) / 2 * np.diff(ts))])
    ph += 0.62 - np.interp(T_IN, ts, ph)
    duty = np.clip(0.24 * np.sqrt(900 / v), 0.15, 0.24)
    g = dict(ts=ts, rel=rel, v=v, ph=ph, duty=duty)
    _grid[key] = g
    return g


def _at(g, k, t):
    return float(np.interp(t, g["ts"], g[k]))


def _t_of_phase(g, p):
    return float(np.interp(p, g["ph"], g["ts"]))


def body_at(g, t, hipx_fn):
    """Корпус кота в мире: центр, длина спины, наклон (рад, + нос вверх), суставы."""
    p = _at(g, "ph", t) % 1.0
    X = hipx_fn(t) + _at(g, "rel", t)
    L = 150 + 22 * math.cos(2 * math.pi * (p - 0.40))
    th = math.radians(7.0) * math.cos(2 * math.pi * (p - 0.15))
    y = -152 - 9 * math.cos(4 * math.pi * (p - 0.40))
    d = np.array([math.cos(th), -math.sin(th)])
    nd = np.array([math.sin(th), math.cos(th)])
    C = np.array([X / CS, y])                       # внутренние единицы (x — мир/CS)
    H = C - d * L / 2
    S = C + d * L / 2
    return dict(p=p, C=C, H=H, S=S, d=d, nd=nd, th=th, L=L, Jh=H + nd * 40 + d * 6, Jf=S + nd * 46 - d * 4)


def _joint(g, t, kind, hipx_fn):
    b = body_at(g, t, hipx_fn)
    return b["Jh"] if kind == "h" else b["Jf"]


def paw(g, leg, t, hipx_fn):
    """Лодыжка лапы (внутр. ед.) и поворот стопы; на опоре — стоит в мире."""
    a, kind, _ = LEGS[leg]
    P = _at(g, "ph", t)
    c = math.floor(P - a)
    duty = lambda tc: float(np.interp(tc, g["ts"], g["duty"]))  # noqa: E731

    def stance(ci):
        t0 = _t_of_phase(g, ci + a)
        t1 = _t_of_phase(g, ci + a + duty(t0))
        tm = (t0 + t1) / 2
        x = _joint(g, tm, kind, hipx_fn)[0] + (8 if kind == "f" else -4)
        return t0, t1, x

    t0, t1, x = stance(c)
    if t <= t1:
        return np.array([x, -ANK]), 0.0, 1.0
    n0, n1, nx = stance(c + 1)
    u = clamp((t - t1) / (n0 - t1))
    ux = (1 - math.cos(math.pi * u ** 1.2)) / 2
    xx = x + (nx - x) * ux
    lift = 44 if kind == "f" else 36
    yy = -ANK - lift * math.sin(math.pi * u) ** 1.2
    if kind == "h":            # задняя: сначала назад-вверх (толчок), потом подтягивается под живот
        xx -= 26 * math.sin(math.pi * clamp(u * 1.6))
        rot = -0.45 * math.sin(math.pi * clamp(u * 1.25))
    else:                      # передняя: кисть подгибается назад, потом выбрасывается вперёд
        xx += 0
        rot = 0.6 * math.sin(math.pi * clamp(u * 1.4)) - 0.2 * smooth(.7, 1, u) * (1 - smooth(.95, 1, u))
    return np.array([xx, yy]), rot, 0.0


def tail_pts(b, t, sway):
    """Средняя линия хвоста от корня (у таза) назад-вверх и завиток на конце (вид сбоку)."""
    H, d, nd = b["H"], b["d"], b["nd"]
    up = -nd
    base = H - d * 30 + up * 20
    ang = math.radians(4 + 10 * sway)
    pts = [base]
    # тело хвоста: дуга назад и вверх
    for k, (s_, a_) in enumerate([(54, 0.0), (58, 0.35), (58, 0.75), (52, 1.2)]):
        a2 = ang + a_ + 0.12 * sway * k * .5
        dirv = -d * math.cos(a2) + up * math.sin(a2)
        pts.append(pts[-1] + dirv * s_)
    # завиток (по часовой, как у эталона: закрученный конец, огонёк сверху)
    c0 = pts[-1]
    last = pts[-1] - pts[-2]
    a0 = math.atan2(last[1], last[0])
    r = 40.0
    cen = c0 + np.array([math.cos(a0 + math.pi / 2), math.sin(a0 + math.pi / 2)]) * r
    for k in range(1, 7):
        a = a0 - math.pi / 2 + k * 0.62
        rr = r * (1 - k * 0.06)
        pts.append(cen + np.array([math.cos(a), math.sin(a)]) * rr)
    return [(float(p[0]), float(p[1])) for p in pts]


def flame(tip, tdir, t, k=1.0):
    """Огонёк: язычки колышутся (форма от времени)."""
    bx, by = tip
    w1 = 4 * math.sin(t * 23) + 3 * math.sin(t * 37 + 1)
    w2 = 5 * math.sin(t * 29 + 2)
    P = [(-20, 4), (-24, -16), (-15, -36 + w2 * .3), (-13 + w1 * .4, -56), (-4, -45), (2 + w1, -80 + w2, 1), (11, -52), (20 + w2 * .6, -63 + w1 * .5, 1),
         (24, -36), (22, -11), (15, 4), (0, 9)]
    lean = math.radians(-14)            # пламя сдувает назад на бегу
    c, s = math.cos(lean), math.sin(lean)

    def tf(q):
        x, y = q[0] * k, q[1] * k
        return (bx + x * c - y * s, by + x * s + y * c) + ((1,) if len(q) > 2 else ())
    o = shape([tf(q) for q in P], "#ff8a2a", blob([tf((q[0] * .7, q[1] * .7 + 2)) + q[2:] for q in P], "#ffbe55"), w=3.4, seed=233,
              ink_color="#7a2a10", var=.2)
    o += blob([tf(q) for q in [(-7, 2), (-5, -19), (2 + w1 * .3, -37), (7, -18), (5, 2)]], "#fff2c0")
    return o


def head(look, blink, t):
    """Голова кота 24 в своих координатах (центр 836, 1068) → сдвиг к началу; черты чуть вправо (3/4 к бегу)."""
    s = []
    FX = 12   # сдвиг черт морды вправо
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884, 990), (940, 1050), (930, 1150), (866, 1150), (902, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    inner += blob([(800, 1106), (836, 1098), (872, 1106), (864, 1142), (808, 1142)], CAT_FUR, .45)
    for i, st in enumerate([[(800, 1004), (806, 1016)], [(836, 996), (838, 1010)], [(870, 1002), (866, 1014)]]):
        inner += line(st, 2, CAT_EDGE, seed=258 + i, op=.8)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250))
    s.append(ears())
    CXH = 836 + FX
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CXH + sx * 76 - (6 if sx > 0 else 0)
            s.append(line([(x0, 1100 + dy), (x0 + sx * 28, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    # глаза
    lx, ly = look
    for nm, ex, sd in [("L", CXH - 44, 255), ("R", CXH + 42, 256)]:
        rx = 34 if nm == "L" else 32
        ep = ellipse_pts(ex, 1072, rx, 38, 14)
        if blink > 0.98:
            s.append(line([(ex - 32, 1072), (ex - 12, 1082), (ex + 12, 1082), (ex + 32, 1072)], 5.6, INK, seed=sd + 40, taper=.5, wmin=.3))
            continue
        cid = lib.clip_of(ep)
        o = [f'<g><path d="{fill_d(ep)}" fill="#a9d84a"/><g clip-path="url(#{cid})">']
        o.append(blob(ellipse_pts(ex, 1046, 36, 20, 10), "#6f9a2e", .95))
        o.append(blob(ellipse_pts(ex, 1102, 26, 11, 10), "#d4f27a", .75))
        o.append(blob(ellipse_pts(ex - 18, 1080, 10, 20, 8), "#c8ee6a", .5))
        px, py = ex + lx * 12, 1074 + ly * 10
        o.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="12" ry="24" fill="#0b0a10"/>')
        o.append(f'<circle cx="{px - 7:.1f}" cy="{py - 15:.1f}" r="6.5" fill="#f4f8ff"/>')
        if blink > 0:
            ly2 = 1072 - 40 + 80 * blink
            o.append(f'<rect x="{ex - 40}" y="{1072 - 60}" width="80" height="{ly2 - 1012:.1f}" fill="{CAT}"/>')
            o.append(line([(ex - 36, ly2 - 4), (ex, ly2 + 4), (ex + 36, ly2 - 4)], 5, INK, seed=sd + 30))
        o.append(f'</g><path d="{ink_closed(ep, 4.4, seed=sd + 3)}" fill="{INK}"/></g>')
        s.append("".join(o))
    s.append(shape([(826 + FX, 1108), (846 + FX, 1108), (836 + FX, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836 + FX, 1119), (836 + FX, 1124)], 2.4, seed=263))
    # улыбка, ротик приоткрыт (бежит, радуется)
    s.append(shape([(824 + FX, 1124), (836 + FX, 1128), (848 + FX, 1124), (846 + FX, 1136), (836 + FX, 1142), (826 + FX, 1136)], "#7a3340",
                   blob([(828 + FX, 1134), (844 + FX, 1134), (840 + FX, 1142), (832 + FX, 1142)], "#e48a92"), w=3.0, seed=265))
    s.append(line([(816 + FX, 1120), (826 + FX, 1127), (836 + FX, 1124)], 3, seed=264))
    s.append(line([(836 + FX, 1124), (846 + FX, 1127), (856 + FX, 1120)], 3, seed=266))
    # усы
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CXH + sx * 58
            s.append(line([(x0, 1128 + dy * .8), (x0 + sx * 50, 1126 + dy + dl * .5 + 4 * math.sin(t * 9 + k)),
                           (x0 + sx * 96, 1124 + dy * 1.2 + dl + 6 * math.sin(t * 9 + k))], 1.4, "#cfcbe0", seed=270 + k + sx, op=.9))
    return f'<g transform="translate(-836 -1068)">{"".join(s)}</g>'


def ears():
    s = []
    re_out = [(864, 1004), (902, 922, 1), (932, 1016)]
    re_fill = re_out + [(934, 1046), (866, 1046)]
    s.append(blob(re_fill, CAT))
    c = lib.clip_of(re_fill)
    s.append(f'<g clip-path="url(#{c})">' + blob([(880, 1004), (902, 950), (918, 1008), (900, 1010)], "#9b6150") +
             blob([(904, 924), (940, 1000), (936, 1016), (918, 1014)], CAT_SH, .7) +
             line([(888, 1004), (898, 972)], 2, "#d79a84", seed=252, op=.8) + "</g>")
    s.append(line(re_out, 5, seed=251, taper=.25, wmin=.3))
    le_out = [(752, 1014), (744, 986), (728, 994, 1), (728, 966), (746, 948), (772, 940), (796, 948), (808, 968), (814, 1006)]
    le_fill = le_out + [(816, 1046), (752, 1046)]
    s.append(blob(le_fill, CAT))
    c = lib.clip_of(le_fill)
    s.append(f'<g clip-path="url(#{c})">' + blob([(762, 1002), (770, 980), (804, 996), (790, 1004)], "#9b6150") +
             blob([(728, 940), (812, 940), (806, 972), (770, 974), (744, 984), (726, 996)], CAT_FUR, .65) +
             line([(770, 998), (776, 984)], 2, "#d79a84", seed=256, op=.8) + "</g>")
    s.append(line([(740, 980), (770, 972), (800, 970)], 2.4, seed=255, op=.85))
    s.append(line(le_out, 5, seed=253, taper=.25, wmin=.3))
    return "".join(s)


def far_c(h, far):
    return lib.mul(h, FAR_K) if far else h


def leg_svg(J, A, rot, kind, far, seed):
    """Лапа: сустав J → колено/скакательный (ИК) → лодыжка A → стопа-подушка."""
    L1, L2 = SEG_F if kind == "f" else SEG_H
    side = 1 if kind == "f" else -1        # передняя: запястье вперёд; задняя: скакательный сустав назад
    K, E = ik2(J, A, L1, L2, side)
    col, sh = far_c(CAT, far), far_c(CAT_SH, far)
    o = []
    w0, w1 = (48, 30) if kind == "f" else (52, 30)
    pts = lib.band([tuple(E), tuple(K), tuple(J - (K - J) * .12)], w1, w0, step=4, cap=True)
    dd = E - K
    dd = dd / (np.linalg.norm(dd) + 1e-9)
    inner = blob(lib.band([tuple(J + (K - J) * .1), tuple(K), tuple(E)], w0 * .55, w1 * .5, step=5), sh, .6)
    o.append(shape(pts, col, inner, w=4.6, seed=seed))
    # стопа: вдоль земли на опоре, в махе — по голени + поворот
    toe = np.array([1.0, 0.0])
    if rot != 0.0:
        base = np.array([-dd[1], dd[0]]) * -1
        base = np.array([dd[1], -dd[0]]) if kind == "f" else np.array([dd[1], -dd[0]])
        c, s_ = math.cos(rot), math.sin(rot)
        toe = np.array([base[0] * c - base[1] * s_, base[0] * s_ + base[1] * c])
        toe = toe / (np.linalg.norm(toe) + 1e-9)
    nrm = np.array([-toe[1], toe[0]])
    pc = E + toe * 12 + nrm * 2
    ang = math.degrees(math.atan2(toe[1], toe[0]))
    pp = ellipse_pts(pc[0], pc[1], 23, 14, 12, rot=ang)
    o.append(shape(pp, col, blob(ellipse_pts(pc[0] + nrm[0] * 6, pc[1] + nrm[1] * 6, 22, 8, 10, rot=ang), sh, .6), w=4.4, seed=seed + 5))
    for k in (-8, 5):
        a_ = pc + toe * (14 + k * .2) + nrm * (-6)
        b_ = pc + toe * (18 + k * .2) + nrm * 6
        o.append(line([tuple(a_ + toe * k), tuple(b_ + toe * k)], 2.2, INK, seed=seed + 7 + k))
    if not far and rot != 0.0:
        # подушечки видны у лапы, поднятой назад
        o.append(blob(ellipse_pts(pc[0] - nrm[0] * 9, pc[1] - nrm[1] * 9, 9, 5, 8, rot=ang), "#e8823a", 1.0))
    return "".join(o)


def body_svg(b):
    """Тело одной фигурой вокруг спины: спина выше, живот ниже; грудь вперёд, ляжка у таза."""
    H, S, d, nd = b["H"], b["S"], b["d"], b["nd"]
    up = -nd
    L = b["L"]
    arch = 16 * (1 - (L - 128) / 44)                    # собранная спина выгибается
    mid = (H + S) / 2 + up * arch
    pts = [
        H - d * 70 + nd * 10, H - d * 62 + up * 44, H - d * 20 + up * 72, mid + up * 80, S + up * 72 + d * 10,
        S + up * 56 + d * 56, S + d * 82 + nd * 10, S + d * 52 + nd * 62, S + nd * 70 - d * 10, mid + nd * 70,
        H + nd * 66 + d * 10, H + nd * 50 - d * 52,
    ]
    bp = pts
    inner = blob([tuple(H + nd * 70 - d * 80), tuple(S + nd * 80 + d * 90), tuple(S + nd * 20 + d * 90), tuple(mid + nd * 18),
                   tuple(H + nd * 10 - d * 80)], CAT_SH, .85)
    inner += blob([tuple(S + up * 70 - d * 30), tuple(S + up * 80 + d * 30), tuple(S + up * 40 + d * 40), tuple(mid + up * 52)], CAT_FUR, .55)
    inner += line([tuple(H + up * 20 - d * 34), tuple(H + up * 48 + d * 20), tuple(H + nd * 6 + d * 54)], 3.4, CAT_SH, seed=622, op=.9)
    for i, (u, v) in enumerate([(-.2, .5), (.15, .55), (.45, .4), (.0, -.2), (.6, -.1)]):
        p = mid + d * L * u * .7 + up * 40 * v
        inner += line([tuple(p), tuple(p + d * -10 + nd * 12)], 2.2, CAT_EDGE, seed=624 + i, op=.8)
    return shape(bp, CAT, inner, w=5, seed=620)


def haunch(b, far=False):
    """Ляжка задней ближней лапы: заливка поверх тела, тушь только по переднему-нижнему краю (без шва с телом)."""
    J, d, nd = b["Jh"], b["d"], b["nd"]
    c = J - nd * 22 - d * 4
    pts = ellipse_pts(c[0], c[1], 46, 50, 16, rot=-math.degrees(b["th"]) + 12)
    o = blob(pts, CAT)
    cid = lib.clip_of(pts)
    o += f'<g clip-path="url(#{cid})">' + blob(ellipse_pts(c[0] + 14, c[1] + 22, 44, 38, 12), CAT_SH, .7) + "</g>"
    arc = [tuple(c + np.array([math.cos(a), math.sin(a)]) * np.array([46, 50])) for a in np.linspace(-1.2, 1.9, 9)]
    o += line(arc, 4.0, INK, seed=631, taper=.6, wmin=.15)
    return o


def state(t, hipx, dima_v):
    """Всё нужное для кадра: хранит функцию x таза Димы (камера и кот от неё)."""
    import scene
    g = _build(dima_v)
    fn = lambda tt: scene.hip_at(tt, bob=False)[0]  # noqa: E731
    b = body_at(g, t, fn)
    paws = {k: paw(g, k, t, fn) for k in LEGS}
    sway = math.sin(2 * math.pi * b["p"] - 0.6)
    tp = tail_pts(b, t, sway)
    return dict(g=g, b=b, paws=paws, tail=tp, fn=fn, sway=sway)


def tail_svg(tp):
    S = np.array(tp)
    pts = lib.band(tp, 44, 20, step=3, cap=True)
    inner = blob(lib.band(tp[:5], 20, 10, step=5), CAT_SH, .7)
    o = shape(pts, CAT, inner, w=4.8, seed=636)
    tip = S[-1]
    return o, tip, S[-1] - S[-2]


def flame_tip(cs):
    S = np.array(cs["tail"])
    return S[-1]


def draw(cs, t):
    b = cs["b"]
    o = []
    # дальние лапы
    for k in ("hf", "ff"):
        A, rot, _ = cs["paws"][k]
        J = b["Jh"] if k[0] == "h" else b["Jf"]
        o.append(leg_svg(J, A, rot, k[0], True, 700 + (0 if k[0] == "h" else 20)))
    to, tip, tdir = tail_svg(cs["tail"])
    o.append(to)
    o.append(body_svg(b))
    # ближние лапы
    A, rot, _ = cs["paws"]["hn"]
    o.append(leg_svg(b["Jh"], A, rot, "h", False, 740))
    o.append(haunch(b))
    A, rot, _ = cs["paws"]["fn"]
    o.append(leg_svg(b["Jf"], A, rot, "f", False, 760))
    # голова: впереди-сверху груди, качается с запаздыванием
    hc = b["S"] + b["d"] * 58 + (-b["nd"]) * 120
    hc = hc + np.array([0, 6 * math.sin(2 * math.pi * b["p"] - 1.2)])
    hrot = -math.degrees(b["th"]) * 0.5
    look_k = smooth(31.75, 32.05, t)
    look = (0.7 - 1.3 * look_k, 0.1 - 0.9 * look_k)
    blink = 0.0
    tb = 32.42
    if abs(t - tb) < 0.06:
        blink = min(1.0, 1.6 * (1 - abs(t - tb) / 0.06))
    o.append(f'<g transform="translate({hc[0]:.2f} {hc[1]:.2f}) rotate({hrot:.2f}) scale(1.0)">{head(look, blink, t)}</g>')
    o.append(flame(tuple(tip), tdir, t, 1.15))
    return f'<g transform="translate(0 {LANE_Y}) scale({CS})">{"".join(o)}</g>'


def sparks(cs, t):
    """Искры от огонька: рождаются у кончика хвоста в мире и остаются позади, гаснут уменьшаясь."""
    g, fn = cs["g"], cs["fn"]
    o = []
    dt = 0.015
    j1 = math.floor((t - (T_IN - 0.4)) / dt)
    for j in range(max(0, j1 - 30), j1 + 1):
        ts = T_IN - 0.4 + j * dt
        age = t - ts
        rs = np.random.RandomState(4000 + j)
        life = rs.uniform(0.22, 0.4)
        if age < 0 or age > life:
            continue
        b = body_at(g, ts, fn)
        sway = math.sin(2 * math.pi * b["p"] - 0.6)
        tp = tail_pts(b, ts, sway)
        tip = np.array(tp[-1]) * CS + np.array([0, LANE_Y])
        tip = tip + np.array([rs.uniform(-6, 6), -16 + rs.uniform(-8, 8)])
        vx, vy = rs.uniform(-90, 40), rs.uniform(-200, -60)
        p = tip + np.array([vx * age, vy * age + 260 * age * age])
        u = age / life
        r = rs.uniform(7, 12) * (1 - u) ** 0.8
        if r < 0.6:
            continue
        if rs.uniform() < 0.5:
            a = rs.uniform(0, 1.5) + age * 9
            pts = []
            for k in range(8):
                rr = r * (2.2 if k % 2 == 0 else .55)
                pts.append((p[0] + rr * math.cos(a + k * math.pi / 4), p[1] + rr * math.sin(a + k * math.pi / 4), 1))
            o.append(blob(pts, "#ffd25a" if u < .5 else "#ff9a3a"))
            o.append(blob(ellipse_pts(p[0], p[1], r * .5, r * .5, 6), "#fff6d0"))
        else:
            o.append(blob(ellipse_pts(p[0], p[1], r, r, 8), "#ff9a3a"))
            o.append(blob(ellipse_pts(p[0], p[1], r * .55, r * .55, 6), "#fff0b0"))
    return "".join(o)
