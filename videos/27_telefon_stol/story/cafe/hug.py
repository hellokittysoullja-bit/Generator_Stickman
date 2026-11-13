"""Хук s01: вход в кафе, Дима и друг обнимаются, друг хлопает Диму по спине.

Постановка: Дима спиной к нам (худи, капюшон на спине, лохматый затылок), друг выше ростом, лицом к нам из-за плеча
Димы — зажмурился от радости, широкая улыбка в рыжей бороде. Руки друга лежат у Димы на спине и хлопают на словах;
руки Димы обхватили друга (локти торчат по бокам, предплечья уходят за друга).
Рисунок — в L-единицах героев (голова ~300), группа масштабируется U и ставится в точку O мира.
Слои сзади вперёд: предплечья Димы → торс друга → голова друга → плечи Димы → спина Димы → затылок → руки друга.
"""
import math

import numpy as np

import hand as Hand
import lib
import people as Pp
from lib import INK, blob, ellipse_pts


def _P(p):
    return (float(p[0]), float(p[1]))


def dima_back_head(hb=0.0, turn=0.0):
    """Затылок Димы: волосы прядями, оба уха, шея. turn > 0 — чуть повернул голову вправо (видна скула справа)."""
    Pp.C = Pp.PAL["dima"]
    C = Pp.C
    s = []
    # шея
    neck = [(-62, 50), (60, 50), (68, 150, 1), (-70, 150, 1)]
    s.append(Pp.shape(neck, C["SKIN"], blob([(-80, 60), (80, 60), (80, 120), (-80, 130)], C["SKIN_SH"], .9), w=4.6, seed=4000))
    # уши
    for sx, sd in ((-1, 4001), (1, 4002)):
        ear = [(sx * 104, -30), (sx * 132, -40), (sx * 150, -10), (sx * 146, 30), (sx * 126, 54), (sx * 104, 46)]
        s.append(Pp.shape(ear, C["SKIN"], blob([(sx * 120, -20), (sx * 146, -6), (sx * 140, 30), (sx * 122, 30)], C["SKIN_SH"], .9), w=4.6, seed=sd))
        s.append(Pp.line([(sx * 116, -16), (sx * 136, -8), (sx * 134, 22)], 2.6, seed=sd + 10, op=.8))
    # скула справа (голова чуть повёрнута к другу)
    if turn > 0:
        ch = [(96, -20), (124 + 10 * turn, 10), (120 + 8 * turn, 70), (90, 100), (70, 60)]
        s.append(Pp.shape(ch, C["SKIN"], blob([(80, 40), (130, 40), (120, 100), (80, 100)], C["SKIN_SH"], .7), w=4.4, seed=4005))
        rs = np.random.RandomState(9)
        for _ in range(14):
            x, y = rs.uniform(92, 120), rs.uniform(50, 86)
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="#5c4446" opacity=".55"/>')
    # волосы: вся макушка и затылок, пряди торчат
    hair = [(-112, 40), (-128, 0), (-150, -30, 1), (-130, -50), (-160, -96, 1), (-120, -104), (-140, -160, 1), (-90, -150), (-90, -206, 1),
            (-46, -168), (-20, -224, 1), (6, -176), (40, -222, 1), (56, -170), (102, -196, 1), (98, -146), (150, -146, 1), (126, -100),
            (162, -66, 1), (128, -44), (146, -6, 1), (112, 24), (100, 56), (70, 66), (40, 80), (10, 72), (-20, 82), (-50, 70), (-80, 56)]
    hair = Pp._bounce(hair, hb, y0=-60, k=80)
    inner = blob([(20, -240), (180, -200), (180, 100), (40, 100), (70, -60)], C["HAIR_SH"], .9)
    inner += blob(Pp._bounce([(-90, -170), (-30, -196), (10, -160), (-40, -140)], hb, -60, 80), C["HAIR_HI"], .85)
    inner += blob(Pp._bounce([(-130, -60), (-100, -110), (-70, -80), (-100, -40)], hb, -60, 80), C["HAIR_HI"], .6)
    for i, st in enumerate([[(-60, -150), (-40, -90), (-50, -30)], [(0, -160), (8, -100), (0, -40)], [(60, -150), (50, -90), (60, -20)],
                            [(-110, -80), (-90, -30), (-96, 20)], [(100, -100), (90, -40), (96, 20)], [(-20, 0), (-10, 40)], [(30, 10), (34, 50)]]):
        inner += Pp.line(Pp._bounce(st, hb, -60, 80), 3.2, "#2a170f", seed=4020 + i, op=.85)
    s.append(Pp.shape(hair, C["HAIR"], inner, w=5.4, seed=4010))
    return "".join(s)


