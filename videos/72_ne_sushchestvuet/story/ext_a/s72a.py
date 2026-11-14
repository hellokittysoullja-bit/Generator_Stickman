"""Рилс 72 «СДВГ не существует», группа A: графика на бумаге (шарик-мозг, моторчик, мозг-малыш, башня-диплом).
s02 (1.42–2.38): шарик-мозг качается на ниточке над листом; лапа кота входит справа и на ударном «сту» (≈1.70) тычет когтем —
    шарик лопается клочьями, ниточка падает, штрихи хлопка. Камера: лёгкий наезд, тряска и отскок на хлопке.
s12 (14.50–16.90, whip): Дима на траве дёргает тросик садового моторчика. «хватает» (15.24) рывок — мотор чихает; «сил» (15.76)
    рывок изо всех сил — мотор трясётся и почти заводится; «начать» (16.08) глохнет жалким пуфом, Дима плюхается на траву с ручкой.
s13 (16.90–18.10, whip): мозг-малыш выглядывает из-за края листа на «Мозг» (17.08); «видит» (17.72) глаза-блюдца, извилины дыбом,
    смотрит вверх; сверху наползает тень.
s14 (18.10–19.06): ракурс снизу: над крошечным мозгом нависает башня-диплом с лентой, камера задирается вверх вдоль башни;
    «написать диплом» (18.16–18.96) башня клонится к мозгу и качается, листы шуршат, тень накрывает мозг.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Предметы — common/props.py, люди и кот — common/people.py."""
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
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, svg  # noqa: E402

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
    d = "".join(f"M-1400 {i * 64}H2600" for i in range(-24, 50)) + "".join(f"M{i * 64} -1600V3000" for i in range(-24, 42))
    return (f'<path d="M-1400 -1600H2600V3000H-1400Z" fill="{col or P.C_PAGE}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def darken(svg_, u):
    """Тень на фигуре: фильтр яркости (фигура остаётся сплошной)."""
    if u <= 0.01:
        return svg_
    k = 1 - .42 * clamp(u)
    fid = f"dk{int(k * 1000)}"
    if not any(f'id="{fid}"' in x for x in lib.DEFS):
        lib.DEFS.append(f'<filter id="{fid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="{k} 0 0 0 0 0 {k} 0 0 0 0 0 '
                        f'{k * 1.05:.3f} 0 0 0 0 0 1 0"/></filter>')
    return f'<g filter="url(#{fid})">{svg_}</g>'


def whip_in(t, t0, dur=.2, amp=-170.0):
    u = clamp((t - t0) / dur)
    e = 1 - ease_out(u, 3)
    return amp * e, -2.2 * e * (1 if amp < 0 else -1)


def motion_lines(x, y, u, ang, n=3, L=120.0, gap=40.0, seed=0, w=6.0):
    if u <= .01:
        return ""
    a = math.radians(ang)
    nx, ny = -math.sin(a), math.cos(a)
    o = []
    for j in range(n):
        off = (j - (n - 1) / 2) * gap
        p0 = (x + nx * off, y + ny * off)
        p1 = (p0[0] + math.cos(a) * L * u, p0[1] + math.sin(a) * L * u)
        o.append(line([p0, p1], w, INK, taper=.7, wmin=.1, seed=seed + j, op=.85))
    return "".join(o)


# ═══════════════════════════════ s02: шарик-мозг лопается от лапы ═══════════════════════════════
T2_POP = 1.70                   # ударный «сту» в «существует» (1.43–2.16)
T2_IN = 1.40                    # лапа начинает входить
BAL = (540.0, 640.0)
BAL_K = 2.7


def s02(t):
    lib.dyn_begin()
    o = [paper_bg()]
    # ниточка привязана к колышку внизу листа (виден узелок) — шарик натягивает её и качается
    sway = 26 * math.sin(t * 3.1 + .6) + 10 * math.sin(t * 5.3)
    bob = 14 * math.sin(t * 4.2)
    bx, by = BAL[0] + sway, BAL[1] + bob
    pop = clamp((t - T2_POP) / .85)
    # лапа: из-за правого края, к шарику; на ударе — тычок и отдёргивание
    k = 1.8
    if t < T2_POP:
        u = ease_out((t - T2_IN) / (T2_POP - T2_IN), 2)
        tip = (lerp(1300, bx + 235, u), lerp(1000, by + 80, u))
        claw = clamp((t - T2_POP + .14) / .1)
    else:
        v = t - T2_POP
        back = ease_out(clamp((v - .06) / .35), 2)
        tip = (bx + 235 - 50 * math.sin(math.pi * clamp(v / .1)) + 120 * back + 600 * ease_in(clamp((v - .45) / .4), 2),
               by + 80 + 60 * back + 380 * ease_in(clamp((v - .45) / .4), 2))
        claw = 1 - clamp((v - .3) / .2)
    tip = (tip[0], tip[1])
    base = (tip[0] + 520, tip[1] + 330)
    # тень шарика на листе
    if pop <= 0:
        o.append(blob(ellipse_pts(bx + 30, 1250, 150, 20, 14), "#000000", .08))
    o.append(P.brain_balloon(bx, by, BAL_K, t, pop, string=200))
    if 0 < pop < .3:
        o.append(P.sparkles(bx, by, 3.0, 1 - pop / .3, t, seed=5, n=5, r=230))
    o.append(people.cat_forearm(base, tip, k, claw, seed=3))
    if T2_IN < t < T2_POP:
        o.append(motion_lines(tip[0] + 80, tip[1] + 80, clamp((t - T2_IN) / .15) * (1 - clamp((t - T2_POP + .05) / .1)), 30, n=3, L=160, seed=2050))
    # камера: лёгкий наезд, тряска и отскок на хлопке
    a = max(0.0, t - 1.22)
    s = 1.0 + .06 * ease_io(a / 1.2)
    sh = P.shake(t, T2_POP, 22, .3, seed=2)
    kick = .05 * math.exp(-max(0, t - T2_POP) * 9) * (t >= T2_POP)
    return frame_svg("".join(o), 540 + sh[0], 860 + sh[1], s + kick, .9 * math.sin(t * 1.3), P.C_PAGE)


# ═══════════════════════════════ s12: моторчик не заводится ═══════════════════════════════
T12_A = wt("хватает")      # 15.24
T12_B = wt("сил")          # 15.76
T12_C = wt("начать")       # 16.08
GROUND12 = 1250.0
ENG = (660.0, GROUND12)
ENG_K = 1.25
D12 = (240.0, GROUND12 - (people.LEG_LEN - 12) * .7)
S12 = .7


def _grass(x0, x1, y, t, seed=0):
    rs = P._rs(12000 + seed)
    o = [f'<path d="M{x0} {y}L{x1} {y}L{x1} {y + 900}L{x0} {y + 900}Z" fill="#8FC27A"/>',
         f'<path d="M{x0} {y + 40}L{x1} {y + 40}L{x1} {y + 900}L{x0} {y + 900}Z" fill="#7DB068"/>']
    o.append(line([(x0, y), (x1, y + 4)], 5, INK, taper=.05, wmin=.8, seed=12050 + seed))
    xx = x0
    while xx < x1:
        h = rs.uniform(20, 44)
        sw = 5 * math.sin(t * 2 + xx * .01)
        o.append(line([(xx, y + 6), (xx + 6 + sw, y - h), (xx + 14, y + 6)], 3.4, "#4E8A3E", taper=.4, wmin=.3, seed=int(xx) + seed))
        xx += rs.uniform(40, 80)
    return "".join(o)


def _cord_u(t):
    """Сколько вытянут тросик (0.15 — рука у шкива)."""
    if t < T12_A - .05:
        return .42 + .05 * math.sin(t * 6)          # примеряется, чуть подёргивает
    if t < T12_A + .14:
        return lerp(.44, .95, ease_out((t - T12_A + .05) / .19, 3))
    if t < T12_B - .1:
        return lerp(.95, .44, ease_io((t - T12_A - .14) / (T12_B - .1 - T12_A - .14)))
    if t < T12_B + .12:
        return lerp(.44, 1.08, ease_out((t - T12_B + .1) / .22, 3))
    return 1.08


def s12(t):
    lib.dyn_begin()
    o = [paper_bg()]
    o.append(_grass(-1200, 2400, GROUND12, t))
    cord = _cord_u(t)
    plop = ease_in(clamp((t - T12_C - .04) / .26), 2)        # падает на траву
    land = clamp((t - T12_C - .3) / .3)
    # мотор: кашель на первом рывке, тряска и пыхтение на втором, жалкий пуф на «начать»
    shake = 0.0
    cough = -1.0
    if T12_A + .05 < t < T12_A + .6:
        shake = .6 * (1 - (t - T12_A - .05) / .55)
        cough = (t - T12_A - .05) / .55
    if T12_B + .05 < t < T12_C + .05:
        shake = 1.3
        cough = ((t - T12_B - .05) / .16) % 1
    o.append(P.blob(ellipse_pts(ENG[0], ENG[1] + 4, 200, 18, 14), "#000000", .12) if hasattr(P, "blob") else "")
    # Дима: стойка → откидывается при рывке → плюхается на траву
    lean_pull = .32 - .5 * clamp((cord - .44) / .56)
    hip0 = D12
    hipx = hip0[0] - 40 * clamp((cord - .44) / .56) - 90 * plop
    hipy = lerp(hip0[1], GROUND12 - 40, plop)
    stand = people.stand_kw(hipx, hipy, S12)["feet"]
    sitf = people.plop_kw(hipx, hipy, S12)["feet"]
    feet = {}
    for sd in ("n", "f"):
        (a0, p0), (a1, p1) = stand[sd], sitf[sd]
        if plop <= 0:
            feet[sd] = ((a0[0], GROUND12 if sd == "n" else GROUND12 + 4), p0)
        else:
            feet[sd] = ((lerp(a0[0], a1[0], plop), lerp(GROUND12, a1[1], plop)), lerp(p0, p1, plop))
    # ручка: пока стоит — в точке тросика; после падения — в руке (рука опускается на колено)
    hx, hy = P.engine_handle(ENG[0], ENG[1], ENG_K, min(1.0, cord))
    if cord > 1.0:
        hx -= (cord - 1) * 120
        hy -= (cord - 1) * 40
    if plop > 0:
        rest = (hipx + 230 * S12, hipy - 120 * S12)
        hx, hy = lerp(hx, rest[0], ease_io(plop)), lerp(hy, rest[1], ease_io(plop))
    if t < T12_A - .05:
        ex = "resolve" if t > 14.7 else "hope"
    elif t < T12_B - .1:
        ex = "strain" if t < T12_A + .3 else "hope"
    elif t < T12_C:
        ex = "strain"
    else:
        ex = "surprise" if land < .5 else "sink"
    exd = dict(people.EXPR["dima"][ex])
    exd["bags"] = False
    if ex in ("hope", "resolve", "surprise", "sink"):
        exd["look"] = (.75, .45)
    fig = people.dima(hipx, hipy, S12, exd, "pull_cord", lean_add=lean_pull + .12 * plop * (1 - land) - .05 * land,
                      arms={"n": ("ik", (hx, hy), 1)}, feet=feet,
                      hands={"n": {"dir": (-.6, -.8), "curl": (.75, .78, .8, .8), "thumb": .7}})
    # дальняя рука на раме мотора, пока стоит; при падении — машет
    o.append(P.pull_engine(ENG[0], ENG[1], ENG_K, cough=cough if cough >= 0 else 0, shake=shake, cord=min(1.0, cord), t=t,
                           handle=(hx, hy), hand_ang=-148 + 40 * plop))
    o.append(fig["svg"])
    if ex == "strain":
        o.append(people.strain_marks(fig["head"], S12, t, 1.0))
    # пыхтение «почти заводится»: три клубка подряд + штрихи тряски
    if T12_B + .05 < t < T12_C + .05:
        for j in range(3):
            c = ((t - T12_B - .05) / .18 - j * .33) % 1
            o.append(P.puff_cloud(ENG[0] + 300 + 60 * j * ENG_K, ENG[1] - 200 * ENG_K - 80 * c, 1.0, c, seed=j + 3, col="#BFC4CC"))
        for sx in (-1, 1):
            o.append(line([(ENG[0] + sx * 260, ENG[1] - 220), (ENG[0] + sx * 285, ENG[1] - 180)], 6, INK, taper=.6, wmin=.1, seed=12100 + sx))
            o.append(line([(ENG[0] + sx * 275, ENG[1] - 140), (ENG[0] + sx * 300, ENG[1] - 100)], 6, INK, taper=.6, wmin=.1, seed=12110 + sx))
    # жалкий пуф на «начать»: один маленький клубок, падает вниз
    pf = (t - T12_C - .05) / .9
    if 0 < pf < 1:
        o.append(P.puff_cloud(ENG[0] + 290, ENG[1] - 190 * ENG_K + 60 * pf, .8, pf, seed=9, col="#9AA0AA"))
    if T12_C + .15 < t:
        # «пиу» — повисшая струйка дыма из выхлопа
        o.append(P.smoke_curls(ENG[0] + 270, ENG[1] - 172 * ENG_K, .9, clamp((t - T12_C - .15) / .4), t, seed=5, n=1, col="#BFC4CC"))
    # удар о траву: штрихи и комья
    if plop >= 1 and land < 1:
        for j in range(5):
            a = math.radians(-160 + 35 * j)
            r0 = 120 + 160 * land
            cx, cy = hipx, GROUND12 - 10
            o.append(line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0 * .5), (cx + math.cos(a) * (r0 + 50), cy + math.sin(a) * (r0 + 50) * .5)], 6 * (1 - land),
                          INK, taper=.6, wmin=.1, seed=12200 + j))
    # камера: хлёст, тряска на рывках, на «начать» проседает с Димой
    wx, wr = whip_in(t, 14.30, .22)
    sh = P.shake(t, T12_A + .05, 12, .3, seed=4)
    sh2 = P.shake(t, T12_B + .05, 18, .45, seed=6)
    sh3 = P.shake(t, T12_C + .3, 14, .3, seed=8)
    cy = 900 + 90 * ease_io(clamp((t - T12_C) / .5))
    s = 1.12 + .05 * ease_io(clamp((t - 14.5) / 1.4)) + .04 * ease_out(clamp((t - T12_B) / .2)) * (1 - plop)
    return frame_svg("".join(o), 470 + wx + sh[0] + sh2[0] + sh3[0], cy + sh[1] + sh2[1] + sh3[1], s, wr + .6 * math.sin(t * 1.1), P.C_PAGE)


