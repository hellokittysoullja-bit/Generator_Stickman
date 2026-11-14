"""Карточка подписки рилса 42 (копия scene_sub рилса 39, своё время и свои движения; хлёст въезда делает сборщик).
s03 (клип 3.0–4.8): колокольчик качается с первого кадра, на «Подпишись» (3.36) подпрыгивает и звенит — штрихи звона;
под ним красная кнопка «ПОДПИСАТЬСЯ». Кот запрыгивает справа дугой с кадра 0, приземляется у края карточки (сжатие),
кладёт лапу на край.
s04 (клип 4.4–6.7): кот вылезает сильнее, тянет лапу к кнопке, на «кончится» (5.24) кнопка вдавливается и становится
серой «ВЫ ПОДПИСАНЫ» с галочкой, фонтаном вылетают сердечки и искры, колокольчик ещё раз звякает; толчок камеры."""
import math

import cat
import lib
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg, T)

_ST = {}
HIT = 3.36          # «Подпишись»
PRESS = 5.24        # «кончится»
T_A, T_B = 3.0, 6.7
LAND = 3.3          # кот приземлился
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


def bell(ang, cl, t, dy=0.0):
    """Колокольчик: подвес в BELL (+dy — подскок), угол ang, язычок отстаёт (cl)."""
    x, y = BELL[0], BELL[1] + dy
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
    e = t - PRESS
    dn = 0.0
    on = e >= 0.03
    if e >= 0:
        dn = 16 * math.exp(-e * 14) * (1 if e < 0.06 else 1) if e < 0.06 else 16 * math.exp(-(e - 0.06) * 9) + 5 * (1 - math.exp(-(e - 0.06) * 9))
        dn = min(16.0, dn)
    pop = 1.0
    if on:
        pop = 1 + 0.06 * math.exp(-(e - 0.03) * 7) * math.sin((e - 0.03) * 26)
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
        k = ease_out(clamp((e - 0.03) / 0.18))
        p0, p1, p2 = (BX0 + 46, cy + dn), (BX0 + 66, cy + dn + 20), (BX0 + 104, cy + dn - 26)
        pts2 = [p0, p1] if k < 0.4 else [p0, p1, (p1[0] + (p2[0] - p1[0]) * (k - .4) / .6, p1[1] + (p2[1] - p1[1]) * (k - .4) / .6)]
        if k < 0.4:
            q = k / 0.4
            pts2 = [p0, (p0[0] + (p1[0] - p0[0]) * max(q, .05), p0[1] + (p1[1] - p0[1]) * max(q, .05))]
        s_ck = line(pts2, 12, "#ffffff", taper=.2, wmin=.6, seed=455)
        g.append(s_ck)
    s.append(f'<g transform="translate({f(cx)} {f(cy + dn)}) scale({pop:.4f}) translate({f(-cx)} {f(-cy - dn)})">{"".join(g)}</g>')
    return "".join(s)


# сердечки фонтаном из кнопки: (угол от вертикали, скорость, поворот, размер)
HEARTS = [(-38, 1180, -18, 1.2), (-22, 1320, 8, 1.0), (-6, 1420, -6, 1.35), (10, 1300, 16, 1.05), (26, 1220, -12, 0.9),
          (42, 1050, 20, 1.0), (-50, 950, 2, 0.8), (18, 1500, 12, 0.85), (-30, 1500, -4, 0.75)]
# искры-звёздочки: (угол, дальность, размер)
SPARKS = [(-150, 260, 1.0), (-110, 320, .8), (-70, 300, 1.1), (-35, 340, .85), (-5, 280, 1.0), (25, 200, .7)]


def hearts(t):
    """Сердечки бьют фонтаном вверх из кнопки, тормозят, падают по дуге и тают; каждое крутится в свою сторону."""
    e = t - PRESS - 0.03
    if e < 0:
        return ""
    s = []
    ox, oy = (BX0 + BX1) / 2 + 40, BY0 + 10
    for k, (ang, v, rot, sz) in enumerate(HEARTS):
        ee = e - k * 0.03
        if ee <= 0:
            continue
        a = math.radians(ang)
        x = ox + math.sin(a) * v * ee * 1.05 + 14 * math.sin(ee * 6 + k)
        y = oy - math.cos(a) * v * ee + 1150 * ee * ee
        sc = sz * 4.2 * back_pop(ee) * (1 - smooth(0.75, 1.05, ee))
        if sc < 0.25:
            continue
        s.append(heart(x, y, sc, rot + 70 * ee * (1 if k % 2 else -1), 460 + k))
    return "".join(s)


