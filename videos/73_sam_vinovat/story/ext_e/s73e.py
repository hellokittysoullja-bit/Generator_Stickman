"""Рилс 73 «Ты сам виноват», группа E — тепло на кровати и конверт.
s10 (13.10–14.90): тёплый свет ночника, Дима сидит в кровати под одеялом, кот сидит на одеяле, рядом судейский молоток из s02.
    «Ты не виноват» (13.49) кот спокойно сталкивает лапой молоток — он падает с кровати вниз из кадра; «что начинать» Дима выдыхает;
    «тяжело» (14.45) плечи опускаются, кот прислоняется боком к его руке.
s11 (14.90–16.05): общий план, Дима и кот сидят рядом на краю кровати в пятне ночника, луна в окне, на стене пыльный конверт.
    «один» (15.45) кот бодает Диму головой в плечо, Дима улыбается краешком рта и кладёт ладонь коту на спину, огонёк разгорается.
s13 (17.40–18.85, хлёст): пробковая доска с пыльным конвертом в паутине, Дима стоит у доски, кот у ног. «одно» (17.58) кот дует на
    конверт — облако пыли, паучок убегает по нитке вверх; «маленькое» Дима снимает конверт двумя пальцами; «действие» (18.30) отгибает
    клапан — внутри чистый лист.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, Дима — common/people.py, кот — common/cat.py,
предметы — common/props.py; здесь только хореография и камера. Надписей, букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from h73 import blinks, bump, flame_world, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
from lib import blob, clamp, ease_in, ease_out, ellipse_pts, line  # noqa: E402

BG = "#3a2418"
FRAMES = {}
LAYERS_UP = ("pelvis", "arm_f", "body", "arm_n")


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.setdefault("bags", False)
    e.update(kw)
    return e


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')


def puff(head, t, t0, dur=.7, side=1, col="#f3e6d2"):
    """Выдох: три мягких пятна у рта растут и тают."""
    q = clamp((t - t0) / dur)
    if q <= 0 or q >= 1:
        return ""
    hx, hy = head
    o = ""
    for j in range(3):
        x0 = hx + side * (140 + 70 * q + j * 26)
        y0 = hy + 62 - 10 * q + (j - 1) * 14
        r = (14 + 10 * j) * (.5 + .7 * q)
        o += blob(ellipse_pts(x0, y0, r * 1.3, r, 12), col, .45 * math.sin(math.pi * q))
    return o


WARM_ = '<rect x="-4000" y="-4000" width="9000" height="9000" fill="#ff9a40" opacity="{op}" style="mix-blend-mode:soft-light"/>'


# ═════════════════════════ s10: «Ты не виноват» — молоток с кровати ═════════════════════════
T_A10 = 13.10
T_TY, T_VIN, T_CHTO, T_NACH, T_TYAZH = wt(34), wt(36), wt(37), wt(38), wt(39)      # 13.16, 13.49, 13.95, 14.05, 14.45
BT = R.BED73_TOP
DIMA10 = (1790.0, BT + 20)          # таз Димы у подушки (изголовье справа), сидит лицом влево, ноги под одеялом
CAT10 = (1420.0, BT - 70)           # кот сидит на одеяле у его колен
CAT10_K = 1.0
GAV10 = (1272.0, BT - 112)           # молоток лежит на одеяле: (x, y) — конец рукояти, боёк слева


def mir(p, x0):
    return (2 * x0 - p[0], p[1])


def s10(t):
    sc = R.bedroom(t, "lamp", "bed")
    P = sc["P"]
    # Дима: сидит, плечи сначала подняты (зажат); «что начинать» — выдох, «тяжело» плечи опускаются, голова клонится, тёплая улыбка
    drop = sm(t, T_TYAZH - .05, T_TYAZH + .4)
    sh = .5 * (1 - drop) + .03 * math.sin(t * 2.2)
    exh = bump(t, T_CHTO, .55)
    if t < T_CHTO - .05:
        e = ex("sag73", look=(.4, .4), lid=.5, closed=blinks(t, (13.02,)))
    elif t < T_TYAZH + .1:
        e = ex("exhale73", closed=.6 * exh)
    else:
        e = ex("smile73", look=(.5, .55), closed=blinks(t, (14.8,)))
    hx, hy = DIMA10
    # руки (цели в координатах до отражения: фигура рисуется лицом вправо и отражается вокруг таза): кисти лежат на одеяле на коленях
    Wn = (hx + 190 + 10 * drop, BT - 56 + 16 * drop)
    Wf = (hx + 150, BT - 50 + 10 * drop)
    hn = {"dir": (1, .25), "curl": (.25, .3, .35, .4), "thumb": .35, "spread": .1}
    kw = dict(arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, hands={"f": hn, "n": hn}, lean_add=.04 + .1 * drop + .012 * math.sin(t * 2.0),
              head_add=.08 * drop - .03 * exh, shrug=sh, flip=True)
    full = people.dima(hx, hy, 1.0, e, None, **kw)
    parts = {k: R.warm_tint(people.dima(hx, hy, 1.0, e, None, layers=(k,), **kw)["svg"], .6) for k in LAYERS_UP}
    # кот: смотрит на молоток → «Ты не виноват» левая (от зрителя) передняя лапа толкает его (та же лапа, вторая на одеяле) → лапа
    # назад → «тяжело» кот переступает к Диме и прислоняется боком к его руке, жмурится
    push = sm(t, T_TY + .02, T_VIN + .04) * (1 - sm(t, T_VIN + .25, T_VIN + .5))
    lean_c = sm(t, T_TYAZH - .12, T_TYAZH + .35)
    cx = CAT10[0] + 45 * lean_c
    cy = CAT10[1] - 4 * lean_c
    look_d = sm(t, T_VIN + .3, T_TYAZH - .1)
    st = dict(turn=lerp(-.55, .5, look_d), look=(lerp(-.8, .7, look_d), lerp(.5, -.2, lean_c)),
              tilt=lerp(-4, 10, lean_c) + 2 * math.sin(t * 1.7), blink=max(blinks(t, (13.98,)), .6 * lean_c), smile=1.0 if lean_c > .4 else 0.0,
              paw_l=.3 * push, paw_l_dx=200, rot=8 * lean_c - 3 * push, tail=-8 + 6 * math.sin(t * 2.3), ear=3 * math.sin(t * 2.9),
              walk=(t - T_TYAZH + .12) * 2.2 if .02 < lean_c < .98 else None, flame_e=1.0 + .5 * lean_c)
    cat = R.warm_tint(CAT.draw(cx, cy, CAT10_K, st, t), .25)
    flx, fly = flame_world(cx, cy, CAT10_K, st["tail"])
    cat += PR.glow(flx, fly - 40, 80, .4, "#ffb347")
    # молоток: лежит; на «виноват» лапа толкает — скользит влево, переваливается через край кровати и падает вниз из кадра
    tp = T_VIN - .03
    if t < tp:
        gx, gy, gr = GAV10[0], GAV10[1], -6.0
    else:
        q = t - tp
        slide = 150 * ease_out(clamp(q / .22), 2)
        fall = max(0.0, q - .2)
        gx = GAV10[0] - slide - 160 * fall
        gy = GAV10[1] + .5 * 4200 * fall * fall
        gr = -6 - 220 * fall
    gav = R.warm_tint(PR.gavel(gx, gy, .62, gr, t), .5)
    world = [sc["bg"], sc["pillow"], parts["pelvis"], parts["arm_f"], parts["body"], sc["blanket"], gav, cat, parts["arm_n"],
             puff(full["head"], t, T_CHTO - .02, .75, side=-1)]
    # камера: медленный дрейф вправо, на падении молотка короткий сдвиг вниз 2 %
    u = sm(t, T_A10 - .2, 15.1)
    s = 1.3 + .03 * u + .01 * math.sin(t * 1.8)
    ccx = lerp(1520, 1560, u) + 4 * math.sin(t * 1.3)
    ccy = 960 + 3 * math.sin(t * 1.6) + 30 * bump(t, T_VIN + .25, .5)
    set_ink(s)
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.4, .3, u))}">{"".join(world)}</g>', BG


FRAMES["s10"] = s10


# ═════════════════════════ s11: «и ты не один» — кот бодает, ладонь на спине ═════════════════════════
T_A11 = 14.90
T_I11, T_ODIN = wt(40), wt(43)              # 15.01, 15.45
DIMA11 = (700.0, BT + 6)                     # таз Димы на краю кровати у изножья, лицом вправо, ступни на полу; окно с луной слева
CAT11 = (1010.0, BT - 40)                    # кот сидит на кровати рядом, чуть глубже (за его коленями)
CAT11_K = 1.05


def s11(t):
    sc = R.bedroom(t, "lamp", "wide")
    bump_ = bump(t, T_ODIN - .04, .55)
    near = sm(t, T_ODIN - .14, T_ODIN + .04)
    pet = sm(t, T_ODIN + .1, T_ODIN + .42)
    flare = sm(t, T_ODIN, T_ODIN + .3) * (1 - .4 * sm(t, 15.9, 16.3))
    # кот: сидит рядом и смотрит на Диму; на «один» подаётся к нему и бодает головой в плечо (глаза закрыты), потом жмурится под ладонью
    cx = CAT11[0] - 55 * near - 25 * bump_
    cy = CAT11[1]
    st = dict(turn=lerp(-.5, -.8, near), look=(-.8, -.4), tilt=lerp(-4, -16, near) - 6 * bump_, rot=lerp(0, -8, near) - 6 * bump_,
              blink=max(blinks(t, (14.95,)), bump_, .55 * pet), smile=1.0, tail=-6 + 8 * math.sin(t * 2.1),
              ear=-5 * bump_ + 2 * math.sin(t * 3), perk=.2 * pet, flame_e=1.0 + 1.3 * flare, sy=1 + .06 * bump_)
    cat = R.warm_tint(CAT.draw(cx, cy, CAT11_K, st, t), .25)
    flx, fly = flame_world(cx, cy, CAT11_K, st["tail"])
    glow = PR.glow(flx, fly - 50, 80 + 90 * flare, .4 + .45 * flare, "#ffb347") + PR.sparkles(flx, fly - 70, .9, flare, t, seed=11, n=4, r=70)
    # Дима: сидит, смотрит вниз; на «один» его качнуло назад от толчка, улыбка краешком рта, ближняя ладонь ложится коту на спину
    hx, hy = DIMA11
    if t > T_ODIN - .02:
        e = ex("smile73", look=(.8, .6), closed=blinks(t, (15.9,)))
    else:
        e = ex("sag73", look=(.6, .5), lid=.55, closed=blinks(t, (15.15,)))
    back = (cx - 5 * CAT11_K, cy - 168 * CAT11_K)
    rest_n = (hx + 215, hy - 24)
    Wn = lerp2(rest_n, (back[0] - 24, back[1] + 10), pet)
    hn = {"dir": (1, .45), "curl": (.12, .15, .2, .25), "spread": .12, "thumb": .25} if pet > .5 else {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}
    feet = {"n": ((hx + 300, R.FL73 - 40), 0.0), "f": ((hx + 250, R.FL73 - 36), 0.0)}
    kw = dict(feet=feet, arms={"f": ("ik", (hx + 175, hy - 20), -1), "n": ("ik", Wn, -1)},
              hands={"f": {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}, "n": hn},
              lean_add=.04 - .07 * bump_ + .03 * pet + .01 * math.sin(t * 2.2), head_add=.05 * pet - .04 * bump_)
    dima = {k: R.warm_tint(people.dima(hx, hy, 1.0, e, None, layers=(k,), **kw)["svg"], .6) for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    world = [sc["bg"], sc["pillow"], sc["blanket"], dima["arm_f"], dima["pelvis"], dima["body"], cat, dima["legs"], dima["arm_n"], glow]
    # камера: медленный наезд 5 %, на «один» тёплая вспышка (огонёк) и мини-толчок
    u = sm(t, T_A11 - .2, 16.25)
    s = lerp(.86, .9, u) + .015 * bump(t, T_ODIN, .4)
    ccx = lerp(640, 680, u) + 4 * math.sin(t * 1.4)
    ccy = lerp(960, 945, u) + 3 * math.sin(t * 1.7)
    set_ink(s)
    flash = f'<rect width="1080" height="1920" fill="#ffcf80" opacity="{.16 * bump(t, T_ODIN + .05, .5):.3f}" style="mix-blend-mode:screen"/>'
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.3, .3, u))}">{"".join(world)}</g>{flash}', BG


FRAMES["s11"] = s11


# ═════════════════════════ s13: одно маленькое действие — конверт снят и открыт ═════════════════════════
T_A13 = 17.40
T_ODNO, T_MAL, T_DEY = wt(49), wt(50), wt(51)       # 17.58, 17.82, 18.30
PIN13 = R.BOARD73_PIN                                # кнопка с пыльным конвертом
ENV_K13 = 1.15
CAT13 = (-650.0, R.FL73 - 8)                         # кот сидит у ног Димы, под доской справа
CAT13_K = 1.0


def s13(t):
    sc = R.bedroom(t, "lamp", "board")
    P = sc["P"]
    px, py = PIN13
    hip_x = px - 330
    sc_d = people.HEIGHT["dima"]
    hip_y = R.FL73 - 26 - (people.LEG_LEN - 12) * sc_d
    # кот дует на конверт: вдох (грудь шире) → выдох струйкой вверх → облако пыли с конверта, паучок убегает вверх
    inhale = bump(t, T_ODNO - .22, .3)
    blow = bump(t, T_ODNO - .02, .5)
    dust_t = T_ODNO + .06
    # Дима: смотрит на конверт; «маленькое» — ближняя рука вверх щепотью, двумя пальцами снимает конверт с кнопки,
    # опускает к груди; «действие» — отгибает клапан, внутри чистый лист, лёгкая улыбка
    reach = sm(t, T_MAL - .05, T_MAL + .18)
    down = sm(t, T_MAL + .2, T_DEY - .04)
    openu = ease_out(clamp((t - (T_DEY - .03)) / .26), 2)
    if openu > .3:
        e = ex("smile73", look=(.55, .6), closed=blinks(t, (18.75,)))
    elif reach > .05:
        e = ex("unpin73", look=(.5, lerp(-.6, .5, down)))
    else:
        e = ex("lost73", look=(.55, -.5), closed=blinks(t, (17.3,)))
    if down < .02:
        kw = people.pose_kw("unpin73", hip_x, hip_y, 1.0)
        rest = people.pose_kw("sag73", hip_x, hip_y, 1.0)
        # до «маленького» рука внизу, потом поднимается к кнопке
        nA = rest["arms"]["n"]
        kw["arms"] = dict(kw["arms"])
        if reach < .99:
            tgt = kw["arms"]["n"][1]
            low = (hip_x + 120, hip_y + 40)
            kw["arms"]["n"] = ("ik", lerp2(low, tgt, reach), -1) if reach > .01 else nA
        if reach < .3:
            kw["hands"] = {"n": {"curl": (.25, .3, .35, .4), "thumb": .3}}
    else:
        kw = people.mix_pose("unpin73", "open73", down, hip_x, hip_y, 1.0)
    kw.update(people.stand_kw(hip_x, hip_y, 1.0))
    kw["lean"] = kw["lean"] + .01 * math.sin(t * 2.0)
    fig = people.figure("dima", hip_x, hip_y, 1.0, e, **kw)
    grab = people.hand_pos(fig, "n", 62)
    parts = {k: people.figure("dima", hip_x, hip_y, 1.0, e, layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    parts = {k: R.warm_tint(v, .6) for k, v in parts.items()}
    # конверт: качается от выдоха кота; снят — едет за щепотью (верх конверта у пальцев), у груди клапан отгибается
    sw = 9 * math.exp(-3 * max(0.0, t - dust_t)) * math.sin(2 * math.pi * 2.2 * max(0.0, t - dust_t)) if t > dust_t else 2 * math.sin(t * 3)
    held = reach > .97
    if not held:
        env = PR.pinned_envelope(px, py, ENV_K13, swing=sw, dust=lerp(1.0, .4, sm(t, dust_t, dust_t + .4)), web=1.0 - sm(t, dust_t, dust_t + .3),
                                 open_u=0.0, t=t, seed=1)
        pin = ""
    else:
        ex_, ey_ = grab
        ex_, ey_ = ex_ + 6, ey_ + 6
        sheet = ""
        if openu > .2:     # чистый лист выглядывает из раскрытого конверта
            sheet = PR.letter(ex_, ey_ + 30 * ENV_K13 - 40 * openu, .62 * ENV_K13, rot=-2, write=0.0, seed=7)
        env = sheet + PR.pinned_envelope(ex_, ey_, ENV_K13, swing=-4 * down, dust=.25, web=0.0, open_u=openu, t=t, seed=1, pin=False)
        pin = PR.push_pin(px, py, ENV_K13)
    env = R.light_tint(env, P)
    # паучок: висит на нитке под конвертом; на выдох — проворно бежит по нитке вверх и прячется за край доски
    up = sm(t, dust_t, dust_t + .55)
    sp = PR.spider(px + 150, R.BOARD73[1] + 60, .95, drop=lerp(150, -40, up), t=t, seed=2, look=-.6) if up < .99 else ""
    web = PR.cobweb(R.BOARD73_WEB[0] + 30, R.BOARD73_WEB[1] + 30, 1.1, tremble=blow, t=t, ang=0, span=90, seed=4)
    puffs = PR.dust_puff(px, py + 60, 1.25, clamp((t - dust_t) / .55), seed=3)
    # кот: смотрит вверх на конверт, вдыхает и дует, потом смотрит на Диму и щурится
    cx, cy = CAT13
    look_d = sm(t, T_MAL + .2, T_DEY)
    st = dict(turn=lerp(-.2, -.5, look_d), look=(lerp(-.3, -.8, look_d), lerp(-1.0, -.3, look_d)), tilt=lerp(-10, -4, look_d) + 2 * math.sin(t * 1.7),
              sx=1 + .05 * inhale, sy=1 + .04 * inhale - .02 * blow, blink=max(.7 * blow, blinks(t, (18.6,))), smile=1.0 if t > T_DEY else 0.0,
              tail=-6 + 7 * math.sin(t * 2.2), ear=3 * math.sin(t * 2.6), flame_e=1.0 + .3 * blow)
    cat = R.warm_tint(CAT.draw(cx, cy, CAT13_K, st, t), .25)
    # струйка выдоха: три волнистые линии от рта кота вверх к конверту
    air = ""
    if blow > .03:
        mx, my = cx - 2, cy - (CAT.CBOT - 1128) * CAT13_K
        for j in range(3):
            q = clamp(blow * 1.5 - j * .15)
            pts = [(mx + (j - 1) * 14 + 30 * math.sin(i * .9 + t * 18 + j) * (i / 8), my - i * 90 * q) for i in range(9)]
            pts = [(x_ + (px - mx) * (i / 8) * q, y_) for i, (x_, y_) in enumerate(pts)]
            air += line(pts, 7.0, "#fbf0dc", taper=.6, wmin=.3, seed=9300 + j, op=.85 * blow)
    world = [sc["bg"], web, pin, sp if not held else "", env if not held else "", puffs, parts["legs"], parts["pelvis"], parts["arm_f"], parts["body"],
             env if held else "", parts["arm_n"], sp if held else "", cat, air]
    # камера: хлёст вправо, затем медленный наезд к конверту
    u = sm(t, T_A13 - .1, 19.05)
    s = lerp(1.12, 1.2, u) + .02 * bump(t, dust_t, .35)
    ccx = lerp(-930, -900, u) + 4 * math.sin(t * 1.4)
    ccy = lerp(930, 880, u) + 3 * math.sin(t * 1.7)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(.4, -.3, u))}">{"".join(world)}</g>'
    return whip(g, t, T_A13, side=1), BG


FRAMES["s13"] = s13
