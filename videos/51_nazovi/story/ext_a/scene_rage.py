"""Рилс 51 «назови чувство», группа A: комната, телефон, злость.
s01 (0–1.5): ночь, Дима с телефоном, сообщение, лицо краснеет, влёт камеры.
s02 (1.5–4.3): руки сжимают телефон с сообщением, дрожь на «затряслись» (2.96), красные пары.
s05 (7.1–8.5): Дима яростно печатает ответ большими пальцами (альбомный телефон), пот, красное лицо.
s06 (8.5–10.8): экран крупно, злой ответ набран, палец над «отправить», на «извиняться» (9.76) облачко с кланяющимся Димой."""
import math

import numpy as np

import dima
import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, clip_of, clip_rect, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, mix, mul, rad_grad, rect_pts, shape, smooth, spring, svg)
from parts import sausage

SKIN, SKIN_SH, SKIN_SH2 = dima.SKIN, dima.SKIN_SH, dima.SKIN_SH2
HOOD, HOOD_SH, HOOD_SH2, FOLD = dima.HOOD, dima.HOOD_SH, dima.HOOD_SH2, dima.FOLD
RED = "#e8452c"
_ST = {}

# время слов (words.json)
T_ZATR = 2.96          # «затряслись»
T_IZV = 9.76           # «извиняться»


def rnd(k, a=0.0, b=1.0):
    """Детерминированное «случайное» по номеру."""
    x = math.sin(k * 127.1 + 311.7) * 43758.5453
    return a + (x - math.floor(x)) * (b - a)


def txt(x, y, s, size, color, anchor="start", extra=""):
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="IDB" font-weight="900" font-size="{f(size)}" fill="{color}" '
            f'text-anchor="{anchor}" {extra}>{s}</text>')


def G(inner, tx=0.0, ty=0.0, s=1.0, rot=0.0, extra=""):
    return f'<g transform="translate({f(tx)} {f(ty)}) rotate({f(rot)}) scale({s:.5f})" {extra}>{inner}</g>'


# ═══════════════════════════════ Дима (обёртка над dima.draw)
def dima_g(hip, bs, lean, expr, arms, hands=None, held=None, head_ang=0.0, hood=0.0, strings=(0, 0), lwk=1.0):
    dima.BS, dima.LWK = bs, lwk
    leg = (dima.THIGH + dima.SHIN) * bs * 0.96
    hx, hy = hip
    pose = dict(hip=(hx, hy), lean=lean, feet={"n": ((hx + 24 * bs, hy + leg), 0.0), "f": ((hx - 24 * bs, hy + leg), 0.0)},
                arms=arms, hands=hands or {"n": "fist", "f": "fist"}, head_ang=head_ang, expr=expr, hood=hood, strings=strings)
    if held:
        pose["held"] = held
    g, wr = dima.draw(pose)
    return g, wr


def head_world(hip, bs, lean, head_ang=0.0):
    up = dima.rot(np.array([0.0, -1.0]), lean)
    fw = dima.rot(np.array([1.0, 0.0]), lean)
    neck = up * (dima.TORSO + 52) + fw * 30
    hp = neck + dima.rot(np.array([24.0, -96.0]), lean * .5 + head_ang)
    return np.array(hip, float) + hp * bs


# ═══════════════════════════════ телефон
def ui_lines(x, y, widths, color="#a7aec2", h=16, gap=34, seed=0, op=1.0):
    return "".join(blob(rect_pts(x, y + k * gap, x + w, y + k * gap + h, h / 2), color, op) for k, w in enumerate(widths))


def phone_p_static():
    """Портрет 600×1240 (экран 560×1200): шапка чата, пузырь, строка ввода. Центр (0,0)."""
    s = []
    s.append(shape(rect_pts(-300, -620, 300, 620, 66), "#1b1d28", "", w=8, seed=11))
    return "".join(s)


def phone_p(t, shake=(0, 0), glow=1.0, msgs=1.0):
    """Телефон-портрет экраном к зрителю. msgs 0..: сколько пузырей показано."""
    o = [_ST["pp_body"]]
    cid = clip_rect(-280, -600, 560, 1200, 50)
    c = [blob(rect_pts(-280, -600, 280, 600), "#e9ecf4")]
    c.append(blob(rect_pts(-280, -600, 280, -470), "#3c64c8"))
    c.append(shape(ellipse_pts(-212, -535, 36, 36, 16), "#f2c9a6", "", w=3.4, seed=21))
    c.append(txt(-212, -519, "С", 46, "#3c64c8", "middle"))
    c.append(txt(-150, -520, "Саша", 44, "#ffffff"))
    c.append(blob(rect_pts(-150, -503, -40, -493, 5), "#9db6ee"))
    # пузырь 1 (пришёл раньше)
    c.append(shape(rect_pts(-250, -430, 110, -230, 34), "#ffffff", ui_lines(-222, -392, [290, 310, 190], "#9aa2b8", 18, 46), w=3.6, seed=22))
    # пузырь 2 — прилетает
    u = back_out(clamp(msgs - 0.0), 1.9)
    if msgs > 0:
        dy = (1 - u) * 80
        c.append(f'<g transform="translate(0 {f(dy)})" opacity="{clamp(msgs * 3):.3f}">' + shape(
            rect_pts(-250, -190, 170, 40, 34), "#ffffff", ui_lines(-222, -150, [340, 360, 300, 150], "#9aa2b8", 18, 46), w=3.6, seed=23) + "</g>")
    u3 = clamp(msgs - 1.0)
    if u3 > 0:
        dy = (1 - back_out(u3, 1.9)) * 80
        c.append(f'<g transform="translate(0 {f(dy)})" opacity="{clamp(u3 * 3):.3f}">' + shape(
            rect_pts(-130, 80, 250, 240, 34), "#ffffff", ui_lines(-102, 118, [300, 220], "#9aa2b8", 18, 46) +
            txt(215, 215, "!!", 56, RED, "end"), w=3.6, seed=24) + "</g>")
    # строка ввода
    c.append(blob(rect_pts(-280, 480, 280, 600), "#d5d9e6"))
    c.append(shape(rect_pts(-250, 506, 200, 574, 34), "#ffffff", "", w=3, seed=25))
    c.append(shape(ellipse_pts(236, 540, 30, 30, 14), "#3c64c8", "", w=3, seed=26))
    o.append(f'<g clip-path="url(#{cid})">{"".join(c)}</g>')
    # блик на стекле
    o.append(f'<g clip-path="url(#{cid})">' + blob([(-280, -600), (-60, -600), (-280, -300)], "#ffffff", .22) + "</g>")
    o.append(shape(ellipse_pts(0, -576, 12, 12, 12), "#1b1d28", "", w=2.6, seed=27))
    return "".join(o)


