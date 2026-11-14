"""Рилс 59 «подарок», группа B: s05 (друзья), s06 (статья), s07 (спутанная голова). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Люди и кот — только ../common/people.py (Дима, друзья), предметы — ../common/props.py. Печатных букв и цифр нет: заголовок листа — полоса,
текст — штрихи, номера пунктов — кружки."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
from lib import (INK, back_out, blob, blur, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rrect, shape,  # noqa: E402,F401
                 smooth, spring)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def decay(t, t0, k=9.0, fr=22.0):
    """Затухающая тряска после удара в t0 (0 до удара)."""
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def open_hand(c=.2, d=(1, 0), spread=.2, thumb=.2, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(c, c, c, c * .9), spread=spread, thumb=thumb, bend=.1, k=k)


def point_hand(d, flip=1, k=1.0):
    """Указательный вытянут, остальные согнуты, большой прижат."""
    return dict(kind="open", flip=flip, dir=d, curl=(0.0, .92, .92, .92), spread=.05, thumb=.75, bend=.05, k=k)


def person(who, hip, bs, expr, arms, hands, lean=0.0, head_ang=0.0, head_off=(0, 0), feet=None, torso_k=1.0):
    p = dict(hip=tuple(hip), scale=bs * people.HEIGHT.get(who, 1.0), lean=lean, torso_k=torso_k, feet=feet, arms=arms, hands=hands, expr=expr,
             head_ang=head_ang, head_off=head_off, hood=0.0, strings=(0, 0))
    return people.draw(p, who)


def lin(stops, x1=0, y1=0, x2=0, y2=1):
    return lib.lin_grad(stops, x1, y1, x2, y2)


# ═════════════════════════════ s05: друзья ═════════════════════════════
T_DRUZ, T_KAZH, T_SVOE = wt(17), wt(19), wt(21)        # 6.86, 7.49, 8.32
T_SOV = wt(20)                                         # 7.81
TABLE_Y = 1130
TABLE_Y2 = 1115
# x в мире: девушка, лысый, Дима, парень в кепке (в мире 1080 + запас под панораму)
XS = {"girl": 205, "bald": 470, "dima": 760, "cap": 1030}


def room_wall():
    g = lin([(0, "#efdcc3", 1), (1, "#e3c9a6", 1)])
    o = [f'<rect x="-300" y="-200" width="1700" height="1700" fill="url(#{g})"/>']
    # нижняя панель стены
    o.append(blob(lib.rect_pts(-300, 960, 1400, 1500), "#c9a074"))
    o.append(line([(-300, 960), (1400, 960)], 5, "#8d6a44", taper=0, wmin=1, seed=11))
    # окно с вечерним небом
    wg = lin([(0, "#f7c98c", 1), (1, "#e88f6a", 1)])
    o.append(shape(rrect(40, 300, 420, 760, 10), f"url(#{wg})", blob(ellipse_pts(300, 520, 70, 70, 14), "#fff1c4"), w=7, seed=12))
    o.append(line([(230, 300), (230, 760)], 6, "#7a5a3a", taper=0, wmin=1, seed=13))
    o.append(line([(40, 530), (420, 530)], 6, "#7a5a3a", taper=0, wmin=1, seed=14))
    # картины без надписей
    o.append(shape(rrect(560, 340, 800, 560, 6), "#f3ece0", blob(ellipse_pts(680, 470, 60, 40, 12), "#7ab0a0") + blob([(580, 540), (680, 440), (780, 540)], "#e08a6a"),
                   w=7, seed=15))
    o.append(shape(rrect(900, 380, 1060, 520, 6), "#f3ece0", blob(ellipse_pts(980, 450, 34, 34, 12), "#e9b84a"), w=7, seed=16))
    # лампа
    o.append(line([(1180, 300), (1180, 520)], 5, INK, taper=0, wmin=1, seed=17))
    o.append(shape([(1130, 520), (1230, 520), (1206, 440), (1154, 440)], "#f0c870", blob(ellipse_pts(1180, 520, 60, 20, 10), "#fff0b0"), w=5, seed=18))
    return "".join(o)


def table_front():
    o = [shape(rrect(-300, TABLE_Y, 1400, TABLE_Y + 70, 8), "#c58b52", blob(rrect(-300, TABLE_Y, 1400, TABLE_Y + 24, 6), "#dba66f"), w=6, seed=21)]
    o.append(blob(lib.rect_pts(-300, TABLE_Y + 70, 1400, 2800), "#a2693a"))
    o.append(line([(-300, TABLE_Y + 70), (1400, TABLE_Y + 70)], 4, "#6e4524", taper=0, wmin=1, seed=22))
    o.append(line([(-300, TABLE_Y + 110), (1400, TABLE_Y + 110)], 2.4, "#8a5a30", taper=0, wmin=1, seed=23, op=.7))
    # чашки на столе
    for i, (cx, col) in enumerate(((120, "#e88c6a"), (360, "#7ab0a0"), (640, "#e9b84a"), (900, "#9aa0d0"), (1120, "#e88c6a"))):
        y = TABLE_Y + 20
        o.append(blob(ellipse_pts(cx + 6, y + 8, 56, 10, 12), "#8a5a30", .7))
        o.append(shape([(cx - 40, y - 56), (cx + 40, y - 56), (cx + 32, y + 6, 1), (cx - 32, y + 6, 1)], col, blob([(cx + 14, y - 56), (cx + 40, y - 56), (cx + 32, y + 6), (cx + 10, y + 6)], mix(col, "#000000", .2)),
                       w=4.2, seed=30 + i))
        o.append(blob(ellipse_pts(cx, y - 56, 40, 8, 12), "#6b3f25"))
        o.append(line([(cx + 40, y - 40), (cx + 66, y - 36), (cx + 58, y - 12), (cx + 34, y - 10)], 5, col, taper=.2, wmin=.8, seed=40 + i))
    return "".join(o)


def cloud(cx, cy, s, seed, name, k_item, rot_i=0.0, tail_to=None, squash=0.0):
    """Облачко-мысль с вещью внутри. squash — сплющивание при толчке (0..1). tail_to — точка, к которой идут кружки-хвостик."""
    rx, ry = 118 * s, 92 * s
    n = 9
    pts = []
    for i in range(72):
        th = 2 * math.pi * i / 72
        r = 1 + .10 * math.cos(n * th + seed)
        pts.append((cx + rx * r * math.cos(th) * (1 + .1 * squash), cy + ry * r * math.sin(th) * (1 - .12 * squash)))
    o = []
    if tail_to is not None:
        tx, ty = tail_to
        for j, (u, rr) in enumerate(((.18, 16), (.36, 11), (.52, 7))):
            px = cx + (tx - cx) * u
            py = cy + ry * .82 + (ty - cy - ry * .82) * u
            o.append(shape(ellipse_pts(px, py, rr * s, rr * s, 10), "#ffffff", "", w=4.0, seed=int(seed * 10) + j))
    o.append(shape(pts, "#ffffff", blob(ellipse_pts(cx + 20 * s, cy + 30 * s, 100 * s, 50 * s, 14), "#e7ebf2", .9), w=5.6, seed=int(seed * 100)))
    ih = PR.ITEM_H[name]
    o.append(PR.item(name, cx, cy + ih * k_item * .5 - 4, k_item, rot_i))
    return "".join(o)


def frame05(t):
    a = 5.66
    pan = ease_io(clamp((t - a) / 2.9))
    z = 1.0 + .06 * pan
    set_ink(z)
    shake = 9 * decay(t, T_KAZH, 8, 20) + 6 * decay(t, T_SVOE, 8, 24)
    cx = 470 + 130 * pan + shake
    cy = 960 + 10 * math.sin(t * 2)
    o = [room_wall()]
    FB = 1230                                    # таз друзей (скрыт столом)
    POS = {"girl": (190, .82), "bald": (520, .8), "cap": (870, .82)}
    tk = {"girl": "book", "bald": "sneaker", "cap": "kettle"}
    talk_t = {"girl": T_KAZH + .02, "bald": T_KAZH + .12, "cap": T_KAZH + .22}
    face_to = {"girl": 1, "bald": 1, "cap": -1}
    figs = {}
    TY = TABLE_Y2
    for i, who in enumerate(("girl", "bald", "cap")):
        x, bs = POS[who]
        ph = t - (T_DRUZ + .09 * i - .08)
        sx = -face_to[who] if ph < 0 else -face_to[who] + 2 * face_to[who] * ease_io(clamp(ph / .2))
        g = clamp((t - talk_t[who]) / .25)
        gest = math.sin((t - talk_t[who]) * 9 + i) * .5 + .5
        expr = dict(lid=.8, brows="up", mouth="smile", smile=.7, look=(.5, 0), closed=blink_of(t, (6.3 + .3 * i, 7.9 + .2 * i)))
        arms = {"f": ("ik", (x + 80, TY - 10), -1), "n": ("ik", (x + 120, TY), -1)}
        hands = {"f": open_hand(.35, (1, .1), .1, .4, k=bs), "n": open_hand(.35, (1, .1), .1, .4, k=bs)}
        head_ang = 0.0
        if g > 0:
            expr.update(mouth="talk", open=.2 + .6 * abs(math.sin((t - talk_t[who]) * 11 + i)), smile=.6, brows="up", lid=.95)
            up = ease_out(g)
            wy = TY - (330 + 50 * gest) * up
            wx = x + {"girl": 215, "bald": 150, "cap": -215}[who] + 25 * math.sin((t - talk_t[who]) * 7)
            arms["n"] = ("ik", (wx, wy), -1)
            hands["n"] = {"bald": point_hand((.3, -1), flip=1, k=bs), "girl": open_hand(.1, (.4, -1), .35, .1, k=bs)}.get(who, open_hand(.45, (.3, -1), .15, .5, k=bs))
            head_ang = .06 * math.sin((t - talk_t[who]) * 8)
        fig = person(who, (x, FB), bs, expr, arms, hands, head_ang=head_ang)
        figs[who] = fig
        svg = fig["arm_f"] + fig["body"] + fig["arm_n"]
        o.append(f'<g transform="translate({x} 0) scale({sx:.4f} 1) translate({-x} 0)">{svg}</g>')
    o.append(table_front())
    # Дима спереди, крупно, растерян
    dx, dbs = 560, 1.3
    sq = clamp((t - T_SVOE) / .25)
    look_x = -.6 * math.sin(clamp((t - T_DRUZ) / 1.6) * math.pi * 2.2)
    expr = dict(lid=.85 - .35 * sq, brows="worry", mouth="flat" if sq < .5 else "wobble", smile=0, look=(look_x, .15), closed=blink_of(t, (6.4, 7.6, 8.5)), open=.3)
    wr = (dx + 190 - 140 * sq, 1690 - 640 * sq)
    arms = {"f": ("ik", (dx + 100, 1740), -1), "n": ("ik", wr, -1)}
    hands = {"f": open_hand(.5, (1, .1), .1, .4, k=dbs), "n": open_hand(.3 + .5 * sq, (1 - sq, .5 - 1.5 * sq), .3, .3, k=dbs)}
    hoff = (0, 16 * ease_out(clamp((t - T_SVOE) / .2)) + 4 * math.sin(t * 5))
    d = person("dima", (dx, 1960), dbs, expr, arms, hands, head_ang=.04 * math.sin(t * 3) + .05 * sq, head_off=hoff)
    o.append(d["arm_f"] + d["body"] + d["arm_n"])
    figs["dima"] = d
    # облачка над друзьями
    for who in ("girl", "bald", "cap"):
        x, bs = POS[who]
        hx, hy = figs[who]["head"]
        t_on = T_KAZH + {"girl": 0, "bald": .12, "cap": .24}[who] - .05
        if t < t_on:
            continue
        u = back_out(clamp((t - t_on) / .3), 2.2)
        mv = ease_io(clamp((t - T_SOV) / .45))
        push = clamp((t - T_SVOE) / .25)
        tgt = {"girl": 380, "bald": 540, "cap": 700}[who]
        bx = x + (tgt - x) * mv
        s = (.85 + .1 * u) * max(u, .05) * (1.0 + .4 * ease_out(push))
        by = 400 + 8 * math.sin(t * 4 + x) + 20 * (1 - u) + 110 * ease_out(push)
        jig = 10 * decay(t, T_SVOE + .03 * ("girl", "bald", "cap").index(who), 6, 26)
        sqq = (clamp((t - T_SVOE) / .2) * (math.sin((t - T_SVOE) * 30) * .4 + .6)) if t > T_SVOE else 0
        o.append(cloud(bx + jig, by, s, {"girl": 1.0, "bald": 2.2, "cap": 3.1}[who], tk[who], 1.5, rot_i=4 * math.sin(t * 5 + x),
                       tail_to=(hx, hy - 150 * bs), squash=sqq))
    dh = d["head"]
    if t > T_SVOE:
        o.append(shape([(dh[0] - 190, dh[1] - 90, 1), (dh[0] - 215, dh[1] - 30), (dh[0] - 190, dh[1] + 10), (dh[0] - 165, dh[1] - 30)], "#bfe6fa",
                       blob([(dh[0] - 198, dh[1] - 40), (dh[0] - 190, dh[1] - 15), (dh[0] - 182, dh[1] - 40)], "#ffffff"), w=3.4, seed=77))
    cam = lib.cam(cx, cy, z, .8 * (1 - pan) - .3 * bump(t, T_KAZH, .3))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════════ s06: статья ═════════════════════════════
T_STAT, T_LUCH, T_PODA = wt(24), wt(26), wt(27)          # 10.05, 10.60, 11.00
SH_C = (610, 740)
SH_W, SH_H = 800, 1060
# строки текста листа: (y, x0, x1, блок)
LINES = []


def sheet_layout():
    L = []
    y = 520
    for blk in range(3):
        n = (4, 3, 4)[blk]
        for j in range(n):
            L.append((y, 330 + (0 if j else 54), 840 - ((j * 37 + blk * 53) % 120), blk))
            y += 44
        y += 60
    return L


LAYOUT = sheet_layout()
STAR_SPOTS = [(250, 470), (930, 560), (250, 780), (930, 900), (270, 1050), (920, 1120), (300, 330), (900, 400)]
ICON_SPOTS = [(240, 540, 0), (940, 480, 1), (230, 700, 2), (950, 700, 3), (235, 880, 0), (945, 860, 4), (240, 1030, 5), (940, 1010, 1), (260, 1170, 2),
              (920, 1150, 3), (590, 1220, 0), (300, 1220, 4), (880, 1230, 5), (760, 330, 1), (420, 330, 2)]


def mini_icon(kind, x, y, k, rot=0.0, lid=0.0):
    if kind == 0:
        return PR.giftbox(x, y, k, lid, rot, seed=kind)
    nm = PR.ITEMS[(kind - 1) % 6]
    return PR.item(nm, x, y, k * 1.35, rot)


def article(t, u_in):
    """Лист: бумага, полоса заголовка, блоки штрихов, маркер идёт за пальцем."""
    cx, cy = SH_C
    x0, y0, x1, y1 = cx - SH_W / 2, cy - SH_H / 2, cx + SH_W / 2, cy + SH_H / 2
    o = [blob(rrect(x0 + 18, y0 + 24, x1 + 18, y1 + 24, 10), "#2b2118", .22)]
    o.append(shape(rrect(x0, y0, x1, y1, 10), "#fbf7ec", blob(rrect(x1 - 60, y0, x1, y1, 6), "#efe7d4", .9), w=6, seed=61))
    # полоса заголовка (выезжает слева)
    wu = ease_out(clamp(u_in * 1.4))
    o.append(shape(rrect(x0 + 40, y0 + 52, x0 + 40 + (SH_W - 80) * wu, y0 + 150, 8), "#2f3e6a", blob(rrect(x0 + 40, y0 + 52, x0 + 40 + (SH_W - 80) * wu, y0 + 74, 6), "#44568a"), w=5, seed=62))
    o.append(line([(x0 + 70, y0 + 120), (x0 + 70 + 420 * wu, y0 + 120)], 8, "#f1e6c4", taper=0, wmin=1, seed=63) if wu > .05 else "")
    o.append(line([(x0 + 70, y0 + 96), (x0 + 70 + 560 * wu, y0 + 96)], 10, "#f7efd8", taper=0, wmin=1, seed=64) if wu > .05 else "")
    # картинка-блок: коробка в рамке
    pu = ease_out(clamp((u_in - .3) * 1.6))
    if pu > .02:
        o.append(shape(rrect(x0 + 40, y0 + 185, x0 + 40 + 250 * pu, y0 + 345, 8), "#f2dcc4", blob(ellipse_pts(x0 + 165, y0 + 300, 80, 16, 12), "#e4c9ac", .8), w=5, seed=65))
        if pu > .6:
            o.append(PR.giftbox(x0 + 165, y0 + 332, 1.0, 0.0, 0.0, seed=2))
    # строки текста
    o.append(f'<g>')
    tip = None
    for i, (y, xa, xb, blk) in enumerate(LAYOUT):
        yy = y - 160 + (y0 - 80 + 160) - 0
        yy = y + (SH_C[1] - 740)
        st = .25 + .09 * i
        wu2 = ease_out(clamp((u_in - st * .6) * 2.2))
        if wu2 <= .02:
            continue
        xe = xa + (xb - xa) * wu2
        # маркер за пальцем
        hi = clamp((t - (T_STAT - .15 + .115 * i)) / .22)
        if hi > 0:
            o.append(blob(lib.rect_pts(xa - 6, yy - 18, xa - 6 + (xb - xa + 12) * ease_out(hi), yy + 16), "#ffe36a"))
        o.append(line([(xa, yy), ((xa + xe) / 2, yy + 3), (xe, yy - 1)], 8, "#6b6358", taper=0, wmin=1, seed=100 + i, op=.95))
        if (i % 4) == 0 and wu2 > .8:        # кружок-пункт
            o.append(shape(ellipse_pts(xa - 28, yy, 9, 9, 10), "#e04a5a", "", w=2.4, seed=140 + i))
    o.append("</g>")
    return "".join(o)


def finger_tip_path(t):
    """Кончик пальца Димы: линия за линией сверху вниз со слова «статью» (10.05)."""
    per = .115
    k = (t - (T_STAT - .15)) / per
    k = max(0.0, k)
    i = min(int(k), len(LAYOUT) - 1)
    u = k - int(k)
    if k >= len(LAYOUT):
        i, u = len(LAYOUT) - 1, 1.0
    y, xa, xb, blk = LAYOUT[i]
    yy = y + (SH_C[1] - 740)
    return xa + (xb - xa) * ease_io(u) , yy - 10, i


def frame06(t):
    a = 8.5
    u = clamp((t - a + .3) / 1.1)            # въезд листа (первый кадр уже с заголовком)
    z0 = 1.02 + .26 * ease_io(clamp((t - a) / 2.9))
    set_ink(z0)
    sh = 7 * decay(t, T_LUCH, 7, 22) + 12 * decay(t, T_PODA, 6, 20)
    # бумага стола
    g = lin([(0, "#8c5f3a", 1), (1, "#6e4526", 1)])
    o = [f'<rect x="-400" y="-400" width="1900" height="2700" fill="url(#{g})"/>']
    for k in range(9):
        o.append(line([(-400, 100 + k * 240), (1500, 110 + k * 240)], 3, "#5a371c", taper=0, wmin=1, seed=200 + k, op=.5))
    rot = -2.2 + 2.2 * ease_out(u) + .4 * math.sin(t * 2)
    slide = (1 - ease_out(u)) * 160
    art = [article(t, u)]
    # звёздочки на полях («лучшие») и значки («подарки»)
    sp = []
    for i, (x, y) in enumerate(STAR_SPOTS):
        tt = T_LUCH + .06 * i
        k = clamp((t - tt) / .55)
        if 0 < k < 1:
            sp.append(PR.spark(x, y + (SH_C[1] - 740), 1.4 + .6 * math.sin(i), k, "#ffd54a"))
        elif k >= 1 and t - tt < 3:
            pass
    for i, (x, y, kind) in enumerate(ICON_SPOTS):
        tt = T_PODA + .045 * i
        k = clamp((t - tt) / .32)
        if k <= 0:
            continue
        s_ = back_out(k, 2.6) * .55
        sp.append(mini_icon(kind, x, y + (SH_C[1] - 740) + 30, s_, rot=8 * math.sin(i * 2 + t * 3) , lid=.4 * bump(t, tt + .2, .3)))
        # блик
        sp.append(PR.spark(x + 30, y + (SH_C[1] - 740) - 60, 1.0, clamp((t - tt - .1) / .5), "#ffd54a"))
    o.append(f'<g transform="translate({slide:.2f} {-slide * .3:.2f}) rotate({rot:.2f} {SH_C[0]} {SH_C[1]})">{"".join(art)}{"".join(sp)}</g>')
    # Дима в углу + рука с пальцем
    bs = 1.08
    hip = (215, 1640)
    reading = clamp((t - (T_STAT - .3)) / .3)
    fx, fy, li = finger_tip_path(t)
    # перевод в мир через вращение листа
    ang = math.radians(rot)
    px, py = fx - SH_C[0], fy - SH_C[1]
    wx = SH_C[0] + px * math.cos(ang) - py * math.sin(ang) + slide
    wy = SH_C[1] + px * math.sin(ang) + py * math.cos(ang) - slide * .3
    dvec = np.array([.8, .6])
    dvec = dvec / np.linalg.norm(dvec)
    rest = (520, 1500)
    h_u = ease_out(reading)
    tipx, tipy = rest[0] + (wx - rest[0]) * h_u, rest[1] + (wy - rest[1]) * h_u
    wrist = (tipx - dvec[0] * 130 * bs / .96 - 0, tipy - dvec[1] * 130 * bs / .96 + 18)
    look = (.7 + .15 * math.sin(t * 7), .5 + .3 * math.sin(t * 3.3)) if reading > 0 else (.5 + .5 * math.sin(t * 5), .3)
    lid = .3 + .02 * math.sin(t * 6)
    expr = dict(lid=lid, brows="det", mouth="flat", look=look, closed=blink_of(t, (9.3, 10.9, 12.0)))
    arms = {"f": ("ik", (330, 1330), -1), "n": ("ik", wrist, -1)}
    hands = {"f": open_hand(.5, (1, .2), .1, .4, k=bs), "n": point_hand(tuple(dvec), flip=-1, k=bs * 1.0)}
    d = person("dima", hip, bs, expr, arms, hands, lean=.06, head_ang=.12, head_off=(0, 0))
    o.append(d["arm_f"] + d["body"] + d["arm_n"])
    zz = z0
    cam = lib.cam(560 + 30 * ease_io(clamp((t - a) / 2.9)) + sh, 840 + 70 * ease_io(clamp((t - a) / 2.9)) + sh * .7, zz,
                  1.0 * (1 - u) - .5 + .3 * math.sin(t * 2.2) + .5 * decay(t, T_LUCH, 6, 14))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════════ s07: спутанная голова ═════════════════════════════
T_ZAP, T_ESHE, T_SIL = wt(29), wt(30), wt(31)             # 11.66, 12.32, 12.61


def spiral_pts(cx, cy, r0, r1, turns, ang0, u):
    """Спираль от центра наружу; u 0..1 — доля нарисованной длины."""
    n = 140
    pts = []
    for i in range(int(n * u) + 1):
        s = i / n
        th = ang0 + s * turns * 2 * math.pi
        r = r0 + (r1 - r0) * s
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th) * .92))
    return pts


def frame07(t):
    a = 11.1
    # камера: наезд с разгоном (ease_in), тряска на «запутался»
    ui = ease_in(clamp((t - a) / 2.2), 2.2)
    z = 1.0 + .4 * ui
    set_ink(z)
    shk = 14 * decay(t, T_ZAP, 7, 21) + 8 * decay(t, T_SIL, 8, 24)
    # фон
    g = rad_grad([(0, "#f6ead3", 1), (1, "#d9c3a0", 1)], 540, 900, 900)
    o = [f'<rect x="-600" y="-500" width="2300" height="3000" fill="url(#{g})"/>']
    HX, HY = 560, 1010
    sp_u = ease_out(clamp((t - T_ZAP) / .7))
    inten = 1 + 1.4 * smooth(T_ESHE - .05, T_ESHE + .4, t)
    cover = ease_out(clamp((t - T_SIL) / .22))
    cx, cy = HX + 10, HY - 300
    # спираль + значки (за головой)
    if t >= T_ZAP - .02:
        spin = (t - T_ZAP) * (2.4 + 3.0 * smooth(T_ESHE - .05, T_ESHE + .5, t) + 1.2 * cover)
        turns = 2.6 + 1.6 * smooth(T_ESHE - .05, T_ESHE + .5, t)
        for k, (col, w) in enumerate((("#7a5bbd", 11), ("#e0586f", 8), ("#3b9a8f", 6))):
            ph = k * 2.1
            pts = spiral_pts(cx, cy, 50, 460 * inten ** .5 + k * 18, turns + k * .25, spin + ph, sp_u)
            if len(pts) > 2:
                o.append(line(pts, w, col, taper=.6, wmin=.25, seed=300 + k, peak=.4))
        n_ic = int(7 + 6 * smooth(T_ESHE - .05, T_ESHE + .5, t))
        for i in range(n_ic):
            s = (i + .5) / 14
            th = spin * 1.1 + s * turns * 2 * math.pi + i * .3
            r = (70 + 440 * s * inten ** .4)
            x_, y_ = cx + r * math.cos(th), cy + r * math.sin(th) * .92
            k_ = clamp((t - (T_ZAP + .03 * i)) / .3)
            if k_ <= 0:
                continue
            kind = i % 6
            o.append(mini_icon(kind, x_, y_ + 28, .62 * back_out(k_, 2.4) * (.85 + .3 * s), rot=(spin * 40 + i * 30) % 360 - 180 if i % 3 == 0 else 14 * math.sin(i + t * 4)))
    # Дима
    bs = 1.7
    hip = (HX - 30 * bs, HY + 586 * bs)
    ph = t * 9
    dz = smooth(T_ZAP - .05, T_ZAP + .25, t)
    dz2 = smooth(T_ESHE - .05, T_ESHE + .3, t)
    lk_n = (.6 * math.cos(ph * (1 + dz2)) * dz, -.5 + .6 * math.sin(ph * (1 + dz2)) * dz)
    lk_f = (-.6 * math.cos(ph * (1 + dz2) + 1.2) * dz, .5 - .6 * math.sin(ph * (1 + dz2) + 1.2) * dz)
    expr = dict(lid=.9 - .3 * cover, brows="worry", mouth="wobble" if dz > .5 else "flat", look=(0, 0), look_n=lk_n, look_f=lk_f, smile=0,
                closed=blink_of(t, (11.5, 12.9)) if dz < .2 else 0.0, open=.3)
    expr["mouth"] = "talk" if dz > .5 and cover < .5 else ("flat" if cover >= .5 else "flat")
    expr["open"] = .25 + .1 * abs(math.sin(t * 8))
    hx_, hy_ = HX, HY
    arm_n = ("ik", (hx_ + 60 + 260 * (1 - ease_out(cover)), hy_ + 330 + 900 * (1 - ease_out(cover))), 1)
    arm_f = ("ik", (hx_ + 10 + 300 * (1 - ease_out(cover)), hy_ + 360 + 900 * (1 - ease_out(cover))), 1)
    dd = (.25 * (1 - cover), -1 + 2 * (1 - cover))
    hands = {"n": open_hand(.15 + .35 * cover, dd, .35, .3, flip=1, k=bs), "f": open_hand(.15 + .35 * cover, dd, .35, .3, flip=-1, k=bs)}
    d = person("dima", hip, bs, expr, {"n": arm_n, "f": arm_f}, hands, lean=.03 + .05 * cover, head_ang=.08 * dz - .35 * cover,
               head_off=(0, 40 * cover))
    o.append(d["body"])
    if cover > .02:
        o.append(d["arm_f"])
    o.append(d["arm_n"])
    cam = lib.cam(HX + shk, HY - 80 + 40 * ui + shk * .6, z, -.6 * dz + 1.4 * decay(t, T_ZAP, 6, 16) + .6 * cover)
    return f'<g transform="{cam}">{"".join(o)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    fn = {"s05": frame05, "s06": frame06, "s07": frame07}[sid]
    body = fn(t)
    return lib.svg(body)
