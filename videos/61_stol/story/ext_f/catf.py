"""Кот группы F рилса 61 поверх общего кота (common/cat.py; анфас, как look/hero.png: ЛЕВОЕ от зрителя ухо загнуто).

draw_f(x, y, k, st, t) — сидящий кот, как cat.draw, плюс:
    st['reach'] 0..1  — передняя лапа (справа от зрителя) тянется вбок и толкает (st['reach_lift'] 0..1 — лапа приподнята);
    st['knead'] — фаза «топтания» (лапы по очереди приподнимаются), st['knead_a'] 0..1 — сила;
    st['eyes'] = (закрыт_левый, закрыт_правый) 0..1 — у каждого глаза своё веко (1 — дуга сна).
curl(x, y, k, st, t) — кот спит клубком (вид спереди-сверху): голова на лапах, глаза-дуги, хвост с огоньком обвивает тело;
    st['eye_r'] 0..1 — правый глаз приоткрыт; st['breath'] — дыхание; st['ear'] — подёргивание стоячего уха.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
_C61 = os.path.join(STORY, "common")
if _C61 not in sys.path:
    sys.path.insert(0, _C61)
if not os.path.exists(os.path.join(_C61, "cat.py")):          # пока группа B не положила cat.py в common — тот же кот рилса 60
    sys.path.append(os.path.join(STORY, "..", "..", "60_temnota", "story", "common"))
import cat as Cat  # noqa: E402
import lib  # noqa: E402
from ink import ellipse_pts, fill_d, fur, sample  # noqa: E402
from lib import INK, blob, line, shape  # noqa: E402

import numpy as np  # noqa: E402

CAT, CAT_SH, CAT_FUR, CAT_EDGE = Cat.CAT, Cat.CAT_SH, Cat.CAT_FUR, Cat.CAT_EDGE
CX, CBOT, NECK = Cat.CX, Cat.CBOT, Cat.NECK
PAD = "#e8823a"


# ───────────────────────────── голова с отдельными веками ─────────────────────────────
def head_f(st, t):
    """Как cat.head, но веки у глаз свои: st['eyes'] = (левый, правый)."""
    turn = st.get("turn", 0.0)
    look = st.get("look", (0.0, 0.0))
    bl = st.get("blink", 0.0)
    eyes = st.get("eyes", (bl, bl))
    FX = 22 * turn
    s = []
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884 + FX * .5, 990), (940, 1050), (930, 1150), (866 + FX * .5, 1150), (902 + FX * .5, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    inner += blob([(800 + FX, 1106), (836 + FX, 1098), (872 + FX, 1106), (864 + FX, 1142), (808 + FX, 1142)], CAT_FUR, .45)
    for i, p in enumerate([[(800, 1004), (806, 1016)], [(836, 996), (838, 1010)], [(870, 1002), (866, 1014)]]):
        inner += line(p, 2, CAT_EDGE, seed=258 + i, op=.8)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250))
    s.append(Cat.ears(st.get("ear", 0.0), st.get("perk", 0.0)))
    CXH = CX + FX
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76 + FX * (.5 if sx * turn > 0 else 1.0)
            ln = 30 * (1 - .4 * max(0, sx * turn))
            s.append(line([(x0, 1100 + dy), (x0 + sx * ln, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    for i, (nm, ex, sd) in enumerate([("L", CXH - 44 - 4 * turn, 255), ("R", CXH + 44 - 4 * turn, 256)]):
        sq = 1.0 - .22 * max(0.0, turn if nm == "R" else -turn)
        s.append(Cat.eye(ex, 1072, 34, 38, look, eyes[i], sd, sq))
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


# ───────────────────────────── тело с живыми передними лапами ─────────────────────────────
def _paw_leg(top, foot, w=40.0, seed=0, pad=False):
    """Передняя лапа одной фигурой: от плеча (top) до стопы (foot), стопа округлая; pad — видны подушечки (лапа поднята)."""
    tx, ty = top
    fx, fy = foot
    d = np.array([fx - tx, fy - ty], float)
    L = float(np.linalg.norm(d)) + 1e-6
    u = d / L
    n = np.array([-u[1], u[0]])
    h = w / 2
    pts = []
    pts.append(tuple(np.array(top) + n * h * 1.05))
    pts.append(tuple(np.array(top) + n * h * .98 + u * L * .55))
    for a in np.linspace(0, math.pi, 9):          # округлая стопа: полукруг от +n через носок к −n
        q = np.array(foot) + n * h * 1.08 * math.cos(a) + u * h * .95 * math.sin(a)
        pts.append(tuple(q))
    pts.append(tuple(np.array(top) - n * h * .98 + u * L * .55))
    pts.append(tuple(np.array(top) - n * h * 1.05))
    inner = blob([tuple(np.array(top) - n * h * 1.2), tuple(np.array(top) - n * h * .2), tuple(np.array(foot) - n * h * .2 + u * h),
                  tuple(np.array(foot) - n * h * 1.3 + u * h)], CAT_SH, .7)
    o = shape(pts, CAT, inner, w=4.6, seed=seed)
    if pad:
        c = np.array(foot) + u * h * .2
        o += blob(ellipse_pts(c[0], c[1], 12, 9, 10), PAD)
        for kk in (-1, 0, 1):
            q = c + n * kk * 14 + u * (14 - 4 * abs(kk))
            o += blob(ellipse_pts(q[0], q[1], 4.6, 4, 8), PAD)
    else:
        for kk in (-7, 7):
            a = np.array(foot) + n * kk + u * (h * .55)
            b = a - u * 11
            o += line([tuple(b), tuple(a)], 2.2, seed=seed + 5 + kk)
    return o


def body_f(st, t):
    """Тело кота (как cat.body), но передние лапы — отдельными фигурами: тянуться, топтаться."""
    s = []
    bd = [(760, 1296), (744, 1240), (756, 1180), (790, 1142), (880, 1142), (916, 1180), (928, 1240), (912, 1296)]
    bp = fur(bd, 7, 7, seed=22)
    inner = blob([(860, 1140), (930, 1180), (930, 1300), (874, 1300), (888, 1220)], CAT_SH, .9)
    inner += blob([(798, 1170), (836, 1160), (874, 1170), (864, 1244), (836, 1266), (808, 1244)], CAT_FUR, .6)
    for i, p in enumerate([[(816, 1190), (826, 1208)], [(852, 1192), (846, 1212)], [(834, 1214), (836, 1236)], [(806, 1222), (814, 1238)],
                           [(864, 1226), (858, 1244)]]):
        inner += line(p, 2.2, CAT_EDGE, seed=240 + i, op=.85)
    s.append(shape(bp, CAT, inner, w=5, seed=241))
    for sx, sd in [(-1, 242), (1, 243)]:          # задние лапы
        px = CX + sx * 70
        foot = ellipse_pts(px, 1286, 34, 26, 12, rot=sx * 12)
        s.append(shape(foot, CAT, blob(lib.T(ellipse_pts(px, 1292, 26, 20, 10), sx * 4, 0), CAT_SH, .5), w=4.6, seed=sd))
        s.append(blob(ellipse_pts(px + sx * 3, 1296, 13, 10, 10, rot=sx * 10), PAD))
        for k in range(3):
            ang = math.radians(-90 + (k - 1) * 42 + sx * 10)
            s.append(blob(ellipse_pts(px + sx * 3 + math.cos(ang) * 19, 1296 + math.sin(ang) * 15, 5, 4.4, 8), PAD))
    reach, rl = st.get("reach", 0.0), st.get("reach_lift", 0.0)
    kn, ka = st.get("knead"), st.get("knead_a", 0.0)
    for sx, sd in [(-1, 244), (1, 245)]:          # передние лапы
        fx = CX + sx * 25
        lift = 0.0
        if kn is not None:
            lift = ka * max(0.0, math.sin(2 * math.pi * kn + (0 if sx < 0 else math.pi))) * 26
        dx = 0.0
        if sx > 0:
            dx = 92 * reach
            lift += 44 * rl
        foot = (fx + dx, 1290 - lift)
        top = (fx + 4 * sx + 10 * reach * (sx > 0), 1206)
        s.append(_paw_leg(top, foot, 42, seed=sd, pad=(sx > 0 and rl > .45)))
    return "".join(s)


def draw_f(x, y, k, st, t):
    """Сидящий кот: st — как cat.draw (tilt, turn, look, blink, ear, perk, tail, flame_e, sx/sy — сжатие) + reach/knead/eyes."""
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    sx, sy = st.get("sx", 1.0), st.get("sy", 1.0) * br
    o = [f'<g transform="rotate({st.get("tail", 0.0):.2f} {Cat.TAIL_PIVOT[0]} {Cat.TAIL_PIVOT[1]})">{Cat.tail_art()}'
         f'{Cat.flame(t, 1.3, st.get("flame_e", 1.0))}</g>']
    o.append(f'<g transform="translate({CX} {CBOT}) scale({sx:.4f} {sy:.4f}) translate({-CX} {-CBOT})">{body_f(st, t)}</g>')
    hy = -(sy - 1) * (CBOT - NECK[1]) + st.get("head_dy", 0.0)
    o.append(f'<g transform="translate({st.get("head_dx", 0.0):.2f} {hy:.2f}) rotate({st.get("tilt", 0.0):.2f} {NECK[0]} {NECK[1]})">'
             f'{head_f(st, t)}</g>')
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({st.get("rot", 0.0):.2f}) scale({k:.4f}) translate({-CX} {-CBOT})">{"".join(o)}</g>'


# ───────────────────────────── клубок ─────────────────────────────
def _sleep_eye(ex, ey, rx, sd, open_=0.0, look=(0.0, 0.0)):
    """Спящий глаз — дуга ∪ (ресницы-уголок); open_ > 0 — веко приподнимается, видна щёлка зелёного глаза."""
    if open_ < .05:
        return (line([(ex - rx, ey - 4), (ex - rx * .45, ey + 8), (ex + rx * .45, ey + 8), (ex + rx, ey - 4)], 6, INK, seed=sd, taper=.55, wmin=.35)
                + line([(ex + rx * .9, ey - 2), (ex + rx * 1.25, ey - 9)], 3, INK, seed=sd + 3, taper=.6))
    return Cat.eye(ex, ey, rx, rx * 1.1, look, 1.0 - .62 * open_, sd, 1.0)


def curl_head(st, t):
    """Голова спящего кота (в координатах cat.head, но глаза — дуги, морда спокойная)."""
    s = []
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884, 990), (940, 1050), (930, 1150), (866, 1150), (902, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    inner += blob([(800, 1106), (836, 1098), (872, 1106), (864, 1142), (808, 1142)], CAT_FUR, .45)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250))
    s.append(Cat.ears(st.get("ear", 0.0), 0.0))
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76
            s.append(line([(x0, 1100 + dy), (x0 + sx * 30, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    s.append(_sleep_eye(CX - 44, 1074, 30, 455, 0.0))
    s.append(_sleep_eye(CX + 44, 1074, 30, 456, st.get("eye_r", 0.0), st.get("look", (0.0, 0.0))))
    s.append(shape([(826, 1108), (846, 1108), (836, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836, 1119), (836, 1124)], 2.4, seed=263))
    s.append(line([(824, 1123), (830, 1130), (836, 1125), (842, 1130), (848, 1123)], 2.8, seed=264))
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CX + sx * 58
            wv = 2 * math.sin(t * 1.6 + k + sx)
            s.append(line([(x0, 1128 + dy * .8), (x0 + sx * 48, 1128 + dy + dl * .5 + wv * .5), (x0 + sx * 90, 1130 + dy * 1.2 + dl + wv)], 1.4,
                          "#cfcbe0", seed=270 + k + sx, op=.9))
    return "".join(s)


# хвост клубка: от спины справа, вокруг передней части тела, кончик с огоньком слева у морды
CURL_TAIL = [(992, 1236), (1006, 1268), (980, 1300), (920, 1318), (836, 1326), (742, 1322), (676, 1308), (634, 1290), (612, 1262)]


def _tail_band(pts, w0, w1):
    S = sample(pts, False, 3.0)
    n = len(S)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = w0 + (w1 - w0) * np.linspace(0, 1, n) ** 1.2
    L, R = S + N * Wd[:, None] / 2, S - N * Wd[:, None] / 2
    tip = S[-1] + Tg[-1] * Wd[-1] * .45
    return [tuple(p) for p in L] + [tuple(tip)] + [tuple(p) for p in R[::-1]], S, Tg


def curl(x, y, k, st, t):
    br = st.get("breath", math.sin(t * 2 * math.pi / 2.6))
    o = []
    # тело-«булочка»: овал, спина вверх, дыхание поднимает спину
    by = 1236
    body = [(686, 1300), (676, 1250), (700, 1196), (760, 1162 - 6 * br), (840, 1150 - 8 * br), (920, 1160 - 6 * br), (982, 1198), (1000, 1252),
            (986, 1300)]
    bp = fur(body, 7, 7, seed=422)
    inner = blob([(900, 1150), (1010, 1190), (1010, 1310), (900, 1310), (930, 1240)], CAT_SH, .9)
    inner += blob([(740, 1180), (840, 1162), (920, 1176), (880, 1196), (780, 1200)], CAT_FUR, .55)
    for i, p in enumerate([[(760, 1206), (770, 1222)], [(900, 1200), (892, 1218)], [(948, 1240), (938, 1256)], [(830, 1176), (834, 1192)]]):
        inner += line(p, 2.2, CAT_EDGE, seed=430 + i, op=.85)
    o.append(shape(bp, CAT, inner, w=5, seed=421))
    # задняя лапа сбоку (справа), подушечки спрятаны
    o.append(shape(ellipse_pts(944, 1282, 40, 22, 12, rot=-8), CAT, blob(ellipse_pts(950, 1290, 30, 14, 10), CAT_SH, .6), w=4.6, seed=433))
    # передние лапы под подбородком
    for sx, sd in ((-1, 436), (1, 437)):
        px = 806 + sx * 34
        o.append(shape(ellipse_pts(px, 1300, 30, 17, 12, rot=sx * 6), CAT, blob(ellipse_pts(px, 1306, 22, 9, 10), CAT_SH, .5), w=4.4, seed=sd))
        for kk in (-8, 8):
            o.append(line([(px + kk, 1296), (px + kk, 1310)], 2, seed=sd + 7 + kk))
    # голова лежит на лапах, наклонена
    tilt = -10 + 1.5 * br
    o.append(f'<g transform="translate({-74:.1f} {128 + 3 * br:.1f}) rotate({tilt:.2f} 836 1146) translate(836 1146) scale(.98) translate(-836 -1146)">'
             f'{curl_head(st, t)}</g>')
    # хвост обвивает тело спереди, огонёк у кончика
    tw = st.get("tail_w", 0.0)
    tp = [(p[0], p[1] + (4 * tw * math.sin(i * .9) if i > 4 else 0)) for i, p in enumerate(CURL_TAIL)]
    outline, S, Tg = _tail_band(tp, 40, 16)
    o.append(shape(outline, CAT, blob([(600, 1300), (1020, 1300), (1020, 1360), (600, 1360)], CAT_SH, .7), w=4.8, seed=440))
    tip = S[-1]
    fb = Cat.FLAME_BASE
    fk = st.get("flame_k", 1.0)
    o.append(f'<g transform="translate({tip[0] - 4:.1f} {tip[1] - 6:.1f}) scale({.8 * fk:.3f}) translate({-fb[0]} {-fb[1]})">'
             f'{Cat.flame(t, 1.3, st.get("flame_e", 1.0))}</g>')
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-CX} {-CBOT})">{"".join(o)}</g>'
