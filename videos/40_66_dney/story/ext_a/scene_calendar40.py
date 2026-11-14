"""Сцена calendar рилса 40 «66 дней» (основа — scene_calendar рилса 26).
s02: МАРТ крупно, на «подряд» красные галочки штампуются на днях 1–9, день 10 пустой (пунктир).
s04: тот же лист; рука маркером — жирный крест на весь лист («всё»), на «сломана» лист трескается пополам и мнётся.
s07: 9 галочек, пустая клетка темнеет и растёт дырой; на «концом» галочки по одной падают с листа.
s14: АПРЕЛЬ: ряд галочек, на «пропускает» клетка 13 остаётся пустой, на «день» сразу галочка на 14-м и ряд дальше.
s16: МАРТ, АПРЕЛЬ, МАЙ рядом, галочки бегут по дням, счётчик в углу до 66 на «шесть»; на «календаре» 66-я обведена."""
import math

import numpy as np

import hand
import lib
from calbase import CHECK, PAPER, Sheet, check, dashed_ring, wallpaper
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rect_pts, shape, smooth, svg)

_ST = {}
BOX = (150, 410, 930, 1230)
MAR = Sheet(3, BOX, sd=10)
APR = Sheet(4, BOX, sd=20)
# s02: 9 штампов на «подряд»
ST02 = [1.50 + 0.095 * i for i in range(9)]
XRED = "#e0352b"


def bg():
    return f'<rect width="{W}" height="{H}" fill="#9fae8e"/>'


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


def sway(t, sh, pivot):
    """Лёгкое покачивание листа на гвозде — рисунок живёт с первого кадра."""
    a = 0.35 * math.sin(t * 2.3) + 0.15 * math.sin(t * 3.7 + 1)
    return f'<g transform="rotate({f(a)} {f(pivot[0])} {f(pivot[1])})">{sh}</g>'


def checks(sheet, stamp, sd0):
    """stamp(d) -> время удара или None."""
    r = sheet.rcheck()
    out = []
    for d in range(1, sheet.n + 1):
        ts = stamp(d)
        if ts is None:
            continue
        x, y = sheet.cell(d)
        out.append(check(x, y, r, _T[0] - ts, sd0 + d))
    return "".join(out)


_T = [0.0]


# ═════════════════════════════════════ s02
def frame02(t):
    s = [_ST["wall"], MAR.shadow()]
    pv = ((BOX[0] + BOX[2]) / 2, BOX[1] - 196 * MAR.k)
    art = MAR.board() + _ST["mar"]
    art += checks(MAR, lambda d: ST02[d - 1] if d <= 9 else None, 300)
    # день 10: пустой, пунктир проявляется и «дышит» после девятой галочки
    if t > ST02[-1] + 0.05:
        x, y = MAR.cell(10)
        u = ease_out((t - ST02[-1] - 0.05) / 0.25)
        r = MAR.rcheck() * (1.25 + 0.06 * math.sin((t - 2.3) * 9)) * (0.6 + 0.4 * u)
        art += dashed_ring(x, y, r, 77, "#8f8478", 3.4, ph=(t - 2.3) * 0.8) if u > 0.05 else ""
    art += MAR.rings()
    s.append(sway(t, art, pv))
    return "".join(s)


def cam02(t):
    u = ease_out(clamp((t - 1.3) / 0.42), 3)
    sc = 0.9 + 0.36 * u
    x10, y10 = MAR.cell(10)
    v = ease_io(clamp((t - 2.3) / 0.8))
    cx = 540 + (x10 - 540) * 0.35 * v + 6 * math.sin(t * 1.7)
    cy = 790 + 70 * u + (y10 - 860) * 0.5 * v
    sc *= 1 + 0.05 * v
    k, rot = kick(t, ST02, 0.028)
    rot += -2.2 * (1 - u)
    return cam(cx, cy, sc * k, rot)


