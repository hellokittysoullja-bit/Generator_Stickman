"""Рилс 63 «кофе», группа E — утро после и хорошее утро, спокойный сон: s12 (серое утро, Дима-зомби оседает и бухается лбом
на стол), s13 (солнечное утро, две чашки до обеда, часы без цифр), s14 (спальня сбоку, спит на боку с улыбкой).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Кухня и спальня — common/room.py, люди — common/people.py,
предметы — common/props.py (своих копий нет)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rect_pts, shape  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


T_USTAESH, T_ESCHE, T_SILNEE = wt(60), wt(61), wt(62)                   # 23.74, 24.22, 24.46
T_TEPER, T_PYOT, T_DVE, T_CHASHKI, T_OBEDA = wt(63), wt(65), wt(67), wt(68), wt(70)   # 25.34, 26.60, 27.10, 27.36, 27.89
T_SPOK, T_SPIT, T_NOCH = wt(72), wt(73), wt(74)                        # 28.46, 29.01, 29.36
E = people.EXPR["dima"]


def lerp(a, b, u):
    return a + (b - a) * u


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def ex(name, **kw):
    e = dict(E[name])
    e.update(kw)
    return e


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def blinkv(t, times, dur=.16):
    v = 0.0
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def cam_wrap(body, cx, cy, s, rot_=0.0):
    return f'<g transform="{lib.cam(cx, cy, s, rot_)}">{body}</g>'


def whip_in(t, t0, dur=.3):
    """Хлёст-влёт плана: 1 → 0 за dur (смещение камеры и поворот гаснут)."""
    return 1 - ease_out(clamp((t - t0 + .2) / dur), 3)


def chair(x, y, k=1.0, seed=0):
    """Простой кухонный стул сбоку (сиденье под тазом (x, y), спинка слева): деревянный, без букв."""
    sd = 16000 + seed
    o = []
    seat_y = y + 70 * k
    for lx in (x - 150 * k, x + 120 * k):
        o.append(shape(rect_pts(lx, seat_y + 20 * k, lx + 26 * k, R.K_FLOOR + 40), R.WOOD_SH, "", w=3.4, seed=sd + int(lx) % 97))
    o.append(shape(rect_pts(x - 200 * k, y - 330 * k, x - 166 * k, seat_y + 10 * k), R.WOOD, blob(rect_pts(x - 180 * k, y - 330 * k, x - 166 * k, seat_y), R.WOOD_SH),
                   w=3.6, seed=sd + 1))
    o.append(shape(lib.rrect(x - 214 * k, y - 360 * k, x - 150 * k, y - 250 * k, 10 * k), R.WOOD, blob(rect_pts(x - 168 * k, y - 360 * k, x - 150 * k, y - 250 * k),
                                                                                                         R.WOOD_SH), w=3.6, seed=sd + 2))
    o.append(shape(lib.rrect(x - 200 * k, seat_y - 6 * k, x + 160 * k, seat_y + 24 * k, 8 * k), R.WOOD, blob(rect_pts(x - 200 * k, seat_y + 12 * k, x + 160 * k,
                                                                                                                     seat_y + 24 * k), R.WOOD_SH), w=3.6, seed=sd + 3))
    return "".join(o)


# ═══════════════════════════════ s12: серое утро, Дима-зомби ═══════════════════════════════
S12_S = 1.08
S12_HIP = (330.0, 1405.0)
S12_MUG = (250.0, R.K_TABLE[2] - 34)


def dima12(t):
    """Сидящий Дима за столом: (fig, расположение). Оседает на предплечья → веки слипаются → лоб на стол."""
    x, y = S12_HIP
    s = S12_S
    sc = s * people.HEIGHT["dima"]
    tab = R.K_TABLE[2] - 62                          # уровень, где лежат предплечья (середина крышки)
    sway = math.sin(2 * math.pi * .55 * (t - 23.2))
    # 1) с кадра 0 качается, клюёт носом; 2) «устаёшь» — оседает на локти; 3) «ещё» — веки слипаются; 4) «сильнее» — бух лбом
    sink = sm(t, T_USTAESH - .05, T_ESCHE + .05)
    nod = .07 * math.sin(2 * math.pi * 1.1 * (t - 23.2)) * (1 - sink * .5)
    fall_u = ease_in(clamp((t - (T_SILNEE - .16)) / .16), 2.2)          # падение к удару ровно на «сильнее»
    lean = lerp(.1 + .03 * sway, .32, sink) + fall_u * .26
    ha = lerp(.06 + nod, .2, sink) + fall_u * .78
    hoff_y = 46 * fall_u
    # отскок головы от стола
    bounce = damp(t, T_SILNEE, 1.0, 3.2, 7.0)
    if t > T_SILNEE:
        lean = .58 - .02 * bounce
        ha = .98 - .07 * bounce
        hoff_y = 46 - 10 * abs(bounce)
    # руки: предплечья лежат на столе и уезжают вперёд, когда оседает
    reach = lerp(300, 345, sink) + 40 * fall_u
    if t > T_SILNEE:
        reach = 385 + 6 * bounce
    A = {"f": ("ik", (x + reach * sc - 40 * sc, tab - 4), -1), "n": ("ik", (x + reach * sc + 30 * sc, tab + 6), -1)}
    # на ударе ближняя рука соскальзывает со стола и повисает (не закрывает лицо)
    drop = sm(t, T_SILNEE - .12, T_SILNEE + .08)
    if drop > 0:
        nt = A["n"][1]
        hang = (x + 120 * sc + 30 * damp(t, T_SILNEE, 1, 2.4, 5), y + 120 * sc)
        A["n"] = ("ik", (lerp(nt[0], hang[0], drop), lerp(nt[1], hang[1], drop)), -1)
    H = {"f": {"curl": (.25, .25, .3, .35), "thumb": .25, "dir": (1, .08)}, "n": {"curl": (.2, .2, .3, .35), "thumb": .2, "dir": (1, .1),
                                                                              "spread": .25 + .15 * fall_u}}
    # лицо: зомби (рот приоткрыт, взгляд вниз), веки слипаются на «ещё», после удара — глаза закрыты
    if t < T_ESCHE:
        e = ex("zombie", hair=2 * sway)
        e["closed"] = blinkv(t, (23.55, 24.0), .28) * .8
        e["lid"] = lerp(.12, .05, sink)
    elif t < T_SILNEE - .02:
        u = sm(t, T_ESCHE, T_ESCHE + .2)
        e = ex("zombie", lid=lerp(.05, 0.0, u), look=(0, lerp(.6, -.2, u)))
        e["closed"] = u
    else:
        e = ex("zombie", shut=1.0, open=.08, hair=6 * math.exp(-6 * (t - T_SILNEE)))
    feet = {"n": ((x + 300 * sc, R.K_FLOOR + 60), 0.0), "f": ((x + 250 * sc, R.K_FLOOR + 66), 0.0)}
    kw = dict(lean=lean, head_ang=ha, head_off=(10 * fall_u, hoff_y), arms=A, hands=H, feet=feet)
    fg = people.figure("dima", x, y, s, e, layers=("legs",), **kw)
    fg["kw"] = (s, e, kw)
    return fg


def apron(y, x0=None, x1=None, h=120.0, seed=0):
    """Царга стола — широкая доска под крышкой: прячет колени сидящего (кадр ниже крышки не пестрит)."""
    x0 = R.K_TABLE[0] if x0 is None else x0
    x1 = R.K_TABLE[1] if x1 is None else x1
    inner = blob(rect_pts(x0, y + h - 22, x1, y + h), R.WOOD_SH) + line([(x0 + 30, y + 60), (x1 - 40, y + 64)], 2.6, R.WOOD_HI, seed=16200 + seed)
    return shape(rect_pts(x0 + 6, y, x1 - 6, y + h), R.WOOD, inner, w=3.8, seed=16201 + seed)


def island(front_y, x0=None, x1=None):
    """Кухонный остров под крышкой стола (s13): фасад с дверцами до пола — стоящего Диму видно по пояс, ноги закрыты."""
    m = R.KMODE["sunny"]
    x0 = R.K_TABLE[0] if x0 is None else x0
    x1 = R.K_TABLE[1] if x1 is None else x1
    y0, y1 = front_y + 26, R.K_FLOOR + 40
    o = [shape(rect_pts(x0 + 8, y0, x1 - 8, y1), m["cab"], blob(rect_pts(x0 + 8, y1 - 40, x1 - 8, y1), m["cab_sh"]), w=4.0, seed=16300)]
    n = 3
    for i in range(n):
        a = x0 + 30 + (x1 - x0 - 60) * i / n
        b = x0 + 30 + (x1 - x0 - 60) * (i + 1) / n - 14
        inner = blob(rect_pts(b - 22, y0 + 24, b, y1 - 60), m["cab_sh"]) + blob(rect_pts(a + 12, y0 + 36, a + 22, y1 - 72), m["cab_hi"])
        o.append(shape(rect_pts(a, y0 + 24, b, y1 - 60), m["cab"], inner, w=3.6, seed=16310 + i))
        o.append(shape(lib.rrect(a + 40, y0 + 60, a + 110, y0 + 76, 6), "#c4ccd4", "", w=2.4, seed=16320 + i))
    return "".join(o)


def behind_table(fg, table, top_y, front_y):
    """Сидящий за столом: ноги под столом → стол → туловище (видно выше дальнего края крышки) → руки (лежат на крышке)."""
    s, e, kw = fg["kw"]
    x, y = fg["hip"]
    body = people.figure("dima", x, y, s, e, layers=("arm_f", "body"), **kw)["svg"]
    arm_n = people.figure("dima", x, y, s, e, layers=("arm_n",), **kw)["svg"]
    arm_f = people.figure("dima", x, y, s, e, layers=("arm_f",), **kw)["svg"]
    cb = lib.clip_rect(-2000, -3000, 6000, 3000 + front_y)
    ca = lib.clip_rect(-2000, -3000, 6000, 3000 + front_y)
    return (fg["svg"] + table + apron(front_y + 28) + f'<g clip-path="url(#{ca})">{arm_f}</g>' + f'<g clip-path="url(#{cb})">{body}</g>'
            + f'<g clip-path="url(#{ca})">{arm_n}</g>')


def frame12(t):
    lib.dyn_begin()
    ah, am = PR.clock_hm(7, 5 + (t - 23.4) * 6)
    kit = R.kitchen(t, "grey", clock=(ah, am))
    fg = dima12(t)
    fg["hip"] = S12_HIP
    # кружка: пустая, на «сильнее» подпрыгивает и чуть кренится
    mx, my = S12_MUG
    hop = PR.hop(t, T_SILNEE, 46, .3) + PR.hop(t, T_SILNEE + .3, 12, .16)
    tilt = 14 * math.sin(math.pi * clamp((t - T_SILNEE) / .3)) if t > T_SILNEE else 0.0
    msx, msy = PR.squash(t, T_SILNEE + .3, .18, 3.0, 9.0)
    mug = PR.coffee_mug(mx, my + hop, 1.05, rot=tilt, fill=0.0, seed=21)
    if msy != 1.0:
        mug = f'<g transform="translate({mx} {my}) scale({msx:.4f} {msy:.4f}) translate({-mx} {-my})">{mug}</g>'
    # стол тоже вздрагивает на ударе
    tsh = PR.shake(t, T_SILNEE, 7, .25, seed=4)
    table = f'<g transform="translate({tsh[0] * .4:.2f} {tsh[1]:.2f})">{kit["table"]}</g>'
    # тучка-закорючка: появляется на «устаёшь», вьётся над головой
    hx, hy = fg["head"]
    gu = clamp((t - T_USTAESH) / .35)
    gsx = PR.pop(t, T_USTAESH, amp=.25)[0] if t < T_USTAESH + .8 else 1.0
    gy = hy - 330 - 16 * math.sin(t * 2.3) + 110 * ease_out(clamp((t - T_SILNEE) / .3))
    gx = hx - 10 + 22 * math.sin(t * 1.7)
    cloud = PR.gloom(gx, gy, 1.0, t, u=gu * max(.01, gsx) if gu < 1 else 1.0, seed=3) if gu > 0 else ""
    # звёздочки-штрихи удара у лба
    hit = ""
    if T_SILNEE < t < T_SILNEE + .45:
        u = (t - T_SILNEE) / .45
        for j, a in enumerate((-150, -110, -60, -20)):
            r0, r1 = 150 + 90 * u, 200 + 130 * u
            aa = math.radians(a)
            p0 = (hx + 120 + math.cos(aa) * r0, hy + 90 + math.sin(aa) * r0)
            p1 = (hx + 120 + math.cos(aa) * r1, hy + 90 + math.sin(aa) * r1)
            hit += line([p0, p1], 9 * (1 - u) + 2, INK, taper=.5, wmin=.2, seed=16100 + j)
    person = behind_table(fg, table, R.K_TABLE[2] - R.K_TABLE[3] + 8, R.K_TABLE[2])
    world = kit["bg"] + chair(S12_HIP[0], S12_HIP[1], 1.0) + person + mug + hit + cloud + kit["front"]
    # камера: медленный наезд на голову, тряска на ударе
    a = 23.4
    push = sm(t, a, 25.5)
    fol = sm(t, T_SILNEE - .2, T_SILNEE + .5)
    cx = lerp(470, 520, push) + 90 * fol
    cy = lerp(950, 930, push) + 70 * fol
    s = lerp(1.22, 1.34, push)
    sh = PR.shake(t, T_SILNEE, 20, .4, seed=5)
    rr = .5 * math.sin(t * 1.1) + damp(t, T_SILNEE, 1.2, 3, 6)
    set_ink(s)
    return lib.svg(cam_wrap(world, cx + sh[0], cy + sh[1], s, rr))


# ═══════════════════════════════ s13: солнечное утро, две чашки до обеда ═══════════════════════════════
S13_S = 1.06
S13_HIP = (440.0, 1360.0)
S13_MUG2 = (830.0, R.K_TABLE[2] - 46)
S13_POT = (965.0, R.K_TABLE[2] - 80)
S13_SPOT = (630.0, R.K_TABLE[2] - 54)          # куда ставит первую чашку
S13_RACK = (905.0, R.K_COUNTER - 74)           # кружка вверх дном в сушилке (низ)


def mug_in_hand(wr, k, rot_=0.0, fill=1.0, steam=0.0, t=0.0, seed=0):
    """Кружка за ручку в ближней руке: пальцы через ручку, большой палец сверху. rot_ — поворот кружки вокруг кисти."""
    hc = (wr[0] - 6 * k, wr[1])
    back, front = people.handle_grip("dima", hc, k=k, side=1)
    km = k * 1.0
    mug = PR.coffee_mug(hc[0] - 88 * km, hc[1] + 70 * km, km, fill=fill, steam=steam, t=t, seed=seed)
    if abs(rot_) > .01:
        mug = f'<g transform="rotate({rot_:.3f} {hc[0]:.2f} {hc[1]:.2f})">{mug}</g>'
    return back + mug + front


def mug_wrist_for(bottom, k, rot_=0.0):
    """Где кисть, если низ кружки (центр дна) в bottom и кружка повёрнута на rot_ вокруг кисти."""
    a = math.radians(rot_)
    dx, dy = -88 * k, 70 * k
    rx, ry = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
    return (bottom[0] - rx + 6 * k, bottom[1] - ry)


def clock13(t):
    """Стрелки: до «Теперь» бегут, на «Теперь» встают на утро с отскоком; на «обеда» прыгают к полудню."""
    h8 = PR.clock_hm(8, 0)
    h12 = PR.clock_hm(12, 0)
    if t < T_TEPER:
        u = (t - 25.1) / (T_TEPER - 25.1)
        return h8[0] - 10 - 30 * (1 - u), h8[1] - 40 - 440 * (1 - u)
    if t < T_OBEDA - .12:
        return PR.settle(t, T_TEPER, h8[0] - 10, h8[0]), PR.settle(t, T_TEPER, h8[1] - 40, h8[1])
    u = clamp((t - (T_OBEDA - .12)) / .22)
    ah = lerp(h8[0], h12[0] + 372, ease_in(u))
    am = lerp(h8[1], h12[1] + 1470, ease_in(u))
    if u >= 1:
        ah = PR.settle(t, T_OBEDA + .1, h12[0] + 360 + 12, h12[0] + 360)
        am = PR.settle(t, T_OBEDA + .1, h12[1] + 1440 + 30, h12[1] + 1440)
    return ah, am


def frame13(t):
    lib.dyn_begin()
    x, y = S13_HIP
    s = S13_S
    sc = s * people.HEIGHT["dima"]
    k = sc
    front_y = R.K_TABLE[2]
    kit = R.kitchen(t, "sunny", clock=clock13(t))
    breath = math.sin(2 * math.pi * (t - 25.1) / 1.4)
    chest = (x + 250 * sc, y - 330 * sc)
    head_guess = people.figure("dima", x, y, s, {}, layers=("body",), lean=.04)["head"]
    mouth = (head_guess[0] + 150 * sc, head_guess[1] + 120 * sc)
    # ── ближняя рука и первая чашка
    rot_ = 0.0
    fill1 = 1.0
    drink = sm(t, T_PYOT - .18, T_PYOT + .02) * (1 - sm(t, T_PYOT + .38, T_PYOT + .56))
    w_chest = (chest[0] + 6 * math.sin(t * 2), chest[1] + 8 * breath)
    w_mouth = (mouth[0] + 95 * sc, mouth[1] - 60 * sc)
    w = (lerp(w_chest[0], w_mouth[0], drink), lerp(w_chest[1], w_mouth[1], drink))
    rot_ = -52 * drink
    fill1 = 1.0 - .5 * sm(t, T_PYOT, T_PYOT + .35)
    w_table = mug_wrist_for(S13_SPOT, k)
    put = sm(t, T_CHASHKI - .22, T_CHASHKI + .02)
    if put > 0:
        w = (lerp(w[0], w_table[0], put), lerp(w[1], w_table[1] + PR.hop(t, T_CHASHKI, 0, .1), put))
    # переворот и сушилка: 27.58–27.98 — вверх, по дуге, вверх дном; кладёт и отпускает
    flip = sm(t, 27.56, 27.98)
    pot_x = S13_POT[0]
    released = t > 28.0
    if flip > 0:
        rack_w = mug_wrist_for((S13_RACK[0] - 8, S13_RACK[1] - 150 * k), k, 180)
        arc = -170 * math.sin(math.pi * flip)
        w = (lerp(w_table[0], rack_w[0], flip), lerp(w_table[1], rack_w[1], flip) + arc)
        rot_ = 180 * ease_io(clamp((flip - .1) / .8))
        fill1 = 0.0
    if released:
        fill1 = 0.0
        # кисть уходит к кофейнику и толкает его вправо
        go = sm(t, 28.0, 28.14)
        push = ease_out(clamp((t - 28.14) / .3), 2)
        pot_x = S13_POT[0] + 210 * push
        pw = (pot_x - 116 * .9, S13_POT[1] - 110 * .9)
        w = (lerp(w[0], pw[0], go), lerp(w[1], pw[1], go))
    # ── дальняя рука лежит на столе
    wf = (x + 170 * sc, front_y - 70 + 4 * breath)
    arms = {"n": ("ik", w, -1), "f": ("ik", wf, -1)}
    if released:
        hands = {"n": {"dir": (1, -.1), "curl": (0, .05, .1, .15), "spread": .3, "thumb": .1}, "f": {"curl": (.35, .35, .4, .45), "thumb": .35}}
    else:
        hands = {"n": {"kind": "none"}, "f": {"curl": (.35, .35, .4, .45), "thumb": .35}}
    # ── лицо: бодрая улыбка, взгляд на часы на «Теперь», блаженство на глотке, весело в камеру
    if drink > .5:
        e = ex("bliss", bags=False)
    elif t < T_TEPER + .6 and t > T_TEPER - .1:
        e = ex("cheerful", look=(.55, -.85))
    elif t > T_OBEDA - .1 and t < T_OBEDA + .35:
        e = ex("cheerful", look=(.55, -.85))
    elif flip > 0 and not released:
        e = ex("cheerful", look=(.8, -.2))
    else:
        e = ex("cheerful", look=(-.3, 0), smile=1.0)
        e["closed"] = blinkv(t, (25.9, 27.45))
    ha = -.12 * sm(t, T_TEPER - .1, T_TEPER + .2) * (1 - sm(t, T_TEPER + .5, T_TEPER + .8)) - .05 * drink
    if T_OBEDA - .1 < t < T_OBEDA + .35:
        ha = -.12
    lean = .04 + .02 * breath - .04 * drink
    kw = dict(lean=lean, head_ang=ha, arms=arms, hands=hands, torso_k=1 + .012 * breath)
    fg = {"svg": island(front_y), "head": head_guess}
    fg["kw"] = (s, e, kw)
    fg["hip"] = (x, y)
    # ── предметы
    items = ""
    m2sx, m2sy = PR.pop(t, T_DVE, amp=.3)
    if t >= T_DVE:
        m2 = PR.coffee_mug(S13_MUG2[0], S13_MUG2[1], k, fill=1.0, steam=1.0, t=t, seed=32, col="white")
        items += f'<g transform="translate({S13_MUG2[0]} {S13_MUG2[1]}) scale({m2sx:.4f} {m2sy:.4f}) translate({-S13_MUG2[0]} {-S13_MUG2[1]})">{m2}</g>'
    pot = PR.coffee_pot(pot_x, S13_POT[1], .9, rot=-4 * math.sin(math.pi * clamp((t - 28.14) / .3)), seed=33)
    rack_mug = ""
    mug1 = ""
    if released:
        rack_mug = PR.coffee_mug(S13_RACK[0], S13_RACK[1], k, fill=0.0, upside=True, seed=31)
        rack_mug = f'<g transform="translate(0 {PR.hop(t, 28.0, 10, .14):.2f})">{rack_mug}</g>'
    else:
        mug1 = mug_in_hand(w, k, rot_, fill1, steam=1.0 - drink, t=t, seed=31)
    # клинк при постановке
    if T_CHASHKI < t < T_CHASHKI + .3:
        items += PR.clink(S13_SPOT[0] + 60, S13_SPOT[1] - 120, 1.0, u=(t - T_CHASHKI) / .3, seed=34)
    table = kit["table"] + items + pot
    person = behind_table(fg, table, front_y - R.K_TABLE[3], front_y)
    # чашка в руке — поверх стола; когда ставит на стол, она уже над крышкой
    world = kit["bg"] + rack_mug + person + mug1 + kit["front"]
    # ── камера: хлёст-влёт справа, дрейф вправо-вверх к часам на «Теперь» и обратно, мини-тряска на «обеда»
    wi = whip_in(t, 25.3, .32)
    to_clock = sm(t, T_TEPER - .2, T_TEPER + .3) * (1 - sm(t, T_TEPER + .7, T_TEPER + 1.3))
    to_clock2 = sm(t, T_OBEDA - .25, T_OBEDA) * (1 - sm(t, T_OBEDA + .3, T_OBEDA + .55))
    tc = max(to_clock, to_clock2 * .7)
    drift = sm(t, 25.1, 28.5)
    cx = lerp(480, 520, drift) + 160 * tc + 300 * wi
    cy = 890 - 230 * tc
    sc_cam = 1.3 + .05 * drift + .08 * tc - .12 * wi
    sh = PR.shake(t, T_OBEDA + .1, 12, .3, seed=7)
    rr = 5 * wi + .4 * math.sin(t * 1.2)
    set_ink(sc_cam)
    return lib.svg(cam_wrap(world, cx + sh[0], cy + sh[1], sc_cam, rr))


# ═══════════════════════════════ s14: спальня сбоку, спит на боку с улыбкой ═══════════════════════════════
S14_S = .9
S14_HEAD = (300.0, 1212.0)            # где голова лежит на подушке


def dima14(t):
    """Дима на боку: фигура (лицом влево) повёрнута на −90° — голова на подушке слева, лицо чуть к подушке, ладонь под щекой.
    Ноги и туловище ниже плеч — под одеялом (одеяло кладёт сцена)."""
    s = S14_S
    sc = s * people.HEIGHT["dima"]
    breath = math.sin(2 * math.pi * (t - 28.1) / 2.2)
    inhale = sm(t, T_SPOK - .05, T_SPOK + .45) * (1 - sm(t, T_SPOK + .6, T_SPOK + 1.1))
    br = .35 * breath + inhale
    e = ex("soft", smile=.6 + .25 * sm(t, T_SPIT, T_SPIT + .4), bags=False)
    # в «стоячей» системе фигуры: таз (0, 0), голова вверху; кисть ближней руки — под щекой
    x0, y0 = 0.0, 0.0
    probe = people.figure("dima", x0, y0, s, e, flip=True, layers=("body",), head_ang=.12)
    hx, hy = probe["head"]
    cheek = (hx - 175 * sc, hy + 70 * sc)
    arms = {"n": ("ik", (2 * x0 - cheek[0], cheek[1]), -1), "f": ("ang", .3, .4)}   # цели — в неотражённой системе
    hands = {"n": {"dir": (-.15, -1), "curl": (.15, .2, .25, .3), "thumb": .75, "spread": .15}, "f": {"kind": "none"}}
    kw = dict(flip=True, head_ang=.12 + .03 * breath, arms=arms, hands=hands, torso_k=1 + .03 * br)
    fg = people.figure("dima", x0, y0, s, e, layers=("pelvis", "body"), **kw)
    arm = people.figure("dima", x0, y0, s, e, layers=("arm_n",), **kw)["svg"]
    # повернуть: голова влево; голова встаёт на подушку
    a = -90.0
    ar = math.radians(a)
    rx, ry = hx * math.cos(ar) - hy * math.sin(ar), hx * math.sin(ar) + hy * math.cos(ar)
    tx, ty = S14_HEAD[0] - rx, S14_HEAD[1] - ry + 3 * br
    mt = R.B_SIDE_BED[1] - 118 * R.B_SIDE_BED[2]
    cl = lib.clip_of([(-2000, -2000), (400, -2000), (396, mt - 168), (447, mt - 243), (582, mt - 258), (630, mt - 194), (730, mt - 224), (840, mt - 180), (940, mt - 194), (1000, mt - 125), (3000, mt - 125), (3000, 4000), (-2000, 4000)])
    # выше линии одеяла правее его края тела не видно (капюшон не торчит)
    svg = f'<g clip-path="url(#{cl})"><g transform="translate({tx:.2f} {ty:.2f}) rotate({a})">{fg["svg"]}</g></g>'
    arm = f'<g transform="translate({tx:.2f} {ty:.2f}) rotate({a})">{arm}</g>'
    return svg, arm, (tx, ty), br


def quilt14(t, hip, br):
    """Одеяло по фигуре: от плеча через бедро к согнутым коленям; вдох поднимает его."""
    x, y, k = R.B_SIDE_BED
    mt = y - 118 * k
    hx = hip[0]
    up = 14 * br
    pts = [(400, mt + 40, 1), (402, mt - 190 - up * .6), (445, mt - 262 - up), (580, mt - 276 - up), (hx - 10, mt - 200 - up * .8),
           (hx + 90, mt - 230 - up * .5), (hx + 200, mt - 185), (hx + 300, mt - 200), (hx + 360, mt - 130), (x + 285 * k, mt - 60),
           (x + 296 * k, mt + 74 * k, 1), (400, mt + 74 * k, 1)]
    col, sh = "#c8553d", "#9a3b2b"
    inner = blob([(380, mt + 30), (x + 300 * k, mt + 30), (x + 300 * k, mt + 80 * k), (380, mt + 80 * k)], sh)
    inner += line([(500, mt - 140 - up), (560, mt - 60)], 4, sh, seed=16401)
    inner += line([(hx + 60, mt - 160 - up * .5), (hx + 120, mt - 40)], 4, sh, seed=16402)
    inner += line([(hx + 250, mt - 150), (hx + 290, mt - 50)], 4, sh, seed=16403)
    inner += blob([(440, mt - 120), (470, mt - 160 - up), (520, mt - 168 - up), (470, mt - 110)], lib.mix(col, "#ffffff", .2))
    return shape(pts, col, inner, w=4.2, seed=16400)


def frame14(t):
    lib.dyn_begin()
    room = R.bed_side(t, warm=1.0)
    body, arm, hip, br = dima14(t)
    q = quilt14(t, (640, 0), br)
    # перевёрнутая пустая кружка на тумбочке
    sx, sy = R.B_SIDE_STAND
    top = sy - 260
    mug = PR.coffee_mug(sx - 92, top, .85, fill=0.0, upside=True, seed=41, col="blue")
    # Z из-за головы на «спит»
    hx, hy = S14_HEAD
    z = PR.zzz(hx + 60, hy - 170, 1.15, t - T_SPIT, u=clamp((t - T_SPIT) / .25)) if t > T_SPIT else ""
    # «ночью»: луна в окне светлеет, мерцают звёздочки
    wx0, wy0, wx1, wy1 = R.B_SIDE_WIN
    mu = sm(t, T_NOCH - .1, T_NOCH + .3)
    moon = ""
    if mu > 0:
        mpx, mpy = wx0 + (wx1 - wx0) * .3, wy0 + (wy1 - wy0) * .72   # ниже луны окна: в кадре видна нижняя часть окна
        sx_, sy_ = PR.pop(t, T_NOCH - .1, amp=.2)
        moon = f'<g transform="translate({mpx} {mpy}) scale({sx_:.3f} {sy_:.3f}) translate({-mpx} {-mpy})">{PR.moon(mpx, mpy, 46, halo=mu)}</g>'
        for j, (ox, oy, d) in enumerate(((-110, -60, 0), (70, 90, .15), (-60, 120, .3))):
            moon += PR.star4(mpx + ox, mpy + oy, 13, u=clamp((t - T_NOCH - d) / .2) * (.7 + .3 * math.sin(t * 9 + j)))
    world = room["bg"] + moon + mug + body + q + arm + z + room["front"]
    # камера: от лица медленный откат и мягкий дрейф; влёт хлёстом
    wi = whip_in(t, 28.3, .3)
    pb = sm(t, 28.1, 30.35)
    cx = lerp(380, 470, pb) - 300 * wi
    cy = lerp(1170, 1050, pb)
    sc_cam = lerp(2.05, 1.45, pb) + .1 * wi
    rr = -4 * wi + .5 * math.sin(t * .9)
    set_ink(sc_cam)
    return lib.svg(cam_wrap(world, cx, cy, sc_cam, rr))


FRAMES = {"s12": frame12, "s13": frame13, "s14": frame14}


def frame(sid, t):
    lib.DEFS.clear()
    lib.static_done()
    return FRAMES[sid](t)
