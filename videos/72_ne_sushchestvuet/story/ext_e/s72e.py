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


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
