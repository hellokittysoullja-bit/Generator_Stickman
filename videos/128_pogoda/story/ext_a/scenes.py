"""Рилс 128 «Прогноз погоды в голове», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920.
Говорит кот-синоптик (Даниил). Студия прогноза: большой экран-карта — силуэт головы, на нём туман, ураган, штиль, ливень.
Кот в строгом сером пиджаке с белой рубашкой и синим галстуком (рисуется на туловище внутри cat.body — двигается вместе
с котом в прыжке, повороте и дыхании), в лапе указка. Сцены дня — Дима (туман с одной мыслью про кофе, ураган вкладок,
штиль на диване, ночной ливень). Призыв — печатное жёлтое «КОТ». NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402
import room as RM  # noqa: E402
import costume as COS  # noqa: E402

COS.use("forecast")          # костюм синоптика во всех планах, включая призыв (cta_code)
COS.POINTER["on"] = False

HIT = stress(1, .4)
INK2 = "#1d2448"
STUDIO = "#2a3550"
SFL = 1560.0


# ═════════════ кот-синоптик ═════════════
def wcat(x, y, k, t, st=None, point=0.0, target=None):
    """Кот-синоптик: костюм и указка — costume.use("forecast") (рисуются внутри групп кота). point 0…1 — правая (от зрителя)
    лапа поднята; target — куда смотрит указка (мир). Кот стоит слева от экрана, указка идёт вправо."""
    st = dict(dict(look=(.5, -.2), smile=.6, tail=8 * math.sin(t * 1.7)), **(st or {}))
    p = max(.25, point)
    st["paw"] = p
    st.setdefault("paw_dx", 90.0)
    rot = st.get("rot", 0.0)
    lx, ly = CT.CX + 25 + st["paw_dx"] * p * 1.6, 1306 - 150 * p
    tip = (x + (lx - CT.CX) * k, y + (ly - CT.CBOT) * k)
    if target is None:
        target = (tip[0] + 260 * k, tip[1] - 160 * k)
    COS.POINTER["ang"] = math.degrees(math.atan2(target[1] - tip[1], target[0] - tip[0])) - rot
    COS.POINTER["on"] = True
    o = cat(x, y, k, t, st)
    COS.POINTER["on"] = False
    return o


# ═════════════ карта-голова ═════════════
HEAD = [(-250, 330), (-300, 200), (-330, 40), (-320, -120), (-260, -250), (-150, -330), (0, -360), (140, -330), (240, -260),
        (290, -150), (300, -40), (350, 40), (330, 70), (300, 80), (310, 130), (290, 160), (300, 200), (270, 230), (200, 240),
        (180, 330)]


def head_shape(fill="#bfe3f2", inner=""):
    return shape([(x_, y_, 1) for x_, y_ in HEAD], fill, inner, w=7, seed=7100)


def fog(t, u=1.0, seed=0):
    o = ""
    for j in range(5):
        y_ = -240 + 120 * j
        dx = 30 * math.sin(t * 1.3 + j)
        o += blob(lib.rrect(-380 + dx, y_ - 40, 380 + dx, y_ + 40, 40), "#ffffff", .7 * u)
        o += line([(-300 + dx, y_), (300 + dx, y_ + 10 * math.sin(j))], 6, "#c9d0d8", taper=.3, wmin=.4, seed=7200 + j + seed, op=u)
    return o


def hurricane(t, u=1.0, spin=None, scale=1.0):
    if u <= 0:
        return ""
    sp = (t * 300) if spin is None else spin
    o = ""
    for j in range(3):
        pts = [((30 + 26 * q) * math.cos(math.radians(sp + 120 * j + 22 * q)) * scale,
                (30 + 26 * q) * math.sin(math.radians(sp + 120 * j + 22 * q)) * .8 * scale) for q in range(10)]
        o += line(pts, 22 * scale, "#6b7a90", taper=.6, wmin=.3, seed=7300 + j, op=u)
    o += blob(ellipse_pts(0, 0, 26 * scale, 22 * scale, 12), "#3d4a5e", u)
    return o


def map_board(x, y, k, t, mode="mix", u=1.0, flash=0.0, timer=0.0, calm=0.0):
    """Экран прогноза (центр): рамка, синий фон с сеткой, голова-карта. mode: mix (облака, молния, солнце), fog, storm,
    calm (солнце и штиль), night (луна, туча, ливень), clear (солнце и радуга)."""
    o = blob(lib.rect_pts(-430 + 16, -520 + 18, 430 + 16, 520 + 18), "#000000", .25)
    bg = rect(-430, -520, 430, 520, "#2d5f9e")
    for j in range(-4, 5):
        bg += line([(-430, 110 * j), (430, 110 * j)], 2, "#4a7cbb", taper=0, wmin=1, seed=7400 + j)
        bg += line([(100 * j, -520), (100 * j, 520)], 2, "#4a7cbb", taper=0, wmin=1, seed=7420 + j)
    o += shape(lib.rect_pts(-430, -520, 430, 520), "#2d5f9e", bg, w=8, seed=7440)
    inner = ""
    fill = "#bfe3f2"
    if mode == "night":
        fill = "#2b3a66"
    if mode == "fog":
        fill = "#d9dee4"
    hd = head_shape(fill)
    if mode == "mix":
        hd += PR.sun(150, -170, 70, 1.0, t, seed=1)
        hd += PR.cloud(-90, -40, 260, 160, seed=2)
        hd += PR.storm(60, 170, 300, 150, seed=3, flash=flash)
        hd += PR.bolt(40, 170, 0, 300, u=.5 if flash > .1 else 0.0, w=30, seed=4)
    elif mode == "fog":
        hd += fog(t, u)
        if timer > 0:
            hd += PR.glow(0, 0, 260 * timer, .8, "#fff1b0")
            hd += blob(ellipse_pts(0, 0, 190 * timer, 160 * timer, 30), "#bfe3f2", min(1.0, timer * 1.3))
            hd += PR.bell_timer(0, 60, .9 * min(1.0, timer * 1.5), 0, .03, 0.0, t)
    elif mode == "storm":
        hd += hurricane(t, u, scale=1.6 * (1 - .7 * calm) + .01)
        if calm > 0:
            hd += PR.sun(0, -60, 90 * calm, calm, t, seed=5)
        for j in range(5):
            a_ = t * 4 + j * 1.25
            hd += PR.flying_sheet(170 * math.cos(a_), 150 * math.sin(a_), .55, a_ * 60, seed=j, flap=a_) if calm < .5 else ""
    elif mode == "calm":
        hd += PR.sun(80, -150, 90, 1.0, t, seed=6)
        hd += line([(-260, 120), (260, 120)], 8, "#5a8fc8", taper=0, wmin=1, seed=7450)
        hd += RM.sofa(0, 260, .32)["back"] if hasattr(RM, "sofa") else ""
    elif mode == "night":
        hd += PR.moon(150, -200, 44)
        hd += PR.storm(-40, -20, 380, 170, seed=7, flash=flash)
        for j in range(9):
            yy = (t * 700 + j * 97) % 300
            hd += line([(-200 + 50 * j, 20 + yy), (-212 + 50 * j, 60 + yy)], 7, "#8fc8ff", seed=7460 + j)
        hd += PR.bolt(-20, -10, -80, 200, u=.5 if flash > .1 else 0.0, w=30, seed=8)
    elif mode == "clear":
        for j, col in enumerate(("#e2453a", "#f2a33a", "#f6d24a", "#5cb85c", "#3f8fe0")):
            r_ = 250 - 22 * j
            pts = [(r_ * math.cos(math.radians(a_)) - 20, r_ * math.sin(math.radians(a_)) + 160) for a_ in range(190, 351, 8)]
            hd += line(pts, 20, col, taper=0, wmin=1, seed=7470 + j)
        hd += PR.sun(0, -120, 100, 1.0, t, seed=9)
    o += hd
    return tf(o, x, y, k * u)


def studio(t):
    o = [rect(-1400, -1400, 2600, SFL, STUDIO)]
    for j in range(-6, 12):
        o.append(rect(j * 160, -1400, j * 160 + 6, SFL, "#334063"))
    o.append(rect(-1400, SFL, 2600, SFL + 1400, "#1c2338"))
    for j in range(1, 8):
        o.append(line([(-1400, SFL + 60 * j * j * .6), (2600, SFL + 60 * j * j * .6)], 3, "#2b3552", taper=0, wmin=1, seed=12 + j))
    o.append(blob(ellipse_pts(470, SFL + 200, 520, 90, 30), "#3b5a8e", .35))
    o.append(blob(ellipse_pts(210, SFL + 20, 260, 40, 24), "#000000", .25))
    o.append(line([(-1400, SFL), (2600, SFL)], 5, "#0e1220", seed=11))
    o.append(PR.glow(540, 200, 700, .25, "#9fc5ff"))
    return o


def vstudio(o, cx, cy, s, t, dx=0.0, dy=0.0):
    return view("".join(o), cx + dx, cy + dy, s, 0, bg=STUDIO, t=t)


def label(s, x, y, u, col="#FFD23F", size=72, w=None):
    if u <= 0:
        return ""
    w = w or (len(s) * size * .62 + 80)
    return tf(shape(lib.rrect(-w / 2, -62, w / 2, 62, 26), col, "", w=5, seed=7500) + text(s, 0, 26, size, fill="#111", stroke="#111", sw=.01),
              x, y, u, -2)


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: студия прогноза, большой экран-голова с солнцем, облаком и тучей; кот-синоптик тычет указкой — бьёт молния."""
    tl = HIT
    fl = bump(t, tl, .03, .25)
    o = stage(t, "mix", dict(smile=.7), point=.3 + .5 * ease_out(ramp(t, -.2, tl + .2)), ck=1.3, cx=200, bx=650, by=1120, bk=.95, flash=fl)
    o.append(PR.sparkles(600, 1060, 1.6, fl, t, seed=11, n=6, r=150))
    if fl > 0:
        o.append(rect(-1400, -1400, 2600, 3400, "#ffffff", .25 * fl))
    dx, dy = shake(t, tl, 12)
    return hook_view("".join(o), t, HIT, 560, 1120, 1.0, 0, bg=STUDIO, dx=dx, dy=dy)


