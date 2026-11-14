"""Рилс 61 «стол», группа F: s05 (кот с вопросом на куче бумаг), s17 (кот спит на тёплом столе), s18 (призыв, рукописное «кот»).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Слова — voice/words.json."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import catf  # noqa: E402
import lib  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rrect, shape  # noqa: E402,F401

import numpy as np  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
WI = {}
for i_, w_ in enumerate(WORDS):
    WI.setdefault(w_["word"].strip(".,!?").lower(), []).append(i_)


def wt(word, k=0):
    return WORDS[WI[word][k]]["start"]


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def blinks(t, times, dur=.16):
    v = 0.0
    for tb in times:
        u = (t - tb) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


PAGE, PAGE_SH, PAGE_LN = "#fbf3dc", "#e2d4b2", "#8f8670"


# ───────────────────────────── бумаги ─────────────────────────────
def sheet_pts(cx, cy, w, h, rot, persp=.42):
    """Лист, лежащий на столе: прямоугольник w×h, повёрнутый в плоскости стола на rot°, сжатый по вертикали (вид под углом)."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for (x, y) in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        X, Y = x * c - y * s, x * s + y * c
        out.append((cx + X, cy + Y * persp, 1))
    return out


def sheet(cx, cy, w, h, rot, seed, persp=.42, col=PAGE, marks=True):
    """Лист бумаги со штрихами (без букв): строки-штрихи и маленький набросок."""
    P = sheet_pts(cx, cy, w, h, rot, persp)
    inner = ""
    if marks:
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))

        def q(x, y):
            return (cx + x * c - y * s, cy + (x * s + y * c) * persp)
        rs = np.random.RandomState(seed)
        for j in range(4):
            yy = -h * .3 + j * h * .16
            x1 = w * (.25 + .15 * rs.rand())
            inner += line([q(-w * .36, yy), q(-w * .1, yy + 2), q(x1, yy - 1)], 3, PAGE_LN, seed=seed * 7 + j, taper=.3, wmin=.5, op=.9)
        kind = seed % 3
        if kind == 0:     # спираль
            pp = [q(w * .22 + 22 * (1 - a / 12) * math.cos(a), h * .3 + 22 * (1 - a / 12) * math.sin(a)) for a in np.linspace(0, 11, 30)]
            inner += line(pp, 3, "#c0553f", seed=seed + 90, taper=.3, wmin=.5)
        elif kind == 1:   # стрелка и кружок
            inner += line([q(-w * .3, h * .3), q(w * .05, h * .28)], 3, "#3f6fb0", seed=seed + 91, taper=.2, wmin=.6)
            inner += line([q(-w * .02, h * .2), q(w * .05, h * .28), q(-w * .02, h * .36)], 3, "#3f6fb0", seed=seed + 92, taper=.2, wmin=.6)
            inner += line([q(w * .2 + 18 * math.cos(a), h * .28 + 18 * math.sin(a)) for a in np.linspace(0, 6.4, 18)], 3, "#3f6fb0", seed=seed + 93,
                          taper=.1, wmin=.7)
        else:             # звёздочка-набросок
            for a in range(4):
                r = math.radians(a * 45)
                inner += line([q(w * .22 - 20 * math.cos(r), h * .28 - 20 * math.sin(r)), q(w * .22 + 20 * math.cos(r), h * .28 + 20 * math.sin(r))],
                              3, "#5c9a78", seed=seed + 94 + a, taper=.3, wmin=.5)
    return shape(P, col, inner, w=3.4, seed=seed)


