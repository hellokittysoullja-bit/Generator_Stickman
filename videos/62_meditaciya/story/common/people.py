"""Люди рилса 61 «стол» (основа — common/people.py рилса 60). Новое в 61: участники эксперимента who="bob" (каре, круглые очки,
вишнёвый свитер) и who="beard" (кепка задом наперёд, густая борода, клетчатая рубашка); мимика мамы brows="skeptic" (одна бровь
вверх) и mouth="pursed" (поджатые губы); готовые позы POSE и мимика EXPR; кот шагает и прыгает (cat_walk / cat_jump).
Из 60: who="kid" — маленький Дима: круглая голова, пижама.
Герои сцены cafe рилса 27: Дима (тот же, что в 23–26: голова, лицо, волосы, мешки, щетина, горчичное худи —
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
from ink import fur

LWK = 1.0
C = {}
PAL = {
    "dima": dict(SKIN="#ecc4a2", SKIN_SH="#d39f83", SKIN_SH2="#bf8a74", HAIR="#5a3826", HAIR_SH="#3d2418", HAIR_HI="#7a5038",
                 TOP="#d4a23e", TOP_SH="#a97b25", TOP_SH2="#8c6219", FOLD="#6b4a12",
                 LEGS="#3d4c6e", LEGS_SH="#2c3854", LEGS_SEAM="#5f6f92",
                 SHOE="#4b505e", SHOE_SH="#363a46", SOLE="#f2eee6", SOLE_SH="#c9c3b8", STRIPE="#d8483c", NAIL="#f1cdbd"),
    # рилс 62: друг Димы — рыжий кудрявый, веснушки, зелёная футболка, бежевые штаны, кеды
    "pal": dict(SKIN="#f6d6bd", SKIN_SH="#e0b096", SKIN_SH2="#c9927a", HAIR="#d4672a", HAIR_SH="#a04818", HAIR_HI="#ee9152",
                TOP="#4fa36a", TOP_SH="#3a8052", TOP_SH2="#2c6340", FOLD="#24503a", STITCH="#8fd1a2",
                LEGS="#c9b48c", LEGS_SH="#a8936c", LEGS_SEAM="#e0d0ac",
                SHOE="#e8e2d6", SHOE_SH="#bdb4a4", SOLE="#f4f0e8", SOLE_SH="#cfc8bc", STRIPE="#d8483c", NAIL="#f6dccb"),
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
PAL["kid"] = dict(SKIN="#f3cfae", SKIN_SH="#dba886", SKIN_SH2="#c8917a", HAIR="#94623a", HAIR_SH="#6e4526", HAIR_HI="#b98354",
                  TOP="#6f9bd1", TOP_SH="#5079ad", TOP_SH2="#3d6290", FOLD="#2c4a73", STITCH="#f4efe6", TEE="#f4efe6", TEE_SH="#d9d2c4",
                  LEGS="#6f9bd1", LEGS_SH="#5079ad", LEGS_SEAM="#9dbfe6", SHOE="#efe8da", SHOE_SH="#cfc7b6", SOLE="#d8d0c0", SOLE_SH="#b5ad9d",
                  STRIPE="#d4a23e", NAIL="#f1cdbd")
PAL["bob"] = dict(SKIN="#f4d3bb", SKIN_SH="#ddab90", SKIN_SH2="#c8947c", HAIR="#2c2228", HAIR_SH="#1a1418", HAIR_HI="#4e4048",
                  TOP="#a8434f", TOP_SH="#86323d", TOP_SH2="#66252e", FOLD="#4a1a21", STITCH="#e6a3a8", TEE="#f4efe6", TEE_SH="#d9d2c4",
                  LEGS="#3a3f4c", LEGS_SH="#2a2e38", LEGS_SEAM="#596072", SHOE="#6b4a3a", SHOE_SH="#4f3529", SOLE="#e9e2d4", SOLE_SH="#c4bcad",
                  STRIPE="#a76a3e", NAIL="#f6dccd", FRAME="#3a2c34")
PAL["beard"] = dict(SKIN="#e3b28e", SKIN_SH="#c99270", SKIN_SH2="#b07b5c", HAIR="#3b2618", HAIR_SH="#24170e", HAIR_HI="#5c3e2a",
                    CAP="#2f6b5a", CAP_SH="#1f4a3e",
                    TOP="#c9473c", TOP_SH="#9e3328", TOP_SH2="#7a241c", FOLD="#541812", STITCH="#f0d7b0", PLAID="#243a5e", PLAID2="#f1e6cf",
                    TEE="#f4efe6", TEE_SH="#d9d2c4",
                    LEGS="#55606e", LEGS_SH="#3e4752", LEGS_SEAM="#76828f", SHOE="#7a4a2a", SHOE_SH="#5a341c", SOLE="#3b2c22", SOLE_SH="#2a1f18",
                    STRIPE="#a76a3e", NAIL="#eec6aa")
FRIENDLIKE = ("pal", "kid", "friend", "granny", "sport", "mama", "bald", "beard")
NEWHEADS = ("mama", "girl", "bald", "cap", "bob", "beard", "pal")
KID_HEAD_K = 1.32      # голова ребёнка крупнее относительно тела
KID_LEG_K = 0.8
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
    blink0 = expr.get("closed", 0.0)
    if bags:
        bk_ = .45 if max(expr.get("shut", 0), expr.get("squeeze", 0)) > .5 else 1.0
        for (cx, cy, rx, ry, sd) in [(*EN, 154), (*EF, 155)]:
            bag = [(cx - rx * .85, cy + ry * .55), (cx, cy + ry * 1.38), (cx + rx * .85, cy + ry * .55), (cx, cy + ry * .9)]
            s.append(blob(bag, "#a77f8c", .78 * (1 - laugh) * bk_))
            if laugh < .5:
                s.append(line([(cx - rx * .8, cy + ry * .7), (cx, cy + ry * 1.36), (cx + rx * .75, cy + ry * .75)], 3.3, seed=sd))
    for nm, (cx, cy, rx, ry), sd in [("F", EF, 160), ("N", EN, 161)]:
        nl = nm.lower()
        sc_ = expr.get("scale_" + nl, 1.0)          # глаз распахнулся пружиной: scale_n / scale_f
        cy = cy + (sc_ - 1) * ry * .7          # распахнутый глаз растёт вниз (не под волосы)
        rx, ry = rx * sc_, ry * sc_
        blink = expr.get("closed_" + nl, blink0)     # один глаз закрыт, другой открыт
        shut = expr.get("shut_" + nl, expr.get("shut", 0.0))
        sqz = expr.get("squeeze_" + nl, expr.get("squeeze", 0.0))
        if sqz > .5:          # напряжённо зажмурен: «>» и «<», морщинки
            sgn = 1 if nm == "N" else -1
            a_ = cx - sgn * rx * .75
            s.append(line([(a_, cy - ry * .55), (cx + sgn * rx * .7, cy - ry * .02), (a_, cy + ry * .45)], 6.6, seed=sd + 80, taper=.35, wmin=.4))
            for j in (-1, 1):
                s.append(line([(cx - sgn * rx * 1.05, cy + j * ry * .5), (cx - sgn * rx * 1.35, cy + j * ry * .8)], 2.4, C["SKIN_SH2"], seed=sd + 81 + j))
            continue
        if shut > .5:         # закрыт спокойно: дуга «∪» с ресничкой
            k_ = (shut - .5) * 2
            yy = cy + ry * .1
            s.append(line([(cx - rx * .9, yy - ry * .1), (cx - rx * .35, yy + ry * (.18 + .14 * k_)), (cx + rx * .35, yy + ry * (.18 + .14 * k_)),
                           (cx + rx * .9, yy - ry * .1)], 6.0, seed=sd + 85, taper=.4, wmin=.35))
            s.append(line([(cx + rx * .85, yy - ry * .08), (cx + rx * 1.1, yy - ry * .3)], 3.0, seed=sd + 86, taper=.3, wmin=.5))
            continue
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
        lxx, lyy = expr.get("look_" + nm.lower(), (lx, ly))      # look_n / look_f — взгляд каждого глаза отдельно (глаза разъезжаются)
        px, py = cx + rx * lxx, cy + ry * lyy
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
         # рилс 62: торжественно (высоко и ровно), грустно (домиком), сведены от напряжения, одна бровь взлетела
         "solemn": ([(-30, -98), (6, -108), (46, -102)], [(72, -102), (100, -108), (126, -98)]),
         "sad": ([(-30, -78), (8, -88), (46, -108)], [(72, -110), (100, -92), (126, -80)]),
         "pinch": ([(-30, -90), (10, -82), (48, -64)], [(70, -64), (100, -80), (128, -92)]),
         "one_up": ([(-30, -80), (4, -86), (46, -80)], [(70, -100), (100, -114), (128, -100)]),
         "n_up": ([(-30, -104), (8, -124), (46, -112)], [(72, -80), (100, -84), (126, -78)]),
         "up": ([(-30, -96), (6, -112), (46, -104)], [(72, -104), (102, -114), (128, -98)]),
         "calm": ([(-30, -80), (4, -86), (46, -78)], [(72, -78), (100, -84), (126, -78)]),
         "det": ([(-30, -88), (8, -84), (48, -68)], [(70, -68), (100, -82), (128, -90)]),
         "worry": ([(-30, -80), (8, -92), (46, -104)], [(72, -106), (100, -94), (126, -82)])}


def dima_mouth(expr):
    m = expr.get("mouth", "tired")
    if m == "smack":       # причмокивает: губы трубочкой, кончик языка, блестящая слюнка (chew 0..1 — фаза)
        ch = expr.get("chew", 0.0)
        w = 16 + 6 * ch
        cy = 92
        o = shape(ellipse_pts(64, cy, w, 12 + 4 * (1 - ch), 12), "#c86b6b", blob(ellipse_pts(64, cy - 3, w * .55, 4 + 2 * ch, 8), "#5a2b33", .9), w=4.4, seed=176)
        if ch > .35:
            o += shape(ellipse_pts(70 + w * .6, cy + 6, 9, 6, 8), "#e8808c", "", w=2.6, seed=177)
        if expr.get("drool", 0.0) > .05:
            dl = 18 * expr["drool"]
            o += shape([(44, cy + 4), (50, cy + 6), (49, cy + 10 + dl), (45, cy + 14 + dl), (41, cy + 10 + dl)], "#cfeaf6",
                       blob([(45, cy + 6 + dl), (47, cy + 8 + dl), (45, cy + 11 + dl)], "#ffffff"), w=2.2, seed=178)
        o += line([(40, cy - 6), (44, cy + 2)], 2.2, C["SKIN_SH2"], seed=179, op=.8) + line([(88, cy - 6), (84, cy + 2)], 2.2, C["SKIN_SH2"], seed=173, op=.8)
        return o
    if m == "wobble":      # расстроен: уголки вниз, нижняя губа дрожит (trem — фаза)
        tr = expr.get("trem", 0.0)
        j = 2.6 * math.sin(tr * 2 * math.pi * 7)
        o = line([(36, 98), (48, 88 + j * .4), (62, 86 - j * .5), (76, 87 + j * .5), (92, 98)], 4.8, seed=165, peak=.5)
        o += line([(48, 102 + j), (62, 106 - j), (78, 102 + j)], 2.6, C["SKIN_SH2"], seed=167, op=.85)
        o += line([(32, 100), (38, 108)], 2.2, C["SKIN_SH2"], seed=168, op=.7)
        return o
    if m == "frown":
        return line([(38, 96), (60, 88), (82, 89), (92, 98)], 4.8, seed=165, peak=.5) + blob([(50, 102), (76, 102), (72, 108), (54, 108)], C["SKIN_SH"], .7)
    if m == "o":           # удивлённое «о»
        o_ = expr.get("open", .6)
        return shape(ellipse_pts(64, 94, 11 + 5 * o_, 9 + 12 * o_, 12), "#5a2b33", blob(ellipse_pts(64, 100 + 6 * o_, 8, 5, 8), "#c86b6b"), w=4.2, seed=172)
    if m == "side":        # улыбка краем рта (ближний уголок вверх)
        return line([(38, 92), (60, 92), (80, 88), (94, 76)], 4.8, seed=165, peak=.5) + line([(92, 72), (98, 78)], 2.4, seed=166, op=.8)
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
    if m == "pursed":      # поджатые губы: короткая сжатая линия, уголки вниз, складочки над и под губой
        return (line([(cx - 28, cy + 6), (cx - 8, cy - 1), (cx + 10, cy - 1), (cx + 30, cy + 7)], 6.2, lip, seed=seed, peak=.5)
                + line([(cx - 26, cy + 2), (cx - 22, cy + 10)], 2.2, C["SKIN_SH2"], seed=seed + 2, op=.8)
                + line([(cx + 26, cy + 3), (cx + 30, cy + 11)], 2.2, C["SKIN_SH2"], seed=seed + 3, op=.8)
                + line([(cx - 8, cy + 16), (cx + 10, cy + 16)], 2.0, C["SKIN_SH2"], seed=seed + 4, op=.6)
                + line([(cx - 6, cy - 10), (cx - 2, cy - 6)], 1.6, C["SKIN_SH2"], seed=seed + 5, op=.6)
                + line([(cx + 8, cy - 10), (cx + 6, cy - 6)], 1.6, C["SKIN_SH2"], seed=seed + 6, op=.6))
    if m == "wobble":      # губы дрожат, вот-вот заплачет (радость или обида)
        return line([(cx - 28, cy - 2), (cx - 14, cy + 6), (cx, cy - 2), (cx + 14, cy + 6), (cx + 30, cy - 4)], 4.6, lip, seed=seed)
    return (line([(cx - 32, cy - 8 * k), (cx - 14, cy + 4 * k), (cx + 14, cy + 4 * k), (cx + 34, cy - 10 * k)], 5.0, lip, seed=seed, peak=.5)
            + line([(cx - 38, cy - 12 * k), (cx - 32, cy - 6 * k)], 2.4, C["SKIN_SH2"], seed=seed + 1, op=.8 * k)
            + blob([(cx - 10, cy + 12), (cx + 14, cy + 12), (cx + 10, cy + 19), (cx - 6, cy + 19)], C["SKIN_SH"], .7))


def _nose():
    return (blob([(48, 14), (64, 46), (54, 54), (42, 44)], C["SKIN_SH"], .9) + line([(58, 2), (82, 40), (78, 56), (60, 58)], 5.0, seed=364, peak=.45)
            + line([(50, 50), (57, 56)], 2.4, seed=369, op=.8))


def _brows(expr, col, wf=1.0, sd=362, dy=0.0):
    br = expr.get("brows", "up")
    B = {"up": ([(-26, -104), (8, -122), (48, -114)], [(70, -114), (98, -124), (122, -108)]),
         "calm": ([(-26, -90), (8, -98), (48, -90)], [(70, -90), (98, -96), (122, -88)]),
         "worry": ([(-26, -90), (10, -100), (48, -112)], [(70, -114), (98, -104), (122, -92)]),
         "frown": ([(-26, -100), (10, -92), (48, -84)], [(70, -84), (98, -92), (122, -102)]),
         # одна бровь вверх (скепсис): ближняя приподнята дугой, дальняя опущена к носу
         "skeptic": ([(-24, -104), (8, -126), (46, -114)], [(70, -90), (98, -92), (122, -96)]),
         "sad": ([(-26, -96), (10, -100), (48, -110)], [(70, -110), (98, -102), (122, -92)])}[br]
    if dy:
        B = tuple([(p[0], p[1] + dy) for p in b] for b in B)
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
    if style == "bob":        # каре: тёмная масса сзади до линии челюсти
        back = [(-40, -156), (-112, -140), (-156, -86), (-168, -10), (-164, 66), (-150, 112), (-112, 128), (-78, 118), (-70, 60), (-60, -40)]
        bi = blob([(-190, -170), (-70, -170), (-80, 40), (-100, 140), (-190, 140)], C["HAIR_SH"], .85)
        for i, st in enumerate([[(-120, -110), (-140, -20), (-136, 90)], [(-96, -100), (-106, 0), (-100, 100)]]):
            bi += line(st, 2.6, C["HAIR_HI"], seed=455 + i, op=.7)
        s.append(shape(back, C["HAIR"], bi, w=5.2, seed=454))
    if style not in ("cap", "beard", "bob", "pal"):
        s.append(shape(ear, C["SKIN"], blob([(-132, -14), (-130, 22), (-116, 48), (-116, 10)], C["SKIN_SH"], .9), w=4.8, seed=451))
        s.append(line([(-98, 32), (-118, 20), (-116, -8), (-102, -18)], 3.2, seed=452))
    if style == "mama":       # серёжка
        s.append(f'<circle cx="-110" cy="56" r="7" fill="#e0b440"/><circle cx="-112" cy="54" r="2.2" fill="#fff2b8"/>')
    if style == "pal":        # кудри сзади, за ухом
        back = fur([(-40, -150), (-120, -136), (-158, -70), (-160, 10), (-134, 60), (-96, 50), (-88, -10), (-60, -80)], depth=22, every=6, seed=611)
        s.append(shape(back, C["HAIR_SH"], "", w=5.0, seed=612))
        s.append(shape(ear, C["SKIN"], blob([(-132, -14), (-130, 22), (-116, 48), (-116, 10)], C["SKIN_SH"], .9), w=4.8, seed=451))
        s.append(line([(-98, 32), (-118, 20), (-116, -8), (-102, -18)], 3.2, seed=452))
    face = {"pal": FACE_G, "girl": FACE_G, "mama": FACE_G, "bald": FACE_B, "cap": F_FACE, "bob": FACE_G, "beard": F_FACE}[style]
    inner = []
    inner.append(blob([(-120, -210), (-40, -210), (-60, -40), (-56, 40), (-30, 160), (-120, 160)], C["SKIN_SH"], .95))
    inner.append(blob(ellipse_pts(56, -16, 100, 60, 14), "#e5a99a", .3))
    bl = expr.get("blush", 0.0) + (.35 if style in ("girl", "mama", "bob") else 0)
    if bl > 0:
        inner.append(blob(ellipse_pts(100, 38, 22, 12, 10), "#e98a86", .5 * min(1, bl)))
        inner.append(blob(ellipse_pts(8, 44, 28, 14, 10), "#e98a86", .45 * min(1, bl)))
    fl = expr.get("flush", 0.0)
    if fl > .01:
        inner.append(blob(ellipse_pts(30, 20, 140, 120, 16), "#e2493c", .5 * fl))
    rs = np.random.RandomState(41)
    if style in ("girl", "pal"):       # веснушки
        for _ in range(34 if style == "girl" else 48):
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
    if style == "beard":      # густая окладистая борода ниже подбородка
        beard = [(-88, 10), (-70, 60), (-54, 120), (-30, 176), (8, 222), (54, 236), (96, 214), (122, 166), (132, 108), (132, 52), (120, 40),
                 (106, 64), (86, 72), (62, 70), (38, 74), (18, 66), (-12, 50), (-44, 24), (-70, -4)]
        bi = blob([(-100, 40), (60, 150), (140, 150), (140, 250), (-100, 250)], C["HAIR_SH"], .85)
        for i, st in enumerate([[(-54, 70), (-40, 104)], [(-28, 118), (-12, 152)], [(10, 150), (22, 190)], [(52, 170), (56, 206)],
                                [(92, 140), (98, 178)], [(116, 100), (120, 130)], [(-70, 20), (-58, 50)]]):
            bi += line(st, 2.6, C["HAIR_HI"], seed=500 + i, op=.75)
        s.append(shape(beard, C["HAIR"], bi, w=5.2, seed=498))
    if style == "cap":        # борода и усы
        beard = [(-84, 24), (-62, 60), (-40, 104), (-14, 148), (20, 184), (58, 190), (92, 168), (114, 128), (124, 82), (126, 46), (116, 40),
                 (104, 66), (86, 72), (62, 70), (38, 74), (18, 66), (-10, 54), (-40, 30), (-66, 6)]
        bi = blob([(-90, 40), (60, 120), (130, 120), (130, 200), (-90, 200)], C["HAIR_SH"], .85)
        for i, st in enumerate([[(-50, 70), (-36, 98)], [(-20, 110), (-6, 138)], [(20, 140), (30, 168)], [(64, 150), (66, 176)], [(98, 124), (102, 150)]]):
            bi += line(st, 2.6, C["HAIR_SH"], seed=500 + i, op=.85)
        s.append(shape(beard, C["HAIR"], bi, w=5.2, seed=499))
    s.append(_nose())
    lip = {"girl": "#c4545c", "mama": "#b8575a", "bob": "#b4505a"}.get(style, INK)
    if style in ("cap", "beard"):
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
    if style == "bob":        # круглые очки: тонкая тёмная оправа, перемычка, дужка под волосы
        for (cx_, cy_, rx_, ry_, sd_) in ((18, -22, 54, 54, 534), (92, -20, 40, 50, 535)):
            gp = ellipse_pts(cx_, cy_, rx_, ry_, 22)
            s.append(f'<path d="{ink_closed(gp, 5.6 * lib.INK_K[0], seed=sd_)}" fill="{C["FRAME"]}"/>')
            s.append(line([(cx_ - rx_ * .55, cy_ - ry_ * .5), (cx_ - rx_ * .2, cy_ - ry_ * .72)], 3.0, "#ffffff", seed=sd_ + 4, op=.55))
        s.append(line([(72, -28), (52, -30)], 4.4, C["FRAME"], seed=536))
        s.append(line([(-36, -30), (-80, -28)], 4.0, C["FRAME"], seed=537))
    if style == "bald":       # очки: толстая тёмная оправа, перемычка, дужка к уху
        for (cx_, cy_, rx_, ry_, sd_) in ((14, -22, 50, 50, 530), (92, -20, 36, 46, 531)):
            gp = lib.rrect(cx_ - rx_, cy_ - ry_, cx_ + rx_, cy_ + ry_, 20)
            s.append(f'<path d="{ink_closed(gp, 9.0 * lib.INK_K[0], seed=sd_)}" fill="#2a2a32"/>')
            s.append(blob(lib.rrect(cx_ - rx_ + 8, cy_ - ry_ + 8, cx_ - rx_ * .2, cy_ - ry_ * .3, 8), "#ffffff", .22))
        s.append(line([(76, -26), (50, -24)], 7.0, "#2a2a32", seed=532))
        s.append(line([(-44, -30), (-104, -26)], 6.0, "#2a2a32", seed=533))
    brow_col = C["HAIR_SH"]
    brows_svg = _brows(expr, brow_col, 1.2 if style in ("bald", "beard") else (1.25 if style in ("mama", "bob") else (.8 if style == "girl" else 1.0)),
                       dy={"mama": 14.0, "bob": 10.0}.get(style, 0.0))
    if style not in ("mama", "bob"):
        s.append(brows_svg)
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
        s.append('<g transform="translate(0 -24)">')      # линия волос выше: лоб открыт, брови (мимика мамы) видны
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
        s.append('</g>')
    elif style == "bob":
        # каре: макушка, ровная чёлка до бровей, боковая прядь закрывает ухо и кончается у челюсти, кончики внутрь
        top = _bounce([(112, -84), (108, -118), (84, -148), (40, -166), (-14, -168), (-66, -156), (-110, -122), (-132, -70), (-140, -10), (-136, 60),
                       (-120, 108), (-96, 122), (-74, 112), (-80, 96), (-92, 60), (-88, 10), (-74, -40), (-50, -72), (-20, -82), (20, -84), (60, -84),
                       (90, -82)], hb * .7)
        hi = blob(_bounce([(-150, -200), (-40, -200), (-50, -120), (-90, -90), (-100, 0), (-150, 40)], hb), C["HAIR_SH"], .9)
        hi += blob(_bounce([(-20, -160), (40, -150), (80, -130), (40, -138), (0, -146)], hb), C["HAIR_HI"], .9)
        for i, st in enumerate([[(-110, -100), (-122, -20), (-110, 80)], [(-90, -110), (-98, -30), (-90, 60)], [(-40, -150), (-30, -100)],
                                [(10, -156), (14, -100)], [(56, -146), (56, -96)]]):
            hi += line(_bounce(st, hb), 2.8, C["HAIR_HI"] if i < 2 else C["HAIR_SH"], seed=556 + i, op=.8)
        s.append(shape(top, C["HAIR"], hi, w=5.4, seed=555))
        # ровная чёлка: нижний край по линии бровей с лёгкими зубцами
        bang = [(116, -112), (70, -136), (10, -142), (-50, -128), (-60, -92), (-30, -88, 1), (-14, -96), (4, -86, 1), (24, -94), (44, -84, 1),
                (64, -92), (86, -84, 1), (104, -90), (118, -88)]
        s.append(shape(bang, C["HAIR"], blob([(-60, -140), (120, -140), (120, -120), (-60, -116)], C["HAIR_SH"], .6)
                       + line([(70, -130), (60, -96)], 2.2, C["HAIR_SH"], seed=561, op=.8)
                       + line([(20, -134), (14, -98)], 2.2, C["HAIR_SH"], seed=562, op=.8), w=4.6, seed=560))
    elif style == "pal":
        # шапка рыжих кудрей: пышная, круглыми завитками, ниже лба — чёлка-завитки
        base = [(116, -70), (112, -120), (80, -160), (30, -178), (-30, -176), (-84, -156), (-124, -112), (-138, -60), (-120, -20), (-94, -46),
                (-80, -80), (-40, -96), (0, -92), (40, -98), (80, -86), (104, -64)]
        hair = _bounce(fur(base, depth=26, every=7, seed=613), hb)
        hi = blob(_bounce([(-150, -200), (-40, -200), (-50, -120), (-90, -90), (-110, -20), (-150, -20)], hb), C["HAIR_SH"], .85)
        hi += blob(_bounce([(0, -170), (60, -150), (96, -110), (60, -132), (30, -150)], hb), C["HAIR_HI"], .9)
        for i, (cx_, cy_) in enumerate([(-80, -140), (-30, -150), (24, -150), (70, -128), (-110, -80), (-50, -110), (10, -118), (60, -100)]):
            hi += line(_bounce([(cx_ - 12, cy_ + 6), (cx_ - 4, cy_ - 10), (cx_ + 10, cy_ - 6), (cx_ + 6, cy_ + 8)], hb), 2.6, C["HAIR_SH"], seed=620 + i, op=.85)
        s.append(shape(hair, C["HAIR"], hi, w=5.4, seed=614))
    elif style == "beard":
        # кепка задом наперёд: козырёк смотрит назад (влево), спереди — вырез застёжки с прядью волос
        s.append(shape([(-100, -70), (-130, -30), (-126, 10, 1), (-104, -4), (-96, 30), (-80, -10), (-70, -60)], C["HAIR"], "", w=4.6, seed=570))
        s.append(shape(ear, C["SKIN"], blob([(-132, -14), (-130, 22), (-116, 48), (-116, 10)], C["SKIN_SH"], .9), w=4.8, seed=571))
        s.append(line([(-98, 32), (-118, 20), (-116, -8), (-102, -18)], 3.2, seed=572))
        brim = [(-80, -96), (-150, -98), (-214, -80), (-222, -62), (-178, -52), (-96, -66)]
        s.append(shape(brim, C["CAP"], blob([(-90, -66), (-222, -66), (-178, -50), (-96, -56)], C["CAP_SH"], .9)
                       + line([(-94, -90), (-200, -76)], 2.0, C["CAP_SH"], seed=574, op=.8), w=5.0, seed=573))
        crown = [(-108, -84), (-112, -140), (-70, -194), (0, -214), (66, -196), (104, -150), (114, -98), (60, -96), (-30, -100)]
        ci = blob([(-130, -230), (-10, -230), (-40, -120), (-120, -80)], C["CAP_SH"], .85)
        ci += line([(-4, -212), (-12, -150), (-30, -104)], 2.2, C["CAP_SH"], seed=576, op=.9)
        ci += line([(56, -196), (60, -140), (62, -100)], 2.2, C["CAP_SH"], seed=577, op=.8)
        # вырез застёжки спереди: арка, в ней волосы, ремешок поперёк
        arch = [(40, -98), (46, -132), (70, -150), (94, -138), (104, -100)]
        ci += shape(arch, C["HAIR"], blob([(40, -150), (104, -150), (104, -120), (40, -120)], C["HAIR_HI"], .6), w=3.4, seed=578)
        ci += shape([(42, -112), (102, -114), (102, -104), (42, -102)], C["CAP_SH"], "", w=2.6, seed=579)
        s.append(shape(crown, C["CAP"], ci + f'<circle cx="0" cy="-214" r="9" fill="{C["CAP_SH"]}"/>', w=5.2, seed=575))
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
    if style in ("mama", "bob"):      # брови поверх чёлки (иначе их прячут волосы, а мимика мамы — на бровях)
        s.append(brows_svg)
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



# ═════════════════════════════ МАЛЕНЬКИЙ ДИМА (рилс 60): круглая голова, пижама ═════════════════════════════
K_EYE_N = (16, -2, 54, 56)
K_EYE_F = (94, 0, 41, 52)
K_FACE = [(-26, -112), (44, -112), (92, -86), (112, -44), (118, -10), (126, 14), (126, 30), (118, 54), (106, 80), (84, 106), (52, 120), (18, 124),
          (-16, 116), (-52, 94), (-86, 52), (-104, -8), (-98, -66), (-66, -100)]
K_HAIR = [(112, -50), (106, -90), (84, -116), (98, -152, 1), (56, -132), (40, -170, 1), (10, -140), (-14, -178, 1), (-38, -138), (-80, -160, 1),
          (-86, -126), (-130, -118, 1), (-108, -90), (-144, -66, 1), (-114, -52), (-132, -22, 1), (-102, -26), (-92, -4), (-82, -40), (-62, -66),
          (-22, -82), (14, -86), (34, -70, 1), (54, -90), (84, -78, 1), (100, -58), (112, -50, 1)]
K_BROWS = {"tired": ([(-24, -76), (8, -84), (50, -78)], [(74, -78), (102, -82), (128, -74)]),
           "up": ([(-26, -92), (8, -106), (50, -100)], [(74, -100), (104, -108), (130, -94)]),
           "calm": ([(-24, -82), (8, -88), (50, -82)], [(74, -82), (102, -86), (128, -80)]),
           "det": ([(-24, -88), (10, -82), (50, -66)], [(72, -66), (102, -80), (130, -90)]),
           "worry": ([(-24, -78), (10, -92), (50, -102)], [(74, -104), (102, -92), (128, -80)]),
           "sleepy": ([(-24, -70), (8, -74), (50, -70)], [(74, -70), (102, -72), (128, -66)])}


def kid_mouth(expr):
    m = expr.get("mouth", "flat")
    o_ = expr.get("open", .3)
    if m == "talk":
        return talk_mouth(66, 84, o_, wide=.62, smile=expr.get("smile", .2), seed=265)
    if m == "yawn":          # широкий зевок: овал, язык, зубки сверху
        h = 26 + 34 * o_
        mp = [(40, 70), (62, 62), (88, 66), (98, 84), (92, 70 + h * .8), (66, 76 + h), (46, 70 + h * .8), (36, 86)]
        mi = blob([(44, 68), (92, 68), (88, 80), (48, 80)], "#f4ede0") + blob([(48, 70 + h * .7), (66, 66 + h * .55), (86, 70 + h * .7), (66, 76 + h)], "#c86b6b")
        return shape(mp, "#5a2b33", mi, w=4.2, seed=266)
    if m == "smile":
        k = expr.get("smile", 1.0)
        return line([(42, 80 - 5 * k), (58, 90 + 2 * k), (78, 91 + 2 * k), (94, 80 - 5 * k)], 4.6, seed=267, peak=.5)
    if m == "grin":
        mp = [(38, 76), (60, 82), (82, 82), (100, 72), (96, 94), (78, 108), (58, 108), (44, 94)]
        mi = blob([(40, 76), (100, 72), (98, 84), (42, 86)], "#f4ede0") + blob([(52, 100), (70, 94), (88, 98), (76, 110), (60, 110)], "#c86b6b")
        return shape(mp, "#5a2b33", mi, w=4.2, seed=268)
    if m == "wince":        # скривился: рот-зигзаг вниз
        return line([(40, 92), (54, 84), (66, 94), (80, 84), (94, 92)], 4.6, seed=269, peak=.5)
    return line([(44, 88), (64, 86), (88, 88)], 4.4, seed=265, peak=.5)


def kid_head(expr):
    """Голова ребёнка 3/4 вправо: круглое лицо, большие глаза, пуговка-нос, лохматые волосы, без щетины и мешков. expr как у Димы +
    redeye 0..1 (красные глаза), rub — зарезервировано, flush."""
    hb = expr.get("hair", 0.0)
    s = []
    bh = _bounce([(-60, -100), (-110, -78), (-146, -34, 1), (-120, -24), (-136, 14, 1), (-104, 8), (-96, 40, 1), (-78, 20), (-68, -40)], hb * .6, y0=-20, k=60)
    s.append(shape(bh, C["HAIR_SH"], "", w=4.8, seed=250))
    ear = [(-84, -8), (-108, -20), (-126, 2), (-124, 34), (-110, 54), (-90, 56), (-80, 46)]
    s.append(shape(ear, C["SKIN"], blob([(-126, 2), (-124, 34), (-110, 54), (-110, 20)], C["SKIN_SH"], .9), w=4.8, seed=251))
    s.append(line([(-94, 38), (-112, 28), (-112, 4), (-98, -6)], 3.0, seed=252))
    inner = []
    inner.append(blob([(-110, -130), (-36, -130), (-58, -40), (-54, 40), (-20, 130), (-110, 130)], C["SKIN_SH"], .9))
    inner.append(blob(ellipse_pts(54, -10, 100, 62, 14), "#e8a898", .25))
    bl = expr.get("blush", 0.0) + .5
    inner.append(blob(ellipse_pts(100, 52, 24, 13, 10), "#ec8e88", .5 * min(1, bl)))
    inner.append(blob(ellipse_pts(2, 58, 30, 15, 10), "#ec8e88", .45 * min(1, bl)))
    fl = expr.get("flush", 0.0)
    if fl > 0.01:
        inner.append(blob(ellipse_pts(30, 20, 140, 120, 16), "#e2493c", .4 * fl))
    rs = np.random.RandomState(17)
    for _ in range(18):        # веснушки на носу
        x, y = rs.uniform(52, 108), rs.uniform(28, 48)
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rs.uniform(1.4, 2.2):.1f}" fill="#c47a4e" opacity=".6"/>')
    s.append(shape(K_FACE, C["SKIN"], "".join(inner), w=5.6, seed=253))
    s.append(eyes(expr, K_EYE_N, K_EYE_F, bags=False))
    red = expr.get("redeye", 0.0)
    if red > 0.01:          # красные веки и прожилки
        for (cx, cy, rx, ry) in (K_EYE_N, K_EYE_F):
            s.append(blob(ellipse_pts(cx, cy + ry * .55, rx * 1.05, ry * .5, 12), "#e0605c", .55 * red))
            s.append(line([(cx - rx * .9, cy + ry * .1), (cx - rx * .4, cy + ry * .25)], 2.0, "#d9453e", seed=277, op=.8 * red))
            s.append(line([(cx + rx * .9, cy + ry * .1), (cx + rx * .4, cy + ry * .3)], 2.0, "#d9453e", seed=278, op=.8 * red))
    br = expr.get("brows", "calm")
    if isinstance(br, tuple):
        A_, B_, u_ = K_BROWS[br[0]], K_BROWS[br[1]], br[2]
        B = tuple([(p[0] + (q[0] - p[0]) * u_, p[1] + (q[1] - p[1]) * u_) for p, q in zip(A_[i], B_[i])] for i in (0, 1))
    else:
        B = K_BROWS[br]
    s.append(line(B[0], 7.6, C["HAIR_SH"], seed=262, peak=.4) + line(B[1], 6.4, C["HAIR_SH"], seed=263, peak=.55))
    s.append(blob([(56, 36), (68, 56), (60, 62), (50, 54)], C["SKIN_SH"], .9))
    s.append(line([(62, 28), (78, 48), (74, 60), (60, 61)], 4.2, seed=264, peak=.45))
    s.append(kid_mouth(expr))
    hair = _bounce(K_HAIR, hb)
    hi = blob(_bounce([(-160, -190), (-20, -190), (-30, -130), (-70, -100), (-80, -40), (-160, -20)], hb), C["HAIR_SH"], .95)
    hi += blob(_bounce([(10, -140), (60, -112), (100, -76), (70, -104), (40, -120)], hb), C["HAIR_HI"], .9)
    for i, st in enumerate([[(-10, -140), (-30, -112), (-60, -92)], [(30, -130), (10, -104), (-20, -90)], [(70, -112), (60, -94), (40, -88)],
                            [(-70, -124), (-96, -104), (-112, -80)], [(-40, -96), (-70, -76), (-84, -52)], [(-110, -104), (-130, -88)]]):
        hi += line(_bounce(st, hb), 3.0, "#2a170f", seed=272 + i, op=.85)
    s.append(shape(hair, C["HAIR"], hi, w=5.4, seed=271))
    return "".join(s)


def pajama_parts():
    """Пижама: круглый ворот, пуговицы, звёздочки на груди, манжеты; без капюшона. Размеры те же, что у худи (масштаб тела меньше)."""
    body = [(-112, 34), (-120, -40), (-132, -170), (-128, -280), (-112, -360), (-78, -410), (-20, -432), (40, -426), (84, -398), (112, -330), (126, -230),
            (124, -120), (116, -20), (110, 34)]
    inner = blob([(30, -440), (130, -380), (140, 40), (60, 40), (80, -200)], C["TOP_SH"], .85)
    inner += blob([(-140, -300), (-100, -320), (-104, -100), (-140, -60)], C["TOP_SH"], .55)
    for k, (x, y) in enumerate(((20, -330), (28, -250), (36, -170), (44, -90))):
        inner += f'<circle cx="{x}" cy="{y}" r="8" fill="#f4efe6"/><circle cx="{x - 2}" cy="{y - 2}" r="2.4" fill="#ffffff"/>'
    inner += line([(14, -400), (24, -330), (32, -250), (40, -170), (48, -90), (52, -20)], 2.4, C["FOLD"], seed=710, op=.8)
    for k, (x, y, r) in enumerate(((-70, -300, 1.0), (-30, -210, .8), (-84, -140, .9), (-50, -60, .7))):      # звёздочки
        pts = [(x + r * 22 * math.sin(a * math.pi / 5) * (1 if a % 2 == 0 else .45), y - r * 22 * math.cos(a * math.pi / 5) * (1 if a % 2 == 0 else .45))
               for a in range(10)]
        inner += blob(pts, "#f1cb5a", .95)
    inner += line([(-118, -8), (116, -8)], 2.6, INK, seed=711, op=.9)
    torso = shape(body, C["TOP"], inner, w=5.2, seed=700)
    col = [(-60, -440), (-20, -462), (40, -452), (72, -420), (52, -396), (20, -420), (-30, -424), (-70, -410)]
    back = shape(col, C["TOP_SH"], line([(-50, -430), (30, -436)], 1.8, C["STITCH"], seed=712, op=.8), w=4.0, seed=713)
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
    if who == "pal":       # футболка: короткий рукав, дальше голая рука (тоньше рукава худи)
        M = np.array(S, float) + (np.array(E, float) - np.array(S, float)) * .55
        s.append(limb_band(S, E, 104, 90, C["SKIN"], far, seed + 7,
                           lambda a, b, d, n: blob([P(np.array(a) - n * 46), P(np.array(b) - n * 40), P(np.array(b) - n * 12), P(np.array(a) - n * 14)],
                                                   far_c(C["SKIN_SH"], far), .8)))
        s.append(limb_band(E, Wr, 90, 74, C["SKIN"], far, seed + 8,
                           lambda a, b, d, n: blob([P(np.array(a) - n * 40), P(np.array(b) - n * 32), P(np.array(b) - n * 10), P(np.array(a) - n * 12)],
                                                   far_c(C["SKIN_SH"], far), .8)))
        s.append(limb_band(S, M, 136, 128, C["TOP"], far, seed + 9,
                           lambda a, b, d, n: blob([P(np.array(a) - n * 64), P(np.array(b) - n * 60), P(np.array(b) - n * 18), P(np.array(a) - n * 20)],
                                                   far_c(C["TOP_SH"], far), .85)))
        return "".join(s)
    top, sh, sh2, fold = C["TOP"], C["TOP_SH"], C["TOP_SH2"], C["FOLD"]

    def up_in(a, b, d, n):
        o = blob([P(np.array(a) - n * 60), P(np.array(b) - n * 50), P(np.array(b) - n * 14), P(np.array(a) - n * 18)], far_c(sh, far), .85)
        c = np.array(b) - d * 30
        o += line([P(c + n * 34), P(c - d * 10), P(c - n * 20)], 2.6, far_c(fold, far), seed=seed + 5, op=.8, peak=.4)
        if who in FRIENDLIKE and who != "beard":
            o += line([P(np.array(a) + d * 20 + n * 40), P(np.array(b) - d * 20 + n * 34)], 1.8, far_c(C["STITCH"], far), seed=seed + 6, op=.7)
        o += _plaid_band(a, b, d, n, far, seed)
        return o

    def _plaid_band(a, b, d, n, far, sd):
        if "PLAID" not in C:
            return ""
        o = ""
        L_ = float(np.linalg.norm(np.array(b, float) - np.array(a, float)))
        for i, u in enumerate(np.arange(30, L_, 64)):
            c = np.array(a, float) + d * u
            o += blob([P(c - n * 80), P(c + n * 80), P(c + n * 80 + d * 20), P(c - n * 80 + d * 20)], far_c(C["PLAID"], far), .5)
        for i, v in enumerate((-40, 10, 54)):
            o += blob([P(np.array(a) + n * v), P(np.array(b) + n * v), P(np.array(b) + n * (v + 18)), P(np.array(a) + n * (v + 18))], far_c(C["PLAID"], far), .45)
        return o

    def fa_in(a, b, d, n):
        o = blob([P(np.array(a) - n * 52), P(np.array(b) - n * 44), P(np.array(b) - n * 10), P(np.array(a) - n * 14)], far_c(sh, far), .85)
        for i, u in enumerate((.18, .32)):
            c = np.array(a) + (np.array(b) - np.array(a)) * u
            o += line([P(c + n * 30), P(c + d * 8), P(c - n * 26)], 2.6, far_c(fold, far), seed=seed + i, op=.85, peak=.4)
        o += _plaid_band(a, b, d, n, far, seed + 3)
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


def plaid_parts():
    """Клетчатая рубашка бородача (профиль вправо): красная клетка с тёмно-синими полосами и светлыми нитками, планка с пуговицами,
    нагрудный карман, острый воротник."""
    body = [(-112, 34), (-120, -40), (-132, -170), (-128, -280), (-112, -360), (-78, -410), (-20, -432), (40, -426),
            (84, -398), (112, -330), (126, -230), (124, -120), (116, -20), (110, 34)]
    inner = ""
    for k, x0 in enumerate(range(-150, 160, 64)):           # вертикальные полосы клетки
        inner += blob([(x0, -470), (x0 + 22, -470), (x0 + 22, 60), (x0, 60)], C["PLAID"], .55)
        inner += line([(x0 + 40, -470), (x0 + 40, 60)], 1.6, C["PLAID2"], seed=660 + k, op=.55)
    for k, y0 in enumerate(range(-460, 60, 64)):            # горизонтальные полосы
        inner += blob([(-160, y0), (160, y0), (160, y0 + 22), (-160, y0 + 22)], C["PLAID"], .5)
        inner += line([(-160, y0 + 40), (160, y0 + 40)], 1.6, C["PLAID2"], seed=680 + k, op=.5)
    inner += blob([(30, -440), (130, -380), (140, 40), (60, 40), (80, -200)], C["TOP_SH2"], .45)
    inner += blob([(-140, -300), (-100, -320), (-104, -100), (-140, -60)], C["TOP_SH2"], .35)
    # планка с пуговицами
    inner += shape([(58, -420), (74, -420), (92, 40), (76, 40)], C["TOP"], blob([(58, -420), (74, -420), (92, 40), (76, 40)], C["PLAID"], .25), w=2.6, seed=700)
    for k, y in enumerate((-370, -280, -190, -100, -14)):
        x = 68 + (y + 420) * .036
        inner += f'<circle cx="{x:.1f}" cy="{y}" r="6" fill="{C["PLAID2"]}"/><circle cx="{x:.1f}" cy="{y}" r="6" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    # нагрудный карман с клапаном
    inner += shape([(-24, -306), (40, -310), (42, -236, 1), (-20, -232, 1)], C["TOP"],
                   "".join(blob([(-30, y0), (50, y0), (50, y0 + 12), (-30, y0 + 12)], C["PLAID"], .55) for y0 in (-296, -260)), w=3.0, seed=701)
    inner += shape([(-28, -310), (44, -314), (44, -290), (8, -282), (-26, -290)], C["TOP_SH"], "", w=3.0, seed=702)
    inner += line([(-80, -150), (-40, -120), (-6, -110)], 2.6, C["FOLD"], seed=703, op=.7)
    inner += line([(-112, 20), (110, 20)], 2.0, C["FOLD"], seed=704, op=.6)
    torso = shape(body, C["TOP"], inner, w=5.2, seed=705)
    col = [(-60, -440), (-20, -462), (40, -452), (78, -424), (96, -380), (60, -398), (24, -424), (-30, -426), (-70, -410)]
    back = shape(col, C["TOP_SH"], line([(-50, -432), (30, -438)], 1.6, C["PLAID"], seed=706, op=.8), w=4.0, seed=707)
    tip = shape([(30, -440), (80, -420), (100, -372), (66, -390), (40, -420)], C["TOP"], blob([(30, -440), (100, -372), (80, -380)], C["PLAID"], .4),
                w=3.4, seed=708)
    return back, torso, tip


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
    if pose.get("lotus") is not None:
        out["legs"] = G(lotus_legs(pose["lotus"], lean))
    elif pose.get("feet"):
        for side in ("f", "n"):
            A, phi = pose["feet"][side]
            A = L(A)
            hipj = np.array([10.0 if side == "n" else -4.0, 0.0])
            lk = KID_LEG_K if who == "kid" else 1.0
            K, A2 = ik2(hipj, A, THIGH * lk, SHIN * lk, +1)
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

    def arm_svg(side, hand_only=False):
        sp, E, Wr = arms[side]
        far = side == "f"
        d = (Wr - E) / np.linalg.norm(Wr - E)
        hs = pose.get("hands", {}).get(side, {"kind": "open"})
        hd = hs.get("dir")
        if hd is not None:
            d = np.array(hd, float) / np.linalg.norm(hd)
        o = "" if hand_only else sleeve(sp, E, Wr, far, 600 + (0 if far else 50), who)
        kw = hand_kw()
        if far:
            kw.update(skin=far_c(C["SKIN"], True), skin_sh=far_c(C["SKIN_SH"], True))
        kind = hs.get("kind", "open")
        k = hs.get("k", 1.0)
        if kind == "mudra":
            o += mudra(Wr + d * 2, d, k=k, flip=hs.get("flip", 1), far=far, seed=700 + (0 if far else 40))
        elif kind == "open":
            o += Hand.hand(Wr + d * 2, d, flip=hs.get("flip", 1), k=k, curl=hs.get("curl", (0.15, .1, .15, .2)), spread=hs.get("spread", .2),
                           thumb=hs.get("thumb", .2), bend=hs.get("bend", .1), seed=700 + (0 if far else 40), nails=not far, **kw)
        return o

    out["arm_f"] = G(arm_svg("f"))
    out["hand_f"] = G(arm_svg("f", hand_only=True))
    if pose.get("feet") is None and pose.get("lotus") is None and pose.get("pelvis", True):
        pel = ellipse_pts(0, -6, 128, 70, 14, rot=math.degrees(lean))
        out["pelvis"] = G(shape(pel, C["LEGS"], blob(ellipse_pts(40, 20, 120, 50, 12), C["LEGS_SH"], .7), w=4.6, seed=880))
    if who in ("dima", "cap"):
        back, torso, strings = hoodie_parts(pose.get("hood", 0.0), pose.get("strings", (0, 0)))
    elif who == "kid":
        back, torso, strings = pajama_parts()
    elif who in ("girl", "bob"):
        back, torso, strings = sweater_parts()
    elif who == "beard":
        back, torso, strings = plaid_parts()
    elif who == "pal":
        back, torso, strings = tee_parts()
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
    hk = KID_HEAD_K if who == "kid" else 1.0
    if who == "kid":
        hf = kid_head
    body += f'<g transform="translate({hpos[0]:.2f} {hpos[1]:.2f}) rotate({math.degrees(lean * .5 + ha):.3f}) scale({hk})">{hf(ex_)}</g>'
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
HEIGHT = {"pal": 1.03, "dima": 1.0, "kid": .66, "mama": .92, "girl": .96, "bald": 1.08, "cap": 1.02, "friend": 1.06, "bob": .95, "beard": 1.05}
FACES = ("pal", "dima", "kid", "mama", "girl", "bald", "cap", "friend", "bob", "beard")


def figure(who, x, y, scale=0.5, expr=None, lean=0.0, head_ang=0.0, arms=None, hands=None, feet=None, flip=False, layers=None, torso_k=1.0, hood=0.0,
           head_off=(0, 0), extra=None, lotus=None):
    """Человек по пояс (feet=None) или с ногами (feet={'n': (ankle, phi), 'f': ...}). (x, y) — таз в мире, scale — масштаб (голова ≈ 300·scale).
    arms по умолчанию — руки вниз. layers — подмножество {'legs','pelvis','arm_f','body','arm_n'} в порядке отрисовки (по умолчанию все).
    Возвращает dict(svg=..., head=(x, y), wrist={'n','f'}, elbow=...) — координаты уже с учётом flip."""
    sc = scale * HEIGHT.get(who, 1.0)
    if arms is None:
        arms = {"f": ("ang", 0.18, 0.18), "n": ("ang", -0.1, 0.25)}
    pose = dict(hip=(x, y), scale=sc, lean=lean, feet=feet, arms=arms, hands=hands or {}, head_ang=head_ang, expr=expr or {}, torso_k=torso_k,
                hood=hood, head_off=head_off, lotus=lotus)
    if extra:
        pose.update(extra)
    o = draw(pose, who)
    order = layers or (("arm_f", "body", "legs", "hand_f", "arm_n") if lotus is not None else ("legs", "pelvis", "arm_f", "body", "arm_n"))
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


# ═════════════════════════════ ГОТОВЫЕ ПОЗЫ И МИМИКА РИЛСА 61 ═════════════════════════════
# EXPR[who][имя] -> dict мимики (копию можно править: dict(EXPR["dima"]["zeal"], look=(.5, 0))).
EXPR = {
    "dima": {"guilty": {"brows": "worry", "mouth": "smile", "smile": .45, "lid": .6, "look": (-.5, .15), "blush": .55},
             "gloom": {"brows": "tired", "mouth": "tired", "lid": .38, "look": (.1, .55)},
             "zeal": {"brows": "up", "mouth": "grin", "open": .8, "lid": 1.0, "look": (.5, .25), "hair": 6},
             "focus": {"brows": "det", "mouth": "flat", "lid": .62, "look": (.55, .45)},
             "calm_smile": {"brows": "calm", "mouth": "smile", "smile": 1.0, "lid": .72, "look": (0, 0)}},
    "mama": {"brow_up": {"brows": "skeptic", "mouth": "pursed", "lid": .82, "look": (.2, 0)},
             "pursed": {"brows": "frown", "mouth": "pursed", "lid": .6, "look": (.3, .1)},
             "talk": {"brows": "skeptic", "mouth": "talk", "open": .5, "smile": 0, "lid": .8},
             "sigh": {"brows": "sad", "mouth": "flat", "lid": .5, "closed": .55}},
    "bob": {"calm": {"brows": "calm", "mouth": "smile", "smile": .4, "lid": .75, "look": (.4, 0)},
            "think": {"brows": "worry", "mouth": "flat", "lid": .8, "look": (.4, -.6)},
            "bite": {"brows": "up", "mouth": "talk", "open": .7, "smile": .3, "lid": .9},
            "pleased": {"brows": "calm", "mouth": "smile", "smile": 1.0, "lid": .6}},
    "beard": {"think": {"brows": "worry", "mouth": "flat", "lid": .8, "look": (.3, -.6)},
              "idea": {"brows": "up", "mouth": "grin", "open": .7, "lid": 1.0, "look": (.4, -.4)},
              "calm": {"brows": "calm", "mouth": "flat", "smile": .3, "lid": .75}},
}

# POSE[имя] -> (lean, head_ang, arms, hands): цели рук — в долях масштаба от таза (x, y)·sc; pose_kw() переводит в мир.
POSE = {
    # сидит за столом: предплечья на крышке (крышка на ~ −190·sc от таза)
    "sit_desk": (0.08, 0.0, {"f": ("ik", (190, -200), -1), "n": ("ik", (240, -195), -1)},
                 {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.3, .3, .35, .4), "thumb": .3}}),
    # сползает, щека на ладони: локоть на столе, кисть вверх у щеки
    "slump": (0.36, 0.3, {"f": ("ik", (230, -175), -1), "n": ("ik", (215, -330), 1)},
              {"f": {"curl": (.5, .5, .55, .6), "thumb": .4}, "n": {"dir": (0.25, -1), "curl": (.1, .15, .2, .25), "thumb": .1}}),
    # рисует маркером: ближняя кисть вперёд-вниз (маркер в кулаке кладёт вызывающий), дальняя придерживает лист
    "draw": (0.2, 0.12, {"f": ("ik", (200, -210), -1), "n": ("ik", (285, -250), -1)},
             {"f": {"curl": (.2, .2, .25, .3), "thumb": .2}, "n": {"kind": "none"}}),
    # ставит галочку: то же, рука дальше и выше
    "tick": (0.16, 0.1, {"f": ("ik", (190, -205), -1), "n": ("ik", (300, -265), -1)},
             {"f": {"curl": (.3, .3, .35, .4), "thumb": .3}, "n": {"kind": "none"}}),
    # раскидывает руки на стуле: ближняя вперёд-вверх, дальняя назад-вверх, ладони раскрыты
    "arms_wide": (-0.06, -0.08, {"f": ("ang", -2.45, 0.3), "n": ("ang", 2.25, -0.3)},
                  {"f": {"spread": .4, "curl": (0, 0, .05, .1), "thumb": 0}, "n": {"spread": .45, "curl": (0, 0, .05, .1), "thumb": 0}}),
    # мама: обводит рукой комнату (ладонь раскрыта вверх-вперёд)
    "sweep": (0.0, 0.0, {"f": ("ang", 0.2, 0.25), "n": ("ang", 1.35, 0.25)},
              {"f": {"curl": (.3, .3, .3, .35)}, "n": {"spread": .35, "curl": (0, .05, .1, .15), "thumb": .05}}),
    # мама: скрестила руки на груди (кисти прячутся под локтями)
    "cross": (-0.04, 0.0, {"f": ("ik", (120, -250), -1), "n": ("ik", (-60, -250), 1)},
              {"f": {"kind": "none"}, "n": {"kind": "none"}}),
    # руки вниз, спокойно
    "rest": (0.0, 0.0, {"f": ("ang", 0.18, 0.18), "n": ("ang", -0.1, 0.25)}, {}),
}


def pose_kw(name, x, y, scale, who="dima"):
    """Аргументы figure() для готовой позы: figure(who, x, y, scale, expr, **pose_kw(name, x, y, scale, who))."""
    lean, ha, arms, hands = POSE[name]
    sc = scale * HEIGHT.get(who, 1.0)
    A = {}
    for k, a in arms.items():
        if a[0] == "ik":
            A[k] = ("ik", (x + a[1][0] * sc, y + a[1][1] * sc), a[2])
        else:
            A[k] = a
    return dict(lean=lean, head_ang=ha, arms=A, hands={k: dict(v) for k, v in hands.items()})


def mix_pose(a, b, u, x, y, scale, who="dima"):
    """Плавный переход между двумя позами (только ik-цели и наклон; у 'ang'-рук берётся ближайшая)."""
    A, B = pose_kw(a, x, y, scale, who), pose_kw(b, x, y, scale, who)
    u = max(0.0, min(1.0, u))
    arms = {}
    for k in ("f", "n"):
        pa, pb = A["arms"][k], B["arms"][k]
        if pa[0] == pb[0] == "ik":
            arms[k] = ("ik", tuple(pa[1][i] + (pb[1][i] - pa[1][i]) * u for i in (0, 1)), pb[2])
        elif pa[0] == pb[0] == "ang":
            arms[k] = ("ang", pa[1] + (pb[1] - pa[1]) * u, pa[2] + (pb[2] - pa[2]) * u)
        else:
            arms[k] = pb if u > .5 else pa
    return dict(lean=A["lean"] + (B["lean"] - A["lean"]) * u, head_ang=A["head_ang"] + (B["head_ang"] - A["head_ang"]) * u, arms=arms,
                hands=B["hands"] if u > .5 else A["hands"])


# ═════════════════════════════ КОТ: ШАГ И ПРЫЖОК (анфас, как look/hero.png) ═════════════════════════════
def cat_walk(x, y, k, t, st=None, period=0.5):
    """Кот шагает на месте/вдоль (x двигает вызывающий): лапы по очереди, тело чуть качается и подпрыгивает."""
    ph = t / period
    st = dict(st or {})
    st.setdefault("walk", ph)
    bob = abs(math.sin(math.pi * ph)) * 6 * k
    st.setdefault("rot", 2.2 * math.sin(2 * math.pi * ph))
    st.setdefault("tail", 6 * math.sin(2 * math.pi * ph * .5))
    return cat_svg(x, y - bob, k, st, t)


def cat_jump(p0, p1, k, u, t, st=None, height=None):
    """Прыжок с толчком задних лап из p0 (точка между лап) в p1. u 0..1: 0–.3 присед, .3–.4 толчок (лапы вытянуты),
    .4–.85 полёт по дуге, .85–1 приземление с сжатием. Возвращает SVG."""
    st = dict(st or {})
    p0, p1 = np.array(p0, float), np.array(p1, float)
    hgt = height if height is not None else max(80.0, abs(p1[1] - p0[1]) * .5 + 120) * k / .45
    if u < .3:
        e = u / .3
        st.update(sy=1 - .2 * math.sin(e * math.pi / 2), sx=1 + .1 * math.sin(e * math.pi / 2), perk=1.0)
        pos = p0
    elif u < .4:
        e = (u - .3) / .1
        st.update(sy=.8 + .42 * e, sx=1.1 - .18 * e, legs=e, perk=1.0)
        pos = p0 + np.array([0, -30 * k * e])
    elif u < .85:
        e = (u - .4) / .45
        pos = p0 + (p1 - p0) * e + np.array([0, -hgt * 4 * e * (1 - e)])
        st.update(sy=1.12 - .12 * e, sx=.92 + .08 * e, legs=1 - .6 * e, rot=(-8 + 14 * e) * np.sign(p1[0] - p0[0] or 1), perk=1.0, tail=-12 + 20 * e)
    else:
        e = (u - .85) / .15
        sq = math.sin(e * math.pi)
        st.update(sy=1 - .16 * sq, sx=1 + .1 * sq, perk=1 - e)
        pos = p1
    return cat_svg(float(pos[0]), float(pos[1]), k, st, t)


# ═════════════════════════════ РИЛС 62: ПОЗА ЛОТОСА, КИСТЬ «КОЛЕЧКО», ФУТБОЛКА ДРУГА ═════════════════════════════
def _lerp(a, b, u):
    return np.array(a, float) + (np.array(b, float) - np.array(a, float)) * u


def sock(A, dirv, far, seed, up=0.0):
    """Босая ступня (лотос): A — щиколотка, dirv — куда смотрят пальцы, up — подошва к зрителю (0..1: розоватая подошва)."""
    d = np.array(dirv, float)
    d /= np.linalg.norm(d) + 1e-9
    n = np.array([-d[1], d[0]])
    if n[1] > 0:
        n = -n          # n — вверх

    def tf(x, y):
        return P(A + d * x + n * y)
    sk, sh, sh2 = far_c(C["SKIN"], far), far_c(C["SKIN_SH"], far), C["SKIN_SH2"]
    o = []
    # пальцы — бугорки на конце, большой палец сверху
    for i, (x, y, r) in enumerate(((104, 22, 15), (112, 4, 12), (114, -12, 11), (110, -26, 10))):
        o.append(shape(ellipse_pts(*tf(x, y), r * 1.15, r, 10), sk, "", w=3.0, seed=seed + 10 + i))
    pts = [tf(-40, 26), tf(0, 34), tf(60, 32), tf(100, 30), tf(108, 8), tf(104, -22), tf(80, -34), tf(30, -36), tf(-24, -34), tf(-48, -6)]
    inner = blob([tf(-48, -36), tf(108, -30), tf(108, -12), tf(-48, -14)], sh, .8)
    if up > .3:        # подошва: розоватая пятка и подушечка
        inner += blob(ellipse_pts(*tf(-6, 2), 24, 18, 10), "#e7a796", .55)
        inner += blob(ellipse_pts(*tf(76, 2), 20, 18, 10), "#e7a796", .5)
    inner += line([tf(-20, 22), tf(30, 16), tf(70, 20)], 2.0, sh2, seed=seed + 3, op=.6)
    o.insert(0, "")
    o.append(shape(pts, sk, inner, w=4.2, seed=seed))
    # щель между пальцами поверх ступни
    o.append(line([tf(96, 12), tf(106, 12)], 1.8, sh2, seed=seed + 20, op=.8))
    return "".join(o)


def lotus_legs(lot, lean=0.0):
    """Ноги в позе лотоса (в системе таза, профиль-3/4 вправо): колени в стороны, голени скрещены перед тазом, ступни в носках
    лежат у противоположных колен. lot: fold 0..1 (0 — ноги свободно висят вперёд-вниз, как в полёте; 1 — сложены),
    spread (ширина колен), squash (сжатие по вертикали при приземлении), sag (колени опущены — сполз)."""
    fold = float(lot.get("fold", 1.0))
    sp = float(lot.get("spread", 1.0))
    sag = float(lot.get("sag", 0.0))
    f = lib.clamp(fold)
    Hn, Hf = np.array([46.0, 18.0]), np.array([-44.0, 8.0])
    Kn = _lerp((190, 230), (300 * sp, 112 + 30 * sag), f)
    Kf = _lerp((60, 240), (-236 * sp, 72 + 30 * sag), f)
    An = _lerp((300, 470), (-70 * sp, 184), f)
    Af = _lerp((170, 480), (150 * sp, 156), f)
    o = []
    # дальнее бедро и голень за тазом
    o.append(limb_band(Hf, Kf, 140, 118, C["LEGS"], True, 801))
    pel = ellipse_pts(0, 10, 150, 78, 14)
    o.append(shape(pel, C["LEGS"], blob(ellipse_pts(40, 34, 130, 50, 12), C["LEGS_SH"], .7), w=4.6, seed=880))
    o.append(limb_band(Hn, Kn, 146, 122, C["LEGS"], False, 802,
                       lambda a, b, d, n: blob([P(np.array(a) + n * 60), P(np.array(b) + n * 50), P(np.array(b) + n * 14), P(np.array(a) + n * 20)],
                                               C["LEGS_SH"], .8)))
    # нижняя голень (ближняя нога, уходит влево под дальнее колено) и её ступня
    dn = An - Kn
    o.append(limb_band(Kn, An, 112, 86, C["LEGS"], False, 803,
                       lambda a, b, d, n: blob([P(np.array(a) - n * 50), P(np.array(b) - n * 40), P(np.array(b) - n * 14), P(np.array(a) - n * 16)],
                                               C["LEGS_SH"], .85)))
    o.append(sock(An, dn if f > .5 else (1.0, .25), False, 805, up=f))
    # верхняя голень (дальняя нога поверх, ступня ложится на ближнюю голень у колена)
    df = Af - Kf
    o.append(limb_band(Kf, Af, 110, 84, C["LEGS"], f < .5, 804,
                       lambda a, b, d, n: blob([P(np.array(a) + n * 48), P(np.array(b) + n * 38), P(np.array(b) + n * 12), P(np.array(a) + n * 14)],
                                               C["LEGS_SH"], .85)))
    o.append(sock(Af, df if f > .5 else (1.0, .3), f < .5, 806, up=f))
    sq = float(lot.get("squash", 0.0))
    body = "".join(o)
    if abs(sq) > 1e-3:
        body = f'<g transform="translate(0 60) scale({1 + .5 * sq:.4f} {1 - sq:.4f}) translate(0 -60)">{body}</g>'
    return body


def lotus_knees(x, y, scale, spread=1.0, sag=0.0, who="dima"):
    """Мировые точки колен в лотосе (куда класть кисти): {'n': (x, y), 'f': (x, y)}."""
    sc = scale * HEIGHT.get(who, 1.0)
    return {"n": (x + 300 * spread * sc, y + (112 + 30 * sag) * sc), "f": (x - 236 * spread * sc, y + (72 + 30 * sag) * sc)}


def mudra(Wr, d, k=1.0, flip=1, far=False, seed=0):
    """Кисть на колене, «колечко»: кончики большого и указательного сомкнуты кольцом (в кольце — просвет бумаги),
    средний, безымянный и мизинец расслаблены и чуть согнуты."""
    kw = hand_kw()
    if far:
        kw.update(skin=far_c(C["SKIN"], True), skin_sh=far_c(C["SKIN_SH"], True))
    Wr = np.array(Wr, float)
    d = np.array(d, float) / (np.linalg.norm(d) + 1e-9)
    n = np.array([-d[1], d[0]]) * flip
    skin, sh2 = kw["skin"], kw["skin_sh2"]
    o = [Hand.hand(Wr, d, flip=flip, k=k, curl=(1.0, .38, .44, .5), spread=.1, thumb=1.0, bend=.12, seed=seed, nails=not far,
                   show_thumb=False, **kw)]
    # кольцо у корня указательного: центр чуть впереди ладони, на стороне большого пальца
    c = Wr + d * 92 * k - n * 22 * k
    R = 18 * k
    wf = 12 * k
    ang = np.linspace(0, 2 * np.pi, 40)
    ringp = [P(c + (math.cos(a) * d + math.sin(a) * n) * R) for a in ang]
    ink_w = 3.0 * lib.INK_K[0]
    path = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in ringp) + "Z"
    # большой палец от основания ладони вдоль края к кольцу (под кольцом)
    base = Wr + d * 14 * k - n * 30 * k
    th = band([P(base), P(_lerp(base, c, .5) - n * 6 * k), P(c - d * R * .6 - n * R * .5)], 26 * k, 17 * k, step=2.5, cap=False)
    o.append(shape(th, skin, "", w=3.0, seed=seed + 51))
    o.append(f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="{wf + 2 * ink_w:.1f}"/>'
             f'<path d="{path}" fill="none" stroke="{skin}" stroke-width="{wf:.1f}"/>')
    # тень на нижней дуге кольца и стык подушечек
    o.append(line([P(c + (math.cos(a) * d + math.sin(a) * n) * R) for a in np.linspace(.4, 2.2, 8)], wf * .35, kw["skin_sh"], seed=seed + 53, op=.8,
                  taper=.2, wmin=.6))
    q = c - n * R
    o.append(line([P(q - d * wf * .45), P(q + d * wf * .45)], 2.0, INK, seed=seed + 52, op=.9))
    if not far:
        o.append(line([P(c + n * R - d * 4 * k), P(c + n * R + d * 8 * k)], 1.6, sh2, seed=seed + 54, op=.8))
    return "".join(o)


def tee_parts():
    """Зелёная футболка друга: круглый ворот, складки, без капюшона и кармана."""
    body = [(-112, 34), (-120, -40), (-132, -170), (-128, -280), (-112, -360), (-78, -410), (-20, -432), (40, -426), (84, -398), (112, -330),
            (126, -230), (124, -120), (116, -20), (110, 34)]
    inner = blob([(30, -440), (130, -380), (140, 40), (60, 40), (80, -200)], C["TOP_SH"], .85)
    inner += blob([(-140, -300), (-100, -320), (-104, -100), (-140, -60)], C["TOP_SH"], .55)
    inner += line([(-80, -140), (-40, -110), (-6, -100)], 2.6, C["FOLD"], seed=703, op=.7)
    inner += line([(-60, -30), (-10, -12), (40, -20)], 2.4, C["FOLD"], seed=704, op=.6)
    inner += line([(-118, 26), (114, 26)], 2.4, C["TOP_SH2"], seed=705, op=.8)
    torso = shape(body, C["TOP"], inner, w=5.2, seed=706)
    col = [(-50, -440), (-14, -458), (40, -450), (66, -424), (48, -404), (18, -426), (-28, -428), (-60, -414)]
    back = shape(col, C["TOP_SH2"], line([(-40, -434), (30, -440)], 2.2, C["STITCH"], seed=707, op=.7), w=4.0, seed=708)
    return back, torso, ""


# Мимика рилса 62 (комедия медитации): EXPR["dima"][имя]. Каждая — своя, чтобы планы не повторялись лицом.
EXPR["dima"].update({
    "solemn": {"brows": "solemn", "mouth": "flat", "lid": .55, "look": (.2, -.1)},                         # торжественно: брови вверх, рот ровно
    "bliss": {"brows": "calm", "mouth": "smile", "smile": .9, "shut": 1.0},                                # блаженно, глаза дугами
    "smack": {"brows": "calm", "mouth": "smack", "chew": .6, "shut": 1.0, "drool": .6},                   # причмокивает
    "one_eye": {"brows": "one_up", "mouth": "frown", "shut_n": 1.0, "lid": 1.0, "scale_f": 1.35, "look": (.8, 0)},   # один глаз распахнут
    "squeeze": {"brows": "pinch", "mouth": "frown", "squeeze": 1.0},                                       # напряжённо зажмурен
    "upset": {"brows": "sad", "mouth": "wobble", "lid": .45, "look": (0, .5)},                             # расстроен, губа дрожит
    "side_eye": {"brows": "sad", "mouth": "flat", "lid": .5, "look": (.95, .1), "shut_n": 1.0},           # косится одним глазом
    "soft": {"brows": "calm", "mouth": "smile", "smile": .55, "shut": 1.0},                                # мягкая улыбка, глаза закрыты
    "friendly": {"brows": "up", "mouth": "grin", "open": .55, "lid": .85, "look": (-.35, 0)},               # дружелюбно в камеру
    "side_smile": {"brows": "calm", "mouth": "side", "shut": 1.0},                                        # улыбка краем рта
})
EXPR["pal"] = {"hurt": {"brows": "skeptic", "mouth": "pursed", "lid": .8, "look": (.3, -.1)},            # обиженная бровь, губы поджаты
               "cross": {"brows": "frown", "mouth": "talk", "open": .5, "smile": 0, "lid": .85},             # возмущается
               "calm": {"brows": "calm", "mouth": "smile", "smile": .6, "lid": .8}}

# Позы рук в лотосе: цели — от колен (lotus_knees), направление кисти — вниз-вперёд по колену.
def lotus_kw(name, x, y, scale, u=0.0, who="dima", spread=1.0, sag=0.0):
    """Аргументы figure() для Димы в лотосе: figure("dima", x, y, s, expr, **lotus_kw("sit", x, y, s)).
    name: sit (кисти на коленях, «колечко»), slump (сполз: плечи вниз, кисти съехали), push (ближняя ладонь толкает вперёд-вверх; u — вытянута 0..1),
    flick (ближняя кисть у виска, щелчок; u 0..1 — палец распрямился), wave (машет ближней рукой; u — фаза), fidget (ёрзает; u — фаза).
    Таз (x, y) — на подушке; дальше вызывающий кладёт свой наклон/смещение поверх."""
    sc = scale * HEIGHT.get(who, 1.0)
    kn = lotus_knees(x, y, scale, spread, sag, who)
    lot = {"fold": 1.0, "spread": spread, "sag": sag}
    mud = {"kind": "mudra", "k": 1.0}
    f_tgt = ("ik", (kn["f"][0] + 30 * sc, kn["f"][1] - 40 * sc), 1)
    n_tgt = ("ik", (kn["n"][0] - 40 * sc, kn["n"][1] - 46 * sc), -1)
    hands = {"f": dict(mud, dir=(-.35, 1)), "n": dict(mud, dir=(.45, 1))}
    lean, ha = 0.0, 0.0
    if name == "slump":
        lean, ha = .22, .32
        f_tgt = ("ik", (kn["f"][0] + 70 * sc, kn["f"][1] + 10 * sc), 1)
        n_tgt = ("ik", (kn["n"][0] - 90 * sc, kn["n"][1] + 6 * sc), -1)
        hands = {"f": {"dir": (.1, 1), "curl": (.3, .35, .4, .45), "thumb": .5}, "n": {"dir": (.1, 1), "curl": (.3, .35, .4, .45), "thumb": .5}}
    elif name == "fidget":
        lean = .06 * math.sin(2 * math.pi * u)
    elif name == "push":
        e = lib.clamp(u)
        n_tgt = ("ik", (x + (150 + 260 * e) * sc, y - (420 + 40 * e) * sc), -1)
        hands = {"f": hands["f"], "n": {"dir": (.15, -1), "spread": .35, "curl": (0, .02, .05, .1), "thumb": .1}}
    elif name == "flick":
        e = lib.clamp(u)
        n_tgt = ("ik", (x + 250 * sc, y - 560 * sc), -1)
        hands = {"f": hands["f"], "n": {"dir": (.6, -1), "curl": (.85 - .8 * e, .8, .8, .8), "thumb": .9 - .4 * e, "spread": .1}}
    elif name == "wave":
        a = math.sin(2 * math.pi * u)
        n_tgt = ("ik", (x + (230 + 50 * a) * sc, y - 640 * sc), -1)
        hands = {"f": hands["f"], "n": {"dir": (.3 * a, -1), "spread": .35, "curl": (0, 0, .05, .1), "thumb": .05}}
    return dict(lean=lean, head_ang=ha, arms={"f": f_tgt, "n": n_tgt}, hands=hands, lotus=lot)


def mobilnik(cx, cy, k=1.0, rot=0.0, seed=950):
    """Мобильник-силуэт: тёмный скруглённый корпус без экрана, кнопок и букв (в руке друга)."""
    pts = lib.T(lib.rrect(-34, -62, 34, 62, 12), cx, cy, k, rot)
    return shape(pts, "#2b2e36", blob(lib.T(lib.rrect(-30, -58, -6, 58, 8), cx, cy, k, rot), "#3c414c", .9), w=4.0, seed=seed)
