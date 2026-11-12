"""Карточки-превью на экране ТВ: цветные абстрактные картинки без единой буквы. Рисунок в базовых координатах
224×140; art(kind, pal, t) -> SVG-строка (используется в <g transform> с обрезкой по карточке)."""
import math

import numpy as np

from lib import blob, ellipse_pts, f, lin_grad, rad_grad, uid, DEFS  # noqa: F401

CW, CH = 224, 140

PALS = [
    ("#ff9a5a", "#ffd27a", "#5a3b7a", "#2c2150"),   # закат
    ("#7fd3ff", "#d8f3ff", "#2f6f8f", "#174257"),   # день-море
    ("#ff6f91", "#ffc2a8", "#6a2c70", "#2e1440"),   # розовый
    ("#9be15d", "#e9ffb8", "#2f7d4a", "#164a2a"),   # зелень
    ("#ffd25a", "#fff1b8", "#c0571f", "#6b2a12"),   # пустыня
    ("#6a7dff", "#b8c4ff", "#2a2f7a", "#141844"),   # ночь-синий
    ("#ff5a5a", "#ffb0a0", "#7a1f2a", "#3d0d14"),   # красный
    ("#3fd6c0", "#c0fff4", "#1f6f80", "#0f3842"),   # бирюза
]
KINDS = ["mountains", "face", "car", "sea", "city", "space", "forest", "dunes", "balloon", "duo", "road", "lighthouse"]


def _sky(a, b, key):
    g = lin_grad([(0, b, 1), (1, a, 1)], 0, 0, 0, 1, gid=f"sky_{key}") if not any(f'id="sky_{key}"' in d for d in DEFS) else f"sky_{key}"
    return f'<rect x="-2" y="-2" width="{CW + 4}" height="{CH + 4}" fill="url(#{g})"/>'


def _poly(pts, c, op=1.0):
    o = f' opacity="{op}"' if op != 1 else ""
    return '<path d="M' + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + f'Z" fill="{c}"{o}/>'


def mountains(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key), f'<circle cx="150" cy="58" r="22" fill="{b}"/>']
    s.append(_poly([(-2, 120), (40, 62), (70, 88), (112, 40), (150, 84), (180, 66), (226, 104), (226, 142), (-2, 142)], c))
    s.append(_poly([(112, 40), (100, 54), (110, 52), (118, 58), (124, 50)], "#ffffff", .85))
    s.append(_poly([(-2, 128), (52, 96), (96, 118), (150, 100), (226, 124), (226, 142), (-2, 142)], d))
    return "".join(s)


def face(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key), f'<circle cx="112" cy="70" r="58" fill="{b}" opacity=".55"/>']
    s.append(blob([(60, 142), (66, 112), (88, 98), (136, 98), (158, 112), (164, 142)], d))
    s.append(blob(ellipse_pts(112, 66, 30, 36, 14), c))
    s.append(blob([(80, 62), (84, 30), (112, 22), (142, 32), (146, 62), (136, 46), (112, 40), (88, 46)], d))
    return "".join(s)


def car(p, t, key, drive=0.0):
    a, b, c, d = p
    s = [_sky(a, b, key), f'<circle cx="60" cy="74" r="26" fill="{b}"/>']
    s.append(_poly([(-2, 96), (60, 80), (120, 92), (180, 76), (226, 88), (226, 142), (-2, 142)], c))
    s.append(_poly([(-2, 110), (226, 104), (226, 142), (-2, 142)], d))
    s.append(_poly([(-2, 119), (226, 115), (226, 117), (-2, 121)], b, .7))
    x = 120 + drive
    s.append(f'<g transform="translate({f(x)} 0)">')
    s.append(blob([(-34, 112, 1), (-34, 102), (-26, 98), (-16, 88), (8, 88), (18, 98), (32, 100), (34, 112, 1)], "#1a1220"))
    s.append(f'<circle cx="-20" cy="113" r="7" fill="#1a1220"/><circle cx="20" cy="113" r="7" fill="#1a1220"/>')
    s.append(f'<path d="M-12 91L4 91L10 98L-18 98Z" fill="{b}" opacity=".8"/>')
    s.append(f'<circle cx="33" cy="104" r="2.6" fill="#fff5c0"/></g>')
    return "".join(s)