# ── альбомный телефон 1000×500 (экран 960×460), печать
KEYS = []
for r_, (n, y0, x0) in enumerate([(11, 18, -440), (10, 94, -410), (9, 170, -380)]):
    for k in range(n):
        KEYS.append((x0 + k * 80 + 34, y0 + 31, r_, k))
SENT = "Ты вообще меня слышишь?! Хватит!"


def phone_l_static():
    o = [shape(rect_pts(-500, -250, 500, 250, 56), "#1b1d28", "", w=8, seed=31)]
    cid = clip_rect(-480, -230, 960, 460, 40)
    c = [blob(rect_pts(-480, -230, 480, 230), "#e9ecf4")]
    c.append(blob(rect_pts(-480, -230, 480, -150), "#3c64c8"))
    c.append(shape(ellipse_pts(-420, -190, 28, 28, 14), "#f2c9a6", "", w=3.2, seed=32))
    c.append(txt(-420, -176, "С", 36, "#3c64c8", "middle"))
    c.append(txt(-372, -176, "Саша", 38, "#ffffff"))
    # серый пузырь входящего
    c.append(shape(rect_pts(-450, -138, -70, -76, 28), "#ffffff", ui_lines(-424, -122, [250, 140], "#9aa2b8", 14, 28), w=3, seed=33))
    # клавиатура
    c.append(blob(rect_pts(-480, 0, 480, 230), "#cfd3e0"))
    for (x, y, r_, k) in KEYS:
        c.append(shape(rect_pts(x - 34, y - 31, x + 34, y + 31, 12), "#fbfbfe", blob(rect_pts(x - 34, y + 14, x + 34, y + 31, 10), "#c2c6d4"), w=2.6,
                       seed=40 + r_ * 12 + k))
    o.append(f'<g clip-path="url(#{cid})">{"".join(c)}</g>')
    return "".join(o), cid


def phone_l(typed, press_key=-1, press_amt=0.0, send_glow=0.0, caret=True, ink_red=0.0, show_msg=True):
    """typed — строка в поле ввода (одна строка, y -86..-14). Вторая часть экрана (статика) уже в _ST."""
    body, cid = _ST["pl"]
    o = [body]
    c = []
    # поле ввода
    c.append(shape(rect_pts(-450, -70, 340, 0, 32), "#ffffff", "", w=3.2, seed=51))
    col = mix("#2b2f45", "#7a1a14", ink_red)
    c.append(txt(-424, -22, typed, 40, col))
    # курсор
    if caret and typed is not None:
        wpx = 24.0 * len(typed) + 0
        c.append(blob(rect_pts(-424 + _text_w(typed, 40) + 4, -58, -424 + _text_w(typed, 40) + 9, -12), "#3c64c8"))
    # кнопка отправки
    c.append(shape(ellipse_pts(402, -35, 56, 56, 18), mix("#3c64c8", "#2f8bff", send_glow),
                   blob(ellipse_pts(402, -35, 56, 56, 18), "#ffffff", .25 * send_glow) +
                   "<path d=\"M378 -35 L428 -35 M410 -58 L432 -35 L410 -12\" stroke=\"#fff\" stroke-width=\"9\" stroke-linecap=\"round\" "
                   "stroke-linejoin=\"round\" fill=\"none\"/>", w=3.4, seed=52))
    if press_key >= 0 and press_amt > 0:
        x, y, _, _ = KEYS[press_key % len(KEYS)]
        c.append(blob(rect_pts(x - 34, y - 31, x + 34, y + 31, 12), "#ffe9a8", .95 * press_amt))
    o.append(f'<g clip-path="url(#{cid})">{"".join(c)}</g>')
    o.append(f'<g clip-path="url(#{cid})">' + blob([(-480, -230), (-200, -230), (-480, 60)], "#ffffff", .18) + "</g>")
    return "".join(o)


def _text_w(s, size):
    # приближённая ширина жирного шрифта IDB (кириллица): ~0.58 кегля на знак
    narrow = sum(1 for ch in s if ch in " ,.!?:;il")
    return (len(s) - narrow) * size * 0.60 + narrow * size * 0.30


