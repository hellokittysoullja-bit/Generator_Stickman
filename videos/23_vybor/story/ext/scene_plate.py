"""Сцена plate (s03, s04): тарелка пасты с соусом и сыром на пледе в зелёную клетку (как у Димы), вилка рядом, пар.
Ночь: арт в «дневных» цветах → фильтр ночи (как герои 22-го), свет телевизора холодный слева и тёплый отсвет огонька
справа — осветлением по силуэту арта. s04: на «остыл» (3.92) последняя струйка тает, соус тускнеет, блики гаснут."""
import math

import numpy as np

import lib
from lib import (DEFS, INK, W, H, band, blob, blur, cam, clamp, ease_io, ellipse_pts, f, fill_d, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg, timing23)

NIGHT = (0.52, 0.56, 0.86)
PCX, PCY = 540, 1010            # центр тарелки
PRX, PRY = 440, 300             # внешний край
WRX, WRY = 318, 214             # дно-колодец
NCX, NCY = 540, 968             # гнездо пасты
COLD_AT = 3.92                  # «остыл»
_ST = {}


def plaid_defs():
    DEFS.append("""
<pattern id="pPl" width="88" height="88" patternUnits="userSpaceOnUse">
 <rect width="88" height="88" fill="#7aa66a"/>
 <rect x="0" width="34" height="88" fill="#5b8a50" opacity=".85"/>
 <rect y="0" width="88" height="34" fill="#5b8a50" opacity=".85"/>
 <rect width="34" height="34" fill="#3f6b3c"/>
 <rect x="56" width="5" height="88" fill="#d9e3a8" opacity=".75"/><rect y="56" width="88" height="5" fill="#d9e3a8" opacity=".75"/>
 <rect x="15" width="3" height="88" fill="#2a4630"/><rect y="15" width="88" height="3" fill="#2a4630"/>
 <rect x="74" width="2" height="88" fill="#a33f35" opacity=".8"/><rect y="74" width="88" height="2" fill="#a33f35" opacity=".8"/>
</pattern>
<pattern id="pPlP" href="#pPl" patternTransform="rotate(-8) scale(2.1 1.45)"/>
""")


def plaid():
    s = [f'<rect x="-300" y="-300" width="{W + 600}" height="{H + 600}" fill="url(#pPlP)"/>']
    # мягкие складки пледа: тень впадины + блик гребня + штрих
    folds = [[(-100, 420), (300, 520), (700, 470), (1200, 560)], [(-100, 1560), (250, 1640), (600, 1600), (1200, 1720)],
             [(-100, 1840), (420, 1920), (1200, 1880)], [(-60, 260), (400, 330), (1200, 280)]]
    for i, fl in enumerate(folds):
        dn = [(x, y + 34) for x, y in fl]
        s.append(blob(fl + dn[::-1], "#12241a", .42, blur(16)))
        up = [(x, y - 30) for x, y in fl]
        s.append(blob(up + [(x, y - 4) for x, y in fl][::-1], "#eef6c8", .14, blur(10)))
    # торчащие ворсинки по складке
    return "".join(s)


