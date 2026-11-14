"""Рилс 63, группа D, s09 (17.4–19.55): ночь, комната (common/room.py night_room) — Дима за столом, за ним пустая кровать, в окне
луна, часы без цифр за полночь. «Другое» (17.44) щёлк — лампа вспыхивает (небольшое пятно с чётким краем), «дело» (18.30) Дима
тянется к кофейнику и берёт его пальцами за ручку, «пить кофе» (18.96–19.25) наклоняет и наливает струёй в кружку; взгляд тусклый,
мешки. Камера: дрейф от кровати к столу и наезд на Диму. Дима ≥ 45 % высоты кадра."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import people  # noqa: E402
import room as R  # noqa: E402
import s63d as D  # noqa: E402
from lib import clamp, ease_io, ease_out, smooth  # noqa: E402

props = D.props
SC = 1.25
HIP = (R.N_DIMA[0] - 40, R.N_DIMA[1] + 20)
POT0 = (875.0, R.N_DESK[2] - 40)        # кофейник стоит на столе
POTK = 1.15
MUG = (735.0, R.N_DESK[2] - 10)         # кружка перед Димой
MUGK = 1.05
H_LOC = (100.0, -130.0)
LAMP = (250.0, R.N_DESK[2] - 60)                 # середина ручки кофейника (кофейник отражён: ручка справа, носик слева)


def pot_state(t):
    """Положение кофейника: (x, y дна, поворот°). Поднимается после хвата и наклоняется носиком к кружке."""
    lift = ease_io(clamp((t - 18.62) / .32))
    tilt = ease_out(clamp((t - 18.86) / .28), 2)
    x = POT0[0] - 40 * lift
    y = POT0[1] - 150 * lift + 6 * math.sin(t * 9) * tilt
    rot = -46 * tilt - 3 * tilt * math.sin(t * 5)          # отражённый: минус — носик вниз влево
    return x, y, rot


def pot_pt(x, y, rot, p):
    """Точка p (локальные координаты отражённого кофейника) в мире."""
    a = math.radians(rot)
    px, py = p[0] * POTK, p[1] * POTK
    return x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)


def pot_svg(x, y, rot, t):
    inner = props.coffee_pot(0, 0, POTK, 0, t)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.3f}) scale(-1 1)">{inner}</g>'


def frame09(t):
    lamp = smooth(D.T_DRUGOE - .02, D.T_DRUGOE + .06, t)
    flash = D.bump(t, D.T_DRUGOE, .3)
    ah, am = props.clock_hm(0, 38 + (t - 17.2) * 1.2)
    rm = R.night_room(t, lamp_on=lamp, flick=.0, clock=(ah, am))
    o = [rm["bg"]]
    # Дима: руки на столе → ближняя тянется к ручке кофейника, берёт, поднимает и наклоняет
    px, py, prot = pot_state(t)
    hc = pot_pt(px, py, prot, H_LOC)
    reach = ease_io(clamp((t - (D.T_DELO - .05)) / .38))
    grab = t >= D.T_DELO + .33
    rest_n = (HIP[0] + 225 * SC, HIP[1] - 200 * SC)
    tgt_h = (hc[0] + 48, hc[1] + 30)
    tgt_n = (rest_n[0] + (tgt_h[0] - rest_n[0]) * reach, rest_n[1] + (tgt_h[1] - rest_n[1]) * reach)
    blink = max(D.bump(t, 17.75, .22), D.bump(t, 19.0, .24))
    ex = dict(people.EXPR["dima"]["dull"])
    ex["lid"] = .22 * (1 - blink) + .1 * flash
    ex["look"] = (.25 + .35 * reach, .5 + .1 * reach)
    if flash > .05:
        ex["scale_n"] = ex["scale_f"] = 1 + .12 * flash
    hands = {"f": {"curl": (.35, .35, .4, .45), "thumb": .35}, "n": {"kind": "none"} if grab else
             {"curl": (.2 + .3 * reach, .2 + .3 * reach, .25 + .3 * reach, .3 + .3 * reach), "thumb": .3, "spread": .15}}
    fig = people.figure("dima", HIP[0], HIP[1], SC, ex, lean=.06 + .08 * reach, head_ang=.04 * math.sin(t * 1.6) + .05 * reach,
                        arms={"f": ("ik", (HIP[0] + 190 * SC, HIP[1] - 205 * SC), -1), "n": ("ik", tgt_n, -1)}, hands=hands,
                        layers=("pelvis", "arm_f", "body"))
    o.append(fig["svg"])
    x0, x1 = R.N_DESK[0], R.N_DESK[1]
    o.append(lib.shape(lib.rect_pts(x0 + 30, R.N_DESK[2] + 20, x1 - 30, R.N_FLOOR + 30), R.WOOD_SH,
                       lib.blob(lib.rect_pts(x0 + 30, R.N_DESK[2] + 20, x1 - 30, R.N_DESK[2] + 60), lib.mul(R.WOOD_SH, (.8, .8, .8)))
                       + lib.line([(x0 + 60, R.N_DESK[2] + 200), (x1 - 60, R.N_DESK[2] + 200)], 3, R.WOOD, seed=9811), w=4.2, seed=9810))
    o.append(rm["desk"])
    lx, ly = LAMP
    if lamp > .02:
        c1 = lib.mix(R.LIGHTWOOD, "#ffe7a3", .65 * lamp)
        c2 = lib.mix(R.LIGHTWOOD, "#fff6d8", .8 * lamp)
        o.append(lib.blob(lib.ellipse_pts(lx + 130, ly + 14, 210, 44, 30), c1) + lib.blob(lib.ellipse_pts(lx + 120, ly + 14, 130, 26, 26), c2))
    # кружка: наполняется под струёй
    fill = clamp((t - 19.02) / .55)
    mug_svg = props.coffee_mug(MUG[0], MUG[1], MUGK, 0, "white", fill=fill, steam=clamp((t - 19.25) / .3) * .8, t=t, seed=3)
    # дальняя рука на столе уже нарисована; ближняя — поверх стола
    arm_n = people.figure("dima", HIP[0], HIP[1], SC, ex, lean=.06 + .08 * reach, head_ang=0,
                          arms={"f": ("ik", (HIP[0] + 190 * SC, HIP[1] - 205 * SC), -1), "n": ("ik", tgt_n, -1)}, hands=hands, layers=("arm_n",))
    if grab:
        back, front = people.handle_grip("dima", hc, k=SC * .8, side=1, seed=961)
        o.append(f'<g transform="rotate({prot * .5:.2f} {hc[0]:.2f} {hc[1]:.2f})">{back}</g>')
        o.append(arm_n["svg"])
        o.append(pot_svg(px, py, prot, t))
        o.append(f'<g transform="rotate({prot * .5:.2f} {hc[0]:.2f} {hc[1]:.2f})">{front}</g>')
    else:
        o.append(pot_svg(px, py, prot, t))
        o.append(arm_n["svg"])
    o.append(mug_svg)
    if t > 18.98:
        tip = pot_pt(px, py, prot, (-110, -194))
        o.append(props.pour_stream(tip[0], tip[1], MUG[0] + 6, MUG[1] - 130 * MUGK + 10, t, w=12, seed=31, bend=.1))
    o.append(props.lamp_desk(lx, ly, 1.6, on=lamp, tilt=14, seed=5))
    # щелчок выключателя лампы: короткие штрихи у абажура
    if 0 < t - D.T_DRUGOE < .3:
        o.append(props.clink(LAMP[0] + 40, LAMP[1] - 230, 1.3, (t - D.T_DRUGOE) / .3, seed=5, col="#ffe7a3"))
    # камера: дрейф от кровати к столу и наезд на Диму
    u = ease_io(clamp((t - 17.2) / 2.55))
    z = 1.14 + .22 * u + .03 * flash
    cx, cy = 380 + 250 * u, 1010 - 110 * u
    sh = props.shake(t, D.T_DRUGOE, amp=5, dur=.25, seed=2)
    lib.INK_K[0] = 1.0 / z ** .5
    return f'<g transform="{lib.cam(cx + sh[0], cy + sh[1], z, -.8 + 1.4 * u)}">{"".join(o)}</g>'
