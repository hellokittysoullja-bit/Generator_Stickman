"""Сцена cat рилса 34 «сорвался — гулять так гулять»: планы s05 s16 s17 s18. frame(sid, t) -> SVG 1080×1920
(t — общее время ролика, удары на словах по voice/words.json).

Мир — кухня Димы из сцены kitchen этого рилса (../kitchen/world.py: стена, кафель, столешница у стены, стол, лампа,
календарик, коробка пончиков donut_box) — импортируется как есть, чтобы кухня и коробка совпадали с планами Димы.
Кот — cat.py (кот рилсов 24–32: ЛЕВОЕ от зрителя ухо загнуто, зелёные глаза, по 2 оранжевые полоски на щеках, огонёк
на кончике хвоста-завитка). Миска, жареная рыбка, скелетик, крошки — props.py.
s05 — кот на столешнице у миски с рыбкой, наклон головы на «почему» (8.08);
s16 — закрытая коробка на переднем плане (крышка подпрыгивает и садится на «закрытой» 30.36), кот ест рыбку из миски,
хруст на «доедает» (31.52), облизывается на «рыбку» (32.32), огонёк вспыхивает;
s17 — крупно кот, подмигивает на «Напиши» (33.01) и кивает на «кот» (33.52);
s18 — кот сидит на закрытой коробке, лапа на крышку на «срыва» (35.44), хвост с огоньком качается, медленный отъезд."""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat  # noqa: E402
import lib  # noqa: E402
import props  # noqa: E402
from lib import blob, clamp, ease_io, ease_out, ellipse_pts, f, rad_grad, smooth, spring  # noqa: E402

_spec = importlib.util.spec_from_file_location("kworld34", os.path.join(os.path.dirname(HERE), "kitchen", "world.py"))
KW = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(KW)

CAT_INK = 1.0
_C = {}

# слова
WHY = 8.08            # «почему»
CLOSED = 30.36        # «закрытой»
EATS = 31.52          # «доедает»
FISHW = 32.32         # «рыбку»
WRITE = 33.013        # «Напиши»
KOT = 33.52           # «кот,»
SRYV = 35.44          # «срыва»


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.18):
    u = (t - tb) / dur
    return min(1.0, 1.3 * math.sin(math.pi * u)) if 0 < u < 1 else 0.0


def flick_at(t, c, amp=-14):
    e = t - c
    return amp * math.exp(-e * 9) * math.sin(e * 34) if 0 <= e < 0.55 else 0.0


def kitchen(t, cal_marks=1.0):
    return KW.kitchen_bg(t, cal=KW.calendar([cal_marks] * 7))


def flame_glow(x, y, s, d, k=1.0, r=260):
    fx, fy = cat.flame_world(x, y, s, d.get("tail", 0.0))
    fl = (0.85 + 0.15 * math.sin(d["_t"] * 13) * math.sin(d["_t"] * 7.3)) * k
    g = rad_grad([(0, "#ffb050", min(.9, .38 * fl)), (1, "#ffb050", 0)], fx, fy, r, r)
    return f'<rect x="{f(fx - r - 20)}" y="{f(fy - r - 20)}" width="{f(2 * r + 40)}" height="{f(2 * r + 40)}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def cat_svg(x, y, s, t, **d):
    """Кот с тушью постоянной толщины (как в крупных планах рилсов 29–32)."""
    keep = lib.INK_K[0]
    lib.INK_K[0] = CAT_INK
    out = cat.draw(x, y, s, t, **d)
    lib.INK_K[0] = keep
    return out


def fish_in_bowl(bx, by, bk, t, bites=(), seed=0):
    """Рыбка лежит в миске наискосок, хвост торчит над ободом справа."""
    return props.fish(bx + 4 * bk, by - (props.BH - 4) * bk, 0.62 * bk, -8, bites=bites, tail=4 * math.sin(t * 2.2), seed=seed)


