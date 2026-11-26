"""Рилс 127 «30 дней с котиком-напарником. День 2», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920.
Продолжение рилса 124: тот же календарь на 30 дней, листок «завтра». Говорит Дима от первого лица. Места: календарь на
стене, диван, стол утром и вечером, корзина со стиркой, стиральная машинка. Призыв — TG-карточка v5 (scripts/story_cta_tg.py).
NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people, REPO, COMMON  # noqa: E402
import room as RM  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "scripts"))
import story_cta_tg as TG  # noqa: E402

HIT = stress(1, .3)
INK2 = "#1d2448"


# ═════════════ календарь на 30 дней (как в рилсе 124) ═════════════
def paw_print(col="#e8823a"):
    return blob(ellipse_pts(0, 8, 20, 17, 12), col) + "".join(blob(ellipse_pts(dx, -20 - (6 if abs(dx) < 15 else 0), 8, 9, 10), col)
                                                                for dx in (-22, -8, 8, 22))


def cal30(x, y, k=1.0, circles=(), paws=(), mark=None, mark_u=0.0, glow=None, glow_u=0.0, rot=0.0):
    """Настенный календарь 30 дней (центр). circles — {номер дня: 0…1 рисуется красный круг}; paws — {номер: 0…1 отпечаток};
    mark — номер клетки под жёлтым «?» (mark_u 0…1); glow — номер клетки с подсветкой."""
    circles, paws = dict(circles), dict(paws)
    Wc, Hc = 760.0, 760.0
    cw, ch = Wc / 6, (Hc - 170) / 5
    o = blob(lib.rect_pts(-Wc / 2 + 16, -Hc / 2 + 20, Wc / 2 + 16, Hc / 2 + 20), "#000000", .18)
    inner = blob(lib.rect_pts(-Wc / 2, -Hc / 2, Wc / 2, -Hc / 2 + 150), "#c8553d")
    inner += text("30 ДНЕЙ", 0, -Hc / 2 + 108, 92, fill="#ffffff", stroke="#7a2a1e", sw=6)

    def cc(i):
        return (-Wc / 2 + cw * ((i - 1) % 6) + cw / 2, -Hc / 2 + 170 + ch * ((i - 1) // 6) + ch / 2)
    if glow and glow_u > 0:
        gx, gy = cc(glow)
        inner += blob(lib.rect_pts(gx - cw / 2 + 4, gy - ch / 2 + 4, gx + cw / 2 - 4, gy + ch / 2 - 4), "#fff1b0", glow_u)
    if mark and mark_u > 0:
        gx, gy = cc(mark)
        inner += blob(lib.rect_pts(gx - cw / 2 + 4, gy - ch / 2 + 4, gx + cw / 2 - 4, gy + ch / 2 - 4), "#ffe08a", .9 * clamp(mark_u))
    for i in range(1, 31):
        cx_, cy_ = cc(i)
        inner += line([(cx_ - cw / 2, cy_ + ch / 2), (cx_ + cw / 2, cy_ + ch / 2)], 2, "#d6cbb4", taper=0, wmin=1, seed=4000 + i)
        big = i <= 3
        inner += text(str(i), cx_, cy_ + 20, 64 if big else 54, fill=RED if i in circles or i in paws else INK2, stroke="#ffffff", sw=.01)
    for j in range(1, 6):
        x_ = -Wc / 2 + cw * j
        inner += line([(x_, -Hc / 2 + 160), (x_, Hc / 2 - 10)], 2, "#d6cbb4", taper=0, wmin=1, seed=4100 + j)
    for i, u in circles.items():
        if u > 0:
            c1 = cc(i)
            n = max(2, int(40 * clamp(u)))
            pts = [(c1[0] + 56 * math.cos(-1.7 + 6.6 * q / 39), c1[1] + 50 * math.sin(-1.7 + 6.6 * q / 39)) for q in range(n)]
            inner += line(pts, 9, RED, taper=.2, wmin=.6, seed=4200 + i)
    for i, u in paws.items():
        if u > 0:
            c1 = cc(i)
            s = 1 + .6 * (1 - ease_out(clamp(u)))
            inner += f'<g opacity="{min(1.0, u * 3):.2f}" transform="translate({c1[0] + 26:.1f} {c1[1] - 10:.1f}) scale({s:.3f})">{paw_print()}</g>'
    if mark and mark_u > 0:
        gx, gy = cc(mark)
        inner += tf(text("?", 0, 40, 120, fill=RED, stroke="#ffffff", sw=8), gx, gy - 10, pop(mark_u, 0, 1.0) if mark_u < 1 else 1.0)
    o += shape(lib.rect_pts(-Wc / 2, -Hc / 2, Wc / 2, Hc / 2), "#fbf6ea", inner, w=5, seed=4300)
    for j in range(6):
        o += shape(ellipse_pts(-Wc / 2 + 70 + 124 * j, -Hc / 2 - 4, 12, 20, 10), "#5a5f6e", "", w=3, seed=4310 + j)
    return tf(o, x, y, k, rot)


def cell(i):
    """Центр клетки дня i в координатах календаря."""
    cw, ch = 760 / 6, 590 / 5
    return (-380 + cw * ((i - 1) % 6) + cw / 2, -380 + 170 + ch * ((i - 1) // 6) + ch / 2)


def room(t):
    return [plain_room(t), rug(540, RFL + 160, 560)]


def frame_s01(t):
    """ХУК: календарь на 30 дней крупно, «1» уже обведена с лапой; кот летит снизу и ставит лапу на «2»."""
    tl = W(1)
    o = room(t)
    o.append(cal30(600, 1000, 1.0, circles={1: 1.0, 2: ramp(t, tl - .05, .3)}, paws={1: 1.0, 2: ramp(t, tl, .2)}, glow=2, glow_u=bump(t, tl, .05, .4)))
    c2 = cell(2)
    px, py = 600 + c2[0] + 26, 1000 + c2[1] - 10
    j = ease_out(ramp(t, -.25, tl + .25))
    ex, ey = 150.0, py + 130
    if t < tl + .15:
        cx_, cy_ = 980 + (ex - 980) * j, 1720 + (ey - 1720) * j - 180 * math.sin(math.pi * j)
    else:
        g = t - tl - .15
        cx_, cy_ = ex - 20 * g, min(RFL, ey + 2400 * g * g)
    o.append(cat(cx_, cy_, .8, t, dict(look=(.8, -.4), smile=.8, paw=1.0 if j > .6 and t < tl + .35 else .2, paw_dx=110,
                                       legs=1.0 if cy_ < RFL - 5 else 0.0, perk=1.0)))
    o.append(PR.sparkles(px, py, 1.6, bump(t, tl, .05, .5), t, seed=11, n=6, r=150))
    dx, dy = shake(t, tl, 12)
    return hook_view("".join(o), t, HIT, 560, 1080, 1.05, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«с котиком-напарником»: Дима на диване, кот запрыгивает рядом, дают «пять»."""
    a, b = T0("s02"), T1("s02")
    o = room(t)
    o.append(PR.window(930, 1020, 280, 380, mode="day", t=t, seed=4, curtain=False))
    sf = RM.sofa(540, RFL, 1.0)
    o.append(sf["back"])
    x, k = 440.0, .66
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    th = W(3) + .45
    hi = ease_out(ramp(t, th, .25))
    f = people.dima82(x, RFL - 314, k, "laugh82", "sit_desk", t=t, feet=feet,
                      arms={"n": ("ik", (x + 200, RFL - 560 - 60 * hi), -1)})
    o.append(f["svg"])
    o.append(sf["arm_r"])
    j = ease_out(ramp(t, a - .15, .4))
    o.append(cat(980 - 300 * j, RFL - 306 - 180 * math.sin(math.pi * j), .62, t,
                 dict(look=(-.8, -.6), smile=1.0, paw=hi, paw_dx=-90, legs=1 - j, perk=1.0)))
    o.append(PR.sparkles(x + 200, RFL - 600, 1.4, bump(t, th + .25, .05, .5), t, seed=21, n=6, r=120))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, th + .25, 7)
    return view("".join(o), 580 + dx, 1050 + dy, 1.3 + .05 * uu, 0, t=t)


