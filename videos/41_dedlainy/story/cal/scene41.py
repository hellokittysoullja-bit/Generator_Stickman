"""Сцены агента B рилса 41 «всё в последнюю ночь»: s02 s08 s09 s12 s13 s16. frame(sid, t) -> SVG 1080×1920,
t — общее время ролика, удары — на словах voice/words.json.
s02  календарь ДЕКАБРЬ со стикером «КУРСОВАЯ»: дни пролетают листками, на «последнюю» рука красным маркером обводит 31-е,
     на «ночь» в клетке выскакивает луна (основа — scene_calendar рилсов 26/40, рука с маркером — hand.py рилса 40);
s08  тот же лист: бикфордов шнур змейкой через все дни к 31-му; на «сгорает» загорается, огонёк бежит, дни за ним
     темнеют; на «ночь» — вспышка в последнем дне, клочки бумаги, дым;
s09  дорога-таймлайн в перспективе на закате, флажок «СРОК» у горизонта; на «далеко» уезжает в точку; на переднем плане
     шезлонг с мозгом-персонажем (мозг рилсов 24–38 — brain_art/brain.py, ножки в кедах — scene_brain32 рилса 32);
s12  полоса из трёх недель, на ней человечек со стопкой листов; на «конце» в последней клетке шлёпается большой красный
     флажок (человечек — person.py рилса 32);
s13  под ней вторая полоса со вторым человечком; на «ровными», «каждую», «неделю» в конце недель — три зелёных флажка;
s16  днём у стены комнаты Димы: ФЕВРАЛЬ, пятницы с жёлтыми стикерами-флажками; рука в горчичном рукаве зелёным маркером
     ставит галочку на пятницу на «пятницу»."""
import json
import math
import os

import numpy as np

import brain as BR
import brain_art
import hand
import lib
import person
from calbase import CHECK, PAPER, Sheet, check_pts, wallpaper
from lib import (DEFS, INK, W, H, back_out, band, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg)

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, near):
    """Начало слова word, ближайшего к времени near."""
    c = [x["start"] for x in WORDS if x["word"].strip(".,?!«»").lower() == word]
    return min(c, key=lambda v: abs(v - near))


POSL = wt("последнюю", 2.0)        # 2.08
NOCH = wt("ночь", 2.6)             # 2.64
SGOR = wt("сгорает", 12.6)         # 12.64
NOCH2 = wt("ночь", 13.7)           # 13.68
DALEKO = wt("далеко", 15.0)        # 14.96
KONCE = wt("конце", 21.4)          # 21.44
ROVN = wt("ровными", 22.3)         # 22.32
KAZHD = wt("каждую", 23.3)         # 23.28
NEDEL = wt("неделю", 23.7)         # 23.68
PYATN = wt("пятницу", 30.4)        # 30.44

_ST = {}
RED = "#e0352b"
GREEN, GREEN_SH = "#2f9a4a", "#1f6f33"


def kick(t, times, amp=0.03, dec=16):
    s, rot = 1.0, 0.0
    for tt in times:
        q = t - tt
        if q >= 0:
            s *= 1 + amp * math.exp(-q * dec) * math.cos(q * 30)
            rot += amp * 18 * math.exp(-q * dec) * math.sin(q * 34)
    return s, rot


def shake(t, t0, amp, dec=9, fr=55):
    q = t - t0
    if q < 0:
        return 0.0, 0.0
    a = amp * math.exp(-q * dec)
    return a * math.sin(q * fr), a * math.cos(q * fr * 1.3)


def sway(t, sh, pivot, amp=1.0):
    a = amp * (0.35 * math.sin(t * 2.3) + 0.15 * math.sin(t * 3.7 + 1))
    return f'<g transform="rotate({f(a)} {f(pivot[0])} {f(pivot[1])})">{sh}</g>'


def lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def polyline_prefix(pts, u):
    """Начало ломаной до доли u её длины."""
    P = np.array(pts, float)
    seg = np.hypot(*np.diff(P, axis=0).T)
    L = seg.sum() * clamp(u)
    out = [tuple(P[0])]
    acc = 0.0
    for i, sl in enumerate(seg):
        if acc + sl >= L:
            v = (L - acc) / max(sl, 1e-6)
            out.append(tuple(P[i] + (P[i + 1] - P[i]) * v))
            return out
        out.append(tuple(P[i + 1]))
        acc += sl
    return out


def catmull(pts, n=10):
    pts = [tuple(p[:2]) for p in pts]
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (np.array(P[j], float) for j in (i - 1, i, i + 1, i + 2))
        for k in range(n):
            s = k / n
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3)))
    out.append(tuple(P[-2]))
    return out


def text(x, y, s, size, fill, anchor="middle", extra=""):
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="IDB" font-weight="900" font-size="{f(size)}" '
            f'fill="{fill}" {extra}>{s}</text>')


def hand_shadow_filter():
    DEFS.append('<filter id="fShH" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                '<feColorMatrix type="matrix" values="0 0 0 0 .1  0 0 0 0 .12  0 0 0 0 .06  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')


def marker_hand(px, py, ang, sc, sd, kind):
    """Рука Димы с маркером, кончик в (px, py), мягкая тень на стене."""
    return (f'<g transform="translate({f(px + 24)} {f(py + 32)}) scale({f(sc)})" opacity=".26" filter="url(#fShH)">{hand.hand(ang, sd, kind=kind)}</g>'
            + hand.draw(px, py, ang, sc, sd, kind=kind))


# ═══════════════════════════════════════════════ общий лист ДЕКАБРЬ (s02, s08)
DBOX = (110, 470, 970, 1290)
DEC = Sheet(12, DBOX, sd=12)
LAST = DEC.n                        # 31


def sticker_kursovaya(sd=0):
    """Жёлтый стикер «КУРСОВАЯ» на шапке листа справа, приклеен скотчем."""
    x0, y0 = 640, DBOX[1] - 34
    w, h = 300, 150
    rot = 5.0
    s = []
    s.append(blob([(x0 + 10, y0 + 14, 1), (x0 + w + 14, y0 + 18, 1), (x0 + w + 8, y0 + h + 18, 1), (x0 + 12, y0 + h + 12, 1)], "#2a1d0c", .3, blur(8)))
    inner = blob([(x0, y0 + h - 30), (x0 + w, y0 + h - 34), (x0 + w, y0 + h), (x0, y0 + h)], "#efc23a")
    inner += line([(x0 + w - 46, y0 + h), (x0 + w, y0 + h - 40)], 3, "#c99a20", seed=sd + 3)
    inner += text(x0 + w / 2, y0 + 96, "КУРСОВАЯ", 50, "#3a2a14", extra='letter-spacing="1"')
    pts = [(x0, y0, 1), (x0 + w, y0 + 2, 1), (x0 + w - 2, y0 + h - 40), (x0 + w - 46, y0 + h, 1), (x0 + 2, y0 + h, 1)]
    s.append(shape(pts, "#ffd84a", inner, w=4.2, seed=sd + 1))
    # загнутый уголок
    s.append(shape([(x0 + w - 2, y0 + h - 40, 1), (x0 + w - 46, y0 + h, 1), (x0 + w - 40, y0 + h - 34, 1)], "#f6e3a0", "", w=3, seed=sd + 2))
    # скотч
    tp = [(x0 + w / 2 - 60, y0 - 18, 1), (x0 + w / 2 + 56, y0 - 24, 1), (x0 + w / 2 + 60, y0 + 18, 1), (x0 + w / 2 - 56, y0 + 24, 1)]
    s.append(shape(tp, "#efe7cf", line([(x0 + w / 2 - 50, y0 - 6), (x0 + w / 2 + 50, y0 - 12)], 2, "#d8ccad", seed=sd + 5), w=2.4, seed=sd + 4))
    cx, cy = x0 + w / 2, y0 + h / 2
    return f'<g transform="rotate({f(rot)} {f(cx)} {f(cy)})">{"".join(s)}</g>'


def dec_number(d, col="#3a3330"):
    x, y = DEC.cell(d)
    c = (DEC.col0 + d - 1) % 7
    if col is None:
        col = "#c9554c" if c >= 5 else "#3a3330"
    return text(x, y + 17, str(d), 48, col)


def dec_static():
    pv = ((DBOX[0] + DBOX[2]) / 2, DBOX[1] - 196 * DEC.k)
    return DEC.shadow(), DEC.board(), DEC.page(numbers=False, name_left=True), pv


def circle31_pts():
    x, y = DEC.cell(LAST)
    rx, ry = DEC.cw * 0.6, DEC.rh * 0.6
    pts = []
    n = 26
    for j in range(int(n * 1.14) + 1):
        a = -2.3 + 2 * math.pi * j / n
        k = 1 + 0.05 * math.sin(j * 1.3) + 0.04 * j / n
        pts.append((x + rx * k * math.cos(a), y - 4 + ry * k * math.sin(a)))
    return pts


CIRC = circle31_pts()


def moon(x, y, r, e, sd=0):
    """Луна-месяц: выскакивает с перелётом (e — с момента появления), рядом две звёздочки."""
    if e <= 0:
        return ""
    sc = back_out(clamp(e / 0.28), 2.6)
    s = []
    g = rad_grad([(0, "#ffe9a0", .55), (1, "#ffe9a0", 0)], x, y, r * 1.6)
    s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 1.6 * sc)}" fill="url(#{g})"/>')
    pts = crescent(r)
    inner = blob([(-r, 0), (-r * .3, r * .8), (r * .3, r * .95), (-r, r)], "#e8b53a")
    body = shape(pts, "#ffd75a", inner, w=3.6, seed=sd)
    s.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(-18 + 6 * math.sin(e * 3))}) scale({f(sc)})">{body}</g>')
    for k, (dx, dy, rr) in enumerate(((-r * 1.6, -r * 0.9, r * .32), (r * 1.15, -r * 1.25, r * .26))):
        ee = e - 0.08 - 0.06 * k
        if ee > 0:
            ss = back_out(clamp(ee / 0.22), 3) * (1 + 0.12 * math.sin(e * 9 + k))
            s.append(star(x + dx, y + dy, rr * ss, sd + 5 + k))
    return "".join(s)


