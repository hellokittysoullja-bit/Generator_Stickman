"""s16 (20.72–22.32, клип 20.52–22.52): коридор квартиры утром. Дима в горчичном худи, синих тапках и с пледом в клетку
на плечах (плед — тот же, что в bed/) сонно шаркает слева направо: глаза почти закрыты, голова свешена, на 21.25 зевает,
рука держит плед у груди. Камера едет рядом сбоку. На «проснулся» (22.32, стык с s17) глаза распахиваются, брови вверх,
волосы подпрыгивают, камера толкается.

Мир: пол коридора y = 0, x растёт вправо (к кухне). Ступня в опоре стоит в мире — не скользит."""
import math

import numpy as np

import flatlib as F
import lib
from flatlib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth

T_A, T_B = 20.52, 22.52
T_PRO = F.word("проснулся", 22.0)
BS = 0.62
LEG = (F.people.THIGH + F.people.SHIN) * BS
TC = 0.56                    # шаг (с)
ST = 0.40                    # опора
STEP = 170.0                 # длина шага
V = STEP / TC
HIP_H = LEG * 1.0 + F.people.AH * BS * 0.4
WALL_TOP = -1500.0


# ───────────────────────────── коридор
def corridor(x0, x1):
    s = []
    wall, wall_sh = "#b9d0c4", "#9ab5a8"
    s.append(f'<rect x="{x0:.0f}" y="{WALL_TOP - 600:.0f}" width="{x1 - x0:.0f}" height="{-WALL_TOP + 640:.0f}" fill="{wall}"/>')
    # обои: тонкие вертикальные полосы и мелкий ромбик
    lib.DEFS.append('<pattern id="pWall37" width="64" height="64" patternUnits="userSpaceOnUse">'
                    f'<rect width="64" height="64" fill="{wall}"/><rect x="0" width="6" height="64" fill="{wall_sh}" opacity=".55"/>'
                    '<path d="M32 26 L36 32 L32 38 L28 32Z" fill="#f2efe2" opacity=".7"/></pattern>')
    s.append(f'<rect x="{x0:.0f}" y="{WALL_TOP:.0f}" width="{x1 - x0:.0f}" height="{-WALL_TOP - 260:.0f}" fill="url(#pWall37)"/>')
    # панель снизу (вагонка) и молдинг
    s.append(shape(rect_pts(x0, -260, x1, -10), "#f1e6cf", "".join(
        line([(x, -250), (x, -14)], 2.4, "#d2c3a4", taper=.05, wmin=.9, seed=4100 + int(x) % 97, op=.9)
        for x in np.arange(math.floor(x0 / 70) * 70, x1, 70)), w=4, seed=4101))
    s.append(shape(rect_pts(x0, -276, x1, -252), "#e2d3b3", "", w=3.8, seed=4102))
    s.append(shape(rect_pts(x0, -34, x1, 0), "#cdb58c", "", w=4, seed=4103))
    # предметы на стене по x (повторяются с шагом 1500)
    for k in range(int(math.floor(x0 / 1500)) - 1, int(math.ceil(x1 / 1500)) + 1):
        bx = k * 1500
        s.append(door(bx + 120, k))
        s.append(frame_pic(bx + 760, -980, k))
        s.append(hooks(bx + 1120, k))
    # пол: доска + дорожка
    s.append(shape(rect_pts(x0, 0, x1, 900), "#c99d6c", "".join(
        line([(x0, 40 + j * 70 + j * j * 6), (x1, 40 + j * 70 + j * j * 6)], 3, "#a97f52", taper=.05, wmin=.9, seed=4110 + j, op=.8)
        for j in range(6)), w=4.4, seed=4111))
    s.append(shape(rect_pts(x0, 46, x1, 150), "#6f8f9e", blob(rect_pts(x0, 46, x1, 62), "#a7c3cc", .9) +
                   blob(rect_pts(x0, 134, x1, 150), "#a7c3cc", .9) + blob(rect_pts(x0, 120, x1, 150), "#4f6c7a", .5), w=4, seed=4112))
    return "".join(s)


def door(x, k):
    s = []
    w, h = 380, 860
    s.append(shape(rect_pts(x - 26, -h - 26, x + w + 26, 0), "#f4efe4", blob(rect_pts(x + w, -h - 26, x + w + 26, 0), "#d9d1c0", .9),
                   w=4.4, seed=4200 + k))
    inner = blob(rect_pts(x + w - 60, -h, x + w, 0), "#a8774c", .8)
    for j, (a, b) in enumerate(((-h + 60, -h + 400), (-h + 460, -60))):
        inner += shape(rect_pts(x + 50, a, x + w - 50, b, 8), "#c38d5c", blob(rect_pts(x + w - 70, a, x + w - 50, b), "#a8774c", .8),
                       w=3.2, seed=4210 + j + k)
    s.append(shape(rect_pts(x, -h, x + w, 0), "#c99566", inner, w=4.6, seed=4220 + k))
    s.append(shape(ellipse_pts(x + w - 50, -430, 15, 15, 12), "#e2b84a", blob(ellipse_pts(x + w - 46, -426, 9, 9, 8), "#b98d2a"), w=3,
                   seed=4230 + k))
    return "".join(s)


