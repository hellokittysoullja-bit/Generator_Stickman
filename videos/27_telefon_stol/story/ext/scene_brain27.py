"""Сцена brain рилса 27 (s06, s07): мозг рилсов 24–26 с ручками (scene_brain.py / scene_brain26.py без изменений) в
той же ночной комнате; рядом на полу лежит телефон экраном вниз.
s06 «Мозг всё время ждёт, что экран сейчас загорится» (10.48–13.70): мозг сидит и старается смотреть в сторону, но правая
     ручка сама ползёт по полу к телефону (пальцы «шагают»); над мозгом мигает лампочка ожидания; на «загорится» (12.773)
     телефон вспыхивает краем (свет из-под корпуса), мозг дёргается к нему, кисть шлёпает на телефон.
s07 «и часть внимания уходит туда» (13.30–15.84): над мозгом шкала внимания из 10 делений (слева значок-глаз); из делений
     справа по одному вылетают огоньки и струйкой утекают в телефон, деление гаснет; к «туда» (14.96) погасла половина.
Ни одной буквы. Всё — функция общего времени ролика t."""
import math

import numpy as np

import brain_art
import lib
import scene_brain as sb
import scene_brain26 as sb26
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
FLASH = 12.773     # «загорится»
TUDA = 14.96       # «туда»
VNIM = 13.96       # «внимания»
FLOOR = sb.FLOOR   # 1160 — линия стены и пола
SQ = 0.42          # сжатие плоскости пола (вид чуть сверху)
PH = (858, 1236)   # центр телефона на полу
PH_ANG = -14


# ───────────────────────── телефон экраном вниз
def plane(pts, cx, cy, ang, sc=1.0):
    """Точки плоскости пола (вид сверху) → экран: поворот, масштаб, сжатие по y."""
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    out = []
    for p in pts:
        x, y = p[0] * sc, p[1] * sc
        q = (cx + x * c - y * s, cy + (x * s + y * c) * SQ)
        out.append(q + ((1,) if len(p) > 2 and p[2] else ()))
    return out


