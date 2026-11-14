"""Группа C рилса 46, сцена study: s08 (15.1–17.5) и s09 (17.5–20.0), опыт в Пенсильвании. Надписей-логотипов нет.
s08: кирпичный корпус лаборатории (черепица, флаг), в шести окнах спят люди на кроватях (по одному в окне); на плашке
     «ПЕНСИЛЬВАНИЯ»; на «две недели» (16.24) сверху падает календарь и 14 клеток по очереди зачёркиваются красным крестом;
     на «шесть» (17.4) над кроватями одна за другой вспыхивают шесть лун.
s09: лаборатория, большой экран теста внимания, за тремя партами люди нажимают кнопки на появляющиеся кружки; на «тесты»
     (18.76) кружки прыгают по экрану очередью; на «внимание» (19.2) крупно уставший глаз (веко, мешок), зрачок бегает за кружками.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import study28 as st
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rect_pts, shape, smooth, svg)

_ST = {}
BRICK, BRICK_SH, BRICK_DK, TRIM = st.BRICK, st.BRICK_SH, st.BRICK_DK, st.TRIM
CAL_T = 16.24      # «две недели»
SIX_T = 17.40      # «шесть»
TESTS = 18.76      # «тесты»
EYE_T = 19.20      # «внимание»
GB = 1290          # земля s08


def text(x, y, s, size, fill="#ffffff", rot=0.0, sc=1.0, stroke=INK, sw=9):
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">'
            f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="{size}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" paint-order="stroke" stroke-linejoin="round">{s}</text></g>')


def star8(x, y, k, col="#ffe27a", rot=0.0):
    pts = []
    for i in range(8):
        rr = (22 if i % 2 == 0 else 7) * k
        a = i * math.pi / 4 + math.radians(rot)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    return blob(pts, col, .97)


# ═════════════════════════════ s08
WIN_X = [110, 410, 710]
WIN_Y = [650, 960]
WW, WH = 260, 270
SLEEP = [  # кожа, волосы, причёска, одеяло, подушка
    ("#f0c4a0", "#5a3a26", "short", "#3f7fd0", "#f6f1e4"),
    ("#8a5a3c", "#2a1a14", "curly", "#d9573f", "#f6f1e4"),
    ("#f4d0b4", "#c8622a", "ponytail", "#3a9a6a", "#f6f1e4"),
    ("#d9a07a", "#2a1a14", "bun", "#8a5ac8", "#f6f1e4"),
    ("#e8b896", "#9a7a66", "bald", "#e0a03a", "#f6f1e4"),
    ("#f2c9a8", "#e0b050", "bob", "#d9467a", "#f6f1e4"),
]


def crescent(x, y, r, sd):
    P0 = (x + .38 * r, y - .925 * r)
    P1 = (x + .38 * r, y + .925 * r)
    d = (f'M{f(P0[0])} {f(P0[1])} A{f(r)} {f(r)} 0 1 0 {f(P1[0])} {f(P1[1])} A{f(r * .78)} {f(r * .78)} 0 0 1 {f(P0[0])} {f(P0[1])}Z')
    return (f'<path d="{d}" fill="#ffd84a" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>'
            f'<path d="M{f(x - .55 * r)} {f(y - .5 * r)} A{f(r * .8)} {f(r * .8)} 0 0 0 {f(x - .55 * r)} {f(y + .5 * r)}" fill="none" '
            f'stroke="#fff6c8" stroke-width="5" stroke-linecap="round"/>')


def sleeper_window(i, t):
    col, row = i % 3, i // 3
    x0, y0 = WIN_X[col], WIN_Y[row]
    sk, hc, hair, blank, pil = SLEEP[i]
    ph = i * 0.9
    br = math.sin(t * 2.0 + ph)
    c = lib.clip_rect(x0, y0, WW, WH)
    s = []
    inner = []
    # стена ночью и пол
    inner.append(f'<rect x="{x0}" y="{y0}" width="{WW}" height="{WH}" fill="#34427c"/>')
    inner.append(blob(rect_pts(x0, y0, x0 + WW, y0 + 70), "#2c386c"))
    inner.append(blob(rect_pts(x0, y0 + WH - 56, x0 + WW, y0 + WH), "#5a4468"))
    inner.append(line([(x0, y0 + WH - 56), (x0 + WW, y0 + WH - 56)], 3.4, INK, taper=.05, wmin=.9, seed=3100 + i))
    yb = y0 + WH - 56          # линия пола
    # кровать: ножки, рама, матрас
    inner.append(shape(rect_pts(x0 + 14, yb - 76, x0 + 30, yb + 4), "#6b4a2e", "", w=3, seed=3110 + i))
    inner.append(shape(rect_pts(x0 + WW - 30, yb - 56, x0 + WW - 14, yb + 4), "#6b4a2e", "", w=3, seed=3120 + i))
    inner.append(shape(rect_pts(x0 + 8, yb - 150, x0 + 34, yb - 38, 6), "#8a5f3c", blob(rect_pts(x0 + 22, yb - 150, x0 + 34, yb - 38), "#6b4a2e", .8), w=3.6, seed=3130 + i))
    inner.append(shape(rect_pts(x0 + 8, yb - 62, x0 + WW - 8, yb - 36, 6), "#8a5f3c", "", w=3.4, seed=3140 + i))
    inner.append(shape(rect_pts(x0 + 30, yb - 92, x0 + WW - 10, yb - 56, 12), "#f4f0e6", blob(rect_pts(x0 + 30, yb - 70, x0 + WW - 10, yb - 56, 6), "#d8d2c0", .8), w=3.6, seed=3150 + i))
    # подушка и голова
    hx, hy = x0 + 82, yb - 112 + 1.2 * br
    inner.append(shape(rect_pts(x0 + 36, hy + 6, x0 + 128, hy + 52, 18), pil, blob(rect_pts(x0 + 88, hy + 6, x0 + 128, hy + 52, 14), "#ded7c4", .8), w=3.4, seed=3160 + i))
    if hair == "ponytail":
        inner.append(shape([(hx - 30, hy), (hx - 62, hy + 8), (hx - 64, hy + 42), (hx - 40, hy + 36)], hc, "", w=3.4, seed=3170 + i))
    if hair == "bun":
        inner.append(shape(ellipse_pts(hx - 6, hy - 40, 16, 13, 10), hc, "", w=3.2, seed=3171 + i))
    head = ellipse_pts(hx, hy + 10, 38, 40, 18)
    face_in = ""
    if hair != "bald":
        hp = [(hx - 40, hy + 8), (hx - 36, hy - 20), (hx - 10, hy - 34), (hx + 20, hy - 30), (hx + 38, hy - 8), (hx + 14, hy - 12), (hx - 16, hy - 8), (hx - 30, hy + 12)]
        if hair == "curly":
            hp = [(hx - 44, hy + 10), (hx - 46, hy - 14), (hx - 30, hy - 36), (hx, hy - 42), (hx + 30, hy - 34), (hx + 44, hy - 10), (hx + 14, hy - 12), (hx - 16, hy - 8), (hx - 30, hy + 14)]
        face_in += blob(hp, hc)
    else:
        face_in += blob([(hx + 8, hy - 26), (hx + 30, hy - 14), (hx + 36, hy + 20), (hx + 14, hy + 44), (hx + 22, hy + 6)], lib.mul(sk, (.9, .86, .86)), .8)
    s_eye = lambda ex: line([(ex - 10, hy + 4), (ex, hy + 12), (ex + 10, hy + 4)], 3.6, INK, taper=.3, wmin=.5, seed=3180 + i + int(ex))
    inner.append(shape(head, sk, face_in + s_eye(hx - 12) + s_eye(hx + 14) +
                       blob(ellipse_pts(hx - 22, hy + 22, 8, 5, 8), "#f07a98", .55) + blob(ellipse_pts(hx + 26, hy + 22, 8, 5, 8), "#f07a98", .55) +
                       line([(hx - 4, hy + 30), (hx + 6, hy + 32)], 3, "#8a3a3a", taper=.3, seed=3190 + i), w=3.8, seed=3200 + i))
    # одеяло
    bt = yb - 108 + 2.2 * br
    bpts = [(hx + 20, bt + 30, 1), (hx + 40, bt + 6), (hx + 80, bt - 8), (x0 + WW - 10, bt - 2, 1), (x0 + WW - 10, yb - 36, 1), (hx + 14, yb - 36, 1), (hx + 8, bt + 50)]
    bin_ = blob([(hx + 60, bt - 8), (x0 + WW - 10, bt - 2), (x0 + WW - 10, yb - 36), (hx + 100, yb - 36)], lib.mul(blank, (.78, .78, .82)), .8)
    bin_ += line([(hx + 40, bt + 20), (hx + 96, bt + 56)], 3, lib.mul(blank, (.62, .62, .7)), taper=.3, seed=3210 + i, op=.8)
    bin_ += line([(hx + 90, bt + 4), (hx + 140, bt + 48)], 3, lib.mul(blank, (.62, .62, .7)), taper=.3, seed=3215 + i, op=.8)
    inner.append(shape(bpts, blank, bin_, w=3.8, seed=3220 + i))
    # zzz
    for k in range(3):
        u = ((t * 0.55 + ph * .3 + k / 3) % 1)
        zx, zy = hx + 46 + 30 * u + 6 * math.sin(u * 8), hy - 44 - 90 * u
        r = 9 * math.sin(math.pi * min(u * 1.1, 1)) + 1
        pts = [(zx - r, zy - r), (zx + r, zy - r), (zx - r, zy + r), (zx + r, zy + r)]
        inner.append(line(pts, 5.5, "#dbe6ff", taper=.1, wmin=.8, seed=3230 + i * 3 + k))
    # луна на «шесть»
    e = t - (SIX_T + 0.05 * i)
    if e > 0:
        k = back_out(clamp(e / 0.18), 2.6)
        mx, my = x0 + WW * .72, y0 + 58
        inner.append(f'<g transform="translate({f(mx)} {f(my)}) scale({f(k)}) rotate({f(-14 * (1 - clamp(e / .25)))}) translate({f(-mx)} {f(-my)})">{crescent(mx, my, 34, 3300 + i)}</g>')
        if e < 0.3:
            for q in range(6):
                a = q * math.pi / 3 + .4
                r0 = 54 + 40 * ease_out(e / .3)
                inner.append(line([(mx + math.cos(a) * r0, my + math.sin(a) * r0), (mx + math.cos(a) * (r0 + 14 * (1 - e / .3)), my + math.sin(a) * (r0 + 14 * (1 - e / .3)))],
                                  5, "#ffe27a", taper=.5, seed=3340 + q))
    s.append(f'<g clip-path="url(#{c})">{"".join(inner)}</g>')
    # рама окна и подоконник
    s.append(shape(rect_pts(x0 - 10, y0 - 10, x0 + WW + 10, y0 + WH + 10), "none", "", w=0, ink=False))
    fr = rect_pts(x0 - 12, y0 - 12, x0 + WW + 12, y0 + WH + 12)
    s.append(f'<path d="{lib.fill_d(fr)}" fill="none" stroke="{TRIM}" stroke-width="20"/>')
    s.append(lib.shape(rect_pts(x0, y0, x0 + WW, y0 + WH), "none", "", w=3.6, seed=3350 + i, ink=True).replace('fill="none"', 'fill="none"'))
    s.append(shape(rect_pts(x0 - 22, y0 + WH + 10, x0 + WW + 22, y0 + WH + 26), TRIM, blob(rect_pts(x0 - 22, y0 + WH + 20, x0 + WW + 22, y0 + WH + 26), "#cfc6b4"), w=3.2, seed=3360 + i))
    return "".join(s)


def facade():
    s = []
    gx0, gx1, top = 60, 1020, 560
    roof = [(gx0 - 30, top), (gx0 + 70, top - 100), (gx1 - 70, top - 100), (gx1 + 30, top)]
    rin = blob([(gx0 + 70, top - 100), (gx1 - 70, top - 100), (gx1 - 60, top - 84), (gx0 + 60, top - 84)], "#e07a52")
    for k in range(5):
        y = top - 20 - k * 19
        rin += line([(gx0 - 10 + k * 20, y), (gx1 + 10 - k * 20, y)], 3, "#8f3a24", seed=3400 + k, op=.7)
    s.append(shape(roof, "#c4593a", rin, w=4.6, seed=3410))
    fac = rect_pts(gx0, top, gx1, GB)
    inner = f'<rect x="{gx0}" y="{top}" width="{gx1 - gx0}" height="{GB - top}" fill="url(#pBrick)"/>'
    inner += blob([(gx1 - 90, top), (gx1, top), (gx1, GB), (gx1 - 40, GB)], BRICK_DK, .35)
    s.append(shape(fac, BRICK, inner, w=5, seed=3420))
    s.append(shape(rect_pts(gx0 - 18, top - 10, gx1 + 18, top + 14), TRIM, blob(rect_pts(gx0 - 18, top + 6, gx1 + 18, top + 14), "#cfc6b4"), w=4, seed=3421))
    s.append(shape(rect_pts(gx0 - 10, GB - 36, gx1 + 10, GB), "#d9cfbd", blob(rect_pts(gx0 - 10, GB - 14, gx1 + 10, GB), "#b9ae99"), w=4, seed=3422))
    # межэтажный пояс
    s.append(shape(rect_pts(gx0, 925, gx1, 941), TRIM, "", w=3.4, seed=3423))
    return "".join(s)


def ground8():
    s = [f'<rect x="-600" y="{GB - 6}" width="{W + 1200}" height="{H + 600}" fill="#7fb35e"/>']
    s.append(blob(rect_pts(-600, GB + 40, W + 600, H + 600), "#e6cf9c"))
    s.append(line([(-500, GB - 6), (W + 500, GB - 6)], 4, INK, taper=.1, wmin=.8, seed=3430))
    s.append(line([(-500, GB + 40), (W + 500, GB + 40)], 3, "#5a8a42", taper=.1, wmin=.8, seed=3431))
    return "".join(s)


def sky8():
    lin_grad([(0, "#5aa6ea", 1), (.6, "#a6d4f5", 1), (1, "#f4ead2", 1)], 0, 0, 0, 1, gid="gSky46")
    return f'<rect x="-700" y="-900" width="{W + 1400}" height="{GB + 900}" fill="url(#gSky46)"/>'


def flag(t):
    x, y = 540, 460
    s = [line([(x, y), (x, y - 190)], 7, "#5a5f6e", taper=.05, wmin=.9, seed=3500)]
    s.append(shape(ellipse_pts(x, y - 196, 9, 9, 10), "#e8c35a", "", w=2.6, seed=3501))
    pts_top, pts_bot = [], []
    for k in range(11):
        u = k / 10
        w = 7 * u * math.sin(t * 5 - u * 5)
        pts_top.append((x + 8 + 150 * u, y - 186 + w))
        pts_bot.append((x + 8 + 150 * u, y - 120 + w * 1.1))
    pts = pts_top + pts_bot[::-1]
    s.append(shape(pts, "#2f6db5", blob([(p[0], p[1]) for p in pts_top[4:]] + [(p[0], p[1] - 10) for p in pts_bot[4:][::-1]], "#2557a0", .6) +
                   star8(x + 54, y - 154 + 3 * math.sin(t * 5 - .6), 1.1, "#ffffff"), w=3.6, seed=3502))
    return "".join(s)


def plaque(t):
    k = back_out(clamp((t - 14.98) / 0.3), 2.4)
    if k < 0.02:
        return ""
    x, y, w, h = 540, 602, 640, 62
    pts = rect_pts(-w / 2, -h / 2, w / 2, h / 2, 10)
    body = shape(pts, "#1f4d3c", blob(rect_pts(50, -h / 2, w / 2, h / 2), "#173a2d", .8) + blob(rect_pts(-w / 2 + 8, -h / 2 + 6, w / 2 - 8, -h / 2 + 12), "#2f6a54", .8), w=4.2, seed=3510)
    body += text(0, 18, "ПЕНСИЛЬВАНИЯ", 48, "#fff3c4", sw=0, stroke="none")
    return f'<g transform="translate({x} {y}) scale({f(k)})">{body}</g>'


def calendar(t):
    e = t - 15.62
    if e < 0:
        return ""
    # падает сверху с пружиной
    y_off = -560 * (1 - back_out(clamp(e / 0.5), 1.9))
    cx0, cy0, cx1, cy1 = 120, 100, 960, 420
    s = []
    card = rect_pts(cx0, cy0, cx1, cy1, 18)
    s.append(shape(card, "#fbf8ee", blob(rect_pts(cx0 + 520, cy0, cx1, cy1, 18), "#ece4d0", .7), w=5, seed=3600))
    s.append(shape(rect_pts(cx0, cy0, cx1, cy0 + 72, 18), "#d9433a", blob(rect_pts(cx0 + 520, cy0, cx1, cy0 + 72, 18), "#b5302a", .7), w=5, seed=3601))
    s.append(text((cx0 + cx1) / 2, cy0 + 54, "14 ДНЕЙ", 50, "#ffffff", sw=0, stroke="none"))
    for k in range(5):
        rx = cx0 + 90 + k * 165
        s.append(shape(rect_pts(rx - 7, cy0 - 22, rx + 7, cy0 + 16, 6), "#5a5f6e", "", w=3, seed=3602 + k))
    cw, ch = 108, 108
    for n in range(14):
        r, c = divmod(n, 7)
        x = cx0 + 40 + c * (cw + 12)
        y = cy0 + 92 + r * (ch + 10)
        ti = CAL_T + n * 0.062
        e2 = t - ti
        done = e2 > 0
        cell = rect_pts(x, y, x + cw, y + ch, 10)
        s.append(shape(cell, "#f1e8cf" if done else "#ffffff", blob(rect_pts(x + 60, y, x + cw, y + ch, 10), "#dcd2b8", .5), w=3.4, seed=3610 + n))
        s.append(text(x + cw / 2, y + 44, str(n + 1), 38, "#3a3440", sw=0, stroke="none"))
        if done:
            u = clamp(e2 / 0.12)
            m = 20
            p1 = [(x + m, y + m), (x + m + (cw - 2 * m) * min(1, u * 2), y + m + (ch - 2 * m) * min(1, u * 2))]
            s.append(line(p1, 11, "#e0301f", taper=.15, wmin=.8, seed=3640 + n))
            if u > .5:
                v = (u - .5) * 2
                s.append(line([(x + cw - m, y + m), (x + cw - m - (cw - 2 * m) * v, y + m + (ch - 2 * m) * v)], 11, "#e0301f", taper=.15, wmin=.8, seed=3660 + n))
            if e2 < 0.2:
                pk = 1 + .1 * math.sin(math.pi * e2 / .2)
                s[-1] = s[-1]
    # перелистывание: маркер-«рука» не рисуем, акцент — удар камеры в сцене
    return f'<g transform="translate(0 {f(y_off)})">{"".join(s)}</g>'


def s08(t):
    art = [_ST["sky"], st.sun(t), st.clouds(t), flag(t), _ST["facade"]]
    for i in range(6):
        art.append(sleeper_window(i, t))
    art += [plaque(t), _ST["ground"], calendar(t)]
    # искры от крестов
    for n in range(14):
        e2 = t - (CAL_T + n * 0.062)
        if 0 <= e2 < 0.25:
            r, c = divmod(n, 7)
            x, y = 120 + 40 + c * 120 + 54, 100 + 92 + r * 118 + 54
            for q in range(5):
                a = q * 1.256 + n
                r0 = 62 + 34 * ease_out(e2 / .25)
                art.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + 14 * (1 - e2 / .25)), y + math.sin(a) * (r0 + 14 * (1 - e2 / .25)))],
                                6, "#ff8a6a", taper=.5, seed=3700 + q))
    # камера: влёт от неба к зданию с кадра 0, толчки на календаре и на лунах
    u = clamp((t - 14.9) / 2.8)
    scl = 1.0 + 0.1 * ease_out(u, 2)
    cy = 640 + 150 * u
    rot = 3.5 * (1 - ease_out(clamp((t - 14.9) / 0.9), 3)) - 0.5 * u
    e = t - CAL_T
    if e > 0:
        scl *= 1 + 0.03 * math.exp(-e * 6) * math.sin(min(e * 14, math.pi))
    e = t - SIX_T
    if e > 0:
        scl *= 1 + 0.04 * math.exp(-e * 5) * math.sin(min(e * 14, math.pi))
        cy += 6 * math.exp(-e * 8) * math.sin(e * 50)
    return "".join(art), cam(540, cy, scl, rot)


# ═════════════════════════════ s09
STUDENTS = [st.STUDENTS[0], st.STUDENTS[3], st.STUDENTS[2]]
SCR = (110, 150, 970, 640)     # экран теста на стене
EVENTS = [17.62, 18.04, 18.42] + [TESTS + 0.0 + 0.135 * k for k in range(13)]


def lab_wall():
    s = []
    lin_grad([(0, "#f3e6c8", 1), (1, "#e8d6b0", 1)], 0, 0, 0, 1, gid="gWall46")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{1400 + 900}" fill="url(#gWall46)"/>')
    lin_grad([(0, "#b9824e", 1), (1, "#a0693c", 1)], 0, 0, 0, 1, gid="gFloor46")
    fl = 1250
    s.append(f'<rect x="-900" y="{fl}" width="{W + 1800}" height="{H + 900}" fill="url(#gFloor46)"/>')
    for k in range(-8, 18):
        x = 540 + k * 120
        s.append(line([(540 + (x - 540) * .7, fl), (540 + (x - 540) * 2.2, H + 400)], 2.4, "#8a5a32", taper=.1, wmin=.8, seed=4600 + k, op=.7))
    s.append(line([(-900, fl), (W + 900, fl)], 4, INK, taper=.05, wmin=.9, seed=4620))
    s.append(blob(rect_pts(-900, fl - 34, W + 900, fl), "#c9a77a"))
    s.append(blob(rect_pts(-900, -900, W + 900, 80), "#e6d3ac"))
    s.append(line([(-900, 80), (W + 900, 80)], 4, INK, taper=.05, wmin=.9, seed=4621))
    # рама экрана
    x0, y0, x1, y1 = SCR
    s.append(shape(rect_pts(x0 - 24, y0 - 24, x1 + 24, y1 + 24, 22), "#2b2f3a", blob(rect_pts(x1 - 140, y0 - 24, x1 + 24, y1 + 24, 22), "#1f232c", .8), w=5, seed=4630))
    s.append(shape(rect_pts(x0, y0, x1, y1, 10), "#10182e", "", w=3.4, seed=4631))
    return "".join(s)


def target_pos(k):
    rs = np.random.RandomState(40 + k)
    x0, y0, x1, y1 = SCR
    return (rs.uniform(x0 + 90, x1 - 90), rs.uniform(y0 + 90, y1 - 90))


def screen_art(t):
    x0, y0, x1, y1 = SCR
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0, 10)
    s = []
    for k in range(1, 6):
        s.append(line([(x0 + k * 143, y0), (x0 + k * 143, y1)], 2.4, "#1e2a4e", taper=.05, wmin=.9, seed=4700 + k))
    for k in range(1, 4):
        s.append(line([(x0, y0 + k * 128), (x1, y0 + k * 128)], 2.4, "#1e2a4e", taper=.05, wmin=.9, seed=4710 + k))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s.append(line([(cx - 40, cy), (cx + 40, cy)], 4, "#3a4a7e", taper=.05, wmin=.9, seed=4720))
    s.append(line([(cx, cy - 40), (cx, cy + 40)], 4, "#3a4a7e", taper=.05, wmin=.9, seed=4721))
    # развёртка луча — полоска «сканера» едет сверху вниз с кадра 0
    sy = y0 + ((t * 260) % (y1 - y0))
    s.append(blob(rect_pts(x0, sy - 5, x1, sy + 5), "#2a3b72"))
    for k, te in enumerate(EVENTS):
        dur = 0.34 if k < 3 else 0.135
        e = t - te
        if -0.02 < e < dur + 0.25:
            px, py = target_pos(k)
            if e < dur:
                kk = back_out(clamp(e / 0.1), 2.6)
                r = 62 if k < 3 else 54
                s.append(f'<g transform="translate({f(px)} {f(py)}) scale({f(kk)})">{shape(ellipse_pts(0, 0, r, r, 24), "#ffd84a", blob(ellipse_pts(14, 12, r * .78, r * .74, 16), "#f0b92e", .75) + blob(ellipse_pts(-r * .3, -r * .32, r * .22, r * .12, 8, rot=-30), "#fff6c8", .9), w=4.6, seed=4730 + k)}</g>')
            else:       # попадание: кольцо расходится
                v = (e - dur) / 0.25
                rr = 62 + 70 * ease_out(v)
                s.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(rr)}" fill="none" stroke="#7fe0a0" stroke-width="{f(10 * (1 - v) + 1)}"/>')
    return f'<g clip-path="url(#{c})">{"".join(s)}</g>'


D3, YB3, SC3, DW3 = st.D3, st.YB3, st.SC3, st.DW3


def pressed(i, t):
    """0..1: рука i сейчас давит кнопку. Кружки чередуются между тремя людьми."""
    best = 0.0
    for k, te in enumerate(EVENTS):
        if k % 3 != i:
            continue
        e = t - (te + (0.13 if k < 3 else 0.06))
        if 0 <= e < 0.2:
            best = max(best, math.sin(math.pi * e / 0.2))
    return best


def desks(t):
    s = []
    depth = DW3 * .3
    for i, x in enumerate(D3):
        pr = pressed(i, t)
        # человек ждёт, руки над кнопкой, при нажатии кисть вдавливает кнопку
        hit = pr
        tilt = (0.2 * math.sin(t * 1.2 + i), -0.7 + 0.15 * math.sin(t * 2 + i))
        extra = {"hand_target": {"L": (-58, -300), "R": (52, -318 + 24 * hit + 3 * math.sin(t * 5 + i))},
                 "curl": {"L": .15, "R": .6}, "look": tilt, "brow": 0.8, "mouth": "flat" if t < TESTS else "o"}
        body, arms = st.student(STUDENTS[i], x - 10, YB3, SC3, t, i * 2.1, 4800 + i * 100, write=False, mood="focus", extra=extra)
        s.append(body)
        s.append(st.desk_surface(x, YB3, DW3, depth, 4850 + i * 10))
        bx, by = x - 10 + 52 * SC3 + 6, YB3 + depth * .5 + 12
        dn = 11 * hit
        s.append(shape(ellipse_pts(bx, by + 6, 44, 15, 14), "#3a3f52", "", w=3.2, seed=4860 + i))
        s.append(shape([(bx - 36, by - 2 + dn, 1), (bx - 34, by - 18 + dn), (bx + 34, by - 18 + dn), (bx + 36, by - 2 + dn, 1)], "#e2433a" if hit < .3 else "#ff7a6a",
                       blob([(bx + 8, by - 18 + dn), (bx + 34, by - 18 + dn), (bx + 36, by - 2 + dn), (bx + 8, by - 2 + dn)], "#b8302a", .8), w=3.4, seed=4870 + i))
        s.append(shape(ellipse_pts(bx, by - 18 + dn, 34, 11, 14), "#ff6b5a", blob(ellipse_pts(bx - 10, by - 20 + dn, 12, 4, 8), "#ffd0c8", .8), w=3.2, seed=4880 + i))
        s.append(arms)
        s.append(st.desk_front(x, YB3, DW3, depth, 1250, 4890 + i * 10))
    return "".join(s)


def eye_badge(t):
    e = t - EYE_T
    if e < 0:
        return ""
    k = back_out(clamp(e / 0.26), 2.4) * (1 + 0.012 * math.sin(e * 3))
    cx, cy, R = 540, 500, 300
    s = []
    s.append(shape(ellipse_pts(cx, cy, R, R, 36), "#fbf8ee", blob(ellipse_pts(cx + 40, cy + 40, R * .9, R * .88, 28), "#ece4d0", .6), w=7, seed=4900))
    c = lib.clip_of(ellipse_pts(cx, cy, R - 6, R - 6, 36))
    inner = []
    # веко/кожа вокруг глаза
    ew, eh = 250, 120
    # бледно-фиолетовые мешки под глазом
    inner.append(blob(ellipse_pts(cx, cy + 98, 230, 52, 18, rot=0), "#b99ad0", .9))
    inner.append(line([(cx - 190, cy + 120), (cx, cy + 156), (cx + 190, cy + 120)], 6, "#8a6aa8", taper=.4, seed=4910))
    # цель, за которой следит зрачок
    jump = int(t * 7.4)
    tx = math.sin(jump * 2.3) * 70
    ty = math.cos(jump * 3.1) * 14
    drift = (1 - math.exp(-((t * 7.4) % 1) * 9))
    px = (math.sin((jump - 1) * 2.3) * 70) * (1 - drift) + tx * drift
    py = (math.cos((jump - 1) * 3.1) * 14) * (1 - drift) + ty * drift
    blink_t = (t - EYE_T) % 1.6
    blink = 0.0
    if 0.9 < blink_t < 1.4:        # медленное тяжёлое моргание уставшего глаза
        blink = math.sin(math.pi * (blink_t - 0.9) / 0.5)
    droop = 0.28 + 0.62 * blink
    top_y = cy - eh + eh * 2 * droop * .5
    eye = [(cx - ew, cy + 6, 1), (cx - ew * .6, cy - eh * .8), (cx, cy - eh), (cx + ew * .6, cy - eh * .8), (cx + ew, cy + 6, 1),
           (cx + ew * .6, cy + eh * .8), (cx, cy + eh), (cx - ew * .6, cy + eh * .8)]
    ei = ""
    ix, iy = cx + px, cy + py
    ei += f'<circle cx="{f(ix)}" cy="{f(iy)}" r="86" fill="#3c9a8a" stroke="{INK}" stroke-width="5"/>'
    ei += f'<circle cx="{f(ix)}" cy="{f(iy)}" r="60" fill="none" stroke="#6fd0bc" stroke-width="6" opacity="1"/>'
    ei += f'<circle cx="{f(ix)}" cy="{f(iy)}" r="38" fill="{INK}"/>'
    ei += f'<circle cx="{f(ix - 22)}" cy="{f(iy - 24)}" r="13" fill="#ffffff"/>'
    for q in range(5):       # красные прожилки белка (усталость)
        a = math.pi + (q - 2) * .26
        ei += line([(cx - ew + 14, cy + 4 + (q - 2) * 14), (cx - ew + 80 + 14 * q, cy + 2 + (q - 2) * 9)], 3.2, "#e0705a", taper=.7, seed=4920 + q, op=.9)
        ei += line([(cx + ew - 14, cy + 4 + (q - 2) * 14), (cx + ew - 80 - 14 * q, cy + 2 + (q - 2) * 9)], 3.2, "#e0705a", taper=.7, seed=4930 + q, op=.9)
    # верхнее веко: кожа, нависает на глаз
    lid = f'<path d="M{f(cx - ew - 20)} {f(cy - eh - 40)} L{f(cx + ew + 20)} {f(cy - eh - 40)} L{f(cx + ew + 20)} {f(top_y + 6)} Q{f(cx)} {f(top_y + 38)} {f(cx - ew - 20)} {f(top_y + 6)} Z" fill="#f0c4a0"/>'
    inner_eye = shape(eye, "#ffffff", ei + lid + line([(cx - ew - 4, top_y + 8), (cx, top_y + 30), (cx + ew + 4, top_y + 8)], 8, INK, taper=.3, wmin=.5, seed=4940), w=7, seed=4941)
    inner.append(inner_eye)
    # бровь над глазом, опущена
    inner.append(line([(cx - 240, cy - 190), (cx - 60, cy - 214), (cx + 120, cy - 196), (cx + 230, cy - 150)], 20, "#5a3a26", taper=.5, wmin=.5, seed=4950))
    s.append(f'<g clip-path="url(#{c})">{"".join(inner)}</g>')
    s.append(shape(ellipse_pts(cx, cy, R, R, 36), "none", "", w=7, seed=4960, ink=True).replace('fill="none"', 'fill="none"'))
    return f'<g transform="translate({cx} {cy}) scale({f(k)}) translate({-cx} {-cy})">{"".join(s)}</g>'


def s09(t):
    art = [_ST["wall"], screen_art(t), desks(t), eye_badge(t)]
    # звёздочки-удары на кружках быстрого режима
    ev = [te for te in EVENTS if te <= t]
    last = ev[-1] if ev else 17.0
    e = t - last
    scl = 1.0 + 0.12 * ease_out(clamp((t - 17.3) / 2.6), 2)
    cy = 800 + 25 * clamp((t - 17.3) / 2.6)
    if t > TESTS:
        ee = t - TESTS
        scl *= 1 + 0.045 * math.exp(-ee * 6) * math.sin(min(ee * 14, math.pi))
    if t > EYE_T:
        ee = t - EYE_T
        scl *= 1 + 0.05 * math.exp(-ee * 6) * math.sin(min(ee * 14, math.pi))
        cy += 8 * math.exp(-ee * 8) * math.sin(ee * 50)
    rot = 1.0 * math.sin(t * .7) + (0.5 if t < TESTS else 0)
    return "".join(art), cam(540, cy, scl, rot)


def build_static():
    if _ST:
        return
    st.brick_defs()
    _ST["sky"] = sky8()
    _ST["facade"] = facade()
    _ST["ground"] = ground8()
    _ST["wall"] = lab_wall()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s08": s08, "s09": s09}[sid](t)
    bg = "#a6d4f5" if sid == "s08" else "#e8d6b0"
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cm}">{art}</g>')
