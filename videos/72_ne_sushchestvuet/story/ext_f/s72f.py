"""Рилс 72 «СДВГ не существует», группа F — кот: мозг под хвостом, «и всё», призыв, лёд на шаги.
s15 (19.06–20.45, графика на бумаге): мозг-малыш смотрит на башню-диплом, «честно» (19.20) подпрыгивает от испуга, «пугается»
    (19.56) извилины дыбом, глаза-блюдца, бежит за кота и прячется за его хвост; кот мягко прикрывает мозг хвостом и спокойно смотрит
    на башню.
s19 (25.30–26.42): у костра Дима откидывается на бревно, кот садится вплотную, «всё» (25.52) — тёплый медленный кивок, огонёк
    вспыхивает, костёр подкидывает искры.
s20 (26.42–28.62, хлёст): призыв — кот близко у костра тянет лапу к зрителю, «висит» (27.66) мешок на ветке гнёт её, на чистом
    куске ночного неба пером пишется «кот» (common/hand_kot.py).
s21 (28.62–30.00): мешок падает, внутри глыба льда, «разломаю» (29.0) кот раскалывает её, «шаги» (29.66) кубики в ряд к зрителю.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Ночь у костра — common/room.py, Дима — common/people.py, кот —
common/cat.py, предметы — common/props.py, «кот» — common/hand_kot.py; здесь только хореография и камера.
Надписей, букв и цифр нет (кроме «кот»)."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(0, os.path.join(STORY, "ext_e"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
import h72 as H  # noqa: E402
import hand_kot  # noqa: E402
from h72 import blinks, bump, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
from lib import INK, blob, clamp, ellipse_pts, line  # noqa: E402

FRAMES = {}
PAPER = "#e6dcc0"
BG = "#05080f"


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.update(kw)
    return e


def world_fire(t, u=1.0, mode="wide"):
    sc = R.fire_scene(t, u, mode)
    back = "".join(sc[k] for k in ("sky", "bg", "ground", "stones_back"))
    return sc, back


def warm(svg, t, u=1.0):
    return R.fire_tint(svg, t, u, 1.0)


def warm_cat(svg, t, u=1.0):
    """Кот у огня: тинт слабее, чем у Димы, — шерсть остаётся почти чёрной (как в группе E)."""
    return R.fire_tint(svg, t, u, .3)


def burst(cx, cy, t, t0, n=18, h=640.0, spread=150.0, seed=0):
    """Костёр подкидывает искры: тёплые точки летят вверх веером и гаснут (одна вспышка на t0)."""
    q0 = t - t0
    if q0 <= 0 or q0 > 1.3:
        return ""
    import numpy as np
    r = np.random.RandomState(seed)
    o = []
    for i in range(n):
        dx0 = r.uniform(-spread, spread)
        sp = r.uniform(.6, 1.15)
        q = clamp(q0 / (1.1 * sp))
        if q >= 1:
            continue
        x = cx + dx0 * (.3 + 1.1 * q) + 26 * math.sin(i * 1.7 + q * 7)
        y = cy - h * sp * (q ** .75)
        rr = (5 + 4 * r.uniform()) * (1 - q)
        col = "#FFD24A" if i % 3 else "#FFF2C0"
        o.append(blob(ellipse_pts(x, y, rr, rr * 1.4, 8), col, min(1.0, 2.5 * (1 - q))))
    return "".join(o)


# ═════════════════════════ s15: мозг прячется за хвост кота (графика на бумаге) ═════════════════════════
T_A15 = 19.06
T_CHES, T_PUG = wt(44), wt(45)                    # 19.20 подскок, 19.56 бежит прятаться
GROUND15 = 1240.0
TOWER15 = (230.0, GROUND15 - 10)
CAT15 = (600.0, GROUND15)
CAT15_K = 1.45
BRAIN_K = .9
B_START, B_HIDE = 350.0, 815.0


def ground15(t):
    """Бумага: линия земли пером и пара штрихов травы — без предметов и букв."""
    o = [blob([(-400, GROUND15 + 4), (1500, GROUND15 + 4), (1500, 2400), (-400, 2400)], "#ddd0ae", .55)]
    o.append(line([(-300, GROUND15 + 6), (300, GROUND15 + 2), (900, GROUND15 + 7), (1400, GROUND15 + 3)], 4.4, INK, taper=.1, wmin=.5, seed=1501))
    for j, gx in enumerate((-120, 60, 470, 1010, 1180)):
        sw = 4 * math.sin(t * 2.2 + j)
        o.append(line([(gx, GROUND15 + 4), (gx + 6 + sw, GROUND15 - 26)], 3, "#7a8a4a", taper=.6, wmin=.2, seed=1510 + j))
        o.append(line([(gx + 12, GROUND15 + 4), (gx + 22 + sw, GROUND15 - 18)], 3, "#7a8a4a", taper=.6, wmin=.2, seed=1520 + j))
    return "".join(o)


def s15(t):
    # мозг: стоит, смотрит на башню и дрожит → «честно» подскок → «пугается» бежит за кота, прячется за хвост, выглядывает
    hop = -150 * bump(t, T_CHES - .02, .34)
    run = sm(t, T_PUG + .02, T_PUG + .42)
    bx = lerp(B_START, B_HIDE, run)
    if 0 < run < 1:          # бег вприпрыжку
        hop += -38 * abs(math.sin(math.pi * (t - T_PUG) / .13))
    hop += -4 * abs(math.sin(t * 9))          # переминается с первого кадра
    if t < T_CHES:
        expr, look = "peek", (-.8, -.2)
    elif t < T_PUG + .5:
        expr, look = "wide", (-.7 if run < .3 else .7, -.1)
    else:
        calm = sm(t, 20.15, 20.4)
        expr, look = ("scared" if calm < .5 else "peek"), (-.9, -.3)
    brain = PR.brain_kid(bx, GROUND15, BRAIN_K, expr, hop, t, look=look, seed=1, blink=blinks(t, (19.0,)))
    # башня-диплом вдали, чуть нависает и шуршит верхом
    tower = PR.paper_tower(TOWER15[0], TOWER15[1], .78, lean=4 + 1.5 * math.sin(t * 1.7), flutter=.5 + .3 * math.sin(t * 3), t=t, seed=2)
    # кот: сидит справа от башни, смотрит на неё спокойно; на «пугается» короткий взгляд на мозг, потом хвост мягко накрывает его
    cover = sm(t, T_PUG + .3, T_PUG + .8)
    glance = bump(t, T_PUG + .05, .55)
    cx, cy = CAT15
    st = dict(turn=-.45 + .5 * glance, look=(lerp(-.7, .6, glance), .05), blink=blinks(t, (19.38, 20.3), .2), tail=-6 + 4 * math.sin(t * 2.4) + 15 * cover,
              ear=5 * bump(t, T_CHES, .25) + 2 * math.sin(t * 3.1), tilt=-3 + 2 * math.sin(t * 1.3) + 4 * cover, smile=1.0 if cover > .6 else 0.0,
              flame_e=1.0 + .4 * cover + .2 * math.sin(t * 5))
    cat = CAT.draw(cx, cy, CAT15_K, st, t)
    shadow = blob(ellipse_pts(cx + 30, GROUND15 + 4, 190, 16, 16), "#000000", .12)
    world = [ground15(t), tower, shadow, brain, cat]
    # испуг: штрихи-лучики вокруг мозга на подскоке
    q = bump(t, T_CHES, .4)
    if q > .02:
        cy_b = GROUND15 - 140 + hop * BRAIN_K
        for j in range(6):
            a = math.radians(-160 + 28 * j)
            r0 = 120 + 30 * q
            world.append(line([(bx + math.cos(a) * r0, cy_b + math.sin(a) * r0), (bx + math.cos(a) * (r0 + 46 * q), cy_b + math.sin(a) * (r0 + 46 * q))],
                              4.6, INK, taper=.5, wmin=.2, seed=1530 + j, op=min(1.0, q * 2)))
    # камера: тряска на подскоке, потом спокойный дрейф к коту
    u = sm(t, T_A15 - .2, 20.65)
    d = sm(t, T_PUG, 20.5)
    s = lerp(1.58, 1.48, sm(t, T_A15 - .2, T_CHES)) + .12 * d
    ccx = lerp(505, 520, u) + 130 * d
    ccy = lerp(1040, 1030, u) + 30 * d
    sx_, sy_ = shake(t, T_CHES, 14)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx + sx_, ccy + sy_, s, lerp(-.8, .6, u))}">{"".join(world)}</g>'
    return g, PAPER


FRAMES["s15"] = s15


# ═════════════════════════ s19: «и всё» — Дима откидывается, кот вплотную, тёплый кивок, огонёк и костёр вспыхивают ═════════════════════════
T_A19 = 25.30
T_I19, T_VSE = wt(57), wt(58)                 # 25.36, 25.52
HIP19 = R.DIMA_LOG
CAT19_A, CAT19_B = (640.0, 1506.0), (548.0, 1502.0)
CAT19_K = .74


def s19(t):
    burn = 1.0 + .25 * bump(t, T_VSE + .05, .7)
    sc, back = world_fire(t, 1.0, "laptop")
    hx, hy = HIP19
    feet = people.knees_kw(hx, hy, 1.0, tight=.35)["feet"]
    # Дима: с ноутбуком на коленях (экран к нему, светится) → «и» выдыхает → «всё» откидывается назад, дальняя рука упирается в бревно
    # за спиной, плечи опускаются, лёгкая улыбка, глаза прикрываются
    back_u = sm(t, T_I19 - .08, T_VSE + .38)
    LAP = (hx + 160, hy - 52)
    lp = H.laptop_side(LAP[0], LAP[1], .78, 1.0, on=1.0, t=t, seed=2)
    Wn = (LAP[0] + 20 - 26 * back_u, LAP[1] - 24 + 6 * back_u + 2 * math.sin(t * 2.2))
    Wf = lerp2((LAP[0] - 20, LAP[1] - 10), (hx - 150, hy + 8), back_u)
    hf = {"dir": lerp2((1, .3), (-.5, 1), back_u), "curl": (.3, .3, .35, .4), "thumb": .3}
    hn = {"dir": (1, .3), "curl": (.25, .3, .35, .4), "thumb": .35}
    if back_u < .35:
        e = ex("surprise", mouth="smile", smile=.8, open=0.0, look=(.6, .45), lid=1.0, bags=False)
    else:
        e = ex("lean_rest", closed=.25 * bump(t, 26.05, .5), look=(.55, .1))
    lean = lerp(.1, -.2, back_u) + .012 * math.sin(t * 2.1) + .02 * bump(t, T_VSE + .3, .5)
    ha = lerp(.05, -.1, back_u) + .02 * math.sin(t * 1.6)
    kw = dict(feet=feet, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, hands={"f": hf, "n": hn}, lean_add=lean, head_add=ha,
              shrug=.12 * (1 - back_u))
    full = people.dima(hx, hy, 1.0, e, None, **kw)
    parts = {k_: people.dima(hx, hy, 1.0, e, None, layers=(k_,), **kw)["svg"] for k_ in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    body = warm("".join(parts[k_] for k_ in ("legs", "pelvis", "arm_f", "body")), t)
    arm_n = warm(parts["arm_n"], t)
    hd = full["head"]
    light = PR.glow(hd[0] + 80, hd[1] + 30, 100, .4, "#DDE8FF", ry=118) + PR.glow(lp["screen"][0] - 30, lp["screen"][1], 80, .35, "#DDE8FF")
    # кот: два шага к Диме и садится вплотную к его голени; «всё» — медленный тёплый кивок, глаза щёлочками, огонёк вспыхивает
    wu = sm(t, T_A19 - .2, T_I19 + .06)
    cx, cy = lerp2(CAT19_A, CAT19_B, wu)
    nod = people.cat_nod(t, T_VSE - .04, .75, .34)
    warm_u = sm(t, T_VSE - .05, T_VSE + .25)
    st = dict(turn=lerp(-.4, -.15, warm_u), look=(lerp(-.7, -.2, warm_u), lerp(-.35, .15, warm_u)), tail=-4 + 6 * math.sin(t * 2.2),
              blink=max(blinks(t, (25.2,)), .55 * warm_u), smile=1.0 if warm_u > .4 else 0.0, drop=nod, tilt=-4 * warm_u + 2 * math.sin(t * 1.4),
              ear=3 * math.sin(t * 3.1) - 4 * warm_u, flame_e=1.0 + .9 * bump(t, T_VSE + .02, .7) + .2 * warm_u)
    if 0 < wu < 1:
        cat = people.cat_walk(cx, cy, CAT19_K, t, st, period=.3)
    else:
        st.update(sy=1 - .04 * bump(t, T_I19 + .06, .3), rot=-3 * warm_u)
        cat = CAT.draw(cx, cy, CAT19_K, st, t)
    cat = warm_cat(cat, t)
    cshadow = blob(ellipse_pts(cx + 10, cy + 4, 104, 12, 14), "#000000", .25)
    sparks = burst(R.FIRE[0], R.FIRE[1] - 120, t, T_VSE + .02, seed=19)
    world = [back, sc["fire"], sparks, sc["stones_front"], sc["log"], body, lp["svg"], arm_n, light, cshadow, cat]
    # камера: медленный отъезд, искры уходят вверх
    u = sm(t, T_A19 - .2, 26.7)
    s = lerp(1.48, 1.3, u) + .02 * bump(t, T_VSE, .5)
    ccx = lerp(290, 330, u) + 4 * math.sin(t * 1.5)
    ccy = lerp(1050, 1075, u) + 3 * math.sin(t * 1.9)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(.3, -.3, u))}">{"".join(world)}</g>'
    warmth = f'<rect width="1080" height="1920" fill="#ff9a40" opacity="{.05 + .06 * (burn - 1) * 4 * sc["light"]:.3f}"/>'
    return g + warmth, BG


FRAMES["s19"] = s19


# ═════════════════════════ общее s20–s21: ветка над огнём гнётся, мешок без своей ветки ═════════════════════════
def fire_branch(t, u, mode, bend=0.0):
    """fire_scene с веткой, прогнутой вниз в точке мешка на bend px (ветку рисует room.py через R.BRANCH; здесь только её
    середина опускается на время кадра — сам room.py не меняется)."""
    b0 = R.BRANCH
    R.BRANCH = (b0[0], b0[1] + bend)
    try:
        return world_fire(t, u, mode)
    finally:
        R.BRANCH = b0


def sack_only(x, y, k=1.0, sway=0.0, t=0.0):
    """props.hanging_sack без его собственной ветки и листьев (ветка уже в сцене): всё выше узла верёвки срезано, верёвка
    дотянута до точки ветки."""
    cid = lib.uid("sk")
    lib.DEFS.append(f'<clipPath id="{cid}"><rect x="{x - 600:.1f}" y="{y + 34 * k:.1f}" width="1200" height="{900 * k:.1f}"/></clipPath>')
    a = math.radians(sway)
    rope = line([(x, y - 6), (x + math.sin(a) * 44 * k, y + math.cos(a) * 44 * k)], 4 * k, "#8A6A3E", taper=.05, wmin=.8, seed=7291)
    return rope + f'<g clip-path="url(#{cid})">{PR.hanging_sack(x, y, k, sway=sway, t=t, seed=1)}</g>'


def dima_bg(t, seed_t=0.0):
    """Дима на бревне с ноутбуком на коленях (экран к нему), откинулся — как в конце s19, дышит."""
    hx, hy = R.DIMA_LOG
    feet = people.knees_kw(hx, hy, 1.0, tight=.35)["feet"]
    LAP = (hx + 160, hy - 52)
    lp = H.laptop_side(LAP[0], LAP[1], .78, 1.0, on=1.0, t=t, seed=2)
    Wn = (LAP[0] - 6, LAP[1] - 18 + 2 * math.sin(t * 2.2))
    Wf = (hx - 150, hy + 8)
    e = ex("lean_rest", closed=blinks(t, (seed_t,)), look=(.55, .1))
    kw = dict(feet=feet, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)},
              hands={"f": {"dir": (-.5, 1), "curl": (.3, .3, .35, .4), "thumb": .3}, "n": {"dir": (1, .3), "curl": (.25, .3, .35, .4), "thumb": .35}},
              lean_add=-.13 + .012 * math.sin(t * 2.1), head_add=-.08 + .02 * math.sin(t * 1.6))
    full = people.dima(hx, hy, 1.0, e, None, **kw)
    parts = {k_: people.dima(hx, hy, 1.0, e, None, layers=(k_,), **kw)["svg"] for k_ in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    body = warm("".join(parts[k_] for k_ in ("legs", "pelvis", "arm_f", "body")), t)
    hd = full["head"]
    light = PR.glow(hd[0] + 80, hd[1] + 30, 100, .4, "#DDE8FF", ry=118)
    return body + lp["svg"] + warm(parts["arm_n"], t) + light


# ═════════════════════════ s20: призыв — кот тянет лапу к зрителю, мешок на ветке, «кот» на небе ═════════════════════════
T_A20 = 26.42
T_NAP, T_KOM, T_VIS = wt(59), wt(61), wt(63)       # 26.42, 27.00, 27.66
KOT_T0, KOT_DUR = 27.2, .6                          # дописано к 27.8, звук «слово дописано» 27.95
KOT20 = (455.0, 318.0, 1.42)                        # чистое небо R.SKY_CLEAN: за буквами ни звёзд, ни веток
CAT20 = (770.0, 1740.0)
CAT20_K = 2.05


def sack_motion(t):
    """Покачивание мешка и прогиб ветки: тихо качается с кадра 0, на «висит» тяжело опускается и раскачивается."""
    v = sm(t, T_VIS - .08, T_VIS + .2)
    sway = 6 * math.sin(t * 2.6) + 9 * H.decay(t, T_VIS, 3.2, 1.6) + 3 * v
    bend = 10 + 22 * v + 8 * H.decay(t, T_VIS + .05, 4.0, 2.4)
    return sway, bend


def s20(t):
    sway, bend = sack_motion(t)
    sc, back = fire_branch(t, 1.0, "branch", bend)
    sack = sack_only(R.BRANCH[0], R.BRANCH[1] + bend, .9, sway, t)
    dima = dima_bg(t, 27.1)
    # кот: смотрит на Диму → «Напиши» морда к зрителю, правая лапа приглашающе тянется к камере, подушечкой вверх-вперёд;
    # «висит» — ухо и короткий взгляд вверх на мешок; когда «кот» дописан — щурится
    tu = sm(t, T_NAP - .04, T_NAP + .3)
    reach = lib.ease_out(clamp((t - (T_NAP + .05)) / .45), 2.2)
    beck = .08 * math.sin(max(0.0, t - T_KOM) * 7.5) * sm(t, T_KOM - .1, T_KOM + .1) * (1 - sm(t, T_VIS - .2, T_VIS))
    up = bump(t, T_VIS - .05, .6)
    done = sm(t, KOT_T0 + KOT_DUR, KOT_T0 + KOT_DUR + .25)
    st = dict(turn=lerp(-.55, 0.0, tu) + .15 * up, look=(lerp(-.8, 0.0, tu) + .3 * up, lerp(.1, -.05, tu) - .9 * up),
              tilt=lerp(-7, 2, tu) + 3 * math.sin(t * 1.5) - 4 * up, blink=max(blinks(t, (26.3, 28.3)), .45 * done),
              smile=1.0 if (tu > .7 and up < .3) else 0.0, tail=-15 + 6 * math.sin(t * 2.3),
              ear=6 * bump(t, T_VIS, .3) + 2 * math.sin(t * 3.2), perk=.5 * bump(t, T_NAP, .5) + .6 * up,
              paw=.15 + .85 * reach + beck, paw_dx=50, flame_e=1.0 + .4 * done)
    cx, cy = CAT20
    cat = warm_cat(CAT.draw(cx, cy, CAT20_K, st, t), t)
    cshadow = blob(ellipse_pts(cx + 30, cy + 6, 270, 24, 16), "#000000", .3)
    kot = hand_kot.kot(t, KOT_T0, KOT_DUR, KOT20[0], KOT20[1], KOT20[2], col="#F3E7C8")
    world = [back, sack, sc["fire"], sc["stones_front"], sc["log"], dima, kot, cshadow, cat]
    # камера: хлёст, лёгкий наезд на кота, перо видно; мини-удар, когда слово дописано
    u = sm(t, T_A20 - .2, 28.8)
    s = lerp(.98, 1.05, u) + .02 * bump(t, KOT_T0 + KOT_DUR, .35)
    ccx = lerp(548, 562, u) + 4 * math.sin(t * 1.3)
    ccy = lerp(905, 915, u) + 3 * math.sin(t * 1.6)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(.4, -.3, u))}">{"".join(world)}</g>'
    warmth = f'<rect width="1080" height="1920" fill="#ff9a40" opacity="{.05 * sc["light"]:.3f}"/>'
    return whip(g + warmth, t, T_A20), BG


FRAMES["s20"] = s20


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
