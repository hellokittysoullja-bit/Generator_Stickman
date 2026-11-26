"""Рилс 117 «Суд над „потом“», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Место: зал суда — судейская трибуна с котом-судьёй
(мантия, белый парик, молоток), скамья подсудимых с клеткой и словом «ПОТОМ» (глаза, пот), место свидетеля справа;
кухня с раковиной и горой посуды. NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

HIT = 0.38
WOOD, WOOD_D, WOOD_L = "#8a5a3c", "#6b432b", "#a8774a"
BENCH = (660.0, 1060.0)            # верх судейской трибуны (центр)
DOCK = (250.0, 1180.0)             # верх скамьи подсудимых
WIT = (1010.0, 1180.0)              # верх места свидетеля
SKIN = "#ecc4a2"


# ═════════════ персонажи суда ═════════════
def judge(t, bang=None, x=None, y=None, k=.95, st=None, raise_=0.0):
    """Кот-судья: кот + чёрная мантия с белым жабо + белый парик; молоток в правой лапе.
    bang — время удара (молоток падает за 0,1 с и отскакивает), raise_ — молоток поднят (0…1)."""
    x = BENCH[0] if x is None else x
    y = BENCH[1] if y is None else y
    st = dict(dict(look=(0, .1), smile=.3, tail=8 * math.sin(t * 1.7)), **(st or {}))
    o = [cat(x, y, k, t, st)]
    robe = shape([(CT.NECK[0] - 60, CT.NECK[1] - 10, 1), (CT.NECK[0] + 60, CT.NECK[1] - 10, 1), (CT.CX + 150, CT.CBOT, 1), (CT.CX - 150, CT.CBOT, 1)],
                 "#1f1d2b", blob([(CT.CX - 150, CT.CBOT - 40), (CT.CX + 150, CT.CBOT - 40), (CT.CX + 150, CT.CBOT), (CT.CX - 150, CT.CBOT)], "#15131e"),
                 w=5, seed=3000)
    robe += shape([(CT.NECK[0] - 30, CT.NECK[1], 1), (CT.NECK[0] + 30, CT.NECK[1], 1), (CT.NECK[0], CT.NECK[1] + 70, 1)], "#ffffff", "", w=3, seed=3001)
    wig = ""
    for j in range(9):
        a = math.pi * (1.05 + .9 * j / 8)
        cx_, cy_ = CT.CX + 118 * math.cos(a), 1040 + 110 * math.sin(a)
        wig += shape(ellipse_pts(cx_, cy_, 34, 30, 14), "#f4f1ea", "", w=3, seed=3010 + j)
    for s_ in (-1, 1):
        for j in range(3):
            wig += shape(ellipse_pts(CT.CX + s_ * 128, 1060 + 44 * j, 30, 26, 12), "#f4f1ea", "", w=3, seed=3020 + j + (5 if s_ > 0 else 0))
    o.append(f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-CT.CX} {-CT.CBOT})">{robe}{wig}</g>')
    # молоток: ось у правой лапы
    px, py = x + 190 * k, y - 80 * k
    ang = -60 * raise_
    if bang is not None:
        u = t - bang
        if -.25 < u < 0:
            ang = -70 * clamp((u + .25) / .15)
        elif 0 <= u < .5:
            ang = 12 * math.exp(-u * 10) * math.cos(u * 30)
        elif u >= .5:
            ang = 0.0
    g = shape(lib.rrect(-14, -150, 14, 0, 8), WOOD_L, "", w=4, seed=3030)
    g += shape(lib.rrect(-60, -200, 60, -130, 18), WOOD_D, blob(lib.rect_pts(-60, -180, 60, -170), "#c99a6b"), w=4, seed=3031)
    o.append(f'<g transform="translate({px:.1f} {py:.1f}) rotate({ang - 70:.2f}) scale({k:.3f})">{g}</g>')
    o.append(shape(lib.rrect(px + 60 * k, py + 30 * k, px + 200 * k, py + 60 * k, 10), WOOD_D, "", w=4, seed=3032))
    if bang is not None and 0 <= t - bang < .4:
        q = (t - bang) / .4
        o.append(PR.ring_arcs(px + 130 * k, py + 30 * k, 1.0, q, t, seed=3, r=120) if hasattr(PR, "ring_arcs") else "")
        o.append(PR.sparkles(px + 130 * k, py + 20 * k, 1.4, 1 - q, t, seed=4, n=6, r=140))
    return "".join(o)


def later_word(x, y, k, t, scared=0.0, sweat=True, op=1.0, red=True):
    """Слово «ПОТОМ» персонажем: красные буквы, глаза в двух «О», капли пота."""
    sz = 150
    o = text("ПОТОМ", 0, 0, sz, fill="#e2453a" if red else "#7d8597", stroke="#111", sw=10)
    for ex in (-121, 76):
        o += blob(ellipse_pts(ex, -54, 26, 30, 14), "#ffffff")
        o += blob(ellipse_pts(ex + 6 + 6 * math.sin(t * 3), -50 + 4 * scared, 11, 13, 10), "#111")
    if scared > 0:
        o += line([(-150, -120), (-95, -110)], 6, seed=3040) + line([(50, -110), (105, -122)], 6, seed=3041)
    if sweat:
        o += PR.sweat(200, -110 + 20 * ((t * 1.5) % 1), 1.2, 10)
    return f'<g opacity="{op:.3f}" transform="translate({x:.1f} {y:.1f}) rotate({2 * math.sin(t * 5):.2f}) scale({k:.3f})">{o}</g>'


def bars(x0, x1, y0, y1, seed=0):
    o = [line([(x0, y0), (x1, y0)], 10, "#5a5f6e", taper=0, wmin=1, seed=3050 + seed)]
    for j in range(7):
        x = x0 + (x1 - x0) * j / 6
        o.append(line([(x, y0), (x, y1)], 9, "#5a5f6e", taper=0, wmin=1, seed=3051 + j + seed))
    return "".join(o)


def court(t, dock_word=True, scared=0.0, witness="", light=1.0):
    o = [rect(-1400, -1400, 2600, RFL, "#c9a37a")]
    for i in range(-12, 24):
        o.append(rect(i * 140, -1400, i * 140 + 120, RFL, "#bf9670", .7))
        o.append(line([(i * 140, -1400), (i * 140, RFL)], 3, "#8a5a3c", taper=0, wmin=1, seed=3100 + i))
    o.append(rect(-1400, 820, 2600, 860, WOOD_D))
    o.append(rect(-1400, RFL, 2600, RFL + 1400, "#7a4f35"))
    o.append(line([(-1400, RFL), (2600, RFL)], 5, seed=11))
    o.append(PR.scales(660, 620, .55, tilt=.15 * math.sin(t * 2), seed=3))
    # трибуна судьи
    o.append(shape(lib.rect_pts(BENCH[0] - 200, BENCH[1], BENCH[0] + 200, RFL), WOOD, "".join(
        shape(lib.rrect(BENCH[0] - 170 + 120 * j, BENCH[1] + 60, BENCH[0] - 70 + 120 * j, RFL - 60, 10), WOOD_L, "", w=3, seed=3110 + j)
        for j in range(3)), w=5, seed=3115))
    o.append(shape(lib.rrect(BENCH[0] - 230, BENCH[1] - 30, BENCH[0] + 230, BENCH[1] + 10, 8), WOOD_D, "", w=5, seed=3116))
    return o


def dock(t, word=True, scared=0.0, k=.72, extra=""):
    """Скамья подсудимых: «ПОТОМ» за решёткой."""
    x, y = DOCK
    o = []
    if word:
        o.append(later_word(x, y - 40, k, t, scared))
    o.append(extra)
    o.append(bars(x - 160, x + 160, y - 220, y - 20))
    o.append(shape(lib.rect_pts(x - 170, y, x + 170, RFL), WOOD, blob(lib.rect_pts(x - 170, y + 40, x + 170, y + 60), WOOD_D), w=5, seed=3120))
    return "".join(o)


def witness_box(inner=""):
    x, y = WIT
    return inner + shape(lib.rect_pts(x - 130, y, x + 130, RFL), WOOD, blob(lib.rect_pts(x - 130, y + 40, x + 130, y + 60), WOOD_D), w=5, seed=3130)


def eyes(x, y, k=1.0, look=(0, 0), sad=0.0):
    o = ""
    for s_ in (-1, 1):
        o += blob(ellipse_pts(x + s_ * 28 * k, y, 18 * k, 22 * k, 12), "#ffffff") + line(ellipse_pts(x + s_ * 28 * k, y, 18 * k, 22 * k, 12) +
                                                                                        [ellipse_pts(x + s_ * 28 * k, y, 18 * k, 22 * k, 12)[0]], 3 * k, seed=3140)
        o += blob(ellipse_pts(x + s_ * 28 * k + 6 * look[0] * k, y + 6 * look[1] * k, 8 * k, 10 * k, 10), "#111")
    if sad > 0:
        o += line([(x - 50 * k, y - 30 * k), (x - 12 * k, y - 40 * k)], 4 * k, seed=3141) + line([(x + 12 * k, y - 40 * k), (x + 50 * k, y - 30 * k)], 4 * k, seed=3142)
    return o


def dish_pile(x, y, k=1.0, n=9, t=0.0, face=True, flies=True):
    """Гора посуды (x, y — низ): тарелки, кружки; глаза на верхней тарелке; мухи."""
    o = []
    for j in range(n):
        yy = y - 26 * j
        dx = 18 * math.sin(j * 1.7)
        o.append(shape(ellipse_pts(x + dx, yy, 130 - 4 * (j % 3), 22, 22), "#ffffff", blob(ellipse_pts(x + dx, yy, 100, 12, 18), "#dbe8f3"), w=3.6,
                       seed=3150 + j))
        if j % 3 == 1:
            o.append(PR.mug(x + dx + 90, yy - 10, .45, col="red" if j % 2 else "white", seed=j))
    top = y - 26 * n
    if face:
        o.append(eyes(x, top - 10, 1.0, look=(.2, 0), sad=1.0))
    if flies:
        for j in range(3):
            a = t * 4 + j * 2.1
            o.append(blob(ellipse_pts(x + 140 * math.cos(a), top - 80 + 40 * math.sin(a * 1.3), 8, 6, 8), "#111"))
    return tf("".join(o), x * (1 - k), y * (1 - k), k)


def deadline_page(x, y, k, t, burn=0.0):
    """Лист календаря «СРОК» с глазами; burn 0…1 — горит и обугливается."""
    inner = blob(lib.rect_pts(-140, -180, 140, -100), "#c8553d") + text("СРОК", 0, -120, 60, fill="#ffffff", stroke="#7a2a1e", sw=4)
    inner += text("31", 0, 60, 150, fill="#1d2448", stroke="#ffffff", sw=4) + eyes(0, -40, .9, sad=burn)
    col = lib.mix("#fbf8f1", "#3a2f2a", clamp(burn * 1.2))
    o = shape(lib.rect_pts(-140, -180, 140, 180), col, inner if burn < .8 else "", w=4, seed=3160)
    if burn > 0:
        for j in range(5):
            o += PR.att_flame(-110 + 55 * j, 180 - 340 * burn, 2.0 * (1 - .5 * burn) + .4 * math.sin(t * 9 + j), t, 1.0, seed=j)
    return tf(o, x, y, k)


def phone(x, y, k, inner, rot=0.0):
    o = shape(lib.rrect(-120, -220, 120, 220, 30), "#2a2d36", "", w=5, seed=3170)
    o += shape(lib.rrect(-104, -200, 104, 200, 20), "#fbf8f1", inner, w=3, seed=3171)
    return tf(o, x, y, k, rot)


def mom_screen(ring=1.0, t=0.0):
    inner = shape(ellipse_pts(0, -80, 60, 60, 20), "#ffd3c4", PR.heart(0, -80, .5, beat=.5 + .5 * math.sin(t * 8), seed=1), w=3, seed=3180)
    inner += plain("Мама", 0, 40, 46, fill="#1d2448", anchor="middle")
    inner += shape(ellipse_pts(0, 130, 40, 40, 16), "#3fb26a", "", w=3, seed=3181)
    return inner


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: зал суда — «ПОТОМ» дрожит за решёткой, кот-судья в парике бьёт молотком на «подал»."""
    o = court(t)
    o.append(judge(t, bang=HIT))
    o.append(dock(t, scared=bump(t, HIT, .05, .5)))
    o.append(witness_box())
    dx, dy = shake(t, HIT + .02, 14)
    return hook_view("".join(o), t, 0.3, 440, 1060, 1.3, 0, bg="#c9a37a", dx=dx, dy=dy)


