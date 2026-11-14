"""Сцена piggy рилса 44: копилка-кот (одна и та же во всех трёх планах).
s15 (31.0–33.45, клип 30.8–33.65): стена Димы днём, слева календарь-месяц, на «пятницу» (31.04) красный маркер обводит
     «ПТ» и все пятницы; справа на полке копилка-кот; на «откладываю» (31.52) рука сверху опускает монету в прорезь, копилка
     подпрыгивает, искры; на «заказа» (32.8) рядом маленький пакет доставки зачёркивается красным.
s16 (33.45–35.3, клип 33.25–35.5): копилка крупнее на полке, рядом растёт столбик монет; на «растёт» (34.56) копилка
     надувается и становится больше, на ней шлёпается наклейка с Фудзи; камера отъезжает.
s17 (35.3–37.4, клип 35.1–37.6): настоящий кот (cat.py рилса 41: ЛЕВОЕ ухо загнуто, огонёк) сидит на полке рядом с
     копилкой, которая уже больше него; на «косится» (36.72) медленно косит глаза на копилку и прищуривается, ухо
     дёргается, хвост с огоньком подёргивается.
Копилка — рыжевато-кремовая керамика: глянцевый блик, нарисованные глаза-точки, прорезь на спине, без огонька."""
import math

import numpy as np

import calbase
import cat as Cat
import lib
import props
from c44 import hand_text, kick, shake, wt
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad,
                 rect_pts, shape, smooth, svg)
from parts import sausage

_ST = {}
T_PT = wt("пятницу")         # 31.04
T_OTKL = wt("откладываю")    # 31.52
T_ZAK = wt("заказа")         # 32.8
T_KOP = wt("копилка")        # 33.573
T_RAST = wt("растёт")        # 34.56
T_NAST = wt("настоящий")     # 35.44
T_KOS = wt("косится")        # 36.72
CER, CER_SH, CER_HI, CER_DK = "#f3c48e", "#d9965a", "#fff4e2", "#b8743e"
SKIN, SKIN_SH, SKIN_SH2 = "#ecc4a2", "#d39f83", "#bf8a74"
HOOD, HOOD_SH, FOLD = "#d4a23e", "#a97b25", "#6b4a12"
GOLD, GOLD_SH, GOLD_HI = "#f2c232", "#c9921a", "#fff0a0"
SHELF_Y = 1150


