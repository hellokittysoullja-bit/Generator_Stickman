"""Рилс 72 «СДВГ не существует», группа E — озарение и маленький шаг (ночь у костра).
s11 (12.40–14.50): Дима на бревне уткнулся в колени; «понял» (13.02) поднимает голову, в глазах отблеск огня; «ленивый» (13.88)
    выдыхает — дымное лицо над костром рассыпается искрами вверх; кот обходит костёр шагом и садится рядом с Димой.
s16 (20.45–22.08, хлёст): Дима стоит перед башней-дипломом у огня, «соберись» (21.36) тужится как атлет — башня не шелохнулась,
    один лист лениво слетает; кот рядом медленно качает головой.
s17 (22.08–24.15): кот вытаскивает лапой из основания башни клочок с горошину, кладёт Диме на ладонь; Дима присел, смотрит;
    «смешно» (23.49) прыскает от смеха, плечи трясутся, кот щурится.
s18 (24.15–25.30): Дима на бревне с ноутбуком на коленях, экран к Диме (зритель видит крышку сзади); «Открыть» (24.19) крышка одним
    пальцем, «файл» (24.80) холодный свет на лице, глаза шире, удивлённая улыбка.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Ночь у костра — common/room.py, Дима — common/people.py, кот —
common/cat.py, башня, клочок, ноутбук — common/props.py; здесь только хореография и камера. Надписей, букв и цифр нет."""
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
import h72 as H  # noqa: E402
from h72 import blinks, bump, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
from lib import blob, clamp, ellipse_pts, line  # noqa: E402

FRAMES = {}
BG = "#05080f"
LAYERS = ("legs", "pelvis", "arm_f", "body", "arm_n")


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
    """Кот у огня: тинт слабее, чем у Димы, — шерсть остаётся почти чёрной (#2a2d30–#3b4143), а не коричневой."""
    return R.fire_tint(svg, t, u, .3)


def puff(head, t, t0, dur=.7, side=1, seed=0, col="#c9d2e0"):
    """Выдох: облачко пара у рта — три мягких пятна, растут и тают (не дуги: дуги читались как буква)."""
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


def burst(cx, cy, t, t0, n=22, h=700.0, seed=0):
    """Искры вверх из рассыпавшегося дыма: тёплые точки-штрихи летят и гаснут."""
    q0 = t - t0
    if q0 <= 0 or q0 > 1.4:
        return ""
    import numpy as np
    r = np.random.RandomState(seed)
    o = []
    for i in range(n):
        dx0, dy0 = r.uniform(-230, 230), r.uniform(-300, 120)
        sp = r.uniform(.6, 1.2)
        q = clamp(q0 / (1.2 * sp))
        if q >= 1:
            continue
        x = cx + dx0 * (1 + .4 * q) + 30 * math.sin(i + q * 6)
        y = cy + dy0 - h * sp * (q ** .8)
        rr = (6 + 4 * r.uniform()) * (1 - q)
        col = "#FFD24A" if i % 3 else "#FFF2C0"
        o.append(blob(ellipse_pts(x, y, rr, rr * 1.4, 8), col, min(1.0, 2.5 * (1 - q))))
    return "".join(o)


# ═════════════════════════ s11: «понял» — поднимает голову, дым рассыпается, кот садится рядом ═════════════════════════
T_A11 = 12.40
T_PON, T_LEN = wt(28), wt(32)                 # 13.02, 13.88
HIP11 = (R.DIMA_LOG[0], R.DIMA_LOG[1])
SMOKE11 = (R.FIRE[0] + 110, R.FIRE[1] - 250)
CAT_PATH = [(900.0, 1330.0, .62), (830.0, 1470.0, .76), (700.0, 1560.0, .88), (610.0, 1575.0, .94)]
T_CW0, T_CW1 = 12.55, 14.05                   # кот идёт; потом садится


def path_pt(P, u):
    n = len(P) - 1
    s = clamp(u) * n
    i = min(n - 1, int(s))
    f = s - i
    return tuple(P[i][j] + (P[i + 1][j] - P[i][j]) * f for j in range(3))