def frame_s02(t):
    """«на слово „потом“»: крупно клетка с «ПОТОМ», Дима справа тычет в него пальцем, слово потеет; молоток бьёт на «потом»."""
    a, b = T0("s02"), T1("s02")
    tb = W(6) + .1
    o = court(t)
    o.append(dock(t, scared=.5 + .5 * bump(t, tb, .05, .4), k=.75))
    f = stand(660, t, "squint82", "d82_one", flip=True, head_add=.05, k=.7)
    o.append(f["svg"])
    o.append(judge(t, bang=tb, x=880, y=BENCH[1]))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb + .02, 12)
    return view("".join(o), 450 + dx, 900 + dy, 1.12 + .06 * u, 0, bg="#c9a37a", t=t)


def frame_s03(t):
    """«Первым свидетелем вышла гора посуды»: гора посуды с грустными глазами въезжает в место свидетеля; судья смотрит."""
    a, b = T0("s03"), T1("s03")
    ein = ease_out(ramp(t, a, W(9) + .2 - a))
    o = court(t)
    o.append(judge(t, st=dict(look=(.8, .2))))
    o.append(dock(t, scared=.3))
    o.append(dish_pile(1300 - (1300 - WIT[0]) * ein, WIT[1] + 10, .9, t=t))
    o.append(witness_box())
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(11), 6)
    return view("".join(o), 780 + dx, 1060 + dy, 1.15 + .06 * u, 0, bg="#c9a37a", t=t)


