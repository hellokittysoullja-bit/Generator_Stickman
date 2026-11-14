"""Сцена brain рилса 44 (копия мозга рилсов 32–41: brain_art без ствола, ручки scene_brain, ножки в кедах и лицо
scene_brain32) в той же ночной комнате.
s06 (9.85–12.85): мозг стоит и смотрит в облачко-экран с картинкой мечты (Фудзи, сакура, тории); на «радуется» (10.72)
     хлопает в ладоши над головой, летит конфетти; на «съездил» (12.2) облачко-экран лопается — пуф — и мозг уже в
     панамке с цветочком, на шее фотоаппарат, рядом чемодан в наклейках; довольно машет, будто вернулся из поездки.
s07 (12.85–14.65): над мозгом большая батарейка; на «сил» (13.08) она быстро разряжается от зелёной до красной пустой
     (мигает), мозг сникает; на «остаётся» (13.84) пятится и оседает на чемодан, зевает и засыпает, плывут «Z».
Всё — функция общего времени ролика t."""
import math

import numpy as np

import brain_art
import japan
import lib
import scene_brain as sb
import scene_brain32 as b32
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad,
                 rect_pts, shape, smooth, spring, svg)

_ST = {}
FLOOR = sb.FLOOR          # 1160
G = FLOOR - 26            # пол под кедами
JOY = 10.72               # «радуется»
TRIP = 12.20              # «съездил»
SIL = 13.08               # «сил»
REST = 13.84              # «остаётся»
SC = 1.2
BX = 600                  # мозг стоит
SUIT = (825, G + 8)       # чемодан лежит: центр низа
SW, SHT = 290, 156        # его ширина и высота
SCR = (370, 390)          # облачко-экран (центр)
SCR_K = 0.62              # масштаб картинки мечты 600×400


# ───────────────────────── предметы
def screen_cloud(t, k=1.0):
    """Облачко-экран с картинкой мечты; k — масштаб (появление/пуф)."""
    if k <= 0.02:
        return ""
    x, y = SCR[0], SCR[1] + 8 * math.sin(t * 2.2)
    rx, ry = 230, 165
    rim = japan.cloud_pts(0, 0, rx + 26, ry + 24, 11, .14, .3)
    win = japan.cloud_pts(0, 0, rx - 6, ry - 8, 11, .08, .3)
    s = []
    s.append(shape(rim, "#ffffff", blob(japan.cloud_pts(30, 40, rx + 10, ry + 6, 11, .14, .3), "#cfe0f6", .95) +
                   blob(japan.cloud_pts(-20, -20, rx, ry, 11, .14, .3), "#ffffff"), w=5, seed=60))
    c = lib.clip_of(win)
    pic = f'<g transform="translate({f(-300 * SCR_K)} {f(-200 * SCR_K)}) scale({SCR_K})">{japan.mini_dream(t, 70)}</g>'
    pic += japan.petals(t, (-rx, -ry, rx, ry), 6, 90, (6, 9), (40, 70), 50)
    s.append(f'<g clip-path="url(#{c})">{pic}</g>')
    s.append(f'<path d="{lib.ink_closed(win, 3.6, seed=61)}" fill="{INK}"/>')
    # хвостик мысли: три пузырька к мозгу
    for j, (bx, by, r) in enumerate([(250, 150, 22), (300, 200, 15), (335, 238, 10)]):
        s.append(shape(ellipse_pts(bx, by, r, r * .85, 14), "#ffffff", blob(ellipse_pts(bx + r * .3, by + r * .3, r * .7, r * .5, 10), "#cfe0f6", .9),
                       w=3.4, seed=62 + j))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(k)})">{"".join(s)}</g>'


