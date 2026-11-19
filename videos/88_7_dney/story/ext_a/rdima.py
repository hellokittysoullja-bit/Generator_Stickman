"""Рилс 82, группа C: Дима на бегу (копия run/dima.py рилса 40) + новые части хука: босая ступня, нога в носке,
ботинок в руке (pose["held_shoe"]), бутерброд в зубах (expr["sandwich"]). Исходно — Дима для сцены stairs рилса 24: тот же герой, что в рилсе 23 (голова, волосы, лицо, мешки, щетина —
перенесены из 23_vybor/story/room/chars_src/heroes23.py), тело — худи горчичного цвета, джинсы, кеды.

Скелет считается в мировых координатах (pose()), рисунок — в «единицах головы» (L: голова ~300, как в 23) и
масштабируется BS. Профиль вправо: ближние к зрителю — левые рука и нога (рисуются последними), дальние — темнее.
"""
import math

import numpy as np

import lib
from lib import INK, band, blob, ellipse_pts, fill_d, ink_closed, ink_open

BS = 0.44                      # L-единицы → мир
LWK = 1.45                     # толщина линий героя относительно 23-го (он здесь мельче в кадре)

SKIN, SKIN_SH, SKIN_SH2 = "#ecc4a2", "#d39f83", "#bf8a74"
HAIR, HAIR_SH, HAIR_HI = "#5a3826", "#3d2418", "#7a5038"
HOOD, HOOD_SH, HOOD_SH2, FOLD = "#d4a23e", "#a97b25", "#8c6219", "#6b4a12"
JEANS, JEANS_SH, JEANS_SEAM = "#454b5c", "#30343f", "#666d80"
SHOE, SHOE_SH, SOLE, SOLE_SH = "#f7f5f0", "#d6d1c7", "#ebe6db", "#bfb8aa"
FAR = (0.80, 0.80, 0.88)

# длины (L-единицы)
THIGH, SHIN, AH = 310.0, 300.0, 62.0          # бедро, голень, высота лодыжки над подошвой
UPPER, FORE = 265.0, 230.0                    # плечо, предплечье (до запястья)
TORSO = 400.0                                 # таз → плечевой сустав
HEEL, TOE = 64.0, 158.0                       # от лодыжки назад до пятки и вперёд до носка (по подошве)


def W(x):
    return x * LWK


def shape(pts, fill, inner="", w=5.0, seed=0, ink=True, var=0.28, weight=0.45):
    return lib.shape(pts, fill, inner, w=W(w), seed=seed, ink=ink, var=var, weight=weight)


def line(pts, w=4.0, color=INK, taper=0.6, wmin=0.12, seed=3, peak=0.5, op=1.0):
    return lib.line(pts, W(w), color, taper=taper, wmin=wmin, seed=seed, peak=peak, op=op)


def far_c(h, far):
    if not far:
        return h
    if h in (SKIN, SKIN_SH, SKIN_SH2):
        return lib.mul(h, (0.93, 0.9, 0.93))
    return lib.mul(h, FAR)


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


def P(p):
    return (float(p[0]), float(p[1]))


# ═════════════════════════════ ГОЛОВА (из рилса 23, лицо 3/4 вправо) ═════════════════════════════
EYE_N = (16, -12, 50, 51)
EYE_F = (92, -10, 39, 47)
FACE = [(-30, -120), (40, -116), (86, -86), (106, -44), (110, -22), (118, 4), (120, 18), (112, 42), (108, 64), (90, 96),
        (62, 116), (30, 126), (2, 124), (-30, 112), (-60, 88), (-88, 46), (-104, -10), (-98, -70), (-68, -108)]
HAIR_PTS = [(108, -40), (104, -78), (82, -110), (94, -152, 1), (52, -128), (36, -172, 1), (8, -138), (-18, -180, 1), (-40, -136),
            (-86, -164, 1), (-90, -128), (-144, -130, 1), (-112, -96), (-158, -78, 1), (-118, -64), (-142, -34, 1), (-104, -38),
            (-94, -14, 1), (-80, -42), (-62, -70), (-22, -88), (12, -92), (30, -76, 1), (50, -98), (80, -86, 1), (98, -62), (108, -40, 1)]


def _bounce(pts, b, y0=-96.0, k=70.0):
    """Пряди прыгают: точки выше линии y0 сдвигаются на b, пропорционально высоте над ней (кончики сильнее)."""
    out = []
    for p in pts:
        x, y = p[0], p[1]
        if y < y0:
            u = min(1.6, (y0 - y) / k)
            y = y + b * u
            x = x - b * 0.25 * u
        out.append((x, y) + ((1,) if len(p) > 2 and p[2] else ()))
    return out


def head(expr):
    """Рилс 83: expr["age"] — возраст (common/aging.py); без age — прежняя голова."""
    global HAIR, HAIR_SH, HAIR_HI
    if expr.get("age") is None:
        return _head(expr)
    import aging
    keep = (HAIR, HAIR_SH, HAIR_HI)
    HAIR, HAIR_SH, HAIR_HI = aging.colors(expr["age"], *keep)
    try:
        return _head(expr)
    finally:
        HAIR, HAIR_SH, HAIR_HI = keep


