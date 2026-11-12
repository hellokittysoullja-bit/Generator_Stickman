"""Сцена jam (s07–s11): супермаркет днём — полки с товаром, плитка пола, лампы; стол-витрина с джемом (24 или 6 банок),
табличка с числом над столом; покупатели в стиле героев. s11 — сравнение пополам, подписи «3%» и «30%» влетают на «десять»."""
import math

import numpy as np

import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, rad_grad, rect_pts, shape, smooth)
from jars import JAMS, jar
from person import draw

SHELF_TOP, SHELF_BASE = 330, 1120
TABLE_Y, TABLE_F, TABLE_X0, TABLE_X1 = 1150, 1222, 150, 930
SKIRT_B = 1560
SIGN = (380, 400, 700, 610)          # x0, y0, x1, y1
TEN = 17.32                          # «десять»
_ST = {}

CAST = {
    "anna": dict(skin="#f2c9a8", hair="bob", hair_c="#c8622a", top="#4a8fc0", low="#2f3a5a", shoes="#5a3a2a", face=.5, collar="#f0ece0"),
    "oleg": dict(skin="#e8b896", hair="bald", hair_c="#9a9aa6", top="#7a8a4a", low="#4a4450", face=-.4, glasses=True, mustache=True, bw=1.12, zip=True),
    "kira": dict(skin="#8a5a3c", hair="curly", hair_c="#2a1a14", top="#e8a63a", low="#3a3a4a", face=.3, stripes="#f6e6c0", h=.95),
    "ivan": dict(skin="#f0c4a0", hair="short", hair_c="#e0b050", top="#c0403a", low="#3a4a6a", face=0.0, cap="#2a5a8a", stubble=True),
    "lena": dict(skin="#f4d0b4", hair="ponytail", hair_c="#3a2418", top="#8a5ab0", low="#2a2a3a", face=-.6, h=.97),
    "mira": dict(skin="#d9a07a", hair="bun", hair_c="#5a3020", top="#3a9a8a", low="#e8dcc0", face=.2, h=.93),
    "boris": dict(skin="#c98e6a", hair="short", hair_c="#3a2a22", top="#5a5a6e", low="#2a3040", face=-.3, h=1.03, bw=1.08),
}


def C(name, **kw):
    d = dict(CAST[name])
    d.update(kw)
    return d


# ───────────────────────── фон
def ceiling():
    s = [f'<rect x="-700" y="-700" width="2480" height="{SHELF_TOP + 700}" fill="#e4e1da"/>']
    # лампы — ряды светящихся полос в перспективе
    for row, (y0, y1, sp) in enumerate([(30, 70, 520), (150, 178, 430), (240, 258, 360)]):
        for k in range(-3, 5):
            cx = 540 + (k - .5) * sp
            w0 = sp * .42
            pts = [(cx - w0 / 2, y0), (cx + w0 / 2, y0), (cx + w0 / 2 * .92, y1), (cx - w0 / 2 * .92, y1)]
            s.append(blob([(x, y - 10) for x, y in pts[:2]] + [(x, y + 10) for x, y in pts[2:]], "#ffffff", .7, blur(12)))
            s.append(shape([p + (1,) for p in pts], "#fbfbf6", w=2.4, seed=1000 + row * 10 + k, ink_color="#8a8780"))
    s.append(blob([(-700, SHELF_TOP - 30), (1780, SHELF_TOP - 30), (1780, SHELF_TOP), (-700, SHELF_TOP)], "#b8b4ac", .5))
    return "".join(s)


