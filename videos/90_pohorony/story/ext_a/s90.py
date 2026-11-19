"""Рилс 90 «Похороны планов», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
Кладбище планов (yard): ряд маленьких надгробий со значками без букв (книга, гантеля, флажок — чашка и силуэт часовой
башни, луна) и подушка-надгробие «сна»; кот в чёрной накидке священника и шапочке, Дима рыдает в платок; лёгкий дождь.
Хук s01 — влёт правил 28–29 (anim.hook_cam) вдоль ряда; s18 — петля тем же ракурсом (дождь кончился, солнце, цветок).
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука белым на чёрном."""
import json
import math
import os
import sys

import numpy as np

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
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402,F401

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


def pop(t, a, d=.22):
    """Выскакивает с перелётом: 0 → 1.15 → 1."""
    u = clamp((t - a) / d)
    return lib.back_out(u) if u < 1 else 1.0


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def tf(inner, x, y, k=1.0, rot=0.0, sx=None, sy=None):
    if sx is not None:
        return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k * sx:.4f} {k * sy:.4f})">{inner}</g>'
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{inner}</g>'


def title(t):
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


# ═════════════════════════ мир: кладбище ═════════════════════════
FL = 1240.0                                   # земля заднего ряда надгробий
GR_X = dict(book=-80.0, dumbbell=230.0, flag=540.0, moon=850.0, pillow=1160.0)
ICON, ICON_HI = "#555a62", "#c9ccd2"
STONE, STONE_SH, STONE_HI = "#aeb2b9", "#8d9199", "#c8ccd2"


def sky_cols(sun):
    top = lib.mix("#8d97ad", "#7cc3ec", sun)
    bot = lib.mix("#c9ccd6", "#e6f3fa", sun)
    return top, bot


def yard_bg(t, sun=0.0, x0=-1600.0, x1=3200.0):
    top, bot = sky_cols(sun)
    g = lib.lin_grad([(0, top, 1), (1, bot, 1)], 0, -1400, 0, FL - 120, units="userSpaceOnUse")
    o = [f'<rect x="{x0}" y="-2400" width="{x1 - x0}" height="{FL - 120 + 2400}" fill="url(#{g})"/>']
    if sun > .02:
        o.append(f'<g opacity="{sun:.3f}">{PR.sun(1000.0, -60.0, 95, 1.0, t, seed=3)}</g>')
    for j, (cx, cy, w_) in enumerate(((-300, -200, 520), (420, -330, 640), (1200, -150, 560))):     # облака уплывают, когда выходит солнце
        cxx = cx + 18 * t + 900 * sun * (1 if j % 2 else -1)
        o.append(blob(ellipse_pts(cxx, cy, w_ / 2, 70, 24), lib.mix("#b3b9c7", "#ffffff", sun), .9))
        o.append(blob(ellipse_pts(cxx - w_ * .2, cy - 40, w_ * .25, 60, 20), lib.mix("#bcc1ce", "#ffffff", sun), .9))
    hills = [(x0, FL - 120), (-700, FL - 260), (-100, FL - 200), (500, FL - 300), (1100, FL - 210), (1800, FL - 280), (x1, FL - 160), (x1, FL + 200),
             (x0, FL + 200)]
    o.append(blob(hills, lib.mix("#9aa892", "#9fc283", sun)))
    o.append(rect(x0, FL - 130, x1, 5200, lib.mix("#87a06c", "#8fc062", sun)))
    o.append(PR.tree(-420.0, FL - 140, 1.0, .25 + .75 * sun, t, seed=2))
    o.append(PR.tree(1520.0, FL - 130, 1.15, .25 + .75 * sun, t, seed=5))
    o.append(PR.fence(x0, x1, FL - 60, .75, seed=1))
    for k in range(int((x1 - x0) / 140)):                       # травинки
        x = x0 + k * 140 + 37 * math.sin(k * 7.1)
        y = FL + 60 + 180 * ((k * 37) % 5)
        o.append(line([(x, y), (x - 8, y - 26)], 3, lib.mix("#5f7a4a", "#5b8c3c", sun), seed=9000 + k, op=.8))
        o.append(line([(x + 8, y), (x + 14, y - 22)], 3, lib.mix("#5f7a4a", "#5b8c3c", sun), seed=9100 + k, op=.8))
    return "".join(o)


def icon(kind, t=0.0, steam=1.0):
    """Значок на камне (выбит), центр (0, 0), ~130 px, без букв."""
    c = ICON
    if kind == "dumbbell":
        o = line([(-50, 0), (50, 0)], 9, c, taper=0, wmin=1, seed=1)
        for s_ in (-1, 1):
            o += shape(lib.rrect(s_ * 40 - 9, -34, s_ * 40 + 9, 34, 5), c, "", w=2.5, seed=2 + s_)
            o += shape(lib.rrect(s_ * 58 - 8, -24, s_ * 58 + 8, 24, 5), c, "", w=2.5, seed=4 + s_)
        return o
    if kind == "book":
        o = shape([(0, -30), (-62, -40), (-62, 34), (0, 42)], ICON_HI, line([(-50, -20), (-10, -14)], 3, c, seed=6) + line([(-50, -4), (-10, 2)], 3, c, seed=7),
                  w=5, seed=5, ink_color=c)
        o += shape([(0, -30), (62, -40), (62, 34), (0, 42)], ICON_HI, line([(10, -14), (50, -20)], 3, c, seed=9) + line([(10, 2), (50, -4)], 3, c, seed=10),
                   w=5, seed=8, ink_color=c)
        return o
    if kind == "flag":       # «английский»: чайная чашка и силуэт часовой башни, без букв
        o = blob([(24, 52), (26, -38), (34, -40), (40, -76), (46, -40), (54, -38), (56, 52)], c)                       # башня
        o += blob(lib.rect_pts(24, -38, 56, -30), c)
        o += f'<circle cx="40" cy="-12" r="9" fill="{ICON_HI}"/>'
        o += line([(40, -12), (40, -18)], 2.5, c, taper=0, wmin=1, seed=11) + line([(40, -12), (44, -10)], 2.5, c, taper=0, wmin=1, seed=12)
        o += blob([(-62, 10), (6, 10), (0, 34), (-18, 44), (-44, 44), (-56, 34)], c)                 # чашка
        o += line(ellipse_pts(10, 22, 11, 11, 12)[3:10], 5, c, taper=0, wmin=1, seed=13)
        o += blob(ellipse_pts(-28, 50, 46, 6, 14), c)
        if steam > .02:
            for j, x in enumerate((-40, -24)):
                ph = t * 5 + j * 2
                pts = [(x + 6 * math.sin(ph + q), 4 - 12 * q) for q in range(4)]
                o += line(pts, 3.2, c, taper=.5, wmin=.3, seed=14 + j, op=steam)
        return o
    if kind == "moon":
        cid = lib.uid("mn")
        o = (f'<defs><mask id="{cid}"><rect x="-80" y="-80" width="160" height="160" fill="#fff"/>'
             f'<circle cx="22" cy="-14" r="40" fill="#000"/></mask></defs>'
             f'<circle cx="0" cy="0" r="46" fill="{c}" mask="url(#{cid})"/>')
        o += PR.star4(40, 34, 12).replace(INK, c) if False else blob([(46, 22), (50, 32), (60, 36), (50, 40), (46, 50), (42, 40), (32, 36), (42, 32)], c)
        return o
    return ""


