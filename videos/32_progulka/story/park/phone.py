"""Телефон в руке Димы экраном к зрителю (мультяшная условность) с таймером: до «двадцать» — «20:00» тускло и кнопка
«пуск», большой палец жмёт её, на «двадцать» цифры вспыхивают и таймер идёт: секундное кольцо бежит, в 26.12 — 19:59.
Рисуется в L-единицах героя (внутри группы dima.draw)."""
import math

import numpy as np

import lib
import parts
from lib import INK, blob, ellipse_pts, line, shape

T_GO = 25.12
PW, PH = 168.0, 292.0


def _timer_text(t):
    if t < T_GO:
        return "20:00"
    s = 20 * 60 - int(math.floor(t - T_GO))
    return f"{s // 60:02d}:{s % 60:02d}"


def draw(Wr, d, t, tap=0.0):
    """Wr — запястье (L), d — направление кисти. Телефон стоит над кулаком, чуть наклонён."""
    c = np.array(Wr, float) + np.array([18.0, -150.0])
    ang = -6.0
    pop = 0.0
    if t >= T_GO:
        u = t - T_GO
        pop = math.exp(-7 * u) * math.sin(u * 22) * 0.10
    sc = 1.0 + pop
    o = []
    x0, y0, x1, y1 = -PW / 2, -PH / 2, PW / 2, PH / 2
    body = lib.rect_pts(x0, y0, x1, y1, 26)
    o.append(shape(body, "#2c2f3a", blob(lib.rect_pts(x0 + 100, y0, x1, y1, 20), "#22242d", .9), w=5.0, seed=901))
    scr = lib.rect_pts(x0 + 11, y0 + 14, x1 - 11, y1 - 14, 16)
    lit = t >= T_GO
    o.append(blob(scr, "#16243a" if lit else "#1a2333"))
    if lit:
        o.append(f'<g opacity="{min(1, (t - T_GO) / 0.12):.3f}">' + blob(scr, "#1d3550") + "</g>")
    # цифры
    txt = _timer_text(t)
    dw, dh, th = 25.0, 46.0, 7.4
    gap = 7.0
    width = 4 * dw + 4 * gap + th * 1.2
    col = "#c6f25a" if lit else "#5a6a5a"
    glow = 0.8 * math.exp(-3 * (t - T_GO)) + 0.35 if lit else 0.0
    sv, _ = parts.sevenseg(txt, -width / 2, -96, dw, dh, th, col, ghost="#26354a", gap=gap, glow=glow, glow_col="#b8ff3a")
    o.append(sv)
    # кольцо секунд / кнопка «пуск»
    rc, cy = 40.0, 46.0
    o.append(f'<circle cx="0" cy="{cy}" r="{rc}" fill="none" stroke="#2c4462" stroke-width="9"/>')
    if lit:
        a = (t - T_GO) % 1.0
        a0 = -math.pi / 2
        a1 = a0 + 2 * math.pi * max(0.02, a)
        large = 1 if (a1 - a0) > math.pi else 0
        p0 = (rc * math.cos(a0), cy + rc * math.sin(a0))
        p1 = (rc * math.cos(a1), cy + rc * math.sin(a1))
        o.append(f'<path d="M{p0[0]:.2f} {p0[1]:.2f} A{rc} {rc} 0 {large} 1 {p1[0]:.2f} {p1[1]:.2f}" fill="none" stroke="#c6f25a" '
                 f'stroke-width="9" stroke-linecap="round"/>')
        o.append(f'<circle cx="{p1[0]:.2f}" cy="{p1[1]:.2f}" r="8" fill="#eaffb0"/>')
        # пауза
        for sx in (-1, 1):
            o.append(blob(lib.rect_pts(sx * 9 - 4, cy - 15, sx * 9 + 4, cy + 15, 2), "#c6f25a"))
    else:
        o.append(blob([(-11, cy - 17), (17, cy), (-11, cy + 17)], "#8fb04a"))
    # блик стекла
    o.append(blob([(x0 + 18, y0 + 30), (x0 + 50, y0 + 22), (x0 + 22, y1 - 120)], "#ffffff", .07))
    o.append(blob(lib.rect_pts(-22, y0 + 4, 22, y0 + 10, 3), "#454a58"))
    g = f'<g transform="translate({c[0]:.2f} {c[1]:.2f}) rotate({ang}) scale({sc:.4f})">{"".join(o)}</g>'
    # большой палец на нижнем крае экрана (жмёт «пуск» перед «двадцать»)
    tp = np.array([-30.0 + 34 * tap, 120.0 - 70 * tap])
    a = math.radians(ang)
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    base = c + R @ np.array([-46.0, 152.0])
    tipw = c + R @ tp
    th_pts = lib.band([tuple(base), tuple((base + tipw) / 2 + np.array([0, 8])), tuple(tipw)], 36, 30, step=3, cap=True)
    import dima
    g += shape(th_pts, dima.SKIN, blob(ellipse_pts(tipw[0] + 6, tipw[1] - 4, 10, 8, 8), "#e9c4b6", .9) +
               line([tuple(base + np.array([6, 14])), tuple((base + tipw) / 2 + np.array([0, 18]))], 2, dima.SKIN_SH2, seed=911, op=.7),
               w=4.0, seed=910)
    return g


def screen_center_L(Wr):
    return np.array(Wr, float) + np.array([18.0, -150.0])


_ = INK
