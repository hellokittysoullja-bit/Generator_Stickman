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
import props  # noqa: E402
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
    o.append(props.mug(900, 1500, 1.8, col="blue", steam=1.0, t=t, seed=700))
    o.append(props.paper_pile(500, 1440, 2.2, seed=61, sy=.5, n=13))
    # верхние листы кучи лицом вверх (на них сидит кот)
    o.append(props.paper(330, 1262, 1.7, -18, 140, 170, 31, "sketch", .45))
    o.append(props.paper(520, 1248, 1.8, 6, 140, 170, 32, "lines", .45))
    o.append(props.paper(660, 1272, 1.6, 24, 130, 160, 35, "grid", .45))
    if t < T_BES + .16:
        o.append(props.paper(s_x, s_y, 1.6, s_rot, 125, 160, 34, "sketch", s_pers, col="#f6d9a6"))
    set_ink(z * CK)
    o.append(blob(ellipse_pts(CXW + 10, CYW + 6, 190, 22, 14), "#7a5a3a", .35))
    o.append(catf.draw_f(CXW, CYW, CK, st, t))
    set_ink(z)
    if t >= T_BES + .16:
        o.append(props.paper(s_x, s_y, 1.6, s_rot, 125, 160, 34, "sketch", s_pers, col="#f6d9a6"))
    # знак вопроса штрихами справа от головы
    if t > T_POM:
        qu = clamp((t - T_POM - .02) / .34)
        hop = -12 * math.exp(-6 * max(0, t - T_POM - .36)) * abs(math.sin(2 * math.pi * 2.2 * max(0, t - T_POM - .36)))
        o.append(f'<g transform="translate(175 {560 + hop:.1f}) rotate({6 * math.sin(t * 2.1):.2f})">'
                 f'{props.question_mark(0, 0, 1.9, qu, w=10)}</g>')
    cam = lib.cam(cx, cy, z, rot)
    return f'<g transform="{cam}">{"".join(o)}</g>'


FRAMES = {"s05": frame05}


def frame(sid, t):
    lib.dyn_begin()
    body = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#d9c9a8"/>{body}')
