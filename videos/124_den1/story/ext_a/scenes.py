"""Рилс 124 «30 дней с котиком-напарником. День 1», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Места: календарь на 30 дней на стене,
диван, стол с ноутбуком (письмо на экране), конверт на кнопке с пылью. Призыв — TG-карточка v5 (scripts/story_cta_tg.py).
NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people, REPO, COMMON  # noqa: E402
import room as RM  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "scripts"))
import story_cta_tg as TG  # noqa: E402

HIT = stress(1, .3)
INK2 = "#1d2448"
SCR = "#eef3fa"


# ═════════════ календарь на 30 дней ═════════════
def cal30(x, y, k=1.0, circle=0.0, paw=0.0, crossed=0, mark2=0.0, glow=0.0, rot=0.0):
    """Настенный календарь 30 дней (центр). circle — красный круг вокруг «1» рисуется; paw — отпечаток лапы на «1»;
    crossed — сколько первых клеток зачёркнуто; mark2 — «?» над клеткой «2»."""
    Wc, Hc = 760.0, 760.0
    cw, ch = Wc / 6, (Hc - 170) / 5
    o = blob(lib.rect_pts(-Wc / 2 + 16, -Hc / 2 + 20, Wc / 2 + 16, Hc / 2 + 20), "#000000", .18)
    inner = blob(lib.rect_pts(-Wc / 2, -Hc / 2, Wc / 2, -Hc / 2 + 150), "#c8553d")
    inner += text("30 ДНЕЙ", 0, -Hc / 2 + 108, 92, fill="#ffffff", stroke="#7a2a1e", sw=6)
    if glow > 0:
        inner += blob(lib.rect_pts(-Wc / 2 + 4, -Hc / 2 + 154, -Wc / 2 + cw, -Hc / 2 + 154 + ch), "#fff1b0", glow)
    for i in range(30):
        cx_ = -Wc / 2 + cw * (i % 6) + cw / 2
        cy_ = -Hc / 2 + 170 + ch * (i // 6) + ch / 2
        inner += line([(cx_ - cw / 2, cy_ + ch / 2), (cx_ + cw / 2, cy_ + ch / 2)], 2, "#d6cbb4", taper=0, wmin=1, seed=4000 + i)
        inner += text(str(i + 1), cx_, cy_ + 20, 54 if i else 66, fill=INK2 if i else RED, stroke="#ffffff", sw=.01)
        if i < crossed:
            inner += PR.cross_stroke((cx_ - 40, cy_ - 36), (cx_ + 40, cy_ + 36), (cx_ + 40, cy_ - 36), (cx_ - 40, cy_ + 36), u=1.0, w=10, seed=i)
    for j in range(1, 6):
        x_ = -Wc / 2 + cw * j
        inner += line([(x_, -Hc / 2 + 160), (x_, Hc / 2 - 10)], 2, "#d6cbb4", taper=0, wmin=1, seed=4100 + j)
    c1 = (-Wc / 2 + cw / 2, -Hc / 2 + 170 + ch / 2)
    if circle > 0:
        n = max(2, int(40 * clamp(circle)))
        pts = [(c1[0] + 56 * math.cos(-1.7 + 6.6 * q / 39), c1[1] + 50 * math.sin(-1.7 + 6.6 * q / 39)) for q in range(n)]
        inner += line(pts, 9, RED, taper=.2, wmin=.6, seed=4200)
    if paw > 0:
        s = 1 + .6 * (1 - ease_out(clamp(paw)))
        pr = blob(ellipse_pts(0, 8, 20, 17, 12), "#e8823a") + "".join(blob(ellipse_pts(dx, -20 - (6 if abs(dx) < 15 else 0), 8, 9, 10), "#e8823a")
                                                                     for dx in (-22, -8, 8, 22))
        inner += f'<g opacity="{min(1.0, paw * 3):.2f}" transform="translate({c1[0] + 26:.1f} {c1[1] - 10:.1f}) scale({s:.3f})">{pr}</g>'
    if mark2 > 0:
        c2 = (c1[0] + cw, c1[1])
        inner += blob(lib.rect_pts(c2[0] - cw / 2 + 4, c2[1] - ch / 2 + 4, c2[0] + cw / 2 - 4, c2[1] + ch / 2 - 4), "#ffe08a", .9 * clamp(mark2))
        inner += tf(text("?", 0, 40, 120, fill=RED, stroke="#ffffff", sw=8), c2[0], c2[1] - 10, pop(mark2, 0, 1.0) if mark2 < 1 else 1.0)
    o += shape(lib.rect_pts(-Wc / 2, -Hc / 2, Wc / 2, Hc / 2), "#fbf6ea", inner, w=5, seed=4300)
    for j in range(6):
        o += shape(ellipse_pts(-Wc / 2 + 70 + 124 * j, -Hc / 2 - 4, 12, 20, 10), "#5a5f6e", "", w=3, seed=4310 + j)
    return tf(o, x, y, k, rot)


CAL1 = (-380 + 760 / 12, -380 + 170 + 590 / 10)      # центр клетки «1» в координатах календаря


def room(t, mode="day"):
    o = [plain_room(t)]
    o.append(rug(540, RFL + 160, 560))
    return o


def frame_s01(t):
    """ХУК: календарь на 30 дней крупно, кот летит снизу и ставит лапу на «1», красный круг; Дима сбоку машет."""
    tl = W(1)
    o = room(t)
    o.append(cal30(600, 1000, 1.0, circle=ramp(t, tl - .1, .35), paw=ramp(t, tl, .2), glow=bump(t, tl, .05, .4)))
    px, py = 600 + CAL1[0] + 26, 1000 + CAL1[1] - 10
    j = ease_out(ramp(t, -.2, tl + .2))
    ex, ey = 150.0, py + 125
    if t < tl + .15:
        cx_, cy_ = 900 + (ex - 900) * j, 1700 + (ey - 1700) * j - 160 * math.sin(math.pi * j)
    else:
        g = t - tl - .15
        cx_, cy_ = ex - 30 * g, min(RFL, ey + 2400 * g * g)
    o.append(cat(cx_, cy_, .8, t, dict(look=(.8, -.4), smile=.8, paw=1.0 if j > .6 and t < tl + .3 else .2, paw_dx=110,
                                       legs=1.0 if cy_ < RFL - 5 else 0.0, perk=1.0)))
    o.append(PR.sparkles(px, py, 1.6, bump(t, tl, .05, .5), t, seed=11, n=6, r=150))
    dx, dy = shake(t, tl, 12)
    return hook_view("".join(o), t, HIT, 560, 1080, 1.05, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«с котиком-напарником»: Дима на диване, кот запрыгивает рядом, дают «пять» лапой и ладонью."""
    a, b = T0("s02"), T1("s02")
    o = room(t)
    o.append(PR.window(930, 1020, 280, 380, mode="day", t=t, seed=4, curtain=False))
    sf = RM.sofa(540, RFL, 1.0)
    o.append(sf["back"])
    x, k = 440.0, .66
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    hi = ease_out(ramp(t, W(5) + .1, .3))
    f = people.dima82(x, RFL - 314, k, "laugh82", "sit_desk", t=t, feet=feet,
                      arms={"n": ("ik", (x + 200, RFL - 560 - 60 * hi), -1)})
    o.append(f["svg"])
    o.append(sf["arm_r"])
    j = ease_out(ramp(t, a - .1, .35))
    o.append(cat(980 - 300 * j, RFL - 306 - 180 * math.sin(math.pi * j), .62, t,
                 dict(look=(-.8, -.6), smile=1.0, paw=hi, paw_dx=-90, legs=1 - j, perk=1.0)))
    o.append(PR.sparkles(x + 200, RFL - 600, 1.4, bump(t, W(5) + .4, .05, .5), t, seed=21, n=6, r=120))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 580, 1050, 1.3 + .05 * uu, 0, t=t)


