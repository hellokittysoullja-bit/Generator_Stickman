"""Рилс 78 «Лента, ты слабак», группа A: графика и предметы — s06, s07, s10, s11, s14, s15.
Время — ТОЛЬКО из shots.json (t0/t1 плана) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
s06 тумблеры: телефон экраном к зрителю, лапа кота щёлкает три тумблера на «настройки» (w24), «телефона» (w25), «после» (w26);
    «которых» (w27) — лента фоном замедляется. Камера: хлёст влево гаснет, наезд на тумблеры, мини-тряска на щелчке.
s07 лассо: маленький Дима обмотан лентой; «лента» (w28) петли тугие, он дёргается; «отпускает» (w30) петли спадают кольцами,
    он выдыхает и расправляет плечи, лента уползает в телефон на полу. Камера: отъезд и «приседание».
s10 колодец: из прорези телефона лента падает в колодец без дна; «виноват» (w46) рывок; «ленты» (w48) камера ныряет вдоль ленты;
    «дна» (w50) провал +6 %; «специально» (w51) камера вылетает обратно — аккуратный раструб у устья.
s11 рука по ленте: Дима висит на бегущей ленте и едет вниз; «рука» (w53) шарит свободной рукой; «находила» (w55) ладонь
    скользит по гладким карточкам; «остановиться» (w57) упирается ногой — соскальзывает, рывок вниз.
s14 доска-дно (тёплый тон): лента из телефона на полке бежит в колодец; «Поэтому» (w70) Дима берёт доску; «ставит» (w73)
    подставляет её на устье; «дно» (w75) лента складывается гармошкой, бег стоп; кот одобрительно моргает.
s15 колокольчик: палец Димы поворачивает стрелку «таймер» (w77), сектор встаёт «десять» (w79), «минут» (w80) звон, кот ведёт ухом.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SHOTS = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def T0(sid):
    return SHOTS[sid]["t0"]


def T1(sid):
    return SHOTS[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def ramp(t, a, d):
    return clamp((t - a) / d)


def paper_bg(col=None, grid="#E3D9BE"):
    d = "".join(f"M-900 {i * 64}H2600" for i in range(-14, 80)) + "".join(f"M{i * 64} -900V5000" for i in range(-14, 42))
    return (f'<path d="M-900 -900H2600V5000H-900Z" fill="{col or P.C_PAGE}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def frame_svg(body, cx, cy, s, rot, bg=None, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg or P.C_PAGE}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def shadow(x, y, rx, op=.13, col="#6B5B3A"):
    return blob(ellipse_pts(x, y, rx, rx * .14, 18), col, op)


def whip_in(t, t0, amp=380.0, dur=.28):
    """Хвост хлёста внутри клипа: камера влетает со стороны и тормозит без остановки (ease out)."""
    u = clamp((t - t0 + .06) / dur)
    return amp * (1 - ease_out(u, 3))


def scroll_slow(t, a, t_slow, v0=260.0, k=3.0, v1=18.0):
    """Прокрутка ленты: скорость v0, после t_slow плавно гаснет к v1 (без скачка)."""
    if t <= t_slow:
        return v0 * (t - a)
    u = t - t_slow
    return v0 * (t_slow - a) + v1 * u + (v0 - v1) * (1 - math.exp(-k * u)) / k


def impact(x, y, u, r0=60.0, n=6, a0=-170.0, span=160.0, w=7.0, sd=0, sy=.6):
    if u <= 0 or u >= 1:
        return ""
    o = []
    for j in range(n):
        a = math.radians(a0 + span * j / max(1, n - 1))
        r1 = r0 + 60 * ease_out(u, 2)
        o.append(line([(x + math.cos(a) * r1, y + math.sin(a) * r1 * sy), (x + math.cos(a) * (r1 + 50 * (1 - u)), y + math.sin(a) * (r1 + 50 * (1 - u)) * sy)],
                      w * (1 - u), INK, taper=.6, wmin=.1, seed=sd + j))
    return "".join(o)


# ═══════════════════════════════ s06: три тумблера ═══════════════════════════════
PH6 = (540.0, 760.0)
PH6_K = 1.85


def s06(t):
    lib.dyn_begin()
    a = max(0.0, T0("s06") - .2)
    clicks = [ws(24), ws(25), ws(26)]
    on = [ease_out(ramp(t, c, .12), 3) for c in clicks]
    hop = sum(P.hop(t, c, 16, .22) for c in clicks)
    sq = (1.0, 1.0)
    for c in clicks:
        q = P.squash(t, c + .02, .05, 3.2, 9)
        sq = (sq[0] * q[0], sq[1] * q[1])
    x, y = PH6
    scroll = scroll_slow(t, a, ws(27), 300.0, 3.2, 14.0)
    o = [paper_bg()]
    o.append(shadow(x, y + 330 * PH6_K * .98, 230 * (1 + hop / 160), .16))
    ph = P.toggle_rows(0, 0, PH6_K, on, t, scroll, 1.0, seed=6)
    o.append(f'<g transform="translate({x:.1f} {y + hop:.1f}) scale({sq[0]:.4f} {sq[1]:.4f})">{ph}</g>')
    # вспышка-искры на каждом щелчке у кружка
    for i, c in enumerate(clicks):
        u = clamp((t - c) / .35)
        if 0 < u < 1:
            kx, ky = P.toggle_knob(x, y + hop, PH6_K, i, 1.0)
            o.append(P.sparkles(kx + 40, ky - 30, 1.2, 1 - u, t, seed=60 + i, n=4, r=90))
    # лапа кота справа: у кружка, нажимает и ведёт его вправо, между щелчками поднимается к следующему
    def knob(i, u):
        return P.toggle_knob(x, y + hop, PH6_K, i, u)
    tip = None
    for i, c in enumerate(clicks):
        nxt = clicks[i + 1] if i < 2 else None
        if t < c or (nxt is not None and t >= nxt - .3):
            continue
        kx, ky = knob(i, on[i])
        tip = (kx - 20, ky + 6)
        if nxt is not None:
            pass
    if t < clicks[0]:
        kx, ky = knob(0, 0)
        w = 10 * math.sin(t * 17)
        tip = (kx - 20 + w, ky - 30 * (1 - ramp(t, clicks[0] - .1, .1)) + 4)
    for i in (0, 1):
        c, nxt = clicks[i], clicks[i + 1]
        if nxt - .3 <= t < nxt:
            u = ease_io(ramp(t, nxt - .3, .26))
            p0 = knob(i, 1)
            p1 = knob(i + 1, 0)
            tip = (lerp(p0[0] - 20, p1[0] - 20, u), lerp(p0[1], p1[1], u) - 70 * math.sin(math.pi * u) + 6)
    out_u = ease_in(ramp(t, clicks[2] + .25, .35), 2)
    if tip is None:
        kx, ky = knob(2, 1)
        tip = (kx - 20, ky + 6)
    tip = (tip[0] + 520 * out_u, tip[1] + 120 * out_u)
    if out_u < 1:
        o.append(people.cat_forearm((1260 + 60 * out_u, tip[1] + 380), tip, 1.55, claw=0.0, seed=6))
    # камера: хлёст влево гаснет, наезд к тумблерам, мини-тряска на щелчках
    wx = whip_in(t, T0("s06"), 420)
    sh = [P.shake(t, c, 9, .22, seed=i) for i, c in enumerate(clicks)]
    dx = sum(s_[0] for s_ in sh)
    dy = sum(s_[1] for s_ in sh)
    pu = ease_io(ramp(t, a, T1("s06") + .2 - a))
    s = 1.0 + .10 * pu
    cx = 560 + 30 * pu - wx + dx
    cy = 820 - 30 * pu + dy
    return frame_svg("".join(o), cx, cy, s, -.6 + .9 * pu)


# ═══════════════════════════════ s07: лассо спадает ═══════════════════════════════
D7 = (430.0, 860.0)
D7_K = .62
PHONE7 = (860.0, 1330.0)


def s07(t):
    lib.dyn_begin()
    a = max(0.0, T0("s07") - .2)
    t_go = ws(30)                    # «отпускает»
    lu = ease_in(ramp(t, t_go, .55), 1.4)
    rew = ease_io(ramp(t, t_go + .55, .6))
    relax = ease_out(ramp(t, t_go + .1, .45), 2)
    x, y = D7
    sc = D7_K
    # пока туго — дёргается (рывки на ударных слогах), после — выдох
    tight = 1 - relax
    wr = tight * (.07 * math.sin(t * 17) + .04 * math.sin(t * 31 + 1))
    jolt = P.shake(t, ws(28), 10, .3, 2)
    hx = x + jolt[0] * tight + 6 * math.sin(t * 13) * tight
    hy = y + jolt[1] * tight - 6 * relax
    o = [paper_bg()]
    o.append(shadow(x + 20, y + 590 * sc * 1.0 + 6, 210, .16))
    # телефон на полу справа, лента тянется к нему
    o.append(shadow(PHONE7[0], PHONE7[1] + 18, 120, .18))
    o.append(P.phone_flat(PHONE7[0], PHONE7[1], 1.0, 0, -18 + 4 * math.sin(t * 9) * tight, face_down=False, glow_=.7))
    tail = (PHONE7[0] - 30, PHONE7[1] - 10)
    lasso_c = (hx + 20, hy - 205 * sc)
    o.append(P.ribbon_lasso(lasso_c[0], lasso_c[1], sc * 1.55, lu, t, "back", rw=118, feet=(y + 560 * sc - lasso_c[1]) / (sc * 1.55),
                            tail_to=tail, rewind=rew, seed=70))
    th_f = lerp(.06, .42, relax)
    th_n = lerp(-.04, -.38, relax)
    bend = lerp(.06, .35, relax)
    expr = "strain78" if t < t_go + .12 else "relief78"
    fig = people.dima(hx, hy, sc, expr, feet=people.stand_kw(x, y, sc)["feet"], lean_add=wr + .05 * relax * math.sin(math.pi * relax),
                      head_add=-.12 * relax * (1 - relax) * 4 * .5, arms={"f": ("ang", th_f, bend), "n": ("ang", th_n, bend)},
                      hands={"f": {"curl": (.3, .3, .35, .4), "spread": .1}, "n": {"curl": (.3, .3, .35, .4), "spread": .1}},
                      shrug=.6 * tight)
    o.append(fig["svg"])
    o.append(P.ribbon_lasso(lasso_c[0], lasso_c[1], sc * 1.55, lu, t, "front", rw=118, feet=(y + 560 * sc - lasso_c[1]) / (sc * 1.55),
                            tail_to=tail, rewind=rew, seed=70))
    # выдох: штрихи у рта
    ex = clamp((t - t_go - .15) / .6)
    if 0 < ex < 1:
        hxh, hyh = fig["head"]
        for j in range(3):
            o.append(line([(hxh + 110 * sc + 30 * ex * (1 + j * .3), hyh + 40 * sc + 14 * j - 10), (hxh + 150 * sc + 70 * ex * (1 + j * .3), hyh + 30 * sc + 16 * j)],
                          6 * (1 - ex), INK, taper=.6, wmin=.1, seed=700 + j))
    # тугие петли — штрихи напряжения
    if tight > .3:
        for j, sd in enumerate((1, -1)):
            ph = (t * 6 + j * .5) % 1
            o.append(line([(hx + sd * 150, hy - 330 * sc - 10 * ph), (hx + sd * 185, hy - 345 * sc - 20 * ph)], 5 * tight * (1 - ph), INK, taper=.5,
                          wmin=.1, seed=720 + j))
    # камера: лёгкий отъезд на «отпускает», чуть приседает
    pu = ease_io(ramp(t, t_go - .05, .7))
    s = 1.2 - .1 * pu + .01 * math.sin(t * 1.4)
    cx = 560 + 8 * math.sin(t * 1.1)
    cy = 800 + 30 * math.sin(math.pi * clamp((t - t_go) / .5)) * (1 if t > t_go else 0) + 20 * pu
    return frame_svg("".join(o), cx, cy, s, .4 * math.sin(t * .9) - .3)


# ═══════════════════════════════ s10: колодец без дна ═══════════════════════════════
PH10 = (540.0, 260.0)
PH10_K = .78
WELL10 = (540.0, 1060.0)
WELL10_K = 1.15
DEPTH10 = 2600.0


def ground_cut(x, y, w, depth, col0="#6B4E36", col1="#050407"):
    g = lib.lin_grad([(0, col0, 1), (.25, "#3A2A20", 1), (.6, "#120D0C", 1), (1, col1, 1)], 0, 0, 0, 1)
    o = [f'<path d="M{x - w:.0f} {y:.0f}H{x + w:.0f}V{y + depth:.0f}H{x - w:.0f}Z" fill="url(#{g})"/>']
    rs = P._rs(1010)
    for j in range(60):
        px, py = rs.uniform(x - w, x + w), y + rs.uniform(20, depth * .5)
        r = rs.uniform(3, 9)
        o.append(blob(ellipse_pts(px, py, r * 1.4, r, 7, rot=rs.uniform(0, 180)), "#8A6A4C", .35 * (1 - (py - y) / (depth * .5))))
    o.append(line([(x - w, y + 2), (x + w, y - 2)], 5, INK, taper=.05, wmin=.8, seed=1011))
    return "".join(o)


def s10(t):
    lib.dyn_begin()
    a = max(0.0, T0("s10") - .2)
    t_jerk, t_dive, t_no, t_dna, t_spec = ws(46), ws(48), ws(49), ws(50), ws(51)
    wx, wy = WELL10
    k = WELL10_K
    # лента: до «виноват» бежит ровно, рывок — и понеслась быстрее
    sp0, sp1 = 260.0, 900.0
    jerk_u = ease_out(ramp(t, t_jerk, .25), 2)
    off = sp0 * (t - a) + (sp1 - sp0) * max(0.0, t - t_jerk) - 40 * math.sin(math.pi * jerk_u) * (1 if t > t_jerk else 0)
    flare = ease_out(ramp(t, t_spec - .05, .45), 2)
    o = [paper_bg()]
    o.append(ground_cut(wx, wy + 40 * k, 1800, DEPTH10 * k + 600))
    o.append(P.bottomless_well(wx, wy, k, t * (1.0 + 1.6 * jerk_u), DEPTH10, flare=flare, seed=10, layer="back"))
    # отблеск-«уголок» раструба на «специально»
    if flare > 0:
        g_u = ramp(t, t_spec, .5)
        if 0 < g_u < 1:
            ang = 200 + 140 * g_u
            gx = wx + 0.92 * 260 * k * math.cos(math.radians(ang))
            gy = wy + 4 * k + .22 * 260 * k * math.sin(math.radians(ang))
            o.append(P.sparkles(gx, gy, 1.6, math.sin(math.pi * g_u), t, seed=105, n=4, r=70))
    # телефон сверху и лента из прорези вниз в колодец — по оси, сужается в глубину
    sx, sy = P.phone_feed_slot(PH10[0], PH10[1], PH10_K)
    D = DEPTH10 * k
    path = [(sx, sy), (sx + 6, (sy + wy) / 2), (wx, wy - 10)]
    for i in range(1, 9):
        u = i / 8
        path.append((wx + 22 * math.sin(t * 3 + i * 1.3) * (1 - u), wy - 10 + D * u))
    o.append(P.feed_ribbon(path, off, speed=1.0, seed=11, w=150, card=150, gap=12, w_end=8, taper_p=2.2))
    o.append(P.bottomless_well(wx, wy, k, t, DEPTH10, seed=10, layer="front"))
    o.append(P.phone_feed(PH10[0], PH10[1], PH10_K, t, scroll=off * .5, seed=10))
    # штрихи рывка у прорези
    o.append(impact(sx, sy + 30, ramp(t, t_jerk, .35), 50, 5, 20, 140, 7, 1040, .8))
    # камера: хлёст вниз гаснет; до «ленты» — общий план телефон+колодец; с «ленты» падает вдоль ленты, ускоряясь;
    # на «дна» провал +6 %; со «специально» вылетает назад к устью (раструб)
    wv = whip_in(t, T0("s10"), 360)
    cy0 = 700.0
    fall = 0.0
    if t > t_dive:
        u = t - t_dive
        fall = 300 * u + 1800 * u * u
    back = ease_io(ramp(t, t_spec - .02, .5))
    fall_at = 300 * (t_spec - t_dive) + 1800 * (t_spec - t_dive) ** 2
    if t > t_spec:
        fall = lerp(fall_at + 260 * (t - t_spec), -(cy0 - (wy + 30)), back)
    dip = .06 * math.sin(math.pi * clamp((t - t_dna) / .4)) if t > t_dna else 0.0
    s = 1.0 + .25 * clamp(fall / 900) * (1 - back) + dip + .35 * back
    cy = cy0 + fall - wv
    rot = -.5 + .8 * math.sin(t * 1.3)
    sh = P.shake(t, t_jerk, 8, .25, 4)
    return frame_svg("".join(o), 540 + sh[0], cy + sh[1], s, rot)


# ═══════════════════════════════ s11: рука по ленте ═══════════════════════════════
RIB11_X = 680.0
RIB11_W = 330.0
D11 = (390.0, 880.0)
D11_K = .66


def s11(t):
    lib.dyn_begin()
    a = max(0.0, T0("s11") - .2)
    t_hand, t_find, t_stop = ws(53), ws(55), ws(57)
    # мир едет вверх (камера с Димой вниз): фон и лента бегут
    v_bg = 520.0
    slip = 0.0
    if t > t_stop:
        u = t - t_stop
        slip = 260 * (1 - math.exp(-u * 6))
    bg_off = v_bg * (t - a) + 2.2 * slip
    rib_off = (v_bg + 160) * (t - a) + 3.0 * slip
    o = []
    # фон: бумага с сеткой и редкими штрихами-рисками, которые уезжают вверх — видно, что падаем
    o.append(f'<g transform="translate(0 {-(bg_off % 64):.1f})">{paper_bg()}</g>')
    rs = P._rs(1100)
    for j in range(14):
        yy = (rs.uniform(0, 2600) - bg_off * 1.0) % 2600 - 300
        xx = rs.choice([rs.uniform(-100, 300), rs.uniform(880, 1180)])
        o.append(line([(xx, yy), (xx, yy + rs.uniform(80, 200))], 5, "#C9BC98", taper=.5, wmin=.2, seed=1110 + j, op=.8))
    # лента вертикально
    o.append(P.feed_ribbon([(RIB11_X, -600), (RIB11_X + 4, 900), (RIB11_X, 2600)], rib_off, speed=1.0, seed=111, w=RIB11_W, card=380, gap=5, ink_w=4))
    # глянец: гладкие блики по ленте (ни выступа, ни уступа)
    for j in range(4):
        yy = (j * 600 - rib_off) % 2400 - 400
        o.append(line([(RIB11_X - 60, yy), (RIB11_X - 52, yy + 260)], 10, "#FFFFFF", taper=.6, wmin=.2, seed=1120 + j, op=.55))
    x, y = D11
    sc = D11_K
    # Дима висит слева от ленты, ближняя рука вцепилась в край ленты над головой
    sway = 8 * math.sin(t * 4.2)
    dropj = 0.0
    if t > t_stop:
        dropj = 70 * math.sin(math.pi * clamp((t - t_stop) / .35)) * (1 - ramp(t, t_stop + .35, .3))
    hx, hy = x + sway, y + dropj
    edge_x = RIB11_X - RIB11_W / 2 + 26
    grip = (edge_x + 30, hy - 820 * sc)
    # дальняя рука шарит по ленте: дуги поиска, с «рука» — по ленте, с «находила» — скользит вниз по карточке
    srch = ramp(t, t_hand - .1, .2)
    ph = (t - t_hand) * 5.0
    fx = edge_x + 110 + 80 * math.sin(ph) * srch
    fy = hy - 430 * sc + 60 * math.cos(ph * .7) * srch
    if t > t_find:
        sl = ease_in(ramp(t, t_find, .45), 1.5)
        fy = fy + 90 * sl
    far_t = (lerp(hx + 160 * sc, fx, srch), lerp(hy - 300 * sc, fy, srch))
    # нога: с «остановиться» — упирается в ленту и соскальзывает
    stand = people.stand_kw(hx, hy, sc)["feet"]
    pf = ease_out(ramp(t, t_stop - .2, .2), 2)
    slide = ease_in(ramp(t, t_stop + .1, .3), 2)
    dang = 14 * math.sin(t * 5)
    leg_n = ((lerp(hx + 80 * sc + dang, edge_x - 6, pf), lerp(hy + 520 * sc, hy + 300 * sc, pf) + 220 * slide), lerp(.25, -1.2, pf))
    leg_f = ((hx - 30 * sc - dang, hy + 540 * sc), .35)
    expr = "strain78" if t < t_stop + .1 else "fall78"
    fig = people.dima(hx, hy, sc, expr, feet={"n": leg_n, "f": leg_f}, lean_add=.08 + .03 * math.sin(t * 3),
                      arms={"n": ("ik", grip, 1), "f": ("ik", far_t, -1)},
                      hands={"n": {"curl": (.75, .75, .8, .85), "thumb": .6, "dir": (0.15, -1)},
                             "f": {"curl": (.05, .05, .1, .15), "spread": .3, "thumb": .1, "dir": (.6, -.4)}})
    o.append(fig["svg"])
    # штрихи скольжения под ладонью и под ногой
    if t > t_find:
        u = ramp(t, t_find, .5)
        if u < 1:
            for j in range(3):
                o.append(line([(fx - 30 + 22 * j, fy + 40), (fx - 30 + 22 * j, fy + 40 + 80 * u)], 5 * (1 - u), INK, taper=.6, wmin=.1, seed=1130 + j))
    if t > t_stop + .1:
        u = ramp(t, t_stop + .1, .45)
        if u < 1:
            for j in range(3):
                o.append(line([(edge_x - 20 + 18 * j, hy + 100 * sc), (edge_x - 20 + 18 * j, hy + 100 * sc + 140 * u)], 6 * (1 - u), INK, taper=.6,
                              wmin=.1, seed=1140 + j))
    # скорость: штрихи вдоль краёв
    for j in range(5):
        yy = (j * 420 - bg_off * 1.6) % 2200 - 200
        o.append(line([(RIB11_X + RIB11_W / 2 + 40, yy), (RIB11_X + RIB11_W / 2 + 40, yy + 160)], 4, INK, taper=.6, wmin=.1, seed=1150 + j, op=.5))
    sh = P.shake(t, t_stop + .1, 14, .4, 7)
    cy = 840 + sh[1] + 40 * math.sin(math.pi * clamp((t - t_stop - .1) / .3)) * (1 if t > t_stop + .1 else 0)
    s = 1.04 + .03 * ease_io(ramp(t, a, 2.6))
    return frame_svg("".join(o), 540 + sh[0], cy, s, .5 * math.sin(t * 1.2))


# ═══════════════════════════════ s14: доска-дно (тёплый) ═══════════════════════════════
C_WARM_WALL = "#F2D3A2"
C_WARM_WALL2 = "#E7B97A"
C_WARM_FLOOR = "#C98F5A"
FLOOR14 = 1250.0
WELL14 = (730.0, 1236.0)
WELL14_K = .46
SHELF14 = (730.0, 330.0)
PH14_K = .42
BOARD14_Y = 1000.0


def warm_room(t, floor=FLOOR14):
    g = lib.lin_grad([(0, "#F6DDAF", 1), (1, C_WARM_WALL2, 1)], 0, 0, 0, 1)
    o = [f'<path d="M-900 -900H2600V{floor:.0f}H-900Z" fill="url(#{g})"/>']
    o.append(f'<path d="M-900 {floor:.0f}H2600V3000H-900Z" fill="{C_WARM_FLOOR}"/>')
    for j in range(5):
        yy = floor + 40 + 70 * j * (1 + j * .25)
        o.append(line([(-900, yy), (2600, yy)], 3, "#A9733F", taper=.05, wmin=.8, seed=1400 + j, op=.6))
    o.append(line([(-900, floor), (2600, floor)], 5, INK, taper=.02, wmin=.8, seed=1410))
    # бра-торшер слева: небольшой чёткий круг света
    o.append(P.torch(110, floor, 1.15, 1.0, C_WARM_WALL, seed=14))
    return "".join(o)


def s14(t):
    lib.dyn_begin()
    a = max(0.0, T0("s14") - .2)
    t_po, t_put, t_dno = ws(70), ws(73), ws(75)
    t_place = t_put + .26
    o = [warm_room(t)]
    # полка с телефоном
    sx0, sy0 = SHELF14
    o.append(lib.shape(lib.rrect(sx0 - 170, sy0 + 92, sx0 + 170, sy0 + 118, 4), P.C_WOOD, "", w=3.6, seed=1420))
    o.append(line([(sx0 - 140, sy0 + 118), (sx0 - 140, sy0 + 170), (sx0 - 100, sy0 + 118)], 5, INK, taper=.1, wmin=.8, seed=1421))
    o.append(line([(sx0 + 140, sy0 + 118), (sx0 + 140, sy0 + 170), (sx0 + 100, sy0 + 118)], 5, INK, taper=.1, wmin=.8, seed=1422))
    wx, wy = WELL14
    o.append(P.bottomless_well(wx, wy, WELL14_K, t, 60, flare=1.0, seed=14, layer="back"))
    slot = P.phone_feed_slot(sx0, sy0 - 10, PH14_K)
    # доска: стоит у стены → в руках у груди → под лентой (Дима держит её, как дно ящика)
    lean_pos = (215.0, FLOOR14 - 165, 78.0)
    chest = (470.0, 930.0, -8.0)
    place = (wx - 20, BOARD14_Y, 0.0)
    u1 = ease_io(ramp(t, t_po, .55))
    u2 = ease_io(ramp(t, t_put, t_place - t_put))
    bxy = [lerp(lerp(lean_pos[i], chest[i], u1), place[i], u2) for i in range(3)]
    if u1 > 0 and u2 < 1:
        bxy[1] -= 40 * math.sin(math.pi * u1) * (1 - u2)
    hit = P.squash(t, t_dno, .06, 3, 8)
    bxy[1] += 10 * (1 - hit[1]) / .06 if t > t_dno else 0.0
    # лента: из прорези телефона на полке вниз в колодец; под доской — гармошка, нижний хвост уходит в колодец
    fold = 0.0
    if t > t_place:
        fold = .14 * ease_out(ramp(t, t_place, t_dno - t_place), 2) + .86 * ease_out(ramp(t, t_dno, .4), 2)
    by = bxy[1] - 40 * .9
    if fold <= 0:
        o.append(P.feed_ribbon([(wx, slot[1]), (wx + 6, (slot[1] + wy) / 2), (wx, wy + 8)], t, speed=420, seed=140, w=96, card=130, gap=10))
    else:
        cut = by + 40
        drop = ease_in(ramp(t, t_place, .5), 2)
        y0 = cut + (wy - cut) * drop
        if y0 < wy - 4:
            o.append(P.feed_ribbon([(wx, y0), (wx + 3, (y0 + wy) / 2), (wx, wy + 8)], t, speed=420, seed=141, w=96, card=130, gap=10))
        o.append(P.ribbon_board(wx, by, .9, fold, t, top=-(by - slot[1]) / .9, board=False, run=1.0, seed=140, w=96 / .9, t_hit=t_dno))
    o.append(P.bottomless_well(wx, wy, WELL14_K, t, 60, seed=14, layer="front"))
    o.append(P.phone_feed(sx0, sy0 - 10, PH14_K, t, scroll=t * 120 * (1 - ramp(t, t_dno, .3)), seed=14))
    # Дима: подходит к доске, поднимает к груди, шаг вправо — подставляет под ленту и держит
    hip_x = lerp(lerp(300, 330, u1), 430, u2)
    sc = .64
    hip_y = FLOOR14 - 598 * sc - 14
    reach = u1 > 0 or t > t_po - .35
    feet = people.stand_kw(hip_x, hip_y, sc)["feet"]
    bang = math.radians(bxy[2])
    bL = (bxy[0] - 150 * math.cos(bang) * .9, bxy[1] - 150 * math.sin(bang) * .9)
    bR = (bxy[0] - 70 * math.cos(bang), bxy[1] - 70 * math.sin(bang))
    if reach:
        pre = ease_io(ramp(t, t_po - .35, .35))
        tf = (lerp(hip_x + 120 * sc, bL[0], pre), lerp(hip_y - 200 * sc, bL[1] - 8, pre))
        tn = (lerp(hip_x + 200 * sc, bR[0], pre), lerp(hip_y - 220 * sc, bR[1] - 8, pre))
        arms = {"f": ("ik", tf, -1), "n": ("ik", tn, -1)}
        hands = {"f": {"curl": (.6, .6, .65, .7), "thumb": .5}, "n": {"curl": (.6, .6, .65, .7), "thumb": .5}}
    else:
        arms = {"f": ("ang", .18 + .05 * math.sin(t * 2), .3), "n": ("ang", -.1, .3)}
        hands = {}
    expr = "carry78" if t < t_dno + .05 else "relief78"
    lean = .12 * u1 * (1 - u2) + .06 * u2 + .03 * math.sin(t * 1.6)
    fig = people.dima(hip_x, hip_y, sc, expr, feet=feet, lean_add=lean, arms=arms, hands=hands)
    o.append(shadow(hip_x + 20, FLOOR14 + 4, 150, .18, "#7A4F28"))
    board = P.wood_board(bxy[0], bxy[1], .9, bxy[2], seed=14)
    # пока доска у стены — она за Димой; в руках — перед корпусом
    if u1 <= 0:
        o.append(board)
        o.append(fig["svg"])
    else:
        o.append(fig["svg"])
        o.append(board)
    # тук на «дно»: штрихи удара у доски
    o.append(impact(wx, by - 10, ramp(t, t_dno, .4), 110, 6, -175, 170, 8, 1450, .45))
    # кот справа у колодца: смотрит на ленту, на «дно» медленно моргает и кивает
    cu = ramp(t, t_dno + .05, .5)
    blink = math.sin(math.pi * cu) if 0 < cu < 1 else 0.0
    nod = people.cat_nod(t, t_dno + .1, .4, .3)
    st = {"look": (-.5, lerp(-.3, .4, ramp(t, t_dno - .3, .4))), "blink": blink, "tail": 6 * math.sin(t * 2.1), "smile": .6 * ramp(t, t_dno, .4),
          "tilt": -4, "drop": nod}
    o.append(shadow(975, FLOOR14 + 4, 110, .18, "#7A4F28"))
    o.append(people.cat_svg(975, FLOOR14, .6, st, t))
    # камера: лёгкий наезд, на «дно» удар-наезд +8 % и мини-тряска
    pu = ease_io(ramp(t, a, T1("s14") + .2 - a))
    punch = .08 * math.exp(-max(0.0, t - t_dno) * 5) * ease_out(ramp(t, t_dno, .06), 2)
    sh = P.shake(t, t_dno, 9, .3, 3)
    s = 1.1 + .06 * pu + punch
    cx = lerp(600, 640, pu) + sh[0]
    cy = lerp(900, 930, pu) + sh[1] + 120 * punch
    return frame_svg("".join(o), cx, cy, s, .3 * math.sin(t * 1.1), bg=C_WARM_WALL)


# ═══════════════════════════════ s15: колокольчик ═══════════════════════════════
BELL15 = (590.0, 895.0)
BELL15_K = 1.1
TABLE15 = 1062.0


def s15(t):
    lib.dyn_begin()
    a = max(0.0, T0("s15") - .2)
    t_tm, t_ten, t_min = ws(77), ws(79), ws(80)
    ang = 60 * ease_io(ramp(t, t_tm, t_ten - t_tm))
    sec = ramp(t, t_tm, .1)
    rg = math.exp(-max(0.0, t - t_min) * 3.5) if t > t_min else 0.0
    rg *= ease_out(ramp(t, t_min, .05), 2)
    bx, by = BELL15
    o = []
    g = lib.lin_grad([(0, "#F6DDAF", 1), (1, C_WARM_WALL2, 1)], 0, 0, 0, 1)
    o.append(f'<path d="M-900 -900H2600V{TABLE15:.0f}H-900Z" fill="url(#{g})"/>')
    o.append(P.torch(960, TABLE15 - 10, .9, 1.0, C_WARM_WALL, seed=15))
    # Дима сидит за столом слева (ниже крышки его закрывает стол), ближняя рука на столе, указательный ведёт стрелку
    sc = .74
    hip = (250.0, 1150.0)
    # точка касания — середина стрелки; до «таймер» палец подходит, после «десять» чуть отходит
    a_r = math.radians(ang)
    touch = (bx + 58 * BELL15_K * math.sin(a_r), by - 58 * BELL15_K * math.cos(a_r))
    app = ease_out(ramp(t, a, t_tm - a + .02), 2)
    away = ease_io(ramp(t, t_ten + .1, .3))
    rest = (touch[0] - 110, touch[1] + 90)
    tip = (lerp(rest[0], touch[0], app) - 150 * away, lerp(rest[1], touch[1], app) + 30 * away)
    d = (1.0, -.25 + .3 * away)
    dl = math.hypot(*d)
    d = (d[0] / dl, d[1] / dl)
    n = (-d[1], d[0])
    wr = (tip[0] - d[0] * 138 * sc + n[0] * 25 * sc, tip[1] - d[1] * 138 * sc + n[1] * 25 * sc)
    breath = 4 * math.sin(t * 2.2)
    fig = people.dima(hip[0], hip[1] + breath, sc, "focus", lean_add=.1, head_add=.06,
                      arms={"n": ("ik", wr, -1), "f": ("ang", .35, .2)},
                      hands={"n": {"curl": (0.0, .85, .9, .95), "thumb": .7, "dir": d, "spread": .05}, "f": {"kind": "none"}},
                      layers=("arm_f", "body"))
    arm = people.dima(hip[0], hip[1] + breath, sc, "focus", lean_add=.1, head_add=.06,
                      arms={"n": ("ik", wr, -1), "f": ("ang", .35, .2)},
                      hands={"n": {"curl": (0.0, .85, .9, .95), "thumb": .7, "dir": d, "spread": .05}, "f": {"kind": "none"}},
                      layers=("arm_n",))
    o.append(fig["svg"])
    o.append(f'<path d="M-900 {TABLE15:.0f}H2600V3000H-900Z" fill="{P.C_WOOD}"/>')
    for j in range(4):
        o.append(line(P._wavy(-900, 2600, TABLE15 + 60 + 90 * j, 1500 + j, amp=6, per=200), 3, P.C_WOOD_SH, taper=.05, wmin=.8, seed=1500 + j, op=.7))
    o.append(line([(-900, TABLE15), (2600, TABLE15)], 5, INK, taper=.02, wmin=.8, seed=1510))
    # рука лежит поверх края стола: перерисуем ближнюю руку поверх крышки
    o.append(shadow(bx, TABLE15 + 4, 220, .2, "#6B3F1E"))
    o.append(P.bell_timer(bx, by, BELL15_K, ang, sec, rg, t, seed=15))
    # кот справа у колокольчика: смотрит на стрелку, на «минут» ведёт ухом
    ear = math.sin(math.pi * clamp((t - t_min - .05) / .25)) if t > t_min + .05 else 0.0
    st = {"look": (-.7, -.2 + .15 * math.sin(t * 2)), "tail": 8 * math.sin(t * 2.4), "ear": ear, "perk": .3 * ear, "tilt": -6 + 3 * ear,
          "blink": 1.0 if 0 < (t - a - .5) % 2.2 < .12 else 0.0}
    o.append(shadow(815, TABLE15 + 4, 90, .2, "#6B3F1E"))
    o.append(people.cat_svg(815, TABLE15, .5, st, t))
    o.append(arm["svg"])
    # штрихи поворота у кончика стрелки
    htip = P.bell_hand_tip(bx, by, BELL15_K, ang)
    if t_tm < t < t_ten + .1:
        for j in range(2):
            o.append(line([(htip[0] + 26 + 12 * j, htip[1] - 20 - 10 * j), (htip[0] + 46 + 12 * j, htip[1] + 6 - 10 * j)], 4, INK, taper=.5, wmin=.2,
                          seed=1530 + j, op=.7))
    pu = ease_io(ramp(t, a, T1("s15") + .2 - a))
    sh = P.shake(t, t_min, 8, .3, 5)
    s = 1.55 + .15 * pu
    cx = lerp(530, bx - 20, pu) + sh[0]
    cy = lerp(880, by + 0, pu) + sh[1]
    return frame_svg("".join(o), cx, cy, s, .35 * math.sin(t * 1.3), bg=C_WARM_WALL)


SCENES = {"s06": s06, "s07": s07, "s10": s10, "s11": s11, "s14": s14, "s15": s15}


def frame(sid, t):
    return SCENES[sid](t)
