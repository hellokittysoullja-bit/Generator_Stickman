"""Утренний парк для сцены run: небо с солнцем, лес (параллакс .22), деревья (.5), кусты (.78), дорожка с краем
газона, фонари и скамейка (слой 1.0, мир), пятна света и длинные тени, передний план (1.35), лучи сквозь листву.
Манера — как у 23–25: чистый контур живой линией (ink.py), плоский цвет с одной тенью."""
import math

import numpy as np

import lib
from lib import INK, blob, ellipse_pts, f, line, shape

PATH_Y0, PATH_Y1 = -72.0, 112.0       # дальний и ближний край дорожки (мир)
EDGE_Y = -84.0                         # газон за дорожкой: на нём стоят фонари и скамейка
SUN = (210.0, 430.0)                   # солнце (экран)

G_LIT, G_MID, G_SH, G_DEEP = "#9cc76a", "#78ad55", "#55893f", "#3f6b33"
TRUNK, TRUNK_SH = "#8a6248", "#5f4232"
PATH, PATH_SH, PATH_LIT = "#e2cfaa", "#c7ae86", "#f4e6c4"
SHADOW = "#3a3f63"


def rs_(*k):
    return np.random.RandomState(abs(hash_int(*k)) % (2 ** 31))


def hash_int(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return h


def scallop(cx, cy, rx, ry, n, seed, depth=0.16, rot=0.0):
    """Крона/куст: эллипс, обведённый n дугами-лепестками (точки с углами между дугами)."""
    rs = np.random.RandomState(seed)
    out = []
    a0 = rs.uniform(0, 2 * math.pi)
    angs = a0 + np.cumsum(np.r_[0, rs.uniform(0.8, 1.2, n - 1)])
    angs = a0 + (angs - a0) / (angs[-1] - a0 + rs.uniform(0.8, 1.2)) * 2 * math.pi
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n):
        a, b = angs[i], angs[(i + 1) % n] + (2 * math.pi if i == n - 1 else 0)
        for j, u in enumerate((0.0, 0.5)):
            m = a + (b - a) * u
            r = 1.0 + (depth * rs.uniform(.7, 1.2) if j == 1 else 0)
            x, y = rx * r * math.cos(m), ry * r * math.sin(m)
            out.append((cx + x * cr - y * sr, cy + x * sr + y * cr) + ((1,) if j == 0 else ()))
    return out


# ═════════════════════════ небо, лес, деревья, кусты (экранные слои) ═════════════════════════
def sky(t):
    g = lib.lin_grad([(0, "#8ec5e6", 1), (0.30, "#bfdcea", 1), (0.46, "#f4e7c6", 1), (0.6, "#fbd9a2", 1), (1, "#f6c98e", 1)],
                     0, 0, 0, 1920, units="userSpaceOnUse")
    o = [f'<rect x="-300" y="-300" width="1680" height="2520" fill="url(#{g})"/>']
    gs = lib.rad_grad([(0, "#fffbe8", 1), (.12, "#fff3cf", .95), (.35, "#ffe2a4", .45), (1, "#ffd99a", 0)], SUN[0], SUN[1], 520)
    o.append(f'<rect x="-300" y="-300" width="1680" height="2520" fill="url(#{gs})"/>')
    o.append(f'<circle cx="{SUN[0]}" cy="{SUN[1]}" r="62" fill="#fffdf2"/>')
    # пара лёгких облаков (медленно)
    for k, (x, y, w) in enumerate([(760, 170, 300), (1010, 300, 200), (380, 120, 220)]):
        xx = (x - t * 9 * (1 + k * .3)) % 1500 - 210
        pts = scallop(xx, y, w / 2, w / 7, 7, 30 + k, depth=.35)
        o.append(blob(pts, "#fdf7ea", .95))
        o.append(blob(scallop(xx + w * .06, y + w / 18, w / 2.3, w / 14, 6, 40 + k, depth=.2), "#ecdfcf", .7))
    return "".join(o)


