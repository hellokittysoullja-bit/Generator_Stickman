"""Герои сцены cafe рилса 27: Дима (тот же, что в 23–26: голова, лицо, волосы, мешки, щетина, горчичное худи —
голова и худи перенесены из 26_krossovki/story/run/dima.py) и его друг (новый взрослый персонаж той же манеры: высокий,
джинсовая куртка поверх белой футболки, рыжие волосы и борода, широкая улыбка).

Оба рисуются в профиль-3/4 ВПРАВО в своих «L-единицах» (голова ~300); друг в кадре отражается (смотрит влево).
Сидят на стуле: таз — точка опоры, бёдра вперёд, голени вниз (ИК), руки — ИК к целям, кисти с пальцами (hand.py).
Палитра героя переключается в draw(pose, who) — все части берут цвета из C.
"""
import math

import numpy as np

import hand as Hand
import lib
from lib import INK, band, blob, ellipse_pts, fill_d, ink_closed

LWK = 1.0
C = {}
PAL = {
    "dima": dict(SKIN="#ecc4a2", SKIN_SH="#d39f83", SKIN_SH2="#bf8a74", HAIR="#5a3826", HAIR_SH="#3d2418", HAIR_HI="#7a5038",
                 TOP="#d4a23e", TOP_SH="#a97b25", TOP_SH2="#8c6219", FOLD="#6b4a12",
                 LEGS="#3d4c6e", LEGS_SH="#2c3854", LEGS_SEAM="#5f6f92",
                 SHOE="#4b505e", SHOE_SH="#363a46", SOLE="#f2eee6", SOLE_SH="#c9c3b8", STRIPE="#d8483c", NAIL="#f1cdbd"),
    "friend": dict(SKIN="#f3d2b6", SKIN_SH="#dcab8e", SKIN_SH2="#c8917a", HAIR="#c8622c", HAIR_SH="#97441c", HAIR_HI="#e4894c",
                   TOP="#5d86b6", TOP_SH="#44678f", TOP_SH2="#344f70", FOLD="#2c4260", STITCH="#e2b46a",
                   TEE="#f4efe6", TEE_SH="#d9d2c4",
                   LEGS="#6b5946", LEGS_SH="#4f4133", LEGS_SEAM="#86735e",
                   SHOE="#7a4a2a", SHOE_SH="#5a341c", SOLE="#3b2c22", SOLE_SH="#2a1f18", STRIPE="#a76a3e", NAIL="#f6dccd"),
}
PAL["granny"] = dict(SKIN="#f2d6c0", SKIN_SH="#dcb095", SKIN_SH2="#c8957e", HAIR="#dcdce4", HAIR_SH="#aeb0c0", HAIR_HI="#f6f6fa",
                     TOP="#a283c4", TOP_SH="#7f62a3", TOP_SH2="#624a82", FOLD="#4a3563", STITCH="#e8d9f2", TEE="#f6efe2", TEE_SH="#ddd2bf",
                     LEGS="#6c4c63", LEGS_SH="#523a4b", LEGS_SEAM="#8a6a80", SHOE="#5b3e3a", SHOE_SH="#43302c", SOLE="#e9e2d4", SOLE_SH="#c4bcad",
                     STRIPE="#a76a3e", NAIL="#f6dccd")
PAL["sport"] = dict(SKIN="#d9a67f", SKIN_SH="#bd8662", SKIN_SH2="#a56f50", HAIR="#2f2220", HAIR_SH="#1c1412", HAIR_HI="#4a3630",
                    TOP="#d8483c", TOP_SH="#a8322a", TOP_SH2="#7e241e", FOLD="#5c1914", STITCH="#f4efe6", TEE="#f4efe6", TEE_SH="#d9d2c4",
                    LEGS="#2a2c36", LEGS_SH="#1c1d25", LEGS_SEAM="#4a4d5c", SHOE="#f1efe8", SHOE_SH="#cfcbbf", SOLE="#e8883a", SOLE_SH="#b86a28",
                    STRIPE="#d8483c", NAIL="#eac3a8")
PAL["mama"] = dict(SKIN="#f0cdb2", SKIN_SH="#d8a98e", SKIN_SH2="#c28f78", HAIR="#6e4a38", HAIR_SH="#4c3024", HAIR_HI="#8d6650", STREAK="#d9d7de",
                    TOP="#cfb48e", TOP_SH="#ab8f69", TOP_SH2="#8a7050", FOLD="#6e5436", STITCH="#e9dcc2", TEE="#f4ece0", TEE_SH="#dccfbb",
                    LEGS="#6a5a6c", LEGS_SH="#4f4252", LEGS_SEAM="#867489", SHOE="#6b4a3a", SHOE_SH="#4f3529", SOLE="#e9e2d4", SOLE_SH="#c4bcad",
                    STRIPE="#a76a3e", NAIL="#f1cdbd")
PAL["girl"] = dict(SKIN="#f6d6bc", SKIN_SH="#e0b095", SKIN_SH2="#cc977f", HAIR="#d2561f", HAIR_SH="#9c3a14", HAIR_HI="#ee8a45",
                   TOP="#4f9a8f", TOP_SH="#397a70", TOP_SH2="#2b5f57", FOLD="#1f4540", STITCH="#8fd0c4", TEE="#f4efe6", TEE_SH="#d9d2c4",
                   LEGS="#3d4558", LEGS_SH="#2c3342", LEGS_SEAM="#5d6780", SHOE="#f1efe8", SHOE_SH="#cfcbbf", SOLE="#d8483c", SOLE_SH="#a8322a",
                   STRIPE="#d8483c", NAIL="#f6dccd")
PAL["bald"] = dict(SKIN="#dfae8a", SKIN_SH="#c58e6c", SKIN_SH2="#ad7858", HAIR="#3a2a22", HAIR_SH="#241914", HAIR_HI="#5a443a",
                   TOP="#7d8a50", TOP_SH="#5f6b3a", TOP_SH2="#48532a", FOLD="#313a1c", STITCH="#d2c08a", TEE="#f4efe6", TEE_SH="#d9d2c4",
                   LEGS="#4a4f58", LEGS_SH="#363a42", LEGS_SEAM="#6a707c", SHOE="#2e2a28", SHOE_SH="#1c1a19", SOLE="#d9d3c6", SOLE_SH="#b5ae9f",
                   STRIPE="#a76a3e", NAIL="#e6bb9e")
PAL["cap"] = dict(SKIN="#efc8a6", SKIN_SH="#d6a384", SKIN_SH2="#c08c70", HAIR="#4a3020", HAIR_SH="#2f1d12", HAIR_HI="#6a4630", CAP="#c4382c", CAP_SH="#8f261d",
                  TOP="#8c939d", TOP_SH="#6c737d", TOP_SH2="#555b64", FOLD="#3a3f46", STITCH="#c6ccd4", TEE="#f4efe6", TEE_SH="#d9d2c4",
                  LEGS="#2f3b56", LEGS_SH="#222b40", LEGS_SEAM="#4d5b7c", SHOE="#e9e6dd", SHOE_SH="#c4c0b3", SOLE="#2a2c36", SOLE_SH="#1c1d25",
                  STRIPE="#4b505e", NAIL="#f1cdbd")
FRIENDLIKE = ("friend", "granny", "sport", "mama", "bald")
NEWHEADS = ("mama", "girl", "bald", "cap")
FAR = (0.82, 0.82, 0.9)

THIGH, SHIN, AH = 310.0, 300.0, 62.0
UPPER, FORE = 265.0, 230.0
TORSO = 400.0


def W(x):
    return x * LWK


def shape(pts, fill, inner="", w=5.0, seed=0, ink=True, var=0.28, weight=0.45):
    return lib.shape(pts, fill, inner, w=W(w), seed=seed, ink=ink, var=var, weight=weight)


def line(pts, w=4.0, color=INK, taper=0.6, wmin=0.12, seed=3, peak=0.5, op=1.0):
    return lib.line(pts, W(w), color, taper=taper, wmin=wmin, seed=seed, peak=peak, op=op)


def ring(pts, w, seed):
    return f'<path d="{ink_closed(pts, W(w) * lib.INK_K[0], seed=seed)}" fill="{INK}"/>'


def far_c(h, far):
    if not far:
        return h
    if h in (C["SKIN"], C["SKIN_SH"], C["SKIN_SH2"]):
        return lib.mul(h, (0.93, 0.9, 0.93))
    return lib.mul(h, FAR)


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


def P(p):
    return (float(p[0]), float(p[1]))


# ═════════════════════════════ ГЛАЗА, РОТ (общие) ═════════════════════════════
def _bounce(pts, b, y0=-96.0, k=70.0):
    out = []
    for p in pts:
        x, y = p[0], p[1]
        if y < y0:
            u = min(1.6, (y0 - y) / k)
            y = y + b * u
            x = x - b * 0.25 * u
        out.append((x, y) + ((1,) if len(p) > 2 and p[2] else ()))
    return out


