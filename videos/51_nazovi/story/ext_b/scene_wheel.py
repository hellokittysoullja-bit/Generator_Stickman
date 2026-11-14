"""Рилс 51, s08 (12.3–13.7, клип 12.1–13.9): метафора «злость забирает руль». Дима за рулём (вид сбоку), красная клякса-злость
вырастает из-за приборной панели, на «забирает» (12.76) выбивает его руки из руля, хватает обод и крутит."""
import math

import numpy as np

import dima
import lib
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg, T)
from parts import sausage

_ST = {}
GRAB = 12.76
HX, HY, S = 250, 1190, 2.55          # таз Димы в мире, масштаб рисунка Димы
WC, WR, WK, WTILT = (760, 930), 250, 0.34, -10.0    # центр руля, радиус, сжатие по x (вид сбоку), наклон
RED, RED_SH, RED_HI = "#e0382e", "#a81f1c", "#ff7a5c"


def Wp(th, off=0.0):
    """Точка обода руля (мир) по углу th градусов в плоскости руля; off — поворот руля."""
    a = math.radians(th + off)
    x, y = WR * WK * math.cos(a), WR * math.sin(a)
    r = math.radians(WTILT)
    return (WC[0] + x * math.cos(r) - y * math.sin(r), WC[1] + x * math.sin(r) + y * math.cos(r))


def tod(p):          # мир → координаты рисунка Димы (до масштаба)
    return ((p[0] - HX) / S, (p[1] - HY) / S)