def frame_s03(t):
    """«День первый!»: календарь, «1» обведена, отпечаток лапы; Дима рядом показывает на неё, кот на плече у календаря."""
    a, b = T0("s03"), T1("s03")
    o = room(t)
    o.append(cal30(700, 920, .85, circle=1.0, paw=ramp(t, W(7), .2), glow=.6 + .4 * bump(t, W(7), .05, .4)))
    f = stand(170, t, "laugh82", "d82_one")
    o.append(f["svg"])
    o.append(cat(940, RFL, .8, t, dict(look=(-.6, -.8), smile=1.0, perk=1.0, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(700 + CAL1[0] * .85, 920 + CAL1[1] * .85, 1.8, bump(t, W(7), .05, .5), t, seed=31, n=7, r=200))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(7), 9)
    return view("".join(o), 520 + dx, 1000 + dy, 1.0 + .05 * uu, 0, t=t)


def envelope(x, y, k, open_u=0.0, dot=1.0, rot=0.0):
    """Конверт письма на экране: красная точка «непрочитано»; open_u — клапан откидывается, лист выезжает."""
    o = ""
    ou = clamp(open_u)
    if ou > 0:
        o += shape(lib.rect_pts(-120, -60 - 120 * ou, 120, 60), "#ffffff",
                   "".join(line([(-90, -30 - 120 * ou + 26 * j), (90 - 40 * (j % 2), -30 - 120 * ou + 26 * j)], 4, "#b9b2a2", seed=4400 + j)
                           for j in range(3)), w=3, seed=4410)
    o += shape(lib.rect_pts(-150, -90, 150, 90), "#f3d9a4", "", w=4, seed=4420)
    o += line([(-150, 90), (0, -4), (150, 90)], 3, "#b8925a", taper=0, wmin=1, seed=4421)
    fy = -90 + 180 * (1 - 2 * ou) * .5 + 90 * (1 - 2 * ou) * 0
    o += shape([(-150, -90, 1), (0, -90 + 100 * (1 - 2 * ou), 1), (150, -90, 1)], "#e8c787", "", w=4, seed=4422)
    del fy
    if dot > 0:
        o += shape(ellipse_pts(150, -90, 26 * dot, 26 * dot, 14), RED, "", w=3, seed=4430)
    return tf(o, x, y, k, rot)


def laptop(x, y, k, inner, glow=0.0):
    """Ноутбук анфас (низ корпуса (x, y)): экран 640×400 с содержимым inner (центр экрана 0,0)."""
    o = shape([(-380, -6, 1), (380, -6, 1), (400, 26, 1), (-400, 26, 1)], "#9aa0aa", "", w=4, seed=4500)
    o += shape(lib.rrect(-340, -470, 340, -6, 22), "#2a2d36", "", w=5, seed=4501)
    scr = rect(-310, -200, 310, 200, SCR) + inner
    o += tf(f'<g clip-path="inset(0)">{scr}</g>', 0, -238)
    if glow > 0:
        o += PR.glow(0, -238, 400, .3 * glow, "#cfe3ff")
    return tf(o, x, y, k)


def mail_ui(inner, title="Письмо"):
    o = rect(-310, -200, 310, -130, "#5b8fd0") + text(title, -280, -150, 40, fill="#ffffff", stroke="#5b8fd0", sw=.01, anchor="start")
    return o + inner


def desk_set(t, inner, mode="day", sun=0.0, lap_k=.8, glow=.5):
    o = desk_room(t, mode=mode, sun=sun)
    o.append(laptop(700, DESK_Y - 6, lap_k, inner, glow))
    return o


def frame_s04(t):
    """«Утром у меня висело письмо»: утро, солнце в окне, Дима за столом смотрит на ноутбук, на экране конверт с красной точкой."""
    a, b = T0("s04"), T1("s04")
    dot = 1 + .25 * math.sin(t * 9)
    o = desk_set(t, mail_ui(envelope(0, 30, 1.1, dot=dot)), sun=1.0)
    f = dima_desk(t, dict(people.EXPR["dima"]["awkward"], look=(.9, -.1)), lean=.05)
    o.append(f["svg"])
    o.append(cat(960, DESK_Y - 4, .45, t, dict(look=(-.8, -.3), smile=.3)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(12), 6)
    return view("".join(o), 620 + dx, 860 + dy, 1.45 + .06 * uu, 0, t=t)


def frame_s05(t):
    """«которое я не открывал две недели»: конверт висит на кнопке на стене, пыль сыплется, паутина; плашка «2 НЕДЕЛИ»."""
    a, b = T0("s05"), T1("s05")
    u = ramp(t, a - .3, b - a)
    o = [plain_room(t)]
    o.append(PR.pinned_envelope(540, 700, 2.4, swing=.3 * math.sin(t * 2), dust=.4 + .6 * u, web=.3 + .7 * u, t=t, seed=1))
    o.append(tf(shape(lib.rrect(-260, -70, 260, 70, 30), RED, "", w=5, seed=4600)
                + text("2 НЕДЕЛИ", 0, 28, 84, fill="#ffffff", stroke="#7a1e18", sw=6), 540, 1360, pop(t, W(17) - .1, .25)))
    f = stand(190, t, "guilty", "d82_rest")
    o.append(f["svg"])
    o.append(cat(880, RFL, .7, t, dict(look=(-.6, -.8), smug=.5)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(17), 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.05 + .06 * uu, 0, t=t)


def frame_s06(t):
    """«Котик сел на клавиатуру»: кот прыгает на клавиатуру ноутбука и садится, Дима удивлён."""
    a, b = T0("s06"), T1("s06")
    tj = W(20)
    j = ease_out(ramp(t, a - .1, tj - a + .25))
    o = desk_set(t, mail_ui(envelope(0, 30, 1.1, dot=1.0)))
    f = dima_desk(t, "surprise", lean=-.05)
    o.append(f["svg"])
    cx_ = 1000 + (720 - 1000) * j
    cy_ = DESK_Y + 200 - (200 + 4) * j - 220 * math.sin(math.pi * j)
    o.append(cat(cx_, cy_, .55, t, dict(look=(-.9, -.2), smug=.8 if j >= 1 else 0, legs=1 - j, perk=1.0, tail=8 * math.sin(t * 2))))
    if j >= 1:
        o.append(PR.sparkles(720, DESK_Y - 100, 1.2, bump(t, tj + .25, .05, .4), t, seed=61, n=5, r=120))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tj + .2, 8)
    return view("".join(o), 620 + dx, 860 + dy, 1.45 + .05 * uu, 0, t=t)


def frame_s07(t):
    """«пока я его не открыл»: Дима тянется и жмёт, конверт на экране открывается, кот с клавиатуры довольно смотрит."""
    a, b = T0("s07"), T1("s07")
    to = W(30)
    ou = ease_out(ramp(t, to - .2, .35))
    o = desk_set(t, mail_ui(envelope(0, 40, 1.1, open_u=ou, dot=1.0 - ou)), glow=.5 + ou)
    reach = ease_io(ramp(t, a, to - a))
    f = dima_desk(t, "focus" if ou < 1 else "relief", lean=.2 * reach, arms={"n": ("ik", (480 + 120 * reach, DESK_Y - 30), 1)})
    o.append(f["svg"])
    o.append(cat(780, DESK_Y + 10, .55, t, dict(look=(-.9, -.4), smile=1.0 if ou > .5 else .2, perk=1.0)))
    o.append(PR.sparkles(700, 560, 1.8, bump(t, to + .1, .05, .5), t, seed=71, n=6, r=220))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, to, 8)
    return view("".join(o), 620 + dx, 860 + dy, 1.45 + .05 * uu, 0, t=t)


def frame_s08(t):
    """«написал одну строку и отправил»: экран крупно — в письме печатается одна строка, кнопка «Отправить», самолётик улетает."""
    a, b = T0("s08"), T1("s08")
    tw_ = ramp(t, W(33) - .1, W(35) - W(33) + .2)
    ts = W(36)
    fly = ease_io(ramp(t, ts, .5))
    inner = mail_ui("", "Ответ")
    inner += shape(lib.rect_pts(-260, -100, 260 - 520 * fly * 0, 60), "#ffffff", "", w=2, seed=4700, ink=True) if fly < .4 else ""
    if fly < .4:
        inner += line([(-230, -50), (-230 + 400 * tw_, -50)], 8, INK2, taper=.1, wmin=.8, seed=4701)
    pr = bump(t, ts - .05, .05, .15)
    inner += shape(lib.rrect(-150, 100, 150, 170, 34), lib.mix("#2f8fe0", "#1d6fb8", pr), "", w=3, seed=4702)
    inner += text("Отправить", 0, 150, 44, fill="#ffffff", stroke="#1d6fb8", sw=.01)
    if fly >= .4:
        inner += text("Отправлено", 40, -20, 56, fill=GREEN, stroke="#ffffff", sw=.01, op=ramp(t, ts + .2, .2)) + PR.check_mark(-200, -40, 1.0, ramp(t, ts + .2, .2), col=GREEN, w=10)
    o = desk_set(t, inner, glow=.8)
    if fly > 0:
        o.append(tf(shape([(-60, 0, 1), (60, -30, 1), (-20, 30, 1)], "#ffffff", "", w=4, seed=4710), 700 + 300 * fly, 560 - 420 * fly, 1.6, -20))
    o.append(cat(980, DESK_Y - 4, .45, t, dict(look=(-.8, -.5), smile=1.0)))
    f = dima_desk(t, "focus_smile", lean=.18, arms={"f": ("ik", (560, DESK_Y - 30), 1), "n": ("ik", (640, DESK_Y - 25), 1)})
    o.append(f["svg"])
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts, 8)
    return view("".join(o), 640 + dx, 800 + dy, 1.5 + .05 * uu, 0, t=t)


