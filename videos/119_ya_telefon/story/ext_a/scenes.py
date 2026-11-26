"""Рилс 119 «Я телефон», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит телефон (голос Даниила): у телефона лицо на экране — глаза и рот,
рот открывается на словах. Руки Димы — кисти с пальцами (people.hand_svg). NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

HIT = stress(1, .4)
SLEEVE = "#d9a441"


def talking(t):
    """Телефон говорит: рот открыт, пока звучит слово."""
    for w in WORDS:
        if w["start"] - .02 <= t <= w["end"]:
            return .4 + .6 * abs(math.sin((t - w["start"]) * 18))
    return 0.0


def phone_face(x, y, k, t, mood="happy", rot=0.0, talk=None, glow=0.0, face_down=False, mask=0.0):
    """Телефон с лицом: (x, y) — центр, экран 360×680. mood: happy, tired, dizzy, sad, roll, calm, sleep."""
    o = [blob(lib.rect_pts(-200 + 14, -380 + 18, 200 + 14, 380 + 18), "#000000", .18)]
    if face_down:
        o.append(shape(lib.rrect(-200, -380, 200, 380, 50), "#3a3d48", blob(ellipse_pts(-110, -280, 40, 40, 16), "#2a2d36")
                       + shape(ellipse_pts(-110, -280, 26, 26, 14), "#1c1c22", "", w=3, seed=5001), w=5, seed=5000))
        return tf("".join(o), x, y, k, rot)
    o.append(shape(lib.rrect(-200, -380, 200, 380, 50), "#2a2d36", "", w=5, seed=5000))
    scr = "#bfe3ff" if mood not in ("tired", "sleep") else ("#9fb6d6" if mood == "tired" else "#5a6aa0")
    inner = ""
    if glow > 0:
        inner += PR.glow(0, 0, 300, .5 * glow, "#ffffff")
    ey = -90
    if mood == "sleep" or mask > 0:
        inner += line([(-120, ey), (-90, ey + 16), (-60, ey)], 7, seed=5010) + line([(60, ey), (90, ey + 16), (120, ey)], 7, seed=5011)
        if mask > 0:
            m = shape([(-170, ey - 50, 1), (170, ey - 50, 1), (175, ey + 40, 1), (0, ey + 60, 1), (-175, ey + 40, 1)], "#7d6aa8",
                      blob(ellipse_pts(-90, ey, 60, 30, 14), "#9a87c4") + blob(ellipse_pts(90, ey, 60, 30, 14), "#9a87c4"), w=4, seed=5012)
            m += line([(-175, ey - 10), (-200, ey - 20)], 6, "#7d6aa8", seed=5013) + line([(175, ey - 10), (200, ey - 20)], 6, "#7d6aa8", seed=5014)
            inner += f'<g opacity="{mask:.3f}">{m}</g>'
    else:
        for s_, ex in ((-1, -90), (1, 90)):
            rx, ry = 52, 62
            inner += shape(ellipse_pts(ex, ey, rx, ry, 20), "#ffffff", "", w=4, seed=5020 + s_)
            if mood == "dizzy":
                pts = [(ex + 4 * a * math.cos(a * 2.2 + t * 8), ey + 4 * a * math.sin(a * 2.2 + t * 8)) for a in [q * .4 for q in range(30)]]
                inner += line(pts, 4, seed=5022)
            else:
                lk = (0, -30) if mood == "roll" else (6 * math.sin(t * 2), 8)
                inner += blob(ellipse_pts(ex + lk[0], ey + lk[1], 24, 28, 14), "#1c1622")
                inner += blob(ellipse_pts(ex + lk[0] + 8, ey + lk[1] - 10, 8, 8, 8), "#ffffff")
            if mood in ("tired", "sad"):
                inner += blob([(ex - rx - 4, ey - ry - 4), (ex + rx + 4, ey - ry - 4), (ex + rx + 4, ey - 10), (ex - rx - 4, ey - 4)], scr)
                inner += line([(ex - rx, ey - 6), (ex + rx, ey - 12)], 5, seed=5024)
            if mood == "tired":
                inner += line([(ex - 40, ey + 80), (ex, ey + 92), (ex + 40, ey + 80)], 5, "#6b5a96", seed=5025)
        if mood == "sad":
            inner += line([(-150, ey - 90), (-50, ey - 110)], 7, seed=5026) + line([(50, ey - 110), (150, ey - 90)], 7, seed=5027)
    tk = talking(t) if talk is None else talk
    my = 120
    if mood == "sleep" or mask > 0:
        inner += line([(-30, my), (30, my)], 6, seed=5030) if tk < .1 else shape(ellipse_pts(0, my, 34, 30 * tk + 6, 16), "#5a2b33", "", w=4, seed=5031)
    elif tk > .05:
        inner += shape(ellipse_pts(0, my, 70, 18 + 46 * tk, 20), "#5a2b33", blob(ellipse_pts(0, my + 18 + 30 * tk, 40, 16, 12), "#e0707a"), w=5,
                       seed=5032)
    elif mood in ("happy", "calm"):
        inner += line([(-60, my - 10), (0, my + 20), (60, my - 10)], 7, seed=5033)
    else:
        inner += line([(-50, my + 10), (0, my - 6), (50, my + 10)], 7, seed=5034)
    o.append(shape(lib.rrect(-176, -350, 176, 350, 32), scr, inner, w=3, seed=5040))
    o.append(shape(lib.rrect(-50, -340, 50, -320, 10), "#1c1c22", "", w=2, seed=5041))
    return tf("".join(o), x, y, k, rot)


def hand_to(tip, frm, k=2.2, curl=(.55, .5, .55, .6), thumb=.6, seed=700):
    """Кисть Димы с рукавом: рукав от frm (за краем кадра) к запястью, пальцы к tip."""
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    L = math.hypot(dx, dy) or 1
    d = (dx / L, dy / L)
    wr = (tip[0] - d[0] * 120 * k, tip[1] - d[1] * 120 * k)
    o = shape(lib.band([frm, (wr[0] - d[0] * 20 * k, wr[1] - d[1] * 20 * k)], 70 * k, 56 * k), SLEEVE, "", w=5, seed=seed)
    o += people.hand_svg("dima", wr, d, k=k, curl=curl, thumb=thumb, seed=seed + 1)
    return o


def grab_u(t, t0, d=.18):
    """0 — рука у края, 1 — схватила (подлёт с разгоном)."""
    u = clamp((t - t0) / d)
    return u * u


def table_bg(t, wall="#efe2c8"):
    o = [rect(-1400, -1400, 2600, 1400, wall)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, 1400, lib.mul(wall, (.96, .95, .93)), .55))
    o.append(rect(-1400, 1400, 2600, 3000, "#c99a6b"))
    o.append(line([(-1400, 1400), (2600, 1400)], 6, seed=11))
    for j in range(5):
        o.append(line([(-1400, 1500 + 120 * j), (2600, 1520 + 120 * j)], 3, "#a8774a", taper=0, wmin=1, seed=5100 + j))
    return o


PH = (540.0, 1050.0)


def frame_s01(t):
    """ХУК: телефон с лицом на столе, рука влетает и хватает его, отпускает и хватает снова; кот рядом смотрит."""
    o = table_bg(t)
    grabs = [-.05, .55]
    held = 0.0
    hand = ""
    for g in grabs:
        if g - .25 <= t < g + .35:
            u = grab_u(t, g - .1, .12) - grab_u(t, g + .2, .12)
            held = max(held, u)
            hand = hand_to((PH[0] + 160, PH[1] + 120), (1500, 1900), k=2.2) if u > .5 else hand_to((PH[0] + 300 + 600 * (1 - u), PH[1] + 200 + 400 * (1 - u)),
                                                                                                   (1500, 1900), k=2.2, curl=(.2, .15, .2, .25), thumb=.2)
    o.append(phone_face(PH[0], PH[1] - 60 * held, 1.0, t, "sad" if held > .5 else "roll", rot=-6 * held))
    o.append(cat(170, 1420, .85, t, dict(look=(.9, -.3), perk=1.0, tail=10 * math.sin(t * 3))))
    o.append(hand)
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 540, 1080, 1.0, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«меня берут в руки»: три руки по очереди тянутся к телефону с разных сторон и хватают."""
    a, b = T0("s02"), T1("s02")
    o = table_bg(t)
    o.append(phone_face(PH[0], PH[1], 1.0, t, "sad"))
    srcs = [((-500, 600), (PH[0] - 150, PH[1] - 200)), ((1600, 700), (PH[0] + 150, PH[1] - 150)), ((540, 2300), (PH[0], PH[1] + 300))]
    for j, (frm, tip) in enumerate(srcs):
        tj = a + .25 * j
        u = ease_out(ramp(t, tj, .2))
        if u > 0:
            tp = (frm[0] + (tip[0] - frm[0]) * u, frm[1] + (tip[1] - frm[1]) * u)
            o.append(hand_to(tp, frm, k=1.8, seed=700 + 10 * j))
    o.append(cat(170, 1420, .85, t, dict(look=(.9, -.4), perk=1.0)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(4), 8)
    return view("".join(o), 540 + dx, 1080 + dy, 1.0 + .05 * u, 0, t=t)


def frame_s03(t):
    """«каждые пять минут»: часы рядом, минутная стрелка прыгает на 5, и рука снова хватает телефон."""
    a, b = T0("s03"), T1("s03")
    o = table_bg(t)
    jumps = [a + .1, a + .5, W(8)]
    n = sum(1 for q in jumps if t >= q)
    o.append(PR.clock(830, 560, 150, *PR.clock_hm(9, 5 * n), seed=1))
    o.append(text("5 мин", 830, 820, 80, fill="#e2453a", stroke="#111", sw=8))
    held = max(grab_u(t, q - .1, .1) - grab_u(t, q + .2, .1) for q in jumps)
    o.append(phone_face(PH[0] - 120, PH[1] - 40 * held, .9, t, "sad"))
    if held > .05:
        o.append(hand_to((PH[0] + 20, PH[1] + 100), (1500, 1900), k=2.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(8), 8)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .05 * u, 0, t=t)


def bedroom(t, night=False):
    o = [plain_room(t, wall="#c9c2d8" if night else WALL, floor="#a99a8a" if night else FLOOR_C)]
    o.append(PR.window(800, 950, 300, 380, mode="night" if night else "day", t=t, seed=3, curtain=False))
    o.append(PR.bed(560, RFL, 1.25, seed=1))
    o.append(shape(lib.rrect(-40, RFL - 300, 200, RFL, 10), "#a8774a", "", w=4, seed=620))
    return o


def frame_s04(t):
    """«Утром меня хватают вместо будильника»: тумба, будильник звенит, а рука тянется мимо него и хватает телефон."""
    a, b = T0("s04"), T1("s04")
    tg = W(14)
    o = table_bg(t, wall="#fff1d6")
    o.append(PR.glow(300, 700, 600, .4, "#fff1b0"))
    import alarm as AL
    o.append(AL.alarm(820, 1230, 190, hh=7, mm=0, ring=1.0, t=t, uid="al4") + AL.ring_marks(820, 1230, 190, t, 1.0))
    u = grab_u(t, tg - .15, .15)
    lift = ease_out(ramp(t, tg + .1, .3))
    o.append(phone_face(380, 1230 - 160 * lift, .7, t, "roll" if u < .5 else "sad", rot=-80 + 70 * lift))
    tip = (380 + 150, 1230 - 160 * lift + 40) if u >= 1 else (1500 - (1500 - 460) * u, 300 + (1300 - 300) * u)
    o.append(hand_to(tip, (1500, 200), k=1.6))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tg, 9)
    return view("".join(o), 560 + dx, 1100 + dy, 1.15 + .05 * uu, 0, t=t)


