"""Кот сидит (анфас) — тот же кот, что в рилсах 24–26 (room/chars_src/heroes24.py: cat_art, cat_ears, cat_eyes,
cat_flame, хвост одной фигурой с петлёй). Эталон look/hero.png: ЛЕВОЕ от зрителя ухо загнуто, зелёные глаза, по две
оранжевые полоски на щеках, закрученный хвост с огоньком, оранжевые подушечки лап.

Здесь кот живой: голова наклоняется и поворачивается (черты морды смещаются), взгляд, моргание, подёргивание
правого уха, «уши торчком», хвост качается вокруг корня, огонёк колышется формой, дыхание.
draw(x, y, k, st) — (x, y) — точка между задних лап на сиденье (мир), k — масштаб рисунка (рисунок 384 ед. в высоту).
"""
import math

import numpy as np

import lib
from ink import ellipse_pts, fill_d, fur, ink_closed, sample
from lib import INK, blob, line, shape

CAT, CAT_SH, CAT_FUR, CAT_EDGE = "#3a3646", "#211e29", "#56506a", "#6c6688"
CX, CBOT = 836, 1306
TAIL_C = [(904, 1272), (962, 1266), (1004, 1240), (1014, 1198), (994, 1166), (962, 1166), (944, 1192), (954, 1224), (986, 1236),
          (1010, 1214), (1014, 1168), (1006, 1120), (996, 1080)]
FLAME_BASE = (995, 1076)
TAIL_PIVOT = (912, 1272)
NECK = (836, 1150)


def ring(pts, w, seed):
    return f'<path d="{ink_closed(pts, w * lib.INK_K[0], seed=seed)}" fill="{INK}"/>'


def tail_art(curl=0.0):
    pts = [(p[0] + (p[0] - 960) * 0, p[1]) for p in TAIL_C]
    S = sample(pts, False, 3.0)
    n = len(S)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = 40 + (14 - 40) * np.linspace(0, 1, n) ** 1.2
    L, R = S + N * Wd[:, None] / 2, S - N * Wd[:, None] / 2
    tip = S[-1] + Tg[-1] * Wd[-1] * .45
    outline = [tuple(p) for p in L] + [tuple(tip)] + [tuple(p) for p in R[::-1]]
    sh = [(1000, 1100), (1060, 1100), (1060, 1280), (990, 1280)]
    out = [f'<path d="{fill_d(outline)}" fill="{CAT}"/>']
    c = lib.clip_of(outline)
    out.append(f'<g clip-path="url(#{c})">{blob(sh, CAT_SH, .8)}</g>')
    out.append(ring(outline, 4.8, 230))
    d_ = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    k0 = int(np.argmin(np.abs(S[:, 1] - 1236) + np.abs(S[:, 0] - 970) + (d_ < d_[-1] * .4) * 1e4))
    k1 = int(np.argmin(np.abs(S[:, 1] - 1172) + np.abs(S[:, 0] - 1014) + (d_ < d_[-1] * .5) * 1e4))
    seg = [tuple(p) for p in L[k0:k1]] + [tuple(p) for p in R[k0:k1][::-1]]
    out.append(f'<path d="{fill_d(seg)}" fill="{CAT}"/>')
    sc = lib.clip_of(seg)
    out.append(f'<g clip-path="url(#{sc})">{blob(sh, CAT_SH, .8)}</g>')
    for side, sd in ((L, 233), (R, 234)):
        pp = [tuple(p) for p in side[k0 - 2:k1 + 2:3]]
        out.append(line(pp, 4.8, seed=sd, taper=.1, wmin=.6, peak=.5))
    for i, k in enumerate(range(int(n * .1), int(n * .9), int(n * .12))):
        p = S[k] + N[k] * Wd[k] * .18
        q = p + Tg[k] * 12
        out.append(line([tuple(p), tuple(q)], 2, CAT_EDGE, seed=236 + i, op=.8))
    return "".join(out)


