"""Предметы сцены paper рилса 33 (вид сверху на стол): столешница, лист, каракули строк, цифры кодом, рука Димы с ручкой
или маркером (горчичный рукав худи), линейка, маркеры, скомканный черновик, штампы, карточка-стикер с квадратиками,
настольные часы с цифрами, лапа кота, отпечаток лапы, звёздочки, сердечки, искры, свет времени суток.

Всё возвращает SVG в мировых координатах; камера — снаружи (scene.py). Манера — как desk рилса 32: живая тушь ink.py,
плоский цвет с одной тенью. Буквы — только цифры и «/», шрифт MK (Shantell Sans ExtraBold, маркер) из base.html.
"""
import math

import numpy as np

import lib
from lib import INK, blob, clamp, ellipse_pts, line, shape

SKIN, SKIN_SH, SKIN_SH2, NAIL = "#ecc4a2", "#d39f83", "#bf8a74", "#f1cdbd"
TOP, TOP_SH, TOP_SH2, FOLD = "#d4a23e", "#a97b25", "#8c6219", "#6b4a12"
CAT, CAT_SH, CAT_FUR, PAD = "#3a3646", "#211e29", "#56506a", "#e8823a"
PEN_INK = "#2b3f8f"
PAPER, PAPER_SH = "#fbf8f0", "#e9e2d2"
RED = "#d8343a"


def P(p):
    return (float(p[0]), float(p[1]))


# ═════════════════════════ стол ═════════════════════════
def wood(x0=-1600, y0=-1600, w=4400, h=6400):
    if not any('id="pWood33"' in d for d in lib.DEFS):
        lib.DEFS.append('<pattern id="pWood33" width="460" height="168" patternUnits="userSpaceOnUse">'
                        '<rect width="460" height="168" fill="#a8693f"/>'
                        '<path d="M0 36 C130 28 280 48 460 34 M0 92 C150 100 300 78 460 96 M0 136 C120 128 320 146 460 132" fill="none" '
                        'stroke="#8f5733" stroke-width="3"/>'
                        '<path d="M210 60 C240 56 262 66 250 74 C236 82 214 72 210 60Z" fill="none" stroke="#8f5733" stroke-width="2.4"/>'
                        '<rect y="165" width="460" height="3" fill="#6e4224"/></pattern>')
    return f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#pWood33)"/>'


def soft_shadow(pts, dx=16, dy=24, op=.32, sd=10, corners=True):
    return blob([(p[0] + dx, p[1] + dy) + ((1,) if corners else ()) for p in pts], "#1a0c04", op, lib.blur(sd))


def sheet(pts, seed=5000, fold=True):
    """Лист бумаги (углы pts по часовой), тень и лёгкая тень по нижнему краю."""
    q = [P(p) + (1,) for p in pts]
    inner = ""
    if fold:
        a, b = np.array(pts[2], float), np.array(pts[3], float)
        inner = blob([P(a), P(b), P(b + np.array([0, -16])), P(a + np.array([0, -16]))], PAPER_SH, .9)
    return soft_shadow(pts) + shape(q, PAPER, inner, w=4.6, seed=seed)


# ═════════════════════════ каракули строк ═════════════════════════
def scribble(x0, x1, y, seed, h=16.0, pitch=13.0):
    """Строка «письма» без букв: слова — петли разной высоты (трохоида), между словами — отрыв пера.
    Возвращает список штрихов (массивы точек)."""
    rs = np.random.RandomState(seed)
    strokes = []
    x = x0
    while x < x1 - 30:
        L = min(rs.uniform(60, 150), x1 - x)
        n = max(2.0, L / pitch)
        u = np.linspace(0, n, int(n * 14) + 2)
        hv = 1 + .35 * np.sin(u * 1.7 + rs.uniform(0, 6)) + .25 * np.sin(u * 3.1 + rs.uniform(0, 6))
        tall = np.zeros_like(u)
        for _ in range(int(rs.randint(0, 3))):
            c = rs.uniform(.5, n - .5)
            tall += 1.1 * np.exp(-((u - c) / .45) ** 2)
        a = pitch * .42
        xs = x + u * pitch - a * np.sin(2 * math.pi * u)
        ys = y - h * (hv + tall) * .5 * (1 - np.cos(2 * math.pi * u)) * .55 + 2.5 * np.sin(u * .9 + seed)
        strokes.append(np.stack([xs, ys], 1))
        x += L + rs.uniform(16, 26)
    return strokes