def far_forest(cx, s):
    """Лес у горизонта, дымка: силуэт без контура, верх ~720–780."""
    p = 0.22
    off = cx * p * s
    o = []
    for layer, (y0, col, amp, sp, sd) in enumerate([(770, "#a9c2b0", 46, 70, 11), (812, "#94b39c", 40, 56, 17)]):
        xs = np.arange(-200, 1300, 8.0)
        X = xs + off * (1 + layer * .3)
        ys = []
        for x in X:
            k = math.floor(x / sp)
            v = 0
            for j in (k - 1, k, k + 1, k + 2):
                rs = rs_(sd, j)
                cxj = j * sp + rs.uniform(0, sp)
                r = rs.uniform(.6, 1.2) * sp * .75
                d = abs(x - cxj)
                if d < r:
                    v = max(v, math.sqrt(r * r - d * d) / r * amp * rs.uniform(.7, 1.1))
            ys.append(y0 - v)
        pts = [(float(a), float(b)) for a, b in zip(xs, ys)] + [(1300, 1100, 1), (-200, 1100, 1)]
        o.append(f'<path d="M{" L".join(f"{f(a)} {f(b)}" for a, b, *_ in pts)}Z" fill="{col}"/>')
    return "".join(o)


def tree(x, base, h, w, seed, ink_w=4.4, cols=(G_LIT, G_MID, G_SH), trunk=(TRUNK, TRUNK_SH), lean=0.0):
    """Дерево: ствол с развилкой и крона-облако из 2–3 крупных масс. x, base — низ ствола (экран или мир)."""
    rs = np.random.RandomState(seed)
    o = []
    top = base - h
    cxk, cyk = x + lean * h * .3, top + h * .32
    tw = w * .085
    # ствол и ветки
    tr = [(x - tw * 1.3, base, 1), (x - tw * .9, base - h * .1), (x - tw * .7 + lean * h * .1, base - h * .45), (cxk - tw * .5, cyk + h * .05),
          (cxk + tw * .5, cyk + h * .05), (x + tw * .7 + lean * h * .1, base - h * .45), (x + tw * .95, base - h * .1), (x + tw * 1.4, base, 1)]
    inner = blob([(x + tw * .1, base), (x + tw * 1.6, base), (cxk + tw, cyk), (cxk + tw * .1, cyk)], trunk[1], .9)
    inner += line([(x - tw * .3, base - h * .12), (x - tw * .1, base - h * .3)], ink_w * .45, trunk[1], seed=seed + 3)
    o.append(shape(tr, trunk[0], inner, w=ink_w, seed=seed))
    for k in (-1, 1):
        br = [(x + lean * h * .1, base - h * .48), (x + k * w * .18, base - h * .62), (x + k * w * .26, base - h * .7)]
        o.append(shape(lib.band(br, tw * .9, tw * .4, step=4), trunk[0], "", w=ink_w * .8, seed=seed + 5 + k))
    # крона
    masses = [(cxk, cyk - h * .02, w * .5, h * .3)]
    masses += [(cxk - w * .3, cyk + h * .1, w * .32, h * .2), (cxk + w * .32, cyk + h * .08, w * .33, h * .21)]
    if rs.uniform() < .6:
        masses.append((cxk + w * .05, cyk - h * .2, w * .34, h * .17))
    for i, (mx, my, rx, ry) in enumerate(masses):
        pts = scallop(mx, my, rx, ry, 9, seed + 20 + i, depth=.14)
        inn = blob(scallop(mx + rx * .3, my + ry * .38, rx * .9, ry * .7, 8, seed + 40 + i, .12), cols[2], .95)
        inn += blob(scallop(mx - rx * .32, my - ry * .4, rx * .5, ry * .4, 7, seed + 60 + i, .2), cols[0], .95)
        for j in range(4):
            a = rs.uniform(0, 2 * math.pi)
            px, py = mx + rx * .55 * math.cos(a), my + ry * .5 * math.sin(a)
            inn += line([(px - rx * .09, py), (px, py - ry * .07), (px + rx * .09, py)], ink_w * .5, cols[2], seed=seed + 80 + i * 4 + j,
                        op=.9)
        o.append(shape(pts, cols[1], inn, w=ink_w, seed=seed + 100 + i))
    return "".join(o)


def mid_trees(cx, s):
    p = 0.5
    o = []
    sp = 380.0
    off = cx * p
    i0 = math.floor((off - 900) / sp)
    for i in range(i0, i0 + 9):
        rs = rs_(77, i)
        lx = i * sp + rs.uniform(-60, 60)
        x = 540 + (lx - off) * s * .62
        if not -500 < x < 1580:
            continue
        h = rs.uniform(560, 700)
        w = rs.uniform(360, 460)
        o.append(tree(x, 1010 + rs.uniform(-10, 10), h, w, 300 + i % 97, ink_w=3.6,
                      cols=("#b6d08a", "#93ba70", "#6f9c58"), trunk=("#9a7a62", "#755a48")))
    return "".join(o)