def frame_s05(t):
    """«и листают в кровати»: Дима лежит в кровати, держит телефон над лицом и листает; у телефона кружится голова."""
    a, b = T0("s05"), T1("s05")
    o = bedroom(t)
    mat = RFL - 118 * 1.25
    f = people.dima_bed(620, mat + 10, .62, expr=dict(people.EXPR["dima"]["screen74"]) if "screen74" in people.EXPR["dima"] else "awake73", t=t,
                        cover="chest", col="blue")
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(phone_face(hx + 200, hy - 300, .5, t, "dizzy", rot=170 + 6 * math.sin(t * 9)))
    o.append(hand_to((hx + 200, hy - 160), (hx + 400, hy + 200), k=1.0, seed=760))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 520, 1200, 1.45 + .08 * u, 0, t=t)


def frame_s06(t):
    """«На паре прячут под партой»: парта крупно, Дима сидит, под партой в руке спрятан телефон, у телефона испуганное лицо."""
    a, b = T0("s06"), T1("s06")
    o = desk_room(t)
    o.append(PR.paper(560, DESK_Y - 40, 1.6, -6, w=180, h=130, seed=3, kind="lines", sy=.5))
    f = dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.4, .9)), head_add=.18, lean=.15)
    o.append(f["svg"])
    hide = ease_out(ramp(t, W(22), .3))
    o.append(phone_face(600, DESK_Y + 120 - 20 * hide, .42, t, "sad", rot=-10))
    o.append(rect(-1400, DESK_Y + 10, 2600, DESK_Y + 30, "#8a6038", .0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(23), 6)
    return view("".join(o), 540 + dx, 960 + dy, 1.5 + .08 * u, 0, t=t)


def frame_s07(t):
    """«„на секундочку“»: у Димы пузырь «на секундочку», телефон крупно закатывает глаза."""
    a, b = T0("s07"), T1("s07")
    o = table_bg(t, wall="#dfe6e9")
    o.append(phone_face(640, 1100, .95, t, "roll"))
    o.append(PR.speech_bubble(380, 560, 560, 220, pop(t, a, .2), seed=3, tail=(-150, 80)))
    if t > a + .1:
        o.append(plain("на секундочку", 380, 580, 60, fill="#1d2448", anchor="middle"))
    o.append(hand_to((520, 1300), (-300, 1900), k=1.8, curl=(.6, .6, .6, .65), seed=780))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1000, 1.0 + .06 * u, 0, t=t)


