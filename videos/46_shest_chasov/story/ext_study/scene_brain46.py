"""Группа C рилса 46, сцена brain: s06 «привыкает» (9.9–12.3), s07 «хуже» (12.3–15.1).
Мозг рилсов 24–32 (brain_art, ручки scene_brain, ножки и лицо scene_brain32) на ночном фоне.
s06: над мозгом тревожная красная лампа «усталость» мигает и светит; на «привыкает» (10.36) мозг надевает на неё
     колпачок-гасилку, свет гаснет, лампа серая, мозг довольно улыбается.
s07: мозг шагает на месте (дорожка едет); слева шкала усталости пуста, справа шкала работы полная; на «хуже» (13.84)
     шкала работы сползает вниз, мозг цепляет камень на дорожке, спотыкается, взмахивает руками и шагает дальше.
Всё — функция общего времени ролика t."""
import math

import brain_art
import lib
import scene_brain as sb
import scene_brain32 as s32
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, svg)

_ST = {}
FLOOR = sb.FLOOR
CAP_T = 10.36     # «привыкает»
WORSE = 13.84     # «хуже»
STUMBLE = 14.42   # нога на камне
LAMP = (540, 560)


def text(x, y, s, size, fill="#ffffff", rot=0.0, sc=1.0, stroke=INK, sw=9):
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">'
            f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="{size}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" paint-order="stroke" stroke-linejoin="round">{s}</text></g>')


def star(x, y, k, col="#ffe27a", rot=0.0):
    pts = []
    for i in range(8):
        rr = (22 if i % 2 == 0 else 7) * k
        a = i * math.pi / 4 + math.radians(rot)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    return blob(pts, col, .97)


def build_static():
    if _ST:
        return
    _ST["bg"] = sb.background()
    _ST["brain"] = brain_art.brain(0, 0, stem=False)
    lib.static_done()


# ───────────────────────── общий актёр: мозг на ножках
def actor(t, pose, feet, wl, wr, al, ar, cl, cr, fa, sd=0, bl=-30, br=30):
    """feet: ((x,y) лев., (x,y) прав.) щиколотки; fa: параметры лица face()."""
    hl, hr = pose.pt(*s32.HIP_L), pose.pt(*s32.HIP_R)
    sc = pose.sc
    legs = s32.leg(hr, feet[1], sc, -1, sd + 20) + s32.leg(hl, feet[0], sc, -1, sd + 40)
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    arms = sb.arm(SL, wl, bl, sd + 61, sc) + sb.arm(SR, wr, br, sd + 62, sc)
    brain = _ST["brain"] + s32.face(fa.get("awake", 1.0), fa.get("look", (0, 0)), fa.get("mouth", "smile"), t,
                                     brow=fa.get("brow", 0.5), blink=fa.get("blink", 0.0))
    hands = sb.toon_hand(wl[0], wl[1], al, cl, sd + 70, sc * 1.3) + sb.toon_hand(wr[0], wr[1], ar, cr, sd + 90, sc * 1.3)
    return legs, arms, f'<g transform="{pose.tf()}">{brain}</g>', hands, SL, SR


