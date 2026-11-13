"""Золотая рыбка и круглый аквариум рилса 31 (для карточки подписки и магнита на холодильнике).
fish(...) — рыбка в своих координатах (нос в +x, длина ~270 при sc=1), ставится группой translate/rotate/scale;
bowl(...) — аквариум-шар, внутрь кладётся рыбка (обрезка по стеклу)."""
import math

import lib
from lib import INK, blob, clip_of, ellipse_pts, f, line, shape, T

BODY, BODY_SH, BELLY, FIN, FIN_L = "#f5862b", "#d8621c", "#ffc46e", "#ff9a3c", "#ffc782"
WATER, WATER_D, WATER_L = "#bfe4ee", "#94cbdc", "#e2f4f8"


def fish(x, y, sc=1.0, rot=0.0, flip=False, tail=0.0, look=(0.0, 0.0), blink=0.0, w=4.6, sd=0, eye_big=1.0, mouth="o"):
    """tail — угол хвоста (градусы), look — взгляд (-1..1), blink 0..1. w — толщина туши на экране при sc."""
    iw = w / max(sc, 1e-3)
    s = []
    # хвост: веер из двух лопастей с выемкой, качается вокруг корня
    tl = [(-78, -10), (-140, -66), (-176, -58), (-150, -14), (-136, 0, 1), (-150, 14), (-176, 58), (-140, 66), (-78, 10)]
    tl = T(tl, 0, 0, 1.0, tail, -82, 0)
    tin = "".join(line(T([(-96, k * 6), (-150, k * 26)], 0, 0, 1, tail, -82, 0), 2.6 / max(sc, .3), FIN_L, seed=sd + 5 + k, op=.95)
                  for k in (-1.6, -0.5, 0.5, 1.6))
    s.append(shape(tl, FIN, tin, w=iw * 0.9, seed=sd + 1))
    # спинной плавник
    dor = [(-40, -40), (-6, -92), (26, -84), (44, -46)]
    s.append(shape(dor, FIN, line([(0, -48), (8, -80)], 2.4 / max(sc, .3), FIN_L, seed=sd + 9), w=iw * 0.9, seed=sd + 2))
    # тело
    body = [(104, 2), (88, -32), (48, -54), (-10, -52), (-62, -32), (-86, 0), (-62, 32), (-10, 50), (48, 50), (88, 30)]
    inner = blob([(-90, 6), (-40, 20), (40, 26), (104, 8), (104, 70), (-90, 70)], BODY_SH, .95)
    inner += blob([(-50, 30), (20, 30), (78, 24), (60, 48), (-20, 52)], BELLY, .95)
    inner += blob([(-20, -46), (40, -50), (70, -38), (10, -36)], "#ffb064", .9)
    for k, (u, v) in enumerate([(-30, -12), (-6, 4), (-40, 12), (-16, -26)]):
        inner += line([(u, v - 9), (u + 8, v), (u, v + 9)], 2.2 / max(sc, .3), BODY_SH, seed=sd + 20 + k, op=.9)
    s.append(shape(body, BODY, inner, w=iw, seed=sd + 3))
    # грудной плавник
    pec = [(10, 18), (-18, 40), (-6, 48), (22, 30)]
    s.append(shape(pec, FIN, "", w=iw * 0.8, seed=sd + 4))
    # глаз: большой белый, маленький зрачок
    er = 22 * eye_big
    ex, ey = 56, -14
    s.append(shape(ellipse_pts(ex, ey, er, er * 1.05, 16), "#ffffff", "", w=iw * 0.85, seed=sd + 6))
    if blink < 0.95:
        px, py = ex + look[0] * er * 0.35, ey + look[1] * er * 0.35
        s.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(7.5 * eye_big)}" fill="#14121a"/>')
        s.append(f'<circle cx="{f(px - 2.5)}" cy="{f(py - 3)}" r="{f(2.4 * eye_big)}" fill="#ffffff"/>')
    if blink > 0.02:
        b = min(1.0, blink)
        yt = ey - er * 1.05 + 2 * er * 1.05 * b
        c = clip_of(ellipse_pts(ex, ey, er, er * 1.05, 16))
        s.append(f'<g clip-path="url(#{c})"><rect x="{f(ex - er - 2)}" y="{f(ey - er * 1.1)}" width="{f(2 * er + 4)}" '
                 f'height="{f(yt - ey + er * 1.1)}" fill="{BODY}"/></g>')
        s.append(line([(ex - er * .9, yt), (ex, yt + 2), (ex + er * .9, yt)], iw * 0.8, INK, seed=sd + 7))
    # рот
    if mouth == "o":
        s.append(shape(ellipse_pts(100, 10, 5, 6, 8), "#a8401a", "", w=iw * 0.6, seed=sd + 8))
    else:
        s.append(line([(92, 14), (100, 18), (104, 12)], iw * 0.7, INK, seed=sd + 8))
    fl = -1 if flip else 1
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc * fl)} {f(sc)})">{"".join(s)}</g>'


