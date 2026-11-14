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
import props as PR  # noqa: E402
from h72 import blinks, bump, lerp, set_ink, shake, sm, wt  # noqa: E402
from lib import INK, blob, clamp, ellipse_pts, line  # noqa: E402

FRAMES = {}
PAPER = "#e6dcc0"


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


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
