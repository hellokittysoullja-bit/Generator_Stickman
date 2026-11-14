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
    for i, (x, col, hair, face, bag, ph, kk) in enumerate(((650, "#C9744A", "#3A2A20", 1, "#4A5A8C", False, .84), (790, "#5F86A8", "#8A5A2A", 1, None, True, .88),
                                                           (930, "#7D9A6A", "#2A2A32", -1, "#8A4A5A", False, .82), (1210, "#8A5A9A", "#6A4A30", -1, None, False, .86))):
        o.append(student(x, 1392, kk * k, col, hair, i + 3, face, bag=bag, phone=ph, sway=3.5, t=t, tone=.32))
    return "".join(o)


def corridor_world(t):
    return _ST["corr"] + queue(t)


# ═════════════════════════ зачётка в руках ═════════════════════════
HB = dict(n_off=(36, 64), f_off=(-34, 66), n_dir=(-.35, -1), f_dir=(.4, -1), n_flip=-1, f_flip=1, n_curl=.7, f_curl=.6, n_th=.5, f_th=.4)


def hold_book(t, x, hip_y, *, lean=.04, ha=0.0, expr=None, shake=1.0, calm=0.0, book_k=1.8, extra_drop=None, hip_dx=0.0, seed=0.0, sx=1.0):
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



# ═════════════════════════ сидящий Дима ═════════════════════════
def sit(x, hip_y, *, lean=.1, ha=0.0, expr=None, n_t, f_t, hands=None, head_off=(0, 0), bob=0.0, fx=(215, 190), floor=1468, torso_k=1.0, sn=None, sf=None,
        hip_dx=0.0):
    e = expr_of()
    if expr:
        e.update(expr)
    hands = hands or {"n": hand_spec(.35), "f": hand_spec(.35)}
    shx = x + 240 * math.sin(lean) + 6
    sn = sn if sn is not None else (-1 if n_t[0] >= shx else 1)
    sf = sf if sf is not None else (-1 if f_t[0] >= shx else 1)
    p = dict(hip=(x + hip_dx, hip_y + bob), scale=S.BS, lean=lean, torso_k=torso_k, feet={"n": ((x + fx[0], floor), 0.0), "f": ((x + fx[1], floor - 5), 0.0)},
             arms={"n": ("ik", n_t, sn), "f": ("ik", f_t, sf)}, hands=hands, expr=e, head_ang=ha, head_off=head_off, hood=0.0, strings=(0, 0))
    d = people.draw(p, "dima")
    d["x"], d["sx"] = x + hip_dx, 1.0
    return d


def bulb(x, y, k, u, t):
    """Лампочка идеи: вспыхивает (back_out), лучи, нить; u 0…1 — рост."""
    if u <= .01:
        return ""
    s = back_out(u, 2.0) * k
    o = []
    for i in range(9):
        a = math.radians(-160 + 18 * i + 2 * math.sin(t * 20 + i))
        r0, r1 = 62 * s, (92 + 16 * (i % 2) + 6 * math.sin(t * 30 + i)) * s
        o.append(line([(x + r0 * math.cos(a), y - 10 * s + r0 * math.sin(a)), (x + r1 * math.cos(a), y - 10 * s + r1 * math.sin(a))], 7 * s, "#F2C84B", taper=.5, wmin=.2,
                      seed=7100 + i, peak=.5))
    o.append(shape(rect_pts(x - 15 * s, y + 38 * s, x + 15 * s, y + 62 * s, 3), "#9AA0A6", blob(rect_pts(x + 3 * s, y + 38 * s, x + 15 * s, y + 62 * s), "#7A8288"), w=3.6 * s, seed=7120))
    bp = ellipse_pts(x, y - 8 * s, 40 * s, 44 * s, 16)
    o.append(shape(bp, "#FFE36A", blob(ellipse_pts(x + 14 * s, y, 20 * s, 30 * s, 10), "#F2C84B") + blob(ellipse_pts(x - 14 * s, y - 20 * s, 8 * s, 12 * s, 8), "#FFFFFF"), w=4.2 * s, seed=7121))
    o.append(line([(x - 12 * s, y + 38 * s), (x - 8 * s, y + 6 * s), (x, y + 16 * s), (x + 8 * s, y + 6 * s), (x + 12 * s, y + 38 * s)], 3.2 * s, INK, taper=.1, wmin=.8, seed=7122))
    return "".join(o)