def strokes_len(strokes):
    return [float(np.sum(np.linalg.norm(np.diff(s, axis=0), axis=1))) for s in strokes]


def reveal(strokes, frac):
    """Префикс штрихов по доле общей длины: (видимые штрихи, точка пера, перо в воздухе?)."""
    Ls = strokes_len(strokes)
    tot = sum(Ls) or 1
    left = clamp(frac) * tot
    out = []
    tip = strokes[0][0]
    for s, L in zip(strokes, Ls):
        if left >= L:
            out.append(s)
            tip = s[-1]
            left -= L
            continue
        d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(s, axis=0), axis=1))])
        k = min(int(np.searchsorted(d, left)), len(d) - 1)
        if k >= 1:
            u = (left - d[k - 1]) / max(d[k] - d[k - 1], 1e-6)
            q = s[k - 1] + (s[k] - s[k - 1]) * u
            out.append(np.vstack([s[:k], q[None]]))
            tip = q
        else:
            tip = s[0]
        break
    return out, tip


def pen_path(strokes, col, w=3.6, op=1.0):
    o = []
    for s in strokes:
        if len(s) < 2:
            continue
        d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in s)
        oo = f' opacity="{op:.3f}"' if op != 1 else ""
        o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w * lib.INK_K[0]:.2f}" stroke-linecap="round" '
                 f'stroke-linejoin="round"{oo}/>')
    return "".join(o)


def text(x, y, s, size, col, rot=0.0, anchor="middle", font="MK", weight=800, stroke=None, sw=0.0):
    tr = f' transform="rotate({rot:.2f} {x:.1f} {y:.1f})"' if rot else ""
    st = f' stroke="{stroke}" stroke-width="{sw:.1f}" paint-order="stroke" stroke-linejoin="round"' if stroke else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-weight="{weight}" font-size="{size:.1f}" fill="{col}" '
            f'text-anchor="{anchor}" dominant-baseline="central"{st}{tr}>{s}</text>')


# ═════════════════════════ рука с ручкой ═════════════════════════
# Система кисти: острие пера в (0, 0), ось пера — +x (от острия к хвосту), кисть лежит на стороне −y.
# В мире группа: translate(tip) rotate(ang) scale(k); ang ≈ 30° — хвост пера и рукав уходят вправо-вниз.
HAND_BACK = [(98, -42), (104, -64), (128, -80), (164, -88), (204, -82), (238, -60), (252, -22), (246, 14), (224, 38), (186, 48), (148, 46),
             (126, 36), (112, 12)]
INDEX = [(150, -44), (120, -34), (92, -20), (66, -9), (46, -4)]
THUMB = [(160, 40), (126, 36), (96, 26), (68, 15), (50, 9)]
CURL = []


def _rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


def tool_svg(kind, col, cap=True):
    """Ручка (kind='pen', col — цвет корпуса) или маркер (kind='marker', col — цвет чернил) в системе кисти."""
    o = []
    if kind == "pen":
        o.append(shape([(0, 0, 1), (26, -5.5), (30, -7, 1), (30, 7, 1), (26, 5.5)], "#c9ccd6",
                       blob([(4, 0), (26, 2), (26, 5.5)], "#9aa0ae"), w=2.4, seed=5101))
        o.append(f'<circle cx="2" cy="0" r="2.2" fill="{INK}"/>')
        body = [(30, -8, 1), (214, -8, 1), (222, -5), (224, 0), (222, 5), (214, 8, 1), (30, 8, 1)]
        o.append(shape(body, col, blob([(30, 2), (214, 2), (214, 8), (30, 8)], lib.mix(col, "#000000", .3), .9) +
                       blob([(36, -7), (70, -7), (70, 8), (36, 8)], "#2a2a34", .9), w=2.8, seed=5102))
        o.append(line([(80, -4), (200, -4)], 2.6, "#ffffff", taper=.1, wmin=.7, seed=5103, op=.45))
        o.append(shape([(176, -10, 1), (218, -10, 1), (218, -4, 1), (176, -4, 1)], "#d8dbe4", "", w=2, seed=5104))
    else:
        o.append(shape([(0, -3, 1), (14, -7, 1), (22, -9, 1), (22, 9, 1), (14, 7, 1), (0, 3, 1)], col, "", w=2.4, seed=5111))
        body = [(22, -12, 1), (190, -12, 1), (196, -8), (198, 0), (196, 8), (190, 12, 1), (22, 12, 1)]
        o.append(shape(body, "#f4f1ea", blob([(22, 3), (190, 3), (190, 12), (22, 12)], "#d9d4c8", .9) +
                       blob([(60, -12), (110, -12), (110, 12), (60, 12)], col), w=2.8, seed=5112))
        if cap:
            o.append(shape([(196, -14, 1), (250, -14, 1), (256, -8), (258, 0), (256, 8), (250, 14, 1), (196, 14, 1)], col,
                           blob([(196, 4), (256, 4), (256, 14), (196, 14)], lib.mix(col, "#000000", .25), .9), w=2.8, seed=5113))
    return "".join(o)


