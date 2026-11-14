"""Общее для сцен группы C рилса 50: хлёст на входе, штрихи скорости, цифры шрифтом IDB, часть камеры."""
import math

import lib
from lib import INK, clamp, ease_out, f, line


def whip_in(t, t_hit, dur=0.2, dist=700.0, rot=7.0):
    """Хлёст-въезд: до t_hit - dur — сцена за кадром справа, к t_hit встала. Возвращает (dx, rot_deg, u 0..1)."""
    u = clamp((t - (t_hit - dur)) / dur)
    k = ease_out(u, 3)
    return dist * (1 - k), rot * (1 - k), u


def speed_streaks(u, seed=0, n=7, y0=420, dy=150):
    """Штрихи скорости на время хлёста (u 0..1, пока идёт)."""
    if not (0 < u < 1):
        return ""
    k = ease_out(u, 3)
    s = []
    for j in range(n):
        yy = y0 + j * dy + (j % 3) * 18
        x0 = 120 + ((j * 211) % 700)
        ln = 420 * (1 - k)
        s.append(line([(x0, yy), (x0 + ln, yy + 4)], 9 * (1 - k) + 2, INK, taper=.6, seed=seed + j, op=.5 * (1 - k) + .15))
    return "".join(s)


def text(x, y, s, size, fill, anchor="middle", extra="", stroke=None, sw=0.0, op=1.0):
    st = f' stroke="{stroke}" stroke-width="{f(sw)}" stroke-linejoin="round" paint-order="stroke"' if stroke else ""
    o = f' opacity="{op:.3f}"' if op != 1 else ""
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="IDB" font-weight="900" font-size="{f(size)}" fill="{fill}" '
            f'text-anchor="{anchor}"{st}{o} {extra}>{s}</text>')


def shake(t, t0, amp=10.0, decay=9.0, freq=38.0):
    e = t - t0
    if e < 0:
        return 0.0, 0.0
    k = math.exp(-e * decay)
    return amp * k * math.sin(e * freq), amp * 0.7 * k * math.sin(e * freq * 1.27 + 1.0)


def punch(t, t0, amp=0.06, decay=7.0):
    e = t - t0
    if e < 0:
        return 1.0
    return 1 + amp * math.exp(-e * decay) * math.sin(min(e * 16, math.pi))


def wob(t, seed=0.0, a=1.0):
    return a * (math.sin(t * 1.7 + seed) + 0.5 * math.sin(t * 3.1 + seed * 2.3))
