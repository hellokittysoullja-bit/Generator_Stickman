"""Кирпичный корпус университета из рилса 24 (scene_diaries.building), перекрашенный в ночь автоматически
(каждый цвет × (0.50, 0.54, 0.78)); стёкла тёмные — свет в окнах кладёт сцена study поверх. Сгенерировано из кода рилса 24."""
import math

import numpy as np

from lib import DEFS, INK, blob, blur, ellipse_pts, line, rect_pts, shape

BRICK, BRICK_SH, BRICK_DK, TRIM = "#5a2c2d", "#482022", "#371819", "#7a80b0"
COVERS = ["#183b8d", "#205348", "#642831", "#6c582c", "#3d2b89", "#164d76", "#70422d", "#25316d"]

# ═══════════════════════════════ s10
GX0, GX1, GTOP, GBASE = 30, 650, 560, 1080       # фасад
WIN_ROWS = [(640, 740), (820, 920)]
WIN_X = [80, 175, 485, 580]
PX0, PX1 = 268, 412                               # портик
STX, SBASE, LH = 845, 1290, 17.0                  # стопка: центр, низ, толщина одного дневника
N0 = 14


def brick_defs():
    DEFS.append(f'<pattern id="pBrick" width="64" height="32" patternUnits="userSpaceOnUse">'
                f'<rect width="64" height="32" fill="{BRICK}"/>'
                f'<path d="M0 15.5H64M0 31.5H64M20 0V15.5M52 16V32" stroke="{BRICK_SH}" stroke-width="2.4"/>'
                f'<rect x="4" y="3" width="12" height="4" fill="#63393e" opacity=".7"/><rect x="36" y="19" width="10" height="4" fill="#63393e" opacity=".6"/>'
                f'</pattern>')


def window(x, y0, y1, open_=False, seed=0):
    w = 62
    s = []
    fr = rect_pts(x - w / 2 - 8, y0 - 8, x + w / 2 + 8, y1 + 8)
    s.append(shape(fr, TRIM, "", w=3.6, seed=seed))
    glass = rect_pts(x - w / 2, y0, x + w / 2, y1)
    if open_:
        inner = blob(rect_pts(x - w / 2, y0, x + w / 2, y1), "#15122c") + blob(rect_pts(x - w / 2, y0, x + w / 2, y0 + 30), "#221d3e")
        s.append(shape(glass, "#15122c", inner, w=3.2, seed=seed + 1))
        # распахнутая створка
        s.append(shape([(x + w / 2, y0, 1), (x + w / 2 + 26, y0 + 10, 1), (x + w / 2 + 26, y1 - 6, 1), (x + w / 2, y1, 1)], "#4e6bb8",
                       line([(x + w / 2 + 8, y0 + 18), (x + w / 2 + 8, y1 - 18)], 4, "#808ac7", seed=seed + 3, op=.7), w=3, seed=seed + 2))
    else:
        inner = blob(rect_pts(x - w / 2, y0, x + w / 2, y1), "#3a3f62") + \
            blob([(x - w / 2, y0 + 40), (x + w / 2, y0 + 8), (x + w / 2, y0 + 30), (x - w / 2, y0 + 62)], "#565c86", .8)
        s.append(shape(glass, "#3a3f62", inner, w=3.2, seed=seed + 1))
        s.append(line([(x, y0), (x, y1)], 3.2, TRIM, taper=.1, wmin=.9, seed=seed + 4))
        s.append(line([(x - w / 2, (y0 + y1) / 2), (x + w / 2, (y0 + y1) / 2)], 3.2, TRIM, taper=.1, wmin=.9, seed=seed + 5))
    # подоконник и замковый камень
    s.append(shape(rect_pts(x - w / 2 - 14, y1 + 8, x + w / 2 + 14, y1 + 20), TRIM, "", w=3, seed=seed + 6))
    s.append(shape([(x - 12, y0 - 22, 1), (x + 12, y0 - 22, 1), (x + 8, y0 - 6, 1), (x - 8, y0 - 6, 1)], TRIM, "", w=2.6, seed=seed + 7))
    return "".join(s)


OPEN_WIN = []


