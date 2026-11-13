"""Кухонный таймер-яйцо рилса 29.
s15 (24.2–26.52): крупно таймер на столешнице; рука в горчичном рукаве (кисть как в кухне рилса 28) заходит справа,
берёт жёлтый верх и в два поворота заводит шкалу; на «десять» (25.76) против указателя встаёт 10 — щелчок, цифра
вспыхивает крупно, рука уходит."""
import math

import hand
import lib
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg, T)
from parts import sausage

_ST = {}
SKIN, SKIN_SH, SKIN_SH2, NAIL = hand.SKIN, hand.SKIN_SH, hand.SKIN_SH2, hand.NAIL
HOOD, HOOD_SH, FOLD = hand.HOOD, hand.HOOD_SH, hand.FOLD
EC = (540, 760)          # центр яйца
ERX, ETOP, EBOT = 250, 400, 1110
SEAM = 820               # шов: выше — жёлтый верх со шкалой, ниже — белое основание
TOP = 1080               # дальний край столешницы
CLICK = 25.76


def egg_pts():
    cx = EC[0]
    out = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        y = math.cos(a)
        x = math.sin(a)
        # яйцо: верх уже, низ шире и ровнее
        yy = (ETOP + EBOT) / 2 - y * (EBOT - ETOP) / 2
        w = ERX * (1 - 0.18 * y) if y > 0 else ERX * (1 + 0.04 * y)
        out.append((cx + x * w, yy))
    return out


def half_w(y):
    """Полуширина яйца на высоте y."""
    yy = ((ETOP + EBOT) / 2 - y) / ((EBOT - ETOP) / 2)
    yy = max(-1, min(1, yy))
    w = ERX * (1 - 0.18 * yy) if yy > 0 else ERX * (1 + 0.04 * yy)
    return w * math.sqrt(max(0, 1 - yy * yy))


def lay_hand(x, y, sc, rot, fsq=0.8, curl=0.0):
    """Кисть тыльной стороной к зрителю, пальцы вперёд (от нас, вверх по экрану, в ракурсе fsq), большой палец слева,
    рукав уходит вниз-вправо за кадр. (x, y) — середина костяшек."""
    s = []

    def P(pts, sy=1.0):
        return T([(p[0], p[1] * sy) + tuple(p[2:]) for p in pts], x, y, sc, rot)
    # рукав (длинный, за кадр)
    sl = [(-118, 150, 1), (108, 140, 1), (420, 1300, 1), (-60, 1360, 1)]
    s.append(shape(P(sl), HOOD, blob(P([(40, 150), (108, 140), (420, 1300), (180, 1330)]), HOOD_SH, .9) +
                   line(P([(-40, 280), (30, 600), (60, 900)]), 4, FOLD, seed=1010, op=.7) +
                   line(P([(60, 320), (150, 560)]), 3.4, FOLD, seed=1013, op=.6), w=5.2, seed=1011))
    s.append(shape(P([(-126, 116, 1), (114, 106, 1), (122, 176, 1), (-120, 186, 1)]), HOOD_SH,
                   "".join(line(P([(-100 + k * 40, 122), (-100 + k * 40, 180)]), 2.6, FOLD, seed=1020 + k, op=.8) for k in range(6)),
                   w=4.6, seed=1012))
    # большой палец слева, вдоль края телефона
    th = sausage(P([(-80, 50), (-118, 10), (-136, -34)], fsq + .2), 50 * sc, 40 * sc)
    s.append(shape(th, SKIN, "", w=4.4, seed=1030))
    # пальцы вперёд (в ракурсе), кончики загибаются за дальний край
    fl = fsq * (1 - 0.25 * curl)
    fingers = [(-62, 118, 42), (-20, 134, 44), (22, 126, 42), (60, 98, 36)]
    for k, (fx, L_, w_) in enumerate(fingers):
        tip = (fx + (k - 1.5) * 5, -L_)
        sp = sausage(P([(fx, 20), (fx + (k - 1.5) * 2.5, -L_ * 0.5), tip], fl), w_ * sc, w_ * 0.9 * sc)
        inner = line(P([(fx - w_ * .3, -L_ * 0.45), (fx + w_ * .3, -L_ * 0.45)], fl), 2.4, SKIN_SH2, seed=1040 + k, op=.8)
        s.append(shape(sp, SKIN, inner, w=4.2, seed=1060 + k))
        nx, ny = P([(tip[0], tip[1] + w_ * 0.5)], fl)[0]
        s.append(shape(ellipse_pts(nx, ny, w_ * 0.3 * sc, w_ * 0.28 * sc, 10, rot=rot), NAIL, "", w=2, seed=1070 + k))
    back = [(-92, 6), (-40, -6), (20, -8), (86, 2), (100, 50), (88, 130), (0, 140), (-90, 136), (-104, 64)]
    inner = blob(P([(40, 0), (96, 56), (90, 130), (30, 136)]), SKIN_SH, .9)
    for k in range(4):
        fx = fingers[k][0]
        inner += line(P([(fx - 10, 6), (fx, -2), (fx + 10, 6)]), 2.6, SKIN_SH2, seed=1080 + k, op=.8)
    inner += line(P([(-30, 40), (-20, 110)]), 2.4, SKIN_SH2, seed=1090, op=.6)
    inner += line(P([(20, 40), (14, 110)]), 2.4, SKIN_SH2, seed=1091, op=.6)
    s.append(shape(P(back), SKIN, inner, w=5, seed=1092))
    return "".join(s)




