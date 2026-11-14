"""Сцена chart рилса 40 «66 дней»: график привычки на тетрадном листе в клетку на столе.
s12: рука ручкой ведёт кривую «привычка» по дням — растёт и выходит на плато, точки-отметки встают по ходу; на
«шестьдесят» (22.68) на кривую втыкается флажок, крупная «66» падает с отскоком, на «дней» (23.52) — подпись.
s13: тот же график; на «пропуск» (24.48) одна точка проваливается вниз и краснеет, кривая не падает — жёлтый маркер
ведёт её дальше вверх до стрелки; на «ничего» (25.04) у ямки зелёная галочка."""
import math

import numpy as np

import hand
import lib
from calbase import check
from lib import (DEFS, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad,
                 rect_pts, shape, svg)

_ST = {}
OX, OY, XL, YT = 190, 1120, 950, 350        # начало осей, конец оси X, верх оси Y
DAYS = 90
BLUE, ORANGE, RED, GREEN = "#2f4f9a", "#e2602b", "#d83a2e", "#2f9a4a"
AX = "#27304a"
PX0, PY0, PX1, PY1 = 70, 230, 1010, 1290    # лист
DIP = 42
FLAG_T, N66_T, DNEY_T = 22.68, 22.70, 23.52
DIP_T, OK_T = 24.48, 25.04


def X(d):
    return OX + d * (720 / DAYS)


def V(d):
    return 1 - math.exp(-d / 22.0)


def Y(d):
    return OY - 640 * V(d)


_rs = np.random.RandomState(12)
DOTS = [(d, _rs.uniform(-9, 9)) for d in range(3, DAYS + 1, 3)]
T_DRAW0, T_DRAW1 = 20.72, 22.32


def dmax(t):
    u = clamp((t - T_DRAW0) / (T_DRAW1 - T_DRAW0))
    return DAYS * (0.55 * u + 0.45 * ease_io(u))


def t_of_d(d):
    lo, hi = T_DRAW0, T_DRAW1
    for _ in range(30):
        m = (lo + hi) / 2
        if dmax(m) < d:
            lo = m
        else:
            hi = m
    return hi