def answer_card(x, y, k, t, t0, n=4):
    """Карточка с ответами: строчки-штрихи рисуются слева направо одна за другой (без букв)."""
    W, H = 150 * k, 112 * k
    o = [shape(rect_pts(x - W / 2, y - H / 2, x + W / 2, y + H / 2, 6), "#FFFFFF", blob(rect_pts(x + W * .3, y - H / 2, x + W / 2, y + H / 2), "#ECE6D2"), w=4.4 * k, seed=7130)]
    for i in range(n):
        u = clamp((t - t0 - .09 * i) / .22)
        if u <= 0:
            continue
        yy = y - H / 2 + (20 + i * 22) * k
        L = (W - 34 * k) * (.95 - .12 * (i % 2))
        o.append(line([(x - W / 2 + 16 * k, yy), (x - W / 2 + 16 * k + L * u * .5, yy - 2 * k), (x - W / 2 + 16 * k + L * u, yy + 1.5 * k)], 5 * k, "#2a2d30", taper=.2, wmin=.7, seed=7140 + i))
        if i == 0 and u > .9:
            pass
    return "".join(o)


def hall_static():
    o = []
    o.append('<rect x="-1600" y="-2200" width="4400" height="3600" fill="#E6E0CE"/>')
    o.append('<rect x="-1600" y="880" width="4400" height="460" fill="#C7B792"/>')
    o.append(line([(-1600, 880), (2800, 880)], 6, INK, taper=.02, wmin=.95, seed=300))
    o.append(line([(-1600, 880), (2800, 880)], 3, "#F2ECD8", taper=.02, wmin=.95, seed=301))
    # высокие окна слева
    for i, x0 in enumerate((-100, 160, 420)):
        sk = lib.lin_grad([(0, "#A7D4F0", 1), (1, "#E8F4FA", 1)], 0, 0, 0, 1)
        inn = f'<rect x="{x0 - 8}" y="190" width="{200}" height="{720}" fill="url(#{sk})"/>' + blob(ellipse_pts(x0 + 90, 420, 52, 20, 12), "#FFFFFF") + blob(rect_pts(x0 + 90, 190, x0 + 110, 900), "#F3ECDA")
        o.append(shape(rect_pts(x0, 200, x0 + 190, 900, 6), "#F3ECDA", inn, w=5, seed=310 + i))
    # доска справа (пустая, штрихи мела — без букв)
    o.append(shape(rect_pts(740, 330, 1300, 740, 8), "#3F5A50", blob(rect_pts(1100, 330, 1300, 740), "#35493F") + line([(790, 420), (1020, 430)], 6, "#E8E8E0", taper=.2, wmin=.7, seed=320) +
                   line([(790, 480), (960, 486)], 6, "#E8E8E0", taper=.2, wmin=.7, seed=321) + line([(790, 540), (1060, 548)], 6, "#E8E8E0", taper=.2, wmin=.7, seed=322), w=6, seed=323))
    o.append(shape(rect_pts(740, 740, 1300, 756, 3), "#A98055", "", w=4, seed=324))
    # пол: доски
    o.append('<rect x="-1600" y="1340" width="4400" height="1000" fill="#B58B5C"/>')
    for k, y in enumerate((1420, 1520, 1650, 1800)):
        o.append(line([(-1600, y), (2800, y + 2)], 2.6, "#8E6A43", taper=.02, wmin=.95, seed=330 + k, op=.8))
    o.append(shape(rect_pts(-1600, 1326, 2800, 1352), "#F2ECD8", "", w=4.2, seed=340))
    return "".join(o)


