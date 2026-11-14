"""Миры и предметы рилса 45 «сходил за хлебом»: улица с магазином, торговый зал, предметы покупок.
Манера та же, что у рилсов 26–29: живая тушь (lib.shape/line), плоский цвет с одной тенью."""
import math

import numpy as np

import lib
from lib import INK, band, blob, clamp, ellipse_pts, line, mix, rect_pts, shape, smooth, T

FLOOR = 1590
PINK, PINK_SH, PINK_HI = "#f4809f", "#d5587d", "#ffc3d3"
CHEESE, CHEESE_SH = "#f6c945", "#d9a528"


def txt(x, y, s, size, fill="#fff", stroke=None, sw=0, rot=0.0, anchor="middle", op=1.0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}" paint-order="stroke" stroke-linejoin="round"' if stroke else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}"{st} '
            f'opacity="{op:.3f}" transform="rotate({rot:.2f} {x:.1f} {y:.1f})" {extra}>{s}</text>')


def glow(x, y, r, col, a=.5):
    g = lib.rad_grad([(0, col, a), (1, col, 0)], x, y, r, r)
    return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


# ═════════════════════════ улица ═════════════════════════
def street(t, banner_sw=0.0, window_flamingo=0.0, flam_smile=1.0, banner=1.0):
    o = []
    g = lib.lin_grad([(0, "#9fd3ee", 1), (.7, "#d8eef2", 1), (1, "#f7ecd2", 1)])
    o.append(f'<rect x="-1500" y="-1200" width="5200" height="2800" fill="url(#{g})"/>')
    o.append(f'<circle cx="150" cy="330" r="130" fill="#fff3b8" opacity=".9"/>')
    o.append(glow(150, 330, 520, "#fff3b8", .45))
    for i, (cx, cy, k) in enumerate([(-200, 420, 1.2), (700, 250, 1.0), (1500, 480, 1.4)]):
        x = (cx + 14 * t) % 3200 - 700
        cl = [(-120, 0), (-90, -40), (-40, -60), (0, -40), (50, -70), (110, -40), (130, 0), (60, 14), (-60, 14)]
        o.append(shape(T(cl, x, cy, k), "#ffffff", "", w=3.6, seed=3500 + i, var=.2))
    # дальние дома
    rs = np.random.RandomState(5)
    x = -1500
    i = 0
    while x < 3000:
        w = rs.randint(260, 420)
        h = rs.randint(420, 760)
        col = ["#b9c8d6", "#c9bfd4", "#d6c4b0", "#bcd0c4"][i % 4]
        inner = ""
        for wy in range(FLOOR - h + 60, FLOOR - 140, 120):
            for wx in range(x + 40, x + w - 60, 90):
                inner += f'<rect x="{wx}" y="{wy}" width="46" height="70" fill="{mix(col, "#ffffff", .5)}"/>'
        o.append(shape(rect_pts(x, FLOOR - h, x + w, FLOOR + 10), col, inner, w=4, seed=3600 + i, var=.15))
        x += w + rs.randint(10, 40)
        i += 1
    # магазин
    X0, X1, TOP = 520, 1640, 600
    wall = "#8cc1b0"
    inner = blob(rect_pts(X0, FLOOR - 190, X1, FLOOR), "#c9795a", .95)
    for r in range(4):
        inner += line([(X0, FLOOR - 160 + r * 40), (X1, FLOOR - 160 + r * 40)], 2.4, "#a85d42", seed=3700 + r, op=.8)
    for c in range(0, 1120, 70):
        for r in range(4):
            xx = X0 + c + (35 if r % 2 else 0)
            inner += line([(xx, FLOOR - 190 + r * 40), (xx, FLOOR - 150 + r * 40)], 2.2, "#a85d42", seed=3720 + c + r, op=.8)
    o.append(shape(rect_pts(X0, TOP, X1, FLOOR + 6), wall, inner, w=5, seed=3701, var=.15))
    o.append(shape(rect_pts(X0 - 20, TOP - 40, X1 + 20, TOP + 20), "#6d9a8a", "", w=5, seed=3702))
    # вывеска
    o.append(shape(rect_pts(640, 830, 1480, 930, 14), "#fff4d6", "", w=5, seed=3703))
    o.append(txt(1060, 905, "МАГАЗИН", 78, "#2f4f46"))
    # тент
    aw = [(600, 950, 1), (1520, 950, 1)]
    stripes = ""
    for i in range(11):
        x0 = 600 + i * 92
        stripes += shape([(x0, 950, 1), (x0 + 92, 950, 1), (x0 + 92, 1040), (x0 + 46, 1062), (x0, 1040)], "#e5483d" if i % 2 == 0 else "#fffaf0", "",
                         w=3.6, seed=3710 + i, var=.12)
    o.append(stripes)
    # окно
    win_in = blob([(700, 1180), (1010, 1180), (700, 1300)], "#ffffff", .22)
    o.append(shape(rect_pts(660, 1130, 1080, 1520, 10), "#a9d8e6", win_in, w=6, seed=3704))
    o.append(line([(870, 1130), (870, 1520)], 5, "#6d9a8a", seed=3705))
    if window_flamingo > 0:
        k = window_flamingo
        o.append(f'<g opacity="1">{flamingo(790, 1505, .5, 0, smile=flam_smile, t=t, wob=1.0)}</g>')
        o.append(txt(950, 1500, "РАСПРОДАЖА", 32, "#d5483d", rot=0))
    o.append(shape(rect_pts(660, 1130, 1080, 1520, 10), "none", "", w=8, seed=3706, ink=True))
    o.append(shape(rect_pts(650, 1520, 1090, 1550, 8), "#6d9a8a", "", w=5, seed=3707))
    # дверь
    o.append(shape(rect_pts(1150, 1100, 1390, FLOOR, 8), "#cfe9f1", blob([(1170, 1120), (1260, 1120), (1170, 1300)], "#fff", .3), w=6, seed=3708))
    o.append(shape(rect_pts(1150, 1100, 1390, 1130), "#6d9a8a", "", w=5, seed=3709))
    o.append(shape(rect_pts(1350, 1300, 1366, 1420, 6), "#f0e6c8", "", w=3.6, seed=3730))
    o.append(txt(1270, 1215, "ОТКРЫТО", 28, "#e5483d"))
    # растяжка-акция
    sw = banner_sw
    if banner <= 0:
        sw = None
    sw0 = sw or 0.0
    bn = [(660 + 20 * sw0, 700, 1), (1480 + 20 * sw0, 700, 1), (1470 + 10 * sw0, 820), (1460 + 20 * sw0, 830, 1), (670 + 10 * sw0, 820)]
    if sw is not None:
        o.append(line([(640, 660), (660, 700)], 5, "#5a4a3a", seed=3740) + line([(1500, 660), (1480, 700)], 5, "#5a4a3a", seed=3741))
        o.append(shape(bn, "#ffd23f", blob([(660, 780), (1480, 780), (1470, 830), (670, 830)], "#e0a91d", .5), w=5.6, seed=3742))
        o.append(txt(1070 + 20 * sw0, 783, "АКЦИЯ: СЫР −50%", 66, "#d3302a", rot=.6 * sw0))
    # тротуар
    o.append(shape(rect_pts(-1500, FLOOR, 3200, 1790), "#d7d0c4", "".join(line([(x, FLOOR), (x - 40, 1790)], 3, "#b8b0a2", seed=3750 + x // 10, op=.8)
                                                                      for x in range(-1400, 3200, 260)), w=4.6, seed=3751, var=.12))
    o.append(shape(rect_pts(-1500, 1790, 3200, 1830), "#a49c90", "", w=4.6, seed=3752))
    o.append(shape(rect_pts(-1500, 1830, 3200, 2600), "#6e6e76", "".join(line([(x, 2040), (x + 120, 2040)], 12, "#e9e4d2", taper=.05, wmin=.9, seed=3760 + i)
                                                                      for i, x in enumerate(range(-1400, 3200, 360))), w=4.6, seed=3753, var=.12))
    return "".join(o)


# ═════════════════════════ торговый зал ═════════════════════════
PRODUCTS = ["#e07a5f", "#81b29a", "#f2cc8f", "#6d9dc5", "#c77dff", "#f4a261", "#e5e5e5", "#8ecae6", "#e76f51", "#b5c99a"]


def product(x, y, w, h, col, kind, seed):
    if kind == 0:   # коробка
        return shape(rect_pts(x, y - h, x + w, y, 3), col, blob(rect_pts(x + w * .15, y - h * .65, x + w * .85, y - h * .3, 3), "#fbf6ea", .95), w=3.2, seed=seed, var=.15)
    if kind == 1:   # банка
        return shape(rect_pts(x + 4, y - h, x + w - 4, y, 6), col, blob(rect_pts(x + 4, y - h * .7, x + w - 4, y - h * .35), "#fbf6ea", .9), w=3.2, seed=seed, var=.15)
    return shape([(x + w * .35, y - h), (x + w * .65, y - h), (x + w * .66, y - h * .8), (x + w * .9, y - h * .5), (x + w * .9, y, 1), (x + w * .1, y, 1),
                  (x + w * .1, y - h * .5), (x + w * .34, y - h * .8)], col, "", w=3.2, seed=seed, var=.15)


def store(t, sale_sw=0.0, cheese=True, cheese_taken=0.0):
    o = []
    o.append(f'<rect x="-1500" y="-1200" width="5200" height="{FLOOR + 1200}" fill="#e6efe4"/>')
    o.append(shape(rect_pts(-1500, 0, 3200, 220), "#f6f8f4", "", w=4, seed=4000, var=.1))
    for i, x in enumerate(range(-600, 2600, 520)):
        o.append(shape(rect_pts(x, 190, x + 340, 230, 10), "#fffbe0", "", w=4, seed=4001 + i))
        o.append(glow(x + 170, 250, 300, "#fff4c0", .35))
    rs = np.random.RandomState(11)
    # стеллаж на заднем плане
    for sx, sw_ in [(-700, 700), (320, 700), (1340, 700)]:
        o.append(shape(rect_pts(sx, 520, sx + sw_, FLOOR - 60, 6), "#d9e2ea", "", w=4.6, seed=4100 + sx // 10, var=.12))
        for r in range(4):
            yb = 640 + r * 220
            for k in range(7):
                o.append(product(sx + 24 + k * 94, yb, 76, rs.randint(100, 170), PRODUCTS[rs.randint(10)], rs.randint(3), 4200 + sx + r * 17 + k))
            o.append(shape(rect_pts(sx, yb, sx + sw_, yb + 18), "#aab6c2", "", w=3.6, seed=4110 + r + sx // 10))
    # пол
    inner = ""
    for k in range(8):
        inner += line([(-1500, FLOOR + 20 + k * 80 + k * k * 6), (3200, FLOOR + 20 + k * 80 + k * k * 6)], 2.6, "#c9bfa9", taper=.05, wmin=.9, seed=4300 + k, op=.8)
    for x in range(-1500, 3200, 180):
        inner += line([(x, FLOOR), (x * 1.3 - 400, FLOOR + 800)], 2.6, "#c9bfa9", taper=.05, wmin=.9, seed=4320 + x // 10, op=.7)
    o.append(shape(rect_pts(-1500, FLOOR - 60, 3200, 3000), "#ece4d2", inner, w=4.6, seed=4301, var=.12))
    return "".join(o)


def sale_sign(x, y, t, k=1.0, text="АКЦИЯ", sw=0.0):
    """Табличка на тросах с покачиванием."""
    rot = 4 * math.sin(t * 2.4) * (0.5 + sw)
    o = line([(x - 70 * k, y - 400), (x - 50 * k, y)], 4, "#6d6d78", seed=4400) + line([(x + 70 * k, y - 400), (x + 50 * k, y)], 4, "#6d6d78", seed=4401)
    star = []
    for i in range(16):
        r = 150 if i % 2 == 0 else 100
        a = math.radians(i * 22.5 - 90)
        star.append((r * math.cos(a), r * math.sin(a), 1))
    o += (f'<g transform="translate({x:.1f} {y + 110 * k:.1f}) rotate({rot:.2f} 0 {-110 * k:.1f}) scale({k})">'
          f'{shape(star, "#e5483d", blob(ellipse_pts(20, 30, 100, 70, 10), "#c23a30", .4), w=5.4, seed=4402)}'
          f'{txt(0, 20, text, 56, "#fff6d6")}</g>')
    return o


# ═════════════════════════ сыр ═════════════════════════
def cheese_wheel(x, y, k=1.0, rot=0.0, shine=0.0):
    def P(pts):
        return T(pts, x, y, k, rot)
    side = shape(P([(-120, -70, 1), (120, -70, 1), (120, -10), (60, 14), (-60, 14), (-120, -10)]), CHEESE_SH, "", w=4.6, seed=5000)
    top = shape(P(ellipse_pts(0, -70, 120, 46, 16)), CHEESE, blob(P(ellipse_pts(30, -60, 90, 30, 12)), "#ffdc6a", .6) +
                "".join(blob(P(ellipse_pts(hx, -70 + hy, r, r * .6, 8)), CHEESE_SH, .9) for hx, hy, r in [(-50, -4, 14), (30, 8, 18), (70, -10, 10), (-10, -14, 8)]),
                w=4.6, seed=5001)
    holes = "".join(shape(P(ellipse_pts(hx, hy, r, r * .8, 8)), "#c8921f", "", w=2.8, seed=5010 + i, var=.2)
                    for i, (hx, hy, r) in enumerate([(-70, -30, 11), (-20, -22, 8), (40, -34, 13), (84, -20, 8)]))
    sp = ""
    if shine > 0:
        sp = sparkle(x + 60 * k, y - 100 * k, 40 * shine, shine * 2)
    return side + holes + top + sp


def sparkle(x, y, r, a=0.0, col="#fff6c8"):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * .25
        ang = math.radians(i * 45 + a * 20)
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang), 1))
    return shape(pts, col, "", w=3, seed=5100)


def price_tag(x, y, k=1.0, rot=0.0, text="−50%"):
    pts = T([(-70, -36, 1), (70, -36, 1), (70, 36, 1), (-70, 36, 1)], x, y, k, rot)
    return shape(pts, "#ffec6e", "", w=4.4, seed=5200) + f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k})">{txt(0, 14, text, 42, "#d3302a")}</g>'


# ═════════════════════════ тележка ═════════════════════════
def cart_back(x, y, k=1.0, rot=0.0):
    def P(pts):
        return T(pts, x, y, k, rot, 0, 0)
    return shape(P([(-150, -190, 1), (180, -190, 1), (140, -50, 1), (-110, -50, 1)]), "#e8edf0", "", w=4.4, seed=5300, var=.12)


def cart_front(x, y, k=1.0, rot=0.0):
    def P(pts):
        return T(pts, x, y, k, rot, 0, 0)
    o = shape(P([(-150, -190, 1), (180, -190, 1), (140, -50, 1), (-110, -50, 1)]), "#cfd7dc", "", w=4.4, seed=5301, var=.12, attrs='opacity=".0"')
    o = ""
    for i in range(1, 6):
        u = i / 6
        o += line(P([(-150 + 330 * u, -190), (-110 + 250 * u, -50)]), 3, "#8b98a3", seed=5310 + i, taper=.05, wmin=.9)
    for j in (1, 2):
        v = j / 3
        o += line(P([(-150 + 40 * v, -190 + 140 * v), (180 - 40 * v, -190 + 140 * v)]), 3, "#8b98a3", seed=5320 + j, taper=.05, wmin=.9)
    o += shape(P([(-150, -190, 1), (180, -190, 1), (180, -178, 1), (-150, -178, 1)]), "#9aa6b0", "", w=4, seed=5330)
    o += shape(P([(-110, -52, 1), (140, -52, 1), (140, -40, 1), (-110, -40, 1)]), "#9aa6b0", "", w=4, seed=5331)
    o += line(P([(-150, -190), (-200, -270), (-150, -290)]), 9, "#5f6b76", seed=5332, taper=.1, wmin=.9)
    o += line(P([(-100, -40), (-80, 4)]), 6, "#5f6b76", seed=5333) + line(P([(120, -40), (100, 4)]), 6, "#5f6b76", seed=5334)
    for wx in (-76, 106):
        o += shape(P(ellipse_pts(wx, 22, 26, 26, 12)), "#3a3d46", blob(P(ellipse_pts(wx, 22, 10, 10, 8)), "#9aa6b0", 1), w=4, seed=5340 + int(wx))
    return o


# ═════════════════════════ гирлянда ═════════════════════════
BULBS = ["#ff5a5f", "#ffd23f", "#4ecdc4", "#6a8dff", "#ff9f1c", "#b565f0"]


def garland(pts, t, on=1.0, flash=0.0, w=4):
    """pts — точки провода (мир), лампочки через каждые ~70 px, мигают бегущим светом."""
    S = lib.sample(pts, False, 4.0)
    o = line([tuple(p) for p in S[::2]] + [tuple(S[-1])], w, "#2b3a2f", seed=5400, taper=.05, wmin=.9)
    L = [0.0]
    for i in range(1, len(S)):
        L.append(L[-1] + float(np.hypot(*(np.array(S[i]) - np.array(S[i - 1])))))
    n = int(L[-1] // 70)
    bulbs, gl = "", ""
    for j in range(1, n):
        d = j * 70
        i = int(np.searchsorted(L, d))
        i = min(i, len(S) - 1)
        x, y = S[i]
        c = BULBS[j % len(BULBS)]
        ph = .5 + .5 * math.sin(t * 7 + j * 1.3)
        a = clamp(on * (.45 + .55 * ph) + flash)
        r = 15
        bulbs += shape([(x - r * .6, y + 4, 1), (x + r * .6, y + 4, 1), (x + r, y + r * 2), (x, y + r * 2.6), (x - r, y + r * 2)], mix("#e8e2cf", c, a), "", w=3, seed=5410 + j, var=.15)
        gl += glow(x, y + r * 1.8, 70 + 40 * flash, c, .55 * a)
    return o + bulbs + gl


# ═════════════════════════ фламинго ═════════════════════════
def flamingo(x, y, k=1.0, rot=0.0, smile=0.0, t=0.0, wob=0.0, part="all"):
    """Надувной фламинго (в рост, стоит на тонких ногах). (x, y) — основание под телом (центр ног), мир px.
    smile 0..1: улыбка и глаз-дуга. Покачивается на wob."""
    sw = wob * 3 * math.sin(t * 3.0)

    def P(pts):
        return T(pts, x, y, k, rot + sw, 0, 0)
    o = ""
    # ноги
    for i, dx in enumerate((-18, 22)):
        o += line(P([(dx, -150), (dx + 8, -60), (dx + 4, -6)]), 9 * k + 2, "#f08aa8", seed=6000 + i, taper=.2, wmin=.7)
        o += shape(P([(dx - 6, -8), (dx + 40, -2), (dx + 30, 8), (dx - 20, 8)]), "#f08aa8", "", w=3.2, seed=6010 + i)
    # хвост
    o += shape(P([(-70, -250, 1), (-170, -270), (-200, -210), (-130, -190)]), PINK_SH, "", w=4.4, seed=6020)
    # тело
    body = P(ellipse_pts(0, -230, 100, 78, 16, rot=-8))
    bin_ = blob(P(ellipse_pts(30, -200, 80, 46, 12)), PINK_SH, .65) + blob(P(ellipse_pts(-30, -265, 50, 22, 10, rot=-20)), PINK_HI, .8)
    bin_ += line(P([(-80, -225), (-40, -240), (10, -240)]), 3, PINK_SH, seed=6030, op=.7)
    # шея S-образная и голова
    neck_pts = [(40, -270), (70, -350), (50, -430), (40, -520), (80, -590)]
    neck = band([tuple(p) for p in P(neck_pts)], 56 * k, 36 * k, step=5, cap=True)
    o += shape(neck, PINK, blob(P([(55, -300), (95, -360), (66, -440), (60, -300)]), PINK_SH, .55), w=4.8, seed=6040)
    o += shape(body, PINK, bin_, w=5.2, seed=6041)
    o += shape(P([(-20, -240), (60, -236), (80, -190), (10, -170), (-40, -196)]), mix(PINK, PINK_SH, .45), blob(P([(-10, -230), (40, -226)]), PINK_HI, .4), w=4, seed=6042)
    hx, hy = 80, -590
    head = P(ellipse_pts(hx, hy, 50, 44, 12))
    beak = P([(hx + 30, hy - 18, 1), (hx + 110, hy + 6), (hx + 100, hy + 34), (hx + 40, hy + 30, 1)])
    o += shape(beak, "#ffd9a8", blob(P([(hx + 72, hy + 4), (hx + 112, hy + 6), (hx + 100, hy + 34), (hx + 66, hy + 30)]), "#2b2b33", .95), w=4.4, seed=6050)
    o += shape(head, PINK, blob(P(ellipse_pts(hx - 10, hy - 18, 28, 14, 8)), PINK_HI, .7), w=4.8, seed=6051)
    # глаз
    ex, ey = hx + 10, hy - 6
    if smile > .5:
        o += line(P([(ex - 16, ey + 6), (ex, ey - 12), (ex + 16, ey + 6)]), 6, seed=6060, peak=.5)
        o += blob(P(ellipse_pts(ex + 18, ey + 20, 14, 8, 8)), "#ff7a9a", .8)
    else:
        o += shape(P(ellipse_pts(ex, ey, 17, 19, 10)), "#fff", blob(P(ellipse_pts(ex + 4, ey + 2, 8, 9, 8)), INK, 1), w=3.6, seed=6061)
    # улыбка на клюве
    sm = smile
    o += line(P([(hx + 34, hy + 24), (hx + 60, hy + 26 + 4 * sm), (hx + 98, hy + 26 - 12 * sm)]), 4, seed=6070, peak=.5)
    # клапан
    o += shape(P(ellipse_pts(30, -190, 10, 6, 8)), "#fff", "", w=3, seed=6080)
    return o


def flamingo_ring(x, y, k=1.0, t=0.0, part="back", smile=0.0):
    """Надувной круг-фламинго на полу, вид 3/4 сверху: тор-кольцо (x, y — центр кольца), шея с головой слева."""
    def P(pts):
        return T(pts, x, y, k)
    if part == "back":
        o = shape(P(ellipse_pts(0, 0, 330, 120, 20)), PINK, blob(P(ellipse_pts(30, 20, 290, 70, 16)), PINK_SH, .55), w=5.4, seed=6100)
        o += shape(P(ellipse_pts(0, -6, 210, 66, 20)), "#efe3cc", blob(P(ellipse_pts(0, 6, 190, 44, 14)), "#d9c9a8", .6), w=4.6, seed=6101)
        # шея и голова справа сзади
        neck = band([tuple(q) for q in P([(250, -60), (330, -170), (300, -290), (340, -380)])], 70 * k, 44 * k, step=5, cap=True)
        o += shape(neck, PINK, blob(P([(280, -100), (340, -180), (310, -280), (290, -100)]), PINK_SH, .55), w=5, seed=6102)
        hx, hy = 350, -400
        beak = P([(hx - 20, hy - 10, 1), (hx - 120, hy + 14), (hx - 106, hy + 42), (hx - 30, hy + 34, 1)])
        o += shape(beak, "#ffd9a8", blob(P([(hx - 82, hy + 14), (hx - 122, hy + 16), (hx - 106, hy + 42), (hx - 74, hy + 36)]), "#2b2b33", .95), w=4.6, seed=6103)
        o += shape(P(ellipse_pts(hx, hy, 58, 52, 12)), PINK, blob(P(ellipse_pts(hx + 10, hy - 22, 32, 14, 8)), PINK_HI, .7), w=5, seed=6104)
        ex, ey = hx - 14, hy - 8
        o += shape(P(ellipse_pts(ex, ey, 18, 21, 10)), "#fff", blob(P(ellipse_pts(ex - 6, ey + 2, 8, 10, 8)), INK, 1), w=3.6, seed=6105)
        o += line(P([(hx - 36, hy + 26), (hx - 64, hy + 30 + 4 * smile), (hx - 102, hy + 28 - 10 * smile)]), 4, seed=6106, peak=.5)
        return o
    # передняя половина кольца (поверх кота)
    front = [(-330, 0, 1)] + [(330 * math.cos(a), 120 * math.sin(a)) for a in np.linspace(math.pi, 0, 14)[::-1]]
    arc = [(-330 * math.cos(a), 120 * math.sin(a)) for a in np.linspace(0, math.pi, 14)]
    inner_arc = [(210 * math.cos(a), 66 * math.sin(a) - 6) for a in np.linspace(0, math.pi, 12)]
    pts = [(330, 0, 1)] + [(330 * math.cos(a), 120 * math.sin(a)) for a in np.linspace(0, math.pi, 14)][1:-1] + [(-330, 0, 1)]
    pts += [(210 * math.cos(a), 66 * math.sin(a) - 6) for a in np.linspace(math.pi, 0, 12)]
    o = shape(P(pts), PINK, blob(P([(330 * math.cos(a) * .9, 120 * math.sin(a) * .98 + 6) for a in np.linspace(0.2, 2.9, 10)]), PINK_SH, .5), w=5.4, seed=6110)
    o += line(P([(-250, 70), (-160, 100), (-40, 112)]), 5, PINK_HI, seed=6111, op=.8, taper=.3)
    return o


# ═════════════════════════ кормушка ═════════════════════════
def feeder(x, y, k=1.0, rot=0.0):
    def P(pts):
        return T(pts, x, y, k, rot)
    o = shape(P(ellipse_pts(0, -26, 120, 34, 14)), "#c9ced6", "", w=4.4, seed=6200)
    o += shape(P([(-100, -26, 1), (100, -26, 1), (84, 0), (-84, 0)]), "#9ea6b3", "", w=4.4, seed=6201)
    o += shape(P([(-70, -30, 1), (70, -30, 1), (76, -170), (-76, -170)]), "#bfe3f2", blob(P(rect_pts(-62, -110, 62, -34)), "#a8683a", .9) +
               "".join(blob(P(ellipse_pts(-40 + i * 26, -64 - 12 * (i % 3), 9, 7, 6)), "#c98456", 1) for i in range(5)) +
               blob(P([(30, -170), (76, -170), (70, -34), (24, -34)]), "#8fc9e0", .5), w=4.6, seed=6202)
    o += shape(P(ellipse_pts(0, -172, 82, 16, 12)), "#7f8794", "", w=4.2, seed=6203)
    o += shape(P(ellipse_pts(0, -186, 30, 14, 8)), "#9ea6b3", "", w=3.4, seed=6204)
    pw = [(0, -92), (-18, -76), (-10, -66), (10, -66), (18, -76)]
    o += shape(P(pw), "#f4809f", "", w=3, seed=6205)
    for i, (dx, dy) in enumerate([(-26, -106), (-8, -118), (14, -118), (32, -106)]):
        o += shape(P(ellipse_pts(dx, dy, 6, 8, 6)), "#f4809f", "", w=2.6, seed=6206 + i)
    return o


# ═════════════════════════ пузыри мысли ═════════════════════════
def bubble(x, y, w, h, tail_to, k=1.0, content="", a=1.0, wob=0.0):
    """Облако мысли с хвостом из кружков к tail_to. Размер масштабируется k от центра, a — прозрачность."""
    if k <= 0.01:
        return ""
    cx, cy = x, y
    pts = []
    n = 14
    for i in range(n):
        ang = 2 * math.pi * i / n
        r = 1 + .09 * math.sin(ang * 3 + 1 + wob)
        pts.append((cx + w / 2 * r * math.cos(ang) * k, cy + h / 2 * r * math.sin(ang) * k))
    o = ""
    tx, ty = tail_to
    for i, (u, rr) in enumerate([(.28, 22), (.55, 15), (.8, 9)]):
        px, py = cx + (tx - cx) * u, cy + (ty - cy) * u
        o += shape(ellipse_pts(px, py, rr * k, rr * k, 8), "#fffdf5", "", w=3.4, seed=6300 + i)
    o += shape(pts, "#fffdf5", blob(ellipse_pts(cx + 20, cy + 20, w * .38 * k, h * .34 * k, 10), "#efe6d2", .6), w=4.6, seed=6310)
    if content:
        o += f'<g transform="translate({cx:.1f} {cy:.1f}) scale({k:.3f}) translate({-cx:.1f} {-cy:.1f})" opacity="{a:.3f}">{content}</g>'
    return o


def loaf(x, y, k=1.0, rot=0.0, cross=0.0):
    def P(pts):
        return T(pts, x, y, k, rot)
    body = P([(-100, 0, 1), (-120, -50), (-80, -96), (0, -110), (80, -96), (120, -50), (100, 0, 1)])
    inner = blob(P([(20, -108), (80, -96), (120, -50), (100, 0), (60, 0)]), "#b9772e", .6)
    o = shape(body, "#e0a14d", inner + "".join(line(P([(-60 + 44 * i, -88), (-36 + 44 * i, -50)]), 6, "#b9772e", seed=6400 + i, taper=.3) for i in range(3)),
              w=4.6, seed=6410)
    if cross > 0:
        o += line(P([(-130, -120), (130, 20)]), 14 * cross, "#e5483d", seed=6420, taper=.05, wmin=.9)
        o += line(P([(130, -120), (-130, 20)]), 14 * cross, "#e5483d", seed=6421, taper=.05, wmin=.9)
    return o
