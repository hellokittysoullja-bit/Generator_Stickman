"""Рилс 64 «спасибо», группа C — вечер у стола: s01 (хук: Дима вертит открытку, раскрывает — пусто, ручка зависает, щелчок колпачка),
s03 (сомнение: замирает, морщится и чешет затылок, открытка поникает, в ящик — хлопок, лампа качнулась),
s04 (ракурс ниже: Дима откинулся, кот шагает, запрыгивает на стол, лапой тянет ящик и вытаскивает открытку, поворачивает морду к зрителю).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Комната — common/room.py, люди и кот — common/people.py (cat.py),
предметы — common/props.py. Букв и цифр нет."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
BS = 1.0
SX, SY = R.SIT
SC = BS * people.HEIGHT["dima"]
FEET = {"n": ((SX + 300 * BS, R.FL - 52), 0.0), "f": ((SX + 250 * BS, R.FL - 50), 0.0)}
CARD_K = .62
PEN_K = .55


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»").lower() == word:
            return w["start"]
    raise KeyError(word)


T_DAVNO, T_HOTEL, T_SKAZAT = wt("давно"), wt("хотел"), wt("сказать")             # 0.37 0.71 1.08
T_KAZ, T_STR, T_NIK, T_NUZH = wt("казалось"), wt("странно"), wt("никому"), wt("нужно")   # 4.44 5.52 6.52 7.11
T_ZNA, T_POCH = wt("знаешь"), wt("почему")                                        # 9.27 9.58
T_JUMP = 8.0


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def shake2(t, t0, amp, k=9.0, fr=19.0):
    def dec(tt):
        if tt < 0:
            return 0.0
        return math.exp(-k * tt) * math.sin(2 * math.pi * fr * tt)
    return amp * dec(t - t0), amp * .7 * dec(t - t0 - .013)


def keys(t, ks):
    """Кусочная интерполяция ключей [(t, value)] с ease_io; value — число или кортеж."""
    if t <= ks[0][0]:
        return ks[0][1]
    for (ta, a), (tb, b) in zip(ks, ks[1:]):
        if t <= tb:
            u = ease_io((t - ta) / max(1e-6, tb - ta))
            if isinstance(a, tuple):
                return tuple(x + (y - x) * u for x, y in zip(a, b))
            return a + (b - a) * u
    return ks[-1][1]


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.update(kw)
    return e


def blinkv(t, times, dur=.16):
    v = 0.0
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def hook_cam(t, t_hit):
    """Влёт правил 28/29: с 40 % дальше (1/(1+0.4)) за 0.22 с, перелёт с отскоком, поворот 3.8° с возвратом, занос сбоку;
    второй удар +8 % на ударном слоге. Возвращает (масштаб-множитель, поворот, занос)."""
    u = clamp(t / .22)
    e = ease_out(u, 3)
    s = 1 / 1.4 + (1 - 1 / 1.4) * e
    if t > .22:
        s += .055 * math.exp(-7 * (t - .22)) * math.sin(2 * math.pi * 2.2 * (t - .22) + math.pi / 2)
    rot = 3.8 * (1 - e) + damp(t, .22, -1.1, 2.0, 6.0)
    side = 50 * (1 - e)
    hit = 0.0
    if t > t_hit:
        h = t - t_hit
        hit = .08 * math.exp(-5.5 * h) * (1 if h > .03 else h / .03)
    return s * (1 + hit), rot, side


def whip_in(t, t0, dur=.18):
    """Хвост хлёста на входе плана: сдвиг по x и наклон гаснут за dur (сборщик кладёт склейку, клип сам доезжает)."""
    u = clamp((t - t0) / dur)
    e = 1 - ease_out(u, 3)
    return -160 * e, -2.0 * e


# ═════════════════════════ Дима за столом ═════════════════════════
def dima_parts(expr, pose, hands=None, arms=None, shrug=0.0, lean_add=0.0, head_add=0.0, u_pose=None):
    """Дима сидит на стуле SIT: тело слоями (legs / pelvis / arm_f / body / arm_n), запястья для предметов."""
    kw = dict(feet=FEET, shrug=shrug, lean_add=lean_add, head_add=head_add, arms=arms, hands=hands, u_pose=u_pose)
    full = people.dima(SX, SY, BS, expr, pose, layers=("legs", "pelvis", "arm_f", "body", "arm_n"), **kw)
    parts = {}
    for k in ("legs", "pelvis", "arm_f", "body", "arm_n"):
        parts[k] = people.dima(SX, SY, BS, expr, pose, layers=(k,), **kw)["svg"]
    return full, parts


def held_pen(W, d, rot, cap=0.0, k=PEN_K):
    """Ручка в кулаке: центр ручки — у центра кулака (запястье + 52·sc вдоль кисти), ось — rot (0 — кончик вниз)."""
    dn = np.array(d, float) / (np.linalg.norm(d) + 1e-9)
    c = np.array(W) + dn * 50 * SC
    return PR.pen(float(c[0]), float(c[1]), k, rot, cap, seed=3), (float(c[0]), float(c[1]))


def room_layers(t, sc, parts, items_mid, items_top, arm_n_extra=""):
    """Порядок слоёв стола (см. room.desk_scene)."""
    return [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"], parts["arm_f"],
            parts["body"], items_mid, parts["arm_n"], arm_n_extra, items_top, sc["lamp"]]


# ═════════════════════════ s01: хук ═════════════════════════
def s01(t):
    lib.dyn_begin()
    # открытка в дальней руке: до «давно» вертится в пальцах (поворот, лёгкий наклон), на «давно» раскрывается — внутри пусто,
    # и ложится на край стола; ближняя рука с ручкой с кадра 0 у груди, к «хотел» ручка зависает над пустой страницей, щелчок колпачка.
    op = sm(t, T_DAVNO - .02, T_DAVNO + .24)
    lay = sm(t, T_DAVNO + .1, T_HOTEL - .02)
    # дальняя кисть: вертит (кругом) → кладёт открытку на стол и прижимает край
    twirl = 1 - lay
    Wf = (SX + 205 * SC + 26 * math.sin(t * 9.0) * twirl, SY - 300 * SC + 18 * math.cos(t * 9.0) * twirl)
    Wf = lerp2(Wf, (SX + 230 * SC, R.DESK_TOP - 74), lay)
    # ближняя кисть с ручкой: у груди → над открыткой
    hover = sm(t, T_DAVNO + .18, T_HOTEL)
    Wn = lerp2((SX + 250 * SC, SY - 330 * SC + 8 * math.sin(t * 6)), (SX + 300 * SC, R.DESK_TOP - 180), hover)
    Wn = (Wn[0], Wn[1] - 14 * bump(t, T_HOTEL - .04, .2) + 3 * math.sin(t * 13) * hover)    # дрожит в нерешительности
    hands = {"f": {"curl": (.55, .6, .62, .65), "thumb": .55, "dir": (.75, -.65)},
             "n": {"curl": (.78, .8, .82, .85), "thumb": .65, "dir": (.85, .35)}}
    talk = t > T_SKAZAT - .25
    e = ex("unsure", look=(lerp(.35, .7, sm(t, .2, T_DAVNO)), lerp(.1, .7, op)), lid=.68 + .25 * blinkv(t, [1.25]) * 0)
    if talk:      # губы шевелятся — репетирует
        e = dict(e, mouth="talk", open=.18 + .22 * abs(math.sin((t - T_SKAZAT) * 17)), smile=.05)
    e["closed"] = blinkv(t, [1.3])
    lean_add = .03 * math.sin(t * 2.3) + .05 * hover
    head_add = -.05 + .05 * op + .03 * damp(t, T_HOTEL, 1.0, 3.5, 6)
    full, parts = dima_parts(e, "card", hands=hands, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, lean_add=lean_add, head_add=head_add)
    wf, wn = full["wrist"]["f"], full["wrist"]["n"]
    # открытка: центр у пальцев дальней кисти, вертится
    rot_c = lerp(-14 + 16 * math.sin(t * 7.5), -6, lay)
    cpos = lerp2((wf[0] + 70, wf[1] - 40), (wf[0] + 120, wf[1] + 26), lay)
    card = PR.card(cpos[0], cpos[1], CARD_K * (1 - .1 * lay), rot_c, op, "blank", seed=1, droop=0.0)
    # кончик пальцев дальней кисти поверх края открытки — хват (большой палец спереди)
    fthumb = people.hand_svg("dima", wf, (.75, -.65), k=SC, far=True, curl=(.55, .6, .62, .65), thumb=.55, seed=720)
    cap = sm(t, T_HOTEL - .03, T_HOTEL + .1)
    pen_rot = lerp(-60, 28, hover) + 5 * math.sin(t * 11) * hover
    pen, pc = held_pen(wn, (.85, .35), pen_rot, cap)
    tip = PR.pen_tip(pc[0], pc[1], PEN_K, pen_rot)
    clk = PR.click(pc[0] - 30, pc[1] + 30, 1.0, clamp((t - T_HOTEL) / .25), seed=2)
    sc = R.desk_scene(t, "evening", drawer=0.0)
    del tip
    items_mid = card + fthumb + pen
    world = room_layers(t, sc, parts, items_mid, clk)
    # камера: влёт к открытке, второй удар на щелчке «хотел»
    k, rot_c2, side = hook_cam(t, T_HOTEL)
    sx1, sy1 = shake2(t, T_HOTEL + .01, 10)
    cx0, cy0, s0 = R.CAM_DESK_CLOSE
    cx = cx0 + side - sx1 + 30 * sm(t, 0, 1.6) + 6 * math.sin(t * 1.7)
    cy = cy0 - sy1 + 30 * hover
    s = s0 * k * (1 + .04 * sm(t, .3, 1.6))
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, rot_c2)}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')


def frame(sid, t):
    return {"s01": s01}[sid](t)