# ═════════════════════════════════════ s04
X1A, X1B = 4.38, 4.56          # первый штрих креста: старт, конец («всё»)
X2A, X2B = 4.64, 4.82
BREAK = 5.52                   # «сломана»
P1 = ((BOX[0] - 30, BOX[1] + 170), (BOX[2] + 30, BOX[3] + 10))
P2 = ((BOX[2] + 30, BOX[1] + 170), (BOX[0] - 30, BOX[3] + 10))


def _lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def _stroke_pts(a, b, u, bow, n=8):
    pts = []
    for j in range(n + 1):
        v = u * j / n
        x, y = _lerp(a, b, v)
        nx, ny = -(b[1] - a[1]), (b[0] - a[0])
        L = math.hypot(nx, ny)
        off = bow * math.sin(math.pi * v)
        pts.append((x + nx / L * off, y + ny / L * off))
    return pts


def big_cross(t):
    out = []
    u1 = ease_in(clamp((t - X1A) / (X1B - X1A)), 1.3)
    if u1 > 0.02:
        out.append(line(_stroke_pts(*P1, u1, 18), 58, XRED, taper=.35, wmin=.55, seed=401, peak=.5))
    u2 = ease_in(clamp((t - X2A) / (X2B - X2A)), 1.3)
    if u2 > 0.02:
        out.append(line(_stroke_pts(*P2, u2, -16), 58, XRED, taper=.35, wmin=.55, seed=402, peak=.5))
    return "".join(out)


def tip04(t):
    """Кончик маркера: влёт в левый верхний угол, первый штрих, перелёт, второй штрих, уход вниз-вправо."""
    if t < X1A:
        u = ease_out(clamp((t - 4.2) / (X1A - 4.2)), 2)
        return _lerp((1250, 760), P1[0], u)
    if t < X1B:
        return _stroke_pts(*P1, ease_in(clamp((t - X1A) / (X1B - X1A)), 1.3), 18)[-1]
    if t < X2A:
        return _lerp(P1[1], P2[0], ease_io((t - X1B) / (X2A - X1B)))
    if t < X2B:
        return _stroke_pts(*P2, ease_in(clamp((t - X2A) / (X2B - X2A)), 1.3), -16)[-1]
    u = ease_in(clamp((t - X2B) / 0.32), 1.8)
    return _lerp(P2[1], (1500, 1900), u)


def crack_line():
    rs = np.random.RandomState(44)
    pts = []
    y = BOX[1] - 4
    x = 548
    while y < BOX[3] + 40:
        pts.append((x, y))
        y += rs.uniform(50, 80)
        x = 540 + rs.uniform(-22, 22)
    pts.append((540 + rs.uniform(-20, 20), BOX[3] + 60))
    return pts


CRACK = crack_line()