def frame_s02(t):
    """«в моей голове»: экран-голова крупно, значки погоды выскакивают по очереди, молния."""
    a, b = T0("s02"), T1("s02")
    o = studio(t)
    o.append(map_board(540, 980, 1.0, t, "mix", flash=bump(t, W(4), .03, .3)))
    o.append(PR.sparkles(540, 900, 2.0, bump(t, W(4), .05, .5), t, seed=21, n=7, r=380))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(4), 8)
    return vstudio(o, 540, 1000, 1.12 + .06 * uu, t, dx, dy)


def frame_s03(t):
    """«на сегодня!»: кот-синоптик крупно у экрана, указка вверх; плашка «СЕГОДНЯ»."""
    a, b = T0("s03"), T1("s03")
    o = stage(t, "mix", dict(look=(0, -.1), smile=1.0), point=.7, ck=1.6, cx=330, bx=800, by=820, bk=.62)
    o.append(label("СЕГОДНЯ", 540, 1640, pop(t, W(6) - .1, .25)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(6), 8)
    return vstudio(o, 560, 1180, 1.0 + .05 * uu, t, dx, dy)


def frame_s04(t):
    """«Утром густой туман»: голова на экране затянута туманом, кот показывает указкой; плашка «УТРОМ»."""
    a, b = T0("s04"), T1("s04")
    o = stage(t, "fog", dict(smile=.2), point=.6)
    o.append(label("УТРОМ", 700, 500, pop(t, a - .05, .25)))
    uu = ease_io(ramp(t, a, b - a))
    return vstudio(o, 540, 1060, 1.0 + .05 * uu, t)


def fog_layer(t, u=1.0):
    o = ""
    for j in range(6):
        y_ = 500 + 220 * j
        dx = 60 * math.sin(t * .9 + j * 1.7)
        o += blob(lib.rrect(-600 + dx, y_ - 70, 1700 + dx, y_ + 70, 70), "#ffffff", .5 * u)
    return o


def frame_s05(t):
    """«Видимость одна мысль»: утро в тумане, Дима сонный стоит, над ним одно маленькое облачко-мысль, пока пустое."""
    a, b = T0("s05"), T1("s05")
    o = [plain_room(t), rug(540, RFL + 160, 560)]
    o.append(fog_layer(t))
    f = stand(520, t, "sleepy", "d82_rest")
    o.append(f["svg"])
    tx_, ty_ = f["temple"]
    o.append(PR.thought_cloud(tx_ + 200, ty_ - 230, 1.0, 300, 220, pop(t, W(11) - .1, .3), seed=2,
                              inner=text("1", 0, 30, 110, fill=INK2, stroke="#ffffff", sw=.01)))
    o.append(rect(-1400, -1400, 2600, 3400, "#ffffff", .16))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(12), 6)
    return view("".join(o), 560 + dx, 1060 + dy, 1.15 + .05 * uu, 0, t=t)


