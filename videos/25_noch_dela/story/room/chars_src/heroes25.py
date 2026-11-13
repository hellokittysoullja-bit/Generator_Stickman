"""Герои рилса 25 «ночные дела», ночные планы room (s02 s03 s04 s13 s14): Дима лежит на диване под пледом, голова
на подушке у подлокотника; кот клубком на его голенях; значки дел вокруг головы, листок календаря, Z сна, столик с
листком. Вечерний план s10 — heroes25e.py (сидячий Дима рилса 24 с листком).

Код и манера — из heroes24.py (тот же Дима, тот же кот, тот же плед, та же тушь): импорт и переиспользование, новые
позы рисуются здесь. Координаты — пиксели кадра 0 комнаты (1080×1920), камера в слои не запекается.
Свет: ночь фильтром fNight (умножение), луна из окна справа сверху и огонёк кота — screen по силуэту слоя.
Запуск: python3 heroes25.py → heroes25.html (анимация — template25.html).
"""
import math
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import heroes24 as H  # noqa: E402
from heroes24 import (INK, SKIN, SKIN_SH, SKIN_SH2, HOOD, HOOD_SH, HOOD_SH2, FOLD, CAT, CAT_SH, CAT_FUR, CAT_EDGE,  # noqa: E402
                      shape, clip_of, rim, line, blob, rect_pts, blur, T, night_hex, tartan)
from ink import band, ellipse_pts, fill_d, fur, ink_closed, sample  # noqa: E402

W, H_ = 1080, 1920
DEFS = H.DEFS
REG = H.REG

# ─── голова лежащего Димы: не зеркальная (лицо 3/4 вправо-вверх, к потолку), макушка к подлокотнику слева
HX, HY, HR, HS = 250, 1028, -36, 1.0
H.head_tf = lambda: f"translate({HX} {HY}) rotate({HR}) scale({HS} {HS})"


def L2G(x, y):
    c, s_ = math.cos(math.radians(HR)), math.sin(math.radians(HR))
    return HX + HS * (x * c - y * s_), HY + HS * (x * s_ + y * c)


# кот: рисунок в координатах кота рилса 24 (голова там же), клубком; в кадр — CAT_TF25
CAT_TF25 = "translate(902 1126) scale(.95) translate(-900 -1262)"


def cat_g(x, y):
    return 902 + (x - 900) * .95, 1126 + (y - 1262) * .95


FLAME_BASE = (1016, 1214)
FLAME_K = 1.0
FLAME_C = cat_g(FLAME_BASE[0], FLAME_BASE[1] - 34)
MOON = (980, 120)


# ═════════════════════════════ ДИМА ЛЁЖА ═════════════════════════════
PILLOW = [(18, 1086), (60, 1040), (150, 1016), (260, 1020), (352, 1050), (388, 1100), (372, 1160), (300, 1196), (160, 1206),
          (52, 1190), (6, 1146)]


def pillow():
    inner = blob([(6, 1146), (60, 1150), (180, 1180), (330, 1170), (388, 1110), (400, 1220), (0, 1230)], "#b9b4c4", .9)
    inner += blob([(60, 1048), (160, 1030), (250, 1034), (190, 1052), (90, 1066)], "#ffffff", .7)
    for i, st in enumerate([[(40, 1090), (70, 1110), (90, 1140)], [(330, 1060), (346, 1090)], [(300, 1180), (260, 1188)]]):
        inner += line(st, 2.6, "#8f8aa0", seed=500 + i, op=.85)
    for (x, y) in [(110, 1100), (190, 1080), (150, 1150), (240, 1140), (300, 1090), (80, 1170), (220, 1180)]:
        inner += blob(ellipse_pts(x, y, 6, 4.5, 8), "#e58a96", .75)
    return shape(PILLOW, "#eeeaf2", inner, w=5.2, seed=501, id="pillow")