def bushes(cx, s):
    p = 0.78
    o = []
    sp = 230.0
    off = cx * p
    i0 = math.floor((off - 700) / sp)
    # газон за кустами
    o.append(f'<rect x="-300" y="1010" width="1680" height="140" fill="#a9cc78"/>')
    for i in range(i0, i0 + 10):
        rs = rs_(91, i)
        lx = i * sp + rs.uniform(-50, 50)
        x = 540 + (lx - off) * s * .8
        if not -300 < x < 1380:
            continue
        w, h = rs.uniform(170, 260), rs.uniform(90, 140)
        y = 1074
        pts = scallop(x, y - h * .45, w / 2, h / 2, 8, 500 + i % 89, .2)
        inn = blob(scallop(x + w * .12, y - h * .25, w * .45, h * .38, 7, 600 + i % 89, .15), "#5f9448", .95)
        inn += blob(scallop(x - w * .16, y - h * .68, w * .22, h * .16, 6, 700 + i % 89, .2), "#b3d585", .95)
        o.append(shape(pts, "#80b25c", inn, w=3.6, seed=800 + i % 89))
    return "".join(o)


def backdrop(cx, cy, s, rot, t):
    o = [sky(t), far_forest(cx, s), mid_trees(cx, s), light_overlay(t, cx), bushes(cx, s)]
    return f'<g transform="rotate({f(rot * .5)} 540 960)">{"".join(o)}</g>'


# ═════════════════════════ слой 1.0: газон, дорожка, фонари, скамейка ═════════════════════════
LAMPS = [520.0, 2040.0, 3300.0]
BENCH = 1260.0
EDGE_TREES = [(-260.0, 1), (2700.0, 2)]


def view(cx, s):
    return cx - 720 / s, cx + 720 / s