def s11(t):
    sc, back = world_fire(t, 1.0, "wide")
    hx, hy = HIP11
    # Дима: подбородок в коленях → «понял» поднимает голову → выдох, плечи опускаются
    up = sm(t, T_PON - .12, T_PON + .3)
    rel = sm(t, T_LEN - .1, T_LEN + .5)
    kw = people.mix_pose("chin_knees", "lift_head", up, hx, hy, 1.0)
    feet = people.knees_kw(hx, hy, 1.0, tight=1.0)["feet"]
    if up < .5:
        e = ex("downcast", closed=blinks(t, (12.7,)))
    elif rel < .3:
        e = ex("dawn", look=(.45, -.25), closed=blinks(t, (13.5,)))
    else:
        e = ex("warm", look=(.5, -.15), mouth="o" if bump(t, T_LEN, .5) > .3 else "smile", open=.25 * bump(t, T_LEN, .5), smile=.6 * rel)
    lean = kw["lean"] - .06 * rel + .012 * math.sin(t * 2.1)
    ha = kw["head_ang"] + .02 * math.sin(t * 1.7) + .06 * bump(t, T_PON + .05, .35)
    full = people.dima(hx, hy, 1.0, e, None, feet=feet, arms=kw["arms"], hands=kw["hands"], lean_add=lean, head_add=ha)
    dima = warm(full["svg"], t)
    glint = ""
    if up > .5:          # отблеск огня в глазах
        gx, gy = full["head"]
        for dx in (18, 92):
            glint += blob(ellipse_pts(gx + dx + 6, gy - 20, 5, 5, 8), "#FFC24A", .9 * (up - .5) * 2)
    # дымное лицо над костром рассыпается на «ленивый»
    fade = sm(t, T_LEN - .05, T_LEN + .55)
    smoke = people.smoke_figure("self", SMOKE11[0], SMOKE11[1], .5, u=1.0, t=t, fade=fade, seed=11) if fade < .99 else ""
    sparks = burst(SMOKE11[0], SMOKE11[1] - 260, t, T_LEN, seed=11)
    # кот: шагает вокруг огня спереди-справа и садится рядом с Димой
    wu = clamp((t - T_CW0) / (T_CW1 - T_CW0))
    cx, cy, ck = path_pt(CAT_PATH, lib.ease_io(wu) if wu < 1 else 1.0)
    sit = sm(t, T_CW1 - .05, T_CW1 + .25)
    st = dict(turn=lerp(-.5, -.2, sit), look=(lerp(-.6, -.8, sit), -.2), tail=6 * math.sin(t * 2.3), flame_e=1.1 + .3 * sit,
              blink=blinks(t, (14.3,)), ear=4 * math.sin(t * 3.0))
    if wu < 1:
        cat = people.cat_walk(cx, cy, ck, t, st, period=.42)
    else:
        st.update(sy=1 - .05 * bump(t, T_CW1, .3))
        cat = CAT.draw(cx, cy, ck, st, t)
    cat = warm_cat(cat, t)
    shadow = blob(ellipse_pts(cx + 10, cy + 4, 150 * ck, 14 * ck, 14), "#000000", .25)
    world = [back, smoke, sc["fire"], sparks, sc["stones_front"], sc["log"], dima, glint, puff(full["head"], t, T_LEN + .05, seed=1101),
             shadow, cat]
    # камера: от лица Димы мягкий отъезд, чтобы вошёл кот; тёплый свет растёт
    u = sm(t, T_A11 - .2, 14.7)
    s = lerp(1.62, 1.22, u) + .015 * math.sin(t * 1.9) + .03 * bump(t, T_PON, .4)
    ccx = lerp(400, 450, u) + 6 * math.sin(t * 1.3)
    ccy = lerp(1000, 1170, u) + 5 * math.sin(t * 1.6)
    set_ink(s)
    glow = sc["light"]
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(.6, -.4, u))}">{"".join(world)}</g>'
    warmth = f'<rect width="1080" height="1920" fill="#ff9a40" opacity="{.04 + .05 * u * glow:.3f}"/>'
    return g + warmth, BG


