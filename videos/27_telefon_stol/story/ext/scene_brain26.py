"""Сцена brain рилса 26 (s07, s08): мозг рилсов 24/25 с ручками (scene_brain.py без изменений), без лица.
s07 «одного желания мало» (9.76–11.28): держит воздушный шарик с нарисованной кроссовкой, растерянно оглядывается
     (поворачивается то влево, то вправо, чешет макушку), на «мало» (10.64) разводит рукой.
s08 «точный момент, когда начинать» (11.28–13.88): перед ним будильник без стрелок, мозг поникший и серый; на «точный»
     (12.08) стрелки влетают и щёлкают на 7:00, на 12.45 (после «момент») загорается зелёная кнопка ▶ на подставке,
     мозг оживает: цвет возвращается, выпрямляется, вскидывает руки. Всё — функция общего времени ролика t."""
import math

import brain_art
import lib
import scene_brain as sb
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
CLICK = 12.08     # «точный»
GO = 12.45        # «момент» — кнопка
MALO = 10.64      # «мало»


class Pose(sb.Pose):
    """Pose рилса 25 + fx: зеркало по x (мозг смотрит вправо при fx < 0, лобная доля — вперёд)."""
    def __init__(self, x, y, sc=1.0, rot=0.0, sq=1.0, fx=1.0):
        super().__init__(x, y, sc, rot, sq)
        self.fx = fx

    def tf(self):
        return (f"translate({f(self.x)} {f(self.y)}) rotate({f(self.rot)}) scale({f(self.fx * self.sc / self.sq ** .5)} {f(self.sc * self.sq)}) "
                f"translate({-BCX} {-BCY})")

    def pt(self, lx, ly):
        x, y = (lx - BCX) * self.fx * self.sc / self.sq ** .5, (ly - BCY) * self.sc * self.sq
        a = math.radians(self.rot)
        return (self.x + x * math.cos(a) - y * math.sin(a), self.y + x * math.sin(a) + y * math.cos(a))


def body(pose, brain_svg, wl, wr, al, ar, cl, cr, bl=-40, br=40, sd=0, mid="", front=""):
    """Ручки от плеч (левое по экрану — к левой кисти), мозг, то, что держат, кисти."""
    a, b = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    SL, SR = (a, b) if a[0] <= b[0] else (b, a)
    s = [sb.arm(SL, wl, bl, sd + 1, pose.sc), sb.arm(SR, wr, br, sd + 2, pose.sc)]
    s.append(f'<g transform="{pose.tf()}">{brain_svg}</g>')
    s.append(mid)
    s.append(sb.toon_hand(wl[0], wl[1], al, cl, sd + 30, pose.sc * 1.3))
    s.append(sb.toon_hand(wr[0], wr[1], ar, cr, sd + 60, pose.sc * 1.3))
    s.append(front)
    return "".join(s)


def qmark(x, y, sc, op, sd):
    """Знак вопроса тушью (символ, не буква): крючок + точка."""
    if op <= 0.01 or sc <= 0.02:
        return ""
    hook = [(-22, -30), (-14, -50), (6, -56), (24, -44), (24, -24), (8, -10), (0, 4), (0, 18)]
    pts = [(x + px * sc, y + py * sc) for px, py in hook]
    s = line([(px + 3, py + 4) for px, py in pts], 15 * sc, "#0f1430", taper=.25, wmin=.6, seed=sd, op=.35 * op)
    s += line(pts, 13 * sc, "#ffe27a", taper=.25, wmin=.6, seed=sd, op=op)
    s += f'<circle cx="{f(x)}" cy="{f(y + 38 * sc)}" r="{f(8 * sc)}" fill="#ffe27a" opacity="{op:.3f}"/>'
    return s


