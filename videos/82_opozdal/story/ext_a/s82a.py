"""Рилс 82 «Опять опоздал?», группа A: s05, s09, s10, s11, s13, s17, s18.
Время — ТОЛЬКО из shots.json (t0/t1 плана) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
s05 улица снизу: над Димой в небе полоска времени с дырами; «куда» (w15) задирает голову, «делись» (w16) — новый укус «ам»,
    «двадцать» (w17) — кусок отламывается и падает ему на нос.
s09 прихожая: хлёст-нырок на «смотри» (w35) — ключи, носок-кукла и чайник оживают; «как» (w36) — разом кусают свисающую ленту и
    замирают «невинно».
s10 вечер, прихожая: «помнит» (w38) кивок, «сборы» (w40) рулон катится по полу — короткий отрезок, «десять» (w42) чик ножницами,
    короткая лента взлетает и прилипает к двери.
s11 утро, прихожая: «уходит» (w47) рулон сам катится, лента летит по полу; «двадцать» (w48) — дверь распахивается, лента вылетает
    на лестницу, камера за ней; «пять» (w49) — лента всё тянется, вдвое длиннее короткой на двери.
s13 лента крупно, три укуса храповиком: «ключи» (w54), «носок» (w55), «чайник» (w56); Дима позади роется в куртке, на одной ноге.
s17 вечер: «Поэтому Дима» (w71–w72) достаёт секундомер, «один раз» (w73–w74) палец, «засёк» (w75) щёлк; кот на табуретке следит.
s18 утро ускоренно: «сборы» (w76) ключи с крючка, стрелка закрашивает сектор; «теперь» (w78) сектор наклейкой на дверь;
    «выходит» (w79) обувается; «цифре» (w82) касается наклейки и выходит; воришки щёлкают пустыми «ртами».
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
import room  # noqa: E402
from lib import blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts, shape, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}
FL = room.FL82
HA = room.HALL82


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def T0(sid):
    return SHOTS[sid]["t0"]


def T1(sid):
    return SHOTS[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up, hold, down):
    if t < a:
        return 0.0
    if t < a + up:
        return ease_out((t - a) / up, 2)
    if t < a + up + hold:
        return 1.0
    return 1 - ease_io((t - a - up - hold) / down)


def kick(t, a, dur=.3, freq=2.2):
    """Затухающий толчок 0 → 1 → 0 с отскоком (для камеры на ударе)."""
    u = t - a
    if u <= 0 or u > dur * 2.5:
        return 0.0
    return math.exp(-u / dur * 2.2) * math.sin(math.pi * min(1.0, u / .06) / 2) * math.cos(2 * math.pi * freq * max(0.0, u - .06))


def frame_svg(body, cx, cy, s, rot, bg, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def shadow(x, y, rx, op=.18, col="#2A1A10"):
    return blob(ellipse_pts(x, y, rx, rx * .12, 20), col, op)


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def vignette(col="#120c08", op=.3):
    g = lib.rad_grad([(0, col, 0), (.62, col, 0), (1, col, op)], 540, 760, 1050, 1250)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def ex(name, **over):
    e = dict(people.EXPR["dima"].get(name, {}))
    e.update(over)
    return e


def whip(t, t0, amp=1.0, dur=.28):
    """Хлёст-влёт: 1 на t0 − 0.06, к dur — 0 (ease_out)."""
    return amp * (1 - ease_out(clamp((t - t0 + .06) / dur), 3))


def motion_blur(sd):
    fid = lib.uid("mb")
    lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{sd[0]:.2f} {sd[1]:.2f}"/>'
                    f'</filter>')
    return fid


def blurred(body, sx, sy):
    if sx < .3 and sy < .3:
        return body
    return f'<g filter="url(#{motion_blur((sx, sy))})">{body}</g>'


def chomp_osc(t, a, b, rate=7.0):
    """Щёлканье «ртом» между a и b: 0…1 с частотой rate, плавно включается и гаснет на краях окна."""
    if t < a or t > b:
        return 0.0
    env = min(1.0, (t - a) / .08, (b - t) / .08)
    return env * (.5 - .5 * math.cos(2 * math.pi * rate * (t - a)))


# ═══════════════════════════════ s05: полоска времени над Димой ═══════════════════════════════
S5_Y = 610.0             # средняя линия ленты в небе
S5_X0, S5_X1 = -420.0, 1500.0
S5_BREAK = (.45, .58)    # кусок между этими местами отламывается на «двадцать»
S5_K = 1.15
S5_HIP = (500.0, 1640.0)


def _sky05(t):
    o = []
    g = lib.lin_grad([(0, "#5aa3e0", 1), (.6, "#9ccdf0", 1), (1, "#d9eefa", 1)], 0, -400, 0, 2300, units="userSpaceOnUse")
    o.append(f'<rect x="-800" y="-600" width="2700" height="3000" fill="url(#{g})"/>')
    # облака
    for i, (x, y, w) in enumerate(((180, 160, 300), (860, 300, 380), (-120, 900, 260), (1150, 980, 300))):
        xx = x + 6 * t
        o.append(P.cloud(xx, y, w, w * .45, seed=820 + i, col="#ffffff", ink_w=3.0))
    # дома снизу: стены сходятся кверху (низкий ракурс), внутренние края — рамка кадра
    for side in (-1, 1):
        bi = 540 + side * 470          # внутренний край внизу
        ti = 540 + side * 300          # внутренний край вверху
        bo, to = bi + side * 900, ti + side * 700
        pts = [(bi, 2300, 1), (ti, -600, 1), (to, -600, 1), (bo, 2300, 1)]
        col = "#e7c9a1" if side < 0 else "#d9b3a0"
        sh = "#cfae86" if side < 0 else "#bf9886"
        inner = []
        for r in range(10):
            y0 = -520 + r * 290
            uu = (y0 + 600) / 2900
            xi = lerp(ti, bi, uu)
            for c in range(3):
                wx = xi + side * (60 + 150 * c) * (.75 + .25 * uu)
                ww = 90 * (.75 + .25 * uu)
                xa, xb = min(wx, wx + side * ww), max(wx, wx + side * ww)
                inner.append(shape(rect_pts(xa, y0, xb, y0 + 170 * (.75 + .25 * uu)), "#9fcbe6",
                                   blob(rect_pts(xa, y0 + 100, xb, y0 + 170), "#bfe0f2", .7), w=2.6, seed=8200 + r * 7 + c + side))
        inner.append(blob([(bi, 2300), (ti, -600), (ti + side * 36, -600), (bi + side * 60, 2300)], sh, .9))
        o.append(shape(pts, col, "".join(inner), w=4.4, seed=8190 + side))
    return "".join(o)


def _strip05(t, broke):
    """Лента в небе: укусы, новый укус на «делись», после «двадцать» — два куска с рваными краями."""
    a_new = ws(16)
    bites = [(.12, 52, -1), (.25, 40, 1), (S5_BREAK[0], 44, 1), (S5_BREAK[1], 46, -1), (.7, 54, -1), (.76, 40, 1), (.88, 46, -1)]
    nb = ramp(t, a_new - .02, .09)
    bites.append((.38, 66, -1, nb))
    crumbs = [(len(bites) - 1, t - a_new)] if t > a_new else []
    sway = 10 * math.sin(t * 2.1) + 14 * kick(t, a_new, .25)
    rot = -3 + .8 * math.sin(t * 1.3)
    L = S5_X1 - S5_X0
    if not broke:
        body = P.time_strip(S5_X0, S5_Y, S5_X1, S5_K, bites, crumbs, seed=5)
    else:
        xa = S5_X0 + L * S5_BREAK[0]
        xb = S5_X0 + L * S5_BREAK[1]
        ua = (xa - S5_X0) / (xa - S5_X0)
        left = [(b[0] * L / (xa - S5_X0),) + tuple(b[1:]) for b in bites if b[0] < S5_BREAK[0] - .001]
        left.append((ua, 60, -1))
        right = [((b[0] * L - (xb - S5_X0)) / (S5_X1 - xb),) + tuple(b[1:]) for b in bites if b[0] > S5_BREAK[1] + .001]
        right.append((0.0, 58, 1))
        jolt = 8 * kick(t, ws(17), .2)
        body = (f'<g transform="translate(0 {-jolt:.2f}) rotate({-1.5 * jolt / 8:.2f} {xa:.1f} {S5_Y})">' +
                P.time_strip(S5_X0, S5_Y, xa, S5_K, left, seed=5) + "</g>" +
                f'<g transform="translate(0 {-jolt * .7:.2f}) rotate({1.5 * jolt / 8:.2f} {xb:.1f} {S5_Y})">' +
                P.time_strip(xb, S5_Y, S5_X1, S5_K, right, [(len(right) - 1, t - ws(17))], seed=6) + "</g>")
    # нитки-подвесы уходят вверх за кадр
    for xx in (S5_X0 + L * .05, S5_X0 + L * .95):
        body = line([(xx, S5_Y - 60), (xx + 30, -700)], 3, "#6E604A", taper=.1, wmin=.8, seed=int(xx) % 997) + body
    return f'<g transform="translate(0 {sway:.2f}) rotate({rot:.2f} 540 {S5_Y})">{body}</g>'


def s05(t):
    a0 = T0("s05") - .2
    look = ws(15)        # «куда» — задирает голову
    bite = ws(16)        # «делись» — укус
    brk = ws(17)         # «двадцать» — кусок отламывается
    hit_t = we(17)       # кусок долетает до носа к концу слова
    broke = t >= brk
    o = [_sky05(t)]
    o.append(_strip05(t, broke))
    # Дима: хлопает по карманам → голова вверх → разводит руками → кусок по носу
    hx, hy = S5_HIP
    up = ease_io(ramp(t, look - .1, .25))
    shrug = ease_io(ramp(t, bite + .05, .22)) * (1 - ease_io(ramp(t, hit_t + .05, .3)))
    pat = .5 + .5 * math.sin((t - a0) * 2 * math.pi * 3.2)
    hit = kick(t, hit_t, .22)
    if t < look:
        pose, u, e = ("d82_rest", "d82_pocket"), .45 + .55 * pat, ex("panic82", look=(.3, .6))
    elif shrug > .01:
        pose, u, e = ("d82_look_up", "d82_shrug"), shrug, ex("puzzled82", look=(.2, -1.0))
    else:
        pose, u, e = ("d82_pocket", "d82_look_up"), up, ex("puzzled82", look=(.3, -.9))
    if t >= hit_t - .02:
        e = ex("squint82", look=(.15, -1.0), mouth="o", open=.4)
        pose, u = ("d82_shrug", "d82_look_up"), ease_io(ramp(t, hit_t, .3))
    bob = 6 * math.sin((t - a0) * 2 * math.pi * 3.2) * (1 - up)
    fy = hy + bob + 18 * hit
    fig = people.dima82(hx, fy, S5_K, e, pose, t=t, u=u, head_add=-.06 * hit, lean_add=-.04 * hit, feet=people.stand_kw(hx, fy, S5_K)["feet"])
    o.append(fig["svg"])
    # кусок падает на нос
    if broke:
        L = S5_X1 - S5_X0
        sx = S5_X0 + L * (S5_BREAK[0] + S5_BREAK[1]) / 2
        nose = (fig["mouth"][0] + 10, fig["mouth"][1] - 8)
        ff = clamp((t - brk) / max(.1, hit_t - brk))
        if t < hit_t:
            px = lerp(sx, nose[0], ff)
            py = lerp(S5_Y, nose[1] - 30, ff * ff)
            rot = -3 + 171 * ff
        else:
            v = t - hit_t
            px = nose[0] + 20 * math.sin(min(v, .5) * 5)
            py = nose[1] - 30 - 26 * math.exp(-v * 9) * abs(math.sin(v * 22))
            rot = 168 + 9 * math.exp(-v * 6) * math.sin(v * 26)
        o.append(P.strip_piece(px, py, S5_K * .7, (S5_BREAK[1] - S5_BREAK[0]) * L / S5_K, rot, seed=3))
        if 0 < t - hit_t < .3:
            o.append(P.click(nose[0] + 20, nose[1] - 70, 1.0, ramp(t, hit_t, .3), seed=5))
    # камера: медленный наезд снизу вверх к ленте; толчок на «двадцать»
    z = ease_io(ramp(t, a0, T1("s05") - a0))
    k_ = kick(t, hit_t, .25)
    s = lerp(1.0, 1.08, z) + .05 * bump(t, brk, .05, .05, .3)
    cx = 540 + 6 * math.sin(t * 1.4)
    cy = lerp(1010, 900, z) + 14 * k_
    return frame_svg("".join(o), cx, cy, s, lerp(-1.2, .6, z) + .8 * k_, "#9ccdf0")


# ═══════════════════════════════ общее для прихожей ═══════════════════════════════
DX = 780.0               # Дима в прихожей лицом влево (flip), таз по x
DK = .85
DHY = FL - 598 * DK
STOOL = HA["stool"]
DOOR_STRIP = (400.0, 560.0)     # где у двери (на стене над крючками) висит короткая лента «как помнится» (s10 → s11)
DOOR_STRIP_W = 300.0


def mir(p):
    """Цель руки для Димы с flip=True: figure зеркалит вокруг таза, поэтому цели задаются в незеркальном мире."""
    return (2 * DX - p[0], p[1])


def dima_h(t, expr, pose="d82_rest", u=1.0, tn=None, tf=None, hn=None, hf=None, x=DX, **kw):
    arms, hands = {}, {}
    if tn is not None:
        arms["n"] = ("ik", (2 * x - tn[0], tn[1]), -1)
    if tf is not None:
        arms["f"] = ("ik", (2 * x - tf[0], tf[1]), -1)
    if hn:
        hands["n"] = hn
    if hf:
        hands["f"] = hf
    return people.dima82(x, DHY, DK, expr, pose, t=t, u=u, flip=True, feet=people.stand_kw(x, DHY, DK)["feet"], arms=arms, hands=hands, **kw)


def strip_seg(p0, p1, k=1.0, bites=(), crumbs_t=(), seed=0):
    """Лента от p0 до p1 (повёрнута), средняя линия по отрезку."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    if L < 2:
        return ""
    a = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    return (f'<g transform="translate({p0[0]:.2f} {p0[1]:.2f}) rotate({a:.2f})">' +
            P.time_strip(0, 0, L, k, bites, crumbs_t, seed=seed) + "</g>")