def tally(n_total, us, y=-70.0):
    """Палочки-дни, выбитые под значком; us — доля прорисовки каждой."""
    o = ""
    xs = [(-1.5 + i) * 30 for i in range(4)] if n_total > 2 else [(-.5 + i) * 34 for i in range(2)]
    for i, u in enumerate(us[:n_total]):
        if u <= .01:
            continue
        x = xs[i]
        o += line([(x - 3, y - 26), (x - 3 + 6 * u, y - 26 + 54 * u)], 10, ICON, taper=.15, wmin=.7, seed=40 + i)
    return o


STONE_PTS = [(-105, 6, 1), (-104, -210), (-92, -262), (-56, -292), (0, -302), (56, -292), (92, -262), (104, -210), (105, 6, 1)]


def mound(x, y, k=1.0, sun=0.0, seed=0):
    col = lib.mix("#7a5c40", "#8a6644", sun)
    o = shape(ellipse_pts(0, 14, 150, 30, 24), col, blob(ellipse_pts(30, 22, 110, 14, 18), lib.mul(col, (.85, .85, .85)), .7), w=4, seed=9200 + seed)
    for j in range(4):
        xx = -110 + j * 70
        o += line([(xx, 6), (xx - 6, -16)], 3, "#5d7d43", seed=9210 + seed + j)
    return tf(o, x, y, k)


def grave(x, y, kind, k=1.0, t=0.0, ticks=None, n=0, wet=1.0, sun=0.0, seed=0, steam=1.0, icon_k=1.0, drip=None, shake_x=0.0):
    """Надгробие (центр низа x, y), высота ~300·k. ticks — доли прорисовки палочек; drip 0…1 — капля бежит по камню."""
    inner = blob([(40, -292), (104, -210), (105, 6), (50, 6)], STONE_SH, .8)
    inner += blob([(-92, -262), (-56, -292), (-20, -298), (-60, -270), (-86, -230)], STONE_HI, .9)
    inner += line([(-80, -230), (-60, -268), (-10, -286)], 3, "#7b8088", seed=9300 + seed, op=.5)
    if wet > .02:
        for j in range(3):
            xx = -70 + j * 55
            inner += line([(xx, -200 + 30 * j), (xx + 2, -120 + 20 * j)], 3, "#e7ebf2", seed=9310 + seed + j, op=.45 * wet)
    inner += tf(icon(kind, t, steam), 0, -190, icon_k)
    if ticks is not None:
        inner += tally(n, ticks)
    if drip is not None and drip > .01:
        dy = -240 + 230 * ease_io(clamp(drip))
        inner += line([(46, -240), (46, dy)], 5, "#cfe7f7", seed=9330, op=.7)
        inner += PR.drop(46, dy + 12, .55)
    st = shape(STONE_PTS, STONE, inner, w=5.5, seed=9320 + seed)
    return tf(mound(0, 0, 1.0, sun, seed) + st, x + shake_x, y, k)


def pillow_grave(x, y, k=1.0, t=0.0, awake=0.0, snore=1.0, sun=0.0, z=True):
    """Подушка вместо надгробия: живая, спит и сопит (дышит, глаза-дуги, Z)."""
    br = math.sin(t * 2 * math.pi / 2.2)
    sy = 1 + .045 * br * snore
    sx = 1 - .02 * br * snore
    col, sh = "#e7dcf4", "#c9b8e2"
    pts = [(-118, 4, 1), (-128, -60), (-116, -160), (-128, -236), (-96, -262), (0, -250), (96, -262), (128, -236), (116, -160), (128, -60), (118, 4, 1)]
    inner = blob([(50, -250), (120, -236), (110, -150), (122, -60), (110, 4), (60, 4)], sh, .7)
    inner += line([(-40, -40), (0, -60), (40, -44)], 3, sh, seed=9401)
    for s_ in (-1, 1):                               # глаза-дуги сна
        ex = s_ * 42
        if awake > .5:
            inner += blob(ellipse_pts(ex, -150, 10, 12, 10), INK)
        else:
            inner += line([(ex - 20, -152), (ex, -142), (ex + 20, -152)], 5, INK, seed=9402 + s_)
    inner += blob(ellipse_pts(0, -108, 10 + 4 * max(0, br), 7 + 5 * max(0, br), 12), "#7a4f6e")       # сопит ртом
    inner += blob(ellipse_pts(-62, -120, 16, 9, 10), "#f2a7b8", .6) + blob(ellipse_pts(62, -120, 16, 9, 10), "#f2a7b8", .6)
    p = shape(pts, col, inner, w=5.5, seed=9400)
    o = mound(0, 0, 1.0, sun, 7) + f'<g transform="scale({sx:.4f} {sy:.4f})">{p}</g>'
    if z:
        o += PR.zzz(90, -300, 1.0, t, 1.0)
    return tf(o, x, y, k)


def rain(t, op=1.0, n=46, seed=0):
    """Лёгкий дождь в экранных координатах: косые штрихи падают непрерывно."""
    if op <= .01:
        return ""
    rs = np.random.RandomState(9500 + seed)
    o = []
    for i in range(n):
        x0, y0, sp = rs.uniform(-200, 1180), rs.uniform(0, 2200), rs.uniform(1700, 2300)
        y = (y0 + t * sp) % 2200 - 140
        x = x0 + (y + 140) * .18
        L = rs.uniform(46, 80)
        o.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x - L * .18:.1f}" y2="{y - L:.1f}" stroke="#e9eff8" stroke-width="3.2" '
                 f'stroke-linecap="round" opacity="{.55 * op:.3f}"/>')
    return "".join(o)


