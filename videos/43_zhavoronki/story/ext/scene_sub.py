"""Карточка подписки рилса 43 (основа — scene_sub рилса 41; ниже — исходное описание 41, время — рилса 43:
«Подпишись» 3.20, «мифы» 4.68 — нажатие, кнопка серая с галочкой; «верят» 5.84 — штамп «МИФ?» и сердечки).
s03 (3.2–4.64): карточка влетает (3.0–3.2), на «Подпишись» (3.2) большой жёлтый колокольчик раскачивается и
звенит (штрихи звона), под ним красная кнопка «ПОДПИСАТЬСЯ». Из-за правого края карточки выглядывает кот, лапа на краю.
s04 (4.64–6.4): кот вылезает сильнее, тянет лапу к кнопке, на «истории» (5.24) вдавливает её и держит; на «Диму» (5.8)
кнопка становится серой «ВЫ ПОДПИСАНЫ» с галочкой, вылетают красные сердечки, колокольчик звякает ещё раз; толчки камеры."""
import math

import cat
import lib
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg, T)

_ST = {}
HIT = 3.2           # «Подпишись»
PRESS = 4.68        # «мифы»
DONE = 4.88        # кнопка серая сразу после нажатия
STAMP = 5.84       # «верят»
CX0, CX1, CY0, CY1 = 80, 830, 300, 1240      # карточка
BELL = (450, 420)
BS = 1.2   # точка подвеса колокольчика
BX0, BX1, BY0, BY1 = 110, 800, 930, 1080     # кнопка
TABLE = 1100        # дальний край стола


