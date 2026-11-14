"""Комната Димы в ремонте (рилс 38), угол с окном и подоконником — мир сцены cat (s04, s16, s17, s18).
Общие предметы брифа: старые жёлтые обои, новая краска мятная, лампа-переноска на крючке, банка краски белая с мятным
потёком; подоконник в s04 затянут прозрачной плёнкой со шпателем, в s16–s18 — свежий белый с горшком растения; лист
на стене — белый, на скотче, строки чёрным маркером от руки (шрифт Caveat), зачёркивание красным, свиток до пола.

Мир (px): окно — стекло x 420…1000, y 300…985; подоконник: верх (задний край) SILL_B=1012, передний край SILL_F=1050,
торец до 1084, x 330…1090; под ним батарея; пол от FLOOR=1560. Кот сидит на подоконнике (низ лап на y≈1036).
state: 'reno' (s04: стена слева покрашена мятной наполовину, справа жёлтые обои; подоконник в плёнке)
       'done' (s16–s18: стена мятная, подоконник белый, батарея белая, лист со списком слева от окна)."""
import math

import numpy as np

import lib
from lib import INK, blob, ellipse_pts, f, line, mix, rect_pts, shape

WIN = (420, 1000, 300, 985)              # стекло: x0, x1, y0, y1
SILL_B, SILL_F, SILL_E = 1012.0, 1050.0, 1084.0
SILL_X0, SILL_X1 = 330.0, 1090.0
FLOOR = 1560
CAT_Y = 1036.0                           # низ лап кота на подоконнике

YEL, YEL_SH, YEL_D = "#ecd27e", "#d6b862", "#c49d45"
MINT, MINT_SH, MINT_L = "#a9dcc4", "#86c2a7", "#c6eadb"
PLASTER = "#cfc6b4"
FRAME, FRAME_SH = "#f1ece1", "#d3cbbb"
WHITE, WHITE_SH = "#fbfaf6", "#dedbd2"
LIST_LINES = ["покрасил стену", "поменял розетку", "положил плитку", "повесил лампу", "зашпаклевал угол", "покрасил батарею"]
LIST_MORE = ["снял плинтус", "купил грунтовку", "помыл валик"]


def _rs(*k):
    return np.random.RandomState(abs(hash(k)) % 2**31)


