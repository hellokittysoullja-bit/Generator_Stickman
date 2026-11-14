"""Рилс 71 «два лагеря», группа B: кухня и друг.
s09 (14.30–16.48, whip): кухня днём; Дима и друг за столом друг напротив друга. «Дима спросил» (14.38–15.12) Дима наклоняется,
    разводит ладонями; «у друга» (15.25) друг (сидел к окну) поворачивается к нему с кружкой; «и тот честно сказал» (15.58–16.40)
    пожимает плечами, простодушно улыбается. Камера: панорама от Димы к другу, лёгкий наезд.
s10 (16.48–18.80): друг крупнее, Дима на краю кадра. «что даже не думает» (16.52–17.28) стучит пальцем по виску, качает головой;
    «об этом» (17.31–17.60) пьёт из кружки; «просто встаёт» (17.78–18.48) мгновенно встаёт, стул крутится волчком, друг уже у
    раковины моет кружку; Дима с открытым ртом провожает его глазами. Камера дёргается за другом, потом на лицо Димы.
s18 (30.40–31.50): кухня, Дима у столешницы по пояс: «налить» (30.44) наклоняет графин, струя в стакан; «воды» (30.78) стакан полон,
    глоток с закрытыми глазами. Камера: лёгкий наезд, на глотке мини-подъём.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Кухня — common/room.py (группа C), предметы — props.py, люди — people.py."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import clamp, ease_in, ease_io, ease_out, line, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?:«»").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def frame_svg(body, cx, cy, s, rot, bg):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>')


def whip_in(t, t0, dur=.2):
    u = clamp((t - t0) / dur)
    e = 1 - ease_out(u, 3)
    return -150 * e, -2.0 * e


def _rot(p, deg):
    a = math.radians(deg)
    return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))


def base_from_point(Pt, local, k, rot, hs):
    hx, hy = _rot((local[0] * hs, local[1]), rot)
    return Pt[0] - hx * k, Pt[1] - hy * k


def mirror(svg_, x):
    return f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{svg_}</g>'


MUG_HANDLE = (88.0, -70.0)
KM = .95          # кружки


def mug_left(x, y, k, rot=0.0, **kw):
    """Кружка ручкой ВЛЕВО (к руке, когда человек смотрит вправо)."""
    return mirror(P.coffee_mug(x, y, k, -rot, **kw), x)


def held_mug(who, W, s, rot=0.0, seed=0, steam=0.0, t=0.0, fill=.7, col="blue"):
    """Кружка в ближней руке (запястье W, человек смотрит вправо): ладонь за ручкой, пальцы поверх."""
    H = (W[0] + 46 * s * 1.15, W[1] - 4 * s)
    back, front = people.handle_grip(who, H, k=s, side=-1, seed=960 + seed)
    bx, by = base_from_point(H, MUG_HANDLE, KM * s, rot, -1)
    return back + mug_left(bx, by, KM * s, rot, col=col, fill=fill, steam=steam, t=t, seed=seed) + front


# ─── кухня ───
DX, DY = R.KS_SIT_L[0] - 70, R.KS_SIT_L[1]          # таз Димы (смотрит вправо); стулья сцены рисуем сами — шире
FX, FY = R.KS_SIT_R[0] + 70, R.KS_SIT_R[1]          # таз друга (смотрит влево — рисуется неотражённым и зеркалится вокруг FX)
BS = .9
FEET_D = {"n": ((DX + 300 * BS, R.KS_FLOOR - 52), 0.0), "f": ((DX + 250 * BS, R.KS_FLOOR - 50), 0.0)}
SCF = BS * people.HEIGHT["friend"]
FEET_F = {"n": ((FX + 290 * SCF, R.KS_FLOOR - 52), 0.0), "f": ((FX + 245 * SCF, R.KS_FLOOR - 50), 0.0)}
FEET_F_AWAY = {"n": ((FX - 230 * SCF, R.KS_FLOOR - 52), 0.0), "f": ((FX - 270 * SCF, R.KS_FLOOR - 50), 0.0)}


def talk(t, words, e, amp=.55):
    """Рот говорит: открыт на слогах слов (words — список начал)."""
    o = 0.0
    for w0 in words:
        u = (t - w0) / .2
        if 0 < u < 1:
            o = max(o, math.sin(math.pi * u))
    e = dict(e)
    if o > .05:
        e.update(mouth="talk", open=amp * o, smile=e.get("smile", .2))
    return e


def blink(t, e, times):
    e = dict(e)
    for b in times:
        if b < t < b + .12:
            e["closed"] = max(e.get("closed", 0), math.sin(math.pi * (t - b) / .12))
    return e


def dima_parts(e, pose=None, u_pose=None, layers=("legs", "pelvis", "arm_f", "body", "arm_n"), **kw):
    kw.setdefault("feet", FEET_D)
    return {k: people.dima(DX, DY, BS, e, pose, u_pose=u_pose, layers=(k,), **kw)["svg"] for k in layers}


def friend_parts(e, pose=None, u_pose=None, away=False, x=None, y=None, **kw):
    """Слои друга. away=False — смотрит влево (к Диме), True — сидит вполоборота к окну (смотрит вправо)."""
    x = FX if x is None else x
    y = FY if y is None else y
    kw.setdefault("feet", FEET_F_AWAY if away else {k: ((v[0][0] - FX + x, v[0][1]), v[1]) for k, v in FEET_F.items()})
    out = {}
    for k in ("legs", "pelvis", "arm_f", "body", "arm_n"):
        f = people.person("friend", x, y, BS, e, pose, u_pose=u_pose, layers=(k,), **kw)
        out[k] = f["svg"]
        out["_f"] = f
    return out


def kitchen_layers(sc, legs, seats_front, pelvis, table, upper, items_front="", chairs_back=None):
    return (sc["bg"] + (sc["chairs_back"] if chairs_back is None else chairs_back) + legs + seats_front + pelvis + table + upper + items_front)


# ═══════════════════════════════ s09: вопрос другу ═══════════════════════════════
T9_DIMA = wt("дима", 14.0)       # 14.38
T9_SPR = wt("спросил")           # 14.77
T9_DRU = wt("друга")             # 15.25
T9_I = wt("и", 15.4)             # 15.58
T9_CH = wt("честно")             # 15.80
T9_SK = wt("сказал")             # 16.13
TURN9 = T9_DRU - .02


def s09(t):
    lib.dyn_begin()
    sc = R.kitchen_scene(t, "day")
    # Дима: наклон и ладони вопросом
    up = ease_out(clamp((t - T9_DIMA) / .28), 2)
    bob = .04 * math.sin((t - T9_DIMA) * 9) * up
    ed = people.EXPR["dima"]["plea"]
    ed = dict(ed, look=(.7, -.1) if t > TURN9 else (.6, -.25))
    ed = talk(t, [T9_DIMA, T9_SPR, T9_SPR + .18], ed, .5) if t < T9_DRU else ed
    ed = blink(t, ed, [14.2, 15.9])
    dp = dima_parts(ed, "nose_wall", ("ask_palms", up), lean_add=.06 * up + bob, head_add=.04 * math.sin(t * 3))
    mug_d = P.coffee_mug(R.KS_MUG_L[0], R.KS_MUG_L[1], KM, col="red", fill=.6, steam=.6, t=t, seed=1)
    # друг: до «друга» уткнулся в кружку (голова вниз, глаза в кружку), на «друга» поднимает голову к Диме
    away = t < TURN9
    if away:
        ef = dict(people.EXPR["friend"]["sip"], look=(.3, .8))
        ef = blink(t, ef, [14.6])
        upose = ("mug_drink", .35 + .1 * math.sin(t * 2.5))
        sh = 0.0
        hd = .16
    else:
        sh = 0.0
        for t0 in (T9_CH, T9_SK):
            sh = max(sh, math.sin(math.pi * clamp((t - t0) / .32)))
        ef = dict(people.EXPR["friend"]["shrug" if t > T9_I else "simple"], look=(.5, 0))
        ef = talk(t, [T9_I, T9_CH, T9_SK], ef, .45)
        ef = blink(t, ef, [15.45])
        upose = ("mug_hold", 0.0)
        hd = .16 * (1 - ease_out(clamp((t - TURN9) / .14), 2)) - .08 * sh
    hop = -26 * math.sin(math.pi * clamp((t - TURN9) / .16))
    lift = 40 * sh
    fp = friend_parts(ef, "mug_hold", u_pose=upose, shrug=sh, head_add=hd, hands={"n": {"kind": "none"}},
                      arms={"f": ("ang", 0.2, 0.25 + .5 * sh)} if not away else {"f": ("ang", 0.2, 0.25)})
    Wn = fp["_f"]["wrist"]["n"]
    mug_f = held_mug("friend", Wn, SCF, rot=(-14 if away else 0) + 4 * math.sin(t * 4), seed=2, steam=.5, t=t, col="blue")
    del lift
    friend_upper = f'<g transform="translate(0 {hop:.1f})">' + mirror(fp["arm_f"] + fp["body"] + mug_f + fp["arm_n"], FX) + "</g>"
    f_legs = mirror(fp["legs"], FX)
    f_pel = mirror(fp["pelvis"], FX)
    # штрихи поворота
    turn_fx = ""
    if 0 < t - TURN9 < .22:
        u = (t - TURN9) / .22
        for j in range(3):
            a0 = math.radians(200 + 40 * j)
            r = 230 + 20 * j
            turn_fx += line([(FX + r * math.cos(a0 + .3), 560 + r * .5 * math.sin(a0 + .3)), (FX + r * math.cos(a0), 560 + r * .5 * math.sin(a0)),
                             (FX + r * math.cos(a0 - .3), 560 + r * .5 * math.sin(a0 - .3))], 6 * (1 - u) + 1, INK, taper=.6, wmin=.2, seed=9100 + j)
    cl = R._side_chair(DX, DY, 1.0, 1, seed=0)
    cr = R._side_chair(FX, FY, 1.0, -1, seed=10)
    body = (sc["bg"] + cl["back"] + cr["back"] + dp["legs"] + f_legs + cl["seat"] + cr["seat"] + dp["pelvis"] + f_pel + sc["table"] + mug_d
            + dp["arm_f"] + dp["body"] + dp["arm_n"] + friend_upper + turn_fx)
    # камера: от Димы к другу, лёгкий наезд
    a = ease_io(clamp((t - (T9_DRU - .45)) / .6))
    cx = lerp(380, 700, a)
    cy = lerp(880, 860, a)
    s = lerp(1.22, 1.3, ease_io(clamp((t - 14.1) / 2.5)))
    wx, wr = whip_in(t, 14.10)
    ex, ey = P.shake(t, TURN9, 8, .22, seed=9)
    return frame_svg(body, cx - wx - ex, cy - ey, s, wr + .4 * math.sin(t * 1.3), R.KS_PAL["wall"])


# ═══════════════════════════════ s10: «просто встаёт» ═══════════════════════════════
T10_CHTO = wt("что", 16.4)       # 16.52
T10_DUM = wt("думает")           # 17.00
T10_OB = wt("об")                # 17.31
T10_PR = wt("просто", 17.6)      # 17.78
T10_VST = wt("встаёт")           # 17.96
STAND_X = 1010.0                 # у раковины (таз; смотрит влево, к раковине)
SINK = (900.0, 940.0)


def friend_chair(t, spin_t0):
    """Стул друга: стоит, после spin_t0 крутится волчком (затухая)."""
    ch = R._side_chair(FX, FY, 1.0, -1, seed=10)
    if t < spin_t0:
        return ch["back"], ch["seat"]
    u = t - spin_t0
    ang = 1500 * (1 - math.exp(-2.2 * u)) / 2.2 * 2.2          # градусы: быстро, затухая
    c = math.cos(math.radians(ang))
    cx = FX + 25
    g = f'<g transform="translate({cx:.1f} 0) scale({c:.4f} 1) translate({-cx:.1f} 0)">'
    lines_ = ""
    if u < .6:
        for j in range(3):
            yy = FY - 300 + 110 * j
            lines_ += line([(cx - 220, yy + 20), (cx - 120, yy - 10), (cx + 120, yy - 10), (cx + 220, yy + 20)], 5 * (1 - u / .6) + .6, INK,
                           taper=.6, wmin=.2, seed=10200 + j, op=.8)
    return g + ch["back"] + "</g>", g + ch["seat"] + "</g>" + lines_


def s10(t):
    lib.dyn_begin()
    sc = R.kitchen_scene(t, "day")
    cl = R._side_chair(DX, DY, 1.0, 1, seed=0)
    # Дима: застыл, рот открывается на «просто встаёт», провожает глазами
    gap = ease_out(clamp((t - T10_PR) / .25), 2)
    ed = dict(people.EXPR["dima"]["puzzled"])
    if gap > 0:
        ed = dict(people.EXPR["dima"]["gape"], open=.4 + .6 * gap, look=(lerp(.6, .95, gap), -.15 * gap))
    ed = blink(t, ed, [16.9])
    dp = dima_parts(ed, "nose_wall", lean_add=-.04 * gap, head_add=-.05 * gap + .02 * math.sin(t * 2))
    mug_d = P.coffee_mug(R.KS_MUG_L[0], R.KS_MUG_L[1], KM, col="red", fill=.6, steam=.6, t=t, seed=1)
    chb, chs = friend_chair(t, T10_VST)
    stand = t >= T10_VST
    if not stand:
        # стучит по виску (три тычка), качает головой; «об этом» — глоток из кружки
        tap = 0.0
        for w0 in (T10_CHTO + .05, wt("даже"), wt("не", 16.8), T10_DUM):
            tap = max(tap, math.sin(math.pi * clamp((t - w0) / .14)))
        drink = ease_io(clamp((t - T10_OB + .05) / .2)) * (1 - ease_io(clamp((t - T10_PR + .08) / .15)))
        ef = dict(people.EXPR["friend"]["simple" if drink < .3 else "sip"], look=(.5, 0))
        ef = talk(t, [T10_CHTO, wt("даже"), T10_DUM], ef, .4) if drink < .3 else ef
        shake_h = .07 * math.sin((t - T10_CHTO) * 13) * clamp((t - T10_CHTO) / .2) * (1 - drink)
        if drink < .02:
            pose, upose = "temple", None
            arms = None
            hands = None
            fl = people.person("friend", FX, FY, BS, ef, "temple", feet=FEET_F, head_add=shake_h, layers=("body",))
            hx, hy = fl["head"]
            arms = {"n": ("ik", (hx + 55 * SCF, hy + 18 * SCF - 10 * tap), 1)}
            fp = friend_parts(ef, "temple", head_add=shake_h, arms=arms)
            items = ""
            mug_tbl = P.coffee_mug(R.KS_MUG_R[0], R.KS_MUG_R[1], KM, col="blue", fill=.7, steam=.5, t=t, seed=2)
            upper = mirror(fp["arm_f"] + fp["body"] + fp["arm_n"], FX)
        else:
            fp = friend_parts(ef, "mug_hold", u_pose=("mug_drink", drink), hands={"n": {"kind": "none"}}, arms={"f": ("ang", 0.2, 0.25)})
            Wn = fp["_f"]["wrist"]["n"]
            items = held_mug("friend", Wn, SCF, rot=-28 * drink, seed=2, steam=.4, t=t, col="blue", fill=.7)
            mug_tbl = ""
            upper = mirror(fp["arm_f"] + fp["body"] + items + fp["arm_n"], FX)
        f_low = mirror(fp["legs"], FX)
        body = (sc["bg"] + cl["back"] + chb + dp["legs"] + f_low + cl["seat"] + chs + dp["pelvis"] + mirror(fp["pelvis"], FX) + sc["table"]
                + mug_d + mug_tbl + dp["arm_f"] + dp["body"] + dp["arm_n"] + upper)
    else:
        # мгновенно встал и уже у раковины: моет кружку под краном
        u = t - T10_VST
        hipy = R.KS_FLOOR - 52 - (people.LEG_LEN - 12) * SCF
        x = lerp(FX + 40, STAND_X, ease_out(clamp(u / .12), 2))
        jump = -60 * math.sin(math.pi * clamp(u / .14))
        ef = dict(people.EXPR["friend"]["chill"], look=(.5, .4), hair=2 * math.sin(t * 9))
        ef = blink(t, ef, [18.45])
        scrub = math.sin(u * 22) * clamp((u - .1) / .1)
        # смотрит влево к раковине: рисуем вправо и зеркалим вокруг x
        loc_sink = (2 * x - SINK[0], SINK[1])
        tgt_n = (loc_sink[0] - 10 + 18 * scrub, loc_sink[1] - 60 + 10 * scrub)
        tgt_f = (loc_sink[0] - 40, loc_sink[1] - 50)
        kw = people.stand_kw(x, hipy + jump, BS, "friend", spread=40)
        fr = people.person("friend", x, hipy + jump, BS, ef, "rest", lean_add=.16, arms={"n": ("ik", tgt_n, -1), "f": ("ik", tgt_f, -1)},
                           hands={"n": {"kind": "none"}, "f": {"curl": (.5, .5, .55, .6), "thumb": .5, "dir": (1, .3)}}, **kw)
        fr_n = people.person("friend", x, hipy + jump, BS, ef, "rest", lean_add=.16, arms={"n": ("ik", tgt_n, -1), "f": ("ik", tgt_f, -1)},
                             hands={"n": {"kind": "none"}}, layers=("arm_n",), **kw)
        Wn = fr_n["wrist"]["n"]
        mug = held_mug("friend", Wn, SCF, rot=-60 + 10 * scrub, seed=2, t=t, col="blue", fill=0)
        water = P.pour_stream(SINK[0] - 4, SINK[1] - 118, SINK[0] - 2, SINK[1] - 30, t=t, w=9, col=P.C_WATER, seed=3) if u > .05 else ""
        foam = "".join(f'<circle cx="{SINK[0] - 30 + 22 * j + 6 * math.sin(t * 8 + j):.1f}" cy="{SINK[1] - 40 - 14 * ((j * 3) % 4) - 10 * math.sin(t * 6 + j):.1f}" '
                       f'r="{8 + 3 * (j % 3)}" fill="#FFFFFF" stroke="{INK}" stroke-width="2.4"/>' for j in range(5)) if u > .15 else ""
        smear = ""
        if u < .1:
            for j in range(4):
                yy = hipy - 300 + 160 * j
                smear += line([(FX - 40, yy + 30), (x - 120, yy)], 7, INK, taper=.8, wmin=.1, seed=10300 + j, op=.8)
        fr_body = fr["svg"].replace(fr_n["svg"], "")
        friend = mirror(fr["svg"] if False else fr_body + water + mug + fr_n["svg"], x)
        body = (sc["bg"] + cl["back"] + chb + dp["legs"] + cl["seat"] + chs + dp["pelvis"] + sc["table"] + mug_d + dp["arm_f"] + dp["body"]
                + dp["arm_n"] + friend + foam + smear)
    # камера: друг крупно, Дима на краю → рывок за другом к раковине → на лицо Димы
    a = ease_io(clamp((t - 16.28) / 1.4))
    cx, cy, s = lerp(640, 670, a), lerp(820, 800, a), lerp(1.24, 1.3, a)
    j = ease_out(clamp((t - T10_VST) / .2), 3)
    cx = lerp(cx, 800, j)
    d = ease_io(clamp((t - 18.25) / .4))
    cx, cy, s = lerp(cx, 380, d), lerp(cy, 660, d), lerp(s, 1.6, d)
    ex, ey = P.shake(t, T10_VST, 14, .3, seed=10)
    return frame_svg(body, cx - ex, cy - ey, s, -.5 * j + .4 * d, R.KS_PAL["wall"])


# ═══════════════════════════════ s18: налить воды ═══════════════════════════════
T18_NAL = wt("налить")           # 30.44
T18_VOD = wt("воды")             # 30.78
D18 = (610.0, R.KS_FLOOR - 52 - (people.LEG_LEN - 12) * BS)
CNT = 940.0                      # верх столешницы
GL18 = (930.0, CNT - 2, 1.0)     # стакан на столешнице (дно)
JUG_HANDLE = (96.0, -140.0)      # центр ручки графина (ручка справа, дно в (0, 0))
KJ = .95


def jug_left(x, y, k, rot, fill):
    """Графин ручкой ВЛЕВО: (x, y) — дно, rot — наклон (по часовой — носик вправо-вниз)."""
    inner = mirror(P.jug(0, 0, k, fill, seed=3), 0)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f})">{inner}</g>'


def s18(t):
    lib.dyn_begin()
    sc = R.kitchen_scene(t, "day")
    x, y = D18
    pour = ease_io(clamp((t - T18_NAL + .1) / .2)) * (1 - ease_io(clamp((t - T18_VOD - .1) / .16)))
    gl_fill = .05 + .9 * ease_in(clamp((t - T18_NAL - .05) / (T18_VOD + .02 - T18_NAL)), 1.2)
    drink = ease_io(clamp((t - T18_VOD - .2) / .3))
    sip = clamp((t - T18_VOD - .5) / .5)
    ed = dict(people.EXPR["dima"]["focus_smile"], look=(.75, .55))
    if drink > .5:
        ed = dict(people.EXPR["dima"]["bliss"])
    ed = blink(t, ed, [30.3])
    # графин в ближней руке (до глотка), стакан — дальняя рука придерживает, потом ближняя к губам
    jrot = 48 * pour
    jh_rest = (x + 300, CNT - 120)
    jh = (jh_rest[0] + 10 * pour, jh_rest[1] - 70 * pour)
    jx, jy = base_from_point(jh, JUG_HANDLE, KJ, jrot, -1)
    gx, gy, gk = GL18
    if drink < .02:
        arms = {"n": ("ik", (jh[0] - 20, jh[1] + 6), -1), "f": ("ik", (gx - 70, gy - 60), -1)}
        hands = {"n": {"kind": "none"}, "f": {"dir": (1, .1), "curl": (.6, .65, .7, .7), "thumb": .6}}
    else:
        f0 = people.dima(x, y, BS, ed, "rest", layers=("body",), lean_add=-.05 * drink)
        hx, hy = f0["head"]
        mouth = (hx + 110, hy + 120)
        hold = (lerp(gx - 40, mouth[0] - 30, drink), lerp(gy - 70, mouth[1] + 10, drink))
        arms = {"n": ("ik", hold, -1), "f": ("ang", .15, .2)}
        hands = {"n": {"kind": "none"}}
    kw = people.stand_kw(x, y, BS, "dima", spread=50)
    lean = .1 * (1 - drink) - .08 * drink
    fd = people.dima(x, y, BS, ed, "rest", lean_add=lean, head_add=.08 * pour - .22 * drink + .03 * math.sin(t * 3), arms=arms, hands=hands,
                     layers=("legs", "pelvis", "arm_f", "body"), **kw)
    fn = people.dima(x, y, BS, ed, "rest", lean_add=lean, head_add=.08 * pour - .22 * drink, arms=arms, hands=hands, layers=("arm_n",), **kw)
    Wn = fn["wrist"]["n"]
    items = ""
    if drink < .02:
        jug_s = jug_left(jx, jy, KJ, jrot, .8 - .3 * gl_fill)
        bk, fr = people.handle_grip("dima", jh, k=BS, side=-1, seed=990, hh=88)
        glass = P.glass(gx, gy, gk, 0, gl_fill, t, splash=.6 * pour * (gl_fill > .85), seed=4)
        stream = ""
        if pour > .3:
            sp = _rot((78 * -1 * 1.0, -232), jrot)        # носик (зеркально: справа) — в мире от дна
            spx, spy = jx + (-sp[0]) * KJ * 0 + _rot((78, -232), jrot)[0] * KJ, jy + _rot((78, -232), jrot)[1] * KJ
            stream = P.pour_stream(spx, spy, gx + 4, gy - 140 * gk * gl_fill - 8, t=t, w=12 * pour, col=P.C_WATER, seed=5, bend=.2)
        items_back = glass
        items = bk + jug_s + stream + fr
        body = sc["bg"] + fd["svg"] + items_back + items + fn["svg"]
    else:
        GR = 40 * gk
        H = (Wn[0] + GR + 50 * BS * .5, Wn[1] - 4)
        bk, fr = people.grip_svg("dima", H, GR, -1, k=BS * 1.05, seed=995)
        rot = -40 * clamp((drink - .4) / .6) - 18 * sip
        bx, by = base_from_point(H, (0.0, -70.0), gk, rot, 1)
        gfill = gl_fill - .25 * sip
        jug_s = jug_left(jx + 0, CNT - 2, KJ, 0, .5)
        body = sc["bg"] + jug_s + fd["svg"] + bk + P.glass(bx, by, gk, rot, gfill, t, seed=4) + fr + fn["svg"]
        if sip > 0:
            body += P.sparkles(Wn[0] + 60, Wn[1] - 160, 1.0, clamp(sip * 2), t, seed=18, n=3, r=70)
    # камера: лёгкий наезд, на глотке мини-подъём
    a = ease_io(clamp((t - 30.2) / 1.5))
    cx, cy, s = lerp(760, 740, a), lerp(700, 680, a), lerp(1.45, 1.56, a)
    cy -= 40 * ease_io(clamp((t - T18_VOD - .2) / .4))
    return frame_svg(body, cx, cy, s, -.4 + .6 * a, R.KS_PAL["wall"])


SHOTS = {"s09": s09, "s10": s10, "s18": s18}


def frame(sid, t):
    return SHOTS[sid](t)