# ═══════════════════════════════ руки
def thumb(base, tip, w=84, press=0.0, seed=0, sleeve_len=520, lit=0.0):
    """Большой палец (вид сверху, ноготь виден) от основания base к кончику tip; рукав горчичный уходит от основания назад."""
    base, tip = np.array(base, float), np.array(tip, float)
    v = tip - base
    L = float(np.linalg.norm(v))
    d = v / (L + 1e-9)
    n = np.array([-d[1], d[0]])
    P = lambda p: (float(p[0]), float(p[1]))
    o = []
    # рукав
    s0 = base - d * (sleeve_len + 90)
    s1 = base - d * 150
    sl = sausage([P(s0), P((s0 + s1) / 2 + n * 8), P(s1)], 250, 186)
    inner = blob([P(s0 + n * 10), P(s1 + n * 10), P(s1 + n * 90), P(s0 + n * 120)], HOOD_SH, .8)
    for k in range(3):
        c0 = s1 - d * (90 + k * 120)
        inner += line([P(c0 + n * 90), P(c0 + d * 14 - n * 4), P(c0 - n * 70)], 4, FOLD, seed=seed + 5 + k, op=.8, peak=.4)
    o.append(shape(sl, HOOD, inner, w=6, seed=seed + 1))
    # манжета
    c0 = base - d * 160
    cf = sausage([P(c0), P(base - d * 120)], 196, 192)
    rib = "".join(line([P(c0 + d * (6 + 10 * k) + n * 92), P(c0 + d * (6 + 10 * k) - n * 92)], 2.4, HOOD_SH2, seed=seed + 20 + k, op=.8) for k in range(4))
    o.append(shape(cf, HOOD_SH, rib, w=5, seed=seed + 2))
    # кисть (основание пальца): мягкий бугор
    palm = ellipse_pts(*(base - d * 40), 112, 96, 18, rot=math.degrees(math.atan2(d[1], d[0])))
    o.append(shape(palm, SKIN, blob(ellipse_pts(*(base - d * 40 + n * 38), 100, 54, 14, rot=math.degrees(math.atan2(d[1], d[0]))), SKIN_SH, .8), w=5.4, seed=seed + 3))
    # сам палец
    m = base + d * L * 0.5 + n * 5
    th = sausage([P(base - d * 20), P(m), P(tip)], w * 1.08, w * 0.86)
    ins = blob([P(base + n * (w * .16)), P(m + n * (w * .1)), P(tip + n * (w * .12)), P(tip + n * (w * .5)), P(m + n * (w * .5)), P(base + n * (w * .56))], SKIN_SH, .85)
    th_g = shape(th, SKIN, ins, w=5.6, seed=seed + 4)
    o.append(th_g)
    # складки сустава
    jc = base + d * L * 0.46
    for k, dd in enumerate((0, 20)):
        o.append(line([P(jc + d * dd + n * w * .34), P(jc + d * (dd + 5) + n * 0), P(jc + d * dd - n * w * .34)], 2.6, SKIN_SH2, seed=seed + 30 + k, op=.85, peak=.5))
    # ноготь
    ang = math.degrees(math.atan2(d[1], d[0]))
    nc = tip - d * (w * 0.52)
    nail = ellipse_pts(*nc, w * 0.40, w * 0.31, 14, rot=ang)
    o.append(shape(nail, "#f5d9c9", blob(ellipse_pts(*(nc - n * w * .05 - d * w * .08), w * .24, w * .1, 10, rot=ang), "#ffffff", .75), w=3.2, seed=seed + 5))
    if press > 0:
        o.append(blob(ellipse_pts(*tip, w * .6, w * .5, 14), "#ffffff", .0))
    return "".join(o)


def finger(x0, y0, ang, L, w, seed, bend=10.0, shade=SKIN_SH):
    """Палец, лежащий на экране: основание (x0, y0) у края телефона, направление ang (град.), длина L; подушечка-кончик круглая."""
    a = math.radians(ang)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])
    b = np.array([x0, y0], float)
    mid = b + d * L * 0.5 + n * bend
    tip = b + d * L
    P = lambda p: (float(p[0]), float(p[1]))
    poly = sausage([P(b - d * 40), P(mid), P(tip)], w * 1.04, w * 0.9)
    ins = blob([P(b + n * w * .2), P(mid + n * w * .15), P(tip + n * w * .12), P(tip + n * w * .5), P(mid + n * w * .5), P(b + n * w * .52)], shade, .85)
    jc = b + d * L * 0.52 + n * bend * 0.6
    cr = line([P(jc + n * w * .36), P(jc + d * 5), P(jc - n * w * .36)], 2.6, SKIN_SH2, seed=seed + 1, op=.85, peak=.5)
    cr += line([P(jc - d * 16 + n * w * .3), P(jc - d * 12), P(jc - d * 16 - n * w * .3)], 2.2, SKIN_SH2, seed=seed + 2, op=.7, peak=.5)
    return shape(poly, SKIN, ins + cr, w=5.2, seed=seed)


# ═══════════════════════════════ фон
def night_wall(extra=""):
    gid = lin_grad([(0, "#3b365f", 1), (1, "#201e3a", 1)])
    return f'<rect x="-1500" y="-1500" width="4200" height="5200" fill="url(#{gid})"/>'


def pattern_wall():
    DEFS.append('<pattern id="wp" width="120" height="120" patternUnits="userSpaceOnUse"><rect width="120" height="120" fill="none"/>'
                '<path d="M60 22 L68 40 L60 58 L52 40 Z" fill="#ffffff" opacity=".05"/><path d="M0 82 L8 100 L0 118 L-8 100Z M120 82 L128 100 L120 118 L112 100Z" fill="#ffffff" opacity=".05"/></pattern>')
    return '<rect x="-1500" y="-1500" width="4200" height="5200" fill="url(#wp)"/>'