def seated_student(x, floor, k, col, hair, seed, face=1, tone=.3, t=0.0, lean=0.0, desk_w=200):
    c = lambda h: mix(h, "#E6E0CE", tone)
    skin = "#E8BE9C"
    sw = 2.5 * math.sin(t * 1.1 + seed)
    o = []
    top = floor - 190 * k
    tor = [(-48, top + 24, 1), (48, top + 24, 1), (54, top - 90), (38, top - 156, 1), (-38, top - 156, 1), (-54, top - 90)]
    o.append(shape([(p[0] * k + x + sw + lean * (top - p[1]), p[1]) + ((1,) if len(p) > 2 else ()) for p in [(q[0], q[1]) for q in tor]], c(col), "", w=4.2 * k, seed=seed * 5))
    hx, hy = x + face * 6 * k + sw + lean * 150, top - 222 * k
    o.append(shape(ellipse_pts(hx, hy, 40 * k, 46 * k, 14), c(skin), "", w=4 * k, seed=seed * 5 + 1))
    o.append(shape([(hx - 40 * k, hy - 4 * k, 1), (hx - 34 * k, hy - 44 * k), (hx + 4 * k, hy - 54 * k), (hx + 40 * k, hy - 40 * k), (hx + 40 * k, hy - 4 * k, 1), (hx + 24 * k, hy - 26 * k),
                    (hx - 8 * k, hy - 30 * k), (hx - 34 * k, hy - 22 * k)], c(hair), "", w=3.8 * k, seed=seed * 5 + 2))
    o.append(blob(ellipse_pts(hx + face * 22 * k, hy + 2 * k, 3.6 * k, 4.4 * k, 6), INK))
    # парта перед ним
    dw = desk_w * k
    o.append(shape(rect_pts(x - dw / 2, top + 22 * k, x + dw / 2, top + 46 * k, 2), c("#C99A62"), "", w=3.6 * k, seed=seed * 5 + 3))
    o.append(shape(rect_pts(x - dw / 2, top + 46 * k, x + dw / 2, top + 58 * k, 2), c("#A87B47"), "", w=3.4 * k, seed=seed * 5 + 4))
    for sx in (-1, 1):
        o.append(shape(rect_pts(x + sx * (dw / 2 - 16 * k) - 4 * k, top + 58 * k, x + sx * (dw / 2 - 16 * k) + 4 * k, floor, 1), c("#7A8288"), "", w=3 * k, seed=seed * 5 + 5 + sx))
    return "".join(o)


def hall_back(t):
    o = []
    row3 = ((90, "#B35D4A", "#2E2A2A"), (330, "#6F8FB5", "#6A4A2E"), (570, "#7FA070", "#3A2A20"), (810, "#C99A4A", "#1E1E26"), (1060, "#9A7AAE", "#7A5A38"), (1290, "#5C8A8F", "#2E2A2A"))
    for i, (x, col, hair) in enumerate(row3):
        o.append(seated_student(x, 1290, .55, col, hair, 20 + i, 1 if i % 2 == 0 else -1, tone=.42, t=t, desk_w=250))
    row2 = ((190, "#D98F4A", "#3A2A20"), (480, "#4E78A0", "#2A2A32"), (760, "#A8584A", "#8A5A2A"), (1040, "#6F9A78", "#2E2A2A"), (1320, "#8D7DB0", "#5A3A2A"))
    for i, (x, col, hair) in enumerate(row2):
        o.append(seated_student(x, 1380, .72, col, hair, 40 + i, 1 if i % 2 == 1 else -1, tone=.28, t=t, desk_w=250))
    return "".join(o)


# ═════════════════════════ s03 ═════════════════════════
def frame03(t):
    T_K = T[8]                       # «знает» 3.20
    u = clamp((t - 2.5) / 2.0)
    Dx = 300
    hip = 1244
    conf = smooth(T_K - .1, T_K + .3, t)
    bob = 2.2 * math.sin(t * 5.5)
    ex = expr_of(lid=.78 + .1 * conf, look=(.78, .42 - .3 * conf), brows="calm" if conf < .5 else "up", mouth="smile", smile=.25 + .6 * conf, blush=.3 * conf)
    dx, dy = Dx + 340, 1176
    # ближняя рука лежит на билете, дальняя на краю парты
    n_t = (dx + 20 + 6 * math.sin(t * 2.1), dy - 2 + 3 * math.sin(t * 2.7))
    f_t = (dx - 40, dy - 6)
    d = sit(Dx, hip, lean=.1 + .01 * math.sin(t * 2), ha=.03 * math.sin(t * 1.9), expr=ex, n_t=n_t, f_t=f_t,
            hands={"n": hand_spec(.45, (1, .25), .3), "f": hand_spec(.35, (1, .3), .25)}, bob=bob)
    lg, af, bd, an = S.dima_layers(d)
    hp = S.head_w(d)
    desk_cx = Dx + 230 + 300
    o = [_ST["hall"], hall_back(t), ROOM.chair(Dx, 1266, 1, 2300)]
    o.append(props.desk(desk_cx, 1196, 1.0, 620, legs_to=1468, depth=34))
    o.append(ticket_flat(dx + 120, 1170))
    o += [lg, af, bd, an]
    o.append(bulb(hp[0] + 40, hp[1] - 220, 1.1, clamp((t - T_K) / .28), t))
    if t > T_K + .08:
        o.append(answer_card(hp[0] + 250, hp[1] - 240, 1.25 * back_out(clamp((t - T_K - .08) / .3), 1.6), t, T_K + .35, 4))
    cam = (lerp(520, 560, u), lerp(1020, 1000, u), 1.18 + .16 * ease_io(u), -.5 + 1.0 * u)
    return cam_group("".join(o), cam)


