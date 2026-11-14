"""Кот рилса 31 в позах: тот же кот, что cat.py (голова, уши — ЛЕВОЕ от зрителя загнуто, зелёные глаза, по две
оранжевые полоски на щеках, хвост завитком с огоньком), но тело собирается по позе:
up 0 — сидит (как cat.draw), 1 — стоит на задних лапах (тело вытянуто вверх, видны бёдра и задние ступни);
lift_l / lift_r — подъём задних ступней (шаг), paw_l / paw_r — точки передних лап во внутренних координатах,
happy — довольный прищур (глаза-дуги ∩), остальное как у cat.draw."""
import math

import numpy as np

import cat
import lib
from cat import CAT, CAT_SH, CAT_FUR, CAT_EDGE, CX, CBOT, TAIL_PIVOT
from ink import ellipse_pts, fill_d, fur
from lib import INK, blob, clip_of, line, shape, T
from parts import sausage

BODY_SIT = [(760, 1296), (744, 1240), (756, 1180), (790, 1142), (880, 1142), (916, 1180), (928, 1240), (912, 1296)]
BODY_UP = [(786, 1228), (772, 1148), (774, 1050), (800, 962), (872, 962), (898, 1050), (900, 1148), (886, 1228)]
NECK_RISE = 188
SH_RISE = 196


def lerp(a, b, u):
    return a + (b - a) * u


def ymap(y, up):
    """Растяжка тела по вертикали: сидя 1142..1296, стоя 1000..1258."""
    ys = 1228 - (1296 - y) * (266 / 154)
    return lerp(y, ys, up)


def body(up):
    pts = [(lerp(a[0], b[0], up), lerp(a[1], b[1], up)) for a, b in zip(BODY_SIT, BODY_UP)]
    bp = fur(pts, 7, 7, seed=22)
    M = lambda q: [(p[0], ymap(p[1], up)) for p in q]
    inner = blob(M([(860, 1140), (930, 1180), (930, 1300), (874, 1300), (888, 1220)]), CAT_SH, .9)
    inner += blob(M([(798, 1170), (836, 1160), (874, 1170), (864, 1244), (836, 1266), (808, 1244)]), CAT_FUR, .6)
    for i, st in enumerate([[(816, 1190), (826, 1208)], [(852, 1192), (846, 1212)], [(834, 1214), (836, 1236)], [(806, 1222), (814, 1238)],
                            [(864, 1226), (858, 1244)]]):
        inner += line(M(st), 2.2, CAT_EDGE, seed=240 + i, op=.85)
    return shape(bp, CAT, inner, w=5, seed=241)


def foot(sx, up, lift):
    px = CX + sx * lerp(70, 48, up)
    py = 1286 - lift * 24
    s = []
    foot = ellipse_pts(px, py, lerp(34, 30, up), lerp(26, 24, up), 12, rot=sx * lerp(12, 6, up))
    s.append(shape(foot, CAT, blob(T(ellipse_pts(px, py + 6, 26, 20, 10), sx * 4, 0), CAT_SH, .5), w=4.6, seed=242 + (sx > 0)))
    s.append(blob(ellipse_pts(px + sx * 3, py + 10, 13, 10, 10, rot=sx * 10), "#e8823a"))
    for k in range(3):
        ang = math.radians(-90 + (k - 1) * 42 + sx * 10)
        s.append(blob(ellipse_pts(px + sx * 3 + math.cos(ang) * 19, py + 10 + math.sin(ang) * 15, 5, 4.4, 8), "#e8823a"))
    return "".join(s), (px, py)


def thigh(sx, up, fp):
    """Бедро: от таза к ступне, коленом наружу (видно, когда тело поднято)."""
    hip = (CX + sx * 38, ymap(1236, up))
    knee = (CX + sx * 80, lerp(1262, 1196, up))
    pts = [hip, knee, (fp[0] - sx * 4, fp[1] - 14)]
    out = sausage(pts, 86, 52)
    inner = blob([(CX + sx * 60, 1150), (CX + sx * 110, 1150), (CX + sx * 110, 1320), (CX + sx * 60, 1320)], CAT_SH if sx > 0 else CAT_FUR, .55)
    return shape(fur(out, 5, 9, seed=300 + (sx > 0)), CAT, inner, w=4.6, seed=302 + (sx > 0))