def door_strip(t, t_in, k=.7, w=DOOR_STRIP_W):
    """Короткая лента на двери: прилипает с выскоком в t_in (до — нет)."""
    if t < t_in:
        return ""
    sx, sy = P.squash(t, t_in, amp=.3)
    x, y = DOOR_STRIP
    body = P.time_strip(-w / 2, 0, w / 2, k, [(0.0, 26, -1), (1.0, 24, 1)], seed=10)
    pin = shape(ellipse_pts(-w / 2 + 18, 0, 11, 11, 12), "#D9483B", blob(ellipse_pts(-w / 2 + 15, -3, 4, 4, 8), "#F28C7E"), w=2.4, seed=1010)
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({sx:.4f} {sy:.4f}) rotate(-3)">{body}{pin}</g>'


# ═══════════════════════════════ s10: вечер, отмеряет короткую ленту ═══════════════════════════════
ROLL10 = (STOOL[0] - 70, STOOL[1] - 4)       # низ рулона на сиденье табуретки
ROLL_K = .78


def s10(t):
    a0 = T0("s10") - .2
    nod = ws(38)         # «помнит» — кивок
    pull = ws(40)        # «сборы» — тянет ленту из рулона
    cut = ws(42)         # «десять» — чик
    stick = we(43) - .25  # к концу «минут» лента прилипает к двери
    h = room.hall82(t, "evening")
    o = [h["bg"], h["door"](0.0)]
    o.append(door_strip(t, stick))
    pu = ease_io(ramp(t, pull - .05, .45))
    R = P.tape_roll_r(ROLL_K, .05 + .1 * pu)
    rc = (ROLL10[0], ROLL10[1] - R)
    tail = (rc[0] + R * .55, rc[1] - R * .82)          # откуда лента сходит с рулона (верх, вправо)
    o.append(shadow(rc[0], ROLL10[1] + 2, R * 1.1, .25))
    o.append(P.tape_roll(rc[0], rc[1], ROLL_K, .05 + .1 * pu, -40 - 300 * pu + 4 * math.sin(t * 3), seed=2))
    # ближняя рука тянет конец ленты к себе: коротко
    grab = (tail[0] + 40, tail[1] + 10)
    endp = (DX - 120, DHY + 30)
    tn = (lerp(grab[0], endp[0], pu), lerp(grab[1], endp[1], pu) - 50 * math.sin(math.pi * pu))
    # дальняя рука с ножницами: у груди → к ленте у рулона → чик → назад
    reach = ease_io(ramp(t, pull + .5, cut - pull - .55))
    back = ease_io(ramp(t, cut + .15, .3))
    cutp = (tail[0] + 46, lerp(tail[1], endp[1], 46 / max(1.0, endp[0] - tail[0])))
    rest_f = (DX - 120, DHY - 120)
    tf = (lerp(rest_f[0], cutp[0] + 40, reach * (1 - back)), lerp(rest_f[1], cutp[1] - 30, reach * (1 - back)))
    nodu = bump(t, nod - .04, .1, .05, .25)
    lift = ease_io(ramp(t, cut + .2, stick - cut - .2))
    if t > cut + .2:          # поднимает кусок, довольный
        tn = (lerp(tn[0], DX - 170, lift), lerp(tn[1], DHY - 260, lift))
    e = ex("sure82", look=(.8, .4)) if t < cut + .1 else ex("proud82", look=(.7, -.6) if t > stick - .35 else (.7, .3))
    fig = dima_h(t, e, tn=tn, tf=tf, hn={"dir": (-1, .1), "curl": (.62, .66, .7, .72), "thumb": .6},
                 hf={"dir": (-1, -.1), "curl": (.6, .62, .66, .7), "thumb": .55}, head_add=.12 * nodu - .03 + .05 * reach, lean_add=.05 * reach)
    hold_n = fig["hold"]
    hold_f = fig["hold_f"]
    snip = clamp((t - cut) / .08) if t >= cut else 0.0
    if t < cut:
        o.append(strip_seg(tail, hold_n, .55, seed=11))
    else:
        dang = ease_out(ramp(t, cut, .4), 2)
        stub_end = (lerp(cutp[0], tail[0] + 30, dang), lerp(cutp[1], tail[1] + 110, dang))
        o.append(strip_seg(tail, stub_end, .55, [(1.0, 18, -1)], seed=12))
    sc_svg = P.scissors(hold_f[0] - 10, hold_f[1], .62, 1.0, 180, seed=4)
    if reach < .35 and t < cut - .3 or t > cut + .35:
        o.append(sc_svg)          # ножницы в дальней руке за телом
    o.append(fig["svg"])
    if t >= cut and t < stick:
        fly = ease_io(ramp(t, stick - .3, .3))
        L0 = math.hypot(hold_n[0] - cutp[0], hold_n[1] - cutp[1])
        if fly <= 0:
            hang = ease_out(ramp(t, cut, .3), 2)
            pe = (lerp(cutp[0], hold_n[0] - 40, hang), lerp(cutp[1], hold_n[1] + L0 * .9, hang))
            o.append(strip_seg(hold_n, pe, .55, [(1.0, 18, 1)], seed=13))
        else:
            x0 = lerp(hold_n[0], DOOR_STRIP[0] - DOOR_STRIP_W * .35, fly)
            y0 = lerp(hold_n[1], DOOR_STRIP[1], fly) - 160 * math.sin(math.pi * fly)
            o.append(strip_seg((x0, y0), (x0 + DOOR_STRIP_W * .7, y0 + 30 * (1 - fly)), .55 + .15 * fly, seed=13))
    # ножницы в дальней руке (лезвия к рулону — влево)
    opn = .5 + .5 * math.sin((t - a0) * 10) if .2 < reach and t < cut else 0.0
    sn = snip if t >= cut else (.15 + .5 * (1 - opn) if reach > .2 else 1.0)
    if not (reach < .35 and t < cut - .3 or t > cut + .35):
        o.append(P.scissors(hold_f[0] - 10, hold_f[1], .62, sn, 180 + 10 * reach, seed=4))
    if 0 < t - cut < .25:
        o.append(P.click(cutp[0], cutp[1] - 30, .9, ramp(t, cut, .25), seed=7))
    # камера: сбоку, микродрейф; толчок на «десять»; к концу — к двери за лентой
    k_ = kick(t, cut, .22)
    pan = ease_io(ramp(t, cut + .25, stick - cut))
    s = 1.3 + .02 * ramp(t, a0, 2) + .07 * bump(t, cut, .05, .08, .45)
    cx = lerp(580, 540, pan) + 8 * math.sin(t * .9)
    cy = lerp(1060, 930, pan) + 6 * math.sin(t * 1.3) + 12 * k_
    return frame_svg("".join(o), cx, cy, s, .3 * math.sin(t * .8) + .7 * k_, "#c79a7c", vignette("#2a140a", .25))


