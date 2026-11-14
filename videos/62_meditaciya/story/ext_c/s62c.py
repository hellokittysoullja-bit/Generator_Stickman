"""Рилс 62 «медитация», группа C: облака-мысли над головой Димы.
s04 (4.35–5.85): голова и плечи Димы снизу, глаза закрыты; «подумал» — из макушки пружиной облако (три кружка-ступеньки),
                 «обед» — с хлопком тарелка супа с паром и котлета на вилке; Дима причмокивает, слюнка блестит. Бумага.
s05 (5.85–7.95): голубоватое «небо»; «вспомнил» — второе облако выскакивает и отпихивает первое (то сплющивается), в нём друг
                 с мобильником-силуэтом, «не ответил» — топает и трясёт мобильником, бровь обиженно вверх; брови Димы дёргаются.
s07 (9.3–10.95): тревожный тёплый фон; «выключил» — третье, самое большое облако выбивает остальные к краям кадра (сплющены),
                 в нём утюг на гладильной доске, «утюг» — подпрыгивает, дымок сплошными завитками и язычок пара.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Букв и цифр нет; без полупрозрачных фигур (дым — сплошные завитки)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
from lib import (INK, back_out, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rrect, shape,  # noqa: E402,F401
                 smooth, spring)

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


T_POD4, T_OBED = wt(10), wt(12)            # 4.373, 5.013
T_VSP, T_OTV = wt(14), wt(17)              # 6.147, 7.093
T_VYK, T_UTUG = wt(21), wt(24)             # 9.333, 10.16


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def decay(t, t0, k=9.0, fr=22.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def G(inner, x, y, s=1.0, rot=0.0, sx=None, sy=None):
    sx = s if sx is None else sx * s
    sy = s if sy is None else sy * s
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sx:.4f} {sy:.4f})">{inner}</g>'


# ---------------------------------------------------------------- пружинный выскок
def pop(t, t0, freq=2.4, damp=6.5, sq=.32):
    """Пружинный выскок общего модуля (props.pop): сжатие по вертикали → вытяжка → отскок с затуханием."""
    return PR.pop(t, t0, amp=sq, freq=freq, damp=damp)


def squeeze(t, t0, amt, k=6.0, fr=3.4):
    """Сплющивание от тесноты: к t0 + .1 c сжато на amt, дальше держится с затухающей дрожью."""
    if t < t0:
        return 0.0
    u = t - t0
    base = ease_out(clamp(u / .12), 2)
    return amt * base * (1 + .35 * math.exp(-k * u) * math.cos(2 * math.pi * fr * u))


# ---------------------------------------------------------------- облако
def cloud_pts(rx, ry, n, seed, wob=0.0, t=0.0, bump=.17):
    rs = np.random.RandomState(seed)
    out = []
    ph = rs.uniform(0, 6.28, n)
    amp = rs.uniform(.75, 1.25, n)
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        for k in range(7):
            u = k / 6
            a = a0 + (a1 - a0) * u
            r = 1 + bump * amp[i] * math.sin(math.pi * u) + wob * math.sin(t * 5 + ph[i])
            p = (math.cos(a) * rx * r, math.sin(a) * ry * r)
            if k == 0:
                out.append(p + (1,))
            elif k < 6:
                out.append(p)
    return out


def cloud(x, y, rx, ry, sx, sy, seed, inner="", col="#fffdf7", shade="#e9edf5", t=0.0, rot=0.0, n=10, w=8.0):
    """Облако-мысль с центром (x, y); sx, sy — сжатие/вытяжка; inner — рисунок внутри (в координатах облака)."""
    if sx <= .01 or sy <= .01:
        return ""
    pts = cloud_pts(rx, ry, n, seed, .012, t)
    sh = blob(cloud_pts(rx * .8, ry * .36, max(6, n - 2), seed + 3), shade)
    sh = f'<g transform="translate({f(rx * .1)} {f(ry * .55)})">{sh}</g>'
    hi = blob(ellipse_pts(-rx * .5, -ry * .55, rx * .2, ry * .09, 10, rot=-12), "#ffffff")
    body = shape(pts, col, sh + hi, w=w, seed=seed)
    return G(body + inner, x, y, 1.0, rot, sx, sy)


def bubbles(p0, p1, t, t0, col="#fffdf7", r=(18, 28, 40), seed=0, step=.06):
    """Три кружка-ступеньки от головы (p0) к облаку (p1): выскакивают по очереди, от маленького к большому."""
    o = []
    for k in range(3):
        u = (k + 1) / 4.0
        x = p0[0] + (p1[0] - p0[0]) * u
        y = p0[1] + (p1[1] - p0[1]) * u
        sx, sy = pop(t, t0 + step * k, 3.0, 8.0, .3)
        if sx <= 0:
            continue
        rr = r[k]
        o.append(G(shape(ellipse_pts(0, 0, rr, rr, 12), col, blob(ellipse_pts(rr * .2, rr * .3, rr * .6, rr * .4, 10), "#e9edf5"),
                         w=5.5, seed=seed + k), x, y + 3 * osc(t, 1.3, k), 1.0, 0, sx, sy))
    return "".join(o)


def burst(x, y, t, t0, r0=150, r1=260, n=12, col="#ffb23c", seed=0, dur=.32):
    """Хлопок: сплошные штрихи разлетаются от центра и укорачиваются (без прозрачности)."""
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return ""
    o = []
    rs = np.random.RandomState(seed)
    for i in range(n):
        a = i / n * 2 * math.pi + rs.uniform(-.12, .12)
        ra = r0 + (r1 - r0) * ease_out(u)
        L = (r1 - r0) * .55 * (1 - u) * rs.uniform(.7, 1.1)
        p0 = (x + math.cos(a) * ra, y + math.sin(a) * ra)
        p1 = (x + math.cos(a) * (ra + L), y + math.sin(a) * (ra + L))
        pm = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        o.append(line([p0, pm, p1], 20 * (1 - u * .5), INK, taper=.6, wmin=.3, peak=.45, seed=seed + i))
        o.append(line([p0, pm, p1], 12 * (1 - u * .5), col, taper=.6, wmin=.3, peak=.45, seed=seed + 40 + i))
    return "".join(o)


def star4(x, y, r, col, rot=0.0, w=4.5, seed=0):
    pts = []
    for i in range(8):
        a = math.radians(rot) + i * math.pi / 4
        rr = r if i % 2 == 0 else r * .28
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, col, w=w, seed=seed)


def wisp(pts, w, col, seed, ink_w=6.0):
    """Сплошной завиток (пар/дым): тушь под цветом."""
    return line(pts, w + ink_w, INK, taper=.75, wmin=.2, peak=.4, seed=seed) + line(pts, w, col, taper=.75, wmin=.2, peak=.4, seed=seed + 1)


def curl_path(x, y, h, t, ph, amp=22.0, turns=1.2):
    pts = []
    for i in range(18):
        u = i / 17
        pts.append((x + amp * math.sin(u * turns * 2 * math.pi + t * 4.5 + ph) * (.5 + .5 * u), y - h * u))
    return pts


# ---------------------------------------------------------------- обед в облаке (props.plate_soup, props.cutlet_fork)
def lunch(t, steam=1.0, sx=1.0, sy=1.0, wob=0.0):
    """Суп слева и котлета на вилке справа, в координатах облака (центр 0, 0)."""
    return G(PR.plate_soup(-95, 95, 1.45, steam, t, seed=1) + PR.cutlet_fork(175, -40 + 6 * wob, 1.1, 22 + 4 * wob, seed=2), 0, 0, 1.0, 0, sx, sy)


# ---------------------------------------------------------------- мобильник-силуэт и друг
def friend_fig(t, x, y, sc, stomp_t, seed=0):
    """Друг во весь рост (лицом вправо, к Диме — нет, лицом к зрителю 3/4), ближняя рука держит мобильник у груди.
    stomp_t — время топа ногой."""
    who = "friend"
    s = sc * people.HEIGHT.get(who, 1.0)
    # топ: колено поднимается за .18 с до удара, потом ступня бьёт об пол
    up = smooth(stomp_t - .22, stomp_t - .06, t) * (1 - smooth(stomp_t - .03, stomp_t, t))
    land = decay(t, stomp_t, 10, 5)
    body_dy = -14 * up * s / .3 + 10 * abs(land) * s / .3
    hip = (x, y + body_dy)
    leg_y = y + 600 * s
    feet = {"f": ((x - 70 * s, leg_y), 0.0),
            "n": ((x + 90 * s, leg_y - 150 * s * up), -0.35 * up)}
    # мобильник: у груди, трясётся после «не ответил»
    shk = decay(t, stomp_t - .02, 5.5, 7) * 1.0
    mob = np.array([x + 210 * s + 40 * s * shk, y - 330 * s - 30 * s * abs(shk)])
    mob_rot = 22 * shk
    wr = mob + np.array([60 * s, 34 * s])
    arms = {"f": ("ik", (x - 150 * s, y - 40 * s), 1), "n": ("ik", tuple(wr), -1)}
    hands = {"n": {"kind": "none"}, "f": {"curl": (.5, .5, .55, .6), "thumb": .4, "dir": (-.2, 1)}}
    brow = "skeptic" if t > stomp_t - .1 else "calm"
    expr = {"brows": brow, "mouth": "flat", "open": .2, "lid": .7 if t > stomp_t - .1 else .85, "look": (.35, -.1)}
    fig = people.figure(who, hip[0], hip[1], sc, expr, lean=-.04 - .05 * up, head_ang=.08 * shk, arms=arms, hands=hands, feet=feet)
    o = [fig["svg"]]
    # мобильник в кулаке: ладонь за корпусом, пальцы обхватывают спереди
    k = s / .3 * .62
    gb, gf = people.grip_svg(who, (0, 0), 36, +1, k=k, h=78, seed=seed + 40)
    o.append(G(gb + mobilnik(seed + 50) + gf, mob[0], mob[1], 1.0, mob_rot))
    # пыль от топа
    if t > stomp_t:
        u = clamp((t - stomp_t) / .35)
        fx, fy = feet["n"][0][0], leg_y + 40 * s
        for j in (-1, 1):
            for m in range(2):
                a0 = (fx + j * (60 + 70 * u + 30 * m) * s / .3 * .3, fy - 8 * m)
                a1 = (a0[0] + j * 60 * (1 - u) * s / .3 * .3, a0[1] - 18 - 10 * m)
                if u < 1:
                    o.append(line([a0, a1], 9 * (1 - u) + 2, INK, taper=.5, wmin=.3, seed=seed + 60 + m + 3 * j))
    return "".join(o)


def smoke_puff(x, y, r, seed, col="#8f939b"):
    pts = cloud_pts(r, r * .82, 6, seed, 0, 0, .22)
    return G(shape(pts, col, blob(ellipse_pts(r * .2, r * .25, r * .6, r * .4, 10), mix(col, INK, .25)), w=5, seed=seed), x, y)


# ---------------------------------------------------------------- Дима снизу кадра
def dima_bust(x, hy, sc, expr, t, lean=0.0, ha=0.0):
    """Дима по пояс, голова в (≈x, hy). Возвращает (svg, функция «точка головы → мир»)."""
    s = sc * people.HEIGHT.get("dima", 1.0)
    hip_y = hy + 548 * s
    fig = people.figure("dima", x - 54 * s, hip_y, sc, expr, lean=lean, head_ang=ha,
                        arms={"f": ("ang", 0.1, 0.1), "n": ("ang", -0.05, 0.1)}, layers=("body",))
    hx, hy2 = fig["head"]
    ang = lean * .5 + ha

    def P(p):
        c, si = math.cos(ang), math.sin(ang)
        return (hx + fig["scale"] * (c * p[0] - si * p[1]), hy2 + fig["scale"] * (si * p[0] + c * p[1]))
    return fig["svg"], P


def paper_bg(o, seed=3, base="#f4ecd9", hi="#fbf6ea", lo="#e7dbc0"):
    o.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="{base}"/>')
    g = lib.rad_grad([(0, hi, 1), (.7, base, 1), (1, lo, 1)], 540, 800, 900, 1150)
    o.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g})"/>')
    rs = np.random.RandomState(seed)
    for k in range(80):
        x, y = rs.uniform(-300, 1380), rs.uniform(-250, 2150)
        a = rs.uniform(0, 3.14)
        L = rs.uniform(10, 26)
        o.append(line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], 2.6, lo if k % 2 else "#fffaf0", taper=.5, wmin=.3, seed=k))


# ================================================================ s04: облако с обедом
def frame04(t):
    o = []
    paper_bg(o, 3)
    # каракули на полях: спираль и волна (без букв)
    sp = [(110 + math.cos(a) * a * 4.5, 300 + math.sin(a) * a * 4.5) for a in np.linspace(0, 13, 56)]
    o.append(line(sp, 5, "#c9b896", taper=.4, wmin=.3, seed=91))
    o.append(line([(840 + 24 * k, 1180 + (12 if k % 2 else -12)) for k in range(8)], 5, "#c9b896", taper=.4, wmin=.3, seed=92))

    # Дима: блаженно покачивается, на «обед» причмокивает
    smack = smooth(T_OBED + .05, T_OBED + .2, t) * (1 - smooth(5.85, 6.0, t))
    chew = abs(math.sin((t - T_OBED) * 2 * math.pi * 2.6)) if smack > 0 else 0.0
    sway = 2.2 * osc(t, .45)
    expr = {"laugh": .85, "lid": .5, "brows": ("calm", "up", smooth(T_OBED, T_OBED + .15, t) * .55),
            "mouth": "talk" if smack > .2 else "smile", "open": .05 + .32 * chew * smack, "smile": .55 + .3 * smack, "hair": 3 * decay(t, T_POD4, 6, 4)}
    hx, hy = 560, 1160 - 10 * osc(t, .5) - 18 * abs(decay(t, T_POD4, 7, 3))
    dsvg, P = dima_bust(hx, hy, 1.9, expr, t, ha=math.radians(sway) * .02 * 0 + .02 * osc(t, .45))
    o.append(dsvg)
    # слюнка: капля у уголка рта, блестит
    if smack > .3:
        dl = smooth(T_OBED + .25, T_OBED + .5, t)
        p = P((36, 98 + 14 * dl))
        r = 7 + 3 * dl
        drop = [(p[0], p[1] - r * 1.8), (p[0] + r, p[1]), (p[0], p[1] + r), (p[0] - r, p[1])]
        o.append(shape(drop, "#bfe6fa", blob(ellipse_pts(p[0] - 2, p[1] - 2, 2.6, 3.6, 6), "#ffffff"), w=3.4, seed=77))
        if osc(t, 2.2) > .3:
            o.append(star4(p[0] + 16, p[1] - 14, 9, "#ffffff", rot=t * 120, w=3, seed=78))
    # макушка
    top = P((-10, -170))
    # облако: выскакивает из макушки
    C4 = (600.0, 395.0)
    sx, sy = pop(t, T_POD4 + .14, 2.4, 6.0, .3)
    o.append(bubbles((top[0] + 20, top[1] - 10), (C4[0] - 90, C4[1] + 250), t, T_POD4 - .03, seed=120))
    # содержимое: с хлопком на «обед»
    csx, csy = pop(t, T_OBED, 3.0, 7.0, .32)
    inner = ""
    if csx > 0:
        inner = lunch(t, clamp((t - T_OBED - .05) / .3), csx, csy, osc(t, 1.1))
    puff = 1 + .07 * decay(t, T_OBED, 7, 4)
    o.append(cloud(C4[0], C4[1] + 6 * osc(t, .7), 345, 255, sx * puff, sy * puff, 41, inner, t=t, rot=-2 + 1.5 * osc(t, .4)))
    o.append(burst(C4[0], C4[1], t, T_OBED, 300, 430, 14, "#ffb23c", seed=200))
    if t > T_OBED:
        for k in range(4):
            a = k / 4 * 2 * math.pi + .6
            tw = .5 + .5 * math.sin((t - T_OBED) * 9 + k)
            o.append(star4(C4[0] + math.cos(a) * 380, C4[1] + math.sin(a) * 280, 12 + 12 * tw * clamp((t - T_OBED) / .2), "#ffd23c",
                           rot=t * 60, seed=210 + k))
    # камера: наезд к облаку, тряска на хлопке
    z = 1.0 + .16 * ease_io(clamp((t - 4.15) / 1.9)) + .05 * math.exp(-7 * max(0.0, t - T_OBED)) * (t >= T_OBED)
    set_ink(z)
    shk = 12 * decay(t, T_OBED, 8, 16) + 5 * decay(t, T_POD4 + .14, 9, 14)
    cam = lib.cam(560 + shk, 900 - 120 * ease_io(clamp((t - 4.15) / 1.9)) + shk * .6, z, -1.0 + 2.0 * ease_io(clamp((t - 4.15) / 1.9)))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ================================================================ s05: облако с другом отпихивает обед
def frame05(t):
    o = []
    o.append('<rect x="-900" y="-900" width="2900" height="3800" fill="#d6e5f2"/>')
    g = lib.lin_grad([(0, "#bcd6ee", 1), (.6, "#d9e8f4", 1), (1, "#eef3f6", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g})"/>')
    rs = np.random.RandomState(11)
    for k in range(9):          # мелкие белые облачка-штрихи на «небе»
        x, y = rs.uniform(-200, 1300), rs.uniform(-100, 1300)
        o.append(blob(cloud_pts(rs.uniform(40, 80), rs.uniform(16, 26), 6, 60 + k), "#e9f1f8") .replace("<path", f'<path transform="translate({f(x + 14 * (t - 5.6))} {f(y)})"', 1))

    # Дима снизу слева: на «вспомнил» и «не ответил» брови дёргаются
    tw = max(0.0, decay(t, T_VSP, 7, 5)) + max(0.0, decay(t, T_OTV, 7, 5))
    br_u = clamp(.35 + .9 * tw + .3 * smooth(T_VSP, T_VSP + .2, t))
    expr = {"closed": 0.0, "lid": -1.05, "brows": ("calm", "worry", br_u), "mouth": "flat", "hair": 4 * decay(t, T_VSP, 6, 4)}
    hx, hy = 300, 1310 + 8 * osc(t, .5)
    dsvg, P = dima_bust(hx, hy, 1.32, expr, t, ha=-.04 + .03 * decay(t, T_OTV, 6, 3))
    top = P((-10, -170))

    # облако обеда: было в центре, на «вспомнил» его отпихивают влево и сплющивают
    push = spring(max(0.0, t - (T_VSP + .06)), 2.2, 6.0) if t > T_VSP + .06 else 0.0
    sqz = squeeze(t, T_VSP + .06, .36)
    LX = 470 - 300 * push
    LY = 560 - 40 * push
    l_in = lunch(t, 1.0, wob=osc(t, .9))
    lunch = cloud(LX, LY + 5 * osc(t, .7), 345, 255, (1 - sqz) * 1.0, (1 + sqz * .45), 41, l_in, t=t, rot=-2 - 6 * push)
    # облако друга
    C5 = (760.0, 640.0)
    sx, sy = pop(t, T_VSP, 2.4, 6.0, .3)
    f_in = ""
    if sx > 0:
        f_in = friend_fig(t, -10, -60, .27, T_OTV, seed=300)
    fr = cloud(C5[0], C5[1] + 5 * osc(t, .6, 1), 330, 330, sx, sy * (1 + .04 * max(0.0, decay(t, T_OTV, 8, 6))), 57, f_in, t=t, rot=2,
               col="#fffef9", n=11)
    o.append(lunch)
    o.append(bubbles((top[0] + 40, top[1] - 30), (C5[0] - 210, C5[1] + 300), t, T_VSP - .1, seed=320))
    o.append(fr)
    # удар при толчке: штрихи между облаками
    o.append(burst((LX + C5[0]) / 2 + 120, 600, t, T_VSP + .08, 30, 120, 7, "#ffffff", seed=330, dur=.25))
    o.append(dsvg)
    # камера: вправо и вверх, лёгкий отъезд
    u = ease_io(clamp((t - 5.65) / 2.5))
    z = 1.08 - .08 * u
    set_ink(z)
    shk = 7 * decay(t, T_VSP + .06, 8, 15) + 6 * decay(t, T_OTV, 8, 16)
    cam = lib.cam(500 + 110 * u + shk, 930 - 130 * u + shk * .4, z, 1.0 - 1.6 * u)
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ================================================================ s07: облако-утюг выбивает остальные к краям
def frame07(t):
    o = []
    o.append('<rect x="-900" y="-900" width="2900" height="3800" fill="#f3a066"/>')
    g = lib.rad_grad([(0, "#ffe0b0", 1), (.55, "#fbb57a", 1), (1, "#e2774c", 1)], 540, 760, 900, 1250)
    o.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g})"/>')
    # тревожные кольца-штрихи, расходятся от облака
    for k in range(4):
        ph = ((t - 9.1) * .9 + k / 4) % 1
        r = 380 + 520 * ph
        pts = [(540 + math.cos(a) * r, 760 + math.sin(a) * r * .9) for a in np.linspace(0, 2 * math.pi, 60)]
        o.append(line(pts, 10 * (1 - ph) + 2, "#e58a52", taper=0, wmin=1, seed=500 + k))

    up = smooth(T_UTUG - .02, T_UTUG + .1, t)
    # Дима снизу по центру: напряжённо зажмурен, капля пота
    expr = {"closed": 0.0, "lid": -1.05, "brows": "worry", "mouth": "flat", "hair": 4 * decay(t, T_VYK, 6, 4) + 3 * decay(t, T_UTUG, 6, 4)}
    hx, hy = 520, 1420 + 6 * osc(t, .7)
    dsvg, P = dima_bust(hx, hy, 1.3, expr, t, ha=.03 * osc(t, 3.2) * smooth(T_VYK, T_VYK + .3, t))
    top = P((-10, -170))

    # старые облака: сначала тесно над головой, на «выключил» вылетают к краям и сплющиваются о края кадра
    hit = T_VYK + .1
    kick = spring(max(0.0, t - hit), 2.0, 6.5) if t > hit else 0.0
    sq = squeeze(t, hit + .08, .42)
    l_in = lunch(t, 1.0, wob=osc(t, 1.3))
    lunch = cloud(330 - 250 * kick, 600 + 120 * kick, 300, 222, (1 - sq) * .95, (1 + sq * .5) * .95, 41, l_in, t=t, rot=-4 - 14 * kick)
    f_in = friend_fig(t, -10, -60, .27, 7.093, seed=300)
    friend = cloud(760 + 250 * kick, 520 + 60 * kick, 300, 300, (1 - sq) * .92, (1 + sq * .5) * .92, 57, f_in, t=t, rot=3 + 12 * kick,
                   col="#fffef9", n=11)
    o.append(lunch)
    o.append(friend)
    # большое облако с утюгом
    C7 = (540.0, 760.0)
    sx, sy = pop(t, T_VYK, 2.2, 5.5, .34)
    jump = 0.0
    land = 0.0
    ju = (t - T_UTUG) / .34
    if 0 <= ju < 1:
        jump = 4 * ju * (1 - ju)
    elif ju >= 1:
        land = math.exp(-8 * (t - T_UTUG - .34)) * math.cos(2 * math.pi * 3.5 * (t - T_UTUG - .34))
    pre = smooth(T_UTUG - .2, T_UTUG - .02, t) * (1 - up)
    isx, isy = 1 + .1 * pre + .12 * land, 1 - .12 * pre + .14 * jump - .14 * land
    hot = smooth(9.7, T_UTUG, t)
    inner = [ironing_board(seed=600)]
    # дым: сплошные клубы и завитки из-под утюга, после прыжка гуще
    sm = []
    nP = 3 + int(5 * up)
    for k in range(nP):
        life = ((t - 9.4) * (.9 + .5 * up) + k / nP) % 1
        if t < 9.6 + .1 * k and up <= 0:
            continue
        r = (16 + 30 * life) * (1 - smooth(.8, 1.0, life)) * (.6 + .4 * hot)
        if r < 3:
            continue
        px = -40 + 40 * math.sin(k * 2.1) + 26 * math.sin(life * 6 + k)
        py = -10 - 360 * life
        sm.append(smoke_puff(px, py, r, 650 + k, col=mix("#a8acb3", "#7d828a", life)))
    for k in range(2 + int(up)):
        h = 160 + 120 * up
        sm.append(wisp(curl_path(-60 + 70 * k, -20, h, t, k * 2.3, 26, 1.4), 12 + 6 * up, "#9ea3ab", 680 + 5 * k))
    iy = -110 * jump
    irot = -14 * jump + 5 * land
    iron_svg = G(iron(t, glow=hot, seed=620), 0, iy, 1.0, irot, isx, isy)
    steam = ""
    if t > T_UTUG + .05:      # язычок пара из носика
        u = clamp((t - T_UTUG - .05) / .25)
        L = 90 * back_out(u, 2) * (1 + .15 * osc(t, 6))
        steam = wisp([(150, iy - 30), (150 + L * .5, iy - 40 - 14 * osc(t, 5)), (150 + L, iy - 30)], 16, "#ffffff", 700, 6)
    inner.append(G("".join(sm), 20, 0) + G(iron_svg + steam, 20, -6))
    # искры тревоги вокруг утюга после прыжка
    if t > T_UTUG:
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * .55
            uu = clamp((t - T_UTUG) / .25)
            inner.append(line([(math.cos(a) * 190, -80 + math.sin(a) * 170), (math.cos(a) * (190 + 70 * uu), -80 + math.sin(a) * (170 + 70 * uu))],
                              12, INK, taper=.5, wmin=.4, seed=720 + k))
    inner_svg = G("".join(inner), 0, 40, .78)
    o.append(bubbles((top[0] + 20, top[1] - 30), (C7[0] - 40, C7[1] + 380), t, T_VYK - .08, r=(22, 34, 48), seed=740))
    o.append(cloud(C7[0], C7[1] + 6 * osc(t, .8), 430, 360, sx, sy * (1 + .03 * decay(t, T_UTUG, 8, 6)), 77, inner_svg, t=t, rot=-1.5,
                   col="#fffdf6", n=12, w=9))
    o.append(burst(C7[0], C7[1], t, T_VYK + .08, 420, 560, 16, "#ffffff", seed=760, dur=.3))
    o.append(dsvg)
    # капля пота у виска
    if t > T_VYK + .2:
        u = ((t - T_VYK - .2) / .9) % 1
        p = P((-70, -60 + 60 * u))
        drop = [(p[0], p[1] - 22), (p[0] + 11, p[1]), (p[0], p[1] + 11), (p[0] - 11, p[1])]
        o.append(shape(drop, "#bfe6fa", blob(ellipse_pts(p[0] - 3, p[1] - 3, 3, 4, 6), "#ffffff"), w=3.4, seed=780))
    # камера: наезд на утюг, тряска на прыжке
    u = ease_in(clamp((t - 9.1) / 2.0), 1.6)
    z = 1.0 + .2 * u + .06 * math.exp(-7 * max(0.0, t - T_UTUG)) * (t >= T_UTUG)
    set_ink(z)
    shk = 14 * decay(t, T_UTUG + .3, 8, 15) + 9 * decay(t, T_VYK + .1, 8, 16)
    cam = lib.cam(540 + shk, 900 - 130 * u + shk * .5, z, 1.5 - 2.5 * u + 1.5 * decay(t, T_UTUG + .3, 7, 6))
    return f'<g transform="{cam}">{"".join(o)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    fn = {"s04": frame04, "s05": frame05, "s07": frame07}[sid]
    return lib.svg(fn(t))
