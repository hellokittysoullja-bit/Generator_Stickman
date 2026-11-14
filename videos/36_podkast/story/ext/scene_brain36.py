"""Сцена brain рилса 36 (s07, s08): мозг рилсов 24–32 (brain_art, ручки scene_brain, ножки в кедах и лицо scene_brain32)
на тёмно-синем фоне.
s07 «Мозгу нужна награда сейчас» (10.1–11.9): мозг стоит в ночной комнате, переминается и облизывается; на «награда»
     (10.92) перед ним выскакивает печенька-звёздочка (сияет, крутится), мозг распахивает глаза; на «сейчас» (11.36)
     хватает её обеими руками и радостно откусывает — укус, крошки, жуёт.
s08 «а не через полгода» (11.9–13.35): мозг (с надкушенной печенькой) смотрит вдаль: длинная дорога к холму на
     горизонте, на холме крошечный золотой кубок светится; у дороги перекидной календарь — на «через полгода»
     (12.24–12.60) листы один за другим улетают; на «полгода» мозг машет рукой, отворачивается и зевает.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import brain_art
import lib
import parts34 as P
import scene_brain as sb
import scene_brain32 as s32
from brain_art import BCX, BCY
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, svg, uid)

_ST = {}
FLOOR = sb.FLOOR                  # 1160
NAGRADA = P.wt("награда")         # 10.92
SEICHAS = P.wt("сейчас")          # 11.36
CHEREZ = P.wt("через")            # 12.24
POLGODA = P.wt("полгода")         # 12.60
EYE_L, EYE_R = s32.EYE_L, s32.EYE_R
HIP_L, HIP_R = s32.HIP_L, s32.HIP_R
MOUTH = (BCX - 72, BCY + 74)


# ───────────────────────── лицо мозга (как scene_brain32.face + жуёт, зевает, счастливые дуги)
def face(look=(0.0, 0.0), mouth="smile", t=0.0, brow=0.0, blink=0.0, eye_k=1.0, happy=0.0):
    s = []
    for k, (x, y) in enumerate((EYE_L, EYE_R)):
        if happy > 0.5:          # счастливые глаза-дуги ∩
            s.append(line([(x - 26, y + 10), (x - 12, y - 8), (x + 12, y - 8), (x + 26, y + 10)], 7, INK, taper=.35, wmin=.4, seed=880 + k))
            continue
        rx, ry = 29 * (0.92 + 0.08 * eye_k), 36 * eye_k
        e = ellipse_pts(x, y, rx, ry, 18)
        pr = 9.5 / (0.85 + 0.15 * eye_k)
        px, py = x + look[0] * 10, y + look[1] * 12
        inner = f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(pr)}" fill="{INK}"/><circle cx="{f(px - 3)}" cy="{f(py - 3.5)}" r="3" fill="#ffffff"/>'
        if blink > 0.02:
            yb = y - ry - 2 + (2 * ry + 4) * blink
            inner += f'<rect x="{x - 34}" y="{y - ry - 4}" width="68" height="{f(yb - (y - ry - 4))}" fill="#f6a9bc"/>'
            inner += line([(x - 32, yb), (x, yb + 3), (x + 32, yb)], 4, INK, seed=890 + k)
        s.append(shape(e, "#ffffff", inner, w=4.4, seed=886 + k))
        if brow:
            by = y - ry - 16 - 8 * brow
            s.append(line([(x - 22, by + 4), (x, by - 4 * brow), (x + 20, by + 2)], 5.5, "#8e3358", taper=.4, wmin=.4, seed=892 + k))
    mx, my = MOUTH
    if mouth == "o":
        s.append(shape(ellipse_pts(mx, my, 14, 18, 14), "#7a2a40", blob(ellipse_pts(mx, my + 8, 8, 6, 10), "#e2543f"), w=3.4, seed=895))
    elif mouth == "yawn":
        s.append(shape(ellipse_pts(mx, my + 6, 24, 32, 18), "#7a2a40", blob(ellipse_pts(mx + 2, my + 22, 14, 10, 12), "#e2543f"), w=3.8, seed=895))
    elif mouth == "chew":
        s.append(line([(mx - 22, my - 2), (mx - 8, my + 8), (mx + 8, my + 8), (mx + 22, my - 2)], 5, INK, taper=.3, wmin=.5, seed=897))
        s.append(blob(ellipse_pts(mx - 34, my - 4, 14, 12, 10), "#f6a9bc"))
    elif mouth == "drool":
        pts = [(mx - 26, my - 6, 1), (mx + 26, my - 8, 1), (mx + 18, my + 12), (mx, my + 18), (mx - 18, my + 12)]
        s.append(shape(pts, "#7a2a40", blob([(mx - 12, my + 8), (mx + 12, my + 6), (mx + 6, my + 16), (mx - 6, my + 16)], "#e2543f"), w=3.6, seed=895))
        dr = 0.5 + 0.5 * math.sin(t * 3)
        s.append(shape([(mx + 10, my + 10), (mx + 18, my + 10), (mx + 17, my + 30 + 10 * dr), (mx + 13, my + 36 + 10 * dr), (mx + 9, my + 30 + 10 * dr)],
                       "#bfe6ff", "", w=2.6, seed=896))
    else:
        pts = [(mx - 30, my - 8, 1), (mx + 30, my - 10, 1), (mx + 20, my + 12), (mx, my + 20), (mx - 20, my + 12)]
        s.append(shape(pts, "#7a2a40", blob([(mx - 14, my + 8), (mx + 14, my + 6), (mx + 8, my + 18), (mx - 8, my + 18)], "#e2543f"), w=3.6, seed=895))
    s.append(blob(ellipse_pts(BCX - 160, BCY + 56, 20, 10, 10), "#f07a98", .55 + .3 * happy))
    return "".join(s)


# ───────────────────────── печенька-звёздочка
DOUGH, DOUGH_SH, DOUGH_HI, CHIP = "#eab25e", "#c98a3c", "#f8d58e", "#5a3018"


def star_pts(r=80, ri=44, n=5, rot=-90):
    pts = []
    for k in range(2 * n):
        a = math.radians(rot + k * 180 / n)
        rr = r if k % 2 == 0 else ri
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    # скруглённые лучи: сплайн через вершины и середины рёбер
    out = []
    for k in range(2 * n):
        p, q = pts[k], pts[(k + 1) % (2 * n)]
        out.append(p)
        out.append(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2))
    return out


def cookie(sd=0, bites=(), rot=0.0):
    """Печенька-звезда, центр (0,0), радиус ~80. bites — укусы (x, y, r) в системе печеньки."""
    outer = star_pts(80, 46)
    inner = blob([(p[0] + 10, p[1] + 12) for p in star_pts(66, 36)], DOUGH_SH, .9)
    inner += blob(star_pts(56, 30), DOUGH, 1)
    inner += blob(ellipse_pts(-18, -24, 20, 9, 10, rot=-30), DOUGH_HI, .9)
    for k, (x, y, r) in enumerate([(-22, 4, 7), (16, -14, 6), (10, 22, 7), (-4, -36, 5), (34, 8, 5), (-38, -12, 5), (-10, 40, 5)]):
        inner += shape(ellipse_pts(x, y, r, r * .85, 8, rot=k * 40), CHIP, "", w=1.8, seed=sd + 30 + k)
    rs = np.random.RandomState(sd)
    for k in range(10):
        x, y = rs.uniform(-40, 40), rs.uniform(-40, 40)
        inner += f'<circle cx="{f(x)}" cy="{f(y)}" r="2" fill="#fff4cf" opacity=".9"/>'
    body = shape(outer, DOUGH, inner, w=4.4, seed=sd + 1)
    if not bites:
        return f'<g transform="rotate({f(rot)})">{body}</g>'
    mid = uid("m")
    cut = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#000"/>' for x, y, r in bites)
    DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-200" y="-200" width="400" height="400">'
                f'<rect x="-200" y="-200" width="400" height="400" fill="#fff"/>{cut}</mask>')
    cl = lib.clip_of(outer)
    crumb = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r + 8)}" fill="{DOUGH_HI}"/>' for x, y, r in bites)
    edge = ""
    for k, (x, y, r) in enumerate(bites):
        pts = [(x + r * math.cos(a), y + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)]
        edge += f'<path d="{lib.ink_open(pts, 4.0 * lib.INK_K[0], taper=.05, wmin=.8, seed=sd + 50 + k)}" fill="{INK}"/>'
    return (f'<g transform="rotate({f(rot)})"><g mask="url(#{mid})">{body}<g clip-path="url(#{cl})">{crumb}</g></g>'
            f'<g clip-path="url(#{cl})" mask="url(#{mid})">{edge}</g></g>')


BITE1 = [(80, -26, 36)]
BITE2 = BITE1 + [(52, -64, 30)]


def glow(x, y, r, a, col="#ffe27a"):
    if a < 0.02:
        return ""
    g = rad_grad([(0, col, .75 * a), (.5, col, .25 * a), (1, col, 0)], x, y, r, r)
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="url(#{g})"/>'


def twinkle(x, y, r, col="#fff3b0", rot=0.0, sd=0):
    return P.sparkle(x, y, r, col, sd, rot)


def crumbs(x, y, e, n=9, sd=0, sc=1.0):
    if e < 0 or e > 0.7:
        return ""
    s = []
    rs = np.random.RandomState(sd)
    for c in range(n):
        a = -math.pi * rs.uniform(0.15, 0.95)
        v = rs.uniform(260, 480) * sc
        cx = x + v * e * math.cos(a)
        cy = y + v * e * math.sin(a) + 1300 * sc * e * e
        r = rs.uniform(5, 9) * sc
        s.append(shape(ellipse_pts(cx, cy, r, r * .8, 7, rot=c * 50), DOUGH if c % 3 else DOUGH_SH, "", w=2.2, seed=sd + c))
    return "".join(s)


# ───────────────────────── мозг целиком (лицом влево; mirror — лицом вправо)
def brain_char(pose, feet, wl, wr, al, ar, cl, cr, face_svg, held="", bend=(-40, 40), legs_sd=1600, mirror=False, under_hands=""):
    """Мозг с ножками (ступни feet=(fl, fr)), ручками к wl/wr, кистями al/ar. held — предмет между мозгом и кистями.
    mirror — отражение вокруг центра pose (смотрит вправо)."""
    hl, hr = pose.pt(*HIP_L), pose.pt(*HIP_R)
    legs = s32.leg(hr, feet[1], pose.sc, -1, legs_sd) + s32.leg(hl, feet[0], pose.sc, -1, legs_sd + 20)
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    arms = sb.arm(SL, wl, bend[0], legs_sd + 41, pose.sc) + sb.arm(SR, wr, bend[1], legs_sd + 42, pose.sc)
    hands = sb.toon_hand(wl[0], wl[1], al, cl, legs_sd + 60, pose.sc * 1.3) + sb.toon_hand(wr[0], wr[1], ar, cr, legs_sd + 90, pose.sc * 1.3)
    body = legs + arms + f'<g transform="{pose.tf()}">{_ST["brain"]}{face_svg}</g>' + under_hands + held + hands
    if mirror:
        body = f'<g transform="translate({f(pose.x)} 0) scale(-1 1) translate({f(-pose.x)} 0)">{body}</g>'
    return body


def blink_at(t, times, d=0.13):
    return max([math.sin(math.pi * clamp((t - x) / d)) if x < t < x + d else 0.0 for x in times] + [0.0])


# ═══════════════════════════════ s07
BX7, BY7 = 600, 840


def s07(t):
    u_bob = 2 * math.pi * (t - 10.0) / 0.9
    e_pop = t - NAGRADA
    e_grab = t - SEICHAS
    T_BITE = SEICHAS + 0.24
    excite = smooth(NAGRADA, NAGRADA + 0.15, t)
    # мозг: переминается с ноги на ногу, на «награду» подскакивает от восторга, на «сейчас» — рывок вперёд к печеньке
    shift = math.sin(u_bob)
    hop = 30 * P.kick(t, NAGRADA + 0.05, 7, 12)
    lunge = smooth(SEICHAS - 0.08, SEICHAS + 0.1, t) - 0.6 * smooth(T_BITE + 0.05, T_BITE + 0.5, t)
    x = BX7 - 70 * lunge + 6 * shift
    y = BY7 - 6 * abs(math.cos(u_bob)) - hop + 10 * lunge
    rot = -3 * shift - 8 * lunge + 4 * P.kick(t, T_BITE, 6, 16)
    sq = 1 + 0.03 * math.cos(2 * u_bob) - 0.08 * P.kick(t, NAGRADA + 0.05, 7, 12) + 0.07 * P.kick(t, T_BITE, 7, 16)
    pose = sb.Pose(x, y, 1.0, rot, sq)
    hl, hr = pose.pt(*HIP_L), pose.pt(*HIP_R)
    g = FLOOR - 26
    lift_l = 34 * max(0.0, math.sin(u_bob)) + 50 * P.bump(t, NAGRADA + 0.02, 0.3)
    lift_r = 34 * max(0.0, -math.sin(u_bob)) + 50 * P.bump(t, NAGRADA + 0.08, 0.3)
    feet = ((hl[0] - 30, g - lift_l), (hr[0] + 20, g - lift_r))
    # печенька: выскакивает перед мозгом, висит и крутится, на «сейчас» летит в руки ко рту
    mouth_w = pose.pt(*MOUTH)
    cx0, cy0 = 320, 610
    hold = (mouth_w[0] - 96, mouth_w[1] + 4)
    gu = ease_in(clamp((e_grab + 0.04) / 0.16), 2)
    ck_x = cx0 + (hold[0] - cx0) * gu + 10 * math.sin(t * 3.1) * (1 - gu)
    ck_y = cy0 + (hold[1] - cy0) * gu + 14 * math.sin(t * 4.2) * (1 - gu)
    pop = back_out(clamp(e_pop / 0.3), 2.4) if e_pop > 0 else 0.0
    ck_sc = (1.5 * pop) * (1 - 0.18 * gu) * (1 + 0.06 * math.sin(t * 7) * (1 - gu))
    ck_rot = 18 + 25 * math.sin(t * 2.4) * (1 - gu) + 360 * (1 - pop) * (e_pop > 0)
    bites = BITE1 if t >= T_BITE else ()
    if t >= T_BITE + 0.42:
        bites = BITE2
    held = ""
    art = [_ST["props7"]]
    if e_pop > 0 and gu < 1:
        art.append(glow(ck_x, ck_y, 260 * ck_sc, (0.8 + 0.2 * math.sin(t * 9)) * (1 - gu)))
        for k in range(6):
            a = t * 1.6 + k * math.pi / 3
            r = 150 * ck_sc + 14 * math.sin(t * 6 + k)
            tw = 0.6 + 0.4 * math.sin(t * 10 + k * 2)
            art.append(twinkle(ck_x + r * math.cos(a), ck_y + r * math.sin(a), 18 * tw * ck_sc, rot=t * 90 + k * 30, sd=1700 + k))
        art.append(P.pop_lines(ck_x, ck_y, e_pop, 120, 200, 10, col="#ffe27a", w=10, sd=1720))
    ck_svg = f'<g transform="translate({f(ck_x)} {f(ck_y)}) scale({f(ck_sc)})">{cookie(1750, bites, ck_rot if gu < 1 else 18 + 5 * math.sin(t * 9))}</g>' \
        if e_pop > 0 else ""
    # ручки: висят и покачиваются → на «награду» вскинуты (восторг) → на «сейчас» тянутся и держат печеньку у рта
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    rest_l = (SL[0] - 110 + 20 * shift, SL[1] + 60)
    rest_r = (SR[0] + 110 + 20 * shift, SR[1] + 60)
    joy = smooth(NAGRADA + 0.02, NAGRADA + 0.18, t) * (1 - smooth(SEICHAS - 0.16, SEICHAS - 0.02, t))
    up_l = (pose.x - 290, pose.y - 170 + 16 * math.sin(t * 11))
    up_r = (pose.x + 270, pose.y - 200 + 16 * math.sin(t * 11 + 1))
    grab = smooth(SEICHAS - 0.14, SEICHAS + 0.04, t)
    gl = (ck_x - 150, ck_y + 46)
    gr = (ck_x + 10, ck_y + 150)

    def mixp(a, b, k):
        return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
    wl = mixp(mixp(rest_l, up_l, joy), gl, grab)
    wr = mixp(mixp(rest_r, up_r, joy), gr, grab)
    al = 120 + (-110 - 120) * joy
    ar = 60 + (-70 - 60) * joy
    al = al + (-20 - al) * grab
    ar = ar + (-95 - ar) * grab
    cl = cr = 0.55 * (1 - joy) * (1 - grab) + 0.35 * grab
    # лицо
    chew = t > T_BITE + 0.08
    if e_pop < -0.05:
        mouth, look, eye_k, brow = "smile", (-0.4 + 0.5 * math.sin(t * 2.3), -0.2), 1.0, 0.4
    elif not chew:
        mouth = "drool" if e_pop > 0.15 else "o"
        look = (-0.9, -0.5) if t < SEICHAS else (-0.6, -0.1)
        eye_k, brow = 1.0 + 0.22 * smooth(NAGRADA - 0.05, NAGRADA + 0.1, t), 1.0
    else:
        mouth = "chew" if math.sin((t - T_BITE) * 22) > -0.2 else "smile"
        look, eye_k, brow = (-0.3, -0.2), 1.0, 0.8
    happy = 1.0 if chew else 0.0
    blink = blink_at(t, [10.35])
    fs = face(look, mouth, t, brow, blink, eye_k, happy)
    if gu >= 1 or grab > 0.5:
        held, out_ck = ck_svg, ""
    else:
        held, out_ck = "", ck_svg
    art.append(sb.shadow(pose.x - 20, FLOOR + 4, 190, .55))
    art.append(brain_char(pose, feet, wl, wr, al, ar, cl, cr, fs, held=held, legs_sd=1600))
    art.append(out_ck)
    if T_BITE <= t:
        art.append(crumbs(mouth_w[0] - 40, mouth_w[1] - 10, t - T_BITE, 10, 1800))
        art.append(crumbs(mouth_w[0] - 40, mouth_w[1] - 10, t - (T_BITE + 0.42), 7, 1830))
        art.append(P.pop_lines(mouth_w[0] - 90, mouth_w[1] - 40, t - T_BITE, 70, 140, 7, a0=-math.pi * .7, spread=2.2, col="#ffe27a", w=9, sd=1860))
    # сердечки-звёздочки радости над головой после укуса
    if t > T_BITE + 0.1:
        e = t - T_BITE - 0.1
        for j in range(3):
            k = back_out(clamp((e - j * 0.08) / 0.25), 2.2)
            if k > 0.03:
                hx = pose.x - 160 + j * 150 + 10 * math.sin(e * 4 + j)
                hy = pose.y - 300 - 60 * e - 20 * (j == 1)
                art.append(P.heart(hx, hy, 2.0 * k, -14 + 14 * j + 6 * math.sin(e * 5 + j), sd=1900 + j * 5))
    # камера: лёгкий наезд с первого кадра, толчок на «сейчас»
    u = clamp((t - 9.9) / 2.2)
    sc = 1.38 + 0.08 * ease_io(u) + 0.04 * P.kick(t, SEICHAS + 0.2, 6, 14) + 0.02 * P.kick(t, NAGRADA, 7, 14)
    return "".join(art), cam(520 - 30 * u, 890 - 6 * u, sc, 0.6 - 0.9 * u)


def props7():
    """Ночная комната мозга (как в рилсе 32): торшер справа, коврик."""
    s = []
    x = 1000
    s.append(sb.shadow(x, FLOOR + 4, 90, .5))
    s.append(shape(ellipse_pts(x, FLOOR - 8, 70, 16, 14), "#2b3764", "", w=4, seed=1101))
    s.append(line([(x, FLOOR - 12), (x, 470)], 12, "#2b3764", taper=.05, wmin=.95, seed=1102))
    shade_ = [(x - 80, 470, 1), (x + 80, 470, 1), (x + 56, 330, 1), (x - 56, 330, 1)]
    s.append(glow(x, 520, 330, .45, "#ffd98a"))
    s.append(shape(shade_, "#e8c47a", blob([(x + 20, 330), (x + 56, 330), (x + 80, 470), (x + 30, 470)], "#c99a52", .8), w=4.6, seed=1103))
    rug = ellipse_pts(560, FLOOR + 70, 470, 52, 30)
    s.append(shape(rug, "#4a3c7a", blob(ellipse_pts(560, FLOOR + 70, 380, 36, 26), "#5a4c8e") + blob(ellipse_pts(560, FLOOR + 70, 250, 22, 20), "#6c5ea0"),
                   w=4.2, seed=1104))
    # рамка с картинкой на стене
    for k, (x, y) in enumerate(((180, 430), (690, 380))):
        pts = rect_pts(x - 90, y - 70, x + 90, y + 70, 6)
        inner = blob(rect_pts(x - 70, y - 50, x + 70, y + 50), "#3d4f86")
        inner += blob([(x - 70, y + 50), (x - 20, y - 6), (x + 14, y + 26), (x + 40, y), (x + 70, y + 50)], "#5a7ab8")
        inner += shape(ellipse_pts(x + 36, y - 22, 12, 12, 10), "#ffe27a", "", w=2.4, seed=1500 + k)
        s.append(shape(pts, "#7a5a3c", inner, w=4.2, seed=1510 + k))
    return "".join(s)


# ═══════════════════════════════ s08: дорога к кубку через полгода
HOR = 1010                     # линия горизонта
TROPHY = (905, 905)            # кубок на холме (низ)
CAL = (590, 1300)              # календарь (низ стойки)
BX8, BY8 = 345, 1210


def sky8():
    s = []
    lib.lin_grad([(0, "#141b3c", 1), (.6, "#25305e", 1), (1, "#3a4a86", 1)], 0, 0, 0, 1, gid="gSky8")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{HOR + 900 + 40}" fill="url(#gSky8)"/>')
    rs = np.random.RandomState(81)
    for k in range(60):
        x, y = rs.uniform(-500, W + 500), rs.uniform(-600, HOR - 120)
        r = rs.uniform(1.5, 3.6)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#dfe6ff" opacity="{rs.uniform(.4, .9):.2f}"/>')
    # месяц
    s.append(shape(ellipse_pts(180, 260, 56, 56, 20), "#fff2c0", blob(ellipse_pts(210, 240, 48, 50, 18), "#2a3566"), w=0, seed=1, ink=False))
    return "".join(s)


def land8():
    s = []
    # дальние холмы
    far = [(-900, HOR + 20)] + [(x, HOR - 60 - 50 * math.sin(x / 210) - 30 * math.sin(x / 90 + 1)) for x in np.linspace(-900, W + 900, 30)] + [(W + 900, HOR + 20)]
    s.append(shape(far + [(W + 900, H + 900, 1), (-900, H + 900, 1)], "#2c3f6c", "", w=3.6, seed=2001))
    # холм кубка
    hill = [(TROPHY[0] - 260, HOR + 10), (TROPHY[0] - 140, TROPHY[1] + 30), (TROPHY[0] - 40, TROPHY[1] + 2), (TROPHY[0] + 60, TROPHY[1] + 4),
            (TROPHY[0] + 160, TROPHY[1] + 34), (TROPHY[0] + 300, HOR + 10)]
    s.append(shape(hill + [(TROPHY[0] + 300, HOR + 200, 1), (TROPHY[0] - 260, HOR + 200, 1)], "#35507e",
                   blob(ellipse_pts(TROPHY[0] + 80, TROPHY[1] + 70, 160, 50, 14), "#2c4470", .8), w=3.8, seed=2002))
    # ближняя земля
    near = [(-900, HOR + 60)] + [(x, HOR + 40 + 24 * math.sin(x / 160)) for x in np.linspace(-900, W + 900, 26)] + [(W + 900, HOR + 60)]
    s.append(shape(near + [(W + 900, H + 900, 1), (-900, H + 900, 1)], "#344d5c", blob([(-900, HOR + 260), (W + 900, HOR + 200), (W + 900, H + 900), (-900, H + 900)],
                                                                                          "#2b4250", .8), w=4, seed=2003))
    # дорога: от нас (низ слева) вдаль к холму — сужается
    def road(u, side):
        # центр дороги — кривая от (250, 1900) до (TROPHY) с изгибом; ширина от 420 до 8
        x = (1 - u) ** 2 * 260 + 2 * (1 - u) * u * 1000 + u * u * (TROPHY[0] - 10)
        y = (1 - u) ** 2 * 1950 + 2 * (1 - u) * u * 1180 + u * u * (TROPHY[1] + 30)
        wdt = 440 * (1 - u) ** 1.6 + 8
        return (x + side * wdt / 2, y)
    us = np.linspace(0, 1, 30)
    rd = [road(u, -1) for u in us] + [road(u, 1) for u in us[::-1]]
    s.append(f'<path d="{lib.fill_d(rd)}" fill="#8f8aa8"/>')
    s.append(f'<path d="{lib.ink_open([road(u, -1) for u in us], 4.2, taper=.05, wmin=.3, seed=2010, peak=.0)}" fill="{INK}"/>')
    s.append(f'<path d="{lib.ink_open([road(u, 1) for u in us], 4.2, taper=.05, wmin=.3, seed=2011, peak=.0)}" fill="{INK}"/>')
    # разметка пунктиром
    for k in range(12):
        u0 = (k + .2) / 13
        u1 = u0 + 0.035
        a, b = road(u0, 0), road(u1, 0)
        s.append(line([a, b], 14 * (1 - u0) ** 1.4 + 1.5, "#e8e2f4", taper=.1, wmin=.8, seed=2020 + k, op=.9))
    # кустики и камни вдоль
    for k, (x, y, r) in enumerate([(80, 1240, 70), (1010, 1120, 40), (760, 1050, 22), (-60, 1110, 50), (1130, 1300, 90)]):
        s.append(shape(P.cloud_pts(x, y, r, r * .6, 6, 2030 + k), "#3f6a5a", blob(ellipse_pts(x + r * .3, y + r * .3, r * .7, r * .3, 10), "#2f5446", .8),
                       w=3.6, seed=2040 + k))
    return "".join(s)


def trophy(x, y, sc, t, sd=2100):
    """Золотой кубок: низ основания в (x, y)."""
    G, GS, GH = "#ffc93a", "#d9962a", "#fff0a8"
    s = []
    for side in (-1, 1):
        hp = [(side * 34, -100), (side * 66, -112), (side * 70, -80), (side * 40, -62)]
        s.append(line(hp, 9, INK, taper=.05, wmin=.9, seed=sd + side))
        s.append(line(hp, 5, G, taper=.05, wmin=.9, seed=sd + 2 + side))
    cup = [(-50, -128, 1), (50, -128, 1), (44, -86), (24, -58), (0, -50), (-24, -58), (-44, -86)]
    s.append(shape(cup, G, blob([(14, -128), (50, -128), (44, -86), (24, -58), (6, -52)], GS, .9) + blob(ellipse_pts(-24, -106, 8, 16, 8), GH, .9),
                   w=3.6, seed=sd + 5))
    s.append(shape(rect_pts(-8, -52, 8, -26), G, blob(rect_pts(2, -52, 8, -26), GS), w=3, seed=sd + 6))
    s.append(shape(rect_pts(-34, -28, 34, 0, 4), "#7a4a2a", blob(rect_pts(8, -28, 34, 0), "#5a3420"), w=3.4, seed=sd + 7))
    s.append(P.sparkle(0, -100, 14, "#fff6c8", sd + 8, t * 60))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{"".join(s)}</g>'


def calendar(x, y, t, sd=2200):
    """Перекидной календарь на стойке-мольберте: низ стойки (x, y). Листы (6 шт.) улетают на «через полгода»."""
    s = []
    top = y - 330
    # стойка
    for dx in (-70, 70):
        s.append(line([(x + dx * .55, top + 40), (x + dx, y)], 9, "#6b4a2e", taper=.05, wmin=.9, seed=sd + dx))
    s.append(line([(x, top + 60), (x + 20, y - 4)], 8, "#5a3c24", taper=.05, wmin=.9, seed=sd + 3))
    s.append(sb.shadow(x, y + 4, 90, .4))
    bw, bh = 190, 210
    x0, y0 = x - bw / 2, top
    # картонная подложка
    s.append(shape(rect_pts(x0 - 8, y0 - 6, x0 + bw + 8, y0 + bh + 10, 8), "#9a7a5a", "", w=3.6, seed=sd + 4))
    n = 7
    fly = []
    for k in range(n):           # k=0 — верхний лист
        tk = CHEREZ - 0.04 + k * (POLGODA + 0.06 - CHEREZ) / 5
        e = t - tk
        if k == n - 1:
            e = -1
        if e > 0.9:
            continue
        page = rect_pts(x0, y0 + 14, x0 + bw, y0 + bh, 6)
        inner = blob(rect_pts(x0, y0 + 14, x0 + bw, y0 + 54), "#e2543f")
        for r in range(3):
            for c in range(5):
                px, py = x0 + 26 + c * 35, y0 + 84 + r * 40
                inner += f'<rect x="{f(px - 10)}" y="{f(py - 10)}" width="20" height="20" rx="4" fill="#e3e6ef"/>'
        inner += blob(rect_pts(x0 + bw - 40, y0 + 14, x0 + bw, y0 + bh), "#e6e8ee", .8)
        pg = shape(page, "#fbfbf8", inner, w=3.8, seed=sd + 10 + k)
        if e <= 0:
            s.append(f'<g data-k="{k}">{pg}</g>')
            continue
        # лист отрывается: взлетает вверх-вправо, крутится
        u = e
        dx = (-120 + 60 * k) * u + 60 * math.sin(u * 7 + k)
        dy = -1100 * u + 300 * u * u
        rr = 200 * u * (1 if k % 2 else -1)
        scl = 1 - 0.35 * u
        cxp, cyp = x, y0 + bh / 2
        fly.append(f'<g transform="translate({f(cxp + dx)} {f(cyp + dy)}) rotate({f(rr)}) scale({f(scl)}) translate({f(-cxp)} {f(-cyp)})">{pg}</g>')
    # нижние листы — снизу вверх (первым рисуется нижний)
    pages = [p for p in s if p.startswith('<g data-k')]
    rest = [p for p in s if not p.startswith('<g data-k')]
    out = rest + pages[::-1]
    # кольца переплёта
    for k in range(5):
        rx_ = x0 + 26 + k * 35
        out.append(line([(rx_ - 6, y0 + 22), (rx_ - 8, y0 + 4), (rx_ + 2, y0 - 4), (rx_ + 8, y0 + 8)], 5, "#c9ced8", taper=.1, wmin=.8, seed=sd + 40 + k))
    return "".join(out), "".join(fly)


def s08(t):
    art = [_ST["sky8"], _ST["land8"]]
    # кубок светится, пульсирует
    pul = 0.75 + 0.25 * math.sin(t * 6)
    art.append(glow(TROPHY[0], TROPHY[1] - 40, 150, pul))
    art.append(trophy(TROPHY[0], TROPHY[1] + 6, 0.52 * (1 + 0.04 * math.sin(t * 6)), t))
    for k in range(4):
        a = t * 2 + k * math.pi / 2
        art.append(twinkle(TROPHY[0] + 60 * math.cos(a), TROPHY[1] - 50 + 40 * math.sin(a), 6 + 3 * math.sin(t * 9 + k), rot=t * 120, sd=2300 + k))
    cal, fly = calendar(*CAL, t)
    art.append(cal)
    # мозг: смотрит вдаль (лицом вправо) → на «полгода» машет рукой, отворачивается (лицом влево) и зевает
    TURN = POLGODA + 0.16
    turn = smooth(TURN - 0.07, TURN + 0.07, t)
    mirror = turn < 0.5
    squash_turn = 1 - 0.8 * math.sin(math.pi * turn)            # «поворот» — мозг сжимается по ширине и разворачивается
    breath = math.sin((t - 11.7) * 2 * math.pi / 1.1)
    x, y = BX8, BY8 + 6 * breath
    pose = sb.Pose(x, y, 0.95, (-3 if mirror else 3) + 2 * breath, 1 + 0.015 * breath)
    hl, hr = pose.pt(*HIP_L), pose.pt(*HIP_R)
    g = BY8 + 300
    feet = ((hl[0] - 24, g), (hr[0] + 18, g + 6))
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    # в «левосторонней» системе (лицом влево) — ручка у лба козырьком смотрит вдаль, другая держит печеньку
    wave = smooth(POLGODA - 0.1, POLGODA + 0.04, t)
    peer = 1 - wave
    # левая ручка (у лица): козырёк над глазами → взмах «да ну» (машет)
    visor = (pose.x - 60, pose.y - 130)
    wv = (pose.x - 260 + 50 * math.sin((t - POLGODA) * 22) * (t > POLGODA), pose.y - 200)
    if t > TURN + 0.1:      # после поворота — прикрывает зевок
        k = smooth(TURN + 0.1, TURN + 0.3, t)
        mouth_w = pose.pt(*MOUTH)
        wv2 = (mouth_w[0] - 40, mouth_w[1] + 10)
        wv = (wv[0] + (wv2[0] - wv[0]) * k, wv[1] + (wv2[1] - wv[1]) * k)
    wl = (visor[0] + (wv[0] - visor[0]) * wave, visor[1] + (wv[1] - visor[1]) * wave)
    al = -10 * peer + (-120 + 30 * math.sin((t - POLGODA) * 22)) * wave
    if t > TURN + 0.1:
        al = al + (10 - al) * smooth(TURN + 0.1, TURN + 0.3, t)
    cl = 0.2
    # правая ручка: печенька у груди
    wr = (SR[0] + 60, SR[1] + 90)
    ar, cr = 200, 0.55
    ck = f'<g transform="translate({f(wr[0] - 34)} {f(wr[1] - 6)}) scale(.62)">{cookie(1750, BITE2, 10)}</g>'
    yawn = smooth(TURN + 0.05, TURN + 0.3, t)
    if t < POLGODA:
        look = (-1.0, -0.4)
        mouth = "o" if t > CHEREZ + 0.1 else "chew"
        eye_k, blink, brow = 1.0, 0.0, 0.7
        if t < 12.15:
            mouth = "chew" if math.sin(t * 22) > -0.2 else "smile"
    elif t < TURN:
        look, mouth, eye_k, blink, brow = (-1.0, -0.2), "o", 0.9, 0.0, -0.4
    else:
        look, mouth, eye_k, blink, brow = (-0.6, -0.2), "yawn" if yawn > 0.3 else "o", 1.0, 0.6 * yawn, 0.2
    fs = face(look, mouth, t, brow, blink, eye_k)
    body = brain_char(pose, feet, wl, wr, al, ar, cl, cr, fs, held=ck, legs_sd=2400, mirror=False)
    sx = (-1 if mirror else 1) * max(0.08, squash_turn)
    body = f'<g transform="translate({f(pose.x)} 0) scale({f(sx)} 1) translate({f(-pose.x)} 0)">{body}</g>'
    art.append(fly)
    art.append(sb.shadow(pose.x, g + 4, 200, .5))
    art.append(body)
    # «пф» — штрихи взмаха
    if t > POLGODA:
        art.append(P.pop_lines(pose.x + 230, pose.y - 220, t - POLGODA, 60, 130, 5, a0=-0.6, spread=1.8, col="#cfe0ff", w=8, sd=2500))
    if t > TURN + 0.2:      # «Z» зевоты
        art.append(s32.zzz(t + 0.8, pose.x - 160, pose.y - 180))
    # камера: с общего плана — тянется к кубку на «через полгода», на «полгода» отскок назад к мозгу
    to = ease_io(clamp((t - 11.95) / 0.6))
    back = ease_out(clamp((t - POLGODA) / 0.3), 3)
    cx = 560 + (760 - 560) * to * (1 - back) - 60 * back
    cy = 1060 + (930 - 1060) * to * (1 - back) + 40 * back
    sc = 1.05 + 0.55 * to * (1 - back) + 0.12 * back + 0.05 * P.kick(t, POLGODA, 6, 14)
    return "".join(art), cam(cx, cy, sc, -0.5 + 0.8 * clamp((t - 11.7) / 1.85))


def build_static():
    if _ST:
        return
    _ST["bg"] = sb.background()
    _ST["brain"] = brain_art.brain(0, 0, stem=False)
    _ST["props7"] = props7()
    _ST["sky8"] = sky8()
    _ST["land8"] = land8()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    if sid == "s07":
        art, cm = s07(t)
        return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{_ST["bg"]}{sb.dust(t)}{art}</g>')
    art, cm = s08(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1b2347"/><g transform="{cm}">{art}</g>')