def room_bg():
    s = [night_wall(), pattern_wall()]
    # окно слева с лунным светом
    win = rect_pts(-120, 150, 330, 700, 8)
    s.append(shape(win, "#0f1630", "", w=8, seed=61, ink_color="#120e1c"))
    s.append(blob(rect_pts(-100, 170, 310, 680), "#27386f"))
    s.append(shape(ellipse_pts(215, 300, 52, 52, 20), "#f3efd8", blob(ellipse_pts(232, 290, 44, 44, 20), "#d9d3b5", .6), w=0, ink=False, seed=62))
    s.append(blob(rect_pts(-100, 170, 310, 330), "#3a4f93", .5))
    for x in (105,):
        s.append(blob(rect_pts(x - 6, 160, x + 6, 690), "#120e1c"))
    s.append(blob(rect_pts(-130, 405, 340, 417), "#120e1c"))
    s.append(blob(rect_pts(-120, 690, 345, 722), "#5d4a63"))      # подоконник
    s.append(line([(-120, 722), (345, 722)], 5, INK, seed=63))
    # штора
    cur = [(-160, 130), (30, 150), (20, 420, 1), (60, 720, 1), (-160, 740)]
    s.append(shape(cur, "#5b3a5e", blob([(-160, 130), (-40, 140), (-60, 700), (-160, 740)], "#43294a", .8) + line([(-30, 190), (-20, 600)], 4, "#2e1b35", seed=64, op=.7), w=5.4, seed=65))
    # полка с книгами справа
    s.append(shape(rect_pts(690, 290, 1260, 312, 4), "#5a3b2a", blob(rect_pts(690, 304, 1260, 312), "#3d271b"), w=4.6, seed=66))
    x = 720
    cols = ["#b55347", "#4f7c9c", "#d7b04a", "#5f8e6a", "#8a5b9a", "#c9704a"]
    for k in range(9):
        w_ = 34 + 8 * (k % 3)
        h_ = 120 + 26 * ((k * 5) % 4)
        s.append(shape(rect_pts(x, 290 - h_, x + w_, 290, 3), cols[k % 6], blob(rect_pts(x + w_ - 9, 290 - h_, x + w_, 290), mul(cols[k % 6], (.8, .8, .8)), .8) +
                       blob(rect_pts(x, 290 - h_ + 18, x + w_, 290 - h_ + 26), "#f2e6c0", .7), w=3.6, seed=70 + k))
        x += w_ + 6
    # торшер (выключен) справа внизу и пол
    s.append(blob(rect_pts(-1500, 1560, 2700, 3000), "#171428"))
    s.append(blob(rect_pts(-1500, 1560, 2700, 1578), "#0e0b1c"))
    s.append(line([(-1500, 1560), (2700, 1560)], 4, INK, seed=67, op=.9))
    return "".join(s)


def glow(x, y, rx, ry, col, op, mode="screen"):
    gid = rad_grad([(0, col, op), (1, col, 0)], x, y, rx, ry)
    return f'<rect x="{f(x - rx)}" y="{f(y - ry)}" width="{f(rx * 2)}" height="{f(ry * 2)}" fill="url(#{gid})" style="mix-blend-mode:{mode}"/>'


def anger_mark(x, y, s, t_pop, t, col=RED):
    """Значок «злость» (четыре дуги крест-накрест), выскакивает с перелётом и пульсирует."""
    u = t - t_pop
    if u < 0:
        return ""
    k = back_out(clamp(u / 0.22), 2.6) * (1 + 0.06 * math.sin(u * 22))
    o = []
    for a0 in (0, 90, 180, 270):
        o.append(G(line([(22, 8), (62, 8 - 0), (70, 40), (44, 66)] if False else [(14, -10), (44, -34), (74, -30), (86, -4)], 17, col, taper=.5, wmin=.2, seed=90 + a0, peak=.5), 0, 0, 1, a0))
    return G("".join(o), x, y, s * k, 0)


def steam_puffs(x, y, t, seed, s=1.0, col=RED):
    """Пара красных штрихов-дуг, поднимающихся и гаснущих (цикл 0.5 с)."""
    o = []
    for k in range(2):
        ph = (t * 2.0 + seed * 0.37 + k * 0.5) % 1.0
        a = math.sin(ph * math.pi)
        dy = -ph * 120 * s
        sg = -1 if k else 1
        o.append(line([(x + sg * 16 * s, y + dy + 40 * s), (x + sg * 28 * s, y + dy), (x + sg * 16 * s, y + dy - 44 * s)], 11 * s, col, taper=.5, wmin=.15,
                      seed=seed * 7 + k, peak=.5, op=a * 0.95))
    return "".join(o)


def sweat(x, y, t, seed, s=1.0):
    ph = (t * 1.6 + seed * 0.43) % 1.0
    a = math.sin(ph * math.pi) ** 0.6
    dy = ph * 110 * s
    d = [(0, -34), (10, -12, 1), (14, 4), (0, 14), (-14, 4), (-10, -12, 1)]
    d = [(p[0] * s + x, p[1] * s + y + dy) + ((1,) if len(p) > 2 else ()) for p in d]
    return f'<g opacity="{a:.3f}">' + shape(d, "#a8dcf5", blob([(x - 2 * s, y + dy - 4 * s), (x + 8 * s, y + dy + 2 * s), (x, y + dy + 10 * s)], "#ffffff", .8), w=3.4 * s, seed=seed + 3) + "</g>"


def shake_off(t, t0, amp, hz=24.0, seed=0):
    """Дрожь: сумма синусов, нарастает после t0."""
    k = ease_out((t - t0) / 0.25) if t > t0 else 0.0
    return (amp * k * (math.sin(t * hz * 2 * math.pi + seed) * 0.6 + math.sin(t * hz * 1.7 * 2 * math.pi + seed * 2.1) * 0.4),
            amp * k * 0.8 * (math.sin(t * hz * 1.3 * 2 * math.pi + seed * 1.3) * 0.6 + math.cos(t * hz * 2.2 * 2 * math.pi + seed) * 0.4))


