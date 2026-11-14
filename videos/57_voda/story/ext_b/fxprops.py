"""Общие мелочи сцен рилса 57 группы B (из 56): place, shadow, burst, dust, glint."""
import math

import lib
from lib import INK, band, blob, ellipse_pts, f, line, rect_pts, shape

def place(g, x, y, rot=0.0, sx=1.0, sy=None, cx=0.0, cy=0.0):
    sy = sx if sy is None else sy
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sx:.4f} {sy:.4f}) translate({f(-cx)} {f(-cy)})">{g}</g>')


def shadow(x, y, rx, ry, op=0.35, sd=8):
    return lib.blob(ellipse_pts(x, y, rx, ry, 18), "#2a1608", op, lib.blur(sd))


# ═════════════════════════ свитер (плоско сверху) ═════════════════════════

def burst(cx, cy, k, n=10, r0=60, r1=170, w=10, color="#fff4c2", seed=0, a0=0.0, spread=360):
    """Лучи-штрихи удара: k 0→1 — лучи разлетаются и тают."""
    if not 0 < k < 1:
        return ""
    s = []
    for j in range(n):
        a = math.radians(a0 + spread * j / n + 7 * math.sin(j * 2.3))
        ra = r0 + (r1 - r0) * lib.ease_out(k, 2) * (0.8 + 0.2 * math.sin(j * 1.7))
        rb = ra + (r1 - r0) * 0.55 * (1 - k)
        s.append(line([(cx + ra * math.cos(a), cy + ra * math.sin(a)), (cx + rb * math.cos(a), cy + rb * math.sin(a))],
                      w * (1 - k) + 1.5, color, taper=.6, wmin=.2, seed=seed + j))
    return "".join(s)


def dust(cx, cy, k, n=6, spread=170, rise=70, seed=0, color="#fff6e0", rmax=34):
    if not 0 < k < 1:
        return ""
    s = []
    for j in range(n):
        u = (j + 0.5) / n * 2 - 1
        x = cx + u * spread * lib.ease_out(k, 2)
        y = cy - rise * lib.ease_out(k, 2) * (1 - abs(u) * .5)
        r = rmax * (0.5 + 0.5 * math.sin(j * 1.9 + 1)) * (0.4 + k) * (1 - k * .6)
        s.append(blob(ellipse_pts(x, y, r, r * .8, 9), color, 0.85 * (1 - k)))
    return "".join(s)


def glint(cx, cy, k, r=60, color="#ffffff"):
    """Четырёхлучевой блик-звёздочка: растёт и тает (k 0→1)."""
    if not 0 < k < 1:
        return ""
    a = r * math.sin(math.pi * k) ** .7
    pts = [(cx, cy - a, 1), (cx + a * .16, cy - a * .16, 1), (cx + a, cy, 1), (cx + a * .16, cy + a * .16, 1), (cx, cy + a, 1),
           (cx - a * .16, cy + a * .16, 1), (cx - a, cy, 1), (cx - a * .16, cy - a * .16, 1)]
    return blob(pts, color, 0.95)
