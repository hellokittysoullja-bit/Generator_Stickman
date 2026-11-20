"""Рилс 93 «Укради мой вечер», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Сквозной образ: кот-воришка в чёрной маске с мешком «крадёт» вечер и раскладывает ритуал по местам, как фокусник;
четыре огонька-шага сверху (screen) загораются по одному. Рассказ от первого лица, в кадре Дима.
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
    if a is None:
        return 0.0
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.35, f=11.0):
    if a is None or NOCAM:
        return 0.0, 0.0
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


NIGHT_BG = "#1d2347"


def view(body, cx, cy, s, rot=0.0, over="", bg=NIGHT_BG):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


# ═════════════════════════ огоньки-шаги ритуала (экранный слой) ═════════════════════════
STEP_WORDS = (25, 47, 67, 76)               # «Первое», «Второе», «Третье», «Четвёртое»


def steps(t, y=250.0):
    """Четыре огонька сверху: шаг загорается на своём слове (пружина + искры); до первого шага слоя нет."""
    if t < W(STEP_WORDS[0]) - .05 or NOCAM:
        return ""
    o = []
    for i, wi in enumerate(STEP_WORDS):
        x = 540 + (i - 1.5) * 150
        a = W(wi)
        on = t >= a
        p = pop(t, a, .28) if on else 0.0
        o.append(shape(ellipse_pts(x, y, 46, 46, 20), "#3a3f63", "", w=4, seed=40 + i))
        if on:
            o.append(PR.glow(x, y, 120, .55 + .35 * bump(t, a, .05, .4), "#ffcf6a"))
            o.append(tf(shape(ellipse_pts(0, 0, 40, 40, 20), "#ffc24a", blob(ellipse_pts(-10, -12, 16, 10, 10), "#fff1b8", .9), w=4, seed=50 + i),
                        x, y, p))
            o.append(PR.sparkles(x, y, 1.0, bump(t, a, .05, .45), t, seed=i, n=4, r=70))
    return "".join(o)


# ═════════════════════════ ночная комната ═════════════════════════
FL = 1300.0
WALL, WALL_ST, FLOOR_C, FLOOR_SH = "#2b3360", "#3a4378", "#4a3a4e", "#3a2c40"
WARM_WALL, WARM_ST, WARM_FLOOR = "#b8673a", "#c97a48", "#7a4630"


def window(x0, y0, x1, y1, sky="#141a3e", t=0.0, moon=None, open_=0.0, trees=0.0):
    o = [shape(lib.rect_pts(x0 - 18, y0 - 18, x1 + 18, y1 + 18), "#e9e1d0", "", w=4.4, seed=3400)]
    inner = [rect(x0, y0, x1, y1, sky)]
    if trees > .01:                          # осенний лес за окном
        for j in range(6):
            tx = x0 + 30 + j * (x1 - x0 - 40) / 5
            ty = y1 + 10
            inner.append(rect(tx - 6, ty - 160, tx + 6, ty, "#3b2a24", trees))
            for q, (dx, dy, r, c) in enumerate(((0, -200, 70, "#d9762b"), (-40, -160, 50, "#c9502a"), (40, -165, 52, "#e8a33a"))):
                inner.append(blob(ellipse_pts(tx + dx, ty + dy - 20 * (j % 2), r, r * .85, 12), c, trees))
    if moon is not None:
        inner.append(PR.glow(moon[0], moon[1], 120, .6, "#f4f0dc"))
        inner.append(f'<circle cx="{moon[0]:.1f}" cy="{moon[1]:.1f}" r="34" fill="#f4f0dc"/>'
                     f'<circle cx="{moon[0] + 15:.1f}" cy="{moon[1] - 9:.1f}" r="29" fill="{sky}"/>')
        for i, (sx, sy) in enumerate(((x0 + 50, y0 + 60), (x0 + 120, y1 - 70), (x1 - 60, y1 - 50), (x0 + 70, (y0 + y1) / 2))):
            inner.append(PR.star4(sx, sy, 9 + 4 * math.sin(t * 5 + i * 1.7), 1.0))
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o.append(f'<g clip-path="url(#{c})">{"".join(inner)}</g>')
    xm = (x0 + x1) / 2
    if open_ > .01:                          # правая створка распахивается внутрь (сжимается по ширине)
        o.append(line([(x0, (y0 + y1) / 2), (xm, (y0 + y1) / 2)], 6, "#e9e1d0", taper=0, wmin=1, seed=3402))
        o.append(line([(xm, y0), (xm, y1)], 6, "#e9e1d0", taper=0, wmin=1, seed=3401))
        o.append(f'<path d="{lib.ink_closed(lib.rect_pts(x0, y0, xm, y1), 4.0, seed=3403)}" fill="{INK}"/>')
        k = 1 - .82 * open_
        sash = (shape(lib.rect_pts(xm, y0, x1, y1), "#9fb7d8", "", w=4, seed=3404) +
                line([(xm, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], 6, "#e9e1d0", taper=0, wmin=1, seed=3405))
        o.append(f'<g opacity=".85" transform="translate({x1:.1f} 0) scale({k:.3f} 1) translate({-x1:.1f} 0)">{sash}</g>')
    else:
        o.append(line([(xm, y0), (xm, y1)], 6, "#e9e1d0", taper=0, wmin=1, seed=3401))
        o.append(line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], 6, "#e9e1d0", taper=0, wmin=1, seed=3402))
        o.append(f'<path d="{lib.ink_closed(lib.rect_pts(x0, y0, x1, y1), 4.0, seed=3403)}" fill="{INK}"/>')
    return "".join(o)


def room(t, x0=-1500.0, x1=2700.0, warm=0.0, win=True, open_=0.0, trees=0.0, masked=False):
    if masked:
        return ""
    wc, sc, fc = lib.mix(WALL, WARM_WALL, warm), lib.mix(WALL_ST, WARM_ST, warm), lib.mix(FLOOR_C, WARM_FLOOR, warm)
    o = [rect(x0, -1500, x1, FL, wc)]
    for i in range(int(x0 // 130), int(x1 // 130) + 1):          # обои: полосы с ромбиками
        xa = i * 130
        o.append(rect(xa, -1500, xa + 44, FL, sc, .9))
        for j in range(-6, 10):
            yy = j * 160 + (80 if i % 2 else 0)
            o.append(blob([(xa + 87, yy - 14), (xa + 97, yy), (xa + 87, yy + 14), (xa + 77, yy)], sc, .9))
    o.append(rect(x0, FL, x1, FL + 1500, fc))
    for i in range(int(x0 // 170), int(x1 // 170) + 1):
        xa = i * 170
        o.append(line([(xa, FL + 6), (xa + (xa - 540) * .7, FL + 900)], 2.4, lib.mix(FLOOR_SH, "#5e3424", warm), seed=20 + i % 9, op=.9))
    o.append(shape(lib.rect_pts(x0, FL - 26, x1, FL + 4), lib.mix("#3d4570", "#d9a070", warm), "", w=3.6, seed=3290))
    if win:
        o.append(window(780, 380, 1120, 820, lib.mix("#141a3e", "#2a2a55", warm), t, moon=(1040, 470), open_=open_, trees=trees))
    return "".join(o)


def tint(warm=0.0, cold=0.0, dark=0.0):
    """Свет комнаты поверх: тёплый (оранжевый, умножение), холодный яркий (белёсый), темнота."""
    o = ""
    if cold > .01:
        o += f'<rect x="-3000" y="-3000" width="7000" height="7000" fill="#e8f4ff" opacity="{.28 * cold:.3f}"/>'
    if warm > .01:
        o += f'<rect x="-3000" y="-3000" width="7000" height="7000" fill="#ffb060" opacity="{.42 * warm:.3f}" style="mix-blend-mode:multiply"/>'
    if dark > .01:
        o += f'<rect x="-3000" y="-3000" width="7000" height="7000" fill="#0b0d22" opacity="{.4 * dark:.3f}"/>'
    return o


# ═════════════════════════ предметы ═════════════════════════
PH_BODY, PH_SCREEN = "#2b2e35", "#cfe9ff"


def phone_up(x, y, k=1.0, rot=0.0, glow=1.0, scroll=0.0, feed=True, dim=0.0, charge=0.0):
    """Телефон экраном к зрителю (центр), без букв: цветные карточки ленты листаются; charge — зелёная молния зарядки."""
    o = []
    if glow > .01:
        o.append(PR.glow(x, y, 260 * k, .5 * glow, "#bfe8ff"))
    body = lib.T(lib.rrect(-60, -120, 60, 120, 18), x, y, k, rot)
    scr = lib.T(lib.rrect(-50, -106, 50, 106, 10), x, y, k, rot)
    inner = blob(scr, lib.mix(PH_SCREEN, "#3b4250", dim))
    if feed and charge < .5:
        for j in range(6):
            yy = -100 + ((j * 42 + scroll * 160) % 252) - 20
            card = lib.T(lib.rrect(-42, yy, 42, yy + 30, 6), x, y, k, rot)
            inner += blob(card, ("#ff8a7a", "#ffd166", "#7bd389", "#c9a7ff", "#ff9ec7", "#6cc4ff")[j], .9 * (1 - dim))
    if charge > .01:
        inner += blob(lib.T([(8, -60), (-26, 6), (-2, 6), (-10, 60), (26, -8), (2, -8)], x, y, k * (.6 + .4 * charge), rot), "#5fd16a")
    c = lib.clip_of(scr)
    o.append(shape(body, PH_BODY, f'<g clip-path="url(#{c})">{inner}</g>', w=4.0 * max(.6, k), seed=3600))
    return "".join(o)


def notebook(x, y, k=1.0, rot=0.0, open_=1.0, lines_=0.0, seed=0, t=0.0):
    """Блокнот (центр): открыт — две страницы с каракулями-волнами (lines_ 0…1 — сколько написано), закрыт — обложка."""
    if open_ < .5:
        cov = shape(lib.rrect(-110, -80, 110, 80, 10), "#e2574c", blob(lib.rrect(-110, 50, 110, 80, 8), "#b8423a", .7) +
                    line([(-80, -80), (-80, 80)], 4, "#b8423a", seed=1700 + seed), w=4.4, seed=1701 + seed)
        sy = 1 - 2 * open_ if open_ < .5 else 1
        return tf(f'<g transform="scale(1 {max(.15, abs(sy)):.3f})">{cov}</g>', x, y, k, rot)
    o = [shape(lib.rrect(-230, -90, 230, 90, 10), "#e2574c", "", w=4.4, seed=1702 + seed)]
    o.append(shape(lib.rrect(-218, -82, -4, 82, 6), "#fbf6e6", "", w=3.4, seed=1703 + seed))
    o.append(shape(lib.rrect(4, -82, 218, 82, 6), "#fbf6e6", "", w=3.4, seed=1704 + seed))
    n = 8
    for i in range(n):
        q = clamp(lines_ * n - i)
        if q <= 0:
            break
        px = -200 if i < 4 else 22
        yy = -58 + (i % 4) * 36
        L = 170 * q * (.75 + .25 * math.sin(i * 2.3))
        pts = [(px + L * j / 14, yy + 7 * math.sin(j * 1.9 + i)) for j in range(15)]
        o.append(line(pts, 4, "#4a5a8a", taper=.2, wmin=.6, seed=1710 + i + seed))
    return tf("".join(o), x, y, k * (1.0 if open_ >= 1 else .6 + .4 * open_), rot)


LEAF_COLS = ("#e07a2e", "#c9502a", "#e8a33a", "#b5452a", "#d99a2b")


def leaf(x, y, k=1.0, rot=0.0, i=0):
    """Осенний лист: остроконечный овал с прожилкой."""
    pts = [(-30, 0, 1)] + [(-30 + 60 * j / 8, -16 * math.sin(math.pi * j / 8)) for j in range(1, 8)] + [(30, 0, 1)] + \
          [(30 - 60 * j / 8, 14 * math.sin(math.pi * j / 8)) for j in range(1, 8)]
    o = shape(pts, LEAF_COLS[i % len(LEAF_COLS)], line([(-34, 0), (26, 0)], 2.2, "#7a3a1a", seed=140 + i % 5), w=2.8, seed=141 + i % 7)
    return tf(o, x, y, k, rot)


def lamp_warm(x, y, k=1.0, on=1.0, t=0.0):
    return PR.night_lamp(x, y, k, on_u=on, t=t)


def sack(x, y, k=1.0, t=0.0, squash=0.0, open_=0.0, rot=0.0):
    """Большой мешок вора (центр дна): холщовый, заплатка, верёвка на горловине; open_ — горловина раскрыта (свет изнутри)."""
    bw = 1 + .12 * squash
    bh = 1 - .12 * squash
    body = [(-150 * bw, -10), (-170 * bw, -150 * bh), (-120 * bw, -300 * bh), (-50, -360 * bh), (50, -360 * bh), (120 * bw, -300 * bh),
            (170 * bw, -150 * bh), (150 * bw, -10), (0, 6)]
    inner = blob([(40, -350 * bh), (160 * bw, -160 * bh), (150 * bw, -10), (60, 0), (90, -180 * bh)], "#a37a48", .8)
    inner += shape(lib.rrect(-90, -200 * bh, -20, -130 * bh, 8), "#7c8fb0", line([(-84, -196 * bh), (-26, -134 * bh)], 2.4, "#5a6a88", seed=1801), w=3,
                   seed=1802)
    for j in range(5):
        inner += line([(-60 + 10 * j, -130 * bh + 3 * j), (-50 + 10 * j, -120 * bh)], 2, "#6a4c2c", seed=1803 + j)
    o = []
    if open_ > .01:
        o.append(PR.glow(0, -380 * bh, 200, .8 * open_, "#ffd98a"))
    o.append(shape(body, "#c49a64", inner, w=5, seed=1810))
    neck = [(-50, -360 * bh), (-40 - 30 * open_, -420 * bh - 20 * open_), (40 + 30 * open_, -420 * bh - 20 * open_), (50, -360 * bh)]
    o.append(shape(neck, "#b58a56", blob(ellipse_pts(0, -420 * bh - 20 * open_, 40 * open_ + .1, 10 * open_ + .1, 12), "#ffe7a8", open_), w=4.4,
                   seed=1811))
    o.append(line([(-56, -366 * bh), (0, -372 * bh), (56, -366 * bh)], 7, "#6a4c2c", seed=1812))
    return tf("".join(o), x, y, k, rot)


def mask_art(turn=0.0, tie=0.0):
    """Чёрная маска вора в координатах кота: полоса с двумя прорезями под глаза и хвостики узла справа."""
    FX = 22 * turn
    band = [(728, 1040), (790, 1026), (836, 1032), (882, 1026), (944, 1040), (948, 1100), (900, 1110), (836, 1098), (772, 1110), (724, 1100)]
    d = lib.fill_d([(p[0] + FX * .6, p[1]) for p in band])
    for sx in (-1, 1):
        ex = CT.CX + FX + sx * 44 - 4 * turn
        d += " " + lib.fill_d(ellipse_pts(ex, 1072, 40, 34, 16))
    o = f'<path d="{d}" fill="#141418" fill-rule="evenodd" stroke="{INK}" stroke-width="3"/>'
    o += blob([(790, 1040), (836, 1036), (870, 1040), (836, 1046)], "#4a4a58", .7)
    w = 10 * math.sin(tie)
    for j, dy in enumerate((-8, 14)):
        o += shape([(944, 1062 + dy * .3), (990, 1048 + dy + w), (1010, 1060 + dy + w * 1.3), (968, 1076 + dy * .4)], "#141418", "", w=3, seed=1820 + j)
    return o


def cat(x, y, k, t, st=None, mask=0.0):
    """Кот рилсов; mask 1 — в маске вора (маска на голове: следует наклону), 0…1 при снятии — маска уезжает вверх-вправо."""
    st = dict(dict(look=(-.4, -.2), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    if mask > .01:
        m = mask_art(st.get("turn", 0.0), t * 9)
        if mask < 1:
            u = 1 - mask
            m = f'<g opacity="{mask:.3f}" transform="translate({160 * u:.1f} {-260 * u:.1f}) rotate({40 * u:.1f} 836 1072)">{m}</g>'
        st["mouth_item"] = st.get("mouth_item", "") + m
    return CT.draw(x, y, k, st, t)


def cat_sneak(x, y, k, t, period=.42, st=None, mask=1.0, sack_on=True, sack_open=0.0, between=""):
    """Кот-воришка крадётся на цыпочках боком: высокий подскок на пальцах, плечи подняты, хитрый взгляд; мешок за плечом."""
    ph = (t / period) % 1.0
    s = math.sin(2 * math.pi * ph)
    lift = abs(math.sin(math.pi * ph)) * 22 * k
    st = dict(dict(walk=ph, rot=4 * s, tail=14 * math.sin(2 * math.pi * ph * .5) - 10, smug=.8, look=(-.9, -.1), turn=-.3, sy=1.04 + .03 * s,
                   ), **(st or {}))
    o = []
    if sack_on:
        o.append(sack(x - 175 * k, y - 60 * k - lift * .8, 1.1 * k, t, squash=.5 + .5 * s, open_=sack_open, rot=-14 - 5 * s))
    o.append(between)
    o.append(cat(x, y - lift, k, t, st, mask))
    return "".join(o)


def falling(item, x0, y0, t, a, x1, ground, spin=200.0):
    """Предмет выпадает в момент a из (x0, y0): дуга вниз по параболе, удар об пол, отскок; дальше лежит. item(x, y, rot, glow)."""
    u = t - a
    if u < 0:
        return ""
    T = math.sqrt(2 * (ground - y0) / 2600)
    if u < T:
        e = u / T
        return item(x0 + (x1 - x0) * e, y0 + (ground - y0) * e * e, spin * e, 1.0)
    v = u - T
    hop = 60 * math.exp(-v * 6) * abs(math.sin(v * 14))
    return item(x1, ground - hop, spin, 1.0 + .6 * math.exp(-v * 4))


def item_lamp(x, y, rot, g, k=.8):
    return PR.glow(x, y - 120, 300, .8 * g, "#ffb347") + tf(PR.night_lamp(0, 0, k, on_u=1.0, t=0.0), x, y, 1.0, rot * .25)


def item_note(x, y, rot, g):
    return PR.glow(x, y - 40, 240, .7 * g, "#fff2c0") + notebook(x, y - 60, .65, rot * .5, open_=0.0)


def item_phone(x, y, rot, g):
    cab = line([(x + 10, y - 10), (x - 40, y + 20), (x - 120, y + 10), (x - 160, y + 26)], 6, "#f2efe6", seed=1830)
    return cab + phone_up(x, y - 60, .8, rot * .6 + 70, glow=1.3 * g, scroll=0.0, feed=True)


def dima_sleep(bx, t, expr="bliss", cover="chest", seed=0, bk=1.3, roll=0.0, sit=0.0, col="blue", arm="in"):
    o = [PR.bed(bx, FL, bk, seed=seed)]
    d = people.dima_bed(bx - 60, FL - 118 * bk - 30, .6, expr=expr, t=t, cover=cover, seed=seed, roll=roll, sit=sit, col=col, arm=arm)
    o.append(d["svg"])
    return "".join(o), d


def nightstand(x, k=1.0, item=""):
    o = shape(lib.rrect(x - 85 * k, FL - 210 * k, x + 85 * k, FL, 8), "#7a5638",
              blob(lib.rrect(x - 85 * k, FL - 210 * k, x + 85 * k, FL - 190 * k, 6), "#946a46") +
              line([(x - 70 * k, FL - 120 * k), (x + 70 * k, FL - 120 * k)], 3, "#5a3e28", seed=1840) +
              blob(ellipse_pts(x, FL - 165 * k, 12 * k, 6 * k, 10), "#d8b070"), w=4.4, seed=1841)
    return o + item


# ═════════════════════════ хук: s01–s03 ═════════════════════════
HIT01 = stress(0, .35)                       # «уКРАди»: из мешка вылетает блокнот, тряска
BX = -150.0                                   # кровать Димы (кот крадётся мимо неё на переднем плане)
CAT_Y = FL + 120


def cat_x(t):
    return -220 + 430 * t


SACK_DROPS = [(item_lamp, -.15, -120.0), (item_note, HIT01, 40.0), (item_phone, .78, 120.0), (item_lamp, 1.55, 60.0), (item_note, 2.1, -40.0)]


def hook_world(t, masked=False):
    o = [room(t, x0=-1600, x1=2600, masked=masked, win=False)]
    if not masked:
        o.append(window(-640, 360, -300, 800, "#141a3e", t, moon=(-360, 450)))
        o.append(window(400, 360, 740, 800, "#141a3e", t, moon=None))
    g, d = dima_sleep(BX, t, "bliss")
    o.append(nightstand(BX - 480))
    o.append(g)
    o.append(PR.zzz(d["head"][0] + 40, d["head"][1] - 140, 1.0, t, 1.0))
    items = []
    for fn, a, dx in SACK_DROPS:             # предметы выпадают из дырки мешка и светятся на полу
        x0 = cat_x(a) - 200
        items.append(falling(fn, x0, CAT_Y - 200, t, a, x0 + dx - 120, CAT_Y + 10, spin=220 if dx > 0 else -200))
    x = cat_x(t)
    o.append(cat_sneak(x, CAT_Y, 1.0, t, sack_open=.4 + .6 * bump(t, HIT01, .05, .3), between="".join(items)))
    o.append(PR.sparkles(x - 200, CAT_Y - 560, 1.6, bump(t, HIT01, .04, .35), t, seed=3, n=5, r=140))
    return "".join(o)


def hook_cam_scene(t):
    """Камера сцены (часть рисунка): летит за котом, чуть сверху вниз."""
    return cat_x(t) - 120, FL - 130 + 20 * math.sin(t * 2.2), 1.72


def hook_wrap(body, t, hit, bg=NIGHT_BG):
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    piv = 960.0
    tr = f"translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-piv})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<use href="#hk93" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk93">{body}</g></g>{blur}'


MASK_F = '<filter id="mk93"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def frame_s01(t):
    cx, cy, s = hook_cam_scene(t)
    if MASK:
        lib.DEFS.append(MASK_F)
        return lib.svg(f'<rect width="1080" height="1920" fill="#000"/><g transform="{lib.cam(cx, cy, s, 0)}"><g filter="url(#mk93)">'
                       f'{hook_world(t, True)}</g></g>')
    body = hook_world(t)
    dx, dy = shake(t, HIT01, 14)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{body}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{NIGHT_BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + title(t))


def frame_s02(t):
    """«ритуал, после которого»: ракурс у кровати — Дима спит крупно, кот-воришка крадётся на цыпочках вдоль кровати
    на переднем плане, мешок светится, за ним по полу остаются светящиеся предметы; камера летит за котом."""
    a, b = T0("s02"), T1("s02")
    u = ease_io(ramp(t, a, b - a))
    bx = 700.0
    o = [room(t, x0=-800, x1=2200, win=False)]
    o.append(window(560, 380, 900, 820, "#141a3e", t, moon=(820, 470)))
    o.append(nightstand(bx - 480, 1.0, item_lamp(bx - 480, FL - 210, 0, 1.0, .6)))
    g, d = dima_sleep(bx, t, "bliss")
    o.append(g)
    o.append(PR.zzz(d["head"][0] + 40, d["head"][1] - 140, 1.1, t, 1.0))
    x = 60 + 520 * (t - a)
    items = [falling(item_phone, 60 + 520 * (q - a) - 200, FL - 20, t, q, 60 + 520 * (q - a) - 330, FL + 230) for q in (a - .3, a + .45)]
    o.append(cat_sneak(x, FL + 260, 1.05, t, sack_open=.5 + .5 * bump(t, W(4), .05, .3), between="".join(items)))
    dx, dy = shake(t, W(4), 7)
    return view("".join(o), x + 40 + dx, FL - 20 + dy - 40 * u, 1.55 + .1 * u, -2 + 3 * u, over=title(t))


def frame_s03(t):
    """«я засыпаю за десять минут»: Дима крупно засыпает (глаза смыкаются на «засыпаю»), над ним часы-сектор на 10 минут
    обегают свой кусочек к «минут»; кот в маске выглядывает из-за изголовья и подмигивает."""
    a, b = T0("s03"), T1("s03")
    fall = W(7)
    expr = "awake73" if t < fall else ("sleepy" if t < fall + .35 else "bliss")
    bx = 560.0
    o = [room(t, x0=-600, x1=2000, win=False)]
    o.append(window(330, 420, 670, 860, "#141a3e", t, moon=(600, 510)))
    peek = ease_out(ramp(t, a + .1, .4))
    wink = 1.0 if abs(t - (W(9) + .1)) < .14 else 0.0
    g, d = dima_sleep(bx, t, expr)
    o.append(g)
    hx, hy = d["head"]
    o.append(cat(hx + 250, FL + 40 + 200 * (1 - peek), .62, t, dict(look=(-.6, -.3), smug=.7, blink_R=wink, tilt=-10), mask=1.0))
    o.append(PR.glow(hx + 250, FL + 60, 260, 1.0, NIGHT_BG) if False else "")
    sweep = ramp(t, W(9), WE(10) - W(9))
    sx, sy = hx + 330, hy - 210
    o.append(PR.glow(sx, sy, 200, .5 + .4 * bump(t, WE(10) - .1, .05, .4), "#ffe7a8"))
    o.append(tf(PR.stopwatch(0, 0, 1.0, hand_a=60 * ease_io(sweep), sector_a=60 * ease_io(sweep), click=bump(t, W(9), .04, .2), t=t), sx, sy, .6))
    o.append(PR.sparkles(sx, sy, 1.4, bump(t, WE(10) - .1, .05, .4), t, seed=4, n=6, r=140))
    o.append(PR.zzz(hx + 30, hy - 130, 1.1, t, ramp(t, fall + .3, .3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(9), 8)
    return view("".join(o), hx + 110 + dx, hy - 60 + dy - 20 * u, 1.7 + .2 * u + .05 * bump(t, W(9), .04, .3), 2 - 3 * u, over=title(t))


def frame(sid, t):
    if sid != "s08":
        lib.DEFS.clear()
    return globals()["frame_" + sid](t)


# ═════════════════════════ s04–s05: раньше — лента до трёх ночи, карусель дел ═════════════════════════
def wall_clock(x, y, r, spin, seed=0):
    return PR.clock(x, y, r, angle_h=spin * 30, angle_m=spin * 360, seed=seed)


def frame_s04(t):
    """«Раньше я лежал до трёх ночи, листал ленту»: Дима не спит, телефон над лицом светит синим, часы на стене крутятся,
    луна плывёт по окну; на «ленту» камера ныряет к экрану."""
    a, b = T0("s04"), T1("s04")
    bx = 560.0
    night = ramp(t, a, W(16) + .3 - a)
    o = [room(t, x0=-600, x1=2000, win=False)]
    o.append(window(330, 420, 670, 860, "#0f1433", t, moon=(380 + 260 * ease_io(night), 520 + 60 * night)))
    g, d = dima_sleep(bx, t, "screen74" if t < W(17) else "glassy", arm="out")
    o.append(g)
    hx, hy = d["head"]
    o.append(wall_clock(hx + 430, hy - 330, 80, 3 * ease_io(night) + .4 * (t - a)))
    wx, wy = d["wrist"]["n"]
    px, py = wx - 20, wy - 90
    o.append(PR.glow(hx + 40, hy - 40, 260, .7, "#7fc8ff"))
    o.append(phone_up(px, py + 6 * math.sin(t * 3), .8, -14, glow=1.3, scroll=(t - a) * (1.2 + 3 * ramp(t, W(17), .4))))
    for i in range(3):                       # большой палец листает: дуги прокрутки
        q = ((t - W(17)) * 2.5 + i / 3) % 1.0
        if t > W(17):
            o.append(line([(px + 70, py + 60 - 120 * q), (px + 80, py + 20 - 120 * q)], 4, "#cfe9ff", seed=60 + i, op=1 - q))
    o.append(tint(dark=.6))
    o.append(PR.glow(px, py, 200, .5, "#bfe8ff"))
    push = ease_io(ramp(t, W(18) - .15, .55))
    dx, dy = shake(t, W(15), 6)
    cx = hx + 160 + (px - hx - 160) * push
    cy = hy - 80 + (py - hy + 80) * push
    return view("".join(o), cx + dx, cy + dy, 1.6 + 1.5 * push + .05 * bump(t, W(15), .04, .3), 1 - 2 * push)


def icon(kind, x, y, k=1.0):
    """Иконки дел без букв: конверт, тележка, ноутбук, колокольчик звонка, список-галочки."""
    if kind == "mail":
        o = shape(lib.rrect(-50, -34, 50, 34, 5), "#f3e4c6", line([(-50, -34), (0, 6), (50, -34)], 3, "#b79e74", seed=70), w=3.4, seed=71)
    elif kind == "cart":
        o = line([(-56, -36), (-40, -36), (-26, 20), (40, 20), (52, -16), (-34, -16)], 6, INK, seed=72)
        o += blob(ellipse_pts(-16, 36, 10, 10, 10), INK) + blob(ellipse_pts(30, 36, 10, 10, 10), INK)
        o += blob(lib.rrect(-24, -40, 0, -18, 3), "#ff8a7a") + blob(lib.rrect(4, -46, 34, -18, 3), "#7bd389")
    elif kind == "laptop":
        o = shape(lib.rrect(-46, -40, 46, 20, 5), "#3a3f4a", blob(lib.rrect(-38, -32, 38, 12, 3), "#9fd0ff"), w=3.4, seed=73)
        o += shape(lib.rrect(-60, 20, 60, 32, 4), "#6a707c", "", w=3, seed=74)
    elif kind == "bell":
        o = shape([(-40, 26, 1), (-30, -10), (-20, -34), (0, -42), (20, -34), (30, -10), (40, 26, 1)], "#ffc24a", "", w=3.6, seed=75)
        o += blob(ellipse_pts(0, 34, 10, 8, 10), INK)
    else:
        o = shape(lib.rrect(-44, -50, 44, 50, 6), "#fbf6e6", "", w=3.4, seed=76)
        for j in range(3):
            o += shape(lib.rrect(-34, -36 + 30 * j, -16, -18 + 30 * j, 2), "#ffffff", "", w=2.4, seed=77 + j)
            o += line([(-6, -27 + 30 * j), (32, -27 + 30 * j)], 4, "#9aa4c0", seed=80 + j)
    return tf(o, x, y, k)


DEALS = ("mail", "cart", "laptop", "bell", "list")


def carousel(cx, cy, t, a, R=330.0, speed=1.0, u=1.0, into=None):
    """Облачка-дела кружат над головой (эллипс в перспективе); into=(x, y, q) — летят туда и сжимаются (q 0…1)."""
    o = []
    ang0 = speed * (t - a)
    for i, kd in enumerate(DEALS):
        ang = ang0 + 2 * math.pi * i / len(DEALS)
        x, y = cx + R * math.cos(ang), cy + .42 * R * math.sin(ang)
        k = .95 + .25 * math.sin(ang)
        if into is not None:
            q = clamp(into[2] * 1.6 - i * .12)
            e = q * q
            x, y, k = x + (into[0] - x) * e, y + (into[1] - y) * e, k * (1 - .9 * e)
            if q >= 1:
                continue
        uu = clamp(u * 1.5 - i * .1)
        o.append((math.sin(ang), PR.thought_cloud(x, y, k, 200, 150, uu, seed=i, dots=0, inner=icon(kd, 0, 0, .85))))
    o.sort(key=lambda z: z[0])
    return "".join(s for _, s in o)


def frame_s05(t):
    """«и прокручивал в голове завтрашние дела»: над головой Димы кружит карусель облачков-дел, всё быстрее; глаза открыты."""
    a, b = T0("s05"), T1("s05")
    bx = 560.0
    o = [room(t, x0=-600, x1=2000, win=False)]
    o.append(window(330, 420, 670, 860, "#0f1433", t, moon=(640, 580)))
    g, d = dima_sleep(bx, t, "stare73")
    o.append(g)
    o.append(tint(dark=.7))
    hx, hy = d["head"]
    sp = 2.0 + 5 * ramp(t, W(20), WE(24) - W(20))
    ang = (t - a) * sp
    o.append(carousel(hx + 60, hy - 330, a + ang / 1.0, a, R=250, speed=1.0, u=ramp(t, a - .1, .35)))
    o.append(PR.sweat(hx + 70, hy - 60, 1.2) if t > W(23) else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(24), 7)
    return view("".join(o), hx + 60 + dx, hy - 240 + dy, 1.45 + .15 * u, -2 + 4 * u + 1.5 * math.sin((t - a) * 3))


# ═════════════════════════ s06–s07: шаг 1 — тёплый свет ═════════════════════════
def frame_s06(t):
    """«Первое: за час до сна»: огонёк 1; кот в маске, как фокусник, достаёт из мешка тёплую лампу (вырастает над мешком,
    искры), ставит её; на «час» над лампой круг-часы с сектором в один час."""
    a, b = T0("s06"), T1("s06")
    o = [room(t, x0=-600, x1=2000, warm=.15 * ramp(t, W(26), .6), win=False)]
    o.append(window(620, 380, 960, 820, "#141a3e", t, moon=(900, 470)))
    o.append(nightstand(300, 1.2))
    pull = ease_out(ramp(t, W(25) + .05, .45))
    land = ease_io(ramp(t, W(26) - .1, .4))
    lx = 600 + (300 - 600) * land
    ly = FL - 330 - 260 * pull * (1 - land) + (FL - 252 - (FL - 330)) * land
    o.append(sack(620, FL + 40, 1.0, t, open_=1.0, squash=.3 * bump(t, W(25), .05, .2)))
    o.append(PR.glow(lx, ly - 100, 380 + 80 * bump(t, W(25) + .4, .05, .5), .9, "#ffb347"))
    o.append(tf(PR.night_lamp(0, 0, 1.0, on_u=ramp(t, W(25) + .2, .2), t=t), lx, ly, 1.0, 20 * (1 - pull) * (1 - land)))
    o.append(PR.sparkles(lx, ly - 120, 2.0, bump(t, W(25) + .35, .05, .5) + bump(t, W(26) + .3, .05, .4), t, seed=6, n=6, r=200))
    st = dict(paw=.9 * (1 - land) + .5 * bump(t, W(26) + .3, .1, .3), paw_dx=-30, smug=.8, look=(.8, -.6), tilt=-8 * pull)
    o.append(cat(800, FL + 60, 1.0, t, st, mask=1.0))
    hr = ramp(t, W(27), .4)
    if t > W(27) - .05:
        o.append(tf(PR.stopwatch(0, 0, 1.0, hand_a=30 * ease_io(hr), sector_a=30 * ease_io(hr), click=bump(t, W(27), .04, .2), t=t), 300, 640,
                    .55 * pop(t, W(27) - .05, .25)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(25), 9)
    return view("".join(o) + tint(warm=.4 * ramp(t, W(26), .6)), 560 + dx, 940 + dy, 1.35 + .12 * u, 2 - 3 * u, over=steps(t))


def bulb(x, y, k, rot=0.0, on=1.0):
    o = shape([(-30, -10), (-38, -50), (-26, -82), (0, -94), (26, -82), (38, -50), (30, -10)], lib.mix("#8a8f9a", "#f4fbff", on),
              blob(ellipse_pts(-12, -60, 8, 16, 10), "#ffffff", .8 * on), w=3.6, seed=90)
    o += shape(lib.rrect(-22, -12, 22, 26, 3), "#b8bcc6", line([(-22, 0), (22, 4)], 2.4, "#7a7e88", seed=91) + line([(-22, 12), (22, 16)], 2.4,
                                                                                                                      "#7a7e88", seed=92), w=3, seed=93)
    return tf(o, x, y, k, rot + 180)


def frame_s07(t):
    """«свет только тёплый и тусклый»: под потолком голая яркая холодная лампа; кот на табурете выкручивает её; на «тёплый»
    лампа выскакивает, холодный свет гаснет, комната становится оранжевой от ночника; на «тусклый» — ещё глуше."""
    a, b = T0("s07"), T1("s07")
    out = W(32)
    q = ease_io(ramp(t, out - .05, .25))
    cold = 1 - q
    o = [room(t, x0=-600, x1=2000, warm=.6 * q, win=False)]
    o.append(window(650, 380, 990, 820, "#141a3e", t, moon=(930, 470)))
    o.append(nightstand(160, 1.2))
    o.append(PR.glow(160, FL - 380, 420, .9 * q * (1 - .35 * ramp(t, W(34), .4)), "#ff9a3c"))
    o.append(PR.night_lamp(160, FL - 252, 1.0, on_u=1.0, t=t))
    o.append(shape(lib.rrect(350, FL - 330, 590, FL - 300, 6), "#b98a5a", "", w=4, seed=94))
    for s_ in (-1, 1):
        o.append(line([(470 + 90 * s_, FL - 300), (470 + 105 * s_, FL)], 12, "#8a6038", seed=95 + s_))
    bx, by = people.cat_paw_tip(470, FL - 320, 1.0, dict(paw=1.0, paw_dx=95))
    bx, by = bx + 30, by + 40
    turn = (t - a) * 900 * (1 - q)
    o.append(line([(bx, -600), (bx, by - 100 + 120 * q)], 5, "#2a2a30", seed=96))
    if cold > .02:
        o.append(PR.glow(bx, by, 700, .9 * cold, "#eaf6ff"))
    jump = ramp(t, out, .5)
    bxx, byy = bx + 200 * jump, by + 60 * jump - 500 * jump * (1 - jump) + 900 * jump * jump
    o.append(bulb(bxx, byy - 100 + 100 * q, 1.0, turn % 360 * .05 + 300 * jump, on=cold))
    reach = 1 - ease_out(ramp(t, out + .1, .3))
    st = dict(paw=1.0 * reach, paw_dx=95, tail=-25, look=(-.3, -1.0), smug=.6, tilt=-6 * math.sin(t * 14) * (1 - q), squint=.0)
    o.append(cat(470, FL - 320, 1.0, t, st, mask=1.0))
    o.append(PR.sparkles(bx, by - 60, 2.0, bump(t, out, .05, .4), t, seed=7, n=6, r=200))
    o.append(tint(cold=cold, warm=.9 * q, dark=.5 * ramp(t, W(34), .4)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, out, 12)
    return view("".join(o), 520 + dx, 860 + dy + 60 * u, 1.25 + .1 * u, -1 + 2 * u, over=steps(t), bg="#2a2030")


# ═════════════════════════ s08: призыв ═════════════════════════
def frame_s08(t):
    import story_cta_tg as tg
    press = W(38) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=os.path.join(STORY, "common"))


# ═════════════════════════ s09: ритуал картинкой ═════════════════════════
def ritual_card(x, y, k=1.0, t=0.0, lit=4):
    """Картинка-ритуал без букв: четыре плитки — тёплая лампа, блокнот, телефон с молнией зарядки, приоткрытое окно с листом."""
    o = [shape(lib.rrect(-260, -320, 260, 320, 26), "#fff8e6", blob(lib.rrect(-260, 250, 260, 320, 22), "#f1e2bf", .8), w=5, seed=110)]
    for i in range(4):
        cx, cy = -122 + 244 * (i % 2), -150 + 280 * (i // 2)
        on = i < lit
        o.append(shape(lib.rrect(cx - 105, cy - 115, cx + 105, cy + 115, 18), "#ffe7b0" if on else "#e9e2d2", "", w=3.6, seed=111 + i))
        if i == 0:
            o.append(PR.glow(cx, cy - 30, 110, .8, "#ffb347") + PR.night_lamp(cx, cy + 95, .62, on_u=1.0, t=t))
        elif i == 1:
            o.append(notebook(cx, cy, .4, -8, open_=1.0, lines_=.7) + PR.pencil(cx + 40, cy + 40, .7, -40))
        elif i == 2:
            o.append(phone_up(cx, cy, .65, 0, glow=0.0, charge=1.0) + line([(cx, cy + 78), (cx + 10, cy + 105)], 5, "#9aa0aa", seed=118))
        else:
            o.append(shape(lib.rect_pts(cx - 70, cy - 80, cx + 70, cy + 80), "#9fc4e8", line([(cx, cy - 80), (cx, cy + 80)], 5, "#fff8e6",
                                                                                                taper=0, wmin=1, seed=119), w=4, seed=120))
            o.append(leaf(cx + 30, cy + 20, 1.4, 30, 0))
            o.append(PR.wind_lines(cx - 40, cy - 20, .6, 1.0, t, seed=3, n=3))
        o.append(tf(shape(ellipse_pts(0, 0, 22, 22, 14), "#ffc24a", "", w=3, seed=121 + i), cx - 82, cy - 92))
        for j in range(i + 1):
            o.append(blob(ellipse_pts(cx - 92 + 7 * j, cy - 92, 2.6, 2.6, 6), INK) if False else "")
    return tf("".join(o), x, y, k)


def frame_s09(t):
    """«картинкой, чтобы сохранить»: кот в маске вытаскивает из мешка картинку-ритуал (4 плитки), разворачивает её к нам;
    на «сохранить» сверху падает закладка-флажок, картинка мигает искрами."""
    a, b = T0("s09"), T1("s09")
    o = [room(t, x0=-600, x1=2000, warm=.7, win=False)]
    o.append(PR.glow(540, 760, 600, .5, "#ffcf8a"))
    rise = pop(t, a - .05, .35)
    sv = W(46)
    o.append(PR.glow(540, 760, 420, .6 * bump(t, sv + .1, .05, .5), "#fff3b0"))
    o.append(ritual_card(540, 1220 - 360 * rise, 1.12 * (.5 + .5 * rise) + .05 * bump(t, sv + .12, .05, .3), t))
    drop = lib.ease_in(ramp(t, sv - .15, .25))
    if t > sv - .15:
        rx, ry = 540 + 200, 560 - 700 * (1 - drop)
        o.append(shape([(rx - 34, ry - 60), (rx + 34, ry - 60), (rx + 34, ry + 60), (rx, ry + 34), (rx - 34, ry + 60)], "#e2574c", "", w=4, seed=130))
    o.append(PR.sparkles(540, 760, 3.0, bump(t, sv + .1, .05, .5), t, seed=9, n=7, r=300))
    o.append(sack(200, FL + 60, .8, t, open_=1.0))
    o.append(cat(860, FL + 60, .85, t, dict(paw=.8, paw_dx=-40, look=(-.6, -.8), smile=1.0), mask=1.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, sv + .12, 9)
    return view("".join(o) + tint(warm=.5), 540 + dx, 930 + dy, 1.12 + .08 * u, 1 - 2 * u, over=steps(t), bg="#5a3020")


# ═════════════════════════ s10–s11: шаг 2 — пять минут на бумаге ═════════════════════════
def write_scene(t, a, lines_, open_=1.0, into=None, expr="write"):
    bx = 560.0
    o = [room(t, x0=-600, x1=2000, warm=.65, win=False)]
    o.append(window(620, 380, 960, 820, "#2a2a55", t, moon=(900, 470)))
    o.append(nightstand(bx - 480, 1.2))
    o.append(PR.glow(bx - 480, FL - 380, 360, .8, "#ff9a3c"))
    o.append(PR.night_lamp(bx - 480, FL - 252, 1.0, on_u=1.0, t=t))
    g, d = dima_sleep(bx, t, expr, sit=1.0, arm="out")
    o.append(g)
    wn, wf = d["wrist"]["n"], d["wrist"]["f"]
    nx, ny = (wn[0] + wf[0]) / 2 + 10, (wn[1] + wf[1]) / 2 + 10
    return o, d, (nx, ny)


def frame_s10(t):
    """«Второе: пять минут пишу на бумаге»: огонёк 2; кот кидает блокнот из мешка, Дима садится в кровати с блокнотом
    на коленях и пишет каракули без букв; маленькие часы проходят сектор пяти минут."""
    a, b = T0("s10"), T1("s10")
    lines_ = ramp(t, W(50), WE(52) + .3 - W(50))
    o, d, (nx, ny) = write_scene(t, a, lines_)
    fly = ramp(t, a - .05, W(48) - a + .05)
    if fly < 1:                              # блокнот летит из мешка по дуге к коленям
        sx, sy = 1050, FL - 200
        e = ease_out(fly)
        x, y = sx + (nx - sx) * e, sy + (ny - sy) * e - 380 * math.sin(math.pi * e)
        o.append(tf(notebook(0, 0, .45, 0, open_=0.0), x, y, 1.0, 540 * (1 - e)))
    else:
        o.append(notebook(nx, ny, .7, -6, open_=1.0, lines_=lines_))
        px = nx - 60 + 160 * ((lines_ * 4) % 1.0)
        o.append(PR.pencil(px + 30, ny - 40 + 8 * math.sin(t * 30), .8, -50))
    o.append(sack(1080, FL + 60, .8, t, open_=1.0))
    o.append(cat(1300, FL + 60, .85, t, dict(paw=.9 * bump(t, a, .06, .3), paw_dx=-60, look=(-.9, -.3), smug=.6), mask=1.0))
    pr = ramp(t, W(48), WE(49) - W(48))
    if t > W(48) - .1:
        o.append(tf(PR.stopwatch(0, 0, 1.0, hand_a=30 * ease_io(pr), sector_a=30 * ease_io(pr), click=bump(t, W(48), .04, .2), t=t),
                    d["head"][0] + 420, d["head"][1] - 120, .5 * pop(t, W(48) - .1, .25)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(47), 8)
    cx = 760 + (nx - 760) * u
    return view("".join(o) + tint(warm=.6), cx + dx, 900 + dy + 40 * u, 1.05 + .45 * u, 1 - 2 * u, over=steps(t), bg="#5a3020")


def frame_s11(t):
    """«что надо сделать завтра»: облачка-дела вылетают из головы и влетают в блокнот; на «завтра» блокнот захлопывается,
    пух, Дима выдыхает."""
    a, b = T0("s11"), T1("s11")
    shut = W(56)
    sh = ramp(t, shut - .05, .15)
    o, d, (nx, ny) = write_scene(t, a, 1.0, expr="write" if t < shut else "relief")
    hx, hy = d["head"]
    q = ramp(t, a, shut - a)
    o.append(notebook(nx, ny, .7, -6, open_=1 - sh, lines_=1.0))
    if sh < 1:
        o.append(carousel(hx + 40, hy - 300, t * 2.5, a, R=230, speed=1.0, u=ramp(t, a - .1, .2), into=(nx, ny, q)))
    o.append(PR.dust_puff(nx, ny - 20, 2.0, clamp((t - shut) / .5), seed=4))
    o.append(PR.sparkles(nx, ny - 60, 1.6, bump(t, shut + .05, .05, .4), t, seed=10, n=5, r=160))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, shut, 12)
    return view("".join(o) + tint(warm=.6), (hx + nx) / 2 + 40 + dx, hy - 40 + dy, 1.5 + .15 * u + .06 * bump(t, shut, .04, .3), 0, over=steps(t),
                bg="#5a3020")


# ═════════════════════════ s12–s13: Бейлор ═════════════════════════
def campus(t, lit=1.0):
    """Университетский корпус без букв: ступени, шесть колонн, фронтон, купол, окна светятся; ночь, деревья."""
    o = [rect(-1500, -1500, 2600, FL, "#141a3e")]
    for i, (sx, sy) in enumerate(((60, 160), (300, 80), (880, 140), (1000, 360), (120, 420), (700, 40), (460, 260))):
        o.append(PR.star4(sx, sy, 9 + 4 * math.sin(t * 4 + i), 1.0))
    o.append(PR.glow(900, 200, 140, .6, "#f4f0dc") + '<circle cx="900" cy="200" r="40" fill="#f4f0dc"/><circle cx="917" cy="190" r="34" fill="#141a3e"/>')
    o.append(rect(-1500, FL, 2600, FL + 1500, "#2c3a2c"))
    o.append(shape(lib.rect_pts(80, 900, 1000, 1240), "#e9dcc0", "", w=5, seed=150))            # корпус
    for j in range(2):
        for i in range(7):
            wx, wy = 130 + i * 125, 960 + j * 140
            o.append(shape(lib.rrect(wx, wy, wx + 60, wy + 90, 6), lib.mix("#3a4378", "#ffd27a", lit), "", w=3, seed=151 + i + 7 * j))
    o.append(shape([(40, 900), (540, 640), (1040, 900)], "#efe4cc", line([(140, 880), (540, 680), (940, 880)], 3, "#c9b894", seed=160), w=5, seed=161))
    o.append(shape(lib.rect_pts(400, 520, 680, 660), "#e3d4b4", "", w=4.4, seed=162))
    dome = [(380, 530)] + [(540 - 170 * math.cos(math.pi * j / 16), 530 - 190 * math.sin(math.pi * j / 16)) for j in range(1, 16)] + [(700, 530)]
    o.append(shape(dome, "#7fa7b8", line([(470, 360), (500, 520)], 3, "#5d8596", seed=163) + line([(610, 360), (580, 520)], 3, "#5d8596", seed=164),
                   w=5, seed=165))
    o.append(line([(540, 340), (540, 270)], 6, INK, seed=166) + blob(ellipse_pts(540, 262, 12, 12, 10), "#e8b84a"))
    for i in range(6):                                                                            # колонны перед фасадом
        cx = 160 + i * 152
        o.append(shape(lib.rect_pts(cx - 26, 910, cx + 26, 1250), "#f6efdd", line([(cx - 8, 920), (cx - 8, 1240)], 2.4, "#cfc2a2", seed=170 + i),
                       w=4, seed=176 + i))
    for k in range(3):
        o.append(shape(lib.rect_pts(40 - 30 * k, 1250 + 18 * k, 1040 + 30 * k, 1268 + 18 * k), "#d8cbb0", "", w=3.4, seed=182 + k))
    for tx in (-120, 1180):
        o.append(rect(tx - 14, FL - 200, tx + 14, FL + 40, "#3b2a24"))
        o.append(blob(ellipse_pts(tx, FL - 300, 140, 160, 16), "#2f5a3a") + blob(ellipse_pts(tx + 40, FL - 340, 80, 90, 14), "#3d7048", .9))
    return "".join(o)


def frame_s12(t):
    """«В Бейлоре проверили»: ночной университетский корпус без букв, окна вспыхивают тёплым по очереди; камера
    поднимается к куполу; на «проверили» над куполом галочка-печать."""
    a, b = T0("s12"), T1("s12")
    o = [campus(t, lit=.4 + .6 * ramp(t, a + .1, .5))]
    ck = W(59) + .1
    o.append(PR.glow(540, 420, 260, .7 * bump(t, ck, .05, .6), "#fff3b0"))
    o.append(PR.check_mark(540, 400, 3.2, ramp(t, ck, .25), col="#5fd16a", w=14, seed=1))
    o.append(PR.sparkles(540, 400, 2.4, bump(t, ck + .1, .05, .5), t, seed=11, n=6, r=220))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ck + .1, 10)
    return view("".join(o), 540 + dx, 980 - 300 * u + dy, 1.05 + .2 * u, 0, over=steps(t))


ROOM_COLS = ("blue", "green", "quilt")


def dorm_room(i, t, dark):
    """Комната общежития (своя система: окно 0…900 × 0…700): спящий под одеялом, тумбочка с блокнотом, ночник."""
    o = [rect(-50, -50, 950, 760, lib.mix("#c98a52", "#2b3360", dark))]
    o.append(rect(-50, 560, 950, 760, lib.mix("#8a5a3a", "#3a2c40", dark)))
    o.append(tf(shape(lib.rrect(-85, -210, 85, 0, 8), "#7a5638", "", w=4.4, seed=190) + notebook(0, -236, .32, -4, open_=0.0), 140, 560, 1.0))
    if dark < .9:
        o.append(PR.glow(140, 330, 260, .8 * (1 - dark), "#ffb347"))
    bx = 560
    o.append(PR.bed(bx, 560, 1.0, seed=i))
    d = people.dima_bed(bx - 50, 560 - 118 - 25, .46, expr="bliss", t=t + i, cover="nose", seed=i, col=ROOM_COLS[i])
    o.append(d["svg"])
    if dark > .5:
        o.append(PR.zzz(d["head"][0] + 110, d["head"][1] + 10, .9, t + .6 * i, ramp(dark, .5, .4)))
    return "".join(o)


def frame_s13(t):
    """«кто так делал перед сном, засыпал быстрее»: разрез общежития — три окна-комнаты, в каждой спящий под одеялом и
    блокнот на тумбочке; на «засыпал быстрее» свет гаснет по очереди, появляются Z."""
    a, b = T0("s13"), T1("s13")
    o = [rect(-800, -800, 1900, 2800, "#e3d4b4")]
    offs = [(60, 520), (60, 1000), (60, 1480)]
    for i, (ox, oy) in enumerate(offs):
        dk = ease_io(ramp(t, W(65) + .18 * i, .25))
        c = lib.clip_rect(ox, oy, 900 * 1.07, 700 * .62)
        o.append(shape(lib.rect_pts(ox - 14, oy - 14, ox + 963 + 14, oy + 434 + 14), "#f6efdd", "", w=5, seed=200 + i))
        o.append(f'<g clip-path="url(#{c})"><g transform="translate({ox} {oy - 270}) scale(1.07)">{dorm_room(i, t, dk)}</g></g>')
        o.append(f'<path d="{lib.ink_closed(lib.rect_pts(ox, oy, ox + 963, oy + 434), 4.0, seed=210 + i)}" fill="{INK}"/>')
        o.append(PR.glow(ox + 900, oy + 60, 80, bump(t, W(65) + .18 * i, .04, .3), "#fff3b0"))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1000 + 60 * u, .92 + .06 * u, 0, over=steps(t), bg="#e3d4b4")


# ═════════════════════════ s14–s15: шаг 3 — телефон на кухне ═════════════════════════
DOOR_X = 900.0


def kitchen(t):
    """Справа от двери — кухня: плитка, шкафчик-столешница, розетка с зарядкой; слева — спальня."""
    o = [room(t, x0=-800, x1=DOOR_X, win=False)]
    o.append(rect(DOOR_X, -1500, 2800, FL, "#3c4a6a"))
    for i in range(int(DOOR_X // 90), 32):
        for j in range(-4, 15):
            o.append(f'<rect x="{i * 90 + 4}" y="{j * 90 + 4}" width="82" height="82" fill="#47587c" rx="6"/>')
    o.append(rect(DOOR_X, FL, 2800, FL + 1500, "#4a4048"))
    o.append(shape(lib.rect_pts(DOOR_X - 40, -1500, DOOR_X + 40, FL), "#e9e1d0", "", w=4.4, seed=220))
    o.append(shape(lib.rect_pts(1300, FL - 340, 2100, FL), "#c8d8e8", line([(1700, FL - 300), (1700, FL - 20)], 3, "#9aaabb", seed=221) +
                   blob(ellipse_pts(1650, FL - 170, 8, 30, 8), "#7a8a9a") + blob(ellipse_pts(1750, FL - 170, 8, 30, 8), "#7a8a9a"), w=4.4, seed=222))
    o.append(shape(lib.rect_pts(1280, FL - 370, 2120, FL - 330), "#e9dcc0", "", w=4.4, seed=223))
    o.append(shape(lib.rrect(1560, FL - 560, 1620, FL - 480, 8), "#f3f0e8", blob(ellipse_pts(1580, FL - 520, 5, 9, 6), INK) +
                   blob(ellipse_pts(1600, FL - 520, 5, 9, 6), INK), w=3.4, seed=224))
    o.append(PR.charger(1590, FL - 500, 1.0))
    o.append(PR.cable([(1590, FL - 472), (1600, FL - 420), (1640, FL - 380), (1660, FL - 372)], w=7, seed=3))
    o.append(tf(PR.cable([(0, 0)], w=1) if False else "", 0, 0))
    o.append(shape(lib.rrect(1840, FL - 470, 1980, FL - 370, 18), "#d65a48", blob(lib.rrect(1850, FL - 470, 1970, FL - 450, 8), "#b8423a"), w=4, seed=225))
    return "".join(o)


def frame_s14(t):
    """«Третье: телефон заряжается на кухне»: огонёк 3; кот в маске уносит светящийся телефон в зубах из спальни на кухню,
    запрыгивает на столешницу и кладёт его на зарядку; на «кухне» — зелёная молния и искры."""
    a, b = T0("s14"), T1("s14")
    jump0, put = W(69) - .1, W(71) + .05
    ph_y = FL - 372
    o = [kitchen(t), tint(dark=.35)]
    if t < put:
        phone = f'<g transform="translate(836 1150) rotate(90) scale(.5)">{phone_up(0, 0, 1.0, 0, glow=1.0, scroll=t)}</g>'
        st = dict(mouth_item=mask_art(-.2, t * 9) + phone, smug=.7, look=(.8, -.1), turn=.3)
        if t < jump0:
            x = 250 + (1250 - 250) * ramp(t, a, jump0 - a)
            o.append(cat_sneak(x, FL + 60, .9, t, st=st, mask=0.0, sack_on=False))
        else:
            o.append(people.cat_jump((1250, FL + 60), (1400, FL - 370), .9, ramp(t, jump0, put - jump0 - .05), t, st=st, height=260))
    else:
        o.append(cat(1400, FL - 370, .9, t, dict(paw=.8 * bump(t, put, .06, .3), paw_dx=70, smile=1.0, look=(.6, .4)), mask=1.0))
        o.append(phone_up(1590, ph_y - 30, .55, 90, glow=1.0, charge=ramp(t, put, .2)))
        o.append(PR.sparkles(1590, ph_y - 40, 1.6, bump(t, put + .05, .05, .5), t, seed=12, n=5, r=140))
    track = clamp((t - a) / (put - a))
    cx = 600 + (1450 - 600) * ease_io(track)
    dx, dy = shake(t, put, 9)
    return view("".join(o), cx + dx, FL - 330 + dy, 1.5, 0, over=steps(t))


def frame_s15(t):
    """«а не у подушки»: крупно подушка и тумбочка — на тумбочке пусто (пунктир телефона тает), кот хлопает лапой по
    пустому месту, Дима спит."""
    a, b = T0("s15"), T1("s15")
    bx = 560.0
    o = [room(t, x0=-600, x1=2000, warm=.5, win=False)]
    g, d = dima_sleep(bx, t, "bliss")
    sx = bx - 640
    o.append(nightstand(sx, 1.2))
    o.append(PR.glow(sx, FL - 380, 300, .6, "#ff9a3c"))
    o.append(g)
    hx, hy = d["head"]
    o.append(PR.zzz(hx + 40, hy - 140, 1.0, t, 1.0))
    fade = 1 - ramp(t, W(75), .4)
    ty = FL - 252
    if fade > .02:
        o.append(f'<rect x="{sx - 70}" y="{ty - 34}" width="140" height="30" rx="8" fill="none" stroke="#fff3cf" stroke-width="5" '
                 f'stroke-dasharray="14 10" opacity="{fade:.3f}"/>')
    pats = [W(73), W(75)]
    p = max(bump(t, q - .08, .06, .14) for q in pats)
    o.append(cat(sx - 190, FL + 40, .75, t, dict(paw=.8 * p, paw_dx=90, look=(-.9, .3), smile=1.0), mask=1.0))
    o.append(PR.dust_puff(sx, ty - 20, 1.0, clamp((t - W(75)) / .4), seed=6))
    o.append(PR.sparkles(sx, ty - 40, 1.0, bump(t, W(75) + .1, .05, .4), t, seed=13, n=4, r=90))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(75), 8)
    return view("".join(o) + tint(warm=.4), (sx + hx) / 2 - 90 + dx, ty - 60 + dy, 1.55 + .15 * u, 0, over=steps(t), bg="#5a3020")