# ───────────────────────── копилка-кот
def piggy(sticker=0.0, slot_glow=0.0, sd=7000):
    """Копилка в своих координатах: низ (0, 0), рост ~400. sticker 0..1 — наклейка с Фудзи (вылет)."""
    o = []
    o.append(blob(ellipse_pts(10, 4, 190, 22, 16), "#2a1608", .3, blur(8)))
    # хвостик-завиток, нарисованный на керамике сзади справа
    tail = [(150, -40), (210, -60), (226, -120), (200, -160), (176, -146), (196, -120), (186, -84), (146, -70)]
    o.append(shape(tail, CER, blob([(196, -120), (226, -120), (210, -60), (186, -84)], CER_SH, .8), w=4.4, seed=sd))
    body = [(-170, -20), (-176, -120), (-150, -220), (-110, -270), (0, -286), (110, -270), (150, -220), (176, -120), (170, -20), (120, 0, 1),
            (-120, 0, 1)]
    inner = blob([(60, -280), (150, -220), (176, -120), (170, -20), (120, 0), (30, 0), (110, -140)], CER_SH, .85)
    inner += blob(ellipse_pts(-20, -60, 90, 40, 14), "#fbe3c0", .8)
    # лапки, нарисованные краской
    for dx in (-60, 40):
        inner += shape(ellipse_pts(dx, -14, 38, 20, 12), "#fbe3c0", "", w=3, seed=sd + 3 + dx)
        inner += line([(dx - 8, -24), (dx - 8, -8)], 2.2, CER_DK, seed=sd + 5 + dx, op=.8)
        inner += line([(dx + 8, -24), (dx + 8, -8)], 2.2, CER_DK, seed=sd + 6 + dx, op=.8)
    o.append(shape(body, CER, inner, w=5.2, seed=sd + 10))
    # голова
    hd = [(-140, -300), (-120, -380), (-60, -416), (60, -416), (120, -380), (140, -300), (110, -250), (0, -236), (-110, -250)]
    for sx in (-1, 1):
        ear = [(sx * 70, -404, 1), (sx * 116, -480, 1), (sx * 136, -360, 1)]
        o.append(shape(ear, CER, blob([(sx * 88, -398), (sx * 114, -458), (sx * 124, -378)], "#f2a0a0", .9), w=4.6, seed=sd + 20 + sx))
    hin = blob([(40, -414), (120, -380), (140, -300), (110, -250), (40, -246), (90, -320)], CER_SH, .8)
    # нарисованные глаза-точки, носик, улыбка, румянец
    for sx in (-1, 1):
        hin += f'<circle cx="{sx * 50}" cy="-330" r="13" fill="#2a2230"/>'
        hin += f'<circle cx="{sx * 50 - 4}" cy="-335" r="4" fill="#ffffff"/>'
        hin += blob(ellipse_pts(sx * 86, -292, 18, 10, 10), "#f29a8a", .8)
    hin += shape([(-10, -306), (10, -306), (0, -294)], "#e0706a", "", w=2, seed=sd + 30)
    hin += line([(-22, -284), (-11, -276), (0, -286), (11, -276), (22, -284)], 3.4, "#2a2230", seed=sd + 31)
    for sx in (-1, 1):
        for j in range(2):
            hin += line([(sx * 100, -300 + j * 14), (sx * 140, -306 + j * 18)], 2.4, CER_DK, seed=sd + 40 + j + sx, op=.9)
    o.append(shape(hd, CER, hin, w=5.2, seed=sd + 50))
    # прорезь на макушке-спине
    o.append(shape(rect_pts(-46, -432, 46, -416, 8), "#2a1810", "", w=3, seed=sd + 60) if False else "")
    slot = [(-50, -421, 1), (50, -421, 1), (46, -409, 1), (-46, -409, 1)]
    o.append(shape(slot, "#3a2216", "", w=3.2, seed=sd + 61))
    if slot_glow > 0.01:
        o.append(f'<ellipse cx="0" cy="-415" rx="{f(60 + 30 * slot_glow)}" ry="{f(14 + 8 * slot_glow)}" fill="none" stroke="#ffe27a" '
                 f'stroke-width="{f(7 * slot_glow)}"/>')
    # глянцевые блики — керамика
    o.append(line([(-130, -180), (-136, -120), (-126, -70)], 14, CER_HI, taper=.6, seed=sd + 70))
    o.append(line([(-96, -390), (-72, -404)], 10, CER_HI, taper=.6, seed=sd + 71))
    o.append(f'<circle cx="-142" cy="-226" r="7" fill="{CER_HI}"/>')
    if sticker > 0.01:
        k = sticker
        o.append(f'<g transform="translate(36 -140) rotate(-8) scale({f(k)})">' + fuji_sticker(sd + 80) + "</g>")
    return "".join(o)


def fuji_sticker(sd):
    pts = [(-62, -46, 1), (62, -46, 1), (62, 46, 1), (-62, 46, 1)]
    inner = blob(rect_pts(-70, -50, 70, 50), "#cfe6f6")
    inner += f'<circle cx="34" cy="-22" r="13" fill="#e0352b"/>'
    inner += blob([(-60, 46), (-14, -22), (14, -22), (60, 46)], "#6f8fb8")
    inner += blob([(-24, -8), (-14, -22), (14, -22), (24, -8), (10, -2), (0, -10), (-10, -2)], "#ffffff")
    inner += blob(rect_pts(-70, 34, 70, 50), "#f4b6c8")
    o = shape(rect_pts(-66, -50, 66, 50, 12), "#ffffff", "", w=3.4, seed=sd)
    o += shape(pts, "#cfe6f6", inner, w=2.6, seed=sd + 1)
    return o


