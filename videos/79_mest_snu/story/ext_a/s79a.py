"""Рилс 79 «Месть сну», группа A: предметы и графика — s03, s04, s08, s10, s11, s14.
Время — ТОЛЬКО из shots.json (t0/t1 плана) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
s03 ванная (тёплый вечер): Дима чистит зубы у раковины; «спать» (w9) огромный зевок, щётка застывает, плечи вверх, камера +5 %;
    «хотел» (w11) пена капает в раковину, он клюёт носом и вздрагивает.
s04 кухня вечером: щека на кулаке над недоеденным ужином; «глаза» (w12) веки тяжелеют; «слипались» (w13) голова соскальзывает с
    кулака — рывок-кивок и тряска; «десять» (w16) за окном над крышами встаёт луна, Дима сонно улыбается; кот на подоконнике зевает.
s08 день (хлёст): окно офиса, солнце несётся по дуге «Весь» (w34) – «день» (w35), тени на столе метут по кругу; «жил» (w37) Дима
    пишет за столом, его тень крутится.
s10 угол с пыльной гитарой: «ни» (w44) Дима проносится с папками (смаз), «минуты» (w45) пыль взвихривается и оседает, «себя» (w47)
    он оглядывается в дверях и убегает, дверь хлопает, гитара звякает.
s11 часы мансарды крупно: тёплый сектор 11→3 проступает; «ночью» (w49) в люке сонная луна; «мозг» (w50) – «отбирает» (w51) рука
    из-под одеяла в голубом свете отклеивает сектор, как наклейку, и тянет вниз; камера наезжает и дёргается вниз.
s14 полка над кроватью: подушка-сон; палец в голубом свете трижды щелчком отодвигает её — «откладывание» (w65: начало и середина),
    «сна» (w66): доезжает до края и печально свешивается.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rect_pts, shape, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def wm(i):
    return (WORDS[i]["start"] + WORDS[i]["end"]) / 2


def T0(sid):
    return SHOTS[sid]["t0"]


def T1(sid):
    return SHOTS[sid]["t1"]


def A0(sid):
    return max(0.0, T0(sid) - SH["pad"])


def lerp(a, b, u):
    return a + (b - a) * u


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up, hold, down):
    """0 → 1 за up, держится hold, 1 → 0 за down (плавно)."""
    if t < a:
        return 0.0
    if t < a + up:
        return ease_out((t - a) / up, 2)
    if t < a + up + hold:
        return 1.0
    return 1 - ease_io((t - a - up - hold) / down)


def frame_svg(body, cx, cy, s, rot, bg, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def shadow(x, y, rx, op=.16, col="#3B2A1A"):
    return blob(ellipse_pts(x, y, rx, rx * .12, 20), col, op)


def whip_in(t, t0, amp=420.0, dur=.3):
    """Хвост хлёста внутри клипа: камера влетает со стороны и тормозит без остановки."""
    u = clamp((t - t0 + .06) / dur)
    return amp * (1 - ease_out(u, 3))


def light_rect(x0, y0, x1, y1, col, op):
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}" opacity="{op:.3f}"/>'


def vignette(col="#2a1a10", op=.35):
    g = lib.rad_grad([(0, col, 0), (.62, col, 0), (1, col, op)], 540, 760, 1050, 1250)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def cat_state(name, **over):
    st = dict(people.CAT_ST.get(name, {})) if hasattr(people, "CAT_ST") else {}
    st.update(over)
    return st


def ex(name, **over):
    e = dict(people.EXPR["dima"].get(name, {}))
    e.update(over)
    return e


# ═══════════════════════════════ s03: ванная, зевок ═══════════════════════════════
BATH_WALL = "#EBD7A8"
BATH_TILE_LN = "#D2B983"
BATH_LOW = "#9CC3C0"
BATH_LOW_LN = "#7FA8A4"
BATH_FLOOR = "#B88F5F"


def bath_bg(t):
    o = [f'<path d="M-600 -600H1700V1690H-600Z" fill="{BATH_WALL}"/>']
    d = "".join(f"M-600 {y}H1700" for y in range(-560, 1000, 110)) + "".join(f"M{x} -600V1000" for x in range(-580, 1700, 110))
    o.append(f'<path d="{d}" stroke="{BATH_TILE_LN}" stroke-width="3" fill="none"/>')
    o.append(f'<path d="M-600 1000H1700V1690H-600Z" fill="{BATH_LOW}"/>')
    d = "".join(f"M-600 {y}H1700" for y in range(1080, 1690, 80)) + "".join(f"M{x} 1000V1690" for x in range(-580, 1700, 80))
    o.append(f'<path d="{d}" stroke="{BATH_LOW_LN}" stroke-width="3" fill="none"/>')
    o.append(shape(rect_pts(-600, 990, 1700, 1012), "#F3E6C4", "", w=3.4, seed=301))
    o.append(f'<path d="M-600 1690H1700V2600H-600Z" fill="{BATH_FLOOR}"/>')
    o.append(line([(-600, 1690), (1700, 1692)], 5, INK, taper=.05, wmin=.8, seed=302))
    # бра над раковиной — тёплый свет
    o.append(P.glow(830, 330, 330, .55, "#FFD98A"))
    o.append(shape(rrect_pts(790, 300, 870, 360, 20), "#F7E3B0", blob(rect_pts(790, 340, 870, 362), "#E2C27A"), w=3.6, seed=303))
    o.append(shape(rect_pts(822, 360, 838, 420), P.C_METAL_SH, "", w=2.6, seed=304))
    # полотенце на перекладине слева (широкое, в полоску)
    o.append(shape(rrect_pts(-40, 500, 300, 516, 6), P.C_METAL, "", w=3.0, seed=305))
    sw = 3 * math.sin(t * 1.7)
    o.append(shape([(-10, 508), (250, 508), (254 + sw, 800), (-6 + sw, 800)], "#5C9AD6",
                   blob(rect_pts(-20, 730, 270, 760), "#F4E9D8") + blob(rect_pts(-20, 770, 270, 782), "#F4E9D8") +
                   blob(rect_pts(200, 500, 270, 810), "#3F78B5"), w=4.0, seed=306))
    return "".join(o)


def rrect_pts(x0, y0, x1, y1, r):
    return lib.rrect(x0, y0, x1, y1, r)


def s03(t):
    lib.dyn_begin()
    a = A0("s03")
    t_y = ws(9)          # «спать» — зевок
    t_h = ws(11)         # «хотел» — пена капает, клюёт носом
    yawn = bump(t, t_y - .06, .2, max(.1, t_h - t_y - .12), .22)
    nod = bump(t, t_h + .02, .22, .06, .18)                  # голова вниз
    jerk = bump(t, t_h + .34, .05, .1, .28)                  # вздрогнул
    brushing = 1 - clamp(yawn * 1.6)
    brushing *= 1 - .7 * nod
    osc = 13 * math.sin(t * 2 * math.pi * 4.2) * brushing
    sc = .9
    hx, hy = 400, 1140
    breath = 3 * math.sin(t * 2.6)
    lean = .26 + .08 * nod - .05 * yawn - .05 * jerk
    head_add = -.22 * yawn + .32 * nod - .12 * jerk
    if yawn > .45:
        e = ex("yawn79", open=clamp((yawn - .3) / .5), closed=1.0)
    elif jerk > .3:
        e = ex("nodjerk79")
    elif nod > .3:
        e = ex("doze79", lid=.05)
    else:
        e = ex("doze79", lid=.22 + .1 * math.sin(t * 3))
    shrug = .85 * yawn
    feet = people.stand_kw(hx, hy, sc)["feet"]
    # голова: первая прикидка без рук, чтобы поставить щётку в рот
    probe = people.dima(hx, hy + breath, sc, e, lean_add=lean, head_add=head_add, shrug=shrug, feet=feet, layers=("body",))
    px, py = probe["head"]
    mx, my = px + 64 * sc, py + 88 * sc + 10 * yawn
    bx, by = mx + osc, my + 2
    wr = (bx + 150 + 6 * yawn, by + 40 + 80 * yawn)
    arms = {"n": ("ik", wr, -1), "f": ("ang", 0.16 + .1 * yawn, 0.22)}
    hands = {"n": {"dir": (-.15, -1), "curl": (.72, .74, .78, .8), "thumb": .65}}
    fig_back = people.dima(hx, hy + breath, sc, e, lean_add=lean, head_add=head_add, shrug=shrug, feet=feet, arms=arms, hands=hands,
                           layers=("legs", "pelvis", "arm_f", "body"))
    fig_arm = people.dima(hx, hy + breath, sc, e, lean_add=lean, head_add=head_add, shrug=shrug, feet=feet, arms=arms, hands=hands,
                          layers=("arm_n",))
    foam = clamp((t - a) / .4) * (1 - .4 * yawn)
    o = [bath_bg(t)]
    o.append(shadow(hx + 40, 1716, 230))
    o.append(P.sink_brush(680, 1110, 1.1, foam_u=clamp((t - t_h - .5) / .25), t=t))
    o.append(fig_back["svg"])
    # щётка: головка во рту (у губ), ручка вправо через кулак
    o.append(P.toothbrush(bx - 6 + 10 * yawn, by + 6 + 26 * yawn, 1.05, rot=6 + 22 * yawn, foam_u=foam, t=t))
    # пена у губ
    if foam > .05 and yawn < .6:
        for j in range(3):
            o.append(shape(ellipse_pts(mx - 4 + 9 * j, my + 14 + 3 * math.sin(t * 9 + j), 9 * foam, 7 * foam, 9), P.C_FOAM, "", w=2.2, seed=330 + j, var=.1))
    # капля пены тянется с губ и падает за рукой (в раковину)
    for (dx_, d0, sd_) in ((22, -.02, 3), (10, .16, 4)):
        u_ = ramp(t, t_h + d0, .55)
        if u_ < .62:
            o.append(P.foam_drop(mx + dx_, my + 22, 1.3, u=u_, seed=sd_))
    o.append(fig_arm["svg"])
    # камера: мягкий дрейф + толчок +5 % на «спать»
    s_ = 1.32 + .066 * ease_out(ramp(t, t_y - .04, .2), 2) - .02 * ramp(t, t_y + .5, 1.0)
    s_ += .012 * (t - a)
    cx = 500 + 16 * (t - a)
    cy = 880 + 6 * math.sin((t - a) * 2.0)
    shk = P.shake(t, t_h + .34, 9, .3, seed=33) if hasattr(P, "shake") else (0, 0)
    sx, sy = (shk if isinstance(shk, tuple) else (0, 0))
    over = light_rect(0, 0, 1080, 1920, "#FFB45A", .08) + vignette("#3a2410", .32)
    return frame_svg("".join(o), cx - sx, cy - sy, s_, -.6 + .3 * math.sin((t - a) * 1.4), BATH_WALL, over)


SCENES = {"s03": s03}


# ═══════════════════════════════ s04: кухня вечером, клюёт носом ═══════════════════════════════
KIT_WALL = "#E6C48C"
KIT_WALL_SH = "#CFA96E"


def roofs(x0, x1, y, col, seed=0, h=150.0, lit=None):
    """Ряд домиков: прямоугольник с двускатной крышей и трубой; lit — цвет окошек (None — без окон)."""
    rs = lib.np.random.RandomState(400 + seed)
    o = []
    x = x0
    while x < x1:
        w = rs.uniform(120, 200)
        hh = h * rs.uniform(.55, 1.0)
        top = y - hh
        body = [(x, y + 400, 1), (x, top, 1), (x + w * .5, top - w * .32, 1), (x + w, top, 1), (x + w, y + 400, 1)]
        o.append(blob(body, col))
        if rs.rand() < .6:
            cx_ = x + w * .72
            o.append(blob(rect_pts(cx_ - 11, top - w * .26 - 26, cx_ + 11, top - 4), col))
        if lit:
            for j in range(2):
                if rs.rand() < .55:
                    wx = x + w * (.25 + .38 * j)
                    o.append(blob(rect_pts(wx, top + 30, wx + 20, top + 56), lit, .95))
        x += w + rs.uniform(-10, 14)
    return "".join(o)


def kitchen_window(t, moon_u, x0=560, y0=230, x1=1000, y1=820):
    o = []
    g = lib.lin_grad([(0, "#3B4C8C", 1), (.55, "#7B7DB5", 1), (1, "#F2A86E", 1)], 0, 0, 0, 1)
    sky = f'<path d="M{x0} {y0}H{x1}V{y1}H{x0}Z" fill="url(#{g})"/>'
    # луна встаёт из-за крыш
    my = lerp(y1 + 40, y0 + 190, ease_out(moon_u, 2))
    sky += P.moon(x0 + 300, my, 46, .8 * moon_u + .2)
    for j in range(5):
        sx, sy = x0 + 50 + 83 * j, y0 + 40 + 37 * ((j * 3) % 4)
        sky += P.star4(sx, sy, 7 + 2 * math.sin(t * 3 + j), .6 + .4 * math.sin(t * 2 + j))
    sky += roofs(x0 - 40, x1 + 40, y1 - 120, "#4A4470", 3, 120, "#E9B860")
    sky += roofs(x0 - 80, x1 + 60, y1 - 30, "#2B2748", 7, 110, "#FFD27A")
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o.append(f'<g clip-path="url(#{c})">{sky}</g>')
    o.append(shape(rect_pts(x0 - 26, y0 - 26, x1 + 26, y0), P.C_WOOD, "", w=3.6, seed=410))
    o.append(shape(rect_pts(x0 - 26, y0, x0, y1), P.C_WOOD, "", w=3.6, seed=411))
    o.append(shape(rect_pts(x1, y0, x1 + 26, y1), P.C_WOOD, "", w=3.6, seed=412))
    o.append(shape(rect_pts((x0 + x1) / 2 - 10, y0, (x0 + x1) / 2 + 10, y1), P.C_WOOD, "", w=3.0, seed=413))
    o.append(shape(rect_pts(x0 - 50, y1, x1 + 50, y1 + 34), P.C_WOOD_HI, blob(rect_pts(x0 - 60, y1 + 22, x1 + 60, y1 + 40), P.C_WOOD_SH), w=3.8,
                   seed=414))
    return "".join(o)


def kitchen_bg(t, moon_u):
    o = [f'<path d="M-700 -600H1800V1500H-700Z" fill="{KIT_WALL}"/>']
    o.append(blob(rect_pts(-700, 1180, 1800, 1500), KIT_WALL_SH))
    o.append(f'<path d="M-700 1500H1800V2700H-700Z" fill="#9C6B43"/>')
    o.append(line([(-700, 1500), (1800, 1502)], 5, INK, taper=.05, wmin=.8, seed=420))
    # верхний шкафчик слева
    o.append(shape(rect_pts(-260, 120, 330, 470), "#D7E3D6", blob(rect_pts(30, 120, 340, 480), "#BCCDBD") +
                   line([(30, 130), (30, 460)], 4, INK, taper=.1, wmin=.8, seed=421), w=4.2, seed=422))
    for xx in (0, 60):
        o.append(shape(rrect_pts(xx - 8, 360, xx + 8, 420, 6), P.C_METAL, "", w=2.4, seed=423 + xx))
    o.append(kitchen_window(t, moon_u))
    return "".join(o)


def pendant_lamp(x, y, t, on=1.0):
    sw = 4 * math.sin(t * 1.3)
    o = [line([(x, -600), (x + sw * .3, y - 90)], 4, INK, taper=.05, wmin=.8, seed=430)]
    o.append(P.glow(x + sw, y + 60, 360, .5 * on, "#FFD98A"))
    o.append(shape([(x - 90 + sw, y), (x + 90 + sw, y), (x + 40 + sw, y - 90), (x - 40 + sw, y - 90)], P.C_LAMP,
                   blob(rect_pts(x + 20 + sw, y - 95, x + 100 + sw, y + 5), P.C_LAMP_SH), w=4.0, seed=431))
    o.append(blob(ellipse_pts(x + sw, y + 4, 40, 12, 12), "#FFF6D8"))
    return "".join(o)


def s04(t):
    lib.dyn_begin()
    a = A0("s04")
    t_g = ws(12)         # «глаза» — веки тяжелеют
    t_s = ws(13)         # «слипались» — голова соскальзывает
    t_d = ws(16)         # «десять» — луна встаёт
    heavy = ease_io(ramp(t, t_g - .05, .35))
    slip = bump(t, t_s + .02, .2, .14, .9)          # голова вниз с кулака и медленно назад
    jerk = bump(t, t_s + .34, .05, .18, .35)        # рывок — поймал себя
    moon_u = ease_out(ramp(t, t_d - .05, .9), 2)
    smile = ease_io(ramp(t, t_d + .1, .5))
    sc = .95
    hx, hy = 330, 1260
    sway = 6 * math.sin(t * 1.9)
    lean = .22 + .2 * slip - .12 * jerk
    head_add = .28 + .42 * slip - .32 * jerk + .02 * math.sin(t * 2.3)
    if jerk > .3:
        e = ex("nodjerk79")
    elif smile > .05:
        e = ex("doze79", lid=.1, mouth="smile", smile=.55 * smile)
    else:
        e = ex("doze79", lid=lerp(.42 + .06 * math.sin(t * 4), .06, heavy))
    feet = people.sit_kw(hx, hy, sc)["feet"]
    probe = people.dima(hx + sway * .3, hy, sc, ex("doze79"), lean_add=.22, head_add=.28, feet=feet, layers=("body",))
    fist = (probe["head"][0] + 40 * sc, probe["head"][1] + 200 * sc)        # ближний кулак под щекой, локоть на столе
    arms = {"n": ("ik", fist, -1), "f": ("ik", (hx + 290 * sc, hy - 185 * sc), -1)}
    hands = {"n": {"dir": (.1, -1), "curl": (.85, .85, .88, .88), "thumb": .75}, "f": {"dir": (1, .3), "curl": (.4, .4, .45, .5), "thumb": .4}}
    table_y = hy - 175 * sc
    o = [kitchen_bg(t, moon_u)]
    o.append(pendant_lamp(640, 520, t))
    # кот на подоконнике: зевает на «слипались», потом сонно моргает
    cy_ = 820 + 26
    yawn_c = bump(t, t_s - .2, .25, .5, .3)
    st = cat_state("yawn79") if yawn_c > .5 else {"look": (-.6, .3), "blink": .3 + .5 * ramp(t, t_d, .6), "tail": 6 * math.sin(t * 2)}
    st = dict(st)
    st["sy"] = 1 + .06 * yawn_c
    o.append(people.cat_svg(890, cy_, .42, st, t))
    # стул (за ним)
    o.append(shape(rect_pts(hx - 150 * sc, hy - 520 * sc, hx - 110 * sc, hy + 300 * sc), P.C_WOOD_SH, "", w=3.6, seed=440))
    o.append(shape(rect_pts(hx - 160 * sc, hy - 20 * sc, hx + 190 * sc, hy + 20 * sc), P.C_WOOD, "", w=3.6, seed=441))
    fig_b = people.dima(hx + sway * .3, hy, sc, e, lean_add=lean, head_add=head_add, feet=feet, arms=arms, hands=hands,
                        layers=("legs", "pelvis", "arm_f", "body"))
    fig_n = people.dima(hx + sway * .3, hy, sc, e, lean_add=lean, head_add=head_add, feet=feet, arms=arms, hands=hands, layers=("arm_n",))
    # стол: крышка от Димы вправо
    tx0, tx1 = hx + 120 * sc, 1200
    o.append(fig_b["svg"])
    o.append(shape(rect_pts(tx0, table_y, tx1, table_y + 34), P.C_WOOD, blob(rect_pts(tx0 - 10, table_y + 22, tx1 + 10, table_y + 40), P.C_WOOD_SH),
                   w=4.2, seed=450))
    o.append(shape(rect_pts(tx0 + 60, table_y + 34, tx0 + 96, 1560), P.C_WOOD_SH, "", w=3.6, seed=451))
    o.append(shape(rect_pts(tx1 - 140, table_y + 34, tx1 - 104, 1560), P.C_WOOD_SH, "", w=3.6, seed=452))
    o.append(P.plate_soup(hx + 470 * sc, table_y + 2, 1.0, steam=.35, t=t))
    o.append(P.cutlet_fork(hx + 640 * sc, table_y - 20, .55, rot=-70))
    o.append(P.cup_plain(hx + 760 * sc, table_y + 2, 1.0))
    o.append(fig_n["svg"])
    # камера: наезд к лицу + тряска-кивок на «слипались»
    s_ = 1.18 + .16 * ease_io(ramp(t, a, T1("s04") - a)) + .03 * jerk
    hd = probe["head"]
    cx = lerp(560, hd[0] + 160, ease_io(ramp(t, a, 2.0)))
    cy = lerp(900, hd[1] + 260, ease_io(ramp(t, a, 2.0)))
    shk = P.shake(t, t_s + .34, 12, .35, seed=44)
    over = light_rect(0, 0, 1080, 1920, "#FF9E4A", .06) + vignette("#2a1408", .4)
    return frame_svg("".join(o), cx - shk[0], cy - shk[1], s_, .4 * math.sin((t - a) * 1.1) - 1.2 * jerk, KIT_WALL, over)


SCENES["s04"] = s04


# ═══════════════════════════════ s08: день, солнце по дуге ═══════════════════════════════
OFF_WALL = "#DCE4EC"
OFF_WALL_SH = "#C3CEDA"


def sun_pos(u, x0=170, x1=930, ybase=640, h=430):
    """Солнце по дуге окна: u 0 — встаёт слева из-за крыш, 0.5 — в зените, 1 — садится справа."""
    x = lerp(x0, x1, u)
    y = ybase - h * math.sin(math.pi * clamp(u))
    return x, y


def office_window(t, su, x0=110, y0=110, x1=990, y1=700):
    o = []
    g = lib.lin_grad([(0, "#6FAEE6", 1), (.6, "#A9D3F2", 1), (1, "#E4F2F8", 1)], 0, 0, 0, 1)
    sky = f'<path d="M{x0} {y0}H{x1}V{y1}H{x0}Z" fill="url(#{g})"/>'
    sx, sy = sun_pos(su, x0 + 60, x1 - 60, y1 - 30, y1 - y0 - 150)
    # шлейф скорости за солнцем
    for j in range(1, 6):
        px, py = sun_pos(su - .035 * j, x0 + 60, x1 - 60, y1 - 30, y1 - y0 - 150)
        sky += blob(ellipse_pts(px, py, 62 - 7 * j, 62 - 7 * j, 18), "#FCE59A", .5 - .08 * j)
    sky += P.sun(sx, sy, 62, 1.0, t * 3, 0)
    for j, (cx_, cy_) in enumerate(((260, 230), (700, 300), (880, 190))):
        dx = ((cx_ + 260 * su * (1 + .3 * j)) - x0) % (x1 - x0 + 300) + x0 - 150
        sky += P.cloud(dx, cy_ + 40, 170, 80, seed=80 + j, col="#FFFFFF", ink_w=3.2)
    sky += roofs(x0 - 60, x1 + 60, y1 - 90, "#9BA9C2", 11, 150, "#DCE8F4")
    sky += roofs(x0 - 120, x1 + 60, y1 - 10, "#7E8CA8", 13, 120, "#C9D9EA")
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o.append(f'<g clip-path="url(#{c})">{sky}</g>')
    fr = "#F4F6F8"
    for r_ in (rect_pts(x0 - 24, y0 - 24, x1 + 24, y0), rect_pts(x0 - 24, y0, x0, y1), rect_pts(x1, y0, x1 + 24, y1),
               rect_pts((x0 + x1) / 2 - 10, y0, (x0 + x1) / 2 + 10, y1)):
        o.append(shape(r_, fr, "", w=3.4, seed=800 + int(r_[0][0])))
    o.append(shape(rect_pts(x0 - 44, y1, x1 + 44, y1 + 30), fr, blob(rect_pts(x0 - 50, y1 + 20, x1 + 50, y1 + 34), "#C9D2DC"), w=3.6, seed=805))
    return "".join(o), (sx, sy)


def cast(pts, ox, oy, sun, L, col="#5B6A82", op=.28):
    """Тень предмета на крышке: основание pts, отброшена от солнца на длину L."""
    dx, dy = ox - sun[0], 0.0
    n = math.hypot(dx, 1) or 1
    kx = dx / n * L
    sh = [(p[0], p[1]) for p in pts] + [(p[0] + kx, p[1] + 26) for p in reversed(pts)]
    return blob(sh, col, op)


def s08(t):
    lib.dyn_begin()
    a = A0("s08")
    t_v = ws(34)         # «Весь» — солнце взлетает
    t_j = ws(37)         # «жил» — Дима крупнее, тень крутится
    su = ease_in(ramp(t, t_v - .25, .45), 2) * .32 + .68 * ramp(t, t_v + .2, T1("s08") + .25 - t_v - .2) if t > t_v + .2 else \
        ease_in(ramp(t, t_v - .25, .45), 2) * .32
    su = clamp(su * 1.0)
    win, sun = office_window(t, su)
    o = [f'<path d="M-700 -600H1800V1640H-700Z" fill="{OFF_WALL}"/>', blob(rect_pts(-700, 1250, 1800, 1640), OFF_WALL_SH)]
    o.append(f'<path d="M-700 1640H1800V2700H-700Z" fill="#A3AEBB"/>')
    o.append(line([(-700, 1640), (1800, 1642)], 5, INK, taper=.05, wmin=.8, seed=810))
    o.append(win)
    # солнечный прямоугольник света на стене и полу едет против солнца
    lx = 540 - (sun[0] - 540) * .9
    o.append(blob([(lx - 300, 1640), (lx + 300, 1640), (lx + 380 - (sun[0] - 540) * .3, 2000), (lx - 380 - (sun[0] - 540) * .3, 2000)], "#FFF6D0", .45))
    sc = .9
    hx, hy = 290, 1330
    desk_y = hy - 180 * sc
    write = math.sin(t * 2 * math.pi * 2.6)
    lean = .2 + .04 * write * .3 + .06 * ease_out(ramp(t, t_j - .05, .2))
    head_add = .22 + .03 * math.sin(t * 5.2)
    feet = people.sit_kw(hx, hy, sc)["feet"]
    pen_t = (hx + 300 * sc + 14 * write, desk_y - 30 - 6 * abs(write))
    arms = {"n": ("ik", (pen_t[0] - 40, pen_t[1] + 6), -1), "f": ("ik", (hx + 220 * sc, desk_y - 10), -1)}
    hands = {"n": {"dir": (1, .55), "curl": (.6, .65, .7, .72), "thumb": .5}, "f": {"dir": (1, .25), "curl": (.2, .2, .25, .3), "thumb": .2}}
    e = ex("work79")
    # тень Димы на полу крутится вместе с солнцем
    ang = math.atan2(0, 1) + (sun[0] - 540) / 380 * 1.2
    fx, fy = hx + 120 * sc, 1660
    Ls = 520
    o.append(blob([(fx - 90, fy), (fx + 90, fy), (fx + 90 - Ls * math.sin(ang) + 60, fy + 120 - 30 * math.cos(ang)),
                   (fx - 90 - Ls * math.sin(ang) - 60, fy + 120 - 30 * math.cos(ang))], "#5B6A82", .22))
    # стул
    o.append(shape(rect_pts(hx - 150 * sc, hy - 520 * sc, hx - 110 * sc, hy + 300 * sc), "#59626F", "", w=3.6, seed=820))
    o.append(shape(rect_pts(hx - 160 * sc, hy - 20 * sc, hx + 190 * sc, hy + 20 * sc), "#6E7886", "", w=3.6, seed=821))
    fb = people.dima(hx, hy, sc, e, lean_add=lean, head_add=head_add, feet=feet, arms=arms, hands=hands, layers=("legs", "pelvis", "arm_f", "body"))
    fn = people.dima(hx, hy, sc, e, lean_add=lean, head_add=head_add, feet=feet, arms=arms, hands=hands, layers=("arm_n",))
    o.append(fb["svg"])
    tx0, tx1 = hx + 140 * sc, 1220
    o.append(shape(rect_pts(tx0, desk_y, tx1, desk_y + 34), P.C_DESK_WHITE, blob(rect_pts(tx0 - 10, desk_y + 22, tx1 + 10, desk_y + 40),
                                                                                      P.C_DESK_WHITE_SH), w=4.2, seed=830))
    o.append(shape(rect_pts(tx0 + 300, desk_y + 34, tx0 + 334, 1640), "#9AA3AE", "", w=3.6, seed=831))
    o.append(shape(rect_pts(tx1 - 120, desk_y + 34, tx1 - 86, 1640), "#9AA3AE", "", w=3.6, seed=832))
    # предметы и их метущие тени
    items = [(790, P.folder_stack(790, desk_y + 2, .95, n=5, seed=2), 230), (1010, P.mug(1010, desk_y + 2, 1.25, col="blue"), 90),
             (pen_t[0] + 20, P.paper(pen_t[0] + 30, desk_y - 4, 1.0, rot=0, w=210, h=40, seed=3, kind="lines", sy=.35), 30)]
    for (ix, svg_i, hgt) in items:
        o.append(cast([(ix - 60, desk_y + 4), (ix + 60, desk_y + 4)], ix, desk_y, sun, hgt * 1.6))
    for (_, svg_i, _) in items:
        o.append(svg_i)
    o.append(P.pen(pen_t[0], pen_t[1] - 40, .7, rot=-30))
    o.append(fn["svg"])
    # камера: хлёст на входе, дрейф вслед солнцу; на «жил» — к Диме
    jx = ease_io(ramp(t, t_j - .1, .5))
    cx = lerp(600 + (sun[0] - 540) * .12, 520, jx) - whip_in(t, T0("s08"), 360, .3)
    cy = lerp(860, 940, jx)
    s_ = lerp(1.18, 1.34, jx) + .02 * ramp(t, a, 2)
    over = light_rect(0, 0, 1080, 1920, "#DDEBFF", .05) + vignette("#24324a", .25)
    return frame_svg("".join(o), cx, cy, s_, -.5 + .9 * jx, OFF_WALL, over)


SCENES["s08"] = s08


# ═══════════════════════════════ s10: пыльная гитара, пробег ═══════════════════════════════
HALL_WALL = "#E9DCC2"
HALL_WALL_L = "#D6C6A6"
HALL_FLOOR = "#B58A5C"
DOOR_X0, DOOR_X1, DOOR_Y0, FLOOR_Y = 700, 990, 470, 1600


def hall_bg(t):
    o = [f'<path d="M-700 -600H1800V{FLOOR_Y}H-700Z" fill="{HALL_WALL}"/>']
    o.append(blob([(-700, -600), (120, -600), (120, FLOOR_Y + 40), (-700, FLOOR_Y + 300)], HALL_WALL_L))       # левая стена угла
    o.append(line([(120, -600), (120, FLOOR_Y + 40)], 4.5, INK, taper=.05, wmin=.8, seed=1001))
    o.append(f'<path d="M-700 {FLOOR_Y}H1800V2700H-700Z" fill="{HALL_FLOOR}"/>')
    for j in range(7):
        y = FLOOR_Y + 70 * j * (1 + .25 * j)
        o.append(line([(-700, y), (1800, y)], 3, "#8E6640", taper=.05, wmin=.8, seed=1002 + j, op=.7))
    o.append(line([(120, FLOOR_Y + 40), (1800, FLOOR_Y)], 5, INK, taper=.05, wmin=.8, seed=1010))
    # плинтус
    o.append(blob(rect_pts(120, FLOOR_Y - 26, 1800, FLOOR_Y), "#F3EBDA"))
    # дверной проём: тёмный коридор
    o.append(shape(rect_pts(DOOR_X0, DOOR_Y0, DOOR_X1, FLOOR_Y), "#6E5A48", blob(rect_pts(DOOR_X0, DOOR_Y0, DOOR_X1, DOOR_Y0 + 90), "#5A4838"),
                   w=4.0, seed=1011))
    # картина-домик и вешалка — бытовые детали
    o.append(shape(rect_pts(300, 360, 520, 540), "#F7F1E3", P.house(410, 520, .55, warm=.8, seed=3), w=4.0, seed=1012))
    o.append(shape(rect_pts(292, 352, 528, 548), "none", "", w=6.0, seed=1013))
    return "".join(o)


def door_front(t, close_u, rattle=0.0, jamb=True):
    """Наличник и полотно двери: close_u 0 — распахнута к стене (узкая полоса), 1 — закрыта."""
    o = []
    u = clamp(close_u)
    xr = lerp(DOOR_X0 + 40, DOOR_X1, u) + rattle
    if u > .02:
        o.append(shape([(DOOR_X0, DOOR_Y0 + 6, 1), (xr, DOOR_Y0 + 6 - 40 * (1 - u), 1), (xr, FLOOR_Y + 30 * (1 - u), 1), (DOOR_X0, FLOOR_Y, 1)], "#C99A6B",
                       blob(rect_pts(DOOR_X0, DOOR_Y0, DOOR_X0 + 30, FLOOR_Y), "#A87A4E"), w=4.2, seed=1020))
        if u > .6:
            kx = lerp(DOOR_X0, xr, .86)
            o.append(shape(ellipse_pts(kx, (DOOR_Y0 + FLOOR_Y) / 2 + 60, 14, 14, 10), P.C_METAL, "", w=2.6, seed=1021))
    if jamb:
        o.append(door_jamb())
    return "".join(o)


def door_jamb():
    o = []
    for r_ in (rect_pts(DOOR_X0 - 34, DOOR_Y0 - 34, DOOR_X1 + 34, DOOR_Y0), rect_pts(DOOR_X0 - 34, DOOR_Y0, DOOR_X0, FLOOR_Y),
               rect_pts(DOOR_X1, DOOR_Y0, DOOR_X1 + 34, FLOOR_Y)):
        o.append(shape(r_, "#F3EBDA", "", w=3.6, seed=1022 + int(r_[0][0]) % 7))
    return "".join(o)


def guitar_stand(x, y):
    return (line([(x - 70, y), (x, y - 120), (x + 70, y)], 9, "#3A3D44", taper=.05, wmin=.8, seed=1030) +
            line([(x - 40, y - 60), (x + 40, y - 60)], 7, "#3A3D44", taper=.05, wmin=.8, seed=1031))


def s10(t):
    lib.dyn_begin()
    a = A0("s10")
    t_n = ws(44)         # «ни» — пробег
    t_m = ws(45)         # «минуты» — пыль взвихривается
    t_s = ws(47)         # «себя» — оглянулся
    t_go = t_s + .3      # убегает
    t_slam = t_go + .32
    sc = .86
    o = [hall_bg(t)]
    # луч света из окна слева сверху на гитару
    o.append(blob([(-200, -100, 1), (60, -100, 1), (700, FLOOR_Y, 1), (200, FLOOR_Y, 1)], "#FFF4D2", .3))
    gx, gy = 300, 1560
    o.append(door_jamb())
    o.append(shadow(gx + 30, gy + 6, 200, .2))
    jingle = bump(t, t_slam, .03, .08, .5)
    o.append(guitar_stand(gx, gy))
    g_rot = -6 + 2.5 * jingle * math.sin(t * 40) + 1.6 * bump(t, t_n + .12, .08, .05, .4) * math.sin(t * 30)
    o.append(P.guitar(gx, gy - 20, 1.3, rot=g_rot, dust_u=1.0, strum=.5 * jingle, t=t))
    swirl = bump(t, t_m - .1, .18, .25, .55)
    o.append(P.dust_motes(gx + 10, gy - 560, 1.3, t=t, u=1.0, swirl=swirl, n=30, w=340, h=640))
    # Дима
    hip_y = FLOOR_Y - (people.LEG_LEN - 12) * sc * people.HEIGHT["dima"] - 10
    run_end = t_n + .5
    over_wall = ""
    if t < run_end:
        u = ramp(t, t_n - .22, run_end - t_n + .22)
        x = lerp(-380, 860, ease_out(u, 1.6))
        smear = clamp(1.4 - u * 1.2)
        fol_c = (x + 175 * sc, hip_y - 215 * sc)
        fol = P.folder_stack(fol_c[0], fol_c[1] + 50, .8, n=3, seed=5)
        fig = people.dima_run79(x, hip_y, sc, t, smear=smear, carry=fol)
        o.append(fig["svg"])
        if smear > .1:
            for j in range(4):
                yy = hip_y - 500 * sc + 160 * j * sc
                o.append(line([(x - 220 - 260 * smear, yy), (x - 160, yy + 4)], 7 * smear, INK, taper=.6, wmin=.1, seed=1040 + j, op=.6 * smear))
    else:
        # стоит у двери, разворот через «тонкий» кадр, оглядывается на гитару, потом убегает в проём
        turn1 = ramp(t, t_s - .1, .12)
        turn2 = ramp(t, t_go, .1)
        sx = math.cos(math.pi * turn1) if turn2 <= 0 else -math.cos(math.pi * turn2)
        if turn1 <= 0:
            sx = 1.0
        go = ease_in(ramp(t, t_go + .05, .3), 2)
        x = lerp(860, 1060, go)
        y_ = hip_y - 40 * go
        k_ = sc * (1 - .1 * go)
        settle = P.squash(t, run_end, .1, 3.0, 8.0)
        e = "look_back79" if sx < 0 else ("run79" if go > 0 else "yes79")
        fol_c = (x + 175 * k_, y_ - 215 * k_)
        fol = P.folder_stack(fol_c[0], fol_c[1] + 50, .8, n=3, seed=5)
        if go > 0:
            fig = people.dima_run79(x, y_, k_, t, smear=.3 * go, carry=fol)
        else:
            fig = people.dima_hold79(x, y_, k_, e, center=fol_c, held_svg=fol, width=200, sit=False, lean_add=.05 + .12 * (sx < 0))
        sxx = max(.08, abs(sx)) * (1 if sx >= 0 else -1) * settle[0]
        o.append(f'<g transform="translate({x:.1f} {FLOOR_Y}) scale({sxx:.4f} {settle[1]:.4f}) translate({-x:.1f} {-FLOOR_Y})">{fig["svg"]}</g>')
        if go > 0:
            over_wall = blob(rect_pts(DOOR_X1 + 34, -600, 1800, FLOOR_Y), HALL_WALL) + line([(DOOR_X1 + 34, FLOOR_Y), (1800, FLOOR_Y)], 5, INK,
                                                                                             taper=.05, wmin=.8, seed=1050)
    o.append(over_wall)
    close_u = ease_in(ramp(t, t_slam - .16, .16), 2)
    rattle = 6 * bump(t, t_slam, .02, .04, .25) * math.sin(t * 70)
    o.append(door_front(t, close_u, rattle, jamb=bool(over_wall) or t > t_slam - .2))
    if t > t_slam:
        o.append(P.dust_puff(DOOR_X1 - 40, FLOOR_Y - 10, 1.1, u=ramp(t, t_slam, .5), seed=7))
        o.append(P.speed_arcs(DOOR_X1 + 50, 900, 1.2, u=1 - ramp(t, t_slam, .3), t=t, seed=3, n=3, ang=0))
    # звон гитары — тонкие дуги от струн
    if jingle > .05:
        hx_, hy_ = P.guitar_pt(gx, gy - 20, 1.3, g_rot, "hole")
        for j in range(3):
            r_ = 110 + 40 * j + 50 * ramp(t, t_slam, .5)
            o.append(line(P._ring_pts(hx_, hy_, r_, r_, -40, 40, 10), 6 * jingle, INK, taper=.6, wmin=.1, seed=1060 + j, op=.7 * jingle))
    # камера: точка у гитары с микродрейфом, рывок вслед пробегающему
    follow = bump(t, t_n - .05, .25, .1, .5)
    cx = 520 + 140 * follow + 6 * math.sin((t - a) * 1.7)
    cy = 960 + 4 * math.cos((t - a) * 1.3)
    s_ = 1.0 + .03 * ramp(t, a, 2) + .02 * follow
    shk = P.shake(t, t_slam, 10, .3, seed=10)
    over = light_rect(0, 0, 1080, 1920, "#FFE3B0", .05) + vignette("#3a2a18", .3)
    return frame_svg("".join(o), cx - shk[0], cy - shk[1], s_, .8 * follow - .3, HALL_WALL, over)


SCENES["s10"] = s10


# ═══════════════════════════════ мансарда: общее для s11 и s14 ═══════════════════════════════
import room  # noqa: E402

PH_BLUE = "#7FB4FF"


def arm_hand(wrist, d, k, curl=(0, .1, .2, .25), thumb=.3, spread=.15, elbow_back=420.0, w_sleeve=86.0, seed=7900, blue=1.0):
    """Предплечье в рукаве худи (рукав не толще предплечья) + кисть: wrist — запястье, d — направление пальцев (мир), k — масштаб кисти
    (1 — голова 300). Локоть — назад по оси на elbow_back·k. Свет экрана снизу — голубой отсвет на коже и рукаве."""
    dx, dy = d
    L = math.hypot(dx, dy) or 1.0
    dx, dy = dx / L, dy / L
    nx, ny = -dy, dx
    el = (wrist[0] - dx * elbow_back * k + nx * 16 * k, wrist[1] - dy * elbow_back * k + ny * 16 * k)
    mid = ((el[0] + wrist[0]) / 2 + nx * 6 * k, (el[1] + wrist[1]) / 2 + ny * 6 * k)
    C = people.PAL["dima"]
    sl = lib.band([el, mid, (wrist[0] - dx * 18 * k, wrist[1] - dy * 18 * k)], w_sleeve * k, w_sleeve * .86 * k)
    inner = blob(lib.band([(el[0] + nx * 22 * k, el[1] + ny * 22 * k), (wrist[0] - dx * 18 * k + nx * 20 * k, wrist[1] - dy * 18 * k + ny * 20 * k)],
                          30 * k, 26 * k), C["TOP_SH"], .9)
    inner += line([(mid[0] - nx * 10 * k, mid[1] - ny * 10 * k), (mid[0] + dx * 30 * k - nx * 26 * k, mid[1] + dy * 30 * k - ny * 26 * k)],
                  3.2 * k, C["FOLD"], taper=.5, wmin=.2, seed=seed + 1, op=.7)
    o = [shape(sl, C["TOP"], inner, w=4.0 * k, seed=seed)]
    cuff = lib.band([(wrist[0] - dx * 34 * k, wrist[1] - dy * 34 * k), (wrist[0] - dx * 10 * k, wrist[1] - dy * 10 * k)], w_sleeve * .9 * k, w_sleeve * .88 * k)
    o.append(shape(cuff, C["TOP_SH"], "".join(line([(wrist[0] - dx * (32 - 5 * j) * k + nx * 36 * k, wrist[1] - dy * (32 - 5 * j) * k + ny * 36 * k),
                                                      (wrist[0] - dx * (32 - 5 * j) * k - nx * 36 * k, wrist[1] - dy * (32 - 5 * j) * k - ny * 36 * k)],
                                                     1.6 * k, C["FOLD"], taper=.1, wmin=.6, seed=seed + 10 + j, op=.6) for j in range(5)),
                   w=3.4 * k, seed=seed + 2))
    o.append(people.hand_svg("dima", wrist, (dx, dy), k=k, curl=curl, thumb=thumb, spread=spread, seed=seed + 3))
    return "".join(o)


def phone_light_from(x, y, r, u=1.0):
    g = lib.rad_grad([(0, PH_BLUE, .38 * u), (.6, PH_BLUE, .12 * u), (1, PH_BLUE, 0)], x, y, r)
    return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" fill="url(#{g})"/>'


def sleepy_sky_overlay(t, u):
    """Сонная луна в колпаке в люке (поверх неба «empty»), со звёздами; u — проявление (качнулась в люк)."""
    box = room.AT_SKY
    cid = lib.clip_of([(x, y, 1) for x, y in box])
    o = []
    for j in range(9):
        sx = 670 + 40 * j + 10 * math.sin(j * 3.1)
        sy = 500 + 34 * ((j * 5) % 7) + .2 * (sx - 660)
        o.append(P.star4(sx, sy, 7 + 2 * math.sin(t * 3 + j), .5 + .5 * math.sin(t * 2.2 + j)))
    if u > .01:
        mx = 850 + 8 * math.sin(t * 1.4)
        my = lerp(900, 640, ease_out(u, 2.4)) + 4 * math.sin(t * 2.0)
        o.append(P.moon_cap(mx, my, 58, t=t, mood="sleepy"))
    return f'<g clip-path="url(#{cid})">{"".join(o)}</g>'


# ═══════════════════════════════ s11: часы крупно, сектор отклеивается ═══════════════════════════════
def s11(t):
    lib.dyn_begin()
    a = A0("s11")
    t_n = ws(49)         # «ночью» — сонная луна в люке
    t_m = ws(50)         # «мозг» — рука тянется
    t_o = ws(51)         # «отбирает» — отклеивает и тянет вниз
    cx0, cy0, R = room.AT_CLOCK
    push = ease_io(ramp(t, t_n + .15, t_m - t_n + .05))
    s_ = lerp(1.0, 3.3, push) + .04 * ramp(t, a, 1.0)
    lib.INK_K[0] = 1.0 / (1 + .55 * (s_ - 1))
    at = room.attic(t, "night_phone", sky="empty")
    sector_u = ease_out(ramp(t, a, .7), 2)
    peel = ease_io(ramp(t, t_o, .38))
    pull_dir = (.22, 1.0)
    away = ease_in(ramp(t, t_o + .38, .55), 2)
    # стрелки медленно тикают около «без десяти три»
    hm = 2 + 50 / 60 + (t - a) * .01
    ha, ma = hm * 30, (hm % 1) * 360 + 6 * math.floor((t - a) * 2) * .0
    o = [at["bg"], at["sky"], sleepy_sky_overlay(t, ease_out(ramp(t, t_n - .25, .5))), at["frame"]]
    # рука: вход снизу к кончику сектора, щипок, отрыв вниз (загиб тёплой стороной едет с рукой)
    reach = ease_out(ramp(t, t_m - .1, t_o - t_m + .1), 2.4)
    off = (30 * away, 520 * away)
    kw = dict(blur=0.0, sector_u=sector_u, peel_u=peel, t=t, pull=pull_dir, flap_off=off)
    o.append(P.attic_clock(cx0, cy0, R, ha, ma, **kw))
    tip = P.sector_peel_tip(cx0, cy0, R, peel, pull_dir)
    kh = .45
    tip = (tip[0] + off[0], tip[1] + off[1])
    start = (cx0 + R * 1.3, cy0 + R * 3.2)
    tgt = (lerp(start[0], tip[0], reach), lerp(start[1], tip[1], reach))
    d = (-.42 + .15 * peel, -1.0)
    dn = math.hypot(*d)
    wr = (tgt[0] - d[0] / dn * 120 * kh - 20 * kh, tgt[1] - d[1] / dn * 120 * kh)
    if reach > .01:
        o.append(arm_hand(wr, d, kh, curl=(.35 + .2 * peel, .45, .55, .6), thumb=.75, spread=.08, elbow_back=520, seed=7951))
    o.append(at["bed"])
    o.append(phone_light_from(cx0 + 60, cy0 + R * 1.9, R * 2.2, .9))
    o.append(at["light"])
    o.append(at["shade"])
    hd = .0
    cy = lerp(cy0 + 120, cy0 + 70, push) + 70 * away / s_ * 3
    cx = lerp(545, cx0 + 8, push)
    shk = P.shake(t, t_o, 7, .25, seed=11)
    out = frame_svg("".join(o), cx - shk[0] / s_, cy - shk[1] / s_ + hd, s_, .5 * math.sin((t - a) * 1.2) * (1 - push) + 1.2 * away, "#1a1f3d")
    lib.INK_K[0] = 1.0
    return out


SCENES["s11"] = s11


# ═══════════════════════════════ s14: подушка-сон на полке, три щелчка ═══════════════════════════════
def s14(t):
    lib.dyn_begin()
    a = A0("s14")
    sx0, sy, sx1 = room.AT_SHELF
    f1, f2, f3 = ws(65), wm(65), ws(66)
    lib.INK_K[0] = .72
    at = room.attic(t, "night_phone", sky="empty")
    # позиция подушки: три толчка с трением
    xs = [sx0 + 120, sx0 + 205, sx0 + 290, sx1 - 4]

    def pos(tt):
        x_ = xs[0]
        for i, tf in enumerate((f1, f2, f3)):
            u = ease_out(ramp(tt, tf + .03, .3 if i < 2 else .45), 2.6)
            x_ += (xs[i + 1] - xs[i]) * u
        return x_
    px = pos(t)
    plag = pos(t - .22)
    hang = ease_out(ramp(t, f3 + .3, .4), 2)
    squash = 0.0
    for tf in (f1, f2, f3):
        q = P.squash(t, tf + .02, .3, 3.0, 8.0)
        squash += (q[0] - 1) * 1.6
    tilt = 14 * hang
    mood = "sad" if t > f3 + .15 else "calm"
    o = [at["bg"], at["sky"], at["frame"]]
    o.append(P.sleep_pillow(px, sy + 2 + 14 * hang, .95, squash=squash, mood=mood, t=t, tilt=tilt, hang=hang, breathe=1.0))
    if t < f3 + .2:
        o.append(P.zzz(px + 80, sy - 260, .9, t=t, u=1.0 - ramp(t, f1, .2) * .5))
    # палец слева: подлетает к подушке перед каждым щелчком, щёлкает (указательный распрямляется), отходит
    kh = .62
    hand_x = plag - 150 - 10 * math.sin(t * 2.0) - 60 * (1 - ease_out(ramp(t, a, .5), 2))
    flick = 0.0
    for tf in (f1, f2, f3):
        flick = max(flick, bump(t, tf - .12, .1, .0, .14))
    snap = 0.0
    for tf in (f1, f2, f3):
        snap = max(snap, bump(t, tf, .04, .02, .2))
    wr = (hand_x - 70 + 34 * flick - 10 * snap, sy - 64 + 6 * math.sin(t * 3))
    d = (1.0, .02)
    curl_i = .75 * (1 - snap) * flick + .1
    o.append(arm_hand(wr, d, kh, curl=(curl_i, .82, .86, .88), thumb=.85 - .3 * snap, spread=.05, elbow_back=560, seed=7961))
    for tf in (f1, f2, f3):
        u = clamp((t - tf) / .3)
        if 0 < u < 1:
            o.append(P.click(px - 128, sy - 70, 1.0, u, seed=int(tf * 10)))
    o.append(phone_light_from(px - 260, sy + 160, 520, 1.0))
    o.append(at["light"])
    cx = pos(t - .12) - 40 + 90 * ease_io(ramp(t, f3 + .2, .5))
    cy = sy - 10 + 6 * math.sin((t - a) * 1.6)
    s_ = 2.6 + .08 * ramp(t, a, 1.5)
    shk = P.shake(t, f3 + .02, 6, .25, seed=14)
    out = frame_svg("".join(o), cx - shk[0] / s_, cy - shk[1] / s_, s_, .4 * math.sin((t - a) * 1.3), "#1a1f3d", vignette("#05081a", .45))
    lib.INK_K[0] = 1.0
    return out


SCENES["s14"] = s14


def frame(sid, t):
    return SCENES[sid](t)