def building():
    s = []
    # тень на газоне
    s.append(blob([(GX0 + 20, GBASE), (GX1 + 60, GBASE), (GX1 + 140, GBASE + 46), (GX0 + 60, GBASE + 46)], "#1e422a", .6, blur(6)))
    # крыша
    roof = [(GX0 - 16, GTOP), (GX0 + 60, GTOP - 80), (GX1 - 60, GTOP - 80), (GX1 + 16, GTOP)]
    s.append(shape(roof, "#252b4d", blob([(GX0 + 60, GTOP - 80), (GX1 - 60, GTOP - 80), (GX1 - 50, GTOP - 66), (GX0 + 50, GTOP - 66)], "#353c6a") +
                   "".join(line([(GX0 + 40 + k * 60, GTOP - 4), (GX0 + 70 + k * 60, GTOP - 76)], 2.4, "#1b1f3b", seed=700 + k, op=.8) for k in range(10)),
                   w=4.6, seed=31))
    # трубы
    for x in (110, 570):
        s.append(shape(rect_pts(x - 18, GTOP - 120, x + 18, GTOP - 60), BRICK, blob(rect_pts(x + 4, GTOP - 120, x + 18, GTOP - 60), BRICK_SH),
                       w=3.6, seed=32 + x))
        s.append(shape(rect_pts(x - 24, GTOP - 130, x + 24, GTOP - 116), TRIM, "", w=3, seed=34 + x))
    # фасад кирпичом
    fac = rect_pts(GX0, GTOP, GX1, GBASE)
    inner = f'<rect x="{GX0}" y="{GTOP}" width="{GX1 - GX0}" height="{GBASE - GTOP}" fill="url(#pBrick)"/>'
    inner += blob([(GX1 - 70, GTOP), (GX1, GTOP), (GX1, GBASE), (GX1 - 40, GBASE)], BRICK_DK, .35)
    inner += blob(rect_pts(GX0, GTOP, GX1, GTOP + 26), BRICK_DK, .45)
    s.append(shape(fac, BRICK, inner, w=5, seed=35))
    # белые пояса и карниз
    s.append(shape(rect_pts(GX0 - 18, GTOP - 10, GX1 + 18, GTOP + 14), TRIM, blob(rect_pts(GX0 - 18, GTOP + 6, GX1 + 18, GTOP + 14), "#686b8c"), w=4, seed=36))
    s.append(shape(rect_pts(GX0 - 6, 776, GX1 + 6, 790), TRIM, "", w=3.2, seed=37))
    s.append(shape(rect_pts(GX0 - 10, GBASE - 40, GX1 + 10, GBASE), "#6c7093", blob(rect_pts(GX0 - 10, GBASE - 14, GX1 + 10, GBASE), "#5c5e77"), w=4, seed=38))
    # окна
    k = 0
    for (y0, y1) in WIN_ROWS:
        for x in WIN_X:
            op = any(abs(ox - x) < 2 and abs(oy - y0) < 2 for ox, oy, _ in OPEN_WIN)
            s.append(window(x, y0, y1, op, seed=800 + k * 10))
            k += 1
    # портик: фронтон, колонны, дверь
    s.append(shape([(PX0 - 30, GTOP + 70), (340, GTOP - 10), (PX1 + 30, GTOP + 70)], TRIM,
                   blob([(PX0 + 10, GTOP + 60), (340, GTOP + 16), (PX1 - 10, GTOP + 60)], "#7277a0"), w=4.4, seed=40))
    s.append(shape(rect_pts(PX0 - 30, GTOP + 70, PX1 + 30, GTOP + 92), TRIM, "", w=4, seed=41))
    s.append(shape(rect_pts(PX0 - 10, GTOP + 92, PX1 + 10, GBASE - 40), "#512625", blob(rect_pts(PX0 - 10, GTOP + 92, PX1 + 10, GTOP + 130), "#3d1c1c", .8), w=3.6, seed=42))
    s.append(window(340, 640, 740, False, seed=880))
    door = [(310, GBASE - 40, 1), (310, 860), (340, 832), (370, 860), (370, GBASE - 40, 1)]
    s.append(shape([(312, 820, 1), (368, 820, 1), (368, 920, 1), (312, 920, 1)], BRICK, "", ink=False))
    s.append(shape(door, "#2d1d1c", blob([(340, 832), (370, 860), (370, GBASE - 40), (348, GBASE - 40)], "#201313") +
                   line([(340, 840), (340, GBASE - 44)], 2.6, "#150c0b", seed=43), w=3.6, seed=44))
    for x in (PX0 - 2, PX0 + 34, PX1 - 34, PX1 + 2):
        col = rect_pts(x - 12, GTOP + 92, x + 12, GBASE - 40)
        s.append(shape(col, TRIM, blob(rect_pts(x + 3, GTOP + 92, x + 12, GBASE - 40), "#6a6e90") +
                       line([(x - 4, GTOP + 100), (x - 4, GBASE - 48)], 2, "#686b8c", seed=45 + x), w=3.4, seed=46 + x))
        s.append(shape(rect_pts(x - 17, GTOP + 88, x + 17, GTOP + 100), TRIM, "", w=3, seed=47 + x))
        s.append(shape(rect_pts(x - 17, GBASE - 52, x + 17, GBASE - 40), TRIM, "", w=3, seed=48 + x))
    # ступени
    for j in range(3):
        s.append(shape(rect_pts(PX0 - 40 - j * 12, GBASE - 40 + j * 14, PX1 + 40 + j * 12, GBASE - 26 + j * 14), "#767ba5", "", w=3.2, seed=49 + j))
    # башенка
    s.append(shape(rect_pts(290, 400, 390, GTOP - 10), TRIM, blob(rect_pts(360, 400, 390, GTOP - 10), "#6b6f90"), w=4.4, seed=50))
    s.append(shape([(304, 400, 1), (304, 352), (340, 316), (376, 352), (376, 400, 1)], "#1e2345", "", w=3.4, seed=51))  # арка-проём
    s.append(shape(rect_pts(280, 392, 400, 408), TRIM, "", w=3.4, seed=52))
    s.append(shape(rect_pts(296, 300, 384, 316), TRIM, "", w=3.4, seed=53))
    s.append(shape([(300, 300, 1), (340, 190, 1), (380, 300, 1)], "#252b4d", blob([(340, 190), (380, 300), (350, 300)], "#1a1e3a"), w=4, seed=54))
    s.append(shape(ellipse_pts(340, 186, 8, 8, 10), "#746946", "", w=2.6, seed=55))
    return "".join(s)


