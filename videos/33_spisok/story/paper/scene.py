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


SHOTS = {"s02": s02, "s06": s06, "s07": s07, "s09": s09}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
