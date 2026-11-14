"""Рилс 55 s04 (7.2–10.2, клип 7.0–10.4): кот на столе у ноутбука поворачивается к зрителю на «Знаешь» (7.37), наклон головы; огонёк вспыхивает на «тянет» (9.77); Дима за столом вздыхает. База — рилс 51 s07.
"""
_UNUSED = """Рилс 51, s07 (10.8–12.3, клип 10.6–12.5): кот запрыгивает на стол рядом с телефоном Димы, садится, на «Знаешь» (10.96)
поворачивает голову к зрителю, поднимает бровь, над ним рисуется знак вопроса; камера наезжает на кота."""
import math

import cat
import dima
import lib
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg, T)

_ST = {}
TURN = 7.37         # «Знаешь»
BROW = 7.62
FLARE = 9.77        # «тянет»
CATX, CATY, CSC = 670, 1210, 1.7
TOP = 1130          # дальний край столешницы
CAMX, CAMY = 590, 1000


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



def laptop(t):
    """Ноутбук слева, виден сзади-сбоку: крышка с тусклым лого-пятном, по краю свет экрана, клавиатурная часть."""
    out = [blob([(110, 1196), (560, 1176), (600, 1214), (80, 1236)], "#1a0e05", .35, blur(10))]
    base = [(100, 1160), (540, 1150), (600, 1218), (70, 1232)]
    out.append(shape(base, "#6f7385", blob([(70, 1214), (600, 1200), (600, 1218), (70, 1232)], "#4d5060"), w=5, seed=520))
    lid = [(120, 930), (530, 920), (548, 1170), (110, 1180)]
    pu = 0.8 + 0.2 * math.sin(t * 5)
    out.append(shape(lid, "#8d92a6", blob([(120, 930), (170, 928), (160, 1178), (110, 1180)], "#a9aec0") + blob([(480, 922), (530, 920), (548, 1170), (500, 1172)], "#6a6f82"), w=5.5, seed=521))
    out.append(shape([(280, 1020), (370, 1018), (372, 1090), (282, 1092)], "#a9aec0", "", w=3, seed=522))
    gl = rad_grad([(0, "#cfe0ff", .55 * pu), (1, "#cfe0ff", 0)], 330, 1040, 420, 380)
    out.append(f'<rect x="-200" y="600" width="1000" height="900" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
    return '<g transform="translate(150 340) scale(.7)">' + "".join(out) + "</g>"


def dima_bg(t):
    """Дима за столом, вид по грудь, сутулится, вздыхает (вдох 8.0–8.6, выдох 8.6–9.4)."""
    inh = smooth(7.9, 8.6, t) - smooth(8.6, 9.5, t)
    sag = smooth(8.6, 9.5, t)
    lean = math.radians(7 - 3 * inh + 4 * sag + 1.2 * math.sin(t * 1.9))
    pose = {"hip": (0.0, 0.0), "lean": lean, "head_ang": math.radians(5 + 6 * sag - 3 * inh + 2 * math.sin(t * 2.2)),
            "feet": {"n": ((40, 260), 0.0), "f": ((-20, 260), 0.0)},
            "arms": {"n": ("ik", (150, 40), -1), "f": ("ik", (110, 30), -1)}, "hands": {"n": "none", "f": "none"},
            "expr": {"lid": 0.3 + 0.2 * inh - 0.15 * sag, "look": (0.5, 0.25), "brows": "worry", "mouth": "tired", "hair": 2 * math.sin(t * 4)},
            "hood": 0.0, "strings": (3 * math.sin(t * 3.1), 0)}
    g, _ = dima.draw(pose)
    K = 1.75
    cid = lib.clip_rect(-400, -400, 2400, 400 + TOP + 4)
    br = 1 + 0.01 * math.sin(t * 2.4) + 0.012 * inh
    return f'<g clip-path="url(#{cid})"><g transform="translate(250 1170) scale({K} {K * br:.4f})">{g}</g></g>'


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



def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        cat.static_parts()
        dima.LWK = 1.0
        lib.static_done()
    lib.dyn_begin()
    X, Y = CATX, CATY
    e0 = t - TURN
    # лёгкий присед-встряска на повороте и на вспышке огонька
    k = math.exp(-max(e0, 0) * 9) * math.cos(max(e0, 0) * 30) if e0 > 0 else 0
    ef = t - FLARE
    kf = math.exp(-ef * 8) * math.cos(ef * 26) if ef > 0 else 0
    sqx, sqy = 1 + 0.05 * k + 0.05 * kf, 1 - 0.05 * k - 0.05 * kf
    turn = -1.0 + 1.0 * ease_out(clamp((t - TURN + 0.05) / 0.22), 3)
    over = spring(t - TURN, 3.5, 7.0) - 1 if t > TURN else 0
    turn = min(0.0, turn) + 0.18 * over
    sw = 1 - smooth(TURN - 0.05, TURN + 0.08, t)
    look = (-1.0 * sw, 0.2 * sw)
    brow = ease_out(clamp((t - BROW) / 0.14), 2) if t > BROW else 0.0
    tilt = 5 * math.sin(t * 2.0) * sw + 5 * (1 - sw) * (1 - 0.6 * smooth(BROW, BROW + .3, t)) - 6 * smooth(BROW, BROW + 0.25, t) + 3 * math.sin(t * 1.5) * (1 - sw)
    blink = 0.0
    for c, half in ((7.15, 0.05), (8.4, 0.06), (9.3, 0.06)):
        if c - half <= t <= c + half:
            blink = 1 - abs(t - c) / half
    flick = 0.0
    for c in (7.05, TURN + 0.1, 8.9):
        ee = t - c
        if 0 <= ee < 0.5:
            flick += -14 * math.exp(-ee * 9) * math.sin(ee * 34)
    tail = 10 * math.sin(t * 3.1) + 5 * math.sin(t * 5.3 + 1) + (16 * math.exp(-ef * 6) * math.sin(ef * 20) if ef > 0 else 0)
    s = [_ST["bg"], dima_bg(t), laptop(t)]
    s.append(blob(ellipse_pts(CATX + 20, CATY + 4, 300, 30, 18), "#1a0e05", .4, blur(10)))
    s.append(cat_draw(X, Y, CSC, t, look, blink, tilt, turn, brow, sqx, sqy, tail, flick))
    fx, fy = cat.flame_world(X, Y, CSC, tail)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    boost = 1 + 2.2 * math.exp(-max(ef, 0) * 3.5) * smooth(-0.04, 0.03, ef) if ef > -0.04 else 1.0
    g = rad_grad([(0, "#ffb050", min(.9, .35 * fl * boost)), (1, "#ffb050", 0)], fx, fy, 300 * boost ** .6, 300 * boost ** .6)
    s.append(f'<rect x="{f(fx - 900)}" y="{f(fy - 900)}" width="1800" height="1800" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    if 0 < ef < 0.55:   # искры огонька
        kk = ef / 0.55
        for j in range(9):
            a = math.radians(-160 + j * 20)
            r0, r1 = 70 + 60 * kk, 120 + 150 * kk
            s.append(line([(fx + r0 * math.cos(a), fy + r0 * math.sin(a) - 30), (fx + r1 * math.cos(a), fy + r1 * math.sin(a) - 30)],
                          9 * (1 - kk) + 1.5, "#ffd27a", seed=540 + j, taper=.6))
    # камера: дрейф с первого кадра, толчок на «Знаешь» и на вспышке
    v = clamp((t - 7.0) / 3.4)
    ccx, ccy = CAMX - 60 * v, CAMY - 20 * v
    scc = 0.92 + 0.28 * ease_io(v) + 0.06 * (1 - ease_out(clamp((t - 7.0) / .5)))
    if e0 > 0:
        kk = math.exp(-e0 * 7)
        scc *= 1 + 0.06 * kk
        ccx += 8 * kk * math.sin(e0 * 43)
    if ef > 0:
        kk = math.exp(-ef * 8)
        scc *= 1 + 0.05 * kk
        ccy += 12 * kk * math.sin(ef * 40)
    crot = 0.9 * math.sin(t * 1.3) + 2.0 * (1 - clamp((t - 7.0) / 0.6)) + (2.5 * math.exp(-max(e0, 0) * 6) if e0 > 0 else 0)
    return svg(f'<rect width="{W}" height="{H}" fill="#2d2a47"/><g transform="{cam(ccx, ccy, scc, crot)}">{"".join(s)}</g>')