def back_pop(ee):
    u = clamp(ee / 0.14)
    return 1 + 0.25 * math.sin(math.pi * u) if u < 1 else 1.0


def spark(x, y, r, rot, sd, col="#ffe27a"):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.36
        a = math.radians(rot + i * 45 - 90)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, col, "", w=max(2.0, r * 0.09), seed=sd)


def sparks(t):
    """Искры брызгают из-под лапы в момент нажатия и гаснут за 0.5 с."""
    e = t - PRESS
    if e < 0 or e > 0.6:
        return ""
    s = []
    ox, oy = (BX0 + BX1) / 2 + 60, BY0 + 30
    for k, (ang, dist, sz) in enumerate(SPARKS):
        p = 1 - math.exp(-e * 9)
        a = math.radians(ang - 90)
        r = 56 * sz * math.sin(math.pi * clamp(e / 0.55)) ** 0.6
        if r < 2:
            continue
        s.append(spark(ox + math.cos(a) * dist * p, oy + math.sin(a) * dist * p, r, 30 * e * (k - 2.5), 470 + k,
                       "#ffe27a" if k % 2 else "#fff4c2"))
    return "".join(s)


def cat_pose(t):
    """(X, Y, s) кота, точка лапы (внутр.), press, look, blink, tilt, (squash, lean) — прыжок и приземление."""
    sc = 1.08
    # s03: запрыгивает справа дугой с первого кадра и приземляется к LAND; s04: вылезает выше и тянется
    k1 = clamp((t - T_A) / (LAND - T_A))
    k2 = ease_io(clamp((t - 4.55) / 0.45))
    X = 1250 - 290 * ease_out(k1, 1.7) - 30 * k2
    hop = 170 * math.sin(math.pi * k1) if k1 < 1 else 0.0
    Y = 1190 - hop - 40 * k2 + 4 * math.sin(t * 2.4)
    el = t - LAND
    sq = 0.09 * math.exp(-el * 9) * math.cos(el * 26) if el >= 0 else -0.05 * math.sin(math.pi * k1)
    lean = -9 * math.sin(math.pi * k1) if k1 < 1 else 0.0
    # лапа: в s03 на краю карточки, в s04 — к кнопке
    edge_w = (CX1 + 6, 1050 - 10 * k2)
    btn_w = (BX1 - 34, BY0 + 82)
    ka = ease_io(clamp((t - 4.78) / (PRESS - 4.78)))
    lift = 46 * math.sin(math.pi * ka)
    tw = (edge_w[0] + (btn_w[0] - edge_w[0]) * ka, edge_w[1] + (btn_w[1] - edge_w[1]) * ka - lift)
    if t < 3.66:
        rest = cat.to_world(cat.PAW_REST, X, Y, sc)
        kk = ease_out(clamp((t - 3.44) / 0.22))
        tw = (rest[0] + (tw[0] - rest[0]) * kk, rest[1] + (tw[1] - rest[1]) * kk)
    press = 0.0
    e = t - PRESS
    if e >= 0:
        press = math.exp(-e * 8) * abs(math.sin(e * 24))
        tw = (tw[0], tw[1] + 16 * math.exp(-e * 14) + 5)
        if e > 0.32:
            k3 = ease_io(clamp((e - 0.32) / 0.4))
            back = (edge_w[0] + 4, edge_w[1] + 40)          # лапа уходит назад на край карточки, кнопку не закрывает
            tw = (tw[0] + (back[0] - tw[0]) * k3, tw[1] + (back[1] - tw[1]) * k3 - 30 * math.sin(math.pi * k3))
    P = cat.to_int(tw, X, Y, sc)
    # взгляд: на колокольчик, на кнопку, после нажатия — в камеру
    lk_b = (-0.9, -0.7)
    lk_btn = (-0.9, 0.2)
    k = smooth(4.55, 4.8, t)
    look = (lk_b[0] * (1 - k) + lk_btn[0] * k, lk_b[1] * (1 - k) + lk_btn[1] * k)
    kc = smooth(PRESS + 0.25, PRESS + 0.45, t)
    look = (look[0] * (1 - kc), look[1] * (1 - kc))
    tilt = -6 * smooth(LAND, LAND + 0.2, t) * (1 - k2) + 3 * k2 + 5 * kc * math.sin((t - PRESS) * 3) * (t > PRESS)
    blink = 0.0
    for c, half in ((4.15, 0.07), (6.3, 0.08)):
        if c - half <= t <= c + half:
            blink = 1 - abs(t - c) / half
    return X, Y, sc, P, press, look, blink, tilt, (sq, lean)


