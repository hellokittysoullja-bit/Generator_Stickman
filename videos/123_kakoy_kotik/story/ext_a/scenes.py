"""Рилс 123 «Какой ты котик?», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Игра-тест: наш кот в четырёх образах, у каждого номер и подпись:
1 Спящий (колпак для сна), 2 Суетливый (тряпка), 3 Ждун (календарь «ПН 9:00»), 4 Перфекционист (линейка и лупа).
Призыв — номер котика в комментариях (поле комментария с цифрой). Говорит Дима (в конце «я второй» — Дима крупно).
NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

HIT = stress(2, .3)
NAMES = {1: "СПЯЩИЙ", 2: "СУЕТЛИВЫЙ", 3: "ЖДУН", 4: "ПЕРФЕКЦИОНИСТ"}
KIND = {1: "sleep", 2: "fuss", 3: "wait", 4: "perfect"}
BADGE = {1: "#2f8fe0", 2: "#e2453a", 3: "#3fb26a", 4: "#8a63d2"}


def lw(lx, ly, x, y, k):
    return x + (lx - CT.CX) * k, y + (ly - CT.CBOT) * k


def nightcap(x, y, k, sl=0.0, t=0.0):
    """Колпак для сна поверх головы (в системе головы кота: та же поправка на сон, что у cat.draw)."""
    sw = 4 * math.sin(t * 2)
    g = (f'<path d="M752 990 Q760 930 830 925 Q900 925 918 985 Z" fill="#5f7fd9" stroke="#111" stroke-width="6" stroke-linejoin="round"/>'
         f'<path d="M770 945 Q860 860 {990 + sw:.1f} 880 Q930 930 905 960" fill="#5f7fd9" stroke="#111" stroke-width="6" stroke-linejoin="round"/>'
         f'<path d="M792 940 Q850 905 880 925 M830 905 Q880 890 905 905" fill="none" stroke="#ffffff" stroke-width="6" opacity=".7"/>'
         f'<path d="M745 992 Q835 1012 925 990 L922 970 Q835 990 748 972 Z" fill="#ffffff" stroke="#111" stroke-width="5"/>'
         f'<circle cx="{995 + sw:.1f}" cy="884" r="22" fill="#ffffff" stroke="#111" stroke-width="5"/>')
    head = f'<g transform="translate({22 * sl:.2f} {34 * sl:.2f}) rotate({16 * sl:.2f} {CT.NECK[0]} {CT.NECK[1]})">{g}</g>'
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-CT.CX} {-CT.CBOT})">{head}</g>'


def rag(x, y, k, t, rub=0.0):
    w = 8 * math.sin(t * 20) * rub
    pts = [(x - 46 * k + w, y - 30 * k), (x + 40 * k + w, y - 40 * k), (x + 52 * k, y + 20 * k), (x + 10 * k, y + 50 * k), (x - 50 * k, y + 30 * k)]
    inner = "".join(line([(x - 60 * k, y - 40 * k + 22 * k * i), (x + 60 * k, y - 40 * k + 22 * k * i)], 6 * k, "#ffffff", taper=0, wmin=1, seed=7000 + i,
                         op=.6) for i in range(5))
    return shape(pts, "#4fa8e8", inner, w=4 * k / .9, seed=7010)


def mini_cal(x, y, k, rot=0.0):
    o = shape(lib.rect_pts(-90, -100, 90, 100), "#fbf8f1", blob(lib.rect_pts(-90, -100, 90, -40), "#c8553d"), w=5, seed=7020)
    o += text("ПН", 0, -55, 46, fill="#ffffff", stroke="#7a2a1e", sw=4)
    o += text("9:00", 0, 50, 62, fill="#1d2448", stroke="#fbf8f1", sw=2)
    return tf(o, x, y, k, rot)


def ruler(x, y, k, rot=0.0):
    o = shape(lib.rect_pts(-130, -16, 130, 16), "#ffd35a", "".join(line([(-120 + 20 * i, -16), (-120 + 20 * i, -4 if i % 2 else 4)], 3, seed=7030 + i)
                                                                   for i in range(13)), w=4, seed=7029)
    return tf(o, x, y, k, rot)


def loupe(x, y, k, rot=0.0):
    o = line([(40, 40), (110, 110)], 22, "#7a5232", taper=0, wmin=1, seed=7040)
    o += f'<circle r="58" fill="#cfe8ff" fill-opacity=".55" stroke="#111" stroke-width="12"/><path d="M-30 -24 Q-14 -40 8 -40" stroke="#fff" stroke-width="8" fill="none"/>'
    return tf(o, x, y, k, rot)


def kitty(n, x, y, k, t, st=None, act=0.0):
    """Котик-образ n (1–4). act — сила действия (трёт, машет)."""
    kind = KIND[n]
    st = dict(st or {})
    st.setdefault("tail", 10 * math.sin(t * 2.5 + n))
    o = []
    if kind == "sleep":
        st.setdefault("sleep", 0.0)
        st.setdefault("smile", .4)
        st.setdefault("blink", .85 if st["sleep"] < .5 else 1.0)
    if kind == "fuss":
        st.setdefault("paw", .75)
        st.setdefault("smile", .7)
        st.setdefault("look", (.4, -.3))
    if kind == "perfect":
        st.setdefault("paw", .6)
        st.setdefault("paw_l", .6)
        st.setdefault("look", (.5, .5))
    if kind == "wait":
        st.setdefault("look", (0, .1))
        st.setdefault("smile", .2)
    o.append(cat(x, y, k, t, st))
    if kind == "sleep":
        o.append(nightcap(x, y, k, st["sleep"], t))
    if kind == "fuss":
        p = st["paw"]
        tip = lw(906 + 70 * p * 1.6, 1306 - 150 * p, x, y, k)
        o.append(rag(tip[0] + 8 * k + 20 * k * math.sin(t * 14) * act, tip[1] - 20 * k, k * 1.1, t, act))
    if kind == "wait":
        o.append(mini_cal(*lw(836, 1222, x, y, k), k * .95, -4 + 3 * math.sin(t * 3)))
    if kind == "perfect":
        tl = lw(766 - 70 * .6 * 1.6, 1306 - 150 * .6, x, y, k)
        tr = lw(906 + 70 * .6 * 1.6, 1306 - 150 * .6, x, y, k)
        o.append(ruler(tl[0], tl[1] - 10 * k, k * .8, -70))
        o.append(loupe(tr[0] + 10 * k, tr[1] - 40 * k, k * .9, 10 * math.sin(t * 2)))
    return "".join(o)


def badge(n, x, y, k=1.0):
    o = shape(ellipse_pts(0, 0, 70, 70, 20), BADGE[n], "", w=6, seed=7100 + n) + text(str(n), 0, 34, 100, fill="#ffffff", stroke="#111", sw=8)
    return tf(o, x, y, k)


def nameplate(n, x, y, k=1.0, u=1.0):
    s = NAMES[n]
    w = 70 + 46 * len(s)
    o = shape(lib.rrect(-w / 2, -55, w / 2, 55, 22), "#FFD23F", "", w=6, seed=7200 + n) + text(s, 0, 25, 76, fill="#111", stroke="#FFD23F", sw=1)
    return tf(o, x, y, k * u)


def stage_bg(col="#f3e7c4"):
    o = [rect(-1400, -1400, 2600, RFL, col)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, RFL, lib.mul(col, (.96, .95, .93)), .55))
    o.append(rect(-1400, RFL, 2600, RFL + 1400, FLOOR_C))
    o.append(line([(-1400, RFL), (2600, RFL)], 5, seed=11))
    return "".join(o)


ROW_X = [150, 390, 630, 870]


def row(t, k=.55, t_in=None, hop_n=None, hop_t=None, spot=None, q=False):
    """Четыре котика в ряд на полу с номерами над головой."""
    o = []
    for i, n in enumerate((1, 2, 3, 4)):
        u = 1.0 if t_in is None else pop(t, t_in[i], .28)
        if u <= 0.01:
            continue
        hop = 0.0
        if hop_n == n and hop_t is not None:
            hop = 160 * bump(t, hop_t, .12, .25)
        elif hop_n == "all":
            hop = 80 * abs(math.sin(t * 6 + i))
        x = ROW_X[i]
        g = kitty(n, x, RFL - hop, k, t, act=1.0)
        o.append(f'<g transform="translate({x:.1f} {RFL:.1f}) scale({u:.4f}) translate({-x:.1f} {-RFL:.1f})">{g}</g>')
        o.append(badge(n, x, RFL - 330 * k / .55 - hop - 30, .7 * u))
        if q:
            o.append(text("?", x + 70, RFL - 360 * k / .55 - 10, 80 * u, fill="#e2453a", stroke="#111", sw=6))
    if spot is not None:
        x = ROW_X[spot]
        o.insert(0, PR.glow(x, RFL - 160, 230, .8, "#fff1b0"))
    return "".join(o)


GRID = [(290, 935), (790, 935), (290, 1330), (790, 1330)]


def grid(t, k=1.05, t_in=None, hop_n=None, hop_t=None, spot=None, q=False, dy=0.0):
    """Четыре котика сеткой 2×2 (экранные координаты при камере 1:1), номер слева сверху у каждого."""
    o = []
    for i, n in enumerate((1, 2, 3, 4)):
        x, y = GRID[i]
        y += dy
        u = 1.0 if t_in is None else pop(t, t_in[i], .28)
        if u <= 0.01:
            continue
        hop = 0.0
        if hop_n == n and hop_t is not None:
            hop = 150 * bump(t, hop_t, .12, .25)
        if spot == i:
            o.append(PR.glow(x, y - 140, 220, .9, "#fff1b0"))
        o.append(blob(ellipse_pts(x, y, 150 * k, 20, 16), "#000000", .12))
        g = kitty(n, x, y - hop, k, t, act=1.0)
        o.append(f'<g transform="translate({x:.1f} {y:.1f}) scale({u:.4f}) translate({-x:.1f} {-y:.1f})">{g}</g>')
        o.append(badge(n, x - 130 * k, y - 330 * k - hop, .75 * u))
        if q:
            o.append(text("?", x + 170 * k, y - 300 * k, 90 * u, fill="#e2453a", stroke="#111", sw=6))
    return "".join(o)


# ═══════════ ХУК ═══════════
def frame_s01(t):
    """ХУК: четыре котика выпрыгивают в ряд один за другим, у каждого номер и вопрос."""
    o = [paper_bg()]
    o.append(grid(t, t_in=[-.3, -.1, .2, .5], q=True))
    dx, dy = shake(t, W(2), 9)
    return hook_view("".join(o), t, HIT, 540, 960, 1.0, 0, bg=PAPER, dx=dx, dy=dy)


def frame_s02(t):
    """«когда откладываешь дела»: прожектор бежит по котикам, тот, на ком свет, подпрыгивает."""
    a, b = T0("s02"), T1("s02")
    i = min(3, int(clamp((t - a) / (b - a)) * 4))
    o = [paper_bg()]
    o.append(grid(t, spot=i, hop_n=i + 1, hop_t=a + (b - a) * i / 4, q=True))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 960, 1.0 + .06 * u, 0, bg=PAPER, t=t)


def intro(n, t, a, b, tw):
    """План-знакомство: котик n крупно, номер, табличка с именем на слове tw."""
    o = [stage_bg(("#e8eefc", "#fde6e0", "#e3f5e0", "#efe6fb")[n - 1])]
    o.append(PR.glow(540, RFL - 400, 500, .5, "#fff6d0"))
    st = {"sleep": .0, "blink": .9} if n == 1 else {}
    o.append(kitty(n, 540, RFL, 1.5, t, st, act=1.0))
    o.append(badge(n, 140, 520, 1.1 * pop(t, a, .25)))
    if t > tw - .05:
        o.append(nameplate(n, 600, 700, .85 if n == 4 else 1.0, pop(t, tw - .05, .25)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tw, 9)
    return view("".join(o), 540 + dx, 1100 + dy, 1.0 + .08 * u, 0, t=t)


def frame_s03(t):
    return intro(1, t, T0("s03"), T1("s03"), W(7))


def folder(x, y, k, rot=0.0, web=0.0, t=0.0):
    o = shape(lib.rrect(-150, -110, 150, 110, 14), "#f2b541", blob(lib.rect_pts(-150, -110, 150, -50), "#e09a20", .7), w=5, seed=7300)
    o += shape(lib.rrect(-150, -134, -40, -104, 8), "#f2b541", "", w=5, seed=7301)
    o += text("ДЕЛО", 0, 40, 72, fill="#1d2448", stroke="#f2b541", sw=2)
    g = tf(o, x, y, k, rot)
    if web > 0:
        g += PR.cobweb(x - 150 * k, y - 110 * k, 1.4 * k * web, t=t, ang=45, seed=2)
    return g


def frame_s04(t):
    """«Дело ждёт»: папка «ДЕЛО» на столе нетерпеливо подпрыгивает, рядом часы тикают."""
    a, b = T0("s04"), T1("s04")
    o = desk_room(t, mode="day", window=True)
    hop = abs(math.sin((t - a) * 9)) * 30
    o.append(folder(680, DESK_Y - 110 - hop, 1.0, 4 * math.sin(t * 9)))
    o.append(PR.clock(900, 560, 90, angle_h=60, angle_m=(t * 720) % 360))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 700, 820, 1.35 + .06 * u, 0, t=t)


def frame_s05(t):
    """«а он ждёт, когда проснётся желание»: Спящий спит на подушке, Z; облачко сна — спящая лампочка-желание."""
    a, b = T0("s05"), T1("s05")
    o = [plain_room(t, wall="#2e3150", floor="#3b3552")]
    o.append(PR.window(880, 1100, 300, 380, mode="night", t=t, seed=4, curtain=False))
    o.append(PR.pillow(560, RFL - 40, 2.8))
    o.append(kitty(1, 540, RFL - 90, 1.2, t, {"sleep": 1.0}))
    for j in range(3):
        ph = ((t - a) * .8 + j / 3) % 1
        o.append(PR.z_mark(700 + 80 * ph + 40 * j, 980 - 280 * ph, 1.2 + .8 * ph, u=1 - ph))
    inner = PR.idea_bulb(0, 0, 1.4, on=.15, t=t) + PR.z_mark(70, -60, 1.0)
    o.append(PR.thought_cloud(300, 640, 1.2, w=300, h=230, u=pop(t, W(13), .3), seed=5, inner=inner))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(15), 6)
    return view("".join(o), 540 + dx, 1000 + dy, 1.05 + .08 * u, 0, bg="#2e3150", t=t)


def frame_s06(t):
    return intro(2, t, T0("s06"), T1("s06"), W(17))


def frame_s07(t):
    """«Моет кружки»: Суетливый яростно трёт кружку тряпкой, пена, стопка чистых кружек."""
    a, b = T0("s07"), T1("s07")
    o = [plain_room(t, wall="#dfeef0", floor="#b9c4c9")]
    o.append(shape(lib.rect_pts(-200, RFL - 300, 1300, RFL), "#e9edf2", "", w=5, seed=7400))
    o.append(kitty(2, 440, RFL - 300, 1.15, t, {"look": (.6, .4)}, act=1.0))
    p = .75
    tip = lw(906 + 70 * p * 1.6, 1306 - 150 * p, 440, RFL - 300, 1.15)
    o.append(PR.mug(tip[0] + 40 + 10 * math.sin(t * 25), tip[1] + 60, 1.6, rot=8 * math.sin(t * 13), coffee=False))
    for j in range(6):
        ph = (t * 1.6 + j / 6) % 1
        o.append(shape(ellipse_pts(tip[0] + 40 + 70 * math.sin(j * 2.1), tip[1] - 160 * ph, 16 * (1 - ph) + 5, 16 * (1 - ph) + 5, 10), "#ffffff", "", w=2,
                       seed=7410 + j))
    for i in range(3):
        o.append(PR.mug(880, RFL - 300 - 95 * i - 2, 1.2, coffee=False))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(19), 6)
    return view("".join(o), 600 + dx, 1050 + dy, 1.15 + .06 * u, 0, bg="#dfeef0", t=t)


def frame_s08(t):
    """«разбирает полку»: Суетливый у полки, книги вылетают и кружатся."""
    a, b = T0("s08"), T1("s08")
    o = room(t)
    o.append(PR.bookshelf(760, RFL, 420, 700, seed=3))
    o.append(kitty(2, 380, RFL, 1.1, t, {"look": (.8, -.4)}, act=1.0))
    cols = ["#e2453a", "#2f8fe0", "#3fb26a", "#ffd23f"]
    for j in range(4):
        ph = ((t - a) * 1.3 + j / 4) % 1
        bx, by = 700 - 520 * ph, 900 - 380 * math.sin(math.pi * ph)
        bk = shape(lib.rect_pts(-34, -50, 34, 50), cols[j], line([(-20, -30), (20, -30)], 4, "#ffffff", taper=0, wmin=1, seed=7500 + j), w=4,
                   seed=7510 + j)
        o.append(tf(bk, bx, by, 1.0, 360 * ph + 90 * j))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(21), 8)
    return view("".join(o), 560 + dx, 1100 + dy, 1.1 + .05 * u, 0, t=t)


def room(t):
    return [plain_room(t), rug(540, RFL + 150, 600)]


def frame_s09(t):
    """«делает всё, кроме дела»: Суетливый носится по комнате с тряпкой (линии скорости), папка «ДЕЛО» стоит в паутине."""
    a, b = T0("s09"), T1("s09")
    o = room(t)
    o.append(folder(800, RFL - 130, 1.0, 0, web=ramp(t, W(24), .4), t=t))
    ph = (t - a) * 2.2
    cx = 400 + 300 * math.sin(ph * 2)
    o.append(kitty(2, cx, RFL - 60 * abs(math.sin(ph * 6)), .85, t, {"look": (math.cos(ph * 2), -.3)}, act=1.0))
    o.append(PR.speed_arcs(cx - 170 * math.copysign(1, math.cos(ph * 2)), RFL - 180, 1.4, 1.0, t, seed=3, ang=180 if math.cos(ph * 2) > 0 else 0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(25), 8)
    return view("".join(o), 580 + dx, 1180 + dy, 1.15 + .06 * u, 0, t=t)


def frame_s10(t):
    return intro(3, t, T0("s10"), T1("s10"), W(27))


def big_cal(x, y, k, label, num, flip=0.0, seed=0):
    o = shape(lib.rect_pts(-230, -280, 230, 280), "#fbf8f1", blob(lib.rect_pts(-230, -280, 230, -150), "#c8553d"), w=5, seed=7600 + seed)
    o += text(label, 0, -185, 96, fill="#ffffff", stroke="#7a2a1e", sw=6)
    o += text(num, 0, 130, 220, fill="#1d2448", stroke="#ffffff", sw=4)
    return f'<g opacity="{1 - flip:.3f}">{tf(o, x, y - 500 * flip * flip, k, -25 * flip)}</g>'


def frame_s11(t):
    """«Начнёт ровно в понедельник»: Ждун смотрит, как листы ЧТ, ПТ, СБ, ВС отрываются и улетают, остаётся «ПН»."""
    a, b = T0("s11"), T1("s11")
    tp = W(31)
    o = room(t)
    days = [("ЧТ", ""), ("ПТ", ""), ("СБ", ""), ("ВС", "")]
    o.append(big_cal(700, 860, 1.0, "ПН", "9:00", seed=9))
    for j in range(3, -1, -1):
        tj = a + (tp - a) * j / 4
        fl = clamp((t - tj) / .25)
        if fl < 1:
            o.append(big_cal(700, 860, 1.0, days[j][0], days[j][1], flip=fl, seed=j))
    if t > tp:
        o.append(f'<circle cx="700" cy="675" r="{130 * pop(t, tp, .25):.1f}" fill="none" stroke="#e2453a" stroke-width="12"/>')
    o.append(kitty(3, 260, RFL, 1.0, t, {"look": (.8, -.6)}))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tp, 9)
    return view("".join(o), 540 + dx, 1050 + dy, 1.05 + .05 * u, 0, t=t)


def frame_s12(t):
    """«в девять ноль-ноль»: большие часы, стрелки доползают до 9:00; Ждун смотрит не мигая; «9:00»."""
    a, b = T0("s12"), T1("s12")
    t9 = W(34)
    o = room(t)
    m = clamp((t - a) / (t9 - a))
    o.append(PR.clock(540, 760, 260, angle_h=270 - 30 * (1 - m), angle_m=360 * (.75 + .25 * m) % 360))
    o.append(kitty(3, 760, RFL, .95, t, {"look": (-.5, -.7), "blink": 0.0}))
    if t > t9:
        o.append(text("9:00", 300, 1200, 170 * pop(t, t9, .25), fill="#FFD23F", stroke="#111", sw=12))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t9, 9)
    return view("".join(o), 540 + dx, 1050 + dy, 1.05 + .06 * u, 0, t=t)


def frame_s13(t):
    return intro(4, t, T0("s13"), T1("s13"), W(36))


def frame_s14(t):
    """«Не начинает, потому что»: Перфекционист над чистым листом, линейка меряет, лупа ходит по листу."""
    a, b = T0("s14"), T1("s14")
    o = [paper_bg()]
    o.append(PR.paper(460, 800, 3.2, 0, kind="blank", seed=3))
    lx = 460 + 160 * math.sin((t - a) * 4)
    o.append(loupe(lx, 760, 1.6, 10))
    o.append(ruler(460, 1080, 1.6, 0))
    o.append(kitty(4, 870, 1330, .9, t, {"look": (-.6, -.7)}))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1050, 1.0 + .06 * u, 0, bg=PAPER, t=t)


def frame_s15(t):
    """«сразу не получится идеально»: на листе дрожащая черта, красный крест, лист мнётся в комок и летит в гору комков."""
    a, b = T0("s15"), T1("s15")
    tx = W(43)
    tc = W(44) + .1
    o = [paper_bg()]
    for j in range(7):
        o.append(PR.paper_ball(140 + 70 * j + 20 * (j % 2), 1300 - 40 * (j % 3), 1.6, rot=40 * j, seed=j))
    cr = ramp(t, tc, .3)
    if cr < 1:
        pg = PR.paper(0, 0, 3.2, 0, kind="blank", seed=3)
        pts = [(-200 + 400 * q, -40 + 30 * math.sin(q * 19) + 20 * math.sin(q * 41)) for q in [i / 40 for i in range(int(40 * clamp((t - a) / .6)) + 1)]]
        if len(pts) > 1:
            pg += line(pts, 9, "#1d2448", taper=.2, wmin=.6, seed=7700)
        if t > tx:
            pg += PR.cross_stroke((-240, -200), (240, 200), (240, -200), (-240, 200), u=ramp(t, tx, .2), w=26, seed=7701)
        o.append(tf(pg, 540 - 300 * cr, 820 + 600 * cr * cr, 1 - .8 * cr, 200 * cr))
    else:
        o.append(PR.paper_ball(330, 1220, 1.8, seed=9))
    o.append(kitty(4, 840, 1300, .9, t, {"look": (-.6, -.5), "smile": 0.0}))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tx, 10)
    return view("".join(o), 560 + dx, 1050 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


def comment_field(x, y, digit, t, t_d, k=1.0):
    """Поле комментария с крупной жёлтой цифрой (печатная цифра выскакивает на t_d)."""
    box = (f'<rect x="-420" y="-150" width="840" height="300" rx="40" fill="#ffffff" stroke="#111" stroke-width="7"/>'
           + f'<path d="M-240 146 l-40 90 l120 -90 z" fill="#ffffff" stroke="#111" stroke-width="7" stroke-linejoin="round"/>'
           + f'<rect x="-416" y="110" width="832" height="36" fill="#ffffff"/>'
           + plain("комментарий", -360, -90, 40, fill="#9aa0aa"))
    o = tf(box, x, y, k, -1.5)
    o += word_print(t, t_d, x, y + 95 * k, 260 * k, digit)
    return o


def frame_s16(t):
    """ПРИЗЫВ: все четыре котика в ряд с номерами, над ними поле комментария, в нём цифра уже на первом кадре."""
    a, b = T0("s16"), T1("s16")
    o = [paper_bg()]
    o.append(grid(t, dy=0))
    o.append(comment_field(540, 300, "1", t, a - .45, .72))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, a + .05, 8)
    return view("".join(o), 540 + dx, 960 + dy, 1.0 + .03 * u, 0, bg=PAPER, t=t)


def frame_s17(t):
    """«номер своего котика»: цифра в поле меняется 2, 3, 4, котик с этим номером подпрыгивает."""
    a, b = T0("s17"), T1("s17")
    i = min(3, 1 + int(clamp((t - a) / (b - a)) * 3))
    ti = a + (b - a) * (i - 1) / 3
    o = [paper_bg()]
    o.append(grid(t, hop_n=i + 1, hop_t=ti, spot=i))
    o.append(comment_field(540, 300, str(i + 1), t, ti - .07 if i > 1 else a - .45, .72))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 960, 1.03 + .03 * u, 0, bg=PAPER, t=t)


def frame_s18(t):
    """«Я свой знаю: я второй»: Дима крупно с телефоном, в комментарии «2»; Суетливый с тряпкой прыгает рядом."""
    a, b = T0("s18"), T1("s18")
    t2 = W(55)
    o = room(t)
    f = stand(330, t, "laugh82" if t > t2 else "proud82", "d82_hold", head_add=.05)
    o.append(f["svg"])
    hx, hy = f["hold"]
    ph = (f'<rect x="-120" y="-210" width="240" height="420" rx="30" fill="#2a2d36" stroke="#111" stroke-width="5"/>'
          f'<rect x="-104" y="-190" width="208" height="380" rx="18" fill="#fbf8f1"/>'
          f'<rect x="-90" y="20" width="180" height="120" rx="20" fill="#ffffff" stroke="#9aa0aa" stroke-width="3"/>')
    o.append(tf(ph, hx + 90, hy - 120, .9, 6))
    if t > t2 - .05:
        o.append(word_print(t, t2 - .05, hx + 90, hy - 120 + 120 * .9, 120, "2"))
    o.append(kitty(2, 820, RFL - 150 * bump(t, t2, .12, .3), .9, t, {"look": (-.7, -.4), "smile": 1.0}, act=1.0))
    o.append(badge(2, 820, RFL - 600 - 150 * bump(t, t2, .12, .3), .8))
    o.append(PR.sparkles(820, RFL - 300, 1.8, bump(t, t2, .05, .5), t, seed=181, n=7, r=260))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t2, 8)
    return view("".join(o), 560 + dx, 1020 + dy, 1.12 + .06 * u, 0, t=t)


def frame_s19(t):
    """Петля: кадр хука — четыре котика с номерами."""
    a, b = T0("s19"), T1("s19")
    o = [paper_bg(), grid(t, q=True)]
    return loop_view("".join(o), t, a, b, HIT, 540, 960, 1.0, bg=PAPER)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