def piggy_at(x, y, k, rot=0.0, sqx=1.0, sqy=1.0, **kw):
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(k * sqx)} {f(k * sqy)})">{piggy(**kw)}</g>')


def coin(x, y, k=1.0, edge=0.0, sd=7300):
    """Монета: edge 0 — лицом, 1 — ребром (тонкая вертикальная)."""
    rx = 40 * k * (1 - 0.82 * edge)
    o = shape(ellipse_pts(x, y, rx, 40 * k, 18), GOLD, blob(ellipse_pts(x + rx * .25, y + 8 * k, rx * .7, 30 * k, 14), GOLD_SH, .7), w=3.2, seed=sd)
    if edge < 0.6:
        o += f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rx * .62)}" ry="{f(25 * k)}" fill="none" stroke="{GOLD_SH}" stroke-width="{f(3 * k)}"/>'
    o += line([(x - rx * .4, y - 22 * k), (x - rx * .55, y + 4 * k)], 4 * k, GOLD_HI, taper=.5, seed=sd + 1)
    return o


def coin_side(x, y, k, sd):
    """Монета в столбике: вид сбоку-сверху (эллипс с ребром)."""
    o = shape([(x - 44 * k, y - 8 * k), (x - 44 * k, y + 6 * k), (x, y + 14 * k), (x + 44 * k, y + 6 * k), (x + 44 * k, y - 8 * k), (x, y - 16 * k)], GOLD_SH,
              "", w=2.6, seed=sd)
    o += shape(ellipse_pts(x, y - 8 * k, 44 * k, 9 * k, 16), GOLD, line([(x - 24 * k, y - 10 * k), (x + 10 * k, y - 13 * k)], 2.4 * k, GOLD_HI, seed=sd + 1),
               w=2.6, seed=sd + 2)
    return o


def sparkle(x, y, r, u, sd, col="#ffd84a"):
    if u <= 0 or u >= 1:
        return ""
    o = []
    for j in range(5):
        a = -math.pi / 2 + (j - 2) * 0.55
        r0, r1 = r * (0.8 + 0.6 * u), r * (1.2 + 0.9 * u)
        o.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 9 * (1 - u) + 2, col,
                      taper=.5, seed=sd + j))
    return "".join(o)


# ───────────────────────── фон
def wall():
    return calbase.wallpaper() + f'<rect x="-2600" y="-2600" width="6000" height="6000" fill="#fff2d8" opacity=".12"/>'


def shelf(x0=-400, x1=1500):
    s = []
    s.append(blob(rect_pts(x0, SHELF_Y + 30, x1, SHELF_Y + 80), "#1d2412", .3, blur(10)))
    s.append(shape(rect_pts(x0, SHELF_Y, x1, SHELF_Y + 40), "#b07a4a", blob(rect_pts(x0, SHELF_Y + 24, x1, SHELF_Y + 40), "#7f4b2b") +
                   line([(x0, SHELF_Y + 8), (x1, SHELF_Y + 8)], 3, "#d29a66", taper=.05, wmin=.9, seed=7401, op=.8), w=4.6, seed=7402))
    s.append(f'<rect x="{x0}" y="{SHELF_Y + 40}" width="{x1 - x0}" height="2000" fill="#7a5a3e"/>')
    s.append(f'<rect x="{x0}" y="{SHELF_Y + 40}" width="{x1 - x0}" height="2000" fill="#3a2a1e" opacity=".35"/>')
    s.append(line([(x0, SHELF_Y + 300), (x1, SHELF_Y + 300)], 3, "#5a3e28", taper=.05, wmin=.9, seed=7403, op=.8))
    return "".join(s)


def small_plant(x, y, t, sd):
    return props.pot(x, y, 0.8, sd, leaves=6, col="#5aa0a0", t=t) if hasattr(props, "pot") else ""


# ───────────────────────── s15
CAL = calbase.Sheet(3, (130, 340, 570, 800), sd=7500)
PIG15 = (790, SHELF_Y, 0.78)
BAG = (390, SHELF_Y)


