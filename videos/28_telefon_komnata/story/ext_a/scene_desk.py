"""Стол Димы рилса 28, вид сверху.
s02: утро, крупно тетрадь-тест с пустыми строками; рука в горчичном рукаве с ручкой зависла над первой строкой;
     карточки английских слов над тетрадью рассыпаются в хлопья одна за другой, последняя тает на «ни слова» (3.36–3.64).
s03: вечер, лампа: телефон экраном вниз рядом с учебником, тихо (пылинки в свете, пар от чая); на «лежал» (4.96)
     камера резко наезжает на телефон; на «молчал» (6.64) над ним тонкие «zz».
s05: тот же стол: из-под телефона высовывается мультяшная рука-воришка в полосатом рукаве и утаскивает светящуюся
     лампочку с учебника на «крадёт» (9.76)."""
import math

import numpy as np

import hand
import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg, T)
from parts import sausage

_ST = {}
SKIN, SKIN_SH, SKIN_SH2, NAIL = hand.SKIN, hand.SKIN_SH, hand.SKIN_SH2, hand.NAIL
INKC = "#26356f"


# ═══════════════════════════════ общий стол
def wood(pid, base, grain, seam):
    DEFS.append(f'<pattern id="{pid}" width="420" height="140" patternUnits="userSpaceOnUse">'
                f'<rect width="420" height="140" fill="{base}"/>'
                f'<path d="M0 30 C120 22 260 40 420 28 M0 78 C140 86 280 66 420 82 M0 118 C110 110 300 126 420 114" fill="none" '
                f'stroke="{grain}" stroke-width="3"/><rect y="138" width="420" height="2" fill="{seam}"/></pattern>')
    return f'<rect x="-1200" y="-1200" width="3500" height="4400" fill="url(#{pid})"/>'


# ═══════════════════════════════ s02 — тетрадь-тест утром
PG = (150, 560, 930, 1600)
ROWS = [800 + k * 98 for k in range(8)]
TIP0 = (548, ROWS[0] - 6)
WORDS = [("apple", (230, 190), -8), ("window", (760, 150), 6), ("river", (830, 360), 9), ("tired", (250, 420), 4), ("remember", (540, 300), -3)]
DIS = [(2.30, 2.56), (2.52, 2.78), (2.76, 3.02), (3.00, 3.28), (3.36, 3.64)]
CW, CHh = 300, 150


def test_page():
    x0, y0, x1, y1 = PG
    s = [blob(rect_pts(x0 + 18, y0 + 26, x1 + 30, y1 + 40), "#3a2410", .35, blur(14))]
    inner = blob(rect_pts(x1 - 40, y0, x1, y1), "#e9e4d6", .9)
    inner += line([(x0 + 92, y0 + 40), (x0 + 92, y1 - 10)], 3, "#e07a7a", taper=.05, wmin=.9, seed=401)
    for k in range(23):
        yy = y0 + 120 + k * 40
        inner += line([(x0 + 20, yy), (x1 - 20, yy)], 1.6, "#bcd2e6", taper=.05, wmin=.9, seed=410 + k)
    s.append(shape(rect_pts(x0, y0, x1, y1, 10), "#fbf8f0", inner, w=5, seed=400))
    # спираль
    for k in range(12):
        cx = x0 + 60 + k * 62
        s.append(shape(ellipse_pts(cx, y0 + 24, 9, 9, 10), "#3a2c20", "", w=2, seed=440 + k))
        s.append(line([(cx - 8, y0 - 16), (cx - 4, y0 + 10), (cx + 2, y0 + 22)], 6, "#9aa0ab", taper=.1, wmin=.7, seed=460 + k))
    # шапка теста: пустая рамка
    s.append(shape(rect_pts(x0 + 120, y0 + 70, x1 - 60, y0 + 170, 8), "#fffdf7",
                   line([(x0 + 150, y0 + 140), (x1 - 330, y0 + 140)], 3, "#7a8494", taper=.05, wmin=.9, seed=481) +
                   "".join(shape(rect_pts(x1 - 290 + k * 74, y0 + 98, x1 - 236 + k * 74, y0 + 150, 4), "#fffdf7", "", w=2.6, seed=482 + k)
                           for k in range(3)), w=3.4, seed=480))
    # строки «слово — перевод»: кружок, короткая пустая строка, тире, длинная пустая строка
    for k, y in enumerate(ROWS):
        s.append(shape(ellipse_pts(x0 + 128, y - 12, 9, 9, 10), "#fbf8f0", "", w=2.6, seed=500 + k))
        s.append(line([(x0 + 160, y), (x0 + 360, y)], 3.4, "#4a5262", taper=.05, wmin=.9, seed=510 + k))
        s.append(line([(x0 + 380, y - 12), (x0 + 404, y - 12)], 3.4, "#4a5262", taper=.1, wmin=.8, seed=520 + k))
        s.append(line([(x0 + 420, y), (x1 - 70, y)], 3.4, "#4a5262", taper=.05, wmin=.9, seed=530 + k))
    return "".join(s)