def phone_down(cx, cy, ang, glow, sd=0):
    """Чёрный телефон лежит экраном вниз: виден тыл с блоком камер; толщина корпуса — тёмный бортик снизу.
    glow 0..1 — экран загорелся: свет выходит из-под корпуса по краю."""
    L, Wd = 300, 150
    body = rect_pts(-L / 2, -Wd / 2, L / 2, Wd / 2, 26)
    s = []
    if glow > 0.01:
        g = rad_grad([(0, "#fff6c8", .95 * glow), (.35, "#ffe27a", .55 * glow), (1, "#ffcf5a", 0)], cx, cy + 6, 330 * (0.8 + .2 * glow),
                     150 * (0.8 + .2 * glow), rot=ang)
        s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy + 6)}" rx="{f(340)}" ry="{f(160)}" fill="url(#{g})"/>')
        # яркая кромка света прямо у корпуса
        rim = plane(rect_pts(-L / 2 - 10, -Wd / 2 - 10, L / 2 + 10, Wd / 2 + 10, 34), cx, cy + 10, ang)
        s.append(blob(rim, "#fffbe6", .85 * glow, blur(5)))
    side = [(x, y + 14) + ((1,) if len(p) > 2 else ()) for p, (x, y) in zip(body, [(q[0], q[1]) for q in plane(body, cx, cy, ang)])]
    s.append(shape(side, "#0c0d11", "", w=4.2, seed=sd + 1))
    top_pts = plane(body, cx, cy, ang)
    inner = blob(plane([(-L / 2, Wd * .1), (L / 2, Wd * .2), (L / 2, Wd / 2), (-L / 2, Wd / 2)], cx, cy, ang), "#14161c", .9)
    inner += blob(plane([(-L * .42, -Wd * .36), (L * .2, -Wd * .36), (L * .1, -Wd * .26), (-L * .44, -Wd * .26)], cx, cy, ang), "#4a5060", .8)
    s.append(shape(top_pts, "#22252e", inner, w=4.6, seed=sd + 2))
    # блок камер (на тыльной стороне, у короткого края)
    cam_blk = plane(rect_pts(-L / 2 + 22, -Wd / 2 + 18, -L / 2 + 92, -Wd / 2 + 88, 16), cx, cy, ang)
    s.append(shape(cam_blk, "#2f333e", "", w=3.2, seed=sd + 3))
    for k, (px, py, r) in enumerate([(-L / 2 + 42, -Wd / 2 + 38, 13), (-L / 2 + 72, -Wd / 2 + 38, 13), (-L / 2 + 42, -Wd / 2 + 68, 13)]):
        q = plane([(px, py)], cx, cy, ang)[0]
        s.append(shape(ellipse_pts(q[0], q[1], r, r * SQ * 1.4, 12), "#0b0c10",
                       blob(ellipse_pts(q[0] - 3, q[1] - 2, r * .35, r * .25, 8), "#7d8aa6", .9), w=2.6, seed=sd + 4 + k))
    q = plane([(-L / 2 + 72, -Wd / 2 + 68)], cx, cy, ang)[0]
    s.append(f'<circle cx="{f(q[0])}" cy="{f(q[1])}" r="5" fill="#e8e2c8"/>')
    if glow > 0.01:
        # свет по нижнему краю корпуса — бортик подсвечен снизу
        e = [p[:2] for p in plane([(-L / 2 + 20, Wd / 2 + 2), (0, Wd / 2 + 4), (L / 2 - 20, Wd / 2 + 2)], cx, cy + 16, ang)]
        s.append(line(e, 7, "#fff3b0", taper=.4, wmin=.3, seed=sd + 9, op=min(1, glow * 1.2)))
    return "".join(s)


def phone_rays(cx, cy, e, sd=0):
    """Лучи вспышки: короткие штрихи от телефона, разлетаются и тают за 0.5 с."""
    if e < 0 or e > 0.55:
        return ""
    s = []
    for k in range(9):
        a = -math.pi * (0.06 + 0.88 * k / 8)
        r0 = 150 + 150 * ease_out(e / .55)
        L = 60 * (1 - e / .55)
        p0 = (cx + math.cos(a) * r0 * 1.25, cy + math.sin(a) * r0 * .75)
        p1 = (cx + math.cos(a) * (r0 + L) * 1.25, cy + math.sin(a) * (r0 + L) * .75)
        s.append(line([p0, p1], 10, "#ffe27a", taper=.5, seed=sd + k))
    return "".join(s)


def buzz(cx, cy, t, amp):
    """Дрожь вибрации: пара дуг-скобок по бокам телефона."""
    if amp < 0.05:
        return ""
    s = []
    for side in (-1, 1):
        for j in range(2):
            r = 190 + j * 34 + 6 * math.sin(t * 40 + j)
            pts = [(cx + side * r, cy - 40), (cx + side * (r + 12), cy - 4), (cx + side * r, cy + 30)]
            s.append(line(pts, 6, "#ffe27a", taper=.4, seed=600 + j + (side > 0) * 3, op=amp * (1 - j * .35)))
    return "".join(s)


# ───────────────────────── лампочка ожидания
def bulb(x, y, on, sc=1.0, sd=0):
    """Лампочка: стеклянная колба, нить, цоколь. on 0..1 — накал (свечение вокруг)."""
    s = []
    if on > 0.02:
        g = rad_grad([(0, "#fff3b0", .85 * on), (.45, "#ffd75a", .35 * on), (1, "#ffd75a", 0)], x, y, 190 * sc, 190 * sc)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(200 * sc)}" fill="url(#{g})"/>')
    glass = mix("#5d6a98", "#fff0a0", on)
    sh = mix("#46527e", "#f2c94c", on)
    pts = []
    for k in range(26):
        a = 2 * math.pi * k / 26
        r = 62 * sc
        px, py = math.cos(a) * r, math.sin(a) * r
        if py > 22 * sc:          # сужение к цоколю
            px *= 1 - 0.55 * (py - 22 * sc) / (40 * sc)
        pts.append((x + px, y + py))
    inner = blob(ellipse_pts(x + 18 * sc, y + 16 * sc, 50 * sc, 46 * sc, 14), sh, .8)
    inner += blob(ellipse_pts(x - 24 * sc, y - 26 * sc, 14 * sc, 22 * sc, 10, rot=30), "#ffffff", .55 + .3 * on)
    fil = mix("#2a2f44", "#ff8a1e", on)
    inner += line([(x - 16 * sc, y + 40 * sc), (x - 14 * sc, y + 4 * sc), (x - 6 * sc, y - 6 * sc), (x, y + 4 * sc), (x + 6 * sc, y - 6 * sc),
                   (x + 14 * sc, y + 4 * sc), (x + 16 * sc, y + 40 * sc)], 4.2 * sc, fil, taper=.1, wmin=.8, seed=sd + 1)
    s.append(shape(pts, glass, inner, w=4.6 * sc, seed=sd + 2))
    for k in range(3):
        yy = y + (62 + k * 14) * sc
        s.append(shape(rect_pts(x - 28 * sc + k * 2 * sc, yy, x + 28 * sc - k * 2 * sc, yy + 14 * sc, 6 * sc), "#9aa3b8" if k % 2 == 0 else "#7b8399",
                       blob(rect_pts(x + 6 * sc, yy, x + 28 * sc, yy + 14 * sc), "#6b7389", .7), w=3.2 * sc, seed=sd + 3 + k))
    s.append(shape(ellipse_pts(x, y + 112 * sc, 12 * sc, 8 * sc, 8), "#3a3f52", "", w=2.6 * sc, seed=sd + 7))
    return "".join(s)


def blink_wait(t):
    """Мигание ожидания: короткие вспышки, неровный ритм — «а вдруг сейчас?»."""
    beats = [10.56, 11.02, 11.30, 11.78, 12.06, 12.40, 12.58]
    v = 0.12
    for b in beats:
        e = t - b
        if 0 <= e < 0.22:
            v = max(v, 0.85 * (1 - e / 0.22) ** 0.6)
    return v


# ───────────────────────── мозг
def brain_pose(t, lunge):
    breath = 1 + 0.012 * math.sin(t * 2.4)
    sc = 0.95
    # до вспышки мозг откинут назад и «не смотрит» (наклон от телефона), потом бросок к телефону
    lean = -9 + 2.5 * math.sin(t * 1.7)
    lean = lean * (1 - lunge) + 10 * lunge
    x = 470 + 46 * lunge
    y = FLOOR + 30 - 270 * sc - 6 * math.sin(t * 2.4) - 26 * lunge
    sq = 1 - 0.05 * lunge
    return sb26.Pose(x, y, sc * breath, lean, sq, -1.0)


def lunge_k(t):
    if t < FLASH:
        return 0.0
    e = t - FLASH
    return clamp(spring(e / 1.0 * 1.4, 1.3, 4.0)) * 0.9 + 0.1 * math.exp(-e * 4)


def s06(t):
    lunge = lunge_k(t)
    pose = brain_pose(t, lunge)
    # правая ручка: шажками ползёт к телефону (пальцы «шагают»), на вспышке — шлёп на телефон
    steps = [10.60, 11.05, 11.45, 11.86, 12.22, 12.52]
    start, goal = (570, 1200), (660, 1222)
    k = 0.0
    curl = 0.25
    for i, b in enumerate(steps):
        e = t - b
        if e > 0:
            k += ease_io(clamp(e / 0.24)) / len(steps)
            if e < 0.24:
                curl = 0.25 + 0.45 * math.sin(math.pi * e / 0.24)
    wr = (start[0] + (goal[0] - start[0]) * k, start[1] + (goal[1] - start[1]) * k - 10 * abs(math.sin(math.pi * k * len(steps))))
    ar = -4
    if t >= FLASH:
        e = t - FLASH
        u = ease_out(clamp(e / 0.14), 2)
        tgt = (PH[0] - 60, PH[1] - 34)
        wr = (wr[0] + (tgt[0] - wr[0]) * u, wr[1] + (tgt[1] - wr[1]) * u - 40 * math.sin(math.pi * u) * (u < 1))
        ar = -4 - 8 * u
        curl = 0.25 + 0.35 * math.exp(-e * 6)
    # левая ручка: упирается в пол за спиной, будто держит себя (ладонь вниз), на вспышке взлетает
    wl = (318 + 6 * math.sin(t * 2.1), 1196 + 4 * math.sin(t * 2.4))
    al = 186
    cl = 0.15
    if t >= FLASH:
        e = t - FLASH
        u = ease_out(clamp(e / 0.2), 2)
        wl = (wl[0] + (345 - wl[0]) * u, wl[1] + (880 - wl[1]) * u + 12 * math.sin(e * 9) * u)
        al = 186 + (-130 - 186) * u
        cl = 0.15 * (1 - u)
    glow = 0.0
    shake = (0.0, 0.0)
    if t >= FLASH:
        e = t - FLASH
        glow = clamp(e / 0.05) * (0.55 + 0.45 * math.exp(-e * 3.0)) * (0.92 + 0.08 * math.sin(e * 22))
        shake = (5 * math.exp(-e * 8) * math.sin(e * 70), 3 * math.exp(-e * 8) * math.sin(e * 55))
    ph_svg = phone_down(PH[0] + shake[0], PH[1] + shake[1], PH_ANG, glow, sd=300)
    hands_over = t >= FLASH and (t - FLASH) > 0.1
    art = sb.shadow(pose.x + 10, FLOOR + 32, 190, .5)
    art += ph_svg if not hands_over else ""
    body = sb26.body(pose, _ST["brain"], wl, wr, al, ar, cl, curl, bl=-60, br=40, sd=0)
    art += body
    if hands_over:
        # кисть уже на телефоне — телефон под ней: рисуем телефон ДО кисти, но после ручки
        art = sb.shadow(pose.x + 10, FLOOR + 32, 190, .5) + ph_svg + body
    art += phone_rays(PH[0], PH[1], t - FLASH, sd=400) + buzz(PH[0], PH[1], t, 1.0 * math.exp(-max(t - FLASH, 0) * 4) * (t >= FLASH))
    # лампочка ожидания над мозгом
    on = blink_wait(t)
    if t >= FLASH:
        on = max(on, 1.0 * math.exp(-(t - FLASH) * 1.2))
    bob = 8 * math.sin(t * 2.2)
    bsc = 0.9 * (1 + 0.12 * math.exp(-max(t - FLASH, 0) * 6) * (t >= FLASH))
    art += bulb(pose.x - 10, 640 + bob, on, bsc, sd=500)
    # «!»-удары у лампы на вспышке — штрихи, не буква
    e = t - FLASH
    if 0 <= e < 0.4:
        for k in range(6):
            a = -math.pi / 2 + (k - 2.5) * 0.42
            r0 = 110 + 90 * ease_out(e / .4)
            L = 36 * (1 - e / .4)
            cx, cy = pose.x - 10, 640 + bob
            art += line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + L), cy + math.sin(a) * (r0 + L))],
                        8, "#ffe27a", taper=.5, seed=520 + k)
    u = clamp((t - 10.48) / 3.22)
    push = 0.05 * math.exp(-max(t - FLASH, 0) * 5) * (t >= FLASH)
    cm = cam(640 + 16 * u + 24 * lunge, 1000 + 10 * u, 1.30 + 0.08 * ease_io(u) + push, 0.6 - 1.0 * u)
    return art, cm