def flame(t, k=1.3, energy=1.0):
    bx, by = FLAME_BASE
    w1 = (4 * math.sin(t * 13) + 3 * math.sin(t * 21 + 1)) * energy
    w2 = (5 * math.sin(t * 17 + 2)) * energy
    P = [(-22, 4), (-26, -18), (-16 + w2 * .2, -40), (-14 + w1 * .4, -62 + w2 * .3), (-4, -50), (2 + w1, -86 + w2, 1), (12, -58),
         (22 + w2 * .6, -70 + w1 * .5, 1), (26, -40), (24, -12), (16, 4), (0, 10)]

    def tf(q, kk=1.0):
        return (bx + q[0] * k * kk, by + q[1] * k * kk + (1 - kk) * 4) + ((1,) if len(q) > 2 else ())
    o = shape([tf(q) for q in P], "#ff8a2a", blob([tf(q, .7) for q in P], "#ffbe55"), w=3.4, seed=233, ink_color="#7a2a10", var=.2)
    o += blob([(bx - 8 * k, by + 2), (bx - 6 * k, by - 22 * k), (bx + (2 + w1 * .3) * k, by - 42 * k), (bx + 8 * k, by - 20 * k), (bx + 6 * k, by + 2)],
              "#fff2c0")
    return o


def ears(ear_r=0.0, perk=0.0):
    """ear_r — поворот правого (стоячего) уха, градусы; perk 0..1 — «торчком»: оба уха выше, загнутое расправляется чуть-чуть."""
    s = []
    re_out = [(864, 1004), (902, 922 - 10 * perk, 1), (932, 1016)]
    re_fill = re_out + [(934, 1046), (866, 1046)]
    g = []
    g.append(blob(re_fill, CAT))
    c = lib.clip_of(re_fill)
    g.append(f'<g clip-path="url(#{c})">' + blob([(880, 1004), (902, 950), (918, 1008), (900, 1010)], "#9b6150") +
             blob([(904, 924), (940, 1000), (936, 1016), (918, 1014)], CAT_SH, .7) +
             line([(888, 1004), (898, 972)], 2, "#d79a84", seed=252, op=.8) + "</g>")
    g.append(line(re_out, 5, seed=251, taper=.25, wmin=.3))
    s.append(f'<g transform="rotate({ear_r:.2f} 898 1030)">{"".join(g)}</g>')
    lift = -8 * perk
    le_out = [(752, 1014), (744, 986 + lift), (728, 994 + lift * 1.4, 1), (728, 966 + lift), (746, 948 + lift), (772, 940 + lift), (796, 948 + lift),
              (808, 968 + lift * .5), (814, 1006)]
    le_fill = le_out + [(816, 1046), (752, 1046)]
    g = [blob(le_fill, CAT)]
    c = lib.clip_of(le_fill)
    g.append(f'<g clip-path="url(#{c})">' + blob([(762, 1002), (770, 980 + lift), (804, 996), (790, 1004)], "#9b6150") +
             blob([(728, 940 + lift), (812, 940 + lift), (806, 972 + lift), (770, 974 + lift), (744, 984 + lift), (726, 996 + lift)], CAT_FUR, .65) +
             line([(770, 998), (776, 984 + lift)], 2, "#d79a84", seed=256, op=.8) + "</g>")
    g.append(line([(740, 980 + lift), (770, 972 + lift), (800, 970 + lift)], 2.4, seed=255, op=.85))
    g.append(line(le_out, 5, seed=253, taper=.25, wmin=.3))
    s.append(f'<g transform="rotate({-ear_r * .3:.2f} 780 1030)">{"".join(g)}</g>')
    return "".join(s)