def desk_morning():
    s = [wood("pWoodM", "#b9824f", "#a06c3d", "#7c5028")]
    # кружка чая в углу
    s.append(blob(ellipse_pts(1010, 1760, 110, 110, 20), "#3a2410", .35, blur(12)))
    s.append(shape(ellipse_pts(990, 1740, 100, 100, 22), "#e9dcc4", blob(ellipse_pts(1010, 1760, 84, 84, 18), "#cbbca2"), w=5, seed=600))
    s.append(shape(ellipse_pts(990, 1740, 74, 74, 20), "#a8642c", blob(ellipse_pts(970, 1720, 30, 22, 12), "#c98a50", .9), w=3.6, seed=601))
    s.append(test_page())
    return "".join(s)


def light_morning():
    g = lin_grad([(0, "#fff4d0", .55), (1, "#fff4d0", 0)], 0, 0, 1, 1)
    s = [f'<rect x="-1200" y="-1200" width="3500" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>']
    g2 = rad_grad([(0, "#000000", 0), (.65, "#000000", 0), (1, "#2a1606", .4)], 540, 900, 1100, 1300)
    s.append(f'<rect x="-1200" y="-1200" width="3500" height="4400" fill="url(#{g2})"/>')
    return "".join(s)


def card_art(word, seed):
    w2, h2 = CW / 2, CHh / 2
    inner = blob(rect_pts(-w2, -h2, w2, -h2 + 34), "#f6e7a8")
    inner += line([(-w2, -h2 + 34), (w2, -h2 + 34)], 3, "#e07a7a", taper=.05, wmin=.9, seed=seed + 1)
    for k in range(2):
        inner += line([(-w2 + 14, 22 + k * 30), (w2 - 14, 22 + k * 30)], 1.6, "#bcd2e6", taper=.05, wmin=.9, seed=seed + 2 + k)
    fs = 58 if len(word) <= 6 else 48
    inner += (f'<text x="0" y="{f(16 + fs * .34)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="{fs}" '
              f'fill="{INKC}">{word}</text>')
    return shape(rect_pts(-w2, -h2, w2, h2, 10), "#fffdf6", inner, w=4, seed=seed)


def jag(k, y):
    return 10 * math.sin(y * 0.11 + k * 3) + 6 * math.sin(y * 0.37 + k)


def card(k, t):
    """Карточка k в момент t: плавает; при распаде её съедает рваный фронт справа налево, хлопья улетают вверх."""
    word, (cx, cy), r0 = WORDS[k]
    a, b = DIS[k]
    bob = 10 * math.sin(t * 2.2 + k * 1.7)
    cx += 6 * math.sin(t * 1.3 + k)
    cy += bob - 24 * (t - 2.04)
    rot = r0 + 3 * math.sin(t * 1.7 + k * 2)
    w2, h2 = CW / 2 + 6, CHh / 2 + 6
    u = clamp((t - a) / (b - a))
    xf = w2 + 20 - u * (2 * w2 + 50)
    out = []
    tf = f"translate({f(cx)} {f(cy)}) rotate({f(rot)})"
    if u < 1:
        if u > 0:
            ys = np.linspace(-h2 - 10, h2 + 10, 24)
            pts = [(-w2 - 40, -h2 - 10, 1)] + [(xf + jag(k, y), y) for y in ys] + [(-w2 - 40, h2 + 10, 1)]
            cid = lib.clip_of(pts)
            cl = f' clip-path="url(#{cid})"'
        else:
            cl = ""
        out.append(f'<g transform="translate({f(cx + 30)} {f(cy + 46)}) rotate({f(rot)})"><g{cl}>'
                   f'{blob(rect_pts(-w2 + 6, -h2 + 6, w2 - 6, h2 - 6, 10), "#3a2410", .3, blur(8))}</g></g>')
        out.append(f'<g transform="{tf}"><g{cl}>{_ST["card%d" % k]}</g></g>')
    # хлопья: рождаются на фронте и уносятся вверх, уменьшаясь
    rs = np.random.RandomState(70 + k)
    n = 46
    for j in range(n):
        px, py = rs.uniform(-w2 + 8, w2 - 8), rs.uniform(-h2 + 8, h2 - 8)
        tb = a + (w2 + 20 - px) / (2 * w2 + 50) * (b - a)
        life = rs.uniform(0.35, 0.6)
        e = t - tb
        if e < 0 or e > life:
            continue
        v = e / life
        cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        wx, wy = cx + px * cr - py * sr, cy + px * sr + py * cr
        wx += rs.uniform(30, 120) * e + 20 * math.sin(e * 9 + j)
        wy += -rs.uniform(160, 320) * e
        r = rs.uniform(7, 13) * (1 - v) ** 0.9
        if r < 0.8:
            continue
        col = INKC if rs.uniform() < 0.1 else ("#f6e7a8" if py < -h2 + 34 and rs.uniform() < .6 else "#fffdf6")
        q = ellipse_pts(wx, wy, r, r * rs.uniform(.55, .9), 5, rot=rs.uniform(0, 360) + 500 * e, jitter=.25, seed=j)
        out.append(shape(q, col, "", w=max(1.2, r * .25), seed=900 + j))
    return "".join(out)