def ground(cx, cy, s, t):
    x0, x1 = view(cx, s)
    o = []
    # газон за дорожкой (мир)
    o.append(f'<rect x="{f(x0)}" y="{f(EDGE_Y - 80)}" width="{f(x1 - x0)}" height="90" fill="#9ec66e"/>')
    # тени крон над дорожкой (деревья за кадром сверху) и пятна солнца — в мире, едут с землёй
    o.append(f'<rect x="{f(x0)}" y="{f(PATH_Y0)}" width="{f(x1 - x0)}" height="{f(PATH_Y1 - PATH_Y0)}" fill="{PATH}"/>')
    rsx = 260.0
    for i in range(math.floor(x0 / rsx) - 1, math.floor(x1 / rsx) + 2):
        rs = rs_(13, i)
        # камешки и трещинки
        for k in range(7):
            px, py = i * rsx + rs.uniform(0, rsx), rs.uniform(PATH_Y0 + 10, PATH_Y1 - 8)
            rx = rs.uniform(3, 7) * (1 + (py - PATH_Y0) / 300)
            o.append(blob(ellipse_pts(px, py, rx, rx * .55, 8), PATH_SH, .9))
            o.append(blob(ellipse_pts(px - rx * .3, py - rx * .2, rx * .45, rx * .22, 6), PATH_LIT, .9))
        if rs.uniform() < .5:
            px, py = i * rsx + rs.uniform(0, rsx), rs.uniform(PATH_Y0 + 30, PATH_Y1 - 30)
            o.append(line([(px, py), (px + 26, py + 6), (px + 40, py + 2), (px + 62, py + 10)], 2.2, PATH_SH, seed=900 + i % 50))
    sh_x = 520.0
    for i in range(math.floor(x0 / sh_x) - 2, math.floor(x1 / sh_x) + 2):
        rs = rs_(17, i)
        px = i * sh_x + rs.uniform(0, 200)
        w = rs.uniform(240, 380)
        pts = scallop(px + w / 2, (PATH_Y0 + PATH_Y1) / 2 + rs.uniform(-20, 30), w / 2, 70, 8, 1000 + i % 71, .25, rot=.32)
        o.append(blob(pts, SHADOW, .2))
    # тени фонарей и скамейки, длинные, вниз-вправо
    for lx in LAMPS:
        if x0 - 600 < lx < x1:
            o.append(blob([(lx - 9, EDGE_Y), (lx + 9, EDGE_Y), (lx + 9 + 330, EDGE_Y + 210), (lx - 4 + 330, EDGE_Y + 214)], SHADOW, .22))
            o.append(blob(ellipse_pts(lx + 345, EDGE_Y + 220, 36, 15, 10, rot=30), SHADOW, .22))
    if x0 - 600 < BENCH < x1:
        o.append(blob([(BENCH - 140, EDGE_Y - 4), (BENCH + 140, EDGE_Y - 4), (BENCH + 140 + 120, EDGE_Y + 80), (BENCH - 140 + 120, EDGE_Y + 80)],
                      SHADOW, .2))
    for tx, sd in EDGE_TREES:
        if x0 - 900 < tx < x1:
            o.append(blob([(tx - 24, EDGE_Y), (tx + 24, EDGE_Y), (tx + 24 + 520, EDGE_Y + 330), (tx - 24 + 520, EDGE_Y + 334)], SHADOW, .22))
    # солнечные пятна
    for i in range(math.floor(x0 / 300) - 1, math.floor(x1 / 300) + 2):
        rs = rs_(19, i)
        for k in range(2):
            px, py = i * 300 + rs.uniform(0, 300), rs.uniform(PATH_Y0 + 20, PATH_Y1 - 20)
            r = rs.uniform(14, 34)
            o.append(blob(ellipse_pts(px, py, r * 1.6, r * .5, 10, rot=12), "#fff4d6", .55))
    # края дорожки
    o.append(line([(x0, PATH_Y0), (x1, PATH_Y0)], 4.0, INK, taper=.05, wmin=.9, seed=21))
    o.append(f'<rect x="{f(x0)}" y="{f(PATH_Y1)}" width="{f(x1 - x0)}" height="600" fill="#93c063"/>')
    o.append(f'<rect x="{f(x0)}" y="{f(PATH_Y1 + 30)}" width="{f(x1 - x0)}" height="600" fill="#86b75a"/>')
    o.append(line([(x0, PATH_Y1), (x1, PATH_Y1)], 4.0, INK, taper=.05, wmin=.9, seed=22))
    # газон перед дорожкой: кустики травы, клевер, цветочки (едут с землёй)
    for i in range(math.floor(x0 / 120) - 1, math.floor(x1 / 120) + 2):
        rs = rs_(29, i)
        for k in range(3):
            px, py = i * 120 + rs.uniform(0, 120), rs.uniform(PATH_Y1 + 50, 470)
            sc = 0.7 + (py - PATH_Y1) / 300
            col = ["#5f9443", "#6ea54d", "#4f8538"][k % 3]
            for j in (-1, 0, 1):
                o.append(line([(px + j * 6 * sc, py), (px + j * 12 * sc, py - 12 * sc), (px + j * 16 * sc + 3, py - 24 * sc)], 3.4 * sc, col,
                              seed=1200 + (i * 7 + k * 3 + j) % 90, taper=.9, wmin=.1, peak=.15))
        if rs.uniform() < .55:
            px, py = i * 120 + rs.uniform(0, 120), rs.uniform(PATH_Y1 + 70, 460)
            sc = 0.8 + (py - PATH_Y1) / 320
            pc = "#fbf6ea" if rs.uniform() < .6 else "#f6d24a"
            for a in range(5):
                an = a * 2 * math.pi / 5 + rs.uniform(0, 1)
                o.append(blob(ellipse_pts(px + 7 * sc * math.cos(an), py + 5 * sc * math.sin(an), 5 * sc, 3.6 * sc, 6, rot=math.degrees(an)), pc))
            o.append(blob(ellipse_pts(px, py, 3.4 * sc, 2.8 * sc, 6), "#e8a52a" if pc != "#f6d24a" else "#c9771f"))
    # травинки у краёв
    for i in range(math.floor(x0 / 40) - 1, math.floor(x1 / 40) + 2):
        rs = rs_(23, i)
        for yb, col, hh, sg in ((PATH_Y0 + 2, "#6e9f4a", 18, -1), (PATH_Y1 + 3, "#5f9443", 26, -1)):
            px = i * 40 + rs.uniform(0, 40)
            h = hh * rs.uniform(.6, 1.2)
            o.append(line([(px, yb), (px + 3, yb - h * .5), (px + 7, yb - h)], 3.2, col, seed=1100 + i % 60, taper=.9, wmin=.1, peak=.15))
        if rs.uniform() < .35:
            px = i * 40 + rs.uniform(0, 40)
            o.append(blob(ellipse_pts(px, EDGE_Y - 40 + rs.uniform(-20, 20), 5, 4, 6), "#f6efe0"))
            o.append(blob(ellipse_pts(px, EDGE_Y - 40, 2, 2, 5), "#f2c23c"))
    return "".join(o)