def eyes(expr, EN, EF, bags=True, lash_col=INK):
    """Большие белые глаза с маленькими зрачками. expr: lid (0 — полуприкрыты, 1 — широко), look, closed (0..1 —
    моргание), laugh (0..1 — глаза-дуги «∩» от смеха), tears (0..1)."""
    s = []
    lidk = expr.get("lid", 0.3)
    lx, ly = expr.get("look", (0.3, 0.0))
    laugh = expr.get("laugh", 0.0)
    blink = expr.get("closed", 0.0)
    if bags:
        for (cx, cy, rx, ry, sd) in [(*EN, 154), (*EF, 155)]:
            bag = [(cx - rx * .85, cy + ry * .55), (cx, cy + ry * 1.38), (cx + rx * .85, cy + ry * .55), (cx, cy + ry * .9)]
            s.append(blob(bag, "#a77f8c", .78 * (1 - laugh)))
            if laugh < .5:
                s.append(line([(cx - rx * .8, cy + ry * .7), (cx, cy + ry * 1.36), (cx + rx * .75, cy + ry * .75)], 3.3, seed=sd))
    for nm, (cx, cy, rx, ry), sd in [("F", EF, 160), ("N", EN, 161)]:
        if laugh > .5:
            # зажмурился от смеха: дуга «∩», морщинки у внешнего угла
            k = (laugh - .5) * 2
            s.append(line([(cx - rx * .85, cy + ry * .25), (cx - rx * .3, cy - ry * (.15 + .1 * k)), (cx + rx * .35, cy - ry * (.15 + .1 * k)),
                           (cx + rx * .85, cy + ry * .25)], 6.4, seed=sd + 70, taper=.4, wmin=.35))
            s.append(line([(cx + rx * .95, cy + ry * .1), (cx + rx * 1.25, cy - ry * .05)], 2.2, C["SKIN_SH2"], seed=sd + 71))
            s.append(line([(cx + rx * .95, cy + ry * .35), (cx + rx * 1.25, cy + ry * .45)], 2.2, C["SKIN_SH2"], seed=sd + 72))
            tr = expr.get("tears", 0.0)
            if tr > 0.02:
                tx, ty = cx + rx * (-.8 if nm == "N" else .8), cy + ry * .45
                drop_y = ty + 40 * tr
                drop = [(tx, drop_y - 22 - 18 * tr), (tx + 10, drop_y - 4), (tx + 8, drop_y + 8), (tx, drop_y + 12), (tx - 8, drop_y + 8),
                        (tx - 10, drop_y - 4)]
                s.append(line([(tx, ty), (tx + 2, drop_y - 10)], 5, "#9fd6f2", seed=sd + 74, taper=.2, wmin=.6))
                s.append(shape(drop, "#bfe6fa", blob([(tx - 2, drop_y - 6), (tx + 3, drop_y - 4), (tx + 1, drop_y + 2)], "#ffffff"), w=2.4,
                               seed=sd + 75))
            continue
        ep = ellipse_pts(cx, cy, rx, ry, 14)
        cid = lib.clip_of(ep)
        s.append(f'<g><path d="{fill_d(ep)}" fill="#f6f2ea"/><g clip-path="url(#{cid})">')
        s.append(blob([(cx - rx, cy - ry), (cx + rx, cy - ry), (cx + rx, cy - ry * .2), (cx - rx, cy - ry * .25)], "#d9d2e2", .8))
        px, py = cx + rx * lx, cy + ry * ly
        s.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="7.4" ry="8.2" fill="{INK}"/>'
                 f'<circle cx="{px - 2.4:.1f}" cy="{py - 3:.1f}" r="2" fill="#ffffff"/>')
        lk = lidk * (1 - blink) - .15 * blink - .35 * laugh
        lid_y = cy - ry * (.02 + .9 * lk)
        lid = [(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 6), (cx + rx * .4, lid_y + 4),
               (cx - rx * .3, lid_y + 1), (cx - rx - 10, lid_y - 10)]
        s.append(blob(lid, C["SKIN"]))
        s.append(blob([(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 20), (cx - rx - 10, lid_y - 22)],
                      "#d9a08f", .5))
        if laugh > .05:      # щёки поднимают нижнее веко
            ly2 = cy + ry * (1.0 - 1.1 * laugh)
            s.append(blob([(cx - rx - 10, cy + ry + 30), (cx + rx + 10, cy + ry + 30), (cx + rx + 10, ly2 + 4), (cx, ly2 - 6), (cx - rx - 10, ly2 + 4)],
                          C["SKIN"]))
            s.append(line([(cx - rx * .8, ly2 + 2), (cx, ly2 - 5), (cx + rx * .8, ly2 + 2)], 3.4, seed=sd + 9))
        if lidk < .6 and blink < .5:
            s.append(line([(cx - rx * .7, lid_y - 16), (cx, lid_y - 13), (cx + rx * .6, lid_y - 15)], 2, C["SKIN_SH2"], seed=sd + 7, op=.7))
        s.append(line([(cx - rx - 6, lid_y - 9), (cx - rx * .3, lid_y + 1.5), (cx + rx * .4, lid_y + 4), (cx + rx + 6, lid_y - 5)],
                      6.0, lash_col, seed=sd, taper=.4, wmin=.35))
        s.append("</g>")
        s.append(ring(ep, 4.4, sd + 2) + "</g>")
    return "".join(s)


def talk_mouth(cx, cy, o, wide=1.0, smile=0.0, seed=180, inner_col="#5a2b33"):
    """Говорящий рот: o — раскрытие 0..1, smile — уголки вверх, wide — ширина."""
    w = 26 * wide + 6 * smile
    h = 4 + 20 * o
    up = 6 * smile
    pts = [(cx - w, cy - up), (cx - w * .4, cy - 3), (cx + w * .5, cy - 3), (cx + w, cy - up), (cx + w * .6, cy + h * .7), (cx, cy + h),
           (cx - w * .6, cy + h * .7)]
    if o < .08:
        return line([(cx - w, cy - up), (cx - w * .3, cy + 2 + smile * 3), (cx + w * .4, cy + 2 + smile * 3), (cx + w, cy - up)], 4.6, seed=seed)
    inner = blob([(cx - w, cy - 3), (cx + w, cy - 3), (cx + w * .8, cy + 5 + 2 * o), (cx - w * .8, cy + 5 + 2 * o)], "#f4ede0")
    inner += blob([(cx - w * .5, cy + h * .75), (cx, cy + h * .45), (cx + w * .55, cy + h * .7), (cx, cy + h + 4)], "#c86b6b")
    return shape(pts, inner_col, inner, w=4.2, seed=seed)


# ═════════════════════════════ ГОЛОВА ДИМЫ (из рилсов 23–26, 3/4 вправо) ═════════════════════════════
EYE_N = (16, -12, 50, 51)
EYE_F = (92, -10, 39, 47)
FACE = [(-30, -120), (40, -116), (86, -86), (106, -44), (110, -22), (118, 4), (120, 18), (112, 42), (108, 64), (90, 96),
        (62, 116), (30, 126), (2, 124), (-30, 112), (-60, 88), (-88, 46), (-104, -10), (-98, -70), (-68, -108)]
HAIR_PTS = [(108, -40), (104, -78), (82, -110), (94, -152, 1), (52, -128), (36, -172, 1), (8, -138), (-18, -180, 1), (-40, -136),
            (-86, -164, 1), (-90, -128), (-144, -130, 1), (-112, -96), (-158, -78, 1), (-118, -64), (-142, -34, 1), (-104, -38),
            (-94, -14, 1), (-80, -42), (-62, -70), (-22, -88), (12, -92), (30, -76, 1), (50, -98), (80, -86, 1), (98, -62), (108, -40, 1)]


def dima_head(expr):
    hb = expr.get("hair", 0.0)
    s = []
    back_hair = _bounce([(-60, -110), (-110, -86), (-150, -40, 1), (-122, -30), (-140, 10, 1), (-108, 6), (-100, 40, 1), (-80, 20),
                         (-70, -40)], hb * .6, y0=-20, k=60)
    s.append(shape(back_hair, C["HAIR_SH"], line([(-120, -50), (-100, -20)], 2.4, "#2a170f", seed=149, op=.8), w=4.8, seed=150))
    ear = [(-84, -18), (-108, -30), (-128, -8), (-126, 26), (-112, 50), (-92, 54), (-82, 44)]
    s.append(shape(ear, C["SKIN"], blob([(-128, -8), (-126, 26), (-112, 50), (-112, 14)], C["SKIN_SH"], .9), w=4.8, seed=151))
    s.append(line([(-96, 34), (-116, 22), (-114, -4), (-100, -14)], 3.2, seed=152))
    s.append(line([(-104, 6), (-96, 14), (-100, 24)], 2.4, seed=158, op=.8))
    inner = []
    inner.append(blob([(-110, -130), (-36, -130), (-58, -40), (-54, 40), (-20, 130), (-110, 130)], C["SKIN_SH"], .95))
    inner.append(blob([(-60, -60), (-34, -66), (-40, -20), (-62, -10)], C["SKIN_SH2"], .5))
    inner.append(blob([(70, 40), (112, 42), (106, 70), (80, 74)], C["SKIN_SH"], .55))
    inner.append(blob([(-20, 104), (40, 118), (96, 92), (110, 140), (-30, 140)], C["SKIN_SH"], .85))
    inner.append(blob([(-60, 70), (-20, 92), (30, 106), (80, 94), (106, 70), (110, 130), (-60, 130)], "#9e8a96", .42))
    rs = np.random.RandomState(7)
    for _ in range(120):
        x, y = rs.uniform(-56, 108), rs.uniform(70, 124)
        if (x - 30) ** 2 / 92 ** 2 + (y - 56) ** 2 / 70 ** 2 > 1.0 or y > 120 - abs(x - 30) * .15:
            continue
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rs.uniform(1.2, 2.2):.1f}" fill="#5c4446" opacity=".55"/>')
    blush = expr.get("blush", 0.0)
    inner.append(blob(ellipse_pts(54, -10, 100, 62, 14), "#d9a08f", .3))
    if blush > 0:
        inner.append(blob(ellipse_pts(100, 40, 22, 12, 10), "#e98a86", .55 * blush))
        inner.append(blob(ellipse_pts(4, 46, 30, 14, 10), "#e98a86", .5 * blush))
    fl = expr.get("flush", 0.0)
    if fl > 0.01:
        inner.append(blob(ellipse_pts(30, 20, 140, 120, 16), "#e2493c", .5 * fl))
        inner.append(blob(ellipse_pts(70, -60, 80, 40, 12), "#e2493c", .35 * fl))
    s.append(shape(FACE, C["SKIN"], "".join(inner), w=5.6, seed=153))
    s.append(line([(-66, 70), (-30, 104), (6, 118)], 2.4, C["SKIN_SH2"], seed=159, op=.8))
    s.append(eyes(expr, EYE_N, EYE_F, bags=True))
    br = expr.get("brows", "tired")
    if isinstance(br, tuple):      # (имя_a, имя_b, u): плавный переход бровей
        A_, B_, u_ = BROWS[br[0]], BROWS[br[1]], br[2]
        B = tuple([(p[0] + (q[0] - p[0]) * u_, p[1] + (q[1] - p[1]) * u_) for p, q in zip(A_[i], B_[i])] for i in (0, 1))
    else:
        B = BROWS[br]
    s.append(line(B[0], 8, C["HAIR_SH"], seed=162, peak=.4) + line(B[1], 6.8, C["HAIR_SH"], seed=163, peak=.55))
    s.append(blob([(50, 30), (62, 58), (54, 66), (44, 56)], C["SKIN_SH"], .9))
    s.append(line([(58, 22), (76, 50), (72, 63), (58, 65)], 4.6, seed=164, peak=.45))
    s.append(line([(50, 58), (56, 63)], 2.4, seed=169, op=.8))
    s.append(blob(ellipse_pts(64, 69, 8, 3, 8), C["SKIN_SH2"], .7))
    s.append(line([(44, 70), (38, 80), (36, 88)], 2.2, C["SKIN_SH2"], seed=170, op=.75))
    s.append(dima_mouth(expr))
    hair = _bounce(HAIR_PTS, hb)
    inner = blob(_bounce([(-160, -190), (-20, -190), (-30, -130), (-70, -100), (-80, -40), (-160, -20)], hb), C["HAIR_SH"], .95)
    inner += blob(_bounce([(10, -150), (60, -120), (100, -80), (70, -112), (40, -128)], hb), C["HAIR_HI"], .9)
    inner += blob(_bounce([(-24, -170), (-4, -140), (-14, -120), (-30, -140)], hb), C["HAIR_HI"], .6)
    for i, st in enumerate([[(-10, -150), (-30, -120), (-60, -100)], [(30, -140), (10, -110), (-20, -96)], [(70, -120), (60, -100), (40, -94)],
                            [(-70, -130), (-96, -110), (-112, -84)], [(-40, -100), (-70, -80), (-84, -56)], [(50, -140), (30, -120)],
                            [(-110, -110), (-130, -92)]]):
        inner += line(_bounce(st, hb), 3.2, "#2a170f", seed=172 + i, op=.85)
    s.append(shape(hair, C["HAIR"], inner, w=5.4, seed=171))
    return "".join(s)


