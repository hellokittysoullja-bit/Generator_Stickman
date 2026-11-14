"""Общие предметы рилса 57 «вода» — ОДИН вид для групп A, B, C (владелец: «не рисуй свои»).

Подключение (в сцене группы, у которой рядом свой lib.py/ink.py):
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common")); import props
Функции возвращают строку SVG (мир кадра, 1080×1920), без собственной камеры. Точка (x, y) — ЦЕНТР ДНА предмета на опоре.
Единица k=1 — масштаб «Дима в полный рост» (BS 0.6): стакан 58×84 ≈ ширина ладони × 1,3 ладони (ладонь Димы ≈ 47 px при
hand k=1); на крупных планах предмет и кисть масштабируются ОДНИМ коэффициентом (k стакана = k кисти). Все заливки сплошные
(без полупрозрачных фигур), тушь — INK из lib, как у худи Димы.

    glass(x, y, k, level, tilt, slosh, wet)   высокий прямой стакан; level 0…1 — высота воды, tilt° — наклон (вода остаётся горизонтальной)
    bottle(x, y, k, level, tilt, slosh, cap, drops)   обычная 0,5 л: прозрачный корпус, вода, оранжевая крышка, одна полоса-этикетка
    bowl(x, y, k, level, t, ripple)   миска кота: кремовая керамика, тёмная полоса по краю, вода
    droplet(x, y, k, rot)             капля воды
    shine_star(x, y, k, u)            четырёхлучевой блик (u 0…1 — жизнь вспышки)
Константы: C_WATER, C_GLASS, C_CAP, C_BOWL, GLASS_W, GLASS_H, BOTTLE_H."""
import math

import lib
from lib import blob, ellipse_pts, f, line, mix, rect_pts, shape

C_WATER = "#4AA3DF"
C_WATER_SH = "#3C8CC6"      # нижняя часть воды / тень
C_WATER_TOP = "#86C8F0"     # поверхность
C_GLASS = "#DCEFF9"
C_GLASS_SH = "#BCD9EA"
C_GLASS_IN = "#C9E4F2"      # задняя стенка внутри (над водой)
C_CAP = "#E8892B"
C_CAP_SH = "#BD6A19"
C_BOWL = "#F3E6CF"
C_BOWL_SH = "#DAC7A6"
C_BOWL_BAND = "#4E3B30"
C_WHITE = "#FFFFFF"
GLASS_W, GLASS_H = 58.0, 84.0
BOTTLE_H = 148.0


def _tf(inner, x, y, k, rot=0.0):
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k:.5f})">{inner}</g>'


def _water(level, H, tilt, slosh, wmax, rx_fn):
    """Вода в локальных координатах стакана: многоугольник (полуплоскость под горизонтальной поверхностью) и эллипс поверхности."""
    a = math.radians(-tilt + slosh)
    cy = -H * level
    u = (math.cos(a), math.sin(a))
    n = (-math.sin(a), math.cos(a))
    c = (0.0, cy)
    P = [(c[0] - 260 * u[0], c[1] - 260 * u[1]), (c[0] + 260 * u[0], c[1] + 260 * u[1]),
         (c[0] + 260 * u[0] + 420 * n[0], c[1] + 260 * u[1] + 420 * n[1]), (c[0] - 260 * u[0] + 420 * n[0], c[1] - 260 * u[1] + 420 * n[1])]
    rx = rx_fn(level)
    surf = ellipse_pts(c[0], c[1], rx, max(4.0, rx * .2), 16, rot=math.degrees(a))
    return [(p[0], p[1], 1) for p in P], surf