# ─────────────────────────────── s05: кот на столешнице у миски
S05 = dict(x=560, y=1022, s=0.9, bowl=(418, 1030, 0.6))


def pose05(t):
    e = t - WHY
    tilt = 1.5 * math.sin(t * 1.7)
    if e > -0.12:
        pre = 2.5 * math.sin(math.pi * clamp((e + 0.12) / 0.12)) if e < 0 else 0.0
        tilt += pre - 13 * spring(max(e, 0), 2.2, 4.5)
    blink = max(blink_at(t, 7.52), blink_at(t, 8.86))
    look = (0.12 * math.sin(t * 0.9), -0.1 + 0.08 * math.sin(t * 1.3))
    if e > 0:
        look = (look[0] - 0.25 * smooth(0, 0.2, e), look[1] - 0.15 * smooth(0, 0.2, e))
    flick = flick_at(t, WHY + 0.04) + flick_at(t, 7.62, -10)
    tail = 7 * math.sin(t * 2.1) + 3 * math.sin(t * 3.7 + 1)
    if e > 0:
        tail += 9 * math.exp(-e * 3) * math.sin(e * 12)
    fk = 1.3 + (0.35 * math.exp(-e * 4) * math.sin(min(e * 8, math.pi)) if e > 0 else 0.0)
    return dict(look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, flame_k=fk)


def frame05(t):
    sc0 = 2.6
    u = clamp((t - 7.4) / 1.95)
    sc = sc0 + 0.16 * (0.35 * u + 0.65 * ease_io(u))
    e = t - WHY
    if e > 0:
        sc *= 1 + 0.03 * math.exp(-e * 7) * math.sin(min(e * 14, math.pi))
    cx, cy = 566 + 10 * u, 930 - 14 * u
    rot = -0.8 + 1.1 * u
    if "bg05" not in _C:
        set_ink(sc0)
        _C["bg05"] = kitchen(7.4)
        lib.static_done()
    lib.dyn_begin()
    set_ink(sc0)
    d = pose05(t)
    hop = -9 * math.sin(math.pi * clamp(e / 0.22)) if 0 < e < 0.22 else 0.0
    P = S05
    bx, by, bk = P["bowl"]
    w = [_C["bg05"]]
    d["_t"] = t
    w.append(flame_glow(P["x"], P["y"] + hop, P["s"], d, 1 + (0.6 * math.exp(-e * 3) if e > 0 else 0), 220))
    w.append(blob(ellipse_pts(P["x"] + 26, P["y"] + 4, 150, 12, 16), "#3a1a08", .3, lib.blur(5)))
    w.append(KW.table_back() + KW.table_top())
    fr = [props.bowl(bx, by, bk, fish_in_bowl(bx, by, bk, t, seed=500), seed=520)]
    dd = {k: v for k, v in d.items() if not k.startswith("_")}
    fr.append(cat_svg(P["x"], P["y"] + hop, P["s"], t, shadow=False, **dd))
    return KW.compose("".join(w), (cx, cy, sc, rot), t, front="".join(fr))


# ─────────────────────────────── s16: коробка закрыта, кот ест рыбку
S16 = dict(x=1000, y=1102, s=0.85, box=(1240, 1150, 1.05))
BK16 = 0.74                                              # масштаб миски
B16 = (1000 + (688 - cat.CX) * 0.85, 1116)              # низ миски: слева от кота, чуть впереди
LEAN16 = (-62.0, 104.0, -18.0)                           # голова в миску: вниз-влево с поворотом
BEND16 = -4.0


