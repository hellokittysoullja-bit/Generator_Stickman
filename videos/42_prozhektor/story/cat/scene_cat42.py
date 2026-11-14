"""Сцена «кот» рилса 42 (основа — cat рилса 39: кот как look/hero.png — ЛЕВОЕ от зрителя ухо загнуто, зелёные глаза,
по две оранжевые полоски на щеках, закрученный хвост с огоньком). Вечер дома: комната Димы (den.py, ночь, лампа),
диван. Всё — функция общего времени ролика t.
s16 (28.85–31.1, клип 28.65–31.3): кот ЛЕЖИТ на диване «буханкой», над ним вырастает маленький пузырь мыслей — Дима
в горчичной футболке задом наперёд (белая бирка под подбородком); на «кот» (30.64) кот хитро щурится и ухмыляется,
хвост бьёт, огонёк вспыхивает. Камера медленно наезжает с первого кадра.
s17 (31.1–33.0, клип 30.9–33.2): кот сидит на диване крупно, смотрит в камеру; на «Напиши» (31.2) поднимает лапу
подушечками к зрителю и дважды «тыкает» в экран; на «кот» (31.68) огонёк вспыхивает втрое, искры летят вверх.
s18 (33.0–34.9, клип 32.8–34.9): кот ещё крупнее; на «смотрят» (34.16) глаза уходят влево, вправо, и он подмигивает."""
import math

import numpy as np

import cat
import den
import lib
import people
from cat import CAT, CAT_SH, CAT_FUR, CAT_EDGE, CX, CBOT, NECK, TAIL_PIVOT
from ink import ellipse_pts, fill_d, fur
from lib import INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, line, rect_pts, shape, smooth, svg, T

WT = {}


def word_t(w, after):
    if not WT:
        for x in lib.words():
            WT.setdefault(x["word"].strip(",.?!").lower(), []).append(x["start"])
    return min(v for v in WT[w] if v >= after)


T_VECH = word_t("вечеру", 28.0)        # 29.04
T_KOT1 = word_t("кот", 30.0)           # 30.64
T_NAP = word_t("напиши", 31.0)         # 31.20
T_KOT2 = word_t("кот", 31.5)           # 31.68
T_SMOT = word_t("смотрят", 34.0)       # 34.16
PAD = "#e8823a"
_ST = {}

# ───────────────────────── диван (мир 1080×1920)
SOFA, SOFA_SH, SOFA_HI, SOFA_DK = "#7d6a9a", "#5e4d7a", "#9786b2", "#3f3256"
SEAT_T, SEAT_F, SOFA_B = 1150.0, 1222.0, 1460.0      # верх сиденья (дальний край), передний край, низ дивана


def sofa_back():
    s = []
    s.append(blob(rect_pts(-80, 1250, 1160, 1500), "#120c18", .45, blur(16)))
    # спинка
    back = [(-60, 1180, 1), (-60, 830), (-20, 790), (1100, 790), (1140, 830), (1140, 1180, 1)]
    inner = blob([(-60, 1060), (1140, 1060), (1140, 1190), (-60, 1190)], SOFA_SH, .8)
    inner += line([(10, 812), (500, 806), (1060, 812)], 6, SOFA_HI, seed=7011, op=.7)
    s.append(shape(back, SOFA, inner, w=5, seed=7010))
    # две подушки спинки
    for k, (x0, x1) in enumerate(((10, 530), (550, 1070))):
        pts = [(x0, 1150, 1), (x0 - 6, 900), (x0 + 30, 852), (x1 - 30, 852), (x1 + 6, 900), (x1, 1150, 1)]
        inn = blob([(x0, 1040), (x1, 1040), (x1, 1160), (x0, 1160)], SOFA_SH, .7)
        inn += line([(x0 + 40, 880), (x1 - 60, 876)], 5, SOFA_HI, seed=7021 + k, op=.8)
        inn += line([((x0 + x1) / 2 - 30, 960), ((x0 + x1) / 2, 980), ((x0 + x1) / 2 + 26, 962)], 2.6, SOFA_DK, seed=7031 + k, op=.6)
        s.append(shape(pts, SOFA, inn, w=4.6, seed=7020 + k))
    # подушка-думка в углу справа (жёлтая, пустая)
    s.append(shape(T([(-70, -60), (70, -66), (78, 60), (-74, 64)], 960, 1080, 1, -10), "#e0b04a",
                   blob(T([(0, -66), (78, -66), (78, 64), (10, 64)], 960, 1080, 1, -10), "#bf8c2c", .8), w=4.4, seed=7040))
    return "".join(s)


