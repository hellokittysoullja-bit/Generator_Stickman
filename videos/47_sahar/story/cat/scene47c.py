"""Сцены рилса 47, агент «cat»: s08 (кот крупно: бровь, «?», мигающий огонёк), s13 (весы: гиря «ожидание взрослых» против
кусочка торта), s16 (призыв: телефон, кот печатает «кот», сердечки). Всё кодом (SVG → Chromium), время — общее время ролика.
Кот — cat.py (как look/hero.png), тушь — ink.py, надписи — шрифты CAV (Caveat) и IDB из base.html."""
import math

import cat as C
import lib
from c44 import kick, shake, wt
from lib import (INK, W, H, blob, blur, cam, clamp, ease_io, ease_out, back_out, ellipse_pts, f, line, lin_grad, rad_grad, mix,
                 rect_pts, shape, smooth, spring, svg)
from parts import sausage
from props import burst

_ST = {}
INK2 = "#1c1622"


def text(x, y, s, size, fill, font="CAV", weight=700, stroke=None, sw=0.0, rot=0.0, anchor="middle", extra=""):
    st = (f' stroke="{stroke}" stroke-width="{f(sw)}" stroke-linejoin="round" paint-order="stroke"' if stroke else "")
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="{font}" font-weight="{weight}" font-size="{f(size)}" '
            f'fill="{fill}"{st} transform="rotate({f(rot)} {f(x)} {f(y)})" {extra}>{s}</text>')


def heart_pts(cx, cy, r, n=22):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        out.append((cx + x * r / 17, cy + y * r / 17))
    return out


def heart(cx, cy, r, sd, rot=0.0, k=1.0):
    pts = heart_pts(0, 0, r)
    sh = blob([(p[0] + r * .15, p[1] + r * .1) for p in heart_pts(0, 0, r * .8)], "#c9304a", 1.0)
    hl = blob(ellipse_pts(-r * .42, -r * .4, r * .2, r * .13, 8, rot=-35), "#ff9aa8")
    return (f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({f(k)})">' +
            shape(pts, "#e8465a", sh + hl, w=3.4, seed=sd) + '</g>')