def product(x, by, kind, col, sc, sd):
    rs = np.random.RandomState(sd)
    if kind == 0:     # коробка
        w, h = rs.uniform(46, 64) * sc, rs.uniform(70, 110) * sc
        inner = blob([(x + w * .55, by - h), (x + w, by - h), (x + w, by), (x + w * .55, by)], lib.mul(col, (.78, .76, .82)), .9)
        inner += f'<rect x="{f(x)}" y="{f(by - h * .62)}" width="{f(w)}" height="{f(h * .22)}" fill="#ffffff" opacity=".8"/>'
        inner += f'<circle cx="{f(x + w * .5)}" cy="{f(by - h * .3)}" r="{f(w * .18)}" fill="{lib.mul(col, (1.3, 1.3, 1.3))}"/>'
        return shape([(x, by - h, 1), (x + w, by - h, 1), (x + w, by, 1), (x, by, 1)], col, inner, w=2.4 * sc, seed=sd), w
    if kind == 1:     # бутылка
        w, h = rs.uniform(28, 36) * sc, rs.uniform(100, 130) * sc
        cx = x + w / 2
        pts = [(x, by, 1), (x, by - h * .55), (cx - w * .18, by - h * .8), (cx - w * .18, by - h, 1), (cx + w * .18, by - h, 1),
               (cx + w * .18, by - h * .8), (x + w, by - h * .55), (x + w, by, 1)]
        inner = f'<rect x="{f(x)}" y="{f(by - h * .45)}" width="{f(w)}" height="{f(h * .25)}" fill="#f6f0e0"/>'
        inner += line([(x + w * .25, by - h * .5), (x + w * .25, by - h * .1)], 3 * sc, "#ffffff", seed=sd + 1, op=.7)
        return shape(pts, col, inner, w=2.4 * sc, seed=sd), w
    w, h = rs.uniform(36, 44) * sc, rs.uniform(48, 60) * sc   # банка-консерва
    inner = f'<rect x="{f(x)}" y="{f(by - h * .7)}" width="{f(w)}" height="{f(h * .4)}" fill="{lib.mul(col, (1.35, 1.35, 1.35))}"/>'
    inner += blob([(x + w * .6, by - h), (x + w, by - h), (x + w, by), (x + w * .6, by)], lib.mul(col, (.75, .75, .8)), .8)
    return shape([(x, by - h, 1), (x + w, by - h, 1), (x + w, by, 1), (x, by, 1)], col, inner, w=2.4 * sc, seed=sd), w


SHELF_COLS = ["#e0503a", "#3a8ad0", "#f0b83a", "#5ab05a", "#d05a9a", "#7a5ad0", "#f08a3a", "#3ab0b0", "#e8e0c0", "#c03a4a"]


def shelves():
    s = [f'<rect x="-700" y="{SHELF_TOP}" width="2480" height="{SHELF_BASE - SHELF_TOP}" fill="#d8d4cc"/>']
    rs = np.random.RandomState(12)
    ys = [470, 620, 770, 920, 1070]
    for i, y in enumerate(ys):
        x = -680
        while x < 1760:
            kind = rs.randint(0, 3)
            col = SHELF_COLS[rs.randint(0, len(SHELF_COLS))]
            g, w = product(x, y, kind, col, .9, 2000 + i * 300 + int(x + 700))
            s.append(g)
            x += w + rs.uniform(4, 10)
            if rs.rand() < .06:
                x += 60
        s.append(shape([(-700, y, 1), (1780, y, 1), (1780, y + 22, 1), (-700, y + 22, 1)], "#a8aab4",
                       "".join(f'<rect x="{xx}" y="{y + 5}" width="34" height="13" fill="#f6e27a"/>' for xx in range(-640, 1760, 210)), w=2.6, seed=2100 + i))
        s.append(blob([(-700, y + 22), (1780, y + 22), (1780, y + 40), (-700, y + 40)], "#6a6870", .25, blur(5)))
    for xx in range(-560, 1760, 560):
        s.append(shape([(xx - 12, SHELF_TOP, 1), (xx + 12, SHELF_TOP, 1), (xx + 12, SHELF_BASE, 1), (xx - 12, SHELF_BASE, 1)], "#9a9ca6", w=2.6, seed=2200 + xx))
    s.append(shape([(-700, SHELF_BASE - 40, 1), (1780, SHELF_BASE - 40, 1), (1780, SHELF_BASE, 1), (-700, SHELF_BASE, 1)], "#8a8c96", w=3, seed=2300))
    # воздушная перспектива — фон светлее и спокойнее
    s.append(f'<rect x="-700" y="{SHELF_TOP}" width="2480" height="{SHELF_BASE - SHELF_TOP}" fill="#f2efe8" opacity=".28"/>')
    return "".join(s)


