"""Мозг рилса 35 — мозг рилсов 24–32 (сбоку, объём, извилины, лобная доля влево), но разобранный на ДОЛИ:
лоб (front), темя (pariet), висок (temp), затылок (occip), мозжечок (cereb) и маленький «уголок» лба (tip).
Каждая доля — своя непрозрачная заливка: цвет = смесь серого «спит» и цвета «горит» по уровню 0..1; извилины
рисуются отдельно в каждой доле (клип по доле) своим тёмным тоном — на стыке цвета нет ни щелей, ни двойных линий.
Границы долей — борозды (те же точки сплайна идут и в заливку, и в тушь). Рисуется вокруг (BCX, BCY);
геометрия строится один раз (init), кадр только подставляет цвета."""
import math

import numpy as np

import lib
from ink import sample
from lib import blob, ellipse_pts, f, fill_d, ink_closed, line, mix

BCX, BCY = 400, 600
LOBES = ("front", "tip", "pariet", "temp", "occip", "cereb")
DULL = "#bdaab9"            # серая «спящая» доля
DULL_C = "#ab98a8"          # мозжечок серый (чуть темнее)
LIT = {"front": "#ffd36a", "tip": "#ffe27a", "pariet": "#8ee6b8", "temp": "#8cc8ff", "occip": "#c7a4ff", "cereb": "#ffb38a"}
PINK = {"front": "#f6a9bc", "tip": "#f6a9bc", "pariet": "#f6a9bc", "temp": "#f3a2b7", "occip": "#f0a0b5", "cereb": "#ef9bb0"}
_G = {}


def _curve(pts):
    return [tuple(p) for p in sample(pts, False, 3.0)]


def brain_outline():
    pts = []
    rs = np.random.RandomState(7)
    ph = rs.uniform(0, 6.28, 3)
    n = 44
    for i in range(n):
        a = 2 * math.pi * i / n
        rx, ry = 215, 150
        r = 1 + 0.035 * math.sin(9 * a + ph[0]) + 0.02 * math.sin(14 * a + ph[1])
        x = math.cos(a) * rx * r
        y = math.sin(a) * ry * r
        if y > 0:
            y *= 0.82
            x *= 1 - 0.08 * math.sin(a)
        if x < 0 and y < 0:
            x *= 1.04
        pts.append((BCX + x, BCY + y))
    return pts


CBL = [(BCX + 70, BCY + 100), (BCX + 150, BCY + 82), (BCX + 205, BCY + 110), (BCX + 200, BCY + 150), (BCX + 150, BCY + 170),
       (BCX + 90, BCY + 160), (BCX + 60, BCY + 130)]

# борозды-границы долей (локальные координаты)
SYLV = [(BCX - 230, BCY + 74), (BCX - 120, BCY + 60), (BCX - 40, BCY + 28), (BCX + 40, BCY + 22), (BCX + 110, BCY - 6), (BCX + 150, BCY + 6)]
CENT = [(BCX + 14, BCY - 200), (BCX + 10, BCY - 148), (BCX - 6, BCY - 90), (BCX + 14, BCY - 40), (BCX + 2, BCY + 10), (BCX + 6, BCY + 26)]
POCC = [(BCX + 128, BCY - 200), (BCX + 124, BCY - 130), (BCX + 140, BCY - 60), (BCX + 136, BCY - 6), (BCX + 150, BCY + 6),
        (BCX + 160, BCY + 60), (BCX + 176, BCY + 200)]
TIPB = [(BCX - 150, BCY - 200), (BCX - 162, BCY - 120), (BCX - 150, BCY - 60), (BCX - 172, BCY - 4), (BCX - 210, BCY + 40),
        (BCX - 260, BCY + 50)]


def _regions():
    sy, ce, po, tb = _curve(SYLV), _curve(CENT), _curve(POCC), _curve(TIPB)
    # точки пересечения кривых: ближайшие точки
    def near(a, b):
        A, B = np.array(a), np.array(b)
        d = np.linalg.norm(A[:, None] - B[None], axis=2)
        i, j = np.unravel_index(np.argmin(d), d.shape)
        return i, j
    i_sc, j_cs = near(sy, ce)        # сильвиева ∩ центральная
    i_sp, j_ps = near(sy, po)        # сильвиева ∩ теменно-затылочная
    i_st, j_ts = near(sy, tb)        # сильвиева ∩ граница уголка
    F = 400
    L, R, T, B = BCX - F, BCX + F, BCY - F, BCY + F
    rv = lambda seq: list(seq)[::-1]  # noqa: E731
    front = [(L, T), (ce[0][0], T)] + ce[:j_cs + 1] + rv(sy[:i_sc + 1]) + [(L, sy[0][1])]
    tip = [(L, T), (tb[0][0], T)] + tb[:j_ts + 1] + rv(sy[:i_st + 1]) + [(L, sy[0][1])]
    pariet = [(ce[0][0], T), (po[0][0], T)] + po[:j_ps + 1] + rv(sy[i_sc:i_sp + 1]) + rv(ce[:j_cs + 1])
    occip = [(po[0][0], T), (R, T), (R, B), (po[-1][0], B)] + rv(po)
    temp = [(L, sy[0][1])] + sy[:i_sp + 1] + po[j_ps:] + [(po[-1][0], B), (L, B)]
    return {"front": front, "tip": tip, "pariet": pariet, "temp": temp, "occip": occip}


