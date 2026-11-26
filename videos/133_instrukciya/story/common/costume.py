"""Костюмы кота рилсов 133, 135, 136 (владелец 26.11: «логично… без артефактов»). Всё — в координатах рисунка кота (cat.py:
CX 836, туловище 744…928 × 1142…1296, шея 1146, глаза 1072 ± 38, лоб ≈ 990…1030) и кладётся в cat.WEAR, поэтому одежда
рисуется внутри групп кота: сжимается с телом, наклоняется с головой, предмет идёт за правой лапой. Ничего не заходит на
глаза и морду (ниже 1034 по голове не рисуется), лапы кота лежат поверх одежды.
    import costume; costume.use("overalls")   # спецовка (133) | "host" — жилетка ведущего и ключ (135) | "sport" (136)
"""
import math

import cat as CT
import lib
from ink import band, ellipse_pts
from lib import blob, line, shape

STITCH = "#f2b04a"


def _dash(p0, p1, col=STITCH, n=6, w=2.2, seed=0):
    o = ""
    for i in range(n):
        a, b = i / n, (i + .55) / n
        o += line([(p0[0] + (p1[0] - p0[0]) * a, p0[1] + (p1[1] - p0[1]) * a), (p0[0] + (p1[0] - p0[0]) * b, p0[1] + (p1[1] - p0[1]) * b)],
                  w, col, taper=0, wmin=1, seed=seed + i)
    return o


# ═════════════ 133: спецовка (комбинезон с нагрудником) и гаечный ключ в кармане ═════════════
DEN, DEN_SH, DEN_D = "#3f73b8", "#2f5c98", "#24497c"


def wrench_pts(x, y, k=1.0, rot=0.0):
    """Гаечный ключ: рукоять и зев сверху (центр низа рукояти — (x, y))."""
    body_ = [(-7, 0), (-7, -64), (-17, -72), (-19, -90, 1), (-8, -96, 1), (-6, -84), (6, -84), (8, -96, 1), (19, -90, 1), (17, -72), (7, -64), (7, 0)]
    return lib.T(body_, x, y, k, rot)


def overalls_body():
    o = []
    pts = [(794, 1166, 1), (878, 1166, 1), (884, 1224), (916, 1222), (922, 1250), (906, 1300, 1), (766, 1300, 1), (750, 1250), (756, 1222),
           (788, 1224)]
    inner = blob([(850, 1166), (884, 1224), (922, 1250), (906, 1300), (860, 1300), (880, 1240)], DEN_SH, .8)
    inner += line([(836, 1262), (836, 1300)], 2.6, DEN_D, seed=5301)                      # шов штанин
    inner += _dash((796, 1176), (876, 1176), seed=5310) + _dash((758, 1232), (914, 1232), n=9, seed=5320)
    inner += shape(lib.rect_pts(812, 1188, 860, 1216), DEN_SH, _dash((814, 1194), (858, 1194), n=4, seed=5330), w=2.6, seed=5302)   # карман
    o.append(shape(pts, DEN, inner, w=4.2, seed=5300))
    for sx in (-1, 1):                                                                    # лямки к плечам (под голову)
        x0 = 836 + sx * 36
        o.append(shape([(x0 - 9, 1172, 1), (x0 + 9, 1172, 1), (x0 + 6 + sx * 4, 1136, 1), (x0 - 10 + sx * 4, 1136, 1)], DEN_D, "", w=3, seed=5306 + sx))
        o.append(shape(ellipse_pts(x0, 1176, 7.5, 7.5, 10), "#f2c14e", "", w=2.4, seed=5308 + sx))
    return "".join(o)


# ═════════════ 135: жилетка ведущего и большой ключ ═════════════
VEST, VEST_SH = "#9c2a3a", "#7a1d2b"
GOLD, GOLD_SH = "#f2c14e", "#c8952a"


