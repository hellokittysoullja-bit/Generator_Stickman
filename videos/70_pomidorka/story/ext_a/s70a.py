"""Рилс 70 «помидорка», группа A: графика на бумаге.
s02 (1.42–2.84, whip): таймер-помидорка на пьедестале с лавровыми веточками и искорками (популярный совет); «худший» (1.48)
    пьедестал трескается зигзагом, помидорка подпрыгивает; «совет» (1.97) пьедестал разваливается, помидорка падает и шлёпается
    в красную кляксу с семечками, клякса растекается и капает. Камера: наезд на помидорку, на шлепке подскок и тряска.
s09 (14.20–16.50, whip): Дима со спины на переднем плане; перед ним маленький таймер. «Двадцать пять минут» (14.24–15.52) таймер
    тянется вверх и растёт, «звучат как» (15.57–16.08) вырастает гора с вершиной-помидоркой, склоны штрихуются; «гора» (16.12)
    гора дорисована, тень накрывает Диму, он запрокидывает голову. Камера: наезд с разгоном вверх по горе, потом лёгкий откат.
s10 (16.50–18.90): подножие горы, Дима сбоку в полный рост перед ступенькой-камнем; «когда даже» ступенька светится; «первая
    минута» (17.01–17.6) ставит ногу; «кажется невозможной» (17.66–18.64) ступенька вытягивается в стену выше головы, нога
    повисает, Дима отступает, плечи к ушам. Камера: дрейф вверх вдоль стены, тряска на 18.04.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Предметы — common/props.py, люди — common/people.py."""
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
from lib import blob, clamp, ease_in, ease_io, ease_out, line, mix, rect_pts, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def frame_svg(body, cx, cy, s, rot, bg):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>')


