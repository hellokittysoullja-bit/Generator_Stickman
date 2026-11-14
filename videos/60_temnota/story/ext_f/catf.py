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
from ink import fill_d, fur  # noqa: E402
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