def frame_s09(t):
    """«Две недели висело»: календарь, 14 клеток зачёркиваются одна за другой, плашка «2 НЕДЕЛИ»."""
    a, b = T0("s09"), T1("s09")
    n = int(14 * clamp((t - a + .2) / (b - a)))
    o = room(t)
    o.append(cal30(540, 960, 1.0, crossed=max(1, n)))
    o.append(tf(shape(lib.rrect(-260, -70, 260, 70, 30), RED, "", w=5, seed=4600)
                + text("2 НЕДЕЛИ", 0, 28, 84, fill="#ffffff", stroke="#7a1e18", sw=6), 540, 1460, 1.0))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1000, 1.0 + .05 * uu, 0, t=t)


def frame_s10(t):
    """«а сделалось за две минуты»: таймер «2:00» крупно, плашка «2 МИНУТЫ»; Дима и кот дают «пять»."""
    a, b = T0("s10"), T1("s10")
    tm = W(44)
    o = room(t)
    o.append(PR.glow(680, 700, 500, .4 + .3 * bump(t, tm, .05, .5), "#fff1b0"))
    o.append(PR.bell_timer(690, 620, 1.4, hand_a=360 * ramp(t, a, tm - a) * 2 / 60, sector_u=ramp(t, a, tm - a) * 2 / 60, ring=bump(t, tm, .05, .4), t=t))
    o.append(tf(shape(lib.rrect(-250, -70, 250, 70, 30), GREEN, "", w=5, seed=4800)
                + text("2 МИНУТЫ", 0, 28, 80, fill="#ffffff", stroke="#1e5a32", sw=6), 690, 960, pop(t, tm - .15, .25)))
    f = stand(200, t, "laugh82" if t > tm - .2 else "proud82", "d82_one")
    o.append(f["svg"])
    o.append(cat(820, RFL, .85, t, dict(look=(-.8, -.7), smile=1.0, paw=ease_out(ramp(t, tm - .2, .25)), paw_dx=-90, perk=1.0)))
    o.append(PR.sparkles(690, 960, 1.8, bump(t, tm, .05, .5), t, seed=101, n=6, r=300))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tm, 9)
    return view("".join(o), 520 + dx, 1000 + dy, 1.02 + .05 * uu, 0, t=t)


