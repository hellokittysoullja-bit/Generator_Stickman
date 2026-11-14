"""Сцена «странный факт» рилса 39 (s07 s08 s09): тёмно-синий фон (как сцена brain рилса 35), всё — функция общего
времени ролика t, удары — по voice/words.json.
s07 «А вот странный факт» (10.44–13.0): кот-ведущий в правом нижнем углу под пятном света машет указкой; на «странный»
    (11.04) из кончика указки выпрыгивает рукописная табличка «СТРАННЫЙ ФАКТ» с «?», на «факт» (11.44) — удар (вспышка
    лучей, тряска камеры, табличка впечатывается), кот округляет взгляд в камеру.
s08 «…делать два дела без потерь» (12.6–15.6): вверху две карточки-дела (документ «отчёт», наушники «созвон»), на «два»
    (13.2) между ними выскакивает «+»; под ними волной встаёт сетка 10×10 одинаковых серых человечков; медленный отъезд.
s09 «…примерно у двух человек из ста» (15.2–17.2): наезд к двум; на «двух» (15.52) два человечка вспыхивают золотом с
    искрами и короной-искрой, остальные темнеют; на «ста» (16.56) над ними надпись «2 из 100»."""
import math

import numpy as np

import cat
import lib
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape,
                 smooth, svg, T, DEFS)

_ST = {}
WT = {}
FLOOR = 1290


def word_t(w, k=0):
    if not WT:
        for x in lib.words():
            WT.setdefault(x["word"].strip(",.:?!").lower(), []).append(x["start"])
    return WT[w][k]


STRANGE = word_t("странный")      # 11.04
FACT = word_t("факт")             # 11.44
TWO = word_t("два")               # 13.2
DELA = word_t("дела", 0)          # 13.52
TWO_P = word_t("двух")            # 15.52
STA = word_t("ста")               # 16.56


# ───────────────────────── фон
def background():
    s = []
    lib.lin_grad([(0, "#1a2244", 1), (.55, "#26335f", 1), (1, "#2e3f74", 1)], 0, 0, 0, 1, gid="gWallF")
    lib.lin_grad([(0, "#33447a", 1), (1, "#1f2950", 1)], 0, 0, 0, 1, gid="gFloorF")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#gWallF)"/>')
    s.append(f'<rect x="-900" y="{FLOOR}" width="{W + 1800}" height="{H + 900}" fill="url(#gFloorF)"/>')
    rad_grad([(0, "#4e64a6", .75), (.6, "#3a4d8a", .28), (1, "#3a4d8a", 0)], 520, 760, 760, 700, gid="gSpotF")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#gSpotF)"/>')
    s.append(blob([(-900, FLOOR - 24), (W + 900, FLOOR - 24), (W + 900, FLOOR), (-900, FLOOR)], "#24305c"))
    s.append(line([(-900, FLOOR - 24), (W + 900, FLOOR - 24)], 2.6, INK, taper=.1, wmin=.8, seed=6, op=.8))
    s.append(line([(-900, FLOOR), (W + 900, FLOOR)], 4.5, INK, taper=.1, wmin=.8, seed=5))
    for k, y in enumerate([1380, 1520, 1720]):
        s.append(line([(-900, y), (W + 900, y + 6)], 2.4, "#1a2244", taper=.2, wmin=.6, seed=10 + k, op=.8))
    return "".join(s)


def dust(t):
    rs = np.random.RandomState(7)
    s = []
    for k in range(30):
        x0, y0 = rs.uniform(-200, W + 200), rs.uniform(-200, FLOOR - 40)
        sp, ph, r = rs.uniform(10, 26), rs.uniform(0, 6.28), rs.uniform(2.2, 4.5)
        x = x0 + 30 * math.sin(t * 0.6 + ph)
        y = (y0 - sp * (t - 10)) % (FLOOR + 160) - 180
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#c9d6ff" opacity="{.16 + .12 * math.sin(t * 2 + ph):.3f}"/>')
    return "".join(s)


def star(x, y, r, col="#ffe27a", sd=0, rot=0.0):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.32
        a = math.radians(rot + i * 45 - 90)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, col, "", w=max(1.6, r * 0.09), seed=sd)


