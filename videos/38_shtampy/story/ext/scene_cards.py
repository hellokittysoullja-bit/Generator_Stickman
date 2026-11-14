"""Сцена cards рилса 38 (s10, s11, s12): карточки лояльности автомойки на кремовом фоне (Nunes, Drèze 2006). Без букв
и логотипов; числа «34 %» и «19 %» — кодом (шрифт IDB).
s10 «Карточку на десять штампов, где два уже стояли» (17.45–19.95): карточка влетает снизу с поворотом; на «десять»
     (18.28) по очереди выскакивают 10 пустых кружков в 2 ряда; печать опускается и на «два» (19.36) ставит синюю
     каплю в 1-й кружок, на «уже» (19.52) — во 2-й; карточка подпрыгивает от удара.
s11 «доводили до конца почти вдвое чаще» (19.95–22.55): две карточки рядом — слева 10 кружков (2 со штампами),
     справа 8 пустых (въезжает); на «доводили» (20.51) у левой штампы быстро набегают, на «конца» (21.04) последняя
     клетка — зелёная галочка и блёстки; у правой за это время — только три штампа; на «вдвое» (21.68) под
     карточками растут столбики 34 % и 19 %.
s12 «чем карточку на восемь» (22.55–24.1): правая карточка крупно (3 штампа из 8); на «восемь» (23.44) она
     сникает со вздохом, сползает и падает в мусорную корзину внизу кадра.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import parts34 as P
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, rect_pts, shape,
                 smooth, spring, svg)

_ST = {}
DESYAT = P.wt("десять")            # 18.28
DVA = P.wt("два", 19)              # 19.36
UZHE = P.wt("уже", 19.4)           # 19.52
DOVOD = P.wt("доводили")           # 20.507
KONCA = P.wt("конца", 20.5)        # 21.04
VDVOE = P.wt("вдвое")              # 21.68
VOSEM = P.wt("восемь")             # 23.44

BLUE = "#2f6db5"
BLUE_D = "#1f4f94"
CREAM = "#fbf3df"
BG = "#f3e9d2"
CW, CH = 320, 200                  # полуразмеры карточки


def slots(n):
    m = n // 2
    sp = 560 / m
    r = 46 if n == 10 else 54
    return [(-280 + sp * (i + 0.5), -36 + 128 * row, r) for row in range(2) for i in range(m)]


def drop_pts(r):
    """Капля (синий штамп): острый верх, круглый низ; центр (0, 0)."""
    pts = [(0, -1.25 * r, 1)]
    for a in np.linspace(-0.55, math.pi + 0.55, 11):
        pts.append((r * .78 * math.cos(a), .25 * r + r * .78 * math.sin(a)))
    return pts


def stamp_mark(x, y, r, e, sd):
    """Отпечаток-капля: e — секунды после удара (до удара — ничего)."""
    if e < 0:
        return ""
    k = 1 + 0.35 * math.exp(-e * 14) * (e < 0.3)
    rot = -12 + (sd % 7) * 4
    s = shape(drop_pts(r * .62), BLUE, blob(ellipse_pts(r * .16, r * .32, r * .3, r * .26, 10), BLUE_D, .9) +
              line([(-r * .2, -r * .25), (-r * .3, r * .05)], r * .1, "#8fbaf0", seed=sd + 1), w=3.2, seed=sd, ink_color=BLUE_D)
    spl = ""
    rs = np.random.RandomState(sd)
    for j in range(4):           # брызги краски вокруг
        a = rs.uniform(0, 2 * math.pi)
        d = r * rs.uniform(.75, .95)
        spl += f'<circle cx="{f(d * math.cos(a))}" cy="{f(d * math.sin(a))}" r="{f(r * rs.uniform(.05, .09))}" fill="{BLUE}"/>'
    return f'<g transform="translate({f(x)} {f(y)}) rotate({rot}) scale({f(k)})">{spl}{s}</g>'


def circle_slot(x, y, r, k, sd):
    if k <= 0:
        return ""
    s = shape(ellipse_pts(0, 0, r, r, 22), "#ffffff", blob(ellipse_pts(r * .2, r * .25, r * .8, r * .7, 16), "#efe6d2", .9), w=6.5, seed=sd,
              ink_color=BLUE, var=.15)
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(k)})">{s}</g>'


def card_base(sd):
    """Пустая карточка (без кружков): кремовая, синяя полоса с машинкой и пузырями, нижний кант."""
    inner = blob(rect_pts(-CW, -CH, CW, -CH + 82), BLUE)
    inner += blob(rect_pts(-CW, -CH + 82, CW, -CH + 92), BLUE_D, .9)
    inner += blob(rect_pts(-CW, CH - 26, CW, CH), "#efe2c2")
    inner += blob(rect_pts(CW - 70, -CH + 92, CW, CH), "#f2e7cd", .8)
    # машинка-пиктограмма белым
    c = [(-270, -128, 1), (-272, -142), (-258, -148), (-246, -168), (-206, -170), (-190, -150), (-172, -146), (-170, -128, 1)]
    inner += blob(c, "#ffffff")
    inner += blob([(-238, -162), (-222, -162), (-222, -150), (-246, -150)], BLUE)
    inner += blob([(-216, -162), (-206, -162), (-196, -150), (-216, -150)], BLUE)
    for wx in (-252, -190):
        inner += f'<circle cx="{wx}" cy="-128" r="10" fill="#ffffff" stroke="{BLUE}" stroke-width="4"/>'
    for (bx, by, br) in ((-160, -176, 9), (-146, -160, 6), (-138, -180, 5)):
        inner += f'<circle cx="{bx}" cy="{by}" r="{br}" fill="none" stroke="#ffffff" stroke-width="4"/>'
    # капли справа на полосе
    for k, x in enumerate((180, 222, 264)):
        inner += f'<g transform="translate({x} -158)">' + blob(drop_pts(13), "#ffffff", .95 - k * .15) + "</g>"
    shadow = blob(rect_pts(-CW + 14, -CH + 22, CW + 14, CH + 22, 26), "#b9a37a", .45, blur(8))
    return shadow + shape(rect_pts(-CW, -CH, CW, CH, 26), CREAM, inner, w=6, seed=sd)


def card(n, t, appear, stamps, sd, check=None):
    """Карточка в своих координатах. appear[i] — время появления кружка (None — с начала), stamps[i] — время штампа.
    check — время, когда в последнем кружке вспыхивает галочка."""
    s = [_ST["card"]]
    for i, (x, y, r) in enumerate(slots(n)):
        a = appear[i] if appear else None
        k = 1.0 if a is None else back_out(clamp((t - a) / 0.22), 2.6)
        s.append(circle_slot(x, y, r, k, sd + 10 + i))
        if check is not None and i == n - 1:
            e = t - check
            if e > -0.02:
                kk = back_out(clamp((e + 0.02) / 0.22), 2.6)
                s.append(f'<g transform="translate({f(x)} {f(y)}) scale({f(kk)})">{P.check(0, 4, r / 70, clamp((e + 0.02) / 0.18), sd=sd + 70)}</g>')
            continue
        st = stamps[i] if i < len(stamps) else None
        if st is not None:
            s.append(stamp_mark(x, y, r, t - st, sd + 40 + i))
    return "".join(s)


def card_at(x, y, sc, rot, body):
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{body}</g>'


# ═══════════════════════════════ печать
def stamper(x, y, squash, sd):
    """Печать: деревянная ручка-шар, шейка, колодка, синяя резина. (x, y) — низ резины."""
    s = []
    s.append(shape(rect_pts(-74, -30, 74, 0, 6), BLUE, blob(rect_pts(-74, -12, 74, 0), BLUE_D, .9), w=4.4, seed=sd))
    s.append(shape(rect_pts(-84, -78, 84, -28, 10), "#c98a4a", blob(rect_pts(30, -78, 84, -28), "#a86c34", .9) +
                   line([(-70, -60), (60, -62)], 3, "#e2aa6a", seed=sd + 2, op=.9), w=4.6, seed=sd + 1))
    s.append(shape([(-22, -78), (22, -78), (16, -150), (-16, -150)], "#d79a58", blob([(6, -78), (22, -78), (16, -150), (6, -150)], "#b07438", .9),
                   w=4.2, seed=sd + 3))
    s.append(shape(ellipse_pts(0, -186, 46, 42, 18), "#d79a58", blob(ellipse_pts(14, -176, 32, 30, 14), "#b07438", .85) +
                   blob(ellipse_pts(-16, -200, 12, 9, 10), "#f2c48a", .9), w=4.6, seed=sd + 4))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(1 + .12 * squash)} {f(1 - .12 * squash)})">{"".join(s)}</g>'


def bg_cards():
    s = [f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="{BG}"/>']
    for k in range(-14, 40):
        s.append(f'<rect x="-900" y="{-400 + k * 80}" width="{W + 1800}" height="2" fill="#dccaa4" opacity=".7"/>')
    return "".join(s)


def burst(x, y, e, n, r0, r1, col, w, sd):
    return P.pop_lines(x, y, e, r0, r1, n, col=col, w=w, sd=sd)


# ═══════════════════════════════ s10
CX10, CY10, SC10 = 540, 800, 1.45


def stamp_path(t):
    """Положение низа печати (в системе карточки) и сжатие: висит над 1-м кружком → удар на «два» → 2-й кружок на «уже»."""
    sl = slots(10)
    p1, p2 = sl[0], sl[1]
    hit1, hit2 = DVA, UZHE + 0.03
    hov = -150
    if t < hit1:
        u = ease_out(clamp((t - (hit1 - 0.55)) / 0.4), 2)
        x = p1[0] + 120 * (1 - u)
        y = -900 + (p1[1] - 30 + hov - (-900)) * u
        if t > hit1 - 0.15:                         # замах вниз
            v = ease_in(clamp((t - (hit1 - 0.15)) / 0.15), 3)
            y = p1[1] - 30 + hov + (p1[1] + 40 - (p1[1] - 30 + hov)) * v
        return x, y, 0.0
    if t < hit2 - 0.12:
        e = t - hit1
        sq = math.exp(-e * 18) * (e < 0.2)
        v = ease_out(clamp((e - 0.03) / 0.1), 2)
        x = p1[0] + (p2[0] - p1[0]) * ease_io(clamp((e - 0.04) / 0.12))
        y = p1[1] + 40 - 70 * v
        return x, y, sq
    if t < hit2:
        v = ease_in(clamp((t - (hit2 - 0.12)) / 0.12), 3)
        return p2[0], p2[1] - 30 + 70 * v, 0.0
    e = t - hit2
    sq = math.exp(-e * 18) * (e < 0.2)
    u = ease_in(clamp((e - 0.12) / 0.45), 2)
    return p2[0] + 320 * u, p2[1] + 40 - 1100 * u, sq


def s10(t):
    art = [_ST["bg"]]
    # влёт карточки снизу с поворотом
    e_in = t - 17.25
    u = spring(e_in + 0.02, 2.2, 6.0)
    y = CY10 + 900 * (1 - u)
    rot = -14 * (1 - u) - 2.5 + 1.2 * math.sin(t * 1.7)
    # прыжок от ударов
    j = 34 * P.kick(t, DVA, 7, 18) + 26 * P.kick(t, UZHE + 0.03, 7, 18)
    sq = 0.03 * (P.kick(t, DVA, 9, 22) + P.kick(t, UZHE + 0.03, 9, 22))
    y += -j + 6 * math.sin(t * 2.1)
    appear = [DESYAT + 0.055 * i for i in range(10)]
    body = card(10, t, appear, [DVA, UZHE + 0.03], 6000)
    if t > DVA - 1.0:
        sx, sy, ssq = stamp_path(t)
        stamp_svg = stamper(sx, sy, ssq, 6100)
    else:
        stamp_svg = ""
    cb = f'<g transform="scale({f(1 + sq)} {f(1 - sq)})">{body}{stamp_svg}</g>'
    art.append(card_at(CX10, y, SC10, rot, cb))
    # удары: штрихи вокруг кружка
    for hit, i in ((DVA, 0), (UZHE + 0.03, 1)):
        x0, y0, r = slots(10)[i]
        rr = math.radians(rot)
        wx = CX10 + SC10 * (x0 * math.cos(rr) - y0 * math.sin(rr))
        wy = y + SC10 * (x0 * math.sin(rr) + y0 * math.cos(rr))
        art.append(burst(wx, wy, t - hit, 8, 90, 160, BLUE, 8, 6200 + i * 10))
    uu = clamp((t - 17.25) / 2.9)
    sc = 1.0 + 0.08 * ease_io(uu) + 0.04 * P.kick(t, DVA, 6, 14) + 0.025 * P.kick(t, UZHE + 0.03, 6, 14) + 0.015 * P.kick(t, DESYAT, 6, 14)
    return "".join(art), cam(540, 830 - 20 * uu, sc, 0.6 - 1.0 * uu)


# ═══════════════════════════════ s11
XL, XR, Y11, SC11 = 290, 790, 470, 0.7
BASE11, PER = 1200, 11.0


def bars(t):
    s = []
    s.append(line([(40, BASE11), (1040, BASE11)], 6, INK, taper=.04, wmin=.9, seed=6500))
    for x, val in ((XL, 34), (XR, 19)):          # пунктир будущих столбиков — ждут результата, уходят на «вдвое»
        hh = (34 * PER + 40) * (1 - ease_in(clamp((t - VDVOE) / 0.12), 2))
        if hh < 8:
            continue
        s.append(f'<rect x="{x - 110}" y="{BASE11 - hh}" width="220" height="{hh}" rx="16" fill="none" stroke="#cdb98f" stroke-width="6" '
                 f'stroke-dasharray="22 16"/>')
    for i, (x, val, col) in enumerate(((XL, 34, "#3cbf63"), (XR, 19, "#e2543f"))):
        e = t - (VDVOE + 0.06 * i)
        if e < -0.02:
            continue
        g = back_out(clamp((e + 0.02) / 0.45), 1.6)
        hgt = val * PER * g
        if hgt > 4:
            pts = rect_pts(x - 110, BASE11 - hgt, x + 110, BASE11, min(16, hgt / 2.2))
            inner = blob(rect_pts(x + 50, BASE11 - hgt - 20, x + 112, BASE11), lib.mul(col, (.78, .78, .84)), .9)
            inner += line([(x - 84, BASE11 - hgt + 24), (x - 84, BASE11 - min(hgt, 60) + 30)], 9, "#ffffff", seed=6510 + i, op=.55) if hgt > 70 else ""
            s.append(shape(pts, col, inner, w=6, seed=6520 + i))
        num = int(round(val * clamp(g, 0, 1)))
        k = back_out(clamp((e + 0.02) / 0.25), 2.4)
        ty = BASE11 - hgt - 34
        txt = f"{num} %"
        s.append(f'<g transform="translate({f(x)} {f(ty)}) scale({f(k)})">'
                 f'<text x="8" y="10" text-anchor="middle" font-family="IDB" font-weight="900" font-size="118" fill="#9c7a52" '
                 f'stroke="#9c7a52" stroke-width="12" stroke-linejoin="round">{txt}</text>'
                 f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="118" fill="{col}" '
                 f'stroke="{INK}" stroke-width="11" stroke-linejoin="round" paint-order="stroke">{txt}</text></g>')
        if i == 0:
            s.append(burst(x, ty - 50, e - 0.3, 8, 110, 190, col, 8, 6530))
    return "".join(s)


L_STAMPS = [None, None] + [DOVOD + 0.065 * k for k in range(7)] + [None]
R_STAMPS = [20.78, 21.2, 21.52]


def sparkles(x, y, t, t0, sd, n=6, R=200):
    e = t - t0
    if e < 0:
        return ""
    s = []
    for j in range(n):
        a = -0.9 + 2.2 * j / max(1, n - 1)
        d = R * (0.55 + 0.45 * ease_out(clamp(e / 0.35), 2)) * (1 if j % 2 else .8)
        k = back_out(clamp((e - 0.03 * j) / 0.2), 2.4) * (0.75 + 0.3 * math.sin(t * 13 + j * 1.7))
        if k <= 0:
            continue
        s.append(P.sparkle(x + d * math.cos(a), y + d * math.sin(a), (30 if j % 2 else 22) * k, "#ffd84a", sd=sd + j, rot=20 * j + 60 * e))
    return "".join(s)


def s11(t):
    art = [_ST["bg"]]
    # левая — на месте (последний кадр s10 уменьшен), правая въезжает справа
    jl = 18 * P.kick(t, KONCA, 7, 18)
    left = card(10, t, None, [-9, -9] + L_STAMPS[2:], 6000, check=KONCA)
    art.append(card_at(XL, Y11 - jl + 5 * math.sin(t * 2.0), SC11 * (1 + 0.04 * P.kick(t, KONCA, 8, 20)), -3 + 1.0 * math.sin(t * 1.6), left))
    u = back_out(clamp((t - 19.72) / 0.42), 1.2)
    xr = XR + 700 * (1 - u)
    right = card(8, t, None, R_STAMPS, 6300)
    art.append(card_at(xr, Y11 + 5 * math.sin(t * 2.0 + 1), SC11, 3 + 10 * (1 - u) + 1.0 * math.sin(t * 1.4 + 1), right))
    # блёстки у галочки
    x9, y9, _ = slots(10)[9]
    art.append(sparkles(XL + SC11 * x9 + 40, Y11 + SC11 * y9 + 30, t, KONCA, 6600, 5, 120))
    art.append(burst(XL + SC11 * x9, Y11 + SC11 * y9, t - KONCA, 8, 60, 120, "#3cbf63", 7, 6620))
    art.append(bars(t))
    uu = clamp((t - 19.75) / 3.0)
    back = ease_io(clamp((t - (VDVOE - 0.35)) / 0.7))
    sc = 1.06 - 0.02 * uu - 0.06 * back + 0.04 * P.kick(t, VDVOE, 6, 14) + 0.02 * P.kick(t, KONCA, 6, 14)
    return "".join(art), cam(540, 560 + 20 * uu + 330 * back, sc, -0.5 + 0.9 * uu)


# ═══════════════════════════════ s12
CX12, CY12, SC12 = 540, 540, 1.18
BX, BY = 540, 1150                     # низ корзины
RIM_Y, RIM_RX = 890, 172
BOT_RX = 128


def basket_back():
    s = shape(ellipse_pts(BX, RIM_Y, RIM_RX, 34, 26), "#5a6470", blob(ellipse_pts(BX, RIM_Y + 8, RIM_RX - 14, 24, 22), "#3f4a55"), w=4.6, seed=6800)
    return s


def basket_front(t):
    pts = [(BX - RIM_RX, RIM_Y), (BX + RIM_RX, RIM_Y), (BX + BOT_RX, BY, 1), (BX - BOT_RX, BY, 1)]
    inner = blob([(BX + 60, RIM_Y), (BX + RIM_RX, RIM_Y), (BX + BOT_RX, BY), (BX + 50, BY)], "#7f8a96", .9)
    for k in range(-4, 5):
        x0 = BX + k * 36
        x1 = BX + k * 27
        inner += line([(x0, RIM_Y + 30), (x1, BY - 16)], 4, "#5f6a76", seed=6810 + k, op=.9)
    inner += line([(BX - 160, RIM_Y + 100), (BX + 160, RIM_Y + 100)], 4, "#5f6a76", seed=6830, op=.9)
    s = blob(ellipse_pts(BX + 10, BY + 6, 170, 18, 18), "#b9a37a", .5, blur(6))
    s += shape(pts, "#9aa5b0", inner, w=5, seed=6820)
    s += shape([(BX - RIM_RX - 8, RIM_Y - 6), (BX + RIM_RX + 8, RIM_Y - 6), (BX + RIM_RX + 8, RIM_Y + 14), (BX - RIM_RX - 8, RIM_Y + 14)], "#c9d0d8",
               "", w=4.2, seed=6840)
    return s


def s12(t):
    art = [_ST["bg"]]
    # корзина качается от падения
    land = VOSEM + 0.56
    wob = 5 * P.kick(t, land, 5, 16)
    bk_back = f'<g transform="rotate({f(wob)} {BX} {BY})">{basket_back()}</g>'
    bk_front = f'<g transform="rotate({f(wob)} {BX} {BY})">{basket_front(t)}</g>'
    art.append(bk_back)
    body = card(8, t, None, [-9, -9, -9], 6300)
    # до «восемь»: висит и чуть покачивается; пустые кружки ждут
    sag = smooth(VOSEM - 0.04, VOSEM + 0.22, t)
    sigh = P.bump(t, VOSEM, 0.4)
    fall = clamp((t - (VOSEM + 0.24)) / 0.32)
    gf = fall * fall
    x = CX12 + 30 * gf
    y = CY12 + 8 * math.sin(t * 2.2) * (1 - sag) + 26 * sag + (RIM_Y + 30 - CY12) * gf
    rot = -2 + 1.5 * math.sin(t * 1.5) * (1 - sag) + 7 * sag + 63 * gf
    sc = SC12 * (1 - 0.56 * ease_in(fall, 1.4))
    # сникает: сплющивается к низу и «выдыхает»
    sq = 0.1 * sag - 0.04 * sigh
    cb = f'<g transform="translate(0 {f(CH)}) scale({f(1 + sq * .4)} {f(1 - sq)}) translate(0 {f(-CH)})">{body}</g>'
    card_svg = card_at(x, y, sc, rot, cb)
    if gf > 0.45:
        # карточка в корзине: видна только над краем и внутри проёма (ниже — за передней стенкой)
        cid = lib.clip_of([(-3000, -3000, 1), (3000, -3000, 1), (3000, RIM_Y, 1), (BX + RIM_RX - 6, RIM_Y, 1), (BX + BOT_RX - 6, BY, 1),
                           (BX - BOT_RX + 6, BY, 1), (BX - RIM_RX + 6, RIM_Y, 1), (-3000, RIM_Y, 1)])
        art.append(f'<g transform="rotate({f(wob)} {BX} {BY})"><g clip-path="url(#{cid})">{card_svg}</g></g>')
    else:
        art.append(card_svg)
    art.append(bk_front)
    # вздох: облачко выдоха
    e = t - (VOSEM + 0.02)
    if 0 < e < 0.55:
        k = ease_out(clamp(e / 0.25), 2)
        op_k = 1 - clamp((e - 0.3) / 0.25)
        px, py = CX12 + SC12 * 300 + 60 * k, CY12 - SC12 * 150 - 30 * k
        if op_k > 0.05:
            cl = shape(P.cloud_pts(0, 0, 60, 36, 6, sd=6900), "#ffffff", "", w=4, seed=6901)
            art.append(f'<g transform="translate({f(px)} {f(py)}) scale({f((0.6 + 0.5 * k) * op_k)})">{cl}</g>')
            if op_k > 0.6:
                for j in range(3):
                    art.append(line([(px - 70 + 10 * j, py + 30 + 22 * j), (px - 120 - 10 * k + 10 * j, py + 44 + 22 * j)], 6, INK, seed=6910 + j))
    # капли «грусти» — пот со лба карточки
    if VOSEM - 0.1 < t < VOSEM + 0.3:
        e2 = t - (VOSEM - 0.1)
        dx, dy = CX12 - SC12 * 300, CY12 - SC12 * 190 + 160 * e2
        art.append(f'<g transform="translate({f(dx)} {f(dy)})">' + shape(drop_pts(16), "#8fd0f5", "", w=3, seed=6920) + "</g>")
    # пыль при падении
    e3 = t - land
    if 0 < e3 < 0.5:
        for j in range(6):
            a = math.pi + j * math.pi / 5
            d = 120 + 160 * ease_out(e3 / 0.5, 2)
            r = 26 * (1 - e3 / 0.5)
            art.append(blob(ellipse_pts(BX + d * math.cos(a) * 1.2, RIM_Y - 10 + d * math.sin(a) * .35, r, r * .8, 10), "#e2d6bc"))
        art.append(burst(BX, RIM_Y - 40, e3, 7, 160, 240, INK, 7, 6930))
    uu = clamp((t - 22.35) / 1.95)
    scc = 1.0 + 0.06 * ease_io(uu) + 0.04 * P.kick(t, VOSEM, 6, 14) + 0.03 * P.kick(t, land, 6, 16)
    return "".join(art), cam(540, 820 + 20 * uu, scc, 0.5 - 0.8 * uu)


def build_static():
    if _ST:
        return
    _ST["bg"] = bg_cards()
    _ST["card"] = card_base(5900)
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s10": s10, "s11": s11, "s12": s12}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="{BG}"/><g transform="{cm}">{art}</g>')
