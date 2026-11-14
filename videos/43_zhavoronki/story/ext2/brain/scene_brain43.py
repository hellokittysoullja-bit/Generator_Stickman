"""Сцена brains рилса 43 (s09 14.72–17.0, s10 17.0–19.44): два мультяшных мозга рилсов 24–41 (brain_art без ствола,
ручки scene_brain, ножки в кедах scene_brain32, лицо scene_brain32) на кремовом фоне. Левый — «утренний» (над ним
солнце, тёплый ореол), правый — «вечерний» (над ним луна, в ночном колпаке, перед ним столик с закрытым ноутбуком).
Мозги смотрят друг на друга (левый отражён).
s09: левый бодр и подпрыгивает, правый клюёт носом; на «утром» (16.40) левый вспыхивает (ореол, лучи) и машет гантелькой,
     правый зевает.
s10: на «вечером» (17.60) правый загорается: колпак слетает, ноутбук раскрывается, экран светит, он бодро печатает; левый
     кладёт гантельку, на него падает колпак, он засыпает (Z); на «нормально» (18.52) над обоими рисуется зелёная
     галочка, оба показывают большой палец.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import brain_art
import lib
import scene_brain as sb
import scene_brain32 as b32
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, band, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
UTR = 16.40      # «утром»
VECH = 17.60     # «вечером»
NORM = 18.52     # «нормально»
X0, X1 = 262.0, 818.0      # центры мозгов
Y0 = 742.0
SC = 0.78
FLOOR = 1000.0
SKIN, SKIN_SH = sb.SKIN, sb.SKIN_SH
TBL = (588.0, 884.0)       # столик: центр столешницы
CREAM = "#f4ead3"
CAP, CAP_SH = "#4d6cc2", "#3a54a0"
SUN = (262.0, 268.0)
MOON = (818.0, 268.0)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return math.sin(math.pi * u) if 0 < u < 1 else 0.0


def blink_at(t, times, dur=.16):
    for c in times:
        if abs(t - c) < dur / 2:
            return 1 - abs(t - c) / (dur / 2)
    return 0.0


# ───────────────────────── фон
def background():
    s = [f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="{CREAM}"/>']
    # тонкая бумажная фактура: редкие крапинки
    rs = np.random.RandomState(3)
    for k in range(140):
        x, y = rs.uniform(-300, W + 300), rs.uniform(-200, 1500)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rs.uniform(1.5, 3.2))}" fill="#e3d6b8" opacity=".7"/>')
    # пол: мягкая полоса и линия горизонта
    s.append(blob(rect_pts(-900, FLOOR - 4, W + 900, H + 900), "#eadcbd"))
    s.append(line([(-900, FLOOR - 2), (300, FLOOR + 2), (W + 900, FLOOR - 3)], 4.5, "#c9b48c", taper=.05, wmin=.9, seed=11))
    return "".join(s)


def halos(day, night):
    """Тёплый ореол утра за левым и синеватый вечера за правым; сила — от состояния."""
    s = []
    g = rad_grad([(0, "#ffe9a6", .95 * day), (.55, "#ffe9a6", .45 * day), (1, "#ffe9a6", 0)], X0, Y0 - 120, 430, 430)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#{g})"/>')
    g2 = rad_grad([(0, "#bcc8f0", .9 * night), (.55, "#c9d2f2", .4 * night), (1, "#c9d2f2", 0)], X1, Y0 - 120, 430, 430)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR + 900}" fill="url(#{g2})"/>')
    return "".join(s)


def star(x, y, r, col, sd, rot=0.0, w=2.8):
    pts = []
    for k in range(8):
        a = math.radians(rot + k * 45 - 90)
        rr = r if k % 2 == 0 else r * 0.4
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return shape(pts, col, "", w=w, seed=sd)


def sun(t, k, punch):
    """Солнце над левым: лучи вращаются; k — яркость (1 днём, тускнеет вечером), punch — вспышка на «утром»."""
    x, y = SUN
    y += 40 * (1 - k)            # вечером чуть садится
    r = 62 * (0.82 + 0.18 * k) * (1 + 0.22 * punch)
    s = []
    body = mix("#f3e2b0", "#ffd447", k)
    sh = mix("#e4cf98", "#f5b730", k)
    for j in range(10):
        a = t * 0.9 + j * math.pi / 5
        r0, r1 = r + 16, r + 46 + 8 * math.sin(t * 5 + j) + 30 * punch
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], 9, mix("#e8d7a4", "#f6b52a", k),
                      taper=.5, wmin=.3, seed=40 + j))
    s.append(shape(ellipse_pts(x, y, r, r, 26), body, blob(ellipse_pts(x + r * .3, y + r * .3, r * .75, r * .7, 18), sh, .9) +
                   blob(ellipse_pts(x - r * .38, y - r * .4, r * .22, r * .14, 10, rot=-30), "#ffffff", .7), w=5, seed=50))
    return "".join(s)


def moon(t, k):
    """Луна над правым: k — сила (тусклая днём, сияет вечером), звёздочки мерцают."""
    x, y = MOON
    y += 4 * math.sin(t * 1.6)
    r = 58 * (1 + 0.12 * k)
    s = []
    if k > 0.02:
        g = rad_grad([(0, "#fff6c8", .8 * k), (1, "#fff6c8", 0)], x, y, r * 2.2, r * 2.2)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 2.2)}" fill="url(#{g})"/>')
    body = mix("#e6dfc4", "#ffe98a", k)
    # серп: внешний круг минус смещённый
    out = []
    for j in range(25):
        a = math.radians(-120 + 240 * j / 24 + 180)
        out.append((x + r * math.cos(a), y + r * math.sin(a)))
    inner_c = (x + r * .42, y)
    rr = r * .87
    a_end = math.atan2(out[-1][1] - inner_c[1], out[-1][0] - inner_c[0])
    a_beg = math.atan2(out[0][1] - inner_c[1], out[0][0] - inner_c[0])
    if a_beg > a_end:
        a_beg -= 2 * math.pi
    for j in range(1, 20):
        a = a_end + (a_beg - a_end) * j / 20
        out.append((inner_c[0] + rr * math.cos(a), inner_c[1] + rr * math.sin(a)))
    out[0] = out[0] + (1,)
    out[24] = out[24] + (1,)
    s.append(shape(out, body, blob(ellipse_pts(x + r * .55, y + r * .35, r * .5, r * .5, 14), mix("#d8cfae", "#f3c94a", k), .85), w=5, seed=60))
    for j, (dx, dy, r0) in enumerate([(-130, -50, 13), (100, -80, 10), (-60, 90, 9), (130, 60, 11)]):
        tw = 0.75 + 0.25 * math.sin(t * 4.2 + j * 1.7)
        s.append(star(x + dx, y + dy, r0 * tw * (0.8 + 0.4 * k), mix("#d9cfa8", "#ffd94a", k), 70 + j, rot=10 * j))
    return "".join(s)


# ───────────────────────── части мозга-персонажа (локальные координаты мозга, лицом влево)
def nightcap(swing=0.0, sd=0):
    """Ночной колпак на макушке, кисточка свисает назад (вправо); swing — качание кончика."""
    sw = swing * 30
    pts = [(BCX - 178, BCY - 96, 1), (BCX - 120, BCY - 196), (BCX - 30, BCY - 270), (BCX + 70, BCY - 302 + sw * .2), (BCX + 170, BCY - 282 + sw * .6),
           (BCX + 240 + sw * .3, BCY - 210 + sw, 1), (BCX + 158, BCY - 236 + sw * .6), (BCX + 92, BCY - 226), (BCX + 140, BCY - 160),
           (BCX + 172, BCY - 112, 1), (BCX + 80, BCY - 152), (BCX - 10, BCY - 170), (BCX - 100, BCY - 146)]
    inner = blob([(BCX + 20, BCY - 300), (BCX + 180, BCY - 290), (BCX + 250, BCY - 200 + sw), (BCX + 150, BCY - 140), (BCX + 60, BCY - 160)], CAP_SH, .9)
    for j, (dx, dy) in enumerate([(-90, -200), (-10, -230), (60, -270), (140, -250), (20, -180), (-120, -150)]):
        inner += star(BCX + dx, BCY + dy, 13, "#ffe27a", sd + 10 + j, rot=15 * j, w=2.2)
    s = shape(pts, CAP, inner, w=5, seed=sd)
    # опушка и помпон
    brim = [(BCX - 190, BCY - 90, 1), (BCX - 100, BCY - 150), (BCX - 10, BCY - 176), (BCX + 80, BCY - 160), (BCX + 184, BCY - 112, 1),
            (BCX + 186, BCY - 82, 1), (BCX + 82, BCY - 128), (BCX - 10, BCY - 144), (BCX - 96, BCY - 120), (BCX - 186, BCY - 60, 1)]
    s += shape(brim, "#fbf6ea", blob([(BCX - 186, BCY - 70), (BCX + 186, BCY - 92), (BCX + 186, BCY - 82), (BCX - 186, BCY - 60)], "#e2dccb", .9),
               w=4.6, seed=sd + 2)
    px, py = BCX + 244 + sw * .3, BCY - 200 + sw
    s += shape(ellipse_pts(px, py, 30, 30, 16), "#fbf6ea", blob(ellipse_pts(px + 8, py + 10, 20, 16, 12), "#e2dccb", .9), w=4.4, seed=sd + 3)
    return s


def yawn_mouth(k):
    mx, my = BCX - 72, BCY + 76
    rx, ry = 12 + 10 * k, 14 + 22 * k
    return shape(ellipse_pts(mx, my, rx, ry, 16), "#7a2a40", blob(ellipse_pts(mx, my + ry * .45, rx * .6, ry * .35, 12), "#e2543f"), w=3.6, seed=896)


def glow_overlay(k, col="#fff2a8"):
    """Подсветка мозга изнутри (вспышка) — тот же контур, полупрозрачная заливка поверх рисунка."""
    if k < 0.02:
        return ""
    return blob(brain_art.brain_outline(), col, .32 * k)


def thumb_up(W_, sc, sd):
    """Кулак с поднятым большим пальцем: запястье W_ снизу, кулак над ним, большой палец вверх (мировые координаты)."""
    x, y = W_
    s = []
    k = sc * 1.25
    thumb = sb.sausage([(x - 6 * k, y - 40 * k), (x - 8 * k, y - 62 * k), (x - 7 * k, y - 84 * k)], 17 * k, 16 * k)
    s.append(shape(thumb, SKIN, "", w=3.2, seed=sd))
    fist = rect_pts(x - 26 * k, y - 46 * k, x + 24 * k, y + 2 * k, 14 * k)
    inner = blob(rect_pts(x + 6 * k, y - 46 * k, x + 24 * k, y + 2 * k), SKIN_SH, .8)
    for j in range(3):
        yy = y - 32 * k + j * 12 * k
        inner += line([(x - 2 * k, yy), (x + 14 * k, yy + 1 * k), (x + 22 * k, yy + 4 * k)], 3.0, INK, taper=.4, wmin=.3, seed=sd + 3 + j)
    s.append(shape(fist, SKIN, inner, w=3.4, seed=sd + 1))
    return "".join(s)


def dumbbell(C, ang, sc, sd):
    """Гантелька: центр грифа C, гриф вдоль ang (градусы)."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    L = 64 * sc
    s = []
    s.append(line([(C[0] - ux * L, C[1] - uy * L), (C[0] + ux * L, C[1] + uy * L)], 13 * sc, "#4a4f5e", taper=.02, wmin=1, seed=sd))
    for j, side in enumerate((-1, 1)):
        for q, (d, h, w) in enumerate(((L * .78, 40, 16), (L * 1.02, 30, 12))):
            cx, cy = C[0] + ux * d * side, C[1] + uy * d * side
            pts = [(cx + ux * w / 2 * sc * s_ + -uy * h / 2 * sc * t_, cy + uy * w / 2 * sc * s_ + ux * h / 2 * sc * t_)
                   for s_, t_ in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            pts = [p + (1,) for p in pts]
            s.append(shape(pts, "#3a3f52" if q == 0 else "#5a6078", "", w=3.4, seed=sd + 2 + j * 2 + q))
    return "".join(s)


def legs(pose, feet, face=-1, sd=0):
    hl, hr = pose.pt(*b32.HIP_L), pose.pt(*b32.HIP_R)
    return b32.leg(hr, feet[1], pose.sc, face, sd + 20) + b32.leg(hl, feet[0], pose.sc, face, sd)


def body(pose, face_svg, cap_svg, arm_l, arm_r, hand_l, hand_r, between="", glow=0.0):
    """arm_* = (запястье, выгиб); hand_* — готовый SVG кисти (рисуется поверх мозга)."""
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    s = [sb.arm(SR, arm_r[0], arm_r[1], 2, pose.sc), sb.arm(SL, arm_l[0], arm_l[1], 1, pose.sc)]
    s.append(f'<g transform="{pose.tf()}">{_ST["brain"]}{glow_overlay(glow)}{face_svg}{cap_svg}</g>')
    s.append(between)
    s.append(hand_r)
    s.append(hand_l)
    return "".join(s)


def zzz(t, x, y, t0, k=1.0):
    s = []
    if k < 0.02:
        return ""
    for j in range(3):
        ph = (t - t0) / 1.5 + j / 3
        if ph < 0:
            continue
        ph %= 1
        sc = back_out(clamp(ph / 0.25), 2) * (1 - ease_in(clamp((ph - 0.8) / 0.2), 2)) * (0.6 + 0.6 * ph) * k
        if sc < 0.03:
            continue
        cx = x + 120 * ph + 14 * math.sin(ph * 9 + j)
        cy = y - 220 * ph
        r = 24 * sc
        pts = [(cx - r, cy - r), (cx + r, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
        s.append(line(pts, 9 * sc + 3, "#3d4f9e", taper=.1, wmin=.8, seed=900 + j))
    return "".join(s)


def pop_rays(x, y, e, sd, r=70, col="#f6b52a", dur=.4):
    if e < 0 or e > dur:
        return ""
    u = e / dur
    s = []
    for k in range(10):
        a = k * math.pi / 5 + .3
        r0 = r + 90 * ease_out(u)
        L = 44 * (1 - u)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))], 8, col,
                      taper=.5, seed=sd + k))
    return "".join(s)