def _head(expr):
    """expr: lid (0 — усталые полуприкрытые, 1 — широко), look (dx, dy) зрачков, brows, mouth, hair (прыжок прядей)."""
    lidk = expr.get("lid", 0.3)
    lx, ly = expr.get("look", (0.3, 0.0))
    hb = expr.get("hair", 0.0)
    s = []
    back_hair = _bounce([(-60, -110), (-110, -86), (-150, -40, 1), (-122, -30), (-140, 10, 1), (-108, 6), (-100, 40, 1), (-80, 20),
                         (-70, -40)], hb * .6, y0=-20, k=60)
    s.append(shape(back_hair, HAIR_SH, line([(-120, -50), (-100, -20)], 2.4, "#2a170f", seed=149, op=.8), w=4.8, seed=150))
    ear = [(-84, -18), (-108, -30), (-128, -8), (-126, 26), (-112, 50), (-92, 54), (-82, 44)]
    s.append(shape(ear, SKIN, blob([(-128, -8), (-126, 26), (-112, 50), (-112, 14)], SKIN_SH, .9), w=4.8, seed=151))
    s.append(line([(-96, 34), (-116, 22), (-114, -4), (-100, -14)], 3.2, seed=152))
    s.append(line([(-104, 6), (-96, 14), (-100, 24)], 2.4, seed=158, op=.8))
    inner = []
    inner.append(blob([(-110, -130), (-36, -130), (-58, -40), (-54, 40), (-20, 130), (-110, 130)], SKIN_SH, .95))
    inner.append(blob([(-60, -60), (-34, -66), (-40, -20), (-62, -10)], SKIN_SH2, .5))
    inner.append(blob([(70, 40), (112, 42), (106, 70), (80, 74)], SKIN_SH, .55))
    inner.append(blob([(-20, 104), (40, 118), (96, 92), (110, 140), (-30, 140)], SKIN_SH, .85))
    age = expr.get("age")
    stb = 1.0 if age is None else __import__("aging").stubble(age)
    if stb > .01:
        inner.append(blob([(-60, 70), (-20, 92), (30, 106), (80, 94), (106, 70), (110, 130), (-60, 130)], "#9e8a96", .42 * stb))
    rs = np.random.RandomState(7)
    for _ in range(120):
        x, y = rs.uniform(-56, 108), rs.uniform(70, 124)
        if (x - 30) ** 2 / 92 ** 2 + (y - 56) ** 2 / 70 ** 2 > 1.0 or y > 120 - abs(x - 30) * .15:
            continue
        r_ = rs.uniform(1.2, 2.2)
        if stb > .01:
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_:.1f}" fill="#5c4446" opacity="{.55 * stb:.3f}"/>')
    inner.append(blob(ellipse_pts(54, -10, 100, 62, 14), "#d9a08f", .3))
    s.append(shape(FACE, SKIN, "".join(inner), w=5.6, seed=153))
    s.append(line([(-66, 70), (-30, 104), (6, 118)], 2.4, SKIN_SH2, seed=159, op=.8))
    if age is not None:
        import aging
        s.append(aging.wrinkles(age, SKIN_SH2, line))
        s.append(aging.beard(age, HAIR, HAIR_SH, shape, line))
    s.append(line([(30, 112), (44, 116), (56, 112)], 2.6, seed=167, op=.75))
    for (cx, cy, rx, ry, sd) in [(*EYE_N, 154), (*EYE_F, 155)]:
        bag = [(cx - rx * .85, cy + ry * .55), (cx, cy + ry * 1.38), (cx + rx * .85, cy + ry * .55), (cx, cy + ry * .9)]
        bg_ = 1.0 if age is None else __import__("aging").bags(age)
        s.append(blob(bag, "#a77f8c", .78 * bg_))
        s.append(line([(cx - rx * .8, cy + ry * .7), (cx, cy + ry * 1.36), (cx + rx * .75, cy + ry * .75)], 3.3, seed=sd, op=max(.25, bg_)))
        if sd == 154 and bg_ > .5:
            s.append(line([(cx - rx * .5, cy + ry * 1.27), (cx + rx * .05, cy + ry * 1.62), (cx + rx * .5, cy + ry * 1.32)], 2.2,
                          seed=sd + 5, op=.75))
    for nm, (cx, cy, rx, ry), sd in [("F", EYE_F, 160), ("N", EYE_N, 161)]:
        ep = ellipse_pts(cx, cy, rx, ry, 14)
        cid = lib.clip_of(ep)
        s.append(f'<g><path d="{fill_d(ep)}" fill="#f6f2ea"/><g clip-path="url(#{cid})">')
        s.append(blob([(cx - rx, cy - ry), (cx + rx, cy - ry), (cx + rx, cy - ry * .2), (cx - rx, cy - ry * .25)], "#d9d2e2", .8))
        px, py = cx + rx * lx, cy + ry * ly
        s.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="7.4" ry="8.2" fill="{INK}"/>'
                 f'<circle cx="{px - 2.4:.1f}" cy="{py - 3:.1f}" r="2" fill="#ffffff"/>')
        lid_y = cy - ry * (.02 + .9 * lidk)
        lid = [(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 6), (cx + rx * .4, lid_y + 4),
               (cx - rx * .3, lid_y + 1), (cx - rx - 10, lid_y - 10)]
        s.append(blob(lid, SKIN))
        s.append(blob([(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 20), (cx - rx - 10, lid_y - 22)],
                      "#d9a08f", .5))
        if lidk < .6:
            s.append(line([(cx - rx * .7, lid_y - 16), (cx, lid_y - 13), (cx + rx * .6, lid_y - 15)], 2, SKIN_SH2, seed=sd + 7, op=.7))
        s.append(line([(cx - rx - 6, lid_y - 9), (cx - rx * .3, lid_y + 1.5), (cx + rx * .4, lid_y + 4), (cx + rx + 6, lid_y - 5)],
                      6.0, seed=sd, taper=.4, wmin=.35))
        s.append("</g>")
        s.append(f'<path d="{ink_closed(ep, W(4.4), seed=sd + 2)}" fill="{INK}"/></g>')
    br = expr.get("brows", "tired")
    B = {"tired": ([(-30, -76), (4, -86), (46, -80)], [(72, -80), (100, -86), (126, -76)]),
         "up": ([(-30, -96), (6, -112), (46, -104)], [(72, -104), (102, -114), (128, -98)]),
         "calm": ([(-30, -80), (4, -86), (46, -78)], [(72, -78), (100, -84), (126, -78)]),
         "det": ([(-30, -88), (8, -84), (48, -68)], [(70, -68), (100, -82), (128, -90)]),
         "worry": ([(-30, -80), (8, -92), (46, -104)], [(72, -106), (100, -94), (126, -82)])}[br]
    s.append(line(B[0], 8, HAIR_SH, seed=162, peak=.4) + line(B[1], 6.8, HAIR_SH, seed=163, peak=.55))
    s.append(line([(-20, -64), (10, -70), (38, -66)], 2, SKIN_SH2, seed=168, op=.6))
    s.append(blob([(50, 30), (62, 58), (54, 66), (44, 56)], SKIN_SH, .9))
    s.append(line([(58, 22), (76, 50), (72, 63), (58, 65)], 4.6, seed=164, peak=.45))
    s.append(line([(50, 58), (56, 63)], 2.4, seed=169, op=.8))
    s.append(blob(ellipse_pts(64, 69, 8, 3, 8), SKIN_SH2, .7))
    s.append(line([(44, 70), (38, 80), (36, 88)], 2.2, SKIN_SH2, seed=170, op=.75))
    m = expr.get("mouth", "tired")
    if m == "tired":
        s.append(line([(38, 88), (60, 85), (82, 88), (92, 94)], 4.8, seed=165, peak=.45))
        s.append(blob([(50, 96), (76, 96), (72, 104), (54, 104)], SKIN_SH, .8))
    elif m == "flat":
        s.append(line([(40, 90), (62, 89), (86, 90)], 4.6, seed=165, peak=.5))
        s.append(blob([(52, 98), (76, 98), (72, 104), (56, 104)], SKIN_SH, .7))
    elif m == "pant":        # дышит ртом на бегу: рот открыт, зубы сверху
        s.append(shape([(38, 84), (60, 82), (86, 86), (82, 104), (62, 112), (44, 102)], "#5a2b33",
                       blob([(46, 100), (68, 98), (80, 106), (60, 114)], "#c86b6b") +
                       blob([(40, 82), (86, 84), (84, 90), (42, 89)], "#f0e6d8"), w=4.2, seed=177))
    elif m == "grin":        # широкая радость
        s.append(shape([(28, 80), (50, 86), (76, 86), (98, 76), (92, 98), (74, 114), (52, 114), (36, 100)], "#5a2b33",
                       blob([(30, 80), (98, 76), (96, 88), (32, 90)], "#f4ede0") +
                       blob([(46, 106), (64, 100), (84, 104), (70, 116), (52, 116)], "#c86b6b"), w=4.2, seed=181))
        s.append(line([(22, 76), (30, 82)], 2.6, seed=174, op=.8))
        s.append(line([(98, 70), (104, 76)], 2.6, seed=175, op=.8))
    elif m == "gape":        # растерянное «о»
        s.append(shape(ellipse_pts(64, 96, 12, 14, 12), "#5a2b33", blob(ellipse_pts(64, 103, 8, 4, 8), "#c86b6b"), w=3.8, seed=172))
        s.append(blob([(52, 114), (76, 114), (72, 118), (56, 118)], SKIN_SH, .8))
    if expr.get("sandwich"):
        s.append(sandwich(50, 90, 0.85, expr.get("sw_rot", 4.0)))
    hair = _bounce(HAIR_PTS, hb)
    inner = blob(_bounce([(-160, -190), (-20, -190), (-30, -130), (-70, -100), (-80, -40), (-160, -20)], hb), HAIR_SH, .95)
    inner += blob(_bounce([(10, -150), (60, -120), (100, -80), (70, -112), (40, -128)], hb), HAIR_HI, .9)
    inner += blob(_bounce([(-24, -170), (-4, -140), (-14, -120), (-30, -140)], hb), HAIR_HI, .6)
    for i, st in enumerate([[(-10, -150), (-30, -120), (-60, -100)], [(30, -140), (10, -110), (-20, -96)], [(70, -120), (60, -100), (40, -94)],
                            [(-70, -130), (-96, -110), (-112, -84)], [(-40, -100), (-70, -80), (-84, -56)], [(50, -140), (30, -120)],
                            [(-110, -110), (-130, -92)]]):
        inner += line(_bounce(st, hb), 3.2, "#2a170f", seed=172 + i, op=.85)
    s.append(shape(hair, HAIR, inner, w=5.4, seed=171))
    return "".join(s)


