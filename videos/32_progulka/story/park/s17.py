"""s17 (30.06–31.90, клип 29.86–32.10): крупно кот в парке (сидит на газоне у дорожки, фон парка мягко размыт)
смотрит в камеру; на «Напиши» (30.16) наклоняет голову, подмигивает (правый от зрителя глаз) и на «кот» (30.64)
кивает; хвост качается, ухо дёргается, огонёк колышется, камера медленно наезжает с первого кадра."""
import math

import cat_sit
import lib
import park
from lib import clamp, ease_io, smooth

T_A, T_B = 29.86, 32.10


def bg(t):
    cx = 1500 + 18 * (t - T_A)
    s = 1.25
    cy = (960 - 1330) / s
    o = [park.backdrop(cx, cy, s, 0, t)]
    o.append(f'<g transform="{lib.cam(cx, cy, s, 0)}">{park.ground(cx, cy, s, t)}</g>')
    return f'<g {lib.blur(3.2)}>{"".join(o)}</g>'


def frame(t):
    lib.DEFS.clear()
    z = 1 + 0.07 * ease_io(clamp((t - T_A) / (T_B - T_A)))
    # подмигивание: правый (от зрителя) глаз
    w = smooth(30.26, 30.40, t) * (1 - smooth(30.84, 30.98, t))
    blink_l = 0.0
    tb = 31.55
    if abs(t - tb) < .09:
        blink_l = min(1, 1.7 * (1 - abs(t - tb) / .09))
    blink = (max(blink_l, 0.22 * w), max(blink_l, w))
    tilt = -6 * smooth(30.10, 30.32, t) * (1 - smooth(31.2, 31.6, t)) + 1.2 * math.sin(t * 1.3)
    nod = 16 * math.sin(math.pi * clamp((t - 30.58) / 0.36)) + 8 * math.sin(math.pi * clamp((t - 30.94) / 0.3)) * .5
    flick = -10 * math.exp(-9 * max(0, t - 29.9)) * math.sin(max(0, t - 29.9) * 30) + -8 * math.exp(-9 * max(0, t - 31.3)) * math.sin(
        max(0, t - 31.3) * 30) * (t > 31.3)
    tail = 5 * math.sin(t * 2.4) - 3
    look = (0.05 * math.sin(t * .8), -0.1)
    cat = cat_sit.draw(478, 1296, 2.8, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, nod=nod)
    body = bg(t) + f'<g transform="translate(540 960) scale({z:.4f}) translate(-540 -960)">{cat}</g>'
    return lib.svg(f'<g transform="translate(540 960) scale({1 + (z - 1) * .4:.4f}) translate(-540 -960)">{body}</g>')