def crescent(r, n=28):
    """Месяц рогами вправо: круг r минус круг 0.82r, сдвинутый вправо-вверх. Наружная дуга — через левый край,
    внутренняя (вогнутая) — по левой стороне малого круга; на рогах углы."""
    cx2, cy2, r2 = 0.42 * r, -0.12 * r, 0.82 * r

    def outside(th):
        return math.hypot(r * math.cos(th) - cx2, r * math.sin(th) - cy2) >= r2
    lo, hi = 0.0, math.pi              # от π в сторону убывания угла: где дуга входит в малый круг
    for _ in range(40):
        m = (lo + hi) / 2
        if outside(math.pi - m):
            lo = m
        else:
            hi = m
    al = lo
    lo, hi = 0.0, math.pi
    for _ in range(40):
        m = (lo + hi) / 2
        if outside(math.pi + m):
            lo = m
        else:
            hi = m
    ar = lo
    ths = np.linspace(math.pi - al, math.pi + ar, n)            # низ рога → левый край → верхний рог
    outer = [(r * math.cos(th), r * math.sin(th)) for th in ths]
    pb, pt = outer[0], outer[-1]
    f_top = math.atan2(pt[1] - cy2, pt[0] - cx2) % (2 * math.pi)
    f_bot = math.atan2(pb[1] - cy2, pb[0] - cx2) % (2 * math.pi)
    if f_bot > f_top:
        f_bot -= 2 * math.pi
    inner = [(cx2 + r2 * math.cos(a), cy2 + r2 * math.sin(a)) for a in np.linspace(f_top, f_bot, 24)]
    return [pb + (1,)] + outer[1:-1] + [pt + (1,)] + inner[1:-1]


def star(x, y, r, sd=0, col="#ffd75a"):
    pts = []
    for j in range(8):
        a = math.radians(-90 + 45 * j)
        rr = r if j % 2 == 0 else r * 0.42
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return shape(pts, col, "", w=max(1.6, r * 0.14), seed=sd)


# ─────────────────────────────── s02
LEAF_T = [1.34 + 0.023 * (d - 1) for d in range(1, LAST)]       # дни 1–30 улетают листками
C_A, C_B = POSL, POSL + 0.36                                    # обводка 31-го


def leaf(d, e):
    """Листок дня d отрывается и улетает вверх-вправо, кувыркаясь (e — с момента отрыва)."""
    if e < 0 or e > 0.7:
        return ""
    x, y = DEC.cell(d)
    rs = np.random.RandomState(100 + d)
    vx, vy = rs.uniform(900, 1600), rs.uniform(-2100, -1500)
    dx = vx * e
    dy = vy * e + 0.5 * 1600 * e * e
    rot = rs.choice([-1, 1]) * (rs.uniform(200, 420) * e) + rs.uniform(-6, 6)
    sc = 0.9 + 0.12 * ease_out(clamp(e / 0.12))
    w2, h2 = DEC.cw * 0.42, DEC.rh * 0.42
    # листок слегка изгибается при отрыве
    bend = 8 * math.sin(min(1, e / 0.2) * math.pi)
    pts = [(-w2, -h2, 1), (w2, -h2, 1), (w2 + bend * .3, h2, 1), (-w2, h2 - bend * .4, 1)]
    inner = blob([(-w2, h2 * .25), (w2, h2 * .1), (w2, h2), (-w2, h2)], "#e9e1d0")
    inner += text(0, 17, str(d), 46, "#3a3330" if (DEC.col0 + d - 1) % 7 < 5 else "#c9554c")
    lf = shape(pts, "#fffdf6", inner, w=3.2, seed=200 + d)
    return f'<g transform="translate({f(x + dx)} {f(y + dy)}) rotate({f(rot)}) scale({f(sc)})">{lf}</g>'


def frame02(t):
    sh, board, page, pv = _ST["dec"]
    s = [_ST["wall"], sh]
    art = board + page + _ST["kurs"]
    # числа: ещё не прожитые — чёрные, прожитые — бледные с косой чертой карандашом
    for d in range(1, LAST + 1):
        gone = d < LAST and t >= LEAF_T[d - 1] + 0.04
        if gone:
            x, y = DEC.cell(d)
            art += dec_number(d, "#cfc5b5")
            art += line([(x - 26, y + 24), (x + 26, y - 20)], 3.4, "#a99e8e", taper=.4, wmin=.4, seed=300 + d)
        else:
            art += dec_number(d, None)
    # обводка 31-го
    u = ease_io(clamp((t - C_A) / (C_B - C_A)))
    if u > 0.01:
        art += line(polyline_prefix(CIRC, u), 13, RED, taper=.25, wmin=.5, seed=991)
    x31, y31 = DEC.cell(LAST)
    art += moon(x31 + 62, y31 - 52, 30, t - NOCH, 77)
    art += DEC.rings()
    s.append(sway(t, art, pv))
    # листки поверх
    for d in range(1, LAST):
        s.append(leaf(d, t - LEAF_T[d - 1]))
    # рука с маркером
    if 1.82 <= t <= C_B + 0.42:
        st = CIRC[0]
        if t < C_A:
            v = ease_out(clamp((t - 1.82) / (C_A - 1.82)), 2)
            tip = lerp((st[0] + 520, st[1] + 620), st, v)
        elif t < C_B:
            tip = polyline_prefix(CIRC, u)[-1]
        else:
            v = ease_in(clamp((t - C_B) / 0.4), 1.8)
            tip = lerp(CIRC[-1], (CIRC[-1][0] + 700, CIRC[-1][1] + 760), v)
        ang = -32 + 5 * math.sin(t * 7)
        s.append(marker_hand(tip[0], tip[1], ang, 1.05, 7, "marker"))
    return "".join(s)


def cam02(t):
    x31, y31 = DEC.cell(LAST)
    c0 = (540, 905)
    c1 = (x31 + 20, y31 - 10)
    v = ease_io(clamp((t - 1.98) / 0.62))
    sc = 1.04 + 0.05 * clamp((t - 1.3) / 0.7) + (1.78 - 1.09) * v + 0.04 * clamp((t - 2.6) / 0.8)
    cx = c0[0] + (c1[0] - c0[0]) * v + 5 * math.sin(t * 1.7)
    cy = c0[1] + (c1[1] - c0[1]) * v
    k, rot = kick(t, [C_B, NOCH], 0.03)
    rot += -1.6 * (1 - v) + 0.6 * v
    return cam(cx, cy, sc * k, rot)


# ─────────────────────────────── s08: бикфордов шнур
def fuse_path():
    """Змейка через все дни: строки поочерёдно слева направо и справа налево, повороты — у края клетки."""
    rows = {}
    for d in range(1, LAST + 1):
        r = (DEC.col0 + d - 1) // 7
        rows.setdefault(r, []).append(d)
    order = []
    for r in sorted(rows):
        ds = rows[r] if r % 2 == 0 else rows[r][::-1]
        order += ds
    off = 34
    pts, dmark = [], []
    x0, y0 = DEC.cell(order[0])
    pts.append((x0 - DEC.cw * 0.44, y0 + off + 4))            # хвостик шнура до первого дня
    for i, d in enumerate(order):
        x, y = DEC.cell(d)
        pts.append((x, y + off))
        dmark.append((d, len(pts) - 1))
        if i + 1 < len(order):
            nd = order[i + 1]
            nx, ny = DEC.cell(nd)
            if abs(ny - y) > 1:                                 # поворот на следующую строку
                side = 1 if nx >= x else -1
                if abs(nx - x) < 1:
                    side = 1 if (DEC.col0 + d - 1) % 7 >= 3 else -1
                ex = x + side * DEC.cw * 0.42
                pts.append((ex, y + off + DEC.rh * 0.25))
                pts.append((ex, ny + off - DEC.rh * 0.25))
    dense = catmull(pts, 8)
    # параметр по длине для каждого дня
    P = np.array(dense)
    acc = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    L = acc[-1]
    du = {}
    for d, idx in dmark:
        pt = np.array(pts[idx])
        j = int(np.argmin(np.hypot(*(P - pt).T)))
        du[d] = acc[j] / L
    return dense, du, acc / L


