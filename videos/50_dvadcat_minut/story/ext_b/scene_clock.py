"""Большие часы рилса 50 (s05, 7.08–8.4): стрелки бешено крутятся 14:00 -> 17:00 на «три часа» (7.40–8.0), за часами темнеет.
(Заготовки night_bg/tiles/clock — из рилса 29.)
Старые тексты рилса 29:
s09 (12.36–14.4): ночь, тёмно-синяя плитка кухни, тёплый отсвет лампы. Стрелки бегут и щёлкают на 1:00 на «час» (12.52),
наезд-удар; потом минутная делает круг, часовая доходит до 2.
s14 (22.76–24.2): утро, светлая плитка, солнечный луч. Часы показывают 9:40; на «опоздал» (22.88) минутная дёргается,
часы подскакивают на гвозде, справа хлопает входная дверь (штрихи удара), по полу катится клубок пыли."""
import math

import lib
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg, T)

_ST = {}
CC = (500, 700)     # центр часов
R = 300
HIT9 = 12.52        # «час»
HIT14 = 22.88       # «опоздал»
FLOOR = 1000        # линия пола в s14
DOOR_X = 830        # левый край дверного проёма в s14


def tiles(night):
    s = []
    if night:
        base, grout, hi = "#22305a", "#141c36", "#2c3c6c"
    else:
        base, grout, hi = "#f1e6cc", "#d4c3a0", "#fbf3e0"
    s.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="{base}"/>')
    tw, th = 150, 150
    for j in range(-6, 22):
        for i in range(-6, 14):
            x, y = i * tw, j * th
            s.append(f'<rect x="{x + 8}" y="{y + 8}" width="20" height="{th - 26}" fill="{hi}"/>')
    for j in range(-6, 22):
        s.append(f'<rect x="-900" y="{j * th - 3}" width="2900" height="6" fill="{grout}"/>')
    for i in range(-6, 14):
        s.append(f'<rect x="{i * tw - 3}" y="-900" width="6" height="3800" fill="{grout}"/>')
    return "".join(s)


def night_bg():
    s = [tiles(True)]
    # абажур лампы сверху слева (край кадра) и тёплый отсвет
    s.append(line([(80, -900), (80, -40)], 6, INK, taper=.05, wmin=.9, seed=601))
    sh = [(-80, 60, 1), (240, 60, 1), (170, -40), (-10, -40)]
    s.append(shape(sh, "#d9773a", blob([(110, -40), (170, -40), (240, 60), (150, 60)], "#b85a26"), w=5, seed=602))
    s.append(blob(ellipse_pts(80, 62, 70, 16, 14), "#ffe7a6"))
    g = rad_grad([(0, "#ffcf7a", .62), (.45, "#ffaa50", .25), (1, "#ffaa50", 0)], 120, 120, 1100, 1000)
    s.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    g2 = rad_grad([(0, "#000000", 0), (.55, "#000000", 0), (1, "#05070f", .55)], 400, 700, 1400, 1500)
    s.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g2})"/>')
    # край шкафчика внизу (столешница), чтобы стена не висела в пустоте
    s.append(shape(rect_pts(-900, 1260, 2000, 1300), "#7a4f2c", "", w=5, seed=603))
    s.append(shape(rect_pts(-900, 1300, 2000, 2800), "#2a2440", blob(rect_pts(-900, 1300, 2000, 1340), "#1a1630"), w=5, seed=604))
    return "".join(s)


def day_bg():
    """Дневная кухня: светлая плитка и тёплый луч окна (без пола) — под часами 14:00."""
    s = [tiles(False)]
    beam = [(-600, -200), (60, -400), (900, 1500), (240, 1700)]
    s.append(f'<path d="M{beam[0][0]} {beam[0][1]} L{beam[1][0]} {beam[1][1]} L{beam[2][0]} {beam[2][1]} L{beam[3][0]} {beam[3][1]}Z" '
             f'fill="#fff6d0" opacity=".55" {blur(30)}/>')
    s.append(shape(rect_pts(-900, 1260, 2000, 1300), "#c99059", "", w=5, seed=605))
    s.append(shape(rect_pts(-900, 1300, 2000, 2800), "#e0c9a0", blob(rect_pts(-900, 1300, 2000, 1340), "#c9b088"), w=5, seed=606))
    return "".join(s)