def frame_s06(t):
    """«и та про кофе»: в облаке — кружка кофе с паром, Дима тянется к ней, туман вокруг."""
    a, b = T0("s06"), T1("s06")
    o = [plain_room(t), rug(540, RFL + 160, 560)]
    o.append(fog_layer(t))
    f = stand(500, t, "sleepy", "d82_hold")
    o.append(f["svg"])
    tx_, ty_ = f["temple"]
    o.append(PR.thought_cloud(tx_ + 200, ty_ - 230, 1.0, 320, 240, 1.0, seed=2,
                              inner=PR.coffee_mug(0, 60, 1.0, steam=1.0, t=t, seed=1) if t > W(16) - .15 else text("1", 0, 30, 110, fill=INK2, stroke="#ffffff", sw=.01)))
    o.append(PR.sparkles(tx_ + 200, ty_ - 230, 1.2, bump(t, W(16) - .1, .05, .5), t, seed=61, n=5, r=160))
    o.append(rect(-1400, -1400, 2600, 3400, "#ffffff", .16))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(16), 7)
    return view("".join(o), 600 + dx, 960 + dy, 1.2 + .06 * uu, 0, t=t)


def frame_s07(t):
    """«К обеду ураган из сорока дел»: на экране-голове крутится ураган, листы летают; плашка «40 ДЕЛ»."""
    a, b = T0("s07"), T1("s07")
    o = stage(t, "storm", dict(smile=0.0, tilt=6 * math.sin(t * 9), look=(-.8, -.6)), point=.5)
    o.append(label("40 ДЕЛ", 700, 500, pop(t, W(21) - .1, .25), col="#ffffff"))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(19), 9)
    return vstudio(o, 540, 1060, 1.0 + .06 * uu, t, dx, dy)