def vest_body():
    o = []
    for sx, sd in ((-1, 5400), (1, 5410)):
        # полочка жилетки: от плеча вниз до края тела, вырез мысом к середине
        pts = [(836 + sx * 46, 1140, 1), (836 + sx * 80, 1160), (836 + sx * 92, 1220), (836 + sx * 88, 1286, 1), (836 + sx * 10, 1292, 1),
               (836 + sx * 4, 1236, 1), (836 + sx * 22, 1176)]
        inner = blob([(836 + sx * 60, 1150), (836 + sx * 92, 1220), (836 + sx * 88, 1286), (836 + sx * 66, 1286), (836 + sx * 70, 1200)], VEST_SH, .8)
        inner += line([(836 + sx * 30, 1250), (836 + sx * 70, 1250)], 3, VEST_SH, seed=sd + 1)       # прорезной карман
        o.append(shape(pts, VEST, inner, w=4.2, seed=sd))
    for j in range(3):
        o.append(shape(ellipse_pts(826, 1212 + 26 * j, 6.5, 6.5, 10), GOLD, "", w=2.2, seed=5420 + j))
    # бабочка у шеи
    o.append(shape([(836, 1150, 1), (806, 1134, 1), (806, 1166, 1)], "#1f2430", "", w=2.6, seed=5430))
    o.append(shape([(836, 1150, 1), (866, 1134, 1), (866, 1166, 1)], "#1f2430", "", w=2.6, seed=5431))
    o.append(shape(ellipse_pts(836, 1150, 8, 8, 10), "#3a4150", "", w=2.4, seed=5432))
    return "".join(o)


def key_pts():
    """Большой старинный ключ (локально: кольцо вверху, стержень вниз, бородка внизу справа)."""
    return None


def big_key(x, y, k=1.0, rot=0.0, glow=0.0, sd=5440):
    """Ключ: (x, y) — точка хвата (середина стержня под кольцом), длина ~170·k вниз."""
    o = ""
    if glow > 0:
        o += f'<circle cx="0" cy="40" r="120" fill="#fff1a8" opacity="{.45 * glow:.3f}"/>'
    o += shape(lib.rect_pts(-8, -10, 8, 150), GOLD, blob(lib.rect_pts(2, -10, 8, 150), GOLD_SH, .7), w=3.4, seed=sd)
    o += shape([(8, 106, 1), (40, 106, 1), (40, 122, 1), (28, 122, 1), (28, 134, 1), (40, 134, 1), (40, 150, 1), (8, 150, 1)], GOLD,
               "", w=3.4, seed=sd + 1)
    ring_o = ellipse_pts(0, -48, 40, 40, 22)
    o += shape(ring_o, GOLD, blob(ellipse_pts(12, -40, 26, 30, 14), GOLD_SH, .6) + shape(ellipse_pts(0, -48, 18, 18, 16), "#7a5a1e", "", w=2.6,
                                                                                         seed=sd + 2), w=3.6, seed=sd + 3)
    o += line([(-14, -70), (-24, -50)], 3, "#fff6d0", seed=sd + 4, op=.8)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{o}</g>'


KEY_STATE = {"rot": 200.0, "up": 182.0, "glow": 0.0}


def key_hold(tip, raised):
    """Ключ в правой лапе: лапа держит кольцо, стержень и бородка смотрят вверх (у плеча); поднята лапа — ключ поднят прямо вверх."""
    rot = KEY_STATE["rot"] * (1 - raised) + KEY_STATE["up"] * raised
    k = .62
    return (f'<g transform="translate({tip[0] + 4:.2f} {tip[1] - 8:.2f}) rotate({rot:.2f}) scale({k}) translate(0 48)">'
            f'{big_key(0, 0, 1.0, 0.0, KEY_STATE["glow"])}</g>')


# ═════════════ 136: спортивный костюм, повязка, свисток, полотенце ═════════════
SUIT, SUIT_SH = "#d8352a", "#a8251c"
STRIPE = "#ffffff"


