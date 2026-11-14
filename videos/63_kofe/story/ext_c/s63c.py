"""Рилс 63 «кофе», группа C — утренняя кухня: s01 (хук: глоток кофе → «обезвоживает»: губы трескаются, пот испаряется, трещина по
столешнице), s03 (стакан воды залпом через силу), s18 (петля к хуку: две кружки, спохватывается, смеётся; кот лакает из блюдца).
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

E = people.EXPR["dima"]
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
S = 1.0                                   # масштаб Димы на кухне
HIPX = R.K_DIMA[0]
HIPY = R.K_FLOOR - (people.LEG_LEN - 12) * S * people.HEIGHT["dima"]
MUG_K = 1.0                               # кружка в руке (110×130·k)
HC = (-89.0, -70.0)                       # центр ручки зеркальной кружки (ручка слева) от центра дна, в ед. кружки


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»").lower() == word:
            return w["start"]
    raise KeyError(word)


T_KOFE, T_OBEZ = wt("кофе"), wt("обезвоживает")                     # 0.64, 1.01
T_DIMA, T_TAK, T_DELAL = wt("дима", 4), wt("так", 4), wt("делал", 4)  # 4.80, 5.34, 5.74
T_ZAPIVAL, T_KOFE2, T_VODOY = wt("запивал", 36), wt("кофе", 36.5), wt("водой", 36.5)   # 36.52, 36.93, 37.43


def lerp(a, b, u):
    return a + (b - a) * u


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def decay(t, t0, k=9.0, fr=22.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def shake2(t, t0, amp, k=9.0, fr=19.0):
    return amp * decay(t, t0, k, fr), amp * .7 * decay(t, t0 + .013, k, fr * 1.13)


def blinkv(t, times, dur=.15):
    v = 0.0
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def ex(name, **kw):
    e = dict(E[name])
    e.update(kw)
    return e


def rotp(p, deg):
    a = math.radians(deg)
    return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))


def hook_cam(t, t_hit):
    """Влёт правила 28/29: с 40 % дальше (1/(1+0.4)) за 0.22 с, перелёт 5 % с отскоком, поворот −3.6° с возвратом, занос сбоку;
    второй удар +9 % на ударном слоге. Возвращает (масштаб-множитель, поворот, занос)."""
    u = clamp(t / .22)
    e = ease_out(u, 3)
    s = 1 / 1.4 + (1 - 1 / 1.4) * e
    if t > .22:
        s += .055 * math.exp(-7 * (t - .22)) * math.sin(2 * math.pi * 2.2 * (t - .22) + math.pi / 2)
    rot = -3.6 * (1 - e) + damp(t, .22, 1.2, 2.0, 6.0)
    side = -55 * (1 - e)
    hit = 0.0
    if t > t_hit:
        h = t - t_hit
        hit = .09 * math.exp(-5.5 * h) * (1 if h > .03 else h / .03)
    return s * (1 + hit), rot, side


# ═════════════════════════ кружка и стакан в руке ═════════════════════════
def held(W, rot, kind="coffee", fill=1.0, steam=0.0, t=0.0, seed=0, k=MUG_K, gfill=1.0, splash=0.0):
    """Предмет в ближней руке: W — запястье в мире, rot — наклон (− — верх к лицу Димы, он смотрит вправо).
    kind "coffee" — кружка ручкой к ладони (зеркальная, хват за ручку пальцами), "glass" — стакан, обхват пальцами.
    Всё строится в локальной системе запястья и поворачивается вместе (кисть не отстаёт от кружки)."""
    hk = S * 1.0
    if kind == "coffee":
        hc = (HC[0] * k, HC[1] * k)
        mug = f'<g transform="scale(-1 1)">{PR.coffee_mug(0, 0, k, 0, "white", fill, steam, t, seed=seed)}</g>'
        back, front = people.handle_grip("dima", hc, k=hk, side=-1, seed=960 + seed)
        # запястье — у края ладони за ручкой (ладонь от ручки на ~60·k влево)
        wl = (hc[0] - 70 * hk, hc[1] + 6 * hk)
    else:
        R0 = 46 * k
        mug = PR.glass(0, 0, k, 0, gfill, t, 0.0, seed=seed)
        back, front = people.grip_svg("dima", (0, -66 * k), R0, -1, k=hk, seed=980 + seed)
        wl = (-R0 - 52 * hk, -60 * k)
    body = back + mug + front
    g = f'<g transform="translate({W[0]:.2f} {W[1]:.2f}) rotate({rot:.3f}) translate({-wl[0]:.2f} {-wl[1]:.2f})">{body}</g>'
    if splash > 0.01:
        top = np.array(W) + np.array(rotp((-wl[0], -wl[1] - 140 * k), rot))
        g += PR.splash_drops(float(top[0]), float(top[1]), k, splash, seed + 3)
    return g


def rim_at(W, rot, kind="coffee", k=MUG_K):
    """Где окажется центр горла предмета (для расчёта, куда вести запястье, чтобы край был у губ)."""
    hk = S
    if kind == "coffee":
        hc = (HC[0] * k, HC[1] * k)
        wl = (hc[0] - 70 * hk, hc[1] + 6 * hk)
        top = (0, -126 * k)
    else:
        R0 = 46 * k
        wl = (-R0 - 52 * hk, -60 * k)
        top = (0, -140 * k)
    d = rotp((top[0] - wl[0], top[1] - wl[1]), rot)
    return (W[0] + d[0], W[1] + d[1])


def mouth_of(fig, head_ang=0.0):
    """Мировая точка рта по голове фигуры (локально около (60, 92) от узла головы)."""
    hx, hy = fig["head"]
    d = rotp((62 * S, 96 * S), math.degrees(head_ang))
    return hx + d[0], hy + d[1]


def wrist_for_rim(mouth, rot, kind="coffee", k=MUG_K, gap=(18, 4)):
    """Запястье, при котором край предмета касается рта (сдвиг gap вправо/вниз от рта)."""
    r0 = rim_at((0.0, 0.0), rot, kind, k)
    return (mouth[0] + gap[0] - r0[0], mouth[1] + gap[1] - r0[1])


def lip_cracks(m, u, seed=0):
    """Губы трескаются: короткие ломаные штрихи на губах."""
    if u <= .02:
        return ""
    o = []
    for i, (dx, dy, L) in enumerate(((-16, -4, 16), (-2, -6, 14), (12, -3, 15), (-8, 6, 12), (8, 7, 12))):
        if i / 5 > u * 1.2:
            break
        a = (m[0] + dx * S, m[1] + dy * S)
        o.append(line([a, (a[0] + 3 * S, a[1] + L * .5 * S * (1 if dy > 0 else -1)), (a[0] + 1, a[1] + L * S * (1 if dy > 0 else -1))], 3.4, INK, taper=.5,
                      wmin=.2, seed=6100 + seed + i))
    return "".join(o)


def dima(t, expr, lean=0.0, head_ang=0.0, near=None, far=None, hands=None, layers=None):
    kw = people.stand_kw(HIPX, HIPY, S)
    arms = {"f": far or ("ang", 0.16, 0.2), "n": near or ("ang", -0.08, 0.3)}
    return people.figure("dima", HIPX, HIPY, S, expr, lean=lean, head_ang=head_ang, arms=arms, hands=hands or {}, layers=layers, **kw)


# ═════════════════════════ s01: хук ═════════════════════════
def s01(t):
    lib.dyn_begin()
    # ход: 0…T_KOFE подносит и запрокидывает, T_KOFE глоток (кадык, глаза закрыты), к T_OBEZ опускает к груди, испуг
    tip = sm(t, -.25, T_KOFE)                       # 0 → 1: от «у губ» к «запрокинул»
    down = sm(t, T_OBEZ - .12, T_OBEZ + .22)        # опускает кружку на «обезвоживает»
    gulp = bump(t, T_KOFE, .3)
    lean = -.14 * tip * (1 - down) + .06 * down - .02 * gulp
    head_ang = -.42 * tip * (1 - down) + .10 * down + .03 * damp(t, T_OBEZ, 1.0, 4, 6)
    if t < T_OBEZ - .05:
        e = ex("relief", closed=min(1.0, .3 + tip), look=(.3, -.2))
    else:
        e = ex("scared", look=(.75, .65))
        e["closed"] = 0.0
    fig0 = dima(t, e, lean, head_ang)
    m = mouth_of(fig0, lean * .5 + head_ang)
    rot_drink = lerp(-62, -112, tip) - 8 * gulp
    rot_hold = -6.0 + 4 * damp(t, T_OBEZ + .1, 1.0, 3, 5)
    rot = lerp(rot_drink, rot_hold, down)
    Wd = wrist_for_rim(m, rot_drink, gap=(22, 6))
    Wh = (HIPX + 300 * S, HIPY - 330 * S)           # у груди, перед собой — смотрит в кружку
    W = (lerp(Wd[0], Wh[0], down), lerp(Wd[1], Wh[1], down) + 10 * bump(t, T_KOFE, .3))
    far = ("ik", (HIPX + 230 * S, R.K_TABLE[2] - 50), -1)
    fig = dima(t, e, lean, head_ang, near=("ik", W, -1), far=far, hands={"n": {"kind": "none"}, "f": {"dir": (1, .25), "curl": (.25, .3, .35, .4), "thumb": .3}},
               layers=("legs", "pelvis", "arm_f", "body"))
    arm_n = dima(t, e, lean, head_ang, near=("ik", W, -1), far=far, hands={"n": {"kind": "none"}}, layers=("arm_n",))
    Wr = arm_n["wrist"]["n"]
    fill = 1.0 - .55 * sm(t, .2, T_KOFE + .2)
    cup = held(Wr, rot, "coffee", fill=fill, steam=1.0 - .6 * tip * (1 - down), t=t, seed=1)
    m = mouth_of(fig, lean * .5 + head_ang)
    room = R.kitchen(t, "morning", clock=PR.clock_hm(7, 40), rack_mug=False)
    # «обезвоживает»: трещина по столу, губы, пот → дымок
    u_ob = sm(t, T_OBEZ, T_OBEZ + .4)
    crack = R.table_crack(u_ob, seed=1, x=640.0)
    lips = lip_cracks(m, sm(t, T_OBEZ + .02, T_OBEZ + .3), 0)
    hx, hy = fig["head"]
    sweat = ""
    if t > T_OBEZ - .02:
        q = clamp((t - T_OBEZ + .02) / .5)
        sx, sy = hx - 40 * S, hy - 40 * S + 70 * q * S
        if q < .6:
            sweat = PR.sweat(sx, sy, 1.3 * S * (1 - .5 * q / .6))
        sweat += PR.evap(sx + 4, sy - 30, 1.2 * S, clamp((q - .3) / .3), t, seed=3)
    # вздрог на «обезвоживает»: штрихи-испуг у головы
    jolt = ""
    v = (t - T_OBEZ) / .3
    if 0 < v < 1:
        for i in range(4):
            th = -2.2 + i * .45
            r0, r1 = 190 + 40 * v, 240 + 60 * v
            jolt += line([(hx + 30 + math.cos(th) * r0, hy + math.sin(th) * r0), (hx + 30 + math.cos(th) * r1, hy + math.sin(th) * r1)], 7, INK, taper=.5,
                         wmin=.2, seed=6200 + i)
    world = [room["bg"], fig["svg"], room["table"], crack, arm_n["svg"], cup, lips, sweat, jolt]
    # камера: влёт на лицо и кружку, второй удар на «обезвоживает», тряска
    k, rot_c, side = hook_cam(t, T_OBEZ)
    sx1, sy1 = shake2(t, T_OBEZ + .02, 14)
    base = 1.25
    cx = 545 + side - sx1 + 12 * math.sin(t * 1.7)
    cy = 840 - 40 * sm(t, 0, 1.4) - sy1
    sc = base * k
    set_ink(sc)
    body = f'<g transform="{lib.cam(cx, cy, sc, rot_c)}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#e9dcc4"/>{body}')


def frame(sid, t):
    return {"s01": s01}[sid](t)
