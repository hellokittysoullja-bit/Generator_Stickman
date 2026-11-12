"""Герои «Дима, 01:47» для совмещённого ролика: Дима + телефон, плед, кот — SVG, три слоя с прозрачным фоном.

Раскладка — пиксели кадра 0 съёмочной камеры Blender (methods/blender/still.png, 1080×1920): диван, сиденье, место
света экрана и огонька. Комнату не рисуем. Каждый слой:
  арт в «дневных» цветах → ночь фильтром (умножение цвета, альфа не трогается) →
  свет экрана/огонька осветлением (screen) ТОЛЬКО по силуэту слоя (маска из самого арта) → светящееся поверх.
Запуск: python3 heroes.py → heroes.html (анимация — в template.html по ../timing.js).
"""
import math
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from ink import band, ellipse_pts, fill_d, fur, ink_closed, ink_open, sample  # noqa: E402

W, H = 1080, 1920
INK = "#1c1622"
DEFS = []
REG = {}
_uid = [0]

NIGHT = (0.52, 0.56, 0.86)     # умножение «дневного» цвета на ночь (согласовано с комнатой Blender)
SCREEN_PX = (566, 760)         # где светит экран (timing.py / Blender)
FLAME_C = (1028, 900)          # центр огонька (фактический, см. отчёт)


def uid(p="c"):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def shape(pts, fill, inner="", w=5.0, seed=0, ink=True, id=None, attrs="", var=0.28, weight=0.45, ink_color=INK):
    d = fill_d(pts)
    if id:
        REG[id] = pts
    gid = f' id="{id}"' if id else ""
    out = [f"<g{gid} {attrs}>", f'<path d="{d}" fill="{fill}"/>']
    if inner:
        c = uid()
        DEFS.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
        out.append(f'<g clip-path="url(#{c})">{inner}</g>')
    if ink:
        out.append(f'<path d="{ink_closed(pts, w, var=var, weight=weight, seed=seed)}" fill="{ink_color}"/>')
    out.append("</g>")
    return "".join(out)


def clip_of(pts, tf=None):
    c = uid()
    t = f' transform="{tf}"' if tf else ""
    DEFS.append(f'<clipPath id="{c}"><path d="{fill_d(pts)}"{t}/></clipPath>')
    return c


def rim(pts, color, dx, dy, op=1.0, tf=None, id=None, cut=()):
    """Рим-свет: фигура минус она же со сдвигом — полумесяц на стороне к источнику (в группе screen чёрное нейтрально)."""
    d = fill_d(pts)
    c = clip_of(pts)
    fill = f"url(#{color})" if color.startswith("g") else color
    gid = f' id="{id}"' if id else ""
    g = (f'<g{gid} clip-path="url(#{c})" opacity="{op}"><path d="{d}" fill="{fill}"/>'
         f'<path d="{d}" transform="translate({dx} {dy})" fill="#000"/>'
         + "".join(f'<path d="{fill_d(c_)}" fill="#000"/>' for c_ in cut) + "</g>")
    return f'<g transform="{tf}">{g}</g>' if tf else g


def line(pts, w=4.0, color=INK, taper=0.6, wmin=0.12, seed=3, peak=0.5, op=1.0, extra=""):
    d = ink_open(pts, w, taper=taper, wmin=wmin, seed=seed, peak=peak)
    o = f' opacity="{op}"' if op != 1 else ""
    return f'<path d="{d}" fill="{color}"{o} {extra}/>'


def blob(pts, color, op=1.0, extra=""):
    o = f' opacity="{op}"' if op != 1 else ""
    return f'<path d="{fill_d(pts)}" fill="{color}"{o} {extra}/>'


def rect_pts(x0, y0, x1, y1, r=0):
    if r <= 0:
        return [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]
    k = r * 0.3
    return [(x0 + r, y0), (x1 - r, y0), (x1 - k, y0 + k), (x1, y0 + r), (x1, y1 - r), (x1 - k, y1 - k), (x1 - r, y1),
            (x0 + r, y1), (x0 + k, y1 - k), (x0, y1 - r), (x0, y0 + r), (x0 + k, y0 + k)]


