"""Рилс 136 «Кот-фитнес-тренер», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json (общая дорожка voice_merge.py: кот-тренер Даниил, Дима male2).
Домашний «зал»: стена в полоску, коврик, стол с ноутбуком, раковина. Дима «качает» дела: штанга и гантель с конвертами-
блинами, кружка как гантель. Кот — тренер в красном спортивном костюме с белыми полосами, повязке на лбу, с полотенцем на шее и
свистком на шнурке (common/costume.py «sport», cat.WEAR: одежда внутри групп кота во всех планах, и в призыве; свисток во рту —
costume.SPORT["blow"]). Имя героя не звучит и не пишется. NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402
import costume  # noqa: E402

costume.use("sport")
HIT = stress(0, .3)
INK2 = "#1d2448"
GYM_WALL = "#dfe9f2"


def gym(t):
    o = [plain_room(t, wall=GYM_WALL)]
    o.append(PR.window(820, 760, 280, 340, mode="day", t=t, seed=5, curtain=False))
    o.append(PR.mat(470, RFL + 120, 1.0, w=760, col="#4f8fd0", seed=1))
    # шведская стенка слева
    for x_ in (-40, 140):
        o.append(line([(x_, RFL - 1100), (x_, RFL)], 16, "#c99a6b", taper=0, wmin=1, seed=6000 + x_))
    for j in range(9):
        o.append(line([(-40, RFL - 100 - 115 * j), (140, RFL - 100 - 115 * j)], 10, "#b8864f", taper=0, wmin=1, seed=6010 + j))
    return "".join(o)


def env_plate(x, y, k=1.0, rot=0.0, sd=0):
    """Конверт-блин: письмо вертикально, как блин штанги."""
    o = shape(lib.rrect(-60, -90, 60, 90, 10), "#fffdf4", line([(-60, -90), (0, -10), (60, -90)], 4, seed=6100 + sd)
              + f'<circle cx="34" cy="56" r="14" fill="#e2453a"/>', w=4.6, seed=6101 + sd)
    return tf(o, x, y, k, rot)


def barbell(x, y, k=1.0, rot=0.0, n=2):
    o = line([(-330, 0), (330, 0)], 16, "#7d8597", taper=0, wmin=1, seed=6120)
    for sx in (-1, 1):
        for j in range(n):
            o += env_plate(sx * (230 + 34 * j), 0, 1.0 - .1 * j, 0, sd=j * 2 + (sx > 0))
    return tf(o, x, y, k, rot)


def coach(t, x=820, y=RFL, k=1.0, st=None, blow=0.0):
    st = dict(dict(look=(-.7, -.2), smile=.8, tail=8 * math.sin(t * 1.7)), **(st or {}))
    costume.SPORT["blow"] = blow
    return cat(x, y, k, t, st)


def whistle_marks(x, y, u, t):
    """Звук свистка: короткие штрихи-лучи от свистка."""
    if u <= .02:
        return ""
    o = ""
    for j in range(3):
        a = math.radians(-30 + 30 * j)
        r0, r1 = 40, 40 + 70 * u
        o += line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 8, "#e2453a", taper=0, wmin=1, seed=6200 + j)
    return o


def mouth_pt(x, y, k):
    return x + (900 - CT.CX) * k, y + (1124 - CT.CBOT) * k


def presser(t, x, lift, expr="strain"):
    """Дима жмёт штангу-письмо над головой: lift 0…1 — от груди до вытянутых рук."""
    k = .64
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    by = hip - 560 * k - 250 * k * lift
    f = people.dima82(x, hip, k, expr, "d82_rest", t=t, feet="stand",
                      arms={"f": ("ik", (x - 150 * k, by), 1), "n": ("ik", (x + 150 * k, by), 1)})
    return f, by


def plaque(n, x, y, u):
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.4) if u < 1 else 1.0
    o = shape(lib.rrect(-120, -100, 120, 100, 20), "#fff6d0", text(str(n), 0, 56, 160, fill="#e2453a", stroke="#7a1a14", sw=6), w=5, seed=6300)
    return tf(o, x, y, s, -5)


def desk_set(t, open_=1.0, screen="lines", lines=0.0):
    return PR.desk(560, RFL - 300, w=600, depth=100, leg_h=300, seed=7) + PR.laptop(600, RFL - 306, 1.1, open_=open_, screen=screen, lines=lines, t=t, seed=1)


def dima_desk_(t, expr="calm82", tap=0.0, x=280):
    k = .62
    hip = RFL - 300
    return people.dima82(x, hip, k, dict(people.EXPR["dima"].get(expr, people.EXPR["dima"]["calm82"]), look=(.9, .1)), "sit_desk", t=t,
                         feet=people.sit_kw(x, hip, k)["feet"], arms={"f": ("ik", (530 + 10 * tap, RFL - 330), 1), "n": ("ik", (610 - 10 * tap, RFL - 320), 1)})


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: Дима жмёт над головой штангу с конвертами-блинами, кот-тренер в костюме свистит прямо на «Ещё»."""
    o = [gym(t)]
    lift = .8 + .2 * math.sin(t * 7)
    f, by = presser(t, 400, lift)
    o.append(f["svg"])
    o.append(barbell(400, by, .85, 3 * math.sin(t * 9)))
    o.append(coach(t, 840, RFL, 1.05, dict(look=(-.8, -.4), perk=1.0), blow=1.0))
    mx, my = mouth_pt(840, RFL, 1.05)
    o.append(whistle_marks(mx + 60, my - 20, bump(t, HIT - .1, .05, .4), t))
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 560, 1020, 1.0, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«письмо! Давай-давай!»: штанга-письмо дрожит и идёт вверх, Дима пыхтит, кот хлопает лапами."""
    a, b = T0("s02"), T1("s02")
    o = [gym(t)]
    lift = .62 + .38 * ease_io(ramp(t, W(3), .7))
    f, by = presser(t, 420, lift, "strain" if lift < .9 else "proud82")
    o.append(f["svg"])
    o.append(barbell(420, by + 6 * math.sin(t * 40) * (1 - lift), .85))
    hx, hy = f["head"]
    if lift < .9:
        o.append(PR.sweat(hx + 90, hy - 30, 1.0))
    clap = abs(math.sin(t * 11)) * (t > W(3))
    o.append(coach(t, 850, RFL, 1.0, dict(look=(-.8, -.6), smile=1.0, perk=1.0, paw=.4 + .4 * clap, paw_dx=-40, paw_l=.4 + .4 * clap, paw_l_dx=-40)))
    o.append(PR.sparkles(420, by, 1.6, bump(t, W(3) + .7, .05, .5), t, seed=21, n=6, r=220))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 580, 1020, 1.0 + .06 * u, 0, t=t)


def frame_s03(t):
    """Дима: «Мой котик стал фитнес-тренером»: кот на коврике в костюме, повязке и с полотенцем подпрыгивает и «поигрывает
    мускулами», Дима рядом показывает на него."""
    a, b = T0("s03"), T1("s03")
    o = [gym(t)]
    j = abs(math.sin((t - a) * 5.5)) * (t > W(6))
    o.append(coach(t, 640, RFL - 160 * j, 1.35, dict(look=(-.2, -.2), smile=1.0, perk=1.0, legs=j, paw=.7, paw_dx=60, paw_l=.7, paw_l_dx=60)))
    f = stand(250, t, "laugh82", "d82_one", k=.74)
    o.append(f["svg"])
    o.append(PR.sparkles(660, RFL - 600, 1.4, bump(t, W(7), .05, .5), t, seed=31, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 520, 1060, 1.04 + .05 * u, 0, t=t)


def frame_s04(t):
    """«Разминка: открыть почту»: Дима за столом тянется к ноутбуку, на экране конверт открывается; кот рядом на коврике считает."""
    a, b = T0("s04"), T1("s04")
    o = [gym(t)]
    op = ease_out(ramp(t, W(9), .4))
    o.append(desk_set(t, open_=1.0, screen="mail", lines=0.0) if False else desk_set(t, open_=.2 + .8 * op, lines=.0))
    o.append(chair(280, RFL - 240, 1.0))
    f = dima_desk_(t, "calm82", 0.0)
    o.append(f["svg"])
    eu = ramp(t, W(10) - .1, .3)
    if eu > 0:
        s = lib.back_out(clamp(eu), 2.4) if eu < 1 else 1.0
        o.append(tf(shape(lib.rect_pts(-90, -60, 90, 60), "#fffdf4", line([(-90, -60), (0, 10 - 40 * eu), (90, -60)], 4, seed=6400), w=4, seed=6401),
                    600, RFL - 560, s))
    o.append(coach(t, 900, RFL, .9, dict(look=(-.9, -.4), smile=.8)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 580, 1100, 1.1 + .05 * u, 0, t=t)


def frame_s05(t):
    """«Не филонить!»: кот-тренер крупно свистит в свисток, Дима подпрыгивает на стуле и выпрямляется."""
    a, b = T0("s05"), T1("s05")
    o = [gym(t)]
    o.append(desk_set(t, lines=.1))
    o.append(chair(280, RFL - 240, 1.0))
    up = bump(t, W(11) + .1, .06, .3)
    f = dima_desk_(t, "wow82" if up > .2 else "calm82")
    o.append(f"<g transform='translate(0 {-60 * up:.1f})'>{f['svg']}</g>")
    o.append(coach(t, 820, RFL, 1.3, dict(look=(-.9, -.2), perk=1.0, smile=0.0), blow=1.0))
    mx, my = mouth_pt(820, RFL, 1.3)
    o.append(whistle_marks(mx + 70, my - 20, bump(t, W(11), .05, .4), t))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(11), 10)
    return view("".join(o), 600 + dx, 1100 + dy, 1.1 + .05 * u, 0, t=t)


def dumbbell(x, y, k=1.0, rot=0.0):
    o = line([(-80, 0), (80, 0)], 14, "#7d8597", taper=0, wmin=1, seed=6500)
    o += env_plate(-80, 0, .7, 0, 7) + env_plate(80, 0, .7, 0, 8)
    return tf(o, x, y, k, rot)


def frame_s06(t):
    """«Первый подход: одно письмо»: табличка «1», Дима сгибает руку с гантелью-конвертом, кот-тренер считает лапой."""
    a, b = T0("s06"), T1("s06")
    o = [gym(t)]
    o.append(plaque(1, 860, 560, ramp(t, a - .2, .3)))
    k = .76
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    curl = .5 + .5 * math.sin((t - a) * 5)
    hand = (360 + 300 * k, hip - 200 * k - 160 * k * curl)      # гантель сбоку, ниже плеча: лицо открыто
    f = people.dima82(360, hip, k, "strain" if curl > .6 else "proud82", "d82_rest", t=t, feet="stand", arms={"n": ("ik", hand, -1)})
    o.append(f["svg"])
    o.append(dumbbell(hand[0] + 10, hand[1], .9, 90))
    o.append(coach(t, 820, RFL, 1.0, dict(look=(-.8, -.4), smile=.9, paw=.5 + .3 * curl, paw_dx=-30)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(16), 6)
    return view("".join(o), 560 + dx, 1060 + dy, 1.04 + .05 * u, 0, t=t)


def frame_s07(t):
    """«Отвечаем в одну строку!»: экран ноутбука крупно, одна строка печатается, кот-тренер заглядывает сбоку и поднимает лапу «раз»."""
    a, b = T0("s07"), T1("s07")
    o = [gym(t)]
    o.append(desk_set(t, lines=0.0))
    ln = ease_io(ramp(t, W(17), WE(20) - W(17)))
    scr = shape(lib.rrect(-260, -150, 260, 150, 12), "#eef3fa", "", w=4, seed=6600)
    scr += line([(-220, -70), (-220 + 440 * ln, -70)], 12, INK2, taper=0, wmin=1, seed=6601) if ln > .02 else ""
    scr += shape(lib.rrect(120, 90, 240, 130, 10), "#2f8fe0" if ln > .95 else "#9aa6b8", "", w=3, seed=6602)
    o.append(tf(scr, 600, RFL - 560, 1.0))
    o.append(chair(280, RFL - 240, 1.0))
    o.append(dima_desk_(t, "calm82", math.sin(t * 32) * (ln < 1))["svg"])
    o.append(coach(t, 930, RFL - 300, .7, dict(look=(-.9, .1), smile=1.0, paw=.8, paw_dx=10)))
    o.append(PR.sparkles(820, RFL - 440, 1.2, bump(t, W(20), .05, .5), t, seed=71, n=5, r=140))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 620, 1060, 1.15 + .06 * u, 0, t=t)


def sink(x, y):
    o = shape(lib.rect_pts(-300, -300, 300, 0), "#c9a06a", blob(lib.rect_pts(-300, -300, 300, -270), "#e0c08a"), w=4, seed=6700)
    o += shape(lib.rrect(-150, -300, 150, -250, 10), "#b9c0c8", "", w=4, seed=6701)
    o += line([(60, -300), (60, -400), (0, -420), (-20, -400)], 14, "#9aa1aa", taper=0, wmin=1, seed=6702)
    return tf(o, x, y)


def frame_s08(t):
    """«Второй подход: одна кружка»: табличка «2», у раковины Дима «сгибает» кружку, как гантель, пена; кот считает."""
    a, b = T0("s08"), T1("s08")
    o = [gym(t)]
    o.append(sink(420, RFL))
    o.append(plaque(2, 860, 560, ramp(t, a - .2, .3)))
    k = .76
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    curl = .5 + .5 * math.sin((t - a) * 5)
    hand = (330 + 300 * k, hip - 160 * k - 160 * k * curl)      # кружка сбоку, ниже плеча: лицо открыто
    f = people.dima82(330, hip, k, "proud82", "d82_rest", t=t, feet="stand", arms={"n": ("ik", hand, -1)})
    o.append(f["svg"])
    o.append(PR.mug(hand[0] + 30, hand[1] + 10, 1.1, col="red", coffee=False, seed=2))
    o.append(PR.sparkles(hand[0] + 30, hand[1], 1.0, bump(t, W(24), .05, .5), t, seed=81, n=5, r=110))
    o.append(coach(t, 860, RFL, 1.0, dict(look=(-.9, -.4), smile=.9, paw=.6, paw_dx=-20)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1060, 1.06 + .05 * u, 0, t=t)


def frame_s09(t):
    """«Держим темп!»: кот-тренер бежит на месте, полотенце и повязка прыгают вместе с ним, свисток; Дима быстро вытирает кружку."""
    a, b = T0("s09"), T1("s09")
    o = [gym(t)]
    o.append(sink(300, RFL))
    k = .7
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    rub = math.sin(t * 30)
    f = people.dima82(220, hip, k, "rush82", "d82_rest", t=t, feet="stand",
                      arms={"n": ("ik", (380 + 20 * rub, hip - 230), 1), "f": ("ik", (360 - 20 * rub, hip - 260), 1)})
    o.append(f["svg"])
    o.append(PR.mug(390, hip - 250, 1.0, col="red", coffee=False, seed=2))
    ph = (t - a) * 9
    jump = abs(math.sin(ph))
    o.append(coach(t, 760, RFL - 70 * jump, 1.25, dict(look=(-.6, -.2), perk=1.0, walk=ph / (2 * math.pi), legs=.3 * jump), blow=1.0 if t > W(26) - .1 else 0.0))
    mx, my = mouth_pt(760, RFL - 70 * jump, 1.25)
    o.append(whistle_marks(mx + 70, my - 20, bump(t, W(26), .05, .4), t))
    o.append(PR.speed_arcs(620, RFL - 300, 1.0, 1.0, t, seed=9, n=3, ang=180))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(26), 8)
    return view("".join(o), 540 + dx, 1080 + dy, 1.1 + .05 * u, 0, t=t)


def frame_s10(t):
    """«Последний подход»: табличка «3», кот-тренер показывает лапой на ноутбук, Дима садится."""
    a, b = T0("s10"), T1("s10")
    o = [gym(t)]
    o.append(desk_set(t, lines=0.0))
    o.append(chair(280, RFL - 240, 1.0))
    o.append(dima_desk_(t, "calm82")["svg"])
    o.append(coach(t, 900, RFL, 1.0, dict(look=(-.9, -.2), smile=.8, perk=1.0, paw=.9, paw_dx=-90)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 580, 1080, 1.08 + .05 * u, 0, t=t)


def frame_s11(t):
    """«открыть файл»: экран ноутбука крупно, папка-файл открывается в лист; Дима жмёт."""
    a, b = T0("s11"), T1("s11")
    o = [gym(t)]
    o.append(desk_set(t, lines=0.0))
    op = ease_out(ramp(t, W(30) - .1, .3))
    scr = shape(lib.rrect(-260, -150, 260, 150, 12), "#eef3fa", "", w=4, seed=6800)
    scr += tf(shape(lib.rect_pts(-80, -100, 80, 100), "#ffffff", blob(lib.rect_pts(-80, -100, 80, -70), "#2f8fe0"), w=3.4, seed=6801), 0, 0, .6 + .4 * op)
    o.append(tf(scr, 600, RFL - 560, 1.0))
    o.append(chair(280, RFL - 240, 1.0))
    o.append(dima_desk_(t, "proud82")["svg"])
    o.append(coach(t, 930, RFL - 300, .7, dict(look=(-.9, .1), smile=1.0, perk=1.0)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(30), 6)
    return view("".join(o), 620 + dx, 1060 + dy, 1.15 + .05 * u, 0, t=t)


def timer_face(x, y, k, left, pulse=0.0):
    m, s_ = int(left // 60), int(left % 60)
    o = shape(ellipse_pts(0, 0, 120, 120, 30), "#ffffff", text(f"{m}:{s_:02d}", 0, 26, 76, fill=INK2, stroke="#ffffff", sw=4), w=5.4, seed=6900)
    o += shape(lib.rrect(-20, -150, 20, -118, 6), "#e2453a", "", w=3.4, seed=6901)
    return tf(o, x, y, k * (1 + .2 * pulse))


def frame_s12(t):
    """«Две минуты!»: кот-тренер крупно поднимает секундомер «2:00» и щёлкает кнопкой."""
    a, b = T0("s12"), T1("s12")
    o = [gym(t)]
    up = ease_out(ramp(t, a - .2, .3))
    o.append(coach(t, 560, RFL, 1.5, dict(look=(.1, -.6), smile=1.0, perk=1.0, paw=.9 * up, paw_dx=30)))
    o.append(timer_face(640, RFL - 760, 1.0, 120, bump(t, W(32), .05, .3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(32), 6)
    return view("".join(o), 560 + dx, 1100 + dy, 1.1 + .05 * u, 0, t=t)


def frame_s13(t):
    """«Я в тебя верю!»: кот-тренер подпрыгивает с поднятыми лапами, полотенце и повязка прыгают с ним, сердечки; Дима улыбается за ноутбуком."""
    a, b = T0("s13"), T1("s13")
    o = [gym(t)]
    o.append(desk_set(t, lines=.3 + .3 * ramp(t, a, b - a)))
    o.append(chair(280, RFL - 240, 1.0))
    o.append(dima_desk_(t, "proud82", math.sin(t * 30))["svg"])
    j = abs(math.sin((t - a) * 6))
    o.append(coach(t, 880, RFL - 120 * j, 1.0, dict(look=(-.6, -.3), smile=1.0, perk=1.0, legs=j, paw=.95, paw_dx=40, paw_l=.95, paw_l_dx=40)))
    for i in range(3):
        u_ = ramp(t, W(36) - .2 + .12 * i, .3)
        if u_ > 0:
            o.append(PR.heart(820 + 60 * (i - 1), RFL - 560 - 160 * u_ - 40 * i, .7 * u_, seed=i))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1080, 1.08 + .05 * u, 0, t=t)


def frame_s14(t):
    """«Через две минуты»: секундомер добегает до 0:00, на экране файл заполнен строками, Дима выдыхает, кот рядом."""
    a, b = T0("s14"), T1("s14")
    o = [gym(t)]
    o.append(desk_set(t, lines=.6 + .4 * ramp(t, a, b - a)))
    o.append(chair(280, RFL - 240, 1.0))
    o.append(dima_desk_(t, "relief", math.sin(t * 30) * (t < W(39)))["svg"])
    o.append(timer_face(860, 560, .85, 120, bump(t, W(39), .05, .3)))      # правило 11: только «две минуты» из фразы, без бега
    o.append(PR.check_mark(940, 470, 1.0, ramp(t, W(39), .25), col="#3fb26a", seed=3))
    o.append(coach(t, 930, RFL - 300, .7, dict(look=(-.9, .1), smile=1.0, perk=1.0)))
    o.append(PR.sparkles(600, RFL - 560, 1.6, bump(t, W(39), .05, .5), t, seed=141, n=6, r=220))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(39), 6)
    return view("".join(o), 600 + dx, 1060 + dy, 1.08 + .05 * u, 0, t=t)


def frame_s15(t):
    """«я сам попросил ещё подход»: Дима встал и поднял палец «ещё!», кот-тренер изумлён и счастлив, уши торчком."""
    a, b = T0("s15"), T1("s15")
    o = [gym(t)]
    o.append(desk_set(t, lines=1.0))
    f = stand(330, t, "proud82", "d82_one", k=.76, head_add=.05 * math.sin(t * 6))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(text("!", hx + 150, hy - 140, 200 * pop(t, W(43), .2), fill="#3fb26a", stroke="#111", sw=10) if t > W(43) else "")
    o.append(coach(t, 860, RFL, 1.15, dict(look=(-.9, -.4), smile=1.0, perk=1.0, tilt=8 * bump(t, W(43), .1, .5), legs=bump(t, W(43), .1, .3))))
    o.append(PR.sparkles(860, RFL - 500, 1.4, bump(t, W(43), .05, .5), t, seed=151, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(43), 8)
    return view("".join(o), 580 + dx, 1060 + dy, 1.06 + .05 * u, 0, t=t)


def frame_s16(t):
    return cta_code(t, T0("s16"), T1("s16"))


def frame_s17(t):
    """«чтобы у тебя тоже был такой тренер»: кот-тренер крупно, свисток во рту, показывает лапой на зрителя."""
    a, b = T0("s17"), T1("s17")
    o = [gym(t)]
    blow = 1.0 if t > W(54) - .15 else 0.0
    o.append(coach(t, 540, RFL, 1.7, dict(look=(0, 0), smile=1.0, perk=1.0, paw=.95, paw_dx=-10), blow=blow))
    mx, my = mouth_pt(540, RFL, 1.7)
    o.append(whistle_marks(mx + 90, my - 30, bump(t, W(54), .05, .4), t))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(54), 6)
    return view("".join(o), 560 + dx, 1140 + dy, 1.1 + .08 * u, 0, t=t)


def frame_s18(t):
    """Петля: кадр хука — штанга с конвертами, кот свистит."""
    a, b = T0("s18"), T1("s18")
    o = [gym(t)]
    f, by = presser(t, 400, .8 + .2 * math.sin(t * 7))
    o.append(f["svg"])
    o.append(barbell(400, by, .85))
    o.append(coach(t, 840, RFL, 1.05, dict(look=(-.8, -.4), perk=1.0), blow=1.0))
    return loop_view("".join(o), t, a, b, HIT, 560, 1020, 1.0)


def frame(sid, t):
    lib.DEFS.clear()
    costume.SPORT["blow"] = 0.0
    return globals()["frame_" + sid](t)
