"""Сцена cat рилса 43 (s17, 30.3–32.8, клип 30.1–33.0): днём комната Димы (спальня рилса 41, scene_bed: стена, окно с
солнцем, кровать), Димы нет — кровать застелена. Кот (как look/hero.png: ЛЕВОЕ от зрителя ухо загнуто, зелёные глаза,
по две оранжевые полоски на щеках, огонёк на кончике закрученного хвоста) спит клубком на подушке в солнечном луче.
На «встаёт» (31.24) лениво поднимает голову, потягивается (лапы вперёд, тело вытягивается) и зевает; на «захочет»
(31.96) пружинит и спрыгивает с кровати (пух-облачко), приземляется на пол перед кроватью и уходит вправо шагом,
хвост с огоньком задран. Клубок — catcurl (тело отражено, голова не отражена — ухо остаётся слева), шаг — кот рилса 32
(cat_side, вид сбоку вправо). Всё — функция общего времени ролика t."""
import math

import numpy as np

import cat
import cat_side as C
import catcurl
import lib
import scene_bed as B
from ink import ellipse_pts
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, line, rect_pts, shape, smooth, svg)

_ST = {}
T_VST = 31.24          # «встаёт»
T_ZAH = 31.96          # «захочет»
T_LAND = 32.30
CURL = (370.0, 994.0, 0.68)      # низ клубка (870, 1300) → (x, y), масштаб — на подушке
CS = 0.68                        # кот сбоку: тот же масштаб
GY = 1500.0                      # пол перед кроватью (мир)
GX = 0.0                         # мир x = GX + внутр. x * CS
X_LAND = 660.0                   # центр тела при приземлении (мир)
V_WALK = 330.0                   # мир/с
STRIDE = 236.0                   # внутр. ед. за цикл
TC = STRIDE * CS / V_WALK
DUTY = 0.58
LEGS = {"hn": (0.00, "h"), "fn": (0.25, "f"), "hf": (0.50, "h"), "ff": (0.75, "f")}


# ───────────────────────── кровать днём без Димы
def quilt():
    x0, x1 = 560, B.BED_X1 + 30
    y0 = B.MAT - 18
    top = [(x0, y0 + 10), (x0 + 200, y0 - 4), (x0 + 420, y0 + 2), (x0 + 640, y0 - 6), (x1, y0 + 4)]
    pts = [(top[0][0], top[0][1], 1)] + top[1:-1] + [(top[-1][0], top[-1][1], 1), (x1, B.MAT + 132, 1), (x0 - 10, B.MAT + 140, 1)]
    inner = blob([(x0 - 20, B.MAT + 70), (x1 + 40, B.MAT + 60), (x1 + 40, B.MAT + 150), (x0 - 20, B.MAT + 150)], B.QUILT_SH, .9)
    for k in range(9):
        x = x0 + 60 + k * 100
        inner += line([(x, y0), (x + 24, B.MAT + 140)], 2.6, B.QUILT_ST, seed=7500 + k, op=.8, taper=.1, wmin=.8)
    o = [shape(pts, B.QUILT, inner, w=5, seed=7510)]
    cuff = [(x0 - 4, y0 + 8, 1), (x0 + 120, y0 + 2, 1), (x0 + 128, y0 + 40, 1), (x0 - 8, y0 + 46, 1)]
    o.append(shape(cuff, "#f8f5ee", blob([(x0, y0 + 30), (x0 + 130, y0 + 26), (x0 + 130, y0 + 46), (x0, y0 + 48)], "#dcd6ca", .9), w=4, seed=7530))
    return "".join(o)


def rug():
    pts = ellipse_pts(860, GY + 34, 420, 70, 30)
    inner = blob(ellipse_pts(860, GY + 34, 340, 50, 24), "#d77a5c", .9) + blob(ellipse_pts(860, GY + 34, 250, 34, 20), "#e8a46a", .9)
    return shape(pts, "#b85a44", inner, w=4.4, seed=7600)