def sport_body():
    o = []
    pts = [(790, 1142), (882, 1142), (918, 1180), (930, 1240), (914, 1298, 1), (758, 1298, 1), (742, 1240), (754, 1180)]
    inner = blob([(860, 1140), (930, 1180), (930, 1300), (874, 1300), (888, 1220)], SUIT_SH, .85)
    inner += line([(836, 1160), (836, 1296)], 3.4, "#7a1a14", seed=5501)                         # молния
    inner += blob(ellipse_pts(836, 1206, 5, 8, 8), "#d9d9d9")
    inner += blob(lib.rect_pts(750, 1272, 922, 1298), SUIT_SH)                                       # резинка
    inner += line([(752, 1272), (920, 1272)], 2.4, "#7a1a14", seed=5502)
    for sx in (-1, 1):                                                                             # белые полосы по бокам
        inner += line([(836 + sx * 84, 1176), (836 + sx * 94, 1240), (836 + sx * 84, 1294)], 6, STRIPE, taper=0, wmin=1, seed=5503 + sx)
    o.append(shape(pts, SUIT, inner, w=4.4, seed=5500))
    # воротник-стойка
    for sx in (-1, 1):
        o.append(shape([(836 + sx * 4, 1150, 1), (836 + sx * 50, 1138, 1), (836 + sx * 46, 1166, 1), (836 + sx * 6, 1174, 1)], SUIT, "", w=3,
                       seed=5506 + sx))
    # полотенце на шее: петля за шеей и два конца на груди
    for sx, sd in ((-1, 5510), (1, 5512)):
        tw = [(836 + sx * 58, 1132, 1), (836 + sx * 30, 1136), (836 + sx * 22, 1214), (836 + sx * 30, 1226, 1), (836 + sx * 58, 1222, 1), (836 + sx * 64, 1170)]
        tin = line([(836 + sx * 26, 1206), (836 + sx * 60, 1204)], 4, "#5aa8e0", seed=sd + 1) + line([(836 + sx * 25, 1196), (836 + sx * 61, 1194)], 2, "#5aa8e0",
                                                                                                      seed=sd + 2)
        tin += blob([(836 + sx * 50, 1140), (836 + sx * 64, 1170), (836 + sx * 58, 1222), (836 + sx * 46, 1222)], "#d9dee6", .7)
        o.append(shape(tw, "#f6f7fb", tin, w=3.4, seed=sd))
    # свисток на шнурке
    o.append(line([(816, 1150), (826, 1180), (836, 1204)], 2.4, "#2a2a2a", seed=5520))
    o.append(line([(856, 1150), (846, 1180), (836, 1204)], 2.4, "#2a2a2a", seed=5521))
    wh = [(818, 1206, 1), (852, 1206), (862, 1218), (852, 1230), (818, 1230, 1)]
    o.append(shape(wh, "#c9ced6", blob([(826, 1210), (848, 1210), (850, 1218), (826, 1218)], "#f2f4f7", .8) + blob(ellipse_pts(846, 1220, 5, 4, 8), "#4a4f58"),
                   w=2.8, seed=5522))
    o.append(shape(lib.rect_pts(808, 1210, 820, 1226), "#c9ced6", "", w=2.6, seed=5523))
    return "".join(o)


def sport_sleeve(kind, pts, sx):
    """Рукав олимпийки на передней лапе: на стоячей — от груди до запястья, на поднятой — плечо и локоть."""
    if kind == "leg":
        (fx, y0), (_, b) = pts
        y1 = y0 + (b - y0) * .45
        p = [(fx - 21, y0 - 6, 1), (fx + 21, y0 - 6, 1), (fx + 21, y1, 1), (fx - 21, y1, 1)]
        inner = line([(fx + sx * 12, y0), (fx + sx * 12, y1 - 2)], 4.4, STRIPE, taper=0, wmin=1, seed=5530 + sx)
        inner += blob(lib.rect_pts(fx - 21, y1 - 8, fx + 21, y1), SUIT_SH)
        return shape(p, SUIT, inner, w=3.6, seed=5532 + sx)
    a, m, tip = pts
    p2 = (m[0] + (tip[0] - m[0]) * .55, m[1] + (tip[1] - m[1]) * .55)
    arm = band([a, m, p2], 46, 42, step=4, cap=False)
    inner = line([(a[0] + sx * 10, a[1]), (m[0] + sx * 10, m[1]), (p2[0] + sx * 10, p2[1])], 4.4, STRIPE, taper=0, wmin=1, seed=5536 + sx)
    return shape(arm, SUIT, inner, w=3.6, seed=5538 + sx)


def headband():
    """Повязка на лбу: над глазами (ниже 1034 не заходит), под ушами."""
    pts = [(752, 1012), (790, 998), (836, 994), (882, 998), (920, 1012), (922, 1032), (882, 1020), (836, 1016), (790, 1020), (750, 1032)]
    inner = line([(756, 1022), (790, 1010), (836, 1006), (882, 1010), (918, 1022)], 3.4, "#ffffff", taper=0, wmin=1, seed=5541)
    o = shape(pts, SUIT, inner, w=3.6, seed=5540)
    # завязки сбоку справа
    o += shape([(918, 1018, 1), (948, 1006), (956, 1022, 1), (936, 1030)], SUIT, "", w=3, seed=5542)
    o += shape([(918, 1024, 1), (944, 1040), (936, 1054, 1), (922, 1036)], SUIT, "", w=3, seed=5543)
    return o


def use(name):
    CT.WEAR.clear()
    if name == "overalls":
        CT.WEAR["body"] = overalls_body
    elif name == "host":
        CT.WEAR["body"] = vest_body
        CT.WEAR["hold"] = key_hold
    elif name == "sport":
        CT.WEAR["body"] = sport_body
        CT.WEAR["sleeve"] = sport_sleeve
        CT.WEAR["head"] = headband


_ = math
