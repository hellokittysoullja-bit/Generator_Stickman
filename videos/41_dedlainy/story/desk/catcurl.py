"""Кот рилса 35 клубком (спит на подушке): тот же кот, что cat.py (голова, уши — ЛЕВОЕ от зрителя загнуто, зелёные
глаза, по две оранжевые полоски на щеках), но тело — клубок, голова лежит на передних лапках, хвост обвивает клубок
спереди, огонёк на кончике хвоста у морды. Глаза: blink 1 — закрыты (спит), 0 — открыты.
Внутренние координаты — как у cat.py (голова около (836, 1070)); draw(x, y, s) ставит точку (870, 1300) — низ клубка —
в (x, y)."""
import math

import numpy as np

import cat
import lib
from cat import CAT, CAT_SH, CAT_FUR, CAT_EDGE
from ink import ellipse_pts, fill_d, fur, ink_closed, sample
from lib import INK, blob, clip_of, line, shape
from parts import sausage

BX, BY = 870, 1300
HEAD_C = (790, 1130)          # куда сдвигается голова cat.py (центр морды 836, 1072)
HEAD_D = (HEAD_C[0] - 836, HEAD_C[1] - 1072 + 40)
TAIL = [(1040, 1236), (1010, 1282), (930, 1300), (830, 1300), (730, 1288), (668, 1258), (650, 1222)]
_ST = {}


def body_art():
    pts = ellipse_pts(905, 1206, 176, 98, 40)
    bp = fur(pts, 7, 7, seed=31)
    inner = blob([(930, 1100), (1100, 1150), (1100, 1320), (900, 1320), (980, 1220)], CAT_SH, .85)
    inner += blob(ellipse_pts(880, 1150, 120, 34, 16, rot=-6), CAT_FUR, .55)
    for i, st in enumerate([[(860, 1140), (880, 1150)], [(940, 1132), (958, 1146)], [(1010, 1160), (1024, 1176)],
                            [(900, 1200), (918, 1212)], [(980, 1214), (996, 1230)], [(1040, 1206), (1050, 1224)]]):
        inner += line(st, 2.2, CAT_EDGE, seed=340 + i, op=.85)
    # бедро задней лапы — дуга
    s = shape(bp, CAT, inner, w=5, seed=330)
    s += line([(960, 1278), (990, 1220), (1050, 1196), (1066, 1210)], 3.4, CAT_EDGE, seed=338, op=.9)
    return s


def tail_art():
    S = sample(TAIL, False, 3.0)
    n = len(S)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = 46 + (20 - 46) * np.linspace(0, 1, n) ** 1.1
    L, R = S + N * Wd[:, None] / 2, S - N * Wd[:, None] / 2
    tip = S[-1] + Tg[-1] * Wd[-1] * .45
    outline = [tuple(p) for p in L] + [tuple(tip)] + [tuple(p) for p in R[::-1]]
    sh = blob([(600, 1270), (1060, 1270), (1060, 1330), (600, 1330)], CAT_SH, .8)
    out = [f'<path d="{fill_d(outline)}" fill="{CAT}"/>']
    c = clip_of(outline)
    out.append(f'<g clip-path="url(#{c})">{sh}</g>')
    out.append(f'<path d="{ink_closed(outline, 4.8, seed=331)}" fill="{INK}"/>')
    for i, k in enumerate(range(int(n * .15), int(n * .9), int(n * .14))):
        p = S[k] + N[k] * Wd[k] * .1
        out.append(line([tuple(p), tuple(p + Tg[k] * 14)], 2, CAT_EDGE, seed=336 + i, op=.8))
    return "".join(out), tuple(tip)


def paws():
    s = []
    for k, px in enumerate((760, 832)):
        pp = ellipse_pts(px, 1252, 36, 22, 14)
        s.append(shape(pp, CAT, blob(ellipse_pts(px + 4, 1262, 30, 12, 10), CAT_SH, .5), w=4.4, seed=350 + k))
        for j in (-12, 0, 12):
            s.append(line([(px + j, 1258), (px + j, 1270)], 2.0, seed=352 + k * 3 + j))
    return "".join(s)


