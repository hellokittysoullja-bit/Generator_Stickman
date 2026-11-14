"""Рилс 55, группа C: кафе 1920-х (сепия). s07 — листание календаря назад и фасад кафе, колокольчик; s08 — психолог в шляпке и очках
пишет в блокнот, поднимает взгляд на «Зейгарник» (18.37), подчёркивает строку на «заметила» (19.06); s09 — официант принимает заказы,
оплаченные исчезают, над неоплаченными облако с блюдами пульсирует на «неоплаченные» (22.06). Ни одной буквы: блокнот и чеки — штрихи.
frame(sid, t) -> SVG 1080x1920. Герои — person.py рилса 51 (контур тушью с нажимом, cel-тень), шляпка-клош добавлена в face()."""
import math

import numpy as np

import lib
import person
from lib import DEFS, INK, blob, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg

W, H = 1080, 1920
WALL, WALL_SH, WOOD, WOOD_L, CREAM, CREAM_SH = "#cfae80", "#bb9366", "#7a5232", "#9a6c42", "#f2e6c8", "#d9c79c"
RED, GOLD, GREEN = "#a9503a", "#e8b95a", "#6e8a62"


def wt(word, after=0.0):
    import scene_c55
    return scene_c55.wt(word, after)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if u <= 0 or u >= 1 else math.sin(math.pi * u) ** 2


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def cloud_shape(circles, fill, ow=5.0):
    """Облако из кругов: сначала чёрные круги чуть больше, поверх заливка — чистый общий контур без внутренних линий."""
    o = [f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r + ow)}" fill="{INK}"/>' for x, y, r in circles]
    o += [f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fill}"/>' for x, y, r in circles]
    return "".join(o)


# ════════════════════════ интерьер ════════════════════════
def interior(t, fl=1214):
    o = [f'<rect x="-900" y="-600" width="2900" height="1830" fill="{WALL}"/>']
    for x in range(-900, 2000, 90):                      # полосатые обои
        o.append(f'<rect x="{x}" y="-600" width="30" height="1400" fill="{WALL_SH}"/>')
    o.append(f'<rect x="-900" y="800" width="2900" height="{fl - 800}" fill="#8a5c38"/>')   # панели
    for x in range(-900, 2000, 150):
        o.append(f'<rect x="{x + 10}" y="850" width="130" height="{fl - 884}" fill="#9a6c42" stroke="{INK}" stroke-width="4"/>')
    o.append(shape([(-900, 790, 1), (2000, 790, 1), (2000, 850, 1), (-900, 850, 1)], "#b68350", "", w=4.4, seed=11))
    # окна
    for k, x0 in enumerate((120, 700)):
        gl = lin_grad([(0, "#fbeab8", 1), (1, "#e9cf92", 1)], 0, 0, 0, 1)
        inner = f'<rect x="{x0}" y="170" width="300" height="560" fill="url(#{gl})"/>'
        inner += blob(rect_pts(x0, 440, x0 + 300, 470), "#d9bd80")
        inner += blob(rect_pts(x0 + 140, 170, x0 + 160, 730), "#f2e6c8")
        o.append(shape(rect_pts(x0 - 14, 156, x0 + 314, 744, 8), "#f2e6c8", inner, w=5, seed=20 + k))
        for sx in (-1, 1):                               # шторы
            xx = x0 - 14 if sx < 0 else x0 + 314
            o.append(shape([(xx, 150), (xx + sx * 90, 150), (xx + sx * 100, 620), (xx, 640)], "#a9503a",
                           blob([(xx + sx * 45, 150), (xx + sx * 90, 150), (xx + sx * 100, 620), (xx + sx * 50, 630)], "#8a3e2e", .8), w=4.4, seed=30 + k + sx))
    # картины
    for k, (x0, y0, w, h) in enumerate(((470, 270, 130, 170),)):
        o.append(shape(rect_pts(x0, y0, x0 + w, y0 + h, 4), "#7a5232", blob(rect_pts(x0 + 14, y0 + 14, x0 + w - 14, y0 + h - 14), "#e6d2a0") +
                       blob([(x0 + 14, y0 + h - 14), (x0 + 50, y0 + 70), (x0 + 80, y0 + 110), (x0 + w - 14, y0 + 60), (x0 + w - 14, y0 + h - 14)], "#9aa078"),
                       w=4.6, seed=40))
    # подвесные лампы
    for k, x in enumerate((300, 780)):
        sw = 4 * math.sin(t * 1.1 + k * 2)
        o.append(line([(x, -600), (x + sw * .3, 430)], 5, INK, taper=.02, wmin=.95, seed=50 + k))
        gx, gy = x + sw * .3, 470
        g = rad_grad([(0, "#fff0b0", .55), (1, "#fff0b0", 0)], gx, gy, 260, 260)
        o.append(f'<rect x="{gx - 270}" y="{gy - 270}" width="540" height="540" fill="url(#{g})" style="mix-blend-mode:screen"/>')
        o.append(shape([(gx - 18, 410, 1), (gx + 18, 410, 1), (gx + 70, 480, 1), (gx - 70, 480, 1)], "#6e8a62",
                       blob([(gx + 10, 410), (gx + 18, 410), (gx + 70, 480), (gx + 30, 480)], "#516a4a", .9), w=4.2, seed=52 + k))
        o.append(shape(ellipse_pts(gx, 492, 28, 28, 14), "#fff4c0", "", w=3.6, seed=54 + k))
    # пол: шахматная плитка в перспективе
    vx, vy = 540.0, 560.0
    d = fl - 1214
    rows = [1220 + d, 1262 + d, 1314 + d, 1376 + d, 1450 + d, 1540 + d, 1650 + d, 1790 + d, 1960 + d, 2400 + d]
    for r in range(len(rows) - 1):
        ya, yb = rows[r], rows[r + 1]
        for c in range(-14, 16):
            def xp(c_, y):
                return vx + c_ * 90 * (y - d - vy) / (1220 - vy)
            pts = [(xp(c, ya), ya), (xp(c + 1, ya), ya), (xp(c + 1, yb), yb), (xp(c, yb), yb)]
            o.append(f'<path d="M{" L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)}Z" fill="{"#e3cfa4" if (r + c) % 2 == 0 else "#8e6a46"}"/>')
    o.append(f'<rect x="-900" y="{fl}" width="2900" height="10" fill="{INK}"/>')
    return "".join(o)