def splashes(t, pts, op=1.0):
    o = []
    for j, (x, y) in enumerate(pts):
        ph = (t * 1.7 + j * .37) % 1.0
        if ph < .35:
            u = ph / .35
            for s_ in (-1, 1):
                o.append(line([(x + s_ * 6, y), (x + s_ * (14 + 18 * u), y - 18 + 8 * u)], 3.4 * (1 - u) + .5, "#dce8f4", taper=.4, wmin=.3,
                              seed=9600 + j, op=op))
    return "".join(o)


# ═════════════════════════ кот-священник ═════════════════════════
CLOAK, CLOAK_SH = "#24232b", "#15141a"
CAP, CAP_SH = "#3c3848", "#2a2733"


def cap_svg(x, y, k=1.0, rot=0.0):
    o = shape([(-56, 6, 1), (-54, -14), (-34, -36), (0, -44), (34, -36), (54, -14), (56, 6, 1)], CAP,
              blob([(10, -40), (54, -14), (56, 6), (24, 6)], CAP_SH) + line([(-40, -20), (-10, -34)], 3, "#55535e", seed=9701), w=4, seed=9700)
    o += f'<circle cx="0" cy="-46" r="7" fill="{CAP}" stroke="{INK}" stroke-width="3"/>'
    return tf(o, x, y, k, rot)


def cat_priest(x, y, k, t, st=None, cap=0.0, book=0.0, nod=0.0):
    """Кот в чёрной накидке с белым воротничком. cap: 0 — шапочка на голове, 0…1 — лапа снимает её и прижимает к груди.
    book 0…1 — держит у груди раскрытую чёрную книгу (страницы без букв). nod — кивок головой (0…1)."""
    st = dict(st or {})
    sl = 0.0
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    tail_a = st.get("tail", 0.0) + 6 * math.sin(t * 1.7)
    tilt = st.get("tilt", 0.0) + 9 * nod
    o = [f'<g transform="rotate({tail_a:.2f} {CT.TAIL_PIVOT[0]} {CT.TAIL_PIVOT[1]})">{CT.tail_art()}{CT.flame(t, 1.3, st.get("flame_e", .8))}</g>']
    o.append(f'<g transform="translate({CT.CX} {CT.CBOT}) scale(1 {br:.4f}) translate({-CT.CX} {-CT.CBOT})">{CT.body()}</g>')
    # накидка: от шеи до лап, разрез спереди, белый воротничок
    cl = [(800, 1146), (872, 1146), (930, 1222), (956, 1300, 1), (850, 1294), (836, 1210), (822, 1294), (716, 1300, 1), (742, 1222)]
    inner = blob([(872, 1146), (930, 1222), (956, 1300), (880, 1296)], CLOAK_SH, .9)
    inner += line([(760, 1250), (780, 1292)], 3, "#4a4954", seed=9711) + line([(912, 1246), (896, 1292)], 3, "#4a4954", seed=9712)
    o.append(f'<g transform="translate({CT.CX} {CT.CBOT}) scale(1 {br:.4f}) translate({-CT.CX} {-CT.CBOT})">'
             + shape(cl, CLOAK, inner, w=5, seed=9710) + '</g>')
    o.append(shape(lib.rrect(806, 1140, 866, 1162, 9), "#fbfaf6", "", w=3.4, seed=9713))
    hy = -(br - 1) * (CT.CBOT - CT.NECK[1]) + 10 * nod
    head = CT.head(st, t)
    cu = clamp(cap)
    if cu < .02:
        head += cap_svg(836, 1004, 1.0, -4)
    o.append(f'<g transform="translate(0 {hy:.2f}) rotate({tilt:.2f} {CT.NECK[0]} {CT.NECK[1]})">{head}</g>')
    if book > .01:
        bu = ease_out(clamp(book), 3)
        by = 1250 - 40 * bu
        bk = shape([(746, by - 6), (836, by + 6), (926, by - 6), (920, by + 60), (836, by + 70), (752, by + 60)], CLOAK, "", w=4, seed=9720)
        for s_ in (-1, 1):
            pg = [(836, by + 2), (836 + s_ * 82, by - 10), (836 + s_ * 78, by + 50), (836, by + 60)]
            inner = "".join(line([(836 + s_ * 14, by + 10 + 12 * j), (836 + s_ * 64, by + 2 + 12 * j)], 2.4, "#b9b2a4", seed=9722 + j + s_ * 5)
                            for j in range(3))
            bk += shape(pg, "#fbf4e2", inner, w=3.4, seed=9721 + s_)
        for s_ in (-1, 1):
            bk += shape(ellipse_pts(836 + s_ * 88, by + 30, 22, 24, 14), CT.CAT, blob(ellipse_pts(836 + s_ * 84, by + 38, 10, 8, 10), "#f0a37b"), w=4,
                        seed=9725 + s_)
        o.append(f'<g opacity="{min(1.0, book * 3):.3f}">{bk}</g>')
    if cu >= .02:
        # лапа в рукаве накидки: от плеча к шапочке; шапочка с головы — дугой — к груди
        hx, hyy = 836, 1004 + hy
        cx_ = hx - 100 * math.sin(math.pi * min(1.0, cu * 1.25)) * (1 - cu) + 0 * cu
        cy_ = hyy + (1222 - hyy) * ease_io(cu) - 110 * math.sin(math.pi * cu)
        px_, py_ = cx_ - 58, cy_ - 2
        sh_ = (762, 1182)
        el = (min(px_, 760) - 70, (sh_[1] + py_) / 2 + 20)
        o.append(line([sh_, el, (px_, py_)], 38, CLOAK, taper=0, wmin=1, seed=9730))
        o.append(cap_svg(cx_, cy_, 1.0, -4 - 16 * cu))
        o.append(shape(ellipse_pts(px_, py_, 24, 22, 14), CT.CAT, blob(ellipse_pts(px_ + 4, py_ + 6, 10, 7, 10), "#f0a37b"), w=4, seed=9731))
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-CT.CX} {-CT.CBOT})">{"".join(o)}</g>'


def cat_st(t, look=(0.0, .2), blink_at=(), **kw):
    st = dict(look=look, tail=0.0, flame_e=.8)
    b = 0.0
    for a in blink_at:
        if a <= t < a + .16:
            b = math.sin(math.pi * (t - a) / .16)
    st["blink"] = b
    st.update(kw)
    return st


# ═════════════════════════ Дима ═════════════════════════
def stand_y(ground, sc):
    return ground - 590 * sc


CRY = {"brows": "sad", "mouth": "wobble", "open": .55, "squeeze": 1.0, "lid": .4}