# ───────────────────────── утренний (левый) — рисуется лицом влево вокруг X0 и отражается
def morning(t):
    on = smooth(UTR - .04, UTR + .06, t)                    # вспыхнул
    off = smooth(VECH - .1, VECH + .25, t)                 # пошёл спать
    hop = 0.0
    if on > 0 and off < 1:                                  # бодрые подскоки
        hop = abs(math.sin((t - UTR) * math.pi * 2.6)) * 22 * (1 - off)
    jump = 46 * bump(t, UTR - .02, .42)
    br = math.sin(t * 2 * math.pi / 1.4)
    idle_bob = 6 * abs(math.sin(t * math.pi * 1.25)) * (1 - on)
    land = max(0.0, 1 - abs(t - (VECH + .2)) / .14) if VECH + .06 < t < VECH + .34 else 0.0     # колпак шлёпнулся
    slump = off
    y = Y0 - jump - hop - idle_bob + 8 * slump + 6 * land
    rot = -2 * on * (1 - off) * math.sin(t * 8) + 5 * slump + 2 * math.sin(t * 1.3)
    pose = sb.Pose(X0, y + 3 * br, SC * (1 + .01 * br), rot, 1.0 - 0.06 * land + 0.04 * bump(t, UTR - .02, .42))
    # лицо
    look = (-0.7, -0.15 * on)
    blink = blink_at(t, [15.25, 16.05, 17.15])
    if off > .5:
        fc = b32.face(0.0, mouth="smile" if t > NORM else "snore", t=t)
    else:
        fc = b32.face(1.0, look, "smile", t, brow=0.8 * on, blink=blink)
    # колпак: падает сверху на «вечером»
    cap = ""
    if t > VECH - .05:
        u = clamp((t - (VECH - .05)) / .25)
        dy = -420 * (1 - ease_in(u, 2))
        sw = math.sin((t - VECH) * 9) * math.exp(-max(0, t - VECH - .2) * 3) + .15 * math.sin(t * 1.7)
        cap = f'<g transform="translate(0 {f(dy)})">{nightcap(sw, 500)}</g>'
    # руки: задняя (R) — гантелька, передняя (L) — машет
    S_R = pose.pt(*sb.SH_R)
    S_L = pose.pt(*sb.SH_L)
    pump = 0.5 + 0.5 * math.sin((t - UTR) * 2 * math.pi * 2.2 - math.pi / 2)
    if on < 0.5 or off > 0.5:
        down = (S_R[0] + 46, S_R[1] + 48)
        if off > 0.5:               # гантелька лежит у ног
            k = smooth(VECH - .1, VECH + .2, t)
            wr_r = (S_R[0] + 44, S_R[1] + 50)
            arm_r = (wr_r, 40)
            hand_r = sb.toon_hand(wr_r[0], wr_r[1], 80, 0.5, 60, pose.sc * 1.3)
            db = dumbbell((X0 + 150, FLOOR - 18), 0, SC * 1.1, 700) if k > .5 else ""
            between = db
            dbel_front = ""
        else:
            wr_r = down
            arm_r = (wr_r, 30)
            between = dumbbell((wr_r[0] + 30 * math.cos(math.radians(80)) * SC * 1.3, wr_r[1] + 40 * SC * 1.3), 0, SC * 1.1, 700)
            hand_r = sb.toon_hand(wr_r[0], wr_r[1], 80, 0.85, 60, pose.sc * 1.3)
            dbel_front = ""
    else:
        top = (S_R[0] + 70, S_R[1] - 250)
        low = (S_R[0] + 110, S_R[1] - 90)
        wr_r = (low[0] + (top[0] - low[0]) * pump, low[1] + (top[1] - low[1]) * pump)
        arm_r = (wr_r, 50 - 20 * pump)
        ang = -70 - 20 * pump
        a = math.radians(ang)
        C = (wr_r[0] + math.cos(a) * 46 * SC * 1.3, wr_r[1] + math.sin(a) * 46 * SC * 1.3)
        between = dumbbell(C, ang + 90, SC * 1.1, 700)
        hand_r = sb.toon_hand(wr_r[0], wr_r[1], ang, 0.85, 60, pose.sc * 1.3)
        dbel_front = ""
    # передняя рука
    if off > .5 and t > NORM - .1:
        k = spring(t - (NORM - .08), 2.2, 6)
        rest = (S_L[0] - 52, S_L[1] + 46)
        up = (S_L[0] - 70, S_L[1] - 40)
        wl = (rest[0] + (up[0] - rest[0]) * k, rest[1] + (up[1] - rest[1]) * k)
        arm_l = (wl, -30)
        hand_l = thumb_up(wl, pose.sc, 80)
    elif on > .5 and off < .5:
        wv = math.sin((t - UTR) * 2 * math.pi * 2.2)
        wl = (S_L[0] - 110 + 20 * wv, S_L[1] - 150 - 30 * on)
        arm_l = (wl, -40)
        hand_l = sb.toon_hand(wl[0], wl[1], -100 + 25 * wv, 0.05, 30, pose.sc * 1.3, spread=1.3)
    else:
        sw = 6 * math.sin(t * 2.4)
        wl = (S_L[0] - 52, S_L[1] + 46 + sw)
        arm_l = (wl, -30)
        hand_l = sb.toon_hand(wl[0], wl[1], 118, 0.4, 30, pose.sc * 1.3)
    glow = on * (1 - off) * (0.55 + 0.45 * math.exp(-max(0, t - UTR) * 3))
    # ножки: подскоки — стопы отрываются вместе
    hl, hr = pose.pt(*b32.HIP_L), pose.pt(*b32.HIP_R)
    fy = FLOOR - 21
    lift = jump + hop
    feet = [(hl[0] - 14, min(fy - lift * .9, hl[1] + 140)), (hr[0] + 6, min(fy - lift * .9, hr[1] + 140))]
    sh = blob(ellipse_pts(X0, FLOOR - 4, 150 * (1 - lift / 200), 16, 16), "#8a7444", .32, blur(5))
    art = sh + legs(pose, feet, -1, 1200) + body(pose, fc, cap, arm_l, arm_r, hand_l, hand_r, between, glow)
    art += dbel_front
    fx = pop_rays(X0, Y0 - 40, t - UTR, 300, r=230)
    zz = zzz(t, X0 - 170, Y0 - 210, VECH + .35, smooth(VECH + .3, VECH + .5, t))
    return f'<g transform="translate({f(2 * X0)} 0) scale(-1 1)">{art}{fx}</g>' + zz


