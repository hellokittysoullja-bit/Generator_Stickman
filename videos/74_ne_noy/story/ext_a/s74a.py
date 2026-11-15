"""Рилс 74 «Прекрати ныть», группа A: графика на бумаге — банка, весы, крекер.
s03 (2.80–3.95, склейка-сбой): «как у взрослых» — на кремовой бумаге стеклянная банка подпрыгивает и крутится с кадра 0;
    «берут» (2.86) сверху входит лапа кота и хватает крышку; «и» (3.24) крышка проворачивается одним движением; «делают» (3.42)
    крышка слетает вверх с пружинкой, вокруг искры «легко». Камера: микродрейф, на «делают» отскок вверх 4 %.
s11 (15.15–16.85): рычажные весы без делений, коромысло с кадра 0 качается; «и это» (15.64) выравниваются; «разные» (15.90)
    на левую чашу падает скомканный платочек — чаша едва вздрагивает; «вещи» (16.24) на правую тяжело падает закрытая банка —
    чаша уходит вниз, коромысло бьётся об упор, штрихи удара. Камера: на «вещи» тряска 3 % вниз.
s12 (16.85–18.55): большой круглый крекер покачивается на бумаге, над ним лапа кота; «Когда шаг» (16.87) лапа нажимает;
    «становится» (17.32) бегут трещины; «крошечным» (17.80) крекер ломается на кусочки и крошки; к 18.40 самый маленький кусочек
    выкатывается вперёд к зрителю — «шаг». Камера: наезд 5 %, на «крошечным» тряска и отскок 4 %.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Предметы — common/props.py, лапа кота — common/people.py."""
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


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?:«»").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def paper_bg(col=None, grid="#E3D9BE"):
    d = "".join(f"M-900 {i * 64}H2600" for i in range(-14, 46)) + "".join(f"M{i * 64} -900V2800" for i in range(-14, 42))
    return (f'<path d="M-900 -900H2600V2800H-900Z" fill="{col or P.C_PAGE}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def frame_svg(body, cx, cy, s, rot, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{P.C_PAGE}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def shadow(x, y, rx, op=.13):
    return blob(ellipse_pts(x, y, rx, rx * .14, 18), "#6B5B3A", op)


def impact(x, y, u, r0=120.0, n=6, a0=-170.0, span=160.0, w=7.0, sd=0, sy=.5):
    """Штрихи удара пером: лучи от точки, вылетают и тают (u 0…1)."""
    if u <= 0 or u >= 1:
        return ""
    o = []
    for j in range(n):
        a = math.radians(a0 + span * j / max(1, n - 1))
        r1 = r0 + 70 * ease_out(u, 2)
        o.append(line([(x + math.cos(a) * r1, y + math.sin(a) * r1 * sy), (x + math.cos(a) * (r1 + 60 * (1 - u)), y + math.sin(a) * (r1 + 60 * (1 - u)) * sy)],
                      w * (1 - u), INK, taper=.6, wmin=.1, seed=sd + j))
    return "".join(o)


# ═══════════════════════════════ s03: банка открывается легко ═══════════════════════════════
T3_B = wt("берут")          # 2.86
T3_I = wt("и", 3.1)         # 3.24
T3_D = wt("делают")         # 3.42
JAR3 = (540.0, 1190.0)
JAR3_K = 2.0


def glitch_bands(body, t, t0, cam):
    """Склейка-сбой: 2 кадра — картинка рвётся горизонтальными полосами со сдвигом и цветной каймой."""
    u = t - t0
    if u < 0 or u >= 2 / 30:
        return None
    r = P._rs(7400 + int(u * 300))
    o = []
    y = 0.0
    while y < 1920:
        h = r.uniform(40, 220)
        dx = r.uniform(-120, 120)
        c = lib.clip_rect(0, y, 1080, h)
        o.append(f'<g clip-path="url(#{c})"><g transform="translate({dx:.1f} 0)"><g transform="{cam}">{body}</g></g></g>')
        if r.random() < .4:
            o.append(f'<rect x="0" y="{y + h * .3:.1f}" width="1080" height="{r.uniform(4, 12):.1f}" fill="{["#3b4fd8", "#e2412f", "#2fa45a"][r.randint(0, 2)]}" opacity=".55"/>')
        y += h
    return svg(f'<rect width="1080" height="1920" fill="{P.C_PAGE}"/>' + "".join(o) + '<rect width="1080" height="1920" fill="#ffffff" opacity=".18"/>')


def s03(t):
    lib.dyn_begin()
    o = [paper_bg()]
    jx, jy = JAR3
    grab = ease_out(clamp((t - T3_B + .1) / .16), 3)
    # банка подпрыгивает и крутится с кадра 0, пока её не схватили
    free = 1 - grab
    ph = (t - 2.55) * 2 * math.pi * 2.6
    hop = -abs(math.sin(ph)) * 80 * free
    rot = 9 * math.sin(ph * .5 + .6) * free
    sq = P.squash(t, T3_B + .02, .1, 3, 8)
    turn = ease_io(clamp((t - T3_I) / .16))
    lid_rot = 300 * turn + 8 * math.sin(t * 30) * grab * (1 - turn)
    lid_off = clamp((t - T3_D) / .75)
    o.append(shadow(jx, jy + 6, 190 * (1 - .3 * abs(hop) / 80), .16))
    jar = P.jar(0, 0, JAR3_K, rot, lid_rot, lid_off, 0.0, seed=1, t=t)
    o.append(f'<g transform="translate({jx:.1f} {jy + hop:.1f}) scale({sq[0]:.4f} {sq[1]:.4f})">{jar}</g>')
    # «легко»: штрихи-дуги от крышки и искры
    if lid_off > 0:
        u = clamp(lid_off / .6)
        lc = P.jar_lid_c(jx, jy, JAR3_K)
        o.append(impact(lc[0], lc[1] + 20, u, 150, 7, -175, 170, 8, 3300, .55))
        o.append(P.sparkles(lc[0], lc[1] - 120, 1.8, 1 - u, t, seed=3, n=5, r=160))
    # лапа кота сверху: хватает крышку, проворачивает её, отпускает и уходит вверх
    if t > T3_B - .12:
        lc = P.jar_lid_c(jx, jy + hop, JAR3_K, rot)
        tip_in = (lc[0] + 40, lc[1] - 20)
        u_in = ease_out(clamp((t - T3_B + .12) / .16), 3)
        tip = (lerp(760, tip_in[0], u_in), lerp(-80, tip_in[1], u_in))
        if turn > 0:
            tip = (tip[0] - 80 * math.sin(math.pi * turn * .9), tip[1] + 10 * math.sin(math.pi * turn))
        out = ease_in(clamp((t - T3_D + .02) / .3), 2)
        tip = (tip[0] + 120 * out, tip[1] - 700 * out)
        o.append(people.cat_forearm((900 + 60 * out, -260 - 300 * out), tip, 1.8, claw=0.0, seed=2))
    # камера: микродрейф, на «делают» отскок вверх 4 %
    b = .04 * math.sin(math.pi * clamp((t - T3_D) / .35))
    s = 1.0 + .015 * math.sin(t * 1.3) + b
    cx, cy = 540 + 6 * math.sin(t * 1.1), 980 - 1300 * b
    rr = .4 * math.sin(t * .9)
    body = "".join(o)
    g = glitch_bands(body, t, 2.8, lib.cam(cx, cy, s, rr))
    return g if g else frame_svg(body, cx, cy, s, rr)


# ═══════════════════════════════ s11: весы ═══════════════════════════════
T11_E = wt("и", 15.5)        # 15.64
T11_R = wt("разные")        # 15.90
T11_V = wt("вещи")          # 16.24
SC11 = (540.0, 1250.0)
SC11_K = 1.55
TILT_MAX = 17.0


def tilt11(t):
    if t < T11_E:
        return 9 * math.sin((t - 14.9) * 2 * math.pi * 1.25 + .9) * math.exp(-(t - 14.95) * .6)
    a = 9 * math.sin((T11_E - 14.9) * 2 * math.pi * 1.25 + .9) * math.exp(-(T11_E - 14.95) * .6)
    base = a * (1 - ease_io(clamp((t - T11_E) / .22)))
    if t > T11_R:      # платочек: едва вздрагивает влево
        base += -2.2 * math.exp(-(t - T11_R) * 7) * math.cos((t - T11_R) * 30)
    if t > T11_V:      # банка: правая чаша вниз до упора, отскок
        u = t - T11_V
        v = TILT_MAX * (1 - math.exp(-u * 18))
        v -= 3.5 * math.exp(-u * 6) * abs(math.sin(u * 24)) * (u > .05)
        base = min(TILT_MAX, base + v)
    return base


def s11(t):
    lib.dyn_begin()
    o = [paper_bg()]
    x, y = SC11
    k = SC11_K
    tilt = tilt11(t)
    o.append(shadow(x, y + 4, 260, .15))
    o.append(P.scales(x, y, k, tilt, seed=1))
    # упор на стойке справа: в него бьётся коромысло
    o.append(lib.shape(lib.rect_pts(x + 12 * k, y - 312 * k, x + 48 * k, y - 292 * k), "#A08332", "", w=3.0, seed=1101))
    (lx, ly), (rx, ry) = P.scale_pans(x, y, k, tilt)
    # платочек: падает на левую чашу
    tf = T11_R - .22
    if t > tf:
        u = clamp((t - tf) / (T11_R - tf))
        py = lerp(-200, ly - 2 * k, u * u)
        sw = 20 * (1 - u) * math.sin(t * 9)
        o.append(P.tissue(lx + sw, py, 1.35, 18 * (1 - u) * math.sin(t * 7), seed=1))
        if t > T11_R:
            o.append(impact(lx, ly - 30, clamp((t - T11_R) / .3), 90, 4, -160, 140, 4, 1120, .4))
    # банка: тяжело падает на правую чашу
    tj = T11_V - .2
    if t > tj:
        u = clamp((t - tj) / (T11_V - tj))
        py = lerp(-300, ry - 2 * k, u * u)
        sq = P.squash(t, T11_V, .14, 3, 8)
        jar = P.jar(0, 0, .78, 2 * (1 - u), 0, 0, 0, seed=2, t=t)
        o.append(f'<g transform="translate({rx:.1f} {py:.1f}) scale({sq[0]:.4f} {sq[1]:.4f})">{jar}</g>')
        if t < T11_V:
            for j in range(3):
                xx = rx - 60 + 60 * j
                o.append(line([(xx, py - 230), (xx, py - 420)], 6, INK, taper=.6, wmin=.1, seed=1130 + j, op=.7))
        else:
            uu = clamp((t - T11_V) / .4)
            o.append(impact(rx, ry, uu, 170, 7, -180, 180, 8, 1140, .45))
            o.append(impact(x + 30 * k, y - 300 * k, uu, 40, 4, -60, 120, 5, 1150, 1.0))
            o.append(P.dust_puff(rx, ry + 30, 1.4, uu, seed=3))
    # камера: на «вещи» тряска 3 % вниз
    sh = P.shake(t, T11_V, 22, .4, seed=4)
    dn = .03 * math.sin(math.pi * clamp((t - T11_V) / .3))
    s = 1.0 + .012 * math.sin(t * 1.2) + .4 * dn
    return frame_svg("".join(o), 540 + sh[0], 980 - 1920 * dn * -.5 + sh[1], s, .3 * math.sin(t * .8) + sh[0] * .04)


# ═══════════════════════════════ s12: крекер на кусочки ═══════════════════════════════
T12_K = wt("когда")         # 16.87
T12_S = wt("становится")    # 17.32
T12_KR = wt("крошечным")    # 17.80
T12_KR_HIT = T12_KR + .05   # ударный «кро»
CR12 = (540.0, 1010.0)
CR12_K = 2.0
N12 = 7
SMALL = N12 - 1
ROLL0 = T12_KR_HIT + .28
ROLL1 = 18.42


def s12(t):
    lib.dyn_begin()
    o = [paper_bg()]
    x, y = CR12
    k = CR12_K
    press = ease_io(clamp((t - T12_K - .1) / .25)) * (1 - ease_out(clamp((t - T12_KR_HIT) / .12)))
    crack = ease_out(clamp((t - T12_S) / .42), 2)
    bu = clamp((t - T12_KR_HIT) / .6)
    rock = (1 - press) * (1 - ease_io(clamp((t - T12_S) / .3))) * 7 * math.sin(t * 5.2 + .4)
    sq = 1 - .05 * press
    o.append(shadow(x, y + 300 * k * .55 + 10, 300 * (1 - .4 * bu) + 60, .12))
    hide = (SMALL,) if t >= T12_KR_HIT else ()
    cr = P.cracker(0, 0, k, crack if bu <= 0 else 1.0, bu, seed=1, n=N12, rot=rock, hide=hide)
    o.append(f'<g transform="translate({x:.1f} {y:.1f}) scale({1 + .03 * press:.4f} {sq:.4f})">{cr}</g>')
    if t >= T12_KR_HIT:
        o.append(impact(x, y, clamp((t - T12_KR_HIT) / .35), 330, 9, -180, 360, 9, 1200, .9))
    # самый маленький кусочек: отлетает, потом выкатывается вперёд к зрителю
    if t >= T12_KR_HIT:
        pieces, _ = P._cracker_pieces(74700 + 1, N12)
        c = pieces[SMALL][1]
        bu_r = clamp((min(t, ROLL0) - T12_KR_HIT) / .6)
        px, py = P.cracker_piece_c(x, y, k, SMALL, bu_r, seed=1, n=N12)
        r0 = P._piece_off(SMALL, c, bu_r, 74700 + 1)[2]
        if t <= ROLL0:
            o.append(P.cracker_piece(px, py, k, SMALL, r0, seed=1, n=N12))
        else:
            u = ease_out(clamp((t - ROLL0) / (ROLL1 - ROLL0)), 2)
            fx, fy = lerp(px, 560, u), lerp(py, 1200, u) - 50 * math.sin(math.pi * u)
            kk = k * (1 + .55 * u)
            o.append(shadow(fx, 1200 + 70 * kk * .5, 70 * kk * u, .14 * u))
            o.append(P.cracker_piece(fx, fy, kk, SMALL, r0 + 360 * u, seed=1, n=N12))
            if t > ROLL1:
                o.append(P.sparkles(fx, fy - 20, 1.3, clamp((t - ROLL1) / .15), t, seed=5, n=4, r=110))
    # лапа кота: занесена с кадра 0, на «Когда шаг» нажимает, на «крошечным» отдёргивается вверх
    lift = ease_in(clamp((t - T12_KR_HIT) / .25), 2)
    hover = (1 - press)
    tip = (lerp(620, 575, press) + 10 * math.sin(t * 3.3) * hover, lerp(640, 760, press) - 26 * hover * (.5 + .5 * math.sin(t * 4.1)))
    tip = (tip[0] + 160 * lift, tip[1] - 900 * lift)
    if lift < 1:
        o.append(people.cat_forearm((920 + 80 * lift, -120 - 400 * lift), tip, 1.7, claw=0.0, seed=3))
    # камера: наезд 5 %, на «крошечным» тряска и отскок 4 %
    push = .05 * ease_io(clamp((t - 16.65) / 1.6))
    sh = P.shake(t, T12_KR_HIT, 26, .38, seed=6)
    b = .04 * math.sin(math.pi * clamp((t - T12_KR_HIT) / .3))
    s = (1.0 + push) * (1 - b * .5)
    return frame_svg("".join(o), 540 + sh[0], 990 + sh[1] - 600 * b, s, .3 * math.sin(t * 1.1) + sh[0] * .04)


SCENES = {"s03": s03, "s11": s11, "s12": s12}


def frame(sid, t):
    return SCENES[sid](t)
