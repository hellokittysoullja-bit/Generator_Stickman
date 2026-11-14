"""Рилс 62 «медитация», группа D: дыхание.
s12 (18.15–20.2): схема на бумаге — силуэт Димы в лотосе, в груди шарик дыхания надувается и сдувается; «Оказалось» (18.32)
                  шарик вспыхивает, расходится волна-линия; «замечать» (19.26) у головы выскакивает огонёк-внимание и замечает
                  облако-мысль; «мысли» (19.97) облако вздрагивает; наезд на шарик.
s13 (20.2–22.5):  та же бумага шире: «убежали» (20.29) мысли (суп, мобильник, утюг) на ниточках улетают шариками и утаскивают
                  огонёк; «возвращаться» (21.24) огонёк катится по пунктиру обратно к груди; «дыханию» (21.96) шарик принимает его
                  и качает спокойную волну; откат, дрейф вниз.
s14 (22.5–24.3):  комната — в s62d_room.py.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Букв и цифр нет; свет — сплошные лучи и кольца, без полупрозрачных фигур."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(STORY, "common"))
import lib  # noqa: E402
from lib import (INK, back_out, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad,  # noqa: E402,F401
                 rrect, shape, smooth)

try:
    import props  # noqa: E402
except Exception:  # pragma: no cover
    props = None

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


T_OK, T_ZAM, T_MYS, T_UB, T_VOZ, T_DYH = wt(43), wt(44), wt(46), wt(47), wt(49), wt(51)   # 18.32 19.26 19.97 20.29 21.24 21.96
BR_T = 2.6          # период дыхания, с (вдох+выдох)


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def decay(t, t0, k=9.0, fr=22.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def breath(t):
    """−1…1, плавный синус: вдох растёт, выдох спадает."""
    return math.sin(2 * math.pi * (t - 17.9) / BR_T)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def G(inner, x, y, s=1.0, rot=0.0, sx=None, sy=None):
    sx = s if sx is None else sx * s
    sy = s if sy is None else sy * s
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sx:.4f} {sy:.4f})">{inner}</g>'


def pop_s(t, t0, freq=2.6, damp=6.0, amp=0.34):
    """Пружинный выскок: (sx, sy). До t0 — 0. Сначала сжатие по вертикали, потом вытяжка, отскок с затуханием."""
    if t < t0:
        return 0.0, 0.0
    u = t - t0
    g = ease_out(clamp(u / .16), 2)
    w = math.exp(-damp * u) * math.sin(2 * math.pi * freq * u)
    sy = g * (1 + amp * w)
    sx = g * (1 - amp * .7 * w)
    return sx, sy


def jolt(t, t0, amp=.22):
    """Вздрагивание: сплющивание и отскок (множители sx, sy)."""
    if t < t0:
        return 1.0, 1.0
    u = t - t0
    w = math.exp(-7 * u) * math.cos(2 * math.pi * 3.2 * u)
    return 1 + amp * w, 1 - amp * w


def rays(x, y, r0, r1, n, col, rot=0.0, wid=10.0, seed=0, ink=False):
    out = []
    rs = np.random.RandomState(seed)
    for i in range(n):
        a = rot + i / n * 2 * math.pi
        L = (r1 - r0) * (1 if i % 2 == 0 else .7) * rs.uniform(.92, 1.06)
        p0 = (x + math.cos(a) * r0, y + math.sin(a) * r0)
        p1 = (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))
        pm = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        if ink:
            out.append(line([p0, pm, p1], wid + 6, INK, taper=.7, wmin=.25, peak=.45, seed=seed + i))
        out.append(line([p0, pm, p1], wid, col, taper=.7, wmin=.25, peak=.45, seed=seed + 50 + i))
    return "".join(out)


def ring_line(cx, cy, r, w, col, seed=0, wob=.012, ry=None):
    ry = r if ry is None else ry
    n = 48
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        k = 1 + wob * math.sin(5 * a + seed)
        pts.append((cx + math.cos(a) * r * k, cy + math.sin(a) * ry * k))
    return line(pts, w, col, taper=0, wmin=1, seed=seed)


def star4(x, y, r, col, rot=0.0, w=4):
    pts = []
    for i in range(8):
        a = math.radians(rot) + i * math.pi / 4
        rr = r if i % 2 == 0 else r * .28
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, col, w=w, seed=int(abs(x + y)) % 97)


# ================================================================ бумага
def paper_bg(seed=3):
    o = ['<rect x="-1400" y="-1400" width="3900" height="4800" fill="#f3ead6"/>']
    g = rad_grad([(0, "#fbf5e8", 1), (.7, "#f3ead6", 1), (1, "#e6d8bc", 1)], 540, 860, 1100, 1400)
    o.append(f'<rect x="-1400" y="-1400" width="3900" height="4800" fill="url(#{g})"/>')
    rs = np.random.RandomState(seed)
    for k in range(120):
        x, y = rs.uniform(-700, 1780), rs.uniform(-700, 2600)
        a = rs.uniform(0, 3.14)
        L = rs.uniform(10, 26)
        o.append(line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], 2.6, "#e2d3b6" if k % 2 else "#fffaf0", taper=.5, wmin=.3, seed=k))
    # каракули на полях (без букв): спираль, волна, звёздочки
    sp = [(110 + math.cos(a) * a * 5, 1480 + math.sin(a) * a * 5) for a in np.linspace(0, 14, 60)]
    o.append(line(sp, 5, "#c4b391", taper=.4, wmin=.3, seed=91))
    o.append(line([(800 + 26 * k, 1560 + (14 if k % 2 else -14)) for k in range(8)], 5, "#c4b391", taper=.4, wmin=.3, seed=92))
    o.append(star4(950, 1400, 20, "#efe2c4", rot=10))
    o.append(star4(-120, 300, 22, "#efe2c4", rot=-8))
    o.append(star4(1200, 120, 18, "#efe2c4", rot=20))
    return "".join(o)


# ================================================================ силуэт Димы в лотосе (схема)
FIG = dict(cx=540.0, head=(540.0, 548.0), chest=(540.0, 900.0), base_y=1262.0)
C_SKIN, C_SKIN_SH = "#f1c9a3", "#dca883"
C_HOOD, C_HOOD_SH, C_HOOD_HI = "#d9a441", "#b6832a", "#e8bf66"
C_PANTS, C_PANTS_SH = "#4f5a6b", "#3b4453"
C_HAIR = "#4a3426"


def lotus_figure(t, rise=0.0, smile=0.0, seed=10):
    """Схематичный Дима в лотосе анфас. rise — подъём плеч на вдохе (px)."""
    o = []
    cx = FIG["cx"]
    by = FIG["base_y"]
    sh = -rise
    # ноги крест-накрест: широкая основа с коленями в стороны
    legs = [(cx - 330, by - 70), (cx - 300, by - 128), (cx - 190, by - 150), (cx - 60, by - 128), (cx, by - 112), (cx + 60, by - 128),
            (cx + 190, by - 150), (cx + 300, by - 128), (cx + 330, by - 70), (cx + 290, by - 18), (cx + 140, by), (cx - 140, by), (cx - 290, by - 18)]
    inner = blob([(cx - 340, by - 60), (cx + 340, by - 60), (cx + 340, by + 10), (cx - 340, by + 10)], C_PANTS_SH)
    # складка скрещённых голеней
    inner += line([(cx - 250, by - 52), (cx - 90, by - 66), (cx + 60, by - 40)], 6, INK, taper=.5, wmin=.3, seed=seed)
    inner += line([(cx + 250, by - 52), (cx + 110, by - 64), (cx - 20, by - 50)], 6, INK, taper=.5, wmin=.3, seed=seed + 1)
    o.append(shape(legs, C_PANTS, inner, w=7, seed=seed + 2))
    # стопы на бёдрах
    for s in (-1, 1):
        fx = cx + s * 120
        foot = [(fx - s * 60, by - 92), (fx, by - 106), (fx + s * 54, by - 96), (fx + s * 60, by - 74), (fx, by - 66), (fx - s * 56, by - 74)]
        o.append(shape(foot, C_SKIN, blob(ellipse_pts(fx, by - 70, 50, 8, 10), C_SKIN_SH), w=5, seed=seed + 3 + (s > 0)))
    # туловище — худи
    sy0 = 720 + sh
    torso = [(cx - 150, sy0 + 18), (cx - 92, sy0 - 6), (cx, sy0 - 12), (cx + 92, sy0 - 6), (cx + 150, sy0 + 18), (cx + 172, sy0 + 90),
             (cx + 146, by - 210), (cx + 150, by - 120, 1), (cx - 150, by - 120, 1), (cx - 146, by - 210), (cx - 172, sy0 + 90)]
    tin = blob([(cx + 110, sy0), (cx + 200, sy0), (cx + 200, by), (cx + 130, by)], C_HOOD_SH)
    tin += blob([(cx - 120, sy0 + 40), (cx - 90, sy0 + 30), (cx - 98, by - 200), (cx - 128, by - 190)], C_HOOD_HI)
    # карман-кенгуру
    o.append(shape(torso, C_HOOD, tin, w=7, seed=seed + 6))
    # капюшон за шеей
    o.append(shape([(cx - 88, sy0 + 4), (cx - 60, sy0 - 30), (cx + 60, sy0 - 30), (cx + 88, sy0 + 4), (cx + 40, sy0 + 34), (cx - 40, sy0 + 34)],
                   C_HOOD_SH, w=6, seed=seed + 7))
    # руки к коленям
    for s in (-1, 1):
        S = (cx + s * 132, sy0 + 40)
        E = (cx + s * 238, sy0 + 268)
        Wr = (cx + s * 268, by - 150)
        pts = [S, (cx + s * 196, sy0 + 150), E, (cx + s * 258, sy0 + 330), Wr]
        o.append(line(pts, 56, INK, taper=0, wmin=1, seed=seed + 10 + (s > 0)))
        o.append(line(pts, 44, C_HOOD if s < 0 else mix(C_HOOD, C_HOOD_SH, .5), taper=0, wmin=1, seed=seed + 12 + (s > 0)))
        o.append(line([(E[0] - s * 4, E[1] - 30), (E[0] + s * 10, E[1] + 6)], 5, C_HOOD_SH, taper=.5, wmin=.3, seed=seed + 18 + (s > 0)))
        cuff = (Wr[0] - s * 3, Wr[1] - 14)
        o.append(line([(cuff[0] - 22, cuff[1] - 4), (cuff[0] + 22, cuff[1] + 4)], 12, C_HOOD_SH, taper=0, wmin=1, seed=seed + 19 + (s > 0)))
        # кисть на колене, пальцы колечком
        hx, hy = Wr[0] + s * 8, Wr[1] + 22
        o.append(shape(ellipse_pts(hx, hy, 34, 28, 12), C_SKIN, blob(ellipse_pts(hx + s * 6, hy + 10, 26, 12, 8), C_SKIN_SH), w=5, seed=seed + 14 + (s > 0)))
        o.append(ring_line(hx - s * 4, hy - 6, 11, 5, INK, seed=seed + 16 + (s > 0)))
    # шея и голова
    hx, hy = FIG["head"][0], FIG["head"][1] + sh * .8
    o.append(shape([(hx - 34, hy + 80), (hx + 34, hy + 80), (hx + 38, sy0 + 6), (hx - 38, sy0 + 6)], C_SKIN_SH, w=5, seed=seed + 20))
    for s in (-1, 1):
        o.append(shape(ellipse_pts(hx + s * 106, hy + 4, 18, 28, 10), C_SKIN, w=5, seed=seed + 21 + (s > 0)))
    face = ellipse_pts(hx, hy, 108, 122, 16)
    fin = blob(ellipse_pts(hx + 70, hy + 30, 40, 70, 10), C_SKIN_SH)
    # щетина точками
    rs = np.random.RandomState(seed)
    for k in range(26):
        a = rs.uniform(.25, 2.9)
        r = rs.uniform(.72, .95)
        fin += f'<circle cx="{f(hx + math.cos(a) * 100 * r)}" cy="{f(hy + 20 + math.sin(a) * 96 * r)}" r="2.4" fill="#9c7a62"/>'
    o.append(shape(face, C_SKIN, fin, w=7, seed=seed + 23))
    # лохматые волосы шапкой сверху
    hair = [(hx - 116, hy - 10), (hx - 124, hy - 70), (hx - 96, hy - 128), (hx - 108, hy - 156, 1), (hx - 52, hy - 150), (hx - 40, hy - 186, 1),
            (hx + 4, hy - 150), (hx + 30, hy - 184, 1), (hx + 56, hy - 146), (hx + 110, hy - 164, 1), (hx + 104, hy - 112), (hx + 128, hy - 64),
            (hx + 116, hy - 8), (hx + 92, hy - 56), (hx + 50, hy - 76, 1), (hx + 10, hy - 54), (hx - 30, hy - 80, 1), (hx - 74, hy - 54), (hx - 100, hy - 60)]
    o.append(shape(hair, C_HAIR, line([(hx - 60, hy - 120), (hx - 10, hy - 104)], 5, "#6a4c38", seed=seed + 24), w=6, seed=seed + 25))
    # закрытые глаза дугами, мешки
    for s in (-1, 1):
        ex = hx + s * 42
        o.append(line([(ex - 24, hy + 2), (ex, hy + 12), (ex + 24, hy + 2)], 7, INK, taper=.5, wmin=.3, seed=seed + 26 + (s > 0)))
        o.append(line([(ex - 18, hy + 30), (ex, hy + 36), (ex + 18, hy + 30)], 3.5, "#c08f72", taper=.5, wmin=.3, seed=seed + 28 + (s > 0)))
        o.append(line([(ex - 22, hy - 30 - 2 * smile), (ex + 18, hy - 34 - 2 * smile)], 7, C_HAIR, taper=.4, wmin=.4, seed=seed + 30 + (s > 0)))
    o.append(line([(hx - 4, hy + 18), (hx + 6, hy + 44), (hx - 6, hy + 50)], 5, mix(C_SKIN_SH, INK, .5), taper=.4, wmin=.3, seed=seed + 32))
    m = 6 + 10 * smile
    o.append(line([(hx - 26, hy + 72), (hx, hy + 72 + m), (hx + 26, hy + 72)], 6, INK, taper=.5, wmin=.3, seed=seed + 33))
    return "".join(o)


# ================================================================ шарик дыхания, огонёк, облака
def breath_ball(x, y, r, glow=0.0, seed=0):
    o = []
    if glow > .2:
        o.append(rays(x, y, r * 1.25, r * (1.25 + 1.3 * (glow - .2) / .8), 12, "#ffc94a", rot=glow * .8, wid=12, seed=seed + 40, ink=True))
    col = mix("#f4793b", "#ffc23a", glow)
    g = rad_grad([(0, mix("#ffd9a0", "#fff6cf", glow), 1), (.55, col, 1), (1, mix(col, "#c8482a", .55), 1)], x - r * .25, y - r * .3, r * 1.3)
    inner = blob(ellipse_pts(x - r * .38, y - r * .42, r * .2, r * .13, 10, rot=-30), "#fff4dc")
    o.append(shape(ellipse_pts(x, y, r, r, 18), f"url(#{g})", inner, w=6, seed=seed))
    return "".join(o)


def flame(x, y, k=1.0, t=0.0, look=(0.0, 0.0), lean=0.0, eyes=True, seed=0):
    """Огонёк-внимание: (x, y) — центр основания, высота ~110·k. look — куда глядят глазки (−1…1)."""
    fl = 1 + .06 * osc(t, 2.3, seed) + .04 * osc(t, 5.1, seed * 2)
    sw = 7 * osc(t, 1.7, seed) + lean
    pts = []
    n = 20
    for i in range(n):
        a = 2 * math.pi * i / n
        u = (1 - math.cos(a)) / 2         # 0 низ … 1 верх
        r = 42 * k * (1 - u ** 1.6) ** .85 * (1.05 - .1 * u)
        yy = -(1 - math.cos(a)) * 0.5 * 110 * k * fl + 34 * k
        xx = math.sin(a) * r + sw * k * u ** 1.5
        pts.append((x + xx, y + yy))
    pts[n // 2] = (x + sw * k * 1.0, y - 110 * k * fl + 34 * k, 1)
    core = []
    for p in pts:
        core.append((x + (p[0] - x) * .55 + sw * k * .12, y + 20 * k + (p[1] - y - 20 * k) * .58))
    inner = blob(core, "#ffd54a")
    o = shape(pts, "#f2862e", inner, w=5.5, seed=seed)
    if eyes:
        for s in (-1, 1):
            ex = x + s * 13 * k + look[0] * 7 * k + sw * k * .25
            ey = y - 8 * k + look[1] * 5 * k
            o += f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{f(5.2 * k)}" ry="{f(7.5 * k)}" fill="{INK}"/>'
            o += f'<circle cx="{f(ex - 1.6 * k)}" cy="{f(ey - 2.6 * k)}" r="{f(1.8 * k)}" fill="#fff6dc"/>'
    return o


def cloud_pts(cx, cy, rx, ry, n, seed, bump=.17):
    rs = np.random.RandomState(seed)
    out = []
    amp = rs.uniform(.75, 1.25, n)
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        for kk in range(7):
            u = kk / 6
            a = a0 + (a1 - a0) * u
            r = 1 + bump * amp[i] * math.sin(math.pi * u)
            p = (cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r)
            if kk == 0:
                out.append(p + (1,))
            elif kk < 6:
                out.append(p)
    return out


def icon_soup(t, seed=0):
    if props is not None and hasattr(props, "plate_soup"):
        return props.plate_soup(0, 30, k=.62, steam=1.0, t=t, seed=seed)
    o = []
    for k in range(3):
        xs = -34 + 34 * k
        pts = [(xs + 10 * math.sin(t * 3 + k + j * .8), -20 - 18 * j) for j in range(5)]
        o.append(line(pts, 8, "#c9c2b4", taper=.6, wmin=.3, seed=seed + k))
    o.append(shape([(-80, 0), (80, 0), (60, 48), (-60, 48)], "#e9e4da", blob([(-80, 0), (80, 0), (78, 12), (-78, 12)], "#e0893a"), w=6, seed=seed + 4))
    o.append(shape(ellipse_pts(0, 0, 80, 14, 14), "#e0893a", blob(ellipse_pts(-22, 0, 12, 5, 8), "#f6b33f") + blob(ellipse_pts(26, 2, 10, 4, 8), "#5f9a4a"),
                   w=5, seed=seed + 5))
    return "".join(o)


def icon_mobilnik(t, seed=0):
    if props is not None and hasattr(props, "mobilnik"):
        return props.mobilnik(0, 0, k=.8, rot=10 * math.sin(t * 9))
    a = 10 * math.sin(t * 9)
    body = lib.T(rrect(-30, -54, 30, 54, r=12), 0, 0, 1, a)
    o = shape(body, "#2c3036", blob(lib.T(rrect(-22, -44, 22, 40, r=6), 0, 0, 1, a), "#3c424a"), w=6, seed=seed)
    for s in (-1, 1):
        o += line([(s * 46, -30), (s * 58, -40)], 5, INK, taper=.5, wmin=.3, seed=seed + 2 + (s > 0))
        o += line([(s * 48, 0), (s * 62, 0)], 5, INK, taper=.5, wmin=.3, seed=seed + 4 + (s > 0))
    return o


def icon_iron(t, seed=0):
    if props is not None and hasattr(props, "iron"):
        return props.iron(0, 34, k=.6, smoke=1.0, t=t, seed=seed)
    o = []
    for k in range(2):
        pts = [(-20 + 30 * k + 10 * math.sin(t * 3.4 + k + j), -42 - 16 * j) for j in range(4)]
        o.append(line(pts, 8, "#bdb6aa", taper=.6, wmin=.3, seed=seed + k))
    body = [(-62, 30, 1), (62, 30, 1), (58, 4), (30, -26), (-30, -26), (-50, 0)]
    o.append(shape(body, "#d65c4a", blob([(-62, 18), (62, 18), (62, 30), (-62, 30)], "#b8bcc4"), w=6, seed=seed + 3))
    o.append(line([(-30, -26), (-24, -48), (26, -48), (34, -26)], 12, INK, taper=0, wmin=1, seed=seed + 4))
    o.append(line([(-30, -26), (-24, -48), (26, -48), (34, -26)], 6, "#8e3a2e", taper=0, wmin=1, seed=seed + 5))
    return "".join(o)


ICONS = {"soup": icon_soup, "mob": icon_mobilnik, "iron": icon_iron}


def thought(x, y, w, h, sx, sy, kind, t, seed=0, rot=0.0):
    """Облако-мысль, (x, y) — центр низа (якорь сжатия)."""
    if sx <= 0.01 or sy <= 0.01:
        return ""
    pts = cloud_pts(0, -h / 2, w / 2, h / 2, 8, seed)
    sh = blob(cloud_pts(4, -h / 2 + 10, w / 2 * .97, h / 2 * .9, 8, seed), "#e3ddd2")
    art = G(ICONS[kind](t, seed + 7), 0, -h / 2 + 4, min(w, h * 1.4) / 190)
    inner = sh + blob(cloud_pts(-4, -h / 2 - 6, w / 2 * .92, h / 2 * .86, 8, seed), "#ffffff") + art
    return G(shape(pts, "#ffffff", inner, w=6, seed=seed + 1), x, y, 1.0, rot, sx, sy)


def string_pts(a, b, t, sag=40.0, wig=10.0, seed=0, n=9):
    out = []
    for i in range(n):
        u = i / (n - 1)
        x = a[0] + (b[0] - a[0]) * u + wig * math.sin(t * 4 + u * 5 + seed) * math.sin(math.pi * u)
        y = a[1] + (b[1] - a[1]) * u + sag * math.sin(math.pi * u)
        out.append((x, y))
    return out


def dashed(pts, u, w=7.0, col="#c27a3a", dash=26.0, gap=18.0, seed=0, u0=0.0):
    """Пунктир по сплайну через pts; виден участок u0…u (доли длины)."""
    S = lib.sample(pts, False, 2.0)
    d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    L = d[-1]
    a, b = u0 * L, u * L
    o = []
    s = 0.0
    k = 0
    while s < L:
        e = s + dash
        lo, hi = max(s, a), min(e, b)
        if hi - lo > 3:
            idx = (d >= lo) & (d <= hi)
            seg = S[idx]
            if len(seg) >= 2:
                o.append(line([tuple(p) for p in seg[::3]] + [tuple(seg[-1])], w, col, taper=.25, wmin=.6, seed=seed + k))
        s = e + gap
        k += 1
    return "".join(o)


def path_at(pts, u):
    S = lib.sample(pts, False, 2.0)
    d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    x = clamp(u) * d[-1]
    i = int(np.searchsorted(d, x))
    i = min(max(i, 1), len(S) - 1)
    q = (x - d[i - 1]) / max(1e-6, d[i] - d[i - 1])
    p = S[i - 1] + (S[i] - S[i - 1]) * q
    tg = S[i] - S[i - 1]
    return float(p[0]), float(p[1]), math.degrees(math.atan2(tg[1], tg[0]))


def wave_line(x0, x1, y, amp, t, k=0.022, w=7.0, col="#e07a3a", seed=0, front=1.0, cx=540.0, ink=True):
    """Волна-лента от центра cx к краям; front — доля, до куда дошла волна."""
    o = []
    for side in (-1, 1):
        xe = x0 if side < 0 else x1
        pts = []
        n = 70
        for i in range(n + 1):
            u = i / n
            if u > front:
                break
            x = cx + (xe - cx) * u
            env = smooth(0, .12, u) * (1 - .35 * u)
            pts.append((x, y + amp * env * math.sin(abs(x - cx) * k - t * 2 * math.pi / BR_T * 1.0)))
        if len(pts) > 2:
            if ink:
                o.append(line(pts, w + 5, INK, taper=.3, wmin=.4, seed=seed + (side > 0)))
            o.append(line(pts, w, col, taper=.3, wmin=.4, seed=seed + 2 + (side > 0)))
    return "".join(o)


# ================================================================ s12
FLAME_HOME = (726.0, 520.0)
CLOUD12 = (858.0, 352.0)


def frame12(t):
    o = [paper_bg()]
    br = breath(t)
    bx, by_ = FIG["chest"]
    rise = 8 * br
    # волна-кольцо на «Оказалось» — за фигурой и поверх (две)
    rings = []
    for kk, d in enumerate((0.0, .18, .36)):
        u = (t - T_OK - d) / 1.1
        if 0 < u < 1:
            r = 80 + 760 * ease_out(u, 2.2)
            w = 16 * (1 - u) ** 1.3 + 1.5
            rings.append(ring_line(bx, by_ - rise * .5, r, w, ["#e98a3c", "#f0a85a", "#f3be7a"][kk], seed=kk * 7, ry=r * .92))
    o += rings[:1]
    o.append(lotus_figure(t, rise=rise, smile=.2 + .5 * smooth(T_OK, T_OK + .4, t)))
    o += rings[1:]
    # шарик: надувается со вдохом, вспышка на «Оказалось»
    glow = clamp((t - T_OK) / .12) * math.exp(-1.6 * max(0.0, t - T_OK - .2)) if t >= T_OK else 0.0
    pun = 1 + .38 * math.exp(-6 * max(0, t - T_OK)) * math.cos(2 * math.pi * 2.4 * max(0, t - T_OK)) * (t >= T_OK)
    r = 62 * (1 + .17 * br) * pun
    o.append(breath_ball(bx, by_ - rise * .5, r, glow, seed=5))
    if glow > .3:
        for k in range(6):
            a = k / 6 * 2 * math.pi + .5
            tw = .6 + .4 * math.sin((t - T_OK) * 9 + k)
            o.append(star4(bx + math.cos(a) * r * 2.6, by_ + math.sin(a) * r * 2.3, (16 * tw + 4) * (glow - .3) / .7, "#fff3b8", rot=t * 50))
    # облако-мысль у головы (выскакивает до «замечать»)
    T_C = T_ZAM - .32
    sx, sy = pop_s(t, T_C)
    jx, jy = jolt(t, T_MYS, .26)
    shx = 18 * decay(t, T_MYS, 7, 9)
    cxx, cyy = CLOUD12[0] + shx + 8 * osc(t, .6), CLOUD12[1] + 6 * osc(t, .8)
    if sx > 0:
        # кружки-ступеньки к голове
        for k, (dx, dy, rr) in enumerate(((-96, 46, 16), (-150, 92, 12), (-194, 128, 8))):
            u = clamp((t - T_C - .05 * k) / .15)
            if u > 0:
                o.append(shape(ellipse_pts(cxx + dx, cyy + dy, rr * back_out(u), rr * back_out(u), 10), "#ffffff", w=4, seed=60 + k))
        o.append(thought(cxx, cyy + 40, 260, 180, sx * jx, sy * jy, "soup", t, seed=31))
        if t > T_MYS:
            u = clamp((t - T_MYS) / .25)
            for k in range(3):
                a = math.radians(-70 + 40 * k)
                L = 40 * ease_out(u) * (1 - smooth(.6, 1.0, (t - T_MYS) / .45))
                if L > 2:
                    p0 = (cxx + math.cos(a) * 160, cyy - 100 + math.sin(a) * 70)
                    o.append(line([p0, (p0[0] + math.cos(a) * L, p0[1] + math.sin(a) * L)], 7, INK, taper=.5, wmin=.3, seed=70 + k))
    # огонёк-внимание выскакивает у головы и смотрит на облако
    fsx, fsy = pop_s(t, T_ZAM, freq=2.8)
    if fsx > 0:
        lookv = smooth(T_ZAM + .15, T_ZAM + .4, t)
        lean = 10 * lookv + 12 * decay(t, T_MYS, 6, 3)
        fx, fy = FLAME_HOME
        body = flame(0, 0, 1.0, t, look=(.9 * lookv, -.8 * lookv), lean=lean, seed=3)
        o.append(G(body, fx, fy, 1.0, 0, fsx, fsy))
        # взгляд-пунктир от огонька к облаку
        u = clamp((t - T_ZAM - .3) / .3)
        if u > 0:
            o.append(dashed([(fx + 30, fy - 70), (fx + 70, fy - 120), (cxx - 110, cyy + 10)], u, w=5, col="#d48a46", dash=14, gap=12, seed=80))
    # камера: хлёст входит, наезд на шарик в груди
    zin = .96 + .32 * ease_io(clamp((t - 17.95) / 2.45))
    z = zin + .05 * math.exp(-6 * max(0.0, t - T_OK)) * (t >= T_OK)
    set_ink(z)
    shk = 9 * decay(t, T_OK, 8, 15) + 4 * decay(t, T_MYS, 9, 16)
    cy = 900 - 110 * ease_io(clamp((t - 17.95) / 2.45)) + shk * .5
    cxx = 540 + 60 * ease_io(clamp((t - 18.6) / 1.6)) + shk
    return f'<g transform="{lib.cam(cxx, cy, z, -1.2 + 1.6 * ease_io(clamp((t - 17.95) / 2.4)))}">{"".join(o)}</g>'


# ================================================================ s13
THOUGHTS = [  # kind, старт (центр низа), куда улетает, ширина, высота, задержка, зерно
    ("soup", (858.0, 392.0), (1340.0, -760.0), 260, 180, 0.00, 31),
    ("mob", (230.0, 380.0), (-330.0, -700.0), 220, 160, 0.07, 41),
    ("iron", (520.0, 210.0), (660.0, -980.0), 240, 170, 0.14, 51),
]
TOP_HEAD = (540.0, 410.0)
ROAM = (872.0, 128.0)             # куда утащило огонёк
RET = [ROAM, (900.0, 300.0), (800.0, 470.0), (740.0, 640.0), (690.0, 790.0), (604.0, 880.0), (540.0, 900.0)]


def frame13(t):
    o = [paper_bg()]
    br = breath(t)
    bx, by_ = FIG["chest"]
    rise = 8 * br
    calm = smooth(T_DYH, T_DYH + .5, t)
    o.append(lotus_figure(t, rise=rise, smile=.7 + .3 * calm))
    # волна дыхания из шарика (после «дыханию»)
    if t > T_DYH:
        front = ease_out(clamp((t - T_DYH) / .7))
        o.append(wave_line(-700, 1780, by_ - rise * .5, 46 * (.55 + .45 * (br + 1) / 2), t, front=front, cx=bx, seed=90))
    # пунктир обратного пути (рисуется перед «возвращаться»)
    u_dash = ease_io(clamp((t - (T_VOZ - .35)) / .32))
    roll = ease_io(clamp((t - T_VOZ) / (T_DYH - T_VOZ - .06)))
    if u_dash > 0:
        o.append(dashed(RET, u_dash, w=8, col="#c8763a", seed=100, u0=roll))
    # шарик
    meet = t - T_DYH
    pun = 1 + .3 * math.exp(-5 * max(0, meet)) * math.sin(2 * math.pi * 2.2 * max(0, meet)) * (meet > 0)
    r = 62 * (1 + .17 * br) * pun
    gl = .55 * math.exp(-2.2 * max(0, meet)) * (meet > 0)
    o.append(breath_ball(bx, by_ - rise * .5, r, gl, seed=5))
    # мысли на ниточках
    for kind, p0, p1, w, h, dl, sd in THOUGHTS:
        tt = T_UB + dl
        if kind == "soup":
            sx, sy = 1.0, 1.0
        else:
            sx, sy = pop_s(t, 19.98 + (0.0 if kind == "mob" else .08))
        if sx <= 0:
            continue
        u = clamp((t - tt) / 1.45)
        e = ease_in(u, 1.7)
        bob = 10 * osc(t, .7, sd)
        x = p0[0] + (p1[0] - p0[0]) * e + 40 * math.sin(u * 5 + sd) * u
        y = p0[1] + (p1[1] - p0[1]) * e + bob
        rot = 10 * math.sin(u * 4 + sd) * smooth(0, .2, u)
        # нитка: до «убежали» привязана к макушке, потом свободно висит под облаком
        if u <= 0:
            a = (x, y - 2)
            b = (TOP_HEAD[0] + (p0[0] - 540) * .12, TOP_HEAD[1])
            o.append(line(string_pts(a, b, t, sag=24, wig=6, seed=sd), 4.5, INK, taper=.2, wmin=.5, seed=sd))
        else:
            tail = 260 * (1 - .3 * u)
            a = (x, y - 2)
            b = (x - (p1[0] - p0[0]) * .18 * smooth(0, .3, u), y + tail)
            o.append(line(string_pts(a, b, t, sag=0, wig=26, seed=sd), 4.5, INK, taper=.5, wmin=.3, seed=sd))
        o.append(thought(x, y, w, h, sx, sy, kind, t, seed=sd, rot=rot))
    # огонёк: утащило за мыслями → катится по пунктиру домой → в шарик
    if t < T_VOZ:
        u = ease_io(clamp((t - T_UB - .12) / .75))
        ax, ay = FLAME_HOME
        x = ax + (ROAM[0] - ax) * u
        y = ay + (ROAM[1] - ay) * u - 70 * math.sin(math.pi * u)
        tilt = 25 * math.sin(math.pi * u)
        look = (.6, -1.0)
        k = 1.0
        if u > .98:   # спохватился: оглядывается к груди
            look = (-.9 * smooth(T_VOZ - .5, T_VOZ - .3, t) + .6 * (1 - smooth(T_VOZ - .5, T_VOZ - .3, t)), .6 * smooth(T_VOZ - .5, T_VOZ - .3, t))
            tilt = -14 * smooth(T_VOZ - .5, T_VOZ - .3, t)
        o.append(G(flame(0, 0, k, t, look=look, lean=0, seed=3), x, y, 1.0, tilt))
    elif t < T_DYH + .05:
        x, y, ang = path_at(RET, roll)
        spin = -360 * 1.4 * roll        # катится: кувырок
        k = 1.0 - .35 * smooth(.8, 1.0, roll)
        o.append(G(flame(0, -40, k, t, look=(-.5, .7), seed=3), x, y - 40, 1.0, spin))
    else:
        # сел на шарик — маленький огонёк сверху шарика, дышит вместе с ним
        u = clamp((t - T_DYH) / .3)
        sx, sy = jolt(t, T_DYH, .3)
        o.append(G(flame(0, 0, .62, t, look=(0, .2), eyes=True, seed=3), bx, by_ - rise * .5 - r + 6, 1.0, 0, sx, sy * (.9 + .1 * u)))
    # камера: откат и лёгкий дрейф вниз к груди
    zb = 1.26 - .46 * ease_out(clamp((t - 20.0) / .55), 2.5)
    z = zb + .14 * ease_io(clamp((t - 21.0) / 1.7))
    set_ink(z)
    cy = 820 - 120 * ease_out(clamp((t - 20.0) / .55)) + 230 * ease_io(clamp((t - 21.0) / 1.7))
    cxx = 600 - 60 * ease_out(clamp((t - 20.0) / .55)) + 5 * osc(t, .3)
    shk = 6 * decay(t, T_DYH, 8, 14)
    return f'<g transform="{lib.cam(cxx + shk, cy, z, .8 - 1.4 * ease_io(clamp((t - 20.0) / 2.7)))}">{"".join(o)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    if sid == "s14":
        import s62d_room
        return s62d_room.frame14(t)
    fn = {"s12": frame12, "s13": frame13}[sid]
    return lib.svg(fn(t))