def plate():
    s = []
    # тень тарелки на пледе (мягкая, вниз-вправо)
    s.append(blob(ellipse_pts(PCX + 26, PCY + 44, PRX + 10, PRY + 6, 18), "#06100a", .55, blur(18)))
    outer = ellipse_pts(PCX, PCY, PRX, PRY, 20)
    inner = []
    inner.append(f'<rect x="{PCX - PRX - 10}" y="{PCY - PRY - 10}" width="{2 * PRX + 20}" height="{2 * PRY + 20}" fill="url(#gRim)"/>')
    # борт ближе к зрителю — толщина фарфора видна снизу
    inner.append(blob([(PCX - PRX, PCY + 6), (PCX - 300, PCY + 250), (PCX, PCY + PRY + 4), (PCX + 300, PCY + 250), (PCX + PRX, PCY + 6),
                       (PCX + PRX, PCY + 40), (PCX, PCY + PRY + 40), (PCX - PRX, PCY + 40)], "#b9b4c6", .0))
    s.append(shape(outer, "#f3efe6", "".join(inner), w=5.6, seed=801))
    # колодец: тень от борта сверху-слева, свет снизу-справа
    well = ellipse_pts(PCX + 4, PCY + 12, WRX, WRY, 18)
    winner = [f'<rect x="{PCX - WRX}" y="{PCY - WRY}" width="{2 * WRX}" height="{2 * WRY + 30}" fill="url(#gWell)"/>',
              blob(ellipse_pts(PCX - 30, PCY - 40, WRX + 20, WRY - 10, 16), "#c9c2d2", .55, blur(14))]
    s.append(shape(well, "#ece6dc", "".join(winner), w=3.2, seed=802, var=.4))
    # блик на борту
    s.append(line([(PCX - 360, PCY - 120), (PCX - 250, PCY - 230), (PCX - 90, PCY - 282)], 9, "#ffffff", seed=803, op=.7, taper=.8))
    s.append(line([(PCX + 330, PCY + 170), (PCX + 230, PCY + 238)], 6, "#ffffff", seed=804, op=.45, taper=.8))
    return "".join(s)


def strands(seed, n, layer_from=0.0, layer_to=1.0, rmax=1.0):
    """Спагетти гнездом: дуги-завитки вокруг центра, ракурс сверху-спереди, горка в центре; от дальних к ближним."""
    rs = np.random.RandomState(seed)
    RX, RY, HGT = 262, 170, 70
    items = []
    for k in range(n):
        r0 = math.sqrt(rs.uniform(0.04, 1.0)) * rmax
        a0 = rs.uniform(0, 2 * math.pi)
        span = rs.uniform(1.2, 3.6) * (1 if rs.rand() < .7 else -1)
        dr = rs.uniform(-0.35, 0.35) if k % 5 else rs.uniform(0.2, 0.45)
        m = 22
        pts = []
        for j in range(m):
            u = j / (m - 1)
            a = a0 + span * u
            r = clamp(r0 + dr * u + 0.06 * math.sin(u * 5 + k), 0.06, 1.12)
            x = NCX + RX * r * math.cos(a)
            y = NCY + RY * r * math.sin(a) - HGT * (1 - r * r)
            pts.append((x, y))
        depth = np.mean([p[1] for p in pts]) + 30 * rs.uniform(-1, 1)
        items.append((depth, k, pts))
    items.sort()
    out = []
    for j, (depth, k, pts) in enumerate(items):
        u = j / max(1, len(items) - 1)
        col = mix("#d29e48", "#f4d27c", 0.35 + 0.65 * u * rs.uniform(.8, 1.0))
        out.append(strand(pts, 11, k + seed * 100, col))
    return out


def strand(pts, w, sd, col="#f0c86a"):
    if len(pts) < 8:
        pts = [tuple(p) for p in lib.sample(pts, False, step=12)]
    poly = band(pts, w, w * .95, step=5, cap=True)
    d = fill_d(poly)
    hi = line([(x - 1.5, y - 2.5) for x, y in pts[2:-2]], 3.0, "#fff2c8", seed=sd, op=.8, taper=.5, wmin=.2)
    sh = line([(x + 1.5, y + 3) for x, y in pts[1:-1]], 3.6, "#c9973c", seed=sd + 1, op=.7, taper=.4, wmin=.3)
    return (f'<path d="{d}" fill="{col}"/>{sh}{hi}'
            f'<path d="{lib.ink_closed(poly, 2.2, var=.3, weight=.5, seed=sd % 100000)}" fill="{INK}" opacity=".9"/>')


SAUCE = [(470, 860), (520, 842), (580, 846), (628, 868), (650, 900), (642, 938), (606, 960), (556, 968), (500, 962),
         (456, 942), (436, 908), (446, 878)]
SC_K, SC_C = 1.3, (545, 905)


