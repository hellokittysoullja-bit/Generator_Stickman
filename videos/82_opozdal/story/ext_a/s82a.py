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


SCENES = {"s05": s05}
_STATIC = [False]


def frame(sid, t):
    if not _STATIC[0]:
        lib.static_done()
        _STATIC[0] = True
    lib.dyn_begin()
    return SCENES[sid](t)
