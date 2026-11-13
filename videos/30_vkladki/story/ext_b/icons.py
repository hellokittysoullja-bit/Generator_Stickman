"""Значки дел (без букв) и стикер-листок. Значок рисуется в своих координатах ~[-48, 48], центр (0, 0)."""
import math

import lib
from lib import INK, blob, ellipse_pts, f, line, rect_pts, shape


def envelope(sd=0):
    s = shape(rect_pts(-44, -30, 44, 30, 4), "#fbf6ea", blob([(-44, 10), (44, 10), (44, 30), (-44, 30)], "#e6dcc6", .9), w=3.4, seed=sd + 1)
    s += line([(-42, -27), (0, 6), (42, -27)], 3.4, INK, taper=.2, wmin=.6, seed=sd + 2)
    s += line([(-42, 27), (-12, 0)], 2.6, INK, taper=.3, seed=sd + 3, op=.8) + line([(42, 27), (12, 0)], 2.6, INK, taper=.3, seed=sd + 4, op=.8)
    return s


def cart(sd=0):
    s = line([(-48, -32), (-34, -30), (-24, 14), (30, 14)], 5, INK, taper=.15, wmin=.7, seed=sd + 1)
    s += shape([(-30, -20, 1), (42, -20, 1), (34, 8, 1), (-24, 8, 1)], "#7ec0e8",
               "".join(line([(-14 + k * 14, -18), (-12 + k * 13, 6)], 2.4, "#4a8cb8", taper=.1, wmin=.8, seed=sd + 5 + k) for k in range(4)), w=3.4, seed=sd + 2)
    s += shape(ellipse_pts(-14, 26, 8, 8, 10), "#3a3440", "", w=2.6, seed=sd + 3) + shape(ellipse_pts(24, 26, 8, 8, 10), "#3a3440", "", w=2.6, seed=sd + 4)
    return s


def laptop(sd=0):
    s = shape([(-36, -34, 1), (36, -34, 1), (36, 12, 1), (-36, 12, 1)], "#5b6474",
              blob(rect_pts(-29, -27, 29, 6), "#8fd0f0") + blob([(-29, -27), (-6, -27), (-20, 6), (-29, 6)], "#b9e6f8", .8), w=3.4, seed=sd + 1)
    s += shape([(-44, 12, 1), (44, 12, 1), (50, 26, 1), (-50, 26, 1)], "#8a93a3", line([(-10, 18), (10, 18)], 3, "#5b6474", seed=sd + 3), w=3.4, seed=sd + 2)
    return s


def tooth(sd=0):
    pts = [(-30, -26), (-14, -38), (0, -30), (14, -38), (30, -26), (30, -2), (22, 22), (16, 38), (8, 36), (4, 12), (-4, 12), (-8, 36), (-16, 38),
           (-22, 22), (-30, -2)]
    return shape(pts, "#ffffff", blob([(14, -34), (30, -26), (30, -2), (22, 22), (16, 38), (12, 10), (20, -16)], "#d9e2ee", .9) +
                 line([(-18, -22), (-20, -6)], 4, "#ffffff", seed=sd + 2), w=3.6, seed=sd + 1)


def receipt(sd=0):
    pts = [(-28, -42, 1), (28, -42, 1), (28, 40, 1), (20, 32, 1), (12, 40, 1), (4, 32, 1), (-4, 40, 1), (-12, 32, 1), (-20, 40, 1), (-28, 32, 1)]
    inner = "".join(line([(-18, -28 + k * 14), (18 - (k % 2) * 10, -28 + k * 14)], 3.4, "#9aa3b2", taper=.1, wmin=.8, seed=sd + 3 + k) for k in range(4))
    inner += line([(-18, 26), (18, 26)], 4, "#e05a4a", taper=.1, wmin=.8, seed=sd + 9)
    return shape(pts, "#fbfaf6", inner, w=3.4, seed=sd + 1)


def phone(sd=0):
    s = shape(rect_pts(-22, -42, 22, 42, 9), "#2b2f3a", blob(rect_pts(-16, -32, 16, 30, 3), "#7fd0a0") +
              blob([(-16, -32), (2, -32), (-16, -4)], "#b8eccb", .8), w=3.4, seed=sd + 1)
    s += f'<circle cx="0" cy="36" r="3" fill="#5b6070"/>'
    # волны звонка
    s += line([(30, -18), (36, -6), (30, 6)], 3.4, INK, taper=.3, seed=sd + 2) + line([(38, -26), (46, -6), (38, 14)], 3.4, INK, taper=.3, seed=sd + 3)
    return s


def trash(sd=0):
    pts = [(-8, -34), (-26, -10), (-34, 18), (-26, 38, 1), (26, 38, 1), (34, 18), (26, -10), (8, -34)]
    s = shape(pts, "#3f5a4a", blob([(6, -30), (26, -10), (34, 18), (26, 38), (6, 38)], "#2c4236", .9) +
              line([(-14, -6), (-18, 24)], 3, "#6b8a76", seed=sd + 2, op=.8), w=3.6, seed=sd + 1)
    s += shape([(-14, -44), (0, -34), (14, -44), (8, -30, 1), (-8, -30, 1)], "#3f5a4a", "", w=3, seed=sd + 3)
    return s


