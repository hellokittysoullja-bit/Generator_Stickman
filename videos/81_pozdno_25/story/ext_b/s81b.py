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

# ═══════════════════════════════ s11: основатели на крышах ═══════════════════════════════
S11_BOT = 2900.0
# крыши трёх самых высоких домов (цвета — те же дома s10: seed 1, 3, 4) и низкий дом юного справа
S11_ROOF = [(300.0, 1140.0, 3, "glasses"), (545.0, 1010.0, 1, "cap"), (790.0, 1180.0, 4, "bald")]
S11_BK = .8
S11_YOUNG = (690.0, 1300.0)
S11_K = .3


def _roof_bld(x, y_roof, seed, sway=0.0, k=1.0):
    fl = (S11_BOT - y_roof - 22 * k) / (110 * k)
    return P.sprout_building(x, S11_BOT, k, 1.0, seed=seed, sway=sway, floors=fl)


def s11(t):
    lib.dyn_begin()
    T_AVG, T_40, T_5, T_NOT, T_20 = ws(44), ws(47), ws(48), ws(51), ws(52)
    a, b = span("s11")
    o = []
    St = R.ST81
    g = lib.lin_grad([(0, St["sky0"], 1), (1, St["sky1"], 1)], 0, -400, 0, 1600, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-900" width="2900" height="4200" fill="url(#{g})"/>')
    for i, (cx_, cy_, k_) in enumerate(((120, 330, .9), (760, 220, .75), (1180, 420, 1.0), (430, 560, .6))):
        o.append(R._cloud81(cx_ + 18 * t, cy_, k_, i))
    # дальние дома — светлее, ниже
    for i, (x_, yr, sd) in enumerate(((60, 1500, 0), (380, 1420, 2), (720, 1460, 0), (1000, 1520, 2), (-200, 1380, 3))):
        o.append(f'<g opacity=".55">{_roof_bld(x_, yr, sd, 0.0, .8)}</g>')
    o.append(f'<rect x="-900" y="1300" width="2900" height="2000" fill="{St["sky1"]}" opacity=".25"/>')
    # три дома и основатели на крышах
    figs = []
    for i, (x_, yr, sd, kind) in enumerate(S11_ROOF):
        sw = .35 * math.sin(t * 2.1 + i * 1.3)
        o.append(_roof_bld(x_, yr, sd, sw, S11_BK))
        flip = (kind == "bald")
        fy = yr - 22
        hip_y = people.hip_on_floor(fy, S11_K) if False else fy - (people.LEG_LEN - 12) * S11_K * people.HEIGHT["fnd_" + kind]
        kw = dict(t=t, feet="stand", flip=flip)
        if kind == "cap":
            cu = ease_io(clamp((t - (T_40 - .1)) / .55))
            ex = "warm" if cu > .5 else "calm"
            f_ = people.founder81("cap", x_ - 10, hip_y, S11_K, "rest", expr=ex, cap_u=cu, head_add=.03 * math.sin(t * 1.7), **kw)
        elif kind == "glasses":
            gu = ease_io(clamp((t - (T_5 - .12)) / .3)) * (1 - ease_io(clamp((t - (T_5 + .75)) / .4)))
            f_ = people.founder81("glasses", x_ - 20, hip_y, S11_K, ("rest", "glasses"), u=gu, expr="calm" if gu < .5 else "focus", **kw)
        else:
            hu = ease_io(clamp((t - (T_AVG + .1)) / .4))
            f_ = people.founder81("bald", x_ + 20, hip_y, S11_K, ("rest", "hips"), u=hu, expr="warm", **kw)
        figs.append(f_)
        o.append(f_["svg"])
    # юный в худи: выскакивает на низкой крыше справа на «не двадцать», он мельче
    yu = clamp((t - (T_NOT - .12)) / .35)
    if yu > 0:
        x_, yr = S11_YOUNG
        pop = lib.back_out(yu, 2.0)
        ky = .2
        hip_y = yr - 16 - (people.LEG_LEN - 12) * ky + 260 * (1 - pop)
        clip = lib.clip_rect(x_ - 300, -900, 600, yr - 14 + 900)
        yf = people.youngster81(x_ - 10, hip_y, ky, ("rest", "hooray"), u=clamp((t - T_20) / .25), expr="grin", t=t, flip=True)
        o.append(f'<g clip-path="url(#{clip})">{yf["svg"]}</g>')
        o.append(_roof_bld(x_, yr, 0, 0.0, .7))
    # камера: подлёт снизу к крышам на «среднем», толчок на «сорок пять», лёгкий доворот к юному в конце
    fly = ease_out(clamp((t - (a - .02)) / (T_AVG + .45 - a)))
    cy = lerp(1550, 960, fly)
    s_ = lerp(.85, 1.55, fly) * (1 + .05 * kick(t, T_40, 1.0, .4) + .05 * kick(t, T_5, 1.0, .4) + .03 * kick(t, T_NOT, 1.0, .3))
    cx = 545 + 30 * ease_io(clamp((t - T_NOT) / .5)) + 8 * math.sin(t * 1.1)
    return frame_svg("".join(o), cx, cy, s_, rot=.4 * math.sin(t * .8), bg=St["sky1"])


# ═══════════════════════════════ s12: юный позёр под софитом ═══════════════════════════════
S12_FLOOR = 1400.0
S12_YK = .7
S12_X = 700.0
S12_CAR = (380.0, 1395.0, 1.15)


def _star_burst(x, y, r, op, rot=0.0):
    """Вспышка фотокамеры: четырёхлучевая звезда и мягкое ядро."""
    pts = []
    for j in range(8):
        a_ = math.radians(rot + j * 45)
        rr = r if j % 2 == 0 else r * .18
        pts.append((x + rr * math.cos(a_), y + rr * math.sin(a_)))
    return glow_spot(x, y, r * .9, "#ffffff", .8 * op) + blob(pts, "#ffffff", op)


def s12(t):
    lib.dyn_begin()
    T_YEARS, T_MILL = ws(53), ws(54)
    a, b = span("s12")
    o = []
    on = ease_out(clamp((t - (T_YEARS - .04)) / .12))
    # тёмная сцена: задник, пол с отражением
    g = lib.lin_grad([(0, "#0d0f1c", 1), (1, "#1c1f33", 1)], 0, -200, 0, S12_FLOOR, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-900" width="2900" height="{S12_FLOOR + 900:.0f}" fill="url(#{g})"/>')
    gf = lib.lin_grad([(0, "#2a2d44", 1), (1, "#12131f", 1)], 0, S12_FLOOR, 0, 2300, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="{S12_FLOOR:.0f}" width="2900" height="1200" fill="url(#{gf})"/>')
    o.append(line([(-900, S12_FLOOR), (2000, S12_FLOOR)], 3, "#3a3e5c", taper=0, wmin=1, seed=8801))
    # бархатный занавес по бокам
    for sx_ in (-1, 1):
        x0 = 540 + sx_ * 640
        cur = [(x0, -600), (x0 + sx_ * 400, -600), (x0 + sx_ * 400, S12_FLOOR), (x0 + sx_ * 30, S12_FLOOR)]
        inner = "".join(line([(x0 + sx_ * (60 + 70 * j), -600), (x0 + sx_ * (50 + 70 * j) + 12 * math.sin(t * 1.3 + j), S12_FLOOR)], 5, "#3a0f1a",
                             seed=8810 + j, op=.8) for j in range(5))
        o.append(shape(cur, "#5a1626", inner, w=4, seed=8820 + sx_))
    # машина и юный
    cx_, cy_, ck = S12_CAR
    car = P.sports_car(cx_, cy_, ck, seed=2, t=t)
    o.append(f'<g transform="translate(0 {2 * S12_FLOOR + 8:.1f}) scale(1 -1)" opacity=".18">{car}</g>')      # отражение в полу
    o.append(car)
    hu = ease_io(clamp((t - (T_MILL - .1)) / .22))
    hip_y = S12_FLOOR - (people.LEG_LEN - 12) * S12_YK * people.HEIGHT["yng81"]
    bounce = 10 * kick(t, T_MILL, 1.0, .45) + 4 * math.sin(t * 5.2) * (1 - hu)
    yf = people.youngster81(S12_X, hip_y - bounce, S12_YK, ("lean", "hooray"), u=hu, expr="cool" if hu < .5 else "shout", t=t,
                            head_add=.05 * math.sin(t * 3.0))
    o.append(blob(ellipse_pts(S12_X - 20, S12_FLOOR + 6, 170, 22, 18), "#000000", .35))
    o.append(yf["svg"])
    # блики на машине
    for j, (gx, gy) in enumerate(((220, 1265), (470, 1240), (610, 1300))):
        tw = .5 + .5 * math.sin(t * 9 + j * 2.1)
        o.append(_star_burst(gx, gy, 26 * tw * (.4 + .6 * on), .8 * on))
    # темнота вне софита и сам софит: конус сверху-слева, «бьёт» с перебором яркости
    dark = 1 - .62 * on
    o.append(f'<rect x="-900" y="-900" width="2900" height="3200" fill="#05060c" opacity="{.55 * dark:.3f}"/>')
    if on > .01:
        snap = 1 + .6 * kick(t, T_YEARS, 1.0, .35)
        cone = [(420, -500), (560, -500), (S12_X + 300, S12_FLOOR + 30), (S12_X - 360, S12_FLOOR + 30)]
        gc = lib.lin_grad([(0, "#ffe9b8", .42 * on * snap), (1, "#ffe9b8", .07 * on * snap)], 0, -500, 0, S12_FLOOR, units="userSpaceOnUse")
        d_ = "M" + " L".join(f"{x_:.1f} {y_:.1f}" for x_, y_ in cone) + " Z"
        o.append(f'<path d="{d_}" fill="url(#{gc})" style="mix-blend-mode:screen"/>')
        o.append(glow_spot(S12_X - 40, S12_FLOOR + 20, 420, "#fff1c8", .45 * on, 70))
    # вспышки фотокамер из темноты на «миллионеры»
    rs = __import__("numpy").random.RandomState(812)
    fl_all = 0.0
    for j in range(16):
        tf = T_MILL - .05 + j * .055 + rs.uniform(0, .04)
        v = (t - tf) / .16
        side = -1 if j % 2 else 1
        fx = 540 + side * rs.uniform(260, 520)
        fy = rs.uniform(300, 1300)
        if 0 < v < 1:
            op = (1 - v) ** 1.5
            o.append(_star_burst(fx, fy, 170 * (.6 + .4 * v), op, rot=rs.uniform(0, 45)))
            fl_all = max(fl_all, op)
    if t > T_YEARS - .04 and t < T_YEARS + .1:        # удар софита — белый кадр-вспышка
        o.append(f'<rect x="-900" y="-900" width="2900" height="3200" fill="#ffffff" opacity="{.55 * (1 - (t - T_YEARS + .04) / .14):.3f}"/>')
    if fl_all > 0:
        o.append(f'<rect x="-900" y="-900" width="2900" height="3200" fill="#ffffff" opacity="{.16 * fl_all:.3f}"/>')
    # камера: медленный наезд, качок на вспышках
    u = ease_io(clamp((t - a) / (b - a)))
    s_ = lerp(1.0, 1.12, u) * (1 + .06 * kick(t, T_YEARS, 1.0, .35) + .04 * kick(t, T_MILL, 1.0, .4))
    rot = 1.6 * math.sin((t - T_MILL) * 18) * math.exp(-3 * max(0.0, t - T_MILL)) if t > T_MILL else .4 * math.sin(t * 1.4)
    return frame_svg("".join(o), 560, 1000, s_, rot=rot, bg="#05060c")


# ═══════════════════════════════ s17: кот гордо кивает и спрыгивает ═══════════════════════════════
def _ext_a():
    """Сцена верстака группы A (s15/s16) — тот же верстак, окно и лодка с парусом: модуль ext_a/s81a.py только читается."""
    import importlib.util
    if "s81a" not in sys.modules:
        spec = importlib.util.spec_from_file_location("s81a", os.path.join(STORY, "ext_a", "s81a.py"))
        m = importlib.util.module_from_spec(spec)
        sys.modules["s81a"] = m
        spec.loader.exec_module(m)
    return sys.modules["s81a"]


def s17(t):
    lib.dyn_begin()
    A = _ext_a()
    T_SURE, T_ALL = ws(78), ws(80)
    a, b = span("s17")
    o = A.bench_scene(t, 0.0, 7.0, 1.0, 1.0)
    bx, by = A.BOAT
    cat_x, cat_y, cat_k = bx + 300, A.BENCH_Y - 118, .6
    # брусок, на котором кот сидел в s16
    o.append(shape(lib.rect_pts(cat_x - 130, A.BENCH_Y - 120, cat_x + 130, A.BENCH_Y - 6), P.C_WOOD_HI,
                   line([(cat_x - 110, A.BENCH_Y - 60), (cat_x + 100, A.BENCH_Y - 62)], 3, P.C_WOOD_SH, seed=5), w=4, seed=1650))
    proud = ease_out(clamp((t - a) / .45))
    st = {"tilt": -9 * proud, "look": (.1 - .3 * proud, -.85 * proud), "blink": .45 * proud, "smile": 1.0, "perk": .6 * proud,
          "drop": -.14 * proud, "flame_e": 1.3 + .3 * proud, "tail": 8 * math.sin(t * 2.6)}
    if t >= T_SURE - .08:     # «уверен»: смотрит на зрителя и уверенно кивает, огонёк вспыхивает
        v = ease_out(clamp((t - (T_SURE - .08)) / .15))
        st.update(tilt=-9 * (1 - v) + 3 * v, look=(0, .1), blink=.45 * (1 - v) + .15 * v, perk=.3)
        st["drop"] = -.14 * (1 - v) + people.cat_nod(t, T_SURE, .34, .3) + people.cat_nod(t, T_SURE + .36, .28, .18)
        st["flame_e"] = 1.4 + 1.2 * kick(t, T_SURE, 1.0, .5)
    floor = A.FLOOR14
    land = (cat_x + 330, floor)
    J0 = T_ALL - .22
    if t < J0:
        o.append(A.shadow(cat_x, cat_y + 2, 110, .2))
        o.append(people.cat_svg(cat_x, cat_y, cat_k, st, t))
        cpos = (cat_x, cat_y)
    else:
        u = clamp((t - J0) / .6)
        st2 = {"look": (.8, .3), "smile": 1.0, "flame_e": 1.6, "turn": .3}
        if u < 1:
            o.append(people.cat_jump((cat_x, cat_y), land, cat_k, u, t, st2, height=170))
            cpos = lerp2((cat_x, cat_y), land, clamp((u - .3) / .55))
        else:
            w_ = (t - (J0 + .6)) / .32
            x_ = land[0] + 260 * (t - (J0 + .6))
            o.append(people.cat_walk(x_, land[1], cat_k, w_ * .32, dict(st2, look=(.9, 0))))
            cpos = (x_, land[1])
    # камера: мягкий наезд к коту, рывок вслед прыжку
    z = ease_io(clamp((t - a) / (T_ALL - .2 - a)))
    s_ = lerp(3.1, 3.45, z) * (1 + .03 * kick(t, T_SURE, 1.0, .4)) * lerp(1.0, .85, ease_io(clamp((t - J0) / .5)))
    follow = ease_in(clamp((t - J0) / .5))
    cx = lerp(lerp(cat_x - 40, cat_x - 10, z), cpos[0] + 30, follow)
    cy = lerp(cat_y - 115, cpos[1] - 140, follow)
    return frame_svg("".join(o), cx, cy, s_, rot=lerp(.4, -.3, z) + 1.5 * follow * math.sin(t * 7) * (1 - follow), bg=A.D_WALL)


def frame(sid, t):
    return globals()[sid](t)
