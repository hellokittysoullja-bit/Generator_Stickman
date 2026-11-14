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
    Wh = (HIPX + 250 * S, HIPY - 330 * S)           # у груди, перед собой — смотрит в кружку
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


# ═════════════════════════ s03: вода залпом через силу ═════════════════════════
TY = R.K_TABLE[2] - 46                       # линия дна предметов на столе
MUG_X, GLASS_X, JUG_X = 610.0, 790.0, 960.0


def _wl(kind):
    if kind == "coffee":
        return (HC[0] * MUG_K - 70 * S, HC[1] * MUG_K + 6 * S)
    return (-46 * MUG_K - 52 * S, -60 * MUG_K)


def wrist_for_bottom(bx, by, kind):
    w = _wl(kind)
    return (bx + w[0], by + w[1])


def mug_on_table(x, fill=0.0, t=0.0, seed=1, steam=0.0):
    return f'<g transform="translate({x:.2f} {TY:.2f}) scale(-1 1)">{PR.coffee_mug(0, 0, MUG_K, 0, "white", fill, steam, t, seed=seed)}</g>'


def lerp2(a, b, u):
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))


def s03(t):
    lib.dyn_begin()
    P_hold = (HIPX + 230 * S, HIPY - 260 * S)
    W_mug = wrist_for_bottom(MUG_X, TY, "coffee")
    W_gl = wrist_for_bottom(GLASS_X, TY, "glass")
    # 1) несёт пустую кружку и ставит на «Дима»; 2) рука к стакану; 3) «так» берёт; 4) «делал» залпом
    put = sm(t, T_DIMA - .5, T_DIMA)
    reach = sm(t, T_DIMA + .12, T_TAK)
    lift = sm(t, T_TAK + .05, T_DELAL)
    drink = sm(t, T_DELAL - .05, T_DELAL + .55)
    gulp = .5 + .5 * math.sin(2 * math.pi * 3.2 * max(0.0, t - T_DELAL)) if t > T_DELAL else 0.0
    lean = -.03 - .08 * drink
    head_ang = .12 * (1 - lift) - .34 * drink + .015 * gulp * drink
    if t < T_TAK:
        e = ex("doubt", look=(.6, .55))
        e["closed"] = blinkv(t, [4.45])
    elif t < T_DELAL - .05:
        e = ex("doubt", look=(.7, .2))
    else:
        e = ex("wince")
    fig0 = dima(t, e, lean, head_ang)
    m = mouth_of(fig0, lean * .5 + head_ang)
    rot_d = lerp(-30, -96, drink) - 4 * gulp
    W_mouth = wrist_for_rim(m, rot_d, "glass", gap=(16, 4))
    hands = {"n": {"kind": "none"}}
    if t < T_DIMA:
        W = lerp2(P_hold, W_mug, put)
        rot, item = 4 * (1 - put), "mug"
    elif t < T_TAK:
        W = lerp2(W_mug, W_gl, reach)
        W = (W[0], W[1] - 60 * math.sin(math.pi * reach))
        rot, item = 0.0, None
        hands = {"n": {"dir": (1, .35), "spread": .3, "curl": (.2, .25, .3, .35), "thumb": .25}}
    else:
        W_up = (W_gl[0] + 30, W_gl[1] - 180)
        W = lerp2(W_gl, W_up, lift) if lift < 1 or drink <= 0 else W_up
        if drink > 0:
            W = lerp2(W_up, W_mouth, sm(t, T_DELAL - .05, T_DELAL + .2))
        rot, item = lerp(0, -30, lift) if drink <= 0 else rot_d, "glass"
    sh_up = 24 * drink                               # плечи вверх, через силу
    far = ("ik", (HIPX + 220 * S, R.K_TABLE[2] - 52 - 4 * drink), -1)
    hf = {"f": {"dir": (1, .25), "curl": (.6, .65, .7, .7), "thumb": .5}}
    fig = dima(t, e, lean, head_ang, near=("ik", W, -1), far=far, hands=dict(hands, **hf), layers=("legs", "pelvis", "arm_f", "body"))
    arm_n = dima(t, e, lean, head_ang, near=("ik", W, -1), far=far, hands=dict(hands, **hf), layers=("arm_n",))
    Wr = arm_n["wrist"]["n"]
    room = R.kitchen(t, "morning", clock=PR.clock_hm(7, 45))
    on_table = [PR.jug(JUG_X, TY + 6, 1.0, fill=.55, seed=2)]
    held_svg = ""
    if item == "mug":
        held_svg = held(Wr, rot, "coffee", fill=0.0, t=t, seed=1)
    else:
        on_table.append(mug_on_table(MUG_X, 0.0, t))
    gfill = 1.0 - .75 * sm(t, T_DELAL + .05, T_DELAL + .6)
    if item == "glass":
        held_svg = held(Wr, rot, "glass", t=t, seed=4, gfill=gfill)
    else:
        on_table.append(PR.glass(GLASS_X, TY, MUG_K, 0, 1.0, t, 0.0, seed=4))
    # капли пота и «через силу»: штрихи у щёк
    hx, hy = fig["head"]
    strain = ""
    if drink > .3:
        for i in range(3):
            ph = (t * 3 + i / 3) % 1.0
            a = (hx - 120 * S - 10 * i, hy - 60 + 40 * i)
            strain += line([a, (a[0] - 30 - 20 * ph, a[1] - 6)], 6, INK, taper=.5, wmin=.2, seed=6300 + i)
        q = clamp((t - T_DELAL - .2) / .6)
        strain += PR.sweat(hx - 30 * S, hy - 60 * S + 50 * q, 1.2 * S)
    world = [room["bg"], fig["svg"], room["table"], "".join(on_table), arm_n["svg"], held_svg, strain]
    if sh_up:
        pass
    # камера: медленный наезд на лицо, мини-тряска на «делал»
    u = sm(t, 4.2, 6.4)
    sx1, sy1 = shake2(t, T_DELAL, 9)
    cx = lerp(600, 600, u) - sx1
    cy = lerp(760, 620, u) - sy1
    sc = lerp(1.30, 1.62, u)
    set_ink(sc)
    body = f'<g transform="{lib.cam(cx, cy, sc, .6 * math.sin(t * 1.1))}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#e9dcc4"/>{body}')