def floor():
    s = [f'<rect x="-700" y="{SHELF_BASE}" width="2480" height="2000" fill="#e8e2d6"/>']
    vx, vy = 540, 700
    ys = [SHELF_BASE]
    y = SHELF_BASE
    step = 40
    while y < 2700:
        step *= 1.32
        y += step
        ys.append(y)
    for k in range(len(ys) - 1):
        if k % 2 == 0:
            continue
        s.append(f'<rect x="-700" y="{f(ys[k])}" width="2480" height="{f(ys[k + 1] - ys[k])}" fill="#ddd6c8"/>')
    for y in ys[1:]:
        s.append(f'<rect x="-700" y="{f(y - 1.5)}" width="2480" height="3" fill="#c9c1b2"/>')
    for k in range(-14, 16):
        x0 = vx + k * 150 * (SHELF_BASE - vy) / 420
        x1 = vx + (x0 - vx) * (2700 - vy) / (SHELF_BASE - vy)
        s.append(f'<path d="M{f(x0)} {SHELF_BASE} L{f(x1)} 2700" stroke="#c9c1b2" stroke-width="3" fill="none"/>')
    # отражения ламп на полу
    for k in range(-2, 4):
        s.append(blob(ellipse_pts(540 + (k - .5) * 430, 1250, 90, 26, 12), "#ffffff", .35, blur(14)))
    return "".join(s)


def table_art(n):
    """Стол с белой скатертью в красную клетку по краю, ступенчатая подставка и банки (n = 24 или 6)."""
    s = []
    s.append(blob(ellipse_pts(540, SKIRT_B + 6, 440, 34, 16), "#6a6258", .35, blur(14)))
    # подставка: ступени
    if n == 24:
        rows = [(TABLE_Y - 228, 8, 84, 30), (TABLE_Y - 114, 8, 84, 20), (TABLE_Y, 8, 84, 10)]
        steps = [(TABLE_Y - 228, 210, 870), (TABLE_Y - 114, 196, 884)]
    else:
        rows = [(TABLE_Y - 2, 6, 104, 40)]
        steps = []
    tc = "#f4f0e6"
    # скатерть: верх + свес
    top = [(TABLE_X0, TABLE_Y - 40, 1), (TABLE_X1, TABLE_Y - 40, 1), (TABLE_X1 + 26, TABLE_F, 1), (TABLE_X0 - 26, TABLE_F, 1)]
    s.append(shape(top, tc, blob([(TABLE_X0, TABLE_Y - 40), (TABLE_X1, TABLE_Y - 40), (TABLE_X1, TABLE_Y - 24), (TABLE_X0, TABLE_Y - 24)], "#d8d2c4", .7), w=4, seed=3000))
    for (yb, x0, x1) in steps:
        box = [(x0, yb - 8, 1), (x1, yb - 8, 1), (x1, yb + 114 - 8, 1), (x0, yb + 114 - 8, 1)]
        s.append(shape(box, "#b9824a", blob([(x0, yb + 8), (x1, yb + 8), (x1, yb + 106), (x0, yb + 106)], "#94612f", .9)
                       + line([(x0 + 20, yb + 40), (x1 - 40, yb + 44)], 2.4, "#7a4e24", seed=3001, op=.7), w=3.6, seed=3002 + yb))
        s.append(shape([(x0 - 6, yb - 14, 1), (x1 + 6, yb - 14, 1), (x1 + 6, yb, 1), (x0 - 6, yb, 1)], "#d4a06a", w=3, seed=3003 + yb))
    k = 0
    for (yb, cnt, sp, sd) in rows:
        x0 = 540 - sp * (cnt - 1) / 2
        for i in range(cnt):
            col = JAMS[(k * 7) % 24] if n == 24 else JAMS[[0, 2, 4, 9, 7, 13][i]]
            s.append(jar(x0 + i * sp, yb - 18, col, 1.05 if n == 24 else 1.18, sd * 10 + i))
            k += 1
    # свес скатерти: складки, кайма в клетку
    skirt = [(TABLE_X0 - 26, TABLE_F, 1), (TABLE_X1 + 26, TABLE_F, 1), (TABLE_X1 + 40, SKIRT_B, 1)]
    xs = np.linspace(TABLE_X1 + 40, TABLE_X0 - 40, 9)
    for i, x in enumerate(xs[1:-1]):
        skirt.append((x, SKIRT_B + (8 if i % 2 else -4)))
    skirt.append((TABLE_X0 - 40, SKIRT_B, 1))
    inner = []
    inner.append(f'<rect x="0" y="{SKIRT_B - 120}" width="1080" height="140" fill="url(#pGing)"/>')
    for i in range(1, 8):
        x = TABLE_X0 - 26 + (TABLE_X1 - TABLE_X0 + 52) * i / 8
        inner.append(blob([(x - 18, TABLE_F), (x + 4, TABLE_F), (x + 22, SKIRT_B + 10), (x - 30, SKIRT_B + 10)], "#cfc6b4", .55, blur(6)))
        inner.append(line([(x - 6, TABLE_F + 30), (x - 2, SKIRT_B - 140), (x + 2, SKIRT_B - 10)], 2.6, seed=3010 + i, op=.55, peak=.7))
    inner.append(blob([(TABLE_X0 - 30, TABLE_F), (TABLE_X1 + 30, TABLE_F), (TABLE_X1 + 30, TABLE_F + 24), (TABLE_X0 - 30, TABLE_F + 24)], "#bdb3a0", .6, blur(5)))
    s.append(shape(skirt, tc, "".join(inner), w=4.6, seed=3004))
    return "".join(s)


