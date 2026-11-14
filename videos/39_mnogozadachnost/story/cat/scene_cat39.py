"""Сцена «кот» рилса 39 (s18, 32.52–36.3, клип 32.32–36.3): крупно кот (как look/hero.png: ЛЕВОЕ от зрителя ухо загнуто,
зелёные глаза, по две оранжевые полоски на щеках, закрученный хвост с огоньком) сидит на столе Димы днём; фон — комната
Димы (den.py рилса 35, день), мягко размыт. Кот смотрит в камеру и моргает; на «Напиши» (32.52) дёргает ухом, на «кот»
(33.04) поднимает левую (от зрителя) лапу подушечками к зрителю и машет; на «думаешь» (34.24) наклоняет голову; на
«двух» (35.6) показывает два пальчика-подушечки (остальные поджаты) и подмигивает правым (от зрителя) глазом.
Камера медленно наезжает с первого кадра. Всё — функция общего времени ролика t."""
import math

import numpy as np

import cat
import den
import lib
from cat import CAT, CAT_SH, CX, CBOT, NECK, TAIL_PIVOT
from ink import ellipse_pts, fill_d
from lib import INK, W, H, back_out, blob, blur, cam, clamp, ease_io, line, mix, rect_pts, shape, smooth, svg

WT = {}


def word_t(w, after=32.3):
    if not WT:
        for x in lib.words():
            WT.setdefault(x["word"].strip(",.?!").lower(), []).append(x["start"])
    return min(v for v in WT[w] if v >= after)


T_A, T_B = 32.32, 36.3
T_NAP = word_t("напиши")       # 32.52
T_KOT = word_t("кот")          # 33.04
T_DUM = word_t("думаешь")      # 34.24
T_DVUH = word_t("двух")        # 35.60
PAD = "#e8823a"
_ST = {}

# кот на экране: точка (836, 1306) внутренних координат → (CAT_X, CAT_Y), масштаб CAT_S
CAT_S = 2.45
CAT_X = 575 - (870 - CX) * CAT_S
CAT_Y = 1270
DESK_Y = 1160                   # задний край столешницы на экране