def static():
    if not _ST:
        _ST["body"] = body_art()
        _ST["tail"], _ST["tip"] = tail_art()
        _ST["paws"] = paws()
        st = cat.static_parts()
        _ST["head"] = st["head"]
        _ST["face"] = st["face"]
    return _ST


def flame(t, x, y, k=1.0, smolder=0.0, rot=-20.0):
    """Огонёк cat.flame на кончике (x, y). smolder 1 — тлеет: меньше, темнее, без светлого ядра."""
    bx, by = cat.FLAME_BASE
    kk = k * (1 - 0.45 * smolder)
    w1 = 4 * math.sin(t * 23) + 3 * math.sin(t * 37 + 1)
    w2 = 5 * math.sin(t * 29 + 2)
    w3 = 3 * math.sin(t * 17 + .5)
    if smolder > 0.5:
        w1, w2, w3 = w1 * .4, w2 * .4, w3 * .4
    P = [(-20, 4), (-24, -16), (-15 + w3 * .3, -36 + w2 * .3), (-13 + w1 * .4, -56), (-4, -45), (2 + w1, -82 + w2, 1), (11, -52),
         (20 + w2 * .6, -64 + w1 * .5, 1), (24, -36), (22, -11), (15, 4), (0, 9)]

    def tf(q):
        return (q[0] * kk, q[1] * kk) + ((1,) if len(q) > 2 else ())
    outer = lib.mix("#ff8a2a", "#b4441c", smolder)
    mid = lib.mix("#ffbe55", "#d8642a", smolder)
    core = lib.mix("#fff2c0", "#f0a050", smolder)
    o = shape([tf(q) for q in P], outer, blob([tf((q[0] * .7, q[1] * .7 + 2) + q[2:]) for q in P], mid), w=3.4, seed=233,
              ink_color="#7a2a10", var=.2)
    o += blob([tf(q) for q in [(-7, 2), (-5, -19), (2 + w1 * .3, -37), (7, -18), (5, 2)]], core)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f})">{o}</g>'


def draw(x, y, s, t, blink=1.0, look=(0.0, 0.0), flick=0.0, smolder=0.0, flame_k=1.0, breath=None, head_lift=0.0, tilt=0.0,
         glow=0.0):
    """Клубок: низ (870, 1300) → (x, y), масштаб s. blink 1 — спит. head_lift 0..1 — голова чуть приподнята."""
    st = static()
    br = (0.5 + 0.5 * math.sin(t * 2 * math.pi / 3.2)) if breath is None else breath
    o = []
    o.append(blob(ellipse_pts(880, 1302, 230, 20, 16), "#1a0e05", .3, lib.blur(8)))
    sy = 1 + 0.02 * br
    o.append(f'<g transform="translate(0 {BY}) scale({1 + .008 * br:.4f} {sy:.4f}) translate(0 {-BY})">{st["body"]}</g>')
    o.append(st["paws"])
    hx, hy = HEAD_D
    hy -= 26 * head_lift + 4 * br
    eyes = cat.eyes(look, blink)
    hg = st["head"] + cat.ears(flick) + st["face"] + eyes + cat.whiskers(t)
    o.append(f'<g transform="translate({hx:.2f} {hy:.2f}) rotate({-8 + tilt:.2f} 836 1146)">{hg}</g>')
    o.append(st["tail"])
    tx, ty = st["tip"]
    if glow > 0:
        g = lib.rad_grad([(0, "#ffd27a", .55 * glow), (1, "#ffb040", 0)], tx, ty - 30, 120)
        o.append(f'<circle cx="{tx:.1f}" cy="{ty - 30:.1f}" r="120" fill="url(#{g})"/>')
    o.append(flame(t, tx + 4, ty + 2, flame_k, smolder))
    return f'<g transform="translate({x - BX * s:.2f} {y - BY * s:.2f}) scale({s:.4f})">{"".join(o)}</g>'
