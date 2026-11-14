"""Сцена cat рилса 38 «дело кажется бесконечным»: планы s04 s16 s17 s18. frame(sid, t) -> SVG 1080×1920
(t — общее время ролика, удары на словах по voice/words.json).

Мир — угол комнаты Димы в ремонте с окном (world.py). Кот — cat.py (кот рилсов 24–34: ЛЕВОЕ от зрителя ухо загнуто,
зелёные глаза, по 2 оранжевые полоски на щеках, огонёк на кончике хвоста-завитка).
s04 — кот на недоделанном подоконнике в плёнке (шпатель, банка), смотрит в камеру, наклон головы на «почему» (7.04);
s16 — готовый белый подоконник с горшком, кот гордо выпячивает грудь на «гордо» (31.20), огонёк вспыхивает на
      «подоконнике» (32.40), камера проезжает вбок;
s17 — крупно кот, подмигивает на «Напиши» (33.44), кивает на «кот» (33.92);
s18 — кот рядом с длинным зачёркнутым списком; на «дело» (35.60) кладёт лапу на последнюю зачёркнутую строку, медленный
      отъезд до свитка на полу и банки с валиком."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat  # noqa: E402
import lib  # noqa: E402
import world as Wd  # noqa: E402
from lib import blob, clamp, ease_io, ellipse_pts, f, rad_grad, smooth, spring  # noqa: E402

CAT_INK = 1.0
_C = {}
_W = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in _W:
        if w["word"].strip(".,?!:«»").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


WHY = wt("почему")              # 7.04
DELO1 = wt("дело")              # 7.92
GORDO = wt("гордо")             # 31.20
SILL_W = wt("подоконнике")      # 32.40
WRITE = wt("Напиши")            # 33.44
KOT = wt("кот", 33)             # 33.92
DELO = wt("дело", 30)           # 35.60
KONCA = wt("конца", 30)         # 36.00


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.18):
    u = (t - tb) / dur
    return min(1.0, 1.3 * math.sin(math.pi * u)) if 0 < u < 1 else 0.0


def flick_at(t, c, amp=-14):
    e = t - c
    return amp * math.exp(-e * 9) * math.sin(e * 34) if 0 <= e < 0.55 else 0.0


def kick(t, t0, k=7.0, fr=14.0):
    e = t - t0
    return math.exp(-e * k) * math.sin(min(e * fr, math.pi)) if e > 0 else 0.0


def flame_glow(x, y, s, d, k=1.0, r=260):
    fx, fy = cat.flame_world(x, y, s, d.get("tail", 0.0))
    fl = (0.85 + 0.15 * math.sin(d["_t"] * 13) * math.sin(d["_t"] * 7.3)) * k
    g = rad_grad([(0, "#ffb050", min(.9, .38 * fl)), (1, "#ffb050", 0)], fx, fy, r, r)
    return f'<rect x="{f(fx - r - 20)}" y="{f(fy - r - 20)}" width="{f(2 * r + 40)}" height="{f(2 * r + 40)}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def cat_svg(x, y, s, t, **d):
    keep = lib.INK_K[0]
    lib.INK_K[0] = CAT_INK
    out = cat.draw(x, y, s, t, **d)
    lib.INK_K[0] = keep
    return out


def cat_shadow(x, y, w=130):
    return blob(ellipse_pts(x + 24, y + 2, w, 10, 16), "#2a1a10", .3, lib.blur(4))


def bg(key, state, t0, extra=""):
    if key not in _C:
        _C[key] = Wd.room_bg(t0, state) + extra
        lib.static_done()
    return _C[key]


# ─────────────────────────────── s04: кот на подоконнике в плёнке
S04 = dict(x=870, s=0.86)


def frame04(t):
    P = S04
    x, y, s = P["x"], Wd.CAT_Y, P["s"]
    u = clamp((t - 6.35) / 2.05)
    sc0 = 2.45
    sc = sc0 + 0.22 * (0.4 * u + 0.6 * ease_io(u)) + 0.025 * kick(t, WHY, 7, 12)
    cx = x - 20 + 18 * u
    cy = 862 - 10 * u
    rot = -1.0 + 1.4 * u
    set_ink(sc0)
    b = bg("bg04", "reno", 6.4, Wd.work_lamp(1180, 420, 6.4))
    lib.dyn_begin()
    set_ink(sc0)
    sp = Wd.paint_can(712, 1034, 0.86) + Wd.spatula(1010, 1046, 1.05, -14)
    e = t - WHY
    tilt = 1.5 * math.sin(t * 1.7)
    if e > -0.12:
        pre = 2.5 * math.sin(math.pi * clamp((e + 0.12) / 0.12)) if e < 0 else 0.0
        tilt += pre - 13 * spring(max(e, 0), 2.2, 4.5)
    blink = max(blink_at(t, 6.62), blink_at(t, 7.9))
    look = (0.1 * math.sin(t * 0.9), -0.12 + 0.06 * math.sin(t * 1.3))
    if e > 0:
        look = (look[0] - 0.22 * smooth(0, 0.2, e), look[1] - 0.12 * smooth(0, 0.2, e))
    flick = flick_at(t, WHY + 0.04) + flick_at(t, 6.5, -10)
    tail = 7 * math.sin(t * 2.1) + 3 * math.sin(t * 3.7 + 1)
    if e > 0:
        tail += 9 * math.exp(-e * 3) * math.sin(e * 12)
    fk = 1.3 + (0.35 * math.exp(-e * 4) * math.sin(min(e * 8, math.pi)) if e > 0 else 0.0) + 0.08 * math.sin(t * 6.3)
    d = dict(look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, flame_k=fk, _t=t)
    hop = -9 * math.sin(math.pi * clamp(e / 0.22)) if 0 < e < 0.22 else 0.0
    w = [b, flame_glow(x, y + hop, s, d, 1 + (0.5 * math.exp(-e * 3) if e > 0 else 0), 220)]
    fr = [Wd.film(t), sp, cat_shadow(x, y)]
    dd = {k: v for k, v in d.items() if not k.startswith("_")}
    fr.append(cat_svg(x, y + hop, s, t, shadow=False, **dd))
    return Wd.compose("".join(w), (cx, cy, sc, rot), front="".join(fr), lamp_xy=(1180, 420))


# ─────────────────────────────── s16: готовый подоконник, кот гордо
S16 = dict(x=720, s=0.86)


def pose16(t):
    e = t - GORDO
    puff = smooth(GORDO - 0.12, GORDO + 0.16, t)
    pk = kick(t, GORDO, 6, 12)
    d = dict(look=(0.08 * math.sin(t * .8), -0.1), tilt=1.6 * math.sin(t * 1.4), flick=flick_at(t, GORDO + 0.05, -12) + flick_at(t, 30.7, -9))
    d["breath"] = (0.5 + 0.5 * math.sin(t * 2 * math.pi / 2.6)) + 3.6 * puff + 1.2 * pk
    d["nod"] = -12 * puff - 4 * pk
    d["tilt"] += 4 * puff
    d["happy"] = 1.0 if GORDO + 0.08 < t < 32.25 else 0.0
    d["blink"] = max(blink_at(t, 30.62), blink_at(t, 32.9))
    d["bend"] = -2.5 * puff
    ef = t - SILL_W
    d["flame_k"] = 1.3 + 0.07 * math.sin(t * 6) + (0.75 * math.exp(-ef * 1.6) * min(1, ef * 8) if ef > 0 else 0.0)
    d["tail"] = 6 * math.sin(t * 2.0) + 3 * math.sin(t * 3.4 + 1) + (10 * math.exp(-ef * 3) * math.sin(ef * 12) if ef > 0 else 0.0)
    d["_t"] = t
    d["_ef"] = ef
    return d


def frame16(t):
    P = S16
    x, y, s = P["x"], Wd.CAT_Y, P["s"]
    u = clamp((t - 30.4) / 3.1)
    sc0 = 2.2
    sc = sc0 + 0.06 * ease_io(u) + 0.02 * kick(t, GORDO, 7, 12) + 0.025 * kick(t, SILL_W, 6, 12)
    cx = x - 120 + 200 * (0.3 * u + 0.7 * ease_io(u))
    cy = 880 - 8 * u
    rot = 0.7 - 1.2 * u
    set_ink(sc0)
    b = bg("bg16", "done", 30.4, Wd.todo_list(30.4, None) + Wd.plant(480, 1040, 1.05) + Wd.work_lamp(1180, 420, 30.4))
    lib.dyn_begin()
    set_ink(sc0)
    d = pose16(t)
    ef = d["_ef"]
    w = [b, flame_glow(x, y, s, d, 1.1 + (1.1 * math.exp(-ef * 2) if ef > 0 else 0), 240)]
    dd = {k: v for k, v in d.items() if not k.startswith("_")}
    fr = [cat_shadow(x, y), cat_svg(x, y, s, t, shadow=False, **dd)]
    if ef > 0:     # искры от вспышки огонька
        fx, fy = cat.flame_world(x, y, s, d["tail"])
        for k in range(7):
            a = -math.pi / 2 + (k - 3) * 0.42
            r = 40 + 170 * ease_io(clamp(ef / 0.7))
            op = 1 - clamp((ef - 0.25) / 0.5)
            if op > 0.02:
                px, py = fx + r * math.cos(a), fy - 30 + r * math.sin(a) + 60 * ef * ef
                fr.append(sparkle(px, py, 9 * (1 - 0.5 * clamp(ef / 0.75)), op, k))
    return Wd.compose("".join(w), (cx, cy, sc, rot), front="".join(fr), lamp_xy=(1180, 420))


def sparkle(x, y, r, op, k):
    pts = []
    for i in range(8):
        a = i * math.pi / 4
        rr = r if i % 2 == 0 else r * .38
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return f'<g opacity="{op:.3f}">' + lib.shape(pts, "#ffe08a", "", w=2.2, seed=1500 + k, ink_color="#a8501a") + "</g>"


# ─────────────────────────────── s17: кот крупно, подмигивает и кивает
S17 = dict(x=720, s=0.86)


def frame17(t):
    P = S17
    x, y, s = P["x"], Wd.CAT_Y, P["s"]
    u = clamp((t - 33.1) / 2.1)
    hc = cat.to_world((836, 1080), x, y, s)
    sc0 = 3.85
    sc = sc0 + 0.25 * (0.4 * u + 0.6 * ease_io(u))
    cx = hc[0] + 52 - 8 * u
    cy = hc[1] + 66 - 8 * u
    rot = -0.8 + 1.4 * u
    sc *= 1 + 0.02 * kick(t, KOT, 7, 12)
    if "bg17" not in _C:
        set_ink(1.6)
        bgs = Wd.room_bg(33.1, "done") + Wd.todo_list(33.1, None) + Wd.plant(480, 1040, 1.05) + Wd.work_lamp(1180, 420, 33.1)
        _C["bg17"] = f'<g {lib.blur(7)}>{bgs}</g>'
        lib.static_done()
    lib.dyn_begin()
    set_ink(1.6)
    wk = smooth(WRITE + 0.04, WRITE + 0.16, t) * (1 - smooth(WRITE + 0.62, WRITE + 0.76, t))
    bb = max(blink_at(t, 33.2, .16), blink_at(t, 34.75, .18))
    blink = (bb, max(bb, wk))
    tilt = -6 * smooth(WRITE - 0.06, WRITE + 0.14, t) * (1 - smooth(34.4, 34.8, t)) + 1.2 * math.sin(t * 1.3)
    nod = 18 * math.sin(math.pi * clamp((t - KOT + 0.04) / 0.34)) + 6 * math.sin(math.pi * clamp((t - KOT - 0.3) / 0.28))
    flick = flick_at(t, 33.15, -10) + flick_at(t, KOT + 0.05, -9)
    tail = 6 * math.sin(t * 2.4) - 2 + 4 * math.sin(t * 3.1 + 1)
    look = (0.05 * math.sin(t * .8), -0.08)
    d = dict(look=look, blink=blink, tilt=tilt, nod=nod, flick=flick, tail=tail, flame_k=1.3 + 0.08 * math.sin(t * 5), _t=t)
    w = [_C["bg17"], flame_glow(x, y, s, d, 1.2, 200)]
    dd = {k: v for k, v in d.items() if not k.startswith("_")}
    return Wd.compose("".join(w), (cx, cy, sc, rot), front=cat_svg(x, y, s, t, shadow=True, **dd), lamp_xy=(1180, 420))


# ─────────────────────────────── s18: кот у списка, лапа на последнюю строку
S18 = dict(x=428, s=0.86)
N_LINES = len(Wd.LIST_LINES) + 3


def frame18(t):
    P = S18
    x, y, s = P["x"], Wd.CAT_Y, P["s"]
    u = clamp((t - 34.8) / 2.0)
    sc0 = 2.05
    sc = sc0 - 0.62 * (0.25 * u + 0.75 * ease_io(u))
    cx = x - 105 + 10 * u
    cy = 850 + 150 * ease_io(u)
    rot = 0.8 - 1.2 * u
    sc *= 1 + 0.018 * kick(t, DELO, 8, 12)
    set_ink(sc0)
    b = bg("bg18", "done", 34.8, Wd.plant(1000, 1040, 1.05) + Wd.work_lamp(1180, 420, 34.8))
    lib.dyn_begin()
    set_ink(sc0)
    can = Wd.paint_can(400, Wd.FLOOR + 36, 1.05, roller=True)
    # точка последней зачёркнутой строки (правый конец) — во внутренних координатах кота
    tx, ty = Wd.LIST_X1 - 8, Wd.list_line_y(N_LINES - 1) - 8
    tgt = cat.to_int((tx, ty), x, y, s)
    rest = cat.PAW_REST
    lift = (tgt[0] + 40, tgt[1] - 70)
    a = smooth(DELO - 0.42, DELO - 0.16, t)
    bb = smooth(DELO - 0.16, DELO, t)
    px = rest[0] + (lift[0] - rest[0]) * a + (tgt[0] - lift[0]) * bb
    py = rest[1] + (lift[1] - rest[1]) * a + (tgt[1] - lift[1]) * bb
    e = t - DELO
    press = math.exp(-max(0, e) * 10) * abs(math.sin(max(0, e) * 30)) if e > 0 else 0.0
    tilt = 1.6 * math.sin(t * 1.2) - 4 * smooth(DELO - 0.1, DELO + 0.2, t)
    blink = max(blink_at(t, 35.05), blink_at(t, 36.45))
    gl = smooth(DELO - 0.45, DELO - 0.2, t) * (1 - smooth(DELO + 0.15, DELO + 0.4, t))
    look = (0.08 * math.sin(t * 0.8) - 0.6 * gl, -0.05 + 0.25 * gl)
    tail = 6 + 9 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1)
    flick = flick_at(t, DELO + 0.05, -12) + flick_at(t, 36.2, -9)
    d = dict(look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, paw=(px, py), press=press, flame_k=1.3 + 0.07 * math.sin(t * 6),
             mitt=a > 0.3, _t=t)
    # последнее зачёркивание дорисовано к удару лапы (ещё видно, как красная линия довершается под лапой)
    lst = Wd.todo_list(t, strike_t=DELO - 0.12)
    w = [b, lst, can, flame_glow(x, y, s, d, 1.2, 230)]
    dd = {k: v for k, v in d.items() if not k.startswith("_")}
    fr = [cat_shadow(x, y), cat_svg(x, y, s, t, shadow=False, **dd)]
    if e > 0:     # штрихи «тап» у лапы
        pw = cat.to_world((px, py), x, y, s)
        for k in range(3):
            a0 = math.pi * (0.75 + 0.25 * k)
            r0, r1 = 34 + 60 * clamp(e / 0.25), 52 + 70 * clamp(e / 0.25)
            op = 1 - clamp((e - 0.15) / 0.2)
            if op > 0.02:
                fr.append(lib.line([(pw[0] + r0 * math.cos(a0), pw[1] + r0 * math.sin(a0)), (pw[0] + r1 * math.cos(a0), pw[1] + r1 * math.sin(a0))],
                                   6, lib.INK, taper=.3, wmin=.4, seed=1600 + k, op=op))
    return Wd.compose("".join(w), (cx, cy, sc, rot), front="".join(fr), lamp_xy=(1180, 420))


def frame(sid, t):
    if "cat" not in _C:
        keep = lib.INK_K[0]
        lib.INK_K[0] = CAT_INK
        cat.static_parts()
        lib.INK_K[0] = keep
        _C["cat"] = 1
        lib.static_done()
    return {"s04": frame04, "s16": frame16, "s17": frame17, "s18": frame18}[sid](t)
