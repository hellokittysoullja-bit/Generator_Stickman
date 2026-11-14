"""Рилс 56, группа B: предметы крупно (свитер, зонт, фен, сковородка, носок) и общие кусочки (пыль, штрихи удара, блик).
Каждый предмет рисуется в своей системе с центром (0, 0) и ставится place(svg, x, y, rot, sx, sy); контур — живая тушь ink.py.
Силуэты узнаваемые: сковородка — круг с длинной ручкой, фен — пистолет с соплом, зонт — купол/свёрток с крючком."""
import math

import lib
from lib import INK, band, blob, ellipse_pts, f, line, rect_pts, shape

# палитра дня
TEAL, TEAL_L, TEAL_D = "#3f93a8", "#6cb8c8", "#2a6a7e"
LINING, LINING_D = "#f1e6cc", "#d9c9a3"
FLOOR_A, FLOOR_B = "#c9a06c", "#a97f4f"
WALL_A, WALL_B = "#f0e2c6", "#e3cfa8"
SWEATERS = ["#c9503c", "#5f8a4e", "#a8648f", "#e0b04a", "#4d6fae"]


def place(g, x, y, rot=0.0, sx=1.0, sy=None, cx=0.0, cy=0.0):
    sy = sx if sy is None else sy
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sx:.4f} {sy:.4f}) translate({f(-cx)} {f(-cy)})">{g}</g>')


def shadow(x, y, rx, ry, op=0.35, sd=8):
    return lib.blob(ellipse_pts(x, y, rx, ry, 18), "#2a1608", op, lib.blur(sd))


# ═════════════════════════ свитер (плоско сверху) ═════════════════════════
def sweater(col, sd=0, sl_l=-28.0, sl_r=28.0, stripes=True):
    """Тело 150×170, рукава — «колбаски» от плеча; sl_l/sl_r — угол рукава от вертикали вниз (градусы; влево −, вправо +).
    Манжета и подол — резинка, воротник — тёмный овал."""
    dk, lt = lib.mul(col, (0.78, 0.78, 0.78)), lib.mix(col, "#ffffff", 0.35)
    o = []

    def sleeve(side, ang):
        a = math.radians(ang)
        sx, sy = side * 66, -58
        L = 128
        ex, ey = sx + math.sin(a) * L, sy + math.cos(a) * L
        mx, my = (sx + ex) / 2 + side * 6, (sy + ey) / 2
        pts = band([(sx, sy), (mx, my), (ex, ey)], 62, 50, step=5, cap=True)
        inner = blob([(sx - 10, sy), (ex - 8, ey), (ex + 8, ey), (sx + 10, sy)], dk, .55)
        # складка у локтя
        inner += line([(mx - 22, my - 4), (mx + 2, my + 6), (mx + 22, my - 2)], 2.4, dk, seed=sd + 3 + side, op=.8)
        g = shape(pts, col, inner, w=4.4, seed=sd + 10 + side)
        # манжета-резинка
        d = (math.sin(a), math.cos(a))
        n = (-d[1], d[0])
        c0 = (ex - d[0] * 22, ey - d[1] * 22)
        cuff = [(c0[0] + n[0] * 30, c0[1] + n[1] * 30), (ex + n[0] * 27 + d[0] * 6, ey + n[1] * 27 + d[1] * 6),
                (ex - n[0] * 27 + d[0] * 6, ey - n[1] * 27 + d[1] * 6), (c0[0] - n[0] * 30, c0[1] - n[1] * 30)]
        rib = "".join(line([(c0[0] + d[0] * k * 8 + n[0] * 28, c0[1] + d[1] * k * 8 + n[1] * 28),
                            (c0[0] + d[0] * k * 8 - n[0] * 28, c0[1] + d[1] * k * 8 - n[1] * 28)], 1.8, dk, seed=sd + 20 + k, op=.7) for k in range(1, 3))
        return g + shape(cuff, dk, rib, w=3.6, seed=sd + 30 + side)

    o.append(sleeve(-1, sl_l))
    o.append(sleeve(1, sl_r))
    body = rect_pts(-75, -88, 75, 88, 22)
    inner = blob([(40, -90), (80, -90), (80, 90), (50, 90)], dk, .5)
    for k in range(-5, 6):
        inner += line([(k * 13, -60), (k * 13 + 1, 66)], 1.5, dk, seed=sd + 40 + k, op=.22)
    if stripes:
        inner += blob([(-80, -6), (80, -6), (80, 12), (-80, 12)], lt, .95) + blob([(-80, 24), (80, 24), (80, 36), (-80, 36)], lt, .95)
    # подол — резинка
    inner += blob([(-80, 66), (80, 66), (80, 92), (-80, 92)], dk, .95)
    inner += "".join(line([(k * 12, 68), (k * 12, 88)], 1.7, lib.mul(col, (.6, .6, .6)), seed=sd + 60 + k, op=.7) for k in range(-6, 7))
    o.append(shape(body, col, inner, w=5.0, seed=sd + 70))
    # ворот
    o.append(shape(ellipse_pts(0, -84, 36, 15, 12), dk, blob(ellipse_pts(0, -80, 28, 9, 10), lib.mul(col, (.5, .5, .5)), .9), w=4.0, seed=sd + 71))
    return "".join(o)


