from ink import band, ellipse_pts, fill_d, fur, ink_closed, ink_open, sample  # noqa: E402

W, H = 1080, 1920
INK = "#1c1622"
DEFS = []
REG = {}
_uid = [0]


def uid(p="c"):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def shape(pts, fill, inner="", w=5.0, seed=0, ink=True, id=None, attrs="", var=0.28, weight=0.45, ink_color=INK):
    """Заливка + внутреннее (тени, узор) по маске силуэта + тушь переменной толщины."""
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


def rim(pts, color, dx, dy, op=1.0, tf=None, id=None, cut=()):
    """Рим-свет: полумесяц по краю силуэта = фигура минус та же фигура со сдвигом (резкая cel-граница).
    Кладётся в группу со screen: чёрный «резец» ничего не осветляет."""
    d = fill_d(pts)
    c = clip_of(pts)
    gid = f' id="{id}"' if id else ""
    fill = f"url(#{color})" if color.startswith("g") else color
    g = (f'<g{gid} clip-path="url(#{c})" opacity="{op}"><path d="{d}" fill="{fill}"/>'
         f'<path d="{d}" transform="translate({dx} {dy})" fill="#000"/>'
         + "".join(f'<path d="{fill_d(c_)}" fill="#000"/>' for c_ in cut) + '</g>')
    return f'<g transform="{tf}">{g}</g>' if tf else g


def clip_of(pts):
    c = uid()
    DEFS.append(f'<clipPath id="{c}"><path d="{fill_d(pts)}"/></clipPath>')
    return c


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


# ───────────────────────────── Дима ─────────────────────────────
HX, HY, HR = 446, 878, -7  # центр головы и наклон


def head_tf():
    return f"translate({HX} {HY}) rotate({HR})"


def H2G(x, y):
    c, s_ = math.cos(math.radians(HR)), math.sin(math.radians(HR))
    return HX + x * c - y * s_, HY + x * s_ + y * c


SKIN, SKIN_SH, SKIN_SH2 = "#ecc4a2", "#d39f83", "#bf8a74"
HAIR, HAIR_SH = "#5a3826", "#3d2418"
HOOD, HOOD_SH, HOOD_SH2 = "#d4a23e", "#a97b25", "#8c6219"

FACE = [(-30, -120), (40, -116), (88, -84), (110, -32), (116, 18), (108, 62), (84, 98), (46, 120), (6, 126), (-34, 112),
        (-68, 82), (-94, 38), (-106, -16), (-96, -72), (-66, -108)]
EYE_N = (18, -10, 50, 50)    # cx, cy, rx, ry — ближний глаз
EYE_F = (94, -8, 40, 47)     # дальний (ракурс 3/4)


def hood_body():
    s = []
    # капюшон, лежащий под головой на подушке
    hood = [(292, 1046), (296, 980), (330, 944), (390, 936), (440, 968), (520, 990), (560, 1010), (520, 1048), (400, 1060)]
    inner = blob([(296, 980), (330, 944), (390, 936), (420, 960), (360, 1000), (300, 1030)], HOOD_SH2, .9)
    inner += line([(316, 980), (350, 958), (392, 952)], 2.6, "#6b4a12", seed=140, op=.8)
    s.append(shape(hood, HOOD, inner, w=5, seed=141))
    # туловище в худи (дальше его закрывает плед)
    body = [(286, 1100), (300, 1040), (360, 1010), (430, 1018), (480, 1030), (540, 1016), (600, 1036), (642, 1080),
            (662, 1150, 1), (300, 1170, 1)]
    inner = blob([(286, 1060), (360, 1040), (420, 1100), (380, 1170), (286, 1170)], HOOD_SH, .9)
    inner += blob([(560, 1030), (640, 1070), (662, 1150), (600, 1150), (590, 1080)], HOOD_SH, .8)
    # складки
    inner += line([(350, 1060), (390, 1080), (410, 1120)], 3, "#6b4a12", seed=142, op=.85)
    inner += line([(520, 1060), (500, 1090), (508, 1130)], 3, "#6b4a12", seed=143, op=.85)
    inner += line([(440, 1100), (470, 1120)], 2.4, "#6b4a12", seed=144, op=.7)
    s.append(shape(body, HOOD, inner, w=5.2, seed=145, id="dima_body"))
    # шея и вырез
    nk = [(420, 960), (474, 958), (486, 1030), (452, 1046), (418, 1030)]
    s.append(shape(nk, SKIN, blob([(420, 960), (474, 958), (480, 1000), (420, 1006)], SKIN_SH, .95) +
                   blob([(420, 960), (440, 960), (440, 1040), (418, 1040)], SKIN_SH2, .6), w=4.6, seed=146, id="dima_neck"))
    collar = [(404, 1026), (432, 1044), (470, 1048), (500, 1030), (510, 1046), (474, 1066), (432, 1064), (396, 1044)]
    s.append(shape(collar, HOOD_SH, "", w=4.4, seed=147))
    # шнурки капюшона
    for (x0, y0, x1, y1, sd) in [(446, 1058, 438, 1124, 148), (480, 1056, 496, 1118, 149)]:
        s.append(line([(x0, y0), ((x0 + x1) / 2 + 3, (y0 + y1) / 2), (x1, y1)], 5.5, "#efe3c4", taper=.2, wmin=.8, seed=sd))
        s.append(line([(x0, y0), ((x0 + x1) / 2 + 3, (y0 + y1) / 2), (x1, y1)], 1.8, INK, taper=.2, wmin=.8, seed=sd + 1, op=.6))
        s.append(shape(rect_pts(x1 - 5, y1, x1 + 5, y1 + 16, 2), "#b9b9c4", w=2.6, seed=sd + 2))
    return "".join(s)


