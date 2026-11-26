"""Рилс 121 «Дело-монстр», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Дело — фиолетовый лохматый монстр с листами
на макушке и табличкой «ДЕЛО»: сначала с тумбочку, потом с холодильник; ест вечера, сон и выходные; кот режет его
ножницами на трёх монстриков, каждого Дима побеждает за две минуты. Призыв — кодовое слово «КОТ». NOCAM=1 — без влёта,
тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, lib, people  # noqa: E402

HIT = stress(3, .3)
MON, MON_SH, MON_HI = "#8a63d2", "#6a46b0", "#a888e6"
NS_H, FR_H = 250.0, 900.0          # тумбочка и холодильник (высота в мире)


def monster(x, y, h, t, mouth=.3, look=(0.0, 0.0), mood="mean", sq=0.0, label="ДЕЛО", seed=0, arms=0.0):
    """Дело-монстр, дно по центру (x, y), высота h. mouth 0…1 — пасть; mood mean (брови, зубы) / cute (улыбка);
    sq — сжатие-растяжение (−1…1: + выше и уже); arms 0…1 — лапки вверх."""
    sc = h / 400.0
    sy, sx = 1 + .12 * sq, 1 - .1 * sq
    wob = t * 5 + seed
    o = []
    # листы на макушке — позади тела
    for j, (ax, rot) in enumerate(((-70, -25), (0, 4), (75, 28))):
        fl = 6 * math.sin(wob * 1.3 + j)
        sheet = shape(lib.rect_pts(-40, -70, 40, 40), "#fbf8f1", "".join(
            line([(-26, -46 + 18 * q), (26, -46 + 18 * q)], 2.2, "#9aa0aa", taper=0, wmin=1, seed=seed * 10 + j * 5 + q) for q in range(4)),
            w=3.2, seed=4100 + seed * 7 + j)
        o.append(tf(sheet, ax, -360, 1.0, rot + fl))
    # тело: лохматый ком
    n = 30
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + .06 * math.sin(3 * a + wob) + .05 * math.sin(7 * a - wob * 1.4) + (.05 if i % 2 else 0)
        px = 175 * r * math.sin(a)
        py = -195 - 195 * r * math.cos(a)
        py = min(py, 0)
        pts.append((px, py))
    inner = blob(ellipse_pts(70, -150, 120, 170, 18), MON_SH, .7)
    inner += blob(ellipse_pts(-10, -120, 105, 85, 18), MON_HI, .55)
    for j in range(7):
        a0 = j * .9 + 1
        inner += line([(120 * math.cos(a0) - 10, -200 + 120 * math.sin(a0)), (120 * math.cos(a0) + 4, -186 + 120 * math.sin(a0))], 2.6,
                      MON_SH, seed=4200 + j, op=.8)
    o.append(shape(pts, MON, inner, w=6, seed=4150 + seed))
    # ножки
    for s_ in (-1, 1):
        o.append(shape(ellipse_pts(s_ * 80, -6, 56, 26, 14), MON_SH, "", w=5, seed=4160 + s_))
    # лапки
    for s_ in (-1, 1):
        up = arms * (1 if s_ > 0 else .8)
        tip = (s_ * (210 + 20 * up), -170 - 120 * up + 10 * math.sin(wob * 2 + s_))
        o.append(shape(lib.band([(s_ * 150, -190), (s_ * 190, -180 - 60 * up), tip], 46, 34), MON, "", w=5, seed=4170 + s_))
        for c in (-1, 0, 1):
            o.append(line([(tip[0] + c * 12, tip[1] - 12), (tip[0] + c * 16 + s_ * 4, tip[1] - 30)], 5, "#fbf8f1", taper=.6, seed=4180 + c + s_ * 5))
    # глаза
    lx, ly = look
    for s_ in (-1, 1):
        ex, ey = s_ * 62, -285
        o.append(shape(ellipse_pts(ex, ey, 46, 52, 16), "#ffffff", "", w=5, seed=4190 + s_))
        o.append(blob(ellipse_pts(ex + 16 * lx, ey + 18 * ly, 19, 22, 12), "#16131c"))
        o.append(blob(ellipse_pts(ex + 16 * lx + 6, ey + 18 * ly - 8, 6, 6, 8), "#ffffff"))
        if mood == "mean":
            o.append(line([(s_ * 20, -330), (s_ * 105, -356)], 12, INK, taper=.2, wmin=.6, seed=4195 + s_))
        else:
            o.append(line([(s_ * 30, -352), (s_ * 62, -362), (s_ * 98, -350)], 7, INK, taper=.3, wmin=.5, seed=4195 + s_))
    # пасть
    if mood == "mean":
        mo = clamp(mouth)
        my, rx, ry = -185, 95, 16 + 70 * mo
        mp = ellipse_pts(0, my, rx, ry, 20)
        teeth = "".join(f'<path d="M{-80 + 32 * i:.1f} {my - ry - 4:.1f} l16 {30 + 10 * mo:.1f} l16 {-30 - 10 * mo:.1f} z" fill="#ffffff" stroke="#111" '
                        f'stroke-width="3"/>' for i in range(5))
        teeth += "".join(f'<path d="M{-64 + 32 * i:.1f} {my + ry + 4:.1f} l16 {-22 - 6 * mo:.1f} l16 {22 + 6 * mo:.1f} z" fill="#ffffff" '
                         f'stroke="#111" stroke-width="3"/>' for i in range(4))
        o.append(shape(mp, "#3a1530", blob(ellipse_pts(0, my + ry * .5, rx * .5, ry * .4, 12), "#c2405a", .9) + teeth, w=5, seed=4199))
    else:
        o.append(line([(-50, -200), (-20, -178), (20, -178), (50, -200)], 9, INK, taper=.3, wmin=.5, seed=4199))
        for s_ in (-1, 1):
            o.append(blob(ellipse_pts(s_ * 110, -225, 22, 13, 10), "#f08ab0", .7))
    if label:
        lw = 52 + 34 * len(label)
        o.append(shape(lib.rrect(-lw / 2, -110, lw / 2, -48, 14), "#fbf8f1", "", w=4, seed=4210))
        o.append(text(label, 0, -63, 52 if len(label) < 6 else 40, fill="#1d2448", stroke="#fbf8f1", sw=1))
    body = "".join(o)
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({sc * sx:.4f} {sc * sy:.4f})">{body}</g>'


def nightstand(x, y, k=1.0):
    """Тумбочка, дно по центру, высота 250·k."""
    o = shape(lib.rect_pts(-150, -250, 150, -20), "#b8865a", "", w=5, seed=4300)
    o += shape(lib.rect_pts(-130, -225, 130, -140), "#c99668", "", w=4, seed=4301)
    o += shape(ellipse_pts(0, -182, 16, 12, 10), "#7a5232", "", w=3, seed=4302)
    for s_ in (-1, 1):
        o += shape(lib.rect_pts(s_ * 130 - 14, -22, s_ * 130 + 14, 0), "#7a5232", "", w=3, seed=4303 + s_)
    o += PR.mug(-60, -250, 1.0)
    return tf(o, x, y, k)


def fridge(x, y, k=1.0, op=1.0, dashed=False):
    """Холодильник, дно по центру, высота 900·k. dashed — только пунктирный контур (от него ничего не осталось)."""
    if dashed:
        d = f'M-200 0 L-200 -880 Q-200 -900 -180 -900 L180 -900 Q200 -900 200 -880 L200 0 M-200 -560 L200 -560'
        return tf(f'<path d="{d}" fill="none" stroke="#6b6f7a" stroke-width="9" stroke-dasharray="34 22" stroke-linecap="round" opacity="{op:.3f}"/>', x, y, k)
    o = shape(lib.rrect(-200, -900, 200, -10, 26), "#f2f4f7", blob(lib.rect_pts(110, -900, 200, 0), "#d7dbe2", .8), w=5, seed=4310)
    o += line([(-200, -560), (200, -560)], 5, seed=4311)
    for y0, y1 in ((-820, -640), (-500, -300)):
        o += shape(lib.rrect(150, y0, 172, y1, 10), "#b9bec8", "", w=3, seed=4312 + int(y0))
    o += shape(lib.rect_pts(-160, -14, 160, 4), "#9aa0aa", "", w=3, seed=4315)
    o += PR.sticky(-80, -760, 1.0, rot=-6, seed=3)
    return f'<g opacity="{op:.3f}">{tf(o, x, y, k)}</g>'


def room(t, wall=WALL):
    o = [plain_room(t, wall=wall)]
    o.append(rug(540, RFL + 150, 600))
    return o


def frame_s01(t):
    """ХУК: монстр-дело с тумбочку рядом с тумбочкой, прыгает и растёт толчками; Дима отпрянул."""
    hop = abs(math.sin(t * 2 * math.pi / .55))
    grow = .95 + .25 * ease_out(ramp(t, 0, 1.6)) + .1 * bump(t, W(5), .06, .25)
    h = NS_H * grow
    o = room(t)
    o.append(PR.window(250, 1150, 300, 380, mode="evening", t=t, seed=4, curtain=False))
    o.append(nightstand(760, RFL))
    o.append(monster(470, RFL - 50 * hop, h, t, mouth=.4 + .4 * hop, look=(.6, .2), sq=.5 * (hop - .5)))
    for j in range(3):
        u = ((t * 1.4 + j / 3) % 1)
        o.append(tf(shape(lib.rect_pts(-30, -40, 30, 40), "#fbf8f1", "", w=3, seed=4400 + j), 470 + (j - 1) * 160 * u, RFL - h - 40 - 380 * u + 300 * u * u,
                    .9, 200 * u * (1 if j % 2 else -1)))
    dx, dy = shake(t, W(5), 10)
    return hook_view("".join(o), t, HIT, 620, 1420, 2.1, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«Через неделю оно стало с холодильник»: рывком вырастает до холодильника, Дима крохотный внизу."""
    a, b = T0("s02"), T1("s02")
    g = ease_out(ramp(t, W(9) - .1, .45))
    h = NS_H * 1.3 + (FR_H - NS_H * 1.3) * g + 30 * bump(t, W(11), .06, .3)
    o = room(t)
    o.append(fridge(840, RFL))
    o.append(nightstand(-160, RFL))
    o.append(monster(430, RFL, h, t, mouth=.3 + .6 * bump(t, W(11), .08, .5), look=(-.5, .5), sq=-.4 * bump(t, W(9), .05, .3) + .3 * bump(t, W(9) + .4, .1, .3)))
    f = stand(60, t, "panic82", "d82_shrug", head_add=-.1)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(11), 12)
    return view("".join(o), 470 + dx, 1110 + dy, 1.0 - .08 * u, 0, t=t)