# ───────────────────────── шарик с кроссовкой
def sneaker(sd=0):
    """Кроссовка сбоку, носок вправо, в своих координатах (~170 × 80), центр (0, 0)."""
    s = []
    upper = [(-82, 14), (-80, -18), (-64, -36), (-38, -40), (-26, -26), (-6, -18), (22, -12), (52, -4), (76, 4), (84, 16),
             (-82, 22)]
    inner = blob([(-82, 2), (84, 4), (84, 22), (-82, 22)], "#d9dde8", .9)
    inner += blob([(-30, -2), (10, -14), (60, 0), (40, 8), (0, 2)], "#3d7fe0")          # полоса на боку
    inner += blob([(-82, -10), (-64, -34), (-50, -36), (-60, -6)], "#3d7fe0")             # задник
    s.append(shape(upper, "#ffffff", inner, w=3.4, seed=sd + 1))
    # подошва
    sole = [(-86, 14, 1), (88, 14, 1), (90, 26), (82, 34, 1), (-82, 34, 1), (-88, 26)]
    s.append(shape(sole, "#f3f0e8", blob([(-88, 26), (90, 26), (82, 34), (-82, 34)], "#ff8a3d"), w=3.2, seed=sd + 2))
    # шнурки
    for k in range(4):
        x = -18 + k * 14
        s.append(line([(x - 6, -22 + k * 2), (x + 8, -14 + k * 2)], 3.2, INK, taper=.2, wmin=.6, seed=sd + 10 + k))
    s.append(line([(-60, -36), (-40, -38)], 2.6, INK, taper=.3, seed=sd + 20))
    return "".join(s)


def balloon(cx, cy, rot, squash, sd=0):
    """Шарик (центр cx, cy), на нём кроссовка; узелок внизу. Возвращает (svg, точка узелка)."""
    rx, ry = 150 * squash, 172 / squash ** .5
    pts = []
    for k in range(28):
        a = 2 * math.pi * k / 28
        y = math.sin(a)
        r = 1 + 0.06 * max(0, y) ** 2            # к узелку чуть вытянут
        pts.append((rx * math.cos(a) * (1 - 0.1 * max(0, y)), ry * y * r))
    inner = blob([(-rx, 0), (0, ry * .4), (rx, -ry * .2), (rx, ry * 1.2), (-rx, ry * 1.2)], "#c94a3e", .75)
    inner += f'<g transform="translate(0 6) scale(1.12) rotate(-8)">{sneaker(sd + 100)}</g>'
    inner += blob(ellipse_pts(-rx * .48, -ry * .5, 30, 52, 12, rot=28), "#ffffff", .55)
    inner += blob(ellipse_pts(-rx * .62, -ry * .12, 9, 14, 8, rot=20), "#ffffff", .5)
    s = [shape(pts, "#ef6a55", inner, w=5.2, seed=sd + 1)]
    kn = [(-12, ry * 1.06 + 16, 1), (12, ry * 1.06 + 16, 1), (0, ry * 1.06 - 4)]
    s.append(shape(kn, "#d9553f", "", w=3.2, seed=sd + 2))
    tr = math.radians(rot)
    knot = (cx - math.sin(tr) * (ry * 1.06 + 16), cy + math.cos(tr) * (ry * 1.06 + 16))
    return f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)})">{"".join(s)}</g>', knot


def string(p0, p1, sway, sd):
    mx, my = (p0[0] + p1[0]) / 2 + sway, (p0[1] + p1[1]) / 2
    pts = [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * mx + u * u * p1[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * my + u * u * p1[1])
           for u in [k / 12 for k in range(13)]]
    return line(pts, 3.2, "#f3f0e8", taper=.05, wmin=.9, seed=sd) if False else line(pts, 3.4, INK, taper=.05, wmin=.9, seed=sd)


# ───────────────────────── s07
def look07(t):
    """Направление взгляда: +1 влево (лоб влево), -1 вправо; быстрые повороты с паузами. fx — зеркало с «сжатием»."""
    turns = [(9.98, -1), (10.42, 1), (10.98, -1)]
    d, fx, sq = 1, 1.0, 0.0
    for tt, nd in turns:
        u = (t - tt + 0.07) / 0.14
        if u >= 1:
            d = nd
        elif u > 0:
            sq = math.sin(math.pi * u)
            fx = (d if u < 0.5 else nd) * (1 - 0.28 * sq)
            return fx, sq
    fx = float(d)
    return fx, sq


