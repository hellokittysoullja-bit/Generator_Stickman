"""Кот рилса 28 — тот же сидящий кот, что в комнате рилсов 24–26 (heroes24: голова, уши — ЛЕВОЕ от зрителя загнуто,
зелёные глаза, по две оранжевые полоски на щеках, хвост завитком с огоньком), но живой кодом: моргание (в т.ч.
медленное), взгляд, наклон головы, флик уха, дыхание, хвост качается, огонёк колышется формой, левая (от зрителя)
передняя лапа вытягивается и ложится на предмет.

Рисунок — во внутренних координатах heroes24 (CX=836, низ лап 1306); в мир — draw(x, y, s, ...) ставит точку (836, 1306)
в (x, y) с масштабом s."""
import math

import numpy as np

import lib
from ink import ellipse_pts, fill_d, fur, ink_closed, sample
from lib import INK, blob, clip_of, line, shape, T
from parts import sausage

CAT, CAT_SH, CAT_FUR, CAT_EDGE = "#3a3646", "#211e29", "#56506a", "#6c6688"
CX, CBOT = 836, 1306
TAIL_C = [(904, 1272), (962, 1266), (1004, 1240), (1014, 1198), (994, 1166), (962, 1166), (944, 1192), (954, 1224), (986, 1236),
          (1010, 1214), (1014, 1168), (1006, 1120), (996, 1080)]
FLAME_BASE = (995, 1076)
TAIL_PIVOT = (912, 1272)
NECK = (836, 1150)
SHOULDER_L = (812, 1222)
PAW_REST = (811, 1298)
_ST = {}


def to_world(p, x, y, s):
    return (x + (p[0] - CX) * s, y + (p[1] - CBOT) * s)


def to_int(p, x, y, s):
    return (CX + (p[0] - x) / s, CBOT + (p[1] - y) / s)


# ───────────────────────── хвост (статичная форма, качается целиком вокруг корня)
def tail_art():
    S = sample(TAIL_C, False, 3.0)
    n = len(S)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = 40 + (14 - 40) * np.linspace(0, 1, n) ** 1.2
    L, R = S + N * Wd[:, None] / 2, S - N * Wd[:, None] / 2
    tip = S[-1] + Tg[-1] * Wd[-1] * .45
    outline = [tuple(p) for p in L] + [tuple(tip)] + [tuple(p) for p in R[::-1]]
    sh = blob([(1000, 1100), (1060, 1100), (1060, 1280), (990, 1280)], CAT_SH, .8)
    out = [f'<path d="{fill_d(outline)}" fill="{CAT}"/>']
    c = clip_of(outline)
    out.append(f'<g clip-path="url(#{c})">{sh}</g>')
    out.append(f'<path d="{ink_closed(outline, 4.8, seed=230)}" fill="{INK}"/>')
    d_ = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    k0 = int(np.argmin(np.abs(S[:, 1] - 1236) + np.abs(S[:, 0] - 970) + (d_ < d_[-1] * .4) * 1e4))
    k1 = int(np.argmin(np.abs(S[:, 1] - 1172) + np.abs(S[:, 0] - 1014) + (d_ < d_[-1] * .5) * 1e4))
    seg = [tuple(p) for p in L[k0:k1]] + [tuple(p) for p in R[k0:k1][::-1]]
    out.append(f'<path d="{fill_d(seg)}" fill="{CAT}"/>')
    sc = clip_of(seg)
    out.append(f'<g clip-path="url(#{sc})">{sh}</g>')
    for side, sd in ((L, 233), (R, 234)):
        pts = [tuple(p) for p in side[k0 - 2:k1 + 2:3]]
        out.append(line(pts, 4.8, seed=sd, taper=.1, wmin=.6, peak=.5))
    for i, k in enumerate(range(int(n * .1), int(n * .9), int(n * .12))):
        p = S[k] + N[k] * Wd[k] * .18
        q = p + Tg[k] * 12
        out.append(line([tuple(p), tuple(q)], 2, CAT_EDGE, seed=236 + i, op=.8))
    return "".join(out)