# ═════════════════════════════ ЧАСТИ ТЕЛА ═════════════════════════════
def limb_band(a, b, w0, w1, color, far, seed, inner_fn=None, cap=True):
    pts = band([P(a), P((np.array(a) + np.array(b)) / 2), P(b)], w0, w1, step=6, cap=cap)
    # стартовый скруглённый край
    d = np.array(b, float) - np.array(a, float)
    d /= np.linalg.norm(d) + 1e-9
    n = np.array([-d[1], d[0]])
    if cap:
        a_ = np.array(a, float)
        pts = pts + [P(a_ - n * w0 * .36 - d * w0 * .3), P(a_ - d * w0 * .46), P(a_ + n * w0 * .36 - d * w0 * .3)]
    inner = inner_fn(a, b, d, n) if inner_fn else ""
    return shape(pts, far_c(color, far), inner, w=5.0, seed=seed)


def leg(H, K, A, phi, far, seed, foot="shoe"):
    """Шин (джинсы) → бедро поверх; стопа по лодыжке A и углу phi (рад, + носок вниз): foot — "shoe" (кед), "sock", "bare"."""
    s = []
    if foot == "shoe":
        s.append(shoe(A, phi, far, seed + 20))
    else:
        s.append(bare_foot(A, phi, far, seed + 20, sock=(foot == "sock")))

    def shin_in(a, b, d, n):
        o = blob([P(np.array(a) - n * 46), P(np.array(b) - n * 34), P(np.array(b) - n * 10), P(np.array(a) - n * 14)], far_c(JEANS_SH, far), .85)
        o += line([P(np.array(a) + d * 40 + n * 20), P(np.array(a) + d * 120 + n * 26)], 2.2, far_c(JEANS_SEAM, far), seed=seed + 3, op=.7)
        return o

    # штанина у лодыжки шире — закрывает воротник кеда
    s.append(limb_band(K, A - (A - K) / np.linalg.norm(A - K) * 6, 118, 102, JEANS, far, seed + 1, shin_in))
    # отворот штанины
    d = (A - K) / np.linalg.norm(A - K)
    n = np.array([-d[1], d[0]])
    c = A + d * 4
    hem = [P(c - n * 54 - d * 22), P(c + n * 54 - d * 22), P(c + n * 56 + d * 2), P(c - n * 56 + d * 2)]
    s.append(shape(hem, far_c(JEANS_SH, far), line([P(c - n * 50 - d * 3), P(c + n * 50 - d * 3)], 1.8, far_c(JEANS_SEAM, far), seed=seed + 9, op=.7),
                   w=4.0, seed=seed + 8))

    def thigh_in(a, b, d, n):
        o = blob([P(np.array(a) - n * 64), P(np.array(b) - n * 50), P(np.array(b) - n * 16), P(np.array(a) - n * 20)], far_c(JEANS_SH, far), .85)
        # складки у колена
        for k, u in enumerate((.78, .88)):
            c = np.array(a) + (np.array(b) - np.array(a)) * u
            o += line([P(c + n * 40), P(c + d * 8 + n * 5), P(c - n * 26)], 2.2, far_c(JEANS_SH, far), seed=seed + 30 + k, op=.9)
        return o

    s.append(limb_band(H, K, 150, 124, JEANS, far, seed + 2, thigh_in))
    return "".join(s)


