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
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

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
        wr["n" if side > 0 else "f"] = (cx + side * 150 * k, cy + 18 * k)
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
    tw = 7 * math.sin(2 * math.pi * 3.1 * t + .6) * (1 - sm(t, T_PUT - .1, T_PUT + .1))
    hold = (R.HOLD[0] + 8 * math.sin(t * 5.3), R.HOLD[1] + 6 * math.cos(t * 4.1) - 10 * bump(t, T_HIT1 - .06, .2))
    down = (R.HOLD[0] - 10, table_y(TK))
    u = sm(t, T_PUT, T_LAND)
    T = (lerp(hold[0], down[0], u), lerp(hold[1], down[1], u ** 1.6))
    rot = -6 + tw
    # после посадки — тикает: мелкая дрожь и подскок на касании
    shake = 0.0
    if t > T_LAND:
        shake = 2.2 + 5 * math.exp(-10 * (t - T_LAND))
        T = (T[0], T[1] - 9 * bump(t, T_LAND, .14))
    leaf = 14 * math.sin(2 * math.pi * 2.3 * t) + damp(t, T_LAND, 22, 3.5, 5)
    timer = PR.tomato_timer(T[0], T[1], TK, rot, wedge=wedge, shake=shake, leaf_swing=leaf, t=t, seed=1)
    gb, gf, wr = timer_grips(T, TK, rot, seed=0)
    # руки: держат → после посадки отпускают и отходят к краю стола
    rel = sm(t, T_LAND - .02, T_LAND + .2)
    wn = lerp2(wr["n"], (wr["n"][0] + 40, R.DESK_TOP - 70), rel)
    wf = lerp2(wr["f"], (wr["f"][0] - 50, R.DESK_TOP - 60), rel)
    hands = {"f": {"kind": "none"}, "n": {"kind": "none"}}
    if rel > .5:
        hands = {"f": {"curl": (.3, .3, .35, .4), "thumb": .35, "dir": (1, .25)}, "n": {"curl": (.3, .35, .4, .45), "thumb": .4, "dir": (1, .3)}}
        gb = gf = ""
    e = ex("unsure", brows="up", mouth="smile", smile=.45 + .25 * sm(t, T_DV, T_MIN), lid=.86, look=(.62, .5 - .25 * u))
    e["closed"] = blinkv(t, [1.48])
    full, parts = dima_layers(e, {"f": ("ik", wf, -1), "n": ("ik", wn, -1)}, hands,
                              lean_add=.06 + .02 * math.sin(t * 3.1) + .04 * u, head_add=.03 * math.sin(t * 2.2 + .4) + .05 * u)
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
             parts["arm_f"], parts["body"], parts["arm_n"], gb, timer, gf, ticks, sc["lamp"]]
    # камера: влёт к таймеру и лицу, второй удар на «двадцать», мини-тряска на посадке таймера
    k, rc, side = hook_cam(t, T_DV)
    sx1, sy1 = shake2(t, T_LAND, 9)
    cx0, cy0, s0 = R.CAM_DESK_CLOSE
    cx = cx0 + side - sx1 + 14 * math.sin(t * 2.1)
    cy = cy0 - sy1 + 18 * sm(t, T_PUT, T_LAND)
    s = s0 * k * (1 + .035 * sm(t, .3, 1.6))
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, rc)}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')


def frame(sid, t):
    return {"s01": s01}[sid](t)