def frame_pic(x, y, k):
    rs = np.random.RandomState(4300 + k)
    w, h = 300, 220
    inner = f'<rect x="{x - 20}" y="{y - 20}" width="{w + 40}" height="{h + 40}" fill="#a8d4ea"/>'
    inner += blob([(x - 10, y + h * .75), (x + w * .3, y + h * .42), (x + w * .55, y + h * .7), (x + w * .8, y + h * .35), (x + w + 10, y + h * .62),
                   (x + w + 10, y + h + 10), (x - 10, y + h + 10)], "#7fae6a")
    inner += blob(ellipse_pts(x + w * .78, y + h * .22, 22, 22, 12), "#fff1b8")
    _ = rs
    s = [shape(rect_pts(x - 22, y - 22, x + w + 22, y + h + 22, 4), "#7a5236", blob(rect_pts(x + w, y - 22, x + w + 22, y + h + 22), "#5a3a24", .9),
               w=4.2, seed=4310 + k),
         shape(rect_pts(x, y, x + w, y + h), "#a8d4ea", inner, w=3.2, seed=4320 + k)]
    return "".join(s)


def hooks(x, k):
    s = [shape(rect_pts(x - 120, -1180, x + 120, -1150, 6), "#a8774c", "", w=3.6, seed=4400 + k)]
    for j, dx in enumerate((-80, 0, 80)):
        s.append(line([(x + dx, -1150), (x + dx, -1120), (x + dx + 14, -1110)], 6, INK, seed=4410 + j, taper=.2, wmin=.6))
    # шарф и сумка
    s.append(shape([(x - 90, -1124), (x - 64, -1124), (x - 56, -900, 1), (x - 98, -890, 1)], "#5f9a5a",
                   "".join(line([(x - 96, -1060 + j * 50), (x - 58, -1060 + j * 50)], 3, "#3f7a42", seed=4420 + j, op=.8) for j in range(4)),
                   w=3.6, seed=4421 + k))
    s.append(line([(x + 74, -1112), (x + 40, -980), (x + 110, -980), (x + 86, -1112)], 5, "#6b4a30", seed=4430, taper=.1, wmin=.8))
    s.append(shape(rect_pts(x + 20, -990, x + 130, -880, 16), "#d9a35a", blob(rect_pts(x + 100, -990, x + 130, -880), "#b8823e", .9),
                   w=4, seed=4431 + k))
    return "".join(s)


# ───────────────────────────── походка
def contacts():
    C = []
    for k in range(-6, 12):
        t = T_A - 0.3 + k * TC
        C.append((t, "n" if k % 2 == 0 else "f", k * STEP))
    return C


CON = contacts()


def hip_x(t):
    return V * (t - T_A) + 18


def foot(side, t):
    cs = [c for c in CON if c[1] == side]
    prev, nxt = cs[0], cs[1]
    for i, c in enumerate(cs):
        if c[0] <= t:
            prev, nxt = c, cs[min(i + 1, len(cs) - 1)]
    ankle_y = -F.people.AH * BS * 0.45
    if t <= prev[0] + ST:
        roll = -0.06 * smooth(prev[0] + ST * .6, prev[0] + ST, t)      # пятка отрывается в конце опоры
        return (prev[2], ankle_y), roll
    u = clamp((t - prev[0] - ST) / (nxt[0] - prev[0] - ST))
    ux = ease_io(u)
    x = prev[2] + (nxt[2] - prev[2]) * ux
    y = ankle_y - 34 * math.sin(math.pi * u)           # шаркает: стопа еле отрывается
    phi = -0.06 * (1 - u) + 0.05 * math.sin(math.pi * u)
    return (x, y), phi


