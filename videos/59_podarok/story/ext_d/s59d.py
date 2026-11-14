"""Рилс 59 «подарок», группа D: s09 (календарь без цифр, ночь) и s10 (цветочный ларёк). frame(sid, t) -> SVG 1080×1920,
t — общее время ролика. Герои — people.py/hand.py (Дима и остальные рилсов 55–57); продавщица — people.PAL['seller'] (свой цвет, причёска, фартук)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import lib  # noqa: E402
import people  # noqa: E402
from lib import (INK, back_out, blob, blur, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rrect,  # noqa: E402,F401
                 shape, smooth, spring)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def find(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after and w["word"].strip(".,!?").lower() == word:
            return w["start"]
    raise KeyError(word)


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def lerp(a, b, u):
    return a + (b - a) * u


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def dima(hip, bs, lean, arms, hands, expr, feet=None, head_ang=0.0, head_off=(0, 0), torso_k=1.0, who="dima", hood=0.0, strings=(0, 0)):
    p = dict(hip=tuple(hip), scale=bs, lean=lean, torso_k=torso_k, feet=feet, arms=arms, hands=hands, expr=expr, head_ang=head_ang,
             head_off=head_off, hood=hood, strings=strings)
    return people.draw(p, who)


def open_hand(c=.2, d=(1, 0), spread=.2, thumb=.2, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(c, c, c, c * .9), spread=spread, thumb=thumb, bend=.1, k=k)


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def partial(pts, u, step=4.0):
    """Первая доля u ломаной (для рисуемых от руки линий)."""
    pts = [(float(p[0]), float(p[1])) for p in pts]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(seg)
    goal = tot * clamp(u)
    out = [pts[0]]
    acc = 0.0
    for i, s_ in enumerate(seg):
        if acc + s_ >= goal:
            k = (goal - acc) / max(s_, 1e-6)
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k))
            return out
        acc += s_
        out.append(pts[i + 1])
    return out


def glint(cx, cy, k, r=60, color="#ffffff"):
    """Четырёхлучевая звёздочка: растёт и тает (k 0→1)."""
    if not 0 < k < 1:
        return ""
    a = r * math.sin(math.pi * k) ** .7
    pts = [(cx, cy - a, 1), (cx + a * .16, cy - a * .16, 1), (cx + a, cy, 1), (cx + a * .16, cy + a * .16, 1), (cx, cy + a, 1),
           (cx - a * .16, cy + a * .16, 1), (cx - a, cy, 1), (cx - a * .16, cy - a * .16, 1)]
    return blob(pts, color, 0.95)


def burst(cx, cy, k, n=10, r0=60, r1=170, w=10, color="#fff4c2", seed=0, a0=0.0, spread=360):
    if not 0 < k < 1:
        return ""
    s = []
    for j in range(n):
        a = math.radians(a0 + spread * j / n + 7 * math.sin(j * 2.3))
        ra = r0 + (r1 - r0) * ease_out(k, 2) * (0.8 + 0.2 * math.sin(j * 1.7))
        rb = ra + (r1 - r0) * 0.55 * (1 - k)
        s.append(line([(cx + ra * math.cos(a), cy + ra * math.sin(a)), (cx + rb * math.cos(a), cy + rb * math.sin(a))],
                      w * (1 - k) + 1.5, color, taper=.6, wmin=.2, seed=seed + j))
    return "".join(s)


def drop(cx, cy, sz, sd, col="#8fd0f5"):
    pts = [(cx, cy - sz * 1.15, 1), (cx + sz * .62, cy + sz * .25), (cx + sz * .5, cy + sz * .8), (cx, cy + sz * 1.0), (cx - sz * .5, cy + sz * .8),
           (cx - sz * .62, cy + sz * .25)]
    s = shape(pts, col, blob([(cx - sz * .3, cy - sz * .1), (cx + sz * .55, cy + sz * .4), (cx + sz * .35, cy + sz * .9), (cx, cy + sz * .95)], "#5fb0e0", .8),
              w=3.6, seed=sd)
    return s + blob(ellipse_pts(cx - sz * .22, cy + sz * .2, sz * .12, sz * .22, 8, rot=20), "#ffffff", .95)


# ═════════════════════════════ s09 16.5–19.04: календарь ═════════════════════════════
T_A = find("а", 16.5)                 # 16.88
T_DEN = find("день", 16.5)            # 17.008
T_ROZH = find("рождения", 16.5)       # 17.244
T_ZAV = find("завтра", 16.5)          # 18.24
GY9 = 1190                            # линия пола
CAL = (730, 740, 2.0)                 # центр календаря на стене, масштаб (база 250×290)
BDAY = (4, 3)                         # (колонка, строка) клетки дня рождения
DIMA_X = 380


def cal_cell(c, r):
    """Центр клетки календаря (колонка c, строка r) в мире (до качания)."""
    cx, cy, s = CAL
    return cx + (-125 + 24 + c * 34) * s, cy + (-145 + 108 + r * 36) * s


def wall_night(t):
    s = []
    g = lib.lin_grad([(0, "#9aa6c4", 1), (1, "#b7bfd2", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-400" y="-400" width="1900" height="{GY9 + 400}" fill="url(#{g})"/>')
    for x in range(-400, 1500, 150):             # обои: широкие полосы
        s.append(f'<rect x="{x}" y="-400" width="64" height="{GY9 + 400}" fill="#8793b4" opacity=".22"/>')
    # плинтус и пол
    s.append(blob(rrect(-400, GY9 - 70, 1500, GY9), "#e9e4dc"))
    s.append(line([(-400, GY9 - 70), (1500, GY9 - 70)], 4, INK, taper=.02, wmin=1, seed=9010))
    gf = lib.lin_grad([(0, "#9c7650", 1), (1, "#6e4f35", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-400" y="{GY9}" width="1900" height="1400" fill="url(#{gf})"/>')
    s.append(line([(-400, GY9), (1500, GY9)], 5, INK, taper=.02, wmin=1, seed=9011))
    for k in range(1, 9):
        y = GY9 + k * 66 + k * k * 4
        s.append(line([(-400, y), (1500, y + 4)], 3, "#5a3e28", taper=.05, wmin=.9, seed=9020 + k, op=.5))
    for xx in range(-400, 1500, 300):
        for k in range(0, 6):
            y = GY9 + k * 66 + k * k * 4
            s.append(line([(xx + (k % 2) * 150, y), (xx + (k % 2) * 150 + 3, y + 70 + k * 6)], 2.4, "#5a3e28", taper=.05, wmin=.9, seed=9040 + k, op=.45))
    return "".join(s)


def night_window(t, x0=30, y0=330, w=280, h=500):
    """Окно с ночным небом: луна, мерцающие звёзды, плывущее облако, штора."""
    s = []
    cid = lib.clip_rect(x0, y0, w, h, 6)
    g = lib.lin_grad([(0, "#141c3e", 1), (1, "#2d3d76", 1)], 0, 0, 0, 1)
    sky = f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#{g})"/>'
    rs = np.random.RandomState(5)
    for i in range(16):
        sx, sy = x0 + rs.uniform(14, w - 14), y0 + rs.uniform(14, h * .7)
        tw = .55 + .45 * math.sin(t * rs.uniform(2, 5) + rs.uniform(0, 6))
        sky += glint(sx, sy, .5, 5 + 9 * tw * rs.uniform(.6, 1), "#fff6d8") if False else \
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{1.6 + 2.2 * tw:.1f}" fill="#fff6d8" opacity="{.5 + .5 * tw:.2f}"/>'
    mx, my = x0 + w * .68, y0 + h * .24
    sky += blob(ellipse_pts(mx, my, 70, 70, 20), "#fff1b8", .25, blur(14))
    sky += blob(ellipse_pts(mx, my, 40, 40, 20), "#fdf0c0", 1.0)
    sky += blob(ellipse_pts(mx + 16, my - 8, 36, 36, 20), "#27386e", 1.0)
    cx_ = x0 - 120 + ((t * 18) % (w + 240))
    sky += blob(ellipse_pts(cx_, y0 + h * .5, 70, 20, 14), "#4c5c94", .8) + blob(ellipse_pts(cx_ + 40, y0 + h * .5 - 10, 44, 18, 14), "#4c5c94", .8)
    s.append(f'<g clip-path="url(#{cid})">{sky}</g>')
    # рама
    s.append(shape(rrect(x0 - 14, y0 - 14, x0 + w + 14, y0 + h + 14, 8), "none", "", w=6, seed=9100, ink=True))
    s.append(blob(rrect(x0 - 14, y0 - 14, x0 + w + 14, y0 - 2), "#f2ecdf") + blob(rrect(x0 - 14, y0 + h + 2, x0 + w + 14, y0 + h + 14), "#f2ecdf"))
    s.append(blob(rrect(x0 - 14, y0 - 14, x0 - 2, y0 + h + 14), "#f2ecdf") + blob(rrect(x0 + w + 2, y0 - 14, x0 + w + 14, y0 + h + 14), "#f2ecdf"))
    s.append(line([(x0 + w / 2, y0), (x0 + w / 2, y0 + h)], 7, "#f2ecdf", taper=0, wmin=1, seed=9101))
    s.append(line([(x0 + w / 2, y0), (x0 + w / 2, y0 + h)], 3, INK, taper=0, wmin=1, seed=9102, op=.8))
    s.append(line([(x0, y0 + h * .5), (x0 + w, y0 + h * .5)], 7, "#f2ecdf", taper=0, wmin=1, seed=9103))
    s.append(line([(x0, y0 + h * .5), (x0 + w, y0 + h * .5)], 3, INK, taper=0, wmin=1, seed=9104, op=.8))
    # подоконник
    s.append(shape(rrect(x0 - 36, y0 + h + 12, x0 + w + 36, y0 + h + 40, 6), "#f2ecdf", "", w=4.6, seed=9105))
    # штора слева, колышется
    sw = 8 * math.sin(t * 1.6)
    cur = [(x0 - 14, y0 - 24), (x0 + 70, y0 - 24), (x0 + 60 + sw, y0 + h * .35), (x0 + 84 + sw * 1.4, y0 + h * .75), (x0 + 50 + sw, y0 + h + 30),
           (x0 - 14, y0 + h + 30)]
    s.append(shape(cur, "#c9726a", blob([(x0 + 20, y0 - 20), (x0 + 70, y0 - 20), (x0 + 60 + sw, y0 + h * .35), (x0 + 84 + sw * 1.4, y0 + h * .75),
                                          (x0 + 50 + sw, y0 + h + 30), (x0 + 30, y0 + h + 30)], "#a4544e", .6), w=4.6, seed=9106))
    s.append(line([(x0 + 20, y0), (x0 + 24 + sw * .5, y0 + h * .5), (x0 + 22 + sw, y0 + h)], 2.4, "#8a403b", seed=9107, op=.8))
    return "".join(s)


def floor_lamp(t, x, top=560, flick=1.0):
    s = []
    s.append(blob(ellipse_pts(x, GY9 + 24, 80, 16, 14), "#2a1608", .35, blur(6)))
    s.append(line([(x, GY9 + 10), (x, top + 60)], 12, "#4a3a2e", taper=0, wmin=1, seed=9200))
    s.append(shape(ellipse_pts(x, GY9 + 8, 54, 14, 12), "#4a3a2e", "", w=4, seed=9201))
    sh = [(x - 66, top + 70), (x - 44, top), (x + 44, top), (x + 66, top + 70)]
    s.append(shape(sh, "#f5d98b", blob([(x + 10, top), (x + 44, top), (x + 66, top + 70), (x + 24, top + 70)], "#e7bf5e", .85), w=4.8, seed=9202))
    return "".join(s)


def lamp_glow(t, x, y, flick):
    g = rad_grad([(0, "#ffe9a8", .62 * flick), (.45, "#ffd980", .22 * flick), (1, "#ffd980", 0)], x, y, 620, 760)
    return f'<ellipse cx="{x}" cy="{y}" rx="620" ry="760" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def calendar_wall(t, sway, mark_u, glow_k, icon_p, cross_p, jolt):
    """Календарь: шапка, сетка клеток, зачёркнутые прошедшие дни, клетка дня рождения (светится) и красный круг."""
    cx, cy, s = CAL
    W_, H_ = 250, 290
    piv = (cx, cy - H_ / 2 * s + 6)
    o = []
    # тень на стене
    o.append(blob(rrect(cx - W_ / 2 * s + 18, cy - H_ / 2 * s + 24, cx + W_ / 2 * s + 18, cy + H_ / 2 * s + 24, 14), "#1c1622", .22, blur(10)))
    g = []
    inner = blob(rrect(-W_ / 2, -H_ / 2, W_ / 2, -H_ / 2 + 66), "#e0614e")
    inner += blob(rrect(-W_ / 2, -H_ / 2 + 60, W_ / 2, -H_ / 2 + 66), "#b84434", .9)
    # шапка: два цветка-значка вместо названия месяца
    inner += blob(ellipse_pts(-70, -H_ / 2 + 32, 14, 14, 12), "#fbe9a8") + blob(ellipse_pts(-70, -H_ / 2 + 32, 5, 5, 8), "#c9762c")
    inner += blob(ellipse_pts(60, -H_ / 2 + 32, 18, 18, 12), "#fbe9a8", .0)
    for k in range(7):
        x = -W_ / 2 + 22 + k * 34
        inner += blob(rect_pts_(x - 6, -H_ / 2 + 76, x + 8, -H_ / 2 + 84, 3), "#9aa0b0", .9)
    g.append(shape(rrect(-W_ / 2, -H_ / 2, W_ / 2, H_ / 2, 8), "#fffdf6", inner, w=5, seed=9300))
    # сетка клеток
    x0, y0 = -W_ / 2 + 7, -H_ / 2 + 94
    for r_ in range(6):
        g.append(line([(x0, y0 + r_ * 36 - 1), (x0 + 7 * 34 + 2, y0 + r_ * 36 - 1)], 1.8, "#b9bccb", taper=0, wmin=1, seed=9310 + r_, op=.9))
    for c_ in range(8):
        g.append(line([(x0 + c_ * 34, y0 - 1), (x0 + c_ * 34, y0 + 5 * 36 - 1)], 1.8, "#b9bccb", taper=0, wmin=1, seed=9320 + c_, op=.9))
    # штрихи-«числа» в клетках и зачёркнутые прошедшие дни
    for r_ in range(5):
        for c_ in range(7):
            px, py = -W_ / 2 + 24 + c_ * 34, -H_ / 2 + 108 + r_ * 36
            idx = r_ * 7 + c_
            if (c_, r_) == BDAY:
                continue
            g.append(blob(rect_pts_(px - 9, py - 3, px + 9, py + 3, 2), "#b4b8c6", .95))
            if idx < BDAY[1] * 7 + BDAY[0] - 1:      # прошедший день: крест маркером
                g.append(line([(px - 12, py - 12), (px + 12, py + 12)], 3.2, "#7e86a8", taper=.2, wmin=.6, seed=9400 + idx))
                g.append(line([(px + 12, py - 12), (px - 12, py + 12)], 3.2, "#7e86a8", taper=.2, wmin=.6, seed=9500 + idx))
    # вчерашний день: крест дорисовывается
    # клетка дня рождения
    bx, by = -W_ / 2 + 24 + BDAY[0] * 34, -H_ / 2 + 108 + BDAY[1] * 36
    if glow_k > 0:
        g.append(blob(rrect(bx - 16, by - 16, bx + 16, by + 16, 3), "#ffe27a", .35 + .55 * glow_k))
        g.append(blob(rrect(bx - 16, by - 16, bx + 16, by + 16, 3), "#fff6c4", .3 * glow_k * (.5 + .5 * math.sin(t * 14))))
    if icon_p > 0:
        ip = back_out(clamp(icon_p), 2.0)
        # подарочная коробочка-значок
        g.append(f'<g transform="translate({bx:.1f} {by + 2:.1f}) scale({ip:.3f})">'
                 + shape(rrect(-10, -3, 10, 12, 2), "#d9473a", blob(rrect(-3, -3, 3, 12), "#ffe27a", 1), w=2.2, seed=9600)
                 + shape(rrect(-12, -8, 12, -2, 2), "#e8604f", blob(rrect(-3, -8, 3, -2), "#ffe27a", 1), w=2.2, seed=9601)
                 + line([(0, -8), (-9, -16), (-4, -17), (0, -8)], 2.2, "#ffe27a", taper=0, wmin=1, seed=9602)
                 + line([(0, -8), (9, -16), (4, -17), (0, -8)], 2.2, "#ffe27a", taper=0, wmin=1, seed=9603) + "</g>")
    if cross_p > 0:       # сегодняшний день: крест
        px, py = -W_ / 2 + 24 + (BDAY[0] - 1) * 34, by
        g.append(line(partial([(px - 12, py - 12), (px + 12, py + 12)], clamp(cross_p * 2)), 3.4, "#7e86a8", taper=.2, wmin=.6, seed=9700))
        g.append(line(partial([(px + 12, py - 12), (px - 12, py + 12)], clamp(cross_p * 2 - 1)), 3.4, "#7e86a8", taper=.2, wmin=.6, seed=9701))
    # красный круг от руки (двойной проход, лёгкий перелёт)
    if mark_u > .02:
        n = 40
        a_ = np.linspace(0, 2 * math.pi * 1.12, n)
        ring = [(bx + (23 + 3 * a / 6) * math.cos(-1.9 + a) * 1.0, by + (21 + 2.4 * a / 6) * math.sin(-1.9 + a)) for a in a_]
        g.append(line(partial(ring, mark_u), 5.6, "#d6322c", taper=.12, wmin=.75, seed=9800))
        ring2 = [(bx + (26 - 2 * a / 6) * math.cos(-1.6 + a), by + (24 - 2 * a / 6) * math.sin(-1.6 + a)) for a in np.linspace(0, 2 * math.pi * .7, 20)]
        g.append(line(partial(ring2, clamp((mark_u - .75) / .25)), 4.4, "#d6322c", taper=.2, wmin=.7, seed=9801))
    # гвоздь и петля
    gg = "".join(g)
    rot = sway
    cal = (f'<g transform="translate({cx} {cy}) scale({s})">{gg}</g>')
    o.append(f'<g transform="rotate({rot:.3f} {piv[0]:.1f} {piv[1]:.1f}) translate({jolt[0]:.1f} {jolt[1]:.1f})">{cal}'
             + shape(ellipse_pts(piv[0], piv[1] - 4, 9, 9, 8), "#a0a4b4", "", w=3, seed=9900) + "</g>")
    o.append(blob(ellipse_pts(piv[0], piv[1] - 6, 8, 8, 8), "#6e7388"))
    return "".join(o), (bx, by)


def rect_pts_(x0, y0, x1, y1, r=0):
    return lib.rect_pts(x0, y0, x1, y1, r)


def frame09(t):
    t0 = 16.3
    # камера: тихий наезд, на «завтра» удар
    pre = clamp((t - t0) / (T_ZAV - t0))
    z = 1.10 + .16 * ease_io(pre) + .0
    hit = t - T_ZAV
    if hit > 0:
        z = 1.26 + .07 * (1 - math.exp(-hit * 9)) + .04 * clamp(hit / 0.9) - .05 * math.exp(-hit * 6) * math.cos(hit * 40)
    z += .05 * math.exp(-(t - t0) * 6)
    set_ink(z)
    shake = 16 * math.exp(-max(0.0, hit) * 7) * math.sin(max(0.0, hit) * 62) if hit > 0 else 0.0
    cxm = lerp(620, 600, ease_io(pre)) + (shake if hit > 0 else 0)
    cym = lerp(760, 730, ease_io(pre)) + (shake * .6 if hit > 0 else 0)
    cym += (-6 * math.sin(t * 3.0))
    roll = .9 * math.sin(t * 2.2) + (2.4 * math.exp(-hit * 6) * math.sin(hit * 30) if hit > 0 else 0)

    flick = .92 + .06 * math.sin(t * 9) + .03 * math.sin(t * 23)
    scn = [wall_night(t), night_window(t, 40, 340)]
    scn.append(floor_lamp(t, 1010, 640))
    scn.append(lamp_glow(t, 930, 700, flick))
    # свет луны на пол
    scn.append(f'<path d="M60 {GY9} L330 {GY9} L560 1700 L-60 1700 Z" fill="#c9d6ff" opacity=".10" style="mix-blend-mode:screen"/>')
    # календарь
    sway = 3.0 * math.sin(t * 2.6) * math.exp(-(t - t0) * .5) + 1.0 * math.sin(t * 1.7)
    if hit > 0:
        sway += 5.5 * math.exp(-hit * 4.2) * math.sin(hit * 26)
    glow_k = smooth(T_ROZH - .04, T_ROZH + .12, t) * (.75 + .25 * math.sin(t * 12)) if t > T_ROZH - .04 else 0.0
    glow_k *= (1 - .35 * smooth(T_ZAV, T_ZAV + .5, t))
    icon_p = (t - (T_ROZH + .02)) / .4
    cross_p = (t - (T_DEN + .02)) / .3
    mark_u = ease_io(clamp((t - T_ZAV) / .5))
    cal_svg, bcell = calendar_wall(t, sway, mark_u, clamp(glow_k) if glow_k > 0 else 0.0, icon_p, clamp(cross_p), (0, 0))
    scn.append(cal_svg)
    cell_w = (cx_ := bcell)  # noqa: F841
    # лучи и блёстки на клетке
    cwx, cwy = cal_cell(*BDAY)
    ray = clamp((t - T_ROZH) / .7)
    if 0 < ray < 1:
        scn.append(burst(cwx, cwy, ray, 12, 50, 170, 11, "#fff0a8", 9950, spread=360))
    for i, (dx, dy, tt) in enumerate(((-40, -50, .1), (46, -40, .22), (-30, 46, .34), (50, 50, .16))):
        scn.append(glint(cwx + dx * 1.4, cwy + dy * 1.4, clamp((t - T_ROZH - tt) / .7), 38 + 8 * i, "#fffbe0"))
    if hit > 0:
        scn.append(burst(cwx, cwy, clamp(hit / .4), 12, 60, 135, 9, "#d6322c", 9980, spread=360))
    # ── Дима
    scn.append(dima09(t))
    cam = lib.cam(cxm, cym, z, roll)
    return f'<g transform="{cam}">{"".join(scn)}</g>'


def dima09(t):
    bs = .72
    hip_y = GY9 - 610 * bs * .985
    run_a = T_A - .02
    stop_t = T_A + .62
    u = clamp((t - run_a) / (stop_t - run_a))
    x = -330 + (DIMA_X + 330) * (1 - (1 - u) ** 2.2)
    speed = 0.0 if u >= 1 else (1 - u) ** 1.2
    hit = t - T_ZAV
    pan = clamp(hit / .14) if hit > 0 else 0.0                  # паника: руки к голове
    tremor = 5 * math.sin(t * 55) * smooth(.0, .15, hit) * math.exp(-max(0, hit) * .6) if hit > 0 else 0.0
    # бег и торможение
    ph = 2 * math.pi * 3.4 * (t - run_a)
    mv = speed > .04
    bob = 14 * abs(math.sin(ph)) * bs * speed
    hip = (x, hip_y - bob)
    feet = {}
    stand = {"n": (hip[0] + 24 * bs, GY9 - 4), "f": (hip[0] - 26 * bs, GY9 - 4)}
    for sd, off in (("n", 0.0), ("f", math.pi)):
        p_ = ph + off
        run_ankle = (hip[0] + 190 * bs * math.sin(p_) * (.4 + .6 * speed), GY9 - 4 - max(0.0, math.cos(p_)) * 200 * bs * speed)
        a = (lerp(stand[sd][0], run_ankle[0], clamp(speed * 1.4)), lerp(stand[sd][1], run_ankle[1], clamp(speed * 1.4)))
        if u >= 1:
            a = stand[sd]
        feet[sd] = (a, -.2 * max(0.0, math.cos(p_)) * speed)
    lean = .22 * speed + .02 - (.05 * pan if hit > 0 else 0)
    # руки: бег → стоит → показывает на клетку → хватается за голову
    sh = (hip[0] + 10 * bs, hip[1] - 400 * bs)
    look_k = smooth(T_ROZH - .1, T_ROZH + .15, t)
    cx_c, cy_c = cal_cell(*BDAY)
    pt_dir = np.array([cx_c - sh[0], cy_c - sh[1]], float)
    pt_dir /= np.linalg.norm(pt_dir)
    swing = {"n": (hip[0] + 110 * bs + 230 * bs * math.sin(ph + math.pi), hip[1] - 230 * bs - 70 * bs * math.cos(ph)),
             "f": (hip[0] + 110 * bs + 230 * bs * math.sin(ph), hip[1] - 230 * bs + 70 * bs * math.cos(ph))}
    hang = {"n": (hip[0] + 60 * bs, hip[1] + 330 * bs), "f": (hip[0] + 30 * bs, hip[1] + 340 * bs)}
    if u < 1:
        tgt = {k: tuple(lerp(hang[k][i], swing[k][i], clamp(speed * 1.6)) for i in (0, 1)) for k in "nf"}
    else:
        tgt = dict(hang)
    # указывает на клетку на «рождения»
    point_k = smooth(T_ROZH - .05, T_ROZH + .25, t) * (1 - smooth(T_ZAV - .05, T_ZAV + .05, t))
    reach = 330 * bs * 1.0
    ptgt = (sh[0] + pt_dir[0] * reach * 1.45, sh[1] + pt_dir[1] * reach * 1.45)
    tgt["n"] = tuple(lerp(tgt["n"][i], ptgt[i], point_k) for i in (0, 1))
    hpos = (hip[0] + 54 * bs, hip[1] - 548 * bs)
    hh = {"n": (hpos[0] + 40 * bs, hpos[1] - 150 * bs - 5 * math.sin(t * 40) * pan), "f": (hpos[0] - 70 * bs, hpos[1] - 110 * bs)}
    tgt["n"] = tuple(lerp(tgt["n"][i], hh["n"][i], pan) for i in (0, 1))
    tgt["f"] = tuple(lerp(tgt["f"][i], hh["f"][i], pan) for i in (0, 1))
    arms = {"n": ("ik", tgt["n"], -1), "f": ("ik", tgt["f"], -1)}
    runh = open_hand(.7, (1, -.1), .05, .7)
    pointh = dict(kind="open", flip=1, dir=(pt_dir[0], pt_dir[1]), curl=(0, .95, .95, .95), spread=.05, thumb=.6, bend=.05, k=1.0)
    grabh = open_hand(.62, (.15, -1), .3, .3)
    hands = {"n": runh if u < 1 and point_k < .3 and pan < .3 else (grabh if pan > .3 else pointh if point_k > .3 else open_hand(.3, (0, 1), .1, .3)),
             "f": grabh if pan > .3 else (runh if u < 1 else open_hand(.25, (0, 1), .1, .3, flip=-1))}
    if pan > .3:
        hands["f"] = dict(grabh, flip=-1, dir=(.1, -1))
    # лицо
    wob = bump(t, T_ZAV, .5)
    st1 = 1.0 if t < T_ROZH else 0.0
    if t < T_A + .6:       # бежит, запыхался
        exp = dict(lid=.9, look=(.9, 0.0), brows="det", mouth="talk", open=.5, smile=0, closed=0, hair=6 * math.sin(t * 30) * speed, flush=.3 * speed)
    elif t < T_ROZH:
        exp = dict(lid=.85, look=(.55, -.5), brows="up", mouth="talk", open=.15, smile=.4, closed=blink_of(t, (17.3,)))
    elif t < T_ZAV - .45:      # свет клетки: радость, потом тень сомнения
        exp = dict(lid=1.0, look=(.75, -.4), brows="up", mouth="smile", smile=1.0, closed=0)
    elif t < T_ZAV:
        k = smooth(T_ZAV - .45, T_ZAV, t)
        exp = dict(lid=1.0, look=(.7, -.3), brows=("up", "worry", k), mouth="talk", open=.15 + .4 * k, smile=.6 * (1 - k), closed=0)
    else:
        exp = dict(lid=1.0, look=(.5 + .4 * math.sin(t * 20), -.2 * pan), brows="worry", mouth="talk", open=.95, smile=0,
                   hair=16 * math.exp(-hit * 3.0) * math.sin(hit * 38) + 6 + tremor * .3, closed=0, flush=smooth(0, .4, hit) * .55)
    ha = -.12 * pan * 1.0 + (.03 * math.sin(t * 50) * pan if hit > 0 else 0)
    hood = 14 * math.sin(t * 30) * speed
    d = dima((hip[0] + tremor, hip[1]), bs, lean, arms, hands, exp, feet=feet, head_ang=ha, hood=hood)
    o = []
    # тень на полу
    o.append(blob(ellipse_pts(hip[0], GY9 + 14, 150 * bs / .62, 14, 14), "#2a1608", .38))
    o.append(d.get("legs", "") + d["arm_f"] + d["body"] + d["arm_n"])
    # пот и «шок»
    if hit > 0:
        for i in range(5):
            per = .55 + .06 * i
            ph_ = ((t + i * .13) % per) / per
            hx_, hy_ = d["head"][0], d["head"][1]
            sx = hx_ + (120 + 22 * i) * (1 if i % 2 else -1) * (.7 + ph_ * .5)
            sy = hy_ - 30 + 150 * ph_ * ph_ - 40 * (i % 3)
            o.append(drop(sx, sy, 15 * (1 - .3 * ph_), 70 + i))
        for i, a in enumerate((-70, -40, -10, 20, 50)):
            if hit < .6:
                ar = math.radians(a - 90 + 60)
                r0 = 190 + 12 * math.sin(t * 40 + i)
                hx_, hy_ = d["head"]
                p0 = (hx_ + r0 * math.cos(ar - 1.0), hy_ + r0 * math.sin(ar - 1.0))
                p1 = (hx_ + (r0 + 70) * math.cos(ar - 1.0), hy_ + (r0 + 70) * math.sin(ar - 1.0))
                o.append(line([p0, p1], 8, "#2a1608", taper=.5, wmin=.2, seed=9990 + i, op=.9 * (1 - hit / .6)))
    return "".join(o)


def frame(sid, t):
    lib.dyn_begin()
    body = {"s09": frame09, "s10": frame10}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#9aa6c4"/>{body}')


def frame10(t):
    return ""