def red_ring(cx, cy, rx, ry, u, sd, w=8):
    if u <= 0:
        return ""
    n = 22
    pts = []
    for j in range(int(n * 1.1 * u) + 2):
        a = -2.4 + 2 * math.pi * j / n
        rr = 1 + 0.05 * math.sin(j * 1.7 + sd)
        pts.append((cx + rx * rr * math.cos(a), cy + ry * rr * math.sin(a)))
    return line(pts, w, "#e0352b", taper=.3, wmin=.5, seed=sd)


def calendar15(t):
    s = [CAL.shadow(), _ST["calpage"]]
    k = CAL.k
    # «ПТ» в шапке и все пятницы
    u = ease_out(clamp((t - T_PT + 0.04) / 0.22), 2)
    cx = CAL.x0 + 20 * k + CAL.cw * 4.5
    s.append(red_ring(cx, CAL.y0 + 232 * k, CAL.cw * .55, 26 * k, u, 7601, 7))
    for j, d in enumerate([d for d in range(1, CAL.n + 1) if (CAL.col0 + d - 1) % 7 == 4]):
        uu = ease_out(clamp((t - T_PT - 0.12 - j * 0.07) / 0.16), 2)
        x, y = CAL.cell(d)
        s.append(red_ring(x, y, CAL.cw * .42, CAL.rh * .4, uu, 7610 + j, 5.5))
    return "".join(s)


def bag(x, y, cross_u, sd=7700):
    """Пакет доставки (крафт, с оранжевой наклейкой-значком тарелки) и красный крест по нему."""
    o = [blob(ellipse_pts(x + 10, y + 2, 110, 14, 14), "#2a1608", .3, blur(6))]
    body = [(x - 90, y, 1), (x - 80, y - 200, 1), (x + 80, y - 200, 1), (x + 90, y, 1)]
    inner = blob([(x + 30, y - 200), (x + 80, y - 200), (x + 90, y), (x + 30, y)], "#b08050", .8)
    inner += shape(ellipse_pts(x, y - 100, 36, 36, 14), "#f0782e", line([(x - 18, y - 96), (x + 18, y - 96)], 4, "#ffffff", seed=sd + 3) +
                   line([(x - 14, y - 104), (x - 4, y - 120)], 3, "#ffffff", seed=sd + 4) + line([(x + 2, y - 104), (x + 12, y - 120)], 3, "#ffffff", seed=sd + 5),
                   w=3, seed=sd + 2)
    o.append(shape(body, "#d1a06a", inner, w=4.2, seed=sd))
    o.append(shape([(x - 80, y - 200, 1), (x - 66, y - 226, 1), (x + 66, y - 226, 1), (x + 80, y - 200, 1)], "#c08e58", "", w=3.6, seed=sd + 1))
    o.append(line([(x - 40, y - 214), (x - 30, y - 270), (x + 30, y - 270), (x + 40, y - 214)], 7, "#8a5a34", taper=.1, wmin=.8, seed=sd + 6))
    if cross_u > 0:
        a = clamp(cross_u / 0.5)
        b = clamp((cross_u - 0.5) / 0.5)
        p0, p1 = (x - 120, y - 260), (x + 120, y + 20)
        q0, q1 = (x + 120, y - 260), (x - 120, y + 20)
        if a > 0.03:
            o.append(line([p0, (p0[0] + (p1[0] - p0[0]) * a, p0[1] + (p1[1] - p0[1]) * a)], 26, "#e0352b", taper=.35, wmin=.5, seed=sd + 10))
        if b > 0.03:
            o.append(line([q0, (q0[0] + (q1[0] - q0[0]) * b, q0[1] + (q1[1] - q0[1]) * b)], 26, "#e0352b", taper=.35, wmin=.5, seed=sd + 11))
    return "".join(o)