def pose16(t):
    d = dict(look=(0.0, 0.25), blink=0.0, tilt=0.0, flick=0.0, lean=0.0, chew=0.0, tongue=0.0, happy=0.0, flame_k=1.3)
    d["tail"] = 6 * math.sin(t * 2.0) + 3 * math.sin(t * 3.4 + 1)
    # 29.8–30.9: морда в миске, жуёт (глаза-дуги); 30.9–31.35 поднимает голову, смотрит на рыбку;
    # 31.35 замах вниз — 31.52 укус (хруст), жуёт; 32.1 поднимает голову, 32.32 облизывается, огонёк вспыхивает
    lean = 0.92
    lean -= 0.42 * smooth(30.85, 31.15, t)
    lean += 0.5 * smooth(31.32, EATS - 0.02, t)
    lean -= 0.12 * math.exp(-max(0, t - EATS) * 9) * math.sin(max(0, t - EATS) * 30) * (t > EATS)
    lean -= 0.88 * smooth(31.98, 32.24, t)
    chew = 0.0
    if t < 30.9:
        chew = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 3.2)
        d["happy"] = 1.0
    elif t < EATS - 0.1:
        chew = 0.25 * smooth(31.3, 31.42, t)
        d["look"] = (0.0, 0.85)
        d["blink"] = blink_at(t, 30.93)
    elif t < 32.0:
        e = t - EATS
        chew = 0.9 * math.exp(-e * 2) * (0.5 + 0.5 * math.cos(e * 2 * math.pi * 3.6)) + (1 if e < 0.06 else 0)
        d["happy"] = 1.0
    else:
        d["happy"] = 1.0
        e = t - FISHW
        if -0.1 < e < 0.62:
            d["tongue"] = clamp((e + 0.1) / 0.62)
    d["lean"] = max(0.0, lean)
    d["chew"] = min(1.0, chew)
    d["tilt"] = 2.0 * math.sin(t * 1.6) + (-5 * smooth(32.1, 32.3, t) * (1 - smooth(32.9, 33.1, t)))
    d["flick"] = flick_at(t, 30.40, -12) + flick_at(t, EATS + 0.02, -14)
    e = t - FISHW
    d["flame_k"] = 1.3 + (0.6 * math.exp(-e * 2.4) * min(1, e * 10) if e > 0 else 0.0)
    if e > 0:
        d["tail"] += 8 * math.exp(-e * 3) * math.sin(e * 13)
    return d


def lid16(t):
    """Крышка: подпрыгивает перед «закрытой» и плотно садится на слове, мелкий отскок."""
    e = t - CLOSED
    if -0.26 < e < 0:
        return 15 * math.sin(math.pi * (e + 0.26) / 0.26) ** 0.8
    if 0 <= e < 0.3:
        return 3.5 * math.exp(-e * 12) * abs(math.sin(e * 26))
    return 0.0


def frame16(t):
    u = clamp((t - 29.8) / 3.35)
    sc0 = 2.12
    sc = sc0 + 0.06 * ease_io(u)
    cx = 1030 + 40 * (0.3 * u + 0.7 * ease_io(u))
    cy = 1020 - 6 * u
    for t0, amp in ((CLOSED, .02), (EATS, .028), (FISHW, .02)):
        e = t - t0
        if e > 0:
            k = math.exp(-e * 8)
            sc *= 1 + amp * k * math.sin(min(e * 12, math.pi))
            cy += 4 * k * math.sin(e * 45) * (t0 == EATS)
    rot = 0.6 - 1.0 * u
    if "bg16" not in _C:
        set_ink(sc0)
        _C["bg16"] = kitchen(29.8) + KW.table_back() + KW.table_top()
        lib.static_done()
    lib.dyn_begin()
    set_ink(sc0)
    P = S16
    d = pose16(t)
    d["_t"] = t
    x, y, s = P["x"], P["y"], P["s"]
    bx, by = B16
    bk = BK16
    d["lean_v"] = LEAN16
    d["bend"] = BEND16 * min(1.0, d["lean"])
    bites = []
    if t >= EATS:
        bites = [(-30, -54, 26), (-2, -56, 22)]
    w = [_C["bg16"]]
    e = t - FISHW
    w.append(flame_glow(x, y, s, d, 1 + (0.8 * math.exp(-e * 2.5) if e > 0 else 0), 230))
    bg, w = w, []
    dd = {k: v for k, v in d.items() if not k.startswith("_")}
    w.append(blob(ellipse_pts(x + 30, y + 4, 140, 11, 16), "#3a1a08", .28, lib.blur(4)))
    w.append(cat_svg(x, y, s, t, shadow=False, layer="body", **dd))
    w.append(props.bowl_back(bx, by, bk, seed=620))
    w.append(fish_in_bowl(bx, by, bk, t, bites=bites, seed=600))
    w.append(cat_svg(x, y, s, t, shadow=False, layer="head", **dd))
    w.append(props.bowl_front(bx, by, bk, seed=620))
    w.append(props.crumbs(bx - 10 * bk, by - (props.BH + 6) * bk, 0.9, t - EATS, seed=640))
    # коробка на переднем плане
    lx, ly, lk = P["box"]
    lj = lid16(t)
    w.append(KW.donut_box(lx, ly, lk, lid=0.0, lid_jump=lj, glow=clamp(lj / 10) * .8, t=t))
    ec = t - CLOSED
    if 0 <= ec < 0.6:
        w.append(props.sugar_puff(lx, ly - (KW.BOX_HF + 2) * lk, lk * .9, ec / 0.6, seed=660))
    return KW.compose("".join(bg), (cx, cy, sc, rot), t, front="".join(w))


