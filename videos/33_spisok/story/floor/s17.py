"""s17 (25.66–27.40, клип 25.46–27.60): крупно кот на столе Димы вечером рядом с маленькой карточкой «1. 2. 3.»
(две галочки, в третьем квадратике отпечаток лапы); смотрит в камеру, на «Напиши» (25.72) наклоняет голову и
подмигивает (правый от зрителя глаз), на «кот» (26.16) кивает, огонёк вспыхивает. Камера дрейфует с первого кадра."""
import math

import catdesk
import cat_sit
import lib
from lib import blob, clamp, ease_io, smooth

T_A, T_B = 25.46, 27.60
T_NAP, T_KOT = 25.72, 26.16


def frame(t):
    lib.DEFS.clear()
    u = clamp((t - T_A) / (T_B - T_A))
    c = catdesk.cam()
    drift = 3 * u
    bg = catdesk.backdrop(c, t, drift)
    dk = catdesk.desk(c, t)
    card = catdesk.Card(c, -10.5, 48.5, rot=-5)
    cd = card.draw(t, glow=0.0)
    mug = catdesk.mug(c, 26, 92)
    pen = catdesk.pencil(c, -24, 62, -13, 54)
    # кот
    x, y = c.p((1.0, catdesk.DESK_Y, 58.0))
    s = c.k(58.0) * 31 / 366
    w = smooth(T_NAP + .08, T_NAP + .2, t) * (1 - smooth(T_NAP + .55, T_NAP + .68, t))
    blink_l = 0.0
    for tb in (27.25,):
        if abs(t - tb) < .09:
            blink_l = min(1, 1.7 * (1 - abs(t - tb) / .09))
    blink = (max(blink_l, 0.22 * w), max(blink_l, w))
    tilt = -6 * smooth(T_NAP - .05, T_NAP + .16, t) * (1 - smooth(26.8, 27.2, t)) + 1.2 * math.sin(t * 1.3)
    nod = 18 * math.sin(math.pi * clamp((t - T_KOT) / 0.34)) + 6 * math.sin(math.pi * clamp((t - T_KOT - .34) / 0.28))
    flick = -10 * math.exp(-9 * max(0, t - 25.5)) * math.sin(max(0, t - 25.5) * 30) - 8 * math.exp(-9 * max(0, t - 26.9)) * math.sin(
        max(0, t - 26.9) * 30) * (t > 26.9)
    tail = 5 * math.sin(t * 2.4) - 3
    look = (0.05 * math.sin(t * .8), -0.05)
    fl = math.exp(-3.5 * max(0, t - T_KOT - .05)) * smooth(T_KOT - .05, T_KOT + .08, t)
    shadow = blob(lib.ellipse_pts(x + 30 * s, y - 2, 175 * s, 20 * s, 16), "#2a160a", .32, lib.blur(6))
    cat = cat_sit.draw(x, y, s, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, nod=nod, shadow=False, flame_k=1.3 + .7 * fl,
                       smile=.6 * smooth(T_KOT + .3, T_KOT + .6, t))
    glow = ""
    if fl > .02:
        fx, fy = cat_sit.flame_world(x, y, s, tail)
        g = lib.rad_grad([(0, "#ffd070", .6 * fl), (1, "#ffb040", 0)], fx, fy, 200 * s * (1 + .6 * fl), 200 * s * (1 + .6 * fl))
        glow = f'<rect x="-100" y="-100" width="1280" height="2200" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    world = bg + dk + mug + pen + glow + shadow + cat + cd
    z = 1.3 + 0.06 * (0.4 * u + 0.6 * ease_io(u))
    return lib.svg(f'<g transform="translate({540 - 14 * u:.2f} 340) scale({z:.4f}) translate(-555 -730)">{world}</g>')