def sofa_seat():
    s = []
    # сиденье: верх в перспективе и передняя грань
    top = [(-60, SEAT_T, 1), (1140, SEAT_T, 1), (1160, SEAT_F, 1), (-80, SEAT_F, 1)]
    s.append(shape(top, SOFA_HI, blob([(-80, SEAT_T + 40), (1160, SEAT_T + 40), (1160, SEAT_F), (-80, SEAT_F)], SOFA, .7) +
                   line([(540, SEAT_T + 4), (540, SEAT_F - 2)], 3, SOFA_DK, seed=7051, op=.6), w=4.6, seed=7050))
    front = [(-80, SEAT_F, 1), (1160, SEAT_F, 1), (1160, SOFA_B, 1), (-80, SOFA_B, 1)]
    inner = blob([(-80, SOFA_B - 70), (1160, SOFA_B - 70), (1160, SOFA_B), (-80, SOFA_B)], SOFA_DK, .8)
    inner += blob([(-80, SEAT_F), (1160, SEAT_F), (1160, SEAT_F + 26), (-80, SEAT_F + 26)], SOFA_SH, .8)
    inner += line([(540, SEAT_F + 4), (540, SOFA_B - 60)], 3, SOFA_DK, seed=7061, op=.6)
    s.append(shape(front, SOFA, inner, w=5, seed=7060))
    # пледик свисает слева
    plaid = [(60, SEAT_T + 10, 1), (330, SEAT_T + 6), (350, SEAT_F + 120), (300, SEAT_F + 190), (220, SEAT_F + 160), (140, SEAT_F + 200),
             (70, SEAT_F + 150)]
    pin = "".join(line([(60 + k * 46, SEAT_T + 8), (70 + k * 46, SEAT_F + 170)], 7, "#e7c9a0", seed=7071 + k, op=.8) for k in range(6))
    pin += blob([(60, SEAT_F + 40), (350, SEAT_F + 40), (350, SEAT_F + 220), (60, SEAT_F + 220)], "#000000", .14)
    s.append(shape(plaid, "#c0513f", pin, w=4.4, seed=7070))
    return "".join(s)


def room_back(t):
    w = [den.wall(t), den.window(t), den.shelf(t), den.board(t)]
    # торшер справа (тёплый свет вечера)
    w.append(line([(1010, 1300), (1010, 560)], 12, INK, taper=.02, wmin=.95, seed=7101) + line([(1010, 1300), (1010, 560)], 6, "#c8a66a",
                                                                                                    taper=.02, wmin=.95, seed=7102))
    w.append(shape([(930, 560, 1), (1090, 560, 1), (1060, 440, 1), (960, 440, 1)], "#f2d79a",
                   blob([(1030, 440), (1060, 440), (1090, 560), (1050, 560)], "#d9b56e", .9), w=4.4, seed=7103))
    w.append(den.floor())
    return "".join(w)


def evening_light(t):
    fl = 1 + .02 * math.sin(t * 5.3)
    g = lib.rad_grad([(0, "#ffd890", .5 * fl), (.45, "#ffbe6a", .2), (1, "#ffbe6a", 0)], 960, 560, 900, 800)
    g2 = lib.rad_grad([(0, "#000000", 0), (.55, "#000000", 0), (1, "#0a0c1e", .55)], 560, 1000, 1200, 1300)
    return (f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
            f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g2})"/>')


# ───────────────────────── кот лёжа «буханкой» (внутренние координаты кота, как cat.py)
HEAD_D = (-34.0, 96.0)        # сдвиг головы от сидячей позы
LOAF_TAIL = 176.0             # сдвиг хвоста вправо
TAIL_PIV_L = (TAIL_PIVOT[0] + LOAF_TAIL, TAIL_PIVOT[1] + 10)