def background():
    s = []
    wall = "#efd9ae"
    s.append(f'<rect x="-900" y="-900" width="2900" height="{TOP + 900}" fill="{wall}"/>')
    for j in range(-6, 8):
        s.append(f'<rect x="-900" y="{j * 160 - 3}" width="2900" height="6" fill="#d6bb88"/>')
    for i in range(-6, 14):
        s.append(f'<rect x="{i * 160 - 3}" y="-900" width="6" height="{TOP + 900}" fill="#d6bb88"/>')
    for j in range(-6, 7):
        for i in range(-6, 14):
            s.append(f'<rect x="{i * 160 + 10}" y="{j * 160 + 10}" width="16" height="130" fill="#f7e7c4"/>')
    s.append(line([(-900, TOP), (2000, TOP)], 4.4, INK, taper=.05, wmin=.9, seed=801))
    tp = [(-900, TOP, 1), (2000, TOP, 1), (2000, 2800, 1), (-900, 2800, 1)]
    inner = "".join(line([(-900, TOP + 60 + k * 70), (2000, TOP + 64 + k * 70)], 2.4, "#b27a48", taper=.1, wmin=.7, seed=810 + k, op=.8)
                    for k in range(10))
    inner += blob(rect_pts(-900, TOP, 2000, TOP + 22), "#a8723f", .7)
    s.append(shape(tp, "#c98f5a", inner, w=4.4, seed=802))
    # кружка в глубине слева (та самая, «одну кружку»)
    mx, my = 150, TOP + 40
    s.append(blob(ellipse_pts(mx + 10, my + 6, 110, 16, 14), "#4a2a10", .35, blur(6)))
    s.append(shape([(mx + 70, my - 170), (mx + 150, my - 160), (mx + 150, my - 70), (mx + 70, my - 60)], "#3f8fa0", "", w=4.4, seed=820))
    s.append(blob([(mx + 92, my - 140), (mx + 124, my - 136), (mx + 124, my - 92), (mx + 92, my - 90)], "#efd9ae"))
    s.append(line([(mx + 92, my - 140), (mx + 124, my - 136), (mx + 124, my - 92), (mx + 92, my - 90)], 4, INK, seed=821))
    s.append(shape(rect_pts(mx - 100, my - 220, mx + 90, my, 24), "#4fa6b8",
                   blob(rect_pts(mx + 30, my - 220, mx + 90, my), "#3f8fa0") + line([(mx - 80, my - 190), (mx - 76, my - 40)], 8, "#bfe6ee", seed=822, op=.9),
                   w=4.6, seed=823))
    s.append(shape(ellipse_pts(mx - 5, my - 220, 95, 16, 16), "#2f6f7d", "", w=4, seed=824))
    lg = rad_grad([(0, "#fff3c8", .5), (1, "#fff3c8", 0)], 300, 200, 1200, 1200)
    s.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{lg})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def egg(setv, ridge, glow10):
    """setv — минуты против указателя (поворот верха), glow10 0..1 — вспышка «10»."""
    cx = EC[0]
    s = []
    s.append(blob(ellipse_pts(cx + 20, EBOT + 4, ERX * 1.15, 26, 20), "#4a2a10", .4, blur(10)))
    ep = egg_pts()
    # верх (жёлтый) и низ (белый) — одна фигура, низ поверх клипом
    inner = f'<rect x="{cx - 400}" y="{SEAM}" width="800" height="400" fill="#f7f3ea"/>'
    inner += blob([(cx + 90, ETOP - 20), (cx + 300, ETOP, 1), (cx + 300, SEAM, 1), (cx + 150, SEAM, 1)], "#e0a92a")
    inner += blob([(cx + 120, SEAM, 1), (cx + 300, SEAM, 1), (cx + 300, EBOT + 20, 1), (cx + 140, EBOT + 20)], "#dcd6c8")
    inner += line([(cx - 170, 520), (cx - 200, 640), (cx - 196, 760)], 16, "#fff2b0", seed=830, op=.9)
    inner += line([(cx - 190, 880), (cx - 180, 1010)], 12, "#ffffff", seed=831)
    # рёбра хвата на верхушке (крутятся вместе с верхом)
    for k in range(12):
        ph = math.radians(k * 30 + ridge)
        if math.cos(ph) < 0.1:
            continue
        x = cx + 120 * math.sin(ph)
        inner += line([(x, ETOP + 30), (x * 1 + (x - cx) * 0.15, ETOP + 120)], 4 * math.cos(ph) + 1, "#c98a16", taper=.3, seed=840 + k)
    # шкала: деления и числа на нижнем поясе верха
    yb = SEAM - 14
    rb = half_w(yb)
    for m in range(60):
        ph = math.radians((m - setv) * 6)
        c = math.cos(ph)
        if c < 0.12:
            continue
        x = cx + rb * math.sin(ph)
        big = m % 5 == 0
        inner += line([(x, yb), (x, yb - (30 if big else 16))], (5 if big else 2.6) * (0.5 + 0.5 * c), INK, taper=.1, wmin=.8, seed=850 + m)
    for m in range(0, 60, 5):
        ph = math.radians((m - setv) * 6)
        c = math.cos(ph)
        if c < 0.25:
            continue
        x = cx + (rb - 14) * math.sin(ph)
        y = yb - 52
        g = glow10 if m == 10 else 0.0
        fs = 52 * (1 + 0.45 * g)
        col = mix("#1c1622", "#e8461e", min(1, g * 1.4)) if g > 0 else INK
        inner += (f'<text transform="translate({f(x)} {f(y)}) scale({c:.3f} 1)" text-anchor="middle" font-family="IDB" '
                  f'font-weight="900" font-size="{f(fs)}" fill="{col}">{m}</text>')
    # шов
    w = half_w(SEAM)
    inner += line([(cx - w - 4, SEAM - 2), (cx, SEAM + 8), (cx + w + 4, SEAM - 2)], 5, INK, taper=.05, wmin=.9, seed=860)
    s.append(shape(ep, "#f8c43c", inner, w=6, seed=861))
    # указатель — красный треугольник на белом
    s.append(shape([(cx - 22, SEAM + 52, 1), (cx + 22, SEAM + 52, 1), (cx, SEAM + 16, 1)], "#e23a32", "", w=3.6, seed=862))
    # маленькая ножка-ободок внизу
    s.append(line([(cx - 160, EBOT - 30), (cx, EBOT - 18), (cx + 160, EBOT - 30)], 3.4, "#c9c2b2", seed=863))
    return "".join(s)