def s07(t):
    fx, sq_turn = look07(t)
    breath = 1 + 0.012 * math.sin(t * 2.4)
    sgn = 1 if fx > 0 else -1
    # подаётся в сторону взгляда, чуть наклоняется вперёд
    lean = -5 * sgn + 2.5 * math.sin(t * 1.9)
    hop = -18 * sq_turn
    pose = Pose(540 - 26 * sgn, 760 + hop + 6 * math.sin(t * 2.4), 1.0 * breath, lean, 1 - 0.05 * sq_turn, fx)
    # шарик: справа сверху, тянет вверх и качается
    bx = 790 + 22 * math.sin(t * 1.3) + 8 * math.sin(t * 2.9)
    by = 300 + 14 * math.sin(t * 1.7 + 1)
    brot = 8 * math.sin(t * 1.3 + .6) + 4
    bal, knot = balloon(bx, by, brot, 1 + 0.015 * math.sin(t * 3.1), sd=700)
    # правая кисть держит нитку (кулак, пальцы вверх)
    wr = (pose.x + 250 + 10 * math.sin(t * 1.3), pose.y - 30 + 8 * math.sin(t * 2.1))
    ar, cr = -96, 1.0
    grip = (wr[0] + 6, wr[1] - 54)
    # левая: чешет макушку (до «мало»), на «мало» разводит в сторону ладонью вверх
    scratch = (pose.x - 90 * sgn + 16 * math.sin(t * 15), pose.y - 150 + 7 * math.sin(t * 30))
    shrug = (pose.x - 290, pose.y + 10)
    k = smooth(MALO - 0.16, MALO + 0.06, t)
    k_in = smooth(9.6, 9.9, t)
    rest = (pose.x - 250, pose.y + 130)
    sc_pt = (rest[0] + (scratch[0] - rest[0]) * k_in, rest[1] + (scratch[1] - rest[1]) * k_in)
    wl = (sc_pt[0] + (shrug[0] - sc_pt[0]) * k, sc_pt[1] + (shrug[1] - sc_pt[1]) * k - 30 * math.sin(math.pi * k))
    pop = back_out(clamp((t - MALO) / 0.22), 2.5) if t > MALO else 0.0
    al = (-60 + 20 * math.sin(t * 15)) * (1 - k) + (200 + 8 * pop) * k
    cl = (0.45 + 0.25 * math.sin(t * 30)) * (1 - k) + 0.0 * k
    brain_svg = _ST["brain"]
    s_str = string(knot, grip, 18 * math.sin(t * 1.6 + 2), 711)
    art = bal + body(pose, brain_svg, wl, wr, al, ar, cl, cr, bl=-30 if k > .5 else 50, br=-50, sd=0, mid="", front="")
    art = s_str + art
    # тень, знаки вопроса — по очереди с той стороны, куда смотрит
    shadow = sb.shadow(pose.x, sb.FLOOR + 10, 180)
    marks = ""
    for (t0, x, y, sd) in [(9.82, 230, 470, 801), (10.5, 860, 600, 802), (MALO + 0.05, 300, 520, 803)]:
        e = t - t0
        if e > 0:
            sc = back_out(clamp(e / 0.24), 2.2) * (1 + 0.04 * math.sin(e * 9)) * (1 - ease_in(clamp((e - 0.6) / 0.22), 2))
            marks += qmark(x, y - 30 * e, sc * 1.25, 1.0, sd)
    u = clamp((t - 9.56) / 1.92)
    cm = cam(545, 640 - 20 * u, 1.16 + 0.07 * (0.4 * u + 0.6 * ease_io(u)), 0.6 - 1.0 * u)
    return shadow + art + marks, cm


# ───────────────────────── s08: будильник без стрелок
CLK = (540, 900)
CR = 190


