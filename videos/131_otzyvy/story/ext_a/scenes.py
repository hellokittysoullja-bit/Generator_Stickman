"""Рилс 131 «Отзывы о моём мозге», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920.
Говорит Дима от первого лица (male2). Карточка товара «МОЙ МОЗГ» как на маркетплейсе (мозг-малыш, звёзды), отзывы
карточками (аватар-мозг, звёзды, текст отзыва словами сценария), между ними сцены: отчёт и полка, ежедневник в пыли,
«я на секундочку» и часы +2 часа, две минуты с котом рядом, новый отзыв на пять звёзд. Призыв — печатное жёлтое «КОТ».
NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402
import room as RM  # noqa: E402

HIT = stress(1, .4)
INK2 = "#1d2448"
GOLD, GREY = "#f6b81f", "#d4d8de"
SHOP = "#e9edf5"


def star5(x, y, r, col, u=1.0, seed=0):
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.6) if u < 1 else 1.0
    pts = [(r * (1 if i % 2 == 0 else .45) * math.cos(math.radians(-90 + 36 * i)), r * (1 if i % 2 == 0 else .45) * math.sin(math.radians(-90 + 36 * i)), 1)
           for i in range(10)]
    return tf(shape(pts, col, "", w=4, seed=8000 + seed), x, y, s)


def stars(x, y, r, n_on, u_list=None, gap=None):
    """Ряд из 5 звёзд с центром (x, y): первые n_on — золотые (u_list — проявление каждой), остальные серые."""
    gap = gap or r * 2.3
    o = ""
    for i in range(5):
        on = i < n_on
        u = 1.0 if u_list is None else (u_list[i] if i < len(u_list) else 1.0)
        o += star5(x + (i - 2) * gap, y, r, GREY, 1.0, seed=i)
        if on:
            o += star5(x + (i - 2) * gap, y, r, GOLD, u, seed=10 + i)
    return o


def avatar(x, y, r, t=0.0, expr="calm"):
    o = shape(ellipse_pts(0, 0, r, r, 24), "#ffe3ea", "", w=4, seed=8100)
    c = lib.clip_rect(-r, -r, 2 * r, 2 * r, r)
    o += f'<g clip-path="url(#{c})">' + PR.brain_kid(0, r * 1.2, r / 150, expr, 0, t, seed=1) + "</g>"
    o += line(ellipse_pts(0, 0, r, r, 24) + [ellipse_pts(0, 0, r, r, 24)[0]], 5, "#111", taper=0, wmin=1, seed=8101)
    return tf(o, x, y)


def review(x, y, k, n_on, lines, t=0.0, u=1.0, star_u=None, expr="calm", line_u=None, ticks=None):
    """Карточка отзыва 860×(220+70·строк) (центр): аватар-мозг, звёзды, текст отзыва."""
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.0) if u < 1 else 1.0
    h = 200 + 74 * len(lines)
    o = blob(lib.rrect(-430 + 14, -h / 2 + 18, 430 + 14, h / 2 + 18, 40), "#000000", .18)
    o += shape(lib.rrect(-430, -h / 2, 430, h / 2, 40), "#ffffff", "", w=6, seed=8200)
    o += avatar(-330, -h / 2 + 100, 64, t, expr)
    o += stars(-20, -h / 2 + 100, 40, n_on, star_u)
    for j, ln in enumerate(lines):
        lu = 1.0 if line_u is None else line_u[j]
        if lu <= 0:
            continue
        c = lib.clip_rect(-400, -h / 2 + 170 + 74 * j, 800 * clamp(lu) + 10, 80)
        o += f'<g clip-path="url(#{c})">' + plain(ln, -380, -h / 2 + 230 + 74 * j, 56, fill=INK2) + "</g>"
        if ticks and ticks[j] > 0:
            o += PR.check_mark(330, -h / 2 + 210 + 74 * j, .8, ticks[j], col=GREEN, w=10)
    return tf(o, x, y, k * s)


def product(x, y, k, t, n_on=1, star_u=None, expr="scared", hop=0.0, glow_=0.0):
    """Карточка товара «МОЙ МОЗГ»: фото — мозг-малыш, название, звёзды."""
    o = blob(lib.rrect(-400 + 16, -520 + 20, 400 + 16, 520 + 20, 46), "#000000", .2)
    inner = rect(-400, -520, 400, 160, "#fdeef2")
    if glow_ > 0:
        inner += PR.glow(0, -170, 380, glow_, "#fff1b0")
    inner += PR.brain_kid(0, 120, 1.25, expr, hop, t, seed=2)
    o += shape(lib.rrect(-400, -520, 400, 520, 46), "#ffffff", inner, w=6, seed=8300)
    o += line([(-400, 160), (400, 160)], 4, "#111", taper=0, wmin=1, seed=8301)
    o += text("МОЙ МОЗГ", -350, 270, 84, fill=INK2, stroke="#ffffff", sw=.01, anchor="start")
    o += stars(-110, 390, 46, n_on, star_u, gap=104)
    return tf(o, x, y, k)


def shop_bg(t):
    o = [rect(-1400, -1400, 2600, 3400, SHOP)]
    for j in range(-10, 24):
        o.append(blob(ellipse_pts(j * 120 + 60 * (j % 2), 200 + (j * 337) % 1700, 6, 6, 8), "#d3dae8", .9))
    return o


def vshop(o, cx, cy, s, t, dx=0.0, dy=0.0):
    return view("".join(o), cx + dx, cy + dy, s, 0, bg=SHOP, t=t)


def room(t):
    return [plain_room(t), rug(540, RFL + 160, 560)]


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: Дима на диване с телефоном, глаза круглые; перед ним вылетает карточка отзыва с одной звездой; кот выглядывает."""
    tl = HIT
    o = room(t)
    sf = RM.sofa(540, RFL, 1.0)
    o.append(sf["back"])
    x, k = 420.0, .66
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    f = people.dima82(x, RFL - 314, k, "wow82", "sit_desk", t=t, feet=feet, lean_add=-.1, arms={"n": ("ik", (x + 170, RFL - 520), -1)})
    o.append(f["svg"])
    o.append(mini_phone(x + 175, RFL - 540, .45, -15, screen="#9cc3ef"))
    o.append(PR.glow(x + 175, RFL - 540, 200, .5, "#cfe3ff"))
    o.append(sf["arm_r"])
    u = ease_out(ramp(t, -.25, tl + .25))
    o.append(review(540, 1250 + 300 * (1 - u), 1.15 * (.5 + .5 * u), 1, ["Обещал отчёт,", "сделал полку."], t, u=1.0, expr="scared",
                    star_u=[ramp(t, tl, .2)]))
    o.append(cat(880, 1250 + 300 * (1 - u) - 200 * 1.15 * (.5 + .5 * u), .5, t, dict(look=(-.8, .3), perk=1.0, smug=.4)))
    o.append(PR.sparkles(300, 1130, 1.6, bump(t, tl, .05, .4), t, seed=11, n=5, r=120))
    dx, dy = shake(t, tl, 12)
    return hook_view("".join(o), t, HIT, 560, 1080, 1.05, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«о своём мозге!»: карточка товара «МОЙ МОЗГ» — мозг-малыш испуган, одна звезда из пяти."""
    a, b = T0("s02"), T1("s02")
    o = shop_bg(t)
    o.append(product(540, 960, .92, t, 1, [ramp(t, W(4) - .1, .25)], "scared"))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(4), 9)
    return vshop(o, 540, 1000, 1.02 + .06 * uu, t, dx, dy)


def frame_s03(t):
    """«Одна звезда:»: карточка первого отзыва, звезда загорается."""
    a, b = T0("s03"), T1("s03")
    o = shop_bg(t)
    o.append(product(540, 1150, .5, t, 1, expr="scared"))
    o.append(review(540, 720, 1.05, 1, ["Обещал отчёт,", "сделал полку."], t, u=pop(t, a - .05, .3), star_u=[ramp(t, W(5), .25)], expr="scared"))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(6), 8)
    return vshop(o, 540, 980, 1.02 + .05 * uu, t, dx, dy)


def folder(x, y, k, label="ОТЧЁТ", rot=0.0, web=0.0):
    o = shape([(-170, -120, 1), (-60, -120, 1), (-40, -150, 1), (60, -150, 1), (80, -120, 1), (170, -120, 1), (170, 120, 1), (-170, 120, 1)],
              "#f2c14e", "", w=5, seed=8400)
    o += text(label, 0, 22, 66, fill=INK2, stroke="#f2c14e", sw=.01)
    o = tf(o, x, y, k, rot)
    if web > 0:
        o += PR.cobweb(x - 150 * k, y - 120 * k, .9 * k, seed=3)
    return o


def frame_s04(t):
    """«обещал отчёт»: стол, на ноутбуке пустой лист, папка «ОТЧЁТ»; Дима обещающе машет, кот смотрит."""
    a, b = T0("s04"), T1("s04")
    o = desk_room(t)
    lap = shape([(-380, -6, 1), (380, -6, 1), (400, 26, 1), (-400, 26, 1)], "#9aa0aa", "", w=4, seed=4500)
    lap += shape(lib.rrect(-340, -470, 340, -6, 22), "#2a2d36", "", w=5, seed=4501) + tf(rect(-310, -200, 310, 200, "#ffffff"), 0, -238)
    o.append(tf(lap, 690, DESK_Y - 6, .5))
    o.append(folder(905, DESK_Y - 56, .32))
    f = dima_desk(t, "proud82", lean=-.05)
    o.append(f["svg"])
    o.append(cat(560, FL, .42, t, dict(look=(.8, -.6), smug=.4)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(8), 6)
    return view("".join(o), 620 + dx, 860 + dy, 1.45 + .05 * uu, 0, t=t)


def wall_shelf(x, y, k, cat_on=True, t=0.0):
    o = shape(lib.rrect(-260, -18, 260, 18, 6), "#a8774a", "", w=4, seed=8500)
    for s_ in (-1, 1):
        o += shape([(s_ * 180 - 10, 18, 1), (s_ * 180 + 10, 18, 1), (s_ * 180 + 10, 80, 1), (s_ * 180 - 50 * s_, 18, 1)], "#5a5f6e", "", w=3, seed=8501 + s_)
    return tf(o, x, y, k)


def drill(x, y, k, rot=0.0, spin=0.0):
    o = shape(lib.rrect(-90, -40, 60, 40, 16), "#e2453a", "", w=4, seed=8600)
    o += shape([(-40, 30, 1), (0, 30, 1), (10, 140, 1), (-50, 140, 1)], "#2a2d36", "", w=4, seed=8601)
    o += shape(lib.rect_pts(60, -12, 110, 12), "#9aa0aa", "", w=3, seed=8602)
    o += line([(110, 0), (170, 0)], 8, "#5a5f6e", taper=0, wmin=1, seed=8603)
    o += line([(120, -6 + 6 * math.sin(spin)), (160, 6 - 6 * math.sin(spin))], 3, "#ffffff", seed=8604)
    return tf(o, x, y, k, rot)


def frame_s05(t):
    """«сделал полку»: Дима с дрелью гордо у новой полки, кот уже сидит на полке; папка «ОТЧЁТ» брошена в паутине."""
    a, b = T0("s05"), T1("s05")
    tp = W(10)
    o = room(t)
    o.append(wall_shelf(700, 960, 1.0))
    o.append(cat(700, 944, .55, t, dict(look=(-.7, .5), smile=1.0, perk=1.0)) if t > tp - .1 else "")
    o.append(PR.sparkles(700, 900, 1.6, bump(t, tp, .05, .5), t, seed=51, n=6, r=220))
    f = stand(330, t, "proud82" if t > tp else "focus", "d82_hold")
    o.append(f["svg"])
    hx, hy = f["hold_f"]
    o.append(drill(hx, hy - 20, .7, -10, t * 80))
    o.append(folder(900, RFL - 120, .6, rot=-8, web=1.0))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tp, 8)
    return view("".join(o), 580 + dx, 1060 + dy, 1.12 + .05 * uu, 0, t=t)


def frame_s06(t):
    """«Одна звезда:»: второй отзыв."""
    a, b = T0("s06"), T1("s06")
    o = shop_bg(t)
    o.append(review(540, 1170, .92, 1, ["Обещал отчёт,", "сделал полку."], t, expr="scared"))
    o.append(review(540, 720, 1.15, 1, ["Купил ежедневник", "и ни разу не открыл."], t, u=pop(t, a - .05, .3), star_u=[ramp(t, W(11), .25)], expr="wide"))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(12), 8)
    return vshop(o, 540, 960, 1.02 + .05 * uu, t, dx, dy)


def planner(x, y, k, rot=0.0, dust=0.0, glow_=0.0, t=0.0):
    o = ""
    if glow_ > 0:
        o += PR.glow(0, 0, 260, glow_, "#fff1b0")
    o += shape(lib.rrect(-150, -200, 150, 200, 18), "#2f6fd1", "", w=5, seed=8700)
    o += shape(lib.rect_pts(-150, -200, -110, 200), "#1f4f9e", "", w=3, seed=8701)
    o += shape(lib.rrect(-60, -120, 110, -40, 10), "#ffffff", "", w=3, seed=8702)
    o += line([(110, -40), (170, -40)], 8, "#e2453a", taper=0, wmin=1, seed=8703)
    if dust > 0:
        for j in range(14):
            o += blob(ellipse_pts(-130 + (j * 47) % 260, -190 + (j * 83) % 380, 10, 6, 8), "#b8ad98", .8 * dust)
    o = tf(o, x, y, k, rot)
    if dust > 0:
        o += PR.cobweb(x + 150 * k, y - 200 * k, 1.1 * k, seed=5, ang=90)
    return o


def frame_s07(t):
    """«купил ежедневник»: Дима держит новенький ежедневник, сияет; кот с интересом смотрит."""
    a, b = T0("s07"), T1("s07")
    o = room(t)
    f = stand(380, t, "laugh82", "d82_hold")
    o.append(f["svg"])
    hx, hy = f["hold_f"]
    o.append(planner(hx + 120, hy + 30, .55, -8, glow_=.6))
    o.append(PR.sparkles(hx + 120, hy + 30, 1.6, bump(t, W(14) - .1, .05, .5), t, seed=71, n=6, r=200))
    o.append(cat(860, RFL, .75, t, dict(look=(-.8, -.6), smile=.6, perk=1.0)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(14), 6)
    return view("".join(o), 580 + dx, 1050 + dy, 1.15 + .05 * uu, 0, t=t)


def frame_s08(t):
    """«и ни разу не открыл»: ежедневник крупно на полке в пыли и паутине, кот сдувает пыль; плашка «0»."""
    a, b = T0("s08"), T1("s08")
    d = ramp(t, a - .3, b - a)
    o = room(t)
    o.append(wall_shelf(540, 1240, 1.6))
    o.append(planner(540, 900, 1.5, 0, dust=.5 + .5 * d))
    o.append(cat(820, RFL, .85, t, dict(look=(-.7, -.8), smug=.6, tilt=-8)))
    for j in range(6):
        u = ((t - a) * 1.4 + j / 6) % 1
        o.append(blob(ellipse_pts(420 + 50 * j + 30 * u, 600 + 900 * u, 8, 6, 8), "#b8ad98", .8 * (1 - u)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(19), 6)
    return view("".join(o), 540 + dx, 1050 + dy, 1.05 + .06 * uu, 0, t=t)


def frame_s09(t):
    """«Одна звезда:»: третий отзыв."""
    a, b = T0("s09"), T1("s09")
    o = shop_bg(t)
    o.append(review(540, 1170, .92, 1, ["Купил ежедневник", "и ни разу не открыл."], t, expr="wide"))
    o.append(review(540, 720, 1.15, 1, ["Сказал «я на секундочку»,", "вернулся через два часа."], t, u=pop(t, a - .05, .3),
                    star_u=[ramp(t, W(20), .25)], expr="peek"))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(21), 8)
    return vshop(o, 540, 980, 1.02 + .05 * uu, t, dx, dy)


def frame_s10(t):
    """«сказал „я на секундочку“»: Дима за столом берёт телефон, пузырь «я на секундочку»; кот прищурился."""
    a, b = T0("s10"), T1("s10")
    o = desk_room(t)
    o.append(PR.desk(680, DESK_Y, w=660, depth=100, leg_h=260, seed=7))
    o.append(folder(760, DESK_Y - 90, .5))
    reach = ease_io(ramp(t, a, .5))
    f = dima_desk(t, "sly", lean=-.05, arms={"n": ("ik", (500 + 30 * reach, DESK_Y - 120 - 80 * reach), -1)})
    o.append(f["svg"])
    o.append(mini_phone(510 + 30 * reach, DESK_Y - 150 - 80 * reach, .4, -10, screen="#9cc3ef"))
    mx, my = f["mouth"]
    u = pop(t, W(23) - .1, .25)
    o.append(PR.speech_bubble(mx + 230, my - 200, 470, 170, u, seed=3, tail=(-170, 50)))
    if u > 0:
        o.append(tf(text("я на секундочку", 0, 18, 50, fill=INK2, stroke="#ffffff", sw=.01), mx + 230, my - 200, u))
    o.append(cat(930, DESK_Y - 4, .42, t, dict(look=(-.9, -.3), smug=.9)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(25), 6)
    return view("".join(o), 620 + dx, 840 + dy, 1.45 + .05 * uu, 0, t=t)


def frame_s11(t):
    """«вернулся через два часа»: настенные часы — стрелки летят на два часа вперёд, плашка «+2 ЧАСА»; Дима виновато возвращается."""
    a, b = T0("s11"), T1("s11")
    sp = ease_io(ramp(t, a, W(29) - a + .1))
    o = room(t)
    o.append(PR.clock(730, 720, 200, angle_h=60 * sp + 300, angle_m=720 * sp, seed=2))
    o.append(red_plate("2 ЧАСА", 730, 1030, pop(t, W(28) - .1, .25), w=440))
    f = stand(260, t, "guilty", "d82_rest")
    o.append(f["svg"])
    o.append(mini_phone(f["hold_f"][0], f["hold_f"][1], .3, 10, screen="#9cc3ef"))
    o.append(cat(880, RFL, .75, t, dict(look=(-.8, -.5), smug=.7, tail=12 * math.sin(t * 4))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(28), 8)
    return view("".join(o), 540 + dx, 1050 + dy, 1.05 + .05 * uu, 0, t=t)


def red_plate(s, x, y, u, w=520):
    if u <= 0:
        return ""
    return tf(shape(lib.rrect(-w / 2, -70, w / 2, 70, 30), RED, "", w=5, seed=4600)
              + text(s, 0, 28, 84, fill="#ffffff", stroke="#7a1e18", sw=6), x, y, u)


def frame_s12(t):
    """«А потом я стал начинать с двух минут»: на столе таймер 2:00 звенит, Дима открывает ноутбук и начинает печатать."""
    a, b = T0("s12"), T1("s12")
    tm = W(36)
    o = desk_room(t, sun=1.0)
    lap = shape([(-380, -6, 1), (380, -6, 1), (400, 26, 1), (-400, 26, 1)], "#9aa0aa", "", w=4, seed=4500)
    scr = rect(-310, -200, 310, 200, "#ffffff") + "".join(line([(-260, -150 + 50 * j), (-260 + 480 * clamp((t - tm) * 1.5 - j * .3), -150 + 50 * j)],
                                                               9, INK2, taper=.1, wmin=.8, seed=8800 + j) for j in range(4))
    lap += shape(lib.rrect(-340, -470, 340, -6, 22), "#2a2d36", "", w=5, seed=4501) + tf(scr, 0, -238)
    o.append(tf(lap, 680, DESK_Y - 6, .6))
    o.append(PR.bell_timer(905, DESK_Y - 4, .42, hand_a=360 * ramp(t, tm, 30), sector_u=.033, ring=bump(t, tm, .05, .5), t=t))
    o.append(tf(shape(lib.rrect(-180, -50, 180, 50, 24), GREEN, "", w=4, seed=8810)
                + text("2 МИНУТЫ", 0, 20, 54, fill="#ffffff", stroke="#1e5a32", sw=5), 800, DESK_Y - 520, pop(t, tm - .1, .25)))
    f = dima_desk(t, "focus_smile", lean=.18, arms={"f": ("ik", (600, DESK_Y - 30), 1), "n": ("ik", (680, DESK_Y - 25), 1)})
    o.append(f["svg"])
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tm, 7)
    return view("".join(o), 640 + dx, 840 + dy, 1.4 + .05 * uu, 0, t=t)


def frame_s13(t):
    """«и котик сидел рядом»: кот запрыгивает на стол и садится рядом с Димой, мурлычет сердечками; Дима печатает."""
    a, b = T0("s13"), T1("s13")
    j = ease_out(ramp(t, a - .15, .45))
    o = desk_room(t, sun=1.0)
    lap = shape([(-380, -6, 1), (380, -6, 1), (400, 26, 1), (-400, 26, 1)], "#9aa0aa", "", w=4, seed=4500)
    scr = rect(-310, -200, 310, 200, "#ffffff") + "".join(line([(-260, -150 + 50 * q), (220, -150 + 50 * q)], 9, INK2, taper=.1, wmin=.8, seed=8800 + q)
                                                          for q in range(5))
    lap += shape(lib.rrect(-340, -470, 340, -6, 22), "#2a2d36", "", w=5, seed=4501) + tf(scr, 0, -238)
    o.append(tf(lap, 700, DESK_Y - 6, .6))
    f = dima_desk(t, "calm_smile", lean=.18, arms={"f": ("ik", (560, DESK_Y - 30), 1), "n": ("ik", (640, DESK_Y - 25), 1)})
    o.append(f["svg"])
    o.append(cat(1100 - 170 * j, DESK_Y - 4 + 300 * (1 - j) - 200 * math.sin(math.pi * j), .5, t,
                 dict(look=(-.9, -.2), smile=1.0, legs=1 - j, perk=1.0, tail=10 * math.sin(t * 3))))
    for q in range(3):
        u = ((t - a) * .9 + q / 3) % 1
        o.append(PR.heart(930 + 40 * math.sin(u * 6 + q), DESK_Y - 260 - 260 * u, .5 * (1 - u * .5), seed=q) if j >= 1 else "")
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 680, 840, 1.45 + .05 * uu, 0, t=t)


def frame_s14(t):
    """«Новый отзыв: пять звёзд»: новая карточка, пять звёзд загораются одна за другой; мозг-аватар счастлив."""
    a, b = T0("s14"), T1("s14")
    ts = W(44)
    su = [ramp(t, ts - .2 + .12 * i, .2) for i in range(5)]
    o = shop_bg(t)
    o.append(review(540, 760, 1.1, 5, [], t, u=pop(t, a - .05, .3), star_u=su, expr="calm"))
    o.append(PR.brain_kid(540, 1330, 1.3, "calm", -50 * abs(math.sin((t - ts) * 7)) if t > ts else 0.0, t, seed=2))
    o.append(PR.sparkles(540, 700, 2.2, bump(t, ts + .4, .05, .6), t, seed=141, n=8, r=420))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts + .4, 9)
    return vshop(o, 540, 980, 1.0 + .05 * uu, t, dx, dy)


def frame_s15(t):
    """«Начинает быстро, дела закрывает»: строки отзыва дописываются, у каждой галочка."""
    a, b = T0("s15"), T1("s15")
    l1 = ramp(t, a - .1, WE(47) - a + .1)
    l2 = ramp(t, W(48) - .1, WE(49) - W(48) + .1)
    o = shop_bg(t)
    o.append(review(540, 760, 1.1, 5, ["Начинает быстро,", "дела закрывает."], t, expr="calm", line_u=[l1, l2],
                    ticks=[ramp(t, WE(47) - .1, .2), ramp(t, WE(49) - .1, .2)]))
    o.append(folder(420, 1170, .8, "ДЕЛО"))
    o.append(PR.brain_kid(760, 1330, .95, "calm", 0.0, t, seed=2))
    o.append(tf(shape(ellipse_pts(0, 0, 90, 90, 20), GREEN, "", w=4, seed=8900) + PR.check_mark(-26, 12, 1.3, 1.0, col="#ffffff", w=14), 540, 1240,
                pop(t, WE(49) - .1, .25)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, WE(49), 7)
    return vshop(o, 540, 1000, 1.0 + .05 * uu, t, dx, dy)


def frame_s16(t):
    """«кот рекомендует»: кот запрыгивает к карточке и ставит отпечаток лапы, печать «КОТ РЕКОМЕНДУЕТ»."""
    a, b = T0("s16"), T1("s16")
    tp = W(51)
    o = shop_bg(t)
    o.append(review(540, 740, 1.1, 5, ["Начинает быстро,", "дела закрывает."], t, expr="calm", ticks=[1, 1]))
    su = pop(t, tp - .05, .25)
    if su > 0:
        stamp = shape(lib.rrect(-300, -80, 300, 80, 30), "#ffffff", "", w=7, seed=9000)
        stamp += line(lib.rrect(-286, -66, 286, 66, 24) + [lib.rrect(-286, -66, 286, 66, 24)[0]], 5, RED, taper=0, wmin=1, seed=9001)
        stamp += text("КОТ РЕКОМЕНДУЕТ", 0, 22, 62, fill=RED, stroke="#ffffff", sw=.01)
        o.append(tf(stamp, 500, 1110, su * 1.2, -6))
    o.append(cat(790, 1640, 1.2, t, dict(look=(-.7, -.8), smile=1.0, perk=1.0, paw=bump(t, tp - .25, .15, .5), paw_dx=-100)))
    o.append(PR.sparkles(560, 1140, 1.8, bump(t, tp, .05, .5), t, seed=161, n=6, r=330))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tp, 10)
    return vshop(o, 540, 1080, 1.0 + .05 * uu, t, dx, dy)


def frame_s17(t):
    return cta_code(t, T0("s17"), T1("s17"))


def frame_s18(t):
    """«чтобы твой мозг тоже получил пять звёзд»: карточка товара «МОЙ МОЗГ» — пять звёзд, мозг-малыш подпрыгивает от радости."""
    a, b = T0("s18"), T1("s18")
    ts = W(60)
    su = [1.0] + [ramp(t, ts - .25 + .1 * i, .2) for i in range(4)]
    o = shop_bg(t)
    hop = -60 * abs(math.sin((t - a) * 6)) if t > ts else 0.0
    o.append(product(540, 960, .92, t, 5, su, "calm", hop=hop, glow_=.6))
    o.append(cat(900, 1700, .8, t, dict(look=(-.7, -.8), smile=1.0, perk=1.0, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(540, 900, 2.2, bump(t, ts + .3, .05, .6), t, seed=181, n=8, r=420))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts + .3, 8)
    return vshop(o, 540, 1080, 1.0 + .05 * uu, t, dx, dy)


def frame_s19(t):
    """Петля: кадр хука — Дима на диване с телефоном, карточка отзыва с одной звездой."""
    a, b = T0("s19"), T1("s19")
    o = room(t)
    sf = RM.sofa(540, RFL, 1.0)
    o.append(sf["back"])
    x, k = 420.0, .66
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    f = people.dima82(x, RFL - 314, k, "calm82", "sit_desk", t=t, feet=feet, lean_add=-.1, arms={"n": ("ik", (x + 170, RFL - 520), -1)})
    o.append(f["svg"])
    o.append(mini_phone(x + 175, RFL - 540, .45, -15, screen="#9cc3ef"))
    o.append(sf["arm_r"])
    o.append(review(540, 1250, 1.15, 1, ["Обещал отчёт,", "сделал полку."], t, expr="scared"))
    o.append(cat(880, 1020, .5, t, dict(look=(-.8, .3), perk=1.0, smug=.4)))
    return loop_view("".join(o), t, a, b, HIT, 560, 1080, 1.05)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
