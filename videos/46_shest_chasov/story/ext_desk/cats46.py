"""Сцены cat рилса 46: s05 (7.3–9.9, кот на подоконнике в полдень, на «почему» наклоняет голову, над ним «?») и s16 (35.3–38.9, кот на
кровати в темноте, медленно моргает, на «Напиши кот» рядом надпись «КОТ»). Кот — ext/cat.py (как look/hero.png: ЛЕВОЕ ухо загнуто)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat  # noqa: E402
import lib  # noqa: E402
from lib import (INK, W, H, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring,
                 svg)  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
T_POCHEMU = WORDS[21]["start"]       # 7.68
T_NAPISHI = WORDS[98]["start"]       # 35.36
T_KOT = WORDS[99]["start"]           # 35.84
_ST = {}


def back_ease(u, k=2.0):
    u = clamp(u)
    return 1 + (k + 1) * (u - 1) ** 3 + k * (u - 1) ** 2


def pulse_blink(t, tb, dur=.2):
    u = (t - tb) / dur
    return math.sin(math.pi * u) if 0 < u < 1 else 0.0


# ═════════════════════════ s05: подоконник днём ═════════════════════════
SILL_BACK, SILL_FRONT, SILL_EDGE = 1000, 1190, 1236
CAT_X, CAT_Y, CAT_S = 650, 1168, 1.75


def day_wall(t):
    s = []
    g = lin_grad([(0, "#f1e6d2", 1), (1, "#e6d8bf", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{SILL_BACK + 700}" fill="url(#{g})"/>')
    wx0, wy0, wx1, wy1 = 90, 60, 990, SILL_BACK - 20
    sky = lin_grad([(0, "#5fb0ea", 1), (.6, "#a6dcf6", 1), (1, "#dcf2fb", 1)], 0, 0, 0, 1)
    inner = f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="url(#{sky})"/>'
    sg = rad_grad([(0, "#fff8c8", .9), (.4, "#fff4b0", .35), (1, "#fff4b0", 0)], 800, 240, 230, 230)
    inner += f'<rect x="560" y="0" width="480" height="480" fill="url(#{sg})"/>' + blob(ellipse_pts(800, 240, 56, 56, 20), "#fff6b8")
    for k, (cx, cy, sc) in enumerate([(150, 200, 1.5), (520, 380, 1.1), (330, 90, .9)]):
        x = wx0 + (cx + 14 * t + 420 * k) % 1100 - 100
        inner += (blob(ellipse_pts(x, wy0 + cy, 90 * sc, 32 * sc, 14), "#ffffff", .96) + blob(ellipse_pts(x - 44 * sc, wy0 + cy - 18 * sc, 46 * sc, 30 * sc, 12), "#ffffff", .96) +
                  blob(ellipse_pts(x + 40 * sc, wy0 + cy - 22 * sc, 50 * sc, 34 * sc, 12), "#ffffff", .96))
    far = [(wx0, 700), (200, 700), (200, 640), (330, 640), (330, 720), (470, 720), (470, 600), (600, 600), (600, 690), (760, 690), (760, 650), (wx1, 650), (wx1, wy1), (wx0, wy1)]
    inner += blob(far, "#a9bdd6")
    for i, (x, y, w, col) in enumerate([(wx0 + 20, 760, 190, "#b9c9de"), (wx0 + 260, 810, 170, "#9db3d0"), (wx0 + 520, 740, 200, "#aabfd9"), (wx0 + 760, 800, 130, "#b9c9de")]):
        inner += shape(rect_pts(x, y, x + w, wy1 + 30), col, blob(rect_pts(x + w * .72, y, x + w, wy1 + 30), mix(col, "#000000", .12), .8), w=3.4, seed=3300 + i)
        rs = np.random.RandomState(40 + i)
        for r in range(8):
            for c in range(int(w // 44)):
                wx, wy = x + 14 + c * 44, y + 20 + r * 50
                if wy < wy1 - 20:
                    inner += blob(rect_pts(wx, wy, wx + 22, wy + 30), "#f2f8fd" if rs.uniform() < .5 else "#6f8fb8")
    fr = "#f4ecdc"
    inner += blob(rect_pts((wx0 + wx1) / 2 - 12, wy0, (wx0 + wx1) / 2 + 12, wy1), fr) + blob(rect_pts(wx0, 430, wx1, 454), fr)
    s.append(shape(rect_pts(wx0 - 26, wy0 - 26, wx1 + 26, wy1 + 20, 8), fr, blob(rect_pts(wx1, wy0 - 26, wx1 + 26, wy1 + 20), "#d4c8b0", .9), w=5, seed=3310))
    s.append(shape(rect_pts(wx0, wy0, wx1, wy1, 4), "#a6dcf6", inner, w=4.4, seed=3311))
    # шторы по бокам
    for k, (x0, x1) in enumerate([(-80, 70), (1010, 1160)]):
        pts = [(x0, -40), (x1, -40), (x1 - 10 * (1 - 2 * k), 500), (x1 + 6 * (1 - 2 * k), SILL_BACK + 30), (x0 + 6, SILL_BACK + 30), (x0 - 4, 480)]
        inn = "".join(line([(x0 + 24 + q * 36, -20), (x0 + 28 + q * 36, 520), (x0 + 36 + q * 36, SILL_BACK + 10)], 2.6, "#8f4540", seed=3320 + k * 5 + q, op=.8) for q in range(3))
        s.append(shape(pts, "#b95a52", inn, w=4.4, seed=3319 + k))
    s.append(shape(rect_pts(-120, -50, 1200, -30, 6), "#3a2a22", "", w=3, seed=3330))
    return "".join(s)


def sill():
    s = []
    top = [(-600, SILL_BACK, 1), (W + 600, SILL_BACK, 1), (W + 600, SILL_FRONT, 1), (-600, SILL_FRONT, 1)]
    inner = blob([(-600, SILL_BACK), (W + 600, SILL_BACK), (W + 600, SILL_BACK + 16), (-600, SILL_BACK + 16)], "#d9ccb4", .7)
    s.append(shape(top, "#f1e8d6", inner, w=4.6, seed=3340))
    s.append(shape([(-600, SILL_FRONT, 1), (W + 600, SILL_FRONT, 1), (W + 600, SILL_EDGE, 1), (-600, SILL_EDGE, 1)], "#e0d3ba",
                   blob([(-600, SILL_EDGE - 12), (W + 600, SILL_EDGE - 12), (W + 600, SILL_EDGE), (-600, SILL_EDGE)], "#c6b898"), w=4.6, seed=3341))
    s.append(f'<rect x="-600" y="{SILL_EDGE}" width="{W + 1200}" height="1400" fill="#e3d5bb"/>')
    for q in range(5):
        s.append(line([(-600, SILL_EDGE + 90 + q * 120), (W + 600, SILL_EDGE + 96 + q * 120)], 3, "#c9b995", seed=3360 + q, op=.7, taper=.1, wmin=.6))
    # горшок с растением слева
    import room
    s.append(room.pot(200, SILL_FRONT - 24, 1.5, 3350, leaves=8, col="#5f86a8"))
    return "".join(s)


def sunlight(t):
    g = rad_grad([(0, "#fff3c8", .42), (.5, "#ffe49a", .16), (1, "#ffe49a", 0)], 800, 240, 900, 900)
    return f'<rect x="-600" y="-600" width="{W + 1200}" height="2600" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def motes(t):
    rs = np.random.RandomState(9)
    o = []
    for k in range(20):
        x0, y0 = rs.uniform(150, 1000), rs.uniform(300, 1000)
        ph, r = rs.uniform(0, 6.28), rs.uniform(2.2, 4.4)
        x = x0 + 26 * math.sin(t * .7 + ph)
        y = y0 - 22 * (t - 7.2) + 10 * math.sin(t * 1.1 + ph)
        o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#ffffff" opacity="{.5 + .3 * math.sin(t * 3 + ph):.3f}"/>')
    return "".join(o)


def qmark(x, y, k, u, t):
    if u <= 0:
        return ""
    sc = k * back_ease(u, 2.4)
    wob = 6 * math.sin(t * 7) * (1 - clamp(u - 1)) if u > 1 else 0
    txt = (f'<text x="5" y="7" text-anchor="middle" font-family="IDB" font-weight="900" font-size="190" fill="{INK}" stroke="{INK}" stroke-width="22" stroke-linejoin="round">?</text>'
           f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="190" fill="#ffd84a">?</text>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({12 + wob:.1f}) scale({sc:.3f})">{txt}</g>'


def cat_state5(t):
    e = t - T_POCHEMU
    tilt = 1.5 * math.sin(t * 1.7)
    if e > -0.12:
        pre = 2.5 * math.sin(math.pi * clamp((e + 0.12) / 0.12)) if e < 0 else 0.0
        tilt += pre - 13 * spring(max(e, 0), 2.2, 4.5)
    blink = 0.0
    for b in (7.5, 9.3):
        blink = max(blink, pulse_blink(t, b, .16))
    look = (0.15 * math.sin(t * 0.9), -0.15 + 0.1 * math.sin(t * 1.3))
    if e > 0:
        look = (look[0] - 0.25 * smooth(0, 0.2, e), look[1] - 0.15 * smooth(0, 0.2, e))
    flick = 0.0
    for c in (T_POCHEMU + .04, 9.2):
        ee = t - c
        if 0 <= ee < 0.5:
            flick += -16 * math.exp(-ee * 9) * math.sin(ee * 34)
    tail = 7 * math.sin(t * 2.1) + 3 * math.sin(t * 3.7 + 1) + (9 * math.exp(-e * 3) * math.sin(e * 12) if e > 0 else 0)
    return dict(look=look, blink=blink, tilt=tilt, tail=tail, flick=flick)


def s05(t):
    st = cat_state5(t)
    e = t - T_POCHEMU
    hop = -10 * math.sin(math.pi * clamp(e / 0.22)) if 0 < e < 0.22 else 0.0
    s = [_ST["wall"], _ST["sill"], sunlight(t)]
    fx, fy = cat.flame_world(CAT_X, CAT_Y + hop, CAT_S, st["tail"])
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3) + (0.35 * math.exp(-e * 3) if e > 0 else 0)
    g = rad_grad([(0, "#ffb050", .30 * fl), (1, "#ffb050", 0)], fx, fy, 260, 260)
    s.append(blob(ellipse_pts(CAT_X + 40, CAT_Y + 6, 270, 26, 18), "#8a6a40", .35, blur(10)))
    s.append(cat.draw(CAT_X, CAT_Y + hop, CAT_S, t, paw=None, shadow=False, **st))
    s.append(f'<rect x="{f(fx - 280)}" y="{f(fy - 280)}" width="560" height="560" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(motes(t))
    s.append(qmark(CAT_X + 20, CAT_Y - 760, 1.0, (t - T_POCHEMU - .12) / .35, t))
    u = clamp((t - 7.1) / 2.8)
    sc = 1.42 + 0.07 * (0.35 * u + 0.65 * ease_io(u))
    cx, cy = 640 + 15 * u, 960 - 10 * u
    if e > 0:
        sc *= 1 + 0.035 * math.exp(-e * 7) * math.sin(min(e * 14, math.pi))
    rot = -0.6 + 0.9 * u
    return svg(f'<rect width="{W}" height="{H}" fill="#e6d8bf"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')


# ═════════════════════════ s16: кот на кровати в темноте, «КОТ» ═════════════════════════
BED_Y = 1270
C16 = (560, 1400, 1.7)


def night_bed(t):
    s = []
    g = lin_grad([(0, "#0d1330", 1), (1, "#1c2550", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{BED_Y + 600}" fill="url(#{g})"/>')
    # окно с луной слева, лунный свет
    wx0, wy0, wx1, wy1 = 60, 240, 380, 760
    inner = f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="#16204a"/>' + blob(ellipse_pts(250, 380, 46, 46, 18), "#f6ecc8")
    inner += blob(ellipse_pts(268, 366, 40, 42, 18), "#16204a")
    rs = np.random.RandomState(7)
    for k in range(12):
        inner += f'<circle cx="{f(rs.uniform(wx0 + 10, wx1 - 10))}" cy="{f(rs.uniform(wy0 + 20, wy0 + 340))}" r="{f(rs.uniform(1.6, 3.4) * (.8 + .2 * math.sin(t * 3 + k)))}" fill="#f3ead0"/>'
    inner += blob(rect_pts(wx0, 640, wx1, wy1), "#10173a")
    inner += blob(rect_pts(210, wy0, 230, wy1), "#d7cdb4") + blob(rect_pts(wx0, 470, wx1, 490), "#d7cdb4")
    s.append(shape(rect_pts(wx0 - 20, wy0 - 20, wx1 + 20, wy1 + 20, 6), "#c9bfa6", "", w=4.4, seed=3410))
    s.append(shape(rect_pts(wx0, wy0, wx1, wy1, 4), "#16204a", inner, w=4, seed=3411))
    beam = [(wx0, wy1), (wx1, wy1), (760, BED_Y + 20), (380, BED_Y + 20)]
    gb = lin_grad([(0, "#9fb4ff", .20), (1, "#9fb4ff", .04)], 0, 0, 0, 1)
    s.append(f'<path d="{lib.fill_d([p + (1,) for p in beam])}" fill="url(#{gb})" style="mix-blend-mode:screen" {blur(16)}/>')
    # изголовье
    s.append(shape([(-200, 600, 1), (700, 600, 1), (700, BED_Y + 40, 1), (-200, BED_Y + 40, 1)], "#4a3328",
                   blob([(-200, 600), (700, 600), (700, 650), (-200, 650)], "#35231b", .9), w=4.6, seed=3420))
    # матрас, одеяло со складками, подушка
    s.append(shape([(-600, BED_Y, 1), (W + 600, BED_Y, 1), (W + 600, 2600, 1), (-600, 2600, 1)], "#3b4f86",
                   blob([(-600, 1620), (W + 600, 1600), (W + 600, 2600), (-600, 2600)], "#2f4070", .85), w=4.6, seed=3421))
    for q in range(6):
        y = BED_Y + 60 + q * 70
        s.append(line([(-600, y), (200, y + 14), (800, y - 8), (W + 600, y + 10)], 2.8, "#2a3a6a", seed=3430 + q, op=.8, taper=.1, wmin=.6))
    s.append(shape([(-60, 1180), (280, 1160), (400, 1230), (300, 1300), (-60, 1300)], "#e9e2d0",
                   blob([(-60, 1260), (300, 1264), (300, 1300), (-60, 1300)], "#c7bea8", .9), w=4.4, seed=3440))
    return "".join(s)


def kot_sign(x, y, k, u, t):
    """Надпись «КОТ»: вылетает с перелётом, дальше чуть качается и мерцает."""
    if u <= 0:
        return ""
    sc = k * back_ease(u, 2.4)
    rot = -7 + 2.4 * math.sin(t * 2.4)
    gl = rad_grad([(0, "#ffd84a", .45), (1, "#ffd84a", 0)], 0, 0, 360, 200)
    txt = (f'<rect x="-380" y="-220" width="760" height="440" fill="url(#{gl})" style="mix-blend-mode:screen"/>'
           f'<text x="9" y="62" text-anchor="middle" font-family="IDB" font-weight="900" font-size="230" fill="{INK}" stroke="{INK}" stroke-width="30" stroke-linejoin="round">КОТ</text>'
           f'<text x="0" y="52" text-anchor="middle" font-family="IDB" font-weight="900" font-size="230" fill="#ffd84a" stroke="{INK}" stroke-width="6" stroke-linejoin="round">КОТ</text>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sc:.3f})">{txt}</g>'


def cat_state16(t):
    look = (0.05 * math.sin(t * .8), 0.02 + .05 * math.sin(t * 1.1))
    # медленное моргание: закрывается 0.45 с, держит, открывается 0.45 с
    blink = 0.0
    for b, d in ((35.55, .9), (37.2, .9)):
        u = (t - b) / d
        if 0 < u < 1:
            blink = max(blink, min(1.0, math.sin(math.pi * u) * 1.5))
    tilt = 2.2 * math.sin(t * 1.3) + (-5 * smooth(T_NAPISHI, T_NAPISHI + .4, t))
    tail = 8 * math.sin(t * 1.9) + 3 * math.sin(t * 3.1)
    flick = 0.0
    ee = t - T_KOT
    if 0 <= ee < .5:
        flick = -14 * math.exp(-ee * 9) * math.sin(ee * 34)
    return dict(look=look, blink=blink, tilt=tilt, tail=tail, flick=flick)


def s16(t):
    st = cat_state16(t)
    x, y, k = C16
    s = [_ST["bed"]]
    fx, fy = cat.flame_world(x, y, k, st["tail"])
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    # огонёк освещает кота и одеяло: тёплое пятно под котом, холодный лунный свет сверху
    gw = rad_grad([(0, "#ffb050", .55 * fl), (.5, "#ff9a40", .18 * fl), (1, "#ff9a40", 0)], fx, fy + 40, 520, 520)
    s.append(blob(ellipse_pts(x + 40, y + 8, 300, 30, 18), "#05081a", .55, blur(10)))
    s.append(cat.draw(x, y, k, t, paw=None, shadow=False, **st))
    # ночной тон на кота: тёмно-синий multiply-слой поверх, огонёк — поверх него
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="#10173a" opacity=".38" style="mix-blend-mode:multiply"/>')
    s.append(f'<rect x="{f(fx - 540)}" y="{f(fy - 480)}" width="1080" height="1080" fill="url(#{gw})" style="mix-blend-mode:screen"/>')
    s.append(kot_sign(560, 640, 1.0, (t - T_KOT - .0) / .4, t) if t >= T_KOT else "")
    u = clamp((t - 35.1) / 3.8)
    sc = 1.3 + .10 * (.35 * u + .65 * ease_io(u))
    cx, cy = 560 + 10 * u, 1090 - 20 * u
    rot = -.5 + .8 * u
    return svg(f'<rect width="{W}" height="{H}" fill="#0d1330"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')


def frame(sid, t):
    if not _ST:
        cat.static_parts()
        lib.static_done()
        _ST["init"] = 1
    lib.dyn_begin()
    if sid == "s05":
        _ST["wall"] = day_wall(t)
        _ST["sill"] = sill()
        return s05(t)
    _ST["bed"] = night_bed(t)
    return s16(t)
