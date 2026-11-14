"""Рилс 59 «подарок», группа D: s09 (календарь без цифр, ночь) и s10 (цветочный ларёк). frame(sid, t) -> SVG 1080×1920,
t — общее время ролика. Герои — people.py/hand.py (Дима и остальные рилсов 55–57); продавщица — people.PAL['seller'] (свой цвет, причёска, фартук)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)           # lib/ink/hand/people/props — общие файлы рилса 59 (группы A, B), своих копий нет
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
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
        z = 1.26 + .08 * (1 - math.exp(-hit * 9)) + .13 * ease_io(clamp(hit / 0.95)) - .05 * math.exp(-hit * 6) * math.cos(hit * 40)
    z += .05 * math.exp(-(t - t0) * 6)
    set_ink(z)
    shake = 16 * math.exp(-max(0.0, hit) * 7) * math.sin(max(0.0, hit) * 62) if hit > 0 else 0.0
    cxm = lerp(620, 600, ease_io(pre)) + 40 * ease_io(clamp(hit / .95)) + (shake if hit > 0 else 0)
    cym = lerp(760, 730, ease_io(pre)) + 40 * ease_io(clamp(hit / .95)) + (shake * .6 if hit > 0 else 0)
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
    idle = 4 * math.sin(t * 5.0) * (1 - speed) * (1 - pan)
    hip = (x, hip_y - bob + idle * .5)
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
    ha = .03 * math.sin(t * 3.1) * (1 - pan) - .12 * pan * 1.0 + (.03 * math.sin(t * 50) * pan if hit > 0 else 0)
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




# ═════════════════════════════ продавщица: свой цвет, голова, фартук (общий people.py её не знает) ═════════════════════════════
people.PAL["seller"] = dict(SKIN="#e9bf9d", SKIN_SH="#d09f7e", SKIN_SH2="#b9866a", HAIR="#2b1d27", HAIR_SH="#18101a", HAIR_HI="#5a3f52",
                            TOP="#f2b8c6", TOP_SH="#d98fa4", TOP_SH2="#b96d85", FOLD="#8f4a62", STITCH="#fff3f6", TEE="#fff7f0", TEE_SH="#e6d9cc",
                            APRON="#4f9a6a", APRON_SH="#357a50", APRON_HI="#7fc08f",
                            LEGS="#3d4558", LEGS_SH="#2c3342", LEGS_SEAM="#5d6780", SHOE="#7a4a2a", SHOE_SH="#5a341c", SOLE="#3b2c22", SOLE_SH="#2a1f18",
                            STRIPE="#a76a3e", NAIL="#f6dccd")
people.FRIENDLIKE = tuple(people.FRIENDLIKE) + ("seller",)
_orig_head = people.person_head
_orig_jacket = people.jacket_parts


def seller_head(expr):
    """Молодая женщина: чёрные волосы, пучок, жёлтая повязка, красные губы, ресницы, серёжка, румянец (3/4 вправо, как у остальных)."""
    C = people.C
    P_ = people
    hb = expr.get("hair", 0.0)
    s = []
    # пучок сзади сверху
    s.append(shape(ellipse_pts(-70, -176, 56, 50, 16), C["HAIR"], blob(ellipse_pts(-52, -164, 26, 22, 10), C["HAIR_HI"], .8) +
                   line([(-96, -190), (-60, -214)], 2.4, C["HAIR_SH"], seed=1301, op=.9) + line([(-84, -150), (-44, -200)], 2.4, C["HAIR_SH"], seed=1302, op=.9),
                   w=5.0, seed=1300))
    ear = [(-86, -26), (-112, -38), (-132, -14), (-130, 22), (-116, 48), (-94, 52), (-84, 40)]
    s.append(shape(ear, C["SKIN"], blob([(-132, -14), (-130, 22), (-116, 48), (-116, 10)], C["SKIN_SH"], .9), w=4.8, seed=1303))
    s.append(line([(-98, 32), (-118, 20), (-116, -8), (-102, -18)], 3.2, seed=1304))
    s.append('<circle cx="-112" cy="58" r="8" fill="#e0b440"/><circle cx="-114" cy="56" r="2.4" fill="#fff2b8"/>')
    inner = [blob([(-120, -210), (-40, -210), (-60, -40), (-56, 40), (-30, 160), (-120, 160)], C["SKIN_SH"], .95),
             blob(ellipse_pts(56, -16, 100, 60, 14), "#e5a99a", .3),
             blob(ellipse_pts(100, 38, 24, 13, 10), "#ec8a88", .55), blob(ellipse_pts(8, 44, 30, 14, 10), "#ec8a88", .5)]
    fl = expr.get("flush", 0.0)
    if fl > .01:
        inner.append(blob(ellipse_pts(30, 20, 140, 120, 16), "#e2493c", .3 * fl))
    s.append(shape(P_.FACE_G, C["SKIN"], "".join(inner), w=5.6, seed=1305))
    s.append(P_._nose())
    s.append(P_._mouth_gen(expr, "#c4303f", seed=1306))
    s.append(P_.eyes(expr, P_.F_EYE_N, P_.F_EYE_F, bags=False))
    for (cx_, cy_, rx_, sd_) in ((18, -22, 44, 1320), (90, -20, 34, 1324)):
        s.append(line([(cx_ + rx_ * .55, cy_ - 38), (cx_ + rx_ * 1.0, cy_ - 56)], 3.4, seed=sd_, taper=.3, wmin=.5))
        s.append(line([(cx_ + rx_ * .25, cy_ - 44), (cx_ + rx_ * .55, cy_ - 64)], 3.0, seed=sd_ + 1, taper=.3, wmin=.5))
    s.append(P_._brows(expr, C["HAIR_SH"], .8))
    # волосы: гладкая шапка с пробором и локоном на висок
    hair = P_._bounce(P_.SM_HAIR, hb * .5)
    hi = blob(P_._bounce([(-140, -200), (-30, -200), (-40, -130), (-80, -100), (-90, -40), (-140, -20)], hb * .5), C["HAIR_SH"], .9)
    hi += blob(P_._bounce([(0, -160), (60, -136), (96, -100), (60, -120), (30, -140)], hb * .5), C["HAIR_HI"], .75)
    hi += line([(-20, -150), (-60, -120), (-96, -80)], 3.0, C["HAIR_SH"], seed=1330, op=.85)
    s.append(shape(hair, C["HAIR"], hi, w=5.4, seed=1331))
    s.append(shape([(100, -90), (62, -118), (8, -124), (-26, -110), (-14, -90), (30, -98), (70, -80), (104, -56), (98, -30), (86, -62)], C["HAIR"],
                   line([(60, -112), (10, -112)], 2.6, C["HAIR_SH"], seed=1332, op=.9), w=4.4, seed=1333))
    # жёлтая повязка
    band_ = [(-110, -112), (-60, -132), (20, -146), (80, -128), (112, -100), (110, -80), (74, -104), (20, -122), (-60, -108), (-114, -90)]
    s.append(shape(band_, "#f3c23b", line([(-60, -122), (20, -134), (80, -116)], 2.0, "#c99a1e", seed=1340, op=.8), w=4.0, seed=1341))
    s.append(shape([(-100, -112), (-130, -96), (-140, -60), (-118, -84), (-110, -62), (-94, -98)], "#f3c23b", "", w=3.6, seed=1342))
    return "".join(s)


def seller_body():
    C = people.C
    body = [(-112, 34), (-120, -40), (-132, -170), (-128, -280), (-112, -360), (-78, -410), (-20, -432), (40, -426), (84, -398), (112, -330), (126, -230),
            (124, -120), (116, -20), (110, 34)]
    inner = blob([(30, -440), (130, -380), (140, 40), (60, 40), (80, -200)], C["TOP_SH"], .85)
    inner += blob([(-140, -300), (-100, -320), (-104, -100), (-140, -60)], C["TOP_SH"], .55)
    torso = shape(body, C["TOP"], inner, w=5.2, seed=1400)
    ap = [(-50, -330), (30, -360), (96, -340), (120, -230), (120, -120), (116, -20), (112, 40), (-110, 40), (-106, -80), (-84, -230)]
    ai = blob([(40, -350), (120, -240), (122, 40), (60, 40), (66, -210)], C["APRON_SH"], .85)
    ai += blob([(-100, -100), (-60, -240), (-40, -300), (-110, -300)], C["APRON_SH"], .5)
    ai += line([(-70, -300), (-84, -200), (-90, -90)], 2.0, C["APRON_SH"], seed=1410, op=.8)
    ai += shape([(10, -150), (86, -158), (108, -128), (110, -40), (10, -36)], C["APRON"], blob([(60, -150), (110, -128), (110, -40), (60, -40)], C["APRON_SH"], .8), w=3.4, seed=1411)
    ai += line([(18, -138), (92, -146)], 2.0, C["APRON_HI"], seed=1412, op=.9)
    # цветочек-нашивка на кармане без букв
    for k, a in enumerate(range(0, 360, 72)):
        ai += blob(ellipse_pts(58 + 12 * math.cos(math.radians(a)), -92 + 12 * math.sin(math.radians(a)), 8, 8, 8), "#fff3f6")
    ai += blob(ellipse_pts(58, -92, 6, 6, 8), "#f3c23b")
    torso += shape(ap, C["APRON"], ai, w=4.8, seed=1415)
    torso += line([(-96, 4), (110, 4)], 2.4, C["APRON_SH"], seed=1416, op=.9)
    # завязки фартука на спине
    torso += shape([(-112, -50), (-160, -76), (-176, -40), (-130, -36)], C["APRON"], "", w=3.8, seed=1417)
    torso += shape([(-112, -50), (-150, -10), (-130, 40), (-110, -22)], C["APRON"], "", w=3.8, seed=1418)
    col = [(-60, -440), (-20, -462), (40, -452), (72, -420), (52, -396), (20, -420), (-30, -424), (-70, -410)]
    back = shape(col, C["TEE"], line([(-50, -430), (30, -436)], 1.8, C["TEE_SH"], seed=1419, op=.8), w=4.0, seed=1420)
    # лямка фартука на шее
    torso += line([(54, -366), (6, -440)], 18, C["APRON"], taper=0, wmin=1, seed=1421)
    torso += line([(54, -366), (6, -440)], 3, C["APRON_SH"], taper=0, wmin=1, seed=1422, op=.8)
    return back, torso, ""


def _ph(expr, style):
    if style == "seller":
        return seller_head(expr)
    return _orig_head(expr, style)


def _jk(*a, **k):
    if people.C.get("APRON"):
        return seller_body()
    return _orig_jacket(*a, **k)


people.person_head = _ph
people.jacket_parts = _jk
people.NEWHEADS = tuple(people.NEWHEADS) + ("seller",)


# ═════════════════════════════ s10 19.04–20.64: цветочный ларёк ═════════════════════════════
GY10 = 1300
T_KUPIL = find("купил", 19.0)          # 19.82
T_CVETY = find("цветы", 19.0)          # 20.16
T10_0 = 18.84
BS_D, BS_S = .78, .70
SELL_X = 780
GK = 1.2                                # масштаб букета (1 = Дима BS 0.6)


def heart(cx, cy, r, col="#e0527a", sd=0, rot=0.0):
    pts = [(0, -.35), (.45, -.95, 0), (1, -.7), (1.05, -.1), (.5, .5), (0, 1.0, 1), (-.5, .5), (-1.05, -.1), (-1, -.7), (-.45, -.95)]
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    P_ = [(cx + r * (x * c - y * sn), cy + r * (x * sn + y * c)) + ((1,) if len(p) > 2 and p[2] else ()) for p in pts for x, y in [(p[0], p[1])]]
    return shape(P_, col, blob(ellipse_pts(cx + r * .2, cy + r * .1, r * .5, r * .4, 8), "#b8304f", .6), w=3.0, seed=sd)


def building(x0, x1, top, bottom, col, sh, rows, cols, sd, awning=None):
    s = [shape(rrect(x0, top, x1, bottom, 4), col, blob(rrect(x1 - (x1 - x0) * .3, top, x1, bottom), sh, .8), w=4.0, seed=sd)]
    ww = (x1 - x0) / (cols + 1)
    hh = (bottom - top - 160) / (rows + 1)
    for r in range(rows):
        for c in range(cols):
            wx = x0 + ww * (c + .6)
            wy = top + 50 + hh * (r + .15) + r * hh * .2
            s.append(shape(rrect(wx, wy, wx + ww * .6, wy + hh * .7, 3), "#e9f4fb", blob(rrect(wx + 4, wy + 4, wx + ww * .3, wy + hh * .4), "#ffffff", .6) +
                           line([(wx + ww * .3, wy), (wx + ww * .3, wy + hh * .7)], 3, INK, taper=0, wmin=1, seed=sd + 7 * r + c), w=3.2, seed=sd + 11 * r + c))
    return "".join(s)


def street_bg(t):
    s = []
    g = lib.lin_grad([(0, "#9fd3ee", 1), (.7, "#d7edf5", 1), (1, "#f3f3e6", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-300" y="-300" width="1700" height="{GY10 + 300}" fill="url(#{g})"/>')
    s.append(blob(ellipse_pts(220 + 12 * math.sin(t * .6), 380, 120, 36, 14), "#ffffff", .95) + blob(ellipse_pts(300 + 12 * math.sin(t * .6), 360, 80, 30, 14), "#ffffff", .95))
    s.append(building(-200, 330, 330, GY10 - 40, "#efd0a6", "#d8b583", 3, 3, 10400))
    s.append(building(1000, 1360, 260, GY10 - 40, "#c9dcb0", "#a9c492", 4, 3, 10500))
    # дерево на заднем плане
    s.append(line([(-40, GY10 - 40), (-30, 780)], 30, "#8a5c3a", taper=0, wmin=1, seed=10600))
    # тротуар и бордюр
    s.append(f'<rect x="-300" y="{GY10 - 40}" width="1700" height="900" fill="#d9cdb8"/>')
    s.append(blob(rrect(-300, GY10 - 40, 1400, GY10 + 12), "#ece4d4"))
    s.append(line([(-300, GY10 - 40), (1400, GY10 - 40)], 4, INK, taper=.02, wmin=1, seed=10601))
    s.append(line([(-300, GY10 + 12), (1400, GY10 + 12)], 3, "#a39577", taper=.02, wmin=1, seed=10602))
    for k in range(1, 7):
        y = GY10 + 12 + k * 74 + k * k * 4
        s.append(line([(-300, y), (1400, y + 3)], 2.6, "#a39577", taper=.05, wmin=.9, seed=10610 + k, op=.6))
    for xx in range(-300, 1400, 260):
        for k in range(0, 6):
            y = GY10 + 12 + k * 74 + k * k * 4
            s.append(line([(xx + (k % 2) * 130 + k * 14, y), (xx + (k % 2) * 130 + k * 22, y + 80 + k * 6)], 2.2, "#a39577", taper=.05, wmin=.9, seed=10630 + k, op=.5))
    return "".join(s)


def stall_back(t):
    s = []
    x0, x1, y0 = 430, 1180, 250
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{GY10 - y0 - 330}" fill="#3d8a82"/>')
    for x in range(x0 + 50, x1, 100):
        s.append(line([(x, y0), (x, 970)], 3, "#2d6e68", taper=0, wmin=1, seed=10700 + x, op=.8))
    s.append(line([(x0, y0), (x0, 970)], 6, INK, taper=0, wmin=1, seed=10701))
    # полки с горшками (слева и справа, у лица продавщицы пусто)
    for (ys, sd) in ((560, 10710), (760, 10720)):
        s.append(shape(rrect(x0 + 4, ys, x1, ys + 22, 3), "#d9b680", "", w=3.8, seed=sd))
    for (px, py, sd) in ((500, 560, 1), (580, 560, 2), (1000, 560, 3), (1090, 560, 4)):
        s.append(pot(px, py, sd))
    s.append(PR.jar_flowers(1060, 760, 1.2, 3))
    s.append(PR.jar_flowers(500, 760, 1.2, 4))
    return "".join(s)


def pot(x, y, sd):
    col = ["#d9654f", "#e8b24a", "#7fb6c9", "#d98fb0"][sd % 4]
    s = []
    for j, (dx, h, dr) in enumerate(((-16, 76, -18), (0, 96, 0), (16, 70, 20))):
        s.append(line([(x, y - 30), (x + dx, y - h)], 4.0, "#43803F", taper=.2, wmin=.8, seed=10800 + sd * 5 + j))
        s.append(PR._leaf(x + dx, y - h, x + dx + 26 * (1 if dx >= 0 else -1), y - h - 18, 11, "#5FA05B", 10810 + sd * 7 + j))
    s.append(shape([(x - 28, y - 34, 1), (x + 28, y - 34, 1), (x + 22, y, 1), (x - 22, y, 1)], col, blob([(x + 4, y - 34), (x + 28, y - 34), (x + 22, y), (x + 2, y)], PR.mix(col, "#000000", .25), .6), w=3.6, seed=10820 + sd))
    return "".join(s)


def awning(t):
    x0, x1, y0, y1 = 400, 1160, 110, 262
    n = 10
    wd = (x1 - x0) / n
    s = []
    sw = 4 * math.sin(t * 2.3)
    for i in range(n):
        xa, xb = x0 + i * wd, x0 + (i + 1) * wd
        col = "#e05a4f" if i % 2 == 0 else "#fff3e6"
        wave = sw * math.sin(i * .9 + t * 3)
        pts = [(xa, y0, 1), (xb, y0, 1), (xb, y1 + wave, 1), ((xa + xb) / 2, y1 + 40 + wave * 1.4), (xa, y1 + wave, 1)]
        s.append(shape(pts, col, blob([((xa + xb) / 2, y0), (xb, y0), (xb, y1 + wave), ((xa + xb) / 2, y1 + 40 + wave * 1.4)], PR.mix(col, "#000000", .12), .55), w=3.6, seed=10900 + i))
    s.append(line([(x0, y0), (x1, y0)], 6, INK, taper=0, wmin=1, seed=10930))
    s.append(line([(x0 + 10, y1 + 70), (x0 + 6, 940)], 12, "#8a5c3a", taper=0, wmin=1, seed=10931))
    return "".join(s)


def hanging_sign(t):
    px, py = 940, 300
    ang = 7 * math.sin(t * 2.0)
    s = line([(px - 40, py), (px - 30, py + 70)], 3, INK, taper=0, wmin=1, seed=10950) + line([(px + 40, py), (px + 30, py + 70)], 3, INK, taper=0, wmin=1, seed=10951)
    board = shape(ellipse_pts(px, py + 130, 74, 66, 16), "#f4d88a", blob(ellipse_pts(px + 14, py + 146, 60, 48, 12), "#e0b858", .6), w=4.6, seed=10952)
    board += PR._daisy(px, py + 130, 34, 12, 10960)
    board += PR._leaf(px - 6, py + 164, px - 40, py + 150, 9, "#5FA05B", 10970) + PR._leaf(px + 6, py + 164, px + 40, py + 150, 9, "#5FA05B", 10972)
    return f'<g transform="rotate({ang:.2f} {px} {py})">{s}{board}</g>'


def counter(t):
    s = []
    x0, x1 = 440, 1200
    top = 936
    s.append(blob(ellipse_pts((x0 + x1) / 2, GY10 + 18, 400, 18, 16), "#2a1608", .3))
    front = shape(rrect(x0, top + 24, x1, GY10, 4), "#e8b24a", "", w=4.8, seed=11000)
    for k in range(1, 8):
        front += line([(x0 + k * 100, top + 30), (x0 + k * 100, GY10 - 4)], 2.8, "#c9922c", taper=0, wmin=1, seed=11010 + k, op=.85)
    s.append(front)
    s.append(shape(rrect(x0, 1100, x1, 1140, 2), "#ffffff", "", w=3.0, seed=11020, ink=False) if False else "")
    s.append(PR._daisy(830, 1120, 60, 8, 11030))
    for sd, (dx, dy, a) in enumerate(((-62, 40, 28), (60, 40, -28), (0, 70, 0))):
        s.append(PR._leaf(830 + dx * .2, 1150, 830 + dx * 1.5, 1150 + dy * .5, 14, "#5FA05B", 11040 + sd * 3))
    s.append(shape(rrect(x0 - 10, top, x1 + 10, top + 30, 5), "#c8915a", blob(rrect(x0 - 10, top + 14, x1 + 10, top + 30), "#a8703c", .7), w=4.8, seed=11060))
    return "".join(s)


def bucket_flowers(x, y, kind, t, sd, k=1.0):
    """Ведро (дно в (x, y)) с цветами: kind 0 — ромашки, 1 — тюльпаны."""
    s = []
    rs = np.random.RandomState(sd)
    n = 7
    for i in range(n):
        u = i / (n - 1) * 2 - 1
        sw = 3 * math.sin(t * 1.7 + i + sd)
        hx = x + u * 56 * k + sw
        hy = y - (150 + 40 * rs.uniform() - 28 * abs(u)) * k
        s.append(line([(x + u * 16 * k, y - 60 * k), (hx, hy + 16 * k)], 4.0, "#43803F", taper=.2, wmin=.8, seed=sd * 100 + i))
        if (i % 3 == 1) and kind == 0:
            s.append(PR._leaf(x + u * 16 * k, y - 80 * k, hx + 24, hy + 40 * k, 8, "#5FA05B", sd * 100 + 20 + i))
        s.append(PR._daisy(hx, hy, 24 * k, 20 * i, sd * 100 + 40 + i) if kind == 0 else PR._tulip(hx, hy, 23 * k, 8 * u, sd * 100 + 40 + i))
    s.append(shape([(x - 44 * k, y - 82 * k, 1), (x + 44 * k, y - 82 * k, 1), (x + 36 * k, y, 1), (x - 36 * k, y, 1)], PR.C_TIN if hasattr(PR, "C_TIN") else "#8D8F94",
                   blob([(x + 6 * k, y - 82 * k), (x + 44 * k, y - 82 * k), (x + 36 * k, y), (x + 4 * k, y)], "#6E7075", .8) +
                   line([(x - 40 * k, y - 62 * k), (x + 40 * k, y - 62 * k)], 2.6, "#6E7075", seed=sd + 5, op=.9), w=3.8, seed=sd + 7))
    return "".join(s)


def person(who, x, bs, y_hip, lean, arms, hands, expr, feet, head_ang=0.0, flip=False, hood=0.0, strings=(0, 0)):
    """Рисует героя слоями; flip — зеркально вокруг x (цели рук в arms уже в зеркальной системе). wrist/head — в мире."""
    pose = dict(hip=(x, y_hip), scale=bs, lean=lean, feet=feet, arms=arms, hands=hands, head_ang=head_ang, expr=expr, torso_k=1.0, hood=hood,
                strings=strings, head_off=(0, 0))
    o = people.draw(pose, who)
    L = {k: o[k] for k in ("legs", "pelvis", "arm_f", "body", "arm_n") if k in o}
    wr = {k: tuple(map(float, v)) for k, v in o["wrist"].items()}
    hd = tuple(map(float, o["head"]))
    if flip:
        L = {k: f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{v}</g>' for k, v in L.items()}
        wr = {k: (2 * x - v[0], v[1]) for k, v in wr.items()}
        hd = (2 * x - hd[0], hd[1])
    return L, wr, hd


NO_HAND = dict(kind="none")


def bouquet_pos(t):
    """Центр захвата букета (мир): у продавщицы → к Диме → к его груди."""
    a = (700.0, 800.0)
    b = (548.0, 808.0)
    c = (372.0, 748.0)
    uB = ease_io(clamp((t - 19.70) / .32))
    uC = back_out(clamp((t - 20.12) / .34), 1.1) if t > 20.12 else 0.0
    x = lerp(lerp(a[0], b[0], uB), c[0], uC)
    y = lerp(lerp(a[1], b[1], uB), c[1], uC)
    return x, y, uB, uC


def frame10(t):
    z0 = clamp((t - T10_0) / 2.0)
    hitC = t - T_CVETY
    z = 1.04 + .14 * ease_io(z0) + (.03 * (1 - math.exp(-hitC * 10)) * math.exp(-hitC * 2) if hitC > 0 else 0)
    set_ink(z)
    shake = 7 * math.exp(-max(0.0, hitC) * 9) * math.sin(max(0.0, hitC) * 55) if hitC > 0 else 0.0
    cxm = lerp(560, 520, ease_io(z0)) + shake
    cym = lerp(820, 790, ease_io(z0)) + shake * .5
    roll = .8 * math.sin(t * 2.0) + (1.6 * math.exp(-hitC * 7) * math.sin(hitC * 28) if hitC > 0 else 0)

    scn = [street_bg(t), stall_back(t)]
    bx, by, uB, uC = bouquet_pos(t)
    R = 34 * GK
    gk_d, gk_s = BS_D, BS_S
    sway = 1.5 * math.sin(t * 3.1)
    # ── продавщица (смотрит влево)
    hip_s = GY10 - 610 * BS_S * .985
    s_hold = 1 - smooth(20.0, 20.16, t)
    Rw = R + 60 * gk_s
    wr_hold = (bx + Rw, by)
    rest_n = (SELL_X - 60 * BS_S, hip_s + 50)
    wr_n = tuple(lerp(rest_n[i], wr_hold[i], s_hold) for i in (0, 1))
    # дальняя рука поправляет букет, потом на прилавке
    tie = math.sin(t * 9) * (1 - smooth(19.6, 19.8, t))
    far_t = (lerp(SELL_X - 20 * BS_S, bx + 20, smooth(18.8, 18.95, t) * (1 - smooth(19.7, 19.95, t))) + 8 * tie, lerp(hip_s + 80, by - 60, smooth(18.8, 18.95, t) * (1 - smooth(19.7, 19.95, t))) + 10 * tie)
    mir = lambda p: (2 * SELL_X - p[0], p[1])  # noqa: E731
    exp_s = dict(lid=1.0, look=(.4, .1), closed=blink_of(t, (19.3, 20.5)), brows="up", mouth="talk", open=.3 + .25 * abs(math.sin(t * 9)) * (1 - smooth(19.7, 19.95, t)), smile=.9,
                 hair=3 * math.sin(t * 4))
    if t > T_CVETY:
        exp_s = dict(lid=1.0, look=(.3, .0), closed=blink_of(t, (20.5,)), brows="up", mouth="grin", open=.4, smile=1.0)
    S_, Sw, Sh = person("seller", SELL_X, BS_S, hip_s, -.03 + .03 * smooth(19.6, 19.85, t),
                        {"n": ("ik", mir(wr_n), -1), "f": ("ik", mir(far_t), -1)}, {"n": NO_HAND, "f": open_hand(.5, (1, 0), .15, .4, flip=1)}, exp_s, None,
                        head_ang=.03 * math.sin(t * 2.4) - .04 * smooth(19.7, 19.9, t), flip=True)
    scn.append(S_.get("pelvis", "") + S_["arm_f"] + S_["body"])
    scn.append(counter(t))
    scn.append(awning(t) + hanging_sign(t))
    scn.append(bucket_flowers(1090, 936, 0, t, 3, 1.15))
    scn.append(bucket_flowers(960, 936, 1, t, 4, 1.0))
    # ведра на земле перед прилавком
    scn.append(bucket_flowers(640, GY10 - 14, 1, t, 5, 1.1) + bucket_flowers(790, GY10 - 8, 0, t, 6, 1.25) + bucket_flowers(960, GY10 - 14, 1, t, 7, 1.1))
    # ── Дима
    walk = clamp((t - T10_0) / .78)
    x_d = -80 + (230 + 80) * ease_io(walk)
    speed = (1 - walk) ** .5 if walk < 1 else 0.0
    sp = max(speed, .0) if walk < 1 else 0.0
    hip_y = GY10 - 610 * BS_D * .985
    ph = 2 * math.pi * 2.2 * (t - T10_0)
    amp = clamp(sp * 1.5)
    hip = (x_d, hip_y - 8 * abs(math.sin(ph)) * BS_D * amp)
    feet = {}
    for sd, off in (("n", 0.0), ("f", math.pi)):
        p_ = ph + off
        stand = (x_d + (26 if sd == "n" else -26) * BS_D, GY10 - 4)
        wk = (hip[0] + 150 * BS_D * math.sin(p_), GY10 - 4 - max(0.0, math.cos(p_)) * 130 * BS_D)
        a = (lerp(stand[0], wk[0], amp), lerp(stand[1], wk[1], amp))
        feet[sd] = (a, -.18 * max(0.0, math.cos(p_)) * amp)
    D_hold = smooth(19.96, 20.06, t)
    reach = smooth(19.70, 19.94, t)
    Rd = R + 60 * gk_d
    wr_d = (bx - Rd, by)
    hang = (hip[0] + 60 * BS_D, hip[1] + 300 * BS_D)
    sw_ = (hip[0] + 90 * BS_D * math.sin(ph + math.pi) * amp + 60 * BS_D, hip[1] + 280 * BS_D - 40 * BS_D * math.cos(ph) * amp)
    base_n = tuple(lerp(hang[i], sw_[i], amp) for i in (0, 1))
    tgt_n = tuple(lerp(base_n[i], wr_d[i], reach) for i in (0, 1))
    base_f = (hip[0] + 30 * BS_D + 90 * BS_D * math.sin(ph) * amp, hip[1] + 290 * BS_D)
    tgt_f = tuple(lerp(base_f[i], (bx + 20, by - 20)[i], smooth(20.14, 20.36, t)) for i in (0, 1))
    exp_d = dict(lid=.9, look=(.7, .0), closed=blink_of(t, (19.5,)), brows="calm", mouth="smile", smile=.4, flush=0.0)
    if t > T_KUPIL - .1:
        k = smooth(T_KUPIL - .1, T_KUPIL + .2, t)
        exp_d = dict(lid=1.0, look=(.8, -.1), brows=("calm", "up", k), mouth="smile", smile=.4 + .6 * k, closed=0)
    if t > T_CVETY:
        k = smooth(T_CVETY, T_CVETY + .2, t)
        exp_d = dict(lid=1.0, look=(.5, .1), brows="up", mouth="grin", open=.5, smile=1.0, blush=k, laugh=.3 * k, closed=blink_of(t, (20.45,)), hair=6 * math.exp(-hitC * 4) * math.sin(hitC * 30))
    D_, Dw, Dh = person("dima", x_d, BS_D, hip[1], .06 * amp + .02 - .05 * uC, {"n": ("ik", tgt_n, -1), "f": ("ik", tgt_f, -1)},
                        {"n": NO_HAND if D_hold > .5 else open_hand(.35 if reach > .5 else .2, (1, .1) if reach > .5 else (0, 1), .2, .3), "f": open_hand(.4, (0, 1), .1, .3, flip=-1) if t < 20.14 else NO_HAND}, exp_d, feet,
                        head_ang=.03 * math.sin(t * 2.6) + .05 * uC, hood=8 * math.sin(ph) * amp)
    scn.append(blob(ellipse_pts(x_d, GY10 + 14, 150, 14, 14), "#2a1608", .35))
    scn.append(D_["legs"] + D_["arm_f"] + D_["body"])
    # букет и руки
    rot = 4 * math.sin(t * 3.2) * (1 - uC) - 14 * uC
    tip = (bx, by + 70 * GK)
    gb_s, gf_s = PR.bouquet(0, 0, 0), ""  # заглушка, не используется
    scn.append(S_["arm_n"])
    back_s, front_s = people.grip_svg("seller", (bx, by), R, +1, k=gk_s, seed=910) if s_hold > .02 else ("", "")
    back_d, front_d = people.grip_svg("dima", (bx, by), R, -1, k=gk_d, seed=930) if D_hold > .5 else ("", "")
    scn.append(D_["arm_n"] if True else "")
    bq = PR.bouquet(tip[0], tip[1], GK, rot, 1)
    scn.append(back_s + back_d + bq + front_s + front_d)
    # сверкание, сердечки на «цветы»
    if hitC > 0:
        scn.append(burst(bx, by - 70, clamp(hitC / .55), 12, 70, 190, 10, "#fff0a8", 11200, spread=360))
        for i, (dx, dy, tt, rr) in enumerate(((-80, -110, .05, 40), (70, -140, .14, 34), (10, -200, .22, 46), (-30, -60, .3, 30))):
            scn.append(glint(bx + dx, by + dy, clamp((hitC - tt) / .8), rr, "#fffbe0"))
        for i, (dx, tt, col) in enumerate(((-50, .12, "#e0527a"), (30, .26, "#f58aa6"), (80, .4, "#e0527a"))):
            u = clamp((hitC - tt) / .9)
            if 0 < u < 1:
                scn.append(heart(bx + 150 + dx * .6 + 14 * math.sin(u * 8 + i), by - 120 - 260 * ease_out(u, 2), 20 * (.6 + .5 * math.sin(math.pi * u)), col, 11300 + i, 10 * math.sin(u * 6 + i)))
    cam = lib.cam(cxm, cym, z, roll)
    return f'<g transform="{cam}">{"".join(scn)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    body = {"s09": frame09, "s10": frame10}[sid](t)
    bg = "#9aa6c4" if sid == "s09" else "#cfe9f5"
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