# ───────────────────────── клубок (тело отражено, голова нет)
def curled(t, lift=0.0, stretch=0.0, yawn=0.0, blink=1.0, squash=0.0, flick=0.0, look=(0.0, 0.0), smolder=0.4):
    st = catcurl.static()
    br = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 3.2)
    BX, BY = catcurl.BX, catcurl.BY
    body = []
    sx = 1 + 0.008 * br + 0.10 * stretch + 0.08 * squash
    sy = 1 + 0.02 * br - 0.06 * stretch - 0.12 * squash
    # в отражённой системе голова слева (x<870): тело тянется от хвоста (справа после отражения → слева) к голове
    body.append(f'<g transform="translate(1040 {BY}) scale({sx:.4f} {sy:.4f}) translate(-1040 {-BY})">{st["body"]}</g>')
    body.append(f'<g transform="translate({-60 * stretch:.1f} {-6 * stretch:.1f})">{st["paws"]}</g>')
    body.append(f'<g transform="translate(1040 {BY}) scale(1 {1 - 0.1 * squash:.4f}) translate(-1040 {-BY})">{st["tail"]}</g>')
    tx, ty = st["tip"]
    body.append(catcurl.flame(t, tx + 4, ty + 2 - 30 * squash, 1.0 + 0.2 * stretch, smolder))
    mir = f'<g transform="translate({2 * BX} 0) scale(-1 1)">{"".join(body)}</g>'
    # голова: в отражённом месте, сама не отражена
    hx, hy = catcurl.HEAD_D
    hy -= 26 * lift + 4 * br + 34 * stretch - 24 * squash
    dx = 2 * BX - 2 * 836 - hx + 40 * stretch
    hg = st["head"] + cat.ears(flick) + st["face"] + cat.eyes(look, blink) + yawn_mouth(yawn) + cat.whiskers(t)
    head = f'<g transform="translate({dx:.2f} {hy:.2f}) rotate({8 - 14 * stretch:.2f} 836 1146)">{hg}</g>'
    sh = blob(ellipse_pts(880, 1302, 230, 20, 16), "#1a0e05", .25, lib.blur(8))
    x, y, s = CURL
    return f'<g transform="translate({x - BX * s:.2f} {y - BY * s:.2f}) scale({s:.4f})">{sh}{mir}{head}</g>'


def yawn_mouth(k):
    if k < 0.02:
        return ""
    rx, ry = 6 + 12 * k, 4 + 22 * k
    cx, cy = 836, 1124 + ry * .55
    m = ellipse_pts(cx, cy, rx, ry, 16)
    inner = blob(ellipse_pts(cx, cy + ry * .5, rx * .7, ry * .4, 12), "#e48a92")
    inner += blob([(cx - rx * .6, cy - ry * .9), (cx - rx * .35, cy - ry * .35), (cx - rx * .15, cy - ry * .9)], "#f4f2ea")
    inner += blob([(cx + rx * .6, cy - ry * .9), (cx + rx * .35, cy - ry * .35), (cx + rx * .15, cy - ry * .9)], "#f4f2ea")
    return shape(m, "#5a2430", inner, w=3.2, seed=7700)


# ───────────────────────── кот сбоку (вправо)
def body_at(Cc, th, L=150.0, puff=0.0, p=0.0):
    d = np.array([math.cos(th), -math.sin(th)])
    nd = np.array([math.sin(th), math.cos(th)])
    Cc = np.array(Cc, float)
    Hh = Cc - d * L / 2
    S = Cc + d * L / 2
    return dict(p=p, C=Cc, H=Hh, S=S, d=d, nd=nd, th=th, L=L, Jh=Hh + nd * 40 + d * 6, Jf=S + nd * 46 - d * 4, puff=puff)


def tail_pts(b, sway, up_k=1.0):
    """Хвост задран (как у кота рилса 32), завиток на конце."""
    Hh, d, nd = b["H"], b["d"], b["nd"]
    up = -nd
    base = Hh - d * 30 + up * 22
    ang = math.radians(32 + 4 * sway) * up_k
    pts = [base]
    for k, (s_, a_) in enumerate([(50, 0.0), (52, 0.42), (50, 0.85), (44, 1.25)]):
        a2 = ang + a_ + 0.05 * sway * k
        pts.append(pts[-1] + (-d * math.cos(a2) + up * math.sin(a2)) * s_)
    c0 = pts[-1]
    last = pts[-1] - pts[-2]
    a0 = math.atan2(last[1], last[0])
    r = 34.0
    cen = c0 + np.array([math.cos(a0 + math.pi / 2), math.sin(a0 + math.pi / 2)]) * r
    for k in range(1, 7):
        a = a0 - math.pi / 2 + k * 0.62
        pts.append(cen + np.array([math.cos(a), math.sin(a)]) * r * (1 - k * 0.06))
    return [(float(q[0]), float(q[1])) for q in pts]


