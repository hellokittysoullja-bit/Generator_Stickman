"""Рилс 61 «стол», группа A: стол-бардак Димы.
s01 (0–1.5) хук: стол крупно сверху-сбоку, гора бумажек, кружки, провода, лампа; рука Димы роется; «бумажки» (0.96) стопка взрывается
    веером в камеру; влёт 1/(1+0.4)→1 за 0.22 с с поворотом, тряска.
s02 (1.5–4.2) Дима за столом средним планом; «кружки» (1.72) кружка качается и звякает, «провода» (2.37) клубок опутывает запястье,
    «Мама» (3.42) взгляд к двери, виноватая улыбка.
s04 (7.1–9.9) Дима сбоку, лампочка-идея мигает и гаснет (7.55), он сползает, щека на ладони; кот шагает из-за кучи и на 8.9 запрыгивает
    на стол; «Знаешь» (9.75) поворачивает морду.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Люди и предметы — common/ (people, props)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import props  # noqa: E402
from lib import blob, clamp, ease_io, ease_out, ellipse_pts, f, line, mix, rect_pts, shape, svg, band, fill_d  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
INK = lib.INK


def lerp(a, b, u):
    return a + (b - a) * u


def bump(t, t0, dur):
    if t < t0:
        return 0.0
    return math.exp(-(t - t0) / dur * 3.0)


def hook_cam(t, hit, base, cx, cy):
    """Влёт правил 28–29: 1/(1+0.4) → 1 за 0.22 с, перелёт 5 %, поворот −3,4° с возвратом, удар +9 % на ударном слоге, занос вбок."""
    u = clamp(t / .22)
    e = 1 - (1 - u) ** 3
    m = 1 / (1 + .42 * (1 - e))
    if t > .22:
        tt = t - .22
        m *= 1 + .055 * math.exp(-tt * 7) * math.sin(min(tt * 18, math.pi))
    rot = -3.4 * (1 - e) + .5 * math.sin(t * 5)
    cx += 46 * (1 - e)
    if t > hit:
        tt = t - hit
        m *= 1 + .09 * math.exp(-tt * 8)
        rot += 1.6 * math.exp(-tt * 9) * math.sin(tt * 38)
        cx += 9 * math.exp(-tt * 11) * math.sin(tt * 55)
        cy += 10 * math.exp(-tt * 11) * math.sin(tt * 47 + 1)
    return cx, cy, base * m, rot


def whip_in(t, t0, dur=.16):
    """Хлёст на входе плана: (dx, размытие) — кадр влетает сбоку и тормозит."""
    u = clamp((t - t0) / dur)
    e = 1 - (1 - u) ** 3
    return 260 * (1 - e), 18 * (1 - e)


def frame_svg(body, cx, cy, s, rot, blur_x=0.0, bg="#2a2220"):
    cam = lib.cam(cx, cy, s, rot)
    g = f'<g transform="{cam}">{body}</g>'
    if blur_x > .5:
        fid = lib.uid("wb")
        lib.DEFS.append(f'<filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="{blur_x:.1f} 0"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/>' + g)


# ───────────────────────── мир стола (s01): вид сверху-сбоку ─────────────────────────
SLEEVE = ("#d4a23e", "#a97b25", "#8c6219")
SKIN = ("#ecc4a2", "#d39f83", "#bf8a74")


def _hand_kw():
    def sh(pts, fill, inner="", w=3.0, seed=0, **k):
        return shape(pts, fill, inner, w=w, seed=seed)

    def ln(pts, w=2.0, color=INK, seed=0, op=1.0, **k):
        return line(pts, w, color, taper=.4, wmin=.4, seed=seed, op=op)
    return dict(shape_fn=sh, line_fn=ln, skin=SKIN[0], skin_sh=SKIN[1], skin_sh2=SKIN[2])


def sleeve_arm(elbow, wrist, k, seed=0):
    """Рукав горчичного худи от локтя к запястью: не толще предплечья, у запястья резинка-манжета."""
    E, Wr = np.array(elbow, float), np.array(wrist, float)
    d = Wr - E
    L = np.linalg.norm(d)
    d /= L
    n = np.array([-d[1], d[0]])
    cuff0 = Wr - d * 34 * k
    mid = (E + cuff0) / 2 + n * 6 * k
    pts = [tuple(E), tuple(mid), tuple(cuff0)]
    o = []
    sl = band(pts, 104 * k, 92 * k, step=5, cap=False)
    inner = f'<path d="{fill_d(band([tuple(p + n * 22 * k) for p in map(np.array, pts)], 40 * k, 32 * k, step=6, cap=False))}" fill="{SLEEVE[1]}"/>'
    for j in range(3):   # складки рукава
        q = E + (cuff0 - E) * (.3 + .2 * j)
        inner += line([tuple(q - n * 32 * k + d * 6 * k), tuple(q + d * 18 * k), tuple(q + n * 18 * k + d * 10 * k)], 4 * k, SLEEVE[2], taper=.5, wmin=.3,
                      seed=seed + j)
    o.append(shape(sl, SLEEVE[0], inner, w=4.4, seed=seed + 5))
    cf = band([tuple(cuff0 - d * 2 * k), tuple(Wr + d * 6 * k)], 96 * k, 88 * k, step=4, cap=False)
    cin = "".join(line([tuple(cuff0 + d * (6 + 9 * j) * k - n * 44 * k), tuple(cuff0 + d * (6 + 9 * j) * k + n * 44 * k)], 2.4 * k, SLEEVE[1], taper=.2, wmin=.6,
                       seed=seed + 10 + j) for j in range(4))
    o.append(shape(cf, mix(SLEEVE[0], "#ffffff", .06), cin, w=4.0, seed=seed + 9))
    return "".join(o)


def desk_scene01(t):
    """Стол-бардак Димы крупно (мир 1080×1920 + запас за краями под влёт)."""
    o = []
    # стена над столом и сам стол
    o.append(blob(rect_pts(-500, -500, 1600, 480), "#D9C7A4"))
    for i in range(9):
        o.append(line([(-300 + 190 * i, -500), (-300 + 190 * i, 470)], 4, "#CDBA94", taper=.1, wmin=.8, seed=50 + i))
    o.append(props.sticky(840, 250, 1.6, 7, "pink", 4, "star") + props.sticky(980, 330, 1.4, -6, "yellow", 5, "lines"))
    o.append(props.wall_sketch(120, 220, 1.4, -5, 3, "spiral"))
    o.append(props.desk(540, 2150, 1900, 1.0, 1710, legs=False, seed=1))
    o.append(blob(rect_pts(-600, 2176, 1700, 2700), "#3A2C26"))
    # тёплый круг лампы: небольшой, чёткий край (не размытый овал)
    o.append(blob(ellipse_pts(250, 640, 190, 62, 24), "#D29A62"))
    o.append(blob(ellipse_pts(250, 640, 150, 46, 24), "#DDA872"))
    o.append(props.lamp_desk(160, 640, 1.7, on=1.0, tilt=-6))
    # кольца кофе, карандаш, стикер, зарядка, провода
    o.append(props.coffee_ring(330, 1080, 1.8, 10, 1) + props.coffee_ring(860, 1210, 1.5, -30, 2) + props.coffee_ring(640, 1420, 1.4, 50, 3))
    o.append(props.pencil(860, 1360, 1.4, -24) + props.sticky(160, 1420, 1.5, -14, "blue", 6, "arrow"))
    tang_w = 0.0
    o.append(props.cable_tangle(250, 1270, 1.9, 2, t * 1.5, tang_w))
    o.append(props.cable([(330, 1250), (420, 1330), (560, 1370), (720, 1460), (980, 1450), (1200, 1500)], w=10, seed=4))
    o.append(props.charger(990, 1450, 1.6, 70))
    # кружки: красная с паром, синяя
    o.append(props.mug(880, 780, 2.0, 0, "red", steam=1.0, t=t, seed=1))
    o.append(props.mug(170, 1060, 1.9, -4, "blue", handle=-1, seed=2, coffee=True))
    return "".join(o)


def pile01(t):
    """Гора бумаг посередине + верхняя стопка (до взрыва) и листы, которые шевелит рука."""
    o = [props.paper_pile(540, 1110, 2.3, 7, sy=.6, n=12)]
    return "".join(o)


def rummage(t):
    """Рука роется: запястье ходит туда-сюда, пальцы сжимаются; к 0.7 с хватает лист и тянет; на 0.96 отдёргивается."""
    ph = t * 2 * math.pi * 2.6
    wr = np.array([690 + 46 * math.sin(ph), 905 + 26 * math.sin(ph * .5 + 1)])
    if t > .96:
        u = clamp((t - .96) / .25)
        wr = wr + np.array([150, 90]) * ease_out(u)
    curl = .25 + .35 * (.5 + .5 * math.sin(ph + 1.2))
    return wr, curl, ph


def frame01(t):
    lib.dyn_begin()
    wr, curl, ph = rummage(t)
    o = [desk_scene01(t), pile01(t)]
    burst = t >= .96
    # листы, которые шевелит рука (лежат на горе)
    for j, (bx, by, br, bs) in enumerate(((470, 880, -14, 3), (600, 860, 18, 5), (540, 930, 6, 8))):
        jig = 0 if burst else 1
        rr = br + jig * 7 * math.sin(ph + j * 2)
        dx = jig * 10 * math.sin(ph * .5 + j)
        o.append(props.paper(bx + dx, by, 2.2, rr, 120, 160, bs, ("lines", "sketch", "grid")[j], .6))
    if not burst:
        # верхняя стопка — та, что взорвётся
        o.append(props.paper_stack(560, 860, 2.1, 6, 9, .35 + .2 * math.sin(ph), .6))
    # рука Димы справа: сначала кисть, рукав поверх запястья
    k = 1.55
    d = np.array([-1.0, -.32])
    elbow = wr + np.array([520, 250])
    hand = _hand_kw()
    import hand as H
    if not burst and t > .55:
        # лист, который рука тянет к себе: лежит ПОД пальцами (кончики пальцев прижимают его правый край)
        u = clamp((t - .55) / .4)
        tip = wr + d / np.linalg.norm(d) * 140 * k
        o.append(props.paper(tip[0] - 55 + 30 * u, tip[1] + 10, 1.9, -16 + 12 * u, 120, 160, 21, "sketch", .65))
    o.append(H.hand(tuple(wr), tuple(d), flip=-1, k=k, curl=(curl, curl + .05, curl + .1, curl + .12), spread=.18 + .1 * math.sin(ph),
                    thumb=.35, bend=.1, seed=40, **hand))
    o.append(sleeve_arm(tuple(elbow), tuple(wr), k * .95, seed=60))
    if burst:
        u = clamp((t - .96) / .62)
        o.append(props.fan_sheets(560, 840, u, 2.2, 11, 4, 1.15))
        o.append(props.clink(560, 820, 2.0, clamp((t - .96) / .3), 3, "#FFFFFF"))
    body = "".join(o)
    cx, cy, s, rot = hook_cam(t, .96, 1.22, 560, 930)
    dx, dy = props.shake(t, .96, 14, .4, 2)
    return frame_svg(body, cx + dx, cy + dy, s, rot)


# ───────────────────────── s02: Дима за столом средним планом ─────────────────────────
import people  # noqa: E402
import room as R  # noqa: E402

BS2 = 1.0
SX2, SY2 = 330.0, R.seat_y(BS2)          # таз Димы на стуле
DX2, DY2 = 930.0, R.DESK_TOP              # передний край стола (центр), стол справа от Димы
MUG_R2, MUG_B2 = (630.0, DY2 - 2), (722.0, DY2 - 22)
TANG2 = (1050.0, DY2 - 24)
CHG2 = (900.0, DY2 - 30)


def wob(t, t0, amp, freq=3.2, damp=4.0):
    if t < t0:
        return 0.0
    u = t - t0
    return amp * math.exp(-u * damp) * math.sin(2 * math.pi * freq * u)


def hand_path2(t):
    """Цель запястья ближней руки: роется в бумагах → отдёргивает назад и задевает кружку (1.72) → тянется к зарядке → тянет её
    к себе (2.37), провода ползут и обматывают запястье → на «Мама» (3.42) рука с проводами застыла чуть выше."""
    keys = [(1.25, (980, 880)), (1.45, (1020, 900)), (1.58, (960, 880)), (1.72, (690, 900)), (1.95, (780, 915)), (2.2, (905, 925)),
            (2.37, (900, 920)), (2.75, (820, 840)), (3.3, (800, 830)), (3.6, (790, 790)), (4.5, (795, 785))]
    for (ta, a), (tb, b) in zip(keys, keys[1:]):
        if t <= tb:
            u = ease_io((t - ta) / (tb - ta))
            p = np.array(a) + (np.array(b) - np.array(a)) * u
            break
    else:
        p = np.array(keys[-1][1], float)
    if t < 1.6:   # роется: мелкие рывки
        p = p + np.array([22 * math.sin(t * 31), 10 * math.sin(t * 23 + 1)])
    return p


def scene02(t):
    o = [R.wall_floor()]
    o.append(props.wall_sketch(820, 420, 1.3, -4, 7, "rocket") + props.sticky(1010, 500, 1.3, 8, "yellow", 8, "lines") +
             props.sticky(640, 560, 1.2, -10, "orange", 9, "circle"))
    ch = R.swivel_chair(SX2 - 20, SY2 + 24, 1.0, 0.0, side=-1)
    o.append(ch["back"])
    o.append(props.desk(DX2, DY2, 1000, 1.0, 110, True, "wood", seed=3, leg_h=R.FL - DY2 - 20))
    # лампа и её небольшой круг света
    o.append(blob(ellipse_pts(1260, DY2 - 50, 120, 26, 22), "#D9A06A"))
    o.append(props.lamp_desk(1300, DY2 - 60, 1.3, on=1.0, tilt=-10))
    o.append(props.coffee_ring(860, DY2 - 30, 1.0, 0, 4, .35))
    o.append(props.paper_pile(1080, DY2 - 6, 1.15, 11, sy=.42, n=10))
    # провода: клубок ползёт к руке после 2.37
    pull = ease_out(clamp((t - 2.37) / .5))
    tx, ty = TANG2[0] - 150 * pull, TANG2[1] + 6 * pull
    o.append(props.cable_tangle(tx, ty, .85, 5, t * 1.4, wind=.35 * pull))
    return "".join(o), ch, (tx, ty), pull


def frame02(t):
    lib.dyn_begin()
    bg, ch, tang, pull = scene02(t)
    wr = hand_path2(t)
    # кружки: красная качается от удара (1.72) и звякает о синюю
    rr = wob(t, 1.72, 16, 3.4, 3.6)
    rb = wob(t, 1.80, -7, 3.8, 4.5)
    mugs = props.mug(MUG_B2[0], MUG_B2[1], 1.35, rb, "blue", seed=3, handle=1) + props.mug(MUG_R2[0], MUG_R2[1], 1.45, rr, "red", steam=.8, t=t, seed=4)
    clk = props.clink(MUG_R2[0] + 50, MUG_R2[1] - 96, 1.0, clamp((t - 1.76) / .32), 5) + props.clink(MUG_R2[0] + 46, MUG_R2[1] - 90, .8, clamp((t - 1.98) / .28), 6)
    # мимика
    if t < 1.72:
        ex = dict(people.EXPR["dima"]["focus"], look=(.7, .5))
    elif t < 2.2:
        ex = {"brows": "up", "mouth": "talk", "open": .45, "lid": 1.0, "look": (-.2, .6)}
    elif t < 3.42:
        ex = {"brows": "worry", "mouth": "flat", "lid": .8, "look": (.55, .55)}
    else:
        u = clamp((t - 3.42) / .2)
        ex = dict(people.EXPR["dima"]["guilty"], look=(lerp(.55, .95, u), lerp(.55, -.35, u)), smile=.45 * u + .05)
    head_ang = -.06 if t < 3.42 else -.06 - .1 * ease_out(clamp((t - 3.42) / .25))
    lean = .1 + .03 * math.sin(t * 2.1) - (.06 * ease_out(clamp((t - 3.42) / .3)))
    grip = 2.2 < t
    hands = {"n": dict(kind="open", flip=1, dir=(1, .25) if not grip else (1, .15), curl=(.7, .72, .75, .78) if grip else (.25, .2, .3, .35),
                       thumb=.6 if grip else .25, spread=.1),
             "f": dict(kind="open", flip=1, dir=(1, .35), curl=(.35, .35, .4, .45), thumb=.3)}
    arms = {"n": ("ik", tuple(wr), -1), "f": ("ik", (1000 + 8 * math.sin(t * 3), DY2 - 70), -1)}
    feet = {"n": ((SX2 + 300, R.FL - 52), 0.0), "f": ((SX2 + 250, R.FL - 50), 0.0)}
    full = people.draw(dict(hip=(SX2, SY2), scale=BS2 * people.HEIGHT["dima"], lean=lean, feet=feet, arms=arms, hands=hands, head_ang=head_ang,
                            expr=ex, torso_k=1.0, hood=0.0, head_off=(0, 0)), "dima")
    wrist = np.array(full["wrist"]["n"], float)
    o = [bg, ch["base"], full["legs"], ch["seat"], full["arm_f"], full.get("pelvis", ""), full["body"]]
    # зарядка в руке (после хвата — под пальцами) и провод от клубка к ней, витки вокруг запястья
    if grip:
        chg = wrist + np.array([70, 6])
    else:
        chg = np.array(CHG2)
    o.append(props.cable([(tang[0] - 30, tang[1] - 10), ((tang[0] + chg[0]) / 2, tang[1] + 16), (chg[0] + 22, chg[1] + 4)], w=8, seed=21))
    o.append(props.charger(chg[0] + 4, chg[1], .9, 80))
    loops_b, loops_f = [], []
    if pull > 0:   # витки провода вокруг запястья: задняя половина под рукой, передняя поверх
        n_loops = 3 * pull
        for j in range(3):
            if n_loops <= j:
                break
            fr = clamp(n_loops - j)
            cx = wrist[0] - 8 - 20 * j
            col = ("#3A3D44", "#E7E2D6", "#C8553D")[j]
            a0 = -math.pi / 2
            ang = np.linspace(a0, a0 + 2 * math.pi * fr, 24)
            pts = [(cx + 11 * math.cos(a), wrist[1] + 44 * math.sin(a)) for a in ang]
            front = [p for p, a in zip(pts, ang) if math.cos(a) >= 0]
            back = [p for p, a in zip(pts, ang) if math.cos(a) < 0]
            if len(back) > 1:
                loops_b.append(props.cable(back, col, 7, seed=30 + j, hi=False))
            if len(front) > 1:
                loops_f.append(props.cable(front, col, 7, seed=40 + j))
    o.extend(loops_b)
    o.append(full["arm_n"])
    o.extend(loops_f)
    o.append(mugs)
    o.append(clk)
    body = "".join(o)
    # камера: дрейф вправо, наезд на руку с проводами, на «Мама» чуть назад к лицу
    u1 = ease_io(clamp((t - 1.3) / 3.0))
    cx = 570 + 60 * u1
    cy = 920
    s = 1.2 + .05 * u1
    push = ease_io(clamp((t - 2.3) / .8)) * (1 - ease_io(clamp((t - 3.35) / .45)))
    cx = lerp(cx, 700, push * .6)
    cy = lerp(cy, 860, push)
    s *= 1 + .2 * push
    cy -= 70 * ease_io(clamp((t - 3.35) / .5))
    dx, dy = props.shake(t, 1.72, 7, .3, 4)
    return frame_svg(body, cx + dx, cy + dy, s, .4 * math.sin(t * .9))


# ───────────────────────── s04: Дима сбоку, лампочка гаснет, кот запрыгивает ─────────────────────────
BS4 = 1.05
SX4, SY4 = 300.0, R.seat_y(BS4)
DX4, DY4 = 980.0, R.DESK_TOP
CAT_K = .72
CAT_LAND = (900.0, DY4 - 40)
JUMP_T0, JUMP_T1 = 8.32, 9.02      # u=.85 (касание) ≈ 8.92


def cat04(t):
    """Кот: шагает по полу справа налево из-за ножки стола, прыгает с толчком на стол (касание ≈ 8.9), на «Знаешь» поворачивает морду."""
    floor = R.FL - 6
    if t < JUMP_T0:
        u = clamp((t - 7.0) / (JUMP_T0 - 7.0))
        x = lerp(1340, 820, ease_io(u) * .3 + u * .7)
        st = {"turn": -.7, "look": (-.6, 0), "tail": 6 * math.sin(t * 6)}
        return people.cat_walk(x, floor, CAT_K, t, st, period=.42), None
    u = clamp((t - JUMP_T0) / (JUMP_T1 - JUMP_T0))
    look_u = ease_io(clamp((t - 9.72) / .2))
    st = {"turn": lerp(-.6, .55, look_u), "look": (lerp(-.5, 0, look_u), lerp(-.3, 0, look_u)), "tail": 4 * math.sin(t * 3)}
    if t > 9.72:
        st["tilt"] = 5 * look_u
    if u >= 1:
        st["blink"] = 1.0 if 9.4 < t < 9.48 else 0.0
        return people.cat_svg(CAT_LAND[0], CAT_LAND[1], CAT_K, st, t), u
    return people.cat_jump((820, floor), CAT_LAND, CAT_K, u, t, st, height=170), u


def frame04(t):
    lib.dyn_begin()
    o = [R.wall_floor()]
    o.append(props.wall_sketch(760, 330, 1.3, 5, 12, "spiral") + props.sticky(980, 440, 1.3, -7, "green", 13, "star"))
    ch = R.swivel_chair(SX4 - 20, SY4 + 24, BS4, 0.0, side=-1)
    o.append(ch["back"])
    o.append(props.desk(DX4, DY4, 900, 1.0, 110, True, "wood", seed=5, leg_h=R.FL - DY4 - 20))
    o.append(props.coffee_ring(800, DY4 - 40, 1.0, 0, 6, .35))
    o.append(props.mug(1270, DY4 - 50, 1.1, 0, "green", seed=6, handle=-1))
    # Дима: сидит, потом сползает (7.6–8.4), щека на ладони
    sl = ease_io(clamp((t - 7.62) / .7))
    lean = lerp(.06, .36, sl) + .02 * math.sin(t * 1.8)
    sy = SY4 + 40 * sl
    probe = people.draw(dict(hip=(SX4, sy), scale=BS4 * people.HEIGHT["dima"], lean=lean, feet=None, arms={"n": ("ang", 0, 0), "f": ("ang", 0, 0)},
                             hands={}, head_ang=lerp(0, .18, sl), expr={}, torso_k=1.0, hood=0.0, head_off=(0, 0)), "dima")
    hx, hy = probe["head"]
    cheek = (hx + 30 * BS4, hy + 175 * BS4)
    tgt_f = (lerp(860, cheek[0], sl), lerp(DY4 - 60, cheek[1], sl))
    if t < 7.55:
        ex = {"brows": "up", "mouth": "smile", "smile": .6, "lid": 1.0, "look": (.3, -.9)}
    elif t < 7.95:
        ex = {"brows": "worry", "mouth": "flat", "lid": .9, "look": (.3, -.9)}
    elif t < 9.0:
        ex = dict(people.EXPR["dima"]["gloom"], look=(.6, .5))
    else:
        ex = dict(people.EXPR["dima"]["gloom"], look=(.9, .2), lid=.5)
    hands = {"f": dict(kind="open", flip=1, dir=(lerp(1, .3, sl), lerp(.35, -1, sl)), curl=(.3, .3, .35, .4), thumb=.2, spread=.15),
             "n": dict(kind="open", flip=1, dir=(1, .3), curl=(.45, .45, .5, .55), thumb=.3)}
    arms = {"f": ("ik", tgt_f, -1), "n": ("ik", (lerp(800, 760, sl), DY4 - 66), -1)}
    feet = {"n": ((SX4 + 320 + 40 * sl, R.FL - 52), 0.0), "f": ((SX4 + 270 + 40 * sl, R.FL - 50), 0.0)}
    full = people.draw(dict(hip=(SX4, sy), scale=BS4 * people.HEIGHT["dima"], lean=lean, feet=feet, arms=arms, hands=hands,
                            head_ang=lerp(0, .18, sl), expr=ex, torso_k=1.0, hood=0.0, head_off=(0, 0)), "dima")
    hx, hy = full["head"]
    catsvg, cu = cat04(t)
    # кот за ножкой стола до прыжка — рисуем раньше стола? ножка тонкая: кот идёт ПЕРЕД столом (ближе к зрителю)
    o += [ch["base"], full["legs"], ch["seat"], full["arm_f"], full.get("pelvis", ""), full["body"], full["arm_n"]]
    # гора бумаг на столе (кот приземляется в неё) и лист, который взлетает
    o.append(props.paper_pile(1060, DY4 - 6, 1.1, 14, sy=.42, n=9))
    o.append(catsvg)
    if t > 8.9:
        u = clamp((t - 8.9) / .9)
        o.append(props.flying_sheet(960 + 120 * u, DY4 - 80 - 380 * math.sin(math.pi * u * .9), 1.05, 40 * u, 17, "sketch", flap=t * 7))
        o.append(props.flying_sheet(860 - 90 * u, DY4 - 70 - 260 * math.sin(math.pi * u * .8), .9, -50 * u, 18, "lines", flap=t * 6 + 1))
    # лампочка-идея над головой: горит, мигает с 7.55, гаснет
    on = props.flicker(t, 7.55, 7.95, 3)
    bob = 8 * math.sin(t * 4)
    bx, by = hx + 40, hy - 340 * BS4 + bob + 50 * sl
    o.append(props.idea_bulb(bx, by, 1.15, on, t, 2))
    if on < .05 and t < 8.6:   # дымок от погасшей лампочки
        u = clamp((t - 7.95) / .6)
        o.append(line([(bx + 8 * math.sin(u * 9 + j), by - 60 - 90 * u - 12 * j) for j in range(5)], 5 * (1 - u), "#8E929A", taper=.8, wmin=.1, seed=77))
    body = "".join(o)
    # камера: хлёст на входе, откат и дрейф, мини-тряска на прыжке
    u = ease_io(clamp((t - 7.0) / 2.9))
    cx = lerp(620, 690, u)
    cy = lerp(860, 930, u)
    s = lerp(1.32, 1.1, u)
    wx, bl = whip_in(t, 6.9)
    dx, dy = props.shake(t, 8.92, 9, .35, 5)
    return frame_svg(body, cx - wx / s + dx, cy + dy, s, -.6 * math.sin(t * .8), blur_x=bl)


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    if sid == "s01":
        return frame01(t)
    if sid == "s02":
        return frame02(t)
    if sid == "s04":
        return frame04(t)
    raise KeyError(sid)