def frame_s08(t):
    """«А ночью мной светят в лицо»: тёмная спальня, Дима в кровати, яркий свет экрана бьёт ему в лицо."""
    a, b = T0("s08"), T1("s08")
    o = bedroom(t, night=True)
    mat = RFL - 118 * 1.25
    f = people.dima_bed(620, mat + 10, .62, expr="awake73", t=t, cover="chest", col="blue")
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(rect(-1400, -1400, 2600, 2900, "#0e1230", .55))
    o.append(PR.beam(hx + 150, hy - 280, ang=100, length=300, spread=30, u=1.0, k=1.0, color="#cfe8ff"))
    o.append(PR.glow(hx, hy, 240, .7, "#cfe8ff"))
    o.append(phone_face(hx + 180, hy - 300, .5, t, "tired", rot=180, glow=1.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(29), 6)
    return view("".join(o), 500 + dx, 1200 + dy, 1.5 + .08 * u, 0, bg="#0e1230", t=t)


def frame_s09(t):
    """«до трёх»: часы показывают 3:00, телефон крупно — мешки под глазами, зевает."""
    a, b = T0("s09"), T1("s09")
    hh = 1 + 2 * clamp((t - a) / (W(33) - a))
    o = [rect(-1400, -1400, 2600, 2900, "#1d2448")]
    o.append(PR.clock(800, 560, 170, *PR.clock_hm(hh, (hh % 1) * 60), seed=1))
    if t > W(33):
        o.append(text("3:00", 800, 840, 110, fill="#ffffff", stroke="#111", sw=8))
    o.append(phone_face(400, 1150, .9, t, "tired", glow=.5))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(33), 8)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .06 * u, 0, bg="#1d2448", t=t)


