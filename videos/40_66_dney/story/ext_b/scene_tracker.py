"""Сцена tracker рилса 40 (s11, 18.4–20.9; клип 18.2–21.1): крупно стол, три листка-трекера (сетка 7 дней × 12 недель,
без букв: шапка — цветная полоса и кружок, недели — серые точки). Три руки разного цвета кожи (рука с ручкой из
hand.py рилсов 24–26, свои рукава) ставят зелёные галочки. До «каждый» (19.28) — первая строка по клетке, с «каждый
день» — ряд за рядом, ручка проходит строку и возвращается к началу следующей; к 20.75 сетка 12 недель заполнена.
В правом листе одна клетка (неделя 6) так и остаётся пустой — пропуск, ряд идёт дальше."""
import math

import hand
import lib
from lib import DEFS, INK, W, H, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, rad_grad, rect_pts, shape, smooth, svg

_ST = {}
SW, SHh = 470, 700                # лист
GX0, GY0 = 78, 150                # сетка внутри листа
CW, CH = 52, 42                   # клетка
COLS, ROWS = 7, 12
T_EVERY = 19.28

# листы: (x, y, поворот°, цвет шапки, рука: кожа, тень кожи, рукав, тень рукава, складка, зеркально, сдвиг по времени)
SHEETS = [
    dict(x=40, y=90, rot=-4.0, head="#e0763a", skin=("#8a5a3c", "#6e4630", "#5c3a26"), sleeve=("#2f8a5a", "#226a44", "#1a5636", "#123f28"),
         mirror=True, dt=0.0, miss=None),
    dict(x=575, y=150, rot=3.5, head="#3a7ad0", skin=("#f0c4a0", "#d39f83", "#bf8a74"), sleeve=("#d9467a", "#b0345f", "#8f284c", "#6e1e3a"),
         mirror=False, dt=0.06, miss=(5, 3)),
    dict(x=300, y=880, rot=-1.5, head="#e0b64a", skin=("#c98e6a", "#a87556", "#8f6048"), sleeve=("#6c7486", "#545b6b", "#434957", "#343944"),
         mirror=False, dt=0.11, miss=None),
]
HSC = 0.7


def tracker(sd, head):
    inner = ""
    inner += shape(ellipse_pts(48, 52, 24, 24, 14), head, line([(36, 52), (46, 62), (62, 42)], 5, "#ffffff", seed=sd + 1), w=3, seed=sd + 2)
    inner += f'<rect x="86" y="38" width="250" height="22" rx="7" fill="{head}"/>'
    inner += f'<rect x="86" y="70" width="170" height="12" rx="5" fill="#aab0bc"/>'
    # дни — кружки над столбцами (без букв)
    for c in range(COLS):
        cx = GX0 + c * CW + CW / 2
        inner += f'<circle cx="{f(cx)}" cy="{GY0 - 18}" r="{6 if c < 5 else 8}" fill="{"#aab0bc" if c < 5 else head}"/>'
    # недели — серые точки слева
    for r in range(ROWS):
        cy = GY0 + r * CH + CH / 2
        inner += f'<rect x="30" y="{f(cy - 5)}" width="{30 if r % 4 == 3 else 22}" height="10" rx="4" fill="#c3c8d1"/>'
    # сетка
    for r in range(ROWS + 1):
        y = GY0 + r * CH
        inner += f'<rect x="{GX0}" y="{f(y - 1.2)}" width="{COLS * CW}" height="2.4" fill="#8d95a6"/>'
    for c in range(COLS + 1):
        x = GX0 + c * CW
        inner += f'<rect x="{f(x - 1.2)}" y="{GY0}" width="2.4" height="{ROWS * CH}" fill="#8d95a6"/>'
    inner += line([(GX0, GY0 + ROWS * CH + 40), (GX0 + 200, GY0 + ROWS * CH + 40)], 3, "#8d95a6", taper=.05, wmin=.9, seed=sd + 5)
    return shape([(0, 0, 1), (SW, 0, 1), (SW, SHh, 1), (0, SHh, 1)], "#fbf9f2", inner, w=4.2, seed=sd + 9)