def glass(x, y, k=1.0, level=0.75, tilt=0.0, slosh=0.0, wet=False, seed=0):
    """Высокий прямой стакан (дно в (x, y)). level 0 — пустой, 1 — до краёв (рисуется до 0.94)."""
    H, WT, WB = GLASS_H, GLASS_W / 2, GLASS_W / 2 - 6
    level = max(0.0, min(0.94, level))
    sd = 7000 + seed * 11
    body = [(-WT, -H, 1), (WT, -H, 1), (WB + 1, -6), (WB - 4, 0, 1), (-WB + 4, 0, 1), (-WB - 1, -6)]
    inner = blob(rect_pts(-WT, -12, WT, 2), C_GLASS_SH)                         # толстое дно
    inner += blob([(WT * .5, -H), (WT, -H), (WB + 1, -6), (WB - 4, 0), (WT * .35, 0)], C_GLASS_SH)   # тень справа
    if level > 0.005:
        poly, surf = _water(level, H - 12, tilt, slosh, WT, lambda lv: (WT - 3) - 6 * (1 - lv) * 0.8)
        # у воды нижняя граница — над дном стакана; тень воды справа
        inner += blob(poly, C_WATER)
        inner += blob(surf, C_WATER_TOP)
    out = [shape(body, C_GLASS, inner, w=3.6, seed=sd)]
    if level > 0.005:
        # тень воды справа — поверх воды, внутри стакана
        c = lib.clip_of(body)
        a = math.radians(-tilt + slosh)
        cy = -(H - 12) * level
        shade = [(WT * .38, cy + 6, 1), (WT + 6, cy + 6 + 40 * math.sin(a), 1), (WT + 6, 4, 1), (WB * .3, 4, 1)]
        out.append(f'<g clip-path="url(#{c})">{blob(shade, C_WATER_SH)}</g>')
    # блик: белая полоса слева и точка (сплошные, поверх)
    hi_top = -H + 12 if level < .2 else -(H - 12) * level + 10
    out.append(line([(-WT + 9, -H + 10), (-WB + 8, -22)], 6, C_WHITE, taper=.5, wmin=.3, seed=sd + 1, peak=.5))
    out.append(blob(ellipse_pts(-WT + 11, -H + 24, 2.6, 4, 8), C_WHITE))
    # ободок: эллипс устья, внутри — задняя стенка
    rim = ellipse_pts(0, -H, WT, 7.5, 18)
    rin = blob(ellipse_pts(0, -H + 1, WT - 4, 5, 16), C_GLASS_IN)
    if level > .86:
        rin = blob(ellipse_pts(0, -H + 1.5, WT - 4, 5, 16), C_WATER_TOP)
    out.append(shape(rim, C_GLASS, rin, w=3.0, seed=sd + 3))
    if wet:   # капельки на стенке
        for j, (dx, dy, r) in enumerate(((8, -44, 2.6), (-14, -58, 2.2), (13, -22, 2.0))):
            out.append(blob(ellipse_pts(dx, dy, r, r * 1.35, 8), C_WATER_TOP))
    return _tf("".join(out), x, y, k, tilt)


def bottle(x, y, k=1.0, level=0.8, tilt=0.0, slosh=0.0, cap=True, drops=False, seed=0, cap_open=0.0):
    """Бутылка 0,5 л. Дно в (x, y); корпус ±23, высота 148 с крышкой. cap_open 0…1 — крышка снята (рисуется рядом выше)."""
    sd = 7300 + seed * 11
    WB, HB, HN = 23.0, 96.0, 124.0
    level = max(0.0, min(1.0, level))
    body = [(-WB + 5, 0, 1), (WB - 5, 0, 1), (WB, -8), (WB, -HB + 10), (WB - 4, -HB - 8), (11, -HN + 8), (9, -HN, 1), (-9, -HN, 1), (-11, -HN + 8), (-WB + 4, -HB - 8),
            (-WB, -HB + 10), (-WB, -8)]
    inner = blob([(WB * .4, -HN), (WB, -HN), (WB, -8), (WB - 5, 0), (WB * .3, 0)], C_GLASS_SH)
    if level > .01:
        poly, surf = _water(level, HN - 14, tilt, slosh, WB, lambda lv: 17 if lv < .75 else 12)
        inner += blob(poly, C_WATER)
        inner += blob(surf, C_WATER_TOP)
    # этикетка-полоса: белая, тонкая синяя линия (без букв)
    inner += blob(rect_pts(-WB - 2, -66, WB + 2, -36), "#F7F6F0")
    inner += blob(rect_pts(-WB - 2, -66, WB + 2, -62), C_WATER_SH) + blob(rect_pts(-WB - 2, -40, WB + 2, -36), C_WATER_SH)
    out = [shape(body, C_GLASS, inner, w=3.4, seed=sd)]
    if level > .01:
        c = lib.clip_of(body)
        a = math.radians(-tilt + slosh)
        cy = -(HN - 14) * level
        shade = [(WB * .4, cy + 4, 1), (WB + 4, cy + 4 + 30 * math.sin(a), 1), (WB + 4, -66, 1), (WB * .4, -66, 1)]
        shade2 = [(WB * .4, -36), (WB + 4, -36), (WB + 4, 2), (WB * .3, 2)]
        out.append(f'<g clip-path="url(#{c})">{blob(shade, C_WATER_SH) if cy < -66 else ""}{blob(shade2, C_WATER_SH) if level > .08 else ""}</g>')
    out.append(line([(-WB + 8, -HB + 6), (-WB + 7, -70)], 5.5, C_WHITE, taper=.5, wmin=.3, seed=sd + 1, peak=.5))
    out.append(line([(-WB + 8, -30), (-WB + 8, -14)], 5, C_WHITE, taper=.5, wmin=.3, seed=sd + 2, peak=.5))
    # горлышко-кольцо и крышка
    out.append(shape(rect_pts(-12, -HN - 1, 12, -HN + 5, 2), C_GLASS_SH, "", w=2.8, seed=sd + 3))
    cy0 = -HN - 20 - 36 * cap_open
    if cap:
        capb = [(-12.5, cy0, 1), (12.5, cy0, 1), (12.5, cy0 + 20, 1), (-12.5, cy0 + 20, 1)]
        ci = blob(rect_pts(4, cy0, 13, cy0 + 20), C_CAP_SH)
        ci += "".join(line([(-9 + 6 * j, cy0 + 3), (-9 + 6 * j, cy0 + 17)], 2.2, C_CAP_SH, taper=.1, wmin=.9, seed=sd + 20 + j) for j in range(3))
        out.append(shape(capb, C_CAP, ci, w=3.2, seed=sd + 4))
        out.append(blob(ellipse_pts(0, cy0, 12.5, 3, 12), mix(C_CAP, "#ffffff", .25)))
    if drops:
        for j, (dx, dy, r) in enumerate(((11, -52, 2.8), (-9, -24, 2.2), (14, -88, 2.2))):
            out.append(blob(ellipse_pts(dx, dy, r, r * 1.4, 8), C_WATER_TOP))
    return _tf("".join(out), x, y, k, tilt)