def dima_back_torso(hood_b=0.0, bump=0.0, dent=None):
    """Спина в худи: плечи, капюшон лежит на лопатках, складки; dent — вмятина от ладони (x, y, сила)."""
    Pp.C = Pp.PAL["dima"]
    C = Pp.C
    body = [(-166, 40), (-140, 0), (-84, -22), (0, -28), (84, -22), (140, 0), (166, 40), (178, 150), (172, 420), (186, 1500, 1),
            (-186, 1500, 1), (-172, 420), (-178, 150)]
    inner = blob([(60, -40), (220, 0), (220, 1500), (110, 1500), (130, 300)], C["TOP_SH"], .7)
    inner += Pp.line([(-120, 160), (-80, 260), (-90, 380)], 2.6, C["FOLD"], seed=4101, op=.75)
    inner += Pp.line([(110, 180), (80, 290), (96, 420)], 2.6, C["FOLD"], seed=4102, op=.75)
    inner += Pp.line([(0, 140), (6, 300), (-4, 470)], 2.4, C["FOLD"], seed=4103, op=.55)
    if dent is not None:
        x, y, k = dent
        if k > .02:
            inner += Pp.line([(x - 70, y - 20), (x - 30, y + 10 * k), (x + 30, y + 10 * k), (x + 70, y - 20)], 3.0, C["FOLD"], seed=4104, op=.9 * k)
            inner += blob(ellipse_pts(x, y, 80, 40, 12), C["TOP_SH"], .5 * k)
    s = [Pp.shape(body, C["TOP"], inner, w=5.4, seed=4100)]
    col = [(-96, -24), (-50, -44), (0, -48), (50, -44), (96, -24), (70, -6), (0, -14), (-70, -6)]
    s.append(Pp.shape(col, C["TOP_SH"], "", w=4.0, seed=4105))
    # капюшон на спине
    hb = hood_b
    hood = [(-120, -10), (-60, -36), (0, -40), (60, -36), (120, -10), (112, 70 + hb), (60, 140 + hb * 1.2), (0, 160 + hb * 1.3), (-60, 140 + hb * 1.2),
            (-112, 70 + hb)]
    h_in = blob([(-90, 0), (90, 0), (70, 90 + hb), (0, 110 + hb), (-70, 90 + hb)], C["TOP_SH2"], .95)
    h_in += Pp.line([(-60, 40 + hb * .6), (0, 70 + hb), (60, 40 + hb * .6)], 2.6, C["FOLD"], seed=4111, op=.85)
    s.append(Pp.shape(hood, C["TOP_SH"], h_in, w=5.0, seed=4110))
    return "".join(s)


def dima_arms_back():
    """Руки Димы, обнимающие друга: плечо видно сбоку, локоть торчит, предплечье уходит за друга."""
    Pp.C = Pp.PAL["dima"]
    s_back, s_mid = [], []
    for sx, sd in ((-1, 4200), (1, 4220)):
        S = np.array([sx * 140.0, 50.0])
        E = np.array([sx * 262.0, 300.0])
        Wr = np.array([sx * 130.0, 380.0])
        s_back.append(Pp.limb_band(E, Wr, 112, 98, Pp.C["TOP_SH"], False, sd + 1))
        s_mid.append(Pp.limb_band(S, E, 132, 114, Pp.C["TOP"], False, sd,
                                  lambda a, b, d, n: blob([_P(np.array(a) + n * 60 * sx), _P(np.array(b) + n * 50 * sx), _P(np.array(b) + n * 14 * sx),
                                                           _P(np.array(a) + n * 18 * sx)], Pp.C["TOP_SH"], .85)))
    return "".join(s_back), "".join(s_mid)


def friend_front_torso():
    """Друг анфас: широкие плечи, джинсовая куртка распахнута, белая футболка, воротник, пуговицы."""
    Pp.C = Pp.PAL["friend"]
    C = Pp.C
    cx = 230
    body = [(cx - 300, -120), (cx - 230, -170), (cx - 90, -196), (cx + 90, -196), (cx + 230, -170), (cx + 300, -120), (cx + 316, 40),
            (cx + 300, 1500, 1), (cx - 300, 1500, 1), (cx - 316, 40)]
    inner = blob([(cx + 120, -200), (cx + 330, -150), (cx + 330, 1500), (cx + 180, 1500)], C["TOP_SH"], .8)
    tee = [(cx - 80, -196), (cx + 80, -196), (cx + 96, 1500, 1), (cx - 96, 1500, 1)]
    inner += Pp.shape(tee, C["TEE"], blob([(cx + 30, -196), (cx + 100, -196), (cx + 100, 1500), (cx + 40, 1500)], C["TEE_SH"], .9) +
                      Pp.line([(cx - 40, -190), (cx, -150), (cx + 40, -190)], 2.6, C["TEE_SH"], seed=4305), w=3.6, seed=4301)
    for sx in (-1, 1):
        flap = [(cx + sx * 80, -196), (cx + sx * 110, -120), (cx + sx * 100, 1500, 1), (cx + sx * 300, 1500, 1), (cx + sx * 300, -100)]
        fi = Pp.line([(cx + sx * 104, -100), (cx + sx * 96, 400)], 1.8, C["STITCH"], seed=4310 + sx, op=.85)
        pk = [(cx + sx * 140, -60), (cx + sx * 250, -60), (cx + sx * 246, 50, 1), (cx + sx * 144, 50, 1)]
        fi += Pp.shape(pk, C["TOP"], Pp.line([(cx + sx * 146, -40), (cx + sx * 244, -40)], 1.6, C["STITCH"], seed=4313 + sx, op=.8), w=3.2,
                       seed=4312 + sx)
        fi += Pp.shape([(cx + sx * 134, -66), (cx + sx * 256, -66), (cx + sx * 252, -34), (cx + sx * 196, -24), (cx + sx * 138, -34)], C["TOP_SH"], "",
                       w=3.2, seed=4314 + sx)
        if sx > 0:
            for y in (-90, 40, 170, 300):
                fi += f'<circle cx="{cx + 92 + 10 * (y / 300):.1f}" cy="{y}" r="9" fill="#c9a96a"/><circle cx="{cx + 89:.1f}" cy="{y - 3}" r="3" fill="#f2dfae"/>'
        inner += Pp.shape(flap, C["TOP"], fi + blob([(cx + sx * 220, -100), (cx + sx * 300, -100), (cx + sx * 300, 1500), (cx + sx * 230, 1500)],
                                                    C["TOP_SH"], .7 if sx > 0 else .3), w=4.4, seed=4320 + sx)
        col = [(cx + sx * 70, -236), (cx + sx * 130, -196), (cx + sx * 150, -110, 1), (cx + sx * 96, -150), (cx + sx * 64, -190)]
        inner += Pp.shape(col, C["TOP_SH"], "", w=3.8, seed=4330 + sx)
    s = Pp.shape(body, C["TOP"], inner, w=5.4, seed=4300)
    neck = [(cx - 60, -300), (cx + 60, -300), (cx + 66, -186, 1), (cx - 66, -186, 1)]
    s = Pp.shape(neck, C["SKIN"], blob([(cx - 70, -320), (cx + 70, -320), (cx + 70, -260), (cx - 70, -250)], C["SKIN_SH"], .9), w=4.6, seed=4340) + s
    return s