def suitcase(sd=0, squash=0.0):
    """Чемодан лежит на боку: бирюзовый, ручка сверху, уголки, колёсики справа, наклейки (без букв)."""
    x, y = SUIT
    h = SHT * (1 - squash)
    x0, x1, y0 = x - SW / 2, x + SW / 2, y - h
    s = []
    s.append(sb.shadow(x, y + 4, 190, .5))
    s.append(line([(x - 50, y0 + 2), (x - 46, y0 - 26), (x + 46, y0 - 26), (x + 50, y0 + 2)], 11, "#2a2f44", taper=.1, wmin=.9, seed=sd + 1))
    inner = blob(rect_pts(x0, y - h * .38, x1, y), "#2d8a8f", .9)
    inner += line([(x0 + 12, y0 + h * .5), (x1 - 12, y0 + h * .5)], 3, "#1f6266", seed=sd + 2, op=.9)
    # наклейки
    st = []
    st.append(sticker_fuji(x - 92, y0 + h * .34, 34, sd + 10))
    st.append(shape(ellipse_pts(x - 6, y0 + h * .62, 30, 30, 18), "#ffd85a", blob(ellipse_pts(x + 4, y0 + h * .66, 22, 20, 14), "#ffbf3a", .9), w=3.2, seed=sd + 20))
    st.append(sakura_sticker(x + 72, y0 + h * .36, 30, sd + 30))
    st.append(shape(rect_pts(x + 40, y0 + h * .6, x + 112, y0 + h * .86, 6), "#ffffff",
                    japan.torii(x + 76, y0 + h * .82, 30, sd + 40), w=3, seed=sd + 41))
    s.append(shape(rect_pts(x0, y0, x1, y, 22), "#3fb0b4", inner + "".join(st), w=5.4, seed=sd))
    for k, (cx, cy) in enumerate([(x0 + 14, y0 + 14), (x1 - 14, y0 + 14), (x0 + 14, y - 14), (x1 - 14, y - 14)]):
        s.append(shape(ellipse_pts(cx, cy, 12, 12, 12), "#2a2f44", "", w=2.6, seed=sd + 50 + k))
    return "".join(s)


def sticker_fuji(x, y, r, sd):
    pic = blob(rect_pts(x - r, y - r, x + r, y + r), "#9fd0f2") + japan.fuji(x, y + r * .75, r * 2.0, r * 1.15, sd + 1)
    c = lib.clip_of(ellipse_pts(x, y, r, r, 18))
    return f'<g clip-path="url(#{c})">{pic}</g>' + f'<path d="{lib.ink_closed(ellipse_pts(x, y, r, r, 18), 3.2, seed=sd)}" fill="{INK}"/>'


def sakura_sticker(x, y, r, sd):
    s = shape(ellipse_pts(x, y, r, r, 18), "#ffffff", "", w=3, seed=sd)
    return s + japan.flower(x, y, r * .8, 10, "#f7b8cc", "#e8678f")


def panama(t):
    """Панамка с цветочком — в локальных координатах мозга."""
    s = []
    cx, cy = BCX - 30, BCY - 138
    brim = [(cx - 168, cy + 6), (cx - 120, cy - 22), (cx, cy - 30), (cx + 130, cy - 20), (cx + 170, cy + 4), (cx + 120, cy + 26), (cx, cy + 32),
            (cx - 120, cy + 28)]
    s.append(shape(brim, "#f2e6c4", blob([(cx - 168, cy + 8), (cx + 170, cy + 6), (cx + 120, cy + 28), (cx - 120, cy + 30)], "#d8c79a", .9), w=4.6, seed=70))
    crown = [(cx - 104, cy - 6, 1), (cx - 98, cy - 66), (cx - 60, cy - 104), (cx + 10, cy - 112), (cx + 72, cy - 96), (cx + 104, cy - 56), (cx + 108, cy - 6, 1)]
    s.append(shape(crown, "#f6ecd0", blob([(cx + 30, cy - 120), (cx + 120, cy - 60), (cx + 110, cy), (cx + 40, cy)], "#ddcda2", .9) +
                   blob([(cx - 110, cy - 34), (cx + 110, cy - 34), (cx + 110, cy - 4), (cx - 110, cy - 4)], "#e0533e") +
                   line([(cx - 104, cy - 34), (cx + 108, cy - 34)], 2.4, "#a8352a", seed=72, op=.8), w=4.8, seed=71))
    # цветочек сбоку (лицом к зрителю — слева)
    fx, fy = cx - 76, cy - 22
    sw = 4 * math.sin(t * 3)
    for k in range(5):
        a = math.radians(k * 72 + sw * 3)
        s.append(shape(ellipse_pts(fx + 17 * math.cos(a), fy + 17 * math.sin(a), 14, 11, 10, rot=math.degrees(a)), "#ffffff",
                       blob(ellipse_pts(fx + 20 * math.cos(a), fy + 20 * math.sin(a), 7, 5, 8), "#ffd3de", .9), w=2.6, seed=73 + k))
    s.append(shape(ellipse_pts(fx, fy, 9, 9, 10), "#ffcf3a", "", w=2.4, seed=79))
    return "".join(s)