def loaf_static():
    s = []
    body = [(770, 1300), (758, 1262), (778, 1214), (840, 1186), (960, 1176), (1060, 1190), (1112, 1230), (1118, 1280), (1100, 1304)]
    bp = fur(body, 7, 7, seed=7201)
    inner = blob([(930, 1250), (1130, 1230), (1130, 1310), (900, 1310)], CAT_SH, .9)
    inner += blob([(860, 1190), (980, 1180), (1060, 1196), (1000, 1214), (880, 1214)], CAT_FUR, .55)
    for i, st in enumerate([[(900, 1200), (912, 1214)], [(960, 1196), (968, 1212)], [(1020, 1204), (1026, 1220)], [(990, 1240), (1000, 1256)]]):
        inner += line(st, 2.2, CAT_EDGE, seed=7210 + i, op=.85)
    s.append(shape(bp, CAT, inner, w=5, seed=7202))
    # задняя лапа (бедро) — дуга на боку
    s.append(line([(1004, 1300), (1000, 1258), (1030, 1230), (1074, 1238), (1092, 1270)], 4.4, seed=7220, taper=.35, wmin=.3))
    s.append(shape(ellipse_pts(1096, 1294, 30, 14, 12), CAT, blob(ellipse_pts(1104, 1298, 20, 10, 10), CAT_SH, .6), w=4, seed=7221))
    return "".join(s)


def front_paws():
    """Передние лапы вытянуты вперёд под подбородком (сверху видны пальчики)."""
    s = []
    for k, (px, py) in enumerate(((752, 1290), (836, 1296))):
        pts = [(px + 70, py - 26), (px + 10, py - 24, 1), (px - 22, py - 12), (px - 26, py + 4), (px - 10, py + 12), (px + 70, py + 12)]
        inn = blob([(px - 30, py + 2), (px + 80, py + 2), (px + 80, py + 14), (px - 30, py + 14)], CAT_SH, .6)
        inn += line([(px - 14, py - 14), (px - 8, py + 4)], 2.2, INK, seed=7231 + k * 3, op=.9)
        inn += line([(px, py - 18), (px + 4, py + 6)], 2.2, INK, seed=7232 + k * 3, op=.9)
        s.append(shape(pts, CAT, inn, w=4.4, seed=7230 + k))
    return "".join(s)


def smirk(k):
    """Хитрая ухмылка: правый (от зрителя) уголок рта поднимается, щека-складка."""
    if k < 0.02:
        return ""
    return (line([(846, 1126), (856, 1121 - 4 * k), (864, 1112 - 6 * k)], 3.2 * min(1, k * 1.5), seed=7240, taper=.4, wmin=.3) +
            line([(866, 1104 - 6 * k), (870, 1112 - 6 * k)], 2.2, INK, seed=7241, op=.7 * k))


def squint_brow(k):
    """Хитрый прищур: над глазами косые складки «бровей» (шерсть темнее), только при k>0."""
    if k < 0.02:
        return ""
    o = ""
    for sx, sd in ((-1, 7250), (1, 7251)):
        ex = CX + sx * 44
        o += line([(ex - 30 * sx, 1030 - 6 * k), (ex, 1022 - 2 * k), (ex + 28 * sx, 1032 + 4 * k)], 3.6, INK, seed=sd, op=.85 * k, taper=.5, wmin=.2)
    return o