def shoe(A, phi, far, seed):
    """Кед в профиль: лодыжка A — начало координат стопы, ось x — вдоль стопы вперёд, phi — поворот (рад)."""
    c, s_ = math.cos(phi), math.sin(phi)
    KS = 1.22

    def tf(p):
        x, y = p[0] * KS, (p[1] - AH) * KS + AH
        return (A[0] + x * c - y * s_, A[1] + x * s_ + y * c) + ((1,) if len(p) > 2 and p[2] else ())

    up = [(-40, -30), (-62, -4), (-68, 34, 1), (150, 34, 1), (166, 24), (160, 8), (128, -4), (74, -14), (30, -34), (4, -40)]
    sole = [(-72, 30, 1), (-74, 50), (-62, 66), (166, 66), (178, 50), (172, 30, 1), (50, 31)]
    o = []
    o.append(shape([tf(p) for p in sole], far_c(SOLE, far),
                   blob([tf(p) for p in [(-72, 54), (176, 54), (176, 70), (-72, 70)]], far_c(SOLE_SH, far), .9) +
                   line([tf((-60, 48)), tf((160, 48))], 1.6, far_c(SOLE_SH, far), seed=seed + 1, op=.8), w=4.2, seed=seed))
    inner = blob([tf(p) for p in [(-70, 10), (160, 10), (170, 36), (-70, 36)]], far_c(SHOE_SH, far), .8)
    inner += blob([tf(p) for p in [(110, -12), (170, 4), (172, 34), (120, 34)]], far_c("#e6e2da", far), .95)   # носок-накладка
    inner += line([tf((118, -8)), tf((150, 2)), tf((166, 22))], 1.8, far_c("#b9b3a6", far), seed=seed + 3, op=.9)
    for k in range(3):
        x = 34 + k * 26
        inner += line([tf((x - 6, -40 + k * 7)), tf((x + 12, -30 + k * 7))], 2.6, far_c("#8f8a80", far), seed=seed + 4 + k)
    # цветная полоска новых кроссовок (бирюзовая, с оранжевым кантом)
    inner += blob([tf(p) for p in [(-46, 18), (6, -6), (66, -18), (104, -14), (64, -4), (20, 14), (-30, 30)]], far_c("#1f9e9a", far))
    inner += line([tf((-40, 32)), tf((20, 16)), tf((70, -2)), tf((104, -12))], 2.4, far_c("#f08a2c", far), seed=seed + 9, taper=.3, wmin=.4)
    o.append(shape([tf(p) for p in up], far_c(SHOE, far), inner, w=4.4, seed=seed + 2))
    return "".join(o)