# ───────────────────────── фон: комната Димы днём, размыта
def backdrop():
    w = [den.wall(0, day=True), den.window(0, day=True), den.board(0), den.shelf(0), den.desk_top(), den.lamp(0, on=0.0),
         den.mug(1150, 1080, 1.0, "#d8553a", fill="coffee")]
    g = lib.rad_grad([(0, "#fff4d0", .4), (1, "#fff4d0", 0)], 200, 500, 1100, 1000)
    w.append(f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    return "".join(w)


def desk_front():
    """Столешница, на которой сидит кот (резкая): дерево в перспективе, задний край у DESK_Y."""
    s = []
    top = [(-60, DESK_Y, 1), (1140, DESK_Y, 1), (1140, H + 40, 1), (-60, H + 40, 1)]
    g = lib.lin_grad([(0, "#b47a4c", 1), (1, "#8d5a34", 1)], 0, 0, 0, 1)
    inner = ""
    for k in range(7):
        y = DESK_Y + 40 + k * k * 22 + k * 30
        inner += line([(-60, y), (400, y + 4), (1140, y - 3)], 2.2 + k * .4, "#7a4a2a", seed=9100 + k, op=.45, taper=.1, wmin=.7)
    inner += blob([(-60, DESK_Y), (1140, DESK_Y), (1140, DESK_Y + 14), (-60, DESK_Y + 14)], "#d39a66")
    s.append(shape(top, f"url(#{g})", inner, w=5, seed=9000))
    return "".join(s)


# ───────────────────────── лапа подушечками к зрителю
def paw_front(P, ang, two=0.0, sd=0):
    """Ладошка лапы (внутр. координаты кота) в P, ang — наклон (0 — пальцами вверх). two 0..1 — два средних пальчика
    вытянуты вверх, крайние поджаты."""
    s = []
    rot = f'transform="translate({P[0]:.2f} {P[1]:.2f}) rotate({ang:.2f})"'
    # вытянутые пальчики (за ладонью, чтобы основание пряталось в ней)
    fing = ""
    if two > 0.01:
        for k, dx in enumerate((-9, 9)):
            L = 30 * two
            tip = (dx * 1.25, -24 - L)
            pts = [(dx - 8.5, -14), (dx * 1.25 - 9, tip[1] + 4), (tip[0] - 6, tip[1] - 6), (tip[0], tip[1] - 9), (tip[0] + 6, tip[1] - 6),
                   (dx * 1.25 + 9, tip[1] + 4), (dx + 8.5, -14)]
            fing += shape(pts, CAT, "", w=3.6, seed=sd + 30 + k)
            fing += blob(ellipse_pts(tip[0], tip[1] + 2, 6.2, 7.5, 10), PAD)
    palm = ellipse_pts(0, 0, 30, 31, 18)
    inner = blob(ellipse_pts(10, 8, 26, 28, 12), CAT_SH, .55)
    # главная подушечка
    main = [(-14, 16), (-10, 4), (0, 0), (10, 4), (14, 16), (8, 22), (0, 19), (-8, 22)]
    inner += blob(main, PAD)
    # пальчиковые подушечки: четыре по дуге; при two — крайние уходят (пальцы поджаты), средние уехали на пальчики
    beans = [(-21, -8), (-8, -17), (8, -17), (21, -8)]
    for k, (bx, by) in enumerate(beans):
        if k in (1, 2):
            if two > 0.35:
                continue
            r = 1 - two / 0.35 * 0.3
        else:
            r = 1 - 0.55 * two
        inner += blob(ellipse_pts(bx, by, 6.2 * r, 7 * r, 10, rot=(bx * 2)), PAD)
    if two > 0.35:   # поджатые крайние пальцы — складки
        for k, sx in enumerate((-1, 1)):
            inner += line([(sx * 26, -14), (sx * 18, -22), (sx * 10, -20)], 2.4, INK, seed=sd + 50 + k, taper=.4, wmin=.3)
    s.append(f'<g {rot}>{fing}{shape(palm, CAT, inner, w=4.4, seed=sd + 1)}</g>')
    return "".join(s)


def leg_up(P):
    """Левая (от зрителя) передняя лапа от плеча вверх к P: лапа-колбаска, без туши у плеча (сливается с грудью)."""
    S = np.array(cat.SHOULDER_L, float) + np.array([4, -10])
    P = np.array(P, float)
    d = P - S
    L = np.linalg.norm(d) + 1e-9
    u = d / L
    nrm = np.array([-u[1], u[0]])
    M = S + d * 0.5 + nrm * 10
    out = cat.sausage([tuple(S - u * 20), tuple(M), tuple(P)], 46, 40)
    o = [f'<path d="{fill_d(out)}" fill="{CAT}"/>']
    c = lib.clip_of(out)
    o.append(f'<g clip-path="url(#{c})">' + blob([tuple(S + nrm * 6 - u * 30), tuple(P + nrm * 26 + u * 30), tuple(P + nrm * 4 + u * 30),
                                                    tuple(S - nrm * 2 - u * 30)], CAT_SH, .5) + "</g>")
    o.append(line(out[2:-2], 4.6, seed=244, taper=.25, wmin=.25))
    return "".join(o)


def draw_cat(t, look, blink, tilt, tail, flick, raise_, wave, two, nod=0.0):
    st = cat.static_parts()
    br = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 2.6)
    o = [blob(ellipse_pts(870, 1306, 175, 20, 16), "#3a2010", .35, blur(6))]
    tw = f"rotate({tail:.2f} {TAIL_PIVOT[0]} {TAIL_PIVOT[1]})"
    o.append(f'<g transform="{tw}">{st["tail"]}</g>')
    sy = 1 + 0.012 * br
    o.append(f'<g transform="translate(0 {CBOT}) scale(1 {sy:.4f}) translate(0 {-CBOT})">{st["body"]}</g>')
    # лапа: в покое — стоит; поднимается дугой к плечу головы
    rest = np.array(cat.PAW_REST, float)
    up = np.array([716.0, 1112.0]) + np.array([10 * wave, -4 * abs(wave)])
    if raise_ < 0.02:
        o.append(cat.leg_left(tuple(rest)))
        P = None
    else:
        k = raise_
        mid = np.array([700.0, 1210.0])
        P = (1 - k) ** 2 * rest + 2 * (1 - k) * k * mid + k * k * up
        o.append(leg_up(tuple(P)))
    hy = -(sy - 1) * (CBOT - 1150) + nod
    hg = st["head"] + cat.ears(flick) + st["face"] + cat.eyes(look, blink) + cat.whiskers(t)
    o.append(f'<g transform="translate(0 {hy:.2f}) rotate({tilt:.2f} {NECK[0]} {NECK[1]})">{hg}</g>')
    if P is not None:
        ang = -18 + 14 * wave - 10 * (1 - raise_)
        o.append(paw_front(tuple(P + np.array([-4, -22]) * raise_), ang, two, sd=9300))
    o.append(f'<g transform="{tw}">{cat.flame(t, 1.3 + 0.12 * math.sin(t * 3.1))}</g>')
    return f'<g transform="translate({CAT_X - CX * CAT_S:.2f} {CAT_Y - CBOT * CAT_S:.2f}) scale({CAT_S:.4f})">{"".join(o)}</g>'


