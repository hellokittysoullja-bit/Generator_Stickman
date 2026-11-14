"""Рилс 71 «два лагеря», группа A: графика на бумаге — друг-тост и два лагеря.
s02 (1.92–3.98, whip): соседская кровать сбоку, друг спит; «встаёте» (2.60) выстреливает вверх, как тост, одеяло слетает и само
    складывается квадратом на кровать; «и делаете» (3.20–3.76) приземляется на ноги и бодро уходит вправо, дуги скорости, подушка
    взбивается. Камера подскакивает с другом, потом короткий проезд за ним.
s04 (5.62–7.55, whip): пустые пузыри-реплики влетают из-за краёв и кружат роем («комментариях» 5.72); «спорят» (6.45) рой
    раскалывается вспышкой-зигзагом; «два лагеря» (6.76–7.36) на холмах вырастают жёлтая и синяя палатки, пузыри разлетаются к своим.
    Камера: отъезд от роя к палаткам, удар на «два».
s05 (7.55–9.36): жёлтый лагерь крупно; «Одни» (7.63) палатка подскакивает и распахивает полог; «пишут» (8.13) пулемёт пузырей со
    стрелкой вверх; «просто встаёшь» (8.59–9.28) большой пузырь надувается и летит прямо в камеру.
s07 (10.66–12.92, whip): синий лагерь; «Другие» (10.72) полог приоткрывается, медленно выплывают мягкие пузыри с клубком;
    «я тоже так не могу» (11.96–12.88) пузыри по одному садятся в ряд и кивают. Камера — медленный тёплый дрейф вдоль ряда.
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
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?:«»").strip(",.!?:«»").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def frame_svg(body, cx, cy, s, rot, bg):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>')


def paper_bg(col=None, grid="#D9DCD6"):
    d = "".join(f"M-900 {i * 64}H2600" for i in range(-14, 46)) + "".join(f"M{i * 64} -900V2800" for i in range(-14, 42))
    return (f'<path d="M-900 -900H2600V2800H-900Z" fill="{col or P.C_PAGE}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def whip_in(t, t0, dur=.2):
    u = clamp((t - t0) / dur)
    e = 1 - ease_out(u, 3)
    return -150 * e, -2.0 * e


def quilt_panel(x, y, w, h, rot=0.0, seed=0, col="blue"):
    """Плоское одеяло-полотно (летит / сложено): ЦЕНТР, w×h, синие стёжки."""
    c, csh, chi = P._QUILT[col]
    pts = [(-w / 2, -h / 2, 1), (w / 2, -h / 2, 1), (w / 2, h / 2, 1), (-w / 2, h / 2, 1)]
    inner = blob([(-w / 2, h * .15), (w / 2, h * .15), (w / 2, h / 2), (-w / 2, h / 2)], csh)
    n = max(2, int(w / 70))
    for i in range(n):
        xx = -w / 2 + w * (i + .5) / n
        inner += line([(xx, -h / 2 + 6), (xx + 4, h / 2 - 6)], 6, mix_c(chi), taper=.2, wmin=.7, seed=9300 + seed + i)
    inner += line([(-w / 2 + 8, -h / 2 + 10), (w / 2 - 8, -h / 2 + 12)], 4, chi, taper=.2, wmin=.6, seed=9320 + seed)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f})">{shape(pts, c, inner, w=4.4, seed=9310 + seed)}</g>'


def mix_c(c):
    return lib.mix(c, "#FFFFFF", .45)


# ═══════════════════════════════ s02: друг-тост ═══════════════════════════════
T2_UP = wt("встаёте")             # 2.60
T2_LAND = wt("и", 3.1)            # 3.20
T2_DEL = wt("делаете")           # 3.32
FL2 = 1250.0
BED2 = (400.0, FL2, 1.5)
MAT2 = FL2 - 118 * 1.5            # верх матраса
SC2 = .6
SCW2 = SC2 * people.HEIGHT["friend"]
HIP_STAND = FL2 - (people.LEG_LEN - 12) * SCW2      # таз стоящего друга
LIE_HIP = (600.0, MAT2 - 62)
LAND_X = 900.0
FOLD2 = (560.0, MAT2 - 34)                          # сложенное одеяло на кровати


def s02_friend(t):
    """SVG друга по времени."""
    if t < T2_UP:
        e = dict(people.EXPR["friend"]["sleep"])
        if t > T2_UP - .12:       # глаза распахнулись перед выстрелом
            e = dict(people.EXPR["friend"]["beam"])
        hx, hy = LIE_HIP
        br = 4 * math.sin(t * 5.5)
        f = people.person("friend", hx, hy, SC2, e, "rest", layers=("body",))
        return f'<g transform="rotate({-90 + br * .2:.2f} {hx} {hy})">{f["svg"]}</g>', 0.0
    if t < T2_LAND:
        u = (t - T2_UP) / (T2_LAND - T2_UP)
        x = lerp(LIE_HIP[0], LAND_X, ease_io(u))
        y0, y1 = LIE_HIP[1] - 120, HIP_STAND
        apex = 330.0
        y = lerp(y0, y1, u) - apex * 4 * u * (1 - u)
        rot = -90 * (1 - ease_out(clamp(u / .18), 2))
        vy = (y1 - y0) - apex * 4 * (1 - 2 * u)          # производная по u: растяжение при скорости
        st = 1 + .16 * clamp(abs(vy) / 900)
        kw = people.stand_kw(x, y, SC2, "friend", spread=30)
        f = people.person("friend", x, y, SC2, "beam", "hooray", **kw)
        g = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({1 / st ** .5:.4f} {st:.4f}) translate({-x:.1f} {-y:.1f})">'
             f'{f["svg"]}</g>')
        trails = ""
        if u < .5:
            for j in range(3):
                xx = x - 70 + 70 * j
                trails += line([(xx, y + 420 * SC2), (xx, y + 420 * SC2 + 140)], 6, INK, taper=.7, wmin=.1, seed=2050 + j, op=.85)
        return trails + g, 1.0
    # приземлился и уходит
    v = t - T2_LAND
    sx, sy = P.squash(t, T2_LAND, .14, 3.2, 8)
    x = LAND_X + 480 * clamp((v - .12) / .85) ** 1.3 if v > .12 else LAND_X
    walk = people.walk_kw(x, HIP_STAND, SC2, v * 2.6 if v > .12 else 0, "friend", stride=260, lift=70)
    hip = walk["hip"]
    e = dict(people.EXPR["friend"]["simple"])
    f = people.person("friend", hip[0], hip[1], SC2, e, "rest", feet=walk["feet"], lean_add=.08 * clamp(v / .2),
                      arms={"f": ("ang", .2 + .5 * math.sin(v * 2.6 * 2 * math.pi), .3), "n": ("ang", -.2 - .5 * math.sin(v * 2.6 * 2 * math.pi), .4)})
    g = (f'<g transform="translate({hip[0]:.1f} {FL2:.1f}) scale({sx:.4f} {sy:.4f}) translate({-hip[0]:.1f} {-FL2:.1f})">{f["svg"]}</g>')
    arcs = P.speed_arcs(hip[0] - 170, hip[1] - 120, 1.2, clamp((v - .15) / .2), t, seed=2) if v > .15 else ""
    return arcs + g, 2.0


def s02(t):
    lib.dyn_begin()
    o = [paper_bg()]
    o.append(line([(-500, FL2 + 4), (600, FL2), (2200, FL2 + 3)], 5, INK, taper=.05, wmin=.8, seed=2001))
    bx, by, bk = BED2
    o.append(P.bed(bx, by, bk, seed=2))
    # подушка: взбивается на «делаете»
    pp = P.squash(t, T2_DEL + .05, .22, 3, 6)
    o.append(f'<g transform="translate(170 {MAT2:.1f}) scale({pp[1]:.4f} {pp[0]:.4f}) translate(-170 {-MAT2:.1f})">' + P.pillow(170, MAT2 + 4, 1.45, -4, seed=2)
             + "</g>")
    fr, phase = s02_friend(t)
    # одеяло
    if t < T2_UP:
        br = 1 + .05 * math.sin(t * 5.5) + .12 * max(0.0, math.sin(math.pi * clamp((t - (T2_UP - .2)) / .2)))
        o.append(fr)
        o.append(P.blanket(640, MAT2 + 6, 1.0, w=620, h=150, seed=2, col="blue", bump=br))
    else:
        u = clamp((t - T2_UP) / .75)
        if u < .35:          # слетает вверх, крутясь
            v = u / .35
            x, y = lerp(640, 620, v), lerp(MAT2 - 60, MAT2 - 520, ease_out(v))
            w, h, rot = 620, lerp(120, 70, v), lerp(0, -18, v) + 8 * math.sin(t * 20)
        else:                # опускается и складывается квадратом
            v = ease_io((u - .35) / .65)
            x, y = lerp(620, FOLD2[0], v), lerp(MAT2 - 520, FOLD2[1], ease_in(v, 1.6))
            w, h, rot = lerp(620, 240, v), lerp(70, 64, v), lerp(-18, 0, v) + 6 * math.sin(t * 16) * (1 - v)
        sq = P.squash(t, T2_UP + .75, .25, 3, 7) if u >= 1 else (1, 1)
        if u >= 1:           # сложено: две «складки» поверх
            o.append(quilt_panel(x, y + 4, w * sq[0], h * sq[1], 0, 2))
            o.append(line([(x - w / 2 + 10, y - 4), (x + w / 2 - 10, y - 2)], 4, P.C_BLUE_SH, taper=.2, wmin=.6, seed=2061))
        else:
            o.append(quilt_panel(x, y, w, h, rot, 2))
        o.append(fr)
    # камера: крупно кровать → подскок с другом на «встаёте» (отъезд) → проезд за ним
    a = ease_io((t - 1.72) / .9)
    cx, cy, s = lerp(430, 450, a), 1040, lerp(1.55, 1.62, a)
    if t >= T2_UP:
        u = clamp((t - T2_UP) / (T2_LAND - T2_UP))
        z = ease_out(clamp(u / .35), 2)
        s = lerp(s, 1.04, z)
        cx = lerp(cx, 640, ease_io(u))
        cy = lerp(cy, 880, z) - 200 * math.sin(math.pi * u) * (1 - .3 * u)
    if t >= T2_LAND:
        cx += 420 * ease_io(clamp((t - T2_LAND - .1) / .85))
    dx, dy = P.shake(t, T2_UP, 16, .3, seed=21)
    ex, ey = P.shake(t, T2_LAND, 12, .3, seed=22)
    wx, wr = whip_in(t, 1.72)
    del phase
    return frame_svg("".join(o), cx - dx - ex - wx, cy - dy - ey, s, wr, P.C_PAGE)


# ═══════════════════════════════ s04: рой → раскол → два лагеря ═══════════════════════════════
T4_COM = wt("комментариях")       # 5.72
T4_SP = wt("спорят")              # 6.45
T4_TWO = wt("два", 6.5)           # 6.76
T4_LAG = wt("лагеря")            # 6.96
SW4 = (540.0, 720.0)
N4 = 10
HILL_L, HILL_R = (290.0, 1150.0), (800.0, 1150.0)
TK4 = .74


def hills(o):
    for (hx, hy), sd in ((HILL_L, 1), (HILL_R, 2)):
        pts = [(hx - 420, hy + 140, 1), (hx - 240, hy + 30), (hx, hy - 10), (hx + 240, hy + 30), (hx + 420, hy + 140, 1)]
        o.append(shape(pts, "#BFD79A", blob([(hx - 420, hy + 110), (hx + 420, hy + 110), (hx + 420, hy + 160), (hx - 420, hy + 160)], "#9DBE78"),
                       w=4.6, seed=4000 + sd))
        for j in range(5):
            gx = hx - 200 + 100 * j
            o.append(line([(gx, hy + 50 + abs(j - 2) * 12), (gx + 6, hy + 30 + abs(j - 2) * 12)], 3, "#6E9150", seed=4010 + 10 * sd + j))
    o.append(shape([(-600, 1290, 1), (-600, 1210), (1700, 1210), (1700, 1290, 1)], "#BFD79A", "", w=0, seed=4003, ink=False))


def s04(t):
    lib.dyn_begin()
    o = [paper_bg()]
    hills(o)
    # палатки вырастают на «два» и «лагеря»
    for (hx, hy), t0, col, fl in ((HILL_L, T4_TWO, "yellow", "bolt"), (HILL_R, T4_LAG, "blue", "yarn")):
        if t >= t0:
            px, py = P.pop(t, t0, amp=.35)
            o.append(f'<g transform="translate({hx} {hy}) scale({px:.4f} {py:.4f}) translate({-hx} {-hy})">'
                     + P.camp_tent(hx + 20, hy, TK4, col, fl, 0.0, 0.0, t, seed=4 + (col == "blue")) + "</g>")
    # рой: влетает из-за краёв, кружит, раскалывается, разлетается к палаткам
    split = ease_io(clamp((t - T4_SP) / .3))
    pos = P.swarm_pos(SW4[0], SW4[1], t, N4, 270, split, 290, seed=4)
    rs = P._rs(4400)
    starts = [(rs.uniform(-1, 1) * 900 + 540, -500 if i % 3 == 0 else (2400 if i % 3 == 1 else rs.uniform(200, 1200)))
              if i % 3 < 2 else ((-500 if i % 2 else 1600), rs.uniform(200, 1200)) for i in range(N4)]
    items = []
    for (x, y, i) in pos:
        tin = 5.45 + .05 * i
        fin = ease_out(clamp((t - tin) / .4), 3)
        sx_, sy_ = starts[i]
        x2, y2 = lerp(sx_, x, fin), lerp(sy_, y, fin)
        side = -1 if i % 2 == 0 else 1
        go = ease_io(clamp((t - (T4_TWO + .05 + .03 * i)) / .45))
        if go > 0:
            hx, hy = HILL_L if side < 0 else HILL_R
            j = i // 2
            tx = hx + 20 + (j - 2) * 85 + 18 * math.sin(t * 3 + i)
            ty = hy - 600 - 70 * (j % 2) + 10 * math.sin(t * 4 + i)
            x2, y2 = lerp(x2, tx, go), lerp(y2, ty, go) - 120 * math.sin(math.pi * go)
        col = "#FFFFFF" if split < .5 else (P.BUB_YELLOW if side < 0 else P.BUB_BLUE)
        icon = "waves" if split < .5 else ("arrow_up" if side < 0 else "yarn")
        k = .42 * (1 - .3 * go)
        wb = .5 * math.sin(t * 9 + i * 1.7)
        items.append((y2, P.comment_bubble(x2, y2, k * (.85 + .2 * ((i * 7) % 5) / 4), icon, 1.0, wb, 40 + i, (-40 if i % 2 else 40, 45), col)))
    for _, s_ in sorted(items, key=lambda q: q[0]):
        o.append(s_)
    o.append(P.split_flash(SW4[0], SW4[1] - 330, SW4[1] + 330, clamp((t - T4_SP + .02) / .38), seed=4, w=80))
    if T4_SP - .02 < t < T4_SP + .08:
        o.append(P.flash_screen(.35 * (1 - abs(t - T4_SP - .03) / .05)))
    # камера: тесно на рое → отъезд на «два», удар
    s = lerp(1.42, 1.48, clamp((t - 5.42) / 1.0))
    cy = SW4[1] + 20
    z = ease_out(clamp((t - T4_TWO + .04) / .32), 3)
    s = lerp(s, 1.1, z)
    cy = lerp(cy, 930, z)
    cx = lerp(540, 575, z) + 10 * math.sin(t * 1.3)
    if t > T4_TWO:
        s *= 1 + .05 * math.exp(-8 * (t - T4_TWO)) * math.cos(18 * (t - T4_TWO))
    dx, dy = P.shake(t, T4_SP, 18, .3, seed=41)
    ex, ey = P.shake(t, T4_TWO, 10, .25, seed=42)
    wx, wr = whip_in(t, 5.42)
    return frame_svg("".join(o), cx - dx - ex - wx, cy - dy - ey, s, wr + .6 * math.sin(t * 1.7), P.C_PAGE)


# ═══════════════════════════════ s05: жёлтый лагерь, пулемёт пузырей ═══════════════════════════════
T5_ODNI = wt("одни")              # 7.63
T5_PISH = wt("пишут", 7.9)       # 8.13
T5_PROS = wt("просто", 8.4)       # 8.59
T5_VST = wt("встаёшь")            # 8.84
TENT5 = (500.0, 1240.0, 1.42)


def s05(t):
    lib.dyn_begin()
    o = [paper_bg()]
    o.append(shape([(-600, 1300, 1), (-600, 1238), (1700, 1238), (1700, 1300, 1)], "#BFD79A", "", w=0, seed=5003, ink=False))
    o.append(line([(-600, 1240), (1700, 1242)], 5, INK, taper=.05, wmin=.8, seed=5001))
    for j in range(9):
        gx = -40 + 140 * j
        o.append(line([(gx, 1250), (gx + 8, 1222)], 3, "#6E9150", seed=5010 + j))
    tx, ty, tk = TENT5
    hop = P.hop(t, T5_ODNI, 120, .34)
    bsq = P.squash(t, T5_ODNI + .34, .2, 3, 7)
    bounce = 1 - bsq[1]
    if t < T5_ODNI:
        bounce = -.03 * math.sin(t * 9)          # дрожит от нетерпения с первого кадра
    open_ = ease_out(clamp((t - T5_ODNI - .08) / .28), 2)
    o.append(f'<g transform="translate(0 {hop:.1f})">' + P.camp_tent(tx, ty, tk, "yellow", "bolt", open_, bounce, t, seed=5, wave=1.6) + "</g>")
    dx_, dy_ = P.tent_door(tx, ty, tk, bounce)
    dy_ += hop
    # пулемёт пузырей со стрелкой
    shots = []
    if t >= T5_PISH - .05:
        n = int((min(t, T5_PROS + .1) - (T5_PISH - .05)) / .07) + 1
        for i in range(n):
            t0 = T5_PISH - .05 + i * .07
            u = (t - t0) / .75
            if u <= 0 or u >= 1:
                continue
            ang = math.radians(-90 + (-38 if i % 3 == 0 else (30 if i % 3 == 1 else -6)) + 7 * math.sin(i * 2.1))
            dist = 1150 * ease_out(u, 2)
            x = dx_ + dist * math.cos(ang)
            y = dy_ - 60 + dist * math.sin(ang) + 260 * u * u
            sc = .52 * min(1.0, u / .12)
            shots.append(P.comment_bubble(x, y, sc, "arrow_up", 1.0, .6 * math.sin(t * 14 + i), 50 + i, (30, 40), P.BUB_YELLOW))
    o += shots
    # большой пузырь: надувается у входа и летит в камеру
    big = ""
    if t >= T5_PROS:
        inf = ease_out(clamp((t - T5_PROS) / (T5_VST - T5_PROS)), 2)
        fly = ease_in(clamp((t - T5_VST) / .5), 2.4)
        k = .2 + .5 * inf + 9.0 * fly
        bx = lerp(dx_ + 40, 560, fly)
        by = lerp(dy_ - 170 * inf, 900, fly)
        wb = .7 * math.sin((t - T5_PROS) * 16) * (1 - fly)
        b = P.comment_bubble(bx, by, k, "arrow_up", 1.0, wb, 59, (40, 40), P.BUB_YELLOW)
        if fly > .25:
            b = f'<g {lib.blur(round(2 + 18 * fly))}>{b}</g>'
        big = b
    o.append(big)
    # камера: наезд на палатку
    a = ease_io(clamp((t - 7.35) / 1.9))
    s = lerp(1.0, 1.16, a)
    cx, cy = lerp(520, 500, a), lerp(860, 900, a)
    fly = clamp((t - T5_VST) / .5)
    s *= 1 + .12 * ease_in(fly, 2)
    ex, ey = P.shake(t, T5_ODNI + .34, 14, .3, seed=51)
    fx, fy = P.shake(t, T5_VST, 8, .4, seed=52)
    return frame_svg("".join(o), cx - ex - fx, cy - ey - fy, s, -.8 * a, P.C_PAGE)


# ═══════════════════════════════ s07: синий лагерь, пузыри в ряд ═══════════════════════════════
T7_DR = wt("другие")              # 10.72
T7_PISH = wt("пишут", 11.0)      # 11.57
T7_ROW = [wt("я", 11.8), wt("тоже"), wt("так", 12.2), wt("не", 12.4), wt("могу")]     # 11.96 12.06 12.36 12.51 12.62
TENT7 = (250.0, 1180.0, 1.15)
ROW7 = [(560.0 + 165 * i, 1080.0) for i in range(5)]
BK7 = .74


def s07(t):
    lib.dyn_begin()
    o = [paper_bg("#FBF0DA", "#E3D9CB")]
    o.append(shape([(-600, 1300, 1), (-600, 1178), (1700, 1178), (1700, 1300, 1)], "#C6DCA4", "", w=0, seed=7003, ink=False))
    o.append(line([(-600, 1180), (1700, 1182)], 5, INK, taper=.05, wmin=.8, seed=7001))
    for j in range(9):
        gx = -40 + 140 * j
        o.append(line([(gx, 1190), (gx + 8, 1162)], 3, "#6E9150", seed=7010 + j))
    tx, ty, tk = TENT7
    open_ = .5 * ease_io(clamp((t - T7_DR) / .7))
    breath = .02 * math.sin(t * 2.4)
    o.append(P.camp_tent(tx, ty, tk, "blue", "yarn", open_, breath, t, seed=7, wave=.9))
    dx_, dy_ = P.tent_door(tx, ty, tk, breath)
    # пузыри: выплывают по одному, покачиваются, садятся в ряд и кивают
    rel = [T7_DR + .2 + .3 * i for i in range(5)]
    for i in range(5):
        if t < rel[i]:
            continue
        u = t - rel[i]
        # плавание: медленно вверх и вбок от входа
        fx = dx_ + 40 + 120 * ease_out(clamp(u / 1.4), 2) + 60 * i * clamp(u / 1.4)
        fy = dy_ - 60 - 420 * ease_out(clamp(u / 1.4), 2) + 30 * math.sin(u * 2.6 + i)
        rx, ry = ROW7[i]
        land = ease_io(clamp((t - T7_ROW[i] + .18) / .3))
        x = lerp(fx, rx, land)
        y = lerp(fy, ry, land) - 80 * math.sin(math.pi * land)
        nod = 0.0
        for w0 in T7_ROW[i:]:
            nod += P.hop(t, w0, 22, .2)
        if land >= 1:
            y += nod
        sc = .38 + .26 * ease_out(clamp(u / .5), 2)
        if land > 0:
            sc = lerp(sc, BK7, land)
        sq = P.squash(t, T7_ROW[i] + .12, .22, 3, 7)
        wb = (.35 * math.sin(u * 3.0 + i) if land < 1 else (sq[1] - 1) * -3) + (.25 * math.sin((t - T7_PISH) * 6) if t > T7_PISH and land < 1 else 0)
        o.append(P.comment_bubble(x, y, sc, "yarn", 1.0, wb, 70 + i, (-35, 40), P.BUB_BLUE))
    # камера: медленный тёплый дрейф вдоль ряда
    a = ease_io(clamp((t - 10.46) / 2.66))
    cx, cy, s = lerp(500, 800, a), lerp(940, 960, a), lerp(1.2, 1.26, a)
    wx, wr = whip_in(t, 10.46)
    return frame_svg("".join(o), cx - wx, cy, s, wr + .5 * math.sin(t * 1.1), "#FBF0DA")


SHOTS = {"s02": s02, "s04": s04, "s05": s05, "s07": s07}


def frame(sid, t):
    return SHOTS[sid](t)
