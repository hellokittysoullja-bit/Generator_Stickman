"""Рилс 59 «подарок», группа A: комната Димы и экран с лентой товаров.
s01 (0–1.4) хук: Дима за ноутбуком, на «маме» облачко с портретом мамы, на «подарок» вылетает коробка; влёт камеры.
s03 (2.9–4.5) на «открыл» крышка ноутбука открывается, экран светит на лицо, на «магазин» ряд карточек.
s04 (4.5–5.86) крупно экран, лента карточек несётся вверх, размытие на «тысячу», отражение в глазах на «товаров».
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Люди и предметы — common/."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props  # noqa: E402
import base_d as D  # noqa: E402
import s56 as S  # noqa: E402
from lib import (blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape, smooth, svg, back_out, spring, rrect)  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
T = {i: w["start"] for i, w in enumerate(WORDS)}
INK = lib.INK
def lerp(a, b, u):
    return a + (b - a) * u


DB, DF = D.DESK_BACK, D.DESK_FRONT
_ST = {}
CARD_COLS = ["#FBE3E6", "#E3F0FB", "#FFF1CF", "#E4F5E1", "#EFE4FA", "#FDE9D4"]
CARD_ITEMS = ["teddy", "sneaker", "kettle", "book", "lamp", "scarf"]


def expr_of(**kw):
    e = dict(lid=.9, look=(.8, 0), brows="calm", mouth="flat", flush=.0)
    e.update(kw)
    return e


def sh(x, y, w, h, c):
    return blob(rect_pts(x, y, x + w, y + h), c)


# ───────────────────────── ноутбук ─────────────────────────
# мировые точки: основание — параллелограмм, крышка поднимается от задней кромки
LB = dict(bl=(552.0, DB + 22), br=(842.0, DB + 14), fl=(536.0, DB + 56), fr=(868.0, DB + 46))   # задняя/передняя кромка основания (лев/прав)
LID_H = 215.0


def lid_quad(op):
    """Четыре угла внешнего контура крышки при раскрытии op 0…1 (0 — лежит на основании, 1 — стоит)."""
    bl, br = LB["bl"], LB["br"]
    # верхняя кромка поднимается от передней кромки основания (лежит) к высоте LID_H над задней (стоит)
    tlx = lerp(LB["fl"][0] + 6, bl[0] + 6, ease_out(op, 1.0))
    tly = lerp(LB["fl"][1] - 6, bl[1] - LID_H, op)
    trx = lerp(LB["fr"][0] - 6, br[0] - 6, ease_out(op, 1.0))
    try_ = lerp(LB["fr"][1] - 6, br[1] - LID_H - 8, op)
    return [(bl[0], bl[1]), (br[0], br[1]), (trx, try_), (tlx, tly)]


def screen_card(ix, x, y, w, h, u, seed):
    """Карточка товара без букв и цифр: пастельный фон, предмет, две полоски-«цена»."""
    if u <= 0.01:
        return ""
    s = back_out(clamp(u), 2.2)
    col = CARD_COLS[ix % len(CARD_COLS)]
    o = [shape(rect_pts(-w / 2, -h / 2, w / 2, h / 2, 6), col, "", w=2.6, seed=seed)]
    o.append(props.item(CARD_ITEMS[ix % 6], 0, h * .14, h * .0075 if h < 100 else h * .0068))
    o.append(blob(rect_pts(-w * .36, h * .27, w * .1, h * .27 + 6), "#6b6f80"))
    o.append(blob(rect_pts(w * .14, h * .27, w * .36, h * .27 + 6), "#E8892B"))
    return f'<g transform="translate({f(x)} {f(y)}) scale({s:.4f})">{"".join(o)}</g>'


def screen_content(W, H, cards_u, t, glow=1.0):
    """Содержимое экрана в локальных координатах 0…W × 0…H: строка поиска и сетка карточек."""
    o = [sh(0, 0, W, H, "#F6F7FB")]
    o.append(shape(rect_pts(10, 8, W - 10, 30, 11), "#E3E6EF", "", w=2.0, seed=410))
    o.append(shape(ellipse_pts(24, 19, 5.2, 5.2, 10), "#E3E6EF", "", w=2.0, seed=411))
    o.append(line([(28, 23), (34, 29)], 2.4, INK, taper=0, wmin=1, seed=412))
    cols, rows = 3, 2
    cw, ch = (W - 40) / cols, (H - 56) / rows
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            cx = 14 + cw * c + cw / 2 + 4 * c
            cy = 40 + ch * r + ch / 2 + 4 * r
            o.append(screen_card(i, cx, cy, cw - 4, ch - 4, cards_u[i] if i < len(cards_u) else 0, 420 + i))
    return "".join(o)


def laptop_back(op):
    """Задняя кромка и основание (под руками)."""
    bl, br, fl, fr = LB["bl"], LB["br"], LB["fl"], LB["fr"]
    top = [(bl[0], bl[1], 1), (br[0], br[1], 1), (fr[0], fr[1], 1), (fl[0], fl[1], 1)]
    side = [(fl[0], fl[1], 1), (fr[0], fr[1], 1), (fr[0] - 4, fr[1] + 14, 1), (fl[0] + 4, fl[1] + 14, 1)]
    o = [blob([(p[0] + 12, p[1] + 20) for p in side], "#2a1408", .3)]
    o.append(shape(side, "#8F95A3", "", w=3.4, seed=4301))
    keys = ""
    for r in range(4):
        v0 = (r + .55) / 5.2
        for c in range(9):
            u0 = (c + .35) / 9.4
            a = (bl[0] + (fl[0] - bl[0]) * v0 + (br[0] - bl[0]) * u0, bl[1] + (fl[1] - bl[1]) * v0 + (br[1] - bl[1]) * u0)
            keys += blob([(a[0], a[1]), (a[0] + 21, a[1] - .6), (a[0] + 20, a[1] + 5), (a[0] - 1, a[1] + 5.5)], "#EDEEF2")
    o.append(shape(top, "#C9CDD8", keys + blob([(bl[0] + 100, fl[1] - 12), (br[0] - 100, fr[1] - 12), (br[0] - 100, fr[1] - 2), (bl[0] + 100, fl[1] - 2)], "#B4B9C6"), w=3.6, seed=4300))
    return "".join(o)


def laptop_lid(op, cards_u, t, glow=1.0):
    """Крышка: тёмная снаружи, пока закрывается, экран с карточками — когда стоит."""
    q = lid_quad(op)
    quad = [(q[0][0], q[0][1], 1), (q[1][0], q[1][1], 1), (q[2][0], q[2][1], 1), (q[3][0], q[3][1], 1)]
    if op < .5:
        return shape(quad, "#7C8294", blob([(q[0][0], q[0][1]), (q[1][0], q[1][1]), (q[2][0], q[2][1]), (q[3][0], q[3][1])], "#8B91A3") +
                     blob(ellipse_pts((q[0][0] + q[2][0]) / 2, (q[0][1] + q[2][1]) / 2, 14, 10, 10), "#B9BECC"), w=3.8, seed=4310)
    bz = shape(quad, "#2C3140", "", w=3.8, seed=4311)
    # экран — параллелограмм внутри рамки: аффинное отображение локальных (0..W, 0..H)
    W_, H_ = 240.0, 170.0
    inset = 13.0
    tl = (q[3][0] + inset, q[3][1] + inset)
    tr = (q[2][0] - inset, q[2][1] + inset)
    bl_ = (q[0][0] + inset, q[0][1] - inset - 4)
    a, b = (tr[0] - tl[0]) / W_, (tr[1] - tl[1]) / W_
    c, d = (bl_[0] - tl[0]) / H_, (bl_[1] - tl[1]) / H_
    cid = lib.clip_of([(tl[0], tl[1], 1), (tr[0], tr[1], 1), (tr[0] + (bl_[0] - tl[0]), tr[1] + (bl_[1] - tl[1]), 1), (bl_[0], bl_[1], 1)])
    # экран «включается»: с op 0.5…0.8 яркость растёт
    lit = smooth(.5, .85, op)
    cont = screen_content(W_, H_, cards_u, t)
    cont = f'<g transform="matrix({a:.5f} {b:.5f} {c:.5f} {d:.5f} {tl[0]:.2f} {tl[1]:.2f})">{cont}</g>'
    veil = blob(rect_pts(tl[0] - 20, tl[1] - 20, tr[0] + 20, bl_[1] + 20), "#1B1F2B", 1 - lit) if lit < .99 else ""
    return bz + f'<g clip-path="url(#{cid})">{cont}{veil}</g>' + shape(quad, "none", "", w=3.8, seed=4312, ink=True)


def screen_glow(face, k):
    """Холодный свет экрана на лицо (screen-смешение) — пятно у головы, обращённое к экрану."""
    if k < .02:
        return ""
    g = rad_grad([(0, "#cfe8ff", .46 * k), (.55, "#9fd0f5", .2 * k), (1, "#9fd0f5", 0)], face[0] + 30, face[1], 260, 220)
    return f'<rect x="{f(face[0] - 300)}" y="{f(face[1] - 260)}" width="620" height="520" fill="url(#{g})" style="mix-blend-mode:screen"/>'


# ───────────────────────── общий мир ─────────────────────────
def init():
    if _ST.get("init"):
        return
    D.DAY[0] = False
    D.static_all()
    _ST["init"] = True


def dima_pose(lean, n_t, f_t, expr, ha=0.0, hands=None, head_off=(0, 0), hip_off=(0, 0), nd=None, fd=None):
    hands = hands or {"n": D.fist(.4), "f": D.fist(.4)}
    return D.dima(lean, {"n": ("ik", n_t), "f": ("ik", f_t)}, hands, expr, head_ang=ha, head_off=head_off, hip_off=hip_off)


def room(t, d, op, cards_u, extra_mid="", extra_front="", motes=True):
    o = [D._ST["room"], D._ST["lamp"], lib.f and "", ]
    o = [D._ST["room"], D._ST["lamp"]]
    from room import chair
    o.append(chair(D.D_HIP[0], D.D_HIP[1] + 4, 1, 2300))
    o.append(D._ST["legs"])
    o.append(d.get("legs", ""))
    o.append(D._ST["top"])
    o.append(D._ST["light"])
    if motes:
        o.append(D.motes(t))
    o.append(laptop_back(op))
    o.append(laptop_lid(op, cards_u, t))
    o.append(d["arm_f"])
    o.append(d["body"])
    o.append(extra_mid)
    o.append(d["arm_n"])
    o.append(extra_front)
    return "".join(o)


def hook_cam(t, hit, base, cx, cy, hit_rot=0.0):
    """Влёт правил 28–29: 1/(1+0.4) → 1 за 0.22 с, перелёт 5 %, поворот −3° с возвратом, удар +8 % на ударном слоге."""
    u = clamp(t / .22)
    e = 1 - (1 - u) ** 3
    m = 1 / (1 + .4 * (1 - e))
    if t > .22:
        tt = t - .22
        m *= 1 + .05 * math.exp(-tt * 7.5) * math.sin(min(tt * 22, math.pi) ) if tt * 22 < math.pi else 1 + .0
    rot = -3.0 * (1 - e) + 0.5 * math.sin(t * 7)
    if t > hit:
        tt = t - hit
        m *= 1 + .08 * math.exp(-tt * 9)
        rot += 1.4 * math.exp(-tt * 10) * math.sin(tt * 40)
        cx += 5 * math.exp(-tt * 12) * math.sin(tt * 55)
        cy += 6 * math.exp(-tt * 12) * math.sin(tt * 47 + 1)
    return cx, cy, base * m, rot


# ───────────────────────── s01 ─────────────────────────
def mama_cloud(t, ccx, ccy, u, pop):
    """Облачко-мысль с портретом мамы (штрихами, без букв)."""
    sc = back_out(clamp(u), 2.4)
    if sc <= .02:
        return ""
    fg = people.figure("mama", 0, 0, 0.52, dict(lid=.9, look=(.2, 0), brows="up", mouth="smile", smile=1.0, laugh=0.0, blush=.5), flip=True)
    hx, hy = fg["head"]
    inner = f'<g transform="translate({f(-hx)} {f(-hy + 36)})">{fg["svg"]}</g>'
    cl = S.thought_cloud(ccx, ccy, 128, 104, inner, sx=sc, sy=sc, rot=-4 * (1 - clamp(u)), seed=2)
    # три пузыря-хвоста от головы Димы к облачку
    bub = S.bubbles(ccx - 90, ccy + 118 + 80, ccx - 40, ccy + 118, clamp(u * 1.4))
    return bub + cl


def type_hand(t, base_x, side):
    ph = t * 15 + (0 if side == "n" else 1.7)
    return (base_x + 8 * math.sin(ph * .5), DB + 14 + 6 * max(0, math.sin(ph)))


def frame01(t):
    T_MA, T_PD = T[2], T[3]       # 0.86 «маме», 1.18 «подарок»
    glow = .8
    bob = 3.0 * math.sin(t * 9)
    look_u = smooth(.5, .9, t)
    expr = expr_of(lid=.8 + .15 * smooth(T_MA - .1, T_MA + .2, t), look=(.9 - .5 * look_u * 0, -.25 * look_u), brows="up" if t > T_MA else "calm",
                   mouth="smile" if t > T_MA else "flat", smile=.5 * smooth(T_MA, T_MA + .4, t), closed=1.0 if (.58 < t < .66) else 0.0)
    n_t = type_hand(t, 690, "n")
    f_t = type_hand(t, 650, "f")
    d = dima_pose(.1 + .02 * math.sin(t * 5), n_t, f_t, expr, ha=-.05 * smooth(T_MA, T_MA + .5, t) + .02 * math.sin(t * 7), head_off=(0, bob),
                  hands={"n": D.fist(.35), "f": D.fist(.35)})
    hp = d["head"]
    ccx, ccy = hp[0] + 90, hp[1] - 270
    mid = mama_cloud(t, ccx, ccy, (t - T_MA) / .38, 0)
    # коробка вылетает из экрана
    u = (t - T_PD) / .5
    front = ""
    if u > 0:
        sx_, sy_ = 710.0, 880.0
        ex_, ey_ = 770.0, 720.0
        uu = ease_out(clamp(u), 2.2)
        bx = lerp(sx_, ex_, uu) + 18 * math.sin(uu * 3.14)
        by = lerp(sy_, ey_, uu) - 90 * math.sin(uu * 3.14) * (1 - uu) + 6 * math.sin(t * 20) * (1 - clamp(u))
        k = 1.15 * back_out(clamp(u * 1.5), 2.8)
        lid = clamp(1.0 - abs(clamp(u * 1.3) - .35) * 2.2) if u < 1 else 0.0
        front = props.giftbox(bx, by + 60 * k * 0, k, lid=lid * 1.0 if u < .8 else 0.2 * math.exp(-(u - .8) * 6), rot=-14 + 22 * ease_out(clamp(u), 1.5) + 4 * math.sin(t * 17))
        # блики вокруг
        for j in range(5):
            a = j * 1.26 + .4
            ru = clamp((u - .15 - j * .05) / .5)
            front += props.spark(bx + 105 * math.cos(a) * (.5 + ru), by - 55 + 90 * math.sin(a) * (.5 + ru), 1.0 + .3 * (j % 2), ru)
    body = room(t, d, 1.0, [0] * 6, extra_mid=mid, extra_front=front)
    cx, cy, s, rot = hook_cam(t, T_PD, 1.62, 500, 1010)
    D.set_ink(s)
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{body}{screen_glow(d["head"], .4)}</g>'


# ───────────────────────── s03 ─────────────────────────
def frame03(t):
    T_OP, T_SH = T[8], T[9]     # 3.08 «открыл», 3.51 «магазин»
    op = smooth(T_OP - .02, T_OP + .30, t)
    ov = 1 + .08 * math.sin(clamp((t - T_OP - .05) / .3) * math.pi) * (1 if t > T_OP else 0)
    op_ = min(1.0, op * ov)
    cards_u = [(t - T_SH - .07 * i) / .26 for i in range(6)]
    azart = smooth(T_OP + .1, T_OP + .5, t)
    wide = smooth(T_SH, T_SH + .2, t)
    expr = expr_of(lid=.7 + .3 * azart, look=(.95, -.2 * azart), brows="up" if azart > .1 else "det", mouth="grin" if wide > .3 else "smile",
                   smile=.6 * azart + .3 * wide, blush=.35 * azart, closed=1.0 if (3.7 < t < 3.76) else 0.0)
    lean = .08 + .06 * azart + .02 * math.sin(t * 4)
    # рука берёт крышку за верхнюю кромку и поднимает
    q = lid_quad(op_)
    lidpt = (lerp(q[3][0], q[2][0], .35), lerp(q[3][1], q[2][1], .35))
    hold = 1 - smooth(T_OP + .3, T_OP + .55, t)
    key = type_hand(t, 690, "n") if t > T_OP + .5 else (690, DB + 16)
    rest = (lerp(key[0], lidpt[0] + 8, hold if t >= T_OP - .35 else 0), lerp(key[1], lidpt[1] + 6, hold if t >= T_OP - .35 else 0))
    hands = {"n": D.fist(.62 if hold > .2 else .3), "f": D.fist(.3)}
    d = dima_pose(lean, rest if t < T_OP + .55 else rest, type_hand(t, 640, "f") if t > T_SH else (640, DB + 16), expr, ha=.05 * azart - .03 * math.sin(t * 6),
                  head_off=(0, 2 * math.sin(t * 6)), hands=hands)
    glow = smooth(T_OP + .12, T_OP + .5, t)
    body = room(t, d, op_, cards_u, motes=True)
    u = clamp((t - 2.7) / 1.8)
    cx, cy, s, rot = 500 + 130 * ease_io(u), 1010 - 30 * ease_io(u), 1.6 + .5 * ease_io(u), -.6 + .8 * u
    D.set_ink(s)
    # дрожь на открытии
    if T_OP < t < T_OP + .4:
        tt = t - T_OP
        cx += 4 * math.sin(tt * 60) * math.exp(-tt * 9)
        cy += 5 * math.sin(tt * 51) * math.exp(-tt * 9)
        s *= 1 + .03 * math.exp(-tt * 8)
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{body}{screen_glow(d["head"], glow * .6)}</g>'


# ───────────────────────── s04 ─────────────────────────
_SC = {}


def scroll_pos(t):
    """Путь ленты (px) к моменту t: пошла на «пролистал», разгон на «тысячу», размытие."""
    if not _SC:
        a, p = 0.0, 0.0
        for i in range(0, 1400):
            tt = 4.0 + i / 600.0
            v = 140 * smooth(4.03, 4.3, tt) + 700 * smooth(4.4, 4.75, tt) + 2300 * smooth(4.61, 5.2, tt) ** 1.5
            p += v / 600.0
            _SC[i] = p
    i = int(clamp((t - 4.0) * 600, 0, 1399))
    return _SC[i]


def eye_world(hp, sc, ha, which):
    ex, ey, rx, ry = people.EYE_N if which == "n" else people.EYE_F
    c, s_ = math.cos(ha), math.sin(ha)
    return (hp[0] + sc * (ex * c - ey * s_), hp[1] + sc * (ex * s_ + ey * c), rx * sc, ry * sc)


def frame04(t):
    T_PL, T_TY, T_TO = T[11], T[12], T[13]    # 4.03, 4.61, 5.19
    pos = scroll_pos(t) if t > 4.0 else 0.0
    spd = (scroll_pos(t + .02) - scroll_pos(t)) / .02 if t > 4.0 else 0.0
    o = ['<rect x="-200" y="-200" width="1500" height="2400" fill="#26304A"/>']
    for x in range(-100, 1200, 130):
        o.append(f'<rect x="{x}" y="-200" width="22" height="2400" fill="#1D2640" opacity=".6"/>')
    # экран: большой, поднят вверх
    X0, Y0, X1, Y1 = 70, 70, 1010, 990
    o.append(shape(rect_pts(X0 - 26, Y0 - 26, X1 + 26, Y1 + 40, 26), "#2C3140", "", w=7, seed=4401))
    cid = lib.clip_rect(X0, Y0, X1 - X0, Y1 - Y0, 8)
    CW, CH, G = 276, 300, 28
    cont = [sh(X0, Y0, X1 - X0, Y1 - Y0, "#F6F7FB")]
    rows = 5
    span = rows * (CH + G)
    for r in range(rows):
        yy = Y0 + 70 + r * (CH + G) - (pos % span)
        if yy < Y0 - CH:
            yy += span
        for c in range(3):
            i = (int((pos // span)) * 0 + r * 3 + c)
            n = (i + int(pos // span) * 5) % 6
            xx = X0 + 40 + c * (CW + G) + CW / 2
            card = [shape(rect_pts(-CW / 2, 0, CW / 2, CH, 14), CARD_COLS[n % 6], "", w=5, seed=4410 + i)]
            card.append(props.item(CARD_ITEMS[n], 0, CH * .62, 2.2 if n != 2 else 1.8))
            card.append(blob(rect_pts(-CW * .38, CH * .8, CW * .05, CH * .8 + 14), "#6b6f80"))
            card.append(blob(rect_pts(CW * .12, CH * .8, CW * .38, CH * .8 + 14), "#E8892B"))
            cont.append(f'<g transform="translate({f(xx)} {f(yy)})">{"".join(card)}</g>')
    # размытие движения
    bl = min(26.0, spd / 110)
    inner = "".join(cont)
    if bl > .6:
        fid = lib.uid("mb")
        lib.DEFS.append(f'<filter id="{fid}" x="-5%" y="-30%" width="110%" height="160%"><feGaussianBlur stdDeviation="0 {bl:.1f}"/></filter>')
        inner = f'<g filter="url(#{fid})">{inner}</g>'
    o.append(f'<g clip-path="url(#{cid})">{sh(X0, Y0, X1 - X0, Y1 - Y0, "#F6F7FB")}{inner}'
             f'{sh(X0, Y0, X1 - X0, 56, "#E3E6EF")}</g>')
    o.append(shape(ellipse_pts(X0 + 36, Y0 + 28, 11, 11, 10), "#BFC4D4", "", w=3, seed=4402))
    # Дима внизу: смотрит на экран снизу вверх
    ha = -.1 + .03 * math.sin(t * 8)
    amaze = smooth(T_TY - .1, T_TY + .3, t)
    expr = dict(lid=1.0, look=(.1, -.95), brows="up", mouth="talk", open=.25 + .25 * amaze, closed=1.0 if (4.35 < t < 4.4 or 5.02 < t < 5.07) else 0.0,
                blush=0, flush=0)
    SCL = 1.5
    fg = people.figure("dima", 0, 0, SCL, expr, head_ang=ha, layers=("body",), lean=0.0)
    hx, hy = fg["head"]
    tx, ty = 430, 1290
    o.append(f'<g transform="translate({tx - hx:.1f} {ty - hy:.1f})">{fg["svg"]}</g>')
    hp = (tx, ty)
    # отражение экрана в глазах: мини-лента, появляется на «товаров»
    ru = clamp((t - T_TO) / .25)
    if ru > 0:
        for w_ in ("n", "f"):
            ex, ey, rx, ry = eye_world(hp, SCL * .6, ha, w_)
            cid2 = lib.clip_of(ellipse_pts(ex, ey, rx * .72, ry * .7, 14))
            mini = ""
            off = (pos * .12) % 40
            for r in range(-1, 4):
                for c in range(3):
                    n = (r + c * 2) % 6
                    mini += blob(rect_pts(ex - rx * .7 + c * rx * .5, ey - ry * .7 + r * 26 - off, ex - rx * .7 + c * rx * .5 + rx * .42, ey - ry * .7 + r * 26 + 20 - off), CARD_COLS[n])
            o.append(f'<g clip-path="url(#{cid2})" opacity="{.92 * ru:.2f}">{blob(rect_pts(ex - rx, ey - ry, ex + rx, ey + ry), "#F6F7FB")}{mini}</g>')
    # свет экрана на лицо
    g = rad_grad([(0, "#cfe8ff", .30), (.6, "#9fd0f5", .12), (1, "#9fd0f5", 0)], 500, 1250, 520, 330)
    o.append(f'<rect x="-100" y="900" width="1300" height="900" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    # камера: наезд и тряска
    u = clamp((t - 4.3) / 1.6)
    s = 1.0 + .13 * ease_in(u, 1.6)
    sh1 = 1 + 4 * smooth(T_TY - .05, T_TY + .1, t) * (1 - smooth(T_TY + .1, T_TY + .6, t)) + 2 * (1 - smooth(T_TO, T_TO + .4, t)) * smooth(T_TO - .3, T_TO, t)
    cx = 540 + 9 * sh1 * math.sin(t * 61)
    cy = 960 + 11 * sh1 * math.sin(t * 53 + 1) - 60 * ease_io(u)
    rot = .4 + 1.3 * sh1 * math.sin(t * 37)
    if t > T_TO:
        tt = t - T_TO
        s *= 1 + .06 * math.exp(-tt * 9)
    D.set_ink(s)
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(o)}</g>'


def frame(sid, t):
    init()
    lib.dyn_begin()
    body = {"s01": frame01, "s03": frame03, "s04": frame04}[sid](t)
    return svg(f'<rect width="1920" height="1920" fill="#2a1f2a"/>{body}')


if __name__ == "__main__":
    sid = sys.argv[1]
    ts = [float(x) for x in sys.argv[2].split(",")]
    lst = []
    os.makedirs("/tmp/a59a/sh", exist_ok=True)
    for t in ts:
        p = f"/tmp/a59a/sh/{sid}_{t:.2f}"
        open(p + ".svg", "w").write(frame(sid, t))
        lst.append(f"{p}.svg\t{p}.png")
    open("/tmp/a59a/l.txt", "w").write("\n".join(lst))
