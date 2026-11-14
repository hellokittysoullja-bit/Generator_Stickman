"""Рилс 51, s07 (10.8–12.3, клип 10.6–12.5): кот запрыгивает на стол рядом с телефоном Димы, садится, на «Знаешь» (10.96)
поворачивает голову к зрителю, поднимает бровь, над ним рисуется знак вопроса; камера наезжает на кота."""
import math

import cat
import lib
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg, T)

_ST = {}
LAND = 10.84        # приземление на стол
TURN = 10.96        # «Знаешь»
BROW = 11.14
CATX, CATY, CSC = 600, 1210, 2.0
TOP = 1130          # дальний край столешницы


def background():
    s = []
    g = lin_grad([(0, "#2d2a47", 1), (1, "#4a3c5c", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-800" y="-800" width="2700" height="{TOP + 800}" fill="url(#{g})"/>')
    for k, x in enumerate(range(-760, 1900, 130)):
        s.append(f'<rect x="{x}" y="-800" width="46" height="{TOP + 800}" fill="#352f50" opacity=".8"/>')
    # окно с ночным небом
    wx0, wy0, wx1, wy1 = 90, 330, 470, 800
    gs = lin_grad([(0, "#14184a", 1), (1, "#3a3f88", 1)], 0, 0, 0, 1)
    pts = rect_pts(wx0, wy0, wx1, wy1, 10)
    inner = f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="url(#{gs})"/>'
    inner += blob(ellipse_pts(360, 460, 46, 46, 16), "#fff2c4")
    inner += blob(ellipse_pts(378, 450, 40, 40, 16), "#2a2f70")
    for k, (x, y) in enumerate([(160, 420), (230, 560), (310, 380), (420, 650), (150, 700)]):
        inner += blob(ellipse_pts(x, y, 4, 4, 6), "#fff6d8")
    inner += blob([(wx0, 720), (200, 690), (300, 720), (400, 680), (wx1, 720), (wx1, wy1), (wx0, wy1)], "#1b1c4a")
    s.append(shape(pts, "#14184a", inner, w=7, seed=501))
    s.append(line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], 9, "#cdb894", seed=502, taper=.05))
    s.append(line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], 9, "#cdb894", seed=503, taper=.05))
    s.append(shape(rect_pts(wx0 - 24, wy1 - 4, wx1 + 24, wy1 + 28, 8), "#cdb894", "", w=5, seed=504))
    # постер
    s.append(shape(rect_pts(760, 380, 960, 620, 6), "#e9d9b8", blob(rect_pts(790, 410, 930, 520), "#d4b07a") +
                   line([(790, 560), (930, 560)], 6, "#9a8a6a", seed=505) + line([(790, 585), (900, 585)], 6, "#9a8a6a", seed=506), w=6, seed=507))
    # стол
    tp = [(-800, TOP, 1), (1900, TOP, 1), (1900, 2800, 1), (-800, 2800, 1)]
    inner = "".join(line([(-800, TOP + 40 + k * 56), (1900, TOP + 44 + k * 56)], 2.4, "#7a5238", taper=.1, wmin=.7, seed=510 + k, op=.8) for k in range(8))
    s.append(shape(tp, "#9a6a46", inner, w=5, seed=508))
    s.append(blob(rect_pts(-800, TOP, 1900, TOP + 26), "#7e5336", .8))
    s.append(blob(rect_pts(-800, 1290, 1900, 1340), "#6a4430", 1))
    s.append(line([(-800, 1290), (1900, 1290)], 5, INK, taper=.05, wmin=.9, seed=509))
    s.append(blob(rect_pts(-800, 1340, 1900, 2800), "#46301f", 1))
    s.append(line([(-800, TOP), (1900, TOP)], 5, INK, taper=.05, wmin=.9, seed=511))
    # лампа слева-сверху: тёплый свет
    lg = rad_grad([(0, "#ffd89a", .5), (.6, "#ffb870", .14), (1, "#ffb870", 0)], 900, 300, 900, 900)
    s.append(f'<rect x="-800" y="-800" width="2700" height="3600" fill="url(#{lg})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def phone(t):
    """Телефон лежит на столе слева, экран светится злым красным и пульсирует."""
    P = [(170, 1180), (460, 1158), (508, 1262), (144, 1286)]
    out = [blob([(150, 1292), (520, 1268), (540, 1300), (130, 1320)], "#1a0e05", .4, blur(10))]
    pu = 0.75 + 0.25 * math.sin(t * 9)
    scr = [(188, 1190), (448, 1170), (488, 1250), (164, 1272)]
    gl = rad_grad([(0, "#ff5a3c", .55 * pu), (1, "#ff5a3c", 0)], 330, 1220, 380, 200)
    out.append(shape(P, "#1d1b26", "", w=5, seed=520))
    out.append(shape(scr, "#ff6a48", blob([(188, 1190), (448, 1170), (452, 1190), (188, 1210)], "#ff8a60", .8) +
                     blob([(164, 1262), (488, 1240), (488, 1250), (164, 1272)], "#d8402a", .8), w=3.5, seed=521))
    for k, (x0, x1, y) in enumerate([(210, 400, 1206), (220, 360, 1226), (210, 420, 1245)]):
        out.append(line([(x0, y + k * 2), (x1, y - 6)], 10, "#fff3e8", seed=522 + k, taper=.2, wmin=.8, op=.92))
    out.append(f'<rect x="-100" y="900" width="700" height="600" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
    return "".join(out)


def question(t):
    """Знак вопроса рисуется штрихами кодом: дуга, ножка, точка; потом покачивается."""
    e = t - (BROW + 0.04)
    if e < 0:
        return ""
    cx, cy = CATX + 20, 400
    bob = 10 * math.sin(e * 5.0) if e > 0.7 else 0
    sc = 1.0 + 0.06 * math.exp(-max(0, e - 0.7) * 6) * math.sin(e * 22) if e > 0.7 else 1.0
    # центральная линия «?»: дуга (угол от 200° до -80° по часовой), потом S-изгиб к ножке
    arc = []
    for k in range(0, 15):
        a = math.radians(165 + k * 16.5)
        arc.append((cx + 78 * math.cos(a), cy - 70 + 78 * math.sin(a) * 0.95))
    stem = [(cx + 34, cy - 4), (cx + 6, cy + 20), (cx, cy + 40), (cx, cy + 66)]
    path = arc + stem
    # длины
    L = [0.0]
    for p, q in zip(path, path[1:]):
        L.append(L[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
    prog = ease_out(clamp(e / 0.42), 2) * L[-1]
    pts = [path[0]]
    for i in range(1, len(path)):
        if L[i] <= prog:
            pts.append(path[i])
        else:
            u = (prog - L[i - 1]) / (L[i] - L[i - 1])
            pts.append((path[i - 1][0] + (path[i][0] - path[i - 1][0]) * u, path[i - 1][1] + (path[i][1] - path[i - 1][1]) * u))
            break
    s = []
    if len(pts) > 2:
        s.append(line(pts, 56, INK, taper=0.0, wmin=1.0, seed=530))
        s.append(line(pts, 40, "#ffe9a8", taper=0.0, wmin=1.0, seed=531))
    ed = ease_out(clamp((e - 0.42) / 0.16), 3)
    if ed > 0.02:
        dot = back_out_dot(ed)
        dx, dy = cx, cy + 116
        s.append(blob(ellipse_pts(dx, dy, 34 * dot, 34 * dot, 14), INK))
        s.append(blob(ellipse_pts(dx, dy, 24 * dot, 24 * dot, 14), "#ffe9a8"))
    # штрихи-«вспышка» вокруг в момент завершения
    if 0.45 < e < 0.9:
        k = (e - 0.45) / 0.45
        for j in range(5):
            a = math.radians(-150 + j * 38)
            r0, r1 = 150 + 30 * k, 190 + 70 * k
            s.append(line([(cx + r0 * math.cos(a), cy + 10 + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + 10 + r1 * math.sin(a))],
                          9 * (1 - k) + 1.5, "#ffe9a8", seed=540 + j, taper=.6))
    return f'<g transform="translate(0 {bob:.2f}) translate({cx} {cy}) scale({sc:.4f}) rotate({6 * math.sin(e * 3) if e > .7 else 0:.2f}) translate({-cx} {-cy})">{"".join(s)}</g>'


def back_out_dot(u):
    u = clamp(u) - 1
    return 1 + 2.6 * u ** 3 + 1.6 * u ** 2


def cat_draw(X, Y, sc, t, look, blink, tilt, turn, brow, sqx, sqy, tail, flick):
    st = cat.static_parts()
    br = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 2.6)
    o = []
    tw = f"rotate({tail:.2f} {cat.TAIL_PIVOT[0]} {cat.TAIL_PIVOT[1]})"
    o.append(f'<g transform="{tw}">{st["tail"]}</g>')
    sy = 1 + 0.012 * br
    o.append(f'<g transform="translate(0 {cat.CBOT}) scale(1 {sy:.4f}) translate(0 {-cat.CBOT})">{st["body"]}</g>')
    o.append(cat.leg_left(cat.PAW_REST, 0))
    hy = -(sy - 1) * (cat.CBOT - 1150)
    # «поворот головы»: голова сжата по x и сдвинута к стороне, куда смотрит (turn: -1 — к телефону, 0 — к зрителю)
    hsx = 1 - 0.07 * abs(turn)
    hdx = 26 * turn
    # бровь: правая (от зрителя) поднята дугой, левая опущена, пригнута
    BC = "#9a94b4"
    bl = [(cat.CX - 78, 1030 + 8 * brow), (cat.CX - 46, 1022 + 12 * brow), (cat.CX - 14, 1028 + 16 * brow)]
    rb_y = -34 * brow
    brr = [(cat.CX + 14, 1026 + rb_y + 4), (cat.CX + 46, 1010 + rb_y - 6 * brow), (cat.CX + 80, 1018 + rb_y + 10 * brow)]
    brows = line(bl, 6, BC, seed=560, taper=.4, wmin=.4) + line(brr, 6.4, BC, seed=561, taper=.4, wmin=.4)
    # половинное веко на левом глазу (скепсис)
    lid = ""
    if brow > 0.05:
        ex = cat.CX - 44
        lid = (f'<path d="M{ex - 42} 1030 L{ex + 42} 1030 L{ex + 42} {1056 + 12 * brow:.1f} Q{ex} {1066 + 12 * brow:.1f} {ex - 42} {1056 + 12 * brow:.1f}Z" '
               f'fill="{cat.CAT}"/>' + line([(ex - 36, 1056 + 12 * brow), (ex, 1064 + 12 * brow), (ex + 36, 1056 + 12 * brow)], 5, INK, seed=562))
    hg = st["head"] + cat.ears(flick) + st["face"] + cat.eyes(look, blink) + lid + brows + cat.whiskers(t)
    o.append(f'<g transform="translate(0 {hy:.2f}) translate({hdx:.2f} 0) rotate({tilt:.2f} {cat.NECK[0]} {cat.NECK[1]}) '
             f'translate({cat.NECK[0]} 0) scale({hsx:.4f} 1) translate({-cat.NECK[0]} 0)">{hg}</g>')
    o.append(f'<g transform="{tw}">{cat.flame(t)}</g>')
    return (f'<g transform="translate({X - cat.CX * sc:.2f} {Y - cat.CBOT * sc:.2f}) scale({sc:.4f}) '
            f'translate({cat.CX} {cat.CBOT}) scale({sqx:.4f} {sqy:.4f}) translate({-cat.CX} {-cat.CBOT})">{"".join(o)}</g>')


def dust(t):
    """Штрихи удара о стол в момент приземления (тушь, без полупрозрачных пятен)."""
    e = t - LAND
    if not 0 <= e < 0.3:
        return ""
    k = e / 0.3
    s = []
    for j in range(5):
        for side in (-1, 1):
            a = math.radians(-8 - j * 14)
            r0, r1 = 150 + 40 * k + j * 6, 190 + 100 * k + j * 6
            x0, y0 = CATX + side * r0 * math.cos(a), CATY + 14 + r0 * math.sin(a) * .5
            x1, y1 = CATX + side * r1 * math.cos(a), CATY + 14 + r1 * math.sin(a) * .5
            s.append(line([(x0, y0), (x1, y1)], 9 * (1 - k) + 1.5, INK, taper=.6, seed=570 + j + (side > 0) * 9))
    return "".join(s)


def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    e = t - LAND
    # прыжок: из-за правого нижнего края дугой на стол
    X, Y = CATX, CATY
    sqx = sqy = 1.0
    if t < LAND:
        u = clamp((t - 10.52) / (LAND - 10.52))
        X = CATX + 520 * (1 - u) ** 1.4
        Y = CATY + 520 * (1 - u) * (1 - u) * 0.9 - 760 * math.sin(math.pi * u) * (1 - 0.3 * u)
        Y = CATY - 760 * math.sin(math.pi * u) + 420 * (1 - u) ** 2
        sqx, sqy = 0.94 + 0.0, 1.07 - 0.02 * u            # вытянут в прыжке
    else:
        k = math.exp(-e * 9) * math.cos(e * 30)
        sqx, sqy = 1 + 0.10 * k, 1 - 0.10 * k
    # голова: смотрит на телефон, на «Знаешь» поворачивается к зрителю
    turn = -1.0 + 1.0 * ease_out(clamp((t - TURN + 0.05) / 0.2), 3)
    if t < LAND:
        turn = -1.0
    over = spring(t - TURN, 3.5, 7.0) - 1 if t > TURN else 0
    turn = min(0.0, turn) + 0.18 * over
    look = (-1.0 * (1 - smooth(TURN - 0.05, TURN + 0.08, t)), 0.35 * (1 - smooth(TURN - 0.05, TURN + 0.08, t)))
    brow = ease_out(clamp((t - BROW) / 0.14), 2) * (1 + 0.15 * math.exp(-(t - BROW) * 8) * math.sin((t - BROW) * 30)) if t > BROW else 0.0
    tilt = 4 * (1 - smooth(TURN - 0.05, TURN + 0.1, t)) - 5 * smooth(BROW, BROW + 0.2, t)
    blink = 0.0
    for c, half in ((10.78, 0.05), (11.9, 0.07)):
        if c - half <= t <= c + half:
            blink = 1 - abs(t - c) / half
    flick = 0.0
    for c in (TURN + 0.1, 11.7):
        ee = t - c
        if 0 <= ee < 0.5:
            flick += -14 * math.exp(-ee * 9) * math.sin(ee * 34)
    tail = 8 * math.sin(t * 3.1) + 4 * math.sin(t * 5.3 + 1)
    s = [_ST["bg"], phone(t)]
    air = clamp((CATY - Y) / 700)
    sh = 1 - 0.7 * air
    s.append(blob(ellipse_pts(CATX + 20, CATY + 4, 300 * sh, 30 * sh, 18), "#1a0e05", .4 * (1 - .5 * air), blur(10)))
    s.append(cat_draw(X, Y, CSC, t, look, blink, tilt, turn, brow, sqx, sqy, tail, flick))
    s.append(dust(t))
    # огонёк кота подсвечивает стену
    fx, fy = cat.flame_world(X, Y, CSC, tail)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g = rad_grad([(0, "#ffb050", .35 * fl), (1, "#ffb050", 0)], fx, fy, 300, 300)
    s.append(f'<rect x="{f(fx - 320)}" y="{f(fy - 320)}" width="640" height="640" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(question(t))
    # камера: наезд на кота, удар на приземлении и на «Знаешь»
    v = clamp((t - 10.6) / 1.9)
    ccx, ccy = 560 + 30 * v, 900 - 90 * v
    scc = 1.0 + 0.22 * ease_io(v)
    if t > LAND:
        kk = math.exp(-e * 8)
        scc *= 1 + 0.05 * kk
        ccy += 14 * kk * math.sin(e * 38)
    et = t - TURN
    if et > 0:
        kk = math.exp(-et * 7)
        scc *= 1 + 0.06 * kk
        ccx += 8 * kk * math.sin(et * 43)
    crot = 0.8 * math.sin(t * 1.3) + (3.0 * math.exp(-max(0, et) * 6) if et > 0 else 2.0 * (1 - v))
    return svg(f'<rect width="{W}" height="{H}" fill="#2d2a47"/><g transform="{cam(ccx, ccy, scc, crot)}">{"".join(s)}</g>')
