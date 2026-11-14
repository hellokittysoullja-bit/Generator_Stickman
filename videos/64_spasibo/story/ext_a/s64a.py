"""Рилс 64 «спасибо», группа A: графика на бумаге.
s05 (10.40–13.17): открытка с сердечком летит через лист к серой тучке над домиком; «меняет» (11.04) туча лопается штрихами,
    выкатывается солнце, лучи пером; «настроение» (11.55) домик и деревья заливаются тёплым; «надолго» (12.14) над домиком дважды
    проходят день и ночь по дуге, солнце снова на месте. Камера: наезд с разгоном к открытке до пика riser (10.40), потом откат.
s06 (13.17–15.96): Дима (people.py) сидит по-турецки, подперев щёку; «помним» (14.14) всплывают пузыри-воспоминания без надписей
    (учительница с листом, друг подаёт руку, мама с пирогом, кот на подоконнике) с отскоком, «хорошее» (14.56) загораются тёплым;
    «но редко» (15.41–15.60) бледнеют и тянутся ниточками к голове. Дрейф вверх, лёгкий откат.
s12 (29.20–31.68): календарь-сетка без цифр; «ещё» (29.20) по клеткам бегут солнышки-штампы, «целый» (29.50) быстрее, «месяц»
    (29.84) вся сетка в солнышках, лист светится и подрагивает; «Поэтому» (30.48) лист переворачивается вверх (к хлёсту на s13).
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Предметы — common/props.py, люди и кот — common/people.py, cat.py."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import props as P  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, svg  # noqa: E402

INK = lib.INK


def lerp(a, b, u):
    return a + (b - a) * u


def frame_svg(body, cx, cy, s, rot, bg):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>')


def paper_bg(col=None, grid="#D7DFE6"):
    o = [blob(rect_pts(-900, -900, 2000, 2800), col or P.C_PAGE)]
    for i in range(-14, 44):
        o.append(line([(-900, i * 64), (2000, i * 64)], 2.0, grid, taper=0, wmin=1, seed=300 + i))
    for i in range(-14, 32):
        o.append(line([(i * 64, -900), (i * 64, 2800)], 2.0, grid, taper=0, wmin=1, seed=360 + i))
    return "".join(o)


def bezier(p0, p1, p2, u):
    a = (1 - u) ** 2
    b = 2 * u * (1 - u)
    c = u * u
    return (a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1])


# ═══════════════════════════════ s05: открытка, туча → солнце ═══════════════════════════════
S05_HOUSE = (540, 1170)
S05_CLOUD = (540, 760)          # центр дна тучки
S05_SUN = (540, 610)            # где солнце стоит (верх дуги)
T_LAUNCH, T_TOUCH, T_WARM, T_LONG = 10.40, 11.02, 11.55, 12.14
T_LONG_END = 13.02
CARD0 = (230, 1440)
CARD_CTRL = (120, 700)
CARD_HIT = (470, 700)


def s05(t):
    o = [paper_bg()]
    # день и ночь: фаза дуги, ночь темнит бумагу (сплошной цвет фона, не фигура)
    night = 0.0
    if T_LONG <= t < T_LONG_END:
        ph = .5 + 4.0 * ease_io((t - T_LONG) / (T_LONG_END - T_LONG))
        q = ph % 2.0
        night = clamp(min(q - 1, 2 - q) * 5) if q > 1 else 0.0
    if night > 0:
        o = [paper_bg(mix(P.C_PAGE, "#2C3463", night), mix("#D7DFE6", "#3B4577", night))]
    warm = ease_io((t - T_WARM) / .45)
    # земля
    gx0, gx1, gy = -200, 1280, S05_HOUSE[1]
    o.append(blob(rect_pts(gx0, gy - 6, gx1, gy + 110), mix(mix("#BFC1C4", "#9BC48A", warm), "#3E4A6E", night * .6)))
    o.append(line([(gx0, gy), (300, gy + 4), (760, gy - 3), (gx1, gy + 2)], 6, INK, taper=.05, wmin=.8, seed=5101))
    for j, gxx in enumerate((150, 320, 760, 940)):   # травинки
        o.append(line([(gxx, gy + 2), (gxx + 6, gy - 22)], 4, mix("#8E9196", "#4F8A5E", warm), taper=.6, wmin=.3, seed=5110 + j))
    # деревья и домик
    o.append(P.tree(830, gy, 1.55, warm, t, seed=1))
    o.append(P.tree(230, gy, 1.2, warm, t + .7, seed=2))
    o.append(P.house(S05_HOUSE[0], gy, 1.75, warm, seed=3))
    # тучка до касания, потом лопается
    if t < T_TOUCH:
        jig = 3 * math.sin(t * 13) * clamp((t - 10.75) / .25)
        o.append(P.gloom(S05_CLOUD[0] + jig, S05_CLOUD[1], 2.0, t, 1.0, seed=4))
    else:
        o.append(P.gloom_burst(S05_CLOUD[0], S05_CLOUD[1] + 30, 2.0, (t - T_TOUCH) / .5, seed=4))
    # солнце: выкатывается из тучи (выскок), поднимается, лучи пером
    if t >= T_TOUCH:
        u = t - T_TOUCH
        sx_, sy_ = P.pop(t, T_TOUCH, amp=.25)
        k = min(sx_, sy_) if u < .9 else 1.0
        rise = ease_out(u / .45)
        x, y = S05_SUN[0], lerp(S05_CLOUD[1] - 60, S05_SUN[1], rise)
        rays = clamp((u - .12) / .4)
        if T_LONG <= t < T_LONG_END:
            ph = .5 + 4.0 * ease_io((t - T_LONG) / (T_LONG_END - T_LONG))
            svg_arc, _ = P.day_arc(540, 1080, 440, ph, seed=5)
            if (ph % 2.0) < 1.0:   # солнце на дуге — с лучами, чуть крупнее
                q = ph % 1.0
                a = math.pi * (1 - q)
                o.append(P.sun(540 + 440 * math.cos(a), 1080 - 352 * math.sin(a), 70, 1.0, t, seed=5))
            else:
                o.append(svg_arc)
        else:
            o.append(P.sun(x, y, 80 * k, rays, t, seed=5))
        if T_LONG - .05 < t < T_LONG + .2 or t > T_LONG_END:
            o.append(P.sparkles(S05_SUN[0], S05_SUN[1], 1.3, clamp((t - T_LONG_END) / .2) if t > T_LONG_END else .7, t, seed=6, n=5, r=150))
    # открытка
    if t < T_LAUNCH:
        cx, cy, rot, ck = CARD0[0], CARD0[1] + 4 * math.sin(t * 20), -8 + 3 * math.sin(t * 9), 1.25
    elif t < T_TOUCH:
        u = ease_in((t - T_LAUNCH) / (T_TOUCH - T_LAUNCH), 1.6)
        cx, cy = bezier(CARD0, CARD_CTRL, CARD_HIT, u)
        rot = -8 + 380 * u
        ck = lerp(1.25, .85, u)
    else:   # отскок от тучки и мягкое падение к двери домика
        u = clamp((t - T_TOUCH) / .7)
        land = (700, S05_HOUSE[1] - 70)
        cx, cy = bezier(CARD_HIT, (620, 520), land, ease_in(u, 1.5))
        rot = lerp(12, -14, u)
        ck = .85
        if u >= 1:
            sxq, syq = P.squash(t, T_TOUCH + .7, .2)
            rot = -14
    card = P.card(0, 0, 1.0, 0, 0.0, seed=7)
    if t >= T_TOUCH + .7:
        card = f'<g transform="translate(0 115) scale({sxq:.4f} {syq:.4f}) translate(0 -115)">{card}</g>'
    o.append(f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f}) scale({ck:.4f})">{card}</g>')
    if T_TOUCH <= t < T_TOUCH + .35:
        o.append(P.clink(CARD_HIT[0], CARD_HIT[1], 2.0, (t - T_TOUCH) / .35, seed=8, col=INK))
    if T_WARM <= t < T_WARM + .5:   # тёплые искорки на «настроение»
        o.append(P.sparkles(S05_HOUSE[0], S05_HOUSE[1] - 250, 1.6, 1 - (t - T_WARM) / .5, t, seed=9, n=6, r=260))
    # камера: наезд с разгоном к открытке до 10.40, затем откат на всю сцену, лёгкий дальнейший отъезд
    if t < T_LAUNCH:
        u = ease_in(clamp((t - 10.2) / .2), 2.2)
        ccx, ccy, s = lerp(400, CARD0[0], u), lerp(1150, CARD0[1], u), lerp(1.25, 1.75, u)
        rot = lerp(0, -3, u)
    else:
        u = ease_out((t - T_LAUNCH) / .6, 3)
        ccx, ccy, s = lerp(CARD0[0], 540, u), lerp(CARD0[1], 930, u), lerp(1.75, 1.0, u)
        rot = lerp(-3, 0, u)
        if t > 11.0:
            s *= 1 - .07 * ease_io((t - 11.0) / 2.4)
            ccy -= 20 * ease_io((t - 11.0) / 2.4)
    dx, dy = P.shake(t, T_TOUCH, 14, .35, 1)
    bg = mix(P.C_PAGE, "#2C3463", night)
    return frame_svg("".join(o), ccx - dx, ccy - dy, s, rot, bg)


# ═══════════════════════════════ s12: календарь ═══════════════════════════════
CAL = (540, 900, 820, 900)
T_E, T_C, T_M, T_FLIP = 29.20, 29.50, 29.84, 30.48


def stamps_at(t):
    """Сколько солнышек проставлено: «ещё» — медленно, «целый» — быстрее, «месяц» — заполнить всё."""
    if t < T_E:
        return 0.0
    if t < T_C:
        return 4.0 * (t - T_E) / (T_C - T_E)
    if t < T_M:
        return 4.0 + 10.0 * (t - T_C) / (T_M - T_C)
    return min(35.0, 14.0 + 21.0 * ease_in(clamp((t - T_M) / .4), 1.4))


def s12(t):
    x, y, w, h = CAL
    st = stamps_at(t)
    gl = ease_out((t - (T_M + .35)) / .25)
    fl = ease_in(clamp((t - T_FLIP) / .32), 1.6)
    trem = 3 * math.sin(t * 47) * gl * (1 - fl) * clamp((T_FLIP - t) / .1 + 1)
    o = [paper_bg()]
    # под листом календаря — следующий день: тёплый стол Димы (дерево и полоса солнца), открывается при перевороте
    if fl > 0:
        o.append(blob(rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2), P.C_WOOD))
        for j in range(5):
            yy = y - h / 2 + 90 + 170 * j
            o.append(line([(x - w / 2, yy), (x, yy + 14), (x + w / 2, yy - 6)], 4, P.C_WOOD_SH, taper=.2, wmin=.4, seed=1200 + j))
        o.append(blob([(x - w / 2, y + 120), (x + 60, y - h / 2), (x + 300, y - h / 2), (x - w / 2 + 40, y + h / 2), (x - w / 2, y + h / 2)], "#E8B77C"))
        o.append(P.letter(x + 60, y + 120, 1.2, -6, write=1.0, seed=3))
        o.append(line([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2), (x - w / 2, y - h / 2)], 4.2, INK,
                      taper=0, wmin=1, seed=1210))
    # гвоздик
    o.append(P.calendar(x + trem, y, w, h, st, gl, fl, t, seed=1))
    # солнышко на только что проставленной клетке — короткие искорки
    if 0 < st < 35:
        i = int(st)
        cx, cy = P.calendar_cell(x, y, w, h, i)
        o.append(P.clink(cx, cy, 1.0, (st - i), seed=i, col="#E9A21F"))
    if gl > 0 and fl < .3:
        o.append(P.sparkles(x, y + 60, 2.2, gl, t, seed=12, n=7, r=300))
    # камера: наезд на сетку, ход за бегущими солнышками; на «Поэтому» хлёсткий поворот за листом вверх
    u = ease_out(clamp((t - 29.0) / 1.4), 2)
    s = lerp(1.08, 1.32, u)
    i = int(clamp(st, 0, 34))
    ccx, ccy = P.calendar_cell(x, y, w, h, i)
    fx = lerp(x, ccx, .35 * (1 - gl))
    fy = lerp(y + 40, ccy, .35 * (1 - gl))
    rot = 0.0
    if t > T_FLIP:
        e = ease_in(clamp((t - T_FLIP) / .5), 2.2)
        fy -= 260 * e
        s *= 1 + .25 * e
        rot = -6 * e
    dx, dy = P.shake(t, T_M + .35, 8, .3, 3)
    return frame_svg("".join(o), fx - dx, fy - dy, s, rot, P.C_PAGE)


def frame(sid, t):
    lib.dyn_begin()
    lib.DEFS.clear()
    return {"s05": s05, "s06": s06, "s12": s12}[sid](t)


def s06(t):
    import s64a_s06
    return s64a_s06.s06(t)
