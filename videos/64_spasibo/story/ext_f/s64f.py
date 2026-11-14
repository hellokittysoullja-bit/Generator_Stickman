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
T_SPAS = wt("спасибо")             # 44.61 улыбка, кот на столе


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
    Wn = (cx - 170 * K16 + 210 * K16 * stroke, back_y - 30 - lift)
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
    world = [sc["bg"], sc["sofa"], mob, parts["legs"], parts["pelvis"], parts["arm_f"], parts["body"], cat_svg, parts["arm_n"], sc["front"], purr]
    # камера: медленный откат, «дыхание»
    u = sm(t, T_A16 - .2, 41.44)
    z = 1.72 - .22 * u + .012 * math.sin(t * 2.1)
    ccx = HX + 200 - 20 * u
    ccy = 900 + 40 * u + 4 * math.sin(t * 1.7)
    set_ink(z)
    g = f'<g transform="{lib.cam(ccx, ccy, z, .7 - 1.0 * u)}">{"".join(world)}</g>'
    return whip(g, t, T_A16), "#e6dcc0"


FRAMES = {"s16": s16}


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