FRAMES["s11"] = s11



# ═════════════════════════ s16: «соберись» — тужится перед башней, башня не шелохнулась ═════════════════════════
T_A16 = 20.45
T_RAB, T_SOB = wt(46), wt(48)                 # 20.52, 21.36
GROUND16 = 1450.0
DX16 = 600.0
HIP16_Y = GROUND16 - (people.LEG_LEN - 12)
TOWER16 = (990.0, GROUND16 - 5)
TOWER_K = 1.35
CAT16 = (400.0, 1540.0)
CAT16_K = .82


def sheet(x, y, rot, k=1.0, seed=0):
    """Один чистый лист (слетает с башни): белый четырёхугольник с тушью, без букв."""
    pts = lib.T([(-150, -40, 1), (130, -56, 1), (160, 44, 1), (-130, 58, 1)], x, y, k, rot)
    inner = line(lib.T([(-100, -10), (100, -22)], x, y, k, rot), 2.4, "#D8D2C4", taper=.3, wmin=.4, seed=1600 + seed)
    inner += line(lib.T([(-90, 14), (90, 2)], x, y, k, rot), 2.4, "#D8D2C4", taper=.3, wmin=.4, seed=1601 + seed)
    return lib.shape(pts, "#FFFFFF", inner, w=3.4, seed=1610 + seed)


def s16(t):
    sc, back = world_fire(t, 1.0, "tower")
    # Дима: стоит, собирается → «соберись» тужится: кулаки к груди, щёки надуты, жилка; дрожит от натуги
    go = sm(t, T_RAB - .05, T_SOB - .05)
    hard = sm(t, T_SOB - .1, T_SOB + .1)
    trem = 4 * math.sin(t * 47) * hard
    feet = people.stand_kw(DX16, HIP16_Y, 1.0, spread=150)["feet"]
    kw = people.mix_pose("rest", "strain", go, DX16, HIP16_Y + 10 * hard, 1.0)
    if hard < .5:
        e = ex("focus", look=(.6, -.35), lid=lerp(.62, .8, go), closed=blinks(t, (20.6,)), bags=False)
    else:
        e = ex("strain", flush=.9)
    full = people.dima(DX16 + trem * .5, HIP16_Y + 10 * hard, 1.0, e, None, feet=feet, arms=kw["arms"], hands=kw["hands"],
                       lean_add=kw["lean"] + .015 * math.sin(t * 2.3) - .05 * hard, head_add=kw["head_ang"] + .04 * hard + .01 * trem)
    dima = warm(full["svg"], t)
    marks = people.strain_marks(full["head"], 1.0, t, hard)
    # башня: ни с места; к концу один верхний лист лениво съезжает и планирует вниз
    tower = PR.paper_tower(TOWER16[0], TOWER16[1], TOWER_K, lean=0.0, flutter=.15 * hard, t=t, seed=3)
    top = PR.paper_tower_top(TOWER16[0], TOWER16[1], TOWER_K)
    fu = clamp((t - (T_SOB + .25)) / 1.1)
    leaf = ""
    if fu > 0:
        x = top[0] + 20 + 230 * fu + 50 * math.sin(fu * 6)
        y = top[1] - 30 + (GROUND16 - 40 - top[1]) * (fu ** 1.5)
        leaf = sheet(x, y, 14 * math.sin(fu * 7) + 4, .75, seed=1)
    # кот: сидит слева впереди, на «соберись» медленно качает головой
    shk = sm(t, T_SOB + .05, T_SOB + .25) * (1 - sm(t, 22.1, 22.3))
    st = dict(turn=.35 * math.sin(2 * math.pi * (t - T_SOB) / .9) * shk + .25 * (1 - shk), look=(.6, -.2), blink=.45 * shk + blinks(t, (20.8,)),
              tail=5 * math.sin(t * 2.0), flame_e=1.0, ear=3 * math.sin(t * 2.7), tilt=-3 * shk)
    cat = warm_cat(CAT.draw(CAT16[0], CAT16[1], CAT16_K, st, t), t)
    cshadow = blob(ellipse_pts(CAT16[0] + 10, CAT16[1] + 4, 140 * CAT16_K, 14, 14), "#000000", .25)
    dshadow = blob(ellipse_pts(DX16 + 20, GROUND16 + 6, 170, 18, 14), "#000000", .25)
    world = [back, sc["fire"], sc["stones_front"], sc["log"], tower, dshadow, dima, marks, leaf, cshadow, cat]
    # камера: хлёст в ночь, мини-тряска на натуге, потом чуть оседает
    u = sm(t, T_A16 - .2, 22.3)
    s = lerp(1.1, 1.03, u) + .04 * bump(t, T_SOB, .35)
    ccx = lerp(740, 780, u)
    ccy = lerp(880, 900, u) + 30 * sm(t, T_SOB + .4, 22.2)
    sx_, sy_ = shake(t, T_SOB, 9)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx + sx_, ccy + sy_, s, lerp(-.5, .4, u))}">{"".join(world)}</g>'
    return whip(g, t, T_A16), BG