# ═══════════════════════════════ s13: мозг выглядывает ═══════════════════════════════
T13_M = wt("мозг")         # 17.08
T13_V = wt("видит")        # 17.72
BK = (540.0, 1180.0)
BK_K = 2.1
EDGE13 = 1030.0


def _sheet_front(t, y, seed=0):
    """Передний лист бумаги (край по y, чуть волнистый, загнутый уголок справа), закрывает низ кадра."""
    wv = 6 * math.sin(t * 2.2)
    pts = [(-900, y + 10, 1), (100, y - 4 + wv), (700, y + 6), (1080, y - 6 + wv * .6), (1300, y + 30), (1600, y + 40, 1), (1600, 3000, 1), (-900, 3000, 1)]
    lines = "".join(line([(-900, y + 90 + 64 * j), (1600, y + 92 + 64 * j)], 2, "#D9DCD6", taper=.02, wmin=.9, seed=13000 + j) for j in range(14))
    o = blob([(p[0], p[1] - 14) for p in pts[:6]] + [(1600, y + 60), (-900, y + 60)], "#000000", .1)
    o += lib.shape(pts, "#FDF7E4", lines, w=5, seed=13050 + seed)
    o += lib.shape([(1050, y - 4, 1), (1180, y + 120, 1), (1240, y + 26, 1)], P.C_PAGE_SH, "", w=4, seed=13060)
    return o


