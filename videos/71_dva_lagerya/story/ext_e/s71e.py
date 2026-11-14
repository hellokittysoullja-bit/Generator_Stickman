"""Рилс 71 «два лагеря», группа E — три маленьких шага и поток.
s16 (28.30–29.36, хлёст): стол сбоку в три четверти, ноутбук экраном к Диме; «Открыть» поднимает крышку одним пальцем, «ноутбук» экран
    загорается, свет на лице, Дима моргает.
s17 (29.36–30.40): край кровати, Дима натягивает полосатый носок на одну ногу, шевелит пальцами, вторая нога босая, кивает.
s19 (31.50–32.74): Дима в потоке печатает, стакан наполовину пуст, на ногах оба носка; «идёт само» — меловая стена за спиной осыпается.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, Дима — common/people.py, предметы — common/props.py;
здесь только хореография и камера (ноутбук экраном к Диме и ступни без кроссовок — h71.py). Надписей, букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from h71 import bare_feet, blinks, bump, laptop_side, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
from lib import INK, blob, clamp, ease_out, ellipse_pts, line  # noqa: E402

BG = "#e6dcc0"
FRAMES = {}
SX, SY = R.SIT
FEET = {"n": ((SX + 300, R.FL - 52), 0.0), "f": ((SX + 250, R.FL - 50), 0.0)}
LAP = (690.0, R.DESK_TOP - 70)       # передний (к Диме) край ноутбука на столешнице
LAP_K = .82


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.setdefault("bags", False)
    e.update(kw)
    return e


def parts_of(e, pose, **kw):
    full = people.dima(SX, SY, 1.0, e, pose, **kw)
    parts = {k: people.dima(SX, SY, 1.0, e, pose, layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    return full, parts


def face_light(head, u):
    """Холодный свет экрана на лице: небольшое пятно у лица (не огромный овал)."""
    if u <= .01:
        return ""
    return PR.glow(head[0] + 60, head[1] + 10, 150, .5 * u, "#DDE8FF", ry=170)


def type_hand(t, base, phase):
    ph = t * 10.5 + phase
    W = (base[0] + 8 * math.sin(ph * .7), base[1] - 5 * abs(math.sin(ph)))
    curl = tuple(.35 + .25 * max(0.0, math.sin(ph + i * 1.7)) for i in range(4))
    return W, {"dir": (1, .32), "curl": curl, "thumb": .35, "spread": .12, "bend": .1}


# ═════════════════════════ s16: открыть ноутбук одним пальцем ═════════════════════════
T_A16 = 28.30
T_OTKR, T_NOUT = wt(87), wt(88)              # 28.37, 28.85


def s16(t):
    sc = R.desk34_scene(t)
    op = ease_out(clamp((t - (T_OTKR - .05)) / (T_NOUT - .02 - (T_OTKR - .05))), 1.8)
    on = sm(t, T_NOUT - .02, T_NOUT + .14)
    lp = laptop_side(LAP[0], LAP[1], LAP_K, op, on=on, lines=0.0, t=t, seed=1)
    lt = lp["lid_top"]
    # ближняя рука: указательный палец под край крышки → поднимает → на «ноутбук» отпускает, кисть ложится у корпуса
    rel = sm(t, T_NOUT + .05, T_NOUT + .3)
    W_lift = (lt[0] - 78, lt[1] + 34)
    W_rest = (LAP[0] - 60, LAP[1] - 20)
    W_start = (LAP[0] - 30, LAP[1] - 10)
    go = sm(t, T_A16 - .2, T_OTKR - .02)
    Wn = lerp2(lerp2(W_start, W_lift, go), W_rest, rel)
    hn = {"dir": (1, -.35), "curl": (0, .8, .85, .85), "spread": .05, "thumb": .6} if rel < .5 else {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}
    Wf = (LAP[0] - 150, LAP[1] - 14)
    surprise = bump(t, T_NOUT + .05, .55)
    e = ex("focus", look=(.65, lerp(.55, .2, op)), lid=lerp(.62, .9, surprise), closed=blinks(t, (T_NOUT + .28, T_NOUT + .52), .14),
           brows="up" if surprise > .3 else "det")
    full, parts = parts_of(e, "lid_finger", feet=FEET, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)},
                           hands={"f": {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}, "n": hn},
                           lean_add=.04 * go - .05 * surprise + .015 * math.sin(t * 2.4), head_add=.05 - .06 * surprise)
    light = face_light(full["head"], on)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"], parts["arm_f"],
             parts["body"], lp["svg"], parts["arm_n"], light]
    # камера: хлёст, короткий наезд на лицо в свете экрана; мини-толчок на вспышке экрана
    u = sm(t, T_A16 - .2, 29.56)
    s = lerp(1.42, 1.62, u) + .03 * bump(t, T_NOUT, .3)
    hx, hy = full["head"]
    ccx = lerp(610, hx + 270, u) + 4 * math.sin(t * 1.5)
    ccy = lerp(880, hy + 200, u) + 3 * math.sin(t * 1.9)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.6, .3, u))}">{"".join(world)}</g>'
    return whip(g, t, T_A16), BG


FRAMES["s16"] = s16


# ═════════════════════════ s17: край кровати — надеть один носок ═════════════════════════
T_A17 = 29.36
T_NAD, T_ODIN, T_NOS = wt(89), wt(90), wt(91)          # 29.40, 29.73, 29.98
HIP17 = (1560.0, R.DR_BED_TOP - 8)


def s17(t):
    sc = R.day_room(t)
    hx, hy = HIP17
    # ближняя ступня поднята к рукам (колено к груди), носок натягивается с мыска на пятку; «носок» — пальцы шевелятся, кивок
    lift = sm(t, T_A17 - .25, T_NAD) * (1 - .5 * sm(t, T_NOS + .05, T_NOS + .35))
    pull = ease_out(clamp((t - (T_NAD - .02)) / (T_NOS - .05 - (T_NAD - .02))), 1.6)
    fk = people.sock_feet_kw(hx, hy, 1.0, lift)
    wig = 0.0
    if t > T_NOS:
        wig = .12 * math.sin(2 * math.pi * 5.5 * (t - T_NOS)) * math.exp(-1.6 * (t - T_NOS))
    (An, phin) = fk["feet"]["n"]
    fk["feet"]["n"] = (An, phin + wig)
    tug = .5 + .5 * math.sin(2 * math.pi * 3.2 * (t - T_NAD)) if pull < .98 else 1.0
    wn = (An[0] + 40 - 18 * pull + 6 * tug, An[1] - 70 - 10 * tug * (1 - pull))
    wf = (An[0] + 10 - 20 * pull, An[1] - 50 + 8 * tug * (1 - pull))
    let_go = sm(t, T_NOS - .05, T_NOS + .2)
    wn = lerp2(wn, (hx + 300, hy - 60), let_go)
    wf = lerp2(wf, (hx + 250, hy - 40), let_go)
    grip = {"dir": (.5, 1), "curl": (.55, .6, .65, .7), "thumb": .6}
    open_h = {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}
    nod = bump(t, T_NOS + .12, .42)
    pleased = sm(t, T_NOS, T_NOS + .25)
    e = ex("focus", look=(.55, .8), lid=.7, closed=blinks(t, (29.6,)))
    if pleased > .05:
        e = ex("relief71", look=(.5, lerp(.8, .6, pleased)), smile=.9 * pleased, closed=.6 * nod)
    lean = lerp(.08, .5, lift) - .1 * let_go + .015 * math.sin(t * 2.3)
    with bare_feet("sock", "bare", pull=pull):
        dima = people.dima(hx, hy, 1.0, e, "sock_pull", feet=fk["feet"], arms={"f": ("ik", wf, -1), "n": ("ik", wn, -1)},
                           hands={"f": grip if let_go < .5 else open_h, "n": grip if let_go < .5 else open_h},
                           lean_add=lean - people.POSE["sock_pull"][0], head_add=.08 * nod + .05 * math.sin(t * 1.9))["svg"]
    world = [sc["bg"], sc["desk"], sc["stand"], sc["bed"], dima, sc["front"]]
    # камера: дрейф вниз к ступням и обратно
    cx0 = R.CAM_BED_EDGE[0]
    d = math.sin(math.pi * sm(t, T_A17 - .2, 30.6))
    s = 1.12 + .06 * d + .01 * math.sin(t * 2)
    ccx = cx0 - 20 + 30 * d + 4 * math.sin(t * 1.5)
    ccy = 1235 + 40 * d + 3 * math.sin(t * 1.7)
    set_ink(s)
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(.5, -.4, d))}">{"".join(world)}</g>', BG


FRAMES["s17"] = s17


# ═════════════════════════ s19: поток — а дальше идёт само, стена за спиной осыпается ═════════════════════════
T_A19 = 31.50
T_A, T_DAL, T_IDET, T_SAMO = wt(94), wt(95), wt(96), wt(97)      # 31.56, 31.66, 32.03, 32.30
WALL19 = (-60.0, 240.0, 330.0, 1440.0)        # невидимая стена за спиной: проступает мелом и осыпается
GLASS19 = (1010.0, R.DESK_TOP - 66)


def s19(t):
    sc = R.desk34_scene(t)
    lines = clamp(.25 + (t - 31.3) * .55)
    lp = laptop_side(LAP[0], LAP[1], LAP_K, 1.0, on=1.0, lines=lines, t=t, seed=1)
    kc = lp["keys"]
    Wf, hf = type_hand(t, (kc[0] - 70, kc[1] + 2), 0.0)
    Wn, hn = type_hand(t, (kc[0] - 20, kc[1] + 10), 1.9)
    e = ex("focus_smile", look=(.7, .25), lid=.66, closed=blinks(t, (31.85, 32.7)))
    with bare_feet("sock", "sock"):
        full, parts = parts_of(e, "type", feet=FEET, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, hands={"f": hf, "n": hn},
                               lean_add=.05 + .02 * math.sin(t * 3.1), head_add=.03 * math.sin(t * 4.2))
    glass = PR.glass(GLASS19[0], GLASS19[1], .7, fill=.45, t=t, seed=2)
    # стена: мел проступает на «а дальше», на «идёт само» кирпичи падают и рассыпаются в пыль
    show = sm(t, T_A - .1, T_DAL + .25)
    crumble = clamp((t - (T_IDET - .05)) / (T_SAMO + .3 - (T_IDET - .05)))
    wall = PR.chalk_wall(*WALL19, u=show, crumble=crumble, t=t, seed=5, wline=6.5)
    light = face_light(full["head"], .8)
    world = [sc["bg"], wall, sc["chair_back"], sc["desk_top"], glass, parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"],
             parts["arm_f"], parts["body"], lp["svg"], parts["arm_n"], light]
    # камера: медленный отъезд, чтобы вошла осыпающаяся стена; мини-толчок, когда кирпичи падают
    u = sm(t, T_A19 - .2, 32.8)
    s = lerp(1.42, .95, u)
    ccx = lerp(640, 470, u) + 4 * math.sin(t * 1.4)
    ccy = lerp(880, 950, u) + 3 * math.sin(t * 1.8)
    sx_, sy_ = shake(t, T_SAMO, 5)
    set_ink(s)
    return f'<g transform="{lib.cam(ccx + sx_, ccy + sy_, s, lerp(-.4, .4, u))}">{"".join(world)}</g>', BG


FRAMES["s19"] = s19


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