SOCK, SOCK_SH, SOCK_ST = "#e9e4da", "#c8c0b2", "#d9543c"


def bare_foot(A, phi, far, seed, sock=False):
    """Ступня в профиль (без кеда): пятка, свод, пальцы-бугорки; sock=True — в носке (белый с красными полосками на резинке,
    мысок мягкий без пальцев). Те же координаты, что у shoe(): лодыжка A — начало, ось x — вперёд вдоль стопы."""
    c, s_ = math.cos(phi), math.sin(phi)
    KS = 1.22

    def tf(p):
        x, y = p[0] * KS, (p[1] - AH) * KS + AH
        return (A[0] + x * c - y * s_, A[1] + x * s_ + y * c) + ((1,) if len(p) > 2 and p[2] else ())

    o = []
    if sock:
        pts = [(-34, -40), (-58, -10), (-70, 30), (-62, 58), (-30, 66), (60, 64), (128, 62), (156, 54), (164, 36), (150, 18), (110, 6), (60, -6),
               (24, -30), (14, -50)]
        inner = blob([tf(p) for p in [(-70, 40), (160, 40), (160, 70), (-70, 70)]], far_c(SOCK_SH, far), .85)
        inner += blob([tf(p) for p in [(-40, -44), (20, -50), (26, -30), (-50, -24)]], far_c(SOCK_ST, far))
        inner += blob([tf(p) for p in [(-48, -18), (28, -24), (34, -10), (-56, -4)]], far_c(SOCK_ST, far))
        inner += blob([tf(p) for p in [(120, 20), (166, 30), (160, 62), (120, 62)]], far_c(SOCK_SH, far), .7)
        inner += line([tf((-50, 40)), tf((-30, 58))], 2.2, far_c(SOCK_SH, far), seed=seed + 4, op=.8)
        o.append(shape([tf(p) for p in pts], far_c(SOCK, far), inner, w=4.2, seed=seed))
        return "".join(o)
    sk, sh = far_c(SKIN, far), far_c(SKIN_SH, far)
    pts = [(-30, -40), (-52, -6), (-64, 30), (-56, 58), (-26, 64), (50, 60), (96, 62), (112, 66, 1), (126, 54), (134, 64, 1), (146, 52),
           (154, 60, 1), (164, 44), (160, 28), (130, 14), (80, 0), (40, -16), (14, -46)]
    inner = blob([tf(p) for p in [(-64, 44), (164, 44), (164, 70), (-64, 70)]], sh, .85)
    inner += line([tf((40, 40)), tf((84, 46))], 2.2, far_c(SKIN_SH2, far), seed=seed + 3, op=.8)
    for k, x in enumerate((122, 140)):
        inner += line([tf((x, 40)), tf((x - 2, 58))], 2.0, far_c(SKIN_SH2, far), seed=seed + 5 + k, op=.8)
    o.append(shape([tf(p) for p in pts], sk, inner, w=4.2, seed=seed))
    o.append(blob([tf(p) for p in [(150, 44), (162, 42), (160, 52), (150, 52)]], "#f4d6c8", .9))     # ноготь большого пальца
    return "".join(o)


def held_shoe(Wr, d, swing=0.0, seed=990, far=False):
    """Кед, который держат за задник: висит носком вниз-вперёд из кулака, качается на swing (рад)."""
    a = math.pi / 2 - 0.5 + swing
    A = np.array(Wr, float) + np.array([math.cos(a), math.sin(a)]) * 40 + np.array(d) * 20
    return shoe(A, a - math.pi / 2 + 0.2, far, seed)


def sandwich(x=58.0, y=96.0, k=1.0, rot=0.0):
    """Бутерброд в зубах (координаты головы): два ломтя хлеба, лист салата, сыр, колбаса торчит вперёд от рта."""
    o = []
    o.append(shape([(-6, -14), (120, -26), (150, -12), (152, 4), (-4, 10)], "#e8b878",
                   blob([(0, -10), (146, -18), (148, -10), (2, -2)], "#f6dcae") + blob([(-6, 4), (152, -2), (152, 6), (-4, 10)], "#c48a4c", .8),
                   w=4.0, seed=1801))
    o.append(shape([(0, 10), (60, 16), (100, 8), (150, 18), (160, 30), (110, 34), (60, 30), (4, 26)], "#7cc24e",
                   line([(20, 22), (120, 24)], 2.2, "#5a9a36", seed=1803, op=.8), w=3.0, seed=1802))
    o.append(shape([(10, 22), (128, 18), (140, 40, 1), (124, 30), (106, 42, 1), (96, 30), (10, 34)], "#ffd24a", "", w=3.0, seed=1804))
    o.append(shape(ellipse_pts(120, 34, 30, 10, 14), "#d0544e", blob(ellipse_pts(116, 32, 14, 4, 10), "#f08a80"), w=3.0, seed=1805))
    o.append(shape([(-4, 34), (120, 38), (148, 50), (146, 62), (-6, 58)], "#e8b878",
                   blob([(-4, 50), (146, 54), (146, 62), (-6, 58)], "#c48a4c", .8), w=4.0, seed=1806))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k:.3f}) translate(0 -24)">{"".join(o)}</g>'