# ───────────────────────── общий фон «комната кота»
def room_bg(floor_y=1250):
    s = []
    g = lin_grad([(0, "#f1cfae", 1), (1, "#fbe9d2", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-700" y="-700" width="{W + 1400}" height="{floor_y + 700}" fill="url(#{g})"/>')
    for k in range(-9, 26):
        s.append(f'<rect x="{k * 90}" y="-700" width="34" height="{floor_y + 700}" fill="#e6bf9a" opacity=".0"/>')
    gl = rad_grad([(0, "#fff4d8", .75), (1, "#fff4d8", 0)], 640, 520, 800, 700)
    s.append(f'<rect x="-700" y="-700" width="{W + 1400}" height="{floor_y + 700}" fill="url(#{gl})"/>')
    fl = [(-700, floor_y, 1), (W + 700, floor_y, 1), (W + 700, H + 700, 1), (-700, H + 700, 1)]
    inner = "".join(line([(-700, floor_y + 60 + k * 110 + k * k * 9), (W + 700, floor_y + 52 + k * 110 + k * k * 9)], 3, "#8a5a34", taper=.1, wmin=.8,
                         seed=3000 + k, op=.45) for k in range(8))
    inner += blob(rect_pts(-700, floor_y, W + 700, floor_y + 26), "#d9a874")
    s.append(shape(fl, "#c48a5c", inner, w=5, seed=3010))
    return "".join(s)


# ═════════════════════════ s08: кот поднимает бровь
T_ZN = wt("странное")       # 13.76
T_A = wt("дальше")          # 12.8


def brow(rise, ang, sd):
    """Бровь правого (от зрителя) глаза во внутренних координатах кота; rise>0 — выше, ang — наклон внешнего конца вверх."""
    pts = [(850, 1032), (881, 1022), (912, 1030)]
    s = line(pts, 12, "#aaa4cc", taper=.7, wmin=.35, seed=sd, peak=.5)
    return f'<g transform="translate(0 {f(-rise)}) rotate({f(ang)} 881 1030)">{s}</g>'


def brow_l(sd, low):
    pts = [(760, 1042 + low), (790, 1034 + low), (820, 1040 + low)]
    return line(pts, 12, "#aaa4cc", taper=.7, wmin=.35, seed=sd, peak=.5)


def s08(t):
    cx, cb, sc = 430, 1360, 2.8
    q = t - 12.4
    # бровь: взлёт на «А дальше» с перелётом, на «странное» — вниз и внутрь
    up = 36 * spring(t - 12.72, 3.4, 9) if t >= 12.72 else 0
    down = smooth(T_ZN - 0.02, T_ZN + 0.12, t)
    rise = up * (1 - down) - 6 * down
    ang = -16 * smooth(12.72, 12.9, t) * (1 - down) + 9 * down
    low = 6 * down
    sq = 0.52 * smooth(T_ZN - 0.02, T_ZN + 0.16, t)
    bl = 0.0
    for tb in (13.28,):
        if 0 <= t - tb < 0.2:
            bl = max(bl, 1 - abs((t - tb) / 0.1 - 1))
    blink = max(sq, bl * (1 - down))
    tilt = (9 * smooth(12.7, 13.1, t) - 9 * down) + 1.2 * math.sin(t * 2.3)
    look = (0.85, -0.55) if t < T_ZN else (-0.5, 0.2)
    if 13.45 < t < T_ZN:
        look = (0.85 - 1.7 * smooth(13.45, 13.6, t), -0.55 + 0.7 * smooth(13.45, 13.6, t))
    flick = 14 * math.sin(max(0, t - 12.9) * 26) * math.exp(-max(0, t - 12.9) * 6) if t > 12.9 else 0
    pulse = 0.55 + 0.55 * abs(math.sin(t * 8.5))
    fk = 0.95 * (0.55 + 0.6 * pulse) if True else 1
    tail = 3 * math.sin(t * 3.1) + 2 * math.sin(t * 5.3) - 4
    hop = 10 * math.exp(-max(0, t - 12.72) * 9) * math.sin(max(0, t - 12.72) * 30) if t > 12.72 else 0
    eb = brow(rise, ang, 311) + brow_l(312, low + 10 * (1 - down))
    out = [_ST["bg"]]
    out.append(C.draw(cx, cb + hop, sc, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, extra_head=eb, flame_k=fk))
    # искры от огонька
    fw = C.flame_world(cx, cb, sc, tail)
    for j in range(7):
        ph = (t * 1.7 + j * .143) % 1
        px = fw[0] + 30 * math.sin(j * 2.1 + t * 3) + 50 * ph * (1 if j % 2 else -1) * .6
        py = fw[1] - 90 - 230 * ph
        r = (5 + 6 * ((j * 7) % 3) / 2) * (1 - ph) * (0.4 + pulse * .6)
        if r > 1.2:
            out.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(r)}" fill="{"#ffbe55" if j % 2 else "#ff8a2a"}"/>')
    # большой знак «?»
    p = back_out(clamp((t - 12.70) / 0.32), 2.2)
    if p > 0.01:
        wob = 4 * math.sin(t * 3.4)
        shk = 0
        if t > T_ZN:
            shk = 9 * math.exp(-(t - T_ZN) * 6) * math.sin((t - T_ZN) * 50)
        bob = 16 * math.sin(t * 4.2)
        scl = p * (1 + 0.1 * math.exp(-max(0, t - T_ZN) * 8) * math.sin(max(0, t - T_ZN) * 30))
        qx, qy = 880, 400 + bob
        out.append(f'<g transform="translate({f(qx + shk)} {f(qy)}) rotate({f(wob + 8)}) scale({f(scl)})">' +
                   text(6, 12, "?", 380, "#2a2430", "IDB", 900, "#2a2430", 18) +
                   text(0, 0, "?", 380, "#ff8a2a", "IDB", 900, INK, 12) + '</g>')
    # малые знаки «?»
    for j, (tt, x, y, r) in enumerate([(13.1, 130, 560, 130), (13.45, 190, 330, 90), (14.0, 780, 250, 80)]):
        pp = back_out(clamp((t - tt) / 0.28), 2.4)
        if pp > 0.01:
            out.append(f'<g transform="translate({f(x)} {f(y + 10 * math.sin(t * 4 + j))}) rotate({f(-14 + 10 * j + 5 * math.sin(t * 3 + j))}) '
                       f'scale({f(pp)})">' + text(0, 0, "?", r * 2.6, "#ffcf5a", "IDB", 900, INK, 8) + '</g>')
    # отлёт камеры
    k1, r1 = kick(t, [12.72], 0.035, 11)
    k2, r2 = kick(t, [T_ZN], 0.03, 12)
    u = clamp((t - 12.4) / 2.4)
    dx, dy = shake(t, T_ZN, 10, 10, 60)
    c = cam(560 - 40 * u + dx, 840 - 20 * u + dy, (1.0 + 0.1 * ease_io(u)) * k1 * k2, r1 + r2 + 0.9 - 1.6 * u)
    return f'<g transform="{c}">{"".join(out)}</g>'


# ═════════════════════════ s13: весы
PX, PY, R_BEAM, LCH = 540, 640, 330, 430
BRASS, BRASS_SH, BRASS_HL = "#c9973f", "#9a6e24", "#f0cf7a"
T_WAIT = wt("ожидании")     # 24.64
T_CAKE = wt("торте")        # 26.28
T_LAND = 23.82


def fall_y(t, t0=23.4):
    """Высота смещения гири над своим местом (0 — на тарелке): бросок вниз с начальной скоростью, потом отскок."""
    tau = t - t0
    if tau < 0:
        return -900.0
    g, v0, y0 = 3500.0, 1400.0, -900.0
    y = y0 + v0 * tau + 0.5 * g * tau * tau
    if y < 0:
        return y
    q = t - T_LAND
    return -34 * abs(math.sin(q * 11)) * math.exp(-q * 6) if q > 0 else 0.0


def theta(t):
    th = 1.2 * math.sin(t * 5.1)
    if t >= T_LAND:
        th += 5.0 * spring(t - T_LAND, 2.4, 4.5) - 1.2 * math.sin(t * 5.1) * smooth(T_LAND, T_LAND + .6, t)
    if t >= T_WAIT:
        th += 11.5 * spring(t - T_WAIT, 2.0, 5.2)
    if t >= T_CAKE:
        th -= 1.6 * math.exp(-(t - T_CAKE) * 5) * math.sin((t - T_CAKE) * 16)
    return th


def kettle(txt_pulse):
    """Гиря в локальных координатах: низ по центру в (0, 0)."""
    body = [(-118, 0, 1), (-134, -54), (-126, -118), (-86, -170), (0, -190), (86, -170), (126, -118), (134, -54), (118, 0, 1)]
    inner = blob([(70, -186), (136, -110), (136, 0), (50, 0), (96, -90)], "#1b1822", .9)
    inner += blob([(-96, -150), (-50, -176), (-8, -180), (-60, -150), (-100, -100), (-122, -80)], "#58526c", .8)
    inner += blob(ellipse_pts(-62, -132, 26, 12, 10, rot=-30), "#8a84a6")
    s = shape(body, "#34303f", inner, w=6, seed=3101)
    ho = [(-72, -168), (-86, -214), (-50, -262), (0, -274), (50, -262), (86, -214), (72, -168),
          (44, -172), (48, -208), (22, -232), (0, -238), (-22, -232), (-48, -208), (-44, -172)]
    outer = [(-76, -166, 1), (-92, -216), (-54, -268), (0, -282), (54, -268), (92, -216), (76, -166, 1)]
    hole = [(50, -172, 1), (52, -208), (26, -236), (0, -242), (-26, -236), (-52, -208), (-50, -172, 1)]
    hd = lib.fill_d(outer) + lib.fill_d(hole)
    hs = (f'<path d="{hd}" fill="#34303f" fill-rule="evenodd"/>'
          f'<path d="{lib.ink_closed(outer, 5.6, seed=3102)}" fill="{INK}"/><path d="{lib.ink_closed(hole, 4.6, seed=3103)}" fill="{INK}"/>')
    hs += blob([(-70, -214), (-44, -252), (-16, -266), (-30, -246), (-56, -220)], "#6a6484")
    _ = ho
    tx = text(0, -102, "ожидание", 64, "#ffffff", "CAV", 700, None, 0, 0)
    tx += text(0, -48, "взрослых", 64, "#ffd86a", "CAV", 700, None, 0, 0)
    return hs + s + f'<g transform="translate(0 -100) scale({f(1 + txt_pulse)}) translate(0 100)">{tx}</g>'


def cake_slice(sd=3200):
    """Кусочек торта сбоку, низ по центру в (0, 0), ширина ~110."""
    base = [(-58, 0, 1), (-58, -26), (-52, -50, 1), (-30, -86, 1), (58, -86, 1), (58, 0, 1)]
    sponge = [(-58, 0, 1), (58, 0, 1), (58, -26, 1), (-58, -26, 1)]
    s = shape(base, "#f4d9a4", blob(rect_pts(-60, -26, 60, -20), "#fff6e6") + blob(rect_pts(-60, -56, 60, -50), "#fff6e6") +
              blob(rect_pts(30, -90, 62, 0), "#d9b274", .8), w=4.4, seed=sd)
    cream = [(-52, -50, 1), (-30, -86, 1), (58, -86, 1), (58, -62, 1), (-6, -62), (-44, -56)]
    s += shape([(-30, -92, 1), (58, -92, 1), (58, -80, 1), (-30, -80, 1)], "#fffaf0", "", w=3.2, seed=sd + 1)
    s += shape(ellipse_pts(14, -108, 17, 15, 10), "#e8465a", blob(ellipse_pts(20, -104, 9, 8, 8), "#b3243b") +
               blob(ellipse_pts(8, -112, 4, 3, 6), "#ff9aa8"), w=3.2, seed=sd + 2)
    s += line([(12, -122), (10, -134)], 3, "#4a7a2a", seed=sd + 3)
    _ = (sponge, cream)
    return s


def pan(x, y):
    """Тарелка весов: верх обода в (x, y)."""
    bowl = [(x - 175, y, 1), (x - 150, y + 20), (x - 90, y + 34), (x, y + 38), (x + 90, y + 34), (x + 150, y + 20), (x + 175, y, 1)]
    inner = blob([(x - 175, y), (x + 175, y), (x + 150, y + 12), (x - 150, y + 12)], BRASS_HL, .8)
    inner += blob([(x + 30, y), (x + 175, y), (x + 150, y + 22), (x + 60, y + 38)], BRASS_SH, .85)
    s = shape(bowl, BRASS, inner, w=5, seed=int(abs(x)) % 997 + 3300)
    return s


def scales_static():
    s = []
    g = lin_grad([(0, "#f7f0dc", 1), (1, "#efe6cf", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-700" y="-700" width="{W + 1400}" height="{H + 1400}" fill="url(#{g})"/>')
    for k in range(-8, 26):
        s.append(f'<rect x="{k * 60}" y="-700" width="2" height="{H + 1400}" fill="#c9bfa4" opacity=".0"/>')
    # пол-линия и тень
    s.append(line([(-300, 1235), (1400, 1235)], 4, "#8c7c5a", taper=.05, wmin=.9, seed=3400))
    s.append(blob(ellipse_pts(540, 1236, 330, 22, 18), "#6a5a3a", 1.0, blur(10)))
    # стойка и основание
    post = [(520, PY, 1), (560, PY, 1), (564, 1235, 1), (516, 1235, 1)]
    s.append(shape(post, BRASS, blob(rect_pts(540, PY, 566, 1235), BRASS_SH, .85) + blob(rect_pts(522, PY, 530, 1235), BRASS_HL, .7), w=5, seed=3410))
    base = [(360, 1256, 1), (400, 1216), (680, 1216), (720, 1256, 1)]
    s.append(shape(base, BRASS, blob([(540, 1196), (700, 1196), (720, 1236), (540, 1236)], BRASS_SH, .85) +
                   blob(rect_pts(400, 1198, 640, 1206), BRASS_HL, .7), w=5, seed=3411))
    return "".join(s)


def beam_group():
    bar = rect_pts(-R_BEAM - 26, -15, R_BEAM + 26, 15, 14)
    s = shape(bar, BRASS, blob(rect_pts(-R_BEAM, 2, R_BEAM, 16), BRASS_SH, .85) + blob(rect_pts(-R_BEAM + 10, -12, R_BEAM - 10, -6), BRASS_HL, .75),
              w=5, seed=3420)
    for sx in (-1, 1):
        s += shape(ellipse_pts(sx * R_BEAM, 0, 19, 19, 12), BRASS_HL, blob(ellipse_pts(sx * R_BEAM + 4, 4, 11, 11, 8), BRASS_SH, .6), w=3.6, seed=3421 + sx)
    # стрелка
    s += shape([(-12, -14, 1), (0, -96, 1), (12, -14, 1)], "#b83a3a", blob([(0, -96), (12, -14), (0, -14)], "#8a2424", .8), w=4, seed=3423)
    return s


def s13(t):
    th = theta(t)
    a = math.radians(th)
    lx, ly = PX - R_BEAM * math.cos(a), PY + R_BEAM * math.sin(a)
    rx, ry = PX + R_BEAM * math.cos(a), PY - R_BEAM * math.sin(a)
    out = [_ST["bg"]]
    # цепи
    pl, pr = (lx, ly + LCH), (rx, ry + LCH)
    for (bx, by), (px, py) in ((((lx, ly)), pl), (((rx, ry)), pr)):
        for sx, sd in ((-150, 1), (150, 2), (0, 3)):
            if sx == 0:
                continue
            out.append(line([(bx, by + 6), (px + sx, py + 2)], 4.2, "#7a5a1c", taper=.05, wmin=.9, seed=3430 + sd))
    # тарелки
    out.append(pan(pl[0], pl[1]))
    out.append(pan(pr[0], pr[1]))
    # гиря
    fy = fall_y(t)
    sq = 0.0
    if t >= T_LAND:
        sq = 0.07 * math.exp(-(t - T_LAND) * 12) * math.cos((t - T_LAND) * 30)
    if t >= T_WAIT:
        sq += 0.08 * math.exp(-(t - T_WAIT) * 11) * math.cos((t - T_WAIT) * 28)
    pulse = 0.05 * math.exp(-max(0, t - T_WAIT) * 9) * math.sin(max(0, t - T_WAIT) * 24) if t >= T_WAIT else 0
    gy = pl[1] + fy
    rot_k = 8 * math.sin(clamp((t - 23.4) / 0.42) * math.pi * .5) * (1 - clamp((t - 23.4) / 0.42)) if t < 23.82 else 0
    out.append(f'<g transform="translate({f(pl[0])} {f(gy)}) rotate({f(rot_k - th * .1)}) scale({f(1 - sq * .6)} {f(1 + sq)})">{kettle(pulse)}</g>')
    # торт: прыжок на «торте»
    q = t - T_CAKE
    cy_off, sqx = 0.0, 1.0
    rot_c = 2 * math.sin(t * 4)
    if q >= 0:
        dur = 0.62
        if q < dur:
            u = q / dur
            cy_off = -230 * 4 * u * (1 - u)
            sqx = 1 - 0.12 * math.sin(math.pi * u)
            rot_c = 14 * math.sin(2 * math.pi * u)
        else:
            qq = q - dur
            cy_off = 0
            sqx = 1 + 0.18 * math.exp(-qq * 12) * math.cos(qq * 34)
            sqx = max(sqx, 0.8)
    small_bob = 3 * math.sin(t * 6.3)
    out.append(f'<g transform="translate({f(pr[0] - 10)} {f(pr[1] + cy_off + small_bob)}) rotate({f(rot_c)}) scale({f(1.12 * sqx)} {f(1.12 / sqx)})">{cake_slice()}</g>')
    if 0.0 <= q - 0.62 < 0.3:
        out.append(burst(pr[0] - 10, pr[1] - 40, 1.0, (q - 0.62) / 0.3, seed=3440, n=7, r0=70, r1=140))
    if 0 <= t - T_LAND < 0.3:
        out.append(burst(pl[0], pl[1] - 20, 1.3, (t - T_LAND) / 0.3, seed=3450, n=8, r0=150, r1=230))
    if 0 <= t - T_WAIT < 0.32:
        out.append(burst(pl[0], pl[1] + 10, 1.4, (t - T_WAIT) / 0.32, seed=3460, n=9, r0=160, r1=250))
    # подпись «торт»
    lab = clamp((t - 24.0) / 0.3)
    out.append(f'<g transform="translate({f(pr[0])} {f(pr[1] + 100)}) scale({f(back_out(lab, 2))})">' + text(0, 0, "торт", 76, "#3a2a20", "CAV", 700) + '</g>')
    # балка поверх цепей
    out.append(f'<g transform="rotate({f(-th)} {PX} {PY}) translate({PX} {PY})">{beam_group()}</g>')
    out.append(shape(ellipse_pts(PX, PY, 30, 30, 14), BRASS_HL, blob(ellipse_pts(PX + 5, PY + 5, 18, 18, 10), BRASS_SH, .7), w=4.4, seed=3470))
    out.append(shape(ellipse_pts(PX, PY, 11, 11, 8), "#7a5a1c", "", w=3, seed=3471))
    # камера: влёт, наезд, толчки
    k1, r1 = kick(t, [T_WAIT], 0.04, 10)
    k2, r2 = kick(t, [T_CAKE], 0.03, 12)
    k0, r0 = kick(t, [T_LAND], 0.03, 12)
    u = clamp((t - 23.4) / 3.7)
    dx, dy = shake(t, T_WAIT, 14, 9, 58)
    c = cam(540 + 20 * (1 - u) + dx, 860 + dy, (1.0 + 0.05 * ease_io(u)) * k0 * k1 * k2, r0 + r1 + r2 + 1.1 - 1.8 * u)
    return f'<g transform="{c}">{"".join(out)}</g>'


# ═════════════════════════ s16: призыв — кот печатает «кот»
PHK = 1.1
PHC = (500, 860)
CATX, CATB, CATS = 790, 1380, 1.5
T_NAP = wt("напиши")             # 30.96
T_KOT = wt("кот", after=31.0)    # 31.48
TAPS = [T_KOT + 0.04, T_KOT + 0.17, T_KOT + 0.30]
T_SEND = 32.18
KEYS = [(92.5, 274), (110.5, 312), (77.5, 350)]   # к, о, т: ряд сверху вниз (локальные координаты телефона)
SEND = (125, 214)
PW_, PH_ = 400, 800


def ph2w(p):
    return (PHC[0] + p[0] * PHK, PHC[1] + p[1] * PHK)


def phone_frame(t):
    """Корпус и экран (локально, центр телефона в 0,0)."""
    body = rect_pts(-PW_ / 2, -PH_ / 2, PW_ / 2, PH_ / 2, 56)
    s = shape(body, "#22222a", blob(rect_pts(150, -380, 200, 380), "#15151b", .9), w=5.5, seed=3501)
    x0, x1, y0, y1 = -PW_ / 2 + 16, PW_ / 2 - 16, -PH_ / 2 + 16, PH_ / 2 - 16
    sc = []
    sc.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#fbf6ec"/>')
    # шапка и «пост»
    sc.append(blob(rect_pts(x0, y0, x1, y0 + 60), "#f0782e"))
    sc.append(blob(ellipse_pts(x0 + 36, y0 + 30, 14, 14, 10), "#ffffff"))
    sc.append(blob(rect_pts(x0 + 62, y0 + 22, x0 + 190, y0 + 38, 8), "#ffe2c8"))
    sc.append(shape(rect_pts(x0 + 16, y0 + 74, x1 - 16, y0 + 250, 18), "#f7d8a8",
                    blob([(x0 + 16, y0 + 190), (x1 - 16, y0 + 150), (x1 - 16, y0 + 250), (x0 + 16, y0 + 250)], "#e8b870", .9) +
                    blob(ellipse_pts(0, y0 + 126, 52, 52, 14), "#f0782e") +
                    blob([(-16, y0 + 100), (30, y0 + 126), (-16, y0 + 152)], "#fff4e0"), w=3.6, seed=3502))
    # комментарии: статичные строки
    rows = [(-70, "#7fb6d4"), (-6, "#9ccf8a")]
    for i, (yy, col) in enumerate(rows):
        yy += 60 - 20
        sc.append(blob(ellipse_pts(x0 + 30, yy, 17, 17, 10), col))
        sc.append(blob(rect_pts(x0 + 62, yy - 14, x0 + 62 + 150 - i * 30, yy - 3, 5), "#3a3330", .85))
        sc.append(blob(rect_pts(x0 + 62, yy + 4, x0 + 62 + 220 - i * 50, yy + 14, 5), "#b9aea0"))
    # новые комментарии «кот» от зрителей
    for i, (tt, col) in enumerate([(T_SEND + 0.12, "#f0782e"), (33.05, "#b48ad8"), (33.6, "#e8b23a")]):
        p = back_out(clamp((t - tt) / 0.3), 2.2)
        if p < 0.02:
            continue
        yy = 106 + 52 * i + 12
        o = (f'<g transform="translate({f(x0 + 30)} {f(yy)}) scale({f(p)}) translate({f(-x0 - 30)} {f(-yy)})">' +
             blob(ellipse_pts(x0 + 30, yy, 17, 17, 10), col) +
             shape(rect_pts(x0 + 60, yy - 22, x0 + 60 + 112, yy + 20, 18), "#f1e6d2", "", w=3, seed=3510 + i) +
             text(x0 + 116, yy + 12, "кот", 34, "#2a2430", "IDB", 900) +
             (heart(x1 - 34, yy, 15 + 2 * math.sin(t * 9 + i), 3520 + i) if t > tt + 0.3 else "") + '</g>')
        sc.append(o)
    # поле ввода
    fy = 232
    sent = t >= T_SEND
    sc.append(shape(rect_pts(x0 + 10, fy - 30, x1 - 10, fy + 30, 28), "#ffffff", "", w=3.6, seed=3530))
    typed = "" if sent else "".join(ch for ch, tk in zip("кот", TAPS) if t >= tk)
    if not typed and not sent:
        sc.append(blob(rect_pts(x0 + 36, fy - 6, x0 + 150, fy + 6, 5), "#cfc6b4"))
    if typed:
        sc.append(text(x0 + 30, fy + 20, typed, 56, "#2a2430", "IDB", 900, anchor="start"))
    # курсор
    if T_NAP <= t < T_SEND:
        wdt = 0 if not typed else 31 * len(typed) + 4
        blink = (int((t - T_NAP) * 3.6) % 2 == 0) or typed
        cp = back_out(clamp((t - T_NAP) / 0.12), 2)
        if blink and cp > 0:
            sc.append(f'<rect x="{f(x0 + 34 + wdt)}" y="{f(fy - 22 * cp)}" width="5" height="{f(44 * cp)}" rx="2" fill="#f0782e"/>')
        if t - T_NAP < 0.35:
            u = (t - T_NAP) / 0.35
            sc.append(f'<circle cx="{f(x0 + 38)}" cy="{f(fy)}" r="{f(20 + 50 * u)}" fill="none" stroke="#f0782e" stroke-width="{f(6 * (1 - u) + 1)}"/>')
    # кнопка отправки
    sp = 1 + 0.16 * math.exp(-max(0, t - T_SEND) * 10) * math.cos(max(0, t - T_SEND) * 30) if t >= T_SEND else 1
    act = 1 if (typed and t >= TAPS[-1]) else 0
    sc.append(f'<g transform="translate({SEND[0]} {SEND[1] + 18}) scale({f(sp)})">' +
              shape(ellipse_pts(0, 0, 25, 25, 14), "#f0782e" if (act or sent) else "#d8cdb8", "", w=3.2, seed=3531) +
              line([(-10, 8), (0, -10), (10, 8)], 5, "#ffffff", taper=.1, wmin=.9, seed=3532) + '</g>')
    # клавиатура
    sc.append(blob(rect_pts(x0, 256, x1, y1, 0), "#d8d3c6"))
    pressed = {}
    for i, tk in enumerate(TAPS + [T_SEND]):
        if 0 <= t - tk < 0.14:
            pressed[i] = 1 - (t - tk) / 0.14
    rows_k = [(274, 10, -156), (312, 9, -138), (350, 7, -100)]
    for ri, (ky, n, kx0) in enumerate(rows_k):
        for ci in range(n):
            kx = kx0 + ci * 35.5
            hit = None
            for i, kp in enumerate(KEYS):
                if kp[1] == ky and abs(kp[0] - kx) < 14:
                    hit = pressed.get(i)
            col = "#ffd9b0" if hit else "#ffffff"
            sc.append(shape(rect_pts(kx - 15, ky - 14, kx + 15, ky + 14, 7), col, "", w=2.4, seed=3600 + ri * 20 + ci))
    c = lib.clip_of(rect_pts(x0, y0, x1, y1, 44))
    s += f'<g clip-path="url(#{c})">{"".join(sc)}</g>'
    s += blob(rect_pts(-46, -PH_ / 2 + 22, 46, -PH_ / 2 + 40, 9), "#15151b")
    return s


def paw_target(t):
    """Точка лапы (мир) и сила нажатия: подход, три нажатия, нажатие «отправить»."""
    rest = ph2w((130, 150))
    hover = ph2w((90, 300))
    pts = [ph2w(k) for k in KEYS]
    send = ph2w(SEND)
    P = list(rest)
    press = 0.0
    # подход к клавиатуре с «Напиши»
    a = ease_io(clamp((t - 30.8) / 0.6))
    P = [rest[0] + (hover[0] - rest[0]) * a, rest[1] + (hover[1] - rest[1]) * a - 30 * math.sin(math.pi * a)]
    if t > 32.6:
        b = ease_io(clamp((t - 32.5) / 0.5))
        P = [P[0] + (rest[0] - P[0]) * b, P[1] + (rest[1] - P[1]) * b]
    seq = list(zip(TAPS, pts)) + [(T_SEND, send)]
    for tk, kp in seq:
        w = math.exp(-((t - tk) / 0.055) ** 2)
        lift = math.exp(-((t - tk + 0.07) / 0.09) ** 2) * 0
        P = [P[0] + (kp[0] - P[0]) * w, P[1] + (kp[1] - P[1]) * w - 18 * (1 - w) * math.exp(-((t - tk) / 0.14) ** 2) - lift]
        press = max(press, w)
    return P, press


def s16(t):
    # вход телефона: подскок снизу с перелётом
    e = spring(t - 30.8, 2.6, 7.5)
    dy = (1 - e) * 140
    ph = (f'<g transform="translate({f(PHC[0])} {f(PHC[1] + dy)}) rotate({f(0.6 * math.sin(t * 1.7) + 3 * (1 - e))}) scale({PHK})">'
          f'{phone_frame(t)}</g>')
    out = [_ST["bg"]]
    out.append(blob(ellipse_pts(PHC[0] + 20, 1244, 250, 26, 16), "#6a4a2a", 1.0, blur(10)))
    # подставка
    out.append(shape([(PHC[0] - 130, 1236, 1), (PHC[0] - 80, 1196), (PHC[0] + 80, 1196), (PHC[0] + 130, 1236, 1)], "#3a3a44",
                     blob(rect_pts(PHC[0], 1196, PHC[0] + 140, 1240), "#25252d", .9), w=4.6, seed=3550))
    out.append(ph)
    # кот
    P, press = paw_target(t)
    pi = C.to_int(P, CATX, CATB, CATS)
    blink = 0.0
    for tb in (31.9, 33.4):
        if 0 <= t - tb < 0.2:
            blink = 1 - abs((t - tb) / 0.1 - 1)
    look = (-0.9, 0.45) if t < T_SEND + 0.6 else (-0.2, -0.3)
    tilt = -5 - 2 * math.sin(t * 2.2) + (4 if t > 33.0 else 0)
    flick = 12 * math.sin(max(0, t - 31.2) * 24) * math.exp(-max(0, t - 31.2) * 7) if t > 31.2 else 0
    tail = 7 * math.sin(t * 3.0) + 4 * math.sin(t * 4.9)
    out.append(C.draw(CATX, CATB, CATS, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw=pi, press=press, flame_k=0.95))
    # сердечки
    for j in range(9):
        t0 = T_SEND + 0.08 + j * 0.26
        u = (t - t0) / 1.5
        if u < 0 or u > 1:
            continue
        bx = [380, 470, 330, 520, 420, 560, 300, 500, 400][j]
        x = bx + 38 * math.sin(u * 5 + j)
        y = 360 - 330 * ease_out(u, 1.6) + 30
        sc = back_out(clamp(u / 0.18), 2) * (1 - smooth(0.82, 1.0, u))
        if sc > 0.03:
            out.append(heart(x, y, 44 + 8 * (j % 3), 3560 + j, rot=10 * math.sin(u * 6 + j), k=sc))
    k1, r1 = kick(t, [T_NAP, T_KOT], 0.02, 12)
    k3, r3 = kick(t, [T_SEND], 0.02, 12)
    u = clamp((t - 30.8) / 3.9)
    c = cam(600 + 10 * (1 - u), 900, (1.1 + 0.05 * ease_io(u)) * k1 * k3, r1 + r3 + 0.8 - 1.2 * u)
    return f'<g transform="{c}">{"".join(out)}</g>'


def frame(sid, t):
    if not _ST:
        lib.DEFS.clear()
        _ST["bg"] = None
    if _ST.get("sid") != sid:
        lib.DEFS.clear()
        lib._uid[0] = 0
        _ST["bg"] = scales_static() if sid == "s13" else room_bg()
        _ST["sid"] = sid
        lib.static_done()
    lib.dyn_begin()
    body = {"s08": s08, "s13": s13, "s16": s16}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#f6ead6"/>{body}')


_ = (INK2, mix, sausage)
