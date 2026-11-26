"""Рилс 113 «Не перебиваю», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Место: Дима слева, друг (борода) справа,
пузыри речи над ними; кафе в итоге. NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

HIT = stress(1, .4)
DX, FX = 270.0, 830.0                  # Дима и друг
FB = (690.0, 420.0)                    # пузырь друга
DB = (330.0, 450.0)                    # пузырь Димы


def friend(t, expr=None, k=.72, x=FX, arms=None, fl=RFL, sit=False):
    sc = k * people.HEIGHT.get("beard", 1.0)
    if sit:
        hip = fl
        feet = people.sit_kw(x, hip, k, "beard")["feet"]
    else:
        hip = fl - (people.LEG_LEN - 12) * sc - 6
        feet = people.stand_kw(x, hip, k, "beard")["feet"]
    e = expr or {"brows": "up", "mouth": "talk", "open": .3 + .3 * abs(math.sin(t * 11)), "lid": .9, "look": (-.6, -.1)}
    kw = {"arms": arms} if arms else {}
    return people.figure("beard", x, hip, k, expr=e, feet=feet, flip=True, head_ang=.03 * math.sin(t * 3), **kw)


def talk_e(t, look=(-.6, -.1), brows="up"):
    return {"brows": brows, "mouth": "talk", "open": .25 + .35 * abs(math.sin(t * 11)), "lid": .9, "look": look}


def bubble(x, y, w, h, u, tail, lines=3, write=1.0, seed=0, col="#3a4157", dot=False, inner=""):
    """Пузырь речи с волнистыми строчками (речь без букв)."""
    if u <= .02:
        return ""
    o = PR.speech_bubble(0, 0, w, h, 1.0, seed=seed, tail=tail)
    for j in range(lines):
        q = clamp(write * lines - j)
        if q <= 0:
            break
        y0 = -h * .25 + j * h * .5 / max(1, lines - 1) if lines > 1 else 0
        x0, x1 = -w * .34, -w * .34 + w * .68 * q * (1 - .2 * (j == lines - 1))
        pts = [(x0 + (x1 - x0) * i / 10, y0 + 5 * math.sin(i * 1.7 + j + seed)) for i in range(11)]
        o += line(pts, 7, col, taper=.2, wmin=.5, seed=1300 + 10 * seed + j)
        if dot and j == lines - 1 and q >= 1:
            o += blob(ellipse_pts(x1 + 22, y0, 9, 9, 10), col)
    o += inner
    s = lib.back_out(clamp(u), 2.0) if u < 1 else 1.0
    return tf(o, x, y, s)


def cracked(x, y, w, h, split, tail, seed=0):
    """Пузырь друга, расколотый пополам: половинки разлетаются (split 0…1), зигзаг трещины."""
    full = bubble(0, 0, w, h, 1.0, tail, seed=seed)
    o = []
    zig = [(0, -h / 2 - 10), (-18, -h * .25), (16, -h * .05), (-14, h * .15), (12, h * .35), (0, h / 2 + 10)]
    for side in (-1, 1):
        pts = [(side * (w / 2 + 40), -h / 2 - 60)] + zig + [(side * (w / 2 + 40), h / 2 + 90)]
        c = lib.clip_of(pts)
        o.append(f'<g transform="translate({side * 120 * split:.1f} {40 * split * split:.1f}) rotate({side * 18 * split:.2f})">'
                 f'<g clip-path="url(#{c})">{full}</g></g>')
    if split < .5:
        o.append(line(zig, 6, INK, taper=.2, wmin=.5, seed=1400))
    return tf("".join(o), x, y, 1.0)


def talk_room(t, cafe=False):
    if cafe:
        o = [plain_room(t, wall="#f3dcc0")]
        o.append(PR.window(540, 900, 360, 420, mode="day", t=t, seed=5, curtain=False))
        return o
    o = [plain_room(t)]
    o.append(rug(550, RFL + 150, 600))
    o.append(PR.window(550, 1000, 300, 380, mode="day", t=t, seed=4, curtain=False))
    return o


def dima_s(t, expr="calm82", pose="d82_rest", x=DX, **kw):
    return stand(x, t, expr, pose, k=.72, **kw)


def mute(x, y, u):
    """Красный крест поверх пузыря Димы."""
    o = PR.cross_stroke((x - 90, y - 70), (x + 90, y + 70), (x + 90, y - 70), (x - 90, y + 70), u=u, w=26, seed=3)
    return o


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: друг говорит, пузырь Димы влетает сбоку и раскалывает пузырь друга пополам."""
    hit = W(1) + .1
    o = talk_room(t)
    o.append(friend(t, talk_e(t) if t < hit else {"brows": "up", "mouth": "o", "open": .7, "lid": 1.0, "look": (-.8, -.3)})["svg"])
    o.append(dima_s(t, "rush82", "d82_one", head_add=.05)["svg"])
    if t < hit:
        o.append(bubble(*FB, 480, 250, 1.0, (60, 80), lines=3, write=.5 + t, seed=1))
    else:
        o.append(cracked(*FB, 480, 250, ease_out(ramp(t, hit, .4)), (60, 80), seed=1))
    fly = ease_in_(clamp((t + .25) / (hit + .25)))
    bx = -200 + (FB[0] - 210 - (-200)) * fly
    o.append(bubble(bx, DB[1] - 40 * fly, 320, 220, 1.0, (-40, 80), lines=2, seed=2, col="#d8352a"))
    o.append(PR.sparkles(FB[0] - 60, FB[1], 1.8, bump(t, hit, .04, .4), t, seed=11, n=7, r=200))
    dx, dy = shake(t, hit, 14)
    return hook_view("".join(o), t, HIT, 560, 900, 1.05, 0, dx=dx, dy=dy)