def neck_camera(t, swing=0.0):
    """Фотоаппарат на ремешке: ремешок через макушку (лок. координаты мозга), камера висит спереди-слева."""
    s = []
    cx, cy = BCX - 196 + swing * 6, BCY + 150
    s.append(line([(BCX - 150, BCY + 112), (BCX - 160, BCY + 120), (cx + 34, cy - 30)], 5, "#3a3440", taper=.1, wmin=.9, seed=80))
    s.append(line([(BCX - 214, BCY + 30), (BCX - 222, BCY + 60), (cx - 30, cy - 32)], 5, "#3a3440", taper=.1, wmin=.9, seed=81))
    g = (shape(rect_pts(-62, -42, 62, 42, 10), "#3a3f52", blob(rect_pts(-62, 8, 62, 42), "#262a38", .9) +
               blob(rect_pts(30, -42, 54, -28), "#c9cfdd", .95), w=4.4, seed=82) +
         shape(ellipse_pts(-6, 2, 34, 34, 20), "#262a38", blob(ellipse_pts(-6, 2, 20, 20, 16), "#6aa3d8") +
               blob(ellipse_pts(-14, -6, 7, 5, 8), "#ffffff", .9), w=3.8, seed=83) +
         shape([(-50, -42, 1), (-50, -56, 1), (-20, -56, 1), (-20, -42, 1)], "#3a3f52", "", w=3, seed=84))
    s.append(f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(-6 + swing * 4)})">{g}</g>')
    return "".join(s)


def confetti(t):
    if t < JOY - 0.02:
        return ""
    rs = np.random.RandomState(14)
    cols = ["#ffd34e", "#5bc0eb", "#f7768e", "#9be15d", "#c792ea", "#ff9f43"]
    s = []
    ox, oy = BX - 100, 440
    for k in range(40):
        t0 = JOY + (k % 4) * 0.2
        e = t - t0
        if e < 0:
            continue
        a = rs.uniform(-math.pi * .95, -math.pi * .05)
        v = rs.uniform(500, 950)
        x = ox + math.cos(a) * v * e * 0.9 + 30 * math.sin(e * 6 + k)
        y = oy + math.sin(a) * v * e + 700 * e * e
        if y > G - 10:
            y = G - 10
        r = rs.uniform(0, 360) + 500 * e * (1 if k % 2 else -1)
        w_, h_ = rs.uniform(10, 16), rs.uniform(18, 26)
        fl = abs(math.cos(e * 9 + k))
        s.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(r)}) scale(1 {f(.25 + .75 * fl)})">'
                 f'{shape(rect_pts(-w_ / 2, -h_ / 2, w_ / 2, h_ / 2), cols[k % 6], "", w=2.2, seed=300 + k % 7)}</g>')
    return "".join(s)


def poof(t, x, y):
    """Пуф-облако на смене (скрывает переодевание)."""
    e = t - (TRIP - 0.1)
    if e < 0 or e > 0.5:
        return ""
    u = e / 0.5
    s = []
    for k in range(7):
        a = k * 2 * math.pi / 7 + 0.4
        rr = 120 + 150 * ease_out(u)
        k_ = back_out(clamp(u / 0.3), 2) * (1 - ease_in(clamp((u - 0.55) / 0.45)))
        if k_ < 0.04:
            continue
        r = 95 * k_
        px, py = x + rr * math.cos(a) * 1.1, y + rr * math.sin(a) * 0.9
        s.append(japan.puff_cloud(px, py, r, r * .8, 400 + k, n=6, bump=.3, w=4.4))
    k_ = back_out(clamp(u / 0.25), 2) * (1 - ease_in(clamp((u - 0.45) / 0.4)))
    if k_ > 0.04:
        s.append(japan.puff_cloud(x, y, 230 * k_, 190 * k_, 410, n=9, bump=.25, w=5))
    return "".join(s)


