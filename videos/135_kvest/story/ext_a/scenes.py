"""Рилс 135 «Квест-комната», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json (общая дорожка voice_merge.py: Дима male2, кот-ведущий Даниил).
Квест-комната: тёмно-фиолетовая стена в кирпичах, лампа-прожектор, тяжёлая дверь с огромным навесным замком (лампочка
красная / зелёная), табло таймера над дверью, стол с ноутбуком, кресло-мешок. Кот — ведущий квеста в бордовой жилетке с
бабочкой и большим золотым ключом в правой лапе (common/costume.py «host», cat.WEAR: одежда и ключ внутри групп кота во всех
планах, и в призыве). Имя героя не звучит и не пишется. NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402
import costume  # noqa: E402

costume.use("host")
HIT = stress(1, .3)
WALLQ, WALLQ_D, FLOORQ = "#463a63", "#3a2f54", "#5b4a3e"
INK2 = "#1d2448"
DOOR_X = 300.0
CATX = 860.0


def room(t, lamp=1.0, open_=0.0, glow_=0.0):
    o = [rect(-1400, -1400, 2600, RFL, WALLQ)]
    for r in range(-12, 26):
        y = RFL - 70 * r
        o.append(line([(-1400, y), (2600, y)], 2.4, WALLQ_D, taper=0, wmin=1, seed=7000 + r, op=.9))
        for c in range(-12, 22):
            x = c * 150 + (75 if r % 2 else 0)
            o.append(line([(x, y), (x, y - 70)], 2.4, WALLQ_D, taper=0, wmin=1, seed=7100 + r * 40 + c, op=.9))
    o.append(rect(-1400, RFL, 2600, RFL + 1400, FLOORQ))
    o.append(line([(-1400, RFL), (2600, RFL)], 5, seed=11))
    if glow_ > 0:
        o.append(PR.glow(DOOR_X, RFL - 480, 700, .7 * glow_, "#fff1b0"))
    # дверь: проём светится, когда открыта
    if open_ > 0:
        o.append(rect(DOOR_X - 210, RFL - 936, DOOR_X + 210, RFL, "#fff4c8"))
        o.append(PR.beam(DOOR_X, RFL - 400, 0, 900, 40, open_, 1.0, "#fff1b0"))
    o.append(PR.door(DOOR_X, RFL, 1.0, ajar=open_, seed=4, col="#8a5a3a"))
    o.append(spot(t, lamp))
    return "".join(o)


def spot(t, u):
    if u <= 0:
        return ""
    return f'<g opacity="{.18 * u:.3f}"><path d="M540 -300 L-200 {RFL} L1300 {RFL} Z" fill="#fff6d8"/></g>'


def padlock(x, y, k, state="red", shake_=0.0, t=0.0, tag="", open_=0.0):
    """Огромный навесной замок: дужка, корпус, скважина, лампочка (red/green). open_ — дужка выскакивает."""
    j = shake_ * 10 * math.sin(t * 60)
    o = ""
    lift = 60 * open_
    o += line([(-70, -90 - lift), (-70, -170 - lift), (-40, -230 - lift), (40, -230 - lift), (70, -170 - lift), (70, -90 + 20 * (1 - open_) - lift * .3)],
              30, "#8a8f99", taper=0, wmin=1, seed=7200)
    o += line([(-70, -90 - lift), (-70, -170 - lift), (-40, -230 - lift), (40, -230 - lift), (70, -170 - lift)], 10, "#c9ced6", taper=0, wmin=1, seed=7201)
    o += shape(lib.rrect(-120, -100, 120, 120, 26), "#e0a83a", blob(lib.rect_pts(50, -96, 116, 116), "#b8862a", .8)
               + blob(ellipse_pts(-60, -60, 30, 16, 10), "#ffe08a", .8), w=5.4, seed=7202)
    o += shape([(0, -10), (-14, 16), (-8, 64, 1), (8, 64, 1), (14, 16)], "#2a2230", "", w=3, seed=7203) + f'<circle cx="0" cy="-10" r="20" fill="#2a2230"/>'
    col = {"red": "#ff3b30", "green": "#3fd26a"}.get(state, "#6b6f78")
    o += f'<circle cx="80" cy="-60" r="18" fill="{col}" stroke="#111" stroke-width="4"/>'
    if state in ("red", "green"):
        o += f'<circle cx="80" cy="-60" r="40" fill="{col}" opacity=".25"/>'
    if tag:
        o += line([(-100, 90), (-150, 170)], 4, "#2a2230", seed=7204)
        o += shape([(-250, 170, 1), (-60, 170, 1), (-40, 210, 1), (-60, 250, 1), (-250, 250, 1)], "#fff6d0",
                   text(tag, -150, 232, 56, fill=INK2, stroke="#fff6d0", sw=.01), w=4, seed=7205)
    return tf(o, x + j, y, k, j * .4)


def board(x, y, k, s_text, col="#ff5a3a"):
    """Табло таймера (LED): чёрная панель с цифрами."""
    o = shape(lib.rrect(-190, -80, 190, 80, 14), "#1a1620", blob(lib.rect_pts(-170, -60, 170, 60), "#0c0a10"), w=5, seed=7300)
    o += f'<text x="0" y="40" font-family="IDB" font-size="110" text-anchor="middle" fill="{col}" style="font-kerning:none">{s_text}</text>'
    o += f'<text x="0" y="40" font-family="IDB" font-size="110" text-anchor="middle" fill="{col}" opacity=".35" style="filter:blur(6px)">{s_text}</text>'
    for sx in (-1, 1):
        o += line([(sx * 140, -80), (sx * 160, -150)], 4, "#2a2230", seed=7301 + sx)
    return tf(o, x, y, k)


def elapsed(t):
    """Правило 11: на табло без бегущих чисел — пока дела нет, табло пустое."""
    return "--:--"


def host(t, x=CATX, y=RFL, k=1.0, st=None, key_up=0.0, glow=0.0):
    """Кот-ведущий в жилетке; key_up 0…1 — поднимает ключ (правая лапа вверх)."""
    st = dict(dict(look=(-.7, -.2), smile=.8, tail=8 * math.sin(t * 1.7)), **(st or {}))
    if key_up > 0:
        st.setdefault("paw", .95 * key_up)
        st.setdefault("paw_dx", 30.0)
    costume.KEY_STATE["glow"] = glow
    return cat(x, y, k, t, st)


def pedestal(x, k=1.0):
    return tf(shape(lib.rrect(-150, -120, 150, 0, 10), "#2c2438", blob(lib.rect_pts(-150, -120, 150, -100), "#5a4a78"), w=4, seed=7400), x, RFL, k)


def dima_door(t, pull=0.0, expr="panic82"):
    """Дима у двери тянет ручку (рука на ручке двери)."""
    k = .78
    x = DOOR_X + 330 + 30 * pull
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    return people.dima82(x, hip, k, expr, "d82_rest", t=t, feet="stand", flip=True, lean_add=-.12 * pull,
                         arms={"f": ("ik", (DOOR_X + 150 + 20 * pull, RFL - 470), 1), "n": ("ik", (DOOR_X + 170 + 20 * pull, RFL - 440), 1)})


def red_x(x, y, u, k=1.0):
    if u <= .01:
        return ""
    return PR.cross_stroke((x - 90 * k, y - 90 * k), (x + 90 * k, y + 90 * k), (x + 90 * k, y - 90 * k), (x - 90 * k, y + 90 * k), u=u, w=26 * k, seed=3,
                           col="#ff3b30")


def bubble(x, y, w, h, u, words_, tail=(-60, 70), size=60):
    if u <= .02:
        return ""
    o = PR.speech_bubble(x, y, w, h, u, seed=5, tail=tail)
    if u > .8:
        ls = words_.split("\n")
        for j, ln in enumerate(ls):
            o += plain(ln, x, y + 20 + (j - (len(ls) - 1) / 2) * size * 1.1, size, fill=INK2, anchor="middle")
    return o


def desk_set(t, mess=0.0, open_=0.0, lines=0.0, tidy=0.0):
    o = [PR.desk(700, RFL - 300, w=620, depth=100, leg_h=300, seed=7)]
    o.append(PR.laptop(720, RFL - 306, 1.0, open_=open_, screen="lines", lines=lines, t=t, seed=1))
    if mess > 0:
        for j, (dx, rot) in enumerate([(-230, -14), (-160, 20), (200, -8), (250, 12)]):
            o.append(PR.paper_ball(700 + dx, RFL - 330, .9 * mess, rot, seed=j))
        o.append(PR.mug(500, RFL - 306, .9, col="red", coffee=False, seed=2))
    return "".join(o)


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: Дима дёргает ручку запертой двери, огромный замок трясётся на «заперли», табло над дверью бежит."""
    o = [room(t)]
    pull = abs(math.sin(t * 9))
    o.append(dima_door(t, pull)["svg"])
    o.append(padlock(DOOR_X + 20, RFL - 560, 1.45, "red", bump(t, HIT, .05, .35) + .2, t))
    o.append(host(t, x=40, y=RFL, k=.85, st=dict(look=(.9, -.3), smile=1.0, perk=1.0), key_up=.6 + .4 * bump(t, HIT, .05, .3), glow=.4))
    dx, dy = shake(t, HIT, 12)
    return hook_view("".join(o), t, HIT, 390, 1060, 1.12, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«квест-комнате»: общий план — дверь с замком, табло, стол с ноутбуком, на тумбе кот-ведущий в жилетке с ключом."""
    a, b = T0("s02"), T1("s02")
    o = [room(t)]
    o.append(board(DOOR_X, RFL - 1080, .9, elapsed(t)))
    o.append(padlock(DOOR_X + 20, RFL - 560, 1.0, "red", .1, t))
    o.append(desk_set(t))
    o.append(pedestal(CATX + 40, .9))
    o.append(host(t, x=CATX + 40, y=RFL - 108, k=.85, st=dict(look=(-.9, .1), smile=1.0)))
    k = .74
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    o.append(people.dima82(560, hip, k, "wow82", "d82_shrug", t=t, feet="stand", head_add=.05 * math.sin(t * 4))["svg"])
    u = ease_io(ramp(t, a, b - a))
    return view(o and "".join(o), 560, 1020, .98 + .05 * u, 0, t=t)


def frame_s03(t):
    """Кот-ведущий: «Выйти можно» — крупно на тумбе, поднимает большой ключ, ключ блестит; пузырь «выйти можно»."""
    a, b = T0("s03"), T1("s03")
    o = [room(t)]
    o.append(pedestal(CATX - 160, 1.0))
    up = ease_out(ramp(t, W(5) - .2, .3))
    o.append(host(t, x=CATX - 160, y=RFL - 120, k=1.25, st=dict(look=(-.4, -.1), smile=1.0, perk=1.0), key_up=up, glow=up))
    o.append(PR.sparkles(CATX - 30, RFL - 700, 1.3, bump(t, W(5), .05, .5), t, seed=31, n=5, r=160))
    o.append(bubble(380, 820, 440, 200, pop(t, a - .1, .22), "Выйти\nможно", tail=(140, 80)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1100, 1.2 + .06 * u, 0, t=t)


def frame_s04(t):
    """«только начав одно дело»: крупно замок на двери с биркой «ДЕЛО», кот-ведущий стучит по нему ключом."""
    a, b = T0("s04"), T1("s04")
    o = [room(t)]
    hit = W(9)
    o.append(padlock(DOOR_X + 20, RFL - 560, 1.3, "red", bump(t, hit, .04, .3), t, tag="ДЕЛО"))
    o.append(host(t, x=DOOR_X + 420, y=RFL, k=1.15, st=dict(look=(-.9, -.6), smile=.8, paw=.6 + .4 * bump(t, hit - .12, .1, .25), paw_dx=-80)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, hit, 8)
    return view("".join(o), 420 + dx, 1080 + dy, 1.3 + .06 * u, 0, t=t)


def plaque(n, x, y, u):
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.4) if u < 1 else 1.0
    o = shape(lib.rrect(-130, -110, 130, 110, 20), "#fff6d0", text(str(n), 0, 60, 170, fill="#e2453a", stroke="#7a1a14", sw=6), w=5, seed=7500)
    return tf(o, x, y, s, -5)


def frame_s05(t):
    """«Первая отговорка»: Дима прищурился с поднятым пальцем, рядом выскакивает табличка «1»."""
    a, b = T0("s05"), T1("s05")
    o = [room(t)]
    o.append(padlock(DOOR_X + 20, RFL - 560, 1.0, "red", 0, t))
    f = stand(620, t, "sly", "d82_one")
    o.append(f["svg"])
    o.append(plaque(1, 840, 640, ramp(t, a - .2, .3)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1000, 1.12 + .06 * u, 0, t=t)


def frame_s06(t):
    """«начну, когда будет настроение»: Дима развалился в кресле-мешке, ждёт; над ним облачко с солнышком."""
    a, b = T0("s06"), T1("s06")
    o = [room(t)]
    sag = .3
    o.append(PR.bean_bag(560, RFL, 1.1, sag, seed=1))
    hx, hy = PR.bean_seat(560, RFL, 1.1, sag)
    k = .66
    f = people.dima82(hx, hy, k, "lean_rest", "d82_rest", t=t, lean_add=-.2, **people.beanbag_kw(hx, hy, k, sag))
    o.append(f["svg"])
    hdx, hdy = f["head"]
    sun = PR.sun(0, 0, 60, 1.0, t=t, seed=2)
    o.append(PR.thought_cloud(hdx + 200, hdy - 250, 1.2, w=280, h=230, u=pop(t, W(13) - .1, .25), seed=3, inner=sun))
    o.append(plaque(1, 240, 600, 1.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(15), 6)
    return view("".join(o), 600 + dx, 1080 + dy, 1.1 + .06 * u, 0, t=t)


def lock_fail(t, sid, n, push=False, expr="panic82"):
    a, b = T0(sid), T1(sid)
    hit = W({"s07": 18, "s09": 25, "s11": 31}[sid])
    o = [room(t)]
    o.append(board(DOOR_X, RFL - 1080, .9, elapsed(t)))
    blink = "red" if (t < hit or int((t - hit) * 8) % 2 == 0) else "off"
    o.append(dima_door(t, abs(math.sin(t * 10)) * (0 if push else 1), expr)["svg"])
    o.append(padlock(DOOR_X + 20, RFL - 560, 1.25, blink, 0 if sid == "s11" else bump(t, hit, .04, .3), t))
    if sid != "s11":
        o.append(red_x(DOOR_X + 20, RFL - 560, ramp(t, hit, .2), 1.4))
    return o, a, b, hit


def frame_s07(t):
    """«Замок не открылся»: лампочка замка мигает красным, красный крест, Дима дёргает дверь."""
    o, a, b, hit = lock_fail(t, "s07", 1)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, hit, 10)
    return view("".join(o), 480 + dx, 1060 + dy, 1.15 + .05 * u, 0, t=t)


def frame_s08(t):
    """«Вторая: сначала уберу стол»: Дима носится у стола, бумажки летают, кружка подпрыгивает."""
    a, b = T0("s08"), T1("s08")
    o = [room(t)]
    o.append(plaque(2, 240, 600, ramp(t, a - .2, .3)))
    o.append(desk_set(t, mess=1 - ease_io(ramp(t, W(21), 1.2))))
    for j in range(5):
        ph = (t * 1.6 + j * .2) % 1
        o.append(PR.flying_sheet(420 + 500 * ph, RFL - 360 - 400 * math.sin(math.pi * ph), .5, rot=200 * ph + 40 * j, seed=j, flap=math.sin(t * 9 + j)))
    k = .74
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    sw = math.sin(t * 14)
    f = people.dima82(360 + 20 * sw, hip, k, "rush82", "d82_rest", t=t, feet="stand", lean_add=.15,
                      arms={"f": ("ik", (520 + 40 * sw, RFL - 330), 1), "n": ("ik", (600 - 40 * sw, RFL - 340), 1)})
    o.append(f["svg"])
    o.append(PR.speed_arcs(220, hip - 200, 1.0, 1.0, t, seed=8, n=3, ang=180))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1080, 1.1 + .05 * u, 0, t=t)


def frame_s09(t):
    """«Замок не открылся»: снова красный крест, Дима устало дёргает ручку."""
    o, a, b, hit = lock_fail(t, "s09", 2, expr="sag73")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, hit, 10)
    return view("".join(o), 520 + dx, 1040 + dy, 1.08 + .05 * u, 0, t=t)


def frame_s10(t):
    """«Третья: сделаю идеально завтра»: Дима мечтательно держит отрывной листок календаря «завтра», рядом искры «идеально»."""
    a, b = T0("s10"), T1("s10")
    o = [room(t)]
    o.append(plaque(3, 240, 600, ramp(t, a - .2, .3)))
    f = stand(520, t, "bliss", "d82_one")
    o.append(f["svg"])
    hx, hy = f["head"]
    cu = ramp(t, W(29) - .25, .3)
    if cu > 0:
        s = lib.back_out(clamp(cu), 2.4) if cu < 1 else 1.0
        cal = shape(lib.rect_pts(-170, -150, 170, 150), "#fffdf4", blob(lib.rect_pts(-170, -150, 170, -80), "#c8553d")
                    + text("завтра", 0, 60, 76, fill=INK2, stroke="#fffdf4", sw=.01), w=5, seed=7600)
        for j in range(5):
            cal += f'<circle cx="{-120 + 60 * j}" cy="-150" r="9" fill="#2a2230"/>'
        o.append(tf(cal, 870, 820, s, 6))
    o.append(PR.sparkles(hx, hy - 120, 1.4, ramp(t, W(28) - .1, .3), t, seed=101, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(29), 6)
    return view("".join(o), 600 + dx, 1020 + dy, 1.08 + .05 * u, 0, t=t)


def frame_s11(t):
    """«Замок даже не дрогнул»: Дима толкает дверь плечом изо всех сил, замок неподвижен; кот-ведущий на тумбе зевает."""
    a, b = T0("s11"), T1("s11")
    o = [room(t)]
    o.append(board(DOOR_X, RFL - 1080, .9, elapsed(t)))
    k = .78
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    o.append(people.dima82(DOOR_X + 300, hip, k, "strain", "d82_rest", t=t, feet="stand", flip=True, lean_add=-.35,
                           arms={"f": ("ik", (DOOR_X + 200, RFL - 600), 1), "n": ("ik", (DOOR_X + 210, RFL - 540), 1)})["svg"])
    o.append(PR.sweat(DOOR_X + 420, hip - 640, 1.1))
    o.append(padlock(DOOR_X + 20, RFL - 560, 1.25, "red", 0, t))
    o.append(pedestal(CATX + 60, .9))
    yawn = bump(t, W(31), .15, .5)
    o.append(host(t, x=CATX + 60, y=RFL - 108, k=.85, st=dict(look=(-.9, 0), blink=.6 * yawn, tongue=.0, smile=0.0, tilt=6 * yawn)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 520, 1060, 1.06 + .05 * u, 0, t=t)


def frame_s12(t):
    """Кот: «Подсказка» — достаёт из кармана жилетки конверт, над ним загорается лампочка."""
    a, b = T0("s12"), T1("s12")
    o = [room(t)]
    o.append(pedestal(560, 1.0))
    pu = ease_out(ramp(t, a + .05, .35))
    o.append(host(t, x=560, y=RFL - 120, k=1.3, st=dict(look=(.1, -.6), smile=1.0, perk=1.0, paw_l=.7 * pu, paw_l_dx=60)))
    env = shape(lib.rect_pts(-110, -75, 110, 75), "#fff6d0", line([(-110, -75), (0, 10), (110, -75)], 4, seed=7710)
                + text("?", 0, 60, 90, fill="#e2453a", stroke="#fff6d0", sw=.01), w=4.4, seed=7711)
    o.append(tf(env, 470 - 40 * pu, RFL - 640 - 120 * pu, .9 + .3 * pu, -10))
    o.append(PR.idea_bulb(560, RFL - 1060, 1.4, on=ramp(t, W(34) + .1, .3), t=t, seed=4))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1080, 1.15 + .06 * u, 0, t=t)


def frame_s13(t):
    """«открой дело на две минуты»: кот-ведущий показывает ключом на ноутбук, карточка «2 минуты», табло переключается на 2:00."""
    a, b = T0("s13"), T1("s13")
    o = [room(t)]
    o.append(board(DOOR_X, RFL - 1080, .9, "2:00", col="#3fd26a"))
    o.append(desk_set(t, open_=ease_out(ramp(t, W(35), .4))))
    o.append(host(t, x=320, y=RFL, k=1.05, st=dict(look=(.9, -.2), smile=1.0, paw=.8, paw_dx=90)))
    cu = ramp(t, W(38) - .25, .3)
    if cu > 0:
        s = lib.back_out(clamp(cu), 2.4) if cu < 1 else 1.0
        card = shape(lib.rrect(-190, -110, 190, 110, 18), "#fff6d0", text("2 минуты", 0, 26, 74, fill=INK2, stroke="#fff6d0", sw=.01), w=5, seed=7700)
        o.append(tf(card, 720, 820, s, -4))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(38), 6)
    return view("".join(o), 560 + dx, 1060 + dy, 1.06 + .05 * u, 0, t=t)


def frame_s14(t):
    """«Я открыл файл, написал строку»: Дима за ноутбуком, на экране строка растёт, табло 2:00 тикает вниз, кот рядом на столе."""
    a, b = T0("s14"), T1("s14")
    o = [room(t)]
    o.append(board(DOOR_X, RFL - 1080, .9, "2:00", col="#3fd26a"))
    o.append(PR.desk(700, RFL - 300, w=620, depth=100, leg_h=300, seed=7))
    o.append(PR.laptop(740, RFL - 306, 1.1, screen="lines", lines=.15 + .5 * ramp(t, W(43), .6), t=t, seed=1))
    o.append(chair(430, RFL - 240, 1.0))
    k = .62
    hip = RFL - 300
    tap = math.sin(t * 30) * (t > W(43))
    f = people.dima82(430, hip, k, dict(people.EXPR["dima"]["calm82"], look=(.9, .1)), "sit_desk", t=t, feet=people.sit_kw(430, hip, k)["feet"],
                      arms={"f": ("ik", (680 + 10 * tap, RFL - 330), 1), "n": ("ik", (760 - 10 * tap, RFL - 320), 1)})
    o.append(f["svg"])
    o.append(host(t, x=960, y=RFL - 300, k=.6, st=dict(look=(-.9, .3), smile=1.0)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 640, 1080, 1.15 + .05 * u, 0, t=t)


def frame_s15(t):
    """«и дверь щёлкнула»: замок зеленеет, дужка выскакивает, дверь распахивается, из проёма свет; ключ кота светится."""
    a, b = T0("s15"), T1("s15")
    hit = W(47)
    op = ease_out(ramp(t, hit + .2, .5))
    o = [room(t, open_=op, glow_=ramp(t, hit, .3))]
    o.append(board(DOOR_X, RFL - 1080, .9, "2:00", col="#3fd26a"))
    o.append(padlock(DOOR_X + 20 - 140 * op, RFL - 560 + 300 * op, 1.25, "green" if t > hit - .05 else "red", bump(t, hit, .04, .3), t, open_=ramp(t, hit, .15)))
    f = stand(DOOR_X + 400, t, "proud82" if t > hit else "wow82", "d82_one", flip=True)
    o.append(f["svg"])
    o.append(host(t, x=CATX + 30, y=RFL, k=1.0, st=dict(look=(-.9, -.3), smile=1.0, perk=1.0), key_up=ramp(t, hit - .1, .3), glow=ramp(t, hit, .3)))
    o.append(PR.sparkles(DOOR_X + 20, RFL - 600, 2.0, bump(t, hit, .05, .6), t, seed=151, n=7, r=300))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, hit, 12)
    return view("".join(o), 520 + dx, 1060 + dy, 1.06 + .05 * u, 0, t=t)


def frame_s16(t):
    return cta_code(t, T0("s16"), T1("s16"))


def frame_s17(t):
    """«найти ключ от своего дела»: кот-ведущий крупно протягивает зрителю светящийся золотой ключ."""
    a, b = T0("s17"), T1("s17")
    o = [room(t, open_=1.0, glow_=.6)]
    o.append(pedestal(560, 1.0))
    o.append(host(t, x=560, y=RFL - 120, k=1.35, st=dict(look=(0, 0), smile=1.0, perk=1.0), key_up=1.0, glow=1.0))
    o.append(PR.sparkles(640, RFL - 760, 1.6, .6 + .4 * math.sin(t * 5) ** 2, t, seed=171, n=6, r=220))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 580, 1080, 1.2 + .08 * u, 0, t=t)


def frame_s18(t):
    """Петля: кадр хука — дверь с замком, Дима дёргает ручку."""
    a, b = T0("s18"), T1("s18")
    o = [room(t)]
    o.append(dima_door(t, abs(math.sin(t * 9)))["svg"])
    o.append(padlock(DOOR_X + 20, RFL - 560, 1.45, "red", .2, t))
    o.append(host(t, x=40, y=RFL, k=.85, st=dict(look=(.9, -.3), smile=1.0, perk=1.0), key_up=.6, glow=.4))
    return loop_view("".join(o), t, a, b, HIT, 390, 1060, 1.12)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
