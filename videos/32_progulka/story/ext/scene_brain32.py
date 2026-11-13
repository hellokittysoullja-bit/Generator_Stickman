"""Сцена brain рилса 32 (s07, s08): мозг рилсов 24–28 (brain_art, ручки scene_brain) — здесь без ствола, с ножками
в кедах и лицом (большие белые глаза с маленькими зрачками), в той же ночной комнате на тёмно-синем фоне.
s07 «Когда ты двигаешься» (10.96–12.24): мозг дремлет в кресле (глаза закрыты, дышит, плывут «Z», ножки болтаются);
     перед «двигаешься» глаза распахиваются, на «двигаешься» (11.6) он выпрыгивает из кресла (подушка подбрасывает),
     приземляется перед креслом и делает первый шаг.
s08 «мысли тоже начинают бегать свободнее» (12.24–14.56): мозг бодро шагает на месте, пол и стена едут назад
     (дорожка); вокруг бегают кругами шесть лампочек-мыслей на ножках и загораются по одной: «мысли» (12.32), «тоже»,
     «начинают», «бегать» (13.52), на «свободнее» (13.79) — все; мозг вскидывает руки.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import brain_art
import lib
import scene_brain as sb
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, band, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
FLOOR = sb.FLOOR          # 1160
SKIN, SKIN_SH = sb.SKIN, sb.SKIN_SH
JUMP = 11.60              # «двигаешься»
LIGHT_T = [12.32, 12.80, 13.12, 13.52, 13.79, 13.83]     # «мысли», «тоже», «начинают», «бегать», «свободнее» ×2
FREE = 13.79              # «свободнее»
HIP_L = (BCX - 62, BCY + 104)
HIP_R = (BCX + 52, BCY + 108)
LEG = 186                 # длина ножки (бедро + голень), локальные единицы мозга
EYE_L, EYE_R = (BCX - 116, BCY + 14), (BCX - 30, BCY + 6)


# ───────────────────────── ножки и кеды
def shoe(F, face, sc, sd):
    """Кед: щиколотка в F, носок в сторону face (−1 влево)."""
    up = [(-20, -6), (8, -10), (24, 2), (42, 12), (46, 26, 1), (-24, 26, 1), (-27, 10)]
    inner = blob([(-30, 17), (50, 17), (50, 30), (-30, 30)], "#ff8a3d")
    inner += blob([(-8, 4), (18, -2), (34, 10), (20, 12), (0, 10)], "#3d7fe0")
    inner += line([(4, -6), (14, 2)], 2.6, INK, seed=sd + 3)
    s = shape(up, "#f6f3ec", inner, w=3.4, seed=sd)
    return f'<g transform="translate({f(F[0])} {f(F[1])}) scale({f(face * sc)} {f(sc)})">{s}</g>'


def leg(Hp, F, sc, face=-1, sd=0):
    """Ножка от бедра Hp до щиколотки F (мир): колено гнётся вперёд (в сторону face)."""
    Hp, F = np.array(Hp, float), np.array(F, float)
    L = LEG * sc
    d = F - Hp
    dist = np.linalg.norm(d) + 1e-6
    if dist > L * 0.995:
        F = Hp + d / dist * L * 0.995
        d = F - Hp
        dist = L * 0.995
    a = L / 2
    hh = math.sqrt(max(a * a - (dist / 2) ** 2, 0))
    n = np.array([-d[1], d[0]]) / dist
    if n[0] * face < 0:
        n = -n
    K = (Hp + F) / 2 + n * hh
    pts = [tuple(Hp), tuple((Hp + K) / 2), tuple(K), tuple((K + F) / 2), tuple(F)]
    pl = band(pts, 30 * sc, 24 * sc, step=4, wmid=27 * sc, cap=True)
    sh = band([(x + 5 * sc, y) for x, y in pts], 11 * sc, 8 * sc, step=4, wmid=10 * sc, cap=False)
    return shape(pl, SKIN, blob(sh, SKIN_SH, .85), w=3.6 * sc, seed=sd) + shoe((F[0], F[1] - 4 * sc), face, sc * 1.05, sd + 5)


# ───────────────────────── лицо мозга (в локальных координатах мозга)
def face(awake, look=(0.0, 0.0), mouth="snore", t=0.0, brow=0.0, blink=0.0):
    """awake 0 — спит (дуги), 1 — глаза открыты. blink — веко опускается на открытый глаз."""
    s = []
    if awake < 0.5:
        for k, (x, y) in enumerate((EYE_L, EYE_R)):
            s.append(line([(x - 26, y + 2), (x - 10, y + 12), (x + 10, y + 12), (x + 26, y + 2)], 6.5, INK, taper=.4, wmin=.35, seed=880 + k))
            s.append(line([(x - 18, y + 14), (x - 22, y + 22)], 2.6, INK, taper=.5, seed=884 + k))
    else:
        op = clamp((awake - 0.5) / 0.08)
        ry = 36 * (0.55 + 0.45 * op)
        for k, (x, y) in enumerate((EYE_L, EYE_R)):
            e = ellipse_pts(x, y, 29, ry, 18)
            px, py = x + look[0] * 10, y + look[1] * 12
            inner = f'<circle cx="{f(px)}" cy="{f(py)}" r="9.5" fill="{INK}"/><circle cx="{f(px - 3)}" cy="{f(py - 3.5)}" r="3" fill="#ffffff"/>'
            if blink > 0.02:
                yb = y - ry - 2 + (2 * ry + 4) * blink
                inner += f'<rect x="{x - 32}" y="{y - ry - 4}" width="64" height="{f(yb - (y - ry - 4))}" fill="#f6a9bc"/>'
                inner += line([(x - 30, yb), (x, yb + 3), (x + 30, yb)], 4, INK, seed=890 + k)
            s.append(shape(e, "#ffffff", inner, w=4.4, seed=886 + k))
            if brow:
                by = y - ry - 16 - 8 * brow
                s.append(line([(x - 22, by + 4), (x, by - 4 * brow), (x + 20, by + 2)], 5.5, "#8e3358", taper=.4, wmin=.4, seed=892 + k))
    mx, my = BCX - 72, BCY + 74
    if mouth == "snore":
        r = 7 + 3 * math.sin(t * 2.6)
        s.append(shape(ellipse_pts(mx, my, r * .9, r, 12), "#7a2a40", "", w=3, seed=895))
    elif mouth == "o":
        s.append(shape(ellipse_pts(mx, my, 14, 18, 14), "#7a2a40", blob(ellipse_pts(mx, my + 8, 8, 6, 10), "#e2543f"), w=3.4, seed=895))
    else:          # улыбка с открытым ртом
        pts = [(mx - 30, my - 8, 1), (mx + 30, my - 10, 1), (mx + 20, my + 12), (mx, my + 20), (mx - 20, my + 12)]
        s.append(shape(pts, "#7a2a40", blob([(mx - 14, my + 8), (mx + 14, my + 6), (mx + 8, my + 18), (mx - 8, my + 18)], "#e2543f"), w=3.6, seed=895))
    # румянец
    s.append(blob(ellipse_pts(BCX - 160, BCY + 56, 20, 10, 10), "#f07a98", .55))
    return "".join(s)


def zzz(t, x, y):
    """Буквы «Z» сна: рождаются у макушки, растут, уплывают вверх-вправо и сжимаются в точку (не тают)."""
    s = []
    for k in range(4):
        ph = ((t - 10.5) / 1.6 + k / 4) % 1
        sc = back_out(clamp(ph / 0.25), 2) * (1 - ease_in(clamp((ph - 0.8) / 0.2), 2)) * (0.6 + 0.6 * ph)
        if sc < 0.03:
            continue
        cx = x + 140 * ph + 16 * math.sin(ph * 9 + k)
        cy = y - 260 * ph
        r = 22 * sc
        pts = [(cx - r, cy - r), (cx + r, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
        s.append(line([(p[0] + 3, p[1] + 4) for p in pts], 10 * sc + 3, "#11163a", taper=.1, wmin=.8, seed=900 + k, op=.5))
        s.append(line(pts, 9 * sc + 3, "#cfe0ff", taper=.1, wmin=.8, seed=900 + k))
    return "".join(s)


# ───────────────────────── кресло (вид спереди)
CHX = 600


def chair(t, bounce=0.0):
    """Кресло: спинка, подлокотники, подушка сиденья (bounce — подушка подкидывает), юбка, ножки."""
    x = CHX
    s = []
    C, CS, CD, CH = "#c8573e", "#a2402f", "#7e2f22", "#e27a5c"
    s.append(sb.shadow(x, FLOOR + 6, 380, .5))
    for xx in (x - 290, x + 290):
        s.append(shape(rect_pts(xx - 18, 1100, xx + 18, FLOOR - 2, 6), "#6b4a2e", blob(rect_pts(xx + 2, 1100, xx + 18, FLOOR), "#4a3020"), w=3.4, seed=1000 + xx))
    back = rect_pts(x - 300, 560, x + 300, 1020, 110)
    inner = blob(rect_pts(x + 120, 540, x + 320, 1040), CS, .8)
    inner += line([(x - 220, 640), (x - 120, 600)], 9, CH, seed=1011, op=.9)
    for k in range(3):
        bx = x - 150 + k * 150
        inner += shape(ellipse_pts(bx, 700, 8, 8, 8), CD, "", w=2.4, seed=1012 + k)
        inner += line([(bx - 30, 690), (bx, 700), (bx + 30, 690)], 2.6, CD, seed=1015 + k, op=.8)
    s.append(shape(back, C, inner, w=5.4, seed=1010))
    skirt = rect_pts(x - 330, 990, x + 330, 1108, 30)
    s.append(shape(skirt, CS, blob(rect_pts(x + 150, 990, x + 340, 1110), CD, .7) + line([(x - 320, 1084), (x + 320, 1086)], 3, CD, seed=1021, op=.8),
                   w=5, seed=1020))
    by = -14 * bounce
    seat = rect_pts(x - 250, 930 + by, x + 250, 1010 + by * .3, 34)
    s.append(shape(seat, C, blob(rect_pts(x - 250, 975 + by, x + 250, 1012), CS, .9) + line([(x - 200, 948 + by), (x + 60, 944 + by)], 6, CH, seed=1031, op=.9),
                   w=5, seed=1030))
    return "".join(s)


def armrests():
    x = CHX
    C, CS, CH = "#c8573e", "#a2402f", "#e27a5c"
    s = []
    for side, sd in ((-1, 1040), (1, 1050)):
        x0, x1 = (x - 360, x - 230) if side < 0 else (x + 230, x + 360)
        pts = rect_pts(x0, 820, x1, 1060, 56)
        inner = blob(rect_pts(x0 + (x1 - x0) * .55, 800, x1 + 10, 1070), CS, .85)
        inner += line([(x0 + 26, 860), (x0 + 30, 1000)], 6, CH, seed=sd + 1, op=.85)
        s.append(shape(pts, C, inner, w=5.2, seed=sd))
        s.append(shape(ellipse_pts((x0 + x1) / 2, 836, (x1 - x0) / 2 - 6, 24, 16), CH, blob(ellipse_pts((x0 + x1) / 2 + 18, 842, 40, 14, 10), C, .9),
                       w=4.2, seed=sd + 3))
    return "".join(s)


def room_props():
    """Торшер справа и коврик — обжитая комната."""
    s = []
    x = 1000
    s.append(sb.shadow(x, FLOOR + 4, 90, .5))
    s.append(shape(ellipse_pts(x, FLOOR - 8, 70, 16, 14), "#2b3764", "", w=4, seed=1101))
    s.append(line([(x, FLOOR - 12), (x, 470)], 12, "#2b3764", taper=.05, wmin=.95, seed=1102))
    shade = [(x - 80, 470, 1), (x + 80, 470, 1), (x + 56, 330, 1), (x - 56, 330, 1)]
    s.append(shape(shade, "#e8c47a", blob([(x + 20, 330), (x + 56, 330), (x + 80, 470), (x + 30, 470)], "#c99a52", .8), w=4.6, seed=1103))
    rug = ellipse_pts(560, FLOOR + 70, 470, 52, 30)
    s.append(shape(rug, "#4a3c7a", blob(ellipse_pts(560, FLOOR + 70, 380, 36, 26), "#5a4c8e") + blob(ellipse_pts(560, FLOOR + 70, 250, 22, 20), "#6c5ea0"),
                   w=4.2, seed=1104))
    return "".join(s)


# ───────────────────────── s07
def s07(t):
    e = t - JUMP
    breath = math.sin((t - 10.5) * 2 * math.pi / 1.6)
    wake = smooth(11.40, 11.50, t)
    # путь: сидит → (подготовка) → прыжок по дуге → приземление перед креслом → шаг
    sit = (CHX, 840)
    land = (430, 905)
    T_LAND = 11.94
    face_dir = -1
    if t < JUMP:
        pre = smooth(11.44, JUMP, t)
        x, y = sit[0], sit[1] + 5 * breath + 26 * pre
        sc = 0.95 * (1 + 0.018 * breath)
        rot = (-7 + 3 * math.sin((t - 10.5) * 1.3)) * (1 - pre) + 4 * pre
        sq = 1 - 0.12 * pre
    elif t < T_LAND:
        u = (t - JUMP) / (T_LAND - JUMP)
        x = sit[0] + (land[0] - sit[0]) * ease_io(u)
        y = sit[1] + (land[1] - sit[1]) * u - 300 * 4 * u * (1 - u)
        sc = 0.95
        rot = -14 * math.sin(math.pi * u)
        sq = 1 + 0.12 * math.sin(math.pi * min(1, u * 1.6)) - 0.04 * u
    else:
        el = t - T_LAND
        x, y = land[0] - 40 * smooth(0.12, 0.45, el), land[1]
        sc = 0.95
        sq = 1 - 0.16 * math.exp(-el * 9) * math.cos(el * 26)
        rot = -5 * smooth(0.1, 0.3, el)
    pose = sb.Pose(x, y, sc, rot, sq)
    # ножки
    hl, hr = pose.pt(*HIP_L), pose.pt(*HIP_R)
    if t < JUMP:
        sw = 10 * math.sin(t * 3.3)
        fl, fr = (hl[0] - 6 + sw, hl[1] + 160), (hr[0] + 6 - sw, hr[1] + 160)
    elif t < T_LAND:
        u = (t - JUMP) / (T_LAND - JUMP)
        tuck = math.sin(math.pi * u)
        fl = (hl[0] - 10, hl[1] + 170 - 90 * tuck)
        fr = (hr[0] + 10, hr[1] + 170 - 90 * tuck)
    else:
        el = t - T_LAND
        g = FLOOR - 26
        st = smooth(0.14, 0.42, el)          # первый шаг: левая ножка вперёд
        lift = 60 * math.sin(math.pi * st)
        fl = (hl[0] - 10 - 90 * st, g - lift)
        fr = (hr[0] + 6, g)
    legs = leg(hr, fr, sc, face_dir, 1200) + leg(hl, fl, sc, face_dir, 1220)
    # ручки: на подлокотниках → вскинуты в прыжке → машут при шаге
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    rest_l, rest_r = (CHX - 300, 836 + 3 * breath), (CHX + 300, 838 + 3 * breath)
    up_l, up_r = (pose.x - 250, pose.y - 230), (pose.x + 240, pose.y - 240)
    if t < JUMP:
        k = smooth(11.48, JUMP + 0.02, t) * 0.25
        wl = (rest_l[0] + (up_l[0] - rest_l[0]) * k, rest_l[1] + (up_l[1] - rest_l[1]) * k)
        wr = (rest_r[0] + (up_r[0] - rest_r[0]) * k, rest_r[1] + (up_r[1] - rest_r[1]) * k)
        al, ar, cl, cr = 110, 70, 0.5, 0.5
        bl, br = 30, -30
    elif t < T_LAND + 0.1:
        k = 0.25 + 0.75 * ease_out(clamp((t - JUMP) / 0.12))
        wl = (rest_l[0] + (up_l[0] - rest_l[0]) * k, rest_l[1] + (up_l[1] - rest_l[1]) * k)
        wr = (rest_r[0] + (up_r[0] - rest_r[0]) * k, rest_r[1] + (up_r[1] - rest_r[1]) * k)
        al, ar, cl, cr = -120, -60, 0.0, 0.0
        bl, br = -40, 40
    else:
        el = t - T_LAND - 0.1
        k = smooth(0, 0.2, el)
        sw = math.sin(math.pi * smooth(0.04, 0.32, el))
        dn_l = (SL[0] - 120 + 50 * sw, SL[1] + 30 - 20 * sw)
        dn_r = (SR[0] + 120 - 50 * sw, SR[1] + 26 - 20 * sw)
        wl = (up_l[0] + (dn_l[0] - up_l[0]) * k, up_l[1] + (dn_l[1] - up_l[1]) * k)
        wr = (up_r[0] + (dn_r[0] - up_r[0]) * k, up_r[1] + (dn_r[1] - up_r[1]) * k)
        al, ar = -120 + (-200 + 120) * k, -60 + (40 + 60) * k
        cl = cr = 0.6 * k
        bl, br = -40 + 10 * k, 40 - 10 * k
    arms = sb.arm(SL, wl, bl, 1301, sc) + sb.arm(SR, wr, br, 1302, sc)
    # лицо
    blink = 0.0
    look = (-0.3, -0.1) if t > JUMP else (0.2 * smooth(11.5, 11.58, t), -0.3)
    mouth = "snore" if wake < 0.5 else ("o" if t < JUMP + 0.25 else "smile")
    brain_svg = _ST["brain"] + face(wake, look, mouth, t, brow=1.0 if t > JUMP else 0.6 * wake, blink=blink)
    hands = sb.toon_hand(wl[0], wl[1], al, cl, 1330, sc * 1.3) + sb.toon_hand(wr[0], wr[1], ar, cr, 1360, sc * 1.3)
    bounce = 0.0
    if e > 0:
        bounce = math.exp(-e * 6) * math.sin(min(e * 18, math.pi * 3)) * (1 if e < 0.6 else 0)
    pre_k = smooth(11.44, JUMP, t) if t < JUMP else 0
    bounce -= 0.8 * pre_k
    art = [_ST["props"]]
    seated = t < JUMP + 0.1
    if seated:
        art += [chair(t, bounce), legs, arms, f'<g transform="{pose.tf()}">{brain_svg}</g>', armrests(), hands]
    else:
        art += [chair(t, bounce), armrests(), sb.shadow(pose.x, FLOOR + 4, 170 * (0.6 + 0.4 * clamp((pose.y - 600) / 300)), .5),
                legs, arms, f'<g transform="{pose.tf()}">{brain_svg}</g>', hands]
    if t < JUMP + 0.3:
        z = zzz(t, CHX + 150, 690)
        if t > 11.45:
            k = clamp((t - 11.45) / 0.15)
            z = f'<g transform="translate({CHX + 200} 560) scale({f(1 - ease_in(k))}) translate({-CHX - 200} -560)">{z}</g>' if k < 1 else ""
        art.append(z)
    # удар прыжка: штрихи-«пружинки» из кресла и вспышка у макушки
    if 0 <= e < 0.4:
        u = e / 0.4
        for k in range(8):
            a = -math.pi * (0.08 + 0.84 * k / 7)
            cx_, cy_ = CHX, 900
            r0 = 200 + 160 * ease_out(u)
            L = 70 * (1 - u)
            art.append(line([(cx_ + math.cos(a) * r0 * 1.3, cy_ + math.sin(a) * r0), (cx_ + math.cos(a) * (r0 + L) * 1.3, cy_ + math.sin(a) * (r0 + L))],
                            10, "#ffe27a", taper=.5, seed=1400 + k))
    # скорость при полёте
    if JUMP < t < 11.94:
        u = (t - JUMP) / 0.34
        for k in range(4):
            yy = pose.y - 80 + k * 50
            x0 = pose.x + 230
            art.append(line([(x0, yy), (x0 + 160 * (1 - u * .5), yy + 30)], 6, "#cfe0ff", taper=.6, seed=1420 + k))
    # камера: наезд на кресло с первого кадра, толчок на прыжке, ведёт за мозгом
    u = clamp((t - 10.76) / 0.84)
    cx = 600 - 140 * smooth(JUMP, 12.15, t)
    cy = 895 - 10 * u
    scl = 1.24 + 0.12 * (0.4 * u + 0.6 * ease_io(u))
    if e > 0:
        scl *= 1 + 0.05 * math.exp(-e * 6) * math.sin(min(e * 16, math.pi))
        cy += 10 * math.exp(-e * 8) * math.sin(e * 45)
    return "".join(art), cam(cx, cy, scl, -0.6 + 0.8 * clamp((t - 10.76) / 1.7))


# ───────────────────────── s08: шагает на месте, лампочки-мысли
def bulb(x, y, on, sc=1.0, sd=0, t=0.0, run=True):
    """Лампочка рилса 27 (колба, нить, цоколь) + ножки бегут. on 0..1 — накал."""
    s = []
    if on > 0.02:
        g = rad_grad([(0, "#fff3b0", .8 * on), (.45, "#ffd75a", .3 * on), (1, "#ffd75a", 0)], x, y, 140 * sc, 140 * sc)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(145 * sc)}" fill="url(#{g})"/>')
    if run:
        ph = t * 16 + sd
        for k, side in enumerate((-1, 1)):
            a = math.sin(ph + k * math.pi)
            hx, hy = x + side * 8 * sc, y + 118 * sc
            fx, fy = hx + 22 * a * sc, hy + 40 * sc - 10 * max(0, -a) * sc
            s.append(line([(hx, hy), ((hx + fx) / 2 - 4 * sc, (hy + fy) / 2), (fx, fy)], 6 * sc, INK, taper=.1, wmin=.8, seed=sd + 20 + k))
            s.append(shape(ellipse_pts(fx - 6 * sc, fy + 2 * sc, 12 * sc, 6 * sc, 10), "#2a2f44", "", w=2 * sc, seed=sd + 24 + k))
    glass = mix("#5d6a98", "#fff0a0", on)
    shc = mix("#46527e", "#f2c94c", on)
    pts = []
    for k in range(26):
        a = 2 * math.pi * k / 26
        r = 62 * sc
        px, py = math.cos(a) * r, math.sin(a) * r
        if py > 22 * sc:
            px *= 1 - 0.55 * (py - 22 * sc) / (40 * sc)
        pts.append((x + px, y + py))
    inner = blob(ellipse_pts(x + 18 * sc, y + 16 * sc, 50 * sc, 46 * sc, 14), shc, .8)
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


def lit(i, t):
    return smooth(LIGHT_T[i] - 0.02, LIGHT_T[i] + 0.08, t)


def pop_rays(x, y, e, sd, r=70):
    if e < 0 or e > 0.4:
        return ""
    u = e / 0.4
    s = []
    for k in range(8):
        a = k * math.pi / 4 + .3
        r0 = r + 70 * ease_out(u)
        L = 34 * (1 - u)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))], 7, "#ffe27a",
                      taper=.5, seed=sd + k))
    return "".join(s)


def moving_room(t):
    """Стена с рамками и пол-доски едут вправо: мозг шагает влево на месте (дорожка)."""
    v = 230.0
    off = (t - 12.0) * v
    s = []
    # рамки с пустыми картинками на стене (параллакс 0.6)
    for k in range(-2, 8):
        x = -700 + k * 420 + (off * 0.6) % 420
        y = 420 + (k % 2) * 70
        pts = rect_pts(x - 90, y - 70, x + 90, y + 70, 6)
        inner = blob(rect_pts(x - 70, y - 50, x + 70, y + 50), "#3d4f86")
        inner += blob([(x - 70, y + 50), (x - 20, y - 6), (x + 14, y + 26), (x + 40, y), (x + 70, y + 50)], "#5a7ab8")
        inner += shape(ellipse_pts(x + 36, y - 22, 12, 12, 10), "#ffe27a", "", w=2.4, seed=1500 + k % 3)
        s.append(shape(pts, "#7a5a3c", inner, w=4.2, seed=1510 + (k % 4)))
    # пол: стыки досок едут (вид чуть сверху — наклонные)
    for k in range(-3, 10):
        x = -600 + k * 170 + off % 170
        s.append(line([(x, FLOOR + 4), (x - 60, FLOOR + 240)], 3.2, "#1c2546", taper=.2, wmin=.6, seed=1530 + (k % 5), op=.85))
    # плинтус с полосками
    for k in range(-3, 14):
        x = -600 + k * 120 + (off * 1.0) % 120
        s.append(line([(x, FLOOR - 22), (x, FLOOR - 4)], 2.4, "#1c2546", taper=.1, wmin=.7, seed=1550 + (k % 5), op=.8))
    return "".join(s)


def s08(t):
    T0 = 12.0
    per = 0.56
    u = 2 * math.pi * (t - T0) / per
    hooray = smooth(FREE, FREE + 0.15, t) * (1 - smooth(14.35, 14.6, t))
    bob = -7 * math.cos(2 * u)
    sc = 1.0
    x = 540
    y = 860 + bob
    rot = -4 + 2 * math.sin(u)
    if t > FREE:
        e = t - FREE
        y -= 26 * math.exp(-e * 5) * math.sin(min(e * 12, math.pi))
    pose = sb.Pose(x, y, sc * (1 + 0.01 * math.sin(2 * u)), rot, 1 + 0.025 * math.cos(2 * u))
    hl, hr = pose.pt(*HIP_L), pose.pt(*HIP_R)
    A, LIFT = 46, 62
    g = FLOOR - 26

    def foot(hx, uu):
        uu = uu % (2 * math.pi)
        return (hx - A * math.cos(uu), g - LIFT * max(0.0, -math.sin(uu)))
    fl = foot(hl[0], u)
    fr = foot(hr[0], u + math.pi)
    legs = leg(hr, fr, sc, -1, 1600) + leg(hl, fl, sc, -1, 1620)
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    wl = (SL[0] - 120 + 55 * math.cos(u), SL[1] + 34 - 26 * math.cos(u))
    wr = (SR[0] + 120 + 55 * math.cos(u), SR[1] + 30 + 26 * math.cos(u))
    up_l = (pose.x - 260, pose.y - 250 + 14 * math.sin(t * 9))
    up_r = (pose.x + 250, pose.y - 260 + 14 * math.sin(t * 9 + 1))
    wl = (wl[0] + (up_l[0] - wl[0]) * hooray, wl[1] + (up_l[1] - wl[1]) * hooray)
    wr = (wr[0] + (up_r[0] - wr[0]) * hooray, wr[1] + (up_r[1] - wr[1]) * hooray)
    al = 160 - 25 * math.cos(u)
    ar = 20 - 25 * math.cos(u)
    al, ar = al + (-120 - al) * hooray, ar + (-60 - ar) * hooray
    cl = cr = 0.55 * (1 - hooray)
    arms = sb.arm(SL, wl, -30 - 10 * hooray, 1641, sc) + sb.arm(SR, wr, 30 + 10 * hooray, 1642, sc)
    hands = sb.toon_hand(wl[0], wl[1], al, cl, 1660, sc * 1.3) + sb.toon_hand(wr[0], wr[1], ar, cr, 1690, sc * 1.3)
    blink = 0.0
    bt = (t - 12.0) % 1.9
    if 1.2 < bt < 1.32:
        blink = math.sin(math.pi * (bt - 1.2) / 0.12)
    nlit = sum(lit(i, t) > 0.5 for i in range(6))
    brain_svg = _ST["brain"] + face(1.0, (-0.4 + 0.25 * math.sin(t * 1.7), -0.2), "smile", t, brow=0.8 + 0.4 * hooray, blink=blink)
    # лампочки по эллипсу вокруг мозга
    back, front = [], []
    cxo, cyo, rx, ry = 540, 900, 390, 200
    for i in range(6):
        a = i * math.pi / 3 + (t - 12.0) * 1.7
        depth = math.sin(a)
        bx, by = cxo + rx * math.cos(a), cyo + ry * depth - 30
        on = lit(i, t)
        e = t - LIGHT_T[i]
        pop = 0.18 * math.exp(-max(e, 0) * 7) * math.sin(min(max(e, 0) * 16, math.pi)) if e > 0 else 0.0
        bsc = (0.5 + 0.08 * depth) * (1 + pop)
        hop = -14 * abs(math.sin((t - 12) * 8 + i))
        b = bulb(bx, by + hop, on, bsc, 1700 + i * 40, t)
        b += pop_rays(bx, by + hop, e, 1960 + i * 10, 70 * bsc / 0.5)
        sh = sb.shadow(bx, by + 118 * bsc + 46 * bsc + 6, 40 * bsc / 0.5, .45)
        (front if depth > 0 else back).append(sh + b)
    art = [_ST["props8"], moving_room(t), "".join(back), sb.shadow(pose.x, FLOOR + 4, 170, .55), legs, arms,
           f'<g transform="{pose.tf()}">{brain_svg}</g>', hands, "".join(front)]
    # на «свободнее» — звёздочки радости
    if t > FREE + 0.05:
        e = t - FREE - 0.05
        for j in range(8):
            a = j * math.pi / 4 + 0.4
            r = 330 + 30 * math.sin(e * 3 + j)
            sx, sy = pose.x + math.cos(a) * r * 1.1, pose.y - 60 + math.sin(a) * r * .7
            k = back_out(clamp((e - j * 0.03) / 0.25)) * (0.8 + 0.25 * math.sin(e * 8 + j))
            if k > 0.05:
                pts = []
                for i in range(8):
                    rr = (20 if i % 2 == 0 else 6) * k
                    aa = i * math.pi / 4
                    pts.append((sx + math.cos(aa) * rr, sy + math.sin(aa) * rr))
                art.append(blob(pts, "#ffe27a", .95))
    uu = clamp((t - 12.04) / 2.72)
    push = 0.03 * math.exp(-max(t - FREE, 0) * 6) * (t > FREE)
    return "".join(art), cam(515 + 60 * uu, 878, 1.3 + 0.04 * uu + push, -0.5 + 0.9 * uu)


def props8():
    """Пол-коврик для s08 нет — комната пустая, едет только фон."""
    return ""


def build_static():
    if _ST:
        return
    _ST["bg"] = sb.background()
    _ST["brain"] = brain_art.brain(0, 0, stem=False)
    _ST["props"] = room_props()
    _ST["props8"] = props8()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s07": s07, "s08": s08}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{_ST["bg"]}{sb.dust(t)}{art}</g>')