def evening_card(x, y, k, rot=0.0):
    o = shape(lib.rrect(-120, -90, 120, 90, 18), "#f6a35c", blob(lib.rect_pts(-120, 20, 120, 90), "#c8553d", .9)
              + blob(ellipse_pts(0, 22, 46, 46, 16), "#ffd35a"), w=4, seed=4500)
    o += PR.moon(70, -40, 22, .4)
    return tf(o, x, y, k, rot)


def gulp_path(t, t0, t1, p0, p1):
    """Предмет летит по дуге из p0 в пасть p1 к t1, затем исчезает."""
    u = clamp((t - t0) / max(.05, t1 - t0))
    x = p0[0] + (p1[0] - p0[0]) * u
    y = p0[1] + (p1[1] - p0[1]) * u - 260 * math.sin(math.pi * u)
    return x, y, 1 - .6 * u, u


def frame_s03(t):
    """«Сначала оно съело мои вечера»: крупно морда монстра, карточки вечеров «19:00» влетают в пасть одна за другой."""
    a, b = T0("s03"), T1("s03")
    te = W(14) + .1
    o = room(t, wall="#e8d6c0")
    o.append(PR.window(880, 1150, 300, 380, mode="evening", t=t, seed=4, curtain=False))
    chomp = max(bump(t, te, .06, .2), bump(t, te + .55, .06, .2))
    mx, my, H = 430, RFL, 900.0
    o.append(monster(mx, my, H, t, mouth=.9 - .8 * chomp, look=(.6, -.2), sq=-.3 * chomp))
    mouth = (mx, my - 185 * H / 400)
    for j, t0 in enumerate((a - .1, te - .15)):
        t1 = t0 + .55 if j == 0 else te + .5
        if t < t1:
            x, y, k, u = gulp_path(t, t0, t1, (880 - 40 * j, 820 + 60 * j), mouth)
            o.append(evening_card(x, y, 1.1 * k, 20 * u))
    o.append(PR.sparkles(mouth[0], mouth[1], 1.6, chomp, t, seed=31, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, te, 10)
    return view("".join(o), 560 + dx, 1150 + dy, 1.12 + .08 * u, -1 + 2 * u, t=t)


def frame_s04(t):
    """«Потом сон»: подушка с месяцем и Z влетает в пасть, ночь."""
    a, b = T0("s04"), T1("s04")
    te = W(18)
    o = [plain_room(t, wall="#2e3150", floor="#3b3552")]
    o.append(PR.window(880, 1150, 300, 380, mode="night", t=t, seed=4, curtain=False))
    chomp = bump(t, te, .06, .25)
    mx, H = 430, 900.0
    o.append(monster(mx, RFL, H, t, mouth=.95 - .85 * chomp, look=(.7, -.4), sq=-.3 * chomp))
    mouth = (mx, RFL - 185 * H / 400)
    if t < te:
        x, y, k, u = gulp_path(t, a - .2, te, (980, 700), mouth)
        pil = PR.pillow(0, 0, 1.6) + PR.moon(40, -120, 36, .6) + PR.z_mark(-60, -150, 1.4)
        o.append(tf(pil, x, y, k, 30 * u))
    if t > te:
        for j in range(3):
            o.append(PR.z_mark(mouth[0] + 100 + 60 * j, mouth[1] - 150 - 90 * j - 120 * ramp(t, te, 1.0), 1.2, u=1 - ramp(t, te + .3 + .1 * j, .5)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, te, 10)
    return view("".join(o), 560 + dx, 1150 + dy, 1.1 + .06 * u, 0, bg="#2e3150", t=t)


def frame_s05(t):
    """«я лежал и думал, какое оно огромное»: Дима в кровати, глаза открыты; над ним облако мыслей с огромным монстром, облако растёт."""
    a, b = T0("s05"), T1("s05")
    tg = W(25)
    o = [plain_room(t, wall="#2e3150", floor="#3b3552")]
    o.append(PR.window(850, 1100, 300, 380, mode="night", t=t, seed=4, curtain=False))
    o.append(PR.bed(800, RFL, 1.3))
    o.append(people.dima_bed(710, RFL - 118 * 1.3 - 10, .62, "awake73", t=t)["svg"])
    big = 1 + .35 * ease_out(ramp(t, tg - .1, .4))
    inner = monster(0, 110, 210 * big, t, mouth=.6, look=(0, .4))
    o.append(PR.thought_cloud(560, 800, 1.25 * big, w=360, h=300, u=pop(t, a - .35, .3), seed=5, inner=inner))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tg, 10)
    return view("".join(o), 560 + dx, 1120 + dy, 1.2 + .05 * u, 0, bg="#2e3150", t=t)


def cal_leaf(label, sub, x, y, k, rot=0.0):
    o = shape(lib.rect_pts(-130, -160, 130, 160), "#fbf8f1", blob(lib.rect_pts(-130, -160, 130, -70), "#c8553d"), w=4, seed=4600 + len(label))
    o += text(label, 0, -92, 70, fill="#ffffff", stroke="#7a2a1e", sw=5)
    o += text(sub, 0, 80, 130, fill="#1d2448", stroke="#fbf8f1", sw=2)
    return tf(o, x, y, k, rot)


def frame_s06(t):
    """«А в субботу сожрало выходные целиком»: листы «СБ» и «ВС» влетают в пасть, монстр глотает их целиком и раздувается."""
    a, b = T0("s06"), T1("s06")
    t1, t2 = W(29), W(31)
    o = room(t)
    o.append(PR.calendar(860, 900, 300, 360, seed=6))
    full = ramp(t, t2, .3)
    chomp = max(bump(t, t1 + .05, .06, .2), bump(t, t2 + .05, .06, .2))
    mx, H = 430, 880.0 + 60 * full
    o.append(monster(mx, RFL, H, t, mouth=.9 - .8 * chomp, look=(.7, -.1), sq=-.35 * chomp - .15 * full))
    mouth = (mx, RFL - 185 * H / 400)
    for lab, sub, t0, te, dx_ in (("СБ", "6", a - .1, t1 + .05, 0), ("ВС", "7", t1 - .1, t2 + .05, 60)):
        if t < te:
            x, y, k, u = gulp_path(t, t0, te, (860 + dx_, 900), mouth)
            o.append(cal_leaf(lab, sub, x, y, .9 * k, -25 * u))
    o.append(PR.sparkles(mouth[0], mouth[1], 1.6, bump(t, t2 + .05, .05, .4), t, seed=61, n=6, r=220))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t2, 12)
    return view("".join(o), 580 + dx, 1150 + dy, 1.1 + .06 * u, 0, t=t)