def stars_burst(t, x, y, t0, n=8, r0=180, sd=500):
    e = t - t0
    if e < 0 or e > 0.6:
        return ""
    u = e / 0.6
    s = []
    for k in range(n):
        a = k * 2 * math.pi / n + 0.2
        rr = r0 + 140 * ease_out(u)
        sc = back_out(clamp(u / 0.3), 2) * (1 - smooth(0.6, 1, u))
        if sc < 0.05:
            continue
        px, py = x + rr * math.cos(a), y + rr * math.sin(a) * .85
        r = 22 * sc
        pts = []
        for i in range(8):
            rad = r if i % 2 == 0 else r * .35
            pts.append((px + rad * math.cos(i * math.pi / 4), py + rad * math.sin(i * math.pi / 4), 1))
        s.append(shape(pts, "#ffe05a", "", w=2.8, seed=sd + k))
    return "".join(s)


# ───────────────────────── батарейка
def battery(t):
    """Батарейка над мозгом: 4 деления; на «сил» гаснут по одному (зелёный → жёлтый → красный), пустая мигает."""
    x, y = 620, 330
    k = back_out(clamp((t - 12.66) / 0.22), 2.2)
    if k < 0.03:
        return ""
    lvl = 4.0 - 4.0 * ease_in(clamp((t - SIL) / 0.5), 1.3)
    col = "#5fd068" if lvl > 2.6 else ("#ffcf3a" if lvl > 1.4 else "#f2453a")
    empty = lvl < 0.05
    blink = empty and (math.sin((t - SIL - 0.5) * 2 * math.pi * 3.0) > 0)
    w2, h2 = 190, 92
    s = []
    rim_c = "#f2453a" if (empty and blink) else "#e8ecf8"
    s.append(shape(rect_pts(-w2, -h2, w2, h2, 26), "#262c4c", blob(rect_pts(-w2, h2 * .2, w2, h2), "#1c2140", .8), w=6, seed=600))
    s.append(f'<path d="{lib.ink_closed(rect_pts(-w2 + 10, -h2 + 10, w2 - 10, h2 - 10, 18), 7, seed=601)}" fill="{rim_c}"/>')
    s.append(shape(rect_pts(w2, -34, w2 + 34, 34, 8), rim_c, "", w=5, seed=602))
    cw = (2 * w2 - 56) / 4
    for i in range(4):
        fill = clamp(lvl - i)
        if i == 0 and empty:
            if blink:
                s.append(shape(rect_pts(-w2 + 26, -h2 + 26, -w2 + 26 + cw * .28, h2 - 26, 4), "#f2453a", "", w=3, seed=610))
            continue
        if fill <= 0.02:
            continue
        x0 = -w2 + 26 + i * (cw + 2)
        x1 = x0 + (cw - 8) * fill
        if x1 - x0 < 6:
            continue
        s.append(shape(rect_pts(x0, -h2 + 26, x1, h2 - 26, 6), col, blob(rect_pts(x0, 8, x1, h2 - 26), lib.mul(col, (.78, .78, .78)), .9) +
                       blob(rect_pts(x0 + 6, -h2 + 32, x1 - 6, -h2 + 42), "#ffffff", .55), w=3.6, seed=620 + i))
    # молния-значок заряда слева сверху (пока полная)
    if lvl > 3.0:
        bx, by = -w2 - 70, -h2 + 10
        bolt = [(bx + 14, by - 40, 1), (bx - 14, by + 8, 1), (bx + 4, by + 8, 1), (bx - 8, by + 44, 1), (bx + 22, by - 4, 1), (bx + 4, by - 4, 1)]
        s.append(shape(bolt, "#ffe05a", "", w=3.4, seed=630))
    jit = 0.0
    if SIL < t < SIL + 0.55:
        jit = 5 * math.sin((t - SIL) * 70)
    return f'<g transform="translate({f(x + jit)} {f(y + 6 * math.sin(t * 2.4))}) scale({f(k)})">{"".join(s)}</g>'