def s13(t):
    lib.dyn_begin()
    o = [paper_bg()]
    # тень сверху наползает к концу (то, что мозг увидел)
    shd = ease_in(clamp((t - T13_V - .05) / .35), 2)
    peek = ease_out(clamp((t - T13_M + .2) / .45), 3)          # всплывает из-за края
    pre = .1 * (0.5 + .5 * math.sin(t * 9)) * (1 - peek)        # до «Мозг» — макушка подрагивает у края
    rise = lerp(330, 0, max(peek, pre))
    hop = P.hop(t, T13_V, 40, .3)
    ex = "peek" if t < T13_V else "wide"
    look = (.4 * math.sin(t * 2), 0) if t < T13_V else (0, -1)
    blink = 1.0 if abs(t - (T13_M + .38)) < .05 else 0.0
    sq = P.squash(t, T13_V, .12, 3.5, 8)
    body = P.brain_kid(0, 0, 1.0, ex, hop / BK_K, t, look=look, seed=1, blink=blink)
    o.append(f'<g transform="translate({BK[0]:.1f} {BK[1] + rise:.1f}) scale({BK_K * sq[0]:.4f} {BK_K * sq[1]:.4f})">{body}</g>')
    # штрихи испуга на «видит»
    if t > T13_V:
        u = clamp((t - T13_V) / .25)
        for sx in (-1, 1):
            for j in range(3):
                a = math.radians(-90 + sx * (35 + 22 * j))
                cx, cy = BK[0], BK[1] + rise - 330
                r0 = 300 + 30 * u
                o.append(line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + 70 * u), cy + math.sin(a) * (r0 + 70 * u))], 7,
                              INK, taper=.6, wmin=.1, seed=13100 + j + sx * 5))
    o.append(_sheet_front(t, EDGE13))
    # тень башни сверху: тёмный клин сползает по листу
    if shd > 0:
        yb = -400 + 900 * shd
        o.append(blob([(-900, -1600), (2000, -1600), (2000, yb - 200), (900, yb), (200, yb + 60), (-900, yb - 80)], "#1C2030", .28 * shd))
    # камера: резкая смена (хлёст), лёгкий наезд на глаза
    wx, wr = whip_in(t, 16.70, .2, amp=170)
    s = 1.0 + .12 * ease_io(clamp((t - 16.9) / 1.2)) + .06 * ease_out(clamp((t - T13_V) / .15)) * (1 - .5 * clamp((t - T13_V - .3) / .4))
    cy = lerp(860, 800, ease_io(clamp((t - 16.9) / 1.2)))
    sh = P.shake(t, T13_V, 8, .25, seed=3)
    return frame_svg("".join(o), 540 + wx + sh[0], cy + sh[1], s, wr, P.C_PAGE)


