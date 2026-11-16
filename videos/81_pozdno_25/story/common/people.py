"""Люди рилса 63 «кофе» (копия common/people.py рилса 62 + раздел «РИЛС 63» в конце: мимика EXPR, рот «puff», мешки по
выбору expr["bags"], стойка и шаг stand_kw/walk_kw, жонглирование juggle_arc, хват кружки за ручку handle_grip).
Прежняя шапка: Люди рилса 61 «стол» (основа — common/people.py рилса 60). Новое в 61: участники эксперимента who="bob" (каре, круглые очки,
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
KIDS = ("kid", "kid2")      # рилс 64: kid2 — маленький Дима-школьник в свитере
HEADS64 = ("teacher_y", "teacher_o", "psych", "curly", "youth", "father")
CLOTHES64 = {}             # заполняется в разделе «РИЛС 64» в конце файла
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
    stb = expr.get("stubble", 1.0)      # рилс 80: 0 — подросток без щетины, 1 — как было (байт в байт)
    if stb > .01:
        inner.append(blob([(-60, 70), (-20, 92), (30, 106), (80, 94), (106, 70), (110, 130), (-60, 130)], "#9e8a96", .42 * min(1.0, stb)))
    rs = np.random.RandomState(7)
    for _ in range(120):
        x, y = rs.uniform(-56, 108), rs.uniform(70, 124)
        if (x - 30) ** 2 / 92 ** 2 + (y - 56) ** 2 / 70 ** 2 > 1.0 or y > 120 - abs(x - 30) * .15:
            continue
        r_ = rs.uniform(1.2, 2.2)
        if stb >= 1.0:
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_:.1f}" fill="#5c4446" opacity=".55"/>')
        elif stb > .01:
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_:.1f}" fill="#5c4446" opacity="{.55 * stb:.3f}"/>')
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
    s.append(eyes(expr, EYE_N, EYE_F, bags=expr.get("bags", True)))
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
    if m == "puff":        # надутые щёки (пьёт через силу): губы сжаты бантиком, щёки округлены тенью и складкой
        pf = expr.get("puff", 1.0)
        o = blob(ellipse_pts(100, 52, 20 + 6 * pf, 22 + 6 * pf, 12), "#e98a86", .35 * pf) + blob(ellipse_pts(0, 58, 34 + 8 * pf, 26 + 6 * pf, 12), "#e98a86", .3 * pf)
        o += line([(-40, 30), (-48, 62), (-34, 92)], 2.6, C["SKIN_SH2"], seed=184, op=.8 * pf)
        o += line([(104, 72), (112, 54)], 2.4, C["SKIN_SH2"], seed=185, op=.8 * pf)
        o += shape(ellipse_pts(64, 92, 13, 8, 10), "#c86b6b", line([(54, 92), (74, 92)], 2.4, "#5a2b33", seed=186), w=3.8, seed=187)
        return o
    if m == "wobble":      # расстроен: уголки вниз, нижняя губа дрожит (trem — фаза)
        tr = expr.get("trem", 0.0)
        j = 2.6 * math.sin(tr * 2 * math.pi * 7)
        o = line([(36, 98), (48, 88 + j * .4), (62, 86 - j * .5), (76, 87 + j * .5), (92, 98)], 4.8, seed=165, peak=.5)
        o += line([(48, 102 + j), (62, 106 - j), (78, 102 + j)], 2.6, C["SKIN_SH2"], seed=167, op=.85)
        o += line([(32, 100), (38, 108)], 2.2, C["SKIN_SH2"], seed=168, op=.7)
        return o
    if m == "pressed":     # рилс 64: губы сжаты (слова не вышли) — плотная короткая линия, ямочки в уголках, складка под губой
        return (line([(42, 92), (56, 90), (72, 90), (86, 93)], 6.0, seed=165, peak=.5)
                + line([(38, 88), (42, 96)], 2.2, C["SKIN_SH2"], seed=169, op=.85) + line([(88, 89), (91, 97)], 2.2, C["SKIN_SH2"], seed=170, op=.85)
                + line([(54, 104), (72, 104)], 2.2, C["SKIN_SH2"], seed=171, op=.7))
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
    if m == "puff":        # надутые щёки (пьёт через силу): губы сжаты бантиком, щёки округлены тенью и складкой
        pf = expr.get("puff", 1.0)
        o = blob(ellipse_pts(100, 52, 20 + 6 * pf, 22 + 6 * pf, 12), "#e98a86", .35 * pf) + blob(ellipse_pts(0, 58, 34 + 8 * pf, 26 + 6 * pf, 12), "#e98a86", .3 * pf)
        o += line([(-40, 30), (-48, 62), (-34, 92)], 2.6, C["SKIN_SH2"], seed=184, op=.8 * pf)
        o += line([(104, 72), (112, 54)], 2.4, C["SKIN_SH2"], seed=185, op=.8 * pf)
        o += shape(ellipse_pts(64, 92, 13, 8, 10), "#c86b6b", line([(54, 92), (74, 92)], 2.4, "#5a2b33", seed=186), w=3.8, seed=187)
        return o
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
    elif style == "cap" and expr.get("nocap"):     # рилс 81: кепка снята — короткие седые волосы, без козырька
        s.append(shape([(-100, -70), (-130, -30), (-126, 10, 1), (-104, -4), (-96, 30), (-80, -10), (-70, -60)], C["HAIR"], "", w=4.6, seed=560))
        s.append(shape(ear, C["SKIN"], blob([(-132, -14), (-130, 22), (-116, 48), (-116, 10)], C["SKIN_SH"], .9), w=4.8, seed=561))
        top = [(112, -84), (106, -126), (74, -160), (20, -176), (-36, -172), (-86, -148), (-116, -106), (-118, -66), (-100, -76), (-70, -100),
               (-24, -110), (26, -110), (70, -104), (100, -90)]
        hi = blob([(-140, -190), (-30, -190), (-50, -120), (-96, -80), (-120, -40)], C["HAIR_SH"], .75)
        for i in range(9):
            x0 = -90 + i * 22
            hi += line([(x0, -150 + abs(i - 4) * 5), (x0 + 8, -122 + abs(i - 4) * 4)], 2.0, C["HAIR_SH"], seed=5800 + i, op=.7)
        s.append(shape(top, C["HAIR"], hi, w=5.0, seed=5810))
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
            lk = KID_LEG_K if who in KIDS else 1.0
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
    elif who in CLOTHES64:
        back, torso, strings = CLOTHES64[who]()
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
    if who in HEADS64:
        hf = lambda e, _w=who: head64(e, _w)  # noqa: E731
    hk = KID_HEAD_K if who in KIDS else 1.0
    if who in KIDS:
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


# ═════════════════════════════ РИЛС 63 «КОФЕ»: мимика, стойка, шаг, жонглирование, хват за ручку ═════════════════════════════
# Мимика: EXPR["dima"][имя]; у каждого плана своя. bags=False — мешков почти нет (бодрое утро s13).
EXPR["dima"].update({
    "scared": {"brows": "up", "mouth": "o", "open": .45, "lid": 1.0, "look": (.7, .45), "scale_n": 1.12, "scale_f": 1.12},     # испуг (s01)
    "wince": {"brows": "pinch", "mouth": "puff", "puff": 1.0, "squeeze": 1.0},                                                 # морщится, щёки надуты (s03)
    "relief": {"brows": "calm", "mouth": "smile", "smile": .75, "lid": .5, "look": (.2, .1)},                                  # облегчение
    "doubt": {"brows": "one_up", "mouth": "flat", "lid": .55, "look": (.65, .15)},                                            # недоверие
    "surprise": {"brows": "up", "mouth": "o", "open": .35, "lid": 1.0, "look": (.3, -.1)},                                    # удивление
    "smug": {"brows": "calm", "mouth": "side", "lid": .6, "look": (.35, 0)},                                                  # довольная полуулыбка
    "dull": {"brows": "tired", "mouth": "tired", "lid": .22, "look": (.25, .45)},                                             # тусклый взгляд (ночь)
    "saucer": {"brows": "up", "mouth": "o", "open": .25, "lid": 1.0, "look": (0, 0), "scale_n": 1.38, "scale_f": 1.38},       # глаза-блюдца
    "zombie": {"brows": "tired", "mouth": "o", "open": .12, "lid": .1, "look": (0, .6)},                                      # зомби (серое утро)
    "cheerful": {"brows": "up", "mouth": "smile", "smile": 1.0, "lid": .8, "look": (.4, 0), "bags": False},                   # бодрая улыбка
    "laugh": {"brows": "up", "mouth": "laugh", "open": .9, "laugh": 1.0, "hair": 4},                                          # смех
    "grimace_ok": {"brows": "worry", "mouth": "grin", "open": .4, "lid": .7, "look": (.4, -.2)},                              # облегчённая гримаса (поймал)
    "shrug": {"brows": "up", "mouth": "side", "lid": .7, "look": (-.2, 0)},                                                   # «ну и что», пожал плечами
})

LEG_LEN = THIGH + SHIN          # длина ноги от тазобедренного до щиколотки в L-единицах


def stand_kw(x, y, scale, who="dima", spread=60.0):
    """Стоит: щиколотки под тазом. Таз (x, y); вернёт dict(feet=...) для figure()."""
    sc = scale * HEIGHT.get(who, 1.0)
    ay = y + (LEG_LEN - 12) * sc
    return {"feet": {"n": ((x + spread * .55 * sc, ay), 0.0), "f": ((x - spread * .45 * sc, ay + 6 * sc), 0.0)}}


def walk_kw(x, y, scale, phase, who="dima", stride=230.0, lift=60.0):
    """Шаг с перекатом стопы (профиль вправо): phase — фаза цикла (1 = два шага). Возвращает dict(feet=..., hip=(x, y'), bob):
    таз (hip) ниже на опоре двумя ногами и выше на одной; стопа опорной ноги перекатывается пяткой → носком (phi)."""
    sc = scale * HEIGHT.get(who, 1.0)
    out = {}
    bob = -abs(math.cos(2 * math.pi * phase)) * 14 * sc + 7 * sc       # выше всего, когда ноги вместе
    hy = y + bob
    ground = y + (LEG_LEN - 12) * sc
    for side, off in (("n", 0.0), ("f", .5)):
        u = (phase + off) % 1.0
        if u < .5:      # опора: стопа идёт назад по земле, перекат пятка → носок
            v = u / .5
            ax = x + (stride * .5 - stride * v) * sc
            ay = ground
            phi = .32 * (1 - v) * 0 - .45 * max(0.0, v - .6) / .4 + .25 * max(0.0, .25 - v) / .25
        else:           # перенос: стопа по дуге вперёд, носок вверх
            v = (u - .5) / .5
            ax = x + (-stride * .5 + stride * v) * sc
            ay = ground - lift * math.sin(math.pi * v) * sc
            phi = -.35 * math.sin(math.pi * v * .8) + .25 * max(0.0, v - .7) / .3
        out[side] = ((ax, ay), phi)
    return {"feet": out, "hip": (x, hy), "bob": bob}


def juggle_arc(p0, p1, u, height):
    """Точка и угол предмета в полёте по параболе из p0 в p1 (u 0..1). Возвращает (x, y, rot_deg)."""
    x = p0[0] + (p1[0] - p0[0]) * u
    y = p0[1] + (p1[1] - p0[1]) * u - 4 * height * u * (1 - u)
    return x, y, 360.0 * u * (1 if p1[0] >= p0[0] else -1)


def handle_grip(who, hc, k=1.0, side=1, far=False, seed=960, hh=None):
    """Хват кружки за ручку: hc — центр ручки в мире, side +1 — ручка справа от кружки (кисть справа, пальцы влево сквозь ручку),
    k — масштаб кисти (≈ scale фигуры). Возвращает (back, front): back рисовать ДО кружки (ладонь и большой палец за ручкой),
    front — ПОСЛЕ кружки (пальцы поверх ручки)."""
    global C
    C = PAL[who]
    kw = hand_kw()
    kw.pop("nail", None)
    if far:
        kw.update(skin=far_c(C["SKIN"], True), skin_sh=far_c(C["SKIN_SH"], True))
    return Hand.grip(hc, 9 * k / .5 * .5, side, k=k * 1.15, seed=seed, h=(hh if hh is not None else 62), **kw)


# ═════════════════════════════ РИЛС 64 «СПАСИБО»: учительница, психолог, участники, отец, Дима-школьник ═════════════════════════════
# who: "teacher_y" / "teacher_o" — ОДНА женщина в двух возрастах (родинка над бровью, пучок, мягкий овал, тот же разрез глаз и улыбка);
#      "psych" — пожилой психолог (седые волосы, короткая седая борода, очки, вельветовый пиджак; НЕ портрет);
#      "curly" — участница с кудрями в очках (лавандовый свитер); "beard" — бородач в клетчатой рубашке (из 61); "youth" — юноша с короткой
#      стрижкой (синяя футболка); "father" — пожилой отец участницы (лысина, седые усы, кофта); "kid2" — маленький Дима (свитер).
PAL["teacher_y"] = dict(SKIN="#f2d0b4", SKIN_SH="#dba98c", SKIN_SH2="#c69078", HAIR="#7a4a2e", HAIR_SH="#55311c", HAIR_HI="#9c6a48",
                        TOP="#5f9a5c", TOP_SH="#477a45", TOP_SH2="#365e35", FOLD="#284628", STITCH="#b9dcae", TEE="#f4ece0", TEE_SH="#dccfbb",
                        LEGS="#4e4a5c", LEGS_SH="#3a3746", LEGS_SEAM="#6a6680", SHOE="#6b4a3a", SHOE_SH="#4f3529", SOLE="#e9e2d4", SOLE_SH="#c4bcad",
                        STRIPE="#a76a3e", NAIL="#f1cdbd", MOLE="#6e4434")
PAL["teacher_o"] = dict(PAL["teacher_y"], SKIN="#f0d2bc", SKIN_SH="#d9ab93", SKIN_SH2="#c4917c", HAIR="#dcdbe2", HAIR_SH="#a9a8b6", HAIR_HI="#f6f6fa",
                        TOP="#b0637a", TOP_SH="#8c4a5f", TOP_SH2="#6c3748", FOLD="#4f2534", STITCH="#e8b9c6", FRAME="#7a5a3a")
PAL["psych"] = dict(SKIN="#eac3a6", SKIN_SH="#d29f84", SKIN_SH2="#bb8970", HAIR="#d6d6dc", HAIR_SH="#a2a2ae", HAIR_HI="#f4f4f8",
                    TOP="#8a6644", TOP_SH="#6c4e32", TOP_SH2="#523a24", FOLD="#3a2818", STITCH="#b89668", TEE="#cfe0ee", TEE_SH="#a9c0d4",
                    LEGS="#4a4f58", LEGS_SH="#363a42", LEGS_SEAM="#6a707c", SHOE="#4a3324", SHOE_SH="#33231a", SOLE="#2a1f18", SOLE_SH="#1c1510",
                    STRIPE="#a76a3e", NAIL="#eec6aa", FRAME="#3a3a44")
PAL["curly"] = dict(SKIN="#f5d5bf", SKIN_SH="#dfad93", SKIN_SH2="#c9967e", HAIR="#3a2620", HAIR_SH="#22150f", HAIR_HI="#5e4034",
                    TOP="#8f7fc0", TOP_SH="#6f60a0", TOP_SH2="#55487f", FOLD="#3c325c", STITCH="#c9bfe8", TEE="#f4efe6", TEE_SH="#d9d2c4",
                    LEGS="#3d4558", LEGS_SH="#2c3342", LEGS_SEAM="#5d6780", SHOE="#6b4a3a", SHOE_SH="#4f3529", SOLE="#e9e2d4", SOLE_SH="#c4bcad",
                    STRIPE="#a76a3e", NAIL="#f6dccd", FRAME="#b4413c")
PAL["youth"] = dict(SKIN="#c99470", SKIN_SH="#ad7854", SKIN_SH2="#94623f", HAIR="#1e1a1a", HAIR_SH="#0f0c0c", HAIR_HI="#3a3434",
                    TOP="#4a6fa5", TOP_SH="#375584", TOP_SH2="#284068", FOLD="#1c2e4c", STITCH="#a9c2e6", TEE="#f4efe6", TEE_SH="#d9d2c4",
                    LEGS="#2f3b56", LEGS_SH="#222b40", LEGS_SEAM="#4d5b7c", SHOE="#e9e6dd", SHOE_SH="#c4c0b3", SOLE="#2a2c36", SOLE_SH="#1c1d25",
                    STRIPE="#4b505e", NAIL="#e2b394")
PAL["father"] = dict(SKIN="#e8b996", SKIN_SH="#cf9a78", SKIN_SH2="#b78262", HAIR="#d4d2d8", HAIR_SH="#a09ea8", HAIR_HI="#f2f2f6",
                     TOP="#7c8a96", TOP_SH="#5f6c78", TOP_SH2="#48535e", FOLD="#323b44", STITCH="#c6d0d8", TEE="#efe6d6", TEE_SH="#d6cab4",
                     LEGS="#5a4e44", LEGS_SH="#433a32", LEGS_SEAM="#786a5e", SHOE="#4a3324", SHOE_SH="#33231a", SOLE="#2a1f18", SOLE_SH="#1c1510",
                     STRIPE="#a76a3e", NAIL="#eec6aa")
PAL["kid2"] = dict(PAL["kid"], HAIR="#5a3826", HAIR_SH="#3d2418", HAIR_HI="#7a5038",           # волосы как у взрослого Димы
                   TOP="#c0583e", TOP_SH="#9c4430", TOP_SH2="#7a3222", FOLD="#5a2216", STITCH="#eab09c",
                   LEGS="#3d4c6e", LEGS_SH="#2c3854", LEGS_SEAM="#5f6f92")
HEIGHT.update({"teacher_y": .93, "teacher_o": .9, "psych": 1.04, "curly": .95, "youth": 1.02, "father": .98, "kid2": .66})
FACES = FACES + ("teacher_y", "teacher_o", "psych", "curly", "youth", "father", "kid2")
FRIENDLIKE = FRIENDLIKE + ("teacher_y", "teacher_o", "psych", "curly", "youth", "father", "kid2")

# лицо учительницы: мягкий овал, лоб выше (под пучок и родинку)
FACE_T = [(p[0], p[1] * 1.16 if p[1] < -60 else p[1]) for p in FACE_G]
EAR64 = [(-86, -26), (-112, -38), (-132, -14), (-130, 22), (-116, 48), (-94, 52), (-84, 40)]


def _ear64(sd=451):
    return (shape(EAR64, C["SKIN"], blob([(-132, -14), (-130, 22), (-116, 48), (-116, 10)], C["SKIN_SH"], .9), w=4.8, seed=sd)
            + line([(-98, 32), (-118, 20), (-116, -8), (-102, -18)], 3.2, seed=sd + 1))


def _wrinkles64(eyes_=True, mouth_=True, forehead=0, sd=480, op=.8):
    """Морщинки: гусиные лапки у глаз, носогубные, лоб (forehead — сколько складок)."""
    o = ""
    if eyes_:
        for k, dy in enumerate((0, 12, 24)):
            o += line([(122, -22 + dy * .5), (140, -34 + dy)], 2.2, C["SKIN_SH2"], seed=sd + k, op=op)
            o += line([(-6, 0 + dy * .4), (-24, -8 + dy)], 2.0, C["SKIN_SH2"], seed=sd + 4 + k, op=op * .85)
    if mouth_:
        o += line([(30, 60), (22, 86), (26, 104)], 2.2, C["SKIN_SH2"], seed=sd + 8, op=op * .9)
        o += line([(96, 56), (106, 80), (100, 98)], 2.2, C["SKIN_SH2"], seed=sd + 9, op=op * .9)
    for k in range(forehead):
        y = -66 - 14 * k
        o += line([(0, y), (36, y - 6), (74, y - 2)], 1.8, C["SKIN_SH2"], seed=sd + 12 + k, op=op * .7)
    return o


def _glasses64(kind, col, sd=530, w=5.6):
    """kind: round — круглые, rect — прямоугольные тонкие, oval — овальные; дужка уходит к уху."""
    o = ""
    for (cx_, cy_, rx_, ry_, s_) in ((16, -22, 50, 44, sd), (92, -20, 37, 41, sd + 1)):
        if kind == "rect":
            gp = lib.rrect(cx_ - rx_, cy_ - ry_ * .82, cx_ + rx_, cy_ + ry_ * .82, 14)
        elif kind == "oval":
            gp = ellipse_pts(cx_, cy_ + 2, rx_, ry_ * .86, 22)
        else:
            gp = ellipse_pts(cx_, cy_, rx_ * 1.02, ry_ * 1.1, 22)
        o += f'<path d="{ink_closed(gp, w * lib.INK_K[0], seed=s_)}" fill="{col}"/>'
        o += line([(cx_ - rx_ * .6, cy_ - ry_ * .45), (cx_ - rx_ * .25, cy_ - ry_ * .68)], 2.8, "#ffffff", seed=s_ + 4, op=.55)
    o += line([(70, -26), (54, -28)], w * .8, col, seed=sd + 2)
    o += line([(-34, -28), (-86, -24)], w * .72, col, seed=sd + 3)
    return o


def _bun64(sd=600):
    """Пучок на затылке + гладко зачёсанные назад волосы с прядками (общая примета учительницы в обоих возрастах)."""
    s = []
    bun = ellipse_pts(-118, -150, 62, 54, 16, rot=-20)
    bi = blob(ellipse_pts(-130, -132, 50, 38, 12, rot=-20), C["HAIR_SH"], .8)
    for i, a in enumerate((-60, -10, 40, 90)):
        r = math.radians(a)
        bi += line([(-118 + 40 * math.cos(r), -150 + 34 * math.sin(r)), (-118 + 10 * math.cos(r + 1.2), -150 + 8 * math.sin(r + 1.2))], 2.6,
                   C["HAIR_SH"], seed=sd + i, op=.85)
    s.append(shape(bun, C["HAIR"], bi, w=5.0, seed=sd + 5))
    # масса волос: от линии лба гладко назад к пучку, закрывает верх уха
    hair = [(108, -110), (96, -140), (60, -166), (6, -178), (-52, -172), (-102, -146), (-128, -104), (-134, -54), (-122, -18), (-104, -30),
            (-92, -64), (-70, -96), (-30, -116), (20, -120), (66, -118), (98, -104)]
    hi = blob([(-150, -200), (-40, -200), (-60, -120), (-96, -80), (-110, -10), (-150, -10)], C["HAIR_SH"], .85)
    hi += blob([(0, -172), (60, -156), (96, -124), (56, -142), (20, -158)], C["HAIR_HI"], .85)
    for i, st in enumerate([[(84, -118), (30, -150), (-40, -158), (-96, -148)], [(70, -110), (10, -136), (-60, -138), (-104, -120)],
                            [(50, -106), (-10, -122), (-76, -112), (-112, -90)]]):
        hi += line(st, 2.4, C["HAIR_SH"], seed=sd + 10 + i, op=.8)
    s.append(shape(hair, C["HAIR"], hi, w=5.2, seed=sd + 9))
    # выбившаяся прядка у виска
    s.append(line([(104, -96), (116, -64), (110, -34), (118, -10)], 3.0, C["HAIR_SH"], seed=sd + 20, taper=.3, wmin=.4))
    return "".join(s)


def _curls64(sd=640):
    """Пышные кудри участницы: масса за головой до плеч + шапка завитков спереди."""
    back = fur([(-30, -160), (-120, -150), (-176, -90), (-196, 0), (-186, 96), (-150, 150), (-96, 146), (-80, 70), (-70, -20), (-50, -100)],
               depth=26, every=6, seed=sd)
    bi = blob([(-220, -180), (-70, -180), (-80, 60), (-110, 180), (-220, 180)], C["HAIR_SH"], .7)
    for i, (cx_, cy_) in enumerate([(-150, -60), (-170, 20), (-140, 100), (-110, -110), (-120, 40)]):
        bi += line([(cx_ - 12, cy_ + 6), (cx_ - 4, cy_ - 10), (cx_ + 10, cy_ - 6), (cx_ + 6, cy_ + 8)], 2.6, C["HAIR_HI"], seed=sd + 3 + i, op=.7)
    return shape(back, C["HAIR"], bi, w=5.0, seed=sd + 1)


def _curls64_front(sd=660):
    base = [(118, -66), (116, -120), (84, -166), (30, -186), (-34, -184), (-92, -162), (-132, -116), (-146, -56), (-126, -16), (-100, -44),
            (-84, -82), (-40, -100), (0, -96), (44, -104), (86, -90), (108, -60)]
    hair = fur(base, depth=24, every=7, seed=sd)
    hi = blob([(-160, -200), (-40, -200), (-50, -120), (-90, -90), (-110, -20), (-160, -20)], C["HAIR_SH"], .85)
    hi += blob([(0, -176), (60, -156), (96, -116), (60, -138), (30, -156)], C["HAIR_HI"], .9)
    for i, (cx_, cy_) in enumerate([(-80, -146), (-30, -158), (24, -158), (70, -136), (-112, -88), (-50, -118), (10, -124), (60, -108)]):
        hi += line([(cx_ - 12, cy_ + 6), (cx_ - 4, cy_ - 10), (cx_ + 10, cy_ - 6), (cx_ + 6, cy_ + 8)], 2.6, C["HAIR_SH"], seed=sd + 2 + i, op=.85)
    return shape(hair, C["HAIR"], hi, w=5.4, seed=sd + 1)


def head64(expr, style):
    """Головы рилса 64, 3/4 вправо, та же сетка лица и глаз, что у person_head (глаза F_EYE_*, нос, рот _mouth_gen)."""
    hb = expr.get("hair", 0.0)
    s = []
    teacher = style.startswith("teacher")
    old = style in ("teacher_o", "psych", "father")
    if teacher:
        s.append(_ear64())
        s.append(_bun64())
    elif style == "curly":
        s.append(_curls64())
        s.append(_ear64())
    else:
        s.append(_ear64())
    face = {"teacher_y": FACE_T, "teacher_o": FACE_T, "curly": FACE_G, "psych": F_FACE, "youth": F_FACE, "father": FACE_B}[style]
    inner = [blob([(-120, -210), (-40, -210), (-60, -40), (-56, 40), (-30, 160), (-120, 160)], C["SKIN_SH"], .95),
             blob(ellipse_pts(56, -16, 100, 60, 14), "#e5a99a", .3)]
    bl = expr.get("blush", 0.0) + (.35 if style in ("teacher_y", "teacher_o", "curly") else .1)
    inner.append(blob(ellipse_pts(100, 38, 22, 12, 10), "#e98a86", .5 * min(1, bl)))
    inner.append(blob(ellipse_pts(8, 44, 28, 14, 10), "#e98a86", .45 * min(1, bl)))
    if style == "father":     # блик на лысине, тень на висках
        inner.append(blob([(10, -190), (56, -176), (84, -146), (60, -158), (24, -172)], "#f6d8bc", .8))
        inner.append(blob([(-70, -170), (-104, -110), (-100, -60), (-60, -150)], C["SKIN_SH2"], .5))
    if style == "youth":      # лёгкая тень скулы
        inner.append(blob([(-60, 70), (-20, 92), (30, 106), (80, 94), (106, 70), (110, 150), (-60, 150)], C["SKIN_SH2"], .25))
    s.append(shape(face, C["SKIN"], "".join(inner), w=5.6, seed=453 + len(style)))
    if old:
        s.append(_wrinkles64(forehead=2 if style != "teacher_o" else 1, op=.85 if style != "teacher_o" else .75))
    elif teacher:             # у молодой — только смешливые лучики у глаз (те же, что потом станут морщинками)
        s.append(_wrinkles64(mouth_=False, op=.35))
    if style == "psych":      # короткая аккуратная седая борода по линии челюсти и усы
        beard = [(-80, 20), (-66, 64), (-46, 106), (-18, 140), (18, 160), (58, 162), (92, 144), (114, 108), (122, 70), (122, 46), (112, 42),
                 (100, 66), (82, 76), (62, 72), (40, 76), (18, 68), (-10, 56), (-40, 34), (-64, 8)]
        bi = blob([(-90, 40), (60, 120), (130, 120), (130, 180), (-90, 180)], C["HAIR_SH"], .75)
        for i, st in enumerate([[(-44, 70), (-30, 96)], [(-10, 104), (2, 130)], [(30, 122), (36, 148)], [(70, 120), (72, 146)], [(102, 100), (104, 124)]]):
            bi += line(st, 2.2, C["HAIR_SH"], seed=505 + i, op=.85)
        s.append(shape(beard, C["HAIR"], bi, w=4.8, seed=504))
    s.append(_nose())
    if style in ("psych", "father"):
        k = expr.get("smile", .3)
        m = expr.get("mouth", "smile")
        if m in ("grin", "laugh", "talk"):
            o_ = expr.get("open", .5)
            dy = 12 * o_ if m == "laugh" else 6 * o_
            mp = [(18, 84), (42, 92), (74, 92), (104, 80), (98, 104 + dy), (78, 122 + dy), (50, 124 + dy), (28, 108 + dy)]
            mi = blob([(18, 84), (104, 80), (100, 96), (22, 98)], "#f6efe2") + blob([(42, 114 + dy), (64, 106 + dy), (90, 110 + dy), (76, 128 + dy), (50, 128 + dy)], "#c86b6b")
            s.append(shape(mp, "#5a2b33", mi, w=4.4, seed=391))
        elif m == "wobble":
            s.append(line([(28, 94), (44, 100), (60, 92), (76, 100), (98, 92)], 4.4, "#5a2b33", seed=391))
        else:
            s.append(line([(26, 94 - 6 * k), (50, 100 + 3 * k), (78, 100 + 3 * k), (102, 92 - 6 * k)], 4.6, "#4a2a24", seed=391, peak=.5))
        mus = [(4, 82), (22, 66), (52, 60), (64, 68), (76, 60), (104, 62), (122, 78), (104, 84), (80, 78), (64, 84), (46, 78), (22, 86)]
        s.append(shape(mus, C["HAIR"], blob([(8, 82), (120, 80), (102, 88), (24, 90)], C["HAIR_SH"], .8)
                       + line([(30, 72), (24, 84)], 1.8, C["HAIR_SH"], seed=357, op=.8) + line([(96, 70), (104, 82)], 1.8, C["HAIR_SH"], seed=358, op=.8),
                       w=4.0, seed=356))
    else:
        lip = {"teacher_y": "#c25a60", "teacher_o": "#b0585c", "curly": "#b64e58"}.get(style, INK)
        s.append(_mouth_gen(expr, lip, seed=391))
    if expr.get("tear", 0.0) > .02:     # слезинка у ближнего глаза (вытирает пальцем)
        tr = expr["tear"]
        ty = 14 + 26 * expr.get("tear_run", 0.0)
        s.append(shape([(24, ty - 8), (32, ty + 6), (26, ty + 14), (18, ty + 8)], "#bfe6f6", blob([(24, ty), (27, ty + 6), (24, ty + 9)], "#ffffff"),
                       w=2.0 * tr, seed=397))
    s.append(eyes(expr, F_EYE_N, F_EYE_F, bags=old and expr.get("bags", True)))
    if teacher or style == "curly":     # ресницы — короткие, у обеих женщин
        for (cx_, cy_, rx_, sd_) in ((18, -22, 44, 520), (90, -20, 34, 524)):
            if expr.get("laugh", 0) > .5 or expr.get("shut", 0) > .5:
                continue
            s.append(line([(cx_ + rx_ * .6, cy_ - 36), (cx_ + rx_ * 1.0, cy_ - 50)], 3.2, seed=sd_, taper=.3, wmin=.5))
            s.append(line([(cx_ + rx_ * .3, cy_ - 42), (cx_ + rx_ * .6, cy_ - 58)], 2.8, seed=sd_ + 1, taper=.3, wmin=.5))
    if style == "teacher_o":            # очки на цепочке: тонкая оправа, цепочка от дужки вниз к шее
        s.append(_glasses64("oval", C["FRAME"], sd=540, w=4.4))
        ch = [(-86, -24), (-98, 20), (-104, 70), (-96, 120), (-80, 170)]
        s.append(line(ch, 2.2, "#b8954a", seed=545, taper=.1, wmin=.8))
        for i in range(9):
            q = ch[min(4, i // 2)]
            s.append(f'<circle cx="{q[0] - 2 + (i % 2) * 3:.1f}" cy="{q[1] + (i % 2) * 18:.1f}" r="2.2" fill="#d8b866"/>')
    if style == "psych":
        s.append(_glasses64("rect", C["FRAME"], sd=546, w=5.0))
    if style == "curly":
        s.append(_glasses64("round", C["FRAME"], sd=550, w=6.2))
    brow_col = C["HAIR_SH"] if style not in ("psych", "father", "teacher_o") else "#8a8894"
    s.append(_brows(expr, brow_col, {"psych": 1.25, "father": 1.3, "youth": 1.15}.get(style, .9), sd=362, dy=8.0 if teacher else 0.0))
    if teacher:     # родинка над ближней (левой от зрителя) бровью — главная примета в обоих возрастах
        s.append(f'<circle cx="-14" cy="-122" r="5.2" fill="{C["MOLE"]}"/>')
    if style == "curly":
        s.append(_curls64_front())
    elif style == "youth":    # короткая стрижка: плотная шапка волос, виски коротко, лёгкий чубчик
        top = [(112, -84), (108, -128), (80, -160), (30, -176), (-30, -174), (-84, -152), (-118, -110), (-124, -60), (-110, -40), (-96, -70),
               (-70, -100), (-30, -112), (20, -112), (64, -108), (96, -92)]
        hi = blob([(-140, -190), (-30, -190), (-50, -120), (-96, -80), (-120, -40)], C["HAIR_SH"], .8)
        hi += blob([(10, -170), (70, -150), (100, -116), (60, -136)], C["HAIR_HI"], .8)
        for i in range(10):
            x0 = -100 + i * 22
            hi += line([(x0, -150 + abs(i - 5) * 4), (x0 + 6, -128 + abs(i - 5) * 3)], 1.8, C["HAIR_HI"], seed=580 + i, op=.6)
        s.append(shape(top, C["HAIR"], hi, w=5.0, seed=579))
        s.append(blob([(-110, -60), (-92, -70), (-86, -20), (-104, -10)], C["HAIR_SH"], .55))     # коротко подстриженный висок
    elif style == "psych":    # седые волосы: короткие, редеют на макушке, гуще на висках и затылке
        s.append(shape([(-104, -80), (-126, -40), (-128, 4), (-110, 0), (-96, 26), (-86, -10), (-76, -60)], C["HAIR"],
                       line([(-112, -40), (-108, -6)], 1.8, C["HAIR_SH"], seed=591, op=.8), w=4.4, seed=590))
        top = [(108, -92), (100, -136), (64, -168), (10, -180), (-48, -172), (-96, -142), (-120, -96), (-112, -70), (-90, -96), (-50, -120),
               (0, -130), (50, -124), (90, -104)]
        hi = blob([(-140, -190), (-40, -190), (-60, -120), (-100, -90), (-120, -60)], C["HAIR_SH"], .7)
        hi += blob([(-20, -176), (40, -166), (20, -150), (-30, -156)], C["SKIN"], .55)        # редеет на макушке
        for i, st in enumerate([[(60, -150), (20, -160), (-30, -158)], [(80, -120), (30, -134), (-30, -134), (-80, -116)]]):
            hi += line(st, 1.8, C["HAIR_SH"], seed=593 + i, op=.8)
        s.append(shape(top, C["HAIR"], hi, w=4.8, seed=592))
    elif style == "father":   # лысина, седая подкова волос над ухом и на затылке
        s.append(shape([(-60, -150), (-100, -128), (-128, -80), (-134, -30), (-120, 10), (-104, -6), (-100, -40), (-86, -84), (-56, -120)], C["HAIR"],
                       blob([(-140, -120), (-90, -120), (-100, -20), (-140, 0)], C["HAIR_SH"], .7)
                       + line([(-110, -90), (-120, -30)], 1.8, C["HAIR_SH"], seed=597, op=.8), w=4.4, seed=596))
        s.append(shape([(96, -96), (110, -70), (112, -40), (102, -52), (94, -76)], C["HAIR"], "", w=3.4, seed=598))
    return "".join(s)


def knit_cardigan_parts():
    """Вязаный кардиган (учительница, отец): полочки поверх светлой блузы/рубашки, пуговицы, резинка, косички вязки."""
    back, torso, st = jacket_parts(cardigan=True)
    knit = ""
    for k, x0 in enumerate((-80, -40, 0)):
        pts = [(x0, -380), (x0 + 10, -330), (x0 - 4, -280), (x0 + 10, -230), (x0 - 4, -180), (x0 + 10, -130), (x0 - 4, -80)]
        knit += line(pts, 2.6, C["TOP_SH2"], seed=760 + k, op=.65)
        knit += line([(p[0] + 8, p[1]) for p in pts], 1.6, C["STITCH"], seed=770 + k, op=.6)
    rib = blob([(-118, -28), (84, -28), (84, 30), (-118, 30)], C["TOP_SH"], .9)
    rib += "".join(line([(-112 + k * 16, -24), (-112 + k * 16, 26)], 1.4, C["TOP_SH2"], seed=780 + k, op=.8) for k in range(13))
    return back, torso + knit + rib, st


def corduroy_parts():
    """Вельветовый пиджак психолога: рубчик вертикальными штрихами, лацкан, светло-голубая рубашка."""
    back, torso, st = jacket_parts()
    cord = "".join(line([(-110 + k * 14, -400 + abs(k - 8) * 3), (-112 + k * 14, 20)], 1.3, C["TOP_SH2"], seed=790 + k, op=.45) for k in range(14))
    lapel = shape([(36, -428), (70, -380), (58, -330), (80, -250), (52, -260), (34, -340), (22, -410)], C["TOP_SH"],
                  line([(40, -410), (56, -330), (70, -270)], 1.6, C["STITCH"], seed=799, op=.7), w=3.6, seed=798)
    return back, torso + cord + lapel, st


CLOTHES64.update({"teacher_y": knit_cardigan_parts, "teacher_o": knit_cardigan_parts, "father": knit_cardigan_parts, "psych": corduroy_parts,
                  "curly": sweater_parts, "youth": tee_parts, "kid2": sweater_parts})

# ─── мимика рилса 64: у каждого плана своя ───
EXPR["dima"].update({
    "unsure": {"brows": "worry", "mouth": "flat", "lid": .7, "look": (.55, .25)},                                  # неуверенность (s01)
    "awkward": {"brows": "worry", "mouth": "side", "lid": .6, "look": (-.5, .2), "blush": .7},                    # неловкость (s03; + плечи dima(shrug=1))
    "glum": {"brows": "sad", "mouth": "frown", "lid": .42, "look": (.2, .55)},                                     # уныние (s03 конец, s04)
    "thoughtful": {"brows": "calm", "mouth": "flat", "lid": .7, "look": (.45, -.6)},                               # задумчиво (s06)
    "pressed": {"brows": "worry", "mouth": "pressed", "lid": .6, "look": (.3, .3)},                                # сжатые губы (s07)
    "nervous": {"brows": "worry", "mouth": "wobble", "lid": .9, "look": (.4, 0), "bags": False},                  # голос дрожит (s14)
    "steady": {"brows": "calm", "mouth": "talk", "open": .45, "smile": .4, "lid": .8, "look": (.4, 0), "bags": False},   # крепнет (s14)
    "relief64": {"brows": "calm", "mouth": "smile", "smile": .8, "lid": .5, "look": (.2, .3), "bags": False},     # облегчение (s16)
    "warm": {"brows": "calm", "mouth": "smile", "smile": 1.0, "lid": .62, "look": (-.35, 0), "blush": .3, "bags": False},   # тёплая улыбка в камеру
    "write": {"brows": "det", "mouth": "smile", "smile": .35, "lid": .55, "look": (.5, .7), "bags": False},       # пишет письмо (s13)
    "breath": {"brows": "up", "mouth": "o", "open": .3, "lid": .85, "look": (.3, -.1), "bags": False},            # вдох перед звонком (s13)
})
EXPR["kid2"] = {"beam": {"brows": "up", "mouth": "grin", "open": .7, "lid": .9, "look": (.5, -.6)},             # сияет, смотрит на учительницу
                "shy": {"brows": "calm", "mouth": "smile", "smile": .8, "lid": .6, "look": (.4, .4), "blush": .6}}
EXPR["teacher_y"] = {"kind": {"brows": "calm", "mouth": "smile", "smile": .9, "lid": .7, "look": (.4, .5)},     # склонилась к парте
                     "praise": {"brows": "up", "mouth": "grin", "open": .45, "lid": .78, "look": (.4, .45)}}     # хвалит
EXPR["teacher_o"] = {"listen": {"brows": "up", "mouth": "flat", "lid": .9, "look": (.3, 0)},                     # слушает в трубку
                     "moved": {"brows": "sad", "mouth": "wobble", "lid": .7, "look": (.2, .2), "tear": 1.0},   # замерла, глаза влажные
                     "laugh": {"brows": "up", "mouth": "laugh", "open": .9, "laugh": 1.0},                       # смеётся, запрокинув голову
                     "wipe": {"brows": "calm", "mouth": "smile", "smile": 1.0, "laugh": .7, "tear": 1.0, "tear_run": .6}}   # вытирает слезу
EXPR["psych"] = {"calm": {"brows": "calm", "mouth": "smile", "smile": .25, "lid": .75, "look": (-.2, 0)},
                 "smile": {"brows": "up", "mouth": "smile", "smile": 1.0, "lid": .62, "look": (-.4, 0)},
                 "explain": {"brows": "up", "mouth": "talk", "open": .4, "smile": .4, "lid": .8, "look": (-.4, 0)}}
EXPR["curly"] = {"serious": {"brows": "worry", "mouth": "flat", "lid": .7, "look": (.4, .55)},
                 "happy": {"brows": "up", "mouth": "grin", "open": .5, "lid": .7, "look": (.2, 0)},
                 "shy": {"brows": "calm", "mouth": "smile", "smile": .9, "lid": .5, "look": (.3, .45), "blush": .8},
                 "cover": {"brows": "up", "mouth": "grin", "open": .7, "laugh": 1.0}}
EXPR["beard"].update({"serious": {"brows": "frown", "mouth": "flat", "lid": .7, "look": (.4, .55)},
                      "happy": {"brows": "up", "mouth": "grin", "open": .5, "lid": .7},
                      "laugh": {"brows": "up", "mouth": "laugh", "open": 1.0, "laugh": 1.0}})
EXPR["youth"] = {"serious": {"brows": "calm", "mouth": "flat", "lid": .65, "look": (.4, .6)},
                 "happy": {"brows": "up", "mouth": "smile", "smile": 1.0, "lid": .75, "look": (.3, 0)}}
EXPR["father"] = {"serious": {"brows": "frown", "mouth": "flat", "smile": 0, "lid": .55, "look": (.3, .3)},
                  "look_up": {"brows": "up", "mouth": "flat", "smile": .2, "lid": .95, "look": (.3, -.4)},
                  "moved": {"brows": "sad", "mouth": "wobble", "lid": .7, "look": (.3, -.2)},
                  "happy": {"brows": "calm", "mouth": "smile", "smile": 1.0, "lid": .6}}

# ─── позы рилса 64: цели рук в долях масштаба от таза (как POSE) ───
POSE.update({
    # держит открытку двумя руками перед грудью (за столом)
    "card": (0.1, 0.12, {"f": ("ik", (215, -255), -1), "n": ("ik", (300, -250), -1)},
             {"f": {"curl": (.55, .55, .6, .6), "thumb": .5, "dir": (.6, -.8)}, "n": {"curl": (.55, .55, .6, .6), "thumb": .5, "dir": (.2, -1)}}),
    # ручка над открыткой: ближняя кисть вперёд-вниз (ручку в пальцы кладёт вызывающий), дальняя прижимает открытку
    "pen": (0.16, 0.14, {"f": ("ik", (200, -200), -1), "n": ("ik", (300, -235), -1)},
            {"f": {"curl": (.3, .3, .35, .4), "thumb": .3}, "n": {"curl": (.6, .55, .6, .65), "thumb": .7, "dir": (.5, .8)}}),
    # чешет затылок: ближняя рука вверх за голову, локоть в сторону
    "scratch": (0.02, 0.1, {"f": ("ik", (180, -200), -1), "n": ("ik", (-105, -520), 1)},
                {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (.45, -1), "curl": (.55, .6, .65, .65), "thumb": .4}}),
    # откинулся, руки за головой (рисовать с layers=LAYERS_BEHIND — кисти за головой)
    "behind": (-0.18, -0.12, {"f": ("ik", (-30, -650), 1), "n": ("ik", (-10, -660), 1)},
               {"f": {"kind": "none"}, "n": {"kind": "none"}}),
    # ладонь на груди (по грудь, крупно)
    "chest": (0.02, 0.0, {"f": ("ang", 0.18, 0.18), "n": ("ik", (70, -300), -1)},
              {"n": {"dir": (-.25, -1), "curl": (.1, .1, .15, .2), "spread": .12, "thumb": .15}}),
    # пишет: ближняя кисть с ручкой у листа, дальняя прижимает лист
    "write": (0.22, 0.2, {"f": ("ik", (205, -205), -1), "n": ("ik", (290, -215), -1)},
              {"f": {"curl": (.2, .2, .25, .3), "thumb": .2}, "n": {"curl": (.45, .5, .55, .6), "thumb": .5, "dir": (.8, .6)}}),
    # складывает лист: обе кисти сходятся перед собой
    "fold": (0.12, 0.16, {"f": ("ik", (220, -235), -1), "n": ("ik", (290, -260), -1)},
             {"f": {"curl": (.5, .5, .55, .6), "thumb": .5, "dir": (.8, -.5)}, "n": {"curl": (.5, .5, .55, .6), "thumb": .5, "dir": (-.3, -1)}}),
    # мобильник у уха (ближняя рука), дальняя опущена; мобильник рисует dima_mobile()
    "mobile": (0.02, 0.06, {"f": ("ang", 0.18, 0.2), "n": ("ik", (-75, -430), 1)},
               {"n": {"dir": (.15, -1), "curl": (.6, .65, .7, .7), "thumb": .7}}),
    # мобильник у уха + письмо в дальней руке перед собой (у окна)
    "mobile_letter": (0.02, 0.06, {"f": ("ik", (200, -230), -1), "n": ("ik", (-75, -430), 1)},
                      {"f": {"curl": (.55, .55, .6, .6), "thumb": .55, "dir": (.4, -1)}, "n": {"dir": (.15, -1), "curl": (.6, .65, .7, .7), "thumb": .7}}),
    # гладит кота на коленях: ближняя ладонь на спине кота (u двигает её вдоль), дальняя на подлокотнике
    "pet": (0.0, 0.18, {"f": ("ik", (160, -150), -1), "n": ("ik", (250, -130), -1)},
            {"f": {"curl": (.3, .3, .35, .4), "thumb": .3}, "n": {"dir": (1, .25), "curl": (.15, .15, .2, .25), "spread": .15, "thumb": .2}}),
    # держит письмо перед грудью двумя руками и улыбается в камеру
    "letter": (0.0, -0.05, {"f": ("ik", (190, -300), -1), "n": ("ik", (275, -300), -1)},
               {"f": {"curl": (.55, .55, .6, .6), "thumb": .55, "dir": (.5, -1)}, "n": {"curl": (.55, .55, .6, .6), "thumb": .55, "dir": (.1, -1)}}),
    # убирает открытку в ящик: ближняя рука вниз-вперёд
    "drawer": (0.26, 0.3, {"f": ("ik", (180, -200), -1), "n": ("ik", (330, -60), -1)},
               {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.5, .5, .55, .6), "thumb": .55, "dir": (.6, .8)}}),
    # учительница: склоняется к парте, ближняя ладонь на плечо ученика (цель — вызывающий подставит плечо через arms)
    "lean_desk": (0.42, 0.3, {"f": ("ik", (200, -260), -1), "n": ("ik", (340, -230), -1)},
                  {"f": {"curl": (.5, .5, .55, .6), "thumb": .5, "dir": (.5, -1)}, "n": {"dir": (.6, .8), "curl": (.15, .2, .25, .3), "spread": .15, "thumb": .2}}),
    # ладонь к губам (учительница замерла / участница прикрывает рот)
    "hand_mouth": (0.04, 0.0, {"f": ("ang", 0.2, 0.25), "n": ("ik", (112, -405), -1)},
                   {"n": {"dir": (.1, -1), "curl": (.15, .15, .2, .25), "spread": .1, "thumb": .2}}),
    # вытирает слезу пальцем у ближнего глаза
    "wipe": (-0.06, -0.12, {"f": ("ang", 0.2, 0.25), "n": ("ik", (100, -455), -1)},
             {"n": {"dir": (.2, -1), "curl": (0, .8, .85, .85), "spread": .05, "thumb": .7}}),
    # ладонь на сердце (отец)
    "heart": (0.0, -0.05, {"f": ("ang", 0.2, 0.2), "n": ("ik", (40, -320), -1)},
              {"n": {"dir": (-.3, -1), "curl": (.15, .15, .2, .25), "spread": .12, "thumb": .2}}),
    # протягивает лист к краю кадра (психолог)
    "offer": (0.06, 0.0, {"f": ("ang", 0.2, 0.25), "n": ("ik", (430, -320), -1)},
              {"n": {"dir": (1, -.1), "curl": (.5, .5, .55, .6), "thumb": .55}}),
    # поправляет очки указательным пальцем (психолог)
    "glasses": (0.0, 0.0, {"f": ("ang", 0.2, 0.25), "n": ("ik", (112, -450), -1)},
                {"n": {"dir": (.3, -1), "curl": (0, .85, .9, .9), "spread": .05, "thumb": .7}}),
})
LAYERS_BEHIND = ("legs", "pelvis", "arm_f", "arm_n", "body")     # руки за головой — рисуются под телом и головой

SHRUG = 46.0      # на сколько голова уходит в плечи на «неловко» (L-единицы)


def person(who, x, y, scale, expr="", pose=None, u_pose=None, shrug=0.0, flip=False, feet=None, lotus=None, layers=None, lean_add=0.0,
           head_add=0.0, arms=None, hands=None, **kw):
    """Любой герой рилса 64 одной строкой: expr — имя из EXPR[who] или dict; pose — имя из POSE (u_pose=(other, u) — переход к другой позе);
    shrug 0..1 — плечи к ушам (голова опускается в плечи); lean_add/head_add — живой наклон поверх позы; arms/hands — точечная замена."""
    ex = EXPR.get(who, {}).get(expr, {}) if isinstance(expr, str) else dict(expr or {})
    if pose and u_pose:
        pk = mix_pose(pose, u_pose[0], u_pose[1], x, y, scale, who)
    elif pose:
        pk = pose_kw(pose, x, y, scale, who)
    else:
        pk = dict(lean=0.0, head_ang=0.0, arms=None, hands=None)
    if arms:
        A = dict(pk["arms"] or {"f": ("ang", 0.18, 0.18), "n": ("ang", -0.1, 0.25)})
        A.update(arms)
        pk["arms"] = A
    if hands:
        H = dict(pk.get("hands") or {})
        H.update(hands)
        pk["hands"] = H
    if layers is None and pose == "behind":
        layers = LAYERS_BEHIND
    return figure(who, x, y, scale, ex, lean=pk["lean"] + lean_add, head_ang=pk["head_ang"] + head_add, arms=pk["arms"], hands=pk["hands"],
                  feet=feet, flip=flip, layers=layers, head_off=(0, SHRUG * shrug), lotus=lotus, **kw)


def dima(x, y, scale, expr="unsure", pose=None, **kw):
    """Взрослый Дима (горчичное худи, лохматый, щетина). Вечером s01–s04 мимика с мешками (по умолчанию), днём — bags=False в EXPR."""
    return person("dima", x, y, scale, expr, pose, **kw)


def kid_dima(x, y, scale, expr="beam", pose=None, **kw):
    """Маленький Дима лет 9: тот же вихор и разрез глаз, без щетины, кирпичный свитер."""
    return person("kid2", x, y, scale, expr, pose, **kw)


def teacher(age="young", x=540, y=1200, scale=.5, expr=None, pose=None, **kw):
    """Учительница — одна женщина: age="young" (s02, каштановый пучок, зелёная кофта) | "old" (s15, седой пучок, очки на цепочке,
    вязаный кардиган). Общие приметы — родинка над левой от зрителя бровью, пучок, овал, глаза и улыбка."""
    who = "teacher_y" if age == "young" else "teacher_o"
    return person(who, x, y, scale, expr if expr is not None else ("kind" if age == "young" else "listen"), pose, **kw)


def psychologist(x, y, scale, expr="calm", pose=None, **kw):
    return person("psych", x, y, scale, expr, pose, **kw)


def participant(name, x, y, scale, expr="serious", pose=None, **kw):
    """name: "curly" (женщина с кудрями в очках), "beard" (бородач в клетчатой), "youth" (юноша с короткой стрижкой)."""
    return person(name, x, y, scale, expr, pose, **kw)


def old_father(x, y, scale, expr="serious", pose=None, **kw):
    return person("father", x, y, scale, expr, pose, **kw)


def mobile_at_ear(fig, scale, flip=False):
    """Мобильник-силуэт в ближней руке у уха (поза "mobile"/"mobile_letter"): рисовать МЕЖДУ телом и ближней рукой —
    figure(..., layers=("legs","pelvis","arm_f","body")) + mobile_at_ear(...) + figure(..., layers=("arm_n",))."""
    w = fig["wrist"]["n"]
    sc = fig["scale"]
    sx = -1 if flip else 1
    return mobilnik(w[0] + sx * 12 * sc, w[1] - 70 * sc, k=sc * 1.25, rot=-14 * sx)


def dima_mobile(x, y, scale, expr="nervous", pose="mobile", **kw):
    """Дима с мобильником у уха: тело, мобильник, затем ближняя рука поверх (пальцы обхватывают корпус)."""
    base = dima(x, y, scale, expr, pose, layers=kw.pop("layers_body", ("legs", "pelvis", "arm_f", "body")), **kw)
    hand_ = dima(x, y, scale, expr, pose, layers=("arm_n",), **kw)
    base["svg"] = base["svg"] + mobile_at_ear(base, scale, kw.get("flip", False)) + hand_["svg"]
    return base


# ─── кот рилса 64 ───
def cat_curl(x, y, k, st=None, t=0.0):
    """Кот клубком (на коленях): см. cat.curl — st: eye (0 закрыт … 1 открыт ближний глаз), squint (жмурится), breath (сила дыхания),
    flame_e, tail. (x, y) — середина низа клубка."""
    import cat
    return cat.curl(x, y, k, st or {}, t)


def ik_ang(who, x, y, scale, lean, target, side=-1, near=True, torso_k=1.0):
    """Цель руки в мире → ("ang", th1, bend) — та же поза, что ("ik", target, side), но углами плеча и локтя. Нужна, чтобы рука
    ПЛАВНО переходила между позами с разным сгибом (side −1 ↔ +1: со стола к уху) — mix_ang() ведёт локоть по дуге, а не перескоком."""
    sc = scale * HEIGHT.get(who, 1.0)
    H = np.array((x, y), float)
    up = rot(np.array([0.0, -1.0]), lean)
    fw = rot(np.array([1.0, 0.0]), lean)
    S = up * TORSO * torso_k + fw * 6
    sp = S + (fw * 4 if near else fw * -14 + up * 6)
    E, Wr = ik2(sp, (np.array(target, float) - H) / sc, UPPER, FORE, side)
    d1 = (E - sp) / UPPER
    d2 = (Wr - E) / np.linalg.norm(Wr - E)
    th1 = math.atan2(d1[0], d1[1]) - lean * .3
    bend = -math.atan2(d1[0] * d2[1] - d1[1] * d2[0], float(d1 @ d2))
    return ("ang", th1, bend)


def mix_ang(a, b, u):
    """Плавный переход между двумя ("ang", th1, bend): плечо — кратчайшей дугой, локоть — линейно (через прямую руку)."""
    u = max(0.0, min(1.0, u))
    d = (b[1] - a[1] + math.pi) % (2 * math.pi) - math.pi
    return ("ang", a[1] + d * u, a[2] + (b[2] - a[2]) * u)


# ═════════════════════════════ РИЛС 70 «ПОМИДОРКА» (автор — группа B): позы, мимика, Дима со спины ═════════════════════════════
# Мимика: ночью s01–s08 с мешками (по умолчанию), утром s13–s18 — имена с «_day» или bags=False.
#   hope (надежда), resolve (решимость), numb (оцепенение, взгляд в стену), peer (всматривается), frowny (хмурится), sink (уныние,
#   глаза вниз), surprise_day, laugh_day, relief_day, focus_smile (сосредоточенная улыбка), sly (хитрый прищур), smile_cam (улыбка в камеру).
# Позы (POSE, по пояс; цели рук — в долях масштаба от таза, Дима смотрит вправо):
#   hold_front — держит/заводит предмет перед грудью двумя руками (центр предмета ≈ (265, −330)·sc); hover — руки зависли над клавишами
#   (≈ (290, −215)·sc); recoil — отдёрнул руки к груди; type — печатает (кисти на (300, −200)·sc, пальцы вниз; дрожь — сцена);
#   cheek — ближние пальцы трогают щёку; head_arms — голова на скрещённых руках на столе (lean большой, лицо вниз; рисовать с
#   layers=LAYERS_ARMS_UNDER — руки под головой, иначе ближняя рука закрывает лицо);
#   swing — обе руки держат верёвку качелей (цель руки задаёт сцена через arms=, см. swing_arms); door — ближняя ладонь на ручке
#   двери (≈ (300, −40)·sc при стойке); mug — несёт кружку перед собой (≈ (250, −250)·sc); push — не глядя отодвигает предмет ладонью
#   вправо-вниз (≈ (420, −190)·sc); pet — гладит (из 64).
#   swing_kw(x, y, scale, kick) → feet для сидения на качелях: ноги вперёд (kick 0…1 — выпрямлены, волнообразно задаёт сцена).
#   sit_kw(x, y, scale) → feet для сидения на стуле (колени вперёд, голени вниз).
#   swing_arms(x, y, scale, rope_top, rope_bot, lean) → arms= для обеих рук на верёвке (кисти на верёвке на высоте плеч и чуть выше).
#   dima_back(x, y, scale, tilt, look_up, shrug, hair, t) — Дима СО СПИНЫ: голова и плечи в горчичном худи (капюшон сзади).
#                         (x, y) — основание шеи (между плеч), голова ≈ 300·scale; tilt — наклон головы набок (градусы),
#                         look_up 0…1 — запрокидывает голову (затылок уходит к капюшону, видны уши ниже и шея короче);
#                         shrug 0…1 — плечи к ушам. Возвращает dict(svg, head=(x, y) центр затылка, shoulders=(левое, правое)).
EXPR["dima"].update({
    "hope": {"brows": "up", "mouth": "smile", "smile": .5, "lid": .92, "look": (.45, .2)},                     # надежда
    "resolve": {"brows": "det", "mouth": "pressed", "lid": .8, "look": (.55, .15)},                             # решимость
    "numb": {"brows": "calm", "mouth": "flat", "lid": .42, "look": (.05, 0)},                                  # оцепенение
    "peer": {"brows": "one_up", "mouth": "flat", "lid": .78, "look": (.8, .05)},                               # всматривается
    "frowny": {"brows": "pinch", "mouth": "frown", "lid": .55, "look": (.7, .1)},                              # хмурится
    "sink": {"brows": "sad", "mouth": "frown", "lid": .3, "look": (.3, .7)},                                   # уныние, глаза вниз
    "surprise_day": {"brows": "up", "mouth": "o", "open": .35, "lid": 1.0, "look": (.3, -.1), "bags": False},
    "laugh_day": {"brows": "up", "mouth": "laugh", "open": .9, "laugh": 1.0, "hair": 6, "bags": False},
    "relief_day": {"brows": "calm", "mouth": "smile", "smile": .8, "lid": .45, "look": (.3, .3), "bags": False},
    "focus_smile": {"brows": "det", "mouth": "smile", "smile": .4, "lid": .58, "look": (.6, .55), "bags": False},
    "sly": {"brows": "one_up", "mouth": "side", "lid": .32, "look": (.5, 0), "bags": False},
    "smile_cam": {"brows": "calm", "mouth": "smile", "smile": 1.0, "lid": .7, "look": (-.35, 0), "bags": False},
})

POSE.update({
    "hold_front": (0.06, 0.1, {"f": ("ik", (205, -330), -1), "n": ("ik", (325, -335), -1)},
                   {"f": {"dir": (.9, -.3), "curl": (.55, .55, .6, .62), "thumb": .5}, "n": {"dir": (-.6, -.7), "curl": (.6, .6, .65, .68), "thumb": .6}}),
    "hover": (0.12, 0.12, {"f": ("ik", (235, -222), -1), "n": ("ik", (330, -228), -1)},
              {"f": {"dir": (1, .35), "curl": (.18, .22, .25, .3), "spread": .25, "thumb": .2}, "n": {"dir": (1, .4), "curl": (.15, .2, .22, .28), "spread": .25, "thumb": .2}}),
    "recoil": (-0.06, -0.06, {"f": ("ik", (110, -300), -1), "n": ("ik", (150, -315), -1)},
               {"f": {"dir": (.3, -1), "curl": (.7, .7, .75, .75), "thumb": .6}, "n": {"dir": (.2, -1), "curl": (.7, .72, .75, .78), "thumb": .6}}),
    "type": (0.14, 0.18, {"f": ("ik", (250, -205), -1), "n": ("ik", (335, -210), -1)},
             {"f": {"dir": (1, .55), "curl": (.3, .35, .4, .45), "spread": .2, "thumb": .3}, "n": {"dir": (1, .6), "curl": (.3, .3, .35, .4), "spread": .2, "thumb": .3}}),
    "cheek": (0.04, 0.06, {"f": ("ik", (220, -210), -1), "n": ("ik", (185, -455), -1)},
              {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (-.1, -1), "curl": (0, .55, .7, .75), "spread": .05, "thumb": .5}}),
    "head_arms": (0.66, 0.95, {"f": ("ik", (300, -222), -1), "n": ("ik", (225, -228), -1)},
                  {"f": {"dir": (-1, .1), "curl": (.5, .5, .55, .6), "thumb": .4}, "n": {"dir": (1, -.05), "curl": (.45, .45, .5, .55), "thumb": .4}}),
    "swing": (-0.08, -0.06, {"f": ("ik", (60, -330), -1), "n": ("ik", (80, -370), -1)},
              {"f": {"dir": (.15, -1), "curl": (.75, .75, .8, .8), "thumb": .7}, "n": {"dir": (.15, -1), "curl": (.75, .78, .8, .8), "thumb": .7}}),
    "door": (0.02, 0.05, {"f": ("ang", 0.16, 0.2), "n": ("ik", (300, -40), -1)},
             {"n": {"dir": (1, .1), "curl": (.65, .7, .72, .75), "thumb": .6}}),
    "mug": (0.0, 0.05, {"f": ("ang", 0.18, 0.22), "n": ("ik", (250, -250), -1)},
            {"n": {"dir": (.4, -1), "curl": (.6, .6, .65, .7), "thumb": .6}}),
    "push": (0.1, 0.12, {"f": ("ik", (250, -205), -1), "n": ("ik", (430, -190), -1)},
             {"f": {"dir": (1, .55), "curl": (.3, .35, .4, .45), "spread": .2, "thumb": .3}, "n": {"dir": (1, .15), "spread": .3, "curl": (0, .03, .06, .1), "thumb": .1}}),
})


LAYERS_ARMS_UNDER = ("legs", "pelvis", "arm_f", "arm_n", "body")


def sit_kw(x, y, scale, who="dima"):
    sc = scale * HEIGHT.get(who, 1.0)
    return {"feet": {"n": ((x + 300 * sc, y + 300 * sc), 0.0), "f": ((x + 250 * sc, y + 306 * sc), 0.0)}}


def swing_kw(x, y, scale, kick=0.5, who="dima"):
    """Ноги на качелях: колени вперёд, голени вперёд-вниз (kick 0) … почти прямо вперёд (kick 1)."""
    sc = scale * HEIGHT.get(who, 1.0)
    k = lib.clamp(kick)
    out = {}
    for side, d in (("n", 0.0), ("f", -40.0)):
        a = math.radians(70 - 58 * k)        # угол голени от горизонтали вниз
        kx, ky = 290.0, 10.0
        ax, ay = kx + 290 * math.cos(a) + d, ky + 290 * math.sin(a)
        out[side] = ((x + ax * sc, y + ay * sc), -.6 * k)
    return {"feet": out}


def swing_arms(x, y, scale, rope_top, rope_bot, lean=0.0, who="dima"):
    """Руки держат верёвку: кисти на верёвке на уровне груди (ближняя чуть выше), лицо открыто. Верёвку выше кистей рисовать ДО
    тела (за головой), ниже кистей — после тела."""
    sc = scale * HEIGHT.get(who, 1.0)
    t_, b_ = np.array(rope_top, float), np.array(rope_bot, float)
    sh_y = y - TORSO * sc

    def on_rope(yy):
        u = lib.clamp((yy - t_[1]) / (b_[1] - t_[1] + 1e-6))
        return tuple(t_ + (b_ - t_) * u)
    return {"f": ("ik", on_rope(sh_y + 215 * sc), -1), "n": ("ik", on_rope(sh_y + 175 * sc), -1)}


def dima_back(x, y, scale, tilt=0.0, look_up=0.0, shrug=0.0, hair=0.0, t=0.0, who="dima"):
    global C
    C = PAL[who]
    s = scale
    o = []
    lu = lib.clamp(look_up)
    sh = SHRUG * .9 * lib.clamp(shrug)
    # спина и плечи худи (L-единицы: (0, 0) — основание шеи)
    back = [(-300, 600, 1), (-306, 300), (-292, 150 - sh * .6), (-250, 66 - sh), (-150, 20 - sh), (0, 6), (150, 20 - sh), (250, 66 - sh),
            (292, 150 - sh * .6), (306, 300), (300, 600, 1)]
    inner = blob([(80, 0), (340, 120), (340, 560), (120, 560), (150, 300)], C["TOP_SH"], .85)
    inner += line([(-40, 200), (-20, 400), (-34, 560)], 3.0, C["FOLD"], seed=7001, op=.7)
    inner += line([(-230, 160), (-200, 300)], 2.6, C["FOLD"], seed=7002, op=.6)
    inner += line([(230, 170), (205, 320)], 2.6, C["FOLD"], seed=7003, op=.6)
    inner += line([(-250, 110), (-290, 220)], 2.8, C["FOLD"], seed=7004, op=.7)      # шов рукава
    inner += line([(250, 110), (290, 220)], 2.8, C["FOLD"], seed=7005, op=.7)
    o.append(shape(back, C["TOP"], inner, w=5.6, seed=7000))
    # капюшон, лежащий на спине
    hood = [(-150, 10 - sh * .5), (-170, 90), (-130, 190), (-40, 240), (40, 240), (130, 190), (170, 90), (150, 10 - sh * .5), (60, 40), (-60, 40)]
    h_in = blob([(20, 40), (170, 80), (130, 200), (30, 240)], C["TOP_SH2"], .8)
    h_in += line([(-110, 70), (-60, 160), (0, 190), (60, 160), (110, 70)], 3.0, C["FOLD"], seed=7011, op=.85)
    o.append(shape(hood, C["TOP_SH"], h_in, w=5.0, seed=7010))
    # шея
    nk = [(-62, 40), (-58, -70), (58, -70), (62, 40), (0, 56)]
    o.append(shape(nk, C["SKIN"], blob([(10, -80), (70, -80), (70, 50), (20, 50)], C["SKIN_SH"], .9), w=4.4, seed=7020))
    # голова: затылок волосами, уши по бокам
    hy = -205 + 70 * lu + sh
    ear_dy = -24 * lu
    hd = []
    for side in (-1, 1):
        ear = [(side * 104, -20), (side * 132, -34), (side * 146, -2), (side * 138, 36), (side * 116, 52), (side * 100, 40)]
        ear = [(p[0], p[1] + ear_dy) for p in ear]
        hd.append(shape(ear, C["SKIN"], blob([(side * 146, -2), (side * 138, 36), (side * 120, 30)], C["SKIN_SH"], .9), w=4.6, seed=7030 + side))
        hd.append(line([(side * 112, 30 + ear_dy), (side * 132, 18 + ear_dy), (side * 128, -12 + ear_dy)], 3.0, seed=7034 + side))
    skull = ellipse_pts(0, -10, 124, 150, 30)
    hd.append(shape(skull, C["SKIN"], "", w=5.0, seed=7040))
    hb = hair
    hp = []
    rs = np.random.RandomState(70)
    n = 14
    for i in range(n + 1):        # лохматый контур волос: от левого виска через макушку к правому, низ — неровная линия у шеи
        a = math.pi * (1.05 + 0.9 * i / n) + rs.uniform(-.04, .04)
        r = 1.0 + (rs.uniform(.05, .11) if i % 2 else .0) + rs.uniform(-.015, .02)
        hp.append((132 * r * math.cos(a), -18 + 160 * r * math.sin(a) + (hb * math.sin(i * 1.7 + t * 14) * 4 if hb else 0)) + ((1,) if i % 2 else ()))
    bottom_y = 96 - 40 * lu
    hp += [(134, 20), (126, 60), (104, bottom_y - 4, 1), (80, bottom_y + 12), (50, bottom_y, 1), (20, bottom_y + 14), (-14, bottom_y, 1),
           (-46, bottom_y + 12), (-80, bottom_y, 1), (-110, bottom_y - 8), (-128, 56), (-134, 20)]
    h_in = blob([(10, -190), (150, -120), (150, 100), (40, 100), (70, -40)], C["HAIR_SH"], .9)
    h_in += blob(ellipse_pts(-40, -120, 46, 24, 12, rot=-.4), C["HAIR_HI"], .7)
    for j in range(10):
        a = math.radians(-160 + j * 15)
        p0 = (40 * math.cos(a) - 10, -70 + 50 * math.sin(a))
        p1 = (120 * math.cos(a + .25) - 10, -40 + 140 * math.sin(a + .1))
        h_in += line([p0, ((p0[0] + p1[0]) / 2 + 8, (p0[1] + p1[1]) / 2), p1], 3.0, "#2a170f", seed=7060 + j, op=.8)
    h_in += f'<circle cx="-6" cy="-92" r="7" fill="{C["HAIR_SH"]}"/>'      # макушка-вихор
    hd.append(shape(hp, C["HAIR"], h_in, w=5.2, seed=7050))
    head_svg = f'<g transform="translate(0 {hy:.2f}) rotate({tilt:.3f} 0 120)">{"".join(hd)}</g>'
    body = "".join(o[:2])
    svg = (f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})">' + body + o[2] + head_svg + "</g>")
    return dict(svg=svg, head=(x, y + (hy - 10) * s), shoulders=((x - 300 * s, y + 80 * s), (x + 300 * s, y + 80 * s)))


# ═════════════════════════════ РИЛС 71 «ДВА ЛАГЕРЯ» (автор — группа B) ═════════════════════════════
# Дима — горчичное худи (who="dima"), друг — who="friend" (рыжий, джинсовая куртка), один и тот же во всех группах.
# Позы — POSE (как всегда: person(who, x, y, scale, expr, pose, ...), друг смотрит влево — flip=True). Мимика — EXPR.
#   Дима: "ask_palms" разводит ладонями (вопрос), "mime_wall" / "mime_wall_hi" / "mime_wall_lo" ладони плашмя в невидимую стену
#         (пальцы вверх, локти согнуты; ведёт по стене — u_pose между ними), "nose_wall" нос в стену, руки у груди,
#         "chin_fist" подбородок на кулаке (сидит на полу), "pinch" щепоть на уровне плеча, "sneak" крадётся пригнувшись
#         (ноги — tiptoe_kw), "lid_finger" открывает крышку ноутбука одним пальцем, "sock_pull" натягивает носок (сидя на краю
#         кровати; ноги — sock_feet_kw), "jug_pour" наклоняет графин (ближняя рука за ручку, дальняя держит стакан),
#         "glass_drink" стакан у губ, "type" печатает, "point_a" / "point_b" показывает на левый / правый флажок,
#         "hooray" руки вверх (выпрыгнул из кокона).
#   Друг: "shrug" пожимает плечами (+ shrug=1), "temple" стучит пальцем по виску, "mug_hold" кружка у груди, "mug_drink" кружка
#         у губ, "hooray" (тост из кровати), "rest".
#   Ладони и кружка: хват кружки — handle_grip (рилс 63) или grip_svg; графин — props.jug.
#   tiptoe_kw(x, y, scale, phase) — ноги на цыпочках, шаг крадучись; sock_feet_kw(x, y, scale, lift) — сидит на краю кровати,
#         ближняя ступня поднята к рукам (lift 0…1).
#   dima_cocoon(x, y, k, roll, squash, wriggle, sag, expr, hood, t, head_rot, feet, seed, col)
#         Дима в одеяле-коконе, РУК НЕТ. hood=False — лежит на боку: (x, y) — центр низа кокона, длина ~900·k, лицо слева
#         (head_rot — наклон головы, по умолчанию −70°: макушка влево-вверх), ступни справа (feet 0…1 — высунулись, шевелятся по t);
#         roll — угол прокатки (градусы: складки-спираль бегут, кокон чуть переваливается), squash — сплющивание (удар о подушку),
#         wriggle 0…1 — гусеница (волна вдоль тела по t). hood=True — сидит, одеяло капюшоном: (x, y) — центр дна, высота ~980·k;
#         sag 0…1 — одеяло сползает (0 — капюшон до бровей, .5 — с головы на плечи, 1 — до пояса, видно худи);
#         cover 0…1 (через expr["cover"]) — край капюшона съезжает на глаза. Возвращает dict(svg, head=(x, y) центр лица в мире).
#   cocoon_blanket(x, y, k, u, t, seed, col)  одеяло, распахнутое и взлетающее (u 0…1: раскрылось → улетает вверх, вращаясь)
C_COCOON = ("#C8553D", "#9A3B2B", "#E27A5C", "#F0C987")      # то же стёганое одеяло, что props.blanket("quilt")

EXPR["dima"].update({
    "plea": {"brows": "worry", "mouth": "o", "open": .35, "lid": .95, "look": (.4, -.35), "bags": False},       # недоумённая мольба
    "saucer": {"brows": "up", "mouth": "o", "open": .55, "lid": 1.0, "look": (.5, 0), "scale_n": 1.25, "scale_f": 1.2, "bags": False},  # глаза-блюдца
    "puzzled": {"brows": "worry", "mouth": "side", "lid": .8, "look": (.55, -.1), "bags": False},              # непонимание, брови домиком
    "relief71": {"brows": "calm", "mouth": "smile", "smile": .8, "lid": .45, "look": (.1, .2), "bags": False},  # облегчение
    "gape": {"brows": "up", "mouth": "o", "open": 1.0, "lid": 1.0, "look": (-.6, 0), "bags": False},            # открытый рот
    "sly": {"brows": "one_up", "mouth": "side", "smile": .6, "lid": .38, "look": (.6, .1), "bags": False},     # хитрый прищур
    "silent_laugh": {"brows": "up", "mouth": "laugh", "open": .8, "laugh": 1.0, "bags": False},                 # беззвучный смех
    "focus_smile": {"brows": "calm", "mouth": "smile", "smile": .5, "lid": .55, "look": (.6, .45), "bags": False},   # сосредоточенная улыбка
    "sleepy": {"brows": "tired", "mouth": "flat", "lid": .3, "look": (.3, .1)},                                 # сонный в коконе
    "squish": {"brows": "pinch", "mouth": "wince", "lid": .4, "closed": .6, "bags": False},                    # нос сплющен о стену
    "bliss": {"brows": "calm", "mouth": "smile", "smile": .7, "closed": 1.0, "bags": False},                   # глоток, глаза закрыты
})
EXPR["friend"] = {
    "sleep": {"brows": "calm", "mouth": "smile", "smile": .3, "closed": 1.0},
    "beam": {"brows": "up", "mouth": "grin", "open": .7, "lid": 1.0, "look": (.4, -.2)},
    "simple": {"brows": "up", "mouth": "smile", "smile": 1.0, "lid": .75, "look": (.4, 0)},
    "shrug": {"brows": "up", "mouth": "smile", "smile": .7, "lid": .7, "look": (.3, 0)},
    "chill": {"brows": "calm", "mouth": "smile", "smile": .6, "lid": .6, "look": (.2, .2)},
    "sip": {"brows": "calm", "mouth": "flat", "lid": .45, "look": (.3, .3)},
}

POSE.update({
    "ask_palms": (0.18, 0.06, {"f": ("ik", (230, -255), -1), "n": ("ik", (340, -245), -1)},
                  {"f": {"dir": (.5, -1), "spread": .4, "curl": (0, .05, .1, .15), "thumb": .05},
                   "n": {"dir": (.7, -1), "spread": .45, "curl": (0, .05, .1, .15), "thumb": .05}}),
    "mime_wall": (0.06, 0.0, {"f": ("ik", (330, -400), -1), "n": ("ik", (360, -380), -1)},
                  {"f": {"dir": (0, -1), "spread": .28, "curl": (0, 0, .03, .05), "thumb": .0},
                   "n": {"dir": (0, -1), "spread": .3, "curl": (0, 0, .03, .05), "thumb": .0}}),
    "mime_wall_hi": (0.04, -0.12, {"f": ("ik", (320, -520), -1), "n": ("ik", (350, -480), -1)},
                     {"f": {"dir": (0, -1), "spread": .28, "curl": (0, 0, .03, .05), "thumb": .0},
                      "n": {"dir": (0, -1), "spread": .3, "curl": (0, 0, .03, .05), "thumb": .0}}),
    "mime_wall_lo": (0.1, 0.1, {"f": ("ik", (330, -300), -1), "n": ("ik", (355, -280), -1)},
                     {"f": {"dir": (0, -1), "spread": .28, "curl": (0, 0, .03, .05), "thumb": .0},
                      "n": {"dir": (0, -1), "spread": .3, "curl": (0, 0, .03, .05), "thumb": .0}}),
    "nose_wall": (0.12, 0.05, {"f": ("ik", (200, -300), -1), "n": ("ik", (250, -290), -1)},
                  {"f": {"curl": (.5, .5, .55, .6), "thumb": .4, "dir": (.3, -1)}, "n": {"curl": (.5, .5, .55, .6), "thumb": .4, "dir": (.3, -1)}}),
    "chin_fist": (0.28, 0.2, {"f": ("ik", (200, -170), -1), "n": ("ik", (200, -378), -1)},
                  {"f": {"curl": (.5, .5, .55, .6), "thumb": .4}, "n": {"dir": (0, -1), "curl": (.8, .85, .9, .9), "thumb": .7}}),
    "pinch": (0.08, 0.04, {"f": ("ang", 0.2, 0.25), "n": ("ik", (320, -420), -1)},
              {"n": {"dir": (.6, -1), "curl": (.35, .7, .95, .95), "spread": .0, "thumb": .85}}),
    "sneak": (0.42, 0.25, {"f": ("ik", (120, -150), -1), "n": ("ik", (230, -210), -1)},
              {"f": {"dir": (.6, .6), "curl": (.4, .45, .5, .55), "thumb": .3}, "n": {"dir": (.8, .4), "curl": (.4, .45, .5, .55), "thumb": .3}}),
    "lid_finger": (0.16, 0.12, {"f": ("ik", (200, -195), -1), "n": ("ik", (330, -215), -1)},
                   {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (1, -.35), "curl": (0, .8, .85, .85), "spread": .05, "thumb": .6}}),
    "sock_pull": (0.55, 0.3, {"f": ("ik", (310, 130), -1), "n": ("ik", (360, 150), -1)},
                  {"f": {"dir": (.4, 1), "curl": (.55, .6, .65, .7), "thumb": .6}, "n": {"dir": (.5, 1), "curl": (.55, .6, .65, .7), "thumb": .6}}),
    "jug_pour": (0.12, 0.12, {"f": ("ik", (250, -250), -1), "n": ("ik", (330, -330), -1)},
                 {"f": {"dir": (.3, -1), "curl": (.55, .6, .65, .7), "thumb": .6}, "n": {"dir": (1, .2), "curl": (.65, .7, .75, .75), "thumb": .7}}),
    "glass_drink": (-0.04, -0.14, {"f": ("ang", 0.2, 0.25), "n": ("ik", (150, -420), -1)},
                    {"n": {"dir": (.3, -1), "curl": (.55, .6, .65, .7), "thumb": .6}}),
    "type": (0.12, 0.1, {"f": ("ik", (200, -200), -1), "n": ("ik", (275, -205), -1)},
             {"f": {"dir": (1, .25), "curl": (.25, .3, .35, .4), "thumb": .25}, "n": {"dir": (1, .25), "curl": (.25, .3, .35, .4), "thumb": .25}}),
    "point_a": (0.0, -0.18, {"f": ("ang", 0.2, 0.25), "n": ("ik", (300, -600), -1)},
                {"n": {"dir": (.8, -1), "curl": (0, .85, .9, .9), "spread": .05, "thumb": .7}}),
    "point_b": (0.0, -0.1, {"f": ("ang", 0.2, 0.25), "n": ("ik", (360, -470), -1)},
                {"n": {"dir": (1, -.4), "curl": (0, .85, .9, .9), "spread": .05, "thumb": .7}}),
    "hooray": (-0.04, -0.15, {"f": ("ik", (-120, -820), 1), "n": ("ik", (200, -830), -1)},
               {"f": {"dir": (-.2, -1), "spread": .45, "curl": (0, .05, .1, .1), "thumb": .1}, "n": {"dir": (.2, -1), "spread": .45, "curl": (0, .05, .1, .1), "thumb": .1}}),
    "shrug": (0.0, 0.12, {"f": ("ik", (60, -230), 1), "n": ("ik", (230, -250), -1)},
              {"f": {"dir": (-.5, -1), "spread": .35, "curl": (0, .05, .1, .15), "thumb": .1}, "n": {"dir": (.6, -1), "spread": .35, "curl": (0, .05, .1, .15), "thumb": .1}}),
    "temple": (0.0, 0.08, {"f": ("ang", 0.2, 0.25), "n": ("ik", (55, -530), 1)},
               {"n": {"dir": (.15, -1), "curl": (0, .85, .9, .9), "spread": .05, "thumb": .7}}),
    "mug_hold": (0.04, 0.04, {"f": ("ik", (190, -230), -1), "n": ("ik", (260, -300), -1)},
                 {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"kind": "none"}}),
    "mug_drink": (-0.06, -0.18, {"f": ("ik", (190, -230), -1), "n": ("ik", (165, -430), -1)},
                  {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"kind": "none"}}),
})


def tiptoe_kw(x, y, scale, phase=0.0, who="dima"):
    """Ноги крадучись на цыпочках: колени согнуты, пятки подняты (phi < 0), шаг маленький. (x, y) — таз."""
    sc = scale * HEIGHT.get(who, 1.0)
    s = math.sin(2 * math.pi * phase)
    lift = max(0.0, s) * 40 * sc
    lift2 = max(0.0, -s) * 40 * sc
    return {"feet": {"n": ((x + (90 + 60 * s) * sc, y + 520 * sc - lift), -.7), "f": ((x + (-20 - 60 * s) * sc, y + 525 * sc - lift2), -.7)}}


def sock_feet_kw(x, y, scale, lift=1.0, who="dima"):
    """Сидит на краю кровати: дальняя нога на полу, ближняя поднята коленом к груди (lift 0…1) — ступня к рукам (поза sock_pull)."""
    sc = scale * HEIGHT.get(who, 1.0)
    u = lib.clamp(lift)
    n = ((x + (300 - 30 * u) * sc, y + (300 - 150 * u) * sc), .15 * u)
    return {"feet": {"n": n, "f": ((x + 250 * sc, y + 306 * sc), 0.0)}}


def _cocoon_quilt(L, Hh, roll, seed, col):
    c, csh, chi, st = col
    o = []
    # спиральные складки бегут при прокатке
    ph = (roll / 360.0) % 1.0
    for j in range(7):
        q = (j / 7 + ph) % 1.0
        xx = -L / 2 + 120 + (L - 240) * q
        o.append(line([(xx - 30, -Hh + 20), (xx + 10, -Hh * .5), (xx - 20, -10)], 5.0, csh, taper=.3, wmin=.5, seed=seed + j, op=.85))
        o.append(line([(xx + 26, -Hh + 30), (xx + 40, -Hh * .45)], 7.0, st, taper=.3, wmin=.6, seed=seed + 20 + j, op=.9))
    o.append(blob([(-L / 2, -12), (L / 2, -12), (L / 2, 10), (-L / 2, 10)], csh))
    o.append(blob([(-L * .4, -Hh * .85), (L * .3, -Hh * .92), (L * .3, -Hh * .72), (-L * .4, -Hh * .66)], chi, .8))
    return "".join(o)


def cocoon_feet(x, y, k, t, u=1.0, seed=0):
    """Две босые ступни, высунутые из конца кокона (x, y) — центр конца, пальцы вправо; шевелятся по t."""
    global C
    C = PAL["dima"]
    o = []
    for j, dy in enumerate((-40, 40)):
        wig = 10 * math.sin(t * 11 + j * 1.9)
        ax, ay = x - 20 * k, y + dy * k
        tip = (x + (70 + 60 * u) * k, y + dy * k - 10 * k + wig * k)
        foot = [(ax, ay - 34 * k), (tip[0] - 20 * k, tip[1] - 36 * k), (tip[0] + 10 * k, tip[1] - 18 * k), (tip[0] + 14 * k, tip[1] + 14 * k),
                (tip[0] - 26 * k, ay + 34 * k), (ax, ay + 30 * k)]
        inner = blob([(ax, ay + 10 * k), (tip[0], tip[1] + 6 * k), (tip[0], tip[1] + 30 * k), (ax, ay + 40 * k)], C["SKIN_SH"], .8)
        o.append(shape(foot, C["SKIN"], inner, w=4.0 * k / .9, seed=7700 + seed + j))
        for q in range(3):
            tx = tip[0] + 6 * k
            ty = tip[1] - 12 * k + q * 13 * k
            o.append(line([(tx - 10 * k, ty), (tx + 4 * k, ty + 2 * k)], 2.6, INK, taper=.5, wmin=.3, seed=7710 + seed + 3 * j + q, op=.8))
    return "".join(o)


def dima_cocoon(x, y, k=1.0, roll=0.0, squash=0.0, wriggle=0.0, sag=0.0, expr=None, hood=False, t=0.0, head_rot=None, feet=1.0, seed=0, col=C_COCOON):
    global C
    ex = EXPR["dima"].get(expr, {}) if isinstance(expr, str) else dict(expr or EXPR["dima"]["sleepy"])
    c, csh, chi, st = col
    sd = 7600 + seed
    if not hood:
        L, Hh = 900.0, 330.0
        sy = 1 - .35 * squash
        sx = 1 + .18 * squash
        # контур с волной гусеницы
        top = []
        n = 14
        for i in range(n + 1):
            q = i / n
            xx = -L / 2 + L * q
            wv = wriggle * 40 * math.sin(2 * math.pi * (q * 1.4 - t * 2.2))
            hh = Hh * (math.sin(math.pi * min(1, max(0, (q * 1.05)))) ** .35) + wv
            top.append((xx, -hh))
        pts = [(-L / 2, -10, 1)] + top[1:-1] + [(L / 2, -10, 1), (L * .3, 6), (-L * .3, 6)]
        body = _cocoon_quilt(L, Hh, roll, sd, col)
        o = [blob(lib.ellipse_pts(0, 8, L * .52, 26, 18), "#3a2a20", .2)]
        o.append(f'<g transform="scale({sx:.4f} {sy:.4f})">')
        # ступни справа (под краем одеяла)
        o.append(cocoon_feet(L / 2 - 30, -Hh * .38, 1.0, t, feet, seed))
        o.append(shape(pts, c, body, w=6.0, seed=sd))
        # голова слева: торчит из «рукава» одеяла
        hr = -70.0 if head_rot is None else head_rot
        hx, hy = -L / 2 - 20, -Hh * .5
        C = PAL["dima"]
        head = f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({hr + 4 * math.sin(t * 3.1) * wriggle:.2f}) scale(1.15)">{dima_head(ex)}</g>'
        o.append(head)
        # край одеяла вокруг шеи — поверх головы снизу
        rim = [(-L / 2 + 140, -Hh * .98), (-L / 2 + 185, -Hh * .5), (-L / 2 + 150, -6), (-L / 2 + 230, -10), (-L / 2 + 270, -Hh * .5),
               (-L / 2 + 230, -Hh * 1.02)]
        o.append(shape(rim, chi, blob([(-L / 2 + 190, -Hh), (-L / 2 + 260, -Hh), (-L / 2 + 260, 0), (-L / 2 + 190, 0)], c, .9), w=5.0, seed=sd + 40))
        o.append("</g>")
        rr = 4 * math.sin(math.radians(roll)) + 0
        svg = f'<g transform="translate({x:.2f} {y:.2f}) rotate({rr:.2f}) scale({k:.5f})">{"".join(o)}</g>'
        hxw = x + (hx * sx) * k
        hyw = y + (hy * sy) * k
        return dict(svg=svg, head=(hxw, hyw))
    # ── сидит, одеяло капюшоном ──
    s_ = lib.clamp(sag)
    fig = person("dima", 0, 0, 1.0, ex, "rest", layers=("pelvis", "body"), shrug=.25 * (1 - s_))
    hx, hy = fig["head"]
    sq = 1 - .25 * squash
    o = [blob(lib.ellipse_pts(0, 6, 420, 30, 18), "#3a2a20", .2)]
    hyW = hy - 380
    e1 = lib.ease_io(min(1.0, s_ * 2))
    e2 = lib.ease_io(max(0.0, s_ * 2 - 1))
    top = hyW - 215 + (-690 - (hyW - 215)) * e1 + 250 * e2       # верх одеяла: над макушкой → плечи → пояс
    wid = 235 + 120 * e1
    # задняя часть одеяла (купол за головой)
    back = [(-400, 0, 1), (-420, -300), (-wid - 60, top + 330), (-wid, top + 120), (-150, top + 10), (0, top - 12), (150, top + 10), (wid, top + 120),
            (wid + 60, top + 330), (420, -300), (400, 0, 1)]
    o.append(shape(back, csh, line([(-wid * .6, top + 80), (-wid * .7, top + 300)], 4, mul(csh, .85), seed=sd + 50), w=6.0, seed=sd + 51))
    o.append(f'<g transform="translate(0 {-380:.1f})">{fig["svg"]}</g>')
    o.append(cocoon_feet(150, -40, 1.0, t, feet, seed))
    # передняя часть: обнимает тело от груди (или ниже) до пола, ступни торчат
    fy = min(-330.0, max(top + 300, -740) + 330 * e2)
    front = [(-390, 0, 1), (-420, -280), (-wid - 40, fy + 70), (-170, fy), (0, fy + 22), (170, fy), (wid + 40, fy + 70), (420, -280), (390, 0, 1)]
    f_in = _cocoon_quilt(820, 600, roll, sd + 60, col)
    o.append(shape(front, c, f_in, w=6.0, seed=sd + 61))
    o.append(line([(-6, fy + 24), (-24, -300), (6, -20)], 5, csh, taper=.3, wmin=.5, seed=sd + 62))
    # край капюшона над лбом (пока одеяло на голове)
    cover = ex.get("cover", 0.0)
    if e1 < .5:
        dy = 260 * e1 + 95 * cover
        hhx = hx
        rim = [(hhx - wid - 10, top + 140 + dy), (hhx - 150, top + 20 + dy), (hhx + 10, top - 6 + dy), (hhx + 170, top + 20 + dy), (hhx + wid + 10, top + 140 + dy),
               (hhx + 150, top + 80 + dy), (hhx + 10, top + 62 + dy + 30 * cover), (hhx - 140, top + 80 + dy)]
        o.append(shape(rim, c, blob([(hhx - 300, top + 40 + dy), (hhx + 300, top + 40 + dy), (hhx + 300, top + 70 + dy), (hhx - 300, top + 70 + dy)],
                                    chi, .9), w=5.4, seed=sd + 70))
    svg = f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.5f} {k * sq:.5f})">{"".join(o)}</g>'
    return dict(svg=svg, head=(x + hx * k, y + (hy - 380) * k * sq))


def mul(h, kk):
    return lib.mul(h, (kk, kk, kk))


def cocoon_blanket(x, y, k=1.0, u=0.0, t=0.0, seed=0, col=C_COCOON):
    """Одеяло распахнулось и улетает вверх, вращаясь (u 0…1). (x, y) — центр."""
    if u >= 1:
        return ""
    c, csh, chi, st = col
    sd = 7800 + seed
    op = lib.ease_out(lib.clamp(u / .35))
    fl = lib.clamp((u - .3) / .7)
    w, h = 520 + 420 * op, 360 + 120 * op
    pts = [(-w / 2, -h / 2, 1), (-w * .1, -h / 2 - 40 * math.sin(t * 9)), (w / 2, -h / 2, 1), (w / 2 + 30 * math.sin(t * 8), 0), (w / 2, h / 2, 1),
           (0, h / 2 + 40 * math.sin(t * 10)), (-w / 2, h / 2, 1), (-w / 2 - 30, 0)]
    inner = "".join(line([(-w / 2 + w * q, -h / 2), (-w / 2 + w * q + 20, h / 2)], 7, st, taper=.2, wmin=.6, seed=sd + i, op=.9)
                    for i, q in enumerate((.2, .4, .6, .8)))
    inner += blob([(-w / 2, h * .2), (w / 2, h * .2), (w / 2, h / 2), (-w / 2, h / 2)], csh)
    yy = y - 900 * fl * fl
    rr = 25 * fl + 6 * math.sin(t * 6)
    return f'<g transform="translate({x:.1f} {yy:.1f}) rotate({rr:.2f}) scale({k * (1 - .3 * fl):.4f})">{shape(pts, c, inner, w=5.6, seed=sd)}</g>'


# ═════════════════════════════ РИЛС 72 «СДВГ НЕ СУЩЕСТВУЕТ» (автор — группа B) ═════════════════════════════
# Дима взрослый (горчичное худи) — dima(x, y, scale, expr, pose, **ноги). (x, y) — таз, Дима смотрит вправо (flip=True — влево).
# Позы POSE (цели рук — в долях масштаба от таза):
#   phone_face  — развалился, ближняя кисть держит телефон у лица (центр телефона ≈ (215, −470)·sc, экран к Диме: рисовать
#                 people.mobilnik ПОСЛЕ фигуры в hand_pos(...) — спинка к зрителю), дальняя на животе
#   hand_hang   — ближняя рука зависла вперёд, пальцы полусогнуты (телефон забрали) ≈ (330, −330)·sc
#   press_back  — вжимается: кисти к груди, плечи вверх (с shrug=0.6–1 и expr "saucer")
#   hug_knees   — сидит, обнял колени (ноги — knees_kw); chin_knees — уткнулся подбородком в колени; lift_head — поднимает голову
#   pull_cord   — стоит, дальняя рука вперёд на раме, ближняя тянет тросик (цель ближней руки — ручка: arms={"n": ("ik", ручка, -1)})
#   strain      — тужится как атлет: кулаки у груди, локти в стороны (expr "strain" + strain_marks)
#   palm_up     — ближняя ладонь вверх перед собой ≈ (320, −250)·sc (клочок кладёт сцена: palm_point(...))
#   lid_finger  — (уже есть, из 71) крышка ноутбука одним пальцем; laptop_lap — обе кисти у ноутбука на коленях
#   lean_back   — откинулся назад, руки упёрты сзади (рисовать layers=LAYERS_BEHIND)
# Ноги: beanbag_kw (полулёжа в кресле-мешке, ноги вперёд), knees_kw (колени к груди, сидит на бревне/земле; tight 0…1),
#   plop_kw (сел на траву, ноги вытянуты), crouch_kw (присел на корточки), sit_kw/stand_kw — из 70/63.
# Мимика EXPR["dima"]: glassy (стеклянный взгляд в телефон), slump (обмяк), strain (надутые щёки, брови сведены), downcast (утыкается),
#   dawn (озарение), giggle (прыскает от смеха), warm (тёплый у огня), lean_rest (откинулся, глаза прикрыты).
# strain_marks(head_xy, scale, t, u) — жилка на виске и капля пота (поверх фигуры).
# dima_shadow(x, y, k, age_u, t, col) — ТЕНЬ Димы (сплошной силуэт без деталей) растёт из детской (kid2) во взрослую; (x, y) — ступни.
# smoke_figure(kind, x, y, k, u, t, fade, seed) — силуэт из дыма ТОЛЬКО ЛИНИЕЙ (без заливки), (x, y) — низ по центру, высота ≈ 900·k:
#   "teacher" — учительница с пучком, указка в одной руке, другой грозит пальцем; "mom" — мама руки в боки, качает головой;
#   "self" — крупное хмурое лицо Димы (лохматый, щетина-штрихи). u 0…1 — дым сплетается в контур; fade 0…1 — рассыпается клочьями
#   вверх (для s11); t — дым колышется.
# Кот (cat.py, новые ключи st): paw_l (левая передняя лапа тянется, как paw у правой), paw_l_dx; smug 0…1 (тяжёлые веки, бровь-штрих
#   вверх, ухмылка краем рта); mouth_item — SVG в точке рта (локально (836, 1130) кота, до масштаба: кубик в зубах).
#   cat_paw_tip(x, y, k, st, side="r"|"l") → кончик лапы в мире (без rot/sx), cat_nod(t, t0, dur, amp) → st["drop"] кивка.
#   cat_forearm(base, tip, k, claw) — лапа кота до локтя без кота (лопает шарик s02).
#   CAT_ST[имя] — готовые состояния: smug, spread (разводит лапами), point (показывает лапой вправо), warm (тёплый, глаза щёлочками),
#   reach (тянет лапу к зрителю), split (обе лапы вниз на лёд).
EXPR["dima"].update({
    "glassy": {"brows": "calm", "mouth": "flat", "lid": .5, "look": (.1, -.15), "bags": False},
    "slump": {"brows": "tired", "mouth": "tired", "lid": .32, "look": (.2, -.1), "bags": False},
    "strain": {"brows": "pinch", "mouth": "puff", "puff": 1.0, "lid": .35, "squeeze": 1.0, "bags": False},
    "downcast": {"brows": "sad", "mouth": "frown", "lid": .25, "look": (.2, .8)},
    "dawn": {"brows": "up", "mouth": "o", "open": .25, "lid": 1.0, "look": (.4, -.2)},
    "giggle": {"brows": "up", "mouth": "laugh", "open": .6, "laugh": 1.0, "hair": 4, "bags": False},
    "warm": {"brows": "calm", "mouth": "smile", "smile": .6, "lid": .6, "look": (.5, .2)},
    "lean_rest": {"brows": "calm", "mouth": "smile", "smile": .8, "lid": .3, "look": (.2, -.3)},
    "smug72": {"brows": "one_up", "mouth": "side", "lid": .5, "look": (.4, 0), "bags": False},
})

POSE.update({
    "phone_face": (-0.22, 0.05, {"f": ("ik", (140, -150), -1), "n": ("ik", (190, -400), -1)},
                   {"f": {"curl": (.4, .4, .45, .5), "thumb": .4, "dir": (1, .3)}, "n": {"dir": (.2, -1), "curl": (.6, .62, .66, .7), "thumb": .6}}),
    "hand_hang": (-0.12, 0.08, {"f": ("ik", (140, -150), -1), "n": ("ik", (330, -330), -1)},
                  {"f": {"curl": (.4, .4, .45, .5), "thumb": .4, "dir": (1, .3)}, "n": {"dir": (1, -.2), "curl": (.35, .45, .5, .55), "thumb": .45}}),
    "press_back": (-0.28, -0.05, {"f": ("ik", (110, -290), -1), "n": ("ik", (160, -305), -1)},
                   {"f": {"dir": (.3, -1), "curl": (.7, .7, .75, .75), "thumb": .6}, "n": {"dir": (.2, -1), "curl": (.7, .72, .75, .78), "thumb": .6}}),
    "hug_knees": (0.22, 0.12, {"f": ("ik", (200, -200), -1), "n": ("ik", (250, -190), -1)},
                  {"f": {"dir": (-.6, .6), "curl": (.55, .6, .65, .7), "thumb": .5}, "n": {"dir": (-.8, .4), "curl": (.55, .6, .65, .7), "thumb": .5}}),
    "chin_knees": (0.5, 0.45, {"f": ("ik", (200, -190), -1), "n": ("ik", (250, -180), -1)},
                   {"f": {"dir": (-.6, .6), "curl": (.55, .6, .65, .7), "thumb": .5}, "n": {"dir": (-.8, .4), "curl": (.55, .6, .65, .7), "thumb": .5}}),
    "lift_head": (0.08, -0.22, {"f": ("ik", (200, -205), -1), "n": ("ik", (250, -195), -1)},
                  {"f": {"dir": (-.6, .6), "curl": (.55, .6, .65, .7), "thumb": .5}, "n": {"dir": (-.8, .4), "curl": (.55, .6, .65, .7), "thumb": .5}}),
    "pull_cord": (-0.12, -0.05, {"f": ("ik", (330, -190), -1), "n": ("ik", (-170, -180), 1)},
                  {"f": {"dir": (1, .4), "curl": (.6, .65, .7, .7), "thumb": .5}, "n": {"dir": (-.3, -1), "curl": (.75, .78, .8, .8), "thumb": .7}}),
    "strain": (0.05, 0.05, {"f": ("ik", (120, -300), -1), "n": ("ik", (230, -290), -1)},
               {"f": {"dir": (.3, -1), "curl": (.85, .9, .9, .9), "thumb": .8}, "n": {"dir": (.2, -1), "curl": (.85, .9, .9, .9), "thumb": .8}}),
    "palm_up": (0.2, 0.15, {"f": ("ik", (180, -160), -1), "n": ("ik", (330, -260), -1)},
                {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (1, -.15), "flip": -1, "spread": .3, "curl": (.05, .1, .15, .2), "thumb": .15}}),
    "laptop_lap": (0.12, 0.15, {"f": ("ik", (230, -200), -1), "n": ("ik", (320, -210), -1)},
                   {"f": {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .3}, "n": {"dir": (1, .3), "curl": (.3, .3, .35, .4), "thumb": .3}}),
    "lean_back": (-0.22, -0.12, {"f": ("ang", -0.5, -0.1), "n": ("ang", -0.4, -0.1)},
                  {"f": {"dir": (-.6, 1), "curl": (.2, .2, .25, .3), "thumb": .2}, "n": {"dir": (-.6, 1), "curl": (.2, .2, .25, .3), "thumb": .2}}),
})


def beanbag_kw(x, y, scale, sag=0.0, who="dima"):
    """Полулёжа в кресле-мешке: ноги вперёд-вниз, пятки на полу (≈ 330·sc ниже таза)."""
    sc = scale * HEIGHT.get(who, 1.0)
    return {"feet": {"n": ((x + (470 + 30 * sag) * sc, y + (300 - 30 * sag) * sc), -.25), "f": ((x + (420 + 30 * sag) * sc, y + (306 - 30 * sag) * sc), -.25)}}


def knees_kw(x, y, scale, tight=1.0, ground=190.0, who="dima"):
    """Колени к груди: стопы на земле (ground·sc ниже таза), близко к тазу (tight 1) … дальше (tight 0)."""
    sc = scale * HEIGHT.get(who, 1.0)
    u = lib.clamp(tight)
    ax = 320 - 210 * u
    return {"feet": {"n": ((x + ax * sc, y + ground * sc), 0.0), "f": ((x + (ax - 40) * sc, y + (ground + 6) * sc), 0.0)}}


def plop_kw(x, y, scale, who="dima"):
    """Сел на землю: ноги вытянуты вперёд, носки вверх."""
    sc = scale * HEIGHT.get(who, 1.0)
    return {"feet": {"n": ((x + 560 * sc, y + 40 * sc), -.9), "f": ((x + 520 * sc, y + 50 * sc), -.9)}}


def crouch_kw(x, y, scale, who="dima"):
    """На корточках: таз низко над пятками, колени высоко вперёд."""
    sc = scale * HEIGHT.get(who, 1.0)
    return {"feet": {"n": ((x + 170 * sc, y + 140 * sc), -.5), "f": ((x + 110 * sc, y + 146 * sc), -.5)}}


def hand_pos(fig, side="n", ahead=60.0):
    """Точка в ладони: запястье + ahead·scale по направлению предплечья (для телефона, клочка, ручки)."""
    w = np.array(fig["wrist"][side], float)
    e = np.array(fig["elbow"][side], float)
    d = (w - e) / (np.linalg.norm(w - e) + 1e-6)
    p = w + d * ahead * fig["scale"]
    return float(p[0]), float(p[1])


def strain_marks(head, scale, t=0.0, u=1.0, flip=False):
    """Жилка на виске (зигзаг) и капля пота у лба. head — центр головы из figure()."""
    if u <= 0.01:
        return ""
    s = scale
    sx = -1 if flip else 1
    hx, hy = head
    pul = 1 + .15 * math.sin(t * 20)
    vx, vy = hx + sx * 20 * s, hy - 70 * s
    v = [(vx - sx * 18 * s * pul, vy - 14 * s), (vx, vy), (vx - sx * 14 * s * pul, vy + 12 * s), (vx + sx * 4 * s, vy + 26 * s)]
    o = line(v, 7 * s * 2, "#C2493D", taper=.3, wmin=.4, seed=7201, op=u)
    o += line([(vx + sx * 30 * s, vy - 26 * s), (vx + sx * 42 * s, vy - 38 * s)], 5 * s * 2, "#C2493D", taper=.6, wmin=.2, seed=7202, op=u)
    o += line([(vx + sx * 30 * s, vy + 30 * s), (vx + sx * 44 * s, vy + 40 * s)], 5 * s * 2, "#C2493D", taper=.6, wmin=.2, seed=7203, op=u)
    dy = 40 * s * ((t * 1.3) % 1)
    dxp, dyp = hx - sx * 110 * s, hy - 40 * s + dy
    drop = [(dxp, dyp - 26 * s, 1), (dxp + 12 * s, dyp), (dxp, dyp + 12 * s), (dxp - 12 * s, dyp)]
    o += shape(drop, "#9BD3F0", blob([(dxp - 4 * s, dyp - 4 * s), (dxp - 1 * s, dyp - 10 * s), (dxp + 1 * s, dyp - 2 * s)], "#FFFFFF"), w=3.2, seed=7204)
    return o


_SHADOW_F = "dshadowfill"


def dima_shadow(x, y, k=1.0, age_u=1.0, t=0.0, col="#0B0E22", blur_sd=3.0):
    """Тень-силуэт Димы стоя (сплошной цвет col, без деталей): age_u 0 — мальчик (kid2), 1 — взрослый. Рост тени плавно растёт;
    на середине (0.45–0.55) силуэт меняется под прикрытием — оба одного роста в этот момент. (x, y) — ступни."""
    u = lib.clamp(age_u)
    fid = f"{_SHADOW_F}{col[1:]}"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        r, g, b = (int(col[i:i + 2], 16) / 255 for i in (1, 3, 5))
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 {r:.3f} '
                        f'0 0 0 0 {g:.3f} 0 0 0 0 {b:.3f} 0 0 0 1 0"/><feGaussianBlur stdDeviation="{blur_sd}"/></filter>')
    h_kid, h_ad = .62, 1.0
    hgt = h_kid + (h_ad - h_kid) * lib.ease_io(u)
    adult = u >= .5
    sc0 = .5
    legs_h = (LEG_LEN - 12) * sc0
    if adult:
        fig = person("dima", 0, -legs_h, sc0, "warm", "rest", feet=stand_kw(0, -legs_h, sc0)["feet"])
        base_h = 1.0
    else:
        hk = HEIGHT.get("kid2", .66)
        fig = person("kid2", 0, -(LEG_LEN * KID_LEG_K - 12) * sc0 * hk, sc0, "beam", "rest",
                     feet=stand_kw(0, -(LEG_LEN * KID_LEG_K - 12) * sc0 * hk, sc0, who="kid2")["feet"])
        base_h = h_kid
    s = k * hgt / base_h
    sway = 1.5 * math.sin(t * 5)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({sway:.2f}) scale({s:.4f})" filter="url(#{fid})">{fig["svg"]}</g>'


# ── дымные силуэты: только линия дыма ──
SMOKE_COL = "#C9D3E3"
SMOKE_HI = "#EEF2F8"


def _smoke_line(pts, k, t, u, fade, seed, w=12.0):
    """Полилиния дыма: проявляется по длине (u), колышется (t), рассыпается вверх клочьями (fade)."""
    P_ = lib.sample([(p[0], p[1]) for p in pts], False, 6.0) if len(pts) > 2 else np.array(pts, float)
    P_ = np.array(P_, float)
    n = len(P_)
    if n < 2:
        return ""
    m = max(2, int(n * lib.clamp(u)))
    P_ = P_[:m]
    Tg = np.gradient(P_, axis=0)
    Tg /= (np.linalg.norm(Tg, axis=1, keepdims=True) + 1e-6)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    idx = np.arange(m)
    wob = 7 * np.sin(t * 2.4 + idx * .35 + seed) + 4 * np.sin(t * 4.1 + idx * .8)
    Q = P_ + N * wob[:, None]
    Q[:, 1] -= (t * 6) % 1 * 0      # без дрейфа целиком: колышется на месте
    o = []
    if fade <= 0.01:
        pts2 = [(x * k, y * k) for x, y in Q]
        o.append(line(pts2, w * k * 2.2 + 3, "#8E9AB0", taper=.35, wmin=.2, seed=seed))
        o.append(line(pts2, w * k * 2.2, SMOKE_COL, taper=.4, wmin=.15, seed=seed + 1))
        o.append(line(pts2, w * k * .8, SMOKE_HI, taper=.6, wmin=.1, seed=seed + 2))
        return "".join(o)
    # рассыпается: куски по 6 точек, каждый уплывает вверх и тает
    rs = np.random.RandomState(seed % 2**31)
    f = lib.clamp(fade)
    for a in range(0, m - 2, 5):
        seg = Q[a:a + 6].copy()
        if len(seg) < 2:
            continue
        drift = rs.uniform(.6, 1.4)
        seg[:, 1] -= 260 * f * drift
        seg[:, 0] += 60 * f * rs.uniform(-1, 1)
        shrink = 1 - f
        if shrink < .05:
            continue
        c = seg.mean(0)
        seg = c + (seg - c) * (.4 + .6 * shrink)
        pts2 = [(x * k, y * k) for x, y in seg]
        o.append(line(pts2, w * k * 2 * shrink + 2, "#8E9AB0", taper=.5, wmin=.2, seed=seed + a))
        o.append(line(pts2, w * k * 2 * shrink, SMOKE_COL, taper=.5, wmin=.2, seed=seed + a + 1))
        if f > .3 and a % 10 == 0:   # искорки
            cx, cy = c[0] * k, c[1] * k - 40 * f * k
            o.append(blob(ellipse_pts(cx, cy, 6 * k * shrink + 2, 6 * k * shrink + 2, 8), "#FFD24A"))
    return "".join(o)


def _arc(cx, cy, rx, ry, a0, a1, n=14):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _smoke_paths(kind, t):
    """Контуры силуэтов в своих координатах: низ по центру (0, 0), высота ≈ 900."""
    if kind == "teacher":
        wag = 14 * math.sin(t * 9)
        P_ = []
        P_.append(_arc(0, -720, 70, 82, 0, 360, 20))                                   # голова
        P_.append(_arc(10, -820, 44, 36, 180, 540, 14))                                # пучок
        P_.append([(-46, -644), (-70, -600), (-120, -560), (-150, -300), (-200, 0)])   # левый бок платья
        P_.append([(46, -644), (70, -600), (120, -560), (150, -300), (200, 0)])        # правый бок
        P_.append([(-200, 0), (0, 12), (200, 0)])                                      # подол
        # правая рука вверх, грозит пальцем
        ex, ey = 230, -700
        P_.append([(110, -570), (200, -600), (ex, ey)])
        P_.append([(ex, ey), (ex + 6 + wag, ey - 70), (ex + 10 + wag * 1.5, ey - 120)])     # палец
        P_.append(_arc(ex, ey + 6, 26, 30, 0, 360, 10))                                # кулак
        # левая рука с указкой
        P_.append([(-110, -570), (-190, -470), (-230, -420)])
        P_.append([(-230, -420), (-330, -640), (-380, -760)])                          # указка
        P_.append([(-28, -722), (-10, -730)])                                          # бровь-хмурь
        P_.append([(26, -730), (44, -722)])
        P_.append([(-14, -680), (16, -684)])                                           # поджатые губы
        return P_
    if kind == "mom":
        sh = 10 * math.sin(t * 7)
        P_ = []
        P_.append([(p[0] + sh, p[1]) for p in _arc(0, -720, 72, 84, 0, 360, 20)])     # голова (качает)
        P_.append([(p[0] + sh, p[1]) for p in _arc(0, -748, 92, 82, 190, 350, 14)])   # волосы шапкой
        P_.append([(-80 + sh, -700), (-96 + sh, -640), (-82 + sh, -600)])            # пряди
        P_.append([(80 + sh, -700), (96 + sh, -640), (82 + sh, -600)])
        P_.append([(-40 + sh, -730), (-14 + sh, -722)])                                # брови домиком
        P_.append([(14 + sh, -722), (40 + sh, -730)])
        P_.append([(-16 + sh, -676), (0 + sh, -684), (16 + sh, -676)])                # рот вниз
        P_.append([(-50, -640), (-110, -590), (-118, -420), (-160, 0)])                # бока
        P_.append([(50, -640), (110, -590), (118, -420), (160, 0)])
        P_.append([(-160, 0), (0, 12), (160, 0)])
        # руки в боки: локти наружу треугольником
        P_.append([(-110, -580), (-240, -480), (-118, -400)])
        P_.append([(110, -580), (240, -480), (118, -400)])
        return P_
    # self: крупное хмурое лицо Димы
    lean = 4 * math.sin(t * 3)
    P_ = []
    P_.append(_arc(0, -450, 260, 320, 20, 160, 18))                                    # низ лица (подбородок)
    P_.append([(-250, -340), (-262, -460), (-240, -580)])
    P_.append([(250, -340), (262, -460), (240, -580)])
    hair = [(-260, -560), (-300, -700, ), (-200, -660), (-210, -820), (-100, -720), (-60, -880), (20, -740), (110, -870), (140, -710), (260, -790), (240, -640),
            (300, -620), (250, -560)]
    P_.append(hair)
    P_.append([(-170, -520 + lean), (-110, -490 + lean), (-50, -470 + lean)])          # брови сведены
    P_.append([(50, -470 + lean), (110, -490 + lean), (170, -520 + lean)])
    P_.append(_arc(-100, -410, 36, 26, 200, 340, 8))                                   # глаза-прищур
    P_.append(_arc(100, -410, 36, 26, 200, 340, 8))
    P_.append([(-80, -230), (0, -250), (80, -230)])                                    # рот вниз
    for j in range(5):
        P_.append([(-150 + 75 * j, -200 + 12 * (j % 2)), (-140 + 75 * j, -180 + 12 * (j % 2))])   # щетина
    return P_


def smoke_figure(kind, x, y, k=1.0, u=1.0, t=0.0, fade=0.0, seed=0):
    if u <= 0.01:
        return ""
    o = []
    for j, pts in enumerate(_smoke_paths(kind, t)):
        uj = lib.clamp(u * 1.4 - j * .03)
        if uj <= 0:
            continue
        w = 12.0 if len(pts) > 3 else 9.0
        o.append(_smoke_line(pts, 1.0, t + j * .7, uj, fade, 7300 + seed * 50 + j, w=w))
    rise = 0.0
    return f'<g transform="translate({x:.2f} {y + rise:.2f}) scale({k:.4f})">{"".join(o)}</g>'


# ── кот: помощники ──
CAT_ST = {
    "smug": {"smug": 1.0, "look": (.3, .1), "tilt": -6, "smile": 0.0},
    "spread": {"paw": .8, "paw_l": .8, "paw_dx": 90, "paw_l_dx": 90, "smug": .7, "tilt": 6},
    "point": {"paw": 1.0, "paw_dx": 110, "look": (.8, 0), "smug": .5},
    "warm": {"blink": .55, "smile": 1.0, "look": (0, .2), "flame_e": 1.5},
    "reach": {"paw": 1.0, "paw_dx": 30, "look": (0, 0), "smile": 1.0},
    "split": {"paw": .7, "paw_l": .7, "paw_dx": 40, "paw_l_dx": 40, "perk": 1.0, "look": (0, .7)},
}


def cat_nod(t, t0, dur=0.32, amp=0.28):
    """st["drop"] кивка: голова опускается и возвращается (одно движение на [t0, t0+dur])."""
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return amp * math.sin(math.pi * u) ** 1.5


def cat_paw_tip(x, y, k, st, side="r"):
    """Кончик вытянутой передней лапы в мире (как в cat.body; поворот rot и sx/sy не учитываются)."""
    import cat
    if side == "r":
        paw, dx, fx = st.get("paw", 0.0), st.get("paw_dx", 70.0), cat.CX + 25
        lx = fx + dx * paw * 1.6
    else:
        paw, dx, fx = st.get("paw_l", 0.0), st.get("paw_l_dx", 70.0), cat.CX - 25
        lx = fx - dx * paw * 1.6
    ly = 1306 - 150 * paw
    return x + (lx - cat.CX) * k, y + (ly - cat.CBOT) * k


def cat_forearm(base, tip, k=1.0, claw=0.0, seed=0):
    """Лапа кота до локтя (средний план, без самого кота): из base (локоть, обычно за краем кадра) к tip (подушечка).
    k — масштаб как у кота (cat k), claw 0…1 — коготь выпущен. Шерсть, подушечки, коготь — как у cat.py."""
    import cat
    from ink import band as _band
    bx, by = base
    tx, ty = tip
    dx, dy = tx - bx, ty - by
    L = math.hypot(dx, dy) + 1e-6
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    mid = (bx + dx * .5 + nx * 14 * k, by + dy * .5 + ny * 14 * k)
    arm = _band([base, mid, (tx - ux * 10 * k, ty - uy * 10 * k)], 66 * k, 54 * k, step=4, cap=False)
    sh = [(bx + nx * 30 * k, by + ny * 30 * k), (tx + nx * 26 * k, ty + ny * 26 * k), (tx, ty), (bx, by)]
    o = shape(arm, cat.CAT, blob(sh, cat.CAT_SH, .7) + "".join(
        line([(bx + dx * q - nx * 10 * k, by + dy * q - ny * 10 * k), (bx + dx * q + ux * 16 * k, by + dy * q + uy * 16 * k)], 2.4 * k, cat.CAT_EDGE, seed=seed + 7400 + i, op=.8)
        for i, q in enumerate((.2, .4, .6, .75))), w=4.8 * k, seed=seed + 7410)
    ang = math.degrees(math.atan2(uy, ux))
    pp = ellipse_pts(tx, ty, 40 * k, 34 * k, 14, rot=ang)
    o += shape(pp, cat.CAT, blob(ellipse_pts(tx + nx * 8 * k, ty + ny * 8 * k, 30 * k, 22 * k, 10, rot=ang), cat.CAT_SH, .5), w=4.6 * k, seed=seed + 7411)
    o += blob(ellipse_pts(tx + ux * 6 * k - nx * 6 * k, ty + uy * 6 * k - ny * 6 * k, 15 * k, 12 * k, 10, rot=ang), "#e8823a")
    for j in (-1, 0, 1):
        cx = tx + ux * 26 * k + nx * j * 16 * k
        cy = ty + uy * 26 * k + ny * j * 16 * k
        o += blob(ellipse_pts(cx, cy, 6.5 * k, 5.5 * k, 8), "#e8823a")
    if claw > .02:
        cx, cy = tx + ux * 36 * k, ty + uy * 36 * k
        L2 = 30 * k * claw
        o += shape([(cx - nx * 6 * k, cy - ny * 6 * k, 1), (cx + ux * L2, cy + uy * L2, 1), (cx + nx * 6 * k, cy + ny * 6 * k, 1)], "#F4F1EA", "", w=2.6 * k, seed=seed + 7412)
    return o


# ═════════════════════════════ РИЛС 73 «ТЫ САМ ВИНОВАТ» (автор — группа B) ═════════════════════════════
# Дима (горчичное худи) — dima(x, y, scale, expr, pose, **ноги); стоит — **stand_kw(x, y, scale); смотрит вправо (flip=True — влево).
# Мимика EXPR["dima"]: lost73 (растерянно смотрит вверх-вправо на доску), glance73 (оглядывается назад-влево), sag73 (плечи опустились,
#   взгляд вниз), awake73 (лежит без сна, глаза открыты, взгляд в потолок), stare73 (лицо на подушке, взгляд в сторону, мешки),
#   exhale73 (выдыхает: веки прикрыты, губы трубочкой), smile73 (улыбка краешком рта), unpin73 (сосредоточенно на конверте),
#   type73 (печатает с лёгкой улыбкой). awake_blink(base, u) — та же мимика с веками, прикрытыми на u (медленное моргание).
# Позы POSE: sag73 (руки повисли, голова опущена), glance73 (полуоборот головы назад), unpin73 (ближняя рука вверх-вперёд щепотью —
#   снимает конверт с кнопки ≈ (330, −560)·sc; кончики пальцев — hand_pos(fig, "n", 70)), open73 (держит конверт обеими руками у груди,
#   ближняя отгибает клапан), «pinch», «pet», «type» — из прошлых рилсов.
# dima_bed(x, y, k, expr, roll, sit, t, cover, arm, col, seed, pillow_col) — Дима в кровати (кровать и матрас — room.bedroom группы C):
#   (x, y) — таз на матрасе; голова на подушке СЛЕВА, ноги под одеялом вправо, лицом вверх; k — масштаб фигуры (голова ≈ 300·k).
#   roll 0…1 — поворачивается на бок (к зрителю): голова поворачивается, бугор плеча и бедра растёт, ближняя рука ложится поверх одеяла
#   к подушке (три позы через промежуточные кадры, без сжатия фигуры); sit 0…1 — садится (туловище поднимается из-под одеяла, ноги
#   остаются под ним); cover "chest" | "nose" (одеяло до носа) | доля 0…1 между ними; arm "out" (ближняя рука поверх одеяла) | "in";
#   expr — имя или dict; flip=True — голова на подушке СПРАВА (кровать room.BED73: изголовье справа). Возвращает dict(svg, head, wrist, pillow).
# cat_judge_shadow(x, y, k, st, t, col, w) — ТЕНЬ кота-судьи ЛИНИЕЙ (контур силуэта той же позы cat.draw, без заливки): для потолка.
# Кот — новые ключи cat.py st: cold 0…1 (холодный судья: веки наполовину, узкие зрачки-щёлки, прямой рот, уши прижаты), flat_ears
#   0…1 (только уши прижаты). CAT_ST: judge (холодный, смотрит на зрителя), judge_tap (холодный, правая лапа на конверт/стол),
#   challenge (наклон головы с вызовом, «бровь» вверх), warm73 (тёплый, глаза мягкие, огонёк ярче), nuzzle (бодает: голова наклонена,
#   глаза закрыты), sit_wrap (сидит, хвост обвит вокруг лап). Лап у кота всегда четыре: тянется ТА ЖЕ передняя лапа (paw/paw_l), вторая
#   стоит на опоре (cat.body сам не рисует стоячую лапу, когда она вытянута).
EXPR["dima"].update({
    "lost73": {"brows": "worry", "mouth": "flat", "lid": .85, "look": (.55, -.55)},
    "glance73": {"brows": "worry", "mouth": "flat", "lid": .8, "look": (-.8, -.1)},
    "sag73": {"brows": "sad", "mouth": "tired", "lid": .42, "look": (.25, .75)},
    "awake73": {"brows": "tired", "mouth": "flat", "lid": .82, "look": (.3, -.7)},
    "stare73": {"brows": "tired", "mouth": "flat", "lid": .7, "look": (.6, -.2)},
    "exhale73": {"brows": "calm", "mouth": "o", "open": .3, "lid": .35, "look": (.2, .2)},
    "smile73": {"brows": "calm", "mouth": "smile", "smile": .45, "lid": .55, "look": (.4, .45), "bags": False},
    "unpin73": {"brows": "det", "mouth": "flat", "lid": .75, "look": (.6, -.5), "bags": False},
    "type73": {"brows": "calm", "mouth": "smile", "smile": .35, "lid": .62, "look": (.55, .45), "bags": False},
})


def awake_blink(base="awake73", u=0.0):
    """Мимика base с веками, прикрытыми на u (0 — как base, 1 — закрыты): медленное моргание без смены лица."""
    e = dict(EXPR["dima"][base]) if isinstance(base, str) else dict(base)
    u = lib.clamp(u)
    if u > .9:
        e["closed"] = 1.0
    else:
        e["lid"] = e.get("lid", .8) * (1 - u)
    return e


POSE.update({
    "sag73": (0.12, 0.28, {"f": ("ang", 0.08, 0.06), "n": ("ang", -0.02, 0.08)},
              {"f": {"curl": (.25, .3, .35, .4), "thumb": .3}, "n": {"curl": (.2, .25, .3, .35), "thumb": .25}}),
    "glance73": (-0.04, -0.12, {"f": ("ang", 0.2, 0.22), "n": ("ang", -0.15, 0.3)}, {}),
    "unpin73": (0.04, -0.2, {"f": ("ang", 0.2, 0.22), "n": ("ik", (330, -560), -1)},
                {"n": {"dir": (.5, -1), "curl": (.35, .7, .95, .95), "spread": .0, "thumb": .85}}),
    "open73": (0.06, 0.16, {"f": ("ik", (215, -320), -1), "n": ("ik", (330, -350), -1)},
               {"f": {"dir": (.9, -.2), "curl": (.55, .55, .6, .62), "thumb": .5}, "n": {"dir": (.3, -1), "curl": (.3, .65, .9, .9), "thumb": .8}}),
})


def _blanket_lying(sc, top_y, roll, front_x, seed, col):
    """Одеяло в «лежачей» системе (до поворота на −90°): тело вдоль −y от таза, перед — +x. top_y — край у головы."""
    c, csh, chi = C_COCOON[0], C_COCOON[1], C_COCOON[2]
    if col == "blue":
        c, csh, chi = "#4A6FA5", "#34507D", "#6E92C9"
    elif col == "green":
        c, csh, chi = "#5C9A78", "#41735A", "#7FBF98"
    r = lib.clamp(roll)
    fx = front_x
    # контур спереди: грудь/плечо, живот, бедро (растёт на боку), колени, стопы
    front = [(fx + 10 * sc + 40 * r * sc, top_y + 30 * sc), (fx + 30 * sc + 70 * r * sc, top_y + 140 * sc), (fx - 10 * sc + 30 * r * sc, top_y + 300 * sc),
             (fx - 20 * sc + 110 * r * sc, 20 * sc), (fx - 50 * sc + 60 * r * sc, 260 * sc), (fx - 10 * sc + 40 * r * sc, 430 * sc),
             (fx - 40 * sc + 20 * r * sc, 590 * sc), (fx - 20 * sc, 680 * sc), (fx - 70 * sc, 730 * sc), (-40 * sc, 750 * sc)]
    back = [(-120 * sc, 745 * sc, 1), (-120 * sc, top_y + 10 * sc, 1)]
    pts = [(fx - 10 * sc, top_y, 1)] + front + back
    inner = blob([(-260 * sc, top_y), (fx + 200 * sc, top_y), (fx + 200 * sc, top_y + 46 * sc), (-260 * sc, top_y + 40 * sc)], chi)      # подвёрнутая кромка
    inner += lib.line([(-110 * sc, top_y + 48 * sc), (fx + 120 * sc, top_y + 50 * sc)], 3.2 * sc * 2, csh, taper=.2, wmin=.5, seed=seed + 2)
    inner += blob([(-260 * sc, top_y + 60 * sc), (-40 * sc, top_y + 60 * sc), (-40 * sc, 780 * sc), (-260 * sc, 780 * sc)], csh)
    for i, yy in enumerate((top_y + 200 * sc, 120 * sc, 380 * sc, 560 * sc)):      # складки поперёк
        if yy < top_y + 90 * sc:
            continue
        inner += lib.line([(fx - 150 * sc, yy + 20 * sc), (fx - 40 * sc, yy - 10 * sc), (fx + 60 * sc, yy + 10 * sc)], 3.0 * sc * 2, csh, taper=.4,
                          wmin=.3, seed=seed + 10 + i)
    return lib.shape(pts, c, inner, w=4.6 * sc * 2, seed=seed)


def dima_bed(x, y, k=0.5, expr="awake73", roll=0.0, sit=0.0, t=0.0, cover="chest", arm=None, col="blue", seed=0, pillow_col=None, flip=False):
    sc = k * HEIGHT["dima"]
    r, s_ = lib.clamp(roll), lib.clamp(sit)
    cov = {"chest": 0.0, "nose": 1.0}.get(cover, cover) if isinstance(cover, str) else lib.clamp(cover)
    if arm is None:
        arm = "in" if cov > .5 else "out"
    br = math.sin(t * 2 * math.pi / 4.2)                       # дыхание: грудь под одеялом
    # руки: лёжа ближняя вдоль тела поверх одеяла; на боку — ладонь к подушке у лица; сидя — на одеяле на коленях
    if s_ > .01:
        arms = {"f": ("ik", (190 * sc, -60 * sc), -1), "n": ("ik", (250 * sc, -50 * sc), -1)}
    else:
        tgt = (60 + 120 * r, -40 - 380 * r)
        arms = {"f": ("ang", 0.05, 0.1), "n": ("ik", (tgt[0] * sc, tgt[1] * sc), -1)}
    hands = {"n": {"dir": (.3 + .4 * r, -.2 - .8 * r), "curl": (.35, .4, .45, .5), "thumb": .35}, "f": {"curl": (.3, .3, .35, .4), "thumb": .3}}
    ha = -0.1 + 0.38 * r - 0.1 * s_
    fig = figure("dima", 0.0, 0.0, k, EXPR["dima"].get(expr, {}) if isinstance(expr, str) else dict(expr), lean=0.0, head_ang=ha, arms=arms, hands=hands,
                 layers=("pelvis", "body") if s_ < .5 else ("pelvis", "arm_f", "body"))
    fig_n = figure("dima", 0.0, 0.0, k, EXPR["dima"].get(expr, {}) if isinstance(expr, str) else dict(expr), lean=0.0, head_ang=ha, arms=arms,
                   hands=hands, layers=("arm_n",))
    a_body = -90.0 + 82.0 * s_
    hx, hy = fig["head"]
    # край одеяла: грудь (−330) … нос (голова + 40), сидя — пояс (−40)
    top_lying = (-330 * sc) * (1 - cov) + (hy + 40 * sc) * cov
    top_y = top_lying * (1 - s_) + (-150 * sc) * s_
    front_x = 125 * sc + 6 * sc * br
    blank = _blanket_lying(sc, top_y, r, front_x, 73900 + seed, col)
    # подушка: за затылком (в лежачей системе — выше и позади головы)
    pc = pillow_col
    pil_local = (hx - 120 * sc, hy - 40 * sc)
    c, sn = math.cos(math.radians(-90)), math.sin(math.radians(-90))
    pw = (x + pil_local[0] * c - pil_local[1] * sn, y + pil_local[0] * sn + pil_local[1] * c)
    import props as _P
    pillow_svg = _P.pillow(pw[0] + 30 * sc, pw[1] + 150 * sc, k * 2.6, 0, col=pc, seed=seed + 3)
    tb = f'translate({x:.2f} {y:.2f}) rotate({a_body:.2f})'
    tl_ = f'translate({x:.2f} {y:.2f}) rotate(-90)'
    out = [pillow_svg, f'<g transform="{tb}">{fig["svg"]}</g>']
    show_arm = arm == "out" and (cov < .5 or r > .3 or s_ > .1)
    out.append(f'<g transform="{tl_}">{blank}</g>')
    if show_arm:
        out.append(f'<g transform="{tb}">{fig_n["svg"]}</g>')

    def W_(p, a):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        q = (x + p[0] * ca - p[1] * sa, y + p[0] * sa + p[1] * ca)
        return (2 * x - q[0], q[1]) if flip else q
    svg = "".join(out)
    if flip:      # голова на подушке СПРАВА, ноги влево
        svg = f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{svg}</g>'
        pw = (2 * x - pw[0], pw[1])
    return dict(svg=svg, head=W_((hx, hy), a_body), wrist={kk: W_(v, a_body) for kk, v in fig["wrist"].items()}, pillow=pw, scale=sc)


def cat_judge_shadow(x, y, k, st=None, t=0.0, col="#8FA3C8", w=5.0, op=0.85):
    """Тень кота-судьи на потолке/стене ЛИНИЕЙ: контур силуэта той же позы (морфология SVG), без заливки. w — толщина линии в px экрана·."""
    import cat
    fid = lib.uid("csh")
    r = max(1.0, w / max(k, 1e-3) / 2)
    lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%"><feMorphology in="SourceAlpha" operator="dilate" '
                    f'radius="{r:.2f}" result="d"/><feComposite in="d" in2="SourceAlpha" operator="out" result="ring"/>'
                    f'<feFlood flood-color="{col}" flood-opacity="{op:.2f}"/><feComposite in2="ring" operator="in"/></filter>')
    inner = cat.draw(x, y, k, dict(st or {}), t)
    return f'<g filter="url(#{fid})">{inner}</g>'


CAT_ST.update({
    "judge": {"cold": 1.0, "look": (0, 0), "tilt": 0.0},
    "judge_tap": {"cold": 1.0, "paw": .7, "paw_dx": 40, "look": (.2, .5)},
    "challenge": {"cold": .6, "smug": .6, "tilt": -9, "look": (0, 0)},
    "warm73": {"blink": .35, "smile": 1.0, "look": (0, .1), "flame_e": 1.5},
    "nuzzle": {"blink": 1.0, "smile": 1.0, "tilt": 18, "rot": 8, "flame_e": 1.6},
    "sit_wrap": {"blink": .3, "smile": 1.0, "tail": -6, "look": (0, 0)},
})


# ═════════════════════════════ РИЛС 74 «ПРЕКРАТИ НЫТЬ» (автор — группа B) ═════════════════════════════
# Дима (горчичное худи) — dima(x, y, scale, expr, pose, **ноги); сидит за столом — **sit_kw(x, y, scale); смотрит вправо (flip — влево).
# Мимика EXPR["dima"]: guilty74 (смотрит вверх виновато), shrink74 (вжимает голову, взгляд вверх-исподлобья), screen74 (лицо в свете
#   экрана, смотрит в телефон, усталый), rub74 (трёт щетину: глаза почти закрыты), straight74 (выпрямился, усталый взгляд вперёд),
#   halfsmile74 (усталая полуулыбка прямо в камеру), look_cat74 (смотрит вниз-вправо на кота), jar74 (лицо сморщено от усилия, зажмурен),
#   slip74 (руки соскользнули: брови домиком, рот приоткрыт), chew74 (жуёт кусочек, глаза в телефон), type_up74 (печатает: брови вверх,
#   улыбка краешком рта).
# Позы POSE (цели рук — в долях масштаба от таза; Дима смотрит вправо):
#   phone_chest74 — телефон двумя руками у груди (центр телефона ≈ (255, −290)·sc, экран к Диме) — рисовать dima_phone(...);
#   phone_belly74 — прячет телефон к животу (≈ (232, −230)·sc); place74 — ближняя рука кладёт телефон экраном вниз на стол (≈ (345, −205)·sc,
#   кисть ладонью вниз), дальняя на столе; desk74 — обе руки спокойно на столе; rub74 — ближняя ладонь трёт щетину (≈ (165, −352)·sc — пальцы на щетине;
#   сцена водит цель вверх-вниз), shrug74 — дальняя рука на столе, ближняя кисть чуть приподнята ладонью вверх (пожимает плечом:
#   + shrug=0.3); jar74 — дальняя кисть держит банку за бок (≈ (300, −235)·sc), ближняя обхватывает крышку (≈ (318, −405)·sc) — точные цели
#   даёт сцена из props.jar_lid_c; eat74 — ближняя кисть у рта с кусочком (≈ (170, −365)·sc, кусочек — в hand_pos(fig, "n", 70)), дальняя держит телефон у груди.
# dima_phone(x, y, scale, expr, pose="phone_chest74", phone_k=None, phone_rot=-12, thumb=0.0, **kw) — Дима с телефоном в обеих руках:
#   тело и дальняя рука → телефон (спинкой к зрителю, экран к Диме) → ближняя рука поверх, пальцы огибают край; thumb 0…1 — большой
#   палец ближней руки ходит по экрану (печатает). Возвращает dict фигуры + phone=(x, y) центр телефона.
# dima_over_shoulder(x, y, k, phone_c, phone_k, phone_rot, phone_svg, thumb_u, press, jit, t, tilt, shade) — ВИД ЧЕРЕЗ ПЛЕЧО (s07, s14):
#   (x, y) — основание шеи Димы (голова и плечо худи СО СПИНЫ, крупно на переднем плане, обычно у левого нижнего края кадра), k — масштаб
#   (голова ≈ 300·k); телефон держат ОБЕ руки: рукава худи поднимаются снизу кадра к бокам телефона, ладони за корпусом, пальцы огибают
#   края, большие пальцы на экране. phone_c — центр телефона, phone_svg — сам экран (props.phone_draft(phone_c…, k=phone_k, rot=phone_rot));
#   thumb_u 0…1 — большой палец правой руки идёт от края экрана к кнопке «отправить» (props.phone_draft_btn), press 0…1 — нажимает,
#   jit — дрожь пальца в px; tilt — наклон головы; shade 0…1 — спина и затылок в тени (свет только от экрана спереди).
#   Возвращает dict(svg, thumb_tip=(x, y), head=(x, y)).
# Кот (cat.py, новые ключи st): cross 0…1 — передние лапы скрещены на груди (правая сверху), cross_tap 0…1 — верхняя лапа из скрещения
#   стукает когтем по подлокотнику справа; roll 0…1 — закатывает глаза. CAT_ST: king74 (надменный король: лапы скрещены, веки наполовину,
#   нос задран, прямой рот), roll74 (закатил глаза; лапа «вниз» — cat_forearm), warm74 (тёплый после поворота),
#   happy74 (довольный, жмурится, огонёк ярче — звёздочки props.sparkles кладёт сцена), no74 (мотает головой — turn/tilt сцена качает
#   по ±), reach74 (лапа к зрителю), nuzzle74 (прижимается боком: наклон, глаза прикрыты).
#   Лап всегда ЧЕТЫРЕ: тянется/стукает ТА ЖЕ передняя лапа, вторая на опоре.
# cat_back74(x, y, k, t, turn) — кот СО СПИНЫ сверху (s02: камера из-за плеча кота): затылок с ушами (загнутое — справа от
#   зрителя: у кота это то же правое ухо, что слева на анфасе), холка и плечо уходят за край кадра; (x, y) — центр затылка, k — масштаб
#   (затылок ≈ 190·k). Морды не видно. Лапа «указывает вниз» — people.cat_forearm(плечо → цель) ДО cat_back74.
EXPR["dima"].update({
    "guilty74": {"brows": "worry", "mouth": "flat", "lid": .9, "look": (.35, -.75), "blush": .35},
    "shrink74": {"brows": "worry", "mouth": "frown", "lid": .7, "look": (.4, -.85), "blush": .4},
    "screen74": {"brows": "tired", "mouth": "flat", "lid": .55, "look": (.45, .55)},
    "rub74": {"brows": "tired", "mouth": "tired", "lid": .2, "look": (.2, .3)},
    "straight74": {"brows": "calm", "mouth": "flat", "lid": .62, "look": (.3, 0)},
    "halfsmile74": {"brows": "tired", "mouth": "side", "lid": .58, "look": (-.4, .02)},
    "look_cat74": {"brows": "calm", "mouth": "flat", "lid": .8, "look": (.65, .7)},
    "jar74": {"brows": "pinch", "mouth": "pressed", "lid": .3, "squeeze": 1.0, "look": (.5, .5)},
    "slip74": {"brows": "worry", "mouth": "o", "open": .22, "lid": .85, "look": (.6, .55)},
    "chew74": {"brows": "calm", "mouth": "flat", "lid": .62, "look": (.45, .55)},
    "type_up74": {"brows": "up", "mouth": "side", "lid": .78, "look": (.5, .5), "bags": False},
})

_PH_HOLD_N = {"dir": (-.55, -.85), "curl": (.62, .66, .7, .74), "thumb": .55}
_PH_HOLD_F = {"dir": (.85, -.4), "curl": (.6, .62, .66, .7), "thumb": .5}
POSE.update({
    "phone_chest74": (0.06, 0.08, {"f": ("ik", (205, -262), -1), "n": ("ik", (288, -256), -1)}, {"f": dict(_PH_HOLD_F), "n": dict(_PH_HOLD_N)}),
    "phone_belly74": (0.1, 0.16, {"f": ("ik", (190, -232), -1), "n": ("ik", (268, -226), -1)}, {"f": dict(_PH_HOLD_F), "n": dict(_PH_HOLD_N)}),
    "place74": (0.14, 0.14, {"f": ("ik", (215, -205), -1), "n": ("ik", (345, -205), -1)},
                {"f": {"dir": (1, .3), "curl": (.35, .4, .45, .5), "thumb": .35}, "n": {"dir": (1, .25), "curl": (.15, .2, .25, .3), "spread": .1, "thumb": .3}}),
    "desk74": (0.08, 0.04, {"f": ("ik", (205, -200), -1), "n": ("ik", (275, -198), -1)},
               {"f": {"dir": (1, .3), "curl": (.4, .42, .46, .5), "thumb": .4}, "n": {"dir": (1, .3), "curl": (.35, .38, .42, .46), "thumb": .35}}),
    "rub74": (0.04, 0.1, {"f": ("ik", (215, -200), -1), "n": ("ik", (165, -352), -1)},
              {"f": {"dir": (1, .3), "curl": (.4, .42, .46, .5), "thumb": .4}, "n": {"dir": (.3, -1), "curl": (.3, .35, .4, .45), "spread": .08, "thumb": .45}}),
    "shrug74": (-0.02, -0.04, {"f": ("ik", (210, -200), -1), "n": ("ik", (300, -255), -1)},
                {"f": {"dir": (1, .3), "curl": (.4, .42, .46, .5), "thumb": .4}, "n": {"dir": (1, -.35), "flip": -1, "spread": .3, "curl": (.1, .15, .2, .25), "thumb": .2}}),
    "jar74": (0.12, 0.12, {"f": ("ik", (300, -235), -1), "n": ("ik", (318, -405), -1)},
              {"f": {"dir": (.3, -1), "curl": (.7, .72, .75, .78), "thumb": .6}, "n": {"dir": (1, .15), "curl": (.72, .75, .78, .8), "thumb": .65}}),
    "eat74": (0.04, 0.08, {"f": ("ik", (240, -300), -1), "n": ("ik", (170, -365), -1)},
              {"f": dict(_PH_HOLD_F), "n": {"dir": (.3, -1), "curl": (.55, .6, .7, .75), "thumb": .7}}),
})


def dima_phone(x, y, scale, expr="screen74", pose="phone_chest74", phone_k=None, phone_rot=-12.0, thumb=0.0, t=0.0, **kw):
    """Дима держит телефон ДВУМЯ руками (экран к нему, нам — спинка). Телефон — между кистями, чуть выше и правее ближнего запястья."""
    lay_body = kw.pop("layers_body", ("legs", "pelvis", "arm_f", "body"))
    base = dima(x, y, scale, expr, pose, layers=lay_body, **kw)
    arm = dima(x, y, scale, expr, pose, layers=("arm_n",), **kw)
    sc = base["scale"]
    wn, wf = np.array(base["wrist"]["n"]), np.array(base["wrist"]["f"])
    c = (wn + wf) / 2 + np.array([12, -40]) * sc
    pk = phone_k if phone_k is not None else 1.45 * sc
    ph = mobilnik(float(c[0]), float(c[1]), pk, phone_rot, seed=952)
    th = ""
    if thumb > .01:      # большой палец ближней руки над краем экрана: короткий штрих-фаланга, ходит вверх-вниз
        ph_top = (float(c[0]) - 6 * sc, float(c[1]) - 40 * sc - 14 * sc * math.sin(t * 14) * thumb)
        th = shape(lib.T(lib.rrect(-9, -26, 9, 18, 8), ph_top[0], ph_top[1], sc * 1.4, -25), C.get("SKIN", "#ecc4a2"), "", w=3.2, seed=953)
    base["svg"] = base["svg"] + ph + arm["svg"] + th
    base["wrist"] = arm["wrist"]
    base["phone"] = (float(c[0]), float(c[1]))
    return base


def _shade_filter(u):
    fid = "shd74_%d" % int(round(u * 100))
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        a = 1 - .55 * u
        b = .02 * u
        lib.DEFS.append(f'<filter id="{fid}"><feComponentTransfer><feFuncR type="linear" slope="{a:.3f}" intercept="{b:.3f}"/>'
                        f'<feFuncG type="linear" slope="{a:.3f}" intercept="{b:.3f}"/><feFuncB type="linear" slope="{a * 1.05:.3f}" intercept="{b * 2:.3f}"/>'
                        f'</feComponentTransfer></filter>')
    return fid


def _thumb(base, tip, w, sd, skin, skin_sh):
    """Большой палец сверху на экране: фаланга от основания к кончику, ноготь."""
    bx, by = base
    tx, ty = tip
    L = math.hypot(tx - bx, ty - by) + 1e-6
    ux, uy = (tx - bx) / L, (ty - by) / L
    nx, ny = -uy, ux
    pts = lib.band([(bx, by), ((bx + tx) / 2 + nx * w * .1, (by + ty) / 2 + ny * w * .1), (tx, ty)], w, w * .82, step=3)
    o = shape(pts, skin, blob([(bx + nx * w * .5, by + ny * w * .5), (tx + nx * w * .4, ty + ny * w * .4), (tx, ty), (bx, by)], skin_sh, .6), w=4.2, seed=sd)
    nl = ellipse_pts(tx - ux * w * .28, ty - uy * w * .28, w * .3, w * .22, 10, rot=math.degrees(math.atan2(uy, ux)))
    o += shape(nl, "#f1cdbd", "", w=2.4, seed=sd + 1)
    return o


def dima_over_shoulder(x, y, k, phone_c, phone_k=1.0, phone_rot=0.0, phone_svg="", thumb_u=0.0, press=0.0, jit=0.0, t=0.0, tilt=0.0, shade=0.0,
                       who="dima"):
    global C
    C = PAL[who]
    pc = np.array(phone_c, float)
    a = math.radians(phone_rot)
    ca, sa = math.cos(a), math.sin(a)

    def P(px, py):          # точка корпуса телефона (локально, центр 0, корпус 300×600) → мир
        return (pc[0] + (px * ca - py * sa) * phone_k, pc[1] + (px * sa + py * ca) * phone_k)
    skin, skin_sh = C["SKIN"], C["SKIN_SH"]
    hk = phone_k * 1.55           # кисть ≈ 1/3 лица Димы: ладонь под стать телефону
    o = []
    back = dima_back(x, y, k, tilt=tilt, look_up=0.0, shrug=.1, t=t, who=who)
    shl = back["shoulders"]
    # рукава: от плеч (под спиной) вперёд-вверх к запястьям у нижних углов корпуса
    for side in (-1, 1):
        wr = P(side * 150, 210)
        root = (shl[0 if side < 0 else 1][0] - side * 60 * k, shl[0 if side < 0 else 1][1] + 40 * k)
        el = ((root[0] + wr[0]) / 2 + side * 90 * phone_k, (root[1] + wr[1]) / 2 + 60 * phone_k)
        sl = lib.band([root, el, (wr[0] + side * 26 * phone_k, wr[1] + 70 * phone_k)], 120 * phone_k, 96 * phone_k, step=5, cap=False)
        sh = blob([(root[0] + side * 60 * phone_k, root[1]), (el[0] + side * 46 * phone_k, el[1]), (wr[0] + side * 40 * phone_k, wr[1] + 70 * phone_k),
                   (wr[0] + side * 10 * phone_k, wr[1] + 70 * phone_k), (el[0], el[1]), (root[0], root[1])], C["TOP_SH"], .85)
        cuff = line([(wr[0] + side * 26 * phone_k - 50 * phone_k, wr[1] + 84 * phone_k), (wr[0] + side * 26 * phone_k + 50 * phone_k, wr[1] + 64 * phone_k)],
                    4, C["FOLD"], taper=.2, wmin=.5, seed=7420 + side)
        o.append(shape(sl, C["TOP"], sh + cuff, w=5.0, seed=7410 + side))
        # ладонь за корпусом: тыльная сторона кисти у бока телефона, пальцы уходят за корпус
        palm = lib.T([(-40, -10), (-30, -70), (10, -96), (52, -80), (64, -20), (46, 40), (0, 56), (-34, 40)], wr[0] - side * 4 * phone_k,
                     wr[1] - 16 * phone_k, hk * .62, -side * 12 + phone_rot)
        if side < 0:
            palm = [(2 * (wr[0] - 4 * phone_k * side) - p[0], p[1]) for p in palm]
        o.append(shape(palm, skin, blob([(p[0] + side * 10 * phone_k, p[1] + 8 * phone_k) for p in palm[:5]], skin_sh, .55), w=4.4, seed=7430 + side))
    o.append(phone_svg)
    # пальцы, огибающие края корпуса (кончики на торце спереди): по три с каждой стороны
    for side in (-1, 1):
        for j, py in enumerate((40, 100, 160)):
            ex = P(side * 150, py)
            tip = (ex[0] - side * 16 * phone_k * ca, ex[1] - side * 16 * phone_k * sa)
            fp = ellipse_pts((ex[0] + tip[0]) / 2 + side * 4 * phone_k, (ex[1] + tip[1]) / 2, 22 * phone_k, 26 * phone_k, 10)
            o.append(shape(fp, skin, blob(ellipse_pts((ex[0] + tip[0]) / 2 + side * 12 * phone_k, (ex[1] + tip[1]) / 2 + 6 * phone_k, 12 * phone_k,
                                                     18 * phone_k, 8), skin_sh, .6), w=3.4, seed=7440 + j + 10 * side))
    # большие пальцы на экране: левый лежит у нижнего левого края, правый идёт к кнопке
    lb = P(-150, 230)
    o.append(_thumb(lb, P(-92, 120), 44 * phone_k, 7450, skin, skin_sh))
    rb = P(150, 250)
    rest = P(70, 70)
    btn = P(82, 196)
    u = lib.ease_io(lib.clamp(thumb_u))
    tip = (rest[0] + (btn[0] - rest[0]) * u + jit, rest[1] + (btn[1] - rest[1]) * u - (1 - press) * 26 * phone_k * u + jit * .6)
    o.append(_thumb(rb, tip, 46 * phone_k * (1 + .06 * press), 7460, skin, skin_sh))
    # голова и плечо со спины на переднем плане
    bsvg = back["svg"]
    if shade > .02:
        bsvg = f'<g filter="url(#{_shade_filter(round(shade, 2))})">{bsvg}</g>'
    o.append(bsvg)
    return dict(svg="".join(o), thumb_tip=tip, head=back["head"])


CAT_ST.update({
    "king74": {"cross": 1.0, "smug": 1.0, "look": (0, .35), "tilt": -4, "cold": .55, "ear": -4},
    "roll74": {"cross": 1.0, "smug": .8, "roll": 1.0, "tilt": 8, "cold": .4},
    "warm74": {"blink": .3, "smile": 1.0, "look": (0, .1), "flame_e": 1.4},
    "happy74": {"blink": .75, "smile": 1.0, "perk": 1.0, "look": (0, 0), "flame_e": 1.8},
    "no74": {"perk": .6, "look": (0, 0), "smile": 0.0},
    "reach74": {"paw": 1.0, "paw_dx": 30, "look": (0, 0), "smile": 1.0, "perk": .5},
    "nuzzle74": {"blink": .85, "smile": 1.0, "tilt": 14, "rot": 6, "flame_e": 1.5},
})


def cat_back74(x, y, k=1.0, t=0.0, turn=0.0):
    import cat
    from ink import fur as _fur
    o = []
    # холка и плечо: от затылка вверх-влево за край (тело кота за камерой)
    bd = [(-360, -420), (-380, -60), (-300, 70), (-170, 120), (-40, 96), (70, 40), (130, -90), (120, -420)]
    inner = blob([(40, 60), (140, -90), (130, -420), (60, -420), (80, -100)], cat.CAT_SH, .85)
    inner += blob([(-300, 20), (-180, 80), (-80, 70), (-200, -20)], cat.CAT_FUR, .55)
    for i, (a, b) in enumerate((((-260, 30), (-250, 60)), ((-180, 60), (-176, 92)), ((-100, 60), (-96, 90)))):
        inner += line([a, b], 2.4, cat.CAT_EDGE, seed=7480 + i, op=.8)
    o.append(shape(_fur(bd, 7, 7, seed=7481), cat.CAT, inner, w=5.2, seed=7482))
    dx = 18 * turn
    # уши: слева от зрителя — стоячее (затылок, без розового), справа — загнутое кончиком вперёд
    le = [(-92 + dx, -40), (-70 + dx, -150, 1), (-20 + dx, -70)]
    o.append(shape(le + [(-30 + dx, -40)], cat.CAT, blob([(-72 + dx, -140), (-40 + dx, -80), (-60 + dx, -60)], cat.CAT_SH, .7), w=5.0, seed=7483))
    re = [(20 + dx, -70), (44 + dx, -120), (70 + dx, -128, 1), (88 + dx, -104), (92 + dx, -48)]
    o.append(shape(re + [(40 + dx, -40)], cat.CAT, blob([(60 + dx, -126), (88 + dx, -104), (90 + dx, -60), (70 + dx, -80)], cat.CAT_SH, .7) +
                   line([(48 + dx, -110), (72 + dx, -112), (86 + dx, -98)], 2.4, cat.CAT_EDGE, seed=7485, op=.85), w=5.0, seed=7484))
    # затылок
    hd = [(-110, 0), (-96, -60), (-40, -92), (40, -92), (96, -60), (110, 0), (92, 60), (0, 84), (-92, 60)]
    hin = blob([(30, -92), (112, -20), (96, 70), (40, 84), (70, 0)], cat.CAT_SH, .8)
    hin += blob([(-70, -70), (-10, -86), (-30, -50)], cat.CAT_FUR, .6)
    for i, (a, b) in enumerate((((-40, -60), (-34, -36)), ((0, -70), (4, -44)), ((40, -60), (36, -34)))):
        hin += line([a, b], 2.2, cat.CAT_EDGE, seed=7490 + i, op=.8)
    o.append(shape(_fur([(p[0] + dx * .4, p[1]) for p in hd], 6, 6, seed=7491), cat.CAT, hin, w=5.2, seed=7492))
    # усы торчат из-за щёк
    for sx in (-1, 1):
        for j in range(2):
            wv = 3 * math.sin(t * 2.3 + j + sx)
            o.append(line([(sx * 100 + dx, 30 + 12 * j), (sx * 150 + dx, 26 + 14 * j + wv), (sx * 190 + dx, 30 + 18 * j + wv)], 1.6, "#cfcbe0", seed=7495 + j + 3 * sx,
                          op=.9))
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f})">{"".join(o)}</g>'


# ═════════════════════════════ РИЛС 78 «ЛЕНТА, ТЫ СЛАБАК» (автор — группа B) ═════════════════════════════
# Все люди рилса — отсюда, кот — только common/cat.py (cat_svg / cat_walk / cat_jump / cat_curl / cat_forearm). Дима смотрит вправо.
# dima_reach78(x, y, k, tip, pull, t, expr, full, clasp, ...) — ХУК s01 и ПЕТЛЯ s18 (один ракурс): Дима по пояс (full=False, (x, y) — таз,
#   голова ≈ 300·k) или во весь рост (full=True, стоит, упирается пяткой — s02). Ближняя (правая) рука вытянута по диагонали к точке
#   tip (мир) — указательный палец вытянут, кончик пальца ровно в tip (возвращается "finger"); pull 0…1 — насколько его тянет туда:
#   0 — рука согнута ближе к телу, 1 — плечо вперёд, рука в струну; clasp=True — дальняя рука вцепилась в своё ближнее запястье и тянет
#   на себя (хук: «отпусти!»), False — дальняя спокойно на колене/подлокотнике (петля). hair_jit, strings_jit — дёрганье волос и шнурков.
#   Возвращает dict(svg, head, finger, finger_dir, wrist, elbow, scale). Мимика EXPR["dima"]: letgo78 («отпусти!»: зубы стиснуты,
#   брови сведены, глаза прищурены), strain78 (тянет изо всех сил, зажмурен), fall78 (летит в подушку: глаза зажмурены, рот «о»),
#   shout78 (кричит, зажмурен, рот открыт), cower78 (вжимает голову, брови домиком), turn78 (повернулся к экрану, сдался: усталый
#   взгляд вбок-вниз), lit78 (лицо в свете экрана, пусто смотрит), nod78 (кивает на нитях: веки опущены, рот приоткрыт),
#   calm_pet78 (гладит кота: мягкая улыбка, взгляд вниз-вправо), stretch78 (потягивается: глаза закрыты, улыбка), read78 (читает),
#   carry78 (несёт телефон: спокойно, взгляд вперёд), relief78 (выдох облегчения).
# dima_faceplant78(x, y, k, u, t, tip) — s02: u 0…1 — срывается и летит лицом вперёд (вправо) в подушку: фигура падает вокруг стоп,
#   руки вперёд, ноги отрываются; (x, y) — таз в начале (стоит). Возвращает dict(svg, head, finger, angle).
# dima_carry78(x, y, k, phase, t, expr) — s16: идёт (phase — фаза шага; x двигает вызывающий), ближняя рука вытянута вперёд, телефон
#   экраном вниз лежит на ладони ("palm" — точка, куда класть телефон, "palm_rot"); arm_u 0…1 — рука вытянута (1) … опущена (0).
# dima_door78(x, y, k, u, t) — s16: стоит, ближняя рука тянется вперёд к ручке двери в точке knob (мир); u — доля пути руки.
# dima_chair78(x, y, k, u_stretch, u_book, t, expr) — s17: сидит в кресле (кресло рисует room), (x, y) — таз; потягивается (руки вверх,
#   u_stretch) и берёт книгу с подлокотника (u_book; ближняя кисть идёт к точке "book_at"; книгу рисует вызывающий в "book_hand").
# dima_lap78(x, y, k, tip, t, stroke) — s18: = dima_reach78(clasp=False, мимика calm_pet78), палец гладит: stroke 0…1 — фаза поглаживания.
# reflection78(svg, col, op) — отражение в ночном окне (s03): только тёмные линии туши рисунка, цвет стекла col, без заливки.
# finger_walker78(base, tip, k, phase, t, lift) — s04: рука из-под одеяла (рукав худи от base) и кисть, у которой указательный и средний
#   пальцы «шагают» как две ножки к точке tip; phase — фаза шага (1 = два шага). Средний план: рукав не толще предплечья.
# inventor(x, y, k, pose, t, expr, u) — изобретатель (без имени): седые кудри, очки подняты на лоб, голубая рубашка с закатанными рукавами,
#   фартук. pose: "sew" (сшивает карточки двумя руками перед грудью), "raise" (гордо поднимает конец ленты ближней рукой, "hold"),
#   "slap" (хлопает ладонью по рулону — "palm"), "sit" (сидит на куче ленты, руки на коленях), "head" (хватается за голову обеими
#   руками), "pull" (тянет ленту обеими руками на себя — "hold"). u — переход из предыдущей позы (pose=(a, b), u). Сидит — full=False
#   (по пояс) или feet="stand"/"sit". Мимика EXPR["inventor"]: proud, busy, slap, look, turn, regret, tug.
EXPR["dima"].update({
    "letgo78": {"brows": "pinch", "mouth": "grin", "open": .15, "lid": .55, "look": (.6, .55), "bags": False, "hair": 8},
    "strain78": {"brows": "pinch", "mouth": "pressed", "lid": .3, "squeeze": 1.0, "look": (.6, .5), "bags": False, "hair": 10},
    "fall78": {"brows": "up", "mouth": "o", "open": .9, "squeeze": 1.0, "bags": False, "hair": 14},
    "shout78": {"brows": "pinch", "mouth": "o", "open": 1.0, "squeeze": 1.0, "look": (.3, -.5)},
    "cower78": {"brows": "sad", "mouth": "frown", "lid": .55, "look": (.6, -.6)},
    "turn78": {"brows": "tired", "mouth": "flat", "lid": .5, "look": (.6, .35)},
    "lit78": {"brows": "tired", "mouth": "flat", "lid": .62, "look": (.5, .45)},
    "nod78": {"brows": "tired", "mouth": "o", "open": .12, "lid": .3, "look": (.4, .6)},
    "calm_pet78": {"brows": "calm", "mouth": "smile", "smile": .8, "lid": .5, "look": (.55, .6), "bags": False},
    "stretch78": {"brows": "calm", "mouth": "smile", "smile": 1.0, "shut": 1.0, "bags": False},
    "read78": {"brows": "calm", "mouth": "smile", "smile": .4, "lid": .55, "look": (.6, .5), "bags": False},
    "carry78": {"brows": "calm", "mouth": "flat", "lid": .7, "look": (.6, .2), "bags": False},
    "relief78": {"brows": "calm", "mouth": "o", "open": .25, "lid": .35, "look": (.3, .2), "bags": False},
})


def _reach_arm(x, y, sc, tip, pull, hand_dir=None):
    """Цель запястья, чтобы кончик вытянутого указательного пальца лёг в tip (мир). Возвращает (wrist, d)."""
    sh = np.array([x + 10 * sc, y - 400 * sc])          # плечо ~ (10, −400)·sc от таза
    tp = np.array(tip, float)
    v = tp - sh
    L = np.linalg.norm(v) + 1e-6
    d = np.array(hand_dir, float) if hand_dir is not None else v / L
    d = d / (np.linalg.norm(d) + 1e-6)
    n = np.array([-d[1], d[0]])
    wr = tp - d * 138 * sc + n * 25 * sc                 # кончик указательного: запястье + 138·d − 25·n (hand.FING, k=1)
    reach = UPPER + FORE - 6
    wv = wr - sh
    wl = np.linalg.norm(wv)
    if wl > reach * sc:                                  # дальше руки не дотянуться: запястье на пределе
        wr = sh + wv / wl * reach * sc
    return wr, d


def dima_reach78(x, y, k, tip, pull=1.0, t=0.0, expr="letgo78", full=False, clasp=True, hair_jit=0.0, strings_jit=0.0, lean=None,
                 hand_dir=None, heel=0.0, head_add=0.0):
    sc = k * HEIGHT["dima"]
    pl = lib.clamp(pull)
    ln = (-0.10 + 0.16 * pl) if lean is None else lean   # тянет на себя — корпус назад; рука в струну — плечо вперёд
    wr, d = _reach_arm(x, y, sc, tip, pl, hand_dir)
    ex = dict(EXPR["dima"].get(expr, {})) if isinstance(expr, str) else dict(expr)
    if hair_jit:
        ex["hair"] = ex.get("hair", 0) + hair_jit
    arms = {"n": ("ik", (float(wr[0]), float(wr[1])), -1)}
    hands = {"n": {"dir": (float(d[0]), float(d[1])), "curl": (0.0, .82, .88, .9), "spread": .05, "thumb": .75, "bend": .04}}
    if clasp:       # дальняя кисть обхватывает ближнее предплечье у запястья и тянет на себя
        tmp = figure("dima", x, y, k, ex, lean=ln, arms={"n": arms["n"], "f": ("ang", .18, .18)}, layers=("arm_n",))
        el = np.array(tmp["elbow"]["n"])
        gp = el + (wr - el) * .62
        arms["f"] = ("ik", (float(gp[0]), float(gp[1])), -1)
        hands["f"] = {"dir": (float(d[0] * .3 + .2), float(d[1] * .3 - 1)), "curl": (.7, .72, .75, .78), "thumb": .6}
    else:           # дальняя рука спокойно опущена к колену
        arms["f"] = ("ik", (x + 170 * sc, y - 70 * sc), -1)
        hands["f"] = {"dir": (1, .4), "curl": (.35, .4, .45, .5), "thumb": .35}
    kw = {}
    if full:
        st = stand_kw(x, y, k, spread=120)
        # упор: передняя (ближняя) нога вперёд пяткой в пол, задняя согнута
        fa, ff = st["feet"]["n"], st["feet"]["f"]
        kw["feet"] = {"n": ((fa[0][0] + 90 * sc * heel, fa[0][1]), -.45 * heel), "f": ((ff[0][0] - 40 * sc * heel, ff[0][1]), .15 * heel)}
    strings = (6 * strings_jit, 4 * abs(strings_jit))
    fig = figure("dima", x, y, k, ex, lean=ln, head_ang=0.06 - 0.1 * pl + head_add, arms=arms, hands=hands,
                 layers=("legs", "pelvis", "arm_f", "body", "arm_n") if full else ("pelvis", "body", "arm_n", "arm_f") if clasp else
                 ("pelvis", "arm_f", "body", "arm_n"), extra={"strings": strings}, **kw)
    wn = np.array(fig["wrist"]["n"])
    dn = np.array(d)
    nn = np.array([-dn[1], dn[0]])
    fig["finger"] = tuple(map(float, wn + dn * 138 * sc - nn * 25 * sc))
    fig["finger_dir"] = (float(dn[0]), float(dn[1]))
    return fig


def dima_faceplant78(x, y, k, u, t=0.0, tip=None):
    """Срыв и падение лицом вперёд вокруг стоп: 0–.25 рывок назад (ещё держит), .25–1 летит вперёд (ease_in), в конце шлепок."""
    sc = k * HEIGHT["dima"]
    u = lib.clamp(u)
    foot = (x + 20 * sc, y + (LEG_LEN - 12) * sc)
    if u < .25:
        a = -10 * math.sin(u / .25 * math.pi / 2)
    else:
        e = lib.ease_in((u - .25) / .75, 2.2)
        a = -10 + 92 * e
    ex = "strain78" if u < .25 else "fall78"
    tp = tip if tip is not None else (x + 520 * sc, y - 180 * sc)
    if u >= .25:        # руки вперёд-вверх, ладони раскрыты — летит
        ln = .1 + .2 * lib.clamp((u - .25) / .5)
        arms = {"n": ("ang", 2.25 - .35 * u, -.2), "f": ("ang", 2.05 - .35 * u, -.3)}
        hands = {"n": {"spread": .4, "curl": (.05, .05, .1, .15), "thumb": .1}, "f": {"spread": .35, "curl": (.1, .1, .15, .2), "thumb": .2}}
        st = stand_kw(x, y, k, spread=100)
        lift = lib.clamp((u - .55) / .45)
        fa, ff = st["feet"]["n"], st["feet"]["f"]
        feet = {"n": ((fa[0][0] - 120 * sc * lift, fa[0][1] - 160 * sc * lift), .6 * lift), "f": ((ff[0][0] - 200 * sc * lift, ff[0][1] - 90 * sc * lift), .4 * lift)}
        fig = figure("dima", x, y, k, EXPR["dima"][ex], lean=ln, head_ang=.2, arms=arms, hands=hands, feet=feet)
        fig["finger"] = None
    else:
        fig = dima_reach78(x, y, k, tp, 1.0, t, ex, full=True, clasp=True, heel=1.0, hair_jit=6 * math.sin(t * 30))
    g = f'<g transform="rotate({a:.2f} {foot[0]:.2f} {foot[1]:.2f})">{fig["svg"]}</g>'
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))

    def R(p):
        dx, dy = p[0] - foot[0], p[1] - foot[1]
        return (foot[0] + dx * ca - dy * sa, foot[1] + dx * sa + dy * ca)
    return dict(svg=g, head=R(fig["head"]), finger=R(fig["finger"]) if fig.get("finger") else None, angle=a, scale=sc)


def dima_carry78(x, y, k, phase=0.0, t=0.0, expr="carry78", arm_u=1.0, walk=True):
    sc = k * HEIGHT["dima"]
    w = walk_kw(x, y, k, phase) if walk else dict(stand_kw(x, y, k), hip=(x, y))
    hx, hy = w["hip"]
    au = lib.clamp(arm_u)
    tgt = (hx + (180 + 280 * au) * sc, hy - (150 + 170 * au) * sc)
    swing = .25 * math.sin(2 * math.pi * phase) if walk else 0.0
    arms = {"n": ("ik", tgt, -1), "f": ("ang", .18 + swing, .2)}
    hands = {"n": {"dir": (1, .05), "flip": -1, "curl": (.15, .18, .22, .28), "spread": .1, "thumb": .2}, "f": {"curl": (.4, .45, .5, .55), "thumb": .4}}
    fig = figure("dima", hx, hy, k, EXPR["dima"].get(expr, expr) if isinstance(expr, str) else expr, lean=.04, head_ang=.04, arms=arms, hands=hands,
                 feet=w["feet"])
    wn = np.array(fig["wrist"]["n"])
    fig["palm"] = (float(wn[0] + 60 * sc), float(wn[1] - 26 * sc))
    fig["palm_rot"] = 0.0
    return fig


def dima_door78(x, y, k, knob, u=1.0, t=0.0, expr="carry78"):
    sc = k * HEIGHT["dima"]
    st = stand_kw(x, y, k)
    u = lib.clamp(u)
    rest = np.array([x + 120 * sc, y - 40 * sc])
    tg = rest + (np.array(knob, float) - np.array([0, 0]) - rest - np.array([40 * sc, 0])) * u
    arms = {"n": ("ik", (float(tg[0]), float(tg[1])), -1), "f": ("ang", .15, .2)}
    hands = {"n": {"dir": (1, .1), "curl": (.6 * u, .65 * u, .7 * u, .72 * u), "thumb": .5 * u}, "f": {"curl": (.4, .45, .5, .55), "thumb": .4}}
    return figure("dima", x, y, k, EXPR["dima"].get(expr, expr) if isinstance(expr, str) else expr, lean=.06 * u, arms=arms, hands=hands,
                  feet=st["feet"])


def dima_chair78(x, y, k, u_stretch=0.0, u_book=0.0, t=0.0, expr=None, book_at=None):
    """Сидит в кресле (ноги вперёд на пол). Потягивание: обе руки вверх над головой, корпус назад; книга: ближняя кисть к book_at."""
    sc = k * HEIGHT["dima"]
    us, ub = lib.clamp(u_stretch), lib.clamp(u_book)
    up = math.sin(math.pi * us) if us < 1 else 0.0       # потянулся и опустил
    ex = expr or ("stretch78" if up > .3 else "read78" if ub > .5 else "calm_pet78")
    ba = np.array(book_at if book_at is not None else (x + 330 * sc, y - 60 * sc), float)
    rest_n = np.array([x + 240 * sc, y - 120 * sc])
    rest_f = np.array([x + 160 * sc, y - 130 * sc])
    hold = np.array([x + 300 * sc, y - 300 * sc])        # книга перед грудью
    if ub < .5:
        n_t = rest_n + (ba - rest_n) * lib.ease_io(ub / .5)
    else:
        n_t = ba + (hold - ba) * lib.ease_io((ub - .5) / .5)
    f_t = rest_f + (hold + np.array([-60 * sc, 10 * sc]) - rest_f) * lib.ease_io(lib.clamp((ub - .5) / .5))
    top_n, top_f = np.array([x - 10 * sc, y - 930 * sc]), np.array([x - 90 * sc, y - 920 * sc])
    n_t = n_t + (top_n - n_t) * up
    f_t = f_t + (top_f - f_t) * up
    arms = {"n": ("ik", tuple(n_t), -1 if up < .5 else 1), "f": ("ik", tuple(f_t), -1 if up < .5 else 1)}
    hands = {"n": {"dir": (.3, -1) if up > .5 else (1, -.3), "curl": (.3, .35, .4, .45) if up > .3 else (.55, .58, .62, .66), "thumb": .5},
             "f": {"dir": (.2, -1) if up > .5 else (1, -.2), "curl": (.3, .35, .4, .45) if up > .3 else (.55, .58, .62, .66), "thumb": .5}}
    fig = figure("dima", x, y, k, EXPR["dima"][ex] if isinstance(ex, str) else ex, lean=-.12 * up - .04, head_ang=-.18 * up + .1 * ub, arms=arms,
                 hands=hands, feet=beanbag_kw(x, y, k, .3)["feet"], layers=("legs", "pelvis", "arm_f", "arm_n", "body") if up > .45 else None)
    fig["book_hand"] = hand_pos(fig, "n", 70)
    return fig


def dima_lap78(x, y, k, tip, t=0.0, stroke=0.0, expr="calm_pet78"):
    """Петля s18: ракурс хука, указательный палец гладит кота (кончик ходит вдоль ±30·k)."""
    sc = k * HEIGHT["dima"]
    ph = math.sin(2 * math.pi * stroke)
    tp = (tip[0] + 34 * sc * ph, tip[1] + 10 * sc * ph)
    return dima_reach78(x, y, k, tp, pull=.55, t=t, expr=expr, clasp=False, lean=.04, hand_dir=(.62, .78))


def reflection78(svg_, col="#7f93c4", op=0.75, th=0.33, gain=4.0):
    """Отражение в тёмном стекле: только тёмная тушь рисунка (L < th) цветом стекла col, заливки прозрачны."""
    fid = lib.uid("refl")
    c = col.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lib.DEFS.append(f'<filter id="{fid}" color-interpolation-filters="sRGB" x="-5%" y="-5%" width="110%" height="110%">'
                    f'<feColorMatrix type="matrix" values="0 0 0 0 {r:.3f} 0 0 0 0 {g:.3f} 0 0 0 0 {b:.3f} '
                    f'{-gain * .3:.3f} {-gain * .59:.3f} {-gain * .11:.3f} 0 {gain * th:.3f}" result="m"/>'
                    f'<feComposite in="m" in2="SourceAlpha" operator="in"/>'
                    f'<feComponentTransfer><feFuncA type="linear" slope="{op:.3f}"/></feComponentTransfer></filter>')
    return f'<g filter="url(#{fid})">{svg_}</g>'


def finger_walker78(base, tip, k=1.0, phase=0.0, t=0.0, lift=1.0, seed=7800, shadow="#0b1024"):
    """Рука ползёт по одеялу (вид сверху, ладонь вниз): рукав худи от base к запястью, тыльная сторона кисти, указательный и средний —
    «ножки»: опорный прямой, кончик на ткани; шагающий приподнят к камере (короче, ноготь крупнее, тень под ним). tip — куда смотрят
    пальцы (направление и «нос» кисти: кончик опорного пальца ≈ tip). Безымянный и мизинец поджаты, большой палец прижат сбоку."""
    global C
    C = PAL["dima"]
    b, tp = np.array(base, float), np.array(tip, float)
    v = tp - b
    L_ = np.linalg.norm(v) + 1e-6
    d = v / L_
    n = np.array([-d[1], d[0]])
    wr = tp - d * 200 * k
    ph = 2 * math.pi * phase
    bob = abs(math.sin(ph)) * 6 * k * lift
    up = -d * bob * .3 - np.array([0, bob])

    def Q(x_, y_):
        q = wr + d * x_ * k + n * y_ * k + up
        return (float(q[0]), float(q[1]))
    o = []
    # рукав (ширина предплечья) с манжетой
    mid = b + (wr - b) * .5 + n * 8 * k
    sl = band([tuple(b), tuple(mid), tuple(wr - d * 22 * k)], 104 * k, 92 * k, step=4, cap=False)
    sh = blob([tuple(b + n * 52 * k), tuple(wr + n * 46 * k - d * 22 * k), tuple(wr + n * 10 * k - d * 22 * k), tuple(b + n * 10 * k)], C["TOP_SH"], .8)
    fold = line([tuple(b + d * L_ * .3 + n * 40 * k), tuple(b + d * L_ * .32), tuple(b + d * L_ * .3 - n * 36 * k)], 2.6, C["FOLD"], seed=seed + 1, op=.8)
    o.append(shape(sl, C["TOP"], sh + fold, w=4.8, seed=seed))
    cf = band([tuple(wr - d * 36 * k), tuple(wr + d * 2 * k)], 96 * k, 92 * k, step=3, cap=False)
    o.append(shape(cf, C["TOP_SH"], "".join(line([tuple(wr - d * (30 - 7 * j) * k + n * 46 * k), tuple(wr - d * (30 - 7 * j) * k - n * 46 * k)], 1.6,
                                                   C["TOP_SH2"], seed=seed + 3 + j, op=.8) for j in range(4)), w=4.0, seed=seed + 2))
    # пальцы-ножки
    legs = []
    for j, (off, pz) in enumerate(((-17, 0.0), (8, .5))):
        u = (phase + pz) % 1.0
        root = np.array([84.0, off])
        if u < .5:      # опора: прямой, кончик на ткани (относительно кисти едет назад — кисть идёт вперёд)
            s_ = u / .5
            foot = np.array([212 - 40 * s_, off * 1.25])
            knee = (root + foot) / 2 + np.array([0, off * .08])
            wf, swing = 24.0, 0.0
        else:           # шаг: приподнят к камере — короче, шире, ноготь крупнее
            s_ = (u - .5) / .5
            hgt = math.sin(math.pi * s_) * lift
            foot = np.array([172 + 40 * s_ - 46 * hgt, off * 1.25])
            knee = (root + foot) / 2 + np.array([-6 * hgt, off * .1])
            wf, swing = 24.0 * (1 + .18 * hgt), hgt
        legs.append((j, root, knee, foot, wf, swing))
    legs.sort(key=lambda q: q[5])
    for j, root, knee, foot, wf, sw in legs:
        if sw > .05:      # тень под приподнятым кончиком
            tq = Q(foot[0] + 26 * sw, foot[1] + 10 * sw)
            o.append(blob(ellipse_pts(tq[0], tq[1] + 10 * k * sw, 16 * k, 10 * k, 10), shadow, .35 * sw))
        fp = lib.band([Q(*root), Q(*knee), Q(*foot)], wf * k, wf * .86 * k, step=3)
        dd = (foot - knee) / (np.linalg.norm(foot - knee) + 1e-6)
        nl = ellipse_pts(*Q(*(foot - dd * 11)), (8 + 3 * sw) * k, (6.5 + 2 * sw) * k, 8, rot=math.degrees(math.atan2(*(d * dd[0] + n * dd[1])[::-1])))
        crease = line([Q(*(knee + np.array([0, -wf * .4]))), Q(*(knee + np.array([0, wf * .4])))], 1.8, C["SKIN_SH2"], seed=seed + 30 + j, op=.75)
        o.append(shape(fp, C["SKIN"] if j == 0 or sw > .05 else C["SKIN_SH"], crease + blob(nl, C["NAIL"], .95), w=4.0, seed=seed + 20 + j))
    # поджатые безымянный и мизинец — костяшки под краем кисти
    for j, (off, ln) in enumerate(((28, 30), (44, 24))):
        c0 = Q(88 + ln * .3, off)
        o.append(shape(ellipse_pts(c0[0], c0[1], ln * .7 * k, 12 * k, 10, rot=math.degrees(math.atan2(d[1], d[0]))), C["SKIN_SH"], "", w=3.6,
                       seed=seed + 10 + j))
    # большой палец прижат сбоку
    o.append(shape(lib.band([Q(30, -42), Q(62, -50), Q(84, -46)], 26 * k, 20 * k, step=3), C["SKIN"],
                   blob([Q(36, -40), Q(80, -42), Q(80, -36), Q(36, -34)], C["SKIN_SH"], .5), w=3.8, seed=seed + 12))
    # тыльная сторона кисти поверх корней пальцев: костяшки, тень с внешней стороны
    pp = [Q(-4, -40), Q(40, -46), Q(78, -38), Q(94, -18), Q(96, 4), Q(92, 30), Q(70, 46), Q(30, 48), Q(-4, 42)]
    knuck = "".join(line([Q(86, o_ - 6), Q(92, o_), Q(86, o_ + 6)], 1.8, C["SKIN_SH2"], seed=seed + 40 + i, op=.7) for i, o_ in enumerate((-17, 8, 30)))
    tend = "".join(line([Q(10, o_ * .5), Q(70, o_)], 1.4, C["SKIN_SH"], seed=seed + 44 + i, op=.6) for i, o_ in enumerate((-17, 8)))
    o.append(shape(pp, C["SKIN"], blob([pp[5], pp[6], pp[7], pp[8], Q(-4, 20), Q(70, 26)], C["SKIN_SH"], .5) + knuck + tend, w=4.4, seed=seed + 41))
    return "".join(o)


# ─── изобретатель (без имени, не портрет): седые кудри, очки подняты на лоб, голубая рубашка с закатанными рукавами, фартук ───
PAL["inventor"] = dict(SKIN="#efc8a8", SKIN_SH="#d6a487", SKIN_SH2="#bd8b72", HAIR="#8f8a92", HAIR_SH="#625e68", HAIR_HI="#c4c0c8",
                       TOP="#9cc3e0", TOP_SH="#77a2c4", TOP_SH2="#5b84a8", FOLD="#46698c", STITCH="#e8f2fa", FRAME="#4a3a30",
                       APRON="#a97e55", APRON_SH="#85603c",
                       LEGS="#5b5048", LEGS_SH="#433a34", LEGS_SEAM="#786b61", SHOE="#5a3e2c", SHOE_SH="#3f2b1e", SOLE="#2e231c", SOLE_SH="#1f1813",
                       STRIPE="#a76a3e", NAIL="#f3d2c0")
HEIGHT["inventor"] = 1.02
HEADS64 = HEADS64 + ("inventor",)
FRIENDLIKE = FRIENDLIKE + ("inventor",)
FACES = FACES + ("inventor",)


def _inventor_head(expr):
    """Голова изобретателя: лицо F_FACE (как у youth), короткие седые кудри шапкой, морщинки у глаз, очки на лбу (линзы — блик)."""
    s = [_ear64()]
    inner = [blob([(-120, -210), (-40, -210), (-60, -40), (-56, 40), (-30, 160), (-120, 160)], C["SKIN_SH"], .95),
             blob(ellipse_pts(56, -16, 100, 60, 14), "#e5a99a", .3), blob(ellipse_pts(100, 38, 22, 12, 10), "#e98a86", .3)]
    s.append(shape(F_FACE, C["SKIN"], "".join(inner), w=5.6, seed=471))
    s.append(_wrinkles64(mouth_=True, forehead=1, op=.6))
    s.append(_nose())
    s.append(_mouth_gen(expr, INK, seed=391))
    s.append(eyes(expr, F_EYE_N, F_EYE_F, bags=False))
    s.append(_brows(expr, C["HAIR_SH"], 1.2, sd=362))
    base = [(118, -84), (116, -128), (84, -170), (30, -190), (-34, -188), (-92, -166), (-130, -120), (-140, -64), (-124, -30), (-104, -56),
            (-86, -96), (-40, -112), (0, -108), (44, -114), (86, -102), (108, -80)]
    hi = blob([(-160, -200), (-40, -200), (-50, -120), (-90, -90), (-110, -30), (-160, -30)], C["HAIR_SH"], .8)
    hi += blob([(0, -180), (60, -160), (96, -120), (60, -142), (30, -160)], C["HAIR_HI"], .9)
    for i, (cx_, cy_) in enumerate([(-80, -150), (-30, -162), (24, -164), (70, -140), (-112, -96), (-50, -124), (10, -130), (-120, -50)]):
        hi += line([(cx_ - 12, cy_ + 6), (cx_ - 4, cy_ - 10), (cx_ + 10, cy_ - 6), (cx_ + 6, cy_ + 8)], 2.6, C["HAIR_SH"], seed=880 + i, op=.85)
    s.append(shape(fur(base, depth=20, every=7, seed=870), C["HAIR"], hi, w=5.2, seed=871))
    gl = "".join(blob(ellipse_pts(cx_, cy_, rx_, ry_, 18), "#cfe6f6", .75) for cx_, cy_, rx_, ry_ in ((16, -22, 48, 42), (92, -20, 35, 39)))
    s.append(f'<g transform="translate(4 -118) scale(.82 .58)">{gl}{_glasses64("round", "#2a1e18", sd=890, w=9.0)}</g>')
    return "".join(s)


def inventor_shirt_parts():
    """Голубая рубашка + фартук мастерской (кармашек с карандашом), острый воротник."""
    body = [(-112, 34), (-120, -40), (-132, -170), (-128, -280), (-112, -360), (-78, -410), (-20, -432), (40, -426),
            (84, -398), (112, -330), (126, -230), (124, -120), (116, -20), (110, 34)]
    inner = blob([(30, -440), (130, -380), (140, 40), (60, 40), (80, -200)], C["TOP_SH"], .8)
    inner += blob([(-140, -300), (-100, -320), (-104, -100), (-140, -60)], C["TOP_SH"], .5)
    ap = [(-60, -300), (70, -306), (96, -200), (112, 40, 1), (-110, 40, 1), (-90, -200)]
    ai = blob([(40, -310), (110, -200), (120, 40), (60, 40)], C["APRON_SH"], .8)
    ai += shape([(-30, -150), (40, -152), (42, -80, 1), (-28, -78, 1)], C["APRON"], line([(-26, -146), (38, -148)], 1.6, C["APRON_SH"], seed=905, op=.9),
                w=3.0, seed=904)
    ai += shape([(-4, -200), (8, -202), (10, -144), (-2, -142)], "#e6c25a", blob([(-4, -200), (8, -202), (8, -190), (-4, -188)], "#d76a5a"), w=2.4, seed=906)
    inner += shape(ap, C["APRON"], ai, w=4.4, seed=903)
    inner += line([(-56, -300), (-40, -380), (-20, -428)], 4.0, C["APRON_SH"], seed=907, taper=.1, wmin=.8)
    inner += line([(66, -306), (60, -380), (44, -424)], 4.0, C["APRON_SH"], seed=908, taper=.1, wmin=.8)
    torso = shape(body, C["TOP"], inner, w=5.2, seed=902)
    col = [(-60, -440), (-20, -462), (40, -452), (78, -424), (96, -380), (60, -398), (24, -424), (-30, -426), (-70, -410)]
    back = shape(col, C["TOP_SH"], "", w=4.0, seed=909)
    tip = shape([(30, -440), (80, -420), (100, -372), (66, -390), (40, -420)], C["TOP"], "", w=3.4, seed=910)
    return back, torso, tip


CLOTHES64["inventor"] = inventor_shirt_parts
_head64_orig = head64


def head64(expr, style):        # noqa: F811 — тот же вызов, плюс стиль изобретателя
    if style == "inventor":
        return _inventor_head(expr)
    return _head64_orig(expr, style)


_sleeve_orig = sleeve


def sleeve(S, E, Wr, far, seed, who):       # noqa: F811 — у изобретателя рукав закатан выше локтя, предплечье голое
    if who != "inventor":
        return _sleeve_orig(S, E, Wr, far, seed, who)
    S, E, Wr = np.array(S, float), np.array(E, float), np.array(Wr, float)
    s = [limb_band(E - (E - S) * .1, Wr, 96, 80, C["SKIN"], far, seed + 8,
                   lambda a, b, d, n: blob([P(np.array(a) - n * 40), P(np.array(b) - n * 32), P(np.array(b) - n * 10), P(np.array(a) - n * 12)],
                                           far_c(C["SKIN_SH"], far), .8)),
         limb_band(S, E + (Wr - E) * .08, 132, 116, C["TOP"], far, seed + 7,
                   lambda a, b, d, n: blob([P(np.array(a) - n * 60), P(np.array(b) - n * 50), P(np.array(b) - n * 14), P(np.array(a) - n * 18)],
                                           far_c(C["TOP_SH"], far), .85))]
    d = (Wr - E) / np.linalg.norm(Wr - E)
    c0 = E + d * 4
    roll = band([P(c0 - d * 18), P(c0 + d * 26)], 128, 124, step=3, cap=False)
    s.append(shape(roll, far_c(C["TOP_SH"], far), line([P(c0 + np.array([-d[1], d[0]]) * 58), P(c0 - np.array([-d[1], d[0]]) * 58)], 1.8,
                                                        far_c(C["FOLD"], far), seed=seed + 21, op=.8), w=4.0, seed=seed + 20))
    return "".join(s)


EXPR["inventor"] = {
    "proud": {"brows": "up", "mouth": "grin", "open": .6, "lid": .8, "look": (.3, -.6)},
    "busy": {"brows": "frown", "mouth": "flat", "lid": .6, "look": (.5, .6)},
    "slap": {"brows": "up", "mouth": "smile", "smile": 1.0, "lid": .7, "look": (.5, .5)},
    "look": {"brows": "worry", "mouth": "open", "open": .35, "lid": .9, "look": (.7, -.3)},
    "turn": {"brows": "worry", "mouth": "flat", "lid": .75, "look": (-.4, 0)},
    "regret": {"brows": "sad", "mouth": "wobble", "lid": .3, "closed": .7, "look": (0, .3)},
    "tug": {"brows": "frown", "mouth": "pursed", "lid": .4, "squeeze": .6, "look": (.6, .4)},
}
_INV_P = {
    "sew": (.14, .16, {"f": ("ik", (215, -270), -1), "n": ("ik", (300, -262), -1)},
            {"f": {"dir": (.9, -.3), "curl": (.55, .6, .65, .7), "thumb": .6}, "n": {"dir": (-.2, -1), "curl": (.5, .6, .65, .7), "thumb": .65}}),
    "raise": (-.04, -.16, {"f": ("ik", (190, -230), -1), "n": ("ik", (330, -700), -1)},
              {"f": {"dir": (1, .2), "curl": (.4, .45, .5, .55), "thumb": .4}, "n": {"dir": (.3, -1), "curl": (.6, .65, .7, .72), "thumb": .65}}),
    "slap": (.2, .22, {"f": ("ik", (190, -230), -1), "n": ("ik", (380, -150), -1)},
             {"f": {"dir": (1, .2), "curl": (.4, .45, .5, .55), "thumb": .4}, "n": {"dir": (1, .35), "curl": (.05, .05, .1, .12), "spread": .2, "thumb": .15}}),
    "sit": (.1, .14, {"f": ("ik", (220, -110), -1), "n": ("ik", (290, -100), -1)},
            {"f": {"dir": (1, .4), "curl": (.4, .45, .5, .55), "thumb": .4}, "n": {"dir": (1, .4), "curl": (.35, .4, .45, .5), "thumb": .35}}),
    "head": (.06, .3, {"f": ("ik", (-160, -640), 1), "n": ("ik", (-60, -770), 1)},
             {"f": {"dir": (.5, .9), "curl": (.3, .35, .4, .45), "thumb": .3}, "n": {"dir": (1, .35), "curl": (.25, .3, .35, .4), "spread": .2, "thumb": .3}}),
    "pull": (-.14, -.04, {"f": ("ik", (300, -260), -1), "n": ("ik", (380, -250), -1)},
             {"f": {"dir": (1, 0), "curl": (.75, .78, .8, .82), "thumb": .7}, "n": {"dir": (1, 0), "curl": (.75, .78, .8, .82), "thumb": .7}}),
}
POSE.update({"inv_" + k_: v_ for k_, v_ in _INV_P.items()})


def inventor(x, y, k, pose="sew", t=0.0, expr=None, u=1.0, feet=None, flip=False, head_add=0.0, lean_add=0.0, arms=None, hands=None):
    """Изобретатель. pose — имя или (из, в) с u; feet: None (по пояс), "stand", "sit" (на куче ленты: ноги вперёд-вниз) или dict."""
    if isinstance(pose, (tuple, list)):
        pa, pb = "inv_" + pose[0], "inv_" + pose[1]
        name = pose[1] if u > .5 else pose[0]
        pk = mix_pose(pa, pb, u, x, y, k, "inventor")
    else:
        name = pose
        pk = pose_kw("inv_" + pose, x, y, k, "inventor")
    ex = EXPR["inventor"].get(expr or {"sew": "busy", "raise": "proud", "slap": "slap", "sit": "look", "head": "regret", "pull": "tug"}[name], {}) \
        if not isinstance(expr, dict) else expr
    ex = dict(ex)
    if feet == "stand":
        ft = stand_kw(x, y, k, "inventor")["feet"]
    elif feet == "sit":
        ft = knees_kw(x, y, k, .3, 150, "inventor")["feet"]
    else:
        ft = feet
    breath = .012 * math.sin(t * 2 * math.pi / 3.4)
    on_head = name == "head" and (u > .6 or not isinstance(pose, (tuple, list)))
    lay = ("legs", "pelvis", "arm_f", "arm_n", "body") if on_head else None
    hand_n = None
    if on_head:      # руки за голову: локти назад, ближняя кисть поверх волос (рисуется после головы), дальняя — за затылком
        hand_n = dict(pk["hands"]["n"])
        pk["hands"] = dict(pk["hands"], n={"kind": "none"})
    if arms:
        pk["arms"] = dict(pk["arms"], **arms)
    if hands:
        pk["hands"] = dict(pk["hands"], **hands)
    if name == "head":      # цели кистей — от настоящего положения головы (наклон и посадка меняют её место)
        pre = figure("inventor", x, y, k, ex, lean=pk["lean"] + lean_add + breath, head_ang=pk["head_ang"] + head_add, arms=pk["arms"], hands=pk["hands"],
                     feet=ft, layers=("body",))
        hx_, hy_ = pre["head"]
        scl = pre["scale"]
        wv = u if isinstance(pose, (tuple, list)) else 1.0
        for side, off in (("n", (-70, -150)), ("f", (-190, -40))):
            a_ = pk["arms"][side]
            tgt = (hx_ + off[0] * scl, hy_ + off[1] * scl)
            if a_[0] == "ik":
                tgt = (a_[1][0] + (tgt[0] - a_[1][0]) * wv, a_[1][1] + (tgt[1] - a_[1][1]) * wv)
            pk["arms"] = dict(pk["arms"], **{side: ("ik", tgt, 1)})
    fig = figure("inventor", x, y, k, ex, lean=pk["lean"] + lean_add + breath, head_ang=pk["head_ang"] + head_add, arms=pk["arms"], hands=pk["hands"],
                 feet=ft, flip=flip, layers=lay)
    if hand_n:
        wr = fig["wrist"]["n"]
        d = hand_n.get("dir", (1, .35))
        if flip:
            d = (-d[0], d[1])
        fig["svg"] += hand_svg("inventor", wr, d, k=fig["scale"], curl=hand_n.get("curl", (.25, .3, .35, .4)), spread=hand_n.get("spread", .2),
                               thumb=hand_n.get("thumb", .3), flip=-1 if flip else 1, seed=7)
    fig["hold"] = hand_pos(fig, "n", 70)
    fig["palm"] = hand_pos(fig, "n", 60)
    return fig


# ═════════════════════════════ РИЛС 80 «МАМА БЫЛА ПРАВА» (автор — группа B) ═════════════════════════════
# Все люди рилса — отсюда, кот — только common/cat.py. Все смотрят вправо (flip=True — влево). (x, y) — таз, голова ≈ 300·k·рост.
# dima80(x, y, k, expr, pose, t, u, age, feet, ...) — Дима рилса 80 (горчичное худи, лохматый). age 0…1: 0 — подросток (хук, s01–s03:
#   ниже ростом ×0.8, без щетины и мешков), 0.5 — студент (×0.9, лёгкая щетина), 1 — взрослый (щетина). Рост меняет ТОЛЬКО масштаб и
#   щетину — одно лицо, одна одежда. feet: None (по пояс), "stand" (стоит; (x, y) — таз), dict figure(). Для «стоит на полу floor» —
#   hip_on_floor(floor, k, age). pose — имя POSE или (из, в) с u. Возвращает figure() + "hold" (точка в ближней ладони), "palm",
#   "neck" (середина шеи спереди — куда вешать шнур бирки), "chest" (середина груди — где висит бирка), "k" (итоговый масштаб).
#   Позы POSE["d80_*"]: stand (руки вниз), sag (под гирей: наклон вперёд, голова вниз, руки висят), grab (обе руки держат бирку у живота
#   — тянет вниз), kneel_down (на коленях, руки упёрлись в пол перед собой — используй с kneel_kw), tie (обе руки у горла затягивают шнур
#   вверх), adjust (ближняя рука поправляет бирку у груди), slump (смирился: плечи вниз, руки висят, голова вниз), neck (ближняя ладонь
#   трогает шею), sit (сидит за столом, предплечья на крышке), sleeve (сидит, ближняя рука закатывает рукав дальней), pen (сидит, ближняя
#   кисть с ручкой над листом: ручку кладёт вызывающий в "hold"), palm (сидит, ладонь на груди), turn_phone — см. dima80_phone.
#   Ноги: kneel_kw (на коленях), sit_kw (сидит на стуле), stand → feet="stand".
#   Мимика EXPR["dima"]: teen80 (подросток спокойно), hit80 (вздрогнул: зажмурен, рот «о»), heavy80 (тяжело: брови домиком, губы сжаты,
#   взгляд вниз), crush80 (лицом к полу: зажмурен, рот кривой), cower80 (съёжился, смотрит вверх), grow80 (растёт: растерянно вперёд),
#   tie80 (сам затягивает: губы сжаты, взгляд вниз), resign80 (смирился: веки опущены, рот вниз), det80 (решительно за столом), gloom80
#   (под облаком: устало), screen80 (в телефон: облегчение, свет), calm80 (спокойно смотрит вверх на облачко), yes80 (кивает «да»: мягкая
#   полуулыбка, веки прикрыты), say_yes80 (одними губами «да»: рот приоткрыт), write80 (пишет, мягко), touch80 (трогает шею: удивлён).
# accuser_shadow(kind, x, y, k, jab, t, col, op, ...) — ТЕНЬ-обвинитель силуэтом без лица (сплошной цвет, мягкий край): kind "mama"
#   (пучок, указка в ближней руке), "teacher" (мужчина в пиджаке, в дальней руке раскрытая книга у груди, тычет пальцем), "aunt" (пышная
#   причёска, сумочка на локте дальней руки, тычет пальцем). jab 0…1: 0 — рука занесена вверх-назад, 1 — выброшена вперёд-вниз.
#   reach (по умолчанию 1) — длина выпада; aim=(x, y) — точка, куда тычет (мир), тогда jab ведёт туда. (x, y) — таз, стоит.
#   Возвращает dict(svg, tip — кончик указки или пальца, head, wrist). flip=True — смотрит влево.
# scientist80(kind, x, y, k, pose, t, expr, feet) — учёные (без имён, не портреты): kind "a" — женщина, тёмное каре, очки, бордовый
#   свитер с белым воротом; "b" — мужчина, седая борода, твидовый кардиган. pose: "write" (сидит, ближняя кисть пишет вниз-вперёд:
#   "hold"), "lean" (наклон к тетради, рука у подбородка), "point" (тычет в тетрадь пальцем: "finger"), "rest". Мимика "focus", "ah"
#   (озарение), "talk", "smile".
EXPR["dima"].update({
    "teen80": {"brows": "calm", "mouth": "flat", "lid": .8, "look": (.4, -.2), "bags": False, "stubble": 0.0},
    "hit80": {"brows": "worry", "mouth": "o", "open": .45, "squeeze": 1.0, "bags": False, "stubble": 0.0},
    "heavy80": {"brows": "sad", "mouth": "pressed", "lid": .5, "look": (.3, .8), "bags": False, "stubble": 0.0},
    "crush80": {"brows": "worry", "mouth": "wobble", "squeeze": 1.0, "bags": False, "stubble": 0.0},
    "cower80": {"brows": "worry", "mouth": "frown", "lid": .95, "look": (-.5, -.7), "bags": False, "stubble": 0.0},
    "grow80": {"brows": "worry", "mouth": "flat", "lid": .8, "look": (.5, .2), "bags": False},
    "tie80": {"brows": "sad", "mouth": "pressed", "lid": .45, "look": (.3, .9)},
    "resign80": {"brows": "sad", "mouth": "tired", "lid": .3, "look": (.2, .9)},
    "det80": {"brows": "det", "mouth": "pressed", "lid": .75, "look": (.6, .45), "bags": False},
    "gloom80": {"brows": "sad", "mouth": "tired", "lid": .5, "look": (.4, .5), "bags": False},
    "screen80": {"brows": "calm", "mouth": "smile", "smile": .3, "lid": .55, "look": (.5, .55), "bags": False},
    "calm80": {"brows": "calm", "mouth": "flat", "lid": .8, "look": (.35, -.75), "bags": False},
    "yes80": {"brows": "calm", "mouth": "smile", "smile": .35, "lid": .4, "look": (.4, -.5), "bags": False},
    "say_yes80": {"brows": "calm", "mouth": "o", "open": .25, "lid": .55, "look": (.4, -.6), "bags": False},
    "write80": {"brows": "calm", "mouth": "smile", "smile": .25, "lid": .55, "look": (.6, .6), "bags": False},
    "touch80": {"brows": "up", "mouth": "o", "open": .3, "lid": 1.0, "look": (.6, .3), "bags": False},
})
_GRIP = {"curl": (.7, .74, .78, .8), "thumb": .65}
_OPEN = {"curl": (.15, .15, .2, .25), "spread": .2, "thumb": .25}
POSE.update({
    "d80_stand": (0.0, 0.0, {"f": ("ang", 0.16, 0.16), "n": ("ang", -0.08, 0.22)},
                  {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": {"curl": (.35, .35, .4, .45), "thumb": .35}}),
    "d80_sag": (0.3, 0.42, {"f": ("ang", 0.5, 0.1), "n": ("ang", 0.42, 0.14)},
                {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.4, .4, .45, .5), "thumb": .4}}),
    "d80_grab": (0.22, 0.35, {"f": ("ik", (190, -250), -1), "n": ("ik", (240, -235), -1)},
                 {"f": dict(_GRIP, dir=(.2, 1)), "n": dict(_GRIP, dir=(.1, 1))}),
    "d80_kneel_down": (0.55, 0.45, {"f": ("ik", (330, 290), -1), "n": ("ik", (390, 300), -1)},
                       {"f": dict(_OPEN, dir=(1, .25)), "n": dict(_OPEN, dir=(1, .2))}),
    "d80_tie": (0.06, 0.2, {"f": ("ik", (95, -300), -1), "n": ("ik", (200, -285), -1)},
                {"f": dict(_GRIP, dir=(.3, 1)), "n": dict(_GRIP, dir=(.2, 1))}),
    "d80_adjust": (0.06, 0.28, {"f": ("ang", 0.16, 0.16), "n": ("ik", (150, -290), -1)},
                   {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": dict(_GRIP, dir=(-.2, 1))}),
    "d80_slump": (0.24, 0.5, {"f": ("ang", 0.1, 0.06), "n": ("ang", 0.0, 0.08)},
                  {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.4, .4, .45, .5), "thumb": .4}}),
    "d80_neck": (0.0, 0.1, {"f": ("ang", 0.16, 0.16), "n": ("ik", (105, -350), -1)},
                 {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": {"dir": (-.6, -.6), "curl": (.15, .15, .2, .25), "spread": .15, "thumb": .2}}),
    "d80_sit": (0.08, 0.0, {"f": ("ik", (190, -200), -1), "n": ("ik", (240, -195), -1)},
                {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.3, .3, .35, .4), "thumb": .3}}),
    "d80_sleeve": (0.1, 0.12, {"f": ("ik", (230, -215), -1), "n": ("ik", (160, -250), -1)},
                   {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": dict(_GRIP, dir=(1, .25))}),
    "d80_pen": (0.18, 0.12, {"f": ("ik", (200, -210), -1), "n": ("ik", (290, -235), -1)},
                {"f": {"curl": (.2, .2, .25, .3), "thumb": .2}, "n": {"dir": (.5, .9), "curl": (.62, .7, .78, .8), "thumb": .6}}),
    "d80_palm": (0.02, -0.05, {"f": ("ik", (200, -200), -1), "n": ("ik", (150, -290), -1)},
                 {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (-.4, -.9), "curl": (.05, .05, .1, .15), "spread": .1, "thumb": .1}}),
})


def age_k(age):
    """Масштаб роста Димы: подросток 0.8 → взрослый 1.0."""
    return .8 + .2 * lib.clamp(age)


def hip_on_floor(floor, k, age=1.0):
    """y таза стоящего Димы, чтобы ступни стояли на полу floor (учитывает возраст)."""
    sc = k * age_k(age) * HEIGHT["dima"]
    return floor - (LEG_LEN - 12) * sc


def kneel_kw(x, y, scale, who="dima", age=1.0):
    """На коленях: колени на полу перед тазом, голени назад, носки за спиной. (x, y) — таз; пол ≈ y + 330·sc."""
    sc = scale * age_k(age) * HEIGHT.get(who, 1.0)
    return {"feet": {"n": ((x - 150 * sc, y + 285 * sc), 2.95), "f": ((x - 200 * sc, y + 290 * sc), 2.95)}}


def dima80(x, y, k, expr="teen80", pose="d80_stand", t=0.0, u=1.0, age=1.0, feet=None, flip=False, **kw):
    """Дима рилса 80 (см. шапку раздела). k — масштаб взрослого; подросток получается age."""
    sc = k * age_k(age)
    if isinstance(pose, (tuple, list)):
        pk = mix_pose(pose[0], pose[1], u, x, y, sc, "dima")
    else:
        pk = pose_kw(pose, x, y, sc, "dima")
    ex = dict(EXPR["dima"][expr]) if isinstance(expr, str) else dict(expr)
    ex["stubble"] = min(ex.get("stubble", 1.0), 1.0 if age >= 1 else lib.clamp((age - .25) / .75))
    if age < .5:
        ex["bags"] = False
    ft = stand_kw(x, y, sc, "dima")["feet"] if feet == "stand" else feet
    br = .012 * math.sin(t * 2 * math.pi / 3.3 + 1.0)
    arms = dict(pk["arms"], **kw.pop("arms", {}))
    hands = dict(pk["hands"], **kw.pop("hands", {}))
    fig = figure("dima", x, y, sc, ex, lean=pk["lean"] + kw.pop("lean_add", 0.0) + br, head_ang=pk["head_ang"] + kw.pop("head_add", 0.0), arms=arms,
                 hands=hands, feet=ft, flip=flip, **kw)
    fig["hold"] = hand_pos(fig, "n", 70)
    fig["palm"] = hand_pos(fig, "n", 55)
    s_ = fig["scale"]
    hx, hy = fig["head"]
    sgn = -1 if flip else 1
    fig["neck"] = (hx - sgn * 10 * s_, hy + 150 * s_)
    fig["chest"] = (hx + sgn * 20 * s_, hy + 330 * s_)
    fig["k"] = sc
    return fig


# ─── тени-обвинители: силуэт одним цветом, без лица ───
_ACC = {"mama": ("mama", .98), "teacher": ("bald", 1.0), "aunt": ("bob", 1.0)}


def _silhouette(inner, col, op, blur_sd):
    fid = lib.uid("acc")
    r, g, b = (int(col[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lib.DEFS.append(f'<filter id="{fid}" x="-25%" y="-25%" width="150%" height="150%" color-interpolation-filters="sRGB">'
                    f'<feColorMatrix type="matrix" values="0 0 0 0 {r:.3f} 0 0 0 0 {g:.3f} 0 0 0 0 {b:.3f} 0 0 0 40 0"/>'
                    + (f'<feGaussianBlur stdDeviation="{blur_sd:.1f}"/>' if blur_sd > 0 else '') + '</filter>')
    return f'<g filter="url(#{fid})" opacity="{op:.3f}">{inner}</g>'


def accuser_shadow(kind, x, y, k, jab=0.0, t=0.0, col="#120d24", op=.88, blur_sd=2.5, flip=False, aim=None, reach=1.0, raw=False):
    """Тень-обвинитель (см. шапку раздела). raw=True — без фильтра силуэта (для проверки позы глазами)."""
    who, hk = _ACC[kind]
    sc = k * hk
    j = lib.clamp(jab)
    tremble = 1.2 * math.sin(t * 23.0) + .8 * math.sin(t * 37.0 + 1)
    # ближняя рука: занесена вверх-назад → выброшена вперёд-вниз
    up = (60, -760)
    if aim is not None:
        ax, ay = aim
        sgn = -1 if flip else 1
        down = ((ax - x) * sgn / sc, (ay - y) / sc)
        L = math.hypot(*down)
        lim = 560 * reach
        if L > lim:
            down = (down[0] * lim / L, down[1] * lim / L)
    else:
        down = (520 * reach, -470)
    tgt = (lerp_(up[0], down[0], j), lerp_(up[1], down[1], j) + tremble)
    lean = -.06 + .16 * j
    hands_n = dict(_GRIP, dir=(1, -.2)) if kind == "mama" else {"dir": (1, .1), "curl": (0, .85, .9, .9), "spread": .05, "thumb": .7}
    far_arm = ("ang", 0.2, 0.2)
    hands_f = {"curl": (.35, .35, .4, .45), "thumb": .35}
    if kind == "teacher":
        far_arm = ("ik", (150, -330), -1)
        hands_f = dict(_GRIP, dir=(1, -.3))
    elif kind == "aunt":
        far_arm = ("ik", (40, -300), 1)
        hands_f = {"dir": (.3, -1), "curl": (.5, .5, .55, .6), "thumb": .4}
    arms = {"n": ("ik", (x + tgt[0] * sc, y + tgt[1] * sc), 1), "f": far_arm if far_arm[0] == "ang" else ("ik", (x + far_arm[1][0] * sc, y + far_arm[1][1] * sc), far_arm[2])}
    fig = figure(who, x, y, sc, {"brows": "sad", "mouth": "flat"}, lean=lean, head_ang=-.1 + .25 * j, arms=arms, hands={"n": hands_n, "f": hands_f},
                 feet=stand_kw(x, y, sc, who)["feet"])
    s_ = fig["scale"]
    hx, hy = fig["head"]
    extra = []
    wr = np.array(fig["wrist"]["n"])
    el = np.array(fig["elbow"]["n"])
    d = wr - el
    d /= (np.linalg.norm(d) + 1e-6)
    tip = wr + d * 70 * s_
    if kind == "mama":      # пучок на затылке и указка
        extra.append(blob(ellipse_pts(hx - 120 * s_, hy - 100 * s_, 82 * s_, 74 * s_, 16), INK))
        extra.append(blob(ellipse_pts(hx - 70 * s_, hy - 150 * s_, 46 * s_, 34 * s_, 12), INK))
        a = wr + d * 30 * s_
        tip = wr + d * 520 * s_
        nrm = np.array([-d[1], d[0]])
        extra.append(blob([tuple(a + nrm * 9 * s_), tuple(tip + nrm * 5 * s_), tuple(tip - nrm * 5 * s_), tuple(a - nrm * 9 * s_)], INK))
    elif kind == "teacher":   # книга у груди в дальней руке, торчит прямоугольником
        fw = np.array(fig["wrist"]["f"])
        extra.append(blob([(fw[0] - 20 * s_, fw[1] - 150 * s_), (fw[0] + 110 * s_, fw[1] - 170 * s_), (fw[0] + 130 * s_, fw[1] + 20 * s_),
                           (fw[0] - 10 * s_, fw[1] + 40 * s_)], INK))
    elif kind == "aunt":      # пышная причёска и сумочка на локте
        extra.append(blob(ellipse_pts(hx - 10 * s_, hy - 90 * s_, 190 * s_, 150 * s_, 20), INK))
        fe = np.array(fig["elbow"]["f"])
        extra.append(blob(ellipse_pts(fe[0] - 20 * s_, fe[1] + 110 * s_, 90 * s_, 70 * s_, 16), INK))
        extra.append(line([(fe[0] - 70 * s_, fe[1] + 60 * s_), (fe[0], fe[1] - 10 * s_), (fe[0] + 40 * s_, fe[1] + 60 * s_)], 10 * s_, INK, taper=0, wmin=1, seed=8001))
    inner = "".join(extra) + fig["svg"] if kind == "aunt" else fig["svg"] + "".join(extra)
    tipw = (float(tip[0]), float(tip[1]))
    if flip:
        inner = f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{inner}</g>'
        tipw = (2 * x - tipw[0], tipw[1])
        hx = 2 * x - hx
    svg_ = inner if raw else _silhouette(inner, col, op, blur_sd)
    return dict(svg=svg_, tip=tipw, head=(hx, hy), wrist=fig["wrist"], scale=s_)


def lerp_(a, b, u):
    return a + (b - a) * u


# ─── учёные (без имён, не портреты) ───
PAL["sci80a"] = dict(PAL["bob"], HAIR="#1f1a1e", HAIR_SH="#120e11", HAIR_HI="#3d343a", SKIN="#efcdb4", SKIN_SH="#d6a68c", SKIN_SH2="#c08f78",
                     TOP="#8e2f3c", TOP_SH="#6e222e", TOP_SH2="#561a24", FOLD="#3e121a", STITCH="#f2e8dc",
                     LEGS="#3a3a48", LEGS_SH="#2a2a34", LEGS_SEAM="#565668")
PAL["sci80b"] = dict(PAL["beard"], HAIR="#cfcbd2", HAIR_SH="#9c97a3", HAIR_HI="#eeebf0", SKIN="#e8bf9e", SKIN_SH="#cf9f80", SKIN_SH2="#b88566",
                     TOP="#7a6a4e", TOP_SH="#5e5038", TOP_SH2="#4a3f2c", FOLD="#352c1e", STITCH="#c9b88e", TEE="#e9e4d8", TEE_SH="#cfc8b8",
                     PLAID="#5b4c34", PLAID2="#a8946a", LEGS="#4a4438", LEGS_SH="#36312a", LEGS_SEAM="#615a4c")
HEIGHT.update({"sci80a": .95, "sci80b": 1.02})
HEADS64 = HEADS64 + ("sci80a", "sci80b")
FRIENDLIKE = FRIENDLIKE + ("sci80a", "sci80b")
FACES = FACES + ("sci80a", "sci80b")
CLOTHES64["sci80a"] = sweater_parts
CLOTHES64["sci80b"] = knit_cardigan_parts
EXPR["sci80a"] = {"focus": {"brows": "calm", "mouth": "flat", "lid": .7, "look": (.5, .7)},
                  "ah": {"brows": "up", "mouth": "o", "open": .35, "lid": 1.0, "look": (.4, .2)},
                  "talk": {"brows": "calm", "mouth": "smile", "smile": .4, "lid": .8, "look": (-.6, 0)},
                  "smile": {"brows": "calm", "mouth": "smile", "smile": .7, "lid": .65, "look": (.4, .5)}}
EXPR["sci80b"] = {k_: dict(v_) for k_, v_ in EXPR["sci80a"].items()}
POSE.update({
    "sci_write": (0.18, 0.15, {"f": ("ik", (220, -200), -1), "n": ("ik", (300, -225), -1)},
                  {"f": {"curl": (.2, .2, .25, .3), "thumb": .2}, "n": {"dir": (.5, .9), "curl": (.62, .7, .78, .8), "thumb": .6}}),
    "sci_lean": (0.22, 0.2, {"f": ("ik", (230, -200), -1), "n": ("ik", (190, -360), 1)},
                 {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (.2, -1), "curl": (.5, .55, .6, .65), "thumb": .4}}),
    "sci_point": (0.15, 0.12, {"f": ("ik", (220, -200), -1), "n": ("ik", (330, -240), -1)},
                  {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (.6, .8), "curl": (0, .85, .9, .9), "spread": .05, "thumb": .7}}),
    "sci_rest": (0.05, 0.05, {"f": ("ik", (200, -200), -1), "n": ("ik", (250, -195), -1)},
                 {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.3, .3, .35, .4), "thumb": .3}}),
})
_head64_orig80 = head64


def head64(expr, style):        # noqa: F811 — плюс учёные рилса 80 (головы стилей bob и beard в своей палитре, у «a» очки)
    if style == "sci80a":
        h = person_head(expr, "bob")
        gl = (line([(-6, -36), (52, -40)], 4.4, "#2a2228", taper=0, wmin=1, seed=8010) + ring(ellipse_pts(20, -10, 34, 26, 14), 4.6, 8011)
              + ring(ellipse_pts(94, -8, 26, 24, 14), 4.0, 8012) + line([(54, -12), (68, -12)], 4, "#2a2228", taper=0, wmin=1, seed=8013))
        return h + gl
    if style == "sci80b":
        return person_head(expr, "beard")
    return _head64_orig80(expr, style)


def scientist80(kind, x, y, k, pose="write", t=0.0, expr="focus", feet=None, flip=False, **kw):
    """Учёный рилса 80: kind "a" | "b"; pose — "write" | "lean" | "point" | "rest" (или имя POSE); feet: None | "stand" | "sit" | dict."""
    who = "sci80a" if kind == "a" else "sci80b"
    pn = pose if pose in POSE else "sci_" + pose
    pk = pose_kw(pn, x, y, k, who)
    ex = dict(EXPR[who][expr]) if isinstance(expr, str) else dict(expr)
    ft = stand_kw(x, y, k, who)["feet"] if feet == "stand" else (sit_kw(x, y, k, who)["feet"] if feet == "sit" else feet)
    br = .01 * math.sin(t * 2 * math.pi / 3.1 + .4 + (1.3 if kind == "b" else 0))
    fig = figure(who, x, y, k, ex, lean=pk["lean"] + kw.pop("lean_add", 0.0) + br, head_ang=pk["head_ang"] + kw.pop("head_add", 0.0),
                 arms=dict(pk["arms"], **kw.pop("arms", {})), hands=dict(pk["hands"], **kw.pop("hands", {})), feet=ft, flip=flip, **kw)
    fig["hold"] = hand_pos(fig, "n", 70)
    fig["finger"] = hand_pos(fig, "n", 120)
    return fig


# ═════════════════════════════ РИЛС 81 «ВСЁ, ПОЗДНО» (автор — группа B) ═════════════════════════════
# Основа — common/people.py рилса 80 (всё прежнее байт в байт; у головы "cap" новый ключ expr["nocap"] — кепка снята).
# Дима (горчичное худи, лохматый, щетина) — dima81(x, y, k, expr, pose, t, ...) = dima80 взрослого: fig["hold"], fig["palm"], fig["chest"].
#   Позы POSE: d81_cup_up (ладони лодочкой над головой — ловит песок), d81_cup (ладони лодочкой у груди, пальцы чуть врозь — песок
#   сквозь пальцы), d81_drop (руки опущены, плечи вниз — засыпан), d81_rest (спокойно, руки вдоль тела), d81_knob (ближняя рука вперёд к
#   ручке двери; ручку даёт arms= / knob=), d81_push (обе ладони вперёд — толкает дверь), d81_phone (телефон у груди, экран к нему),
#   d81_bench (ладони на верстаке), d81_mast (ближняя рука вверх с мачтой, дальняя придерживает корпус), d81_laugh (петля: смеётся,
#   ладони чуть вверх). Переход — pose=(a, b), u.
#   Мимика EXPR["dima"]: panic81, dread81, sink81 (засыпан), screen81, sigh81 (вздох, отворачивается), wonder81 (видит дверь),
#   reach81 (берётся за ручку), hmph81 (хмыкает), work81, proud81, laugh81, smile81.
# dima_floor81(x, y, k, t, ...) — лежит на полу на спине (вид сверху / сбоку), голова слева (flip — справа), телефон над лицом экраном
#   к нему (glow — свет экрана), turn 0…1 — отворачивает голову и опускает телефон к груди, sit 0…1 — садится. (x, y) — таз в мире.
# Основатели (s11): founder81(kind, x, y, k, pose, t, ...) — kind "cap" (седая борода, кепка; cap_u 0…1 — снимает кепку: рука к
#   макушке и вверх, под ней седина), "glasses" (седой, прямоугольные очки, брюшко; pose "glasses" — поправляет очки),
#   "bald" (лысина с седой подковой, усы, очки для чтения полумесяцем, брюшко). Морщинки у глаз у всех. pose: "rest", "hips"
#   (руки в боки), "wave", "cap", "glasses", "fold" (руки на груди), "point" (показывает вдаль). feet: None | "stand" | dict.
# Юный позёр (s11–s13): youngster81(x, y, k, pose, t, ...) — гладкое лицо, худи (бирюзовое, не горчичное), поза "pose" (рука на бедре,
#   вторая вверх «козой» без жеста — открытая ладонь), "hooray" (обе руки вверх), "lean" (облокотился назад), "rest".
# Силуэты за матовым стеклом и прохожие: silhouette81(kind, x, y, k, t, phase, col, op, blur) — идущий человек одним цветом
#   (kind — who: "cap", "bald", "bob", "beard", "psych", "father", "girl", "youth"); passerby81(kind, x, y, k, t, phase, flip) — тот же
#   прохожий в цвете (шаг walk_kw; x двигает вызывающий).
# Кот (cat.py): cat_brush81(x, y, k, st, t) — кисточка в зубах, возвращает dict(svg, tip) — кончик кисти в мире; CAT_ST "proud81"
#   (задрал нос, глаза прикрыты), "nod81" (смотрит на зрителя, кивок — st["drop"] = cat_nod), "paws_up81" (обе передние лапы вверх —
#   упирается в перекладину часов), "paint81" (сосредоточен, смотрит вбок на рисунок). Прыжок — cat_jump (общий).
EXPR["dima"].update({
    "panic81": {"brows": "up", "mouth": "o", "open": .75, "lid": 1.0, "look": (.25, -.85)},
    "dread81": {"brows": "worry", "mouth": "o", "open": .35, "lid": .95, "look": (.4, .55)},
    "sink81": {"brows": "sad", "mouth": "tired", "lid": .42, "look": (.2, .8)},
    "screen81": {"brows": "tired", "mouth": "flat", "lid": .5, "look": (.55, -.15)},
    "sigh81": {"brows": "sad", "mouth": "o", "open": .2, "lid": .3, "look": (-.4, .3)},
    "wonder81": {"brows": "up", "mouth": "o", "open": .3, "lid": 1.0, "look": (.8, -.1), "bags": False},
    "reach81": {"brows": "det", "mouth": "pressed", "lid": .85, "look": (.8, .1), "bags": False},
    "hmph81": {"brows": "calm", "mouth": "smile", "smile": .35, "lid": .55, "look": (.5, .5), "bags": False},
    "work81": {"brows": "det", "mouth": "flat", "lid": .6, "look": (.6, .45), "bags": False},
    "proud81": {"brows": "calm", "mouth": "smile", "smile": 1.0, "lid": .6, "look": (.5, .1), "bags": False},
    "laugh81": {"brows": "up", "mouth": "grin", "open": .8, "lid": .45, "look": (.2, -.5), "bags": False},
    "smile81": {"brows": "calm", "mouth": "smile", "smile": .9, "lid": .7, "look": (.2, -.4), "bags": False},
})
_CUP = {"curl": (.38, .34, .34, .4), "spread": .02, "thumb": .45}
POSE.update({
    "d81_cup_up": (-0.06, -0.3, {"f": ("ik", (110, -640), -1), "n": ("ik", (215, -625), -1)},
                   {"f": dict(_CUP, dir=(.35, -1)), "n": dict(_CUP, dir=(-.25, -1))}),
    "d81_cup": (0.1, 0.32, {"f": ("ik", (220, -255), -1), "n": ("ik", (285, -245), -1)},
                {"f": dict(_CUP, dir=(1, -.15)), "n": dict(_CUP, dir=(1, -.05))}),
    "d81_cup_open": (0.1, 0.32, {"f": ("ik", (215, -250), -1), "n": ("ik", (290, -240), -1)},
                     {"f": {"dir": (1, -.1), "curl": (.12, .1, .12, .16), "spread": .55, "thumb": .2},
                      "n": {"dir": (1, 0), "curl": (.12, .1, .12, .16), "spread": .55, "thumb": .2}}),
    "d81_drop": (0.24, 0.48, {"f": ("ang", 0.42, 0.08), "n": ("ang", 0.34, 0.1)},
                 {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.4, .4, .45, .5), "thumb": .4}}),
    "d81_rest": (0.0, 0.0, {"f": ("ang", 0.16, 0.16), "n": ("ang", -0.08, 0.22)},
                 {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": {"curl": (.35, .35, .4, .45), "thumb": .35}}),
    "d81_knob": (0.12, 0.05, {"f": ("ang", 0.2, 0.2), "n": ("ik", (330, -200), -1)},
                 {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": dict(_GRIP, dir=(1, .15))}),
    "d81_push": (0.2, 0.05, {"f": ("ik", (330, -330), -1), "n": ("ik", (390, -300), -1)},
                 {"f": {"dir": (.15, -1), "curl": (.05, .05, .08, .1), "spread": .2, "thumb": .2},
                  "n": {"dir": (.1, -1), "curl": (.05, .05, .08, .1), "spread": .2, "thumb": .2}}),
    "d81_phone": (0.06, 0.32, {"f": ("ik", (190, -290), -1), "n": ("ik", (230, -270), -1)},
                  {"f": dict(_PH_HOLD_F), "n": dict(_PH_HOLD_N)}),
    "d81_bench": (0.22, 0.3, {"f": ("ik", (250, -60), -1), "n": ("ik", (330, -50), -1)},
                  {"f": {"dir": (1, .3), "curl": (.3, .3, .35, .4), "thumb": .3}, "n": dict(_GRIP, dir=(1, .4))}),
    "d81_mast": (0.16, 0.05, {"f": ("ik", (260, -90), -1), "n": ("ik", (330, -330), -1)},
                 {"f": {"dir": (1, .3), "curl": (.3, .3, .35, .4), "thumb": .3}, "n": dict(_GRIP, dir=(.2, -1))}),
    "d81_laugh": (-0.08, -0.25, {"f": ("ik", (170, -300), -1), "n": ("ik", (260, -330), -1)},
                  {"f": {"dir": (.6, -.8), "curl": (.15, .1, .15, .2), "spread": .3, "thumb": .2},
                   "n": {"dir": (.5, -.85), "curl": (.15, .1, .15, .2), "spread": .3, "thumb": .2}}),
})


def dima81(x, y, k, expr="unsure", pose="d81_rest", t=0.0, u=1.0, feet=None, flip=False, **kw):
    """Взрослый Дима рилса 81 (= dima80 с age=1). pose — имя или (a, b) с переходом u. feet: None (по пояс) | "stand" | dict."""
    return dima80(x, y, k, expr, pose, t=t, u=u, age=1.0, feet=feet, flip=flip, **kw)


def dima_floor81(x, y, k, t=0.0, expr=None, glow=1.0, turn=0.0, sit=0.0, phone=True, flip=False, knees=1.0, seed=0, blink=0.0):
    """Дима на полу на спине, голова слева. turn 0…1 — отворачивает голову к зрителю-низу и роняет телефон к груди; sit 0…1 — садится
    (корпус поднимается от пола до вертикали, ноги остаются). Телефон экраном к нему. Возвращает dict(svg, head, phone, scale)."""
    sc = k * HEIGHT["dima"]
    turn, sit = lib.clamp(turn), lib.clamp(sit)
    a_body = -90.0 + 90.0 * lib.ease_io(sit)          # −90: лежит головой влево; 0: сидит
    br = .02 * math.sin(t * 2 * math.pi / 4.0)
    ph_up = np.array([300.0, -430.0]) * sc
    ph_dn = np.array([210.0, -250.0]) * sc
    pc = ph_up + (ph_dn - ph_up) * lib.ease_io(turn)
    if sit > .01:
        pc = pc + (np.array([230.0, -260.0]) * sc - pc) * lib.ease_io(sit)
    hold_h = {"dir": (.5, -1), "curl": (.62, .66, .7, .74), "thumb": .55}
    hands = {"f": dict(hold_h, dir=(.9, -.2)), "n": dict(hold_h)}
    arms = {"f": ("ik", (float(pc[0] - 30 * sc), float(pc[1] + 50 * sc)), -1), "n": ("ik", (float(pc[0] - 10 * sc), float(pc[1] + 70 * sc)), -1)}
    if not phone:
        arms = {"f": ("ang", .5, .2), "n": ("ang", .3, .25)}
        hands = {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.4, .4, .45, .5), "thumb": .4}}
    if expr is None:
        expr = "screen81" if turn < .5 else "sigh81"
    ex = dict(EXPR["dima"].get(expr, {})) if isinstance(expr, str) else dict(expr)
    if blink > .01:
        ex = dict(ex, lid=ex.get("lid", .8) * (1 - blink))
    ha = .25 - .45 * lib.ease_io(turn) + .1 * sit
    # ноги в «стоячей» системе: колени согнуты (ступни на полу ближе к тазу), knees 0 — прямые
    kz = lib.clamp(knees)
    ground = (LEG_LEN - 12) * sc
    if sit > .5:
        feet = sit_kw(0, 0, sc / HEIGHT["dima"])["feet"]
    else:
        feet = {"n": ((float(260 * sc * kz + 40 * sc), float(ground - 230 * sc * kz)), 1.57 * kz),
                "f": ((float(220 * sc * kz + 10 * sc), float(ground - 210 * sc * kz)), 1.57 * kz)}
    body = figure("dima", 0.0, 0.0, k, ex, lean=br, head_ang=ha, arms=arms, hands=hands, feet=feet, layers=("legs", "pelvis", "arm_f", "body"))
    arm_n = figure("dima", 0.0, 0.0, k, ex, lean=br, head_ang=ha, arms=arms, hands=hands, feet=feet, layers=("arm_n",))
    tb = f'translate({x:.2f} {y:.2f}) rotate({a_body:.2f})'
    o = [f'<g transform="{tb}">{body["svg"]}</g>']
    phone_w = None
    if phone:
        wn, wf = np.array(arm_n["wrist"]["n"]), np.array(body["wrist"]["f"])
        c = (wn + wf) / 2 + np.array([46, -20]) * sc
        hx, hy = body["head"]
        g = lib.clamp(glow)
        if g > .01:
            fl = 1 + .06 * math.sin(t * 11.0) + .04 * math.sin(t * 23.0)
            o.append(f'<g transform="{tb}">' + blob([(c[0] - 10 * sc, c[1] - 90 * sc), (c[0] - 10 * sc, c[1] + 90 * sc), (hx + 60 * sc, hy + 110 * sc),
                                                       (hx + 40 * sc, hy - 120 * sc)], "#cfe6ff", .16 * g * fl) + "</g>")
        o.append(f'<g transform="{tb}">{mobilnik(float(c[0]), float(c[1]), 1.5 * sc, 0, seed=8151 + seed)}</g>')
        if g > .01:
            gid = lib.rad_grad([(0, "#d6ecff", .4 * g * fl), (.6, "#bfe0ff", .15 * g * fl), (1, "#bfe0ff", 0)], hx + 60 * sc, hy + 10 * sc, 170 * sc)
            o.append(f'<g transform="{tb}"><circle cx="{hx + 60 * sc:.1f}" cy="{hy + 10 * sc:.1f}" r="{170 * sc:.1f}" fill="url(#{gid})"/></g>')
        phone_w = _rot81((float(c[0]), float(c[1])), a_body, x, y)
    o.append(f'<g transform="{tb}">{arm_n["svg"]}</g>')
    svg_ = "".join(o)
    head_w = _rot81(body["head"], a_body, x, y)
    if flip:
        svg_ = f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{svg_}</g>'
        head_w = (2 * x - head_w[0], head_w[1])
        phone_w = None if phone_w is None else (2 * x - phone_w[0], phone_w[1])
    return dict(svg=svg_, head=head_w, phone=phone_w, scale=sc, body_angle=a_body)


def _rot81(p, a, x, y):
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    return (x + p[0] * ca - p[1] * sa, y + p[0] * sa + p[1] * ca)


# ─── основатели (без имён, не портреты): седина, очки, брюшко, морщинки ───
PAL["fnd_cap"] = dict(PAL["cap"], HAIR="#cfccd4", HAIR_SH="#9d99a6", HAIR_HI="#efedf2", CAP="#2f5f8a", CAP_SH="#1f4466", SKIN="#e9bf9c",
                      SKIN_SH="#cf9c7c", SKIN_SH2="#b8846a", TOP="#b5463a", TOP_SH="#8e342b", TOP_SH2="#6c261f", FOLD="#4a1913", STITCH="#f0d7b0",
                      PLAID="#2c3e5c", PLAID2="#efe3c8", LEGS="#4b5a74", LEGS_SH="#36425a", LEGS_SEAM="#6a7a96")
PAL["fnd_glasses"] = dict(PAL["psych"])
PAL["fnd_bald"] = dict(PAL["father"], TOP="#5f7f6a", TOP_SH="#47614f", TOP_SH2="#36493c", FOLD="#26352b", STITCH="#c9d8b8")
for _k in ("FRAME",):
    PAL["fnd_bald"].setdefault(_k, "#3a2c2c")
    PAL["fnd_glasses"].setdefault(_k, "#2a2a32")
HEIGHT.update({"fnd_cap": 1.02, "fnd_glasses": 1.0, "fnd_bald": .98, "yng81": 1.0})
HEADS64 = HEADS64 + ("fnd_cap", "fnd_glasses", "fnd_bald", "yng81")
FRIENDLIKE = FRIENDLIKE + ("fnd_cap", "fnd_glasses", "fnd_bald", "yng81")
FACES = FACES + ("fnd_cap", "fnd_glasses", "fnd_bald", "yng81")
CLOTHES64["fnd_cap"] = plaid_parts
CLOTHES64["fnd_glasses"] = corduroy_parts
CLOTHES64["fnd_bald"] = knit_cardigan_parts
# юный позёр: бирюзовое худи (не горчичное, как у Димы), гладкое лицо, тёмная короткая стрижка
PAL["yng81"] = dict(PAL["youth"], SKIN="#efc6a4", SKIN_SH="#d6a384", SKIN_SH2="#bf8c6e", HAIR="#2a1f1c", HAIR_SH="#160f0d", HAIR_HI="#4a3a34",
                    TOP="#2fb3a6", TOP_SH="#238a80", TOP_SH2="#1a6a62", FOLD="#124a45", LEGS="#2c2f3a", LEGS_SH="#1d1f27", LEGS_SEAM="#4a4e5e",
                    SHOE="#f4f1ea", SHOE_SH="#cfcbbf", SOLE="#f4f1ea", SOLE_SH="#cfcbbf", STRIPE="#e94f6a", NAIL="#f1cdbd")
CLOTHES64["yng81"] = hoodie_parts
_FEXPR = {"calm": {"brows": "calm", "mouth": "smile", "smile": .55, "lid": .7, "look": (.3, .1)},
          "warm": {"brows": "calm", "mouth": "smile", "smile": 1.0, "lid": .55, "look": (.2, 0)},
          "focus": {"brows": "calm", "mouth": "flat", "lid": .65, "look": (.5, .5)},
          "wink": {"brows": "up", "mouth": "smile", "smile": .8, "lid": .8, "look": (0, 0)}}
for _w in ("fnd_cap", "fnd_glasses", "fnd_bald"):
    EXPR[_w] = {k_: dict(v_) for k_, v_ in _FEXPR.items()}
EXPR["yng81"] = {"cool": {"brows": "calm", "mouth": "smile", "smile": .7, "lid": .6, "look": (.4, 0)},
                 "shout": {"brows": "up", "mouth": "o", "open": .7, "lid": 1.0, "look": (.2, -.3)},
                 "grin": {"brows": "up", "mouth": "smile", "smile": 1.0, "lid": .85, "look": (0, 0)}}
POSE.update({
    "f81_rest": (0.0, 0.0, {"f": ("ang", 0.16, 0.16), "n": ("ang", -0.08, 0.22)},
                 {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": {"curl": (.35, .35, .4, .45), "thumb": .35}}),
    "f81_hips": (-0.04, 0.0, {"f": ("ik", (60, -150), 1), "n": ("ik", (110, -130), 1)},
                 {"f": {"dir": (.3, 1), "curl": (.5, .5, .55, .6), "thumb": .4}, "n": {"dir": (-.2, 1), "curl": (.5, .5, .55, .6), "thumb": .4}}),
    "f81_wave": (0.0, -0.05, {"f": ("ang", 0.16, 0.16), "n": ("ik", (260, -560), -1)},
                 {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": {"dir": (.2, -1), "curl": (.05, .05, .08, .1), "spread": .35, "thumb": .1}}),
    "f81_cap": (0.0, -0.1, {"f": ("ang", 0.16, 0.16), "n": ("ik", (150, -640), -1)},
                {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": dict(_GRIP, dir=(-.2, -1))}),
    "f81_cap_up": (0.0, -0.12, {"f": ("ang", 0.16, 0.16), "n": ("ik", (260, -700), -1)},
                   {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": dict(_GRIP, dir=(.2, -1))}),
    "f81_glasses": (0.02, -0.05, {"f": ("ang", 0.16, 0.16), "n": ("ik", (165, -455), -1)},
                    {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": {"dir": (-.2, -1), "curl": (.75, 0.0, .85, .9), "thumb": .7}}),
    "f81_fold": (-0.04, 0.0, {"f": ("ik", (120, -250), -1), "n": ("ik", (-60, -250), 1)}, {"f": {"kind": "none"}, "n": {"kind": "none"}}),
    "f81_point": (0.04, -0.1, {"f": ("ang", 0.16, 0.16), "n": ("ik", (420, -420), -1)},
                  {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": {"dir": (1, -.3), "curl": (0, .85, .9, .9), "spread": .05, "thumb": .7}}),
    "y81_pose": (-0.06, -0.1, {"f": ("ik", (60, -150), 1), "n": ("ik", (220, -620), -1)},
                 {"f": {"dir": (.3, 1), "curl": (.5, .5, .55, .6), "thumb": .4}, "n": {"dir": (.2, -1), "curl": (.05, .05, .08, .1), "spread": .4, "thumb": .1}}),
    "y81_hooray": (-0.1, -0.2, {"f": ("ik", (60, -640), -1), "n": ("ik", (250, -640), -1)},
                   {"f": {"dir": (-.1, -1), "curl": (.05, .05, .08, .1), "spread": .4, "thumb": .1},
                    "n": {"dir": (.2, -1), "curl": (.05, .05, .08, .1), "spread": .4, "thumb": .1}}),
    "y81_lean": (-0.14, -0.05, {"f": ("ik", (-150, -40), -1), "n": ("ik", (-60, -60), -1)},
                 {"f": {"dir": (-.3, 1), "curl": (.2, .2, .25, .3), "thumb": .3}, "n": {"dir": (-.2, 1), "curl": (.2, .2, .25, .3), "thumb": .3}}),
})
_head64_orig81 = head64


def _reading_glasses81(col="#3a2c2c", sd=8120):
    """Очки для чтения полумесяцем: низко на носу, верх оправы прямой (глаза над ней видны)."""
    o = ""
    for (cx_, cy_, rx_, ry_, s_) in ((16, 4, 46, 26, sd), (92, 6, 34, 24, sd + 1)):
        pts = [(cx_ - rx_, cy_ - ry_ * .2)] + [(cx_ + rx_ * math.cos(a), cy_ + ry_ * math.sin(a)) for a in np.linspace(math.pi, 0, 12)] + \
              [(cx_ + rx_, cy_ - ry_ * .2)]
        o += line(pts + [pts[0]], 4.6, col, taper=0, wmin=1, seed=s_)
        o += line([(cx_ - rx_ * .5, cy_ + ry_ * .35), (cx_ - rx_ * .1, cy_ + ry_ * .6)], 2.4, "#ffffff", seed=s_ + 4, op=.5)
    o += line([(62, 2), (58, 4)], 4.2, col, seed=sd + 2)
    o += line([(-30, 0), (-86, -20)], 3.6, col, seed=sd + 3)
    return o


def head64(expr, style):        # noqa: F811 — плюс основатели и юный позёр рилса 81
    if style == "fnd_cap":
        return person_head(expr, "cap") + _wrinkles64(True, True, 1, sd=8130, op=.75)
    if style == "fnd_glasses":
        return _head64_orig81(expr, "psych") + _wrinkles64(True, True, 2, sd=8131, op=.8)
    if style == "fnd_bald":
        return _head64_orig81(expr, "father") + _wrinkles64(True, True, 2, sd=8132, op=.8) + _reading_glasses81(C.get("FRAME", "#3a2c2c"))
    if style == "yng81":
        return _head64_orig81(expr, "youth")
    return _head64_orig81(expr, style)


def cap81(x, y, k=1.0, rot=0.0, col=None, seed=0):
    """Кепка отдельно (снятая, в руке): купол и козырёк вправо; (x, y) — середина низа купола, k — масштаб головы (sc)."""
    c0, c1 = col or (PAL["fnd_cap"]["CAP"], PAL["fnd_cap"]["CAP_SH"])
    crown = [(-110, 0), (-112, -50), (-70, -104), (0, -122), (66, -106), (104, -60), (112, -10), (60, 2), (-30, -4)]
    ci = blob([(-130, -140), (-10, -140), (-40, -30), (-120, 10)], c1, .85) + line([(-4, -120), (-12, -60), (-30, -8)], 2.2, c1, seed=8141, op=.9)
    o = shape(crown, c0, ci + f'<circle cx="0" cy="-122" r="9" fill="{c1}"/>', w=5.2, seed=8140 + seed)
    o += shape([(80, -12), (150, -16), (214, 0), (222, 16), (180, 30), (96, 20)], c0, blob([(90, 18), (222, 16), (180, 30), (96, 28)], c1, .9), w=5.0,
               seed=8142 + seed)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{o}</g>'


def _belly81(fig_x, fig_y, sc, lean, col_top, col_sh, size=1.0, seed=0):
    """Брюшко поверх свитера: мягкий выступ вперёд над поясом (в системе фигуры, смотрит вправо)."""
    up = rot(np.array([0.0, -1.0]), lean)
    fw = rot(np.array([1.0, 0.0]), lean)
    c = np.array([fig_x, fig_y]) + (up * 120 + fw * 92) * sc
    pts = [tuple(c + (fw * (math.cos(a) * 92 * size) + up * (math.sin(a) * 122)) * sc) for a in np.linspace(-math.pi / 2, math.pi / 2, 12)]
    pts = [tuple(c + (up * 150 - fw * 40) * sc)] + pts + [tuple(c + (-up * 140 - fw * 40) * sc)]
    inner = blob([tuple(c + (fw * 40 - up * 40) * sc), tuple(c + (fw * 96 * size - up * 10) * sc), tuple(c + (fw * 70 - up * 130) * sc),
                  tuple(c - (up * 140) * sc)], col_sh, .7)
    return shape(pts, col_top, inner, w=5.0 * sc / .4 * .4, seed=8150 + seed)


def founder81(kind, x, y, k, pose="rest", t=0.0, expr="calm", feet=None, flip=False, cap_u=0.0, belly=1.0, u=1.0, **kw):
    """Основатель рилса 81 (см. шапку раздела). cap_u 0…1 у kind="cap": 0 — кепка на голове, .5 — рука у макушки, 1 — кепка поднята
    над головой в руке, на голове седина. Возвращает dict фигуры + "cap" — центр кепки в мире (если снята)."""
    who = "fnd_" + kind
    sc = k * HEIGHT[who]
    if kind == "cap" and cap_u > 0:
        cu = lib.clamp(cap_u)
        pk = mix_pose("f81_rest", "f81_cap", min(1.0, cu * 2), x, y, k, who) if cu < .5 else mix_pose("f81_cap", "f81_cap_up", (cu - .5) * 2, x, y, k, who)
    elif isinstance(pose, (tuple, list)):
        pk = mix_pose("f81_" + pose[0], "f81_" + pose[1], u, x, y, k, who)
    else:
        pk = pose_kw("f81_" + pose, x, y, k, who)
    ex = dict(EXPR[who][expr]) if isinstance(expr, str) else dict(expr)
    if kind == "cap" and cap_u > .5:
        ex["nocap"] = True
    ft = stand_kw(x, y, k, who)["feet"] if feet == "stand" else feet
    br = .012 * math.sin(t * 2 * math.pi / 3.2 + len(kind))
    lean = pk["lean"] + kw.pop("lean_add", 0.0) + br
    common = dict(lean=lean, head_ang=pk["head_ang"] + kw.pop("head_add", 0.0), arms=dict(pk["arms"], **kw.pop("arms", {})),
                  hands=dict(pk["hands"], **kw.pop("hands", {})), feet=ft)
    back = figure(who, x, y, k, ex, layers=("legs", "pelvis", "arm_f", "body"), **common)
    front = figure(who, x, y, k, ex, layers=("arm_n",), **common)
    mid = ""
    if kind in ("glasses", "bald") and belly > 0:
        pal = PAL[who]
        mid = _belly81(x, y, sc, lean, pal["TOP"], pal["TOP_SH"], belly, seed=len(kind))
    cap_c = None
    cap_svg = ""
    if kind == "cap" and cap_u > .5:
        w = np.array(front["wrist"]["n"])
        cap_c = (float(w[0] + 10 * sc), float(w[1] - 40 * sc))
        cap_svg = cap81(cap_c[0], cap_c[1] + 60 * sc, sc, rot=-12 + 20 * (1 - lib.clamp((cap_u - .5) * 2)))
    svg_ = back["svg"] + mid + cap_svg + front["svg"] if cap_svg else back["svg"] + mid + front["svg"]
    if flip:
        svg_ = f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{svg_}</g>'
    res = dict(back)
    res["svg"] = svg_
    fl = (lambda p: (2 * x - p[0], p[1])) if flip else (lambda p: p)
    res["head"] = fl(back["head"])
    res["wrist"] = {s_: fl(front["wrist"][s_]) for s_ in front["wrist"]}
    res["cap"] = None if cap_c is None else fl(cap_c)
    res["scale"] = sc
    return res


def youngster81(x, y, k, pose="pose", t=0.0, expr="cool", feet="stand", flip=False, u=1.0, **kw):
    """Юный позёр: гладкое лицо, бирюзовое худи. pose — "pose" | "hooray" | "lean" | "rest" или (a, b) с переходом u."""
    who = "yng81"
    if isinstance(pose, (tuple, list)):
        pk = mix_pose("y81_" + pose[0] if pose[0] != "rest" else "f81_rest", "y81_" + pose[1] if pose[1] != "rest" else "f81_rest", u, x, y, k, who)
    else:
        pk = pose_kw("y81_" + pose if pose != "rest" else "f81_rest", x, y, k, who)
    ex = dict(EXPR[who][expr]) if isinstance(expr, str) else dict(expr)
    ex["bags"] = False
    ft = stand_kw(x, y, k, who)["feet"] if feet == "stand" else feet
    br = .012 * math.sin(t * 2 * math.pi / 2.6)
    return figure(who, x, y, k, ex, lean=pk["lean"] + kw.pop("lean_add", 0.0) + br, head_ang=pk["head_ang"] + kw.pop("head_add", 0.0),
                  arms=dict(pk["arms"], **kw.pop("arms", {})), hands=dict(pk["hands"], **kw.pop("hands", {})), feet=ft, flip=flip, **kw)


def _walker81(kind, x, y, k, t, phase, flip):
    wk = walk_kw(x, y, k, phase, kind)
    sw = math.sin(2 * math.pi * phase)
    arms = {"f": ("ang", 0.18 + .35 * sw, 0.2), "n": ("ang", -0.1 - .35 * sw, 0.25)}
    hands = {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.4, .4, .45, .5), "thumb": .4}}
    ex = dict(EXPR.get(kind, {}).get("calm", {"brows": "calm", "mouth": "flat", "lid": .7}))
    return figure(kind, wk["hip"][0], wk["hip"][1], k, ex, lean=.05, arms=arms, hands=hands, feet=wk["feet"], flip=flip)


def silhouette81(kind, x, y, k, t=0.0, phase=0.0, col="#5a3e2a", op=.55, blur=6.0, flip=False):
    """Идущий человек одним цветом (за матовым стеклом): без лица, контур размыт."""
    fig = _walker81(kind, x, y, k, t, phase, flip)
    return dict(svg=_silhouette(fig["svg"], col, op, blur), head=fig["head"], scale=fig["scale"])


def passerby81(kind, x, y, k, t=0.0, phase=0.0, flip=False):
    """Прохожий в цвете: шаг на месте (x двигает вызывающий)."""
    return _walker81(kind, x, y, k, t, phase, flip)


# ─── кот рилса 81 ───
CAT_ST.update({
    "proud81": {"tilt": -9, "look": (.15, -.8), "blink": .45, "smile": 1.0, "flame_e": 1.5, "perk": .6},
    "nod81": {"look": (0, .1), "smile": 1.0, "flame_e": 1.3},
    "paws_up81": {"paw": 1.0, "paw_l": 1.0, "paw_dx": 18, "paw_l_dx": 18, "perk": 1.0, "look": (0, -.6), "smile": 1.0},
    "paint81": {"look": (.85, .15), "turn": .35, "flame_e": 1.3, "perk": .4},
})
BRUSH81_K = 1.15


def cat_brush81(x, y, k, st=None, t=0.0, brush_rot=-8.0, col="#D9483B"):
    """Кот с кисточкой в зубах (лапы на полу). Кисть поперёк рта, щетиной вправо от зрителя. Возвращает dict(svg, tip) — кончик в мире."""
    import cat
    import props as _P
    st = dict(CAT_ST["paint81"], **(st or {}))
    FX = 22 * st.get("turn", 0.0)
    mx, my = 836 + FX + 30, 1128
    st["mouth_item"] = _P.paint_brush(mx, my, BRUSH81_K, brush_rot, col=col)
    svg_ = cat_svg(x, y, k, st, t)
    a = math.radians(brush_rot)
    tx, ty = mx + 106 * BRUSH81_K * math.cos(a), my + 106 * BRUSH81_K * math.sin(a)
    # голова: наклон tilt вокруг шеи и опускание drop (как в cat.draw)
    tl = math.radians(st.get("tilt", 0.0))
    nx, ny = cat.NECK
    rx, ry = tx - nx, ty - ny
    tx, ty = nx + rx * math.cos(tl) - ry * math.sin(tl), ny + rx * math.sin(tl) + ry * math.cos(tl) + 70 * st.get("drop", 0.0)
    rr = math.radians(st.get("rot", 0.0))
    dx, dy = (tx - cat.CX) * k, (ty - cat.CBOT) * k
    return dict(svg=svg_, tip=(x + dx * math.cos(rr) - dy * math.sin(rr), y + dx * math.sin(rr) + dy * math.cos(rr)))