def frame02(t):
    s = [_ST["desk_m"]]
    # рука с ручкой зависла над первой строкой: кончик чуть кружит, не касаясь
    x = TIP0[0] + 7 * math.sin(t * 3.4) + 4 * math.sin(t * 7.1)
    y = TIP0[1] - 10 + 5 * math.sin(t * 4.3 + 1)
    # на «ни слова» рука чуть опускается и замирает в нерешительности
    dn = smooth(3.4, 3.9, t)
    lft = 1.07 - 0.03 * dn
    ang = -34 + 2.5 * math.sin(t * 2.1)
    s.append(f'<g transform="translate({f(x + 30 * lft)} {f(y + 40 * lft)}) scale(1.0)" opacity=".28" filter="url(#fShH)">{hand.hand(ang, 7)}</g>')
    s.append(_ST["light_m"])
    s.append(f'<g transform="translate({f(x)} {f(y)}) scale({f(1.0 * lft)})">{hand.hand(ang, 7, curl=.3)}</g>')
    for k in range(len(WORDS)):
        s.append(card(k, t))
    u = clamp((t - 2.04) / 2.45)
    cx = 550 - 10 * ease_io(u)
    cy = 800 - 30 * ease_io(u)
    sc = 1.12 + 0.12 * (0.5 * u + 0.5 * ease_io(u))
    rot = -1.5 + 2.0 * u
    # толчок камеры, когда тает последняя
    e = t - 3.36
    if e > 0:
        kk = math.exp(-e * 6)
        sc *= 1 + 0.02 * kk * math.sin(min(e * 10, math.pi))
    return "".join(s), cam(cx, cy, sc, rot)


# ═══════════════════════════════ вечерний стол (s03, s05)
PHONE = (880, 860, 7.0)        # центр, поворот
PW, PHH = 236, 476
BOOK = (430, 820, -5.0)
BW, BH = 700, 500
BULB = (500, 760)
BROT = 135.0


def textbook():
    cx, cy, r = BOOK
    w2, h2 = BW / 2, BH / 2
    P = lambda pts: T(pts, cx, cy, 1.0, r)
    s = [blob(P(rect_pts(-w2 + 20, -h2 + 30, w2 + 30, h2 + 40)), "#140a04", .4, blur(14))]
    s.append(shape(P(rect_pts(-w2 - 14, -h2 - 10, w2 + 14, h2 + 14, 12)), "#2f6db0", "", w=5, seed=300))
    for side in (-1, 1):
        x0, x1 = (-w2, -4) if side < 0 else (4, w2)
        inner = blob(P(rect_pts(-12 if side > 0 else -14, -h2, 14, h2)), "#d8d0bc", .9) if side > 0 else blob(P(rect_pts(-30, -h2, -4, h2)), "#d8d0bc", .9)
        s.append(shape(P(rect_pts(x0, -h2, x1, h2, 6)), "#faf5e8", inner, w=4, seed=310 + side))
    # левая страница: картинка (яблоко) и «текст» серыми полосками
    s.append(shape(P(rect_pts(-w2 + 40, -h2 + 40, -40, -h2 + 220, 8)), "#e8f0f6", "", w=3, seed=320))
    s.append(shape(P(ellipse_pts(-w2 + 175, -h2 + 140, 52, 48, 16)), "#d9483b", blob(P(ellipse_pts(-w2 + 158, -h2 + 124, 16, 12, 10)), "#f2a08a"),
                   w=3.6, seed=321))
    s.append(line(P([(-w2 + 175, -h2 + 96), (-w2 + 180, -h2 + 76)]), 5, "#6b4a20", seed=322))
    s.append(shape(P([(-w2 + 182, -h2 + 84), (-w2 + 214, -h2 + 70), (-w2 + 196, -h2 + 92)]), "#5f9a5a", "", w=2.6, seed=323))
    for k in range(6):
        y = -h2 + 260 + k * 34
        ln = 270 - (k % 3) * 40 - (60 if k == 5 else 0)
        s.append(blob(P(rect_pts(-w2 + 40, y, -w2 + 40 + ln, y + 12, 6)), "#a9b0bc"))
    # правая страница: полоски и маленькая картинка окна
    for k in range(9):
        y = -h2 + 50 + k * 34
        if 3 <= k <= 6:
            continue
        ln = 280 - (k % 2) * 50
        s.append(blob(P(rect_pts(40, y, 40 + ln, y + 12, 6)), "#a9b0bc"))
    for k in range(4):
        y = -h2 + 320 + k * 34
        s.append(blob(P(rect_pts(40, y, 40 + 260 - (k % 2) * 70, y + 12, 6)), "#a9b0bc"))
    s.append(shape(P(rect_pts(40, -h2 + 150, 170, -h2 + 270, 6)), "#cfe6f5",
                   line(P([(105, -h2 + 150), (105, -h2 + 270)]), 3, INK, seed=330) + line(P([(40, -h2 + 210), (170, -h2 + 210)]), 3, INK, seed=331),
                   w=3.4, seed=332))
    return "".join(s)