# ═══════════════════════════════ s17: вечер, секундомер ═══════════════════════════════
def s17(t):
    a0 = T0("s17") - .2
    take = ws(71)        # «Поэтому» — достаёт секундомер
    one = ws(73)         # «один» — палец
    click = ws(75)       # «засёк» — щёлк
    h = room.hall82(t, "evening")
    o = [h["bg"], h["door"](0.0)]
    # кот на табуретке следит за секундомером
    out = ease_out(ramp(t, take - .1, .45), 2)
    sw_c = (lerp(DX - 70, DX - 240, out), lerp(DHY + 110, DHY - 50, out))
    cx_c, cy_c = STOOL[0] - 10, STOOL[1]
    look_x = clamp((sw_c[0] - cx_c) / 400, -1, 1)
    st = dict(people.CAT_ST["watch82"])
    st.update(look=(.7 * look_x + .2, lerp(.6, -.2, out)), tilt=-4 + 6 * bump(t, click, .06, .1, .3), perk=.9 + .3 * bump(t, click, .05, .1, .3),
              blink=1.0 if (t % 3.1) < .08 else 0.0, tail=6 * math.sin(t * 2.2))
    o.append(shadow(cx_c, cy_c + 4, 120, .22))
    o.append(people.cat_svg(cx_c, cy_c, 1.0, st, t))
    # ближняя рука: у бедра → палец «один» вверх → большой палец на кнопку
    up = bump(t, one - .1, .2, max(.05, click - one - .35), .2)
    press = ease_io(ramp(t, click - .22, .2))
    crown = (sw_c[0], sw_c[1] - 105)
    rest_n = (DX - 40, DHY + 130)
    raise_n = (DX - 330, DHY - 380)
    tn = (lerp(lerp(rest_n[0], raise_n[0], up), crown[0] + 26, press), lerp(lerp(rest_n[1], raise_n[1], up), crown[1] + 50, press))
    if press > .5:
        hn = {"dir": (-.35, -1), "curl": (.7, .75, .8, .8), "thumb": .0}
    elif up > .3:
        hn = {"dir": (-.1, -1), "curl": (0, .9, .9, .9), "spread": .05, "thumb": .75}
    else:
        hn = {"curl": (.4, .4, .45, .5), "thumb": .4}
    tf = (sw_c[0] + 20, sw_c[1] + 60)
    e = ex("sure82", look=(.6, .35)) if t < one else (ex("proud82", look=(.3, -.5)) if t < click - .2 else ex("calm82", look=(.7, .45)))
    kw = dict(tn=tn, tf=tf, hn=hn, hf={"dir": (-1, -.3), "curl": (.62, .66, .7, .72), "thumb": .6}, head_add=.06 * up - .02, lean_add=.02 * press)
    fig = dima_h(t, e, layers=("legs", "pelvis", "arm_f", "body"), **kw)
    o.append(fig["svg"])
    # секундомер в дальней руке, ближняя рука поверх
    cl = bump(t, click, .04, .06, .12)
    run = max(0.0, t - click - .02)
    ha = 140 * run
    k_sw = lerp(.25, .52, out)
    o.append(P.stopwatch(sw_c[0], sw_c[1], k_sw, ha, 0.0, cl, t, seed=1))
    o.append(dima_h(t, e, layers=("arm_n",), **kw)["svg"])
    # камера: мягкий наезд к секундомеру; толчок на «засёк»
    z = ease_io(ramp(t, a0, T1("s17") - a0))
    k_ = kick(t, click, .22)
    s = lerp(1.3, 1.4, z) + .05 * bump(t, click, .04, .06, .4)
    cx = lerp(560, sw_c[0] - 20, z) + 6 * math.sin(t)
    cy = lerp(1000, sw_c[1] - 10, z) + 10 * k_
    return frame_svg("".join(o), cx, cy, s, .5 * k_ - .2 * z, "#c79a7c", vignette("#2a140a", .25))


