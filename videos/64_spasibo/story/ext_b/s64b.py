"""Рилс 64 «спасибо», группа B: s07 (Дима крупно на бумаге: пузырь речи сдувается, огонёк в груди остаётся внутри),
s08 (кабинет психолога: поворачивается от полки, поправляет очки, протягивает чистый лист и ручку),
s13 (комната днём: Дима пишет письмо, складывает, подносит мобильник к уху; кот на краю стола).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Люди и кот — ../common/people.py, cat.py; предметы — props.py (группа A),
комната — room.py (группа C). Букв, цифр и имён на экране нет."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
from lib import (INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth)  # noqa: E402,F401

import props as PR  # noqa: E402
import room as R  # noqa: E402

E = people.EXPR


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def decay(t, t0, k=9.0, fr=22.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def mix_expr(a, b, u):
    """Мимика a → b: числа плавно, слова (рот, брови) — на середине."""
    u = clamp(u)
    out = dict(a if u < .5 else b)
    for k in set(a) | set(b):
        va, vb = a.get(k), b.get(k)
        if isinstance(va, (int, float)) or isinstance(vb, (int, float)):
            out[k] = lerp(float(va or 0.0), float(vb or 0.0), u)
        elif isinstance(va, tuple) and isinstance(vb, tuple):
            out[k] = lerp2(va, vb, u)
    return out


def paper_bg(warm=0.0, seed=0):
    """Кремовая бумага с волокнами и мягким тёплым пятном (без огромных овалов — пятно не ярче бумаги)."""
    o = ['<rect x="-600" y="-600" width="2280" height="3120" fill="#f4efe4"/>']
    rs = np.random.RandomState(640 + seed)
    for i in range(46):
        x, y = rs.uniform(-200, 1280), rs.uniform(-200, 2120)
        a = rs.uniform(0, math.pi)
        L = rs.uniform(20, 60)
        o.append(line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], 1.4, "#e2d8c4", seed=6400 + i, taper=.6, wmin=.3, op=.8))
    return "".join(o)


# ═════════════════════════════ s07: Дима крупно, пузырь речи, огонёк в груди ═════════════════════════════
T7_GOV, T7_VSLUH, T7_RAD, T7_OST, T7_VNU = 15.96, 16.613, 17.58, 17.96, 18.389


def s07(t):
    lib.dyn_begin()
    s = 1.12
    hx, hy = 470.0, 1760.0
    breath = math.sin(t * 2 * math.pi / 3.2)
    lean = .03 + .012 * breath - .03 * bump(t, T7_VSLUH + .2, .6)
    # мимика
    if t < T7_GOV:
        ex = dict(E["dima"]["unsure"], look=(-.25, .05))
    elif t < T7_VSLUH:
        o_ = .45 + .15 * math.sin((t - T7_GOV) * 22)
        ex = dict(brows="up", mouth="talk", open=o_ * smooth(T7_GOV, T7_GOV + .08, t), smile=.1, lid=.85, look=(.5, -.3))
    elif t < T7_RAD:
        ex = dict(E["dima"]["pressed"], look=lerp2((.55, -.2), (.25, .7), smooth(T7_VSLUH + .5, T7_RAD, t)))
        ex["brows"] = "worry"
    else:
        u = smooth(T7_RAD, T7_RAD + .35, t)
        ex = mix_expr(dict(E["dima"]["pressed"], look=(.25, .7)), dict(brows="calm", mouth="smile", smile=.35, lid=.55, look=(.15, .85)), u)
    ex["closed"] = blink_of(t, [15.82, 17.25, 18.62], .15)
    # рука на груди: поднимается к груди на «внутри»
    hu = ease_io(smooth(T7_OST - .1, T7_VNU + .1, t))
    sc = s * people.HEIGHT["dima"]
    a_rest = people.ik_ang("dima", hx, hy, s, lean, (hx + 150 * sc, hy - 110 * sc), -1)
    a_chest = people.ik_ang("dima", hx, hy, s, lean, (hx + 55 * sc, hy - 255 * sc), -1)
    arm_n = people.mix_ang(a_rest, a_chest, hu)
    hand_n = {"dir": (-.25 * hu + .2 * (1 - hu), -1 * hu + 1 * (1 - hu)), "curl": (.1 + .3 * (1 - hu), .1 + .3 * (1 - hu), .15 + .3 * (1 - hu), .2 + .3 * (1 - hu)),
              "spread": .12, "thumb": .15 + .2 * (1 - hu)}
    ha = .05 * breath * .3 + .08 * smooth(T7_VSLUH + .3, T7_RAD, t) + .05 * bump(t, T7_GOV, .3)
    fig = people.figure("dima", hx, hy, s, ex, lean=lean, head_ang=ha, arms={"f": ("ik", (hx + 40 * sc, hy - 120 * sc), -1), "n": arm_n},
                        hands={"n": hand_n}, layers=("pelvis", "arm_f", "body"))
    near = people.figure("dima", hx, hy, s, ex, lean=lean, head_ang=ha, arms={"f": ("ik", (hx + 40 * sc, hy - 120 * sc), -1), "n": arm_n},
                         hands={"n": hand_n}, layers=("arm_n",))
    head = fig["head"]
    mouth = (head[0] + 64 * sc, head[1] + 92 * sc)
    # пузырь речи: растёт на «говорим», сдувается и втягивается в рот на «вслух»
    bub = ""
    if T7_GOV - .02 < t < T7_VSLUH + .42:
        grow = max(0.0, lib.back_out(clamp((t - T7_GOV - .02) / .34)))
        shrink = ease_in(clamp((t - T7_VSLUH) / .38), 2)
        u = grow * (1 - shrink)
        c0 = (mouth[0] + 260, mouth[1] - 300)
        c = lerp2(c0, (mouth[0] + 30, mouth[1] + 10), shrink)
        wob = 1 + .06 * math.sin((t - T7_VSLUH) * 40) * shrink * (1 - shrink) * 4
        if u > .02:
            bub = (f'<g transform="translate({c[0]:.1f} {c[1]:.1f}) scale({wob:.4f} {2 - wob:.4f}) translate({-c[0]:.1f} {-c[1]:.1f})">'
                   + PR.speech_bubble(c[0], c[1], 330, 230, u, seed=7, tail=(-150, 90)) + "</g>")
        # штрихи «сдувания» у краёв
        if 0 < shrink < .9:
            for i in range(4):
                a = -2.2 + i * .55
                r0 = 150 * u + 30
                p0 = (c[0] + math.cos(a) * r0, c[1] + math.sin(a) * r0 * .7)
                p1 = (c[0] + math.cos(a) * (r0 + 40), c[1] + math.sin(a) * (r0 + 40) * .7)
                bub += line([p0, p1], 5, INK, seed=7100 + i, taper=.6, wmin=.2, op=.8 * (1 - shrink))
    # огонёк в груди: под худи, свет только вокруг; бьётся на «остаётся внутри»
    glow = ""
    gu = ease_out(clamp((t - T7_RAD) / .3), 2)
    if gu > .01:
        chest = (hx + (95 - 330 * math.sin(lean)) * sc, hy - 240 * sc)
        beat = max(bump(t, T7_OST, .22), bump(t, T7_OST + .22, .22), bump(t, T7_VNU, .22), bump(t, T7_VNU + .24, .22))
        glow = PR.chest_glow(chest[0], chest[1], 1.25, t, gu, beat, seed=3)
        # огонёк тянется наружу и возвращается: мелкие искры поднимаются и гаснут у самой груди
        for i, t0 in enumerate((17.98, 18.2, 18.42, 18.64)):
            v = (t - t0) / .4
            if 0 < v < 1:
                rise = 60 * math.sin(math.pi * v)
                glow += PR.mote(chest[0] + (i - 1.5) * 14, chest[1] - 70 - rise, 5 + 2 * (1 - v), (1 - v) * .9)
    world = [paper_bg(), fig["svg"], near["svg"], glow, bub]
    # камера: наезд на лицо, затем вниз к огоньку
    z = lerp(1.45, 1.62, ease_io(smooth(15.76, 17.3, t))) - .12 * ease_io(smooth(17.4, 18.3, t))
    cx = lerp(head[0] + 20, hx + 60 * sc, ease_io(smooth(17.4, 18.4, t)))
    cy = lerp(head[1] + 10, hy - 330 * sc, ease_io(smooth(17.4, 18.4, t)))
    cy -= 40 * bump(t, T7_GOV, .5)
    rot = .6 * math.sin(t * 1.1) - 1.0 * bump(t, T7_VSLUH, .4)
    set_ink(1.0)
    return lib.svg(f'<rect width="1080" height="1920" fill="#f4efe4"/><g transform="{lib.cam(cx, cy + 120, z, rot)}">{"".join(world)}</g>')


# ═════════════════════════════ s08: кабинет психолога ═════════════════════════════
T8_PSI, T8_SEL, T8_PROS = 19.40, 20.80, 21.344
FL8 = 1720.0


def armchair(x, y, k=1.0):
    """Кожаное кресло (вид 3/4): спинка, подлокотник, сиденье, ножки. (x, y) — центр низа."""
    c, sh, hi = "#9a4f3a", "#743726", "#b8684e"
    o = [shape([(x - 200 * k, y - 120 * k, 1), (x - 180 * k, y - 520 * k), (x - 60 * k, y - 560 * k), (x + 120 * k, y - 540 * k), (x + 170 * k, y - 470 * k),
                (x + 160 * k, y - 120 * k, 1)], c, blob([(x + 60 * k, y - 560 * k), (x + 180 * k, y - 500 * k), (x + 170 * k, y - 120 * k), (x + 90 * k, y - 120 * k)], sh, .8)
               + line([(x - 120 * k, y - 470 * k), (x + 90 * k, y - 470 * k)], 2.4, sh, seed=8011, op=.7), w=4.4, seed=8010)]
    o.append(shape(lib.rrect(x - 230 * k, y - 230 * k, x + 200 * k, y - 110 * k, 30 * k), hi, blob(lib.rrect(x - 230 * k, y - 160 * k, x + 200 * k, y - 110 * k, 20 * k), c),
                   w=4.2, seed=8012))
    o.append(shape(lib.rrect(x - 260 * k, y - 330 * k, x - 150 * k, y - 80 * k, 40 * k), c, blob(lib.rrect(x - 200 * k, y - 330 * k, x - 150 * k, y - 80 * k, 30 * k), sh),
                   w=4.2, seed=8013))
    o.append(shape(lib.rrect(x + 130 * k, y - 330 * k, x + 230 * k, y - 80 * k, 40 * k), c, blob(lib.rrect(x + 180 * k, y - 330 * k, x + 230 * k, y - 80 * k, 30 * k), sh),
                   w=4.2, seed=8014))
    for i, lx in enumerate((x - 220 * k, x + 200 * k)):
        o.append(shape(lib.rect_pts(lx - 10 * k, y - 80 * k, lx + 10 * k, y), "#4a3020", "", w=3.0, seed=8015 + i))
    return "".join(o)


def office(t):
    o = ['<rect x="-600" y="-600" width="2400" height="3200" fill="#dfe3d2"/>']
    o.append(f'<rect x="-600" y="{FL8 - 560}" width="2400" height="560" fill="#cfd5c0"/>')
    o.append(line([(-600, FL8 - 560), (1800, FL8 - 560)], 4, "#9aa38a", seed=8001, taper=.05, wmin=.6))
    # окно слева: день, полоса света формы окна на полу
    o.append(PR.window(-30, 260, 420, 620, mode="day", t=t, seed=4))
    o.append(f'<path d="M-120 {FL8} L340 {FL8} L520 {FL8 + 240} L-40 {FL8 + 240} Z" fill="#fff3cf" opacity=".0"/>')
    # пол
    o.append(f'<rect x="-600" y="{FL8}" width="2400" height="900" fill="#a9825a"/>')
    for i in range(10):
        yy = FL8 + 20 + i * 44
        o.append(line([(-600, yy), (1800, yy)], 2.2, "#8a6644", seed=8020 + i, taper=.1, wmin=.4))
    o.append(blob([(-60, FL8 + 10), (400, FL8 + 10), (560, FL8 + 230), (60, FL8 + 230)], "#d9b886", .55))     # солнечная полоса от окна
    o.append(shape([(-600, FL8 - 22), (1800, FL8 - 22), (1800, FL8 + 4), (-600, FL8 + 4)], "#eef0e4", "", w=3.2, seed=8030))
    # полки справа (корешки пустые), кресло слева у окна
    o.append(PR.bookshelf(900, FL8 - 10, 560, 1180, shelves=5, seed=3))
    o.append(armchair(80, FL8 + 30, 1.0))
    # растение на полке-тумбе у окна
    o.append(shape(lib.rrect(300, FL8 - 300, 400, FL8 - 180, 10), "#c86f4a", "", w=3.4, seed=8040))
    for i, (a, L) in enumerate(((-2.0, 150), (-1.6, 190), (-1.2, 160), (-2.4, 120), (-.9, 120))):
        sw = 4 * math.sin(t * 1.3 + i)
        tip = (350 + math.cos(a) * L + sw, FL8 - 300 + math.sin(a) * L)
        o.append(shape([(350, FL8 - 300), (350 + math.cos(a) * L * .5 - 16, FL8 - 300 + math.sin(a) * L * .5), tip, (350 + math.cos(a) * L * .5 + 16,
                                                                                                                     FL8 - 300 + math.sin(a) * L * .5)],
                       "#5f9a52", line([(350, FL8 - 300), tip], 1.8, "#3f6f3a", seed=8050 + i, op=.8), w=3.0, seed=8045 + i))
    return "".join(o)


def s08(t):
    lib.dyn_begin()
    s = .92
    hx, hy = 560.0, FL8 - (people.LEG_LEN - 12) * s * people.HEIGHT["psych"]
    sc = s * people.HEIGHT["psych"]
    turn = ease_io(smooth(T8_PSI - .1, T8_PSI + .45, t))
    gl = smooth(T8_SEL, T8_SEL + .2, t) * (1 - smooth(T8_SEL + .55, T8_PROS - .02, t))
    off = ease_out(smooth(T8_PROS, T8_PROS + .38, t), 2)
    lean = lerp(.16, -.02, turn) + .14 * off
    ha = lerp(.2, -.06, turn) + .08 * off
    # ближняя рука: книга на полке → вниз → очки → протягивает лист
    tgt_book = (hx + 470 * sc, hy - 560 * sc)
    tgt_rest = (hx + 160 * sc, hy + 30 * sc)
    tgt_gl = (hx + 112 * sc, hy - 450 * sc)
    tgt_off = (hx + 470 * sc, hy - 330 * sc)
    a_book = people.ik_ang("psych", hx, hy, s, lean, tgt_book, -1)
    a_rest = people.ik_ang("psych", hx, hy, s, lean, tgt_rest, -1)
    a_gl = people.ik_ang("psych", hx, hy, s, lean, tgt_gl, -1)
    a_off = people.ik_ang("psych", hx, hy, s, lean, tgt_off, -1)
    if t < T8_SEL:
        arm = people.mix_ang(a_book, a_rest, turn)
        hand = {"dir": (1, -.4), "curl": (.4, .45, .5, .55), "thumb": .4} if turn < .5 else {"curl": (.3, .3, .35, .4), "thumb": .3}
    elif t < T8_PROS:
        arm = people.mix_ang(a_rest, a_gl, gl)
        hand = {"dir": (.3, -1), "curl": (0, .85, .9, .9), "spread": .05, "thumb": .7} if gl > .4 else {"curl": (.3, .3, .35, .4), "thumb": .3}
    else:
        back = smooth(T8_PROS, T8_PROS + .14, t)
        arm = people.mix_ang(people.mix_ang(a_gl, a_rest, back), a_off, off)
        hand = {"dir": (1, -.15), "curl": (.5, .5, .55, .6), "thumb": .55}
    # мимика: смотрит на книги → на зрителя → улыбка → объясняет
    if t < T8_PSI:
        ex = dict(E["psych"]["calm"], look=(.9, -.3), lid=.7)
    elif t < T8_SEL:
        ex = dict(E["psych"]["calm"], look=lerp2((.9, -.3), (-.35, 0), turn))
        ex["brows"] = "up" if turn > .5 else "calm"
    elif t < T8_PROS:
        ex = dict(E["psych"]["smile"])
    else:
        ex = dict(E["psych"]["explain"], open=.25 + .2 * math.sin((t - T8_PROS) * 20))
    ex["closed"] = blink_of(t, [19.12, 20.36, 21.95], .15)
    feet = people.stand_kw(hx, hy, s, "psych")["feet"]
    arms = {"f": ("ang", 0.2 + .03 * math.sin(t * 1.4), 0.25), "n": arm}
    body = people.figure("psych", hx, hy, s, ex, lean=lean, head_ang=ha, arms=arms, hands={"n": hand}, feet=feet,
                         layers=("legs", "pelvis", "arm_f", "body"))
    near = people.figure("psych", hx, hy, s, ex, lean=lean, head_ang=ha, arms=arms, hands={"n": hand}, feet=feet, layers=("arm_n",))
    W = body["wrist"]["n"]
    sheet = ""
    if t >= T8_PROS - .05:
        # чистый лист и ручка в пальцах: лист под пальцами, ручка поверх листа (большой палец держит обе вещи)
        vis = smooth(T8_PROS - .05, T8_PROS + .05, t)
        if vis > .01:
            pc = (W[0] + 80 * sc, W[1] - 10 * sc)
            sheet = PR.paper(pc[0] + 40 * sc, pc[1] - 50 * sc, k=1.4 * sc, rot=-8 + 6 * (1 - off), w=150, h=200, kind="blank", seed=5)
            sheet += PR.pen(pc[0] + 30 * sc, pc[1] - 30 * sc, k=.9 * sc, rot=-118, seed=2)
    book = ""
    if t < T8_PSI + .3:     # книга, которую он задвигает на полку
        pass
    world = [office(t), body["svg"], sheet, near["svg"], book]
    # камера: наезд на психолога, на «просил» уходит за его рукой
    head = body["head"]
    z = lerp(1.0, 1.22, ease_io(smooth(18.65, 20.6, t))) + .05 * bump(t, T8_SEL, .5)
    cx = lerp(hx + 120, head[0] + 40, ease_io(smooth(18.65, 20.4, t)))
    cy = lerp(1060, head[1] + 260, ease_io(smooth(18.65, 20.4, t)))
    fo = ease_io(smooth(T8_PROS, T8_PROS + .55, t))
    cx = lerp(cx, W[0] + 30, fo * .55)
    cy = lerp(cy, W[1] - 120, fo * .3)
    rot = .5 * math.sin(t * .9) + 1.2 * fo
    set_ink(z)
    return lib.svg(f'<rect width="1080" height="1920" fill="#dfe3d2"/><g transform="{lib.cam(cx, cy, z, rot)}">{"".join(world)}</g>')


# ═════════════════════════════ s13: комната днём, Дима пишет письмо, мобильник к уху ═════════════════════════════
T13_NAP, T13_PIS, T13_I, T13_PRO, T13_END = 31.973, 32.384, 32.96, 33.184, 33.92
LETTER = (720.0, 905.0)
MOB = (905.0, 918.0)


def s13(t):
    lib.dyn_begin()
    bs = 1.0
    sx, sy = R.SIT
    sc = bs * people.HEIGHT["dima"]
    sc_ = R.desk_scene(t, "day", sit=(sx, sy), bs=bs)
    breath = math.sin(t * 2 * math.pi / 3.0)
    # фазы
    wr = clamp((t - 31.55) / (T13_PIS - .05 - 31.55))                 # строки пишутся
    fold = ease_io(smooth(T13_PIS, T13_PIS + .4, t))                    # складывает пополам
    reach = ease_io(smooth(T13_PIS + .45, T13_PRO - .02, t))            # тянется к мобильнику
    lift = ease_io(smooth(T13_PRO, T13_PRO + .5, t))                    # к уху
    lean = .2 - .1 * fold - .12 * lift + .01 * breath + .06 * reach * (1 - lift)
    ha = .2 - .12 * fold - .22 * lift
    # письмо: на столе, пишется; складывается; сдвигается к краю
    lx = LETTER[0] - 40 * smooth(T13_PIS + .4, T13_PIS + .7, t)
    ly = LETTER[1]
    tip = PR.letter_tip(lx, ly, 1.0, 0, 200, 260, wr) if wr < 1 else None
    # ближняя рука — ручка у кончика строки; потом обе руки складывают; потом ближняя к мобильнику и к уху
    jig = (6 * math.sin(t * 38), 3 * math.sin(t * 29))
    if t < T13_PIS:
        tp = tip or PR.letter_tip(lx, ly, 1.0, 0, 200, 260, .999)
        pen_tip = (tp[0] + jig[0] * (wr < 1), ly + (tp[1] - ly) * .45 + jig[1] * (wr < 1))
        tgt_n = (pen_tip[0] - 40, pen_tip[1] - 30)
        hand_n = {"dir": (.6, .8), "curl": (.55, .6, .7, .75), "thumb": .65, "spread": .05}
    else:
        tgt_n = (lx + 70, ly - 20)
        hand_n = {"dir": (-.2, 1), "curl": (.5, .5, .55, .6), "thumb": .5}
    a_desk = people.ik_ang("dima", sx, sy, bs, lean, tgt_n, -1)
    a_mob = people.ik_ang("dima", sx, sy, bs, lean, (MOB[0] - 50, MOB[1] - 30), -1)
    a_ear = people.ik_ang("dima", sx, sy, bs, lean, (sx - 75 * sc, sy - 430 * sc), 1)
    arm_n = people.mix_ang(people.mix_ang(a_desk, a_mob, reach), a_ear, lift)
    if reach > .5:
        hand_n = {"dir": (.15 * lift + 1 * (1 - lift), -1 * lift + .5 * (1 - lift)), "curl": (.6, .65, .7, .7), "thumb": .7}
    # дальняя рука держит лист (на складывании — поднимает нижний край)
    tgt_f = (lx - 60 + 30 * fold * (1 - reach), ly + 10 - 40 * bump(t, T13_PIS + .15, .4))
    arms = {"f": ("ik", tgt_f, -1), "n": arm_n}
    hands = {"f": {"curl": (.45, .5, .55, .6), "thumb": .5, "dir": (.8, .5)}, "n": hand_n}
    # мимика
    if t < T13_PIS:
        ex = dict(E["dima"]["write"])
    elif t < T13_PRO:
        ex = mix_expr(dict(E["dima"]["warm"], look=(.5, .6)), dict(E["dima"]["unsure"], bags=False, look=(.6, .5)), smooth(T13_PIS + .45, T13_PRO, t))
    else:
        ex = dict(E["dima"]["breath"], open=.15 + .25 * bump(t, T13_PRO + .3, .6))
    ex["closed"] = blink_of(t, [31.6, 32.85], .14)
    feet = {"n": ((sx + 300 * bs, R.FL - 52), 0.0), "f": ((sx + 250 * bs, R.FL - 50), 0.0)}
    kw = dict(lean=lean, head_ang=ha, arms=arms, hands=hands, feet=feet)
    legs = people.figure("dima", sx, sy, bs, ex, layers=("legs",), **kw)
    body = people.figure("dima", sx, sy, bs, ex, layers=("pelvis", "arm_f", "body"), **kw)
    near = people.figure("dima", sx, sy, bs, ex, layers=("arm_n",), **kw)
    W = body["wrist"]["n"]
    # предметы на столе
    items = [PR.letter(lx, ly, 1.0, -4 + 4 * fold, 200, 260, write=wr, fold=fold, seed=3, sy=.42 + .25 * fold)]
    pen_svg = ""
    if t < T13_PIS + .05:
        pt = (W[0] + 34, W[1] + 30)
        pen_svg = PR.pen(pt[0] - 40, pt[1] - 64, k=.62, rot=-35, cap=1.0, seed=1)
    elif t < T13_PIS + .45:     # ручку кладёт на стол
        pen_svg = PR.pen(lx + 150, ly + 24, k=.62, rot=-80, cap=1.0, seed=1)
    else:
        pen_svg = PR.pen(lx + 150, ly + 24, k=.62, rot=-80, cap=1.0, seed=1)
    mob = ""
    if reach < .97:
        mob = PR.mobilnik(MOB[0], MOB[1], .7, rot=78)
    mob_held = ""
    if reach >= .97:
        if lift < .5:
            mob_held = PR.mobilnik(W[0] + 40 * (1 - lift), W[1] - 10 - 60 * lift, .7, rot=78 * (1 - lift * 2) - 12 * lift * 2)
        else:
            mob_held = people.mobile_at_ear(body, bs)
    # кот на краю стола смотрит на Диму, моргает, водит ухом
    cat_x, cat_y = R.DESK_X[1] - 110, R.DESK_TOP - 30
    cst = {"look": (-.7, -.2 + .3 * fold), "turn": -.35, "blink": blink_of(t, [32.2, 33.4], .16), "ear": 10 * bump(t, T13_PRO + .1, .3),
           "tail": 8 * math.sin(t * 2.1), "tilt": -6 * bump(t, T13_PIS, .8)}
    cat = people.cat_svg(cat_x, cat_y, .55, cst, t)
    world = [sc_["bg"], sc_["chair_back"], legs["svg"], sc_["chair_seat"], body["svg"], sc_["desk"], sc_["pool"], items[0], mob, cat,
             pen_svg if t >= T13_PIS + .05 else "", near["svg"], pen_svg if t < T13_PIS + .05 else "", mob_held if lift < .5 else "", sc_["lamp"]]
    if lift >= .5:      # мобильник у уха — между головой и ближней рукой
        world = [sc_["bg"], sc_["chair_back"], legs["svg"], sc_["chair_seat"], body["svg"], sc_["desk"], sc_["pool"], items[0], cat, pen_svg,
                 mob_held, near["svg"], sc_["lamp"]]
    # камера: дрейф вправо, наезд на руки, потом на лицо
    head = body["head"]
    hand_c = (LETTER[0] - 20, LETTER[1] - 60)
    u_face = ease_io(smooth(T13_PIS + .5, T13_PRO + .5, t))
    cx = lerp(lerp(560, hand_c[0] - 60, ease_io(smooth(31.48, 32.2, t))), head[0] + 120, u_face)
    cy = lerp(lerp(900, hand_c[1] - 20, ease_io(smooth(31.48, 32.2, t))), head[1] + 230, u_face)
    z = lerp(lerp(1.12, 1.3, ease_io(smooth(31.48, 32.2, t))), 1.38, u_face)
    cx += 30 * (t - 31.48)
    set_ink(z)
    return lib.svg(f'<rect width="1080" height="1920" fill="#e6dcc0"/><g transform="{lib.cam(cx, cy, z, .4 * math.sin(t * .8))}">{"".join(world)}</g>')


SCENES = {"s07": s07, "s08": s08, "s13": s13}


def frame(sid, t):
    return SCENES[sid](t)