# ───────────────────────── вечерний (правый) — лицом влево к столику
def evening(t):
    on = smooth(VECH - .03, VECH + .07, t)
    br = math.sin(t * 2 * math.pi / 2.0)
    yawn = bump(t, UTR + .02, .9) * (1 - on)
    nod = 0.0
    for c in (15.35, 15.95):
        nod += 9 * bump(t, c, .5)
    pop = 38 * bump(t, VECH - .02, .36)
    type_bob = 4 * math.sin(t * 2 * math.pi * 3.2) * on
    y = Y0 + 10 * (1 - on) - pop + type_bob
    rot = (6 + nod - 9 * yawn + 1.5 * math.sin(t * 1.1)) * (1 - on) + on * (-3 + 1.2 * math.sin(t * 6.4))
    pose = sb.Pose(X1, y + 3 * br, SC * (1 + .012 * br), rot, 1 + .05 * bump(t, VECH - .02, .36))
    S_L, S_R = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    # лицо
    if on > .5:
        blink = blink_at(t, [18.25, 19.1])
        fc = b32.face(1.0, (-0.6, 0.35), "smile", t, brow=1.0 * math.exp(-max(0, t - VECH) * 2) + 0.2, blink=blink)
    elif yawn > .15:
        fc = _face_no_mouth_closed() + yawn_mouth(yawn)
    else:
        lid = 0.58 + 0.25 * max(bump(t, 15.35, .5), bump(t, 15.95, .5)) + 0.3 * blink_at(t, [14.95, 16.95], .2)
        fc = _face_drowsy(clamp(lid, 0, 0.98))
    # колпак: на голове, на «вечером» слетает вверх-вправо, кувыркаясь
    if t < VECH:
        cap = nightcap(.25 * math.sin(t * 1.5) + .3 * yawn, 520)
        cap_fly = ""
    else:
        cap = ""
        e = t - VECH
        if e < 1.0:
            cx, cy = pose.pt(BCX + 30, BCY - 220)
            dx, dy = 520 * e, -900 * e + 900 * e * e
            cap_fly = (f'<g transform="translate({f(cx + dx)} {f(cy + dy)}) rotate({f(260 * e)}) scale({f(pose.sc)}) '
                       f'translate({-BCX - 30} {-BCY + 220})">{nightcap(math.sin(e * 14), 520)}</g>')
        else:
            cap_fly = ""
    # руки
    if on > .5:
        tp = t * 2 * math.pi * 5.0
        wl = (TBL[0] + 56 + 8 * math.sin(tp), TBL[1] - 46 - 9 * abs(math.sin(tp)))
        arm_l = (wl, -26)
        hand_l = sb.toon_hand(wl[0], wl[1], 168, 0.45 + .15 * math.sin(tp), 30, pose.sc * 1.3)
        if t > NORM - .08:
            k = spring(t - (NORM - .06), 2.2, 6)
            r0 = (TBL[0] + 96 + 8 * math.sin(tp + 2), TBL[1] - 40)
            up = (S_R[0] + 70, S_R[1] - 120)
            wr = (r0[0] + (up[0] - r0[0]) * k, r0[1] + (up[1] - r0[1]) * k)
            arm_r = (wr, 40)
            hand_r = thumb_up(wr, pose.sc, 60) if k > .35 else sb.toon_hand(wr[0], wr[1], 168, .5, 60, pose.sc * 1.3)
        else:
            wr = (TBL[0] + 96 + 8 * math.sin(tp + 2), TBL[1] - 44 - 9 * abs(math.sin(tp + 2)))
            arm_r = (wr, 34)
            hand_r = sb.toon_hand(wr[0], wr[1], 172, 0.45 + .15 * math.sin(tp + 2), 60, pose.sc * 1.3)
    else:
        sw = 5 * math.sin(t * 1.8)
        wl = (S_L[0] - 48 + sw, S_L[1] + 50)
        arm_l = (wl, -24)
        hand_l = sb.toon_hand(wl[0], wl[1], 112, 0.35, 30, pose.sc * 1.3)
        if yawn > .05:          # потягивается задней рукой
            wr = (S_R[0] + 46 + 30 * yawn, S_R[1] + 50 - 240 * yawn)
            arm_r = (wr, 40)
            hand_r = sb.toon_hand(wr[0], wr[1], 80 - 170 * yawn, 0.3, 60, pose.sc * 1.3)
        else:
            wr = (S_R[0] + 46 - sw, S_R[1] + 50)
            arm_r = (wr, 30)
            hand_r = sb.toon_hand(wr[0], wr[1], 70, 0.35, 60, pose.sc * 1.3)
    glow = on * (0.45 + 0.55 * math.exp(-max(0, t - VECH) * 3))
    hl, hr = pose.pt(*b32.HIP_L), pose.pt(*b32.HIP_R)
    fy = FLOOR - 21
    feet = [(hl[0] - 12, min(fy - pop * .9, hl[1] + 140)), (hr[0] + 8, min(fy - pop * .9, hr[1] + 140))]
    sh = blob(ellipse_pts(X1, FLOOR - 4, 150, 16, 16), "#8a7444", .32, blur(5))
    screen = laptop_light(t, on)
    art = sh + legs(pose, feet, -1, 1300) + screen + body(pose, fc, cap, arm_l, arm_r, hand_l, hand_r, "", glow)
    fx = pop_rays(X1, Y0 - 40, t - VECH, 320, r=230, col="#f6b52a")
    zk = (1 - on) * smooth(14.4, 14.6, t) * (1 - yawn)
    fx += zzz(t, X1 - 60, Y0 - 230, 14.3, zk * .8)
    return art + fx + cap_fly