# ═══════════════════════════════ s11: утро, настоящая лента улетает за дверь ═══════════════════════════════
LAND11 = 130.0           # глубина площадки за дверью на экране
Y11 = 1650.0             # средняя линия ленты на полу (перед ковриком)
X11_TAIL = -800.0        # лента утра тянется из-за левого края кадра
K11 = .8


def _roll11(t):
    """Где рулон: (x, y низа, масштаб, видим ли, угол). Путь: пол → порог → вглубь, на лестницу."""
    go = ws(47)          # «уходит»
    door = ws(48)        # «двадцать» — в дверь
    five = ws(49)        # «пять»
    x_start, x_floor = 160.0, HA["door"][0]
    dx, fy = HA["door"]
    if t < go:
        tw = 6 * math.sin(t * 17) * ramp(t, go - .4, .3)
        return x_start + tw, Y11 + 40, K11, True, tw * 3
    if t < door:
        u = (t - go) / (door - go)
        x = lerp(x_start, x_floor, u * u * (1.6 - .6 * u))
        return x, Y11 + 40, K11, True, -(x - x_start) * .9
    u = clamp((t - door) / max(.2, five - door + .1))
    return dx, lerp(Y11 + 40, fy - LAND11 + 10, ease_out(u, 1.6)), lerp(K11, .3, u), u < .92, -(x_floor - x_start) * .9 - 700 * u