def wallpaper_pattern():
    """Старые обои: жёлтые, вертикальные полосы и мелкий ромбик-цветок."""
    if any('id="pWp38"' in d for d in lib.DEFS):
        return "pWp38"
    w, h = 96, 120
    inner = f'<rect width="{w}" height="{h}" fill="{YEL}"/>'
    inner += f'<rect x="0" y="0" width="6" height="{h}" fill="{YEL_SH}" opacity=".7"/><rect x="48" y="0" width="3" height="{h}" fill="{YEL_SH}" opacity=".55"/>'
    for (cx, cy) in ((26, 30), (74, 90)):
        inner += (f'<path d="M{cx} {cy - 9} L{cx + 7} {cy} L{cx} {cy + 9} L{cx - 7} {cy} Z" fill="{YEL_D}" opacity=".6"/>'
                  f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="#f6e6ad"/>')
    lib.DEFS.append(f'<pattern id="pWp38" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{inner}</pattern>')
    return "pWp38"


def mint_edge(x_top, x_bot, y0, y1, seed=1):
    """Неровная граница свежей краски (валик): волна сверху вниз."""
    rs = np.random.RandomState(seed)
    ys = np.linspace(y0, y1, 40)
    ph = rs.uniform(0, 6, 3)
    return [(x_top + (x_bot - x_top) * (y - y0) / (y1 - y0) + 22 * math.sin(y / 90 + ph[0]) + 10 * math.sin(y / 31 + ph[1])
             + 5 * math.sin(y / 13 + ph[2]), y) for y in ys]


def wall(state):
    s = []
    wp = wallpaper_pattern()
    s.append(f'<rect x="-1600" y="-1600" width="4400" height="{FLOOR + 1600}" fill="url(#{wp})"/>')
    if state == "reno":
        # ободранный кусок обоев у правого края (штукатурка)
        tear = [(1180, 380), (1260, 350), (1330, 420), (1320, 560), (1350, 700), (1270, 760), (1210, 690), (1170, 560)]
        s.append(shape(tear, PLASTER, blob([(1200, 600), (1330, 560), (1350, 700), (1270, 760)], "#b9af9b", .8), w=3.6, seed=1101))
        s.append(line([(1260, 352), (1290, 330), (1305, 360)], 4, INK, seed=1102))
        s.append(shape([(1260, 350), (1300, 328), (1318, 362), (1290, 372)], "#f3e0a0", "", w=3.2, seed=1103))
        # мятная краска: всё левее неровной границы (x≈200), сверху вниз
        edge = mint_edge(150, 230, -1600, FLOOR, seed=3)
        poly = [(-1600, -1600)] + edge + [(-1600, FLOOR)]
        inner = "".join(line([(x, -1600), (x + 10, FLOOR)], 30, MINT_L, taper=.05, wmin=.9, seed=1110 + k, op=.35)
                        for k, x in enumerate(range(-1500, 200, 140)))
        s.append(shape(poly, MINT, inner, w=0, ink=False))
        s.append(line(edge, 2.6, MINT_SH, taper=.05, wmin=.8, seed=1111))
        # потёки краски
        for k, (x, y, L) in enumerate(((172, 620, 60), (205, 980, 44), (160, 1360, 70))):
            s.append(shape([(x - 6, y), (x + 6, y), (x + 5, y + L), (x, y + L + 8), (x - 5, y + L)], MINT, "", w=2.4, seed=1120 + k))
    else:
        s.append(f'<rect x="-1600" y="-1600" width="4400" height="{FLOOR + 1600}" fill="{MINT}"/>')
        s += [line([(x, -1600), (x + 8, FLOOR)], 30, MINT_L, taper=.05, wmin=.9, seed=1130 + k, op=.3)
              for k, x in enumerate(range(-1500, 2700, 160))]
        # дальний правый угол ещё в обоях (комната не вся) — за окном, мельком
        edge = mint_edge(1500, 1540, -1600, FLOOR, seed=5)
        poly = edge + [(2800, FLOOR), (2800, -1600)]
        s.append(f'<path d="{lib.fill_d([p + (1,) for p in [edge[0]] + poly])}" fill="url(#{wp})"/>')
        s.append(line(edge, 2.6, MINT_SH, taper=.05, wmin=.8, seed=1131))
    # карниз-потолок
    s.append(shape(rect_pts(-1600, -60, 2800, -20), "#efe9dc", "", w=3.6, seed=1140))
    return "".join(s)


def sky(t):
    x0, x1, y0, y1 = WIN
    g = lib.lin_grad([(0, "#2c3a74", 1), (.55, "#5a64a8", 1), (.85, "#c98aa0", 1), (1, "#f2b48a", 1)], 0, 0, 0, 1)
    o = f'<rect x="{x0 - 30}" y="{y0 - 30}" width="{x1 - x0 + 60}" height="{y1 - y0 + 60}" fill="url(#{g})"/>'
    o += blob(ellipse_pts(x0 + 130, y0 + 120, 44, 44, 18), "#fbf1cf")
    o += blob(ellipse_pts(x0 + 150, y0 + 108, 40, 40, 18), "#4a5592", 1.0)     # серп луны
    for k, (x, y) in enumerate([(x0 + 300, y0 + 80), (x0 + 470, y0 + 150), (x0 + 380, y0 + 240), (x0 + 540, y0 + 60), (x0 + 60, y0 + 260)]):
        r = 3.6 + 1.3 * math.sin(t * 3 + k * 1.7)
        o += blob(ellipse_pts(x, y, r, r, 6), "#f6efd8")
    # дальний город — дымчатый, светлее (кот на его фоне читается)
    rs = np.random.RandomState(31)
    xs = np.linspace(x0 - 30, x1 + 30, 13)
    pts = [(x0 - 30, y1 + 30)]
    for i in range(12):
        h = rs.uniform(40, 120)
        pts += [(xs[i], y1 - h), (xs[i + 1], y1 - h)]
    pts += [(x1 + 30, y1 + 30)]
    o += blob(pts, "#8d7fb0", .9)
    for i in range(12):
        if rs.rand() < .6:
            wx = xs[i] + 14
            o += blob(rect_pts(wx, y1 - 30, wx + 10, y1 - 18), "#ffd98a", .9)
    return o


def window(t, state):
    x0, x1, y0, y1 = WIN
    s = []
    # откос (ниша окна)
    s.append(shape([(x0 - 70, y0 - 70, 1), (x1 + 70, y0 - 70, 1), (x1 + 70, SILL_B, 1), (x0 - 70, SILL_B, 1)],
                   FRAME if state == "done" else PLASTER,
                   blob([(x1, y0 - 70), (x1 + 70, y0 - 70), (x1 + 70, SILL_B), (x1, SILL_B)], FRAME_SH if state == "done" else "#b9af9b", .9),
                   w=4.4, seed=1150))
    inner = sky(t)
    mx = (x0 + x1) / 2
    inner += blob(rect_pts(mx - 16, y0 - 10, mx + 16, y1 + 10), FRAME) + blob(rect_pts(mx + 4, y0, mx + 16, y1), FRAME_SH, .9)
    inner += line([(mx - 16, y0), (mx - 16, y1)], 3.4, INK, taper=.05, wmin=.9, seed=1151)
    inner += line([(mx + 16, y0), (mx + 16, y1)], 3.4, INK, taper=.05, wmin=.9, seed=1152)
    # блики на стекле
    for k, (a, b) in enumerate((((x0 + 40, y0 + 330), (x0 + 150, y0 + 200)), ((x0 + 70, y0 + 360), (x0 + 120, y0 + 300)),
                                ((mx + 60, y0 + 300), (mx + 170, y0 + 170)))):
        inner += line([a, b], 9 if k != 1 else 5, "#ffffff", taper=.3, wmin=.3, seed=1153 + k, op=.35)
    s.append(shape(rect_pts(x0, y0, x1, y1, 4), "#3c4a86", inner, w=5, seed=1160))
    # рама
    fr = [(x0 - 26, y0 - 26), (x1 + 26, y0 - 26), (x1 + 26, y1), (x0 - 26, y1)]
    holes = f'M{x0} {y0} L{x0} {y1} L{x1} {y1} L{x1} {y0} Z'
    s.append(f'<path d="{lib.fill_d([p + (1,) for p in fr])} {holes}" fill="{FRAME}" fill-rule="evenodd"/>')
    s.append(blob([(x1, y0 - 26), (x1 + 26, y0 - 26), (x1 + 26, y1), (x1, y1)], FRAME_SH, .9))
    s.append(f'<path d="{lib.ink_closed([p + (1,) for p in fr], 4.6 * lib.INK_K[0], seed=1161)}" fill="{INK}"/>')
    return "".join(s)


def radiator(state):
    s = []
    col, sh = (WHITE, WHITE_SH) if state == "done" else ("#d8cbb0", "#b7a789")
    x0, x1, y0, y1 = 480, 960, SILL_E + 80, SILL_E + 340
    s.append(blob(rect_pts(x0 + 10, y0 + 14, x1 + 14, y1 + 18), "#000000", .12, lib.blur(8)))
    n = 10
    w = (x1 - x0) / n
    for k in range(n):
        xa = x0 + k * w + 4
        inner = blob(rect_pts(xa + w * .6, y0, xa + w, y1), sh, .9)
        if state != "done" and k % 3 == 1:
            inner += blob(ellipse_pts(xa + w * .4, y0 + 120 + k * 9, 8, 14, 8), "#a8743e", .7)
        s.append(shape(rect_pts(xa, y0, xa + w - 6, y1, 14), col, inner, w=3.6, seed=1170 + k))
    s.append(shape(rect_pts(x0 - 20, y0 + 40, x0 + 6, y0 + 70, 4), "#c9c3b4", "", w=3, seed=1185))
    return "".join(s)


def sill(state):
    """Подоконник: верхняя плоскость (трапеция в лёгкой перспективе) и торец."""
    s = []
    col, sh = (WHITE, WHITE_SH) if state == "done" else ("#e9e2d2", "#cbc2ae")
    s.append(blob(rect_pts(SILL_X0 + 10, SILL_E, SILL_X1 - 10, SILL_E + 40), "#000000", .18, lib.blur(10)))
    top = [(SILL_X0 + 22, SILL_B, 1), (SILL_X1 - 22, SILL_B, 1), (SILL_X1, SILL_F, 1), (SILL_X0, SILL_F, 1)]
    inner = ""
    if state == "done":
        inner += line([(SILL_X0 + 70, SILL_B + 14), (SILL_X0 + 420, SILL_B + 12)], 7, "#ffffff", taper=.4, seed=1191, op=.9)
        inner += line([(SILL_X0 + 470, SILL_B + 13), (SILL_X0 + 560, SILL_B + 12)], 5, "#ffffff", taper=.4, seed=1192, op=.9)
    s.append(shape(top, col, inner, w=4.4, seed=1190))
    s.append(shape(rect_pts(SILL_X0, SILL_F, SILL_X1, SILL_E, 5), mix(col, "#000000", .04), blob(rect_pts(SILL_X0, SILL_E - 12, SILL_X1, SILL_E), sh, .9),
                   w=4.4, seed=1193))
    return "".join(s)


def film(t):
    """Прозрачная плёнка на подоконнике s04: лежит складками, свисает с края волной, по углам малярный скотч."""
    s = []
    rs = np.random.RandomState(51)
    xs = np.linspace(SILL_X0 - 14, SILL_X1 + 14, 16)
    hang = [(x, SILL_E + 34 + 18 * math.sin(i * 1.3) + 10 * rs.rand() + 3 * math.sin(t * 2 + i)) for i, x in enumerate(xs)]
    pts = [(SILL_X0 + 6, SILL_B - 6, 1), (SILL_X1 - 6, SILL_B - 6, 1)] + [(SILL_X1 + 14, SILL_F, 1)] + hang[::-1] + [(SILL_X0 - 14, SILL_F, 1)]
    s.append(f'<path d="{lib.fill_d(pts)}" fill="#eef6ff" opacity=".58"/>')
    s.append(f'<path d="{lib.ink_closed(pts, 2.4 * lib.INK_K[0], seed=1199)}" fill="#6b7f9a" opacity=".9"/>')
    for i in range(1, 15, 2):
        x = xs[i]
        s.append(line([(x - 6, SILL_F + 2), (x + 4, hang[i][1] - 6)], 5, "#ffffff", taper=.5, wmin=.2, seed=1200 + i, op=.9))
        s.append(line([(x + 10, SILL_F + 6), (x + 18, hang[i][1] - 4)], 2.4, "#7f93ad", taper=.5, wmin=.2, seed=1230 + i, op=.7))
    for k, (a, b) in enumerate((((SILL_X0 + 60, SILL_B + 8), (SILL_X0 + 210, SILL_F - 8)), ((SILL_X0 + 380, SILL_B + 6), (SILL_X0 + 300, SILL_F - 6)),
                                ((SILL_X1 - 160, SILL_B + 8), (SILL_X1 - 60, SILL_F - 6)))):
        s.append(line([a, b], 3.2, "#ffffff", taper=.5, wmin=.2, seed=1210 + k, op=.8))
        s.append(line([(a[0] + 4, a[1] + 3), (b[0] + 4, b[1] + 3)], 2.2, "#7f93ad", taper=.5, wmin=.2, seed=1215 + k, op=.6))
    s.append(line(hang, 2.6, "#6b7f9a", taper=.1, wmin=.6, seed=1220, op=.85))
    for k, x in enumerate((SILL_X0 + 40, SILL_X1 - 60)):
        s.append(shape([(x - 34, SILL_F - 8, 1), (x + 30, SILL_F - 14, 1), (x + 34, SILL_F + 18, 1), (x - 30, SILL_F + 22, 1)], "#e9d9a8",
                       blob([(x - 34, SILL_F + 8), (x + 34, SILL_F + 4), (x + 34, SILL_F + 18), (x - 30, SILL_F + 22)], "#d4c08a", .8), w=2.8, seed=1225 + k))
    return "".join(s)


def spatula(x, y, k=1.0, rot=-8.0):
    """Шпатель лежит на подоконнике: стальное полотно с пятном шпаклёвки, деревянная ручка."""
    blade = [(-70, -6, 1), (0, -10, 1), (0, 10, 1), (-70, 14, 1)]
    inner = blob([(-70, 4), (0, 2), (0, 10), (-70, 14)], "#9aa3ae", .9)
    inner += blob(ellipse_pts(-44, 0, 18, 7, 10), "#efe8d8")
    inner += line([(-64, -4), (-10, -7)], 3, "#ffffff", taper=.4, seed=1231, op=.8)
    o = shape(blade, "#c3cad3", inner, w=3.4, seed=1230)
    o += shape(rect_pts(0, -6, 20, 6, 2), "#8c949e", "", w=3, seed=1232)
    o += shape(rect_pts(20, -9, 92, 9, 8), "#c9874a", blob(rect_pts(20, 2, 92, 9), "#a2622d", .9), w=3.4, seed=1233)
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(k)})">'
            + blob(ellipse_pts(10, 12, 90, 7, 12), "#000000", .18, lib.blur(3)) + o + "</g>")