def draw_loaf(t, look, blink, tilt, tail, flick, sly=0.0, flame_k=1.3):
    st = cat.static_parts()
    if "loaf" not in _ST:
        _ST["loaf"] = loaf_static()
        _ST["paws"] = front_paws()
    br = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 3.0)
    o = [blob(ellipse_pts(940, 1306, 200, 16, 16), "#140a1e", .35, blur(6))]
    tw = f"translate({LOAF_TAIL} 10) rotate({tail:.2f} {TAIL_PIVOT[0]} {TAIL_PIVOT[1]})"
    o.append(f'<g transform="{tw}">{st["tail"]}</g>')
    sy = 1 + 0.02 * br
    o.append(f'<g transform="translate(0 {CBOT}) scale(1 {sy:.4f}) translate(0 {-CBOT})">{_ST["loaf"]}</g>')
    hy = HEAD_D[1] - 4 * br
    hg = st["head"] + cat.ears(flick) + st["face"] + cat.eyes(look, blink) + squint_brow(sly) + smirk(sly) + cat.whiskers(t)
    o.append(f'<g transform="translate({HEAD_D[0]} {hy:.2f}) rotate({tilt:.2f} {NECK[0]} {NECK[1]})">{hg}</g>')
    o.append(_ST["paws"])
    o.append(f'<g transform="{tw}">{cat.flame(t, flame_k)}</g>')
    return "".join(o)


# ───────────────────────── пузырь мыслей с Димой (футболка задом наперёд)
def dima_bust(t, sly):
    people.C.update(people.PAL["dima"])
    C = people.C
    s = []
    # футболка (горчичная), вид спереди 3/4, шея
    shirt = [(-150, 440, 1), (-140, 280), (-96, 214), (-24, 190), (100, 190), (160, 214), (200, 280), (208, 440, 1)]
    inner = blob([(100, 190), (210, 270), (210, 440), (130, 440), (140, 270)], C["TOP_SH"], .9)
    inner += line([(-96, 300), (-80, 400)], 3, C["FOLD"], seed=7301, op=.6)
    inner += line([(150, 300), (136, 400)], 3, C["FOLD"], seed=7302, op=.6)
    inner += line([(-112, 330), (-70, 312)], 3, C["FOLD"], seed=7307, op=.5)
    # спереди — задний ворот: высокий ровный кант и шов посередине (футболка задом наперёд)
    inner += line([(-36, 192), (40, 186), (110, 192)], 9, C["TOP_SH2"], seed=7303, op=.95, taper=.1, wmin=.8)
    inner += line([(36, 196), (34, 420)], 3, C["FOLD"], seed=7304, op=.7, taper=.1, wmin=.6)
    neck = [(-10, 100), (80, 104), (88, 196), (-20, 196)]
    s.append(shape(neck, C["SKIN"], blob([(-20, 150), (88, 150), (88, 196), (-20, 196)], C["SKIN_SH"], .9), w=4.6, seed=7305))
    s.append(shape(shirt, C["TOP"], inner, w=5.2, seed=7306))
    # голова, хохочет над собой (это помнит кот)
    laugh = 0.6 + 0.4 * smooth(T_KOT1 - 0.2, T_KOT1 + 0.1, t)
    expr = dict(lid=.5, look=(0.4, -0.1), mouth="laugh", open=0.6 + 0.3 * abs(math.sin(t * 9)), brows="up", laugh=laugh, blush=.8,
                hair=4 * math.sin(t * 9))
    bob = 5 * math.sin(t * 9)
    s.append(f'<g transform="translate(0 {bob:.2f}) rotate({3 * math.sin(t * 4.5):.2f} 30 120)">{people.dima_head(expr)}</g>')
    # белая бирка торчит из ворота под подбородком, болтается
    wob = 8 * math.sin(t * 7) + 6 * math.sin(t * 11.3)
    tag = T([(-24, 0, 1), (24, 0, 1), (22, -58), (-22, -60)], 40, 190, 1, wob)
    s.append(shape(tag, "#fbfaf6", blob(T([(-24, -14), (24, -14), (24, 0), (-24, 0)], 40, 190, 1, wob), "#d8d6d0", .9) +
                   line(T([(-12, -40), (12, -40)], 40, 190, 1, wob), 2.2, "#b9b6ae", seed=7311) +
                   line(T([(-12, -28), (8, -28)], 40, 190, 1, wob), 2.2, "#b9b6ae", seed=7312), w=3.2, seed=7310))
    return "".join(s)


BUB = (650.0, 520.0, 250.0, 205.0)      # центр и полуоси пузыря (мир)