def rays(x, y, e, sd, r=70, n=10, col="#ffe27a", dur=0.45, L0=60, w=10):
    if e < 0 or e > dur:
        return ""
    u = e / dur
    s = []
    for k in range(n):
        a = k * 2 * math.pi / n + .3
        r0 = r + 120 * ease_out(u)
        L = L0 * (1 - u)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))], w * (1 - .5 * u),
                      col, taper=.5, seed=sd + k))
    return "".join(s)


def text(x, y, txt, size, fill, font="IDB", weight=900, stroke=INK, sw=10, anchor="middle", shadow=True, extra=""):
    s = ""
    if shadow:
        s += (f'<text x="{f(x + size * .04)}" y="{f(y + size * .05)}" text-anchor="{anchor}" font-family="{font}" font-weight="{weight}" '
              f'font-size="{f(size)}" fill="{INK}">{txt}</text>')
    s += (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="{font}" font-weight="{weight}" font-size="{f(size)}" '
          f'fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}" paint-order="stroke" stroke-linejoin="round" {extra}>{txt}</text>')
    return s


# ───────────────────────── s07: кот-ведущий и табличка
CAT_X, CAT_Y, CAT_S = 800, FLOOR - 4, 1.32
SIGN = (540, 545)          # центр таблички


def sign(t):
    """Рукописная табличка: кремовый лист с загнутым уголком, «СТРАННЫЙ / ФАКТ» маркером, красный «?» сбоку."""
    e = t - STRANGE
    if e < 0:
        return ""
    k = back_out(clamp(e / 0.32), 2.4)
    hit = t - FACT
    kick = 0.0
    if hit >= 0:
        kick = 0.16 * math.exp(-hit * 9) * math.cos(hit * 26)
    sc = max(0.0, k) * (1 + kick)
    rot = -4 + 14 * (1 - clamp(e / 0.32)) + 2.2 * math.sin(t * 2.1)
    # выпрыгивает из кончика указки
    tip = pointer_tip_world(t)
    u = ease_out(clamp(e / 0.32), 3)
    cx, cy = tip[0] + (SIGN[0] - tip[0]) * u, tip[1] + (SIGN[1] - tip[1]) * u
    w, h = 680, 400
    s = []
    s.append(blob(rect_pts(-w / 2 + 22, -h / 2 + 30, w / 2 + 22, h / 2 + 30, 26), "#0c1028", .45, blur(10)))
    paper = [(-w / 2, -h / 2 + 8), (w / 2 - 6, -h / 2, 1), (w / 2, h / 2 - 70), (w / 2 - 62, h / 2 + 4, 1), (-w / 2 + 6, h / 2 - 4, 1)]
    inner = blob([(-w / 2, h / 2 - 60), (w / 2, h / 2 - 90), (w / 2, h / 2 + 10), (-w / 2, h / 2 + 10)], "#ecdcb6", .9)
    inner += blob([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, -h / 2 + 22), (-w / 2, -h / 2 + 30)], "#fffaee", .9)
    s.append(shape(paper, "#fbf1d8", inner, w=6, seed=701))
    # загнутый уголок
    s.append(shape([(w / 2, h / 2 - 70, 1), (w / 2 - 62, h / 2 + 4, 1), (w / 2 - 48, h / 2 - 56, 1)], "#dcc89e", "", w=4.4, seed=702))
    # скотч сверху
    s.append(shape(T(rect_pts(-70, -18, 70, 18, 3), 0, -h / 2 + 2, 1, -5), "#e8e2c8", "", w=3, seed=703, attrs='opacity=".92"'))
    # надпись маркером
    s.append(f'<text x="0" y="-24" text-anchor="middle" font-family="Shantell" font-weight="800" font-size="104" fill="{INK}" '
             f'transform="rotate(-3)">СТРАННЫЙ</text>')
    s.append(f'<text x="-70" y="120" text-anchor="middle" font-family="Shantell" font-weight="800" font-size="128" fill="#d8332e" '
             f'transform="rotate(-2)">ФАКТ</text>')
    s.append(line([(-230, 150), (-110, 160), (40, 152), (100, 146)], 9, "#d8332e", taper=.5, wmin=.25, seed=704))
    # большой «?»: подпрыгивает
    qb = 14 * abs(math.sin(t * 5.2)) if e > 0.4 else 0
    qk = 1 + (0.25 * math.exp(-hit * 7) * math.cos(hit * 22) if hit >= 0 else 0)
    s.append(f'<g transform="translate(205 {f(128 - qb)}) rotate({f(12 + 6 * math.sin(t * 3))}) scale({f(qk)})">'
             + text(0, 0, "?", 210, "#ffcf3a", font="Shantell", weight=800, sw=12) + "</g>")
    return f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({f(sc)})">{"".join(s)}</g>'