# ═══════════════════════════════ s14: башня-диплом нависает ═══════════════════════════════
T14_W = wt("написать")     # 18.16
T14_D = wt("диплом")       # 18.60
G14 = 1240.0
TW = (640.0, G14)
TW_K = 2.0
TW_N = 64
BK14 = (330.0, G14)
BK14_K = .62


def s14(t):
    lib.dyn_begin()
    o = [paper_bg()]
    o.append(line([(-1400, G14 + 4), (400, G14), (2600, G14 + 4)], 5, INK, taper=.03, wmin=.8, seed=14001))
    # наклон: на «написать» клонится к мозгу (влево), на «диплом» — ещё ниже и качается
    l1 = -6 * ease_out(clamp((t - T14_W) / .3), 2)
    l2 = -5 * ease_out(clamp((t - T14_D) / .25), 2)
    wob = 2.2 * math.sin((t - 17.9) * 7) * math.exp(-max(0, t - T14_D) * 1.5)
    lean = l1 + l2 + wob - .8
    fl = .6 + .4 * clamp((t - T14_W) / .3)
    # тень башни накрывает мозг
    shd = clamp(.35 + .65 * ease_out(clamp((t - T14_W) / .5)))
    o.append(blob([(TW[0] + 120, G14 + 2), (TW[0] - 520 - 280 * shd, G14 + 2), (TW[0] - 600 - 300 * shd, G14 + 70), (TW[0] + 200, G14 + 70)], "#1C2030", .22))
    o.append(P.paper_tower(TW[0], TW[1], TW_K, lean=lean, flutter=fl, t=t, n=TW_N, seed=4, taper=.42))
    # шуршание: штрихи у верха
    top = P.paper_tower_top(TW[0], TW[1], TW_K, lean, TW_N)
    for j in range(3):
        ph = (t * 3 + j / 3) % 1
        o.append(line([(top[0] - 200 + 150 * j, top[1] - 40 - 60 * ph), (top[0] - 170 + 150 * j, top[1] - 80 - 60 * ph)], 7 * (1 - ph), INK, taper=.6,
                      wmin=.1, seed=14100 + j))
    # мозг: дрожит, глаза вверх, извилины дыбом
    trem = 3 * math.sin(t * 50)
    bk = P.brain_kid(BK14[0] + trem, BK14[1], BK14_K, "scared", 0, t, look=(.3, -1), seed=2)
    o.append(darken(bk, .55 * shd))
    o.append(P.sweat(BK14[0] + 110 * BK14_K * 1.4, BK14[1] - 260 * BK14_K + 30 * ((t * 1.5) % 1), 1.0))
    # камера: резко задирается снизу вверх вдоль башни, потом медленно давит
    u = ease_out(clamp((t - 17.95) / .4), 3)
    cy = lerp(1060, 520, u) - 30 * ease_io(clamp((t - T14_D) / .5))
    cx = lerp(420, 560, u)
    s = lerp(1.25, .8, u) + .03 * ease_io(clamp((t - T14_D) / .5))
    rot = lerp(-3, 2.5, u) + .8 * math.sin(t * 2)
    return frame_svg("".join(o), cx, cy, s, rot, P.C_PAGE)


SCENES = {"s02": s02, "s12": s12, "s13": s13, "s14": s14}


def frame(sid, t):
    return SCENES[sid](t)