def sign_art(txt):
    x0, y0, x1, y1 = SIGN
    s = []
    for cx in (x0 + 40, x1 - 40):
        s.append(line([(cx, SHELF_TOP - 40), (cx, y0 + 6)], 3, "#5a5450", taper=.1, wmin=.9, seed=3100 + cx))
    s.append(blob([(x0 + 14, y1 - 4), (x1 + 14, y1 - 4), (x1 + 14, y1 + 14), (x0 + 14, y1 + 14)], "#5a5048", .3, blur(8)))
    s.append(shape(rect_pts(x0, y0, x1, y1, 14), "#c0502e", w=4.4, seed=3101))
    inner = blob([(x0 + 18, y1 - 60), (x1 - 18, y1 - 50), (x1 - 18, y1 - 18), (x0 + 18, y1 - 18)], "#e9dcc0", .8)
    s.append(shape(rect_pts(x0 + 16, y0 + 16, x1 - 16, y1 - 16, 8), "#fbf3df", inner, w=3, seed=3102))
    for cx in (x0 + 40, x1 - 40):
        s.append(f'<circle cx="{cx}" cy="{y0 + 8}" r="6" fill="#d8c070" stroke="{INK}" stroke-width="2.4"/>')
    fs = 168
    s.append(f'<text x="{(x0 + x1) / 2}" y="{(y0 + y1) / 2 + fs * .36:.0f}" text-anchor="middle" font-family="IDB" font-weight="900" '
             f'font-size="{fs}" fill="#b8322a" stroke="{INK}" stroke-width="3" paint-order="stroke" letter-spacing="-4">{txt}</text>')
    return "".join(s)


def gingham():
    DEFS.append('<pattern id="pGing" width="28" height="28" patternUnits="userSpaceOnUse">'
                '<rect width="28" height="28" fill="#f4f0e6"/><rect width="14" height="28" fill="#d8443a" opacity=".55"/>'
                '<rect width="28" height="14" fill="#d8443a" opacity=".55"/></pattern>')


def build_static():
    if _ST:
        return _ST
    gingham()
    _ST["bg"] = ceiling() + shelves() + floor()
    _ST["t24"] = table_art(24)
    _ST["t6"] = table_art(6)
    _ST["s24"] = sign_art("24")
    _ST["s6"] = sign_art("6")
    lib.static_done()
    return _ST


