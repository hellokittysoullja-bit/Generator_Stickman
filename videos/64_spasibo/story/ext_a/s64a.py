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
    d = "".join(f"M-900 {i * 64}H2000" for i in range(-14, 44)) + "".join(f"M{i * 64} -900V2800" for i in range(-14, 32))
    return (f'<path d="M-900 -900H2000V2800H-900Z" fill="{col or P.C_PAGE}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def bezier(p0, p1, p2, u):
    a = (1 - u) ** 2
    b = 2 * u * (1 - u)
    c = u * u
    return (a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1])


# ═══════════════════════════════ s05: открытка, туча → солнце ═══════════════════════════════
S05_HOUSE = (540, 1180)
S05_CLOUD = (540, 650)          # центр дна тучки
S05_SUN = (540, 470)            # где солнце стоит (верх дуги)
ARC_R = 430.0
ARC_C = (540, 470 + .8 * ARC_R)
T_LAUNCH, T_TOUCH, T_WARM, T_LONG = 10.40, 11.02, 11.55, 12.14
T_LONG_END = 13.02
CARD0 = (230, 1440)
CARD_CTRL = (100, 560)
CARD_HIT = (470, 590)


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
    o.append(P.tree(860, gy, 1.9, warm, t, seed=1))
    o.append(P.tree(200, gy, 1.5, warm, t + .7, seed=2))
    o.append(P.house(S05_HOUSE[0], gy, 2.1, warm, seed=3))
    # тучка до касания, потом лопается
    if t < T_TOUCH:
        jig = 3 * math.sin(t * 13) * clamp((t - 10.75) / .25)
        o.append(P.gloom(S05_CLOUD[0] + jig, S05_CLOUD[1], 2.5, t, 1.0, seed=4))
    else:
        o.append(P.gloom_burst(S05_CLOUD[0], S05_CLOUD[1] + 40, 2.5, (t - T_TOUCH) / .5, seed=4))
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
            svg_arc, _ = P.day_arc(ARC_C[0], ARC_C[1], ARC_R, ph, seed=5)
            if (ph % 2.0) < 1.0:   # солнце на дуге — с лучами, чуть крупнее
                q = ph % 1.0
                a = math.pi * (1 - q)
                o.append(P.sun(ARC_C[0] + ARC_R * math.cos(a), ARC_C[1] - .8 * ARC_R * math.sin(a), 92, 1.0, t, seed=5))
            else:
                o.append(svg_arc)
        else:
            o.append(P.sun(x, y, 92 * k, rays, t, seed=5))
        if T_LONG - .05 < t < T_LONG + .2 or t > T_LONG_END:
            o.append(P.sparkles(S05_SUN[0], S05_SUN[1], 1.3, clamp((t - T_LONG_END) / .2) if t > T_LONG_END else .7, t, seed=6, n=5, r=150))
    # открытка
    if t < T_LAUNCH:
        cx, cy, rot, ck = CARD0[0], CARD0[1] + 4 * math.sin(t * 20), -8 + 3 * math.sin(t * 9), 1.25
    elif t < T_TOUCH:
        u = ease_in((t - T_LAUNCH) / (T_TOUCH - T_LAUNCH), 1.6)
        cx, cy = bezier(CARD0, CARD_CTRL, CARD_HIT, u)
        rot = -8 + 380 * u
        ck = lerp(1.25, 1.0, u)
    else:   # отскок от тучки и мягкое падение к двери домика
        u = clamp((t - T_TOUCH) / .7)
        land = (735, S05_HOUSE[1] - 92)
        cx, cy = bezier(CARD_HIT, (620, 520), land, ease_in(u, 1.5))
        rot = lerp(12, -14, u)
        ck = 1.0
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
        ccx, ccy, s = lerp(CARD0[0], 540, u), lerp(CARD0[1], 915, u), lerp(1.75, 1.14, u)
        rot = lerp(-3, 0, u)
        if t > 11.0:
            s *= 1 - .06 * ease_io((t - 11.0) / 2.4)
            ccy -= 20 * ease_io((t - 11.0) / 2.4)
    dx, dy = P.shake(t, T_TOUCH, 14, .35, 1)
    bg = mix(P.C_PAGE, "#2C3463", night)
    return frame_svg("".join(o), ccx - dx, ccy - dy, s, rot, bg)