def frame04(t):
    s = [_ST["wall"], MAR.shadow()]
    pv = ((BOX[0] + BOX[2]) / 2, BOX[1] - 196 * MAR.k)
    top = MAR.board()
    paper = _ST["mar"] + _ST["mar9"]
    x, y = MAR.cell(10)
    paper += dashed_ring(x, y, MAR.rcheck() * 1.25, 77, "#8f8478", 3.4, ph=t * 0.8)
    paper += big_cross(t)
    e = t - BREAK
    if e < -0.06:
        s.append(sway(t, top + paper + MAR.rings(), pv))
    else:
        # трещина бежит сверху вниз (рвётся только бумага, планка цела), половинки повисают на спирали и
        # расходятся книзу, лист мнётся
        g = clamp((e + 0.06) / 0.12)
        sep = 0.0 if e < 0.04 else (1 - math.exp(-(e - 0.04) * 8) * math.cos((e - 0.04) * 15))
        cr = CRACK
        ncut = max(2, int(round(g * (len(cr) - 1))) + 1)
        partial = cr[:ncut]
        left_poly = [(-400, -600, 1), (cr[0][0], -600, 1)] + [(p[0], p[1], 1) for p in cr] + [(cr[-1][0], 2600, 1), (-400, 2600, 1)]
        right_poly = [(cr[0][0], -600, 1), (1500, -600, 1), (1500, 2600, 1), (cr[-1][0], 2600, 1)] + [(p[0], p[1], 1) for p in cr[::-1]]
        wr = wrinkles(0.5 + 0.5 * clamp(e / 0.3))
        if g < 1 or sep < 0.01:
            body = top + paper + line(partial, 6, "#3a2c22", taper=.25, wmin=.4, seed=451) + wrinkles(g * 0.5) + MAR.rings()
            s.append(sway(t, body, pv))
        else:
            cl, crc = lib.clip_of(left_poly), lib.clip_of(right_poly)
            a = 2.0 * sep
            edge = line(cr, 9, "#3a2c22", taper=.2, wmin=.6, seed=452)
            fib = fibers(cr)
            px, py = cr[0][0], BOX[1]
            body = top
            body += (f'<g transform="rotate({f(a)} {f(px - 20)} {f(py)})"><g clip-path="url(#{cl})">{paper}{wr}{fib}{edge}</g></g>')
            body += (f'<g transform="rotate({f(-a * 1.1)} {f(px + 20)} {f(py)})"><g clip-path="url(#{crc})">{paper}{wr}{fib}{edge}</g></g>')
            body += MAR.rings()
            s.append(sway(t, body, pv))
    # рука с маркером
    if 4.2 <= t <= X2B + 0.34:
        px, py = tip04(t)
        ang = -34 + 6 * math.sin(t * 6)
        s.append(f'<g transform="translate({f(px + 26)} {f(py + 34)}) scale(1.1)" opacity=".26" filter="url(#fShH)">{hand.hand(ang, 7, kind="marker")}</g>')
        s.append(hand.draw(px, py, ang, 1.1, 7, kind="marker"))
    return "".join(s)


def fibers(cr):
    """Белые волокна бумаги вдоль разрыва."""
    rs = np.random.RandomState(61)
    out = []
    for p, q in zip(cr, cr[1:]):
        for _ in range(3):
            u = rs.uniform(0, 1)
            x, y = p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u
            if BOX[1] - 10 < y < BOX[3]:
                out.append(line([(x - 2, y), (x + rs.uniform(-12, 12), y + rs.uniform(-8, 8))], 3, PAPER, taper=.3, seed=int(x * 7 + y)))
    return "".join(out)


def wrinkles(u):
    """Заломы смятого листа: серые линии с белым бликом рядом."""
    if u <= 0:
        return ""
    rs = np.random.RandomState(81)
    out = []
    for j in range(9):
        x0, y0 = rs.uniform(BOX[0] + 40, BOX[2] - 40), rs.uniform(BOX[1] + 220, BOX[3] - 40)
        ang = rs.uniform(0, math.pi)
        L = rs.uniform(90, 220) * u
        p = [(x0, y0), (x0 + math.cos(ang) * L * .5 + rs.uniform(-12, 12), y0 + math.sin(ang) * L * .5), (x0 + math.cos(ang) * L, y0 + math.sin(ang) * L)]
        out.append(line(p, 4.2, "#b9ab95", taper=.5, wmin=.2, seed=900 + j))
        out.append(line([(a + 4, b - 3) for a, b in p], 3, "#ffffff", taper=.5, wmin=.2, seed=920 + j))
    return "".join(out)


def cam04(t):
    sc = 1.12 + 0.05 * (t - 4.3)
    cx, cy = 540 + 8 * math.sin(t * 1.5), 820
    k, rot = kick(t, [X1B, X2B], 0.05, 12)
    dx, dy = shake(t, X1B, 12, 10)
    dx2, dy2 = shake(t, BREAK, 16, 8, 62)
    k2, rot2 = kick(t, [BREAK], 0.06, 9)
    return cam(cx + dx + dx2, cy + dy + dy2, sc * k * k2, rot + rot2 - 0.8)


# ═════════════════════════════════════ s07
HOLE0, FALL = 9.40, 10.08


def hole_r(t):
    r0 = MAR.rcheck() * 1.25
    if t < HOLE0:
        return 0.0
    u = (t - HOLE0)
    return r0 * (0.4 + 1.1 * ease_out(clamp(u / 0.7), 2)) + 60 * max(0, u - 0.7)