def pile(cx, base_y, w, n_layers, seed, top_y):
    """Куча бумаг спереди: слои-края листов со сдвигами, от base_y до top_y; сверху — несколько листов вразброс (лицом вверх)."""
    o = []
    rs = np.random.RandomState(seed)
    hgt = base_y - top_y
    for j in range(n_layers):          # края стопки снизу вверх
        y = base_y - hgt * (j + .5) / n_layers
        dx = rs.uniform(-34, 34)
        ww = w * rs.uniform(.86, 1.02)
        th = hgt / n_layers + 8
        rot = rs.uniform(-3, 3)
        pts = [(cx + dx - ww / 2, y - th / 2 + rot * 2, 1), (cx + dx + ww / 2, y - th / 2 - rot * 2, 1), (cx + dx + ww / 2 + 6, y + th / 2 - rot * 2, 1),
               (cx + dx - ww / 2 - 6, y + th / 2 + rot * 2, 1)]
        col = PAGE if j % 3 else "#f4e7c6"
        if j == 2:
            col = "#cfe0f0"
        if j == 5:
            col = "#f6d9a6"
        o.append(shape(pts, col, blob([(cx - w, y + th * .1), (cx + w, y + th * .1), (cx + w, y + th), (cx - w, y + th)], PAGE_SH, .8),
                       w=3.2, seed=seed + 11 * j))
    return "".join(o)


def qmark(t, t0, x, y, s=1.0, dur=.34, col=INK, seed=900):
    """Знак вопроса штрихами (значок): крючок рисуется пером, затем точка; после — лёгкий подскок."""
    if t < t0:
        return ""
    P = [(-30, -6), (-26, -44), (0, -64), (32, -56), (42, -26), (24, 4), (4, 22), (0, 52)]
    from ink import sample
    S = sample(P, False, 2.0)
    u = clamp((t - t0) / dur)
    n = max(2, int(len(S) * ease_out(u, 2)))
    hop = -10 * math.exp(-6 * max(0, t - t0 - dur)) * math.sin(2 * math.pi * 2.2 * max(0, t - t0 - dur))
    rot = 6 * math.sin(t * 2.1)
    o = line([tuple(p) for p in S[:n]], 16, col, taper=.35, wmin=.45, seed=seed)
    if t > t0 + dur * .8:
        du = clamp((t - t0 - dur * .8) / .12)
        o += blob(ellipse_pts(0, 84, 11 * ease_out(du), 11 * ease_out(du), 12), col)
    return f'<g transform="translate({x:.1f} {y + hop:.1f}) rotate({rot:.2f}) scale({s:.3f})">{o}</g>'


# ───────────────────────────── s05: кот крупно на куче бумаг ─────────────────────────────
T_BES, T_POM = wt("беспорядок"), wt("помогать")


def wall_desk(t, warm=1.0):
    """Тёплая стена у творческого стола: наброски на стене (без букв), край лампы; стол — дерево."""
    o = []
    g = lib.lin_grad([(0, "#eadcbd", 1), (1, "#dccaa4", 1)])
    o.append(f'<rect x="-900" y="-900" width="3200" height="2400" fill="url(#{g})"/>')
    # наброски на стене: листы на кнопках
    for (x, y, w, h, r, sd) in ((150, 380, 200, 250, -6, 51), (420, 300, 170, 210, 4, 52), (880, 360, 220, 270, 7, 53), (1040, 760, 180, 200, -5, 54),
                               (60, 760, 170, 220, 5, 55)):
        P = lib.T(lib.rect_pts(-w / 2, -h / 2, w / 2, h / 2), x, y, rot=r)
        inner = ""
        rs = np.random.RandomState(sd)
        for j in range(3):
            yy = -h * .3 + j * 26
            inner += line(lib.T([(-w * .35, yy), (w * (.05 + .25 * rs.rand()), yy + 3)], x, y, rot=r), 3, PAGE_LN, seed=sd * 5 + j, taper=.3, wmin=.5)
        cc = ("#c0553f", "#3f6fb0", "#5c9a78", "#e0a24a", "#7b6aa0")[sd % 5]
        if sd % 2:
            inner += line(lib.T([(-40 + 30 * math.cos(a) * (1 - a / 14), 50 + 30 * math.sin(a) * (1 - a / 14)) for a in np.linspace(0, 12, 26)], x, y, rot=r),
                          3.4, cc, seed=sd + 70, taper=.3, wmin=.5)
        else:
            inner += line(lib.T([(-50, 70), (-10, 30), (20, 60), (60, 10)], x, y, rot=r), 3.4, cc, seed=sd + 71, taper=.3, wmin=.5)
        o.append(shape(P, PAGE, inner, w=3.6, seed=sd))
        px, py = lib.T([(0, -h / 2 + 14)], x, y, rot=r)[0]
        o.append(shape(ellipse_pts(px, py, 9, 9, 10), "#d9483b", "", w=2.4, seed=sd + 3))
    # стол: столешница под углом и передний край
    top = [(-900, 1330, 1), (1980, 1330, 1), (1980, 1600, 1), (-900, 1600, 1)]
    o.append(shape(top, "#b98a5c", blob([(-900, 1330), (1980, 1330), (1980, 1352), (-900, 1352)], "#cfa274") +
                   "".join(line([(x0, 1380 + 40 * j), (x0 + 260, 1384 + 40 * j)], 2.4, "#9a6c42", seed=600 + j + x0, op=.7)
                           for j, x0 in enumerate((-100, 300, 650, 120, 820))), w=5, seed=605))
    o.append(blob([(-900, 1600), (1980, 1600), (1980, 2400), (-900, 2400)], "#8d6440"))
    o.append(line([(-900, 1602), (1980, 1602)], 5, seed=607, taper=0))
    return "".join(o)