def sauce_art():
    return f'<g transform="translate({SC_C[0]} {SC_C[1]}) scale({SC_K}) translate({-SC_C[0]} {-SC_C[1]})">' + _sauce_art() + "</g>"


def _sauce_art():
    s = []
    inner = blob([(520, 930), (600, 920), (650, 900), (642, 938), (606, 960), (556, 968), (500, 962), (470, 950)], "#8e2416", .9)
    inner += blob([(460, 870), (520, 850), (560, 860), (510, 880), (470, 900)], "#e8604a", .7)
    rs = np.random.RandomState(31)
    for k in range(9):
        x, y = 470 + rs.uniform(0, 160), 868 + rs.uniform(0, 80)
        inner += shape(ellipse_pts(x, y, rs.uniform(9, 16), rs.uniform(6, 10), 9, rot=rs.uniform(0, 180), jitter=.2, seed=k),
                       "#a82a1a", blob(ellipse_pts(x - 3, y - 3, 5, 3, 8), "#ef7a5a", .8), w=2.2, seed=860 + k)
    s.append(shape(SAUCE, "#c7392a", inner, w=4.2, seed=850))
    # соус стекает между нитями — пара языков
    return "".join(s)


def gloss():
    return (blob(ellipse_pts(492, 872, 22, 8, 10, rot=-20), "#ffffff", .85) +
            blob(ellipse_pts(600, 880, 12, 5, 10, rot=-10), "#ffffff", .7) +
            blob(ellipse_pts(540, 860, 6, 3, 8), "#ffffff", .8) + blob(ellipse_pts(470, 912, 5, 3, 8), "#ffffff", .7))


def cheese():
    rs = np.random.RandomState(5)
    s = []
    for k in range(46):
        a = rs.uniform(0, 2 * math.pi)
        r = math.sqrt(rs.uniform(0, 1))
        x = 545 + 190 * r * math.cos(a)
        y = 905 + 105 * r * math.sin(a) - 10
        w_, h_ = rs.uniform(9, 15), rs.uniform(2.6, 4)
        rot = rs.uniform(0, 180)
        s.append(blob(ellipse_pts(x, y, w_, h_, 6, rot=rot, jitter=.25, seed=k), "#fff6cf"))
        if k % 3 == 0:
            s.append(blob(ellipse_pts(x + 1, y + 1.5, w_, h_ * .5, 6, rot=rot), "#d8c48a", .7))
    return "".join(s)


def basil():
    leaf = [(560, 846), (600, 822), (640, 820), (626, 846), (596, 860)]
    inner = blob([(570, 850), (626, 836), (626, 846), (596, 860)], "#2f6b2a", .8)
    return shape(leaf, "#4c9a3c", inner + line([(566, 846), (600, 836), (632, 824)], 2.2, "#22501e", seed=881), w=3, seed=880)


def fork():
    """Вилка лежит справа-снизу на пледе, зубцами к тарелке."""
    s = []
    rot = -58
    def P(pts):
        return lib.T(pts, 905, 1470, 1.0, rot, 0, 0)
    # тень
    s.append(blob(P([(-300, 10), (120, 22), (170, 40), (300, 30), (300, 60), (-300, 40)]), "#06100a", .5, blur(8)))
    handle = P([(-300, -16), (-260, -24), (-80, -12), (60, -7), (60, 7), (-80, 12), (-260, 24), (-300, 16, 1)])
    s.append(shape(handle, "#c9ccd8", blob(P([(-300, 4), (60, 2), (60, 7), (-300, 18)]), "#8e92a6", .9) +
                   line(P([(-280, -10), (-100, -6), (40, -3)]), 4, "#ffffff", seed=891, op=.85), w=3.6, seed=890))
    head = P([(56, -9), (110, -26), (226, -27, 1), (226, -19, 1), (124, -15), (124, -6), (226, -7, 1), (226, 1, 1), (124, 2),
              (124, 9), (226, 9, 1), (226, 17, 1), (124, 18), (124, 25), (226, 27, 1), (226, 33, 1), (112, 34), (56, 9)])
    s.append(shape(head, "#d3d6e2", blob(P([(60, 3), (124, 20), (226, 30), (226, 33), (112, 34), (56, 9)]), "#8e92a6", .8) +
                   line(P([(70, -6), (120, -18), (200, -22)]), 3, "#ffffff", seed=893, op=.8), w=3, seed=892, var=.2))
    return "".join(s)