def frame_s03(t):
    """«День второй!»: календарь, «2» обводится красным, лапа светится; Дима показывает на неё, кот у календаря."""
    a, b = T0("s03"), T1("s03")
    o = room(t)
    o.append(cal30(700, 920, .85, circles={1: 1.0, 2: ramp(t, a - .1, .45)}, paws={1: 1.0, 2: 1.0}, glow=2,
                   glow_u=.5 + .5 * bump(t, W(5), .05, .4)))
    f = stand(170, t, "laugh82", "d82_one")
    o.append(f["svg"])
    o.append(cat(940, RFL, .8, t, dict(look=(-.6, -.8), smile=1.0, perk=1.0, tail=10 * math.sin(t * 3))))
    c2 = cell(2)
    o.append(PR.sparkles(700 + c2[0] * .85, 920 + c2[1] * .85, 1.8, bump(t, W(5), .05, .5), t, seed=31, n=7, r=200))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(5), 9)
    return view("".join(o), 520 + dx, 1000 + dy, 1.0 + .05 * uu, 0, t=t)


# ═════════════ листок ═════════════
def note_sheet(x, y, k, front="", fw=1.0, back=None, flip=0.0, drawing=0.0, rot=0.0, pencil=False):
    """Листок в клетку 460×340. front — слово на лицевой (fw 0…1 — дописано); flip 0…1 — листок переворачивается
    (на половине показывается оборот); back — (строка1, u1, строка2, u2) на обороте; drawing 0…1 — на нём рисуется телефон."""
    sx = math.cos(math.pi * clamp(flip))
    showing_back = flip > .5
    o = blob(lib.rect_pts(-230 + 10, -170 + 12, 230 + 10, 170 + 12), "#000000", .15)
    inner = "".join(line([(-230, -170 + 40 * j), (230, -170 + 40 * j)], 1.6, "#bcd0e6", taper=0, wmin=1, seed=4900 + j) for j in range(1, 9))
    if not showing_back:
        if front and fw > 0:
            c = lib.clip_rect(-215, -110, 440 * clamp(fw), 200)
            inner += f'<g clip-path="url(#{c})">' + plain(front, -190, 40, 120, fill=INK2) + "</g>"
        if drawing > 0:
            inner += phone_sketch(drawing)
    elif back:
        l1, u1, l2, u2 = back
        if u1 > 0:
            c = lib.clip_rect(-215, -150, 440 * clamp(u1), 150)
            inner += f'<g clip-path="url(#{c})">' + plain(l1, -205, -40, 84, fill=INK2) + "</g>"
        if u2 > 0:
            c = lib.clip_rect(-215, -10, 440 * clamp(u2), 160)
            inner += f'<g clip-path="url(#{c})">' + plain(l2, -205, 100, 70, fill=RED) + "</g>"
    o += shape(lib.rect_pts(-230, -170, 230, 170), "#fdfbf4" if not showing_back else "#f7f1e2", inner, w=4, seed=4910)
    body = f'<g transform="scale({max(.02, abs(sx)):.3f} 1)">{o}</g>'
    if pencil:
        body += PR.pencil(150, 10, 1.4, -30)
    return tf(body, x, y, k, rot)