def bowl(sd=0):
    s = ""
    for k, (x, y) in enumerate([(-18, -4), (-4, -10), (10, -4), (22, -8), (-8, 0), (4, -2)]):
        s += shape(ellipse_pts(x, y, 8, 6, 8), "#a8662e", "", w=2.2, seed=sd + 10 + k)
    s += shape([(-42, -2, 1), (42, -2, 1), (32, 24), (0, 30), (-32, 24)], "#e8574a",
               blob([(10, -2), (42, -2), (32, 24), (8, 30)], "#b83c32", .9) + line([(-34, 4), (-22, 18)], 4, "#ff9a8a", seed=sd + 2, op=.8), w=3.6, seed=sd + 1)
    # рыбка-косточка на миске
    s += line([(-12, 12), (12, 12)], 3, "#fbe6d0", taper=.1, wmin=.8, seed=sd + 3)
    return s


def report(sd=0):
    s = shape([(-30, -42, 1), (16, -42, 1), (30, -28, 1), (30, 42, 1), (-30, 42, 1)], "#fbfaf6",
              line([(16, -42), (16, -28), (30, -28)], 2.6, INK, taper=.1, wmin=.8, seed=sd + 2), w=3.4, seed=sd + 1)
    for k, (h, c) in enumerate([(22, "#5a9bd8"), (36, "#f0a83a"), (52, "#4fb36a")]):
        x = -20 + k * 15
        s += shape(rect_pts(x, 30 - h, x + 10, 30), c, "", w=2.4, seed=sd + 4 + k)
    return s


def calendar(sd=0):
    s = shape(rect_pts(-40, -36, 40, 40, 6), "#fbfaf6", "", w=3.6, seed=sd + 1)
    s += shape(rect_pts(-40, -36, 40, -14, 6), "#e05a4a", "", w=3.4, seed=sd + 2)
    for k in (-20, 20):
        s += line([(k, -46), (k, -28)], 6, "#5b6070", taper=.1, wmin=.8, seed=sd + 3 + k)
    for r in range(3):
        for c in range(4):
            s += f'<rect x="{-30 + c * 16}" y="{-4 + r * 13}" width="9" height="7" rx="2" fill="#b9c2d0"/>'
    return s


def chat(sd=0):
    """Два пузыря переписки (рилс 30)."""
    s = shape([(-46, -36, 1), (22, -36, 1), (22, 10, 1), (-14, 10, 1), (-30, 26, 1), (-28, 10, 1), (-46, 10, 1)], "#5aa0e6",
              blob([(-46, -6), (22, -6), (22, 10), (-46, 10)], "#3f82c8", .8), w=3.4, seed=sd + 1)
    s += shape([(-6, -14, 1), (46, -14, 1), (46, 28, 1), (34, 28, 1), (38, 42, 1), (20, 28, 1), (-6, 28, 1)], "#fbfaf6",
               blob([(-6, 14), (46, 14), (46, 28), (-6, 28)], "#e3dccb", .8), w=3.4, seed=sd + 2)
    for k in range(3):
        s += f'<circle cx="{8 + k * 13}" cy="7" r="4.6" fill="{INK}"/>'
    return s


def play(sd=0):
    """Кнопка видео ▶ (рилс 30)."""
    s = shape(rect_pts(-46, -32, 46, 32, 14), "#e8453c", blob(rect_pts(-46, 8, 46, 32, 14), "#c13128", .85) +
              blob(rect_pts(-38, -26, 10, -16, 5), "#ff8a80", .8), w=3.6, seed=sd + 1)
    s += shape([(-12, -17, 1), (20, 0, 1), (-12, 17, 1)], "#ffffff", "", w=2.8, seed=sd + 2)
    return s


ICONS = {"envelope": envelope, "cart": cart, "laptop": laptop, "tooth": tooth, "receipt": receipt, "phone": phone, "trash": trash,
         "bowl": bowl, "report": report, "calendar": calendar, "chat": chat, "play": play}
NOTE_COLS = {"yellow": ("#ffe066", "#f2c94c", "#fff1a8"), "pink": ("#ff9fc2", "#f07aa6", "#ffd0e2"),
             "blue": ("#8fd3ff", "#62b5ea", "#c8ecff"), "green": ("#a8e68a", "#7fc962", "#d6f6c4"),
             "orange": ("#ffb870", "#f2994a", "#ffdcb4")}


def icon(name, x, y, sc=1.0, rot=0.0, sd=0):
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{ICONS[name](sd)}</g>'


def note(col, ic, sd=0):
    """Стикер 150×150 с центром (0, 0): клейкая полоска сверху, загнутый уголок, значок."""
    c, c2, c3 = NOTE_COLS[col]
    pts = [(-75, -75, 1), (75, -75, 1), (75, 52, 1), (52, 75, 1), (-75, 75, 1)]
    inner = blob(rect_pts(-80, -80, 80, -52), c2, .7) + blob([(40, -75), (75, -75), (75, 52), (40, 75)], c2, .45)
    inner += ICONS[ic](sd + 20)
    s = shape(pts, c, inner, w=3.8, seed=sd + 1)
    s += shape([(75, 52, 1), (52, 75, 1), (56, 56, 1)], c3, "", w=3, seed=sd + 2)
    return s


def sticky(x, y, col, ic, rot=0.0, sc=1.0, sd=0, shadow=True):
    sh = (f'<g transform="translate({f(x + 8 * sc)} {f(y + 10 * sc)}) rotate({f(rot)}) scale({f(sc)})">'
          f'<path d="{lib.fill_d(rect_pts(-74, -74, 74, 74))}" fill="#10142a" opacity=".35"/></g>') if shadow else ""
    return sh + f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{note(col, ic, sd)}</g>'