# ═══════════════════════════════ s01
def frame01(t):
    # камера: влёт 0.72→1.05 за 0.22 с, потом оседает и тихо наезжает; поворот −3° → 0
    if t < 0.22:
        z = 0.72 + (1.05 - 0.72) * ease_out(t / 0.22, 3)
    elif t < 0.55:
        z = 1.05 - 0.05 * ease_io((t - 0.22) / 0.33)
    else:
        z = 1.0 + 0.10 * ease_io((t - 0.55) / 1.15)
    rot = -3.0 * (1 - ease_out(t / 0.5, 2.5)) + 0.5 * math.sin(t * 9) * math.exp(-t * 2.0)
    # Дима
    bs = 1.5
    hip = (430, 1560)
    ang = clamp((t - 0.25) / 0.9)                       # прочёл → злость
    flush = clamp((t - 0.35) / 1.2) ** 0.8
    expr = dict(lid=0.45 + 0.4 * smooth(0.0, 0.4, t), look=(0.55, 0.62), brows="tired", brows2="det", brow_mix=ease_io(clamp((t - 0.45) / 0.55)),
                mouth="flat" if t < 0.95 else "grit", flush=flush, hair=2 * math.sin(t * 30) * smooth(0.9, 1.3, t))
    # дрожь рук нарастает
    tr = shake_off(t, 0.8, 5.0 * 1.0, 22)
    lean = 0.05 + 0.03 * smooth(0.6, 1.5, t)
    buzz = (math.sin(t * 2 * math.pi * 33) * 4.0 * (1 if t < 1.2 else 0.6), math.cos(t * 2 * math.pi * 27) * 3.0)

    def held(Wr, d):
        return phone_s01(t, Wr, d, buzz)
    tgt_n = (hip[0] + 420 + tr[0], hip[1] - 400 + tr[1])
    tgt_f = (hip[0] + 380 + tr[0] * .7, hip[1] - 330 + tr[1] * .6)
    g, wr = dima_g(hip, bs, lean, expr, {"n": ("ik", tgt_n), "f": ("ik", tgt_f)}, held=("behind", held), head_ang=0.03 * math.sin(t * 7) * smooth(0.8, 1.4, t))
    hw = head_world(hip, bs, lean)
    o = [_ST["bg"], g]
    # свет экрана на лице и вокруг телефона
    ph = wr["n"]
    flick = 0.75 + 0.25 * math.sin(t * 40)
    o.append(glow(ph[0] + 40, ph[1] - 150, 420, 420, "#8fc4ff", 0.55 * flick))
    o.append(glow(hw[0] + 70, hw[1] + 30, 240, 230, "#9ccaff", 0.35 * flick * (1 - 0.4 * flush)))
    # красное свечение злости
    o.append(f'<rect x="-1500" y="-1500" width="4200" height="5200" fill="{RED}" opacity="{0.10 * flush:.3f}" style="mix-blend-mode:multiply"/>')
    # значки: злость на виске, пот
    o.append(anger_mark(hw[0] - 60, hw[1] - 300, 1.1, 1.05, t))
    for k in range(3):
        if t > 1.15:
            o.append(steam_puffs(hw[0] + 40 + k * 70 - 70, hw[1] - 320, t, k + 1, 1.0))
    # вибрация-волны от телефона
    for k in range(3):
        ph_ = (t * 3.2 + k / 3) % 1.0
        o.append(f'<path d="M{f(ph[0] + 150 + ph_ * 70)} {f(ph[1] - 200)} q22 {f(60)} 0 {f(120)}" stroke="#d6e8ff" stroke-width="7" stroke-linecap="round" fill="none" opacity="{(1 - ph_) * 0.8:.3f}"/>')
        o.append(f'<path d="M{f(ph[0] - 70 - ph_ * 70)} {f(ph[1] - 200)} q-22 {f(60)} 0 {f(120)}" stroke="#d6e8ff" stroke-width="7" stroke-linecap="round" fill="none" opacity="{(1 - ph_) * 0.8:.3f}"/>')
    return "".join(o), cam(540, 960, z, rot)


def phone_s01(t, Wr, d, buzz):
    """Телефон в руке Димы (в L-единицах): экран к зрителю, прилетает сообщение."""
    sc = 0.24
    cx, cy = float(Wr[0]) + 40 + buzz[0] * 0.5, float(Wr[1]) - 70 + buzz[1] * 0.5
    rot = 8 + 2 * math.sin(t * 50)
    msgs = clamp(t / 0.35) + clamp((t - 0.6) / 0.3)
    return G(phone_p(t, msgs=min(msgs, 2.0)), cx, cy, sc, rot)