def frame_s10(t):
    """«Но вчера меня унесли в другую комнату»: Дима идёт к двери, несёт телефон в вытянутой руке, телефон удивлён."""
    a, b = T0("s10"), T1("s10")
    o = [plain_room(t)]
    o.append(PR.door(950, RFL, 1.0, ajar=.6, seed=4))
    k = .72
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    x = 200 + 520 * ease_io(ramp(t, a, b - a))
    f = people.dima82_run(x, hip, k, (t - a) / .6, t=t, expr="proud82", boot=False, socks=None, sandwich=False) if hasattr(people, "dima82_run") else None
    f = people.dima82(x, hip, k, "proud82", "d82_hold", t=t, feet=people.walk_kw(x, hip, k, (t - a) * 6)["feet"])
    o.append(f["svg"])
    hx, hy = f["hold"]
    o.append(phone_face(hx + 60, hy - 120, .32, t, "roll"))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 400 + 300 * u, 1050, 1.15, 0, t=t)


def shelf_room(t, night=False):
    o = [plain_room(t, wall="#d9d2c3")]
    o.append(shape(lib.rect_pts(250, 1150, 850, 1180), "#a8774a", "", w=4, seed=5200))
    for x in (290, 810):
        o.append(line([(x, 1180), (x, 1230)], 8, "#6b432b", seed=5201))
    o.append(PR.book_closed(330, 1120, .8))
    return o