def eye(ex, ey, rx, ry, look, blink, sd, squash=1.0):
    rx = rx * squash
    ep = ellipse_pts(ex, ey, rx, ry, 14)
    if blink > 0.97:
        return line([(ex - rx * .94, ey - 2), (ex - rx * .35, ey + 9), (ex + rx * .35, ey + 9), (ex + rx * .94, ey - 2)], 5.6, INK, seed=sd + 40,
                    taper=.5, wmin=.3)
    cid = lib.clip_of(ep)
    o = [f'<g><path d="{fill_d(ep)}" fill="#a9d84a"/><g clip-path="url(#{cid})">']
    o.append(blob(ellipse_pts(ex, ey - 26, rx + 2, 20, 10), "#6f9a2e", .95))
    o.append(blob(ellipse_pts(ex, ey + 30, rx * .76, 11, 10), "#d4f27a", .75))
    o.append(blob(ellipse_pts(ex - rx * .52, ey + 8, 10 * squash, 20, 8), "#c8ee6a", .5))
    lx, ly = look
    px, py = ex + lx * 12 * squash, ey + 2 + ly * 10
    o.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{11.5 * squash:.1f}" ry="24" fill="#0b0a10"/>')
    o.append(f'<circle cx="{px - 8 * squash:.1f}" cy="{py - 16:.1f}" r="7" fill="#f4f8ff"/>')
    o.append(f'<circle cx="{px + 10 * squash:.1f}" cy="{py + 14:.1f}" r="3.2" fill="#ffd9a0"/>')
    if blink > 0.01:
        ly2 = ey - ry - 4 + (2 * ry + 8) * blink
        o.append(f'<rect x="{ex - rx - 6:.1f}" y="{ey - ry - 30:.1f}" width="{2 * rx + 12:.1f}" height="{ly2 - (ey - ry - 30):.1f}" fill="{CAT}"/>')
        o.append(line([(ex - rx * .95, ly2 - 4), (ex, ly2 + 5), (ex + rx * .95, ly2 - 4)], 5, INK, seed=sd + 30))
    o.append(f'</g>{ring(ep, 4.4, sd + 3)}</g>')
    return "".join(o)