def note_sheet(x, y, k, write=0.0, t=0.0, rot=0.0):
    """Листок в клетку; write 0…1 — на нём рукой пишется «завтра»."""
    o = blob(lib.rect_pts(-230 + 10, -160 + 12, 230 + 10, 160 + 12), "#000000", .15)
    inner = "".join(line([(-230, -160 + 40 * j), (230, -160 + 40 * j)], 1.6, "#bcd0e6", taper=0, wmin=1, seed=4900 + j) for j in range(1, 8))
    o += shape(lib.rect_pts(-230, -160, 230, 160), "#fdfbf4", inner, w=4, seed=4910)
    if write > 0:
        w_ = 400 * clamp(write)
        c = lib.clip_rect(-200, -90, w_, 160)
        o += f'<g clip-path="url(#{c})">' + plain("завтра", -190, 40, 120, fill=INK2) + "</g>"
        if write < 1:
            o += PR.pencil(-200 + w_ + 20, 10, 1.4, -30)
    return tf(o, x, y, k, rot)


def frame_s11(t):
    """«А вечером котик положил передо мной листок»: вечер, лампа, кот носом и лапой двигает листок по столу к Диме."""
    a, b = T0("s11"), T1("s11")
    p = ease_io(ramp(t, W(48) - .2, .7))
    o = desk_room(t, mode="evening")
    o.append(PR.glow(560, 760, 420, .35, "#ffd890"))
    o.append(laptop(800, DESK_Y - 6, .55, mail_ui(PR.check_mark(0, 40, 1.6, 1.0, col=GREEN, w=14))))
    o.append(note_sheet(720 - 170 * p, DESK_Y - 22, .5, rot=-4 + 4 * p))
    f = dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.8, .5)), lean=.05)
    o.append(f["svg"])
    o.append(cat(820 - 120 * p, DESK_Y - 4, .5, t, dict(look=(-.9, .4), smile=.8, paw=.8 * (1 - p) + .3, paw_dx=-80, tilt=-8 * (1 - p))))
    o.append(rect(-1400, -1400, 2600, 3400, "#3b2a4a", .18))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 620, 860, 1.45 + .05 * uu, 0, t=t)