BROWS = {"tired": ([(-30, -76), (4, -86), (46, -80)], [(72, -80), (100, -86), (126, -76)]),
         "up": ([(-30, -96), (6, -112), (46, -104)], [(72, -104), (102, -114), (128, -98)]),
         "calm": ([(-30, -80), (4, -86), (46, -78)], [(72, -78), (100, -84), (126, -78)]),
         "det": ([(-30, -88), (8, -84), (48, -68)], [(70, -68), (100, -82), (128, -90)]),
         "worry": ([(-30, -80), (8, -92), (46, -104)], [(72, -106), (100, -94), (126, -82)])}


def dima_mouth(expr):
    m = expr.get("mouth", "tired")
    if m == "talk":
        return talk_mouth(64, 88, expr.get("open", .3), wide=.9, smile=expr.get("smile", .3), seed=165)
    if m == "smile":
        k = expr.get("smile", 1.0)
        o = line([(36, 84 - 6 * k), (52, 92 + 2 * k), (72, 94 + 2 * k), (90, 86 - 6 * k)], 4.8, seed=165, peak=.5)
        o += line([(32, 80 - 5 * k), (38, 86 - 6 * k)], 2.4, seed=166, op=.8 * k)
        return o + blob([(50, 102), (76, 102), (72, 108), (54, 108)], C["SKIN_SH"], .7)
    if m == "flat":
        return line([(40, 90), (62, 89), (86, 90)], 4.6, seed=165, peak=.5) + blob([(52, 98), (76, 98), (72, 104), (56, 104)], C["SKIN_SH"], .7)
    if m in ("grin", "laugh"):
        o_ = expr.get("open", 1.0)
        dy = 10 * o_ if m == "laugh" else 0
        o = shape([(28, 80), (50, 86), (76, 86), (98, 76), (92, 98 + dy), (74, 114 + dy), (52, 114 + dy), (36, 100 + dy)], "#5a2b33",
                  blob([(30, 80), (98, 76), (96, 88), (32, 90)], "#f4ede0") +
                  blob([(46, 106 + dy), (64, 100 + dy), (84, 104 + dy), (70, 116 + dy), (52, 116 + dy)], "#c86b6b"), w=4.2, seed=181)
        o += line([(22, 76), (30, 82)], 2.6, seed=174, op=.8) + line([(98, 70), (104, 76)], 2.6, seed=175, op=.8)
        return o
    return line([(38, 88), (60, 85), (82, 88), (92, 94)], 4.8, seed=165, peak=.45) + blob([(50, 96), (76, 96), (72, 104), (54, 104)], C["SKIN_SH"], .8)


# ═════════════════════════════ ГОЛОВА ДРУГА (новая, та же манера, 3/4 вправо) ═════════════════════════════
F_EYE_N = (18, -22, 44, 46)
F_EYE_F = (90, -20, 34, 42)
F_FACE = [(-34, -128), (40, -126), (88, -96), (108, -54), (114, -26), (122, 0), (124, 16), (116, 40), (112, 70), (98, 110), (72, 140),
          (34, 154), (0, 150), (-34, 134), (-64, 104), (-90, 52), (-106, -10), (-100, -76), (-70, -116)]
F_HAIR = [(110, -66), (100, -104), (74, -128), (96, -158, 1), (50, -146), (28, -184, 1), (-4, -150), (-40, -176, 1), (-58, -138),
          (-104, -150, 1), (-104, -114), (-128, -86), (-112, -58), (-114, -20, 1), (-96, -34), (-86, -66), (-60, -88), (-16, -96),
          (24, -96), (60, -92), (92, -80), (110, -66, 1)]


def friend_head(expr):
    hb = expr.get("hair", 0.0)
    s = []
    ear = [(-86, -26), (-112, -38), (-132, -14), (-130, 22), (-116, 48), (-94, 52), (-84, 40)]
    s.append(shape(ear, C["SKIN"], blob([(-132, -14), (-130, 22), (-116, 48), (-116, 10)], C["SKIN_SH"], .9), w=4.8, seed=351))
    s.append(line([(-98, 32), (-118, 20), (-116, -8), (-102, -18)], 3.2, seed=352))
    inner = []
    inner.append(blob([(-120, -140), (-40, -140), (-60, -40), (-56, 40), (-30, 160), (-120, 160)], C["SKIN_SH"], .95))
    inner.append(blob(ellipse_pts(56, -16, 100, 60, 14), "#e5a99a", .3))
    rs = np.random.RandomState(31)
    for _ in range(26):            # веснушки на скулах и носу
        x, y = rs.uniform(-10, 116), rs.uniform(10, 40)
        if (x - 56) ** 2 / 70 ** 2 + (y - 26) ** 2 / 18 ** 2 > 1:
            continue
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rs.uniform(1.6, 2.6):.1f}" fill="#c47a4e" opacity=".75"/>')
    s.append(shape(F_FACE, C["SKIN"], "".join(inner), w=5.6, seed=353))
    # борода: от уха по челюсти, широкая, ниже подбородка; поверх — рот
    mouth = expr.get("mouth", "grin")
    o_ = expr.get("open", .6)
    beard = [(-84, 24), (-62, 60), (-40, 104), (-14, 148), (20, 184), (58, 190), (92, 168), (114, 128), (124, 82), (126, 46), (116, 40),
             (104, 66), (86, 72), (62, 70), (38, 74), (18, 66), (-10, 54), (-40, 30), (-66, 6)]
    binner = blob([(-90, 40), (60, 120), (130, 120), (130, 200), (-90, 200)], C["HAIR_SH"], .85)
    for i, st in enumerate([[(-50, 70), (-36, 98)], [(-20, 110), (-6, 138)], [(20, 140), (30, 168)], [(64, 150), (66, 176)], [(98, 124), (102, 150)],
                            [(4, 96), (12, 118)], [(-62, 40), (-50, 60)]]):
        binner += line(st, 2.6, "#7d3514", seed=380 + i, op=.85)
    style = expr.get("style", "")
    if style == "":
        s.append(shape(beard, C["HAIR"], binner, w=5.2, seed=354))
    elif style == "sport":      # щетина вместо бороды
        rs2 = np.random.RandomState(9)
        for _ in range(60):
            x, y = rs2.uniform(-40, 112), rs2.uniform(84, 140)
            if (x - 36) ** 2 / 90 ** 2 + (y - 112) ** 2 / 40 ** 2 > 1:
                continue
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="#6b4a3a" opacity=".6"/>')
    # нос
    s.append(blob([(48, 14), (64, 46), (54, 54), (42, 44)], C["SKIN_SH"], .9))
    s.append(line([(58, 2), (82, 40), (78, 56), (60, 58)], 5.0, seed=364, peak=.45))
    s.append(line([(50, 50), (57, 56)], 2.4, seed=369, op=.8))
    # усы и рот
    if mouth == "grin" or mouth == "laugh":
        dy = 14 * o_ if mouth == "laugh" else 6 * o_
        mpts = [(14, 82), (40, 90), (74, 90), (108, 76), (102, 104 + dy), (80, 124 + dy), (50, 126 + dy), (26, 108 + dy)]
        mi = blob([(14, 82), (108, 76), (104, 94), (18, 96)], "#f6efe2")
        mi += line([(30, 95), (96, 90)], 1.6, "#cfc5b4", seed=392, op=.8)
        mi += blob([(40, 116 + dy), (64, 108 + dy), (92, 112 + dy), (78, 130 + dy), (50, 130 + dy)], "#c86b6b")
        s.append(shape(mpts, "#5a2b33", mi, w=4.4, seed=391))
    elif mouth == "talk":
        s.append(talk_mouth(60, 92, o_, wide=1.3, smile=expr.get("smile", .6), seed=391))
    else:      # flat / fade: улыбка гаснет
        k = expr.get("smile", 0.0)
        s.append(line([(24, 92 - 6 * k), (50, 98 + 3 * k), (80, 98 + 3 * k), (104, 90 - 6 * k)], 4.8, seed=391, peak=.5))
    must = [(6, 80), (24, 66), (54, 62), (64, 70), (76, 62), (102, 64), (118, 76), (100, 82), (78, 78), (64, 84), (48, 78), (24, 84)]
    if style == "":
        s.append(shape(must, C["HAIR"], blob([(10, 80), (118, 78), (100, 86), (24, 88)], C["HAIR_SH"], .8), w=4.0, seed=355))
    if style == "granny":
        for (a, b, c_) in (([(-20, 70), (-8, 90), (-12, 108)], 0, 0),):
            pass
        s.append(blob(ellipse_pts(100, 52, 20, 11, 10), "#e98a86", .5) + blob(ellipse_pts(10, 60, 24, 12, 10), "#e98a86", .45))
        s.append(line([(24, 76), (14, 92), (18, 108)], 2.2, C["SKIN_SH2"], seed=398, op=.8) + line([(108, 70), (118, 84)], 2.2, C["SKIN_SH2"], seed=399, op=.8))
    s.append(eyes(expr, F_EYE_N, F_EYE_F, bags=False))
    if style == "granny":      # очки: тонкие круглые оправы без заливки
        for (cx_, cy_, r_, sd_) in ((18, -22, 56, 410), (90, -20, 44, 411)):
            s.append(f'<path d="{ink_closed(ellipse_pts(cx_, cy_, r_, r_ * .96, 18), 3.6 * lib.INK_K[0], seed=sd_)}" fill="#5a4a5e"/>')
        s.append(line([(64, -26), (48, -24)], 3.4, "#5a4a5e", seed=412))
        s.append(line([(-34, -30), (-100, -26)], 3.0, "#5a4a5e", seed=413))
    br = expr.get("brows", "up")
    B = {"up": ([(-26, -104), (8, -122), (48, -114)], [(70, -114), (98, -124), (122, -108)]),
         "calm": ([(-26, -90), (8, -98), (48, -90)], [(70, -90), (98, -96), (122, -88)]),
         "worry": ([(-26, -90), (10, -100), (48, -112)], [(70, -114), (98, -104), (122, -92)])}[br]
    s.append(line(B[0], 10, C["HAIR_SH"], seed=362, peak=.4) + line(B[1], 8.4, C["HAIR_SH"], seed=363, peak=.55))
    if style == "granny":
        G_HAIR = [(112, -58), (104, -98), (76, -126), (30, -140), (-20, -138), (-70, -124), (-112, -92), (-126, -40), (-116, 14), (-98, -14), (-88, -56),
                  (-60, -84), (-16, -96), (24, -98), (60, -92), (92, -80)]
        s.append(shape(ellipse_pts(-86, -150, 46, 42, 14), C["HAIR"], blob(ellipse_pts(-70, -142, 22, 20, 10), C["HAIR_HI"], .8), w=5.0, seed=420))
        s.append(shape(G_HAIR, C["HAIR"], blob([(-120, -140), (-20, -140), (-70, -100), (-110, -50)], C["HAIR_SH"], .7) +
                       line([(-40, -128), (-70, -100)], 2.6, C["HAIR_SH"], seed=421) + line([(10, -130), (-20, -110)], 2.6, C["HAIR_SH"], seed=422), w=5.2, seed=423))
        br = {"up": ([(-26, -90), (8, -102), (48, -94)], [(70, -94), (98, -100), (122, -88)])}["up"]
        s.append(line(br[0], 4.6, "#aeb0c0", seed=424, peak=.4) + line(br[1], 4.2, "#aeb0c0", seed=425, peak=.55))
        return "".join(s)
    hair = _bounce(F_HAIR, hb)
    inner = blob(_bounce([(-140, -200), (-30, -200), (-40, -130), (-80, -100), (-90, -40), (-140, -20)], hb), C["HAIR_SH"], .95)
    inner += blob(_bounce([(0, -160), (60, -136), (96, -100), (60, -120), (30, -140)], hb), C["HAIR_HI"], .9)
    for i, st in enumerate([[(-20, -160), (-40, -128), (-66, -104)], [(30, -160), (14, -126), (-10, -104)], [(76, -130), (60, -108)],
                            [(-80, -140), (-100, -116)], [(-50, -110), (-80, -84)]]):
        inner += line(_bounce(st, hb), 3.0, "#7d3514", seed=372 + i, op=.85)
    s.append(shape(hair, C["HAIR"], inner, w=5.4, seed=371))
    if style == "sport":      # повязка на лбу
        band_ = [(-104, -96), (-30, -112), (50, -108), (112, -80), (116, -56), (52, -84), (-26, -88), (-100, -66)]
        s.append(shape(band_, "#f4efe6", line([(-60, -100), (60, -96)], 2.4, "#d8483c", seed=430, taper=.2, wmin=.8), w=4.0, seed=431))
    return "".join(s)