def drop_hand(x, y, open_u, sd=7800):
    """Рука сверху держит монету кончиками пальцев (ладонь вниз, рукав уходит вверх-вправо). Запястье (x, y), пальцы вниз."""
    o = []
    # рукав
    sl = [(x + 40, y - 40), (x + 330, y - 640), (x + 560, y - 560), (x + 140, y + 30)]
    o.append(shape(sl, HOOD, blob([(x + 100, y), (x + 470, y - 590), (x + 560, y - 560), (x + 140, y + 30)], HOOD_SH, .85) +
                   line([(x + 140, y - 200), (x + 300, y - 470)], 4, FOLD, seed=sd + 1, op=.7), w=5, seed=sd + 2))
    cuff = [(x + 20, y - 30), (x + 70, y - 90), (x + 170, y - 10), (x + 130, y + 50)]
    o.append(shape(cuff, HOOD_SH, "".join(line([(x + 50 + k * 22, y - 60 + k * 14), (x + 30 + k * 22, y - 30 + k * 14)], 3, FOLD, seed=sd + 3 + k, op=.8)
                                       for k in range(5)), w=4.4, seed=sd + 9))
    # ладонь (тыл), пальцы вниз-влево
    pal = [(x - 20, y - 50), (x + 70, y - 20), (x + 60, y + 70), (x + 10, y + 110), (x - 60, y + 80), (x - 70, y + 10)]
    fing = []
    spread = 6 * open_u
    for j, (bx, by) in enumerate(((x - 50, y + 70), (x - 22, y + 92), (x + 8, y + 100), (x + 36, y + 90))):
        L = [74, 84, 80, 64][j]
        a = math.radians(100 + (j - 1.5) * (8 + spread))
        tip = (bx + L * math.cos(a) - 6 * (1 - open_u) * (j - 1.5), by + L * math.sin(a))
        fing.append(shape(sausage([(bx, by - 10), ((bx + tip[0]) / 2, (by + tip[1]) / 2 + 4), tip], 32, 28), SKIN,
                          blob(sausage([(bx + 6, by), (tip[0] + 6, tip[1])], 12, 10), SKIN_SH, .6), w=3.6, seed=sd + 20 + j))
    th = [(x - 50, y - 10), (x - 90, y + 40), (x - 92 - 10 * open_u, y + 100)]
    o.append(shape(sausage(th, 38, 30), SKIN, "", w=3.8, seed=sd + 30))
    o += fing
    o.append(shape(pal, SKIN, blob([(x + 20, y + 40), (x + 60, y + 70), (x + 10, y + 110), (x - 30, y + 90)], SKIN_SH, .8), w=4.4, seed=sd + 31))
    for j, (bx, by) in enumerate(((x - 50, y + 64), (x - 22, y + 84), (x + 8, y + 92), (x + 36, y + 82))):
        o.append(line([(bx - 8, by - 4), (bx, by + 2), (bx + 8, by - 4)], 2.4, SKIN_SH2, seed=sd + 40 + j, op=.8))
    return "".join(o)


