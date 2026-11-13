"""Карточка подписки рилса 35 (сцена sub; основа — scene_sub рилса 31).
s03: кремовая карточка на столе у обойной стены: большой золотой колокольчик качается с первого кадра и звенит на
«Подпишись» (3.88) — штрихи звона; ниже красная кнопка «ПОДПИСАТЬСЯ»; сбоку на столе маленький розовый мозг машет ручкой.
s04: лапа кота снизу-справа жмёт кнопку на «мифы» (5.32) и держит; на «верят» (6.40) кнопка серая с галочкой,
вылетают сердечки, мозг подпрыгивает от радости, колокольчик ещё раз звякает."""
import math

import cat
import minibrain
import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg, T)
from ink import fur
from parts import sausage

_ST = {}
RING = 3.88
PRESS = 5.32
DONE = 6.40
CARD = (110, 250, 870, 1192)
BELL = (490, 560)          # центр купола колокольчика
BELL_PIV = (490, 355)      # точка подвеса
BTN = (180, 820, 800, 972)
BRAIN = (215, 1132, 0.46)   # центр мозга на столе, масштаб
DESK = 1192


def backdrop():
    s = []
    s.append(f'<rect x="-1200" y="-1500" width="3500" height="{DESK + 1500}" fill="#ecd7ae"/>')
    DEFS.append('<pattern id="pWall31" width="120" height="120" patternUnits="userSpaceOnUse">'
                '<rect width="120" height="120" fill="#ecd7ae"/><rect x="0" width="38" height="120" fill="#e5cda1"/>'
                '<circle cx="80" cy="30" r="5" fill="#dcc193"/><circle cx="80" cy="90" r="5" fill="#dcc193"/></pattern>')
    s.append(f'<rect x="-1200" y="-1500" width="3500" height="{DESK + 1500}" fill="url(#pWall31)"/>')
    # рамка с картинкой на стене (обжито)
    s.append(shape(rect_pts(-260, 120, -40, 380, 8), "#9a6a3e", shape(rect_pts(-236, 144, -64, 356, 4), "#cfe3d6",
                   blob([(-236, 300), (-180, 250), (-120, 290), (-64, 240), (-64, 356), (-236, 356)], "#8fb59a"), w=3, seed=31), w=4.4, seed=30))
    # стол
    s.append(shape([(-1200, DESK - 30, 1), (2300, DESK - 30, 1), (2300, DESK + 34, 1), (-1200, DESK + 34, 1)], "#c98f5a",
                   blob(rect_pts(-1200, DESK - 30, 2300, DESK - 14), "#b27a48", .8), w=4.6, seed=33))
    s.append(shape(rect_pts(-1200, DESK + 34, 2300, 2600), "#a8723f",
                   "".join(line([(-1200, DESK + 80 + k * 60), (2300, DESK + 86 + k * 60)], 2.4, "#8f5e31", taper=.1, wmin=.7, seed=34 + k, op=.8)
                           for k in range(8)), w=4.6, seed=39))
    return "".join(s)


def light():
    g = rad_grad([(0, "#fff1c8", .45), (.6, "#ffe3a0", .12), (1, "#ffe3a0", 0)], 420, 520, 1100, 1100)
    s = [f'<rect x="-1200" y="-1500" width="3500" height="4500" fill="url(#{g})" style="mix-blend-mode:screen"/>']
    g2 = rad_grad([(0, "#000000", 0), (.65, "#000000", 0), (1, "#2a1606", .3)], 480, 800, 1300, 1300)
    s.append(f'<rect x="-1200" y="-1500" width="3500" height="4500" fill="url(#{g2})"/>')
    return "".join(s)