def tabs_bar(n, w=600):
    o = ""
    tw = w / max(n, 1)
    for i in range(n):
        o += shape(lib.rrect(-w / 2 + tw * i + 2, -26, -w / 2 + tw * (i + 1) - 2, 20, 8), "#dfe6ef" if i < n - 1 else "#ffffff", "", w=2, seed=7600 + i)
    return o


def frame_s08(t):
    """«порывы до десяти вкладок в минуту»: Дима за ноутбуком, ветер, вкладки на экране множатся до 10, листы летят."""
    a, b = T0("s08"), T1("s08")
    n = 10                                    # сразу число из фразы, без бегущего счётчика
    o = desk_room(t)
    scr = rect(-310, -200, 310, 200, "#eef3fa") + tf(tabs_bar(n), 0, -170) + text(str(n), 0, 90, 170, fill=RED, stroke="#ffffff", sw=8)
    o.append(PR.desk(680, DESK_Y, w=660, depth=100, leg_h=260, seed=7))
    lap = shape([(-380, -6, 1), (380, -6, 1), (400, 26, 1), (-400, 26, 1)], "#9aa0aa", "", w=4, seed=4500)
    lap += shape(lib.rrect(-340, -470, 340, -6, 22), "#2a2d36", "", w=5, seed=4501) + tf(scr, 0, -238)
    o.append(tf(lap, 720, DESK_Y - 6, .8))
    f = dima_desk(t, "panic82", lean=-.15)
    o.append(f["svg"])
    for j in range(4):
        a_ = t * 3 + j * 1.6
        o.append(PR.flying_sheet(200 + (t * 600 + j * 260) % 900, 330 + 40 * math.sin(a_) + 50 * j, .6, a_ * 50, seed=j, flap=a_))
    o.append(PR.wind_lines(300, 600, 1.4, 1.0, t, seed=3, n=4))
    o.append(label("10 ВКЛАДОК", 640, 330, pop(t, W(26) - .1, .25), col="#ffffff", size=64))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(25), 8)
    return view("".join(o), 620 + dx, 900 + dy, 1.35 + .05 * uu, 0, t=t)