def desk():
    s = [f'<rect x="-1600" y="-1600" width="{W + 3200}" height="{H + 3200}" fill="#b07a4a"/>']
    rs = np.random.RandomState(4)
    for k in range(-14, 30):
        y = k * 150
        s.append(line([(-1600, y), (W + 1600, y + rs.uniform(-6, 6))], 3, "#8a5a33", taper=.05, wmin=.9, seed=200 + k))
        for j in range(3):
            x0 = rs.uniform(-600, 1600)
            s.append(line([(x0, y + rs.uniform(30, 120)), (x0 + rs.uniform(200, 500), y + rs.uniform(30, 120))], 2.2, "#9c6a3e",
                          taper=.6, seed=300 + k * 5 + j))
    g = lib.rad_grad([(0, "#ffe2a8", .45), (.6, "#ffd08a", .1), (1, "#ffd08a", 0)], 400, 400, 1300, 1300)
    s.append(f'<rect x="-1600" y="-1600" width="{W + 3200}" height="{H + 3200}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    g2 = lib.rad_grad([(0, "#000", 0), (.5, "#000", 0), (1, "#1a0c03", .5)], 540, 800, 1300, 1550)
    s.append(f'<rect x="-1600" y="-1600" width="{W + 3200}" height="{H + 3200}" fill="url(#{g2})"/>')
    return "".join(s)


def paper():
    s = [blob([(PX0 + 20, PY0 + 26, 1), (PX1 + 26, PY0 + 22, 1), (PX1 + 30, PY1 + 30, 1), (PX0 + 24, PY1 + 34, 1)], "#2a1406", .4, blur(14))]
    inner = ""
    for x in np.arange(PX0 + 10, PX1, 36):
        inner += f'<rect x="{f(x)}" y="{PY0}" width="2" height="{PY1 - PY0}" fill="#b9cde3"/>'
    for y in np.arange(PY0 + 14, PY1, 36):
        inner += f'<rect x="{PX0}" y="{f(y)}" width="{PX1 - PX0}" height="2" fill="#b9cde3"/>'
    gid = lin_grad([(0, "#ffffff", 0), (1, "#d9cdb4", .35)], 0, 0, 0, 1)
    inner += f'<rect x="{PX0}" y="{PY0}" width="{PX1 - PX0}" height="{PY1 - PY0}" fill="url(#{gid})"/>'
    s.append(shape([(PX0, PY0, 1), (PX1, PY0, 1), (PX1, PY1, 1), (PX0, PY1, 1)], "#fbfaf4", inner, w=4.2, seed=5))
    return "".join(s)


def axes():
    s = []
    s.append(line([(OX, OY + 20), (OX - 1, (OY + YT) / 2), (OX, YT)], 7, AX, taper=.1, wmin=.8, seed=11))
    s.append(line([(OX - 20, OY), ((OX + XL) / 2, OY + 1), (XL, OY)], 7, AX, taper=.1, wmin=.8, seed=12))
    s.append(line([(OX - 18, YT + 34), (OX, YT - 4), (OX + 18, YT + 34)], 7, AX, taper=.2, wmin=.6, seed=13))
    s.append(line([(XL - 34, OY - 18), (XL + 4, OY), (XL - 34, OY + 18)], 7, AX, taper=.2, wmin=.6, seed=14))
    for d in (30, 60, 90):
        x = X(d)
        s.append(line([(x, OY - 12), (x, OY + 12)], 4, AX, taper=.2, seed=15 + d))
        s.append(f'<text x="{f(x)}" y="{OY + 52}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="34" fill="{AX}">{d}</text>')
    s.append(f'<text x="{XL - 10}" y="{OY + 100}" text-anchor="end" font-family="IDB" font-weight="900" font-size="52" fill="{AX}">дни</text>')
    s.append(f'<text x="{OX + 36}" y="{YT + 18}" text-anchor="start" font-family="IDB" font-weight="900" font-size="52" fill="{AX}">привычка</text>')
    return "".join(s)


def curve_pts(d0, d1, step=1.5):
    n = max(2, int((d1 - d0) / step) + 1)
    return [(X(d), Y(d)) for d in np.linspace(d0, d1, n)]


def dot(d, jit, sc=1.0, color=BLUE, dy=0.0):
    x, y = X(d), Y(d) + jit + dy
    r = 9 * sc
    return shape(ellipse_pts(x, y, r, r, 12), color, blob(ellipse_pts(x - r * .3, y - r * .35, r * .35, r * .28, 8), "#ffffff", .9),
                 w=3.0, seed=int(d) + 40)


def flag(t):
    e = t - FLAG_T
    if e < -0.1:
        return ""
    x, y = X(66), Y(66)
    if e < 0:
        fall = 1 - ease_in((e + 0.1) / 0.1, 2)
        dy, rot = -520 * fall, 0.0
    else:
        dy = 0.0
        rot = 9 * math.exp(-e * 6) * math.sin(e * 22)
    L = 190
    wave = math.sin(t * 9)
    pole = shape([(x - 4, y - L, 1), (x + 4, y - L, 1), (x + 4, y, 1), (x - 4, y + 6, 1)], "#6b4a2a", "", w=3.0, seed=71)
    top = y - L
    cloth = [(x + 4, top + 2, 1), (x + 60, top + 14 + 6 * wave), (x + 118, top + 30 + 4 * wave, 1), (x + 62, top + 52 + 6 * wave),
             (x + 4, top + 66, 1)]
    cl = shape(cloth, RED, blob([(x + 4, top + 44), (x + 62, top + 40 + 6 * wave), (x + 118, top + 30 + 4 * wave), (x + 62, top + 52 + 6 * wave),
                                  (x + 4, top + 66)], "#a92f29"), w=3.6, seed=72)
    knob = shape(ellipse_pts(x, top - 6, 9, 9, 10), "#e8b23a", "", w=2.6, seed=73)
    out = f'<g transform="translate(0 {f(dy)}) rotate({f(rot)} {f(x)} {f(y)})">{pole}{cl}{knob}</g>'
    if 0 <= e < 0.22:
        a = 1 - e / 0.22
        for j, ang in enumerate((-160, -130, -50, -20)):
            r0, r1 = 22 + 40 * (1 - a), 46 + 60 * (1 - a)
            c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            out += line([(x + r0 * c, y + r0 * s_), (x + r1 * c, y + r1 * s_)], 8 * a + 1, AX, taper=.5, seed=80 + j)
    return out


def guide(t):
    e = t - (FLAG_T + 0.08)
    if e < 0:
        return ""
    u = ease_out(clamp(e / 0.25))
    x, y = X(66), Y(66) + 14
    y1 = y + (OY - y) * u
    out = []
    yy = y
    while yy < y1:
        out.append(line([(x, yy), (x, min(y1, yy + 18))], 4.4, ORANGE, taper=.2, wmin=.7, seed=int(yy)))
        yy += 32
    return "".join(out)


def big66(t):
    e = t - N66_T
    if e < 0:
        return ""
    cx, by = 548, 960
    land = 0.22
    if e < land:
        dy = -1100 * (1 - ease_in(e / land, 2))
        sx, sy = 0.94, 1.08
    else:
        q = e - land
        dy = -70 * math.exp(-q * 7) * abs(math.sin(q * 13))
        k = math.exp(-q * 9) * math.cos(q * 30)
        sx, sy = 1 + 0.14 * k, 1 - 0.16 * k
    txt = (f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="300" fill="{ORANGE}" '
           f'stroke="{AX}" stroke-width="10" paint-order="stroke" stroke-linejoin="round">66</text>')
    out = f'<g transform="translate({cx} {f(by + dy)}) scale({f(sx)} {f(sy)})">{txt}</g>'
    if land <= e < land + 0.25:
        a = 1 - (e - land) / 0.25
        for j, (dx, ang) in enumerate(((-190, 200), (-170, 160), (190, -20), (170, 20))):
            c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            x0, y0 = cx + dx, by - 10
            out += line([(x0, y0), (x0 + c * 60 * (1.4 - a), y0 + s_ * 60 * (1.4 - a))], 9 * a + 1, AX, taper=.5, seed=90 + j)
    return out


def dney(t):
    e = t - (DNEY_T - 0.04)
    if e < 0:
        return ""
    sc = back_out(clamp(e / 0.2), 2.2)
    return (f'<g transform="translate(548 1070) scale({f(sc)})"><text x="0" y="0" text-anchor="middle" font-family="IDB" '
            f'font-weight="900" font-size="104" fill="{AX}">дней</text></g>')


def chart_full(t, dm, dip_e=None, hl=0.0):
    """Весь график на момент t: кривая до дня dm, точки, флажок, 66, дней; dip_e — секунды с провала точки."""
    s = []
    if hl > 0:
        s.append(line(curve_pts(DIP, DIP + (DAYS - DIP) * hl), 30, "#ffd84a", taper=.15, wmin=.6, seed=95))
    if dm > 0.5:
        s.append(line(curve_pts(0, dm), 9, ORANGE, taper=.08, wmin=.75, seed=21, peak=.5))
    for d, j in DOTS:
        if d > dm + 0.01:
            continue
        if d == DIP and dip_e is not None and dip_e >= 0:
            drop = 66 * (1 - math.exp(-dip_e * 10) * math.cos(dip_e * 22))
            s.append(dot(d, j, 1.6, RED, drop))
            continue
        e = t - t_of_d(d) if t < T_DRAW1 + 0.2 else 1.0
        sc = 1.0 if e > 0.1 else 1 + 0.6 * (1 - e / 0.1)
        s.append(dot(d, j, sc))
    if hl >= 1:
        x, y = X(DAYS), Y(DAYS)
        s.append(line([(x - 30, y - 24), (x + 6, y), (x - 30, y + 22)], 10, ORANGE, taper=.2, wmin=.6, seed=96))
    s.append(guide(t))
    s.append(flag(t))
    s.append(big66(t))
    s.append(dney(t))
    return "".join(s)


def pen_tip12(t):
    if t < T_DRAW0:
        return X(0), Y(0)
    if t <= T_DRAW1:
        d = dmax(t)
        return X(d), Y(d)
    u = ease_in(clamp((t - T_DRAW1) / 0.3), 1.6)
    x0, y0 = X(DAYS), Y(DAYS)
    return x0 + (1450 - x0) * u, y0 + (1500 - y0) * u


def kick(t, times, amp=0.03, dec=14):
    s, rot = 1.0, 0.0
    for tt in times:
        q = t - tt
        if q >= 0:
            s *= 1 + amp * math.exp(-q * dec) * math.cos(q * 26)
            rot += amp * 16 * math.exp(-q * dec) * math.sin(q * 30)
    return s, rot


def frame12(t):
    s = [_ST["desk"], f'<g transform="rotate(-1 540 760)">', _ST["paper"], _ST["axes"]]
    s.append(chart_full(t, min(DAYS, dmax(t))))
    if t <= T_DRAW1 + 0.32:
        px, py = pen_tip12(t)
        ang = -36 + 4 * math.sin(t * 7)
        s.append(f'<g transform="translate({f(px + 22)} {f(py + 28)}) scale(.85)" opacity=".26" filter="url(#fShH)">{hand.hand(ang, 9)}</g>')
        s.append(hand.draw(px, py, ang, 0.85, 9))
    s.append("</g>")
    return "".join(s)


def cam12(t):
    u = ease_io(clamp((t - 20.7) / 2.1))
    sc = 1.02 + 0.2 * u
    cx = 540 + 20 * u + 6 * math.sin(t * 1.3)
    cy = 790 + 50 * u
    k, rot = kick(t, [FLAG_T], 0.03)
    k2, rot2 = kick(t, [N66_T + 0.22], 0.06, 10)
    k3, rot3 = kick(t, [DNEY_T], 0.02)
    sh = 0.0
    q = t - (N66_T + 0.22)
    if q >= 0:
        sh = 10 * math.exp(-q * 9) * math.sin(q * 60)
    return cam(cx + sh, cy, sc * k * k2 * k3, rot + rot2 + rot3 - 1.2 + 1.0 * u)


def frame13(t):
    s = [_ST["desk"], f'<g transform="rotate(-1 540 760)">', _ST["paper"], _ST["axes"]]
    hl = ease_io(clamp((t - (DIP_T + 0.18)) / 0.85))
    s.append(chart_full(t, DAYS, t - DIP_T, hl))
    # зелёная галочка у ямки — пишется за 0.14 с
    e = t - (OK_T - 0.06)
    if e >= 0:
        cx, cy = X(DIP) + 78, Y(DIP) + 112
        s.append(check(cx, cy, 50, e, 1234, color=GREEN, wk=0.2))
    if DIP_T <= t < DIP_T + 0.25:
        a = 1 - (t - DIP_T) / 0.25
        x, y = X(DIP), Y(DIP) + 66
        for j, ang in enumerate((150, 200, -20, 30)):
            c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            s.append(line([(x + 22 * c, y + 22 * s_), (x + (40 + 30 * (1 - a)) * c, y + (40 + 30 * (1 - a)) * s_)], 7 * a + 1, RED,
                          taper=.5, seed=60 + j))
    s.append("</g>")
    return "".join(s)


def cam13(t):
    a = ease_io(clamp((t - 23.7) / 0.75))
    b = ease_io(clamp((t - 25.25) / 0.75))
    c0 = (560, 840, 1.22)
    c1 = (X(DIP) - 10, Y(DIP) + 60, 1.85)
    c2 = (565, 830, 1.2)
    cx = c0[0] + (c1[0] - c0[0]) * a + (c2[0] - c1[0]) * b
    cy = c0[1] + (c1[1] - c0[1]) * a + (c2[1] - c1[1]) * b
    sc = c0[2] + (c1[2] - c0[2]) * a + (c2[2] - c1[2]) * b
    sc *= 1 + 0.015 * math.sin(t * 2)
    k, rot = kick(t, [DIP_T], 0.04, 12)
    k2, rot2 = kick(t, [OK_T], 0.03, 12)
    return cam(cx + 5 * math.sin(t * 1.6), cy, sc * k * k2, rot + rot2 - 0.2 + 0.8 * a - 0.6 * b)


def frame(sid, t):
    if not _ST:
        DEFS.append('<filter id="fShH" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                    '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
        _ST["desk"] = desk()
        _ST["paper"] = paper()
        _ST["axes"] = axes()
        lib.static_done()
    lib.dyn_begin()
    fr, cm = {"s12": (frame12, cam12), "s13": (frame13, cam13)}[sid]
    return svg(f'<rect width="{W}" height="{H}" fill="#b07a4a"/><g transform="{cm(t)}">{fr(t)}</g>')


_ = (rect_pts,)