# ═════════════════════════ s18: петля к хуку ═════════════════════════
CAT18 = (888.0, TY + 4)            # точка между задних лап кота на столе
CAT18_K = .8
SAUCER18 = (884.0, TY + 40)
GLASS18_X = 690.0                  # куда ставит стакан на «водой»


def s18(t):
    lib.dyn_begin()
    sip = sm(t, T_ZAPIVAL - .25, T_ZAPIVAL + .12) * (1 - sm(t, T_KOFE2 - .05, T_KOFE2 + .25))
    reachw = sm(t, T_ZAPIVAL + .05, T_KOFE2 - .02)            # машинально тянет воду к губам
    catch = sm(t, T_KOFE2, T_KOFE2 + .12)                      # спохватился: стакан замер и отдёрнут
    put = sm(t, T_VODOY - .05, T_VODOY + .35)                  # ставит стакан на стол
    laugh = t > T_VODOY - .08
    lean = -.08 * sip + .05 * catch * (1 - put) + .04 * math.sin(2 * math.pi * 4 * (t - T_VODOY)) * (1 if laugh else 0) * math.exp(-2 * max(0, t - T_VODOY))
    head_ang = -.28 * sip + .1 * catch * (1 - put) + (.06 * math.sin(2 * math.pi * 5 * (t - T_VODOY)) * math.exp(-1.5 * max(0, t - T_VODOY)) if laugh else 0)
    if laugh:
        e = ex("laugh")
    elif t > T_KOFE2 - .02:
        e = ex("surprise", look=(.75, .5))
    elif sip > .3:
        e = ex("relief", closed=.9)
    else:
        e = ex("cheerful", look=(.55, .25))
        e["closed"] = blinkv(t, [36.2])
    fig0 = dima(t, e, lean, head_ang)
    m = mouth_of(fig0, lean * .5 + head_ang)
    rot_d = -78.0
    W_d = wrist_for_rim(m, rot_d, "coffee", gap=(22, 6))
    W_hold = (HIPX + 170 * S, HIPY - 370 * S)
    Wn = lerp2(W_hold, W_d, sip)
    Wn = (Wn[0], Wn[1] + 14 * bump(t, T_KOFE2, .3))
    rot_n = lerp(-4, rot_d, sip)
    # дальняя рука со стаканом
    Wf_low = (HIPX + 290 * S, HIPY - 235 * S)
    Wf_up = (HIPX + 300 * S, HIPY - 420 * S)
    Wf_jerk = (HIPX + 330 * S, HIPY - 300 * S)
    if t < T_KOFE2:
        Wf = lerp2(Wf_low, Wf_up, reachw)
    else:
        Wf = lerp2(Wf_up, Wf_jerk, catch)
    Wf_table = wrist_for_bottom(GLASS18_X, TY, "glass")
    Wf = lerp2(Wf, Wf_table, put)
    rot_f = -14 * reachw * (1 - catch) + 10 * damp(t, T_KOFE2, 1.0, 4, 6) * (1 - put)
    hands = {"n": {"kind": "none"}, "f": {"kind": "none"}}
    kw = dict(near=("ik", Wn, -1), far=("ik", Wf, -1), hands=hands)
    back = dima(t, e, lean, head_ang, layers=("legs", "pelvis", "arm_f"), **kw)
    body = dima(t, e, lean, head_ang, layers=("body",), **kw)
    arm_n = dima(t, e, lean, head_ang, layers=("arm_n",), **kw)
    Wfr, Wnr = back["wrist"]["f"], arm_n["wrist"]["n"]
    splash = clamp((t - T_KOFE2) / .45) if t > T_KOFE2 else 0.0
    glass_svg = held(Wfr, rot_f, "glass", t=t, seed=7, gfill=.9, splash=splash if splash < 1 else 0.0)
    cup = held(Wnr, rot_n, "coffee", fill=.7, steam=.8 * (1 - sip), t=t, seed=1)
    room = R.kitchen(t, "morning", clock=PR.clock_hm(7, 55))
    # кот на столе лакает молоко из блюдца
    ph = 3.2 * (t - 35.9)
    cyc = .5 + .5 * math.sin(2 * math.pi * ph - math.pi / 2)
    st = dict(drop=1.62 + .34 * cyc, tongue=clamp((cyc - .5) / .3), look=(-.25, .95), blink=.45, tail=6 * math.sin(t * 1.7),
              ear=2 * math.sin(t * 2.3), tilt=-4 * cyc, rot=0.0)
    cat = people.cat_svg(CAT18[0], CAT18[1], CAT18_K, st, t)
    saucer = PR.milk_saucer(SAUCER18[0], SAUCER18[1], .82, t, ripple=.8, lick=st["tongue"])
    hx, hy = body["head"]
    ha = ""
    if laugh:
        u = (t - T_VODOY) % .5 / .5
        for i in range(3):
            a = (hx + 170 * S + 20 * i, hy - 90 + 40 * i - 30 * u)
            ha += line([a, (a[0] + 40, a[1] - 14)], 7, INK, taper=.5, wmin=.2, seed=6400 + i)
    world = [room["bg"], back["svg"], glass_svg, body["svg"], room["table"], saucer, cat, arm_n["svg"], cup, ha]
    # камера: откат к общему плану как у хука (s01 кончается на 1.25), мини-тряска на «водой»
    u = sm(t, 35.95, 37.3)
    sx1, sy1 = shake2(t, T_VODOY, 9)
    sc = lerp(1.42, 1.12, u) * (1 + .03 * bump(t, T_VODOY, .3))
    cx = lerp(700, 610, u) - sx1
    cy = lerp(740, 860, u) - sy1
    set_ink(sc)
    bodyg = f'<g transform="{lib.cam(cx, cy, sc, -1.2 * (1 - u))}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#e9dcc4"/>{bodyg}')


def frame(sid, t):
    return {"s01": s01, "s03": s03, "s18": s18}[sid](t)
