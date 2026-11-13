"""Сцена cat рилса 32 (s05, 7.9–9.3): ночь, край стола Димы у настольной лампы; кот рилсов 24–29 (cat.py: ЛЕВОЕ от
зрителя ухо загнуто, зелёные глаза, по две оранжевые полоски на щеках, огонёк на кончике хвоста-завитка) крупно сидит
на краю стола и смотрит в камеру; моргает; на «почему» (8.32) наклоняет голову с перелётом, ухо дёргается, огонёк
вспыхивает и колышется. Вокруг лампы кружит мотылёк, в луче — пылинки. Камера — лёгкий наезд. Всё — от общего t."""
import math

import numpy as np

import cat
import lib
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
WHY = 8.32            # «почему»
TOP_BACK, TOP_FRONT, EDGE = 1000, 1190, 1236     # дальний край столешницы, передний край, низ кромки
CAT_X, CAT_Y, CAT_S = 650, 1168, 1.75
LAMP_BASE = (120, 1080)
SHADE = (250, 540)    # центр абажура


def wall():
    s = []
    g = lin_grad([(0, "#1d2342", 1), (.6, "#2a3058", 1), (1, "#353a66", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{TOP_BACK + 600}" fill="url(#{g})"/>')
    # обои: мягкие вертикальные полосы с ромбиками
    for k, x in enumerate(range(-560, W + 600, 110)):
        s.append(f'<rect x="{x}" y="-600" width="38" height="{TOP_BACK + 600}" fill="#252b52" opacity=".9"/>')
        for j, y in enumerate(range(-520, TOP_BACK, 150)):
            yy = y + (k % 2) * 75
            s.append(blob([(x + 74, yy - 9), (x + 82, yy), (x + 74, yy + 9), (x + 66, yy)], "#3a4278", .7))
    # окно справа: ночное небо, луна, рама
    wx0, wy0, wx1, wy1 = 780, 140, 1260, 760
    sky = lin_grad([(0, "#0f1838", 1), (1, "#2c3a74", 1)], 0, 0, 0, 1)
    inner = f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="url(#{sky})"/>'
    inner += shape(ellipse_pts(1010, 300, 46, 46, 20), "#fff3c4", blob(ellipse_pts(1024, 314, 34, 34, 14), "#f2dc9a", .8), w=3.4, seed=31)
    rs = np.random.RandomState(5)
    for k in range(14):
        x, y = rs.uniform(wx0 + 20, wx1 - 20), rs.uniform(wy0 + 20, wy1 - 200)
        inner += f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rs.uniform(1.6, 3.2))}" fill="#e8ecff" opacity=".8"/>'
    # силуэты крыш напротив
    roof = [(wx0, wy1), (wx0, 600), (860, 600), (860, 560), (940, 520, 1), (1020, 560), (1020, 640), (1140, 640), (1140, 580),
            (wx1, 580), (wx1, wy1)]
    inner += blob(roof, "#151b36")
    for k, (x, y) in enumerate([(890, 610), (1060, 670), (1180, 610)]):
        inner += blob(rect_pts(x, y, x + 26, y + 30, 3), "#ffcf6a", .9)
    s.append(shape([(wx0, wy0, 1), (wx1, wy0, 1), (wx1, wy1, 1), (wx0, wy1, 1)], "#0f1838", inner, w=5, seed=32))
    s.append(shape(rect_pts(wx0 - 22, wy1 - 6, wx1 + 40, wy1 + 26, 6), "#3e3a5e", blob(rect_pts(wx0 - 22, wy1 + 10, wx1 + 40, wy1 + 26), "#2b2846"),
                   w=4.4, seed=33))
    s.append(shape(rect_pts(1010, wy0, 1030, wy1), "#3e3a5e", "", w=3.6, seed=34))
    s.append(shape(rect_pts(wx0, 430, wx1, 450), "#3e3a5e", "", w=3.6, seed=35))
    # пробковая доска со стикерами слева вверху (пустые, без букв)
    bx0, by0, bx1, by1 = -120, 120, 300, 380
    cork = blob(rect_pts(bx0 + 220, by0, bx1, by1), "#8a5f3c", .6)
    for k, (x, y, c, a) in enumerate([(-40, 180, "#ffd84a", -6), (90, 220, "#8fd3ff", 5), (200, 160, "#ff9ab0", -3)]):
        pts = [(x - 46, y - 40, 1), (x + 46, y - 40, 1), (x + 46, y + 40, 1), (x - 46, y + 40, 1)]
        cork += f'<g transform="rotate({a} {x} {y})">' + shape(pts, c, blob([(x + 10, y - 40), (x + 46, y - 40), (x + 46, y + 40), (x + 20, y + 40)],
                                                                          lib.mul(c, (.88, .86, .9)), .8), w=3, seed=40 + k)
        cork += shape(ellipse_pts(x, y - 30, 7, 7, 8), "#e2543f", "", w=2.2, seed=50 + k) + "</g>"
    s.append(shape(rect_pts(bx0, by0, bx1, by1, 6), "#a87a50", cork, w=5, seed=36))
    return "".join(s)


def table():
    s = []
    top = [(-600, TOP_BACK, 1), (W + 600, TOP_BACK, 1), (W + 600, TOP_FRONT, 1), (-600, TOP_FRONT, 1)]
    inner = ""
    for k in range(6):
        y = TOP_BACK + 22 + k * 30
        inner += line([(-600, y), (W + 600, y + 3)], 2.2, "#7a4a2e", taper=.1, wmin=.6, seed=60 + k, op=.55)
    inner += blob([(-600, TOP_BACK), (W + 600, TOP_BACK), (W + 600, TOP_BACK + 16), (-600, TOP_BACK + 16)], "#6a3f26", .6)
    s.append(shape(top, "#a8693f", inner, w=4.6, seed=61))
    s.append(shape([(-600, TOP_FRONT, 1), (W + 600, TOP_FRONT, 1), (W + 600, EDGE, 1), (-600, EDGE, 1)], "#7f4b2b",
                   blob([(-600, EDGE - 12), (W + 600, EDGE - 12), (W + 600, EDGE), (-600, EDGE)], "#5e3720"), w=4.6, seed=62))
    s.append(f'<rect x="-600" y="{EDGE}" width="{W + 1200}" height="1200" fill="#141830"/>')
    # лист бумаги и кружка на столе (слева от кота)
    pap = [(330, 1120, 1), (500, 1108, 1), (540, 1180, 1), (350, 1186, 1)]
    s.append(shape(pap, "#f7f3e6", blob([(440, 1110), (500, 1108), (540, 1180), (470, 1183)], "#e2dccb", .7), w=3.4, seed=63))
    s.append(line([(360, 1150), (520, 1130)], 7, "#e8b23a", taper=.05, wmin=.95, seed=64))
    s.append(line([(520, 1130), (536, 1128)], 5, "#3a2a20", taper=.8, seed=65))
    return "".join(s)


def lamp_back():
    """Ножка и плечи лампы (абажур — отдельно, поверх света)."""
    s = []
    bx, by = LAMP_BASE
    s.append(blob(ellipse_pts(bx + 10, by + 30, 120, 18, 14), "#2a1a10", .45, blur(6)))
    s.append(shape(ellipse_pts(bx, by + 14, 96, 26, 18), "#2f5d57", blob(ellipse_pts(bx + 20, by + 22, 80, 16, 12), "#1f413d"), w=4.4, seed=70))
    s.append(shape(ellipse_pts(bx, by + 2, 82, 20, 18), "#3f7a72", blob(ellipse_pts(bx - 30, by - 4, 30, 6, 8), "#7fb8ae", .8), w=4, seed=71))
    elbow = (40, 760)
    s.append(line([(bx, by), elbow], 16, "#2f5d57", taper=.05, wmin=.95, seed=72))
    s.append(line([(bx + 4, by - 6), (elbow[0] + 4, elbow[1] + 4)], 5, "#7fb8ae", taper=.2, wmin=.6, seed=73, op=.8))
    s.append(line([elbow, (SHADE[0] - 70, SHADE[1] - 40)], 16, "#2f5d57", taper=.05, wmin=.95, seed=74))
    s.append(shape(ellipse_pts(elbow[0], elbow[1], 18, 18, 12), "#3f7a72", "", w=3.6, seed=75))
    return "".join(s)


def lamp_shade(on):
    x, y = SHADE
    s = []
    rot = 32
    pts = [(-70, -50), (40, -60, 1), (110, 40, 1), (-110, 60, 1), (-96, -20)]
    P = lib.T(pts, x, y, 1.0, rot)
    inner = blob(lib.T([(10, -60), (40, -60), (110, 40), (30, 50)], x, y, 1.0, rot), "#1f413d", .8)
    inner += blob(lib.T([(-60, -40), (-30, -50), (-80, 20), (-100, 30)], x, y, 1.0, rot), "#7fb8ae", .7)
    s.append(shape(P, "#3f7a72", inner, w=5, seed=80))
    # открытый низ абажура — светится
    rim = lib.T(ellipse_pts(0, 50, 110, 22, 18), x, y, 1.0, rot)
    s.append(shape(rim, mix("#ffe9a8", "#fff6d6", on), blob(lib.T(ellipse_pts(0, 50, 60, 10, 12), x, y, 1.0, rot), "#ffffff", .9), w=4, seed=81))
    return "".join(s)


def light(t):
    """Тёплый конус лампы на стол и кота + пятно на стене; дрожит чуть-чуть (нить)."""
    fl = 1 + 0.03 * math.sin(t * 17) * math.sin(t * 5.3)
    s = []
    g = rad_grad([(0, "#ffd890", .55 * fl), (.5, "#ffb860", .2 * fl), (1, "#ffb860", 0)], 430, 1080, 560, 300)
    s.append(f'<rect x="-600" y="600" width="{W + 1200}" height="1000" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    g2 = rad_grad([(0, "#fff0c0", .45 * fl), (1, "#fff0c0", 0)], 300, 640, 260, 200)
    s.append(f'<rect x="0" y="300" width="800" height="600" fill="url(#{g2})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def dust(t):
    rs = np.random.RandomState(9)
    s = []
    for k in range(18):
        x0, y0 = rs.uniform(150, 440), rs.uniform(640, 1100)
        ph, r = rs.uniform(0, 6.28), rs.uniform(2.2, 4.2)
        x = x0 + 26 * math.sin(t * 0.7 + ph)
        y = y0 - 22 * (t - 7.7) + 10 * math.sin(t * 1.1 + ph)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#fff2c8" opacity="{.35 + .2 * math.sin(t * 3 + ph):.3f}"/>')
    return "".join(s)


def moth(t):
    """Мотылёк кружит у абажура: тельце и два крыла, крылья машут."""
    a = t * 3.1
    x = SHADE[0] - 10 + 120 * math.cos(a)
    y = SHADE[1] - 40 + 70 * math.sin(a * 1.3)
    flap = abs(math.sin(t * 38))
    s = []
    for side in (-1, 1):
        wing = [(0, 0), (side * 22, -14 - 8 * flap), (side * 30, 2), (side * 14, 10)]
        s.append(shape([(x + px, y + py * (0.4 + 0.6 * flap)) for px, py in wing], "#e9dcc0",
                       blob([(x + side * 12, y), (x + side * 24, y - 4), (x + side * 20, y + 6)], "#c8b896", .9), w=2.2, seed=90 + side))
    s.append(shape(ellipse_pts(x, y + 2, 5, 11, 8), "#6a5a48", "", w=2, seed=93))
    return "".join(s)


def cat_state(t):
    """Наклон головы на «почему»: замах в обратную сторону, наклон −13° с перелётом, держит; ухо дёргается."""
    e = t - WHY
    tilt = 1.5 * math.sin(t * 1.7)
    if e > -0.12:
        pre = 2.5 * math.sin(math.pi * clamp((e + 0.12) / 0.12)) if e < 0 else 0.0
        tilt += pre - 13 * spring(max(e, 0), 2.2, 4.5)
    blink = 0.0
    for b in (7.86, 9.05):
        u = (t - b) / 0.16
        if 0 < u < 1:
            blink = max(blink, math.sin(math.pi * u))
    blink = min(1.0, blink * 1.25)
    look = (0.15 * math.sin(t * 0.9), -0.15 + 0.1 * math.sin(t * 1.3))
    if e > 0:
        look = (look[0] - 0.25 * smooth(0, 0.2, e), look[1] - 0.15 * smooth(0, 0.2, e))
    flick = 0.0
    for c in (WHY + 0.04, 8.95):
        ee = t - c
        if 0 <= ee < 0.5:
            flick += -16 * math.exp(-ee * 9) * math.sin(ee * 34)
    tail = 7 * math.sin(t * 2.1) + 3 * math.sin(t * 3.7 + 1)
    if e > 0:
        tail += 9 * math.exp(-e * 3) * math.sin(e * 12)
    return dict(look=look, blink=blink, tilt=tilt, tail=tail, flick=flick)


def frame(sid, t):
    if not _ST:
        _ST["wall"] = wall()
        _ST["table"] = table()
        _ST["lamp"] = lamp_back()
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    st = cat_state(t)
    e = t - WHY
    # лёгкий подскок тела на наклоне, дыхание — внутри draw
    hop = -10 * math.sin(math.pi * clamp(e / 0.22)) if 0 < e < 0.22 else 0.0
    s = [_ST["wall"], _ST["lamp"], _ST["table"]]
    # свет огонька на стене
    fx, fy = cat.flame_world(CAT_X, CAT_Y + hop, CAT_S, st["tail"])
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3) + (0.35 * math.exp(-e * 3) if e > 0 else 0)
    g = rad_grad([(0, "#ffb050", .42 * fl), (1, "#ffb050", 0)], fx, fy, 300, 300)
    s.append(f'<rect x="{f(fx - 320)}" y="{f(fy - 320)}" width="640" height="640" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(light(t))
    s.append(blob(ellipse_pts(CAT_X + 40, CAT_Y + 6, 270, 26, 18), "#3a1e0c", .35, blur(10)))
    s.append(cat.draw(CAT_X, CAT_Y + hop, CAT_S, t, paw=None, shadow=False, **st))
    s.append(lamp_shade(1.0))
    s.append(dust(t))
    s.append(moth(t))
    # камера: лёгкий наезд с первого кадра, толчок на «почему»
    u = clamp((t - 7.7) / 1.8)
    sc = 1.2 + 0.08 * (0.35 * u + 0.65 * ease_io(u))
    cx, cy = 610 + 15 * u, 905 - 12 * u
    if e > 0:
        k = math.exp(-e * 7)
        sc *= 1 + 0.035 * k * math.sin(min(e * 14, math.pi))
    rot = -0.6 + 0.9 * u
    return svg(f'<rect width="{W}" height="{H}" fill="#141830"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')