def hand(tip, ang, k=1.0, tool="pen", col="#3b6fd8", lift=0.0, curl=0.0, arm_len=1200, arm_bend=-4.0, seed=0):
    """Правая рука Димы сверху: кисть держит ручку/маркер, рукав худи уходит вправо-вниз.
    lift — перо в воздухе (кисть чуть крупнее, тень дальше); arm_bend — поворот предплечья от оси кисти (град)."""
    k = k * (1 + .035 * lift)
    old = lib.INK_K[0]
    lib.INK_K[0] = old / k
    try:
        o = []
        # предплечье в рукаве: от запястья по направлению arm_bend
        wr = np.array([246.0, -18.0])
        d = _rot(np.array([1.0, -.12]), math.radians(arm_bend))
        d /= np.linalg.norm(d)
        n = np.array([-d[1], d[0]])
        far = wr + d * arm_len
        cuff0, cuff1 = wr - d * 6, wr + d * 40
        slv = [P(cuff1 - n * 60) + (1,), P(far - n * 74) + (1,), P(far + n * 74) + (1,), P(cuff1 + n * 58) + (1,)]
        sl_in = blob([P(cuff1 + n * 18), P(far + n * 26), P(far + n * 74), P(cuff1 + n * 58)], TOP_SH, .85)
        for j, u in enumerate((.12, .3, .52)):
            c = cuff1 + (far - cuff1) * u
            sl_in += line([P(c - n * 50 + d * 10), P(c - n * 10 - d * 4), P(c + n * 30 + d * 14)], 2.6, FOLD, seed=seed + 5150 + j, op=.8)
        # кисть
        hb = [P(p) for p in HAND_BACK]
        curls = []
        for (c, rx, ry, rot) in CURL:
            pts = ellipse_pts(c[0], c[1], rx, ry, 14, rot=rot)
            curls.append(shape(pts, SKIN, blob(ellipse_pts(c[0] + 4, c[1] + 6, rx * .8, ry * .6, 10, rot=rot), SKIN_SH, .7), w=3.2,
                               seed=seed + 5160 + len(curls)))
        idx = lib.band(INDEX, 36, 27, step=2.5, cap=True)
        idx_in = blob(lib.band(INDEX[1:], 12, 9, step=3, cap=False), SKIN_SH, .55)
        idx_in += line([(100, -31), (98, -22), (100, -12)], 1.6, SKIN_SH2, seed=seed + 5170, op=.8)
        nc = (54, -5)
        idx_in += blob(ellipse_pts(nc[0], nc[1], 9, 7.5, 10, rot=-8), NAIL)
        th = lib.band(THUMB, 38, 27, step=2.5, cap=True)
        th_in = blob([(p[0], p[1] + 6) for p in lib.band(THUMB[1:], 12, 8, step=3, cap=False)], SKIN_SH, .6)
        th_in += blob(ellipse_pts(58, 13, 9, 7, 10, rot=-14), NAIL)
        back_in = blob([(110, 8), (250, -8), (252, 20), (230, 44), (130, 44)], SKIN_SH, .75)
        back_in += "".join(line([(150 + j * 24, -58 - j * 6), (156 + j * 26, -46 - j * 6)], 2, SKIN_SH2, seed=seed + 5180 + j, op=.75)
                           for j in range(3))
        back_in += "".join(line([(170, -40 + j * 16), (226, -34 + j * 18)], 1.4, SKIN_SH2, seed=seed + 5190 + j, op=.45) for j in range(3))
        o.append("".join(curls))
        o.append(tool_svg(tool, col))
        o.append(shape(th, SKIN, th_in, w=3.0, seed=seed + 5120))
        o.append(shape(idx, SKIN, idx_in, w=3.0, seed=seed + 5121))
        o.append(shape(hb + [(110, -16)], SKIN, back_in, w=3.4, seed=seed + 5122, ink=False))
        o.append(line(hb[1:12], 3.4, seed=seed + 5123, taper=.25, wmin=.55))
        o.append(line([(124, 32), (116, 18), (114, 4)], 2.6, seed=seed + 5124, taper=.5, wmin=.3))      # складка у большого пальца
        o.append(shape(slv, TOP, sl_in, w=4.6, seed=seed + 5130))
        cf = lib.band([P(cuff0), P(cuff1 + d * 4)], 118, 122, step=3, cap=False)
        rib = "".join(line([P(cuff0 + d * (6 + j * 6) - n * 57), P(cuff0 + d * (6 + j * 6) + n * 57)], 1.6, TOP_SH2, seed=seed + 5140 + j, op=.8)
                      for j in range(6))
        o.append(shape(cf, TOP_SH, rib, w=4.2, seed=seed + 5131))
        g = f'<g transform="translate({tip[0]:.2f} {tip[1]:.2f}) rotate({ang:.2f}) scale({k:.4f})">{"".join(o)}</g>'
        # тень на столе — в мире, свет сверху-слева
        sh_loc = hb[:11] + [P(cuff1 + n * 60), P(far + n * 74), P(far - n * 74), P(cuff1 - n * 60)]
        sh = lib.T(sh_loc, tip[0], tip[1], k, ang)
        off = 14 + 26 * lift
        shadow = blob([(x + off, y + off * 1.5) for x, y in sh], "#1a0c04", .28, lib.blur(9 + 6 * lift))
        tl = lib.T([(30, 0), (224, 0)], tip[0], tip[1], k, ang)
        pshadow = line([(tl[0][0] + 6 + off * .6, tl[0][1] + 10 + off * .6), (tl[1][0] + off, tl[1][1] + off * 1.4)], 9 * k, "#1a0c04", taper=.1,
                       wmin=.8, seed=5199, op=.22)
        return shadow + pshadow + g
    finally:
        lib.INK_K[0] = old