def eyes(look, blink=0.0, brow=0.0):
    """Открытые глаза лица scene_brain32 без рта (веко blink 0..1) и румянец."""
    s = []
    ry = 36
    for k, (x, y) in enumerate((b32.EYE_L, b32.EYE_R)):
        px, py = x + look[0] * 10, y + look[1] * 12
        inner = f'<circle cx="{f(px)}" cy="{f(py)}" r="9.5" fill="{INK}"/><circle cx="{f(px - 3)}" cy="{f(py - 3.5)}" r="3" fill="#ffffff"/>'
        if blink > 0.02:
            yb = y - ry - 2 + (2 * ry + 4) * blink
            inner += f'<rect x="{x - 32}" y="{y - ry - 4}" width="64" height="{f(yb - (y - ry - 4))}" fill="#f6a9bc"/>'
            inner += line([(x - 30, yb), (x, yb + 3), (x + 30, yb)], 4, INK, seed=890 + k)
        s.append(shape(ellipse_pts(x, y, 29, ry, 18), "#ffffff", inner, w=4.4, seed=886 + k))
        if brow:
            by = y - ry - 16 - 8 * brow
            s.append(line([(x - 22, by + 4), (x, by - 4 * brow), (x + 20, by + 2)], 5.5, "#8e3358", taper=.4, wmin=.4, seed=892 + k))
    s.append(blob(ellipse_pts(BCX - 160, BCY + 56, 20, 10, 10), "#f07a98", .55))
    return "".join(s)