def ease_in_(u):
    return u * u


def s11(t):
    a0 = T0("s11") - .2
    go = ws(47)
    door = ws(48)
    five = ws(49)
    h = room.hall82(t, "morning")
    dx, fy = HA["door"]
    ajar = ease_out(ramp(t, door - .12, .2), 2)
    o = [h["bg"], h["door"](ajar)]
    w2 = 236 * HA["door_k"]
    top = fy - 960 * HA["door_k"]
    if ajar > .01:
        # за дверью: площадка и лестница вниз, утренний свет
        xa = dx - w2 + 2 * w2 * (1 - .8 * ajar) + 6
        cid = lib.clip_of(rect_pts(xa, top, dx + w2, fy))
        st = [rect(xa - 10, top, dx + w2 + 10, fy, "#fff1cc")]
        st.append(blob([(dx - w2, fy - LAND11), (dx + w2, fy - LAND11), (dx + w2, fy), (dx - w2, fy)], "#e8cfa0"))
        for i in range(3):
            yy = fy - LAND11 + 45 * i
            st.append(line([(dx - w2, yy), (dx + w2, yy)], 3, "#c4a676", taper=0, wmin=1, seed=1100 + i))
        # край площадки и пролёт вниз: перила уходят вниз
        st.append(blob([(dx - w2, fy - LAND11 - 70), (dx + w2, fy - LAND11 - 70), (dx + w2, fy - LAND11), (dx - w2, fy - LAND11)], "#d9bb8a"))
        st.append(line([(dx - w2, fy - LAND11), (dx + w2, fy - LAND11)], 5, "#8a6a40", taper=0, wmin=1, seed=1105))
        st.append(shape([(dx + w2 - 120, top + 90, 1), (dx + w2 - 20, top + 90, 1), (dx + w2 - 20, top + 360, 1), (dx + w2 - 120, top + 360, 1)],
                        "#bfe3f4", blob(rect_pts(dx + w2 - 120, top + 260, dx + w2 - 20, top + 360), "#ffe9b0", .8), w=3.0, seed=1110))
        o.append(f'<g clip-path="url(#{cid})">{"".join(st)}</g>')
    # короткая лента у двери (с вечера)
    o.append(door_strip(t, -1))
    # длинная лента утра: по полу → к порогу → вглубь
    rx, ry, rk, vis, ang = _roll11(t)
    unr = clamp((rx - 160) / 900 + max(0.0, t - door) * .4)
    R = P.tape_roll_r(rk, .1 + .7 * unr)
    flat_end = min(rx, dx)
    o.append(P.time_strip(X11_TAIL, Y11, flat_end - (R * .4 if t < door else -44 * K11), K11, [(0.0, 30, -1)], seed=20))
    if t >= door:
        # лента уходит вглубь: трапеция по полу и площадке, ширина сужается
        tip = (rx, ry - R * .4)
        w0, w1 = 44 * K11 * 1.1, max(5.0, 55 * rk)
        poly = [(dx - w0, Y11 + 40 * K11), (tip[0] - w1, tip[1]), (tip[0] + w1, tip[1]), (dx + w0, Y11 + 40 * K11)]
        n = 14
        ticks = []
        for j in range(1, n):
            q = j / n
            yy = lerp(Y11 + 40 * K11, tip[1], q)
            ww = lerp(w0, w1, q)
            ln = .55 if j % 5 == 0 else .3
            ticks.append(line([(dx - ww, yy), (dx - ww * (1 - 2 * ln), yy)], 2.8 * (1 - q * .6), P.C_STRIP_TICK, taper=.1, wmin=.8, seed=1130 + j))
            ticks.append(line([(dx + ww, yy), (dx + ww * (1 - ln), yy)], 2.2 * (1 - q * .6), P.C_STRIP_TICK, taper=.1, wmin=.8, seed=1150 + j,
                              op=.75))
        ticks.append(blob([(dx + w0 * .6, Y11 + 60), (tip[0] + w1 * .6, tip[1]), (tip[0] + w1, tip[1]), (dx + w0, Y11 + 60)], P.C_STRIP_SH, .8))
        ticks = "".join(ticks)
        o.append(shape(poly, P.C_STRIP, ticks, w=3.0, seed=1131))
    if vis:
        o.append(shadow(rx, ry + 2, R * 1.1, .25))
        o.append(P.tape_roll(rx, ry - R, rk, .1 + .7 * unr, ang, seed=3))
    # камера: у рулона → за ним → нырок в дверь на «двадцать» → отъезд: длинная против короткой на «пять»
    rush = ease_io(ramp(t, door - .1, .3))
    back = ease_io(ramp(t, five - .12, .3))
    fx = clamp(rx, 300, 760)
    cx0, cy0, s0 = fx + 60, 1500.0, 1.25
    cx1, cy1, s1 = dx + 20, fy - 120, 1.7
    cx2, cy2, s2 = 620.0, 1300.0, .92
    cx = lerp(lerp(cx0, cx1, rush), cx2, back)
    cy = lerp(lerp(cy0, cy1, rush), cy2, back)
    s = lerp(lerp(s0, s1, rush), s2, back)
    k_ = kick(t, door, .2)
    return frame_svg("".join(o), cx + 6 * math.sin(t * 2), cy + 12 * k_, s, -1.0 * k_ + .5 * math.sin(t * .9), "#e9d6b4")