def kitchen(t, mode="day"):
    o = [plain_room(t, wall="#e9f0e6", floor="#b9a58a")]
    o.append(PR.window(250, 900, 300, 380, mode=mode, t=t, seed=5, curtain=False))
    o.append(shape(lib.rect_pts(-200, 1150, 1300, RFL), "#d9cbb4", "".join(
        shape(lib.rrect(-160 + 260 * j, 1210, -10 + 260 * j, RFL - 40, 10), "#e6dac6", "", w=3, seed=3200 + j) for j in range(6)), w=5, seed=3210))
    o.append(shape(lib.rect_pts(-220, 1120, 1320, 1160), "#c9cdd5", "", w=5, seed=3211))
    o.append(shape(lib.rrect(360, 1100, 880, 1180, 20), "#9aa0aa", "", w=5, seed=3212))
    o.append(line([(620, 1110), (620, 940), (700, 940), (700, 990)], 16, "#7d8597", taper=0, wmin=1, seed=3213))
    return o


def frame_s04(t):
    """«Она стоит в раковине с понедельника»: раковина, гора посуды, мухи; листки дней срываются ПН → ПТ."""
    a, b = T0("s04"), T1("s04")
    o = kitchen(t)
    o.append(dish_pile(620, 1110, 1.0, n=12, t=t))
    days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ"]
    n = min(4, int(5 * clamp((t - a) / (W(17) + .3 - a))))
    cal = shape(lib.rect_pts(-110, -130, 110, 130), "#fbf8f1", blob(lib.rect_pts(-110, -130, 110, -60), "#c8553d")
                + text(days[n], 0, 70, 110, fill="#1d2448", stroke="#ffffff", sw=4), w=4, seed=3220)
    o.append(tf(cal, 900, 680, 1.0 + .1 * bump(t, a + (n) * (W(17) + .3 - a) / 5, .04, .2)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(17), 8)
    return view("".join(o), 640 + dx, 960 + dy, 1.2 + .06 * u, 0, t=t)


def frame_s05(t):
    """«Вторым пришёл дедлайн»: лист календаря «СРОК» с глазами шагает в место свидетеля, посуда отодвинута."""
    a, b = T0("s05"), T1("s05")
    ein = ease_out(ramp(t, a, W(20) - a))
    o = court(t)
    o.append(judge(t, st=dict(look=(.8, .2))))
    o.append(dock(t, scared=.5))
    o.append(deadline_page(1300 - (1300 - WIT[0]) * ein, WIT[1] - 110 - 30 * abs(math.sin(t * 9)) * (1 - ein), .9, t))
    o.append(witness_box())
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(20), 6)
    return view("".join(o), 800 + dx, 1040 + dy, 1.2 + .06 * u, 0, bg="#c9a37a", t=t)