def card():
    x0, y0, x1, y1 = CARD
    s = [blob(rect_pts(x0 + 26, y1 - 18, x1 + 40, y1 + 14, 8), "#2a1606", .4, blur(12))]
    s.append(blob(rect_pts(x0 + 18, y0 + 22, x1 + 18, y1 + 6, 58), "#c7a879"))
    inner = blob(rect_pts(x1 - 60, y0, x1, y1), "#efe2c6", .9)
    inner += blob(rect_pts(x0, y0, x1, y0 + 26), "#fffaf0", .9)
    s.append(shape(rect_pts(x0, y0, x1, y1, 56), "#fbf2de", inner, w=5.6, seed=40))
    # пунктирная рамочка внутри
    pts = rect_pts(x0 + 34, y0 + 34, x1 - 34, y1 - 34, 32)
    S = lib.sample(pts, True, 3)
    for k in range(0, len(S) - 6, 14):
        s.append(line([tuple(S[k]), tuple(S[k + 6])], 3, "#d9c49c", taper=.2, wmin=.6, seed=41 + k))
    # искорки у колокольчика
    for k, (x, y, r) in enumerate([(230, 420, 20), (770, 380, 16), (740, 650, 12)]):
        s.append(star(x, y, r, "#f2b43a", 60 + k))
    return "".join(s)


def star(x, y, r, col, sd, rot=0.0):
    pts = []
    for k in range(8):
        a = math.radians(rot + k * 45 - 90)
        rr = r if k % 2 == 0 else r * 0.38
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return shape(pts, col, "", w=2.6, seed=sd)


def bell_angle(t):
    """Покачивание с первого кадра + удар на «Подпишись» + маленький звяк на «мифов»."""
    a = 4.0 * math.sin((t - 3.36) * 5.2)
    e = t - (RING - 0.06)
    if e > 0:
        a = a * math.exp(-e * 3) + 22 * math.exp(-e * 2.6) * math.sin(e * 15)
    e2 = t - DONE
    if e2 > 0:
        a += 9 * math.exp(-e2 * 4) * math.sin(e2 * 18)
    return a


def bell(t):
    ang = bell_angle(t)
    px, py = BELL_PIV
    cx, cy = BELL
    s = []
    # язычок отстаёт от купола
    cl = ang * 0.45 + (6 * math.sin((t - RING) * 15 - 1) * math.exp(-(t - RING) * 3) if t > RING else 0)
    g = [f'<g transform="rotate({f(ang)} {px} {py})">']
    g.append(f'<g transform="rotate({f(cl - ang)} {cx} {cy + 70})">' +
             line([(cx, cy + 60), (cx, cy + 150)], 10, INK, taper=.05, wmin=.9, seed=70) +
             shape(ellipse_pts(cx, cy + 160, 30, 28, 14), "#c98a26", blob(ellipse_pts(cx + 8, cy + 166, 20, 18, 10), "#a46d16"), w=4.6, seed=71) +
             "</g>")
    # ушко
    g.append(shape(ellipse_pts(px, py + 14, 26, 26, 14), "#d89a2c", blob(ellipse_pts(px, py + 14, 12, 12, 10), "#fbf2de"), w=4.6, seed=72))
    dome = [(cx - 20, cy - 196), (cx + 20, cy - 196), (cx + 74, cy - 170), (cx + 112, cy - 100), (cx + 126, cy), (cx + 150, cy + 76),
            (cx + 196, cy + 112, 1), (cx + 186, cy + 140, 1), (cx - 186, cy + 140, 1), (cx - 196, cy + 112, 1), (cx - 150, cy + 76),
            (cx - 126, cy), (cx - 112, cy - 100), (cx - 74, cy - 170)]
    inner = blob([(cx + 40, cy - 200), (cx + 200, cy - 200), (cx + 200, cy + 150), (cx + 110, cy + 150), (cx + 90, cy + 40), (cx + 70, cy - 80)],
                 "#d48f20", .95)
    inner += blob([(cx - 92, cy - 120), (cx - 70, cy - 150), (cx - 54, cy - 60), (cx - 74, cy + 40), (cx - 100, cy + 30)], "#ffe28a", .95)
    inner += blob([(cx - 200, cy + 92), (cx + 200, cy + 92), (cx + 200, cy + 150), (cx - 200, cy + 150)], "#c47f18", .95)
    g.append(shape(dome, "#f2b43a", inner, w=5.6, seed=73))
    g.append(line([(cx - 160, cy + 92), (cx, cy + 98), (cx + 160, cy + 92)], 3.6, "#a46d16", seed=74, op=.9))
    g.append("</g>")
    s.append("".join(g))
    # штрихи звона: на ударе и на звяке
    for t0, amp, n in ((RING, 1.0, 3), (DONE, 0.7, 2)):
        e = t - t0
        if 0 <= e < 0.7:
            a = 1 - e / 0.7
            for side in (-1, 1):
                for k in range(n):
                    r = 230 + k * 46 + 80 * ease_out(e / 0.7)
                    a0, a1 = (-30 - k * 4, 20 + k * 4)
                    pts = [(cx + side * r * math.cos(math.radians(q)), cy - 20 + r * math.sin(math.radians(q)))
                           for q in [a0 + (a1 - a0) * j / 5 for j in range(6)]]
                    s.append(line(pts, (10 - k * 2) * a * amp + 1.5, INK, taper=.7, wmin=.1, seed=80 + k + side))
    return "".join(s)