def phone_back(dx=0.0, dy=0.0, drot=0.0):
    cx, cy, r = PHONE
    P = lambda pts: T(pts, cx + dx, cy + dy, 1.0, r + drot)
    w2, h2 = PW / 2, PHH / 2
    s = []
    s.append(shape(P(rect_pts(-w2, -h2, w2, h2, 40)), "#353a48",
                   blob(P(rect_pts(w2 - 30, -h2, w2, h2)), "#272b36", .9) + line(P([(-w2 + 22, -h2 + 90), (-w2 + 22, h2 - 60)]), 4, "#5f6880", seed=341, op=.9),
                   w=5, seed=340))
    s.append(shape(P(rect_pts(-w2 + 18, -h2 + 18, -w2 + 112, -h2 + 128, 22)), "#2a2e3a", "", w=3.4, seed=342))
    for k, (u, v) in enumerate([(-w2 + 44, -h2 + 46), (-w2 + 86, -h2 + 46), (-w2 + 44, -h2 + 98)]):
        s.append(shape(P(ellipse_pts(u, v, 17, 17, 14)), "#14161d", blob(P(ellipse_pts(u - 4, v - 4, 6, 5, 8)), "#8fa0c8"), w=2.6, seed=343 + k))
    s.append(shape(P(ellipse_pts(-w2 + 86, -h2 + 98, 7, 7, 8)), "#f2e6c0", "", w=2, seed=347))
    return "".join(s)


def phone_shadow():
    cx, cy, r = PHONE
    return blob(T(rect_pts(-PW / 2, -PHH / 2, PW / 2, PHH / 2, 40), cx + 16, cy + 22, 1.0, r), "#140a04", .45, blur(10))


def desk_evening():
    s = [wood("pWoodE", "#8a5a34", "#734824", "#5c3818")]
    # кружка с чаем сверху слева
    s.append(blob(ellipse_pts(240, 360, 110, 110, 20), "#140a04", .4, blur(12)))
    s.append(line([(300, 300), (360, 250), (380, 300), (330, 350)], 26, INK, taper=.05, wmin=.9, seed=601))
    s.append(line([(300, 300), (360, 250), (380, 300), (330, 350)], 15, "#d9483b", taper=.05, wmin=.9, seed=602))
    s.append(shape(ellipse_pts(230, 340, 100, 100, 22), "#d9483b", blob(ellipse_pts(250, 360, 84, 84, 18), "#a8322a"), w=5, seed=603))
    s.append(shape(ellipse_pts(230, 340, 76, 76, 20), "#8a4a1c", blob(ellipse_pts(212, 322, 30, 22, 12), "#b06a30", .9), w=3.6, seed=604))
    # основание настольной лампы справа сверху
    s.append(blob(ellipse_pts(930, 230, 130, 120, 20), "#140a04", .4, blur(12)))
    s.append(shape(ellipse_pts(910, 210, 120, 112, 22), "#3d6f6a", blob(ellipse_pts(930, 230, 100, 92, 18), "#2c524e"), w=5, seed=605))
    s.append(shape(ellipse_pts(910, 210, 30, 30, 14), "#2c524e", "", w=3.4, seed=606))
    s.append(line([(910, 210), (840, -40), (760, -260)], 26, INK, taper=.05, wmin=.9, seed=607))
    s.append(line([(910, 210), (840, -40), (760, -260)], 16, "#3d6f6a", taper=.05, wmin=.9, seed=608))
    # тетрадь Димы и карандаш снизу
    s.append(blob(rect_pts(170, 1260, 790, 1760), "#140a04", .4, blur(12)))
    s.append(shape(T(rect_pts(-300, -230, 300, 230, 10), 470, 1490, 1.0, 4), "#f2c23a",
                   blob(T(rect_pts(-300, -230, -250, 230), 470, 1490, 1.0, 4), "#d9a420") +
                   blob(T(rect_pts(-140, -110, 160, -30, 8), 470, 1490, 1.0, 4), "#fffdf6"), w=5, seed=610))
    P = lambda pts: T(pts, 860, 1330, 1.0, -58)
    s.append(shape(P([(-170, -14, 1), (130, -14, 1), (170, 0), (130, 14, 1), (-170, 14, 1)]), "#f2a33a",
                   blob(P([(130, -14), (170, 0), (130, 14)]), "#e9cfa0") + blob(P([(-170, 4), (130, 4), (130, 14), (-170, 14)]), "#d4842a"), w=3.6,
                   seed=611))
    s.append(shape(P(rect_pts(-200, -14, -170, 14, 4)), "#e8a0a8", "", w=3.2, seed=612))
    s.append(textbook())
    s.append(phone_shadow())
    return "".join(s)