def dima_lying_back():
    """Подушка, капюшон под затылком, шея и верх худи над пледом (всё, что под головой)."""
    s = [pillow()]
    # капюшон смят на подушке под затылком и шеей
    hood = [(150, 1150), (190, 1120), (260, 1112), (330, 1118), (392, 1136), (420, 1176), (380, 1206), (290, 1210), (200, 1200)]
    inner = blob([(190, 1120), (260, 1112), (300, 1150), (240, 1180), (190, 1170)], HOOD_SH2, .9)
    inner += line([(200, 1160), (240, 1140), (282, 1140)], 3, FOLD, seed=510, op=.85)
    inner += line([(320, 1180), (360, 1160), (392, 1166)], 2.6, FOLD, seed=511, op=.7)
    s.append(shape(hood, HOOD, inner, w=5.2, seed=512, id="dima_hood"))
    # туловище в худи: плечо и грудь до края пледа (дальше — под пледом)
    body = [(296, 1140), (340, 1108), (392, 1100), (440, 1112), (470, 1140), (470, 1250, 1), (296, 1250, 1)]
    inner = blob([(300, 1150), (360, 1110), (420, 1100), (380, 1170), (320, 1250), (300, 1250)], HOOD_SH, .85)
    for i, st in enumerate([[(430, 1120), (452, 1150), (458, 1190)], [(490, 1110), (500, 1140)], [(470, 1170), (490, 1200)]]):
        inner += line(st, 3, FOLD, seed=513 + i, op=.8)
    s.append(shape(body, HOOD, inner, w=5.4, seed=516, id="dima_body"))
    # шея: от подбородка вниз-вправо к вороту
    nk = [(296, 1078), (356, 1094), (394, 1140), (356, 1166), (304, 1142)]
    inner = blob([(296, 1078), (356, 1094), (362, 1124), (306, 1112)], SKIN_SH, .95)
    inner += line([(320, 1102), (346, 1122), (368, 1144)], 2.4, SKIN_SH2, seed=517, op=.85)
    s.append(shape(nk, SKIN, inner, w=4.8, seed=518, id="dima_neck"))
    # ворот с рубчиком и шнурки
    collar = [(318, 1124), (352, 1140), (392, 1134), (418, 1110), (432, 1124), (400, 1160), (350, 1168), (306, 1146)]
    s.append(shape(collar, HOOD_SH, line([(322, 1140), (356, 1154), (396, 1148), (424, 1124)], 2, FOLD, seed=519, op=.7), w=4.6, seed=520))
    for (x0, y0, x1, y1, sd) in [(380, 1162, 392, 1196, 521), (410, 1150, 438, 1178, 524)]:
        s.append(line([(x0, y0), ((x0 + x1) / 2 + 3, (y0 + y1) / 2), (x1, y1)], 6, "#efe3c4", taper=.2, wmin=.8, seed=sd))
        s.append(line([(x0, y0), ((x0 + x1) / 2 + 3, (y0 + y1) / 2), (x1, y1)], 1.8, INK, taper=.2, wmin=.8, seed=sd + 1, op=.55))
        s.append(shape(rect_pts(x1 - 5, y1, x1 + 5, y1 + 16, 2), "#b9b9c4", w=2.6, seed=sd + 2))
    return "".join(s)


# ═════════════════════════════ ПЛЕД НА ЛЕЖАЩЕМ ═════════════════════════════
# верх пледа по телу: край у груди (подвёрнут), грудь, живот, бедро, колени, голени (на них кот), стопы
PL_TOP = [(334, 1262, 1), (352, 1200), (392, 1150), (446, 1110), (510, 1088), (574, 1094), (636, 1122), (700, 1112), (760, 1102),
          (830, 1118), (900, 1140), (990, 1146), (1060, 1140), (1096, 1146, 1)]
EDGE_Y = 1300


