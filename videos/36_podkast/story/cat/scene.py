"""Сцена cat рилса 36 «не идёт в спортзал»: планы s05 s16 s17 s18. frame(sid, t) -> SVG 1080×1920
(t — общее время ролика, удары на словах по voice/words.json).

Кот — cat.py рилса 34 (ЛЕВОЕ от зрителя ухо загнуто, зелёные глаза, по 2 оранжевые полоски на щеках, огонёк на
кончике хвоста-завитка), стоящий кот — cat2.py рилса 35. Прихожая — ../home/hall.py (общая с планами Димы).
s05 — кот крупно на подлокотнике дивана в вечерней комнате, наклон головы на «почему» (6.96);
s16 — кот сидит у входной двери рядом со спортивной сумкой; на «кот» (28.40) поворачивает голову к двери, на «двери»
(29.44) дверь открывается, кот встаёт навстречу на задние лапы, огонёк вспыхивает;
s17 — крупно кот в прихожей (фон размыт), подмигивает на «Напиши» (30.12) и кивает на «кот» (30.64);
s18 — полочка у двери: старый абонемент в пыли прислонён к стене, кот рядом смахивает лапой пыль на «пылится» (32.48)
— облачко пыли, карта блестит, кот смотрит в камеру; медленный отъезд. Клип до 33.6 с."""
import importlib.util
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat  # noqa: E402
import cat2  # noqa: E402
import lib  # noqa: E402
from lib import INK, T, blob, clamp, ease_io, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape, smooth, spring  # noqa: E402

_spec = importlib.util.spec_from_file_location("hall36", os.path.join(os.path.dirname(HERE), "home", "hall.py"))
HL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(HL)

WHY = 6.96
KOT16, DOOR16 = 28.40, 29.44
WRITE, KOT17 = 30.12, 30.64
DUST = 32.48
_C = {}


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.18):
    u = (t - tb) / dur
    return min(1.0, 1.3 * math.sin(math.pi * u)) if 0 < u < 1 else 0.0


def flick_at(t, c, amp=-14):
    e = t - c
    return amp * math.exp(-e * 9) * math.sin(e * 34) if 0 <= e < 0.55 else 0.0


def cat_svg(x, y, s, t, **d):
    keep = lib.INK_K[0]
    lib.INK_K[0] = 1.0
    out = cat.draw(x, y, s, t, **d)
    lib.INK_K[0] = keep
    return out


def cat2_svg(x, y, s, t, **d):
    keep = lib.INK_K[0]
    lib.INK_K[0] = 1.0
    out = cat2.draw(x, y, s, t, **d)
    lib.INK_K[0] = keep
    return out


def flame_glow(x, y, s, tail, t, k=1.0, r=260, up=0.0):
    fx, fy = cat.flame_world(x, y, s, tail)
    fy -= 62 * up * s
    fl = (0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)) * k
    g = rad_grad([(0, "#ffb050", min(.9, .38 * fl)), (1, "#ffb050", 0)], fx, fy, r, r)
    return f'<rect x="{f(fx - r - 20)}" y="{f(fy - r - 20)}" width="{f(2 * r + 40)}" height="{f(2 * r + 40)}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def svg_cam(world, camv, bg="#2a2030", screen="", vig=0.28):
    cx, cy, s, r = camv
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, r)}">{world}</g>{HL.vignette(vig)}{screen}')


def sparkle(x, y, r, a=0.0, col="#fff6c8", op=1.0):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * .28
        ang = a + k * math.pi / 4
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    return blob(pts, col, op)


# ═════════════════════════════ s05: кот на подлокотнике дивана
SOFA, SOFA_SH, SOFA_HI, SOFA_DK = "#c46a48", "#9e4f34", "#d9845f", "#7c3a26"     # как диван комнаты (home/room.py)
PLAID, PLAID_SH = "#c9584a", "#a8453a"


