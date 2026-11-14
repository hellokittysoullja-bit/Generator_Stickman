"""Рилс 62 «медитация», группа F: s15 (утро: облако с котлетой — щелчком прочь), s17 (призыв: Дима и кот смотрят на зрителя,
пером пишется «кот»), s18 (петля к кадру хука: вечер, «кот» ещё на месте, облако с обедом выскакивает снова).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Люди и кот — common/people.py, предметы — common/props.py,
комната — common/room.py (группа E; пока её нет — временная простая комната ниже), «кот» — common/hand_kot.py.
Печатных букв и цифр нет; единственная надпись — рукописное «кот» (s17, видно и в s18)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import hand_kot  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, shape  # noqa: E402,F401

import room as ROOM  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
EX = people.EXPR["dima"]


def wt(i):
    return WORDS[i]["start"]


T_VOZ = wt(59)        # «возвращается» 25.72
T_NAP = wt(65)        # «Напиши» 28.36
T_KOT = wt(66)        # «кот» 29.06 (звук «слово дописано» — 29.36)
T_MYS = wt(70)        # «мысли» 30.05
T_OBED = wt(73)       # «обед» 31.49


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def decay(t, t0, k=9.0, fr=20.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def shake(t, t0, amp, k=9.0, fr=19.0):
    return amp * decay(t, t0, k, fr), amp * .7 * decay(t, t0 + .013, k, fr * 1.13)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blinks(t, times, dur=.16):
    v = 0.0
    for tb in times:
        u = (t - tb) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def whip(g, t, t_in=None, t_out=None, amp=280.0, blur=30.0, dur=.2, side=1):
    """Хлёст: на входе план приезжает сбоку с размытием по x, на выходе уезжает."""
    dx, b = 0.0, 0.0
    if t_in is not None:
        e = ease_out(clamp((t - t_in) / dur), 2)
        dx += side * amp * (1 - e)
        b += blur * (1 - e)
    if t_out is not None:
        e = ease_in(clamp((t - t_out) / dur), 2)
        dx -= side * amp * e
        b += blur * e
    g = f'<g transform="translate({dx:.1f} 0)">{g}</g>'
    if b > .5:
        fid = lib.uid("wb")
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{b:.1f} 0"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return g


# ═════════════════════════════ мир: уголок для медитации (common/room.py, группа E) ═════════════════════════════
DX, DY = ROOM.seat()                      # таз Димы на подушке
DS = 1.0
CAT = (1005.0, 1705.0)                    # кот сидит на коврике справа от Димы (точка между задних лап)
CAT_K = .95


def room_layer(t, mode):
    r = ROOM.room_bg(t, mode)
    return r["bg"] + ROOM.cushion_layer(), r.get("front", "")


def dima(t, expr, pose="sit", u=0.0, breath=0.0, squash_y=1.0, extra_lean=0.0, head_ang=0.0):
    kw = people.lotus_kw(pose, DX, DY, DS, u)
    kw["lean"] += extra_lean
    kw["head_ang"] += head_ang
    res = people.figure("dima", DX, DY - 6 * breath, DS, expr, **kw)
    svg = res["svg"]
    if abs(squash_y - 1) > 1e-3 or breath:
        sy = squash_y * (1 + .012 * breath)
        svg = f'<g transform="translate({DX} {DY + 80}) scale({1 / sy ** .5:.4f} {sy:.4f}) translate({-DX} {-DY - 80})">{svg}</g>'
    res["svg"] = svg
    return res


def mix_kw(a, b, u, t):
    """Плавный переход между двумя позами лотоса (цели рук и наклон); кисть меняется на середине."""
    A = people.lotus_kw(a[0], DX, DY, DS, a[1])
    B = people.lotus_kw(b[0], DX, DY, DS, b[1])
    u = clamp(u)
    arms = {}
    for k in ("f", "n"):
        pa, pb = A["arms"][k], B["arms"][k]
        arms[k] = ("ik", tuple(pa[1][i] + (pb[1][i] - pa[1][i]) * u for i in (0, 1)), pb[2] if u > .5 else pa[2])
    hands = {k: (B["hands"][k] if u > .5 else A["hands"][k]) for k in ("f", "n")}
    return dict(lean=A["lean"] + (B["lean"] - A["lean"]) * u, head_ang=A["head_ang"] + (B["head_ang"] - A["head_ang"]) * u, arms=arms,
                hands=hands, lotus=A["lotus"])


def lunch_inner(soup=True, k=1.0):
    o = ""
    if soup:
        o += PR.plate_soup(-62 * k, 52 * k, .72 * k, steam=1.0, seed=5)
        o += PR.cutlet_fork(70 * k, -6 * k, .62 * k, rot=-18, seed=6)
    else:
        o += PR.cutlet_fork(0, -18 * k, .9 * k, rot=-14, seed=7)
    return o


# ═════════════════════════════ s15: утро, щелчком прочь ═════════════════════════════
S15_A = 24.1
T_POP15 = T_VOZ + .02
T_RAISE = T_VOZ + .06
T_FLICK = T_VOZ + .34
T_BURST = T_FLICK + .3


def cloud15(t, head):
    """Облако с котлетой: выскакивает пружиной из макушки вверх-вправо; щелчок — отлетает со сжатием, кружится и лопается."""
    hx, hy = head
    bx, by = hx + 150, hy - 230                 # центр дна облака (над рукой, у которой будет щелчок)
    if t < T_POP15:
        return ""
    sx, sy = PR.pop(t, T_POP15)
    rot = 0.0
    dots = (hx + 30 - bx, hy - 110 - by)
    if t >= T_FLICK:
        e = t - T_FLICK
        bx += 430 * e
        by -= 330 * e - 200 * e * e
        rot = 220 * e
        qx, qy = PR.squash(t, T_FLICK, amp=.38, freq=4.0, damp=6.0)
        sx, sy = qy, qx                          # удар сбоку: сплющен по x
        dots = None
        k = PR.unpop(t, T_BURST, .14)
        sx, sy = sx * k, sy * k
        if k <= 0.01:
            return burst(t, bx, by - 110)
    c = PR.cloud(bx, by, 300, 210, sx, sy, seed=15, dots=dots, inner=lunch_inner(False))
    if rot:
        c = f'<g transform="rotate({rot:.1f} {bx:.1f} {by - 110:.1f})">{c}</g>'
    return c


def burst(t, x, y):
    """Лопнуло: короткие штрихи-лучи и три белых клочка, разлетаются и уменьшаются (сплошные, без прозрачности)."""
    e = t - T_BURST - .14
    if e > .45:
        return ""
    o = []
    u = ease_out(clamp(e / .3), 2)
    for i in range(8):
        a = 2 * math.pi * i / 8 + .3
        r0, r1 = 60 + 120 * u, 100 + 150 * u
        if e < .28:
            o.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 7, "#1d2030", seed=1500 + i,
                          taper=.5, wmin=.3))
    for i in range(3):
        a = 2 * math.pi * i / 3 + .9
        r = 70 + 190 * u
        k = max(0.0, 1 - e / .45)
        o.append(shape(ellipse_pts(x + r * math.cos(a), y + r * math.sin(a), 34 * k + 2, 26 * k + 2, 12), "#FFFFFF", "", w=3.0, seed=1510 + i))
    return "".join(o)


def s15(t):
    raise_u = sm(t, T_RAISE, T_FLICK - .06) * (1 - sm(t, T_FLICK + .3, T_FLICK + .62))
    fl = clamp((t - T_FLICK) / .06)
    kw = mix_kw(("sit", 0.0), ("flick", fl), raise_u, t)
    breath = math.sin(2 * math.pi * (t - S15_A) / 2.2)
    # мимика: блаженно с закрытыми глазами → на облаке бровь чуть дрогнула → после щелчка улыбка шире, краем рта
    if t < T_POP15 + .12:
        ex = dict(EX["soft"])
    elif t < T_FLICK + .05:
        ex = dict(EX["soft"], brows="up", smile=.35)
    else:
        ex = dict(EX["bliss"], smile=1.0)
    nod = .05 * bump(t, T_FLICK, .4)
    res = people.figure("dima", DX, DY - 6 * breath, DS, ex, lean=kw["lean"], head_ang=kw["head_ang"] - nod + .02 * math.sin(t * 1.3),
                        arms=kw["arms"], hands=kw["hands"], lotus=kw["lotus"])
    bg, front = room_layer(t, "morning")
    o = [bg, res["svg"], front, cloud15(t, res["head"])]
    # камера: дрейф вбок и лёгкий наезд, мини-тряска на щелчке
    u = sm(t, S15_A, 26.75)
    z = 1.04 + .08 * u + .03 * bump(t, T_FLICK, .3)
    cx = 500 + 80 * u
    cy = 1030 + 10 * u
    dx, dy = shake(t, T_FLICK, 9)
    set_ink(z)
    g = f'<g transform="{lib.cam(cx + dx, cy + dy, z, -.8 + 1.4 * u)}">{"".join(o)}</g>'
    return whip(g, t, t_in=S15_A, dur=.22), "#cfdbe4"


# ═════════════════════════════ s17: призыв, рукописное «кот» ═════════════════════════════
S17_A = 28.1
KOT_T0, KOT_DUR = T_KOT - .04, .38          # дописано к 29.36 (звук «слово дописано»)
KOT_XY, KOT_SIZE = (CAT[0] - 135, CAT[1] - 445), 1.3


def cat_st(t, look=(0.0, 0.0), turn=0.0, extra=None):
    st = dict(look=look, turn=turn, blink=blinks(t, (28.95, 30.62, 31.2)), tail=7 * math.sin(t * 2.1), ear=2 * math.sin(t * 3.3),
              tilt=2.5 * math.sin(t * 1.2), flame_e=1.0 + .25 * math.sin(t * 5), sy=1 + .012 * math.sin(2 * math.pi * t / 2.0))
    if extra:
        st.update(extra)
    return st


def kot_word(t):
    return hand_kot.kot(t, KOT_T0, KOT_DUR, KOT_XY[0], KOT_XY[1], KOT_SIZE)


def s17(t):
    breath = math.sin(2 * math.pi * (t - S17_A) / 2.3)
    nod = .05 * bump(t, T_NAP + .1, .45) + .04 * bump(t, T_KOT + .2, .45)
    ex = dict(EX["friendly"], closed=blinks(t, (28.75, 29.85)), open=.5 + .12 * bump(t, T_KOT + .3, .5))
    res = people.figure("dima", DX, DY - 6 * breath, DS, ex, head_ang=-.02 - nod, **{k: v for k, v in people.lotus_kw("sit", DX, DY, DS).items()
                                                                                    if k != "head_ang"})
    # кот: сначала смотрит на Диму, на «Напиши» поворачивает морду к зрителю; на «кот» ушки торчком, огонёк вспыхивает
    tu = sm(t, T_NAP - .02, T_NAP + .26)
    turn = -.55 * (1 - tu) + .06 * bump(t, T_NAP + .26, .3)
    st = cat_st(t, look=(-.7 * (1 - tu), .05), turn=turn,
                extra=dict(perk=.55 * bump(t, T_KOT, .55), flame_e=1.1 + .7 * bump(t, T_KOT + .1, .5), smile=1.0 if t > T_KOT + .35 else 0.0))
    bg, front = room_layer(t, "evening")
    o = [bg, res["svg"], front]
    set_ink(1.3)
    o.append(blob(ellipse_pts(CAT[0] + 6, CAT[1] - 2, 150, 16, 14), "#4f6c5e"))
    o.append(people.cat_svg(CAT[0], CAT[1], CAT_K, st, t))
    o.append(kot_word(t))
    u = sm(t, S17_A + .1, 30.2)
    z = 1.08 + .2 * u + .03 * bump(t, KOT_T0 + KOT_DUR, .35)
    cx = 690 + 80 * u
    cy = 1080 - 20 * u
    set_ink(z)
    g = f'<g transform="{lib.cam(cx, cy, z, .6 - .9 * u)}">{"".join(o)}</g>'
    return whip(g, t, t_in=S17_A, dur=.22), "#8e98b8"


# ═════════════════════════════ s18: петля к кадру хука ═════════════════════════════
S18_A = 29.8
T_POP18 = T_OBED + .01
# камера: конец s17 → общий план кадра хука (s01, группа E)
CAM17_END = None
HOOK_CAM = (ROOM.CAM_WIDE[0] + 50, ROOM.CAM_WIDE[1], ROOM.CAM_WIDE[2] * .98, 0.0)


def s18(t):
    breath = math.sin(2 * math.pi * (t - S18_A) / 2.6)
    close = sm(t, T_MYS, T_MYS + .28)
    if close < .5:
        ex = dict(EX["friendly"], closed=2 * close, open=.4 * (1 - 2 * close))
    elif t < T_POP18 + .2:
        ex = dict(EX["soft"], smile=.4)
    else:
        ex = dict(EX["side_smile"])
    kw = people.lotus_kw("sit", DX, DY, DS)
    kw["head_ang"] = .03 * close
    res = people.figure("dima", DX, DY - 6 * breath, DS, ex, **kw)
    hx, hy = res["head"]
    # кот: смотрит на зрителя; на «обед» поднимает глаза на облако
    up = sm(t, T_POP18 + .08, T_POP18 + .3)
    st = cat_st(t, look=(-.55 * up, -1.0 * up), turn=-.18 * up, extra=dict(tilt=2.5 * math.sin(t * 1.2) - 7 * up, perk=.4 * bump(t, T_POP18 + .1, .5)))
    bg, front = room_layer(t, "evening")
    o = [bg, res["svg"], front]
    set_ink(1.3)
    o.append(blob(ellipse_pts(CAT[0] + 6, CAT[1] - 2, 150, 16, 14), "#4f6c5e"))
    o.append(people.cat_svg(CAT[0], CAT[1], CAT_K, st, t))
    o.append(kot_word(t))
    if t >= T_POP18:
        sx, sy = PR.pop(t, T_POP18, amp=.38)
        bx, by = hx + 60, hy - 270
        o.append(PR.cloud(bx, by, 380, 250, sx, sy, seed=18, dots=(hx + 10 - bx, hy - 110 - by), inner=lunch_inner(True)))
    # камера: от крупного плана призыва откатывается к общему плану хука; тряска на хлопке облака
    u = sm(t, S18_A + .1, 31.35)
    z0, cx0, cy0, r0 = 1.28, 770.0, 1060.0, -.3
    cxh, cyh, zh, rh = HOOK_CAM
    z = z0 + (zh - z0) * u + .04 * bump(t, T_POP18, .3)
    cx = cx0 + (cxh - cx0) * u
    cy = cy0 + (cyh - cy0) * u
    dx, dy = shake(t, T_POP18, 12)
    set_ink(max(z, 1.0))
    return f'<g transform="{lib.cam(cx + dx, cy + dy, z, r0 + (rh - r0) * u)}">{"".join(o)}</g>', "#8e98b8"


FRAMES = {"s15": s15, "s17": s17, "s18": s18}


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body = FRAMES[sid](t)
    bg = "#d9c9a8"
    if isinstance(body, tuple):
        body, bg = body
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