# ═════════════════════════ зонт (сверху, сложенный, с крючком) ═════════════════════════
def umbrella(sd=0):
    """Длина ~470: слева крючок-ручка (J), дальше стержень, свёрнутый купол (темно-синий в складках, ремешок с кнопкой), справа наконечник."""
    NAVY, NAVY_D, NAVY_L = "#34408f", "#232c66", "#5a6cc2"
    o = []
    # ручка-крючок
    hook = [(-230, 40), (-232, 6), (-214, -22), (-182, -28), (-156, -10), (-152, 14), (-144, 14), (-146, -18), (-178, -44), (-220, -40), (-248, -4), (-250, 36)]
    o.append(shape(band([(-150, 4), (-152, -16), (-170, -34), (-200, -36), (-228, -18), (-240, 14), (-232, 38)], 24, 22, step=4, cap=True), "#8a5a36",
                   line([(-150, 0), (-160, -22), (-188, -32)], 3, "#b98a5a", seed=sd + 1, op=.9), w=4.0, seed=sd + 2))
    # стержень
    o.append(shape(rect_pts(-152, -7, -70, 7, 3), "#c9ced8", blob([(-152, 2), (-70, 2), (-70, 7), (-152, 7)], "#8e95a5"), w=3.0, seed=sd + 3))
    # купол свёрнут — вытянутая капля, складки вдоль
    cv = [(-76, 0, 1), (-52, -26), (20, -44), (120, -38), (190, -16), (228, 0, 1), (190, 16), (120, 38), (20, 44), (-52, 26)]
    inner = blob([(-76, 4), (228, 4), (190, 16), (120, 38), (20, 44), (-52, 26)], NAVY_D, .85)
    for k, y in enumerate((-30, -12, 14, 30)):
        inner += line([(-40, y * .5), (60, y), (160, y * .55), (214, y * .12)], 3.0, NAVY_L if k % 2 == 0 else NAVY_D, seed=sd + 5 + k, op=.85, taper=.5)
    # ремешок и кнопка
    inner += blob([(70, -46), (96, -46), (98, 46), (72, 46)], "#d6c8a2", .95)
    inner += line([(72, -44), (72, 44)], 2.0, "#8f805c", seed=sd + 11, op=.8) + line([(96, -44), (98, 44)], 2.0, "#8f805c", seed=sd + 12, op=.8)
    o.append(shape(cv, NAVY, inner, w=5.0, seed=sd + 13))
    o.append(shape(ellipse_pts(84, 0, 8, 8, 8), "#c9ced8", "", w=2.6, seed=sd + 14))
    # наконечник
    o.append(shape([(224, -5, 1), (262, -2, 1), (262, 2, 1), (224, 5, 1)], "#c9ced8", "", w=2.6, seed=sd + 15))
    return "".join(o)