# ═════════════════════════════ НОВЫЕ ГОЛОВЫ РИЛСА 59: мама, рыжая девушка, лысый в очках, парень в кепке ═════════════════════════════
FACE_G = [(-34, -128), (40, -126), (88, -96), (108, -54), (114, -26), (120, 0), (120, 16), (112, 40), (104, 70), (88, 106), (62, 132), (30, 142),
          (0, 138), (-34, 124), (-64, 98), (-90, 50), (-106, -10), (-100, -76), (-70, -116)]
SM_HAIR = [(112, -60), (106, -102), (82, -134), (38, -152), (-12, -154), (-64, -142), (-108, -110), (-120, -56), (-114, -8), (-94, -30), (-86, -66),
           (-60, -90), (-16, -100), (24, -100), (60, -96), (94, -82)]
FACE_B = [(-30, -196), (30, -200), (82, -168), (106, -110), (112, -54), (118, -26), (122, 0), (122, 18), (114, 44), (108, 76), (92, 112), (62, 142),
          (30, 154), (0, 150), (-34, 134), (-64, 104), (-90, 52), (-106, -10), (-104, -90), (-86, -152), (-60, -184)]


def _mouth_gen(expr, lip, seed=391, cx=60, cy=92, wide=1.15):
    m = expr.get("mouth", "smile")
    o_ = expr.get("open", .5)
    k = expr.get("smile", .8)
    if m in ("talk", "open"):
        return talk_mouth(cx, cy, o_, wide=wide, smile=k * .7, seed=seed)
    if m in ("grin", "laugh"):
        dy = 12 * o_ if m == "laugh" else 5 * o_
        w = 44 * wide / 1.15
        mp = [(cx - w, cy - 8), (cx - w * .4, cy - 2), (cx + w * .5, cy - 2), (cx + w, cy - 12), (cx + w * .8, cy + 14 + dy), (cx + w * .3, cy + 26 + dy),
              (cx - w * .3, cy + 26 + dy), (cx - w * .8, cy + 12 + dy)]
        mi = blob([(cx - w, cy - 8), (cx + w, cy - 12), (cx + w * .9, cy + 6), (cx - w * .9, cy + 8)], "#f6efe2")
        mi += blob([(cx - w * .5, cy + 18 + dy), (cx, cy + 10 + dy), (cx + w * .5, cy + 16 + dy), (cx, cy + 28 + dy)], "#c86b6b")
        return shape(mp, "#5a2b33", mi, w=4.2, seed=seed)
    if m == "flat":
        return line([(cx - 30, cy), (cx, cy - 2), (cx + 32, cy)], 4.6, lip, seed=seed, peak=.5)
    if m == "wobble":      # губы дрожат, вот-вот заплачет (радость или обида)
        return line([(cx - 28, cy - 2), (cx - 14, cy + 6), (cx, cy - 2), (cx + 14, cy + 6), (cx + 30, cy - 4)], 4.6, lip, seed=seed)
    return (line([(cx - 32, cy - 8 * k), (cx - 14, cy + 4 * k), (cx + 14, cy + 4 * k), (cx + 34, cy - 10 * k)], 5.0, lip, seed=seed, peak=.5)
            + line([(cx - 38, cy - 12 * k), (cx - 32, cy - 6 * k)], 2.4, C["SKIN_SH2"], seed=seed + 1, op=.8 * k)
            + blob([(cx - 10, cy + 12), (cx + 14, cy + 12), (cx + 10, cy + 19), (cx - 6, cy + 19)], C["SKIN_SH"], .7))


def _nose():
    return (blob([(48, 14), (64, 46), (54, 54), (42, 44)], C["SKIN_SH"], .9) + line([(58, 2), (82, 40), (78, 56), (60, 58)], 5.0, seed=364, peak=.45)
            + line([(50, 50), (57, 56)], 2.4, seed=369, op=.8))


def _brows(expr, col, wf=1.0, sd=362):
    br = expr.get("brows", "up")
    B = {"up": ([(-26, -104), (8, -122), (48, -114)], [(70, -114), (98, -124), (122, -108)]),
         "calm": ([(-26, -90), (8, -98), (48, -90)], [(70, -90), (98, -96), (122, -88)]),
         "worry": ([(-26, -90), (10, -100), (48, -112)], [(70, -114), (98, -104), (122, -92)]),
         "frown": ([(-26, -100), (10, -92), (48, -84)], [(70, -84), (98, -92), (122, -102)])}[br]
    return line(B[0], 10 * wf, col, seed=sd, peak=.4) + line(B[1], 8.4 * wf, col, seed=sd + 1, peak=.55)


