"""Рилс 57 группа B: s08 (12.8–14.7) вид сверху на стол: суп, на «супа» (13.34) ложка падает, на «чая» (13.76) приходит чашка,
на «фруктов» (14.16) вкатываются яблоко, апельсин, арбуз; у всего блестящие капельки воды."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import fxprops as fp  # noqa: E402
import lib  # noqa: E402
import props  # noqa: E402
from lib import INK, W, H, back_out, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg  # noqa: E402

SEED = 9000
T0 = 12.6
T_SPOON, T_CUP, T_APPLE, T_ORANGE, T_MELON = 13.34, 13.76, 14.16, 14.24, 14.34
SOUP = (550, 480)
CUP = (270, 930)
APPLE = (810, 880)
ORANGE = (720, 1090)
MELON = (330, 1190)


def lerp(a, b, u):
    return a + (b - a) * u


def rnd(i):
    return abs(math.sin(i * 12.9898) * 43758.5453) % 1.0


def tablecloth():
    s = []
    s.append('<rect x="-1500" y="-1500" width="4200" height="4600" fill="#f4efe2"/>')
    for k in range(-14, 22):
        s.append(f'<rect x="{k * 150}" y="-1500" width="75" height="4600" fill="#9ccbd8"/>')
    for k in range(-14, 30):
        s.append(f'<rect x="-1500" y="{k * 150 - 600}" width="4200" height="75" fill="#9ccbd8" opacity=".75"/>')
    for k in range(-14, 22):
        for j in range(-4, 30):
            s.append(f'<rect x="{k * 150}" y="{j * 150 - 600}" width="75" height="75" fill="#7fb4c6" opacity=".55"/>')
    return "".join(s)


def ssh(cx, cy, rx, ry, op=.3):
    """Мягкая тень без фильтра: три вложенных эллипса."""
    return "".join(blob(ellipse_pts(cx, cy, rx * m, ry * m, 18), "#2a1608", op / 3.2) for m in (1.0, .86, .72))


def wet_drops(cx, cy, r, n, seed, t, u=1.0, kk=1.0):
    """Блестящие капельки воды по кругу r: сплошные, с белым бликом (props.droplet)."""
    o = []
    for i in range(n):
        a = 2 * math.pi * (i + rnd(seed + i) * .7) / n
        rr = r * (.25 + .7 * rnd(seed + i * 3))
        gl = 0.55 + 0.45 * math.sin(t * 6 + i * 1.7)
        o.append(props.droplet(cx + rr * math.cos(a), cy + rr * math.sin(a), (.75 + .35 * rnd(seed + i * 7)) * kk * u, rot=-20 + 40 * rnd(seed + i * 5), seed=seed + i))
        if gl > .93:
            o.append(props.shine_star(cx + rr * math.cos(a) + 8, cy + rr * math.sin(a) - 8, .8, (gl - .93) / .07))
    return "".join(o)


def steam(cx, cy, t, n=3, seed=0):
    s = []
    for i in range(n):
        ph = (t * .9 + i / n) % 1.0
        x = cx + (i - 1) * 70 + 24 * math.sin(ph * 6 + i)
        y = cy - ph * 230
        r = 22 + 30 * ph
        a = 1 - ph
        s.append(blob(ellipse_pts(x, y, r, r * .8, 10), "#ffffff", .9 * a * (1 if ph < .85 else 0)))
        s.append(blob(ellipse_pts(x + 8, y + 5, r * .7, r * .55, 8), "#e8f0f2", .6 * a))
    return "".join(s)


# ═════════════════════════ предметы (вид сверху) ═════════════════════════
def soup_plate(x, y, k, t, ripple=0.0):
    o = []
    o.append(fp.shadow(x + 26, y + 34, 270 * k, 250 * k, .3, 12))
    o.append(shape(ellipse_pts(x, y, 270 * k, 270 * k, 32), "#fbfaf4", blob(ellipse_pts(x + 40 * k, y + 50 * k, 250 * k, 220 * k, 24), "#e2dccd", .8), w=6, seed=SEED + 1))
    o.append(shape(ellipse_pts(x, y, 205 * k, 205 * k, 28), "#e6e1d2", "", w=4, seed=SEED + 2))
    ins = blob(ellipse_pts(x + 20 * k, y + 28 * k, 170 * k, 150 * k, 20), "#cf8a25", .9)
    # овощи: морковь, горошек, зелень, блики жира
    for i in range(7):
        a = 2 * math.pi * i / 7 + .4
        rr = (40 + 90 * rnd(i + 3)) * k
        ins += blob(ellipse_pts(x + rr * math.cos(a), y + rr * math.sin(a), 26 * k, 22 * k, 10), "#e8662b")
        ins += blob(ellipse_pts(x + rr * math.cos(a) - 6 * k, y + rr * math.sin(a) - 6 * k, 9 * k, 7 * k, 8), "#f59a5b")
    for i in range(6):
        a = 2 * math.pi * i / 6 + 1.1
        rr = (30 + 100 * rnd(i + 11)) * k
        ins += blob(ellipse_pts(x + rr * math.cos(a), y + rr * math.sin(a), 11 * k, 11 * k, 8), "#5f9a3a")
    for i in range(5):
        a = 2 * math.pi * i / 5 + .2
        rr = (60 + 60 * rnd(i + 21)) * k
        ins += blob(ellipse_pts(x + rr * math.cos(a), y + rr * math.sin(a), 20 * k, 9 * k, 8, rot=30 * i), "#f6d682", .95)
    ins += blob(ellipse_pts(x - 56 * k, y - 62 * k, 52 * k, 20 * k, 10, rot=-35), "#fff1b8")
    o.append(shape(ellipse_pts(x, y, 188 * k, 188 * k, 28), "#e8a43a", ins, w=5, seed=SEED + 3))
    if ripple > 0:
        for j in range(3):
            u = clamp(ripple * 1.2 - j * .22)
            if 0 < u < 1:
                o.append(f'<ellipse cx="{x + 74 * k:.1f}" cy="{y + 24 * k:.1f}" rx="{(30 + 120 * u) * k:.1f}" ry="{(26 + 100 * u) * k:.1f}" fill="none" stroke="#fff6dc" stroke-width="{7 * (1 - u):.1f}"/>')
    return "".join(o)


def spoon(x, y, ang, k):
    """Ложка сверху: черпак у (x, y), ручка по углу ang (градусы), металл."""
    o = []
    bowl = shape(ellipse_pts(0, 0, 60, 80, 18, rot=0), "#e5e9ec", blob(ellipse_pts(14, 18, 40, 56, 14), "#bfc7cd") + blob(ellipse_pts(-20, -30, 16, 30, 8), "#ffffff"), w=5, seed=SEED + 10)
    handle = shape([(-14, 70, 1), (14, 70, 1), (20, 300), (12, 372, 1), (-12, 372, 1), (-20, 300)], "#dfe4e8", blob([(2, 70), (14, 70), (20, 300), (12, 372), (6, 372)], "#b8c0c6"), w=5, seed=SEED + 11)
    o.append(handle + bowl)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)}) scale({k:.4f})">{"".join(o)}</g>'


def cup_top(x, y, ang, k, t, tea=1.0):
    o = []
    o.append(ssh(26, 30, 200, 190))
    o.append(shape(ellipse_pts(0, 0, 200, 200, 28), "#fbfaf4", blob(ellipse_pts(40, 40, 170, 150, 20), "#e2dccd", .8), w=6, seed=SEED + 20))
    # ручка справа
    hd = [(120, -30, 1), (230, -42), (264, 0), (230, 44), (120, 30, 1), (130, 12), (206, 6), (212, -6), (132, -12)]
    o.append(shape(hd, "#fbfaf4", "", w=5, seed=SEED + 21))
    o.append(shape(ellipse_pts(0, 0, 138, 138, 26), "#f2eee2", blob(ellipse_pts(24, 30, 110, 100, 16), "#d9d2c0", .7), w=5, seed=SEED + 22))
    o.append(shape(ellipse_pts(0, 0, 112, 112, 24), "#c97a28", blob(ellipse_pts(20, 24, 90, 80, 14), "#a85f1b", .8) + blob(ellipse_pts(-30, -34, 36, 14, 10, rot=-35), "#f2b56a"), w=4, seed=SEED + 23))
    # лимонный круг в чае
    o.append(shape(ellipse_pts(-20, 10, 40, 40, 14), "#f6e07a", blob(ellipse_pts(-20, 10, 24, 24, 10), "#fff2a8"), w=3, seed=SEED + 24))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)}) scale({k:.4f})">{"".join(o)}</g>'


def apple(x, y, r, ang):
    o = []
    o.append(ssh(14, 20, r * 1.05, r * .98))
    body = [(0, -r * .86), (r * .62, -r * 1.0), (r * 1.0, -r * .3), (r * .92, r * .52), (r * .46, r * 1.0), (0, r * .9), (-r * .46, r * 1.0), (-r * .92, r * .52), (-r * 1.0, -r * .3), (-r * .62, -r * 1.0)]
    inner = blob(ellipse_pts(r * .35, r * .35, r * .8, r * .7, 14), "#a91f1c", .9) + blob(ellipse_pts(-r * .4, -r * .4, r * .22, r * .36, 10, rot=40), "#ff8a7a")
    o.append(shape(body, "#d6302b", inner, w=5, seed=SEED + 30))
    o.append(line([(0, -r * .78), (r * .06, -r * 1.12), (r * .22, -r * 1.3)], 9, "#5c3a1c", taper=.3, wmin=.7, seed=SEED + 31))
    o.append(shape([(r * .12, -r * 1.0), (r * .6, -r * 1.3), (r * .76, -r * 1.02), (r * .34, -r * .84)], "#5f9a3a", "", w=3.6, seed=SEED + 32))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)})">{"".join(o)}</g>'


def orange(x, y, r, ang):
    o = []
    o.append(ssh(x + 14, y + 20, r * 1.05, r * 1.0))
    inner = blob(ellipse_pts(r * .3, r * .3, r * .85, r * .8, 14), "#e07a12", .85) + blob(ellipse_pts(-r * .42, -r * .42, r * .3, r * .38, 10, rot=40), "#ffc27a")
    for i in range(14):
        a = i * 0.9
        inner += blob([(r * .3 * math.cos(a), r * .3 * math.sin(a)), (r * .32 * math.cos(a + .1), r * .32 * math.sin(a + .1))], "#c8690f") if False else ""
    for i in range(10):
        xx, yy = r * (rnd(i + 40) * 1.6 - .8), r * (rnd(i + 60) * 1.6 - .8)
        inner += blob(ellipse_pts(xx, yy, 3, 3, 6), "#d9650c")
    o.append(shape(ellipse_pts(x, y, r, r, 22), "#f59428", f'<g transform="translate({f(x)} {f(y)})">{inner}</g>', w=5, seed=SEED + 40))
    o.append(shape([(x - 10, y - r * .12, 1), (x + 14, y - r * .08, 1), (x + 12, y + r * .12, 1), (x - 8, y + r * .1, 1)], "#6a9a3a", "", w=3, seed=SEED + 41))
    return "".join(o)


def melon(x, y, r, ang):
    """Ломтик арбуза сверху: полукруг, зелёная корка, розовая мякоть, чёрные косточки."""
    o = []
    o.append(ssh(14, r * .5 + 14, r * 1.0, r * .56))
    pts = [(-r, 0, 1), (-r * .94, r * .5), (-r * .6, r * .9), (0, r * 1.0), (r * .6, r * .9), (r * .94, r * .5), (r, 0, 1)]
    o.append(shape(pts, "#3f8a3a", "", w=5, seed=SEED + 50))
    fl = [(-r * .88, r * .04, 1), (-r * .82, r * .46), (-r * .52, r * .8), (0, r * .9), (r * .52, r * .8), (r * .82, r * .46), (r * .88, r * .04, 1)]
    inner = blob([(-r, -4), (r, -4), (r, r * .18), (-r, r * .18)], "#ff7a8a", .0)
    o.append(shape(fl, "#f0475a", blob([(r * .2, r * .2), (r * .88, r * .04), (r * .82, r * .46), (r * .5, r * .8), (r * .1, r * .85)], "#d9374d", .8) + blob(ellipse_pts(-r * .4, r * .25, r * .22, r * .1, 8, rot=-25), "#ff9aa8"), w=4, seed=SEED + 51))
    o.append(line([(-r * .92, r * .06), (-r * .5, r * .86), (0, r * .95), (r * .5, r * .86), (r * .92, r * .06)], 9, "#c9f0a8", taper=.1, wmin=.8, seed=SEED + 52, op=.0))
    for i in range(7):
        a = math.pi * (.12 + .76 * i / 6)
        rr = r * (.4 + .22 * (i % 2))
        o.append(shape(ellipse_pts(rr * math.cos(a + math.pi) * -1, rr * math.sin(a) * .9 + r * .06, 8, 13, 8, rot=math.degrees(a) - 90), "#2b1e1a", "", w=1.4, seed=SEED + 60 + i, ink=False))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)})">{"".join(o)}</g>'


def s08_frame(t):
    s = [tablecloth()]
    # суп: заезжает слева на первых кадрах (движение с кадра 0)
    u = clamp((t - T0) / 0.38)
    sx = lerp(-330, SOUP[0], 1 - (1 - spring(t - T0 - 0.0, 2.2, 5.5)) * 0 - 0) if False else lerp(-330, SOUP[0], ease_out(u, 3)) + 18 * math.sin(clamp(u, 0, 1) * math.pi) * (1 - u) * 3
    sy = SOUP[1]
    rip = clamp((t - T_SPOON) / 0.6)
    s.append(soup_plate(sx, sy, 1.0, t, rip))
    # пар от супа
    s.append(steam(sx, sy - 30, t, 3))
    s.append(wet_drops(sx, sy, 245, 7, 100, t, ease_out(clamp((t - T0 - 0.25) / 0.3))))
    # ложка: висит над супом, качается; падает на «супа» (удар в 13.34)
    if t < T_SPOON:
        u = clamp((t - (T_SPOON - 0.2)) / 0.2)
        k = lerp(1.9, 1.0, ease_in(u, 2.0)) if t > T_SPOON - 0.2 else lerp(2.2, 1.9, ease_io(clamp((t - T0) / 0.8)))
        k = k if t > T_SPOON - 0.2 else lerp(2.2, 1.9, ease_out(clamp((t - T0) / 0.9)))
        px = lerp(SOUP[0] + 40, SOUP[0] + 16, u) + 20 * math.sin(t * 11)
        py = lerp(SOUP[1] - 70, SOUP[1] + 10, u) + 12 * math.sin(t * 8)
        ang = -34 + 6 * math.sin(t * 9)
        sh = (k - 1.0) * 60
        s.append(fp.shadow(px + sh, py + sh * .9 + 20, 90 * k * .5, 120 * k * .5, .22, 12))
        s.append(spoon(px, py, ang, k))
    else:
        e = t - T_SPOON
        s.append(spoon(SOUP[0] + 16, SOUP[1] + 10 + 3 * math.exp(-e * 9) * math.sin(e * 40), -34 + 2 * math.sin(e * 30) * math.exp(-e * 8), 1.0))
    # брызги от ложки
    e = t - T_SPOON
    if 0 < e < 0.55:
        for i in range(9):
            a = 2 * math.pi * i / 9 + .3
            v = 330 * (.6 + .7 * rnd(i + 5))
            px = SOUP[0] + 60 + v * math.cos(a) * e
            py = SOUP[1] + 30 + v * math.sin(a) * e * .9 - 480 * e * (1 - e)
            s.append(blob(ellipse_pts(px, py, 14 * (1 - e), 18 * (1 - e), 8), "#e8a43a"))
        s.append(fp.burst(SOUP[0] + 60, SOUP[1] + 30, e / .5, 10, 170, 330, 11, "#fff4c2", SEED + 70))
    # чашка: влетает слева, кружится, садится на «чая»
    if t > T_CUP - 0.34:
        u = clamp((t - (T_CUP - 0.34)) / 0.34)
        cxp = lerp(-300, CUP[0], ease_out(u, 3))
        cyp = lerp(CUP[1] + 120, CUP[1], ease_out(u, 3))
        ang = lerp(-210, 0, ease_out(u, 3)) + 4 * math.sin(spring(t - T_CUP, 2.4, 6) * 6) * (1 if t > T_CUP else 0)
        kk = 1 + 0.06 * math.exp(-max(0.0, t - T_CUP) * 9) * math.sin(max(0.0, t - T_CUP) * 40)
        s.append(cup_top(cxp, cyp, ang, 0.8 * kk, t))
        if t >= T_CUP - 0.05:
            s.append(wet_drops(CUP[0] - 10, CUP[1], 150, 5, 130, t, ease_out(clamp((t - T_CUP) / 0.3)), .85))
        e = t - T_CUP
        if 0 < e < 0.5:
            s.append(fp.burst(CUP[0], CUP[1], e / .5, 10, 190, 340, 10, "#fff4c2", SEED + 80))
        if t > T_CUP:
            s.append(steam(CUP[0] - 20, CUP[1] - 40, t * 1.1, 2))
    # фрукты вкатываются: яблоко справа, апельсин снизу, арбуз слева-снизу
    for (tt, pos, kind, r, ang0, frm) in ((T_APPLE, APPLE, "apple", 100, 400, (1350, 700)), (T_ORANGE, ORANGE, "orange", 96, -360, (1300, 1350)), (T_MELON, MELON, "melon", 190, 500, (-320, 1500))):
        if t < tt - 0.30:
            continue
        u = clamp((t - (tt - 0.30)) / 0.30)
        x = lerp(frm[0], pos[0], ease_out(u, 2.4))
        y = lerp(frm[1], pos[1], ease_out(u, 2.4)) - 40 * math.sin(math.pi * u) * (0.4 if kind != "melon" else 0.2)
        ang = lerp(ang0, 0, ease_out(u, 2.4))
        bounce = 0.0
        if t > tt:
            e = t - tt
            bounce = -22 * math.exp(-e * 8) * abs(math.sin(e * 22))
        if kind == "apple":
            s.append(apple(x, y + bounce, r, ang))
        elif kind == "orange":
            s.append(orange(x, y + bounce, r, ang))
        else:
            s.append(melon(x, y + bounce, r, ang))
        if t > tt - .1:
            s.append(wet_drops(x, y, r * .75, 4, 200 + int(tt * 3), t, ease_out(clamp((t - tt + .1) / 0.25)), .7))
        e = t - tt
        if 0 < e < 0.4:
            s.append(fp.dust(x, y + r * .8, e / .4, 5, r * 1.5, 30, SEED + 90 + int(tt), "#ffffff", 20))
    # камера сверху: лёгкий поворот и наезд, на каждом ударе — толчок
    u = clamp((t - T0) / 2.3)
    sc = lerp(1.06, 1.2, ease_io(u))
    cx, cy = lerp(540, 540, u), lerp(800, 830, ease_io(u))
    rot = lerp(-3.0, 2.2, ease_io(u))
    for te, a in ((T_SPOON, .06), (T_CUP, .045), (T_APPLE, .04), (T_ORANGE, .035), (T_MELON, .05)):
        e = t - te
        if e > 0:
            kk = math.exp(-e * 9)
            sc *= 1 + a * kk
            rot += 1.4 * kk * math.sin(e * 34)
            cy += 16 * kk * math.sin(e * 45)
    return svg(f'<rect width="{W}" height="{H}" fill="#f4efe2"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')


def frame(sid, t):
    lib.dyn_begin()
    return s08_frame(t)