# ───────────────────────── люди
def walker(spec, t, x0, v, y, sc, sd, **pose):
    x = x0 + v * t
    stride = 300 * sc * spec.get("h", 1)
    ph = (x - x0) / stride * 2 * math.pi * (1 if v > 0 else -1) + sd
    p = dict(walk=ph)
    p.update(pose)
    return draw(spec, p, x, y, sc, sd)


def blink(t, seed, every=3.1):
    ph = (t + seed * 0.77) % every
    if ph < 0.06:
        return ph / 0.06
    if ph < 0.14:
        return 1 - (ph - 0.06) / 0.08
    return 0.0


def swing(t):
    return 0.8 * math.sin(t * 2.1)


def sign_g(st, txt, t):
    a = swing(t)
    return f'<g transform="rotate({a:.3f} 540 {SHELF_TOP - 40})">{st["s" + txt]}</g>'


def world(st, which, t, people_back="", people_front=""):
    tab = st["t24"] if which == 24 else st["t6"]
    return st["bg"] + sign_g(st, str(which), t) + people_back + tab + people_front


def frame(sid, t):
    st = build_static()
    lib.dyn_begin()
    if sid == "s07":
        u = (t - 8.56) / 2.68
        back = walker(C("mira", face=-.4), t - 8.56, 1050, -150, TABLE_Y - 4, .78, 11, basket="R", look=(-.6, .3))
        back += walker(C("oleg", face=.5), t - 8.56, -120, 120, TABLE_Y + 10, .74, 23, look=(.6, .4))
        front = walker(C("anna", face=.6), t - 8.56, -160, 400, 1930, 1.12, 5, basket="L", look=(.4, .5), blink=blink(t, 1))
        front += walker(C("boris", face=-.5), t - 8.56, 1650, -400, 2170, 1.38, 7, look=(-.7, .2), blink=blink(t, 2))
        body = world(st, 24, t, back, front)
        cm = cam(540 + 14 * u, 1010, 1.0 + 0.03 * u)
    elif sid == "s08":
        u = ease_io((t - 10.84) / 2.29)
        body = world(st, 24, t)
        cm = cam(400 + 280 * u, 1030, 2.35)
    elif sid == "s09":
        u = ease_io((t - 12.73) / 1.83)
        back = walker(C("ivan", face=.5), t - 12.73, -60, 190, TABLE_Y + 6, .76, 31, look=(.4, .5), blink=blink(t, 3))
        body = world(st, 6, t, back, "")
        cm = cam(540, 1000, 1.0 + 0.08 * u)
    elif sid == "s10":
        u = ease_io((t - 14.16) / 2.44)
        body = world(st, 24, t, crowd_back(t), crowd_front(t))
        cm = cam(540, 1020 - 20 * u, 1.0 + 0.12 * u)
    else:
        return split(st, t)
    return lib.svg(f'<g transform="{cm}">{body}</g>')


def crowd_back(t):
    s = []
    # за столом: двое рассматривают банки, наклоняются, переводят взгляд
    look = math.sin(t * 1.7)
    s.append(draw(C("lena", face=.3 + .2 * look), dict(look=(.5 * look, .8), head_tilt=6 * math.sin(t * .9), blink=blink(t, 4),
                                                         mouth="flat", brow=.4), 330, TABLE_Y + 70, .8, 41))
    s.append(draw(C("ivan", face=-.3), dict(look=(-.3 + .4 * math.sin(t * 2.3 + 1), .9), head_tilt=-5, blink=blink(t, 5), mouth="wavy", brow=.8,
                                            arms={"R": (-150 + 10 * math.sin(t * 9), 40)}), 760, TABLE_Y + 76, .78, 43))
    return "".join(s)