def frame_s09(t):
    """«Днём полный штиль на диване»: экран-голова — солнце и ровная гладь; кот разводит лапой."""
    a, b = T0("s09"), T1("s09")
    o = stage(t, "calm", dict(smile=.3, smug=.6, look=(-.8, -.3)), point=.55)
    o.append(label("ДНЁМ", 700, 500, pop(t, a - .05, .25)))
    uu = ease_io(ramp(t, a, b - a))
    return vstudio(o, 540, 1060, 1.0 + .05 * uu, t)


def frame_s10(t):
    """«Дело стоит на месте»: Дима лежит на диване с телефоном, рядом папка «ДЕЛО» стоит в паутине; флажок на столике висит без ветра."""
    a, b = T0("s10"), T1("s10")
    o = [plain_room(t), rug(540, RFL + 160, 560)]
    o.append(PR.window(900, 1000, 280, 380, mode="day", t=t, seed=4, curtain=False))
    sf = RM.sofa(520, RFL, 1.0)
    o.append(sf["back"])
    x, k = 420.0, .66
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    f = people.dima82(x, RFL - 314, k, "dull", "sit_desk", t=t, feet=feet, lean_add=-.3, arms={"n": ("ik", (x + 170, RFL - 520), -1)})
    o.append(f["svg"])
    o.append(mini_phone(x + 175, RFL - 540, .45, -15, screen="#9cc3ef"))
    o.append(sf["arm_r"])
    fo = shape(lib.rect_pts(-120, -160, 120, 0), "#f2c14e", "", w=4, seed=7700) + text("ДЕЛО", 0, -60, 58, fill=INK2, stroke="#f2c14e", sw=.01)
    o.append(tf(fo, 840, RFL - 330, .9, 2))
    o.append(PR.cobweb(735, RFL - 470, .8, seed=2))
    o.append(PR.zzz(560, RFL - 620, .7, t, 1.0))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 580, 1080, 1.18 + .05 * uu, 0, t=t)


def frame_s11(t):
    """«А в два часа ночи»: экран-голова тёмный, луна, туча; плашка «2:00»; кот зевает у экрана."""
    a, b = T0("s11"), T1("s11")
    o = stage(t, "night", dict(smile=0.0, look=(-.6, -.6)), point=.5)
    o.append(label("2 ЧАСА НОЧИ", 700, 500, pop(t, W(40) - .1, .25), col="#ffffff", size=72))
    o.append(rect(-1400, -1400, 2600, 3400, "#0c1030", .22))
    uu = ease_io(ramp(t, a, b - a))
    return vstudio(o, 540, 1060, 1.0 + .06 * uu, t)


