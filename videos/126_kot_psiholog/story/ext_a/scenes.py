"""Рилс 126 «Кот-психолог принимает», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json (общая дорожка voice_merge.py). Это шутка: без диагнозов и обещаний вылечить.
Кабинет: уютное кресло, кот-психолог в круглых очках, вязаном кардигане и маленькой бабочке, с блокнотом и ручкой; кушетка,
настольный звонок, дверь. Дима, пациентки «girl» и «bob». NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

HIT = stress(3, .4)
CHAIR = (760.0, RFL)          # кресло кота
COUCH = (300.0, RFL)          # кушетка
KNIT, KNIT_D = "#c9824a", "#a5663a"


def psy_cat(x, y, k, t, st=None, pen=0.0, note="", note_u=0.0, glasses=True):
    """Кот-психолог: кардиган крупной вязки, бабочка, круглые очки, блокнот в лапах (note — что написано, note_u — показывает)."""
    st = dict(dict(look=(-.5, -.1), smile=.5, tail=8 * math.sin(t * 1.7)), **(st or {}))
    o = [cat(x, y, k, t, st)]
    cx, ny, by = CT.CX, CT.NECK[1], CT.CBOT
    cardi = shape([(cx - 70, ny - 6, 1), (cx + 70, ny - 6, 1), (cx + 150, by - 10, 1), (cx + 40, by, 1), (cx - 40, by, 1), (cx - 150, by - 10, 1)], KNIT,
                  "".join(line([(cx - 120 + 30 * j, ny + 30), (cx - 130 + 32 * j, by - 20)], 3, KNIT_D, taper=0, wmin=1, seed=6000 + j) for j in range(9))
                  + blob([(cx - 30, ny), (cx + 30, ny), (cx + 20, by), (cx - 20, by)], "#3b4143"), w=4.4, seed=6010)
    for j in range(3):
        cardi += shape(ellipse_pts(cx + 34, ny + 50 + 40 * j, 7, 7, 8), "#6b432b", "", w=2, seed=6011 + j)
    bow = shape([(cx, ny + 8, 1), (cx - 40, ny - 14, 1), (cx - 40, ny + 30, 1)], "#d8352a", "", w=3, seed=6020)
    bow += shape([(cx, ny + 8, 1), (cx + 40, ny - 14, 1), (cx + 40, ny + 30, 1)], "#d8352a", "", w=3, seed=6021)
    bow += shape(ellipse_pts(cx, ny + 8, 10, 10, 10), "#b02a20", "", w=3, seed=6022)
    gl = ""
    if glasses:
        for ex in (-46, 46):
            ring_ = [tuple(p_) for p_ in ellipse_pts(cx + ex, 1062, 36, 36, 20)]
            gl += line(ring_ + [ring_[0]], 8, "#5a3a20", seed=6030)
        gl += line([(cx - 12, 1060), (cx + 12, 1060)], 4, "#5a3a20", seed=6031)
    o.append(f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-cx} {-by})">{cardi}{bow}{gl}</g>')
    # блокнот и ручка
    show = clamp(note_u)
    nx, ny_ = x - 60 * k - 280 * k * show, y - 60 * k - 200 * k * show
    w_, h_ = 150 + 120 * show, 190 + 80 * show
    pad = shape(lib.rect_pts(-w_ / 2, -h_ / 2, w_ / 2, h_ / 2), "#fffdf4", "", w=3.4, seed=6040)
    pad += rect(-w_ / 2, -h_ / 2, w_ / 2, -h_ / 2 + 22, "#e2453a")
    for j in range(4):
        pad += line([(-w_ / 2 + 16, -h_ / 2 + 50 + 34 * j), (w_ / 2 - 16, -h_ / 2 + 50 + 34 * j)], 2, "#c9d7ea", taper=0, wmin=1, seed=6041 + j)
    if note and show > .05:
        for j, ln in enumerate(note.split("\n")):
            pad += plain(ln, 0, -h_ / 2 + 90 + 64 * j, 52, fill="#1d2448", anchor="middle")
    o.append(tf(pad, nx, ny_, k * (1 + .5 * show), -8 + 8 * show))
    pa = -30 + 20 * math.sin(t * 12) * pen
    if show < .3:
        o.append(tf(shape(lib.rrect(-8, -110, 8, 0, 6), "#2f6fd1", "", w=3, seed=6050), nx + 60 * k, ny_ + 20 * k, k, pa))
    return "".join(o)


def armchair(x, y, k=1.0):
    o = shape(lib.rrect(-190, -560, 190, -200, 60), "#5f8f7a", blob(lib.rrect(-150, -520, 150, -240, 40), "#6fa58a", .6), w=5, seed=6100)
    o += shape(lib.rrect(-220, -320, -140, -60, 30), "#527c6a", "", w=5, seed=6101)
    o += shape(lib.rrect(140, -320, 220, -60, 30), "#527c6a", "", w=5, seed=6102)
    o += shape(lib.rrect(-160, -240, 160, -100, 30), "#6fa58a", "", w=5, seed=6103)
    for s_ in (-1, 1):
        o += line([(s_ * 170, -60), (s_ * 180, 0)], 12, "#6b432b", taper=0, wmin=1, seed=6104 + s_)
    return tf(o, x, y, k)


def couch(x, y, k=1.0):
    o = shape(lib.rrect(-300, -260, -170, -60, 40), "#b5657a", "", w=5, seed=6110)
    o += shape(lib.rrect(-300, -150, 300, -40, 30), "#c97a8e", blob(lib.rrect(-280, -140, 280, -100, 20), "#d993a5", .6), w=5, seed=6111)
    for s_ in (-1, 1):
        o += line([(s_ * 270, -40), (s_ * 280, 0)], 12, "#6b432b", taper=0, wmin=1, seed=6112 + s_)
    o += shape(ellipse_pts(-210, -170, 60, 40, 16), "#f4f1ea", "", w=4, seed=6114)
    return tf(o, x, y, k)


def bell(x, y, k, u=0.0):
    o = shape(lib.rrect(-70, -14, 70, 6, 6), "#7d8597", "", w=4, seed=6120)
    o += shape([(-60, -14, 1), (-40, -70, 1), (0, -84, 1), (40, -70, 1), (60, -14, 1)], "#e8c25a", blob(ellipse_pts(-20, -50, 14, 20, 10), "#fff1b0"), w=4,
               seed=6121)
    o += shape(lib.rect_pts(-6, -108 + 16 * u, 6, -84), "#5a5f6e", "", w=3, seed=6122)
    o += shape(ellipse_pts(0, -112 + 16 * u, 14, 8, 10), "#5a5f6e", "", w=3, seed=6123)
    if u > 0:
        o += PR.ring_arcs(0, -60, .7, u, 0.0, seed=4, r=120)
    return tf(o, x, y, k)


def office(t, door=0.0, queue=False):
    o = [plain_room(t, wall="#efe0c8")]
    o.append(PR.window(560, 900, 300, 360, mode="day", t=t, seed=5, curtain=False))
    o.append(shape(lib.rect_pts(820, 620, 1000, 760), "#fbf8f1", PR.heart(910, 690, .6, seed=1), w=4, seed=6130))
    o.append(PR.door(-80, RFL, 1.0, ajar=door, seed=4))
    if queue and door > .2:
        for j in range(3):
            o.append(people.figure(["girl", "bob", "beard"][j], -20 - 110 * j, RFL - 330, .45,
                                   expr={"brows": "up", "mouth": "flat", "lid": .9, "look": (.8, 0)},
                                   feet=people.stand_kw(-20 - 110 * j, RFL - 330, .45, ["girl", "bob", "beard"][j])["feet"])["svg"])
    o.append(rug(540, RFL + 150, 620, "#8fb39b", "#a7c7b1"))
    o.append(couch(*COUCH))
    o.append(armchair(*CHAIR))
    o.append(PR.plant(1000, RFL, 1.0, seed=2) if hasattr(PR, "plant") else "")
    o.append(shape(lib.rect_pts(540, RFL - 260, 660, RFL), "#a8774a", "", w=4, seed=6131))
    return o


def cat_in_chair(t, **kw):
    return psy_cat(CHAIR[0], CHAIR[1] - 230, 1.0, t, **kw)


def dima_couch(t, expr="calm82", lie=False, **kw):
    k = .66
    hip = COUCH[1] - 130
    if lie:
        return people.dima_bed(COUCH[0] + 40, COUCH[1] - 150, .6, expr=expr, t=t, cover="none", col="blue")
    return people.dima82(COUCH[0], hip, k, expr, kw.pop("pose", "d82_rest"), t=t, feet=people.sit_kw(COUCH[0], hip, k)["feet"], **kw)


def bubble(x, y, w, h, u, words_, tail=(-60, 70), size=48):
    if u <= .02:
        return ""
    o = PR.speech_bubble(x, y, w, h, u, seed=5, tail=tail)
    if u > .8:
        for j, ln in enumerate(words_.split("\n")):
            o += plain(ln, x, y + 16 + (j - (len(words_.split("\n")) - 1) / 2) * size * 1.1, size, fill="#1d2448", anchor="middle")
    return o


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: дверь кабинета распахивается, Дима в дверях, в кресле кот-психолог в очках и кардигане поднимает взгляд от блокнота."""
    o = office(t, door=ease_out(clamp((t + .3) / .5)))
    o.append(cat_in_chair(t, st=dict(look=(-.9, -.3), perk=1.0), pen=1.0))
    f = stand(250, t, "wow82", "d82_rest", head_add=.05)
    o.append(f["svg"])
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 540, 1010, 1.12, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«а там кот»: у Димы отвисла челюсть, кот поправляет очки и мило улыбается."""
    a, b = T0("s02"), T1("s02")
    o = office(t, door=1.0)
    o.append(cat_in_chair(t, st=dict(look=(-.9, -.2), smile=1.0, tilt=6 * bump(t, W(6), .1, .5))))
    f = stand(220, t, "wow82", "d82_shrug", head_add=.06 * bump(t, W(6), .05, .3))
    o.append(f["svg"])
    hx, hy = f["head"]
    if t > W(6):
        o.append(text("!", hx + 40, hy - 220, 180 * pop(t, W(6), .2), fill="#e2453a", stroke="#111", sw=10))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(6), 10)
    return view("".join(o), 520 + dx, 1010 + dy, 1.12 + .04 * u, 0, t=t)


def frame_s03(t):
    """Кот: «На что жалуемся?» — кот крупно в кресле, ручка у блокнота, пузырь с вопросом."""
    a, b = T0("s03"), T1("s03")
    o = office(t, door=1.0)
    o.append(cat_in_chair(t, st=dict(look=(-.6, -.2), smile=.8, tilt=-4), pen=1.0))
    o.append(bubble(560, 820, 520, 220, pop(t, a, .2), "На что\nжалуемся?", tail=(120, 90)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 700, 1080, 1.5 + .06 * u, 0, t=t)


def frame_s04(t):
    """Дима на кушетке: «Не могу начать дела» — сидит, руки разводит; кот записывает."""
    a, b = T0("s04"), T1("s04")
    o = office(t, door=0.0)
    o.append(cat_in_chair(t, st=dict(look=(-.8, .1)), pen=1.0))
    o.append(dima_couch(t, dict(people.EXPR["dima"]["guilty"], look=(.8, -.1)), pose="d82_shrug")["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(13), 6)
    return view("".join(o), 520 + dx, 1180 + dy, 1.15 + .06 * u, 0, t=t)


def frame_s05(t):
    """«Сажусь и сразу листаю ленту»: над Димой облачко — телефон, лента бежит вверх."""
    a, b = T0("s05"), T1("s05")
    o = office(t, door=0.0)
    o.append(cat_in_chair(t, st=dict(look=(-.8, -.3)), pen=1.0))
    f = dima_couch(t, dict(people.EXPR["dima"]["guilty"], look=(.2, -.8)), pose="d82_rest")
    o.append(f["svg"])
    hx, hy = f["head"]
    sc = ((t - a) * 400) % 120
    inner = shape(lib.rrect(-70, -120, 70, 120, 18), "#2a2d36", "", w=3, seed=6140)
    feed = "".join(shape(lib.rrect(-56, -150 + 60 * j - sc, 56, -110 + 60 * j - sc, 8), ["#9fc2e8", "#ffd27a", "#d6c7f0", "#9fe0a4"][j % 4], "", w=2,
                         seed=6141 + j) for j in range(7))
    c = lib.clip_rect(-58, -106, 116, 212, 10)
    inner += f'<g clip-path="url(#{c})">{feed}</g>'
    o.append(PR.thought_cloud(hx + 200, hy - 260, 1.3, w=300, h=320, u=pop(t, a, .25), seed=3, inner=inner))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(17), 6)
    return view("".join(o), 480 + dx, 1100 + dy, 1.15 + .06 * u, 0, t=t)


def frame_s06(t):
    """Кот: «Начните с двух минут» — пишет в блокноте «2 минуты» и разворачивает листок к Диме."""
    a, b = T0("s06"), T1("s06")
    show = ease_out(ramp(t, W(21), .35))
    o = office(t)
    o.append(cat_in_chair(t, st=dict(look=(-.7, 0), smile=.9), pen=1 - show, note="2\nминуты", note_u=show))
    o.append(PR.sparkles(560, 960, 1.6, bump(t, W(22), .05, .5), t, seed=61, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1080, 1.3 + .05 * u, 0, t=t)


def frame_s07(t):
    """«Следующий!»: кот лапой жмёт звонок, Дима подлетает с кушетки к двери."""
    a, b = T0("s07"), T1("s07")
    tb = W(23) + .05
    o = office(t, door=ease_out(ramp(t, tb, .3)))
    o.append(bell(600, RFL - 260, 1.2, bump(t, tb, .03, .3)))
    o.append(cat_in_chair(t, st=dict(look=(-.8, .3), smile=1.0, paw=bump(t, tb - .1, .08, .3))))
    fly = ease_in2(ramp(t, tb + .15, .5))
    if fly < .01:
        o.append(dima_couch(t, dict(people.EXPR["dima"]["guilty"], look=(.8, -.1)))["svg"])
    else:
        k = .66
        hip = COUCH[1] - 130 - 200 * math.sin(math.pi * fly)
        o.append(people.dima82(COUCH[0] - 380 * fly, hip, k, "wow82", "d82_shrug", t=t, feet=people.sit_kw(COUCH[0], hip, k)["feet"])["svg"])
        o.append(PR.speed_arcs(COUCH[0] + 120 - 380 * fly, hip - 200, 1.2, 1.0, t, seed=7, n=3, ang=0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 12)
    return view("".join(o), 500 + dx, 1100 + dy, 1.1 + .06 * u, 0, t=t)


def woman(style, t, expr, pose_feet="sit", x=None, k=.62):
    x = COUCH[0] if x is None else x
    hip = COUCH[1] - 130
    feet = people.sit_kw(x, hip, k, style)["feet"]
    return people.figure(style, x, hip, k, expr=expr, feet=feet)


def frame_s08(t):
    """Пациентка: «А я всё откладываю на понедельник» — сидит на кушетке, над ней облачко с листком «ПН»; кот слушает."""
    a, b = T0("s08"), T1("s08")
    o = office(t)
    o.append(cat_in_chair(t, st=dict(look=(-.8, -.1)), pen=1.0))
    talk = abs(math.sin(t * 11)) if t < WE(29) else 0
    f = woman("girl", t, {"brows": "worry", "mouth": "talk", "open": .2 + .4 * talk, "lid": .9, "look": (.7, -.1)})
    o.append(f["svg"])
    hx, hy = f["head"]
    cal = shape(lib.rect_pts(-70, -80, 70, 80), "#fbf8f1", blob(lib.rect_pts(-70, -80, 70, -40), "#c8553d") + text("ПН", 0, 50, 70, fill="#1d2448",
                                                                                                             stroke="#ffffff", sw=4), w=3, seed=6150)
    o.append(PR.thought_cloud(hx + 200, hy - 240, 1.2, w=260, h=240, u=pop(t, W(28) - .2, .25), seed=4, inner=cal))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(29), 6)
    return view("".join(o), 520 + dx, 1100 + dy, 1.15 + .06 * u, 0, t=t)


def frame_s09(t):
    """Кот: «Две минуты сегодня» — разворачивает листок «2 минуты сегодня»."""
    a, b = T0("s09"), T1("s09")
    show = ease_out(ramp(t, a - .35, .3))
    o = office(t)
    o.append(cat_in_chair(t, st=dict(look=(-.7, 0), smile=.9), note="2 минуты\nсегодня", note_u=show))
    o.append(PR.sparkles(560, 960, 1.6, bump(t, W(32), .05, .5), t, seed=91, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1080, 1.3 + .05 * u, 0, t=t)


def frame_s10(t):
    """«Следующий!»: звонок, пациентка встаёт и машет на прощание, дверь открывается."""
    a, b = T0("s10"), T1("s10")
    tb = W(33) + .05
    o = office(t, door=ease_out(ramp(t, tb, .3)))
    o.append(bell(600, RFL - 260, 1.2, bump(t, tb, .03, .3)))
    o.append(cat_in_chair(t, st=dict(look=(-.8, .3), smile=1.0, paw=bump(t, tb - .1, .08, .3))))
    up = ease_out(ramp(t, tb + .1, .3))
    k = .62
    hip = COUCH[1] - 130 - 120 * up
    feet = people.sit_kw(COUCH[0], COUCH[1] - 130, k, "girl")["feet"] if up < .5 else people.stand_kw(COUCH[0], hip, k, "girl")["feet"]
    o.append(people.figure("girl", COUCH[0] - 60 * up, hip, k, expr={"brows": "up", "mouth": "smile", "smile": .8, "lid": .9, "look": (.6, 0)},
                           feet=feet)["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 10)
    return view("".join(o), 500 + dx, 1100 + dy, 1.1 + .06 * u, 0, t=t)


def frame_s11(t):
    """Третья пациентка: «А я…» — только открыла рот, кот поднимает лапу «стоп»."""
    a, b = T0("s11"), T1("s11")
    o = office(t)
    o.append(cat_in_chair(t, st=dict(look=(-.8, 0), smile=.6, paw=ease_out(ramp(t, W(35), .2)), paw_dx=-40)))
    o.append(woman("bob", t, {"brows": "up", "mouth": "o", "open": .5, "lid": 1.0, "look": (.8, -.2)})["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(35), 6)
    return view("".join(o), 520 + dx, 1100 + dy, 1.15 + .06 * u, 0, t=t)


def frame_s12(t):
    """Кот: «Две минуты» — листок «2 минуты» ей в лицо, пациентка моргает."""
    a, b = T0("s12"), T1("s12")
    show = ease_out(ramp(t, a - .35, .3))
    o = office(t)
    o.append(woman("bob", t, {"brows": "up", "mouth": "o", "open": .3, "lid": 1.0, "look": (.8, -.2)}, x=110)["svg"])
    o.append(cat_in_chair(t, st=dict(look=(-.7, 0), smile=.9), note="2\nминуты", note_u=show))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 500, 1100, 1.15 + .05 * u, 0, t=t)


def frame_s13(t):
    """«Следующий!»: звонок, дверь распахивается — за ней очередь из пациентов."""
    a, b = T0("s13"), T1("s13")
    tb = W(38) + .05
    o = office(t, door=ease_out(ramp(t, tb - .1, .3)), queue=True)
    o.append(bell(600, RFL - 260, 1.2, bump(t, tb, .03, .3)))
    o.append(cat_in_chair(t, st=dict(look=(-.9, .1), smile=1.0, paw=bump(t, tb - .1, .08, .3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 12)
    return view("".join(o), 360 + dx, 1150 + dy, 1.0 + .05 * u, 0, t=t)


def frame_s14(t):
    """Дима: «Я думал, это шутка» — дома за столом смеётся над листком «2 минуты»."""
    a, b = T0("s14"), T1("s14")
    o = desk_room(t)
    o.append(tf(shape(lib.rect_pts(-90, -110, 90, 110), "#fffdf4", plain("2", 0, -10, 70, fill="#1d2448", anchor="middle")
                      + plain("минуты", 0, 60, 40, fill="#1d2448", anchor="middle"), w=3, seed=6160), 640, DESK_Y - 120, 1.2, -6))
    o.append(dima_desk(t, "laugh82", head_add=.06 * math.sin(t * 10), lean=0.0)["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(42), 6)
    return view("".join(o), 520 + dx, 850 + dy, 1.4 + .06 * u, 0, t=t)


def frame_s15(t):
    """«Но через две минуты я правда начал»: Дима печатает за ноутбуком, таймер 2:00 добегает, кот-психолог рядом кивает."""
    a, b = T0("s15"), T1("s15")
    o = desk_room(t, sun=1.0)
    o.append(PR.laptop(640, DESK_Y - 8, 1.0, screen="lines", lines=clamp((t - a) / (b - a)), t=t, seed=1))
    tap = math.sin(t * 30)
    o.append(dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.9, -.1)), lean=.18,
                       arms={"f": ("ik", (560 + 10 * tap, DESK_Y - 30), 1), "n": ("ik", (640 - 10 * tap, DESK_Y - 25), 1)})["svg"])
    o.append(psy_cat(960, DESK_Y - 4, .5, t, st=dict(look=(-.8, -.2), smile=1.0, tilt=4 * math.sin(t * 6))))
    left = max(0.0, 120 * (1 - clamp((t - a) / (W(49) - a))))
    m, s_ = int(left // 60), int(left % 60)
    o.append(tf(shape(ellipse_pts(0, 0, 110, 110, 30), "#ffffff", text(f"{m}:{s_:02d}", 0, 26, 74, fill="#1d2448", stroke="#ffffff", sw=4), w=5,
                      seed=6170), 400, 560, 1.0 + .2 * bump(t, W(49), .05, .3)))
    o.append(PR.sparkles(640, 700, 1.8, bump(t, W(49), .05, .5), t, seed=151, n=6, r=240))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(49), 6)
    return view("".join(o), 600 + dx, 820 + dy, 1.35 + .06 * u, 0, t=t)


def frame_s16(t):
    return cta_code(t, T0("s16"), T1("s16"))


def frame_s17(t):
    """«чтобы твои две минуты начались сегодня»: кот-психолог крупно протягивает листок «2 минуты сегодня» к зрителю, на листке тикает таймер."""
    a, b = T0("s17"), T1("s17")
    show = ease_out(ramp(t, a - .35, .3))
    o = office(t)
    o.append(cat_in_chair(t, st=dict(look=(0, 0), smile=1.0), note="2 минуты\nсегодня", note_u=show))
    o.append(PR.sparkles(560, 960, 1.8, bump(t, W(58), .05, .5), t, seed=171, n=7, r=260))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1100, 1.3 + .06 * u, 0, t=t)


def frame_s18(t):
    """Петля: кадр хука — дверь кабинета, кот в кресле."""
    a, b = T0("s18"), T1("s18")
    o = office(t, door=0.0)
    o.append(cat_in_chair(t, st=dict(look=(-.9, -.3)), pen=1.0))
    o.append(stand(250, t, "wow82", "d82_rest", head_add=.05)["svg"])
    return loop_view("".join(o), t, a, b, HIT, 540, 1010, 1.12)


def ease_in2(u):
    return u * u


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