def person_head(expr, style):
    """Голова 3/4 вправо для mama / girl / bald / cap (та же манера и сетка глаз, что у друга)."""
    hb = expr.get("hair", 0.0)
    s = []
    ear = [(-86, -26), (-112, -38), (-132, -14), (-130, 22), (-116, 48), (-94, 52), (-84, 40)]
    if style == "girl":       # длинные волосы сзади, падают на плечо
        back = [(-50, -150), (-120, -138), (-160, -80), (-176, 10), (-170, 100), (-150, 170), (-108, 214), (-70, 196), (-76, 120), (-60, 40), (-52, -40)]
        bi = blob([(-190, -160), (-60, -160), (-80, 60), (-100, 230), (-190, 230)], C["HAIR_SH"], .85)
        for i, st in enumerate([[(-110, -100), (-130, 0), (-124, 110)], [(-140, -60), (-156, 50), (-140, 150)], [(-90, -90), (-100, 20), (-94, 130)]]):
            bi += line(st, 2.8, C["HAIR_SH"], seed=470 + i, op=.9)
        s.append(shape(back, C["HAIR"], bi, w=5.2, seed=469))
    if style == "mama":
        back = [(-50, -146), (-116, -134), (-148, -80), (-150, -10), (-136, 56), (-104, 96), (-76, 90), (-84, 20), (-62, -40)]
        bi = blob([(-170, -160), (-60, -160), (-80, 60), (-90, 120), (-170, 120)], C["HAIR_SH"], .8)
        bi += line([(-100, -100), (-118, -20), (-110, 60)], 2.8, C["HAIR_SH"], seed=476, op=.9)
        s.append(shape(back, C["HAIR"], bi, w=5.2, seed=475))
    if style != "cap":
        s.append(shape(ear, C["SKIN"], blob([(-132, -14), (-130, 22), (-116, 48), (-116, 10)], C["SKIN_SH"], .9), w=4.8, seed=451))
        s.append(line([(-98, 32), (-118, 20), (-116, -8), (-102, -18)], 3.2, seed=452))
    if style == "mama":       # серёжка
        s.append(f'<circle cx="-110" cy="56" r="7" fill="#e0b440"/><circle cx="-112" cy="54" r="2.2" fill="#fff2b8"/>')
    face = {"girl": FACE_G, "mama": FACE_G, "bald": FACE_B, "cap": F_FACE}[style]
    inner = []
    inner.append(blob([(-120, -210), (-40, -210), (-60, -40), (-56, 40), (-30, 160), (-120, 160)], C["SKIN_SH"], .95))
    inner.append(blob(ellipse_pts(56, -16, 100, 60, 14), "#e5a99a", .3))
    bl = expr.get("blush", 0.0) + (.35 if style in ("girl", "mama") else 0)
    if bl > 0:
        inner.append(blob(ellipse_pts(100, 38, 22, 12, 10), "#e98a86", .5 * min(1, bl)))
        inner.append(blob(ellipse_pts(8, 44, 28, 14, 10), "#e98a86", .45 * min(1, bl)))
    fl = expr.get("flush", 0.0)
    if fl > .01:
        inner.append(blob(ellipse_pts(30, 20, 140, 120, 16), "#e2493c", .5 * fl))
    rs = np.random.RandomState(41)
    if style == "girl":       # веснушки
        for _ in range(34):
            x, y = rs.uniform(-6, 116), rs.uniform(8, 44)
            if (x - 56) ** 2 / 70 ** 2 + (y - 26) ** 2 / 20 ** 2 > 1:
                continue
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rs.uniform(1.6, 2.6):.1f}" fill="#c47a4e" opacity=".75"/>')
    if style == "bald":       # тень скулы, щетина, блик на лысине
        inner.append(blob([(-60, 70), (-20, 92), (30, 106), (80, 94), (106, 70), (110, 150), (-60, 150)], "#8a7a80", .35))
        for _ in range(110):
            x, y = rs.uniform(-60, 108), rs.uniform(64, 140)
            if (x - 30) ** 2 / 92 ** 2 + (y - 60) ** 2 / 82 ** 2 > 1 or y > 146 - abs(x - 30) * .15:
                continue
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rs.uniform(1.0, 1.8):.1f}" fill="#5c4446" opacity=".5"/>')
        inner.append(blob([(10, -190), (56, -176), (84, -146), (60, -158), (24, -172)], "#f2d2b4", .8))
        inner.append(blob([(-70, -170), (-104, -110), (-100, -60), (-60, -150)], C["SKIN_SH2"], .5))
    s.append(shape(face, C["SKIN"], "".join(inner), w=5.6, seed=453))
    # морщинки: мама — у глаз и носогубные; кот-парень — ничего
    if style == "mama":
        for k, (dx, dy) in enumerate(((0, 0), (0, 12), (0, 24))):
            s.append(line([(116, -22 + dy * .5), (134, -34 + dy)], 2.2, C["SKIN_SH2"], seed=480 + k, op=.8))
            s.append(line([(-4, 0 + dy * .4), (-22, -8 + dy)], 2.0, C["SKIN_SH2"], seed=484 + k, op=.7))
        s.append(line([(30, 60), (22, 86), (26, 104)], 2.2, C["SKIN_SH2"], seed=488, op=.75))
        s.append(line([(96, 56), (106, 80), (100, 98)], 2.2, C["SKIN_SH2"], seed=489, op=.75))
        s.append(line([(0, -60), (36, -66), (74, -62)], 1.8, C["SKIN_SH2"], seed=490, op=.55))
    if style == "cap":        # борода и усы
        beard = [(-84, 24), (-62, 60), (-40, 104), (-14, 148), (20, 184), (58, 190), (92, 168), (114, 128), (124, 82), (126, 46), (116, 40),
                 (104, 66), (86, 72), (62, 70), (38, 74), (18, 66), (-10, 54), (-40, 30), (-66, 6)]
        bi = blob([(-90, 40), (60, 120), (130, 120), (130, 200), (-90, 200)], C["HAIR_SH"], .85)
        for i, st in enumerate([[(-50, 70), (-36, 98)], [(-20, 110), (-6, 138)], [(20, 140), (30, 168)], [(64, 150), (66, 176)], [(98, 124), (102, 150)]]):
            bi += line(st, 2.6, C["HAIR_SH"], seed=500 + i, op=.85)
        s.append(shape(beard, C["HAIR"], bi, w=5.2, seed=499))
    s.append(_nose())
    lip = {"girl": "#c4545c", "mama": "#b8575a"}.get(style, INK)
    if style == "cap":
        o_ = expr.get("open", .5)
        m = expr.get("mouth", "grin")
        if m in ("grin", "laugh", "talk"):
            dy = 12 * o_ if m == "laugh" else 6 * o_
            mp = [(14, 82), (40, 90), (74, 90), (108, 76), (102, 104 + dy), (80, 124 + dy), (50, 126 + dy), (26, 108 + dy)]
            mi = blob([(14, 82), (108, 76), (104, 94), (18, 96)], "#f6efe2") + blob([(40, 116 + dy), (64, 108 + dy), (92, 112 + dy), (78, 130 + dy), (50, 130 + dy)], "#c86b6b")
            s.append(shape(mp, "#5a2b33", mi, w=4.4, seed=391))
        else:
            k = expr.get("smile", 0.0)
            s.append(line([(24, 92 - 6 * k), (50, 98 + 3 * k), (80, 98 + 3 * k), (104, 90 - 6 * k)], 4.8, "#2f1d12", seed=391, peak=.5))
        s.append(shape([(6, 80), (24, 66), (54, 62), (64, 70), (76, 62), (102, 64), (118, 76), (100, 82), (78, 78), (64, 84), (48, 78), (24, 84)], C["HAIR"],
                       blob([(10, 80), (118, 78), (100, 86), (24, 88)], C["HAIR_SH"], .8), w=4.0, seed=355))
    else:
        s.append(_mouth_gen(expr, lip, seed=391))
    s.append(eyes(expr, F_EYE_N, F_EYE_F, bags=(style == "bald" and expr.get("bags", False))))
    if style == "girl":       # ресницы
        for (cx_, cy_, rx_, sd_) in ((18, -22, 44, 520), (90, -20, 34, 524)):
            s.append(line([(cx_ + rx_ * .6, cy_ - 36), (cx_ + rx_ * 1.0, cy_ - 52)], 3.4, seed=sd_, taper=.3, wmin=.5))
            s.append(line([(cx_ + rx_ * .3, cy_ - 42), (cx_ + rx_ * .6, cy_ - 60)], 3.0, seed=sd_ + 1, taper=.3, wmin=.5))
    if style == "bald":       # очки: толстая тёмная оправа, перемычка, дужка к уху
        for (cx_, cy_, rx_, ry_, sd_) in ((14, -22, 50, 50, 530), (92, -20, 36, 46, 531)):
            gp = lib.rrect(cx_ - rx_, cy_ - ry_, cx_ + rx_, cy_ + ry_, 20)
            s.append(f'<path d="{ink_closed(gp, 9.0 * lib.INK_K[0], seed=sd_)}" fill="#2a2a32"/>')
            s.append(blob(lib.rrect(cx_ - rx_ + 8, cy_ - ry_ + 8, cx_ - rx_ * .2, cy_ - ry_ * .3, 8), "#ffffff", .22))
        s.append(line([(76, -26), (50, -24)], 7.0, "#2a2a32", seed=532))
        s.append(line([(-44, -30), (-104, -26)], 6.0, "#2a2a32", seed=533))
    brow_col = C["HAIR_SH"]
    s.append(_brows(expr, brow_col, 1.2 if style == "bald" else (.8 if style in ("girl", "mama") else 1.0)))
    if style == "girl":
        hair = _bounce(SM_HAIR, hb)
        hi = blob(_bounce([(-140, -200), (-30, -200), (-40, -130), (-80, -100), (-90, -40), (-140, -20)], hb), C["HAIR_SH"], .95)
        hi += blob(_bounce([(0, -160), (60, -136), (96, -100), (60, -120), (30, -140)], hb), C["HAIR_HI"], .9)
        for i, st in enumerate([[(-20, -160), (-40, -128), (-66, -104)], [(30, -160), (14, -126), (-10, -104)], [(76, -130), (60, -108)], [(-80, -140), (-100, -116)]]):
            hi += line(_bounce(st, hb), 3.0, C["HAIR_SH"], seed=540 + i, op=.85)
        s.append(shape(hair, C["HAIR"], hi, w=5.4, seed=539))
        # чёлка набок
        s.append(shape([(100, -96), (60, -122), (6, -126), (-30, -112), (-20, -90), (30, -100), (70, -84), (104, -62)], C["HAIR"],
                       line([(60, -112), (10, -112)], 2.6, C["HAIR_SH"], seed=548, op=.9), w=4.6, seed=547))
    elif style == "mama":
        hair = _bounce(SM_HAIR, hb * .6)
        hi = blob([(-140, -200), (-30, -200), (-40, -130), (-80, -100), (-90, -40), (-140, -20)], C["HAIR_SH"], .9)
        hi += blob([(0, -160), (60, -136), (96, -100), (60, -120), (30, -140)], C["HAIR_HI"], .8)
        for i, st in enumerate([[(-20, -160), (-40, -128), (-66, -104)], [(-80, -140), (-100, -116)]]):
            hi += line(st, 3.0, C["HAIR_SH"], seed=550 + i, op=.85)
        s.append(shape(hair, C["HAIR"], hi, w=5.4, seed=549))
        # седая прядь: широкая серебристая полоса от пробора по чёлке
        s.append(shape([(84, -104), (50, -138), (6, -150), (-30, -146), (4, -132), (44, -112), (80, -90)], C["STREAK"],
                       line([(60, -122), (10, -140)], 1.8, "#aaa8b2", seed=553, op=.9), w=3.4, seed=552))
        s.append(shape([(94, -80), (60, -104), (20, -110), (6, -96), (36, -92), (70, -76), (98, -60)], C["HAIR"], "", w=4.0, seed=554))
    elif style == "cap":
        # волосы из-под кепки сзади и на ухе
        s.append(shape([(-100, -70), (-130, -30), (-126, 10, 1), (-104, -4), (-96, 30), (-80, -10), (-70, -60)], C["HAIR"], "", w=4.6, seed=560))
        s.append(shape(ear, C["SKIN"], blob([(-132, -14), (-130, 22), (-116, 48), (-116, 10)], C["SKIN_SH"], .9), w=4.8, seed=561))
        crown = [(-108, -84), (-112, -140), (-70, -194), (0, -214), (66, -196), (104, -150), (112, -100), (60, -92), (-30, -100)]
        ci = blob([(-130, -230), (-10, -230), (-40, -120), (-120, -80)], C["CAP_SH"], .85)
        ci += line([(-4, -212), (-12, -150), (-30, -104)], 2.2, C["CAP_SH"], seed=563, op=.9)
        ci += line([(56, -196), (60, -140), (62, -96)], 2.2, C["CAP_SH"], seed=564, op=.8)
        s.append(shape(crown, C["CAP"], ci + f'<circle cx="0" cy="-214" r="9" fill="{C["CAP_SH"]}"/>', w=5.2, seed=562))
        brim = [(80, -104), (150, -108), (214, -92), (222, -76), (180, -62), (96, -72)]
        s.append(shape(brim, C["CAP"], blob([(90, -74), (222, -76), (180, -62), (96, -64)], C["CAP_SH"], .9)
                       + line([(94, -98), (200, -88)], 2.0, C["CAP_SH"], seed=566, op=.8), w=5.0, seed=565))
    return "".join(s)