# ───────────────────────── мозг
def body(t, x, y, sc, rot, sq, face_svg, wl, wr, al, ar, cl, cr, fl, fr, bl=-30, br=30, hat=False, cam_sw=None, legs_first=True):
    pose = sb.Pose(x, y, sc, rot, sq)
    hl, hr = pose.pt(*b32.HIP_L), pose.pt(*b32.HIP_R)
    legs = b32.leg(hr, fr, sc, -1, 1200) + b32.leg(hl, fl, sc, -1, 1220)
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    arms = sb.arm(SL, wl, bl, 1301, sc) + sb.arm(SR, wr, br, 1302, sc)
    extra = ""
    if hat:
        extra = neck_camera(t, cam_sw or 0.0) + panama(t)
    brain_svg = f'<g transform="{pose.tf()}">{_ST["brain"]}{face_svg}{extra}</g>'
    hands = sb.toon_hand(wl[0], wl[1], al, cl, 1330, sc * 1.3) + sb.toon_hand(wr[0], wr[1], ar, cr, 1360, sc * 1.3)
    return legs + arms + brain_svg + hands, pose


def s06(t):
    e_trip = t - TRIP
    after = t >= TRIP
    br = math.sin(t * 2 * math.pi / 1.3)
    bounce = 0.0
    if t > JOY - 0.05:     # подпрыгивает от радости в такт хлопкам
        bounce = 16 * abs(math.sin((t - JOY + 0.05) * math.pi / 0.21)) * (1 - smooth(11.75, 11.95, t))
    x = BX
    y = 790 + 4 * br - bounce
    rot = -3 + 2 * math.sin(t * 1.6)
    sq = 1 + 0.02 * br
    if after:
        rot = 3 * math.sin(e_trip * 5) * math.exp(-e_trip * 2) - 2
        y -= 30 * math.exp(-e_trip * 7) * math.sin(min(e_trip * 14, math.pi))
    pose = sb.Pose(x, y, SC, rot, sq)
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    hl, hr = pose.pt(*b32.HIP_L), pose.pt(*b32.HIP_R)
    fl = (hl[0] - 14, G - (bounce * 0.9 if bounce > 0 else 0))
    fr = (hr[0] + 10, G - (bounce * 0.9 if bounce > 0 else 0))
    look = (-0.75, -0.55)
    blink = 0.0
    for c in (10.3, 11.9):
        if abs(t - c) < 0.07:
            blink = 1 - abs(t - c) / 0.07
    if not after:
        # ручки: у груди «ах» → хлопки над головой с «радуется»
        up = smooth(JOY - 0.22, JOY - 0.04, t) * (1 - smooth(11.85, 12.05, t))
        ph = max(0.0, t - JOY)
        gap = 70 * abs(math.sin(ph * math.pi / 0.21)) if t > JOY else 70
        cxh, cyh = pose.x - 90, pose.y - 360
        rest_l, rest_r = (pose.x - 210, pose.y + 150), (pose.x - 120, pose.y + 165)
        tl, tr = (cxh - 22 - gap / 2, cyh), (cxh + 22 + gap / 2, cyh)
        wl = (rest_l[0] + (tl[0] - rest_l[0]) * up, rest_l[1] + (tl[1] - rest_l[1]) * up)
        wr = (rest_r[0] + (tr[0] - rest_r[0]) * up, rest_r[1] + (tr[1] - rest_r[1]) * up)
        al = -20 + (-80 + 20) * up
        ar = -160 + (-100 + 160) * up
        cl = cr = 0.3 * (1 - up)
        mouth = "smile" if t < JOY - 0.1 else "smile"
        face_svg = b32.face(1.0, look, mouth, t, brow=0.9 + 0.3 * up, blink=blink)
        face_svg += sparkle_eyes(t)
        art, pose = body(t, x, y, SC, rot, sq, face_svg, wl, wr, al, ar, cl, cr, fl, fr, -40, 30)
    else:
        # вернулся: правая ручка машет над головой, левая — на поясе (кулачок)
        wv = math.sin(e_trip * 2 * math.pi / 0.42)
        up = ease_out(clamp(e_trip / 0.2))
        wr = (SR[0] + 120 + 40 * wv, SR[1] - 250 * up)
        ar = -70 + 30 * wv
        wl = (SL[0] - 100, SL[1] + 40)
        al = 60
        face_svg = b32.face(1.0, (-0.45, -0.1), "smile", t, brow=1.1, blink=blink)
        art, pose = body(t, x, y, SC, rot, sq, face_svg, wl, wr, al, ar, 0.6, 0.0, fl, fr, 30, 30, hat=True, cam_sw=math.sin(e_trip * 6) * math.exp(-e_trip * 2))
    out = []
    if after:
        out.append(suitcase(700))
    out.append(sb.shadow(pose.x, FLOOR + 4, 170, .5))
    out.append(art)
    # облачко-экран: на «съездил» сжимается в пуф
    k = 1.0
    k *= back_out(clamp((t - 9.62) / 0.25), 2) if t < 9.9 else 1.0
    if t > TRIP - 0.14:
        k *= 1 - ease_in(clamp((t - (TRIP - 0.14)) / 0.12))
    out.insert(0, screen_cloud(t, k))
    out.append(confetti(t) if t < TRIP + 0.2 else "")
    out.append(poof(t, BX - 30, 760))
    out.append(stars_burst(t, BX - 20, 720, TRIP + 0.12, 10, 260, 520))
    u = clamp((t - 9.65) / 3.4)
    cx, cy = 535 + 15 * u, 720 - 10 * ease_io(u)
    scl = 1.22 + 0.06 * (0.35 * u + 0.65 * ease_io(u))
    if t > TRIP:
        scl *= 1 + 0.05 * math.exp(-e_trip * 6) * math.sin(min(e_trip * 14, math.pi))
        cy += 8 * math.exp(-e_trip * 8) * math.sin(e_trip * 40)
    if t > JOY:
        e = t - JOY
        scl *= 1 + 0.02 * math.exp(-e * 7) * math.sin(min(e * 14, math.pi))
    return "".join(out), cam(cx, cy, scl, 0.5 * math.sin(t * 1.1))