def sea(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key), f'<circle cx="160" cy="40" r="16" fill="#fffbe8"/>']
    for i, y in enumerate([84, 98, 114, 128]):
        col = [c, d, c, d][i]
        pts = [(-2, 142)] + [(x, y + 4 * math.sin(x / 18 + i * 1.3 + t * 2)) for x in range(-2, 230, 12)] + [(226, 142)]
        s.append(_poly(pts, col))
    s.append(_poly([(150, 84), (170, 84), (166, 130), (154, 130)], "#fffbe8", .25))
    return "".join(s)


def city(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key)]
    rs = np.random.RandomState(4)
    x = -2
    while x < 226:
        w = rs.randint(18, 34)
        h = rs.randint(36, 96)
        s.append(f'<rect x="{x}" y="{142 - h}" width="{w}" height="{h + 2}" fill="{c if rs.rand() < .5 else d}"/>')
        for wy in range(142 - h + 8, 136, 12):
            for wx in range(x + 4, x + w - 5, 8):
                if rs.rand() < .45:
                    s.append(f'<rect x="{wx}" y="{wy}" width="4" height="5" fill="{b}"/>')
        x += w + rs.randint(1, 5)
    return "".join(s)


def space(p, t, key):
    a, b, c, d = p
    s = [f'<rect x="-2" y="-2" width="228" height="144" fill="{d}"/>']
    rs = np.random.RandomState(7)
    for _ in range(26):
        s.append(f'<circle cx="{rs.uniform(0, 224):.1f}" cy="{rs.uniform(0, 140):.1f}" r="{rs.uniform(.8, 1.8):.1f}" fill="#ffffff"/>')
    s.append(f'<circle cx="112" cy="74" r="38" fill="{a}"/>')
    s.append(f'<path d="M80 60 A38 38 0 0 1 150 70 A40 30 0 0 0 80 60Z" fill="{b}" opacity=".6"/>')
    s.append(f'<ellipse cx="112" cy="76" rx="70" ry="14" fill="none" stroke="{b}" stroke-width="5" transform="rotate(-12 112 76)"/>')
    s.append(f'<path d="M74 66 A38 38 0 0 0 150 82" fill="none" stroke="{a}" stroke-width="6" transform="rotate(-12 112 76)"/>')
    return "".join(s)


def forest(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key)]
    for row, (y0, col, sc) in enumerate([(110, c, 1.0), (134, d, 1.25)]):
        for i in range(-1, 9):
            x = i * 30 + row * 14
            h = 50 * sc + (i % 3) * 8
            s.append(_poly([(x - 16 * sc, y0), (x, y0 - h), (x + 16 * sc, y0)], col))
        s.append(f'<rect x="-2" y="{y0 - 1}" width="228" height="{144 - y0}" fill="{col}"/>')
    return "".join(s)


def dunes(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key), f'<circle cx="168" cy="44" r="20" fill="#fff8e0"/>']
    s.append(blob([(-10, 150), (-10, 96), (60, 80), (130, 102), (234, 86), (234, 150)], c))
    s.append(blob([(-10, 150), (-10, 124), (80, 104), (160, 126), (234, 112), (234, 150)], d))
    s.append(_poly([(50, 94), (54, 64), (60, 64), (62, 94)], "#2f6a3a"))
    s.append(_poly([(54, 80), (44, 80), (44, 70), (48, 70), (48, 76), (54, 76)], "#2f6a3a"))
    return "".join(s)


def balloon(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key)]
    s.append(blob(ellipse_pts(70, 120, 60, 12, 12), "#ffffff", .5))
    s.append(blob(ellipse_pts(170, 30, 40, 9, 12), "#ffffff", .5))
    y = 58 + 3 * math.sin(t * 2)
    s.append(blob([(112, y - 34), (138, y - 22), (140, y + 2), (122, y + 26), (102, y + 26), (84, y + 2), (86, y - 22)], c))
    s.append(blob([(112, y - 34), (122, y - 22), (122, y + 26), (102, y + 26), (102, y - 22)], d))
    s.append(f'<rect x="104" y="{f(y + 34)}" width="16" height="10" fill="#5a3a22"/>')
    s.append(f'<path d="M104 {f(y + 26)}L105 {f(y + 34)}M120 {f(y + 26)}L119 {f(y + 34)}" stroke="#3a2416" stroke-width="1.5"/>')
    return "".join(s)