def blur(sd):
    i = f"bl{sd}".replace(".", "_")
    if not any(f'id="{i}"' in x for x in DEFS):
        DEFS.append(f'<filter id="{i}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return f'filter="url(#{i})"'


def T(pts, dx, dy, s=1.0, rot=0.0, cx=0.0, cy=0.0):
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for p in pts:
        x, y = (p[0] - cx) * s, (p[1] - cy) * s
        q = (cx + x * c - y * sn + dx, cy + x * sn + y * c + dy)
        out.append(q + ((1,) if len(p) > 2 and p[2] else ()))
    return out


def night_hex(h):
    r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    return "#%02x%02x%02x" % (round(r * NIGHT[0]), round(g * NIGHT[1]), round(b * NIGHT[2]))


# ═════════════════════════════ ДИМА ═════════════════════════════
SKIN, SKIN_SH, SKIN_SH2 = "#ecc4a2", "#d39f83", "#bf8a74"
HAIR, HAIR_SH, HAIR_HI = "#5a3826", "#3d2418", "#7a5038"
HOOD, HOOD_SH, HOOD_SH2, FOLD = "#d4a23e", "#a97b25", "#8c6219", "#6b4a12"

HX, HY, HR, HS = 292, 884, -16, 1.12   # голова: центр, наклон (откинулся назад), масштаб


def head_tf():
    return f"translate({HX} {HY}) rotate({HR}) scale({HS})"


def H2G(x, y):
    c, s_ = math.cos(math.radians(HR)), math.sin(math.radians(HR))
    return HX + HS * (x * c - y * s_), HY + HS * (x * s_ + y * c)


# лицо 3/4 вправо: лоб, надбровье, скула, впадина под скулой, угол челюсти, подбородок
FACE = [(-30, -120), (40, -116), (86, -86), (106, -44), (110, -22), (118, 4), (120, 18), (112, 42), (108, 64), (90, 96),
        (62, 116), (30, 126), (2, 124), (-30, 112), (-60, 88), (-88, 46), (-104, -10), (-98, -70), (-68, -108)]
EYE_N = (16, -12, 50, 51)
EYE_F = (92, -10, 39, 47)
PX, PY, PR = 632, 772, -8              # телефон: центр, поворот


def dima_back():
    """Капюшон за шеей, дальнее плечо, туловище, шея — всё, что под головой."""
    s = []
    # капюшон смят между спиной и спинкой дивана
    hood = [(172, 1080), (179, 1018), (210, 984), (255, 974), (297, 1000), (346, 1018), (396, 1020), (423, 1040), (405, 1080),
            (322, 1090), (230, 1096)]
    inner = blob([(179, 1018), (210, 984), (255, 974), (272, 1000), (230, 1040), (189, 1070)], HOOD_SH2, .95)
    inner += line([(194, 1030), (222, 1000), (257, 990)], 3, FOLD, seed=140, op=.85)
    inner += line([(214, 1060), (247, 1030), (288, 1024)], 2.6, FOLD, seed=139, op=.7)
    s.append(shape(hood, HOOD, inner, w=5.2, seed=141, id="dima_hood"))
    # туловище: полулёжа — дальнее плечо выше и левее, грудь уходит под плед
    body = [(127, 1300, 1), (124, 1160), (139, 1088), (180, 1048), (244, 1034), (297, 1044), (346, 1052), (396, 1050), (438, 1064),
            (473, 1100), (496, 1160), (509, 1300, 1)]
    inner = blob([(124, 1100), (189, 1060), (239, 1100), (222, 1300), (124, 1300)], HOOD_SH, .9)
    inner += blob([(438, 1064), (479, 1100), (509, 1190), (479, 1300), (446, 1190)], HOOD_SH, .75)
    # складки на животе — худи собралось, когда сполз
    for i, st in enumerate([[(214, 1140), (255, 1160), (288, 1200)], [(297, 1160), (322, 1190), (327, 1240)],
                            [(363, 1140), (346, 1180), (356, 1230)], [(172, 1190), (205, 1210), (222, 1250)],
                            [(263, 1220), (297, 1236), (313, 1270)], [(396, 1180), (413, 1210)]]):
        s_ = line(st, 3.4 - (i % 3) * .4, FOLD, seed=142 + i, op=.85)
        inner += s_
    # шов плеча
    inner += line([(172, 1070), (189, 1120), (194, 1170)], 2.2, FOLD, seed=150, op=.6)
    s.append(shape(body, HOOD, inner, w=5.4, seed=145, id="dima_body"))
    # шея: кивательная мышца, кадык, тень под челюстью
    nk = [(268, 980), (335, 990), (346, 1056), (312, 1076), (273, 1062)]
    inner = blob([(268, 980), (335, 990), (340, 1030), (297, 1034), (268, 1020)], SKIN_SH, .95)
    inner += blob([(268, 980), (287, 990), (288, 1070), (268, 1070)], SKIN_SH2, .6)
    inner += line([(285, 1014), (300, 1040), (310, 1066)], 2.4, SKIN_SH2, seed=151, op=.9)
    inner += line([(323, 1034), (328, 1046)], 2.6, seed=152, op=.7)
    s.append(shape(nk, SKIN, inner, w=4.8, seed=146, id="dima_neck"))
    # вырез капюшона с рубчиком и шнурки
    collar = [(260, 1052), (290, 1074), (325, 1080), (356, 1060), (366, 1076), (330, 1102), (288, 1098), (253, 1072)]
    s.append(shape(collar, HOOD_SH, line([(265, 1070), (297, 1086), (335, 1090), (361, 1072)], 2, FOLD, seed=153, op=.7),
                   w=4.6, seed=147))
    for (x0, y0, x1, y1, sd) in [(302, 1096, 296, 1132, 148), (332, 1092, 360, 1124, 149)]:
        s.append(line([(x0, y0), ((x0 + x1) / 2 + 4, (y0 + y1) / 2), (x1, y1)], 6, "#efe3c4", taper=.2, wmin=.8, seed=sd))
        s.append(line([(x0, y0), ((x0 + x1) / 2 + 4, (y0 + y1) / 2), (x1, y1)], 1.8, INK, taper=.2, wmin=.8, seed=sd + 1, op=.55))
        s.append(shape(rect_pts(x1 - 5, y1, x1 + 5, y1 + 17, 2), "#b9b9c4", w=2.6, seed=sd + 2))
    return "".join(s)


def dima_head():
    s = [f'<g id="dima_head" transform="{head_tf()}">']
    back_hair = [(-60, -110), (-110, -86), (-150, -40, 1), (-122, -30), (-140, 10, 1), (-108, 6), (-100, 40, 1), (-80, 20), (-70, -40)]
    s.append(shape(back_hair, HAIR_SH, line([(-120, -50), (-100, -20)], 2.4, "#2a170f", seed=149, op=.8), w=4.8, seed=150))
    # ухо: завиток, козелок, мочка
    ear = [(-84, -18), (-108, -30), (-128, -8), (-126, 26), (-112, 50), (-92, 54), (-82, 44)]
    s.append(shape(ear, SKIN, blob([(-128, -8), (-126, 26), (-112, 50), (-112, 14)], SKIN_SH, .9), w=4.8, seed=151))
    s.append(line([(-96, 34), (-116, 22), (-114, -4), (-100, -14)], 3.2, seed=152))
    s.append(line([(-104, 6), (-96, 14), (-100, 24)], 2.4, seed=158, op=.8))
    inner = []
    # конструкция объёма: затылочная сторона в тени (свет экрана справа), висок, впадина под скулой, подбородок
    inner.append(blob([(-110, -130), (-36, -130), (-58, -40), (-54, 40), (-20, 130), (-110, 130)], SKIN_SH, .95))
    inner.append(blob([(-60, -60), (-34, -66), (-40, -20), (-62, -10)], SKIN_SH2, .5))
    inner.append(blob([(70, 40), (112, 42), (106, 70), (80, 74)], SKIN_SH, .55))
    inner.append(blob([(-20, 104), (40, 118), (96, 92), (110, 140), (-30, 140)], SKIN_SH, .85))
    inner.append(blob([(-60, 70), (-20, 92), (30, 106), (80, 94), (106, 70), (110, 130), (-60, 130)], "#9e8a96", .42))
    rs = np.random.RandomState(7)
    for _ in range(120):
        x, y = rs.uniform(-56, 108), rs.uniform(70, 124)
        if (x - 30) ** 2 / 92 ** 2 + (y - 56) ** 2 / 70 ** 2 > 1.0 or y > 120 - abs(x - 30) * .15:
            continue
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rs.uniform(.9, 1.7):.1f}" fill="#5c4446" opacity=".55"/>')
    inner.append(blob(ellipse_pts(54, -10, 100, 62, 14), "#d9a08f", .3))
    s.append(shape(FACE, SKIN, "".join(inner), w=5.6, seed=153, id="dima_face"))
    # линия челюсти и подбородок (конструкция низа лица)
    s.append(line([(-66, 70), (-30, 104), (6, 118)], 2.4, SKIN_SH2, seed=159, op=.8))
    s.append(line([(30, 112), (44, 116), (56, 112)], 2.6, seed=167, op=.75))
    # мешки под глазами
    for (cx, cy, rx, ry, sd) in [(*EYE_N, 154), (*EYE_F, 155)]:
        bag = [(cx - rx * .85, cy + ry * .55), (cx, cy + ry * 1.38), (cx + rx * .85, cy + ry * .55), (cx, cy + ry * .9)]
        s.append(blob(bag, "#a77f8c", .78))
        s.append(line([(cx - rx * .8, cy + ry * .7), (cx, cy + ry * 1.36), (cx + rx * .75, cy + ry * .75)], 3.3, seed=sd))
        if sd == 154:
            s.append(line([(cx - rx * .5, cy + ry * 1.27), (cx + rx * .05, cy + ry * 1.62), (cx + rx * .5, cy + ry * 1.32)], 2.2,
                          seed=sd + 5, op=.75))
    # глаза: белки, зрачки, веки
    for nm, (cx, cy, rx, ry), sd in [("F", EYE_F, 160), ("N", EYE_N, 161)]:
        ep = ellipse_pts(cx, cy, rx, ry, 14)
        cid = clip_of(ep)
        s.append(f'<g id="dima_eye_{nm}"><path d="{fill_d(ep)}" fill="#f6f2ea"/><g clip-path="url(#{cid})">')
        s.append(blob([(cx - rx, cy - ry), (cx + rx, cy - ry), (cx + rx, cy + 8), (cx - rx, cy + 4)], "#c9c2d6", .9))
        s.append(f'<g id="dima_pupil_{nm}"><ellipse cx="{cx + rx * .40:.1f}" cy="{cy + 16:.1f}" rx="6.8" ry="7.6" fill="{INK}"/>'
                 f'<circle cx="{cx + rx * .40 + 2.4:.1f}" cy="{cy + 13:.1f}" r="1.8" fill="#dfe9ff"/></g>')
        lid_y = cy - ry * .02
        lid = [(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 6), (cx + rx * .4, lid_y + 4),
               (cx - rx * .3, lid_y + 1), (cx - rx - 10, lid_y - 10)]
        s.append(f'<g id="dima_lid_{nm}">')
        s.append(blob(lid, SKIN))
        s.append(blob([(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 20), (cx - rx - 10, lid_y - 22)],
                      "#d9a08f", .5))
        s.append(line([(cx - rx * .7, lid_y - 16), (cx, lid_y - 13), (cx + rx * .6, lid_y - 15)], 2, SKIN_SH2, seed=sd + 7, op=.7))
        s.append(line([(cx - rx - 6, lid_y - 9), (cx - rx * .3, lid_y + 1.5), (cx + rx * .4, lid_y + 4), (cx + rx + 6, lid_y - 5)],
                      6.4, seed=sd, taper=.4, wmin=.35))
        s.append("</g></g>")
        s.append(f'<path d="{ink_closed(ep, 4.7, seed=sd + 2)}" fill="{INK}"/></g>')
    # надбровье и брови
    s.append(line([(-30, -76), (4, -86), (46, -80)], 8, HAIR_SH, seed=162, peak=.4))
    s.append(line([(72, -80), (100, -86), (126, -76)], 6.8, HAIR_SH, seed=163, peak=.55))
    s.append(line([(-20, -64), (10, -70), (38, -66)], 2, SKIN_SH2, seed=168, op=.6))
    # нос в 3/4: спинка, кончик, крыло, ноздря, тень снизу; носогубная складка
    s.append(blob([(50, 30), (62, 58), (54, 66), (44, 56)], SKIN_SH, .9))
    s.append(line([(58, 22), (76, 50), (72, 63), (58, 65)], 4.6, seed=164, peak=.45))
    s.append(line([(50, 58), (56, 63)], 2.4, seed=169, op=.8))
    s.append(blob(ellipse_pts(64, 69, 8, 3, 8), SKIN_SH2, .7))
    s.append(line([(44, 70), (38, 80), (36, 88)], 2.2, SKIN_SH2, seed=170, op=.75))
    # рот: усталая гримаса, верхняя губа, тень под нижней
    s.append('<g id="dima_mouth">')
    s.append(line([(38, 88), (60, 85), (82, 88), (92, 94)], 4.8, seed=165, peak=.45))
    s.append(line([(48, 82), (64, 80), (78, 83)], 2, SKIN_SH2, seed=171, op=.7))
    s.append(blob([(50, 96), (76, 96), (72, 104), (54, 104)], SKIN_SH, .8))
    s.append(line([(54, 100), (72, 100)], 2.4, seed=166, op=.7))
    s.append("</g>")
    hair = [(108, -40), (104, -78), (82, -110), (94, -152, 1), (52, -128), (36, -172, 1), (8, -138), (-18, -180, 1), (-40, -136),
            (-86, -164, 1), (-90, -128), (-144, -130, 1), (-112, -96), (-158, -78, 1), (-118, -64), (-142, -34, 1), (-104, -38),
            (-94, -14, 1), (-80, -42), (-62, -70), (-22, -88), (12, -92), (30, -76, 1), (50, -98), (80, -86, 1), (98, -62), (108, -40, 1)]
    inner = blob([(-160, -190), (-20, -190), (-30, -130), (-70, -100), (-80, -40), (-160, -20)], HAIR_SH, .95)
    inner += blob([(10, -150), (60, -120), (100, -80), (70, -112), (40, -128)], HAIR_HI, .9)
    inner += blob([(-24, -170), (-4, -140), (-14, -120), (-30, -140)], HAIR_HI, .6)
    for i, st in enumerate([[(-10, -150), (-30, -120), (-60, -100)], [(30, -140), (10, -110), (-20, -96)], [(70, -120), (60, -100), (40, -94)],
                            [(-70, -130), (-96, -110), (-112, -84)], [(-40, -100), (-70, -80), (-84, -56)], [(50, -140), (30, -120)],
                            [(-110, -110), (-130, -92)]]):
        inner += line(st, 3.2, "#2a170f", seed=172 + i, op=.85)
    s.append(shape(hair, HAIR, inner, w=5.4, seed=171, id="dima_hair"))
    s.append("</g>")
    return "".join(s)


