"""Рилс 115 «Английский», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Места: экран приложения крупно (огонёк серии),
комната, ванная с зеркалом и раковиной. Приложение своё, без чужих логотипов. NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

HIT = stress(1, .3)
SKIN = "#ecc4a2"
APP = "#4f6bd8"
PH = (540.0, 960.0)


def phone(x, y, k, inner, bg="#fbf8f1"):
    o = shape(lib.rrect(-220, -400, 220, 400, 50), "#2a2d36", "", w=5, seed=2000)
    o += shape(lib.rrect(-196, -370, 196, 370, 32), bg, inner, w=3, seed=2001)
    return tf(o, x, y, k)


def flag_en(x, y, k=1.0):
    o = shape(lib.rrect(-60, -40, 60, 40, 8), "#ffffff", "".join(rect(-60, -40 + 16 * j, 60, -32 + 16 * j, "#e2453a") for j in range(5))
              + rect(-60, -40, -8, 0, "#2f4fa8"), w=3, seed=2050)
    return tf(o, x, y, k)


def streak_screen(n, t, glow=0.0):
    """Экран приложения: шапка «English», флаг, огонёк серии и число дней."""
    inner = rect(-196, -370, 196, -250, APP)
    inner += plain("English", -150, -290, 50, fill="#ffffff")
    inner += flag_en(120, -310, .7)
    if glow > 0:
        inner += PR.glow(0, -40, 220, .6 * glow, "#ffb347")
    inner += PR.att_flame(0, 40, 3.2, t, 1.0, seed=1)
    inner += text(str(n), 0, 260, 170, fill="#ff8a1f", stroke="#111", sw=10)
    inner += plain("дней подряд", 0, 330, 40, fill="#5a5f6e", anchor="middle")
    return inner


def counter(t, a, b, n0=1, n1=60):
    u = clamp((t - a) / max(.05, b - a))
    u = 1 - (1 - u) ** 2
    return int(round(n0 + (n1 - n0) * u))


def room(t):
    o = [plain_room(t)]
    o.append(rug(540, RFL + 150, 600))
    o.append(PR.window(800, 1000, 300, 380, mode="day", t=t, seed=4, curtain=False))
    return o


def hand_phone(x, y, k, inner, rot=0.0):
    """Телефон в руке снизу (рукав худи)."""
    o = shape(lib.band([(x + 260, y + 1500), (x + 60, y + 400 * k)], 300, 220), "#d9a441", "", w=5, seed=2060)
    o += shape(ellipse_pts(x + 40, y + 380 * k, 190, 120, 16), SKIN, "", w=5, seed=2061)
    o += phone(x, y, k, inner)
    o += shape(ellipse_pts(x - 190 * k, y + 220 * k, 34, 70, 12), SKIN, "", w=4, seed=2062)
    return tf(o, 0, 0, 1.0, rot)


def frame_s01(t):
    """ХУК: экран приложения крупно в руке, огонёк серии, счётчик крутится с 1 до 60."""
    n = counter(t, 0.0, W(5))
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 800, .35, "#ffb347")]
    o.append(hand_phone(PH[0], PH[1], 1.3, streak_screen(n, t, glow=.6)))
    o.append(PR.sparkles(540, 900, 2.2, .6 + .4 * math.sin(t * 9), t, seed=11, n=6, r=380))
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 540, 980, 1.0, 0, bg="#3b3552", dx=dx, dy=dy)


def confetti(t, t0, n=18, cx=540, y0=300, spread=900):
    o = []
    for j in range(n):
        rs = (j * 37 % 17) / 17
        u = ramp(t, t0 + .02 * j, 1.2)
        if u > 0:
            x = cx + (rs - .5) * spread
            y = y0 + 900 * u * u - 300 * u
            col = ("#e2453a", "#FFD23F", "#3fb26a", "#2f8fe0")[j % 4]
            o.append(tf(shape(lib.rect_pts(-14, -8, 14, 8), col, "", w=2, seed=1200 + j), x, y, 1.0, 360 * u * (1 + rs)))
    return "".join(o)


def frame_s02(t):
    """«учу английский каждый день»: Дима смотрит в телефон и улыбается, над ним огонёк и «60», на «день» — конфетти; кот рядом."""
    a, b = T0("s02"), T1("s02")
    n = counter(t, -.3, W(5))
    o = room(t)
    f = stand(380, t, "laugh82" if t > W(5) else "proud82", "d82_hold", head_add=.05)
    o.append(f["svg"])
    hx, hy = f["hold"]
    o.append(phone(hx + 30, hy - 60, .32, streak_screen(n, t)))
    fx, fy = f["head"][0] + 300, f["head"][1] - 40
    o.append(PR.att_flame(fx, fy + 60, 2.2 * (1 + .2 * bump(t, W(5), .05, .3)), t, 1.0, seed=2))
    o.append(text(str(n), fx + 140, fy + 80, 150, fill="#ff8a1f", stroke="#111", sw=10))
    o.append(cat(850, RFL, .8, t, dict(look=(-.7, -.6), smile=1.0, tail=10 * math.sin(t * 3))))
    o.append(confetti(t, W(5)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(5), 9)
    return view("".join(o), 560 + dx, 920 + dy, 1.12 + .05 * u, -1 + 2 * u, t=t)


def app_icon(x, y, k, wob=0.0, op=1.0):
    o = shape(lib.rrect(-70, -70, 70, 70, 26), APP, PR.att_flame(0, 30, 1.0, 0.0, 1.0, seed=3), w=4, seed=2070)
    return f'<g opacity="{op:.3f}">' + tf(o, x, y, k, wob) + "</g>"


def home_screen(t, icon=None):
    inner = rect(-196, -370, 196, 370, "#9fc2e8")
    for j in range(8):
        c = ["#e2453a", "#3fb26a", "#FFD23F", "#9a6fd1", "#2f8fe0", "#ff8a1f", "#5a5f6e", "#d26fa8"][j]
        inner += shape(lib.rrect(-150 + 100 * (j % 4) - 34, -300 + 110 * (j // 4) - 34, -150 + 100 * (j % 4) + 34, -300 + 110 * (j // 4) + 34, 14),
                       c, "", w=3, seed=2080 + j)
    if icon:
        inner += icon
    return inner


def frame_s03(t):
    """«А раньше скачивал приложение»: полоска загрузки ползёт, на «приложение» иконка выпрыгивает на домашний экран."""
    a, b = T0("s03"), T1("s03")
    tl = W(9) + .3
    u = clamp((t - a) / (tl - a))
    if t < tl:
        inner = rect(-196, -370, 196, 370, "#fbf8f1") + plain("Загрузка", 0, -80, 50, fill="#1d2448", anchor="middle")
        inner += shape(lib.rrect(-150, 0, 150, 40, 20), "#e6e8ee", "", w=3, seed=2090)
        inner += rect(-146, 4, -146 + 292 * u, 36, APP)
        inner += app_icon(0, -220, 1.0)
    else:
        inner = home_screen(t, app_icon(-50, -80, 1.0 * pop(t, tl, .25)))
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552")]
    o.append(hand_phone(PH[0], PH[1], 1.3, inner))
    o.append(PR.sparkles(470, 780, 1.8, bump(t, tl + .1, .05, .5), t, seed=31, n=6, r=200))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tl, 7)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .05 * uu, 0, bg="#3b3552", t=t)


DAYS = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]


def day_row(t, lit, y=900, k=1.0, x0=120, step=140, new_at=None):
    o = []
    for j, d in enumerate(DAYS):
        x = x0 + step * j
        on = j < lit
        o.append(shape(lib.rrect(x - 60, y - 90, x + 60, y + 90, 24), "#fff4dc" if on else "#e3e0da", "", w=4, seed=2100 + j))
        o.append(plain(d, x, y - 40, 40, fill="#1d2448" if on else "#9aa0aa", anchor="middle"))
        if on:
            s = pop(t, new_at[j], .25) if new_at else 1.0
            o.append(PR.att_flame(x, y + 60, 1.4 * s, t, 1.0, seed=j))
        else:
            o.append(blob(ellipse_pts(x, y + 30, 22, 22, 12), "#c9c6bf"))
    return tf("".join(o), 0, 0, k)


def frame_s04(t):
    """«занимался три дня»: ряд дней, три огонька загораются на «три», остальные серые; Дима внизу пожимает плечами."""
    a, b = T0("s04"), T1("s04")
    ts = [a, a + .15, W(11)]
    lit = sum(1 for q in ts if t >= q)
    o = [paper_bg()]
    o.append(day_row(t, lit, 700, new_at=ts))
    if t > W(12):
        o.append(text("3", 540, 520, 200 * pop(t, W(11), .25), fill="#e2453a", stroke="#111", sw=12))
    k = .66
    f = people.dima82(330, 1640 - (people.LEG_LEN - 12) * k - 6, k, "sure82" if t < W(12) else "puzzled82", "d82_shrug", t=t, feet="stand")
    o.append(f["svg"])
    o.append(cat(820, 1640, .8, t, dict(look=(-.6, -.7), smile=.3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(12), 8)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .05 * u, 0, bg=PAPER, t=t)


def frame_s05(t):
    """«а потом удалял от стыда»: палец держит иконку, она дрожит, «Удалить?» и красная кнопка; на «удалял» иконка лопается;
    сбоку Дима закрывает лицо, румянец."""
    a, b = T0("s05"), T1("s05")
    td = W(15) + .1
    wob = 6 * math.sin(t * 40) if t < td else 0
    icon = app_icon(-50, -80, 1.0, wob, op=1 - ramp(t, td, .1))
    inner = home_screen(t, icon)
    if t > a + .2 and t < td + .1:
        inner += shape(lib.rrect(-170, 80, 170, 300, 24), "#ffffff", plain("Удалить?", 0, 150, 46, fill="#1d2448", anchor="middle")
                       + shape(lib.rrect(-120, 190, 120, 270, 30), "#e2453a", text("Удалить", 0, 245, 40, fill="#fff", stroke="#a02a20", sw=3), w=3,
                               seed=2111), w=3, seed=2110)
    if t > td:
        inner += PR.dust_puff(-50, -80, .9, ramp(t, td, .4), seed=4)
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552")]
    o.append(hand_phone(620, 860, 1.25, inner))
    o.append(PR.sparkles(560, 760, 1.6, bump(t, td, .05, .4), t, seed=51, n=6, r=150))
    k = .55
    hip = 1720 - (people.LEG_LEN - 12) * k - 6
    f0 = people.dima82(170, hip, k, "guilty", "d82_rest", t=t, feet="stand")
    hx, hy = f0["head"]
    cover = ramp(t, W(16), .25)
    arms = {"n": ("ik", (hx + 40, hy + 70 - 20 * cover), -1), "f": ("ik", (hx - 20, hy + 80), 1)} if cover > 0 else None
    f = people.dima82(170, hip, k, dict(people.EXPR["dima"]["guilty"], blush=1.0), "d82_rest", t=t, feet="stand", **({"arms": arms} if arms else {}))
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, td, 8)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .05 * u, 0, bg="#3b3552", t=t)


def frame_s06(t):
    """«Вот что я поменял»: Дима поднимает палец, лампочка; кот рядом; надпись сверху."""
    a, b = T0("s06"), T1("s06")
    ti = W(18) + .15
    o = room(t)
    f = stand(400, t, "wow82" if t > ti else "sure82", "d82_one", head_add=.06 * bump(t, ti, .08, .3))
    o.append(f["svg"])
    o.append(cat(820, RFL, .8, t, dict(look=(-.7, -.6), smile=.6)))
    hx, hy = f["head"]
    if t > ti:
        o.append(PR.glow(hx + 170, hy - 200, 220, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx + 170, hy - 200 + 8 * math.sin(t * 5), 1.2 * pop(t, ti, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx + 170, hy - 200, 1.8, bump(t, ti, .05, .5), t, seed=61, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ti, 9)
    return view("".join(o), 540 + dx, 1000 + dy, 1.15 + .05 * u, -1 + 2 * u, t=t)


def timer_screen(t, ts, mins=5):
    left = max(0.0, mins * 60 - max(0.0, t - ts) * 40)
    inner = rect(-196, -370, 196, -250, APP) + plain("Урок", -150, -290, 50, fill="#ffffff") + flag_en(120, -310, .7)
    u = 1 - left / (mins * 60)
    inner += shape(ellipse_pts(0, 20, 150, 150, 40), "#eef0f4", "", w=5, seed=2120)
    if u > 0:
        pts = [(0, 20)] + [(150 * math.sin(2 * math.pi * u * q / 30), 20 - 150 * math.cos(2 * math.pi * u * q / 30)) for q in range(31)]
        inner += blob(pts, "#9fb3ff")
    m, s = int(left // 60), int(left % 60)
    inner += text(f"{m}:{s:02d}", 0, 60, 100, fill="#1d2448", stroke="#ffffff", sw=6)
    inner += plain("минут", 0, 260, 44, fill="#5a5f6e", anchor="middle")
    return inner


def frame_s07(t):
    """«Пять минут сразу после того»: на телефоне урок с таймером «5:00», на «пять» он стартует и бежит."""
    a, b = T0("s07"), T1("s07")
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 700, .3, "#9fb3ff")]
    o.append(hand_phone(PH[0], PH[1], 1.3, timer_screen(t, W(22))))
    if t > W(22):
        o.append(text("5", 860, 500, 220 * pop(t, W(22), .25), fill="#ff8a1f", stroke="#111", sw=12))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(22), 7)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .05 * u, 0, bg="#3b3552", t=t)


BFL = 1560.0


def bathroom(t):
    o = [rect(-1400, -1400, 2600, BFL, "#dfeef0")]
    for i in range(-12, 24):
        o.append(line([(i * 110, -1400), (i * 110, BFL)], 2, "#bcd3d6", taper=0, wmin=1, seed=2130 + i))
    for j in range(-12, 16):
        o.append(line([(-1400, j * 110), (2600, j * 110)], 2, "#bcd3d6", taper=0, wmin=1, seed=2160 + j))
    o.append(rect(-1400, BFL, 2600, BFL + 1400, "#b9c4c9"))
    o.append(line([(-1400, BFL), (2600, BFL)], 5, seed=11))
    o.append(shape(lib.rrect(380, 520, 900, 960, 30), "#cfe3ea", blob(lib.rect_pts(420, 560, 520, 920), "#e8f4f8", .7), w=5, seed=2190))
    o.append(shape(lib.rrect(360, 1080, 920, 1140, 14), "#ffffff", "", w=5, seed=2191))
    o.append(shape([(400, 1140, 1), (880, 1140, 1), (800, 1300, 1), (480, 1300, 1)], "#ffffff", "", w=5, seed=2192))
    o.append(shape(lib.rect_pts(600, 1300, 680, BFL), "#ffffff", "", w=4, seed=2193))
    o.append(shape(lib.rrect(760, 1000, 840, 1080, 10), "#9fc2e8", "", w=4, seed=2194))
    return o


def frame_s08(t):
    """«как почистил зубы»: ванная, Дима у зеркала чистит зубы, кот сидит на раковине."""
    a, b = T0("s08"), T1("s08")
    o = bathroom(t)
    f = stand(300, t, dict(people.EXPR["dima"]["calm82"], look=(.9, -.1)), "d82_rest", fl=BFL, brush=True, head_add=.03 * math.sin(t * 14))
    o.append(f["svg"])
    o.append(cat(870, 1080, .55, t, dict(look=(-.8, -.3), smile=.6, tail=10 * math.sin(t * 3))))
    for j in range(4):
        u = (t * 1.6 + j * .25) % 1
        o.append(blob(ellipse_pts(f["mouth"][0] + 40 + 30 * j, f["mouth"][1] - 40 - 160 * u, 10 + 6 * j, 10 + 6 * j, 12), "#ffffff", .8 * (1 - u)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(29), 6)
    return view("".join(o), 540 + dx, 1000 + dy, 1.12 + .06 * u, 0, bg="#dfeef0", t=t)


def frame_s09(t):
    """«Привязал к тому, что и так делаю»: на раковине стакан со щёткой и телефон с уроком; красная нитка обвивает их на «Привязал»;
    Дима рядом с полотенцем, кивает."""
    a, b = T0("s09"), T1("s09")
    tt = W(30)
    o = bathroom(t)
    o.append(shape([(700, 1080, 1), (780, 1080, 1), (770, 960, 1), (710, 960, 1)], "#9fc2e8", "", w=4, seed=2200))
    o.append(line([(740, 970), (760, 860)], 10, "#e2453a", taper=0, wmin=1, seed=2201))
    o.append(shape(lib.rrect(745, 820, 785, 870, 8), "#ffffff", "", w=3, seed=2202))
    o.append(tf(phone(0, 0, 1.0, streak_screen(61 - 1, t)), 540, 930, .32, -6))
    u = ramp(t, tt, .5)
    if u > 0:
        pts = [(540 + 110 * math.cos(q * 2 * math.pi * 2.2) * (1 if q < .5 else .6) + 200 * q, 950 + 60 * math.sin(q * 2 * math.pi * 2.2))
               for q in [i / 60 for i in range(int(60 * u) + 1)]]
        if len(pts) > 1:
            o.append(line(pts, 7, "#e2453a", taper=.1, wmin=.6, seed=2203))
    o.append(PR.sparkles(640, 930, 1.6, bump(t, tt + .5, .05, .5), t, seed=91, n=6, r=200))
    f = stand(240, t, "proud82", "d82_one", fl=BFL, head_add=.06 * math.sin((t - a) * 6) * ramp(t, W(36), .2))
    o.append(f["svg"])
    o.append(cat(900, 1080, .5, t, dict(look=(-.9, -.2), smile=.8)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tt + .5, 7)
    return view("".join(o), 600 + dx, 960 + dy, 1.35 + .1 * uu, 0, bg="#dfeef0", t=t)


def frame_s10(t):
    return cta_code(t, T0("s10"), T1("s10"))


def frame_s11(t):
    """«чтобы учёба держалась»: ряд дней, огоньки загораются один за другим до конца недели; дальше ещё ряд."""
    a, b = T0("s11"), T1("s11")
    d = (b - a) / 9
    ts = [a - .3 + d * j for j in range(7)]
    lit = sum(1 for q in ts if t >= q)
    o = [paper_bg()]
    o.append(day_row(t, lit, 760, new_at=ts))
    o.append(day_row(t, 7, 1040, new_at=[a - 2] * 7))
    o.append(cat(540, 1500, .9, t, dict(look=(0, -.8), smile=1.0, tail=12 * math.sin(t * 4))))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 980, 1.0 + .05 * u, 0, bg=PAPER, t=t)


def bin_(x, y, k=1.0):
    o = shape([(-110, -200, 1), (110, -200, 1), (90, 0, 1), (-90, 0, 1)], "#7d8597",
              "".join(line([(-60 + 60 * j, -170), (-50 + 50 * j, -30)], 4, "#5a5f6e", seed=2210 + j) for j in range(3)), w=5, seed=2215)
    o += shape(lib.rrect(-130, -230, 130, -195, 10), "#5a5f6e", "", w=4, seed=2216)
    return tf(o, x, y, k)


def frame_s12(t):
    """«а не бросалась»: телефон с уроком летит в мусорку, кот прыгает и ловит его лапами над мусоркой."""
    a, b = T0("s12"), T1("s12")
    tc = W(45) + .2
    o = room(t)
    o.append(bin_(820, RFL))
    fly = clamp((t - a) / (tc - a))
    if t < tc:
        px, py = 200 + 560 * fly, 900 - 300 * math.sin(math.pi * fly * .8)
        rot = 400 * fly
    else:
        px, py, rot = 760, 1060, 10
    j = ease_out(ramp(t, tc - .3, .3))
    cx, cy = 1100 + (760 - 1100) * j, RFL - 500 * math.sin(math.pi * min(1, j) * .5) * (1 if t < tc + .3 else 1)
    o.append(cat(cx, cy + 100, .9, t, dict(look=(-.6, -.6), smile=1.0 if t > tc else .3, legs=0.0, perk=1.0)))
    o.append(tf(phone(0, 0, 1.0, streak_screen(4, t)), px, py, .3, rot))
    o.append(PR.sparkles(760, 1060, 1.6, bump(t, tc, .05, .5), t, seed=121, n=6, r=180))
    f = stand(200, t, "panic82" if t < tc else "laugh82", "d82_shrug")
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tc, 10)
    return view("".join(o), 560 + dx, 1000 + dy, 1.08 + .05 * u, 0, t=t)


def frame_s13(t):
    """«Сегодня шестьдесят дней подряд»: Дима гордо держит телефон экраном к нам, огонёк «60», конфетти; кот рядом; надпись «ДЕНЬ 60»."""
    a, b = T0("s13"), T1("s13")
    t6 = W(47)
    n = 59 if t < t6 else 60
    o = room(t)
    f = stand(330, t, "laugh82" if t > t6 else "proud82", "d82_hold", head_add=.05)
    o.append(f["svg"])
    hx, hy = f["hold"]
    o.append(phone(hx + 170, hy - 160, .55 * (1 + .1 * bump(t, t6, .05, .3)), streak_screen(n, t, glow=bump(t, t6, .05, .6))))
    o.append(cat(860, RFL, .8, t, dict(look=(-.7, -.6), smile=1.0, tail=12 * math.sin(t * 4))))
    o.append(confetti(t, t6))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t6, 10)
    return view("".join(o), 560 + dx, 980 + dy, 1.15 + .06 * u, 1 - 2 * u, t=t)


def frame_s14(t):
    """Петля: кадр хука — экран с огоньком «1»."""
    a, b = T0("s14"), T1("s14")
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 800, .35, "#ffb347")]
    o.append(hand_phone(PH[0], PH[1], 1.3, streak_screen(1, t, glow=.6)))
    return loop_view("".join(o), t, a, b, HIT, 540, 980, 1.0, bg="#3b3552")


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