def setv_at(t):
    """Поворот верха: два хода руки, щелчок на 10."""
    a = ease_io(clamp((t - 24.62) / 0.5)) * 5.6
    b = ease_io(clamp((t - 25.3) / (CLICK - 25.3))) * 4.4
    v = a + b
    e = t - CLICK
    if e >= 0:
        v = 10 + 0.5 * math.exp(-e * 12) * math.sin(e * 60)
    return v


def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        lib.static_done()
    lib.dyn_begin()
    v = setv_at(t)
    e = t - CLICK
    glow = 0.0
    if e >= 0:
        glow = min(1.0, e / 0.08) * (0.75 + 0.25 * math.exp(-e * 5))
    s = [_ST["bg"]]
    # свечение вокруг «10»
    if glow > 0:
        gx, gy = EC[0], SEAM - 80
        g = rad_grad([(0, "#fff1a0", 1.0 * glow), (.5, "#ffd36a", .7 * glow), (1, "#ffd36a", 0)], gx, gy, 190, 120)
        s.append(f'<rect x="{gx - 200}" y="{gy - 140}" width="400" height="280" fill="url(#{g})"/>')
    s.append(egg(v, v * 6, glow))
    if glow > 0:
        gx, gy = EC[0], SEAM - 80
        g = rad_grad([(0, "#fff0b0", .55 * glow), (1, "#fff0b0", 0)], gx, gy, 130, 80)
        s.append(f'<rect x="{gx - 160}" y="{gy - 110}" width="320" height="220" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    # рука: заходит справа, два хода, уходит после щелчка
    k_in = ease_out(clamp((t - 24.12) / 0.42), 3)
    k_out = ease_in(clamp((t - (CLICK + 0.22)) / 0.45), 2)
    tw1 = ease_io(clamp((t - 24.62) / 0.5))
    rg = ease_io(clamp((t - 25.12) / 0.18))           # перехват назад
    tw2 = ease_io(clamp((t - 25.3) / (CLICK - 25.3)))
    twist = tw1 * (1 - rg) + tw2
    hx = EC[0] + 100 + 700 * (1 - k_in) + 500 * k_out - 40 * twist
    hy = ETOP + 150 - 30 * (1 - k_in) - 140 * k_out + 10 * twist
    rot = -92 + 18 * twist - 20 * k_out
    curl = 0.6 if 24.55 < t < CLICK + 0.2 else 0.0
    if t > 24.0:
        s.append(lay_hand(hx, hy, 1.05, rot, fsq=0.55, curl=curl))
    # щелчок
    if 0 <= e < 0.35:
        a = 1 - e / 0.35
        for k in range(7):
            ang = math.radians(200 + k * 24)
            r0 = 120 + 70 * ease_out(e / .35)
            cx0, cy0 = EC[0], SEAM - 70
            s.append(line([(cx0 + r0 * 1.5 * math.cos(ang), cy0 + r0 * math.sin(ang)),
                           (cx0 + (r0 + 60 * a) * 1.5 * math.cos(ang), cy0 + (r0 + 60 * a) * math.sin(ang))], 9 * a + 1, INK, taper=.5,
                          seed=880 + k))
    # хлёст в начале и наезд
    u = clamp((t - 24.0) / 0.2)
    k = ease_out(u, 3)
    ccx = 560 + 560 * (1 - k)
    ccy = 760
    vv = clamp((t - 24.0) / 2.72)
    scc = 1.3 + 0.12 * ease_io(vv)
    rot_c = 3 * (1 - k) + 0.4 * math.sin(t * 1.4)
    if e >= 0:
        kk = math.exp(-e * 7)
        scc *= 1 + 0.05 * kk * math.sin(min(e * 14, math.pi))
        ccy += 8 * kk * math.sin(e * 45)
    body = "".join(s)
    if u < 1:
        for j in range(7):
            yy = 300 + j * 150
            ln = 520 * (1 - k)
            x0 = 1100 - (j % 3) * 60
            body += line([(x0, yy), (x0 - ln, yy + 6)], 10 * (1 - k) + 2, INK, taper=.6, seed=890 + j)
    return svg(f'<rect width="{W}" height="{H}" fill="#efd9ae"/><g transform="{cam(ccx, ccy - 0, scc, rot_c)}">{body}</g>')