def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        _ST["card"] = card_static()
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    X, Y, sc, P, press, look, blink, tilt, (sq, lean) = cat_pose(t)
    hopg = (f'translate({X:.2f} {Y:.2f}) rotate({lean:.2f}) scale({1 + 0.6 * sq:.4f} {1 - sq:.4f}) translate({-X:.2f} {-Y:.2f})')
    tail = 6 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1)
    flick = 0.0
    for c in (LAND + 0.05, 4.7, PRESS + 0.1):
        e = t - c
        if 0 <= e < 0.5:
            flick += -14 * math.exp(-e * 9) * math.sin(e * 34)
    e = t - HIT
    rot = 0.0
    if e >= 0:
        rot += -1.6 * math.exp(-e * 6) * math.sin(e * 22)
    s = [_ST["bg"]]
    # свет от огонька кота на стене
    fx, fy = cat.flame_world(X, Y, sc, tail)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g = rad_grad([(0, "#ffb050", .38 * fl), (1, "#ffb050", 0)], fx, fy, 280, 280)
    s.append(f'<rect x="{f(fx - 300)}" y="{f(fy - 300)}" width="600" height="600" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    grp = []
    st = dict(look=look, blink=blink, tilt=tilt, tail=tail, flick=flick)
    grp.append(f'<g transform="{hopg}">{cat.draw(X, Y, sc, t, paw="none", **st)}</g>')
    grp.append(_ST["card"])
    # колокольчик: качается с первого кадра, удар на «Подпишись», звяк на нажатии
    ang = 7 * math.sin((t - T_A) * 5.0 + 1.2)
    cl = -4 * math.sin((t - T_A) * 5.0 + 0.3)
    if e >= 0:
        ang = ang * math.exp(-e * 3) + 22 * math.exp(-e * 1.3) * math.sin(2 * math.pi * 2.4 * e) + 3 * math.sin(t * 2.0)
        cl = cl * math.exp(-e * 3) - 14 * math.exp(-e * 1.3) * math.sin(2 * math.pi * 2.4 * e - 0.9)
    ep = t - PRESS
    if ep >= 0:
        ang += 10 * math.exp(-ep * 3) * math.sin(ep * 16)
        cl += -7 * math.exp(-ep * 3) * math.sin(ep * 16 - 0.9)
    bdy = 0.0
    if e >= 0:   # на «Подпишись» колокольчик подпрыгивает и падает обратно с отскоком
        bdy = -30 * math.sin(math.pi * clamp(e / 0.2)) if e < 0.2 else -10 * math.exp(-(e - 0.2) * 7) * abs(math.sin((e - 0.2) * 16))
    grp.append(bell(ang, cl, t, bdy))
    grp.append(ring_strokes(t))
    grp.append(button(t))
    # лапа кота — поверх карточки (огибает край)
    grp.append(f'<g transform="{hopg}"><g transform="translate({X - cat.CX * sc:.2f} {Y - cat.CBOT * sc:.2f}) scale({sc:.4f})">'
               f'{cat.leg_left(P, press)}</g></g>')
    grp.append(sparks(t))
    grp.append(hearts(t))
    s.append(f'<g transform="rotate({f(rot)} 540 1300)">{"".join(grp)}</g>')
    # камера: лёгкий наезд с первого кадра, удар на звоне и толчок на нажатии
    v = clamp((t - T_A) / (T_B - T_A))
    ccx, ccy = 585 + 18 * v, 905 - 25 * v
    scc = 1.0 + 0.055 * (0.35 * v + 0.65 * ease_io(v))
    if e >= 0:
        kk = math.exp(-e * 7)
        scc *= 1 + 0.05 * kk
        ccy += 8 * kk * math.sin(e * 40)
    if ep >= 0:
        kk = math.exp(-ep * 8)
        scc *= 1 + 0.045 * kk * math.sin(min(ep * 14, math.pi))
        ccx += 7 * kk * math.sin(ep * 47)
        ccy += 9 * kk * math.sin(ep * 39)
    crot = 0.6 * math.sin(t * 0.9)
    return svg(f'<rect width="{W}" height="{H}" fill="#e6a862"/><g transform="{cam(ccx, ccy, scc, crot)}">{"".join(s)}</g>')