def ticket_flat(x, y, w=110, h=40):
    """Билет лежит на парте (вид сверху-сбоку): параллелограмм, штрихи вместо текста."""
    pts = [(x - w / 2, y - h / 2, 1), (x + w / 2 + 8, y - h / 2 + 2, 1), (x + w / 2 - 6, y + h / 2, 1), (x - w / 2 - 12, y + h / 2 - 2, 1)]
    inner = blob([(x - w / 2, y - h / 2 + 4), (x - w / 2 + 40, y - h / 2 + 4), (x - w / 2 + 34, y - h / 2 + 12), (x - w / 2 - 4, y - h / 2 + 12)], "#7E8CB0")
    for j in range(3):
        yy = y - h / 2 + 18 + j * 8
        inner += line([(x - w / 2 + 6 - j, yy), (x + w / 2 - 14 - (j % 2) * 16, yy + 1)], 2.2, "#2a2d30", taper=.15, wmin=.7, seed=7200 + j)
    return shape(pts, props.C_TICKET, inner, w=3.0, seed=7201)


# ═════════════════════════ комната днём: общие вещи ═════════════════════════
def room_desk_base():
    return _ST["room_day"]


def notes_open(x, y, k, t, *, left=1.0, right=1.0, turn=0.0, seed=0):
    """Раскрытый конспект на столе (вид сверху-сбоку, ширина ≈ 340 k): страницы со штрихами строк, turn 0…1 — страница переворачивается справа налево.
    left/right — доля записанных строк. Возвращает (svg, [(x0, y0, x1, y1) центры строк правой страницы])."""
    o = []
    cover = [(x - 168 * k, y - 16 * k, 1), (x + 168 * k, y - 18 * k, 1), (x + 190 * k, y + 36 * k, 1), (x - 190 * k, y + 38 * k, 1)]
    o.append(shape(cover, "#4F7FA8", "", w=4 * k, seed=9980 + seed))

    def page(sgn, frac, sd):
        if sgn < 0:
            pts = [(x - 180 * k, y - 10 * k, 1), (x - 4 * k, y - 16 * k, 1), (x - 4 * k, y + 32 * k, 1), (x - 182 * k, y + 32 * k, 1)]
        else:
            pts = [(x + 4 * k, y - 16 * k, 1), (x + 172 * k, y - 10 * k, 1), (x + 178 * k, y + 32 * k, 1), (x + 4 * k, y + 32 * k, 1)]
        ln = ""
        n = 5
        for j in range(n):
            if j / n >= frac:
                break
            yy = y - 6 * k + j * 8.6 * k
            ln += line([(x + sgn * 16 * k, yy), (x + sgn * (150 - 14 * (j % 3)) * k, yy + .6 * k)], 2.8 * k, "#2a2d30", taper=.15, wmin=.7, seed=sd + j)
        return shape(pts, "#F7F2E4", ln, w=3.4 * k, seed=sd + 20)

    o.append(page(-1, left, 9990 + seed))
    o.append(page(1, right, 9960 + seed))
    if turn > .02:
        th = turn * math.pi
        wx = 170 * math.cos(th) * k
        lift = 56 * math.sin(th) * k
        pts = [(x + 4 * k, y - 16 * k, 1), (x + wx, y - 14 * k - lift, 1), (x + wx - 4 * math.sin(th) * k, y + 30 * k - lift * .5, 1), (x + 4 * k, y + 32 * k, 1)]
        ln = ""
        for j in range(4):
            yy = y - 6 * k + j * 8.6 * k - lift * .5
            ln += line([(x + 16 * k * math.cos(th), yy), (x + wx - 14 * k * math.cos(th), yy)], 2.8 * k, "#2a2d30", taper=.15, wmin=.7, seed=9940 + j)
        o.append(shape(pts, "#EFE8D3", ln, w=3.4 * k, seed=9945))
    return "".join(o)