# ─────────────────────────────── s17: кот крупно, подмигивает и кивает
S17 = dict(x=1150, y=1102, s=0.85)


def frame17(t):
    P = S17
    x, y, s = P["x"], P["y"], P["s"]
    u = clamp((t - 32.75) / 2.25)
    hc = cat.to_world((836, 1080), x, y, s)
    sc0 = 3.9
    sc = sc0 + 0.25 * (0.4 * u + 0.6 * ease_io(u))
    cx = hc[0] + 48 - 8 * u
    cy = hc[1] + 62 - 8 * u
    rot = -0.8 + 1.4 * u
    ek = t - KOT
    if ek > 0:
        sc *= 1 + 0.02 * math.exp(-ek * 7) * math.sin(min(ek * 12, math.pi))
    if "bg17" not in _C:
        set_ink(1.6)
        bg = kitchen(32.75) + KW.table_back() + KW.table_top()
        bg += props.bowl(x - 260, 1132, 0.95, props.bones(x - 266, 1132 - (props.BH - 4) * .95, .55, -8, seed=700), seed=720)
        bg += KW.donut_box(x + 330, 1148, 1.05, lid=0.0)
        _C["bg17"] = f'<g {lib.blur(7)}>{bg}</g>'
        lib.static_done()
    lib.dyn_begin()
    set_ink(1.6)
    # подмигивание правым (от зрителя) глазом
    wk = smooth(WRITE + 0.04, WRITE + 0.16, t) * (1 - smooth(33.70, 33.84, t))
    bb = max(blink_at(t, 32.86, .16), blink_at(t, 34.55, .18))
    blink = (bb, max(bb, wk))
    tilt = -6 * smooth(WRITE - 0.06, WRITE + 0.14, t) * (1 - smooth(34.0, 34.4, t)) + 1.2 * math.sin(t * 1.3)
    nod = 18 * math.sin(math.pi * clamp((t - KOT + 0.04) / 0.34)) + 6 * math.sin(math.pi * clamp((t - KOT - 0.3) / 0.28))
    flick = flick_at(t, 32.8, -10) + flick_at(t, KOT + 0.05, -9)
    tail = 6 * math.sin(t * 2.4) - 2 + 4 * math.sin(t * 3.1 + 1)
    look = (0.05 * math.sin(t * .8), -0.08)
    d = dict(look=look, blink=blink, tilt=tilt, nod=nod, flick=flick, tail=tail, flame_k=1.3 + 0.08 * math.sin(t * 5), _t=t)
    w = [_C["bg17"]]
    w.append(flame_glow(x, y, s, d, 1.2, 200))
    dd = {k: v for k, v in d.items() if not k.startswith("_")}
    return KW.compose("".join(w), (cx, cy, sc, rot), t, cone=False, front=cat_svg(x, y, s, t, shadow=True, **dd))