def phone_sketch(u):
    """Телефон, нарисованный карандашом на листке: контур, экран, кнопка; u 0…1 — сколько нарисовано."""
    pts = [(-70, -130), (70, -130), (82, -118), (82, 118), (70, 130), (-70, 130), (-82, 118), (-82, -118), (-70, -130)]
    seg = []
    for a_, b_ in zip(pts, pts[1:]):
        for q in range(8):
            seg.append((a_[0] + (b_[0] - a_[0]) * q / 8, a_[1] + (b_[1] - a_[1]) * q / 8))
    seg.append(pts[-1])
    u1 = clamp(u / .6)
    n = max(2, int(len(seg) * u1))
    o = line(seg[:n], 9, "#3a3f52", taper=.15, wmin=.7, seed=4950)
    if u > .6:
        v = clamp((u - .6) / .3)
        scr = [(-60, -100), (60, -100), (60, 90), (-60, 90), (-60, -100)]
        o += line(scr[:max(2, int(5 * v))], 6, "#3a3f52", taper=.1, wmin=.7, seed=4951)
    if u > .9:
        o += line(ellipse_pts(0, 110, 10, 10, 10) + [ellipse_pts(0, 110, 10, 10, 10)[0]], 5, "#3a3f52", seed=4952)
    return tf(o, 0, 0, .95)


def sketch_tip(u):
    """Где сейчас кончик карандаша на рисунке телефона (координаты листка до масштаба .95)."""
    pts = [(-70, -130), (70, -130), (82, -118), (82, 118), (70, 130), (-70, 130), (-82, 118), (-82, -118), (-70, -130)]
    seg = []
    for a_, b_ in zip(pts, pts[1:]):
        for q in range(8):
            seg.append((a_[0] + (b_[0] - a_[0]) * q / 8, a_[1] + (b_[1] - a_[1]) * q / 8))
    n = max(2, int((len(seg) + 1) * clamp(u / .6)))
    x_, y_ = seg[min(n, len(seg)) - 1]
    return x_ * .95, y_ * .95


def wood_desk(t, night=0.0):
    o = [rect(-1400, -1400, 2600, 3400, "#b27c4c")]
    for j in range(6):
        o.append(line([(-200, 300 + 260 * j), (1300, 320 + 260 * j)], 3, "#94633a", taper=.3, wmin=.4, seed=5000 + j))
    o.append(PR.glow(540, 900, 600, .3, "#ffd890"))
    return o