def paw_point(t):
    """Точка лапы (внутр. коорд. кота): машет указкой с первого кадра, на «странный» — выброс к табличке, на «факт» —
    стук-удар указкой."""
    base = np.array([724.0, 1112.0])
    wv = np.array([10 * math.sin(t * 7.5), 12 * math.sin(t * 7.5 + 1.2)])
    e = t - (STRANGE - 0.12)
    thr = 0.0
    if e > 0:
        thr = math.exp(-e * 3) * math.sin(min(e * 10, math.pi / 2))
    hit = t - FACT
    tap = 0.0
    if hit > -0.1:
        tap = math.exp(-max(hit, 0) * 8) * (1 - abs(min(hit, 0)) / 0.1)
    P = base + wv * (1 - .7 * smooth(STRANGE, STRANGE + .3, t)) + np.array([-34, -30]) * thr + np.array([-10, 22]) * tap
    return tuple(P)


def pointer_dir(t):
    """Угол указки (градусы, мир): вверх-влево к табличке, качается."""
    a = -142 + 6 * math.sin(t * 7.5 + .4) * (1 - .7 * smooth(STRANGE, STRANGE + .3, t))
    hit = t - FACT
    if hit > -0.1:
        a += 10 * math.exp(-max(hit, 0) * 8) * (1 - abs(min(hit, 0)) / 0.1)
    return a


PTR_L = 330


def pointer_tip_world(t):
    P = cat.to_world(paw_point(t), CAT_X, CAT_Y, CAT_S)
    a = math.radians(pointer_dir(t))
    return (P[0] + math.cos(a) * PTR_L, P[1] + math.sin(a) * PTR_L)


def pointer(t):
    P = cat.to_world(paw_point(t), CAT_X, CAT_Y, CAT_S)
    a = math.radians(pointer_dir(t))
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    a0 = (P[0] - ux * 40, P[1] - uy * 40)
    b = (P[0] + ux * PTR_L, P[1] + uy * PTR_L)
    w0, w1 = 9, 5
    poly = [(a0[0] + nx * w0, a0[1] + ny * w0, 1), (b[0] + nx * w1, b[1] + ny * w1, 1), (b[0] - nx * w1, b[1] - ny * w1, 1),
            (a0[0] - nx * w0, a0[1] - ny * w0, 1)]
    s = shape(poly, "#c98f5a", blob([(a0[0], a0[1]), (b[0], b[1]), (b[0] - nx * w1, b[1] - ny * w1), (a0[0] - nx * w0, a0[1] - ny * w0)],
                                    "#a8723f", .9), w=3.6, seed=720)
    tip = [(b[0] - ux * 30 + nx * 7, b[1] - uy * 30 + ny * 7, 1), (b[0] + ux * 6 + nx * 7, b[1] + uy * 6 + ny * 7), (b[0] + ux * 12, b[1] + uy * 12),
           (b[0] + ux * 6 - nx * 7, b[1] + uy * 6 - ny * 7), (b[0] - ux * 30 - nx * 7, b[1] - uy * 30 - ny * 7, 1)]
    s += shape(tip, "#e5383b", "", w=3.6, seed=721)
    return s