def clock_back():
    """Будильник: ножки, колокольчики, корпус, циферблат с рисками (без цифр), подставка с гнездом кнопки."""
    x, y = CLK
    s = []
    # подставка
    s.append(sb.shadow(x, 1192, 330, .6))
    s.append(shape(rect_pts(x - 300, 1104, x + 300, 1188, 18), "#3b4a7e",
                   blob(rect_pts(x - 300, 1150, x + 300, 1188, 16), "#2b3764") + line([(x - 280, 1114), (x + 280, 1114)], 4, "#5e70ad", seed=31, op=.8),
                   w=5, seed=30))
    # ножки
    for sd, side in ((41, -1), (42, 1)):
        s.append(shape([(x + side * 120, y + 150), (x + side * 150, y + 168), (x + side * 176, y + 212, 1), (x + side * 130, y + 212, 1)],
                       "#e8b23a", blob([(x + side * 150, y + 190), (x + side * 176, y + 212), (x + side * 140, y + 212)], "#b9851f"), w=4, seed=sd))
    # колокольчики и молоточек
    for sd, side in ((51, -1), (52, 1)):
        bx, by = x + side * 128, y - 168
        pts = ellipse_pts(bx, by, 72, 52, 18, rot=side * 34)
        s.append(shape(pts, "#f2c14e", blob(ellipse_pts(bx + side * 18, by + 18, 60, 36, 14, rot=side * 34), "#c9922b", .9) +
                       blob(ellipse_pts(bx - side * 22, by - 16, 20, 9, 8, rot=side * 34), "#fff3c4", .9), w=4.6, seed=sd))
        s.append(shape(ellipse_pts(x + side * 92, y - 132, 14, 10, 8, rot=side * 34), "#c9922b", "", w=3, seed=sd + 5))
    s.append(shape(rect_pts(x - 7, y - 236, x + 7, y - 196), "#b9851f", "", w=3, seed=55))
    s.append(shape(ellipse_pts(x, y - 240, 22, 12, 10), "#f2c14e", "", w=3.4, seed=56))
    # корпус
    s.append(shape(ellipse_pts(x, y, CR + 30, CR + 30, 36), "#2f9c93",
                   blob(ellipse_pts(x + 22, y + 26, CR + 20, CR + 20, 30), "#217069", .9) +
                   blob(ellipse_pts(x - 70, y - 120, 70, 26, 14, rot=-36), "#7fd3c8", .8), w=6, seed=60))
    return "".join(s)


def clock_face(warm):
    x, y = CLK
    s = []
    face = mix("#d9d6cc", "#fff6dd", warm)
    s.append(shape(ellipse_pts(x, y, CR, CR, 36), face, blob(ellipse_pts(x + 14, y + 18, CR, CR, 30), mix("#bdb9ad", "#f3e3bc", warm), .7),
                   w=4.6, seed=70))
    for k in range(12):
        a = math.radians(k * 30)
        r0, r1 = (CR - 46, CR - 16) if k % 3 == 0 else (CR - 32, CR - 16)
        s.append(line([(x + math.sin(a) * r0, y - math.cos(a) * r0), (x + math.sin(a) * r1, y - math.cos(a) * r1)],
                      11 if k % 3 == 0 else 7, INK, taper=.15, wmin=.7, seed=80 + k))
    return "".join(s)


def hand_shape(ang, L, w, color, sd):
    """Стрелка: от центра под углом ang (0 — вверх, по часовой), длина L, ромбовидное остриё."""
    x, y = CLK
    a = math.radians(ang)
    dx, dy = math.sin(a), -math.cos(a)
    nx, ny = -dy, dx
    tail = 26
    pts = [(x - dx * tail + nx * w * .5, y - dy * tail + ny * w * .5), (x + dx * L * .72 + nx * w, y + dy * L * .72 + ny * w),
           (x + dx * L, y + dy * L, 1), (x + dx * L * .72 - nx * w, y + dy * L * .72 - ny * w),
           (x - dx * tail - nx * w * .5, y - dy * tail - ny * w * .5)]
    return shape(pts, color, "", w=3.6, seed=sd)


