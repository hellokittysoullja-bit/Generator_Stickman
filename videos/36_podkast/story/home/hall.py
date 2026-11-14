"""Прихожая Димы (рилс 36): тёплые бежевые стены, коричневая входная дверь с круглой ручкой (открывается НАРУЖУ,
петли справа, ручка слева — по-нашему), узкое окно справа от двери (вечер, синее небо, дома с огнями; дождь по
параметру rain), вешалка слева с пальто, шарфом и шапкой, зонт, полочка у двери (на ней — место под телефон
PHONE_SPOT), картинка с горами, выключатель, коврик у двери, пол из досок.

Мир: пол y = 0 (вверх — минус), дверь DOOR = (x0, y0, x1, y1). Рост Димы (dima.BS 0.44) ~ 600, дверь 700.
Использование (сцены home и cat):
    import hall
    svg = hall.frame(t, cam=(cx, cy, s, rot), door=0.0, rain=0.0, mid=<SVG героев в мире>, fg=<поверх>)
или по слоям: hall.back(t, door, rain) — всё за героями (в мировых координатах, камеру накладывать снаружи,
lib.cam(...)), hall.front(t) — передний план (пусто/тень у пола). Камера обзора всей прихожей: WIDE.
Манера — как у 23–35: чистый контур живой линией (ink.py), плоский цвет с одной тенью, свет слоями.
"""
import math

import numpy as np

import lib
from lib import INK, ellipse_pts, line, shape

WALL, WALL_SH, WALL_HI = "#ecd3ab", "#d6b688", "#f6e4c4"
WOOD, WOOD_SH, WOOD_HI, WOOD_DK = "#8a5233", "#6a3b22", "#a86a44", "#4f2c18"
CASING, CASING_SH = "#f3e8d4", "#d8c8ac"
FLOOR, FLOOR_SH, FLOOR_LN = "#b07a4c", "#8e5e38", "#6e4428"
FLOOR_Y = 0.0
DOOR = (300.0, -700.0, 610.0, 0.0)
KNOB = (338.0, -330.0)                 # круглая ручка (слева, петли справа)
WIN = (680.0, -640.0, 820.0, -220.0)   # узкое окно справа от двери
SHELF = (60.0, -440.0, 250.0)          # полочка у двери: x0, y (верх доски), x1
PHONE_SPOT = (192.0, -440.0)           # где лежит телефон на полочке (низ телефона)
RACK = (-600.0, -650.0, -200.0)        # вешалка: x0, y, x1
WIDE = (420.0, -420.0, 1.45, 0.0)      # камера на всю прихожую (cx, cy, s, rot)