def morning_bg():
    s = [tiles(False)]
    # солнечный луч из окна слева: светлая полоса наискосок
    beam = [(-600, -200), (60, -400), (900, 1500), (240, 1700)]
    s.append(f'<path d="M{beam[0][0]} {beam[0][1]} L{beam[1][0]} {beam[1][1]} L{beam[2][0]} {beam[2][1]} L{beam[3][0]} {beam[3][1]}Z" '
             f'fill="#fff6d0" opacity=".55" {blur(30)}/>')
    g = rad_grad([(0, "#fff3c4", .5), (1, "#fff3c4", 0)], 200, 200, 1100, 1100)
    s.append(f'<rect x="-900" y="-900" width="2900" height="3800" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    # пол
    fl = [(-900, FLOOR, 1), (2200, FLOOR, 1), (2200, 2800, 1), (-900, 2800, 1)]
    inner = "".join(line([(-900, FLOOR + 60 + k * 90), (2200, FLOOR + 66 + k * 90)], 3, "#a8763f", taper=.1, wmin=.7, seed=610 + k, op=.8)
                    for k in range(8))
    inner += blob(rect_pts(-900, FLOOR, 2200, FLOOR + 24), "#9a6a36", .8)
    s.append(shape(fl, "#c99059", inner, w=5, seed=611))
    # плинтус
    s.append(shape(rect_pts(-900, FLOOR - 34, DOOR_X, FLOOR), "#efe6d4", "", w=4.4, seed=612))
    return "".join(s)


def door(open_a, t):
    """Входная дверь справа: проём от DOOR_X, полотно на петлях у правого края; open_a 0 — закрыта, 1 — приоткрыта."""
    s = []
    x0, y0, x1, y1 = DOOR_X, -160, 1500, FLOOR
    # наличник
    s.append(shape(rect_pts(x0 - 44, y0 - 44, x1 + 44, y1, 6), "#e8dcc4", blob(rect_pts(x0 - 44, y0 - 44, x0 - 30, y1), "#cdbd9c"),
                   w=5, seed=620))
    # тёмная щель подъезда за дверью
    s.append(shape(rect_pts(x0, y0, x1, y1), "#3a3446", "", w=4, seed=621))
    # полотно: при открытии его левый (дальний от петель) край уходит вправо — видим полотно уже
    gap = 150 * open_a
    dx0 = x0 + gap
    pts = [(dx0, y0 + 10 * open_a, 1), (x1, y0, 1), (x1, y1, 1), (dx0, y1 - 10 * open_a, 1)]
    inner = blob([(dx0, y0), (dx0 + 40, y0), (dx0 + 40, y1), (dx0, y1)], "#7a4524")
    for k, (a, b) in enumerate([(y0 + 80, y0 + 520), (y0 + 610, y1 - 90)]):
        px0 = dx0 + 70 + gap * 0.1
        inner += shape(rect_pts(px0, a, x1 - 60, b, 8), "#a0622f", blob(rect_pts(px0, b - 18, x1 - 60, b), "#7a4524"), w=3.6, seed=623 + k)
    s.append(shape(pts, "#b06e36", inner, w=5.4, seed=622))
    # ручка
    hx, hy = dx0 + 70, 480
    s.append(shape(rect_pts(hx - 14, hy - 60, hx + 14, hy + 60, 12), "#c9ced8", "", w=3.4, seed=626))
    s.append(shape(rect_pts(hx - 6, hy - 10, hx + 58, hy + 12, 10), "#d8dde6", blob(rect_pts(hx - 6, hy + 2, hx + 58, hy + 12), "#9aa0ab"),
                   w=3.4, seed=627))
    return "".join(s)


def clock_static(night):
    s = []
    cx, cy = CC
    rim = "#2c2836"
    face = "#f2e6c8" if night else "#fbf6ea"
    face_sh = "#d8c9a4" if night else "#e6dcc6"
    inner = blob(ellipse_pts(cx + 30, cy + 34, R - 30, R - 30, 40), face_sh)
    inner += blob(ellipse_pts(cx, cy, R - 44, R - 44, 40), face)
    s.append(shape(ellipse_pts(cx, cy, R, R, 40), rim, blob(ellipse_pts(cx + 26, cy + 26, R - 10, R - 10, 40), "#1a1722"), w=6, seed=640))
    s.append(shape(ellipse_pts(cx, cy, R - 34, R - 34, 40), face, blob(ellipse_pts(cx + 40, cy + 46, R - 40, R - 40, 40), face_sh) +
                   blob(ellipse_pts(cx - 6, cy - 6, R - 56, R - 56, 40), face), w=4.4, seed=641))
    # деления
    for k in range(60):
        a = math.radians(k * 6 - 90)
        big = k % 5 == 0
        r0, r1 = (R - 66, R - 98) if big else (R - 66, R - 80)
        p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        p1 = (cx + r1 * math.cos(a), cy + r1 * math.sin(a))
        s.append(line([p0, p1], 7 if big else 3.2, INK, taper=.1, wmin=.7, seed=650 + k))
    for n in range(1, 13):
        a = math.radians(n * 30 - 90)
        rr = R - 140
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        s.append(f'<text x="{f(x)}" y="{f(y + 21)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="60" fill="{INK}">{n}</text>')
    return "".join(s)


def hand_shape(ang, L, w, tail, col, sd):
    """Стрелка: угол ang (градусы от 12 по часовой), длина L, ширина w."""
    a = math.radians(ang - 90)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    cx, cy = CC
    P = lambda u, v: (cx + ux * u + nx * v, cy + uy * u + ny * v)
    pts = [P(-tail, -w * .35), P(L * .15, -w / 2), P(L * .82, -w * .32), P(L, 0) + (1,), P(L * .82, w * .32), P(L * .15, w / 2),
           P(-tail, w * .35)]
    return shape(pts, col, "", w=4, seed=sd)


def clock(t, hour_a, min_a, sec_a, night):
    cx, cy = CC
    s = [_ST["clock_n" if night else "clock_d"]]
    s.append(hand_shape(hour_a, R * .5, 30, 40, "#2c2836", 660))
    s.append(hand_shape(min_a, R * .76, 22, 50, "#2c2836", 661))
    a = math.radians(sec_a - 90)
    s.append(line([(cx - 60 * math.cos(a), cy - 60 * math.sin(a)), (cx + R * .8 * math.cos(a), cy + R * .8 * math.sin(a))], 6, "#d8382e",
                  taper=.1, wmin=.7, seed=662))
    s.append(shape(ellipse_pts(cx, cy, 20, 20, 14), "#d8382e", "", w=4, seed=663))
    # блик стекла
    s.append(line([(cx - R * .62, cy - R * .2), (cx - R * .5, cy - R * .5), (cx - R * .22, cy - R * .64)], 9,
                  "#ffffff", taper=.6, seed=664, op=.85))
    return "".join(s)


def shadow(dx, dy, sc=1.0, col="#05070f", op=.5):
    cx, cy = CC
    return blob(ellipse_pts(cx + dx, cy + dy, R * sc, R * sc, 30), col, op, blur(16))


def speed_lines(u, k, y0=300, n=7, sd=690):
    s = []
    for j in range(n):
        yy = y0 + j * 150
        ln = 520 * (1 - k)
        x0 = -40 + (j % 3) * 60
        s.append(line([(x0, yy), (x0 + ln, yy + 6)], 10 * (1 - k) + 2, INK, taper=.6, seed=sd + j))
    return "".join(s)



T0 = 6.88           # начало клипа
HIT = 7.40          # «три»
SPIN0, SPIN1 = 7.34, 8.22


def spin_angles(t):
    """(hour_a, min_a, k) — стрелки 14:00 -> 17:00: минутная делает 3 круга, часовая идёт с 2 до 5. Перед рывком — замах назад."""
    if t < SPIN0:
        m = 0.0
        w = clamp((t - (SPIN0 - 0.2)) / 0.2)       # замах назад на 0.2 с
        m = -14 * math.sin(w * math.pi / 2) * (1 if w < 1 else 1)
        k = 0.0
    else:
        u = clamp((t - SPIN0) / (SPIN1 - SPIN0))
        k = ease_io(u) * 0.55 + (1 - (1 - u) ** 2.2) * 0.45
        m = -14 * (1 - clamp((t - SPIN0) / 0.12))
        m += 1080 * k + 0.0
        # дошла до 17:00 с перелётом и успокоением
        e = t - SPIN1
        if e >= 0:
            m += 7 * math.exp(-e * 8) * math.cos(e * 30)
    min_a = m
    hour_a = 60 + (m / 360.0) * 30
    return hour_a, min_a, (clamp((t - SPIN0) / (SPIN1 - SPIN0)) if t >= SPIN0 else 0.0)


def frame5(t):
    hour_a, min_a, k = spin_angles(t)
    # темнеет: ночной фон проступает поверх дневного (плитка, лампа), с 7.5 до 8.35
    dk = smooth(7.5, 8.35, t)
    s = [_ST["day"]]
    if dk > 0:
        s.append(f'<g opacity="{dk:.3f}">{_ST["night"]}</g>')
    sec_a = (t * 360 * (0.6 + 6 * k)) % 360
    sw = 0.5 * math.sin(t * 2.3)
    e = t - HIT
    if e >= 0:
        sw += 3.0 * math.exp(-e * 5) * math.sin(e * 28)
    # во время рывка часы дрожат
    if 0 < k < 1:
        sw += 1.6 * math.sin(t * 90) * math.sin(math.pi * k)
    s.append(shadow(26, 30))
    s.append(f'<g transform="rotate({f(sw)} {CC[0]} {CC[1] - R - 30})">')
    s.append(line([(CC[0], CC[1] - R - 40), (CC[0], CC[1] - R + 4)], 8, INK, seed=670))
    s.append(clock(t, hour_a, min_a, sec_a, False))
    s.append("</g>")
    # штрихи вращения вокруг ободка: короткие дуги, бегущие по кругу (сплошные, не прозрачные)
    if 0.04 < k < 0.97:
        a = math.sin(math.pi * k)
        for j in range(10):
            base = math.radians(j * 36 + min_a * 0.9)
            for sub in (0.0, 0.12):
                r0 = R + 34 + 22 * (j % 3)
                p = [(CC[0] + r0 * math.cos(base - sub - q * 0.22), CC[1] + r0 * math.sin(base - sub - q * 0.22)) for q in (0, 0.5, 1)]
                if sub == 0.0:
                    s.append(line(p, 8 * a + 1.2, INK, taper=.7, wmin=.2, seed=730 + j))
    # круглая надпись-вспышка времени «17:00» после остановки
    if t >= SPIN1:
        ee = t - SPIN1
        pop = 1 + 0.12 * math.exp(-ee * 9) * math.cos(ee * 26)
        sc = ease_out(clamp(ee / 0.14)) * pop
        px, py = CC[0], CC[1] + R + 150
        s.append(f'<g transform="translate({f(px)} {f(py)}) scale({sc:.3f}) translate({f(-px)} {f(-py)})">'
                 + shape(rect_pts(px - 200, py - 70, px + 200, py + 66, 34), "#fbf3de", blob(rect_pts(px - 200, py + 30, px + 200, py + 66, 30), "#e3d4b0"),
                         w=5, seed=740)
                 + f'<text x="{f(px)}" y="{f(py + 28)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="104" fill="#d8382e">17:00</text></g>')
    # камера: хлёст слева (6.88–7.08), наезд, удар на «три», дрожь рывка
    u = clamp((t - T0) / 0.2)
    kk = ease_out(u, 3)
    ccx = 500 - 560 * (1 - kk) + 6 * math.sin(t * 40) * math.sin(math.pi * k) * (k > 0)
    ccy = 700
    scc = 1.18 + 0.1 * clamp((t - T0) / 1.5)
    rot = -4 * (1 - kk)
    if e >= 0:
        q = math.exp(-e * 6)
        scc += 0.16 * ease_out(min(1, e / 0.08)) * (0.5 + 0.5 * q)
        ccy += 8 * math.exp(-e * 9) * math.sin(e * 45)
        rot += 1.8 * math.exp(-e * 8) * math.sin(e * 35)
    body = "".join(s)
    if u < 1:
        body += speed_lines(u, kk)
    return body, cam(ccx, ccy, scc, rot)


def frame(sid, t):
    global CC
    CC = (500, 640)
    if not _ST:
        _ST["night"] = night_bg()
        _ST["day"] = day_bg()
        _ST["clock_d"] = clock_static(False)
        lib.static_done()
    lib.dyn_begin()
    art, cm = frame5(t)
    bg = mix("#efe2c4", "#1a2240", smooth(7.5, 8.35, t))
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cm}">{art}</g>')