def frame_s06(t):
    """«Он сгорел, пока я говорил»: дедлайн крупно вспыхивает на «сгорел» и чернеет."""
    a, b = T0("s06"), T1("s06")
    burn = clamp((t - W(22) + .1) / (b - W(22) + .1))
    o = court(t)
    o.append(witness_box(deadline_page(WIT[0], WIT[1] - 110, .9, t, burn)))
    o.append(PR.glow(WIT[0], WIT[1] - 140, 360, .5 * burn, "#ff8a3a"))
    o.append(PR.smoke_curls(WIT[0], WIT[1] - 320, 1.4, burn, t, seed=2))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(22), 10)
    return view("".join(o), WIT[0] - 60 + dx, 1050 + dy, 1.7 + .1 * u, 0, bg="#c9a37a", t=t)


def frame_s07(t):
    """«„потом сделаю“»: воспоминание — Дима на диване с телефоном, пузырь «потом сделаю», на столике кучка пепла от «СРОК»."""
    a, b = T0("s07"), T1("s07")
    o = [plain_room(t, wall="#e7dccb")]
    o.append(shape(lib.rrect(120, 1200, 900, 1420, 40), "#7d6aa8", "", w=5, seed=3230))
    o.append(shape(lib.rrect(100, 1050, 920, 1240, 40), "#6b5a96", "", w=5, seed=3231))
    k = .7
    hip = 1220
    f = people.dima82(420, hip, k, dict(people.EXPR["dima"]["calm82"], look=(.2, .6)), "d82_hold", t=t,
                      feet=people.sit_kw(420, hip, k)["feet"], lean_add=-.2)
    o.append(f["svg"])
    hx, hy = f["hold"]
    o.append(tf(shape(lib.rrect(-40, -70, 40, 70, 12), "#2a2d36", "", w=3, seed=3232), hx + 10, hy - 30, 1.0, 10))
    bu = pop(t, W(26) - .1, .25)
    if t > W(26) - .1:
        o.append(PR.speech_bubble(f["head"][0] + 260, f["head"][1] - 220, 460, 200, bu, seed=3, tail=(-120, 60)))
        if bu > .8:
            o.append(plain("потом сделаю", f["head"][0] + 260, f["head"][1] - 205, 52, fill="#1d2448", anchor="middle"))
    o.append(shape(lib.rect_pts(860, 1290, 1060, 1310), WOOD, "", w=4, seed=3233))
    o.append(blob(ellipse_pts(960, 1280, 70, 22, 14), "#3a2f2a"))
    o.append(PR.smoke_curls(960, 1250, 1.0, 1.0, t, seed=3))
    o.append(rect(-1400, -1400, 2600, 2900, "#5a4a6a", .18))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(27), 6)
    return view("".join(o), 560 + dx, 1050 + dy, 1.15 + .05 * u, 0, t=t)


