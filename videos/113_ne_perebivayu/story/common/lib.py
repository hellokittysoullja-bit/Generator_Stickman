"""Общие помощники сцены cafe рилса 27 (из run рилса 26; добавлен INK_K — толщина туши от масштаба камеры).
Исходно: помощники сцен tv / plate / jam рилса 23 (тот же способ, что герои 22-го: живая линия с нажимом — ink.py,
cel-тени, свет слоями). Сцена — функция frame(t) -> строка SVG 1080×1920; статика строится один раз и кэшируется
(defs статики остаются, динамические defs сбрасываются на каждый кадр — dyn_begin())."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from ink import band, ellipse_pts, fill_d, ink_closed, ink_open, sample  # noqa: E402,F401

W, H = 1080, 1920
INK = "#1c1622"
DEFS = []
_uid = [0]
_mark = [0, 0]
INK_K = [1.0]           # множитель толщины туши (крупный план — тоньше в мире, чтобы на экране не толстела)


def static_done():
    _mark[0], _mark[1] = len(DEFS), _uid[0]


def dyn_begin():
    del DEFS[_mark[0]:]
    _uid[0] = max(_mark[1], 100000)


def uid(p="c"):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def shape(pts, fill, inner="", w=5.0, seed=0, ink=True, attrs="", var=0.28, weight=0.45, ink_color=INK, id=None):
    d = fill_d(pts)
    gid = f' id="{id}"' if id else ""
    out = [f"<g{gid} {attrs}>", f'<path d="{d}" fill="{fill}"/>']
    if inner:
        c = uid()
        DEFS.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
        out.append(f'<g clip-path="url(#{c})">{inner}</g>')
    if ink:
        out.append(f'<path d="{ink_closed(pts, w * INK_K[0], var=var, weight=weight, seed=abs(int(seed)) % 2**31)}" fill="{ink_color}"/>')
    out.append("</g>")
    return "".join(out)


def clip_of(pts):
    c = uid()
    DEFS.append(f'<clipPath id="{c}"><path d="{fill_d(pts)}"/></clipPath>')
    return c


def clip_rect(x, y, w, h, r=0):
    c = uid()
    DEFS.append(f'<clipPath id="{c}"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(r)}"/></clipPath>')
    return c


def line(pts, w=4.0, color=INK, taper=0.6, wmin=0.12, seed=3, peak=0.5, op=1.0, extra=""):
    d = ink_open(pts, w * INK_K[0], taper=taper, wmin=wmin, seed=abs(int(seed)) % 2**31, peak=peak)
    if not d:
        return ""
    o = f' opacity="{op:.3f}"' if op != 1 else ""
    return f'<path d="{d}" fill="{color}"{o} {extra}/>'


def blob(pts, color, op=1.0, extra=""):
    o = f' opacity="{op:.3f}"' if op != 1 else ""
    return f'<path d="{fill_d(pts)}" fill="{color}"{o} {extra}/>'


def rect_pts(x0, y0, x1, y1, r=0):
    if r <= 0:
        return [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]
    k = r * 0.3
    return [(x0 + r, y0), (x1 - r, y0), (x1 - k, y0 + k), (x1, y0 + r), (x1, y1 - r), (x1 - k, y1 - k), (x1 - r, y1),
            (x0 + r, y1), (x0 + k, y1 - k), (x0, y1 - r), (x0, y0 + r), (x0 + k, y0 + k)]


def blur(sd):
    i = f"bl{sd}".replace(".", "_")
    if not any(f'id="{i}"' in x for x in DEFS):
        DEFS.append(f'<filter id="{i}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return f'filter="url(#{i})"'


def T(pts, dx, dy, s=1.0, rot=0.0, cx=0.0, cy=0.0):
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for p in pts:
        x, y = (p[0] - cx) * s, (p[1] - cy) * s
        q = (cx + x * c - y * sn + dx, cy + x * sn + y * c + dy)
        out.append(q + ((1,) if len(p) > 2 and p[2] else ()))
    return out


def lin_grad(stops, x1=0, y1=0, x2=0, y2=1, units="objectBoundingBox", gid=None):
    g = gid or uid("g")
    st = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a != 1 else "") + "/>" for o, c, a in stops)
    DEFS.append(f'<linearGradient id="{g}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" gradientUnits="{units}">{st}</linearGradient>')
    return g


def rad_grad(stops, cx, cy, rx, ry=None, gid=None, rot=0):
    g = gid or uid("g")
    ry = rx if ry is None else ry
    st = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a != 1 else "") + "/>" for o, c, a in stops)
    DEFS.append(f'<radialGradient id="{g}" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" '
                f'gradientTransform="translate({f(cx)} {f(cy)}) rotate({rot}) scale({f(rx)} {f(ry)})">{st}</radialGradient>')
    return g


def mix(a, b, u):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * u) for x, y in zip(a, b))


def mul(h, k):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(min(255, round(v * kk)) for v, kk in zip((r, g, b), k))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(e0, e1, x):
    u = clamp((x - e0) / (e1 - e0))
    return u * u * (3 - 2 * u)


def ease_out(u, p=3):
    u = clamp(u)
    return 1 - (1 - u) ** p


def ease_in(u, p=2):
    return clamp(u) ** p


def ease_io(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def back_out(u, s=1.7):
    u = clamp(u) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def spring(u, freq=3.0, damp=5.0):
    """0→1 с перелётом и затуханием (u — секунды)."""
    if u <= 0:
        return 0.0
    return 1 - math.exp(-damp * u) * math.cos(2 * math.pi * freq * u)


def cam(cx, cy, s, rot=0.0):
    """Камера: точка (cx, cy) мира — в центр кадра, масштаб s."""
    return f"translate(540 960) rotate({f(rot)}) scale({s:.5f}) translate({-cx:.3f} {-cy:.3f})"


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{"".join(DEFS)}</defs>{body}</svg>')


def words():
    import json
    return json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def rrect(x0, y0, x1, y1, r=0, n=7):
    """Скруглённый прямоугольник плотными точками дуг (без «рогов» у углов)."""
    if r <= 0:
        return [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]
    r = min(r, (x1 - x0) / 2 - .5, (y1 - y0) / 2 - .5)
    out = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)) + ((1,) if k in (0, n) else ()))
    return out
