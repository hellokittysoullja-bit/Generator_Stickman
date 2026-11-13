"""Сцена paper рилса 33: крупно сверху стол — лист/карточка, рука Димы, часы, лапа кота.
Планы s02, s06, s07, s09, s12, s13, s14, s15, s16. frame(sid, t) -> SVG 1080×1920 (t — общее время ролика).
Удары — на словах по voice/words.json. Главное держится выше y=1300 (ниже — субтитры).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import props as Pr  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after and w["word"].lower().strip(".,!?") == word:
            return w["start"]
    raise KeyError(word)


T_27 = wt("двадцать")            # 1.76
T_PUNKT = wt("пунктов")          # 2.48
T_POKR = wt("покрасивее")        # 10.76
T_NOL = wt("ноль")               # 13.76
T_TRI = wt("три", 17)            # 17.92
T_OBED = wt("обеду")             # 19.6
T_TREM = wt("трём")              # 20.72
T_VECH = wt("вечеру")            # 21.68
T_TREH = wt("трёх")              # 23.16
T_LAPOY = wt("лапой")            # 25.04


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def punch(t, t0, amp=.08, up=.06, down=.35):
    if t < t0:
        return 0.0
    if t < t0 + up:
        return amp * ease_out((t - t0) / up, 2)
    return amp * (1 - ease_io(clamp((t - t0 - up) / down)))


def shake(t, t0, amp=14.0, dur=.35):
    u = clamp((t - t0) / dur)
    if t < t0 or u >= 1:
        return 0.0, 0.0, 0.0
    e = (1 - u) ** 2
    return amp * e * osc(t, 17), amp * e * osc(t, 13, 1.3), 1.6 * e * osc(t, 11, .4)


def whip_in(t, t0, dur=.22):
    return (1 - ease_out(clamp((t - t0) / dur), 3)) if t >= t0 else 1.0


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


AY = 700.0       # точка экрана, в которую ставится центр камеры (главное — выше субтитров)


def cam(cx, cy, s, rot=0.0):
    return f"translate(540 {AY}) rotate({rot:.3f}) scale({s:.5f}) translate({-cx:.3f} {-cy:.3f})"


def compose(world, c, front="", light_u=0.0, lcx=200, lcy=200):
    cx, cy, s, r = c
    o = ['<rect width="1080" height="1920" fill="#5a3a22"/>', f'<g transform="{cam(cx, cy, s, r)}">{world}</g>', front,
         Pr.light(light_u, lcx, lcy)]
    return lib.svg("".join(o))


# ═════════════════════════ s02: длинный лист, рука строчит строки 23…27; «двадцать семь» — красный штамп «27» ═════════════════════════
L_X0, L_X1, L_Y0, L_DY = 210.0, 870.0, 260.0, 76.0
N_ROWS = 27


def row_y(i):
    return L_Y0 + (i - 1) * L_DY


def long_rows():
    rs = np.random.RandomState(33)
    out = []
    for i in range(1, N_ROWS + 1):
        x1 = rs.uniform(620, 830) if i < N_ROWS else 640
        out.append(Pr.scribble(L_X0 + 96, x1, row_y(i) + 10, 700 + i, h=17))
    return out


ROWS = long_rows()
ROW_D = .13
ROW_END27 = 1.70


def row_span(i):
    e = ROW_END27 - (N_ROWS - i) * ROW_D
    return e - ROW_D, e


def long_sheet(t, upto_t, num_pop=True):
    """Лист: строки, дописанные к моменту upto_t; текущая строка — частично. Возвращает (svg, острие, перо в воздухе)."""
    top = L_Y0 - 120
    bot = row_y(N_ROWS) + 900
    o = [Pr.sheet([(L_X0 - 40, top), (L_X1 + 30, top - 6), (L_X1 + 36, bot), (L_X0 - 46, bot + 4)], seed=6200, fold=False)]
    # поле: красная линия полей и голубые линейки
    o.append(line([(L_X0 + 66, top + 4), (L_X0 + 70, bot)], 2.6, "#e88a8a", taper=.02, wmin=.95, seed=6201))
    for i in range(1, N_ROWS + 14):
        y = row_y(i) + 26
        if y > bot - 20:
            break
        o.append(f'<rect x="{L_X0 - 36:.0f}" y="{y:.1f}" width="{L_X1 - L_X0 + 66:.0f}" height="2" fill="#bcd3ea"/>')
    tip, air = None, 0.0
    for i in range(1, N_ROWS + 1):
        a, b = row_span(i)
        if upto_t <= a:
            break
        y = row_y(i)
        u = clamp((upto_t - a) / (b - a))
        travel = .26
        if u > 0:
            ps = clamp(u / travel)
            s_ = 1 + .5 * bump(ps, .0, 1.0) if num_pop else 1
            o.append(Pr.text(L_X0 + 30, y + 2, f"{i}", 40 * s_ if ps < 1 else 40, Pr.PEN_INK, rot=-4))
        frac = clamp((u - travel) / (1 - travel))
        st, tp = Pr.reveal(ROWS[i - 1], frac)
        o.append(Pr.pen_path(st, Pr.PEN_INK, 3.6))
        if u < 1:
            if u < travel:          # перелёт от конца прошлой строки к началу новой
                prev_end = ROWS[i - 2][-1][-1] if i > 1 else np.array([L_X0 + 96, y - 60])
                e = ease_io(u / travel)
                start = ROWS[i - 1][0][0]
                tip = prev_end + (start - prev_end) * e
                air = math.sin(math.pi * e)
            else:
                tip = tp
                air = 0.0
    return "".join(o), tip, air


def stamp27(cx, cy, s, rot=-12.0, op=1.0):
    r = 104
    ring1 = ellipse_pts(0, 0, r, r * .96, 30)
    ring2 = ellipse_pts(0, 0, r - 16, (r - 16) * .96, 28)
    g = [f'<path d="{lib.ink_closed(ring1, 11, var=.35, seed=6301)}" fill="{Pr.RED}"/>',
         f'<path d="{lib.ink_closed(ring2, 5, var=.4, seed=6302)}" fill="{Pr.RED}"/>',
         Pr.text(0, 4, "27", 118, Pr.RED)]
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f}) scale({s:.4f})">{"".join(g)}</g>'


def s02(t):
    tw = min(t, ROW_END27)
    body, tip, air = long_sheet(t, tw)
    w = [Pr.wood(), body]
    # камера: следует за острием вниз по листу; после штампа — отъезд, виден весь длинный лист
    follow = row_y(N_ROWS) if tip is None else tip[1]
    k = ease_io(clamp((t - 1.98) / 1.1))
    s = 1.18 + (.74 - 1.18) * k
    cy_f = follow - 220 / 1.18
    cy_w = row_y(N_ROWS) - 330 / .74
    cyy = cy_f + (cy_w - cy_f) * k
    s *= 1 + punch(t, T_27, .07, .05, .35) + .025 * bump(t, T_PUNKT, .3)
    sx, sy, sr = shake(t, T_27, 18, .4)
    c = (560 - 10 * k + sx, cyy + sy, s, -2.0 + 1.5 * k + sr + .6 * osc(t, .7))
    set_ink(s)
    # рука: пишет до 1.70, потом отдёргивается вниз-вправо
    if t < ROW_END27 + .02 and tip is not None:
        ang = 46 + 4 * osc(t, 3.1) + 3 * air
        w.append(Pr.hand((tip[0], tip[1]), ang, 1.3, "pen", "#3b6fd8", lift=air + .15 * abs(osc(t, 7)), seed=0))
    else:
        end = ROWS[N_ROWS - 1][-1][-1]
        u = ease_in(clamp((t - ROW_END27) / .3), 2)
        if u < 1:
            w.append(Pr.hand((end[0] + 700 * u, end[1] + 1000 * u), 32 + 10 * u, 1.3, "pen", "#3b6fd8", lift=1.0, seed=0))
    # штамп «27»: падает сверху (с экрана), удар на 1.76
    scx, scy = 735, row_y(N_ROWS) + 6
    if t > T_27 - .14:
        u = clamp((t - (T_27 - .14)) / .14)
        sc = 2.6 - 1.6 * ease_in(u, 2)
        if t > T_27:
            v = t - T_27
            sc = 1 + .1 * math.exp(-9 * v) * math.cos(v * 30)
            w.append(Pr.burst(scx, scy, clamp(v / .32), 120, 200, 12, Pr.RED, 8, seed=6410))
        if u < 1:
            w.append(blob(ellipse_pts(scx + 20 * sc, scy + 34 * sc, 110 * sc, 104 * sc, 20), "#1a0c04", .25 * u, lib.blur(12)))
        w.append(stamp27(scx, scy, sc))
    return compose("".join(w), c, light_u=0.0)


# ═════════════════════════ красивый список (s06 — переписывает, s07 — готов, s09 — вечер, «0 / 27») ═════════════════════════
PX0, PX1, PY0, PY1 = 110.0, 970.0, 110.0, 1272.0
GROUP_COL = ["#e8508a", "#2f9e5a", "#3f7fd8"]


def prow_y(i):
    return 372 + (i - 1) * 32.4


def pretty_rows():
    rs = np.random.RandomState(270)
    out = []
    for i in range(1, N_ROWS + 1):
        x1 = rs.uniform(640, 860)
        out.append(Pr.scribble(262, x1, prow_y(i) + 6, 900 + i, h=9.5, pitch=8.5))
    return out


PROWS = pretty_rows()
HEARTS = [(170, 4, 0), (918, 9, 1), (170, 13, 2), (918, 18, 3), (170, 22, 4), (918, 26, 5)]
STARS = [(918, 5, 0), (170, 9, 1), (918, 14, 2), (170, 18, 3), (918, 22, 4), (170, 26, 5)]


def curl_line(cx, cy, s, flip=1, seed=0):
    pts = []
    for a in np.linspace(0, 3.2 * math.pi, 40):
        r = 4 + a * 4.2
        pts.append((cx + flip * (r * math.cos(a)) * s, cy + r * math.sin(a) * s * .8))
    return line(pts[::-1] + [(cx + flip * 95 * s, cy - 4 * s)], 4.2, "#e8508a", taper=.4, wmin=.5, seed=seed)


def title27(cx, cy, k=1.0):
    o = []
    box_ = lib.rect_pts(cx - 120 * k, cy - 70 * k, cx + 120 * k, cy + 70 * k, 30 * k)
    o.append(shape(box_, "#fff1c9", "", w=4.6, seed=6601, ink_color="#e8508a"))
    o.append(f'<path d="{lib.ink_closed(lib.rect_pts(cx - 104 * k, cy - 55 * k, cx + 104 * k, cy + 55 * k, 22 * k), 2.6, seed=6602)}" fill="#f29abb"/>')
    o.append(Pr.text(cx, cy + 4 * k, "27", 92 * k, "#e8508a", rot=-3, stroke="#ffffff", sw=6))
    o.append(curl_line(cx - 128 * k, cy, k, -1, 6603))
    o.append(curl_line(cx + 128 * k, cy, k, 1, 6604))
    return "".join(o)


def pretty_sheet(t, done=27, cur=None, deco=0.0, last_star=1.0, glow=0.0):
    """Красивый лист: done — сколько строк готово; cur — (номер, доля) строка в работе; deco 0..1 — украшения
    (рамка, сердечки, звёзды, проявляются по очереди); last_star — масштаб последней звезды у заголовка.
    Возвращает (svg, острие пера или None)."""
    o = [Pr.sheet([(PX0, PY0), (PX1, PY0 + 4), (PX1 + 4, PY1), (PX0 - 2, PY1 - 2)], seed=6600)]
    if deco > 0:
        r = lib.rect_pts(PX0 + 24, PY0 + 26, PX1 - 22, PY1 - 26, 26)
        d = lib.fill_d(r)
        o.append(f'<path d="{d}" fill="none" stroke="#7cc4e4" stroke-width="5" stroke-dasharray="22 12" stroke-linecap="round" '
                 f'opacity="{clamp(deco * 3):.3f}"/>' if deco < 1 / 3 else
                 f'<path d="{d}" fill="none" stroke="#7cc4e4" stroke-width="5" stroke-dasharray="22 12" stroke-linecap="round"/>')
    o.append(title27(540, 228))
    tip = None
    n_show = done + (1 if cur else 0)
    for i in range(1, min(n_show, N_ROWS) + 1):
        y = prow_y(i)
        g = (i - 1) // 9
        col = GROUP_COL[g]
        frac = 1.0
        if cur and i == cur[0]:
            frac = cur[1]
        if (i - 1) % 9 == 0:          # заголовок группы — полоса маркера
            hl = clamp(frac / .3)
            x1 = 250 + (PROWS[i - 1][-1][-1][0] + 16 - 250) * hl
            o.append(f'<rect x="246" y="{y - 13:.1f}" width="{max(0, x1 - 246):.1f}" height="27" rx="9" fill="#ffe36a"/>')
        nfr = clamp(frac / .2)
        if nfr > 0:
            o.append(Pr.text(222, y + 3, f"{i}.", 22 * (1 + .4 * bump(nfr, 0, 1)), col))
        st, tp = Pr.reveal(PROWS[i - 1], clamp((frac - .2) / .8))
        o.append(Pr.pen_path(st, col, 3.2 if (i - 1) % 9 else 3.8))
        if cur and i == cur[0] and frac < 1:
            tip = tp if frac >= .2 else np.array([222.0, y])
    if deco > 0:
        items = [("h", *h) for h in HEARTS] + [("s", *s_) for s_ in STARS]
        items.sort(key=lambda q: q[3] + (0 if q[0] == "h" else .5))
        for j, (kind, x, row, _) in enumerate(items):
            u = clamp(deco * len(items) - j)
            if u <= 0:
                continue
            sc = Pr.lib.clamp(1) * (1 + .35 * bump(u, 0, 1)) * min(1, u * 2.5)
            y = prow_y(row)
            if kind == "h":
                o.append(Pr.heart(x, y, 21 * sc, "#ef5b8c", rot=-10 + row * 3, seed=6700 + j, w=2.6))
            else:
                o.append(Pr.star(x, y, 23 * sc, "#f4c430", rot=row * 7, seed=6750 + j, w=2.6))
        o.append(Pr.star(356, 196, 22 * min(1, deco * 2), "#f4c430", rot=-8, seed=6790, w=3))
    if last_star > 0:
        o.append(Pr.star(726, 168, 30 * last_star, "#f4c430", rot=12, seed=6791, w=3.2))
    return "".join(o), tip


def desk_bits(t, evening=False):
    o = [Pr.crumpled(40, 560, 86, rot=20, seed=5701), Pr.marker_lying(1060, 930, 72, "#f4c430", seed=5601, k=.9),
         Pr.marker_lying(1100, 640, 96, "#e8508a", seed=5602, k=.9)]
    return "".join(o)


def s06(t):
    # строки 10–14 зелёной группой; каждая — 0.42 с, линейка под строкой переезжает
    rows = [(10 + j, 8.48 + j * .43) for j in range(5)]
    cur, done = None, 9
    for i, a in rows:
        if t >= a + .33:
            done = i
        elif t >= a:
            cur = (i, (t - a) / .33)
            break
    body, tip = pretty_sheet(t, done, cur, deco=0.0, last_star=0.0)
    w = [Pr.wood(), body, Pr.crumpled(215, 1060, 92, rot=20, seed=5701), Pr.marker_lying(800, 1130, 18, "#f4c430", seed=5601, k=.9),
         Pr.marker_lying(700, 1210, -8, "#e8508a", seed=5602, k=.9)]
    # линейка: под текущей строкой, переезжает вниз между строками
    ri = cur[0] if cur else done + 1
    ry_t = prow_y(min(ri, N_ROWS)) + 30
    ry_p = prow_y(min(ri - 1, N_ROWS)) + 30
    a_cur = dict(rows).get(ri, t)
    u = ease_io(clamp((t - (a_cur - .1)) / .1)) if cur is None else 1.0
    ry = ry_p + (ry_t - ry_p) * (u if cur is None else 1)
    w.append(Pr.ruler(560, ry + 16, 660, 54, rot=-.6, seed=5501))
    # рука с зелёным маркером
    if tip is None:
        nxt = PROWS[min(done, N_ROWS - 1)][0][0]
        prev = PROWS[done - 1][-1][-1]
        a_n = dict(rows).get(done + 1, t + .05)
        e = ease_io(clamp((t - (a_n - .1)) / .1)) if a_n - .1 < t else 0
        tip = prev + (np.array([222.0, prow_y(done + 1)]) - prev) * e
        air = 1.0
    else:
        air = 0.0
    w.append(Pr.hand((tip[0], tip[1]), 46 + 3 * osc(t, 2.3), .72, "marker", "#2f9e5a", lift=air * .6, seed=10))
    kk = ease_io(clamp((t - 8.6) / 1.8))
    s = 1.42 + .08 * kk
    wh = whip_in(t, 8.6, .22)
    c = (500 + 60 * kk + 260 * wh, prow_y(12) - 150 + 20 * kk, s, 1.2 - 1.8 * kk)
    set_ink(s)
    return compose("".join(w), c, light_u=0.05)


def s07(t):
    ts = T_POKR
    body, _ = pretty_sheet(t, 27, None, deco=1.0, last_star=0.0)
    w = [Pr.wood(), body, desk_bits(t)]
    sx_, sy_ = 726, 168
    if t >= ts:
        v = t - ts
        sc = min(1.0, v / .06) * (1 + .45 * math.exp(-7 * v) * math.sin(v * 26 + .3))
        w.append(Pr.star(sx_, sy_, 30 * sc, "#f4c430", rot=12 + 40 * math.exp(-6 * v), seed=6791, w=3.2))
        for j in range(4):
            a = j * 90 + 45
            r = 50 + 60 * ease_out(clamp(v / .4))
            gu = clamp(v / .5)
            w.append(Pr.glint(sx_ + r * math.cos(math.radians(a)), sy_ + r * math.sin(math.radians(a)), 18 * math.sin(math.pi * gu), "#fff2a8",
                              rot=v * 120))
        w.append(Pr.glint(sx_ + 6, sy_ - 4, 70 * math.sin(math.pi * clamp(v / .35)), "#ffffff", rot=15))
    # рука с жёлтым маркером: приходит снизу справа, ставит звезду, уходит
    ta, tb = ts - .5, ts + .06
    if t < tb:
        e = ease_out(clamp((t - ta) / (tb - ta - .08)), 3)
        tip = np.array([sx_ + 520 * (1 - e), sy_ + 820 * (1 - e)])
        lift = 1 - e * .8 if t < ts - .02 else 0.0
        if t > ts - .08:
            tip = np.array([sx_, sy_ - 22 * (1 - clamp((t - (ts - .08)) / .08))])
    else:
        e = ease_in(clamp((t - tb - .1) / .5), 2)
        tip = np.array([sx_ + 640 * e, sy_ + 940 * e + 30 * bump(t, tb, .25)])
        lift = .6 + .4 * e
    w.append(Pr.hand((tip[0], tip[1]), 30, 1.05, "marker", "#f4c430", lift=lift, seed=20))
    kk = ease_io(clamp((t - 10.0) / 1.88))
    s = (1.08 + .32 * kk) * (1 + punch(t, ts, .05, .05, .35))
    c = (540 + 60 * kk, 690 - 220 * kk, s, -.6 + 1.0 * kk)
    set_ink(s)
    return compose("".join(w), c, light_u=0.1)


def stamp0(cx, cy, s, rot=-9.0):
    g = []
    r = lib.rect_pts(-300, -110, 300, 110, 30)
    g.append(f'<path d="{lib.ink_closed(r, 14, var=.35, seed=6801)}" fill="{Pr.RED}"/>')
    g.append(f'<path d="{lib.ink_closed(lib.rect_pts(-276, -88, 276, 88, 20), 5, var=.4, seed=6802)}" fill="{Pr.RED}"/>')
    g.append(Pr.text(0, 6, "0 / 27", 132, Pr.RED, stroke="#fbf3e2", sw=10))
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f}) scale({s:.4f})">{"".join(g)}</g>'


def s09(t):
    tn = T_NOL
    body, _ = pretty_sheet(t, 27, None, deco=1.0, last_star=1.0)
    # лист подпрыгивает от удара
    hop = 0.0
    if t > tn:
        v = t - tn
        hop = -46 * math.exp(-6 * v) * abs(math.sin(v * 14))
    sq = 1 - .03 * bump(t, tn, .14)
    w = [Pr.wood(), desk_bits(t), Pr.pen_lying(1010, 1180, -60, seed=5611),
         f'<g transform="translate(540 {690 + hop:.1f}) scale(1 {sq:.4f}) translate(-540 -690)">{body}</g>']
    scx, scy = 540, 700
    if t > tn - .14:
        u = clamp((t - (tn - .14)) / .14)
        sc = 2.4 - 1.4 * ease_in(u, 2)
        if t > tn:
            v = t - tn
            sc = 1 + .08 * math.exp(-9 * v) * math.cos(v * 30)
            w.append(Pr.burst(scx, scy, clamp(v / .35), 280, 420, 14, Pr.RED, 10, seed=6810))
        else:
            w.append(blob([(scx - 300 * sc + 30, scy - 110 * sc + 50, 1), (scx + 300 * sc + 30, scy - 110 * sc + 50, 1),
                           (scx + 300 * sc + 30, scy + 110 * sc + 50, 1), (scx - 300 * sc + 30, scy + 110 * sc + 50, 1)], "#1a0c04", .25 * u,
                          lib.blur(14)))
        w.append(f'<g transform="translate(0 {hop:.1f})">{stamp0(scx, scy, sc)}</g>')
    kk = ease_io(clamp((t - 12.94) / 1.5))
    s = (1.12 + .1 * kk) * (1 + punch(t, tn, .07, .05, .35))
    sx, sy, sr = shake(t, tn, 20, .45)
    wh = whip_in(t, 12.94, .22)
    c = (540 + sx - 240 * wh, 690 + sy + 10 * kk, s, .8 - 1.2 * kk + sr)
    set_ink(s)
    return compose("".join(w), c, light_u=1.0, lcx=820, lcy=300)


# ═════════════════════════ карточка (s12–s16): «1. 2. 3.», квадратики, галочки, часы, лапа ═════════════════════════
CARD_C = (520.0, 700.0)
CARD_R = -3.0
ROWY = [530.0, 700.0, 870.0]
BOX_X = 446.0
NUM_X = 340.0
CARD_ROWS = [Pr.scribble(510, 770 - j * 40, ROWY[j] + 12, 1300 + j, h=18, pitch=14) for j in range(3)]
ROW_A = [17.0, 17.44, 17.86]          # начало строк (номер → квадратик → каракули)
CHECK_T = [T_OBED, T_TREM]            # 19.6, 20.72
HAND_K = .92
PEN_REST = ((598.0, 936.0), 24.0)    # где ручка ляжет (острие, угол): на нижний угол карточки


def card_xy(p):
    """Точка карточки → мир (поворот карточки)."""
    return Pr.lib.T([p], CARD_C[0], CARD_C[1], 1, CARD_R, 0, 0)[0] if False else _crot(p)


def _crot(p):
    a = math.radians(CARD_R)
    x, y = p[0] - CARD_C[0], p[1] - CARD_C[1]
    return np.array([CARD_C[0] + x * math.cos(a) - y * math.sin(a), CARD_C[1] + x * math.sin(a) + y * math.cos(a)])


def card(t, checks=(0.0, 0.0), paw_u=0.0, hop=0.0):
    """Карточка-стикер. checks — доли двух галочек; paw_u — проявление отпечатка лапы в третьем квадратике.
    Возвращает (svg, острие пера для текущего действия письма или None)."""
    cx, cy = CARD_C
    o = []
    pts = [(cx - 280, cy - 280), (cx + 280, cy - 284), (cx + 284, cy + 280), (cx - 282, cy + 284)]
    inner = blob([(cx - 290, cy - 290), (cx + 290, cy - 290), (cx + 290, cy - 236), (cx - 290, cy - 230)], "#f4cf55", .9)
    inner += blob([(cx + 284, cy + 200), (cx + 284, cy + 284), (cx + 200, cy + 284)], "#f0c64a", .9)
    body = [Pr.soft_shadow(pts, 14, 22, .32, 10), shape([p + (1,) for p in pts], "#ffe27a", inner, w=4.6, seed=6900)]
    tip = None
    for j in range(3):
        a = ROW_A[j]
        y = ROWY[j]
        if t < a:
            break
        u_num = clamp((t - a) / .08)
        sc = 1 + .45 * bump(u_num, 0, 1) if u_num < 1 else 1
        body.append(Pr.text(NUM_X, y + 4, f"{j + 1}.", 64 * sc, Pr.PEN_INK, rot=-4))
        bsv, btip = Pr.box(BOX_X, y + 2, 1.0, clamp((t - a - .08) / .12), seed=5800 + j)
        body.append(bsv)
        st, stip = Pr.reveal(CARD_ROWS[j], clamp((t - a - .2) / .22))
        body.append(Pr.pen_path(st, Pr.PEN_INK, 4.4))
        if t < a + .42:
            tip = np.array([NUM_X + 20, y + 10]) if t < a + .08 else (btip if t < a + .2 else stip)
    for j in range(2):
        if checks[j] > 0:
            csv_, ctip = Pr.check(BOX_X + 4, ROWY[j] - 2, 1.25, checks[j])
            body.append(csv_)
            if checks[j] < 1:
                tip = ctip
    if paw_u > 0:
        body.append(Pr.paw_print(BOX_X + 2, ROWY[2] + 6, .78 * (1 + .25 * (1 - ease_out(paw_u))), rot=-8))
    g = "".join(body)
    o.append(f'<g transform="translate(0 {-hop:.1f}) rotate({CARD_R} {cx} {cy})">{g}</g>')
    if tip is not None:
        tip = _crot(tip) - np.array([0, hop])
    return "".join(o), tip


def clock_m(t):
    """Минуты суток на часах."""
    if t < 18.84:
        return 9 * 60 + 40 + (t - 17.0) * 2
    if t < 20.2:
        return 13 * 60
    if t < 20.62:
        return 13 * 60 + 120 * ease_io((t - 20.2) / .42)
    if t < 21.2:
        return 15 * 60
    if t < 21.66:
        return 15 * 60 + 240 * ease_io((t - 21.2) / .46)
    return 19 * 60


def clock_now(t):
    m = clock_m(t)
    mm = m % 60
    roll = clamp((mm - 48) / 12) if 20.2 < t < 21.66 else 0.0
    shown = m - mm + (0 if roll == 0 else 0)
    jolt = bump(t, 20.62, .2) + bump(t, 21.66, .2)
    icon = "sun" if m < 17 * 60 else "dusk"
    return Pr.clock(752, 278 + 6 * jolt * osc(t, 20), shown + (int(mm) if roll == 0 else 0), .8, roll=roll, icon=icon, icon_t=t)


def evening_u(t):
    return smooth(21.25, 21.75, t)


def card_world(t, checks=(0.0, 0.0), paw_u=0.0, hop=0.0, pen_rest=False):
    c_svg, tip = card(t, checks, paw_u, hop)
    w = [Pr.wood(), clock_now(t)]
    # пятно солнца из окна (днём — светлое слева, вечером — длинное оранжевое)
    eu = evening_u(t)
    sun = [(-300, 120 + 300 * eu), (420 - 120 * eu, 40 + 260 * eu), (300 - 60 * eu, 1500), (-300, 1500)]
    col = lib.mix("#fff3d0", "#ffb15a", eu)
    w.append(blob([p + (1,) for p in sun], col, .22 + .08 * eu, lib.blur(30) + ' style="mix-blend-mode:screen"'))
    w.append(c_svg)
    if pen_rest:
        w.append(Pr.pen_at(*PEN_REST, HAND_K))
    return w, tip


def hover_path(t, pts):
    """Кусочная траектория [(t, x, y, ang, lift)] с ease_io между ключами."""
    if t <= pts[0][0]:
        return pts[0][1:]
    for a, b in zip(pts, pts[1:]):
        if t <= b[0]:
            e = ease_io((t - a[0]) / (b[0] - a[0]))
            return tuple(a[i] + (b[i] - a[i]) * e for i in range(1, len(a)))
    return pts[-1][1:]


def card_cam(t, s, dx=0.0, dy=0.0, r=0.0):
    set_ink(s * 1.36)
    return (536 + dx, 622 + dy, s * 1.36, r)


def s12(t):
    hop = 26 * bump(t, T_TRI, .28)
    w, tip = card_world(t, hop=hop)
    if tip is None:
        # между строками: перелёт к следующей; после третьей — отдых у карточки
        if t < ROW_A[2]:
            j = 0 if t < ROW_A[1] else 1
            a0 = CARD_ROWS[j][-1][-1]
            a1 = np.array([NUM_X + 20, ROWY[j + 1] + 10])
            e = ease_io(clamp((t - (ROW_A[j + 1] - .02)) / .02))
            tip = _crot(a0 + (a1 - a0) * e)
            lift = 1.0
        else:
            end = _crot(CARD_ROWS[2][-1][-1])
            x, y, _ = hover_path(t, [(18.28, end[0], end[1], 0), (18.6, 760, 980, 0)])
            tip = np.array([x, y + 4 * osc(t, 1.3)])
            lift = .6
    else:
        lift = 0.0
    w.append(Pr.hand(tuple(tip), 46 + 3 * osc(t, 2.1), HAND_K, "pen", "#3b6fd8", lift=lift, seed=30))
    kk = ease_io(clamp((t - 17.2) / 1.84))
    s = (1.06 + .06 * kk) * (1 + punch(t, T_TRI, .05, .05, .3))
    return compose("".join(w), card_cam(t, s, -20 + 40 * kk, 10 - 20 * kk, -.8 + 1.2 * kk), light_u=0.0)


def check_tip(j):
    return _crot(np.array([BOX_X + 4 - 26 * 1.25, ROWY[j] - 2 - 2 * 1.25]))


def s13(t):
    tc = T_OBED
    ch0 = clamp((t - (tc - .14)) / .14)
    w, tip = card_world(t, (ch0, 0.0))
    if tip is None:
        a = check_tip(0)
        if t < tc - .14:
            x, y = hover_path(t, [(18.64, 770, 990, 0), (19.0, 700, 900, 0), (tc - .14, a[0], a[1], 0)])[:2]
            tip, lift = np.array([x, y]), 1.0
        else:
            end = Pr.check(BOX_X + 4, ROWY[0] - 2, 1.25, 1)[1]
            end = _crot(end)
            x, y = hover_path(t, [(tc, end[0], end[1], 0), (tc + .35, end[0] + 160, end[1] + 230, 0)])[:2]
            tip, lift = np.array([x, y]), .7
    else:
        lift = 0.0
    w.append(Pr.hand(tuple(tip), 46 + 3 * osc(t, 2.1), HAND_K, "pen", "#3b6fd8", lift=lift, seed=30))
    if t > tc:
        v = t - tc
        bx = _crot(np.array([BOX_X + 60, ROWY[0] - 50]))
        sc = min(1, v / .06) * (1 + .5 * math.exp(-7 * v) * math.sin(v * 24 + .4))
        w.append(Pr.star(bx[0], bx[1], 30 * sc, "#f4c430", rot=20 * math.exp(-5 * v), seed=6950))
        w.append(Pr.glint(bx[0] + 40, bx[1] - 30, 22 * math.sin(math.pi * clamp(v / .4)), "#fff6c8", rot=v * 90))
    kk = ease_io(clamp((t - 18.64) / 1.72))
    s = (1.12 + .05 * kk) * (1 + punch(t, tc, .06, .05, .3))
    sx, sy, sr = shake(t, tc, 8, .25)
    return compose("".join(w), card_cam(t, s, 10 - 30 * kk + sx, -10 + sy, .6 - 1 * kk + sr), light_u=0.0)


def s14(t):
    tc, tv = T_TREM, T_VECH
    ch1 = clamp((t - (tc - .14)) / .14)
    pen_down = t > 22.06
    w, tip = card_world(t, (1.0, ch1), pen_rest=pen_down)
    a = check_tip(1)
    b3 = _crot(np.array([BOX_X + 2, ROWY[2] - 30]))
    e1 = _crot(Pr.check(BOX_X + 4, ROWY[1] - 2, 1.25, 1)[1])
    rest = PEN_REST[0]
    tool = "pen"
    ang = 46.0
    if tip is None:
        if t < tc - .14:
            x, y = hover_path(t, [(19.96, 860, 1040), (20.3, 760, 900), (tc - .14, a[0], a[1])])[:2]
            lift = 1.0
        else:
            # зависает над третьим квадратиком, колеблется, откладывает ручку
            keys = [(tc, e1[0], e1[1]), (tc + .3, b3[0] + 30, b3[1] - 20), (21.2, b3[0] + 10, b3[1] - 10),
                    (21.75, b3[0] + 18, b3[1] - 16), (22.06, rest[0], rest[1])]
            x, y = hover_path(t, keys)[:2]
            if tc + .3 < t < 21.9:
                x += 9 * osc(t, 2.6)
                y += 6 * osc(t, 3.4, 1)
            lift = 1.0 if t < 22.0 else .3
            ang = 46 + (PEN_REST[1] - 46) * smooth(21.8, 22.06, t)
            if t > 22.06:
                v = ease_in(clamp((t - 22.08) / .4), 2)
                x, y = rest[0] + 300 * v, rest[1] + 520 * v
                tool = "none"
                lift = .5
        tip = np.array([x, y])
    else:
        lift = 0.0
    w.append(Pr.hand(tuple(tip), ang + 3 * osc(t, 2.1) * (1 - smooth(21.8, 22.0, t)), HAND_K, tool, "#3b6fd8", lift=lift, seed=30))
    if t > tc:
        v = t - tc
        bx = _crot(np.array([BOX_X + 60, ROWY[1] - 50]))
        sc = min(1, v / .06) * (1 + .5 * math.exp(-7 * v) * math.sin(v * 24 + .4))
        w.append(Pr.star(bx[0], bx[1], 30 * sc, "#f4c430", rot=20 * math.exp(-5 * v), seed=6951))
        w.append(Pr.glint(bx[0] + 40, bx[1] - 30, 22 * math.sin(math.pi * clamp(v / .4)), "#fff6c8", rot=v * 90))
    kk = ease_io(clamp((t - 19.96) / 2.56))
    s = (1.1 + .06 * kk) * (1 + punch(t, tc, .05, .05, .3) + .03 * bump(t, tv, .3))
    wh = whip_in(t, 19.96, .22)
    return compose("".join(w), card_cam(t, s, 40 - 60 * kk + 240 * wh, -20 + 30 * kk, -.6 + 1.1 * kk), light_u=evening_u(t), lcx=900, lcy=150)


def paw_state(t):
    """Лапа: (острие стопы, угол к плечу, подушечками к зрителю?, нажим, сплющ. флипа fy) или None."""
    t_in = T_TREH - .04
    if t < t_in:
        return None
    b3 = _crot(np.array([BOX_X + 2, ROWY[2] + 6]))
    hov = (b3[0] + 70, b3[1] - 150)
    keys = [(t_in, 1240, 360, -28), (t_in + .42, 820, 560, -32), (23.9, hov[0] + 40, hov[1] - 20, -34), (24.5, hov[0], hov[1], -36),
            (24.92, b3[0] + 10, b3[1] - 40, -38), (T_LAPOY, b3[0], b3[1], -38), (25.3, b3[0] + 4, b3[1] - 4, -38),
            (25.7, b3[0] + 300, b3[1] - 330, -32), (26.0, 1300, 300, -28)]
    x, y, ang = hover_path(t, keys)
    if t < 24.5:
        x += 10 * osc(t, 1.7)
        y += 8 * osc(t, 2.3, .5)
    # флип: подушечками к зрителю → тыльной стороной (идёт вниз) → снова подушечки (уходит)
    pads = not (24.8 <= t < 25.4)
    fy = 1.0
    for tf in (24.8, 25.4):
        if abs(t - tf) < .06:
            fy = max(.08, abs(t - tf) / .06)
    press = bump(t, T_LAPOY - .02, .3) if t > T_LAPOY - .02 else 0.0
    return (x, y), ang, pads, press, fy


def draw_paw(t):
    st = paw_state(t)
    if st is None:
        return ""
    (x, y), ang, pads, press, fy = st
    g = Pr.paw((x, y), ang, .92, pads=pads, press=press, seed=6000)
    if fy < 1:
        g = f'<g transform="translate({x:.1f} {y:.1f}) scale(1 {fy:.3f}) translate({-x:.1f} {-y:.1f})">{g}</g>'
    return g


def s15(t):
    w, _ = card_world(t, (1.0, 1.0), pen_rest=True)
    w.append(draw_paw(t))
    kk = ease_io(clamp((t - 22.12) / 1.78))
    s = 1.08 + .1 * kk
    return compose("".join(w), card_cam(t, s, -10 * kk + 6 * osc(t, .5), 40 * kk, .5 - .9 * kk), light_u=1.0, lcx=900, lcy=150)


def s16(t):
    tl = T_LAPOY
    pu = 1.0 if t > tl else 0.0
    w, _ = card_world(t, (1.0, 1.0), paw_u=clamp((t - tl) / .2) * pu, pen_rest=True)
    w.append(draw_paw(t))
    b3 = _crot(np.array([BOX_X + 2, ROWY[2] + 6]))
    if t > tl:
        v = t - tl
        w.append(Pr.burst(b3[0], b3[1], clamp(v / .35), 70, 170, 10, "#3a2a22", 7, seed=6960))
        for j in range(6):
            a = math.radians(j * 60 + 20)
            r = 90 + 150 * ease_out(clamp(v / .5))
            w.append(Pr.glint(b3[0] + r * math.cos(a), b3[1] + r * math.sin(a), 26 * math.sin(math.pi * clamp(v / .55)),
                              "#ffd84a" if j % 2 else "#fff6c8", rot=v * 140))
        u = clamp((v - .08) / .12)
        if u > 0:
            sc = (1 + .5 * math.exp(-6 * (v - .08)) * math.sin((v - .08) * 22 + .3)) * min(1, u * 1.5)
            w.append(Pr.text(660, 458, "3/3", 104 * sc, "#2fa24a", rot=-8, stroke="#ffffff", sw=12))
    kk = ease_io(clamp((t - 23.5) / 1.5))
    s = (1.18 + .14 * kk) * (1 + punch(t, tl, .07, .05, .35))
    sx, sy, sr = shake(t, tl, 16, .4)
    return compose("".join(w), card_cam(t, s, -10 - 40 * kk + sx, 40 + 60 * kk + sy, .4 - .8 * kk + sr), light_u=1.0, lcx=900, lcy=150)


SHOTS = {"s02": s02, "s06": s06, "s07": s07, "s09": s09, "s12": s12, "s13": s13, "s14": s14, "s15": s15, "s16": s16}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