def dima(x, ground, sc, t, expr="cry", sob=0.0, tissue=1.0, look=None, lean=0.0, head_ang=-.06, arms=None, hands=None, layers=None, tears=1.0):
    """Дима стоит (ступни на ground). expr 'cry' — рыдает: глаза зажмурены, губа дрожит, платок у щеки ближней рукой,
    плечи вздрагивают (sob — фаза всхлипа 0…1), слёзы брызгают. -> (svg, res)."""
    y = stand_y(ground, sc) - 14 * sc * sob
    if expr == "cry":
        ex = dict(CRY, open=.35 + .4 * sob)
    else:
        ex = dict(people.EXPR["dima"][expr]) if isinstance(expr, str) else dict(expr)
    if look:
        ex["look"] = look
    lean_ = lean + .05 * sob
    probe = people.figure("dima", x, y, sc, expr=ex, lean=lean_, head_ang=head_ang, feet=people.stand_kw(x, y, sc)["feet"])
    hx, hy = probe["head"]
    if arms is None and tissue > .01:
        tp = (hx + 185 * sc, hy + 175 * sc + 10 * sc * sob)
        arms = {"n": ("ik", tp, -1), "f": ("ang", .14, .25)}
        hands = {"n": {"dir": (-.3, -1), "curl": (.6, .6, .65, .7), "thumb": .5}}
    res = people.figure("dima", x, y, sc, expr=ex, lean=lean_, head_ang=head_ang, arms=arms, hands=hands, feet=people.stand_kw(x, y, sc)["feet"],
                        layers=layers)
    o = res["svg"]
    if arms is not None and tissue > .01 and expr == "cry":
        wx, wy = res["wrist"]["n"]
        o += PR.tissue(wx - 14 * sc, wy - 58 * sc, 1.1 * sc, -35 + 8 * sob, seed=1)
    if expr == "cry" and tears > .01:
        hx, hy = res["head"]
        for j, (ox, ph0) in enumerate(((-10, 0.0), (110, .45))):           # слёзы брызгают струйками от глаз
            for q in range(3):
                ph = (t * 2.2 + ph0 + q / 3) % 1.0
                ex_, ey_ = hx + ox * sc, hy - 15 * sc
                sgn = -1 if ox < 0 else 1
                px = ex_ + sgn * (30 + 160 * ph) * sc
                py = ey_ - 40 * sc + 300 * sc * ph * ph - 60 * sc * ph
                o += PR.drop(px, py, .55 * sc / .66 * (1 - .4 * ph), sgn * 30, col="#8fcdf2")
    return o, res


# ═════════════════════════ ракурс хука / петли ═════════════════════════
DIMA_POS = (300.0, FL + 300, .62)          # x, земля, масштаб
CAT_POS = (790.0, FL + 250, 1.4)
FG = [(-120.0, "book"), (820.0, "moon"), (1500.0, "dumbbell")]
FG_Y, FG_K = FL + 960, 1.75


def yard_row(t, sun=0.0, flower=0.0, fresh=0.0, sticks=True, steam=1.0, pillow_z=True, wet=1.0, drip=None):
    o = []
    for name, x in GR_X.items():
        if name == "pillow":
            o.append(pillow_grave(x, FL, .95, t, sun=sun, z=pillow_z))
            continue
        tk = None
        n = 0
        if sticks and name == "dumbbell":
            tk, n = [1, 1, 1, 1], 4
        if sticks and name == "flag":
            tk, n = [1, 1], 2
        o.append(grave(x, FL, name, 1.0, t, tk, n, wet=wet, sun=sun, seed=hash(name) % 50, steam=0.0, drip=drip if name == "moon" else None))
        if name == "flag" and flower > .01:
            o.append(flower_svg(x - 110, FL + 14, .9 * flower, t))
    return "".join(o)


def hook_world(t, sun=0.0, cry=True, cat_cap=0.0, dima_expr="cry", fg_dx=0.0, flower=0.0, cat_sleep=False, rain_on=True):
    """-> (тело мира, рисунок хука для маски)."""
    o = [yard_bg(t, sun)]
    row = yard_row(t, sun, flower)
    o.append(row)
    dx, dg, ds = DIMA_POS
    sob = .5 + .5 * math.sin(t * 2 * math.pi * 1.6)
    if cry:
        dsvg, _ = dima(dx, dg, ds, t, "cry", sob)
    else:
        dsvg, _ = dima(dx, dg, ds, t, dima_expr, 0.0, tissue=0.0, arms=None)
    cx, cg, ck = CAT_POS
    if cat_sleep:
        csvg = ""
    else:
        csvg = cat_priest(cx, cg, ck, t, cat_st(t, look=(-.5, .35), blink_at=(.9,)), cap=cat_cap, nod=.5 + .5 * math.sin(t * 2.4))
    o += [csvg, dsvg]
    fg = "".join(grave(x + fg_dx, FG_Y, kind, FG_K, t, wet=1.0 - sun, sun=sun, seed=30 + j) for j, (x, kind) in enumerate(FG))
    o.append(fg)
    if rain_on and sun < .5:
        o.append(splashes(t, [(GR_X[n] + 60, FL + 10) for n in GR_X] + [(dx + 200, dg), (cx - 200, cg)], 1 - 2 * sun))
    return "".join(o), row + csvg + dsvg + fg


def view(body, cx, cy, s, rot=0.0, over="", bg="#8d97ad"):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


PIV = 820.0


def hook_wrap(body, t, hit):
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    tr = f"translate({540 + dx:.2f} {PIV + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-PIV})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<g opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {PIV + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-PIV})">{body}</g>')
    return f'<rect width="1080" height="1920" fill="#8d97ad"/><g transform="{tr}">{body}</g>{blur}'


MASK_F = '<filter id="mk90"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def mask_svg(world_mask, cam):
    lib.DEFS.append(MASK_F)
    return lib.svg('<rect width="1080" height="1920" fill="#000"/>'
                   f'<g transform="{lib.cam(*cam)}"><g filter="url(#mk90)">{world_mask}</g></g>')


HIT01 = stress(2, .42)          # «прощА́емся»


def hook_cam_scene(t):
    u = 1 - math.exp(-t / .6)
    return 300 + 260 * u, 1180 - 40 * u, .93 + .05 * u, -1.5 + 1.5 * u


def frame_s01(t):
    cx, cy, s, r = hook_cam_scene(t)
    fg_dx = -(cx - 300) * .8                 # передний ряд надгробий пролетает быстрее (параллакс)
    body, maskw = hook_world(t, fg_dx=fg_dx)
    if MASK:
        return mask_svg(maskw, (cx, cy, s, r))
    dx, dy = shake(t, HIT01, 12) if not NOCAM else (0, 0)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, r)}">{body}</g>'
    if NOCAM:
        return lib.svg('<rect width="1080" height="1920" fill="#8d97ad"/>' + v + rain(t))
    return lib.svg(hook_wrap(v + rain(t), t, HIT01) + title(t))


