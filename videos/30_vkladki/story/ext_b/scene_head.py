"""Рилс 30, s04 «Почта, отчёт, чат, видео, снова отчёт, и так по кругу» (6.9–8.8; клип 6.7–9.0).
Голова и плечи Димы (горчичное худи, руки в кармане) на тёмно-синем фоне мозга; вокруг головы по наклонному кольцу
летят значки дел: конверт, документ, чат, ▶, снова документ. Дальняя половина кольца — за головой, ближняя — перед.
Зрачки следят за значком, что пролетает спереди; на «отчёт» (6.96) документ вспыхивает и толкает голову; на «по кругу»
(8.08) кольцо разгоняется со шлейфами, глаза становятся спиралями и крутятся, голова кружится. Всё — функция t."""
import math

import numpy as np

import dima
import icons
import lib
import scene_brain as sb
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

REPORT2 = 6.96     # «отчёт» (снова)
ROUND = 8.08       # «кругу»
_ST = {}

K = 4.2                       # масштаб Димы относительно его мировых единиц
HIP = (455.0, 1660.0)          # таз (за кадром не виден: низ — худи)
dima.LWK = 0.72                # крупный план — тушь тоньше, чем у мелкого героя в парке


# ───────────────────────── значки
def chat(sd=0):
    s = shape([(-46, -36, 1), (22, -36, 1), (22, 10, 1), (-14, 10, 1), (-30, 26, 1), (-28, 10, 1), (-46, 10, 1)], "#5aa0e6",
              blob([(-46, -6), (22, -6), (22, 10), (-46, 10)], "#3f82c8", .8), w=3.4, seed=sd + 1)
    s += shape([(-6, -14, 1), (46, -14, 1), (46, 28, 1), (34, 28, 1), (38, 42, 1), (20, 28, 1), (-6, 28, 1)], "#fbfaf6",
               blob([(-6, 14), (46, 14), (46, 28), (-6, 28)], "#e3dccb", .8), w=3.4, seed=sd + 2)
    for k in range(3):
        s += f'<circle cx="{8 + k * 13}" cy="7" r="4.6" fill="{INK}"/>'
    return s


def play(sd=0):
    s = shape(rect_pts(-46, -32, 46, 32, 14), "#e8453c", blob(rect_pts(-46, 8, 46, 32, 14), "#c13128", .85) +
              blob(rect_pts(-38, -26, 10, -16, 5), "#ff8a80", .8), w=3.6, seed=sd + 1)
    s += shape([(-12, -17, 1), (20, 0, 1), (-12, 17, 1)], "#ffffff", "", w=2.8, seed=sd + 2)
    return s


ICONS = [icons.envelope, icons.report, chat, play, icons.report]


def tile(fn, sd, flash=0.0):
    """Значок на белой карточке-вкладке со скруглёнными углами (как фавикон вкладки, но крупно)."""
    col = mix("#fbf7ee", "#fff6c4", flash)
    s = f'<path d="{lib.fill_d(rect_pts(-70, -62, 76, 70, 20))}" fill="#0d1230" opacity=".45"/>'
    s += shape(rect_pts(-74, -70, 70, 62, 20), col, blob(rect_pts(-74, 34, 70, 62, 20), mix("#e7dfcc", "#ffe58a", flash), .9),
               w=4.4, seed=sd)
    s += f'<g transform="translate(-2 -4) scale(1.05)">{fn(sd + 10)}</g>'
    return s


# ───────────────────────── кольцо
CX, CY = 545.0, 318.0          # центр кольца (на уровне лба)
RX, RY, TILT = 420.0, 104.0, -7.0


def phase(t):
    """Угол кольца: ровно до «кругу», потом разгон (интеграл скорости)."""
    w0, w1 = 2.3, 10.5
    a = w0 * (t - 6.7)
    if t > ROUND - 0.08:
        e = t - (ROUND - 0.08)
        ramp = 0.35
        # скорость растёт от w0 до w1 за ramp (ease-in), дальше постоянна
        if e < ramp:
            a += (w1 - w0) * (e ** 3) / (3 * ramp ** 2)
        else:
            a += (w1 - w0) * (ramp / 3 + (e - ramp))
    return a