def hole(t):
    r = hole_r(t)
    if r <= 2:
        return ""
    x, y = MAR.cell(10)
    rs = np.random.RandomState(5)
    n = 34
    jit = rs.uniform(0.84, 1.1, n)
    jit2 = rs.uniform(1.06, 1.16, n)
    wob = [1 + 0.025 * math.sin(t * 7 + j * 1.3) for j in range(n)]

    def ring(kk):
        return [(x + r * kk[j] * wob[j] * math.cos(2 * math.pi * j / n), y + r * 0.92 * kk[j] * wob[j] * math.sin(2 * math.pi * j / n), 1)
                for j in range(n)]
    g = lib.rad_grad([(0, "#050307", 1), (.6, "#120a0e", 1), (.88, "#33241f", 1), (1, "#5a4636", 1)], x, y + r * .1, r * 1.05)
    # рваный край: изнанка бумаги чуть шире дыры, потом сама дыра
    out = [shape(ring(jit * jit2), "#e4d8c3", "", w=3.0, seed=34), shape(ring(jit), f"url(#{g})", "", w=4.0, seed=33)]
    return "".join(out)


def frame07(t):
    s = [_ST["wall"], MAR.shadow()]
    pv = ((BOX[0] + BOX[2]) / 2, BOX[1] - 196 * MAR.k)
    art = MAR.board() + _ST["mar"]
    x10, y10 = MAR.cell(10)
    # пустая клетка темнеет до начала дыры
    if t < HOLE0 + 0.2:
        u = clamp((t - 9.2) / 0.4)
        art += blob(ellipse_pts(x10, y10, MAR.cw * .45, MAR.rh * .42, 16), mix("#e8e0d2", "#8a7f74", u))
    art += hole(t)
    r = MAR.rcheck()
    fall = []
    for d in range(1, 10):
        x, y = MAR.cell(d)
        tf = FALL + (9 - d) * 0.045
        e = t - tf
        if e < 0:
            jig = 0.0
            if t > FALL - 0.25:
                jig = 2.5 * math.sin(t * 60 + d) * clamp((t - FALL + 0.25) / 0.25)
            art += check(x + jig, y, r, 5.0, 300 + d, pop=False)
        else:
            rs = np.random.RandomState(d)
            vx = rs.uniform(-160, 160)
            dx = vx * e
            dy = -260 * e + 0.5 * 5200 * e * e
            rot = rs.choice([-1, 1]) * (360 * e + 600 * e * e)
            fall.append(f'<g transform="translate({f(x + dx)} {f(y + dy)}) rotate({f(rot)})">{check(0, 0, r, 5.0, 300 + d, pop=False)}</g>')
    art += MAR.rings()
    s.append(sway(t, art, pv))
    s.extend(fall)
    return "".join(s)


def cam07(t):
    x10, y10 = MAR.cell(10)
    u = ease_io(clamp((t - 9.2) / 0.85))
    sc = 1.08 + 0.42 * u + 0.05 * clamp((t - 10.1) / 1.2)
    cx = 540 + (x10 + 40 - 540) * u
    cy = 800 + (y10 - 30 - 800) * u
    k, rot = kick(t, [FALL], 0.045, 8)
    dx, dy = shake(t, FALL, 7, 6)
    return cam(cx + dx, cy + dy, sc * k, rot + 1.2 * u)


# ═════════════════════════════════════ s14
SKIP, HIT14 = 27.65, 28.20
ST14 = {10: 26.12, 11: 26.60, 12: 27.12, 14: HIT14, 15: 28.40, 16: 28.56, 17: 28.70}


def frame14(t):
    s = [_ST["wall"], APR.shadow()]
    pv = ((BOX[0] + BOX[2]) / 2, BOX[1] - 196 * APR.k)
    art = APR.board() + _ST["apr"]
    art += checks(APR, lambda d: (-10.0 if d <= 9 else ST14.get(d)), 500)
    x, y = APR.cell(13)
    if t >= SKIP - 0.05:
        u = ease_out(clamp((t - SKIP + 0.05) / 0.2))
        wob = 2.5 * math.exp(-max(0, t - SKIP) * 6) * math.sin((t - SKIP) * 50)
        art += dashed_ring(x + wob, y, APR.rcheck() * (0.8 + 0.65 * u), 131, "#7d7368", 4.2, ph=t * 0.7)
    art += APR.rings()
    s.append(sway(t, art, pv))
    return "".join(s)


