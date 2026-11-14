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
CARD_K = .95
PEN_K = .9


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
    c = np.array(W) + dn * 58 * SC
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
    Wf = lerp2(Wf, (SX + 225 * SC, R.DESK_TOP - 120), lay)
    # ближняя кисть с ручкой: у груди → кончик ручки зависает над правой (пустой) страницей
    hover = sm(t, T_DAVNO + .18, T_HOTEL)
    cpos_end = (SX + 225 * SC + 150, R.DESK_TOP - 40 - 115 * CARD_K * .9)
    tgt = (cpos_end[0] + 50, R.DESK_TOP - 70)
    rot_end = -48.0
    tip_off = PR.pen_tip(0, 0, PEN_K, rot_end)
    dn = np.array((.9, .45)) / np.linalg.norm((.9, .45))
    W_end = (tgt[0] - tip_off[0] - dn[0] * 58 * SC, tgt[1] - tip_off[1] - dn[1] * 58 * SC)
    Wn = lerp2((SX + 250 * SC, SY - 330 * SC + 8 * math.sin(t * 6)), W_end, hover)
    Wn = (Wn[0], Wn[1] - 16 * bump(t, T_HOTEL - .04, .2) + 3 * math.sin(t * 13) * hover)    # дрожит в нерешительности
    hands = {"f": {"curl": (.55, .6, .62, .65), "thumb": .55, "dir": (.75, -.65)},
             "n": {"curl": (.78, .8, .82, .85), "thumb": .65, "dir": (lerp(.85, .9, hover), lerp(.35, .45, hover))}}
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
    cpos = lerp2((wf[0] + 125, wf[1] - 95), (wf[0] + 150, R.DESK_TOP - 40 - 115 * CARD_K * .9), lay)
    card = PR.card(cpos[0], cpos[1], CARD_K * (1 - .1 * lay), rot_c, op, "blank", seed=1, droop=0.0)
    # открытка ложится на стол наклонно: сжатие по высоте к нижнему краю (верх видно сверху)
    yb = cpos[1] + 115 * CARD_K * .9
    q = 1 - .45 * lay
    card = f'<g transform="translate(0 {yb:.2f}) scale(1 {q:.4f}) translate(0 {-yb:.2f})">{card}</g>'
    # кончик пальцев дальней кисти поверх края открытки — хват (большой палец спереди)
    fthumb = people.hand_svg("dima", wf, (.75, -.65), k=SC, far=True, curl=(.55, .6, .62, .65), thumb=.55, seed=720)
    cap = .995 * sm(t, T_HOTEL - .03, T_HOTEL + .1)
    pen_rot = lerp(150, rot_end, hover) + 4 * math.sin(t * 11) * hover
    pen, pc = held_pen(wn, (lerp(.85, .9, hover), lerp(.35, .45, hover)), pen_rot, cap)
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


# ═════════════════════════ s03: сомнение и открытка в ящик ═════════════════════════
DRAWER_C = ((R.DRAWER[0] + R.DRAWER[1]) / 2, (R.DRAWER[2] + R.DRAWER[3]) / 2)
T_PEN_DOWN, T_TAKE, T_IN = T_NIK + .2, T_NIK + .3, T_NUZH - .14