# ═════════════════════════ s02: отпевание — кот читает, Дима сморкается ═════════════════════════
def frame_s02(t):
    a = T0("s02")
    o = [yard_bg(t), yard_row(t)]
    cx, cg, ck = CAT_POS
    honk = bump(t, stress(5, .3), .06, .35)
    o.append(cat_priest(cx - 80, cg, ck, t, cat_st(t, look=(-.6, .1) if honk < .3 else (-.9, -.1), blink_at=(a + .5,)), book=ramp(t, a - .1, .3),
                        nod=.3 * math.sin(t * 3)))
    sob = .5 + .5 * math.sin(t * 2 * math.pi * 1.8)
    dsvg, res = dima(DIMA_POS[0] + 60, DIMA_POS[1], DIMA_POS[2], t, "cry", sob + .6 * honk)
    o.append(dsvg)
    if honk > .02:     # сморкается: платок раздувается, брызги
        hx, hy = res["head"]
        o.append(PR.sparkles(hx + 120, hy + 40, .8, honk, t, seed=4, col="#8fcdf2"))
    z = 1.32 + .08 * ease_io(ramp(t, a, T1("s02") - a)) + .05 * honk
    dx, dy = shake(t, stress(5, .3), 9)
    return view("".join(o), 620 + dx, 1000 + dy, z, -1.0 + 1.6 * ramp(t, a, 1.2), over=rain(t, .9) + title(t))


# ═════════════════════════ s03: кот указывает на надгробие-гантелю ═════════════════════════
def frame_s03(t):
    a = T0("s03")
    o = [yard_bg(t), yard_row(t, sticks=False)]
    u = ease_io(ramp(t, a, T1("s03") - a + .2))
    cx, cg, ck = CAT_POS
    o.append(cat_priest(cx - 300, cg - 30, ck * .95, t, cat_st(t, look=(-.8, -.1), tilt=-8), nod=.4 * bump(t, W(8), .1, .4)))
    o.append(dima(DIMA_POS[0] - 330, DIMA_POS[1], DIMA_POS[2], t, "cry", .5 + .5 * math.sin(t * 9))[0])
    cxc = 520 - 230 * u
    return view("".join(o), cxc, 1080 - 60 * u, .95 + .5 * u, 1.5 - 2.5 * u, over=rain(t, .9, seed=1))


# ═════════════════════════ храповик: гантеля / флажок / луна ═════════════════════════
def grave_close(t, sid, kind, n, wi, cam_from, extra="", steam=0.0, tumble=None, ghost=None):
    a, b = T0(sid), T1(sid)
    o = [yard_bg(t, x0=GR_X[kind] - 900, x1=GR_X[kind] + 900)]
    for nm, x in GR_X.items():
        if False:
            o.append(grave(x, FL, nm, 1.0, t, [1] * (4 if nm == "dumbbell" else 2) if nm in ("dumbbell", "flag") else None,
                           4 if nm == "dumbbell" else 2 if nm == "flag" else 0, steam=0.0, seed=hash(nm) % 50))
    ticks = []
    hits = []
    for i in range(n):
        h = stress(wi, .2) + i * .11
        hits.append(h)
        ticks.append(ease_out(ramp(t, h - .05, .09), 2))
    lh = max([h for h in hits if h <= t], default=-9)
    sx_ = 6 * math.exp(-(t - lh) * 14) * math.sin((t - lh) * 70) if t >= lh > 0 else 0.0
    o.append(grave(GR_X[kind], FL, kind, 1.0, t, ticks, n if n else 0, steam=steam, seed=hash(kind) % 50, shake_x=sx_))
    for h in hits:          # мел крошится на каждой палочке
        if 0 <= t - h < .4:
            o.append(PR.dust_puff(GR_X[kind] + (hits.index(h) - 1.5) * 30, FL - 40, .35, clamp((t - h) / .4), seed=hits.index(h)))
    if ghost is not None:
        o.append(ghost)
    if tumble is not None:
        o.append(tumble)
    o.append(extra)
    u = ease_out(ramp(t, a - .05, .45), 3)
    fx, fy, fs = cam_from
    cx = fx + (GR_X[kind] - fx) * u
    cy = fy + (FL - 150 - fy) * u
    s = fs + (2.55 - fs) * u + .12 * ease_io(ramp(t, a + .45, b - a))
    dx, dy = shake(t, lh, 7) if lh > 0 else (0, 0)
    return view("".join(o), cx + dx, cy + dy, s, 0, over=rain(t, .8, seed=2))


def ghost_svg(x, y, t, u, kind="dumbbell"):
    """Душа плана: прозрачный значок с нимбом поднимается и машет."""
    if u <= .01:
        return ""
    yy = y - 150 * ease_out(u, 2)
    sw = 10 * math.sin(t * 6)
    o = tf(icon(kind).replace(ICON, "#ffffff").replace(ICON_HI, "#ffffff"), 0, 0, 1.0, sw)
    o += f'<ellipse cx="0" cy="-70" rx="46" ry="12" fill="none" stroke="#ffe27a" stroke-width="7"/>'
    for s_ in (-1, 1):      # крылышки
        o += blob(ellipse_pts(s_ * 82, -10, 30, 18, 12, rot=s_ * 25 + 15 * math.sin(t * 14)), "#ffffff", .8)
    return f'<g opacity="{.85 * clamp(u * 3):.3f}">{tf(o, x, yy, .9)}</g>'


def frame_s04(t):
    g = ghost_svg(GR_X["dumbbell"], FL - 150, t, ramp(t, W(11) - .1, .6))
    return grave_close(t, "s04", "dumbbell", 4, 10, (GR_X["dumbbell"] - 200, FL - 300, 1.6), ghost=g)


def frame_s05(t):
    st = 1.0 - smooth(W(16) + .2, W(16) + .6, t)             # пар над чашкой гаснет на «два»
    return grave_close(t, "s05", "flag", 2, 16, (GR_X["flag"] - 320, FL - 140, 1.9), steam=st)


def tumbleweed(x, y, t, k=1.0):
    o = ""
    rs = np.random.RandomState(9800)
    for j in range(9):
        a0 = rs.uniform(0, 6.28)
        pts = [(math.cos(a0 + q * .7) * rs.uniform(30, 60), math.sin(a0 + q * .7) * rs.uniform(30, 60)) for q in range(6)]
        o += line(pts, 3.4, "#8a6a3a", taper=.3, wmin=.4, seed=9810 + j)
    return tf(o, x, y, k, t * 400)