def plaid_lying():
    s = []
    folds = [330, 440, 560, 690, 820, 950, 1080]
    bottom = []
    for i in range(len(folds) - 1):
        xa, xb = folds[i], folds[i + 1]
        bottom += [(xa, 1478 - (i % 2) * 6), ((xa + xb) / 2, 1450 + (i % 3) * 4)]
    bottom = [(1096, 1462)] + bottom[::-1][:-1] + [(330, 1466)]
    outline = PL_TOP + [(1096, 1300), (1098, 1462, 1)] + bottom[1:-1] + [(328, 1468, 1), (318, 1380), (322, 1300)]
    inner = [f'<rect x="300" y="1080" width="{W}" height="460" fill="#7aa66a"/>', tartan(0, W, 1080, 1500)]
    # объём: свет на горбах (грудь, бедро, колени), тень в ложбинах и под телом
    inner.append(blob([(446, 1110), (510, 1088), (574, 1094), (580, 1140), (480, 1160), (440, 1170)], "#eef6c8", .2))
    inner.append(blob([(700, 1120), (750, 1112), (800, 1122), (790, 1160), (720, 1160)], "#eef6c8", .18))
    inner.append(blob([(580, 1130), (640, 1134), (650, 1230), (600, 1250), (570, 1200)], "#203a24", .3))
    inner.append(blob([(840, 1128), (900, 1136), (900, 1250), (850, 1250)], "#203a24", .25))
    inner.append(blob([(330, 1240), (1096, 1230), (1096, EDGE_Y + 6), (330, EDGE_Y + 10)], "#203a24", .22))
    for i, st in enumerate([[(470, 1170), (520, 1200), (560, 1240)], [(620, 1150), (640, 1200)], [(760, 1160), (790, 1220)],
                            [(900, 1160), (930, 1230)], [(380, 1220), (420, 1262)], [(1000, 1150), (1030, 1220)]]):
        inner.append(line(st, 3.2, seed=530 + i, op=.8))
    # кромка сиденья: плед переламывается и падает вниз
    inner.append(blob([(330, EDGE_Y - 14), (W, EDGE_Y - 16), (W, EDGE_Y + 4), (330, EDGE_Y + 6)], "#eef6c8", .16))
    inner.append(blob([(330, EDGE_Y + 8), (W, EDGE_Y + 6), (W, EDGE_Y + 44), (330, EDGE_Y + 46)], "#0f1d12", .35))
    for i in range(len(folds) - 1):
        xa, xb = folds[i], folds[i + 1]
        xm = (xa + xb) / 2
        inner.append(blob([(xm - 10, EDGE_Y + 30), (xm + 6, EDGE_Y + 30), (xm + 26, 1400), (xm + 30, 1490), (xm - 34, 1490), (xm - 26, 1400)],
                          "#132416", .45, blur(9)))
        inner.append(line([(xm - 2, EDGE_Y + 40), (xm + 4, 1380), (xm + 10, 1460)], 3, seed=540 + i, op=.7, peak=.7))
    inner.append(blob([(300, 1390), (W, 1390), (W, 1490), (300, 1490)], "#0f1d12", .3))
    # тень кота на голенях
    inner.append(blob(ellipse_pts(910, 1148, 160, 16, 12), "#0d160f", .6, blur(6)))
    s.append(shape(outline, "#7aa66a", "".join(inner), w=5.4, seed=545, id="plaid"))
    # подвёрнутый край у груди: полоса изнанки
    hem = [(338, 1252), (354, 1198), (394, 1150), (448, 1112), (512, 1090), (520, 1114), (462, 1136), (414, 1170), (378, 1216), (360, 1262)]
    s.append(shape(hem, "#86b276", tartan(0, W, 1080, 1300) + blob([(338, 1250), (354, 1198), (394, 1150), (414, 1170), (378, 1220)], "#5f8a52", .55) +
                   line([(370, 1226), (404, 1172), (456, 1132), (512, 1108)], 2.2, "#4f7a44", seed=548, op=.8), w=4.6, seed=547))
    S_ = sample(bottom, False, step=10)
    rs = np.random.RandomState(9)
    for i, (x, y) in enumerate(S_):
        ln = rs.uniform(14, 22)
        s.append(line([(x, y - 2), (x + rs.uniform(-3, 3), y + ln * .5), (x + rs.uniform(-4, 4), y + ln)], 3.6, "#4f7c48",
                      seed=600 + i, taper=.6, wmin=.3, peak=.3))
    return "".join(s)


# ─── столик у изголовья с листком дел (s13)
def side_table():
    """Тумбочка перед левым концом дивана; на ней листок со списком (три строки штрихами, без букв) и ручка."""
    s = ['<g id="table">']
    for x in (62, 250):
        s.append(shape(rect_pts(x - 11, 1262, x + 11, 1660), "#6e4426", blob(rect_pts(x + 3, 1262, x + 11, 1660), "#4a2c16", .8), w=4.2,
                       seed=561 + x))
    s.append(shape(rect_pts(44, 1330, 268, 1350), "#5e3a20", w=3.6, seed=566))
    s.append(shape([(30, 1258), (290, 1258), (290, 1278), (30, 1278)], "#7a4c2a", w=4.4, seed=567))
    s.append(shape([(46, 1214), (274, 1214), (290, 1258), (30, 1258)], "#a06a3c",
                   blob([(30, 1246), (290, 1246), (290, 1258), (30, 1258)], "#7a4c2a", .7) +
                   line([(80, 1226), (200, 1224)], 1.6, "#7a4c2a", seed=568, op=.7), w=4.6, seed=560))
    sh = [(88, 1220), (214, 1216), (226, 1246), (78, 1250)]
    lines = "".join(line([(98 + k * 2, 1226 + k * 7.5), (176 + k * 6 - (k == 1) * 22, 1224 + k * 7.5)], 2.2, "#2a3a8a", seed=570 + k,
                         taper=.3, wmin=.5) for k in range(3))
    s.append(shape(sh, "#f6f1e4", lines, w=3, seed=575))
    s.append(H.pen(150, 1252, 246, 1240, seed=576))
    s.append("</g>")
    return "".join(s)


# ═════════════════════════════ КОТ КЛУБКОМ ═════════════════════════════
CX = 836
TAIL25 = [(1070, 1200), (1094, 1236), (1080, 1266), (1040, 1276), (1012, 1262), (1008, 1240), (1016, 1220)]