def head():
    s = [f'<g id="dima_head" transform="{head_tf()}">']
    # волосы сзади (за ухом и затылком, на подушке)
    back_hair = [(-60, -110), (-110, -86), (-150, -40, 1), (-122, -30), (-140, 10, 1), (-108, 6), (-104, 40, 1), (-80, 20), (-70, -40)]
    s.append(shape(back_hair, HAIR_SH, "", w=4.6, seed=150))
    # ухо
    ear = [(-86, -16), (-110, -26), (-128, -4), (-124, 30), (-104, 52), (-84, 46)]
    s.append(shape(ear, SKIN, blob([(-128, -4), (-124, 30), (-104, 52), (-110, 20)], SKIN_SH, .9), w=4.6, seed=151))
    s.append(line([(-96, 30), (-114, 18), (-112, -2), (-98, -10)], 3, seed=152))
    # лицо
    inner = []
    # тень: затылочная сторона и под подбородком (свет экрана справа)
    inner.append(blob([(-110, -130), (-40, -130), (-62, -40), (-58, 40), (-24, 130), (-110, 130)], SKIN_SH, .95))
    inner.append(blob([(-20, 100), (50, 112), (100, 80), (110, 140), (-30, 140)], SKIN_SH, .85))
    # щетина: синеватый налёт по челюсти
    inner.append(blob([(-60, 70), (-20, 92), (30, 104), (80, 92), (104, 70), (110, 130), (-60, 130)], "#9e8a96", .45))
    rs = np.random.RandomState(7)
    for _ in range(90):
        x, y = rs.uniform(-50, 104), rs.uniform(76, 124)
        if (x - 30) ** 2 / 90 ** 2 + (y - 60) ** 2 / 66 ** 2 > 1.0 or y > 118 - abs(x - 30) * .15:
            continue
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rs.uniform(1, 1.8):.1f}" fill="#5c4446" opacity=".55"/>')
    # румянец/красные от усталости веки вокруг глаз
    inner.append(blob(ellipse_pts(54, -10, 100, 62, 14), "#d9a08f", .35))
    s.append(shape(FACE, SKIN, "".join(inner), w=5.4, seed=153, id="dima_face"))
    # мешки под глазами — два полумесяца и вторая складка
    for (cx, cy, rx, ry, sd) in [(EYE_N[0], EYE_N[1], EYE_N[2], EYE_N[3], 154), (EYE_F[0], EYE_F[1], EYE_F[2], EYE_F[3], 155)]:
        bag = [(cx - rx * .85, cy + ry * .55), (cx, cy + ry * 1.38), (cx + rx * .85, cy + ry * .55), (cx, cy + ry * .9)]
        s.append(blob(bag, "#a77f8c", .75))
        s.append(line([(cx - rx * .8, cy + ry * .7), (cx, cy + ry * 1.36), (cx + rx * .75, cy + ry * .75)], 3.2, seed=sd))
        s.append(line([(cx - rx * .5, cy + ry * 1.25), (cx + rx * .05, cy + ry * 1.6), (cx + rx * .5, cy + ry * 1.3)], 2.2, seed=sd + 5, op=.75))
    # глаза: белки, зрачки, веки (веко — группа под маской глаза, двигается при моргании)
    for nm, (cx, cy, rx, ry), sd in [("F", EYE_F, 160), ("N", EYE_N, 161)]:
        ep = ellipse_pts(cx, cy, rx, ry, 14)
        cid = clip_of(ep)
        s.append(f'<g id="dima_eye_{nm}">')
        s.append(f'<path d="{fill_d(ep)}" fill="#f6f2ea"/>')
        s.append(f'<g clip-path="url(#{cid})">')
        # тень от века на белке
        s.append(blob([(cx - rx, cy - ry), (cx + rx, cy - ry), (cx + rx, cy + 6), (cx - rx, cy + 2)], "#c9c2d6", .9))
        # зрачок смотрит вправо — на экран
        s.append(f'<g class="dima_pupil" id="dima_pupil_{nm}"><ellipse cx="{cx + rx * .42:.1f}" cy="{cy + 14:.1f}" rx="6.8" ry="7.4" fill="{INK}"/></g>')
        # веко: кожа сверху + край века (утолщённый штрих) + ресничная тень
        lid_y = cy - ry * .02
        lid = [(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 6), (cx + rx * .4, lid_y + 4),
               (cx - rx * .3, lid_y + 1), (cx - rx - 10, lid_y - 10)]
        s.append(f'<g id="dima_lid_{nm}">')
        s.append(blob(lid, SKIN))
        s.append(blob([(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 20), (cx - rx - 10, lid_y - 22)],
                      "#d9a08f", .5))
        s.append(line([(cx - rx - 6, lid_y - 9), (cx - rx * .3, lid_y + 1.5), (cx + rx * .4, lid_y + 4), (cx + rx + 6, lid_y - 5)],
                      6.2, seed=sd, taper=.4, wmin=.35))
        s.append("</g></g>")
        s.append(f'<path d="{ink_closed(ep, 4.6, seed=sd + 2)}" fill="{INK}"/>')
        s.append("</g>")
    # брови — уставшие, чуть вверх у переносицы
    s.append(line([(-26, -74), (6, -82), (44, -78)], 7.5, HAIR_SH, seed=162, peak=.4))
    s.append(line([(74, -78), (102, -84), (128, -74)], 6.5, HAIR_SH, seed=163, peak=.55))
    # нос (3/4): крючок
    s.append(line([(66, 18), (82, 44), (76, 56), (62, 54)], 4.2, seed=164, peak=.45))
    s.append(blob(ellipse_pts(72, 56, 6, 2.5, 8), SKIN_SH, .8))
    # рот: усталая полуулыбка-гримаса
    s.append(f'<g id="dima_mouth">')
    s.append(line([(36, 86), (60, 84), (82, 87), (90, 92)], 4.6, seed=165, peak=.45))
    s.append(line([(54, 98), (70, 98)], 2.6, seed=166, op=.7))
    s.append("</g>")
    # волосы: лохматые, торчат назад и вверх
    hair = [(108, -40), (104, -78), (82, -110), (92, -150, 1), (52, -128), (36, -170, 1), (8, -138), (-18, -178, 1), (-40, -136),
            (-86, -162, 1), (-90, -128), (-142, -128, 1), (-112, -96), (-156, -78, 1), (-118, -64), (-140, -34, 1), (-104, -38),
            (-94, -14, 1), (-80, -42), (-62, -70), (-22, -88), (12, -92), (30, -76, 1), (50, -98), (80, -86, 1), (98, -62), (108, -40, 1)]
    inner = blob([(-160, -190), (-20, -190), (-30, -130), (-70, -100), (-80, -40), (-160, -20)], HAIR_SH, .95)
    inner += blob([(10, -150), (60, -120), (100, -80), (70, -112), (40, -128)], "#7a5038", .9)
    for i, st in enumerate([[(-10, -150), (-30, -120), (-60, -100)], [(30, -140), (10, -110), (-20, -96)],
                            [(70, -120), (60, -100), (40, -94)], [(-70, -130), (-96, -110), (-112, -84)],
                            [(-40, -100), (-70, -80), (-84, -56)]]):
        inner += line(st, 3.2, "#2a170f", seed=170 + i, op=.85)
    s.append(shape(hair, HAIR, inner, w=5.2, seed=171, id="dima_hair"))
    s.append("</g>")
    return "".join(s)