def duo(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key)]
    s.append(blob(ellipse_pts(82, 66, 26, 30, 12), d) + blob([(42, 142), (48, 110), (82, 98), (116, 110), (122, 142)], d))
    s.append(blob(ellipse_pts(146, 72, 24, 28, 12), c) + blob([(108, 142), (114, 116), (146, 104), (178, 116), (184, 142)], c))
    s.append(blob([(110, 36), (118, 28), (126, 36), (118, 46)], "#ffffff", .9))
    return "".join(s)


def road(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key)]
    s.append(_poly([(-2, 72), (226, 72), (226, 142), (-2, 142)], c))
    s.append(_poly([(100, 72), (124, 72), (200, 142), (24, 142)], d))
    for k in range(4):
        u = ((k + t * 1.5) % 4) / 4
        y0, y1 = 72 + 70 * u ** 1.6, 72 + 70 * min(1, (u + .12)) ** 1.6
        w0, w1 = 1 + 6 * u, 1 + 6 * min(1, u + .12)
        s.append(_poly([(112 - w0, y0), (112 + w0, y0), (112 + w1, y1), (112 - w1, y1)], b))
    s.append(f'<circle cx="112" cy="58" r="14" fill="{b}"/>')
    return "".join(s)


def lighthouse(p, t, key):
    a, b, c, d = p
    s = [_sky(a, b, key)]
    s.append(_poly([(-2, 116), (226, 112), (226, 142), (-2, 142)], d))
    s.append(_poly([(130, 116), (136, 40), (152, 40), (158, 116)], "#f4f0e8"))
    for y in (56, 80, 104):
        s.append(_poly([(134.5, y), (153.5, y), (154.3, y + 10), (133.7, y + 10)], "#d94a3a"))
    s.append(_poly([(132, 40), (156, 40), (150, 28), (138, 28)], "#3a2e40"))
    s.append(_poly([(144, 34), (40, 10), (40, 48)], b, .55))
    s.append(_poly([(122, 120), (190, 118), (200, 128), (110, 130)], c))
    return "".join(s)


FUN = dict(mountains=mountains, face=face, car=car, sea=sea, city=city, space=space, forest=forest, dunes=dunes,
           balloon=balloon, duo=duo, road=road, lighthouse=lighthouse)


def card_spec(idx):
    """Карточка по номеру (детерминированно): вид и палитра; соседние не повторяются."""
    k = KINDS[(idx * 5 + 3) % len(KINDS)]
    p = PALS[(idx * 3 + 1) % len(PALS)]
    return k, p


def art(kind, pal, t=0.0, key="", **kw):
    return FUN[kind](pal, t, key or kind + pal[0][1:], **kw)


def card(x, y, w, h, kind, pal, t=0.0, r=10, key="", rot=0.0, scale=1.0, bar=None, **kw):
    """Карточка с обрезкой; рисунок вписан «с запасом» (uniform scale, по центру)."""
    from lib import DEFS as D
    cid = uid("cc")
    D.append(f'<clipPath id="{cid}"><rect x="0" y="0" width="{f(w)}" height="{f(h)}" rx="{f(r)}"/></clipPath>')
    k = max(w / CW, h / CH)
    ox, oy = (w - CW * k) / 2, (h - CH * k) / 2
    cx, cy = w / 2, h / 2
    tf = f"translate({f(x + cx)} {f(y + cy)}) rotate({f(rot)}) scale({scale:.4f}) translate({f(-cx)} {f(-cy)})"
    s = [f'<g transform="{tf}">', f'<rect x="-1" y="2" width="{f(w + 2)}" height="{f(h + 2)}" rx="{f(r)}" fill="#05070f" opacity=".55"/>',
         f'<g clip-path="url(#{cid})"><g transform="translate({f(ox)} {f(oy)}) scale({k:.5f})">{art(kind, pal, t, key, **kw)}</g>']
    if bar is not None:
        s.append(f'<rect x="0" y="{f(h - 5)}" width="{f(w)}" height="5" fill="#000" opacity=".45"/>'
                 f'<rect x="0" y="{f(h - 5)}" width="{f(w * bar)}" height="5" fill="#e8413a"/>')
    s.append("</g></g>")
    return "".join(s)