def cat_s07(t):
    hit = t - FACT
    look = (-0.75, -0.75) if t < FACT + 0.25 else (0.0, 0.05)
    k = smooth(FACT + 0.15, FACT + 0.4, t)
    look = (-0.75 * (1 - k), -0.75 * (1 - k) + 0.05 * k)
    blink = 0.0
    for c, half in ((10.62, 0.07), (12.45, 0.08)):
        if c - half <= t <= c + half:
            blink = 1 - abs(t - c) / half
    tilt = -5 * math.sin(t * 2.4) * (1 - k) + 4 * k * math.sin((t - FACT) * 2.2)
    flick = 0.0
    for c in (STRANGE, FACT):
        e = t - c
        if 0 <= e < 0.5:
            flick += -14 * math.exp(-e * 9) * math.sin(e * 34)
    tail = 6 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1)
    bob = 6 * math.exp(-max(hit, 0) * 6) * math.sin(max(hit, 0) * 20) if hit > 0 else 0
    X, Y = CAT_X, CAT_Y + bob
    s = []
    # пятно света под котом — тёмный кот читается на тёмном фоне
    g = rad_grad([(0, "#7f95d6", .55), (.55, "#5a70b4", .22), (1, "#5a70b4", 0)], X + 40, Y - 220, 330, 300)
    s.append(f'<rect x="{f(X - 400)}" y="{f(Y - 640)}" width="900" height="760" fill="url(#{g})"/>')
    s.append(blob(ellipse_pts(X + 30, Y + 2, 230, 26, 16), "#141b38", .55, blur(8)))
    fx, fy = cat.flame_world(X, Y, CAT_S, tail)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g2 = rad_grad([(0, "#ffb050", .42 * fl), (1, "#ffb050", 0)], fx, fy, 260, 260)
    s.append(f'<rect x="{f(fx - 280)}" y="{f(fy - 280)}" width="560" height="560" fill="url(#{g2})" style="mix-blend-mode:screen"/>')
    s.append(cat.draw(X, Y, CAT_S, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw="none", shadow=False))
    s.append(pointer(t))
    press = 0.5 * math.exp(-max(hit, 0) * 8) if hit > 0 else 0
    s.append(f'<g transform="translate({X - cat.CX * CAT_S:.2f} {Y - cat.CBOT * CAT_S:.2f}) scale({CAT_S:.4f})">'
             f'{cat.leg_left(paw_point(t), press)}</g>')
    return "".join(s)


def sparkles07(t):
    s = []
    rs = np.random.RandomState(11)
    for k in range(9):
        x, y = rs.uniform(90, 990), rs.uniform(220, 1100)
        if 760 < x and y > 820:
            continue
        ph = rs.uniform(0, 6.28)
        r = 10 + 8 * (0.5 + 0.5 * math.sin(t * 4 + ph))
        s.append(star(x, y, r, "#ffe27a", 730 + k, rot=t * 40 + ph * 20))
    return "".join(s)


def s07(t):
    s = [_ST["bg"], dust(t), sparkles07(t)]
    s.append(rays(SIGN[0], SIGN[1], t - FACT, 760, r=380, n=14, L0=90, w=12))      # лучи под котом: не режут морду
    s.append(cat_s07(t))
    s.append(sign(t))
    # камера: влёт с первого кадра (сборщик даёт хлёст), толчок на «странный», удар на «факт»
    u = clamp((t - 10.44) / 0.5)
    sc = 1.0 + 0.12 * (1 - ease_out(u, 3)) + 0.03 * clamp((t - 10.9) / 2.1)
    cx, cy = 560 - 30 * (1 - ease_out(u, 3)), 860 + 40 * (1 - ease_out(u, 3))
    rot = -2.0 * (1 - ease_out(u, 3)) + 0.5 * math.sin(t * 1.1)
    e = t - STRANGE
    if e > 0:
        sc *= 1 + 0.03 * math.exp(-e * 8) * math.sin(min(e * 14, math.pi))
    e = t - FACT
    if e > 0:
        kk = math.exp(-e * 7)
        sc *= 1 + 0.06 * kk
        cx += 14 * kk * math.sin(e * 47)
        cy += 12 * kk * math.sin(e * 39)
        rot += 1.2 * kk * math.sin(e * 31)
    return cam(cx, cy, sc, rot), "".join(s)


# ───────────────────────── s08 / s09: карточки и сетка 10×10
GX0, GDX, GY0, GDY = 117, 94, 610, 70
GOLD = [(5, 3), (7, 6)]          # (ряд, колонка) двух «многозадачных»
PS = 1.05           # масштаб человечка в клетке