def sleeve(S, E, Wr, far, seed):
    s = []

    def up_in(a, b, d, n):
        o = blob([P(np.array(a) - n * 60), P(np.array(b) - n * 50), P(np.array(b) - n * 14), P(np.array(a) - n * 18)], far_c(HOOD_SH, far), .85)
        c = np.array(b) - d * 30
        o += line([P(c + n * 34), P(c - d * 10), P(c - n * 20)], 2.6, far_c(FOLD, far), seed=seed + 5, op=.8, peak=.4)
        return o

    def fa_in(a, b, d, n):
        o = blob([P(np.array(a) - n * 52), P(np.array(b) - n * 44), P(np.array(b) - n * 10), P(np.array(a) - n * 14)], far_c(HOOD_SH, far), .85)
        for i, u in enumerate((.18, .32)):
            c = np.array(a) + (np.array(b) - np.array(a)) * u
            o += line([P(c + n * 30), P(c + d * 8), P(c - n * 26)], 2.6, far_c(FOLD, far), seed=seed + i, op=.85, peak=.4)
        return o

    s.append(limb_band(S, E, 132, 112, HOOD, far, seed + 7, up_in))
    s.append(limb_band(E, Wr, 112, 96, HOOD, far, seed + 8, fa_in))
    d = (Wr - E) / np.linalg.norm(Wr - E)
    n = np.array([-d[1], d[0]])
    c0 = Wr - d * 30
    cf = band([P(c0), P(Wr + d * 4)], 100, 96, step=3, cap=False)
    rib = "".join(line([P(c0 + d * k * 6 + n * 50), P(c0 + d * k * 6 - n * 50)], 1.6, far_c(HOOD_SH2, far), seed=seed + 20 + k, op=.8)
                  for k in range(1, 6))
    s.append(shape(cf, far_c(HOOD_SH, far), rib, w=4.0, seed=seed + 9))
    return "".join(s)


def fist(Wr, d, far, seed, flip=1):
    """Кулак в профиль: ось d — от запястья вперёд, большой палец сверху (сторона -n*flip). Пальцы согнуты валиками."""
    d = np.array(d, float) / np.linalg.norm(d)
    n = np.array([-d[1], d[0]]) * flip

    def tf(p):
        q = Wr + d * p[0] + n * p[1]
        return P(q)

    sk, sh = far_c(SKIN, far), far_c(SKIN_SH, far)
    o = []
    # кисть: тыл с округлым краем; спереди — согнутые пальцы фалангами-бугорками (4 штуки), между ними складки
    pts = [(-6, -40), (36, -50), (70, -48)]
    ys = [-40, -18, 4, 26, 46]
    for k in range(4):
        y0, y1 = ys[k], ys[k + 1]
        ym = (y0 + y1) / 2
        pts += [(86, y0 + 2), (100, ym - 6), (101, ym + 2), (92, y1 - 1, 1)] if k < 3 else [(86, y0 + 2), (99, ym - 4), (98, ym + 6), (84, y1)]
    pts += [(48, 54), (10, 46), (-8, 20)]
    inner = blob([tf(p) for p in [(-10, 22), (110, 22), (110, 60), (-10, 60)]], sh, .75)
    for k in range(1, 4):
        y = ys[k]
        inner += line([tf((94, y)), tf((80, y + 1)), tf((70, y + 3))], 2.4, far_c(SKIN_SH2, far), seed=seed + 10 + k, taper=.4)
    inner += line([tf((62, -40)), tf((58, 0)), tf((62, 44))], 2.0, far_c(SKIN_SH2, far), seed=seed + 7, op=.7)
    o.append(shape([tf(p) for p in pts], sk, inner, w=4.0, seed=seed))
    # большой палец поверх, ноготь у кончика
    th = band([tf((14, -40)), tf((44, -38)), tf((70, -28)), tf((84, -14))], 30, 22, step=3, cap=True)
    o.append(shape(th, sk, blob([tf((70, -26)), tf((90, -18)), tf((90, -8)), tf((72, -14))], "#e9c4b6", .95) +
                   line([tf((40, -28)), tf((56, -24))], 1.6, far_c(SKIN_SH2, far), seed=seed + 8, op=.7), w=3.6, seed=seed + 6))
    return "".join(o)


def open_hand(Wr, d, far, seed, flip=1, curl=0.0):
    """Раскрытая кисть, тянется к предмету (curl 0 — пальцы прямые, 1 — обхватили)."""
    d = np.array(d, float) / np.linalg.norm(d)
    n = np.array([-d[1], d[0]]) * flip
    sk, sh = far_c(SKIN, far), far_c(SKIN_SH, far)
    o = []
    palm = [(-6, -36), (50, -42), (80, -30), (84, 26), (54, 44), (6, 40), (-8, 14)]
    o.append(shape([P(Wr + d * x + n * y) for x, y in palm], sk, blob([P(Wr + d * x + n * y) for x, y in [(-8, 14), (84, 16), (84, 50), (-8, 50)]], sh, .8),
                   w=4.0, seed=seed))
    for i, (y, L) in enumerate([(-26, 70), (-8, 78), (10, 74), (28, 62)]):
        a = math.radians(70 * curl)
        p0 = np.array([78.0, y])
        p1 = p0 + np.array([L * .5, 0])
        p2 = p1 + np.array([L * .5 * math.cos(a), L * .5 * math.sin(a)])
        pts = [P(Wr + d * q[0] + n * q[1]) for q in (p0, p1, p2)]
        o.append(shape(band(pts, 22, 18, step=3, cap=True), sk, "", w=3.2, seed=seed + 1 + i))
    th = band([P(Wr + d * 20 + n * -34), P(Wr + d * 50 + n * -54), P(Wr + d * 84 + n * -58)], 26, 20, step=3, cap=True)
    o.append(shape(th, sk, "", w=3.6, seed=seed + 6))
    return "".join(o)