# ═══════════════════════════════ s02
def frame02(t):
    # t: 1.3 .. 4.5
    o = []
    z = 1.0 + 0.30 * ease_io(clamp((t - 1.3) / 3.0))
    sh = shake_off(t, T_ZATR, 12.0, 26, 1.0)
    # фон: тёмная комната, красный жар растёт
    heat = smooth(1.5, 3.6, t)
    o.append(_ST["wall"])
    for k in range(7):
        x, y = 120 + rnd(k) * 840, 200 + rnd(k + 9) * 1300
        r = 60 + rnd(k + 3) * 90
        o.append(glow(x, y, r, r, "#6e7fd8" if k % 2 else "#d9a35a", 0.20))
    pcx, pcy = 540, 940
    pr = -3 + 2.5 * math.sin(t * 1.7) * 0 + heat * -2
    px, py = pcx + sh[0], pcy + sh[1]
    # свет экрана
    flick = 0.8 + 0.2 * math.sin(t * 31)
    o.append(glow(px, py - 120, 640, 700, "#9cc8ff", 0.42 * flick))
    msgs = clamp((t - 1.3) / 0.01) + clamp((t - 2.0) / 0.35)
    # руки за телефоном (кисть у края) — задний план
    tight = 0.5 + 0.5 * smooth(1.4, 2.6, t)
    hands_back, hands_front = hands_grip(t, px, py, pr, tight, sh)
    o.append(f'<g transform="translate({f(px)} {f(py)}) rotate({f(pr)})">{hands_back}</g>')
    o.append(f'<g transform="translate({f(px)} {f(py)}) rotate({f(pr)})">{phone_p(t, msgs=min(msgs, 2.0) + (1 if t > 3.0 else 0) * 0)}</g>')
    o.append(f'<g transform="translate({f(px)} {f(py)}) rotate({f(pr)})">{hands_front}</g>')
    # красный жар по краям
    gid = rad_grad([(0.55, "#e8452c", 0), (1, "#e8452c", 1)], 540, 960, 900, 1250)
    o.append(f'<rect x="-1500" y="-1500" width="4200" height="5200" fill="{RED}" opacity="{0.12 * heat:.3f}" style="mix-blend-mode:multiply"/>')
    o.append(f'<rect x="-100" y="-100" width="1300" height="2100" fill="url(#{gid})" opacity="{0.55 * heat:.3f}" style="mix-blend-mode:multiply"/>')
    # пары-штрихи и значки злости
    for k, (x, y) in enumerate([(190, 300), (880, 270), (330, 170), (740, 160)]):
        if t > 1.6 + 0.12 * k:
            o.append(steam_puffs(x, y, t, k + 2, 1.2))
    o.append(anger_mark(110, 470, 1.4, 2.0, t))
    o.append(anger_mark(985, 520, 1.1, 2.7, t))
    return "".join(o), cam(540, 960 - 60 * ease_io(clamp((t - 1.3) / 3.0)), z, 0.6 * math.sin(t * 2.4))


def hands_grip(t, px, py, pr, tight, sh):
    """Две руки сжимают телефон с боков (кончики пальцев на экране). Возвращает (сзади, спереди) в системе телефона."""
    back, front = [], []
    tr = shake_off(t, T_ZATR, 3.0, 29, 2.0)
    for side in (-1, 1):
        ex = side * 300                        # край телефона
        # рукав и ладонь за телефоном
        s0 = (ex + side * 420, 1200)
        s1 = (ex + side * 60, 380)
        sl = sausage([s0, ((s0[0] + s1[0]) / 2 + side * 20, (s0[1] + s1[1]) / 2), s1], 330, 250)
        ins = blob([(s0[0] - side * 130, s0[1]), (s1[0] - side * 100, s1[1]), (s1[0] + side * 20, s1[1]), (s0[0] + side * 20, s0[1])], HOOD_SH, .8)
        for k in range(3):
            ins += line([(s0[0] + side * (-100 - 40 * k), 920 - 130 * k), (s0[0] - side * (200 + 40 * k), 880 - 130 * k + 20)], 4, FOLD, seed=300 + k + side, op=.8)
        back.append(shape(sl, HOOD, ins, w=6, seed=310 + side))
        cuff = sausage([(ex + side * 100, 420), (ex + side * 40, 300)], 250, 230)
        back.append(shape(cuff, HOOD_SH, "".join(line([(ex + side * (60 + 20 * k) - 110, 380 - 30 * k + 40), (ex + side * (60 + 20 * k) + 110, 380 - 30 * k - 30)], 2.4, HOOD_SH2, seed=320 + k, op=.8) for k in range(4)), w=5, seed=318 + side))
        palm = ellipse_pts(ex + side * 4, 190, 96, 230, 18)
        back.append(shape(palm, SKIN_SH, blob(ellipse_pts(ex + side * 30, 230, 70, 180, 16), SKIN_SH2, .6), w=5.4, seed=330 + side))
        # четыре пальца на экране
        for k in range(4):
            y0 = 90 + k * 76 + tr[1] * 0.3
            ln = [112, 128, 122, 100][k] + 14 * tight
            ang = (0 if side == 1 else 180) + (-1) * side * 0  # вправо от левого края: 0°, влево от правого: 180°
            a_ = ang + (k - 1.5) * 3.5 * (-side)
            x0 = ex - side * 56
            front.append(finger(x0 + tr[0] * 0.3, y0, a_, ln, 58, 340 + k * 7 + (0 if side < 0 else 40), bend=side * -6 * (1 if k % 2 else -1)))
    return "".join(back), "".join(front)


# ═══════════════════════════════ s05 / s06: печать
def key_pos(i):
    x, y, _, _ = KEYS[i % len(KEYS)]
    return x, y


T_TYPE0 = 6.95
RATE = 19.0            # знаков в секунду
CHARS = list(SENT)


def typed_at(t):
    n = int(max(0.0, (t - T_TYPE0)) * RATE)
    return SENT[:min(n, len(SENT))], n


def key_for(n):
    """Какой клавише соответствует n-й знак (псевдослучайно, левая/правая половина по чётности)."""
    k = int(rnd(n * 3 + 1, 0, len(KEYS)))
    left = [i for i, kk in enumerate(KEYS) if kk[0] < 0]
    right = [i for i, kk in enumerate(KEYS) if kk[0] >= 0]
    return (left if n % 2 == 0 else right)[k % len(left if n % 2 == 0 else right)]