def s03(t):
    lib.dyn_begin()
    # ящик приоткрыт с начала (открытку из него и доставали), на «нужно» захлопывается
    close = sm(t, T_IN, T_NUZH)
    drawer = .62 * (1 - close)
    swing = damp(t, T_NUZH, 11.0, 2.0, 2.6)
    sc = R.desk_scene(t, "evening", drawer=drawer, lamp_swing=swing)
    # ближняя кисть: ручка вверх → замирает → чешет затылок → вниз, бросает ручку → берёт открытку → в ящик → толкает ящик
    scr = sm(t, T_STR, T_STR + .3) * (1 - sm(t, T_NIK - .1, T_NIK + .15))
    Wpen = (SX + 300 * SC, R.DESK_TOP - 250)
    Wscr = (SX - 30 * SC + 14 * math.sin(t * 26) * scr, SY - 650 * SC + 10 * math.cos(t * 26) * scr)
    Wcard = (SX + 330 * SC, SY - 300 * SC)
    Wdrw = (DRAWER_C[0] - 70, R.DRAWER[2] - 30)
    Wpush = (DRAWER_C[0] - 80, DRAWER_C[1] + 30)
    ks = [(4.2, (SX + 260 * SC, SY - 320 * SC)), (T_KAZ, (SX + 270 * SC, SY - 330 * SC)), (T_KAZ + .3, Wpen), (T_STR, (Wpen[0] + 4, Wpen[1] - 6)),
          (T_STR + .3, Wscr), (T_NIK - .1, Wscr), (T_PEN_DOWN, (SX + 340 * SC, R.DESK_TOP - 130)), (T_TAKE, Wcard), (T_IN - .02, Wdrw),
          (T_NUZH, Wpush), (7.7, (Wpush[0] - 20, Wpush[1] - 10))]
    Wn = keys(t, ks)
    if T_KAZ + .3 < t < T_STR:     # замер с ручкой: мелкая дрожь
        Wn = (Wn[0] + 2 * math.sin(t * 15), Wn[1] + 2 * math.cos(t * 13))
    up = scr > .3
    pen_in_hand = t < T_PEN_DOWN
    card_in_near = t >= T_TAKE
    # дальняя кисть держит раскрытую открытку перед собой; на «никому» поникает, на передаче опускается на стол
    droop = sm(t, T_NIK, T_NIK + .3)
    Wf = keys(t, [(4.2, (SX + 215 * SC, SY - 285 * SC)), (T_NIK, (SX + 215 * SC, SY - 285 * SC)), (T_NIK + .3, (SX + 230 * SC, SY - 245 * SC)),
                  (T_TAKE, (SX + 250 * SC, SY - 265 * SC)), (T_TAKE + .25, (SX + 205 * SC, R.DESK_TOP - 80))])
    Wf = (Wf[0] + 3 * math.sin(t * 2.1), Wf[1] + 3 * math.cos(t * 1.7))
    # мимика
    if t < T_STR:
        e = ex("unsure", look=(.55, .45))
        e["closed"] = blinkv(t, [4.9])
    elif t < T_NIK:
        e = ex("awkward")
        e["closed"] = blinkv(t, [6.2])
    else:
        e = ex("glum", look=(.6, .75) if t < T_NUZH + .1 else (.35, .5))
        e["closed"] = blinkv(t, [7.35])
    shrug = sm(t, T_STR, T_STR + .25) * (1 - sm(t, T_NIK + .05, T_NIK + .4))
    lean_add = .02 * math.sin(t * 2) + .08 * sm(t, T_TAKE, T_IN) - .05 * sm(t, T_NUZH, T_NUZH + .4)
    head_add = -.04 * shrug + .08 * droop + .04 * damp(t, T_NUZH, 1.0, 3, 5)
    hn = {"curl": (.78, .8, .82, .85), "thumb": .65, "dir": (.85, .35)} if pen_in_hand else {"curl": (.55, .55, .6, .62), "thumb": .55, "dir": (.8, .55)}
    if up:
        hn = dict(hn, dir=(.2, -1))
    if t >= T_IN - .02:
        hn = {"curl": (.12, .12, .16, .2), "thumb": .2, "spread": .1, "dir": (.95, .25)}     # ладонь толкает ящик
    hands = {"f": {"curl": (.55, .6, .62, .65), "thumb": .55, "dir": (.75, -.65)} if t < T_TAKE + .1 else {"curl": (.35, .35, .4, .45), "thumb": .35, "dir": (1, .3)},
             "n": hn}
    full, parts = dima_parts(e, "card", hands=hands, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, 1 if up else -1)}, shrug=shrug, lean_add=lean_add,
                             head_add=head_add)
    wf, wn = full["wrist"]["f"], full["wrist"]["n"]
    items = []
    # открытка
    op = 1 - sm(t, T_TAKE - .15, T_TAKE + .1)
    if not card_in_near:
        cpos = (wf[0] + 140, wf[1] - 60 + 24 * droop)
        items.append(PR.card(cpos[0], cpos[1], CARD_K * .9, -6 + 10 * droop, op, "blank", seed=1, droop=droop))
        items.append(people.hand_svg("dima", wf, (.75, -.65), k=SC, far=True, curl=(.55, .6, .62, .65), thumb=.55, seed=720))
    elif t < T_NUZH:
        cpos = (wn[0] + 70, wn[1] + 30)
        crd = PR.card(cpos[0], cpos[1], CARD_K * .9, -14 + 10 * sm(t, T_TAKE, T_IN), 0.0, "blank", seed=1, droop=.6 * (1 - sm(t, T_TAKE, T_IN)))
        ins = sc["inside"]
        if t > T_TAKE + .15 and ins is not None:     # в ящик: ниже края передней панели не видно
            cid = lib.clip_rect(-2000, -2000, 6000, ins[3] + 2000)
            crd = f'<g clip-path="url(#{cid})">{crd}</g>' + sc["drawer_front"]
        items.append(crd)
    # ручка: в руке, потом брошена на стол
    if pen_in_hand:
        prot = keys(t, [(4.2, 150.0), (T_KAZ + .3, 25.0), (T_STR, 25.0), (T_STR + .3, 185.0), (T_NIK - .1, 185.0), (T_PEN_DOWN, 100.0)])
        pn, pc = held_pen(wn, hands["n"]["dir"], prot, 0.0)
    else:
        u = clamp((t - T_PEN_DOWN) / .16)
        pn = PR.pen(lerp(wn[0] + 60, SX + 470, u) if u < 1 else SX + 470, R.DESK_TOP - 36 - 10 * bump(t, T_PEN_DOWN + .16, .2), PEN_K, 96 + 10 * (1 - u), 0.0, seed=3)
        pn = pn
    items_mid = "".join(items) + pn
    # хлопок: пыль-штрихи у щели ящика
    hit = ""
    v = (t - T_NUZH) / .3
    if 0 < v < 1:
        for i, dx in enumerate((-150, -60, 60, 150)):
            x0 = DRAWER_C[0] + dx
            hit += line([(x0, R.DRAWER[2] - 4), (x0 + dx * .25 * v, R.DRAWER[2] - 30 - 40 * v)], 6 * (1 - v) + 1, INK, taper=.5, wmin=.2, seed=6300 + i)
    world = room_layers(t, sc, parts, items_mid, hit)
    # камера: хлёст на входе, дрейф влево, тряска на хлопке
    wx, wr = whip_in(t, 4.4)
    sx1, sy1 = shake2(t, T_NUZH + .01, 16)
    cx0, cy0, s0 = R.CAM_DESK_MID
    cx = cx0 + 60 - 110 * sm(t, 4.2, 7.6) + wx - sx1
    cy = cy0 - 20 * sm(t, 4.2, 7.6) - sy1
    s = s0 * (1 + .05 * sm(t, 4.4, 7.6))
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, wr + .6 * math.sin(t * .9))}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')