def frame_s12(t):
    """«На нём было написано: „завтра“»: листок крупно на столе, на нём пишется «завтра»; лапа кота придерживает угол."""
    a, b = T0("s12"), T1("s12")
    w_ = ramp(t, W(55) - .1, W(56) + .3 - W(55) + .1)
    o = [rect(-1400, -1400, 2600, 3400, "#b27c4c")]
    for j in range(6):
        o.append(line([(-200, 300 + 260 * j), (1300, 320 + 260 * j)], 3, "#94633a", taper=.3, wmin=.4, seed=5000 + j))
    o.append(PR.glow(540, 900, 600, .3, "#ffd890"))
    o.append(note_sheet(540, 880, 2.0, w_, t, -3))
    o.append(cat(900, 1560, 1.0, t, dict(look=(-.7, -.8), smile=1.0 if w_ >= 1 else .4, paw=.7, paw_dx=-90, perk=1.0)))
    o.append(PR.sparkles(540, 880, 2.0, bump(t, W(56) + .3, .05, .5), t, seed=121, n=6, r=360))
    o.append(rect(-1400, -1400, 2600, 3400, "#3b2a4a", .12))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(56), 8)
    return view("".join(o), 560 + dx, 1000 + dy, 1.0 + .06 * uu, 0, bg="#b27c4c", t=t)