def frame_s08(t):
    """«А третьей позвонила мама»: в месте свидетеля звонит телефон «Мама», дрожит; судья поворачивает голову."""
    a, b = T0("s08"), T1("s08")
    ring = 1.0 if t > W(30) - .1 else 0.0
    o = court(t)
    o.append(judge(t, st=dict(look=(.9, .1), perk=ring)))
    o.append(dock(t, scared=.6))
    sh = 8 * math.sin(t * 60) * ring
    o.append(witness_box(phone(WIT[0] + sh, WIT[1] - 150, 1.0 * pop(t, a, .25), mom_screen(ring, t), rot=sh * .5)))
    if ring:
        o.append(PR.ring_arcs(WIT[0], WIT[1] - 150, 1.0, (t * 2) % 1, t, seed=5, r=200) if hasattr(PR, "ring_arcs") else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(31), 6)
    return view("".join(o), 800 + dx, 1050 + dy, 1.2 + .06 * u, 0, bg="#c9a37a", t=t)


def frame_s09(t):
    """«Ей я тоже обещал перезвонить потом»: Дима виновато держит телефон, на экране «Мама — 5 пропущенных», счётчик растёт."""
    a, b = T0("s09"), T1("s09")
    n = 1 + int(4 * clamp((t - a) / (W(36) - a)))
    o = [plain_room(t)]
    o.append(rug(540, RFL + 150, 600))
    f = stand(330, t, dict(people.EXPR["dima"]["guilty"], blush=.8), "d82_hold", head_add=.1)
    o.append(f["svg"])
    inner = plain("Пропущенные", 0, -140, 34, fill="#e2453a", anchor="middle")
    for j in range(min(n, 4)):
        inner += plain("Мама", -70, -70 + 60 * j, 36, fill="#1d2448") + plain("✕" if False else "", 60, -70 + 60 * j, 30)
    hx, hy = f["hold"]
    o.append(phone(hx + 200, hy - 260, 1.25, inner, rot=4))
    o.append(text(f"×{n}", 860, 1240, 170 * (1 + .25 * bump(t, a + (n - 1) * (W(36) - a) / 4, .04, .2)), fill="#e2453a", stroke="#111", sw=12))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(36), 8)
    return view("".join(o), 560 + dx, 1000 + dy, 1.12 + .06 * u, 0, t=t)