def bubble(t, sly):
    """Пузырь мыслей: сначала из головы кота выскакивают три кружка, потом раздувается облако с Димой."""
    bx, by, rx, ry = BUB
    s = []
    dots = [(372, 878, 15), (432, 815, 23), (500, 752, 32)]
    for k, (x, y, r) in enumerate(dots):
        kk = back_out(clamp((t - (28.68 + 0.1 * k)) / 0.2), 2.2)
        if kk < 0.02:
            continue
        rr = r * kk * (1 + 0.04 * math.sin(t * 5 + k))
        s.append(shape(ellipse_pts(x, y + 3 * math.sin(t * 3 + k), rr, rr * .9, 14), "#fbf6ea", "", w=4.2, seed=7400 + k))
    kb = back_out(clamp((t - 28.98) / 0.3), 1.8)
    if kb < 0.02:
        return "".join(s)
    sc = kb * (1 + 0.025 * math.sin(t * 3.4)) * (1 + 0.06 * math.exp(-max(0, t - T_KOT1) * 6) * (t > T_KOT1))
    n = 11
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        pts.append((rx * math.cos(a), ry * math.sin(a), 1))
        a2 = 2 * math.pi * (i + .5) / n
        pts.append((rx * 1.16 * math.cos(a2), ry * 1.16 * math.sin(a2)))
    c = lib.clip_of(pts)
    inside = (blob(ellipse_pts(0, 0, rx * 1.2, ry * 1.2, 16), "#fbf6ea") +
              blob(ellipse_pts(40, 60, rx * 1.1, ry * .9, 16), "#efe4cf", .9) +
              f'<g transform="translate(-40 -55) scale(0.78)">{dima_bust(t, sly)}</g>')
    body = (f'<path d="{fill_d(pts)}" fill="#fbf6ea"/><g clip-path="url(#{c})">{inside}</g>'
            f'<path d="{lib.ink_closed(pts, 5.2, seed=7410)}" fill="{INK}"/>')
    s.append(f'<g transform="translate({bx} {by}) scale({sc:.4f})">{body}</g>')
    return "".join(s)


def frame16(t):
    if "bg16" not in _ST:
        _ST["bg16"] = room_back(0) + sofa_back()
        _ST["seat"] = sofa_seat()
        cat.static_parts()
        _ST["loaf"] = loaf_static()
        _ST["paws"] = front_paws()
        lib.static_done()
    lib.dyn_begin()
    e = t - T_KOT1
    sly = smooth(T_KOT1 - 0.1, T_KOT1 + 0.15, t)
    # глаза: сонно полуприкрыты, смотрят вверх на пузырь; на «кот» — прищур и взгляд в камеру
    lk_up = (0.55, -0.85)
    k = smooth(T_KOT1 - 0.15, T_KOT1 + 0.1, t)
    look = (lk_up[0] * (1 - k), lk_up[1] * (1 - k) + 0.1 * k)
    base = 0.32 + 0.06 * math.sin(t * 1.3)
    bl = base
    for tb in (29.62,):
        if abs(t - tb) < .1:
            bl = max(bl, 1 - abs(t - tb) / .1)
    blink = (bl * (1 - k) + 0.52 * k, bl * (1 - k) + 0.6 * k)
    tilt = 4 * math.sin(t * 1.1) - 8 * k
    flick = 0.0
    for c in (29.3, T_KOT1 + 0.05):
        ee = t - c
        if 0 <= ee < 0.5:
            flick += -14 * math.exp(-ee * 9) * math.sin(ee * 34)
    tail = 5 * math.sin(t * 1.6) - 4
    if e > 0:   # хвост довольно бьёт
        tail += 16 * math.exp(-e * 3) * math.sin(e * 15)
    flk = 1.3 + 0.5 * math.exp(-max(e, 0) * 4) * (e > 0) + 0.08 * math.sin(t * 3.1)
    S_, X_, Y_ = 1.5, 330.0, 1208.0
    kitty = draw_loaf(t, look, blink, tilt, tail, flick, sly, flk)
    kitty = f'<g transform="translate({X_ - CX * S_:.2f} {Y_ - CBOT * S_:.2f}) scale({S_})">{kitty}</g>'
    # свет огонька
    fx = X_ + (cat.FLAME_BASE[0] + LOAF_TAIL - CX) * S_
    fy = Y_ + (cat.FLAME_BASE[1] - 30 - CBOT) * S_
    g = lib.rad_grad([(0, "#ffb050", .3 * flk / 1.3), (1, "#ffb050", 0)], fx, fy, 260, 260)
    glow = f'<rect x="{fx - 300:.0f}" y="{fy - 300:.0f}" width="600" height="600" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    world = _ST["bg16"] + _ST["seat"] + glow + kitty + evening_light(t) + bubble(t, sly)
    u = clamp((t - 28.65) / (31.3 - 28.65))
    z = 1.0 + 0.09 * (0.4 * u + 0.6 * ease_io(u)) + 0.03 * math.exp(-max(e, 0) * 6) * math.sin(min(max(e, 0) * 12, math.pi)) * (e > 0)
    ccx, ccy = 560 + 20 * u, 900 - 10 * u
    return svg(f'<rect width="{W}" height="{H}" fill="#2b2a3a"/><g transform="{cam(ccx, ccy, z, 0.5 * math.sin(t * .8))}">{world}</g>')