def lamp(x, y, seed):
    o = []
    H = 520
    post = [(x - 7, y, 1), (x - 6, y - H + 40), (x + 6, y - H + 40), (x + 7, y, 1)]
    o.append(shape(post, "#2f4a40", blob([(x + 1, y), (x + 9, y), (x + 8, y - H), (x + 1, y - H)], "#1f342c", .9), w=3.4, seed=seed))
    base = [(x - 20, y + 2, 1), (x - 16, y - 40), (x - 9, y - 54), (x + 9, y - 54), (x + 16, y - 40), (x + 20, y + 2, 1)]
    o.append(shape(base, "#2f4a40", blob([(x + 2, y + 4), (x + 22, y + 4), (x + 12, y - 56)], "#1f342c", .9), w=3.4, seed=seed + 1))
    # фонарь
    top = y - H
    gl = [(x - 24, top + 34, 1), (x - 30, top - 26, 1), (x + 30, top - 26, 1), (x + 24, top + 34, 1)]
    o.append(shape(gl, "#f5ecc8", blob([(x + 4, top - 26), (x + 30, top - 26), (x + 24, top + 34), (x + 4, top + 34)], "#e1d3a2", .9) +
                   line([(x - 14, top - 18), (x - 12, top + 26)], 3, "#fffbe8", seed=seed + 5), w=3.2, seed=seed + 2))
    cap = [(x - 40, top - 24, 1), (x, top - 58), (x + 40, top - 24, 1)]
    o.append(shape(cap, "#2f4a40", "", w=3.4, seed=seed + 3))
    o.append(shape(lib.rect_pts(x - 22, top + 32, x + 22, top + 44, 3), "#2f4a40", "", w=3, seed=seed + 4))
    o.append(f'<circle cx="{x}" cy="{top - 64}" r="6" fill="#2f4a40"/>')
    return "".join(o)


def bench(x, y, seed):
    o = []
    W2 = 150
    WOOD, WOOD_SH = "#b9774a", "#8b5535"
    # ножки (чугун)
    for sx in (-1, 1):
        lx = x + sx * (W2 - 26)
        leg = [(lx - 8, y, 1), (lx - 6, y - 128), (lx + 8, y - 128), (lx + 10, y, 1)]
        o.append(shape(leg, "#33343c", "", w=3.2, seed=seed + 2 + sx))
    # спинка
    for k in range(2):
        yy = y - 168 + k * 30
        o.append(shape(lib.rect_pts(x - W2, yy, x + W2, yy + 20, 4), WOOD,
                       blob([(x - W2, yy + 12), (x + W2, yy + 12), (x + W2, yy + 22), (x - W2, yy + 22)], WOOD_SH, .9), w=3.4, seed=seed + 10 + k))
    # сиденье
    for k in range(2):
        yy = y - 98 + k * 18
        o.append(shape(lib.rect_pts(x - W2 - 6, yy, x + W2 + 6, yy + 15, 4), WOOD,
                       blob([(x - W2, yy + 9), (x + W2, yy + 9), (x + W2, yy + 16), (x - W2, yy + 16)], WOOD_SH, .9), w=3.4, seed=seed + 20 + k))
    for sx in (-1, 1):
        lx = x + sx * (W2 - 26)
        o.append(shape(lib.rect_pts(lx - 7, y - 178, lx + 7, y - 66, 3), "#33343c", "", w=3, seed=seed + 30 + sx))
    return "".join(o)


def props_back(cx, s, t):
    x0, x1 = view(cx, s)
    o = []
    for tx, sd in EDGE_TREES:
        if x0 - 500 < tx < x1 + 500:
            o.append(tree(tx, EDGE_Y + 6, 1150, 760, 1300 + sd, ink_w=4.6))
    if x0 - 300 < BENCH < x1 + 300:
        o.append(bench(BENCH, EDGE_Y + 4, 1400))
    for i, lx in enumerate(LAMPS):
        if x0 - 100 < lx < x1 + 100:
            o.append(lamp(lx, EDGE_Y + 2, 1500 + i * 10))
    return "".join(o)