def flame_pts(k=1.0):
    bx, by = FLAME_BASE
    P = [(-20, 4), (-24, -16), (-15, -36), (-13, -56), (-4, -45), (2, -78, 1), (11, -52), (20, -63, 1), (24, -36), (22, -11), (15, 4), (0, 9)]
    return [(bx + q[0] * k, by + q[1] * k) + ((1,) if len(q) > 2 else ()) for q in P]


def tail25():
    S = sample(TAIL25, False, 3.0)
    n = len(S)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = 40 + (16 - 40) * np.linspace(0, 1, n) ** 1.1
    L, R = S + N * Wd[:, None] / 2, S - N * Wd[:, None] / 2
    tip = S[-1] + Tg[-1] * Wd[-1] * .45
    outline = [tuple(p) for p in L] + [tuple(tip)] + [tuple(p) for p in R[::-1]]
    REG["cat_tail_shape"] = outline
    inner = blob([(1030, 1250), (1110, 1230), (1110, 1290), (1020, 1290)], CAT_SH, .8)
    for i, k in enumerate(range(int(n * .15), int(n * .85), max(1, int(n * .14)))):
        p = S[k] + N[k] * Wd[k] * .15
        inner += line([tuple(p), tuple(p + Tg[k] * 12)], 2, CAT_EDGE, seed=636 + i, op=.8)
    return shape(outline, CAT, inner, w=4.8, seed=630)