def table(x, yt, sc, t=0.0, skirt_col=CREAM, rx=None):
    """Круглый стол со скатертью до пола. Возвращает (столешница — под героем, юбка — поверх героя)."""
    rx = rx or 215 * sc
    ry = 36 * sc
    fl = yt + 330 * sc
    top = shape(ellipse_pts(x, yt, rx, ry, 28), skirt_col, "", w=4.4, seed=int(x) % 97 + 100)
    hem = [(x - rx - 8, fl)]
    n = 9
    for k in range(n + 1):
        xx = x - rx - 8 + (2 * rx + 16) * k / n
        hem.append((xx, fl + 10 + 12 * math.sin(k * 1.9)))
    pts = [(x - rx, yt - 2, 1)] + [(x - rx - 8, fl)] + hem[1:] + [(x + rx, yt - 2, 1)]
    inner = ""
    for k in range(6):
        xx = x - rx + (2 * rx) * (k + .5) / 6
        inner += line([(xx, yt + 8), (xx + (xx - x) * .05, fl)], 3, mix(skirt_col, "#7a5232", .35), taper=.1, wmin=.85, seed=int(x) % 53 + 120 + k, op=.9)
    inner += blob([(x + rx * .3, yt), (x + rx, yt), (x + rx + 8, fl + 6), (x + rx * .4, fl)], mix(skirt_col, "#7a5232", .25), .7)
    sk = shape(pts, skirt_col, inner, w=4.4, seed=int(x) % 89 + 140)
    return top, sk


def cup(x, y, k=1.0, steam_t=None):
    o = [blob(ellipse_pts(x, y + 2, 40 * k, 9 * k, 12), "#a88f60", .6)]
    o.append(shape(ellipse_pts(x, y, 38 * k, 9 * k, 12), "#fbf4e0", "", w=3, seed=int(x) % 31 + 200))
    body = [(x - 24 * k, y - 36 * k, 1), (x + 24 * k, y - 36 * k, 1), (x + 18 * k, y - 4 * k), (x - 18 * k, y - 4 * k)]
    o.append(shape(body, "#fbf4e0", blob([(x + 6 * k, y - 36 * k), (x + 24 * k, y - 36 * k), (x + 18 * k, y - 4 * k), (x + 4 * k, y - 4 * k)], "#dccfa8", .9), w=3.6, seed=int(x) % 31 + 210))
    o.append(line([(x + 22 * k, y - 28 * k), (x + 40 * k, y - 22 * k), (x + 22 * k, y - 10 * k)], 4 * k, INK, taper=.1, wmin=.9, seed=int(x) % 31 + 220))
    o.append(blob(ellipse_pts(x, y - 36 * k, 24 * k, 6 * k, 10), "#6b3f26"))
    if steam_t is not None:
        for j, dx in enumerate((-8, 8)):
            ph = steam_t * 1.4 + j * 1.9
            o.append(line([(x + dx * k + 6 * math.sin(ph + q * .9), y - 50 * k - q * 16 * k) for q in range(5)], 4, "#f4efe2", taper=.8, wmin=.1, seed=230 + j, peak=.4))
    return "".join(o)


def chair_back(x, yt, sc, side=1):
    """Спинка венского стула за героем: тёмная дуга."""
    cx, cy = x - side * 40 * sc, yt - 190 * sc
    pts = [(cx + side * 10 * sc + 95 * sc * math.cos(a), cy + 120 * sc * math.sin(a)) for a in np.linspace(math.pi * .55, math.pi * 1.55, 14)]
    return line(pts, 11 * sc + 4, INK, taper=.05, wmin=.95, seed=int(x) % 37 + 300) + line(pts, 6 * sc + 2, WOOD_L, taper=.05, wmin=.95, seed=int(x) % 37 + 310)


# ════════════════════════ герои ════════════════════════
SK = "#e8bd98"


def woman_spec(fc=.55):
    return dict(skin="#eac3a0", hair="bob", hair_c="#4a3426", top="#7a4a58", low="#4d3b45", shoes="#3a2a2a", face=fc, glasses=True,
                cloche="#8c5a46", ribbon="#5a3a2a", collar="#f2e6c8", sleeve="#7a4a58", bw=.92, brow_c="#3a2a22")


def waiter_spec(fc=.5):
    return dict(skin="#e3b894", hair="short", hair_c="#2a2020", top="#f3ead4", low="#3a3040", shoes="#2a2020", face=fc, mustache=True, collar="#2a2020",
                sleeve="#f3ead4", brow_c="#2a2020")