def light_evening():
    g = rad_grad([(0, "#ffd890", .55), (.6, "#ffb860", .16), (1, "#ffb860", 0)], 640, 600, 950, 950)
    s = [f'<rect x="-1200" y="-1200" width="3500" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>']
    g2 = rad_grad([(0, "#000000", 0), (.55, "#000000", 0), (1, "#120802", .5)], 640, 800, 1100, 1300)
    s.append(f'<rect x="-1200" y="-1200" width="3500" height="4400" fill="url(#{g2})"/>')
    return "".join(s)


def motes(t, seed=3):
    rs = np.random.RandomState(seed)
    s = []
    for j in range(16):
        x0, y0 = rs.uniform(250, 1000), rs.uniform(350, 1150)
        vx, vy = rs.uniform(-12, 12), rs.uniform(-18, -6)
        x = x0 + vx * t + 14 * math.sin(t * rs.uniform(.6, 1.2) + j)
        y = y0 + vy * t + 10 * math.sin(t * rs.uniform(.5, 1.0) + j * 2)
        r = rs.uniform(2.2, 3.6) * (0.85 + 0.15 * math.sin(t * 3 + j))
        s.append(blob(ellipse_pts(x, y, r, r, 8), "#fff0c8"))
    return "".join(s)


def steam(t, x0, y0, k0):
    s = []
    for k in range(3):
        xx = x0 - 30 + k * 30
        ph = t * 2.6 + k * 2.1
        pts = [(xx + 18 * math.sin(ph - v * 5) * (0.4 + v), y0 - 160 * v - 8 * k) for v in np.linspace(0, 1, 7)]
        s.append(line(pts, 9, "#f6efe2", taper=.8, wmin=.15, seed=k0 + k, peak=.35))
    return "".join(s)


def zz(t, x, y, k, t0):
    """Тонкая «z» тишины: выскакивает с перебором, плывёт вверх и покачивается."""
    e = t - t0
    if e < 0:
        return ""
    sc = back_out(clamp(e / 0.18)) * (1 - 0.15 * k)
    x += 18 * math.sin(e * 4 + k)
    y -= 70 * e
    r = -10 + 6 * math.sin(e * 5 + k)
    zw, zh = 62 * sc, 58 * sc
    pts = T([(-zw / 2, -zh / 2), (zw / 2, -zh / 2, 1), (-zw / 2, zh / 2, 1), (zw / 2, zh / 2)], x, y, 1.0, r)
    return line(pts, 6.5 * sc + .5, "#f6efe2", taper=.2, wmin=.6, seed=700 + k) + line(pts, 3.2 * sc + .3, INK, taper=.2, wmin=.6, seed=710 + k)


def frame03(t):
    s = [_ST["desk_e"], steam(t, 230, 300, 620), _ST["light_e"], phone_back(), motes(t)]
    for k, t0 in enumerate((6.64, 6.80)):
        cx, cy, _ = PHONE
        s.append(zz(t, cx + 40 + 70 * k, cy - 300 - 50 * k, k, t0))
    hit = 4.96
    u = clamp((t - 4.09) / 0.87)
    cx0, cy0, sc0 = 600 + 40 * u, 860 - 10 * u, 1.0 + 0.04 * u
    cx1, cy1, sc1 = PHONE[0] - 10, PHONE[1] - 40, 1.72
    e = t - hit
    if e < 0:
        cx, cy, sc, rot = cx0, cy0, sc0, -1.0 + 0.8 * u
    else:
        k = clamp(spring(e, freq=2.2, damp=9.0), 0, 1.15)
        drift = clamp(e / 2.2)
        cx = cx0 + (cx1 - cx0) * k + 14 * drift
        cy = cy0 + (cy1 - cy0) * k - 10 * drift
        sc = sc0 + (sc1 - sc0) * k + 0.08 * drift
        rot = -0.2 + 2.2 * min(k, 1) - 0.6 * drift
    return "".join(s), cam(cx, cy, sc, rot)


# ─────────────── s05: рука-воришка
SL_A, SL_B = "#25222c", "#f3efe6"
TSKIN, TSKIN_SH = "#f0c9a6", "#d6a283"


