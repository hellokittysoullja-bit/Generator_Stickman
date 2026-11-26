"""Рилс 112 «Реферат», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Места: спальня с кроватью и столиком
(реферат со штампом «СДАН»), стол с ноутбуком, листки абзацев, календарь со сроком. Призыв — 2D-ноутбук
(scripts/story_cta_laptop.py), без подмигивания аватара. NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people, REPO, COMMON  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "scripts"))
import story_cta_laptop as LP  # noqa: E402

HIT = stress(1, .3)
BED = (560.0, RFL, 1.25)
MAT = RFL - 118 * 1.25
BHIP = (BED[0] + 60, MAT + 10)
NST = (40.0, RFL)                    # столик у кровати справа
REF = (40.0, RFL - 300)              # реферат на столике


def stamp(x, y, k, u, word="СДАН", rot=-14.0):
    """Красный штамп: u — шлепок (масштаб с перелётом)."""
    if u <= 0:
        return ""
    s = 1.0 + 1.4 * (1 - ease_out(clamp(u / .6))) if u < .6 else 1.0
    op = clamp(u / .15)
    body = (f'<rect x="-150" y="-62" width="300" height="124" rx="14" fill="none" stroke="#d8352a" stroke-width="12"/>'
            + text(word, 0, 34, 92, fill="#d8352a", stroke="#d8352a", sw=.01))
    return f'<g opacity="{op * .92:.3f}" transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({k * s:.4f})">{body}</g>'


def referat(x, y, k, st=0.0, rot=-4.0):
    """Реферат: лист с заголовком и строками, сверху штамп «СДАН» (st — время шлепка, <0 — без)."""
    inner = plain("РЕФЕРАТ", 0, -120, 46, fill="#1d2448", anchor="middle")
    for j in range(7):
        inner += line([(-110, -60 + 30 * j), (110 - 40 * (j % 3), -60 + 30 * j)], 4, "#7d8597", taper=.2, wmin=.5, seed=820 + j)
    o = blob(lib.rect_pts(-150 + 10, -190 + 12, 150 + 10, 190 + 12), "#000000", .14)
    o += shape(lib.rect_pts(-150, -190, 150, 190), "#fbf8f1", inner, w=4, seed=810)
    o += stamp(20, 60, .9, st)
    return tf(o, x, y, k, rot)


def bedroom(t, night=False, sun=0.0):
    o = [plain_room(t, wall="#c9c2d8" if night else WALL, floor="#a99a8a" if night else FLOOR_C)]
    o.append(PR.window(620, 950, 360, 440, mode="night" if night else ("day" if sun > .5 else "evening"), t=t, seed=3, curtain=False))
    o.append(PR.bed(*BED, seed=1))
    o.append(shape(lib.rrect(NST[0] - 130, NST[1] - 300, NST[0] + 130, NST[1], 10), "#a8774a",
                   blob(lib.rect_pts(NST[0] - 130, NST[1] - 160, NST[0] + 130, NST[1] - 150), "#8a6038"), w=4, seed=620))
    o.append(rug(560, RFL + 150, 560))
    if sun > 0:
        o.append(PR.glow(620, 800, 700, .45 * sun, "#fff1b0"))
    return o


def sleeper(t, expr=None):
    expr = expr or dict(people.EXPR["dima"]["bliss"], shut=1.0)
    return people.dima_bed(BHIP[0], BHIP[1], .62, expr=expr, t=t, cover="chest", col="blue")


def frame_s01(t):
    """ХУК: Дима спокойно спит, на столике реферат, штамп «СДАН» шлёпается на «наконец-то»."""
    o = bedroom(t)
    f = sleeper(t)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.zzz(hx + 90, hy - 140, 1.2, t, 1.0))
    o.append(CT.curl(BED[0] - 10, MAT - 20, .5, dict(eye=.0, look=(.6, -.4)), t))
    o.append(referat(REF[0], REF[1] - 170, .9, t - W(1)))
    o.append(PR.sparkles(REF[0], REF[1] - 170, 1.4, bump(t, W(1) + .1, .05, .4), t, seed=11, n=6, r=150))
    dx, dy = shake(t, W(1) + .05, 10)
    return hook_view("".join(o), t, HIT, 260, 1230, 1.6, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«сдал реферат»: реферат крупно на столике, штамп бьёт второй раз, искры."""
    a, b = T0("s02"), T1("s02")
    ts = W(3) + .1
    o = bedroom(t)
    o.append(sleeper(t)["svg"])
    o.append(referat(REF[0] + 60, REF[1] - 200, 1.5, t - ts))
    o.append(PR.sparkles(REF[0] + 80, REF[1] - 160, 2.0, bump(t, ts + .1, .05, .5), t, seed=21, n=7, r=240))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts + .05, 12)
    return view("".join(o), 120 + dx, 1050 + dy, 1.55 + .08 * u, -1 + 2 * u, t=t)