FRAMES["s16"] = s16


# ═════════════════════════ s17: клочок с горошину на ладонь, смех ═════════════════════════
T_A17 = 22.08
T_MAL, T_SME = wt(52), wt(54)                 # 22.85, 23.49
DX17 = 430.0
CAT17_A, CAT17_B = (420.0, 1540.0), (900.0, 1480.0)
CAT17_K = .85
SCRAP0 = (805.0, GROUND16 - 14)
PALM17 = (720.0, GROUND16 - 26)


def s17(t):
    sc, back = world_fire(t, 1.0, "tower")
    # башня та же, отражена: клочок выезжает из основания влево, к Диме
    tower = f'<g transform="translate({2 * TOWER16[0]:.1f} 0) scale(-1 1)">' + PR.paper_tower(TOWER16[0], TOWER16[1], TOWER_K, t=t, seed=3) + "</g>"
    # Дима: стоит → присаживается на корточки, ладонь вниз к земле перед собой (ладонью вверх) → подносит к лицу → прыскает
    cr = sm(t, T_A17 - .1, 22.75)
    st_f = people.stand_kw(DX16, HIP16_Y, 1.0, spread=150)["feet"]
    cr_hip = GROUND16 - 140
    hip = (lerp(DX16, DX17, cr), lerp(HIP16_Y, cr_hip, cr))
    cf = people.crouch_kw(hip[0], hip[1], 1.0)["feet"]
    feet = {k_: (lerp2(st_f[k_][0], cf[k_][0], cr), lerp(st_f[k_][1], cf[k_][1], cr)) for k_ in ("n", "f")}
    lift = sm(t, 23.22, 23.48)
    laugh = sm(t, T_SME - .04, T_SME + .1)
    shake_l = laugh * math.sin(2 * math.pi * (t - T_SME) / .16)
    W_rest = (hip[0] + 140, hip[1] - 120)
    W_palm = (PALM17[0] - 60, PALM17[1] + 6)
    W_up = (hip[0] + 280, hip[1] - 300)
    reach = sm(t, 22.45, 22.85)
    Wn = lerp2(lerp2(W_rest, W_palm, reach), W_up, lift)
    Wn = (Wn[0], Wn[1] - 8 * shake_l)
    hn = {"dir": (1, -.1), "flip": -1, "spread": .3, "curl": (.05, .1, .15, .2), "thumb": .15}
    arms = {"f": ("ik", (hip[0] + 200, hip[1] - 110), -1), "n": ("ik", Wn, -1)}
    hands = {"f": {"dir": (1, .5), "curl": (.4, .45, .5, .55), "thumb": .4}, "n": hn}
    if laugh > .5:
        e = ex("giggle")
    elif reach > .5:
        e = ex("surprise", look=(.5, .9 - .7 * lift), closed=blinks(t, (23.05,)), bags=False)
    else:
        e = ex("downcast", look=(.6, .3), lid=.6)
    full = people.dima(hip[0], hip[1] + 6 * shake_l, 1.0, e, None, feet=feet, arms=arms, hands=hands,
                       lean_add=.22 * cr - .05 * lift + .03 * shake_l, head_add=.2 * cr * (1 - lift) - .06 * laugh + .04 * shake_l)
    dima = warm(full["svg"], t)
    # кот: идёт к башне, садится перед ней, левой лапой вытягивает клочок и подвигает Диме на ладонь, потом щурится
    wu = clamp((t - (T_A17 - .1)) / (22.62 - (T_A17 - .1)))
    pull = sm(t, T_MAL - .25, T_MAL) * (1 - sm(t, 23.2, 23.4))
    sq = sm(t, T_SME, T_SME + .3)
    st = dict(turn=-.3 + .2 * sq, look=(-.7, .5 - .5 * sq), paw_l=.5 * pull, paw_l_dx=130, blink=.55 * sq, smile=1.0 if sq > .4 else 0.0,
              tail=6 * math.sin(t * 2.2), flame_e=1.0 + .4 * sq, ear=4 * bump(t, T_MAL, .3))
    if wu < 1:
        cx, cy = lerp2(CAT17_A, CAT17_B, lib.ease_io(wu))
        cat = people.cat_walk(cx, cy, lerp(.82, CAT17_K, wu), t, st, period=.4)
    else:
        cx, cy = CAT17_B
        cat = CAT.draw(cx, cy, CAT17_K, st, t)
    cat = warm_cat(cat, t)
    # клочок: из основания башни → по земле под лапой на ладонь → поднят с ладонью
    pop = sm(t, T_MAL - .02, T_MAL + .1)
    slide = sm(t, 22.92, 23.18)
    if lift > 0:
        sp = people.hand_pos(full, "n", 45)
        sp = (sp[0], sp[1] - 18)
    else:
        sp = lerp2(SCRAP0, PALM17, slide)
        sp = (sp[0], sp[1] - 26 * math.sin(math.pi * slide))
    scrap = PR.scrap(sp[0], sp[1], 1.1 * (.3 + .7 * pop), -12 + 30 * slide, seed=7) if pop > 0 else ""
    flick = ""
    if 0 < slide < 1:
        flick = blob(ellipse_pts(sp[0] + 30, sp[1] + 14, 20, 5, 8), "#FFD24A", .5)
    cshadow = blob(ellipse_pts(cx + 10, cy + 4, 140 * CAT17_K, 14, 14), "#000000", .25)
    dshadow = blob(ellipse_pts(hip[0] + 60, GROUND16 + 6, 170, 18, 14), "#000000", .25)
    world = [back, sc["fire"], sc["stones_front"], sc["log"], tower, dshadow, cshadow, cat, scrap, flick, dima]
    # камера: наезд на ладонь с клочком (средний план), потом отъезд на смех
    zin = sm(t, 22.6, 23.2)
    zout = sm(t, T_SME, 24.1)
    s = lerp(1.15, 1.55, zin) - .38 * zout + .015 * math.sin(t * 2.1)
    ccx = lerp(700, 640, zin) + 40 * zout
    ccy = lerp(1010, 1150, zin) - 140 * zout
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(.4, -.3, zin) + .3 * zout)}">{"".join(world)}</g>'
    return g, BG