def bulb(x, y, sc=1.0, rot=0.0, glow=1.0, t=0.0):
    """Лампочка лежит на боку (цоколь вправо-вниз), светится."""
    P = lambda pts: T(pts, x, y, sc, rot)
    s = []
    gl = ellipse_pts(0, 0, 46, 46, 22)
    neck = [(26, 30), (44, 46, 1), (62, 64, 1), (46, 80, 1), (28, 62, 1), (12, 44)]
    glass = [(-46, 0), (-40, -24), (-22, -42), (0, -46), (24, -40), (42, -22), (48, 4), (40, 30), (26, 46), (12, 52), (-10, 46), (-32, 32)]
    hot = mix("#e8e2c8", "#fff2a0", glow)
    inner = blob(P(ellipse_pts(-12, -14, 26, 22, 12)), mix("#f6f3e8", "#fffbe0", glow), .95)
    fil = line(P([(-6, 8), (2, -4), (10, 8), (18, -4), (26, 8)]), 4, mix("#8a7a60", "#ff9a2a", glow), taper=.1, wmin=.8, seed=801)
    inner += fil + line(P([(-6, 8), (14, 40)]), 2.4, "#8a7a60", seed=802) + line(P([(26, 8), (24, 40)]), 2.4, "#8a7a60", seed=803)
    s.append(shape(P(glass), hot, inner, w=4.4, seed=804))
    # цоколь
    base = [(18, 46), (40, 24, 1), (70, 54, 1), (48, 76, 1)]
    bin_ = "".join(line(P([(28 + k * 9, 38 + k * 9), (44 + k * 9, 22 + k * 9 + 34)]), 2.4, "#6d737e", seed=805 + k) for k in range(3))
    s.append(shape(P(base), "#b9bec8", bin_, w=4, seed=809))
    s.append(shape(P([(66, 50, 1), (78, 62, 1), (62, 78, 1), (50, 66, 1)]), "#4a4f5a", "", w=3, seed=810))
    return "".join(s)


def bulb_glow(x, y, k, t):
    if k <= 0.01:
        return ""
    fl = 0.9 + 0.1 * math.sin(t * 9)
    g = rad_grad([(0, "#fff2a0", .7 * k * fl), (.4, "#ffd860", .3 * k * fl), (1, "#ffd860", 0)], x, y, 230, 230)
    s = [f'<rect x="{f(x - 240)}" y="{f(y - 240)}" width="480" height="480" fill="url(#{g})" style="mix-blend-mode:screen"/>']
    return "".join(s)


def rays(x, y, k, t):
    if k <= 0.02:
        return ""
    s = []
    for j in range(8):
        a = j * math.pi / 4 + 0.2
        p = 0.5 + 0.5 * math.sin(t * 6 + j)
        r0, r1 = 76, 76 + (24 + 16 * p) * k
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], 7 * k, "#ffe27a", taper=.5,
                      seed=820 + j))
    return "".join(s)


def thief_hand(open_k, wig, t):
    """Кисть сверху (тыл), смотрит вдоль +x, запястье в (0,0). open_k: 1 — пальцы раскрыты, 0 — сжаты (кулак)."""
    s = []
    # большой палец (сбоку, -y)
    tl = 46 * (0.55 + 0.45 * open_k)
    ta = -0.9 + 0.35 * (1 - open_k)
    tp = [(40, -30), (40 + math.cos(ta) * tl * .55, -30 + math.sin(ta) * tl * .55), (40 + math.cos(ta) * tl, -30 + math.sin(ta) * tl)]
    s.append(shape(sausage(tp, 30, 25), TSKIN, "", w=3.8, seed=850))
    # ладонь
    palm = [(0, -30), (34, -40), (76, -38), (96, -18), (98, 18), (78, 38), (34, 40), (0, 30)]
    s.append(shape(palm, TSKIN, blob([(40, 24), (98, 10), (78, 38), (34, 40)], TSKIN_SH, .9) +
                   line([(30, -10), (60, -14)], 2.2, TSKIN_SH, seed=851) + line([(30, 10), (60, 12)], 2.2, TSKIN_SH, seed=852), w=4.4, seed=853))
    # четыре пальца
    for k, (dy, L) in enumerate([(-27, 58), (-9, 66), (9, 62), (26, 50)]):
        sp = (k - 1.5) * 0.16 * open_k
        w = wig * math.sin(t * 16 + k * 1.3)
        Lk = L * (0.42 + 0.58 * open_k)
        a = sp + w * 0.12
        b0 = (92, dy * 0.9)
        b1 = (b0[0] + math.cos(a) * Lk * .5, b0[1] + math.sin(a) * Lk * .5 + dy * .1 * open_k)
        b2 = (b0[0] + math.cos(a * 1.4) * Lk, b0[1] + math.sin(a * 1.4) * Lk + dy * .18 * open_k)
        s.append(shape(sausage([b0, b1, b2], 21, 18), TSKIN, line([(b1[0] - 2, b1[1] - 7), (b1[0] - 2, b1[1] + 7)], 2, TSKIN_SH, seed=860 + k),
                       w=3.6, seed=870 + k))
        if open_k > 0.4:
            s.append(shape(ellipse_pts(b2[0] - 4, b2[1], 6, 5, 8, rot=math.degrees(a)), "#f7dfcd", "", w=1.6, seed=880 + k))
    # костяшки
    for k, dy in enumerate((-27, -9, 9, 26)):
        s.append(line([(84, dy * .9 - 6), (90, dy * .9), (84, dy * .9 + 6)], 2.2, TSKIN_SH, seed=890 + k))
    return "".join(s)