# ───────────────────────── красная лампа «усталость»
def beacon(x, y, glow, t, sc=1.0, capk=None):
    """Тревожная лампа: подставка, купол (красный → серый), блик. glow 1 — горит и светит, 0 — серая.
    capk — None без колпачка, иначе (dx, dy, rot, sc) колпачка-конуса, который надет/летит."""
    s = []
    flick = 0.78 + 0.22 * math.sin(t * 17) if glow > 0.05 else 1.0
    g = glow * flick
    if g > 0.03:
        gid = rad_grad([(0, "#ff7a6a", .85 * g), (.5, "#ff3b3b", .3 * g), (1, "#ff3b3b", 0)], x, y - 10, 300 * sc, 300 * sc)
        s.append(f'<circle cx="{f(x)}" cy="{f(y - 10)}" r="{f(300 * sc)}" fill="url(#{gid})"/>')
        # лучи тревоги
        for k in range(9):
            a = -math.pi * (0.06 + 0.88 * k / 8) + 0.05 * math.sin(t * 9 + k)
            L = (46 + 26 * math.sin(t * 14 + k * 1.7)) * g
            r0 = 118 * sc
            s.append(line([(x + math.cos(a) * r0, y - 20 + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y - 20 + math.sin(a) * (r0 + L))],
                          9, "#ffd0c8", taper=.5, seed=2000 + k))
    s.append(line([(x, y - 900), (x, y - 80 * sc)], 6, '#0e1330', taper=.05, wmin=.9, seed=2005))
    base = [(x - 92 * sc, y + 62 * sc, 1), (x + 92 * sc, y + 62 * sc, 1), (x + 80 * sc, y + 10 * sc, 1), (x - 80 * sc, y + 10 * sc, 1)]
    s.append(shape(base, "#8b93a8", blob([(x + 20 * sc, y + 10 * sc), (x + 80 * sc, y + 10 * sc), (x + 92 * sc, y + 62 * sc), (x + 30 * sc, y + 62 * sc)],
                                       "#656d84", .85) + line([(x - 70 * sc, y + 34 * sc), (x + 70 * sc, y + 34 * sc)], 3, "#656d84", seed=2010),
                   w=4.2 * sc, seed=2011))
    dome = []
    for k in range(21):
        a = math.pi * (1 - k / 20)
        dome.append((x + math.cos(a) * 82 * sc, y + 12 * sc - math.sin(a) * 94 * sc))
    dome.append((x - 82 * sc, y + 12 * sc, 1))
    red, redsh = mix("#8a8f9e", "#ff3d3d", glow), mix("#6a6f7e", "#c91f2e", glow)
    inner = blob([(x + 10 * sc, y - 90 * sc), (x + 82 * sc, y + 12 * sc), (x + 20 * sc, y + 12 * sc)], redsh, .8)
    inner += blob(ellipse_pts(x - 32 * sc, y - 46 * sc, 14 * sc, 26 * sc, 10, rot=25), "#ffffff", .35 + .5 * glow)
    s.append(shape(dome, red, inner, w=4.6 * sc, seed=2012))
    if capk is not None:
        dx, dy, rt, cs = capk
        cone = [(-70, 0, 1), (70, 0, 1), (52, -60), (22, -130), (0, -150), (-22, -130), (-52, -60)]
        cin = blob([(10, -150), (22, -130), (52, -60), (70, 0), (24, 0)], "#3e4660", .85) + blob(ellipse_pts(-30, -70, 8, 24, 8, rot=18), "#9aa6c8", .6)
        rim = shape([(-78, 2, 1), (78, 2, 1), (78, 22, 1), (-78, 22, 1)], "#4d567a", blob([(20, 2), (78, 2), (78, 22), (20, 22)], "#3a4160", .8), w=4, seed=2021)
        s.append(f'<g transform="translate({f(x + dx)} {f(y + 8 * sc + dy)}) rotate({f(rt)}) scale({f(cs * sc)})">'
                 f'{shape(cone, "#6a7596", cin, w=4.4, seed=2020)}{rim}</g>')
    return "".join(s)


def hang_tag(x, y, t, e):
    """Бирка «УСТАЛОСТЬ» на лампе: вылетает с перелётом в начале клипа."""
    k = back_out(clamp(e / 0.28), 2.4)
    if k < 0.02:
        return ""
    w = 340
    pts = rect_pts(-w / 2, -42, w / 2, 42, 14)
    sw = 4 * math.sin(t * 2.2)
    body = shape(pts, "#fff4d6", blob([(30, -42), (w / 2, -42), (w / 2, 42), (-10, 42)], "#ecd9a8", .8), w=4.2, seed=2040)
    body += text(0, 20, "УСТАЛОСТЬ", 50, "#d92d2d", sc=1, sw=0, stroke="none")
    string = line([(0, -42), (0, -86)], 5, INK, taper=.1, wmin=.8, seed=2041)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(sw)}) scale({f(k)})">{string}{body}</g>'