def room05(t):
    """Вечерняя комната за диваном (будет размыта): тёплая стена, торшер, картина, тёмное окно."""
    o = [f'<rect x="-2000" y="-2400" width="5000" height="4000" fill="#9db8b8"/>']
    o.append(blob(rect_pts(-2000, 260, 3000, 1600), "#a9744a"))
    # окно-ночь слева
    o.append(shape(rect_pts(-560, -820, -200, -300, 8), "#f3e8d4", blob(rect_pts(-536, -796, -224, -324), "#26315e") +
                   blob(ellipse_pts(-300, -700, 22, 22, 12), "#f3ead0") + blob(rect_pts(-536, -470, -224, -324), "#151b38") +
                   blob(rect_pts(-390, -796, -370, -324), "#f3e8d4"), w=5, seed=7001))
    # торшер справа: тёплое пятно
    o.append(shape(rect_pts(430, -560, 450, 260), "#4f2c18", "", w=3, seed=7002))
    o.append(shape([(340, -560), (540, -560), (490, -740), (390, -740)], "#f2d38a", blob([(470, -740), (490, -740), (540, -560), (500, -560)],
                   "#d9b064", .9), w=4.4, seed=7003))
    g = rad_grad([(0, "#ffd58a", .75), (1, "#ffd58a", 0)], 440, -620, 700, 700)
    o.append(f'<rect x="-200" y="-1600" width="1600" height="1600" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    # картина
    o.append(shape(rect_pts(30, -760, 300, -560), HL.WOOD_DK, blob(rect_pts(48, -742, 282, -578), "#d9c9a0") +
                   blob([(48, -578), (120, -690), (170, -640), (220, -710), (282, -578)], "#7aa07a"), w=4, seed=7004))
    return "".join(o)


def sofa05():
    """Подлокотник крупно (на нём сидит кот, верх y = 0) и край сиденья с пледом справа."""
    o = []
    # спинка за сиденьем справа
    o.append(shape([(230, -420), (1400, -440), (1400, 300), (230, 300)], SOFA_SH, blob(rect_pts(230, -420, 1400, -380), SOFA_DK, .6), w=5, seed=7010))
    # сиденье и плед
    o.append(shape([(220, 60), (1400, 60), (1400, 700), (220, 700)], SOFA, blob(rect_pts(220, 60, 1400, 110), SOFA_HI, .7), w=5, seed=7011))
    pl = [(330, 40), (760, 20), (900, 70), (980, 700), (420, 700), (380, 300)]
    pin = blob([(330, 40), (760, 20), (780, 80), (360, 110)], PLAID_SH, .6)
    for k in range(5):
        pin += line([(360 + k * 110, 30), (420 + k * 120, 700)], 10, "#e9d8c0", taper=.05, wmin=.9, seed=7020 + k, op=.8)
    for k in range(4):
        pin += line([(330, 160 + k * 140), (980, 140 + k * 150)], 8, "#e9d8c0", taper=.05, wmin=.9, seed=7030 + k, op=.7)
    o.append(shape(pl, PLAID, pin, w=5, seed=7012))
    # подлокотник: валик сверху, фасад вниз
    arm_front = [(-460, 40), (300, 40), (310, 900), (-470, 900)]
    o.append(shape(arm_front, SOFA, blob([(140, 40), (300, 40), (310, 900), (160, 900)], SOFA_SH, .85) +
                   line([(-300, 200), (-290, 880)], 4, SOFA_DK, seed=7041, op=.5), w=5.2, seed=7040))
    roll = [(-490, 40), (-470, -40), (-380, -78), (0, -86), (280, -76), (330, -30), (320, 50), (200, 76), (-300, 80), (-470, 72)]
    o.append(shape(roll, SOFA_HI, blob([(-490, 20), (330, 0), (320, 50), (200, 76), (-300, 80), (-470, 72)], SOFA, .9) +
                   line([(-400, -40), (-100, -56), (220, -50)], 3, "#ecab88", seed=7043, op=.8), w=5.2, seed=7042))
    # шов-кант по краю валика
    o.append(line([(-470, 60), (-300, 70), (200, 64), (316, 36)], 3, SOFA_DK, seed=7044, op=.7))
    return "".join(o)


def frame05(t):
    sc0 = 2.4
    u = clamp((t - 6.25) / 1.5)
    sc = sc0 + 0.18 * (0.35 * u + 0.65 * ease_io(u))
    e = t - WHY
    if e > 0:
        sc *= 1 + 0.03 * math.exp(-e * 7) * math.sin(min(e * 12, math.pi))
    x, y, s = 0.0, -84.0, 0.95
    cx, cy = 30 + 10 * u, -180 - 14 * u
    rot = -0.8 + 1.1 * u
    if "bg05" not in _C:
        set_ink(1.6)
        _C["bg05"] = f'<g {lib.blur(9)}>{room05(t)}</g>'
        set_ink(sc0)
        _C["sofa05"] = sofa05()
        lib.static_done()
    lib.dyn_begin()
    tilt = 1.5 * math.sin(t * 1.7)
    if e > -0.12:
        pre = 2.5 * math.sin(math.pi * clamp((e + 0.12) / 0.12)) if e < 0 else 0.0
        tilt += pre - 13 * spring(max(e, 0), 2.2, 4.5)
    blink = max(blink_at(t, 6.42), blink_at(t, 7.42))
    look = (0.12 * math.sin(t * 0.9), -0.1 + 0.08 * math.sin(t * 1.3))
    if e > 0:
        look = (look[0] - 0.25 * smooth(0, 0.2, e), look[1] - 0.15 * smooth(0, 0.2, e))
    flick = flick_at(t, WHY + 0.04) + flick_at(t, 6.5, -10)
    tail = 7 * math.sin(t * 2.1) + 3 * math.sin(t * 3.7 + 1)
    if e > 0:
        tail += 9 * math.exp(-e * 3) * math.sin(e * 12)
    fk = 1.3 + (0.35 * math.exp(-e * 4) * math.sin(min(e * 8, math.pi)) if e > 0 else 0.0)
    hop = -9 * math.sin(math.pi * clamp(e / 0.22)) if 0 < e < 0.22 else 0.0
    w = [_C["bg05"], _C["sofa05"]]
    w.append(blob(ellipse_pts(x + 26, y + 4, 140, 12, 16), "#1d2236", .35, lib.blur(5)))
    w.append(flame_glow(x, y + hop, s, tail, t, 1 + (0.6 * math.exp(-e * 3) if e > 0 else 0), 220))
    w.append(cat_svg(x, y + hop, s, t, shadow=False, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, flame_k=fk))
    return svg_cam("".join(w), (cx, cy, sc, rot), bg="#9db8b8")


# ═════════════════════════════ спортивная сумка
BAG, BAG_SH, BAG_HI, BAG_OR = "#23315a", "#18223f", "#34477a", "#f08a2c"


def sports_bag(x, y, k=1.0, seed=7100):
    """Тёмно-синяя спортивная сумка-бочонок на полу (низ — y), оранжевая полоса, ручки и ремень."""
    w, h = 250 * k, 120 * k
    o = [blob(ellipse_pts(x, y + 2, w * .55, 12 * k, 14), "#1a0e05", .3, lib.blur(5))]
    body = [(x - w / 2, y - 12 * k), (x - w / 2 + 6 * k, y - h * .7), (x - w / 2 + 34 * k, y - h), (x + w / 2 - 34 * k, y - h),
            (x + w / 2 - 6 * k, y - h * .7), (x + w / 2, y - 12 * k), (x + w / 2 - 14 * k, y, 1), (x - w / 2 + 14 * k, y, 1)]
    inner = blob([(x - w, y - h * .38), (x + w, y - h * .38), (x + w, y + 10), (x - w, y + 10)], BAG_SH, .85)
    inner += blob([(x - w / 2, y - h * .62), (x + w / 2, y - h * .62), (x + w / 2, y - h * .5), (x - w / 2, y - h * .5)], BAG_OR)
    inner += blob([(x - w / 2 + 30 * k, y - h * .96), (x + w * .1, y - h * .96), (x, y - h * .84), (x - w / 2 + 30 * k, y - h * .84)], BAG_HI, .8)
    inner += line([(x - w / 2 + 36 * k, y - h * .88), (x + w / 2 - 36 * k, y - h * .88)], 2.4, "#9aa6c4", seed=seed + 1, op=.9)
    o.append(shape(body, BAG, inner, w=4.4, seed=seed))
    for sx in (-1, 1):
        o.append(shape(ellipse_pts(x + sx * (w / 2 - 6 * k), y - h * .48, 12 * k, h * .44, 12), BAG_SH,
                       blob(ellipse_pts(x + sx * (w / 2 - 6 * k), y - h * .48, 6 * k, h * .3, 10), BAG_OR), w=3.4, seed=seed + 3 + sx))
    for sx in (-1, 1):
        o.append(line([(x + sx * 46 * k, y - h * .96), (x + sx * 30 * k, y - h * 1.3), (x - sx * 4 * k, y - h * 1.36),
                       (x - sx * 26 * k, y - h * 1.28)], 9 * k, BAG_SH, taper=.05, wmin=.9, seed=seed + 6 + sx))
    o.append(line([(x - w / 2 + 10 * k, y - h * .7), (x - w * .2, y - h * .1), (x + w * .2, y - h * .05), (x + w / 2 - 10 * k, y - h * .7)],
                  8 * k, "#1b1b22", taper=.05, wmin=.9, seed=seed + 9))
    return "".join(o)


# ═════════════════════════════ s16: кот ждёт у двери
S16 = dict(x=150.0, y=0.0, s=0.62)


def frame16(t):
    u = clamp((t - 27.95) / 2.25)
    sc = 2.0 + 0.05 * ease_io(u)
    cx = 222 + 40 * (0.3 * u + 0.7 * ease_io(u))
    cy = -150 - 6 * u
    rot = 0.6 - 1.0 * u
    e = t - DOOR16
    if e > 0:
        sc *= 1 + 0.025 * math.exp(-e * 7) * math.sin(min(e * 12, math.pi))
    lib.dyn_begin()
    set_ink(sc)
    th = 0.62 * (1 - math.exp(-max(0, e + 0.06) * 6)) if e > -0.06 else 0.0
    w = [HL.back(t, door_open=th, rain=0.0, phone=True)]
    if th > 0.02:
        # свет с площадки на пол прихожей
        x0, y0, x1, y1 = HL.DOOR
        w.append(blob([(x0 + 20, 4), (x1 - 40, 4), (x1 + 40, 120), (x0 - 60, 120)], "#fff1c8", .22 * min(1, th * 2), lib.blur(10)))
    x, y, s = S16["x"], S16["y"], S16["s"]
    w.append(sports_bag(20, 0, 0.72))
    ek = t - KOT16
    turn = smooth(KOT16 - 0.06, KOT16 + 0.16, t)
    up = 0.62 * smooth(DOOR16 + 0.02, DOOR16 + 0.3, t)
    look = (0.15 * math.sin(t * .9) * (1 - turn) + 0.85 * turn, -0.05 - 0.2 * turn + 0.1 * up)
    tilt = 1.4 * math.sin(t * 1.3) + 9 * turn * (1 - 0.4 * up)
    if ek > 0:
        tilt += 4 * math.exp(-ek * 6) * math.sin(ek * 18)
    blink = max(blink_at(t, 28.1), blink_at(t, 29.05))
    flick = flick_at(t, KOT16 + 0.04, -12) + flick_at(t, DOOR16 + 0.02, -14)
    tail = 6 * math.sin(t * 2.0) + 3 * math.sin(t * 3.4 + 1) + (10 * math.exp(-e * 3) * math.sin(e * 13) if e > 0 else 0)
    fk = 1.3 + (0.7 * math.exp(-e * 2.2) * min(1, e * 10) if e > 0 else 0.0)
    w.append(flame_glow(x, y, s, tail, t, 1 + (1.0 * math.exp(-e * 2.2) if e > 0 else 0), 230, up))
    pl = (811 + 20 * up, 1298 - 120 * up) if up > 0.02 else None
    pr = (861 - 4 * up, 1298 - 130 * up) if up > 0.02 else None
    w.append(cat2_svg(x, y, s, t, up=up, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw_l=pl, paw_r=pr))
    w.append(HL.front(t))
    # вспышка огонька
    if e > 0:
        fx, fy = cat.flame_world(x, y, s, tail)
        fy -= 62 * up * s
        a = math.exp(-e * 3) * min(1, e * 8)
        for k in range(6):
            ang = -math.pi * 0.6 + k * math.pi / 5 + e * 0.8
            r = 40 + 70 * (1 - math.exp(-e * 4))
            w.append(sparkle(fx + r * math.cos(ang), fy - 20 + r * math.sin(ang), 12, e * 3, "#ffd36a", a))
    # «вспышка» огонька — пламя крупнее (сам cat2 рисует огонёк через cat.flame с k=1.3, добавим поверх ещё одно)
    return svg_cam("".join(w), (cx, cy, sc, rot))


# ═════════════════════════════ s17: кот крупно в прихожей, подмигивает и кивает
S17 = dict(x=150.0, y=0.0, s=0.62)


def frame17(t):
    x, y, s = S17["x"], S17["y"], S17["s"]
    u = clamp((t - 29.8) / 2.35)
    hc = cat.to_world((836, 1080), x, y, s)
    sc0 = 5.0
    sc = sc0 + 0.32 * (0.4 * u + 0.6 * ease_io(u))
    cx = hc[0] + 36 - 8 * u
    cy = hc[1] + 50 - 8 * u
    rot = -0.8 + 1.4 * u
    ek = t - KOT17
    if ek > 0:
        sc *= 1 + 0.02 * math.exp(-ek * 7) * math.sin(min(ek * 12, math.pi))
    if "bg17" not in _C:
        set_ink(2.0)
        bg = HL.back(30.0, 0.0, 0.0, True) + sports_bag(20, 0, 0.72)
        _C["bg17"] = f'<g {lib.blur(4)}>{bg}</g>'
        lib.static_done()
    lib.dyn_begin()
    wk = smooth(WRITE + 0.04, WRITE + 0.16, t) * (1 - smooth(30.82, 30.96, t))
    bb = max(blink_at(t, 29.9, .16), blink_at(t, 31.62, .18))
    blink = (bb, max(bb, wk))
    tilt = -6 * smooth(WRITE - 0.06, WRITE + 0.14, t) * (1 - smooth(31.1, 31.5, t)) + 1.2 * math.sin(t * 1.3)
    nod = 18 * math.sin(math.pi * clamp((t - KOT17 + 0.04) / 0.34)) + 6 * math.sin(math.pi * clamp((t - KOT17 - 0.3) / 0.28))
    flick = flick_at(t, 29.86, -10) + flick_at(t, KOT17 + 0.05, -9)
    tail = 6 * math.sin(t * 2.4) - 2 + 4 * math.sin(t * 3.1 + 1)
    look = (0.05 * math.sin(t * .8), -0.08)
    w = [_C["bg17"], flame_glow(x, y, s, tail, t, 1.2, 160)]
    w.append(cat_svg(x, y, s, t, shadow=True, look=look, blink=blink, tilt=tilt, nod=nod, flick=flick, tail=tail,
                     flame_k=1.3 + 0.08 * math.sin(t * 5)))
    return svg_cam("".join(w), (cx, cy, sc, rot))


# ═════════════════════════════ s18: полочка, абонемент в пыли, кот смахивает пыль
SHX0, SHY, SHX1 = -230.0, HL.SHELF[1], HL.SHELF[2]
CARD = (-62.0, SHY, 0.95)          # низ карты (стоит на полке, прислонена к стене), масштаб
S18 = dict(x=10.0, y=SHY, s=0.42)


def shelf_long():
    """Полочка длиннее (до вешалки): доска поверх полки прихожей, кронштейн слева."""
    o = []
    bx = SHX0 + 40
    o.append(shape([(bx - 6, SHY), (bx + 6, SHY), (bx + 6, SHY + 50), (bx - 6, SHY + 14)], HL.WOOD_SH, w=2.6, seed=7300))
    o.append(shape(HL.R(SHX0, SHY, SHX1, SHY + 20), HL.WOOD_HI, blob([(SHX0, SHY + 10), (SHX1, SHY + 10), (SHX1, SHY + 20), (SHX0, SHY + 20)],
                   HL.WOOD_SH, .9), w=3.4, seed=7301))
    return o and "".join(o)


def card_svg(cx, by, k, dust, wipe_x, t, shine=0.0):
    """Бирюзовая карта-абонемент с белой гантелью (без букв), стоит на полке, прислонена к стене (наклон −8°).
    dust 0..1 — слой пыли; пыль убрана правее wipe_x (мир); shine — блеск после."""
    w, h = 96 * k, 62 * k
    rot = -8
    o = []
    o.append(blob(T(rect_pts(-w / 2 + 6, -h + 6, w / 2 + 8, 4, 8 * k), cx, by), "#000000", .18, lib.blur(3)))
    inner = blob(rect_pts(-w / 2, h * .1 - h, w / 2, -h), "#5fd0c4", .5)
    inner += blob(rect_pts(-w / 2, -h * .25, w / 2, 0), "#1f8f86", .5)
    # гантель
    gx, gy = 0, -h / 2
    inner += blob(rect_pts(gx - 22 * k, gy - 3.5 * k, gx + 22 * k, gy + 3.5 * k, 2), "#ffffff")
    for sx in (-1, 1):
        inner += blob(rect_pts(gx + sx * 22 * k - 6 * k, gy - 12 * k, gx + sx * 22 * k + 6 * k, gy + 12 * k, 3 * k), "#ffffff")
        inner += blob(rect_pts(gx + sx * 31 * k - 3.5 * k, gy - 8 * k, gx + sx * 31 * k + 3.5 * k, gy + 8 * k, 2 * k), "#ffffff")
    if shine > 0:
        sx_ = -w / 2 + (w + 60) * shine
        inner += blob([(sx_ - 18, -h - 4), (sx_ + 4, -h - 4), (sx_ - 22, 4), (sx_ - 44, 4)], "#ffffff", .55 * math.sin(math.pi * shine))
    if dust > 0:
        dl = blob(rect_pts(-w / 2 - 4, -h - 4, w / 2 + 4, 4), "#a49c8c", .82)
        rs = np.random.RandomState(5)
        for _ in range(60):
            x_, y_ = rs.uniform(-w / 2, w / 2), rs.uniform(-h, 0)
            dl += f'<circle cx="{x_:.1f}" cy="{y_:.1f}" r="{rs.uniform(.8, 2.2):.1f}" fill="#7d7566" opacity=".7"/>'
        for _ in range(8):
            x_, y_ = rs.uniform(-w / 2, w / 2), rs.uniform(-h, 0)
            dl += line([(x_, y_), (x_ + rs.uniform(-8, 8), y_ + rs.uniform(-6, 6))], 1.2, "#6f685b", seed=int(x_ * 10) % 999, op=.7)
        # пыль остаётся левее wipe_x (в системе карты, с поправкой на наклон грубо)
        cw = lib.clip_rect(-w, -h - 40, wipe_x - cx + w, h + 80)
        o_d = f'<g clip-path="url(#{cw})" opacity="{dust:.3f}">{dl}</g>'
        inner += o_d
    body = rect_pts(-w / 2, -h, w / 2, 0, 8 * k)
    o.append(shape(body, "#2fb3a8", inner, w=3.6, seed=7310))
    if dust > 0.05:
        # паутинка в углу
        o.append(line([(-w / 2 - 2, -h * .5), (-w / 2 + 14, -h - 2)], 1.2, "#efece4", seed=7311, op=.8 * dust))
        o.append(line([(-w / 2 + 2, -h * .7), (-w / 2 + 6, -h * .78), (-w / 2 + 10, -h * .9)], 1.0, "#efece4", seed=7312, op=.8 * dust))
    return f'<g transform="translate({cx:.2f} {by:.2f}) rotate({rot})">{"".join(o)}</g>'


def dust_cloud(x, y, u, seed=7400):
    if u <= 0 or u >= 1:
        return ""
    rs = np.random.RandomState(seed)
    o = []
    for i in range(9):
        a = rs.uniform(-2.6, -0.4)
        sp = rs.uniform(40, 120)
        r = rs.uniform(14, 26) * (0.6 + 1.2 * u)
        px = x + math.cos(a) * sp * u - 50 * u
        py = y + math.sin(a) * sp * u * .8
        o.append(blob(ellipse_pts(px, py, r, r * .85, 12), "#c9bfae", .75 * (1 - u) ** 1.2))
    for i in range(10):
        a = rs.uniform(-3.0, -0.2)
        sp = rs.uniform(60, 170)
        px, py = x + math.cos(a) * sp * u - 40 * u, y + math.sin(a) * sp * u + 40 * u * u
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="#8f8676" opacity="{(1 - u):.3f}"/>')
    return "".join(o)


def frame18(t):
    x, y, s = S18["x"], S18["y"], S18["s"]
    ccx, cby, ck = CARD
    u = clamp((t - 31.75) / 1.85)
    sc0 = 4.1
    sc = sc0 - 0.7 * (0.25 * u + 0.75 * ease_io(u))
    cx = -34 + 10 * u
    cy = SHY - 64 + 6 * u
    rot = 0.8 - 1.2 * u
    e = t - DUST
    if e > 0:
        sc *= 1 + 0.02 * math.exp(-e * 8) * math.sin(min(e * 12, math.pi))
    lib.dyn_begin()
    set_ink(sc)
    w = [HL.back(31.8, 0.0, 0.0, False), shelf_long()]
    # лапа: поднимается к правому краю карты и смахивает влево на «пылится»
    rest = cat.PAW_REST
    a = smooth(DUST - 0.42, DUST - 0.16, t)
    b = smooth(DUST - 0.16, DUST + 0.12, t)
    back = smooth(DUST + 0.3, DUST + 0.6, t)

    def I(px_, py_):
        return cat.to_int((px_, py_), x, y, s)
    p_start = I(ccx + 50, cby - 40)
    p_end = I(ccx - 30, cby - 34)
    px = rest[0] + (p_start[0] - rest[0]) * a + (p_end[0] - p_start[0]) * b
    py = rest[1] + (p_start[1] - rest[1]) * a + (p_end[1] - p_start[1]) * b - 26 * math.sin(math.pi * b)
    px = px + (rest[0] - px) * back
    py = py + (rest[1] - py) * back
    paw_wx = cat.to_world((px, py), x, y, s)[0]
    wipe = 1e4 if t < DUST - 0.16 else min(1e4, paw_wx + 6) if b < 0.999 else ccx - 80
    if t > DUST + 0.12:
        wipe = ccx - 80
    shine = clamp((t - DUST - 0.18) / 0.5)
    w.append(card_svg(ccx, cby, ck, 1.0, wipe, t, shine=shine if 0 < shine < 1 else 0.0))
    if t > DUST + 0.4:
        a2 = math.sin(math.pi * clamp((t - DUST - 0.4) / 0.6))
        w.append(sparkle(ccx + 30, cby - 50, 16 * a2, t * 2, "#ffffff", a2))
        w.append(sparkle(ccx - 34, cby - 20, 10 * a2, -t * 2, "#fff6c8", a2))
    tilt = 1.6 * math.sin(t * 1.2) - 5 * smooth(DUST - 0.4, DUST - 0.1, t) * (1 - smooth(DUST + 0.3, DUST + 0.6, t))
    blink = max(blink_at(t, 31.9), blink_at(t, 33.2))
    lk = smooth(DUST - 0.45, DUST - 0.2, t) * (1 - smooth(DUST + 0.35, DUST + 0.6, t))
    look = (0.08 * math.sin(t * 0.8) - 0.75 * lk, -0.05 + 0.45 * lk)
    tail = 6 + 9 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1)
    flick = flick_at(t, DUST + 0.05, -12) + flick_at(t, 32.0, -9)
    w.append(blob(ellipse_pts(x + 20, y + 2, 120 * s / .85, 10, 16), "#3a1a08", .28, lib.blur(4)))
    w.append(flame_glow(x, y, s, tail, t, 1.2, 140))
    w.append(cat_svg(x, y, s, t, shadow=False, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw=(px, py),
                     press=0.0, flame_k=1.3, mitt=a > 0.3))
    w.append(dust_cloud(ccx - 10, cby - 40, clamp((t - DUST + 0.05) / 0.9)))
    w.append(HL.front(t))
    return svg_cam("".join(w), (cx, cy, sc, rot))


def frame(sid, t):
    if "cat" not in _C:
        keep = lib.INK_K[0]
        lib.INK_K[0] = 1.0
        cat.static_parts()
        lib.INK_K[0] = keep
        _C["cat"] = 1
        lib.static_done()
    return {"s05": frame05, "s16": frame16, "s17": frame17, "s18": frame18}[sid](t)