def cat_head_art():
    """Голова кота рилса 24 (те же точки): голова, уши (левое от зрителя загнуто), полоски, нос, рот."""
    s = []
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884, 990), (940, 1050), (930, 1150), (866, 1150), (902, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    inner += blob([(800, 1106), (836, 1098), (872, 1106), (864, 1142), (808, 1142)], CAT_FUR, .45)
    for i, st in enumerate([[(800, 1004), (806, 1016)], [(836, 996), (838, 1010)], [(870, 1002), (866, 1014)]]):
        inner += line(st, 2, CAT_EDGE, seed=258 + i, op=.8)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250, id="cat_head"))
    s.append(H.cat_ears())
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76
            s.append(line([(x0, 1100 + dy), (x0 + sx * 30, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    s.append(shape([(826, 1108), (846, 1108), (836, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836, 1119), (836, 1124)], 2.4, seed=263))
    s.append(line([(822, 1124), (829, 1131), (836, 1124), (843, 1131), (850, 1124)], 3, seed=264))
    return "".join(s)


def cat_curl():
    s = [f'<g id="cat" transform="{CAT_TF25}"><g id="cat_breath">']
    # тело клубком: спина горкой справа (бедро), снизу ровно на пледе
    body = [(752, 1262, 1), (744, 1200), (772, 1150), (840, 1124), (940, 1108), (1030, 1118), (1078, 1152), (1092, 1210), (1078, 1262, 1)]
    bp = fur(body, 7, 7, seed=621)
    inner = blob([(960, 1110), (1070, 1150), (1070, 1270), (990, 1270), (1000, 1190)], CAT_SH, .85)
    inner += blob([(820, 1140), (930, 1124), (980, 1140), (930, 1160), (840, 1168)], CAT_FUR, .55)
    inner += line([(950, 1244), (962, 1192), (1004, 1158), (1056, 1168)], 3.4, CAT_SH, seed=622, op=.9)    # бедро
    inner += line([(958, 1240), (968, 1198), (1006, 1168)], 2, CAT_EDGE, seed=623, op=.7)
    for i, st in enumerate([[(880, 1150), (890, 1166)], [(940, 1140), (946, 1156)], [(1000, 1140), (1004, 1154)], [(860, 1200), (866, 1216)]]):
        inner += line(st, 2.2, CAT_EDGE, seed=624 + i, op=.8)
    s.append(shape(bp, CAT, inner, w=5, seed=620, id="cat_body"))
    # задняя лапа спереди у бедра (подушечки)
    s.append(shape(ellipse_pts(964, 1254, 32, 13, 12), CAT, blob(ellipse_pts(968, 1259, 26, 8, 10), CAT_SH, .6), w=4.4, seed=640))
    # передние лапы под подбородком
    for k, fx in enumerate((800, 872)):
        paw = [(fx - 26, 1264, 1), (fx - 28, 1238), (fx - 12, 1226), (fx + 12, 1226), (fx + 28, 1238), (fx + 26, 1264, 1)]
        s.append(shape(paw, CAT, blob([(fx + 6, 1226), (fx + 30, 1236), (fx + 28, 1266), (fx + 8, 1266)], CAT_SH, .6), w=4.6, seed=641 + k))
        for dx in (-9, 9):
            s.append(line([(fx + dx, 1252), (fx + dx, 1264)], 2.2, seed=645 + k * 2 + dx))
    s.append(tail25())
    s.append('<g id="cat_headg">' + cat_head_art() + "</g>")
    s.append("</g></g>")
    return "".join(s)


def cat_eyes25():
    lid_c = night_hex(CAT)
    s = [f'<g id="cat_eyes" transform="{CAT_TF25}"><g id="cat_breath_e"><g id="cat_eyes_tilt">']
    for nm, ex, sd in [("L", CX - 44, 255), ("R", CX + 44, 256)]:
        ep = ellipse_pts(ex, 1072, 34, 38, 14)
        cid = clip_of(ep)
        s.append(f'<g id="cat_eye_{nm}"><path d="{fill_d(ep)}" fill="#a9d84a"/><g clip-path="url(#{cid})">')
        s.append(blob(ellipse_pts(ex, 1046, 36, 20, 10), "#6f9a2e", .95))
        s.append(blob(ellipse_pts(ex, 1102, 26, 11, 10), "#d4f27a", .75))
        s.append(blob(ellipse_pts(ex - 18, 1080, 10, 20, 8), "#c8ee6a", .5))
        s.append(f'<g id="cat_pupil_{nm}"><ellipse cx="{ex}" cy="1074" rx="12.5" ry="25" fill="#0b0a10"/>'
                 f'<circle cx="{ex - 7}" cy="1060" r="6.5" fill="#f4f8ff"/><circle cx="{ex + 9}" cy="1088" r="3" fill="#ffd9a0"/></g>')
        s.append(f'<g id="cat_lid_{nm}" transform="translate(0 -84)"><rect class="catlid" x="{ex - 40}" y="990" width="80" height="84" fill="{lid_c}"/>'
                 + line([(ex - 34, 1066), (ex, 1078), (ex + 34, 1066)], 5.4, "#8f88b0", seed=sd) + "</g>")
        s.append(f'<g id="cat_lidlo_{nm}" transform="translate(0 48)"><rect class="catlid" x="{ex - 40}" y="1072" width="80" height="50" fill="{lid_c}"/></g>')
        s.append(f'</g><path id="cat_ring_{nm}" d="{ink_closed(ep, 4.4, seed=sd + 3)}" fill="{INK}"/></g>')
        s.append(f'<g id="cat_closed_{nm}" style="display:none">' +
                 line([(ex - 30, 1072), (ex - 12, 1082), (ex + 12, 1082), (ex + 30, 1072)], 5.6, "#9a93bc", seed=sd + 40, taper=.5, wmin=.3) + "</g>")
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CX + sx * 58
            s.append(line([(x0, 1128 + dy * .8), (x0 + sx * 50, 1126 + dy + dl * .5), (x0 + sx * 96, 1124 + dy * 1.2 + dl)], 1.3, "#c4c1d6",
                          seed=270 + k + sx, op=.8))
    s.append("</g></g></g>")
    return "".join(s)


def cat_flame25():
    k = FLAME_K
    bx, by = FLAME_BASE
    s = [f'<g id="cat_flame_rot" transform="{CAT_TF25}"><g id="cat_breath_f"><g id="cat_flame">']
    s.append(shape(flame_pts(k), "#ff8a2a", blob(flame_pts(.7 * k), "#ffbe55"), w=3.4, seed=233, ink_color="#7a2a10", var=.2))
    s.append(blob([(bx - 7, by + 2), (bx - 5, by - 19), (bx + 2, by - 37), (bx + 7, by - 18), (bx + 5, by + 2)], "#fff2c0"))
    s.append("</g></g></g>")
    return "".join(s)


# ═════════════════════════════ ЗНАЧКИ ДЕЛ, КАЛЕНДАРЬ, Z ═════════════════════════════
ICONS = ["mail", "cart", "laptop", "tooth", "receipt", "phone", "trash"]
NICON = 14


def icon_art(kind, i):
    """Бейдж 120×120 с рисунком дела, без букв."""
    pal = {"mail": ("#3a6fd8", "#cfe2ff"), "cart": ("#2f9a6a", "#c8f2c0"), "laptop": ("#7a4ad8", "#e6d2ff"),
           "tooth": ("#d84a7a", "#ffd6e4"), "receipt": ("#e0a030", "#fff0c0"), "phone": ("#2a8aa8", "#c8f2f4"),
           "trash": ("#5a6070", "#dfe2ea")}
    a, b = pal[kind]
    fr = rect_pts(-60, -60, 60, 60, 22)
    g = [blob(fr, b), blob([(-60, 20), (60, 20), (60, 60), (-60, 60)], a, .22)]
    if kind == "mail":
        g.append(shape(rect_pts(-38, -24, 38, 26, 4), "#ffffff", line([(-36, -22), (0, 6), (36, -22)], 4, a, seed=900 + i), w=4, seed=901 + i))
    elif kind == "cart":
        g.append(line([(-44, -32), (-30, -32), (-20, 18), (30, 18)], 5.5, INK, seed=902 + i, taper=.1, wmin=.8))
        g.append(shape([(-26, -20), (40, -20), (32, 8), (-20, 8)], "#ffffff", line([(-6, -20), (-4, 8)], 2.4, a, seed=903 + i) +
                       line([(16, -20), (14, 8)], 2.4, a, seed=904 + i), w=4, seed=905 + i))
        g.append(shape(ellipse_pts(-6, -28, 9, 9, 10), "#ff7a3a", w=3, seed=906 + i))
        g.append(shape([(10, -40), (20, -26), (8, -24)], "#4ec27a", w=3, seed=907 + i))
        for x in (-14, 24):
            g.append(shape(ellipse_pts(x, 30, 7, 7, 10), "#2a2a33", w=3, seed=908 + i + x))
    elif kind == "laptop":
        g.append(shape(rect_pts(-34, -34, 34, 10, 5), "#2c2f38", blob(rect_pts(-27, -27, 27, 4, 3), "#9fd0ff"), w=4, seed=909 + i))
        g.append(shape([(-46, 12), (46, 12), (40, 26), (-40, 26)], "#b4bac6", w=4, seed=910 + i))
    elif kind == "tooth":
        tp = [(-30, -30), (-14, -40), (0, -32), (14, -40), (30, -30), (30, -2), (20, 34, 1), (10, 34), (4, 8), (-4, 8), (-10, 34),
              (-20, 34, 1), (-30, -2)]
        g.append(shape(tp, "#ffffff", blob([(14, -36), (30, -28), (28, 0), (20, 30), (16, 0)], "#e2dcef", .9), w=4.4, seed=911 + i))
        g.append(blob(ellipse_pts(-14, -22, 7, 5, 8), "#ffffff"))
    elif kind == "receipt":
        rp = [(-28, -42, 1), (28, -42, 1), (28, 34)] + [(28 - 7 * k, 42 if k % 2 else 34, 1) for k in range(1, 9)] + [(-28, 34, 1)]
        ln = "".join(line([(-18, -28 + 13 * k), (18 - (k % 2) * 12, -28 + 13 * k)], 3.2, "#8a8f9e", seed=912 + i + k, taper=.2, wmin=.6)
                     for k in range(5))
        g.append(shape(rp, "#ffffff", ln, w=4, seed=918 + i))
    elif kind == "phone":
        g.append(shape(rect_pts(-24, -44, 24, 44, 9), "#23252c", blob(rect_pts(-18, -34, 18, 32, 4), "#7ad0e8") +
                       blob(ellipse_pts(0, -6, 9, 9, 10), "#ffffff", .9), w=4.2, seed=919 + i))
    elif kind == "trash":
        bag = [(-32, 40), (-38, 4), (-26, -22), (-12, -30), (12, -30), (26, -22), (38, 4), (32, 40)]
        g.append(shape(bag, "#3a3d48", blob([(8, -28), (38, 4), (32, 40), (12, 40)], "#262832", .8) +
                       line([(-16, -6), (-10, 20)], 2.4, "#6a6e7c", seed=920 + i, op=.9), w=4.4, seed=921 + i))
        g.append(shape([(-12, -30), (-22, -46), (-4, -38), (0, -50), (6, -38), (22, -46), (12, -30)], "#3a3d48", w=4, seed=922 + i))
    c = clip_of(fr)
    return (f'<path d="{fill_d(fr)}" fill="{b}"/><g clip-path="url(#{c})">{"".join(g)}</g>'
            f'<path d="{ink_closed(fr, 4.6, seed=930 + i)}" fill="#14141c"/>')


def icon_defs():
    DEFS.append("".join(f'<g id="ic{i}">{icon_art(k, i)}</g>' for i, k in enumerate(ICONS)))


def icons_group(gid):
    return f'<g id="{gid}">' + "".join(f'<use href="#ic{i % 7}" id="{gid}_{i}" style="display:none"/>' for i in range(NICON)) + "</g>"


def digit(ch, x, y, s, sd):
    """Цифра пером (без шрифта): «1» и «4» листка календаря."""
    P = {"1": [[(-8, -26), (6, -40), (6, 40)], [(-10, 40), (22, 40)]],
         "4": [[(14, 40), (14, -40), (-24, 18), (26, 18)]]}
    return "".join(line([(x + p[0] * s, y + p[1] * s) for p in st], 13 * s, "#1c1622", seed=sd + j, taper=.15, wmin=.7) for j, st in enumerate(P[ch]))


def calendar():
    s = ['<g id="cal">']
    page = rect_pts(-100, -112, 100, 112, 14)
    c = clip_of(page)
    inner = (f'<rect x="-100" y="-112" width="200" height="64" fill="#e0405a"/>'
             f'<rect x="-100" y="-56" width="200" height="8" fill="#a82a40" opacity=".6"/>'
             + blob([(40, -48), (100, -48), (100, 112), (60, 112)], "#e8e0d0", .7))
    s.append(f'<path d="{fill_d(page)}" fill="#fbf7ee"/><g clip-path="url(#{c})">{inner}</g>')
    s.append(f'<path d="{ink_closed(page, 5, seed=950)}" fill="{INK}"/>')
    for x in (-50, 50):
        s.append(shape(ellipse_pts(x, -112, 9, 9, 10), "#2a2a33", w=3, seed=951 + x))
        s.append(line([(x, -122), (x, -96)], 7, "#c9ccd8", seed=953 + x, taper=.1, wmin=.8))
    s.append(digit("1", -36, 30, 1.0, 960) + digit("4", 34, 30, 1.0, 965))
    # оторванный край сверху (зубцы)
    s.append("</g>")
    return "".join(s)


NZ = 4


def zglyph(i):
    pts = [(-20, -22, 1), (20, -22, 1), (20, -12, 1), (-6, 14, 1), (22, 14, 1), (22, 24, 1), (-22, 24, 1), (-22, 14, 1), (4, -12, 1),
           (-20, -12, 1)]
    return shape(pts, "#dfe8ff", blob([(-22, 14), (22, 14), (22, 24), (-22, 24)], "#a9b8e8", .9), w=3.4, seed=980 + i,
                 ink_color="#1a2040", var=.1)


def z_group():
    return '<g id="zz">' + "".join(f'<g id="z{i}" style="display:none">{zglyph(i)}</g>' for i in range(NZ)) + "</g>"


# ═════════════════════════════ СВЕТ ═════════════════════════════
def light_defs():
    mx, my = MOON
    fx, fy = FLAME_C
    DEFS.append(f"""
<radialGradient id="gMoon" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({mx} {my}) scale(1300 1300)">
 <stop offset="0" stop-color="#b8ccff" stop-opacity=".9"/><stop offset=".6" stop-color="#6a86d0" stop-opacity=".45"/>
 <stop offset="1" stop-color="#3a5aa8" stop-opacity=".05"/></radialGradient>
<radialGradient id="gFaceMoon" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(110 -120) scale(260 240)">
 <stop offset="0" stop-color="#c8d8ff" stop-opacity=".55"/><stop offset=".55" stop-color="#7a96e0" stop-opacity=".25"/>
 <stop offset="1" stop-color="#3a5cb0" stop-opacity="0"/></radialGradient>
<radialGradient id="gFl" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({fx:.1f} {fy:.1f}) scale(300 300)">
 <stop offset="0" stop-color="#ffb060" stop-opacity=".9"/><stop offset=".3" stop-color="#ff8a3a" stop-opacity=".45"/>
 <stop offset=".7" stop-color="#c05a22" stop-opacity=".12"/><stop offset="1" stop-color="#c05a22" stop-opacity="0"/></radialGradient>
<radialGradient id="gRimF" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({FLAME_BASE[0]} {FLAME_BASE[1] - 20}) scale(220 260)">
 <stop offset="0" stop-color="#ffc878"/><stop offset=".5" stop-color="#ff8a3a"/><stop offset="1" stop-color="#c05020" stop-opacity="0"/></radialGradient>
<filter id="fNight" x="-500" y="-500" width="{W + 1000}" height="{H_ + 1000}" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
 <feColorMatrix id="fNightM" type="matrix" values="{.5 * .9} {.5 * .1} 0 0 0  {.55 * .05} {.55 * .9} {.55 * .05} 0 0  0 {.9 * .1} {.9 * .9} 0 0  0 0 0 1 0"/>
</filter>
<filter id="fWhite" x="-500" y="-500" width="{W + 1000}" height="{H_ + 1000}" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
 <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>
""")


def lights_dima():
    fc = clip_of(H.FACE)
    face = (f'<g id="face_light_moon"><g transform="{H.head_tf()}"><g clip-path="url(#{fc})">'
            f'<rect x="-140" y="-140" width="280" height="280" fill="url(#gFaceMoon)"/><path d="{fill_d(REG["dima_hair"])}" fill="#000"/></g></g></g>')
    return (f'<g id="moon_dima"><rect x="-500" y="-500" width="{W + 1000}" height="{H_ + 1000}" fill="url(#gMoon)" opacity=".3"/>'
            f'{face}</g>')


def lights_plaid():
    return (f'<g id="moon_plaid"><rect x="-500" y="-500" width="{W + 1000}" height="{H_ + 1000}" fill="url(#gMoon)" opacity=".4"/></g>'
            f'<g id="fl_plaid"><rect width="{W}" height="{H_}" fill="url(#gFl)" opacity=".85"/></g>')


def lights_cat():
    s = [f'<g id="fl_cat"><rect x="-500" y="-500" width="{W + 1000}" height="{H_ + 1000}" fill="url(#gFl)" opacity=".55"/>']
    s.append(f'<g transform="{CAT_TF25}"><g id="cat_breath_r">')
    s.append(rim(REG["cat_body"], "gRimF", -12, 2, .75, soft=6))
    s.append(f'<g id="cat_head_rim">{rim(REG["cat_head"], "gRimF", -12, 5, .7, soft=6)}</g>')
    s.append("</g></g></g>")
    s.append(f'<g id="moon_cat"><g transform="{CAT_TF25}"><g id="cat_breath_m">')
    s.append(f'<g id="cat_head_rim_m">{rim(REG["cat_head"], "#8aa8f0", -6, 10, .6, soft=6)}{rim(REG["cat_ear_R"], "#8aa8f0", -6, 8, .6, soft=4)}</g>')
    s.append(rim(REG["cat_body"], "#8aa8f0", -8, 10, .5, soft=6))
    s.append("</g></g></g>")
    return "".join(s)


def mask_of(art_id):
    m = f"M_{art_id}"
    DEFS.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="-500" y="-500" width="{W + 1000}" height="{H_ + 1000}">'
                f'<use href="#{art_id}" filter="url(#fWhite)"/></mask>')
    return m


def sleep_eyes():
    """Спящие глаза: веки сомкнуты — дуга вниз с ресницами (вместо белков), в осях головы."""
    g = [f'<g transform="{H.head_tf()}"><g id="dima_eyes_sleep" style="display:none">']
    for (cx, cy, rx, ry), sd in [(H.EYE_F, 990), (H.EYE_N, 993)]:
        g.append(line([(cx - rx * .85, cy + 2), (cx - rx * .3, cy + 14), (cx + rx * .3, cy + 14), (cx + rx * .85, cy + 2)], 6.0,
                      seed=sd, taper=.5, wmin=.3))
        g.append(line([(cx - rx * .6, cy + 12), (cx - rx * .3, cy + 26), (cx + rx * .3, cy + 26), (cx + rx * .6, cy + 12)], 2.2,
                      SKIN_SH2, seed=sd + 1, op=.8))
    g.append("</g></g>")
    return "".join(g)


def build():
    light_defs()
    icon_defs()
    a_dima = ('<g id="dima_all">' + dima_lying_back() + f'<g id="dima_head_pose">{H.dima_head()}{sleep_eyes()}</g></g>')
    a_plaid = '<g id="plaid_breath">' + plaid_lying() + "</g>" + side_table()
    a_cat = cat_curl()
    layers = []
    for name, art, lit, back, top in [("dima", a_dima, lights_dima(), '<g filter="url(#fFx)">' + icons_group("ic_back") + "</g>", ""),
                                      ("plaid", a_plaid, lights_plaid(), "", ""),
                                      ("cat", a_cat, lights_cat(), "", cat_eyes25() + cat_flame25()),
                                      ("fx", "", "", "", icons_group("ic_front") + calendar() + z_group())]:
        if art:
            m = mask_of(f"A_{name}")
            body = (f'<g id="A_{name}" filter="url(#fNight)">{art}</g>'
                    f'<g style="mix-blend-mode:screen" mask="url(#{m})">{lit}</g>')
        else:
            body = ""
        if name == "fx":
            top = f'<g id="fx_night" filter="url(#fFx)">{top}</g>'
        layers.append(f'<g id="L_{name}" style="isolation:isolate">{back}{body}{top}</g>')
    DEFS.append(f'<filter id="fFx" x="-500" y="-500" width="{W + 1000}" height="{H_ + 1000}" filterUnits="userSpaceOnUse" '
                f'color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values=".78 .04 0 0 0  .02 .8 .04 0 0  0 .06 .95 0 0  0 0 0 1 0"/></filter>')
    return (f'<svg id="scene" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H_}" viewBox="0 0 {W} {H_}">'
            f'<defs>{"".join(DEFS)}</defs>{"".join(layers)}</svg>')


if __name__ == "__main__":
    here = __file__.rsplit("/", 1)[0]
    svg = build()
    html = open(f"{here}/template25.html").read().replace("<!--SVG-->", svg)
    open(f"{here}/heroes25.html", "w").write(html)
    print("heroes25.html", len(html) // 1024, "KB")