def ring_pos(ang):
    x, y = RX * math.cos(ang), RY * math.sin(ang)
    c, s = math.cos(math.radians(TILT)), math.sin(math.radians(TILT))
    return CX + x * c - y * s, CY + x * s + y * c, math.sin(ang)   # depth: +1 — ближе к зрителю


def speed(t):
    return 2.3 + (10.5 - 2.3) * smooth(ROUND - 0.08, ROUND + 0.3, t)


def ring_items(t):
    """Возвращает (за головой, перед головой)."""
    back, front = [], []
    a0 = phase(t)
    sp = speed(t)
    n = len(ICONS)
    for k, fn in enumerate(ICONS):
        ang = a0 + 2 * math.pi * k / n
        x, y, dep = ring_pos(ang)
        sc = 0.80 + 0.26 * dep
        # «отчёт» вспыхивает и подпрыгивает (второй документ, k=4) на REPORT2
        flash = 0.0
        pop = 0.0
        if k == 4:
            e = t - REPORT2
            if e > -0.05:
                flash = math.exp(-max(e, 0) * 4.5) * smooth(-0.05, 0.03, e)
                pop = 0.28 * math.exp(-max(e, 0) * 6) * math.sin(max(e, 0) * 22 + 0.6) * (e > 0) + 0.18 * flash
        rot = 10 * math.cos(ang) + 4 * math.sin(t * 3 + k)
        s = ""
        # шлейф при разгоне — штрихи по кольцу позади значка
        if sp > 4:
            tr = clamp((sp - 4) / 6)
            for j in range(3):
                pts = []
                for i in range(7):
                    aa = ang - 0.06 - i * 0.055 * (1 + j * 0.2)
                    px, py, _ = ring_pos(aa)
                    pts.append((px, py + (j - 1) * 26 * sc))
                s += line(pts, 9 * sc * tr, "#e9eeff", taper=.9, wmin=.1, seed=700 + k * 5 + j)
        s += f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc * (1 + pop))})">{tile(fn, 600 + k * 20, flash)}</g>'
        if flash > 0.05:
            for j in range(8):
                aa = j * math.pi / 4 + 0.2
                u = 1 - flash
                r0 = 95 * sc + 70 * u
                s += line([(x + math.cos(aa) * r0, y + math.sin(aa) * r0), (x + math.cos(aa) * (r0 + 34 * flash), y + math.sin(aa) * (r0 + 34 * flash))],
                          7, "#ffe27a", taper=.5, seed=760 + j)
        (front if dep > 0 else back).append((dep, s))
    back.sort(key=lambda d: d[0])
    front.sort(key=lambda d: d[0])
    return "".join(s for _, s in back), "".join(s for _, s in front)


def orbit_line(t, front):
    """Тонкая орбита-след (светлая), половина за головой, половина спереди."""
    pts = []
    rng = np.linspace(0, math.pi, 40) if front else np.linspace(math.pi, 2 * math.pi, 40)
    for a in rng:
        x, y, _ = ring_pos(a)
        pts.append((x, y))
    k = smooth(ROUND - 0.1, ROUND + 0.25, t)
    return line(pts, 3.2 + 3 * k, mix("#6b7cc0", "#b9c6ff", k), taper=.3, wmin=.4, seed=790 + front)


# ───────────────────────── Дима
def look_at(t):
    """Куда смотрят зрачки: за ближайшим к зрителю значком."""
    a0 = phase(t)
    n = len(ICONS)
    best = max(range(n), key=lambda k: math.sin(a0 + 2 * math.pi * k / n))
    x, y, _ = ring_pos(a0 + 2 * math.pi * best / n)
    lx = clamp((x - 600) / 380, -1, 1) * 0.42
    ly = -0.30 + 0.1 * clamp((y - 330) / 120, -1, 1)
    return lx, ly


