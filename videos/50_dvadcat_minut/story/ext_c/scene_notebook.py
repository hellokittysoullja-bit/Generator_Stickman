"""Сцена notebook рилса 50.
s12 (24.04–25.96): крупно тетрадь Димы, кот сидит на её краю и тычет лапой в пустое место на «Помогает» (24.04); рука с ручкой
пишет «Вопрос:» (24.8–25.3), «сколько это заняло» (25.6–26.42) — буквы проявляются по ходу пера.
s13 (25.96–27.6): наезд на строки, «в прошлый раз» дописывается, знак вопроса прыгает на «раз» (27.12).
s14 (27.6–29.88): стол, стопка прошлых отчётов, рука листает, штампы «3 ч», «2,5 ч», «3 ч», на «прошлые» (28.80) ближний отчёт
ложится крупно.
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat  # noqa: E402
import dima  # noqa: E402
import hand  # noqa: E402
import lib  # noqa: E402
from common import punch, shake, speed_streaks, text, whip_in  # noqa: E402
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad,
                 rect_pts, shape, smooth, spring, svg, T)

G = json.load(open(os.path.join(HERE, "glyphs.json")))
_ST = {}
INKC = "#26356f"
FS = 104
SC = FS / G["upm"]
TX0 = 238
BASES = [610, 790, 970]
PAGE = (130, 250, 960, 1290)
# слоты письма (общее время)
SLOTS = [(24.84, 25.34), (25.58, 26.44), (26.52, 27.08)]
QPOP = 27.12


def build_lines():
    out = []
    for li in range(3):
        gl = G["lines"][li]
        if li == 2:
            gl = gl[:-1]                      # «?» — отдельный прыгающий знак
        x = TX0
        base = BASES[li]
        path, gls = [], []
        for gi, g in enumerate(gl):
            gls.append(dict(g=g, x=x))
            for st in g.get("strokes", []):
                for k, (px, py) in enumerate(st):
                    path.append((x + px * SC, base - py * SC, gi, k > 0))
            x += g["adv"] * SC
        P = np.array([(p[0], p[1]) for p in path])
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        down = np.array([p[3] for p in path[1:]])
        cum = np.concatenate([[0], np.cumsum(np.where(down, seg, seg * 0.4))])
        out.append(dict(path=path, P=P, cum=cum / cum[-1], gls=gls, base=base, x1=x))
    return out


L = build_lines()
QG = G["lines"][2][-1]
QX = L[2]["x1"] + 8


def progress(li, t):
    a, b = SLOTS[li]
    u = clamp((t - a) / (b - a))
    return u * 0.85 + 0.15 * (u * u * (3 - 2 * u))


def tip_at(li, p):
    ln = L[li]
    i = int(np.searchsorted(ln["cum"], p, side="right")) - 1
    i = max(0, min(i, len(ln["P"]) - 2))
    c0, c1 = ln["cum"][i], ln["cum"][i + 1]
    q = 0 if c1 <= c0 else (p - c0) / (c1 - c0)
    x, y = ln["P"][i] + (ln["P"][i + 1] - ln["P"][i]) * q
    lift = 0.0 if ln["path"][i + 1][3] else math.sin(math.pi * q)
    return x, y, i, lift


def text_line(li, t):
    ln = L[li]
    a, b = SLOTS[li]
    if t <= a:
        return ""
    p = progress(li, t)
    s = []
    if p >= 1:
        cur, i_now = len(ln["gls"]), len(ln["P"]) - 1
    else:
        _, _, i_now, _ = tip_at(li, p)
        cur = ln["path"][i_now][2]
    for gi, o in enumerate(ln["gls"]):
        g = o["g"]
        if not g["bounds"] or gi > cur:
            continue
        body = f'<path d="{g["d"]}" transform="translate({f(o["x"])} {ln["base"]}) scale({SC:.5f} {-SC:.5f})" fill="{INKC}"/>'
        if gi == cur and p < 1:
            pts = [(x, y, d) for (x, y, gg, d) in ln["path"][:i_now + 1] if gg == gi]
            tx, ty, _, _ = tip_at(li, p)
            pts.append((tx, ty, True))
            d = ""
            for k, (x, y, dn) in enumerate(pts):
                d += ("L" if (dn and k > 0) else "M") + f"{f(x)} {f(y)}"
            wpx = g["width"] * SC * 1.25
            mid = lib.uid("m")
            lib.DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-600" y="-600" width="3400" height="3200">'
                            f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{f(wpx)}" stroke-linecap="round" stroke-linejoin="round"/></mask>')
            body = f'<g mask="url(#{mid})">{body}</g>'
        s.append(body)
    return "".join(s)


def pen_tip(t):
    """Кончик ручки: влетает снизу справа к началу строки 1, пишет, переходы между строками с подъёмом, потом уходит."""
    a0 = SLOTS[0][0]
    if t < a0:
        u = ease_out(clamp((t - 24.45) / (a0 - 24.45)), 2.0)
        sx, sy = 1020, 1500
        ex, ey = tip_at(0, 0)[:2]
        return sx + (ex - sx) * u, sy + (ey - sy) * u - 50 * math.sin(math.pi * u), 1.0 + 0.06 * (1 - u)
    for li, (a, b) in enumerate(SLOTS):
        if a <= t <= b:
            x, y, _, lift = tip_at(li, progress(li, t))
            return x, y, 1.0 + 0.03 * lift
        if li + 1 < len(SLOTS) and b < t < SLOTS[li + 1][0]:
            u = ease_io((t - b) / (SLOTS[li + 1][0] - b))
            sx, sy = tip_at(li, 1.0)[:2]
            ex, ey = tip_at(li + 1, 0.0)[:2]
            return sx + (ex - sx) * u, sy + (ey - sy) * u - 40 * math.sin(math.pi * u), 1.0 + 0.07 * math.sin(math.pi * u)
    sx, sy = tip_at(2, 1.0)[:2]
    e = t - SLOTS[-1][1]
    if e < 0.3:
        # короткая «точка» у знака вопроса
        return sx + (QX + 30 - sx) * ease_io(e / 0.3), sy, 1.0
    u = ease_in(clamp((e - 0.3) / 0.35), 1.5)
    return QX + 30 + 500 * u, sy + 600 * u, 1.0 + 0.07 * u


# ───────────────────────── стол и тетрадь
def desk():
    s = []
    lib.DEFS.append('<pattern id="pWood" width="420" height="150" patternUnits="userSpaceOnUse">'
                    '<rect width="420" height="150" fill="#c28a56"/>'
                    '<path d="M0 32 C120 24 260 42 420 30 M0 84 C140 92 280 70 420 86 M0 126 C110 118 300 134 420 122" fill="none" stroke="#a8713f" stroke-width="3"/>'
                    '<rect y="148" width="420" height="2" fill="#8a5a30"/></pattern>')
    s.append('<rect x="-800" y="-800" width="2700" height="3600" fill="url(#pWood)"/>')
    g = rad_grad([(0, "#fff0c8", .55), (.6, "#ffe0a0", .18), (1, "#ffe0a0", 0)], 520, 700, 1000, 1000)
    s.append(f'<rect x="-800" y="-800" width="2700" height="3600" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def notebook():
    x0, y0, x1, y1 = PAGE
    s = []
    s.append(blob(rect_pts(x0 + 16, y0 + 26, x1 + 18, y1 + 30, 22), "#3a2410", .42, blur(14)))
    # обложка и страницы
    s.append(shape(rect_pts(x0 - 26, y0 - 22, x1 + 20, y1 + 24, 26), "#2f5f9a", blob(rect_pts(x1 - 40, y0 - 22, x1 + 20, y1 + 24, 26), "#244a7a", .9),
                   w=5.4, seed=1100))
    inner = "".join(line([(x0, y + 0), (x1, y + 2)], 2.6, "#9cc3e6", taper=.0, wmin=1, seed=1110 + k, op=.9)
                    for k, y in enumerate(range(y0 + 90, y1, 90)))
    inner += line([(x0 + 92, y0), (x0 + 92, y1)], 3.4, "#e88a8a", taper=.0, wmin=1, seed=1130, op=.9)
    inner += blob(rect_pts(x1 - 40, y0, x1, y1), "#e9e2cf", .8)
    s.append(shape(rect_pts(x0, y0, x1, y1, 14), "#fffdf5", inner, w=4.8, seed=1101))
    # спираль слева
    for k, y in enumerate(range(y0 + 40, y1 - 20, 80)):
        s.append(shape(ellipse_pts(x0 - 2, y, 12, 12, 10), "#1c1622", "", w=0, seed=1140 + k, ink=False))
        s.append(line([(x0 - 40, y - 16), (x0 - 8, y - 4), (x0 + 22, y + 4)], 9, "#c9ced8", taper=.2, wmin=.8, seed=1160 + k))
        s.append(line([(x0 - 40, y - 16), (x0 - 8, y - 4), (x0 + 22, y + 4)], 3, "#8e95a5", taper=.2, wmin=.8, seed=1180 + k, op=.8))
    return "".join(s)


def qmark(t):
    e = t - QPOP
    if e < 0:
        return ""
    k = spring(e, 2.6, 5.5)
    jump = -70 * abs(math.sin(e * 9)) * math.exp(-e * 2.6)
    wig = 7 * math.sin(e * 16) * math.exp(-e * 3)
    base = BASES[2]
    cx = QX + 40
    return (f'<g transform="translate({f(cx)} {f(base + jump)}) rotate({wig:.2f}) scale({1.18 * k:.3f}) translate({-cx} {-base})">'
            f'<path d="{QG["d"]}" transform="translate({f(QX)} {base}) scale({SC:.5f} {-SC:.5f})" fill="#e8281a"/></g>')


# ───────────────────────── кот на тетради
CAT_X, CAT_Y, CAT_S = 790, 650, 1.0
TAPS = [24.04, 24.46, 24.88]
TARGET = (610, 600)


def cat_scene(t, sid):
    sh = cat.to_world(cat.SHOULDER_L, CAT_X, CAT_Y, CAT_S)
    rest = cat.PAW_REST
    tgt_i = cat.to_int((TARGET[0] + 0, TARGET[1]), CAT_X, CAT_Y, CAT_S)
    # лапа тычет: вытягивается к цели и бьёт
    e = t - 24.0
    away = smooth(24.9, 25.2, t)
    act = ease_out(clamp((t - 23.9) / 0.2), 2) * (1 - away)
    P = (rest[0] + (tgt_i[0] - rest[0]) * act, rest[1] + (tgt_i[1] - rest[1]) * act)
    press = 0.0
    for tp in TAPS:
        d = t - tp
        if 0 <= d < 0.3:
            press = max(press, math.sin(math.pi * d / 0.3))
    P = (P[0] + 0, P[1] - 28 * act * (1 - press))
    # взгляд: на лапу, потом на ручку
    k = smooth(25.0, 25.3, t)
    look = (-0.5 * (1 - k) + 0.0 * k, 0.8 * (1 - k) + 0.7 * k)
    blink = 0.0
    for c, half in ((24.75, .07), (26.6, .07)):
        if c - half <= t <= c + half:
            blink = 1 - abs(t - c) / half
    tail = 6 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1)
    flick = 0.0
    for c in (24.3, 26.9):
        d = t - c
        if 0 <= d < 0.5:
            flick += -14 * math.exp(-d * 9) * math.sin(d * 34)
    tilt = 4 * math.sin(t * 1.1) + (-6 if 24.0 < t < 24.9 else 0)
    return cat.draw(CAT_X, CAT_Y, CAT_S, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw=P, press=press, shadow=False)


def frame_note(sid, t):
    s = [_ST["desk"], _ST["nb"]]
    s.append("".join(text_line(i, t) for i in range(3)))
    s.append(qmark(t))
    # тень кота на странице
    s.append(blob(ellipse_pts(CAT_X + 30, CAT_Y + 4, 150, 22, 16), "#3a2410", .3, blur(8)))
    s.append(cat_scene(t, sid))
    # удар лапы: круги на бумаге
    for tp in TAPS:
        d = t - tp - 0.08
        if 0 < d < 0.4 and t < 25.2:
            u = d / 0.4
            r = 20 + 60 * ease_out(u, 2)
            s.append(f'<ellipse cx="{TARGET[0]}" cy="{TARGET[1] + 10}" rx="{r:.1f}" ry="{r * .5:.1f}" fill="none" stroke="#26356f" stroke-width="{4 * (1 - u) + 1:.1f}" opacity="{.5 * (1 - u):.2f}"/>')
    # рука с ручкой
    x, y, lft = pen_tip(t)
    if t >= 24.45:
        ang = -36 + 3 * math.sin(t * 2.3) - 4 * (lft - 1)
        s.append(f'<g transform="translate({f(x + 26 * lft)} {f(y + 34 * lft)}) scale(1.15)" opacity=".28" filter="url(#fShH)">{hand.hand(ang, 7)}</g>')
        s.append(f'<g transform="translate({f(x)} {f(y)}) scale({f(1.15 * lft)})">{hand.hand(ang, 7)}</g>')
    return "".join(s)


# ───────────────────────── s14: стопка отчётов
SHEETS = [  # центр, поворот, штамп
    dict(c=(520, 520), rot=-3.0, stamp="3 ч", t=27.78, sc=1.0),
    dict(c=(560, 800), rot=2.0, stamp="2,5 ч", t=28.22, sc=1.0),
    dict(c=(525, 1080), rot=-1.5, stamp="3 ч", t=28.55, sc=1.0),
]
SW, SH_ = 560, 700
NEAR = 28.8


def sheet_body(i):
    s = []
    hw, hh = SW / 2, SH_ / 2
    s.append(blob(rect_pts(-hw + 10, -hh + 16, hw + 14, hh + 20, 10), "#3a2410", .35, blur(8)))
    inner = blob(rect_pts(hw - 50, -hh, hw, hh), "#e9e2cf", .8)
    s.append(shape(rect_pts(-hw, -hh, hw, hh, 8), "#fffdf5", inner, w=4.6, seed=1200 + i))
    s.append(text(-hw + 44, -hh + 80, "ОТЧЁТ", 50, "#5a6b86", anchor="start"))
    s.append(line([(-hw + 44, -hh + 112), (hw - 190, -hh + 112)], 4, "#c1c9d6", seed=1210 + i))
    for k in range(7):
        w_ = [0.82, 0.7, 0.9, 0.55, 0.78, 0.66, 0.4][k]
        s.append(line([(-hw + 44, -hh + 190 + k * 56), (-hw + 44 + (SW - 88) * w_, -hh + 192 + k * 56)], 7, "#aeb8c9", taper=.1, wmin=.9, seed=1220 + i * 10 + k))
    # таблица внизу
    s.append(shape(rect_pts(-hw + 44, hh - 190, hw - 44, hh - 50, 6), "#f4f1e6", "".join(
        line([(-hw + 44, hh - 190 + j * 46), (hw - 44, hh - 190 + j * 46)], 2.6, "#c1c9d6", taper=.0, wmin=1, seed=1260 + i * 5 + j) for j in range(1, 3)), w=3.6, seed=1250 + i))
    return "".join(s)


def stamp(txt, e):
    if e < 0:
        return ""
    k = 1.0 + 1.6 * max(0, 1 - e * 9)           # прилетает крупным и садится
    a = clamp(e / 0.05)
    s = []
    s.append(f'<g transform="rotate(-11) scale({k:.3f})" opacity="{a:.2f}">'
             f'<rect x="-120" y="-64" width="240" height="128" rx="18" fill="none" stroke="#d2321f" stroke-width="9"/>'
             f'<rect x="-104" y="-48" width="208" height="96" rx="10" fill="none" stroke="#d2321f" stroke-width="3.4" opacity=".8"/>'
             + text(0, 28, txt, 84, "#d2321f") + '</g>')
    return "".join(s)


def dima_hand(x, y, ang, press=0.0, sc=1.0):
    """Раскрытая рука Димы в горчичном рукаве (вид сверху): запястье в (x, y), пальцы по направлению ang (град, 180 — влево)."""
    d = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
    Wr = np.array([0.0, 0.0])
    E = Wr - d * 330
    S = Wr - d * 700
    o = dima.sleeve(S, E, Wr, False, 1300) + dima.open_hand(Wr + d * 2, d, False, 1320, -1, 0.25 + 0.5 * press)
    return f'<g transform="translate({f(x)} {f(y)}) scale({sc})">{o}</g>'


def frame_reports(t):
    s = [_ST["desk"]]
    # движение рук: листает — рука идёт вдоль стопки сверху вниз и смахивает листы вправо
    n = len(SHEETS)
    items = []
    for i, sh in enumerate(SHEETS):
        cx, cy = sh["c"]
        rot = sh["rot"]
        sc = 1.0
        # вход листов: из-за правого края с наклоном (с 27.45)
        tin = 27.4 + 0.18 * i
        u = ease_out(clamp((t - tin) / 0.3), 3)
        cx += 700 * (1 - u)
        rot += 12 * (1 - u)
        # ближний отчёт на «прошлые»
        if i == 2:
            k = ease_io(clamp((t - NEAR) / 0.4))
            cx += (540 - cx) * k
            cy += (780 - cy) * k
            rot *= 1 - k
            sc = 1.0 + 0.3 * k
        else:
            k = ease_io(clamp((t - NEAR) / 0.4))
            cy -= 260 * k
            cx -= 60 * k * (1 if i == 0 else -1)
        items.append((i, cx, cy, rot, sc))
    for i, cx, cy, rot, sc in items:
        sh = SHEETS[i]
        e = t - sh["t"]
        body = sheet_body(i)
        st = ""
        if e >= 0:
            st = f'<g transform="translate({SW / 2 - 150} {-SH_ / 2 + 120})">{stamp(sh["stamp"], e)}</g>'
        yb = 0.0
        if 0 <= e < 0.25:
            yb = 10 * math.sin(math.pi * e / 0.25) * (1 - e / 0.25)
        s.append(f'<g transform="translate({f(cx)} {f(cy + yb)}) rotate({rot:.2f}) scale({sc:.3f})">{body}{st}</g>')
    # рука листает
    ha = 180.0
    if t < 28.0:
        u = ease_out(clamp((t - 27.5) / 0.5), 3)
        hx, hy = 1500 - 700 * u, 1180 - 40 * u
    elif t < NEAR + 0.4:
        # три взмаха: к листам и смахивает
        ph = (t - 28.0) / 0.8
        hx = 820 + 60 * math.sin(ph * math.pi * 2.2)
        hy = 1130 - 120 * smooth(0, 1, ph) + 40 * math.sin(ph * 9)
    else:
        u = ease_io(clamp((t - NEAR - 0.4) / 0.5))
        hx, hy = 900 + 100 * u, 1000 + 160 * u + 8 * math.sin(t * 5)
        ha = 180 - 12 * u
    s.append(blob(ellipse_pts(hx - 80, hy + 90, 150, 26, 14), "#3a2410", .25, blur(10)))
    s.append(dima_hand(hx, hy, ha, 0.3 * smooth(NEAR + .4, NEAR + .8, t), 2.0))
    return "".join(s)


def frame(sid, t):
    if not _ST:
        lib.DEFS.append('<filter id="fShH" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                        '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
        _ST["desk"] = desk()
        _ST["nb"] = notebook()
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    dx, wrot, wu = (0.0, 0.0, 1.0)
    if sid in ("s12", "s14"):
        t0 = {"s12": 24.04, "s14": 27.6}[sid]
        dx, wrot, wu = whip_in(t, t0, 0.2, 700, 6)
    if sid == "s14":
        art = frame_reports(t)
        v = clamp((t - 27.6) / 2.28)
        sc_, cx_, cy_ = 1.0 + 0.06 * v, 540, 800 + 20 * v
        if t > NEAR:
            u = ease_io(clamp((t - NEAR) / 0.6))
            sc_ = 1.0 + 0.32 * u + 0.05 * v
            cx_, cy_ = 540, 800 + 80 * u
        sc_ *= punch(t, NEAR, 0.05, 7.0)
        sx, sy = shake(t, 28.22, 5)
        sx2, sy2 = shake(t, 28.55, 5)
        sx, sy = sx + sx2, sy + sy2
    else:
        art = frame_note(sid, t)
        if sid == "s12":
            v = clamp((t - 24.04) / 1.92)
            sc_, cx_, cy_ = 1.0 + 0.1 * ease_io(v), 560, 760
        else:
            v = ease_io(clamp((t - 25.96) / 1.64))
            sc_, cx_, cy_ = 1.1 + 0.4 * v, 560 + 40 * v, 760 + 60 * v
            sc_ *= punch(t, QPOP, 0.05, 7.0)
        sx, sy = shake(t, 24.04, 6) if sid == "s12" else shake(t, QPOP, 6)
    body = f'<g transform="{cam(cx_ + sx, cy_ + sy, sc_, wrot + 0.4 * math.sin(t * 0.9))}"><g transform="translate({f(dx)} 0)">{art}</g></g>'
    return svg(body + speed_streaks(wu, 540))