def frame_s10(t):
    """«Судья кот выслушал всех»: кот-судья крупно кивает, перед трибуной в ряд свидетели — посуда, обугленный срок, телефон мамы."""
    a, b = T0("s10"), T1("s10")
    nod = 4 * math.sin((t - a) * 8) * ramp(t, W(40), .2)
    o = court(t)
    o.append(judge(t, st=dict(look=(0, .4), tilt=nod, smile=.2)))
    o.append(dish_pile(200, RFL, .8, n=8, t=t, flies=False))
    o.append(deadline_page(420, RFL - 150, .6, t, .6))
    o.append(phone(940, RFL - 170, .75, mom_screen(1.0, t)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1120, 1.0 + .08 * u, 0, bg="#c9a37a", t=t)


def frame_s11(t):
    """«и стукнул молотком»: молоток крупно падает на подставку на «молотком», волна, всё вздрагивает."""
    a, b = T0("s11"), T1("s11")
    tb = W(44)
    o = court(t)
    o.append(judge(t, bang=tb, st=dict(look=(.6, .4), smile=.5)))
    o.append(PR.flash_screen(.3 * bump(t, tb, .03, .15)) if hasattr(PR, "flash_screen") else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb + .02, 18)
    return view("".join(o), 760 + dx, 960 + dy, 1.7 + .1 * u, 0, bg="#c9a37a", t=t)


def scroll(x, y, k, u, lines_, cross=0.0, t=0.0):
    """Свиток: раскрывается вниз (u), строки."""
    h = 600 * clamp(u)
    o = shape(lib.rect_pts(-300, 0, 300, h), "#f6e7c4", "", w=4, seed=3240)
    o += shape(lib.rrect(-330, -30, 330, 20, 20), "#d9b98a", "", w=4, seed=3241)
    o += shape(lib.rrect(-330, h - 20, 330, h + 30, 20), "#d9b98a", "", w=4, seed=3242)
    c = lib.clip_rect(-300, 0, 600, h)
    inner = text("ПРИГОВОР", 0, 110, 80, fill="#7a2a1e", stroke="#f6e7c4", sw=2)
    for j, s_ in enumerate(lines_):
        inner += plain(s_, 0, 230 + 100 * j, 64, fill="#1d2448", anchor="middle")
    if cross > 0:
        inner += PR.cross_stroke((-160, 180), (160, 260), (160, 180), (-160, 260), u=cross, w=20, seed=3243)
    o += f'<g clip-path="url(#{c})">{inner}</g>'
    return tf(o, x, y, k)


def frame_s12(t):
    """«Приговор: каждое „потом“ заменить»: перед трибуной раскрывается свиток «ПРИГОВОР», строка «потом» перечёркивается."""
    a, b = T0("s12"), T1("s12")
    o = court(t)
    o.append(judge(t, st=dict(look=(0, .5), smile=.4)))
    o.append(scroll(560, 1000, 1.0, ease_out(ramp(t, W(45) - .05, .4)), ["потом", "→ 2 минуты"], cross=ramp(t, W(47) + .1, .25), t=t))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(47) + .3, 8)
    return view("".join(o), 540 + dx, 1180 + dy, 1.05 + .06 * u, 0, bg="#c9a37a", t=t)


def timer(x, y, k, left, label="СЕЙЧАС"):
    m, s = int(left // 60), int(left % 60)
    o = shape(ellipse_pts(0, 0, 220, 220, 40), "#ffffff", "", w=6, seed=3250)
    u = 1 - left / 120
    if u > 0:
        pts = [(0, 0)] + [(200 * math.sin(2 * math.pi * u * q / 30), -200 * math.cos(2 * math.pi * u * q / 30)) for q in range(31)]
        o += blob(pts, "#9fe0a4")
    o += text(f"{m}:{s:02d}", 0, 40, 130, fill="#1d2448", stroke="#ffffff", sw=8)
    o += text(label, 0, 330, 90, fill="#3fb26a", stroke="#111", sw=8)
    return tf(o, x, y, k)


def frame_s13(t):
    """«на две минуты сейчас»: слово «ПОТОМ» сжимается и превращается в таймер «2:00» с подписью «СЕЙЧАС»."""
    a, b = T0("s13"), T1("s13")
    m = ease_io(ramp(t, a, W(51) - a))
    o = court(t)
    o.append(judge(t, st=dict(look=(-.3, .5), smile=.8)))
    if m < .5:
        o.append(later_word(540, 1180, .9 * (1 - m), t, scared=1.0, op=1 - 2 * m))
    o.append(f'<g opacity="{clamp(m * 2 - .6):.3f}">' + timer(540, 1150, .8 * (.6 + .4 * m), 120) + "</g>")
    o.append(PR.sparkles(540, 1150, 2.0, bump(t, W(52), .05, .5), t, seed=131, n=7, r=280))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(52), 8)
    return view("".join(o), 540 + dx, 1150 + dy, 1.05 + .06 * u, 0, bg="#c9a37a", t=t)