def bowl(cx, cy, R, t, inside="", sd=0, w=5.0, bubbles=True, water_shift=0.0):
    """Аквариум-шар: центр (cx, cy), радиус R. inside — SVG рыбки (в мировых координатах), обрезается по стеклу."""
    s = []
    s.append(blob(ellipse_pts(cx + 10, cy + R * 0.93, R * 0.8, R * 0.11, 16), "#2a1606", .35, lib.blur(8)))
    yr = cy - R * 0.74                 # срез горла
    rx_r = R * 0.62
    glass = []
    th0 = math.atan2(yr - cy, math.sqrt(max(R * R - (yr - cy) ** 2, 1)))
    for k in range(29):
        a = th0 + (math.pi - 2 * th0) * k / 28
        glass.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    gl = [(p[0], p[1]) for p in glass]
    hw = math.sqrt(max(R * R - (yr - cy) ** 2, 1))
    # вода до уровня wl
    wl = cy - R * 0.5 + water_shift
    wave = [(cx - R - 10 + k * (2 * R + 20) / 16, wl + 4 * math.sin(t * 3.1 + k * 0.9)) for k in range(17)]
    water = wave + [(cx + R + 10, cy + R + 10, 1), (cx - R - 10, cy + R + 10, 1)]
    c_gl = clip_of(gl + [(cx - hw, yr)])
    inner = [f'<path d="{lib.fill_d(water)}" fill="{WATER}"/>']
    inner.append(blob([(cx + R * 0.2, wl), (cx + R + 10, wl), (cx + R + 10, cy + R + 10), (cx + R * 0.1, cy + R + 10)], WATER_D, .9))
    inner.append(blob([(p[0], p[1] + 10) for p in wave[2:9]] + [(wave[8][0], wl + 26), (wave[2][0], wl + 26)], WATER_L, .9))
    # гравий и водоросль
    gy = cy + R * 0.72
    inner.append(blob([(cx - R, gy), (cx - R * .4, gy - 12), (cx + R * .3, gy - 8), (cx + R, gy + 4), (cx + R, cy + R + 10),
                       (cx - R, cy + R + 10)], "#d9b98a"))
    cols = ["#e07a5f", "#8ab6d6", "#e9c46a", "#9fc5a8", "#c9a37a"]
    for k in range(13):
        px = cx - R * .8 + k * R * 1.6 / 12
        py = gy + 6 + 8 * ((k * 7) % 3)
        inner.append(shape(ellipse_pts(px, py, R * .07, R * .055, 8, rot=k * 23), cols[k % 5], "", w=2.2, seed=sd + 40 + k))
    for k, (bx, hh) in enumerate([(cx - R * .45, R * .75), (cx - R * .3, R * .55)]):
        sw = 6 * math.sin(t * 2.2 + k)
        stem = [(bx, gy + 4), (bx + sw * .4 - 6, gy - hh * .35), (bx + sw, gy - hh * .7), (bx + sw * 1.4 + 4, gy - hh)]
        inner.append(line(stem, R * .11, "#5f9a5a", taper=.8, wmin=.2, seed=sd + 60 + k))
        inner.append(line(stem, 3, INK, taper=.6, wmin=.3, seed=sd + 64 + k, op=.7))
    inner.append(inside)
    if bubbles:
        for k in range(4):
            ph = (t * 0.55 + k * 0.27) % 1.0
            bx = cx + R * (0.15 + 0.12 * k % 0.4) + 6 * math.sin(t * 4 + k)
            by = gy - 10 - ph * (gy - wl - 10)
            r = R * (0.035 + 0.015 * (k % 2)) * (0.7 + 0.5 * ph)
            inner.append(f'<circle cx="{f(bx)}" cy="{f(by)}" r="{f(r)}" fill="{WATER_L}" stroke="{INK}" stroke-width="2.2"/>')
    # верхняя линия воды
    inner.append(line(wave, 3.2, "#5a9cb4", taper=.1, wmin=.8, seed=sd + 70))
    s.append(f'<g clip-path="url(#{c_gl})">{"".join(inner)}</g>')
    # стекло: тушь по контуру шара, блик
    s.append(f'<path d="{lib.ink_open(gl, w, taper=.05, wmin=.9, seed=sd + 80)}" fill="{INK}"/>')
    s.append(line([(cx - R * .72, cy - R * .2), (cx - R * .78, cy + R * .12), (cx - R * .64, cy + R * .45)], R * .07, "#ffffff",
                  taper=.8, wmin=.2, seed=sd + 81))
    s.append(line([(cx + R * .55, cy + R * .45), (cx + R * .62, cy + R * .3)], R * .05, "#ffffff", taper=.8, wmin=.2, seed=sd + 82))
    # горло-ободок
    s.append(shape(ellipse_pts(cx, yr, hw + 8, R * .085, 20), "#e7f4f7", blob(ellipse_pts(cx, yr + 3, hw - 6, R * .05, 16), WATER_D, .9),
                   w=w * .9, seed=sd + 83))
    return "".join(s)