# ═════════════════════════ мелочи на столе ═════════════════════════
def star_pts(cx, cy, r, rot=0.0, n=5, inner=.45):
    out = []
    for i in range(n * 2):
        a = math.radians(rot - 90 + i * 180 / n)
        rr = r if i % 2 == 0 else r * inner
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a), 1))
    return out


def star(cx, cy, r, col="#f4c430", rot=0.0, seed=5300, w=3.0):
    if r <= .5:
        return ""
    sh = lib.mix(col, "#000000", .18)
    pts = star_pts(cx, cy, r, rot)
    return shape(pts, col, blob([(cx, cy)] + [p[:2] for p in star_pts(cx, cy, r, rot)[3:7]], sh, .8), w=w, seed=seed)


def heart_pts(cx, cy, r, rot=0.0):
    pts = []
    for a in np.linspace(0, 2 * math.pi, 26, endpoint=False):
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x / 16 * r, y / 16 * r))
    return lib.T(pts, cx, cy, 1, rot)


def heart(cx, cy, r, col="#ef5b8c", rot=0.0, seed=5320, w=3.0):
    if r <= .5:
        return ""
    pts = heart_pts(cx, cy, r, rot)
    return shape(pts, col, blob(ellipse_pts(cx - r * .38, cy - r * .32, r * .18, r * .12, 8, rot=-30), "#ffffff", .8), w=w, seed=seed)


def glint(cx, cy, r, col="#fff6c8", rot=0.0, op=1.0):
    """Четырёхлучевая искра (блик)."""
    if r <= .5 or op <= 0:
        return ""
    pts = []
    for i in range(8):
        a = math.radians(rot - 90 + i * 45)
        rr = r if i % 2 == 0 else r * .22
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<path d="{lib.fill_d([p + (1,) for p in pts])}" fill="{col}"{o}/>'