# ═════════════════════════ фен (пистолет, сопло, шнур) ═════════════════════════
def dryer(sd=0):
    PINK, PINK_D, PINK_L = "#e0527e", "#a8335a", "#f58aa8"
    o = []
    # шнур завитком позади
    cord = [(-30, 70), (-70, 130), (-40, 190), (-100, 220), (-80, 270), (-150, 300), (-210, 270)]
    o.append(line(cord, 11, INK, taper=0, wmin=1, seed=sd + 1))
    o.append(line(cord, 6, "#3a3f50", taper=0, wmin=1, seed=sd + 2))
    # ручка (вниз, чуть наклонена назад)
    hd = [(-34, 30, 1), (30, 30, 1), (50, 150), (44, 188, 1), (-12, 190, 1), (-30, 150)]
    o.append(shape(hd, PINK_D, blob([(10, 30), (34, 30), (52, 150), (44, 188), (20, 188)], "#7e2442", .7) +
                   line([(-14, 60), (-4, 150)], 3.0, PINK_L, seed=sd + 3, op=.7) +
                   blob(rect_pts(-26, 78, 30, 100, 5), "#2b2f3a", .9), w=4.6, seed=sd + 4))
    # корпус — барабан
    body = [(-150, -50, 1), (-60, -66), (60, -66), (130, -56, 1), (134, 40, 1), (60, 40), (-60, 40), (-150, 30, 1)]
    inner = blob([(-150, 12), (134, 12), (134, 40), (60, 40), (-60, 40), (-150, 30)], PINK_D, .85)
    inner += line([(-120, -42), (60, -52), (116, -46)], 6.0, PINK_L, seed=sd + 5, op=.9, taper=.5)
    o.append(shape(body, PINK, inner, w=5.0, seed=sd + 6))
    # решётка сзади
    o.append(shape(rect_pts(-170, -44, -148, 26, 4), "#3a3f50", "".join(line([(-168, y), (-150, y)], 2, "#8d92a6", seed=sd + 10 + k)
                                                                   for k, y in enumerate((-30, -14, 2, 18))), w=3.6, seed=sd + 9))
    # сопло (шире)
    noz = [(128, -50, 1), (184, -72, 1), (214, -72, 1), (214, 56, 1), (184, 56, 1), (130, 36, 1)]
    o.append(shape(noz, "#2b2f3a", blob([(130, 20), (214, 20), (214, 56), (184, 56), (130, 36)], "#161922", .8) +
                   line([(190, -62), (190, 46)], 3.0, "#5d6376", seed=sd + 12, op=.9), w=4.4, seed=sd + 11))
    o.append(line([(150, -40), (196, -60)], 3.0, "#6b7186", seed=sd + 13, op=.8))
    # кнопка
    o.append(shape(rect_pts(-20, -78, 24, -62, 5), "#f7e07a", "", w=3.0, seed=sd + 14))
    return "".join(o)


# ═════════════════════════ сковородка (сверху: круг + длинная ручка) ═════════════════════════
def pan(sd=0):
    o = []
    # ручка вправо
    o.append(shape(rect_pts(70, -22, 360, 22, 10), "#2b2f3a", blob([(70, 6), (360, 6), (360, 22), (70, 22)], "#161922", .85) +
                   line([(96, -12), (330, -12)], 3.0, "#6b7186", seed=sd + 1, op=.8), w=4.6, seed=sd + 2))
    o.append(shape(ellipse_pts(334, 0, 11, 9, 10), "#7b8296", "", w=3.0, seed=sd + 3))       # отверстие-подвес (светлое пятно под ним — стена)
    o.append(shape(ellipse_pts(334, 0, 7, 5.5, 10), "#d9c9a3", "", w=2.0, seed=sd + 33, ink=True))
    # крепление
    o.append(shape([(78, -30, 1), (124, -34, 1), (124, 34, 1), (78, 30, 1)], "#8d92a6", "", w=3.8, seed=sd + 4))
    # чаша: наружный борт и внутренность
    o.append(shape(ellipse_pts(0, 0, 118, 118, 22), "#4a4f5c", blob(ellipse_pts(14, 16, 108, 100, 18), "#2f333d", .6), w=5.4, seed=sd + 5))
    inner = shape(ellipse_pts(0, 0, 96, 96, 22), "#3b3f4a", blob(ellipse_pts(-20, -22, 56, 50, 16), "#575c6c", .75) +
                  blob(ellipse_pts(10, 20, 80, 70, 14), "#262a33", .45), w=4.0, seed=sd + 6)
    o.append(inner)
    o.append(line([(-62, -46), (-30, -76), (10, -86)], 5.0, "#aeb4c6", seed=sd + 7, taper=.6, wmin=.3, op=.9))   # блик
    return "".join(o)


