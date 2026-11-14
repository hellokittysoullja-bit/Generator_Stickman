"""Рилс 57 группа B: s04 (5.0–7.1) коридор, Дима мчится к двери туалета, на «туалет» (6.19) дверь хлопает;
s05 (6.7–8.9) часы без цифр крупно, на «полчаса» (7.02) минутная стрелка делает круг и ещё один, Дима согнулся у двери и топчется."""
import math

import dima
import os
import sys

import fxprops as fp
import lib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common'))
import props
from lib import INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg

SEED = 7000
HIT_DOOR = 6.19
HIT_HALF = 7.02


def lerp(a, b, u):
    return a + (b - a) * u


def rnd(i):
    return abs(math.sin(i * 12.9898) * 43758.5453) % 1.0


# ═════════════════════════ общие куски: стена, пол, дверь ═════════════════════════
def corridor_bg(x0, x1, floor_y):
    """Стена коридора x0..x1 (мир), пол ниже floor_y. Рамки картин, лампа, плинтус."""
    s = []
    g = lin_grad([(0, "#f4e3c4", 1), (1, "#e7cfa4", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="{x0}" y="-1500" width="{x1 - x0}" height="{1500 + floor_y}" fill="url(#{g})"/>')
    for x in range((int(x0) // 120) * 120, int(x1), 120):
        s.append(f'<rect x="{x}" y="-1500" width="50" height="{1500 + floor_y}" fill="#dcc296" opacity=".28"/>')
    # плинтус
    s.append(blob(rect_pts(x0, floor_y - 64, x1, floor_y), "#fbf6ea"))
    s.append(line([(x0, floor_y - 64), (x1, floor_y - 64)], 4, INK, taper=.02, wmin=1, seed=SEED + 1))
    # пол
    gf = lin_grad([(0, "#c9a06c", 1), (1, "#a97f4f", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="{x0}" y="{floor_y}" width="{x1 - x0}" height="1400" fill="url(#{gf})"/>')
    s.append(line([(x0, floor_y), (x1, floor_y)], 5, INK, taper=.02, wmin=1, seed=SEED + 2))
    for k in range(1, 9):
        y = floor_y + k * 58 + k * k * 3
        s.append(line([(x0, y), (x1, y + 4)], 3, "#8c6238", taper=.05, wmin=.9, seed=SEED + 10 + k, op=.5))
    for xx in range((int(x0) // 340) * 340, int(x1) + 340, 340):
        for k in range(0, 6):
            y = floor_y + k * 58 + k * k * 3
            s.append(line([(xx + (k % 2) * 170, y), (xx + (k % 2) * 170 + 3, y + 62 + k * 6)], 2.4, "#8c6238", taper=.05, wmin=.9, seed=SEED + 40 + k, op=.45))
    return "".join(s)


def picture(x, y, w, h, kind, sd):
    """Рамка с картинкой без текста: пейзаж/цветок/горы."""
    s = []
    s.append(fp.shadow(x + w / 2 + 8, y + h + 4, w * .5, 10, .25, 6))
    inner = ""
    if kind == 0:
        inner = blob(rect_pts(x, y, x + w, y + h * .6), "#bfe0ee") + blob([(x, y + h * .75), (x + w * .35, y + h * .45), (x + w * .6, y + h * .7), (x + w * .85, y + h * .5), (x + w, y + h * .7), (x + w, y + h), (x, y + h)], "#7aa86a")
        inner += blob(ellipse_pts(x + w * .78, y + h * .22, w * .09, w * .09, 10), "#f5d36a")
    elif kind == 1:
        inner = blob(rect_pts(x, y, x + w, y + h), "#f2d9d0") + blob(ellipse_pts(x + w * .5, y + h * .4, w * .2, w * .2, 10), "#d9675a") + \
            blob(ellipse_pts(x + w * .5, y + h * .4, w * .08, w * .08, 8), "#f5d36a") + line([(x + w * .5, y + h * .6), (x + w * .5, y + h * .92)], 6, "#5f8a4e", seed=sd)
    else:
        inner = blob(rect_pts(x, y, x + w, y + h), "#d6e4cf") + blob([(x, y + h), (x + w * .3, y + h * .35), (x + w * .55, y + h * .75), (x + w * .75, y + h * .25), (x + w, y + h)], "#6d8fb0")
    s.append(shape(rect_pts(x - 14, y - 14, x + w + 14, y + h + 14, 4), "#7a4f2c", "", w=5, seed=sd))
    s.append(shape(rect_pts(x, y, x + w, y + h, 2), "#f4ece0", inner, w=3.4, seed=sd + 1))
    return "".join(s)


def wc_icon(cx, cy, sz, sd):
    """Значок без букв: кружок-голова и треугольник-туловище на тёмно-бирюзовой плашке."""
    s = [shape(rect_pts(cx - sz * .6, cy - sz * .75, cx + sz * .6, cy + sz * .75, sz * .14), "#2a6a7e", "", w=4.4, seed=sd)]
    s.append(shape(ellipse_pts(cx, cy - sz * .42, sz * .16, sz * .16, 12), "#fdf6e4", "", w=3.2, seed=sd + 1))
    s.append(shape([(cx, cy - sz * .2, 1), (cx + sz * .3, cy + sz * .5, 1), (cx - sz * .3, cy + sz * .5, 1)], "#fdf6e4", "", w=3.2, seed=sd + 2))
    return "".join(s)


def door_frame_and_interior(x, y, w, h, sd):
    """Проём: тёмная комната (кафель и свет), рамка. Возвращает (внутренность, клип-id, рамка)."""
    inner = []
    g = lin_grad([(0, "#cfe6e8", 1), (1, "#8fb8c0", 1)], 0, 0, 0, 1)
    inner.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{g})"/>')
    for k in range(0, 5):
        inner.append(line([(x, y + 80 + k * 90), (x + w, y + 80 + k * 90)], 3, "#6f9aa4", taper=.05, wmin=.9, seed=sd + k, op=.6))
    for k in range(0, 4):
        inner.append(line([(x + 40 + k * 90, y), (x + 40 + k * 90, y + h)], 3, "#6f9aa4", taper=.05, wmin=.9, seed=sd + 9 + k, op=.5))
    inner.append(blob(rect_pts(x, y + h - 150, x + w, y + h), "#e9efe9"))
    # унитаз-силуэт в проёме (белая форма)
    inner.append(shape([(x + w * .36, y + h - 150, 1), (x + w * .36, y + h - 300), (x + w * .64, y + h - 300), (x + w * .64, y + h - 150, 1)], "#fbfdfb", "", w=4, seed=sd + 30))
    inner.append(shape(ellipse_pts(x + w * .5, y + h - 150, w * .22, 34, 14), "#fbfdfb", "", w=4, seed=sd + 31))
    c = lib.clip_rect(x, y, w, h)
    frame = shape(rect_pts(x - 26, y - 26, x + w + 26, y + h + 6, 3), "#fbf6ea", "", w=5, seed=sd + 40, ink=False)
    fr = "".join([
        blob(rect_pts(x - 26, y - 26, x + w + 26, y), "#fbf6ea"), blob(rect_pts(x - 26, y, x, y + h), "#fbf6ea"), blob(rect_pts(x + w, y, x + w + 26, y + h), "#fbf6ea"),
        line([(x - 26, y + h, 1), (x - 26, y - 26, 1), (x + w + 26, y - 26, 1), (x + w + 26, y + h, 1)], 5, INK, taper=.05, wmin=.8, seed=sd + 41),
        line([(x, y, 1), (x + w, y, 1)], 4, INK, taper=.05, wmin=.8, seed=sd + 43), line([(x, y, 1), (x, y + h, 1)], 4, INK, taper=.05, wmin=.8, seed=sd + 44),
        line([(x + w, y, 1), (x + w, y + h, 1)], 4, INK, taper=.05, wmin=.8, seed=sd + 45)])
    return "".join(inner), c, fr


def door_leaf(x, y, w, h, c, sd, icon=True, knob_left=True):
    """Створка, сидящая на петлях у правого края проёма; c: 1 — закрыта (во весь проём), 0 — ребром; вид «внутрь» (свободный край дальше → ниже и короче)."""
    if c <= 0.04:
        return ""
    wd = w * c
    xr = x + w
    xl = xr - wd
    far = 1 - c
    shrink = 0.07 * far * h
    pts = [(xr, y, 1), (xl, y + shrink, 1), (xl, y + h - shrink, 1), (xr, y + h, 1)]
    col = mix("#e9b36a", "#c98f4c", far * .6)
    inner = ""
    # филёнки
    for (a, b, cc, d) in ((.1, .08, .9, .42), (.1, .52, .9, .92)):
        p0 = (xr - wd * (1 - a), y + shrink * (1 - a) + h * b)
        p1 = (xr - wd * (1 - cc), y + shrink * (1 - cc) + h * b)
        p2 = (xr - wd * (1 - cc), y + h - shrink * (1 - cc) - h * (1 - d))
        p3 = (xr - wd * (1 - a), y + h - shrink * (1 - a) - h * (1 - d))
        inner += shape([p0 + (1,), p1 + (1,), p2 + (1,), p3 + (1,)], mix(col, "#7a4f2c", .18), "", w=3.4, seed=sd + int(a * 100 + b * 100), ink=True)
    out = [shape(pts, col, inner, w=5.2, seed=sd)]
    if icon and c > 0.5:
        cx = xl + wd * .5
        out.append(wc_icon(cx, y + h * .24, 150 * c, sd + 20))
    if c > 0.35:
        kx = xl + wd * .12
        out.append(shape(ellipse_pts(kx, y + h * .56, 17 * c, 17, 10), "#f1d27a", "", w=3.4, seed=sd + 7))
    return "".join(out)


# ═════════════════════════ Дима ═════════════════════════
def run_state(t):
    pass


# ═════════════════════════ s04 ═════════════════════════
FLOOR4 = 1330
DX0, DW, DH, DY = 1150, 300, 760, FLOOR4 - 760     # проём двери: x 1150–1450, пол у FLOOR4
T_OPEN = 5.50          # дверь распахивается
T_SLAM = HIT_DOOR      # хлопок
BS4 = 0.62
DCX = DX0 + DW * .5
T_ARR = 5.92           # Дима в проёме


def dima_run4(t):
    T0 = 5.0
    ks = BS4 / 0.44
    x = DCX - 1100.0 * (T_ARR - t)
    x = min(x, DCX)
    th = (t - T0) * 2 * math.pi / 0.30
    ankle = FLOOR4 - 38 * ks / 1.4 + 10
    moving = x < DCX - 1
    bob = 22 * ks * abs(math.sin(th)) * (1 if moving else 0.0)
    hip = (x, ankle - 634 * BS4 - bob)
    feet = {}
    for k, side in enumerate(("n", "f")):
        ph = th + math.pi * k
        if not moving:
            feet[side] = ((hip[0] + 40 * (1 - k * .8), ankle), 0.0)
        else:
            feet[side] = ((hip[0] + 150 * ks * math.cos(ph) + 20, ankle - 140 * ks * max(0, -math.sin(ph))), 0.35 * math.sin(ph))
    arms = {"n": ("ik", (hip[0] + 40 + 150 * ks * math.sin(th), hip[1] - 70 + 60 * ks * math.cos(th))),
            "f": ("ik", (hip[0] + 40 - 150 * ks * math.sin(th), hip[1] - 70 - 60 * ks * math.cos(th)))}
    return hip, feet, arms, th


def dima_svg4(t):
    hip, feet, arms, th = dima_run4(t)
    vy = (dima_run4(t)[0][1] - dima_run4(t - .05)[0][1]) / .05
    pose = dict(hip=hip, lean=0.34, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"},
                head_ang=0.05 * math.sin(t * 5), hood=clamp(-vy * .05, -16, 22), strings=(-14 + 4 * math.sin(t * 6), 4),
                expr={"lid": 1.0, "look": (0.95, 0.25), "brows": "strain", "mouth": "pant", "hair": 5 * math.sin(t * 9)})
    dima.BS = BS4
    dima.LWK = 1.2
    kL = 1.0 / 0.6

    def held(Wr, d):
        sl = 9 * math.sin(t * 34) + 4 * math.sin(t * 21)
        return props.glass(Wr[0] + d[0] * 64 + 6, Wr[1] + d[1] * 64 + 52, kL, 0.5 - 0.2 * clamp((t - 5.0) / 1.0), tilt=-8 + 5 * math.sin(t * 17), slosh=sl, seed=4)

    pose["held"] = ("front", held)
    g, _ = dima.draw(pose)
    return g, hip


def s04_frame(t):
    s = []
    s.append(corridor_bg(-1200, 3200, FLOOR4))
    for k, kind in enumerate((0, 1, 2, 1, 0, 2, 1, 0)):
        x = -300 + k * 330
        if DX0 - 230 < x < DX0 + DW + 120:
            continue
        s.append(picture(x, 540, 180 if kind != 1 else 140, 230, kind, SEED + 100 + k * 5))
    inside, clip_id, frame = door_frame_and_interior(DX0, DY, DW, DH, SEED + 300)
    s.append(f'<rect x="{DX0 - 26}" y="{DY - 26}" width="{DW + 52}" height="{DH + 32}" fill="#8fb8c0"/>')
    s.append(f'<g clip-path="url(#{clip_id})">{inside}</g>')
    # Дима: слева от проёма виден целиком, в проёме — только внутри него; ныряя вглубь, уменьшается
    g, hip = dima_svg4(t)
    dive = ease_io(clamp((t - 5.62) / 0.5))
    k = 1 - 0.34 * dive
    cid = f"cl{int(t * 1000)}"
    lib.DEFS.append(f'<clipPath id="{cid}"><rect x="-1500" y="-1500" width="{DX0 - 26 + 1500}" height="4000"/>'
                    f'<rect x="{DX0}" y="{DY}" width="{DW}" height="{DH}"/></clipPath>')
    s.append(fp.shadow(hip[0] + 30, FLOOR4 + 18, 210, 24, .3, 10) if t < 5.7 else "")
    s.append(f'<g clip-path="url(#{cid})"><g transform="translate({f(hip[0])} {FLOOR4 - 10}) scale({k:.4f}) translate({f(-hip[0])} {-(FLOOR4 - 10)})">{g}</g></g>')
    s.append(frame)
    # брызги из стакана: капли летят назад и вниз
    for i in range(0, 60):
        tb = 4.9 + i * 0.04
        e = t - tb
        if not 0 < e < 0.7 or tb > T_ARR:
            continue
        hb, _, _, thb = dima_run4(tb)
        ksb = BS4 / 0.44
        gx, gy = hb[0] + 40 + 150 * ksb * math.sin(thb) + 14, hb[1] - 70 + 60 * ksb * math.cos(thb) - 70
        vx, vy = -430 - 220 * rnd(i), -330 + 260 * rnd(i + 7) - 120 * math.sin(i)
        px, py = gx + vx * e, gy + vy * e + 1500 * e * e
        if py < FLOOR4 + 30:
            s.append(props.droplet(px, py, 1.0 + .5 * rnd(i + 3), rot=math.degrees(math.atan2(vy + 3000 * e, vx)) + 90, seed=i))
    # лужица у двери после хлопка
    if t > T_SLAM - 0.1:
        pu = clamp((t - T_SLAM) / 0.8)
        s.append(shape(ellipse_pts(DCX - 40, FLOOR4 + 40, 40 + 140 * ease_out(pu), 12 + 30 * ease_out(pu), 18), props.C_WATER_TOP, "", w=3.4, seed=SEED + 900))
    # створка: распахивается внутрь (ребром), хлопает на «туалет»
    if t < T_OPEN:
        c = 1.0
    elif t < T_SLAM - 0.04:
        c = 1 - ease_out((t - T_OPEN) / 0.14, 2) * 0.94
    else:
        c = 0.06 + 0.94 * ease_in(clamp((t - (T_SLAM - 0.04)) / 0.05), 1.3)
    s.append(door_leaf(DX0, DY, DW, DH, c, SEED + 400))
    if t >= T_SLAM:
        e = t - T_SLAM
        s.append(fp.burst(DCX, DY + DH * .45, e / 0.4, 12, 250, 480, 12, "#fff4c2", SEED + 500))
        s.append(fp.dust(DX0 - 60, FLOOR4 + 10, e / 0.7, 7, 200, 80, SEED + 520, rmax=36))
        s.append(fp.dust(DX0 + DW + 60, FLOOR4 + 10, e / 0.7, 7, 200, 80, SEED + 530, rmax=36))
    # камера
    cx = lerp(hip[0] + 190, DCX, ease_io(clamp((t - 5.25) / 0.65)))
    if t < 5.25:
        cx = hip[0] + 190
    sc = lerp(1.06, 1.22, ease_io(clamp((t - 5.0) / 1.2)))
    cy = 990
    rot = lerp(-2.5, 0.0, ease_out(clamp((t - 5.0) / 0.5)))
    if t >= T_SLAM:
        e = t - T_SLAM
        kk = math.exp(-e * 9)
        sc *= 1 + 0.07 * kk
        rot += 3.0 * kk * math.sin(e * 38)
        cy += 22 * kk * math.sin(e * 52)
    if t < T_ARR:
        cy += 7 * math.sin(t * 40)
    return svg(f'<rect width="{W}" height="{H}" fill="#e7cfa4"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')


# ═════════════════════════ s05: часы ═════════════════════════
CC5 = (540, 380)
R5 = 270


def clock_face(t, sd=9100):
    cx, cy = CC5
    s = []
    s.append(fp.shadow(cx + 18, cy + 30, R5 + 30, R5 + 24, .28, 16))
    # гвоздь-ушко сверху
    s.append(shape(ellipse_pts(cx, cy - R5 - 40, 22, 22, 10), "#6f6f78", "", w=4, seed=sd))
    rim = ellipse_pts(cx, cy, R5, R5, 28)
    gr = lin_grad([(0, "#b06a3a", 1), (1, "#7a4524", 1)], 0, 0, 1, 1)
    s.append(shape(rim, f"url(#{gr})", "", w=7, seed=sd + 1))
    face = ellipse_pts(cx, cy, R5 - 34, R5 - 34, 28)
    inner = blob(ellipse_pts(cx - 36, cy - 44, R5 * .62, R5 * .58, 14), "#ffffff", .55)
    inner += blob([(cx - 300, cy + 130), (cx + 300, cy + 90), (cx + 300, cy + 330), (cx - 300, cy + 330)], "#efe3c8", .9)
    s.append(shape(face, "#fbf4e2", inner, w=5, seed=sd + 2))
    # риски
    for k in range(60):
        a = math.radians(k * 6)
        big = k % 5 == 0
        r0 = R5 - 34 - (46 if k % 15 == 0 else (34 if big else 15))
        r1 = R5 - 34 - 8
        w = 13 if k % 15 == 0 else (8 if big else 3)
        s.append(line([(cx + r0 * math.sin(a), cy - r0 * math.cos(a)), (cx + r1 * math.sin(a), cy - r1 * math.cos(a))], w, INK, taper=.0, wmin=1, seed=sd + 10 + k, peak=.5))
    return "".join(s)


def clock_angle(t):
    """Угол минутной стрелки (градусы по часовой от 12): дрожь, круг на «полчаса», ещё круг."""
    a = 0.0
    a += 360 * ease_io((t - HIT_HALF) / 0.78)
    a += 360 * ease_io((t - (HIT_HALF + 0.82)) / 0.78)
    if t < HIT_HALF:
        a += 2.2 * math.sin(t * 38) + 3 * smooth(6.7, HIT_HALF, t)
    e = t - (HIT_HALF + 1.6)
    if e > 0:
        a += 9 * math.exp(-e * 7) * math.cos(e * 30)
    return a


def hand(cx, cy, ang, L, w, col, tail, sd):
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    nx, ny = -uy, ux
    tip = (cx + ux * L, cy + uy * L)
    base = (cx - ux * tail, cy - uy * tail)
    pts = [(base[0] + nx * w * .4, base[1] + ny * w * .4, 1), (cx + nx * w * .5 + ux * 30, cy + ny * w * .5 + uy * 30), (tip[0], tip[1], 1),
           (cx - nx * w * .5 + ux * 30, cy - ny * w * .5 + uy * 30), (base[0] - nx * w * .4, base[1] - ny * w * .4, 1)]
    return shape(pts, col, "", w=4, seed=sd, var=.15)


def clock_hands(t):
    cx, cy = CC5
    m = clock_angle(t)
    hr = 12 + m / 12 + 30 * 0
    sec = (t - 6.7) * 720.0
    s = []
    # серый «вихрь» за минутной стрелкой, пока она бежит
    sp = (clock_angle(t) - clock_angle(t - 0.06)) / 0.06
    if sp > 400:
        Lr = R5 - 70
        a1 = math.radians(m)
        a0 = math.radians(m - min(150, sp * 0.09))
        n = 14
        pts = [(cx, cy, 1)]
        for k in range(n + 1):
            a = a0 + (a1 - a0) * k / n
            pts.append((cx + Lr * math.sin(a), cy - Lr * math.cos(a)))
        s.append(blob(pts + [(cx, cy, 1)], "#f0dcae"))
    s.append(hand(cx, cy, hr, R5 * .5, 30, INK, 36, 9300))
    s.append(hand(cx, cy, m, R5 - 72, 20, INK, 50, 9310))
    s.append(hand(cx, cy, sec, R5 - 60, 6, "#d9473a", 56, 9320))
    s.append(shape(ellipse_pts(cx, cy, 26, 26, 12), "#d9473a", "", w=4.4, seed=9330))
    return "".join(s)


DOOR5 = (740, 760, 290, 670)   # x, y, w, h


def drop(cx, cy, sz, sd, col="#8fd0f5"):
    pts = [(cx, cy - sz * 1.15, 1), (cx + sz * .62, cy + sz * .25), (cx + sz * .5, cy + sz * .8), (cx, cy + sz * 1.0), (cx - sz * .5, cy + sz * .8), (cx - sz * .62, cy + sz * .25)]
    s = shape(pts, col, blob([(cx - sz * .3, cy - sz * .1), (cx + sz * .55, cy + sz * .4), (cx + sz * .35, cy + sz * .9), (cx, cy + sz * .95)], "#5fb0e0", .8), w=4, seed=sd)
    s += blob(ellipse_pts(cx - sz * .22, cy + sz * .2, sz * .12, sz * .22, 8, rot=20), "#ffffff", .95)
    return s


def dima5(t):
    FL = 1430
    dima.BS = 0.66
    dima.LWK = 1.1
    hipx = 270
    ankle = FL - 38
    st = 3.3 * math.pi * 2
    pa, pb = math.sin(t * st), math.sin(t * st + math.pi)
    feet = {"n": ((hipx + 70 - 14 * pa, ankle - 34 * max(0, pa)), -0.12 * max(0, pa)),
            "f": ((hipx + 20 + 8 * pb, ankle - 34 * max(0, pb)), -0.12 * max(0, pb))}
    hip = (hipx + 6 * math.sin(t * 6.6), ankle - 385 + 8 * abs(pa))
    sw = math.sin(t * 6.6)
    arms = {"n": ("ik", (hip[0] + 70, hip[1] + 78)), "f": ("ik", (hip[0] + 30, hip[1] + 60))}
    pose = dict(hip=hip, lean=0.62 + 0.03 * sw, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"}, head_ang=-0.18 + 0.03 * sw,
                hood=4 * sw, strings=(5 * sw, 3),
                expr={"lid": 1.0, "look": (1.0, 0.1), "brows": "worry", "mouth": "strain", "hair": 4 * math.sin(t * 13)})
    g, _ = dima.draw(pose)
    return g, hip


def s05_frame(t):
    s = []
    g = lin_grad([(0, "#c9dde0", 1), (1, "#aecacf", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="-1500" width="4200" height="{1500 + 1430}" fill="url(#{g})"/>')
    for x in range(-1400, 2500, 130):
        s.append(f'<rect x="{x}" y="-1500" width="54" height="{1500 + 1430}" fill="#b9d3d8" opacity=".55"/>')
    # плинтус и пол
    s.append(blob(rect_pts(-1500, 1366, 2700, 1430), "#fbf6ea"))
    s.append(line([(-1500, 1366), (2700, 1366)], 4, INK, taper=.02, wmin=1, seed=SEED + 600))
    gf = lin_grad([(0, "#c9a06c", 1), (1, "#a97f4f", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="1430" width="4200" height="1500" fill="url(#{gf})"/>')
    s.append(line([(-1500, 1430), (2700, 1430)], 5, INK, taper=.02, wmin=1, seed=SEED + 601))
    for k in range(1, 9):
        y = 1430 + k * 58 + k * k * 3
        s.append(line([(-1500, y), (2700, y + 4)], 3, "#8c6238", taper=.05, wmin=.9, seed=SEED + 610 + k, op=.5))
    # дверь туалета справа, закрыта; дрожит
    x, y, w, h = DOOR5
    shake = 3.2 * math.sin(t * 52) * (0.5 + 0.5 * smooth(HIT_HALF, 8.2, t)) if t > 6.7 else 0
    s.append(f'<g transform="translate({shake:.2f} 0)">')
    inside, clip_id, frame = door_frame_and_interior(x, y, w, h, SEED + 700)
    s.append(f'<rect x="{x - 26}" y="{y - 26}" width="{w + 52}" height="{h + 32}" fill="#8fb8c0"/>')
    s.append(frame)
    s.append(door_leaf(x, y, w, h, 1.0, SEED + 720))
    s.append("</g>")
    # часы
    pulse = 1 + 0.015 * math.sin(t * 38) * (1 if t > HIT_HALF - .1 else .5)
    cx, cy = CC5
    s.append(f'<g transform="translate({cx} {cy}) scale({pulse:.4f}) translate({-cx} {-cy})">{clock_face(t)}{clock_hands(t)}</g>')
    # Дима
    g, hip = dima5(t)
    s.append(fp.shadow(hip[0] + 60, 1442, 200, 22, .3, 10))
    s.append(g)
    # капля пота над головой + стресс-штрихи
    hx, hy = hip[0] + 190, hip[1] - 370
    k = (t * 1.6) % 1.0
    s.append(drop(hx - 90, hy - 20 + 40 * k, 24 * (0.8 + 0.4 * (1 - k)), SEED + 800))
    s.append(drop(hx + 70, hy + 10 + 40 * ((t * 1.6 + .5) % 1.0), 17, SEED + 810))
    for j in range(3):
        a = math.radians(-125 + j * 28)
        r0 = 150
        s.append(line([(hx - 10 + r0 * math.cos(a), hy + 60 + r0 * math.sin(a)), (hx - 10 + (r0 + 38 + 10 * math.sin(t * 20 + j)) * math.cos(a), hy + 60 + (r0 + 38 + 10 * math.sin(t * 20 + j)) * math.sin(a))],
                      7, "#2a2030", taper=.5, wmin=.3, seed=SEED + 820 + j))
    # тик-штрихи у часов на каждом обороте
    for t0 in (HIT_HALF, HIT_HALF + 0.82):
        e = t - t0
        if 0 < e < 0.5:
            s.append(fp.burst(cx, cy, e / 0.5, 12, R5 + 20, R5 + 110, 10, "#fff4c2", SEED + 830 + int(t0 * 10)))
    # камера: наезд на часы и тряска
    u = clamp((t - 6.7) / 2.2)
    sc = lerp(1.02, 1.3, ease_io(u))
    ccx, ccy = lerp(560, 540, u), lerp(860, 640, ease_io(u))
    rot = lerp(-1.5, 1.0, u) + 0.5 * math.sin(t * 2.5)
    for t0 in (HIT_HALF, HIT_HALF + 0.82, HIT_HALF + 1.6):
        e = t - t0
        if e > 0:
            kk = math.exp(-e * 9)
            sc *= 1 + 0.04 * kk
            ccy += 14 * kk * math.sin(e * 45)
            rot += 1.6 * kk * math.sin(e * 30)
    return svg(f'<rect width="{W}" height="{H}" fill="#aecacf"/><g transform="{cam(ccx, ccy, sc, rot)}">{"".join(s)}</g>')


def frame(sid, t):
    lib.dyn_begin()
    return s04_frame(t) if sid == "s04" else s05_frame(t)
