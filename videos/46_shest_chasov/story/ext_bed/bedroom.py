"""Комната Димы утром (сцена bed рилса 37): стена с узором и окно на утренний город (den.py рилса 33, время суток
morning), постер, диван-кровать (вид спереди: спинка с подушками, подлокотники, разложенное сиденье с простынёй),
тумбочка с будильником слева, пол с ковром, угол комнаты справа (x = CORNER_X), потолок с карнизом.

Мир (px): пол y = FLOOR_Y = 1330, верх сиденья MAT_T = 1112, Дима лежит головой влево на подушке (голова H_HEAD).
Каждая функция возвращает SVG в мировых координатах; камера — снаружи (scene.py). Манера — как у 26–33: живая тушь
(ink.py), плоский цвет с одной тенью, свет слоями.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import den  # noqa: E402
import lib  # noqa: E402
import room  # noqa: E402
from lib import INK, blob, ellipse_pts, line, mix, rect_pts, shape  # noqa: E402

FLOOR_Y = 1330.0
CORNER_X = 1330.0
CEIL_Y = -260.0
NS = (52.0, 230.0, 1046.0)            # тумбочка: x0, x1, верх
ALARM = (196.0, 48.0)                  # будильник на тумбочке: cx, size
SOFA_X0, SOFA_X1 = 236.0, 1196.0
MAT_T, MAT_F = 1112.0, 1150.0          # сиденье: задний край, передний край верхней плоскости
SOFA, SOFA_SH, SOFA_HI, SOFA_DK = "#8f7aa6", "#6f5b86", "#a894bd", "#463653"   # как край дивана в сцене clock
SHEET, SHEET_SH = "#e9eef2", "#c6d0d9"
WOOD, WOOD_SH, WOOD_HI = "#b5794a", "#8e5a34", "#d39a68"            # тумбочка — как в сцене clock
WALL_SIDE, WALL_SIDE_SH = "#7d95a2", "#6b8390"


def setup():
    den.set_tod("morning")
    den.WIN = (600.0, 250.0, 960.0, 770.0)


def ceiling():
    s = [blob(rect_pts(-900, -1400, 2800, CEIL_Y), "#d9d2c4")]
    s.append(shape(rect_pts(-900, CEIL_Y - 6, 2800, CEIL_Y + 26), "#efe8da", blob(rect_pts(-900, CEIL_Y + 14, 2800, CEIL_Y + 26), "#cfc6b4", .9),
                   w=3.6, seed=8001))
    return "".join(s)


def wall_ext(t):
    """Стена: узор den.wall, растянутый вверх до потолка; плинтус."""
    den.wall(t)          # регистрирует узор стены в DEFS
    pid = "pWall" + den.WALL[1:]
    return (f'<rect x="-900" y="-1400" width="3700" height="{FLOOR_Y + 1400}" fill="url(#{pid})"/>' +
            shape(rect_pts(-900, FLOOR_Y - 34, 2800, FLOOR_Y + 4), "#3a2a22", blob(rect_pts(-900, FLOOR_Y - 12, 2800, FLOOR_Y + 4), "#271b15", .9),
                  w=3.6, seed=4001))


def poster():
    x0, y0, x1, y1 = 90.0, 380.0, 330.0, 700.0
    inner = blob(rect_pts(x0, y0, x1, y1), "#f3e6c8")
    inner += blob([(x0, y1 - 90), (x0 + 80, y1 - 190), (x0 + 130, y1 - 140), (x0 + 180, y1 - 230), (x1, y1 - 110), (x1, y1), (x0, y1)], "#5f86a8")
    inner += blob([(x0 + 160, y1 - 210), (x0 + 180, y1 - 230), (x0 + 200, y1 - 205), (x0 + 186, y1 - 196)], "#ffffff")
    inner += blob(ellipse_pts(x0 + 70, y0 + 80, 34, 34, 16), "#e8a24a")
    inner += blob([(x0, y1 - 40), (x1, y1 - 70), (x1, y1), (x0, y1)], "#3f7a72")
    s = [blob(rect_pts(x0 + 8, y0 + 12, x1 + 8, y1 + 12), "#2a1c18", .25)]
    s.append(shape(rect_pts(x0 - 12, y0 - 12, x1 + 12, y1 + 12), "#3a2a22", "", w=4, seed=8010))
    s.append(shape(rect_pts(x0, y0, x1, y1), "#f3e6c8", inner, w=3, seed=8011))
    return "".join(s)


def shelf_r():
    """Полка с книгами над спинкой дивана справа от окна (den.shelf, сдвинута)."""
    return f'<g transform="translate(330 40)">{den.shelf(0)}</g>'


def side_wall():
    """Угол комнаты справа: боковая стена уходит к зрителю, плинтус по диагонали."""
    cx = CORNER_X
    s = [shape([(cx, -1400, 1), (2900, -1400, 1), (2900, FLOOR_Y + 520, 1), (cx, FLOOR_Y, 1)], WALL_SIDE,
               blob([(cx, -1400), (cx + 60, -1400), (cx + 60, FLOOR_Y + 40), (cx, FLOOR_Y)], WALL_SIDE_SH, .8), w=4.4, seed=8020)]
    s.append(shape([(cx, FLOOR_Y - 34, 1), (2900, FLOOR_Y + 470, 1), (2900, FLOOR_Y + 520, 1), (cx, FLOOR_Y + 4, 1)], "#3a2a22", "", w=3.4, seed=8021))
    s.append(line([(cx, CEIL_Y + 26), (2900, CEIL_Y - 300)], 4, seed=8022))
    return "".join(s)


def floor():
    return den.floor()


def nightstand():
    x0, x1, y = NS
    s = [blob(ellipse_pts((x0 + x1) / 2 + 10, FLOOR_Y + 4, (x1 - x0) * .62, 12, 14), "#1a100a", .3)]
    for k, x in enumerate((x0 + 14, x1 - 14)):
        s.append(shape(rect_pts(x - 9, y + 200, x + 9, FLOOR_Y + 4), WOOD_SH, "", w=3, seed=8030 + k))
    body = rect_pts(x0 + 4, y + 18, x1 - 4, y + 220, 4)
    s.append(shape(body, WOOD, blob(rect_pts(x1 - 40, y + 18, x1 - 4, y + 220), WOOD_SH, .8), w=4, seed=8033))
    for k, (a, b) in enumerate(((y + 34, y + 116), (y + 126, y + 206))):
        s.append(shape(rect_pts(x0 + 18, a, x1 - 50, b, 4), WOOD_HI, blob(rect_pts(x0 + 18, b - 12, x1 - 50, b), WOOD_SH, .7), w=3, seed=8035 + k))
        s.append(shape(ellipse_pts((x0 + x1) / 2 - 18, (a + b) / 2, 10, 7, 10), "#d9c08a", "", w=2.4, seed=8040 + k))
    s.append(shape(rect_pts(x0 - 8, y, x1 + 8, y + 20, 4), WOOD_HI, blob(rect_pts(x0 - 8, y + 12, x1 + 8, y + 20), WOOD_SH, .9), w=4, seed=8045))
    # стакан воды и книжка
    s.append(shape(rect_pts(x0 + 4, y - 20, x0 + 52, y + 2, 3), "#c44f3a", blob(rect_pts(x0 + 4, y - 8, x0 + 52, y + 2), "#8f3a2c", .8), w=2.8,
                   seed=8046))
    return "".join(s)


def sofa_back():
    s = []
    s.append(shape(rect_pts(SOFA_X0 + 30, 830, SOFA_X1 - 30, 1130, 40), SOFA_SH, "", w=4.6, seed=8050))
    for k, (a, b) in enumerate(((SOFA_X0 + 64, 716), (724, SOFA_X1 - 64))):
        inner = blob(rect_pts(a, 1040, b, 1120), SOFA_SH, .8)
        inner += blob(rect_pts(a, 850, b, 880), SOFA_HI, .7)
        inner += line([(a + 30, 900), ((a + b) / 2, 912), (b - 30, 902)], 2.2, SOFA_DK, seed=8060 + k, op=.6)
        s.append(shape(rect_pts(a, 850, b, 1124, 34), SOFA, inner, w=4.4, seed=8055 + k))
    return "".join(s)


def armrest(x0, x1, seed):
    inner = blob(rect_pts(x1 - 26, 960, x1, 1300), SOFA_SH, .85) + blob(rect_pts(x0, 960, x1, 990), SOFA_HI, .7)
    return shape(rect_pts(x0, 950, x1, 1296, 30), SOFA, inner, w=4.6, seed=seed)


def seat():
    s = []
    x0, x1 = SOFA_X0 + 60, SOFA_X1 - 60
    s.append(shape(rect_pts(x0 - 6, MAT_F - 6, x1 + 6, 1290, 10), SOFA, blob(rect_pts(x0, 1250, x1, 1290), SOFA_SH, .9), w=4.4, seed=8070))
    for k, x in enumerate((x0 + 30, x1 - 30)):
        s.append(shape(rect_pts(x - 12, 1288, x + 12, FLOOR_Y + 2), WOOD_SH, "", w=3, seed=8072 + k))
    # простыня: верх сиденья + свисает на перед
    top = [(x0 + 10, MAT_T, 1), (x1 - 10, MAT_T, 1), (x1, MAT_F + 46), (x1 - 40, MAT_F + 60), (x0 + 200, MAT_F + 52), (x0 + 40, MAT_F + 58),
           (x0, MAT_F + 44)]
    inner = blob([(x0, MAT_F + 4), (x1, MAT_F + 4), (x1, MAT_F + 70), (x0, MAT_F + 70)], SHEET_SH, .8)
    s.append(shape(top, SHEET, inner, w=4, seed=8075))
    return "".join(s)


def pillow(cx, cy, k=1.0, dent=0.0, lift=0.0, sq=1.0):
    rx, ry = 132 * k, 46 * k * sq
    cy = cy - lift
    pts = [(cx - rx, cy + ry * .2), (cx - rx * .92, cy - ry * .8), (cx - rx * .4, cy - ry * (1 - .5 * dent)), (cx, cy - ry * (1 - .8 * dent)),
           (cx + rx * .5, cy - ry * (1 - .4 * dent)), (cx + rx * .95, cy - ry * .75), (cx + rx, cy + ry * .3), (cx + rx * .7, cy + ry),
           (cx - rx * .6, cy + ry * 1.02)]
    inner = blob([(cx - rx, cy + ry * .1), (cx + rx, cy + ry * .1), (cx + rx, cy + ry * 1.2), (cx - rx, cy + ry * 1.2)], "#c8d3dd", .85)
    inner += line([(cx - rx * .8, cy - ry * .2), (cx - rx * .3, cy + ry * .1)], 2, "#a9b7c4", seed=8081, op=.7)
    inner += line([(cx + rx * .4, cy + ry * .2), (cx + rx * .8, cy - ry * .1)], 2, "#a9b7c4", seed=8082, op=.7)
    return (blob([(p[0] + 8, p[1] + 10) for p in pts], "#2a1c18", .18) + shape(pts, "#f4f1ea", inner, w=4.4, seed=8080))


PLAID, PLAID_D, PLAID_L, PLAID_R = "#4f7d55", "#35583c", "#8fb08a", "#c9473a"   # плед — цвета сцены clock (scene_clock.py)


def plaid_defs():
    pid = "plaid37"
    sz = 110
    lib.DEFS.append(
        f'<pattern id="{pid}" width="{sz}" height="{sz}" patternUnits="userSpaceOnUse" patternTransform="rotate(-6)">'
        f'<rect width="{sz}" height="{sz}" fill="{PLAID}"/>'
        f'<rect x="0" y="{sz * .35}" width="{sz}" height="{sz * .3}" fill="{PLAID_D}" opacity=".55"/>'
        f'<rect x="{sz * .35}" y="0" width="{sz * .3}" height="{sz}" fill="{PLAID_D}" opacity=".55"/>'
        f'<rect x="0" y="{sz * .86}" width="{sz}" height="{sz * .04}" fill="{PLAID_R}"/>'
        f'<rect x="{sz * .86}" y="0" width="{sz * .04}" height="{sz}" fill="{PLAID_R}"/>'
        f'<rect x="0" y="{sz * .12}" width="{sz}" height="{sz * .03}" fill="{PLAID_L}" opacity=".8"/>'
        f'<rect x="{sz * .12}" y="0" width="{sz * .03}" height="{sz}" fill="{PLAID_L}" opacity=".8"/>'
        f'</pattern>')
    return pid


def plaid(pts, folds=(), seed=8090, shade_y=None):
    pid = plaid_defs()
    inner = f'<rect x="-900" y="-900" width="4000" height="4000" fill="url(#{pid})"/>'
    if shade_y is not None:
        inner += blob([(-900, shade_y), (4000, shade_y), (4000, 3000), (-900, 3000)], "#13241a", .3)
    inner += blob([(-900, -900), (4000, -900), (4000, 3000)], "#ffffff", 0)
    for k, f_ in enumerate(folds):
        inner += line(f_, 3, "#22382a", seed=seed + 10 + k, op=.7)
    return shape(pts, PLAID, inner, w=4.8, seed=seed)


def light():
    """Утро: косой тёплый луч из окна на спинку дивана и постель, мягкая виньетка."""
    x0, y0, x1, y1 = den.WIN
    g = lib.lin_grad([(0, "#fff1c8", .55), (1, "#fff1c8", 0)], 0, 0, 0, 1)
    beam = [(x0, y0), (x1, y0), (x1 - 120, 1300), (x0 - 520, 1300)]
    o = [f'<path d="{lib.fill_d([p + (1,) for p in beam])}" fill="url(#{g})" style="mix-blend-mode:screen" {lib.blur(30)}/>']
    g2 = lib.rad_grad([(0, "#ffd9a0", .25), (1, "#ffd9a0", 0)], (x0 + x1) / 2, 1100, 900, 600)
    o.append(f'<rect x="-900" y="-1400" width="3800" height="4400" fill="url(#{g2})" style="mix-blend-mode:screen"/>')
    return "".join(o)


def slippers():
    o = []
    for k, (x, y, a) in enumerate(((1010, 1420, -8), (1100, 1440, 6))):
        pts = lib.T([(-60, -10), (-30, -22), (40, -22), (64, -6), (60, 14), (-56, 16)], x, y, 1, a)
        o.append(blob(lib.T(ellipse_pts(0, 18, 64, 10, 12), x, y, 1, a), "#1a100a", .25))
        o.append(shape(pts, "#5f6fa8", blob(lib.T([(-60, 4), (60, 4), (60, 16), (-60, 16)], x, y, 1, a), "#465390", .9) +
                       blob(lib.T([(-10, -22), (40, -22), (64, -6), (20, -4)], x, y, 1, a), "#7d8cc2", .9), w=3.4, seed=8100 + k))
    return "".join(o)


def back_world(t):
    """Всё, что за Димой: потолок, стена, окно, постер, полка, пол, угол, тумбочка, диван без подлокотников спереди."""
    s = [wall_ext(t), ceiling(), den.window(t), poster(), shelf_r(), floor(), side_wall(), slippers(), nightstand(), sofa_back(),
         armrest(SOFA_X0, SOFA_X0 + 88, 8065), armrest(SOFA_X1 - 88, SOFA_X1, 8066), seat()]
    return "".join(s)


def mix_c(a, b, u):
    return mix(a, b, u)


__all__ = ["setup", "back_world", "pillow", "plaid", "light", "INK", "math"]