def dima_arm():
    """Ближняя рука: плечо → локоть на пледе → предплечье вверх. Рукав со складками, манжета в рубчик."""
    s = []
    up = [(392, 1046), (446, 1058), (488, 1100), (526, 1160), (556, 1214), (530, 1246), (490, 1236), (462, 1190), (420, 1130), (388, 1086)]
    inner = blob([(460, 1066), (500, 1110), (556, 1214), (530, 1246), (510, 1170)], HOOD_SH, .9)
    for i, st in enumerate([[(430, 1096), (452, 1124), (450, 1150)], [(470, 1150), (492, 1180)], [(420, 1136), (436, 1172), (452, 1192)]]):
        inner += line(st, 3, FOLD, seed=180 + i, op=.85)
    s.append(shape(up, HOOD, inner, w=5.4, seed=183, id="dima_upperarm"))
    # предплечье: от локтя вверх к кисти; у локтя рукав собран гармошкой, у манжеты — напуск
    fa = [(510, 1230), (518, 1164), (566, 1060), (584, 990), (598, 934), (668, 936), (660, 1000), (642, 1070), (592, 1174), (574, 1242), (540, 1252)]
    inner = blob([(640, 930), (676, 930), (580, 1254), (560, 1254), (628, 1080)], HOOD_SH, .9)
    folds = [[(522, 1194), (544, 1182), (558, 1200)], [(526, 1164), (550, 1152), (568, 1168)], [(536, 1132), (590, 1098), (576, 1136)],
             [(596, 960), (620, 972), (650, 962)], [(588, 1000), (612, 1010), (640, 1004)], [(600, 1040), (618, 1030)],
             [(576, 1060), (590, 1074)]]
    for i, st in enumerate(folds):
        inner += line(st, 3.2 if i < 3 else 2.6, FOLD, seed=184 + i, op=.85)
    inner += line([(530, 1224), (556, 1204), (574, 1224)], 3.4, FOLD, seed=191, op=.9)
    s.append(shape(fa, HOOD, inner, w=5.4, seed=192, id="dima_forearm"))
    cuff = [(596, 940), (594, 906), (664, 904), (668, 940)]
    rib = "".join(line([(x, 908), (x + 1, 938)], 2, HOOD_SH2, seed=x, op=.85) for x in range(600, 666, 8))
    s.append(shape(cuff, HOOD_SH, rib, w=4.8, seed=193, id="dima_cuff"))
    return "".join(s)


