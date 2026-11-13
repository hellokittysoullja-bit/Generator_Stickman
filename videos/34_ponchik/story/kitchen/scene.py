"""Сцена kitchen рилса 34 «сорвался — гулять так гулять»: планы s01 s02 s03 s04 s06 s14 s15.
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика). Мир — world.py (кухня рилса 29, перестроенная под стол,
коробка пончиков, календарик), Дима сидит слева лицом вправо (people.py из рилсов 27/32, таз (230, 1262)).
Удары — на словах по voice/words.json."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
import world as Wd  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


def ww(word, after=0.0):
    """Время начала первого слова word (без знаков) не раньше after."""
    for w in WORDS:
        if w["start"] >= after and w["word"].strip(".,:;!?«»").lower() == word:
            return w["start"]
    raise KeyError(word)


BS = 0.6
HIP = np.array([230.0, 1262.0])
FEET = {"n": ((450, 1468), 0.0), "f": ((425, 1462), 0.0)}


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def dima(t, arms, hands=None, expr=None, hip=None, lean=0.12, head_ang=0.0, feet=None):
    hip = HIP if hip is None else np.array(hip, float)
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet or FEET, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=0.0, strings=(2 * osc(t, 1.3), 1.5 * osc(t, 1.1, 1)))
    return people.draw(p, "dima")


def table_world(t, d, *, cal=None, on_table="", mid="", front="", back_extra=""):
    """Слои: кухня, стул, задние ножки стола, ноги Димы, столешница, предметы, дальняя рука, тело, mid, ближняя рука, front."""
    w = [Wd.kitchen_bg(t, cal=cal, extra=back_extra)]
    w.append(room.chair(HIP[0], HIP[1] + 4, 1, 2300))
    w.append(Wd.table_back())
    w.append(d.get("legs", ""))
    w.append(Wd.table_top())
    w.append(on_table)
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(mid)
    w.append(d["arm_n"])
    w.append(front)
    return "".join(w)


# ═════════════════════════ общие помощники ═════════════════════════
BOX_X, BOX_Y, BOX_K = 690.0, 1126.0, 0.95
PLATE = (478.0, 1136.0, .66)
T_NED, T_DERZH = wi(1), wi(2)                  # «неделю» 0.48, «держал» 1.08
T_SYEL, T_PONCH = wi(5), wi(7)                 # «съел» 2.04, «пончик» 3.0
T_PODUM, T_SORV = wi(9), wi(12)                # «подумал» 3.76, «сорвался» 4.96
T_DOEM, T_KOROB = wi(13), wi(15)               # «доем» 5.84, «коробку» 6.64
T_HOCH, T_SORV2, T_SOVS = wi(21), wi(22), wi(23)   # 9.68, 10.16, 10.56
T_PONCHIKA, T_GOVOR = ww("пончика"), ww("говорит")          # 25.92, 26.76
T_BYV, T_DALSHE, T_KOROBKA = ww("бывает", 27), ww("дальше"), ww("коробка")   # 27.79, 28.72, 29.49


def hook_zoom(t, t0=0.0, mx=0.4, dur=0.22, rot=-3.0):
    """Влёт (правила 28/29): масштаб 1/(1+mx) → 1.05 за dur, отскок к 1 за 0.3 с; поворот rot → +0.8 → 0."""
    u = (t - t0) / dur
    if u <= 0:
        return 1 / (1 + mx), rot
    if u < 1:
        e = ease_out(u, 3)
        return 1 / (1 + mx) + (1.05 - 1 / (1 + mx)) * e, rot * (1 - e) + .8 * e
    v = (t - t0 - dur) / 0.3
    if v < 1:
        e = ease_io(v)
        return 1.05 - .05 * e, .8 * (1 - e)
    return 1.0, 0.0


def punch(t, t0, amp=.08, up=.06, down=.35):
    """Удар камерой: +amp за up с, возврат за down с."""
    if t < t0:
        return 0.0
    if t < t0 + up:
        return amp * ease_out((t - t0) / up, 2)
    return amp * (1 - ease_io(clamp((t - t0 - up) / down)))


def whip_in(t, t0, dur=0.2):
    return 1 - ease_out(clamp((t - t0) / dur), 3)


def shake(t, t0, amp=10.0, dur=.4, f=13.0):
    if t < t0 or t > t0 + dur:
        return 0.0, 0.0
    e = (1 - (t - t0) / dur) ** 2
    return amp * e * math.sin((t - t0) * f * 6.28), amp * .7 * e * math.cos((t - t0) * f * 5.1)


def mouth_of(d, lean, ha):
    return d["head"] + people.rot(np.array([66.0, 94.0]) * BS, lean * .5 + ha)


def slot_world(i, x=None, y=None, k=None):
    x = BOX_X if x is None else x
    y = BOX_Y if y is None else y
    k = BOX_K if k is None else k
    sx, sy, rr = Wd.box_slots()[i]
    return np.array([x + sx * k, y + sy * k]), rr * k


def bits(t, t0, origin, n=14, seed=1, spread=(-1.0, 1.0), speed=420.0, up=1.0, life=.7, floor_y=None, sz=1.0, cols=None):
    """Крошки и посыпка: вылетают из origin в момент t0, падают с гравитацией, к концу жизни уменьшаются (без прозрачности)."""
    if t < t0:
        return ""
    rs = np.random.RandomState(seed)
    o = []
    cols = cols or ("#c98a45", "#e8b46a", "#4fb3d9", "#f2d24b", "#7cc46a", "#f27fa5", "#c98a45")
    for j in range(n):
        a = rs.uniform(*spread) - math.pi / 2 * up
        v = speed * rs.uniform(.5, 1.1)
        lt = life * rs.uniform(.7, 1.1)
        tt = t - t0
        if tt > lt:
            continue
        x = origin[0] + math.cos(a) * v * tt
        y = origin[1] + math.sin(a) * v * tt + 900 * tt * tt
        if floor_y is not None and y > floor_y:
            y = floor_y
        r = (3.2 + 2.6 * rs.uniform()) * sz * (1 - (tt / lt) ** 3)
        if r < .6:
            continue
        col = cols[j % len(cols)]
        if j % 3 == 1:
            ang = rs.uniform(0, 180) + 400 * tt
            o.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f})"><rect x="{-r * 1.4:.1f}" y="{-r * .45:.1f}" width="{r * 2.8:.1f}" '
                     f'height="{r * .9:.1f}" rx="{r * .45:.1f}" fill="{col}"/></g>')
        else:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" stroke="{INK}" stroke-width="1.1"/>')
    return "".join(o)


def cloud_pts(cx, cy, rx, ry, wob=0.0, t=0.0, n=9):
    pts = []
    for j in range(n * 6):
        th = 2 * math.pi * j / (n * 6)
        bump_ = abs(math.sin(n * th / 2 + .4)) ** .7
        r = 1 + .14 * bump_ + wob * .08 * math.sin(th * 3 + t * 9)
        pts.append((cx + rx * r * math.cos(th), cy + ry * r * math.sin(th)))
    return pts


def thought_cloud(cx, cy, k, t, hx, hy, content=""):
    """Облако мысли (как в рилсе 32): пузырьки от головы (hx, hy), content — что внутри (рисуется поверх облака)."""
    o = []
    rx, ry = 150 * k, 130 * k
    for j, u in enumerate((.3, .55, .76)):
        bx, by = hx + (cx - hx) * u, hy + (cy + ry * .8 - hy) * u
        r = (10 + 12 * u) * k ** .5
        o.append(shape(ellipse_pts(bx, by, r, r * .9, 12), "#ffffff", blob(ellipse_pts(bx + r * .3, by + r * .3, r * .8, r * .7, 10), "#dfe4ee"), w=3.4,
                       seed=4100 + j))
    pts = cloud_pts(cx, cy, rx, ry, .4, t)
    inner = blob(cloud_pts(cx + 18 * k, cy + 24 * k, rx * .95, ry * .9, .4, t), "#dfe4ee")
    inner += blob(cloud_pts(cx - 6 * k, cy - 4 * k, rx * .9, ry * .82, .4, t), "#ffffff")
    o.append(shape(pts, "#ffffff", inner, w=5, seed=4110))
    o.append(content)
    return "".join(o)


def donut_in_hand(t, c, kind, dirv, tilt=.72, r=34.0, bite=0.0, bite_ang=180.0, curl=.62, seed=0):
    """Пончик в ближней руке: c — центр пончика, dirv — направление от запястья к пончику.
    Возвращает (mid — пончик, wrist, hand dict)."""
    dirv = np.array(dirv, float)
    dirv /= np.linalg.norm(dirv)
    wr = np.array(c) - dirv * (r + 34)
    mid = Wd.donut(c[0], c[1], r, kind, tilt, bite=bite, bite_ang=bite_ang, seed=3700 + seed)
    hand = dict(kind="open", dir=tuple(dirv), curl=(curl, curl + .05, curl + .1, curl + .15), spread=.04, thumb=.55, bend=.08)
    return mid, tuple(wr), hand


def far_rest(x=470.0, y=1108.0):
    return ("ik", (x, y), -1), dict(kind="open", dir=(1, .12), curl=(.2, .25, .3, .35), spread=.08, thumb=.4)


# ═════════════════════════ s01: хук — жуёт сельдерей, 7 крестиков на «неделю», коробка светится ═════════════════════════
def celery_chew(t, expr, lean0=.13, head_ang=0.0, rate=3.6, amp=1.0, far=None):
    """Дима жуёт сельдерей: откушенный конец у рта, кулак держит стебель, листья торчат вверх-вперёд."""
    chew = osc(t, rate) * amp
    lean, hang = lean0 + .006 * chew, .03 * chew + head_ang
    farA, farH = far or far_rest(420, 1104)
    probe = dima(t, {"n": ("ik", (380, 1080), -1), "f": farA}, {}, expr, lean=lean, head_ang=hang)
    mouth = mouth_of(probe, lean, hang)
    ang = math.radians(28 + 4 * chew)
    u = np.array([math.cos(ang), math.sin(ang)])
    a = mouth - u * 8
    fist = a + u * 64
    hd = np.array([-.3, -1.0]) / np.linalg.norm([-.3, -1.0])
    wr = fist - hd * 26
    arms = {"n": ("ik", tuple(wr), -1), "f": farA}
    hands = {"n": dict(kind="open", dir=tuple(hd), curl=(.85, .9, .92, .95), spread=.02, thumb=.85, bend=.05), "f": farH}
    d = dima(t, arms, hands, expr, lean=lean, head_ang=hang)
    stalk = Wd.celery(tuple(a), tuple(a + u * 175), 17, bite=0.0)
    return d, stalk, chew


def s01(t):
    z, rot = hook_zoom(t, 0.0, .4, .22, -3.0)
    k = ease_io(clamp(t / 1.6))
    hit = punch(t, T_NED, .08, .06, .4)
    s = 1.5 * z * (1 + .04 * k) * (1 + hit)
    sx, sy = shake(t, T_NED, 6, .3)
    cam = (555 - 30 * (1 - z) + 14 * k + sx, 930 + 40 * (1 - z) - 10 * k + sy, s, rot + .3 * osc(t, .5))
    set_ink(s)
    # крестики: на «неделю» пробегают по 7 клеткам
    marks = [clamp((t - (T_NED + .02 + i * .065)) / .1) for i in range(7)]
    jolt = bump(t, T_NED + .45, .3)
    expr = dict(lid=.42 + .25 * jolt, look=(.75, .5 - .2 * jolt), brows="worry", mouth="chew", open=.12 + .12 * max(0, osc(t, 3.6)),
                smile=-.4, closed=blink_at(t, 1.25, .14), hair=3 * jolt * osc(t, 8))
    d, stalk, chew = celery_chew(t, expr, head_ang=-.02 + .03 * jolt)
    glow = .75 + .25 * osc(t, 2.2)
    lid = .09 + .025 * osc(t, 3.1) + .03 * bump(t, T_NED + .55, .35)
    on = Wd.donut_box(BOX_X, BOX_Y, BOX_K, lid=lid, glow=glow, t=t) + Wd.plate(*PLATE)
    w = table_world(t, d, cal=Wd.calendar(marks), on_table=on, mid=stalk)
    return Wd.compose(w, cam, t)


# ═════════════════════════ s02: рука тянется к коробке, «съел» — хватает пончик, «пончик» — откусывает ═════════════════════════
def s02(t):
    k = ease_io(clamp((t - 1.2) / 2.55))
    hit = punch(t, T_PONCH, .07, .06, .4)
    s = (1.75 + .2 * k) * (1 + hit)
    sx, sy = shake(t, T_PONCH, 5, .3)
    cam = (520 + 0 * k + sx, 990 - 20 * k + sy, s, -.6 + .8 * k + .3 * osc(t, .6))
    set_ink(s)
    slot = 3                                   # передний левый — розовый
    sp, sr = slot_world(slot)
    reach = ease_io(clamp((t - 1.2) / (T_SYEL - .05 - 1.2)))      # рука к коробке
    lift = ease_io(clamp((t - T_SYEL - .08) / .55))                # пончик к лицу
    lid = .1 + .3 * smooth(1.5, T_SYEL - .1, t) - .25 * smooth(T_SYEL + .2, T_SYEL + .5, t)
    bite = clamp((t - T_PONCH) / .07)
    bliss = smooth(T_PONCH - .02, T_PONCH + .12, t)
    lean = .13 + .2 * reach * (1 - lift) + .06 * lift
    open_m = smooth(T_PONCH - .35, T_PONCH - .05, t) * (1 - bite)
    expr = dict(lid=.45 + .35 * lift * (1 - bliss), look=(.8, .55 - .5 * lift), brows="up" if lift > .3 else "worry",
                mouth="chew" if bliss < .5 else "smile", open=.15 + .7 * open_m, smile=.2 + .8 * bliss, laugh=bliss,
                puff=.35 * bliss * (1 + .2 * osc(t, 4)), closed=blink_at(t, 1.55, .14), hair=4 * bump(t, T_PONCH, .3) * osc(t, 9))
    ha = -.04 * lift + .05 * bump(t, T_PONCH, .3)
    probe = dima(t, {"n": ("ik", (380, 1080), -1), "f": far_rest(420, 1104)[0]}, {}, expr, lean=lean, head_ang=ha)
    mouth = mouth_of(probe, lean, ha)
    donuts = list(Wd.DEFAULT_DONUTS)
    mid = ""
    if t < T_SYEL:
        # кисть над гнездом, пальцы вниз в коробку
        rest = np.array([520.0, 1104.0])
        tgt = sp + np.array([-40.0, -30.0])
        wr = rest + (tgt - rest) * reach + np.array([0, -40 * math.sin(math.pi * reach)])
        hand = dict(kind="open", dir=(1, .25 + .5 * reach), curl=(.25 + .25 * reach,) * 4, spread=.12 * (1 - reach), thumb=.3, bend=.1)
        arms_n, hand_n = ("ik", tuple(wr), -1), hand
    else:
        donuts[slot] = None
        c0 = sp + np.array([0.0, -8.0])
        c1 = mouth + np.array([46.0, 14.0]) + np.array([22.0, 10.0]) * smooth(T_PONCH + .05, T_PONCH + .4, t)
        e = lift
        c = c0 + (c1 - c0) * e + np.array([0, -60 * math.sin(math.pi * e)])
        dv = np.array([1.0, .5]) * (1 - e) + np.array([-.55, -.6]) * e
        tilt = .5 + .25 * e
        mid, wr, hand_n = donut_in_hand(t, c, "pink", dv, tilt=tilt, r=sr * 1.0, bite=bite, bite_ang=200, seed=11)
        arms_n = ("ik", wr, -1)
        mid += bits(t, T_PONCH, c + np.array([-30.0, -6.0]), n=16, seed=3, spread=(-1.6, .9), speed=380, life=.8, sz=1.1)
    farA, farH = far_rest(420, 1104)
    d = dima(t, {"n": arms_n, "f": farA}, {"n": hand_n, "f": farH}, expr, lean=lean, head_ang=ha)
    on = Wd.donut_box(BOX_X, BOX_Y, BOX_K, lid=lid, donuts=donuts, glow=.8 + .2 * osc(t, 2.2), t=t) + Wd.plate(*PLATE)
    stalk = Wd.celery((PLATE[0] - 30, PLATE[1] - 30), (PLATE[0] + 120, PLATE[1] - 46), 15, bite=.6)
    w = table_world(t, d, cal=Wd.calendar([1.0] * 7), on_table=on + stalk, mid=mid)
    return Wd.compose(w, cam, t)


# ═════════════════════════ s03: замер с надкушенным пончиком; облако с календарём трескается на «сорвался» ═════════════════════════
def s03(t):
    k = ease_io(clamp((t - 3.35) / 2.45))
    sx, sy = shake(t, T_SORV, 12, .45)
    s = (1.85 + .15 * k) * (1 + punch(t, T_SORV, .05, .05, .35))
    cam = (440 + 10 * k + sx, 860 + 15 * k + sy, s, .4 * osc(t, .5) + 1.4 * bump(t, T_SORV, .3) * osc(t, 7))
    set_ink(s)
    wide = smooth(3.45, 3.75, t)
    sag = ease_out(clamp((t - T_SORV - .05) / .5), 2)
    expr = dict(lid=.35 + .6 * wide - .45 * sag, look=(.15 - .1 * sag, .1 + .5 * sag), brows="up" if sag < .4 else "worry",
                mouth="full" if sag < .5 else "tired", puff=.3 * (1 - .5 * sag), closed=blink_at(t, 4.3, .14),
                hair=5 * bump(t, T_SORV, .35) * osc(t, 9))
    lean = .1 + .12 * sag + .004 * osc(t, 1.2)
    ha = .1 * sag - .02 * wide
    probe = dima(t, {"n": ("ik", (380, 1080), -1), "f": far_rest(405, 1102)[0]}, {}, expr, lean=lean, head_ang=ha)
    hx, hy = probe["head"]
    # пончик в руке у груди: застыл, на «сорвался» рука опускается
    c = np.array([hx + 80, hy + 150 + 40 * sag]) + np.array([0, 2 * osc(t, 7) * (1 - wide) ])
    mid, wr, hand_n = donut_in_hand(t, c, "pink", (-.4, -.9), tilt=.72, r=sr_(), bite=1.0, bite_ang=200, seed=11)
    farA, farH = far_rest(405, 1102)
    d = dima(t, {"n": ("ik", wr, -1), "f": farA}, {"n": hand_n, "f": farH}, expr, lean=lean, head_ang=ha)
    # облако мысли: выскакивает на «подумал», в нём календарь с 7 крестиками
    pop = Wd.clamp_((t - (T_PODUM - .15)) / .3)
    ck = .0 if pop <= 0 else (.2 + .8 * lib.back_out(pop, 2.2))
    front = ""
    if ck > 0:
        cx, cy = hx + 215, hy - 255
        crack = ease_out(clamp((t - T_SORV) / .25), 2)
        fall = ease_in(clamp((t - T_SORV - .1) / .7), 1.6)
        cal = Wd.calendar([1.0] * 7, x=(cx - 95 * ck, cy - 100 * ck, cx + 95 * ck, cy + 100 * ck), k=ck, split=crack, fall=fall, seed=3520)
        front = thought_cloud(cx, cy, ck * (1 + .02 * osc(t, 1.3)), t, hx + 90, hy - 110, cal)
    on = Wd.donut_box(BOX_X, BOX_Y, BOX_K, lid=.1, donuts=[x if i != 3 else None for i, x in enumerate(Wd.DEFAULT_DONUTS)], glow=.7 + .2 * osc(t, 2.2)) \
        + Wd.plate(*PLATE)
    w = table_world(t, d, cal="", on_table=on, mid=mid, front=front)
    return Wd.compose(w, cam, t)


def sr_():
    return slot_world(3)[1]


# ═════════════════════════ s04: подтягивает коробку, «доем» — распахивает крышку, «коробку» — второй пончик в рот ═════════════════════════
def s04(t):
    k = ease_io(clamp((t - 5.4) / 2.4))
    s = (1.7 + .12 * k) * (1 + punch(t, T_KOROB, .08, .06, .4) + .04 * punch(t, T_DOEM, 1, .05, .3))
    sx, sy = shake(t, T_KOROB, 7, .3)
    cam = (520 + 10 * k + sx, 990 - 10 * k + sy, s, -.5 + .6 * k + .8 * bump(t, T_KOROB, .3) * osc(t, 8))
    set_ink(s)
    pull = ease_io(clamp((t - 5.4) / .4))
    bx = BOX_X + 70 - 110 * pull                           # коробка едет к Диме
    lid = 0.1 + .9 * clamp(Wd.clamp_(lib.spring(max(0, t - T_DOEM), 3.2, 7)))
    if t < T_DOEM:
        lid = .1
    grab_t = 6.12
    feed = ease_in(clamp((t - grab_t) / (T_KOROB - grab_t)), 1.5)
    puffk = smooth(T_KOROB - .04, T_KOROB + .08, t)
    puff = puffk * (1 + .15 * math.exp(-6 * max(0, t - T_KOROB)) * math.sin(max(0, t - T_KOROB) * 30) + .05 * osc(t, 3.5))
    det = smooth(5.4, 5.6, t)
    expr = dict(lid=.55 + .4 * smooth(T_DOEM, T_DOEM + .1, t), look=(.7 - .6 * feed, .5 - .4 * feed), brows="det" if t < T_DOEM + .2 else "up",
                mouth="full" if puffk > .5 else ("chew" if feed > .3 else "flat"), open=.6 * feed, puff=max(.25, puff), chew=osc(t, 4),
                hair=5 * bump(t, T_KOROB, .3) * osc(t, 9))
    lean = .16 + .06 * det - .04 * feed
    ha = .03 * bump(t, T_KOROB, .3)
    probe = dima(t, {"n": ("ik", (380, 1080), -1), "f": far_rest(405, 1102)[0]}, {}, expr, lean=lean, head_ang=ha)
    mouth = mouth_of(probe, lean, ha)
    donuts = [x if i != 3 else None for i, x in enumerate(Wd.DEFAULT_DONUTS)]
    mid = ""
    if t < T_DOEM + .05:
        # обе руки на коробке: тянут к себе, ближняя откидывает крышку
        wn = np.array([bx - 150, BOX_Y - 40 - 50 * smooth(T_DOEM - .15, T_DOEM, t)])
        arms_n, hand_n = ("ik", tuple(wn), -1), dict(kind="open", dir=(1, .3), curl=(.45,) * 4, spread=.05, thumb=.4)
        farA = ("ik", (bx - 120, BOX_Y - 30), -1)
        farH = dict(kind="open", dir=(1, .2), curl=(.4,) * 4, spread=.05, thumb=.4)
    elif t < grab_t:
        u = ease_io(clamp((t - T_DOEM - .05) / (grab_t - T_DOEM - .05)))
        sp, sr = slot_world(1, x=bx)
        wn = np.array([bx - 150, BOX_Y - 90]) * (1 - u) + (sp + np.array([-50, -26])) * u
        arms_n, hand_n = ("ik", tuple(wn), -1), dict(kind="open", dir=(1, .5), curl=(.3 + .2 * u,) * 4, spread=.1, thumb=.3)
        farA, farH = far_rest(405, 1102)
    else:
        donuts[1] = None
        sp, sr = slot_world(1, x=bx)
        c0 = sp + np.array([0.0, -6.0])
        c1 = mouth + np.array([10.0, 4.0])
        c = c0 + (c1 - c0) * feed + np.array([0, -50 * math.sin(math.pi * feed)])
        if puffk < .5:
            mid, wr, hand_n = donut_in_hand(t, c, "choc", np.array([1.0, .4]) * (1 - feed) + np.array([-.6, -.5]) * feed, tilt=.5 + .25 * feed, r=sr,
                                            seed=21)
        else:        # пончик уже во рту: кулак у щеки, отходит
            back = ease_out(clamp((t - T_KOROB) / .4), 2)
            wr = tuple(mouth + np.array([70 + 60 * back, 60 + 70 * back]))
            hand_n = dict(kind="open", dir=(-.6, -.6), curl=(.55,) * 4, spread=.05, thumb=.5)
            mid = bits(t, T_KOROB, mouth + np.array([40.0, 4.0]), n=10, seed=5, spread=(-1.0, .8), speed=430, life=.6, sz=.7)
        arms_n = ("ik", wr, -1)
        farA = ("ik", (bx - 130, BOX_Y - 34), -1)
        farH = dict(kind="open", dir=(1, .2), curl=(.4,) * 4, spread=.05, thumb=.4)
    d = dima(t, {"n": arms_n, "f": farA}, {"n": hand_n, "f": farH}, expr, lean=lean, head_ang=ha)
    glow = .7 + .6 * math.exp(-3 * max(0, t - T_DOEM)) * (t > T_DOEM) + .15 * osc(t, 2.4)
    on = Wd.donut_box(bx, BOX_Y, BOX_K, lid=lid, donuts=donuts, glow=min(1.2, glow), t=t)
    if t > T_DOEM:
        on += sparkles(t, (bx, BOX_Y - 150), T_DOEM)
    w = table_world(t, d, cal=Wd.calendar([1.0] * 7), on_table=Wd.plate(PLATE[0] - 20, PLATE[1], PLATE[2], salad=1.0) * 0 + on, mid=mid)
    return Wd.compose(w, cam, t)


def sparkles(t, c, t0, n=6):
    o = []
    for j in range(n):
        a = -math.pi / 2 + (j - (n - 1) / 2) * .45
        u = clamp((t - t0 - j * .03) / .5)
        if u <= 0 or u >= 1:
            continue
        r = 90 + 120 * ease_out(u, 2)
        x, y = c[0] + r * math.cos(a) * 1.3, c[1] + r * math.sin(a) * .7
        sz = 26 * math.sin(math.pi * u)
        o.append(Wd.sparkle(x, y, sz, 20 * j, "#fff2a8"))
    return "".join(o)


# ═════════════════════════ s06: щёки набиты, «сорваться» — два последних, «совсем» — голова на стол ═════════════════════════
def s06(t):
    k = ease_io(clamp((t - 8.95) / 2.45))
    s = (1.95 - .4 * k) * (1 + punch(t, T_SOVS, .07, .05, .4))
    sx, sy = shake(t, T_SOVS + .02, 10, .35)
    cam = (470 + 50 * k + sx, 960 + 30 * k + sy, s, .5 - .6 * k + .3 * osc(t, .5))
    set_ink(s)
    bx = BOX_X - 40
    grab = ease_out(clamp((t - (T_SORV2 - .2)) / .2), 2)
    lift = ease_io(clamp((t - T_SORV2) / .25))
    drop = ease_in(clamp((t - (T_SOVS - .14)) / .14), 2)
    bounce = math.exp(-8 * max(0, t - T_SOVS)) * math.sin(max(0, t - T_SOVS) * 26) * (t > T_SOVS)
    chew = osc(t, 4.2)
    expr = dict(lid=.35 + .2 * lift, look=(.6, .4), brows="worry" if drop < .5 else "tired", mouth="full", puff=1.0, chew=chew, sugar=1.0,
                closed=max(blink_at(t, 9.5, .14), smooth(T_SOVS - .05, T_SOVS + .05, t)), hair=8 * bump(t, T_SOVS, .4) * osc(t, 9))
    lean = (.14 + .03 * chew + .1 * lift) * (1 - drop) + .6 * drop - .03 * bounce
    ha = .05 * chew * (1 - drop) + .5 * drop + .04 * bounce
    donuts = [None, "pink", None, None, "white", None]
    mid = ""
    # кисти: тянутся в коробку, хватают два последних; на «совсем» руки падают на стол
    s1, r1 = slot_world(1, x=bx)
    s4, r4 = slot_world(4, x=bx)
    if t < T_SORV2 - .2:
        u = ease_io(clamp((t - 8.95) / (T_SORV2 - .2 - 8.95)))
        wn = np.array([500.0, 1100.0]) * (1 - u) + (s4 + np.array([-52, -20])) * u
        wf = np.array([470.0, 1096.0]) * (1 - u) + (s1 + np.array([-52, -24])) * u
        hn = dict(kind="open", dir=(1, .4), curl=(.3 + .2 * u,) * 4, spread=.12, thumb=.3)
        hf = dict(kind="open", dir=(1, .35), curl=(.3 + .2 * u,) * 4, spread=.12, thumb=.3)
    else:
        donuts = [None] * 6
        up = np.array([0.0, -70.0]) * lift * (1 - drop) + np.array([20.0, 6.0]) * drop
        c4 = s4 + np.array([-10.0, -10.0]) + up + np.array([-40.0, 0]) * lift
        c1 = s1 + np.array([-20.0, -12.0]) + up + np.array([-30.0, 0]) * lift
        if drop > .5:
            c4 = np.array([bx - 20.0, 1120.0]) + np.array([0, -4 * bounce])
            c1 = np.array([bx + 40.0, 1100.0])
        m4, wn, hn = donut_in_hand(t, c4, "white", (1, .3), tilt=.55, r=r4, seed=31)
        m1, wf, hf = donut_in_hand(t, c1, "pink", (1, .3), tilt=.55, r=r1, seed=32)
        wn, wf = np.array(wn), np.array(wf)
        mid = m4
        hf = dict(hf)
        far_d = m1
    probe = None
    d = dima(t, {"n": ("ik", tuple(wn), -1), "f": ("ik", tuple(wf), -1)}, {"n": hn, "f": hf}, expr, lean=lean, head_ang=ha)
    on = Wd.donut_box(bx, BOX_Y, BOX_K, lid=1.0, donuts=donuts, glow=.25, t=t, crumbs=1.0)
    on += Wd.donut(bx + 230, 1120, 26, "choc", .5, bite=1.0, bite_ang=-150, seed=3750)
    if t >= T_SORV2 - .2:
        on += far_d
    if drop > .5:
        on += bits(t, T_SOVS, (bx - 260, 1100), n=12, seed=9, spread=(-1.2, 1.2), speed=300, life=.6, sz=.9)
        on += stars(t, d["head"], T_SOVS)
    w = table_world(t, d, cal=Wd.calendar([1.0] * 7), on_table=on, mid=mid)
    return Wd.compose(w, cam, t)


def stars(t, c, t0):
    u = t - t0
    if u < 0.05:
        return ""
    o = []
    for j in range(3):
        a = u * 5 + j * 2.09
        x, y = c[0] + 90 * math.cos(a), c[1] - 120 + 26 * math.sin(a)
        o.append(Wd.sparkle(x, y, 16 * min(1, u * 4), a * 30, "#f2d24b"))
    return "".join(o)


# ═════════════════════════ s14: спокойный вечер: доедает кусочек, салфетка, ладонь на груди ═════════════════════════
def s14(t):
    k = ease_io(clamp((t - 24.6) / 3.2))
    wh = whip_in(t, 24.6, .22)
    s = (1.75 + .15 * k)
    cam = (440 + 50 * k + 260 * wh, 960 - 15 * k, s, -2.0 * wh + .3 * osc(t, .45))
    set_ink(s)
    tp = T_PONCHIKA
    feed = ease_io(clamp((t - (tp - .45)) / .45))           # кусочек к рту
    back = ease_io(clamp((t - tp - .05) / .3))
    wipe = clamp((t - (tp + .35)) / .45)                     # салфетка у рта
    chest = ease_io(clamp((t - (T_GOVOR - .25)) / .3))
    chew = osc(t, 3.2) * smooth(tp, tp + .1, t) * (1 - smooth(T_GOVOR - .3, T_GOVOR, t))
    expr = dict(lid=.38 - .1 * chest, look=(.55 - .3 * feed, .45 - .2 * feed), brows="calm", mouth="smile" if chest > .3 or feed < .3 else "full",
                smile=.4 + .5 * chest, puff=.25 * smooth(tp - .02, tp + .1, t) * (1 - smooth(T_GOVOR - .5, T_GOVOR - .2, t)), chew=chew,
                closed=max(blink_at(t, 25.3, .14), .0), laugh=.0)
    lean = .1 + .02 * osc(t, .7)
    ha = .02 * chew - .03 * chest
    probe = dima(t, {"n": ("ik", (380, 1080), -1), "f": far_rest(405, 1102)[0]}, {}, expr, lean=lean, head_ang=ha)
    mouth = mouth_of(probe, lean, ha)
    mid = ""
    napkin_on = Wd.napkin(560, 1124, .7, 8)
    if t < tp + .05:
        c0 = mouth + np.array([95.0, 120.0]) + np.array([0, 4 * osc(t, 1.1)])
        c = c0 + (mouth + np.array([24.0, 8.0]) - c0) * feed
        mid, wr, hand_n = donut_in_hand(t, c, "white", (-.45, -.9), tilt=.72, r=27, bite=1.0, bite_ang=-60, curl=.45, seed=60)
        arms_n = ("ik", wr, -1)
    elif chest <= 0:
        # салфетка: рука берёт со стола и вытирает рот (ходит вбок)
        go = ease_io(clamp((t - tp - .05) / .3))
        wipe_dx = 16 * math.sin(wipe * math.pi * 3) * (wipe > 0) * (wipe < 1)
        pos = np.array([560.0, 1110.0]) * (1 - go) + (mouth + np.array([30.0 + wipe_dx, 14.0])) * go
        mid = Wd.napkin(pos[0], pos[1], .62, -20 + 10 * go, crumple=.6 * go)
        napkin_on = ""
        wr = pos + np.array([42.0, 40.0])
        arms_n = ("ik", tuple(wr), -1)
        hand_n = dict(kind="open", dir=(-.7, -.7), curl=(.55, .6, .65, .7), spread=.04, thumb=.5)
        if go >= 1 and wipe >= 1:
            pass
    else:
        # ладонь на груди
        chest_p = probe["head"] + np.array([20.0, 150.0])
        start = mouth + np.array([72.0, 54.0])
        wr = start + (chest_p + np.array([50.0, 34.0]) - start) * chest
        arms_n = ("ik", tuple(wr), -1)
        hand_n = dict(kind="open", dir=(-.85, -.5), curl=(.1, .1, .15, .2), spread=.06, thumb=.2, bend=.08)
        napkin_on = Wd.napkin(560, 1124, .62, -10, crumple=.6)
    farA, farH = far_rest(405, 1102)
    d = dima(t, {"n": arms_n, "f": farA}, {"n": hand_n, "f": farH}, expr, lean=lean, head_ang=ha)
    on = Wd.donut_box(BOX_X + 150, BOX_Y, BOX_K, lid=0.0) + Wd.plate(*PLATE, salad=0.0) + napkin_on
    w = table_world(t, d, cal=Wd.calendar([1.0] * 2 + [0.0] * 5), on_table=on, mid=mid)
    return Wd.compose(w, cam, t)


# ═════════════════════════ s15: «бывает» — кивает, «дальше» — хлоп крышкой, «Коробка» — отодвигает, палец вверх ═════════════════════════
def s15(t):
    k = ease_io(clamp((t - 27.4) / 2.8))
    s = (1.7 + .2 * k) * (1 + punch(t, T_DALSHE, .07, .05, .4))
    sx, sy = shake(t, T_DALSHE, 7, .3)
    cam = (505 + 10 * k + sx, 975 - 20 * k + sy, s, .4 - .5 * k + .3 * osc(t, .5))
    set_ink(s)
    nod = math.sin(clamp((t - T_BYV + .05) / .5) * math.pi * 2) * (T_BYV - .05 < t < T_BYV + .45)
    close = clamp((t - (T_DALSHE - .3)) / .3)
    lid = 1.0 - ease_in(close, 2.2)
    slide = ease_io(clamp((t - T_KOROBKA) / .35))
    thumb = ease_out(clamp((t - T_KOROBKA - .3) / .25), 2)
    bx = BOX_X - 60 + 260 * slide
    jump = 10 * math.exp(-10 * max(0, t - T_DALSHE)) * abs(math.sin(max(0, t - T_DALSHE) * 30)) * (t > T_DALSHE)
    expr = dict(lid=.42 + .2 * smooth(T_DALSHE - .05, T_DALSHE + .1, t), look=(.75 - .5 * thumb, .45 - .4 * thumb), brows="calm" if t < T_DALSHE else "up",
                mouth="smile", smile=.5 + .5 * thumb + .2 * smooth(T_DALSHE, T_DALSHE + .2, t), closed=blink_at(t, 29.1, .14))
    lean = .14 + .06 * close * (1 - slide) - .04 * thumb
    ha = .09 * nod
    donuts = ["choc", None, "white", "pink", "white", "choc"]
    hinge_y = BOX_Y - (Wd.BOX_HF + Wd.BOX_D) * BOX_K
    if t < T_KOROBKA:
        # обе руки на крышке: опускают её
        th = math.radians(105 * lid)
        fe = np.array([bx, hinge_y + (Wd.BOX_D * math.cos(th) - 129 * math.sin(th)) * BOX_K])
        hold = smooth(27.5, T_DALSHE - .35, t)
        rest_n, rest_f = np.array([500.0, 1104.0]), np.array([470.0, 1100.0])
        tn = fe + np.array([-80.0, -30.0])
        tf = fe + np.array([-20.0, -36.0])
        if t > T_DALSHE:
            tn = np.array([bx - 60.0, hinge_y - 30])
            tf = np.array([bx + 10.0, hinge_y - 36])
        wn = rest_n + (tn - rest_n) * hold
        wf = rest_f + (tf - rest_f) * hold
        arms = {"n": ("ik", tuple(wn), -1), "f": ("ik", tuple(wf), -1)}
        hands = {"n": dict(kind="open", dir=(1, .5), curl=(.2,) * 4, spread=.08, thumb=.3), "f": dict(kind="open", dir=(1, .5), curl=(.2,) * 4, spread=.08, thumb=.3)}
    else:
        # ближняя толкает коробку вправо, потом большой палец вверх
        push = np.array([bx - 170.0, BOX_Y - 40])
        up = np.array([470.0, 960.0])
        wn = push + (up - push) * thumb
        arms = {"n": ("ik", tuple(wn), -1), "f": far_rest(405, 1102)[0]}
        hands = {"n": dict(kind="open", dir=(1, -.18 * thumb + .3 * (1 - thumb)), curl=(.25 + .75 * thumb,) * 4, spread=.04, thumb=.25 - .25 * thumb,
                           bend=.05), "f": far_rest(405, 1102)[1]}
    d = dima(t, arms, hands, expr, lean=lean, head_ang=ha)
    on = Wd.donut_box(bx, BOX_Y, BOX_K, lid=lid, donuts=donuts, glow=.3 * lid, lid_jump=jump) + Wd.plate(*PLATE, salad=0.0)
    puff = sugar_puff(t, T_DALSHE, (bx, hinge_y + 20))
    w = table_world(t, d, cal=Wd.calendar([1.0] * 2 + [0.0] * 5), on_table=on + puff)
    return Wd.compose(w, cam, t)


def sugar_puff(t, t0, c):
    """Облачко сахарной пудры от хлопка крышки: клубы вдоль щели крышки разлетаются в стороны, поднимаются и
    уменьшаются (без прозрачности)."""
    u = t - t0
    if u < 0 or u > .75:
        return ""
    e = ease_out(u / .75, 2.2)
    o = []
    for j in range(8):
        sgn = -1 if j % 2 else 1
        rank = j // 2
        x = c[0] + sgn * (40 + 70 * rank + 120 * e * (1 + .3 * rank)) * (1 if sgn > 0 else .7)
        y = c[1] - 8 - 30 * e * (1 + .4 * (rank % 2)) - 8 * rank
        r = (34 - 4 * rank) * (1 - (u / .75) ** 2.5) * min(1, u * 10)
        if r > 1.5:
            o.append(shape(cloud_pts(x, y, r, r * .78, 0, 0, 5), "#fbf8f2", blob(ellipse_pts(x + r * .2, y + r * .3, r * .75, r * .45, 10), "#e9e2d6"),
                           w=2.6, seed=5200 + j))
    return "".join(o)


def test(t):
    set_ink(1.3)
    d = dima(t, {"n": ("ik", (520, 1110), -1), "f": ("ik", (482, 1112), -1)},
             {"n": dict(kind="open", dir=(1, .1)), "f": dict(kind="open", dir=(1, .12))}, dict(lid=.4, look=(.6, .3), mouth="flat"))
    on = Wd.plate(520, 1128, .8) + Wd.donut_box(800, 1124, .85, lid=.12, glow=1)
    w = table_world(t, d, on_table=on)
    return Wd.compose(w, (560, 880, 1.3, 0), t)


SHOTS = {"test": test, "s01": s01, "s02": s02, "s03": s03, "s04": s04, "s06": s06, "s14": s14, "s15": s15}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)


def test_head(t):
    set_ink(3)
    ex = [dict(lid=.4, look=(.6, .3), mouth="full", puff=1.0, sugar=1.0, brows="up"),
          dict(laugh=1.0, mouth="smile", smile=1.0, brows="calm", puff=.5, mouth_="chew"),
          dict(lid=1.0, look=(.0, .0), mouth="chew", open=.5, brows="up"),
          dict(lid=.3, look=(.6, .5), mouth="tired", brows="worry")][int(t)]
    d = dima(t, {"n": ("ik", (520, 1110), -1), "f": ("ik", (482, 1112), -1)},
             {"n": dict(kind="open", dir=(1, .1)), "f": dict(kind="open", dir=(1, .12))}, ex)
    w = table_world(t, d)
    return Wd.compose(w, (320, 960, 3.0, 0), t)


SHOTS["test_head"] = test_head
