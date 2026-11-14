"""Мир рилса 44 (копия с правками из scene_cat42 рилса 42): вечерняя комната Димы (den.py), фиолетовый диван, кот сидя
(как look/hero.png: ЛЕВОЕ от зрителя ухо загнуто), искры огонька. Функции возвращают SVG в мировых координатах 1080×1920."""
import math

import numpy as np

import cat
import den
import lib
from cat import CAT, CAT_SH, CAT_FUR, CAT_EDGE, CX, CBOT, NECK, TAIL_PIVOT  # noqa: F401
from ink import ellipse_pts, fill_d, fur  # noqa: F401
from lib import INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, line, rect_pts, shape, smooth, svg, T  # noqa: F401

PAD = "#e8823a"
_ST = {}

# ───────────────────────── диван (мир 1080×1920)
SOFA, SOFA_SH, SOFA_HI, SOFA_DK = "#7d6a9a", "#5e4d7a", "#9786b2", "#3f3256"
SEAT_T, SEAT_F, SOFA_B = 1150.0, 1222.0, 1460.0


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