def hand_xy(spec, pose, sc, x, y, side="R"):
    sh_w = 74 * spec.get("bw", 1.0)
    p0 = (sh_w - 10, -520 + 18) if side == "R" else (-sh_w + 10, -520 + 18)
    a1, a2 = pose["arms"][side]
    sign = 1 if side == "R" else -1
    _, h = person.limb(p0, a1 + sign * 6, 130, a2, 120)
    return x + h[0] * sc * spec.get("h", 1.0), y + h[1] * sc * spec.get("h", 1.0)


def seated(spec, pose, x, yt, sc, sd, flip=False):
    return person.draw(spec, pose, x, yt + 312 * sc, sc, sd, flip)


def pencil(x, y, ang=-40, s=1.0):
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    p0 = (x, y)
    p1 = (x + dx * 90 * s, y + dy * 90 * s)
    return (line([p0, p1], 11 * s + 3, INK, taper=.02, wmin=.97, seed=401) + line([p0, p1], 6.5 * s, "#e8b95a", taper=.02, wmin=.97, seed=402) +
            line([(x - dx * 8, y - dy * 8), (x + dx * 16 * s, y + dy * 16 * s)], 6 * s, "#3a3030", taper=.5, wmin=.5, seed=403))


def notebook(x, y, k=1.0, lines_u=1.0, under_u=0.0):
    """Раскрытый блокнот плашмя (вид сверху-спереди): две страницы со строками-штрихами; под одной строкой — подчёркивание."""
    w, h = 300 * k, 120 * k
    quad = [(x - w / 2 + 14 * k, y - h / 2, 1), (x + w / 2 - 6 * k, y - h / 2, 1), (x + w / 2 + 14 * k, y + h / 2, 1), (x - w / 2, y + h / 2, 1)]
    o = [blob([(q[0] + 8, q[1] + 10) for q in quad], "#7a5a30", .35)]
    inner = line([(x + 4 * k, y - h / 2), (x + 4 * k + 6 * k, y + h / 2)], 4, "#b8a070", taper=.05, wmin=.9, seed=410)
    for i in range(5):
        yy = y - h / 2 + (14 + i * 20) * k
        u = clamp(lines_u * 5 - i)
        if u <= 0:
            continue
        for side in (0, 1):
            xa = x - w / 2 + (30 if side == 0 else 164) * k + (yy - y) * .12
            ln = (110 - 22 * ((i + side) % 3)) * k * u
            inner += line([(xa, yy), (xa + ln, yy - 1)], 4, "#4a5a7a", taper=.05, wmin=.95, seed=420 + i * 2 + side)
    if under_u > 0:
        yy = y - h / 2 + (14 + 2 * 20) * k + 12 * k
        xa = x - w / 2 + 164 * k + (yy - y) * .12
        pts = [(xa + 130 * k * v, yy + 3 * math.sin(v * 5)) for v in np.linspace(0, under_u, 8)]
        if len(pts) > 1:
            inner += line(pts, 7 * k, "#b8402e", taper=.3, wmin=.6, seed=440)
    o.append(shape(quad, "#f6ecd0", inner, w=3.8, seed=411))
    return "".join(o)


def ticket(x, y, s=1.0, k=1.0, bob_t=0.0):
    """Заказ-значок: бумажный чек с зигзагом снизу и двумя штрихами строк, подпрыгивает."""
    if k <= 0.01:
        return ""
    yy = y + 6 * math.sin(bob_t * 3.2)
    w, h = 54 * s, 76 * s
    zz = []
    for i in range(7):
        zz.append((x - w + 2 * w * i / 6, yy + h + (8 * s if i % 2 else 0)))
    pts = [(x - w, yy - h, 1), (x + w, yy - h, 1)] + zz[::-1]
    inner = ""
    for i, L in enumerate((.8, .6, .75)):
        inner += line([(x - w * .7, yy - h * .5 + i * 26 * s), (x - w * .7 + 2 * w * .8 * L, yy - h * .5 + i * 26 * s)], 5 * s, "#6a6a7a", taper=.05, wmin=.95, seed=450 + i)
    inner += blob([(x + w * .3, yy - h), (x + w, yy - h), (x + w, yy + h), (x + w * .5, yy + h)], "#e2d3ae", .8)
    return f'<g transform="translate({f(x)} {f(yy)}) scale({k:.4f}) translate({-f(x) if False else -x:.2f} {-yy:.2f})">' + shape(pts, "#f8f1da", inner, w=4, seed=455) + "</g>"


def poof(x, y, u, s=1.0):
    """Облачко-«пуф» исчезновения: круги растут и расходятся (u 0..1), заливка без прозрачности."""
    if u <= 0 or u >= 1:
        return ""
    k = math.sin(math.pi * min(1, u * 1.15)) ** .6
    circles = []
    for i in range(8):
        a = i * math.pi / 4 + .3
        r = (46 + 14 * (i % 3)) * s * k
        circles.append((x + math.cos(a) * 60 * s * u * 1.4, y + math.sin(a) * 50 * s * u * 1.2, r))
    circles.append((x, y, 70 * s * k))
    return cloud_shape(circles, "#f6efe0", 4.5)


def coin(x, y, k=1.0):
    return shape(ellipse_pts(x, y, 20 * k, 8 * k, 12), "#e8b95a", "", w=3, seed=460)