def frame_s11(t):
    """«и положили экраном вниз»: рука кладёт телефон на полку и переворачивает экраном вниз."""
    a, b = T0("s11"), T1("s11")
    flip = ease_io(ramp(t, W(43), .35))
    o = shelf_room(t)
    sy = math.cos(math.pi * flip)
    ph = phone_face(0, 0, 1.0, t, "sad", face_down=flip > .5)
    o.append(f'<g transform="translate(560 1130) scale(.5 {.12 + .1 * abs(sy):.3f})">' + tf(ph, 0, 0, 1.0, 0) + "</g>"
             if flip > .02 else phone_face(560, 1000, .45, t, "sad", rot=0))
    if flip < 1:
        o.append(hand_to((600, 1000 + 120 * flip), (1500, 300), k=1.5))
    o.append(PR.dust_puff(560, 1150, .5, ramp(t, W(44), .4), seed=3))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(44), 8)
    return view("".join(o), 560 + dx, 1050 + dy, 1.5 + .06 * u, 0, t=t)


def lying_phone(x, y, k, t):
    """Телефон лежит экраном вниз; изнутри «говорит» — от него расходятся дуги звука."""
    o = shape(lib.rrect(-200, -40, 200, 0, 18), "#3a3d48", "", w=4, seed=5210)
    tk = talking(t)
    if tk > .05:
        for j in range(2):
            o += line([(220 + 30 * j, -60 - 20 * j), (240 + 30 * j, -20), (220 + 30 * j, 20 + 20 * j)], 5, "#5a5f6e", seed=5211 + j, op=tk)
    return tf(o, x, y, k)


def frame_s12(t):
    """«Я ждал час»: телефон лежит экраном вниз на полке, настенные часы прокручивают целый час."""
    a, b = T0("s12"), T1("s12")
    o = shelf_room(t)
    m = 60 * clamp((t - a) / (b - a))
    o.append(PR.clock(560, 700, 160, *PR.clock_hm(4, m), seed=1))
    o.append(lying_phone(560, 1150, .6, t))
    o.append(text("1 час", 560, 940, 90, fill="#e2453a", stroke="#111", sw=8) if t > W(47) else "")
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 960, 1.2 + .06 * u, 0, t=t)


def frame_s13(t):
    """«Никто не пришёл»: пустая комната, дверь закрыта, телефон лежит один на полке."""
    a, b = T0("s13"), T1("s13")
    o = shelf_room(t)
    o.append(PR.door(950, RFL, 1.0, ajar=0.0, seed=4))
    o.append(lying_phone(560, 1150, .6, t))
    o.append(rug(560, RFL + 150, 560))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(50), 5)
    return view("".join(o), 640 + dx, 1100 + dy, 1.0 + .05 * u, 0, t=t)