def leg(S, P, w0=50, w1=42, press=0.0, seed=244, mitt=False):
    S = np.array(S, float)
    P = np.array(P, float)
    d = P - S
    L = np.linalg.norm(d) + 1e-9
    u = d / L
    nrm = np.array([-u[1], u[0]])
    bend = 10 * min(1.0, max(0.0, (L - 76) / 60))
    M = S + d * 0.5 + nrm * bend * (1 if d[0] < 0 else -1)
    mid = [tuple(S - u * 18), tuple(M), tuple(P)]
    out = sausage(mid, w0, w1 * (1 + 0.08 * press))
    o = [f'<path d="{fill_d(out)}" fill="{CAT}"/>']
    c = clip_of(out)
    o.append(f'<g clip-path="url(#{c})">' + blob([tuple(S + nrm * 4 - u * 30), tuple(P + nrm * 30 + u * 30), tuple(P - nrm * 2 + u * 30),
                                                    tuple(S - nrm * 6 - u * 30)], CAT_SH, .55) + "</g>")
    o.append(line(out[2:-2], 4.6, seed=seed, taper=.25, wmin=.25))
    if mitt:
        ang = math.degrees(math.atan2(u[1], u[0]))
        pw = ellipse_pts(P[0] + u[0] * 4, P[1] + u[1] * 4, w1 * 0.66, w1 * 0.62, 14, rot=ang)
        o.append(shape(pw, CAT, blob(T([(-10, 6), (24, 4), (24, 26), (-10, 26)], P[0], P[1], 1, ang), CAT_SH, .6), w=4.4, seed=seed + 9))
        P = P + u * 4
    tip = P + u * (w1 / 2 - 4)
    for k in (-1, 1):
        a = tip + nrm * k * 8
        o.append(line([tuple(a - u * 14), tuple(a)], 2.2, seed=seed + 2 + k))
    return "".join(o)


def happy_eyes():
    s = []
    for ex, sd in ((CX - 44, 255), (CX + 44, 256)):
        s.append(line([(ex - 32, 1086), (ex - 16, 1064), (ex, 1058), (ex + 16, 1064), (ex + 32, 1086)], 6.4, INK, seed=sd + 50, taper=.5,
                      wmin=.35))
    # румянец под глазами (непрозрачные мягкие пятнышки)
    for ex in (CX - 52, CX + 52):
        s.append(blob(ellipse_pts(ex, 1098, 16, 6, 10), "#7a4a5e"))
    return "".join(s)


def draw(x, y, s, t, up=0.0, look=(0, 0), blink=0.0, tilt=0.0, tail=0.0, flick=0.0, paw_l=None, paw_r=None, press=0.0,
         lift_l=0.0, lift_r=0.0, happy=0.0, breath=None, shadow=True, bob=0.0):
    st = cat.static_parts()
    br = (0.5 + 0.5 * math.sin(t * 2 * math.pi / 2.6)) if breath is None else breath
    o = []
    if shadow:
        o.append(blob(ellipse_pts(850, 1306, lerp(150, 120, up), 18, 16), "#1a0e05", .35, lib.blur(8)))
    g = [f'<g transform="translate(0 {bob:.2f})">']
    tw = f"translate(0 {-62 * up:.2f}) rotate({tail:.2f} {TAIL_PIVOT[0]} {TAIL_PIVOT[1]})"
    g.append(f'<g transform="{tw}">{st["tail"]}</g>')
    feet = []
    for sx, lf in ((-1, lift_l), (1, lift_r)):
        fs, fp = foot(sx, up, lf)
        if up > 0.04:
            g.append(thigh(sx, up, fp))
        feet.append(fs)
    sy = 1 + 0.012 * br
    g.append(f'<g transform="translate(0 {CBOT}) scale(1 {sy:.4f}) translate(0 {-CBOT})">{body(up)}</g>')
    g.extend(feet)
    shy = 1222 - SH_RISE * up
    pr = paw_r if paw_r is not None else (861, 1298)
    pl = paw_l if paw_l is not None else (811, 1298)
    g.append(leg((860, shy), pr, seed=250))
    g.append(leg((812, shy), pl, press=press, seed=244, mitt=paw_l is not None and up > 0.5))
    hy = -(sy - 1) * (CBOT - 1150) - NECK_RISE * up
    eyes = cat.eyes(look, blink) if happy < 0.5 else happy_eyes()
    hg = st["head"] + cat.ears(flick) + st["face"] + eyes + cat.whiskers(t)
    g.append(f'<g transform="translate(0 {hy:.2f}) rotate({tilt:.2f} 836 1150)">{hg}</g>')
    g.append(f'<g transform="{tw}">{cat.flame(t)}</g>')
    g.append("</g>")
    o.extend(g)
    return f'<g transform="translate({x - CX * s:.2f} {y - CBOT * s:.2f}) scale({s:.4f})">{"".join(o)}</g>'


def flame_world(x, y, s, tail=0.0, up=0.0, bob=0.0):
    fx, fy = cat.flame_world(x, y, s, tail)
    return fx, fy + (-62 * up + bob) * s