def frame_s06(t):
    u = ramp(t, W(23) - .3, 1.3)
    tw = tumbleweed(GR_X["moon"] - 420 + 840 * u, FL - 40 - 60 * abs(math.sin(u * 9)), t, .9) if 0 < u < 1 else None
    return grave_close(t, "s06", "moon", 0, 20, (GR_X["moon"] + 280, FL - 200, 1.9), tumble=tw)


# ═════════════════════════ s07: «ушли рано, ушли молча» — шапочку долой, капля по камню ═════════════════════════
def frame_s07(t):
    a, b = T0("s07"), T1("s07")
    drip = ramp(t, W(30) - .15, .9)
    o = [yard_bg(t), yard_row(t, drip=drip)]
    cap = ease_io(ramp(t, stress(27, .1), .55))
    cx, cg, ck = CAT_POS
    o.append(cat_priest(cx - 230, cg, ck, t, cat_st(t, look=(-.2, .6), blink_at=(a + .3,)), cap=cap, nod=.6 * cap))
    o.append(dima(DIMA_POS[0] - 130, DIMA_POS[1], DIMA_POS[2], t, "cry", .3 + .3 * math.sin(t * 6), tears=.6)[0])
    u = ease_io(ramp(t, W(28) - .2, b - W(28) + .2))
    cxc = 600 + 220 * u
    cyc = 1180 - 120 * u
    s = 1.4 + .5 * u
    return view("".join(o), cxc, cyc, s, 0, over=rain(t, .7, seed=3))


# ═════════════════════════ s08: призыв ═════════════════════════
def frame_s08(t):
    import story_cta_tg as tg
    press = W(33) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=os.path.join(STORY, "common"))


# ═════════════════════════ росток, лейка, цветок ═════════════════════════
def sprout(x, y, k, u, t, leaves=1.0, bud=0.0):
    """Росток из земли (центр низа), u 0…1 — растёт."""
    if u <= .01:
        return ""
    h = 150 * ease_out(u, 2)
    sw = 6 * math.sin(t * 3)
    o = line([(0, 0), (sw * .3, -h * .5), (sw, -h)], 9, "#4f9a3a", taper=.1, wmin=.7, seed=9900)
    for j, (yy, s_) in enumerate(((.55, -1), (.8, 1))):
        lu = clamp((u - .3 - .2 * j) / .4) * leaves
        if lu > .01:
            px, py = sw * yy, -h * yy
            lf = [(0, 0), (s_ * 30, -18), (s_ * 62, -6), (s_ * 34, 12)]
            o += tf(shape(lf, "#7cc35c", line([(0, 0), (s_ * 50, -6)], 2.4, "#4f9a3a", seed=9902 + j), w=3.6, seed=9901 + j), px, py, lu, -s_ * 10)
    if bud > .01:
        o += tf(flower_head(t), sw, -h, bud)
    return tf(o, x, y, k)


def flower_head(t):
    o = ""
    for j in range(6):
        a = j * 60 + 8 * math.sin(t * 2)
        o += tf(shape(ellipse_pts(0, -26, 16, 26, 12), "#ff9fb8", "", w=3.4, seed=9910 + j), 0, 0, 1.0, a)
    o += shape(ellipse_pts(0, 0, 16, 16, 12), "#ffd34d", "", w=3.4, seed=9920)
    return o


def flower_svg(x, y, k, t):
    return sprout(x, y, k, 1.0, t, 1.0, 1.0)


def watering_can(x, y, k=1.0, rot=0.0, pour=0.0, t=0.0):
    o = shape(lib.rrect(-60, -50, 50, 40, 14), "#5fb7c9", blob(lib.rect_pts(10, -50, 50, 40), "#4497a8", .7), w=4.4, seed=9930)
    o += shape([(40, -10), (120, -60), (128, -48), (50, 16)], "#5fb7c9", "", w=4, seed=9931)
    o += line([(-50, -40), (-60, -90), (20, -90), (30, -50)], 7, INK, taper=0, wmin=1, seed=9932)
    if pour > .01:
        for j in range(6):
            ph = (t * 3 + j / 6) % 1
            o += PR.drop(124 + 30 * ph, -50 + 160 * ph, .45 * pour)
    return tf(o, x, y, k, rot)


# ═════════════════════════ s09: «оживляем по одному плану в неделю, без силы воли» ═════════════════════════
def frame_s09(t):
    a, b = T0("s09"), T1("s09")
    sunu = .35 * ramp(t, a, b - a)
    o = [yard_bg(t, sunu)]
    gx = GR_X["book"]
    for nm in ("book", "dumbbell"):
        o.append(grave(GR_X[nm], FL, nm, 1.0, t, [1] * 4 if nm == "dumbbell" else None, 4 if nm == "dumbbell" else 0, sun=sunu, seed=hash(nm) % 50))
    su = ramp(t, stress(40, .3), .7)
    o.append(sprout(gx + 70, FL + 20, 1.3, su, t, bud=pop(t, W(46) - .1, .3) if t > W(46) - .1 else 0))
    pour = smooth(a, a + .2, t) * (1 - smooth(W(44), W(44) + .3, t))
    o.append(cat_priest(gx + 330, FL + 180, 1.0, t, cat_st(t, look=(-.8, .5), smile=1.0 if t > W(41) else 0.0), cap=1.0))
    o.append(watering_can(gx + 210, FL - 60, 1.0, -30 * pour - 5, pour, t))
    ds, res = dima(gx - 260, FL + 230, .58, t, dict(people.EXPR["dima"]["hope"], look=(.8, .4)), 0.0, tissue=0.0, arms=None)
    o.append(ds)
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), gx + 40 + 30 * u, FL - 110, 1.75 + .15 * u + .06 * bump(t, W(41)), 0, over=rain(t, 1 - 3 * sunu, seed=4))


# ═════════════════════════ s10: «Почему они умирают?» ═════════════════════════
def frame_s10(t):
    a, b = T0("s10"), T1("s10")
    o = [yard_bg(t), yard_row(t)]
    ex = dict(people.EXPR["dima"]["puzzled"], look=(.7, -.2))
    ds, res = dima(DIMA_POS[0] + 40, DIMA_POS[1], DIMA_POS[2], t, ex, 0.0, tissue=0.0, head_ang=.12 * math.sin(t * 3))
    o.append(ds)
    cx, cg, ck = CAT_POS
    o.append(cat_priest(cx, cg, ck, t, cat_st(t, look=(-.8, -.4), tilt=-12 * smooth(W(49), W(49) + .3, t)), cap=1.0))
    hx, hy = res["head"]
    o.append(PR.question_mark(hx + 30, hy - 260, 1.4 * pop(t, W(49) - .05), 1.0, col="#f2b84b"))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560 - 40 * u, 1000 + 30 * u, 1.05 + .12 * u + .05 * bump(t, W(49)), 0, over=rain(t, .6, seed=5))