def sweater_parts():
    """Вязаный свитер девушки: круглый ворот, косы-жгуты, резинка внизу, без кармана и капюшона."""
    body = [(-112, 34), (-120, -40), (-132, -170), (-128, -280), (-112, -360), (-78, -410), (-20, -432), (40, -426), (84, -398), (112, -330), (126, -230),
            (124, -120), (116, -20), (110, 34)]
    inner = blob([(30, -440), (130, -380), (140, 40), (60, 40), (80, -200)], C["TOP_SH"], .85)
    inner += blob([(-140, -300), (-100, -320), (-104, -100), (-140, -60)], C["TOP_SH"], .55)
    for k, x0 in enumerate((-60, -20, 20, 60)):      # косы
        pts = [(x0, -330), (x0 + 12, -280), (x0 - 4, -230), (x0 + 12, -180), (x0 - 4, -130), (x0 + 10, -80)]
        inner += line(pts, 3.2, C["TOP_SH2"], seed=610 + k, op=.8)
        inner += line([(x0 + 8, -330), (x0 + 20, -280), (x0 + 4, -230), (x0 + 20, -180), (x0 + 4, -130), (x0 + 18, -80)], 2.0, C["STITCH"], seed=620 + k, op=.7)
    rib = blob([(-130, -6), (130, -6), (130, 40), (-130, 40)], C["TOP_SH"], .95)
    rib += "".join(line([(-112 + k * 18, -2), (-112 + k * 18, 32)], 1.6, C["TOP_SH2"], seed=630 + k, op=.8) for k in range(13))
    inner += rib + line([(-118, -8), (116, -8)], 2.6, INK, seed=650, op=.9)
    torso = shape(body, C["TOP"], inner, w=5.2, seed=600)
    col = [(-60, -440), (-20, -462), (40, -452), (72, -420), (52, -396), (20, -420), (-30, -424), (-70, -410)]
    back = shape(col, C["TOP_SH"], line([(-50, -430), (30, -436)], 1.8, C["TOP_SH2"], seed=651, op=.8), w=4.0, seed=652)
    return back, torso, ""


# ═════════════════════════════ ТЕЛО ═════════════════════════════
def limb_band(a, b, w0, w1, color, far, seed, inner_fn=None, cap=True):
    pts = band([P(a), P((np.array(a) + np.array(b)) / 2), P(b)], w0, w1, step=6, cap=cap)
    d = np.array(b, float) - np.array(a, float)
    d /= np.linalg.norm(d) + 1e-9
    n = np.array([-d[1], d[0]])
    if cap:
        a_ = np.array(a, float)
        pts = pts + [P(a_ - n * w0 * .36 - d * w0 * .3), P(a_ - d * w0 * .46), P(a_ + n * w0 * .36 - d * w0 * .3)]
    inner = inner_fn(a, b, d, n) if inner_fn else ""
    return shape(pts, far_c(color, far), inner, w=5.0, seed=seed)


def leg(H, K, A, phi, far, seed, who):
    s = []
    s.append(shoe(A, phi, far, seed + 20, who))

    def shin_in(a, b, d, n):
        o = blob([P(np.array(a) - n * 46), P(np.array(b) - n * 34), P(np.array(b) - n * 10), P(np.array(a) - n * 14)], far_c(C["LEGS_SH"], far), .85)
        o += line([P(np.array(a) + d * 40 + n * 20), P(np.array(a) + d * 120 + n * 26)], 2.2, far_c(C["LEGS_SEAM"], far), seed=seed + 3, op=.7)
        return o

    s.append(limb_band(K, A - (A - K) / np.linalg.norm(A - K) * 6, 118, 102, C["LEGS"], far, seed + 1, shin_in))
    d = (A - K) / np.linalg.norm(A - K)
    n = np.array([-d[1], d[0]])
    c = A + d * 4
    hem = [P(c - n * 54 - d * 22), P(c + n * 54 - d * 22), P(c + n * 56 + d * 2), P(c - n * 56 + d * 2)]
    s.append(shape(hem, far_c(C["LEGS_SH"], far), line([P(c - n * 50 - d * 3), P(c + n * 50 - d * 3)], 1.8, far_c(C["LEGS_SEAM"], far), seed=seed + 9,
                                                       op=.7), w=4.0, seed=seed + 8))

    def thigh_in(a, b, d, n):
        o = blob([P(np.array(a) + n * 64), P(np.array(b) + n * 50), P(np.array(b) + n * 16), P(np.array(a) + n * 20)], far_c(C["LEGS_SH"], far), .85)
        for k, u in enumerate((.78, .88)):
            c = np.array(a) + (np.array(b) - np.array(a)) * u
            o += line([P(c - n * 40), P(c + d * 8 - n * 5), P(c + n * 26)], 2.2, far_c(C["LEGS_SH"], far), seed=seed + 30 + k, op=.9)
        return o

    s.append(limb_band(H, K, 150, 124, C["LEGS"], far, seed + 2, thigh_in))
    return "".join(s)


def shoe(A, phi, far, seed, who):
    c, s_ = math.cos(phi), math.sin(phi)
    KS = 1.22

    def tf(p):
        x, y = p[0] * KS, (p[1] - AH) * KS + AH
        return (A[0] + x * c - y * s_, A[1] + x * s_ + y * c) + ((1,) if len(p) > 2 and p[2] else ())

    o = []
    if who in FRIENDLIKE:          # ботинок: выше, тупой нос, толстая подошва
        up = [(-40, -60), (-66, -20), (-70, 34, 1), (156, 34, 1), (170, 18), (162, 0), (124, -10), (70, -18), (34, -50), (4, -64)]
        sole = [(-74, 30, 1), (-76, 58), (-66, 70), (170, 70), (180, 54), (174, 30, 1), (50, 31)]
    else:
        up = [(-40, -30), (-62, -4), (-68, 34, 1), (150, 34, 1), (166, 24), (160, 8), (128, -4), (74, -14), (30, -34), (4, -40)]
        sole = [(-72, 30, 1), (-74, 50), (-62, 66), (166, 66), (178, 50), (172, 30, 1), (50, 31)]
    o.append(shape([tf(p) for p in sole], far_c(C["SOLE"], far),
                   blob([tf(p) for p in [(-72, 54), (176, 54), (176, 72), (-72, 72)]], far_c(C["SOLE_SH"], far), .9), w=4.2, seed=seed))
    inner = blob([tf(p) for p in [(-70, 10), (160, 10), (170, 36), (-70, 36)]], far_c(C["SHOE_SH"], far), .8)
    if who in FRIENDLIKE:
        for k in range(3):
            x = 30 + k * 22
            inner += line([tf((x - 4, -46 + k * 9)), tf((x + 14, -38 + k * 9))], 2.6, far_c("#e8d7b8", far), seed=seed + 4 + k)
        inner += line([tf((-60, 22)), tf((160, 22))], 1.6, far_c(C["STRIPE"], far), seed=seed + 9, op=.9)
    else:
        inner += blob([tf(p) for p in [(110, -12), (170, 4), (172, 34), (120, 34)]], far_c("#e9e3d8", far), .95)
        for k in range(3):
            x = 34 + k * 26
            inner += line([tf((x - 6, -40 + k * 7)), tf((x + 12, -30 + k * 7))], 2.4, far_c("#e9e3d8", far), seed=seed + 4 + k)
        inner += line([tf((-30, -20)), tf((40, 6)), tf((120, 0))], 2.2, far_c(C["STRIPE"], far), seed=seed + 9, op=.9)
    o.append(shape([tf(p) for p in up], far_c(C["SHOE"], far), inner, w=4.4, seed=seed + 2))
    return "".join(o)


