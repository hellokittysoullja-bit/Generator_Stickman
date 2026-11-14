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
S12_HIP = (400.0, 1405.0)
S12_MUG = (880.0, R.K_TABLE[2] - 62)


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


def behind_table(fg, table, top_y, front_y):
    """Сидящий за столом: ноги под столом → стол → туловище (видно выше дальнего края крышки) → руки (лежат на крышке)."""
    s, e, kw = fg["kw"]
    x, y = fg["hip"]
    body = people.figure("dima", x, y, s, e, layers=("arm_f", "body"), **kw)["svg"]
    arm_n = people.figure("dima", x, y, s, e, layers=("arm_n",), **kw)["svg"]
    arm_f = people.figure("dima", x, y, s, e, layers=("arm_f",), **kw)["svg"]
    cb = lib.clip_rect(-2000, -3000, 6000, 3000 + top_y)
    ca = lib.clip_rect(-2000, -3000, 6000, 3000 + front_y)
    return (fg["svg"] + table + f'<g clip-path="url(#{ca})">{arm_f}</g>' + f'<g clip-path="url(#{cb})">{body}</g>'
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
    gy = hy - 330 - 16 * math.sin(t * 2.3) + (60 if t > T_SILNEE else 0) * ease_out(clamp((t - T_SILNEE) / .3))
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
    cx = lerp(500, 560, push)
    cy = lerp(940, 920, push)
    s = lerp(1.24, 1.42, push)
    sh = PR.shake(t, T_SILNEE, 20, .4, seed=5)
    rr = .5 * math.sin(t * 1.1) + damp(t, T_SILNEE, 1.2, 3, 6)
    set_ink(s)
    return lib.svg(cam_wrap(world, cx + sh[0], cy + sh[1], s, rr))


FRAMES = {"s12": frame12}


def frame(sid, t):
    lib.DEFS.clear()
    lib.static_done()
    return FRAMES[sid](t)