def s06(t):
    cap_in = clamp((t - 10.12) / (CAP_T - 10.12))
    covered = t >= CAP_T
    since = t - CAP_T
    glow = 1.0 if not covered else 1.0 - ease_out(clamp(since / 0.55), 2)
    # мозг
    breath = math.sin(t * 5.2)
    pose = sb.Pose(540, 905 - 6 * abs(breath) * (1 if not covered else .6), 1.0, -2 + 2.5 * math.sin(t * 2.3), 1 + 0.02 * breath)
    gr = FLOOR - 26
    sway = math.sin(t * 2.0)
    hl, hr = pose.pt(*s32.HIP_L), pose.pt(*s32.HIP_R)
    feet = ((hl[0] - 26 + 4 * sway, gr), (hr[0] + 18, gr))
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    # левая рука свисает и вяло качается; правая держит колпачок и надевает на лампу
    wl = (SL[0] - 70 + 14 * math.sin(t * 2.2), SL[1] + 150 + 8 * math.sin(t * 3))
    hold = (pose.x + 250, pose.y - 150)            # колпачок в руке, виден заранее
    onlamp = (LAMP[0] + 6, LAMP[1] - 70)
    if t < 10.12:
        u = clamp((t - 9.7) / 0.42)
        wr = (hold[0] + 12 * math.sin(t * 7), hold[1] + 14 * math.cos(t * 6) - 24 * math.sin(math.pi * u))   # потряхивает колпачком
    elif t < CAP_T:
        u = ease_io(cap_in)
        arc = -90 * math.sin(math.pi * u)
        wr = (hold[0] + (onlamp[0] + 60 - hold[0]) * u, hold[1] + (onlamp[1] + 40 - hold[1]) * u + arc)
    else:
        u = smooth(CAP_T + 0.05, CAP_T + 0.5, t)
        a = (onlamp[0] + 60, onlamp[1] + 40)
        rest = (SR[0] + 100, SR[1] + 110 + 8 * math.sin(t * 2.4))
        wr = (a[0] + (rest[0] - a[0]) * u, a[1] + (rest[1] - a[1]) * u)
    face_mouth = "o" if not covered else "smile"
    blink = 0.42 + 0.05 * math.sin(t * 3) if not covered else 0.0
    if covered:
        bt = (t - 11.0) % 1.7
        if bt < 0.12:
            blink = math.sin(math.pi * bt / 0.12)
    brow = 0.0 if not covered else 0.6
    look = (0.3 - 0.0, -0.9) if not covered else (-0.2 + 0.2 * math.sin(t), 0.1)
    if covered and since < 0.6:
        look = (0.3, -0.9 * (1 - smooth(0, 0.5, since)))
    legs, arms, brainsvg, hands, _, _ = actor(t, pose, feet, wl, wr, 160 - 20 * math.sin(t * 2.2), -20 if t < CAP_T else 10 - 90 * smooth(CAP_T + 0.05, CAP_T + 0.5, t),
                                              0.3, 0.55 if t < CAP_T + 0.12 else 0.1,
                                              dict(awake=1.0, look=look, mouth=face_mouth, brow=brow, blink=blink), sd=3000)
    # колпачок: в руке, потом на лампе (отскок)
    capk = None
    if t < CAP_T:
        if t < 10.12:
            capk = (wr[0] - LAMP[0] + 2, wr[1] - LAMP[1] - 4, 12 - 10 * (t - 9.7), 0.32)
        else:
            capk = ((wr[0] - LAMP[0] - 8) * (1 - cap_in), (wr[1] - LAMP[1] - 14) * (1 - cap_in) - 70 * cap_in, 12 * (1 - cap_in), 0.32 + 0.18 * ease_in(cap_in, 2))
    else:
        bounce = 14 * math.exp(-since * 11) * math.sin(since * 30)
        capk = (0, -70 - bounce, 3 * math.exp(-since * 9) * math.sin(since * 24), 0.5)
    # лампа дышит и дрожит от гудения, пока горит; после колпачка тихо покачивается
    lamp_y = LAMP[1] + (2 * math.sin(t * 30) if glow > .6 else 0)
    art = [sb.shadow(pose.x, FLOOR + 4, 190, .55), legs, arms, brainsvg, hands]
    lamp = beacon(LAMP[0], lamp_y, glow, t, 1.0, capk)
    tag = hang_tag(LAMP[0] - 262, LAMP[1] - 190, t, t - 9.74) if True else ""
    if covered and since > 0.2:
        # бирка гаснет вместе с лампой: уезжает вверх и в точку
        kk = ease_in(clamp((since - 0.2) / 0.4))
        tag = f'<g transform="translate({f(LAMP[0] - 262)} {f(LAMP[1] - 190)}) scale({f(1 - kk)})">{hang_tag(0, 0, t, 5)}</g>' if kk < 1 else ""
    fx = []
    if 0 <= since < 0.5:      # пуф при надевании
        for k in range(8):
            a = k * math.pi / 4 + .3
            r0 = 120 + 80 * ease_out(since / .5)
            L = 30 * (1 - since / .5)
            fx.append(line([(LAMP[0] + math.cos(a) * r0, LAMP[1] - 20 + math.sin(a) * r0), (LAMP[0] + math.cos(a) * (r0 + L), LAMP[1] - 20 + math.sin(a) * (r0 + L))],
                           8, "#cfd8ff", taper=.5, seed=2100 + k))
    if covered and since > 0.4:   # спокойные нотки и «ааа» — тихие звёздочки покоя
        for k in range(3):
            ph = ((since - .4) * .7 + k / 3) % 1
            fx.append(star(pose.x - 230 + 230 * k + 20 * math.sin(ph * 6), pose.y - 330 - 140 * ph, math.sin(math.pi * ph) * 0.9, "#cfe0ff", ph * 90))
    # камера: влёт на мозг сразу с кадра 0, толчок на надевании
    u = clamp((t - 9.7) / 2.8)
    scl = 1.0 + 0.2 * ease_out(u, 2)
    cy = 790 + 40 * u
    if t > CAP_T:
        scl *= 1 + 0.045 * math.exp(-since * 6) * math.sin(min(since * 14, math.pi))
    return "".join(art) + lamp + tag + "".join(fx), cam(540 + 10 * math.sin(t * .8), cy, scl, -1.2 + 1.6 * u)