def dima_bust(t):
    e = t - ROUND
    dizzy = smooth(-0.1, 0.25, e)
    sway = (2.2 * math.sin(t * 2.3) * (1 - dizzy) + 5.5 * math.sin(max(e, 0) * 9.0) * dizzy)
    jolt = 0.0
    er = t - REPORT2
    if er > 0:
        jolt = -6 * math.exp(-er * 6) * math.sin(er * 18)
    lx, ly = look_at(t)
    expr = {"lid": 0.62 + 0.3 * dizzy, "look": (lx, ly), "brows": "worry" if dizzy < .5 else "up",
            "mouth": "tired" if dizzy < .5 else "gape", "hair": 6 * math.sin(t * 7) * dizzy + (4 * math.exp(-max(er, 0) * 5) if er > 0 else 0)}
    if dizzy > 0:
        expr["spiral"] = (-(t - ROUND) * 15.0, back_out(clamp((e + 0.06) / 0.2), 2.2))
    hx, hy = HIP
    pose = {"hip": (0.0, 0.0), "lean": math.radians(-2 + 1.2 * math.sin(t * 1.7)), "head_ang": math.radians(sway + jolt - 3),
            "feet": {"n": ((40, 260), 0.0), "f": ((-20, 260), 0.0)},
            "arms": {"n": ("ik", (60, -40), -1), "f": ("ik", (40, -46), -1)},
            "hands": {"n": "none", "f": "none"}, "expr": expr, "hood": 0.0, "strings": (4 * math.sin(t * 3.1), 0)}
    g, _ = dima.draw(pose)
    breath = 1 + 0.008 * math.sin(t * 2.4)
    return f'<g transform="translate({f(hx)} {f(hy)}) scale({f(K)} {f(K * breath)})">{g}</g>'


def stars(t):
    """На разгоне — звёздочки головокружения над макушкой (не сразу, через 0.15 с)."""
    e = t - ROUND - 0.12
    if e < 0:
        return ""
    s = []
    k = back_out(clamp(e / 0.25), 2)
    for j in range(3):
        a = e * 7 + j * 2 * math.pi / 3
        x = 560 + 170 * math.cos(a)
        y = 150 + 34 * math.sin(a)
        sc = k * (0.8 + 0.25 * math.sin(a))
        pts = []
        for i in range(10):
            r = 26 if i % 2 == 0 else 11
            aa = -math.pi / 2 + i * math.pi / 5
            pts.append((x + r * sc * math.cos(aa), y + r * sc * math.sin(aa), 1))
        s.append(shape(pts, "#ffe27a", "", w=3.0, seed=880 + j))
    return "".join(s)


def background():
    s = []
    lib.lin_grad([(0, "#1f2747", 1), (.55, "#2c3a66", 1), (1, "#33457a", 1)], 0, 0, 0, 1, gid="gWallH")
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#gWallH)"/>')
    lib.rad_grad([(0, "#6276b8", .95), (.55, "#40538d", .4), (1, "#40538d", 0)], 520, 600, 720, 640, gid="gSpotH")
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#gSpotH)"/>')
    return "".join(s)


def s04(t):
    back, front = ring_items(t)
    art = orbit_line(t, False) + back + dima_bust(t) + orbit_line(t, True) + front + stars(t)
    u = clamp((t - 6.7) / 2.3)
    e = t - ROUND
    kick = 0.035 * math.exp(-max(e, 0) * 5) * (e > 0) * smooth(0, 0.08, e)
    shake = 5 * math.exp(-max(e, 0) * 4) * math.sin(e * 47) * (e > 0)
    cm = cam(540 + shake, 800 - 30 * u, 1.0 + 0.07 * ease_io(u) + kick + 0.05 * (1 - ease_out(clamp((t - 6.7) / 0.5))),
             -1.2 + 2.4 * u + 1.5 * smooth(0, 0.6, e) * math.sin(max(e, 0) * 6))
    return art, cm


def build_static():
    if _ST:
        return
    _ST["bg"] = background()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = s04(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{_ST["bg"]}{sb.dust(t)}{art}</g>')