# ═══════════════════════════════ s18: утро ускоренно, сектор на двери ═══════════════════════════════
SW18 = (STOOL[0] - 40, STOOL[1] - 150 * .55 - 30)     # секундомер стоит на табуретке
SOCK18 = (STOOL[0] + 105, STOOL[1] - 2)
KETTLE18 = (HA["stove"][0] - 90, HA["stove"][1] - 20)
STICK18 = (720.0, 620.0)                              # наклейка-сектор на двери (левый верх полотна)
SEC18 = 150.0                                         # угол сектора — «как на деле»


def dima_at(t, x, flip, expr, pose="d82_rest", u=1.0, tn=None, tf=None, hn=None, hf=None, feet=None, **kw):
    arms, hands = {}, {}
    m = (lambda p: (2 * x - p[0], p[1])) if flip else (lambda p: p)
    if tn is not None:
        arms["n"] = ("ik", m(tn), -1)
    if tf is not None:
        arms["f"] = ("ik", m(tf), -1)
    if hn:
        hands["n"] = hn
    if hf:
        hands["f"] = hf
    return people.dima82(x, DHY, DK, expr, pose, t=t, u=u, flip=flip, feet=feet or people.stand_kw(x, DHY, DK)["feet"], arms=arms, hands=hands,
                         **kw)


def _x18(t):
    """Где Дима: у крючков → рывок к плите → рывок к двери → шаг в проём. (x, flip, скорость px/с)."""
    keys_t, kettle_t, door_t = ws(76) + .12, ws(77) - .02, ws(78) - .06
    pts = [(T0("s18") - .2, 700.0), (keys_t, 700.0), (keys_t + .1, 1180.0), (kettle_t, 1180.0), (kettle_t + .1, 1060.0)]
    for (ta, xa), (tb, xb) in zip(pts, pts[1:]):
        if ta <= t < tb:
            u = (t - ta) / (tb - ta)
            x = lerp(xa, xb, ease_io(u))
            v = (xb - xa) / (tb - ta) * (1.5 * math.sin(math.pi * u))
            return x, (xb < xa) if xb != xa else (xa < 900), v
    if t < pts[0][0]:
        return 700.0, True, 0.0
    _ = door_t
    return 1060.0, True, 0.0


def s18(t):
    a0 = T0("s18") - .2
    sb = ws(76)          # «сборы»
    now = ws(78)         # «теперь» — сектор летит на дверь
    out_ = ws(79)        # «выходит» — обувается
    num = ws(82)         # «цифре» — касается наклейки и выходит
    h = room.hall82(t, "morning")
    ajar = ease_io(ramp(t, num + .2, .35)) * .8
    o = [h["bg"], h["door"](ajar)]
    if ajar > .01:
        dx, fy = HA["door"]
        w2 = 236 * HA["door_k"]
        xa = dx - w2 + 2 * w2 * (1 - .8 * ajar) + 6
        o.append(blob(rect_pts(xa, fy - 960 * HA["door_k"], dx + w2, fy), "#fff6dc", .9))
    # наклейка-сектор на двери (летит с секундомера на «теперь»)
    fly = ease_io(ramp(t, now, .26))
    sweep = ease_io(ramp(t, sb, now - sb)) * SEC18
    if t >= now:
        sx0, sy0 = SW18
        px = lerp(sx0, STICK18[0], fly)
        py = lerp(sy0, STICK18[1], fly) - 260 * math.sin(math.pi * fly)
        if ajar > .01:          # полотно уходит к петле — наклейка с ним
            dx, fy = HA["door"]
            w2 = 236 * HA["door_k"]
            hx = dx - w2
            px = hx + (px - hx) * (1 - .8 * ajar)
        sq = P.squash(t, now + .26, amp=.3) if fly >= 1 else (1.0, 1.0)
        kk = lerp(.55, .9, fly)
        o.append(f'<g transform="translate({px:.2f} {py:.2f}) scale({sq[0]:.4f} {sq[1]:.4f}) translate({-px:.2f} {-py:.2f})">' +
                 P.sector_sticker(px, py, kk, SEC18, rot=360 * fly * (1 - fly) * 2, peel=0.0, seed=2) + "</g>")
    # табуретка: секундомер (стрелка бежит, закрашивает сектор) и носок-воришка щёлкает пустым ртом
    o.append(P.stopwatch(SW18[0], SW18[1], .55, sweep, sweep if t < now else 0.0, bump(t, sb - .05, .04, .05, .1), t, seed=3))
    sock_ch = chomp_osc(t, sb + .1, num + .6, 6.0) * (1 - ramp(t, num, .5) * .6)
    o.append(P.thief_sock(SOCK18[0], SOCK18[1], .45, sock_ch, t, seed=2, rot=-6 + 10 * ramp(t, num, .5)))
    # чайник на плите: пар до «и», потом выключен — крышка хлопает впустую
    steam = 1.0 - ramp(t, ws(77), .25)
    o.append(P.thief_kettle(KETTLE18[0], KETTLE18[1], .62, chomp_osc(t, ws(77) + .1, T1("s18") + .3, 5.0) * .8, steam, t, seed=2))
    # Дима
    x, flip, v = _x18(t)
    keys_in = t > sb + .05
    shoe = bump(t, out_ - .02, .15, max(.05, num - out_ - .45), .25)
    touch = bump(t, num - .1, .14, .25, .3)
    socks = ("sock", "sock") if t < out_ + .25 else None
    hk = (HA["keys"][0], HA["keys"][1] + 40)
    if t < sb + .1:
        tn = (lerp(x - 120, hk[0] + 40, ease_io(ramp(t, a0, .25))), lerp(DHY + 80, hk[1] + 40, ease_io(ramp(t, a0, .25))))
        e = ex("rush82", look=(.9, -.5))
        fig = dima_at(t, x, True, e, tn=tn, hn={"dir": (-.3, -1), "curl": (.55, .6, .65, .7), "thumb": .5}, socks=socks)
    elif not flip:          # у плиты: поворачивает ручку
        knob = (HA["stove"][0] - 110, HA["stove"][1] + 50)
        tn = (lerp(x + 120, knob[0], ease_io(ramp(t, ws(77) - .1, .1))), lerp(DHY + 40, knob[1], ease_io(ramp(t, ws(77) - .1, .1))))
        fig = dima_at(t, x, False, ex("rush82", look=(.8, .4)), tn=tn, tf=(x + 60, DHY - 40), hn={"dir": (1, .3), "curl": (.6, .65, .7, .75), "thumb": .55},
                      hf={"curl": (.62, .66, .7, .72), "thumb": .6}, socks=socks)
    elif shoe > .05:        # обувается
        fig = dima_at(t, x, True, ex("calm82", look=(.4, .9)), ("d82_rest", "d82_shoe"), u=shoe, socks=socks)
    else:
        tn = (lerp(x - 60, STICK18[0] + 40, touch), lerp(DHY + 100, STICK18[1] - 10, touch))
        hn = {"dir": (-1, -.4), "curl": (0, .9, .9, .9), "spread": .05, "thumb": .75} if touch > .3 else None
        e = ex("calm82", look=(.7, -.6)) if t > now else ex("rush82", look=(.8, -.3))
        fig = dima_at(t, x, True, e, tn=tn if touch > .01 or t > now else None, hn=hn, tf=(x - 90, DHY - 40) if keys_in else None,
                      hf={"curl": (.62, .66, .7, .72), "thumb": .6}, socks=socks)
    leave = ramp(t, num + .45, .55)
    if leave > 0:          # поворачивается к проёму и шагает за порог
        wx = x + 110 * ease_io(leave)
        fig = people.dima82_walk(wx, DHY - 20 * leave, DK * (1 - .1 * leave), 1.3 * leave, t=t, expr="calm82", mug=False)
    body = fig["svg"]
    o.append(blurred(body, min(18.0, abs(v) * .006), 0.0))
    if abs(v) > 600:          # след рывка
        for j in range(3):
            o.append(line([(x - math.copysign(140 + 60 * j, v), DHY - 200 + 120 * j), (x - math.copysign(320 + 60 * j, v), DHY - 200 + 120 * j)],
                          6, "#8a6a40", taper=.6, wmin=.1, seed=1800 + j, op=.6))
    # ключи: на крючке → в руке (щёлкают пустыми бородками)
    kc = chomp_osc(t, a0, num + .5, 6.5) * (.4 if keys_in else .8)
    if not keys_in:
        o.append(P.thief_keys(hk[0], hk[1] - 40, .5, kc, t, seed=1))
    else:
        hp = fig["hold_f"] if (flip and shoe < .05 and leave <= 0) else fig["hold"]
        o.append(P.thief_keys(hp[0], hp[1] - 30, .42, kc, t, seed=1))
    # камера: дрейф к двери; толчок на «цифре»
    z = ease_io(ramp(t, a0, T1("s18") - a0))
    k_ = kick(t, num, .22)
    s = lerp(.86, .98, z) + .04 * bump(t, num, .05, .05, .35) + .03 * bump(t, now + .26, .04, .04, .25)
    cx = lerp(820, 880, z) + 6 * math.sin(t * 1.5)
    cy = lerp(1030, 990, z) + 10 * k_
    return frame_svg("".join(o), cx, cy, s, .6 * k_ + .3 * math.sin(t), "#e9d6b4")


