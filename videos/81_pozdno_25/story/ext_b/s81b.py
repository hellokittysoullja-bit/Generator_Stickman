"""Рилс 81 «Всё, поздно», группа B: люди, кот, призыв. Время — только из shots.json и voice/words.json (слово по индексу wN).
s05: ночная комната, стена с дверью: «узнал» (w15) Дима садится, дверь проступает; «сколько…тем» (w16–w18) силуэты за стеклом;
     «кто» (w19) вскакивает; «правда» (w20) тянется к ручке, «добился» (w21) берётся.
s06: призыв «Телеграм» модулем scripts/story_cta_tg.py: PRESS = W[25].start + 0.12, T0 = PRESS − 1.10.
s07: кот с кисточкой в зубах рисует на кремовой стене три сценки с Димой: «такие» (w29), «истории» (w30), «Диму» (w32).
s11: крыши трёх домов, основатели: «среднем» (w44) подлёт, «сорок/пять» (w47–w48) кепка и очки, «не/двадцать» (w51–w52) юный мелькает.
s12: софит и спортивная машина, юный позёр: «Двадцатилетние» (w53) софит, «миллионеры» (w54) руки вверх, вспышки.
s17: верстак, лодка, кот гордо задирает нос, «уверен» (w78) кивает, «всё» (w80) спрыгивает к часам.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402,F401

INK = lib.INK
W = json.load(open(os.path.join(STORY, "voice", "words.json")))
W = W if isinstance(W, list) else W["words"]
SH = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return W[i]["start"]


def we(i):
    return W[i]["end"]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def span(sid):
    return SH[sid]["t0"] - .2, SH[sid]["t1"] + .2


def frame_svg(body, cx, cy, s, rot=0.0, bg="#05070f", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def kick(t, t0, amp=1.0, dur=.35):
    """Толчок: быстро вверх и затухание (0 до t0)."""
    if t < t0:
        return 0.0
    u = (t - t0) / dur
    return amp * math.exp(-3.5 * u) * math.sin(math.pi * min(1.0, u * 2.2)) if u < 3 else 0.0


def shake(t, t0, amp=8.0, dur=.3, seed=0):
    if t < t0 or t > t0 + dur:
        return 0.0, 0.0
    e = 1 - (t - t0) / dur
    return amp * e * math.sin(t * 91 + seed), amp * e * math.cos(t * 77 + seed * 2)


def glow_spot(x, y, r, col, op, ry=None):
    g = lib.rad_grad([(0, col, op), (.55, col, op * .45), (1, col, 0)], x, y, r, ry or r)
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{(ry or r):.1f}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


# ═══════════════════════════════ s05: дверь со светом, силуэты, ручка ═══════════════════════════════
S05_DOOR = (R.DOOR81[0], R.DOOR81[1])
S05_K = .6                       # Дима
S05_SIT = (1120.0, 1330.0)       # таз на ковре (лёжа — ось поворота, сидя — таз)
S05_STAND_FEET = 1215.0          # стоит у стены перед дверью


def s05(t):
    lib.dyn_begin()
    T_KNOW, T_HOW, T_THEM, T_WHO, T_TRUE, T_DONE = ws(15), ws(16), ws(18), ws(19), ws(20), ws(21)
    a, b = span("s05")
    n = R.night81(t, "door", glow=1.0)
    dx, dy = S05_DOOR
    # дверь проступает на «узнал»: сначала свет, потом створка
    du = ease_out(clamp((t - (T_KNOW - .12)) / .5))
    sil_u = clamp((t - (T_HOW - .1)) / .3) * (1 - .6 * clamp((t - (T_TRUE + .1)) / .4))
    door = P.glow_door(dx, dy, 1.0, 0.0, t, seed=1, sil=0.0, light=du)
    o = [n["bg"]]
    o.append(f'<g opacity="{du:.3f}">{door}</g>')
    # силуэты за матовым стеклом (закрытая дверь: стекло 0.17…0.83 ширины, 0.1…0.58 высоты)
    x0, x1, y0, y1 = dx - 190, dx + 190, dy - 820, dy
    gx0, gx1, gy0, gy1 = x0 + .17 * 380, x0 + .83 * 380, y0 + .1 * 820, y0 + .58 * 820
    if sil_u > .01 and du > .3:
        cid = lib.clip_rect(gx0 + 4, gy0 + 4, gx1 - gx0 - 8, gy1 - gy0 - 8, 6)
        sl = []
        for i, (kind, x_a, x_b, ph0, kk, d0) in enumerate((("father", gx0 - 60, gx1 + 80, .0, .2, 0.0), ("bob", gx1 + 70, gx0 - 80, .4, .18, .25),
                                                           ("cap", gx0 - 90, gx1 + 60, .7, .21, .55))):
            u = clamp((t - (T_HOW - .15 + d0)) / 1.15)
            fx = lerp(x_a, x_b, u)
            fl = x_b < x_a
            r = people.silhouette81(kind, fx, gy1 + 60, kk, t, phase=(t * 1.6 + ph0) % 1.0, col="#5a3a22", op=.62, blur=5.0, flip=fl)
            sl.append(r["svg"])
        frost = f'<rect x="{gx0:.1f}" y="{gy0:.1f}" width="{gx1 - gx0:.1f}" height="{gy1 - gy0:.1f}" fill="{P.C_FROST}" opacity=".28"/>'
        o.append(f'<g clip-path="url(#{cid})" opacity="{sil_u * du:.3f}">{"".join(sl)}{frost}</g>')
    o.append(n["rug"])
    # телефон на ковре экраном вверх: слабый свет
    o.append(people.mobilnik(820, 1395, .75, 78, seed=8151))
    o.append(glow_spot(820, 1395, 70, "#bfe0ff", .25 * (1 - du * .7)))
    # Дима: лёжа → садится (лицом к двери) → вскакивает → к ручке → берётся
    k = S05_K
    sit_u = ease_io(clamp((t - (T_KNOW - .2)) / .55))
    T_UP = T_WHO - .06
    rise = ease_io(clamp((t - T_UP) / .36))
    hx_ = P.glow_door_handle(dx, dy, 1.0, 0.0)
    if t < T_UP:
        ex = "sigh81" if sit_u < .35 else "wonder81"
        dima = people.dima_floor81(S05_SIT[0], S05_SIT[1], k, t, expr=ex, sit=sit_u, phone=False, glow=0.0)
        hd = dima["head"]
        o.append(dima["svg"])
    else:
        sc = k * people.HEIGHT["dima"]
        stand_hip = (hx_[0] - 215 * sc, people.hip_on_floor(S05_STAND_FEET, k))
        crouch_hip = (S05_SIT[0] + 20 * sc, S05_SIT[1] - 40 * sc)
        hip = lerp2(crouch_hip, stand_hip, rise)
        hip = (hip[0], hip[1] - 40 * sc * math.sin(math.pi * rise))        # прыжок вверх-вперёд
        cr = people.crouch_kw(crouch_hip[0], crouch_hip[1], k)["feet"]
        stf = people.stand_kw(stand_hip[0], stand_hip[1], k)["feet"]
        feet = {}
        for s_ in ("n", "f"):
            # дальняя нога толкает первой, ближняя догоняет
            us = ease_io(clamp((rise - (0 if s_ == "f" else .25)) / .75))
            p_ = lerp2(cr[s_][0], stf[s_][0], us)
            lift = 60 * sc * math.sin(math.pi * us) if 0 < us < 1 else 0.0
            feet[s_] = ((p_[0], p_[1] - lift), lerp(cr[s_][1], stf[s_][1], us))
        reach = ease_io(clamp((t - (T_TRUE - .08)) / .32))
        grip = ease_out(clamp((t - (T_DONE - .05)) / .22))
        rest_w = (hip[0] + 140 * sc, hip[1] - 60 * sc)
        tgt = lerp2(rest_w, (hx_[0] - 10, hx_[1] + 6), reach)
        lean_add = .1 * reach + .05 * grip + .03 * math.sin(t * 2.4)
        ex = dict(people.EXPR["dima"]["wonder81" if reach < .5 else "reach81"])
        arms = {"n": ("ik", tgt, -1), "f": ("ang", .25 - .2 * (1 - rise), .3)}
        hands = {"n": {"dir": (1, .15), "curl": tuple(c * (.35 + .65 * grip) for c in (.6, .65, .7, .72)), "thumb": .2 + .4 * grip},
                 "f": {"curl": (.4, .4, .45, .5), "thumb": .4}}
        fig = people.dima81(hip[0], hip[1], k, ex, "d81_rest", t=t, feet=feet, arms=arms, hands=hands, lean_add=lean_add - .12 * (1 - rise))
        hd = fig["head"]
        o.append(fig["svg"])
    o.append(n["dark"])
    # тёплый свет двери поверх тьмы (свет из щелей и стекла), растёт с силуэтами
    if du > .01:
        gl = du * (.55 + .25 * sil_u + .05 * math.sin(t * 5.3))
        o.append(glow_spot(dx, dy - 470, 330, "#ffd98a", .38 * gl, 520))
        o.append(glow_spot(dx - 60, dy + 120, 420, "#ffcf7a", .22 * gl, 110))
        o.append(f'<g opacity="{.55 * du:.3f}"><rect x="{gx0:.1f}" y="{gy0:.1f}" width="{gx1 - gx0:.1f}" height="{gy1 - gy0:.1f}" '
                 f'fill="#ffe7b0" style="mix-blend-mode:screen" opacity=".35"/></g>')
    # камера: медленный наезд к двери, толчок на «правда»
    u = ease_io(clamp((t - a) / (b - a)))
    cx = lerp(1210, 1350, u)
    cy = lerp(890, 830, u)
    s = lerp(1.24, 1.44, u) * (1 + .045 * kick(t, T_TRUE, 1.0, .4) + .02 * kick(t, T_UP + .1, 1.0, .3))
    sx, sy = shake(t, T_UP + .05, 5, .22)
    del hd
    return frame_svg("".join(o), cx + sx, cy + sy, s, rot=.5 * math.sin(t * .9), bg="#0b0f22")


# ═══════════════════════════════ s06: призыв «Телеграм» ═══════════════════════════════
def s06(t):
    import story_cta_tg as tg
    press = ws(25) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=COMMON)


# ═══════════════════════════════ s07: кот с кисточкой рисует сценки с Димой ═══════════════════════════════
S07_FLOOR = 1350.0
S07_K = 1.45
S07_CAT = (1900.0, 1080.0, 260.0)      # справа налево: кисть щетиной влево, хвост с огоньком не мешает      # где сидит кот у каждой сценки (сценка — вверх-вправо от кончика кисти)
S07_ROT = 198.0                       # кисть щетиной вверх-вправо
S07_W, S07_H = 470.0, 400.0
_INK_F = []


def _ink_filter():
    """Тушь по стене: яркость → сепия, белое уходит в цвет стены (mix-blend multiply у группы)."""
    if not _INK_F or not any(f'id="{_INK_F[0]}"' in d for d in lib.DEFS):
        fid = lib.uid("ink81")
        lib.DEFS.append(f'<filter id="{fid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="'
                        '.27 .53 .09 0 .05  .25 .5 .085 0 .045  .22 .44 .075 0 .04  0 0 0 1 0"/></filter>')
        _INK_F[:] = [fid]
    return _INK_F[0]


def _sketch(i, cx, cy, t):
    """Сценка i (мир, центр cx, cy): 0 — под песочными часами, 1 — лежит с телефоном, 2 — у двери со светом."""
    if i == 0:
        hg = P.giant_hourglass(cx + 10, cy - 150, .42, sand_top=.15, sand_bot=.8, stream=1.0, t=t, chain=260)
        d = people.dima81(cx + 10, cy + 190, .25, "panic81", "d81_cup_up", t=t)
        return hg + d["svg"]
    if i == 1:
        d = people.dima_floor81(cx + 20, cy + 80, .28, t, expr="screen81", glow=.6)
        rug = blob([(cx - 210, cy + 120), (cx + 210, cy + 120), (cx + 230, cy + 170), (cx - 230, cy + 170)], "#b48a6a")
        moon = blob(ellipse_pts(cx + 160, cy - 130, 30, 30, 14), "#e8d7a8") + blob(ellipse_pts(cx + 174, cy - 140, 26, 26, 14), "#f6efe0")
        return moon + rug + d["svg"]
    door = P.glow_door(cx + 90, cy + 175, .44, 0.0, t, seed=3, sil=0.0, light=.8)
    hx_ = P.glow_door_handle(cx + 90, cy + 175, .44, 0.0)
    d = people.dima81(cx - 80, people.hip_on_floor(cy + 180, .25), .25, "reach81", "d81_rest", t=t, feet="stand",
                      arms={"n": ("ik", hx_, -1)}, hands={"n": {"dir": (1, .15), "curl": (.6, .65, .7, .72), "thumb": .5}})
    return door + d["svg"]


def _brush_wipe(cx, cy, u, seed, d=1):
    """Маска мазка: полоса слева направо (d=-1 — справа налево) с рваным краем (u 0…1)."""
    x0 = cx - d * (S07_W / 2 + 20)
    xe = x0 + d * (S07_W + 40) * u
    rs = __import__("numpy").random.RandomState(seed)
    pts = [(x0, cy - S07_H / 2 - 30)]
    for j in range(9):
        yy = cy - S07_H / 2 - 30 + (S07_H + 60) * j / 8
        pts.append((xe + 26 * math.sin(j * 1.7 + seed) + rs.uniform(-10, 10), yy))
    pts.append((x0, cy + S07_H / 2 + 30))
    return pts


def s07(t):
    lib.dyn_begin()
    T0 = SH["s07"]["t0"]
    beats = [ws(29), ws(30), ws(32)]
    o = []
    # кремовая стена, плинтус, пол
    g = lib.lin_grad([(0, "#efe2c6", 1), (1, "#f7eedb", 1)], 0, 0, 0, S07_FLOOR, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-900" width="3600" height="{S07_FLOOR + 900:.0f}" fill="url(#{g})"/>')
    for j in range(14):     # фактура штукатурки
        yy = 120 + j * 92
        o.append(line([(-600, yy), (2600, yy + 14)], 1.6, "#e2d2b0", seed=8700 + j, op=.35))
    o.append(shape(lib.rect_pts(-900, S07_FLOOR - 34, 2700, S07_FLOOR + 6), "#c9a77c", blob(lib.rect_pts(-900, S07_FLOOR - 10, 2700, S07_FLOOR + 6),
                                                                                         "#a8865c"), w=4, seed=8720))
    o.append(f'<rect x="-900" y="{S07_FLOOR + 6:.0f}" width="3600" height="1400" fill="#b98f62"/>')
    for j in range(9):
        o.append(line([(-900 + j * 420, S07_FLOOR + 6), (-1100 + j * 520, 2300)], 2.4, "#9c7650", seed=8730 + j, op=.6))
    # расписание: мазок i идёт [p0, p1]; между мазками кот перебегает к следующему месту
    paint = [(T0 - .24, beats[0] + .18), (beats[1] - .12, beats[1] + .3), (beats[2] - .16, beats[2] + .24)]
    tip = people.cat_brush81(0, 0, S07_K, {}, 0.0, brush_rot=S07_ROT, side=-1)["tip"]
    sk_c = [(x_ + tip[0] - S07_W / 2 + 30, S07_FLOOR + tip[1] - S07_H / 2 - 110) for x_ in S07_CAT]
    fid = _ink_filter()
    for i, ((sx_, sy_), (p0, p1)) in enumerate(zip(sk_c, paint)):
        u = clamp((t - p0) / (p1 - p0))
        if u <= 0:
            continue
        cid = lib.clip_of(_brush_wipe(sx_, sy_, ease_io(u), 870 + i, -1))
        sk = _sketch(i, sx_, sy_, t)
        pop = 1 + .05 * kick(t, p1 - .05, 1.0, .3)
        o.append(f'<g clip-path="url(#{cid})"><g style="mix-blend-mode:multiply" filter="url(#{fid})" '
                 f'transform="translate({sx_:.1f} {sy_:.1f}) scale({pop:.4f}) translate({-sx_:.1f} {-sy_:.1f})">{sk}</g></g>')
    # кот: сидит у своей сценки и машет кистью; между сценками перебегает
    walk = None
    cat_x = S07_CAT[0]
    for i in range(3):
        p0, p1 = paint[i]
        if t < p1 or i == 2:
            if i > 0 and t < p0:
                prev = paint[i - 1][1]
                v = clamp((t - prev) / (p0 - prev))
                cat_x = lerp(S07_CAT[i - 1], S07_CAT[i], ease_io(v))
                walk = (t - prev) / .3
            else:
                cat_x = S07_CAT[i] - 18 * ease_io(clamp((t - p0) / (p1 - p0)))
            break
    painting = walk is None
    sw = (9 * math.sin(t * 2 * math.pi * 3.4) if painting else 0.0)
    st = {"tilt": sw, "flame_e": 1.3 + .7 * sum(kick(t, bt, 1.0, .4) for bt in beats), "tail": 12 * math.sin(t * 3.1), "look": (-.6, -.5)}
    if walk is not None:
        st["walk"] = walk
        st["look"] = (-.8, 0)
    cy_cat = S07_FLOOR - 2 - (16 * abs(math.sin(math.pi * walk)) if walk is not None else 0.0)
    cb = people.cat_brush81(cat_x, cy_cat, S07_K, st, t, brush_rot=S07_ROT + (sw * .6 if painting else -10), side=-1)
    # брызги туши с кисти к рисунку на ударах
    for bt, (sx_, sy_) in zip(beats, sk_c):
        v = (t - bt + .06) / .3
        if 0 < v < 1:
            tx_, ty_ = cb["tip"]
            for j in range(5):
                q = lerp2((tx_, ty_), (sx_ + S07_W * .3 - 40 * j, sy_ + 60 - 30 * j), ease_out(v))
                o.append(blob(ellipse_pts(q[0], q[1], 6 - .8 * j, 5 - .6 * j, 8), "#3a2c22", .8 * (1 - v)))
    fx_, fy_ = cat_x + 170 * S07_K, cy_cat - 300 * S07_K
    o.append(glow_spot(fx_, fy_, 360, "#ffb35a", .24))
    o.append(blob(ellipse_pts(cat_x, S07_FLOOR + 10, 170 * S07_K, 26, 20), "#6e5034", .35))
    o.append(cb["svg"])
    # камера: хлёст на входе (смаз), дрейф вдоль рисунков за котом
    whip = clamp(1 - (t - (T0 - .2)) / .3)
    cx = cat_x - 205 + 520 * whip ** 2
    s_ = 1.1 + .035 * kick(t, beats[1], 1.0, .3) + .035 * kick(t, beats[2], 1.0, .3)
    body = "".join(o)
    if whip > .02:
        bid = lib.uid("wb")
        lib.DEFS.append(f'<filter id="{bid}" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{60 * whip ** 1.5:.1f} 0"/></filter>')
        body = f'<g filter="url(#{bid})">{body}</g>'
    return frame_svg(body, cx, 960, s_, rot=-.6 * math.sin(t * 1.3), bg="#efe2c6")

def frame(sid, t):
    return globals()[sid](t)
