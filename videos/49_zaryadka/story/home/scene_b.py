"""Рилс 49 «зарядка», группа B: планы s02 s03 s07 s10 s13 (предметы крупно).
s02 — телефон с чёрным экраном и отражением Димы, пустая батарея, стрелка к розетке без шнура;
s03 — офис: зарядка одна в розетке, пустое кресло, свет гаснет, ярлык «ОФИС» хлопает на «работе»;
s07 — Дима с проводным дисковым телефоном, набирает номер; на «чужого» на столе появляется телефон-кирпич;
s10 — часы: минутная делает оборот и встаёт на «1 час», штрихи, качается верёвочка;
s13 — календарь, воскресенье обведено, значок часов, телефон ложится в ящик и ящик закрывается.
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика). Всё кодом, удары на словах по voice/words.json."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
from lib import (INK, band, blob, blur, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth,  # noqa: E402
                 back_out, spring, T)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def decay(t, t0, k=7.0, fr=7.0):
    """Затухающее дрожание после удара в t0: (амплитуда 0..1, знак)."""
    e = t - t0
    if e < 0:
        return 0.0
    return math.exp(-e * k) * math.sin(e * fr * 2 * math.pi)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def hook_zoom(t, t0, mx=0.4, dur=0.22, rot=-3.0):
    u = (t - t0) / dur
    if u <= 0:
        return 1 / (1 + mx), rot
    if u < 1:
        e = ease_out(u, 3)
        return 1 / (1 + mx) + (1.05 - 1 / (1 + mx)) * e, rot * (1 - e) - 1.2 * e
    return 1.0, 0.0


def whip(t, t0, dur=0.2):
    """Хлёст на входе плана: 1 → 0 за dur."""
    return 1 - ease_out(clamp((t - t0) / dur), 3)


def text(x, y, s, size, fill=INK, rot=0.0, anchor="middle", stroke="", sw=0.0, sx=1.0):
    st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke"' if stroke else ""
    return (f'<text transform="translate({lib.f(x)} {lib.f(y)}) rotate({lib.f(rot)}) scale({sx:.3f} 1)" text-anchor="{anchor}" '
            f'font-family="IDB" font-weight="900" font-size="{size}" fill="{fill}"{st}>{s}</text>')


def compose(world, cam, bg="#efe2c4", over="", vig=0.32, vcol="#2a1408"):
    cx, cy, s, r = cam
    set_ink(s)
    g = lib.rad_grad([(0, vcol, 0), (.6, vcol, 0), (1, vcol, vig)], 540, 900, 1180, 1400)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, r)}">{world}</g>{over}'
                   f'<rect width="1080" height="1920" fill="url(#{g})"/>')


def speed_streaks(cx, cy, r0, r1, e, n=9, col=INK, seed=900, w=9, a0=0.0):
    """Штрихи удара вокруг точки: e — время с удара."""
    if e < 0 or e > .45:
        return ""
    a = 1 - e / .45
    out = []
    for k in range(n):
        ang = a0 + k * 2 * math.pi / n + .2 * math.sin(k * 3.1)
        rr = r0 + (r1 - r0) * ease_out(e / .3)
        out.append(line([(cx + rr * math.cos(ang), cy + rr * math.sin(ang)),
                         (cx + (rr + 70 * a) * math.cos(ang), cy + (rr + 70 * a) * math.sin(ang))], w * a + 1, col, taper=.5, seed=seed + k))
    return "".join(out)


def kw_hand():
    people.C = people.PAL["dima"]
    return dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])


def sleeve(a, b, k, seed=610):
    """Рукав худи от a до b (мир) шириной под масштаб k."""
    people.C = people.PAL["dima"]
    a, b = np.array(a, float), np.array(b, float)
    d = (b - a) / np.linalg.norm(b - a)
    body = people.limb_band(a, b, 112 * k, 130 * k, people.C["TOP"], False, seed)
    cuff = shape(band([tuple(a - d * 4 * k), tuple(a + d * 30 * k)], 100 * k, 96 * k, step=3, cap=False), people.C["TOP_SH"], "", w=4, seed=seed + 1)
    return body + cuff


# ═════════════════════════ s10: часы ═════════════════════════
CC10, R10 = (540, 700), 330
T_CHAS = wi(44)           # «час» 15.60


def hand_poly(cx, cy, ang, ln, w0, w1, tail=40):
    a = math.radians(ang - 90)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])
    c = np.array([cx, cy])
    return [tuple(c - d * tail + n * w0 / 2), tuple(c + n * w0 / 2 + d * 10), tuple(c + d * ln + n * w1 / 2), tuple(c + d * (ln + 14)),
            tuple(c + d * ln - n * w1 / 2), tuple(c - n * w0 / 2 + d * 10), tuple(c - d * tail - n * w0 / 2)]


def wall_stripes(col1, col2, x0=-300, x1=1400, y0=-300, y1=2300, w=120):
    s = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{col1}"/>']
    for i in range(int((x1 - x0) / w / 2) + 2):
        x = x0 + i * w * 2
        s.append(f'<rect x="{x}" y="{y0}" width="{w}" height="{y1 - y0}" fill="{col2}"/>')
    return "".join(s)


def clock_face(cx, cy, R, mn, hr, shake=0.0, t=0.0):
    s = []
    rim = ellipse_pts(cx, cy, R, R, 28)
    s.append(blob(ellipse_pts(cx + 14, cy + 22, R, R, 28), "#000000", .16, blur(10)))
    s.append(shape(rim, "#c44f3a", blob(ellipse_pts(cx + 30, cy + 40, R * .92, R * .9, 24), "#a23b2a"), w=7, seed=1010))
    face = ellipse_pts(cx, cy, R * .86, R * .86, 28)
    s.append(shape(face, "#fdf8ea", blob(ellipse_pts(cx + 40, cy + 60, R * .8, R * .75, 24), "#efe4c8"), w=5, seed=1011))
    for k in range(60):
        a = math.radians(k * 6 - 90)
        big = k % 5 == 0
        r0, r1 = R * (.74 if big else .78), R * .83
        s.append(line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], 7 if big else 3,
                      INK, taper=.05, wmin=.9, seed=1020 + k))
    for n in range(1, 13):
        a = math.radians(n * 30 - 90)
        s.append(text(cx + R * .6 * math.cos(a), cy + R * .6 * math.sin(a) + 20, n, 58))
    s.append(shape(hand_poly(cx, cy, hr, R * .45, 26, 16, 36), "#2a2a38", "", w=4, seed=1030))
    s.append(shape(hand_poly(cx, cy, mn, R * .7, 18, 10, 44), "#2a2a38", "", w=4, seed=1031))
    s.append(shape(ellipse_pts(cx, cy, 20, 20, 12), "#c44f3a", "", w=4, seed=1032))
    return "".join(s)


def s10(t):
    ew = t - T_CHAS
    u = clamp((t - 14.55) / (T_CHAS - 14.55))
    mn = 360 * (1 - (1 - u) ** 1.9)
    if ew > 0:
        mn += 9 * math.exp(-ew * 9) * math.sin(ew * 46)
    hr = 30 * ease_io(clamp((t - 14.55) / (T_CHAS - 14.55 + .1)))
    cx, cy = CC10
    jump = 0.0
    sh = 0.0
    if ew > 0:
        jump = -34 * math.exp(-ew * 7) * abs(math.sin(ew * 13))
        sh = 3.5 * math.exp(-ew * 5) * math.sin(ew * 26)
    w = [wall_stripes("#f0dfb4", "#e8d3a2")]
    w.append(blob(rect_pts(-300, 1480, 1400, 2300), "#b98a5a"))
    w.append(f'<rect x="-300" y="1480" width="1700" height="40" fill="#8a5a30"/>')
    w.append(f'<g transform="translate(0 {lib.f(jump)}) rotate({lib.f(sh)} {cx} {cy - R10})">')
    w.append(line([(cx, cy - R10 - 120), (cx, cy - R10 + 10)], 9, INK, seed=1000, taper=.05, wmin=.9))
    w.append(clock_face(cx, cy, R10, mn, hr, t=t))
    # штрихи скорости вокруг стрелки, пока она летит
    if 0 < u < 1:
        a = math.radians(mn - 90)
        for j in range(1, 5):
            aa = math.radians(mn - 90 - j * 15 * (1 - u) ** .5)
            r0, r1 = R10 * .3, R10 * (.7 - .06 * j)
            w.append(line([(cx + r0 * math.cos(aa), cy + r0 * math.sin(aa)), (cx + r1 * math.cos(aa), cy + r1 * math.sin(aa))],
                          7 - j, "#7a6a50", taper=.6, wmin=.1, seed=1040 + j))
    w.append("</g>")
    # верёвочка сверху справа качается
    th = math.radians(14 * math.sin(2 * math.pi * 0.85 * t + .5) + 6 * decay(t, T_CHAS, 3, 1.3) * 3)
    L = 640
    bx, by = 935, -60
    ex, ey = bx + L * math.sin(th), by + L * math.cos(th)
    mid = (bx + L * .5 * math.sin(th * .8), by + L * .5 * math.cos(th * .8))
    w.append(line([(bx, by), mid, (ex, ey)], 8, "#6a4a2a", taper=.05, wmin=.9, seed=1050))
    w.append(shape(ellipse_pts(ex, ey + 26, 34, 40, 12, jitter=.04, seed=3), "#e0584a", blob(ellipse_pts(ex + 12, ey + 40, 24, 22, 10), "#b83a30"),
                   w=5, seed=1051))
    for j in range(5):
        a = math.radians(-50 + j * 25)
        w.append(line([(ex + 20 * math.sin(a), ey + 50), (ex + 46 * math.sin(a), ey + 100 + 8 * math.cos(a * 2))], 7, "#e0584a", taper=.3, wmin=.3,
                      seed=1060 + j))
    # на «час»: штрихи и плашка
    w.append(speed_streaks(cx, cy, R10 + 40, R10 + 110, ew, 12, INK, 1070, 10))
    if ew > -0.02:
        k = back_out(clamp(ew / .28), 2.2)
        py = cy + R10 + 230
        plate = rect_pts(-250, -70, 250, 70, 34)
        pl = shape(plate, "#f2c23a", blob(rect_pts(-250, 10, 250, 70, 34), "#d9a521"), w=7, seed=1080)
        w.append(f'<g transform="translate({cx} {py}) rotate({lib.f(-3 + 3 * k)}) scale({k:.3f})">{pl}{text(0, 36, "1 ЧАС", 120)}</g>')
    ww = whip(t, 14.7, .22)
    s_ = 1.0 + .26 * ease_io(clamp((t - 14.7) / 1.8))
    if ew > 0:
        s_ *= 1 + .06 * math.exp(-ew * 8) * ease_out(min(1, ew / .05))
    cam = (540 + 300 * ww, 770 + 40 * math.exp(-ew * 8) * math.sin(ew * 40) * (ew > 0) - 30 * smooth(14.7, 16.7, t), s_, -4 * ww + .5 * osc(t, .6))
    return compose("".join(w), cam, "#e8d3a2")



def phone(x, y, k=1.0, rot=0.0, body="#2b2d3a", screen="#0b0b10", glow=None, inner=""):
    """Смартфон (центр x, y), 200×400 в единицах k; inner — рисунок на экране (в локальных координатах)."""
    P = lambda pts: pts
    o = [f'<g transform="translate({lib.f(x)} {lib.f(y)}) rotate({lib.f(rot)}) scale({k:.4f})">']
    o.append(shape(rect_pts(-100, -200, 100, 200, 30), body, blob(rect_pts(50, -200, 100, 200, 30), "#1a1b24"), w=6, seed=1300))
    sc = rect_pts(-84, -178, 84, 178, 18)
    cl = lib.clip_of(sc)
    o.append(f'<path d="{lib.fill_d(sc)}" fill="{glow or screen}"/>')
    o.append(f'<g clip-path="url(#{cl})">{inner}</g>')
    o.append(f'<path d="{lib.ink_closed(sc, 3.2, seed=1301)}" fill="{INK}"/>')
    o.append(blob(ellipse_pts(0, -166, 18, 5, 10), "#000000", .9))
    o.append("</g>")
    return "".join(o)


# ═════════════════════════ s02: телефон ═════════════════════════
T_ZAR = wi(5)           # «зарядку» 1.68


def battery_icon(x, y, k, blink):
    c = "#e0453a"
    o = shape(rect_pts(-70, -34, 56, 34, 10), "#0b0b10", "", w=5, seed=1400, ink_color=c)
    o += shape(rect_pts(56, -14, 70, 14, 4), c, "", w=3, seed=1401, ink=False)
    o += blob(rect_pts(-62, -26, -40, 26, 4), c)
    return f'<g transform="translate({x} {y}) scale({k:.3f})" opacity="{blink:.2f}">{o}</g>'


def face_reflection(ex, tk):
    """Отражение лица Димы на чёрном экране — плоские тёмно-серые формы без прозрачности (волосы, овал лица, глаза, брови)."""
    col, col2 = "#23252f", "#2f323f"
    o = [blob(ellipse_pts(0, 40, 108, 126, 20), col2)]
    o.append(blob([(-112, 10), (-90, -90), (-30, -120), (40, -110), (100, -70), (112, 0), (70, -40), (0, -62), (-60, -44)], col))
    for sx in (-44, 44):
        o.append(blob(ellipse_pts(sx, 18, 18, 22 * (1 - .9 * ex), 10), "#c9ccd8"))
        o.append(blob(ellipse_pts(sx + 3, 22, 7, 8 * (1 - .9 * ex), 8), "#23252f"))
    o.append(line([(-66, -14), (-22, -24)], 7, col, seed=1410))
    o.append(line([(22, -26), (66, -12)], 7, col, seed=1411))
    o.append(line([(-30, 96), (0, 90), (30, 98)], 6, col, seed=1412))
    return f'<g transform="translate(0 20) scale({tk:.3f})">{"".join(o)}</g>'


def outlet(x, y, k=1.0):
    o = shape(rect_pts(-80, -80, 80, 80, 22), "#f4efe6", blob(rect_pts(30, -80, 80, 80, 22), "#d6cfc0"), w=6, seed=1420)
    for sx in (-30, 30):
        o += shape(rect_pts(sx - 9, -26, sx + 9, 26, 5), "#2a2a30", "", w=3, seed=1421 + sx, ink=False)
    o += blob(ellipse_pts(0, 56, 7, 7, 8), "#bdb5a2")
    return f'<g transform="translate({x} {y}) scale({k})">{o}</g>'


def arrow(pts, prog, col="#e0453a", w=14, seed=1430):
    """Рукописная стрелка вдоль pts (прорисовывается по prog 0..1)."""
    if prog <= 0:
        return ""
    S = lib.sample(pts, False, 6)
    n = max(3, int(len(S) * clamp(prog)))
    P = [tuple(p) for p in S[:n]]
    o = line(P, w, col, taper=.3, wmin=.5, seed=seed)
    if prog > .92:
        a, b = np.array(S[-3]), np.array(S[-1])
        d = (b - a) / (np.linalg.norm(b - a) + 1e-9)
        nn = np.array([-d[1], d[0]])
        h = 46
        o += line([tuple(b - d * h + nn * h * .55), tuple(b + d * 6), tuple(b - d * h - nn * h * .55)], w, col, taper=.2, wmin=.6, seed=seed + 1)
    return o


def s02(t):
    tk = 0.0
    # тычок в кнопку: два нажатия на 1.65 и 2.1 (пальцы Димы слева)
    press = max(bump(t, 1.55, .22), bump(t, 2.0, .22))
    blink = 1.0 if (t > 1.5 and (1.56 < t < 1.9 or 2.01 < t < 2.4)) else 0.0
    if 2.55 < t < 2.7:
        blink = 1.0
    ey = clamp(1 - bump(t, 1.2, .2) - bump(t, 2.5, .2))
    shake = 4 * press * math.sin(t * 90)
    px, py = 560, 800
    inner = face_reflection(.0 if ey > .5 else ey, 1.0 + .03 * osc(t, 1.1))
    inner += battery_icon(0, 60, 1.35 + .1 * press, blink)
    # блик по стеклу
    inner += blob([(-84, -178), (-20, -178), (-84, -60)], "#3a3d4c")
    ph = phone(px + shake, py - 10 * press, 1.65, -3 + 2.5 * osc(t, .8) + 4 * press, inner=inner)
    w = [wall_stripes("#e9d9b6", "#e1cea6", w=140)]
    w.append(outlet(880, 520, 1.15))
    # подставка под телефон и рука Димы, жмущая кнопку слева (палец крупно, под масштаб телефона)
    kw = kw_hand()
    kk = 1.75
    dock = shape(rect_pts(px - 190, py + 318, px + 190, py + 392, 16), "#b98a5a", blob(rect_pts(px - 190, py + 362, px + 190, py + 392, 16), "#8a5a30"), w=6,
                 seed=1451)
    dock += shape(rect_pts(px - 150, py + 296, px + 150, py + 326, 10), "#d2a06a", "", w=5, seed=1452)
    d = np.array([1.0, 0.0])
    tip = np.array([px - 150 + 26 * press, py - 60])
    wr = tip - d * 148 * kk + np.array([0, -25 * kk * -1 * -1 * 1.0])
    wr = np.array([wr[0], tip[1] - 55])
    sl2 = sleeve(wr - d * 10 + np.array([-420, 110]), wr, .62 * 2.4, 1470)
    h2 = Hand.hand(wr, d, flip=-1, k=kk, curl=(0, .95, .95, .9), spread=.04, thumb=.85, bend=.03, seed=1480, **kw)
    w.append(dock + ph)
    w.append(sl2 + h2)
    # стрелка к розетке без шнура: на «зарядку»
    a = clamp((t - T_ZAR) / .45)
    if a > 0:
        w.append(arrow([(px + 150, py - 230), (px + 250, py - 330), (700, 380), (800, 440)], a))
        q = back_out(clamp((t - T_ZAR - .35) / .3), 2.5)
        w.append(f'<g transform="translate(880 340) rotate({lib.f(10 * osc(t, 3))}) scale({q:.3f})">{text(0, 0, "?", 120, "#e0453a", stroke=INK, sw=7)}</g>')
    w.append(speed_streaks(px, py, 360, 420, t - 1.5, 10, INK, 1500, 9) if t > 1.5 else "")
    u = clamp((t - 1.3) / 1.5)
    ww = whip(t, 1.3, .2)
    cam = (610 + 20 * u - 260 * ww, 800 - 20 * u, 1.18 + .24 * ease_io(u) + .06 * bump(t, T_ZAR, .3), .8 - 1.4 * u + 2 * ww)
    return compose("".join(w), cam, "#e1cea6")



# ═════════════════════════ s03: офис ═════════════════════════
T_RAB = wi(9)           # «работе» 2.88


def office_chair(x, y, sw):
    """Пустое кресло (вид спереди-сбоку): спинка поворачивается (sw -1..1) — кресло вертится само."""
    o = []
    k = abs(math.cos(sw * .6))
    o.append(blob(ellipse_pts(x, y + 360, 150, 22, 14), "#000000", .18, blur(6)))
    # звезда-основание и колёса
    for dx in (-130, -66, 0, 66, 130):
        yy = y + 340 + (12 if abs(dx) < 70 else 0)
        o.append(line([(x, y + 300), (x + dx * 1.0, yy)], 12, "#2a2a32", taper=.1, wmin=.9, seed=1600 + dx))
        o.append(shape(ellipse_pts(x + dx, yy + 18, 17, 17, 10), "#1f1f26", "", w=4, seed=1610 + dx))
    o.append(shape(rect_pts(x - 14, y + 140, x + 14, y + 300), "#6a6e7a", "", w=4, seed=1620))
    o.append(shape(rect_pts(x - 150 * k, y + 100, x + 150 * k, y + 150, 16), "#3d4c6e", blob(rect_pts(x, y + 100, x + 150 * k, y + 150, 16), "#2c3854"), w=5, seed=1621))
    o.append(shape(rect_pts(x - 22, y + 60, x + 22, y + 112, 6), "#2c3854", "", w=4, seed=1623))
    bk = rect_pts(x - 120 * k, y - 270, x + 120 * k, y + 80, 40)
    o.append(shape(bk, "#4a5e86", blob(rect_pts(x + 20 * k, y - 270, x + 120 * k, y + 80, 40), "#3a4a6e") +
                   line([(x - 40 * k, y - 220), (x - 40 * k, y + 10)], 3, "#6f84ad", seed=1630), w=6, seed=1622))
    return "".join(o)


def s03(t):
    e = t - T_RAB
    lights = smooth(3.05, 3.7, t)       # свет гаснет
    w = []
    w.append(f'<rect x="-400" y="-400" width="2000" height="2600" fill="#d6e0e3"/>')
    w.append(f'<rect x="-400" y="1000" width="2000" height="60" fill="#c0ccd0"/>')
    # окно
    w.append(shape(rect_pts(110, 220, 430, 640, 10), "#bfe0f2", blob(rect_pts(110, 220, 430, 330, 10), "#e6f4fb") + "".join(
        blob(rect_pts(150 + 60 * j, 380 + 100 * (j % 2), 190 + 60 * j, 640), "#a6c3d4") for j in range(4)), w=6, seed=1640))
    w.append(line([(270, 220), (270, 640)], 6, INK, seed=1641, taper=.05, wmin=.9) + line([(110, 430), (430, 430)], 6, INK, seed=1642, taper=.05, wmin=.9))
    # стол
    w.append(shape(rect_pts(-120, 1090, 1260, 1140, 8), "#c98f5a", blob(rect_pts(-120, 1120, 1260, 1140, 8), "#a8723f"), w=6, seed=1650))
    w.append(shape(rect_pts(-80, 1140, 1220, 1560), "#b98050", blob(rect_pts(-80, 1140, 1220, 1190), "#8a5a30") + line([(500, 1190), (500, 1560)], 4, INK, seed=1651) +
                   shape(rect_pts(520, 1230, 1100, 1380, 12), "#c98f5a", "", w=4, seed=1652) + shape(rect_pts(760, 1290, 860, 1310, 8), "#6a4a2a", "", w=3, seed=1653),
                   w=6, seed=1654))
    # монитор, клавиатура, кружка
    w.append(shape(rect_pts(450, 1020, 650, 1092, 6), "#5a5e6a", "", w=5, seed=1655))
    w.append(shape(rect_pts(380, 560, 760, 880, 16), "#2a2c36", shape(rect_pts(398, 578, 742, 862, 8), "#12131a", blob([(398, 578), (500, 578), (398, 720)], "#23252f"), w=3, seed=1657) +
                   shape(rect_pts(540, 880, 600, 1030, 4), "#5a5e6a", "", w=4, seed=1658), w=6, seed=1656))
    w.append(shape(rect_pts(430, 1040, 700, 1092, 10), "#aeb4c0", "".join(line([(450 + 24 * j, 1062), (462 + 24 * j, 1062)], 5, "#7a8090", seed=1660 + j) for j in range(10)), w=5, seed=1659))
    w.append(shape(rect_pts(820, 990, 900, 1092, 10), "#f4efe6", blob(rect_pts(868, 990, 900, 1092, 10), "#d6cfc0") + line([(900, 1020), (934, 1040), (900, 1070)], 6, INK, seed=1665), w=5, seed=1664))
    # розетка и зарядка одна
    ox, oy = 1010, 840
    w.append(shape(rect_pts(ox - 70, oy - 70, ox + 70, oy + 70, 18), "#f4efe6", blob(rect_pts(ox + 20, oy - 70, ox + 70, oy + 70, 18), "#d6cfc0"), w=5, seed=1670))
    sw = 8 * osc(t, .7)
    cx0, cy0 = ox, oy + 6
    cable = [(cx0, cy0 + 70), (cx0 - 40 + sw, cy0 + 150), (cx0 - 120 + sw * 1.4, cy0 + 220), (cx0 - 90, 1070), (cx0 - 170, 1082), (cx0 - 240, 1078)]
    w.append(line(cable, 10, "#f4efe6", taper=.05, wmin=.95, seed=1671, extra=f'stroke="{INK}" stroke-width="3"'))
    w.append(shape(rect_pts(cx0 - 52, cy0 - 56, cx0 + 52, cy0 + 70, 20), "#fbfaf6", blob(rect_pts(cx0 + 16, cy0 - 56, cx0 + 52, cy0 + 70, 20), "#dad5c8"), w=5, seed=1672))
    glow = 1.0 if lights < .1 else 1.0
    w.append(blob(ellipse_pts(cx0, cy0 + 40, 8, 8, 8), mix("#8be07a", "#c8ff9a", lights)))
    w.append(shape(rect_pts(cx0 - 270, 1072, cx0 - 226, 1094, 6), "#aeb4c0", "", w=4, seed=1673))
    # пустое кресло слева-сзади, вертится
    w.append(office_chair(190, 850, osc(t, .5) + .3))
    # свет гаснет: тёмная синяя пелена на мир, окно и зарядка остаются виднее по яркости светодиода
    dark = f'<rect x="-400" y="-400" width="2000" height="2600" fill="#0d1230" opacity="{.62 * lights:.3f}"/>'
    w.append(dark)
    w.append(blob(ellipse_pts(cx0, cy0 + 40, 26, 26, 12), "#8be07a", .55 * lights, blur(6)))
    # ярлык «ОФИС»
    sign = ""
    if e > -0.01:
        k = back_out(clamp(e / .22), 2.4)
        rot = -7 * (1 - k) + 2.5 * decay(t, T_RAB, 4, 3)
        yoff = 60 * math.exp(-e * 6) * 0
        pl = shape(rect_pts(-280, -100, 280, 100, 28), "#f2c23a", blob(rect_pts(-280, 40, 280, 100, 28), "#d9a521") +
                   blob(ellipse_pts(-230, -50, 14, 14, 8), "#fff3b0"), w=8, seed=1680)
        strs = line([(-200, -100), (-130, -520)], 6, INK, taper=.05, wmin=.9, seed=1681) + line([(200, -100), (130, -520)], 6, INK, taper=.05, wmin=.9, seed=1682)
        sign = (f'<g transform="translate(540 440) rotate({lib.f(rot)} 0 -520) scale({lib.f(.5 + .5 * k)})">{strs}{pl}{text(0, 44, "ОФИС", 140)}</g>')
        sign += speed_streaks(540, 440, 330, 400, e, 14, INK, 1690, 11)
    cam_u = clamp((t - 2.6) / 1.4)
    ww = whip(t, 2.6, .22)
    kick = decay(t, T_RAB, 8, 5) * 18
    s_ = 1.05 + .12 * ease_io(cam_u) + .05 * bump(t, T_RAB, .25)
    cam = (570 + 40 * cam_u - 320 * ww, 860 + kick - 20 * cam_u, s_, 1.2 * ww - .6 * cam_u)
    return compose("".join(w) + sign, cam, "#d6e0e3", vcol="#0a1020", vig=.28)


SHOTS = {"s10": s10, "s02": s02, "s03": s03}


def frame(sid, t):
    lib.DEFS.clear()
    return SHOTS[sid](t)