def light_defs():
    DEFS.append(f"""
<filter id="fNight" x="-400" y="-400" width="1880" height="2720" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
 <feColorMatrix type="matrix" values="{NIGHT[0] * .9} {NIGHT[0] * .1} 0 0 0  {NIGHT[1] * .05} {NIGHT[1] * .9} {NIGHT[1] * .05} 0 0  0 {NIGHT[2] * .1} {NIGHT[2] * .9} 0 0  0 0 0 1 0"/>
</filter>""")
    lin_grad([(0, "#ffffff", 1), (.5, "#f3efe6", 1), (1, "#cfc6d4", 1)], 0, 0, .3, 1, gid="gRim")
    lin_grad([(0, "#cfc6d0", 1), (.45, "#ece6dc", 1), (1, "#f6f1e8", 1)], 0, 0, 0, 1, gid="gWell")
    # холодный свет экрана слева сверху, тёплый отсвет огонька справа
    rad_grad([(0, "#a8ccff", .9), (.35, "#6e9ef0", .5), (.75, "#4a6fc0", .12), (1, "#4a6fc0", 0)], -180, 640, 1250, 1050, gid="gScr")
    rad_grad([(0, "#ffb060", .8), (.35, "#ff8a3a", .38), (.8, "#c05a22", .06), (1, "#c05a22", 0)], 1240, 1180, 640, 700, gid="gFl")


def build_static():
    if _ST:
        return _ST
    light_defs()
    plaid_defs()
    _ST["plaid"] = plaid()
    _ST["plate"] = plate()
    under = strands(11, 64, rmax=1.0)
    shadow = blob(ellipse_pts(NCX + 14, NCY + 34, 280, 168, 16), "#5a4a52", .55, blur(14))
    _ST["pasta_under"] = shadow + "".join(under)
    _ST["sauce"] = sauce_art()
    _ST["over"] = "".join(strand(p, 11, 9000 + i) for i, p in enumerate([
        [(436, 902), (452, 870), (490, 850), (530, 846)], [(650, 936), (636, 962), (596, 974), (560, 972)],
        [(600, 846), (630, 862), (652, 896)], [(462, 950), (500, 970), (540, 972)]]))
    _ST["cheese"] = cheese()
    _ST["basil"] = basil()
    _ST["gloss"] = gloss()
    _ST["fork"] = fork()
    lib.static_done()
    return _ST


# ───────── пар
WISPS = [  # x0, y0, фаза, амплитуда, скорость, ширина, время, когда перестаёт идти
    (470, 900, 0.0, 46, 150, 44, 3.28),
    (535, 860, 1.7, 56, 165, 54, 3.52),
    (615, 885, 3.1, 50, 140, 46, 3.40),
    (410, 960, 4.4, 40, 130, 36, 3.12),
    (680, 940, 2.2, 42, 135, 38, 3.22),
    (555, 905, 5.3, 52, 150, 50, 3.92),   # последняя — тает на «остыл»
]


def ribbon(pts, widths):
    P = np.array(pts)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    L = P + N * widths[:, None] / 2
    R = P - N * widths[:, None] / 2
    return [tuple(p) for p in L] + [tuple(p) for p in R[::-1]]


