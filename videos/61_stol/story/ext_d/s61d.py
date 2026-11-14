"""Рилс 61 «стол», группа D: графика мозга и идей.
s06 (12.8–15.6): мозг на бумаге — «Оказывается» подпрыгивает и светится, «обстановка» по орбите мини-предметы комнаты,
                 «подталкивает» стрелки-штрихи толкают мозг; наезд с разгоном.
s07 (15.6–17.8): тёплый фон, от мозга вверх дорожки, «думать» вспыхивают лампочки, «по-разному» веер, у каждой свой цвет и
                 форма; откат.
s11 (25.9–27.8): пёстрый фон, облачка: справа необычные идеи (лампочка с крыльями, ракета со спиралью, мячик на ножках,
                 радужная клякса) разлетаются веером на «необычнее»; слева маленькое облако с одной серой лампочкой; наезд вглубь.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Букв и цифр нет; свечение — сплошные лучи, без полупрозрачных фигур."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brain_art as ba  # noqa: E402
import lib  # noqa: E402
from lib import (INK, T, back_out, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, lin_grad, line, mix, rad_grad,  # noqa: E402,F401
                 rrect, shape, smooth, spring)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def decay(t, t0, k=9.0, fr=22.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def G(inner, x, y, s=1.0, rot=0.0, sx=None, sy=None):
    sx = s if sx is None else sx * s
    sy = s if sy is None else sy * s
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sx:.4f} {sy:.4f})">{inner}</g>'


def star4(x, y, r, col, rot=0.0, w=5):
    k = .26
    pts = []
    for i in range(8):
        a = math.radians(rot) + i * math.pi / 4
        rr = r if i % 2 == 0 else r * k
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, col, w=w, seed=int(x + y) % 97)


def rays(x, y, r0, r1, n, col, rot=0.0, wid=10.0, seed=0, ink=False):
    """Сплошные лучи-штрихи вокруг точки (свечение без мутных пятен)."""
    out = []
    rs = np.random.RandomState(seed)
    for i in range(n):
        a = rot + i / n * 2 * math.pi
        L = r1 * (1 if i % 2 == 0 else .72) * rs.uniform(.92, 1.06)
        p0 = (x + math.cos(a) * r0, y + math.sin(a) * r0)
        p1 = (x + math.cos(a) * (r0 + L - r0), y + math.sin(a) * (r0 + L - r0))
        pm = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        if ink:
            out.append(line([p0, pm, p1], wid + 6, INK, taper=.7, wmin=.25, peak=.45, seed=seed + i))
        out.append(line([p0, pm, p1], wid, col, taper=.7, wmin=.25, peak=.45, seed=seed + 50 + i))
    return "".join(out)


def sunburst(x, y, r, n, c1, c2, rot=0.0):
    """Сплошные клинья вокруг точки (фон-сияние)."""
    out = [f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{c1}"/>']
    for i in range(n):
        a0 = rot + i / n * 2 * math.pi
        a1 = a0 + math.pi / n
        out.append(f'<path d="M{f(x)} {f(y)}L{f(x + math.cos(a0) * r)} {f(y + math.sin(a0) * r)}'
                   f'L{f(x + math.cos(a1) * r)} {f(y + math.sin(a1) * r)}Z" fill="{c2}"/>')
    return "".join(out)


def brain_at(t, x, y, s, rot=0.0, sx=1.0, sy=1.0, stem=True):
    return G(f'<g transform="translate({-ba.BCX} {-ba.BCY})">{ba.brain(t, 0.0, stem=stem)}</g>', x, y, s, rot, sx, sy)


# ---------------------------------------------------------------- мини-предметы комнаты (орбита s06)
def icon_mug(seed=0):
    body = rrect(-38, -34, 34, 44, r=12)
    o = [line([(30, -18), (62, -16), (64, 18), (30, 22)], 20, INK, taper=0, wmin=1, seed=seed),
         line([(30, -18), (62, -16), (64, 18), (30, 22)], 11, "#e86a4a", taper=0, wmin=1, seed=seed + 1)]
    inner = blob([(-40, 20), (40, 14), (40, 50), (-40, 50)], "#c94e36") + blob(ellipse_pts(-16, -12, 9, 20, 8), "#ffb7a0")
    o.append(shape(body, "#e86a4a", inner, w=6, seed=seed + 2))
    o.append(shape(ellipse_pts(-2, -34, 36, 9, 12), "#6b3d24", w=5, seed=seed + 3))
    return "".join(o)


def icon_sheet(seed=0):
    pts = [(-46, -58, 1), (30, -58, 1), (46, -42, 1), (46, 58, 1), (-46, 58, 1)]
    inner = "".join(line([(-30, -34 + 20 * k), (-6, -38 + 20 * k), (14, -32 + 20 * k), (30 - 10 * (k == 4), -36 + 20 * k)],
                         5, "#6d7fa8", taper=.4, wmin=.4, seed=seed + k) for k in range(5))
    inner += blob([(30, -58), (46, -42), (30, -42)], "#d9d2c3")
    return shape(pts, "#fffdf6", inner, w=6, seed=seed)


def icon_lamp(on=1.0, seed=0):
    o = []
    if on > 0:
        o.append(rays(10, 30, 46, 96, 7, "#ffd23c", rot=math.radians(40), wid=11, seed=seed + 9))
    o.append(shape(ellipse_pts(-6, 60, 44, 12, 12), "#4d6c8a", w=5, seed=seed))
    o.append(line([(-6, 56), (-24, 10), (6, -28)], 16, INK, taper=0, wmin=1, seed=seed + 1))
    o.append(line([(-6, 56), (-24, 10), (6, -28)], 8, "#6f8fb0", taper=0, wmin=1, seed=seed + 2))
    shade = [(-14, -44, 1), (20, -60, 1), (52, -6, 1), (2, 18, 1)]
    o.append(shape(shade, "#3f78a6", blob([(-14, -44), (20, -60), (28, -46), (-6, -30)], "#6aa5d0"), w=6, seed=seed + 3))
    o.append(blob(ellipse_pts(28, 8, 12, 10, 8), "#ffe27a"))
    return "".join(o)


def icon_wire(t, seed=0):
    pts = []
    for i in range(46):
        u = i / 45
        a = u * 2 * math.pi * 3.2 + .3 * math.sin(t * 3)
        r = 24 + 10 * math.sin(u * 7)
        pts.append((-20 + u * 40 + math.cos(a) * r, math.sin(a) * r * .8))
    pts += [(40, 20), (62, 34), (70, 52)]
    o = [line(pts, 13, INK, taper=0, wmin=1, seed=seed), line(pts, 6, "#2f3a3f", taper=0, wmin=1, seed=seed + 1)]
    o.append(shape(T(rrect(58, 48, 88, 72, r=5), 0, 0, 1, 30, 72, 60), "#f2f0ea", w=5, seed=seed + 2))
    o.append(line([(80, 74), (86, 92)], 6, INK, taper=0, wmin=1, seed=seed + 3))
    o.append(line([(92, 66), (100, 82)], 6, INK, taper=0, wmin=1, seed=seed + 4))
    return "".join(o)


# ---------------------------------------------------------------- лампочки (s07, s11)
BULB_KINDS = {
    "round": [(0, -62), (40, -50), (56, -14), (44, 20), (26, 40, 1), (-26, 40, 1), (-44, 20), (-56, -14), (-40, -50)],
    "pear": [(0, -78), (30, -66), (46, -32), (36, 6), (24, 40, 1), (-24, 40, 1), (-36, 6), (-46, -32), (-30, -66)],
    "tube": [(-26, -86), (0, -94), (26, -86), (30, -40), (30, 20), (24, 40, 1), (-24, 40, 1), (-30, 20), (-30, -40)],
    "globe": [(0, -72), (52, -56), (70, -16), (56, 22), (24, 40, 1), (-24, 40, 1), (-56, 22), (-70, -16), (-52, -56)],
    "flame": [(0, -104, 1), (22, -64), (44, -22), (40, 14), (24, 40, 1), (-24, 40, 1), (-40, 14), (-44, -22), (-22, -64)],
    "drop": [(14, -96, 1), (38, -50), (52, -10), (40, 22), (24, 40, 1), (-24, 40, 1), (-44, 16), (-44, -26), (-16, -66)],
}


def bulb(kind, col, on, seed=0, t=0.0, rays_on=True, filament=True, base_col="#9aa3ab"):
    """Лампочка в своих координатах: стекло вокруг (0, −20), цоколь 40…86. on 0…1 — вспышка (лучи вырастают)."""
    o = []
    glass = BULB_KINDS[kind]
    if on > 0 and rays_on:
        rr = 70 + 30 * on
        o.append(rays(0, -22, rr, rr + 70 * on, 10, mix(col, "#ffffff", .25), rot=seed * .7 + t * .6, wid=13, seed=seed + 30, ink=True))
    gcol = mix("#eceae4", col, on)
    hi = mix("#ffffff", mix(col, "#ffffff", .6), on)
    inner = blob(ellipse_pts(-20, -38, 12, 22, 10, rot=20), hi)
    if on > .3:
        inner = blob(ellipse_pts(0, -8, 34, 30, 12), mix(col, "#fffbe8", .55)) + inner
    if filament:
        fc = mix("#8b8f96", "#fff6c8", on)
        fil = [(-14, 38), (-12, 4), (-6, -6), (0, 4), (6, -6), (12, 4), (14, 38)]
        inner += line(fil, 5, fc, taper=.1, wmin=.6, seed=seed + 2)
    o.append(shape(glass, gcol, inner, w=7, seed=seed + 4))
    # цоколь
    base = rrect(-26, 40, 26, 80, r=6)
    bi = "".join(line([(-28, 50 + 10 * k), (28, 46 + 10 * k)], 5, mix(base_col, "#4a5058", .6), taper=0, wmin=1, seed=seed + 8 + k) for k in range(3))
    o.append(shape(base, base_col, bi, w=6, seed=seed + 6))
    o.append(shape([(-12, 80, 1), (12, 80, 1), (8, 92), (-8, 92)], "#3b3f45", w=4, seed=seed + 7))
    return "".join(o)


# ---------------------------------------------------------------- облако
def cloud_pts(cx, cy, rx, ry, n, seed, wob=0.0, t=0.0, bump=.16):
    rs = np.random.RandomState(seed)
    out = []
    ph = rs.uniform(0, 6.28, n)
    amp = rs.uniform(.75, 1.25, n)
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        for k in range(7):
            u = k / 6
            a = a0 + (a1 - a0) * u
            r = 1 + bump * amp[i] * math.sin(math.pi * u) + wob * math.sin(t * 5 + ph[i])
            p = (cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r)
            if k == 0:
                out.append(p + (1,))
            elif k < 6:
                out.append(p)
    return out


# ================================================================ s06: мозг на бумаге
T_OK, T_OBS, T_POD = wt(24), wt(25), wt(26)      # 13.18, 14.16, 14.88
B6 = (540.0, 800.0)


def brain_jump(t):
    """Подскок мозга на «Оказывается»: присед → взлёт → приземление со сплющиванием."""
    dy, sx, sy = 0.0, 1.0, 1.0
    pre = smooth(T_OK - .22, T_OK, t) * (1 - smooth(T_OK, T_OK + .05, t))
    sx += .07 * pre
    sy -= .08 * pre
    u = t - T_OK
    if 0 <= u < .42:
        h = 4 * (u / .42) * (1 - u / .42)
        dy = -150 * h
        st = .1 * (1 - u / .21) if u < .21 else 0
        sy += st
        sx -= st * .7
    elif u >= .42:
        e = u - .42
        sq = math.exp(-9 * e) * math.cos(2 * math.pi * 3.2 * e)
        sy -= .12 * sq
        sx += .1 * sq
    return dy, sx, sy


def orbit_angle(k, t):
    return -math.pi / 2 + k * math.pi / 2 + .55 * (t - T_OBS) + .35


def frame06(t):
    o = []
    # бумага
    o.append('<rect x="-900" y="-900" width="2900" height="3800" fill="#f3ead6"/>')
    g = rad_grad([(0, "#fbf5e8", 1), (.7, "#f3ead6", 1), (1, "#e6d8bc", 1)], 540, 820, 900, 1100)
    o.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g})"/>')
    rs = np.random.RandomState(3)
    for k in range(70):
        x, y = rs.uniform(-300, 1380), rs.uniform(-200, 2100)
        a = rs.uniform(0, 3.14)
        L = rs.uniform(10, 26)
        o.append(line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], 2.6, "#e2d3b6" if k % 2 else "#fffaf0", taper=.5, wmin=.3, seed=k))
    # каракули на полях бумаги (без букв): спираль, звёздочка, волна
    sp = [(120 + math.cos(a) * a * 5, 360 + math.sin(a) * a * 5) for a in np.linspace(0, 14, 60)]
    o.append(line(sp, 5, "#b9a98a", taper=.4, wmin=.3, seed=91))
    o.append(line([(820 + 26 * k, 1250 + (14 if k % 2 else -14)) for k in range(8)], 5, "#b9a98a", taper=.4, wmin=.3, seed=92))
    o.append(star4(900, 330, 22, "#efe2c4", rot=10, w=4))
    o.append(star4(170, 1230, 18, "#efe2c4", rot=-8, w=4))

    jdy, sx, sy = brain_jump(t)
    glow = ease_out(clamp((t - T_OK) / .25))
    cx, cy = B6[0], B6[1] + jdy
    # толчки стрелок: качание и сдвиг
    rot = 2.0 * osc(t, .7) * (1 - glow) + 1.5 * osc(t, .45)
    push_x = 0.0
    for k in range(4):
        th = T_POD + .07 * k
        a = orbit_angle(k, th)
        rot += -9 * math.cos(a) * decay(t, th + .14, 6.5, 2.6)
        push_x += -18 * math.cos(a) * decay(t, th + .14, 6.5, 2.6)
    cx += push_x
    # сияние за мозгом: сплошные клинья и лучи
    if glow > 0:
        R = 330 * back_out(glow, 1.6)
        o.append(G(sunburst(0, 0, R * 1.35, 16, "#ffe6a0", "#ffd56e", rot=t * .35), cx, cy - 20))
        o.append(f'<circle cx="{f(cx)}" cy="{f(cy - 20)}" r="{f(R * .92)}" fill="#fff3c4"/>')
        o.append(rays(cx, cy - 20, R * .95, R * 1.3, 14, "#ffbf2e", rot=-t * .5, wid=16, seed=5, ink=True))
    # орбита и предметы
    uo = ease_out(clamp((t - T_OBS) / .35))
    ORX, ORY = 470, 225
    behind, front = [], []
    if uo > 0:
        n = 60
        for i in range(n):
            if i % 2:
                continue
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + .8) / n
            seg = [(cx + ORX * uo * math.cos(a), cy + 40 + ORY * uo * math.sin(a)) for a in (a0, (a0 + a1) / 2, a1)]
            (front if math.sin(a0) > 0 else behind).append(line(seg, 5, "#b48a58", taper=.3, wmin=.5, seed=i))
    icons = []
    if t >= T_OBS:
        for k in range(4):
            uk = clamp((t - T_OBS - .09 * k) / .3)
            if uk <= 0:
                continue
            a = orbit_angle(k, t)
            rr = .35 + .65 * ease_out(uk)
            px, py = cx + ORX * rr * math.cos(a), cy + 40 + ORY * rr * math.sin(a)
            # толчок: предмет подаётся к мозгу
            th = T_POD + .07 * k
            pu = smooth(th, th + .12, t) * (1 - .6 * smooth(th + .25, th + .6, t))
            px += (cx - px) * .14 * pu
            py += (cy - py) * .14 * pu
            sc = back_out(uk, 2.2) * (1.05 + .18 * math.sin(a))
            art = [icon_mug(10), icon_sheet(20), icon_lamp(0.0, 30), icon_wire(t, 40)][k]
            icons.append((math.sin(a), px, py, sc, 14 * math.sin(t * 2 + k), art, a, k))
    for z, px, py, sc, rr, art, a, k in sorted(icons):
        (front if z > 0 else behind).append(G(art, px, py, sc * 1.65, rr))
    o += behind
    # мозг
    o.append(brain_at(t, cx, cy, 1.02, rot, sx, sy * (1 + .015 * osc(t, 1.3))))
    # искры при свечении
    if glow > 0:
        for k in range(6):
            a = k / 6 * 2 * math.pi + .4
            ph = (t - T_OK) * 1.3 + k * .17
            tw = .55 + .45 * math.sin(ph * 6.28)
            o.append(star4(cx + math.cos(a) * 300, cy - 30 + math.sin(a) * 230, 24 * glow * tw + 4, "#fff6c8", rot=t * 40, w=4))
    o += front
    # стрелки-штрихи от предметов к мозгу
    for z, px, py, sc, rr, art, a, k in icons:
        th = T_POD + .07 * k
        ua = clamp((t - th) / .16)
        if ua <= 0:
            continue
        dx, dy = cx - px, (cy - 10) - py
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        st = (px + ux * 95, py + uy * 95)
        endL = max(40.0, L - 95 - 190)
        pulse = 18 * max(0.0, math.sin((t - th) * 9)) * (t > th + .16)
        e = (st[0] + ux * (endL * ease_out(ua) + pulse), st[1] + uy * (endL * ease_out(ua) + pulse))
        col = ["#e86a4a", "#4f7fd0", "#e2a21b", "#3c9a6a"][k]
        nx, ny = -uy, ux
        bend = 16 * (1 if k % 2 else -1)
        mid = ((st[0] + e[0]) / 2 + nx * bend, (st[1] + e[1]) / 2 + ny * bend)
        o.append(line([st, mid, e], 22, INK, taper=.15, wmin=.5, peak=.6, seed=70 + k))
        o.append(line([st, mid, e], 12, col, taper=.15, wmin=.5, peak=.6, seed=80 + k))
        hd = [(e[0] + ux * 34, e[1] + uy * 34, 1), (e[0] - ux * 10 + nx * 28, e[1] - uy * 10 + ny * 28, 1),
              (e[0] - ux * 10 - nx * 28, e[1] - uy * 10 - ny * 28, 1)]
        o.append(shape(hd, col, w=6, seed=90 + k))
    # камера: наезд с разгоном к пику riser, удар, дальше медленный наезд
    zin = .86 + .14 * ease_in(clamp((t - 12.6) / (T_OK - 12.6)), 2.2)
    z = zin + .06 * math.exp(-6 * max(0.0, t - T_OK)) * (t >= T_OK) + .05 * ease_io(clamp((t - T_OK) / (15.8 - T_OK)))
    set_ink(z)
    shk = 10 * decay(t, T_OK, 8, 17) + 6 * decay(t, T_POD + .16, 7, 15)
    cam = lib.cam(540 + shk, 840 - 30 * glow + shk * .5, z, -1.5 + 1.2 * ease_io(clamp((t - 12.6) / 3.2)))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ================================================================ s07: дорожки и лампочки веером
T_DUM, T_RAZ = wt(28), wt(29)     # 16.08, 16.45
O7 = (540.0, 1000.0)
B7 = [  # (вид, цвет, базовый угол от вертикали °, длина)
    ("round", "#ffcc2e", -8, 600),
    ("pear", "#ff6f4f", 14, 560),
    ("tube", "#3cc6e0", -30, 520),
    ("globe", "#6ccf5a", 34, 540),
    ("flame", "#ff6fb4", -52, 470),
    ("drop", "#9a7cf0", 56, 480),
]


def frame07(t):
    o = []
    g = lin_grad([(0, "#ffe2b0", 1), (.55, "#ffc27c", 1), (1, "#f39a57", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g})"/>')
    # тёплые горошины фона
    for j in range(-6, 26):
        for i in range(-6, 14):
            x = i * 110 + (55 if j % 2 else 0)
            y = j * 100
            o.append(f'<circle cx="{x}" cy="{y}" r="10" fill="{"#ffd598" if y < 900 else "#f6ad6c"}"/>')
    # дорожки: растут от мозга, на «по-разному» расходятся веером
    grow = ease_out(clamp((t - 15.45) / .6))
    fan = spring(max(0.0, t - T_RAZ), 2.2, 4.5)
    tips = []
    for k, (kind, col, ang, L) in enumerate(B7):
        a = math.radians(ang * (.55 + .45 * fan) + 2.2 * osc(t, .6, k))
        LL = L * (.86 + .14 * fan)
        u = clamp(grow * 1.15 - .03 * k)
        if u <= 0:
            continue
        e = (O7[0] + math.sin(a) * LL * u, O7[1] - math.cos(a) * LL * u)
        c = (O7[0] + math.sin(a) * LL * .45 * u - math.sin(a) * 60, O7[1] - math.cos(a) * LL * .55 * u)
        pts = [O7, ((O7[0] + c[0]) / 2, (O7[1] + c[1]) / 2 - 20 * u), c, e]
        o.append(line(pts, 26, INK, taper=0, wmin=1, seed=200 + k))
        o.append(line(pts, 15, mix(col, "#fff4dc", .25), taper=0, wmin=1, seed=210 + k))
        # бегущие искры по дорожке (сплошные точки)
        if t > T_DUM - .1:
            for m in range(2):
                q = ((t - T_DUM) * 1.6 + m * .5 + k * .13) % 1
                from ink import sample
                S = sample(pts, False, 8)
                p = S[min(len(S) - 1, int(q * (len(S) - 1)))]
                o.append(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="7" fill="#fffbe6"/>')
        tips.append((k, kind, col, e, u, a))
    # мозг внизу (без стебля, низ выше полосы субтитров)
    bump = 10 * decay(t, T_DUM, 6, 3) + 8 * decay(t, T_RAZ, 6, 3)
    o.append(brain_at(t, 540, 1112 - bump, .78, 2 * osc(t, .5), 1 + .02 * osc(t, 1.4), 1 - .02 * osc(t, 1.4), stem=False))
    # лампочки: первые три на «думать», остальные — по очереди на «по-разному»
    order = [0, 1, 2, 3, 4, 5]
    on_t = {0: T_DUM, 1: T_DUM + .08, 2: T_RAZ + .05, 3: T_RAZ + .14, 4: T_RAZ + .23, 5: T_RAZ + .32}
    for k, kind, col, e, u, a in tips:
        if u < .5:
            continue
        ap = back_out(clamp((u - .5) / .5), 2.0)
        on = ease_out(clamp((t - on_t[order[k]]) / .14))
        flash = 1 + .22 * math.exp(-10 * max(0.0, t - on_t[k])) * (t >= on_t[k])
        o.append(G(bulb(kind, col, on, seed=k * 11, t=t), e[0] + math.sin(a) * 100, e[1] - math.cos(a) * 100,
                   1.3 * ap * flash * (.68 + .32 * min(1.0, fan)), math.degrees(a) + 6 * osc(t, .8, k)))
    # камера: откат, чтобы показать веер, лёгкий дрейф
    z = 1.32 - .42 * ease_out(clamp((t - 15.4) / 1.5), 2.4) - .04 * ease_io(clamp((t - 16.9) / 1.1))
    set_ink(z)
    cy = 900 - 110 * ease_out(clamp((t - 15.4) / 1.4))
    cam = lib.cam(540 + 30 * osc(t, .18), cy, z, 1.2 - 1.6 * ease_io(clamp((t - 15.4) / 2.6)))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ================================================================ s11: облачка идей
T_NEO = wt(47)      # 26.293
C_BIG = (650.0, 920.0)
C_SM = (220.0, 1090.0)


def winged_bulb(t, seed=0):
    flap = math.sin(t * 22)
    o = []
    for sgn in (-1, 1):
        wpts = [(sgn * 36, -40, 1), (sgn * 90, -96 - 30 * flap), (sgn * 140, -70 - 40 * flap), (sgn * 130, -30 - 18 * flap),
                (sgn * 96, -20), (sgn * 60, -8, 1)]
        inner = "".join(line([(sgn * 50, -28), (sgn * (90 + 12 * j), -54 - 20 * flap - 6 * j)], 5, "#c9d7e6", taper=.5, wmin=.3, seed=seed + j)
                        for j in range(3))
        o.append(shape(wpts, "#ffffff", inner, w=6, seed=seed + 3 + sgn))
    o.append(bulb("round", "#ffd23a", 1.0, seed=seed, t=t, rays_on=False))
    return "".join(o)


def spiral_rocket(t, seed=0):
    o = []
    # спиральный след сзади (сплошной штрих)
    sp = []
    for i in range(40):
        u = i / 39
        a = u * 6 * math.pi + t * 9
        sp.append((-math.sin(a) * 26 * (1 - .4 * u), 90 + u * 200))
    o.append(line(sp, 22, INK, taper=.6, wmin=.25, peak=.15, seed=seed))
    o.append(line(sp, 13, "#ff9e3c", taper=.6, wmin=.25, peak=.15, seed=seed + 1))
    fl = [(-20, 70, 1), (20, 70, 1), (10 + 4 * math.sin(t * 40), 120), (0, 140 + 10 * math.sin(t * 33)), (-10, 120)]
    o.append(shape(fl, "#ffd23a", w=5, seed=seed + 2))
    for sgn in (-1, 1):
        o.append(shape([(sgn * 30, 20, 1), (sgn * 62, 70, 1), (sgn * 30, 64, 1)], "#3f6fc9", w=6, seed=seed + 4 + sgn))
    body = [(0, -110), (28, -70), (34, 10), (30, 70, 1), (-30, 70, 1), (-34, 10), (-28, -70)]
    stripes = "".join(f'<path d="M-60 {-90 + 34 * j}L60 {-130 + 34 * j}L60 {-112 + 34 * j}L-60 {-72 + 34 * j}Z" fill="#e8463e"/>' for j in range(7))
    inner = stripes + blob(ellipse_pts(0, -30, 16, 16, 10), "#9fd8ff") + line(ellipse_pts(0, -30, 16, 16, 12) + [ellipse_pts(0, -30, 16, 16, 12)[0]], 5, INK, seed=seed + 9)
    o.append(shape(body, "#fdf6ea", inner, w=7, seed=seed + 7))
    return "".join(o)


def legged_ball(t, seed=0):
    o = []
    step = math.sin(t * 16)
    for sgn, ph in ((-1, 1), (1, -1)):
        hip = (sgn * 22, 48)
        knee = (sgn * 26 + 10 * step * ph, 84)
        ft = (sgn * 30 + 18 * step * ph, 118 - 8 * max(0.0, step * ph))
        o.append(line([hip, knee, ft], 13, INK, taper=0, wmin=1, seed=seed + sgn))
        o.append(shape(rrect(ft[0] - 14, ft[1] - 8, ft[0] + 26, ft[1] + 12, r=9), "#e8463e", w=5, seed=seed + 3 + sgn))
    inner = (f'<path d="M-80 -20 Q0 10 80 -20 L80 10 Q0 40 -80 10Z" fill="#3f6fc9"/>'
             f'<path d="M-80 -70 Q0 -40 80 -70 L80 -50 Q0 -20 -80 -50Z" fill="#ffd23a"/>'
             + blob(ellipse_pts(-26, -30, 16, 12, 10, rot=-30), "#ffffff"))
    o.append(shape(ellipse_pts(0, 0, 62, 62, 14), "#f5f2ea", inner, w=7, seed=seed + 6))
    return "".join(o)


def rainbow_blob(t, seed=0):
    pts = []
    n = 12
    rs = np.random.RandomState(seed)
    ph = rs.uniform(0, 6.28, n)
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 68 * (1 + .18 * math.sin(3 * a + t * 4) + .08 * math.sin(5 * a + ph[i] + t * 6))
        pts.append((math.cos(a) * r, math.sin(a) * r * .9))
    cols = ["#e8463e", "#ff9e3c", "#ffd23a", "#6ccf5a", "#3cc6e0", "#3f6fc9", "#9a7cf0"]
    inner = "".join(f'<rect x="-120" y="{-100 + 28 * j}" width="240" height="30" fill="{c}" transform="rotate(-18)"/>' for j, c in enumerate(cols))
    inner += blob(ellipse_pts(-24, -26, 14, 9, 8, rot=-20), "#ffffff")
    o = [shape(pts, "#ffd23a", inner, w=7, seed=seed + 2)]
    # капельки-брызги
    for k in range(3):
        a = t * 2 + k * 2.1
        o.append(shape(ellipse_pts(math.cos(a) * 100, math.sin(a) * 90, 12, 12, 8), cols[(k * 2) % 7], w=4, seed=seed + 10 + k))
    return "".join(o)


IDEAS = [  # (функция, конечная точка относительно облака, масштаб, скорость вращения)
    (winged_bulb, (-330, -500), 1.3, -8),
    (spiral_rocket, (40, -640), 1.4, 0),
    (legged_ball, (-350, -270), 1.5, 18),
    (rainbow_blob, (280, -400), 1.6, -40),
]


def frame11(t):
    o = []
    # пёстрый фон: глубокий фиолетовый с цветными конфетти
    o.append('<rect x="-900" y="-900" width="2900" height="3800" fill="#3b3266"/>')
    rs = np.random.RandomState(17)
    cols = ["#ff7a5c", "#ffd23a", "#5fd0c4", "#ff8fc8", "#8fd36a", "#7aa7ff"]
    par = 18 * (t - 25.7)
    for k in range(110):
        x, y = rs.uniform(-350, 1430), rs.uniform(-250, 2150)
        c = cols[k % 6]
        r = rs.uniform(9, 20)
        a = rs.uniform(0, 6.28) + (t - 25.7) * rs.uniform(-.6, .6)
        y += par * rs.uniform(.3, 1)
        kind = k % 3
        if kind == 0:
            o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{c}"/>')
        elif kind == 1:
            pts = [(x + math.cos(a + j * 2.094) * r * 1.3, y + math.sin(a + j * 2.094) * r * 1.3, 1) for j in range(3)]
            o.append(blob(pts, c))
        else:
            o.append(line([(x - math.cos(a) * r * 1.4, y - math.sin(a) * r * 1.4), (x + math.sin(a) * 8, y - math.cos(a) * 8),
                           (x + math.cos(a) * r * 1.4, y + math.sin(a) * r * 1.4)], 7, c, taper=.3, wmin=.5, seed=k))
    burst = t - T_NEO
    puff = 1 + .08 * math.exp(-7 * max(0.0, burst)) * math.sin(max(0.0, burst) * 30) * (burst > 0)
    pre = smooth(25.7, T_NEO, t)
    # маленькое облако слева: одна серая лампочка, вяло покачивается
    bub = [(C_SM[0] + 40, C_SM[1] + 140, 18), (C_SM[0] + 66, C_SM[1] + 180, 11)]
    for k, (x, y, r) in enumerate(bub):
        o.append(shape(ellipse_pts(x, y, r, r, 10), "#cfd3dc", w=5, seed=300 + k))
    o.append(shape(cloud_pts(C_SM[0], C_SM[1], 128, 104, 8, 31, .01, t), "#cfd3dc", w=7, seed=301))
    o.append(G(bulb("round", "#9aa0a8", 0.0, seed=5, filament=True, base_col="#868d95"), C_SM[0], C_SM[1] + 8, .82, 6 * osc(t, .4)))
    # большое облако справа
    bub = [(C_BIG[0] - 100, C_BIG[1] + 300, 26), (C_BIG[0] - 150, C_BIG[1] + 350, 16), (C_BIG[0] - 185, C_BIG[1] + 385, 10)]
    for k, (x, y, r) in enumerate(bub):
        o.append(shape(ellipse_pts(x, y + 4 * osc(t, 1.2, k), r, r, 10), "#ffffff", w=6, seed=310 + k))
    cpts = cloud_pts(C_BIG[0], C_BIG[1], 345 * puff * (1 + .03 * pre), 270 * puff * (1 + .03 * pre), 11, 41, .015, t)
    o.append(shape(cpts, "#fffdf7", blob(cloud_pts(C_BIG[0] + 40, C_BIG[1] + 100, 300, 180, 9, 7), "#eef1fb"), w=8, seed=311))
    # идеи: до «необычнее» толкутся в облаке, потом вылетают веером и кружатся
    starts = [(-150, -60), (130, -80), (-60, 110), (150, 90)]
    for k, (fn, end, sc, spin) in enumerate(IDEAS):
        tk = T_NEO + .06 * k
        u = spring(max(0.0, t - tk), 1.6, 5.0) if t > tk else 0.0
        jig = (1 - clamp(u)) * 10
        sx0, sy0 = starts[k]
        x = C_BIG[0] + sx0 + (end[0] - sx0) * u + jig * osc(t, 3.1, k)
        y = C_BIG[1] + sy0 + (end[1] - sy0) * u + jig * osc(t, 2.7, k + 1)
        # после вылета — плавное кружение по своей маленькой орбите
        after = max(0.0, t - tk - .3)
        x += 26 * math.sin(after * 3 + k) * clamp(after * 3)
        y += 20 * math.cos(after * 3 + k) * clamp(after * 3)
        s = sc * (.55 + .45 * clamp(u)) * (1 + .03 * pre * osc(t, 4, k))
        rot = spin * max(0.0, t - tk) + 10 * osc(t, .7, k)
        if t > tk:
            # короткие штрихи вылета позади (сплошные)
            ud = clamp((t - tk) / .25) * (1 - smooth(tk + .25, tk + .55, t))
            if ud > 0:
                dx, dy = end[0] - sx0, end[1] - sy0
                L = math.hypot(dx, dy)
                ux, uy = dx / L, dy / L
                for j in (-1, 0, 1):
                    p0 = (x - ux * 90 + uy * 26 * j, y - uy * 90 - ux * 26 * j)
                    p1 = (p0[0] - ux * 110 * ud, p0[1] - uy * 110 * ud)
                    o.append(line([p0, p1], 9, "#ffffff", taper=.6, wmin=.3, seed=400 + k * 3 + j))
        o.append(G(fn(t, seed=50 + 13 * k), x, y, s, rot))
    # камера: наезд вглубь облака, поворот 2°
    z = .95 + .17 * ease_in(clamp((t - 25.7) / 2.3), 1.6) + .04 * math.exp(-6 * max(0.0, burst)) * (burst > 0)
    set_ink(z)
    cam = lib.cam(550 + 20 * ease_io(clamp((t - 25.7) / 2.3)), 860 - 70 * ease_io(clamp((t - 25.7) / 2.3)), z,
                  -2.0 * ease_io(clamp((t - 25.7) / 2.3)) + 2 * decay(t, T_NEO, 7, 6))
    return f'<g transform="{cam}">{"".join(o)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    fn = {"s06": frame06, "s07": frame07, "s11": frame11}[sid]
    return lib.svg(fn(t))
