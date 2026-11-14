"""Комната Димы вечером (s04 рилса 36): стена с обоями цвета пыльной бирюзы, окно с ночью и шторой, торшер в правом
углу, картина, диван терракотовый анфас (спинка, подлокотники, подушки), плед в клетку, ковёр, пол из досок.
Мир: пол y = 0 (вверх — минус); сиденье дивана y = SEAT_Y; слева подлокотник, к нему Дима откидывается спиной."""
import math

import numpy as np

import lib
from lib import INK, ellipse_pts, line, shape

WALL, WALL_SH = "#9db8b8", "#86a3a4"
SOFA, SOFA_SH, SOFA_HI, SOFA_DK = "#c46a48", "#9e4f34", "#d9845f", "#7c3a26"
FLOOR, FLOOR_SH, FLOOR_LN = "#a8724a", "#875a37", "#684226"
SOFA_X = (-250.0, 470.0)        # от левого края левого подлокотника до правого края правого
SEAT_Y = -232.0
BACK_Y = -470.0
ARM_W = 86.0
ARM_Y = -340.0
CORNER = (600.0, 0.0)           # куда летит сумка (угол у торшера)


def R(x0, y0, x1, y1):
    return [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]


def blob(pts, color, op=1.0, extra=""):
    return lib.blob([(p[0], p[1], 1) for p in pts] if len(pts) <= 6 else pts, color, op, extra)