def thumbs_world(t, pcx, pcy, sc, rot, mode="type", t_b=None):
    """Два больших пальца в мире: основание — у боковых краёв телефона (внизу), кончик — на клавише. Возвращает (svg, n_press, key)."""
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def W_(p):
        x, y = p[0] * sc, p[1] * sc
        return (pcx + x * ca - y * sa, pcy + x * sa + y * ca)

    o = []
    typed, n = typed_at(t)
    ph = (t - T_TYPE0) * RATE
    cur_k, cur_press = -1, 0.0
    for side in (-1, 1):
        # индекс «нажатия» этой руки: чётные — левая, нечётные — правая
        m = int(math.floor(ph / 2.0 + (0 if side < 0 else -0.5)))
        fr = (ph / 2.0 + (0 if side < 0 else -0.5)) - m
        k_cur = key_for(2 * m + (0 if side < 0 else 1)) if t > T_TYPE0 else (2 if side < 0 else 7)
        k_prev = key_for(2 * (m - 1) + (0 if side < 0 else 1)) if m > 0 else (3 if side < 0 else 8)
        a = ease_io(clamp(fr / 0.5))
        kx0, ky0 = key_pos(k_prev)
        kx1, ky1 = key_pos(k_cur)
        kx, ky = kx0 + (kx1 - kx0) * a, ky0 + (ky1 - ky0) * a
        press = math.sin(clamp((fr - 0.45) / 0.55) * math.pi) if t > T_TYPE0 else 0.0
        lift = math.sin(clamp(fr / 0.5) * math.pi) * 22
        tip = W_((kx + side * 10, ky + 18 - lift))
        base = W_((side * 640, 170))
        v = np.array(tip) - np.array(base)
        o.append(thumb(base, np.array(tip) - np.array([0, 0]) , w=100, seed=500 + (0 if side < 0 else 60), sleeve_len=300))
        if press > cur_press and fr > .45:
            cur_press, cur_k = press, k_cur
    return "".join(o), cur_k, cur_press