def frame_s03(t):
    """«без ночи перед сдачей»: ночь, луна, Дима сладко спит и улыбается, кот свернулся у ног, Z плывут."""
    a, b = T0("s03"), T1("s03")
    o = bedroom(t, night=True)
    o.append(PR.moon(620, 760, 60))
    f = sleeper(t, dict(people.EXPR["dima"]["bliss"], shut=1.0, smile=1.0))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.zzz(hx + 90, hy - 150, 1.4, t, 1.0))
    o.append(CT.curl(BED[0] - 10, MAT - 20, .5, dict(eye=.0, look=(.6, -.4)), t))
    o.append(referat(REF[0], REF[1] - 170, .9, 1.0))
    o.append(rect(-1400, -1400, 2600, 2900, "#1d2448", .3))
    o.append(PR.glow(620, 760, 260, .5, "#fff6d0"))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 330, 1230, 1.5 + .1 * u, 0, bg="#2a2f4a", t=t)


def desk_laptop(t, screen="page", lines=0.0, mode="day", lamp=0.0):
    o = desk_room(t, mode=mode)
    if lamp > 0:
        o.append(PR.lamp_desk(930, DESK_Y, 1.1, on=lamp, seed=2))
    o.append(PR.laptop(640, DESK_Y - 8, 1.0, screen=screen, lines=lines, t=t, seed=1, glow=.6))
    return o


def frame_s04(t):
    """«А раньше неделю смотрел в пустой файл»: ноутбук с пустым документом, курсор мигает, Дима подпёр щёку; счётчик «день 1…7»."""
    a, b = T0("s04"), T1("s04")
    o = desk_laptop(t)
    e = dict(people.EXPR["dima"]["zombie"], look=(.9, .3))
    f = dima_desk(t, e, head_add=.12, lean=.15)
    o.append(f["svg"])
    n = 1 + min(6, int(6 * clamp((t - a) / max(.3, W(14) - a))))
    o.append(PR.calendar(830, 470, 220, 250, stamps=0, seed=1))
    o.append(text(f"{n}", 830, 540, 120 * (1 + .2 * bump(t, a + (n - 1) * (W(14) - a) / 6, .04, .2)), fill="#e2453a", stroke="#111", sw=10))
    o.append(text("ДЕНЬ", 830, 420, 46, fill="#ffffff", stroke="#111", sw=6))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(14), 6)
    return view("".join(o), 600 + dx, 820 + dy, 1.45 + .1 * u, 0, t=t)


def frame_s05(t):
    """«писал всё в последнюю ночь»: ночь, лампа, Дима бешено печатает, строки бегут, часы на стене 3:00, кружки."""
    a, b = T0("s05"), T1("s05")
    o = desk_laptop(t, screen="lines", lines=clamp((t - a) / (b - a)) * .9 + .1, mode="night", lamp=1.0)
    tap = math.sin(t * 40)
    f = dima_desk(t, dict(people.EXPR["dima"]["panic82"], look=(.9, .4)), pose="sit_desk", head_add=.05 + .02 * tap, lean=.25,
                  arms={"f": ("ik", (560 + 15 * tap, DESK_Y - 30), 1), "n": ("ik", (640 - 15 * tap, DESK_Y - 25), 1)})
    o.append(f["svg"])
    o.append(PR.mug(880, DESK_Y - 30, .8, col="red", steam=1.0, t=t, seed=1))
    o.append(PR.mug(960, DESK_Y - 30, .7, col="white", steam=0.0, t=t, seed=2))
    o.append(AL_clock(330, 560, 110, 3, 0))
    o.append(rect(-1400, -1400, 2600, 2900, "#1d2448", .35))
    o.append(PR.glow(700, DESK_Y - 160, 420, .45, "#ffe9a8"))
    hx, hy = f["head"]
    o.append(PR.sweat(hx - 60, hy - 40, 1.2, -20))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(19), 8)
    return view("".join(o), 560 + dx, 860 + dy, 1.4 + .1 * u, 0, bg="#2a2f4a", t=t)


