"""Рилс 60 «темнота», группа A: ночная детская и палатка из одеяла.
s01 (0–1.5) хук: ночная детская, бугор-палатка из одеяла, в проёме маленький Дима с книгой и фонариком; «читать» (0.94) луч дёрнулся; влёт.
s04 (4.9–6.4) внутри палатки крупно: «фонариком» (5.00) щёлк, тёплый конус на странице и носу; «мама» (5.82) тень мамы на одеяле, Дима замер.
s18 (30.2–32.1) финал как кадр хука: та же палатка, камера откатывает, мама заглядывает в дверь и улыбается; «одеялом» (31.41) луч мигает.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Люди и предметы — common/ (people, props)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props  # noqa: E402
from lib import (blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, lin_grad, rect_pts, shape, smooth, svg, back_out,
                 rrect, blur)  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
T = {i: w["start"] for i, w in enumerate(WORDS)}
INK = lib.INK


def lerp(a, b, u):
    return a + (b - a) * u


def bump(t, t0, dur):
    """0 → 1 → 0 импульс от t0 длиной dur (затухающий)."""
    if t < t0:
        return 0.0
    return math.exp(-(t - t0) / dur * 3.0)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(.6, s) ** .55


# ───────────────────────── комната ─────────────────────────
FLOOR = 1450.0
BED_X, BED_Y, BED_K = 610.0, 1430.0, 1.25
MAT = BED_Y - 118 * BED_K          # верх матраса 1282.5
DOOR = (70.0, 560.0, 300.0, FLOOR)  # x0 y0 x1 y1 проёма
TX, TW, TH = 650.0, 700.0, 480.0    # палатка: центр, ширина, высота
OPEN = (470.0, 850.0, 880.0)        # проём палатки: x0, x1, верх


def door(open_u, light_u):
    x0, y0, x1, y1 = DOOR
    o = []
    # наличник
    o.append(shape(rect_pts(x0 - 26, y0 - 26, x1 + 26, y1), "#D9CDB4", blob(rect_pts(x1 + 10, y0 - 26, x1 + 26, y1), "#B9AC90"), w=4.0, seed=8101))
    # проём: коридор (тёплый свет) — сплошной цвет, свет добавит glow
    hall = lin_grad([(0, mix("#3A3550", "#F2C977", light_u), 1), (1, mix("#2C2840", "#D99A55", light_u), 1)], 0, 0, 0, 1)
    o.append(shape(rect_pts(x0, y0, x1, y1), "#3A3550", f'<path d="M{f(x0 - 5)} {f(y0 - 5)}H{f(x1 + 5)}V{f(y1 + 5)}H{f(x0 - 5)}Z" fill="url(#{hall})"/>'
                   + blob(rect_pts(x0, y1 - 160, x1, y1), mix("#2C2840", "#C98B4E", light_u)), w=3.6, seed=8102))
    # створка: открывается внутрь комнаты (поворачивается к зрителю — сужается к левому краю)
    wd = (x1 - x0) * (1 - .82 * open_u)
    leaf = [(x0, y0 + 4, 1), (x0 + wd, y0 + 4 - 18 * open_u), (x0 + wd, y1 + 10 * open_u), (x0, y1, 1)]
    inner = blob([(x0 + wd * .14, y0 + 60), (x0 + wd * .86, y0 + 56), (x0 + wd * .86, y0 + 380), (x0 + wd * .14, y0 + 384)], "#8E6A48", .9)
    inner += blob([(x0 + wd * .14, y0 + 470), (x0 + wd * .86, y0 + 466), (x0 + wd * .86, y1 - 70), (x0 + wd * .14, y1 - 66)], "#8E6A48", .9)
    o.append(shape(leaf, "#A97E57", inner, w=4.2, seed=8103))
    hx = x0 + wd * .86
    o.append(shape(ellipse_pts(hx, y0 + 450, 10, 10, 10), "#E0C27A", "", w=2.6, seed=8104))
    return "".join(o)


def room_bg(t):
    o = []
    o.append(blob(rect_pts(-600, -400, 1700, FLOOR), props.C_NIGHT_WALL))
    # обои: ряды мелких звёздочек-штрихов (без букв), чуть светлее стены
    for j in range(9):
        for i in range(10):
            x = -180 + i * 150 + (j % 2) * 75
            y = 80 + j * 150
            o.append(line([(x - 9, y), (x + 9, y)], 3, "#2C3262", taper=.2, wmin=.6, seed=8000 + i + j * 10))
            o.append(line([(x, y - 9), (x, y + 9)], 3, "#2C3262", taper=.2, wmin=.6, seed=8100 + i + j * 10))
    o.append(blob(rect_pts(-600, FLOOR - 26, 1700, FLOOR), "#1A1E40"))           # плинтус
    o.append(line([(-600, FLOOR - 26), (1700, FLOOR - 26)], 3.2, seed=8201))
    o.append(blob(rect_pts(-600, FLOOR, 1700, 2400), props.C_NIGHT_FLOOR))
    for i in range(7):   # доски пола
        y = FLOOR + 50 + i * i * 14
        o.append(line([(-600, y), (1700, y + 4)], 3.0, "#10122A", taper=.2, wmin=.6, seed=8210 + i))
    # коврик
    o.append(shape(ellipse_pts(560, 1600, 420, 70, 26), "#3E4E86", blob(ellipse_pts(560, 1612, 360, 46, 22), "#33416F"), w=3.6, seed=8220))
    o.append(props.window(905, 830, 300, 380, "night", t, seed=3))
    # полка с игрушками (кубик, мяч) — без букв
    o.append(shape(rrect(380, 640, 700, 662, 4), props.C_WOOD, "", w=3.2, seed=8230))
    o.append(shape(rrect(420, 572, 488, 640, 6), "#D9483B", blob(rect_pts(420, 620, 488, 640), "#A5322A"), w=3.2, seed=8231))
    o.append(shape(ellipse_pts(540, 610, 30, 30, 18), "#F4C24A", line([(512, 600), (568, 616)], 4, "#C99726", seed=8233), w=3.2, seed=8232))
    o.append(shape(rrect(596, 540, 626, 640, 4), "#5C9A78", "", w=3.0, seed=8234))
    o.append(shape(rrect(630, 556, 660, 640, 4), "#3F6FB0", "", w=3.0, seed=8235))
    # тапочки
    o.append(shape(ellipse_pts(330, 1488, 44, 15, 14), "#6E92C9", "", w=3.0, seed=8240))
    o.append(shape(ellipse_pts(400, 1500, 44, 15, 14), "#6E92C9", "", w=3.0, seed=8241))
    return "".join(o)


def bed_back():
    o = [props.bed(BED_X, BED_Y, BED_K, seed=4)]
    o.append(props.pillow(BED_X - 255, MAT + 4, .9, -6, seed=2))
    return "".join(o)


# ───────────────────────── палатка из одеяла с Димой ─────────────────────────
def tent_outer(t, breathe):
    """Купол одеяла (лоскутное, оранжевое), низ — по матрасу; свисает за край кровати."""
    x, y, w, h = TX, MAT + 6, TW, TH * (1 + .012 * breathe)
    pts = [(x - w * .62, y + 70, 1), (x - w * .55, y - h * .22), (x - w * .46, y - h * .62), (x - w * .3, y - h * .9), (x - w * .06, y - h),
           (x + w * .2, y - h * .95), (x + w * .38, y - h * .72), (x + w * .5, y - h * .36), (x + w * .6, y + 4), (x + w * .64, y + 80, 1)]
    inner = blob([(x - w, y - h * .2), (x + w, y - h * .2), (x + w, y + 120), (x - w, y + 120)], props.C_QUILT_SH, .9)
    inner += blob([(x - w * .5, y - h * .3), (x - w * .4, y - h * .74), (x - w * .22, y - h * .92), (x - w * .3, y - h * .55), (x - w * .44, y - h * .18)],
                  props.C_QUILT_HI)
    for i in range(6):   # лоскуты-стёжка
        xx = x - w * .5 + w * .2 * i
        inner += line([(xx, y + 60), (xx + 10, y - h * (.6 + .08 * (i % 3)))], 3.2, props.C_QUILT_SH, taper=.3, wmin=.6, seed=8300 + i)
    for j in range(3):
        yy = y - h * (.25 + .25 * j)
        inner += line([(x - w * .55, yy + 20), (x, yy - 16), (x + w * .5, yy + 22)], 3.0, props.C_QUILT_SH, taper=.3, wmin=.6, seed=8310 + j)
    for i in range(5):   # светлые полосы узора
        xx = x - w * .42 + w * .17 * i
        inner += line([(xx, y - h * .05), (xx + 8, y - h * (.55 + .06 * (i % 2)))], 8, props.C_QUILT_ST, taper=.2, wmin=.7, seed=8320 + i)
    return shape(pts, props.C_QUILT, inner, w=5.0, seed=8330)


def open_pts(breathe=0.0):
    x0, x1, top = OPEN
    yb = MAT + 2
    cx = (x0 + x1) / 2
    pts = [(x0, yb, 1)]
    for k in range(1, 12):
        a = math.pi * k / 12
        pts.append((cx - (x1 - x0) / 2 * math.cos(a), yb - (yb - top - 6 * breathe) * math.sin(a) ** .8))
    pts.append((x1, yb, 1))
    return pts


def tent_hole(breathe):
    """Тёмная внутренность палатки в проёме."""
    x0, x1, top = OPEN
    g = rad_grad([(0, "#7A3A33", 1), (.6, "#4A2128", 1), (1, "#2A1420", 1)], (x0 + x1) / 2, MAT - 120, 260, 300)
    return f'<path d="{lib.fill_d(open_pts(breathe))}" fill="url(#{g})"/>'


def tent_rim(breathe):
    """Край проёма: толстая складка одеяла поверх Димы (сверху над головой и по бокам) + складка на коленях."""
    pts = open_pts(breathe)
    rim = lib.band([(p[0], p[1]) for p in pts], 34, 34, step=6, cap=True)
    inner = blob([(p[0], p[1] + 8) for p in pts[2:-2]] + [(pts[-3][0], pts[-3][1] + 30), (pts[2][0], pts[2][1] + 30)], props.C_QUILT_SH, .5)
    o = shape(rim, props.C_QUILT_HI, inner, w=4.4, seed=8340)
    # складка одеяла на коленях — поперёк низа проёма
    x0, x1, _ = OPEN
    lap = [(x0 - 40, MAT + 30, 1), (x0 - 20, MAT - 30), (x0 + 110, MAT - 48), (x0 + 230, MAT - 40), (x1 + 10, MAT - 28), (x1 + 40, MAT + 30, 1)]
    li = blob([(x0 - 40, MAT - 10), (x1 + 40, MAT - 10), (x1 + 40, MAT + 40), (x0 - 40, MAT + 40)], props.C_QUILT_SH, .9)
    li += line([(x0 + 40, MAT - 40), (x0 + 160, MAT - 30), (x0 + 280, MAT - 38)], 3, props.C_QUILT_SH, taper=.3, wmin=.6, seed=8342)
    o += shape(lap, props.C_QUILT, li, w=4.4, seed=8341)
    return o


def grip_on(who, Cp, R, ang_deg, k, side=1, seed=900, h=None):
    """Хват вокруг предмета, ось которого идёт под углом ang_deg (0 — вправо). Возвращает (back, front, wrist)."""
    back, front = people.grip_svg(who, (0.0, 0.0), R, side, k=k, h=h, seed=seed)
    rot = ang_deg - 90.0     # вертикаль хвата → ось предмета
    tr = f'translate({f(Cp[0])} {f(Cp[1])}) rotate({f(rot)})'
    a = math.radians(rot)
    wx, wy = side * (R + 46 * k), 0.0
    wr = (Cp[0] + wx * math.cos(a) - wy * math.sin(a), Cp[1] + wx * math.sin(a) + wy * math.cos(a))
    return f'<g transform="{tr}">{back}</g>', f'<g transform="{tr}">{front}</g>', wr


KID_HIP = (596.0, 1330.0)
KID_SCALE = .8


def kid_in_tent(t, expr, fl_ang, fl_on, flip_u, sway=0.0, nod=0.0):
    """Дима в проёме палатки. Возвращает (svg, точки света: линза, направление, лицо, книга)."""
    sc = KID_SCALE * people.HEIGHT["kid"]
    book_c = (770.0 + 2 * sway, 1196.0 + 3 * math.sin(t * 3.1))
    bk, br = .92, -12.0
    book = props.book_open(book_c[0], book_c[1], bk, br, flip=flip_u, seed=1, cover=props.C_BLUE_COVER)
    # дальняя рука держит левую обложку (край книги, середина по высоте)
    a = math.radians(br)
    lx, ly = -104 * bk, -62 * bk
    bl = (book_c[0] + lx * math.cos(a) - ly * math.sin(a), book_c[1] + lx * math.sin(a) + ly * math.cos(a))
    fb, ff, fwr = grip_on("kid", bl, 9, 90 + br, sc * 1.05, side=-1, seed=930, h=64)
    # ближняя рука держит фонарик снизу, светит вверх на страницы
    F = (668.0 + 4 * sway, 1192.0 + 3 * math.sin(t * 6))
    fk = .7
    nb, nf, nwr = grip_on("kid", (F[0] - 22 * fk * math.cos(math.radians(fl_ang)), F[1] - 22 * fk * math.sin(math.radians(fl_ang))), 15 * fk,
                          fl_ang, sc * 1.05, side=-1, seed=950)
    fig = people.figure("kid", KID_HIP[0] + 3 * sway, KID_HIP[1], KID_SCALE, expr, lean=.12 + .02 * sway, head_ang=-.05 + nod,
                        arms={"f": ("ik", fwr, -1), "n": ("ik", nwr, -1)}, hands={"f": {"kind": "none"}, "n": {"kind": "none"}},
                        layers=("arm_f", "body", "arm_n"))
    a = math.radians(fl_ang)
    lens = (F[0] + 64 * fk * math.cos(a), F[1] + 64 * fk * math.sin(a))
    body = fig["svg"]
    # порядок: тело (дальняя рука под ним), книга, пальцы на книге, фонарик в ближней руке
    s = body + fb + book + ff + nb + props.flashlight(F[0], F[1], fk, fl_ang, fl_on) + nf
    return s, dict(lens=lens, ang=fl_ang, face=fig["head"], book=(book_c[0] + 20, book_c[1] - 60))


def kid_tent_scene(t, expr, fl_ang, fl_on, flip_u, sway=0.0, nod=0.0, breathe=0.0):
    hole = tent_hole(breathe)
    kid, L = kid_in_tent(t, expr, fl_ang, fl_on, flip_u, sway, nod)
    c = lib.clip_of(open_pts(breathe))
    inner = f'<g clip-path="url(#{c})">{kid}</g>'
    return tent_outer(t, breathe) + hole + inner + tent_rim(breathe), L


def night_light(L, fl_on, extra_holes=(), op=.66):
    """Вуаль ночи с дырами света + тёплые лучи поверх."""
    lx, ly = L["lens"]
    holes = [(props.cone_d(lx, ly, L["ang"], 240, 40, 12), .95 * fl_on),
             (props.circle_d(L["face"][0] + 20, L["face"][1] + 10, 150, 160), .75 * fl_on + .15),
             (props.circle_d((OPEN[0] + OPEN[1]) / 2, MAT - 150, 230, 210), .45 * fl_on + .1),
             (props.circle_d(905 - 300 * .28 + 0, 830 - 380 + 380 * .2, 110), .45)]
    holes += list(extra_holes)
    o = props.darkness(op, holes=holes, blur_sd=18, box=(-700, -500, 1800, 2500))
    o += props.beam(lx, ly, L["ang"], 240, 40, .9 * fl_on, k=.7)
    o += props.glow(L["book"][0], L["book"][1], 120, .55 * fl_on)
    o += props.glow(L["face"][0] + 30, L["face"][1] + 40, 170, .35 * fl_on)
    return o


def hook_cam(t, hit, base, cx, cy):
    """Влёт правил 28–29: 1/(1+0.4) → 1 за 0.22 с, перелёт 5 %, поворот −3,4° с возвратом, удар +9 % на ударном слоге, занос вбок."""
    u = clamp(t / .22)
    e = 1 - (1 - u) ** 3
    m = 1 / (1 + .42 * (1 - e))
    if t > .22:
        tt = t - .22
        m *= 1 + .055 * math.exp(-tt * 7) * math.sin(min(tt * 18, math.pi))
    rot = -3.4 * (1 - e) + .5 * math.sin(t * 5)
    cx += 46 * (1 - e)
    if t > hit:
        tt = t - hit
        m *= 1 + .09 * math.exp(-tt * 8)
        rot += 1.6 * math.exp(-tt * 9) * math.sin(tt * 38)
        cx += 7 * math.exp(-tt * 11) * math.sin(tt * 55)
        cy += 8 * math.exp(-tt * 11) * math.sin(tt * 47 + 1)
    return cx, cy, base * m, rot


def world_scene(t, expr, fl_ang, fl_on, flip_u, sway, nod, door_u=0.0, hall_u=0.0, mama=""):
    breathe = math.sin(t * 2.2)
    o = [room_bg(t), door(door_u, hall_u), mama, bed_back()]
    tent, L = kid_tent_scene(t, expr, fl_ang, fl_on, flip_u, sway, nod, breathe)
    o.append(tent)
    extra = []
    if hall_u > 0:
        x0, y0, x1, y1 = DOOR
        extra.append((f"M{f(x0)} {f(y0)}H{f(x1)}V{f(y1)}H{f(x0)}Z", .9 * hall_u))
        extra.append((f"M{f(x0)} {f(y1)}L{f(x1)} {f(y1)}L{f(x1 + 420)} {f(y1 + 300)}L{f(x0 + 60)} {f(y1 + 300)}Z", .6 * hall_u))
    o.append(night_light(L, fl_on, extra))
    if hall_u > 0:
        x0, y0, x1, y1 = DOOR
        o.append(props.glow((x0 + x1) / 2, y1 - 300, 330, .3 * hall_u, color="#FFD8A0", ry=480))
    return "".join(o), L


# ───────────────────────── s01 ─────────────────────────
HOOK_S, HOOK_C = 2.05, (660.0, 1105.0)
def frame01(t):
    T_GO, T_CH = T[0], T[2]           # 0.07 «Говорят», 0.94 «читать»
    # фонарик: качается в руке, на «читать» дёргается вверх и возвращается пружиной
    jerk = 0.0
    if t > T_CH:
        tt = t - T_CH
        jerk = -52 * math.sin(clamp(tt / .08) * math.pi / 2) if tt < .08 else -52 * math.exp(-(tt - .08) * 5.5) * math.cos((tt - .08) * 13)
    fl_ang = -38 + 5 * math.sin(t * 7.3) + jerk
    flick = 1.0 - .55 * bump(t, T_CH, .08)
    flip_u = clamp((t - .05) / .62)                     # страница перелистывается с кадра 0
    squint = smooth(T_CH, T_CH + .06, t) * (1 - smooth(T_CH + .3, T_CH + .5, t))
    expr = dict(mouth="grin" if squint < .5 else "wince", lid=.95 - .5 * squint, brows="up", look=(.75, .55 - .9 * squint), closed=.6 * squint,
                hair=.6 * math.sin(t * 9) * (1 - clamp(t)) + .5 * bump(t, T_CH, .2))
    sway = math.sin(t * 4.4)
    nod = .05 * math.sin(t * 6.5) - .08 * squint
    body, L = world_scene(t, expr, fl_ang, flick, flip_u, sway, nod)
    cx, cy, s, rot = hook_cam(t, T_CH, HOOK_S, HOOK_C[0], HOOK_C[1])
    set_ink(s)
    bl = 6.0 * (1 - clamp(t / .16))
    wrap = f'<g {blur(round(bl, 1))}>' if bl > .4 else "<g>"
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{wrap}{body}</g></g>'


# ───────────────────────── s18 ─────────────────────────
def mama_peek(t, u):
    """Мама в дверном проёме: улыбается, рука на косяке; u — насколько вошла в проём (0 — за косяком)."""
    x0, y0, x1, y1 = DOOR
    sc = .6
    hipx = lerp(x0 - 60, x0 + 120, ease_out(u, 2))
    hipy = y1 - 610 * sc * .92 - 6
    smile = smooth(.2, .7, u)
    expr = dict(mouth="smile", smile=.5 + .5 * smile, lid=.8, brows="up" if smile > .5 else "calm", look=(.9, .25), laugh=0.0, blush=.4)
    sk = sc * people.HEIGHT["mama"]
    feet = {"n": ((hipx + 50 * sk, y1 - 4), 0.0), "f": ((hipx - 40 * sk, y1 - 8), 0.0)}
    jamb = (x1 - 4, hipy - 40 * sk + 4 * math.sin(t * 3))
    fig = people.figure("mama", hipx, hipy, sc, expr, lean=.14 + .04 * math.sin(t * 2), head_ang=.1 + .03 * math.sin(t * 2.6), feet=feet,
                        arms={"f": ("ang", .1, .2), "n": ("ik", jamb, -1)},
                        hands={"n": {"kind": "open", "curl": (.55, .6, .6, .65), "thumb": .4, "dir": (0.35, 1.0)}})
    return fig["svg"]


def frame18(t):
    T_RU, T_OD = T[84], T[88]          # 30.2 «ругали», 31.41 «одеялом»
    u = clamp((t - 30.0) / 2.15)
    blink = 0.0
    for b0 in (T_OD, T_OD + .17):
        if b0 <= t < b0 + .09:
            blink = 1.0
    fl_on = 1.0 - .92 * blink
    fl_ang = -38 + 4 * math.sin(t * 5.1)
    flip_u = clamp((t - 30.5) / .7)
    expr = dict(mouth="smile", smile=.9, lid=.8, brows="calm", look=(.75, .55), closed=1.0 if 31.0 < t < 31.08 else 0.0)
    sway = math.sin(t * 3.4) * .6
    door_u = ease_out(clamp((t - 30.0) / .5), 2)
    hall_u = .5 + .5 * door_u
    mama = mama_peek(t, clamp((t - 30.1) / .9))
    body, L = world_scene(t, expr, fl_ang, fl_on, flip_u, sway, .03 * math.sin(t * 4), door_u=.55 + .45 * door_u, hall_u=hall_u, mama=mama)
    # откат: от кадра хука к общему плану с дверью
    e = ease_io(clamp((t - 30.05) / 1.7))
    s = lerp(HOOK_S, 1.17, e) * (1 + .03 * bump(t, T_OD, .25))
    cx = lerp(HOOK_C[0], 505, e) + 4 * math.sin(t * 1.7)
    cy = lerp(HOOK_C[1], 1075, e)
    rot = lerp(-.8, .4, e)
    set_ink(s)
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>'


# ───────────────────────── s04 ─────────────────────────
def frame04(t):
    return frame01(t - 4.7)


def frame(sid, t):
    lib.DEFS.clear()
    lib._uid[0] = 0
    body = {"s01": frame01, "s04": frame04, "s18": frame18}[sid](t)
    return svg(f'<rect width="1080" height="1920" fill="#0F1229"/>{body}')
