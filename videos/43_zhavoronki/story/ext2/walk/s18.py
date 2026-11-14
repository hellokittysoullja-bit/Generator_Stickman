"""s18 (24.76–27.90, клип 24.56–27.90): финал-призыв. Крупно кот (look/hero.png: ЛЕВОЕ от зрителя ухо загнуто, зелёные
глаза, по две оранжевые полоски на щеках, огонёк на хвосте) сидит на столешнице перед кофеваркой рядом с будильником,
смотрит в камеру. На «кот» (25.28) кладёт левую (от зрителя) лапу на будильник и чуть прижимает, огонёк вспыхивает;
дальше медленно моргает (26.05 и 27.25), щурится довольно. Камера влетает хлёстом и медленно наезжает."""
import math

import cat_sit
import flatlib as F
from flatlib import clamp, ease_io, ease_out, smooth

T_A, T_B = 24.56, 27.90
T_NAP = F.word("напиши", 24.5)
T_KOT = F.word("кот", 25.0)
CAT_X, CAT_Y, CAT_S = 858.0, 1226.0, 0.70
AL_X = 752.0


def cam(t):
    u = clamp((t - T_A) / (T_B - T_A))
    ww = F.whip_in(t, T_A, .24)
    hit = F.bump(t, T_KOT + .05, .3)
    cx = 828 + 8 * u - 200 * ww
    cy = 1130 - 12 * u
    s = 2.95 + .3 * (0.4 * u + 0.6 * ease_io(u)) + .07 * hit
    r = 1.2 * ww + .5 - .9 * u
    return cx, cy, s, r


def paw(t):
    """Точка лапы (внутр. коорд. кота): от покоя дугой на будильник к T_KOT, потом лежит, два лёгких похлопывания."""
    cy = F.CT - F.A37.FOOT_Y / 200.0 * F.ALARM_S
    tgt_w = (AL_X + F.ALARM_S * .72, cy + F.ALARM_S * .02)
    tgt = cat_sit.to_int(tgt_w, CAT_X, CAT_Y, CAT_S)
    rest = cat_sit.PAW_REST
    a0 = T_KOT - .32
    u = clamp((t - a0) / (T_KOT - a0))
    k = ease_io(u)
    x = rest[0] + (tgt[0] - rest[0]) * k
    y = rest[1] + (tgt[1] - rest[1]) * k - 40 * math.sin(math.pi * u) ** 1.2
    press = 0.0
    if t >= T_KOT:
        e = t - T_KOT
        press = math.exp(-e * 10) * abs(math.sin(e * 30))
        x -= 3 * press
        for c in (0.7, 1.05):
            if c < e < c + .3:
                y -= 10 * math.sin(math.pi * (e - c) / .3)
    return (x, y), press


def frame(t):
    F.lib.DEFS.clear()
    c = cam(t)
    F.set_ink(c[2])
    w = F.room(t, clock=(7, 25))
    k_al = 0.0
    if t >= T_KOT:
        k_al = math.exp(-(t - T_KOT) * 9) * math.sin((t - T_KOT) * 40)
    al = F.alarm(AL_X, F.CT, F.ALARM_S, t, 7, 25, squash=1 - .05 * abs(k_al), rot=1.5 * k_al, uid="a18")
    objs = F.machine(0.0) + F.A37.shadow(AL_X, F.CT - 2, F.ALARM_S, .3) + al
    # кот
    P, press = paw(t)
    blink = 0.0
    for cb, half, hold in ((26.05, .36, .28), (27.25, .34, .22)):
        a = cb - half
        if a <= t <= cb + hold + half:
            blink = ease_io((t - a) / half) if t < cb else (1.0 if t < cb + hold else 1 - ease_io((t - cb - hold) / half))
    look_al = smooth(T_KOT - .45, T_KOT - .2, t) * (1 - smooth(T_KOT + .25, T_KOT + .5, t))
    look = (-.7 * look_al + .03 * math.sin(t * .9), .4 * look_al - .04)
    tilt = 4 * smooth(T_NAP, T_NAP + .25, t) * (1 - smooth(25.6, 26.0, t)) - 3 * look_al + 1.2 * math.sin(t * 1.3)
    flick = -10 * F.kick(t, T_KOT + .05, 9, 4.5) - 8 * F.kick(t, 26.7, 9, 4.5)
    tail = 6 * math.sin(t * 2.0 + .4) - 2
    fl = math.exp(-3.5 * max(0, t - T_KOT - .05)) * smooth(T_KOT - .05, T_KOT + .08, t)
    old = F.lib.INK_K[0]
    F.lib.INK_K[0] = old * CAT_S ** -0.62
    sh = F.blob(F.ellipse_pts(CAT_X + 20, CAT_Y - 1, 175 * CAT_S, 16 * CAT_S, 16), "#2a160a", .3, F.lib.blur(4))
    cat = cat_sit.draw(CAT_X, CAT_Y, CAT_S, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw=P, press=press, shadow=False,
                       flame_k=1.3 + .6 * fl, smile=smooth(26.4, 26.8, t))
    F.lib.INK_K[0] = old
    fx, fy = cat_sit.flame_world(CAT_X, CAT_Y, CAT_S, tail)
    r = 140 * (1 + .5 * fl)
    g = F.lib.rad_grad([(0, "#ffc060", .4 + .3 * fl), (1, "#ffb040", 0)], fx, fy, r, r)
    glow = f'<rect x="{fx - r:.1f}" y="{fy - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    return F.compose(w, objs + glow + sh + cat, c)


_ = ease_out