def frame_s12(t):
    """«внезапный ливень продуктивности»: ночь, Дима за ноутбуком печатает как ураган, из тучи над ним сыплются галочки, молния."""
    a, b = T0("s12"), T1("s12")
    tf_ = W(44)
    o = desk_room(t, mode="night")
    o.append(PR.desk(680, DESK_Y, w=660, depth=100, leg_h=260, seed=7))
    lap = shape([(-380, -6, 1), (380, -6, 1), (400, 26, 1), (-400, 26, 1)], "#9aa0aa", "", w=4, seed=4500)
    scr = rect(-310, -200, 310, 200, "#eef3fa") + "".join(line([(-260, -150 + 50 * j), (-260 + 480 * clamp((t - a) * 2 - j * .25), -150 + 50 * j)],
                                                               9, INK2, taper=.1, wmin=.8, seed=7800 + j) for j in range(6))
    lap += shape(lib.rrect(-340, -470, 340, -6, 22), "#2a2d36", "", w=5, seed=4501) + tf(scr, 0, -238)
    o.append(tf(lap, 720, DESK_Y - 6, .8))
    o.append(PR.glow(720, 760, 420, .5, "#cfe3ff"))
    f = dima_desk(t, "zeal", lean=.25, arms={"f": ("ik", (590 + 20 * math.sin(t * 40), DESK_Y - 30), 1), "n": ("ik", (660 + 20 * math.cos(t * 37), DESK_Y - 25), 1)})
    o.append(f["svg"])
    fl = bump(t, tf_, .03, .25)
    o.append(PR.storm(600, 330, 620, 230, seed=7, flash=fl))
    for j in range(8):
        yy = (t * 900 + j * 131) % 520
        o.append(PR.check_mark(330 + 70 * j, 360 + yy, .6, 1.0, col=GREEN, w=9))
    o.append(PR.bolt(560, 330, 480, 560, u=.5 if fl > .1 else 0.0, w=30, seed=8))
    o.append(rect(-1400, -1400, 2600, 3400, "#0c1030", .18))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tf_, 10)
    return view("".join(o), 620 + dx, 760 + dy, 1.3 + .05 * uu, 0, t=t)


def frame_s13(t):
    """«Совет синоптика»: кот-синоптик крупно, поднимает указку вверх; плашка «СОВЕТ»."""
    a, b = T0("s13"), T1("s13")
    o = studio(t)
    o.append(map_board(860, 820, .5, t, "fog"))
    o.append(wcat(400, SFL, 1.7, t, dict(look=(.2, -.3), smile=.8, perk=1.0), point=.85, target=(900, 100)))
    o.append(label("СОВЕТ", 540, 480, pop(t, a - .05, .25)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(47), 7)
    return vstudio(o, 560, 1180, 1.0 + .06 * uu, t, dx, dy)


def frame_s14(t):
    """«в туман начинайте с двух минут»: на экране-голове туман, в центре таймер — вокруг него туман расходится; «2 МИНУТЫ»."""
    a, b = T0("s14"), T1("s14")
    tm = W(52)
    o = stage(t, "fog", dict(smile=1.0, look=(-.8, -.6)), point=.6, timer=ease_out(ramp(t, tm - .1, .6)))
    o.append(label("2 МИНУТЫ", 700, 500, pop(t, tm - .1, .25), col="#7ee08a"))
    o.append(PR.sparkles(680, 940, 2.0, bump(t, tm, .05, .5), t, seed=141, n=6, r=300))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tm, 8)
    return vstudio(o, 540, 1060, 1.0 + .05 * uu, t, dx, dy)


