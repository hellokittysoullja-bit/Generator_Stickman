"""Рилс 55 s10 (23.2–26.2) и s11 (26.2–27.6): две башни из кубиков. Левая недостроенная светится тёплым и дрожит на «Начатое» (23.73),
над ней крючок-мысль; правая достроенная холодная, к s11 уходит в серый, галочка над ней тает на «сделанное» (26.49), левая вырастает.
s10 — общий план с наездом на светящуюся башню, s11 — низкий ракурс с наклоном, панорама от галочки к растущей башне."""
import math

import lib
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
FLOOR = 1300.0
S = 150.0
LX, RX = 320.0, 790.0
HIT = 23.73       # «Начатое»
GONE = 26.49      # «сделанное»
WARM = [("#ff9a3c", "#ffc36a", "#d9701f"), ("#ffd04a", "#ffe58a", "#d9a521"), ("#ff7a5c", "#ffa38c", "#d65a3e"),
        ("#ffb347", "#ffd48a", "#d98a24"), ("#ff8f4a", "#ffbb82", "#d6682a")]
COOL = [("#4f9fc9", "#82c4e6", "#33789e"), ("#58b59a", "#8ad6bd", "#3a8c75"), ("#6a8fd6", "#98b5ee", "#4a6bb0"),
        ("#4fb0b8", "#84d2d8", "#348a92"), ("#7a8fc9", "#a4b4e4", "#566ba3")]
GRAY = ("#8a90a2", "#a9aebf", "#6a7084")