def s15(t):
    s = [_ST["wall"]]
    s.append(calendar15(t))
    s.append(_ST["shelf"])
    # пакет и крест
    cu = clamp((t - T_ZAK + 0.02) / 0.3)
    bag_pop = 1 + 0.12 * math.exp(-max(0, t - T_ZAK - 0.3) * 9) * math.sin(max(0, t - T_ZAK - 0.3) * 30) * (t > T_ZAK + 0.3)
    s.append(f'<g transform="translate({BAG[0]} {BAG[1]}) scale({f(bag_pop)}) translate({-BAG[0]} {-BAG[1]})">{bag(BAG[0], BAG[1], cu)}</g>')
    # копилка: монета падает в прорезь
    px, py, pk = PIG15
    slot = (px, py - 415 * pk)
    land = T_OTKL + 0.28
    e = t - land
    hop, sq = 0.0, 0.0
    if e >= 0:
        hop = -26 * math.exp(-e * 7) * abs(math.sin(e * 16))
        sq = 0.08 * math.exp(-e * 9) * math.cos(e * 26)
    rot = 2 * math.sin(t * 2.0) * (1 if e < 0 else math.exp(-e * 2))
    glow = math.exp(-max(0, e) * 4) if e >= 0 else 0.0
    s.append(piggy_at(px, py + hop, pk, rot, 1 + sq, 1 - sq, slot_glow=glow))
    # монета: в руке до T_OTKL, потом падает ребром в прорезь (ниже прорези — спрятана внутри)
    hx0, hy0 = slot[0] + 40, slot[1] - 300
    hand_in = ease_out(clamp((t - 30.8) / 0.5), 3)
    hand_out = ease_in(clamp((t - T_OTKL - 0.2) / 0.4), 2)
    hx = hx0 + 400 * (1 - hand_in) + 360 * hand_out
    hy = hy0 - 500 * (1 - hand_in) - 520 * hand_out + 6 * math.sin(t * 5)
    tip = (hx - 8, hy + 190)
    if t < T_OTKL:
        s.append(coin(tip[0], tip[1], 0.9, edge=0.15))
    else:
        q = t - T_OTKL
        cy = tip[1] + 0.5 * 5200 * q * q
        cx = tip[0] + (slot[0] - tip[0]) * clamp(q / 0.28)
        edge = clamp(q / 0.2)
        if cy < slot[1] + 60:
            c = lib.clip_rect(cx - 80, cy - 200, 160, max(0.0, slot[1] + hop - (cy - 200) - 6))
            s.append(f'<g clip-path="url(#{c})">{coin(cx, cy, 0.9, edge=edge)}</g>')
    s.append(sparkle(slot[0], slot[1] + hop - 10, 60, (t - land) / 0.4, 7900))
    if hand_out < 1:
        s.append(drop_hand(hx, hy, clamp((t - T_OTKL) / 0.12)))
    return "".join(s)


def cam15(t):
    u = clamp((t - 30.8) / 2.85)
    k1, r1 = kick(t, [T_OTKL + 0.28], 0.04, 10)
    k2, r2 = kick(t, [T_ZAK + 0.3], 0.03, 10)
    k3, r3 = kick(t, [T_PT], 0.02, 12)
    v = ease_io(clamp((t - T_OTKL) / 0.6)) * (1 - ease_io(clamp((t - 32.5) / 0.4)))
    cx = 560 + 140 * v + 10 * math.sin(t * 1.3)
    cy = 820 + 90 * v
    sc = (1.12 + 0.05 * u) * (1 + 0.16 * v)
    return cam(cx, cy, sc * k1 * k2 * k3, r1 + r2 + r3 - 0.8 + 1.2 * u)


# ───────────────────────── s16
PIG16 = (600, SHELF_Y)
STACK16 = (250, SHELF_Y)


def coins_n(t):
    return int(clamp((t - 33.3) / 1.9) * 12) + 1


def s16(t):
    s = [_ST["wall"], _ST["shelf"]]
    # столбик монет растёт: каждая монета падает сверху и садится
    n = coins_n(t)
    st = []
    for j in range(n):
        y = STACK16[1] - 6 - j * 22
        tj = 33.3 + j * 1.9 / 12
        q = t - tj
        dy = -260 * (1 - ease_in(clamp(q / 0.12), 2)) if q < 0.12 else 0.0
        st.append(coin_side(STACK16[0], y + dy, 1.4, 8000 + j))
    s.append("".join(st))
    # копилка надувается на «растёт»
    e = t - T_RAST
    k = 0.92
    sqx = sqy = 1.0
    if e > -0.1:
        g = ease_out(clamp((e + 0.1) / 0.3), 2)
        k = 0.92 + 0.38 * g
        q = max(0.0, e - 0.2)
        wob = 0.07 * math.exp(-q * 6) * math.sin(q * 24) * (e > 0.2)
        sqx, sqy = 1 + wob, 1 - wob
    breathe = 1 + 0.012 * math.sin(t * 5)
    stick = 0.0
    if t > T_RAST + 0.4:
        q = t - T_RAST - 0.4
        stick = 1.6 - 0.6 * ease_out(clamp(q / 0.1)) if q < 0.1 else 1 - 0.08 * math.exp(-q * 9) * math.cos(q * 26)
    s.append(piggy_at(PIG16[0], PIG16[1], k * breathe, 1.5 * math.sin(t * 1.6), sqx, sqy, sticker=stick))
    if T_RAST <= t < T_RAST + 0.5:
        s.append(props.burst(PIG16[0], PIG16[1] - 260 * k, 2.6, (t - T_RAST) / 0.5, seed=8100, n=8, r0=160, r1=220))
    return "".join(s)