def torso_parts(lean, bounce_hood, strings_lag, far_arm_behind=True):
    """Туловище в своей системе: таз (0,0), вверх -y, вперёд +x; поворот lean снаружи. Возвращает (худи, капюшон, шнурки)."""
    body = [(-112, 34), (-120, -40), (-132, -170), (-128, -280), (-112, -360), (-78, -410), (-20, -432), (40, -426),
            (84, -398), (112, -330), (126, -230), (124, -120), (116, -20), (110, 34)]
    inner = blob([(30, -440), (130, -380), (140, 40), (60, 40), (80, -200)], HOOD_SH, .85)
    inner += blob([(-140, -300), (-100, -320), (-104, -100), (-140, -60)], HOOD_SH, .55)
    # карман-кенгуру
    pk = [(10, -170), (88, -178), (118, -150), (120, -30, 1), (6, -26, 1), (-10, -40), (-4, -150)]
    inner += shape(pk, HOOD, blob([(60, -180), (130, -160), (130, -20), (80, -20)], HOOD_SH, .9) +
                   line([(14, -160), (84, -168)], 2.4, FOLD, seed=401, op=.8), w=3.6, seed=402)
    inner += line([(-80, -140), (-40, -110), (-6, -100)], 2.6, FOLD, seed=403, op=.75)
    inner += line([(-96, -260), (-60, -236)], 2.4, FOLD, seed=404, op=.7)
    # резинка внизу
    rib = blob([(-130, -6), (130, -6), (130, 40), (-130, 40)], HOOD_SH, .95)
    rib += "".join(line([(-112 + k * 18, -2), (-112 + k * 18, 32)], 1.6, HOOD_SH2, seed=410 + k, op=.8) for k in range(13))
    inner += rib + line([(-118, -8), (116, -8)], 2.6, INK, seed=430, op=.9)
    hoodie = shape(body, HOOD, inner, w=5.2, seed=400)
    # капюшон лежит на спине; прыгает с запаздыванием
    hb = bounce_hood
    hood = [(-40, -440), (-110, -432 + hb * .4), (-158, -396 + hb), (-170, -330 + hb), (-146, -286 + hb * .7), (-108, -300), (-80, -352),
            (-48, -390)]
    h_in = blob([(-150, -390 + hb), (-110, -420 + hb * .5), (-90, -360), (-130, -320 + hb)], HOOD_SH2, .9)
    h_in += line([(-140, -380 + hb), (-118, -352 + hb * .6), (-100, -340)], 2.6, FOLD, seed=421, op=.85)
    hood_s = shape(hood, HOOD_SH, h_in, w=5.0, seed=420)
    # шнурки капюшона
    sx, sy = strings_lag
    st = ""
    for k, x0 in enumerate((44, 66)):
        pts = [(x0, -418), (x0 + 4 + sx * .4, -370 + sy * .3), (x0 + 6 + sx, -320 + sy)]
        st += line(pts, 4.2, "#efe8da", seed=440 + k, taper=.2, wmin=.8)
        st += line(pts, 1.4, INK, seed=450 + k, op=.6, taper=.2, wmin=.8)
        e = pts[-1]
        st += shape(lib.rect_pts(e[0] - 5, e[1] - 4, e[0] + 5, e[1] + 14, 3), "#c9c2b0", w=2.4, seed=460 + k)
    return hoodie, hood_s, st


# ═════════════════════════════ ИК и поза ═════════════════════════════
def ik2(a, b, L1, L2, side):
    """Двузвенная ИК: a — корень, b — цель; side=+1 — изгиб вперёд (колено), -1 — назад (локоть)."""
    a, b = np.array(a, float), np.array(b, float)
    v = b - a
    d = np.linalg.norm(v)
    d = min(max(d, abs(L1 - L2) + 1e-3), (L1 + L2) * 0.9995)
    u = v / (np.linalg.norm(v) + 1e-9)
    x = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, L1 * L1 - x * x))
    perp = np.array([u[1], -u[0]]) * side
    j = a + u * x + perp * h
    end = a + u * d
    return j, end