def sleeve_svg(pts, w=52):
    S = lib.sample(pts, False, 3.0)
    if len(S) < 4:
        return ""
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True) + 1e-9
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    L, R = S + N * w / 2, S - N * w / 2
    out = [tuple(p) for p in L] + [tuple(p) for p in R[::-1]]
    d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    inner = []
    sw = 26.0
    tot = d[-1]
    k = 0
    while True:
        a = tot - (k + 1) * sw     # полосы от манжеты назад: у манжеты всегда одна фаза
        b = tot - k * sw
        if b <= 0:
            break
        if k % 2 == 1:
            i0, i1 = np.searchsorted(d, max(a, 0)), np.searchsorted(d, b)
            i1 = min(i1, len(S) - 1)
            if i1 > i0:
                q = [tuple(p) for p in L[i0:i1 + 1]] + [tuple(p) for p in R[i0:i1 + 1][::-1]]
                inner.append(blob(q, SL_A))
        k += 1
    inner.append(blob([tuple(p) for p in (S + N * w * .1)[::2]] + [tuple(p) for p in R[::-2]], "#000000", .12))
    o = shape(out, SL_B, "".join(inner), w=4.4, seed=840)
    # манжета у запястья
    c = S[-1] - Tg[-1] * 6
    cu = T(rect_pts(-12, -w / 2 - 4, 8, w / 2 + 4, 4), c[0], c[1], 1.0, math.degrees(math.atan2(Tg[-1][1], Tg[-1][0])))
    o += shape(cu, SL_A, "", w=3.6, seed=841)
    return o


BASE = (835, 905)


def right_clip():
    """Полуплоскость левее правого края телефона (то, что уехало дальше под телефон, не торчит справа)."""
    cx, cy, r = PHONE
    a, b = T([(PW / 2 - 30, -3000), (PW / 2 - 30, 3000)], cx, cy, 1.0, r)
    return lib.clip_of([(-3000, a[1], 1), (a[0], a[1], 1), (b[0], b[1], 1), (-3000, b[1], 1)])


def wrist_path(p):
    """Точка запястья на пути (p 0 — под телефоном, 1 — справа от лампочки, ладонью к ней) и средняя линия рукава."""
    a = np.array(BASE, float)
    bx, by = BULB
    b = np.array([bx + 150, by], float)
    ctrl = np.array([800.0, by], float)
    q = (1 - p) ** 2 * a + 2 * (1 - p) * p * ctrl + p * p * b
    pts = [tuple((1 - v) ** 2 * a + 2 * (1 - v) * v * ctrl + v * v * b) for v in np.linspace(0, p, max(3, int(20 * p) + 3))]
    return q, pts


def path_ang(p):
    q1, _ = wrist_path(max(p, 0.03))
    q0, _ = wrist_path(max(p, 0.03) - 0.02)
    d = q1 - q0
    return math.degrees(math.atan2(d[1], d[0]))