SHADOW_K, SHADOW_M = 0.95, 0.30


def long_shadow(svg_group, gy=0.0):
    """Длинная тень на дорожке: тот же рисунок, сдвинутый по высоте (тень вниз-вправо), одним цветом."""
    fid = "shdF"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">'
                        f'<feColorMatrix type="matrix" values="0 0 0 0 0.227  0 0 0 0 0.247  0 0 0 0 0.388  0 0 0 0.24 0"/>'
                        f'<feGaussianBlur stdDeviation="2.2"/></filter>')
    k, m = SHADOW_K, SHADOW_M
    return (f'<g transform="matrix(1 0 {-k} {-m} {k * gy:.3f} {gy * (1 + m):.3f})"><g filter="url(#{fid})">{svg_group}</g></g>')


def foreground(cx, cy, s, rot, t):
    """Передний план (параллакс 1.35): травы и куст внизу кадра, ниже зоны действия."""
    p = 1.35
    o = []
    sp = 520.0
    off = cx * p
    i0 = math.floor((off - 900) / sp)
    for i in range(i0, i0 + 6):
        rs = rs_(31, i)
        lx = i * sp + rs.uniform(-80, 80)
        x = 540 + (lx - off) * s
        if not -400 < x < 1480:
            continue
        if rs.uniform() < .55:
            w, h = rs.uniform(300, 420), rs.uniform(200, 260)
            y = 1920 + 30
            pts = scallop(x, y - h * .45, w / 2, h / 2, 9, 1600 + i % 70, .2)
            inn = blob(scallop(x + w * .14, y - h * .25, w * .45, h * .38, 7, 1700 + i % 70, .15), G_DEEP, .95)
            inn += blob(scallop(x - w * .18, y - h * .7, w * .25, h * .16, 6, 1800 + i % 70, .2), G_LIT, .95)
            o.append(shape(pts, G_SH, inn, w=5.2, seed=1900 + i % 70))
        else:
            for k in range(9):
                bx = x + rs.uniform(-120, 120)
                h = rs.uniform(150, 280)
                bend = rs.uniform(-40, 40)
                o.append(lib.shape(lib.band([(bx, 1960), (bx + bend * .3, 1960 - h * .5), (bx + bend, 1960 - h)], 18, 3, step=5), G_SH,
                                   "", w=3.6, seed=2000 + i * 10 + k))
    return f'<g transform="rotate({f(rot)} 540 960)">{"".join(o)}</g>'


def light_overlay(t, cx):
    """Лучи солнца сквозь листву: веер от солнца, мерцают по мере того, как кроны проезжают."""
    o = []
    for k in range(6):
        a = math.radians(18 + k * 9.5)
        L = 2300
        wdt = math.radians(1.6 + (k % 3) * .9)
        flick = 0.5 + 0.5 * math.sin(cx * 0.004 + k * 1.7 + t * .6)
        op = 0.09 + 0.10 * flick
        p1 = (SUN[0] + L * math.cos(a - wdt), SUN[1] + L * math.sin(a - wdt))
        p2 = (SUN[0] + L * math.cos(a + wdt), SUN[1] + L * math.sin(a + wdt))
        g = lib.lin_grad([(0, "#fff6d8", 1), (0.55, "#fff6d8", .5), (1, "#fff6d8", 0)], SUN[0], SUN[1],
                         SUN[0] + L * .8 * math.cos(a), SUN[1] + L * .8 * math.sin(a), units="userSpaceOnUse")
        o.append(f'<path d="M{SUN[0]} {SUN[1]}L{f(p1[0])} {f(p1[1])}L{f(p2[0])} {f(p2[1])}Z" fill="url(#{g})" opacity="{op:.3f}"/>')
    # тёплое общее сияние слева сверху
    gw = lib.rad_grad([(0, "#fff0c8", .35), (1, "#fff0c8", 0)], SUN[0], SUN[1], 900)
    o.append(f'<rect x="0" y="0" width="1080" height="1920" fill="url(#{gw})"/>')
    return f'<g style="mix-blend-mode:screen">{"".join(o)}</g>'