def clock_hands(t):
    """До «точного» — нет; с 11.86 влетают, крутятся и щёлкают на 7:00 ровно на CLICK (с перелётом)."""
    x, y = CLK
    if t < 11.86:
        return shape(ellipse_pts(x, y, 14, 14, 12), "#9b978c", "", w=3, seed=91)
    u = clamp((t - 11.86) / (CLICK - 11.86))
    grow = ease_out(u, 2)
    if t < CLICK:
        mh = 360 * 1.6 * (1 - ease_out(u, 2.4))       # раскрутка к цели
        hh = 210 - 360 * 0.6 * (1 - ease_out(u, 2.4))
        mang, hang = 0 - mh, hh
    else:
        e = t - CLICK
        jig = 7 * math.exp(-e * 9) * math.cos(e * 40)
        mang, hang = jig, 210 + jig * .7
    s = hand_shape(hang, 118 * grow, 18, INK, 92)
    s += hand_shape(mang, 160 * grow, 13, "#e2543f", 93)
    s += shape(ellipse_pts(x, y, 16, 16, 12), "#e2543f", blob(ellipse_pts(x - 4, y - 4, 5, 5, 8), "#ffffff", .8), w=3.2, seed=94)
    return s


def click_burst(t):
    e = t - CLICK
    if e < 0 or e > 0.45:
        return ""
    x, y = CLK
    s = []
    for k in range(10):
        a = k * math.pi / 5 + .3
        r0 = CR + 50 + 90 * ease_out(e / .45)
        L = 50 * (1 - e / .45)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))],
                      9, "#ffe27a", taper=.5, seed=120 + k))
    return "".join(s)


def button(t):
    """Кнопка ▶ на подставке: до GO — серая, на GO — нажимается и загорается зелёным, свечение пульсирует."""
    x, y = CLK[0], 1146
    on = smooth(GO - 0.02, GO + 0.12, t)
    press = math.exp(-max(t - GO, 0) * 12) * (t >= GO) * 8
    s = []
    if on > 0:
        pulse = 1 + 0.06 * math.sin((t - GO) * 7)
        g = rad_grad([(0, "#7dff9a", .75 * on), (.5, "#46d36b", .3 * on), (1, "#46d36b", 0)], x, y - 10, 210 * pulse, 150 * pulse)
        s.append(f'<ellipse cx="{x}" cy="{y - 10}" rx="{f(220 * pulse)}" ry="{f(160 * pulse)}" fill="url(#{g})"/>')
    s.append(shape(ellipse_pts(x, y + 4, 92, 34, 20), "#232c52", "", w=4, seed=130))
    top = mix("#7d8295", "#3fcf62", on)
    shd = mix("#5b6072", "#22994a", on)
    yy = y - 14 + press
    s.append(shape(ellipse_pts(x, yy, 80, 30, 22), shd, "", w=4, seed=131))
    s.append(shape(ellipse_pts(x, yy - 12, 80, 30, 22), top,
                   blob(ellipse_pts(x - 28, yy - 22, 30, 9, 10), mix("#a7abba", "#b6ffc8", on), .9), w=4.4, seed=132))
    tri = [(x - 14, yy - 28, 1), (x + 22, yy - 12, 1), (x - 14, yy + 4, 1)]
    s.append(shape(tri, mix("#c9ccd6", "#ffffff", on), "", w=3, seed=133))
    if t > GO:
        e = t - GO
        if e < 0.5:
            for k in range(7):
                a = -math.pi * (0.1 + 0.8 * k / 6)
                r0 = 70 + 110 * ease_out(e / .5)
                L = 40 * (1 - e / .5)
                s.append(line([(x + math.cos(a) * r0 * 1.4, yy + math.sin(a) * r0), (x + math.cos(a) * (r0 + L) * 1.4, yy + math.sin(a) * (r0 + L))],
                              8, "#9dffb2", taper=.5, seed=140 + k))
    return f'<g transform="translate({x} {y}) scale(1.3) translate({-x} {-y})">{"".join(s)}</g>'


