"""Рилс 70 «помидорка», группа C — ночь у стола: s01 (хук: пальцы крутят таймер-помидорку с кадра 0, щелчки, клин на полкруга,
таймер на стол, тикает; лицо Димы с надеждой), s04 (средний план сбоку: берёт таймер, заводит, ставит у ноутбука — подпрыгнул),
s05 (через плечо: плюхается на стул, ускоренное время — полоса света ползёт, клин тает, затылок склоняется к пятнышку на стене).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Комната — common/room.py, люди и кот — common/people.py,
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
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
BS = 1.0
SX, SY = R.SIT
SC = BS * people.HEIGHT["dima"]
FEET = {"n": ((SX + 300 * BS, R.FL - 52), 0.0), "f": ((SX + 250 * BS, R.FL - 50), 0.0)}


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»").lower() == word:
            return w["start"]
    raise KeyError(word)


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


# ═════════════════════════ общее: Дима за столом, таймер в двух руках ═════════════════════════
T_POM, T_DV, T_MIN = wt("помидорка"), wt("двадцать"), wt("минут")           # 0.14 0.61 1.03
T_HIT1 = 0.30          # ударный слог «поМИдорка»
TK = .95               # масштаб таймера в руках крупно


def dima_layers(e, arms, hands, lean_add=0.0, head_add=0.0, shrug=0.0, pose="sit_desk"):
    kw = dict(feet=FEET, arms=arms, hands=hands, lean_add=lean_add, head_add=head_add, shrug=shrug)
    full = people.dima(SX, SY, BS, e, pose, **kw)
    parts = {k: people.dima(SX, SY, BS, e, pose, layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    return full, parts


def timer_grips(T, k, rot, seed=0, sides=(-1, 1)):
    """Пальцы обеих кистей обхватили таймер с боков (ладонь за ним, пальцы и большой палец спереди по краю).
    Возвращает (back, front, wrists): wrists — куда вести запястья (ik)."""
    back, front, wr = [], [], {}
    rr = math.radians(rot)
    for side in sides:
        lx, ly = side * (PR.TOMATO_RX - 52) * k, 22 * k
        cx = T[0] + lx * math.cos(rr) - ly * math.sin(rr)
        cy = T[1] + lx * math.sin(rr) + ly * math.cos(rr)
        b, f_ = people.grip_svg("dima", (cx, cy), 52 * k, side, k=k * 1.05, h=64, seed=930 + seed + side)
        back.append(b)
        front.append(f_)
        wr["f" if side > 0 else "n"] = (cx + side * (112 if side < 0 else 70) * k, cy + (40 if side < 0 else 70) * k)
    return "".join(back), "".join(front), wr


def table_y(k):
    """Центр таймера, стоящего на столе (дно на середине глубины столешницы)."""
    return R.DESK_TOP - 42 - PR.TOMATO_RY * k


# ═════════════════════════ s01: хук ═════════════════════════
def clicks(t, times, step):
    """Ступенчатый рост клина: каждый щелчок — быстрый доворот на step за 0.05 с."""
    v = 0.0
    for a in times:
        v += step * ease_out(clamp((t - a) / .05), 2)
    return v


S01_CLICKS = [0.0, .07, .14, .22, .30, .40, .50]
S01_TURN = [T_DV + .0, T_DV + .1, T_DV + .2, T_DV + .3, T_DV + .42, T_DV + .55]
T_PUT = 1.10           # таймер опускается на стол
T_LAND = 1.30


def s01(t):
    lib.dyn_begin()
    sc = R.desk_scene(t, "night")
    # клин: щелчки с кадра 0 (мелкими шагами), на «двадцать пять минут» раскрывается почти на полкруга
    wedge = .02 + clicks(t, S01_CLICKS, .012) + clicks(t, S01_TURN, (PR.WEDGE_25 - .02 - .012 * len(S01_CLICKS)) / len(S01_TURN))
    # таймер в руках: вертится (поворот туда-обратно на каждом щелчке), потом опускается на стол
    tw = 10 * math.sin(2 * math.pi * 3.4 * t + 1.1) * (1 - sm(t, T_PUT - .1, T_PUT + .1))
    hold = (R.HOLD[0] + 14 * math.sin(t * 7.3 + .8), R.HOLD[1] + 10 * math.cos(t * 6.1) - 16 * bump(t, T_HIT1 - .06, .2))
    down = (R.HOLD[0] - 10, table_y(TK))
    hold = (hold[0], hold[1] - 40 * (1 - sm(t, T_DV, T_PUT)))
    u = sm(t, T_PUT, T_LAND)
    T = (lerp(hold[0], down[0], u), lerp(hold[1], down[1], u ** 1.6))
    rot = -6 + tw
    # после посадки — тикает: мелкая дрожь и подскок на касании
    shake = 0.0
    if t > T_LAND:
        shake = 2.2 + 5 * math.exp(-10 * (t - T_LAND))
        T = (T[0], T[1] - 9 * bump(t, T_LAND, .14))
    leaf = 20 * math.sin(2 * math.pi * 2.6 * t + .9) + damp(t, T_LAND, 22, 3.5, 5)
    timer = PR.tomato_timer(T[0], T[1], TK, rot, wedge=wedge, shake=shake, leaf_swing=leaf, t=t, seed=1)
    gb, gf, wr = timer_grips(T, TK, rot, seed=0, sides=(-1,))
    # руки: держат → после посадки отпускают и отходят к краю стола
    rel = sm(t, T_LAND - .02, T_LAND + .2)
    wn = lerp2(wr["n"], (T[0] - 200, R.DESK_TOP - 46), rel)
    hands = {"f": {"kind": "none"}, "n": {"kind": "none"}}
    if rel > .5:
        hands = {"f": {"kind": "none"}, "n": {"curl": (.3, .35, .4, .45), "thumb": .4, "dir": (1, .3)}}
        gb = gf = ""
    e = ex("unsure", brows="up", mouth="smile", smile=.45 + .25 * sm(t, T_DV, T_MIN), lid=.86, look=(.78, .3 + .3 * u))
    e["closed"] = blinkv(t, [1.48])
    full, parts = dima_layers(e, {"f": ("ang", 0.25, 0.2), "n": ("ik", wn, -1)}, hands,
                              lean_add=.06 + .035 * math.sin(t * 4.3 + .5) + .04 * u, head_add=.05 * math.sin(t * 3.6 + .4) + .05 * u)
    lap = PR.laptop(R.LAPTOP[0], R.LAPTOP[1], .72, 1.0, "dark", t=t, seed=1, turn=.55)
    # тиканье: короткие штрихи-тики у таймера на столе
    ticks = ""
    if t > T_LAND + .05:
        ph = ((t - T_LAND) * 2) % 1
        if ph < .45:
            q = ph / .45
            for i, ang in enumerate((-40, -15)):
                a = math.radians(ang - 90)
                r0, r1 = 150 * TK + 16 * q, 178 * TK + 22 * q
                ticks += line([(T[0] + 90 * TK + math.cos(a) * r0 * .5, T[1] - 60 * TK + math.sin(a) * r0 * .4),
                               (T[0] + 90 * TK + math.cos(a) * r1 * .5, T[1] - 60 * TK + math.sin(a) * r1 * .4)], 5 * (1 - q) + 1.5, INK,
                              taper=.5, wmin=.2, seed=5100 + i)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], lap, parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"],
             parts["arm_f"], parts["body"], gb, timer, gf, parts["arm_n"], ticks, sc["lamp"]]
    # камера: влёт к таймеру и лицу, второй удар на «двадцать», мини-тряска на посадке таймера
    k, rc, side = hook_cam(t, T_DV)
    sx1, sy1 = shake2(t, T_LAND, 9)
    cx0, cy0, s0 = R.CAM_DESK_CLOSE
    if os.environ.get("NOCAM"):          # замер движения рисунка без камеры (правила 25–26)
        body = f'<g transform="{lib.cam(cx0, cy0, s0)}">{"".join(world)}</g>'
        set_ink(s0)
        return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')
    cx = cx0 + side - sx1 + 14 * math.sin(t * 2.1)
    cy = cy0 - sy1 + 18 * sm(t, T_PUT, T_LAND)
    s = s0 * k * (1 + .035 * sm(t, .3, 1.6))
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, rc)}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')


# ═════════════════════════ s04: средний план сбоку — завёл и поставил ═════════════════════════
T_DIMA, T_POST, T_TAIM = wt("дима"), wt("поставил"), wt("таймер")          # 5.11 5.33 5.74
TK4 = .82
T4_DESK0 = (R.TIMER_DESK[0] - 10, table_y(TK4))
T4_DESK1 = (R.TIMER_DESK[0] + 30, table_y(TK4))
T4_UP = (R.TIMER_DESK[0] + 60, 745.0)


def s04(t):
    lib.dyn_begin()
    sc = R.desk_scene(t, "night")
    # таймер: лежит → «Дима» поднимает → «поставил» резкий завод поворотом (клин рывками до полкруга) → «таймер» ставит, подскок
    pick = sm(t, T_DIMA - .05, T_POST - .02)
    put = sm(t, T_TAIM - .2, T_TAIM)
    T = lerp2(lerp2(T4_DESK0, T4_UP, pick), T4_DESK1, put)
    T = (T[0], T[1] - 50 * math.sin(math.pi * pick) * (1 - pick) * 0)
    twist = sm(t, T_POST, T_POST + .12) - .35 * sm(t, T_POST + .12, T_POST + .3)        # рывок поворота с возвратом руки
    rot = -4 - 26 * twist * (1 - put) + 4 * math.sin(t * 9) * (1 - put) * pick
    wedge = PR.WEDGE_25 * (sm(t, T_POST, T_POST + .1) * .55 + sm(t, T_POST + .14, T_POST + .24) * .3 + sm(t, T_POST + .28, T_POST + .36) * .15)
    shake = 0.0
    if t > T_TAIM:
        shake = 2.0 + 6 * math.exp(-9 * (t - T_TAIM))
        T = (T[0], T[1] - 26 * bump(t, T_TAIM + .02, .2) - 8 * bump(t, T_TAIM + .22, .12))
    leaf = 12 * math.sin(2 * math.pi * 1.9 * t) + damp(t, T_TAIM, 26, 3.5, 4.5) + damp(t, T_POST, -18, 3, 5)
    timer = PR.tomato_timer(T[0], T[1], TK4, rot, wedge=wedge, shake=shake, leaf_swing=leaf, t=t, seed=1)
    holding = pick > .02 and t < T_TAIM + .04
    gb = gf = ""
    if holding:
        gb, gf, wr = timer_grips(T, TK4, rot, seed=0, sides=(-1,))
        wn = wr["n"]
        hands = {"f": {"kind": "none"}, "n": {"kind": "none"}}
    else:
        if t < T_DIMA:      # тянется к таймеру с кадра 0
            wn = lerp2((SX + 250, SY - 330), (T[0] - 150, T[1] + 10), sm(t, 4.9, T_DIMA))
        else:               # отпустил — ладонь отходит, ложится на стол
            wn = lerp2((T[0] - 150, T[1] + 10), (T[0] - 210, R.DESK_TOP - 46), sm(t, T_TAIM + .04, T_TAIM + .3))
        hands = {"f": {"kind": "none"}, "n": {"curl": (.35, .4, .45, .5), "thumb": .45, "dir": (1, .25)}}
    e = ex("unsure", brows="up", mouth="pressed", lid=1.0, look=(.7, .55 - .3 * pick + .3 * put))
    if t > T_TAIM + .1:
        e = dict(e, mouth="smile", smile=.5)
    e["closed"] = blinkv(t, [6.15])
    lean = .08 + .06 * pick - .04 * put + .025 * math.sin(t * 3.7) + .05 * bump(t, T_POST + .05, .25)
    full, parts = dima_layers(e, {"f": ("ang", 0.25, 0.2), "n": ("ik", wn, -1)}, hands, lean_add=lean,
                              head_add=.04 * math.sin(t * 2.9) + .06 * bump(t, T_TAIM, .3), shrug=.25 * bump(t, T_POST + .05, .3))
    lap = PR.laptop(R.LAPTOP[0] + 40, R.LAPTOP[1], .72, 1.0, "dark", t=t, seed=1, turn=.55)
    # щелчок: короткие штрихи у таймера
    hit = ""
    v = (t - T_TAIM) / .3
    if 0 < v < 1:
        for i, ang in enumerate((-150, -120, -60, -30)):
            a = math.radians(ang)
            r0 = 110 * TK4 + 40 * v
            hit += line([(T[0] + math.cos(a) * r0, T[1] + math.sin(a) * r0), (T[0] + math.cos(a) * (r0 + 46 * (1 - v * .5)), T[1] + math.sin(a) * (r0 + 46 * (1 - v * .5)))],
                        6 * (1 - v) + 1.5, INK, taper=.5, wmin=.2, seed=5400 + i)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], lap, parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"],
             parts["arm_f"], parts["body"], gb, timer, gf, parts["arm_n"], hit, sc["lamp"]]
    sx1, sy1 = shake2(t, T_TAIM + .01, 12)
    cx0, cy0, s0 = R.CAM_SIDE_MID
    cx = cx0 - 60 + 45 * sm(t, 4.9, 6.6) - sx1
    cy = cy0 - 20 * sm(t, 4.9, 6.6) - sy1
    s = s0 * (1 + .05 * sm(t, 4.9, 6.6) + .03 * bump(t, T_POST + .02, .3))
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, .6 * math.sin(t * .9))}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')


# ═════════════════════════ s05: через плечо — сел и смотрит в стену ═════════════════════════
T_SEL, T_DV5, T_MIN5, T_SMOT, T_STENU = wt("сел"), wt("двадцать", 6.0), wt("минут", 7.0), wt("смотрел"), wt("стену")   # 6.32 6.85 7.25 7.56 8.05
TL0, TL1 = T_DV5 - .05, T_MIN5 + .3      # ускоренное время


def s05(t):
    lib.dyn_begin()
    tl = sm(t, TL0, TL1)
    v = R.wall_view(t, "night", tl, spot=1.0)
    # плюх: Дима опускается в кадр сверху, стул пружинит, плечи подпрыгивают и успокаиваются
    drop = ease_in(clamp((t - (T_SEL - .2)) / .2), 2)
    ny = R.DIMA_V[1] - 300 * (1 - drop) + damp(t, T_SEL, 34, 2.6, 5.5)
    squash = max(0.0, damp(t, T_SEL, 1.0, 2.6, 5.5))
    bounce = damp(t, T_SEL, 2.2, 2.6, 5.0)
    breath = 4 * math.sin(t * 2.4) * (1 - tl * .5)
    # «смотрел в стену»: затылок медленно склоняется набок
    tilt = 2 * math.sin(t * 1.7) * (1 - tl) + 11 * sm(t, T_SMOT, T_STENU + .2) + 2 * damp(t, T_SEL, 1.0, 3, 5)
    nx = R.DIMA_V[0] + 6 * math.sin(t * 1.3) * (1 - tl)
    back = people.dima_back(nx, ny + breath, 1.9, tilt=tilt, shrug=.15 + .25 * sm(t, T_SMOT, T_STENU + .2), t=t)
    # таймер на столе: клин тает до нуля за «двадцать пять минут», тикает (в ускоренном времени — чаще)
    wedge = PR.WEDGE_25 * (1 - tl)
    tx, ty = R.TIMER_V
    timer = PR.tomato_timer(tx, ty, .66, -3, wedge=wedge, shake=1.6 + 2.5 * tl * (1 - tl) * 4, leaf_swing=4 * math.sin(t * 3), t=t, seed=1)
    lap = PR.laptop(R.LAPTOP_V[0], R.LAPTOP_V[1], .7, 1.0, "page", t=t, seed=1)
    world = [v["bg"], v["desk"], v["pool"], lap, timer, v["lamp"], back["svg"], v["chair"](squash, bounce)]
    # камера: тряска на плюхе, затем ровный наезд через плечо к пятнышку на стене
    sx1, sy1 = shake2(t, T_SEL + .02, 14)
    cx0, cy0, s0 = R.CAM_SHOULDER
    z = ease_io(clamp((t - 6.2) / 2.5))
    cx = lerp(cx0, R.WALL_SPOT_V[0] - 20, .5 * z) - sx1
    cy = lerp(cy0, 900.0, z) - sy1
    s = s0 * (1 + .22 * z)
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s)}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')


def frame(sid, t):
    return {"s01": s01, "s04": s04, "s05": s05}[sid](t)