def tail_svg(tp):
    S = np.array(tp)
    pts = lib.band(tp, 50, 24, step=3, cap=True)
    inner = blob(lib.band(tp[:5], 22, 12, step=5), C.CAT_SH, .7)
    inner += line(tp[1:8], 2.4, C.CAT_EDGE, seed=637, op=.7)
    return shape(pts, C.CAT, inner, w=4.8, seed=636), S[-1], S[-1] - S[-2]


def side_svg(b, paws, sway, t, look, blink, hrot_add=0.0):
    o = []
    for k in ("hf", "ff"):
        A, rot = paws[k]
        J = b["Jh"] if k[0] == "h" else b["Jf"]
        o.append(C.leg_svg(J, np.array(A, float), rot, k[0], True, 700 + (0 if k[0] == "h" else 20)))
    to, tip, tdir = tail_svg(tail_pts(b, sway))
    o.append(to)
    o.append(_body(b))
    A, rot = paws["hn"]
    o.append(C.leg_svg(b["Jh"], np.array(A, float), rot, "h", False, 740))
    o.append(C.haunch(b))
    A, rot = paws["fn"]
    o.append(C.leg_svg(b["Jf"], np.array(A, float), rot, "f", False, 760))
    hc = b["S"] + b["d"] * 64 + (-b["nd"]) * 124
    hc = hc + np.array([0, 3 * math.sin(2 * math.pi * b["p"] * 2 - 1.0)])
    hrot = -6 - math.degrees(b["th"]) * 0.4 + 1.5 * math.sin(2 * math.pi * b["p"] * 2) + hrot_add
    o.append(f'<g transform="translate({hc[0]:.2f} {hc[1]:.2f}) rotate({hrot:.2f})">{C.head(look, blink, t)}</g>')
    fk = 1.15 + 0.08 * math.sin(t * 11)
    g = lib.rad_grad([(0, "#ffe9a0", .6), (.4, "#ffb347", .25), (1, "#ff9a3a", 0)], tip[0], tip[1] - 40, 120)
    o.append(f'<circle cx="{tip[0]:.1f}" cy="{tip[1] - 40:.1f}" r="120" fill="url(#{g})"/>')
    o.append(C.flame(tuple(tip), tdir, t, fk))
    return "".join(o)


def _body(b):
    Hh, S, d, nd = b["H"], b["S"], b["d"], b["nd"]
    up = -nd
    mid = (Hh + S) / 2 + up * 6
    pts = [Hh - d * 70 + nd * 10, Hh - d * 62 + up * 44, Hh - d * 20 + up * 70, mid + up * 76, S + up * 70 + d * 10,
           S + up * 56 + d * 60, S + d * 88 + nd * 12, S + d * 58 + nd * 62, S + nd * 70 - d * 10, mid + nd * 66,
           Hh + nd * 64 + d * 10, Hh + nd * 50 - d * 52]
    inner = blob([tuple(Hh + nd * 70 - d * 80), tuple(S + nd * 80 + d * 90), tuple(S + nd * 20 + d * 90), tuple(mid + nd * 18),
                  tuple(Hh + nd * 10 - d * 80)], C.CAT_SH, .85)
    inner += blob([tuple(S + up * 70 - d * 30), tuple(S + up * 80 + d * 30), tuple(S + up * 40 + d * 40), tuple(mid + up * 52)], C.CAT_FUR, .55)
    inner += blob([tuple(S + d * 60 + up * 30), tuple(S + d * 92 + nd * 10), tuple(S + d * 56 + nd * 56), tuple(S + d * 34 + nd * 10)], C.CAT_FUR, .5)
    for i, (u, v) in enumerate([(-.2, .5), (.15, .55), (.45, .4), (.0, -.2), (.6, -.1)]):
        q = mid + d * b["L"] * u * .7 + up * 40 * v
        inner += line([tuple(q), tuple(q + d * -10 + nd * 12)], 2.2, C.CAT_EDGE, seed=624 + i, op=.8)
    return shape(pts, C.CAT, inner, w=5, seed=620)