# ═══════════════════════════════ s12: календарь ═══════════════════════════════
CAL = (540, 900, 840, 820)
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
        o.append(lib.shape(rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2), P.C_WOOD, "", w=4.2, seed=1210))
        for j in range(5):
            yy = y - h / 2 + 90 + 170 * j
            o.append(line([(x - w / 2, yy), (x, yy + 14), (x + w / 2, yy - 6)], 4, P.C_WOOD_SH, taper=.2, wmin=.4, seed=1200 + j))
        cdesk = lib.clip_rect(x - w / 2, y - h / 2, w, h)
        o.append(f'<g clip-path="url(#{cdesk})">' + blob([(x - w / 2 - 300, y + 380, 1), (x + 40, y - h / 2 - 100, 1), (x + 300, y - h / 2 - 100, 1),
                                                          (x - w / 2 + 20, y + h / 2 + 200, 1)], "#E8B77C") + '</g>')
        o.append(P.letter(x + 60, y + 120, 1.2, -6, write=1.0, seed=3))

    # гвоздик
    o.append(P.calendar(x + trem, y, w, h, st, gl * (1 - clamp(fl * 4)), fl, t, seed=1))
    # солнышко на только что проставленной клетке — короткие искорки
    if 0 < st < 35:
        i = int(st)
        cx, cy = P.calendar_cell(x, y, w, h, i)
        o.append(P.clink(cx, cy, 1.0, (st - i), seed=i, col="#E9A21F"))
    if gl > 0 and fl < .3:
        o.append(P.sparkles(x, y + 60, 2.2, gl, t, seed=12, n=7, r=300))
    # камера: наезд на сетку, ход за бегущими солнышками; на «Поэтому» хлёсткий поворот за листом вверх
    u = ease_out(clamp((t - 29.0) / 1.6), 2)
    s = lerp(1.0, 1.12, u)
    i = int(clamp(st, 0, 34))
    ccx, ccy = P.calendar_cell(x, y, w, h, i)
    fx = lerp(x, ccx, .12 * (1 - gl))
    fy = lerp(y + 90, ccy + 90, .12 * (1 - gl))
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


# ═══════════════════════════════ s06: Дима по-турецки, пузыри-воспоминания ═══════════════════════════════
D6 = (520, 1250, 1.0)                  # таз Димы (x, y), масштаб
T_MEM, T_GOOD, T_RARE = 14.14, 14.56, 15.41
# пузыри: центр, ширина, высота, момент выскока
BUB = [((190, 560), 330, 250, T_MEM), ((420, 250), 330, 250, T_MEM + .11), ((760, 240), 330, 250, T_MEM + .22), ((925, 580), 300, 240, T_MEM + .33)]


def pie(x, y, k=1.0):
    """Пирог на блюде (ЦЕНТР дна) — для пузыря «мама с пирогом»."""
    o = [lib.shape(ellipse_pts(0, 0, 120, 26, 18), "#EDE6D6", blob(ellipse_pts(0, 8, 110, 16, 14), "#CFC4AE"), w=3.2, seed=6101)]
    o.append(lib.shape([(-96, -4, 1), (-90, -56), (-40, -76), (40, -76), (90, -56), (96, -4, 1)], "#D99A4E",
                       blob(ellipse_pts(0, -60, 84, 18, 14), "#EDB86A") + blob(rect_pts(-100, -30, 100, 0), "#B77A35"), w=3.6, seed=6102))
    for j in range(4):
        o.append(line([(-60 + 40 * j, -66), (-48 + 40 * j, -58)], 4, "#9A5F28", taper=.4, wmin=.4, seed=6110 + j))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})">{"".join(o)}</g>'


def bub_inner(i, t):
    """Картинка внутри пузыря i (локально: (0, 0) — центр). Люди и кот — из common/people.py, cat.py."""
    import people as PP
    if i == 0:   # учительница с листом (молодая, как в s02)
        r = PP.teacher("young", 0, 150, .2, "praise", "letter", layers=("arm_f", "body", "pelvis"))
        w = r["wrist"]
        lt = P.letter((w["n"][0] + w["f"][0]) / 2 + 6, (w["n"][1] + w["f"][1]) / 2 - 18, .28, -6, write=1.0, seed=11)
        r2 = PP.teacher("young", 0, 150, .2, "praise", "letter", layers=("arm_n",))
        return r["svg"] + lt + r2["svg"]
    if i == 1:   # друг протягивает руку для пожатия
        sw = 4 * math.sin(t * 6)
        r = PP.person("friend", -20, 150, .2, "", None, arms={"n": ("ik", (90 + sw, 20), -1)},
                      hands={"n": {"dir": (1, -.15), "curl": (.15, .15, .2, .25), "spread": .1, "thumb": .45}})
        return r["svg"]
    if i == 2:   # мама с пирогом
        r = PP.person("mama", -40, 160, .2, "", None, arms={"f": ("ik", (20, 40), -1), "n": ("ik", (75, 46), -1)},
                      hands={"f": {"curl": (.5, .5, .55, .6), "thumb": .5, "dir": (1, .2)}, "n": {"curl": (.5, .5, .55, .6), "thumb": .5, "dir": (-.2, 1)}},
                      layers=("arm_f", "body", "pelvis"))
        r2 = PP.person("mama", -40, 160, .2, "", None, arms={"f": ("ik", (20, 40), -1), "n": ("ik", (75, 46), -1)},
                       hands={"f": {"curl": (.5, .5, .55, .6), "thumb": .5, "dir": (1, .2)}, "n": {"curl": (.5, .5, .55, .6), "thumb": .5, "dir": (-.2, 1)}},
                       layers=("arm_n",))
        return r["svg"] + pie(55, 40, .55) + r2["svg"]
    # кот на подоконнике: окно днём, подоконник, кот сидит и щурится
    o = P.window(0, 40, 230, 220, "day", t, seed=21, curtain=False)
    o += lib.shape(rect_pts(-150, 36, 150, 56), P.C_WOOD, blob(rect_pts(-150, 48, 150, 58), P.C_WOOD_SH), w=3.2, seed=6120)
    import cat
    o += cat.draw(-10, 40, .32, {"tail": 6 * math.sin(t * 2), "blink": 1.0 if (t % 2.3) < .12 else 0.0, "smile": .6}, t)
    return o