def gpos(r, c):
    return GX0 + c * GDX, GY0 + r * GDY


def person_def(gid, col, sh, sd):
    """Человечек: голова-кружок и плечи-купол, контур тушью, плоский цвет с одной тенью, точки-глаза."""
    body = [(-24, 0, 1), (-24, -14), (-18, -26), (0, -32), (18, -26), (24, -14), (24, 0, 1)]
    head = ellipse_pts(0, -46, 14.5, 14.5, 14)
    inb = blob([(6, -34), (26, -24), (26, 2), (10, 2)], sh, .9)
    inh = blob(ellipse_pts(6, -42, 9, 12, 10), sh, .85)
    g = (shape(body, col, inb, w=3.0, seed=sd) + shape(head, col, inh, w=3.0, seed=sd + 1)
         + f'<circle cx="-5" cy="-47" r="2.3" fill="{INK}"/><circle cx="5" cy="-47" r="2.3" fill="{INK}"/>')
    DEFS.append(f'<g id="{gid}">{g}</g>')


def doc_icon(x, y, sd):
    s = shape([(x - 46, y - 60, 1), (x + 22, y - 60, 1), (x + 46, y - 36, 1), (x + 46, y + 60, 1), (x - 46, y + 60, 1)], "#ffffff",
              blob([(x + 22, y - 60), (x + 46, y - 36), (x + 46, y + 60), (x + 30, y + 60), (x + 30, y - 40)], "#dfe5f2", .9), w=4, seed=sd)
    s += shape([(x + 22, y - 60, 1), (x + 22, y - 36, 1), (x + 46, y - 36, 1)], "#cfd6e8", "", w=3, seed=sd + 1)
    for k in range(5):
        ww = 60 if k % 2 else 46
        s += line([(x - 32, y - 30 + k * 18), (x - 32 + ww, y - 30 + k * 18)], 4, "#7e8bb0", taper=.1, wmin=.8, seed=sd + 3 + k)
    return s


def headphones_icon(x, y, sd):
    arc = [(x - 52 + 104 * u, y - 20 - 58 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 13)]
    s = line(arc, 15, INK, taper=.05, wmin=.9, seed=sd)
    s += line(arc, 7, "#5ec8f0", taper=.05, wmin=.9, seed=sd + 1)
    for sx in (-1, 1):
        s += shape(rect_pts(x + sx * 52 - 22, y - 32, x + sx * 52 + 22, y + 36, 16), "#3a4a86",
                   blob(rect_pts(x + sx * 52 + 4, y - 32, x + sx * 52 + 22, y + 36), "#2a3768", .9), w=4, seed=sd + 2 + (sx > 0))
        s += shape(rect_pts(x + sx * 30 - 6, y - 20, x + sx * 30 + 6, y + 24, 5), "#5ec8f0", "", w=3, seed=sd + 5 + (sx > 0))
    return s


def card(x, y, kind, label, sd, glow=0.0):
    w, h = 300, 250
    s = []
    s.append(blob(rect_pts(x - w / 2 + 14, y - h / 2 + 18, x + w / 2 + 14, y + h / 2 + 18, 30), "#0c1028", .45, blur(8)))
    if glow > 0.01:
        g = rad_grad([(0, "#ffe27a", .5 * glow), (1, "#ffe27a", 0)], x, y, 240, 200)
        s.append(f'<rect x="{f(x - 260)}" y="{f(y - 220)}" width="520" height="440" fill="url(#{g})"/>')
    inner = blob(rect_pts(x - w / 2, y + h / 2 - 22, x + w / 2, y + h / 2), "#d9cfb8", .9)
    s.append(shape(rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 30), "#fbf1d8", inner, w=5.2, seed=sd))
    if kind == "doc":
        s.append(doc_icon(x, y - 30, sd + 10))
    else:
        s.append(headphones_icon(x, y - 26, sd + 10))
    s.append(f'<text x="{f(x)}" y="{f(y + 96)}" text-anchor="middle" font-family="Shantell" font-weight="800" font-size="54" '
             f'fill="{INK}">{label}</text>')
    return "".join(s)


