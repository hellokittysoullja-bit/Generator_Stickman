"""Кот группы F рилса 60: голова с зевком и довольным прищуром поверх common/cat.py (анфас, как look/hero.png: ЛЕВОЕ ухо загнуто).
head2(st, t) — как cat.head, плюс st['yawn'] 0..1 (рот открыт, глаза зажмурены) и st['happy'] 0..1 (глаза-дуги ∩, улыбка, румянец).
draw2(x, y, k, st, t) — как cat.draw, но с этой головой."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
for d in (os.path.join(STORY, "common"), os.path.join(STORY, "..", "..", "59_podarok", "story", "common")):
    if os.path.isdir(d):
        sys.path.insert(0, d)
import cat as Cat  # noqa: E402
import lib  # noqa: E402
from ink import ellipse_pts, fill_d, fur  # noqa: E402
from lib import INK, blob, line, shape  # noqa: E402

CAT, CAT_SH, CAT_FUR, CAT_EDGE = Cat.CAT, Cat.CAT_SH, Cat.CAT_FUR, Cat.CAT_EDGE
CX = Cat.CX


def happy_eye(ex, ey, rx, sd, k=1.0):
    """Закрытый довольный глаз ∩: дуга вверх, толще посередине."""
    h = 15 * k
    return line([(ex - rx * .92, ey + 8), (ex - rx * .5, ey - h * .6), (ex, ey - h), (ex + rx * .5, ey - h * .6), (ex + rx * .92, ey + 8)], 6.2, INK, seed=sd + 50,
                taper=.5, wmin=.4)


def squeeze_eye(ex, ey, rx, sd, side):
    """Зажмуренный (зевок): дуга ∪ и две складки у внешнего края."""
    o = line([(ex - rx * .9, ey - 2), (ex - rx * .4, ey + 9), (ex + rx * .4, ey + 9), (ex + rx * .9, ey - 2)], 6, INK, seed=sd + 40, taper=.5, wmin=.4)
    for i, dy in enumerate((-9, -1)):
        o += line([(ex + side * rx * .85, ey + dy), (ex + side * (rx + 16), ey + dy - 6 + i * 2)], 3, INK, seed=sd + 60 + i, taper=.6)
    return o


def mouth(FX, yawn, happy):
    """Рот. yawn 0..1 — широко открыт с розовым нёбом, языком и двумя клыками; иначе спокойная или довольная линия."""
    o = []
    if yawn > .04:
        w = 30 + 20 * yawn
        hgt = 62 * yawn
        cx, y0 = 836 + FX, 1122
        pts = [(cx - w, y0 - 2, 1), (cx - w * .8, y0 + hgt * .55), (cx - w * .35, y0 + hgt * .95), (cx, y0 + hgt), (cx + w * .35, y0 + hgt * .95),
               (cx + w * .8, y0 + hgt * .55), (cx + w, y0 - 2, 1), (cx, y0 - 6 + 4 * yawn)]
        tongue = [(cx - w * .5, y0 + hgt * .95), (cx - w * .4, y0 + hgt * .55), (cx, y0 + hgt * .45), (cx + w * .4, y0 + hgt * .55), (cx + w * .5, y0 + hgt * .95),
                  (cx, y0 + hgt * 1.02)]
        inner = blob(tongue, "#e8808c")
        inner += line([(cx, y0 + hgt * .5), (cx, y0 + hgt * .95)], 2, "#c4565f", seed=290, op=.9)
        inner += blob([(cx - w, y0 - 6), (cx + w, y0 - 6), (cx + w * .8, y0 + hgt * .3), (cx - w * .8, y0 + hgt * .3)], "#8f3b4c", .9)
        o.append(shape(pts, "#5a2b33", inner, w=3.4, seed=292))
        for sx in (-1, 1):
            fx = cx + sx * w * .55
            o.append(shape([(fx - 5, y0 - 2, 1), (fx + 5, y0 - 2, 1), (fx + sx, y0 + 13 * min(1, yawn * 1.6))], "#f6efe0", w=1.6, seed=294 + sx))
        return "".join(o)
    if happy > .5:
        return line([(818 + FX, 1121), (828 + FX, 1134), (836 + FX, 1126), (844 + FX, 1134), (854 + FX, 1121)], 3.4, seed=265)
    return line([(822 + FX, 1124), (829 + FX, 1131), (836 + FX, 1124), (843 + FX, 1131), (850 + FX, 1124)], 3, seed=264)


def head2(st, t):
    turn = st.get("turn", 0.0)
    look = st.get("look", (0.0, 0.0))
    blink = st.get("blink", 0.0)
    yawn = st.get("yawn", 0.0)
    happy = st.get("happy", 0.0)
    FX = 22 * turn
    s = []
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    if yawn > .04:      # голова чуть шире и ниже челюстью
        hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (928, 1112 + 8 * yawn), (884, 1146 + 18 * yawn), (788, 1146 + 18 * yawn),
              (744, 1112 + 8 * yawn)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884 + FX * .5, 990), (940, 1050), (930, 1150), (866 + FX * .5, 1150), (902 + FX * .5, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    inner += blob([(800 + FX, 1106), (836 + FX, 1098), (872 + FX, 1106), (864 + FX, 1142), (808 + FX, 1142)], CAT_FUR, .45)
    for i, st_ in enumerate([[(800, 1004), (806, 1016)], [(836, 996), (838, 1010)], [(870, 1002), (866, 1014)]]):
        inner += line(st_, 2, CAT_EDGE, seed=258 + i, op=.8)
    if happy > .3:      # румянец-щёки
        for sx in (-1, 1):
            inner += blob(lib.ellipse_pts(836 + FX + sx * 68, 1108, 20, 10, 10), "#9b6150", .55 * happy)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250))
    s.append(Cat.ears(st.get("ear", 0.0), st.get("perk", 0.0)))
    CXH = CX + FX
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76 + FX * (.5 if sx * turn > 0 else 1.0)
            ln = 30 * (1 - .4 * max(0, sx * turn))
            s.append(line([(x0, 1100 + dy), (x0 + sx * ln, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    for nm, ex, sd in [("L", CXH - 44 - 4 * turn, 255), ("R", CXH + 44 - 4 * turn, 256)]:
        sq = 1.0 - .22 * max(0.0, turn if nm == "R" else -turn)
        if yawn > .3:
            s.append(squeeze_eye(ex, 1072, 34 * sq, sd, -1 if nm == "L" else 1))
        elif happy > .75:
            s.append(happy_eye(ex, 1072, 34 * sq, sd, min(1.0, (happy - .75) * 4)))
        else:
            s.append(Cat.eye(ex, 1072, 34, 38, look, max(blink, .55 * happy / .75), sd, sq))
    s.append(shape([(826 + FX, 1108), (846 + FX, 1108), (836 + FX, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836 + FX, 1119), (836 + FX, 1124)], 2.4, seed=263))
    s.append(mouth(FX, yawn, happy))
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CXH + sx * 58
            wv = 3 * math.sin(t * 2.3 + k + sx)
            s.append(line([(x0, 1128 + dy * .8), (x0 + sx * 50, 1126 + dy + dl * .5 + wv * .5), (x0 + sx * 96, 1124 + dy * 1.2 + dl + wv)], 1.4,
                          "#cfcbe0", seed=270 + k + sx, op=.9))
    return "".join(s)


def draw2(x, y, k, st, t):
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    tilt = st.get("tilt", 0.0)
    o = [f'<g transform="rotate({st.get("tail", 0.0):.2f} {Cat.TAIL_PIVOT[0]} {Cat.TAIL_PIVOT[1]})">{Cat.tail_art()}{Cat.flame(t, 1.3, st.get("flame_e", 1.0))}</g>']
    o.append(f'<g transform="translate({Cat.CX} {Cat.CBOT}) scale(1 {br:.4f}) translate({-Cat.CX} {-Cat.CBOT})">{Cat.body()}</g>')
    hy = -(br - 1) * (Cat.CBOT - Cat.NECK[1]) + 70 * st.get("drop", 0.0)
    o.append(f'<g transform="translate(0 {hy:.2f}) rotate({tilt:.2f} {Cat.NECK[0]} {Cat.NECK[1]})">{head2(st, t)}</g>')
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-Cat.CX} {-Cat.CBOT})">{"".join(o)}</g>'


# ═══════════════════════ кот со спины (s15): тот же рисунок, вид сзади ═══════════════════════
def _mx(pts):
    """Отражение относительно оси кота: со спины правое (загнутое) ухо кота — справа от зрителя."""
    return [(2 * CX - p[0], p[1]) + tuple(p[2:]) for p in pts]


def back_ears(ear=0.0):
    s = []
    # стоячее ухо (у кота левое) — со спины слева от зрителя, тыльная сторона уха — шерсть, без розового
    re_out = _mx([(864, 1004), (902, 922, 1), (932, 1016)])
    re_fill = re_out + _mx([(934, 1046), (866, 1046)])
    g = [blob(re_fill, CAT)]
    c = lib.clip_of(re_fill)
    g.append(f'<g clip-path="url(#{c})">' + blob(_mx([(902, 924), (940, 1000), (936, 1016), (912, 1012)]), CAT_SH, .75) +
             line(_mx([(892, 1000), (900, 968)]), 2, CAT_EDGE, seed=352, op=.8) + "</g>")
    g.append(line(re_out, 5, seed=351, taper=.25, wmin=.3))
    s.append(f'<g transform="rotate({-ear:.2f} {2 * CX - 898} 1030)">{"".join(g)}</g>')
    # загнутое ухо (у кота правое) — справа от зрителя: кончик свисает наружу
    le_out = _mx([(752, 1014), (744, 986), (728, 994, 1), (728, 966), (746, 948), (772, 940), (796, 948), (808, 968), (814, 1006)])
    le_fill = le_out + _mx([(816, 1046), (752, 1046)])
    g = [blob(le_fill, CAT)]
    c = lib.clip_of(le_fill)
    g.append(f'<g clip-path="url(#{c})">' + blob(_mx([(728, 940), (812, 940), (806, 972), (770, 974), (744, 984), (726, 996)]), CAT_SH, .7) + "</g>")
    g.append(line(_mx([(740, 980), (770, 972), (800, 970)]), 2.4, seed=355, op=.85))
    g.append(line(le_out, 5, seed=353, taper=.25, wmin=.3))
    s.append(f'<g transform="rotate({ear * .3:.2f} {2 * CX - 780} 1030)">{"".join(g)}</g>')
    return "".join(s)


def back_head(st, t):
    s = []
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 5, 9, seed=29)
    inner = blob([(884, 990), (940, 1050), (930, 1150), (870, 1150), (900, 1080)], CAT_SH, .85)
    inner += blob([(790, 1006), (836, 996), (876, 1006), (860, 1030), (810, 1030)], CAT_FUR, .5)
    for i, p in enumerate([[(812, 1016), (816, 1034)], [(836, 1010), (838, 1030)], [(860, 1016), (856, 1034)], [(826, 1060), (830, 1080)],
                           [(852, 1062), (848, 1082)]]):
        inner += line(p, 2, CAT_EDGE, seed=358 + i, op=.8)
    # усы видны из-за щёк
    for sx in (-1, 1):
        for k, dy in enumerate((-4, 6, 16)):
            wv = 3 * math.sin(t * 2.3 + k + sx)
            s.append(line([(CX + sx * 84, 1110 + dy), (CX + sx * 118, 1106 + dy + k * 3 + wv * .5), (CX + sx * 150, 1104 + dy + k * 5 + wv)], 1.6,
                          "#cfcbe0", seed=370 + k + sx, op=.9))
    s.append(shape(hp, CAT, inner, w=5.2, seed=357))
    s.append(back_ears(st.get("ear", 0.0)))
    return "".join(s)


def back_body(legs=0.0, walk=None):
    """legs 0..1 — задние лапы вытянуты вниз (прыжок); walk — фаза шага (лапы по очереди приподнимаются)."""
    s = []
    for sx in (-1, 1):
        px = CX + sx * 62
        lift = 0.0
        if walk is not None:
            lift = max(0.0, math.sin(2 * math.pi * walk + (0 if sx < 0 else math.pi))) * 16
        dy = 70 * legs
        if legs > .05:
            leg = [(px - 22, 1250), (px + 22, 1250), (px + 18 + sx * 4, 1286 + dy), (px - 18 + sx * 4, 1286 + dy)]
            s.append(shape(leg, CAT, blob([(px + 4, 1250), (px + 22, 1250), (px + 22, 1300 + dy), (px + 4, 1300 + dy)], CAT_SH, .7), w=4.4, seed=380 + sx))
        foot = ellipse_pts(px + sx * 4, 1290 + dy - lift, 34, 22, 12, rot=sx * 8)
        s.append(shape(foot, CAT, blob(lib.T(ellipse_pts(px, 1296 + dy - lift, 26, 14, 10), sx * 6, 0), CAT_SH, .6), w=4.6, seed=382 + sx))
        # пятка: оранжевая подушечка видна сзади краешком
        s.append(blob(ellipse_pts(px + sx * 6, 1302 + dy - lift, 12, 5, 8), "#e8823a"))
    bd = [(756, 1296), (738, 1250), (744, 1196), (770, 1158), (806, 1140), (866, 1140), (902, 1158), (928, 1196), (934, 1250), (916, 1296)]
    bp = fur(bd, 4, 10, seed=27)
    inner = blob([(862, 1140), (940, 1180), (940, 1300), (870, 1300), (890, 1220)], CAT_SH, .9)
    inner += blob([(822, 1150), (850, 1150), (848, 1290), (824, 1290)], CAT_FUR, .35)
    for i, p in enumerate([[(800, 1190), (808, 1208)], [(866, 1196), (860, 1214)], [(812, 1240), (818, 1258)], [(856, 1244), (852, 1262)],
                           [(836, 1170), (836, 1190)]]):
        inner += line(p, 2.2, CAT_EDGE, seed=384 + i, op=.85)
    s.append(shape(bp, CAT, inner, w=5, seed=386))
    return "".join(s)


def draw_back(x, y, k, st, t):
    """Кот со спины. st: sx, sy (сжатие/растяжение тела от точки опоры), legs, walk, tail (град), flame_e, ear, head_dx, head_dy, rot (град)."""
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    sx, sy = st.get("sx", 1.0), st.get("sy", 1.0) * br
    sq = f'translate({CX} {Cat.CBOT}) scale({sx:.4f} {sy:.4f}) translate({-CX} {-Cat.CBOT})'
    o = [f'<g transform="{sq}">{back_body(st.get("legs", 0.0), st.get("walk"))}</g>']
    hy = -(sy - 1) * (Cat.CBOT - Cat.NECK[1]) + st.get("head_dy", 0.0)
    o.append(f'<g transform="translate({st.get("head_dx", 0.0):.2f} {hy:.2f}) rotate({st.get("tilt", 0.0):.2f} {Cat.NECK[0]} {Cat.NECK[1]})">{back_head(st, t)}</g>')
    # со спины хвост лежит перед телом и поднимается справа, огонёк над ним не закрыт головой
    o.append(f'<g transform="{sq}"><g transform="rotate({st.get("tail", 0.0):.2f} {Cat.TAIL_PIVOT[0]} {Cat.TAIL_PIVOT[1]})">{Cat.tail_art()}'
             f'{Cat.flame(t, 1.3, st.get("flame_e", 1.0))}</g></g>')
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({st.get("rot", 0.0):.2f}) scale({k:.4f}) translate({-CX} {-Cat.CBOT})">{"".join(o)}</g>'