def frame_s14(t):
    return cta_code(t, T0("s14"), T1("s14"))


def frame_s15(t):
    """«чтобы твоё „потом“»: крупно клетка с «ПОТОМ», за ней кот-судья поднимает молоток."""
    a, b = T0("s15"), T1("s15")
    o = court(t)
    o.append(judge(t, raise_=ease_out(ramp(t, a, .5)), x=600, st=dict(look=(-.6, .4))))
    o.append(dock(t, scared=1.0, k=.75))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 400, 1080, 1.3 + .08 * u, 0, bg="#c9a37a", t=t)


def frame_s16(t):
    """«тоже получило приговор»: удар молотка, на «ПОТОМ» шлёпается красный штамп «ВИНОВНО»."""
    a, b = T0("s16"), T1("s16")
    tb = W(61)
    o = court(t)
    o.append(judge(t, bang=tb, x=600, st=dict(look=(-.6, .4), smile=.6)))
    st = ""
    if t > tb:
        s = 1.0 + 1.4 * (1 - ease_out(clamp((t - tb) / .25)))
        st = (f'<g transform="translate({DOCK[0]} {DOCK[1] - 60}) rotate(-14) scale({s:.3f})"><rect x="-210" y="-60" width="420" height="120" rx="14" '
              f'fill="none" stroke="#d8352a" stroke-width="12"/>' + text("ВИНОВНО", 0, 34, 84, fill="#d8352a", stroke="#d8352a", sw=.01) + "</g>")
    o.append(dock(t, scared=1.0, k=.75, extra=st))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb + .02, 16)
    return view("".join(o), 400 + dx, 1080 + dy, 1.3 + .08 * u, 0, bg="#c9a37a", t=t)


def frame_s17(t):
    """«Я открыл кран»: кухня, Дима поворачивает кран, льётся вода; таймер 2:00 рядом стартует."""
    a, b = T0("s17"), T1("s17")
    on = ramp(t, W(63), .2)
    o = kitchen(t)
    o.append(dish_pile(620, 1110, 1.0, n=12, t=t))
    if on > 0:
        o.append(line([(700, 995), (700, 995 + 160 * on)], 22, "#7fc8f0", taper=0, wmin=1, seed=3260, op=.85))
    f = stand(220, t, "proud82", "d82_rest", arms={"n": ("ik", (690, 960), -1)})
    o.append(f["svg"])
    o.append(timer(920, 700, .5, 120 - 60 * clamp(t - W(64))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(64), 6)
    return view("".join(o), 560 + dx, 980 + dy, 1.15 + .06 * u, 0, t=t)


def frame_s18(t):
    """«через две минуты посуды стало вдвое меньше»: таймер бежит к 0:00, гора тает вдвое, рядом растёт чистая стопка; «ВДВОЕ МЕНЬШЕ»."""
    a, b = T0("s18"), T1("s18")
    u = clamp((t - a) / (W(72) - a))
    o = kitchen(t)
    o.append(dish_pile(560, 1110, 1.0, n=12 - int(6 * u), t=t, face=True, flies=u < .5))
    o.append(line([(700, 995), (700, 1110)], 22, "#7fc8f0", taper=0, wmin=1, seed=3260, op=.85))
    for j in range(int(6 * u)):
        o.append(shape(ellipse_pts(1000, 1110 - 22 * j, 110, 18, 20), "#ffffff", blob(ellipse_pts(1000, 1110 - 22 * j, 80, 9, 14), "#dbe8f3"), w=3,
                       seed=3270 + j))
    o.append(timer(920, 650, .5, 120 * (1 - u)))
    o.append(PR.sparkles(1000, 1000, 1.6, bump(t, W(72), .05, .5), t, seed=181, n=6, r=180))
    f = stand(200, t, "laugh82" if u > .9 else "proud82", "d82_rest", arms={"n": ("ik", (480 + 30 * math.sin(t * 12), 1080), -1)})
    o.append(f["svg"])
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(72), 8)
    return view("".join(o), 600 + dx, 980 + dy, 1.12 + .06 * uu, 0, t=t)