def waiter_fig(x, y, sc, fc, pose, flip=False):
    spec = waiter_spec(fc)
    fig = person.draw(spec, pose, x, y, sc, 500, flip)
    # белый фартук до колен поверх ног и туловища
    ap = [(-52 * (-1 if flip else 1) * 0 - 50, -340, 1), (50, -340, 1), (66, -120, 1), (-66, -120, 1)]
    apron = shape(ap, "#f8f2e0", blob([(10, -340), (50, -340), (66, -120), (20, -120)], "#ddd0b0", .8), w=4, seed=520)
    apron += line([(-50, -330), (50, -330)], 6, INK, taper=.05, wmin=.95, seed=521)
    return fig + f'<g transform="translate({f(x)} {f(y)}) scale({sc:.4f})">{apron}</g>'


# ════════════════════════ s08: психолог ════════════════════════
def frame_s08(t):
    u = clamp((t - 17.7) / 2.7)
    sc = 1.7
    x, yt = 470.0, 1010.0
    look_up = smooth(18.3, 18.5, t) * (1 - smooth(19.0, 19.25, t))
    write = 1 - look_up
    under_u = smooth(19.06, 19.5, t)
    # рука с карандашом: письмо — небольшие движения предплечья; на «заметила» — взмах подчёркивания
    wob = math.sin(t * 17) * 5 * write * (1 - smooth(18.95, 19.06, t))
    arms = {"R": (-4 + 2 * write * math.sin(t * 13), 78 + wob * .8 + 8 * under_u * math.sin((t - 19.06) * 14) * (1 - smooth(19.5, 19.7, t))),
            "L": (-8, -40)}
    spec = woman_spec(.55 - .25 * look_up)
    pose = dict(arms=arms, look=(.85 * look_up + (1 - look_up) * .15, .55 * (1 - look_up) + -.1 * look_up), blink=0.9 * bump(t, 17.95, .18) + .9 * bump(t, 19.4, .2),
                mouth="flat" if look_up < .5 else "o", brow=.4 * look_up, head_tilt=-4 * look_up + 8 * write)
    o = [interior(t)]
    # дальний план: второй столик и официант идёт с подносом
    wx = 930 - 180 * (t - 17.7) / 2.7
    o.append(chair_back(x, yt, sc))
    top, sk = table(x, yt, sc)
    o.append(top)
    hx0, hy0 = hand_xy(spec, pose, sc, x, yt + 312 * sc, "R")
    o.append(notebook(hx0 - 20 * sc, yt - 16, 1.15 * sc, lines_u=clamp(.5 + .5 * (t - 17.7) / 1.4), under_u=under_u))
    # фон: официанты (маленькие) за её спиной, к ним она обращает взгляд
    wp = dict(walk=(t * 6.0) % (2 * math.pi), arms={"L": (10, 80), "R": (-30, 120)}, look=(-.5, 0), mouth="smile")
    o.append(waiter_fig(wx, 1214, .8, -.4, wp))
    o.append(seated(spec, pose, x, yt, sc, 600))
    hx, hy = hand_xy(spec, pose, sc, x, yt + 312 * sc, "R")
    o.append(pencil(hx, hy + 2, -35 - 18 * look_up, 1.0 * sc))
    o.append(sk)
    o.append(cup(x - 120 * sc, yt - 6, .9 * sc, steam_t=t))
    cam = lib.cam(520 + 30 * u, 1060 + 20 * u, 1.0 + .12 * ease_io(u), -.5 + .9 * u)
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ════════════════════════ s09: заказы ════════════════════════
def frame_s09(t):
    u = clamp((t - 19.9) / 3.5)
    yt, sc = 900.0, 1.0
    tx = {"A": 180.0, "B": 520.0, "C": 890.0}
    T_PAY = 21.55
    cust = {
        "A": dict(spec=dict(skin="#e8bd98", hair="short", hair_c="#3a2a22", top="#6a5a4a", low="#4a4030", shoes="#2a2020", face=-.4, cap="#7a6a50", collar="#f2e6c8", sleeve="#6a5a4a"), x=tx["A"], gone=T_PAY + .1),
        "B": dict(spec=dict(skin="#efc7a4", hair="bun", hair_c="#7a4a2a", top="#5a7a58", low="#3a3a30", shoes="#2a2020", face=.3, collar="#f2e6c8", sleeve="#5a7a58"), x=tx["B"], gone=T_PAY + .28),
        "C1": dict(spec=dict(skin="#e3b894", hair="bald", hair_c="#8a7a6a", top="#8a6a4a", low="#3a3a30", shoes="#2a2020", face=.2, mustache=True, collar="#f2e6c8", sleeve="#8a6a4a"), x=tx["C"] - 90, gone=99),
        "C2": dict(spec=dict(skin="#eac3a0", hair="bob", hair_c="#2a2020", top="#7a4a58", low="#4d3b45", shoes="#2a2020", face=-.4, cloche="#506a60", collar="#f2e6c8", sleeve="#7a4a58", bw=.9), x=tx["C"] + 92, gone=99),
    }
    o = [interior(t, 1120)]
    layers_top, layers_skirt = [], []
    for k, (tk, xx) in enumerate(tx.items()):
        tp, sk_ = table(xx, yt, sc, rx=(180 if tk == "C" else 150))
        layers_top.append(tp)
        layers_skirt.append(sk_)
    o.append("".join(chair_back(c["x"], yt, sc, 1 if c["spec"]["face"] >= 0 else -1) for c in cust.values()))
    o.append("".join(layers_top))
    # пара чашек на столах
    for tk, xx in tx.items():
        o.append(cup(xx + (30 if tk != "C" else -2), yt - 8, .7, steam_t=t))
    # посетители
    poofs = ""
    slips = ""
    slip_t = {"A": 20.45, "B": 21.05, "C1": 21.5, "C2": 21.62}
    for nm, c in cust.items():
        gone = t >= c["gone"]
        if not gone:
            sway = math.sin(t * 2.2 + len(nm)) * 1.5
            sp = c["spec"]
            pose = dict(arms={"R": (-4, 80), "L": (-12, -60)}, look=(.4 if sp["face"] > 0 else -.4, .1), blink=0.9 * bump(t, 20.6 + len(nm) * .4, .18),
                        mouth="smile" if nm in ("A", "B") and t > 20.6 else "flat", head_tilt=sway)
            o.append(seated(sp, pose, c["x"], yt, sc, 700 + len(nm), flip=False))
        pf = (t - c["gone"] + .12) / .5
        poofs += poof(c["x"], yt - 120, pf, 1.0)
    o.append("".join(layers_skirt))
    # монеты на оплаченных
    for tk in ("A", "B"):
        tg = {"A": T_PAY, "B": T_PAY + .18}[tk]
        if t >= tg:
            ex = ease_out(clamp((t - tg) / .2))
            o.append(coin(tx[tk] - 30, yt - 8 - 30 * (1 - ex), .9))
    # официант: стоит у A (лицом влево), потом у B, потом у C
    if t < 20.78:
        wx, fc, flipw, walk = 300.0, -.5, True, None
    elif t < 21.0:
        v = ease_io(clamp((t - 20.78) / .22))
        wx, fc, flipw, walk = 300 + 90 * v, .5, False, None
    elif t < 21.45:
        v = ease_io(clamp((t - 21.05) / .38))
        wx, fc, flipw, walk = 390 + 360 * v, .5, False, (t * 11) % (2 * math.pi)
    else:
        wx, fc, flipw, walk = 750.0, .5, False, None
    wy = 1480
    writing = bump(t, 20.0, 99) if False else 1.0
    pw = dict(arms={"L": (30, 100 + 8 * math.sin(t * 15)), "R": (22, 108)}, look=(-.5 if flipw else .5, .2), mouth="smile", head_tilt=3 * math.sin(t * 4))
    if walk is not None:
        pw["walk"] = walk
    fig_w = waiter_fig(wx, wy, .9, -.5 if flipw else .5, pw, flip=False)
    o.append(fig_w)
    # значки заказов
    for nm, c in cust.items():
        k0 = slip_t[nm]
        k = ease_out(clamp((t - k0) / .28), 2.2) * (1 + .15 * math.sin(clamp((t - k0) / .28) * math.pi))
        if nm in ("A", "B"):
            k *= 1 - smooth(c["gone"] - .12, c["gone"], t)
            if t >= c["gone"]:
                k = 0
        if nm in ("C1", "C2"):
            k *= 1 - smooth(22.0, 22.22, t)
        slips += ticket(c["x"] - 6, yt - 300 * sc - 40, .8, k, t + len(nm))
    o.append(slips)
    o.append(poofs)
    # облако с блюдами над C
    cu = smooth(22.0, 22.3, t)
    if cu > 0:
        pul = 1 + .07 * math.sin(2 * math.pi * 2.3 * (t - 22.06)) * smooth(22.1, 22.4, t) + .22 * bump(t, 22.06, .3)
        cx_, cy_ = tx["C"] - 90, 360.0
        sc_c = cu * pul
        circ = [(-190, 20, 80), (-90, -50, 100), (30, -80, 110), (140, -40, 100), (210, 30, 76), (60, 50, 90), (-60, 56, 84)]
        base = cloud_shape([(x, y, r) for x, y, r in circ], "#fbf4e0", 6)
        # блюда: тарелка с котлетой, чашка, миска
        dish = shape(ellipse_pts(-110, 24, 62, 20, 16), "#fffaf0", "", w=3.6, seed=470) + shape(ellipse_pts(-110, 6, 42, 20, 14), "#a8663a", blob(ellipse_pts(-100, 0, 22, 8, 10), "#c98a54"), w=3.6, seed=471)
        dish += shape([(20, -30, 1), (86, -30, 1), (80, 44), (26, 44)], "#fbf4e0", blob([(60, -30), (86, -30), (80, 44), (54, 44)], "#dccfa8", .9), w=3.8, seed=472)
        dish += blob(ellipse_pts(53, -30, 33, 7, 10), "#6b3f26") + line([(86, -14), (110, -8), (84, 26)], 6, INK, taper=.1, wmin=.9, seed=473)
        dish += shape([(120, 0, 1), (200, 0, 1), (186, 46), (134, 46)], "#d9a86a", blob([(170, 0), (200, 0), (186, 46), (160, 46)], "#b8864a", .85), w=3.8, seed=474)
        dish += blob(ellipse_pts(160, 0, 40, 9, 12), "#e8dcc0") + blob(ellipse_pts(150, -8, 14, 8, 10), "#9fbf6a")
        dish += "".join(line([(x0 + 4 * math.sin(t * 3 + q), -60 - j * 18) for j in range(4) for q in (j,)], 4, "#f4efe2", taper=.8, wmin=.1, seed=480 + i, peak=.4)
                        for i, x0 in enumerate((40, 140)))
        tail = "".join(f'<circle cx="{cx_ - 20 + i * 4:.1f}" cy="{cy_ + 170 + i * 56:.1f}" r="{r}" fill="{INK}"/><circle cx="{cx_ - 20 + i * 4:.1f}" cy="{cy_ + 170 + i * 56:.1f}" r="{r - 4}" fill="#fbf4e0"/>'
                       for i, r in ((0, 24), (1, 15)))
        o.append(f'<g transform="translate({cx_} {cy_}) scale({sc_c:.4f}) translate({-cx_} {-cy_})">{tail}'
                 f'<g transform="translate({cx_} {cy_})">{base}{dish}</g></g>')
    cam = lib.cam(540 + 90 * ease_io(u), 900 + 30 * u, 1.0 + .16 * ease_io(u) + .04 * bump(t, 22.06, .3), -.8 + 1.6 * u)
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ════════════════════════ s07: календарь и фасад ════════════════════════
def calendar_scene(t):
    """Настенный календарь (без цифр): страницы листаются НАЗАД — каждая перекидывается сверху вниз поверх предыдущей; тон бумаги от серо-голубого к сепии."""
    cols = ["#e9eef2", "#efe7de", "#ecdcc0", "#e6cf9f", "#dfc28a"]
    o = [f'<rect x="-400" y="-400" width="1900" height="2700" fill="{mix("#8fa1ad", "#8a6a46", clamp((t - 15.4) / 1.3))}"/>']
    px0, py0, pw, ph = 130.0, 330.0, 820.0, 1040.0
    flips = [15.5 + .24 * i for i in range(4)]
    def page(col, idx, scale_y=1.0, face=True):
        sy = scale_y
        h = ph * abs(sy)
        top = py0
        pts = [(px0, top, 1), (px0 + pw, top, 1), (px0 + pw, top + h, 1), (px0, top + h, 1)]
        inner = ""
        if face and sy > 0:
            inner += blob(rect_pts(px0, top, px0 + pw, top + 150 * abs(sy)), mix(col, "#a9503a", .55))
            for r in range(5):
                for c in range(6):
                    xx = px0 + 40 + c * 118
                    yy = top + (200 + r * 150) * abs(sy)
                    inner += f'<rect x="{xx}" y="{yy:.1f}" width="100" height="{110 * abs(sy):.1f}" fill="none" stroke="#6a5a4a" stroke-width="3"/>'
                    if (r * 6 + c + idx) % 5 == 0:
                        inner += line([(xx + 24, yy + 30 * abs(sy)), (xx + 74, yy + 76 * abs(sy))], 5, "#4a4a5a", taper=.1, wmin=.9, seed=600 + r * 6 + c)
                        inner += line([(xx + 74, yy + 30 * abs(sy)), (xx + 24, yy + 76 * abs(sy))], 5, "#4a4a5a", taper=.1, wmin=.9, seed=700 + r * 6 + c)
        return shape(pts, col if sy > 0 else mix(col, "#7a5a30", .35), inner, w=4.6, seed=800 + idx)
    # нижний (самый ранний) лист — под всеми
    base_idx = 4
    o.append(blob([(px0 + 14, py0 + 18, 1), (px0 + pw + 14, py0 + 18, 1), (px0 + pw + 14, py0 + ph + 18, 1), (px0 + 14, py0 + ph + 18, 1)], "#3a2a20", .3))
    o.append(page(cols[4], 9))
    # листы возвращаются: i-й идёт сверху (угол 180° → 0°) и ложится на предыдущий
    for i in range(4):
        col = cols[3 - i]
        u = clamp((t - flips[i]) / .26)
        if u <= 0:
            continue
        ang = math.radians(180 * (1 - ease_in_out(u)))
        cs = math.cos(ang)
        if u >= 1:
            o.append(page(col, i))
        else:
            if cs >= 0:
                o.append(page(col, i, cs))
            else:
                # лист в воздухе над шарниром: виден оборот, поднят вверх
                h = ph * abs(cs)
                pts = [(px0, py0 - h, 1), (px0 + pw, py0 - h, 1), (px0 + pw, py0, 1), (px0, py0, 1)]
                o.append(shape(pts, mix(col, "#7a5a30", .3), "", w=4.6, seed=820 + i))
    # шапка: деревянная планка и два кольца
    o.append(shape(rect_pts(px0 - 30, py0 - 56, px0 + pw + 30, py0 - 4, 10), "#7a5232", blob(rect_pts(px0 - 30, py0 - 24, px0 + pw + 30, py0 - 4), "#5a3a22", .8), w=5, seed=830))
    for k, xx in enumerate((px0 + 160, px0 + pw - 160)):
        o.append(shape(ellipse_pts(xx, py0 - 30, 16, 16, 12), "#d9d2c0", "", w=4, seed=840 + k))
    return "".join(o)