def button(t):
    x0, y0, x1, y1 = BTN
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hold = smooth(PRESS - 0.04, PRESS + 0.03, t) * (1 - smooth(DONE - 0.04, DONE + 0.02, t))
    done = t >= DONE
    dy = 9 * hold
    pop = 1.0
    if done:
        e = t - DONE
        pop = 1 + 0.08 * math.exp(-e * 7) * math.sin(e * 20 + 0.6) + 0.04 * math.exp(-e * 12)
    col, col_d, col_l = ("#e5383b", "#a91f25", "#ff7a6e") if not done else ("#c9c5bd", "#9b968c", "#e4e1da")
    s = [blob(rect_pts(x0 + 8, y0 + 22, x1 + 8, y1 + 22, 70), "#2a1606", .28 * (1 - .6 * hold), blur(10))]
    g = []
    g.append(shape(rect_pts(x0, y0 + 16, x1, y1 + 16, 70), col_d, "", w=5, seed=90))
    inner = blob(rect_pts(x0, y0 + 10, x1, y0 + 34, 20), col_l, .9)
    inner += blob(rect_pts(x0, y1 - 26 + dy, x1, y1 + dy), col_d, .8)
    g.append(shape(rect_pts(x0, y0 + dy, x1, y1 + dy, 70), col, inner, w=5.4, seed=91))
    if not done:
        g.append(f'<text x="{f(cx - 42)}" y="{f(cy + 22 + dy)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="60" '
                 f'letter-spacing="1" fill="#fff8ee">ПОДПИСАТЬСЯ</text>')
    else:
        e = t - DONE
        k = ease_out(clamp(e / 0.18))
        chk = [(x0 + 66, cy + 4), (x0 + 92, cy + 30), (x0 + 140, cy - 28)]
        if k > 0:
            n = 1 + k * 1.999
            i = int(n)
            pts = chk[:i] + ([tuple(chk[i - 1][j] + (chk[min(i, 2)][j] - chk[i - 1][j]) * (n - i) for j in (0, 1))] if i < 3 else [])
            g.append(line(pts, 15, "#3f3a33", taper=.15, wmin=.7, seed=95))
        g.append(f'<text x="{f(cx + 62)}" y="{f(cy + 17)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="46" '
                 f'letter-spacing="1" fill="#4a453d" opacity="{min(1, .3 + k):.3f}">ВЫ ПОДПИСАНЫ</text>')
    s.append(f'<g transform="translate({f(cx)} {f(cy)}) scale({pop:.4f}) translate({f(-cx)} {f(-cy)})">{"".join(g)}</g>')
    return "".join(s)


def heart(x, y, r, col, sd, rot=0.0):
    pts = []
    for k in range(20):
        a = 2 * math.pi * k / 20
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((hx / 16 * r, hy / 16 * r + r * 0.15) + ((1,) if k == 0 or k == 10 else ()))
    pts = T(pts, x, y, 1.0, rot)
    return shape(pts, col, blob(T([(-r * .55, -r * .45), (-r * .2, -r * .7), (-r * .1, -r * .4), (-r * .4, -r * .2)], x, y, 1, rot), "#ffffff", .55),
                 w=3.6, seed=sd)