def burst(cx, cy, u, r0, r1, n=10, col="#3a2a22", w=6.0, seed=5400, rot=0.0):
    """Штрихи удара разлетаются от центра (u 0..1)."""
    if u <= 0 or u >= 1:
        return ""
    o = []
    rs = np.random.RandomState(seed)
    for j in range(n):
        a = math.radians(rot + j * 360 / n + rs.uniform(-8, 8))
        e = 1 - (1 - u) ** 2
        a0 = r0 + (r1 - r0) * e
        L = (r1 - r0) * .35 * (1 - u) + 6
        o.append(line([(cx + a0 * math.cos(a), cy + a0 * math.sin(a)), (cx + (a0 + L) * math.cos(a), cy + (a0 + L) * math.sin(a))], w, col,
                      taper=.3, wmin=.4, seed=seed + j))
    return "".join(o)


def ruler(cx, cy, L=620, w=70, rot=0.0, seed=5500):
    pts = [(-L / 2, -w / 2, 1), (L / 2, -w / 2, 1), (L / 2, w / 2, 1), (-L / 2, w / 2, 1)]
    inner = blob([(-L / 2, w * .18), (L / 2, w * .18), (L / 2, w / 2), (-L / 2, w / 2)], "#c9b98f", .5)
    for i in range(int(L / 20) + 1):
        x = -L / 2 + 14 + i * 20
        if x > L / 2 - 8:
            break
        hh = 22 if i % 5 == 0 else 12
        inner += f'<rect x="{x - 1.1:.1f}" y="{-w / 2:.1f}" width="2.2" height="{hh}" fill="#4a3a2a"/>'
    g = shape(pts, "#f3e3b0", inner, w=3.4, seed=seed)
    sh = soft_shadow(lib.T([p[:2] for p in pts], cx, cy, 1, rot), 10, 14, .25, 6)
    return sh + f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f})">{g}</g>'


def marker_lying(cx, cy, rot, col, seed=5600, k=1.0):
    g = tool_svg("marker", col)
    tip = lib.T([(0, 0), (258, 0)], 0, 0, k, rot)
    sh = line([(cx + tip[0][0] + 8, cy + tip[0][1] + 14), (cx + tip[1][0] + 8, cy + tip[1][1] + 14)], 26 * k, "#1a0c04", taper=.05, wmin=.9,
              seed=seed, op=.25)
    return sh + f'<g transform="translate({cx - 129 * k * math.cos(math.radians(rot)):.1f} {cy - 129 * k * math.sin(math.radians(rot)):.1f}) ' \
                f'rotate({rot:.2f}) scale({k:.3f})">{g}</g>'


def pen_lying(cx, cy, rot, col="#3b6fd8", k=1.0, seed=5610):
    g = tool_svg("pen", col)
    a = math.radians(rot)
    x0, y0 = cx - 112 * k * math.cos(a), cy - 112 * k * math.sin(a)
    sh = line([(x0 + 8, y0 + 12), (x0 + 224 * k * math.cos(a) + 8, y0 + 224 * k * math.sin(a) + 12)], 14 * k, "#1a0c04", taper=.05, wmin=.9,
              seed=seed, op=.25)
    return sh + f'<g transform="translate({x0:.1f} {y0:.1f}) rotate({rot:.2f}) scale({k:.3f})">{g}</g>'