# шаг (как cat_walk рилса 32): лапа на опоре стоит в мире
def wx(t):
    return (X_LAND - GX) / CS + V_WALK / CS * (t - T_LAND)


def ph(t):
    return (t - T_LAND) / TC + 0.12


def walk_body(t):
    p = ph(t) % 1.0
    y = -150 - 3.5 * math.cos(4 * math.pi * (p - 0.1))
    return body_at((wx(t), y), math.radians(5.0), p=p)


def _t_of(phase):
    return T_LAND + (phase - 0.12) * TC


def walk_paw(leg, t):
    a, kind = LEGS[leg]
    P = ph(t)
    c = math.floor(P - a)

    def stance(ci):
        t0 = _t_of(ci + a)
        t1 = _t_of(ci + a + DUTY)
        b = walk_body((t0 + t1) / 2)
        J = b["Jh"] if kind == "h" else b["Jf"]
        return t0, t1, J[0] + (6 if kind == "f" else -2)

    t0, t1, x = stance(c)
    if t <= t1:
        return (x, -C.ANK), 0.0
    n0, n1, nx = stance(c + 1)
    u = clamp((t - t1) / (n0 - t1))
    ux = (1 - math.cos(math.pi * u)) / 2
    xx = x + (nx - x) * ux
    lift = 34 if kind == "f" else 24
    yy = -C.ANK - lift * math.sin(math.pi * u) ** 1.1
    if kind == "h":
        xx -= 14 * math.sin(math.pi * clamp(u * 1.6))
        rot = -0.18 * math.sin(math.pi * clamp(u * 1.2))
    else:
        rot = 0.32 * math.sin(math.pi * clamp(u * 1.2))
    return (xx, yy), rot


def leap_state(t):
    """Прыжок с подушки на пол: тело по дуге, передние лапы вперёд-вниз, задние вытянуты назад."""
    u = clamp((t - T_ZAH) / (T_LAND - T_ZAH))
    x0, y0 = (CURL[0] + 30 - GX) / CS, (CURL[1] - 70 - GY) / CS
    x1, y1 = (X_LAND - GX) / CS, -150.0
    x = x0 + (x1 - x0) * u
    y = y0 + (y1 - y0) * u ** 1.6 - 160 * math.sin(math.pi * u) * (1 - u * .4)
    th = math.radians(14 - 40 * u)
    b = body_at((x, y), th, L=150 + 22 * math.sin(math.pi * u))
    d, nd = b["d"], b["nd"]
    reach = math.sin(math.pi * clamp(u * 1.1))
    paws = {"fn": (tuple(b["Jf"] + d * (40 + 60 * reach) + nd * 96), 0.3),
            "ff": (tuple(b["Jf"] + d * (26 + 50 * reach) + nd * 100), 0.3),
            "hn": (tuple(b["Jh"] - d * (30 + 70 * reach) + nd * 100), -0.4),
            "hf": (tuple(b["Jh"] - d * (20 + 60 * reach) + nd * 104), -0.4)}
    return b, paws


def poof(t):
    e = t - (T_ZAH - .02)
    if e < 0 or e > .38:
        return ""
    s = []
    x, y, _ = CURL
    for k, (dx, dy, r) in enumerate([(-60, -40, 46), (10, -70, 56), (80, -36, 44), (-20, 0, 50), (60, 10, 40), (120, -60, 30)]):
        kk = back_out(clamp(e / .12), 2.0) * (1 - ease_in(clamp((e - .2) / .18), 2))
        if kk < .03:
            continue
        rr = r * kk
        s.append(shape(ellipse_pts(x + dx * (1 + e * 1.5), y - 50 + dy * (1 + e), rr, rr * .9, 16), "#fbf8f0",
                       blob(ellipse_pts(x + dx * (1 + e * 1.5) + rr * .25, y - 50 + dy * (1 + e) + rr * .3, rr * .7, rr * .5, 12), "#e6e0d2"),
                       w=3.6, seed=7800 + k))
    return "".join(s)