def paint_can(x, y, k=1.0, roller=False, t=0.0):
    """Банка краски: белая, мятный потёк по краю, мятная этикетка-полоса (без букв). (x, y) — низ-центр."""
    o = [blob(ellipse_pts(x + 8 * k, y + 2 * k, 70 * k, 9 * k, 14), "#000000", .22, lib.blur(4))]
    w, h = 62 * k, 120 * k
    body = [(x - w, y - h, 1), (x + w, y - h, 1), (x + w, y - 10 * k, 1)]
    body += [(x + w * math.cos(a), y - 10 * k + 10 * k * math.sin(a)) for a in [math.pi * j / 8 for j in range(1, 8)]]
    body += [(x - w, y - 10 * k, 1)]
    inner = blob([(x + w * .45, y - h), (x + w, y - h), (x + w, y), (x + w * .45, y)], WHITE_SH, .9)
    inner += blob(rect_pts(x - w, y - h * .62, x + w, y - h * .34), MINT)
    inner += blob(rect_pts(x + w * .45, y - h * .62, x + w, y - h * .34), MINT_SH, .9)
    inner += shape([(x - w * .5, y - h - 2), (x - w * .3, y - h - 2), (x - w * .32, y - h * .58), (x - w * .4, y - h * .52), (x - w * .48, y - h * .6)],
                   MINT, "", w=2.4, seed=1241)
    o.append(shape(body, WHITE, inner, w=4, seed=1240))
    o.append(shape(ellipse_pts(x, y - h, w, 12 * k, 18), "#d5d2ca", blob(ellipse_pts(x, y - h + 2 * k, w * .82, 8 * k, 16), MINT), w=3.8, seed=1242))
    # дужка
    o.append(line([(x - w + 4, y - h + 4), (x - w * .6, y - h - 50 * k), (x + w * .6, y - h - 50 * k), (x + w - 4, y - h + 4)], 3.4, "#7c818a",
                  taper=.05, wmin=.9, seed=1243))
    if roller:
        # валик в банке: ручка торчит наискось
        a = math.radians(-62)
        b0 = (x - 8 * k, y - h + 6 * k)
        b1 = (b0[0] + 96 * k * math.cos(a), b0[1] + 96 * k * math.sin(a))
        o.insert(1, line([b0, b1], 12 * k, "#5d636c", taper=.05, wmin=.9, seed=1245))
        hx = b1
        o.insert(2, shape([(hx[0] - 9 * k, hx[1] + 6 * k, 1), (hx[0] + 13 * k, hx[1] - 4 * k, 1), (hx[0] + 44 * k, hx[1] - 66 * k, 1),
                           (hx[0] + 24 * k, hx[1] - 76 * k, 1)], "#3f7ec4", "", w=3.4, seed=1246))
    return "".join(o)