def hearts(t):
    e = t - DONE
    if e < 0:
        return ""
    s = []
    cx, cy = (BTN[0] + BTN[2]) / 2, BTN[1] + 20
    spec = [(-300, -520, 46, "#ff5a6e", 0.0), (-120, -640, 38, "#ff8fa0", .06), (90, -600, 52, "#ff5a6e", .03), (260, -500, 36, "#ff8fa0", .1),
            (-220, -330, 30, "#ff5a6e", .14), (200, -320, 34, "#ff5a6e", .18), (20, -420, 28, "#ff8fa0", .2)]
    for k, (dx, dy, r, col, d) in enumerate(spec):
        u = (e - d) / 0.95
        if u <= 0:
            continue
        p = ease_out(clamp(u), 2.5)
        sc = back_out(clamp(u / 0.35), 2.2) * (1 - smooth(0.75, 1.15, u))
        if sc <= 0.02:
            continue
        x = cx + dx * p + 10 * math.sin(e * 7 + k)
        y = cy + dy * p
        s.append(heart(x, y, r * sc, col, 100 + k, rot=dx * 0.04 * (1 - p) + 8 * math.sin(e * 5 + k)))
    return "".join(s)


def mini_brain(t):
    """Мозг на столе слева: машет правой ручкой с первого кадра (на «Подпишись» — шире), моргает; на «верят» —
    подпрыгивает и радуется, смотрит на кнопку."""
    x, y, sc = BRAIN
    wave = t * 9.0
    e = t - DONE
    hop = 0.0
    if 0 <= e < 0.6:
        hop = 70 * math.sin(math.pi * clamp(e / 0.45)) if e < 0.45 else 0.0
    bob = 4 * math.sin(t * 4.5)
    look = (0.7, 0.4) if t < PRESS - 0.3 else (0.9, 0.9)
    bl = 0.0
    for tb in (3.7, 4.95, 5.95, 6.9):
        u = (t - tb) / 0.16
        if 0 <= u <= 1:
            bl = math.sin(math.pi * u)
    rot = -6 * math.sin(t * 4.5 + .5)
    sh = blob(ellipse_pts(x + 6, DESK - 26, 90 * (1 - hop / 200), 12, 14), "#2a1606", .3, blur(6))
    return sh + minibrain.draw(x, y - hop + bob, sc, t, wave=wave, look=look, blink=bl, rot=rot)


PRESS_PT = (BTN[2] - 18, (BTN[1] + BTN[3]) / 2 + 8)