def friend_arm(S, E, Wr, d, lift, seed, flip):
    """Рука друга на спине Димы: рукав, кисть тыльной стороной к нам."""
    Pp.C = Pp.PAL["friend"]
    o = Pp.sleeve(np.array(S, float), np.array(E, float), np.array(Wr, float), False, seed, "friend")
    kw = Pp.hand_kw()
    k = 1.06 + .12 * lift
    o += Hand.hand(np.array(Wr, float) + np.array(d) * 2, d, flip=flip, k=k, curl=(.05, .05, .08, .1), spread=.12 + .1 * lift, thumb=.35,
                   bend=.06, seed=seed + 50, **kw)
    return o


def hug(t, slaps, sway=0.0, jolt=0.0):
    """Вся группа в L-единицах. slaps — список (время, сторона −1/+1) хлопков."""
    o = []
    # хлопки: подъём ладони и удар
    lift = {-1: 0.0, 1: 0.0}
    dent = None
    impact = []
    for ts, side in slaps:
        u = t - ts
        if -.16 < u < 0:
            lift[side] = max(lift[side], math.sin(math.pi * (u + .16) / .16 * .5))
        elif 0 <= u < .22:
            k = 1 - u / .22
            if u < .05:
                lift[side] = max(lift[side], .25 * (1 - u / .05))
            dent = ((-60 if side < 0 else 110), (150 if side < 0 else 440), k)
            impact.append((side, u))
    hd = Pp.PAL
    db_back, db_mid = dima_arms_back()
    o.append(db_back)
    o.append(friend_front_torso())
    expr = dict(lid=.9, look=(.3, 0), brows="up", mouth="laugh", open=.85 + .15 * jolt, laugh=1.0)
    Pp.C = hd["friend"]
    fh = Pp.friend_head(expr)
    o.append(f'<g transform="translate(262 -420) rotate({-6 + 3 * sway:.2f}) scale(-1 1)">{fh}</g>')
    o.append(db_mid)
    o.append(dima_back_torso(hood_b=10 * jolt, dent=dent))
    arms = {}
    for side, S, E, Wr0, d, flip, sd in ((-1, (-70, -150), (-250, 60), (-80, 130), (1, -.15), 1, 4400),
                                          (1, (500, -120), (450, 330), (130, 430), (-1, -.1), -1, 4460)):
        li = lift[side]
        Wr = (Wr0[0] - side * 10 * li, Wr0[1] - 70 * li)
        dd = (d[0], d[1] - .5 * li)
        arms[side] = friend_arm(S, E, Wr, dd, li, sd, flip)
    o.append(arms[-1])
    o.append(f'<g transform="translate(-50 -196) rotate({4 * sway + 2 * jolt:.2f})">{dima_back_head(hb=8 * jolt, turn=.6)}</g>')
    o.append(arms[1])
    for side, u in impact:
        x, y = (-10, 130) if side < 0 else (60, 430)
        a = 1 - u / .22
        for j, ang in enumerate((-150, -110, -60) if side < 0 else (-120, -70, -30)):
            r0, r1 = 90 + 60 * u / .22, 130 + 90 * u / .22
            c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            o.append(Pp.line([(x + c * r0, y + sn * r0), (x + c * r1, y + sn * r1)], 7, INK, seed=4500 + j + (side > 0) * 5, op=a, taper=.4, wmin=.3))
    return "".join(o)