# ═════════════════════════ s06 ═════════════════════════
def frame06(t):
    T_A, T_V = T[19], T[21]         # «тревога» 8.69, «вспомнить» 9.67
    u = clamp((t - 8.5) / 2.2)
    cl = clamp((t - T_A) / .5)
    sh = math.exp(-(t - T_V) * 9) * (t >= T_V)
    flip_ph = ((t - 8.7) / .62) % 1.0
    turning = 1 if t < T_V else 0
    turn = ease_io(flip_ph) if turning else 0.0
    frown = smooth(T_A - .1, T_A + .4, t)
    ex = expr_of(lid=.72 - .1 * frown, look=(.6, .55), brows=("worry", "det", frown), mouth="flat", sweat=0, flush=.1 * frown)
    nx, ny, nk = 640, 1138, 1.1
    # конспект: до «вспомнить» — страницы со строками, потом пустеют
    emp = smooth(T_V, T_V + .55, t)
    left = 1 - emp
    right = 1 - emp
    # ближняя рука держит край переворачиваемой страницы
    n_t = (nx + 40 - 100 * turn, ny - 6 - 26 * math.sin(math.pi * turn) * turning)
    f_t = (nx - 120, ny + 4)
    hnd = {"n": hand_spec(.5, (1, .2), .35), "f": hand_spec(.4, (1, .3), .3)}
    d = D.dima(.11 + .01 * math.sin(t * 2), {"n": ("ik", n_t), "f": ("ik", f_t)}, hnd, ex, head_ang=.04 * frown + .02 * math.sin(t * 3), head_off=(0, 3 * frown),
               hip_off=(1.5 * math.sin(t * 90) * sh, 1.5 * math.sin(t * 77) * sh))
    d["x"], d["sx"] = 250, 1.0
    lg, af, bd, an = S.dima_layers(d)
    hp = S.head_w(d)
    legs, top = _ST["desk_legs"], _ST["desk_top"]
    o = [_ST["room_day"], ROOM.chair(250, 1266, 1, 2300), legs, lg, af, bd, top]
    o.append(notes_open(nx, ny, nk, t, left=left, right=right, turn=turn))
    # строчки вылетают со страницы на «вспомнить»
    if t >= T_V:
        for j in range(12):
            tt = (t - T_V - .03 * j)
            if tt < 0 or tt > .9:
                continue
            ph = tt / .9
            sx0 = nx - 140 + (j % 6) * 52 + (j // 6) * 8
            sy0 = ny - 4 + (j // 6) * 10
            vx = (-70 + 28 * (j % 5)) + 22 * math.sin(j * 1.7)
            vy = -420 - 40 * (j % 3)
            px, py = sx0 + vx * ph, sy0 + vy * ph + 90 * ph * ph
            L = 64 * (1 - ph) + 6
            a = (j * 37) % 40 - 20
            o.append(line([(px - L / 2 * math.cos(math.radians(a)), py - L / 2 * math.sin(math.radians(a))), (px + L / 2 * math.cos(math.radians(a)), py + L / 2 * math.sin(math.radians(a)))],
                          5.5 * (1 - ph) + 1.5, "#2a2d30", taper=.2, wmin=.7, seed=7300 + j))
    o.append(an)
    # облако над головой
    if cl > .01:
        cs = back_out(cl, 1.5)
        cxh, cyh = hp[0] + 20, hp[1] - 240
        o.append(props.anx_cloud(cxh, cyh, 2.4 * cs, 1, t, seed=3))
        o.append(props.anx_cloud(cxh - 150, cyh + 60, 1.3 * clamp(cl * 1.3 - .2), 0, t + .3, seed=5))
        o.append(props.anx_cloud(cxh + 160, cyh + 70, 1.1 * clamp(cl * 1.3 - .3), 0, t + .6, seed=7))
    shx, shy = 3.5 * math.sin(t * 83) * sh, 3 * math.sin(t * 71) * sh
    cam = (lerp(520, 560, u) + shx, lerp(1050, 990, u) + shy, 1.22 + .16 * ease_io(u), -.6 + 1.0 * u)
    return cam_group("".join(o), cam)


# ═════════════════════════ s13 ═════════════════════════
def pose_blend(t, u, *, expr, n_t, f_t, hands, ha=0.0, head_off=(0, 0), seatx=250):
    """Дима между стоя (u=0) и сидя (u=1) на стуле: бёдра опускаются, стопы уезжают вперёд."""
    hy = lerp(1112, 1262, u)
    lean = lerp(.04, .1, u)
    fn = ((seatx + lerp(18, 215, u), 1468), 0.0)
    ff = ((seatx + lerp(-22, 190, u), 1463), 0.0)
    shx = seatx + 240 * math.sin(lean) + 6
    sn = -1 if n_t[0] >= shx else 1
    sf = -1 if f_t[0] >= shx else 1
    p = dict(hip=(seatx, hy), scale=S.BS, lean=lean, torso_k=1.0, feet={"n": fn, "f": ff}, arms={"n": ("ik", n_t, sn), "f": ("ik", f_t, sf)}, hands=hands,
             expr=expr, head_ang=ha, head_off=head_off, hood=0.0, strings=(0, 0))
    d = people.draw(p, "dima")
    d["x"], d["sx"] = seatx, 1.0
    return d


def sheet_flat(x, y, w=150, h=52, fill=0.0, seed=0):
    """Листок лежит на столе (вид сверху-сбоку): параллелограмм со штрихами строк."""
    pts = [(x - w / 2 + 8, y - h / 2, 1), (x + w / 2, y - h / 2, 1), (x + w / 2 - 8, y + h / 2, 1), (x - w / 2, y + h / 2, 1)]
    inner = ""
    for j in range(5):
        if j / 5 >= fill:
            break
        yy = y - h / 2 + 10 + j * 8
        inner += line([(x - w / 2 + 22 - j, yy), (x + w / 2 - 22 - (j % 3) * 14, yy + .6)], 2.6, "#2a2d30", taper=.15, wmin=.7, seed=7400 + seed * 9 + j)
    return shape(pts, props.C_PAPER, inner, w=3.2, seed=7410 + seed)


def frame13(t):
    T_S = 27.3                      # листок вынут
    pu = smooth(28.0, 28.85, t)     # присел
    st_ = kf(t, [(26.4, 0.0), (28.0, 0.0), (28.9, 1.0)])[0]
    u = clamp((t - 26.4) / 2.7)
    pack = (468, 1124, .78)
    mouth = (pack[0] + 6, pack[1] - 150 * pack[2])
    # руки: ближняя тянется в рюкзак, достаёт листок (26.9–27.5), потом ручку (27.6–28.0)
    rea = smooth(26.5, 27.0, t)
    pull = smooth(27.0, 27.55, t)
    n_pos = (lerp(380, mouth[0] + 10, rea), lerp(1000, mouth[1] + 6, rea))
    pen_take = smooth(27.6, 28.0, t)
    desk_y = 1128
    # листок: вынут → кладётся на стол
    put = smooth(28.0, 28.5, t)
    # цели рук по фазам
    if t < 27.55:
        wr = (n_pos[0] + 4 * pull, n_pos[1] - 80 * pull)
    elif t < 28.0:
        wr = (lerp(mouth[0] + 14, mouth[0] - 6, pen_take), lerp(mouth[1] - 74, mouth[1] + 4, ease_in(clamp((t - 27.55) / .2))) - 28 * pen_take * (t > 27.8))
    else:
        wr = (lerp(mouth[0] - 6, 640, put), lerp(mouth[1] - 20, 1080, put))
    if t >= 28.0:
        wr = (lerp(468, 640, put), lerp(1000, 1090, put))
    f_pos = (lerp(420, 560, smooth(27.6, 28.6, t)), lerp(1020, 1118, smooth(27.6, 28.6, t)))
    conf = smooth(28.3, 28.9, t)
    ex = expr_of(lid=.88, look=(.8, .25), brows="calm" if t < 28.4 else "up", mouth="smile", smile=.15 + .5 * conf, blush=.25 * conf)
    hands = {"n": dict(hand_spec(.62, (-.3, -1), .45, k=.95), flip=-1), "f": hand_spec(.35, (1, .3), .25)}
    d = pose_blend(t, st_, expr=ex, n_t=wr, f_t=f_pos, hands=hands, ha=.03 * conf)
    lg, af, bd, an = S.dima_layers(d)
    w_n = S.wrist_w(d, "n", 0)
    o = [_ST["room_day"], ROOM.chair(250, 1266, 1, 2300), _ST["desk_legs"], lg, af, bd, _ST["desk_top"]]
    # рюкзак на столе, раскрытый
    o.append(ROOM.backpack(pack[0], pack[1], pack[2], open_=1.0, zip_u=0.0))
    # листок: выходит из рюкзака на wr
    sheet = ""
    if t < 28.0:
        if t >= 27.0:
            sc = 2.2
            sy = lerp(mouth[1] + 20, w_n[1] - 52, pull) if pull < 1 else w_n[1] - 52
            clipy = pack[1] - 150 * pack[2]
            sheet = props.paper_sheet(w_n[0] + 8, sy, sc, 0.0, rot=-4 + 2 * math.sin(t * 6), seed=4)
            if pull < .95 and False:
                pass
    else:
        sheet = sheet_flat(640, 1136, 180, 56, 0.0)
    if sheet:
        o.append(sheet)
    # ручка: берётся в ближнюю руку
    pen_on = t >= 27.62
    if pen_on:
        if t < 28.0:
            px, py = w_n[0] + 18, w_n[1] - 34
            o.append(props.pen(px + 12, py + 36, 2.0, rot=26))
        else:
            o.append(props.pen(w_n[0] + 16, w_n[1] - 4, 2.0, rot=34 - 8 * put))
    o.append(an)
    # кот на подоконнике
    cst = dict(look=(-.9, .25), turn=-.8, blink=D.Cat_blink(t, [(27.5, .2, .3), (28.6, .2, .3)]), tail=6 * D.osc(t, .45) + 2 * D.osc(t, 1.3), ear=3 * D.bump(t, 27.2, .4),
               tilt=-2 * smooth(27.6, 28.4, t), smile=0)
    cat_svg = Cat.draw(930, 820, .56, cst, t)
    o.insert(1, f'<g>{cat_svg}</g>')
    cam = (lerp(560, 560, u), lerp(1020, 1090, ease_io(u)), 1.12 + .7 * ease_in(u, 2.2), -1.0 * (1 - u) + .3 * u)
    out = cam_group("".join(o), cam)
    return whip(out, t, 26.61, 260)


# ═════════════════════════ s15 ═════════════════════════
def frame15(t):
    T_P, T_H = T[74], T[75]          # «карман» 32.22, «голова» 32.80
    u = clamp((t - 31.4) / 2.5)
    fold1 = smooth(31.62, 32.0, t)
    fold2 = smooth(31.95, 32.2, t)
    ins = smooth(T_P - .05, T_P + .3, t)
    bright = smooth(T_H - .05, T_H + .5, t)
    x0 = 480
    ex = expr_of(lid=.8 + .1 * bright, look=(.6, .35 * (1 - bright)), brows=("worry", "calm", bright), mouth="smile" if bright > .3 else "flat", smile=.7 * bright, blush=.4 * bright)
    pocket_in = (x0 + 52, 1052)
    sheet_c = (x0 + 150, 940)
    # ближняя рука: держит сложенный листок у груди, потом ведёт в карман
    k1 = smooth(T_P - .15, T_P + .12, t)
    wr = (lerp(sheet_c[0] + 28, pocket_in[0] + 16, k1), lerp(sheet_c[1] + 30, pocket_in[1] - 6, k1))
    wr = (wr[0] + 2.5 * math.sin(t * 40) * (1 - k1), wr[1])
    out_down = smooth(T_P + .3, T_P + .8, t)
    wr = (lerp(wr[0], x0 + 120, out_down), lerp(wr[1], 1090, out_down))
    f_t = (sheet_c[0] - 26, sheet_c[1] + 34 + 40 * out_down)
    lean = lerp(.05, .018, bright)
    hands = {"n": dict(hand_spec(.6, (-.3, -1), .5, k=.95), flip=-1), "f": dict(hand_spec(.5, (.4, -1), .4, k=.95), flip=1)}
    if out_down > .1:
        hands = {"n": hand_spec(.3, (.5, 1), .2), "f": hand_spec(.3, (.5, 1), .2)}
    d = S.stand(t, x0, lean=lean, ha=.05 * (1 - bright) - .02 * bright, expr=ex, n_t=wr, f_t=f_t, hands=hands, sn=-1, sf=-1, hip_dy=-40 * 0 + 6 * bright,
                head_off=(0, 4 * bright))
    d_lg, d_af, d_bd, d_an = S.dima_layers(d)
    hp = S.head_w(d)
    o = [_ST["room_day"], ROOM.chair(150, 1266, 1, 2300), d_lg, d_af]
    o.append(d_bd)
    # листок сложен вдвое ×2, едет к карману; вход скрыт срезом по верхнему краю кармана
    if t < T_P + .5:
        wnx = S.wrist_w(d, "n", 0)
        cxs, cys = wnx[0] + 6, wnx[1] - 40 * (1 - k1) - 10 * k1 - 24 * ins * 0
        slide = ins * 78
        shy = cys + slide
        sh = props.paper_sheet(cxs, shy, 2.2, 1.0, rot=-3 + 4 * ins, seed=6)
        # складывание: уменьшаем по высоте
        sy = lerp(1.0, .5, fold1) * lerp(1.0, .6, fold2)
        sh = f'<g transform="translate({f(cxs)} {f(shy)}) scale(1 {sy:.3f}) translate({f(-cxs)} {f(-shy)})">{sh}</g>'
        cut_y = 1038 - 10
        cid = lib.uid()
        lib.DEFS.append(f'<clipPath id="{cid}"><rect x="-1000" y="-2000" width="4000" height="{f(2000 + cut_y)}"/></clipPath>')
        o.append(f'<g clip-path="url(#{cid})">{sh}</g>' if ins > .02 else sh)
    o.append(d_an)
    # облачка уходят над головой на «голова»
    for j, (dx, dy, sc) in enumerate(((-30, -240, 1.7), (60, -300, 1.3), (-110, -300, 1.0))):
        v = clamp((t - T_H - .06 * j) / .75)
        vis = 1 - v
        if t < T_H - .55:
            continue
        pre = smooth(T_H - .55, T_H - .15, t)
        if pre <= 0 or v >= 1:
            continue
        rise = ease_in(v, 1.6) * 260
        o.append(props.anx_cloud(hp[0] + dx + 26 * math.sin(v * 4 + j), hp[1] + dy - rise, sc * (1.0 + 0.2) * (1 - ease_in(v, 2.0)) * pre + .001, j % 2, t + j, seed=j))
    cam = (lerp(600, 560, u), lerp(1080, 1030, u), 1.52 - .26 * ease_out(clamp((t - 31.56) / .8)) + .1 * ease_io(clamp((t - 32.3) / 1.4)), -.6 + 1.0 * u)
    return cam_group("".join(o), cam)


# ═════════════════════════ s18 ═════════════════════════
def frame18(t):
    T_T = T[89]                       # «трясутся» 38.85
    u = clamp((t - 38.3) / 2.5)
    z = lerp(1.62, 1.32, ease_io(u))
    cx, cy = lerp(450, 505, ease_io(u)), lerp(1130, 1085, ease_io(u))
    env = 0.0
    if t >= T_T:
        dt = t - T_T
        env = smooth(0, .06, dt) * math.exp(-dt / .38)
    shake = .95 * env
    ex = expr_of(lid=.78, look=(.85, .02), brows="calm", mouth="smile", smile=.22 + .12 * smooth(39.3, 40.2, t) - .2 * env, blush=.3)
    d, bk, (bx, by) = hold_book(t, 330, 1108 + 1.2 * math.sin(t * 1.5), lean=.04, ha=.02, expr=ex, shake=shake, calm=1.0, seed=2.0)
    hp = S.head_w(d)
    o = [corridor_world(t)]
    lg, af, bd, an = S.dima_layers(d)
    # кот рядом, сидит спокойно, смотрит на зрителя
    cst = dict(look=(.1, .05), turn=-.05, blink=D.Cat_blink(t, [(39.4, .2, .3)]), tail=5 * D.osc(t, .4) + 2 * D.osc(t, 1.1), ear=2 * D.bump(t, 38.9, .4), smile=1 if t > 39.5 else 0,
               tilt=2 * math.sin(t * .7))
    o.append(f'<g>{blob(ellipse_pts(560 + 12, 1452 + 4, 150 * .62 * 1.25, 12, 16), "#2a1408", .22)}{Cat.draw(560, 1452, .62, cst, t)}</g>')
    o += [lg, af, bk, bd, an]
    if env > .08:
        o.append(tremor_marks(bx + 8, by + 40, t, .8 * env, 2))
    cam_ = (cx, cy, z, (-.6) * (1 - u))
    return whip(cam_group("".join(o), cam_), t, 38.5, 260)


# ═════════════════════════ диспетчер ═════════════════════════
def frame(sid, t):
    if not _ST.get("init"):
        D.DAY[0] = True
        _ST["corr"] = corridor_static()
        _ST["hall"] = hall_static()
        _ST["room_day"] = D.room_static()
        _ST["desk_legs"], _ST["desk_top"] = D.desk_static()
        lib.static_done()
        _ST["init"] = True
    lib.dyn_begin()
    body = FRAMES[sid](t)
    return svg(f'<rect width="1920" height="1920" fill="#d9e3da"/>{body}')


FRAMES = {"s01": frame01, "s03": frame03, "s06": frame06, "s13": frame13, "s15": frame15, "s18": frame18}