# ═════════════════════════ носок ═════════════════════════
def sock(col="#f2ede0", sd=0, stripe="#c9503c"):
    pts = [(-16, -70, 1), (22, -70, 1), (26, -10), (24, 24), (64, 44), (80, 74, 1), (50, 92), (-6, 70), (-22, 30)]
    inner = blob([(-18, -70), (26, -70), (26, -46), (-18, -46)], stripe, .95) + blob([(-18, -36), (26, -36), (26, -30), (-18, -30)], stripe, .8)
    inner += blob([(40, 56), (80, 74), (52, 92)], lib.mul(col, (.82, .82, .82)), .9)
    return shape(pts, col, inner, w=3.8, seed=sd + 1)


def trouser_leg(col="#4d6fae", sd=0):
    """Штанина, торчащая из щели (вертикально вверх из точки 0,0)."""
    pts = [(-46, 0, 1), (-42, -110), (-52, -200, 1), (46, -200, 1), (40, -110), (46, 0, 1)]
    inner = blob([(10, 0), (46, 0), (50, -200), (20, -200)], lib.mul(col, (.74, .74, .74)), .75)
    inner += line([(-30, -120), (0, -104), (28, -126)], 2.4, lib.mul(col, (.66, .66, .66)), seed=sd + 4, op=.9)
    inner += line([(-8, 0), (-6, -190)], 2.0, "#8fa6d4", seed=sd + 5, op=.6)
    return shape(pts, col, inner, w=4.4, seed=sd + 1)


# ═════════════════════════ эффекты ═════════════════════════
def burst(cx, cy, k, n=10, r0=60, r1=170, w=10, color="#fff4c2", seed=0, a0=0.0, spread=360):
    """Лучи-штрихи удара: k 0→1 — лучи разлетаются и тают."""
    if not 0 < k < 1:
        return ""
    s = []
    for j in range(n):
        a = math.radians(a0 + spread * j / n + 7 * math.sin(j * 2.3))
        ra = r0 + (r1 - r0) * lib.ease_out(k, 2) * (0.8 + 0.2 * math.sin(j * 1.7))
        rb = ra + (r1 - r0) * 0.55 * (1 - k)
        s.append(line([(cx + ra * math.cos(a), cy + ra * math.sin(a)), (cx + rb * math.cos(a), cy + rb * math.sin(a))],
                      w * (1 - k) + 1.5, color, taper=.6, wmin=.2, seed=seed + j))
    return "".join(s)


def dust(cx, cy, k, n=6, spread=170, rise=70, seed=0, color="#fff6e0", rmax=34):
    if not 0 < k < 1:
        return ""
    s = []
    for j in range(n):
        u = (j + 0.5) / n * 2 - 1
        x = cx + u * spread * lib.ease_out(k, 2)
        y = cy - rise * lib.ease_out(k, 2) * (1 - abs(u) * .5)
        r = rmax * (0.5 + 0.5 * math.sin(j * 1.9 + 1)) * (0.4 + k) * (1 - k * .6)
        s.append(blob(ellipse_pts(x, y, r, r * .8, 9), color, 0.85 * (1 - k)))
    return "".join(s)


def glint(cx, cy, k, r=60, color="#ffffff"):
    """Четырёхлучевой блик-звёздочка: растёт и тает (k 0→1)."""
    if not 0 < k < 1:
        return ""
    a = r * math.sin(math.pi * k) ** .7
    pts = [(cx, cy - a, 1), (cx + a * .16, cy - a * .16, 1), (cx + a, cy, 1), (cx + a * .16, cy + a * .16, 1), (cx, cy + a, 1),
           (cx - a * .16, cy + a * .16, 1), (cx - a, cy, 1), (cx - a * .16, cy - a * .16, 1)]
    return blob(pts, color, 0.95)