def sleeve(S, E, Wr, far, seed, who):
    s = []
    top, sh, sh2, fold = C["TOP"], C["TOP_SH"], C["TOP_SH2"], C["FOLD"]

    def up_in(a, b, d, n):
        o = blob([P(np.array(a) - n * 60), P(np.array(b) - n * 50), P(np.array(b) - n * 14), P(np.array(a) - n * 18)], far_c(sh, far), .85)
        c = np.array(b) - d * 30
        o += line([P(c + n * 34), P(c - d * 10), P(c - n * 20)], 2.6, far_c(fold, far), seed=seed + 5, op=.8, peak=.4)
        if who in FRIENDLIKE:
            o += line([P(np.array(a) + d * 20 + n * 40), P(np.array(b) - d * 20 + n * 34)], 1.8, far_c(C["STITCH"], far), seed=seed + 6, op=.7)
        return o

    def fa_in(a, b, d, n):
        o = blob([P(np.array(a) - n * 52), P(np.array(b) - n * 44), P(np.array(b) - n * 10), P(np.array(a) - n * 14)], far_c(sh, far), .85)
        for i, u in enumerate((.18, .32)):
            c = np.array(a) + (np.array(b) - np.array(a)) * u
            o += line([P(c + n * 30), P(c + d * 8), P(c - n * 26)], 2.6, far_c(fold, far), seed=seed + i, op=.85, peak=.4)
        return o

    s.append(limb_band(S, E, 132, 112, top, far, seed + 7, up_in))
    s.append(limb_band(E, Wr, 112, 96, top, far, seed + 8, fa_in))
    d = (Wr - E) / np.linalg.norm(Wr - E)
    n = np.array([-d[1], d[0]])
    c0 = Wr - d * 30
    cf = band([P(c0), P(Wr + d * 4)], 100, 96, step=3, cap=False)
    if who in FRIENDLIKE:      # манжета с пуговицей и строчкой
        inner = line([P(c0 + d * 6 + n * 48), P(c0 + d * 6 - n * 48)], 1.8, far_c(C["STITCH"], far), seed=seed + 20, op=.8)
        inner += f'<circle cx="{(c0 + d * 18 - n * 30)[0]:.1f}" cy="{(c0 + d * 18 - n * 30)[1]:.1f}" r="6" fill="{far_c("#c9a96a", far)}"/>'
        s.append(shape(cf, far_c(sh, far), inner, w=4.0, seed=seed + 9))
    else:
        rib = "".join(line([P(c0 + d * k * 6 + n * 50), P(c0 + d * k * 6 - n * 50)], 1.6, far_c(sh2, far), seed=seed + 20 + k, op=.8)
                      for k in range(1, 6))
        s.append(shape(cf, far_c(sh, far), rib, w=4.0, seed=seed + 9))
    return "".join(s)


def hoodie_parts(hood_b=0.0, strings=(0, 0)):
    body = [(-112, 34), (-120, -40), (-132, -170), (-128, -280), (-112, -360), (-78, -410), (-20, -432), (40, -426),
            (84, -398), (112, -330), (126, -230), (124, -120), (116, -20), (110, 34)]
    inner = blob([(30, -440), (130, -380), (140, 40), (60, 40), (80, -200)], C["TOP_SH"], .85)
    inner += blob([(-140, -300), (-100, -320), (-104, -100), (-140, -60)], C["TOP_SH"], .55)
    pk = [(10, -170), (88, -178), (118, -150), (120, -30, 1), (6, -26, 1), (-10, -40), (-4, -150)]
    inner += shape(pk, C["TOP"], blob([(60, -180), (130, -160), (130, -20), (80, -20)], C["TOP_SH"], .9) +
                   line([(14, -160), (84, -168)], 2.4, C["FOLD"], seed=401, op=.8), w=3.6, seed=402)
    inner += line([(-80, -140), (-40, -110), (-6, -100)], 2.6, C["FOLD"], seed=403, op=.75)
    inner += line([(-96, -260), (-60, -236)], 2.4, C["FOLD"], seed=404, op=.7)
    rib = blob([(-130, -6), (130, -6), (130, 40), (-130, 40)], C["TOP_SH"], .95)
    rib += "".join(line([(-112 + k * 18, -2), (-112 + k * 18, 32)], 1.6, C["TOP_SH2"], seed=410 + k, op=.8) for k in range(13))
    inner += rib + line([(-118, -8), (116, -8)], 2.6, INK, seed=430, op=.9)
    torso = shape(body, C["TOP"], inner, w=5.2, seed=400)
    hb = hood_b
    hood = [(-40, -440), (-110, -432 + hb * .4), (-158, -396 + hb), (-170, -330 + hb), (-146, -286 + hb * .7), (-108, -300), (-80, -352),
            (-48, -390)]
    h_in = blob([(-150, -390 + hb), (-110, -420 + hb * .5), (-90, -360), (-130, -320 + hb)], C["TOP_SH2"], .9)
    h_in += line([(-140, -380 + hb), (-118, -352 + hb * .6), (-100, -340)], 2.6, C["FOLD"], seed=421, op=.85)
    back = shape(hood, C["TOP_SH"], h_in, w=5.0, seed=420)
    sx, sy = strings
    st = ""
    for k, x0 in enumerate((44, 66)):
        pts = [(x0, -418), (x0 + 4 + sx * .4, -370 + sy * .3), (x0 + 6 + sx, -320 + sy)]
        st += line(pts, 4.2, "#efe8da", seed=440 + k, taper=.2, wmin=.8)
        st += line(pts, 1.4, INK, seed=450 + k, op=.6, taper=.2, wmin=.8)
        e = pts[-1]
        st += shape(lib.rect_pts(e[0] - 5, e[1] - 4, e[0] + 5, e[1] + 14, 3), "#c9c2b0", w=2.4, seed=460 + k)
    return back, torso, st


def jacket_parts(hood_b=0.0, strings=(0, 0), cardigan=False):
    """Джинсовая куртка друга (профиль вправо): спереди открыта, видна белая футболка; воротник, карман с клапаном,
    строчка горчичной ниткой, пояс-планка внизу."""
    TORSO_K = 1.0
    body = [(-112, 30), (-122, -40), (-134, -170), (-130, -290), (-114, -370), (-80, -420), (-20, -440), (40, -434),
            (86, -404), (110, -334), (122, -230), (120, -120), (114, -20), (110, 30)]
    tee = [(40, -430), (84, -404), (108, -336), (120, -230), (118, -120), (112, -10), (84, -10), (80, -120), (76, -250), (62, -360), (36, -420)]
    inner = blob([(-140, -300), (-100, -320), (-104, -100), (-140, -60)], C["TOP_SH"], .6)
    inner += shape(tee, C["TEE"], blob([(90, -420), (130, -300), (130, 0), (100, 0)], C["TEE_SH"], .9), w=3.4, seed=505)
    # полочка куртки (правый край — линия застёжки) поверх футболки
    flap = [(36, -424), (62, -360), (76, -250), (80, -120), (84, -10), (60, 30), (-20, 30), (-10, -300)]
    finner = blob([(40, -420), (90, -300), (90, 30), (50, 30), (54, -240)], C["TOP_SH"], .9)
    finner += line([(44, -400), (68, -250), (72, -40)], 1.8, C["STITCH"], seed=506, op=.8)
    for k, y in enumerate((-330, -230, -130, -40)):
        x = 66 + (y + 330) * .055
        finner += f'<circle cx="{x:.1f}" cy="{y}" r="7" fill="#c9a96a"/><circle cx="{x - 2:.1f}" cy="{y - 2}" r="2.4" fill="#f2dfae"/>'
    # нагрудный карман с клапаном
    if not cardigan:
      finner += shape([(-30, -300), (40, -306), (44, -240, 1), (-26, -236, 1)], C["TOP"], line([(-24, -270), (40, -274)], 1.6, C["STITCH"], seed=508, op=.8),
                    w=3.0, seed=507)
      finner += shape([(-34, -304), (44, -310), (46, -284), (6, -276), (-32, -284)], C["TOP_SH"], "", w=3.0, seed=509)
    inner += shape(flap, C["TOP"], finner, w=4.4, seed=504)
    # пояс-планка
    belt = [(-118, -26), (86, -26), (84, 30), (-114, 30)]
    inner += shape(belt, C["TOP_SH"], line([(-110, -18), (80, -18)], 1.6, C["STITCH"], seed=511, op=.85) +
                   line([(-110, 22), (80, 22)], 1.6, C["STITCH"], seed=512, op=.85), w=3.6, seed=510)
    inner += line([(-96, -260), (-60, -236)], 2.4, C["FOLD"], seed=513, op=.7)
    inner += line([(-80, -150), (-40, -120)], 2.4, C["FOLD"], seed=514, op=.7)
    torso = shape(body, C["TOP"], inner, w=5.2, seed=500)
    # воротник: отложной, у шеи сзади и спереди
    col = [(-60, -444), (-20, -462), (40, -452), (70, -420), (50, -400), (20, -426), (-30, -430), (-70, -414)]
    back = shape(col, C["TOP_SH"], line([(-50, -436), (30, -440)], 1.6, C["STITCH"], seed=521, op=.8), w=4.0, seed=520)
    return back, torso, ""


def ik2(a, b, L1, L2, side):
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


def hand_kw():
    return dict(shape_fn=shape, line_fn=line, skin=C["SKIN"], skin_sh=C["SKIN_SH"], skin_sh2=C["SKIN_SH2"], nail=C["NAIL"])


