"""Герои рилса 23 «выбор» (сцена room): Дима с пастой и пультом, плед, кот, карточки и пар — SVG-слои с прозрачным фоном.

Раскладка — пиксели кадра 0 комнаты 22-го (1080×1920), рендер с увеличением S (layout.json). Камеру в слои не запекаем.
Каждый слой:
  арт в «дневных» цветах → ночь фильтром (умножение цвета, альфа не трогается) →
  свет экрана/огонька осветлением (screen) ТОЛЬКО по силуэту слоя (маска из самого арта) → светящееся поверх.
Запуск: python3 heroes23.py → heroes23.html (анимация — template23.html по ../../timing23.js).
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
TV_PX = (-260, 930)            # телевизор за кадром слева спереди: откуда свет на лицо
FLAME_C = (987, 934)           # центр огонька


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


def rim(pts, color, dx, dy, op=1.0, tf=None, id=None, cut=(), soft=4):
    """Рим-свет: фигура минус она же со сдвигом — полумесяц на стороне к источнику (в группе screen чёрное нейтрально)."""
    d = fill_d(pts)
    c = clip_of(pts)
    fill = f"url(#{color})" if color.startswith("g") else color
    gid = f' id="{id}"' if id else ""
    g = (f'<g{gid} clip-path="url(#{c})" opacity="{op}"><path d="{d}" fill="{fill}"/>'
         f'<path d="{d}" transform="translate({dx} {dy})" fill="#000" {blur(soft) if soft else ""}/>'
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

HX, HY, HR, HS = 292, 884, -8, 1.12   # голова: центр, наклон, масштаб; лицо зеркально — смотрит влево, на ТВ


def head_tf():
    return f"translate({HX} {HY}) rotate({HR}) scale({-HS} {HS})"


def H2G(x, y):
    c, s_ = math.cos(math.radians(HR)), math.sin(math.radians(HR))
    x = -x
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
    nk = [(294, 980), (361, 990), (372, 1056), (338, 1076), (299, 1062)]
    inner = blob([(294, 980), (361, 990), (366, 1030), (323, 1034), (294, 1020)], SKIN_SH, .95)
    inner += blob([(294, 980), (313, 990), (314, 1070), (294, 1070)], SKIN_SH2, .6)
    inner += line([(311, 1014), (326, 1040), (336, 1066)], 2.4, SKIN_SH2, seed=151, op=.9)
    inner += line([(349, 1034), (354, 1046)], 2.6, seed=152, op=.7)
    s.append(shape(nk, SKIN, inner, w=4.8, seed=146, id="dima_neck"))
    # вырез капюшона с рубчиком и шнурки
    collar = [(286, 1052), (316, 1074), (351, 1080), (382, 1060), (392, 1076), (356, 1102), (314, 1098), (279, 1072)]
    s.append(shape(collar, HOOD_SH, line([(291, 1070), (323, 1086), (361, 1090), (387, 1072)], 2, FOLD, seed=153, op=.7),
                   w=4.6, seed=147))
    for (x0, y0, x1, y1, sd) in [(328, 1096, 322, 1132, 148), (358, 1092, 386, 1124, 149)]:
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
        s.append(f'<g id="dima_pupil_{nm}"><ellipse cx="{cx + rx * .26:.1f}" cy="{cy + 12:.1f}" rx="6.8" ry="7.6" fill="{INK}"/>'
                 f'<circle cx="{cx + rx * .26 - 2.4:.1f}" cy="{cy + 9:.1f}" r="1.8" fill="#dfe9ff"/></g>')
        lid_y = cy - ry * .02
        lid = [(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 6), (cx + rx * .4, lid_y + 4),
               (cx - rx * .3, lid_y + 1), (cx - rx - 10, lid_y - 10)]
        s.append(f'<g id="dima_lid_{nm}" class="lid">')
        s.append(blob(lid, SKIN))
        s.append(blob([(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 20), (cx - rx - 10, lid_y - 22)],
                      "#d9a08f", .5))
        s.append(line([(cx - rx * .7, lid_y - 16), (cx, lid_y - 13), (cx + rx * .6, lid_y - 15)], 2, SKIN_SH2, seed=sd + 7, op=.7))
        s.append(line([(cx - rx - 6, lid_y - 9), (cx - rx * .3, lid_y + 1.5), (cx + rx * .4, lid_y + 4), (cx + rx + 6, lid_y - 5)],
                      6.4, seed=sd, taper=.4, wmin=.35))
        s.append("</g></g>")
        s.append(f'<path d="{ink_closed(ep, 4.7, seed=sd + 2)}" fill="{INK}"/></g>')
    # надбровье и брови
    s.append('<g id="brows_tired">' + line([(-30, -76), (4, -86), (46, -80)], 8, HAIR_SH, seed=162, peak=.4) +
             line([(72, -80), (100, -86), (126, -76)], 6.8, HAIR_SH, seed=163, peak=.55) + "</g>")
    s.append('<g id="brows_up" style="display:none">' + line([(-30, -90), (6, -106), (46, -98)], 8, HAIR_SH, seed=162, peak=.45) +
             line([(72, -98), (102, -108), (128, -94)], 6.8, HAIR_SH, seed=163, peak=.5) + "</g>")
    s.append('<g id="brows_calm" style="display:none">' + line([(-30, -80), (4, -86), (46, -78)], 8, HAIR_SH, seed=162, peak=.5) +
             line([(72, -78), (100, -84), (126, -78)], 6.8, HAIR_SH, seed=163, peak=.5) + "</g>")
    s.append(line([(-20, -64), (10, -70), (38, -66)], 2, SKIN_SH2, seed=168, op=.6))
    # нос в 3/4: спинка, кончик, крыло, ноздря, тень снизу; носогубная складка
    s.append(blob([(50, 30), (62, 58), (54, 66), (44, 56)], SKIN_SH, .9))
    s.append(line([(58, 22), (76, 50), (72, 63), (58, 65)], 4.6, seed=164, peak=.45))
    s.append(line([(50, 58), (56, 63)], 2.4, seed=169, op=.8))
    s.append(blob(ellipse_pts(64, 69, 8, 3, 8), SKIN_SH2, .7))
    s.append(line([(44, 70), (38, 80), (36, 88)], 2.2, SKIN_SH2, seed=170, op=.75))
    # рот: усталая гримаса, верхняя губа, тень под нижней
    s.append('<g id="m_tired">')
    s.append(line([(38, 88), (60, 85), (82, 88), (92, 94)], 4.8, seed=165, peak=.45))
    s.append(line([(48, 82), (64, 80), (78, 83)], 2, SKIN_SH2, seed=171, op=.7))
    s.append(blob([(50, 96), (76, 96), (72, 104), (54, 104)], SKIN_SH, .8))
    s.append(line([(54, 100), (72, 100)], 2.4, seed=166, op=.7))
    s.append("</g>")
    s.append('<g id="m_tense" style="display:none">')
    s.append(shape(ellipse_pts(64, 92, 11, 8, 10), "#5a2b33", blob(ellipse_pts(64, 97, 8, 3, 8), "#c86b6b"), w=3.6, seed=172))
    s.append(blob([(52, 104), (76, 104), (72, 110), (56, 110)], SKIN_SH, .8))
    s.append("</g>")
    s.append('<g id="m_smile" style="display:none">')
    s.append(line([(34, 84), (52, 94), (72, 96), (90, 88), (96, 80)], 4.8, seed=173, peak=.5))
    s.append(line([(30, 80), (36, 86)], 2.6, seed=174, op=.8))
    s.append(line([(90, 76), (98, 82)], 2.6, seed=175, op=.8))
    s.append(blob([(54, 102), (78, 102), (74, 108), (58, 108)], SKIN_SH, .7))
    s.append("</g>")
    s.append('<g id="m_open" style="display:none">')
    s.append(shape([(40, 84), (62, 82), (86, 86), (80, 104), (60, 110), (44, 100)], "#5a2b33",
                   blob([(48, 98), (70, 96), (78, 104), (60, 110)], "#c86b6b") +
                   line([(46, 86), (62, 88), (80, 88)], 3, "#f0e6d8", seed=176), w=4.2, seed=177))
    s.append("</g>")
    s.append('<g id="m_chew" style="display:none">')
    s.append(line([(36, 90), (56, 94), (76, 94), (92, 88)], 4.8, seed=178, peak=.5))
    s.append(blob(ellipse_pts(96, 74, 14, 12, 10), "#f3c2a4", .9))    # щека надута
    s.append(blob([(54, 102), (78, 102), (74, 108), (58, 108)], SKIN_SH, .7))
    s.append("</g>")
    # капля пота (s13) — на виске со стороны зрителя
    s.append('<g id="dima_sweat" style="display:none">')
    drop = [(104, -40), (110, -28), (114, -16), (110, -6), (102, -6), (98, -16), (100, -28)]
    s.append(shape(drop, "#cfe4ff", blob([(102, -20), (106, -30), (108, -18)], "#ffffff"), w=3, seed=179, ink_color="#2a3a6a"))
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


# ═════════════════════════════ КОТ ═════════════════════════════
CAT, CAT_SH, CAT_FUR, CAT_EDGE = "#3a3646", "#211e29", "#56506a", "#6c6688"
CX, CBOT = 836, 1306                     # опорные точки рисунка (внутренние координаты)
CAT_TF = "translate(812 1244) scale(1.1) translate(-836 -1306)"
TAIL_C = [(904, 1272), (962, 1266), (1004, 1240), (1014, 1198), (994, 1166), (962, 1166), (944, 1192), (954, 1224), (986, 1236),
          (1010, 1214), (1014, 1168), (1006, 1120), (996, 1080)]
FLAME_BASE = (995, 1076)
TAIL_PIVOT = (912, 1272)


def cat_to_g(x, y):
    return 812 + (x - 836) * 1.1, 1244 + (y - 1306) * 1.1


def flame_pts(k=1.0):
    bx, by = FLAME_BASE
    P = [(-22, 4), (-26, -18), (-16, -40), (-14, -62), (-4, -50), (2, -86, 1), (12, -58), (22, -70, 1), (26, -40), (24, -12), (16, 4), (0, 10)]
    return [(bx + q[0] * k, by + q[1] * k) + ((1,) if len(q) > 2 else ()) for q in P]


FLAME_K = 1.3


def tail_art():
    """Хвост одной фигурой: толщина 40→14, петля-завиток, поздняя часть петли лежит поверх ранней
    (перерисовывается заливкой и двумя боковыми линиями без торцов — шва нет)."""
    S = sample(TAIL_C, False, 3.0)
    n = len(S)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = 40 + (14 - 40) * np.linspace(0, 1, n) ** 1.2
    L, R = S + N * Wd[:, None] / 2, S - N * Wd[:, None] / 2
    tip = S[-1] + Tg[-1] * Wd[-1] * .45
    outline = [tuple(p) for p in L] + [tuple(tip)] + [tuple(p) for p in R[::-1]]
    REG["cat_tail_shape"] = outline
    inner = blob([(1000, 1100), (1060, 1100), (1060, 1280), (990, 1280)], CAT_SH, .8)
    out = [f'<path d="{fill_d(outline)}" fill="{CAT}"/>']
    c = clip_of(outline)
    out.append(f'<g clip-path="url(#{c})">{inner}</g>')
    out.append(f'<path d="{ink_closed(outline, 4.8, seed=230)}" fill="{INK}"/>')
    # поздний участок петли (после нижней точки петли) — поверх
    d_ = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    k0 = int(np.argmin(np.abs(S[:, 1] - 1236) + np.abs(S[:, 0] - 970) + (d_ < d_[-1] * .4) * 1e4))
    k1 = int(np.argmin(np.abs(S[:, 1] - 1172) + np.abs(S[:, 0] - 1014) + (d_ < d_[-1] * .5) * 1e4))
    seg = [tuple(p) for p in L[k0:k1]] + [tuple(p) for p in R[k0:k1][::-1]]
    out.append(f'<path d="{fill_d(seg)}" fill="{CAT}"/>')
    sc = clip_of(seg)
    out.append(f'<g clip-path="url(#{sc})">{blob([(1000, 1100), (1060, 1100), (1060, 1280), (990, 1280)], CAT_SH, .8)}</g>')
    for side, sd in ((L, 233), (R, 234)):
        pts = [tuple(p) for p in side[k0 - 2:k1 + 2:3]]
        out.append(line(pts, 4.8, seed=sd, taper=.1, wmin=.6, peak=.5))
    # шерсть-штрихи вдоль хвоста
    for i, k in enumerate(range(int(n * .1), int(n * .9), int(n * .12))):
        p = S[k] + N[k] * Wd[k] * .18
        q = p + Tg[k] * 12
        out.append(line([tuple(p), tuple(q)], 2, CAT_EDGE, seed=236 + i, op=.8))
    return "".join(out)


def cat_ears():
    """Уши поверх головы: заливка уходит в голову (закрывает её контур у основания), тушь — только по краю уха.
    Правое стоит; левое — мягко загнуто наружу-вниз, как у эталона, складка — тонкой линией."""
    s = []
    re_out = [(864, 1004), (902, 922, 1), (932, 1016)]
    re_fill = re_out + [(934, 1046), (866, 1046)]
    s.append(blob(re_fill, CAT))
    c = clip_of(re_fill)
    s.append(f'<g clip-path="url(#{c})">' + blob([(880, 1004), (902, 950), (918, 1008), (900, 1010)], "#9b6150") +
             blob([(904, 924), (940, 1000), (936, 1016), (918, 1014)], CAT_SH, .7) +
             line([(888, 1004), (898, 972)], 2, "#d79a84", seed=252, op=.8) + "</g>")
    s.append(line(re_out, 5, seed=251, taper=.25, wmin=.3))
    REG["cat_ear_R"] = re_fill
    le_out = [(752, 1014), (744, 986), (728, 994, 1), (728, 966), (746, 948), (772, 940), (796, 948), (808, 968), (814, 1006)]
    le_fill = le_out + [(816, 1046), (752, 1046)]
    s.append(blob(le_fill, CAT))
    c = clip_of(le_fill)
    s.append(f'<g clip-path="url(#{c})">' + blob([(762, 1002), (770, 980), (804, 996), (790, 1004)], "#9b6150") +
             blob([(728, 940), (812, 940), (806, 972), (770, 974), (744, 984), (726, 996)], CAT_FUR, .65) +
             line([(770, 998), (776, 984)], 2, "#d79a84", seed=256, op=.8) + "</g>")
    s.append(line([(740, 980), (770, 972), (800, 970)], 2.4, seed=255, op=.85))
    s.append(line(le_out, 5, seed=253, taper=.25, wmin=.3))
    REG["cat_ear_L"] = le_fill
    return "".join(s)


def cat_art():
    s = [f'<g id="cat" transform="{CAT_TF}">']
    s.append('<g id="cat_tail">')
    s.append(tail_art())
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
    s.append('<g id="cat_headg">')
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884, 990), (940, 1050), (930, 1150), (866, 1150), (902, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    inner += blob([(800, 1106), (836, 1098), (872, 1106), (864, 1142), (808, 1142)], CAT_FUR, .45)
    for i, st in enumerate([[(800, 1004), (806, 1016)], [(836, 996), (838, 1010)], [(870, 1002), (866, 1014)]]):
        inner += line(st, 2, CAT_EDGE, seed=258 + i, op=.8)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250, id="cat_head"))
    s.append(cat_ears())
    # полоски, нос, рот, усы
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76
            s.append(line([(x0, 1100 + dy), (x0 + sx * 30, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    s.append(shape([(826, 1108), (846, 1108), (836, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836, 1119), (836, 1124)], 2.4, seed=263))
    s.append('<g id="cat_mouth_n">' + line([(822, 1124), (829, 1131), (836, 1124), (843, 1131), (850, 1124)], 3, seed=264) + "</g>")
    s.append('<g id="cat_mouth_h" style="display:none">' + line([(818, 1122), (828, 1134), (836, 1126), (844, 1134), (854, 1122)], 3.2, seed=265) +
             "</g>")
    s.append("</g>")   # cat_headg
    s.append("</g>")
    return "".join(s)


def cat_eyes():
    """Глаза кота — поверх ночи (отражают свет), веки для моргания цвета ночной шерсти."""
    lid_c = night_hex(CAT)
    s = [f'<g id="cat_eyes" transform="{CAT_TF}"><g id="cat_eyes_tilt">']
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
                 + line([(ex - 34, 1066), (ex, 1078), (ex + 34, 1066)], 5.4, "#8f88b0", seed=sd) + "</g>")
        s.append(f'<g id="cat_lidlo_{nm}" transform="translate(0 48)"><rect x="{ex - 40}" y="1072" width="80" height="50" fill="{lid_c}"/></g>')
        s.append(f'</g><path id="cat_ring_{nm}" d="{ink_closed(ep, 4.4, seed=sd + 3)}" fill="{INK}"/></g>')
    # усы поверх (тонкие, светлые — читаются на тёмном)
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CX + sx * 58
            s.append(line([(x0, 1128 + dy * .8), (x0 + sx * 50, 1126 + dy + dl * .5), (x0 + sx * 96, 1124 + dy * 1.2 + dl)], 1.3, "#c4c1d6",
                          seed=270 + k + sx, op=.8))
    s.append("</g></g>")
    return "".join(s)


def cat_flame():
    k = FLAME_K
    bx, by = FLAME_BASE
    s = [f'<g id="cat_flame_rot" transform="{CAT_TF}"><g id="cat_flame">']
    s.append(shape(flame_pts(k), "#ff8a2a", blob(flame_pts(.7 * k), "#ffbe55"), w=3.4, seed=233, ink_color="#7a2a10", var=.2))
    s.append(blob([(bx - 8 * k, by + 2), (bx - 6 * k, by - 22 * k), (bx + 2 * k, by - 42 * k), (bx + 8 * k, by - 20 * k), (bx + 6 * k, by + 2)],
                  "#fff2c0"))
    s.append("</g></g>")
    return "".join(s)



# ═════════════════════════════ РУКИ, ТАРЕЛКА, ВИЛКА, ПУЛЬТ ═════════════════════════════
def sleeve(S, E, Wr, w=(62, 52, 44), seed=0, cuff=True):
    """Рукав худи: плечо → локоть → запястье, складки у локтя, манжета в рубчик."""
    s = []
    up = band([S, ((S[0] + E[0]) / 2, (S[1] + E[1]) / 2), E], w[0], w[1], step=5, cap=True)
    fa = band([Wr, ((E[0] + Wr[0]) / 2, (E[1] + Wr[1]) / 2), E], w[2], w[1], step=5, cap=True)   # округлый локоть
    ax = np.array(Wr, float) - np.array(E, float)
    L = np.linalg.norm(ax)
    ax /= L
    nx = np.array([-ax[1], ax[0]])
    inner = blob([tuple(np.array(E) + nx * 40), tuple(np.array(Wr) + nx * 40), tuple(np.array(Wr) + nx * 8), tuple(np.array(E) + nx * 10)],
                 HOOD_SH, .85)
    for i, u in enumerate((.12, .24, .7)):
        c = np.array(E) + ax * L * u
        inner += line([tuple(c + nx * 20), tuple(c + ax * 6), tuple(c - nx * 18)], 2.8, FOLD, seed=seed + i, op=.85, peak=.4)
    s.append(shape(up, HOOD, blob([tuple(np.array(S) + 20), tuple(np.array(E) + 30), tuple(np.array(E) + (0, 40))], HOOD_SH, .7) +
                   line([tuple(np.array(E) + (-14, -40)), tuple(np.array(E) + (0, -24)), tuple(np.array(E) + (14, -36))], 2.8, FOLD,
                        seed=seed + 5, op=.8), w=5.2, seed=seed + 7))
    s.append(shape(fa, HOOD, inner, w=5.2, seed=seed + 8))
    if cuff:
        c0 = np.array(Wr) - ax * 22
        cf = band([tuple(c0), tuple(np.array(Wr) + ax * 2)], w[2] + 6, w[2] + 4, step=3, cap=False)
        rib = "".join(line([tuple(c0 + ax * k * 4 + nx * (w[2] / 2 + 2)), tuple(c0 + ax * k * 4 - nx * (w[2] / 2 + 2))], 1.8, HOOD_SH2,
                           seed=seed + 20 + k, op=.8) for k in range(1, 6))
        s.append(shape(cf, HOOD_SH, rib, w=4.6, seed=seed + 9))
    return "".join(s)


def fist(cx, cy, ang, seed=0, scale=1.0):
    """Кулак, сжимающий предмет вдоль локальной оси x (предмет рисуется ДО кулака): тыл кисти, четыре согнутых пальца
    разной ширины с суставами и ногтями снизу, большой палец сверху с ногтем."""
    tf = f"translate({cx} {cy}) rotate({ang}) scale({scale})"
    s = [f'<g transform="{tf}">']
    palm = [(-26, -20), (-6, -30), (20, -28), (32, -12), (30, 8), (-24, 10)]
    s.append(shape(palm, SKIN, blob([(-30, 0), (34, 0), (34, 14), (-30, 14)], SKIN_SH, .8), w=4.4, seed=seed))
    fx = [(-17, 12.5, 26), (-4, 13.5, 28), (9, 13, 27), (21, 11, 22)]
    for i, (x, wd, ln) in enumerate(fx):
        f = rect_pts(x - wd / 2, -2, x + wd / 2, ln, wd * .45)
        nail = rect_pts(x - wd * .28, ln - 9, x + wd * .28, ln - 2, 3)
        s.append(shape(f, SKIN, blob([(x - wd, 8), (x + wd, 8), (x + wd, ln + 2), (x - wd, ln + 2)], SKIN_SH, .55) +
                       blob(nail, "#e6c1b4") + blob([(x - wd * .2, ln - 8), (x + wd * .1, ln - 8), (x + wd * .1, ln - 5), (x - wd * .2, ln - 5)],
                                                    "#f6e0d4", .9) +
                       line([(x - wd * .32, 9), (x, 11), (x + wd * .3, 9)], 1.6, SKIN_SH2, seed=seed + 10 + i, op=.85), w=3.8, seed=seed + 1 + i))
    th = band([(-24, -18), (-30, -30), (-20, -40), (-4, -40)], 18, 15, cap=True)
    s.append(shape(th, SKIN, blob([(-34, -34), (6, -34), (6, -26), (-34, -26)], SKIN_SH, .5), w=4, seed=seed + 6, id=None))
    s.append(shape(rect_pts(-12, -46, -2, -36, 3), "#e6c1b4", w=1.8, seed=seed + 7))
    s.append("</g>")
    return "".join(s)


def flat_hand(cx, cy, ang, seed=0):
    """Расслабленная кисть на пледе: тыл, четыре пальца с ногтями, большой палец сбоку."""
    tf = f"translate({cx} {cy}) rotate({ang})"
    s = [f'<g transform="{tf}">']
    for i, (y, ln, wd) in enumerate([(-15, 34, 11), (-4, 40, 12), (7, 38, 12), (17, 30, 10)]):
        f = band([(14, y), (14 + ln * .55, y + 1), (14 + ln, y + 2)], wd, wd * .85, cap=True)
        nail = rect_pts(14 + ln - 8, y - wd * .28, 14 + ln, y + wd * .28, 3)
        s.append(shape(f, SKIN, blob(nail, "#e6c1b4") + blob([(10, y + 2), (60, y + 3), (60, y + 8), (10, y + 8)], SKIN_SH, .5), w=3.6,
                       seed=seed + i))
    back = [(-30, -20), (-6, -26), (18, -24), (24, 0), (20, 24), (-6, 28), (-30, 20)]
    s.append(shape(back, SKIN, blob([(-34, 10), (26, 12), (26, 30), (-34, 30)], SKIN_SH, .7) +
                   line([(0, -14), (16, -14)], 1.5, SKIN_SH2, seed=seed + 8, op=.6) + line([(0, 6), (16, 8)], 1.5, SKIN_SH2, seed=seed + 9, op=.6),
                   w=4.4, seed=seed + 5))
    th = band([(-14, -22), (2, -34), (20, -38)], 15, 12, cap=True)
    s.append(shape(th, SKIN, blob(rect_pts(12, -42, 22, -34, 3), "#e6c1b4"), w=3.8, seed=seed + 7))
    s.append("</g>")
    return "".join(s)


def remote(cx, cy, ang, seed=0, press_id=None):
    """Чёрный пульт без надписей: корпус, крестовина, кнопки, красная кнопка питания; ось — локальная x (перед — влево)."""
    tf = f"translate({cx} {cy}) rotate({ang})"
    s = [f'<g transform="{tf}">']
    body = rect_pts(-78, -17, 78, 17, 15)
    s.append(shape(body, "#1e1e26", blob([(-78, 6), (78, 6), (78, 17), (-78, 17)], "#121218", .9) +
                   blob([(-70, -16), (70, -16), (70, -11), (-70, -11)], "#3a3a48", .9), w=4.2, seed=seed))
    s.append(f'<circle cx="-62" cy="-2" r="4.5" fill="#c43a32"/><circle cx="-63.2" cy="-3.2" r="1.5" fill="#f08a80"/>')
    s.append(f'<circle cx="-34" cy="-1" r="10" fill="#33333f"/><circle cx="-34" cy="-1" r="4" fill="#24242c"/>')
    for k, (bx, by) in enumerate([(-14, -6), (-14, 5), (0, -6), (0, 5), (14, -6), (14, 5)]):
        s.append(f'<rect x="{bx - 4}" y="{by - 3}" width="8" height="6" rx="2" fill="#3a3a48"/>')
    s.append("</g>")
    return "".join(s)


PLATE_C = (365, 1186)


def plate():
    cx, cy = PLATE_C
    s = []
    pc = clip_of(REG["plaid"])      # тень тарелки — только на пледе, без полупрозрачного ореола за его краем
    s.append(f'<g clip-path="url(#{pc})">' + blob(ellipse_pts(cx + 4, cy + 14, 124, 30, 16), "#0d160f", .55, blur(5)) + "</g>")
    outer = ellipse_pts(cx, cy, 120, 38, 20)
    s.append(shape(outer, "#ece6da", blob(ellipse_pts(cx, cy + 14, 120, 30, 16), "#c9c1b2", .9) +
                   blob(ellipse_pts(cx - 50, cy - 18, 40, 8, 10), "#fbf8f2", .9), w=4.8, seed=300))
    well = ellipse_pts(cx, cy - 2, 90, 26, 18)
    s.append(shape(well, "#f2ede4", blob(ellipse_pts(cx, cy - 12, 90, 16, 14), "#d8d0c2", .8), w=3, seed=301, ink_color="#6b6250"))
    # паста: соус, спагетти петлями, базилик, сыр
    for hot in (True, False):
        g = 'sauce_hot' if hot else 'sauce_cold'
        st = '' if hot else ' style="display:none"'
        sc = "#d24a2e" if hot else "#9a4a3a"
        sp, sp_d = ("#f0cf6c", "#a8742c") if hot else ("#cdb27a", "#866a3c")
        o = [f'<g id="{g}"{st}>']
        mound = [(cx - 66, cy - 2), (cx - 50, cy - 26), (cx - 10, cy - 38), (cx + 34, cy - 32), (cx + 64, cy - 10), (cx + 52, cy + 10),
                 (cx, cy + 16), (cx - 48, cy + 10)]
        o.append(shape(mound, sp, blob(ellipse_pts(cx, cy + 6, 62, 12, 12), sp_d, .5), w=3.6, seed=302))
        rs = np.random.RandomState(31)
        for k in range(16):
            a0 = rs.uniform(0, 2 * math.pi)
            px, py = cx + rs.uniform(-48, 48), cy + rs.uniform(-28, 8)
            pts = [(px + 20 * math.cos(a0 + j * .9) * (1 - j * .1), py + 8 * math.sin(a0 + j * .9)) for j in range(5)]
            o.append(line(pts, 3.4, sp_d, seed=310 + k, taper=.3, wmin=.4, op=.9))
            o.append(line(pts, 2.0, "#fff0b0" if hot else "#e0cc98", seed=330 + k, taper=.3, wmin=.4))
        sauce = [(cx - 30, cy - 24), (cx + 4, cy - 34), (cx + 30, cy - 22), (cx + 26, cy - 6), (cx - 6, cy), (cx - 34, cy - 10)]
        o.append(shape(sauce, sc, blob(ellipse_pts(cx - 4, cy - 12, 22, 6, 8), "#8e2a1c" if hot else "#6e3428", .6) +
                       (blob(ellipse_pts(cx - 10, cy - 24, 8, 3, 8), "#ffb49c") if hot else ""), w=3.4, seed=303))
        o.append(shape(T(ellipse_pts(0, 0, 14, 6, 10), cx + 18, cy - 30, rot=-25), "#4f8a3c" if hot else "#55704a",
                       line([(cx + 6, cy - 25), (cx + 30, cy - 35)], 1.4, "#2f5a26", seed=304), w=2.6, seed=305))
        for k in range(10):
            o.append(f'<rect x="{cx + rs.uniform(-40, 40):.1f}" y="{cy + rs.uniform(-30, 0):.1f}" width="3" height="3" fill="#f6f1e0"/>')
        o.append("</g>")
        s.append("".join(o))
    return "".join(s)


def fork(x0, y0, x1, y1, seed=0, twirl=False):
    """Вилка: ручка (x0,y0) → зубцы (x1,y1); при twirl — накрученная паста на зубцах."""
    ax = np.array([x1 - x0, y1 - y0], float)
    L = np.linalg.norm(ax)
    ax /= L
    nx = np.array([-ax[1], ax[0]])
    P = lambda u, v: tuple(np.array([x0, y0]) + ax * u + nx * v)  # noqa: E731
    handle = [P(0, -8), P(L * .62, -4.4), P(L * .72, -7), P(L * .72, 7), P(L * .62, 4.4), P(0, 8)]
    s = [shape(handle, "#c9ccd6", blob([P(0, 1), P(L * .7, 1), P(L * .7, 6), P(0, 6)], "#8f93a2", .9), w=3.4, seed=seed)]
    for k in (-6, -2, 2, 6):
        s.append(line([P(L * .72, k * .9), P(L * .86, k), P(L, k * 1.05)], 3.2, "#b9bcc8", seed=seed + int(k * 3) + 10, taper=.2, wmin=.6))
        s.append(line([P(L * .72, k * .9), P(L, k * 1.05)], .9, INK, seed=seed + int(k * 3) + 20, taper=.2, wmin=.6, op=.8))
    if twirl:
        c = P(L * .9, 0)
        tw = ellipse_pts(c[0], c[1], 22, 15, 12, rot=math.degrees(math.atan2(ax[1], ax[0])))
        s.append(shape(tw, "#f0cf6c", "".join(line([P(L * .8, v), P(L * .92, v + 3), P(L, v)], 2, "#a8742c", seed=seed + 40 + i, op=.85)
                                              for i, v in enumerate((-10, -3, 4, 11))) +
                       blob(ellipse_pts(c[0] + 4, c[1] - 4, 8, 5, 8), "#d24a2e"), w=3.4, seed=seed + 30))
    return "".join(s)


L_S, L_E, L_W = (190, 1070), (150, 1192), (230, 1098)      # левая рука с пультом (поза A)
R_S, R_E = (452, 1078), (528, 1190)


def front_dima():
    """Всё Димино, что лежит поверх пледа: тарелка, руки, вилка, пульт — три позы (A пульт, B отложил, C ест)."""
    s = [plate()]
    # --- поза A: левая рука держит пульт на телевизор, правая — вилку в тарелке
    s.append('<g id="pose_A">')
    s.append(sleeve(L_S, L_E, L_W, seed=400))
    s.append('<g id="remote_A">' + remote(178, 1072, 18, seed=410) + "</g>")
    s.append('<g id="fist_L">' + fist(246, 1086, 18, seed=420) + "</g>")
    s.append(fork(500, 1096, 388, 1180, seed=430))
    s.append(sleeve(R_S, R_E, (480, 1146), seed=440))
    s.append(fist(466, 1130, -37, seed=450))
    s.append("</g>")
    # --- поза B: пульт отложен на плед, левая кисть лежит, правая с вилкой в тарелке
    s.append('<g id="pose_B" style="display:none">')
    s.append(remote(96, 1222, 4, seed=460))
    s.append(sleeve(L_S, (138, 1196), (206, 1208), seed=470))
    s.append(flat_hand(236, 1210, 4, seed=480))
    s.append(fork(500, 1096, 388, 1180, seed=430))
    s.append(sleeve(R_S, R_E, (480, 1146), seed=440))
    s.append(fist(466, 1130, -37, seed=450))
    s.append("</g>")
    # --- поза C: ест — вилка с накрученной пастой у рта
    s.append('<g id="pose_C" style="display:none">')
    s.append(remote(96, 1222, 4, seed=460))
    s.append(sleeve(L_S, (138, 1196), (206, 1208), seed=470))
    s.append(flat_hand(236, 1210, 4, seed=480))
    s.append(sleeve(R_S, (520, 1184), (404, 1092), seed=490))
    s.append('<g id="fork_C">' + fork(404, 1080, 268, 1002, seed=500, twirl=True) + fist(384, 1068, 30, seed=510) + "</g>")
    s.append("</g>")
    return "".join(s)


# ═════════════════════════════ ПЛЕД (вектором, без растровых узоров) ═════════════════════════════
PLAID_TOP = [(36, 1250), (70, 1196), (140, 1170), (250, 1166), (360, 1172), (440, 1196), (500, 1230), (560, 1236), (620, 1196),
             (690, 1140), (740, 1128), (800, 1150), (880, 1190), (960, 1196), (1000, 1168), (1040, 1160), (1092, 1180, 1)]
EDGE_Y = 1252
PERIOD = 124


def tartan(x0, x1, y0, y1, top=False):
    """Шотландка полосами-многоугольниками: широкая тёмная, тонкая светлая, тонкая тёмная, красная нитка.
    Сверху (на ногах) — в перспективе: вертикали сходятся вверх, горизонтали сжаты."""
    s = []
    bands = [(0, 44, "#4e7e46", .9), (18, 22, "#2a4630", 1), (68, 74, "#dfe8b0", .85), (94, 97, "#a33f35", .85)]

    def vx(x, y):
        if not top:
            return x
        k = 1 - .12 * (EDGE_Y - y) / 160
        return 540 + (x - 540) * k
    for base in range(-PERIOD * 2, W + PERIOD * 2, PERIOD):
        for a, b, col, op in bands:
            xa, xb = base + a, base + b
            s.append(f'<path d="M{vx(xa, y0):.1f} {y0} L{vx(xb, y0):.1f} {y0} L{vx(xb, y1):.1f} {y1} L{vx(xa, y1):.1f} {y1}Z" '
                     f'fill="{col}" opacity="{op}"/>')
    if top:
        ys = [EDGE_Y - k * 34 for k in range(0, 8)]
        for yy in ys:
            for a, b, col, op in [(0, 14, "#4e7e46", .75), (6, 8, "#2a4630", .9), (22, 24, "#dfe8b0", .7)]:
                s.append(f'<rect x="0" y="{yy - b}" width="{W}" height="{b - a}" fill="{col}" opacity="{op}"/>')
    else:
        for base in range(int(y0) - PERIOD, int(y1) + PERIOD, PERIOD):
            for a, b, col, op in bands:
                s.append(f'<rect x="0" y="{base + a}" width="{W}" height="{b - a}" fill="{col}" opacity="{op}"/>')
    return "".join(s)


def plaid():
    s = []
    folds = [70, 190, 330, 470, 610, 760, 900, 1040]
    bottom = []
    for i in range(len(folds) - 1):
        xa, xb = folds[i], folds[i + 1]
        bottom += [(xa, 1478 - (i % 2) * 6), ((xa + xb) / 2, 1448 + (i % 3) * 4)]
    bottom = [(1092, 1462)] + bottom[::-1] + [(30, 1452)]
    outline = PLAID_TOP + [(1092, 1300), (1094, 1462, 1)] + bottom[1:-1] + [(30, 1452, 1), (22, 1360), (30, 1290)]
    inner = [f'<rect x="0" y="1080" width="{W}" height="460" fill="#7aa66a"/>', tartan(0, W, 1080, EDGE_Y, top=True),
             tartan(0, W, EDGE_Y, 1500)]
    inner.append(blob([(740, 1128), (800, 1150), (880, 1190), (880, EDGE_Y), (760, EDGE_Y), (790, 1190)], "#203a24", .35))
    inner.append(blob([(960, 1196), (1000, 1168), (1010, EDGE_Y), (950, EDGE_Y)], "#203a24", .3))
    inner.append(blob([(620, 1196), (690, 1140), (740, 1128), (700, 1170), (640, 1210)], "#eef6c8", .18))
    for i, st in enumerate([[(200, 1176), (236, 1210), (240, EDGE_Y - 6)], [(560, 1236), (600, 1244)], [(650, 1176), (680, 1214)],
                            [(820, 1172), (850, 1210)], [(1010, 1176), (1030, 1220)], [(110, 1190), (130, 1230)]]):
        inner.append(line(st, 3.2, seed=230 + i, op=.8))
    inner.append(blob([(0, EDGE_Y - 14), (W, EDGE_Y - 16), (W, EDGE_Y + 4), (0, EDGE_Y + 6)], "#eef6c8", .16))
    inner.append(blob([(0, EDGE_Y + 8), (W, EDGE_Y + 6), (W, EDGE_Y + 44), (0, EDGE_Y + 46)], "#0f1d12", .35))
    for i in range(len(folds) - 1):
        xa, xb = folds[i], folds[i + 1]
        xm = (xa + xb) / 2
        inner.append(blob([(xm - 10, EDGE_Y + 30), (xm + 6, EDGE_Y + 30), (xm + 26, 1400), (xm + 30, 1490), (xm - 34, 1490), (xm - 26, 1400)],
                          "#132416", .45, blur(9)))
        inner.append(blob([(xa - 6, EDGE_Y + 40), (xa + 6, EDGE_Y + 40), (xa + 20, 1490), (xa - 18, 1490)], "#eef6c8", .12, blur(7)))
        inner.append(line([(xm - 2, EDGE_Y + 40), (xm + 4, 1380), (xm + 10, 1460)], 3, seed=240 + i, op=.7, peak=.7))
    inner.append(blob([(0, 1390), (W, 1390), (W, 1490), (0, 1490)], "#0f1d12", .3))
    inner.append(blob(ellipse_pts(822, 1250, 120, 20, 12), "#0d160f", .7, blur(7)))
    s.append(shape(outline, "#7aa66a", "".join(inner), w=5.4, seed=245, id="plaid"))
    S_ = sample(bottom, False, step=10)
    rs = np.random.RandomState(9)
    for i, (x, y) in enumerate(S_):
        ln = rs.uniform(14, 22)
        s.append(line([(x, y - 2), (x + rs.uniform(-3, 3), y + ln * .5), (x + rs.uniform(-4, 4), y + ln)], 3.6, "#4f7c48",
                      seed=300 + i, taper=.6, wmin=.3, peak=.3))
    return "".join(s)


# ═════════════════════════════ ЭФФЕКТЫ: карточки, пар ═════════════════════════════
NCARDS = 26


def card_defs():
    rs = np.random.RandomState(23)
    pal = [("#3a6fd8", "#9fd0ff"), ("#d84a5a", "#ffb08a"), ("#2f9a6a", "#b8f0a0"), ("#7a4ad8", "#e0a8ff"), ("#e0a030", "#fff0a0"),
           ("#1f2a5a", "#5a8ae0"), ("#c0306a", "#ffa0c8"), ("#2a8aa8", "#a8f0f0")]
    out = []
    for i in range(NCARDS):
        a, b = pal[i % len(pal)]
        gid = f"gc{i}"
        out.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{b}"/>'
                   f'<stop offset="1" stop-color="{a}"/></linearGradient>')
        frame_ = rect_pts(-62, -36, 62, 36, 9)
        img = [f'<rect x="-62" y="-36" width="124" height="72" fill="url(#{gid})"/>']
        kind = i % 4
        if kind == 0:     # горы и солнце
            img.append(blob([(-62, 36), (-30, -6), (-8, 16), (18, -14), (62, 36)], a))
            img.append(f'<circle cx="34" cy="-16" r="9" fill="#fff4c0"/>')
        elif kind == 1:   # силуэт героя
            img.append(f'<circle cx="0" cy="-8" r="13" fill="{a}"/>')
            img.append(blob([(-26, 36), (-20, 10), (0, 4), (20, 10), (26, 36)], a))
        elif kind == 2:   # машина/предмет — круги
            img.append(f'<circle cx="-20" cy="6" r="16" fill="{a}"/><circle cx="18" cy="-4" r="22" fill="#ffffff" opacity=".8"/>')
        else:             # полосы-горизонт
            img.append(f'<rect x="-62" y="10" width="124" height="26" fill="{a}"/><rect x="-62" y="2" width="124" height="5" fill="#fff4c0"/>')
        img.append(f'<path d="M-54 -26 L-54 -8" stroke="#ffffff" stroke-width="3" opacity=".55"/>')
        c = clip_of(frame_)
        out.append(f'<g id="card{i}"><path d="{fill_d(frame_)}" fill="#14141c"/><g clip-path="url(#{c})">{"".join(img)}</g>'
                   f'<path d="{ink_closed(frame_, 4.2, seed=600 + i)}" fill="#0c0c12"/></g>')
    DEFS.append("".join(out))


def cards_group(gid):
    return f'<g id="{gid}">' + "".join(f'<use href="#card{i}" id="{gid}_{i}" style="display:none"/>' for i in range(NCARDS)) + "</g>"


STEAM = [[(338, 1158), (326, 1120), (344, 1086), (330, 1046), (346, 1006)], [(366, 1150), (378, 1110), (362, 1070), (380, 1030), (366, 990)],
         [(396, 1158), (408, 1124), (394, 1090), (410, 1052), (398, 1016)]]


def steam_group():
    s = ['<g id="steam">']
    for i, pts in enumerate(STEAM):
        d = fill_d(pts, closed=False)
        s.append(f'<path id="steam_o{i}" d="{d}" fill="none" stroke="#3a3f62" stroke-width="12" stroke-linecap="round" '
                 f'stroke-dasharray="34 62"/>')
        s.append(f'<path id="steam_i{i}" d="{d}" fill="none" stroke="#b4bedc" stroke-width="7.5" stroke-linecap="round" '
                 f'stroke-dasharray="34 62"/>')
    s.append("</g>")
    return "".join(s)


# ═════════════════════════════ СВЕТ ═════════════════════════════
def light_defs():
    tx, ty = TV_PX
    fx, fy = FLAME_C
    DEFS.append(f"""