def dima_phone_hand():
    """Телефон спинкой к зрителю; кисть держит его сзади: видна тыльная сторона, костяшки, пальцы загибаются
    за правый край (каждый палец отдельно, с суставом), большой палец — на экране у левого края."""
    s = [f'<g id="dima_hand_phone" transform="translate({PX} {PY}) rotate({PR})">']
    # телефон
    side = [(-46, -94), (-60, -88), (-62, 88), (-46, 96)]
    s.append(shape(side, "#2e2e3a", "", w=3.6, seed=187, id="phone_side"))
    back = rect_pts(-46, -98, 46, 98, 18)
    inner = blob([(14, -98), (46, -98), (46, 98), (26, 98)], "#24242c", .95)
    inner += blob([(-46, -98), (-30, -98), (-32, 98), (-46, 98)], "#4c4c5c", .75)
    inner += blob([(-24, -98), (-14, -98), (-18, 98), (-28, 98)], "#3a3a48", .5)
    s.append(shape(back, "#1a1a21", inner, w=4.8, seed=188, id="phone"))
    cam = rect_pts(-38, -90, 4, -46, 11)
    s.append(shape(cam, "#34343f", blob(rect_pts(-38, -64, 4, -46, 6), "#26262f") + blob([(-36, -88), (2, -88), (0, -84), (-34, -84)], "#55556a"),
                   w=3.6, seed=189))
    for (lx, ly) in [(-25, -78), (-25, -57), (-8, -67)]:
        s.append(shape(ellipse_pts(lx, ly, 9.5, 9.5, 10), "#55556a", w=2.8, seed=int(abs(lx * ly)) % 97,
                       inner=f'<circle cx="{lx}" cy="{ly}" r="6.6" fill="#0c0c12"/><circle cx="{lx}" cy="{ly}" r="3.6" fill="#1d2848"/>'
                             f'<circle cx="{lx - 2.4}" cy="{ly - 2.4}" r="1.8" fill="#a9bdf0"/>'))
    s.append('<circle cx="-8" cy="-82" r="3.2" fill="#e8e0c8"/><circle cx="-8" cy="-52" r="2.8" fill="#121218"/>')
    # пальцы (под тыльной стороной: их основания уходят под ладонь) — указательный сверху, мизинец ниже и короче
    fingers = [((20, -6), (56, -12), 22), ((24, 20), (62, 18), 23), ((22, 46), (60, 48), 22), ((14, 70), (50, 76), 19)]
    for i, ((x0, y0), (x1, y1), wd) in enumerate(fingers):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - 3
        fp = band([(x0, y0), (mx, my), (x1, y1), (x1 + 6, y1 + 8)], wd, wd * .88, cap=True)
        inner = blob([(x0 - 4, y0 + 4), (x1 + 12, y1 + 4), (x1 + 12, y1 + 16), (x0 - 4, y0 + 16)], SKIN_SH, .85)
        inner += blob(ellipse_pts(x1 + 2, y1 - 2, 8, 6, 8), "#f5d6bb", .7)      # средняя фаланга на сгибе — светлее
        s.append(shape(fp, SKIN, inner, w=4.2, seed=190 + i, id=f"dima_finger{i}"))
        s.append(line([(x1 - 6, y1 - wd * .42), (x1 - 3, y1), (x1 - 6, y1 + wd * .38)], 2.2, seed=196 + i, op=.8))   # складки сустава
        s.append(line([(x1 - 12, y1 - wd * .3), (x1 - 10, y1 + wd * .2)], 1.6, SKIN_SH2, seed=200 + i, op=.8))
    # тыльная сторона кисти и запястье (поверх оснований пальцев): костяшки буграми, сухожилия
    dor = [(-58, 150), (-60, 110), (-62, 70), (-54, 34), (-30, 16), (0, 8), (22, -14, 1), (34, 4), (36, 30), (34, 56), (26, 82), (14, 112),
           (8, 150)]
    inner = blob([(-62, 60), (-30, 70), (-10, 150), (-62, 150)], SKIN_SH, .9)
    inner += blob([(10, 0), (36, 0), (36, 90), (14, 112)], SKIN_SH, .55)
    for i, (kx, ky) in enumerate([(26, -6), (30, 20), (28, 46), (20, 70)]):
        inner += blob(ellipse_pts(kx - 4, ky, 9, 7, 8), "#f6d9bf", .75)
        inner += line([(kx - 10, ky - 6), (kx - 6, ky + 6)], 1.6, SKIN_SH2, seed=210 + i, op=.7)
    for i, (y0, y1) in enumerate([(-2, 100), (24, 110), (48, 118)]):
        inner += line([(18 - i * 2, y0 + 6), (-6 - i * 6, y1)], 1.8, SKIN_SH2, seed=214 + i, op=.55)
    inner += line([(-40, 128), (-20, 132), (0, 128)], 2, SKIN_SH2, seed=217, op=.6)
    s.append(shape(dor, SKIN, inner, w=4.8, seed=218, id="dima_dorsum"))
    # большой палец — у левого края, кончик с ногтем лежит на экране (анимируется)
    s.append('<g id="dima_thumb">')
    th = band([(-50, 62), (-66, 34), (-72, 6), (-66, -18)], 27, 21, cap=True)
    s.append(shape(th, SKIN, blob([(-96, 0), (-70, 0), (-62, 80), (-96, 80)], SKIN_SH, .75), w=4.5, seed=219, id="dima_thumb_shape"))
    s.append(shape([(-64, -20), (-58, -26), (-54, -14), (-58, -6)], "#f2d2c4", w=2, seed=220))
    s.append(line([(-74, 22), (-62, 26)], 2, seed=221, op=.7))
    s.append("</g>")
    s.append("</g>")
    return "".join(s)