def flame(t, k=1.3):
    """Огонёк на кончике хвоста: язычки колышутся (форма от времени), ядро светлое."""
    bx, by = FLAME_BASE
    w1 = 4 * math.sin(t * 23) + 3 * math.sin(t * 37 + 1)
    w2 = 5 * math.sin(t * 29 + 2)
    w3 = 3 * math.sin(t * 17 + .5)
    P = [(-20, 4), (-24, -16), (-15 + w3 * .3, -36 + w2 * .3), (-13 + w1 * .4, -56), (-4, -45), (2 + w1, -82 + w2, 1), (11, -52),
         (20 + w2 * .6, -64 + w1 * .5, 1), (24, -36), (22, -11), (15, 4), (0, 9)]

    def tf(q, kk=k):
        return (bx + q[0] * kk, by + q[1] * kk) + ((1,) if len(q) > 2 else ())
    o = shape([tf(q) for q in P], "#ff8a2a", blob([tf((q[0] * .7, q[1] * .7 + 2) + q[2:]) for q in P], "#ffbe55"), w=3.4, seed=233,
              ink_color="#7a2a10", var=.2)
    o += blob([tf(q) for q in [(-7, 2), (-5, -19), (2 + w1 * .3, -37), (7, -18), (5, 2)]], "#fff2c0")
    return o


# ───────────────────────── уши (правое — флик), голова
def ears(flick=0.0):
    s = []
    re_out = [(864, 1004), (902, 922, 1), (932, 1016)]
    re_fill = re_out + [(934, 1046), (866, 1046)]
    r = []
    r.append(blob(re_fill, CAT))
    c = clip_of(re_fill)
    r.append(f'<g clip-path="url(#{c})">' + blob([(880, 1004), (902, 950), (918, 1008), (900, 1010)], "#9b6150") +
             blob([(904, 924), (940, 1000), (936, 1016), (918, 1014)], CAT_SH, .7) +
             line([(888, 1004), (898, 972)], 2, "#d79a84", seed=252, op=.8) + "</g>")
    r.append(line(re_out, 5, seed=251, taper=.25, wmin=.3))
    s.append(f'<g transform="rotate({flick:.2f} 898 1030)">{"".join(r)}</g>')
    le_out = [(752, 1014), (744, 986), (728, 994, 1), (728, 966), (746, 948), (772, 940), (796, 948), (808, 968), (814, 1006)]
    le_fill = le_out + [(816, 1046), (752, 1046)]
    s.append(blob(le_fill, CAT))
    c = clip_of(le_fill)
    s.append(f'<g clip-path="url(#{c})">' + blob([(762, 1002), (770, 980), (804, 996), (790, 1004)], "#9b6150") +
             blob([(728, 940), (812, 940), (806, 972), (770, 974), (744, 984), (726, 996)], CAT_FUR, .65) +
             line([(770, 998), (776, 984)], 2, "#d79a84", seed=256, op=.8) + "</g>")
    s.append(line([(740, 980), (770, 972), (800, 970)], 2.4, seed=255, op=.85))
    s.append(line(le_out, 5, seed=253, taper=.25, wmin=.3))
    return "".join(s)


def head_static():
    s = []
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884, 990), (940, 1050), (930, 1150), (866, 1150), (902, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    inner += blob([(800, 1106), (836, 1098), (872, 1106), (864, 1142), (808, 1142)], CAT_FUR, .45)
    for i, st in enumerate([[(800, 1004), (806, 1016)], [(836, 996), (838, 1010)], [(870, 1002), (866, 1014)]]):
        inner += line(st, 2, CAT_EDGE, seed=258 + i, op=.8)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250))
    return "".join(s)