def _gyri():
    """Извилины как в рилсах 24–32: (тень, свет) — пары путей, цвет подставляется."""
    rs = np.random.RandomState(12)
    out = []
    seeds = []
    for ring, (rx, ry, n) in enumerate([(178, 118, 9), (128, 82, 7), (76, 46, 4)]):
        a0 = rs.uniform(0, 6.28)
        for k in range(n):
            seeds.append((ring, rx, ry, a0 + 2 * math.pi * k / n + rs.uniform(-.15, .15)))
    for j, (ring, rx, ry, a) in enumerate(seeds):
        span = rs.uniform(0.38, 0.62) * (1.0 if ring < 2 else 1.3)
        amp = rs.uniform(7, 12)
        m = 18
        pts = []
        for i in range(m + 1):
            u = i / m
            aa = a + span * u
            w = amp * math.sin(u * math.pi * rs.uniform(2.2, 3.2) + j)
            rr = 1 + w / max(rx, 1)
            x, y = math.cos(aa) * rx * rr, math.sin(aa) * ry * rr
            if y > 0:
                y *= 0.85
            pts.append((BCX + x, BCY + y))
        ex, ey = pts[-1]
        ix, iy = BCX - ex, BCY - ey
        L = math.hypot(ix, iy) + 1e-6
        pts.append((ex + ix / L * 18 + rs.uniform(-6, 6), ey + iy / L * 18))
        out.append((line([(x + 1.5, y + 4) for x, y in pts], 4.0, "@HI@", seed=200 + j, op=.6, taper=.6),
                    line(pts, 5.4, "@GY@", seed=300 + j, taper=.7, wmin=.15)))
    hi = "".join(a for a, b in out)
    gy = "".join(b for a, b in out)
    return hi, gy


def init():
    """Геометрия и клипы — один раз до lib.static_done()."""
    if _G:
        return
    pts = brain_outline()
    _G["out_d"] = fill_d(pts)
    _G["out_ink"] = ink_closed(pts, 6.2, var=.28, weight=.45, seed=53)
    oc = lib.uid()
    lib.DEFS.append(f'<clipPath id="{oc}"><path d="{_G["out_d"]}"/></clipPath>')
    _G["oclip"] = oc
    _G["reg"] = {}
    for k, poly in _regions().items():
        c = lib.uid()
        d = fill_d([(x, y, 1) for x, y in poly])
        lib.DEFS.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
        _G["reg"][k] = (d, c)
    _G["hi"], _G["gy"] = _gyri()
    # мозжечок
    _G["cb_d"] = fill_d(CBL)
    _G["cb_ink"] = ink_closed(CBL, 4.6, var=.28, weight=.45, seed=52)
    cb = ""
    for k in range(4):
        y = BCY + 105 + k * 16
        cb += line([(BCX + 75 + k * 6, y), (BCX + 140, y - 6 + k * 2), (BCX + 198 - k * 4, y + 4 + k * 3)], 3.4, "@GY@", seed=60 + k)
    _G["cb_lines"] = cb
    c = lib.uid()
    lib.DEFS.append(f'<clipPath id="{c}"><path d="{_G["cb_d"]}"/></clipPath>')
    _G["cb_clip"] = c
    # борозды-границы — тушь поверх заливок
    _G["sulci"] = (line(SYLV[1:-1], 6.5, "@SU@", seed=401) + line(CENT[1:-1], 5.5, "@SU@", seed=402)
                   + line(POCC[1:-2], 5.0, "@SU@", seed=403) + line(TIPB[1:-1], 4.2, "@SU@", seed=404, taper=.8, wmin=.1))


def lobe_color(lobe, level, lit=None, pink=False, warm=0.0):
    """Цвет доли: серый → «горит» (level 0..1). pink=True — живой розовый мозг вместо серого."""
    base = (PINK if pink else {k: DULL for k in LOBES})[lobe]
    if lobe == "cereb" and not pink:
        base = DULL_C
    c = mix(base, (lit or LIT)[lobe], lib.clamp(level))
    if warm:
        c = mix(c, "#ffb08a", warm)
    return c