def paw(t):
    """Передняя лапа кота справа-снизу: пушистая лапа с круглой «варежкой» на конце; подход дугой, нажатие (сжатие),
    держит до «мифов», отпускает и уходит вниз-вправо."""
    if t < PRESS - 0.45:
        return ""
    tx, ty = PRESS_PT
    a = PRESS - 0.45
    u = clamp((t - a) / 0.45)
    k = ease_out(u, 2.4)
    sx, sy = 1300, 1560
    px = sx + (tx - sx) * k
    py = sy + (ty - sy) * k - 80 * math.sin(math.pi * k) * (1 - k)
    press = 0.0
    if t >= PRESS:
        press = smooth(PRESS, PRESS + 0.05, t) * (1 - smooth(DONE - 0.02, DONE + 0.1, t))
        py += 9 * press
    if t > DONE:
        e = t - DONE
        r = ease_in(clamp((e - 0.04) / 0.5), 2)
        px += 380 * r
        py += 640 * r - 40 * math.sin(math.pi * clamp(e / 0.3)) * (1 - r)
    c = cat
    base = (1380, 1640)
    dx, dy = px - base[0], py - base[1]
    L = math.hypot(dx, dy) + 1e-9
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    wr = (px - ux * 70, py - uy * 70)                       # запястье
    mid = ((base[0] + wr[0]) / 2 + nx * 18, (base[1] + wr[1]) / 2 + ny * 18)
    leg = sausage([base, mid, wr], 210, 150)
    legf = fur(leg, 5, 14, seed=611)
    s = []
    inner = blob([(base[0] - nx * 10, base[1] - ny * 10), (wr[0] - nx * 4, wr[1] - ny * 4), (wr[0] - nx * 90, wr[1] - ny * 90),
                  (base[0] - nx * 140, base[1] - ny * 140)], c.CAT_SH, .75)
    for j in range(5):
        q = (wr[0] - ux * (70 + 80 * j) + nx * (20 * ((j % 3) - 1)), wr[1] - uy * (70 + 80 * j) + ny * (20 * ((j % 3) - 1)))
        inner += line([q, (q[0] + ux * 22 + nx * 6, q[1] + uy * 22 + ny * 6)], 2.6, c.CAT_EDGE, seed=600 + j, op=.85)
    s.append(shape(legf, c.CAT, inner, w=5.4, seed=610))
    # шерстинки по краям ноги
    for j in range(6):
        sd_ = 1 if j % 2 else -1
        dd = 60 + 70 * j
        hw = 75 + 30 * min(1.0, dd / max(L - 70, 1)) - 3
        q = (wr[0] - ux * dd + nx * sd_ * hw, wr[1] - uy * dd + ny * sd_ * hw)
        s.append(line([(q[0] - ux * 14, q[1] - uy * 14), (q[0] + nx * sd_ * 12 - ux * 2, q[1] + ny * sd_ * 12 - uy * 2)], 4.4, INK,
                      taper=.6, wmin=.2, seed=640 + j))
    # «варежка» лапы: округлая, на переднем крае три пальца-бугорка; сплющена нажатием
    ang = math.degrees(math.atan2(uy, ux))
    sq = 1 - 0.07 * press
    pp = [(-70, -70), (-10, -84), (30, -78), (52, -58, 1), (78, -40), (82, -16), (66, -6, 1), (88, 8), (88, 30), (66, 40, 1),
          (80, 56), (70, 76), (36, 84), (-20, 86), (-74, 66)]
    pp = [((p[0] * sq), p[1] * (2 - sq)) + tuple(p[2:]) for p in pp]
    cxp, cyp = px - ux * 30, py - uy * 30
    pw = T(pp, cxp, cyp, 1.0, ang)
    pin = blob(T([(-60, 30), (40, 40), (70, 70), (-50, 84)], cxp, cyp, 1, ang), c.CAT_SH, .7)
    pin += line(T([(-30, -60), (10, -66)], cxp, cyp, 1, ang), 3, c.CAT_EDGE, seed=614, op=.8)
    s.append(shape(pw, c.CAT, pin, w=5.2, seed=613))
    return "".join(s)


def ripple(t):
    e = t - PRESS
    if e < 0 or e > 0.6:
        return ""
    cx, cy = PRESS_PT
    a = 1 - e / 0.6
    s = []
    for k in range(6):
        ang = math.radians(-160 + k * 28)
        r0 = 90 + 120 * ease_out(e / 0.6)
        s.append(line([(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0), (cx + math.cos(ang) * (r0 + 46 * a), cy + math.sin(ang) * (r0 + 46 * a))],
                      9 * a + 1, INK, taper=.6, seed=650 + k))
    return "".join(s)


def frame(sid, t):
    if not _ST:
        _ST["bg"] = backdrop()
        _ST["card"] = card()
        _ST["light"] = light()
        minibrain.body()
        lib.static_done()
    lib.dyn_begin()
    s = [_ST["bg"], _ST["card"], bell(t), button(t)]
    s.append(mini_brain(t))
    s.append(ripple(t))
    s.append(paw(t))
    s.append(hearts(t))
    s.append(_ST["light"])
    if sid == "s03":
        u = clamp((t - 3.55) / 1.75)
        cx, cy = 500 + 10 * u, 830 - 30 * ease_io(u)
        sc = 1.02 + 0.08 * (0.3 * u + 0.7 * ease_io(u))
        rot = -1.2 + 1.4 * u
        e = t - RING
        if e > 0:
            kk = math.exp(-e * 8)
            cx += 7 * kk * math.sin(e * 46)
            sc *= 1 + 0.025 * kk
    else:
        u = clamp((t - 4.9) / 2.25)
        cx, cy = 540 - 10 * u, 880 + 10 * u
        sc = 1.06 + 0.04 * u
        rot = 0.6 * math.sin(t * 1.3)
        for t0, amp in ((PRESS, 0.05), (DONE, 0.035)):
            e = t - t0
            if e > 0:
                kk = math.exp(-e * 9)
                sc *= 1 + amp * kk * math.sin(min(e * 14, math.pi))
                cy += 6 * kk * math.sin(e * 50)
    return svg(f'<rect width="{W}" height="{H}" fill="#ecd7ae"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')