def frame05(t):
    s = [_ST["desk_e"]]
    GRAB, YANK, SLAM = 9.64, 9.76, 9.96
    # прогресс выхода руки: крадётся рывками
    if t < 8.4:
        p = 0.0
    elif t < YANK:
        u = clamp((t - 8.4) / (9.48 - 8.4))
        steps = 4
        pu = u * steps
        i = math.floor(pu)
        p = (i + ease_io(pu - i)) / steps if i < steps else 1.0
        p = 0.18 * smooth(8.4, 8.62, t) + 0.82 * p * smooth(8.55, 8.7, t) if u < 0.25 else p
        p = min(1.0, max(p, 0.18 * smooth(8.4, 8.62, t)))
    else:
        p = 1.0
    # телефон подрагивает и приподнимается, пока рука снаружи
    lift = smooth(8.25, 8.45, t) * (1 - smooth(SLAM - 0.04, SLAM, t))
    jig = 2.5 * math.sin(t * 31) * (0.4 + lift)
    e = t - SLAM
    slam = 10 * math.exp(-e * 10) * math.sin(e * 45) if e > 0 else 0.0
    pdx, pdy, prot = 10 * lift + jig * .4 + slam, -6 * lift, -2.5 * lift + jig * .3
    # тёмная щель под приподнятым краем
    if lift > 0.01:
        cx, cy, r = PHONE
        gap = T(rect_pts(-PW / 2 - 18, -PHH / 2 + 30, -PW / 2 + 40, PHH / 2 - 30, 20), cx, cy, 1.0, r)
        s.append(blob(gap, "#0c0806", min(1, lift * 1.4)))
    held = t >= GRAB - 0.06
    open_k = 1.0 if t < GRAB - 0.14 else (1 - ease_in(clamp((t - (GRAB - 0.14)) / 0.14), 2))
    if t < 9.3:
        open_k = 0.55 + 0.45 * smooth(9.1, 9.3, t)
    q, pts = wrist_path(p)
    # рывок: рука с лампочкой целиком уезжает под телефон (по прямой вправо), за правым краем телефона — срезано
    yk = ease_in(clamp((t - YANK) / (SLAM - 0.03 - YANK)), 2) if t >= YANK else 0.0
    if yk > 0:
        off = np.array([360.0 * yk, 0.0])
        q = q + off
        pts = [tuple(np.array(pp) + off) for pp in pts]
    gone = t >= SLAM - 0.03
    # лампочка: лежит на учебнике; после хвата — в руке
    bglow = 1.0
    bx, by = BULB
    # линии скорости на рывке (под рукой)
    if YANK <= t < YANK + 0.3:
        a = 1 - (t - YANK) / 0.3
        for j in range(4):
            yy = by - 36 + j * 24
            x0 = bx + 40 + 260 * (t - YANK) / .3
            s.append(line([(x0 - 160 * a, yy), (x0, yy)], 6 * a + 1, "#f6efe2", taper=.5, seed=950 + j))
    if p > 0.02 and not gone:
        s.append('<g clip-path="url(#%s)">' % right_clip())
        s.append(sleeve_svg(pts + [tuple(q)]))
        ang = path_ang(p) if t < GRAB else path_ang(1.0) + 12 * smooth(YANK, SLAM, t)
        hx, hy = q
        if held:
            ag = path_ang(1.0)
            qg, _ = wrist_path(1.0)
            dv = np.array(BULB, float) - qg
            ca, sa = math.cos(math.radians(-ag)), math.sin(math.radians(-ag))
            loc = (dv[0] * ca - dv[1] * sa, dv[0] * sa + dv[1] * ca)
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            wx, wy = hx + loc[0] * ca - loc[1] * sa, hy + loc[0] * sa + loc[1] * ca
            s.append(bulb(wx, wy, 1.0, BROT + ang - ag, bglow, t))
        s.append(f'<g transform="translate({f(hx)} {f(hy)}) rotate({f(ang)})">{thief_hand(open_k, 1.0 if t < 9.3 else 0.3, t)}</g>')
        s.append('</g>')
    if not held:
        s.insert(1, bulb(bx, by, 1.0, BROT, 1.0, t))
    s.append(steam(t, 230, 300, 620))
    s.append(_ST["light_e"])
    s.append(phone_back(pdx, pdy, prot))
    # свет лампочки
    if not held:
        s.append(bulb_glow(bx, by, 1.0, t))
        s.append(rays(bx, by, 1.0 - 0.6 * smooth(9.4, 9.6, t), t))
    elif not gone:
        s.append(bulb_glow(q[0] - 150, q[1], bglow, t))
    # после кражи: свет пробивается из-под телефона и гаснет
    if t > SLAM - 0.02:
        k = math.exp(-(t - SLAM) * 2.2) * (0.7 + 0.3 * math.sin(t * 20))
        cx, cy, _ = PHONE
        s.append(bulb_glow(cx - PW / 2 + 10, cy + 40, 0.6 * k, t))
    s.append(motes(t, 5))
    u = clamp((t - 8.16) / 2.92)
    cx, cy = 650 + 20 * u, 800 - 10 * u
    sc = 1.72 + 0.14 * (0.4 * u + 0.6 * ease_io(u))
    rot = 1.2 - 1.6 * u
    for t0, amp in ((YANK, 1.0), (SLAM, 0.8)):
        ee = t - t0
        if ee > 0:
            kk = math.exp(-ee * 9) * amp
            cx += 8 * kk * math.sin(ee * 55)
            cy += 6 * kk * math.sin(ee * 47 + 1)
            sc *= 1 + 0.025 * kk
    return "".join(s), cam(cx, cy, sc, rot)


def frame(sid, t):
    if not _ST:
        DEFS.append('<filter id="fShH" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                    '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
        _ST["desk_m"] = desk_morning()
        _ST["light_m"] = light_morning()
        _ST["desk_e"] = desk_evening()
        _ST["light_e"] = light_evening()
        for k, (w, _, _) in enumerate(WORDS):
            _ST["card%d" % k] = card_art(w, 1000 + k * 20)
        lib.static_done()
    lib.dyn_begin()
    if sid == "s02":
        art, cm = frame02(t)
        bg = "#b9824f"
    elif sid == "s03":
        art, cm = frame03(t)
        bg = "#8a5a34"
    else:
        art, cm = frame05(t)
        bg = "#8a5a34"
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cm}">{art}</g>')