def dima():
    return dima_back() + dima_head() + dima_arm() + dima_phone_hand()


# ═════════════════════════════ ПЛЕД ═════════════════════════════
PLAID_TOP = [(36, 1250), (70, 1196), (140, 1170), (250, 1166), (360, 1172), (440, 1196), (500, 1230), (560, 1236), (620, 1196),
             (690, 1140), (740, 1128), (800, 1150), (880, 1190), (960, 1196), (1000, 1168), (1040, 1160), (1092, 1180, 1)]
EDGE_Y = 1252        # где плед перегибается через край сиденья


def plaid_patterns():
    DEFS.append("""
<pattern id="pPlaid" width="88" height="88" patternUnits="userSpaceOnUse">
 <rect width="88" height="88" fill="#7aa66a"/>
 <rect x="0" width="34" height="88" fill="#5b8a50" opacity=".85"/>
 <rect y="0" width="88" height="34" fill="#5b8a50" opacity=".85"/>
 <rect width="34" height="34" fill="#3f6b3c"/>
 <rect x="56" width="5" height="88" fill="#d9e3a8" opacity=".75"/><rect y="56" width="88" height="5" fill="#d9e3a8" opacity=".75"/>
 <rect x="15" width="3" height="88" fill="#2a4630"/><rect y="15" width="88" height="3" fill="#2a4630"/>
 <rect x="74" width="2" height="88" fill="#a33f35" opacity=".8"/><rect y="74" width="88" height="2" fill="#a33f35" opacity=".8"/>
</pattern>
<pattern id="pPlaidTop" href="#pPlaid" patternTransform="rotate(-3) scale(1 .5)"/>
<pattern id="pPlaidFront" href="#pPlaid" patternTransform="rotate(1) translate(30 6)"/>
""")


def plaid():
    """Плед одним куском: верх по ногам (колено, голени, ступни) и свес через край сиденья веером складок.
    Перегиб — мягкий блик и тень, без шва; узор сверху в ракурсе, спереди — прямо."""
    plaid_patterns()
    s = []
    folds = [70, 190, 330, 470, 610, 760, 900, 1040]          # гребни складок свеса
    bottom = []
    for i in range(len(folds) - 1):
        xa, xb = folds[i], folds[i + 1]
        bottom += [(xa, 1478 - (i % 2) * 6), ((xa + xb) / 2, 1448 + (i % 3) * 4)]
    bottom = [(1092, 1462)] + bottom[::-1] + [(30, 1452)]
    outline = PLAID_TOP + [(1092, 1300), (1094, 1462, 1)] + bottom[1:-1] + [(30, 1452, 1), (22, 1360), (30, 1290)]
    inner = []
    inner.append(f'<rect x="0" y="1100" width="{W}" height="{EDGE_Y - 1100}" fill="url(#pPlaidTop)"/>')
    inner.append(f'<rect x="0" y="{EDGE_Y}" width="{W}" height="300" fill="url(#pPlaidFront)"/>')
    # верх: тени за коленом и у ступней, блики на колене и груди
    inner.append(blob([(740, 1128), (800, 1150), (880, 1190), (880, EDGE_Y), (760, EDGE_Y), (790, 1190)], "#203a24", .35))
    inner.append(blob([(960, 1196), (1000, 1168), (1010, EDGE_Y), (950, EDGE_Y)], "#203a24", .3))
    inner.append(blob([(620, 1196), (690, 1140), (740, 1128), (700, 1170), (640, 1210)], "#eef6c8", .18))
    inner.append(blob([(140, 1170), (300, 1166), (400, 1176), (330, 1190), (160, 1190)], "#eef6c8", .14))
    for i, st in enumerate([[(200, 1176), (236, 1210), (240, EDGE_Y - 6)], [(420, 1196), (450, 1226)], [(650, 1176), (680, 1214)],
                            [(820, 1172), (850, 1210)], [(1010, 1176), (1030, 1220)], [(110, 1190), (130, 1230)]]):
        inner.append(line(st, 3.2, seed=230 + i, op=.8))
    # перегиб через край сиденья: округлый блик, под ним тень
    inner.append(blob([(0, EDGE_Y - 14), (W, EDGE_Y - 16), (W, EDGE_Y + 4), (0, EDGE_Y + 6)], "#eef6c8", .16))
    inner.append(blob([(0, EDGE_Y + 8), (W, EDGE_Y + 6), (W, EDGE_Y + 44), (0, EDGE_Y + 46)], "#0f1d12", .35))
    # свес: впадины темнее и шире книзу, гребни светлее, линии складок частично
    for i in range(len(folds) - 1):
        xa, xb = folds[i], folds[i + 1]
        xm = (xa + xb) / 2
        inner.append(blob([(xm - 10, EDGE_Y + 30), (xm + 6, EDGE_Y + 30), (xm + 26, 1400), (xm + 30, 1490), (xm - 34, 1490), (xm - 26, 1400)],
                          "#132416", .45, blur(9)))
        inner.append(blob([(xa - 6, EDGE_Y + 40), (xa + 6, EDGE_Y + 40), (xa + 20, 1490), (xa - 18, 1490)], "#eef6c8", .12, blur(7)))
        inner.append(line([(xm - 2, EDGE_Y + 40), (xm + 4, 1380), (xm + 10, 1460)], 3, seed=240 + i, op=.7, peak=.7))
    inner.append(blob([(0, 1390), (W, 1390), (W, 1490), (0, 1490)], "#0f1d12", .3))
    s.append(shape(outline, "#5b8a50", "".join(inner), w=5.4, seed=245, id="plaid"))
    S_ = sample(bottom, False, step=10)
    rs = np.random.RandomState(9)
    for i, (x, y) in enumerate(S_):
        ln = rs.uniform(14, 22)
        s.append(line([(x, y - 2), (x + rs.uniform(-3, 3), y + ln * .5), (x + rs.uniform(-4, 4), y + ln)], 3.6, "#4f7c48",
                      seed=300 + i, taper=.6, wmin=.3, peak=.3))
    # контактные тени руки Димы и кота на пледе
    s.append(blob([(470, 1226), (570, 1236), (580, 1262), (470, 1258)], "#0d160f", .55, blur(6)))
    s.append(blob(ellipse_pts(860, 1250, 120, 20, 12), "#0d160f", .7, blur(7)))
    return "".join(s)