def steam(t):
    """Пар — мягкие S-ленты, сужающиеся к концам; частицы поднимаются и качаются, поэтому волна бежит вверх.
    Струйка перестаёт идти в своё время: низ отрывается и тает, хвост уходит вверх."""
    s = []
    for i, (x0, y0, ph, A, v, wd, stop) in enumerate(WISPS):
        amax = 3.4
        amin = max(0.0, t - stop)
        if amin >= amax - 0.3:
            continue
        ages = np.linspace(amin, amax, 46)
        pts = []
        for a in ages:
            e = t - a
            y = y0 - v * a - 8 * a * a
            x = x0 + A * (a ** 0.8) * math.sin(ph + 2.4 * e + 1.6 * a) + 16 * a * math.sin(ph)
            pts.append((x, y))
        u = (ages - 0) / amax
        prof = np.sin(np.clip(u, 0, 1) * math.pi) ** 0.6
        wid = wd * (0.35 + 0.9 * u) * prof + 2
        if amin > 0:      # оторвавшийся низ — сужается
            wid *= np.clip((ages - amin) / 0.35, 0.05, 1)
        poly = ribbon(pts, wid)
        ytop, ybot = pts[-1][1], pts[0][1]
        k0 = 0.42 * (1 - smooth(0.0, 0.55, amin))
        if k0 < 0.004:
            continue
        g = lib.lin_grad([(0, "#f4f6ff", 0), (.5, "#f4f6ff", .55 * k0), (.85, "#f4f6ff", k0), (1, "#f4f6ff", k0 * .6)],
                         0, ytop, 0, ybot, units="userSpaceOnUse")
        d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in poly) + "Z"
        s.append(f'<path d="{d}" fill="url(#{g})" {blur(5)}/>')
        s.append(f'<path d="{d}" fill="url(#{g})" opacity=".5" transform="translate(0 0)" {blur(14)}/>')
    return "".join(s)


def frame(sid, t):
    st = build_static()
    lib.dyn_begin()
    cold = smooth(COLD_AT - 0.05, COLD_AT + 0.6, t)
    tvl = timing23.tv(t)
    fl = timing23.flame(t)
    # соус тускнеет (не прозрачная фигура — та же форма, цвет под «застывший»)
    dull = (f'<g transform="translate({SC_C[0]} {SC_C[1]}) scale({SC_K}) translate({-SC_C[0]} {-SC_C[1]})">'
            f'<path d="{fill_d(SAUCE)}" fill="#7a4a3c" opacity="{0.42 * cold:.3f}"/></g>') if cold > 0 else ""
    gl_op = 1 - cold
    SG = f'<g transform="translate({SC_C[0]} {SC_C[1]}) scale({SC_K}) translate({-SC_C[0]} {-SC_C[1]})">'
    art = (st["plaid"] + st["plate"] + st["fork"] + st["pasta_under"] + st["sauce"] + dull + SG + st["over"] + "</g>" + st["cheese"] + st["basil"]
           + (f'<g opacity="{gl_op:.3f}" transform="translate({SC_C[0]} {SC_C[1]}) scale({SC_K}) translate({-SC_C[0]} {-SC_C[1]})">{st["gloss"]}</g>' if gl_op > 0.01 else ""))
    light = (f'<rect x="-300" y="-300" width="{W + 600}" height="{H + 600}" fill="url(#gScr)" opacity="{clamp(.42 * tvl, 0, 1):.3f}"/>'
             f'<rect x="-300" y="-300" width="{W + 600}" height="{H + 600}" fill="url(#gFl)" opacity="{clamp(.7 * fl, 0, 1):.3f}"/>')
    if sid == "s03":
        u = ease_io((t - 2.44) / 1.68)
        cm = cam(560, 930 - 10 * u, 1.24 + 0.08 * u)
    else:
        u = (t - 3.72) / 1.25
        cm = cam(566 + 8 * u, 918 - 4 * u, 1.34 + 0.008 * u)
    body = (f'<g transform="{cm}"><g style="isolation:isolate"><g filter="url(#fNight)">{art}</g>'
            f'<g style="mix-blend-mode:screen">{light}</g></g>{steam(t)}</g>')
    return lib.svg(body)