def sparkle(x, y, r, sd, rot=0.0):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.34
        a = math.radians(rot + i * 45 - 90)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, "#ffe27a", "", w=max(1.6, r * 0.1), seed=sd)


def frame(sid, t):
    if "bg" not in _ST:
        _ST["bg"] = backdrop()
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    # моргания: обычное и подмигивание правым (от зрителя) глазом на «двух»
    bl = 0.0
    for tb in (32.78, 34.62):
        if abs(t - tb) < .09:
            bl = max(bl, min(1, 1.7 * (1 - abs(t - tb) / .09)))
    wk = smooth(T_DVUH - 0.06, T_DVUH + 0.06, t) * (1 - smooth(T_DVUH + 0.5, T_DVUH + 0.62, t))
    blink = (max(bl, 0.2 * wk), max(bl, wk))
    raise_ = back_out(clamp((t - (T_KOT - 0.2)) / 0.3), 1.6)
    wave = math.sin((t - T_KOT) * 2 * math.pi * 2.2) * (1 - smooth(T_KOT + 0.75, T_KOT + 1.1, t)) * (t > T_KOT - 0.05)
    wave = wave * 0.9 + 0.25 * math.sin(t * 2.3)
    two = back_out(clamp((t - (T_DVUH - 0.16)) / 0.22), 2.0)
    tilt = -7 * smooth(T_DUM - 0.1, T_DUM + 0.2, t) * (1 - smooth(T_DVUH - 0.4, T_DVUH - 0.1, t)) + 1.5 * math.sin(t * 1.3)
    tilt += 5 * smooth(T_DVUH - 0.15, T_DVUH + 0.1, t)
    e = t - T_NAP
    flick = -16 * math.exp(-9 * max(0, e)) * math.sin(max(0, e) * 28) * (e > 0)
    e2 = t - T_DVUH
    flick += -10 * math.exp(-9 * max(0, e2)) * math.sin(max(0, e2) * 28) * (e2 > 0)
    tail = 6 * math.sin(t * 2.2) - 2
    look = (0.06 * math.sin(t * .9), -0.08)
    nod = 10 * math.sin(math.pi * clamp((t - (T_KOT - 0.05)) / 0.3))
    kitty = draw_cat(t, look, blink, tilt, tail, flick, raise_, wave, two, nod)
    # искорки на «двух» у лапы
    fx = ""
    e3 = t - T_DVUH
    if -0.02 < e3 < 0.7:
        px, py = CAT_X + (690 - CX) * CAT_S, CAT_Y + (1010 - CBOT) * CAT_S
        for j in range(3):
            kk = back_out(clamp((e3 - j * 0.05) / 0.2), 2.4) * (1 - smooth(0.45, 0.7, e3))
            if kk > 0.03:
                a = math.radians(-125 + j * 45)
                fx += sparkle(px + 40 + math.cos(a) * 125, py - 20 + math.sin(a) * 110, 26 * kk, 9500 + j, rot=20 * j)
    u = clamp((t - T_A) / (T_B - T_A))
    z = 1 + 0.08 * ease_io(u) + 0.035 * math.exp(-max(e3, 0) * 7) * math.sin(min(max(e3, 0) * 14, math.pi)) * (e3 > 0)
    zc = (540, 900)
    bg = f'<g {blur(7)}><g transform="{cam(700, 640, 1.45, 0)}">{_ST["bg"]}</g></g>'
    par = f'translate({zc[0]} {zc[1]}) scale({1 + (z - 1) * .4:.4f}) translate({-zc[0] - 12 * u} {-zc[1]})'
    fg = f'translate({zc[0]} {zc[1]}) scale({z:.4f}) translate({-zc[0]} {-zc[1]})'
    vg = lib.rad_grad([(0, "#3a2a1a", 0), (.6, "#3a2a1a", 0), (1, "#3a2a1a", .3)], 540, 900, 1180, 1400)
    return svg(f'<rect width="{W}" height="{H}" fill="#cfe0d6"/><g transform="{par}">{bg}</g>'
               f'<g transform="{fg}">{desk_front()}{kitty}{fx}</g><rect width="{W}" height="{H}" fill="url(#{vg})"/>')