# ───────────────────────── s17, s18: кот сидит на диване крупно
CAT_S = 2.45
CAT_X = 470.0
CAT_Y = 1300.0


def paw_front(P, ang, sd=0, push=0.0):
    """Ладошка лапы подушечками к зрителю (внутр. координаты кота) в P, ang — наклон; push 0..1 — лапа ближе к камере."""
    sc = 1 + 0.28 * push
    rot = f'transform="translate({P[0]:.2f} {P[1]:.2f}) rotate({ang:.2f}) scale({sc:.4f})"'
    palm = ellipse_pts(0, 0, 30, 31, 18)
    inner = blob(ellipse_pts(10, 8, 26, 28, 12), CAT_SH, .55)
    inner += blob([(-14, 16), (-10, 4), (0, 0), (10, 4), (14, 16), (8, 22), (0, 19), (-8, 22)], PAD)
    for bx, by in [(-21, -8), (-8, -17), (8, -17), (21, -8)]:
        inner += blob(ellipse_pts(bx, by, 6.2, 7, 10, rot=(bx * 2)), PAD)
    return f'<g {rot}>{shape(palm, CAT, inner, w=4.4 / sc, seed=sd + 1)}</g>'


def leg_up(P):
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


def draw_sit(t, look, blink, tilt, tail, flick, raise_, push, nod=0.0, flame_k=1.3, sly=0.0):
    st = cat.static_parts()
    br = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 2.6)
    o = [blob(ellipse_pts(870, 1306, 175, 20, 16), "#140a1e", .35, blur(6))]
    tw = f"rotate({tail:.2f} {TAIL_PIVOT[0]} {TAIL_PIVOT[1]})"
    o.append(f'<g transform="{tw}">{st["tail"]}</g>')
    sy = 1 + 0.012 * br
    o.append(f'<g transform="translate(0 {CBOT}) scale(1 {sy:.4f}) translate(0 {-CBOT})">{st["body"]}</g>')
    rest = np.array(cat.PAW_REST, float)
    up = np.array([712.0, 1118.0])
    if raise_ < 0.02:
        o.append(cat.leg_left(tuple(rest)))
        P = None
    else:
        k = raise_
        mid = np.array([700.0, 1210.0])
        P = (1 - k) ** 2 * rest + 2 * (1 - k) * k * mid + k * k * up
        P = P + np.array([4, 10]) * push
        o.append(leg_up(tuple(P)))
    hy = -(sy - 1) * (CBOT - 1150) + nod
    hg = st["head"] + cat.ears(flick) + st["face"] + cat.eyes(look, blink) + squint_brow(sly) + smirk(sly) + cat.whiskers(t)
    o.append(f'<g transform="translate(0 {hy:.2f}) rotate({tilt:.2f} {NECK[0]} {NECK[1]})">{hg}</g>')
    if P is not None:
        ang = -16 - 10 * (1 - raise_) + 6 * push
        o.append(paw_front(tuple(P + np.array([-4, -22]) * raise_), ang, sd=9300, push=push))
    o.append(f'<g transform="{tw}">{cat.flame(t, flame_k)}</g>')
    return f'<g transform="translate({CAT_X - CX * CAT_S:.2f} {CAT_Y - CBOT * CAT_S:.2f}) scale({CAT_S:.4f})">{"".join(o)}</g>'