def ease_in_(u):
    return u * u


def frame_s02(t):
    """«перестал перебивать людей»: пузырь Димы перечёркивается и улетает, пузырь друга целый и растёт, Дима кивает."""
    a, b = T0("s02"), T1("s02")
    tx = W(3)
    o = talk_room(t)
    o.append(friend(t)["svg"])
    nod = .06 * math.sin((t - a) * 9) * ramp(t, W(4), .2)
    o.append(dima_s(t, dict(people.EXPR["dima"]["calm_smile"], look=(.8, -.2)), "d82_rest", head_add=nod)["svg"])
    o.append(bubble(*FB, 460 * (1 + .15 * ramp(t, a, .5)), 300, 1.0, (60, 80), lines=3, write=clamp((t - a) / 1.2), seed=1))
    away = ease_in_(ramp(t, tx + .3, .4))
    if away < 1:
        o.append(tf(bubble(0, 0, 320, 220, 1.0, (-40, 80), lines=2, seed=2, col="#d8352a") + mute(0, 0, ramp(t, tx, .25)),
                    DB[0] - 600 * away, DB[1] + 80 - 300 * away, 1.0 - .5 * away, -40 * away))
    o.append(PR.check_mark(FB[0] + 200, FB[1] - 160, 2.2, ramp(t, W(4), .3), w=10))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tx, 8)
    return view("".join(o), 560 + dx, 900 + dy, 1.05 + .06 * u, 1 - 2 * u, t=t)


def frame_s03(t):
    """«вставлял слово посреди фразы»: друг тянет длинную фразу, пузырь Димы врезается в середину, строчки рвутся."""
    a, b = T0("s03"), T1("s03")
    hit = W(9)
    o = talk_room(t)
    o.append(friend(t, talk_e(t) if t < hit else {"brows": "frown", "mouth": "o", "open": .5, "lid": 1.0, "look": (-.8, -.1)})["svg"])
    o.append(dima_s(t, "rush82" if t > W(7) else "calm82", "d82_one" if t > W(7) else "d82_rest")["svg"])
    if t < hit:
        o.append(bubble(*FB, 520, 250, 1.0, (60, 80), lines=3, write=clamp((t - a) / (hit - a) * .6), seed=1))
    else:
        o.append(cracked(*FB, 520, 250, .35 * ease_out(ramp(t, hit, .3)), (60, 80), seed=1))
    if t > W(7) - .1:
        fly = ease_out(ramp(t, W(7) - .1, hit - W(7) + .1))
        o.append(bubble(DB[0] + 260 * fly, DB[1] - 30 * fly, 300, 200, 1.0, (-40, 80), lines=2, seed=2, col="#d8352a"))
    o.append(PR.sparkles(FB[0], FB[1], 1.6, bump(t, hit, .04, .4), t, seed=31, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, hit, 12)
    return view("".join(o), 560 + dx, 900 + dy, 1.05 + .08 * u, 0, t=t)


def frame_s04(t):
    """«забывал мысль, если молчал»: над Димой облачко с лампочкой — пока друг говорит, оно тает, остаётся «?»."""
    a, b = T0("s04"), T1("s04")
    fade = ramp(t, W(12), W(14) - W(12) + .2)
    o = talk_room(t)
    o.append(friend(t)["svg"])
    f = dima_s(t, "puzzled82" if fade > .6 else "calm82", "d82_rest", head_add=-.05)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(bubble(FB[0] + 60, FB[1] - 40, 440, 280, 1.0, (40, 80), lines=3, write=clamp((t - a) / 1.0), seed=1))
    cl = PR.idea_bulb(0, 0, 1.0, on=1 - fade, t=t) if fade < .9 else PR.question_mark(0, 0, 1.6, ramp(t, W(14), .25), col="#e2453a")
    if fade < .99:
        o.append(f'<g opacity="{1 - .7 * fade:.3f}">' + PR.thought_cloud(hx + 40, hy - 260, 1.1 * (1 - .3 * fade), u=pop(t, a, .2), seed=3,
                                                                    inner=cl) + "</g>")
    else:
        o.append(PR.thought_cloud(hx + 40, hy - 260, .8, u=1.0, seed=3, inner=cl))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(14), 8)
    return view("".join(o), 520 + dx, 900 + dy, 1.05 + .08 * u, 0, t=t)


