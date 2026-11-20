"""Рилс 95 «Тир-лист: как перестать откладывать», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Главный образ: доска тир-листа с цветными полками S (золото), A (зелёная), B (голубая), C (жёлтая), D (красная). Кот в очках
судьи раскладывает карточки-картинки без букв: кулак, календарь с красным днём, свиток до пола, помидор-таймер, стрелка-развилка,
двое за столом, сияющие песочные часы. Каждая карточка: показ крупно со сценкой Димы, потом бросок на полку с грохотом.
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука белым на чёрном."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(1, os.path.join(REPO, "scripts"))
import big_title  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import cat as CT  # noqa: E402
import props as PR  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    return W(i) + (WE(i) - W(i)) * u


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up=.08, down=.3):
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.35, f=11.0):
    u = t - a
    if u <= 0 or u > dur * 3:
        return 0.0, 0.0
    e = math.exp(-u / dur * 2.5)
    return amp * e * math.sin(2 * math.pi * f * u), amp * .6 * e * math.cos(2 * math.pi * f * .8 * u)


def pop(t, a, d=.24):
    u = clamp((t - a) / d)
    return lib.back_out(u, 2.2) if u < 1 else 1.0


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def tf(inner, x, y, k=1.0, rot=0.0):
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{inner}</g>'


def title(t):
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


def view(body, cx, cy, s, rot=0.0, over="", bg="#e9dcc4"):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


# ═════════════════════════ зал ═════════════════════════
FLOOR = 1420.0


def hall(t, x0=-900.0, x1=2000.0, top=-1600.0, dim=0.0):
    o = [rect(x0, top, x1, FLOOR, lib.mix("#eadcc2", "#7d7266", dim)),
         rect(x0, FLOOR, x1, FLOOR + 1400, lib.mix("#d6c19c", "#6e604e", dim))]
    o.append(line([(x0, FLOOR), (x1, FLOOR)], 5, seed=11))
    for i in range(-3, 9):                       # доски пола
        xa = 540 + i * 260
        o.append(line([(xa, FLOOR + 30), (540 + (xa - 540) * 2.2, FLOOR + 900)], 2.4, "#b59f78", seed=20 + i, op=.8))
    for i, (x, r) in enumerate(((130, 260), (950, 260))):      # прожекторы зала (медленно дышат)
        o.append(PR.glow(x, -60, r * 2.2, .35 + .1 * math.sin(t * 1.3 + i * 2), "#fff3cf", ry=r * 4))
    return "".join(o)


# ═════════════════════════ доска тир-листа ═════════════════════════
BX0, BX1 = 70.0, 1010.0
BY0, RH = 250.0, 170.0
LW = 170.0                                       # ширина плашки ранга
RANKS = [("S", "#f2bd22"), ("A", "#62c25a"), ("B", "#5ab3ea"), ("C", "#f2d84a"), ("D", "#e5483c")]
RANK_I = {r: i for i, (r, _) in enumerate(RANKS)}
BY1 = BY0 + RH * len(RANKS)


def row_y(r):
    return BY0 + RH * RANK_I[r]


def slot(r, j):
    """Точка карточки на полке: (x центра, y низа = верх бортика)."""
    return BX0 + LW + 150 + j * 150, row_y(r) + RH - 18


_BOARD = {}


def board_static():
    if "b" in _BOARD:
        return _BOARD["b"]
    o = []
    fr = lib.rrect(BX0 - 30, BY0 - 30, BX1 + 30, BY1 + 30, 14)
    o.append(shape(fr, "#a97a4c", blob(lib.rrect(BX0 - 30, BY1 - 4, BX1 + 30, BY1 + 30, 10), "#8a6038", .8), w=6, seed=31))
    for i, (r, c) in enumerate(RANKS):
        y0 = BY0 + RH * i
        o.append(rect(BX0 + LW, y0, BX1, y0 + RH, lib.mix(c, "#fbf5e6", .74)))
        o.append(rect(BX0 + LW, y0, BX1, y0 + 26, lib.mix(c, "#fbf5e6", .6), .7))
        o.append(shape([(BX0, y0, 1), (BX0 + LW, y0, 1), (BX0 + LW, y0 + RH, 1), (BX0, y0 + RH, 1)], c,
                       blob([(BX0, y0 + RH * .62), (BX0 + LW, y0 + RH * .7), (BX0 + LW, y0 + RH), (BX0, y0 + RH)], lib.mul(c, (.86, .86, .86)), .7),
                       w=5, seed=40 + i))
        o.append(f'<text x="{BX0 + LW / 2:.1f}" y="{y0 + RH / 2 + 46:.1f}" font-family="IDB" font-size="128" text-anchor="middle" '
                 f'fill="#fffdf6" stroke="{INK}" stroke-width="11" stroke-linejoin="round" paint-order="stroke">{r}</text>')
        sh = [(BX0 + LW, y0 + RH - 20, 1), (BX1, y0 + RH - 20, 1), (BX1, y0 + RH, 1), (BX0 + LW, y0 + RH, 1)]       # бортик-полка
        o.append(shape(sh, "#c99a63", line([(BX0 + LW + 10, y0 + RH - 12), (BX1 - 10, y0 + RH - 12)], 2, "#a57643", seed=60 + i), w=4, seed=50 + i))
    o.append(shape(lib.rrect(BX0, BY0, BX1, BY1, 4), "none", "", w=6, seed=33))
    for x in (BX0 + 40, BX1 - 40):              # ножки-стойки
        o.append(shape([(x - 18, BY1 + 30, 1), (x + 18, BY1 + 30, 1), (x + 24, FLOOR + 8, 1), (x - 24, FLOOR + 8, 1)], "#8a6038", "", w=5, seed=int(x)))
    _BOARD["b"] = "".join(o)
    return _BOARD["b"]


def row_flash(r, u, col=None):
    if u <= .01:
        return ""
    y0 = row_y(r)
    c = col or dict(RANKS)[r]
    return rect(BX0, y0, BX1, y0 + RH, lib.mix(c, "#ffffff", .5), .55 * u) + PR.glow(BX0 + LW / 2, y0 + RH / 2, 220, u, c)


# ═════════════════════════ карточки (поле 200×240, центр 0, 0) ═════════════════════════
SKIN, SKIN_SH = "#f1c09a", "#d99a74"


def ic_fist(t, a=0.0):
    sq = 1 - .06 * a
    o = [shape([(-34, 70, 1), (34, 70, 1), (30, 104, 1), (-30, 104, 1)], "#4f6fa8", "", w=4, seed=101)]       # рукав
    body = [(-56, -30), (-58, 10), (-50, 52), (-20, 72), (30, 72), (54, 48), (60, 6), (54, -32)]
    o.append(shape([(x * sq, y) for x, y in body], SKIN, blob([(10, 20), (56, 0), (50, 60), (20, 70)], SKIN_SH, .6), w=5, seed=102))
    for i in range(4):                       # костяшки
        cx = -40 + i * 27
        pts = ellipse_pts(cx * sq, -34, 16, 20, 12)
        o.append(shape(pts, SKIN, blob(ellipse_pts(cx * sq + 4, -26, 10, 10, 8), SKIN_SH, .5), w=4.2, seed=110 + i))
    o.append(shape([(-60, -6), (-20, -12), (14, -4), (16, 12), (-22, 14), (-58, 20)], SKIN, blob([(-50, 8), (10, 6), (12, 14), (-50, 18)], SKIN_SH, .5),
                   w=4.4, seed=120))                                                  # большой палец
    for i in range(3):
        o.append(line([(-27 + i * 27, -20), (-27 + i * 27, 0)], 2.6, seed=130 + i))
    if a > .05:                              # дрожит от напряжения
        for s in (-1, 1):
            o.append(line([(s * 78, -40), (s * 92, -20), (s * 80, 0)], 3.2, seed=140 + s, op=a))
    return "".join(o)


def ic_calendar(t, red=0):
    o = [shape(lib.rrect(-76, -72, 76, 82, 8), "#fffdf8", "", w=5, seed=201)]
    o.append(shape(lib.rrect(-76, -72, 76, -34, 6), "#4d6a99", "", w=4, seed=202))
    for x in (-40, 40):
        o.append(shape(lib.rrect(x - 7, -88, x + 7, -58, 6), "#c9c3b8", "", w=3.4, seed=203 + x))
    for j in range(4):
        for i in range(5):
            x0, y0 = -70 + i * 28, -28 + j * 27
            c = "#e5483c" if j * 5 + i == red else "#f3eee3"
            o.append(rect(x0 + 2, y0 + 2, x0 + 26, y0 + 25, c))
    for j in range(5):
        o.append(line([(-70, -28 + j * 27), (70, -28 + j * 27)], 1.8, "#9a9284", seed=210 + j))
    for i in range(6):
        o.append(line([(-70 + i * 28, -28), (-70 + i * 28, 80)], 1.8, "#9a9284", seed=220 + i))
    return "".join(o)


def ic_scroll(t, L=0.0, k=1.0):
    """Свиток: рулон сверху, лента вниз на 120 + L (L — в единицах карточки: тянется за край карточки до пола)."""
    h = 120 + L
    o = []
    pts = [(-62, -60, 1), (62, -60, 1)]
    n = max(2, int(h / 40))
    for i in range(1, n + 1):
        y = -60 + h * i / n
        pts.append((62 + 5 * math.sin(i * 1.7 + t * 3), y))
    pts += [(-62 + 5 * math.sin(n * 1.3 + t * 3), -60 + h)]
    for i in range(n - 1, 0, -1):
        pts.append((-62 + 5 * math.sin(i * 1.3 + t * 3), -60 + h * i / n))
    inner = ""
    m = int((h - 20) / 17)
    for i in range(m):
        y = -44 + i * 17
        inner += line([(-46, y), (-46 + 12, y)], 3, "#8d8577", seed=300 + i) + line([(-26, y), (20 + 20 * math.sin(i * 2.1), y)], 3, "#b5ad9e", seed=330 + i)
    o.append(shape(pts, "#fbf1d6", inner, w=4.4, seed=301))
    o.append(shape(lib.rrect(-74, -84, 74, -52, 16), "#e9d6a8", line([(-60, -68), (60, -68)], 2, "#c4ad7a", seed=303), w=4.6, seed=302))
    return "".join(o)


def ic_timer(t, ring=0.0, wedge=None):
    return PR.tomato_timer(0, 8, .62, wedge=PR.WEDGE_25 if wedge is None else wedge, ring=ring, t=t, seed=4)


def ic_fork(t, u=1.0):
    g, gs = "#4fb050", "#3a8c3e"
    o = [shape([(-14, 90, 1), (14, 90, 1), (14, 6), (60, -40), (74, -26, 1), (86, -76, 1), (36, -64, 1), (50, -50), (0, -8), (-50, -50), (-36, -64, 1),
                (-86, -76, 1), (-74, -26, 1), (-60, -40), (-14, 6)], g, blob([(2, 90), (14, 90), (14, 6), (4, 0)], gs, .7), w=5, seed=401)]
    if u > .05:
        o.append(f'<circle cx="0" cy="0" r="{16 * u:.1f}" fill="#fff6c4" opacity="{.9 * u:.2f}"/>')
    return "".join(o)


def ic_two(t, nod=0.0):
    o = [shape([(-90, 40, 1), (90, 40, 1), (90, 56, 1), (-90, 56, 1)], "#b98a5a", "", w=4, seed=501)]
    for i, (x, c, s) in enumerate(((-44, "#4b5e86", 1.0), (46, "#3b4143", .92))):
        hy = -36 + 4 * math.sin(t * 5 + i * 2) * nod
        o.append(shape([(x - 34 * s, 40, 1), (x - 30 * s, 4), (x - 14 * s, -10), (x + 14 * s, -10), (x + 30 * s, 4), (x + 34 * s, 40, 1)], c, "", w=4.4,
                       seed=510 + i))
        o.append(shape(ellipse_pts(x, hy, 24 * s, 26 * s, 14), c, "", w=4.4, seed=520 + i))
        if i == 1:                          # силуэт с ушками — напарник
            for e in (-1, 1):
                o.append(shape([(x + e * 8, hy - 20), (x + e * 22, hy - 44, 1), (x + e * 24, hy - 14)], c, "", w=4, seed=530 + e))
    o.append(shape([(-30, 40, 1), (-6, 26, 1), (14, 40, 1)], "#eaeef2", "", w=3.4, seed=540))       # раскрытый лист
    return "".join(o)


def ic_hourglass(t, shine=1.0):
    o = [PR.glow(0, 0, 150, .7 * shine, "#ffe28a")]
    o.append(PR.hourglass(0, 0, .62, rot=0, flow=1.0, top=.7, t=t, seed=3))
    return "".join(o)


ICONS = {"fist": ic_fist, "cal": ic_calendar, "scroll": ic_scroll, "timer": ic_timer, "fork": ic_fork, "two": ic_two, "hour": ic_hourglass}


def card(kind, x, y, k, t, rot=0.0, glow=0.0, back=False, **kw):
    """Карточка, ЦЕНТР (x, y), 200×240·k."""
    o = []
    if glow > .01:
        o.append(PR.glow(0, 0, 230, glow, "#ffe06a"))
    o.append(blob(lib.rrect(-96, -112, 104, 128, 16), "#000", .18))
    edge = "#f6c33a" if glow > .3 else "#fffaf0"
    o.append(shape(lib.rrect(-100, -120, 100, 120, 16), edge, "", w=5, seed=601))
    if back:
        o.append(shape(lib.rrect(-86, -106, 86, 106, 10), "#6b5fa3", "".join(
            line([(-86 + i * 30, -106), (-86 + i * 30 + 60, 106)], 3, "#8a7fc0", seed=610 + i, op=.8) for i in range(6)), w=3.4, seed=602))
    else:
        o.append(shape(lib.rrect(-86, -106, 86, 106, 10), "#fffdf8", "", w=2.6, seed=603))
        o.append(ICONS[kind](t, **kw))
    return tf("".join(o), x, y, k, rot)


# ═════════════════════════ кот-судья в очках ═════════════════════════
CAT_X, CAT_K = 810.0, 1.2


def glasses(x, y, k, st, lift=0.0, shine=0.0):
    tilt = st.get("tilt", 0.0)
    o = []
    for ex in (836 - 44, 836 + 44):
        o.append(f'<circle cx="{ex}" cy="1070" r="46" fill="#cfe6f2" fill-opacity=".25" stroke="{INK}" stroke-width="10"/>')
        o.append(line([(ex - 22, 1050), (ex - 6, 1040)], 4, "#ffffff", seed=ex, op=.8))
    o.append(line([(836 - 4, 1064), (836, 1058), (836 + 4, 1064)], 6, seed=703))
    for s in (-1, 1):
        o.append(line([(836 + s * 86, 1064), (836 + s * 104, 1052)], 6, seed=704 + s))
    if shine > .01:
        o.append(PR.sparkles(836 + 70, 1030, .7, shine, 0, seed=8, n=2))
    sl = st.get("sy", 1.0)
    return (f'<g transform="translate({x:.2f} {y:.2f}) rotate({st.get("rot", 0.0):.2f}) scale({k:.4f}) translate(-836 -1306)">'
            f'<g transform="translate(0 {-(sl - 1) * 156 - lift:.2f}) rotate({tilt:.2f} 836 1150)">{"".join(o)}</g></g>')


def judge(x, y, k, t, st=None, lift=0.0, shine=0.0):
    st = dict(dict(look=(-.6, -.3), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t) + glasses(x, y, k, st, lift, shine)


def paw_tip(x, y, k, paw, paw_dx):
    fx = 836 + 25
    lx, ly = fx + paw_dx * paw * 1.6, 1306 - 150 * paw
    return x + (lx - 836) * k, y + (ly - 1306) * k


# ═════════════════════════ бросок ═════════════════════════
THROW = .42          # полёт карточки, с
WIND = .34           # замах


def throw_state(t, land, start, end, k0=1.0, k1=.62, spin=1.0):
    """(x, y, k, rot, phase): phase 'wind' — в лапе, 'fly', 'land' (на полке)."""
    ta = land - THROW
    if t >= land:
        return end[0], end[1], k1, 0.0, "land"
    if t >= ta:
        u = (t - ta) / THROW
        e = u * u * (1.2 - .2 * u)
        cx, cy = (start[0] + end[0]) / 2, min(start[1], end[1]) - 260
        x = (1 - e) ** 2 * start[0] + 2 * (1 - e) * e * cx + e * e * end[0]
        y = (1 - e) ** 2 * start[1] + 2 * (1 - e) * e * cy + e * e * end[1]
        return x, y, k0 + (k1 - k0) * e, -360 * spin * e, "fly"
    return start[0], start[1], k0, 0.0, "wind"


def trail(pts, col="#ffffff"):
    o = []
    for j in range(len(pts) - 1):
        o.append(line([pts[j], pts[j + 1]], 26 * (j + 1) / len(pts), col, seed=900 + j, op=.55 * (j + 1) / len(pts)))
    return "".join(o)


def impact(x, y, t, land, k=1.0, col="#ffffff"):
    u = t - land
    if u < 0 or u > .45:
        return ""
    o = [PR.dust_puff(x, y, 1.1 * k, clamp(u / .45), seed=5)]
    e = ease_out(clamp(u / .3))
    for i in range(9):
        a = math.radians(-180 + i * 22.5)
        r0, r1 = (70 + 120 * e) * k, (120 + 200 * e) * k
        o.append(line([(x + math.cos(a) * r0, y - 40 * k + math.sin(a) * r0 * .8), (x + math.cos(a) * r1, y - 40 * k + math.sin(a) * r1 * .8)],
                      9 * k * (1 - u / .45), INK, seed=950 + i, op=1 - u / .45))
    return "".join(o)


CARDS = [("fist", "D", 0, lambda: stress(13, .3)), ("cal", "D", 1, lambda: stress(21, .4)), ("scroll", "C", 0, lambda: W(41) + .3),
         ("timer", "B", 0, lambda: W(51) + .32), ("fork", "A", 0, lambda: W(63) + .36), ("two", "A", 1, lambda: stress(73, .3)),
         ("hour", "S", 1.6, lambda: W(81) + .04)]
LAND = {c[0]: c[3]() for c in CARDS}


def shelf_card(kind, r, j, t, land, extra=None):
    x, yb = slot(r, j)
    k = .6
    u = t - land
    sq = 1 + .25 * math.exp(-u / .08) * math.cos(u * 40) if u < .5 else 1.0
    y = yb - 120 * k
    if kind == "two":                       # у самой кромки S: чуть приподнята, наклонена вверх
        y -= 34
    rot = {"fist": -6, "cal": 5, "scroll": -3, "timer": 4, "fork": -2, "two": 8, "hour": 0}[kind]
    kw = dict(extra or {})
    if kind == "scroll":
        kw.setdefault("L", 200.0)
    if kind == "hour":
        kw.setdefault("shine", 1.0)
        k = .75
        y = yb - 120 * k
    return f'<g transform="translate({x:.1f} {yb:.1f}) scale({1 / sq:.4f} {sq:.4f}) translate({-x:.1f} {-yb:.1f})">' + \
        card(kind, x, y, k, t, rot, glow=1.0 if kind == "hour" else 0.0, **kw) + "</g>"


def board_scene(t, landed=(), throw=None, flash=None, cat_st=None, bshake=(0.0, 0.0), cat_lift=0.0, cat_shine=0.0, cat_x=CAT_X, dima=None,
                over=""):
    """Доска с уже лежащими карточками (landed — виды), бросок throw=(kind, land, t_extra kw), кот справа на полу, Дима."""
    o = [hall(t)]
    bdx, bdy = bshake
    bo = [board_static()]
    if flash:
        for r, u in flash:
            bo.append(row_flash(r, u))
    for kind, r, j, _ in CARDS:
        if kind in landed:
            bo.append(shelf_card(kind, r, j, t, -9.0))
    fly_svg = ""
    cst = dict(cat_st or {})
    if throw:
        kind, land = throw[0], throw[1]
        kw = throw[2] if len(throw) > 2 else {}
        r, j = [(c[1], c[2]) for c in CARDS if c[0] == kind][0]
        sx, sy = slot(r, j)
        ta = land - THROW
        wind = ease_io(ramp(t, ta - WIND - .25, WIND))
        fl = ease_out(ramp(t, ta - .06, .14))
        cst.setdefault("paw", max(.25, .95 * wind * (1 - .3 * fl)) if t < land + .3 else .3 + .5 * (1 - ramp(t, land + .3, .4)))
        cst.setdefault("paw_dx", 95 - 170 * fl)
        cst.setdefault("tilt", 10 * wind - 18 * fl * (1 - ramp(t, land, .5)))
        cst.setdefault("look", (-.9, -.6))
        cst.setdefault("rot", -6 * fl * (1 - ramp(t, land, .5)))
        px, py = paw_tip(cat_x, FLOOR, CAT_K, max(.25, .95 * wind), 95)
        start = (px + 20, py - 90 - 60 * wind)
        if t < land:
            pts = []
            for d in range(6, 0, -1):
                x, y, *_ = throw_state(t - d * .022, land, start, (sx, sy - 72))
                pts.append((x, y))
            x, y, k, rot, ph = throw_state(t, land, start, (sx, sy - 72))
            if ph == "fly":
                fly_svg += trail(pts + [(x, y)])
            fly_svg += card(kind, x, y, k, t, rot, **kw)
        else:
            bo.append(shelf_card(kind, r, j, t, land, kw))
            bo.append(impact(sx, sy, t, land))
            bo.append(row_flash(r, bump(t, land, .04, .35)))
    o.append(f'<g transform="translate({bdx:.2f} {bdy:.2f}) rotate({bdx * .05:.3f} 540 {FLOOR})">{"".join(bo)}</g>')
    if dima:
        o.append(dima)
    o.append(judge(cat_x, FLOOR, CAT_K, t, cst, cat_lift, cat_shine))
    o.append(fly_svg)
    o.append(over)
    return "".join(o)


def board_shake(t, land, amp=16.0):
    if land is None:
        return 0.0, 0.0
    return shake(t, land, amp, .3, 9)


def audience(t, x=215.0, k=.42, expr="calm82", gasp_at=None, pose="d82_rest", flip=False, hop=0.0):
    """Дима в зале внизу слева, смотрит на доску."""
    g = bump(t, gasp_at, .06, .5) if gasp_at is not None else 0.0
    if gasp_at is not None and t >= gasp_at:
        expr, pose = "panic82", "d82_shrug"
    y = FLOOR + 330 - (people.LEG_LEN - 12) * k - 6 - 40 * g - hop
    d = people.dima82(x - 20 * g, y, k, expr, pose, t=t, feet="stand", flip=flip, head_add=-.18 - .1 * g)
    return d["svg"]


# ═════════════════════════ s01: хук — кот швыряет кулак на D ═════════════════════════
HIT01 = stress(0, .5)        # «ОценИваю»: карточка грохается на полку D


def hook_scene(t):
    land = HIT01
    bs = board_shake(t, land, 22)
    dm = audience(t, 215, .42, "wow82", gasp_at=land + .05)
    flap = .5 + .5 * math.sin(t * 9)
    st = dict(look=(-.9, -.4) if t < land + .5 else (-.3, .3), blink=0.0)
    if t > land + .55:                      # поправляет очки
        st.update(paw=.85 * bump(t, land + .55, .12, .5), paw_dx=-30, tilt=6)
    body = board_scene(t, (), ("fist", land, {"a": flap}), cat_st=st, bshake=bs, dima=dm, cat_lift=8 * bump(t, land + .6, .1, .4))
    return body


def hook_wrap(body, t, hit, bg="#e9dcc4"):
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    piv = 960.0
    tr = f"translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-piv})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<use href="#hk95" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk95">{body}</g></g>{blur}'


MASK_F = '<filter id="mk95"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def hook_cam_scene(t):
    """Камера сцены (часть рисунка): от полки D к общему плану, медленно."""
    u = ease_out(clamp(t / 1.6), 2)
    return 610 - 20 * u, 1080 - 80 * u, 1.42 - .14 * u


def frame_s01(t):
    cx, cy, s = hook_cam_scene(t)
    if MASK:
        lib.DEFS.append(MASK_F)
        body = hook_scene(t).replace(hall(t), "", 1)
        return lib.svg(f'<rect width="1080" height="1920" fill="#000"/><g transform="{lib.cam(cx, cy, s, 0)}"><g filter="url(#mk95)">{body}</g></g>')
    body = hook_scene(t)
    dx, dy = shake(t, HIT01, 14) if not NOCAM else (0, 0)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{body}</g>'
    if NOCAM:
        return lib.svg('<rect width="1080" height="1920" fill="#e9dcc4"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + title(t))


# ═════════════════════════ s02: кот тасует колоду ═════════════════════════
def juggle(t, cx, cy, n=6, speed=2.2):
    o = []
    for i in range(n):
        ph = (t * speed + i / n) % 1.0
        a = math.pi * ph
        x = cx + 150 * math.cos(a)
        y = cy - 230 * math.sin(a)
        o.append(card("fist", x, y, .42, t, rot=360 * ph + i * 20, back=True))
    return "".join(o)


def frame_s02(t):
    a, b = T0("s02"), T1("s02")
    u = ease_io(ramp(t, a, b - a))
    hx, hy = CT.head_world(CAT_X, FLOOR, CAT_K, {})
    st = dict(paw=.7 + .25 * math.sin(t * 13.8), paw_dx=-40, look=(-.2, -.9), tilt=4 * math.sin(t * 6.9))
    dm = audience(t, 215, .42, "wow82")
    body = board_scene(t, ("fist",), cat_st=st, dima=dm, over=juggle(t, hx - 40, hy - 200), cat_shine=bump(t, W(4), .06, .4))
    dx, dy = shake(t, W(3) + .1, 6)
    return view(body, 640 - 80 * u + dx, 1000 - 40 * u + dy, 1.12 + .1 * u, -1.5 + 2 * u, over=title(t))


# ═════════════════════════ s03: от худшего к лучшему — камера с D на S ═════════════════════════
def frame_s03(t):
    a, b = T0("s03"), T1("s03")
    u = ease_io(ramp(t, W(6) - .1, W(8) + .1 - W(6)))
    shine = bump(t, W(8) + .05, .08, .6)
    fl = [("D", .6 * bump(t, W(6), .06, .5)), ("S", shine + .4 * ramp(t, W(8), .3))]
    body = board_scene(t, ("fist",), flash=fl, cat_st=dict(look=(-.4, -1.0)), dima=audience(t, 215, .42, "look82", pose="d82_look_up"))
    if t > W(8):
        body += PR.sparkles(400, row_y("S") + 60, 2.2, shine + .5, t, seed=3, n=6, r=260)
    cy = row_y("D") + 40 + (row_y("S") + 300 - row_y("D") - 40) * u
    z = 1.5 - .15 * u + .08 * shine
    dx, dy = shake(t, W(8) + .05, 7)
    return view(body, 520 + dx, cy + dy, z, 0, over=title(t))


# ═════════════════════════ показ карточки со сценкой Димы ═════════════════════════
def dima(x, ground, k, expr, pose, t, flip=False, head_add=0.0, lean=0.0):
    y = ground - (people.LEG_LEN - 12) * k - 6
    return people.dima82(x, y, k, expr, pose, t=t, feet="stand", flip=flip, head_add=head_add, lean_add=lean)


def show_scene(t, sid, kind, kw, scene, ck=1.6, cy=430.0, cat=True, cat_st=None):
    """Карточка крупно сверху (влетает с поворотом в начале плана), под ней сценка; кот-судья сбоку показывает лапой."""
    a = T0(sid)
    p = pop(t, a - .05, .3)
    o = [hall(t), PR.glow(540, cy, 520, .5, "#fff4cf")]
    o.append(scene)
    if cat:
        st = dict(dict(paw=.9, paw_dx=-60, look=(-.7, -.8), tilt=-6 + 3 * math.sin(t * 3)), **(cat_st or {}))
        o.append(judge(900, FLOOR, .85, t, st))
    rot = -14 * (1 - p) + 2.5 * math.sin(t * 2.1)
    o.append(card(kind, 540, cy + 4 * math.sin(t * 2.7), ck * (.5 + .5 * p), t, rot, **kw))
    o.append(PR.sparkles(540, cy, 2.4, bump(t, a + .05, .06, .4), t, seed=2, n=5, r=230))
    return "".join(o)


def show_view(body, sid, t, z0=1.0, z1=1.08, cy=820.0, hit=None):
    a, b = T0(sid), T1(sid)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, hit, 9) if hit is not None else (0, 0)
    return view(body, 540 + dx, cy + dy - 30 * u, .17 + z0 + (z1 - z0) * u + (.05 * bump(t, hit, .05, .3) if hit is not None else 0), 0)


def frame_s04(t):
    sag = ease_io(ramp(t, stress(11, .3), .35))
    strain = (1 - sag) * ramp(t, W(9), .3)
    jx = 5 * strain * math.sin(t * 70)
    f = dima(450 + jx, FLOOR, .55, "puzzled82" if sag > .5 else "squint82", ("d82_press", "d82_rest"), t, lean=.25 * sag, head_add=.2 * sag)
    sc = f["svg"] + people.strain_marks(f["head"], f["scale"], t, strain)
    if sag > .1:
        sc += PR.sweat(f["head"][0] - 70, f["head"][1] - 20 + 60 * sag, .9)
    body = show_scene(t, "s04", "fist", {"a": strain}, sc)
    return show_view(body, "s04", t, hit=W(9) + .05)


def throw_view(body, t, land, c0, c1, sid, kick=.1):
    a, b = T0(sid), T1(sid)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, land, 16)
    z = c0[2] + (c1[2] - c0[2]) * u + kick * bump(t, land, .04, .3)
    return view(body, c0[0] + (c1[0] - c0[0]) * u + dx, c0[1] + (c1[1] - c0[1]) * u + dy, z, -1.2 * bump(t, land, .04, .4))


def frame_s05(t):
    land = LAND["fist"]
    st = {}
    if t > W(14):
        st = dict(tilt=9 * math.sin((t - W(14)) * 14) * math.exp(-(t - W(14)) / 1.2), look=(.0, .2))
    body = board_scene(t, (), ("fist", land, {"a": .5 + .5 * math.sin(t * 9)}), cat_st=st, bshake=board_shake(t, land),
                       dima=audience(t, gasp_at=land + .05))
    return throw_view(body, t, land, (660, 1010, 1.12), (560, 1060, 1.3), "s05")


def frame_s06(t):
    red = 7 + 5 * (t > stress(19, .3)) + 6 * (t > stress(19, .3) + .55)
    reach = ease_io(ramp(t, W(17), .4))
    f = dima(420, FLOOR, .55, "puzzled82" if t > stress(19, .3) else "look82", ("d82_rest", "d82_one"), t, u=0, head_add=-.2) if False else \
        people.dima82(420, FLOOR - (people.LEG_LEN - 12) * .55 - 6, .55, "puzzled82" if t > stress(19, .3) else "look82",
                      ("d82_rest", "d82_one"), t=t, u=reach, feet="stand", head_add=-.25)
    body = show_scene(t, "s06", "cal", {"red": red}, f["svg"])
    hop = stress(19, .3)
    body += PR.sparkles(540, 560, 1.2, bump(t, hop, .05, .3), t, seed=9, n=3, r=120)
    return show_view(body, "s06", t, 1.04, 1.12, hit=hop)


def frame_s07(t):
    land = LAND["cal"]
    blink = int(t * 4) % 2 if t > W(22) else 0
    st = dict(paw=.5 * bump(t, W(23), .2, .6), paw_dx=40, tilt=-7 * bump(t, W(23), .2, .6)) if t > W(22) else {}
    body = board_scene(t, ("fist",), ("cal", land, {"red": 19 if blink else 18}), cat_st=st, bshake=board_shake(t, land),
                       dima=audience(t, expr="puzzled82"))
    return throw_view(body, t, land, (560, 900, 1.0), (520, 1080, 1.22), "s07")


def frame_s08(t):
    import story_cta_tg as tg
    press = W(28) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=os.path.join(STORY, "common"))


def frame_s09(t):
    gone = stress(35, .3)
    u = clamp((t - gone) / .5)
    o = [hall(t), PR.glow(540, 900, 600, .4 + .4 * u, "#fff4cf")]
    if t < gone:
        wob = 4 * math.sin(t * 20)
        o.append(tf(PR.paper_pile(0, 0, 1.6, seed=3), 620 + wob, FLOOR, 1.0, wob * .3))
        o.append(tf(PR.paper_stack(0, 0, 1.2, n=8, seed=2), 660, FLOOR - 170, 1.0, 6))
    o.append(PR.dust_puff(640, FLOOR - 120, 2.6, u, seed=4))
    o.append(PR.sparkles(640, FLOOR - 200, 2.0, bump(t, gone + .1, .1, .5), t, seed=5, n=5, r=200))
    f = dima(330, FLOOR, .6, "calm82" if u > .3 else "look82", "d82_rest", t, head_add=-.05)
    o.append(f["svg"])
    o.append(judge(930, FLOOR, .8, t, dict(look=(-.6, .1), tilt=8 * bump(t, gone + .2, .15, .4), smile=1.0 if u > .5 else 0.0), shine=bump(t, gone, .1, .5)))
    a, b = T0("s09"), T1("s09")
    v = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1060 - 40 * v, 1.25 - .1 * v)


def frame_s10(t):
    L = 570 * ease_out(ramp(t, W(37), W(40) + .2 - W(37)), 2)
    land = W(40) + .25
    f = dima(270 - 40 * ease_out(ramp(t, land, .3)), FLOOR, .55, "panic82" if t > land else "look82",
             "d82_shrug" if t > land else "d82_rest", t, head_add=-.15)
    sc = f["svg"]
    body = show_scene(t, "s10", "scroll", {"L": L}, sc, cy=400, cat_st=dict(look=(-.8, .4)))
    body += impact(540, FLOOR, t, land, 1.2)
    return show_view(body, "s10", t, 1.0, .96, cy=930, hit=land)


def frame_s11(t):
    land = LAND["scroll"]
    L = 200 + 420 * ease_out(ramp(t, land + .05, .5))
    flinch = W(43)
    body = board_scene(t, ("fist", "cal"), ("scroll", land, {"L": L}), bshake=board_shake(t, land),
                       dima=audience(t, expr="calm82", gasp_at=flinch))
    return throw_view(body, t, land, (600, 860, 1.0), (520, 960, 1.12), "s11")


def frame_s12(t):
    a = T0("s12")
    o = []
    f = dima(400, FLOOR, .55, "look82", "d82_rest", t, head_add=.15)
    o.append(f["svg"])
    o.append(PR.desk(440, 1250, w=560, depth=90, leg_h=170, seed=2))
    o.append(PR.paper(470, 1205, 1.1, rot=3, seed=1, kind="blank", sy=.4))
    o.append(PR.sweat(f["head"][0] + 60, f["head"][1] - 30 + 40 * ((t - a) % .8), .9))
    tick = .5 + .5 * math.sin(t * 2 * math.pi * 2)
    body = show_scene(t, "s12", "timer", {"wedge": PR.WEDGE_25 * (1 - .15 * ramp(t, a, 2.0)), "ring": .3 * tick}, "".join(o))
    return show_view(body, "s12", t, 1.02, 1.1, hit=W(46) + .05)


def frame_s13(t):
    land = LAND["timer"]
    ring = clamp((t - land) / .1) * (1 - ramp(t, land + 1.0, .4))
    shr = W(53)
    body = board_scene(t, ("fist", "cal", "scroll"), ("timer", land, {"ring": ring}), bshake=board_shake(t, land),
                       dima=audience(t, expr="puzzled82" if t > shr else "calm82", pose="d82_shrug" if t > shr else "d82_rest"))
    return throw_view(body, t, land, (580, 820, .98), (560, 760, 1.12), "s13")


def frame_s14(t):
    idea, do = W(57), W(61)
    f = dima(420, FLOOR, .55, "sure82" if t > do else ("wow82" if t > idea else "calm82"), ("d82_rest", "d82_one"), t,
             head_add=-.1) if False else people.dima82(420, FLOOR - (people.LEG_LEN - 12) * .55 - 6, .55,
                                                       "proud82" if t > do + .3 else ("wow82" if t > idea else "calm82"),
                                                       ("d82_rest", "d82_one"), t=t, u=ease_io(ramp(t, do, .3)), feet="stand")
    sc = f["svg"] + PR.idea_bulb(f["head"][0] - 10, f["head"][1] - 190, 1.0, on=ramp(t, idea, .15), t=t)
    sc += PR.check_mark(f["head"][0] + 190, f["head"][1] - 60, 3.0, ramp(t, do + .25, .3))
    body = show_scene(t, "s14", "fork", {"u": ramp(t, idea, .2)}, sc)
    return show_view(body, "s14", t, 1.0, 1.1, hit=do + .25)


def frame_s15(t):
    land = LAND["fork"]
    nod = W(65)
    st = dict(tilt=7 * math.sin((t - nod) * 12) * math.exp(-(t - nod) / .8), look=(-.2, .3)) if t > nod else {}
    body = board_scene(t, ("fist", "cal", "scroll", "timer"), ("fork", land), cat_st=st, bshake=board_shake(t, land), cat_shine=bump(t, nod + .2, .1, .5),
                       dima=audience(t, expr="sure82"))
    return throw_view(body, t, land, (600, 760, 1.0), (560, 640, 1.16), "s15")


def frame_s16(t):
    a = T0("s16")
    o = []
    f = people.dima82(360, FLOOR - (people.LEG_LEN - 12) * .55 - 6, .55, "proud82", "d82_press", t=t, feet="stand", head_add=.1)
    o.append(f["svg"])
    o.append(PR.desk(520, 1250, w=640, depth=90, leg_h=170, seed=3))
    o.append(PR.checklist(470, 1190, 1.0, rot=-4, checks=int(clamp((t - a - .2) / .45) * 3.999), u=((t - a - .2) / .45) % 1.0, seed=2, sy=.55))
    o.append(PR.pencil(520, 1170, .9, rot=-35 + 8 * math.sin(t * 14)) if hasattr(PR, "pencil") else "")
    o.append(judge(700, 1180, .45, t, dict(look=(-.8, .2), tail=10 * math.sin(t * 2), smile=1.0, blink=1.0 if (t * 1.3) % 1 < .08 else 0.0)))
    for i in range(3):
        o.append(PR.check_mark(220 + i * 70, 1020 - i * 30, 1.4, ramp(t, a + .35 + i * .4, .2), seed=i))
    body = show_scene(t, "s16", "two", {"nod": 1.0}, "".join(o), cat=False)
    return show_view(body, "s16", t, 1.02, 1.1, hit=W(68) + .05)


def frame_s17(t):
    land = LAND["two"]
    body = board_scene(t, ("fist", "cal", "scroll", "timer", "fork"), ("two", land), bshake=board_shake(t, land),
                       flash=[("S", .5 * bump(t, land + .05, .1, .5))], dima=audience(t, expr="wow82"))
    return throw_view(body, t, land, (600, 720, 1.0), (560, 560, 1.18), "s17")


def confetti(t, t0, n=60, cx=540.0, cy=420.0):
    if t < t0:
        return ""
    u = t - t0
    rs = PR._rs(9911)
    cols = ["#f2bd22", "#62c25a", "#5ab3ea", "#e5483c", "#f08a3c", "#b07ae0"]
    o = []
    for i in range(n):
        a = rs.uniform(-math.pi, 0)
        v = rs.uniform(500, 1300)
        x = cx + math.cos(a) * v * u * .9 + 40 * math.sin(u * 6 + i)
        y = cy + math.sin(a) * v * u + 900 * u * u
        r = rs.uniform(0, 360) + 600 * u * (1 if i % 2 else -1)
        w, h = rs.uniform(14, 26), rs.uniform(8, 14)
        o.append(f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h * abs(math.cos(u * 9 + i)):.1f}" fill="{cols[i % 6]}" '
                 f'transform="translate({x:.1f} {y:.1f}) rotate({r:.1f})"/>')
    return "".join(o)


def frame_s18(t):
    a, b = T0("s18"), T1("s18")
    land = LAND["hour"]
    landed = ("fist", "cal", "scroll", "timer", "fork", "two")
    raise_u = ease_out(ramp(t, a, .5))
    sglow = .3 + .5 * ramp(t, W(76), .4)
    over = confetti(t, land)
    if t < land - THROW - WIND:              # поднимает сияющую карточку над головой
        hx, hy = CT.head_world(CAT_X, FLOOR, CAT_K, {})
        st = dict(paw=.95 * raise_u, paw_dx=10, look=(-.2, -1.0), tilt=-4)
        body = board_scene(t, landed, cat_st=st, flash=[("S", sglow)], dima=audience(t, expr="wow82", pose="d82_look_up"),
                           cat_shine=bump(t, a + .3, .1, .5),
                           over=card("hour", hx + 30, hy - 230 - 120 * raise_u + 8 * math.sin(t * 4), .8, t, 4 * math.sin(t * 3), glow=1.0)
                           + PR.sparkles(hx + 30, hy - 350 - 120 * raise_u, 2.0, 1.0, t, seed=4, n=6, r=200))
    else:
        st = {}
        if t > land + .25:                   # довольно поправляет очки
            st = dict(paw=.85 * bump(t, land + .3, .15, .6), paw_dx=-30, tilt=6, smile=1.0, look=(.0, .3))
        body = board_scene(t, landed, ("hour", land), cat_st=st, flash=[("S", sglow + bump(t, land, .04, .5))], bshake=board_shake(t, land, 18),
                           dima=audience(t, expr="proud82", hop=60 * bump(t, land + .1, .12, .3)), cat_lift=10 * bump(t, land + .35, .12, .5),
                           over=over)
        body += PR.glow(690, row_y("S") + 80, 700, bump(t, land, .03, .4), "#fff6c8")
    # камера: кот с карточкой → взгляд вверх на S → общий план = ракурс хука
    hc = (560.0, 800.0, .98)                 # общий план всей доски (как начало влёта хука)
    u1 = ease_io(ramp(t, a, land - .2 - a))
    u2 = ease_io(ramp(t, land + .15, b - land - .15))
    cx = 760 + (600 - 760) * u1
    cy = 1080 + (560 - 1080) * u1
    z = 1.25 + (1.1 - 1.25) * u1
    cx, cy, z = cx + (hc[0] - cx) * u2, cy + (hc[1] - cy) * u2, z + (hc[2] - z) * u2
    dx, dy = shake(t, land, 16)
    return view(body, cx + dx, cy + dy, z + .08 * bump(t, land, .04, .3), 0)


FRAMES = {k[6:]: v for k, v in dict(globals()).items() if k.startswith("frame_s")}


def frame(sid, t):
    if sid not in ("s08",):
        lib.DEFS.clear()
    return FRAMES[sid](t)