# ───────────────────────── s07: шкала внимания
BAR = (300, 590, 970, 680)      # x0, y0, x1, y1 (мир)
NC = 10


def cell_box(i):
    x0, y0, x1, y1 = BAR
    pad = 18
    x0 += 96               # слева место под значок-глаз
    cw = (x1 - x0 - pad * 2) / NC
    return (x0 + pad + i * cw + 4, y0 + pad, x0 + pad + (i + 1) * cw - 4, y1 - pad)


def leave_times():
    """Когда гаснет деление: справа налево, пятое — ровно на «туда»."""
    return {9: 13.98, 8: 14.30, 7: 14.58, 6: 14.80, 5: TUDA}


def eye_icon(x, y, sc, sd):
    s = []
    pts = [(x - 46 * sc, y, 1), (x, y - 26 * sc), (x + 46 * sc, y, 1), (x, y + 26 * sc)]
    s.append(shape(pts, "#fbf6e8", "", w=4 * sc, seed=sd))
    s.append(shape(ellipse_pts(x, y, 18 * sc, 18 * sc, 14), "#3b7fd0", f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(8 * sc)}" fill="{INK}"/>'
                   f'<circle cx="{f(x - 5 * sc)}" cy="{f(y - 5 * sc)}" r="{f(3 * sc)}" fill="#fff"/>', w=3 * sc, seed=sd + 1))
    return "".join(s)