def _face_drowsy(lid):
    s = eyes((-0.5, 0.4), lid)
    mx, my = BCX - 72, BCY + 78
    s += line([(mx - 20, my + 2), (mx, my + 6), (mx + 18, my + 1)], 5, "#7a2a40", taper=.4, wmin=.4, seed=897)
    return s


def _face_no_mouth_closed():
    s = []
    for k, (x, y) in enumerate((b32.EYE_L, b32.EYE_R)):
        s.append(line([(x - 26, y - 4), (x - 10, y + 6), (x + 10, y + 6), (x + 26, y - 4)], 6.5, INK, taper=.4, wmin=.35, seed=880 + k))
    s.append(blob(ellipse_pts(BCX - 160, BCY + 56, 20, 10, 10), "#f07a98", .55))
    return "".join(s)


# ───────────────────────── столик и ноутбук (вид сбоку: экран смотрит вправо, на вечерний мозг)
def table():
    x, y = TBL
    s = [blob(ellipse_pts(x, FLOOR - 4, 90, 12, 14), "#8a7444", .3, blur(4))]
    s.append(shape([(x - 12, y + 10, 1), (x + 12, y + 10, 1), (x + 16, FLOOR - 16, 1), (x - 16, FLOOR - 16, 1)], "#a5703f",
                   blob([(x + 2, y + 10), (x + 12, y + 10), (x + 16, FLOOR - 16), (x + 4, FLOOR - 16)], "#86552c", .9), w=4, seed=600))
    s.append(shape(ellipse_pts(x, FLOOR - 14, 56, 12, 14), "#a5703f", blob(ellipse_pts(x + 12, FLOOR - 10, 40, 8, 12), "#86552c", .9), w=4, seed=601))
    s.append(shape(rect_pts(x - 100, y - 6, x + 100, y + 16, 8), "#b47c48",
                   blob(rect_pts(x - 100, y + 5, x + 100, y + 16), "#8c5a30", .9) + line([(x - 80, y - 1), (x + 40, y - 1)], 3, "#d8a26a", seed=602, op=.9),
                   w=4.4, seed=603))
    return "".join(s)