def table():
    s = []
    DEFS.append('<pattern id="pWood40" width="420" height="140" patternUnits="userSpaceOnUse">'
                '<rect width="420" height="140" fill="#b88a5c"/>'
                '<path d="M0 30 C120 22 260 40 420 28 M0 78 C140 86 280 66 420 82 M0 118 C110 110 300 126 420 114" fill="none" stroke="#a2764a" stroke-width="3"/>'
                '<rect y="138" width="420" height="2" fill="#8a6038"/></pattern>')
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#pWood40)"/>')
    g = rad_grad([(0, "#fff0c8", .5), (.6, "#ffe0a0", .15), (1, "#ffe0a0", 0)], 420, 500, 1100, 1100)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    for k, sh in enumerate(SHEETS):
        s.append(f'<g transform="translate({sh["x"] + 16} {sh["y"] + 22}) rotate({sh["rot"]})">'
                 f'{blob(rect_pts(0, 0, SW, SHh), "#3a2410", .35, blur(12))}</g>')
        s.append(f'<g transform="translate({sh["x"]} {sh["y"]}) rotate({sh["rot"]})">{tracker(800 + k * 40, sh["head"])}</g>')
    # кружка с чаем у края — обжитость
    s.append(blob(ellipse_pts(990, 930, 92, 92, 18), "#3a2410", .3, blur(9)))
    s.append(shape(ellipse_pts(975, 910, 84, 84, 20), "#e8e2d4", blob(ellipse_pts(975, 910, 64, 64, 18), "#8a5a34", .95) +
                   blob(ellipse_pts(952, 888, 22, 10, 10, rot=-30), "#c08a5a", .8), w=4.4, seed=990))
    return "".join(s)


# ───────────────────────── расписание галочек
def schedule(sh):
    """[(r, c, время)] — когда ручка ставит галочку в клетку; плюс отрезки хода ручки."""
    dt = sh["dt"]
    ev = []
    t = 18.52 + dt
    for c in range(COLS):            # первая неделя — по клетке
        ev.append((0, c, t))
        t += 0.105
    for r in range(1, ROWS):          # с «каждый день» — ряд за рядом
        t0 = T_EVERY + dt + (r - 1) * 0.135
        for c in range(COLS):
            ev.append((r, c, t0 + 0.095 * c / (COLS - 1)))
    if sh["miss"]:
        ev = [e for e in ev if (e[0], e[1]) != sh["miss"]]
    return ev


def cell_pt(sh, r, c, dx=0.0, dy=0.0):
    lx, ly = GX0 + c * CW + CW / 2 + dx, GY0 + r * CH + CH / 2 + dy
    a = math.radians(sh["rot"])
    return sh["x"] + lx * math.cos(a) - ly * math.sin(a), sh["y"] + lx * math.sin(a) + ly * math.cos(a)


TICK = [(-15, 0), (-5, 10), (16, -13)]     # галочка в клетке (лист)


def ticks(sh, t, ev):
    o = []
    for r, c, te in ev:
        if t < te:
            continue
        u = clamp((t - te) / 0.07)
        pts = [cell_pt(sh, r, c, *p) for p in TICK]
        L1 = math.dist(pts[0], pts[1])
        L2 = math.dist(pts[1], pts[2])
        L = L1 + L2
        d = f"M{f(pts[0][0])} {f(pts[0][1])}L{f(pts[1][0])} {f(pts[1][1])}L{f(pts[2][0])} {f(pts[2][1])}"
        o.append(f'<path d="{d}" fill="none" stroke="#1f7a46" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round" '
                 f'stroke-dasharray="{f(L)}" stroke-dashoffset="{f(L * (1 - u))}"/>')
    return "".join(o)


