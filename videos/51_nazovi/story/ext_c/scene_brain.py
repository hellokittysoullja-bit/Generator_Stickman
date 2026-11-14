"""s12: мозг в разрезе (вид сбоку). Красная миндалина пульсирует на «тревожный центр мозга» (22.0–22.76), кольца тревоги расходятся,
на «успокаивался» (23.12) она остывает в зелёную, кольца затихают, пульс ровнеет. Подпись «миндалина» пишется пером на «центр» (22.4)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hw  # noqa: E402
import lib  # noqa: E402
from lib import (INK, W, H, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, shape, smooth, spring)  # noqa: E402

BX, BY = 540, 640           # центр мозга
K = 1.15                    # масштаб мозга на экране
OUT = [(-400, 40), (-382, -78), (-304, -186), (-172, -250), (0, -276), (172, -256), (302, -196), (382, -102), (402, 18), (362, 108), (292, 148),
       (204, 150), (150, 178), (60, 200), (-60, 214), (-170, 190), (-262, 150), (-340, 118)]
AMY = (-70, 112)


def sc_pts(pts, k, dx=0, dy=0):
    return [(x * k + dx, y * k + dy) for x, y in pts]


def gyri(t):
    """Извилины: волнистые контуры внутри разреза + пара поперечных складок."""
    s = []
    for j, k in enumerate((0.80, 0.62, 0.44)):
        ring = []
        for i in range(60):
            a = 2 * math.pi * i / 60
            r = 1 + 0.05 * math.sin(7 * a + j) + 0.04 * math.sin(11 * a + 2 * j)
            ring.append((math.cos(a) * 372 * k * r + 4, math.sin(a) * 222 * k * r - 24))
        s.append(line(ring[:46] if j % 2 == 0 else ring[10:56], 7.5 - j, "#c9707a", taper=.4, wmin=.5, seed=60 + j, op=.9))
    for j, (x, y) in enumerate([(-250, -110), (-60, -190), (150, -170), (280, -60), (-300, 30), (240, 70)]):
        a = [(x, y), (x + 40, y + 24), (x + 30, y + 64), (x + 70, y + 84)]
        s.append(line(a, 7, "#c9707a", taper=.4, wmin=.5, seed=80 + j, op=.9))
    return "".join(s)


def brain_body(col, sz):
    s = []
    # мозжечок и ствол — сзади
    s.append(shape(ellipse_pts(262, 186, 118, 78, 20, rot=-14), "#e07f8b", "".join(line([(172 + 8 * k, 150 + 10 * k), (352 + 4 * k, 132 + 12 * k)], 5, "#b85a68", seed=120 + k, taper=.3, op=.8) for k in range(1, 7)), w=5.4, seed=111))
    s.append(shape([(100, 120), (190, 120), (214, 360), (150, 380), (110, 300)], "#dc8089", blob([(170, 120), (214, 360), (150, 380)], "#bd5f6c", .85), w=5.4, seed=112))
    # большое полушарие
    s.append(shape(OUT, "#eb9aa0", blob(sc_pts(OUT, 1.0, 26, 20), "#d17580", .9), w=7.4, seed=113))
    s.append(blob(sc_pts(OUT, 0.9, 0, -6), "#f6c4c0", 1.0))
    s.append(blob([(-300, 30), (-120, 100), (120, 110), (330, 50), (320, 100), (120, 150), (-120, 150), (-300, 100)], "#eaa9ac", .55))
    s.append(gyri(0))
    # мозолистое тело
    s.append(line([(-250, -20), (-160, -80), (0, -96), (160, -80), (250, -20)], 16, "#fbe9e0", taper=.2, wmin=.7, seed=140, peak=.5))
    s.append(line([(-250, -20), (-160, -80), (0, -96), (160, -80), (250, -20)], 3, "#b85a68", taper=.2, wmin=.7, seed=141, op=.7))
    return "".join(s)


def amygdala(col, sz, t, lite):
    x, y = AMY
    g = f'<g transform="translate({x} {y}) scale({sz:.4f}) rotate(-28)">'
    g += shape([(-58, 4), (-44, -26), (-6, -38), (40, -28), (62, 2), (44, 30), (4, 38), (-38, 30)], col,
               blob([(0, 6), (62, 2), (44, 30), (4, 38), (-38, 30)], mix(col, "#000000", .28), .55) + blob(ellipse_pts(-18, -16, 20, 8, 10, rot=-10), mix(col, "#ffffff", .5), .8), w=6, seed=150)
    g += "</g>"
    return g


def ring_set(t, alarm_end, col_a, col_c, cx, cy):
    s = []
    ems = []
    e = 21.6
    while e < alarm_end:
        ems.append((e, 0)); e += 0.30 - 0.04 * clamp((e - 22.0) / 0.8)
    e = alarm_end + 0.1
    while e < 25.0:
        ems.append((e, 1)); e += 0.85
    for (e, kind) in ems:
        age = t - e
        if age < 0 or age > (0.95 if kind == 0 else 1.7):
            continue
        u = age / (0.95 if kind == 0 else 1.7)
        r = 70 + (480 if kind == 0 else 300) * ease_out(u, 2)
        a = (0.65 if kind == 0 else 0.42) * (1 - u)
        c = col_a if kind == 0 else col_c
        s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(r * 1.2)}" ry="{f(r * 1.1)}" fill="none" stroke="{c}" stroke-width="{f(3 + 12 * (1 - u))}" opacity="{a:.3f}"/>')
    return "".join(s)


def alarm_spikes(t, cx, cy, strength):
    s = []
    if strength < .05:
        return ""
    for i in range(14):
        th = 2 * math.pi * i / 14 + 0.3
        ph = (t * 7 + i * .61) % 1.0
        r0 = 150 + 60 * ph
        L = (46 + 30 * (i % 3)) * strength
        d = (math.cos(th), math.sin(th))
        n = (-d[1], d[0])
        p0 = (cx + d[0] * r0, cy + d[1] * r0)
        zig = [p0, (p0[0] + d[0] * L * .35 + n[0] * 10, p0[1] + d[1] * L * .35 + n[1] * 10), (p0[0] + d[0] * L * .65 - n[0] * 10, p0[1] + d[1] * L * .65 - n[1] * 10),
               (p0[0] + d[0] * L, p0[1] + d[1] * L)]
        s.append(line(zig, 8, "#ffd04a", taper=.5, wmin=.3, seed=200 + i, op=(1 - ph) * strength))
    return "".join(s)


_L = {}


def label():
    if "l" not in _L:
        _L["l"] = hw.Line("миндалина", 116, 96, 1090, "#fff0c8", span=(22.38, 22.92))
    return _L["l"]


def ecg(t, calm, col):
    """Лента пульса внизу: острые всплески, пока тревога, ровная волна после."""
    x0, x1, y0 = 120, 960, 1236
    pts = []
    for i in range(0, 85):
        x = x0 + i * (x1 - x0) / 84
        ph = (x * 0.012 - t * 5.0)
        spike = max(0.0, 1 - abs(((ph / (2 * math.pi)) % 1) - .5) * 14)
        amp_s = (1 - calm) * (30 + 78 * spike) * (1 if (int(ph / (2 * math.pi)) % 2 == 0 or True) else 1)
        y = y0 - amp_s * (1 if spike > 0 else 0) * 1.0 + 0
        y = y0 - (1 - calm) * (24 * spike * 3.2) * math.copysign(1, math.sin(ph * 2.0) + 0.001) - calm * 16 * math.sin(ph * 0.5 + 1)
        pts.append((x, y))
    return line(pts, 7, col, taper=.1, wmin=.8, seed=222)


def s12(t):
    alarm = smooth(21.7, 22.05, t) * (1 - smooth(23.12, 23.55, t))
    c = smooth(23.12, 23.6, t)                       # остывание
    pre = 0.35 if t < 22.0 else 1.0
    colt = mix(mix("#f08a3a", "#e0302a", clamp((t - 21.8) / 0.3)), "#3fb86a", c)
    # пульс миндалины
    if t < 23.12:
        ph = (t - 21.6) * (2.6 if t < 22.0 else 3.4)
        pul = abs(math.sin(math.pi * ph)) ** 1.5
        sz = 1.0 + (0.12 + 0.36 * clamp((t - 21.95) / 0.12) * 1.0) * pul * pre + 0.5 * spring(t - 22.0, 2.4, 6.0) * (t >= 22.0) * (1 - smooth(22.8, 23.12, t))
    else:
        sz = 1.0 + 0.10 * (1 - smooth(23.12, 23.8, t)) * math.sin((t - 23.12) * 8) + 0.04 * math.sin((t - 23.12) * 2.4)
    bg1 = mix(mix("#20284a", "#4a1c2a", alarm), "#1d4a4c", c)
    bg2 = mix(mix("#33406a", "#7a2a34", alarm), "#2f7a70", c)
    g = lin_grad([(0, bg1, 1), (1, bg2, 1)], 0, 0, 0, 1)
    s = [f'<rect x="-1500" y="-1500" width="{W + 3000}" height="{H + 3000}" fill="url(#{g})"/>']
    ax, ay = BX + AMY[0] * K, BY + AMY[1] * K
    gl = rad_grad([(0, colt, .75), (.45, colt, .22), (1, colt, 0)], ax, ay, 520)
    s.append(f'<rect x="-1500" y="-1500" width="{W + 3000}" height="{H + 3000}" fill="url(#{gl})"/>')
    s.append(ring_set(t, 23.12, "#ff4a3a", "#7ee8a4", ax, ay))
    jx = 7 * alarm * math.sin(t * 61) * math.sin(t * 37 + 1)
    jy = 6 * alarm * math.sin(t * 53 + 2)
    br = 1 + 0.012 * math.sin(t * 2.6) + 0.02 * alarm * abs(math.sin(t * 20))
    tilt = 1.2 * math.sin(t * 1.3)
    bod = brain_body(colt, sz) + amygdala(colt, sz, t, 0)
    s.append(f'<g transform="translate({f(BX + jx)} {f(BY + jy)}) rotate({tilt:.3f}) scale({br * K:.4f})">{bod}</g>')
    s.append(alarm_spikes(t, ax, ay, alarm))
    # подпись и стрелка
    ln = label()
    s.append(ln.svg(t))
    if t > 22.7:
        u = ease_out(clamp((t - 22.7) / 0.35), 2)
        ex, ey = ax - 8, ay + 38
        p = [(300, 1010), (350, 950), (410, 880), (ex, ey)]
        k = max(2, int(2 + (len(p) - 2) * u)) if u < 1 else len(p)
        s.append(line(p[:k], 7, "#fff0c8", taper=.5, wmin=.5, seed=230))
        s.append(line([(ex, ey), (ex - 28, ey + 4), (ex - 6, ey - 26)], 7, "#fff0c8", taper=.2, wmin=.7, seed=231, op=u))
    s.append(ecg(t, c, mix("#ff6a5a", "#7ee8a4", c)))
    a = ease_io(clamp((t - 21.8) / 2.4))
    zs = 1.0 + 0.04 * a + 0.09 * smooth(22.0, 22.5, t) * (1 - smooth(23.1, 23.7, t))
    cm = cam(540 + 10 * math.sin(t * 1.1), 760 + 30 * a + 16 * alarm * math.sin(t * 45), zs, 0.7 * math.sin(t * 1.4) + 1.4 * alarm * math.sin(t * 33))
    return f'<g transform="{cm}">{"".join(s)}</g>'