def bowl(x, y, k=1.0, level=0.75, t=0.0, ripple=0.0, seed=0):
    """Миска кота (дно в (x, y)): ширина 170, высота 56. ripple 0…1 — сила ряби (кольца от центра)."""
    sd = 7600 + seed * 11
    RX, RY, HH = 85.0, 15.0, 56.0
    body = [(-RX, -HH, 1), (RX, -HH, 1), (RX - 7, -30), (RX - 26, -9), (RX - 40, 0, 1), (-RX + 40, 0, 1), (-RX + 26, -9), (-RX + 7, -30)]
    inner = blob([(RX * .35, -HH), (RX, -HH), (RX - 7, -30), (RX - 26, -9), (RX - 40, 0), (RX * .3, 0)], C_BOWL_SH)
    inner += blob(rect_pts(-RX - 4, -HH, RX + 4, -HH + 11), C_BOWL_BAND)            # тёмная полоса по краю
    inner += blob(rect_pts(-RX - 4, -HH + 17, RX + 4, -HH + 19), C_BOWL_BAND)       # тонкая вторая
    out = [shape(body, C_BOWL, inner, w=3.8, seed=sd)]
    rim = ellipse_pts(0, -HH, RX, RY, 24)
    wl = -HH + (1 - max(0.05, min(1.0, level))) * 8
    rin = blob(ellipse_pts(0, -HH + 1, RX - 6, RY - 3, 22), "#CDBA98")             # внутренняя стенка
    rin += blob(ellipse_pts(0, wl + 2.5, RX - 11, RY - 6.5, 22), C_WATER)
    rin += blob(ellipse_pts(-6, wl + 1, RX - 30, RY - 9, 20), C_WATER_TOP)
    if ripple > .02:
        for j in range(3):
            u = (t * 1.5 + j / 3.0) % 1.0
            rr = 10 + u * (RX - 28)
            ry_ = max(2.0, rr * (RY - 7) / RX)
            pts = [(rr * math.cos(a), wl + 2 + ry_ * math.sin(a)) for a in [math.pi * (0.05 + 1.9 * i / 18) for i in range(19)]]
            rin += line(pts, 3.2, C_WHITE, taper=.7, wmin=.1, seed=sd + 40 + j, op=1.0) if (1 - u) * ripple > .35 and rr > 22 else ""
    out.append(shape(rim, C_BOWL, rin, w=3.4, seed=sd + 1))
    out.append(line([(-RX + 14, -HH + 24), (-RX + 22, -14)], 5, "#FFF8EA", taper=.5, wmin=.3, seed=sd + 3, peak=.5))
    return _tf("".join(out), x, y, k)


def droplet(x, y, k=1.0, rot=0.0, seed=0):
    """Капля воды (острый кончик вверх): сплошная заливка цвета воды, тонкая тушь, белый блик."""
    pts = [(0, -17, 1), (7, -5), (10, 5), (5, 13), (0, 15), (-5, 13), (-10, 5), (-7, -5)]
    inner = blob([(-4.5, 1), (-2.5, -6), (-1, -5), (-3, 6)], C_WHITE)
    return _tf(shape(pts, C_WATER, inner, w=2.6, seed=7900 + seed), x, y, k, rot)


def shine_star(x, y, k=1.0, u=0.5):
    """Четырёхлучевой блик-вспышка (u 0…1: растёт и гаснет); белый с тонкой жёлтой серединой, без туши."""
    s = math.sin(math.pi * max(0.0, min(1.0, u)))
    if s < .05:
        return ""
    R, r = 17 * s, 3.4 * s
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = R if i % 2 == 0 else r
        pts.append((rr * math.cos(a), rr * math.sin(a), 1))
    return _tf(blob(pts, C_WHITE), x, y, k, 10 * u)