def frame_s04(t):
    """«Утром я понял, зачем котик оставил листок»: утро, солнце; на столе листок «завтра», кот сидит рядом; у Димы лампочка."""
    a, b = T0("s04"), T1("s04")
    o = desk_room(t, sun=1.0)
    o.append(note_sheet(660, DESK_Y - 26, .52, "завтра", rot=-4))
    o.append(cat(880, DESK_Y - 4, .5, t, dict(look=(-.8, .3), smile=.6, paw=.5, paw_dx=-70, perk=1.0)))
    f = dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.8, .4)), lean=.12)
    o.append(f["svg"])
    tb = W(8)
    o.append(PR.idea_bulb(400, 520, 1.1, on=ramp(t, tb, .15), t=t, seed=3) if t > tb - .05 else "")
    o.append(PR.sparkles(400, 520, 1.2, bump(t, tb, .05, .5), t, seed=41, n=5, r=120))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 6)
    return view("".join(o), 600 + dx, 860 + dy, 1.4 + .06 * uu, 0, t=t)


def frame_s05(t):
    """«оставил листок „завтра“»: листок крупно на столе, «завтра», лапа кота на углу, свет."""
    a, b = T0("s05"), T1("s05")
    o = wood_desk(t)
    o.append(note_sheet(540, 880, 2.0, "завтра", rot=-3))
    o.append(cat(900, 1560, 1.0, t, dict(look=(-.7, -.8), smile=.7, paw=.7, paw_dx=-90, perk=1.0)))
    o.append(PR.sparkles(540, 880, 2.0, bump(t, W(13), .05, .5), t, seed=51, n=6, r=360))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(13), 7)
    return view("".join(o), 560 + dx, 1000 + dy, 1.0 + .07 * uu, 0, bg="#b27c4c", t=t)


def laundry(x, y, k, seed=0, flies=0.0, t=0.0):
    """Корзина, набитая бельём (центр дна): горка вещей, свисает носок и рукав; flies — мухи кружат."""
    o = PR.basket(0, 0, 1.0, seed=seed)
    cols = ["#4a7bd0", "#e2a23a", "#d95b6a", "#6fb38a", "#f2f2f2", "#9b7ad1", "#4a7bd0"]
    for i, (cx_, cy_, rx, ry) in enumerate(((-90, -170, 80, 50), (0, -200, 95, 60), (90, -170, 80, 50), (-40, -250, 75, 48),
                                             (55, -255, 70, 45), (0, -300, 60, 40), (-110, -215, 50, 35))):
        o += shape(ellipse_pts(cx_, cy_, rx, ry, 14), cols[i], "", w=3.4, seed=5100 + i + seed)
    o += PR.striped_sock(140, -120, 1.0, 70, seed=2)
    o += shape([(-150, -160, 1), (-180, -120, 1), (-200, -40, 1), (-170, -36, 1), (-150, -120, 1)], "#d95b6a", "", w=3, seed=5120)
    if flies > 0:
        for i in range(3):
            a_ = t * (3 + i) + i * 2.1
            fx, fy = 60 * math.cos(a_) + (i - 1) * 50, -360 + 40 * math.sin(a_ * 1.3)
            o += blob(ellipse_pts(fx, fy, 12, 10, 8), "#2a2d36", flies)
            o += blob(ellipse_pts(fx - 9, fy - 12, 10, 6, 8), "#cfe3ff", .8 * flies) + blob(ellipse_pts(fx + 9, fy - 12, 10, 6, 8), "#cfe3ff", .8 * flies)
    return tf(o, x, y, k)


def red_plate(s, x, y, u, w=520):
    if u <= 0:
        return ""
    return tf(shape(lib.rrect(-w / 2, -70, w / 2, 70, 30), RED, "", w=5, seed=4600)
              + text(s, 0, 28, 84, fill="#ffffff", stroke="#7a1e18", sw=6), x, y, u)


