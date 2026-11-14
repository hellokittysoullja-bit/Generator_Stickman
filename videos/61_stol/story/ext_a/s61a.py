"""Рилс 61 «стол», группа A: стол-бардак Димы.
s01 (0–1.5) хук: стол крупно сверху-сбоку, гора бумажек, кружки, провода, лампа; рука Димы роется; «бумажки» (0.96) стопка взрывается
    веером в камеру; влёт 1/(1+0.4)→1 за 0.22 с с поворотом, тряска.
s02 (1.5–4.2) Дима за столом средним планом; «кружки» (1.72) кружка качается и звякает, «провода» (2.37) клубок опутывает запястье,
    «Мама» (3.42) взгляд к двери, виноватая улыбка.
s04 (7.1–9.9) Дима сбоку, лампочка-идея мигает и гаснет (7.55), он сползает, щека на ладони; кот шагает из-за кучи и на 8.9 запрыгивает
    на стол; «Знаешь» (9.75) поворачивает морду.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Люди и предметы — common/ (people, props)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import props  # noqa: E402
from lib import blob, clamp, ease_io, ease_out, ellipse_pts, f, line, mix, rect_pts, shape, svg, band, fill_d  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
INK = lib.INK


def lerp(a, b, u):
    return a + (b - a) * u


def bump(t, t0, dur):
    if t < t0:
        return 0.0
    return math.exp(-(t - t0) / dur * 3.0)


def hook_cam(t, hit, base, cx, cy):
    """Влёт правил 28–29: 1/(1+0.4) → 1 за 0.22 с, перелёт 5 %, поворот −3,4° с возвратом, удар +9 % на ударном слоге, занос вбок."""
    u = clamp(t / .22)
    e = 1 - (1 - u) ** 3
    m = 1 / (1 + .42 * (1 - e))
    if t > .22:
        tt = t - .22
        m *= 1 + .055 * math.exp(-tt * 7) * math.sin(min(tt * 18, math.pi))
    rot = -3.4 * (1 - e) + .5 * math.sin(t * 5)
    cx += 46 * (1 - e)
    if t > hit:
        tt = t - hit
        m *= 1 + .09 * math.exp(-tt * 8)
        rot += 1.6 * math.exp(-tt * 9) * math.sin(tt * 38)
        cx += 9 * math.exp(-tt * 11) * math.sin(tt * 55)
        cy += 10 * math.exp(-tt * 11) * math.sin(tt * 47 + 1)
    return cx, cy, base * m, rot


def whip_in(t, t0, dur=.16):
    """Хлёст на входе плана: (dx, размытие) — кадр влетает сбоку и тормозит."""
    u = clamp((t - t0) / dur)
    e = 1 - (1 - u) ** 3
    return 260 * (1 - e), 18 * (1 - e)


def frame_svg(body, cx, cy, s, rot, blur_x=0.0, bg="#2a2220"):
    cam = lib.cam(cx, cy, s, rot)
    g = f'<g transform="{cam}">{body}</g>'
    if blur_x > .5:
        fid = lib.uid("wb")
        lib.DEFS.append(f'<filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="{blur_x:.1f} 0"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/>' + g)


# ───────────────────────── мир стола (s01): вид сверху-сбоку ─────────────────────────
SLEEVE = ("#d4a23e", "#a97b25", "#8c6219")
SKIN = ("#ecc4a2", "#d39f83", "#bf8a74")


def _hand_kw():
    def sh(pts, fill, inner="", w=3.0, seed=0, **k):
        return shape(pts, fill, inner, w=w, seed=seed)

    def ln(pts, w=2.0, color=INK, seed=0, op=1.0, **k):
        return line(pts, w, color, taper=.4, wmin=.4, seed=seed, op=op)
    return dict(shape_fn=sh, line_fn=ln, skin=SKIN[0], skin_sh=SKIN[1], skin_sh2=SKIN[2])


def sleeve_arm(elbow, wrist, k, seed=0):
    """Рукав горчичного худи от локтя к запястью: не толще предплечья, у запястья резинка-манжета."""
    E, Wr = np.array(elbow, float), np.array(wrist, float)
    d = Wr - E
    L = np.linalg.norm(d)
    d /= L
    n = np.array([-d[1], d[0]])
    cuff0 = Wr - d * 34 * k
    mid = (E + cuff0) / 2 + n * 6 * k
    pts = [tuple(E), tuple(mid), tuple(cuff0)]
    o = []
    sl = band(pts, 104 * k, 92 * k, step=5, cap=False)
    inner = f'<path d="{fill_d(band([tuple(p + n * 22 * k) for p in map(np.array, pts)], 40 * k, 32 * k, step=6, cap=False))}" fill="{SLEEVE[1]}"/>'
    for j in range(3):   # складки рукава
        q = E + (cuff0 - E) * (.3 + .2 * j)
        inner += line([tuple(q - n * 32 * k + d * 6 * k), tuple(q + d * 18 * k), tuple(q + n * 18 * k + d * 10 * k)], 4 * k, SLEEVE[2], taper=.5, wmin=.3,
                      seed=seed + j)
    o.append(shape(sl, SLEEVE[0], inner, w=4.4, seed=seed + 5))
    cf = band([tuple(cuff0 - d * 2 * k), tuple(Wr + d * 6 * k)], 96 * k, 88 * k, step=4, cap=False)
    cin = "".join(line([tuple(cuff0 + d * (6 + 9 * j) * k - n * 44 * k), tuple(cuff0 + d * (6 + 9 * j) * k + n * 44 * k)], 2.4 * k, SLEEVE[1], taper=.2, wmin=.6,
                       seed=seed + 10 + j) for j in range(4))
    o.append(shape(cf, mix(SLEEVE[0], "#ffffff", .06), cin, w=4.0, seed=seed + 9))
    return "".join(o)


def desk_scene01(t):
    """Стол-бардак Димы крупно (мир 1080×1920 + запас за краями под влёт)."""
    o = []
    # стена над столом и сам стол
    o.append(blob(rect_pts(-500, -500, 1600, 480), "#D9C7A4"))
    for i in range(9):
        o.append(line([(-300 + 190 * i, -500), (-300 + 190 * i, 470)], 4, "#CDBA94", taper=.1, wmin=.8, seed=50 + i))
    o.append(props.sticky(840, 250, 1.6, 7, "pink", 4, "star") + props.sticky(980, 330, 1.4, -6, "yellow", 5, "lines"))
    o.append(props.wall_sketch(120, 220, 1.4, -5, 3, "spiral"))
    o.append(props.desk(540, 2150, 1900, 1.0, 1710, legs=False, seed=1))
    o.append(blob(rect_pts(-600, 2176, 1700, 2700), "#3A2C26"))
    # тёплый круг лампы: небольшой, чёткий край (не размытый овал)
    o.append(blob(ellipse_pts(250, 640, 190, 62, 24), "#D29A62"))
    o.append(blob(ellipse_pts(250, 640, 150, 46, 24), "#DDA872"))
    o.append(props.lamp_desk(160, 640, 1.7, on=1.0, tilt=-6))
    # кольца кофе, карандаш, стикер, зарядка, провода
    o.append(props.coffee_ring(330, 1080, 1.8, 10, 1) + props.coffee_ring(860, 1210, 1.5, -30, 2) + props.coffee_ring(640, 1420, 1.4, 50, 3))
    o.append(props.pencil(860, 1360, 1.4, -24) + props.sticky(160, 1420, 1.5, -14, "blue", 6, "arrow"))
    tang_w = 0.0
    o.append(props.cable_tangle(250, 1270, 1.9, 2, t * 1.5, tang_w))
    o.append(props.cable([(330, 1250), (420, 1330), (560, 1370), (720, 1460), (980, 1450), (1200, 1500)], w=10, seed=4))
    o.append(props.charger(990, 1450, 1.6, 70))
    # кружки: красная с паром, синяя
    o.append(props.mug(880, 780, 2.0, 0, "red", steam=1.0, t=t, seed=1))
    o.append(props.mug(170, 1060, 1.9, -4, "blue", handle=-1, seed=2, coffee=True))
    return "".join(o)


def pile01(t):
    """Гора бумаг посередине + верхняя стопка (до взрыва) и листы, которые шевелит рука."""
    o = [props.paper_pile(540, 1110, 2.3, 7, sy=.6, n=12)]
    return "".join(o)


def rummage(t):
    """Рука роется: запястье ходит туда-сюда, пальцы сжимаются; к 0.7 с хватает лист и тянет; на 0.96 отдёргивается."""
    ph = t * 2 * math.pi * 2.6
    wr = np.array([690 + 46 * math.sin(ph), 905 + 26 * math.sin(ph * .5 + 1)])
    if t > .96:
        u = clamp((t - .96) / .25)
        wr = wr + np.array([150, 90]) * ease_out(u)
    curl = .25 + .35 * (.5 + .5 * math.sin(ph + 1.2))
    return wr, curl, ph


def frame01(t):
    lib.dyn_begin()
    wr, curl, ph = rummage(t)
    o = [desk_scene01(t), pile01(t)]
    burst = t >= .96
    # листы, которые шевелит рука (лежат на горе)
    for j, (bx, by, br, bs) in enumerate(((470, 880, -14, 3), (600, 860, 18, 5), (540, 930, 6, 8))):
        jig = 0 if burst else 1
        rr = br + jig * 7 * math.sin(ph + j * 2)
        dx = jig * 10 * math.sin(ph * .5 + j)
        o.append(props.paper(bx + dx, by, 2.2, rr, 120, 160, bs, ("lines", "sketch", "grid")[j], .6))
    if not burst:
        # верхняя стопка — та, что взорвётся
        o.append(props.paper_stack(560, 860, 2.1, 6, 9, .35 + .2 * math.sin(ph), .6))
    # рука Димы справа: сначала кисть, рукав поверх запястья
    k = 1.55
    d = np.array([-1.0, -.32])
    elbow = wr + np.array([520, 250])
    hand = _hand_kw()
    import hand as H
    if not burst and t > .55:
        # лист, который рука тянет к себе: лежит ПОД пальцами (кончики пальцев прижимают его правый край)
        u = clamp((t - .55) / .4)
        tip = wr + d / np.linalg.norm(d) * 140 * k
        o.append(props.paper(tip[0] - 55 + 30 * u, tip[1] + 10, 1.9, -16 + 12 * u, 120, 160, 21, "sketch", .65))
    o.append(H.hand(tuple(wr), tuple(d), flip=-1, k=k, curl=(curl, curl + .05, curl + .1, curl + .12), spread=.18 + .1 * math.sin(ph),
                    thumb=.35, bend=.1, seed=40, **hand))
    o.append(sleeve_arm(tuple(elbow), tuple(wr), k * .95, seed=60))
    if burst:
        u = clamp((t - .96) / .62)
        o.append(props.fan_sheets(560, 840, u, 2.2, 11, 4, 1.15))
        o.append(props.clink(560, 820, 2.0, clamp((t - .96) / .3), 3, "#FFFFFF"))
    body = "".join(o)
    cx, cy, s, rot = hook_cam(t, .96, 1.22, 560, 930)
    dx, dy = props.shake(t, .96, 14, .4, 2)
    return frame_svg(body, cx + dx, cy + dy, s, rot)


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    if sid == "s01":
        return frame01(t)
    raise KeyError(sid)