def s08(t):
    live = smooth(GO, GO + 0.4, t)
    lift = spring(max(t - GO, 0), 1.6, 4.0) if t > GO else 0.0
    perk = 0.25 * math.exp(-max(t - CLICK, 0) * 5) * (t > CLICK)          # вздрагивает на щелчке
    sad = 0.8 * (1 - live)
    breath = 1 + 0.014 * math.sin(t * 2.0)
    droop = 1 - lift
    pose = Pose(540, 470 + 46 * droop - 30 * perk + 8 * math.sin(t * 2.0) * droop, 0.92 * breath,
                -9 * droop + 3 * math.sin(t * 1.5) * live, 0.9 + 0.1 * lift + 0.05 * perk, 1.0)
    brain_svg = brain_art.brain(0, sad)
    # руки: висят по бокам будильника → вскинуты вверх (пальцы врозь) и качаются
    hang_l, hang_r = (250, 820 + 10 * math.sin(t * 2)), (830, 820 + 10 * math.sin(t * 2 + 1))
    up_l = (190 + 14 * math.sin(t * 6), 300 - 16 * abs(math.sin(t * 5)))
    up_r = (890 + 14 * math.sin(t * 6 + 1), 300 - 16 * abs(math.sin(t * 5 + 1)))
    k = lift if t > GO else 0.0
    k = clamp(k)
    wl = (hang_l[0] + (up_l[0] - hang_l[0]) * k, hang_l[1] + (up_l[1] - hang_l[1]) * k)
    wr = (hang_r[0] + (up_r[0] - hang_r[0]) * k, hang_r[1] + (up_r[1] - hang_r[1]) * k)
    al = 100 * (1 - k) + (-110) * k
    ar = 80 * (1 - k) + (-70) * k
    cl = cr = 0.3 * (1 - k)
    br_ = body(pose, brain_svg, wl, wr, al, ar, cl, cr, bl=-40 + 80 * k, br=40 - 80 * k, sd=200)
    # искры радости вокруг мозга
    sp = ""
    if t > GO + 0.1:
        e = t - GO - 0.1
        for j in range(8):
            a = j * math.pi / 4 + 0.4
            r = 250 + 40 * math.sin(e * 3 + j)
            x, y = pose.x + math.cos(a) * r * 1.2, pose.y + math.sin(a) * r * .8
            sc = back_out(clamp((e - j * 0.04) / 0.25)) * (0.8 + 0.25 * math.sin(e * 8 + j))
            if sc > 0.05:
                pts = []
                for i in range(8):
                    rr = (22 if i % 2 == 0 else 6) * sc
                    aa = i * math.pi / 4
                    pts.append((x + math.cos(aa) * rr, y + math.sin(aa) * rr))
                sp += blob(pts, "#ffe27a", .95)
    warm = smooth(CLICK, CLICK + 0.3, t)
    clk = clock_back() + clock_face(warm) + clock_hands(t)
    jolt = 6 * math.exp(-max(t - CLICK, 0) * 10) * math.sin(max(t - CLICK, 0) * 50) * (t > CLICK)
    clk = f'<g transform="translate(0 {f(jolt)})">{clk}</g>'
    art = sb.shadow(540, sb.FLOOR + 6, 150, .4) + br_ + sp + clk + click_burst(t) + button(t)
    u = clamp((t - 11.08) / 3.0)
    push = 0.05 * math.exp(-max(t - CLICK, 0) * 6) * (t > CLICK) + 0.035 * math.exp(-max(t - GO, 0) * 6) * (t > GO)
    cm = cam(540, 770 - 10 * u, 1.08 + 0.04 * u + push, -0.5 + 0.8 * u)
    return art, cm


def build_static():
    if _ST:
        return
    sb.build_static()
    _ST["bg"] = sb._ST["bg"]
    _ST["brain"] = sb._ST["brain"]
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s07": s07, "s08": s08}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{_ST["bg"]}{sb.dust(t)}{art}</g>')