<radialGradient id="gTV" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({tx} {ty}) scale(1000 900)">
 <stop offset="0" stop-color="#bcd2ff" stop-opacity=".95"/><stop offset=".45" stop-color="#86a8ec" stop-opacity=".5"/>
 <stop offset=".8" stop-color="#4a6fc0" stop-opacity=".12"/><stop offset="1" stop-color="#4a6fc0" stop-opacity="0"/></radialGradient>
<radialGradient id="gFl" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({fx} {fy + 40}) scale(330 330)">
 <stop offset="0" stop-color="#ffb060" stop-opacity=".9"/><stop offset=".3" stop-color="#ff8a3a" stop-opacity=".45"/>
 <stop offset=".7" stop-color="#c05a22" stop-opacity=".12"/><stop offset="1" stop-color="#c05a22" stop-opacity="0"/></radialGradient>
<radialGradient id="gRimF" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({fx} {fy + 60}) scale(220 260)">
 <stop offset="0" stop-color="#ffc878"/><stop offset=".5" stop-color="#ff8a3a"/><stop offset="1" stop-color="#c05020" stop-opacity="0"/></radialGradient>
<radialGradient id="gFaceL" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(150 -10) scale(230 210)">
 <stop offset="0" stop-color="#8ab0f4" stop-opacity=".85"/><stop offset=".55" stop-color="#5a80d0" stop-opacity=".38"/>
 <stop offset="1" stop-color="#3a5cb0" stop-opacity="0"/></radialGradient>