# телефон и рука: локальные координаты телефона
PX, PY, PR = 668, 818, -11


# ───────────────────────────── кот ─────────────────────────────
CAT, CAT_SH, CAT_FUR = "#2f2b37", "#1b1821", "#4b4559"
CX, CY = 836, 1080


TAIL_C = [(900, 1272), (970, 1266), (1018, 1236), (1042, 1190), (1040, 1140), (1018, 1104), (984, 1090), (956, 1102), (950, 1128),
          (964, 1142), (982, 1134), (982, 1116)]
FLAME_BASE = (990, 1088)


def flame_pts(k=1.0):
    bx, by = FLAME_BASE
    P = [(-22, 4), (-26, -18), (-16, -40), (-14, -62), (-4, -50), (2, -86, 1), (12, -58), (22, -70, 1), (26, -40), (24, -12), (16, 4), (0, 10)]
    return [(bx + x * k, by + y * k) + ((1,) if len(q) > 2 else ()) for q in P for x, y in [q[:2]]]


def cat():
    s = ['<g id="cat">']
    # хвост: за телом справа, закручен завитком, огонёк на верхней дуге (группа — для покачивания)
    s.append('<g id="cat_tail">')
    tp = band(TAIL_C, 46, 13, step=7)
    tp = fur(tp, 5, 7, seed=21)
    s.append(shape(tp, CAT, blob([(1006, 1110), (1046, 1150), (1036, 1270), (980, 1276)], CAT_SH, .85) +
                   line([(986, 1240), (1004, 1206), (1010, 1170)], 2.4, CAT_FUR, seed=231, op=.9) +
                   line([(966, 1126), (970, 1114), (982, 1110)], 2.4, INK, seed=232, op=.9), w=4.8, seed=230, id="cat_tail_shape"))
    s.append('<g id="cat_flame">')
    s.append(shape(flame_pts(1.0), "#ff8a2a", blob(flame_pts(.68), "#ffbe55"), w=3.4, seed=233, ink_color="#7a2a10", var=.2))
    s.append(blob([(FLAME_BASE[0] - 8, FLAME_BASE[1] + 2), (FLAME_BASE[0] - 6, FLAME_BASE[1] - 22), (FLAME_BASE[0] + 2, FLAME_BASE[1] - 40),
                   (FLAME_BASE[0] + 8, FLAME_BASE[1] - 20), (FLAME_BASE[0] + 6, FLAME_BASE[1] + 2)], "#fff2c0"))
    s.append("</g></g>")
    # тело — грушей, мягкий пушистый край
    body = [(760, 1296), (744, 1240), (756, 1180), (790, 1142), (880, 1142), (916, 1180), (928, 1240), (912, 1296)]
    bp = fur(body, 7, 7, seed=22)
    inner = blob([(860, 1140), (930, 1180), (930, 1300), (874, 1300), (888, 1220)], CAT_SH, .9)
    inner += blob([(800, 1172), (836, 1162), (872, 1172), (862, 1240), (836, 1262), (810, 1240)], CAT_FUR, .5)
    for i, st in enumerate([[(816, 1190), (826, 1208)], [(852, 1192), (846, 1212)], [(834, 1214), (836, 1236)], [(806, 1222), (814, 1238)]]):
        inner += line(st, 2.2, "#6a6380", seed=240 + i, op=.8)
    s.append(shape(bp, CAT, inner, w=5, seed=241, id="cat_body"))
    # задние лапы с оранжевыми подушечками (как у эталона)
    for sx, sd in [(-1, 242), (1, 243)]:
        px = CX + sx * 70
        foot = ellipse_pts(px, 1286, 34, 26, 12, rot=sx * 12)
        s.append(shape(foot, CAT, blob(T(ellipse_pts(px, 1292, 26, 20, 10), sx * 4, 0), CAT_SH, .5), w=4.6, seed=sd))
        s.append(blob(ellipse_pts(px + sx * 3, 1296, 13, 10, 10, rot=sx * 10), "#e8823a"))
        for k in range(3):
            ang = math.radians(-90 + (k - 1) * 42 + sx * 10)
            s.append(blob(ellipse_pts(px + sx * 3 + math.cos(ang) * 19, 1296 + math.sin(ang) * 15, 5, 4.4, 8), "#e8823a"))
    # передние лапки
    for sx, sd in [(-1, 244), (1, 245)]:
        fx = CX + sx * 25
        paw = [(fx - 20, 1306, 1), (fx - 19, 1252), (fx + 19, 1252), (fx + 20, 1306, 1)]
        s.append(shape(paw, CAT, blob([(fx + sx * 6, 1250), (fx + 20 * sx, 1250), (fx + 20 * sx, 1306), (fx + sx * 8, 1306)], CAT_SH, .7),
                       w=4.6, seed=sd))
        for k in (-7, 7):
            s.append(line([(fx + k, 1294), (fx + k, 1306)], 2.2, seed=sd + k))
    # уши за головой: правое (от зрителя) стоит, левое загнуто вниз
    re_ = [(864, 1010), (902, 924, 1), (930, 1034)]
    s.append(shape(re_, CAT, blob([(878, 1010), (902, 948), (918, 1024)], "#9b6150") +
                   line([(888, 1000), (900, 968)], 2, "#d79a84", seed=252, op=.8), w=4.8, seed=251, id="cat_ear_R"))
    # левое ухо: обычное ухо с розовым внутри, верхушка загнута наружу-вниз пушистой «шапочкой» (как у эталона)
    ear = [(748, 1032, 1), (742, 990), (746, 958), (770, 942), (798, 952), (812, 1004, 1)]
    s.append(shape(ear, CAT, blob([(758, 1022), (768, 972), (804, 1004)], "#9b6150") +
                   line([(764, 1010), (772, 984)], 2, "#d79a84", seed=256, op=.8), w=4.6, seed=253))
    flap = [(732, 1000, 1), (736, 966), (754, 944), (782, 938), (802, 954), (788, 970), (766, 968), (748, 980)]
    s.append(shape(fur(flap, 4, 5, seed=26), CAT, blob([(736, 966), (754, 944), (782, 938), (790, 950), (760, 956)], CAT_FUR, .55),
                   w=4.6, seed=254, id="cat_ear_L"))
    # голова: широкая, пушистые щёки
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884, 990), (940, 1050), (930, 1150), (866, 1150), (902, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .5)
    inner += blob([(806, 1108), (836, 1100), (866, 1108), (860, 1140), (812, 1140)], CAT_FUR, .35)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250, id="cat_head"))
    # глаза: большие зелёные, вертикальный зрачок, блик; веко-шерсть для моргания
    for nm, ex, sd in [("L", CX - 44, 255), ("R", CX + 44, 256)]:
        ep = ellipse_pts(ex, 1072, 34, 38, 14)
        cid = clip_of(ep)
        s.append(f'<g id="cat_eye_{nm}"><path d="{fill_d(ep)}" fill="#b8e04a"/>')
        s.append(f'<g clip-path="url(#{cid})">')
        s.append(blob(ellipse_pts(ex, 1048, 36, 20, 10), "#86b236", .95))
        s.append(blob(ellipse_pts(ex, 1100, 26, 10, 10), "#dcf47e", .7))
        s.append(f'<g id="cat_pupil_{nm}"><ellipse cx="{ex}" cy="1074" rx="11.5" ry="24" fill="#0f0d14"/>'
                 f'<circle cx="{ex + 7}" cy="1059" r="5.6" fill="#fff"/><circle cx="{ex - 6}" cy="1090" r="2.2" fill="#fff" opacity=".8"/></g>')
        s.append(f'<g id="cat_lid_{nm}" transform="translate(0 -84)"><rect x="{ex - 40}" y="990" width="80" height="84" fill="{CAT}"/>'
                 + line([(ex - 36, 1070), (ex, 1076), (ex + 36, 1070)], 4.6, seed=sd) + "</g>")
        s.append(f'<g id="cat_lidlo_{nm}" transform="translate(0 48)"><rect x="{ex - 40}" y="1072" width="80" height="50" fill="{CAT}"/></g>')
        s.append(f'</g><path d="{ink_closed(ep, 4.4, seed=sd + 3)}" fill="{INK}"/></g>')
    # полоски на щеках — по две
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76
            s.append(line([(x0, 1100 + dy), (x0 + sx * 30, 1094 + dy + k * 3)], 5.4, "#ee8a3c", seed=260 + k + sx, taper=.3, wmin=.5))
    # нос, рот, усы
    s.append(shape([(826, 1108), (846, 1108), (836, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836, 1119), (836, 1124)], 2.4, seed=263))
    s.append(line([(822, 1124), (829, 1131), (836, 1124), (843, 1131), (850, 1124)], 3, seed=264))
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CX + sx * 62
            s.append(line([(x0, 1114 + dy), (x0 + sx * 50, 1110 + dy + dl * .4), (x0 + sx * 92, 1106 + dy + dl)], 1.8, "#cfc8dc",
                          seed=270 + k + sx, op=.7))
    s.append("</g>")
    return "".join(s)