def frame_s06(t):
    """«Я как раз собирался всё отложить»: Дима на диване с телефоном, корзина со стиркой у дивана, кот на подлокотнике смотрит."""
    a, b = T0("s06"), T1("s06")
    o = room(t)
    o.append(PR.window(930, 1020, 280, 380, mode="day", t=t, seed=4, curtain=False))
    sf = RM.sofa(520, RFL, 1.0)
    o.append(sf["back"])
    x, k = 420.0, .66
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    lay = ease_io(ramp(t, W(18) - .2, .4))
    f = people.dima82(x, RFL - 314, k, "sly" if lay > .5 else "calm82", "sit_desk", t=t, feet=feet, lean_add=-.25 * lay,
                      arms={"n": ("ik", (x + 170, RFL - 520), -1)})
    o.append(f["svg"])
    o.append(mini_phone(x + 175, RFL - 540, .45, -15, screen="#9cc3ef"))
    o.append(sf["arm_r"])
    o.append(laundry(920, RFL + 40, .7, flies=.8, t=t))
    o.append(cat(150, RFL - 300, .55, t, dict(look=(.9, .2), smug=.6, tilt=8 * bump(t, W(19), .1, .5))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(19), 6)
    return view("".join(o), 560 + dx, 1080 + dy, 1.2 + .05 * uu, 0, t=t)


def frame_s07(t):
    """«Стирка лежала в корзине неделю»: корзина с бельём крупно, мухи, плашка «НЕДЕЛЯ»."""
    a, b = T0("s07"), T1("s07")
    o = room(t)
    o.append(laundry(540, 1500, 2.0, flies=1.0, t=t))
    o.append(red_plate("НЕДЕЛЯ", 540, 720, pop(t, W(24) - .1, .25)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(24), 8)
    return view("".join(o), 540 + dx, 1180 + dy, 1.05 + .07 * uu, 0, t=t)


def frame_s08(t):
    """«и я уже сказал себе»: Дима стоит у корзины, пожимает плечами и отворачивается; кот рядом смотрит на него."""
    a, b = T0("s08"), T1("s08")
    o = room(t)
    o.append(laundry(760, RFL + 10, .9, flies=.7, t=t))
    sh = ease_io(ramp(t, W(28) - .1, .3))
    f = stand(330, t, "sly", ("d82_rest", "d82_shrug"), u=sh)
    o.append(f["svg"])
    o.append(cat(980, RFL, .7, t, dict(look=(-.9, -.6), smug=.7)))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1060, 1.12 + .05 * uu, 0, t=t)


def frame_s09(t):
    """«завтра»: из Димы выскакивает пузырь «завтра»; кот поднимает бровь."""
    a, b = T0("s09"), T1("s09")
    o = room(t)
    o.append(laundry(760, RFL + 10, .9, flies=.7, t=t))
    f = stand(330, t, "sly", "d82_shrug")
    o.append(f["svg"])
    mx, my = f["mouth"]
    u = pop(t, W(30) - .08, .25)
    o.append(PR.speech_bubble(mx + 200, my - 230, 420, 200, u, seed=3, tail=(-150, 60)))
    if u > 0:
        o.append(tf(text("завтра", 0, 26, 92, fill=INK2, stroke="#ffffff", sw=.01), mx + 200, my - 230, u))
    o.append(cat(980, RFL, .7, t, dict(look=(-.9, -.7), smug=1.0, tilt=-10 * bump(t, W(30) + .2, .1, .6))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(30), 8)
    return view("".join(o), 580 + dx, 1000 + dy, 1.2 + .05 * uu, 0, t=t)


def frame_s10(t):
    """«Котик перевернул листок»: листок крупно, лапа кота переворачивает его, на обороте пусто, но светится."""
    a, b = T0("s10"), T1("s10")
    fl = ease_io(ramp(t, W(32), .5))
    o = wood_desk(t)
    o.append(note_sheet(520, 860, 1.9, "завтра", flip=fl, rot=-3 + 3 * fl))
    o.append(cat(880 - 60 * math.sin(math.pi * fl), 1560 - 80 * math.sin(math.pi * fl), 1.0, t,
                 dict(look=(-.7, -.8), smile=.4 + .6 * fl, paw=.4 + .6 * math.sin(math.pi * fl), paw_dx=-110, perk=1.0)))
    o.append(PR.sparkles(520, 860, 1.8, bump(t, W(32) + .5, .05, .5), t, seed=101, n=6, r=360))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(32) + .45, 6)
    return view("".join(o), 560 + dx, 1000 + dy, 1.0 + .06 * uu, 0, bg="#b27c4c", t=t)


def frame_s11(t):
    """«На обороте было написано»: оборот листка, карандаш кота начинает писать; кот наклонился над листком."""
    a, b = T0("s11"), T1("s11")
    o = wood_desk(t)
    u1 = ramp(t, W(37), .5)
    o.append(note_sheet(540, 900, 2.0, flip=1.0, back=("сегодня,", u1, "две минуты", 0.0), pencil=True, rot=-1))
    o.append(cat(860, 1450, 1.0, t, dict(look=(-.7, -.8), smile=.6, paw=.6, paw_dx=-90, perk=1.0, tilt=-6)))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 545, 1060, 1.1 + .06 * uu, 0, bg="#b27c4c", t=t)


