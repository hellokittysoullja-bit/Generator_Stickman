"""Сцена «аудитория» рилса 42 (s11, 19.0–21.4): «…в комнату к другим в нелепой футболке». Слева дверь аудитории
распахивается (уже идёт с первого кадра), из коридора входит студент в ярко-розовой футболке с огромным глупым
мультяшным лицом-принтом (косые глаза, язык); на «нелепой» (19.92) принт подмигивает и вспыхивает, студент смущённо
разводит руками. Справа за партами сидят студенты и пишут. Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import person
import study28 as st
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, svg)

_ST = {}
SILLY = 19.92            # «нелепой»
FLOOR = 1060
DOOR = (90, 520, 330, FLOOR)
HERO = dict(skin="#f0c4a0", hair="curly", hair_c="#d9782e", top="#ff5fa8", low="#2f3a5a", face=.6, shoes="#2a2a30")


def wall():
    s = []
    g = lin_grad([(0, "#f3e6c8", 1), (1, "#e6d2a8", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#{g})"/>')
    g2 = lin_grad([(0, "#b9824e", 1), (1, "#9a643a", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="{FLOOR}" width="{W + 1800}" height="{H + 900}" fill="url(#{g2})"/>')
    for k in range(-8, 18):
        x = 540 + k * 110
        s.append(line([(540 + (x - 540) * .4, FLOOR), (540 + (x - 540) * 2.6, H + 400)], 2.4, "#8a5a32", taper=.1, wmin=.8, seed=7000 + k, op=.7))
    s.append(blob(rect_pts(-900, FLOOR - 34, W + 900, FLOOR), "#c9a77a"))
    s.append(line([(-900, FLOOR), (W + 900, FLOOR)], 4, INK, taper=.05, wmin=.9, seed=7030))
    # доска без букв: меловые человечки и стрелка
    s.append(shape(rect_pts(450, 300, 1060, 620, 6), "#2f5a46", blob(rect_pts(450, 550, 1060, 620), "#284e3d", .6) +
                   blob([(470, 320), (640, 320), (500, 500)], "#3a6c55", .5), w=5, seed=7040))
    s.append(shape(rect_pts(436, 616, 1074, 636), "#a87c4c", "", w=3.2, seed=7041))
    for k, x in enumerate((560, 700, 840)):
        s.append(line([(x + 26 * math.cos(a), 400 + 26 * math.sin(a)) for a in np.linspace(0, 6.4, 18)], 5, "#eef4ea", taper=.1, wmin=.7, seed=7050 + k))
        s.append(line([(x, 426), (x, 500), (x - 22, 540)], 5, "#eef4ea", taper=.1, wmin=.7, seed=7055 + k))
        s.append(line([(x, 500), (x + 22, 540)], 5, "#eef4ea", taper=.1, wmin=.7, seed=7060 + k))
    s.append(line([(920, 520), (1010, 420)], 6, "#eef4ea", taper=.1, wmin=.7, seed=7065))
    s.append(line([(980, 418), (1012, 418), (1008, 450)], 6, "#eef4ea", taper=.1, wmin=.7, seed=7066))
    # часы без цифр
    s.append(shape(ellipse_pts(760, 190, 50, 50, 22), "#fbf8ee", blob(ellipse_pts(768, 198, 44, 44, 18), "#e6dfcc", .7), w=5, seed=7070))
    return "".join(s)


def corridor():
    x0, y0, x1, y1 = DOOR
    s = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#8fa7c8"/>']
    s.append(blob(rect_pts(x0, y1 - 120, x1, y1), "#6f86a8"))
    s.append(line([(x0, y1 - 120), (x1, y1 - 120)], 3, "#4e6280", seed=7101, op=.8))
    g = rad_grad([(0, "#ffffff", .55), (1, "#ffffff", 0)], (x0 + x1) / 2, y0 + 40, 200, 160)
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>')
    return "".join(s)


def door_leaf(theta):
    """Створка на петлях у ЛЕВОГО косяка, открывается в аудиторию (к нам): theta 0 — закрыта, 1 — открыта."""
    x0, y0, x1, y1 = DOOR
    a = math.radians(80 * theta)
    wv = (x1 - x0) * math.cos(a)
    grow = 0.07 * math.sin(a) * (y1 - y0)
    xr = x0 + wv
    pts = [(x0, y0, 1), (xr, y0 - grow * .5, 1), (xr, y1 + grow * .5, 1), (x0, y1, 1)]
    col = mix("#9a5f34", "#b8784a", 0.6 * math.sin(a))
    inner = ""
    if wv > 30:
        for k, (a0, b0) in enumerate([(0.1, 0.44), (0.54, 0.9)]):
            ya, yb = y0 + (y1 - y0) * a0, y0 + (y1 - y0) * b0
            inner += shape([(x0 + wv * .16, ya, 1), (xr - wv * .16, ya - grow * .3, 1), (xr - wv * .16, yb + grow * .3, 1), (x0 + wv * .16, yb, 1)],
                           lib.mul(col, (.88, .86, .86)), "", w=2.6, seed=7120 + k)
        inner += shape(ellipse_pts(xr - wv * .12, (y0 + y1) / 2 + 20, 9, 10, 10), "#e8c35a", "", w=2.4, seed=7125)
    return shape(pts, col, inner, w=4.2, seed=7126)


def door_frame():
    x0, y0, x1, y1 = DOOR
    return shape([(x0 - 22, y1, 1), (x0 - 22, y0 - 22, 1), (x1 + 22, y0 - 22, 1), (x1 + 22, y1, 1), (x1, y1, 1), (x1, y0, 1), (x0, y0, 1), (x0, y1, 1)],
                 "#f3ede1", blob(rect_pts(x1, y0 - 22, x1 + 22, y1), "#d6cdb9"), w=4.2, seed=7130)


def print_face(t):
    """Принт на груди: огромная глупая мультяшная морда (косые глаза, язык); на «нелепой» подмигивает и вспыхивает."""
    e = t - SILLY
    wink = 1.0 if 0.02 < e < 0.34 else 0.0
    pulse = 1 + (0.16 * math.exp(-e * 7) * math.cos(e * 22) if e > 0 else 0)
    flash = math.exp(-e * 3.5) if e > 0 else 0.0

    def draw(y0, sw):
        cy = y0 + 118
        r = sw * .98 * pulse
        o = []
        if flash > .02:
            g = rad_grad([(0, "#fff7a0", .9 * flash), (1, "#fff7a0", 0)], 0, cy, r * 1.4, r * 1.4)
            o.append(f'<ellipse cx="0" cy="{f(cy)}" rx="{f(r * 1.4)}" ry="{f(r * 1.4)}" fill="url(#{g})"/>')
        face = mix("#ffe14a", "#fff6b0", flash * .6)
        o.append(shape(ellipse_pts(0, cy, r, r * .95, 22), face, blob(ellipse_pts(r * .25, cy + r * .25, r * .8, r * .7, 16), "#f2c22e", .6), w=3.6, seed=7201))
        for k, (ex, px) in enumerate(((-r * .36, .5), (r * .36, -.5))):          # косые глаза
            ey = cy - r * .22
            if k == 1 and wink:
                o.append(line([(ex - r * .2, ey), (ex, ey + r * .1), (ex + r * .2, ey)], 5, seed=7210))
            else:
                o.append(shape(ellipse_pts(ex, ey, r * .24, r * .27, 14), "#ffffff",
                               f'<circle cx="{f(ex + px * r * .13)}" cy="{f(ey + r * .05)}" r="{f(r * .1)}" fill="{INK}"/>', w=3.2, seed=7211 + k))
        # рот до ушей с языком
        m = [(-r * .55, cy + r * .2), (-r * .3, cy + r * .58), (0, cy + r * .66), (r * .3, cy + r * .58), (r * .55, cy + r * .2)]
        o.append(shape(m + [(0, cy + r * .32)], "#8a2a3a",
                       shape(ellipse_pts(r * .12, cy + r * .62, r * .2, r * .18, 12), "#ff7a90", "", w=2.4, seed=7221), w=3.4, seed=7220))
        o.append(shape([(-r * .18, cy + r * .3, 1), (r * .14, cy + r * .3, 1), (r * .12, cy + r * .4), (-r * .16, cy + r * .4)], "#ffffff", "", w=2.2, seed=7222))
        o.append(line([(-r * .7, cy + r * .05), (-r * .5, cy + r * .2)], 3, "#e8a020", seed=7223))
        return "".join(o)
    return draw


def hero(t):
    """Студент: входит из коридора (19.0–19.75), останавливается, поворачивается к нам, на «нелепой» разводит руками."""
    spec = dict(HERO)
    sc = .62
    stop = 19.78
    if t < stop:
        x = 30 + 450 * ease_out(clamp((t - 19.04) / (stop - 19.04)), 1.3)
        walk = (t - 19.0) * 9.5
    else:
        x = 480.0
        walk = None
    turn = smooth_(stop - .1, stop + .15, t)
    spec["face"] = .6 * (1 - turn) + 0.05 * turn
    e = t - SILLY
    shrug = clamp(e / 0.18) * (1 - clamp((e - 1.0) / 0.3)) if e > 0 else 0.0
    pose = {"look": (0.5 * (1 - turn), 0.05), "mouth": "smile", "brow": -0.4 * shrug, "on_torso": print_face(t),
            "blink": 1.0 if 20.9 < t < 20.97 else 0.0, "curl": {"L": .3, "R": .3}}
    if walk is not None:
        pose["walk"] = walk
    else:
        pose["arms"] = {"L": (8 - 30 * shrug, -6 - 84 * shrug), "R": (-8 + 30 * shrug, 6 + 84 * shrug)}
        pose["curl"] = {"L": .1, "R": .1}
        pose["head_tilt"] = 6 * shrug + 2 * math.sin(t * 2)
    bob = -6 * abs(math.sin(walk)) if walk is not None else 3 * math.sin(t * 2.2)
    y = FLOOR + 30 + bob
    sh = blob(ellipse_pts(x, FLOOR + 32, 90, 12, 12), "#4a3a30", .35, blur(5))
    body = person.draw(spec, dict(pose, no_arms=True), x, y, sc, sd=7300)
    arms = person.draw(spec, dict(pose, only_arms=True), x, y, sc, sd=7300)
    c = lib.clip_rect(DOOR[0], -900, 3000, 3000)
    out = f'<g clip-path="url(#{c})">{sh + body + arms}</g>'
    if e > 0:                                           # вспышка-лучи вокруг принта
        out += rays(x, y - 400 * sc, e, 7400)
    return out


def smooth_(a, b, x):
    u = clamp((x - a) / (b - a))
    return u * u * (3 - 2 * u)


def rays(x, y, e, sd, r=110, n=12, dur=0.45):
    if e < 0 or e > dur:
        return ""
    u = e / dur
    s = []
    for k in range(n):
        a = k * 2 * math.pi / n + .2
        r0 = r + 90 * ease_out(u)
        L = 55 * (1 - u)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))],
                      10 * (1 - .5 * u), "#ffcf3a", taper=.5, seed=sd + k))
    return "".join(s)


ROWS = [(980, .52, [690, 930], 220), (1170, .68, [640, 960], 280)]


def desks(t, rows):
    s = []
    n = 0
    for r, (yb, sc, xs, dw) in enumerate(ROWS):
        depth = dw * .30
        floor = yb + depth + 320 * sc
        for j, x in enumerate(xs):
            if r in rows:
                spec = st.STUDENTS[(n * 3 + 2) % len(st.STUDENTS)]
                body, arms = st.student(spec, x, yb, sc, t, n * 1.9 + 1, 7500 + n * 100)
                s.append(body)
                s.append(st.desk_surface(x, yb, dw, depth, 7600 + n * 10))
                s.append(st.paper(x + dw * .02, yb + depth * .58, dw * .40, depth * .62, 4 + n, sd=n))
                s.append(arms)
                s.append(st.desk_front(x, yb, dw, depth, floor, 7650 + n * 10))
            n += 1
    return "".join(s)


def s11(t):
    theta = ease_out(clamp((t - 18.95) / 0.35), 2.4)
    th = theta + 0.04 * math.exp(-max(t - 19.3, 0) * 8) * math.sin(max(t - 19.3, 0) * 30) * (t > 19.3)
    a1 = math.radians((t - 19.0) * 40)
    clock = line([(760, 190), (760 + 34 * math.sin(a1), 190 - 34 * math.cos(a1))], 5, INK, taper=.3, seed=7071)
    clock += line([(760, 190), (760 + 22 * math.sin(2.3), 190 - 22 * math.cos(2.3))], 7, INK, taper=.3, seed=7072)
    s = [_ST["wall"], clock, _ST["corr"], door_frame(), desks(t, (0,)), hero(t), door_leaf(th), desks(t, (1,))]
    # камера: средний план, едет за студентом, толчок на «нелепой»
    u = clamp((t - 19.0) / 2.4)
    sc = 1.3 + 0.22 * ease_io(clamp((t - 19.0) / 0.9)) + 0.06 * u
    cx = 400 + 120 * ease_io(clamp((t - 19.0) / 0.9))
    cy = 860
    rot = 0.8 - 1.2 * u
    e = t - SILLY
    if e > 0:
        kk = math.exp(-e * 7)
        sc *= 1 + 0.07 * kk
        cx += 10 * kk * math.sin(e * 45)
        cy += 8 * kk * math.sin(e * 37)
    return cam(cx, cy, sc, rot), "".join(s)


def build_static():
    _ST["wall"] = wall()
    _ST["corr"] = corridor()
    lib.static_done()


def frame(sid, t):
    if not _ST:
        build_static()
    lib.dyn_begin()
    tr, body = s11(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#9a643a"/><g transform="{tr}">{body}</g>')
