"""Рилс 58 «тревога», группа A: Дима средним планом.
s01 (0–1.4) хук: коридор у аудитории, Дима с зачёткой, руки трясутся, очередь силуэтов, влёт камеры 0.22 с.
s03 (2.7–4.3) аудитория: Дима за партой, билет, на «знает» (3.20) лампочка и строчки-штрихи ответов.
s06 (8.7–10.5) конспект: на «тревога» (8.69) растёт облако, на «вспомнить» (9.67) строчки вылетают со страницы.
s13 (26.61–29.1) комната днём: Дима достаёт из рюкзака листок и ручку, садится за стол; кот на подоконнике.
s15 (31.56–33.9) Дима складывает листок, на «карман» (32.22) прячет, на «голова» (32.80) уходят облачка.
s18 (38.5–40.8) финал как хук: коридор, Дима спокоен, зачётка, кот рядом; на «трясутся» (38.85) руки вздрагивают и успокаиваются.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Общие предметы — common/props.py."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import base_d as D  # noqa: E402
import cat as Cat  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props  # noqa: E402
import s56 as S  # noqa: E402
import room as ROOM  # noqa: E402
from lib import (blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rect_pts, shape, smooth, svg, back_out)  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
T = {i: w["start"] for i, w in enumerate(WORDS)}
INK = lib.INK
FLOOR_Y = 1440
lerp, hand_spec, kf = S.lerp, S.hand_spec, S.kf
_ST = {}


def whip(out, t, t0, dist=260):
    return S.whip(out, t, t0, dist)


def tremor(t, amp, seed=0.0, hz=1.0):
    """Мелкая дрожь: сумма быстрых несоизмеримых синусов, (dx, dy) в px."""
    a = t * hz
    return (amp * (.6 * math.sin(a * 61 + seed) + .4 * math.sin(a * 97 + seed * 2.3)),
            amp * (.6 * math.sin(a * 73 + seed * 1.7) + .4 * math.sin(a * 113 + seed * .6)))


def expr_of(**kw):
    e = dict(lid=.9, look=(.5, .1), brows="worry", mouth="flat", flush=.0)
    e.update(kw)
    return e


def cam_group(body, cam):
    D.set_ink(cam[2])
    return f'<g transform="{lib.cam(*cam)}">{body}</g>'


# ═════════════════════════ люди на заднем плане ═════════════════════════
def student(x, y, k, col, hair, seed, face=1, skin="#E8BE9C", legs="#46506E", bag=None, phone=False, sway=0.0, t=0.0, tone=.0):
    """Силуэт студента в очереди (дальний план): (x, y) — подошвы. Высота ≈ 640·k. Цвета слегка выцвечены к стене (tone)."""
    c = lambda h: mix(h, "#CFDAD2", tone)
    sx = sway * math.sin(t * 1.3 + seed)
    o = []
    H = 640.0
    # ноги
    for i, dx in enumerate((-24, 26)):
        lg = [(dx - 20, -300, 1), (dx + 20, -300, 1), (dx + 17, -22, 1), (dx - 17, -22, 1)]
        o.append(shape(lg, c(legs), blob([(dx + 4, -300), (dx + 20, -300), (dx + 17, -22), (dx + 4, -22)], mix(c(legs), "#000000", .2)), w=4.2, seed=seed * 7 + i))
        o.append(shape([(dx - 24 * face * (-1 if face < 0 else 1) - 6, -24, 1), (dx + 30 * face, -24, 1), (dx + 32 * face, 0, 1), (dx - 22, 0, 1)], c("#E9E4DA"), "", w=3.6, seed=seed * 7 + 3 + i))
    # торс
    tor = [(-52, -300, 1), (52, -300, 1), (60, -470), (44, -540, 1), (-44, -540, 1), (-60, -470)]
    o.append(shape(tor, c(col), blob([(18, -540), (60, -470), (52, -300), (18, -300)], mix(c(col), "#000000", .18)), w=4.6, seed=seed * 7 + 5))
    if bag:
        o.append(line([(-40, -530), (-6, -390), (30, -300)], 8, c(bag), taper=.1, wmin=.9, seed=seed * 7 + 6))
    # руки вдоль тела
    for sd, dx in ((8, -62), (9, 62)):
        arm = [(dx - 14, -520), (dx + 14, -520), (dx + 12, -330), (dx - 12, -330)]
        o.append(shape(arm, c(col), "", w=4.0, seed=seed * 7 + sd))
        o.append(shape(ellipse_pts(dx, -318, 14, 17, 8), c(skin), "", w=3.2, seed=seed * 7 + sd + 2))
    if phone:
        o.append(shape(rect_pts(face * 40, -430, face * 66, -380, 3), "#2b2f3a", "", w=3, seed=seed * 7 + 12))
    # голова
    o.append(shape(rect_pts(-12, -560, 12, -532, 3), c(skin), "", w=3.6, seed=seed * 7 + 10))
    hd = ellipse_pts(face * 4, -606, 46, 54, 14)
    o.append(shape(hd, c(skin), "", w=4.4, seed=seed * 7 + 11))
    hr = [(-46 + face * 4, -610, 1), (-38 + face * 4, -656), (4 + face * 4, -668), (44 + face * 4, -648), (46 + face * 4, -606, 1), (28 + face * 4, -626), (-10 + face * 4, -632),
          (-40 + face * 4, -622)]
    o.append(shape(hr, c(hair), "", w=4.0, seed=seed * 7 + 13))
    o.append(blob(ellipse_pts(face * 24, -604, 4, 5, 6), INK))
    return f'<g transform="translate({f(x + sx)} {f(y)}) scale({k:.4f})">{"".join(o)}</g>'


def corridor_static():
    o = []
    o.append('<rect x="-1600" y="-2200" width="4400" height="3600" fill="#DCE6DC"/>')
    o.append('<rect x="-1600" y="1000" width="4400" height="360" fill="#A9C2B6"/>')
    o.append(line([(-1600, 1000), (2800, 1000)], 7, INK, taper=.02, wmin=.95, seed=100))
    o.append(line([(-1600, 1000), (2800, 1000)], 3, "#EFE7D3", taper=.02, wmin=.95, seed=101))
    for k in range(-8, 18):
        o.append(line([(k * 160, 1010), (k * 160, 1330)], 2.2, "#8FAAA0", taper=.02, wmin=.95, seed=110 + k, op=.8))
    # пол
    o.append('<rect x="-1600" y="1330" width="4400" height="1000" fill="#D2BE98"/>')
    for k, y in enumerate((1410, 1500, 1620, 1760)):
        o.append(line([(-1600, y), (2800, y + 2)], 2.6, "#B8A27A", taper=.02, wmin=.95, seed=130 + k, op=.8))
    for k in range(-14, 30):
        o.append(line([(k * 130, 1330), (k * 130 - 90 + (k % 3) * 20, 1990)], 2.2, "#B8A27A", taper=.02, wmin=.95, seed=150 + k, op=.6))
    o.append(shape(rect_pts(-1600, 1316, 2800, 1344), "#EFE7D3", "", w=4.2, seed=140))
    # окно слева: дневной свет, переплёт
    x0, y0, x1, y1 = -40, 330, 300, 860
    sk = lib.lin_grad([(0, "#9ED0F0", 1), (1, "#E4F3FA", 1)], 0, 0, 0, 1)
    inn = f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="url(#{sk})"/>'
    inn += blob(ellipse_pts(150, 450, 40, 40, 16), "#FFF1AE") + blob(ellipse_pts(220, 560, 62, 22, 14), "#FFFFFF") + blob(ellipse_pts(60, 640, 50, 18, 14), "#FFFFFF")
    inn += blob([(x0 - 10, 780), (60, 760), (60, 700), (150, 700), (150, 770), (230, 740), (230, 690), (x1 + 10, 700), (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)], "#8FB4C6")
    inn += blob(rect_pts(120, y0, 140, y1), "#F3ECDA") + blob(rect_pts(x0, 560, x1, 580), "#F3ECDA")
    o.append(shape(rect_pts(x0, y0, x1, y1, 8), "#F3ECDA", inn, w=5, seed=160))
    o.append(shape(rect_pts(x0 - 20, y1 - 2, x1 + 24, y1 + 24, 6), "#F3ECDA", "", w=4.2, seed=161))
    # доска объявлений: пробка и цветные листки (без букв)
    o.append(shape(rect_pts(360, 460, 600, 760, 8), "#C89B62", blob(rect_pts(360, 700, 600, 760), "#A97E48"), w=5.0, seed=170))
    for i, (px, py, pw, ph, col) in enumerate(((380, 484, 80, 110, "#F7F1DE"), (480, 480, 96, 70, "#9CC7E8"), (392, 620, 90, 100, "#F0B8A8"), (506, 590, 76, 118, "#F7F1DE"))):
        o.append(shape(rect_pts(px, py, px + pw, py + ph, 2), col, "".join(line([(px + 10, py + 16 + j * 16), (px + pw - 10 - (j % 2) * 16, py + 16 + j * 16)], 2.0, "#7F8AA0", taper=.1, wmin=.8,
                                                                                    seed=180 + i * 5 + j) for j in range(int((ph - 24) // 16))), w=3.0, seed=171 + i))
        o.append(blob(ellipse_pts(px + pw / 2, py + 6, 4, 4, 6), "#C9503C"))
    # двери аудитории справа
    dx0, dx1, dy0 = 760, 1100, 480
    o.append(shape(rect_pts(dx0 - 22, dy0 - 24, dx1 + 22, 1330, 4), "#6B4A30", "", w=5, seed=190))
    for i, (a, b) in enumerate(((dx0, (dx0 + dx1) // 2 - 3), ((dx0 + dx1) // 2 + 3, dx1))):
        o.append(shape(rect_pts(a, dy0, b, 1330, 3), "#9A6B43", blob(rect_pts(a + (b - a) * .7, dy0, b, 1330), "#82582F", .9) +
                       blob(rect_pts(a + 26, dy0 + 40, b - 26, dy0 + 150, 4), "#CBE2EE") + blob(rect_pts(a + 26, dy0 + 40, b - 26, dy0 + 60), "#E6F2F6") +
                       blob(rect_pts(a + 26, dy0 + 220, b - 26, 1230, 4), "#8A5C38") + line([(a + 30, dy0 + 40), (a + 30, dy0 + 150)], 3, "#FFFFFF", taper=.1, wmin=.8, seed=191 + i),
                       w=4.4, seed=192 + i))
        o.append(shape(ellipse_pts(b - 18 if i == 0 else a + 18, 960, 7, 22, 8), "#C4C9CF", "", w=3, seed=195 + i))
    o.append(shape(rect_pts(dx0 + 60, dy0 - 70, dx1 - 60, dy0 - 36, 4), "#4E8C6E", blob(rect_pts(dx0 + 100, dy0 - 58, dx1 - 100, dy0 - 48), "#E9F2EA"), w=4, seed=197))
    # скамейка у стены
    o.append(shape(rect_pts(1180, 1130, 1500, 1160, 3), "#B88A5A", "", w=4, seed=198))
    for i, lx in enumerate((1200, 1480)):
        o.append(shape(rect_pts(lx - 8, 1160, lx + 8, 1320, 2), "#7A8288", "", w=3.4, seed=199 + i))
    return "".join(o)


def queue(t, k=1.0):
    """Очередь силуэтов у двери (дальний план, слегка выцвечены): стоят, кто-то в телефоне, покачиваются."""
    o = []
    for i, (x, col, hair, face, bag, ph, kk) in enumerate(((600, "#C9744A", "#3A2A20", 1, "#4A5A8C", False, .92), (700, "#5F86A8", "#8A5A2A", 1, None, True, .96),
                                                           (800, "#7D9A6A", "#2A2A32", -1, "#8A4A5A", False, .9), (1190, "#8A5A9A", "#6A4A30", -1, None, False, .94))):
        o.append(student(x, 1392, kk * k, col, hair, i + 3, face, bag=bag, phone=ph, sway=3.5, t=t, tone=.32))
    return "".join(o)


def corridor_world(t):
    return _ST["corr"] + queue(t)


# ═════════════════════════ зачётка в руках ═════════════════════════
HB = dict(n_off=(26, 60), f_off=(-30, 62), n_dir=(-.35, -1), f_dir=(.4, -1), n_flip=-1, f_flip=1, n_curl=.7, f_curl=.6, n_th=.5, f_th=.4)


def hold_book(t, x, hip_y, *, lean=.04, ha=0.0, expr=None, shake=1.0, calm=0.0, book_k=1.5, extra_drop=None, hip_dx=0.0, seed=0.0, sx=1.0):
    """Дима стоит и держит зачётку двумя руками на груди. shake 0…1 — сила дрожи рук, calm — спокойствие позы. Возвращает слои."""
    px, py = x + hip_dx, 0.0
    jx, jy = tremor(t, 5.5 * shake, seed)
    jx2, jy2 = tremor(t, 4.5 * shake, seed + 3.0)
    bk = tremor(t, 2.5 * shake, seed + 7.0)
    # положение книги — перед грудью, чуть правее
    bx, by = px + 150 + bk[0], 955 + bk[1]
    n_t = (bx + HB["n_off"][0] + jx, by + HB["n_off"][1] + jy)         # ближняя рука — запястье у нижнего правого угла
    f_t = (bx + HB["f_off"][0] + jx2, by + HB["f_off"][1] + jy2)
    ex = dict(lid=.95 - .15 * calm, look=(.82, .05), brows="worry" if calm < .5 else "calm", mouth="flat")
    if expr:
        ex.update(expr)
    hands = {"n": dict(hand_spec(HB["n_curl"], HB["n_dir"], HB["n_th"], k=.95), flip=HB["n_flip"]),
             "f": dict(hand_spec(HB["f_curl"], HB["f_dir"], HB["f_th"], k=.95), flip=HB["f_flip"])}
    d = S.stand(t, px, lean=lean, ha=ha, expr=ex, n_t=n_t, f_t=f_t, hands=hands, hip_dy=hip_y - 1108, sn=-1, sf=-1,
                head_off=(jx * .25, jy * .25))
    bk_svg = props.gradebook(bx, by, book_k, rot=-4 + .8 * jx, open_=0.0)
    return d, bk_svg, (bx, by)


def dima_stack(d, mid_before_near="", behind=""):
    lg, af, bd, an = S.dima_layers(d)
    return behind + lg + af + mid_before_near + bd + an


def sweat(x, y, t, seed, s=1.0):
    return S.sweat_drop(x, y, t, seed, s)


def tremor_marks(x, y, t, k=1.0, n=3, col="#8F8A7E", spread=40):
    """Штрихи дрожи вокруг рук: короткие дуги по обе стороны, мигают на 30 Гц."""
    o = []
    for i in range(n):
        ph = (math.sin(t * 47 + i * 2.1) + 1) / 2
        a = math.radians(-60 + 70 * i + 12 * math.sin(t * 31 + i))
        r0, r1 = 54 * k, (82 + 18 * ph) * k
        c, s_ = math.cos(a), math.sin(a)
        for sg in (-1, 1):
            o.append(line([(x + sg * r0 * c, y + r0 * s_), (x + sg * r1 * c, y + r1 * s_)], 6 * k, col, taper=.5, wmin=.15, seed=700 + i * 2 + (sg > 0), peak=.4))
    return "".join(o)


# ═════════════════════════ s01 ═════════════════════════
def frame01(t):
    base_z = 1.32
    if t < .22:
        u = ease_out(t / .22, 3)
        z = base_z / 1.4 + (base_z - base_z / 1.4) * u
        rot = -2.6 * (1 - u)
    else:
        z, rot = base_z, 0.0
    # затем лёгкий дрейф
    dr = clamp((t - .22) / 1.4)
    cx, cy = 505 - 14 * dr, 1085 - 6 * dr
    shake = 1.0 + .5 * smooth(1.0, 1.4, t)
    ex = expr_of(lid=.98, look=(.85 + .05 * math.sin(t * 9), .05), brows="worry", mouth="talk", open=.12 + .08 * (math.sin(t * 23) > 0), smile=0.0,
                 hair=.5 * math.sin(t * 30), flush=.15)
    d, bk, (bx, by) = hold_book(t, 330, 1108 + 2 * math.sin(t * 34), lean=.045, ha=.04, expr=ex, shake=shake)
    hp = S.head_w(d)
    o = [corridor_world(t)]
    lg, af, bd, an = S.dima_layers(d)
    o += [lg, af, bk, bd, an]
    o.append(tremor_marks(bx + 8, by + 40, t, 1.0, 3))
    o.append(tremor_marks(bx + 8, by + 40, t + .5, .7, 2, spread=60))
    o.append(sweat(hp[0] + 100, hp[1] - 40, t, 2, .9))
    o.append(sweat(hp[0] - 60, hp[1] - 70, t + .6, 5, .7))
    return cam_group("".join(o), (cx, cy, z, rot))


# ═════════════════════════ диспетчер ═════════════════════════
def frame(sid, t):
    if not _ST.get("init"):
        D.DAY[0] = True
        _ST["corr"] = corridor_static()
        lib.static_done()
        _ST["init"] = True
    lib.dyn_begin()
    body = FRAMES[sid](t)
    return svg(f'<rect width="1920" height="1920" fill="#d9e3da"/>{body}')


FRAMES = {"s01": frame01}