# ═══════════════════════════════ воришки у табуретки (s09, s13) ═══════════════════════════════
KEYS_H = (HA["keys"][0], HA["keys"][1] - 40)          # точка подвеса ключей (средний крючок)
SOCK_S = (STOOL[0] + 70, STOOL[1] - 2)                # носок стоит на табуретке справа
KETTLE_S = (STOOL[0] - 110, STOOL[1] - 2)             # чайник на табуретке слева
TK = .55
TKK = .8                                              # ключи крупнее, иначе не читаются


def thieves(t, kc, sc, ec, steam=0.0, hop_k=0.0, hop_s=0.0, hop_e=0.0, tilt=(0.0, 0.0, 0.0)):
    """Три воришки: ключи на крючке, носок и чайник на табуретке. hop_* — подскок к ленте (px вверх)."""
    o = []
    o.append(f'<g transform="rotate({tilt[0]:.2f} {KEYS_H[0]:.1f} {KEYS_H[1]:.1f})">' +
             P.thief_keys(KEYS_H[0], KEYS_H[1] + hop_k, TKK, kc, t, seed=1) + "</g>")
    o.append(shadow(SOCK_S[0], SOCK_S[1] + 2, 60, .2))
    o.append(P.thief_sock(SOCK_S[0], SOCK_S[1] - hop_s, TK, sc, t, seed=1, rot=tilt[1]))
    o.append(shadow(KETTLE_S[0], KETTLE_S[1] + 2, 80, .2))
    ke = P.thief_kettle(KETTLE_S[0], KETTLE_S[1] - hop_e, TK, ec, steam, t, seed=1)
    o.append(f'<g transform="rotate({tilt[2]:.2f} {KETTLE_S[0]:.1f} {KETTLE_S[1]:.1f})">{ke}</g>')
    return "".join(o)


def mouths(hop_k=0.0, hop_s=0.0, hop_e=0.0):
    k = P.thief_keys_mouth(KEYS_H[0], KEYS_H[1] + hop_k, TKK)
    s_ = P.thief_sock_mouth(SOCK_S[0], SOCK_S[1] - hop_s, TK)
    e = P.thief_kettle_mouth(KETTLE_S[0], KETTLE_S[1] - hop_e, TK)
    return k, s_, e