def frame05(t):
    z = 1.0 + 0.16 * ease_io(clamp((t - 6.9) / 1.8))
    o = [_ST["wall"]]
    for k in range(6):
        x, y = 100 + rnd(k + 20) * 880, 100 + rnd(k + 29) * 1500
        r = 70 + rnd(k + 13) * 90
        o.append(glow(x, y, r, r, "#d9a35a" if k % 2 else "#6e7fd8", 0.18))
    sh = shake_off(t, 6.9, 5.0, 31, 3.0)
    # Дима сверху
    bs = 1.55
    heat = 0.6 + 0.4 * smooth(6.9, 8.2, t)
    hip = (360, 1210)
    expr = dict(lid=0.8, look=(0.45, 0.8), brows="det", mouth="grit", flush=0.7 + 0.25 * smooth(6.9, 8.0, t),
                hair=3 * math.sin(t * 34), brow_mix=0.0)
    g, wr = dima_g(hip, bs, 0.0, expr, {"n": ("ik", (hip[0] + 430, 900)), "f": ("ik", (hip[0] - 40, 930))}, head_ang=0.08 + 0.03 * math.sin(t * 29), hood=4 * math.sin(t * 33))
    hw = head_world(hip, bs, 0.0, 0.08)
    o.append(f'<g transform="translate({f(sh[0] * .5)} {f(sh[1] * .5)})">{g}</g>')
    gid = lin_grad([(0, "#201e3a", 0), (1, "#201e3a", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="-200" y="1000" width="1500" height="260" fill="url(#{gid})"/><rect x="-200" y="1259" width="1500" height="900" fill="#201e3a"/>')
    # телефон альбомный
    pcx, pcy, sc = 540 + sh[0], 905 + sh[1], 0.86
    rot = -2.0 + 1.2 * math.sin(t * 8)
    typed, n = typed_at(t)
    ph = (t - T_TYPE0) * RATE
    th, kk, pr = thumbs_world(t, pcx, pcy, sc, rot)
    flick = 0.85 + 0.15 * math.sin(t * 28)
    o.append(glow(pcx, pcy - 40, 760, 420, "#9cc8ff", 0.35 * flick))
    body = phone_l(typed, press_key=kk, press_amt=pr, send_glow=0.0, ink_red=0.0)
    o.append(G(body, pcx, pcy, sc, rot))
    o.append(th)
    o.append(f'<rect x="-1500" y="-1500" width="4200" height="5200" fill="{RED}" opacity="{0.10 * heat:.3f}" style="mix-blend-mode:multiply"/>')
    # пот, пары, значок злости у головы
    for k, dx in enumerate((-230, 215, 250)):
        o.append(sweat(hw[0] + dx, hw[1] - 150 + k * 80, t, k + 1, 1.5))
    for k, x in enumerate((hw[0] - 170, hw[0] + 20)):
        o.append(steam_puffs(x, hw[1] - 330, t, k + 5, 1.2))
    o.append(anger_mark(hw[0] + 230, hw[1] - 250, 1.2, 7.0, t))
    return "".join(o), cam(540, 960, z, 0.5 * math.sin(t * 3.1))


# ═══════════════════════════════ s06
def cloud_pts(cx, cy, rx, ry, n=9, seed=0):
    pts = []
    hw = math.pi / n
    for k in range(n):
        ac = 2 * math.pi * k / n
        for da, rr, cor in ((-hw, 0.88, 1), (-hw * .55, 1.08, 0), (0, 1.14 + 0.03 * math.sin(k * 2.3 + seed), 0), (hw * .55, 1.08, 0)):
            a = ac + da
            pts.append((cx + rx * rr * math.cos(a), cy + ry * rr * math.sin(a)) + ((1,) if cor else ()))
    return pts


def bow_dima(t, tb):
    """Мини-Дима в облачке кланяется (в системе облачка, центр (0,0))."""
    u = t - tb
    lean = 1.25 * spring(clamp(u / 0.9) * 0.9, 2.2, 5.0) if u > 0 else 0.0
    lean = clamp(lean, 0, 1.45)
    bs = 0.36
    hip = (-40, 40)
    expr = dict(lid=0.45, look=(0.5, 0.7), brows="worry", mouth="sorry", flush=max(0.0, 0.55 - 0.5 * clamp(u / 1.3)))
    arms = {"n": ("ang", 0.35, 0.5), "f": ("ang", 0.2, 0.5)}
    g, _ = dima_g(hip, bs, lean, expr, arms, head_ang=0.25 * clamp(u / .8), lwk=1.5)
    return g


def frame06(t):
    # t: 8.3 .. 11.0
    z = 1.04 + 0.07 * ease_io(clamp((t - 8.3) / 2.7))
    o = [_ST["wall"]]
    for k in range(6):
        x, y = 100 + rnd(k + 40) * 880, 100 + rnd(k + 49) * 1500
        r = 70 + rnd(k + 33) * 90
        o.append(glow(x, y, r, r, "#d9a35a" if k % 2 else "#6e7fd8", 0.17))
    sh = shake_off(t, 8.3, 4.0, 27, 5.0)
    pcx, pcy, sc = 540 + sh[0] * .5, 1130 + sh[1] * .5, 0.9
    rot = -2.0
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    Wp = lambda p: (pcx + p[0] * sc * ca - p[1] * sc * sa, pcy + p[0] * sc * sa + p[1] * sc * ca)
    flick = 0.9 + 0.1 * math.sin(t * 25)
    o.append(glow(pcx, pcy - 40, 760, 420, "#9cc8ff", 0.35 * flick))
    send = Wp((402, -35))
    # палец висит над кнопкой «отправить»: рукав справа снизу, лёгкая дрожь
    tx, ty = send[0] + 10 + shake_off(t, 8.3, 6.0, 23, 9.0)[0], send[1] - 18 + shake_off(t, 8.3, 6.0, 23, 9.0)[1] * 0.8
    hover = 62 + 10 * math.sin(t * 9)
    tip = (tx - 34, ty - hover)
    base = (tx + 300, ty + 420)
    # кнопка светится, когда вспыхивает облачко
    pop = clamp((t - T_IZV) / 0.2)
    body = phone_l(SENT, press_key=-1, send_glow=0.5 + 0.5 * math.sin(t * 7) * 0.5 + 0.3 * pop, caret=False, ink_red=0.6)
    o.append(G(body, pcx, pcy, sc, rot))
    # облачко над кнопкой
    if t >= T_IZV - 0.02:
        u = t - T_IZV
        k = back_out(clamp(u / 0.35), 2.2)
        cxl, cyl = 600, 520
        cl = cloud_pts(0, 0, 300, 250, 9, 1.0)
        cid_ = clip_of(cl)
        inner = blob(rect_pts(-420, -340, 420, 340), "#fff6e6")
        inner += glow(0, -20, 300, 240, "#ffe9b0", 0.7, "normal")
        inner += f'<g>{bow_dima(t, T_IZV + 0.15)}</g>'
        art = shape(cl, "#fff6e6", f'<g clip-path="url(#{cid_})">' + inner + "</g>", w=7, seed=77)
        # пузыри-хвост к кнопке
        sx, sy = send[0], send[1]
        tail = ""
        sx, sy = send[0], send[1]
        for j, (fr, r_) in enumerate([(0.42, 26), (0.68, 16)]):
            px_ = cxl + 190 + (sx - 20 - cxl - 190) * fr
            py_ = cyl + 215 + (sy - 70 - cyl - 215) * fr
            tail += shape(ellipse_pts((px_ - cxl) / k if k else 0, (py_ - cyl) / k if k else 0, r_, r_, 14), "#fff6e6", "", w=4.6, seed=80 + j)
        o.append(G(art + tail, cxl, cyl, k, -4 * (1 - k)))
        # вспышка и искры
        if u < 0.4:
            fl = (1 - u / 0.4)
            o.append(f'<circle cx="{cxl}" cy="{cyl}" r="{f(300 + 260 * u / 0.4)}" fill="none" stroke="#fff3c4" stroke-width="{f(26 * fl + 2)}" opacity="{fl:.3f}"/>')
            for a in range(10):
                an = a * 36 + 9
                r0, r1 = 330 + 120 * u / .4, 400 + 200 * u / .4
                o.append(line([(cxl + r0 * math.cos(math.radians(an)), cyl + r0 * 0.8 * math.sin(math.radians(an))),
                               (cxl + r1 * math.cos(math.radians(an)), cyl + r1 * 0.8 * math.sin(math.radians(an)))], 14, "#ffd35a", taper=.6, wmin=.1, seed=a, op=fl))
    o.append(thumb(base, tip, w=104, seed=600, sleeve_len=380))
    o.append(f'<rect x="-1500" y="-1500" width="4200" height="5200" fill="{RED}" opacity="{0.10:.3f}" style="mix-blend-mode:multiply"/>')
    return "".join(o), cam(540, 960, z, 0.4 * math.sin(t * 2.7))


# ═══════════════════════════════ вход
def frame(sid, t):
    if not _ST:
        _ST["pp_body"] = phone_p_static()
        _ST["pl"] = phone_l_static()
        _ST["bg"] = room_bg()
        _ST["wall"] = night_wall() + pattern_wall()
        lib.static_done()
    lib.dyn_begin()
    art, cm = {"s01": frame01, "s02": frame02, "s05": frame05, "s06": frame06}[sid](t)
    bg = {"s01": "#201e3a", "s02": "#201e3a", "s05": "#201e3a", "s06": "#201e3a"}[sid]
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cm}">{art}</g>')