FRAMES["s17"] = s17


# ═════════════════════════ s18: ноутбук на коленях, крышка одним пальцем, свет экрана на лице ═════════════════════════
T_A18 = 24.15
T_OTK, T_FIL = wt(55), wt(56)                 # 24.19, 24.80
HIP18 = R.DIMA_LOG
CAT18 = (560.0, 1500.0)


def s18(t):
    sc, back = world_fire(t, 1.0, "laptop")
    hx, hy = HIP18
    feet = people.knees_kw(hx, hy, 1.0, tight=.35)["feet"]
    op = lib.ease_out(clamp((t - (T_OTK - .02)) / (T_FIL - .06 - (T_OTK - .02))), 1.8)
    on = sm(t, T_FIL - .02, T_FIL + .14)
    LAP = (hx + 150, hy - 70)
    lp = H.laptop_side(LAP[0], LAP[1], .78, op, on=on, t=t, seed=2)
    lt = lp["lid_top"]
    rel = sm(t, T_FIL + .05, T_FIL + .3)
    W_lift = (lt[0] - 70, lt[1] + 30)
    W_start = (LAP[0] + 60, LAP[1] - 20)
    W_rest = (LAP[0] + 20, LAP[1] - 24)
    go = sm(t, T_A18 - .2, T_OTK - .02)
    Wn = lerp2(lerp2(W_start, W_lift, go if op < .02 else 1.0), W_rest, rel)
    if op > .02 and rel < .5:
        Wn = (lt[0] - 70, lt[1] + 30)
    hn = {"dir": (1, -.35), "curl": (0, .8, .85, .85), "spread": .05, "thumb": .6} if rel < .5 else {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}
    Wf = (LAP[0] - 20, LAP[1] - 10)
    surprise = sm(t, T_FIL + .02, T_FIL + .3)
    if surprise < .5:
        e = ex("focus", look=(.65, .5), lid=.62, closed=blinks(t, (24.5,)), bags=False)
    else:
        e = ex("surprise", mouth="smile", smile=.8, open=0.0, look=(.6, .45), lid=1.0, bags=False)
    full = people.dima(hx, hy, 1.0, e, None, feet=feet, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)},
                       hands={"f": {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}, "n": hn},
                       lean_add=.12 + .03 * go - .06 * surprise + .012 * math.sin(t * 2.4), head_add=.12 - .1 * surprise)
    parts = {k_: people.dima(hx, hy, 1.0, e, None, feet=feet, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)},
                             hands={"f": {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35}, "n": hn},
                             lean_add=.12 + .03 * go - .06 * surprise + .012 * math.sin(t * 2.4), head_add=.12 - .1 * surprise,
                             layers=(k_,))["svg"] for k_ in LAYERS}
    body = warm("".join(parts[k_] for k_ in ("legs", "pelvis", "arm_f", "body")), t)
    arm_n = warm(parts["arm_n"], t)
    hd = full["head"]
    light = PR.glow(hd[0] + 70, hd[1] + 20, 170, .75 * on, "#DDE8FF", ry=190) + PR.glow(lp["screen"][0] - 30, lp["screen"][1], 120, .5 * on, "#DDE8FF")
    # кот сидит у ног, на «файл» ухо и взгляд на экран
    st = dict(turn=-.35, look=(-.6, -.3), ear=6 * bump(t, T_FIL, .3) + 2 * math.sin(t * 3), tail=5 * math.sin(t * 2.1), blink=blinks(t, (24.4,)),
              perk=.6 * bump(t, T_FIL, .5), flame_e=1.0 + .3 * on)
    cat = warm_cat(CAT.draw(CAT18[0], CAT18[1], .72, st, t), t)
    cshadow = blob(ellipse_pts(CAT18[0] + 10, CAT18[1] + 4, 100, 12, 14), "#000000", .25)
    world = [back, sc["fire"], sc["stones_front"], sc["log"], cshadow, cat, body, lp["svg"], arm_n, light]
    # камера: лёгкий наезд к лицу в свете экрана
    u = sm(t, T_A18 - .2, 25.5)
    s = lerp(1.45, 1.62, u) + .03 * bump(t, T_FIL, .3)
    ccx = lerp(330, 360, u) + 4 * math.sin(t * 1.5)
    ccy = lerp(1060, 1000, u) + 3 * math.sin(t * 1.9)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.4, .3, u))}">{"".join(world)}</g>'
    return g, BG


FRAMES["s18"] = s18


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
