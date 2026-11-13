"""Сцена dima рилса 31: планы s05, s06, s12 (комната Димы) и s15 (прихожая). frame(sid, t) -> SVG 1080×1920,
t — общее время ролика. Удары — на словах по voice/words.json.

Дима — people.py (копия героев cafe рилса 27: голова, лицо, волосы, мешки, щетина, горчичное худи), стоит, ноги уходят
за нижний край кадра; руки — ИК к целям, кисти с пальцами (hand.py). Предметы и фоны — props.py.
Толщина туши героя: lib.INK_K = EFF / масштаб героя (на экране — как у героев 27-го на среднем плане).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import people  # noqa: E402
import props as Pr  # noqa: E402
from lib import back_out, clamp, ease_io, ease_out, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!").lower() == word.lower() and w["start"] >= after:
            return w["start"]
    raise KeyError(word)


T_GOVORIT = wt("говорит")              # 6.80
T_PAMYAT = wt("память", 7)             # 7.72
T_KAK = wt("как", 7)                   # 8.08
T_RYBKI = wt("рыбки", 8)               # 8.32
T_DIMA2 = wt("дима", 17)               # 18.00
T_NICHEGO = wt("ничего", 18)           # 18.80
T_ZAPIS = wt("записывает")             # 19.28
T_NICHEGO2 = wt("ничего", 24)          # 24.80
T_TERYAETSYA = wt("теряется")          # 25.88

FLIP6 = -1
SCR_SIDE = 1
EFF = 0.78                             # экранная толщина туши героя (как у 27-го на среднем плане)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def talk(t, t0, t1, rate=7.0):
    if t < t0 or t > t1:
        return 0.0
    v = .5 + .5 * math.sin(2 * math.pi * rate * (t - t0)) * (.7 + .3 * math.sin(t * 3.1))
    return clamp(v * smooth(t0, t0 + .08, t) * (1 - smooth(t1 - .08, t1, t)))


def blink(t, times, dur=.16):
    v = 0.0
    for tb in times:
        if abs(t - tb) < dur / 2:
            v = max(v, 1 - abs(t - tb) / (dur / 2))
    return v


def lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def cam_tf(cx, cy, s, r=0.0):
    return lib.cam(cx, cy, s, r)


def vignette(col="#2a1408", a=.36):
    g = lib.rad_grad([(0, col, 0), (.62, col, 0), (1, col, a)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


# ═════════════════════════ Дима стоя ═════════════════════════
def dima(hip, s, lean=0.04, arms=None, hands=None, expr=None, head_ang=0.0, head_off=(0, 0), cam_s=1.0):
    """Дима стоит, ноги — за нижним краем. Возвращает dict слоёв people.draw + 'head_ang' (рад, полный поворот головы)."""
    lib.INK_K[0] = EFF / (s * cam_s)
    hx, hy = hip
    p = dict(hip=(hx, hy), scale=s, lean=lean,
             feet={"n": ((hx + 40 * s, hy + 640 * s), 0.0), "f": ((hx - 30 * s, hy + 630 * s), 0.0)},
             arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang, head_off=head_off, hood=0.0)
    out = people.draw(p, "dima")
    out["head_ang"] = lean * .5 + head_ang
    out["s"] = s
    lib.INK_K[0] = 1.0 / cam_s ** .62
    return out


def head_pt(d, local):
    """Точка лица (единицы головы) → мир."""
    return d["head"] + rot(np.array(local, float), d["head_ang"]) * d["s"]


def layers(d, mid="", front=""):
    return (d.get("legs", "") + d["arm_f"] + d.get("pelvis", "") + d["body"] + d.get("hand_f", "") + mid + d["arm_n"] + d.get("hand_n", "")
            + front)


# ═════════════════════════ комната Димы ═════════════════════════
def room_bg(t, variant):
    o = [Pr.room_wall(t)]
    if variant == "s05":
        o.append(Pr.window(40, 330, 330, 820, t))
        o.append(Pr.curtain(-20, 290, 900, 110, t))
        o.append(Pr.curtain(400, 290, 900, -110, t, seed=2210))
        o.append(Pr.shelf_books(620, 960, 1120, t))
        o.append(Pr.lamp(980, 760, t))
    elif variant == "s06":
        o.append(Pr.window(-60, 250, 260, 760, t))
        o.append(Pr.curtain(300, 210, 840, -110, t, seed=2210))
        o.append(Pr.shelf_books(600, 1000, 1140, t))
    else:
        o.append(Pr.poster(700, 300, 960, 620))
        o.append(Pr.window(-120, 300, 180, 800, t))
        o.append(Pr.curtain(250, 260, 880, -100, t, seed=2210))
        o.append(Pr.lamp(1000, 760, t))
    return "".join(o)


def fish_bubble_inner(cx, cy, k, t, flip=1):
    """Рыбка, плывущая в облачке: маленькая восьмёрка."""
    x = cx + 30 * k * math.sin(t * 2.4)
    y = cy + 10 * k * math.sin(t * 4.8)
    return Pr.gold_fish(x, y, k * .62, t, flip=flip, rot=6 * math.cos(t * 2.4), seed=11, look=(.5, .1))


# ═════════════════════════ s05: «всем говорит» — разводит руками, облачко с рыбкой ═════════════════════════
def s05(t):
    a, b = 5.95, 7.9
    k = ease_io(clamp((t - a) / (b - a)))
    whip = 1 - ease_out(clamp((t - a) / .35), 3)
    tg = T_GOVORIT
    cam = (560 - 70 * whip + 20 * k, 930 - 30 * k, 1.0 + .09 * k + .025 * bump(t, tg - .02, .3), -.6 * whip + .5 * k)
    o = [f'<g transform="{cam_tf(*cam)}">']
    o.append(room_bg(t, "s05"))
    # жест: ладони вверх, плечи вверх на «говорит», руки разводятся с 6.25
    g0 = ease_out(clamp((t - 6.05) / .45), 3)
    sh = smooth(tg - .32, tg - .02, t) * (1 - .55 * smooth(tg + .35, tg + .8, t))
    sh_pop = bump(t, tg - .05, .32)
    s = 1.3
    hip = (390, 1450)
    swing = .5 * osc(t, 1.6)
    near0, far0 = (250, 1250), (640, 1230)
    near1 = (205 - 25 * sh, 1170 - 60 * sh + 8 * swing)
    far1 = (790 + 30 * sh, 1090 - 60 * sh - 8 * swing)
    nt = lerp(near0, near1, g0)
    ft = lerp(far0, far1, g0)
    nt = (nt[0], nt[1] - 16 * sh_pop)
    ft = (ft[0], ft[1] - 16 * sh_pop)
    op = talk(t, 6.2, 7.75, 6.2)
    expr = dict(lid=.75 + .2 * sh, look=(.55, -.15 - .1 * sh), brows="up" if t > 6.35 else "calm", mouth="talk", open=.15 + .75 * op,
                smile=.7 + .3 * sh, closed=blink(t, [6.42, 7.62]), hair=6 * sh_pop)
    hands = {"n": dict(kind="open", flip=1, dir=(-1, -.6 - .3 * sh), curl=(.12, .16, .2, .26), spread=.3, thumb=.05, bend=.14, nails=False),
             "f": dict(kind="open", flip=-1, dir=(1, -.6 - .3 * sh), curl=(.12, .16, .2, .26), spread=.3, thumb=.05, bend=.14, nails=False)}
    d = dima(hip, s, lean=-.03 - .04 * sh, arms={"n": ("ik", nt, 1), "f": ("ik", ft)}, hands=hands, expr=expr,
             head_ang=-.06 * sh + .03 * osc(t, 1.3), head_off=(0, 46 * sh), cam_s=cam[2])
    o.append(layers(d))
    # облачко-реплика с рыбкой: выскакивает на «говорит»
    u = clamp((t - (tg - .12)) / .34)
    if u > 0:
        sc = back_out(u, 2.2)
        mouth = head_pt(d, (110, 90))
        bc = (810, 520 + 6 * osc(t, .9))
        lib.INK_K[0] = 1.0 / cam[2] ** .62
        bub = Pr.speech_bubble(bc[0], bc[1], 205, 150, (mouth[0] + 40, mouth[1] - 40), s=sc)
        inner = fish_bubble_inner(bc[0] - 6, bc[1] + 2, 1.2 * sc, t)
        o.append(bub + inner)
        o.append(Pr.burst(bc[0], bc[1], 1.0, clamp((t - tg + .05) / .35), n=8, r0=230, r1=280))
    o.append("</g>")
    o.append(vignette())
    return lib.svg("".join(o))


# ═════════════════════════ s06: стучит пальцем по лбу, облако-мысль, аквариум на «рыбки» ═════════════════════════
def s06(t):
    a, b = 7.5, 9.3
    k = ease_io(clamp((t - a) / (b - a)))
    tr = T_RYBKI
    hit = bump(t, tr - .02, .3)
    cam = (520 + 16 * k, 800 - 30 * k, 1.04 + .07 * k + .045 * hit, .4 - .8 * k + .7 * hit * osc(t, 9))
    o = [f'<g transform="{cam_tf(*cam)}">']
    o.append(room_bg(t, "s06"))
    s = 1.95
    hip = (330, 1900)
    # удары пальцем по лбу: на «память», между словами, на «как»
    taps = [T_PAMYAT + .02, T_PAMYAT + .26, T_KAK + .02]
    tap = 0.0
    for tt in taps:
        tap = max(tap, bump(t, tt - .09, .2))
    raise_ = ease_out(clamp((t - 7.45) / .3), 3)
    after = smooth(tr + .2, tr + .6, t)
    d0 = dima(hip, s, lean=.02, arms={"n": ("ik", (500, 1300)), "f": ("ang", .15, .3)}, hands={}, expr={}, cam_s=cam[2])
    # кончик указательного — у лба; палец смотрит вверх-влево
    fdir = np.array([-.97, .12])
    fdir /= np.linalg.norm(fdir)
    tip = head_pt(d0, (100, -80)) - fdir * (4 + 34 * (1 - tap)) - fdir * 30 * after
    rest = np.array([560.0, 1420.0])
    tip = rest + (tip - rest) * raise_
    wr = tip - fdir * 128 * s - np.array([-fdir[1], fdir[0]]) * FLIP6 * (-22 * s)
    jolt = -.05 * tap
    squint = .55 * tap
    look_up = smooth(7.85, 8.05, t)
    expr = dict(lid=.55 + .35 * look_up - .3 * tap, look=(.35 + .15 * look_up, -.15 - .38 * look_up), brows="worry" if t > 7.9 else "tired",
                mouth="sheep" if t > tr - .05 else ("flat" if t < 7.95 else "smile"), smile=.6 + .4 * after, closed=max(squint, blink(t, [7.62, 8.95])),
                blush=after * .9)
    hands = {"f": dict(kind="open", flip=FLIP6, dir=tuple(fdir), curl=(0.0, .95, 1.0, 1.0), spread=.0, thumb=.95, bend=.04, front=True, nails=True)}
    d = dima(hip, s, lean=.02, arms={"f": ("ik", tuple(wr), -1), "n": ("ang", -.6, .1)}, hands=hands, expr=expr,
             head_ang=jolt - .05 * after + .02 * osc(t, 1.1), cam_s=cam[2])
    # ближняя рука опущена и отведена назад — за туловищем (иначе на крупном плане внизу висит круглый рукав)
    o.append(d.get("legs", "") + d["arm_f"] + d["arm_n"] + d["body"] + d.get("hand_f", ""))
    # облако-мысль
    src = head_pt(d, (150, -170))
    cu = clamp((t - 7.78) / .3)
    trail = clamp((t - 7.6) / .2)
    lib.INK_K[0] = 1.0 / cam[2] ** .62
    cc = (770, 330 + 5 * osc(t, .8))
    o.append(Pr.thought_cloud(cc[0], cc[1], 255, 175, (src[0], src[1]), s=back_out(cu, 1.8) if cu > 0 else 0, trail=trail, t=t))
    au = clamp((t - (tr - .06)) / .32)
    if au > 0:
        sc = back_out(au, 2.4)
        R = 128 * sc
        bx, by = cc[0] + 4, cc[1] + 14

        def fin():
            fx = bx + 26 * sc * math.sin(t * 2.2)
            fl = 1 if math.cos(t * 2.2) > 0 else -1
            return Pr.gold_fish(fx, by + 22 * sc + 6 * math.sin(t * 4.4), .38 * sc, t, flip=fl, seed=21)
        o.append(Pr.bowl(bx, by, R, t, fin, seed=930))
        o.append(Pr.burst(bx, by, 1.0, clamp((t - tr) / .32), n=8, r0=150, r1=210))
    o.append("</g>")
    o.append(vignette())
    return lib.svg("".join(o))


# ═════════════════════════ s12: хлопает по карманам, пустой блокнот, ручка падает на «записывает» ═════════════════════════
DESK = (560, 1180, 1120)
PEN0 = (690.0, 1258.0)


def pen_state(t):
    """Ручка лежит у края, на «записывает» скатывается и падает с кромки."""
    tz = T_ZAPIS
    x, y = PEN0
    ang = -6.0
    roll = smooth(tz - .3, tz, t)
    x += 0 * roll
    y += 26 * roll
    ang += 0 * roll
    if t > tz:
        u = t - tz
        y += 0.5 * 3600 * u * u + 60 * u
        x += 120 * u
        ang += 420 * u
    return x, y, ang


def s12(t):
    a, b = 17.8, 20.5
    k = ease_io(clamp((t - a) / (b - a)))
    whip = 1 - ease_out(clamp((t - a) / .35), 3)
    tz = T_ZAPIS
    shake = bump(t, tz + .05, .3)
    cam = (560 + 60 * whip + 10 * k, 900 - 10 * k + 6 * shake * osc(t, 14), 1.0 + .06 * k, .7 * whip - .4 * k + .5 * shake * osc(t, 11))
    o = [f'<g transform="{cam_tf(*cam)}">']
    o.append(room_bg(t, "s12"))
    o.append(Pr.desk(DESK[0], DESK[1], DESK[2]))
    o.append(Pr.mug(1040, 1232, 1.0))
    o.append(Pr.notebook(860, 1228, .95, flutter=bump(t, tz + .1, .4)))
    px, py, pa = pen_state(t)
    pen_svg = Pr.pen(px, py, pa, 1.25)
    s = 1.3
    hip = (380, 1390)
    tn = T_NICHEGO
    # хлопки: ближняя рука по карману-кенгуру, дальняя — по переднему карману джинсов
    pats_n = [17.86, 18.14, 18.42]
    pats_f = [18.0, 18.28, 18.56]
    pn = max(bump(t, tt - .08, .18) for tt in pats_n)
    pf = max(bump(t, tt - .08, .18) for tt in pats_f)
    pat_on = 1 - smooth(tn - .22, tn - .02, t)
    open_u = smooth(tn - .2, tn + .08, t) * (1 - smooth(19.62, 19.9, t))
    scratch = smooth(19.6, 19.95, t)
    # цели рук
    n_pat = (hip[0] + 30 * s, hip[1] - 60 * s - 60 * pn)
    f_pat = (hip[0] + 190 * s, hip[1] + 40 * s - 50 * pf)
    n_open = (hip[0] - 170, 1150 - 10 * osc(t, 1.4))
    f_open = (hip[0] + 400, 1080 + 10 * osc(t, 1.4))
    d0 = dima(hip, s, arms={"n": ("ik", n_pat), "f": ("ik", f_pat)}, hands={}, expr={}, cam_s=cam[2])
    sc_pt = head_pt(d0, (-60, -150)) + np.array([0, 0])
    sc_osc = 14 * osc(t, 5.5) * scratch
    n_scr = (sc_pt[0] - 70 + sc_osc, sc_pt[1] + 70 - sc_osc * .4)
    f_rest = (hip[0] + 200, hip[1] + 150)
    if t < tn - .1:
        nt, ft = n_pat, f_pat
    else:
        nt = lerp(n_pat, n_open, open_u if t < 19.62 else 1)
        ft = lerp(f_pat, f_open, open_u if t < 19.62 else 1)
        if t >= 19.62:
            nt = lerp(n_open, n_scr, scratch)
            ft = lerp(f_open, f_rest, scratch)
    pen_look = smooth(tz - .05, tz + .12, t) * (1 - smooth(19.75, 20.0, t))
    dn = pat_on
    look = (.2 + .3 * dn, .55 * dn)
    look = lerp(look, (.5, -.05), open_u)
    look = lerp(look, (.75, .8), pen_look)
    look = lerp(look, (.4, -.55), scratch)
    if t < tn - .1:
        mouth, op = "flat", 0
    elif t < tz - .05:
        mouth, op = "gape", .4
    elif t < 19.7:
        mouth, op = "gape", 1.0
    else:
        mouth, op = "gape", .35
    expr = dict(lid=.55 + .35 * open_u + .1 * pen_look, look=look, brows="worry" if t < tn - .1 or t > 19.7 else "up", mouth=mouth, open=op,
                closed=blink(t, [18.62, 20.25]), hair=5 * bump(t, tz, .3) + 3 * scratch * osc(t, 5.5))
    hn = dict(kind="open", flip=1, dir=(.45, 1), curl=(.1, .12, .14, .18), spread=.1, thumb=.35, bend=.06)
    hf = dict(kind="open", flip=-1, dir=(.25, 1), curl=(.08, .1, .12, .16), spread=.08, thumb=.3, bend=.05)
    if open_u > .5:
        hn = dict(kind="open", flip=1, dir=(-1, -.5), curl=(.12, .16, .2, .26), spread=.32, thumb=.05, bend=.14, nails=False)
        hf = dict(kind="open", flip=-1, dir=(1, -.6), curl=(.12, .16, .2, .26), spread=.32, thumb=.05, bend=.14, nails=False)
    if t >= 19.62 and scratch > .35:
        hn = dict(kind="open", flip=1, dir=(.75, -.6), curl=(.55 + .2 * osc(t, 5.5), .6, .62, .6), spread=.12, thumb=.4, bend=.1)
        hf = dict(kind="open", flip=-1, dir=(.1, 1), curl=(.3, .35, .4, .45), spread=.06, thumb=.5)
    head_ang = .06 * pen_look - .07 * scratch + .03 * pn
    d = dima(hip, s, lean=.04 + .05 * pat_on * (1 - open_u), arms={"n": ("ik", nt, 1 if scratch < .3 else SCR_SIDE), "f": ("ik", ft)},
             hands={"n": hn, "f": hf}, expr=expr, head_ang=head_ang, head_off=(0, 26 * open_u * (1 - scratch)), cam_s=cam[2])
    lib.INK_K[0] = 1.0 / cam[2] ** .62
    # пыль из пустого кармана на «ничего»
    du = clamp((t - tn + .05) / .55)
    dust = ""
    if 0 < du < 1:
        c0 = (hip[0] + 90 * s, hip[1] - 120 * s)
        for j in range(4):
            ang = -2.7 + j * .62
            r = 40 + 120 * ease_out(du)
            x, y = c0[0] + math.cos(ang) * r, c0[1] + math.sin(ang) * r - 30 * du
            rr = (22 + 6 * (j % 3)) * (1 - .6 * du)
            dust += Pr.shape(Pr.cloud_pts(x, y, rr, rr * .8, 5), "#ddd6c6", "", w=3.0, seed=4100 + j)
    slaps = ""
    for tt in pats_n:
        slaps += Pr.burst(n_pat[0] + 120, hip[1] - 20 * s, 1.0, clamp((t - tt + .02) / .22), n=5, r0=60, r1=95, seed=4200)
    for tt in pats_f:
        slaps += Pr.burst(f_pat[0] + 50, hip[1] + 60 * s, 1.0, clamp((t - tt + .02) / .22), n=5, r0=70, r1=110, seed=4210)
    o.append(layers(d, front=dust + slaps))
    o.append(pen_svg)
    o.append("</g>")
    o.append(vignette())
    return lib.svg("".join(o))


# ═════════════════════════ s15: прихожая, ключи с крючка, подбрасывает и ловит на «теряется» ═════════════════════════
RACK = (700, 600, 940)


def keys_flight(t, catch_pt):
    """Ключи в полёте: бросок с ладони, вершина, поимка. Возвращает (x, y, угол) или None, если в руке."""
    t0, t1 = T_TERYAETSYA - .06, T_TERYAETSYA + .5
    if t < t0 or t > t1:
        return None
    u = (t - t0) / (t1 - t0)
    x = catch_pt[0] + 40 * math.sin(math.pi * u)
    y = catch_pt[1] - 4 * 520 * u * (1 - u)
    return x, y, 360 * u * 1.5


def s15(t):
    a, b = 24.55, 27.05
    k = ease_io(clamp((t - a) / (b - a)))
    whip = 1 - ease_out(clamp((t - a) / .35), 3)
    tt = T_TERYAETSYA
    fly = smooth(tt - .1, tt + .2, t) * (1 - smooth(tt + .35, tt + .65, t))
    catch = bump(t, tt + .5, .3)
    cam = (570 - 70 * whip + 10 * k, 880 - 50 * fly + 14 * catch, 1.1 + .05 * k + .03 * catch, -.6 * whip + .4 * k)
    o = [f'<g transform="{cam_tf(*cam)}">']
    o.append(Pr.hall_wall(t))
    o.append(Pr.door(-110, 260, 200, 1400))
    rack, hooks = Pr.key_rack(*RACK)
    o.append(rack)
    o.append(Pr.coat(1030, RACK[1] + 20, t))
    s = 1.25
    hip = (410, 1340)
    hook = np.array(hooks[1])
    # фазы: тянется к крючку → снял (24.98) → к груди → бросок на «теряется» → поймал
    reach = ease_io(clamp((t - 24.5) / .38))
    grab_t = 24.98
    take = ease_io(clamp((t - grab_t - .05) / .4))
    chest = np.array([640.0, 1060.0])
    wr_hook = hook + np.array([-82, 30])
    rest0 = np.array([560.0, 1300.0])
    nt = rest0 + (wr_hook - rest0) * reach
    nt = nt + (chest - nt) * take
    # замах и бросок
    wind = bump(t, tt - .3, .28)
    flick = bump(t, tt - .08, .22)
    nt = nt + np.array([0, 40 * wind - 70 * flick])
    catch_pt = chest + np.array([10, -30])
    caught = bump(t, tt + .48, .26)
    nt = nt + np.array([0, 30 * caught])
    held = t < tt - .06 or t > tt + .5
    in_flight = keys_flight(t, catch_pt)
    grab_c = clamp((t - grab_t + .1) / .12)
    if t < grab_t - .1:
        hn = dict(kind="open", flip=1, dir=(.55, -.85), curl=(.15, .2, .25, .3), spread=.18, thumb=.2, bend=.1)
    elif held:
        hn = dict(kind="open", flip=1, dir=(.8, -.6) if t < tt else (.85, -.5), curl=(.85 * grab_c, .9 * grab_c, .9 * grab_c, .85 * grab_c),
                  spread=.05, thumb=.4 + .5 * grab_c, bend=.08)
    else:
        hn = dict(kind="open", flip=1, dir=(.9, -.45), curl=(.15, .18, .22, .26), spread=.25, thumb=.1, bend=.12, nails=False)
    hf = dict(kind="open", flip=-1, dir=(.3, -1), curl=(.7, .78, .82, .8), spread=.04, thumb=.75, bend=.06)
    ft = (630 + 6 * osc(t, .7), 1200 - 8 * osc(t, .7))
    look = (.55, -.35) if t < grab_t + .2 else (.5, .05)
    if in_flight:
        look = (.5, -.8 * math.sin(math.pi * (t - tt + .06) / .56))
    joy = smooth(tt + .5, tt + .7, t)
    expr = dict(lid=.75 + .2 * fly, look=look, brows="up", mouth="grin" if t > 25.2 else "smile", smile=1.0, open=.6,
                laugh=.45 * joy, closed=blink(t, [24.75]), hair=5 * caught)
    d = dima(hip, s, lean=.03 - .04 * fly, arms={"n": ("ik", tuple(nt), -1), "f": ("ik", ft)}, hands={"n": hn, "f": hf}, expr=expr,
             head_ang=-.08 * fly + .03 * osc(t, 1.2) - .04 * reach * (1 - take), cam_s=cam[2])
    lib.INK_K[0] = 1.0 / cam[2] ** .62
    wr = d["wrist"]["n"]
    hd = np.array(hn["dir"], float)
    hd /= np.linalg.norm(hd)
    grip_pt = wr + hd * 92 * s + np.array([-hd[1], hd[0]]) * 6 * s
    front = ""
    if t < grab_t:
        kx, ky = hook[0] - 6, hook[1] - 8
        ksvg = Pr.keys(kx, ky, 4 * osc(t, .9), 1.3)
        o.append(ksvg)
    elif held:
        sw = 18 * math.sin(7 * (t - grab_t)) * math.exp(-2.5 * (t - grab_t)) if t < tt else 22 * math.sin(8 * (t - tt - .5)) * math.exp(-3 * max(0, t - tt - .5))
        front = Pr.keys(grip_pt[0], grip_pt[1], sw, 1.3)
    # телефон в дальней руке
    fw = d["wrist"]["f"]
    ph = Pr.phone(fw[0] + 40, fw[1] - 90, 8 + 2 * osc(t, .7), 1.05, glow=1)
    out = d.get("legs", "") + d["arm_f"] + ph + d.get("pelvis", "") + d["body"] + d["arm_n"] + front
    o.append(out)
    if in_flight:
        x, y, ang = in_flight
        o.append(Pr.keys(x, y, ang, 1.3))
        if y < catch_pt[1] - 200:
            o.append(Pr.burst(x, y + 80, .6, clamp((t - tt) / .3), n=6, r0=60, r1=100))
    o.append("</g>")
    o.append(vignette())
    return lib.svg("".join(o))


SHOTS = {"s05": s05, "s06": s06, "s12": s12, "s15": s15}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