FUSE, FUSE_DU, FUSE_ACC = fuse_path()
F_A, F_B = SGOR, NOCH2


def fuse_u(t):
    x = clamp((t - F_A) / (F_B - F_A))
    return 0.35 * x + 0.65 * ease_in(x, 1.6)


def fuse_at(u):
    j = int(np.searchsorted(FUSE_ACC, u))
    j = max(1, min(len(FUSE) - 1, j))
    a, b = FUSE_ACC[j - 1], FUSE_ACC[j]
    v = (u - a) / max(b - a, 1e-9)
    p = lerp(FUSE[j - 1], FUSE[j], v)
    d = (FUSE[j][0] - FUSE[j - 1][0], FUSE[j][1] - FUSE[j - 1][1])
    return p, math.atan2(d[1], d[0])


def cord(pts, sd=0):
    if len(pts) < 2:
        return ""
    s = [line(pts, 17, INK, taper=.02, wmin=.95, seed=sd), line(pts, 11, "#c9a066", taper=.02, wmin=.95, seed=sd + 1)]
    # витки
    P = np.array(pts)
    acc = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    n = int(acc[-1] / 13)
    for k in range(1, n):
        L = k * 13
        j = int(np.searchsorted(acc, L))
        j = max(1, min(len(P) - 1, j))
        v = (L - acc[j - 1]) / max(acc[j] - acc[j - 1], 1e-6)
        p = P[j - 1] + (P[j] - P[j - 1]) * v
        tg = P[j] - P[j - 1]
        tg = tg / (np.hypot(*tg) + 1e-9)
        nn = np.array([-tg[1], tg[0]])
        a = p + nn * 4.5 - tg * 3
        b = p - nn * 4.5 + tg * 3
        s.append(f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="#8a6232" stroke-width="2.2" stroke-linecap="round"/>')
    return "".join(s)


def ash(pts, sd=0):
    if len(pts) < 2:
        return ""
    return line(pts, 12, INK, taper=.02, wmin=.95, seed=sd) + line(pts, 6, "#5a524e", taper=.02, wmin=.95, seed=sd + 1)


def flame(x, y, t, k=1.0, sd=0):
    """Огонёк шнура: язык пламени дрожит, искры летят во все стороны (кадр — своё зерно)."""
    fl = 1 + 0.12 * math.sin(t * 47) + 0.08 * math.sin(t * 71 + 1)
    lean = 6 * math.sin(t * 23)
    s = []
    g = rad_grad([(0, "#fff2b0", .95), (.4, "#ffb347", .5), (1, "#ff7a2a", 0)], x, y - 10 * k, 90 * k)
    s.append(f'<circle cx="{f(x)}" cy="{f(y - 10 * k)}" r="{f(90 * k)}" fill="url(#{g})"/>')

    def tongue(h, w, col, sdd, ink=True):
        pts = [(x - w, y), (x - w * 0.9, y - h * 0.35), (x - w * 0.3 + lean * .4, y - h * 0.75), (x + lean, y - h, 1),
               (x + w * 0.45 + lean * .4, y - h * 0.62), (x + w * 0.95, y - h * 0.3), (x + w, y), (x, y + w * 0.7)]
        return shape(pts, col, "", w=3.2 * k, seed=sdd, ink=ink)
    s.append(tongue(58 * k * fl, 20 * k, "#ff8a2a", sd))
    s.append(tongue(36 * k * fl, 12 * k, "#ffd23f", sd + 1, ink=False))
    s.append(tongue(16 * k * fl, 6 * k, "#fff6d0", sd + 2, ink=False))
    rs = np.random.RandomState(int(t * 30 + 0.5) * 7 + sd)
    for j in range(7):
        a = rs.uniform(-math.pi, 0.2)
        r0, r1 = rs.uniform(14, 30) * k, rs.uniform(40, 80) * k
        s.append(line([(x + r0 * math.cos(a), y - 10 * k + r0 * math.sin(a)), (x + r1 * math.cos(a), y - 10 * k + r1 * math.sin(a))],
                      rs.uniform(3, 5.5) * k, "#ffc23a" if j % 2 else "#ff8a2a", taper=.6, seed=sd + 10 + j))
    return "".join(s)


def char_cell(d, e, sd=0):
    """Клетка дня темнеет за огнём: опалённая клетка с рваным краем, гарь гуще к краю (e — с момента, как огонь прошёл)."""
    if e <= 0:
        return ""
    x, y = DEC.cell(d)
    u = ease_out(clamp(e / 0.18))
    rs = np.random.RandomState(400 + d)
    hw, hh = DEC.cw * 0.47, DEC.rh * 0.46
    pts = []
    for (ax, ay, bx, by) in ((-1, -1, 1, -1), (1, -1, 1, 1), (1, 1, -1, 1), (-1, 1, -1, -1)):
        for k in range(6):
            v = k / 6
            j = rs.uniform(-1, 1) * 5
            px, py = ax + (bx - ax) * v, ay + (by - ay) * v
            pts.append((x + px * hw + (j if ax == bx else 0), y + py * hh + (j if ay == by else 0)))
    col = mix("#e6d9c2", "#5e4a3e", u)
    edge = mix("#e6d9c2", "#3a2a22", u)
    g = rad_grad([(0, col, 1), (.75, col, 1), (1, edge, 1)], x, y, hw * 1.25, hh * 1.25)
    return blob(pts, f"url(#{g})")


def smoke_puff(x, y, r, sd=0, col="#cfc9c4"):
    rs = np.random.RandomState(sd)
    s = []
    for j in range(4):
        a = 2 * math.pi * j / 4 + rs.uniform(-.3, .3)
        rr = r * rs.uniform(0.55, 0.75)
        s.append(ellipse_pts(x + r * 0.5 * math.cos(a), y + r * 0.45 * math.sin(a), rr, rr * 0.9, 12))
    out = "".join(shape(p, col, "", w=max(1.5, r * 0.07), seed=sd + 1 + j) for j, p in enumerate(s))
    out += "".join(blob(ellipse_pts(x - r * .2 + r * 0.5 * math.cos(2 * math.pi * j / 4), y - r * .25 + r * 0.45 * math.sin(2 * math.pi * j / 4),
                                    r * .28, r * .2, 10), "#ece8e4") for j in range(4))
    return out


def blast(x, y, e, sd=0):
    """Вспышка в последнем дне: звезда растёт и схлопывается, клочки бумаги разлетаются, дым поднимается."""
    if e < 0:
        return "", ""
    back, front = [], []
    # пятно гари на месте клетки (держится)
    rs = np.random.RandomState(sd)
    pts = []
    for j in range(20):
        a = 2 * math.pi * j / 20
        rr = rs.uniform(0.85, 1.12)
        pts.append((x + DEC.cw * 0.62 * rr * math.cos(a), y + DEC.rh * 0.62 * rr * math.sin(a)))
    g = rad_grad([(0, "#140c08", 1), (.6, "#2a1a12", 1), (1, "#5a3a24", 1)], x, y, DEC.cw * 0.7)
    back.append(shape(pts, f"url(#{g})", "", w=3.6, seed=sd + 1, ink_color="#1a100a"))
    # тлеющий край
    for j in range(0, 20, 2):
        p = pts[j]
        glow = 0.5 + 0.5 * math.sin(e * 12 + j)
        back.append(blob(ellipse_pts(p[0], p[1], 6, 4, 8), mix("#ff7a2a", "#ffd23f", glow)))
    # звезда вспышки
    if e < 0.28:
        if e < 0.06:
            r = 40 + 210 * ease_out(e / 0.06)
        else:
            r = 250 * (1 - ease_in((e - 0.06) / 0.22, 1.5))
        if r > 4:
            g2 = rad_grad([(0, "#ffffff", .95), (.35, "#fff2b0", .7), (1, "#ffb347", 0)], x, y, r * 1.6)
            front.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 1.6)}" fill="url(#{g2})"/>')
            sp = []
            for j in range(20):
                a = math.radians(-90 + 18 * j) + 0.08 * math.sin(j * 3)
                rr = r if j % 2 == 0 else r * 0.48
                sp.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
            front.append(shape(sp, "#ffd23f", shape([(x + (p[0] - x) * .55, y + (p[1] - y) * .55, 1) for p in sp], "#fff6d0", "", ink=False),
                               w=5, seed=sd + 3))
    # клочки бумаги
    for j in range(16):
        r2 = np.random.RandomState(sd + 50 + j)
        a = r2.uniform(-math.pi, 0.3)
        v = r2.uniform(700, 1500)
        dx = math.cos(a) * v * e
        dy = math.sin(a) * v * e + 0.5 * 2400 * e * e
        rot = r2.uniform(-1, 1) * 900 * e
        sz = r2.uniform(14, 28)
        q = [(-sz, -sz * .7, 1), (sz * .9, -sz * .6, 1), (sz * .7, sz * .8, 1), (-sz * .8, sz * .5, 1)]
        burnt = j % 3 == 0
        piece = shape(q, "#3a2a20" if burnt else "#f6efe0", blob([(-sz, sz * .1), (sz, -sz * .1), (sz, sz), (-sz, sz)], "#8a6a50" if not burnt else "#1e140e"),
                      w=2.4, seed=sd + 70 + j)
        front.append(f'<g transform="translate({f(x + dx)} {f(y + dy)}) rotate({f(rot)})">{piece}</g>')
    # дым
    for j in range(6):
        r3 = np.random.RandomState(sd + 90 + j)
        ee = e - 0.05 - 0.04 * j
        if ee <= 0:
            continue
        px = x + r3.uniform(-70, 70) + 30 * math.sin(ee * 2 + j)
        py = y - 40 - 260 * ee - r3.uniform(0, 40)
        rr = (30 + 60 * ease_out(clamp(ee / 0.8))) * r3.uniform(0.8, 1.2)
        front.append(smoke_puff(px, py, rr, sd + 100 + j * 10, "#bdb6b0" if j % 2 else "#cfc9c4"))
    return "".join(back), "".join(front)


def frame08(t):
    sh, board, page, pv = _ST["dec"]
    s = [_ST["wall"], sh]
    art = board + page + _ST["kurs"]
    u = fuse_u(t) if t >= F_A else 0.0
    burning = F_A <= t < F_B
    for d in range(1, LAST + 1):
        tp = None
        if t >= F_A:
            # когда огонь прошёл день d
            du = FUSE_DU[d]
            if u >= du:
                # обратное время: найдём момент прохождения
                lo, hi = F_A, F_B
                for _ in range(18):
                    mid = (lo + hi) / 2
                    if fuse_u(mid) < du:
                        lo = mid
                    else:
                        hi = mid
                tp = hi
        if d == LAST:
            continue
        if tp is not None:
            art += char_cell(d, t - tp)
            art += dec_number(d, "#f3e6d0" if t - tp > 0.1 else "#3a3330")
        else:
            art += dec_number(d, None)
    # 31-е: до вспышки — число в красном кружке и луна
    x31, y31 = DEC.cell(LAST)
    if t < F_B:
        art += dec_number(LAST, None)
        art += line(CIRC, 13, RED, taper=.25, wmin=.5, seed=991)
    # шнур: сгоревшая часть — пепел, остальное — шнур
    j = int(np.searchsorted(FUSE_ACC, u))
    if u <= 0:
        art += cord(FUSE, 31)
    else:
        p, _ = fuse_at(min(u, 1.0))
        burnt = FUSE[:j] + [p]
        rest = [p] + FUSE[j:]
        art += ash(burnt, 33)
        if u < 1:
            art += cord(rest, 31)
    # дымок за огнём
    if burning:
        for k in range(5):
            uu = u - 0.025 * (k + 1)
            if uu <= 0:
                continue
            q, _ = fuse_at(uu)
            age = 0.06 * (k + 1)
            art += smoke_puff(q[0] + 6 * math.sin(t * 5 + k), q[1] - 20 - 160 * age, 10 + 40 * age, 600 + k)
    back, front = blast(x31, y31, t - F_B, 700)
    art += back
    art += DEC.rings()
    s.append(sway(t, art, pv, 0.6))
    if t < F_B and t >= F_A - 0.05:
        p, _ = fuse_at(max(u, 0.0))
        ign = back_out(clamp((t - F_A + 0.05) / 0.12), 2.5)
        s.append(f'<g transform="translate({f(p[0])} {f(p[1])}) scale({f(ign)}) translate({f(-p[0])} {f(-p[1])})">{flame(p[0], p[1], t, 1.35, 800)}</g>')
    elif t < F_A - 0.05:
        # кончик шнура тлеет, ждёт
        p = FUSE[0]
        s.append(shape(ellipse_pts(p[0] - 4, p[1], 7, 6, 8), mix("#c9a066", "#ff8a2a", 0.5 + 0.5 * math.sin(t * 9)), "", w=2.4, seed=811))
    s.append(front)
    return "".join(s)


def cam08(t):
    u = fuse_u(t) if t >= F_A else 0.0
    if t < F_A:
        fy = FUSE[0][1] + 30 * clamp((t - 11.8) / 0.84)
        fx = FUSE[0][0]
    else:
        (fx, fy), _ = fuse_at(min(u, 1.0))
    x31, y31 = DEC.cell(LAST)
    sc = 1.1 + 0.05 * clamp((t - 11.8) / 0.84) + 0.06 * clamp((t - F_A) / (F_B - F_A))
    cx = 540 + (fx - 540) * 0.08
    cy = 0.55 * fy + 0.45 * 960 - 40
    v = ease_out(clamp((t - F_B) / 0.4))
    cx += (x31 - cx) * 0.25 * v
    cy += (y31 - 160 - cy) * v
    k, rot = kick(t, [F_B], 0.07, 9)
    k2, _ = kick(t, [F_A], 0.025, 14)
    dx, dy = shake(t, F_B, 22, 7, 60)
    return cam(cx + dx, cy + dy, sc * k * k2, rot + 0.8 * math.sin(t * 1.1))


# ═══════════════════════════════════════════════ s16: ФЕВРАЛЬ, пятницы
FBOX = (150, 470, 930, 1290)
FEB = Sheet(2, FBOX, sd=22)
FRIS = [d for d in range(1, FEB.n + 1) if (FEB.col0 + d - 1) % 7 == 4]      # 5 12 19 26
DONE = FRIS[:2]
NOW = FRIS[2]
NEXT = FRIS[3]
K_A, K_B = PYATN, PYATN + 0.22


CKX, CKY, CKR = 44.0, 32.0, 0.86       # галочка правее числа (число пятницы читается)


def fri_flag(d, t, sd=0, wiggle=0.0):
    """Жёлтый стикер-флажок на пятнице: прямоугольник с вырезом-«ласточкиным хвостом», торчит из угла клетки."""
    x, y = FEB.cell(d)
    bx, by = x - FEB.cw * 0.46, y - FEB.rh * 0.46
    a = -6 + wiggle
    pts = [(0, 0, 1), (46, 0, 1), (36, 13), (46, 26, 1), (0, 26, 1)]
    g = shape(pts, "#ffd84a", blob([(0, 16), (42, 16), (46, 26), (0, 26)], "#efc23a"), w=3.0, seed=sd)
    shd = blob([(3, 5, 1), (49, 5, 1), (49, 31, 1), (3, 31, 1)], "#2a1d0c", .25, blur(3))
    return f'<g transform="translate({f(bx)} {f(by)}) rotate({f(a)})">{shd}{g}</g>'


def check_stroke(x, y, r, u, sd, col=GREEN, rot=-4.0):
    pts = catmull(check_pts(x, y, r, rot), 6)
    if u <= 0.01:
        return ""
    return line(polyline_prefix(pts, u), r * 0.34, col, taper=.4, wmin=.45, seed=sd, peak=.42)


def day_wall():
    """Стена комнаты Димы днём: обои рилса 40 + солнечный свет из окна слева (рама даёт тень-крест)."""
    s = [wallpaper()]
    g = lin_grad([(0, "#fff1c8", .55), (1, "#fff1c8", 0)], 0, 0, 1, 0.3)
    poly = [(-400, 150), (520, 300), (560, 1700), (-400, 1900)]
    s.append(f'<path d="{lib.fill_d(poly)}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(blob([(-400, 960), (540, 980), (545, 1010), (-400, 1000)], "#7b8a6a", .22, blur(10)))
    s.append(blob([(180, 150), (215, 160), (240, 1720), (205, 1740)], "#7b8a6a", .22, blur(10)))
    # открытка на кнопке справа вверху и розетка внизу — обжитая стена
    px, py = 905, 250
    pc = shape([(px - 80, py - 50, 1), (px + 80, py - 56, 1), (px + 84, py + 60, 1), (px - 76, py + 64, 1)], "#f4efe2",
               blob(rect_pts(px - 62, py - 36, px + 62, py + 40), "#8fc0d8") + blob([(px - 62, py + 40), (px - 20, py), (px + 10, py + 22), (px + 40, py - 10), (px + 62, py + 40)], "#5f9a62"),
               w=3.4, seed=1601)
    s.append(blob([(px - 70, py - 40, 1), (px + 96, py - 46, 1), (px + 100, py + 76, 1), (px - 64, py + 80, 1)], "#1d2412", .3, blur(8)))
    s.append(pc)
    s.append(shape(ellipse_pts(px, py - 52, 11, 11, 10), "#e2584a", blob(ellipse_pts(px - 4, py - 56, 4, 3, 8), "#f7a08f"), w=2.6, seed=1602))
    return "".join(s)


def frame16(t):
    s = [_ST["daywall"], _ST["fshadow"]]
    pv = ((FBOX[0] + FBOX[2]) / 2, FBOX[1] - 196 * FEB.k)
    art = _ST["fboard"] + _ST["fpage"]
    r = FEB.rcheck()
    for d in DONE:
        x, y = FEB.cell(d)
        art += check_stroke(x + CKX, y + CKY, r * CKR, 1.0, 1700 + d)
    x, y = FEB.cell(NOW)
    x, y = x + CKX, y + CKY
    r *= CKR
    u = ease_in(clamp((t - K_A) / (K_B - K_A)), 1.2)
    art += check_stroke(x, y, r, u, 1700 + NOW)
    for d in FRIS:
        wig = 0.0
        if d == NEXT:
            wig = 4 * math.sin(t * 5) * smooth(K_B, K_B + 0.3, t)
        if d == NOW and t > K_B:
            wig = 7 * math.exp(-(t - K_B) * 7) * math.sin((t - K_B) * 30)
        art += fri_flag(d, t, 1750 + d, wig)
    # искорки от свежей галочки
    if t > K_B:
        e = t - K_B
        if e < 0.3:
            rs = np.random.RandomState(9)
            for j in range(6):
                a = math.radians(-150 + j * 30 + rs.uniform(-8, 8))
                v = e / 0.3
                d0, d1 = r * (1.1 + 0.5 * v), r * (1.45 + 0.7 * v)
                art += line([(x + d0 * math.cos(a), y - 10 + d0 * math.sin(a)), (x + d1 * math.cos(a), y - 10 + d1 * math.sin(a))],
                            9 * (1 - v) + 1.5, "#f2b33a", taper=.5, seed=1780 + j)
    art += FEB.rings()
    s.append(sway(t, art, pv, 0.7))
    # рука с зелёным маркером
    pts = catmull(check_pts(x, y, r, -4.0), 6)
    if 29.85 <= t <= K_B + 0.6:
        if t < K_A:
            v = ease_out(clamp((t - 29.85) / (K_A - 29.85)), 2.4)
            tip = lerp((pts[0][0] + 560, pts[0][1] + 700), pts[0], v)
            tip = (tip[0], tip[1] - 14 * math.sin(math.pi * v))
        elif t < K_B:
            tip = polyline_prefix(pts, u)[-1]
        else:
            v = ease_in(clamp((t - K_B) / 0.55), 1.7)
            tip = lerp(pts[-1], (pts[-1][0] + 620, pts[-1][1] + 760), v)
            tip = (tip[0], tip[1] - 40 * math.sin(math.pi * min(v * 2, 1)))
        ang = -30 + 4 * math.sin(t * 6)
        s.append(marker_hand(tip[0], tip[1], ang, 1.05, 9, "marker_g"))
    return "".join(s)


def cam16(t):
    x, y = FEB.cell(NOW)
    c0 = (540, 900)
    c1 = (x - 40, y + 60)
    v = ease_io(clamp((t - 28.0) / 2.35))
    sc = 1.02 + 0.6 * v
    cx = c0[0] + (c1[0] - c0[0]) * v + 5 * math.sin(t * 1.3)
    cy = c0[1] + (c1[1] - c0[1]) * v
    k, rot = kick(t, [K_B], 0.04, 11)
    return cam(cx, cy, sc * k, rot + 1.2 * (1 - v) - 0.4)


# ═══════════════════════════════════════════════ s09: дорога-таймлайн
HOR = 700.0
FOC, HC = 900.0, 300.0
ROAD_HW = 260.0


def proj(X, Z):
    return (540 + FOC * X / Z, HOR + FOC * HC / Z)


def sky09():
    s = []
    lin_grad([(0, "#f6dcb4", 1), (.55, "#f7c79a", 1), (1, "#f39f78", 1)], 0, 0, 0, 1, gid="gSky41")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{HOR + 920}" fill="url(#gSky41)"/>')
    # солнце у горизонта справа
    g = rad_grad([(0, "#fff3c8", .9), (.4, "#ffe2a0", .45), (1, "#ffd08a", 0)], 820, HOR - 70, 420)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{HOR + 920}" fill="url(#{g})"/>')
    s.append(shape(ellipse_pts(820, HOR - 40, 96, 96, 28), "#ffe7a8", blob(ellipse_pts(850, HOR - 10, 80, 50, 18), "#ffd48a"), w=4, seed=901))
    # облака-полоски
    for k, (x, y, w) in enumerate(((240, 330, 220), (700, 240, 180), (120, 520, 160), (960, 470, 150))):
        pts = [(x - w, y + 10, 1), (x - w * .6, y - 14), (x - w * .1, y - 26), (x + w * .5, y - 18), (x + w, y + 8, 1)]
        s.append(shape(pts, "#fbe9cf", blob([(x - w, y + 10), (x + w, y + 8), (x + w * .5, y + 2), (x - w * .5, y + 4)], "#f0cfae"), w=3.4, seed=910 + k))
    return "".join(s)


def ground09():
    s = []
    lin_grad([(0, "#c6b77a", 1), (.3, "#b7ab6c", 1), (1, "#9a9a5a", 1)], 0, 0, 0, 1, gid="gGr41")
    s.append(f'<rect x="-900" y="{HOR}" width="{W + 1800}" height="{H + 900 - HOR}" fill="url(#gGr41)"/>')
    # дальние холмы на горизонте
    s.append(shape([(-900, HOR + 2, 1), (-600, HOR - 40), (-200, HOR - 22), (150, HOR - 52), (420, HOR - 26), (700, HOR - 46), (1050, HOR - 30), (1400, HOR - 50),
                    (1980, HOR + 2, 1)], "#a9a46c", "", w=3.4, seed=920))
    # кустики вдоль дороги
    rs = np.random.RandomState(3)
    for k in range(14):
        side = -1 if k % 2 else 1
        Z = 900 + 600 * (k // 2) + rs.uniform(-150, 150)
        X = side * (ROAD_HW + rs.uniform(140, 520))
        x, y = proj(X, Z)
        r = 60 * FOC / Z
        s.append(shape(ellipse_pts(x, y - r * .5, r * 1.2, r * .7, 12), "#7f9a52", blob(ellipse_pts(x + r * .3, y - r * .2, r * .8, r * .4, 10), "#678243"),
                       w=max(1.2, 3.6 * FOC / Z * 1.6), seed=930 + k))
    return "".join(s)


def road09(t):
    s = []
    zn, zf = 260.0, 60000.0
    L = [proj(-ROAD_HW, zn) + (1,), proj(-ROAD_HW, zf) + (1,), proj(ROAD_HW, zf) + (1,), proj(ROAD_HW, zn) + (1,)]
    g = lin_grad([(0, "#9a8f94", 1), (1, "#6e6574", 1)], 0, 0, 0, 1)
    s.append(blob(L, f"url(#{g})"))
    # обочины
    for sd, side in ((941, -1), (942, 1)):
        a, b = proj(side * ROAD_HW, zn), proj(side * ROAD_HW, zf)
        a2, b2 = proj(side * (ROAD_HW + 26), zn), proj(side * (ROAD_HW + 26), zf)
        s.append(blob([a + (1,), b + (1,), b2 + (1,), a2 + (1,)], "#e8dcc4"))
        s.append(line([a2, proj(side * (ROAD_HW + 26), 9000)], 5, INK, taper=1.0, wmin=.2, seed=sd + 5, peak=0.0))
    # деления таймлайна — плывут к нам медленно (время идёт)
    step = 420.0
    off = (t * 260.0) % step
    Z = zn + step - off
    k = 0
    while Z < 26000:
        sc = FOC / Z
        a, b = proj(-ROAD_HW * 0.82, Z), proj(ROAD_HW * 0.82, Z)
        w = 22 * sc
        s.append(blob([(a[0], a[1] - w * .5, 1), (b[0], b[1] - w * .5, 1), (b[0], b[1] + w * .5, 1), (a[0], a[1] + w * .5, 1)], "#f4ead6"))
        Z += step
        k += 1
    # осевая — короткий штрих по центру каждого деления
    return "".join(s)


def flag09(t):
    """Флажок «СРОК»: у горизонта; на «далеко» отъезжает и становится точкой."""
    e = t - DALEKO
    Z0, Z1 = 11000.0, 90000.0
    v = ease_in_out_back(clamp(e / 0.55)) if e > 0 else 0.0
    Z = Z0 * (Z1 / Z0) ** v
    sc = FOC / Z
    x, y = proj(0, Z)
    hop = 0.0
    pole = 1500 * sc
    wave = math.sin(t * 6) * 40 * sc
    s = []
    top = (x, y - pole)
    s.append(line([(x, y + hop), top], max(1.2, 46 * sc), INK, taper=.02, wmin=.95, seed=950))
    fw, fh = 1100 * sc, 680 * sc
    fl = [(top[0], top[1], 1), (top[0] + fw * .5, top[1] + wave * .6), (top[0] + fw, top[1] + wave, 1), (top[0] + fw, top[1] + fh + wave, 1),
          (top[0] + fw * .5, top[1] + fh + wave * .6), (top[0], top[1] + fh, 1)]
    inner = ""
    if fw > 40:
        inner = text(top[0] + fw / 2, top[1] + fh * 0.66 + wave * .6, "СРОК", fh * 0.52, "#fff4e6")
    s.append(shape(fl, "#e0352b", blob([(top[0], top[1] + fh * .62), (top[0] + fw, top[1] + fh * .62 + wave), (top[0] + fw, top[1] + fh + wave), (top[0], top[1] + fh)],
                                       "#b8281f") + inner, w=max(1.0, 40 * sc), seed=951))
    # шлейф скорости при отъезде
    if 0.0 < e < 0.5:
        a = 1 - e / 0.5
        for j in range(3):
            yy = top[1] + fh * (0.2 + 0.3 * j)
            s.append(line([(top[0] - 20 - 60 * a, yy), (top[0] - 4, yy)], 4 * a + 1, "#fff4e6", taper=.6, seed=955 + j))
    return "".join(s)


def ease_in_out_back(u, s=1.2):
    u = clamp(u)
    if u < 0.5:
        q = 2 * u
        return 0.5 * (q * q * ((s + 1) * q - s))
    q = 2 * u - 2
    return 0.5 * (q * q * ((s + 1) * q + s) + 2)


# шезлонг и мозг (шезлонг сбоку: изножье влево, к дороге; мозг полулёжа лицом влево, к флажку)
GY = 1262.0
LEG = 186
SKIN, SKIN_SH = BR.SKIN, BR.SKIN_SH
WOOD, WOOD_SH, WOOD_HI = "#c98a4a", "#9a6330", "#e3ab6c"
TOPB = (935.0, 740.0)              # верхняя перекладина (на ней висит полотно)
FRB = (606.0, 1094.0)              # передняя перекладина
SAGC = (745.0, 1200.0)             # провис полотна (контрольная точка)
REAR = (1020.0, GY)                # задняя нога на земле
FRONT = (590.0, GY)                # передняя нога на земле
RAIL = (984.0, 1150.0)             # куда упирается нижняя планка на задней ноге


def shoe(F, face, sc, sd):
    up = [(-20, -6), (8, -10), (24, 2), (42, 12), (46, 26, 1), (-24, 26, 1), (-27, 10)]
    inner = blob([(-30, 17), (50, 17), (50, 30), (-30, 30)], "#ff8a3d")
    inner += blob([(-8, 4), (18, -2), (34, 10), (20, 12), (0, 10)], "#3d7fe0")
    inner += line([(4, -6), (14, 2)], 2.6, INK, seed=sd + 3)
    s = shape(up, "#f6f3ec", inner, w=3.4, seed=sd)
    return f'<g transform="translate({f(F[0])} {f(F[1])}) rotate({f(-12 * face)}) scale({f(face * sc)} {f(sc)})">{s}</g>'


def bleg(Hp, F, sc, face=-1, sd=0):
    """Ножка мозга (рилс 32): колено вверх."""
    Hp, F = np.array(Hp, float), np.array(F, float)
    L = LEG * sc
    d = F - Hp
    dist = np.linalg.norm(d) + 1e-6
    if dist > L * 0.995:
        F = Hp + d / dist * L * 0.995
        d = F - Hp
        dist = L * 0.995
    a = L / 2
    hh = math.sqrt(max(a * a - (dist / 2) ** 2, 0))
    n = np.array([-d[1], d[0]]) / dist
    if n[1] > 0:
        n = -n
    K = (Hp + F) / 2 + n * hh
    pts = [tuple(Hp), tuple((Hp + K) / 2), tuple(K), tuple((K + F) / 2), tuple(F)]
    pl = band(pts, 30 * sc, 24 * sc, step=4, wmid=27 * sc, cap=True)
    shp = band([(x + 5 * sc, y) for x, y in pts], 11 * sc, 8 * sc, step=4, wmid=10 * sc, cap=False)
    return shape(pl, SKIN, blob(shp, SKIN_SH, .85), w=3.6 * sc, seed=sd) + shoe((F[0], F[1] - 4 * sc), face, sc * 1.05, sd + 5)


def bar(p0, p1, w, sd, col=WOOD, sh=WOOD_SH):
    """Деревянная планка от p0 до p1 (толщина w), тень по нижнему краю."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    pts = [(p0[0] + nx, p0[1] + ny, 1), (p1[0] + nx, p1[1] + ny, 1), (p1[0] - nx, p1[1] - ny, 1), (p0[0] - nx, p0[1] - ny, 1)]
    inner = blob([(p0[0] + nx * .2, p0[1] + ny * .2), (p1[0] + nx * .2, p1[1] + ny * .2), (p1[0] + nx, p1[1] + ny), (p0[0] + nx, p0[1] + ny)], sh, .9)
    inner += line([(p0[0] - nx * .5, p0[1] - ny * .5), (p1[0] - nx * .5, p1[1] - ny * .5)], 2.4, WOOD_HI, seed=sd + 1, op=.9)
    return shape(pts, col, inner, w=3.6, seed=sd)


def peg(p, r, sd):
    return shape(ellipse_pts(p[0], p[1], r, r, 12), WOOD_SH, blob(ellipse_pts(p[0] - r * .25, p[1] - r * .25, r * .45, r * .45, 8), WOOD_HI), w=3, seed=sd)


def sling_curve(n=24):
    return [((1 - u) ** 2 * TOPB[0] + 2 * (1 - u) * u * SAGC[0] + u * u * FRB[0],
             (1 - u) ** 2 * TOPB[1] + 2 * (1 - u) * u * SAGC[1] + u * u * FRB[1]) for u in np.linspace(0, 1, n)]


def chair_back():
    """Дальняя сторона рамы и полотно (полосами вдоль)."""
    s = [blob(ellipse_pts(810, GY + 6, 250, 26, 20), "#4d4a2a", .4, blur(8))]
    o = (40, -28)

    def O(p):
        return (p[0] + o[0], p[1] + o[1])
    s.append(bar(O(TOPB), O(REAR), 22, 990, WOOD_SH, "#7e4f24"))
    s.append(bar(O(FRB), O(FRONT), 22, 991, WOOD_SH, "#7e4f24"))
    # полотно: полоса шириной 34/28 (в 3/4 видна лицевая сторона), красные полосы вдоль
    C = sling_curve()
    C2 = [(x + o[0], y + o[1]) for x, y in C]
    poly = [C[0] + (1,)] + C[1:-1] + [C[-1] + (1,), C2[-1] + (1,)] + C2[-2:0:-1] + [C2[0] + (1,)]
    inner = ""
    for a0, a1 in ((0.1, 0.3), (0.45, 0.65), (0.8, 1.0)):
        A = [(x + o[0] * a0, y + o[1] * a0) for x, y in C]
        B = [(x + o[0] * a1, y + o[1] * a1) for x, y in C]
        inner += blob(A + B[::-1], "#e04a3a")
    s.append(shape(poly, "#f3ead6", inner, w=4.2, seed=995))
    s.append(peg(O(TOPB), 14, 996))
    s.append(peg(O(FRB), 14, 997))
    return "".join(s)


def sling_lip():
    """Ближний край полотна на сиденье — перед мозгом: мозг сидит В шезлонге, а не висит перед ним."""
    C = sling_curve(40)[25:]
    o = (40, -28)
    A = [(x + o[0] * 0.0, y + o[1] * 0.0) for x, y in C]
    B = [(x + o[0] * 0.55, y + o[1] * 0.55) for x, y in C]
    poly = [A[0] + (1,)] + A[1:-1] + [A[-1] + (1,), B[-1] + (1,)] + B[-2:0:-1] + [B[0] + (1,)]
    M0 = [(x + o[0] * 0.18, y + o[1] * 0.18) for x, y in C]
    M1 = [(x + o[0] * 0.38, y + o[1] * 0.38) for x, y in C]
    inner = blob(M0 + M1[::-1], "#e04a3a")
    return shape(poly, "#f3ead6", inner, w=4.2, seed=1010)


def chair_front():
    """Ближняя сторона рамы: задняя нога, передняя нога, нижняя планка, торцы перекладин."""
    s = []
    s.append(bar(FRB, FRONT, 24, 1002))
    s.append(bar(TOPB, REAR, 24, 1000))
    s.append(peg(FRB, 15, 1006))
    s.append(peg(TOPB, 15, 1007))
    return "".join(s)


def glass(x, y, sc, sd=0):
    """Стакан сока с трубочкой и долькой."""
    s = []
    s.append(line([(x + 10 * sc, y - 70 * sc), (x + 34 * sc, y - 128 * sc)], 7 * sc, INK, taper=.05, wmin=.95, seed=sd))
    s.append(line([(x + 10 * sc, y - 70 * sc), (x + 34 * sc, y - 128 * sc)], 4 * sc, "#ff5a7a", taper=.05, wmin=.95, seed=sd + 1))
    pts = [(x - 26 * sc, y - 86 * sc, 1), (x + 26 * sc, y - 86 * sc, 1), (x + 20 * sc, y, 1), (x - 20 * sc, y, 1)]
    inner = blob([(x - 26 * sc, y - 64 * sc), (x + 26 * sc, y - 64 * sc), (x + 22 * sc, y), (x - 22 * sc, y)], "#ffb43a")
    inner += line([(x - 14 * sc, y - 76 * sc), (x - 10 * sc, y - 14 * sc)], 4 * sc, "#ffffff", seed=sd + 2, op=.8)
    s.append(shape(pts, "#e9f3f2", inner, w=3.2 * sc, seed=sd + 3))
    s.append(shape([(x + 14 * sc, y - 86 * sc, 1), (x + 40 * sc, y - 100 * sc), (x + 46 * sc, y - 82 * sc), (x + 26 * sc, y - 74 * sc, 1)], "#9fd14a",
                   blob([(x + 22 * sc, y - 84 * sc), (x + 38 * sc, y - 92 * sc), (x + 40 * sc, y - 86 * sc)], "#d8f08a"), w=2.6 * sc, seed=sd + 4))
    return "".join(s)


def sunglasses(t):
    """Тёмные очки на «носу» мозга — в локальных координатах мозга (поверх глаз)."""
    s = []
    for k, (x, y) in enumerate((BR.EYE_L, BR.EYE_R)):
        lens = [(x - 34, y - 6, 1), (x + 32, y - 8, 1), (x + 28, y + 26), (x, y + 36), (x - 28, y + 28)]
        s.append(shape(lens, "#2a2a3a", line([(x - 20, y + 2), (x - 6, y)], 4, "#7a7a9a", seed=1980 + k), w=4.4, seed=1970 + k))
    s.append(line([(BR.EYE_L[0] + 32, BR.EYE_L[1] - 2), (BR.EYE_R[0] - 34, BR.EYE_R[1] - 2)], 5, INK, seed=1975))
    s.append(line([(BR.EYE_R[0] + 30, BR.EYE_R[1] - 4), (BR.EYE_R[0] + 90, BR.EYE_R[1] - 18)], 5, INK, seed=1976))
    return "".join(s)


def brain09(t):
    sc = 0.46
    breath = math.sin(t * 2.1)
    relax = smooth(DALEKO + 0.15, DALEKO + 0.55, t)
    x, y = 706 + 2 * breath, 1022 + 3 * breath
    rot = 26 + 1.2 * math.sin(t * 0.9) + 3 * relax
    pose = BR.Pose(x, y, sc, rot, 1 + 0.012 * breath)
    # ножки по полотну к изножью, свешиваются за перекладину; болтают в такт
    hl, hr = pose.pt(*HIP_L), pose.pt(*HIP_R)
    sw = 7 * math.sin(t * 2.6)
    fl = (FRB[0] - 44 + sw, FRB[1] + 58)
    fr = (FRB[0] - 14 - sw * .6, FRB[1] + 70 - 24 * relax)
    legs = bleg(hr, fr, sc, -1, 2010) + bleg(hl, fl, sc, -1, 2020)
    SL = pose.pt(*BR.SH_L)
    # рука со стаканом; на «далеко» — лениво поднимает стакан («за срок!»)
    up = smooth(DALEKO - 0.05, DALEKO + 0.25, t) * (1 - smooth(DALEKO + 0.75, DALEKO + 1.05, t))
    wr = (x - 132 - 8 * up + 3 * math.sin(t * 1.7), y + 2 - 70 * up)
    arm = BR.arm(SL, wr, 30, 2101, sc)
    look = (-0.9, -0.5) if t < DALEKO + 0.25 else (-0.6, -0.2)
    mouth = "o" if DALEKO - 0.02 < t < DALEKO + 0.3 else "smile"
    face = BR.face(1.0, look, mouth, t, brow=0.3 + 0.5 * relax, blink=0.0)
    body = f'<g transform="{pose.tf()}">{_ST["brain"]}{face}{sunglasses(t)}</g>'
    hand_r = BR.toon_hand(wr[0], wr[1], -100, 0.8, 2130, sc * 1.3)
    gl = glass(wr[0] - 2, wr[1] + 22, 0.85, 2140)
    return legs, body + arm + gl + hand_r


HIP_L = (brain_art.BCX - 62, brain_art.BCY + 104)
HIP_R = (brain_art.BCX + 52, brain_art.BCY + 108)
BCX, BCY = brain_art.BCX, brain_art.BCY


def frame09(t):
    legs, body = brain09(t)
    s = [_ST["sky09"], _ST["ground09"], road09(t), flag09(t), chair_back(), body, sling_lip(), legs, chair_front()]
    return "".join(s)


def cam09(t):
    u = clamp((t - 14.09) / 2.1)
    sc = 1.14 - 0.12 * ease_io(u)
    k, rot = kick(t, [DALEKO + 0.4], 0.02, 10)
    return cam(560 - 10 * u, 905 + 20 * u, sc * k, rot - 0.6 + 0.8 * u)


# ═══════════════════════════════════════════════ s12/s13: полосы недель
# Полоса из трёх недель — три строки по 7 дней (в вертикальном кадре так крупнее); конец недели — правый столбец.
CW, CH = 100.0, 76.0
RGAP = 30.0
BX0 = 272.0
BY = {1: 330.0, 2: 800.0}
WDS = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]


def cell_xy(row, i):
    """Левый верх клетки дня i (0..20) в полосе row."""
    wk, j = divmod(i, 7)
    return BX0 + j * CW, BY[row] + wk * (CH + RGAP)


def cell_c(row, i):
    x, y = cell_xy(row, i)
    return x + CW / 2, y + CH / 2


def strip(row, t, appear=1.0, sd=0):
    s = []
    y0 = BY[row]
    if appear > 0.3:
        for j, w in enumerate(WDS):
            s.append(text(BX0 + (j + .5) * CW, y0 - 16, w, 26, "#c9554c" if j >= 5 else "#8a7e72"))
    for i in range(21):
        a = clamp((appear * 24 - i) / 2.0)
        if a <= 0:
            continue
        wk, j = divmod(i, 7)
        x, y = cell_xy(row, i)
        sc = back_out(a, 2.2)
        col = "#fffaf0" if j < 5 else "#fbe1da"
        inner = blob(rect_pts(x, y + CH * .74, x + CW, y + CH), mix(col, "#d8c6a8", .45))
        inner += text(x + 16, y + 30, str(i + 1), 24, "#a89a88" if j < 5 else "#d08a80", anchor="start")
        c = shape(rect_pts(x + 3, y, x + CW - 3, y + CH, 8), col, inner, w=3.4, seed=sd + i)
        cx, cy = x + CW / 2, y + CH / 2
        s.append(f'<g transform="translate({f(cx)} {f(cy)}) scale({f(sc)}) translate({f(-cx)} {f(-cy)})">{c}</g>')
    return "".join(s)


def flag_pole(x, y, h, fw, fh, col, col_sh, wave, sd, label=None, k=1.0):
    """Флажок на древке; полотнище — влево от древка (к центру кадра)."""
    s = []
    top = (x, y - h)
    s.append(line([(x, y), top], 11 * k, INK, taper=.02, wmin=.95, seed=sd))
    s.append(line([(x, y), top], 6 * k, "#d9dde6", taper=.02, wmin=.95, seed=sd + 1))
    fl = [(top[0], top[1], 1), (top[0] - fw * .5, top[1] + wave * .5), (top[0] - fw, top[1] + wave, 1), (top[0] - fw * .86, top[1] + fh * .5 + wave),
          (top[0] - fw, top[1] + fh + wave, 1), (top[0] - fw * .5, top[1] + fh + wave * .5), (top[0], top[1] + fh, 1)]
    inner = blob([(top[0], top[1] + fh * .64), (top[0] - fw, top[1] + fh * .64 + wave), (top[0] - fw, top[1] + fh + wave), (top[0], top[1] + fh)], col_sh)
    if label:
        inner += text(top[0] - fw * 0.53, top[1] + fh * 0.64 + wave * .5, label, fh * 0.42, "#fff4e6")
    s.append(shape(fl, col, inner, w=4.4 * k, seed=sd + 2))
    s.append(shape(ellipse_pts(top[0], top[1] - 7 * k, 10 * k, 10 * k, 10), "#ffcf3a", "", w=3 * k, seed=sd + 3))
    return "".join(s)


def slam_flag(x, y, e, h, fw, fh, col, col_sh, sd, label=None, k=1.0, drop=520.0, dur=0.14):
    """Флажок падает сверху и втыкается в клетку на e = 0 (e — с удара; до удара — падение)."""
    if e < -dur:
        return ""
    if e < 0:
        v = 1 + e / dur
        dy = -drop * (1 - v * v)
        sq = 1.0
    else:
        dy = 0.0
        sq = 1 - 0.18 * math.exp(-e * 12) * math.cos(e * 30)
    wave = 8 * k * math.sin(max(e, 0) * 7 + sd) * (1 + 2 * math.exp(-max(e, 0) * 5))
    body = flag_pole(x, y, h, fw, fh, col, col_sh, wave, sd, label, k)
    return f'<g transform="translate({f(x)} {f(y + dy)}) scale(1 {f(sq)}) translate({f(-x)} {f(-y)})">{body}</g>'


def impact(x, y, e, sd, k=1.0, col="#e0352b"):
    if e < 0 or e > 0.3:
        return ""
    v = e / 0.3
    s = []
    for j in range(7):
        a = math.radians(180 + 30 * j)
        d0, d1 = (34 + 50 * v) * k, (64 + 80 * v) * k
        s.append(line([(x + d0 * math.cos(a), y + d0 * math.sin(a) * .8), (x + d1 * math.cos(a), y + d1 * math.sin(a) * .8)],
                      (9 * (1 - v) + 1.5) * k, col, taper=.5, seed=sd + j))
    return "".join(s)


def paper_stack(x, y, sd=0, n=5, w=110, sheet_h=9):
    """Стопка листов (низ в y, центр x) — в координатах человечка."""
    s = []
    for j in range(n):
        yy = y - j * sheet_h
        dx = 4 * math.sin(j * 2.1)
        pts = [(x - w / 2 + dx, yy - sheet_h, 1), (x + w / 2 + dx, yy - sheet_h - 1, 1), (x + w / 2 + dx, yy, 1), (x - w / 2 + dx, yy, 1)]
        s.append(shape(pts, "#fdfaf2" if j % 2 else "#f1ece0", "", w=2.6, seed=sd + j))
    return "".join(s)


STUD1 = dict(skin="#f0c4a0", hair="short", hair_c="#5a3a26", top="#2d55a8", low="#1f2b52", face=.25)
STUD2 = dict(skin="#f4d0b4", hair="ponytail", hair_c="#c8622a", top="#3a9a6a", low="#24484a", face=.25)
PX = 150.0
PSC = 0.42


def student(spec, x, feet, sc, t, sd, look, mouth="flat", brow=0.3, nod=0.0, flinch=0.0):
    ph = sd * 0.37
    bl = (t * 0.8 + ph) % 2.9
    blink = max(0.0, 1 - abs(bl - 1.4) / 0.07)
    pose = {"legs": {"L": (3, 0), "R": (-3, 0)}, "blink": blink, "mouth": mouth, "brow": brow, "look": look,
            "head_tilt": 3 * math.sin(t * 1.3 + ph) + 8 * nod - 6 * flinch}
    lift = 16 * flinch + 3 * math.sin(t * 2.2 + ph)
    pose["hand_target"] = {"L": (-70, -372 - lift), "R": (74, -376 - lift)}
    pose["curl"] = {"L": .35, "R": .35}
    sh = blob(ellipse_pts(x + 6, feet + 4, 100 * sc, 13 * sc, 12), "#8a7a5a", .4, blur(4))
    body = person.draw(spec, dict(pose, no_arms=True), x, feet, sc, sd=sd)
    st = f'<g transform="translate({f(x)} {f(feet)}) scale({sc:.4f})">{paper_stack(0, -366 - lift, sd + 70, 6, 150, 11)}</g>'
    arms = person.draw(spec, dict(pose, only_arms=True), x, feet, sc, sd=sd)
    return sh + body + st + arms


def cream_bg():
    s = [f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="#f3ead8"/>']
    g = rad_grad([(0, "#fbf5e8", 1), (.6, "#f3ead8", 1), (1, "#e2d4b8", 1)], 540, 800, 1100, 1300)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#{g})"/>')
    rs = np.random.RandomState(5)
    for _ in range(140):
        x, y = rs.uniform(-200, W + 200), rs.uniform(-200, H + 200)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rs.uniform(1, 2.4))}" fill="#d9c9a8"/>')
    return "".join(s)


def block_feet(row):
    return BY[row] + 3 * (CH + RGAP) - RGAP


def red_flag(t):
    x, y = cell_c(1, 20)
    return slam_flag(x + 22, y + 10, t - KONCE, 360, 200, 122, "#e0352b", "#b8281f", 3100, "СРОК", 1.0, 760, 0.16)


def frame12(t):
    s = [_ST["cream"], strip(1, t, 1.0, 3000)]
    e = t - KONCE
    flinch = math.exp(-e * 5) * math.sin(min(1, e / 0.08) * math.pi / 2) if e > 0 else 0.0
    look = (0.9, -0.3) if t > KONCE - 0.12 else (0.4 + 0.3 * math.sin(t * 1.2), 0.3)
    mouth = "o" if KONCE < t < KONCE + 0.7 else "flat"
    s.append(student(STUD1, PX, block_feet(1), PSC, t, 3200, look, mouth, 0.3 + 0.7 * (t > KONCE), flinch=flinch))
    s.append(red_flag(t))
    x, y = cell_c(1, 20)
    s.append(impact(x + 20, y + 10, e, 3150, 1.3))
    return "".join(s)


def cam12(t):
    dx, dy = shake(t, KONCE, 12, 9)
    k, rot = kick(t, [KONCE], 0.035, 10)
    u = clamp((t - 20.44) / 1.76)
    return cam(552 + 10 * math.sin(t * 0.9) + dx, 600 + 10 * u + dy, (1.1 + 0.04 * u) * k, rot + 0.5 * math.sin(t * 0.7))


G_T = [ROVN, KAZHD, NEDEL]


def frame13(t):
    s = [_ST["cream"], strip(1, t, 1.0, 3000)]
    s.append(student(STUD1, PX, block_feet(1), PSC, t, 3200, (0.6 + 0.2 * math.sin(t), 0.2), "flat", 0.3))
    s.append(red_flag(t))
    ap = ease_out(clamp((t - 21.86) / 0.36))
    s.append(strip(2, t, ap, 3300))
    e = t - 21.98
    if e > 0:
        pop = back_out(clamp(e / 0.28), 2.4)
        nod = 0.0
        for gt in G_T:
            q = t - gt
            if q > 0:
                nod += 0.6 * math.exp(-q * 6) * math.sin(min(q / 0.12, 1) * math.pi)
        look = (0.8, -0.2) if t > ROVN - 0.1 else (0.3, 0.2)
        mouth = "smile" if t > ROVN + 0.1 else "flat"
        fy = block_feet(2)
        st = student(STUD2, PX, fy, PSC, t, 3400, look, mouth, 0.6, nod=nod)
        s.append(f'<g transform="translate({f(PX)} {f(fy)}) scale({f(pop)}) translate({f(-PX)} {f(-fy)})">{st}</g>')
    for k, gt in enumerate(G_T):
        x, y = cell_c(2, 7 * k + 6)
        s.append(slam_flag(x + 26, y + 8, t - gt, 78, 76, 46, GREEN, GREEN_SH, 3500 + 10 * k, None, 0.9, 420, 0.12))
        s.append(impact(x + 22, y + 10, t - gt, 3600 + 10 * k, 0.85, GREEN))
    return "".join(s)


def cam13(t):
    u = ease_io(clamp((t - 21.85) / 1.0))
    sc = 1.1 - 0.1 * u
    cx = 552 + (548 - 552) * u
    cy = 600 + (872 - 600) * u
    k, rot = kick(t, G_T, 0.02, 12)
    return cam(cx + 8 * math.sin(t * 0.8), cy, sc * k, rot + 0.4 * math.sin(t * 0.6))


# ═══════════════════════════════════════════════
def build_static():
    if _ST:
        return
    hand_shadow_filter()
    _ST["wall"] = wallpaper()
    _ST["dec"] = dec_static()
    _ST["kurs"] = sticker_kursovaya(1500)
    _ST["daywall"] = day_wall()
    _ST["fshadow"] = FEB.shadow()
    _ST["fboard"] = FEB.board()
    _ST["fpage"] = FEB.page(name_left=False)
    _ST["sky09"] = sky09()
    _ST["ground09"] = ground09()
    _ST["brain"] = brain_art.brain(0, 0.0, stem=False)
    _ST["cream"] = cream_bg()
    lib.static_done()


SCENES = {"s02": (frame02, cam02), "s08": (frame08, cam08), "s09": (frame09, cam09), "s12": (frame12, cam12),
          "s13": (frame13, cam13), "s16": (frame16, cam16)}


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    fr, cm = SCENES[sid]
    return svg(f'<rect width="{W}" height="{H}" fill="#9fae8e"/><g transform="{cm(t)}">{fr(t)}</g>')


_ = (CHECK, PAPER, H, ease_in, f)