def cam14(t):
    u = ease_io(clamp((t - 26.0) / 2.8))
    x13, y13 = APR.cell(13)
    sc = 1.14 + 0.2 * u
    cx = 540 + (x13 + 60 - 540) * 0.2 * u + 5 * math.sin(t * 1.4)
    cy = 800 + (y13 - 800) * 0.5 * u
    k, rot = kick(t, [26.12, 26.60, 27.12, 28.40, 28.56, 28.70], 0.018)
    k2, rot2 = kick(t, [HIT14], 0.05, 12)
    dx, dy = shake(t, HIT14, 8, 10)
    return cam(cx + dx, cy + dy, sc * k * k2, rot + rot2 + 0.6 - 1.2 * u)


# ═════════════════════════════════════ s16
B16 = {3: (60, 330, 520, 810), 4: (560, 330, 1020, 810), 5: (60, 900, 520, 1380)}
SH16 = {m: Sheet(m, b, sd=40 + m) for m, b in B16.items()}
CNT = (560, 900, 1020, 1380)
F0, F1, RING = 30.14, 30.96, 31.72


def order16():
    out = []
    for m in (3, 4, 5):
        sh = SH16[m]
        for d in range(1, sh.n + 1):
            if m == 3 and d == 10:
                continue
            out.append((m, d))
            if len(out) == 66:
                return out
    return out


ORD16 = order16()
TS16 = {md: F0 + (F1 - F0) * (i / 65) ** 0.85 for i, md in enumerate(ORD16)}


def counter(t):
    x0, y0, x1, y1 = CNT
    n = sum(1 for v in TS16.values() if t >= v)
    s = []
    s.append(blob([(x0 + 26, y0 + 30, 1), (x1 + 30, y0 + 30, 1), (x1 + 34, y1 + 34, 1), (x0 + 30, y1 + 30, 1)], "#1d2412", .36, blur(14)))
    inner = blob(rect_pts(x0 - 10, y0 - 10, x1 + 10, y0 + 110), "#2b2f3a")
    inner += (f'<text x="{f((x0 + x1) / 2)}" y="{f(y0 + 78)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="56" '
              f'letter-spacing="3" fill="#fff6ea">ОТМЕТОК</text>')
    s_in = ""
    hit = t - F1
    sc = 1.0
    if n > 0:
        q = t - TS16[ORD16[n - 1]]
        sc = 1 + 0.07 * math.exp(-q * 30)
    if hit >= 0:
        sc = 1 + 0.35 * math.exp(-hit * 7) * math.cos(hit * 18)
    col = "#d8433a" if n < 66 else "#2f9a4a"
    cx, cy = (x0 + x1) / 2, (y0 + 110 + y1) / 2 + 92
    s_in += (f'<g transform="translate({f(cx)} {f(cy)}) scale({f(sc)})"><text x="0" y="0" text-anchor="middle" font-family="IDB" '
             f'font-weight="900" font-size="260" fill="{col}">{n}</text></g>')
    s.append(shape([(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)], PAPER, inner + s_in, w=4.4, seed=777))
    for xx in (x0 + 50, x1 - 50):
        s.append(shape(ellipse_pts(xx, y0 + 16, 15, 15, 12), "#e2584a", blob(ellipse_pts(xx - 5, y0 + 11, 5, 4, 8), "#f7a08f"), w=3, seed=int(xx)))
    if hit >= 0:
        # искры от «66»
        rs = np.random.RandomState(3)
        for j in range(8):
            a = 2 * math.pi * j / 8 + rs.uniform(-.2, .2)
            if hit < 0.3:
                v = hit / 0.3
                d0, d1 = 150 + 80 * v, 190 + 110 * v
                s.append(line([(cx + d0 * math.cos(a), cy - 90 + d0 * math.sin(a)), (cx + d1 * math.cos(a), cy - 90 + d1 * math.sin(a))],
                              12 * (1 - v) + 1, "#f2b33a", taper=.5, seed=700 + j))
    return "".join(s)