def ease_in_out(u):
    return ease_io(u)


def facade(t):
    o = []
    sky = lin_grad([(0, "#ecd6a4", 1), (1, "#f4e4be", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="-900" y="-900" width="2900" height="3400" fill="url(#{sky})"/>')
    # стена: кирпич
    pat = "pb"
    DEFS.append(f'<pattern id="{pat}" width="90" height="40" patternUnits="userSpaceOnUse"><rect width="90" height="40" fill="#b27a58"/>'
                f'<path d="M0 20 H90 M0 0 H90 M45 0 V20 M0 20 V40 M90 20 V40" stroke="#8a5a3e" stroke-width="3.5" fill="none"/></pattern>')
    o.append(f'<rect x="-600" y="-900" width="2300" height="2300" fill="url(#{pat})"/>')
    for k, x0 in enumerate((70, 400, 730)):
        o.append(shape(rect_pts(x0 - 12, 60, x0 + 262, 400, 6), "#f2e6c8", blob(rect_pts(x0, 74, x0 + 250, 386), "#c9b078") +
                       blob(rect_pts(x0 + 118, 74, x0 + 132, 386), "#f2e6c8") + blob(rect_pts(x0, 220, x0 + 250, 234), "#f2e6c8"), w=4.6, seed=990 + k))
    o.append(f'<rect x="-600" y="1380" width="2300" height="900" fill="#cdb894"/>')
    for k in range(8):
        o.append(f'<rect x="-600" y="{1380 + k * 70 + (k * k) * 3}" width="2300" height="6" fill="#a8946c"/>')
    o.append(f'<rect x="-600" y="1372" width="2300" height="12" fill="{INK}"/>')
    # окна по бокам
    for k, x0 in enumerate((40, 760)):
        inner = f'<rect x="{x0}" y="800" width="280" height="500" fill="#f4dca0"/>'
        inner += blob(ellipse_pts(x0 + 140, 880, 60, 60, 14), "#fff0b0")
        # силуэты столиков внутри
        inner += blob(rect_pts(x0 + 20, 1200, x0 + 260, 1300), "#8a5c38")
        inner += blob(ellipse_pts(x0 + 90, 1190, 36, 16, 10), "#fbf4e0") + blob(ellipse_pts(x0 + 200, 1190, 36, 16, 10), "#fbf4e0")
        inner += blob(rect_pts(x0 + 130, 800, x0 + 150, 1300), "#f2e6c8")
        o.append(shape(rect_pts(x0 - 14, 786, x0 + 294, 1314, 8), "#f2e6c8", inner, w=5, seed=900 + k))
        o.append(shape(rect_pts(x0 - 24, 1300, x0 + 304, 1340, 6), "#7a5232", "", w=4.4, seed=902 + k))
        # ящик с цветами
        for j in range(6):
            o.append(blob(ellipse_pts(x0 + 30 + j * 44, 1286, 20, 22, 10), ["#6e8a62", "#a9503a"][j % 2]))
    # маркиза: полосатая
    aw = []
    n = 10
    x0, x1, ya, yb = -60, 1140, 540, 720
    for i in range(n):
        xa = x0 + (x1 - x0) * i / n
        xb = x0 + (x1 - x0) * (i + 1) / n
        col = "#a9503a" if i % 2 == 0 else "#f2e6c8"
        aw.append(shape([(xa, ya, 1), (xb, ya, 1), (xb + 6, yb, 1), (xa - 6, yb, 1)], col, "", w=4, seed=910 + i))
        aw.append(shape(ellipse_pts((xa + xb) / 2, yb + 4, (xb - xa) / 2 + 3, 20, 12), col, "", w=4, seed=930 + i))
    o.append("".join(aw))
    # дверь
    dx0, dx1, dy0, dy1 = 400, 680, 760, 1380
    o.append(shape(rect_pts(dx0 - 22, dy0 - 22, dx1 + 22, dy1, 8), "#5a3a22", "", w=5, seed=950))
    return "".join(o)


def door_and_bell(t, open_u, bell):
    dx0, dx1, dy0, dy1 = 400, 680, 760, 1380
    o = []
    # проём (тёплый свет внутри)
    ig = lin_grad([(0, "#f7dc98", 1), (1, "#c9954f", 1)], 0, 0, 0, 1)
    room_in = f'<rect x="{dx0}" y="{dy0}" width="{dx1 - dx0}" height="{dy1 - dy0}" fill="url(#{ig})"/>'
    room_in += f'<rect x="{dx0}" y="{dy0 + 330}" width="{dx1 - dx0}" height="{dy1 - dy0 - 330}" fill="#8a5c38"/>'
    room_in += f'<rect x="{dx0}" y="{dy1 - 150}" width="{dx1 - dx0}" height="150" fill="#5a3a22"/>'
    room_in += shape(ellipse_pts(540, dy0 + 120, 22, 22, 12), "#fff4c0", "", w=3, seed=953) + line([(540, dy0), (540, dy0 + 98)], 4, INK, taper=.02, wmin=.97, seed=954)
    room_in += blob(ellipse_pts(480, dy0 + 330, 60, 14, 12), "#fbf4e0") + blob(ellipse_pts(610, dy0 + 330, 60, 14, 12), "#fbf4e0")
    o.append(shape(rect_pts(dx0, dy0, dx1, dy1, 6), "#6a4222", room_in, w=4.4, seed=951))
    # створка: открывается внутрь (сужается к петле слева)
    k = 1 - .55 * open_u
    w = (dx1 - dx0) * k
    door = [(dx0, dy0, 1), (dx0 + w, dy0 + 10 * open_u, 1), (dx0 + w, dy1 - 10 * open_u, 1), (dx0, dy1, 1)]
    glass = blob([(dx0 + 30 * k, dy0 + 50, 1), (dx0 + w - 30 * k, dy0 + 60 * (1 - .1 * open_u), 1), (dx0 + w - 30 * k, dy0 + 420, 1), (dx0 + 30 * k, dy0 + 420, 1)], "#f4dca0")
    glass += line([(dx0 + w * .5, dy0 + 50), (dx0 + w * .5, dy0 + 420)], 5, "#7a5232", taper=.05, wmin=.95, seed=952)
    panels = blob([(dx0 + 30 * k, dy0 + 470, 1), (dx0 + w - 30 * k, dy0 + 470, 1), (dx0 + w - 30 * k, dy0 + 580, 1), (dx0 + 30 * k, dy0 + 580, 1)], "#7a4a2a") + blob([(dx0 + 30 * k, dy0 + 600, 1), (dx0 + w - 30 * k, dy0 + 600, 1), (dx0 + w - 30 * k, dy1 - 40, 1), (dx0 + 30 * k, dy1 - 40, 1)], "#7a4a2a")
    o.append(shape(door, "#9a6038", glass + panels, w=5, seed=953))
    o.append(shape(ellipse_pts(dx0 + w - 26 * k, dy0 + 520, 12, 12, 10), "#e8b95a", "", w=3, seed=954))
    # колокольчик на кронштейне над дверью
    bx, by = 540.0, 650.0
    o.append(line([(bx - 90, by - 70), (bx - 40, by - 70), (bx, by - 38)], 9, INK, taper=.02, wmin=.97, seed=960))
    sw = bell * math.sin(t * 2 * math.pi * 6) * 22
    g = f'<g transform="rotate({sw:.2f} {bx} {by - 40})">'
    g += line([(bx, by - 40), (bx, by - 20)], 5, INK, taper=.02, wmin=.97, seed=961)
    g += shape([(bx - 30, by + 40, 1), (bx - 22, by - 6), (bx, by - 22), (bx + 22, by - 6), (bx + 30, by + 40, 1)], "#e8b95a",
               blob([(bx + 8, by - 18), (bx + 22, by - 6), (bx + 30, by + 40), (bx + 8, by + 40)], "#c4902e", .9), w=4.2, seed=962)
    g += blob(ellipse_pts(bx, by + 46, 10, 10, 8), INK) + "</g>"
    o.append(g)
    if bell > .05:
        for sx in (-1, 1):
            for j in range(2):
                o.append(line([(bx + sx * (50 + 24 * j), by + 4 - 14 * j), (bx + sx * (70 + 28 * j), by - 4 - 20 * j)], 6, "#f2b53a", taper=.5, wmin=.3, seed=970 + j + sx * 3, op=1))
    return "".join(o)


def sign_board(t):
    sw = 3 * math.sin(t * 1.9)
    x, y = 150.0, 520.0
    o = [line([(x - 60, y - 140), (x + 130, y - 140)], 10, INK, taper=.02, wmin=.97, seed=980)]
    g = line([(x + 20, y - 136), (x + 20, y - 100)], 5, INK, taper=.02, wmin=.97, seed=981) + line([(x + 110, y - 136), (x + 110, y - 100)], 5, INK, taper=.02, wmin=.97, seed=982)
    board = shape(rect_pts(x - 40, y - 100, x + 170, y + 60, 12), "#f2e6c8", "", w=4.8, seed=983)
    cupg = cup(x + 65, y + 24, 1.25) + "".join(line([(x + 50 + 14 * j, y - 40 - q * 12 + 3 * math.sin(q + j * 2)) for q in range(3)], 4, "#b8a070", taper=.8, wmin=.1, seed=985 + j) for j in range(2))
    o.append(f'<g transform="rotate({sw:.2f} {x + 65} {y - 120})">{g}{board}{cupg}</g>')
    return "".join(o)


def frame_s07(t):
    swt = 16.70
    if t < swt:
        a = (t - 15.4)
        u2 = clamp((t - 16.35) / (swt - 16.35))
        s_ = 1.0 + 4.2 * ease_in_out(u2) ** 2 + .05 * (t - 15.4)
        rot = -2.0 + 1.6 * a
        body = f'<g transform="{lib.cam(540 + 0 * u2, 850, s_, rot)}">{calendar_scene(t)}</g>'
        blur = 2 + 16 * u2
    else:
        u = clamp((t - swt) / (18.1 - swt))
        pu = ease_io(u)
        s_ = 1.55 + .0 * u - .0
        zoom = 1.0 + 1.1 * pu ** 1.5
        if t < swt + .28:
            zoom *= 1 + 1.4 * (1 - (t - swt) / .28) ** 2
        open_u = smooth(17.55, 17.8, t)
        bell = bump(t, 17.52, .6) if t >= 17.52 else 0.0
        bell = max(bell, .15) if t >= 17.52 else 0.0
        g = facade(t) + sign_board(t) + door_and_bell(t, open_u, bell)
        body = f'<g transform="{lib.cam(540 - 10 * u, 1000 - 40 * u, zoom, .8 - 1.4 * u)}">{g}</g>'
        blur = 18 * max(0.0, 1 - (t - swt) / .22)
    if blur > 3:
        DEFS.append(f'<filter id="mb" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{blur:.1f} {blur * .15:.1f}"/></filter>')
        body = f'<g filter="url(#mb)">{body}</g>'
    return body


def frame(sid, t):
    lib.INK_K[0] = 1.0
    body = {"s07": frame_s07, "s08": frame_s08, "s09": frame_s09}[sid](t)
    return svg(f'<rect width="1920" height="1920" fill="#2a1f1a"/>{body}')