<filter id="fNight" x="-500" y="-500" width="{W + 1000}" height="{H + 1000}" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
 <feColorMatrix type="matrix" values="{NIGHT[0] * .9} {NIGHT[0] * .1} 0 0 0  {NIGHT[1] * .05} {NIGHT[1] * .9} {NIGHT[1] * .05} 0 0  0 {NIGHT[2] * .1} {NIGHT[2] * .9} 0 0  0 0 0 1 0"/>
</filter>
<filter id="fBlack" x="-50%" y="-50%" width="200%" height="200%" color-interpolation-filters="sRGB">
 <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"/></filter>
<filter id="fWhite" x="-500" y="-500" width="{W + 1000}" height="{H + 1000}" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
 <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>
""")


def mask_of(art_id):
    m = f"M_{art_id}"
    DEFS.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="-500" y="-500" width="{W + 1000}" height="{H + 1000}">'
                f'<use href="#{art_id}" filter="url(#fWhite)"/></mask>')
    return m


def lights_dima():
    tf = head_tf()
    hair = REG["dima_hair"]
    fc = clip_of(FACE)
    return (f'<g id="tv_dima"><rect x="-500" y="-500" width="{W + 1000}" height="{H + 1000}" fill="url(#gTV)"/>'
            f'<g id="face_light_pose"><g transform="{tf}"><g clip-path="url(#{fc})">'
            f'<rect x="-140" y="-140" width="280" height="280" fill="url(#gFaceL)"/><path d="{fill_d(hair)}" fill="#000"/></g></g></g></g>')


def lights_plaid():
    return (f'<g id="tv_plaid"><rect x="-500" y="-500" width="{W + 1000}" height="{H + 1000}" fill="url(#gTV)" opacity=".8"/></g>'
            f'<g id="fl_plaid"><rect width="{W}" height="{H}" fill="url(#gFl)" opacity=".85"/></g>')


def lights_cat():
    s = [f'<g id="fl_cat"><rect width="{W}" height="{H}" fill="url(#gFl)" opacity=".55"/>']
    s.append(f'<g transform="{CAT_TF}"><g id="cat_head_rim">')
    s.append(rim(REG["cat_head"], "gRimF", -12, 5, .85, soft=6))
    s.append(rim(REG["cat_ear_R"], "gRimF", -8, 4, .8, soft=4))
    s.append("</g>")
    s.append(rim(REG["cat_body"], "gRimF", -12, 2, .7, soft=6))
    s.append(f'<g id="tail_rim">{rim(REG["cat_tail_shape"], "gRimF", -6, 8, .85, soft=5)}</g>')
    s.append("</g></g>")
    s.append(f'<g id="tv_cat"><g transform="{CAT_TF}"><g id="cat_head_rim2">')
    s.append(rim(REG["cat_head"], "#8aa8f0", 11, 4, .6, soft=6))
    s.append(rim(REG["cat_ear_L"], "#8aa8f0", 7, 6, .6, soft=4))
    s.append("</g>")
    s.append(rim(REG["cat_body"], "#8aa8f0", 10, 0, .45, soft=6))
    s.append("</g></g>")
    return "".join(s)


def build():
    light_defs()
    card_defs()
    a_dima = cards_group("cards_back") + '<g id="dima_all">' + dima_back() + f'<g id="dima_head_pose">{dima_head()}</g></g>'
    a_plaid = plaid() + front_dima()
    a_cat = cat_art()
    layers = []
    for name, art, lit, top in [("dima", a_dima, lights_dima(), ""), ("plaid", a_plaid, lights_plaid(), ""),
                                ("cat", a_cat, lights_cat(), cat_eyes() + cat_flame()), ("fx", "", "", cards_group("cards_front") + steam_group())]:
        if art:
            m = mask_of(f"A_{name}")
            body = (f'<g id="A_{name}" filter="url(#fNight)">{art}</g>'
                    f'<g style="mix-blend-mode:screen" mask="url(#{m})">{lit}</g>')
        else:
            body = ""
        layers.append(f'<g id="L_{name}" style="isolation:isolate">{body}{top}</g>')
    return (f'<svg id="scene" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{"".join(DEFS)}</defs>{"".join(layers)}</svg>')


if __name__ == "__main__":
    here = __file__.rsplit("/", 1)[0]
    svg = build()
    html = open(f"{here}/template23.html").read().replace("<!--SVG-->", svg)
    open(f"{here}/heroes23.html", "w").write(html)
    print("heroes23.html", len(html) // 1024, "KB")