def face_static():
    s = []
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76
            s.append(line([(x0, 1100 + dy), (x0 + sx * 30, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    s.append(shape([(826, 1108), (846, 1108), (836, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836, 1119), (836, 1124)], 2.4, seed=263))
    s.append(line([(822, 1124), (829, 1131), (836, 1124), (843, 1131), (850, 1124)], 3, seed=264))
    return "".join(s)


def eyes(look, blink, lid_c=CAT):
    """Глаза: blink 0 — открыт, 1 — закрыт (верхнее веко опускается до дуги, нижнее чуть поднимается)."""
    lx, ly = look
    s = []
    for nm, ex, sd in [("L", CX - 44, 255), ("R", CX + 44, 256)]:
        ep = ellipse_pts(ex, 1072, 34, 38, 16)
        if blink > 0.97:
            s.append(line([(ex - 32, 1076), (ex - 12, 1086), (ex + 12, 1086), (ex + 32, 1076)], 5.6, INK, seed=sd + 40, taper=.5, wmin=.3))
            continue
        cid = clip_of(ep)
        o = [f'<path d="{fill_d(ep)}" fill="#a9d84a"/><g clip-path="url(#{cid})">']
        o.append(blob(ellipse_pts(ex, 1046, 36, 20, 10), "#6f9a2e", .95))
        o.append(blob(ellipse_pts(ex, 1102, 26, 11, 10), "#d4f27a", .75))
        o.append(blob(ellipse_pts(ex - 18, 1080, 10, 20, 8), "#c8ee6a", .5))
        px, py = ex + lx * 12, 1074 + ly * 10
        o.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="11.5" ry="24" fill="#0b0a10"/>')
        o.append(f'<circle cx="{px - 8:.1f}" cy="{py - 16:.1f}" r="7" fill="#f4f8ff"/>')
        o.append("</g>")
        if blink > 0.01:
            # веко — поверх глаза в чуть большем овале (иначе по краю овала просвечивает зелёная кайма), контур глаза —
            # только ниже края века (иначе над веком остаётся пустой круг)
            b = blink
            ytop = 1072 - 40 + 84 * b          # край верхнего века
            ybot = 1112 - 22 * b               # край нижнего века
            c2 = clip_of(ellipse_pts(ex, 1072, 37, 41, 16))
            o.append(f'<g clip-path="url(#{c2})"><path d="M{ex - 44} 1020 L{ex + 44} 1020 L{ex + 44} {ytop - 6:.1f} Q{ex} {ytop + 10:.1f} {ex - 44} {ytop - 6:.1f}Z" fill="{lid_c}"/>'
                     f'<path d="M{ex - 44} 1124 L{ex + 44} 1124 L{ex + 44} {ybot + 4:.1f} Q{ex} {ybot - 6:.1f} {ex - 44} {ybot + 4:.1f}Z" fill="{lid_c}"/></g>')
            cc = lib.clip_rect(ex - 60, ytop - 2, 120, 200)
            o.append(f'<g clip-path="url(#{cc})"><path d="{ink_closed(ep, 4.4, seed=sd + 3)}" fill="{INK}"/></g>')
            o.append(f'<g clip-path="url(#{c2})">' + line([(ex - 38, ytop - 6), (ex, ytop + 3), (ex + 38, ytop - 6)], 5, INK, seed=sd + 30) + "</g>")
        else:
            o.append(f'<path d="{ink_closed(ep, 4.4, seed=sd + 3)}" fill="{INK}"/>')
        s.append("".join(o))
    return "".join(s)


def whiskers(t):
    s = []
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CX + sx * 58
            w = 3 * math.sin(t * 2.1 + k + sx)
            s.append(line([(x0, 1128 + dy * .8), (x0 + sx * 50, 1126 + dy + dl * .5 + w * .5), (x0 + sx * 96, 1124 + dy * 1.2 + dl + w)], 1.4,
                          "#cfcbe0", seed=270 + k + sx, op=.9))
    return "".join(s)


# ───────────────────────── тело, лапы
def body_static():
    s = []
    body = [(760, 1296), (744, 1240), (756, 1180), (790, 1142), (880, 1142), (916, 1180), (928, 1240), (912, 1296)]
    bp = fur(body, 7, 7, seed=22)
    inner = blob([(860, 1140), (930, 1180), (930, 1300), (874, 1300), (888, 1220)], CAT_SH, .9)
    inner += blob([(798, 1170), (836, 1160), (874, 1170), (864, 1244), (836, 1266), (808, 1244)], CAT_FUR, .6)
    for i, st in enumerate([[(816, 1190), (826, 1208)], [(852, 1192), (846, 1212)], [(834, 1214), (836, 1236)], [(806, 1222), (814, 1238)],
                            [(864, 1226), (858, 1244)]]):
        inner += line(st, 2.2, CAT_EDGE, seed=240 + i, op=.85)
    s.append(shape(bp, CAT, inner, w=5, seed=241))
    for sx, sd in [(-1, 242), (1, 243)]:
        px = CX + sx * 70
        foot = ellipse_pts(px, 1286, 34, 26, 12, rot=sx * 12)
        s.append(shape(foot, CAT, blob(T(ellipse_pts(px, 1292, 26, 20, 10), sx * 4, 0), CAT_SH, .5), w=4.6, seed=sd))
        s.append(blob(ellipse_pts(px + sx * 3, 1296, 13, 10, 10, rot=sx * 10), "#e8823a"))
        for k in range(3):
            ang = math.radians(-90 + (k - 1) * 42 + sx * 10)
            s.append(blob(ellipse_pts(px + sx * 3 + math.cos(ang) * 19, 1296 + math.sin(ang) * 15, 5, 4.4, 8), "#e8823a"))
    # правая (от зрителя) передняя лапа — стоит
    fx = CX + 25
    paw = [(fx - 20, 1306, 1), (fx - 19, 1252), (fx + 19, 1252), (fx + 20, 1306, 1)]
    s.append(shape(paw, CAT, blob([(fx + 6, 1250), (fx + 20, 1250), (fx + 20, 1306), (fx + 8, 1306)], CAT_SH, .7), w=4.6, seed=245))
    for k in (-7, 7):
        s.append(line([(fx + k, 1294), (fx + k, 1306)], 2.2, seed=245 + k))
    return "".join(s)


def leg_left(P, press=0.0):
    """Левая (от зрителя) передняя лапа от плеча к точке P (внутр. коорд.). Без чернил у плеча — сливается с грудью."""
    S = np.array(SHOULDER_L, float)
    P = np.array(P, float)
    d = P - S
    L = np.linalg.norm(d) + 1e-9
    u = d / L
    nrm = np.array([-u[1], u[0]])
    bend = 10 * min(1.0, max(0.0, (L - 76) / 60))
    M = S + d * 0.5 + nrm * bend * (1 if d[0] < 0 else -1)
    mid = [tuple(S - u * 18), tuple(M), tuple(P)]
    w0, w1 = 44, 40 * (1 + 0.08 * press)
    out = sausage(mid, w0, w1)
    o = [f'<path d="{fill_d(out)}" fill="{CAT}"/>']
    c = clip_of(out)
    o.append(f'<g clip-path="url(#{c})">' + blob([tuple(S + nrm * 4 - u * 30), tuple(P + nrm * 30 + u * 30), tuple(P - nrm * 2 + u * 30),
                                                    tuple(S - nrm * 6 - u * 30)], CAT_SH, .55) + "</g>")
    # тушь по контуру без основания: от 3-й точки (основание прямое, внутри груди)
    o.append(line(out[2:-2], 4.6, seed=244, taper=.25, wmin=.25))
    # пальцы на конце
    tip = P + u * (w1 / 2 - 4)
    for k in (-1, 1):
        a = tip + nrm * k * 8
        o.append(line([tuple(a - u * 14), tuple(a)], 2.2, seed=246 + k))
    return "".join(o)


def static_parts():
    if not _ST:
        _ST["tail"] = tail_art()
        _ST["head"] = head_static()
        _ST["face"] = face_static()
        _ST["body"] = body_static()
    return _ST


def draw(x, y, s, t, look=(0, 0), blink=0.0, tilt=0.0, tail=0.0, flick=0.0, paw=None, press=0.0, breath=None, shadow=True):
    """Кот в мире: низ лап (836, 1306) → (x, y), масштаб s. paw — точка лапы во внутренних координатах (None — стоит)."""
    st = static_parts()
    br = (0.5 + 0.5 * math.sin(t * 2 * math.pi / 2.6)) if breath is None else breath
    o = []
    if shadow:
        o.append(blob(ellipse_pts(860, 1306, 150, 18, 16), "#1a0e05", .35, lib.blur(8)))
    tw = f"rotate({tail:.2f} {TAIL_PIVOT[0]} {TAIL_PIVOT[1]})"
    o.append(f'<g transform="{tw}">{st["tail"]}</g>')
    sy = 1 + 0.012 * br
    o.append(f'<g transform="translate(0 {CBOT}) scale(1 {sy:.4f}) translate(0 {-CBOT})">{st["body"]}</g>')
    P = PAW_REST if paw is None else paw
    o.append(leg_left(P, press))
    hy = -(sy - 1) * (CBOT - 1150)
    hg = st["head"] + ears(flick) + st["face"] + eyes(look, blink) + whiskers(t)
    o.append(f'<g transform="translate(0 {hy:.2f}) rotate({tilt:.2f} {NECK[0]} {NECK[1]})">{hg}</g>')
    o.append(f'<g transform="{tw}">{flame(t)}</g>')
    return f'<g transform="translate({x - CX * s:.2f} {y - CBOT * s:.2f}) scale({s:.4f})">{"".join(o)}</g>'


def flame_world(x, y, s, tail=0.0):
    a = math.radians(tail)
    dx, dy = FLAME_BASE[0] - TAIL_PIVOT[0], FLAME_BASE[1] - TAIL_PIVOT[1]
    p = (TAIL_PIVOT[0] + dx * math.cos(a) - dy * math.sin(a), TAIL_PIVOT[1] + dx * math.sin(a) + dy * math.cos(a) - 40)
    return to_world(p, x, y, s)