def rsd(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


def R(x0, y0, x1, y1):
    return [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]


def blob(pts, color, op=1.0, extra=""):
    """Заливка без контура; многоугольник до 6 точек — с прямыми сторонами (углы), длиннее — сплайн (овалы)."""
    return lib.blob(C(pts) if len(pts) <= 6 else pts, color, op, extra)


def C(pts):
    """Все точки — углы (прямые стороны без выгиба сплайна)."""
    return [(p[0], p[1], 1) for p in pts]


# ═════════════════════════ за окном и за дверью ═════════════════════════
def sky(x0, y0, x1, y1, t, rain=0.0):
    """Вечернее небо с домами и огнями в прямоугольнике окна; rain 0..1 — тучи, темнее, косые струи."""
    o = []
    top = lib.mix("#24306a", "#2a3150", rain)
    mid = lib.mix("#4a5aa8", "#3d4766", rain)
    low = lib.mix("#e7a27e", "#6f7590", rain)
    g = lib.lin_grad([(0, top, 1), (.62, mid, 1), (1, low, 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    o.append(f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{g})"/>')
    if rain < 0.99:
        for k, (sx, sy) in enumerate([(x0 + 40, y0 + 60), (x0 + 120, y0 + 110), (x0 + 70, y0 + 170)]):
            o.append(f'<circle cx="{sx}" cy="{sy}" r="{2.2 + k % 2}" fill="#fff6d8" opacity="{(1 - rain) * (.6 + .4 * math.sin(t * 3 + k)):.2f}"/>')
    # тучи наплывают
    if rain > 0.01:
        for k, (cx, cy, rx) in enumerate([(x0 + 40, y0 + 70, 120), (x1 - 20, y0 + 40, 140), (x0 + 90, y0 + 150, 110)]):
            dx = 30 * (1 - rain) * (1 if k % 2 else -1)
            o.append(blob(ellipse_pts(cx + dx + 6 * math.sin(t * .7 + k), cy, rx, rx * .42, 16), "#3a3f55", .92 * rain))
    # дома вдали
    hs = [(x0 - 20, 0.58, "#2d2f55"), (x0 + 44, 0.50, "#353866"), (x0 + 100, 0.62, "#2b2d50"), (x0 + 150, 0.54, "#34365f")]
    for k, (hx, hf, col) in enumerate(hs):
        hy = y0 + (y1 - y0) * hf
        o.append(f'<rect x="{hx}" y="{hy:.1f}" width="66" height="{y1 - hy + 20:.1f}" fill="{lib.mix(col, "#2a2c3e", rain * .5)}"/>')
        rs = rsd(31, k)
        for i in range(3):
            for j in range(6):
                if rs.rand() < .45:
                    wy = hy + 18 + j * 26
                    if wy < y1 - 8:
                        o.append(f'<rect x="{hx + 10 + i * 18}" y="{wy:.1f}" width="9" height="12" fill="#ffd77a" opacity=".9"/>')
    # дождь: косые струи, падают
    if rain > 0.01:
        rs = rsd(77)
        for i in range(46):
            px, ph = rs.uniform(x0 - 120, x1 + 40), rs.uniform(0, 1)
            sp = rs.uniform(1.6, 2.4)
            u = (ph + t * sp) % 1.0
            yy = y0 - 40 + u * (y1 - y0 + 80)
            xx = px + u * (y1 - y0) * .32
            L = rs.uniform(26, 44)
            o.append(f'<line x1="{xx:.1f}" y1="{yy:.1f}" x2="{xx - L * .3:.1f}" y2="{yy - L:.1f}" stroke="#cfe0ff" '
                     f'stroke-width="2.6" stroke-linecap="round" opacity="{.75 * rain:.2f}"/>')
    return "".join(o)


def glass_drops(x0, y0, x1, y1, t, rain):
    """Капли на стекле: появляются и стекают."""
    if rain <= 0.01:
        return ""
    o = []
    rs = rsd(91)
    for i in range(16):
        px, py, t0 = rs.uniform(x0 + 8, x1 - 8), rs.uniform(y0 + 10, y1 - 60), rs.uniform(0, 0.5)
        a = lib.smooth(t0, t0 + .08, rain * 0.6 + 0.0) if False else lib.clamp((rain - t0) / 0.2)
        if a <= 0:
            continue
        slide = 40 * max(0.0, math.sin((t * .9 + i * .37) % 1 * math.pi)) if i % 3 == 0 else 0
        o.append(f'<ellipse cx="{px:.1f}" cy="{py + slide:.1f}" rx="4.4" ry="5.6" fill="#e9f1ff" opacity="{.55 * a:.2f}"/>')
        o.append(f'<circle cx="{px - 1.2:.1f}" cy="{py + slide - 2:.1f}" r="1.6" fill="#ffffff" opacity="{.9 * a:.2f}"/>')
    return "".join(o)


def landing(x0, y0, x1, y1, t):
    """Лестничная площадка за дверью (тёмная, лампа на стене, перила)."""
    o = []
    g = lib.lin_grad([(0, "#4d5a6e", 1), (.7, "#5f6c80", 1), (1, "#3e4757", 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    o.append(f'<rect x="{x0 - 30}" y="{y0 - 30}" width="{x1 - x0 + 60}" height="{y1 - y0 + 60}" fill="url(#{g})"/>')
    o.append(f'<rect x="{x0 - 30}" y="{y0 + (y1 - y0) * .55:.1f}" width="{x1 - x0 + 60}" height="{(y1 - y0) * .45 + 30:.1f}" fill="#6e7a6c"/>')
    gl = lib.rad_grad([(0, "#fff3c4", .8), (.4, "#ffe08a", .35), (1, "#ffe08a", 0)], x0 + 120, y0 + 130, 230)
    o.append(f'<circle cx="{x0 + 120}" cy="{y0 + 130}" r="230" fill="url(#{gl})"/>')
    o.append(shape(ellipse_pts(x0 + 120, y0 + 130, 22, 16, 12), "#fff7d6", w=3, seed=6101))
    # перила лестницы вниз
    o.append(line([(x0 - 20, y1 - 230), (x1 + 20, y1 - 120)], 6, "#2d2a2a", seed=6102))
    for k in range(6):
        bx = x0 + 10 + k * 64
        yt = y1 - 225 + (bx - x0 + 20) * 110 / (x1 - x0 + 40)
        o.append(line([(bx, yt), (bx, y1 + 10)], 3.2, "#2d2a2a", seed=6110 + k, taper=.1, wmin=.8))
    o.append(blob(R(x0 - 30, y1 - 30, x1 + 30, y1 + 10), "#3c4250", .8))
    return "".join(o)


# ═════════════════════════ предметы ═════════════════════════
def door(t, theta=0.0):
    """Наличник, проём и полотно. theta 0 — закрыта, 1 — распахнута наружу (полотно уходит вправо, мельчает)."""
    x0, y0, x1, y1 = DOOR
    o = []
    # проём и площадка за ним
    if theta > 0.002:
        c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
        o.append(f'<g clip-path="url(#{c})">{landing(x0, y0, x1, y1, t)}</g>')
    # наличник
    cw = 28
    outer = R(x0 - cw, y0 - cw, x1 + cw, y1)
    o.append(f'<path d="{lib.fill_d(outer)}M{x0} {y0}H{x1}V{y1}H{x0}Z" fill="{CASING}" fill-rule="evenodd"/>')
    o.append(blob(C([(x1, y0), (x1 + cw, y0 - cw), (x1 + cw, y1), (x1, y1)]), CASING_SH, .9))
    o.append(f'<path d="{lib.ink_closed(outer, 3.8 * lib.INK_K[0], seed=6001)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed(R(x0, y0, x1, y1), 3.2 * lib.INK_K[0], seed=6002)}" fill="{INK}"/>')
    # полотно: петли справа, открывается наружу — свободный (левый) край уходит вправо и вглубь (мельчает)
    th = math.radians(88 * lib.clamp(theta))
    w = (x1 - x0) * math.cos(th)
    ex = x1 - w
    sh = 46 * math.sin(th)

    def L(u, v):                                  # u 0 — свободный край, 1 — петли; v 0 — верх, 1 — низ
        xa = ex + (x1 - ex) * u
        ya = y0 + sh * (1 - u)
        yb = y1 - sh * .55 * (1 - u)
        return (xa, ya + (yb - ya) * v)
    if w > 3:
        pts = [L(0, 0) + (1,), L(1, 0) + (1,), L(1, 1) + (1,), L(0, 1) + (1,)]
        tone = 1 - 0.28 * math.sin(th)
        base = lib.mul(WOOD, (tone, tone, tone))
        inner = blob(C([L(.82, 0), L(1, 0), L(1, 1), L(.82, 1)]), WOOD_SH, .7)
        inner += blob(C([L(0, 0), L(.05, 0), L(.05, 1), L(0, 1)]), WOOD_HI, .5 * (1 - math.sin(th)))
        for (va, vb) in ((.07, .44), (.52, .93)):
            pp = C([L(.17, va), L(.83, va), L(.83, vb), L(.17, vb)])
            inner += lib.shape(pp, lib.mul(WOOD_SH, (tone, tone, tone)),
                               blob(C([pp[0], pp[1], (pp[1][0], pp[1][1] + 14), (pp[0][0], pp[0][1] + 14)]), WOOD_DK, .7) +
                               blob(C([pp[3], pp[2], (pp[2][0], pp[2][1] - 8), (pp[3][0], pp[3][1] - 8)]), WOOD_HI, .6), w=2.6, seed=6020 + int(va * 10))
        # глазок
        px, py = L(.5, .2)
        inner += lib.shape(ellipse_pts(px, py, 7 * max(.3, math.cos(th)), 7, 10), "#c9a24a", blob(ellipse_pts(px, py, 3, 3, 8), "#2a2228"), w=2.2, seed=6030)
        # ручка: круглая, латунная, с бликом
        kx, ky = L((KNOB[0] - x0) / (x1 - x0), (KNOB[1] - y0) / (y1 - y0))
        kr = 17 * max(.35, math.cos(th))
        inner += lib.shape(ellipse_pts(kx, ky, kr * 1.5, 25, 12), "#b8862e", w=2.4, seed=6031)
        inner += lib.shape(ellipse_pts(kx, ky, kr, 17, 12), "#e2b24a",
                           blob(ellipse_pts(kx + kr * .3, ky + 4, kr * .7, 10, 10), "#b8862e", .9) +
                           blob(ellipse_pts(kx - kr * .35, ky - 6, kr * .3, 4, 8), "#fff3c4", .95), w=2.8, seed=6032)
        # замочная скважина
        inner += blob([(kx - 3, ky + 46), (kx + 3, ky + 46), (kx + 4, ky + 62), (kx - 4, ky + 62)], "#2a2228")
        o.append(lib.shape(pts, base, inner, w=4.4, seed=6010))
    # петли
    for hy in (y0 + 90, y1 - 110):
        o.append(lib.shape(R(x1 - 6, hy, x1 + 6, hy + 44), "#b8a27a", w=2, seed=6040 + int(hy)))
    return "".join(o)


def window(t, rain=0.0):
    x0, y0, x1, y1 = WIN
    o = []
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o.append(f'<g clip-path="url(#{c})">{sky(x0, y0, x1, y1, t, rain)}{glass_drops(x0, y0, x1, y1, t, rain)}</g>')
    # блик стекла
    o.append(blob([(x0 + 18, y0 + 30), (x0 + 50, y0 + 30), (x0 + 22, y0 + 160), (x0 + 12, y0 + 160)], "#ffffff", .14))
    fw = 22
    outer = R(x0 - fw, y0 - fw, x1 + fw, y1 + fw)
    o.append(f'<path d="{lib.fill_d(outer)}M{x0} {y0}H{x1}V{y1}H{x0}Z" fill="{CASING}" fill-rule="evenodd"/>')
    o.append(f'<path d="{lib.ink_closed(outer, 3.6 * lib.INK_K[0], seed=6201)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed(R(x0, y0, x1, y1), 3.0 * lib.INK_K[0], seed=6202)}" fill="{INK}"/>')
    # переплёт
    my = y0 + (y1 - y0) * .36
    o.append(shape(R(x0, my - 7, x1, my + 7), CASING, w=2.6, seed=6203))
    o.append(shape(R((x0 + x1) / 2 - 6, my, (x0 + x1) / 2 + 6, y1), CASING, w=2.6, seed=6204))
    # подоконник
    o.append(shape(R(x0 - 40, y1 + fw - 4, x1 + 40, y1 + fw + 18), CASING, blob([(x0 - 40, y1 + fw + 8), (x1 + 40, y1 + fw + 8),
                   (x1 + 40, y1 + fw + 18), (x0 - 40, y1 + fw + 18)], CASING_SH, .9), w=3.4, seed=6205))
    # горшок с растением на подоконнике
    px, py = x1 - 40, y1 + fw - 4
    o.append(shape([(px - 26, py - 44), (px + 26, py - 44), (px + 19, py, 1), (px - 19, py, 1)], "#c96b4a",
                   blob([(px + 6, py - 44), (px + 26, py - 44), (px + 19, py), (px + 8, py)], "#a2533a", .9), w=3, seed=6206))
    for k in range(5):
        a = math.radians(-150 + k * 30) + 0.05 * math.sin(t * 1.3 + k)
        tip = (px + 70 * math.cos(a), py - 44 + 70 * math.sin(a))
        mid = (px + 34 * math.cos(a) - 8 * math.sin(a), py - 44 + 34 * math.sin(a))
        o.append(shape([(px, py - 44), mid, tip + (1,), (px + 30 * math.cos(a) + 10 * math.sin(a), py - 44 + 30 * math.sin(a) - 4)],
                       "#5c9a54" if k % 2 else "#4c8446", w=2.6, seed=6210 + k))
    return "".join(o)


def coat_rack(t):
    x0, y, x1 = RACK
    o = []
    o.append(shape(R(x0, y - 22, x1, y + 22), WOOD_HI, blob([(x0, y + 8), (x1, y + 8), (x1, y + 22), (x0, y + 22)], WOOD_SH, .9), w=3.6, seed=6301))
    hooks = [x0 + 50, x0 + 150, x0 + 250, x0 + 350]
    for k, hx in enumerate(hooks):
        o.append(line([(hx, y), (hx, y + 34), (hx + 16, y + 44), (hx + 22, y + 30)], 4.2, "#3a3436", seed=6310 + k, taper=.2, wmin=.7))
    sw = 2.0 * math.sin(t * 1.1)
    # серое пальто на первом крючке
    hx = hooks[0]
    coat = [(hx - 8, y + 36), (hx + 30, y + 40), (hx + 74, y + 120), (hx + 88, y + 330), (hx + 70 + sw, y + 470, 1),
            (hx - 70 + sw, y + 470, 1), (hx - 88, y + 330), (hx - 70, y + 120)]
    inner = blob([(hx + 20, y + 40), (hx + 100, y + 120), (hx + 100, y + 480), (hx + 30, y + 480)], "#5d6470", .8)
    inner += line([(hx, y + 60), (hx + 4, y + 300), (hx + sw, y + 470)], 2.6, "#3c414b", seed=6321, op=.8)
    for b in range(3):
        inner += f'<circle cx="{hx + 14}" cy="{y + 150 + b * 90}" r="7" fill="#2c3038"/>'
    inner += line([(hx - 60, y + 330), (hx - 20, y + 340)], 2.4, "#3c414b", seed=6322, op=.7)
    o.append(shape(coat, "#7b8392", inner, w=4.0, seed=6320))
    o.append(shape([(hx - 40, y + 36), (hx + 40, y + 36), (hx + 20, y + 110), (hx, y + 90), (hx - 20, y + 110)], "#6b7381", w=3.2, seed=6323))
    # красный шарф на третьем крючке
    hx = hooks[2]
    sw2 = 3 * math.sin(t * 1.3 + 1)
    for k, dx in enumerate((-16, 16)):
        L = 300 if k == 0 else 250
        pts = band_pts([(hx + dx * .3, y + 40), (hx + dx + sw2 * .5, y + L * .5), (hx + dx * 1.2 + sw2, y + L)], 30)
        o.append(shape(pts, "#c8443a" if k == 0 else "#b13a31",
                       "".join(line([(hx + dx - 20 + sw2, y + L - 30 - j * 40), (hx + dx + 20 + sw2, y + L - 30 - j * 40)], 2.4, "#f0d7b0",
                                    seed=6330 + j + k * 5, op=.85) for j in range(2)), w=3.4, seed=6331 + k))
        for j in range(4):
            fx = hx + dx * 1.2 + sw2 - 12 + j * 8
            o.append(line([(fx, y + L), (fx + 1, y + L + 18)], 2.4, "#c8443a", seed=6340 + j + k * 4, taper=.2))
    # шапка на четвёртом
    hx = hooks[3]
    o.append(shape([(hx - 50, y + 110), (hx - 44, y + 60), (hx - 20, y + 36), (hx + 20, y + 34), (hx + 46, y + 56), (hx + 52, y + 110, 1)],
                   "#3f7a72", blob([(hx - 52, y + 88), (hx + 52, y + 88), (hx + 52, y + 112), (hx - 52, y + 112)], "#2f5d57", .95) +
                   "".join(line([(hx - 40 + j * 16, y + 90), (hx - 40 + j * 16, y + 110)], 2, "#244a45", seed=6350 + j, op=.8) for j in range(6)),
                   w=3.4, seed=6351))
    o.append(shape(ellipse_pts(hx, y + 30, 18, 16, 12), "#e8dcc4", w=2.8, seed=6352))
    # зонт-трость у стены под вешалкой
    ux = x1 - 40
    o.append(shape([(ux - 6, -380), (ux + 30, -360), (ux + 40, -60), (ux + 20, -18, 1), (ux, -20, 1), (ux - 16, -60)], "#2f3454",
                   blob([(ux + 12, -370), (ux + 40, -360), (ux + 40, -40), (ux + 18, -40)], "#232741", .9), w=3.4, seed=6360))
    o.append(line([(ux + 6, -380), (ux + 2, -440), (ux - 20, -456), (ux - 36, -440)], 6, "#6a3b22", seed=6361, taper=.15, wmin=.8))
    o.append(line([(ux + 10, -18), (ux + 10, 0)], 4, "#3a3436", seed=6362))
    # кеды под вешалкой
    for k, sx in enumerate((x0 + 40, x0 + 170)):
        o.append(shape([(sx, -6, 1), (sx, -40), (sx + 30, -52), (sx + 60, -40), (sx + 110, -26), (sx + 116, -6, 1)], "#f2efe8",
                       blob([(sx, -18), (sx + 116, -18), (sx + 116, -6), (sx, -6)], "#d6d1c7", .95) +
                       line([(sx + 10, -30), (sx + 60, -42), (sx + 100, -26)], 2.4, "#1f9e9a", seed=6370 + k), w=3.2, seed=6371 + k))
    return "".join(o)


def band_pts(pts, w):
    return lib.band(pts, w, w * .9, step=6, cap=True)


def shelf(t, phone=True):
    """Полочка у двери: доска на кронштейнах, миска для ключей; телефон рисует сцена (PHONE_SPOT), если phone=False."""
    x0, y, x1 = SHELF
    o = []
    for bx in (x0 + 30, x1 - 30):
        o.append(shape([(bx - 6, y), (bx + 6, y), (bx + 6, y + 50), (bx - 6, y + 14)], WOOD_SH, w=2.6, seed=6400 + int(bx)))
    o.append(shape(R(x0, y, x1, y + 20), WOOD_HI, blob([(x0, y + 10), (x1, y + 10), (x1, y + 20), (x0, y + 20)], WOOD_SH, .9), w=3.4, seed=6401))
    # миска с ключами
    mx = x0 + 58
    o.append(line([(mx - 6, y - 24), (mx - 22, y - 46), (mx - 40, y - 44)], 3, "#b6a780", seed=6402))
    o.append(shape(ellipse_pts(mx - 44, y - 44, 9, 9, 10), "#d9c48a", blob(ellipse_pts(mx - 44, y - 44, 4, 4, 8), WALL), w=2.4, seed=6403))
    o.append(shape([(mx - 40, y - 26), (mx + 40, y - 26), (mx + 28, y, 1), (mx - 28, y, 1)], "#4f8ea0",
                   blob([(mx + 6, y - 26), (mx + 40, y - 26), (mx + 28, y), (mx + 10, y)], "#3d7182", .9) +
                   blob([(mx - 40, y - 26), (mx + 40, y - 26), (mx + 40, y - 18), (mx - 40, y - 18)], "#2d5563", .8), w=3, seed=6404))
    if phone:
        o.append(phone_lying(*PHONE_SPOT))
    return "".join(o)


def phone_lying(x, y):
    """Телефон лежит экраном вверх у стены (видно ребро и чуть экран)."""
    return shape(R(x - 46, y - 12, x + 46, y, ), "#22242c", blob([(x - 40, y - 12), (x + 40, y - 12), (x + 40, y - 8), (x - 40, y - 8)], "#4a5068"),
                 w=2.6, seed=6450)


def picture(t):
    """Картинка над полочкой: горы и солнце (без букв)."""
    x0, y0, x1, y1 = 80.0, -680.0, 250.0, -540.0
    o = [shape(R(x0, y0, x1, y1), WOOD_DK, w=3.4, seed=6501)]
    ix0, iy0, ix1, iy1 = x0 + 12, y0 + 12, x1 - 12, y1 - 12
    inner = blob([(ix0, iy0), (ix1, iy0), (ix1, iy1), (ix0, iy1)], "#bfe0e6")
    inner += f'<circle cx="{ix1 - 34}" cy="{iy0 + 30}" r="16" fill="#f4c25a"/>'
    inner += blob([(ix0, iy1), (ix0 + 46, iy0 + 40), (ix0 + 80, iy1 - 30), (ix0 + 110, iy0 + 60), (ix1, iy1)], "#5c8f6a")
    inner += blob([(ix0 + 38, iy0 + 52), (ix0 + 46, iy0 + 40), (ix0 + 56, iy0 + 54)], "#ffffff")
    o.append(shape(R(ix0, iy0, ix1, iy1), "#bfe0e6", inner, w=2.6, seed=6502))
    return "".join(o)


def wall(t):
    o = []
    g = lib.lin_grad([(0, "#dcbd8e", 1), (.45, WALL, 1), (1, "#e4c79a", 1)], 0, -1500, 0, 0, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="-2200" width="4000" height="2300" fill="url(#{g})"/>')
    # тёплый свет плафона сверху и ночника у двери
    for (x, y, r, a) in [(240, -900, 760, .55), (470, -560, 420, .25)]:
        gl = lib.rad_grad([(0, "#fff2cc", a), (.5, "#ffdca0", a * .45), (1, "#ffd08a", 0)], x, y, r)
        o.append(f'<rect x="{x - r}" y="{y - r}" width="{2 * r}" height="{2 * r}" fill="url(#{gl})"/>')
    # обои: тонкие вертикальные полоски и ромбики
    for k in range(-30, 50):
        x = k * 60
        o.append(f'<rect x="{x}" y="-2200" width="4" height="2200" fill="{WALL_SH}" opacity=".35"/>')
    rs = rsd(5)
    for i in range(70):
        x, y = rs.uniform(-1500, 2300), rs.uniform(-1500, -120)
        o.append(line([(x, y), (x + rs.uniform(8, 22), y + rs.uniform(-3, 3))], 1.4, WALL_SH, seed=6600 + i, op=.4))
    # плинтус
    o.append(shape(R(-1600, -44, 2400, 0), CASING, blob([(-1600, -14), (2400, -14), (2400, 0), (-1600, 0)], CASING_SH, .9), w=3.2, seed=6601))
    # выключатель у двери
    sx, sy = 690, -390
    o.append(shape(R(sx - 18, sy - 26, sx + 18, sy + 26), "#f7f1e4", blob([(sx - 7, sy - 12), (sx + 7, sy - 12), (sx + 7, sy + 12), (sx - 7, sy + 12)],
                                                                        "#e2d8c4"), w=2.6, seed=6602))
    return "".join(o)


def floor():
    o = []
    o.append(blob(R(-1600, 0, 2400, 1400), FLOOR))
    vx, vy = 470, -900
    for k in range(-20, 24):
        xb = 470 + k * 120
        x0 = vx + (xb - vx) * (0 - vy) / (1400 - vy)
        o.append(line([(x0, 0), (xb, 1400)], 2.2, FLOOR_LN, seed=6700 + k, op=.6, taper=.1, wmin=.7))
    for k, y in enumerate((40, 110, 210, 350, 560)):
        o.append(line([(-1600, y), (2400, y)], 1.6, FLOOR_SH, seed=6750 + k, op=.4))
    o.append(blob(R(-1600, 0, 2400, 30), "#6e4428", .35))
    gl = lib.rad_grad([(0, "#ffdca0", .32), (1, "#ffd08a", 0)], 300, 60, 700, 180)
    o.append(f'<ellipse cx="300" cy="60" rx="700" ry="180" fill="url(#{gl})"/>')
    return "".join(o)


def mat():
    """Коврик у двери (лежит на полу, в перспективе)."""
    x0, x1 = DOOR[0] - 10, DOOR[2] + 10
    pts = [(x0 + 20, 14, 1), (x1 - 20, 14, 1), (x1 + 10, 74, 1), (x0 - 10, 74, 1)]
    inner = blob(R(x0 - 10, 58, x1 + 10, 80), "#6e2a26", .9)
    for k in range(3):
        y = 28 + k * 14
        inner += line([(x0 + 14 - k * 5, y), (x1 - 14 + k * 5, y)], 2.4, "#e0b46a", seed=6801 + k, op=.8)
    return shape(pts, "#9e3a33", inner, w=3.4, seed=6800)


def back(t, door_open=0.0, rain=0.0, phone=True):
    """Всё за героями, в мировых координатах."""
    return "".join([wall(t), picture(t), window(t, rain), door(t, door_open), coat_rack(t), shelf(t, phone), floor(), mat()])


def front(t):
    """Передний план: мягкая тень по низу (виньетка пола)."""
    g = lib.lin_grad([(0, "#2a1810", 0), (1, "#2a1810", .35)], 0, 200, 0, 900, units="userSpaceOnUse")
    return f'<rect x="-1600" y="200" width="4000" height="1200" fill="url(#{g})"/>'


def vignette(op=0.28):
    g = lib.rad_grad([(0, "#1a1020", 0), (.7, "#1a1020", 0), (1, "#1a1020", op)], 540, 900, 1200, 1500)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def frame(t, cam=WIDE, door=0.0, rain=0.0, mid="", fg="", phone=True, screen_fg=""):
    """Полный кадр 1080×1920 (SVG-строка): фон прихожей, mid (герои в мире), fg (поверх в мире), screen_fg (поверх в экране).
    lib.DEFS НЕ очищается здесь (в mid уже есть ссылки на clipPath) — сцена делает lib.DEFS.clear() в начале своего кадра."""
    cx, cy, s, rot = cam
    body = f'<g transform="{lib.cam(cx, cy, s, rot)}">{back(t, door, rain, phone)}{mid}{front(t)}{fg}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2030"/>{body}{vignette()}{screen_fg}')


if __name__ == "__main__":      # пробный кадр: python3 hall.py out.svg
    import sys
    lib.DEFS.clear()
    open(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdout", "w").write(frame(1.0, rain=0.0))