# ═════════════════════════════ КОТ ═════════════════════════════
CAT, CAT_SH, CAT_FUR, CAT_EDGE = "#3a3646", "#211e29", "#56506a", "#6c6688"
CX, CBOT = 836, 1306                     # опорные точки рисунка (внутренние координаты)
CAT_TF = "translate(850 1244) scale(1.1) translate(-836 -1306)"
TAIL_C = [(900, 1272), (970, 1266), (1020, 1236), (1048, 1186), (1052, 1130), (1036, 1082), (1006, 1050), (976, 1046), (956, 1064),
          (960, 1086), (980, 1090)]
FLAME_BASE = (1000, 1046)
TAIL_PIVOT = (912, 1272)


def cat_to_g(x, y):
    return 850 + (x - 836) * 1.1, 1244 + (y - 1306) * 1.1


def flame_pts(k=1.0):
    bx, by = FLAME_BASE
    P = [(-22, 4), (-26, -18), (-16, -40), (-14, -62), (-4, -50), (2, -86, 1), (12, -58), (22, -70, 1), (26, -40), (24, -12), (16, 4), (0, 10)]
    return [(bx + q[0] * k, by + q[1] * k) + ((1,) if len(q) > 2 else ()) for q in P]


FLAME_K = 1.3


def cat_art():
    s = [f'<g id="cat" transform="{CAT_TF}">']
    s.append('<g id="cat_tail">')
    tp = fur(band(TAIL_C, 46, 16, step=7), 5, 7, seed=21)
    s.append(shape(tp, CAT, blob([(1010, 1060), (1060, 1110), (1046, 1272), (990, 1278)], CAT_SH, .85) +
                   line([(990, 1240), (1010, 1206), (1018, 1170)], 2.4, CAT_EDGE, seed=231, op=.9) +
                   line([(972, 1072), (978, 1060), (990, 1058)], 2.4, INK, seed=232, op=.9), w=4.8, seed=230, id="cat_tail_shape"))
    s.append("</g>")
    body = [(760, 1296), (744, 1240), (756, 1180), (790, 1142), (880, 1142), (916, 1180), (928, 1240), (912, 1296)]
    bp = fur(body, 7, 7, seed=22)
    inner = blob([(860, 1140), (930, 1180), (930, 1300), (874, 1300), (888, 1220)], CAT_SH, .9)
    inner += blob([(798, 1170), (836, 1160), (874, 1170), (864, 1244), (836, 1266), (808, 1244)], CAT_FUR, .6)
    for i, st in enumerate([[(816, 1190), (826, 1208)], [(852, 1192), (846, 1212)], [(834, 1214), (836, 1236)], [(806, 1222), (814, 1238)],
                            [(864, 1226), (858, 1244)]]):
        inner += line(st, 2.2, CAT_EDGE, seed=240 + i, op=.85)
    s.append(shape(bp, CAT, inner, w=5, seed=241, id="cat_body"))
    for sx, sd in [(-1, 242), (1, 243)]:
        px = CX + sx * 70
        foot = ellipse_pts(px, 1286, 34, 26, 12, rot=sx * 12)
        s.append(shape(foot, CAT, blob(T(ellipse_pts(px, 1292, 26, 20, 10), sx * 4, 0), CAT_SH, .5), w=4.6, seed=sd))
        s.append(blob(ellipse_pts(px + sx * 3, 1296, 13, 10, 10, rot=sx * 10), "#e8823a"))
        for k in range(3):
            ang = math.radians(-90 + (k - 1) * 42 + sx * 10)
            s.append(blob(ellipse_pts(px + sx * 3 + math.cos(ang) * 19, 1296 + math.sin(ang) * 15, 5, 4.4, 8), "#e8823a"))
    for sx, sd in [(-1, 244), (1, 245)]:
        fx = CX + sx * 25
        paw = [(fx - 20, 1306, 1), (fx - 19, 1252), (fx + 19, 1252), (fx + 20, 1306, 1)]
        s.append(shape(paw, CAT, blob([(fx + sx * 6, 1250), (fx + 20 * sx, 1250), (fx + 20 * sx, 1306), (fx + sx * 8, 1306)], CAT_SH, .7),
                       w=4.6, seed=sd))
        for k in (-7, 7):
            s.append(line([(fx + k, 1294), (fx + k, 1306)], 2.2, seed=sd + k))
    # уши: правое стоит; левое — ухо с розовым, верхушка загнута наружу пушистой «шапочкой» (как у эталона)
    re_ = [(864, 1010), (902, 924, 1), (930, 1034)]
    s.append(shape(re_, CAT, blob([(878, 1010), (902, 948), (918, 1024)], "#9b6150") +
                   line([(886, 1000), (898, 968)], 2, "#d79a84", seed=252, op=.8) + line([(892, 1010), (904, 984)], 1.6, "#d79a84", seed=257, op=.6),
                   w=4.8, seed=251, id="cat_ear_R"))
    ear = [(748, 1032, 1), (742, 990), (746, 958), (770, 942), (798, 952), (812, 1004, 1)]
    s.append(shape(ear, CAT, blob([(758, 1022), (768, 972), (804, 1004)], "#9b6150") +
                   line([(764, 1010), (772, 984)], 2, "#d79a84", seed=256, op=.8), w=4.6, seed=253))
    flap = [(730, 1002, 1), (726, 968), (740, 946), (770, 934), (800, 940), (812, 960), (804, 980), (780, 984), (758, 990)]
    s.append(shape(fur(flap, 4, 5, seed=26), CAT, blob([(736, 966), (754, 944), (782, 938), (790, 950), (760, 956)], CAT_FUR, .7),
                   w=4.6, seed=254, id="cat_ear_L"))
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884, 990), (940, 1050), (930, 1150), (866, 1150), (902, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    inner += blob([(800, 1106), (836, 1098), (872, 1106), (864, 1142), (808, 1142)], CAT_FUR, .45)
    for i, st in enumerate([[(800, 1004), (806, 1016)], [(836, 996), (838, 1010)], [(870, 1002), (866, 1014)]]):
        inner += line(st, 2, CAT_EDGE, seed=258 + i, op=.8)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250, id="cat_head"))
    # полоски, нос, рот, усы
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76
            s.append(line([(x0, 1100 + dy), (x0 + sx * 30, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    s.append(shape([(826, 1108), (846, 1108), (836, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836, 1119), (836, 1124)], 2.4, seed=263))
    s.append(line([(822, 1124), (829, 1131), (836, 1124), (843, 1131), (850, 1124)], 3, seed=264))
    s.append("</g>")
    return "".join(s)


def cat_eyes():
    """Глаза кота — поверх ночи (отражают свет), веки для моргания цвета ночной шерсти."""
    lid_c = night_hex(CAT)
    s = [f'<g id="cat_eyes" transform="{CAT_TF}">']
    for nm, ex, sd in [("L", CX - 44, 255), ("R", CX + 44, 256)]:
        ep = ellipse_pts(ex, 1072, 34, 38, 14)
        cid = clip_of(ep)
        s.append(f'<g id="cat_eye_{nm}"><path d="{fill_d(ep)}" fill="#a9d84a"/><g clip-path="url(#{cid})">')
        s.append(blob(ellipse_pts(ex, 1046, 36, 20, 10), "#6f9a2e", .95))
        s.append(blob(ellipse_pts(ex, 1102, 26, 11, 10), "#d4f27a", .75))
        s.append(blob(ellipse_pts(ex - 18, 1080, 10, 20, 8), "#c8ee6a", .5))
        s.append(f'<g id="cat_pupil_{nm}"><ellipse cx="{ex}" cy="1074" rx="11.5" ry="24" fill="#0b0a10"/></g>')
        # блики: большой от экрана (сверху слева), малый тёплый от огонька (справа)
        s.append(f'<circle cx="{ex - 8}" cy="1058" r="7" fill="#f4f8ff"/><circle cx="{ex + 10}" cy="1088" r="3.2" fill="#ffd9a0"/>')
        s.append(f'<g id="cat_lid_{nm}" transform="translate(0 -84)"><rect x="{ex - 40}" y="990" width="80" height="84" fill="{lid_c}"/>'
                 + line([(ex - 36, 1070), (ex, 1076), (ex + 36, 1070)], 4.6, seed=sd) + "</g>")
        s.append(f'<g id="cat_lidlo_{nm}" transform="translate(0 48)"><rect x="{ex - 40}" y="1072" width="80" height="50" fill="{lid_c}"/></g>')
        s.append(f'</g><path d="{ink_closed(ep, 4.4, seed=sd + 3)}" fill="{INK}"/></g>')
    # усы поверх (тонкие, светлые — читаются на тёмном)
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CX + sx * 62
            s.append(line([(x0, 1114 + dy), (x0 + sx * 50, 1110 + dy + dl * .4), (x0 + sx * 92, 1106 + dy + dl)], 1.9, "#b9b6cc",
                          seed=270 + k + sx, op=.75))
    s.append("</g>")
    return "".join(s)


def cat_flame():
    k = FLAME_K
    bx, by = FLAME_BASE
    s = [f'<g id="cat_flame_rot" transform="{CAT_TF}"><g id="cat_flame">']
    s.append(f'<ellipse cx="{bx}" cy="{by - 34 * k}" rx="{40 * k}" ry="{58 * k}" fill="#ff8a2a" opacity=".28" {blur(10)}/>')
    s.append(shape(flame_pts(k), "#ff8a2a", blob(flame_pts(.7 * k), "#ffbe55"), w=3.4, seed=233, ink_color="#7a2a10", var=.2))
    s.append(blob([(bx - 8 * k, by + 2), (bx - 6 * k, by - 22 * k), (bx + 2 * k, by - 42 * k), (bx + 8 * k, by - 20 * k), (bx + 6 * k, by + 2)],
                  "#fff2c0"))
    s.append("</g></g>")
    return "".join(s)


# ═════════════════════════════ СВЕТ НА ГЕРОЯХ ═════════════════════════════
def light_defs():
    sx, sy = SCREEN_PX
    fx, fy = FLAME_C
    DEFS.append(f"""
<radialGradient id="gScr" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({sx} {sy}) scale(420 400)">
 <stop offset="0" stop-color="#a8ccff" stop-opacity=".85"/><stop offset=".3" stop-color="#6e9ef0" stop-opacity=".45"/>
 <stop offset=".7" stop-color="#4a6fc0" stop-opacity=".12"/><stop offset="1" stop-color="#4a6fc0" stop-opacity="0"/></radialGradient>
<radialGradient id="gFl" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({fx} {fy + 40}) scale(330 330)">
 <stop offset="0" stop-color="#ffb060" stop-opacity=".9"/><stop offset=".3" stop-color="#ff8a3a" stop-opacity=".45"/>
 <stop offset=".7" stop-color="#c05a22" stop-opacity=".12"/><stop offset="1" stop-color="#c05a22" stop-opacity="0"/></radialGradient>
<radialGradient id="gRimF" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({fx} {fy + 60}) scale(220 260)">
 <stop offset="0" stop-color="#ffc878"/><stop offset=".5" stop-color="#ff8a3a"/><stop offset="1" stop-color="#c05020" stop-opacity="0"/></radialGradient>
<radialGradient id="gRimS" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({sx} {sy}) scale(420 520)">
 <stop offset="0" stop-color="#b9d6ff"/><stop offset=".5" stop-color="#6f9ff0"/><stop offset="1" stop-color="#3a5cb0" stop-opacity="0"/></radialGradient>
<radialGradient id="gFaceL" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(150 -10) scale(230 210)">
 <stop offset="0" stop-color="#8ab0f4" stop-opacity=".8"/><stop offset=".55" stop-color="#5a80d0" stop-opacity=".35"/>
 <stop offset="1" stop-color="#3a5cb0" stop-opacity="0"/></radialGradient>
<filter id="fNight" x="0" y="0" width="100%" height="100%" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
 <feColorMatrix type="matrix" values="{NIGHT[0] * .9} {NIGHT[0] * .1} 0 0 0  {NIGHT[1] * .05} {NIGHT[1] * .9} {NIGHT[1] * .05} 0 0  0 {NIGHT[2] * .1} {NIGHT[2] * .9} 0 0  0 0 0 1 0"/>
</filter>
<filter id="fBlack" x="-50%" y="-50%" width="200%" height="200%" color-interpolation-filters="sRGB">
 <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"/></filter>
<filter id="fWhite" x="0" y="0" width="100%" height="100%" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
 <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>
""")


def mask_of(art_id):
    m = f"M_{art_id}"
    DEFS.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                f'<use href="#{art_id}" filter="url(#fWhite)"/></mask>')
    return m


def lights_dima():
    tf, hf = head_tf(), f"translate({PX} {PY}) rotate({PR})"
    hair = REG["dima_hair"]
    fc = clip_of(FACE)
    s = [f'<g id="scr_dima"><rect width="{W}" height="{H}" fill="url(#gScr)"/>']
    # лицо целиком светлее со стороны экрана (как в образце), волосы не светятся этим пятном
    s.append(f'<g transform="{tf}"><g clip-path="url(#{fc})"><rect x="-140" y="-140" width="280" height="280" fill="url(#gFaceL)"/>'
             f'<path d="{fill_d(hair)}" fill="#000"/></g></g>')
    s.append(rim(REG["dima_forearm"], "gRimS", 12, 10, .55))
    s.append(rim(REG["dima_cuff"], "gRimS", 8, 6, .5))
    s.append(rim(REG["dima_upperarm"], "gRimS", 6, 12, .35))
    s.append(f'<g transform="{hf}">{rim(REG["dima_dorsum"], "#7aa6f0", 10, 6, .55)}'
             f'<g id="thumb_rim">{rim(REG["dima_thumb_shape"], "#c4dcff", 8, 2, .7)}</g></g>')
    s.append("</g>")
    return "".join(s)


def lights_plaid():
    return (f'<g id="scr_plaid"><rect width="{W}" height="{H}" fill="url(#gScr)" opacity=".7"/></g>'
            f'<g id="fl_plaid"><rect width="{W}" height="{H}" fill="url(#gFl)" opacity=".85"/></g>')


def lights_cat():
    s = [f'<g id="fl_cat"><rect width="{W}" height="{H}" fill="url(#gFl)" opacity=".55"/>']
    # тёплый рим справа (огонёк), холодный слева (экран) — резкая cel-граница, гаснет с расстоянием
    s.append(f'<g transform="{CAT_TF}">')
    s.append(rim(REG["cat_head"], "gRimF", -10, 6, .95))
    s.append(rim(REG["cat_ear_R"], "gRimF", -7, 5, .9))
    s.append(rim(REG["cat_body"], "gRimF", -9, 2, .8))
    s.append(f'<g id="tail_rim">{rim(REG["cat_tail_shape"], "gRimF", -4, 9, .95)}</g>')
    s.append("</g></g>")
    s.append(f'<g id="scr_cat"><g transform="{CAT_TF}">')
    s.append(rim(REG["cat_head"], "#7d9cf0", 9, 4, .7))
    s.append(rim(REG["cat_ear_L"], "#7d9cf0", 6, 6, .7))
    s.append(rim(REG["cat_body"], "#7d9cf0", 8, 0, .5))
    s.append("</g></g>")
    return "".join(s)


def glow_dima():
    hf = f"translate({PX} {PY}) rotate({PR})"
    DEFS.append(f'<mask id="mThumb" maskUnits="userSpaceOnUse" x="-200" y="-200" width="400" height="400">'
                '<rect x="-200" y="-200" width="400" height="400" fill="#fff"/><use href="#dima_thumb" filter="url(#fBlack)"/></mask>')
    return (f'<g transform="{hf}" id="screen_edge" mask="url(#mThumb)">'
            + line([(-59, -82), (-61, 0), (-60, 84)], 4.6, "#d7ebff", taper=.3, wmin=.4, seed=320)
            + f'<path d="M-62 -84 L-64 86" stroke="#bfe0ff" stroke-width="10" opacity=".55" {blur(5)}/></g>')


def build():
    light_defs()
    a_dima, a_plaid = dima(), plaid()
    a_cat = cat_art()
    l_dima, l_plaid, l_cat = lights_dima(), lights_plaid(), lights_cat()
    layers = []
    for name, art, lit, top in [("dima", a_dima, l_dima, glow_dima()), ("plaid", a_plaid, l_plaid, ""),
                                ("cat", a_cat, l_cat, cat_eyes() + cat_flame())]:
        m = mask_of(f"A_{name}")
        layers.append(f'<g id="L_{name}" style="isolation:isolate"><g id="A_{name}" filter="url(#fNight)">{art}</g>'
                      f'<g style="mix-blend-mode:screen" mask="url(#{m})">{lit}</g>{top}</g>')
    return (f'<svg id="scene" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{"".join(DEFS)}</defs>{"".join(layers)}</svg>')


if __name__ == "__main__":
    here = __file__.rsplit("/", 1)[0]
    svg = build()
    html = open(f"{here}/template.html").read().replace("<!--SVG-->", svg)
    open(f"{here}/heroes.html", "w").write(html)
    fx, fy = cat_to_g(FLAME_BASE[0], FLAME_BASE[1] - 40 * FLAME_K)
    print("heroes.html", len(html) // 1024, "KB; flame centre ≈", round(fx), round(fy))