def frame_s05(t):
    """«а друзья обижались»: друг скрестил руки и отвернулся, над ним тучка; Дима растерян."""
    a, b = T0("s05"), T1("s05")
    o = talk_room(t)
    tu = ease_out(ramp(t, a, .35))
    arms = {"f": ("ik", (FX - 60, 1020), 1), "n": ("ik", (FX + 40, 1000), -1)}
    ff = friend(t, {"brows": "frown", "mouth": "pressed", "lid": .7, "look": (.9, 0)}, arms=arms)
    o.append(ff["svg"])
    hx, hy = ff["head"]
    o.append(PR.cloud(hx, hy - 220, 300 * tu + 1, 160 * tu + 1, seed=5, col="#7d8597"))
    o.append(PR.rain(hx - 120, hy - 200, 240, t, a, n=6, seed=2, k=.8, floor=hy - 60))
    o.append(dima_s(t, "panic82", "d82_shrug")["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(17), 8)
    return view("".join(o), 560 + dx, 900 + dy, 1.05 + .08 * u, 0, t=t)


def frame_s06(t):
    """«Вот что я поменял»: Дима поднимает палец, над ним лампочка; друг рядом; надпись сверху."""
    a, b = T0("s06"), T1("s06")
    ti = W(18) + .15
    o = talk_room(t)
    o.append(friend(t, {"brows": "up", "mouth": "flat", "lid": .9, "look": (-.6, -.2)})["svg"])
    f = dima_s(t, "wow82" if t > ti else "sure82", "d82_one", head_add=.06 * bump(t, ti, .08, .3))
    o.append(f["svg"])
    hx, hy = f["head"]
    if t > ti:
        o.append(PR.glow(hx + 170, hy - 200, 220, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx + 170, hy - 200 + 8 * math.sin(t * 5), 1.2 * pop(t, ti, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx + 170, hy - 200, 1.8, bump(t, ti, .05, .5), t, seed=61, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ti, 9)
    return view("".join(o), 520 + dx, 900 + dy, 1.05 + .05 * u, -1 + 2 * u, t=t)


def phone_note(x, y, k, word, typed, saved=0.0):
    """Телефон крупно: заметка, печатается слово, курсор."""
    o = shape(lib.rrect(-200, -380, 200, 380, 46), "#2a2d36", "", w=5, seed=1500)
    inner = blob(lib.rect_pts(-176, -350, 176, -270), "#ffe36e")
    inner += plain("Заметки", -150, -296, 44, fill="#1d2448")
    n = int(len(word) * clamp(typed))
    inner += plain(word[:n], -150, -180, 70, fill="#1d2448")
    cx = -150 + big_title_w(word[:n], 70)
    if typed < 1 or int(typed * 10) % 2 == 0:
        inner += rect(cx + 6, -236, cx + 12, -166, "#2f6fd1")
    for j in range(4):
        inner += line([(-150, -60 + 60 * j), (120 - 60 * (j % 2), -60 + 60 * j)], 5, "#d6d0c2", taper=.1, wmin=.8, seed=1510 + j)
    o += shape(lib.rrect(-176, -350, 176, 350, 30), "#fbf8f1", inner, w=3, seed=1501)
    if saved > 0:
        o += PR.check_mark(120, -200, 2.0, saved, w=10)
    return tf(o, x, y, k)


def big_title_w(s, size):
    import big_title
    return big_title.text_w(s, size) * .9 if s else 0.0


def frame_s07(t):
    """«Мысль сразу записываю одним словом в заметку»: лампочка мысли влетает в телефон, в заметке печатается «отпуск»."""
    a, b = T0("s07"), T1("s07")
    tf_ = W(23)
    o = [paper_bg()]
    o.append(phone_note(560, 980, 1.25, "отпуск", clamp((t - W(25)) / max(.3, W(27) - W(25))), saved=ramp(t, W(28), .3)))
    if t < tf_ + .35:
        fly = ease_in_(ramp(t, a, tf_ + .35 - a))
        o.append(PR.idea_bulb(300 + 260 * fly, 500 + 200 * fly, 1.6 * (1 - .6 * fly), on=1.0, t=t))
    o.append(PR.sparkles(560, 760, 1.8, bump(t, tf_ + .35, .05, .5), t, seed=71, n=6, r=220))
    k = .62
    f = people.dima82(170, 1660 - (people.LEG_LEN - 12) * k - 6, k, "sure82", "d82_one", t=t, feet="stand")
    o.append(f["svg"])
    o.append(cat(920, 1660, .8, t, dict(look=(-.6, -.7), smile=.8)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(28), 6)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


def frame_s08(t):
    """«и дослушиваю до конца»: друг договаривает, пузырь заполняется до точки, Дима кивает, рука на телефоне в кармане; галочка."""
    a, b = T0("s08"), T1("s08")
    o = talk_room(t)
    o.append(friend(t)["svg"])
    nod = .06 * math.sin((t - a) * 9)
    o.append(dima_s(t, dict(people.EXPR["dima"]["calm_smile"], look=(.8, -.2)), "d82_pocket", head_add=nod)["svg"])
    o.append(bubble(*FB, 500, 260, 1.0, (60, 80), lines=4, write=clamp((t - a + .2) / (W(32) - a)), seed=1, dot=True))
    o.append(PR.check_mark(FB[0] + 220, FB[1] - 170, 2.4, ramp(t, W(32), .3), w=10))
    o.append(PR.sparkles(FB[0] + 220, FB[1] - 170, 1.6, bump(t, W(32) + .2, .05, .5), t, seed=81, n=6, r=150))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(32), 7)
    return view("".join(o), 560 + dx, 900 + dy, 1.05 + .06 * u, 1 - 2 * u, t=t)


def frame_s09(t):
    return cta_code(t, T0("s09"), T1("s09"))


def frame_s10(t):
    """«чтобы тебя слушали»: Дима говорит, друг слушает с улыбкой и кивает, над ним сердечки."""
    a, b = T0("s10"), T1("s10")
    o = talk_room(t)
    ff = friend(t, {"brows": "up", "mouth": "smile", "smile": .8, "lid": .9, "look": (-.8, -.2)})
    o.append(ff["svg"])
    o.append(dima_s(t, talk_e(t, look=(.8, -.1)), "d82_one")["svg"])
    o.append(bubble(DB[0] + 130, DB[1] - 20, 420, 240, pop(t, a, .2), (-50, 80), lines=3, write=clamp((t - a) / .6), seed=2))
    hx, hy = ff["head"]
    for j in range(3):
        u = ramp(t, W(38) + .1 * j, .3)
        if u > 0:
            o.append(PR.heart(hx + 60 + 70 * j, hy - 160 - 120 * u, .6 + .2 * j, beat=u, seed=j))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 900, 1.05 + .06 * u, 0, t=t)


def frame_s11(t):
    """«а не терпели»: друг терпит — зевает и смотрит на часы, песочные часы сыплются; красный крест перечёркивает."""
    a, b = T0("s11"), T1("s11")
    o = talk_room(t)
    ff = friend(t, {"brows": "calm", "mouth": "yawn", "open": .8, "lid": .4, "look": (0, .4)})
    o.append(ff["svg"])
    o.append(dima_s(t, talk_e(t, look=(.8, -.1)), "d82_one")["svg"])
    o.append(bubble(DB[0] + 130, DB[1] - 20, 420, 240, 1.0, (-50, 80), lines=3, write=1.0, seed=2))
    hx, hy = ff["head"]
    o.append(PR.hourglass(hx + 40, hy - 260, 1.4, flow=1.0, top=1 - clamp((t - a) / (b - a)), t=t))
    xu = ramp(t, WE(41) - .1, .25)
    if xu > 0:
        o.append(PR.cross_stroke((hx - 80, hy - 400), (hx + 160, hy - 120), (hx + 160, hy - 400), (hx - 80, hy - 120), u=xu, w=34, seed=5))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, WE(41) + .1, 10)
    return view("".join(o), 600 + dx, 900 + dy, 1.05 + .06 * u, 0, t=t)


def cafe(t, fe, de, write=1.0, dot=False, heart=0.0):
    o = talk_room(t, cafe=True)
    ty = RFL - 330
    k = .66
    hip = ty + 20
    fd = people.dima82(260, hip, k, de, "d82_rest", t=t, feet=people.sit_kw(260, hip, k)["feet"], lean_add=.06,
                       head_add=.04 * math.sin(t * 6))
    ff = people.figure("beard", 820, hip, k, expr=fe, feet=people.sit_kw(820, hip, k, "beard")["feet"], flip=True,
                       head_ang=-.05 + .03 * math.sin(t * 3))
    o.append(PR.stool(260, hip + 40, .62, seed=1) + PR.stool(820, hip + 40, .62, seed=2))
    o.append(fd["svg"])
    o.append(ff["svg"])
    o.append(PR.desk(540, ty, w=560, depth=90, leg_h=320, seed=9))
    o.append(PR.coffee_mug(420, ty - 30, .7, steam=1.0, t=t, seed=1))
    o.append(PR.coffee_mug(680, ty - 30, .7, col="red", steam=1.0, t=t, seed=2))
    o.append(tf(shape(lib.rrect(-60, -24, 60, 24, 10), "#2a2d36", "", w=3, seed=1600), 550, ty - 14, 1.0, -4))
    hx, hy = ff["head"]
    o.append(bubble(hx - 160, hy - 300, 440, 260, 1.0, (100, 90), lines=3, write=write, seed=4, dot=dot))
    if heart > 0:
        o.append(PR.heart(hx - 160, hy - 300, 1.4 * pop(heart, 0, 1), beat=heart, seed=2))
    o.append(cat(560, ty - 30 - 140, .55, t, dict(look=(.7, -.3), smile=.8, tail=8 * math.sin(t * 3))) if False else "")
    return o, (hx, hy)


def frame_s12(t):
    """«Вчера друг договорил»: кафе, друг договаривает, пузырь до точки; Дима слушает; телефон на столе."""
    a, b = T0("s12"), T1("s12")
    o, _ = cafe(t, talk_e(t, look=(-.7, 0)), dict(people.EXPR["dima"]["calm_smile"], look=(.8, 0)),
                write=clamp((t - a + .3) / (W(44) + .3 - a)), dot=t > W(44) + .2)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(44) + .3, 6)
    return view("".join(o), 540 + dx, 1020 + dy, 1.12 + .06 * u, 0, t=t)


def frame_s13(t):
    """«и сказал: спасибо, что выслушал»: друг улыбается, в пузыре сердце; Дима смущённо улыбается; надпись «СПАСИБО»."""
    a, b = T0("s13"), T1("s13")
    th = W(47)
    o, (hx, hy) = cafe(t, {"brows": "up", "mouth": "grin", "open": .5, "lid": .8, "look": (-.8, 0)}, "laugh82", write=1.0 if t < th else 0.0,
                       heart=clamp((t - th) / .5) if t > th else 0.0)
    o.append(PR.sparkles(hx - 160, hy - 300, 2.0, bump(t, th + .1, .05, .5), t, seed=131, n=7, r=240))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, th + .1, 8)
    return view("".join(o), 560 + dx, 1000 + dy, 1.18 + .06 * u, 1 - 2 * u, t=t)


def frame_s14(t):
    """Петля: кадр хука — друг говорит, пузырь Димы на подлёте."""
    a, b = T0("s14"), T1("s14")
    o = talk_room(t)
    o.append(friend(t)["svg"])
    o.append(dima_s(t, "rush82", "d82_one", head_add=.05)["svg"])
    o.append(bubble(*FB, 480, 250, 1.0, (60, 80), lines=3, write=.5, seed=1))
    o.append(bubble(-200 - 100 * (1 - ramp(t, a, b - a)), DB[1], 320, 220, 1.0, (-40, 80), lines=2, seed=2, col="#d8352a"))
    return loop_view("".join(o), t, a, b, HIT, 560, 900, 1.05)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