def background(t):
    s = []
    g = lin_grad([(0, "#161a3a", 1), (.55, "#3a2f5a", 1), (1, "#7a4a5a", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-800" y="-800" width="2700" height="{1700}" fill="url(#{g})"/>')
    # дома-силуэты, уезжают влево (машина едет вправо)
    for layer, (sp, col, hmin) in enumerate([(120, "#26264a", 260), (260, "#1a1a38", 340)]):
        off = (t * sp) % 600
        for k in range(-1, 6):
            x = k * 600 - off
            for j, (dx, w, h) in enumerate([(0, 190, hmin), (210, 150, hmin + 120), (380, 200, hmin - 60)]):
                s.append(blob(rect_pts(x + dx, 930 - h - layer * 30, x + dx + w, 1000), col, 1))
                for r_ in range(3):
                    for c_ in range(2):
                        if (j + r_ + c_ + k) % 3:
                            s.append(blob(rect_pts(x + dx + 30 + c_ * 70, 930 - h + 40 + r_ * 70 - layer * 30,
                                                   x + dx + 62 + c_ * 70, 930 - h + 80 + r_ * 70 - layer * 30), "#ffd27a", .85))
    # фонари: столб + жёлтый шар, пролетают быстро
    off = (t * 700) % 900
    for k in range(-1, 3):
        x = k * 900 - off + 300
        s.append(line([(x, 1000), (x, 560)], 12, "#12122a", seed=600 + k, taper=0))
        gl = rad_grad([(0, "#ffe09a", .6), (1, "#ffe09a", 0)], x, 560, 150, 150)
        s.append(f'<rect x="{x - 160}" y="400" width="320" height="320" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
        s.append(blob(ellipse_pts(x, 560, 26, 26, 12), "#fff2c4"))
    # дорога и бегущая разметка
    s.append(blob(rect_pts(-800, 1000, 1900, 1400), "#23233a", 1))
    s.append(line([(-800, 1000), (1900, 1000)], 4, INK, taper=.05, wmin=.9, seed=610))
    off = (t * 1300) % 520
    for k in range(-1, 5):
        x = k * 520 - off
        s.append(blob(rect_pts(x, 1130, x + 260, 1156), "#e9dfc0", 1))
    return "".join(s)


def interior():
    """Передний план: сиденье сзади Димы, приборная панель справа, дверь снизу (закрывает ноги)."""
    back = []
    seat = [(-60, 560), (150, 560), (200, 700), (230, 1200), (-60, 1300)]
    back.append(shape(seat, "#6a3a3a", blob([(120, 560), (210, 700), (240, 1250), (160, 1250)], "#4a2630", .9) +
                      line([(60, 620), (110, 1200)], 4, "#4a2630", seed=620, op=.8), w=5.6, seed=621))
    fr = []
    dash = [(900, 1110), (1200, 1070), (1200, 1400), (700, 1400), (700, 1260), (790, 1170, 1)]
    fr.append(shape(dash, "#2b2b3a", blob([(760, 1230), (1200, 1230), (1200, 1400), (760, 1400)], "#1c1c28", 1) +
                    line([(910, 1118), (1200, 1078)], 6, "#5a5a74", seed=630, op=.8), w=5.6, seed=631))
    door = [(-60, 1210), (1200, 1180), (1200, 2100), (-60, 2100)]
    fr.append(shape(door, "#3c3046", blob([(-60, 1210), (1200, 1180), (1200, 1250), (-60, 1280)], "#2a2034", 1) +
                    line([(-60, 1215), (1200, 1186)], 8, "#6f628a", seed=632, op=.9), w=6, seed=633))
    return "".join(back), "".join(fr)


def wheel(off):
    pts = [Wp(th, off) for th in range(0, 380, 10)]
    s = []
    # колонка
    s.append(line([WC, (WC[0] + 120, WC[1] + 200)], 40, INK, taper=0, wmin=1, seed=640))
    s.append(line([WC, (WC[0] + 120, WC[1] + 200)], 28, "#3b3b4e", taper=0, wmin=1, seed=641))
    # спицы
    for k, a in enumerate((90, 210, 330)):
        p = Wp(a, off)
        s.append(line([WC, p], 30, INK, taper=0, wmin=1, seed=650 + k))
        s.append(line([WC, p], 20, "#3b3b4e", taper=0, wmin=1, seed=653 + k))
    s.append(line(pts, 56, INK, taper=0, wmin=1, seed=660))
    s.append(line(pts, 42, "#5a5c80", taper=0, wmin=1, seed=661))
    hi = [p for th, p in zip(range(0, 380, 10), pts) if 200 <= th % 360 <= 300 or th > 560]
    s.append(line([Wp(th, off) for th in range(205, 300, 10)], 9, "#b4b6d8", seed=662, op=.9))
    s.append(shape(ellipse_pts(WC[0], WC[1], 34, 58, 16, rot=WTILT), "#3b3b4e", blob(ellipse_pts(WC[0] + 8, WC[1] + 14, 22, 36, 12), "#26263a"),
                   w=5, seed=663))
    return "".join(s)


def blob_pts(cx, cy, r, t, n=22, seed=0, sx=1.0, sy=1.0):
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        rr = r * (1 + 0.09 * math.sin(a * 3 + t * 9 + seed) + 0.06 * math.sin(a * 5 - t * 13 + seed * 2))
        out.append((cx + rr * math.cos(a) * sx, cy + rr * math.sin(a) * sy))
    return out


def anger(t, off):
    """Клякса-злость: растёт из-за панели, на GRAB прыгает на руль, хватает обод."""
    e = t - GRAB
    grow = ease_out(clamp((t - 12.05) / 0.7), 2)
    # положение: прячется за панелью справа-внизу, потом прыгает к рулю
    k = ease_io(clamp((e + 0.12) / 0.2)) if e > -0.12 else 0.0
    cx = 1040 + (990 - 1040) * k
    cy = 1230 - 40 * (1 - k) + (-290) * k
    r = 60 + 110 * grow + 30 * k
    r *= 1 + 0.07 * math.sin(t * 15) * (1 - k) + (0.1 * math.exp(-max(e, 0) * 7) * math.sin(e * 30) if e > 0 else 0)
    sx, sy = (1.0, 1.0)
    if 0 < e < 0.25:
        sx, sy = 1 + 0.18 * math.exp(-e * 12) * math.sin(e * 28), 1 - 0.18 * math.exp(-e * 12) * math.sin(e * 28)
    body = blob_pts(cx, cy, r, t, seed=3, sx=sx, sy=sy)
    inner = blob(blob_pts(cx + r * .28, cy + r * .3, r * .95, t, seed=5), RED_SH, .9)
    inner += blob(ellipse_pts(cx - r * .38, cy - r * .45, r * .3, r * .16, 10, rot=-35), RED_HI, .85)
    s = []
    # руки кляксы: к ободу
    reach = ease_io(clamp((e + 0.2) / 0.22)) if e > -0.2 else 0.0
    for sd, th in ((0, 40), (1, 118)):
        tgt = Wp(th, off)
        src = (cx - r * .5, cy + (sd - .3) * r * .5)
        ex = src[0] + (tgt[0] - src[0]) * reach + 90 * (1 - reach) * (1 if sd else .6)
        ey = src[1] + (tgt[1] - src[1]) * reach - 40 * (1 - reach)
        mid = ((src[0] + ex) / 2 - 20, (src[1] + ey) / 2 + 30 * (1 - reach) - 20)
        s.append(shape(sausage([src, mid, (ex, ey)], 60, 52), RED, "", w=5.2, seed=700 + sd))
        s.append(shape(ellipse_pts(ex, ey, 46, 42, 14), RED, blob(ellipse_pts(ex + 8, ey + 10, 26, 22, 10), RED_SH, .9), w=5, seed=702 + sd))
        for j in (-1, 0, 1):
            s.append(line([(ex - 26, ey + j * 14), (ex - 8, ey + j * 14)], 3, INK, seed=704 + sd * 4 + j, taper=.4))
    s.append(shape(body, RED, inner, w=6.2, seed=710))
    # лицо
    mood = ease_out(clamp((t - 12.3) / 0.4))
    for sx_ in (-1, 1):
        ex, ey = cx - r * .08 + sx_ * r * .3, cy - r * .12
        w_, h_ = r * .2, r * (.2 + .06 * (1 - mood))
        s.append(shape(ellipse_pts(ex, ey, w_, h_, 12), "#fff6ee", "", w=4.2, seed=720 + sx_))
        s.append(blob(ellipse_pts(ex - sx_ * 2 - (1 - k_if(e)) * 4, ey + h_ * .2, w_ * .38, h_ * .45, 10), INK))
        s.append(line([(ex - sx_ * w_ * 1.25, ey - h_ * 1.7 + sx_ * -r * .02 * 0), (ex + sx_ * w_ * .1, ey - h_ * 0.5)], 12 + r * .02, INK,
                      seed=730 + sx_, taper=.2, wmin=.5))
    # рот: оскал с зубами
    mx, my = cx - r * .04, cy + r * .3
    mw, mh = r * .5, r * (.14 + .12 * mood)
    mouth = [(mx - mw, my - mh * .4), (mx - mw * .5, my - mh * .6), (mx + mw * .5, my - mh * .6), (mx + mw, my - mh * .4),
             (mx + mw * .6, my + mh), (mx, my + mh * 1.3), (mx - mw * .6, my + mh)]
    teeth = "".join(blob([(mx - mw + j * mw / 2.5, my - mh * .5), (mx - mw + (j + 1) * mw / 2.5 - 4, my - mh * .5),
                          (mx - mw + (j + .5) * mw / 2.5, my + mh * .25)], "#fff6ee") for j in range(5))
    s.append(shape(mouth, "#4a0f12", teeth, w=4.6, seed=740))
    return "".join(s)


def k_if(e):
    return clamp((e + 0.1) / 0.1)


def shove(e):
    """0 — руки на руле, 1 — выбиты назад."""
    return ease_out(clamp(e / 0.14), 2) if e > 0 else 0.0


def frame(sid, t):
    if not _ST:
        _ST["fx"] = interior()
        lib.static_done()
    lib.dyn_begin()
    e = t - GRAB
    # поворот руля: ровно, на GRAB — рывок на 75° с перелётом
    off = 3 * math.sin(t * 3) + (75 * spring(e, 2.2, 9.0) if e > 0 else 0)
    sv = shove(e)
    # руки Димы: на ободе, потом выбиты вверх-назад (раскрытые ладони)
    tn = Wp(-160, 3 * math.sin(t * 3) if e < 0 else 0)
    tf = Wp(-45, 3 * math.sin(t * 3) if e < 0 else 0)
    away_n = (HX + 220, HY - 600)
    away_f = (HX + 330, HY - 650)
    wob = math.exp(-max(e, 0) * 5) * math.sin(max(e, 0) * 26) * 14
    tn = (tn[0] + (away_n[0] - tn[0]) * sv, tn[1] + (away_n[1] - tn[1]) * sv + wob)
    tf = (tf[0] + (away_f[0] - tf[0]) * sv, tf[1] + (away_f[1] - tf[1]) * sv - wob)
    # мимика: сперва усталый, на «быстро» (12.4) настораживается, на GRAB — шок
    lid = 0.35 + 0.5 * smooth(12.35, 12.55, t) + 0.15 * sv
    brows = "tired" if t < 12.4 else ("worry" if e < 0 else "up")
    mouth = "flat" if t < 12.5 else ("gape" if e > -0.05 else "tired")
    look = (0.9, 0.2) if e < 0 else (0.9, 0.6)
    jolt = math.exp(-max(e, 0) * 6) * math.sin(max(e, 0) * 22) * 0.06 if e > 0 else 0
    pose = {
        "hip": (0, 0), "lean": 0.1 - 0.22 * sv + jolt, "feet": {"n": ((100, 235), 0.3), "f": ((60, 238), 0.3)},
        "arms": {"n": ("ik", tod(tn)), "f": ("ik", tod(tf))},
        "hands": {"n": "fist" if sv < .3 else ("open", 0.2), "f": "fist" if sv < .3 else ("open", 0.2)},
        "head_ang": -0.2 * sv + jolt * 2 + 0.02 * math.sin(t * 6), "hood": 22 * sv * math.sin(e * 25) if e > 0 else 0,
        "strings": (0, 0), "hair": (26 * math.exp(-max(e, 0) * 7) * (1 if e > 0 else 0)),
        "expr": {"lid": lid, "look": look, "brows": brows, "mouth": mouth, "hair": 26 * math.exp(-max(e, 0) * 7) if e > 0 else 0},
    }
    dg, _ = dima.draw(pose)
    back, front = _ST["fx"]
    bump = 5 * math.sin(t * 17) + 3 * math.sin(t * 29)        # дорожная вибрация
    s = [background(t), back]
    s.append(f'<g transform="translate(0 {bump * .6:.2f})">'
             f'<g transform="translate({HX} {HY}) scale({S}) translate({-0} {-0})">{dg}</g>')
    # руль поверх тела, но руки Димы рисуются в dg: руль ставим ДО рук нельзя — поэтому руль отдельным слоем под телом
    s.append("</g>")
    body = "".join(s)
    # порядок: фон, сиденье, руль, Дима (руки поверх обода), клякса, панель, дверь
    layers = [background(t), back, f'<g transform="translate(0 {bump * .6:.2f})">{wheel(off)}', f'<g transform="translate({HX} {HY}) scale({S})">{dg}</g></g>',
              anger(t, off), front]
    # красные штрихи гнева и штрихи удара
    fxs = []
    if 0 <= e < 0.45:
        k = e / 0.45
        for j in range(9):
            a = math.radians(-170 + j * 22)
            r0, r1 = 290 + 60 * k, 360 + 160 * k
            fxs.append(line([(WC[0] + r0 * math.cos(a), WC[1] - 40 + r0 * math.sin(a)), (WC[0] + r1 * math.cos(a), WC[1] - 40 + r1 * math.sin(a))],
                            14 * (1 - k) + 2, INK, taper=.6, seed=750 + j))
    layers.append("".join(fxs))
    # камера
    v = clamp((t - 12.1) / 1.8)
    ccx, ccy = 600 + 40 * v, 900
    scc = 0.98 + 0.08 * ease_io(v)
    if e > 0:
        kk = math.exp(-e * 7)
        scc *= 1 + 0.09 * kk
        ccx += 16 * kk * math.sin(e * 51)
        ccy += 20 * kk * math.sin(e * 43)
    crot = 0.6 * math.sin(t * 1.7) + (4.0 * math.exp(-max(e, 0) * 6) * math.sin(e * 25) if e > 0 else 0)
    return svg(f'<rect width="{W}" height="{H}" fill="#161a3a"/><g transform="{cam(ccx, ccy, scc, crot)}">{"".join(layers)}</g>')