def work_lamp(x, y, t, k=1.0, on=True):
    """Лампа-переноска на крючке: оранжевый шнур, решётка-клетка, тёплая лампочка."""
    o = []
    sw = 2.5 * math.sin(t * 1.3)
    o.append(shape(ellipse_pts(x, y - 220 * k, 10 * k, 10 * k, 10), "#9aa0a8", "", w=3, seed=1250))
    cx, cy = x + sw, y
    o.append(line([(x, y - 214 * k), (x + 30 * k + sw * .5, y - 120 * k), (cx, cy - 52 * k)], 6 * k, "#f08a24", taper=.05, wmin=.9, seed=1251))
    if on:
        g = lib.rad_grad([(0, "#fff1b8", .9), (.4, "#ffd27a", .4), (1, "#ffd27a", 0)], cx, cy, 160 * k, 160 * k)
        o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(160 * k)}" fill="url(#{g})"/>')
    o.append(shape(ellipse_pts(cx, cy, 28 * k, 34 * k, 16), "#fff4c4" if on else "#e9e2cc", blob(ellipse_pts(cx - 8 * k, cy - 10 * k, 8 * k, 12 * k, 10), "#ffffff"),
                   w=3.2, seed=1252))
    for j in (-1, 0, 1):
        o.append(line([(cx + j * 22 * k, cy - 40 * k), (cx + j * 32 * k, cy), (cx + j * 20 * k, cy + 40 * k)], 3.4 * k, "#4b4f57", taper=.05, wmin=.9,
                      seed=1253 + j))
    o.append(line([(cx - 30 * k, cy - 6 * k), (cx + 30 * k, cy - 6 * k)], 3.2 * k, "#4b4f57", taper=.05, wmin=.9, seed=1257))
    o.append(shape(rect_pts(cx - 16 * k, cy - 66 * k, cx + 16 * k, cy - 40 * k, 4), "#2f3238", "", w=3, seed=1258))
    return "".join(o)


def plant(x, y, k=1.0, t=0.0):
    """Горшок с растением на подоконнике (s16–s18), (x, y) — низ-центр."""
    o = [blob(ellipse_pts(x + 6 * k, y, 60 * k, 7 * k, 12), "#000000", .2, lib.blur(3))]
    leaves = []
    for j in range(7):
        a = -math.pi / 2 + (j - 3) * 0.36 + 0.04 * math.sin(t * 1.6 + j)
        L = (120 + 26 * ((j * 5) % 3)) * k
        base = (x + (j - 3) * 4 * k, y - 84 * k)
        tip = (base[0] + L * math.cos(a), base[1] + L * math.sin(a))
        mid = ((base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2)
        n = (-math.sin(a), math.cos(a))
        wd = 22 * k
        pts = [base, (mid[0] + n[0] * wd, mid[1] + n[1] * wd), tip, (mid[0] - n[0] * wd, mid[1] - n[1] * wd)]
        sh = [base, (mid[0] - n[0] * wd, mid[1] - n[1] * wd), tip, mid]
        leaves.append(shape(pts, "#6fae5c", blob(sh, "#4f8c43", .9) + line([base, tip], 2.2, "#3f7436", taper=.6, seed=1270 + j, op=.8),
                            w=3.2, seed=1260 + j))
    o += leaves
    pot = [(x - 52 * k, y - 92 * k, 1), (x + 52 * k, y - 92 * k, 1), (x + 40 * k, y, 1), (x - 40 * k, y, 1)]
    o.append(shape(pot, "#d0714a", blob([(x + 16 * k, y - 92 * k), (x + 52 * k, y - 92 * k), (x + 40 * k, y), (x + 12 * k, y)], "#a95533", .9), w=3.8,
                   seed=1280))
    o.append(shape(rect_pts(x - 58 * k, y - 104 * k, x + 58 * k, y - 84 * k, 4), "#dc8058", blob(rect_pts(x + 20 * k, y - 104 * k, x + 58 * k, y - 84 * k), "#b45f3b", .9),
                   w=3.6, seed=1281))
    return "".join(o)


LIST_X0, LIST_X1, LIST_Y0 = 36.0, 322.0, 300.0       # лист слева от окна
LIST_GAP = 70.0


def list_line_y(i):
    return LIST_Y0 + 80 + i * LIST_GAP


def todo_list(t, strike_t=None, extra=3):
    """Лист на стене: белый, скотч сверху, строки маркером, зачёркнуты красным; ниже — ещё строки и свиток до пола.
    strike_t — время, когда дорисовывается последнее зачёркивание (None — все уже зачёркнуты)."""
    o = []
    x0, x1, y0 = LIST_X0, LIST_X1, LIST_Y0
    yb = FLOOR + 10
    # тень и сам лист-свиток до пола, внизу загибается на пол
    o.append(blob([(x0 + 10, y0 + 10), (x1 + 12, y0 + 10), (x1 + 16, yb), (x0 + 12, yb)], "#000000", .14, lib.blur(8)))
    rs = np.random.RandomState(77)
    ys = np.linspace(y0, yb - 40, 30)
    right = [(x1 + 3 * math.sin(y / 70) + rs.uniform(-1, 1), y) for y in ys]
    left = [(x0 + 3 * math.sin(y / 63 + 1) + rs.uniform(-1, 1), y) for y in ys]
    curl = [(x1 + 6, yb - 10, 1), (x1 + 30, yb + 34, 1), (x0 - 20, yb + 36, 1), (x0 - 4, yb - 10, 1)]
    paper = [(x0, y0, 1), (x1, y0, 1)] + right[1:] + curl + left[::-1][:-1]
    inner = blob([(x1 - 26, y0), (x1 + 10, y0), (x1 + 10, yb + 40), (x1 - 26, yb + 40)], "#e8e4da", .9)
    inner += blob([(x0 - 30, yb - 6), (x1 + 40, yb - 6), (x1 + 40, yb + 60), (x0 - 30, yb + 60)], "#dedad0", .9)
    for k in range(1, 7):                               # лёгкие сгибы свитка
        yk = y0 + 560 + k * 120
        inner += line([(x0 + 4, yk), (x1 - 4, yk + 3)], 2.2, "#d9d4c8", taper=.2, seed=1300 + k, op=.8)
    # строки
    fs = 36
    for i, txt in enumerate(LIST_LINES + LIST_MORE[:extra]):
        yl = list_line_y(i)
        rot = (-1.6 + 1.1 * math.sin(i * 2.3))
        inner += (f'<text x="{f(x0 + 18)}" y="{f(yl)}" font-family="Caveat" font-weight="700" font-size="{fs}" fill="#1b1a22" '
                  f'transform="rotate({f(rot)} {f(x0 + 18)} {f(yl)})">{txt}</text>')
    o.append(shape(paper, "#fbfaf5", inner, w=3.6, seed=1290))
    # зачёркивания красным (последняя строка — strike_t)
    n = len(LIST_LINES) + extra
    for i in range(n):
        yl = list_line_y(i) - 11
        prog = 1.0
        if strike_t is not None and i == n - 1:
            prog = lib.clamp((t - strike_t) / 0.22)
        if prog <= 0.01:
            continue
        r = np.random.RandomState(400 + i)
        xa, xb = x0 + 10, x1 - 14 - r.uniform(0, 26)
        pts = [(xa + (xb - xa) * u, yl + 4 * math.sin(u * 3 + i) + r.uniform(-1.5, 1.5)) for u in np.linspace(0, prog, 10)]
        o.append(line(pts, 6.4, "#e0362c", taper=.15, wmin=.5, seed=1340 + i))
    # скотч
    for k, (cx, ang) in enumerate(((x0 + 30, -14), (x1 - 30, 12))):
        o.append(f'<g transform="rotate({ang} {f(cx)} {f(y0)})">' +
                 shape(rect_pts(cx - 40, y0 - 14, cx + 40, y0 + 14), "#e8dca8", "", w=2.6, seed=1360 + k, attrs='opacity=".92"') + "</g>")
    return "".join(o)


def floor_(state):
    col = "#b8865a"
    inner = "".join(line([(-1600, FLOOR + 40 + k * 70 + k * k * 6), (2800, FLOOR + 40 + k * 70 + k * k * 6)], 3, mix(col, "#000000", .25),
                         taper=.05, wmin=.9, seed=1400 + k, op=.8) for k in range(8))
    o = shape(rect_pts(-1600, FLOOR, 2800, 3200), col, inner, w=4.4, seed=1401)
    if state == "reno":   # газеты на полу
        for k, (x, r) in enumerate(((300, -4), (760, 6), (1150, -2))):
            p = [(x - 200, FLOOR + 30, 1), (x + 200, FLOOR + 20, 1), (x + 220, FLOOR + 150, 1), (x - 190, FLOOR + 160, 1)]
            inn = "".join(line([(x - 170, FLOOR + 50 + j * 18), (x + 170, FLOOR + 44 + j * 18)], 3, "#b8b3a6", taper=.1, seed=1410 + k * 9 + j)
                          for j in range(6))
            o += shape(p, "#e9e5da", inn, w=3.2, seed=1405 + k)
    return o


def glow(cx=760.0, cy=520.0):
    """Тёплый свет лампы-переноски + тёмные углы (вечер)."""
    g = lib.rad_grad([(0, "#ffd890", .42), (.45, "#ffbe6a", .15), (1, "#ffbe6a", 0)], cx, cy, 1100, 1000)
    g2 = lib.rad_grad([(0, "#000000", 0), (.5, "#000000", 0), (1, "#1a1030", .5)], cx, cy + 300, 1400, 1400)
    return (f'<rect x="-1600" y="-1600" width="4400" height="4800" fill="url(#{g})" style="mix-blend-mode:screen"/>'
            f'<rect x="-1600" y="-1600" width="4400" height="4800" fill="url(#{g2})"/>')


def vignette():
    g = lib.rad_grad([(0, "#2a1408", 0), (.62, "#2a1408", 0), (1, "#2a1408", .4)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def room_bg(t, state):
    """Статичный фон комнаты (кэшируется сценой): стена, окно, батарея, подоконник, пол."""
    return wall(state) + window(t, state) + radiator(state) + floor_(state) + sill(state)


def compose(world_svg, cam, front="", lamp_xy=(1120.0, 330.0)):
    cx, cy, s, r = cam
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62
    o = ['<rect width="1080" height="1920" fill="#2a2440"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world_svg}{glow(*lamp_xy)}{front}</g>', vignette()]
    return lib.svg("".join(o))