def sparkle_eyes(t):
    """Звёздочки-блики в глазах (восторг)."""
    s = []
    for k, (ex, ey) in enumerate((b32.EYE_L, b32.EYE_R)):
        px, py = ex - 0.75 * 10 + 7, ey - 0.55 * 12 - 6
        r = 6 + 1.5 * math.sin(t * 9 + k)
        pts = []
        for i in range(8):
            rad = r if i % 2 == 0 else r * .35
            pts.append((px + rad * math.cos(i * math.pi / 4), py + rad * math.sin(i * math.pi / 4)))
        s.append(blob(pts, "#ffffff"))
    return "".join(s)


def s07(t):
    # 0 — стоит довольный; сникает с «сил»; с «остаётся» пятится на чемодан и садится
    tired = smooth(SIL + 0.05, SIL + 0.6, t)
    mv = smooth(REST, REST + 0.32, t)
    sit_t = REST + 0.32
    br = math.sin(t * 2 * math.pi / (1.3 + 0.6 * tired))
    seat_x = SUIT[0] - 10
    x = BX + (seat_x - BX) * mv
    hop = 34 * math.sin(math.pi * mv)
    sit_y = SUIT[1] - SHT - 132 * SC
    stand_y = 790 + 22 * tired
    y = stand_y + (sit_y - stand_y) * mv - hop + 4 * br
    sq = 1 + 0.02 * br - 0.05 * tired
    if t > sit_t:
        e = t - sit_t
        sq -= 0.14 * math.exp(-e * 8) * math.cos(e * 24)
    rot = (-2 + 2 * math.sin(t * 1.6)) * (1 - tired) + 6 * tired - 4 * mv
    if t > REST + 0.6:          # засыпает: голова клонится
        rot += 6 * smooth(REST + 0.6, REST + 0.95, t)
    pose = sb.Pose(x, y, SC, rot, sq)
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    hl, hr = pose.pt(*b32.HIP_L), pose.pt(*b32.HIP_R)
    if mv < 1:
        fl = (hl[0] - 14 + 0 * mv, G - 50 * math.sin(math.pi * clamp(mv * 2)))
        fr = (hr[0] + 10, G - 50 * math.sin(math.pi * clamp(mv * 2 - 1)))
    else:
        sw = 8 * math.sin(t * 2.5) * (1 - smooth(REST + 0.8, REST + 1.0, t))
        fl = (hl[0] - 120 + sw, G - 4)
        fr = (hr[0] - 70 - sw, G - 4)
    # ручки: сперва машет (как в конце s06), потом опускаются
    e0 = t - TRIP
    wv = math.sin(e0 * 2 * math.pi / 0.42)
    up = 1 - smooth(12.95, SIL + 0.3, t)
    wr_up = (SR[0] + 120 + 40 * wv, SR[1] - 250)
    wr_dn = (SR[0] + 60, SR[1] + 90 + 10 * tired)
    wr = (wr_dn[0] + (wr_up[0] - wr_dn[0]) * up, wr_dn[1] + (wr_up[1] - wr_dn[1]) * up)
    ar = (-70 + 30 * wv) * up + 100 * (1 - up)
    wl = (SL[0] - 100 + 30 * tired, SL[1] + 40 + 50 * tired)
    al = 60 + 40 * tired
    if mv >= 1:          # сидя: ручки лежат на чемодане
        wl = (pose.x - 230, pose.y + 110)
        wr = (pose.x - 150, pose.y + 128)
        al, ar = 25, 170
    # лицо
    yawn = smooth(REST + 0.35, REST + 0.45, t) * (1 - smooth(REST + 0.7, REST + 0.8, t))
    asleep = t > REST + 0.78
    if asleep:
        face_svg = b32.face(0.0, (0, 0), "snore", t)
    else:
        lid = 0.0
        if tired > 0:
            lid = 0.45 * tired + 0.4 * yawn
        bt = (t - 12.6) % 1.1
        if 0.9 < bt < 1.0 and tired < 0.3:
            lid = math.sin(math.pi * (bt - 0.9) / 0.1)
        mouth = "smile" if tired < 0.4 else ("o" if yawn > 0.3 else "snore")
        face_svg = b32.face(1.0, (-0.45, -0.1 + 0.6 * tired), mouth, t, brow=1.1 * (1 - tired), blink=lid)
        if yawn > 0.3:
            face_svg += yawn_mouth(yawn)
    art, pose = body(t, x, y, SC, rot, sq, face_svg, wl, wr, al, ar, 0.6, 0.0 if up > 0.5 else 0.5, fl, fr, 30, 30, hat=True,
                     cam_sw=0.3 * math.sin(t * 3))
    out = [suitcase(700, 0.05 * math.exp(-max(t - sit_t, 0) * 8) * (t > sit_t)), sb.shadow(pose.x, FLOOR + 4, 170 * (1 - 0.3 * mv), .5 * (1 - mv)), art]
    if asleep:
        out.append(b32.zzz(t - REST - 0.78 + 10.5 - 0.3, pose.x + 130, pose.y - 290))
    out.append(battery(t))
    # капля пота / усталость: стрелка вниз-пар
    if tired > 0.3 and not asleep:
        out.append(sb.sweat(*pose.pt(BCX + 120, BCY - 120), 1.1, 1.0))
    u = clamp((t - 12.65) / 2.2)
    scl = 1.3 - 0.12 * (0.35 * u + 0.65 * ease_io(u))
    cx, cy = 600 + 80 * ease_io(u), 720 + 30 * ease_io(u)
    if t > SIL:
        e = t - SIL
        scl *= 1 + 0.02 * math.exp(-e * 7) * math.sin(min(e * 14, math.pi))
    return "".join(out), cam(cx, cy, scl, -0.4 + 0.6 * u)


def yawn_mouth(k):
    mx, my = BCX - 72, BCY + 78
    r = 16 + 14 * k
    return shape(ellipse_pts(mx, my, r * .8, r, 14), "#7a2a40", blob(ellipse_pts(mx, my + r * .5, r * .5, r * .35, 10), "#e2543f"), w=3.6, seed=896)


def build_static():
    if _ST:
        return
    _ST["bg"] = sb.background()
    _ST["brain"] = brain_art.brain(0, 0, stem=False)
    sb._ST["brain"] = _ST["brain"]
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s06": s06, "s07": s07}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{_ST["bg"]}{sb.dust(t)}{art}</g>')