def crumpled(cx, cy, r, rot=0.0, seed=5700):
    """Скомканный лист: неровный ком с гранями-складками."""
    rs = np.random.RandomState(seed)
    n = 13
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * rs.uniform(.82, 1.08)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a), 1 if i % 3 == 0 else 0))
    pts = [p if p[2] else p[:2] for p in pts]
    inner = blob([(cx - r * .2, cy - r * .1), (cx + r * 1.2, cy - r * .3), (cx + r * 1.2, cy + r * 1.2), (cx - r * .4, cy + r * 1.2)], PAPER_SH, .9)
    for j in range(7):
        a = rs.uniform(0, 2 * math.pi)
        b = a + rs.uniform(.6, 1.6)
        r0, r1 = rs.uniform(.1, .45) * r, rs.uniform(.6, .95) * r
        p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        pm = (cx + (r0 + r1) / 2 * math.cos((a + b) / 2) + rs.uniform(-8, 8), cy + (r0 + r1) / 2 * math.sin((a + b) / 2))
        p1 = (cx + r1 * math.cos(b), cy + r1 * math.sin(b))
        inner += line([p0, pm, p1], 2.4, "#b8ae98", seed=seed + 10 + j, taper=.5, wmin=.3)
    for j in range(3):          # обрывки каракулей на комке
        y = cy - r * .35 + j * r * .3
        inner += line([(cx - r * .5, y), (cx - r * .1, y - 5), (cx + r * .3, y + 3)], 2.2, PEN_INK, seed=seed + 30 + j, op=.55, taper=.4)
    sh = soft_shadow(ellipse_pts(cx, cy, r, r, 14), 12, 18, .3, 8, corners=False)
    return sh + f'<g transform="rotate({rot:.1f} {cx} {cy})">{shape(pts, PAPER, inner, w=4.2, seed=seed)}</g>'


def check(x, y, s, frac, col=PEN_INK, w=9.0):
    """Галочка, нарисованная ручкой: frac 0..1 — доля штриха."""
    pts = np.array([(x - 26 * s, y - 2 * s), (x - 8 * s, y + 20 * s), (x + 34 * s, y - 36 * s)])
    st, tip = reveal([np.vstack([np.linspace(pts[0], pts[1], 8), np.linspace(pts[1], pts[2], 14)[1:]])], frac)
    return pen_path(st, col, w * s), tip


def box(x, y, s, frac=1.0, col=PEN_INK, seed=5800):
    """Пустой квадратик (нарисован ручкой, чуть неровный): frac — доля обвода."""
    h = 30 * s
    rs = np.random.RandomState(seed)
    c = [(x - h + rs.uniform(-2, 2), y - h + rs.uniform(-2, 2)), (x + h + rs.uniform(-2, 2), y - h + rs.uniform(-2, 2)),
         (x + h + rs.uniform(-2, 2), y + h + rs.uniform(-2, 2)), (x - h + rs.uniform(-2, 2), y + h + rs.uniform(-2, 2))]
    path = np.vstack([np.linspace(c[i], c[(i + 1) % 4], 10)[:-1] for i in range(4)] + [np.array([c[0]]) + np.array([[3, 1]])])
    st, tip = reveal([path], frac)
    return pen_path(st, col, 5.2 * s), tip