def spark(x, y, r, rot, sd, col="#ffe27a"):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.36
        a = math.radians(rot + i * 45 - 90)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, col, "", w=max(1.8, r * 0.1), seed=sd)


def embers(t, fx, fy, t0):
    """Искры от вспыхнувшего огонька: летят вверх, виляют, гаснут."""
    e = t - t0
    if e < 0 or e > 1.3:
        return ""
    o = []
    for j in range(7):
        ee = e - j * 0.04
        if ee <= 0:
            continue
        a = math.radians(-90 + (j - 3) * 16)
        d = 260 * (1 - math.exp(-ee * 3)) + 40 * ee
        x = fx + math.cos(a) * d + 18 * math.sin(ee * 9 + j)
        y = fy + math.sin(a) * d
        r = (26 + 7 * (j % 3)) * (1 - smooth(0.6, 1.2, ee)) * min(1, ee / 0.08)
        if r > 1.5:
            o.append(spark(x, y, r, 40 * ee * (1 if j % 2 else -1), 9600 + j, "#ffd36a" if j % 2 else "#ffb347"))
    return "".join(o)


def backdrop_blur():
    return room_back(0) + sofa_back()


def frame_sit(sid, t):
    if "bg_sit" not in _ST:
        _ST["bg_sit"] = backdrop_blur()
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    # моргания
    bl = 0.0
    for tb in (31.0, 32.55, 33.45):
        if abs(t - tb) < .09:
            bl = max(bl, min(1, 1.7 * (1 - abs(t - tb) / .09)))
    # s17: лапа на «Напиши», два тычка в экран, опускается к концу плана
    raise_ = back_out(clamp((t - (T_NAP - 0.12)) / 0.3), 1.6) * (1 - ease_io(clamp((t - 32.45) / 0.35)))
    push = 0.0
    for tp in (T_NAP + 0.3, T_NAP + 0.62):
        ee = t - tp
        if -0.1 < ee < 0.22:
            push = max(push, math.sin(math.pi * clamp((ee + 0.1) / 0.32)))
    ef = t - T_KOT2
    flame_k = 1.3 + 0.08 * math.sin(t * 3.1)
    if ef > -0.05:
        flame_k += 1.0 * back_out(clamp((ef + 0.05) / 0.18), 2.0) * math.exp(-max(ef - 0.15, 0) * 1.6)
    # s18: глаза влево-вправо на «смотрят», потом подмигивание (левым от зрителя глазом)
    lx = -1.0 * smooth(T_SMOT - 0.06, T_SMOT + 0.06, t) + 2.0 * smooth(T_SMOT + 0.2, T_SMOT + 0.32, t) - 1.0 * smooth(T_SMOT + 0.42, T_SMOT + 0.52, t)
    look = (0.05 * math.sin(t * .9) + lx * 0.95, -0.08 + 0.1 * abs(lx))
    wk = smooth(T_SMOT + 0.48, T_SMOT + 0.6, t)
    blink = (max(bl, wk), max(bl, 0.25 * wk))
    sly = 0.8 * wk
    tilt = 1.5 * math.sin(t * 1.3) - 5 * smooth(T_NAP - .05, T_NAP + .2, t) * (1 - smooth(32.3, 32.7, t))
    tilt += 6 * wk - 3 * lx * smooth(T_SMOT - .1, T_SMOT + .1, t) * (1 - wk)
    flick = 0.0
    for c in (T_NAP, T_KOT2 + 0.05, T_SMOT + 0.5):
        e = t - c
        if 0 <= e < 0.5:
            flick += -15 * math.exp(-e * 9) * math.sin(e * 30)
    tail = 6 * math.sin(t * 2.0) - 2
    if ef > 0:
        tail += 10 * math.exp(-ef * 3) * math.sin(ef * 12)
    nod = 8 * math.sin(math.pi * clamp((t - (T_NAP + .02)) / 0.28)) + 6 * math.sin(math.pi * clamp((t - (T_SMOT + .48)) / 0.3))
    kitty = draw_sit(t, look, blink, tilt, tail, flick, raise_, push, nod, flame_k, sly)
    # мир огонька
    fxw, fyw = cat.flame_world(CAT_X, CAT_Y, CAT_S, tail)
    fx = embers(t, fxw, fyw - 170, T_KOT2 + 0.06)
    gl = ""
    if ef > -0.05:
        kk = clamp((flame_k - 1.3) / 1.0)
        g = lib.rad_grad([(0, "#ffb050", .5 * kk), (1, "#ffb050", 0)], fxw, fyw, 520, 520)
        gl = f'<rect width="{W}" height="{H}" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    if sid == "s17":
        T_A, T_B = 30.9, 33.2
        u = clamp((t - T_A) / (T_B - T_A))
        z = 1 + 0.07 * ease_io(u) + 0.04 * math.exp(-max(ef, 0) * 6) * math.sin(min(max(ef, 0) * 12, math.pi)) * (ef > 0)
        zc = (540, 880)
    else:
        T_A, T_B = 32.8, 34.9
        u = clamp((t - T_A) / (T_B - T_A))
        es = t - T_SMOT
        z = 1.1 + 0.1 * (0.3 * u + 0.7 * ease_io(u)) + 0.03 * math.exp(-max(es - .5, 0) * 6) * math.sin(min(max(es - .5, 0) * 12, math.pi)) * (es > .5)
        zc = (540, 820)
    seat = (f'<g transform="translate(0 {CAT_Y - SEAT_T - 60:.0f})">{sofa_seat_front()}</g>')
    bg = f'<g {blur(7)}><g transform="{cam(560, 760, 1.5, 0)}">{_ST["bg_sit"]}{evening_light(t)}</g></g>'
    par = f'translate({zc[0]} {zc[1]}) scale({1 + (z - 1) * .4:.4f}) translate({-zc[0] - 10 * u} {-zc[1]})'
    fg = f'translate({zc[0]} {zc[1]}) scale({z:.4f}) translate({-zc[0]} {-zc[1]})'
    vg = lib.rad_grad([(0, "#1a1028", 0), (.6, "#1a1028", 0), (1, "#1a1028", .4)], 540, 900, 1180, 1400)
    return svg(f'<rect width="{W}" height="{H}" fill="#3a3550"/><g transform="{par}">{bg}</g>'
               f'<g transform="{fg}">{seat}{gl}{kitty}{fx}</g><rect width="{W}" height="{H}" fill="url(#{vg})"/>')