def frame_s07(t):
    """«Тогда кот достал ножницы»: монстр слева нависает; кот справа выхватывает лапой ножницы, блеск."""
    a, b = T0("s07"), T1("s07")
    ts = W(35)
    o = room(t)
    o.append(monster(250, RFL, 900, t, mouth=.5, look=(.8, .3)))
    paw = ease_out(ramp(t, W(34) - .1, .3))
    ck, cx = 1.3, 700
    o.append(cat(cx, RFL, ck, t, dict(look=(-.6, -.6), smile=.7, paw_l=paw, paw_l_dx=70, perk=1.0, tail=10 * math.sin(t * 3))))
    tip = (cx + (-70 - 70 * paw * 1.6) * ck, RFL - 150 * paw * ck)
    if paw > .05:
        o.append(PR.scissors(tip[0] + 30, tip[1] - 20, 1.4 * (.5 + .5 * paw), snip_u=(t * 3) % 1 if t > ts else 0.0, rot=200))
        o.append(PR.star4(tip[0] - 10, tip[1] - 300 * paw, 40 * bump(t, ts, .05, .5) + 1))
        o.append(PR.sparkles(tip[0] - 10, tip[1] - 200, 1.6, bump(t, ts, .05, .5), t, seed=71, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts, 9)
    return view("".join(o), 640 + dx, 1100 + dy, 1.1 + .06 * u, 0, t=t)


def frame_s08(t):
    """«и разрезал его на маленьких монстриков»: ножницы чикают по монстру, он распадается на три маленьких, они выпрыгивают."""
    a, b = T0("s08"), T1("s08")
    tc = W(37)
    ts = W(40)
    o = room(t)
    split = ease_out(ramp(t, ts - .2, .4))
    if split < .5:
        sh = bump(t, tc, .05, .3)
        o.append(monster(540 + 10 * sh * math.sin(t * 60), RFL, 900 * (1 - .3 * split), t, mouth=.6, look=(0, .2), sq=.2 * sh))
        for j in range(2):
            u = ramp(t, tc + .15 * j, .3)
            if u > 0:
                yy = RFL - 300 - 260 * j
                o.append(line([(240, yy - 80 * j), (240 + 600 * u, yy + 40 - 80 * j)], 9, "#ffffff", taper=.2, wmin=.6, seed=4700 + j))
                o.append(PR.scissors(240 + 600 * u, yy + 40 - 80 * j, 1.1, snip_u=(t * 6) % 1, rot=10))
    else:
        for j in range(3):
            jx = 260 + 250 * j
            hop = abs(math.sin((t - ts) * 7 + j)) * (1 - ramp(t, ts + .6, .6))
            o.append(monster(jx, RFL - 120 * hop, 300, t, mouth=.3, look=(0, .3), mood="cute", sq=.3 * (hop - .3), seed=j + 1,
                             label=("ФАЙЛ", "ТЕКСТ", "?")[j]))
        o.append(PR.sparkles(540, RFL - 300, 2.4, bump(t, ts, .05, .5), t, seed=81, n=8, r=420))
    o.append(cat(980, RFL, .8, t, dict(look=(-.8, -.3), smile=1.0)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tc, 9)
    return view("".join(o), 600 + dx, 1100 + dy, 1.05 + .05 * u, 0, t=t)


def frame_s09(t):
    """«Каждого я побеждал за две минуты»: Дима с секундомером, напротив монстрик «ФАЙЛ»; стрелка делает круг до 2:00."""
    a, b = T0("s09"), T1("s09")
    tm = W(46)
    o = room(t)
    f = stand(300, t, "sure82", "d82_hold")
    o.append(f["svg"])
    hx, hy = f["hold"]
    o.append(PR.stopwatch(hx + 60, hy - 120, .8, hand_a=720 * ramp(t, a, b - a), click=bump(t, tm, .05, .2), t=t))
    o.append(monster(820, RFL, 320, t, mouth=.2, look=(-.7, -.2), mood="cute", label="ФАЙЛ", seed=1, sq=.2 * math.sin(t * 8)))
    if t > tm:
        o.append(text("2:00", 560, 520, 170 * pop(t, tm, .25), fill="#FFD23F", stroke="#111", sw=12))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tm, 8)
    return view("".join(o), 560 + dx, 1180 + dy, 1.12 + .06 * u, 0, t=t)


def poof(x, y, t, t0, k=1.0):
    """Монстрик лопается: кольцо и звёздочки."""
    u = ramp(t, t0, .4)
    if u <= 0 or u >= 1:
        return ""
    o = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{(40 + 160 * u) * k:.1f}" fill="none" stroke="#FFD23F" stroke-width="{14 * (1 - u) * k:.1f}"/>'
    return o + PR.sparkles(x, y, 1.4 * k, 1 - u, t, seed=int(t0 * 10), n=6, r=180 * k)


def frame_s10(t):
    """«открыть файл, написать заголовок»: Дима за столом с ноутбуком; на «файл» лопается монстрик ФАЙЛ, на «заголовок» — ТЕКСТ."""
    a, b = T0("s10"), T1("s10")
    t1, t2 = W(49), W(51) + .2
    o = desk_room(t, mode="day")
    o.append(dima_desk(t, "sure82" if t < t2 else "proud82", "sit_desk")["svg"])
    o.append(PR.laptop(700, DESK_Y, .55, 1.0, screen="page" if t > t1 else "dark", lines=ramp(t, W(50), .8), t=t))
    for lab, x, t0, sd in (("ФАЙЛ", 830, t1, 1), ("ТЕКСТ", 950, t2, 2)):
        if t < t0:
            o.append(monster(x, DESK_Y - 10, 190, t, mouth=.2, look=(-.6, .2), mood="cute", label=lab, seed=sd, sq=.25 * math.sin(t * 9 + sd)))
        else:
            o.append(poof(x, DESK_Y - 100, t, t0))
            o.append(PR.check_mark(x, DESK_Y - 60, 2.6, ramp(t, t0 + .1, .25)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t2, 8)
    return view("".join(o), 720 + dx, 930 + dy, 1.55 + .06 * u, 0, t=t)


def plane(x, y, k, rot=0.0):
    o = '<path d="M-60 0 L60 -30 L-10 40 Z" fill="#ffffff" stroke="#111" stroke-width="5" stroke-linejoin="round"/>'
    o += '<path d="M-10 40 L0 6 L60 -30" fill="none" stroke="#111" stroke-width="4"/>'
    o += text("?", -2, -10, 46, fill="#2f8fe0", stroke="#ffffff", sw=2)
    return tf(o, x, y, k, rot)


def frame_s11(t):
    """«отправить один вопрос»: самолётик с вопросом улетает из ноутбука, последний монстрик «?» лопается галочкой."""
    a, b = T0("s11"), T1("s11")
    tf_ = W(52) + .2
    tq = W(54)
    o = desk_room(t, mode="day")
    o.append(dima_desk(t, "proud82", "sit_desk")["svg"])
    o.append(PR.laptop(700, DESK_Y, .55, 1.0, screen="page", lines=1.0, t=t))
    u = lib.ease_in(ramp(t, tf_, .7))
    if t > tf_ - .1 and u < 1:
        o.append(plane(700 + 500 * u, DESK_Y - 220 - 420 * u, 1.3, -20 * u))
    if t < tq:
        o.append(monster(970, DESK_Y - 10, 190, t, mouth=.2, look=(-.6, .2), mood="cute", label="?", seed=3, sq=.25 * math.sin(t * 9)))
    else:
        o.append(poof(970, DESK_Y - 100, t, tq))
        o.append(PR.check_mark(970, DESK_Y - 60, 2.6, ramp(t, tq + .1, .25)))
    for x in (830, 900):
        o.append(PR.check_mark(x, DESK_Y - 60, 1.8, 1.0))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tq, 8)
    return view("".join(o), 720 + dx, 930 + dy, 1.5 + .05 * uu, 0, t=t)


def frame_s12(t):
    return cta_code(t, T0("s12"), T1("s12"))


def frame_s13(t):
    """«чтобы твой монстр тоже стал маленьким»: огромный монстр сжимается рывками в маленького милого; кот гладит его лапой."""
    a, b = T0("s13"), T1("s13")
    tw = W(60)
    s = ease_out(ramp(t, tw - .1, .9))
    h = 900 - 620 * s
    o = room(t)
    o.append(fridge(900, RFL, op=.35 + .65 * (1 - s)))
    o.append(monster(480, RFL, h, t, mouth=.6 * (1 - s), look=(.4, .3), mood="mean" if s < .55 else "cute", sq=.25 * math.sin(t * 14) * (1 - s)))
    o.append(cat(760, RFL, .9, t, dict(look=(-.8, .3), smile=1.0 if s > .6 else .3, paw_l=ramp(t, tw + .7, .3), paw_l_dx=90,
                                     tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(480, RFL - h / 2, 1.6, bump(t, W(63), .05, .5), t, seed=131, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(63), 8)
    return view("".join(o), 600 + dx, 1160 + dy, 1.0 + .1 * u, 0, t=t)


def frame_s14(t):
    """«От холодильника осталась одна галочка»: пунктирный контур холодильника, внутри одна большая зелёная галочка; Дима и кот рады."""
    a, b = T0("s14"), T1("s14")
    tg = W(68)
    o = room(t)
    o.append(fridge(660, RFL, dashed=True))
    o.append(PR.glow(660, RFL - 400, 400, .5 * ramp(t, tg, .3), "#c8ffb0"))
    o.append(PR.check_mark(660, RFL - 400, 9.0 * (1 + .1 * bump(t, tg, .05, .3)), ramp(t, a + .2, .6), w=7))
    f = stand(180, t, "laugh82" if t > tg else "proud82", "d82_one", head_add=.05)
    o.append(f["svg"])
    o.append(cat(930, RFL, .8, t, dict(look=(-.7, -.6), smile=1.0, tail=12 * math.sin(t * 4))))
    o.append(PR.sparkles(660, RFL - 420, 2.0, bump(t, tg, .05, .6), t, seed=141, n=8, r=360))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tg, 8)
    return view("".join(o), 610 + dx, 1050 + dy, 1.0 + .06 * u, 0, t=t)


def frame_s15(t):
    """Петля: кадр хука — монстр с тумбочку."""
    a, b = T0("s15"), T1("s15")
    o = room(t)
    o.append(PR.window(250, 1150, 300, 380, mode="evening", t=t, seed=4, curtain=False))
    o.append(nightstand(760, RFL))
    o.append(monster(470, RFL, NS_H * .95, t, mouth=.4, look=(.6, .2)))
    return loop_view("".join(o), t, a, b, HIT, 620, 1420, 2.1)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