# ═════════════════════════════ СБОРКА ГЕРОЯ ═════════════════════════════
def draw(pose, who="dima"):
    """pose (мир, у друга — уже в его неотражённой системе): hip, scale, lean, feet {'n'|'f': (ankle, phi)} или None (ног нет),
    arms {'n'|'f': ('ik', target[, side]) | ('ang', th1, bend)}, hands {'n'|'f': dict(kind='open'|'grip'|'none', ...)},
    head_ang, expr, hood, layers — что рисовать: 'legs', 'body', 'arm_f', 'arm_n' (по умолчанию всё).
    Возвращает dict слоёв (строки SVG в мире) и точки запястий."""
    global C
    C = PAL[who]
    BS = pose["scale"]
    H = np.array(pose["hip"], float)
    lean = pose["lean"]
    tl = TORSO * pose.get("torso_k", 1.0)

    def L(p):
        return (np.array(p, float) - H) / BS

    def G(s):
        return f'<g transform="translate({H[0]:.3f} {H[1]:.3f}) scale({BS})">{s}</g>'

    up = rot(np.array([0.0, -1.0]), lean)
    fw = rot(np.array([1.0, 0.0]), lean)
    S = up * tl + fw * 6
    neck = up * (tl + 52) + fw * 30
    out = {}
    legs = {}
    if pose.get("feet"):
        for side in ("f", "n"):
            A, phi = pose["feet"][side]
            A = L(A)
            hipj = np.array([10.0 if side == "n" else -4.0, 0.0])
            K, A2 = ik2(hipj, A, THIGH, SHIN, +1)
            legs[side] = (hipj, K, A2, phi)
        lg = leg(*legs["f"][:3], legs["f"][3], True, 800, who)
        pel = ellipse_pts(0, -6, 128, 70, 14, rot=math.degrees(lean))
        lg += shape(pel, C["LEGS"], blob(ellipse_pts(40, 20, 120, 50, 12), C["LEGS_SH"], .7), w=4.6, seed=880)
        lg += leg(*legs["n"][:3], legs["n"][3], False, 840, who)
        out["legs"] = G(lg)
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
            E, Wr = ik2(sp, L(a[1]), UPPER, FORE, a[2] if len(a) > 2 else -1)
        arms[side] = (sp, E, Wr)

    def arm_svg(side):
        sp, E, Wr = arms[side]
        far = side == "f"
        d = (Wr - E) / np.linalg.norm(Wr - E)
        hs = pose.get("hands", {}).get(side, {"kind": "open"})
        hd = hs.get("dir")
        if hd is not None:
            d = np.array(hd, float) / np.linalg.norm(hd)
        o = sleeve(sp, E, Wr, far, 600 + (0 if far else 50), who)
        kw = hand_kw()
        if far:
            kw.update(skin=far_c(C["SKIN"], True), skin_sh=far_c(C["SKIN_SH"], True))
        kind = hs.get("kind", "open")
        k = hs.get("k", 1.0)
        if kind == "open":
            o += Hand.hand(Wr + d * 2, d, flip=hs.get("flip", 1), k=k, curl=hs.get("curl", (0.15, .1, .15, .2)), spread=hs.get("spread", .2),
                           thumb=hs.get("thumb", .2), bend=hs.get("bend", .1), seed=700 + (0 if far else 40), nails=not far, **kw)
        return o

    out["arm_f"] = G(arm_svg("f"))
    if pose.get("feet") is None and pose.get("pelvis", True):
        pel = ellipse_pts(0, -6, 128, 70, 14, rot=math.degrees(lean))
        out["pelvis"] = G(shape(pel, C["LEGS"], blob(ellipse_pts(40, 20, 120, 50, 12), C["LEGS_SH"], .7), w=4.6, seed=880))
    if who in ("dima", "cap"):
        back, torso, strings = hoodie_parts(pose.get("hood", 0.0), pose.get("strings", (0, 0)))
    elif who == "girl":
        back, torso, strings = sweater_parts()
    else:
        back, torso, strings = jacket_parts(cardigan=(who == "mama"))
    ha = pose.get("head_ang", 0.0)
    hpos = neck + rot(np.array([24.0, -96.0]), lean * .5 + ha) + np.array(pose.get("head_off", (0, 0)))
    nk = band([P(S * .9 + fw * 20), P(neck + fw * 4), P(hpos + rot(np.array([-14, 90]), lean * .5 + ha))], 92, 84, step=5, cap=False)
    body = shape(nk, C["SKIN"], blob([P(neck - fw * 50), P(neck + fw * 4), P(neck + fw * 10 + up * -60), P(neck - fw * 50 + up * -60)], C["SKIN_SH"], .9),
                 w=4.4, seed=890)
    deg = math.degrees(lean)
    tk = pose.get("torso_k", 1.0)
    body += f'<g transform="rotate({deg:.3f}) scale(1 {tk:.4f})">{back}{torso}{strings}</g>'
    hf = dima_head if who == "dima" else friend_head
    ex_ = dict(pose.get("expr", {}))
    if who in NEWHEADS:
        hf = lambda e, _w=who: person_head(e, _w)  # noqa: E731
    if who in ("granny", "sport"):
        ex_["style"] = who
    body += f'<g transform="translate({hpos[0]:.2f} {hpos[1]:.2f}) rotate({math.degrees(lean * .5 + ha):.3f})">{hf(ex_)}</g>'
    out["body"] = G(body)
    out["arm_n"] = G(arm_svg("n"))
    out["wrist"] = {k: H + v[2] * BS for k, v in arms.items()}
    out["elbow"] = {k: H + v[1] * BS for k, v in arms.items()}
    out["head"] = H + hpos * BS
    return out


def hand_world(Wr_world, d, scale, who, far=False, **hs):
    """Отдельная кисть в мире (для захвата чашки/телефона поверх предметов)."""
    global C
    C = PAL[who]
    kw = hand_kw()
    if far:
        kw.update(skin=far_c(C["SKIN"], True), skin_sh=far_c(C["SKIN_SH"], True))
    return kw, scale


# ═════════════════════════════ ПУБЛИЧНЫЙ API РИЛСА 59 (всё остальное — внутренности) ═════════════════════════════
# Импорт из ext_*:  sys.path.insert(0, COMMON); import lib, people   (COMMON = videos/59_podarok/story/common; lib/ink/hand/cat — копии 57 ext_c)
#   who: "dima" (горчичное худи), "mama" (седая прядь, бежевый кардиган), "girl" (рыжая, бирюзовый свитер), "bald" (лысый в очках, оливковая куртка),
#        "cap" (парень в кепке и с бородой, серое худи), "friend" (рыжий бородач в джинсовке, запасной).
#   figure(who, x, y, scale, expr, ...) -> SVG по пояс или во весь рост (лицом вправо; flip=True — влево). Высоты: HEIGHT[who] — множитель к scale.
#   hand_svg(who, wrist, d, ...) — отдельная кисть (хват, указка, ладонь); grip_svg(who, C, R, side, ...) — пальцы, обхватившие предмет.
#   cat_svg(x, y, k, st, t) — кот как look/hero.png (левое ухо загнуто, шерсть #3b4143).
#   expr: lid 0..1, look (x, y), closed, laugh 0..1 (глаза-дуги ∩), tears 0..1 (слёзы счастья при laugh>.5), mouth: talk/smile/grin/laugh/flat/wobble (+open, smile),
#         brows: Дима tired/up/calm/det/worry, остальные up/calm/worry/frown; blush, flush, hair (волосы подпрыгивают).
HEIGHT = {"dima": 1.0, "mama": .92, "girl": .96, "bald": 1.08, "cap": 1.02, "friend": 1.06}
FACES = ("dima", "mama", "girl", "bald", "cap", "friend")


def figure(who, x, y, scale=0.5, expr=None, lean=0.0, head_ang=0.0, arms=None, hands=None, feet=None, flip=False, layers=None, torso_k=1.0, hood=0.0,
           head_off=(0, 0), extra=None):
    """Человек по пояс (feet=None) или с ногами (feet={'n': (ankle, phi), 'f': ...}). (x, y) — таз в мире, scale — масштаб (голова ≈ 300·scale).
    arms по умолчанию — руки вниз. layers — подмножество {'legs','pelvis','arm_f','body','arm_n'} в порядке отрисовки (по умолчанию все).
    Возвращает dict(svg=..., head=(x, y), wrist={'n','f'}, elbow=...) — координаты уже с учётом flip."""
    sc = scale * HEIGHT.get(who, 1.0)
    if arms is None:
        arms = {"f": ("ang", 0.18, 0.18), "n": ("ang", -0.1, 0.25)}
    pose = dict(hip=(x, y), scale=sc, lean=lean, feet=feet, arms=arms, hands=hands or {}, head_ang=head_ang, expr=expr or {}, torso_k=torso_k,
                hood=hood, head_off=head_off)
    if extra:
        pose.update(extra)
    o = draw(pose, who)
    order = layers or ("legs", "pelvis", "arm_f", "body", "arm_n")
    svg = "".join(o[k] for k in order if k in o)
    res = dict(svg=svg, head=tuple(map(float, o["head"])), wrist={k: tuple(map(float, v)) for k, v in o["wrist"].items()},
               elbow={k: tuple(map(float, v)) for k, v in o["elbow"].items()}, scale=sc)
    if flip:
        res["svg"] = f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{svg}</g>'
        res["head"] = (2 * x - res["head"][0], res["head"][1])
        res["wrist"] = {k: (2 * x - v[0], v[1]) for k, v in res["wrist"].items()}
        res["elbow"] = {k: (2 * x - v[0], v[1]) for k, v in res["elbow"].items()}
    return res


def hand_svg(who, wrist, d, k=1.0, far=False, flip=1, curl=(0.15, .1, .15, .2), spread=.2, thumb=.2, bend=.1, seed=700, nails=True, show_thumb=True):
    """Отдельная кисть в мире: wrist — запястье, d — направление пальцев, k — масштаб (1 = голова 300). Для хвата: curl 0.5–0.8, thumb 0.6."""
    global C
    C = PAL[who]
    kw = hand_kw()
    if far:
        kw.update(skin=far_c(C["SKIN"], True), skin_sh=far_c(C["SKIN_SH"], True))
    return Hand.hand(wrist, d, flip=flip, k=k, curl=curl, spread=spread, thumb=thumb, bend=bend, seed=seed, nails=nails, show_thumb=show_thumb, **kw)


def grip_svg(who, center, R, side, k=1.0, h=None, seed=900):
    """Пальцы, обхватившие предмет спереди. Возвращает (back, front): back — ладонь и большой палец ЗА предметом, front — пальцы ПОВЕРХ него."""
    global C
    C = PAL[who]
    kw = hand_kw()
    kw.pop("nail", None)
    return Hand.grip(center, R, side, k=k, seed=seed, h=h, **kw)


def cat_svg(x, y, k, st=None, t=0.0):
    import cat
    return cat.draw(x, y, k, st or {}, t)