# ───────────────────────── s07: шкалы, шагает, спотыкается
def gauge(x, top, bot, fill_k, col, colsh, label, t, sd, shake=0.0, icon=None):
    """Вертикальная шкала-градусник: трубка с рисками, уровень fill_k (0..1), подпись над ней."""
    wd = 120
    s = []
    pts = rect_pts(x - wd / 2, top, x + wd / 2, bot, 46)
    inner = ""
    h = bot - top
    lv = bot - h * fill_k
    if fill_k > 0.01:
        inner += blob(rect_pts(x - wd / 2 - 4, lv, x + wd / 2 + 4, bot + 4), col)
        inner += blob([(x + 14, lv), (x + wd / 2 + 4, lv), (x + wd / 2 + 4, bot + 4), (x + 14, bot + 4)], colsh, .85)
        inner += line([(x - wd / 2 + 4, lv), (x + wd / 2 - 4, lv)], 5, "#ffffff", taper=.1, wmin=.8, seed=sd + 5, op=.7)
    inner += blob(rect_pts(x - wd / 2 + 14, top + 30, x - wd / 2 + 28, bot - 40), "#ffffff", .5)
    for k in range(1, 6):
        yy = top + h * k / 6
        inner += line([(x + wd / 2 - 40, yy), (x + wd / 2 - 4, yy)], 3.4, INK, taper=.1, wmin=.8, seed=sd + 10 + k, op=.7)
    s.append(shape(pts, "#f3f1ea", inner, w=5.2, seed=sd))
    s.append(text(x, top - 34, label, 46, "#ffffff", sw=9))
    return f'<g transform="translate({f(shake)} 0)">{"".join(s)}</g>'


def rock(x, g, sc=1.0):
    pts = [(x - 62 * sc, g), (x - 52 * sc, g - 34 * sc), (x - 20 * sc, g - 52 * sc), (x + 24 * sc, g - 48 * sc), (x + 56 * sc, g - 26 * sc), (x + 64 * sc, g, 1)]
    inner = blob([(x + 6 * sc, g - 50 * sc), (x + 56 * sc, g - 26 * sc), (x + 64 * sc, g), (x + 10 * sc, g)], "#7c8296", .85)
    inner += line([(x - 36 * sc, g - 30 * sc), (x - 14 * sc, g - 40 * sc)], 3.4, "#d5daea", seed=2210, op=.7)
    return shape(pts, "#a4abc0", inner, w=4.4, seed=2211)