def laptop(t):
    """Ноутбук на столике: петля слева, экран обращён вправо; на «вечером» крышка поднимается."""
    x, y = TBL
    op = ease_out(clamp((t - VECH) / .22)) + 0.05 * bump(t, VECH + .2, .25)
    base = rect_pts(x - 76, y - 20, x + 70, y - 6, 4)
    s = [shape(base, "#9aa3b8", blob(rect_pts(x - 76, y - 12, x + 70, y - 6), "#6b7389", .9) +
               "".join(line([(x - 50 + j * 20, y - 17), (x - 40 + j * 20, y - 17)], 3, "#5a6078", seed=610 + j, op=.8) for j in range(5)),
               w=4, seed=611)]
    a = math.radians(-108 * op)
    hx, hy = x - 72, y - 21
    L, th = 140, 12
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    p = [(hx, hy, 1), (hx + ux * L, hy + uy * L, 1), (hx + ux * L - nx * th, hy + uy * L - ny * th, 1), (hx - nx * th, hy - ny * th, 1)]
    scr = "#dce8ff" if op > .3 else "#9aa3b8"
    s.append(shape(p, "#7b8399", blob([p[0][:2], p[1][:2], (p[1][0] - nx * 5, p[1][1] - ny * 5), (p[0][0] - nx * 5, p[0][1] - ny * 5)], scr, .95),
                   w=4, seed=612))
    return "".join(s)