# ═════════════════════════ ступени: огромная и маленькая ═════════════════════════
STEP_X = 640.0


def frame_s11(t):
    a, b = T0("s11"), T1("s11")
    grow = ease_out(ramp(t, W(54) - .05, .45), 3)
    o = [yard_bg(t)]
    o.append(PR.step_wall(STEP_X, FL + 120, 1.15, .75 + .25 * grow, t=t, seed=1))
    ex = dict(people.EXPR["dima"]["scared"], look=(.5, -1.0))
    ds, _ = dima(STEP_X - 330, FL + 120, .52, t, ex, 0.0, tissue=0.0, head_ang=-.3 - .1 * grow, lean=-.06)
    o.append(ds)
    u = ease_io(ramp(t, a, b - a))
    tilt = smooth(W(54) - .1, W(54) + .5, t)
    cy = 900 - 260 * tilt
    dx, dy = shake(t, W(54) + .2, 10)
    return view("".join(o), STEP_X - 130 + dx, cy + dy, .82 - .05 * u, 0, over=rain(t, .5, seed=6))


def head_icon(x, y, k, calm=1.0, t=0.0, fear=0.0):
    """Силуэт головы в профиль с облачком внутри: calm — белое пушистое, fear — грозовая туча дрожит, молния."""
    o = shape([(-60, 120, 1), (-70, 40), (-96, -10), (-96, -80), (-60, -140), (10, -160), (80, -120), (104, -50), (96, 10), (120, 40), (100, 52),
               (98, 90), (60, 100), (50, 130, 1)], "#f3e6d6", "", w=5, seed=9950)
    jit = 5 * fear * math.sin(t * 60)
    if fear < .5:
        o += PR.cloud(0 + jit, -10, 150, 100, 1 + .04 * math.sin(t * 3), 1 + .04 * math.sin(t * 3 + 1), seed=3, col="#ffffff", ink_w=3.6)
    else:
        o += PR.storm(jit, -10, 160, 90, 1.0, 1.0, seed=3, flash=.5 + .5 * math.sin(t * 25))
        o += PR.bolt(-10 + jit, -10, 10, 70, .6, 14, seed=2)
    return tf(o, x, y, k)


def frame_s12(t):
    a, b = T0("s12"), T1("s12")
    o = [yard_bg(t)]
    o.append(PR.step_wall(STEP_X + 220, FL + 120, 1.0, 1.0, t=t, seed=1))
    o.append(PR.step_wall(STEP_X - 200, FL + 120, .9, 0.0, glow_=.6, t=t, seed=2))      # маленькая ступенька
    step = ease_io(ramp(t, W(57) - .1, .5))
    ex = dict(people.EXPR["dima"]["calm_smile"], look=(.3, .6))
    sx = STEP_X - 430 + 150 * step
    ds, _ = dima(sx, FL + 120 - 72 * step + 30 * math.sin(math.pi * step) * 0, .52, t, ex, 0.0, tissue=0.0, lean=.05)
    o.append(ds)
    o.append(head_icon(STEP_X - 280, FL - 560, 1.25 * pop(t, a + .05), 1.0, t))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), STEP_X - 220 + 30 * u, FL - 330, 1.05 + .1 * u, 0, over=rain(t, .4, seed=7))


def frame_s13(t):
    a, b = T0("s13"), T1("s13")
    o = [yard_bg(t)]
    slam = ease_in_(ramp(t, stress(64, .2) - .18, .18))
    o.append(PR.step_wall(STEP_X + 120, FL + 120, 1.15, 1.0, t=t, seed=1))
    # на «хоронит» перед ступенью падает плита-надгробие
    if slam > .01:
        gy = FL + 130 - 900 * (1 - slam)
        o.append(grave(STEP_X + 120, gy, "dumbbell", 1.5, t, None, 0, seed=7).replace("icon", "icon"))
    hit = stress(64, .2)
    if t >= hit:
        o.append(PR.dust_puff(STEP_X - 60, FL + 120, 1.2, clamp((t - hit) / .5), seed=3))
        o.append(PR.dust_puff(STEP_X + 300, FL + 120, 1.1, clamp((t - hit) / .5), seed=5))
    ex = dict(people.EXPR["dima"]["scared"], look=(.6, -.6))
    ds, _ = dima(STEP_X - 420, FL + 120, .5, t, ex, 0.0, tissue=0.0, lean=-.12 - .1 * smooth(hit, hit + .2, t))
    o.append(ds)
    o.append(head_icon(STEP_X - 300, FL - 560, 1.25, 0.0, t, fear=1.0))
    dx, dy = shake(t, hit, 22)
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), STEP_X - 140 + dx, FL - 340 + dy, .9 + .08 * u + .08 * bump(t, hit), 0, over=rain(t, .5, seed=8))


def ease_in_(u):
    return u * u


# ═════════════════════════ s14: «Дима оживил один план» — росток из надгробия-флажка ═════════════════════════
def frame_s14(t):
    a, b = T0("s14"), T1("s14")
    sunu = .4 + .3 * ramp(t, a, b - a)
    o = [yard_bg(t, sunu)]
    gx = GR_X["flag"]
    o.append(grave(gx, FL, "flag", 1.0, t, [1, 1], 2, wet=1 - sunu, sun=sunu, seed=hash("flag") % 50, steam=smooth(W(67), W(67) + .4, t)))
    hit = stress(67, .3)
    su = ramp(t, hit - .1, .6)
    o.append(sprout(gx - 95, FL + 20, 1.4, su, t))
    if t >= hit - .1:
        o.append(PR.dust_puff(gx - 95, FL + 20, .7, clamp((t - hit + .1) / .45), seed=2))
        o.append(PR.sparkles(gx - 95, FL - 120, 1.0, smooth(hit, hit + .3, t), t, seed=4))
    ex = dict(people.EXPR["dima"]["wonder81"] if "wonder81" in people.EXPR["dima"] else people.EXPR["dima"]["hope"], look=(.6, .6))
    ds, _ = dima(gx - 400, FL + 220, .5, t, ex, 0.0, tissue=0.0)
    o.append(ds)
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), gx - 170, FL - 180 + 20 * u, 1.85 + .2 * u + .06 * bump(t, hit), 0, over=rain(t, .15, seed=9))