def frame_s14(t):
    """«Из-за двери доносилось только»: закрытая дверь крупно, из-под неё полоска света, от неё расходятся звуковые дуги."""
    a, b = T0("s14"), T1("s14")
    o = [plain_room(t, wall="#d9d2c3")]
    o.append(PR.door(540, RFL, 1.1, ajar=0.0, seed=4))
    o.append(rect(380, RFL - 12, 700, RFL, "#fff4c0"))
    o.append(PR.glow(540, RFL - 10, 300, .4, "#fff4c0"))
    for j in range(3):
        u = ((t - a) * 1.2 + j / 3) % 1
        r = 120 + 260 * u
        o.append(line([(540 + r * math.cos(q), 900 + r * math.sin(q)) for q in [-.5 + .1 * i for i in range(11)]], 7, "#5a5f6e", seed=5220 + j, op=1 - u))
    o.append(lying_phone(160, 1180, .5, t))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1050, 1.0 + .08 * u, 0, t=t)


def frame_s15(t):
    """«как он печатает и мурлычет кот»: за дверью Дима печатает на ноутбуке, кот сидит рядом на столе и мурлычет."""
    a, b = T0("s15"), T1("s15")
    o = desk_room(t, sun=1.0)
    o.append(PR.laptop(640, DESK_Y - 8, 1.0, screen="lines", lines=clamp((t - a) / (b - a)), t=t, seed=1))
    tap = math.sin(t * 30)
    f = dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.9, -.1)), lean=.18,
                  arms={"f": ("ik", (560 + 10 * tap, DESK_Y - 30), 1), "n": ("ik", (640 - 10 * tap, DESK_Y - 25), 1)})
    o.append(f["svg"])
    o.append(cat(940, DESK_Y - 4, .55, t, dict(look=(-.8, -.2), smile=1.0, squint=.6, tail=10 * math.sin(t * 3))))
    o.append(PR.purr(940, DESK_Y - 220, 1.2, t, ramp(t, W(59) - .1, .3)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 640, 820, 1.4 + .06 * u, 0, t=t)


def frame_s16(t):
    return cta_code(t, T0("s16"), T1("s16"))


def frame_s17(t):
    """«чтобы и твой телефон наконец отдохнул»: телефон лежит на маленькой подушке, довольно улыбается; кот рядом."""
    a, b = T0("s17"), T1("s17")
    o = table_bg(t, wall="#f3e6ff")
    o.append(PR.cushion(540, 1300, 2.4, sy=.5, col=("#d6c7f0", "#b9a8de", "#ece4fb"), seed=2))
    o.append(phone_face(540, 1150, .8, t, "calm", rot=-80))
    o.append(cat(880, 1420, .85, t, dict(look=(-.8, -.3), smile=1.0, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(540, 1000, 1.8, bump(t, W(69), .05, .5), t, seed=171, n=6, r=280))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1080, 1.0 + .06 * u, 0, t=t)


def frame_s18(t):
    """«Этой ночью я впервые выспался»: ночь, телефон спит на подушке в маске для сна, Z плывут; кот спит рядом."""
    a, b = T0("s18"), T1("s18")
    o = table_bg(t, wall="#2a2f4a")
    o.append(PR.moon(860, 400, 70))
    o.append(PR.cushion(540, 1300, 2.4, sy=.5, col=("#7d6aa8", "#5f4f8a", "#9a87c4"), seed=2))
    o.append(phone_face(540, 1150, .8, t, "sleep", rot=-80, mask=1.0))
    o.append(PR.zzz(700, 880, 1.6, t, 1.0))
    o.append(CT.curl(880, 1400, .6, dict(eye=.0), t))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1080, 1.0 + .06 * u, 0, bg="#2a2f4a", t=t)


def frame_s19(t):
    """Петля: кадр хука — телефон с лицом на столе, рука тянется."""
    a, b = T0("s19"), T1("s19")
    o = table_bg(t)
    o.append(phone_face(PH[0], PH[1], 1.0, t, "roll"))
    o.append(cat(170, 1420, .85, t, dict(look=(.9, -.3), perk=1.0)))
    u = ramp(t, a, b - a)
    o.append(hand_to((PH[0] + 300 + 600 * (1 - u), PH[1] + 200 + 400 * (1 - u)), (1500, 1900), k=2.2, curl=(.2, .15, .2, .25), thumb=.2))
    return loop_view("".join(o), t, a, b, HIT, 540, 1080, 1.0)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
