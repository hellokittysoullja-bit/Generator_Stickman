"""Рилс 111 «Доделал», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json; числа в коде — длительности движений. Говорит Дима от первого лица.
Сквозное место: комната, на стене лист «НАЧАТО» из десяти дел, красный маркер, комод с котом справа.
NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

ITEMS = ["Диплом", "Курс английского", "Полка", "Сайт", "Книга", "Спортзал", "Гитара", "Шкаф", "Блог", "Права"]
DONE = (2, 4, 7)                         # три галочки: полка, книга, шкаф
LIST = (520.0, 760.0)                    # центр листа на стене
LW, LH = 560.0, 780.0
ROW0, ROWS = LIST[1] - LH / 2 + 150, 60.0
HIT = stress(1, .3)
DRESSER = (830.0, RFL)


def row_y(i):
    return ROW0 + ROWS * i


def box_xy(i):
    return LIST[0] - LW / 2 + 62, row_y(i) - 14


def task_list(t, ticks=None, glow=0.0, pins=1.0, extra_row=None):
    """Лист «НАЧАТО» на стене: ticks — {номер строки: доля нарисованной галочки}; glow — свечение галочек."""
    ticks = ticks or {}
    x0, y0 = LIST[0] - LW / 2, LIST[1] - LH / 2
    o = [blob(lib.rect_pts(x0 + 14, y0 + 18, x0 + LW + 14, y0 + LH + 18), "#000000", .14)]
    inner = plain("НАЧАТО:", x0 + 50, y0 + 92, 60, fill="#1d2448")
    inner += line([(x0 + 48, y0 + 112), (x0 + 300, y0 + 108)], 5, "#e2453a", taper=.3, wmin=.5, seed=301)
    for i, s in enumerate(ITEMS):
        y = row_y(i)
        bx, by = box_xy(i)
        inner += shape(lib.rect_pts(bx - 18, by - 18, bx + 18, by + 18), "#ffffff", "", w=3, seed=310 + i)
        inner += plain(s, x0 + 106, y, 38, fill="#2a2f4a")
        u = ticks.get(i, 0.0)
        if u > 0:
            if glow > 0:
                inner += PR.glow(bx + 6, by - 6, 70, .6 * glow, "#ff9a7a")
            inner += PR.check_mark(bx + 4, by - 2, 1.9, u, col="#e2453a", w=10, seed=320 + i)
    if extra_row is not None:
        inner += extra_row
    o.append(shape(lib.rect_pts(x0, y0, x0 + LW, y0 + LH), "#fbf8f1", inner, w=4, seed=300))
    if pins > 0:
        for j, (px, py) in enumerate(((x0 + 40, y0 + 30), (x0 + LW - 40, y0 + 30))):
            o.append(PR.push_pin(px, py, 1.2 * pins))
    return "".join(o)


def marker_at(x, y, k=2.2, rot=-130.0):
    """Красный маркер, кончик в (x, y): ручка уходит вниз-вправо."""
    a = math.radians(rot)
    L = 62 * k
    return PR.red_marker(x - L * math.cos(a), y - L * math.sin(a), k, rot)


def tick_path(i, u):
    """Где кончик маркера, пока рисует галочку строки i (u 0…1) — по форме check_mark."""
    bx, by = box_xy(i)
    pts = [(-22, 0), (-12, 10), (-6, 17), (6, 2), (18, -12), (28, -24)]
    k = 1.9
    n = len(pts) - 1
    q = clamp(u) * n
    j = min(n - 1, int(q))
    f = q - j
    ax, ay = pts[j]
    cx, cy = pts[j + 1]
    return bx + 4 + (ax + (cx - ax) * f) * k, by - 2 + (ay + (cy - ay) * f) * k


def ticking(t, plan):
    """plan — [(строка, начало, длительность)]: галочки и где маркер."""
    ticks = {}
    tip = None
    for i, a, d in plan:
        u = clamp((t - a) / d)
        if u > 0:
            ticks[i] = u
        if a - .25 <= t <= a + d + .15:
            tip = tick_path(i, u) if t >= a else None
    return ticks, tip


def dresser(t, cat_on=True, cat_st=None):
    x, y = DRESSER
    o = [shape(lib.rrect(x - 150, y - 360, x + 150, y, 10), "#a8774a",
               blob(lib.rect_pts(x - 150, y - 190, x + 150, y - 180), "#8a6038"), w=4, seed=620)]
    for j in (0, 1):
        o.append(shape(ellipse_pts(x, y - 270 + 170 * j, 14, 10, 10), "#6e4a2c", "", w=3, seed=621 + j))
    if cat_on:
        o.append(cat(x + 10, y - 360, .62, t, dict(dict(look=(-.8, -.3), smile=.6, tail=10 * math.sin(t * 3)), **(cat_st or {}))))
    return "".join(o)


def room(t):
    o = [plain_room(t)]
    o.append(rug(520, RFL + 150, 560))
    o.append(PR.plant(1180, RFL, 1.0, seed=3) if hasattr(PR, "plant") else "")
    return o


def sticky_word(x, y, k, word, rot=0.0, col="#ffe36e"):
    body = shape(lib.rect_pts(-120, -70, 120, 70), col, blob(lib.rect_pts(-124, -74, 124, -50), lib.mul(col, (.9, .9, .88))), w=3.4, seed=900)
    body += plain(word, 0, 18, 46 if len(word) < 8 else 34, fill="#1d2448", anchor="middle")
    return tf(body, x, y, k, rot)


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: лист «НАЧАТО» крупно, красный маркер уже в движении и ставит галочки на полке и книге."""
    ticks, tip = ticking(t, [(2, -0.05, .3), (4, .38, .28)])
    o = room(t)
    o.append(task_list(t, ticks, glow=bump(t, .3, .05, .4)))
    o.append(dresser(t, cat_st=dict(look=(-.6, -.8), smile=.6)))
    if tip:
        o.append(marker_at(*tip))
    else:
        o.append(marker_at(tick_path(4, 1.0)[0] + 30, tick_path(4, 1.0)[1] + 40))
    o.append(PR.sparkles(*box_xy(2), 1.2, bump(t, .25, .05, .4), t, seed=11, n=5, r=90))
    o.append(PR.sparkles(*box_xy(4), 1.2, bump(t, .66, .05, .4), t, seed=12, n=5, r=90))
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 560, 740 + 40 * ramp(t, 0, .9), 1.45, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«закончил то, что начал»: Дима у листа ставит третью галочку (шкаф), улыбается; кот на комоде."""
    a, b = T0("s02"), T1("s02")
    tt = W(5) - .15
    ticks = {2: 1.0, 4: 1.0}
    u = clamp((t - tt) / .3)
    if u > 0:
        ticks[7] = u
    o = room(t)
    o.append(task_list(t, ticks, glow=bump(t, tt + .3, .05, .5)))
    o.append(dresser(t, cat_st=dict(look=(-.9, -.4), smile=1.0 if t > tt + .3 else .5)))
    tip = tick_path(7, u) if u > 0 else (box_xy(7)[0] + 60, box_xy(7)[1] + 40 - 60 * ramp(t, a, tt - a))
    f = stand(160, t, "laugh82" if t > tt + .3 else "proud82", "d82_rest", arms={"n": ("ik", (tip[0] + 70, tip[1] + 50), -1)},
              head_add=.05 * bump(t, tt + .3, .05, .3))
    o.append(f["svg"])
    o.append(marker_at(*tip, k=1.4, rot=-150))
    o.append(PR.sparkles(*box_xy(7), 1.4, bump(t, tt + .3, .05, .5), t, seed=21, n=6, r=120))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tt + .3, 9)
    return view("".join(o), 470 + dx, 1030 + dy, 1.18 + .05 * uu, -1 + 2 * uu, t=t)


def half_shelf(x, y, k, done=.5):
    """Полка-стеллаж, собранная до половины: две стойки, нижние две доски на месте, верхние лежат на полу."""
    o = []
    for s in (-1, 1):
        o.append(shape(lib.rect_pts(x + s * 200 - 14, y - 640, x + s * 200 + 14, y), "#c99a6b", "", w=4, seed=700 + s))
    for j in range(4):
        yy = y - 40 - 190 * j
        if j < 2:
            o.append(shape(lib.rect_pts(x - 214, yy - 16, x + 214, yy + 10), "#d9ae7e", "", w=4, seed=710 + j))
    for j in range(2):
        o.append(tf(shape(lib.rect_pts(-214, -14, 214, 12), "#d9ae7e", "", w=4, seed=720 + j), x + 350 + 30 * j, y - 14 - 26 * j, 1.0, -4 + 6 * j))
    return tf("".join(o), 0, 0, 1.0) if k == 1 else tf("".join(o), x * (1 - k), y * (1 - k), k)


def screwdriver(x, y, k=1.0, rot=0.0):
    o = shape(lib.rrect(-60, -16, 40, 16, 10), "#e2453a", blob(lib.rect_pts(-50, -4, 30, 4), "#b8332a"), w=3.4, seed=730)
    o += shape(lib.rect_pts(40, -5, 150, 5), "#9aa0aa", "", w=3, seed=731)
    return tf(o, x, y, k, rot)


def frame_s03(t):
    """«А раньше бросал на середине»: полка собрана наполовину; Дима роняет отвёртку и отворачивается к телефону; «50%»."""
    a, b = T0("s03"), T1("s03")
    td = W(10)
    o = [plain_room(t)]
    o.append(rug(560, RFL + 150, 600))
    o.append(half_shelf(700, RFL, 1.0))
    drop = ease_in_(ramp(t, td, .3))
    if t < td:
        f = stand(330, t, "calm82", "d82_hold", head_add=.05)
        hx, hy = f["wrist"]["n"]
        o.append(f["svg"])
        o.append(screwdriver(hx + 10, hy - 10, 1.2, -30))
    else:
        f = stand(300, t, "sure82", "d82_rest", flip=True, head_add=-.05)
        o.append(f["svg"])
        o.append(screwdriver(450 + 40 * drop, 1180 + (RFL - 30 - 1180) * drop, 1.2, -30 + 120 * drop))
        o.append(mini_phone(f["hold"][0] if False else 150, 960, .7, 10, screen="#7fb7ff"))
    o.append(text("50%", 760, 760, 170 * pop(t, W(9), .25), fill="#e2453a", stroke="#111", sw=12) if t > W(9) else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, td + .3, 10)
    return view("".join(o), 540 + dx, 1050 + dy, 1.12 + .06 * u, 0, t=t)


def ease_in_(u):
    return u * u


STARTED = [("Курс", -330, -420, -8), ("Гитара", 320, -470, 7), ("Сайт", -380, -160, 6), ("Спортзал", 360, -200, -6),
           ("Книга", -350, 100, -5), ("Блог", 380, 60, 8), ("Права", -300, 340, 4), ("Шкаф", 330, 320, -7),
           ("Диплом", -40, -640, 3), ("Полка", 40, 520, -4)]


def frame_s04(t):
    """«копил десять начатых»: вокруг Димы по одному выскакивают стикеры начатых дел, счётчик красным до 10."""
    a, b = T0("s04"), T1("s04")
    o = [plain_room(t)]
    o.append(rug(540, RFL + 150, 600))
    f = stand(540, t, "panic82" if t > W(13) else "sure82", "d82_shrug", head_add=.05 * math.sin(t * 6))
    o.append(f["svg"])
    hx, hy = f["head"]
    span_ = max(.3, W(13) + .2 - a)
    n = 0
    for j, (w_, dx_, dy_, r_) in enumerate(STARTED):
        tj = a + span_ * j / 9
        if t >= tj:
            n = j + 1
            o.append(sticky_word(540 + dx_, 1000 + dy_, .95 * pop(t, tj, .2), w_, r_ + 3 * math.sin(t * 4 + j)))
    if n:
        o.append(text(str(n), 540, 560, 230 * (1 + .25 * bump(t, a + span_ * (n - 1) / 9, .04, .2)), fill="#e2453a", stroke="#111", sw=14))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(13), 10)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .08 * u, 0, t=t)


def bed_room_night(t):
    o = [plain_room(t, wall="#c9c2d8", floor="#a99a8a")]
    o.append(PR.window(250, 900, 330, 420, mode="night", t=t, seed=3, curtain=False))
    o.append(PR.bed(600, RFL, 1.25, seed=1))
    return o


def frame_s05(t):
    """«а вечером грыз себя за каждое»: ночь, Дима лежит с открытыми глазами, над ним туча из начатых дел, молнии."""
    a, b = T0("s05"), T1("s05")
    o = bed_room_night(t)
    mat = RFL - 118 * 1.25
    f = people.dima_bed(660, mat + 10, .62, expr="panic82" if t > W(16) else "sure82", t=t, cover="chest", col="blue")
    o.append(f["svg"])
    hx, hy = f["head"]
    cu = ease_out(ramp(t, a + .05, .3))
    flash = bump(t, W(19), .04, .2) + bump(t, W(16), .04, .2)
    o.append(PR.storm(520, 930, 560, 240, sx=cu, sy=cu, seed=4, flash=min(1.0, flash)))
    for j, (w_, dx_, dy_, r_) in enumerate(STARTED[:6]):
        ang = t * 1.6 + j * math.pi / 3
        o.append(sticky_word(560 + 330 * math.cos(ang), 940 + 110 * math.sin(ang), .5 * cu, w_, r_))
    if flash > .05:
        o.append(PR.bolt(480, 1020, hx + 20, hy - 70, u=1.0, w=26, seed=int(t > W(19))))
    o.append(rect(-1400, -1400, 2600, 2900, "#1d2448", .35))
    o.append(PR.glow(hx, hy, 260, .3 + .4 * flash, "#ffe9a8"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(16), 12)
    return view("".join(o), 540 + dx, 1150 + dy, 1.45 + .08 * u, 0, bg="#2a2f4a", t=t)


def frame_s06(t):
    """«Вот что я поменял»: Дима у листа поднимает палец, над ним лампочка; кот на комоде; надпись сверху."""
    a, b = T0("s06"), T1("s06")
    ti = W(20) + .15
    o = room(t)
    o.append(task_list(t))
    o.append(dresser(t))
    f = stand(130, t, "wow82" if t > ti else "sure82", "d82_one", head_add=.06 * bump(t, ti, .08, .3))
    o.append(f["svg"])
    hx, hy = f["head"]
    if t > ti:
        o.append(PR.glow(hx + 170, hy - 200, 220, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx + 170, hy - 200 + 8 * math.sin(t * 5), 1.2 * pop(t, ti, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx + 170, hy - 200, 1.8, bump(t, ti, .05, .5), t, seed=41, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ti, 9)
    return view("".join(o), 470 + dx, 980 + dy, 1.18 + .05 * u, -1 + 2 * u, t=t)


def barrier(x, y, k, up=0.0):
    """Шлагбаум: стойка слева, полосатая планка поднимается (up 0 — опущена, 1 — вверх)."""
    o = [shape(lib.rect_pts(-22, -260, 22, 0), "#5a5f6e", "", w=4, seed=740)]
    ang = -80 * up
    bar = ""
    for j in range(6):
        bar += shape(lib.rect_pts(30 + 70 * j, -20, 100 + 70 * j, 20), "#e2453a" if j % 2 == 0 else "#ffffff", "", w=3, seed=741 + j)
    o.append(f'<g transform="translate(0 -230) rotate({ang:.2f})">{bar}</g>')
    o.append(shape(ellipse_pts(0, -230, 26, 26, 12), "#3a3d48", "", w=3, seed=750))
    return tf("".join(o), x, y, k)


def frame_s07(t):
    """«Новое начинаю только после того»: Дима держит стикер «НОВОЕ», перед листом опущен шлагбаум — стикер отскакивает."""
    a, b = T0("s07"), T1("s07")
    tb = W(26)
    o = room(t)
    o.append(task_list(t))
    o.append(barrier(850, 1180, 1.0, 0.0))
    # стикер летит к листу и отскакивает от шлагбаума
    fly = ease_in_(ramp(t, a + .2, tb - a - .2))
    back = ease_out(ramp(t, tb, .45))
    sx = 1250 - 330 * fly + 220 * back
    sy = 900 - 40 * fly + 60 * back
    o.append(sticky_word(sx, sy, 1.15, "НОВОЕ", -8 + 30 * back, col="#9fe0a4"))
    if t > tb:
        o.append(text("!", sx - 10, sy - 140, 150 * pop(t, tb, .2), fill="#e2453a", stroke="#111", sw=10))
    f = stand(170, t, "squint82" if t > tb else "calm82", "d82_one", head_add=-.04)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 10)
    return view("".join(o), 560 + dx, 1020 + dy, 1.05 + .05 * u, 0, t=t)


def frame_s08(t):
    """«как закрыл одно старое»: маркер ставит галочку на «Полке», шлагбаум поднимается, «НОВОЕ» прилипает к стене."""
    a, b = T0("s08"), T1("s08")
    tt = W(30)
    ticks, tip = ticking(t, [(2, tt, .35)])
    up = ease_out(ramp(t, W(32), .35))
    o = room(t)
    o.append(task_list(t, ticks, glow=bump(t, tt + .35, .05, .5)))
    o.append(barrier(850, 1180, 1.0, up))
    stick = ease_out(ramp(t, W(32) + .1, .35))
    o.append(sticky_word(1030 - 140 * stick, 860 + 0 * stick, 1.15 * (1 + .15 * bump(t, W(32) + .45, .04, .2)), "НОВОЕ", 22 - 28 * stick,
                         col="#9fe0a4"))
    if tip:
        o.append(marker_at(*tip, k=2.0))
    o.append(PR.sparkles(*box_xy(2), 1.4, bump(t, tt + .35, .05, .5), t, seed=81, n=6, r=110))
    o.append(PR.sparkles(870, 860, 1.4, bump(t, W(32) + .45, .05, .5), t, seed=82, n=6, r=150))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(32) + .45, 8)
    return view("".join(o), 680 + dx, 860 + dy, 1.45 + .06 * u, 0, t=t)


def frame_s09(t):
    """«А список начатых висит на стене»: Дима прикладывает лист к стене и вдавливает кнопки; кот на комоде кивает."""
    a, b = T0("s09"), T1("s09")
    p1, p2 = W(36), W(38)
    lift = 1 - ease_out(ramp(t, a, p1 - a - .05))
    o = room(t)
    lst = task_list(t, {2: 1.0}, pins=0.0)
    o.append(tf(lst, 0, 80 * lift, 1.0, 4 * lift))
    for j, (pt, px) in enumerate(((p1, LIST[0] - LW / 2 + 40), (p2, LIST[0] + LW / 2 - 40))):
        if t > pt:
            o.append(PR.push_pin(px, LIST[1] - LH / 2 + 30, 1.2 * pop(t, pt, .2)))
    o.append(dresser(t, cat_st=dict(look=(-.9, -.5), smile=.8)))
    hx = LIST[0] - LW / 2 + 40 if t < p1 + .1 else LIST[0] + LW / 2 - 40
    f = stand(230, t, "proud82", "d82_rest", arms={"n": ("ik", (hx + 20, LIST[1] - LH / 2 + 60 + 80 * lift), -1)}, head_add=-.1)
    o.append(f["svg"])
    o.append(PR.sparkles(LIST[0], LIST[1] - LH / 2, 1.6, bump(t, p2, .05, .5), t, seed=91, n=6, r=260))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, p2, 7)
    return view("".join(o), 520 + dx, 1020 + dy, 1.15 + .06 * u, 1 - 2 * u, t=t)


def frame_s10(t):
    return cta_code(t, T0("s10"), T1("s10"))


def frame_s11(t):
    """«чтобы твои начатые дела»: лист крупно, маркер быстро ставит галочки на «Полке», «Книге», «Шкафу»."""
    a, b = T0("s11"), T1("s11")
    d = (b - a - .1) / 3
    ticks, tip = ticking(t, [(2, a - .05, d), (4, a - .05 + d, d), (7, a - .05 + 2 * d, d)])
    o = room(t)
    o.append(task_list(t, ticks))
    o.append(dresser(t, cat_st=dict(look=(-.6, -.8), smile=.8)))
    if tip:
        o.append(marker_at(*tip))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 700 + 40 * u, 1.4, 1 - 2 * u, t=t)


def frame_s12(t):
    """«наконец закрывались»: Дима наклоняется и даёт пять коту на комоде, конфетти над листом."""
    a, b = T0("s12"), T1("s12")
    th = W(47) + .1
    o = room(t)
    o.append(task_list(t, {i: 1.0 for i in DONE}, glow=.6))
    o.append(dresser(t, cat_st=dict(look=(-.9, -.6), smile=1.0, perk=1.0)))
    reach = ease_out(ramp(t, a, th - a))
    f = stand(500, t, "laugh82" if t > th else "proud82", "d82_rest",
              arms={"n": ("ik", (660 + 80 * reach, 1060 - 40 * reach), -1)}, head_add=.08)
    o.append(f["svg"])
    o.append(PR.sparkles(820, 1040, 1.6, bump(t, th, .05, .5), t, seed=121, n=7, r=150))
    for j in range(18):
        rs = (j * 37 % 17) / 17
        u = ramp(t, th + .02 * j, 1.2)
        if u > 0:
            x = 540 + (rs - .5) * 900
            y = 300 + 900 * u * u - 300 * u
            col = ("#e2453a", "#FFD23F", "#3fb26a", "#2f8fe0")[j % 4]
            o.append(tf(shape(lib.rect_pts(-14, -8, 14, 8), col, "", w=2, seed=1200 + j), x, y, 1.0, 360 * u * (1 + rs)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, th, 9)
    return view("".join(o), 620 + dx, 1030 + dy, 1.15 + .05 * u, 0, t=t)


def frame_s13(t):
    """«Теперь на стене три галочки»: лист крупно, три красные галочки вспыхивают по очереди на «три»; надпись «3 ИЗ 10»."""
    a, b = T0("s13"), T1("s13")
    t3 = W(51)
    o = room(t)
    o.append(task_list(t, {i: 1.0 for i in DONE}, glow=.4 + .6 * bump(t, t3, .05, .6)))
    o.append(dresser(t, cat_st=dict(look=(-.6, -.8), smile=1.0, perk=bump(t, t3, .05, .5))))
    for j, i in enumerate(DONE):
        o.append(PR.sparkles(*box_xy(i), 1.3, bump(t, t3 + .08 * j, .05, .5), t, seed=131 + j, n=5, r=100))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t3, 9)
    return view("".join(o), 540 + dx, 790 + dy, 1.38 + .08 * u, 0, t=t)


def frame_s14(t):
    """«и ни одного нового „потом“»: стикер «ПОТОМ» летит к листу, кот на комоде отбивает его лапой, стикер улетает."""
    a, b = T0("s14"), T1("s14")
    ts = W(57) - .1
    o = room(t)
    o.append(task_list(t, {i: 1.0 for i in DONE}, glow=.3))
    fly = ease_in_(ramp(t, a, ts - a))
    back = ease_out(ramp(t, ts, .5))
    sx = -100 + 900 * fly + 700 * back
    sy = 600 + 260 * fly - 700 * back
    o.append(sticky_word(sx, sy, 1.1, "ПОТОМ", -10 + 400 * back, col="#ffb3a8"))
    paw = bump(t, ts - .05, .06, .25)
    o.append(dresser(t, cat_st=dict(look=(-.9, -.5), smile=1.0 if t > ts else .2, paw=paw, perk=1.0)))
    o.append(PR.sparkles(sx, sy, 1.3, bump(t, ts, .05, .4), t, seed=141, n=6, r=120))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts, 10)
    return view("".join(o), 600 + dx, 1000 + dy, 1.1 + .06 * u, 0, t=t)


def frame_s15(t):
    """Петля: кадр хука — лист крупно, маркер у строки."""
    a, b = T0("s15"), T1("s15")
    o = room(t)
    o.append(task_list(t))
    o.append(dresser(t, cat_st=dict(look=(-.6, -.8), smile=.6)))
    tip = tick_path(2, 0.0)
    o.append(marker_at(tip[0] + 40 * (1 - ramp(t, a, b - a)), tip[1] + 30))
    return loop_view("".join(o), t, a, b, HIT, 560, 740, 1.45)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