def speed_lines(b, t):
    e = t - T_ZAH
    if e < 0 or t > T_LAND + .05:
        return ""
    s = []
    C0 = b["C"]
    for k in range(3):
        a = C0 + np.array([-150 - 30 * k, -40 + 40 * k])
        q = a + np.array([-110, -60 + 10 * k])
        s.append(line([tuple(a), tuple(q)], 6, "#7d7f92", taper=.6, seed=7900 + k))
    return "".join(s)


def side_cat(t):
    look = (0.6, -0.2)
    blink = 0.0
    if t < T_LAND:
        b, paws = leap_state(t)
        sway = 0.0
        sq = 1.0
        hra = -6
    else:
        b = walk_body(t)
        paws = {k: walk_paw(k, t) for k in LEGS}
        sway = math.sin(2 * math.pi * b["p"] * 2 - 0.6)
        e = t - T_LAND
        land = math.exp(-e * 10) * math.sin(min(e * 18, math.pi)) if e < .35 else 0.0
        b = body_at(b["C"] + np.array([0, 18 * land]), b["th"], p=b["p"])
        hra = 0.0
        sq = 1.0
        if abs(t - 32.72) < .06:
            blink = min(1.0, 1.6 * (1 - abs(t - 32.72) / .06))
    art = side_svg(b, paws, sway, t, look, blink, hra)
    art += speed_lines(b, t)
    _ = sq
    sh = ""
    if t >= T_LAND - .1:
        cx = GX + b["C"][0] * CS
        sh = blob(ellipse_pts(cx, GY + 4, 110, 14, 14), "#3a2412", .3, lib.blur(5))
    return sh + f'<g transform="translate({GX} {GY}) scale({CS})">{art}</g>'


# ───────────────────────── кадр
def scene(t):
    o = [_ST["room"], B.window("day", t), _ST["bed"], quilt(), B.pillow(dent=.6), rug()]
    o.append(B.sunbeams(t))
    stretch = smooth(T_VST - .02, T_VST + .38, t) * (1 - smooth(31.72, 31.86, t))
    yawn = smooth(T_VST + .1, T_VST + .3, t) * (1 - smooth(31.6, 31.78, t))
    lift = smooth(T_VST - .1, T_VST + .25, t)
    squash = smooth(31.80, 31.93, t)
    if t < T_VST - .05:
        blink = 1.0
    elif yawn > .3:
        blink = 1.0
    else:
        blink = 1 - 0.65 * smooth(31.62, 31.75, t)
    flick = -14 * math.exp(-(t - 30.75) * 8) * math.sin((t - 30.75) * 34) if 30.75 <= t < 31.2 else 0.0
    smold = 0.6 * (1 - smooth(T_VST, T_VST + .4, t))
    if t < T_ZAH:
        o.append(curled(t, lift=lift, stretch=stretch, yawn=yawn, blink=blink, squash=squash, flick=flick, look=(0.3, -0.1), smolder=smold))
    else:
        o.append(side_cat(t))
    o.append(poof(t))
    return "".join(o)


def camera(t):
    u = clamp((t - 30.1) / 1.8)
    cx, cy, s = 400 + 20 * u, 960 - 10 * u, 2.05 + 0.15 * ease_io(u)
    k = ease_io(clamp((t - (T_ZAH - .1)) / .5))
    cx += (700 - cx) * k
    cy += (1330 - cy) * k
    s += (1.55 - s) * k
    if t > T_LAND:
        cx += 160 * (t - T_LAND)
    e = t - T_LAND
    if e > 0:
        cy += 8 * math.exp(-e * 7) * math.sin(e * 40)
    e2 = t - T_VST
    if e2 > 0:
        s *= 1 + 0.03 * math.exp(-e2 * 5) * math.sin(min(e2 * 10, math.pi))
    return cx, cy, s, 0.5 * math.sin(t * 1.1)


def build_static():
    if _ST:
        return
    _ST["room"] = B.wall("day") + B.frame_art()
    _ST["bed"] = B.bed_back()
    catcurl.static()
    cat.static_parts()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    cx, cy, s, r = camera(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#d8e2c6"/><g transform="{cam(cx, cy, s, r)}">{scene(t)}</g>')


_ = (INK, H, back_out, blur, rect_pts, ease_out)
