"""Стол Димы рилса 30 (вид спереди, чуть сверху) и кот (агент C).
s05 (8.6–11.05): вечер, лампа; кот сидит на столе справа от открытого ноутбука (на экране — двадцать крошечных вкладок),
     смотрит в камеру, на «почему» (9.28) наклоняет голову; огонёк горит.
s17 (33.66–36.07): день, обед; ноутбук закрыт, на нём калачиком спит кот, огонёк тлеет; на «спит» (34.16) над ним
     выплывают «z»; Дима слева с кружкой, рядом тарелка с бутербродом, улыбается; камера едет к коту.
s18 (35.67–39.7): крупно кот на закрытом ноутбуке поднимает голову, смотрит в камеру и медленно моргает до конца."""
import math

import numpy as np

import cat
import dima
dima.BS = 0.70
import lib
from ink import fur
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad,
                 mix, rad_grad, rect_pts, shape, smooth, svg, T)
from parts import sausage

_ST = {}
DBK, DFR = 1150, 1400             # задний и передний край столешницы
WALL, WALL_SH = "#e9d3ad", "#d6bb8f"
T_WHY = 9.28
T_SLEEP = 34.16


# ═══════════════════════════════ комната
def room(day):
    s = []
    s.append(f'<rect x="-1500" y="-1500" width="4100" height="{DBK + 1500}" fill="{WALL}"/>')
    # обои: тонкие вертикальные полоски
    DEFS.append(f'<pattern id="pWall{int(day)}" width="70" height="70" patternUnits="userSpaceOnUse"><rect width="70" height="70" fill="{WALL}"/>'
                f'<rect x="0" width="6" height="70" fill="{WALL_SH}" opacity=".55"/><circle cx="35" cy="35" r="3" fill="{WALL_SH}" opacity=".7"/></pattern>')
    s.append(f'<rect x="-1500" y="-1500" width="4100" height="{DBK + 1500}" fill="url(#pWall{int(day)})"/>')
    # окно слева
    x0, x1, y0, y1 = 40, 520, 230, 960
    win = rect_pts(x0, y0, x1, y1, 10)
    if day:
        sky = lin_grad([(0, "#5aa6ea", 1), (1, "#bfe0f6", 1)], 0, 0, 0, 1)
        inner = f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>'
        g = rad_grad([(0, "#fff8d8", 1), (.3, "#fff1b0", .7), (1, "#fff1b0", 0)], 300, 260, 260, 260)
        inner += f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>'
        inner += shape(ellipse_pts(300, 270, 52, 52, 22), "#ffd84a", blob(ellipse_pts(312, 282, 44, 42, 16), "#f4b92e", .6), w=4, seed=3001)
        for k, (cx, cy, sc) in enumerate([(140, 450, 1.0), (440, 560, .8)]):
            pts = [(cx + 80 * sc * math.cos(a) * (1 + .2 * math.sin(5 * a + k)), cy + 30 * sc * math.sin(a) * (0.7 if math.sin(a) > 0 else 1))
                   for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)]
            inner += shape(pts, "#ffffff", blob(ellipse_pts(cx + 14 * sc, cy + 14 * sc, 64 * sc, 10 * sc, 10), "#d8e8f5"), w=3.4, seed=3002 + k)
        # дома и деревья напротив
        inner += blob([(x0 - 20, 800), (140, 780), (140, 700), (300, 700), (300, 760), (x1 + 20, 740), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)], "#c98f6a")
        for k, (x, y) in enumerate([(170, 730), (230, 730), (330, 790), (420, 790), (480, 790)]):
            inner += blob(rect_pts(x, y, x + 30, y + 40), "#8fc0e8")
        for k, (x, y, r) in enumerate([(90, 850, 70), (470, 870, 80)]):
            inner += shape(ellipse_pts(x, y, r, r * .9, 16), "#6aae5a", blob(ellipse_pts(x + 18, y + 18, r * .7, r * .6, 12), "#4d8f45", .9),
                           w=3.6, seed=3010 + k)
    else:
        sky = lin_grad([(0, "#18223f", 1), (1, "#3a4c78", 1)], 0, 0, 0, 1)
        inner = f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>'
        inner += blob(ellipse_pts(400, 340, 40, 40, 16), "#f3ead0") + blob(ellipse_pts(386, 328, 34, 34, 14), "#1e2a4a")
        for k, (x, y) in enumerate([(110, 300), (240, 420), (160, 560), (470, 500), (330, 260)]):
            inner += blob(ellipse_pts(x, y, 4, 4, 6), "#f3ead0")
        inner += blob([(x0 - 20, 760), (160, 740), (160, 660), (310, 660), (310, 720), (x1 + 20, 700), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)], "#141a30")
        for k, (x, y) in enumerate([(190, 690), (250, 690), (340, 750), (430, 750), (190, 800)]):
            inner += blob(rect_pts(x, y, x + 30, y + 40), "#f2c46a")
    inner += blob(rect_pts(272, y0, 290, y1), "#efe6d6") + blob(rect_pts(x0, 590, x1, 608), "#efe6d6")
    s.append(shape(win, "#efe6d6", inner, w=5, seed=3020))
    s.append(shape(rect_pts(x0 - 26, y1 - 6, x1 + 26, y1 + 30, 6), "#efe6d6", blob(rect_pts(x0 - 26, y1 + 18, x1 + 26, y1 + 30), "#d6cdb9"), w=4.4, seed=3021))
    # штора справа от окна
    cur = [(520, 180, 1), (640, 180, 1), (650, 500), (620, 820), (660, 1150, 1), (540, 1150, 1), (560, 820), (530, 500)]
    cin = "".join(line([(560 + k * 26, 190), (556 + k * 26 + 10 * math.sin(k), 1140)], 3, "#8f4a3a", seed=3030 + k, op=.7) for k in range(4))
    cin += blob([(610, 180), (650, 180), (660, 1150), (620, 1150)], "#9a4e3c", .6)
    s.append(shape(cur, "#c2654e", cin, w=4.4, seed=3031))
    s.append(shape(rect_pts(0, 160, 700, 182, 6), "#7a5236", "", w=3.6, seed=3032))
    # полка справа: книги, кактус в горшке, рамка с котиком-рисунком без букв
    s.append(shape(rect_pts(700, 560, 1100, 590, 4), "#a8794a", blob(rect_pts(700, 580, 1100, 590), "#8a5a36"), w=4.2, seed=3040))
    bx = 720
    for k, (w_, h_, c) in enumerate([(34, 150, "#3f6fb5"), (28, 130, "#e2543f"), (40, 162, "#3cbf63"), (30, 120, "#e8b23a"), (36, 146, "#7a4fb0")]):
        s.append(shape(rect_pts(bx, 560 - h_, bx + w_, 560), c, blob(rect_pts(bx + w_ * .6, 560 - h_, bx + w_, 560), lib.mul(c, (.8, .8, .85)), .9) +
                       blob(rect_pts(bx, 560 - h_ + 20, bx + w_, 560 - h_ + 30), "#f3ede1", .8), w=3.4, seed=3041 + k))
        bx += w_ + 2
    s.append(shape([(940, 560, 1), (1010, 560, 1), (1020, 490, 1), (930, 490, 1)], "#c4673f", blob([(985, 560), (1010, 560), (1020, 490), (990, 490)], "#9c4a2c", .8),
                   w=3.6, seed=3050))
    for k in range(5):
        a = -2.3 + k * 0.4
        s.append(line([(975, 490), (975 + 70 * math.cos(a), 490 + 90 * math.sin(a))], 16, "#5f9a5a", taper=.6, seed=3051 + k))
    s.append(shape(rect_pts(760, 300, 900, 420, 4), "#7a5236", blob(rect_pts(774, 314, 886, 406), "#fbf3e0") +
                   blob(ellipse_pts(830, 372, 30, 24, 12), "#3a3646") + blob([(806, 356), (812, 330), (822, 352)], "#3a3646") +
                   blob([(838, 352), (850, 330), (854, 356)], "#3a3646"), w=4, seed=3060))
    # плинтус у стола не виден; стена темнеет к столу
    g = lin_grad([(0, "#000000", 0), (1, "#3a2410", .22)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="{DBK - 260}" width="4100" height="260" fill="url(#{g})"/>')
    wall = "".join(s)
    s = []
    # стол
    top = "#c98f5a"
    tp = [(-1500, DBK, 1), (2600, DBK, 1), (2600, DFR, 1), (-1500, DFR, 1)]
    inner = "".join(line([(-1500, DBK + 50 + k * 60), (2600, DBK + 56 + k * 58)], 2.4, "#b27a48", taper=.1, wmin=.7, seed=3070 + k, op=.8)
                    for k in range(4))
    inner += blob(rect_pts(-1500, DBK, 2600, DBK + 18), "#a8723f", .6)
    s.append(shape(tp, top, inner, w=4.4, seed=3080))
    s.append(shape(rect_pts(-1500, DFR, 2600, DFR + 40), "#a8723f", blob(rect_pts(-1500, DFR + 26, 2600, DFR + 40), "#8a5a32"), w=4.6, seed=3081))
    s.append(f'<rect x="-1500" y="{DFR + 40}" width="4100" height="2000" fill="#6e4a2c"/>')
    s.append(blob(rect_pts(-1500, DFR + 40, 2600, DFR + 120), "#5a3b22", .8))
    return wall, "".join(s)


def light(day):
    if day:
        g = rad_grad([(0, "#fff2c0", .55), (.6, "#ffe6a0", .15), (1, "#ffe6a0", 0)], 300, 700, 1100, 1100)
        s = f'<rect x="-1500" y="-1500" width="4100" height="5000" fill="url(#{g})" style="mix-blend-mode:screen"/>'
        return s
    g = rad_grad([(0, "#ffd890", .55), (.5, "#ffbe6a", .2), (1, "#ffbe6a", 0)], 960, 820, 900, 900)
    s = f'<rect x="-1500" y="-1500" width="4100" height="5000" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    g2 = rad_grad([(0, "#000000", 0), (.55, "#000000", 0), (1, "#1a1030", .45)], 700, 1000, 1300, 1300)
    s += f'<rect x="-1500" y="-1500" width="4100" height="5000" fill="url(#{g2})"/>'
    return s


def lamp():
    """Настольная лампа-«луксор» сзади справа (вечер — горит)."""
    s = []
    bx, by = 1130, DBK + 40
    s.append(blob(ellipse_pts(bx, by + 6, 80, 14, 14), "#1a0e05", .35, blur(5)))
    s.append(shape(ellipse_pts(bx, by - 6, 70, 18, 16), "#2f5a6e", blob(ellipse_pts(bx + 14, by - 2, 56, 12, 12), "#22424f", .9), w=4, seed=3100))
    s.append(line([(bx, by - 14), (bx - 60, by - 260)], 16, "#2f5a6e", taper=.05, wmin=.9, seed=3101))
    s.append(line([(bx - 60, by - 260), (bx + 50, by - 420)], 14, "#2f5a6e", taper=.05, wmin=.9, seed=3102))
    s.append(shape(ellipse_pts(bx - 60, by - 260, 14, 14, 10), "#9aa3b2", "", w=3, seed=3103))
    hx, hy = bx + 50, by - 420
    shade_ = [(hx - 20, hy - 30), (hx + 40, hy - 50), (hx + 30, hy + 40, 1), (hx - 110, hy + 70, 1), (hx - 90, hy + 10)]
    s.append(shape(shade_, "#3f8a9e", blob([(hx + 40, hy - 50), (hx + 30, hy + 40), (hx - 20, hy + 46), (hx, hy - 30)], "#2f6a7e", .9), w=4.2, seed=3104))
    return "".join(s), (hx - 40, hy + 60)


def mug(x, y, sc, sd, steam_t=None):
    """Кружка (низ-центр x, y): горчичная с белым кружком, ручка справа, пар."""
    s = []
    s.append(blob(ellipse_pts(x + 6 * sc, y + 2, 54 * sc, 9 * sc, 12), "#1a0e05", .3, blur(4)))
    hd = [(x + 36 * sc, y - 90 * sc), (x + 72 * sc, y - 86 * sc), (x + 78 * sc, y - 52 * sc), (x + 40 * sc, y - 30 * sc)]
    s.append(line(hd, 13 * sc, INK, taper=.05, wmin=.95, seed=sd + 1))
    s.append(line(hd, 6 * sc, "#e8b23a", taper=.05, wmin=.95, seed=sd + 2))
    body = [(x - 46 * sc, y - 116 * sc, 1), (x + 46 * sc, y - 116 * sc, 1), (x + 42 * sc, y - 8 * sc), (x + 30 * sc, y, 1), (x - 30 * sc, y, 1), (x - 42 * sc, y - 8 * sc)]
    inner = blob([(x + 14 * sc, y - 120 * sc), (x + 50 * sc, y - 120 * sc), (x + 50 * sc, y), (x + 20 * sc, y)], "#c9922b", .9)
    inner += blob(ellipse_pts(x - 6 * sc, y - 62 * sc, 18 * sc, 18 * sc, 12), "#fbf3e0")
    s.append(shape(body, "#e8b23a", inner, w=4.2, seed=sd + 3))
    s.append(shape(ellipse_pts(x, y - 116 * sc, 46 * sc, 10 * sc, 16), "#6b3d22", blob(ellipse_pts(x + 6 * sc, y - 114 * sc, 36 * sc, 6 * sc, 12), "#8a5232"),
                   w=3.6, seed=sd + 4))
    if steam_t is not None:
        for k in range(2):
            ph = (steam_t * .5 + k * .5) % 1
            yy = y - 130 * sc - 120 * sc * ph
            a = 10 * sc * math.sin(steam_t * 2.5 + k * 2)
            r = math.sin(math.pi * ph)
            if r < .15:
                continue
            pts = [(x - 10 * sc + k * 20 * sc + a + 12 * sc * math.sin(u * 5 + steam_t * 2), yy + 70 * sc * u) for u in np.linspace(0, 1, 6)]
            s.append(line(pts, 7 * sc * r, "#ffffff", taper=.6, seed=sd + 10 + k))
    return "".join(s)


# ═══════════════════════════════ ноутбук
TAB_COL = ["#e2543f", "#3f6fb5", "#3cbf63", "#e8b23a", "#7a4fb0", "#2fa0a8", "#e07a9a"]


def laptop_open(cx, base_y, t):
    """Открытый ноутбук: клавиатура трапецией на столе (передний край base_y), экран стоит сзади, на нём 20 вкладок."""
    s = []
    s.append(blob(ellipse_pts(cx + 10, base_y + 6, 270, 22, 16), "#1a0e05", .35, blur(6)))
    # экран (за клавиатурой)
    sx0, sx1, sy0, sy1 = cx - 230, cx + 230, base_y - 470, base_y - 120
    scr = [(sx0, sy0, 1), (sx1, sy0, 1), (sx1 + 6, sy1, 1), (sx0 - 6, sy1, 1)]
    ix0, ix1, iy0, iy1 = sx0 + 20, sx1 - 20, sy0 + 20, sy1 - 18
    inner = blob(rect_pts(ix0, iy0, ix1, iy1), "#eef3fb")
    # полоса вкладок: 20 крошечных вкладок со значками
    inner += blob(rect_pts(ix0, iy0, ix1, iy0 + 38), "#c9d3e6")
    n = 20
    tw = (ix1 - ix0 - 8) / n
    act = int(t * 2.2) % n
    for k in range(n):
        x = ix0 + 4 + k * tw
        col = "#ffffff" if k == act else "#dde4f2"
        inner += f'<rect x="{f(x)}" y="{f(iy0 + 8)}" width="{f(tw - 2)}" height="30" rx="5" fill="{col}" stroke="#8e98b0" stroke-width="1.4"/>'
        inner += f'<rect x="{f(x + tw / 2 - 6)}" y="{f(iy0 + 15)}" width="10" height="10" rx="2" fill="{TAB_COL[k % 7]}"/>'
    # страница: блоки-«строки» и картинка (без букв)
    inner += blob(rect_pts(ix0, iy0 + 38, ix1, iy0 + 62), "#ffffff")
    inner += f'<rect x="{f(ix0 + 40)}" y="{f(iy0 + 44)}" width="{f(ix1 - ix0 - 80)}" height="12" rx="6" fill="#dfe5ef"/>'
    inner += blob(rect_pts(ix0 + 30, iy0 + 90, ix0 + 190, iy0 + 210, 8), mix("#9fd0f2", TAB_COL[act % 7], .35))
    for k in range(6):
        w_ = (ix1 - ix0 - 260) * (1 - .15 * (k % 3))
        inner += f'<rect x="{f(ix0 + 210)}" y="{f(iy0 + 96 + k * 24)}" width="{f(w_)}" height="10" rx="5" fill="#b9c3d6"/>'
    inner += blob([(ix0, iy0), (ix0 + 160, iy0), (ix0, iy0 + 200)], "#ffffff", .35)
    s.append(shape(scr, "#2b2f3a", f'<g>{inner}</g>', w=4.6, seed=3200))
    # петля и клавиатура
    kb = [(cx - 236, base_y - 120, 1), (cx + 236, base_y - 120, 1), (cx + 290, base_y - 14, 1), (cx - 290, base_y - 14, 1)]
    kin = blob([(cx + 120, base_y - 120), (cx + 236, base_y - 120), (cx + 290, base_y - 14), (cx + 150, base_y - 14)], "#a6adbb", .8)
    for r in range(4):
        v = (r + .5) / 5.5
        y = base_y - 112 + 82 * v
        hw = 220 + 50 * v
        nk = 13
        for k in range(nk):
            x = cx - hw * .9 + (2 * hw * .9) * (k + .1) / nk
            kin += f'<rect x="{f(x)}" y="{f(y)}" width="{f(hw * 1.6 / nk * .82)}" height="12" rx="2" fill="#3a3f4c"/>'
    kin += blob([(cx - 60, base_y - 36), (cx + 60, base_y - 36), (cx + 66, base_y - 18), (cx - 66, base_y - 18)], "#b9bfcc")
    s.append(shape(kb, "#c9ced8", kin, w=4.2, seed=3201))
    s.append(shape([(cx - 290, base_y - 14, 1), (cx + 290, base_y - 14, 1), (cx + 284, base_y, 1), (cx - 284, base_y, 1)], "#8e95a5", "", w=3.8, seed=3202))
    return "".join(s), ((sx0 + sx1) / 2, (sy0 + sy1) / 2)


def laptop_closed(cx, base_y):
    """Закрытый ноутбук: крышка сверху трапецией (передний край base_y - 18), кромка 18 px."""
    s = []
    s.append(blob(ellipse_pts(cx + 10, base_y + 4, 300, 22, 16), "#1a0e05", .4, blur(6)))
    lid = [(cx - 250, base_y - 150, 1), (cx + 250, base_y - 150, 1), (cx + 300, base_y - 18, 1), (cx - 300, base_y - 18, 1)]
    inner = blob([(cx + 120, base_y - 150), (cx + 250, base_y - 150), (cx + 300, base_y - 18), (cx + 150, base_y - 18)], "#a6adbb", .7)
    inner += blob([(cx - 230, base_y - 146), (cx - 120, base_y - 146), (cx - 220, base_y - 30), (cx - 280, base_y - 30)], "#e6e9f0", .7)
    inner += shape(ellipse_pts(cx, base_y - 86, 22, 12, 14), "#b9bfcc", "", w=2.4, seed=3210)
    s.append(shape(lid, "#c9ced8", inner, w=4.4, seed=3211))
    s.append(shape([(cx - 300, base_y - 18, 1), (cx + 300, base_y - 18, 1), (cx + 294, base_y, 1), (cx - 294, base_y, 1)], "#8e95a5",
                   line([(cx - 250, base_y - 9), (cx + 250, base_y - 9)], 2, "#6d737e", seed=3212, taper=.1, wmin=.8), w=3.8, seed=3213))
    return "".join(s)


def plate(x, y, sd):
    """Тарелка с бутербродом (один укус)."""
    s = [blob(ellipse_pts(x + 6, y + 6, 120, 20, 16), "#1a0e05", .3, blur(4))]
    s.append(shape(ellipse_pts(x, y, 120, 30, 20), "#f6f3ec", blob(ellipse_pts(x + 10, y + 2, 84, 18, 16), "#e2dccb"), w=4, seed=sd))
    bread = [(x - 76, y - 4), (x - 70, y - 40), (x - 20, y - 52), (x + 12, y - 50), (x + 22, y - 62, 1), (x + 34, y - 46), (x + 46, y - 60, 1),
             (x + 60, y - 42), (x + 74, y - 34), (x + 76, y - 4)]
    s.append(shape(T(bread, 0, 6), "#d9a25a", "", w=3.6, seed=sd + 1))
    s.append(shape([(x - 82, y - 14), (x + 82, y - 18), (x + 76, y - 4), (x - 76, y - 2)], "#6aae5a", "", w=3, seed=sd + 2))
    s.append(shape([(x - 74, y - 22), (x + 74, y - 26), (x + 70, y - 16), (x - 72, y - 14)], "#e2543f", "", w=3, seed=sd + 3))
    s.append(shape(T(bread, 0, -18), "#e8b46a", blob(T([(x - 70, y - 40), (x - 20, y - 52), (x - 10, y - 40), (x - 60, y - 30)], 0, -18), "#f3cf8a", .9),
                   w=3.6, seed=sd + 4))
    return "".join(s)


# ═══════════════════════════════ спящий кот (тело калачиком; голова — из cat.py)
CAT_C, CAT_SH, CAT_FUR, CAT_EDGE = cat.CAT, cat.CAT_SH, cat.CAT_FUR, cat.CAT_EDGE


def curl_body():
    """Тело лежит калачиком (внутр. коорд. кота, низ — y=1306): холмик шире головы, бедро справа."""
    s = []
    body = [(668, 1306, 1), (666, 1250), (702, 1190), (780, 1152), (870, 1140), (956, 1150), (1016, 1190), (1040, 1250), (1034, 1306, 1)]
    bp = fur(body, 7, 7, seed=31)
    inner = blob([(930, 1140), (1050, 1190), (1060, 1310), (950, 1310), (970, 1220)], CAT_SH, .9)
    inner += blob([(720, 1176), (860, 1150), (900, 1170), (800, 1200), (700, 1230)], CAT_FUR, .55)
    inner += blob(ellipse_pts(970, 1240, 60, 48, 14, rot=-20), CAT_SH, .5)
    for i, st in enumerate([[(760, 1196), (772, 1212)], [(820, 1178), (830, 1196)], [(900, 1168), (906, 1186)], [(960, 1182), (962, 1200)],
                            [(860, 1216), (868, 1232)]]):
        inner += line(st, 2.2, CAT_EDGE, seed=320 + i, op=.85)
    s.append(shape(bp, CAT_C, inner, w=5, seed=330))
    # бедро задней лапы
    s.append(line([(910, 1300), (918, 1242), (962, 1208), (1012, 1214)], 4.4, seed=331, taper=.3, wmin=.3))
    return "".join(s)


def curl_paws():
    """Передние лапы поджаты вперёд под подбородок (верх лап с пальчиками)."""
    s = []
    for k, (px, sd) in enumerate([(752, 340), (850, 343)]):
        foot = ellipse_pts(px, 1290, 44, 24, 14)
        s.append(shape(foot, CAT_C, blob(ellipse_pts(px + 10, 1298, 32, 14, 10), CAT_SH, .6), w=4.6, seed=sd))
        for j in (-14, 0, 14):
            s.append(line([(px + j, 1300), (px + j, 1312)], 2.2, seed=sd + 5 + j))
    return "".join(s)


TAIL_C = [(1030, 1288), (980, 1318), (880, 1328), (760, 1326), (660, 1316), (590, 1294), (556, 1256), (560, 1216)]


def curl_tail():
    S = lib.sample(TAIL_C, False, 3.0)
    n = len(S)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True)
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = 44 + (16 - 44) * np.linspace(0, 1, n) ** 1.3
    L, R = S + N * Wd[:, None] / 2, S - N * Wd[:, None] / 2
    tip = S[-1] + Tg[-1] * Wd[-1] * .45
    outline = [tuple(p) for p in L] + [tuple(tip)] + [tuple(p) for p in R[::-1]]
    sh = blob([(600, 1306), (1100, 1306), (1100, 1360), (600, 1360)], CAT_SH, .85)
    out = [f'<path d="{lib.fill_d(outline)}" fill="{CAT_C}"/>']
    c = lib.clip_of(outline)
    out.append(f'<g clip-path="url(#{c})">{sh}</g>')
    out.append(f'<path d="{lib.ink_closed(outline, 4.8, seed=350)}" fill="{INK}"/>')
    for i, k in enumerate(range(int(n * .1), int(n * .85), int(n * .13))):
        p = S[k] + N[k] * Wd[k] * .2
        q = p + Tg[k] * 12
        out.append(line([tuple(p), tuple(q)], 2, CAT_EDGE, seed=351 + i, op=.8))
    return "".join(out), (float(tip[0]), float(tip[1]))


def flame(t, bx, by, k, glow):
    """Огонёк на кончике хвоста: k — размер (тлеет 0.5, горит 1.2), glow 0..1 — от тлеющего красного к жёлтому."""
    w1 = 4 * math.sin(t * 23) + 3 * math.sin(t * 37 + 1)
    w2 = 5 * math.sin(t * 29 + 2)
    w3 = 3 * math.sin(t * 17 + .5)
    P = [(-20, 4), (-24, -16), (-15 + w3 * .3, -36 + w2 * .3), (-13 + w1 * .4, -56), (-4, -45), (2 + w1, -82 + w2, 1), (11, -52),
         (20 + w2 * .6, -64 + w1 * .5, 1), (24, -36), (22, -11), (15, 4), (0, 9)]

    def tf(q, kk=k):
        return (bx + q[0] * kk, by + q[1] * kk) + ((1,) if len(q) > 2 else ())
    outer = mix("#c9502a", "#ff8a2a", glow)
    core = mix("#e8783a", "#ffbe55", glow)
    o = shape([tf(q) for q in P], outer, blob([tf((q[0] * .7, q[1] * .7 + 2) + q[2:]) for q in P], core), w=3.4, seed=233, ink_color="#7a2a10", var=.2)
    o += blob([tf(q) for q in [(-7, 2), (-5, -19), (2 + w1 * .3, -37), (7, -18), (5, 2)]], mix("#ffb070", "#fff2c0", glow))
    return o


def head_group(t, look, blink, flick=0.0):
    st = cat.static_parts()
    return st["head"] + cat.ears(flick) + st["face"] + cat.eyes(look, blink) + cat.whiskers(t)


def sleepy_cat(x, y, s, t, lift, look=(0, 0), blink=1.0, flick=0.0, flame_k=0.55, glow=0.0, ears_up=0.0):
    """Кот калачиком: низ (836, 1306) → (x, y), масштаб s. lift 0 — голова лежит на лапах, 1 — поднята, смотрит."""
    br = 0.5 + 0.5 * math.sin(t * 2 * math.pi / (3.4 - 0.9 * lift))
    sy = 1 + (0.028 - 0.016 * lift) * br
    o = [blob(ellipse_pts(860, 1306, 250, 20, 16), "#1a0e05", .35, blur(8))]
    if "curl" not in _ST:
        _ST["curl"] = curl_body()
        _ST["paws"] = curl_paws()
        _ST["tail"] = curl_tail()
    o.append(f'<g transform="translate(0 1306) scale(1 {sy:.4f}) translate(0 -1306)">{_ST["curl"]}</g>')
    tl, tip = _ST["tail"]
    o.append(tl)
    # голова: лежит (сдвиг вниз-влево, наклон) → поднята
    dx = -40 + 10 * lift
    dy = 150 - 108 * lift - (sy - 1) * 120
    tilt = -9 * (1 - lift) + 2.5 * lift * math.sin(t * .9)
    o.append(f'<g transform="translate({dx:.2f} {dy:.2f}) rotate({tilt:.2f} 836 1146)">{head_group(t, look, blink, flick)}</g>')
    o.append(_ST["paws"])
    o.append(flame(t, tip[0] - 2, tip[1] + 6, flame_k, glow))
    return f'<g transform="translate({x - 836 * s:.2f} {y - 1306 * s:.2f}) scale({s:.4f})">{"".join(o)}</g>', (836 + dx, 1068 + dy)


def zzz(t, x, y, s):
    """«z» выплывают по очереди от головы вверх-вправо, растут и сходят в ноль (без полупрозрачности)."""
    o = []
    for k in range(4):
        e = t - (T_SLEEP + k * 0.55)
        if e < 0 or e > 1.7:
            continue
        ph = e / 1.7
        base = (17 + 7 * (k % 3)) * s
        sz = base * min(1.0, back_out(clamp(ph / .22), 2.0)) * (1 - smooth(.75, 1.0, ph))
        if sz < 2.5:
            continue
        cx = x + (30 + 120 * ph) * s + 14 * s * math.sin(e * 3.2 + k)
        cy = y - (20 + 280 * ph) * s
        z = [(cx - sz, cy - sz, 1), (cx + sz, cy - sz, 1), (cx - sz, cy + sz, 1), (cx + sz, cy + sz, 1)]
        q = sz / base
        o.append(line(z, (12 * q + 1.5) * s, INK, taper=.1, wmin=.8, seed=380 + k))
        o.append(line(z, (5.5 * q + .5) * s, "#9fd84a", taper=.1, wmin=.8, seed=380 + k))
    return "".join(o)


# ═══════════════════════════════ Дима (s17): сидит за столом слева, кружка в ближней руке, улыбается
def dima_s17(t):
    hip = (215.0, 1330.0)
    lean = 0.12 + 0.02 * math.sin(t * 1.3)
    sip = smooth(34.5, 34.9, t) * (1 - smooth(35.3, 35.7, t))
    wr = (395 + 6 * math.sin(t * 1.1), 1200 - 40 * sip)
    pose = {"hip": hip, "lean": lean,
            "feet": {"n": ((330, 1800), 0.0), "f": ((300, 1800), 0.0)},
            "arms": {"f": ("ang", 0.25, 0.6), "n": ("ik", wr, -1)},
            "split": True,
            "hands": {"f": "fist", "n": "fist"},
            "hand_dir": {"n": (1.0, -0.25)},
            "head_ang": 0.12 + 0.05 * math.sin(t * .9),
            "expr": {"lid": 0.86, "look": (0.7, 0.35), "brows": "calm", "mouth": "smile"},
            "held_side": "n",
            "held": ("behind", lambda Wr, d: f'<g transform="translate({Wr[0] + d[0] * 45 + 100:.1f} {Wr[1] + d[1] * 45 + 95:.1f}) scale(-1.6 1.6)">{mug(0, 0, 1.0, 3300, t)}</g>')}
    return dima.draw(pose)


def draw_room(day, part=None):
    key = "room1" if day else "room0"
    if key not in _ST:
        _ST[key] = room(day)
        _ST["light1" if day else "light0"] = light(day)
    w, d = _ST[key]
    return w if part == "wall" else d if part == "desk" else w + d


# ═══════════════════════════════ кадры
CAT5 = (735, 1330, 1.22)


def s05(t):
    s = [draw_room(False)]
    lp, lc = lamp()
    s.append(lp)
    lt, sc_c = laptop_open(330, 1352, t)
    # свет экрана на стену
    g = rad_grad([(0, "#bfe0ff", .35), (1, "#bfe0ff", 0)], sc_c[0], sc_c[1], 420, 360)
    s.append(f'<rect x="{f(sc_c[0] - 440)}" y="{f(sc_c[1] - 380)}" width="880" height="760" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(lt)
    s.append(mug(960, 1300, 0.8, 3400, t))
    s.append(_ST["light0"])
    x, y, sc = CAT5
    # кот: смотрит в камеру; «Знаешь» — ухо и взгляд; «почему» — наклон головы с пружиной
    e = t - T_WHY
    tilt = -1.5 + 1.0 * math.sin(t * 1.4)
    if e > -0.08:
        u = e + 0.08
        tilt += 11 * (1 - math.exp(-u * 7) * math.cos(u * 13)) * (1 - smooth(10.55, 11.0, t) * .35)
    look = (0.06 * math.sin(t * .8), -0.05 + 0.08 * smooth(T_WHY, T_WHY + .3, t))
    blink = 0.0
    for c, half, hold in ((8.78, 0.06, 0.0), (10.35, 0.1, 0.04)):
        a = c - half
        if a <= t <= c + hold + half:
            blink = ease_io((t - a) / half) if t < c else (1.0 if t < c + hold else 1 - ease_io((t - c - hold) / half))
    flick = 0.0
    for c in (8.96, 9.32):
        q = t - c
        if 0 <= q < 0.5:
            flick += -14 * math.exp(-q * 9) * math.sin(q * 34)
    tail = 6 * math.sin(t * 2.1) + 3 * math.sin(t * 3.7 + 1)
    fx, fy = cat.flame_world(x, y, sc, tail)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g = rad_grad([(0, "#ffb050", .38 * fl), (1, "#ffb050", 0)], fx, fy, 320, 320)
    s.append(f'<rect x="{f(fx - 340)}" y="{f(fy - 340)}" width="680" height="680" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(cat.draw(x, y, sc, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick))
    u = clamp((t - 8.6) / 2.45)
    hc = cat.to_world((836, 1100), x, y, sc)
    cx = hc[0] + 25 + 20 * ease_io(u)
    cy = hc[1] + 100 - 15 * u
    scc = 2.0 + 0.16 * (0.4 * u + 0.6 * ease_io(u))
    if e > 0:
        scc *= 1 + 0.035 * math.exp(-e * 6) * math.sin(min(e * 10, math.pi))
    rot = 1.2 - 1.8 * u
    return "".join(s), cam(cx, cy, scc, rot), "#1e2440"


CAT17 = (760, 1300, 0.74)


def s17_18(sid, t):
    s = [draw_room(True, "wall")]
    if sid == "s17":
        body, arm = dima_s17(t)
        s.append(body)
    s.append(draw_room(True, "desk"))
    s.append(plate(400, 1368, 3500))
    if sid == "s17":
        s.append(arm)
    s.append(laptop_closed(745, 1330))
    x, y, sc = CAT17
    if sid == "s17":
        lift, look, blink, glow, fk = 0.0, (0, 0), 1.0, 0.0, 0.5 + 0.06 * math.sin(t * 3)
        flick = -10 * math.exp(-(t - 35.1) * 8) * math.sin((t - 35.1) * 34) if 35.1 <= t < 35.6 else 0.0
    else:
        # просыпается: голова поднимается 35.95–36.45, глаза открываются 36.3–36.5, огонёк разгорается; медленные моргания
        lift = ease_io(clamp((t - 35.95) / 0.5)) + 0.06 * math.exp(-max(t - 36.45, 0) * 6) * math.sin(max(t - 36.45, 0) * 14) * (t > 36.45)
        blink = 1 - ease_io(clamp((t - 36.25) / 0.25))
        for c, half, hold in ((37.55, 0.4, 0.3), (38.95, 0.4, 0.2)):
            a = c - half
            if a <= t <= c + hold + half:
                blink = ease_io((t - a) / half) if t < c else (1.0 if t < c + hold else 1 - ease_io((t - c - hold) / half))
        look = (0.04 * math.sin(t * .7), 0.0)
        glow = smooth(36.0, 36.6, t)
        fk = 0.5 + 0.55 * back_out(clamp((t - 36.05) / 0.5), 1.6) + 0.04 * math.sin(t * 3)
        flick = 0.0
        for c in (36.4, 38.5):
            q = t - c
            if 0 <= q < 0.5:
                flick += -14 * math.exp(-q * 9) * math.sin(q * 34)
    # тёплый отсвет огонька
    tip = _ST.get("tail", (None, (640, 1224)))[1]
    fx, fy = x + (tip[0] - 836) * sc, y + (tip[1] - 1306 - 30) * sc
    g = rad_grad([(0, "#ffb050", .18 + .25 * glow), (1, "#ffb050", 0)], fx, fy, 220, 220)
    s.append(f'<rect x="{f(fx - 240)}" y="{f(fy - 240)}" width="480" height="480" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    ct, hc = sleepy_cat(x, y, sc, t, lift, look, blink, flick, fk, glow)
    s.append(ct)
    hx, hy = x + (hc[0] - 836) * sc, y + (hc[1] - 1306) * sc
    if sid == "s17":
        s.append(zzz(t, hx + 95 * sc, hy - 120 * sc, 1.0))
    s.append(_ST["light1"])
    if sid == "s17":
        u = clamp((t - 33.66) / 2.41)
        k = ease_io(u)
        cx = 545 + (hx + 30 - 545) * k
        cy = 1110 + (hy + 120 - 1110) * k
        scc = 1.3 + (2.35 - 1.3) * (0.3 * u + 0.7 * k)
        rot = -0.8 + 1.2 * u
    else:
        u = clamp((t - 35.67) / 4.03)
        hy1 = y + (1068 + 150 - 108 - 1306) * sc
        hx1 = x + (836 - 30 - 836) * sc
        up = ease_io(clamp((t - 35.9) / 0.7))
        cx = hx1 - 35 - 10 * u
        cy = hy1 + 150 - 45 * up - 10 * u
        scc = 2.45 + 0.3 * (0.4 * u + 0.6 * ease_io(u))
        rot = 0.9 - 1.4 * u
    return "".join(s), cam(cx, cy, scc, rot), WALL


def frame(sid, t):
    if "static" not in _ST:
        cat.static_parts()
        draw_room(False)
        draw_room(True)
        curl_tail_ = curl_tail()
        _ST["curl"], _ST["paws"], _ST["tail"] = curl_body(), curl_paws(), curl_tail_
        lib.static_done()
        _ST["static"] = 1
    lib.dyn_begin()
    if sid == "s05":
        art, cm, bg = s05(t)
    else:
        art, cm, bg = s17_18(sid, t)
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cm}">{art}</g>')
