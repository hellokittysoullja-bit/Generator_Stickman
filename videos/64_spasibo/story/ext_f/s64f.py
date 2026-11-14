"""Рилс 64 «спасибо», группа F: s16 (диван днём: кот клубком у Димы на коленях приоткрывает глаз, мурлычет, Дима гладит, кот
жмурится, огонёк ярче), s17 (призыв: Дима с письмом и кот на подлокотнике смотрят на зрителя, кот поворачивает морду, на чистой стене
пером пишется «кот», Дима кивает), s18 (петля к кадру хука s01: тот же стол и ракурс, днём; Дима кладёт письмо в открытку, поднимает
глаза на зрителя, улыбается, кот запрыгивает на стол).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Комната — common/room.py, люди и кот — common/people.py (cat.py),
предметы — common/props.py, «кот» — common/hand_kot.py. Печатных букв и цифр нет; единственная надпись — рукописное «кот» (s17)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as CAT  # noqa: E402
import hand_kot  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»").lower() == word:
            return w["start"]
    raise KeyError(word)


T_A16 = 38.56
T_KOT16 = wt("кот", 38.0)          # 38.72 приоткрывает глаз
T_MUR = wt("мурлыкал")             # 39.00
T_KOL = wt("коленях")              # 39.90 жмурится
T_NAP = wt("напиши")               # 41.24
T_KOT = wt("кот", 41.5)            # 41.98 пишется «кот»
T_ESLI = wt("если")                # 42.30 Дима кивает
T_HOCH = wt("хочешь")              # 43.44 кладёт письмо в открытку
T_KOMU = wt("кому-то")             # 43.89 глаза на зрителя
T_SPAS = wt("спасибо", 44.0)           # 44.61 улыбка, кот на столе


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def decay(t, t0, k=9.0, fr=20.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def blinks(t, times, dur=.16):
    v = 0.0
    for tb in times:
        u = (t - tb) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.update(kw)
    return e


def whip(g, t, t_in, amp=260.0, blur=28.0, dur=.2, side=-1):
    """Хвост хлёста на входе плана: приезжает сбоку с размытием по x, гаснет за dur."""
    e = ease_out(clamp((t - t_in) / dur), 2)
    dx, b = side * amp * (1 - e), blur * (1 - e)
    g = f'<g transform="translate({dx:.1f} 0)">{g}</g>'
    if b > .5:
        fid = lib.uid("wb")
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{b:.1f} 0"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return g


# ═════════════════════════ диван: Дима сидит ═════════════════════════
BS = 1.0
HX, HY = R.SOFA_DIMA
SC = BS * people.HEIGHT["dima"]
FEET_SOFA = {"n": ((HX + 360 * BS, R.FL - 52), 0.0), "f": ((HX + 310 * BS, R.FL - 50), 0.0)}


def dima_sofa(e, pose, arms=None, hands=None, lean_add=0.0, head_add=0.0):
    kw = dict(feet=FEET_SOFA, arms=arms, hands=hands, lean_add=lean_add, head_add=head_add)
    full = people.dima(HX, HY, BS, e, pose, layers=("legs", "pelvis", "arm_f", "body", "arm_n"), **kw)
    parts = {k: people.dima(HX, HY, BS, e, pose, layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    return full, parts


# ═════════════════════════ s16: кот на коленях ═════════════════════════
CAT16 = (HX + 225.0, HY - 50.0)       # середина низа клубка — на бёдрах
K16 = 1.12
PET_PER = 1.25                        # период поглаживания


def s16(t):
    lib.dyn_begin()
    u_eye = sm(t, T_KOT16 - .02, T_KOT16 + .2) * (1 - sm(t, T_KOL - .1, T_KOL + .12))
    sq = sm(t, T_KOL - .05, T_KOL + .25)
    purr_u = sm(t, T_MUR - .05, T_MUR + .2)
    # мурлыканье — мелкая вибрация клубка (штрихи и дрожь), бока ходят глубже
    vib = purr_u * 1.6 * math.sin(t * 2 * math.pi * 23)
    stc = dict(eye=u_eye, look=(.35, -.1), squint=sq, breath=1.0 + .9 * purr_u, flame_e=1.0 + .25 * math.sin(t * 5) + .9 * sq,
               tail=6 * math.sin(t * 1.4), ear=3 * bump(t, T_KOT16 + .05, .3) + 1.2 * math.sin(t * 2.6), turn=-.15 + .1 * u_eye)
    cx, cy = CAT16
    cat_svg = CAT.curl(cx, cy + vib * .4, K16, stc, t)
    # рука гладит: ладонь по спине кота от шеи к бедру и обратно (по спине — с нажимом, назад — чуть выше)
    ph = ((t - T_A16 + .3) / PET_PER) % 1.0
    stroke = ease_io(ph / .62) if ph < .62 else 1 - ease_io((ph - .62) / .38)
    lift = 0.0 if ph < .62 else math.sin(math.pi * (ph - .62) / .38) * 22
    pet_on = sm(t, T_A16 - .3, T_A16 + .1)
    back_y = cy - 104 * K16
    Wn = (cx - 95 * K16 + 200 * K16 * stroke, back_y - 30 - lift)
    Wn = lerp2((HX + 250 * SC, HY - 160 * SC), Wn, pet_on)
    e = ex("relief64", look=(lerp(.3, -.25, sm(t, T_MUR + .3, T_MUR + .8)), lerp(.55, .15, sm(t, T_MUR + .3, T_MUR + .8))),
           closed=blinks(t, (40.6,)), smile=.8 + .2 * sq)
    hands = {"n": {"dir": (1, .42 - .3 * (lift / 22)), "curl": (.32, .34, .38, .42), "spread": .14, "thumb": .3, "bend": .25},
             "f": {"dir": (.9, .45), "curl": (.35, .4, .45, .5), "thumb": .35}}
    Wf = (HX + 330 * SC, HY - 70 * SC)
    full, parts = dima_sofa(e, "pet", arms={"n": ("ik", Wn, -1), "f": ("ik", Wf, -1)}, hands=hands,
                            lean_add=.04 * math.sin(t * 1.1) + .06, head_add=.06 * math.sin(t * .9) - .04)
    sc = R.sofa_scene(t, "day")
    mob = PR.mobilnik(HX + 545 * SC, R.SOFA_SEAT - 12, .8, 84)   # мобильник опущен рядом на подушку, у колена
    purr = PR.purr(cx - 120 * K16, cy - 150 * K16, 1.1, t, purr_u, seed=1) + PR.purr(cx + 120 * K16, cy - 120 * K16, .9, t + .35, purr_u * .8, seed=7)
    # голова кота лежит ближе к зрителю, чем предплечье: копия кота поверх руки, обрезанная по голове и передним лапам
    hc = lib.uid("hd")
    lib.DEFS.append(f'<clipPath id="{hc}"><path d="{lib.fill_d(ellipse_pts(cx - 150 * K16, cy - 120 * K16, 128 * K16, 150 * K16, 24))}"/></clipPath>')
    head_over = f'<g clip-path="url(#{hc})">{cat_svg}</g>'
    world = [sc["bg"], sc["sofa"], mob, parts["legs"], parts["pelvis"], parts["arm_f"], parts["body"], cat_svg, parts["arm_n"], head_over, sc["front"], purr]
    # камера: медленный откат, «дыхание»
    u = sm(t, T_A16 - .2, 41.44)
    z = 1.72 - .22 * u + .012 * math.sin(t * 2.1)
    ccx = HX + 200 - 20 * u
    ccy = 900 + 40 * u + 4 * math.sin(t * 1.7)
    set_ink(z)
    g = f'<g transform="{lib.cam(ccx, ccy, z, .7 - 1.0 * u)}">{"".join(world)}</g>'
    return whip(g, t, T_A16), "#e6dcc0"


FRAMES = {"s16": s16}


# ═════════════════════════ s17: призыв, рукописное «кот» ═════════════════════════
T_A17 = 41.24
CAT17 = (R.ARM_TOP[0] - 6, R.ARM_TOP[1] + 4)
K17 = .82
KOT_T0, KOT_DUR = T_KOT - .02, .32          # дописано к 42.28 (звук «слово дописано»)
KOT_SIZE = 1.6
KOT_XY = (CAT17[0] - 215.0, 615.0)          # над котом, чистая стена CLEAN_WALL (2420…3000 × 260…680)


def s17(t):
    nod = .07 * bump(t, T_ESLI + .02, .42) + .04 * bump(t, T_ESLI + .45, .38)
    breath = math.sin(2 * math.pi * (t - T_A17) / 2.4)
    e = ex("warm", look=(-.35, .02), closed=blinks(t, (41.7, 43.1)), smile=1.0)
    # письмо в обеих руках у груди, чуть покачивается; на кивке руки приподнимаются
    lift = 10 * bump(t, T_ESLI, .5) + 5 * breath
    Wf = (HX + 205 * SC, HY - 300 * SC - lift)
    Wn = (HX + 290 * SC, HY - 296 * SC - lift)
    full, parts = dima_sofa(e, "letter", arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, lean_add=-.04 + .01 * breath, head_add=-nod - .04)
    wf, wn = full["wrist"]["f"], full["wrist"]["n"]
    lt = PR.letter((wf[0] + wn[0]) / 2 + 40, (wf[1] + wn[1]) / 2 - 70, .62, -6 + 2 * math.sin(t * 1.3), write=1.0, seed=17)
    # кот на подлокотнике: смотрит на Диму, на «Напиши» поворачивает морду к зрителю через три четверти
    tu = sm(t, T_NAP + .06, T_NAP + .46)
    st = dict(turn=-.8 * (1 - tu) + .05 * bump(t, T_NAP + .46, .3), look=(-.85 * (1 - tu), -.25 * (1 - tu)), blink=blinks(t, (41.9, 43.25)),
              tail=7 * math.sin(t * 2.1), ear=2 * math.sin(t * 3.3) + 6 * bump(t, T_KOT + .05, .3),
              tilt=-6 * (1 - tu) + 2.5 * math.sin(t * 1.2) + 5 * bump(t, T_KOT + .15, .5), perk=.6 * bump(t, T_KOT, .55),
              flame_e=1.1 + .7 * bump(t, T_KOT + .1, .5), smile=1.0 if t > T_KOT + .3 else 0.0)
    sc = R.sofa_scene(t, "day")
    shadow = blob(ellipse_pts(CAT17[0] + 8, CAT17[1] - 2, 105 * K17 / .82, 12, 14), "#2c4470", .5)
    world = [sc["bg"], sc["sofa"], parts["legs"], parts["pelvis"], parts["arm_f"], parts["body"], lt, parts["arm_n"], sc["front"], shadow,
             CAT.draw(CAT17[0], CAT17[1], K17, st, t), hand_kot.kot(t, KOT_T0, KOT_DUR, KOT_XY[0], KOT_XY[1], KOT_SIZE)]
    u = sm(t, T_A17 - .1, 43.64)
    z = 1.13 + .1 * u + .025 * bump(t, KOT_T0 + KOT_DUR, .35)
    cx = 2455 + 10 * u
    cy = 980 - 30 * u
    set_ink(z)
    g = f'<g transform="{lib.cam(cx, cy, z, .6 - .9 * u)}">{"".join(world)}</g>'
    return whip(g, t, T_A17, side=1), "#e6dcc0"


FRAMES["s17"] = s17


# ═════════════════════════ s18: петля к кадру хука s01 (тот же стол и ракурс, днём) ═════════════════════════
sys.path.insert(0, os.path.join(STORY, "ext_c"))
import s64c as C1  # noqa: E402  (только чтение: та же раскладка Димы за столом и порядок слоёв, что у s01)

T_A18 = 43.44
CARD_POS = (C1.SX + 225 * C1.SC + 150, R.DESK_TOP - 40 - 115 * C1.CARD_K * .9)   # открытка лежит там же, где легла в s01
CARD_YB = CARD_POS[1] + 115 * C1.CARD_K * .9
LET_IN = (CARD_POS[0] + 80, CARD_POS[1] + 34)          # письмо ложится на правую страницу раскрытой открытки
CAT18_K = .5
CAT18_FLOOR = (1290.0, R.FL - 6)
CAT18_DESK = (1215.0, R.DESK_TOP - 34)
T_JUMP0, T_JUMP1 = T_SPAS - .3, T_SPAS + .42


def s18(t):
    # ближняя кисть: держит сложенное письмо над открыткой → «хочешь» опускает его на страницу → отпускает → к груди
    put = sm(t, T_HOCH - .02, T_HOCH + .36)
    rel = sm(t, T_HOCH + .4, T_HOCH + .75)
    dn = np.array((.85, .5)) / np.linalg.norm((.85, .5))
    W_hold = (C1.SX + 270 * C1.SC + 6 * math.sin(t * 2.4), C1.SY - 330 * C1.SC + 5 * math.cos(t * 2.0))
    W_put = (LET_IN[0] - dn[0] * 58 * C1.SC - 20, LET_IN[1] - dn[1] * 58 * C1.SC - 10)
    W_rest = (C1.SX + 330 * C1.SC, R.DESK_TOP - 110)
    Wn = lerp2(lerp2(W_hold, W_put, put), W_rest, rel)
    Wn = (Wn[0], Wn[1] - 8 * bump(t, T_HOCH + .3, .2))
    Wf = (C1.SX + 225 * C1.SC + 3 * math.sin(t * 1.3), R.DESK_TOP - 120)
    grip = 1 - rel
    hands = {"f": {"curl": (.55, .6, .62, .65), "thumb": .55, "dir": (.75, -.65)},
             "n": {"curl": tuple(lerp(a, b, grip) for a, b in zip((.25, .25, .3, .35), (.72, .76, .8, .82))), "thumb": lerp(.3, .6, grip),
                   "dir": (lerp(.9, .85, grip), lerp(.25, .5, grip))}}
    # взгляд: на открытку → «кому-то» на зрителя; «спасибо» — тёплая улыбка
    up = sm(t, T_KOMU - .04, T_KOMU + .22)
    sml = sm(t, T_SPAS - .05, T_SPAS + .3)
    e = ex("warm", look=(lerp(.6, -.35, up), lerp(.7, 0, up)), lid=lerp(.55, .7, up) + .15 * bump(t, T_SPAS, .4), smile=lerp(.35, 1.0, sml),
           closed=blinks(t, (43.75, 44.95)))
    lean_add = .03 * math.sin(t * 2.1) + .05 * put * (1 - rel) - .03 * up
    head_add = -.06 + .06 * (1 - up) - .03 * bump(t, T_SPAS, .45)
    full, parts = C1.dima_parts(e, "card", hands=hands, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, lean_add=lean_add, head_add=head_add)
    wf, wn = full["wrist"]["f"], full["wrist"]["n"]
    # раскрытая открытка лежит наклонно (как в конце s01)
    card = PR.card(CARD_POS[0], CARD_POS[1], C1.CARD_K * .9, -6, 1.0, "blank", seed=1)
    q = .55
    card = f'<g transform="translate(0 {CARD_YB:.2f}) scale(1 {q:.4f}) translate(0 {-CARD_YB:.2f})">{card}</g>'
    fthumb = people.hand_svg("dima", wf, (.75, -.65), k=C1.SC, far=True, curl=(.55, .6, .62, .65), thumb=.55, seed=720)
    # сложенное письмо: в кулаке → на странице открытки (в наклоне стола, как открытка)
    held = np.array(wn) + dn * 58 * C1.SC
    lp = lerp2((float(held[0]), float(held[1])), LET_IN, sm(t, T_HOCH + .3, T_HOCH + .42)) if put > .97 else (float(held[0]), float(held[1]))
    lay = sm(t, T_HOCH + .1, T_HOCH + .4)
    let = PR.letter(lp[0], lp[1], .44, lerp(-18 + 3 * math.sin(t * 2), -8, lay), write=1.0, fold=1.0, seed=17, sy=lerp(1.0, .6, lay))
    if rel < .5:          # пока держит: пальцы поверх края письма (хват)
        let += people.hand_svg("dima", wn, hands["n"]["dir"], k=C1.SC, curl=hands["n"]["curl"], thumb=hands["n"]["thumb"], seed=721)
    items_mid = card + fthumb + let
    # кот: подходит справа по полу, присед, толчок, на «спасибо» запрыгивает на стол рядом с открыткой
    cat = ""
    ju = clamp((t - T_JUMP0) / (T_JUMP1 - T_JUMP0))
    cst = dict(look=(-.4, -.2), blink=blinks(t, (44.25,)), tail=8 * math.sin(t * 2.3), ear=2 * math.sin(t * 3.1), turn=-.3 + .3 * sm(t, T_JUMP1, T_JUMP1 + .3),
               smile=1.0 if t > T_JUMP1 else 0.0, flame_e=1.1 + .5 * bump(t, T_JUMP1, .5))
    if t < T_JUMP0:
        wu = sm(t, 43.6, T_JUMP0 - .05)
        x = lerp(CAT18_FLOOR[0] + 260, CAT18_FLOOR[0], wu)
        cat = people.cat_walk(x, CAT18_FLOOR[1], CAT18_K, t, dict(cst, rot=0.0), period=.45) if wu < .999 else CAT.draw(*CAT18_FLOOR, CAT18_K, cst, t)
    else:
        cat = people.cat_jump(CAT18_FLOOR, CAT18_DESK, CAT18_K, ju, t, cst)
    sc = R.desk_scene(t, "day", drawer=0.0)
    world = C1.room_layers(t, sc, parts, items_mid, cat)
    # камера: ровный откат от крупного плана к общему, как кадр 0 хука (s01 начинается с этого плана и влетает)
    cx0, cy0, s0 = R.CAM_DESK_CLOSE
    u = sm(t, T_A18 - .2, 45.3)
    s = lerp(s0 * 1.04, s0 / 1.4, u)
    cx = lerp(cx0 + 30, cx0 + 50, u) + 4 * math.sin(t * 1.7)
    cy = lerp(cy0 + 30, cy0 + 60, u)
    set_ink(s)
    g = f'<g transform="{lib.cam(cx, cy, s, 0.0)}">{"".join(world)}</g>'
    return g, "#e6dcc0"


FRAMES["s18"] = s18


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