# ═════════════════════════ s04: ракурс ниже, кот достаёт открытку ═════════════════════════
CAT_K = .8
T_LAND = T_JUMP + .32
T_REACH, T_OPEN, T_PULL, T_OUT = 8.62, 8.82, 9.0, 9.2
CAT_START, CAT_TAKEOFF = (1430.0, R.FL - 6), (1085.0, R.FL - 6)
CAT_TOP = (835.0, R.DESK_TOP - 12)
HANDLE = ((R.DRAWER[0] + R.DRAWER[1]) / 2, (R.DRAWER[2] + R.DRAWER[3]) / 2 - 4)


def cat_paw_down(base, tip, k, seed=4600):
    """Передняя лапа кота вниз через край стола к ручке ящика (мир), подушечки к зрителю, когти зацепили."""
    from ink import band
    mid = ((base[0] + tip[0]) / 2 + 14 * k, (base[1] + tip[1]) / 2)
    arm = band([base, mid, tip], 60 * k, 50 * k, step=4, cap=False)
    import cat as C
    o = [shape(arm, C.CAT, blob([(base[0] + 8 * k, base[1]), (base[0] + 22 * k, base[1]), (tip[0] + 16 * k, tip[1]), (tip[0] + 4 * k, tip[1])],
                                 C.CAT_SH, .6), w=4.6 * k / .62, seed=seed)]
    pp = ellipse_pts(tip[0], tip[1] + 6 * k, 27 * k, 22 * k, 12)
    o.append(shape(pp, C.CAT, "", w=4.4 * k / .62, seed=seed + 1))
    for kk in (-10, 0, 10):     # когти поддели ручку
        o.append(line([(tip[0] + kk * k, tip[1] + 16 * k), (tip[0] + (kk - 2) * k, tip[1] + 28 * k)], 2.4, seed=seed + 5 + kk))
    return "".join(o)