def s06(t):
    import people as PP
    x, y, sc = D6
    o = [paper_bg()]
    # пол-подушка под Димой: тень на бумаге
    o.append(blob(ellipse_pts(x + 30, y + 150 * sc, 360 * sc, 40 * sc, 22), "#E6D9B8"))
    # Дима: по-турецки, ближняя ладонь подпирает щёку, локоть на колене; живое качание и вдох
    sway = .03 * math.sin(t * 2.1)
    ex = "thoughtful"
    if t >= T_GOOD - .05:
        ex = dict(PP.EXPR["dima"]["calm_smile"], look=(.3, -.55))
    if t >= T_RARE + .1:
        ex = dict(PP.EXPR["dima"]["thoughtful"], look=(.1, -.3))
    kw = PP.lotus_kw("sit", x, y, sc)
    base = PP.figure("dima", x, y, sc, PP.EXPR["dima"]["thoughtful"], **kw)
    hx, hy = base["head"]
    kw["arms"]["n"] = ("ik", (hx + 46 * sc, hy + 200 * sc), -1)
    kw["hands"]["n"] = {"dir": (.15, -1), "curl": (.35, .4, .45, .5), "thumb": .3}
    kw["hands"]["f"] = {"dir": (.2, 1), "curl": (.35, .4, .45, .5), "thumb": .45}
    kw["head_ang"] = .16 + .03 * math.sin(t * 1.3)
    kw["lean"] = kw["lean"] + sway
    exd = PP.EXPR["dima"][ex] if isinstance(ex, str) else ex
    fig = PP.figure("dima", x, y, sc, exd, **kw)
    o.append(fig["svg"])
    hx, hy = fig["head"]
    head_top = (hx - 10, hy - 150 * sc)
    # пузыри
    for i, ((bx, by), bw, bh, t0) in enumerate(BUB):
        if t < t0:
            continue
        sx_, sy_ = P.pop(t, t0, amp=.28)
        u = min(sx_, sy_) if t - t0 < 1.0 else 1.0
        warm = ease_out((t - (T_GOOD + .07 * i)) / .3)
        pale = ease_io((t - (T_RARE + .05 * i)) / .4)
        thread = ease_out((t - (T_RARE + .08 + .05 * i)) / .45)
        pull = ease_io((t - (T_RARE + .15)) / .6)
        bx2 = lerp(bx, head_top[0], .14 * pull)
        by2 = lerp(by, head_top[1], .14 * pull) + 6 * math.sin(t * 2.4 + i)
        u *= 1 - .12 * pull
        warm *= 1 - pale
        o.append(P.memory_bubble(bx2, by2, bw, bh, u, seed=i + 1, inner=bub_inner(i, t), head=head_top, thread=thread, pale=pale, warm=warm))
        if T_GOOD + .07 * i <= t < T_GOOD + .07 * i + .5:
            o.append(P.sparkles(bx2, by2, 1.2, 1 - (t - T_GOOD - .07 * i) / .5, t, seed=30 + i, n=4, r=bw * .62))
    # камера: медленный дрейф вверх за пузырями, лёгкий откат; к «редко» — чуть вниз к голове
    u = ease_io(clamp((t - 12.97) / 2.2))
    cx_, cy_, s = lerp(560, 540, u), lerp(1010, 880, u), lerp(1.04, .97, u)
    if t > T_RARE:
        e = ease_io((t - T_RARE) / .7)
        cy_ += 50 * e
        s += .03 * e
    return frame_svg("".join(o), cx_, cy_, s, .6 * math.sin(t * .9), P.C_PAGE)