# ═════════════════════════ часы ═════════════════════════
def clock(cx, cy, minutes, k=1.0, roll=0.0, seed=5900, icon="sun", icon_t=0.0):
    """Настольные электронные часы (вид сверху-спереди): корпус, экран с ЧЧ:ММ. minutes — минуты суток (float);
    roll — вертикальная прокрутка цифр часа (0..1 — доля перехода к следующему часу). icon — sun / dusk."""
    o = []
    bw, bh = 300 * k, 170 * k
    body = lib.rect_pts(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2, 34 * k)
    o.append(soft_shadow([p[:2] for p in body], 14, 22, .3, 9))
    o.append(shape(body, "#4f8f8a", blob([(cx - bw / 2, cy + bh * .12), (cx + bw / 2, cy + bh * .12), (cx + bw / 2, cy + bh / 2),
                                          (cx - bw / 2, cy + bh / 2)], "#3c706c", .9), w=4.6, seed=seed))
    # ножки-кнопки сверху
    for sx in (-1, 1):
        o.append(shape(lib.rect_pts(cx + sx * 70 * k - 26 * k, cy - bh / 2 - 16 * k, cx + sx * 70 * k + 26 * k, cy - bh / 2 + 4 * k, 6 * k),
                       "#e0a93a", "", w=3.2, seed=seed + 1 + sx))
    sx0, sy0, sx1, sy1 = cx - bw / 2 + 26 * k, cy - bh / 2 + 24 * k, cx + bw / 2 - 26 * k, cy + bh / 2 - 34 * k
    scr = lib.rect_pts(sx0, sy0, sx1, sy1, 14 * k)
    cid = lib.clip_of(scr)
    h = int(minutes // 60) % 24
    m = int(minutes % 60)
    fs = 74 * k
    ty = (sy0 + sy1) / 2 + 2 * k
    hx = sx0 + (sx1 - sx0) * .3
    mx = sx0 + (sx1 - sx0) * .74
    inner = []
    dy = roll * (sy1 - sy0)
    inner.append(text(hx, ty - dy, f"{h:02d}", fs, "#b8ff8a", font="IDB", weight=900))
    if roll > 0:
        inner.append(text(hx, ty - dy + (sy1 - sy0), f"{(h + 1) % 24:02d}", fs, "#b8ff8a", font="IDB", weight=900))
    inner.append(text(mx, ty, f"{m:02d}", fs, "#b8ff8a", font="IDB", weight=900))
    inner.append(text((sx0 + sx1) / 2 + 2 * k, ty - 4 * k, ":", fs * .9, "#b8ff8a", font="IDB", weight=900))
    inner.append(blob([(sx0, sy0), (sx1, sy0), (sx1 - 60 * k, sy0 + 26 * k), (sx0, sy0 + 30 * k)], "#ffffff", .12))
    o.append(shape(scr, "#1d2a24", f'<g clip-path="url(#{cid})">{"".join(inner)}</g>', w=3.6, seed=seed + 5))
    # значок времени суток справа снизу
    ix, iy = cx + bw / 2 - 40 * k, cy + bh / 2 - 17 * k
    if icon == "sun":
        for j in range(8):
            a = math.radians(j * 45 + icon_t * 40)
            o.append(line([(ix + 13 * k * math.cos(a), iy + 13 * k * math.sin(a)), (ix + 19 * k * math.cos(a), iy + 19 * k * math.sin(a))],
                          3.2 * k, "#ffd23a", taper=.1, wmin=.8, seed=seed + 10 + j))
        o.append(shape(ellipse_pts(ix, iy, 9 * k, 9 * k, 12), "#ffd23a", "", w=2.4, seed=seed + 20))
    else:
        o.append(shape(ellipse_pts(ix, iy, 11 * k, 11 * k, 14), "#ff8a3a", blob([(ix - 14 * k, iy + 2 * k), (ix + 14 * k, iy + 2 * k),
                                                                                (ix + 14 * k, iy + 14 * k), (ix - 14 * k, iy + 14 * k)],
                                                                               "#4f8f8a"), w=2.4, seed=seed + 21))
    o.append(blob([(cx - bw / 2 + 30 * k, cy + bh / 2 - 22 * k), (cx - bw / 2 + 120 * k, cy + bh / 2 - 22 * k),
                   (cx - bw / 2 + 120 * k, cy + bh / 2 - 12 * k), (cx - bw / 2 + 30 * k, cy + bh / 2 - 12 * k)], "#3c706c"))
    return "".join(o)


# ═════════════════════════ лапа кота ═════════════════════════
def paw(tip, ang, k=1.0, pads=True, press=0.0, seed=6000, length=700):
    """Передняя лапа кота сверху: tip — центр стопы, ang — направление ОТ стопы к плечу (лапа входит из-за края).
    pads=True — стопа повёрнута подушечками к зрителю (поднята), иначе — вид сверху (пальцы-бугорки).
    press — 0..1 сплющивание при нажатии."""
    old = lib.INK_K[0]
    lib.INK_K[0] = old / k
    try:
        o = []
        sq = 1 + .12 * press
        # лапа в локальной системе: стопа в (0,0), плечо — по +x
        leg = [(30, -46), (length * .5, -56), (length, -64), (length, 64), (length * .5, 56), (30, 46)]
        leg_in = blob([(30, 14), (length, 20), (length, 64), (30, 46)], CAT_SH, .85)
        for j in range(4):
            x = 120 + j * 120
            leg_in += line([(x, -40 + (j % 2) * 10), (x + 26, -30 + (j % 2) * 10)], 2.2, CAT_FUR, seed=seed + 10 + j, op=.8)
            leg_in += line([(x + 50, 18), (x + 72, 26)], 2.2, CAT_FUR, seed=seed + 20 + j, op=.6)
        foot = []
        rx, ry = 74 * sq, 66 * sq
        for a in np.linspace(0, 2 * math.pi, 22, endpoint=False):
            x, y = rx * math.cos(a), ry * math.sin(a)
            if math.cos(a) < -.2:          # пальцы впереди — волнистый край
                x -= 6 * abs(math.sin(a * 4))
            foot.append((x, y))
        foot_in = blob(ellipse_pts(10, 20, rx * .9, ry * .6, 14), CAT_SH, .55)
        if pads:
            foot_in += shape([(-8, -30), (34, -26), (40, 0), (34, 28), (-8, 32), (-22, 0)], PAD, "", w=2.6, seed=seed + 30)
            for j, yy in enumerate((-44, -15, 15, 44)):
                xx = -46 + abs(yy) * .32
                foot_in += shape(ellipse_pts(xx, yy, 13 * sq, 11.5 * sq, 10), PAD, "", w=2.4, seed=seed + 31 + j)
        else:
            for yy in (-26, 2, 30):
                foot_in += line([(-rx + 4, yy), (-rx + 30, yy * .9)], 3, CAT_SH, seed=seed + 40 + yy, taper=.4, wmin=.3)
            foot_in += line([(-50, -40), (-30, -50), (0, -54)], 2.6, CAT_FUR, seed=seed + 50, op=.8)
        g = [shape([P(p) for p in leg], CAT, leg_in, w=4.6, seed=seed + 1),
             shape(foot, CAT, foot_in, w=4.6, seed=seed + 2)]
        # шерстинки у запястья
        for j, yy in enumerate((-58, 58)):
            g.append(line([(46, yy * .95), (30, yy * 1.08), (60, yy * 1.0)], 3, INK, seed=seed + 60 + j, taper=.5, wmin=.3))
        sh_loc = [(-70, -60), (length, -64), (length, 64), (-70, 60)]
        off = 12 + 40 * (1 - press) * (1 if pads else .6)
        sh = blob([(x + off, y + off * 1.4) for x, y in lib.T(sh_loc, tip[0], tip[1], k, ang)], "#1a0c04", .26, lib.blur(10))
        return sh + f'<g transform="translate({tip[0]:.2f} {tip[1]:.2f}) rotate({ang:.2f}) scale({k:.4f})">{"".join(g)}</g>'
    finally:
        lib.INK_K[0] = old


def paw_print(cx, cy, s, rot=0.0, col=PAD, op=1.0, seed=6100):
    pts_main = lib.T([(-26, -10), (0, -22), (26, -10), (30, 14), (14, 26), (0, 22), (-14, 26), (-30, 14)], cx, cy, s, rot)
    o = [shape(pts_main, col, "", w=3.0, seed=seed, ink_color=lib.mix(col, "#000000", .45))]
    for j, (x, y) in enumerate([(-34, -30), (-12, -44), (12, -44), (34, -30)]):
        q = lib.T([(x, y)], cx, cy, s, rot)[0]
        o.append(shape(ellipse_pts(q[0], q[1], 10 * s, 12 * s, 10, rot=rot + (x * .8)), col, "", w=2.6, seed=seed + 1 + j,
                       ink_color=lib.mix(col, "#000000", .45)))
    g = "".join(o)
    return f'<g opacity="{op:.3f}">{g}</g>' if op < 1 else g


# ═════════════════════════ свет ═════════════════════════
def light(mode_u, cx=200, cy=200):
    """Экранный свет: mode_u 0 — день (тёплый белый слева сверху), 1 — вечер (оранжевый, темнее, лампа)."""
    u = clamp(mode_u)
    o = []
    g = lib.rad_grad([(0, "#fff4d6", .42 * (1 - u)), (.6, "#fff0c8", .12 * (1 - u)), (1, "#fff0c8", 0)], cx, cy, 1300, 1300)
    o.append(f'<rect width="1080" height="1920" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    if u > 0:
        o.append(f'<rect width="1080" height="1920" fill="#ff9a50" opacity="{.38 * u:.3f}" style="mix-blend-mode:multiply"/>')
        g2 = lib.rad_grad([(0, "#ffd08a", .35 * u), (.55, "#ffb060", .12 * u), (1, "#ffb060", 0)], 760, 520, 900, 900)
        o.append(f'<rect width="1080" height="1920" fill="url(#{g2})" style="mix-blend-mode:screen"/>')
    g3 = lib.rad_grad([(0, "#0a0c1e", 0), (.55, "#0a0c1e", 0), (1, "#140a06", .38 + .25 * u)], 540, 760, 1100, 1350)
    o.append(f'<rect width="1080" height="1920" fill="url(#{g3})"/>')
    return "".join(o)