def frame_s13(t):
    """«Что было на второй день»: календарь, «1» обведена с лапой, клетка «2» загорается со знаком «?»; кот рядом."""
    a, b = T0("s13"), T1("s13")
    o = room(t)
    o.append(cal30(560, 960, 1.0, circle=1.0, paw=1.0, mark2=ramp(t, W(60) - .1, .3)))
    o.append(cat(900, RFL, .85, t, dict(look=(-.7, -.8), perk=1.0, tilt=-10 * bump(t, W(60), .1, .5))))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1000, 1.05 + .06 * uu, 0, t=t)


def frame_s14(t):
    """«покажу в следующей серии»: ночь, кот спит на листке «завтра», Дима выключает лампу; за окном луна."""
    a, b = T0("s14"), T1("s14")
    off = ramp(t, W(64) - .1, .15)
    o = desk_room(t, mode="night")
    o.append(PR.lamp_desk(980, DESK_Y, 1.4, on=1 - off))
    if off < 1:
        o.append(PR.glow(900, 760, 420, .4 * (1 - off), "#ffd890"))
    o.append(note_sheet(700, DESK_Y - 22, .5, 1.0, t, -3))
    o.append(CT.curl(700, DESK_Y - 30, .55, dict(eye=.0), t))
    o.append(PR.zzz(760, DESK_Y - 220, .9, t, 1.0))
    f = dima_desk(t, "warm", lean=0.0, head_add=-.05)
    o.append(f["svg"])
    o.append(rect(-1400, -1400, 2600, 3400, "#0c1030", .15 + .3 * off))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 620, 860, 1.45 + .05 * uu, 0, t=t)


def cta(t, zoom=1.0, focus=None):
    c = SH["cta"]
    if "bg" not in TG._ST:
        TG._ST["bg"] = TG.background(lib)
        TG.prepare(COMMON)
        lib.static_done()
    lib.dyn_begin()
    body, (cx, cy, s, rot) = TG.layer(t, c["t0"], c["press"], COMMON)
    if focus:
        cx, cy = cx + (focus[0] - cx) * .3, cy + (focus[1] - cy) * .3
    return lib.svg(f'<rect width="1080" height="1920" fill="#6e4a32"/><g transform="{lib.cam(cx, cy, s * zoom, rot)}">{TG._ST["bg"]}{body}</g>{over(t)}')


def frame_s15(t):
    return cta(t)


def frame_s16(t):
    return cta(t, 1.1, (540, 1000))


def frame_s17(t):
    return cta(t, 1.04)


def frame_s18(t):
    """Петля: кадр хука — календарь на 30 дней, кот внизу готов к прыжку."""
    a, b = T0("s18"), T1("s18")
    o = room(t)
    o.append(cal30(600, 1000, 1.0))
    o.append(cat(900, 1700, .8, t, dict(look=(-.8, -.6), smile=.8, perk=1.0)))
    return loop_view("".join(o), t, a, b, HIT, 560, 1080, 1.05)


def frame(sid, t):
    if sid not in ("s15", "s16", "s17"):
        lib.DEFS.clear()
    return globals()["frame_" + sid](t)