def frame_s12(t):
    """«сегодня»: камера ближе, «сегодня,» дописывается."""
    a, b = T0("s12"), T1("s12")
    o = wood_desk(t)
    u1 = clamp(.4 + ramp(t, a - .1, WE(38) - a))
    o.append(note_sheet(540, 900, 2.0, flip=1.0, back=("сегодня,", u1, "две минуты", 0.0), pencil=True, rot=-1))
    o.append(cat(900, 1580, 1.0, t, dict(look=(-.7, -.8), smile=1.0, paw=.6, paw_dx=-90, perk=1.0)))
    o.append(PR.sparkles(420, 820, 1.6, bump(t, W(38) + .3, .05, .5), t, seed=121, n=5, r=260))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(38), 6)
    return view("".join(o), 540 + dx, 900 + dy, 1.12 + .06 * uu, 0, bg="#b27c4c", t=t)


def frame_s13(t):
    """«две минуты»: на обороте дописывается «две минуты» красным, рядом звенит таймер; кот доволен."""
    a, b = T0("s13"), T1("s13")
    o = wood_desk(t)
    u2 = ramp(t, a - .05, WE(40) - a + .1)
    o.append(note_sheet(480, 820, 1.7, flip=1.0, back=("сегодня,", 1.0, "две минуты", u2), rot=-1))
    tm = WE(40)
    o.append(PR.bell_timer(820, 1380, 1.1, hand_a=0, sector_u=.033, ring=bump(t, W(39), .05, .5), t=t))
    o.append(cat(330, 1640, .95, t, dict(look=(.7, -.8), smile=1.0, perk=1.0, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(480, 900, 2.0, bump(t, tm, .05, .5), t, seed=131, n=6, r=360))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(39), 8)
    return view("".join(o), 560 + dx, 1050 + dy, 1.02 + .05 * uu, 0, bg="#b27c4c", t=t)


# ═════════════ стиральная машинка ═════════════
def washer(x, y, k, spin=0.0, door=1.0, load=1.0, foam=0.0, t=0.0):
    """Стиральная машинка анфас (центр низа). spin — угол барабана (град), door 0…1 закрыта, load — бельё внутри, foam — пена."""
    o = blob(lib.rect_pts(-210, -520, 230, 10), "#000000", .12)
    o += shape(lib.rrect(-220, -540, 220, 0, 30), "#f4f6f8", "", w=5, seed=5300)
    o += shape(lib.rect_pts(-220, -540, 220, -440), "#e3e7ec", "", w=4, seed=5301)
    o += shape(lib.rrect(-40, -515, 110, -465, 10), "#2c3e50", "", w=3, seed=5302)
    o += shape(ellipse_pts(160, -490, 26, 26, 14), "#cfd6de", line([(160, -490), (160 + 20 * math.cos(math.radians(spin * .3)), -490 + 20 * math.sin(math.radians(spin * .3)))], 4, "#2c3e50", seed=5303), w=3, seed=5304)
    o += shape(lib.rrect(-190, -515, -80, -470, 8), "#cfd6de", "", w=3, seed=5305)
    cy = -230
    o += shape(ellipse_pts(0, cy, 168, 168, 30), "#cfd6de", "", w=5, seed=5310)
    drum = blob(ellipse_pts(0, 0, 135, 135, 30), "#2b4a78")
    if load > 0:
        cols = ["#e2a23a", "#d95b6a", "#6fb38a", "#4a7bd0", "#9b7ad1"]
        for i in range(5):
            a_ = math.radians(spin + 72 * i)
            drum += blob(ellipse_pts(70 * math.cos(a_), 70 * math.sin(a_) + 20, 52, 38, 12), cols[i], load)
    if foam > 0:
        for i in range(7):
            a_ = math.radians(spin * .5 + 51 * i)
            drum += blob(ellipse_pts(95 * math.cos(a_), 95 * math.sin(a_), 22, 22, 10), "#ffffff", .85 * foam)
    c = lib.clip_rect(-135, cy - 135, 270, 270, 135)
    o += f'<g clip-path="url(#{c})"><g transform="translate(0 {cy})">{drum}</g></g>'
    o += blob(ellipse_pts(-50, cy - 60, 50, 26, 12), "#ffffff", .35 * door)
    o += line(ellipse_pts(0, cy, 140, 140, 30) + [ellipse_pts(0, cy, 140, 140, 30)[0]], 9, "#7b8794", taper=0, wmin=1, seed=5311)
    o += shape(lib.rrect(-120, -40, -60, -10, 6), "#cfd6de", "", w=3, seed=5320) + shape(lib.rrect(60, -40, 120, -10, 6), "#cfd6de", "", w=3, seed=5321)
    return tf(o, x, y, k)


def frame_s14(t):
    """«Две минуты, и машинка крутится»: Дима закидывает бельё, на машинке таймер звенит; на «крутится» барабан закручивается."""
    a, b = T0("s14"), T1("s14")
    ts = W(44)
    sp = 0.0 if t < ts else 900 * (t - ts) ** 1.3
    o = room(t)
    o.append(washer(660, RFL + 10, 1.1, spin=sp, foam=ramp(t, ts + .2, .6), t=t))
    o.append(PR.bell_timer(780, RFL - 620, .7, hand_a=360 * ramp(t, a, ts - a), sector_u=ramp(t, a, ts - a), ring=bump(t, ts, .05, .5), t=t))
    th = ease_io(ramp(t, a, .5))
    f = stand(230, t, "focus_smile" if t < ts else "laugh82", "d82_one" if t > ts else "d82_hold", head_add=.05)
    o.append(f["svg"])
    if th < 1:
        o.append(PR.striped_sock(420 + 140 * th, RFL - 400 + 120 * th, .9, 40 + 200 * th, seed=4))
    o.append(cat(980, RFL, .65, t, dict(look=(-.8, -.4), smile=1.0, perk=1.0, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(660, RFL - 250, 1.6, bump(t, ts, .05, .5), t, seed=141, n=6, r=220))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts, 8)
    return view("".join(o), 560 + dx, 1100 + dy, 1.12 + .05 * uu, 0, t=t)


def frame_s15(t):
    """«А я стою и не понимаю»: Дима стоит перед крутящейся машинкой, чешет затылок, над ним «?»."""
    a, b = T0("s15"), T1("s15")
    sp = 900 * (t - W(44)) ** 1.3
    o = room(t)
    o.append(washer(700, RFL + 10, 1.1, spin=sp, foam=1.0, t=t))
    f = stand(300, t, "puzzled82", "d82_look_up")
    o.append(f["svg"])
    tx_, ty_ = f["temple"]
    o.append(PR.question_mark(tx_ + 40, ty_ - 170, 1.4, pop(t, W(51) - .15, .25), col=RED, seed=3))
    o.append(cat(960, RFL, .6, t, dict(look=(-.8, -.5), smile=.8)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(51), 6)
    return view("".join(o), 560 + dx, 1080 + dy, 1.15 + .05 * uu, 0, t=t)


def frame_s16(t):
    """«почему ждал неделю»: Дима у крутящейся машинки, в облаке мыслей — корзина с бельём и «НЕДЕЛЯ»; кот улыбается."""
    a, b = T0("s16"), T1("s16")
    sp = 900 * (t - W(44)) ** 1.3
    o = room(t)
    o.append(washer(820, RFL + 10, .95, spin=sp, foam=1.0, t=t))
    f = stand(340, t, "awkward", "d82_shrug")
    o.append(f["svg"])
    tx_, ty_ = f["temple"]
    inner = laundry(0, 60, .45, seed=3) + text("НЕДЕЛЯ", 0, 140, 64, fill=RED, stroke="#ffffff", sw=6)
    o.append(PR.thought_cloud(tx_ + 330, ty_ - 220, 1.0, 420, 340, pop(t, a - .05, .3), seed=5, inner=inner))
    o.append(cat(1010, RFL, .55, t, dict(look=(-.8, -.6), smile=1.0, perk=1.0)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(54), 7)
    return view("".join(o), 580 + dx, 1000 + dy, 1.08 + .05 * uu, 0, t=t)


def frame_s17(t):
    """«Вечером котик положил новый листок»: вечер, лампа, кот носом двигает чистый листок к Диме."""
    a, b = T0("s17"), T1("s17")
    p = ease_io(ramp(t, W(57) - .2, .7))
    o = desk_room(t, mode="evening")
    o.append(PR.glow(560, 760, 420, .35, "#ffd890"))
    o.append(PR.lamp_desk(980, DESK_Y, 1.2, on=1.0))
    o.append(note_sheet(720 - 170 * p, DESK_Y - 26, .5, rot=-4 + 4 * p))
    f = dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.8, .5)), lean=.05)
    o.append(f["svg"])
    o.append(cat(820 - 120 * p, DESK_Y - 4, .5, t, dict(look=(-.9, .4), smile=.8, paw=.8 * (1 - p) + .3, paw_dx=-80, tilt=-8 * (1 - p))))
    o.append(rect(-1400, -1400, 2600, 3400, "#3b2a4a", .18))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 620, 860, 1.45 + .05 * uu, 0, t=t)