def frame_s15(t):
    """«Ураган от этого стихает»: ураган на экране сжимается и превращается в солнце; кот довольно кивает."""
    a, b = T0("s15"), T1("s15")
    c = ease_io(ramp(t, W(57) - .2, .6))
    o = stage(t, "storm", dict(smile=.3 + .7 * c, tilt=-8 * c), point=.5, calm=c)
    o.append(PR.sparkles(680, 930, 2.0, bump(t, W(57) + .3, .05, .5), t, seed=151, n=6, r=300))
    uu = ease_io(ramp(t, a, b - a))
    return vstudio(o, 540, 1060, 1.0 + .05 * uu, t)


def frame_s16(t):
    """«Отправь тому, у кого такая же погода»: телефон крупно, на экране карточка прогноза-головы и кнопка-самолётик; лапа кота
    жмёт, самолётик улетает."""
    a, b = T0("s16"), T1("s16")
    tp = W(58) + .25
    fly = ease_io(ramp(t, tp, .6))
    o = [paper_bg()]
    ph = shape(lib.rrect(-260, -470, 260, 470, 50), "#2a2d36", "", w=6, seed=7900)
    scr = rect(-230, -430, 230, 430, "#eef3fa")
    scr += tf(map_board(0, 0, 1.0, t, "mix"), 0, -120, .42)
    pr = bump(t, tp - .05, .05, .15)
    scr += shape(lib.rrect(-150, 230, 150, 330, 40), lib.mix("#2f8fe0", "#1d6fb8", pr), "", w=4, seed=7901)
    scr += tf(shape([(-40, 0, 1), (40, -22, 1), (-14, 22, 1)], "#ffffff", "", w=3, seed=7902), 0, 280, 1.2)
    ph += tf(scr, 0, 0)
    o.append(tf(ph, 540, 1000, 1.25, -3))
    if fly > 0:
        o.append(tf(shape([(-60, 0, 1), (60, -30, 1), (-20, 30, 1)], "#ffffff", "", w=4, seed=7910), 540 + 500 * fly, 1350 - 1000 * fly, 1.8, -25))
    o.append(cat(870, 1700, .95, t, dict(look=(-.7, -.6), smile=1.0, paw=.9 * bump(t, tp - .25, .15, .4), paw_dx=-110, perk=1.0)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tp, 8)
    return view("".join(o), 540 + dx, 1050 + dy, 1.0 + .05 * uu, 0, bg=PAPER, t=t)


def frame_s17(t):
    return cta_code(t, T0("s17"), T1("s17"))


def frame_s18(t):
    """«чтобы в твоей голове чаще было ясно»: экран-голова — солнце и радуга, кот-синоптик кланяется."""
    a, b = T0("s18"), T1("s18")
    o = stage(t, "clear", dict(look=(-.4, -.3), smile=1.0, tilt=-10 * bump(t, W(74), .15, .5)), point=.5)
    o.append(PR.sparkles(680, 900, 2.2, bump(t, W(74), .05, .6), t, seed=181, n=7, r=380))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(74), 7)
    return vstudio(o, 540, 1060, 1.0 + .05 * uu, t, dx, dy)


def frame_s19(t):
    """Петля: кадр хука — студия, экран-голова, кот с указкой."""
    a, b = T0("s19"), T1("s19")
    o = stage(t, "mix", dict(smile=.7), point=.3, ck=1.3, cx=200, bx=650, by=1120, bk=.95)
    return loop_view("".join(o), t, a, b, HIT, 560, 1120, 1.0, bg=STUDIO)


def stage(t, mode, cst=None, point=.55, ck=1.45, cx=245.0, bx=720.0, by=930.0, bk=.75, **mk):
    """Студия: экран-голова (bx, by, bk) справа и кот-синоптик спереди слева (cx, ck), указка на экран."""
    o = studio(t)
    o.append(map_board(bx, by, bk, t, mode, **mk))
    o.append(wcat(cx, SFL, ck, t, dict(dict(look=(.7, -.4), smile=.6, perk=1.0), **(cst or {})), point=point, target=(bx - 60, by)))
    return o


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