def laptop_light(t, on):
    if on < .02:
        return ""
    x, y = TBL
    k = on * (0.8 + 0.2 * math.sin(t * 9))
    g = rad_grad([(0, "#d8e6ff", .85 * k), (1, "#d8e6ff", 0)], x + 60, y - 120, 260, 180)
    return f'<ellipse cx="{f(x + 60)}" cy="{f(y - 120)}" rx="260" ry="180" fill="url(#{g})"/>'


def checkmark(t):
    e = t - NORM
    if e < 0:
        return ""
    u = clamp(e / .28)
    cx, cy = 540, 230
    pts = [(cx - 90, cy + 2), (cx - 62, cy + 26), (cx - 26, cy + 64), (cx + 30, cy - 10), (cx + 110, cy - 96)]
    S = lib.sample(pts, False, 4.0)
    n = max(2, int(len(S) * ease_out(u, 2)))
    q = [tuple(p) for p in S[:n]]
    sc = 1 + 0.12 * bump(t, NORM + .26, .3)
    s = (f'<g transform="translate({cx} {cy}) scale({f(sc)}) translate({-cx} {-cy})">' +
         line(q, 44, INK, taper=.02, wmin=1, seed=950) + line(q, 30, "#3fb54b", taper=.02, wmin=1, seed=951) +
         line(q[: max(2, n - 3)], 9, "#a6e59a", taper=.3, wmin=.4, seed=952, op=.8) + "</g>")
    if u >= 1:
        for j, (dx, dy) in enumerate([(-150, -40), (150, -110), (40, 90)]):
            k = back_out(clamp((e - .28) / .2), 2) * (0.85 + 0.15 * math.sin(t * 7 + j))
            s += star(cx + dx, cy + dy, 22 * k, "#ffd34e", 960 + j, rot=30 * e)
    return s


