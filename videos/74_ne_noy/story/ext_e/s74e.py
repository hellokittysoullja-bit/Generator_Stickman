"""Рилс 74 «Прекрати ныть», группа E — лагеря и время.
s05 (4.90–6.25): «два лагеря» на пустой кремовой бумаге. С кадра 0 по бумаге катится волна-штрих. «согласен» (4.95) слева
    выскакивает жёлтый смайлик и кивает; «или» (5.28) между ними проскакивает искра; «обиделся» (5.57) справа выскакивает синий
    надутый смайлик, отворачивается и топает; смайлики сталкиваются боками; с 5.80 края темнеют. Камера — наезд с разгоном к стыку
    смайликов прямо в склейку 6.25.
s09 (11.30–13.60, хлёст): стол Димы общим планом без людей — телефон с черновиком, цветок, кружка, окно. «висело» (12.54),
    «три» (12.98), «недели» (13.11) — три смены неба день-ночь, цветок никнет, кружка остывает, два листа падают, телефон гаснет и
    снова загорается.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Предметы — common/props.py, комната — common/room.py; здесь только
хореография и камера. Надписей, букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import props as PR  # noqa: E402
from h74 import bump, lerp, set_ink, shake, sm, wt  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_out, ellipse_pts, line  # noqa: E402

FRAMES = {}


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')


def vignette(u, col="#05070f"):
    """Края кадра темнеют (экранные координаты)."""
    if u <= .01:
        return ""
    g = lib.rad_grad([(0, col, 0), (.45, col, 0), (.8, col, .55 * u), (1, col, .92 * u)], 540, 900, 820, 1250)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


# ═════════════════════════ s05: два лагеря — смайлики ═════════════════════════
T_A05, T_B05 = 4.90, 6.25
T_SOG, T_ILI, T_OBI = wt(13), wt(14), wt(15)        # 4.949, 5.28, 5.573
T_HIT = 5.98                                         # бока смайликов сталкиваются
FY = 820.0                                           # высота центров смайликов
FX_Y, FX_B = 345.0, 735.0
FK = 1.0


def paper_wave(t):
    """Лёгкая волна-штрих катится по бумаге слева направо (с кадра 0)."""
    o = []
    for j, (y0, amp, sp, op) in enumerate(((1130.0, 16.0, 2.6, .55), (1190.0, 10.0, 3.3, .32))):
        ph = t * sp
        pts = [(x, y0 + amp * math.sin(x / 95.0 - ph * 2.2) * (.6 + .4 * math.sin(x / 260.0 + ph))) for x in range(80, 1001, 40)]
        o.append(line(pts, 4.2, PR.C_PAGE_LINE, taper=.45, wmin=.25, seed=7400 + j, op=op))
    return "".join(o)


def spark(x, y, u, t):
    """Искра «или»: четырёхлучевая вспышка и три коротких штриха, гаснет за 0.3 с."""
    if u <= .01:
        return ""
    o = [PR.star4(x, y, 46 * u, u)]
    o.append(blob(ellipse_pts(x, y, 9 * u, 9 * u, 10), "#FFD34A"))
    for j in range(3):
        a = math.radians(-90 + j * 120 + 20)
        r0, r1 = 34 * u, 70 * u
        o.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 4.6, "#E9A21F",
                      taper=.7, wmin=.2, seed=7410 + j, op=u))
    return "".join(o)


def stomp_lines(x, y, u, seed=0):
    """Штрихи топота под смайликом."""
    if u <= .02:
        return ""
    o = []
    for j, s in enumerate((-1, 1)):
        o.append(line([(x + s * 70, y), (x + s * (100 + 40 * u), y - 18 * u)], 4.0, INK, taper=.7, wmin=.2, seed=seed + j, op=.8 * u))
        o.append(line([(x + s * 60, y + 18), (x + s * (96 + 46 * u), y + 22)], 3.6, INK, taper=.7, wmin=.2, seed=seed + 5 + j, op=.6 * u))
    return "".join(o)


def face(x, y, k, kind, popu, t, rot=0.0, sx=1.0, sy=1.0):
    g = PR.face_icon(0, 0, k, kind, popu, t)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({sx:.4f} {sy:.4f})">{g}</g>'


def s05(t):
    o = [f'<rect x="-1400" y="-1600" width="4000" height="4800" fill="{PR.C_PAGE}"/>', paper_wave(t)]
    # жёлтый: выскакивает на «согласен» с перебором, два кивка
    ysx, ysy = PR.pop(t, T_SOG - .04, amp=.34)
    nod = math.sin(clamp((t - (T_SOG + .16)) / .5) * 2 * math.pi * 2) * (1 - clamp((t - (T_SOG + .16)) / .5)) if t > T_SOG + .16 else 0.0
    # синий: выскакивает на «обиделся», отворачивается и топает
    bsx, bsy = PR.pop(t, T_OBI - .03, amp=.38)
    turn = sm(t, T_OBI + .14, T_OBI + .3)
    st1, st2 = T_OBI + .3, T_OBI + .44
    hopb = PR.hop(t, st1 - .1, 26, .12) + PR.hop(t, st2 - .1, 22, .12)
    shb = shake(t, st1, 7)[0] + shake(t, st2, 6)[0]
    sqb = PR.squash(t, st1, .14)
    sqb2 = PR.squash(t, st2, .12)
    # столкновение: оба едут к середине, бока встречаются на T_HIT, отскок
    go = ease_in(clamp((t - (T_HIT - .2)) / .2), 2.2)
    back = PR.settle(t, T_HIT, 1.0, .82) if t > T_HIT else 1.0
    slide = go * back
    sq_hit = PR.squash(t, T_HIT, .16, 3.4, 8)
    xY = FX_Y + 42 * slide
    xB = FX_B - 42 * slide
    hitjit = shake(t, T_HIT, 6)
    if ysx > .01:
        o.append(face(xY + hitjit[0], FY + 8 * nod + hitjit[1], FK, "smile", 1.0, t, rot=-4 + 7 * nod,
                      sx=ysx * sq_hit[1], sy=ysy * sq_hit[0] * (1 - .04 * nod)))
    if bsx > .01:
        o.append(face(xB + shb - hitjit[0], FY + hopb, FK, "pout", 1.0 if turn < 1 else 1.0, t, rot=10 * turn,
                      sx=bsx * sqb[0] * sqb2[0] * sq_hit[1], sy=bsy * sqb[1] * sqb2[1] * sq_hit[0]))
        o.append(stomp_lines(xB, FY + 165, bump(t, st1, .2) + bump(t, st2, .2), seed=7420))
    o.append(spark(540, FY - 40 + 30 * (t - T_ILI), bump(t, T_ILI - .02, .32), t))
    if t > T_HIT - .01:
        o.append(spark(540, FY, .8 * bump(t, T_HIT - .01, .22), t))
    # камера: дрейф, затем наезд с разгоном к стыку прямо в склейку 6.25
    drift = sm(t, T_A05 - .2, 5.8)
    rush = ease_in(clamp((t - 5.62) / (T_B05 - 5.62)), 2.6)
    s = lerp(1.0, 1.06, drift) + .72 * rush + .04 * max(0.0, t - T_B05)
    cx = 540 + 6 * math.sin(t * 1.8) * (1 - rush)
    cy = lerp(910, 860, drift) + (FY - 860) * rush
    set_ink(s)
    rot = lerp(-.6, .4, drift) + 1.4 * rush
    body = f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(o)}</g>'
    return body + vignette(sm(t, 5.80, T_B05 + .05)), PR.C_PAGE


FRAMES["s05"] = s05
