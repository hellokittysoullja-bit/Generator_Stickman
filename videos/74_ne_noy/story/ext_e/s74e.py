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
import room as R  # noqa: E402
from h74 import bump, lerp, set_ink, shake, sm, whip, wt  # noqa: E402
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
FX_Y, FX_B = 315.0, 765.0
FK = 1.75


def paper_wave(t):
    """Лёгкая волна-штрих катится по бумаге слева направо (с кадра 0)."""
    o = []
    for j, (y0, amp, sp, op) in enumerate(((1130.0, 18.0, 2.6, .75), (1190.0, 12.0, 3.3, .45))):
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
    xY = FX_Y + 34 * slide
    xB = FX_B - 34 * slide
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


# ═════════════════════════ s09: письмо висело три недели — стол без людей, небо перелистывается ═════════════════════════
T_A09 = 11.30
T_DVUH, T_STROK = wt(28), wt(29)                     # 11.95, 12.15
T_VIS, T_TRI, T_NED = wt(30), wt(31), wt(32)         # 12.54, 12.98, 13.11
FLIPS = ((T_VIS, T_VIS + .38), (T_TRI, T_TRI + .12), (T_NED, T_NED + .38))
PH09 = (705.0, R.DESK_TOP - 12)                      # телефон лежит на столе левее цветка
PLANT09 = (905.0, R.DESK_TOP - 30)
MUG09 = (1075.0, R.DESK_TOP - 18)
CAM09 = (930.0, 790.0, 1.5)


def sky09(t):
    """Небо: ночь с луной (0.70 → 0.75), затем три полных оборота день-ночь, каждый быстрее «перелистывается»."""
    u = .70 + .05 * clamp((t - 11.1) / (T_VIS - 11.1))
    for a, b in FLIPS:
        u += ease_in(clamp((t - a) / (b - a)), 1.4) if t > a else 0.0
    return u


def phone_lying(x, y, k, t, glow, hl):
    """Телефон экраном вверх на столе: чертёж phone_draft, сжатый по вертикали (вид сверху-спереди) и повёрнутый."""
    ph = PR.phone_draft(0, 0, 1.0, 0.0, glow=glow, cursor_t=t * 1.6, hl=hl, dust_u=clamp(.35 + .65 * (sky09(t) - .75) / 3))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f} {k * .5:.4f}) rotate(-88)">{ph}</g>')


def s09(t):
    sky = sky09(t)
    sc = R.night_desk(t, "lamp", "wide", sky_u=sky)
    # цветок: никнет на каждой смене, два листа падают на «недели»
    droop = .08 + .3 * sm(t, T_VIS, T_VIS + .3) + .3 * sm(t, T_TRI, T_TRI + .2) + .3 * sm(t, T_NED, T_NED + .3)
    fallen = 1.4 * ease_in(clamp((t - (T_NED + .02)) / .3), 1.3) + .6 * clamp((t - (T_NED + .32)) / .14)
    plant = PR.houseplant(PLANT09[0], PLANT09[1], .82, droop=droop, fallen=min(2.0, fallen), t=t)
    # кружка: пар тает к «три»
    steam = 1 - sm(t, T_VIS, T_TRI + .05)
    mug = PR.mug(MUG09[0], MUG09[1], .8, col="red", steam=steam, t=t, seed=3)
    # телефон: «двух строк» — экран мигает дважды; «недели» — гаснет и снова загорается
    blink = bump(t, T_DVUH, .16) + bump(t, T_STROK + .05, .16)
    off = bump(t, T_NED + .06, .36)
    glow = clamp(1 - .7 * blink - 1.0 * off)
    phone = phone_lying(PH09[0], PH09[1], .48, t, glow, .6 * blink)
    plight = PR.glow(PH09[0], PH09[1] - 20, 170, .3 * glow, "#DDE8FF", ry=70)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], sc["desk_legs"], sc["chair_seat"], plant, mug, phone, plight, sc["lamp"]]
    cx, cy, s0 = CAM09
    kick = bump(t, T_NED, .4)
    s = s0 * (1.0 + .015 * sm(t, T_A09 - .2, 13.8) + .03 * kick)
    ccx = cx + 10 * math.sin(t * 1.3) - 30 * sm(t, T_A09 - .2, 13.8)
    ccy = cy + 6 * math.sin(t * 1.7) + 20 * kick
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, .3 * math.sin(t * .9))}">{"".join(world)}</g>'
    return whip(g, t, T_A09 - .2, amp=420, blur=36, dur=.24, side=1), "#2a2030"


FRAMES["s09"] = s09