# ─────────────────────────────── s18: кот на закрытой коробке, лапа на крышку
S18 = dict(box=(1150, 1150, 1.05), s=0.85)


def frame18(t):
    bx, by, bk = S18["box"]
    s = S18["s"]
    # кот сидит на крышке (середина её верха)
    x = bx - 10
    y = by - (KW.BOX_HF + KW.BOX_D * 0.42) * bk
    u = clamp((t - 34.6) / 2.7)
    sc0 = 2.25
    sc = sc0 - 0.5 * (0.25 * u + 0.75 * ease_io(u))
    cx = x + 30 - 20 * u
    cy = y - 150 + 40 * u
    rot = 0.8 - 1.2 * u
    e = t - SRYV
    if e > 0:
        sc *= 1 + 0.018 * math.exp(-e * 8) * math.sin(min(e * 12, math.pi))
    if "bg18" not in _C:
        set_ink(1.9)
        bg = kitchen(34.6) + KW.table_back() + KW.table_top()
        bg += props.bowl(bx - 290, 1136, 0.9, props.bones(bx - 296, 1136 - (props.BH - 4) * .9, .52, -8, seed=800), seed=820)
        _C["bg18"] = bg
        lib.static_done()
    lib.dyn_begin()
    set_ink(1.9)
    # лапа: замах вверх и хлоп по крышке на «срыва», держит
    rest = cat.PAW_REST
    tgt = (682, 1290)
    lift = (730, 1188)
    a = smooth(SRYV - 0.42, SRYV - 0.16, t)
    b = smooth(SRYV - 0.16, SRYV, t)
    px = rest[0] + (lift[0] - rest[0]) * a + (tgt[0] - lift[0]) * b
    py = rest[1] + (lift[1] - rest[1]) * a + (tgt[1] - lift[1]) * b
    press = math.exp(-max(0, e) * 10) * abs(math.sin(max(0, e) * 30)) if e > 0 else 0.0
    tilt = 1.6 * math.sin(t * 1.2) - 4 * smooth(SRYV - 0.1, SRYV + 0.2, t) * (1 - smooth(36.3, 36.8, t))
    blink = max(blink_at(t, 34.95), blink_at(t, 36.55))
    look = (0.08 * math.sin(t * 0.8) - 0.5 * smooth(SRYV - 0.45, SRYV - 0.2, t) * (1 - smooth(SRYV + 0.15, SRYV + 0.4, t)),
            -0.05 + 0.6 * smooth(SRYV - 0.45, SRYV - 0.2, t) * (1 - smooth(SRYV + 0.15, SRYV + 0.4, t)))
    tail = 6 + 9 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1)
    flick = flick_at(t, SRYV + 0.05, -12) + flick_at(t, 36.2, -9)
    d = dict(look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw=(px, py), press=press, flame_k=1.3, mitt=a > 0.3, _t=t)
    w = [_C["bg18"], flame_glow(x, y, s, d, 1.2, 230)]
    bg, w = w, [KW.donut_box(bx, by, bk, lid=0.0)]
    w.append(blob(ellipse_pts(x + 20, y + 4, 120, 10, 16), "#3a1a08", .3, lib.blur(4)))
    dd = {k: v for k, v in d.items() if not k.startswith("_")}
    w.append(cat_svg(x, y, s, t, shadow=False, **dd))
    return KW.compose("".join(bg), (cx, cy, sc, rot), t, front="".join(w))


def frame(sid, t):
    if "cat" not in _C:
        keep = lib.INK_K[0]
        lib.INK_K[0] = CAT_INK
        cat.static_parts()
        lib.INK_K[0] = keep
        _C["cat"] = 1
        lib.static_done()
    return {"s05": frame05, "s16": frame16, "s17": frame17, "s18": frame18}[sid](t)