# ═════════════════════════ s15: «одна минута английского в день» ═════════════════════════
def flag_card(x, y, k=1.0, rot=0.0):
    """Карточка-флажок без букв: синее поле, белый и красный крест с диагоналями."""
    cid = lib.uid("fc")
    pts = lib.rect_pts(-90, -60, 90, 60)
    inner = rect(-100, -70, 100, 70, "#2a4f9e")
    for a_ in (33.7, -33.7):
        inner += f'<rect x="-120" y="-10" width="240" height="20" fill="#ffffff" transform="rotate({a_})"/>'
        inner += f'<rect x="-120" y="-4" width="240" height="8" fill="#d83a3a" transform="rotate({a_})"/>'
    inner += rect(-100, -18, 100, 18, "#ffffff") + rect(-16, -70, 16, 70, "#ffffff")
    inner += rect(-100, -10, 100, 10, "#d83a3a") + rect(-9, -70, 9, 70, "#d83a3a")
    o = (f'<defs><clipPath id="{cid}"><path d="{lib.ink_closed(pts, 0.1, seed=1) if False else "M-90,-60 L90,-60 L90,60 L-90,60 Z"}"/></clipPath></defs>'
         f'<g clip-path="url(#{cid})">{inner}</g>')
    o += f'<path d="M-90,-60 L90,-60 L90,60 L-90,60 Z" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
    return tf(o, x, y, k, rot)


def frame_s15(t):
    a, b = T0("s15"), T1("s15")
    sunu = .7 + .3 * ramp(t, a, b - a)
    o = [yard_bg(t, sunu)]
    gx = GR_X["flag"]
    o.append(grave(gx + 160, FL, "flag", 1.0, t, [1, 1], 2, wet=0, sun=sunu, seed=hash("flag") % 50, steam=1.0))
    o.append(sprout(gx + 65, FL + 20, 1.4, 1.0, t, bud=ease_out(ramp(t, W(72), .5), 2)))
    sc = .6
    x = gx - 260
    ground = FL + 260
    y = stand_y(ground, sc)
    card = (x + 260 * sc, y - 520 * sc + 10 * math.sin(t * 4))
    sw = (x - 230 * sc, y - 440 * sc)
    arms = {"n": ("ik", (card[0] - 60, card[1] + 50), -1), "f": ("ik", (sw[0] + 30, sw[1] + 60), 1)}
    hands = {"n": {"dir": (.6, -.8), "curl": (.55, .55, .6, .62), "thumb": .5}, "f": {"dir": (-.3, -1), "curl": (.6, .6, .65, .7), "thumb": .5}}
    ex = dict(people.EXPR["dima"]["cheerful"], look=(.7, -.3))
    base = people.figure("dima", x, y, sc, expr=ex, lean=.02, head_ang=.08, arms=arms, hands=hands, feet=people.stand_kw(x, y, sc)["feet"],
                         layers=("legs", "pelvis", "arm_f", "body"))
    near = people.figure("dima", x, y, sc, expr=ex, lean=.02, head_ang=.08, arms=arms, hands=hands, feet=people.stand_kw(x, y, sc)["feet"],
                         layers=("arm_n",))
    hand_a = 360 * ease_io(ramp(t, W(71), 1.1))
    o.append(base["svg"])
    o.append(PR.stopwatch(sw[0], sw[1] - 20, .55, hand_a, hand_a, bump(t, W(71) - .05), t, seed=1))
    o.append(flag_card(card[0], card[1], 1.1 * pop(t, a + .02), -8 + 4 * math.sin(t * 3)))
    o.append(near["svg"])
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), gx - 120 + 30 * u, FL - 230, 1.35 + .1 * u + .05 * bump(t, W(72)), 0)


# ═════════════════════════ s16: кот спит на могиле «сна» ═════════════════════════
def frame_s16(t):
    a, b = T0("s16"), T1("s16")
    sunu = 1.0
    o = [yard_bg(t, sunu)]
    px = GR_X["pillow"]
    o.append(grave(GR_X["moon"], FL, "moon", 1.0, t, None, 0, wet=0, sun=sunu, seed=hash("moon") % 50))
    o.append(pillow_grave(px, FL, 1.25, t, sun=sunu))
    o.append(CT.curl(px - 40, FL + 40, 1.05, dict(squint=.6 * bump(t, W(81), .2, .8), breath=1.3, turn=-.1), t))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), px - 80 + 40 * u, FL - 160, 1.55 + .25 * u + .05 * bump(t, W(81)), 0)


# ═════════════════════════ s17: петля — ракурс хука, солнце, цветок ═════════════════════════
def frame_s17(t):
    a, b = T0("s17"), T1("s17")
    o = [yard_bg(t, 1.0), yard_row(t, 1.0, flower=1.0, pillow_z=True, wet=0)]
    cx, cg, ck = CAT_POS
    o.append(CT.curl(GR_X["pillow"] - 40, FL + 40, .78, dict(breath=1.3, squint=.5), t))
    o.append(cat_priest(cx, cg, ck, t, cat_st(t, look=(-.6, .1), smile=1.0, blink_at=(b - .9,)), cap=0.0) if False else "")
    ex = dict(people.EXPR["dima"]["calm_smile"], look=(.6, .2))
    sc = DIMA_POS[2]
    x = DIMA_POS[0]
    y = stand_y(DIMA_POS[1], sc)
    card = (x + 250 * sc, y - 470 * sc)
    arms = {"n": ("ik", (card[0] - 50, card[1] + 50), -1), "f": ("ang", .14, .25)}
    hands = {"n": {"dir": (.6, -.8), "curl": (.55, .55, .6, .62), "thumb": .5}}
    base = people.figure("dima", x, y, sc, expr=ex, arms=arms, hands=hands, feet=people.stand_kw(x, y, sc)["feet"], layers=("legs", "pelvis", "arm_f", "body"))
    near = people.figure("dima", x, y, sc, expr=ex, arms=arms, hands=hands, feet=people.stand_kw(x, y, sc)["feet"], layers=("arm_n",))
    o += [base["svg"], flag_card(card[0], card[1], .9, -6 + 3 * math.sin(t * 3)), near["svg"]]
    o.append("".join(grave(x_ - (560 - 300) * .8, FG_Y, kind, FG_K, t, wet=0, sun=1.0, seed=30 + j) for j, (x_, kind) in enumerate(FG)))
    u = ease_io(ramp(t, a, b - a))
    cx0, cy0, s0, r0 = hook_cam_scene(2.0)
    return view("".join(o), cx0 + 120 * (1 - u), cy0, s0 + .06 * (1 - u), 0)


FRAMES = {k[6:]: v for k, v in dict(globals()).items() if k.startswith("frame_s")}


def frame(sid, t):
    if sid != "s08":
        lib.DEFS.clear()
    return FRAMES[sid](t)