def AL_clock(x, y, r, hh, mm):
    ah, am = PR.clock_hm(hh, mm)
    return PR.clock(x, y, r, ah, am, seed=1)


def frame_s06(t):
    """«а утром сдавал с трясущимися руками»: Дима с мешками под глазами протягивает листы, листы и руки дрожат."""
    a, b = T0("s06"), T1("s06")
    o = [plain_room(t, wall="#dfe6e9")]
    o.append(PR.desk(800, RFL - 330, w=520, depth=90, leg_h=320, seed=9))
    o.append(PR.paper_stack(820, RFL - 350, 1.0, n=6, seed=2))
    sh = 8 * math.sin(t * 47) * (.6 + .4 * math.sin(t * 9))
    e = dict(people.EXPR["dima"]["zombie"], look=(.8, .2), bags=True)
    f = stand(330, t, e, "d82_hold", head_add=.04 + .01 * math.sin(t * 30))
    o.append(f["svg"])
    hx, hy = f["hold"]
    o.append(tf(shape(lib.rect_pts(-90, -120, 90, 120), "#fbf8f1",
                      "".join(line([(-60, -80 + 26 * j), (60 - 20 * (j % 2), -80 + 26 * j)], 3, "#7d8597", seed=840 + j) for j in range(7)),
                      w=3.6, seed=845), hx + 60 + sh, hy - 40 + sh * .4, 1.1, -8 + sh * .6))
    for j in range(3):
        o.append(line([(hx + 170 + 14 * j, hy - 90 + 50 * j), (hx + 200 + 14 * j, hy - 110 + 50 * j)], 5, seed=850 + j))
    o.append(PR.sweat(f["head"][0] - 70, f["head"][1] - 30, 1.2, -20))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(24), 8)
    return view("".join(o), 520 + dx, 1080 + dy, 1.2 + .08 * u, 0, t=t)