def head(st, t):
    turn = st.get("turn", 0.0)          # −1 — смотрит влево, +1 — вправо (черты смещаются)
    look = st.get("look", (0.0, 0.0))
    blink = st.get("blink", 0.0)
    FX = 22 * turn
    s = []
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884 + FX * .5, 990), (940, 1050), (930, 1150), (866 + FX * .5, 1150), (902 + FX * .5, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    inner += blob([(800 + FX, 1106), (836 + FX, 1098), (872 + FX, 1106), (864 + FX, 1142), (808 + FX, 1142)], CAT_FUR, .45)
    for i, st_ in enumerate([[(800, 1004), (806, 1016)], [(836, 996), (838, 1010)], [(870, 1002), (866, 1014)]]):
        inner += line(st_, 2, CAT_EDGE, seed=258 + i, op=.8)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250))
    s.append(ears(st.get("ear", 0.0), st.get("perk", 0.0)))
    CXH = CX + FX
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76 + FX * (.5 if sx * turn > 0 else 1.0)
            ln = 30 * (1 - .4 * max(0, sx * turn))
            s.append(line([(x0, 1100 + dy), (x0 + sx * ln, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    for nm, ex, sd in [("L", CXH - 44 - 4 * turn, 255), ("R", CXH + 44 - 4 * turn, 256)]:
        sq = 1.0 - .22 * max(0.0, turn if nm == "R" else -turn)
        s.append(eye(ex, 1072, 34, 38, look, blink, sd, sq))
    s.append(shape([(826 + FX, 1108), (846 + FX, 1108), (836 + FX, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836 + FX, 1119), (836 + FX, 1124)], 2.4, seed=263))
    if st.get("smile", 0) > .5:
        s.append(line([(818 + FX, 1122), (828 + FX, 1134), (836 + FX, 1126), (844 + FX, 1134), (854 + FX, 1122)], 3.2, seed=265))
    else:
        s.append(line([(822 + FX, 1124), (829 + FX, 1131), (836 + FX, 1124), (843 + FX, 1131), (850 + FX, 1124)], 3, seed=264))
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CXH + sx * 58
            wv = 3 * math.sin(t * 2.3 + k + sx)
            s.append(line([(x0, 1128 + dy * .8), (x0 + sx * 50, 1126 + dy + dl * .5 + wv * .5), (x0 + sx * 96, 1124 + dy * 1.2 + dl + wv)], 1.4,
                          "#cfcbe0", seed=270 + k + sx, op=.9))
    return "".join(s)


def body():
    s = []
    bd = [(760, 1296), (744, 1240), (756, 1180), (790, 1142), (880, 1142), (916, 1180), (928, 1240), (912, 1296)]
    bp = fur(bd, 7, 7, seed=22)
    inner = blob([(860, 1140), (930, 1180), (930, 1300), (874, 1300), (888, 1220)], CAT_SH, .9)
    inner += blob([(798, 1170), (836, 1160), (874, 1170), (864, 1244), (836, 1266), (808, 1244)], CAT_FUR, .6)
    for i, st in enumerate([[(816, 1190), (826, 1208)], [(852, 1192), (846, 1212)], [(834, 1214), (836, 1236)], [(806, 1222), (814, 1238)],
                            [(864, 1226), (858, 1244)]]):
        inner += line(st, 2.2, CAT_EDGE, seed=240 + i, op=.85)
    s.append(shape(bp, CAT, inner, w=5, seed=241))
    for sx, sd in [(-1, 242), (1, 243)]:
        px = CX + sx * 70
        foot = ellipse_pts(px, 1286, 34, 26, 12, rot=sx * 12)
        s.append(shape(foot, CAT, blob(lib.T(ellipse_pts(px, 1292, 26, 20, 10), sx * 4, 0), CAT_SH, .5), w=4.6, seed=sd))
        s.append(blob(ellipse_pts(px + sx * 3, 1296, 13, 10, 10, rot=sx * 10), "#e8823a"))
        for k in range(3):
            ang = math.radians(-90 + (k - 1) * 42 + sx * 10)
            s.append(blob(ellipse_pts(px + sx * 3 + math.cos(ang) * 19, 1296 + math.sin(ang) * 15, 5, 4.4, 8), "#e8823a"))
    for sx, sd in [(-1, 244), (1, 245)]:
        fx = CX + sx * 25
        paw = [(fx - 20, 1306, 1), (fx - 19, 1252), (fx + 19, 1252), (fx + 20, 1306, 1)]
        s.append(shape(paw, CAT, blob([(fx + sx * 6, 1250), (fx + 20 * sx, 1250), (fx + 20 * sx, 1306), (fx + sx * 8, 1306)], CAT_SH, .7),
                       w=4.6, seed=sd))
        for k in (-7, 7):
            s.append(line([(fx + k, 1294), (fx + k, 1306)], 2.2, seed=sd + k))
    return "".join(s)


def draw(x, y, k, st, t):
    """st: tilt (град), turn, look, blink, ear, perk, tail (град), breath (0..1), smile, flame_e."""
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    tail_a = st.get("tail", 0.0)
    tilt = st.get("tilt", 0.0)
    o = []
    o.append(f'<g transform="rotate({tail_a:.2f} {TAIL_PIVOT[0]} {TAIL_PIVOT[1]})">{tail_art()}{flame(t, 1.3, st.get("flame_e", 1.0))}</g>')
    o.append(f'<g transform="translate(0 {CBOT}) scale(1 {br:.4f}) translate(0 {-CBOT})">{body()}</g>')
    hy = -(br - 1) * (CBOT - NECK[1])
    o.append(f'<g transform="translate(0 {hy:.2f}) rotate({tilt:.2f} {NECK[0]} {NECK[1]})">{head(st, t)}</g>')
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-CX} {-CBOT})">{"".join(o)}</g>'


def head_world(x, y, k, st):
    """Точка морды (между глаз) в мире — для камеры."""
    return x, y + (1072 - CBOT) * k