def ring66(t):
    e = t - (RING - 0.1)
    if e < 0:
        return ""
    sh = SH16[5]
    x, y = sh.cell(6)
    r = sh.rcheck() * 1.6
    u = ease_out(clamp(e / 0.2), 2)
    n = 20
    pts = []
    for j in range(int(n * 1.12 * u) + 2):
        a = -2.2 + 2 * math.pi * j / n
        rr = r * (1 + 0.06 * math.sin(j * 1.7))
        pts.append((x + rr * math.cos(a) * 1.08, y + rr * math.sin(a)))
    return line(pts, 13, CHECK, taper=.3, wmin=.5, seed=991)


def frame16(t):
    s = [_ST["wall"]]
    for m in (3, 4, 5):
        sh = SH16[m]
        art = _ST[f"p16_{m}"]
        art += checks(sh, lambda d, m=m: TS16.get((m, d)), 600 + m * 40)
        if m == 3:
            x, y = sh.cell(10)
            art += dashed_ring(x, y, sh.rcheck() * 1.2, 141, "#8f8478", 2.6, ph=t * .7)
        if m == 5:
            art += ring66(t)
        s.append(sway(t + m, art, ((sh.x0 + sh.x1) / 2, sh.y0)))
    s.append(counter(t))
    return "".join(s)


def cam16(t):
    u = ease_io(clamp((t - 30.1) / 0.95))
    sh = SH16[3]
    c0 = ((sh.x0 + sh.x1) / 2 + 40, (sh.y0 + sh.y1) / 2 - 20)
    c1 = (540, 1022)
    sc = 1.8 + (1.02 - 1.8) * u - 0.02 * clamp((t - 31.05) / 0.6)
    cx, cy = c0[0] + (c1[0] - c0[0]) * u, c0[1] + (c1[1] - c0[1]) * u
    # на «календаре» — лёгкий подъезд к 66-й галочке
    v = ease_io(clamp((t - RING + 0.12) / 0.5))
    x6, y6 = SH16[5].cell(6)
    sc *= 1 + 0.1 * v
    cx += (x6 - cx) * 0.25 * v
    cy += (y6 - cy) * 0.12 * v
    k, rot = kick(t, [F1], 0.04, 10)
    k2, rot2 = kick(t, [RING], 0.035, 10)
    return cam(cx, cy, sc * k * k2, rot + rot2 + 1.5 * (1 - u))


def frame(sid, t):
    if not _ST:
        DEFS.append('<filter id="fShH" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                    '<feColorMatrix type="matrix" values="0 0 0 0 .1  0 0 0 0 .12  0 0 0 0 .06  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
        _ST["wall"] = wallpaper()
        _ST["mar"] = MAR.page()
        _ST["apr"] = APR.page()
        _T[0] = 99.0
        _ST["mar9"] = checks(MAR, lambda d: 0.0 if d <= 9 else None, 300)
        for m, sh in SH16.items():
            pins = "".join(shape(ellipse_pts(xx, sh.y0 + 40 * sh.k, 14, 14, 12), "#e2584a",
                                 blob(ellipse_pts(xx - 5, sh.y0 + 40 * sh.k - 5, 5, 4, 8), "#f7a08f"), w=3, seed=int(xx) + m)
                           for xx in (sh.x0 + 34, sh.x1 - 34))
            _ST[f"p16_{m}"] = sh.shadow(24, 26) + sh.page() + pins
        lib.static_done()
    lib.dyn_begin()
    _T[0] = t
    fr, cm = {"s02": (frame02, cam02), "s04": (frame04, cam04), "s07": (frame07, cam07), "s14": (frame14, cam14),
              "s16": (frame16, cam16)}[sid]
    return svg(bg() + f'<g transform="{cm(t)}">{fr(t)}</g>')


_ = (INK, back_out, smooth, CHECK)