def background():
    s = []
    g = lin_grad([(0, "#f3c98a", 1), (1, "#e6a862", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-800" y="-800" width="2700" height="{TABLE + 800}" fill="url(#{g})"/>')
    # обои: мягкие вертикальные полосы
    for k, x in enumerate(range(-760, 1900, 120)):
        s.append(f'<rect x="{x}" y="-800" width="44" height="{TABLE + 800}" fill="#ecb878" opacity="1"/>')
    s.append(line([(-800, TABLE), (1900, TABLE)], 4.4, INK, taper=.05, wmin=.9, seed=401))
    tp = [(-800, TABLE, 1), (1900, TABLE, 1), (1900, 2800, 1), (-800, 2800, 1)]
    inner = "".join(line([(-800, TABLE + 46 + k * 58), (1900, TABLE + 50 + k * 58)], 2.4, "#b27a48", taper=.1, wmin=.7, seed=410 + k, op=.8)
                    for k in range(8))
    inner += blob(rect_pts(-800, TABLE, 1900, TABLE + 22), "#a8723f", .7)
    s.append(shape(tp, "#c98f5a", inner, w=4.4, seed=402))
    # тёплый свет сверху-слева
    lg = rad_grad([(0, "#fff0c8", .55), (.6, "#ffd890", .15), (1, "#ffd890", 0)], 300, 300, 1300, 1300)
    s.append(f'<rect x="-800" y="-800" width="2700" height="3600" fill="url(#{lg})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def card_static():
    s = []
    s.append(blob(rect_pts(CX0 + 30, CY1 - 24, CX1 + 50, CY1 + 26, 20), "#4a2a10", .4, blur(14)))
    pts = rect_pts(CX0, CY0, CX1, CY1, 54)
    inner = blob(rect_pts(CX1 - 70, CY0 - 10, CX1 + 10, CY1 + 10), "#ecdcbd", 1)
    inner += blob(rect_pts(CX0, CY1 - 50, CX1 + 10, CY1 + 10), "#ecdcbd", 1)
    inner += line([(CX0 + 40, CY0 + 34), (CX1 - 120, CY0 + 30)], 5, "#fffaf0", seed=420, op=.9)
    s.append(shape(pts, "#fbf1dc", inner, w=6, seed=421))
    # две строки-«точки» вверху: аватар канала и полоски — как карточка в приложении
    s.append(shape(ellipse_pts(CX0 + 90, CY0 + 92, 40, 40, 16), "#2f2a3a",
                   blob(ellipse_pts(CX0 + 90, CY0 + 108, 18, 12, 10), "#ff9a3a") + blob(ellipse_pts(CX0 + 90, CY0 + 92, 8, 12, 8), "#ffd36a"),
                   w=4, seed=422))
    s.append(shape(rect_pts(CX0 + 150, CY0 + 70, CX0 + 400, CY0 + 92, 11), "#d9c39c", "", w=3, seed=423))
    s.append(shape(rect_pts(CX0 + 150, CY0 + 104, CX0 + 310, CY0 + 120, 8), "#e6d3b0", "", w=2.6, seed=424))
    return "".join(s)


def bell(ang, cl, t):
    """Колокольчик: подвес в BELL, угол ang, язычок отстаёт (cl)."""
    x, y = BELL
    P = lambda pts, a=ang: T([(q[0] * BS, q[1] * BS) + tuple(q[2:]) for q in pts], x, y, 1.0, a)
    s = []
    # язычок (за телом, виден снизу)
    s.append(shape(T(ellipse_pts(0, 300 * BS, 28 * BS, 28 * BS, 14), x, y, 1.0, ang + cl), "#e8a21e",
                   blob(T(ellipse_pts(8 * BS, 306 * BS, 18 * BS, 18 * BS, 10), x, y, 1.0, ang + cl), "#c27c10"), w=4.4, seed=431))
    body = [(-22, 34), (-64, 60), (-96, 130), (-104, 200), (-118, 248), (-150, 270, 1), (150, 270, 1), (118, 248), (104, 200),
            (96, 130), (64, 60), (22, 34)]
    inner = blob(P([(30, 40), (110, 120), (130, 270), (60, 270), (70, 140)]), "#dc9a1c", 1)
    inner += line(P([(-58, 92), (-74, 160), (-80, 220)]), 12, "#fff0a8", seed=432, op=.95)
    inner += blob(P([(-150, 240), (150, 240), (150, 272), (-150, 272)]), "#e5a923", 1)
    s.append(shape(P(body), "#f8cb3c", inner, w=6, seed=433))
    s.append(shape(P(rect_pts(-160, 262, 160, 296, 16)), "#f0b72e", blob(P(rect_pts(40, 262, 160, 296)), "#d18f18", 1), w=5.4, seed=434))
    s.append(shape(P(ellipse_pts(0, 22, 26, 22, 14)), "#f0b72e", blob(P(ellipse_pts(8, 28, 16, 12, 10)), "#d18f18"), w=4.6, seed=435))
    s.append(blob(P(ellipse_pts(0, 0, 14, 14, 12)), INK))
    return "".join(s)


def ring_strokes(t):
    """Штрихи звона: дуги по обе стороны, вспыхивают на каждом крайнем положении качания."""
    e = t - HIT
    if e < 0:
        return ""
    x, y = BELL[0], BELL[1] + 170 * BS
    s = []
    amp = math.exp(-e * 0.9)
    ph = (e * 2.4) % 1.0                         # волна звона расходится, 2.4 раза в секунду
    for side in (-1, 1):
        for j in range(3):
            u = (ph + j / 3) % 1.0
            r = 240 + 80 * u
            wv = (1 - u) * 9 * amp
            if wv < 1.2:
                continue
            a0, a1 = (150, 210) if side < 0 else (-30, 30)
            pts = [(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in (a0, (a0 + a1) / 2, a1)]
            s.append(line(pts, wv, INK, taper=.6, wmin=.15, seed=440 + j + (side > 0) * 7))
    return "".join(s)


def heart(cx, cy, sc, rot, sd):
    pts = []
    for k in range(20):
        a = 2 * math.pi * k / 20
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((hx, hy) + ((1,) if k in (0, 10) else ()))
    P = lambda q: T(q, cx, cy, sc, rot)
    hl = blob(P([(-11, -8), (-6, -12), (-3, -8), (-8, -3)]), "#ffb3a8")
    return shape(P(pts), "#e8413a", blob(P([(2, -6), (16, -6), (16, 16), (0, 16)]), "#c22a26") + hl, w=3.6 / max(sc, .3) * sc, seed=sd)


def button(t):
    # вдавлена лапой с «истории» и держится, на «Диму» отпускается и становится серой
    dn = 16 * smooth(PRESS - 0.03, PRESS + 0.04, t) * (1 - smooth(DONE - 0.02, DONE + 0.12, t)) + 5 * smooth(DONE, DONE + 0.2, t)
    e = t - DONE
    on = e >= 0.0
    pop = 1.0
    if on:
        pop = 1 + 0.07 * math.exp(-e * 7) * math.sin(e * 26)
    cx, cy = (BX0 + BX1) / 2, (BY0 + BY1) / 2
    s = []
    col, sh, lip = ("#e23a32", "#b8261f", "#8f1a14") if not on else ("#a8a6b2", "#8a8896", "#6c6a78")
    # нижняя «толщина» кнопки
    s.append(shape(rect_pts(BX0, BY0 + 20, BX1, BY1 + 18, 40), lip, "", w=5, seed=450))
    g = []
    pts = rect_pts(BX0, BY0 + dn, BX1, BY1 + dn, 40)
    inner = blob(rect_pts(BX0, BY1 + dn - 34, BX1 + 4, BY1 + dn + 4), sh, 1)
    inner += line([(BX0 + 50, BY0 + dn + 22), (BX1 - 160, BY0 + dn + 20)], 7, "#ffffff" if not on else "#d6d4de", seed=451, op=.55)
    g.append(shape(pts, col, inner, w=5.4, seed=452))
    ty = cy + dn + 24
    if not on:
        g.append(f'<text x="{f(cx - 15)}" y="{f(ty + 4)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="68" '
                 f'fill="{sh}">ПОДПИСАТЬСЯ</text>')
        g.append(f'<text x="{f(cx - 18)}" y="{f(ty)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="68" '
                 f'fill="#ffffff">ПОДПИСАТЬСЯ</text>')
    else:
        tx = cx + 40
        g.append(f'<text x="{f(tx + 3)}" y="{f(ty + 2)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="50" '
                 f'fill="{sh}">ВЫ ПОДПИСАНЫ</text>')
        g.append(f'<text x="{f(tx)}" y="{f(ty - 2)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="50" '
                 f'fill="#ffffff">ВЫ ПОДПИСАНЫ</text>')
        k = ease_out(clamp(e / 0.18))
        p0, p1, p2 = (BX0 + 46, cy + dn), (BX0 + 66, cy + dn + 20), (BX0 + 104, cy + dn - 26)
        pts2 = [p0, p1] if k < 0.4 else [p0, p1, (p1[0] + (p2[0] - p1[0]) * (k - .4) / .6, p1[1] + (p2[1] - p1[1]) * (k - .4) / .6)]
        if k < 0.4:
            q = k / 0.4
            pts2 = [p0, (p0[0] + (p1[0] - p0[0]) * max(q, .05), p0[1] + (p1[1] - p0[1]) * max(q, .05))]
        s_ck = line(pts2, 12, "#ffffff", taper=.2, wmin=.6, seed=455)
        g.append(s_ck)
    s.append(f'<g transform="translate({f(cx)} {f(cy + dn)}) scale({pop:.4f}) translate({f(-cx)} {f(-cy - dn)})">{"".join(g)}</g>')
    return "".join(s)


HEARTS = [(-420, -760, -18, 1.25), (-250, -900, 8, 1.0), (-80, -980, -6, 1.4), (120, -860, 16, 1.1), (-520, -560, -22, 0.9),
          (200, -700, 20, 1.0), (-330, -1040, 2, 0.8), (40, -1100, 12, 0.85)]


def hearts(t):
    e = t - STAMP - 0.03
    if e < 0:
        return ""
    s = []
    ox, oy = BX1 - 120, BY0 + 10
    for k, (vx, vy, rot, sz) in enumerate(HEARTS):
        ee = e - k * 0.035
        if ee <= 0:
            continue
        x = ox + vx * ee * 1.1
        y = oy + vy * ee + 900 * ee * ee
        sc = sz * 4.4 * min(1.0, ee / 0.12) * (1 - smooth(0.55, 0.85, ee))
        if sc < 0.25:
            continue
        s.append(heart(x, y, sc, rot + 40 * ee * (1 if k % 2 else -1), 460 + k))
    return "".join(s)


def cat_pose(t):
    """(X, Y, s) кота, точка лапы (внутр.), press, look, blink, tilt."""
    sc = 1.08
    # s03: выглядывает из-за края (выезжает вбок на 3.3–3.66), s04: вылезает выше и тянется
    k1 = ease_out(clamp((t - 3.3) / 0.36))
    k2 = ease_io(clamp((t - 3.95) / 0.4))
    X = 1060 - 100 * k1 - 70 * k2
    Y = 1190 - 40 * k2 + 4 * math.sin(t * 2.4)
    # лапа: в s03 на краю карточки, в s04 — к кнопке
    edge_w = (CX1 + 6, 1050 - 10 * k2)
    btn_w = (BX1 - 78, BY0 + 80)
    ka = ease_io(clamp((t - 4.15) / (PRESS - 4.15)))
    lift = 40 * math.sin(math.pi * ka)
    tw = (edge_w[0] + (btn_w[0] - edge_w[0]) * ka, edge_w[1] + (btn_w[1] - edge_w[1]) * ka - lift)
    if t < 3.48:
        rest = cat.to_world(cat.PAW_REST, X, Y, sc)
        kk = ease_out(clamp((t - 3.32) / 0.16))
        tw = (rest[0] + (tw[0] - rest[0]) * kk, rest[1] + (tw[1] - rest[1]) * kk)
    press = 0.0
    e = t - PRESS
    if e >= 0:
        press = math.exp(-e * 8) * abs(math.sin(e * 24))
        tw = (tw[0], tw[1] + 16 * smooth(0, 0.05, e))
        ed = t - DONE
        if ed > 0:
            k3 = ease_io(clamp(ed / 0.3))
            tw = (tw[0] + 50 * k3, tw[1] - 16 + 70 * k3)
    P = cat.to_int(tw, X, Y, sc)
    # взгляд: на колокольчик, на кнопку, после нажатия — в камеру
    lk_b = (-0.9, -0.7)
    lk_btn = (-0.9, 0.2)
    k = smooth(3.95, 4.2, t)
    look = (lk_b[0] * (1 - k) + lk_btn[0] * k, lk_b[1] * (1 - k) + lk_btn[1] * k)
    kc = smooth(DONE + 0.05, DONE + 0.25, t)
    look = (look[0] * (1 - kc), look[1] * (1 - kc))
    tilt = -6 * k1 * (1 - k2) + 3 * k2 + 4 * kc * math.sin((t - DONE) * 3) * (t > DONE)
    blink = 0.0
    for c, half in ((3.86, 0.07), (5.4, 0.08), (6.6, 0.08)):
        if c - half <= t <= c + half:
            blink = 1 - abs(t - c) / half
    if t < 3.42:
        look = (-0.3, -0.2)
    return X, Y, sc, P, press, look, blink, tilt


def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        _ST["card"] = card_static()
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    X, Y, sc, P, press, look, blink, tilt = cat_pose(t)
    tail = 6 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1)
    flick = 0.0
    for c in (3.75, 5.85):
        e = t - c
        if 0 <= e < 0.5:
            flick += -14 * math.exp(-e * 9) * math.sin(e * 34)
    # влёт карточки 3.0–3.2 (хлёст), тень и кот — с ней
    u = clamp((t - 3.0) / (HIT - 3.0))
    k = ease_out(u, 3)
    dx = 640 * (1 - k)
    rot = 9 * (1 - k)
    e = t - HIT
    if e >= 0:
        rot += -2.2 * math.exp(-e * 6) * math.sin(e * 22)
    s = [_ST["bg"]]
    # свет от огонька кота на стене
    fx, fy = cat.flame_world(X, Y, sc, tail)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g = rad_grad([(0, "#ffb050", .38 * fl), (1, "#ffb050", 0)], fx + dx, fy, 280, 280)
    s.append(f'<rect x="{f(fx + dx - 300)}" y="{f(fy - 300)}" width="600" height="600" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    grp = []
    st = dict(look=look, blink=blink, tilt=tilt, tail=tail, flick=flick)
    grp.append(cat.draw(X, Y, sc, t, paw="none", **st))
    grp.append(_ST["card"])
    ang = 0.0
    cl = 0.0
    if e >= 0:
        ang = 22 * math.exp(-e * 1.3) * math.sin(2 * math.pi * 2.4 * e) + 3 * math.sin(t * 2.0)
        cl = -14 * math.exp(-e * 1.3) * math.sin(2 * math.pi * 2.4 * e - 0.9)
        e2 = t - STAMP
        if e2 >= 0:      # второй звяк на «верят»
            ang += 10 * math.exp(-e2 * 3) * math.sin(2 * math.pi * 2.6 * e2)
            cl += -7 * math.exp(-e2 * 3) * math.sin(2 * math.pi * 2.6 * e2 - 0.9)
    else:
        ang = 3 * math.sin(t * 2.0)
    grp.append(bell(ang, cl, t))
    grp.append(ring_strokes(t))
    grp.append(button(t))
    # лапа кота — поверх карточки (огибает край)
    grp.append(f'<g transform="translate({X - cat.CX * sc:.2f} {Y - cat.CBOT * sc:.2f}) scale({sc:.4f})">{cat.leg_left(P, press)}</g>')
    grp.append(hearts(t))
    s.append(f'<g transform="translate({f(dx)} 0) rotate({f(rot)} 540 1300)">{"".join(grp)}</g>')
    # штрихи скорости при влёте
    if 0 < u < 1:
        for j in range(6):
            yy = 520 + j * 130
            x0 = CX0 + dx - 40 - (j % 2) * 60
            ln = 380 * (1 - k)
            s.append(line([(x0 + 40, yy), (x0 + 40 + ln, yy + 4)], 9 * (1 - k) + 2, INK, taper=.6, seed=480 + j))
    # камера: лёгкий наезд, удар на влёте и толчок на нажатии
    v = clamp((t - 3.0) / (6.84 - 3.0))
    ccx, ccy = 590 + 15 * v, 920 - 20 * v
    scc = 1.0 + 0.05 * ease_io(v) + 0.01 * v
    if e >= 0:
        kk = math.exp(-e * 7)
        scc *= 1 + 0.05 * kk
        ccy += 8 * kk * math.sin(e * 40)
    ep = t - PRESS
    if ep >= 0:
        kk = math.exp(-ep * 8)
        scc *= 1 + 0.045 * kk * math.sin(min(ep * 14, math.pi))
        ccx += 7 * kk * math.sin(ep * 47)
        ccy += 9 * kk * math.sin(ep * 39)
    ed = t - STAMP
    if ed >= 0:
        kk = math.exp(-ed * 8)
        scc *= 1 + 0.05 * kk * math.sin(min(ed * 14, math.pi))
        ccy += 6 * kk * math.sin(ed * 42)
    crot = 0.6 * math.sin(t * 0.9)
    return svg(f'<rect width="{W}" height="{H}" fill="#e6a862"/><g transform="{cam(ccx, ccy, scc, crot)}">{"".join(s)}</g>')