def draw(pose):
    """pose (всё в мире): hip, lean (рад, + вперёд), feet {'n'|'f': (ankle, phi)}, arms {'n'|'f': ('ang', th1, bend) |
    ('ik', target)}, hands {'n'|'f': 'fist'|'open'|('hold', curl)}, head_ang, expr, hood (прыжок), strings (dx,dy),
    held (функция svg предмета в руке (wrist, dir) -> str) для ближней руки."""
    H = np.array(pose["hip"], float)
    lean = pose["lean"]

    def L(p):                 # мир → L-ед. относительно таза
        return (np.array(p, float) - H) / BS

    up = rot(np.array([0.0, -1.0]), lean)
    fw = rot(np.array([1.0, 0.0]), lean)
    S = up * TORSO + fw * 6                              # плечевой сустав (L)
    neck = up * (TORSO + 52) + fw * 30
    out = []
    legs = {}
    for side in ("f", "n"):
        A, phi = pose["feet"][side]
        A = L(A)
        hipj = fw * (6 if side == "n" else -6)
        K, A2 = ik2(hipj, A, THIGH, SHIN, +1)
        legs[side] = (hipj, K, A2, phi)

    arms = {}
    for side in ("f", "n"):
        sp = S + (fw * -14 if side == "f" else fw * 4) + up * (6 if side == "f" else 0)
        a = pose["arms"][side]
        if a[0] == "ang":
            th1, bend = a[1], a[2]
            d1 = np.array([math.sin(th1 + lean * .3), math.cos(th1 + lean * .3)])
            E = sp + d1 * UPPER
            d2 = rot(d1, -bend)
            Wr = E + d2 * FORE
        else:
            E, Wr = ik2(sp, L(a[1]), UPPER, FORE, -1 if len(a) < 3 else a[2])
        arms[side] = (sp, E, Wr)

    def arm_svg(side):
        sp, E, Wr = arms[side]
        far = side == "f"
        d = (Wr - E) / np.linalg.norm(Wr - E)
        hd = pose.get("hand_dir", {}).get(side)
        if hd is not None:
            d = np.array(hd, float) / np.linalg.norm(hd)
        hk = pose.get("hands", {}).get(side, "fist")
        o = ""
        held = pose.get("held") if side == pose.get("held_side", "n") else None
        if held and held[0] == "behind":
            o += held[1](Wr, d)
        o += sleeve(sp, E, Wr, far, 600 + (0 if far else 50))
        flip = -1 if d[0] < -0.2 and False else 1
        if hk == "fist":
            o += fist(Wr + d * 2, d, far, 700 + (0 if far else 40), flip)
        elif isinstance(hk, tuple) and hk[0] == "open":
            o += open_hand(Wr + d * 2, d, far, 720 + (0 if far else 40), flip, hk[1])
        if held and held[0] == "front":
            o += held[1](Wr, d)
        hs = pose.get("held_shoe")
        if hs is not None and hs[0] == side:
            o = held_shoe(Wr + d * 30, d, hs[1], far=far) + o
        return o

    out.append(arm_svg("f"))
    ft = pose.get("foot", {})
    out.append(leg(*legs["f"][:3], legs["f"][3], True, 800, ft.get("f", "shoe")))
    # таз (джинсы) под худи
    pel = ellipse_pts(0, -6, 128, 70, 14, rot=math.degrees(lean))
    out.append(shape(pel, JEANS, blob(ellipse_pts(40, 20, 120, 50, 12), JEANS_SH, .7), w=4.6, seed=880))
    out.append(leg(*legs["n"][:3], legs["n"][3], False, 840, ft.get("n", "shoe")))
    # шея
    hoodie, hood_s, strings = torso_parts(lean, pose.get("hood", 0.0), pose.get("strings", (0, 0)))
    ha = pose.get("head_ang", 0.0)
    hpos = neck + rot(np.array([24.0, -96.0]), lean * .5 + ha)
    nk = band([P(S * .9 + fw * 20), P(neck + fw * 4), P(hpos + rot(np.array([-14, 90]), lean * .5 + ha))], 92, 84, step=5, cap=False)
    out.append(shape(nk, SKIN, blob([P(neck - fw * 50), P(neck + fw * 4), P(neck + fw * 10 + up * -60), P(neck - fw * 50 + up * -60)], SKIN_SH, .9),
                     w=4.4, seed=890))
    deg = math.degrees(lean)
    bp = pose.get("backpack", 0.0)
    if bp > 0.01:                       # рилс 83: школьный рюкзак на спине (bp 0…1 — растворяется на взрослении)
        bag = [(-118, -400), (-196, -392), (-236, -330), (-244, -170), (-226, -110), (-130, -104)]
        b_in = blob([(-240, -250), (-150, -250), (-150, -120), (-240, -120)], "#2f5f9e", .9)
        b_in += shape([(-236, -240), (-170, -244), (-160, -150), (-232, -140)], "#4f86c9", "", w=3.4, seed=2402)
        b_in += line([(-200, -400), (-216, -430), (-176, -440), (-160, -404)], 3.0, seed=2403)
        bsvg = shape(bag, "#3f78c2", b_in, w=4.6, seed=2401)
        strap = line([(-110, -398), (-40, -420), (10, -360), (-10, -200), (-50, -120)], 13.0, "#2f5f9e", seed=2404, taper=.1, wmin=.9)
        strap += line([(-110, -398), (-40, -420), (10, -360), (-10, -200), (-50, -120)], 2.2, INK, seed=2405, op=.7, taper=.1, wmin=.9)
        out.append(f'<g opacity="{bp:.3f}" transform="rotate({deg:.3f})">{bsvg}</g>')
        out.append(f'<g transform="rotate({deg:.3f})">{hood_s}{hoodie}{strings}</g>')
        out.append(f'<g opacity="{bp:.3f}" transform="rotate({deg:.3f})">{strap}</g>')
    else:
        out.append(f'<g transform="rotate({deg:.3f})">{hood_s}{hoodie}{strings}</g>')
    out.append(f'<g transform="translate({hpos[0]:.2f} {hpos[1]:.2f}) rotate({math.degrees(lean * .5 + ha):.3f})">{head(pose.get("expr", {}))}</g>')
    out.append(arm_svg("n"))
    g = f'<g transform="translate({H[0]:.3f} {H[1]:.3f}) scale({BS})">{"".join(out)}</g>'
    return g, {k: H + v[2] * BS for k, v in arms.items()}