# ───────────────────────── кадр и камеры
def scene(t):
    day = 1 - 0.75 * smooth(VECH, VECH + .4, t)
    pun_sun = bump(t, UTR - .02, .4)
    night = 0.35 + 0.65 * smooth(VECH - .05, VECH + .3, t)
    return (halos(day, night) + sun(t, day, pun_sun) + moon(t, night - .2 if night > .2 else 0) + table() + laptop(t) +
            evening(t) + morning(t) + checkmark(t))


def camera(sid, t):
    if sid == "s09":
        u = ease_io(clamp((t - 14.52) / 1.9))
        cx, cy, s = 540 - 170 * u, 700, 1.12 + 0.30 * u
        e = t - UTR
        if e > 0:
            k = math.exp(-e * 6)
            s *= 1 + 0.05 * k * math.sin(min(e * 14, math.pi))
            cy += 8 * k * math.sin(e * 40)
        rot = 0.6 * math.sin(t * 1.2)
    else:
        u = ease_io(clamp((t - 16.8) / 1.0))
        cx, cy, s = 420 + 290 * u, 700, 1.30 + 0.08 * u
        o = ease_io(clamp((t - (NORM - .14)) / .32))
        cx += (540 - cx) * o
        cy += (650 - cy) * o
        s += (1.08 - s) * o + 0.04 * clamp((t - NORM) / 1.1)
        for c in (VECH, NORM):
            e = t - c
            if e > 0:
                k = math.exp(-e * 6)
                s *= 1 + 0.045 * k * math.sin(min(e * 14, math.pi))
                cy += 7 * k * math.sin(e * 40)
        rot = 0.5 * math.sin(t * 1.1)
    return cam(cx, cy, s, rot)


def build_static():
    if _ST:
        return
    _ST["bg"] = background()
    _ST["brain"] = brain_art.brain(0, 0, stem=False)
    sb._ST["brain"] = _ST["brain"]
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art = scene(t)
    return svg(f'<rect width="{W}" height="{H}" fill="{CREAM}"/><g transform="{camera(sid, t)}">{_ST["bg"]}{art}</g>')


_ = (band, ease_in, mix, np, H)