# ═══════════════════════════════ s09: воришки оживают и кусают ═══════════════════════════════
def s09(t):
    a0 = T0("s09") - .2
    look = ws(35)        # «смотри» — нырок, оживают
    how = ws(36)         # «как» — разом кусают и замирают
    h = room.hall82(t, "morning")
    o = [h["bg"], h["door"](0.0)]
    alive = ramp(t, look, .1)
    frz = t >= how + .12
    jump = bump(t, how - .1, .1, .04, .2)
    if frz:
        kc, sc, ec = .0, .05, .0
    else:
        kc = alive * chomp_osc(t, look, how, 6.5) + .9 * bump(t, how - .1, .08, .02, .06)
        sc = alive * chomp_osc(t, look + .04, how, 5.5) + .9 * bump(t, how - .1, .08, .02, .06)
        ec = alive * chomp_osc(t, look + .08, how, 6.0) + .9 * bump(t, how - .1, .08, .02, .06)
    hk, hs, he = 26 * jump, 30 * jump + 8 * alive * abs(math.sin(t * 11)), 40 * jump + 8 * alive * abs(math.sin(t * 9 + 1))
    mk, ms, me = mouths(hk, hs, he)
    # свисающая лента проходит у всех трёх «ртов»
    sway = 6 * math.sin(t * 2.4)
    A = (820.0, 900.0 + sway)
    B = (mk[0] + 10, mk[1] + 50)
    C = (ms[0] + 10, ms[1] - 40)
    D = (me[0] - 10, me[1] - 50)
    E = (40.0, 1130.0 + sway)
    bit = t >= how
    bk = ramp(t, how, .06)
    kk = .62
    segs = [(A, B, [(.97, 46, 1, bk)] if bit else []), (B, C, [(.9, 40, -1, bk)] if bit else []), (C, D, [(.95, 44, -1, bk)] if bit else []),
            (D, E, [(.05, 40, -1, bk)] if bit else [])]
    for i, (p0, p1, bites) in enumerate(segs):
        o.append(strip_seg(p0, p1, kk, bites, [(0, t - how)] if bit and bites else [], seed=90 + i))
    o.append(thieves(t, kc, sc, ec, 0.0, hk, hs, he, tilt=(-6 * ramp(t, how + .1, .2), -8 * ramp(t, how + .1, .2), 5 * ramp(t, how + .1, .2))))
    if bit:          # в «ртах» — по кусочку ленты
        if t - how < .3:
            o.append(P.click(mk[0], mk[1] - 40, .8, ramp(t, how, .3), seed=11))
            o.append(P.click(me[0], me[1] - 50, .8, ramp(t, how, .3), seed=12))
    # камера: хлёст-нырок сверху на «смотри», стоп-удар на «как»
    w = whip(t, T0("s09"), 1.0, .24)
    tx, ty, ts = 450.0, 1100.0, 1.5
    cx = tx - 60 * w
    cy = ty - 900 * w
    s = ts * (1 - .25 * w) + .07 * bump(t, how, .03, .05, .3)
    k_ = kick(t, how, .2)
    body = "".join(o)
    blur = 22 * w
    if blur > .3:
        body = blurred(body, 2 * w, blur)
    return frame_svg(body, cx + 8 * k_, cy + 10 * k_, s, -4 * w + 1.0 * k_, "#e9d6b4")


# ═══════════════════════════════ s13: три укуса храповиком ═══════════════════════════════
Y13 = 1030.0
K13 = 1.3


def s13(t):
    a0 = T0("s13") - .2
    hits = [ws(54), ws(55), ws(56)]          # «ключи», «носок», «чайник»
    h = room.hall82(t, "morning")
    o = [h["bg"], h["door"](0.0)]
    n_done = sum(1 for x in hits if t >= x)
    # Дима позади: роется в куртке → на одной ноге → «ой»
    dx_ = 900.0
    if t < hits[1]:
        fig = people.dima82(dx_, DHY, DK, ex("panic82", look=(.5, .6)), "d82_pocket", t=t, flip=True,
                            feet=people.stand_kw(dx_, DHY, DK)["feet"], lean_add=.03 * math.sin(t * 9))
    elif t < hits[2]:
        fig = people.dima82_onefoot(dx_, DHY, DK, t=t, flip=True, wob=math.sin(t * 7), socks=("sock", "bare"))
    else:
        fig = people.dima82(dx_, DHY, DK, ex("wow82", look=(.9, .5)), "d82_pocket", t=t, flip=True, feet=people.stand_kw(dx_, DHY, DK)["feet"],
                            lean_add=-.04)
    o.append(fig["svg"])
    # лента: кусок за куском, после каждого укуса короче рывком (правый конец отскакивает)
    x0 = -160.0
    x1 = 1000.0
    for i, hx in enumerate(hits):
        if t >= hx:
            x1 -= 120 * (1 - math.exp(-(t - hx) * 12) * math.cos((t - hx) * 30))
    hop = [bump(t, hx - .09, .08, .03, .16) for hx in hits]
    hk, hs, he = 60 * hop[0], 60 * hop[1], 70 * hop[2]
    mk, ms, me = mouths(hk, hs, he)
    L = x1 - x0
    bites = [(.08, 40, -1), (.16, 34, 1), (.9, 36, -1)]
    crumbs = []
    for i, (m, side) in enumerate(((mk, -1), (ms, 1), (me, 1))):
        if t >= hits[i]:
            bites.append(((m[0] - x0) / L, 74 if i < 2 else 92, side, ramp(t, hits[i], .05)))
            crumbs.append((len(bites) - 1, t - hits[i]))
    o.append(P.time_strip(x0, Y13 + 6 * math.sin(t * 2.2), x1, K13, bites, crumbs, seed=31))
    ch = [bump(t, hx - .09, .05, .03, .1) for hx in hits]
    o.append(thieves(t, ch[0] * .95 + .15 * chomp_osc(t, a0, hits[0] - .1, 5), ch[1] * .95 + .15 * chomp_osc(t, a0, hits[1] - .1, 5),
                     ch[2] * .95 + .15 * chomp_osc(t, a0, hits[2] - .1, 5), steam=ramp(t, hits[2], .1) * (1 - ramp(t, hits[2] + .5, .3)),
                     hop_k=hk, hop_s=hs, hop_e=he))
    for i, (m, hx) in enumerate(zip((mk, ms, me), hits)):
        if 0 < t - hx < .28:
            o.append(P.click(m[0], m[1] - (60 if i == 0 else -10), 1.0, ramp(t, hx, .28), seed=20 + i))
    # камера: удар-наезд склейкой на каждый укус
    frames = [(560.0, 1060.0, 1.12), (600.0, 1040.0, 1.24), (560.0, 1090.0, 1.34), (520.0, 1110.0, 1.44)]
    cx, cy, s = frames[n_done]
    t_last = hits[n_done - 1] if n_done else a0
    dr = t - t_last
    s *= 1 + .02 * min(1.0, dr / 1.0)
    k_ = kick(t, t_last, .16) if n_done else 0.0
    return frame_svg("".join(o), cx + 10 * math.sin(t * 1.3), cy + 12 * k_, s, .8 * k_ + .3 * math.sin(t), "#e9d6b4")


SCENES = {"s05": s05, "s10": s10, "s17": s17, "s11": s11, "s18": s18, "s09": s09, "s13": s13}
_STATIC = [False]


def frame(sid, t):
    if not _STATIC[0]:
        lib.static_done()
        _STATIC[0] = True
    lib.dyn_begin()
    return SCENES[sid](t)