def frame(t):
    lib.DEFS.clear()
    F.people.SLIPPERS[0] = True
    wake = smooth(T_PRO - .03, T_PRO + .08, t)
    hx = hip_x(t)
    ph = 2 * math.pi * (t - (T_A - 0.3)) / TC
    hip = np.array([hx, -HIP_H - 6 * math.cos(ph) * (1 - .5 * wake) - 18 * wake])
    lean = 0.13 - 0.03 * math.sin(ph) - 0.1 * wake
    feet = {s: foot(s, t) for s in ("n", "f")}
    up = np.array([math.sin(lean), -math.cos(lean)])
    fw = np.array([math.cos(lean), math.sin(lean)])
    chest = hip + up * 128 + fw * 66
    arms = {"n": ("ik", tuple(chest + np.array([4, 6])), -1), "f": ("ik", tuple(chest + np.array([-18, 0])), -1)}
    fist = dict(kind="open", flip=-1, dir=(.15, -1), curl=(.85, .9, .9, .9), spread=.02, thumb=.7)
    hands = {"n": fist, "f": dict(fist)}
    yawn = F.bump(t, 21.3, .75)
    ex = dict(lid=.05 + .95 * wake, closed=.55 * (1 - wake) * (1 - yawn * .3), look=(.35 + .3 * wake, .3 - .5 * wake),
              brows="up" if wake > .5 else "tired", mouth="talk" if wake < .5 else "talk", open=.9 * yawn + .55 * wake, smile=-.3 - .2 * wake,
              hair=10 * F.bump(t, T_PRO, .45) * F.osc(t, 6))
    head_ang = .22 + .06 * math.sin(ph * .5) - .1 * yawn - .3 * wake
    dm = F.people.draw(dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands, expr=ex, head_ang=head_ang, hood=0,
                            strings=(4 * math.sin(ph), 2 * math.cos(ph))), "dima")
    F.people.SLIPPERS[0] = False
    cape = plaid_cape(hip, lean, ph, wake)
    # камера: едет за Димой, лёгкое качание; на «проснулся» — толчок
    cs = 1.36 + 0.05 * ease_io(clamp((t - T_A) / 2.0)) + 0.07 * F.bump(t, T_PRO + .02, .3)
    cx = hx + 40 + 10 * math.sin(t * 1.3)
    cy = -560 + 6 * math.sin(t * 2.0) - 10 * wake
    r = 0.5 * math.sin(t * 1.4) + 1.2 * F.kick(t, T_PRO, 8, 6)
    F.set_ink(cs)
    view = 1080 / cs
    bg = corridor(cx - view, cx + view)
    sh = blob(ellipse_pts(hx + 10, 4, 170, 16, 16), "#2a1606", .28, lib.blur(5))
    body = sh + dm["legs"] + dm["arm_f"] + dm["body"] + cape + dm["arm_n"]
    # звёздочки-удивление при пробуждении
    if wake > 0:
        hxx, hyy = dm["head"]
        for j, (dx, dy) in enumerate(((-70, -150), (90, -170), (150, -90))):
            body += F.star(hxx + dx, hyy + dy, 22 * ease_out(clamp((t - T_PRO) / .12)), j, op=1.0)
    light = sunbeam(cx)
    return F.compose(bg + light, body, (cx, cy, cs, r), glow=False)


def sunbeam(cx):
    """Тёплый свет из кухни (справа): мягкий градиент по стене."""
    g = lib.lin_grad([(0, "#fff1c8", 0), (1, "#fff1c8", .35)], 0, 0, 1, 0)
    return f'<rect x="{cx - 900:.0f}" y="-1600" width="1800" height="1800" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def plaid_cape(hip, lean, ph, wake):
    """Плед на плечах: от плеч по спине до бёдер, сзади чуть отстаёт и колышется; спереди его держит рука у груди."""
    up = np.array([math.sin(lean), -math.cos(lean)])
    fw = np.array([math.cos(lean), math.sin(lean)])
    sh = hip + up * F.people.TORSO * BS
    sw = 10 * math.sin(ph + .8)
    flare = 30 + 8 * math.sin(ph * .5)

    def p(base, a, b, c=False):
        q = base + up * a + fw * b
        return (float(q[0]), float(q[1])) + ((1,) if c else ())
    pts = [p(sh, -4, 62), p(sh, 14, 26), p(sh, 20, -30), p(sh, 4, -84), p(hip, 140, -108 - flare * .3),
           p(hip, -40, -116 - flare + sw), p(hip, -140, -96 - flare + sw * 1.4, True), p(hip, -158, -40 + sw), p(hip, -140, 0 + sw * .6, True),
           p(hip, 0, 22), p(hip, 90, 52), p(hip, 128, 70)]
    folds = [[p(sh, -20, -40), p(hip, 60, -80), p(hip, -120, -70 - flare + sw)],
             [p(sh, -30, 10), p(hip, 40, -10), p(hip, -140, -10 + sw)]]
    pid = "plaid37"
    lib.DEFS.append(
        f'<pattern id="{pid}" width="96" height="96" patternUnits="userSpaceOnUse" patternTransform="rotate({-6 + math.degrees(lean):.2f})">'
        f'<rect width="96" height="96" fill="#4f7d55"/>'
        f'<rect x="0" y="34" width="96" height="28" fill="#35583c" opacity=".9"/><rect x="34" y="0" width="28" height="96" fill="#35583c" opacity=".9"/>'
        f'<rect x="0" y="44" width="96" height="8" fill="#c9473a"/><rect x="44" y="0" width="8" height="96" fill="#c9473a"/>'
        f'<rect x="0" y="6" width="96" height="3" fill="#f2e3c4" opacity=".8"/><rect x="6" y="0" width="3" height="96" fill="#f2e3c4" opacity=".8"/>'
        f'</pattern>')
    inner = f'<rect x="{hip[0] - 600:.0f}" y="{hip[1] - 900:.0f}" width="1200" height="1600" fill="url(#{pid})"/>'
    inner += blob([p(hip, 200, -260), p(hip, 200, -60), p(hip, -200, -70), p(hip, -200, -260)], "#1a2a1e", .22)
    for k, f_ in enumerate(folds):
        inner += line(f_, 3, "#22382a", seed=4500 + k, op=.7)
    return shape(pts, "#4f7d55", inner, w=4.8, seed=4510)


_ = (mix, ease_out)