def folder(x, y, k, close, stamp_t=None, t=0.0):
    """Папка «ДЕЛО»: створка закрывается (close 0…1), штамп «ЗАКРЫТО»."""
    o = shape(lib.rect_pts(-260, -180, 260, 180), "#e3c79a", plain("ДЕЛО №1", 0, -60, 60, fill="#5a3a20", anchor="middle")
              + plain("«потом»", 0, 30, 56, fill="#5a3a20", anchor="middle"), w=5, seed=3280)
    sx = 1 - 2 * clamp(close)
    if close < 1:
        o += f'<g transform="translate(-260 0) scale({sx:.3f} 1) translate(260 0)">' + shape(lib.rect_pts(-260, -180, 260, 180), "#d9b98a", "", w=5,
                                                                                         seed=3281) + "</g>"
    if stamp_t is not None and t > stamp_t:
        s = 1.0 + 1.4 * (1 - ease_out(clamp((t - stamp_t) / .25)))
        o += (f'<g transform="rotate(-12) scale({s:.3f})"><rect x="-230" y="-60" width="460" height="120" rx="14" fill="none" stroke="#d8352a" '
              f'stroke-width="12"/>' + text("ЗАКРЫТО", 0, 34, 84, fill="#d8352a", stroke="#d8352a", sw=.01) + "</g>")
    return tf(o, x, y, k)


def frame_s19(t):
    """«Дело закрыто»: на трибуне папка «ДЕЛО №1 „потом“» захлопывается, кот-судья бьёт молотком, штамп «ЗАКРЫТО»."""
    a, b = T0("s19"), T1("s19")
    tb = W(74) + .05
    o = court(t)
    o.append(judge(t, bang=tb, x=800, st=dict(look=(-.7, .5), smile=1.0)))
    o.append(folder(420, 980, .9, ease_in2(ramp(t, a, tb - a)), tb, t))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb + .02, 14)
    return view("".join(o), 560 + dx, 1000 + dy, 1.15 + .06 * u, 0, bg="#c9a37a", t=t)


def ease_in2(u):
    return u * u


def frame_s20(t):
    """«И посуда тоже»: кухонный шкаф, чистая стопка тарелок внутри, дверца закрывается, искры; кот сидит на столешнице."""
    a, b = T0("s20"), T1("s20")
    tc = W(76) + .1
    o = kitchen(t)
    o.append(shape(lib.rect_pts(560, 520, 1000, 900), "#e6dac6", "".join(
        shape(ellipse_pts(780, 860 - 24 * j, 150, 22, 20), "#ffffff", blob(ellipse_pts(780, 860 - 24 * j, 110, 10, 14), "#dbe8f3"), w=3, seed=3290 + j)
        for j in range(8)), w=5, seed=3299))
    cl = ease_out(ramp(t, tc - .25, .3))
    o.append(f'<g transform="translate(1000 0) scale({max(.02, cl):.3f} 1) translate(-1000 0)">' + shape(lib.rect_pts(560, 520, 1000, 900), "#d9cbb4",
                                                                                                        shape(ellipse_pts(600, 710, 14, 14, 10), WOOD_D, "", w=3, seed=3300), w=5, seed=3301) + "</g>")
    o.append(PR.sparkles(780, 700, 1.8, bump(t, tc, .05, .5), t, seed=201, n=7, r=260))
    o.append(cat(300, 1120, .7, t, dict(look=(.8, -.5), smile=1.0, tail=12 * math.sin(t * 4))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tc, 8)
    return view("".join(o), 640 + dx, 900 + dy, 1.2 + .06 * u, 0, t=t)


def frame_s21(t):
    """Петля: кадр хука — зал суда, «ПОТОМ» за решёткой, молоток поднят."""
    a, b = T0("s21"), T1("s21")
    o = court(t)
    o.append(judge(t, raise_=ramp(t, a, b - a)))
    o.append(dock(t, scared=.3))
    o.append(witness_box())
    return loop_view("".join(o), t, a, b, 0.3, 440, 1060, 1.3, bg="#c9a37a")


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