def cards(t):
    e = t - 12.42                     # въезд уже идёт на первом кадре s08
    k = ease_out(clamp(e / 0.5), 3)
    fl = 8 * math.sin(t * 2.6)
    # на «два» карточки подскакивают навстречу друг другу
    hop = 0.0
    eh = t - TWO
    if eh > 0:
        hop = 30 * math.exp(-eh * 5) * math.sin(min(eh * 12, math.pi))
    lx = 300 - 420 * (1 - k) + hop
    rx = 780 + 420 * (1 - k) - hop
    ly = 340 + fl - 40 * (1 - k)
    ry = 340 - fl - 40 * (1 - k)
    rl = -6 * (1 - k) - 3 + 2 * math.sin(t * 2.0)
    rr = 6 * (1 - k) + 3 - 2 * math.sin(t * 2.0 + .7)
    glow = smooth(DELA, DELA + .2, t) * (1 - smooth(14.6, 15.1, t))
    s = [f'<g transform="rotate({f(rl)} {f(lx)} {f(ly)})">{card(lx, ly, "doc", "отчёт", 800, glow)}</g>',
         f'<g transform="rotate({f(rr)} {f(rx)} {f(ry)})">{card(rx, ry, "phones", "созвон", 830, glow)}</g>']
    if eh > 0:
        kp = back_out(clamp(eh / 0.3), 2.6)
        s.append(f'<g transform="translate(540 {f(340 + 4 * math.sin(t * 3))}) scale({f(kp)}) rotate({f(8 * math.sin(t * 2.5))})">'
                 + text(0, 40, "+", 150, "#ffe27a", sw=11) + "</g>")
    return "".join(s)


def grid(t, sid):
    s = []
    gold_k = smooth(TWO_P - 0.02, TWO_P + 0.12, t)
    dim = smooth(TWO_P + 0.05, TWO_P + 0.5, t)
    for r in range(10):
        for c in range(10):
            x, y = gpos(r, c)
            t_in = 12.58 + c * 0.045 + r * 0.075
            e = t - t_in
            if e <= 0:
                continue
            sc = back_out(clamp(e / 0.3), 2.2)
            # волна: каждый слегка подпрыгивает, когда волна проходит через него, и потом покачивается
            jump = 16 * math.sin(math.pi * clamp(e / 0.3)) if e < 0.3 else 0
            idle = 2.5 * math.sin(t * 4.2 - c * .6 - r * .45)
            yy = y - jump + idle
            gold = (r, c) in GOLD
            if gold and gold_k > 0:
                ep = t - TWO_P
                pop = 1 + 0.35 * math.exp(-max(ep, 0) * 6) * math.sin(min(max(ep, 0) * 12, math.pi)) * (ep > 0)
                hop = 26 * math.sin(math.pi * clamp(ep / 0.35)) if 0 < ep < 0.35 else 0
                g = rad_grad([(0, "#ffd84a", .7 * gold_k), (.5, "#ffb52a", .25 * gold_k), (1, "#ffb52a", 0)], x, yy - 30, 90, 90)
                s.append(f'<rect x="{f(x - 100)}" y="{f(yy - 130)}" width="200" height="200" fill="url(#{g})"/>')
                ref = "pGrey" if gold_k < 0.5 else "pGold"
                s.append(f'<use href="#{ref}" transform="translate({f(x)} {f(yy - hop)}) scale({f(sc * pop * 1.06 * PS)})"/>')
                s.append(crown(x, yy - hop - 74 * pop * PS, t, ep, (r * 10 + c)))
            else:
                ref = "pGrey" if dim < 0.5 else "pDim"
                s.append(f'<use href="#{ref}" transform="translate({f(x)} {f(yy)}) scale({f(sc * PS)})"/>')
    return "".join(s)