def paper_bg(col=None, grid="#D9DCD6"):
    d = "".join(f"M-900 {i * 64}H2000" for i in range(-14, 46)) + "".join(f"M{i * 64} -900V2800" for i in range(-14, 32))
    return (f'<path d="M-900 -900H2000V2800H-900Z" fill="{col or P.C_PAGE}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def darken(svg_, u):
    """Тень на фигуре: фильтр яркости (фигура остаётся сплошной)."""
    if u <= 0.01:
        return svg_
    k = 1 - .38 * clamp(u)
    fid = f"dk{int(k * 1000)}"
    if not any(f'id="{fid}"' in x for x in lib.DEFS):
        lib.DEFS.append(f'<filter id="{fid}"><feColorMatrix type="matrix" values="{k} 0 0 0 0 0 {k} 0 0 0 0 0 {k * 1.05:.3f} 0 0 0 0 0 1 0"/></filter>')
    return f'<g filter="url(#{fid})">{svg_}</g>'


def whip_in(t, t0, dur=.2):
    u = clamp((t - t0) / dur)
    e = 1 - ease_out(u, 3)
    return -150 * e, -2.0 * e


# ═══════════════════════════════ s02: помидорка на пьедестале → клякса ═══════════════════════════════
T2_BAD = wt("худший")            # 1.48
T2_ADV = wt("совет")             # 1.97
T2_FALL = T2_ADV + .02
T2_HIT = T2_FALL + .26           # шлепок
GROUND2 = 1120.0
PED = (540.0, GROUND2, 1.55)
TOMK2 = 1.45


def s02(t):
    lib.dyn_begin()
    o = [paper_bg()]
    # пол-линия листа
    o.append(line([(-300, GROUND2 + 4), (400, GROUND2), (1400, GROUND2 + 3)], 5, INK, taper=.05, wmin=.8, seed=2001))
    px, py, pk = PED
    top = P.pedestal_top(px, py, pk)
    crack_u = ease_out((t - T2_BAD) / .28)
    split = ease_in(clamp((t - T2_ADV) / .3), 2)
    # пьедестал: трещина бежит, на «совет» половинки разъезжаются и оседают
    ped = P.pedestal(px, py + 30 * split, pk, crack_=crack_u, split=split, seed=1)
    o.append(ped)
    # лавры и искорки — только пока помидорка «награда»
    glory = 1 - clamp((t - T2_ADV) / .2)
    tom_y = top[1] - P.TOMATO_RY * TOMK2 + 6
    if glory > 0:
        sway = 4 * math.sin(t * 6)
        o.append(f'<g transform="rotate({sway:.2f} {px - 210} {tom_y + 120})">' + P.laurel(px - 205, tom_y + 140, 1.35 * glory, 1, side=-1, seed=1) + "</g>")
        o.append(f'<g transform="rotate({-sway:.2f} {px + 210} {tom_y + 120})">' + P.laurel(px + 205, tom_y + 140, 1.35 * glory, 1, side=1, seed=2) + "</g>")
        o.append(P.sparkles(px, tom_y - 20, 2.4, glory, t, seed=3, n=6, r=150))
    # помидорка: на пьедестале тикает и подрагивает; «худший» — подскок; «совет» — падает, вращаясь
    if t < T2_HIT:
        hop1 = P.hop(t, T2_BAD, 70, .3)
        if t < T2_FALL:
            x, y = px, tom_y + hop1
            rot = 3 * math.sin(t * 9) + (-8 * math.sin(math.pi * clamp((t - T2_BAD) / .3)))
        else:
            u = (t - T2_FALL) / (T2_HIT - T2_FALL)
            x = px + 30 * u
            y = lerp(tom_y, GROUND2 - 40, u * u)
            rot = 160 * u
        sq = P.squash(t, T2_BAD + .3, .12)
        o.append(f'<g transform="translate({x:.1f} {y + P.TOMATO_RY * TOMK2:.1f}) scale({sq[0]:.4f} {sq[1]:.4f}) translate({-x:.1f} {-y - P.TOMATO_RY * TOMK2:.1f})">'
                 + P.tomato_timer(x, y, TOMK2, rot, wedge=P.WEDGE_25, shake=2.0, leaf_swing=10 * math.sin(t * 8), t=t, seed=2) + "</g>")
        if t >= T2_FALL:
            for j in range(3):      # штрихи падения
                yy = y - 170 - 60 * j
                o.append(line([(x - 60 + 60 * j, yy), (x - 60 + 60 * j, yy - 90)], 5, INK, taper=.6, wmin=.2, seed=2010 + j, op=.8))
    else:
        u = ease_out((t - T2_HIT) / .22, 3)
        drip = .62 * clamp((t - T2_HIT - .25) / .55)
        sx = P.squash(t, T2_HIT, .18)
        o.append(f'<g transform="translate({px + 30} {GROUND2 - 10}) scale({sx[0]:.4f} {sx[1]:.4f}) translate({-px - 30} {-GROUND2 + 10})">'
                 + P.splat(px + 30, GROUND2 - 10, 1.9, .25 + .75 * u, drip, t, seed=4) + "</g>")
        # хвостик-листик лежит на кляксе
        lx, ly = px + 40, GROUND2 - 34
        lv = []
        for j, a in enumerate((-170, -120, -60, -10, 40, 100)):
            aa = math.radians(a)
            tip = (lx + 70 * math.cos(aa), ly + 34 * math.sin(aa))
            nx, ny = -math.sin(aa) * 14, math.cos(aa) * 7
            m = ((lx + tip[0]) / 2, (ly + tip[1]) / 2)
            lv.append(lib.shape([(lx, ly, 1), (m[0] + nx, m[1] + ny), (tip[0], tip[1], 1), (m[0] - nx, m[1] - ny)], P.C_LEAF if j % 2 else P.C_LEAF_SH, "",
                                w=3.4, seed=2030 + j))
        lv.append(lib.shape(lib.band([(lx, ly), (lx + 6, ly - 22), (lx + 18, ly - 34)], 14, 10, step=4, cap=True), P.C_LEAF_SH, "", w=3, seed=2040))
        o.append("".join(lv))
        o.append(P.clink(px + 30, GROUND2 - 70, 2.2, clamp((t - T2_HIT) / .3), seed=5, col=P.C_TOMATO))
    # камера: наезд на помидорку, на шлепке — подскок вниз к кляксе и тряска
    push = ease_io((t - 1.22) / (T2_FALL - 1.22))
    cx, cy, s = 540, lerp(840, 760, push), lerp(1.22, 1.38, push)
    if t > T2_FALL:
        v = ease_out((t - T2_FALL) / .4)
        cy = lerp(cy, 980, v)
        s = lerp(s, 1.28, v)
        cy += -46 * math.sin(math.pi * clamp((t - T2_HIT) / .18))
    dx, dy = P.shake(t, T2_HIT, 22, .38, seed=2)
    ex, ey = P.shake(t, T2_BAD, 8, .25, seed=1)
    wx, wr = whip_in(t, 1.42)
    return frame_svg("".join(o), cx - dx - ex - wx, cy - dy - ey, s, wr, P.C_PAGE)


# ═══════════════════════════════ s09: таймер → гора, Дима со спины ═══════════════════════════════
T9_DV = wt("двадцать", 14.0)      # 14.24
T9_MIN = wt("минут", 14.5)        # 15.25
T9_ZV = wt("звучат")              # 15.57
T9_GORA = wt("гора")              # 16.12
NECK9 = (500.0, 1330.0)
SC9 = 1.1
MT9 = (720.0, 1170.0, .86)        # гора: центр основания и масштаб
TIM9 = (735.0, 1150.0)            # дно маленького таймера на листе


def s09(t):
    lib.dyn_begin()
    o = [paper_bg()]
    mx, my, mk = MT9
    gy = my
    # тень горы ложится на лист (сплошная, тон бумаги темнее)
    sh = ease_out((t - T9_GORA + .05) / .3)
    # земля-линия горизонта
    o.append(line([(-400, gy + 6), (500, gy), (1500, gy + 4)], 5, INK, taper=.05, wmin=.8, seed=9001))
    # таймер растёт и тянется вверх (дно на месте)
    stretch = ease_io((t - T9_DV) / (T9_ZV - T9_DV))
    grow = ease_in(clamp((t - T9_ZV + .05) / (T9_GORA - T9_ZV + .05)), 1.6)
    hatch = ease_out((t - T9_ZV - .15) / (T9_GORA - T9_ZV + .25))
    if grow > 0.0:
        grow = .26 + .74 * grow
        if sh > 0:
            L = 900 * sh
            o.append(blob([(mx - 470 * mk, gy + 2, 1), (mx + 470 * mk, gy + 2, 1), (mx + 470 * mk - 120 * sh, gy + L, 1), (mx - 470 * mk - 700 * sh, gy + L, 1)],
                          "#E4D6B4"))
        o.append(P.mountain(mx, gy, mk, grow, hatch, seed=3))
        if grow < .45:      # «пуф» перехода
            o.append(P.sparkles(mx, gy - 380 * mk, 2.6, 1 - (grow - .26) / .19, t, seed=7, n=6, r=170))
    else:
        k = lerp(.62, .82, stretch)
        sy = 1 + .95 * stretch
        sx = 1 - .12 * stretch
        bx, by = TIM9
        cyb = by - P.TOMATO_RY * k
        tick = 1.4 * (1 - stretch * .5)
        g = P.tomato_timer(bx, cyb, k, 0, wedge=P.WEDGE_25 * (1 - .15 * stretch), shake=tick, leaf_swing=12 * math.sin(t * 7), t=t, seed=9)
        o.append(f'<g transform="translate({bx} {by}) scale({sx:.4f} {sy:.4f}) translate({-bx} {-by})">{g}</g>')
        if stretch > 0:
            for j in range(3):          # штрихи роста вверх
                yy = by - 2 * P.TOMATO_RY * k * sy - 40 - 50 * j
                o.append(line([(bx - 90 + 90 * j, yy + 60), (bx - 90 + 90 * j, yy)], 5, INK, taper=.6, wmin=.2, seed=9010 + j, op=.75 * stretch))
    # Дима со спины: вдох, на «гора» запрокидывает голову, плечи вверх; тень темнит его
    lu = ease_out((t - T9_GORA) / .3)
    breathe = 1.5 * math.sin(t * 3.1)
    tilt = lerp(-3 + 2 * math.sin(t * 1.7), 0, lu) + 6 * stretch * (1 - lu)
    dimab = people.dima_back(NECK9[0], NECK9[1] + breathe, SC9, tilt=tilt, look_up=lu, shrug=.5 * lu + .2 * stretch, t=t)
    o.append(darken(dimab["svg"], .9 * sh))
    # камера: близко к Диме и таймеру → разгон вверх по горе к пику на «гора» → лёгкий откат
    a = ease_io((t - 14.0) / (T9_ZV - 14.0))
    cx, cy, s = lerp(650, 660, a), lerp(1150, 1110, a), lerp(1.3, 1.36, a)
    up = ease_in(clamp((t - T9_ZV + .25) / (T9_GORA - T9_ZV + .25)), 2.2)
    cy = lerp(cy, 935, up)
    s = lerp(s, 1.03, up)
    cx = lerp(cx, 600, up)
    back = ease_out((t - T9_GORA) / .55)
    s = lerp(s, 1.0, back)
    dx, dy = P.shake(t, T9_GORA, 14, .35, seed=9)
    wx, wr = whip_in(t, 14.2)
    return frame_svg("".join(o), cx - dx - wx, cy - dy, s, wr, P.C_PAGE)


# ═══════════════════════════════ s10: ступенька → стена ═══════════════════════════════
T10_KOG = wt("когда")             # 16.52
T10_FIRST = wt("первая")          # 17.01
T10_KAZ = wt("кажется")           # 17.66
T10_NEV = wt("невозможной")       # 18.04
G10 = 1250.0
SC10 = .7
STEP = (720.0, G10, 1.0)


def s10(t):
    lib.dyn_begin()
    o = [paper_bg()]
    # подножие горы сзади (та же гора: серые склоны со штрихами)
    o.append(P.mountain(980, G10 + 20, 1.7, 1.0, 1.0, seed=3))
    o.append(line([(-400, G10 + 4), (600, G10), (1600, G10 + 4)], 5, INK, taper=.05, wmin=.8, seed=10001))
    sx_, sy_, sk = STEP
    wall = ease_in(clamp((t - T10_KAZ) / (18.64 - T10_KAZ)), 1.4)
    wall = ease_io(wall) * .25 + wall * .75
    glow = clamp(.55 + .45 * math.sin(t * 5)) * (1 - .9 * wall) * ease_out((t - 16.3) / .4)
    o.append(P.step_wall(sx_, sy_, sk, wall, glow, t, seed=1))
    step_top_y = P.step_top(sx_, sy_, sk, wall)
    # Дима: смотрит на ступеньку → нога на ступеньку → ступенька уходит вверх, нога повисает → отступает, плечи к ушам
    lift = ease_io((t - T10_FIRST) / .45)
    back = ease_io((t - T10_NEV + .1) / .5)
    hx = lerp(430, 330, back)
    hy = G10 - (people.LEG_LEN - 12) * SC10 * people.HEIGHT["dima"]
    st = people.stand_kw(hx, hy, SC10)
    fn = st["feet"]["n"]
    foot_on = (sx_ - 70, sy_ - 80 * sk)
    # ступня едет вверх со стеной, пока не соскользнёт (к «невозможной»)
    slip = ease_in(clamp((t - T10_KAZ - .08) / .3), 2)
    on_y = lerp(foot_on[1], min(foot_on[1], step_top_y), 0) - 70 * slip * (1 - back)
    fx = lerp(fn[0][0], foot_on[0] - 20 * slip, lift * (1 - back))
    fy = lerp(fn[0][1], on_y, lift * (1 - back))
    if back > 0:
        fx = lerp(fx, fn[0][0], back)
    st["feet"]["n"] = ((fx, fy), -.25 * lift * (1 - back))
    if wall < .02 and lift < .02:
        expr = dict(people.EXPR["dima"]["hope"], look=(.6, .55), bags=False)
    elif back < .3:
        expr = dict(people.EXPR["dima"]["resolve"], look=(.6, .4 - .9 * wall), bags=False)
    else:
        expr = dict(people.EXPR["dima"]["surprise_day"], look=(.55, -.8), brows="worry", mouth="o", open=.3)
    shrug = ease_out((t - T10_NEV) / .3)
    sc = SC10 * people.HEIGHT["dima"]
    arms = {"f": ("ang", 0.25 + .3 * lift, 0.3), "n": ("ang", -0.15, 0.6)}
    hands = None
    if back > 0:
        arms = {k: people.mix_ang(arms[k], people.ik_ang("dima", hx, hy, SC10, -.06 * back, (hx + tx * sc, hy + ty * sc), -1, near=(k == "n")), ease_out(back * 1.6))
                for k, (tx, ty) in (("f", (120, -310)), ("n", (165, -330)))}
        hands = {"f": {"dir": (.4, -1), "curl": (.6, .65, .7, .7), "thumb": .5}, "n": {"dir": (.3, -1), "curl": (.65, .7, .72, .75), "thumb": .6}}
    lean = -.06 * back + .04 * lift * (1 - back)
    f = people.dima(hx, hy, SC10, expr, None, arms=arms, hands=hands, shrug=shrug, lean_add=lean, head_add=-.18 * wall, **st)
    o.append(f["svg"])
    if back > 0:      # штрихи испуга над головой
        hx2, hy2 = f["head"]
        for j in range(3):
            a = math.radians(-130 + 40 * j)
            r0, r1 = 150, 150 + 60 * clamp(back * 2)
            o.append(line([(hx2 + r0 * math.cos(a), hy2 + r0 * math.sin(a)), (hx2 + r1 * math.cos(a), hy2 + r1 * math.sin(a))], 6, INK, taper=.5, wmin=.3,
                          seed=10020 + j, op=clamp(1.5 - back)))
    # камера: дрейф вверх вдоль растущей стены, тряска на «невозможной»
    a = ease_io((t - 16.3) / 2.8)
    up = ease_io(wall)
    cx, cy, s = lerp(560, 580, a), lerp(860, 780, a) - 80 * up, lerp(1.02, .98, a)
    dx, dy = P.shake(t, T10_NEV, 18, .4, seed=10)
    return frame_svg("".join(o), cx - dx, cy - dy, s, 0, P.C_PAGE)


SHOTS = {"s02": s02, "s09": s09, "s10": s10}


def frame(sid, t):
    return SHOTS[sid](t)