def sofa_seat_front():
    """Сиденье дивана крупно (резко), на нём сидит кот: верх в перспективе, передняя грань, шов."""
    s = []
    top = [(-80, SEAT_T, 1), (1160, SEAT_T, 1), (1180, SEAT_T + 120, 1), (-100, SEAT_T + 120, 1)]
    s.append(shape(top, SOFA_HI, blob([(-100, SEAT_T + 60), (1180, SEAT_T + 60), (1180, SEAT_T + 120), (-100, SEAT_T + 120)], SOFA, .6) +
                   line([(-80, SEAT_T + 30), (1160, SEAT_T + 34)], 2.4, SOFA, seed=7551, op=.6), w=5, seed=7550))
    front = [(-100, SEAT_T + 120, 1), (1180, SEAT_T + 120, 1), (1180, 2400, 1), (-100, 2400, 1)]
    s.append(shape(front, SOFA, blob([(-100, SEAT_T + 120), (1180, SEAT_T + 120), (1180, SEAT_T + 160), (-100, SEAT_T + 160)], SOFA_SH, .9) +
                   line([(-100, SEAT_T + 300), (1180, SEAT_T + 296)], 3, SOFA_DK, seed=7561, op=.5), w=5, seed=7560))
    return "".join(s)


def frame(sid, t):
    if sid == "s16":
        return frame16(t)
    return frame_sit(sid, t)