def crown(x, y, t, ep, sd):
    """Корона-искра над головой и искры вокруг: появляется на «двух», искры разлетаются и мерцают."""
    if ep < 0:
        return ""
    k = back_out(clamp(ep / 0.3), 2.5)
    s = []
    pts = [(-20, 8, 1), (-22, -14, 1), (-10, -2, 1), (0, -20, 1), (10, -2, 1), (22, -14, 1), (20, 8, 1)]
    s.append(f'<g transform="translate({f(x)} {f(y)}) scale({f(k)}) rotate({f(6 * math.sin(t * 3 + sd))})">'
             + shape(pts, "#ffd84a", blob([(4, -4), (22, -14), (20, 8), (6, 8)], "#e3a826", .9), w=3.0, seed=900 + sd) + "</g>")
    for j in range(6):
        a = j * math.pi / 3 + sd + t * 0.8
        rr = 40 + 50 * ease_out(clamp(ep / 0.5))
        tw = 0.5 + 0.5 * math.sin(t * 9 + j * 1.7 + sd)
        r = (7 + 7 * tw) * k
        s.append(star(x + math.cos(a) * rr, y + 40 + math.sin(a) * rr * .9, r, "#fff1a0", 910 + j + sd, rot=t * 90 + j * 20))
    s.append(rays(x, y + 40, ep, 940 + sd, r=40, n=8, L0=34, w=6, dur=0.4))
    return "".join(s)


def label_2of100(t):
    e = t - (STA - 0.06)
    if e < 0:
        return ""
    k = back_out(clamp(e / 0.3), 2.2)
    x, y = 588, 700
    w, h = 420, 132
    hit = 1 + 0.1 * math.exp(-e * 8) * math.cos(e * 24)
    s = [blob(rect_pts(-w / 2 + 12, -h / 2 + 16, w / 2 + 12, h / 2 + 16, 36), "#0a0e24", .55, blur(8)),
         shape(rect_pts(-w / 2, -h / 2, w / 2, h / 2, 36), "#1c2650", blob(rect_pts(-w / 2, h / 2 - 22, w / 2, h / 2), "#141c40", .9),
               w=5.4, seed=960)]
    s.append(text(-118, 40, "2", 120, "#ffd84a", sw=10))
    s.append(text(72, 36, "из 100", 92, "#ffffff", sw=9))
    rot = -3 + 1.5 * math.sin(t * 2.3)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(k * hit)})">{"".join(s)}</g>'


def s08(t):
    s = [_ST["bg"], dust(t), cards(t), grid(t, "s08")]
    u = clamp((t - 12.6) / 3.0)
    sc = 1.14 - 0.14 * (0.3 * u + 0.7 * ease_io(u))
    cx, cy = 545, 820 - 20 * u
    rot = 0.6 * math.sin(t * 0.9)
    e = t - TWO
    if e > 0:
        sc *= 1 + 0.025 * math.exp(-e * 8) * math.sin(min(e * 14, math.pi))
    return cam(cx, cy, sc, rot), "".join(s)


def s09(t):
    s = [_ST["bg"], dust(t), cards(t), grid(t, "s09"), label_2of100(t)]
    # наезд к двум: от общего плана (как конец s08) к паре
    (r1, c1), (r2, c2) = GOLD
    p1, p2 = gpos(r1, c1), gpos(r2, c2)
    tx, ty = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 50
    u = ease_io(clamp((t - 15.25) / 1.0))
    v = clamp((t - 15.2) / 2.0)
    sc = 1.0 + 0.4 * u + 0.05 * v
    cx, cy = 545 + (tx - 545) * u, 800 + (ty - 800) * u
    rot = 0.6 * math.sin(t * 0.9)
    for t0, amp in ((TWO_P, 0.045), (STA, 0.035)):
        e = t - t0
        if e > 0:
            kk = math.exp(-e * 8)
            sc *= 1 + amp * kk * math.sin(min(e * 14, math.pi))
            cy += 6 * kk * math.sin(e * 43)
    return cam(cx, cy, sc, rot), "".join(s)


def build_static():
    _ST["bg"] = background()
    person_def("pGrey", "#9aa0b6", "#7a8099", 980)
    person_def("pDim", "#6f7690", "#585e78", 980)
    person_def("pGold", "#ffd23f", "#e0a51c", 980)
    cat.static_parts()
    lib.static_done()


def frame(sid, t):
    if not _ST:
        build_static()
    lib.dyn_begin()
    tr, body = {"s07": s07, "s08": s08, "s09": s09}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1a2244"/><g transform="{tr}">{body}</g>')