def wall(t, tv=0.0):
    o = []
    g = lib.lin_grad([(0, "#7f9c9e", 1), (.5, WALL, 1), (1, "#a9c0bc", 1)], 0, -1400, 0, 0, units="userSpaceOnUse")
    o.append(f'<rect x="-1400" y="-2200" width="3200" height="2300" fill="url(#{g})"/>')
    for k in range(-24, 34):          # обои: узкие полосы с ромбиком
        x = k * 70
        o.append(f'<rect x="{x}" y="-2200" width="5" height="2200" fill="{WALL_SH}" opacity=".45"/>')
        for j in range(14):
            y = -1300 + j * 90 + (k % 2) * 45
            o.append(f'<rect x="{x + 31}" y="{y}" width="8" height="8" transform="rotate(45 {x + 35} {y + 4})" fill="{WALL_SH}" opacity=".5"/>')
    # тёплый свет торшера справа и холодный — от телевизора (справа, за кадром)
    gl = lib.rad_grad([(0, "#ffe6b0", .7), (.45, "#ffd590", .3), (1, "#ffd590", 0)], 640, -560, 620)
    o.append(f'<rect x="20" y="-1180" width="1240" height="1240" fill="url(#{gl})"/>')
    if tv > 0:
        gl = lib.rad_grad([(0, "#9fd0ff", .35 * tv), (1, "#9fd0ff", 0)], 700, -400, 700)
        o.append(f'<rect x="0" y="-1100" width="1400" height="1400" fill="url(#{gl})"/>')
    # окно слева с ночью и шторой
    x0, y0, x1, y1 = -520.0, -900.0, -290.0, -560.0
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    sky = lib.lin_grad([(0, "#1c2452", 1), (1, "#3b4a8c", 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    o.append(f'<g clip-path="url(#{c})"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{sky})"/>'
             f'<circle cx="{x0 + 160}" cy="{y0 + 80}" r="26" fill="#f6efc8"/><circle cx="{x0 + 172}" cy="{y0 + 72}" r="24" fill="#1f2858"/>'
             + "".join(f'<circle cx="{x0 + 30 + k * 47}" cy="{y0 + 40 + (k * 37) % 90}" r="2.4" fill="#fff7d6" opacity="{.5 + .5 * math.sin(t * 3 + k):.2f}"/>'
                       for k in range(5)) + "</g>")
    o.append(f'<path d="{lib.fill_d(R(x0 - 18, y0 - 18, x1 + 18, y1 + 18))}M{x0} {y0}H{x1}V{y1}H{x0}Z" fill="#f1e8d6" fill-rule="evenodd"/>')
    o.append(f'<path d="{lib.ink_closed(R(x0 - 18, y0 - 18, x1 + 18, y1 + 18), 3.6, seed=7001)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed(R(x0, y0, x1, y1), 3.0, seed=7002)}" fill="{INK}"/>')
    o.append(shape(R(x0, (y0 + y1) / 2 - 6, x1, (y0 + y1) / 2 + 6), "#f1e8d6", w=2.4, seed=7003))
    sw = 6 * math.sin(t * 1.2)
    cur = [(x1 - 40, y0 - 40), (x1 + 50, y0 - 40), (x1 + 60 + sw, -300), (x1 + 80 + sw, -120, 1), (x1 - 10 + sw, -120, 1), (x1 - 30, -400)]
    o.append(shape(cur, "#d7a64a", lib.blob([(x1 + 30, y0 - 40), (x1 + 50, y0 - 40), (x1 + 80 + sw, -120), (x1 + 50, -120)], "#b48433", .9) +
                   line([(x1, y0), (x1 + 10 + sw * .5, -300), (x1 + 20 + sw, -130)], 2.6, "#9c6f28", seed=7005, op=.8), w=3.6, seed=7004))
    o.append(line([(x0 - 60, y0 - 46), (x1 + 90, y0 - 46)], 7, "#5a3c26", seed=7006, taper=.1, wmin=.8))
    # картина над диваном (кот на подушке — силуэт, без букв)
    px0, py0, px1, py1 = 40.0, -760.0, 260.0, -590.0
    o.append(shape(R(px0, py0, px1, py1), "#4f2c18", w=3.4, seed=7010))
    inner = blob([(px0 + 14, py0 + 14), (px1 - 14, py0 + 14), (px1 - 14, py1 - 14), (px0 + 14, py1 - 14)], "#f2d38a")
    inner += blob([(px0 + 14, py1 - 50), (px1 - 14, py1 - 64), (px1 - 14, py1 - 14), (px0 + 14, py1 - 14)], "#e07a4f")
    inner += f'<circle cx="{px0 + 150}" cy="{py0 + 56}" r="24" fill="#fff4cf"/>'
    o.append(shape(R(px0 + 14, py0 + 14, px1 - 14, py1 - 14), "#f2d38a", inner, w=2.6, seed=7011))
    # плинтус
    o.append(shape(R(-1400, -40, 1800, 0), "#efe5d2", blob([(-1400, -12), (1800, -12), (1800, 0), (-1400, 0)], "#d4c6ac", .9), w=3, seed=7012))
    return "".join(o)


def floor_lamp(t):
    x, y = 640.0, 0.0
    o = [shape(ellipse_pts(x, y - 8, 60, 12, 14), "#2f2a2c", w=3, seed=7101),
         line([(x, y - 10), (x, -700)], 7, "#2f2a2c", seed=7102, taper=.05, wmin=.9)]
    gl = lib.rad_grad([(0, "#fff1c4", .9), (.4, "#ffe08a", .4), (1, "#ffe08a", 0)], x, -690, 260)
    o.append(f'<circle cx="{x}" cy="-690" r="260" fill="url(#{gl})"/>')
    o.append(shape([(x - 90, -680, 1), (x - 56, -820), (x + 56, -820), (x + 90, -680, 1)], "#f6e2b0",
                   blob([(x + 30, -820), (x + 56, -820), (x + 90, -680), (x + 50, -680)], "#e2c27e", .9), w=3.6, seed=7103))
    return "".join(o)


def floor():
    o = [lib.blob(R(-1400, 0, 1800, 1400), FLOOR)]
    vx, vy = 180, -900
    for k in range(-18, 22):
        xb = 180 + k * 120
        x0 = vx + (xb - vx) * (0 - vy) / (1400 - vy)
        o.append(line([(x0, 0), (xb, 1400)], 2.2, FLOOR_LN, seed=7200 + k, op=.6, taper=.1, wmin=.7))
    for k, y in enumerate((40, 120, 240, 400)):
        o.append(line([(-1400, y), (1800, y)], 1.6, FLOOR_SH, seed=7250 + k, op=.4))
    # ковёр
    rug = [(-260, 20, 1), (520, 20, 1), (600, 150, 1), (-340, 150, 1)]
    o.append(shape(rug, "#e2c58a", lib.blob([(-330, 120), (590, 120), (600, 150), (-340, 150)], "#c8a768", .9) +
                   line([(-230, 36), (500, 36), (566, 136), (-306, 136), (-230, 36)], 3, "#b0514a", seed=7261, op=.85), w=3.4, seed=7260))
    return "".join(o)


def sofa_back(t):
    """Спинка, подушки спинки, подлокотники, сиденье — всё, что за героем."""
    x0, x1 = SOFA_X
    o = []
    o.append(lib.blob(ellipse_pts((x0 + x1) / 2, 6, (x1 - x0) / 2 + 30, 22, 16), "#3a2418", .25))
    # спинка
    back = [(x0 + 30, BACK_Y + 30), (x0 + 70, BACK_Y), (x1 - 70, BACK_Y), (x1 - 30, BACK_Y + 30), (x1 - 20, SEAT_Y, 1), (x0 + 20, SEAT_Y, 1)]
    o.append(shape(back, SOFA_SH, lib.blob([(x0, BACK_Y), (x1, BACK_Y), (x1, BACK_Y + 26), (x0, BACK_Y + 26)], SOFA_DK, .5), w=4.4, seed=7301))
    # подушки спинки
    n = 2
    cw = (x1 - x0 - 2 * ARM_W) / n
    for k in range(n):
        a = x0 + ARM_W + k * cw
        cus = [(a + 8, BACK_Y + 30), (a + cw - 8, BACK_Y + 30), (a + cw - 2, SEAT_Y - 10, 1), (a + 2, SEAT_Y - 10, 1)]
        o.append(shape(cus, SOFA, lib.blob([(a + cw * .7, BACK_Y + 30), (a + cw, BACK_Y + 30), (a + cw, SEAT_Y), (a + cw * .75, SEAT_Y)], SOFA_SH, .7) +
                       line([(a + cw * .3, BACK_Y + 80), (a + cw * .5, BACK_Y + 100), (a + cw * .7, BACK_Y + 84)], 2.4, SOFA_DK, seed=7310 + k, op=.7),
                       w=4.0, seed=7311 + k))
    # подлокотники
    for k, ax in enumerate((x0, x1 - ARM_W)):
        arm = [(ax, ARM_Y + 20), (ax + 10, ARM_Y - 6), (ax + ARM_W - 10, ARM_Y - 6), (ax + ARM_W, ARM_Y + 20), (ax + ARM_W, -50, 1), (ax, -50, 1)]
        o.append(shape(arm, SOFA, lib.blob([(ax, ARM_Y + 30), (ax + ARM_W, ARM_Y + 30), (ax + ARM_W, -50), (ax, -50)], SOFA_SH, .55) +
                       lib.blob([(ax + 8, ARM_Y), (ax + ARM_W - 8, ARM_Y), (ax + ARM_W - 8, ARM_Y + 16), (ax + 8, ARM_Y + 16)], SOFA_HI, .8),
                       w=4.4, seed=7320 + k))
    # сиденье: подушки сверху и фартук спереди
    for k in range(n):
        a = x0 + ARM_W + k * cw
        top = [(a + 2, SEAT_Y - 8), (a + cw - 2, SEAT_Y - 8), (a + cw + 2, SEAT_Y + 34, 1), (a - 2, SEAT_Y + 34, 1)]
        o.append(shape(top, SOFA_HI, lib.blob([(a, SEAT_Y + 18), (a + cw, SEAT_Y + 18), (a + cw, SEAT_Y + 36), (a, SEAT_Y + 36)], SOFA, .9),
                       w=3.8, seed=7330 + k))
    o.append(shape(R(x0 + ARM_W - 4, SEAT_Y + 34, x1 - ARM_W + 4, -50), SOFA_SH,
                   lib.blob([(x0, SEAT_Y + 34), (x1, SEAT_Y + 34), (x1, SEAT_Y + 52), (x0, SEAT_Y + 52)], SOFA_DK, .6), w=4.2, seed=7340))
    for k, lx in enumerate((x0 + 20, x1 - 40)):
        o.append(shape(R(lx, -52, lx + 20, -4), "#4f2c18", w=2.6, seed=7350 + k))
    return "".join(o)


def plaid(pts_top, drop=120.0, seed=0, op=1.0):
    """Плед в клетку: верхний край по точкам pts_top (слева направо, по ногам), свисает вниз на drop с бахромой."""
    top = [tuple(p[:2]) for p in pts_top]
    bot = [(x + 10 * math.sin(i * 1.7), y + drop + 14 * math.sin(i * 2.3)) for i, (x, y) in enumerate(top)]
    poly = top + bot[::-1]
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs) - 20, max(xs) + 20, min(ys) - 20, max(ys) + 20
    inner = []
    for k in range(int((x1 - x0) / 46) + 1):         # вертикальные полосы клетки
        x = x0 + k * 46
        inner.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="16" height="{y1 - y0:.1f}" fill="#7c2a28" opacity=".55"/>')
    for k in range(int((y1 - y0) / 46) + 1):
        y = y0 + k * 46
        inner.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{x1 - x0:.1f}" height="16" fill="#7c2a28" opacity=".55"/>')
        inner.append(f'<rect x="{x0:.1f}" y="{y + 26:.1f}" width="{x1 - x0:.1f}" height="4" fill="#f3e2b8" opacity=".7"/>')
    inner.append(lib.blob([(x0, (y0 + y1) / 2 + 20), (x1, (y0 + y1) / 2 + 20), (x1, y1), (x0, y1)], "#5a1c1c", .25))
    # складки
    for i in range(1, len(top) - 1, 2):
        x, y = top[i]
        inner.append(line([(x, y + 10), (x + 6, y + drop * .6)], 2.6, "#5a1c1c", seed=seed + 40 + i, op=.6))
    o = [f'<g opacity="{op:.3f}">', shape(poly, "#c8463c", "".join(inner), w=4.2, seed=seed)]
    for i, (x, y) in enumerate(bot):                  # бахрома
        if i % 1 == 0:
            o.append(line([(x - 6, y), (x - 8, y + 16)], 2.4, "#c8463c", seed=seed + 80 + i, taper=.2))
            o.append(line([(x + 6, y), (x + 5, y + 16)], 2.4, "#c8463c", seed=seed + 120 + i, taper=.2))
    o.append("</g>")
    return "".join(o)


def mug(x, y, k=1.0, steam_t=None, tilt=0.0):
    """Кружка чая (вид сбоку, ручка слева): x, y — центр дна (любые координаты, k — масштаб)."""
    def T(p):
        return (x + p[0] * k, y + p[1] * k) + ((1,) if len(p) > 2 else ())
    o = []
    hd = [T((-40, -70)), T((-66, -66)), T((-70, -40)), T((-60, -22)), T((-40, -20))]
    o.append(line(hd, 11, INK, seed=7501, taper=.1, wmin=.85))
    o.append(line(hd, 6, "#f0e6d4", seed=7502, taper=.1, wmin=.85))
    body = [T((-42, -92, 1)), T((42, -92, 1)), T((40, -8)), T((30, 0, 1)), T((-30, 0, 1)), T((-40, -8))]
    inner = lib.blob([T(p) for p in [(14, -92), (46, -92), (44, 0), (14, 0)]], "#d9cbb4", .9)
    inner += lib.blob([T(p) for p in [(-46, -66), (46, -66), (46, -50), (-46, -50)]], "#3f7a72")
    o.append(shape(body, "#f0e6d4", inner, w=3.8, seed=7503))
    o.append(shape(ellipse_pts(x, y - 92 * k, 42 * k, 9 * k, 14), "#f0e6d4", lib.blob(ellipse_pts(x, y - 91 * k, 36 * k, 6 * k, 12), "#8a4a24"),
                   w=3.0, seed=7504))
    if steam_t is not None:
        for j in range(2):
            ph = steam_t * .9 + j * .5
            u = ph % 1.0
            a = math.sin(math.pi * u)
            sx = x + (-10 + j * 20) * k
            pts = [(sx, y - 108 * k - u * 30 * k), (sx + 10 * k * math.sin(ph * 6), y - 140 * k - u * 40 * k),
                   (sx - 6 * k * math.sin(ph * 5), y - 172 * k - u * 50 * k)]
            o.append(line(pts, 6 * k, "#ffffff", seed=7510 + j, op=.55 * a, taper=.3, wmin=.2))
    g = "".join(o)
    if tilt:
        g = f'<g transform="rotate({tilt:.2f} {x:.1f} {y:.1f})">{g}</g>'
    return g


def remote(x, y, ang=0.0, k=1.0, lit=0.0):
    pts = [(-46, -11, 1), (46, -11, 1), (46, 11, 1), (-46, 11, 1)]
    inner = "".join(f'<circle cx="{-24 + j * 16}" cy="0" r="3.6" fill="#8b8f9c"/>' for j in range(4))
    inner += f'<circle cx="36" cy="0" r="5" fill="#e04a3a"/>'
    o = shape(pts, "#2a2c34", inner, w=3.0, seed=7601)
    if lit > 0:
        o += f'<circle cx="52" cy="0" r="{8 + 10 * lit:.1f}" fill="#ff8a7a" opacity="{.5 * lit:.2f}"/>'
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.2f}) scale({k})">{o}</g>'


def back(t, tv=0.0):
    return wall(t, tv) + floor_lamp(t) + floor()


def vignette(op=0.3):
    g = lib.rad_grad([(0, "#1a1020", 0), (.7, "#1a1020", 0), (1, "#1a1020", op)], 540, 900, 1200, 1500)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'