def pen_at(sh, t, ev):
    """Кончик ручки: подход из-за края до первой клетки, потом по событиям; между клетками — короткий перелёт с подъёмом,
    в конце — отход. Возвращает (x, y, подъём 1..1.08)."""
    first = ev[0]
    p0 = cell_pt(sh, first[0], first[1], *TICK[0])
    if t < first[2]:
        u = ease_out(clamp((t - 18.2) / (first[2] - 18.2)), 1.6)
        sx = p0[0] + (-80 if sh["mirror"] else 170)
        sy = p0[1] + 230
        return sx + (p0[0] - sx) * u, sy + (p0[1] - sy) * u - 40 * math.sin(math.pi * u), 1.0 + 0.08 * (1 - u)
    for i, (r, c, te) in enumerate(ev):
        nxt = ev[i + 1] if i + 1 < len(ev) else None
        if nxt is None or t < nxt[2]:
            # пишет галочку (0.07 с), потом летит к следующей
            u = clamp((t - te) / 0.07)
            if u < 1 or nxt is None:
                pts = [cell_pt(sh, r, c, *p) for p in TICK]
                if u < 0.4:
                    q = u / 0.4
                    x, y = pts[0][0] + (pts[1][0] - pts[0][0]) * q, pts[0][1] + (pts[1][1] - pts[0][1]) * q
                else:
                    q = (u - 0.4) / 0.6
                    x, y = pts[1][0] + (pts[2][0] - pts[1][0]) * q, pts[1][1] + (pts[2][1] - pts[1][1]) * q
                if nxt is None and t > te + 0.07:
                    e = ease_io(clamp((t - te - 0.15) / 0.5))
                    return x + (90 if not sh["mirror"] else -90) * e, y + 160 * e, 1.0 + 0.08 * e
                return x, y, 1.0
            a = cell_pt(sh, r, c, *TICK[2])
            b = cell_pt(sh, nxt[0], nxt[1], *TICK[0])
            q = ease_io(clamp((t - te - 0.07) / max(0.01, nxt[2] - te - 0.07)))
            hop = 0.06 if nxt[0] != r else 0.025
            return a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q, 1.0 + hop * math.sin(math.pi * q)
    return p0[0], p0[1], 1.0


def one_hand(sh, t, ev, k):
    x, y, lift = pen_at(sh, t, ev)
    hand.SKIN, hand.SKIN_SH, hand.SKIN_SH2 = sh["skin"]
    hand.HOOD, hand.HOOD_SH, hand.HOOD_SH2, hand.FOLD = sh["sleeve"]
    ang = -36 + 3 * math.sin(t * 2.3 + k) - 40 * (lift - 1)
    mx = -1 if sh["mirror"] else 1
    body = hand.hand(ang, 7 + k * 300, 0.0)
    sc = HSC * lift
    shadow = (f'<g transform="translate({f(x + 22 * lift)} {f(y + 28 * lift)}) scale({f(mx * HSC)} {f(HSC)})" opacity=".26" filter="url(#fShH40)">'
              f'{body}</g>')
    hnd = f'<g transform="translate({f(x)} {f(y)}) scale({f(mx * sc)} {f(sc)})">{body}</g>'
    return shadow, hnd


def s11(t):
    tk, sh_, hn = [], [], []
    for k, sh in enumerate(SHEETS):
        ev = _ST["ev"][k]
        tk.append(ticks(sh, t, ev))
        a, b = one_hand(sh, t, ev, k)
        sh_.append(a)
        hn.append(b)
    # нижний лист и его рука — первыми (верхние руки ложатся поверх)
    art = _ST["table"] + "".join(tk) + sh_[2] + hn[2] + sh_[0] + sh_[1] + hn[0] + hn[1]
    u = clamp((t - 18.2) / 2.9)
    cm = cam(545 + 10 * u, 760 + 30 * ease_io(u), 1.0 + 0.07 * (0.4 * u + 0.6 * ease_io(u)), -0.8 + 1.2 * u)
    return art, cm


def build_static():
    if _ST:
        return
    DEFS.append('<filter id="fShH40" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="8"/></filter>')
    _ST["table"] = table()
    _ST["ev"] = [schedule(sh) for sh in SHEETS]
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = s11(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#b88a5c"/><g transform="{cm}">{art}</g>')