def s07(t):
    T0 = 12.0
    per = 0.56
    # шаг: фаза растёт, перед камнем скорость падает; на спотыкании рывок
    u = 2 * math.pi * (t - T0) / per
    e = t - STUMBLE
    stum = 0.0
    if e > 0:
        stum = math.exp(-e * 3.2) * (0.5 + 0.5 * math.cos(e * 0)) if e < 1.1 else 0.0
    kick = ease_out(clamp(e / 0.22), 2) * (1 - smooth(0.35, 0.95, e)) if e > 0 else 0.0     # наклон вперёд
    flail = ease_out(clamp(e / 0.15)) * (1 - smooth(0.4, 0.9, e)) if e > 0 else 0.0
    # осадка после WORSE: шаг вяловатее
    tired = smooth(WORSE, WORSE + 0.4, t) * 0.25
    bob = -7 * math.cos(2 * u) * (1 - tired)
    x = 560 - 24 * kick
    y = 860 + bob + 18 * kick
    rot = -3 + 2 * math.sin(u) - 16 * kick + 4 * tired
    sq = 1 + 0.025 * math.cos(2 * u) - 0.1 * kick
    pose = sb.Pose(x, y, 1.0, rot, sq)
    hl, hr = pose.pt(*s32.HIP_L), pose.pt(*s32.HIP_R)
    A, LIFT = 46, 62 - 18 * tired
    g = FLOOR - 26

    def foot(hx, uu):
        uu = uu % (2 * math.pi)
        return (hx - A * math.cos(uu), g - LIFT * max(0.0, -math.sin(uu)))
    fl, fr = foot(hl[0], u), foot(hr[0], u + math.pi)
    if e > 0:         # носок цепляется за камень, другая нога вскидывается вперёд-вниз, потом обе на пол
        hook = 1 - smooth(0.0, 0.3, e)
        fl = (fl[0] + (hl[0] - 120 - fl[0]) * 0.0, fl[1])
        fr = (hr[0] - 70 * ease_out(clamp(e / .2)) * (1 - smooth(.4, .8, e)) + (fr[0] - hr[0]) * smooth(.4, .8, e), g - 70 * math.sin(math.pi * clamp(e / .5)) * hook)
    legs_feet = (fl, fr)
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    wl = (SL[0] - 120 + 55 * math.cos(u), SL[1] + 34 - 26 * math.cos(u))
    wr = (SR[0] + 120 + 55 * math.cos(u), SR[1] + 30 + 26 * math.cos(u))
    up_l = (pose.x - 250, pose.y - 280 + 16 * math.sin(t * 30))
    up_r = (pose.x + 260, pose.y - 250 + 16 * math.sin(t * 30 + 1))
    wl = (wl[0] + (up_l[0] - wl[0]) * flail, wl[1] + (up_l[1] - wl[1]) * flail)
    wr = (wr[0] + (up_r[0] - wr[0]) * flail, wr[1] + (up_r[1] - wr[1]) * flail)
    al = 160 - 25 * math.cos(u) + (-120 - 160 + 25 * math.cos(u)) * flail
    ar = 20 - 25 * math.cos(u) + (-60 - 20 + 25 * math.cos(u)) * flail
    cl = cr = 0.55 * (1 - flail)
    if t < WORSE:
        mouth, brow = "smile", 0.9
    elif e < 0:
        mouth, brow = "smile", 0.9 - 0.3 * smooth(WORSE, WORSE + .5, t)
    elif e < 0.7:
        mouth, brow = "o", 1.2
    else:
        mouth, brow = "smile", 0.3
    bt = (t - 12.0) % 1.9
    blink = math.sin(math.pi * (bt - 1.2) / 0.12) if 1.2 < bt < 1.32 else 0.0
    look = (-0.5, 0.2 if e < 0 else 0.9 - 0.9 * smooth(0.3, .8, e))
    if e < 0 and t > WORSE:       # косится на упавшую шкалу, не понимая
        look = (0.6, -0.5)
    legs, arms, brainsvg, hands, _, _ = actor(t, pose, legs_feet, wl, wr, al, ar, cl, cr,
                                              dict(awake=1.0, look=look, mouth=mouth, brow=brow, blink=blink), sd=3300)
    # камень едет с дорожкой вправо и встречает ногу
    rx = 470 + 230 * (t - STUMBLE)
    stone = rock(rx, FLOOR - 16, 1.0)
    # шкалы
    sh_n = 0.0
    work = 1.0 - 0.8 * ease_in(clamp((t - WORSE) / 0.5), 2) if t >= WORSE else 1.0
    if t >= WORSE:
        ee = t - WORSE
        work = 0.97 - 0.77 * (1 - math.exp(-ee * 3.4)) + 0.04 * math.exp(-ee * 6) * math.sin(ee * 30)
        sh_n = 8 * math.exp(-ee * 5) * math.sin(ee * 55)
    else:
        work = 0.97 + 0.012 * math.sin(t * 6)
    GT, GB = 290, 840
    fat = gauge(235, GT, GB, 0.0, "#ff5a4a", "#c93a2e", "УСТАЛОСТЬ", t, 2300, 3 * math.sin(t * 3) * 0)
    # пустая шкала «моргает» красной чёрточкой на нуле: видно, что стрелка есть, но ничего не показывает
    fat += line([(185, GB - 22 + 3 * math.sin(t * 7)), (285, GB - 22 + 3 * math.sin(t * 7))], 5, "#ff5a4a", taper=.1, wmin=.8, seed=2330, op=.55 + .3 * math.sin(t * 5))
    wk = gauge(845, GT, GB, work, "#4cc46f", "#2f9a52", "РАБОТА", t, 2400, sh_n)
    fx = []
    if t >= WORSE:       # красная стрелка вниз рядом со шкалой
        ee = t - WORSE
        k = back_out(clamp(ee / .25), 2.2)
        ay = 380 + 140 * ease_out(clamp(ee / .6))
        arrow = [(0, 120), (-46, 56), (-18, 56), (-18, -70), (18, -70), (18, 56), (46, 56)]
        fx.append(f'<g transform="translate(715 {f(ay + 120)}) scale({f(k)})">{shape(arrow, "#ff5a4a", "", w=4.4, seed=2350)}</g>')
        if ee < 0.4:
            for j in range(6):
                a = math.pi * (0.1 + 0.8 * j / 5)
                r0 = 110 + 90 * ease_out(ee / .4)
                fx.append(line([(845 + math.cos(a) * r0, 560 - math.sin(a) * r0 * .8 + 130), (845 + math.cos(a) * (r0 + 26 * (1 - ee / .4)), 560 - math.sin(a) * (r0 + 26 * (1 - ee / .4)) * .8 + 130)],
                               8, "#bff0cc", taper=.5, seed=2360 + j))
    if 0 <= e < 0.6:    # искры и звёздочки на спотыкании
        for j in range(6):
            a = -math.pi * (0.1 + 0.8 * j / 5)
            r0 = 60 + 150 * ease_out(e / .5)
            fx.append(star(pose.x - 40 + math.cos(a) * r0, pose.y - 30 + math.sin(a) * r0, (1 - e / .6), "#ffe27a", j * 20 + e * 200))
    if 0 <= e < 0.3:
        for j in range(5):
            a = math.pi * (0.62 + 0.28 * j / 4)
            fx.append(line([(rx - 30, FLOOR - 40), (rx - 30 + math.cos(a) * 90 * ease_out(e / .3), FLOOR - 40 - math.sin(a) * 90 * ease_out(e / .3))], 7, "#e9eeff", taper=.5, seed=2380 + j))
    art = [s32.moving_room(t), sb.shadow(pose.x, FLOOR + 4, 170, .55), stone, legs, arms, brainsvg, hands, fat, wk] + fx
    uu = clamp((t - 12.1) / 3.0)
    push = 0.035 * math.exp(-max(t - WORSE, 0) * 6) * (t > WORSE) + 0.05 * math.exp(-max(e, 0) * 5) * (e > 0)
    return "".join(art), cam(540 + 14 * math.sin(t * .6), 780 + 30 * uu, 1.02 + 0.07 * uu + push, -0.8 + 1.2 * uu + (2.2 * math.sin(e * 25) * math.exp(-e * 6) if e > 0 else 0))


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s06": s06, "s07": s07}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{_ST["bg"]}{sb.dust(t)}{art}</g>')