def cam16(t):
    u = clamp((t - 33.25) / 2.25)
    k1, r1 = kick(t, [T_RAST], 0.05, 9)
    sc = 1.45 - 0.33 * ease_io(u)
    return cam(520 + 20 * u, 900 - 40 * u, sc * k1, r1 + 1.0 - 1.8 * u)


# ───────────────────────── s17
CAT17 = (330, SHELF_Y + 4, 1.0)
PIG17 = (760, SHELF_Y, 1.3)


def s17(t):
    s = [_ST["wall"], _ST["shelf"]]
    x, y, sc = CAT17
    s.append(piggy_at(PIG17[0], PIG17[1], PIG17[2], 1.0 * math.sin(t * 1.4), sticker=1.0))
    # кот: смотрит в камеру, на «косится» глаза медленно уходят вправо на копилку, прищур
    side = ease_io(clamp((t - T_KOS + 0.1) / 0.45))
    look = (0.05 * math.sin(t * .9) + 0.95 * side, -0.05 + 0.1 * side)
    blink = 0.38 * side
    for c in (35.6,):
        a = c - 0.06
        if a <= t <= c + 0.06:
            blink = max(blink, ease_io((t - a) / .06) if t < c else 1 - ease_io((t - c) / .06))
    tilt = -1.2 + 0.8 * math.sin(t * 1.3) - 3.5 * side
    flick = 0.0
    for c in (T_KOS + 0.35, T_KOS + 0.75):
        q = t - c
        if 0 <= q < 0.5:
            flick += -16 * math.exp(-q * 9) * math.sin(q * 34)
    tail = 6 * math.sin(t * 2.1) + 3 * math.sin(t * 3.7 + 1)
    if t > T_KOS:
        q = t - T_KOS
        tail += 9 * math.exp(-q * 2.5) * math.sin(q * 16)
    fx, fy = Cat.flame_world(x, y, sc, tail)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g = rad_grad([(0, "#ffb050", .3 * fl), (1, "#ffb050", 0)], fx, fy, 180, 180)
    s.append(f'<rect x="{fx - 200:.1f}" y="{fy - 200:.1f}" width="400" height="400" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(Cat.draw(x, y, sc, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick))
    return "".join(s)


def cam17(t):
    u = clamp((t - 35.1) / 2.5)
    k1, r1 = kick(t, [T_KOS], 0.02, 8)
    v = ease_io(clamp((t - T_KOS + 0.2) / 0.8))
    sc = 1.3 + 0.08 * ease_io(u) + 0.12 * v
    cx = 540 + (-70) * v
    return cam(cx, 900 - 30 * v, sc * k1, r1 + 0.6 - 1.0 * u)


def frame(sid, t):
    if not _ST:
        lib.DEFS.clear()
        lib.INK_K[0] = 1.0
        Cat.static_parts()
        _ST["wall"] = wall()
        _ST["shelf"] = shelf()
        _ST["calpage"] = CAL.board() + CAL.page() + CAL.rings()
        lib.static_done()
    lib.dyn_begin()
    art, cm = {"s15": (s15, cam15), "s16": (s16, cam16), "s17": (s17, cam17)}[sid]
    return svg(f'<rect width="{W}" height="{H}" fill="#9fae8e"/><g transform="{cm(t)}">{art(t)}</g>')


_ = (INK, H, hand_text, shake, np, mix, lin_grad, smooth, small_plant)
