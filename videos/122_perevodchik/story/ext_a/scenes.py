"""Рилс 122 «Переводчик с СДВГ», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Места: стол со словарём (кот в очках листает
толстый словарь «СДВГ — РУССКИЙ», переводы выскакивают карточками «фраза → перевод»), диван, стол с ноутбуком.
В пузырях и на карточках — настоящие слова сценария. NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people, big_title  # noqa: E402
import room as RM  # noqa: E402

HIT = stress(0, .3)
STUDY_WALL = "#4a3f5e"
DESK_TOP = 1540.0
COVER, COVER_SH = "#b8433a", "#8a2c25"
PAGE, PAGE_SH = "#fbf6ea", "#ece2cc"
SKIN = "#ecc4a2"
INK2 = "#1d2448"


def tw(s, size):
    return big_title.text_w(s, size)


def wrap(s, size, maxw):
    lines, cur = [], ""
    for w_ in s.split():
        nx = (cur + " " + w_).strip()
        if cur and tw(nx, size) > maxw:
            lines.append(cur)
            cur = w_
        else:
            cur = nx
    if cur:
        lines.append(cur)
    return lines


# ═════════════ словарь, очки кота, карточка перевода ═════════════
def page_lines(x0, x1, y0, n, seed, head=None):
    o = ""
    if head:
        o += plain(head, (x0 + x1) / 2, y0 - 24, 34, fill=COVER, anchor="middle")
    for j in range(n):
        y = y0 + 34 * j
        bw = 40 + 26 * ((j * 7 + seed) % 3)
        o += line([(x0, y), (x0 + bw, y)], 7, INK2, taper=.1, wmin=.8, seed=seed + 2 * j)
        o += line([(x0 + bw + 14, y), (x1 - 20 * ((j + seed) % 3), y)], 4, "#b9b2a2", taper=.1, wmin=.8, seed=seed + 2 * j + 1)
    return o


def big_book(x, y, k=1.0, t=0.0, flip=None, glow=0.0, heads=True):
    """Толстый раскрытый словарь, страницы к зрителю. (x, y) — низ корешка. Левая страница «СДВГ», правая «РУССКИЙ».
    flip 0…1 — страница переворачивается справа налево."""
    Wp, Hp = 330.0, 400.0
    o = [blob(ellipse_pts(0, 20, Wp + 60, 30, 24), "#000000", .25)]
    o.append(shape([(-Wp - 26, 12, 1), (0, 24, 1), (Wp + 26, 12, 1), (Wp + 24, -Hp - 6, 1), (0, -Hp + 6, 1), (-Wp - 24, -Hp - 6, 1)],
                   COVER, "", w=5, seed=3100))
    for j in range(5):                                       # толщина: торцы страниц стопкой
        dy = 4 + 3.4 * j
        o.append(line([(-Wp - 14, dy - 6), (-4, dy + 6)], 2.4, "#c9bda4", taper=0, wmin=1, seed=3110 + j))
        o.append(line([(4, dy + 6), (Wp + 14, dy - 6)], 2.4, "#c9bda4", taper=0, wmin=1, seed=3120 + j))
    lp = [(0, 0, 1), (-Wp * .5, -14), (-Wp, -6, 1), (-Wp, -Hp, 1), (-Wp * .5, -Hp - 10), (0, -Hp + 8, 1)]
    rp = [(0, 0, 1), (Wp * .5, -14), (Wp, -6, 1), (Wp, -Hp, 1), (Wp * .5, -Hp - 10), (0, -Hp + 8, 1)]
    o.append(shape(lp, PAGE, blob(lib.rect_pts(-40, -Hp, 0, 0), PAGE_SH, .8)
                   + page_lines(-Wp + 34, -40, -Hp + 92, 9, 3130, "СДВГ" if heads else None), w=4.4, seed=3140))
    o.append(shape(rp, PAGE, blob(lib.rect_pts(0, -Hp, 40, 0), PAGE_SH, .8)
                   + page_lines(40, Wp - 34, -Hp + 92, 9, 3150, "РУССКИЙ" if heads else None), w=4.4, seed=3160))
    if glow > 0:
        o.append(PR.glow(Wp * .5, -Hp * .5, 300, .45 * glow, "#fff1b0"))
    if flip is not None and 0 < flip < 1:
        c = math.cos(math.pi * flip)
        lift = 40 * math.sin(math.pi * flip)
        xe = Wp * c
        fp = [(0, 0, 1), (xe * .5, -14 - lift), (xe, -6 - lift, 1), (xe, -Hp - lift, 1), (xe * .5, -Hp - 10 - lift), (0, -Hp + 8, 1)]
        col = PAGE if c > 0 else PAGE_SH
        o.append(shape(fp, col, "", w=4.0, seed=3170))
    return tf("".join(o), x, y, k)


def glasses(x, y, k):
    """Круглые очки на кота draw(x, y, k): глаза в (±44, −234)·k от точки лап."""
    hy = y - 234 * k
    o = ""
    for sx in (-1, 1):
        o += f'<circle cx="{x + sx * 46 * k:.1f}" cy="{hy:.1f}" r="{44 * k:.1f}" fill="#ffffff" fill-opacity=".18" stroke="#1a1a1a" stroke-width="{7 * k:.1f}"/>'
    o += line([(x - 6 * k, hy - 6 * k), (x + 6 * k, hy - 6 * k)], 6 * k, "#1a1a1a", taper=0, wmin=1, seed=3180)
    return o


def cat_g(x, y, k, t, st=None):
    return cat(x, y, k, t, st) + glasses(x, y, k)


def tcard(x, y, k, src, dst, u_src=1.0, u_dst=1.0, rot=-2.0, strike=0.0, new=None, u_new=0.0, t=0.0):
    """Карточка перевода: плашка «СДВГ», фраза в кавычках, красная стрелка, плашка «ПО-РУССКИ», перевод.
    strike — перевод перечёркивается, new — новое слово штампом поверх (u_new)."""
    Wc = 900.0
    s1, s2 = 74.0, 66.0
    L1 = wrap("«" + src + "»", s1, Wc - 80)
    L2 = wrap(dst, s2, Wc - 70)
    h = 90 + 84 * len(L1) + 120 + 76 * len(L2) + 60
    top = -h / 2
    o = blob(lib.rect_pts(-Wc / 2 + 16, top + 20, Wc / 2 + 16, top + h + 20), "#000000", .22)
    inner = ""

    def pill(s_, cx, cy, col):
        w_ = tw(s_, 38) + 44
        return (shape(lib.rrect(cx - w_ / 2, cy - 30, cx + w_ / 2, cy + 26, 26), col, "", w=3.4, seed=3200 + len(s_))
                + text(s_, cx, cy + 12, 38, fill="#ffffff", stroke=col, sw=.01))
    yy = top + 60
    inner += pill("СДВГ", -Wc / 2 + 120, yy, "#7a5cc0")
    yy += 30
    for j, s_ in enumerate(L1):
        yy += 84
        inner += text(s_, 0, yy, s1, fill=INK2, stroke="#ffffff", sw=.01, op=u_src)
    yy += 30
    if u_dst > 0:
        a = clamp(u_dst * 2)
        inner += line([(0, yy), (0, yy + 54 * a)], 12, RED, taper=0, wmin=1, seed=3210)
        if a >= 1:
            inner += shape([(-30, yy + 40, 1), (30, yy + 40, 1), (0, yy + 76, 1)], RED, "", w=3, seed=3211)
    yy += 90
    du = clamp(u_dst * 2 - .6)
    if du > 0:
        inner += pill("ПО-РУССКИ", Wc / 2 - 170, yy - 40, GREEN)
        y0 = yy
        for j, s_ in enumerate(L2):
            yy += 76
            inner += text(s_, 0, yy, s2, fill=RED if new is None else "#a0303a", stroke="#ffffff", sw=.01, op=du)
        if strike > 0:
            for j in range(len(L2)):
                ly = y0 + 76 * (j + 1) - 22
                lw = tw(L2[j], s2) / 2 + 20
                n = clamp(strike * len(L2) - j)
                if n > 0:
                    inner += line([(-lw, ly + 6), (-lw + 2 * lw * n, ly - 6)], 12, INK2, taper=.1, wmin=.8, seed=3220 + j)
    card_b = shape(lib.rrect(-Wc / 2, top, Wc / 2, top + h, 34), "#fffdf6", inner, w=6, seed=3230)
    o += card_b
    o += blob(lib.rect_pts(-60, top - 18, 60, top + 22), "#f2d27a", .85)      # скотч
    if new and u_new > 0:
        s = 1.0 + 1.4 * (1 - ease_out(clamp(u_new)))
        st = (f'<g transform="translate(0 {top + h - 120:.1f}) rotate(-10) scale({s:.3f})" opacity="{min(1.0, u_new * 3):.3f}">'
              f'<rect x="-250" y="-90" width="500" height="160" rx="18" fill="#ffffff" fill-opacity=".85" stroke="{GREEN}" stroke-width="16"/>'
              + text(new, 0, 34, 130, fill=GREEN, stroke=GREEN, sw=.01) + "</g>")
        o += st
    return tf(o, x, y, k, rot)


def study(t, glow=0.0):
    """Стол у стены, тёплая лампа: здесь кот переводит."""
    o = [rect(-1400, -1400, 2600, DESK_TOP, STUDY_WALL)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, DESK_TOP, lib.mul(STUDY_WALL, (.93, .93, .95)), .6))
    o.append(PR.glow(300, 700, 700, .35 + .2 * glow, "#ffd890"))
    for j, (bx, bh, col) in enumerate(((60, 150, "#4f78b5"), (110, 170, "#3fb26a"), (160, 140, "#e2a03a"), (900, 160, "#9a6fd1"),
                                       (950, 140, "#e2453a"), (1000, 170, "#4f78b5"))):
        o.append(shape(lib.rect_pts(bx - 22, 1000 - bh, bx + 22, 1000), col, "", w=3.4, seed=3300 + j))
    o.append(shape(lib.rect_pts(-200, 1000, 1300, 1024), "#8a5b32", "", w=4, seed=3310))
    o.append(rect(-1400, DESK_TOP, 2600, 3000, "#c48a52"))
    o.append(rect(-1400, DESK_TOP + 380, 2600, 3000, "#8a5b32"))
    o.append(line([(-1400, DESK_TOP + 380), (2600, DESK_TOP + 380)], 5, seed=3313))
    o.append(rect(-1400, DESK_TOP, 2600, DESK_TOP + 40, "#ce9a68"))
    o.append(line([(-1400, DESK_TOP), (2600, DESK_TOP)], 5, seed=3311))
    o.append(line([(-1400, DESK_TOP + 40), (2600, DESK_TOP + 40)], 3, seed=3312))
    for j in range(5):
        o.append(line([(-100 + 300 * j, DESK_TOP + 200 + 40 * (j % 2)), (120 + 300 * j, DESK_TOP + 210 + 40 * (j % 2))], 3, "#94633a",
                      taper=.3, wmin=.4, seed=3320 + j))
    return o


def flip_of(t, a, d=.35):
    u = (t - a) / d
    return u if 0 < u < 1 else None


def book_desk(t, flips=(), glow=0.0, bx=420.0, cat_x=905.0, look=(-.7, .3), smile=.6):
    """Стол, словарь, кот в очках справа листает лапой (flips — моменты начала перелистывания)."""
    o = study(t, glow)
    fl = None
    paw = 0.0
    for a in flips:
        f_ = flip_of(t, a)
        if f_ is not None:
            fl = f_
        paw = max(paw, bump(t, a - .12, .1, .2))
    o.append(big_book(bx, DESK_TOP - 10, 1.18, t, fl, glow))
    o.append(cat_g(cat_x, DESK_TOP + 6, .95, t, dict(look=look, smile=smile, paw=paw, paw_dx=-95, tail=10 * math.sin(t * 2.6))))
    o.append(desk_props(t))
    return o


def desk_props(t):
    """Передний край стола: кружка с паром, карандаши, стикеры (низ кадра не пустой)."""
    o = PR.mug(150, DESK_TOP + 230, 1.3, col="red", steam=1.0, t=t)
    o += PR.pencil(520, DESK_TOP + 200, 1.6, -12)
    o += PR.pencil(600, DESK_TOP + 230, 1.6, 8)
    o += PR.sticky(860, DESK_TOP + 210, 1.0, -8, col="yellow", seed=2)
    o += PR.sticky(970, DESK_TOP + 240, .9, 10, col="pink", seed=3)
    return o


def frame_s01(t):
    """ХУК: кот в очках с бешеной скоростью листает толстый словарь, страницы летят."""
    flips = [-.1 + .22 * j for j in range(7)]
    o = book_desk(t, flips, glow=.6, look=(-.8, .4), smile=.4)
    for j in range(5):                                   # вылетевшие листки
        u = ((t * 1.4 + j * .23) % 1.0)
        x = 430 + 80 * j - 150 + 500 * u * (1 if j % 2 else -.6)
        y = 1060 - 420 * u + 200 * u * u
        o.append(tf(shape(lib.rect_pts(-50, -64, 50, 64), PAGE, page_lines(-36, 36, -40, 4, 3400 + j), w=3, seed=3410 + j),
                    x, y, .9, 200 * u + 40 * j))
    o.append(PR.sparkles(430, 1250, 2.0, .6 + .4 * math.sin(t * 9), t, seed=11, n=6, r=330))
    dx, dy = shake(t, W(2), 10)
    return hook_view("".join(o), t, HIT, 540, 1110, 1.0, 0, bg=STUDY_WALL, dx=dx, dy=dy)


def frame_s02(t):
    """«на русский»: словарь замер, красная дуга-стрелка от «СДВГ» к «РУССКИЙ», кот довольный тычет лапой в перевод."""
    a, b = T0("s02"), T1("s02")
    ta = W(4)
    o = book_desk(t, [a - .2], glow=1.0, look=(-.8, .2), smile=1.0)
    u = ease_out(ramp(t, a, ta + .1 - a))
    pts = [(210 + 420 * (i / 14), 1150 - 170 * math.sin(math.pi * i / 14)) for i in range(15)]
    n = max(2, int(15 * u))
    o.append(line(pts[:n], 14, RED, taper=.2, wmin=.6, seed=3500))
    if u >= 1:
        ex, ey = pts[-1]
        o.append(shape([(ex - 36, ey - 30, 1), (ex + 12, ey + 6, 1), (ex - 40, ey + 24, 1)], RED, "", w=3, seed=3501))
    o.append(PR.sparkles(640, 1150, 1.8, bump(t, ta, .05, .5), t, seed=21, n=6, r=200))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ta, 9)
    return view("".join(o), 600 + dx, 1180 + dy, 1.12 + .06 * uu, 0, bg=STUDY_WALL, t=t)


def card_scene(t, sid, src, dst, i_dst, strike=0.0, new=None, u_new=0.0, cy=720.0):
    """План-карточка: стол со словарём, кот листает на старте плана, карточка выскакивает из книги; перевод проявляется
    с первого слова перевода (i_dst)."""
    a, b = T0(sid), T1(sid)
    o = book_desk(t, [a - .25], glow=.8, look=(-.5, -.8), smile=.8)
    u = ramp(t, a - .2, .3)
    s = .9 + .1 * (lib.back_out(u, 2.2) if u < 1 else 1.0)
    ud = ramp(t, W(i_dst) - .15, .45)
    o.append(PR.sparkles(540, cy, 2.2, bump(t, W(i_dst), .05, .5), t, seed=hash(sid) % 50, n=6, r=430))
    o.append(tcard(540, cy - 40 * (1 - u), s, src, dst, 1.0, ud, -2.0 + 1.0 * u, strike, new, u_new, t))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(i_dst), 8)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .05 * uu, 0, bg=STUDY_WALL, t=t)


def bubble_t(x, y, s, size, u, tail=(-80, 70), seed=0, cam=None):
    """Пузырь речи с настоящими словами (1–2 строки). cam=(cx, s) — пузырь не выходит за края кадра (хвост держит адресата)."""
    if u <= .02:
        return ""
    L = wrap(s, size, 560)
    w = max(tw(x_, size) for x_ in L) + 110
    if cam:
        cx, sc = cam
        lim = (540 - 50) / sc - w / 2
        nx = min(max(x, cx - lim), cx + lim)
        tail = (tail[0] + (x - nx), tail[1])
        x = nx
    h = 70 + size * 1.1 * len(L)
    o = PR.speech_bubble(0, 0, w, h, 1.0, seed=seed, tail=tail)
    for j, s_ in enumerate(L):
        o += text(s_, 0, -h / 2 + 40 + size * .95 + size * 1.1 * j - size * .1, size, fill=INK2, stroke="#ffffff", sw=.01)
    k = lib.back_out(clamp(u), 2.0) if u < 1 else 1.0
    return tf(o, x, y, k)


SOFA_X = 540.0
SEAT = RFL - 310


def sofa_dima(t, expr, x=470.0, lean=0.0, head_add=0.0, arms=None, k=.66):
    hip = SEAT - 4
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    kw = {"arms": arms} if arms else {}
    return people.dima82(x, hip, k, expr, "sit_desk", t=t, feet=feet, lean_add=lean, head_add=head_add, **kw)


def living(t, mode="day", clock=None, evening=0.0):
    o = [plain_room(t)]
    o.append(PR.window(930, 1050, 300, 400, mode=mode, t=t, seed=4, curtain=False))
    if evening > 0:
        o.append(tf(rect(-150, -400, 150, 0, "#2b2f6a", .55 * evening), 930, 1050))
    if clock:
        o.append(clock)
    o.append(rug(540, RFL + 160, 560))
    return o


def frame_s03(t):
    """«„Я на секундочку“»: Дима на диване берёт телефон, пузырь «Я на секундочку»; кот рядом смотрит с подозрением."""
    a, b = T0("s03"), T1("s03")
    o = living(t)
    sf = RM.sofa(SOFA_X, RFL, 1.0)
    o.append(sf["back"])
    f = sofa_dima(t, "sly", head_add=-.05)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(mini_phone(hx + 150, hy + 230, .75, -10, screen="#9fc7ff"))
    o.append(sf["arm_r"])
    o.append(cat(780, SEAT + 4, .62, t, dict(look=(-.9, -.3), smug=.6, tail=8 * math.sin(t * 2))))
    o.append(bubble_t(hx + 190, hy - 230, "Я на секундочку", 64, pop(t, a - .1, .25), tail=(-150, 70), seed=1, cam=(560, 1.3)))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1040, 1.3 + .05 * uu, 0, t=t)


def frame_s04(t):
    return card_scene(t, "s04", "Я на секундочку", "увидимся через два часа", 9)


def frame_s05(t):
    """«два часа»: Дима на диване залип в телефон, стрелки часов над ним пролетают два часа, кот уснул."""
    a, b = T0("s05"), T1("s05")
    u = ease_io(ramp(t, a - .1, b - a - .2))
    h = 2 + 2 * u
    clk = PR.clock(540, 560, 100, *PR.clock_hm(h, 60 * (h % 1) + 0.0), seed=2)
    o = living(t, clock=clk, evening=u * .7)
    o.append(text("+2 ЧАСА", 540, 760, 70, fill="#ffffff", stroke="#111", sw=8, op=clamp(u * 3)))
    sf = RM.sofa(SOFA_X, RFL, 1.0)
    o.append(sf["back"])
    f = sofa_dima(t, "screen80", lean=.15, head_add=.1)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(mini_phone(hx + 130, hy + 170, .75, -25, screen="#9fc7ff"))
    o.append(PR.glow(hx + 100, hy + 100, 160, .5, "#9fc7ff"))
    o.append(sf["arm_r"])
    o.append(CT.curl(800, SEAT - 20, .5, dict(eye=0.0), t))
    o.append(PR.zzz(840, SEAT - 180, .8, t, 1.0))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 980, 1.2 + .05 * uu, 0, t=t)


def desk_laptop(t, lines=.0, screen="page"):
    o = desk_room(t)
    o.append(PR.laptop(700, DESK_Y, .55, 1.0, screen=screen, lines=lines, t=t))
    return o


def frame_s06(t):
    """«„Я сейчас начну“»: Дима за столом у открытого ноутбука, руки за головой, пузырь «Я сейчас начну»; кот на столе."""
    a, b = T0("s06"), T1("s06")
    o = desk_laptop(t)
    f = dima_desk(t, "sure82", lean=-.12)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(cat(900, DESK_Y - 4, .45, t, dict(look=(-.9, -.4), smile=.3, tail=8 * math.sin(t * 2))))
    o.append(bubble_t(hx + 170, hy - 200, "Я сейчас начну", 60, pop(t, a - .1, .25), tail=(-130, 70), seed=2, cam=(590, 1.5)))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 590, 880, 1.5 + .05 * uu, 0, t=t)


def frame_s07(t):
    return card_scene(t, "s07", "Я сейчас начну", "я буду думать об этом до вечера", 17)


def frame_s08(t):
    """«думать об этом до вечера»: Дима на диване, облако с ноутбуком над головой, за окном день → вечер."""
    a, b = T0("s08"), T1("s08")
    u = ease_io(ramp(t, a, b - a))
    o = living(t, mode="day" if u < .5 else "evening", evening=0.0)
    o.append(rect(-1400, -1400, 2600, 3400, "#3b2a5a", .3 * u))
    sf = RM.sofa(SOFA_X, RFL, 1.0)
    o.append(sf["back"])
    f = sofa_dima(t, dict(people.EXPR["dima"]["thoughtful"], look=(.3, -.9)), lean=-.1, head_add=-.1)
    o.append(f["svg"])
    o.append(sf["arm_r"])
    hx, hy = f["head"]
    inner = PR.laptop(0, 40, .32, 1.0, screen="dark", t=t) + text("?", 120, -10, 90, fill=RED, stroke="#ffffff", sw=6)
    o.append(PR.thought_cloud(hx + 200, hy - 260, 1.25, w=340, h=220, u=1.0, seed=3, inner=inner))
    o.append(cat(800, SEAT + 4, .6, t, dict(look=(-.8, -.5), smile=.2)))
    return view("".join(o), 580, 980, 1.25 + .05 * u, 0, t=t)


def frame_s09(t):
    """«„Я не забыл“»: Дима стоит с телефоном у уха, бодро машет, пузырь «Я не забыл»; кот снизу косится."""
    a, b = T0("s09"), T1("s09")
    o = [plain_room(t), rug(540, RFL + 160, 560)]
    f = stand(380, t, "cheerful", "d82_hold", head_add=.04)
    o.append(f["svg"])
    hx, hy = f["hold"]
    o.append(mini_phone(hx, hy - 40, .9, 0, screen="#9fc7ff"))
    o.append(cat(780, RFL, .75, t, dict(look=(-.8, -.6), smug=.7)))
    o.append(bubble_t(f["head"][0] + 240, f["head"][1] - 230, "Я не забыл", 72, pop(t, a - .1, .25), tail=(-140, 70), seed=4, cam=(540, 1.22)))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1060, 1.22 + .05 * uu, 0, t=t)


def frame_s10(t):
    return card_scene(t, "s10", "Я не забыл", "я забыл, и мне ужасно стыдно", 28)


def frame_s11(t):
    """«ужасно стыдно»: Дима краснеет, капля пота, тучка над головой; кот встаёт и гладит его лапой по ноге."""
    a, b = T0("s11"), T1("s11")
    o = [plain_room(t), rug(540, RFL + 160, 560)]
    f = stand(420, t, dict(people.EXPR["dima"]["guilty"], blush=1.0), "d82_shrug", head_add=.12)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sweat(hx + 70, hy - 30, 1.2))
    o.append(PR.gloom(hx, hy - 220, 1.1, t, ramp(t, a, .3), seed=5))
    pat = .7 + .3 * math.sin(t * 9)
    o.append(cat(640, RFL, .75, t, dict(look=(-.8, -.7), smile=.6, paw=pat, paw_dx=-70, tilt=-6)))
    o.append(PR.heart(560, 1260 - 30 * ramp(t, W(33), .6), .5 * pop(t, W(33), .3)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(33), 7)
    return view("".join(o), 520 + dx, 1000 + dy, 1.3 + .07 * uu, 0, t=t)


def frame_s12(t):
    """«„Я просто устал“»: Дима сполз на диване, пузырь «Я просто устал»; кот на подлокотнике."""
    a, b = T0("s12"), T1("s12")
    o = living(t, mode="evening")
    sf = RM.sofa(SOFA_X, RFL, 1.0)
    o.append(sf["back"])
    f = sofa_dima(t, "zombie", lean=-.25, head_add=.2)
    o.append(f["svg"])
    o.append(sf["arm_r"])
    hx, hy = f["head"]
    o.append(cat(800, SEAT + 4, .6, t, dict(look=(-.8, -.3), smile=.3)))
    o.append(bubble_t(hx + 190, hy - 230, "Я просто устал", 62, pop(t, a - .1, .25), tail=(-140, 70), seed=5, cam=(560, 1.3)))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1040, 1.3 + .05 * uu, 0, t=t)


def frame_s13(t):
    return card_scene(t, "s13", "Я просто устал", "я весь день держал в голове сорок дел", 38)


def frame_s14(t):
    """«держал в голове сорок дел»: вокруг головы Димы кружат стикеры дел, счётчик «40 ДЕЛ»; кот снизу смотрит вверх."""
    a, b = T0("s14"), T1("s14")
    o = [plain_room(t, wall="#e6d6bc"), rug(540, RFL + 160, 560)]
    f = stand(540, t, "strain", "d82_rest", head_add=.03 * math.sin(t * 7))
    o.append(f["svg"])
    hx, hy = f["head"]
    n = 8 + int(32 * clamp((t - a) / (W(44) - a)))
    cols = ["yellow", "pink", "blue", "green"]
    back, front = [], []
    for j in range(min(n, 40)):
        ring = j % 3
        ang = t * (1.4 - .3 * ring) + j * 2.399
        r = 250 + 100 * ring
        x = hx + r * math.cos(ang)
        y = hy - 40 + .8 * r * math.sin(ang)
        if abs(x - hx) < 150 and abs(y - hy) < 170:
            continue                                     # лицо всегда открыто
        st_ = PR.sticky(x, y, .55 + .1 * (ring == 0), 20 * math.sin(ang + j), col=cols[j % 4], seed=j % 9)
        (front if math.sin(ang) > 0 else back).append(st_)
    o.insert(2, "".join(back))
    o.append("".join(front))
    o.append(tf(shape(lib.rrect(-150, -66, 150, 66, 30), RED, "", w=5, seed=3600)
                + text(f"{n} ДЕЛ" if n < 40 else "40 ДЕЛ", 0, 26, 76, fill="#ffffff", stroke="#7a1e18", sw=6),
                hx, hy - 420, 1.0 + .25 * bump(t, W(44), .04, .25)))
    o.append(cat(820, RFL, .7, t, dict(look=(-.5, -.9), perk=1.0)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(44), 9)
    return view("".join(o), 540 + dx, 960 + dy, 1.05 + .05 * uu, 0, t=t)


def phone_big(x, y, k, inner):
    o = shape(lib.rrect(-260, -470, 260, 470, 60), "#2a2d36", "", w=6, seed=3700)
    o += shape(lib.rrect(-230, -430, 230, 430, 34), "#e9eef5", inner, w=3, seed=3701)
    return tf(o, x, y, k)


def mini_dict(x, y, k, rot=0.0):
    """Маленький закрытый словарь «СЛОВАРЬ» (для чата и самолётика)."""
    o = shape(lib.rrect(-120, -150, 120, 150, 14), COVER, blob(lib.rect_pts(-120, -150, -96, 150), COVER_SH, .9), w=5, seed=3710)
    o += text("СЛОВАРЬ", 10, -30, 42, fill="#fff3c8", stroke=COVER_SH, sw=4)
    o += text("СДВГ", 10, 30, 40, fill="#ffffff", stroke=COVER_SH, sw=4)
    o += text("→", 10, 74, 40, fill="#ffffff", stroke=COVER_SH, sw=4)
    o += text("РУССКИЙ", 10, 118, 36, fill="#ffffff", stroke=COVER_SH, sw=4)
    return tf(o, x, y, k, rot)


def frame_s15(t):
    """«Отправь это тому»: телефон крупно, в чате словарь, лапа кота жмёт «Отправить», словарь улетает самолётиком."""
    a, b = T0("s15"), T1("s15")
    tp = W(48) - .15
    fly = ease_io(ramp(t, tp, .6))
    inner = rect(-230, -430, 230, -330, "#5b8fd0") + text("Чат", 0, -365, 44, fill="#ffffff", stroke="#5b8fd0", sw=.01)
    if fly < 1:
        inner += mini_dict(60 + 200 * fly, 40 - 500 * fly, .9 - .6 * fly, 10 * fly)
    if fly > .6:
        inner += tf(shape(lib.rrect(-150, -60, 150, 60, 30), "#d8f5c8", "", w=3, seed=3725) + text("словарь ✓✓", 0, 16, 44, fill=INK2, stroke="#d8f5c8", sw=.01),
                    60, -200, pop(t, tp + .4, .25))
    pr = bump(t, tp, .05, .15)
    btn = shape(lib.rrect(-190, 300, 190, 400, 44), lib.mix("#2f8fe0", "#1d6fb8", pr), "", w=4, seed=3720)
    btn += text("Отправить", 0, 366, 52, fill="#ffffff", stroke="#1d6fb8", sw=.01)
    inner += btn
    o = [rect(-1400, -1400, 2600, 3400, "#3b3552"), PR.glow(540, 900, 700, .3, "#8fb7ff")]
    o.append(phone_big(540, 860, 1.3 - .03 * pr, inner))
    if fly > 0:
        px, py = 640 + 260 * fly, 760 - 480 * fly
        o.append(tf(shape([(-60, 0, 1), (60, -30, 1), (-20, 30, 1)], "#ffffff", "", w=4, seed=3730), px, py, 1.4, -20))
    paw = ease_out(ramp(t, a, tp - a))
    o.append(cat(900 - 40 * paw, 1830 - 90 * paw, 1.05, t, dict(look=(-.7, -.8), smile=.8, paw=paw, paw_dx=-90, perk=1.0)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tp + .05, 9)
    return view("".join(o), 540 + dx, 980 + dy, 1.0 + .05 * uu, 0, bg="#3b3552", t=t)


def frame_s16(t):
    """«такой словарь»: кот в очках обнимает толстый словарь «СЛОВАРЬ СДВГ → РУССКИЙ», искры."""
    a, b = T0("s16"), T1("s16")
    o = study(t, glow=1.0)
    o.append(cat_g(760, DESK_TOP + 6, 1.15, t, dict(look=(-.4, .2), smile=1.0, paw=.6, paw_dx=-80, tail=10 * math.sin(t * 3))))
    o.append(mini_dict(420, DESK_TOP - 270, 1.75, -6 + 3 * math.sin(t * 3)))
    o.append(desk_props(t))
    o.append(PR.sparkles(470, 1200, 2.4, bump(t, W(52), .05, .5) + .3, t, seed=161, n=7, r=330))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(52), 8)
    return view("".join(o), 560 + dx, 1180 + dy, 1.12 + .07 * uu, 0, bg=STUDY_WALL, t=t)


def frame_s17(t):
    return cta_code(t, T0("s17"), T1("s17"))


def frame_s18(t):
    """«чтобы „сейчас начну“ наконец…»: карточка «Я сейчас начну», старый перевод перечёркнут, штамп «НАЧАЛ»."""
    strike = ramp(t, W(58), .35)
    return card_scene(t, "s18", "сейчас начну", "я буду думать об этом до вечера", 55, strike=strike, new="НАЧАЛ",
                      u_new=ramp(t, W(59), .3), cy=720)


def frame_s19(t):
    """«значило „начал“»: Дима бодро печатает, строки бегут по экрану ноутбука, кот на столе, зелёная галочка."""
    a, b = T0("s19"), T1("s19")
    o = desk_laptop(t, lines=.2 + .8 * ramp(t, a - .2, b - a), screen="lines")
    tap = math.sin(t * 30)
    f = dima_desk(t, "focus_smile", lean=.18,
                  arms={"f": ("ik", (560 + 10 * tap, DESK_Y - 30), 1), "n": ("ik", (640 - 10 * tap, DESK_Y - 25), 1)})
    o.append(f["svg"])
    o.append(cat(900, DESK_Y - 4, .45, t, dict(look=(-.8, -.3), smile=1.0, tail=10 * math.sin(t * 3))))
    o.append(PR.check_mark(760, 520, 1.8, ramp(t, W(61) - .1, .3), col=GREEN, w=16))
    o.append(PR.sparkles(760, 520, 1.8, bump(t, W(61), .05, .5), t, seed=191, n=6, r=220))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(61), 8)
    return view("".join(o), 590 + dx, 860 + dy, 1.5 + .06 * uu, 0, t=t)


def frame_s20(t):
    """Петля: кадр хука — кот в очках над словарём."""
    a, b = T0("s20"), T1("s20")
    o = book_desk(t, [b - .05], glow=.6, look=(-.8, .4), smile=.4)
    return loop_view("".join(o), t, a, b, HIT, 540, 1110, 1.0, bg=STUDY_WALL)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