def s04(t):
    lib.dyn_begin()
    drawer = .58 * sm(t, T_OPEN, T_PULL + .05)
    sc = R.desk_scene(t, "evening", drawer=drawer, lamp_swing=damp(t, T_LAND, 3.0, 2.0, 3.0), chair_tilt=-2.5)
    # Дима откинулся, руки за головой, смотрит в сторону (влево); к концу косится на кота
    look = (-.7, -.15) if t < 9.5 else (lerp(-.7, .55, sm(t, 9.5, 9.8)), lerp(-.15, .2, sm(t, 9.5, 9.8)))
    e = ex("thoughtful", look=look) if "thoughtful" in people.EXPR["dima"] else ex("unsure", look=look)
    e["closed"] = blinkv(t, [7.9, 9.45])
    lean_add = .015 * math.sin(t * 1.9)
    head_add = .02 * math.sin(t * 1.3 + .5) + .05 * sm(t, 9.5, 9.8)
    kw = dict(feet=FEET, lean_add=lean_add, head_add=head_add)
    parts = {k: people.dima(SX, SY, BS, e, "behind", layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "arm_n", "body")}
    # кот
    st = {"look": (-.3, .2), "turn": -.55, "tail": 8 * math.sin(t * 2.6), "blink": blinkv(t, [8.7])}
    if t < 7.8:                                                   # шагает по полу влево, лапы по очереди
        u = clamp((t - 7.2) / .6)
        x = lerp(CAT_START[0], CAT_TAKEOFF[0], u if t >= 7.2 else 0)
        x = CAT_START[0] - (CAT_START[0] - CAT_TAKEOFF[0]) * clamp((t - 7.0) / .8)
        cx_, cy_ = x, CAT_START[1]
        st.update(walk=(CAT_START[0] - x) / 110.0, rot=1.5 * math.sin((CAT_START[0] - x) / 110 * 2 * math.pi), turn=-.6, look=(-.4, .1))
    elif t < T_JUMP:                                              # присел, смотрит на стол
        c = sm(t, 7.8, T_JUMP)
        cx_, cy_ = CAT_TAKEOFF
        st.update(sy=1 - .18 * c, sx=1 + .1 * c, look=(-.3, -.5), turn=-.4, tail=8 + 12 * c)
    elif t < T_LAND:                                              # прыжок: толчок задних, дуга
        u = (t - T_JUMP) / (T_LAND - T_JUMP)
        cx_ = lerp(CAT_TAKEOFF[0], CAT_TOP[0], u)
        cy_ = lerp(CAT_TAKEOFF[1], CAT_TOP[1], u) - 210 * 4 * u * (1 - u)
        st.update(legs=1.0 if u > .08 else u / .08, sy=1.12 - .1 * u, sx=.93 + .05 * u, rot=-10 * math.sin(math.pi * u), look=(-.3, -.2), turn=-.4,
                  tail=-18 * math.sin(math.pi * u))
    else:
        cx_, cy_ = CAT_TOP
        q = math.exp(-14 * (t - T_LAND))
        st.update(sy=1 - .16 * q, sx=1 + .1 * q, legs=.6 * q)
        if t < T_ZNA:
            st.update(turn=-.5, look=(-.35, .75), tilt=-7 * sm(t, T_LAND, T_REACH))
        else:                                                     # «Знаешь»: морда к зрителю через три четверти
            v = sm(t, T_ZNA, T_ZNA + .32)
            st.update(turn=lerp(-.5, 0.0, v), look=(lerp(-.35, 0.0, v), lerp(.75, 0.0, v)), tilt=lerp(-7, 0, v))
            if t > T_POCH:                                        # «почему»: наклон головы, ухо дёрнулось
                st["tilt"] = 9 * sm(t, T_POCH, T_POCH + .18) + damp(t, T_POCH + .18, 2.0, 3.0, 6.0)
                st["ear"] = damp(t, T_POCH + .05, 16.0, 6.0, 7.0)
                st["perk"] = .4 * sm(t, T_POCH, T_POCH + .2)
    catsvg = people.cat_svg(cx_, cy_, CAT_K, st, t)
    # лапа вниз к ящику: тянет ручку, потом достаёт открытку
    paw = ""
    reach = sm(t, T_REACH - .12, T_REACH) * (1 - sm(t, T_OUT + .05, T_OUT + .3))
    chest = (cx_ + 30 * CAT_K, cy_ - 80 * CAT_K)
    pull = sm(t, T_OPEN, T_PULL)
    ins = sc["inside"]
    tip_card = None
    if reach > .01:
        tgt = (HANDLE[0] - 40, HANDLE[1] + 30 * pull)
        if t > T_PULL and ins is not None:                        # лапа в ящике, подцепила открытку и тянет вверх
            dip = sm(t, T_PULL, T_PULL + .1)
            up = sm(t, T_PULL + .1, T_OUT)
            tgt = (lerp(tgt[0], HANDLE[0] - 20, dip), lerp(lerp(tgt[1], ins[3] - 30, dip), R.DESK_TOP - 70, up))
            tip_card = tgt
        tip = lerp2((chest[0] + 10, chest[1] + 20), tgt, reach)
        paw = cat_paw_down(chest, tip, CAT_K)
    # открытка: в ящике → лапа тянет вверх → ложится на стол у кота
    card = ""
    if t > T_PULL and ins is not None:
        if tip_card is not None and t < T_OUT + .05:
            cpos = (tip_card[0] - 10, tip_card[1] + 70)
            rot = -8 + 14 * sm(t, T_PULL, T_OUT)
        else:
            v = sm(t, T_OUT + .05, T_OUT + .3)
            cpos = lerp2((HANDLE[0] - 30, R.DESK_TOP - 70 + 70), (HANDLE[0] - 120, R.DESK_TOP - 70), v)
            rot = 6 - 14 * v
        crd = PR.card(cpos[0], cpos[1], CARD_K * .8, rot, 0.0, "blank", seed=1)
        if t < T_OUT + .3:
            cid = lib.clip_rect(-2000, -2000, 6000, ins[3] + 2000 - 0)
            crd = f'<g clip-path="url(#{cid})">{crd}</g>'
            if cpos[1] + 90 > R.DRAWER[2]:
                crd += sc["drawer_front"]
        card = crd
    # пыль при приземлении
    dust = ""
    v = (t - T_LAND) / .3
    if 0 < v < 1:
        for i, dx in enumerate((-90, -40, 40, 90)):
            x0 = CAT_TOP[0] + dx * CAT_K * 1.3
            dust += line([(x0, CAT_TOP[1] + 4), (x0 + dx * .3 * v, CAT_TOP[1] - 14 - 26 * v)], 5 * (1 - v) + 1, INK, taper=.5, wmin=.2, seed=6400 + i)
    on_floor = t < T_JUMP + .12
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"],
             parts["arm_f"], parts["arm_n"], parts["body"]]
    if on_floor:
        world += [card, catsvg, sc["lamp"]]
    else:
        world += [sc["lamp"], card, paw, catsvg, dust]
    # камера: откат и дрейф; мини-тряска на прыжке; к концу наезд на морду кота
    sx1, sy1 = shake2(t, T_LAND, 7)
    cx0, cy0, s0 = R.CAM_DESK_LOW
    u = sm(t, 7.2, 8.4)
    cx = lerp(cx0 - 120, cx0 - 165, u) + 6 * math.sin(t * 1.3)
    cy = lerp(cy0 + 30, cy0 - 10, u)
    s = s0 * lerp(1.06, 1.0, u)
    hx, hy = CAT_TOP[0], CAT_TOP[1] - 170 * CAT_K
    z = sm(t, 9.2, 10.5)
    cx, cy, s = lerp(cx, hx - 40, .7 * z), lerp(cy, hy + 120, .7 * z), s * (1 + .38 * z)
    cx -= sx1
    cy -= sy1
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, .5 * math.sin(t * .8))}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')


def frame(sid, t):
    return {"s01": s01, "s03": s03, "s04": s04}[sid](t)