def gauge(t, lost):
    """Шкала: капсула с 10 делениями; lost[i] 0..1 — насколько погасло деление i."""
    x0, y0, x1, y1 = BAR
    s = []
    s.append(blob(rect_pts(x0 + 8, y0 + 12, x1 + 8, y1 + 12, 44), "#10162e", .45, blur(6)))
    inner = blob(rect_pts(x0, (y0 + y1) / 2, x1, y1, 44), "#1c2444", .7)
    s.append(shape(rect_pts(x0, y0, x1, y1, 44), "#2a3460", inner, w=5.4, seed=700))
    s.append(eye_icon(x0 + 62, (y0 + y1) / 2, 1.0, 710))
    for i in range(NC):
        cx0, cy0, cx1, cy1 = cell_box(i)
        k = lost[i]
        on = mix("#ffd23f", "#3a4470", k)
        hi = mix("#fff4b8", "#4a5482", k)
        if k < 0.98:
            g = rad_grad([(0, "#ffe27a", .45 * (1 - k)), (1, "#ffe27a", 0)], (cx0 + cx1) / 2, (cy0 + cy1) / 2, 46, 52)
            s.append(f'<ellipse cx="{f((cx0 + cx1) / 2)}" cy="{f((cy0 + cy1) / 2)}" rx="48" ry="54" fill="url(#{g})"/>')
        s.append(shape(rect_pts(cx0, cy0, cx1, cy1, 10), on, blob(rect_pts(cx0, cy0, cx1, cy0 + 12, 6), hi, .9), w=3.4, seed=720 + i))
    return "".join(s)


