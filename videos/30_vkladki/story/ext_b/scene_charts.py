"""Рилс 30 (агент B), сцены-схемы на кремовом листе (фон — как графики рилса 28, chart_bg).
s06 «так много дел дают так мало результата» (10.85–12.3; клип 10.65–12.5): весы. На левой чаше гора дел, сверху
     падают ещё три дела; весы дрожат, держатся; на «мало» (11.12) левая чаша тяжело падает на пол, гора подпрыгивает,
     пыль; правая чаша взлетает с крошечной зелёной галочкой, на «результата» (11.36) галочка робко блеснёт — и всё.
s11 «на каждом переключении терялось время» (20.85–23.36; клип 20.65–23.56): секундомер, стрелка бежит. На
     «переключении» (21.32) щелчок кнопки, наезд-удар, серый сектор циферблата трескается и отваливается; на
     «терялось» (22.08) и «время» (22.56) — ещё два сектора, они рассыпаются на осколки и крошки.
s13 «до сорока процентов рабочего дня» (25.56–27.75; клип 25.36–27.95): полоска рабочего дня из 10 клеток, над
     левым краем солнце, над правым луна; клетки загораются; на «сорока процентов» (25.76–26.64) 4 клетки краснеют,
     над ними выскакивает «40 %»; потом красная часть трескается и крошится вниз, на её месте пунктир.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import icons
import lib
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}


def chart_bg():
    s = []
    lib.lin_grad([(0, "#f6eedb", 1), (1, "#ead9b8", 1)], 0, 0, 0, 1, gid="gChart")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#gChart)"/>')
    for k in range(-6, 34):
        y = -400 + k * 80
        s.append(f'<rect x="-900" y="{y}" width="{W + 1800}" height="2" fill="#dccbaa"/>')
    return "".join(s)


def soft_shadow(x, y, rx, ry, op=.35):
    return blob(ellipse_pts(x, y, rx, ry, 16), "#8f7650", op, blur(7))


def burst(x, y, e, dur, n, r0, r1, L, col, w, sd, a0=0.2):
    if e < 0 or e > dur:
        return ""
    u = e / dur
    s = []
    for k in range(n):
        a = a0 + k * 2 * math.pi / n
        r = r0 + (r1 - r0) * ease_out(u)
        ll = L * (1 - u)
        s.append(line([(x + math.cos(a) * r, y + math.sin(a) * r), (x + math.cos(a) * (r + ll), y + math.sin(a) * (r + ll))], w, col,
                      taper=.5, seed=sd + k))
    return "".join(s)


# ═══════════════════════════════ s06: весы ═══════════════════════════════
MALO = 11.12
RES = 11.36
PIV = (540.0, 380.0)
LB = 318.0          # половина коромысла
HANG = 540.0        # от конца коромысла до дна чаши
GROUND = 1062.0
PAN_W = 150.0       # полуширина чаши
TILT_MAX = math.degrees(math.asin((GROUND - HANG - PIV[1]) / LB))   # чаша ложится ровно на пол


def beam_angle(t):
    """Угол коромысла (отрицательный — левый конец вниз)."""
    e = t - MALO
    tremble = 0.9 * math.sin(t * 38) * smooth(10.6, 10.8, t)
    pre = -2.0 + tremble
    # каждое падающее дело толкает
    for tl in DROP_T:
        d = t - tl
        if d > 0:
            pre += -2.6 * math.exp(-d * 9) * math.cos(d * 30)
    if e < -0.02:
        return pre
    u = e + 0.02
    fall = TILT_MAX * ease_in(clamp(u / 0.16), 2.2)
    bounce = 0.0
    if u > 0.16:
        b = u - 0.16
        bounce = -3.6 * math.exp(-b * 7) * abs(math.sin(b * 16))
    return -(min(fall, TILT_MAX) + bounce) + pre * (1 - clamp(u / 0.1))


def beam_ends(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    L = (PIV[0] - LB * c, PIV[1] - LB * s)
    R = (PIV[0] + LB * c, PIV[1] + LB * s)
    return L, R


def pan(cx, by, sd, swing=0.0):
    """Чаша: дно в by, центр по x; цепочки к точке подвеса (cx, by - HANG)."""
    top = by - 46
    s = []
    hx, hy = cx + swing, by - HANG
    for k, dx in enumerate((-PAN_W + 10, PAN_W - 10)):
        pts = [(hx, hy), (cx + dx * .5 + swing * .5, (hy + top) / 2), (cx + dx, top)]
        s.append(line(pts, 4.6, "#6b5a46", taper=.05, wmin=.9, seed=sd + k))
        # звенья — точки
        for j in range(1, 9):
            u = j / 9
            px, py = hx + (cx + dx - hx) * u, hy + (top - hy) * u
            s.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="4.2" fill="#c9a24a" stroke="{INK}" stroke-width="2"/>')
    s.append(shape(ellipse_pts(hx, hy, 14, 14, 12), "#d9b35a", "", w=3.4, seed=sd + 3))
    return "".join(s)


def pan_bowl(cx, by, sd):
    top = by - 46
    pts = [(cx - PAN_W - 8, top, 1), (cx + PAN_W + 8, top, 1), (cx + PAN_W - 30, by - 6), (cx + PAN_W - 70, by, 1), (cx - PAN_W + 70, by, 1),
           (cx - PAN_W + 30, by - 6)]
    inner = blob([(cx + 30, top), (cx + PAN_W + 8, top), (cx + PAN_W - 30, by - 6), (cx + PAN_W - 70, by), (cx + 10, by)], "#b8892c", .9)
    inner += line([(cx - PAN_W + 10, top + 12), (cx - 40, top + 14)], 4, "#ffe08a", seed=sd + 5)
    s = shape(pts, "#e2b546", inner, w=5, seed=sd + 4)
    s += shape([(cx - PAN_W - 14, top - 10, 1), (cx + PAN_W + 14, top - 10, 1), (cx + PAN_W + 14, top + 4, 1), (cx - PAN_W - 14, top + 4, 1)], "#f0c85a",
               blob([(cx + 40, top - 10), (cx + PAN_W + 14, top - 10), (cx + PAN_W + 14, top + 4), (cx + 40, top + 4)], "#c99a34", .9), w=4.2, seed=sd + 6)
    return s


def stand():
    s = []
    s.append(soft_shadow(540, GROUND + 8, 160, 18))
    # основание
    s.append(shape([(430, GROUND, 1), (650, GROUND, 1), (626, GROUND - 46, 1), (454, GROUND - 46, 1)], "#8a5a36",
                   blob([(560, GROUND - 46), (626, GROUND - 46), (650, GROUND), (560, GROUND)], "#6e4528", .9) +
                   line([(462, GROUND - 36), (540, GROUND - 38)], 3.4, "#b07a48", seed=1503), w=5, seed=1501))
    s.append(shape([(500, GROUND - 46, 1), (580, GROUND - 46, 1), (566, GROUND - 74, 1), (514, GROUND - 74, 1)], "#a06a3e", "", w=4.4, seed=1502))
    # стойка
    s.append(shape([(522, GROUND - 74, 1), (558, GROUND - 74, 1), (552, PIV[1] + 20, 1), (528, PIV[1] + 20, 1)], "#d9b35a",
                   blob([(540, GROUND - 74), (558, GROUND - 74), (552, PIV[1] + 20), (540, PIV[1] + 20)], "#b38a34", .9), w=4.6, seed=1504))
    return "".join(s)


def beam(a):
    w2 = LB + 26
    pts = [(-w2, -14, 1), (w2, -14, 1), (w2, 14, 1), (-w2, 14, 1)]
    inner = blob([(-w2, 2), (w2, 2), (w2, 14), (-w2, 14)], "#b38a34", .9) + line([(-w2 + 20, -6), (w2 - 60, -6)], 3.4, "#ffe08a", seed=1511)
    s = shape(pts, "#d9b35a", inner, w=4.8, seed=1510)
    for k, x in enumerate((-w2, w2)):
        s += shape(ellipse_pts(x, 0, 20, 20, 14), "#e8c463", "", w=4, seed=1512 + k)
    s += shape(ellipse_pts(0, 0, 34, 34, 16), "#e8c463", blob(ellipse_pts(6, 8, 26, 24, 12), "#c99a34", .8), w=4.6, seed=1515)
    s += shape(ellipse_pts(0, 0, 9, 9, 10), "#6b5a46", "", w=2.6, seed=1516)
    return f'<g transform="translate({f(PIV[0])} {f(PIV[1])}) rotate({f(a)})">{s}</g>'


def finial():
    x, y = PIV
    return shape([(x, y - 96), (x + 24, y - 60), (x + 14, y - 30, 1), (x - 14, y - 30, 1), (x - 24, y - 60)], "#e8c463",
                 blob([(x + 4, y - 90), (x + 24, y - 60), (x + 14, y - 30), (x + 4, y - 30)], "#c99a34", .9), w=4.4, seed=1520)


def sheet_paper(sd, col="#fbfaf4"):
    s = shape(rect_pts(-56, -40, 56, 40, 4), col, blob(rect_pts(-56, 22, 56, 40, 4), "#e3dccb", .9), w=3.4, seed=sd)
    for k in range(3):
        s += line([(-42, -24 + k * 15), (30 - 18 * (k % 2), -24 + k * 15)], 3, "#9aa3b2", taper=.1, wmin=.8, seed=sd + 1 + k)
    return s


def folder(sd):
    s = shape([(-62, -34, 1), (-20, -34, 1), (-10, -44, 1), (30, -44, 1), (36, -34, 1), (62, -34, 1), (62, 40, 1), (-62, 40, 1)], "#7ab4e6",
              blob([(-62, 14), (62, 14), (62, 40), (-62, 40)], "#4f8cc8", .9), w=3.6, seed=sd)
    s += shape(rect_pts(-52, -24, 52, 34, 3), "#fbfaf4", "", w=3, seed=sd + 1)
    s += shape([(-62, -12, 1), (62, -12, 1), (62, 40, 1), (-62, 40, 1)], "#8fc4f0", blob([(-62, 18), (62, 18), (62, 40), (-62, 40)], "#62a2dc", .9),
               w=3.6, seed=sd + 2)
    return s


def chat_icon(sd=0):
    s = shape([(-46, -36, 1), (22, -36, 1), (22, 10, 1), (-14, 10, 1), (-30, 26, 1), (-28, 10, 1), (-46, 10, 1)], "#5aa0e6",
              blob([(-46, -6), (22, -6), (22, 10), (-46, 10)], "#3f82c8", .8), w=3.4, seed=sd + 1)
    s += shape([(-6, -14, 1), (46, -14, 1), (46, 28, 1), (34, 28, 1), (38, 42, 1), (20, 28, 1), (-6, 28, 1)], "#fbfaf6",
               blob([(-6, 14), (46, 14), (46, 28), (-6, 28)], "#e3dccb", .8), w=3.4, seed=sd + 2)
    for k in range(3):
        s += f'<circle cx="{8 + k * 13}" cy="7" r="4.6" fill="{INK}"/>'
    return s


def play_icon(sd=0):
    s = shape(rect_pts(-46, -32, 46, 32, 14), "#e8453c", blob(rect_pts(-46, 8, 46, 32, 14), "#c13128", .85) +
              blob(rect_pts(-38, -26, 10, -16, 5), "#ff8a80", .8), w=3.6, seed=sd + 1)
    s += shape([(-12, -17, 1), (20, 0, 1), (-12, 17, 1)], "#ffffff", "", w=2.8, seed=sd + 2)
    return s


def thing(kind, sd):
    if kind == "paper":
        return sheet_paper(sd)
    if kind == "folder":
        return folder(sd)
    if kind == "chat":
        return chat_icon(sd)
    if kind == "play":
        return play_icon(sd)
    if kind.startswith("note:"):
        _, col, ic = kind.split(":")
        return f'<g transform="scale(.62)">{icons.note(col, ic, sd)}</g>'
    return f'<g transform="scale(1.15)">{icons.ICONS[kind](sd)}</g>'


# гора на левой чаше: (dx, dy от верха чаши, вид, поворот, масштаб) — снизу вверх
PILE = [(-88, -34, "paper", -6, .95), (0, -38, "folder", 3, 1.0), (88, -34, "paper", 8, .9),
        (-62, -98, "note:yellow:envelope", -10, .85), (40, -100, "laptop", 4, 1.0), (-104, -92, "receipt", -14, .8),
        (100, -94, "note:pink:calendar", 12, .78), (-20, -156, "paper", -4, .95), (64, -166, "envelope", 10, .9),
        (-70, -170, "chat", -8, .85), (6, -218, "note:blue:cart", 6, .8), (-44, -248, "report", -12, .9),
        (46, -246, "play", 9, .8), (0, -296, "note:green:phone", -5, .75)]
DROP = [(-30, -342, "envelope", -18, .9, 10.70), (40, -360, "note:orange:receipt", 14, .72, 10.88), (-6, -400, "chat", -6, .85, MALO - 0.04)]
DROP_T = [d[5] for d in DROP]


def pile(cx, top, t, jump):
    s = []
    for i, (dx, dy, kind, rot, sc) in enumerate(PILE):
        hop = jump * (0.4 + 0.6 * (-dy / 350)) * 34
        r = rot + jump * 6 * math.sin(i * 1.7)
        s.append(f'<g transform="translate({f(cx + dx)} {f(top + dy - hop)}) rotate({f(r)}) scale({f(sc)})">{thing(kind, 1600 + i * 30)}</g>')
    for i, (dx, dy, kind, rot, sc, tl) in enumerate(DROP):
        e = t - tl
        if e < -0.34:
            continue
        if e < 0:
            u = 1 + e / 0.34
            y = top + dy - 900 * (1 - ease_in(u, 2))
            r = rot + 70 * (1 - u)
            sq = 1.0
        else:
            y = top + dy - jump * 40
            r = rot + 5 * math.exp(-e * 8) * math.sin(e * 30)
            sq = 1 - 0.12 * math.exp(-e * 14)
        s.append(f'<g transform="translate({f(cx + dx)} {f(y)}) rotate({f(r)}) scale({f(sc)} {f(sc * sq)})">{thing(kind, 1900 + i * 30)}</g>')
        if 0 <= e < 0.25:
            s.append(burst(cx + dx, y + 30, e, 0.25, 6, 50, 90, 26, "#7a5a3a", 6, 1990 + i * 7, a0=-2.6))
    return "".join(s)


def tick_mark(x, y, sc, sd):
    pts = [(-30, -2), (-12, 16), (28, -26), (36, -18), (-12, 32), (-38, 6)]
    s = shape(pts, "#3cbf63", blob([(-12, 22), (32, -20), (36, -18), (-12, 32)], "#2a9a4c", .9), w=3.2, seed=sd)
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{s}</g>'


def dust_puff(x, y, e, sd, life=0.85):
    """Клубы пыли из-под чаши (как хлопок крышки рилса 26): вылетают в стороны, растут и сжимаются к концу."""
    if e < 0 or e > life:
        return ""
    s = []
    rs = np.random.RandomState(sd)
    cl = []
    for k in range(12):
        side = -1 if k % 2 else 1
        x0 = x + side * rs.uniform(40, 150)
        px = x0 + side * rs.uniform(60, 200) * (1 - math.exp(-e * 5))
        py = y - 20 - rs.uniform(10, 110) * (1 - math.exp(-e * 4)) + 10 * e
        lf = rs.uniform(0.5, life)
        r = rs.uniform(30, 58) * math.sin(math.pi * clamp(e / lf)) ** 0.6
        if r < 4:
            continue
        cl.append((px, py, r, mix("#d9cdb4", "#e9dfca", rs.uniform(0, 1)), k))
    for px, py, r, col, k in cl:
        s.append(shape(ellipse_pts(px, py, r, r * .8, 14), col, "", w=2.4, seed=sd + k, var=.15))
    for px, py, r, col, k in cl:
        s.append(blob(ellipse_pts(px - r * .2, py - r * .28, r * .5, r * .3, 10), "#f6f1e6", .95))
    return "".join(s)


def s06(t):
    a = beam_angle(t)
    Lp, Rp = beam_ends(a)
    e = t - MALO
    jump = 0.0
    if e > 0.12:
        b = e - 0.12
        jump = math.exp(-b * 6) * abs(math.sin(b * 11)) * 0.9
    swing_l = 10 * math.exp(-max(e - .14, 0) * 5) * math.sin(max(e - .14, 0) * 14) * (e > .14)
    swing_r = -14 * math.exp(-max(e, 0) * 4) * math.sin(max(e, 0) * 12) * (e > 0) + 3 * math.sin(t * 3)
    lb = min(Lp[1] + HANG, GROUND)          # чаша не проваливается в пол
    rb = Rp[1] + HANG
    s = []
    s.append(stand())
    s.append(soft_shadow(Lp[0], GROUND + 6, 150 + 60 * clamp((lb - 900) / 160), 14, .25 + .2 * clamp((lb - 900) / 160)))
    s.append(soft_shadow(Rp[0], GROUND + 6, 130, 12, .2))
    s.append(pan(Lp[0], lb, 1530, swing_l))
    s.append(pile(Lp[0], lb - 46, t, jump))
    s.append(pan(Rp[0], rb, 1540, swing_r))
    s.append(beam(a))
    s.append(finial())
    s.append(pan_bowl(Lp[0], lb, 1530))
    # правая чаша и маленькая галочка
    er = t - RES
    blink = math.exp(-max(er, 0) * 5) * (er > 0)
    tsc = 0.9 * (1 + 0.22 * blink * math.sin(max(er, 0) * 18 + 1.2))
    s.append(tick_mark(Rp[0] + swing_r * .8, rb - 72 - 6 * blink, tsc, 1560))
    s.append(pan_bowl(Rp[0] + swing_r, rb, 1540))
    if er > 0:
        s.append(burst(Rp[0] + swing_r * .8, rb - 80, er, 0.32, 5, 34, 52, 16, "#3cbf63", 4.5, 1570, a0=-2.8))
    # удар об пол
    if e > 0.12:
        s.append(dust_puff(Lp[0], GROUND, e - 0.12, 1580))
    u = clamp((t - 10.65) / 1.85)
    shake = 9 * math.exp(-max(e - .12, 0) * 7) * math.sin((e - .12) * 50) * (e > .12)
    cm = cam(540 + shake, 830 + 10 * ease_io(u) + shake * .4, 1.08 + 0.08 * ease_io(u) + 0.02 * math.exp(-max(e - .12, 0) * 6) * (e > .12),
             -0.8 + 1.4 * u)
    return "".join(s), cm


# ═══════════════════════════════ s11: секундомер ═══════════════════════════════
SC = (540.0, 760.0)
RF = 330.0               # радиус циферблата
CLK = [21.32, 22.08, 22.56]
# сектора: (угол от 12 часов по часовой, начало и конец, градусы)
WEDGES = [(28.0, 70.0), (108.0, 148.0), (222.0, 264.0)]
R_IN = 70.0


def ang_xy(deg, r):
    a = math.radians(deg - 90)
    return SC[0] + r * math.cos(a), SC[1] + r * math.sin(a)


def watch_case():
    x, y = SC
    s = []
    s.append(soft_shadow(x + 20, y + 380, 300, 26, .3))
    # дужка и кнопка-коронка рисуются отдельно (кнопка двигается)
    s.append(shape(ellipse_pts(x, y, RF + 46, RF + 46, 48), "#c9ccd6",
                   blob(ellipse_pts(x + 30, y + 34, RF + 30, RF + 26, 40), "#9ea3b2", .9) +
                   blob(ellipse_pts(x - 120, y - 200, 120, 46, 20, rot=-35), "#eef0f6", .9), w=6.4, seed=2001))
    s.append(shape(ellipse_pts(x, y, RF + 16, RF + 16, 48), "#7d8394", "", w=4.4, seed=2002))
    return "".join(s)


def face_static():
    x, y = SC
    s = []
    s.append(shape(ellipse_pts(x, y, RF, RF, 48), "#fbf6e8", blob(ellipse_pts(x + 40, y + 50, RF - 10, RF - 30, 30), "#efe6cf", .8), w=4.6, seed=2003))
    return "".join(s)


def ticks():
    s = []
    for k in range(60):
        deg = k * 6
        big = k % 5 == 0
        r0, r1 = (RF - 52, RF - 14) if big else (RF - 30, RF - 14)
        s.append(line([ang_xy(deg, r0), ang_xy(deg, r1)], 8 if big else 4, INK if big else "#6b6470", taper=.05, wmin=.9, seed=2010 + k))
    # малый циферблат (без цифр)
    cx, cy = x0, y0 = SC[0], SC[1] + 120
    s.append(shape(ellipse_pts(cx, cy, 62, 62, 24), "#f1e8d2", "", w=3.6, seed=2080))
    for k in range(12):
        a = math.radians(k * 30 - 90)
        s.append(line([(cx + 46 * math.cos(a), cy + 46 * math.sin(a)), (cx + 56 * math.cos(a), cy + 56 * math.sin(a))], 3.4, INK, taper=.05,
                      wmin=.9, seed=2090 + k))
    return "".join(s)


def wedge_pts(a0, a1, r0, r1, jag_seed=None, n=10):
    """Кольцевой сектор; по желанию — рваные боковые края."""
    rs = np.random.RandomState(jag_seed or 1)
    out = []
    for k in range(n + 1):
        out.append(ang_xy(a0 + (a1 - a0) * k / n, r1))
    m = 5
    for k in range(1, m):
        u = k / m
        r = r1 + (r0 - r1) * u
        j = rs.uniform(-3.5, 3.5) if jag_seed else 0
        out.append(ang_xy(a1 + j, r))
    for k in range(n + 1):
        out.append(ang_xy(a1 + (a0 - a1) * k / n, r0))
    for k in range(1, m):
        u = k / m
        r = r0 + (r1 - r0) * u
        j = rs.uniform(-3.5, 3.5) if jag_seed else 0
        out.append(ang_xy(a0 + j, r))
    return out


def shards(i):
    """Сектор i делится на 3 осколка: по углу пополам и наружная половина ещё по радиусу."""
    a0, a1 = WEDGES[i]
    am = (a0 + a1) / 2 + (4 if i % 2 else -4)
    rm = (R_IN + RF) / 2 + 18
    return [(a0, am, rm, RF), (am, a1, rm, RF), (a0, a1, R_IN, rm)]


def shard_poly(a0, a1, r0, r1, sd):
    rs = np.random.RandomState(sd)
    out = []
    n = max(3, int((a1 - a0) / 6))
    for k in range(n + 1):
        out.append(ang_xy(a0 + (a1 - a0) * k / n, r1) + (((1,) if k in (0, n) else ())))
    for k in range(1, 4):
        r = r1 + (r0 - r1) * k / 4
        out.append(ang_xy(a1 + rs.uniform(-3, 3), r))
    for k in range(n + 1):
        out.append(ang_xy(a1 + (a0 - a1) * k / n + (rs.uniform(-2, 2) if 0 < k < n else 0), r0 + rs.uniform(-4, 4) * (0 < k < n))
                   + (((1,) if k in (0, n) else ())))
    for k in range(1, 4):
        r = r0 + (r1 - r0) * k / 4
        out.append(ang_xy(a0 + rs.uniform(-3, 3), r))
    return out


def crack_lines(i, k):
    a0, a1 = WEDGES[i]
    s = []
    for j, (aa, rr) in enumerate([(a0, 1.0), (a1, 1.0), ((a0 + a1) / 2, .6)]):
        pts = []
        for m in range(6):
            u = m / 5 * k
            r = RF - (RF - R_IN) * u * rr
            pts.append(ang_xy(aa + 3.2 * math.sin(m * 2.1 + j), r))
        if k > 0.05:
            s.append(line(pts, 4.4, INK, taper=.4, wmin=.3, seed=2100 + i * 10 + j))
    return "".join(s)


def hole(i):
    a0, a1 = WEDGES[i]
    pts = shard_poly(a0, a1, R_IN, RF, 2200 + i)
    inner = blob([(px + 10, py + 14) for px, py, *_ in shard_poly(a0, a1, R_IN, RF, 2200 + i)], "#2a2532", .95)
    inner += line([ang_xy(a0 + 4, RF - 14), ang_xy((a0 + a1) / 2, RF - 18), ang_xy(a1 - 4, RF - 14)], 3, "#6a6378", seed=2215 + i)
    return shape(pts, "#433c4e", inner, w=4.6, seed=2210 + i)


def falling_shards(i, t):
    """Осколки сектора i после щелчка: вылет наружу, гравитация, вращение; второй и третий рассыпаются крошками."""
    T = CLK[i]
    e = t - T - 0.05
    if e < 0:
        return ""
    a0, a1 = WEDGES[i]
    mid = math.radians((a0 + a1) / 2 - 90)
    out_dir = (math.cos(mid), math.sin(mid))
    s = []
    col = "#a3a7b3"
    cr = []
    # крошки
    rs = np.random.RandomState(2400 + i)
    for k in range(12 if i > 0 else 7):
        aa = rs.uniform(a0, a1)
        rr = rs.uniform(R_IN, RF)
        x0, y0 = ang_xy(aa, rr)
        vx = out_dir[0] * rs.uniform(400, 800) + rs.uniform(-200, 200)
        vy = out_dir[1] * rs.uniform(400, 800) - rs.uniform(200, 500)
        ee = max(e - 0.04, 0)
        x, y = x0 + vx * ee, y0 + vy * ee + 2600 * ee * ee
        r = rs.uniform(9, 15)
        if ee <= 0.03 or y > H + 200:
            continue
        rot = rs.uniform(0, 360) + 400 * ee
        pts = [(x + r * math.cos(math.radians(rot + q * 120 + rs.uniform(-20, 20))), y + r * math.sin(math.radians(rot + q * 120))) for q in range(3)]
        cr.append(shape([p + (1,) for p in pts], "#9a9eab", "", w=2.0, seed=2420 + i * 20 + k))
    s.append("".join(cr))
    for j, (b0, b1, r0, r1) in enumerate(shards(i)):
        cx, cy = ang_xy((b0 + b1) / 2, (r0 + r1) / 2)
        sep = smooth(0.06, 0.22, e) * (1.0 if i > 0 else smooth(0.18, 0.35, e))
        vx = out_dir[0] * (700 + 120 * j) + (j - 1) * 220 * sep
        vy = out_dir[1] * (700 + 120 * j) - 420
        dx = vx * e
        dy = vy * e + 2400 * e * e
        rot = (200 + 120 * j) * e * (1 if (j + i) % 2 else -1)
        if cy + dy > H + 400:
            continue
        pts = shard_poly(b0, b1, r0, r1, 2300 + i * 10 + j)
        inner = blob([(px + 8, py + 10) for px, py, *_ in pts], "#868a97", .9)
        g = shape(pts, col, inner, w=4.2, seed=2320 + i * 10 + j)
        s.append(f'<g transform="translate({f(dx)} {f(dy)}) rotate({f(rot)} {f(cx)} {f(cy)})">{g}</g>')
    return "".join(s)


def wedge_live(i, t):
    """Сектор до отрыва: за 0.12 с до щелчка трескается, на щелчке сереет (без прозрачности: цвет смешивается)."""
    T = CLK[i]
    e = t - T
    if e > 0.05:
        return ""
    a0, a1 = WEDGES[i]
    g = smooth(-0.06, 0.04, e)
    col = mix("#fbf6e8", "#a3a7b3", g)
    s = ""
    if g > 0.01 or e > -0.14:
        s += shape(shard_poly(a0, a1, R_IN, RF, 2200 + i), col, "", w=4.0, seed=2500 + i, ink=g > 0.3)
        s += crack_lines(i, smooth(-0.14, 0.02, e))
    return s


def stopwatch_hand(t):
    x, y = SC
    deg = (t - 20.65) * 210 + 30
    tip = ang_xy(deg, RF - 26)
    tail = ang_xy(deg + 180, 52)
    s = line([tail, (x, y), tip], 9, "#e2543f", taper=.15, wmin=.5, seed=2600)
    s += shape(ellipse_pts(x, y, 22, 22, 14), "#e2543f", "", w=3.6, seed=2601)
    s += shape(ellipse_pts(x, y, 8, 8, 10), "#fbf6e8", "", w=2.4, seed=2602)
    # малая стрелка
    sd = (t - 20.65) * 40
    cx, cy = SC[0], SC[1] + 120
    a = math.radians(sd - 90)
    s += line([(cx, cy), (cx + 40 * math.cos(a), cy + 40 * math.sin(a))], 5, INK, taper=.2, seed=2603)
    return s


def crown(t):
    """Коронка с кнопкой сверху и дужка; на щелчках кнопка вдавливается."""
    x, y = SC
    press = 0.0
    for c in CLK:
        e = t - c
        if -0.06 < e < 0.25:
            press = max(press, smooth(-0.06, 0.0, e) * (1 - smooth(0.06, 0.25, e)))
    top = y - RF - 46
    s = []
    s.append(shape(rect_pts(x - 26, top - 52, x + 26, top + 8, 6), "#b9bdc9", blob(rect_pts(x + 4, top - 52, x + 26, top + 8, 6), "#8f94a3", .9),
                   w=4.4, seed=2700))
    by = top - 52 - 46 + 22 * press
    s.append(shape(rect_pts(x - 48, by, x + 48, by + 50, 14), "#e2543f", blob(rect_pts(x - 48, by + 30, x + 48, by + 50, 14), "#b93a2a", .9) +
                   line([(x - 34, by + 12), (x + 6, by + 12)], 4, "#ff9c8a", seed=2702), w=4.8, seed=2701))
    # боковые кнопки
    for k, deg in enumerate((-42, 42)):
        p0 = ang_xy(deg, RF + 40)
        p1 = ang_xy(deg, RF + 76)
        s.append(line([p0, p1], 30, "#9ea3b2", taper=.0, wmin=1, seed=2710 + k))
        s.append(line([p0, p1], 6, INK, taper=.0, wmin=1, seed=2720 + k, op=0.0) if False else "")
    return "".join(s), press


def side_buttons():
    s = []
    for k, deg in enumerate((-42, 42)):
        a = deg
        c = ang_xy(a, RF + 58)
        pts = [ang_xy(a - 6, RF + 36), ang_xy(a + 6, RF + 36), ang_xy(a + 5, RF + 80), ang_xy(a - 5, RF + 80)]
        s.append(shape([p + (1,) for p in pts], "#b9bdc9", "", w=4.2, seed=2730 + k))
    return "".join(s)


def s11(t):
    s = []
    s.append(side_buttons())
    cr, press = crown(t)
    s.append(cr)
    s.append(watch_case())
    s.append(face_static())
    # дыры уже отвалившихся секторов — под стрелкой
    for i in range(3):
        if t > CLK[i] + 0.05:
            s.append(hole(i))
    s.append(ticks_masked(t))
    for i in range(3):
        s.append(wedge_live(i, t))
    s.append(stopwatch_hand(t))
    for i, c in enumerate(CLK):
        s.append(burst(SC[0], SC[1] - RF - 140, t - c, 0.3, 7, 70, 120, 30, "#e2543f", 7, 2800 + i * 10, a0=-math.pi))
    for i in range(3):
        s.append(falling_shards(i, t))
    pop = 0.0
    sh = 0.0
    for c in CLK:
        e = t - c
        if e > 0:
            pop += 0.07 * math.exp(-e * 7)
            sh += 7 * math.exp(-e * 9) * math.sin(e * 52)
    u = clamp((t - 20.65) / 2.9)
    cm = cam(540 + sh, 850 + 10 * ease_io(u), 1.1 + 0.08 * ease_io(u) + pop, 0.6 - 1.0 * u + 0.3 * sh / 7)
    return "".join(s), cm


def ticks_masked(t):
    """Деления, кроме тех, что попали в отвалившиеся сектора (и в серый сектор на щелчке)."""
    out = []
    for k in range(60):
        deg = k * 6
        gone = False
        for i, (a0, a1) in enumerate(WEDGES):
            if a0 - 1 <= deg <= a1 + 1 and t > CLK[i] + 0.05:
                gone = True
        if gone:
            continue
        big = k % 5 == 0
        r0, r1 = (RF - 52, RF - 14) if big else (RF - 30, RF - 14)
        out.append(line([ang_xy(deg, r0), ang_xy(deg, r1)], 8 if big else 4, INK if big else "#6b6470", taper=.05, wmin=.9, seed=2010 + k))
    cx, cy = SC[0], SC[1] + 120
    out.append(shape(ellipse_pts(cx, cy, 62, 62, 24), "#f1e8d2", "", w=3.6, seed=2080))
    for k in range(12):
        a = math.radians(k * 30 - 90)
        out.append(line([(cx + 46 * math.cos(a), cy + 46 * math.sin(a)), (cx + 56 * math.cos(a), cy + 56 * math.sin(a))], 3.4, INK, taper=.05,
                        wmin=.9, seed=2090 + k))
    return "".join(out)


# ═══════════════════════════════ s13: полоска рабочего дня ═══════════════════════════════
BX0, BX1, BY, BH = 100.0, 980.0, 820.0, 150.0
NC = 10
RED0, RED1 = 25.76, 26.64        # «сорока процентов»
TXT = 26.16                      # «процентов» — «40 %»
CRUMB = 26.80


def cell(i):
    pad = 10
    cw = (BX1 - BX0 - 2 * pad) / NC
    x0 = BX0 + pad + i * cw
    return x0 + 4, BY - BH / 2 + pad, x0 + cw - 4, BY + BH / 2 - pad


DAYC = ["#ffe58a", "#ffdc72", "#ffd35e", "#ffc94e", "#ffbd48", "#f7ad4c", "#e99c58", "#c98a78", "#a07c98", "#7d73b0"]


def sun(t):
    x, y = 190, 470
    s = []
    for k in range(10):
        a = k * math.pi / 5 + t * 0.9
        s.append(line([(x + math.cos(a) * 92, y + math.sin(a) * 92), (x + math.cos(a) * 128, y + math.sin(a) * 128)], 11, "#ffb52e", taper=.4,
                      seed=3010 + k))
    s.append(shape(ellipse_pts(x, y, 76, 76, 24), "#ffd84a", blob(ellipse_pts(x + 14, y + 16, 66, 60, 18), "#f4b92e", .8) +
                   blob(ellipse_pts(x - 26, y - 26, 20, 12, 10, rot=-30), "#fff6c8", .95), w=5, seed=3000))
    return s and "".join(s)


def moon(t):
    x, y = 880, 470
    rot = 6 * math.sin(t * 2.0)
    pts = []
    for k in range(25):
        a = math.radians(-117 + k * 234 / 24)
        pts.append((74 * math.cos(a), 74 * math.sin(a)) + ((1,) if k in (0, 24) else ()))
    for k in range(1, 24):
        a = math.radians(89.6 - k * 179.2 / 24)
        pts.append((-34 + 66 * math.cos(a), 66 * math.sin(a)))
    m = shape(pts, "#f6e9a8", blob(ellipse_pts(30, 30, 40, 40, 16), "#e2cf7a", .9) +
              blob(ellipse_pts(40, -30, 9, 7, 10), "#e2cf7a", .9), w=5, seed=3050)
    st = ""
    for k, (sx, sy, r) in enumerate([(980, 380, 14), (990, 520, 10), (790, 370, 9)]):
        tw = 1 + 0.3 * math.sin(t * 6 + k * 2)
        pts2 = [(sx + (r if q % 2 == 0 else r * .4) * tw * math.cos(-math.pi / 2 + q * math.pi / 4),
                 sy + (r if q % 2 == 0 else r * .4) * tw * math.sin(-math.pi / 2 + q * math.pi / 4), 1) for q in range(8)]
        st += shape(pts2, "#ffe27a", "", w=2.4, seed=3060 + k)
    return f'<g transform="translate({x} {y}) rotate({f(rot)})">{m}</g>' + st


def bar_frame():
    s = []
    s.append(soft_shadow(540, BY + BH / 2 + 30, 470, 22, .3))
    s.append(shape(rect_pts(BX0, BY - BH / 2, BX1, BY + BH / 2, 30), "#efe3c6", blob(rect_pts(BX0, BY + 20, BX1, BY + BH / 2, 30), "#e0d0ac", .9),
                   w=6, seed=3100))
    # часы-засечки снизу (без цифр)
    for k in range(NC + 1):
        x = BX0 + 10 + k * (BX1 - BX0 - 20) / NC
        s.append(line([(x, BY + BH / 2 + 14), (x, BY + BH / 2 + (40 if k % 5 == 0 else 28))], 5 if k % 5 == 0 else 3.6, INK, taper=.05, wmin=.9,
                      seed=3110 + k))
    return "".join(s)


def red_cells():
    return [0, 1, 2, 3]


def s13_cells(t):
    s = []
    # пустые лунки
    for i in range(NC):
        x0, y0, x1, y1 = cell(i)
        s.append(shape(rect_pts(x0, y0, x1, y1, 14), "#d8c8a4", "", w=3, seed=3200 + i))
    for i in range(NC):
        x0, y0, x1, y1 = cell(i)
        ti = 25.36 + i * 0.035
        k = back_out(clamp((t - ti) / 0.16), 2.0)
        if k <= 0.02:
            continue
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        # красная волна по 4 клеткам слева
        red = 0.0
        if i in red_cells():
            tr = RED0 + (RED1 - RED0) * (i / 4.0) * 0.85
            red = smooth(tr, tr + 0.14, t)
        if i in red_cells() and t > CRUMB + 0.08 * i + 0.12:
            continue
        col = mix(DAYC[i], "#e2543f", red)
        sh = mix(lib.mul(DAYC[i], (0.9, 0.86, 0.84)), "#b93a2a", red)
        hi = mix("#fff6d0", "#ff9c8a", red)
        inner = blob(rect_pts(x0, (y0 + y1) / 2 + 18, x1, y1, 14), sh, .9) + blob(rect_pts(x0 + 10, y0 + 10, x1 - 22, y0 + 22, 6), hi, .9)
        wob = 0.0
        if red > 0 and i in red_cells():
            pulse = math.exp(-max(t - (RED0 + (RED1 - RED0) * (i / 4.0) * 0.85), 0) * 7)
            wob = 0.08 * pulse
        if i in red_cells() and t > CRUMB - 0.12:
            # трещины перед обвалом
            ck = smooth(CRUMB - 0.12, CRUMB + 0.05, t)
            inner += line([(x0 + 14, y0 + 6), (cx - 4, cy - 6), (cx + 10, cy + 10), (x1 - 12, y1 - 4)], 4, INK, taper=.4, wmin=.3,
                          seed=3300 + i, op=1.0) if ck > 0.05 else ""
        tr_ = f"translate({f(cx)} {f(cy)}) scale({f(k * (1 + wob))}) translate({f(-cx)} {f(-cy)})"
        s.append(f'<g transform="{tr_}">' + shape(rect_pts(x0, y0, x1, y1, 14), col, inner, w=4, seed=3220 + i) + "</g>")
    return "".join(s)


def crumbs(t):
    """Красные клетки ломаются на куски и падают вниз, крутясь; на их месте — пунктир."""
    s = []
    for i in red_cells():
        tc = CRUMB + 0.08 * i + 0.12
        e = t - tc
        if e < 0:
            continue
        x0, y0, x1, y1 = cell(i)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rs = np.random.RandomState(3400 + i)
        pieces = [
            [(x0, y0, 1), (cx + rs.uniform(-8, 8), y0, 1), (cx - 6, cy, 1), (x0, cy + rs.uniform(-6, 6), 1)],
            [(cx + rs.uniform(-8, 8), y0, 1), (x1, y0, 1), (x1, cy + 8, 1), (cx + 10, cy + 10, 1), (cx - 6, cy, 1)],
            [(x0, cy + rs.uniform(-6, 6), 1), (cx - 6, cy, 1), (cx + 10, cy + 10, 1), (cx + 4, y1, 1), (x0, y1, 1)],
            [(cx + 10, cy + 10, 1), (x1, cy + 8, 1), (x1, y1, 1), (cx + 4, y1, 1)],
        ]
        for k in range(6):
            px = rs.uniform(x0, x1)
            py = rs.uniform(y0, y1)
            vx, vy = rs.uniform(-120, 120), -rs.uniform(60, 220)
            ee = e + 0.02
            x, y = px + vx * ee, py + vy * ee + 2600 * ee * ee
            if y > H + 100:
                continue
            r = rs.uniform(6, 11)
            a0 = rs.uniform(0, 6.28) + 6 * ee
            s.append(shape([(x + r * math.cos(a0 + q * 2.1), y + r * math.sin(a0 + q * 2.1), 1) for q in range(3)], "#c94a36", "", w=2.4,
                           seed=3480 + i * 10 + k))
        for j, pts in enumerate(pieces):
            pcx = sum(p[0] for p in pts) / len(pts)
            pcy = sum(p[1] for p in pts) / len(pts)
            vx = (pcx - cx) * 3.2 + rs.uniform(-60, 60)
            vy = -rs.uniform(80, 240)
            dx, dy = vx * e, vy * e + 2300 * e * e
            if pcy + dy > H + 200:
                continue
            rot = rs.uniform(-1, 1) * 420 * e
            sh = blob([(p[0] + 4, p[1] + 10) for p in pts], "#b93a2a", .9)
            g = shape(pts, "#e2543f", "", w=3.6, seed=3420 + i * 10 + j)
            s.append(f'<g transform="translate({f(dx)} {f(dy)}) rotate({f(rot)} {f(pcx)} {f(pcy)})">{g}</g>')
    return "".join(s)


def lost_outline(t):
    """Пунктирная рамка на месте выкрошенных 40 %."""
    k = smooth(CRUMB + 0.3, CRUMB + 0.6, t)
    if k <= 0:
        return ""
    x0, y0 = cell(0)[0] - 6, cell(0)[1] - 6
    x1, y1 = cell(3)[2] + 6, cell(0)[3] + 6
    per = []
    for (ax, ay), (bx, by) in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
        L = math.hypot(bx - ax, by - ay)
        n = max(1, int(L / 34))
        for i in range(n):
            u0, u1 = i / n, (i + 0.55) / n
            per.append(((ax + (bx - ax) * u0, ay + (by - ay) * u0), (ax + (bx - ax) * u1, ay + (by - ay) * u1)))
    m = int(len(per) * k)
    return "".join(line([p, q], 6, "#d2442f", taper=.1, wmin=.8, seed=3500 + i) for i, (p, q) in enumerate(per[:m]))


def forty(t):
    e = t - TXT
    if e < -0.04:
        return ""
    k = back_out(clamp((e + 0.04) / 0.22), 2.4)
    x = 540
    y = 560
    wob = 3 * math.sin(e * 4) * (e > 0.25)
    txt = (f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="190" fill="#e2543f" '
           f'stroke="{INK}" stroke-width="12" stroke-linejoin="round" paint-order="stroke">40 %</text>')
    sh = (f'<text x="10" y="12" text-anchor="middle" font-family="IDB" font-weight="900" font-size="190" fill="#9c7a52" '
          f'stroke="#9c7a52" stroke-width="12" stroke-linejoin="round">40 %</text>')
    s = f'<g transform="translate({f(x)} {f(y + 70)}) rotate({f(-6 + wob)}) scale({f(k)})">{sh}{txt}</g>'
    s += burst(x, y, e, 0.32, 8, 200, 280, 44, "#e2543f", 9, 3600)
    # стрелка-указатель от цифры к красной части
    ka = smooth(TXT + 0.15, TXT + 0.35, t)
    if ka > 0:
        ax0, ay0 = x - 170, y + 96
        ax1, ay1 = (cell(0)[0] + cell(3)[2]) / 2 + 20, BY - BH / 2 - 16
        ay = ay0 + (ay1 - ay0) * ka
        axx = ax0 + (ax1 - ax0) * ka
        s += line([(ax0, ay0), ((ax0 + axx) / 2 - 10, (ay0 + ay) / 2), (axx, ay)], 9, INK, taper=.15, wmin=.6, seed=3620)
        if ka > 0.9:
            s += line([(ax1 - 4, ay - 34), (ax1, ay), (ax1 + 30, ay - 18)], 9, INK, taper=.15, wmin=.6, seed=3621)
    return s


def s13(t):
    s = [sun(t), moon(t), bar_frame(), lost_outline(t), s13_cells(t), crumbs(t), forty(t)]
    u = clamp((t - 25.36) / 2.6)
    e = t - TXT
    pop = 0.035 * math.exp(-max(e, 0) * 6) * (e > 0)
    ec = t - CRUMB - 0.12
    sh = 5 * math.exp(-max(ec, 0) * 6) * math.sin(ec * 45) * (ec > 0)
    cm = cam(540 + sh, 760 - 20 * u, 1.0 + 0.1 * ease_io(u) + pop, -0.6 + 1.2 * u)
    return "".join(s), cm


def build_static():
    if _ST:
        return
    _ST["bg"] = chart_bg()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s06": s06, "s11": s11, "s13": s13}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#f0e4c8"/><g transform="{cm}">{_ST["bg"]}{art}</g>')