def crowd_front(t):
    s = []
    sc_ = 9 * math.sin(t * 15)       # чешет затылок
    s.append(draw(C("kira", face=.5), dict(arms={"R": (172, 132 + sc_), "L": (6, -4)}, look=(.6, -.2), brow=1, mouth="wavy",
                                           head_tilt=-6, blink=blink(t, 6)), 150, 1800, 1.12, 51))
    s.append(draw(C("oleg", face=.6), dict(arms={"R": (-40, -120), "L": (6, -4)}, look=(.7, .1), brow=.7, mouth="frown", basket="L",
                                           blink=blink(t, 7), head_tilt=4), 345, 1910, 1.22, 53))
    pt = 0.5 + 0.5 * math.sin(t * 2.4)
    s.append(draw(C("anna", face=-.5), dict(arms={"L": (-150 + 18 * pt, -10)}, look=(-.7, 0), brow=.5, mouth="o", blink=blink(t, 8)), 900, 1790, 1.1, 55))
    s.append(draw(C("mira", face=-.6), dict(arms={"R": (-30, -110)}, look=(-.5, .2), brow=.9, mouth="flat", head_tilt=-4 + 3 * math.sin(t * 1.3),
                                            blink=blink(t, 9)), 760, 1960, 1.2, 57))
    return "".join(s)


# ───────────────────────── s11: сравнение пополам
def label(txt, x, y, t, delay=0.0):
    u = t - TEN - delay
    if u < 0:
        return ""
    k = back_out(clamp(u / 0.26), 2.0)
    dy = 120 * (1 - ease_out(clamp(u / 0.26)))
    r = -8 * (1 - ease_out(clamp(u / 0.3)))
    fs = 176
    return (f'<g transform="translate({x} {f(y + dy)}) rotate({r:.2f}) scale({k:.4f})">'
            f'<text x="0" y="{fs * .36:.0f}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="{fs}" '
            f'fill="#ffffff" stroke="#1c1622" stroke-width="11" stroke-linejoin="round" paint-order="stroke">{txt}</text></g>')


def split(st, t):
    u = t - 16.2
    # слева: уходит с пустой корзиной от большого стола
    lp = walker(C("boris", face=-.7), u, 700, -170, 1900, 1.25, 61, basket="R", look=(-.6, .4), brow=.6, mouth="frown", blink=blink(t, 10))
    left = world(st, 24, t, "", lp)
    # справа: кладёт банку в корзину у малого стола
    a = clamp((t - 16.5) / 1.0)
    # рука: тянется к банке на столе (влево), берёт, опускает в корзину перед собой
    if a < 0.35:
        e = ease_io(a / 0.35)
        arm = (-60 - 30 * e, -10 + 6 * e)
    else:
        e = ease_io((a - 0.35) / 0.65)
        arm = (-90 + 72 * e, -4 - 40 * e)
    holding = 0.3 <= a < 0.97
    in_basket = a >= 0.97
    pose = dict(arms={"L": arm, "R": (-22, -30)}, look=(-.7, .3 + .4 * e), mouth="smile" if a > .6 else "flat", basket="R",
                blink=blink(t, 11), basket_items=JAMS[2] if in_basket else 0)
    if holding:
        pose["item"] = ("L", JAMS[2])
    rp = draw(C("lena", face=-.5), pose, 760, 1880, 1.25, 63)
    right = world(st, 6, t, "", rp)
    lc = lib.clip_rect(0, 0, 536, H)
    rc = lib.clip_rect(544, 0, 536, H)
    camL = cam(500, 960, 0.86)
    camR = cam(560, 960, 0.86)
    body = (f'<g clip-path="url(#{lc})"><g transform="translate(-270 0)"><g transform="{camL}">{left}</g></g></g>'
            f'<g clip-path="url(#{rc})"><g transform="translate(270 0)"><g transform="{camR}">{right}</g></g></g>'
            f'<rect x="533" y="0" width="14" height="{H}" fill="#ffffff"/>'
            f'<rect x="530" y="0" width="3" height="{H}" fill="{INK}"/><rect x="547" y="0" width="3" height="{H}" fill="{INK}"/>'
            + label("3%", 270, 380, t) + label("30%", 810, 380, t, 0.08))
    return lib.svg(body)