def dark(c, k=0.62):
    return lib.mul(c, (k, k * 0.92, k * 0.98))


def brain(levels, lit=None, pink=False, warm=0.0, glow=1.0, sulcus=None):
    """levels: {доля: 0..1}; доли без уровня — 0. Возвращает SVG мозга в локальных координатах."""
    init()
    lv = {k: levels.get(k, 0.0) for k in LOBES}
    cols = {k: lobe_color(k, lv[k], lit, pink, warm) for k in LOBES}
    s = []
    # мозжечок — сзади
    cc = cols["cereb"]
    cbi = (f'<path d="{_G["cb_d"]}" fill="{cc}"/>'
           + blob([(BCX + 90, BCY + 140), (BCX + 200, BCY + 130), (BCX + 200, BCY + 150), (BCX + 150, BCY + 170), (BCX + 90, BCY + 160)],
                  "#000000", .12)
           + _G["cb_lines"].replace("@GY@", dark(cc, .66)))
    s.append(f'<g clip-path="url(#{_G["cb_clip"]})">{cbi}</g><path d="{_G["cb_ink"]}" fill="{lib.INK}"/>')
    # полушарие: доли
    inner = [f'<path d="{_G["out_d"]}" fill="{cols["front"]}"/>']
    for k in ("front", "pariet", "temp", "occip", "tip"):
        d, c = _G["reg"][k]
        col = cols[k]
        inner.append(f'<g clip-path="url(#{c})"><path d="{d}" fill="{col}"/>')
        if lv[k] > 0.02 and glow:
            cx, cy = {"front": (BCX - 90, BCY - 60), "tip": (BCX - 200, BCY - 40), "pariet": (BCX + 70, BCY - 80),
                      "temp": (BCX - 20, BCY + 80), "occip": (BCX + 180, BCY - 10)}[k]
            g = lib.rad_grad([(0, "#ffffff", .55 * lv[k] * glow), (1, "#ffffff", 0)], cx, cy, 120, 90)
            inner.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="120" ry="90" fill="url(#{g})"/>')
        inner.append(_G["hi"].replace("@HI@", mix(col, "#ffffff", .45)).replace("@GY@", dark(col)) + "</g>")
    # объём: тень снизу, блик сверху — поверх долей одинаково
    inner.append(blob([(BCX - 240, BCY + 70), (BCX - 60, BCY + 120), (BCX + 120, BCY + 70), (BCX + 240, BCY - 10),
                       (BCX + 240, BCY + 200), (BCX - 240, BCY + 200)], "#2a1030", .16))
    inner.append(blob(ellipse_pts(BCX - 90, BCY - 85, 95, 42, 14, rot=-14), "#ffffff", .18))
    inner.append(blob(ellipse_pts(BCX - 120, BCY - 98, 34, 13, 10, rot=-22), "#ffffff", .55))
    su = sulcus or dark(mix(cols["front"], cols["temp"], .5), .5)
    inner.append(_G["sulci"].replace("@SU@", su))
    s.append(f'<g clip-path="url(#{_G["oclip"]})">{"".join(inner)}</g>')
    s.append(f'<path d="{_G["out_ink"]}" fill="{lib.INK}"/>')
    return "".join(s)


def halo(levels, lit=None, warm=0.0, k=1.0):
    """Свечение вокруг горящих долей (свет, не фигура) — под мозгом, в локальных координатах."""
    out = []
    for lobe, (cx, cy, r) in {"front": (BCX - 120, BCY - 50, 260), "tip": (BCX - 210, BCY - 40, 200), "pariet": (BCX + 60, BCY - 110, 250),
                              "temp": (BCX - 20, BCY + 90, 240), "occip": (BCX + 200, BCY - 10, 240), "cereb": (BCX + 150, BCY + 140, 200)}.items():
        v = levels.get(lobe, 0.0) * k
        if v < 0.03:
            continue
        col = mix((lit or LIT)[lobe], "#ffb08a", warm)
        g = lib.rad_grad([(0, col, .55 * v), (.5, col, .22 * v), (1, col, 0)], cx, cy, r, r)
        out.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="url(#{g})"/>')
    return "".join(out)


LOBE_CENTER = {"front": (BCX - 70, BCY - 70), "tip": (BCX - 196, BCY - 40), "pariet": (BCX + 70, BCY - 90), "temp": (BCX + 40, BCY + 70),
               "occip": (BCX + 182, BCY - 20), "cereb": (BCX + 150, BCY + 135)}