def frame_s07(t):
    """«Вот что я поменял»: Дима за столом с ноутбуком поднимает палец, над ним лампочка; надпись сверху."""
    a, b = T0("s07"), T1("s07")
    ti = W(26) + .15
    o = desk_laptop(t)
    f = dima_desk(t, "wow82" if t > ti else "sure82", head_add=.05 * bump(t, ti, .08, .3), lean=0.0)
    o.append(f["svg"])
    hx, hy = f["head"]
    if t > ti:
        o.append(PR.glow(hx + 170, hy - 180, 220, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx + 170, hy - 180 + 8 * math.sin(t * 5), 1.1 * pop(t, ti, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx + 170, hy - 180, 1.8, bump(t, ti, .05, .5), t, seed=71, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ti, 9)
    return view("".join(o), 560 + dx, 820 + dy, 1.4 + .06 * u, -1 + 2 * u, t=t)


def page(x, y, k, rot, day, write=1.0, crooked=0.0, fix=0.0, blank=False, seed=0):
    """Листок дня с одним абзацем: write — дописан на долю, crooked — кривизна и помарки, fix — правка красным."""
    inner = plain(day, -120, -150, 44, fill="#e2453a")
    if not blank:
        n = 5
        for j in range(n):
            u = clamp(write * n - j)
            if u <= 0:
                break
            y0 = -80 + 40 * j
            amp = 10 * crooked * (1 - fix)
            pts = [(-120 + 240 * q * u, y0 + amp * math.sin(q * 9 + j * 2 + seed)) for q in [i / 12 for i in range(13)]]
            inner += line(pts, 5, "#3a4157", taper=.2, wmin=.5, seed=860 + j + seed)
            if crooked > 0 and j in (1, 3) and fix < .5:
                inner += line([(-60 + 30 * j, y0 - 14), (20 + 30 * j, y0 + 12)], 5, "#3a4157", seed=870 + j)
        if fix > 0:
            for j in (1, 3):
                yy = -80 + 40 * j
                inner += line([(-120, yy - 6), (-120 + 240 * clamp(fix * 2 - (j == 3)), yy - 6)], 4, "#e2453a", taper=.2, wmin=.5, seed=880 + j)
    o = blob(lib.rect_pts(-160 + 10, -210 + 12, 160 + 10, 210 + 12), "#000000", .14)
    o += shape(lib.rect_pts(-160, -210, 160, 210), "#fbf8f1", inner, w=4, seed=890 + seed)
    return tf(o, x, y, k, rot)


def frame_s08(t):
    """«Каждый день пишу один абзац»: три листка дней ПН ВТ СР выскакивают по очереди, на каждом дописывается абзац."""
    a, b = T0("s08"), T1("s08")
    o = [paper_bg()]
    days = [("ПН", 230, 860, -6), ("ВТ", 550, 740, 3), ("СР", 860, 880, -2)]
    starts = [a, W(32) - .1, W(34) - .1]
    for j, ((d, x, y, r), ts) in enumerate(zip(days, starts)):
        if t >= ts - .05:
            o.append(page(x, y, 1.3 * pop(t, ts - .05, .2), r, d, write=clamp((t - ts) / .5), seed=j))
    cu = ease_out(ramp(t, a + .1, .4))
    o.append(cat(560, 1380, .75 * cu + .01, t, dict(look=(-.3, -.8), smile=.8)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(34), 6)
    return view("".join(o), 560 + dx, 1000 + dy, 1.0 + .08 * u, 0, bg=PAPER, t=t)


def frame_s09(t):
    """«даже кривой»: кривой абзац с помарками крупно, Дима сбоку пожимает плечами и улыбается, кот кивает."""
    a, b = T0("s09"), T1("s09")
    o = [paper_bg()]
    o.append(page(640, 760, 1.6, 3, "ЧТ", write=1.0, crooked=1.0, seed=4))
    k = .7
    f = people.dima82(230, 1640 - (people.LEG_LEN - 12) * k - 6, k, "laugh82", "d82_shrug", t=t, feet="stand", head_add=.05 * math.sin(t * 5))
    o.append(f["svg"])
    o.append(cat(860, 1640, .8, t, dict(look=(-.6, -.6), smile=1.0, perk=bump(t, W(36), .05, .4))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(36), 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


def red_pen(x, y, k=1.6, rot=-130.0):
    a = math.radians(rot)
    L = 62 * k
    return PR.red_marker(x - L * math.cos(a), y - L * math.sin(a), k, rot)


def frame_s10(t):
    """«Плохой черновик можно исправить»: красная ручка проходит по кривому абзацу — строки выпрямляются, галочка."""
    a, b = T0("s10"), T1("s10")
    fx = clamp((t - W(38)) / max(.3, W(40) + .3 - W(38)))
    o = [paper_bg()]
    o.append(page(540, 860, 2.0, 2, "ЧТ", write=1.0, crooked=1.0, fix=fx, seed=4))
    if 0 < fx < 1:
        yy = -80 + 40 * (1 if fx < .5 else 3) - 6
        xx = -120 + 240 * clamp(fx * 2 - (fx >= .5))
        o.append(red_pen(540 + xx * 2.0, 860 + yy * 2.0))
    if fx >= 1:
        o.append(PR.check_mark(800, 560, 3.0, ramp(t, W(40) + .3, .3), col="#e2453a", w=10))
        o.append(PR.sparkles(780, 560, 1.8, bump(t, W(40) + .5, .05, .5), t, seed=101, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(40) + .5, 8)
    return view("".join(o), 540 + dx, 900 + dy, 1.0 + .08 * u, 0, bg=PAPER, t=t)


def frame_s11(t):
    """«а пустой лист нельзя»: пустой листок крупно, красная ручка зависает над ним и не знает, что править; «?»."""
    a, b = T0("s11"), T1("s11")
    o = [paper_bg()]
    o.append(page(540, 860, 2.0, -2, "ПТ", blank=True, seed=5))
    hov = 1 - ease_out(ramp(t, a, .4))
    o.append(red_pen(560 + 80 * math.sin(t * 3), 820 + 40 * math.cos(t * 4) - 200 * hov))
    if t > W(43):
        o.append(PR.question_mark(780, 520, 2.6, pop(t, W(43), .25), col="#e2453a"))
    o.append(cat(900, 1420, .8, t, dict(look=(-.8, -.6), smile=.0, ear_r=.3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(44), 8)
    return view("".join(o), 540 + dx, 940 + dy, 1.0 + .08 * u, 0, bg=PAPER, t=t)


_LP = {}


def cta(t, zoom=1.0, focus=None):
    c = SH["cta"]
    if "bg" not in LP._ST:
        LP._ST["bg"] = LP.tg.background(lib)
        LP.tg.prepare(COMMON)
        lib.static_done()
    lib.dyn_begin()
    body, (cx, cy, s, rot) = LP.layer(t, c["t0"], c["press"], COMMON)
    if focus:
        cx, cy = cx + (focus[0] - cx) * .3, cy + (focus[1] - cy) * .3
    return lib.svg(f'<rect width="1080" height="1920" fill="#6e4a32"/><g transform="{lib.cam(cx, cy, s * zoom, rot)}">{LP._ST["bg"]}{body}</g>{over(t)}')


def frame_s12(t):
    return cta(t)


def frame_s13(t):
    return cta(t, 1.15, LP.BTN_C)


def frame_s14(t):
    return cta(t, 1.08)


def frame_s15(t):
    """«Сдал за два дня до срока»: календарь, срок обведён красным, штамп «СДАН» шлёпается за два дня до него; надпись «ЗА 2 ДНЯ»."""
    a, b = T0("s15"), T1("s15")
    o = [plain_room(t)]
    o.append(PR.calendar(540, 900, 760, 860, stamps=0, seed=2))
    cw, ch = (760 - 60) / 7, (860 - 180) / 5
    gx0, gy0 = 540 - 380 + 30, 900 - 430 + 150
    dl = (gx0 + cw * 5.5, gy0 + ch * 2.5)
    sd = (gx0 + cw * 3.5, gy0 + ch * 2.5)
    o.append(line([(dl[0] + 58 * math.cos(q * 6.6), dl[1] + 50 * math.sin(q * 6.6)) for q in [i / 30 for i in range(31)]], 8, "#e2453a", seed=150))
    o.append(text("СРОК", dl[0], dl[1] - 80, 40, fill="#e2453a", stroke="#ffffff", sw=6))
    ts = W(61) - .05
    o.append(stamp(sd[0], sd[1], .7, t - ts) if t > ts else "")
    if t > ts + .2:
        o.append(PR.dash_arrow([(sd[0] + 60, sd[1] + 80), (dl[0] - 10, dl[1] + 90)], u=ramp(t, ts + .2, .3), w=6, col="#2f6fd1"))
    o.append(PR.sparkles(sd[0], sd[1], 1.6, bump(t, ts + .1, .05, .5), t, seed=151, n=6, r=150))
    f = stand(170, t, "proud82", "d82_one", head_add=.05)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts + .05, 10)
    return view("".join(o), 520 + dx, 1050 + dy, 1.15 + .06 * u, 0, t=t)


def frame_s16(t):
    """«и выспался»: утро, солнце в окне, Дима потягивается у кровати, кот на подушке, реферат со штампом на столике."""
    a, b = T0("s16"), T1("s16")
    o = bedroom(t, sun=1.0)
    o.append(PR.pillow(BED[0] - 230, MAT - 10, 1.3, seed=1))
    o.append(cat(BED[0] - 190, MAT - 6, .5, t, dict(look=(.8, -.2), smile=1.0, tail=10 * math.sin(t * 3))))
    o.append(referat(REF[0], REF[1] - 170, .9, 1.0))
    st = ease_out(ramp(t, a - .1, .4))
    f = stand(720, t, "stretch78", "d82_rest", k=.74,
              arms={"n": ("ik", (600 - 140 * st, 760 - 300 * st), -1), "f": ("ik", (860 + 100 * st, 760 - 300 * st), 1)}, head_add=.03)
    o.append(f["svg"])
    o.append(PR.sparkles(720, 600, 1.6, bump(t, W(66), .05, .5), t, seed=161, n=6, r=220))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 640, 1000, 1.1 + .05 * u, 0, t=t)


def frame_s17(t):
    """Петля: кадр хука — Дима спит, реферат на столике."""
    a, b = T0("s17"), T1("s17")
    o = bedroom(t)
    f = sleeper(t)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.zzz(hx + 90, hy - 140, 1.2, t, 1.0))
    o.append(CT.curl(BED[0] - 10, MAT - 20, .5, dict(eye=.0, look=(.6, -.4)), t))
    o.append(referat(REF[0], REF[1] - 170, .9, -1.0))
    return loop_view("".join(o), t, a, b, HIT, 260, 1230, 1.6)


def frame(sid, t):
    if sid not in ("s12", "s13", "s14"):
        lib.DEFS.clear()
    return globals()["frame_" + sid](t)