def background():
    s = []
    g = lin_grad([(0, "#1a2040", 1), (1, "#323a68", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="3000" height="{FLOOR + 900}" fill="url(#{g})"/>')
    for x in range(-900, 2000, 150):
        s.append(f'<rect x="{x}" y="-900" width="50" height="{FLOOR + 900}" fill="#232a52" opacity=".6"/>')
    tp = [(-900, FLOOR, 1), (2000, FLOOR, 1), (2000, 2800, 1), (-900, 2800, 1)]
    inner = "".join(line([(-900, FLOOR + 50 + k * 60), (2000, FLOOR + 54 + k * 60)], 2.4, "#7a5238", taper=.1, wmin=.7, seed=710 + k, op=.8) for k in range(8))
    s.append(shape(tp, "#9a6a46", inner, w=5, seed=708))
    s.append(blob(rect_pts(-900, FLOOR, 2000, FLOOR + 28), "#7e5336", .8))
    s.append(line([(-900, FLOOR), (2000, FLOOR)], 5, INK, taper=.05, wmin=.9, seed=711))
    return "".join(s)


def cube(cx, yb, rot, pal, sd, wob=(0, 0)):
    d = S * 0.28
    x0, x1 = cx - S / 2, cx + S / 2
    y1, y0 = yb, yb - S
    front = [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]
    top = [(x0, y0, 1), (x0 + d, y0 - d * .7, 1), (x1 + d, y0 - d * .7, 1), (x1, y0, 1)]
    side = [(x1, y0, 1), (x1 + d, y0 - d * .7, 1), (x1 + d, y1 - d * .7, 1), (x1, y1, 1)]
    g = shape(side, pal[2], "", w=4.2, seed=sd + 1) + shape(front, pal[0], blob([(x0, y1 - 22), (x1, y1 - 22), (x1, y1), (x0, y1)], pal[2], .35) +
              line([(x0 + 14, y0 + 16), (x0 + 40, y0 + 14)], 6, pal[1], taper=.5, wmin=.5, seed=sd + 5), w=4.6, seed=sd + 2) + shape(top, pal[1], "", w=4.2, seed=sd + 3)
    return f'<g transform="translate({f(wob[0])} {f(wob[1])}) rotate({f(rot)} {f(cx)} {f(yb)})">{g}</g>'


def left_tower(t, n, glow):
    """n кубиков (может быть дробным — последний вырастает падением сверху); дрожь на HIT."""
    e = t - HIT
    amp = (7 * math.exp(-max(e, 0) * 2.6) if e > 0 else 0) + 1.6
    out = []
    for k in range(int(math.ceil(n))):
        base = FLOOR - k * S
        yb = base
        sd = 100 + k * 7
        wobx = amp * (k + 1) / 5 * math.sin(t * 31 + k * 1.3)
        woby = 0.3 * amp * math.sin(t * 27 + k)
        rot = 0.0
        if k >= 4:                            # новый кубик падает на башню и пружинит
            u = n - k
            dropt = clamp(u)
            yb = base - 800 * (1 - ease_in(dropt, 2.2)) if dropt < 1 else base
            sq = 0
            if dropt >= 1:
                pass
        cx = LX + 5 * math.sin(k * 2.1) + wobx
        pal = tuple(mix(WARM[k % 5][i], "#ffffff", .0) for i in range(3))
        out.append(cube(cx, yb + woby, rot + 1.8 * math.sin(k * 1.7), pal, sd))
    return "".join(out)


def right_tower(t, gray):
    out = []
    for k in range(7):
        pal = tuple(mix(COOL[k % 5][i], GRAY[i], gray) for i in range(3))
        out.append(cube(RX + 4 * math.sin(k * 1.9), FLOOR - k * S, 0.0, pal, 200 + k * 7))
    return "".join(out)


def check(t, gray):
    """Галочка над правой башней: рисуется штрихом; на GONE тает (сжимается к концу штриха, капли вниз)."""
    cx, cy = RX + 40, FLOOR - 7 * S - 120
    base = [(-70, 0), (-24, 52), (84, -66)]
    L = [math.hypot(base[1][0] - base[0][0], base[1][1] - base[0][1]), math.hypot(base[2][0] - base[1][0], base[2][1] - base[1][1])]
    tot = sum(L)
    draw = ease_out(clamp((t - 25.2) / 0.5), 2) if t < GONE else 1.0
    if t < 25.2 and t >= 23.0:
        draw = 1.0   # уже нарисована к началу s10 (кроме последних кадров)
    draw = 1.0 if t < GONE else 1.0
    melt = ease_in(clamp((t - GONE) / 0.6), 1.6)
    if melt >= 1:
        return ""
    head = tot * (1 - melt)                  # тает с начала штриха
    tail0 = tot * melt
    pts = []
    def at(d):
        if d <= L[0]:
            u = d / L[0]
            return (base[0][0] + (base[1][0] - base[0][0]) * u, base[0][1] + (base[1][1] - base[0][1]) * u)
        u = (d - L[0]) / L[1]
        return (base[1][0] + (base[2][0] - base[1][0]) * u, base[1][1] + (base[2][1] - base[1][1]) * u)
    for i in range(0, 25):
        d = tail0 + (tot - tail0) * i / 24
        p = at(d)
        pts.append((cx + p[0], cy + p[1] + 40 * melt * (d / tot)))
    s = []
    if len(pts) > 2:
        s.append(line(pts, 40, INK, taper=0, wmin=1, seed=720))
        s.append(line(pts, 26, mix("#7fe08a", "#9aa0b0", gray * .6 + melt * .4), taper=0, wmin=1, seed=721))
    if 0 < melt < 1:          # капли
        for j in range(5):
            x = cx - 50 + j * 36
            y = cy + 10 + melt * (150 + j * 40) % 260
            s.append(blob(ellipse_pts(x, y, 7, 11, 8), "#7fe08a"))
    return "".join(s)


def hook(t):
    e = t - HIT
    pull = (30 * math.exp(-e * 4) * math.sin(e * 18) if e > 0 else 0) + 5 * math.sin(t * 3.1)
    x0 = LX + 30
    top = -300
    dy = 90 - (900 * ease_in(clamp((t - 26.55) / 0.5), 2) if t > 26.55 else 0)
    hp = [(x0, top), (x0, 200 + dy), (x0 + 4, 380 + dy + pull * .5), (x0 - 4, 450 + dy + pull), (x0 - 36, 480 + dy + pull), (x0 - 66, 462 + dy + pull), (x0 - 70, 430 + dy + pull), (x0 - 54, 414 + dy + pull)]
    s = [line(hp, 18, INK, taper=0, wmin=1, seed=730), line(hp, 12, "#f0b43c", taper=0, wmin=1, seed=731),
         line(hp[2:6], 3.5, "#fff0b0", taper=.1, wmin=.5, seed=732)]
    return "".join(s)


def glow(t, boost):
    pu = 0.8 + 0.2 * math.sin(t * 6.0)
    fl = 1 + 1.4 * math.exp(-max(t - HIT, 0) * 3.0) * smooth(HIT - 0.04, HIT + 0.02, t) if t > HIT - 0.04 else 1.0
    g = rad_grad([(0, "#ffb050", min(.85, .6 * pu * fl)), (.6, "#ff9a3c", .22 * pu), (1, "#ff9a3c", 0)], LX + 40, FLOOR - 330, 560 * boost, 620 * boost)
    return f'<rect x="-500" y="-400" width="1700" height="2200" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def sparks(t):
    e = t - HIT
    if not 0 < e < 0.5:
        return ""
    k = e / 0.5
    s = []
    for j in range(10):
        a = math.radians(-170 + j * 18)
        r0, r1 = 150 + 80 * k, 220 + 200 * k
        cx, cy = LX + 40, FLOOR - 4 * S - 60
        s.append(line([(cx + r0 * math.cos(a) * 1.2, cy + r0 * math.sin(a)), (cx + r1 * math.cos(a) * 1.2, cy + r1 * math.sin(a))],
                      9 * (1 - k) + 1.5, "#ffd27a", taper=.6, seed=740 + j))
    return "".join(s)


def shadows():
    return (blob(ellipse_pts(LX + 30, FLOOR + 8, 150, 24, 18), "#1a0e05", .45, blur(8)) +
            blob(ellipse_pts(RX + 30, FLOOR + 8, 150, 24, 18), "#1a0e05", .45, blur(8)))


def world(t, sid):
    if sid == "s10":
        gray, n = 0.72, 4.0
    else:
        gray = 0.72 + 0.28 * smooth(26.3, 26.9, t)
        n = 4.0
    # кубики падают по очереди: n дробное, каждый новый — 0.3 с
    if sid == "s11":
        raw = clamp((t - 26.75) / 0.9)
        n = 4 + min(3, raw * 3.0)
    s = [_ST["bg"], shadows(), glow(t, 1.0), right_tower(t, gray), check(t, gray), left_tower(t, n, 1.0), hook(t), sparks(t)]
    return "".join(s)


def camera(t, sid):
    e = t - HIT
    if sid == "s10":
        u = ease_io(clamp((t - 23.0) / 3.2))
        ccx, ccy = 600 - 220 * u, 820 + 130 * u
        sc = 0.78 + 0.5 * u + 0.07 * (1 - ease_out(clamp((t - 23.0) / 0.5)))
        rot = 2.2 * (1 - clamp((t - 23.0) / 0.7)) + 0.9 * math.sin(t * 1.2)
        if e > 0:
            k = math.exp(-e * 7)
            sc *= 1 + 0.06 * k
            ccx += 10 * k * math.sin(e * 43)
            rot += 2.5 * k * math.sin(e * 28)
        return cam(ccx, ccy, sc, rot)
    u = ease_io(clamp((t - 26.0) / 1.8))
    ccx, ccy = RX + 30 - (RX - LX + 20) * u, 420 + 120 * u
    sc = 1.45 - 0.25 * u
    rot = -5 + 4 * u
    ee = t - GONE
    if ee > 0:
        k = math.exp(-ee * 7)
        sc *= 1 + 0.05 * k
        ccy += 12 * k * math.sin(ee * 36)
    return cam(ccx, ccy, sc, rot)


def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        lib.static_done()
    lib.dyn_begin()
    return svg(f'<rect width="{W}" height="{H}" fill="#1a2040"/><g transform="{camera(t, sid)}">{world(t, sid)}</g>')