def frame_s18(t):
    """«новый листок. На нём был…»: листок крупно, лапа кота держит карандаш, начинается рисунок."""
    a, b = T0("s18"), T1("s18")
    o = wood_desk(t)
    d = .35 * ramp(t, W(61), b - W(61))
    o.append(note_sheet(540, 880, 2.0, drawing=d, rot=-2))
    px_, py_ = sketch_tip(d)
    o.append(PR.pencil(540 + 1.9 * px_ + 50, 880 + 1.9 * py_ - 60, 1.6, -35))
    o.append(cat(900, 1580, 1.0, t, dict(look=(-.7, -.8), smile=.6, paw=.8, paw_dx=-110, perk=1.0)))
    o.append(rect(-1400, -1400, 2600, 3400, "#3b2a4a", .12))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1000, 1.0 + .06 * uu, 0, bg="#b27c4c", t=t)


def frame_s19(t):
    """«нарисован телефон»: на листке дорисовывается телефон, ближе; кот гордо садится рядом, Дима заглядывает сбоку."""
    a, b = T0("s19"), T1("s19")
    o = wood_desk(t)
    d = .35 + .65 * ramp(t, a, W(64) + .3 - a)
    o.append(note_sheet(560, 820, 2.2, drawing=d, rot=-2))
    o.append(cat(900, 1600, 1.0, t, dict(look=(-.7, -.8), smile=1.0, smug=.5, perk=1.0, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(560, 820, 2.0, bump(t, W(64) + .3, .05, .5), t, seed=191, n=6, r=360))
    o.append(rect(-1400, -1400, 2600, 3400, "#3b2a4a", .12))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(64), 8)
    return view("".join(o), 560 + dx, 960 + dy, 1.05 + .07 * uu, 0, bg="#b27c4c", t=t)


def frame_s20(t):
    """«Что было на третий день»: календарь, «1» и «2» обведены с лапами, клетка «3» загорается под «?»."""
    a, b = T0("s20"), T1("s20")
    o = room(t)
    o.append(cal30(560, 960, 1.0, circles={1: 1.0, 2: 1.0}, paws={1: 1.0, 2: 1.0}, mark=3, mark_u=ramp(t, W(68) - .1, .3)))
    o.append(cat(900, RFL, .85, t, dict(look=(-.7, -.8), perk=1.0, tilt=-10 * bump(t, W(68), .1, .5))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(68), 6)
    return view("".join(o), 540 + dx, 1000 + dy, 1.05 + .06 * uu, 0, t=t)


def frame_s21(t):
    """«покажу в следующей серии»: ночь, кот спит на листке с телефоном, Дима выключает лампу."""
    a, b = T0("s21"), T1("s21")
    off = ramp(t, W(72) - .1, .15)
    o = desk_room(t, mode="night")
    o.append(PR.lamp_desk(980, DESK_Y, 1.4, on=1 - off))
    if off < 1:
        o.append(PR.glow(900, 760, 420, .4 * (1 - off), "#ffd890"))
    o.append(note_sheet(700, DESK_Y - 26, .5, drawing=1.0, rot=-3))
    o.append(CT.curl(720, DESK_Y - 30, .55, dict(eye=.0), t))
    o.append(PR.zzz(780, DESK_Y - 220, .9, t, 1.0))
    f = dima_desk(t, "warm", lean=0.0, head_add=-.05)
    o.append(f["svg"])
    o.append(rect(-1400, -1400, 2600, 3400, "#0c1030", .15 + .3 * off))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 620, 860, 1.45 + .05 * uu, 0, t=t)


def cta(t, zoom=1.0, focus=None):
    c = SH["cta"]
    if "bg" not in TG._ST:
        TG._ST["bg"] = TG.background(lib)
        TG.prepare(COMMON)
        lib.static_done()
    lib.dyn_begin()
    body, (cx, cy, s, rot) = TG.layer(t, c["t0"], c["press"], COMMON)
    if focus:
        cx, cy = cx + (focus[0] - cx) * .3, cy + (focus[1] - cy) * .3
    return lib.svg(f'<rect width="1080" height="1920" fill="#6e4a32"/><g transform="{lib.cam(cx, cy, s * zoom, rot)}">{TG._ST["bg"]}{body}</g>{over(t)}')


def frame_s22(t):
    return cta(t)


def frame_s23(t):
    return cta(t, 1.1, (540, 1000))


def frame_s24(t):
    return cta(t, 1.04)


def frame_s25(t):
    """Петля: кадр хука — календарь на 30 дней, «1» обведена, кот внизу готов к прыжку."""
    a, b = T0("s25"), T1("s25")
    o = room(t)
    o.append(cal30(600, 1000, 1.0, circles={1: 1.0}, paws={1: 1.0}))
    o.append(cat(980, 1720, .8, t, dict(look=(-.8, -.6), smile=.8, perk=1.0)))
    return loop_view("".join(o), t, a, b, HIT, 560, 1080, 1.05)


def frame(sid, t):
    if sid not in ("s22", "s23", "s24"):
        lib.DEFS.clear()
    return globals()["frame_" + sid](t)