def stream_path(u, t, j=0):
    """Путь струйки: от деления/макушки мозга дугой вниз к телефону. u 0..1."""
    p0 = (690, 790)
    p1 = (930, 760)
    p2 = (PH[0] + 10, PH[1] - 20)
    x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
    y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
    w = 10 * math.sin(math.pi * u) * math.sin(t * 6 + u * 9 + j)
    return x + w, y


def s07(t):
    lt = leave_times()
    lost = [0.0] * NC
    sparks = []
    for i, tt in lt.items():
        lost[i] = smooth(tt - 0.06, tt + 0.08, t)
        # огонёк вылетает из деления и по дуге уходит в телефон за 0.55 с
        e = t - (tt - 0.05)
        if 0 <= e < 0.6:
            cx0, cy0, cx1, cy1 = cell_box(i)
            c = ((cx0 + cx1) / 2, (cy0 + cy1) / 2)
            u = ease_in(e / 0.6, 1.4)
            if u < 0.3:            # из деления — вниз к лобной доле мозга, где начинается струйка
                v = ease_io(u / 0.3)
                q0 = stream_path(0, t, i)
                x = c[0] + (q0[0] - c[0]) * v + 40 * math.sin(math.pi * v)
                y = c[1] + (q0[1] - c[1]) * v
            else:
                x, y = stream_path((u - 0.3) / 0.7, t, i)
            sparks.append((x, y, 1 - 0.5 * u))
    sad = 0.45 * smooth(13.9, 15.1, t)
    breath = 1 + 0.012 * math.sin(t * 2.4)
    droop = smooth(13.9, 15.2, t)
    pose = sb26.Pose(480, FLOOR + 30 - 270 * 0.95 - 6 * math.sin(t * 2.4) + 14 * droop, 0.95 * breath, 6 + 3 * math.sin(t * 1.5) - 4 * droop,
                     1 - 0.04 * droop, -1.0)
    bsvg = brain_art.brain(0, sad)
    # правая кисть на телефоне (как в конце s06), левая подпирает щёку-бок
    wr = (PH[0] - 60 + 3 * math.sin(t * 3), PH[1] - 34)
    wl = (330 + 6 * math.sin(t * 2), 1192 + 4 * math.sin(t * 2.3))
    jolt = 0.0
    if t >= TUDA:
        e = t - TUDA
        jolt = math.exp(-e * 7) * math.sin(e * 40)
    glow = 0.25 + 0.5 * smooth(13.9, 15.0, t) + 0.25 * math.exp(-max(t - TUDA, 0) * 4) * (t >= TUDA)
    glow *= 0.92 + 0.08 * math.sin(t * 9)
    art = sb.shadow(pose.x + 10, FLOOR + 32, 190, .5)
    art += phone_down(PH[0], PH[1], PH_ANG, glow, sd=300)
    art += sb26.body(pose, bsvg, wl, wr, 160, -12, 0.2, 0.35, bl=-50, br=40, sd=0)
    # струйка: тонкий поток огоньков всё время, гуще, пока гаснут деления
    flow = 0.35 + 0.65 * smooth(13.85, 14.1, t) * (1 - 0.6 * smooth(TUDA + 0.2, TUDA + 0.8, t))
    rs = np.random.RandomState(3)
    pts = []
    for j in range(46):
        ph = rs.uniform(0, 1)
        sp = rs.uniform(0.55, 0.9)
        u = (ph + t * sp) % 1
        if rs.uniform() > flow:
            continue
        q = stream_path(u, t, j * .7)
        r = (3.5 + 4 * rs.uniform()) * (0.6 + 0.4 * math.sin(math.pi * u))
        pts.append((q[0], q[1], r))
    st = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#ffe27a"/>' for x, y, r in pts)
    halo = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 3)}" fill="#ffd23f" opacity=".22"/>' for x, y, r in pts)
    # лента струйки (мягкая, под огоньками)
    rib = [stream_path(k / 30, t, 0) for k in range(31)]
    art += line(rib, 16, "#ffd23f", taper=.4, wmin=.25, seed=760, op=.22 * flow)
    art += halo + st
    for (x, y, a) in sparks:
        g = rad_grad([(0, "#fff8d0", .95 * a), (.4, "#ffd23f", .6 * a), (1, "#ffd23f", 0)], x, y, 46, 46)
        art += f'<circle cx="{f(x)}" cy="{f(y)}" r="46" fill="url(#{g})"/>'
        art += f'<circle cx="{f(x)}" cy="{f(y)}" r="11" fill="#fff6c0"/>'
    gy = 6 * jolt
    art += f'<g transform="translate(0 {f(gy)})">{gauge(t, lost)}</g>'
    # на «туда»: вспышка-обводка вокруг погасшей половины
    e = t - TUDA
    if 0 <= e < 0.5:
        x0, y0, _, y1 = cell_box(5)
        _, _, x1, _ = cell_box(9)
        a = 1 - e / 0.5
        art += shape(rect_pts(x0 - 14 - 30 * e, y0 - 14 - 30 * e, x1 + 14 + 30 * e, y1 + 14 + 30 * e, 16), "none", "", w=6, seed=780,
                     ink_color="#ffe27a", attrs=f'opacity="{a:.3f}"')
    u = clamp((t - 13.3) / 2.54)
    cm = cam(645 - 10 * u, 960 + 12 * u, 1.24 + 0.03 * u + 0.012 * jolt, -0.3 + 0.5 * u)
    return art, cm


def build_static():
    if _ST:
        return
    sb.build_static()
    _ST["bg"] = sb._ST["bg"]
    _ST["brain"] = sb._ST["brain"]
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s06": s06, "s07": s07}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{_ST["bg"]}{sb.dust(t)}{art}</g>')