def lamp_glow_small(x, y, r, u):
    """Небольшой круг тёплого света на столе с чёткой границей (от абажура)."""
    g = lib.rad_grad([(0, "#fff1c8", .85 * u), (.8, "#ffe3a0", .55 * u), (1, "#ffe3a0", 0)], x, y, r, r * .32)
    return f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * .32:.1f}" fill="url(#{g})"/>'


def mug(x, y, k=1.0, seed=0, col="#3f6fb0"):
    """Кружка (временная, до props.py группы A): цилиндр, ручка, кольцо кофе внутри."""
    o = []
    o.append(shape(ellipse_pts(x + 6, y + 4, 70 * k, 12 * k, 14), "#000000", "", ink=False))
    o[-1] = blob(ellipse_pts(x + 6, y + 4, 70 * k, 12 * k, 14), "#5a3d22", .35)
    hand = [(x + 46 * k, y - 110 * k), (x + 86 * k, y - 104 * k, 1), (x + 92 * k, y - 66 * k), (x + 50 * k, y - 40 * k, 1),
            (x + 48 * k, y - 56 * k), (x + 74 * k, y - 70 * k), (x + 72 * k, y - 94 * k), (x + 46 * k, y - 96 * k)]
    o.append(shape(hand, col, "", w=4, seed=seed + 1))
    body = [(x - 50 * k, y - 128 * k, 1), (x + 50 * k, y - 128 * k, 1), (x + 46 * k, y - 4 * k), (x, y + 6 * k), (x - 46 * k, y - 4 * k)]
    o.append(shape(body, col, blob([(x + 14 * k, y - 130 * k), (x + 52 * k, y - 130 * k), (x + 48 * k, y), (x + 18 * k, y)], lib.mix(col, "#000000", .3), .8),
                   w=4.6, seed=seed + 2))
    o.append(shape(ellipse_pts(x, y - 128 * k, 50 * k, 12 * k, 16), "#4a2c1a", blob(ellipse_pts(x - 6 * k, y - 126 * k, 34 * k, 6 * k, 12), "#6b4228", .8),
                   w=3.6, seed=seed + 3))
    return "".join(o)


def frame05(t):
    T0 = 9.7
    # кот: смотрит на зрителя → вниз на листок → лапа сталкивает листок на «беспорядок» → снова на зрителя → «помогать?» наклон, ухо
    look_down = sm(t, 10.55, 10.8) * (1 - sm(t, 11.25, 11.6))
    reach = sm(t, T_BES - .02, T_BES + .16) * (1 - sm(t, T_BES + .34, T_BES + .62))
    lift = sm(t, 10.66, 10.86) * (1 - sm(t, T_BES + .08, T_BES + .2)) + .55 * sm(t, T_BES + .34, T_BES + .45) * (1 - sm(t, T_BES + .45, T_BES + .62))
    tilt_q = sm(t, T_POM - .06, T_POM + .2)
    st = dict(look=(.55 * look_down + .1 * math.sin(t * .9) * (1 - look_down), .7 * look_down),
              blink=blinks(t, (10.12, 11.72)),
              turn=.18 * look_down - .1 * tilt_q,
              tilt=2.2 * math.sin(t * 1.3) + 8 * look_down + 13 * tilt_q - 4 * bump(t, T_POM + .25, .5),
              ear=2 * math.sin(t * 3.1) + 16 * bump(t, T_POM + .02, .2) - 8 * bump(t, T_POM + .2, .2),
              perk=.35 * tilt_q,
              tail=9 * math.sin(t * 2.3) + 12 * bump(t, T_BES + .1, .5),
              flame_e=1.0 + .9 * bump(t, T_BES + .05, .4) + .4 * bump(t, T_POM, .4),
              reach=reach, reach_lift=lift,
              head_dx=6 * look_down, head_dy=10 * look_down,
              sy=1 - .03 * bump(t, T_BES, .3))
    CK = 2.5
    CXW, CYW = 500.0, 1250.0
    # листок, который сталкивает лапа: лежит справа на верху кучи; паж толкает, лист съезжает с края и падает
    s_rest = (770.0, 1296.0)
    s_x, s_y, s_rot, s_pers = s_rest[0], s_rest[1], 8.0, .42
    push = clamp((t - T_BES) / .16)
    if t > T_BES:
        s_x = s_rest[0] + 70 * ease_out(push, 2)
        s_y = s_rest[1] + 30 * ease_out(push, 2)
    if t > T_BES + .16:
        e = t - T_BES - .16
        land = 1540.0
        tl = math.sqrt(2 * (land - s_rest[1] - 30) / 1500)
        ee = min(e, tl)
        s_x = s_rest[0] + 70 + 150 * ee + 18 * math.sin(ee * 12)
        s_y = s_rest[1] + 30 + 0.5 * 1500 * ee * ee
        s_rot = 8 + 70 * ee + 16 * math.sin(ee * 10)
        s_pers = .42 + .45 * abs(math.sin(ee * 7)) * clamp(1 - (e - tl) * 4 if e > tl else 1)
        if e > tl:          # лёг на стол, чуть подпрыгнул
            s_y -= 10 * math.exp(-8 * (e - tl)) * abs(math.sin(14 * (e - tl)))
    # камера: медленный наезд на морду, поворот на вопросе
    u = sm(t, T0, 12.95)
    z = 1.0 + .3 * u + .04 * bump(t, T_BES, .3) + .05 * bump(t, T_POM, .45)
    head_y = CYW + (1072 - 1306) * CK
    cx = 540 + (CXW - 540) * u + 6 * math.sin(t * 1.1)
    cy = 1010 + (head_y + 120 - 1010) * u
    rot = -.8 + 1.6 * u + 2.4 * tilt_q
    set_ink(z)
    o = [wall_desk(t)]
    o.append(lamp_glow_small(110, 1400, 210, 1.0))
    o.append(mug(890, 1470, 1.05, seed=700))
    o.append(pile(500, 1430, 660, 11, 40, 1236))
    # листы свисают с кучи и торчат вразброс
    o.append(sheet(190, 1330, 180, 230, 28, 36, .95))
    o.append(sheet(820, 1360, 170, 220, -22, 37, .9))
    # верхние листы кучи лицом вверх
    o.append(sheet(300, 1246, 240, 300, -18, 31))
    o.append(sheet(520, 1236, 250, 300, 6, 32))
    o.append(sheet(640, 1262, 200, 240, 24, 35))
    if t < T_BES + .16:
        o.append(sheet(s_x, s_y, 200, 260, s_rot, 34, s_pers, col="#f6d9a6"))
    set_ink(z * CK)
    o.append(blob(ellipse_pts(CXW + 10, CYW + 6, 190, 22, 14), "#7a5a3a", .35))
    o.append(catf.draw_f(CXW, CYW, CK, st, t))
    set_ink(z)
    if t >= T_BES + .16:
        o.append(sheet(s_x, s_y, 200, 260, s_rot, 34, s_pers, col="#f6d9a6"))
    # знак вопроса штрихами справа от головы
    o.append(qmark(t, T_POM + .02, 175, 540, 1.7, col="#1c1622", seed=905))
    cam = lib.cam(cx, cy, z, rot)
    return f'<g transform="{cam}">{"".join(o)}</g>'


FRAMES = {"s05": frame05}


def frame(sid, t):
    lib.dyn_begin()
    body = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#d9c9a8"/>{body}')
