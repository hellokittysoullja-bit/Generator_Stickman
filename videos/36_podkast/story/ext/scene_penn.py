"""Сцена campus рилса 36 (s09): «В Пенсильвании людям…» (13.35–15.3). Американский университет осенью, день: корпус из
красного кирпича с белыми окнами, в центре — кирпичная башенка с белой звонницей и зелёным шпилем; осенние деревья
(рыжие, красные, жёлтые), листья на газоне. На «Пенсильвании» (13.49) порыв ветра — листья кружат; на «людям» (14.24)
по дорожке слева направо идут трое в спортивном (разные причёски и цвет кожи). Без букв. Камера: медленный наезд.
Основа — scene_campus рилса 34 (кирпич, окна, газон, люди person.py). Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import parts34 as P
import person
import scene_campus as C
from lib import (INK, W, H, blob, blur, cam, clamp, ease_io, ellipse_pts, f, line, rect_pts, shape, smooth, svg)

_ST = {}
PENN = P.wt("пенсильвании")     # 13.49
LYUDI = P.wt("людям")            # 14.24
GROUND = C.GROUND                # 1090
PATH_Y = 1195                    # дорожка перед корпусом
WHITE, WHITE_SH = C.WHITE, C.WHITE_SH
AUT = [("#e8762a", "#c25a1c", "#f6a04a"), ("#d8442e", "#a83020", "#ef7050"), ("#f2b632", "#cf8c1e", "#ffd76a")]

RUNNERS = [
    dict(skin="#6b4430", hair="short", hair_c="#1c1412", top="#2f6db5", low="#24304a", track="#ffffff", zip=True, face=.35, shoes="#f2eee6"),
    dict(skin="#f4d0b4", hair="ponytail", hair_c="#7a3a1c", top="#e2543f", low="#2a2a3a", track="#f2eee6", face=.35, lashes=True, shoes="#3a9a6a"),
    dict(skin="#d9a477", hair="curly", hair_c="#2a1a14", top="#3a9a6a", low="#3a3f4c", track="#ffd23a", zip=True, face=.35, shoes="#e2543f"),
]


def tower():
    s = []
    x = 540
    # кирпичный ствол башни
    s.append(C.brick_wall(450, 630, 250, 600, 1700))
    for k, y in enumerate((300,)):
        s.append(shape(rect_pts(x - 26, y, x + 26, y + 80, 26), "#2f3a52", blob(rect_pts(x - 26, y + 50, x + 26, y + 80), "#222a3c") +
                       line([(x, y + 8), (x, y + 80)], 4, WHITE, taper=.05, wmin=.9, seed=1710 + k), w=3.6, seed=1712 + k))
        s.append(shape(rect_pts(x - 34, y + 80, x + 34, y + 94), WHITE, "", w=3, seed=1714 + k))
    # белая звонница: карниз, арки-проёмы, купол, шпиль
    s.append(shape(rect_pts(436, 232, 644, 254), WHITE, blob(rect_pts(436, 244, 644, 254), WHITE_SH), w=3.6, seed=1720))
    bell = rect_pts(468, 110, 612, 232)
    inner = blob(rect_pts(570, 110, 612, 232), WHITE_SH, .9)
    for k, ax in enumerate((500, 540, 580)):
        inner += blob([(ax - 13, 220, 1), (ax - 13, 150), (ax, 136), (ax + 13, 150), (ax + 13, 220, 1)], "#3a4660")
    s.append(shape(bell, WHITE, inner, w=4, seed=1721))
    s.append(shape(rect_pts(456, 94, 624, 112), WHITE, blob(rect_pts(456, 104, 624, 112), WHITE_SH), w=3.4, seed=1722))
    s.append(shape([(470, 96, 1), (540, -40, 1), (610, 96, 1)], "#5f9a7a", blob([(540, -40), (610, 96), (560, 96)], "#4a7d61"), w=4, seed=1723))
    s.append(line([(540, -40), (540, -90)], 5, INK, taper=.1, wmin=.8, seed=1724))
    s.append(shape(ellipse_pts(540, -92, 9, 9, 10), "#e8c24a", "", w=3, seed=1725))
    return "".join(s)


def building():
    s = []
    s.append(f'<g transform="translate(0 70)">{tower()}</g>')
    s.append(C.brick_wall(-360, 1440, 560, GROUND, 1310))
    for row, y in enumerate((620, 830)):
        for k, x in enumerate((-260, -100, 60, 220, 380, 700, 860, 1020, 1180, 1340)):
            s.append(C.window(x, y, 84, 140, 1400 + row * 100 + k * 7))
    # карниз и крыша крыла
    s.append(shape(rect_pts(-380, 530, 1460, 562), WHITE, blob(rect_pts(-380, 550, 1460, 562), WHITE_SH), w=3.6, seed=1600))
    s.append(shape([(-390, 532, 1), (-350, 492, 1), (1420, 492, 1), (1470, 532, 1)], "#5b5f6e", blob(rect_pts(-380, 518, 1460, 532), "#454856"), w=3.6, seed=1601))
    # вход в центре: белая арка, двойная дверь
    s.append(shape(rect_pts(470, 820, 610, GROUND - 2, 8), WHITE, "", w=4, seed=1630))
    s.append(shape([(486, GROUND - 4, 1), (486, 880), (540, 842), (594, 880), (594, GROUND - 4, 1)], "#6b3a26",
                   blob(rect_pts(540, 850, 594, GROUND), "#552c1c") + line([(540, 850), (540, GROUND - 8)], 3, INK, seed=1631, op=.8) +
                   '<circle cx="528" cy="990" r="5" fill="#e8c24a"/><circle cx="552" cy="990" r="5" fill="#e8c24a"/>', w=4, seed=1632))
    for k in range(3):
        y = GROUND + k * 18
        s.append(shape(rect_pts(450 - k * 18, y, 630 + k * 18, y + 18), "#ece4d6", blob(rect_pts(450 - k * 18, y + 12, 630 + k * 18, y + 18), "#cfc6b6"),
                       w=3, seed=1640 + k))
    return "".join(s)


def lawn():
    s = []
    s.append(f'<rect x="-800" y="{GROUND}" width="{W + 1600}" height="1500" fill="#8fb85a"/>')
    s.append(line([(-800, GROUND), (W + 800, GROUND)], 4.4, INK, taper=.05, wmin=.9, seed=1901))
    # дорожка
    s.append(blob([(-800, PATH_Y - 50), (W + 800, PATH_Y - 50), (W + 800, PATH_Y + 90), (-800, PATH_Y + 90)], "#d9cdb0"))
    s.append(line([(-800, PATH_Y - 50), (W + 800, PATH_Y - 50)], 3.6, INK, taper=.05, wmin=.9, seed=1902))
    s.append(line([(-800, PATH_Y + 90), (W + 800, PATH_Y + 90)], 3.6, INK, taper=.05, wmin=.9, seed=1903))
    for k in range(-6, 14):
        x = k * 140
        s.append(line([(x, PATH_Y - 46), (x - 20, PATH_Y + 86)], 2, "#bfb193", taper=.1, wmin=.7, seed=1910 + k % 7, op=.8))
    # опавшие листья на газоне
    rs = np.random.RandomState(19)
    for k in range(70):
        x = rs.uniform(-500, W + 500)
        y = rs.choice([rs.uniform(GROUND + 20, PATH_Y - 60), rs.uniform(PATH_Y + 100, PATH_Y + 600)])
        c = AUT[k % 3][0]
        s.append(blob(ellipse_pts(x, y, 9, 5, 8, rot=rs.uniform(0, 180)), c, .9))
    # кусты у входа
    for k, x in enumerate((380, 700)):
        s.append(shape(P.cloud_pts(x, GROUND + 10, 70, 38, 6, 1950 + k), "#5d8f40", blob(ellipse_pts(x + 16, GROUND + 26, 54, 16, 10), "#467232"),
                       w=4, seed=1960 + k))
    return "".join(s)


def tree(x, y, h, t, sd, sc=1.0, pal=0, gust=0.0):
    sway = 5 * math.sin(t * 1.3 + sd) + 22 * gust
    c, csh, chi = AUT[pal]
    s = shape(lib.band([(x, y), (x + 4, y - h * .5), (x + 2 + sway * .3, y - h * .8)], 46 * sc, 26 * sc, step=6, cap=False), "#7a5232",
              blob(lib.band([(x + 12, y), (x + 14, y - h * .5), (x + 10, y - h * .8)], 16 * sc, 10 * sc, step=6, cap=False), "#5a3a22", .9), w=4, seed=sd)
    for k, (dx, dy, r) in enumerate(((-90, -1.0, 120), (80, -1.05, 120), (0, -1.25, 140), (-40, -0.85, 100), (60, -0.82, 100))):
        cc = AUT[(pal + (k == 2)) % 3]
        cx, cy = x + dx * sc + sway * (1 + k * .2), y + h * dy
        s += shape(P.cloud_pts(cx, cy, r * sc, r * .8 * sc, 7, sd + 10 + k), cc[0],
                   blob(ellipse_pts(cx + 30 * sc, cy + 34 * sc, r * .8 * sc, r * .45 * sc, 12), cc[1], .85) +
                   blob(ellipse_pts(cx - 30 * sc, cy - 30 * sc, r * .35 * sc, r * .2 * sc, 10), cc[2], .85), w=4, seed=sd + 20 + k)
    return s


def leaf(x, y, rot, sc, col, sd):
    c, csh, _ = col
    pts = [(-16, 0, 1), (-6, -9), (8, -8), (18, 0, 1), (8, 8), (-6, 9)]
    inner = line([(-14, 0), (14, 0)], 1.6, csh, taper=.1, wmin=.8, seed=sd + 1)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{shape(pts, c, inner, w=2.4, seed=sd)}</g>'


def leaves(t):
    """Листья кружат: с «Пенсильвании» порыв — листья летят слева направо по спиралям, вращаются."""
    s = []
    rs = np.random.RandomState(31)
    g = smooth(PENN - 0.15, PENN + 0.3, t)
    for k in range(26):
        x0, y0 = rs.uniform(-500, W + 300), rs.uniform(100, 1150)
        sp, ph, r = rs.uniform(120, 260), rs.uniform(0, 6.28), rs.uniform(30, 70)
        e = t - 13.0
        drift = sp * e * (0.4 + 1.2 * g)
        x = (x0 + drift + 300 * g) % (W + 900) - 450 + r * math.cos(t * 3 + ph)
        y = y0 + 60 * e + r * math.sin(t * 3.4 + ph) * (0.5 + g)
        rot = t * (200 + 160 * g) * (1 if k % 2 else -1) + ph * 57
        sc = rs.uniform(1.1, 1.9) * (0.75 + 0.25 * abs(math.cos(t * 4 + ph)))
        s.append(leaf(x, y, rot, sc, AUT[k % 3], 2600 + k * 3))
    return "".join(s)


def runners(t):
    """Трое в спортивном выходят слева на «людям» и идут бодрым шагом по дорожке вправо."""
    out = []
    e = t - (LYUDI - 0.9)
    for i, spec in enumerate(RUNNERS):
        x0 = -200 - i * 210
        v = 300 + i * 12
        x = x0 + v * max(0.0, e)
        y = PATH_Y + 40 + (i % 2) * 26
        if x < -500:
            continue
        ph = max(0.0, e) * 11 + i * 1.7
        pose = {"walk": ph, "look": (0.6, 0.0), "mouth": "smile", "brow": 0.4, "head_tilt": 3 * math.sin(ph + i),
                "blink": P.bump(t, 14.8 + i * 0.17, 0.14), "curl": {"L": .7, "R": .7}}
        sc = 0.8
        out.append((y, blob(ellipse_pts(x, y + 6, 100 * sc, 14 * sc, 12), "#7a6a4a", .4, blur(4)) +
                    person.draw(spec, pose, x, y, sc, sd=2400 + i * 100)))
    out.sort()
    return "".join(o for _, o in out)


def s09(t):
    gust = smooth(PENN - 0.1, PENN + 0.25, t) * (0.6 + 0.4 * math.sin(t * 5))
    art = [_ST["sky"], C.sun(t), C.clouds(t), _ST["trees_back"], _ST["building"], _ST["lawn"]]
    art.append(tree(-60, GROUND + 40, 560, t, 2500, 1.2, 0, gust))
    art.append(tree(1150, GROUND + 40, 520, t, 2550, 1.1, 1, gust))
    art.append(tree(250, GROUND + 20, 380, t, 2580, 0.7, 2, gust))
    art.append(tree(850, GROUND + 20, 360, t, 2590, 0.66, 0, gust))
    art.append(runners(t))
    art.append(leaves(t))
    u = clamp((t - 13.15) / 2.35)
    sc = 1.0 + 0.08 * ease_io(u) + 0.025 * P.kick(t, PENN, 6, 14) + 0.015 * P.kick(t, LYUDI, 6, 14)
    return "".join(art), cam(540 + 20 * u, 940 + 20 * u, sc, -0.6 + 0.9 * u)


def build_static():
    if _ST:
        return
    _ST["sky"] = C.sky()
    _ST["building"] = building()
    _ST["lawn"] = lawn()
    _ST["trees_back"] = (shape(P.cloud_pts(-220, 540, 260, 120, 9, 2700), "#d88a3a", "", w=4, seed=2701) +
                         shape(P.cloud_pts(1320, 540, 260, 120, 9, 2710), "#c9603a", "", w=4, seed=2711))
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = s09(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#a6d4f5"/><g transform="{cm}">{art}</g>')
