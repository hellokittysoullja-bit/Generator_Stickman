"""Рилс 61 «стол», группа F: s05 (кот с вопросом на куче бумаг), s17 (кот спит на тёплом столе), s18 (призыв, рукописное «кот»).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Слова — voice/words.json."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import catf  # noqa: E402
import props  # noqa: E402
import room  # noqa: E402
import people  # noqa: E402
import hand_kot  # noqa: E402
import lib  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rrect, shape  # noqa: E402,F401

import numpy as np  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
WI = {}
for i_, w_ in enumerate(WORDS):
    WI.setdefault(w_["word"].strip(".,!?").lower(), []).append(i_)


def wt(word, k=0):
    return WORDS[WI[word][k]]["start"]


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def blinks(t, times, dur=.16):
    v = 0.0
    for tb in times:
        u = (t - tb) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


PAGE, PAGE_SH, PAGE_LN = "#fbf3dc", "#e2d4b2", "#8f8670"


# ───────────────────────────── s05: кот крупно на куче бумаг ─────────────────────────────
T_BES, T_POM = wt("беспорядок"), wt("помогать")


def wall_desk(t, warm=1.0):
    """Тёплая стена у творческого стола: наброски на стене (без букв), край лампы; стол — дерево."""
    o = []
    g = lib.lin_grad([(0, "#eadcbd", 1), (1, "#dccaa4", 1)])
    o.append(f'<rect x="-900" y="-900" width="3200" height="2400" fill="url(#{g})"/>')
    # наброски на стене: листы на кнопках
    for (x, y, w, h, r, sd) in ((150, 380, 200, 250, -6, 51), (420, 300, 170, 210, 4, 52), (880, 360, 220, 270, 7, 53), (1040, 760, 180, 200, -5, 54),
                               (60, 760, 170, 220, 5, 55)):
        P = lib.T(lib.rect_pts(-w / 2, -h / 2, w / 2, h / 2), x, y, rot=r)
        inner = ""
        rs = np.random.RandomState(sd)
        for j in range(3):
            yy = -h * .3 + j * 26
            inner += line(lib.T([(-w * .35, yy), (w * (.05 + .25 * rs.rand()), yy + 3)], x, y, rot=r), 3, PAGE_LN, seed=sd * 5 + j, taper=.3, wmin=.5)
        cc = ("#c0553f", "#3f6fb0", "#5c9a78", "#e0a24a", "#7b6aa0")[sd % 5]
        if sd % 2:
            inner += line(lib.T([(-40 + 30 * math.cos(a) * (1 - a / 14), 50 + 30 * math.sin(a) * (1 - a / 14)) for a in np.linspace(0, 12, 26)], x, y, rot=r),
                          3.4, cc, seed=sd + 70, taper=.3, wmin=.5)
        else:
            inner += line(lib.T([(-50, 70), (-10, 30), (20, 60), (60, 10)], x, y, rot=r), 3.4, cc, seed=sd + 71, taper=.3, wmin=.5)
        o.append(shape(P, PAGE, inner, w=3.6, seed=sd))
        px, py = lib.T([(0, -h / 2 + 14)], x, y, rot=r)[0]
        o.append(shape(ellipse_pts(px, py, 9, 9, 10), "#d9483b", "", w=2.4, seed=sd + 3))
    # стол: столешница под углом и передний край
    top = [(-900, 1330, 1), (1980, 1330, 1), (1980, 1600, 1), (-900, 1600, 1)]
    o.append(shape(top, "#b98a5c", blob([(-900, 1330), (1980, 1330), (1980, 1352), (-900, 1352)], "#cfa274") +
                   "".join(line([(x0, 1380 + 40 * j), (x0 + 260, 1384 + 40 * j)], 2.4, "#9a6c42", seed=600 + j + x0, op=.7)
                           for j, x0 in enumerate((-100, 300, 650, 120, 820))), w=5, seed=605))
    o.append(blob([(-900, 1600), (1980, 1600), (1980, 2400), (-900, 2400)], "#8d6440"))
    o.append(line([(-900, 1602), (1980, 1602)], 5, seed=607, taper=0))
    return "".join(o)


def lamp_glow_small(x, y, r, u):
    """Небольшой круг тёплого света на столе с чёткой границей (от абажура)."""
    g = lib.rad_grad([(0, "#fff1c8", .85 * u), (.8, "#ffe3a0", .55 * u), (1, "#ffe3a0", 0)], x, y, r, r * .32)
    return f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * .32:.1f}" fill="url(#{g})"/>'


def frame05(t):
    T0 = 9.7
    # кот: смотрит на зрителя → вниз на листок → лапа сталкивает листок на «беспорядок» → снова на зрителя → «помогать?» наклон, ухо
    look_down = sm(t, 10.55, 10.8) * (1 - sm(t, 11.25, 11.6))
    reach = sm(t, T_BES - .02, T_BES + .16) * (1 - sm(t, T_BES + .34, T_BES + .62))
    lift = sm(t, 10.66, 10.86) * (1 - sm(t, T_BES + .08, T_BES + .2)) + .55 * sm(t, T_BES + .34, T_BES + .45) * (1 - sm(t, T_BES + .45, T_BES + .62))
    tilt_q = sm(t, T_POM - .06, T_POM + .2)
    st = dict(look=(.55 * look_down + .1 * math.sin(t * .9) * (1 - look_down), .7 * look_down),
              blink=blinks(t, (10.12, 11.72)),
              turn=.18 * look_down - .1 * tilt_q,
              tilt=2.2 * math.sin(t * 1.3) + 8 * look_down + 13 * tilt_q - 4 * bump(t, T_POM + .25, .5),
              ear=2 * math.sin(t * 3.1) + 16 * bump(t, T_POM + .02, .2) - 8 * bump(t, T_POM + .2, .2),
              perk=.35 * tilt_q,
              tail=9 * math.sin(t * 2.3) + 12 * bump(t, T_BES + .1, .5),
              flame_e=1.0 + .9 * bump(t, T_BES + .05, .4) + .4 * bump(t, T_POM, .4),
              reach=reach, reach_lift=lift,
              head_dx=6 * look_down, head_dy=10 * look_down,
              sy=1 - .03 * bump(t, T_BES, .3))
    CK = 2.5
    CXW, CYW = 500.0, 1250.0
    # листок, который сталкивает лапа: лежит справа на верху кучи; паж толкает, лист съезжает с края и падает
    s_rest = (770.0, 1296.0)
    s_x, s_y, s_rot, s_pers = s_rest[0], s_rest[1], 8.0, .42
    push = clamp((t - T_BES) / .16)
    if t > T_BES:
        s_x = s_rest[0] + 70 * ease_out(push, 2)
        s_y = s_rest[1] + 30 * ease_out(push, 2)
    if t > T_BES + .16:
        e = t - T_BES - .16
        land = 1540.0
        tl = math.sqrt(2 * (land - s_rest[1] - 30) / 1500)
        ee = min(e, tl)
        s_x = s_rest[0] + 70 + 150 * ee + 18 * math.sin(ee * 12)
        s_y = s_rest[1] + 30 + 0.5 * 1500 * ee * ee
        s_rot = 8 + 70 * ee + 16 * math.sin(ee * 10)
        s_pers = .42 + .45 * abs(math.sin(ee * 7)) * clamp(1 - (e - tl) * 4 if e > tl else 1)
        if e > tl:          # лёг на стол, чуть подпрыгнул
            s_y -= 10 * math.exp(-8 * (e - tl)) * abs(math.sin(14 * (e - tl)))
    # камера: медленный наезд на морду, поворот на вопросе
    u = sm(t, T0, 12.95)
    z = 1.0 + .3 * u + .04 * bump(t, T_BES, .3) + .05 * bump(t, T_POM, .45)
    head_y = CYW + (1072 - 1306) * CK
    cx = 540 + (CXW - 540) * u + 6 * math.sin(t * 1.1)
    cy = 1010 + (head_y + 120 - 1010) * u
    rot = -.8 + 1.6 * u + 2.4 * tilt_q
    set_ink(z)
    o = [wall_desk(t)]
    o.append(lamp_glow_small(110, 1400, 210, 1.0))
    o.append(props.mug(900, 1500, 1.8, col="blue", steam=1.0, t=t, seed=700))
    o.append(props.paper_pile(500, 1440, 2.2, seed=61, sy=.5, n=13))
    # верхние листы кучи лицом вверх (на них сидит кот)
    o.append(props.paper(330, 1262, 1.7, -18, 140, 170, 31, "sketch", .45))
    o.append(props.paper(520, 1248, 1.8, 6, 140, 170, 32, "lines", .45))
    o.append(props.paper(660, 1272, 1.6, 24, 130, 160, 35, "grid", .45))
    if t < T_BES + .16:
        o.append(props.paper(s_x, s_y, 1.6, s_rot, 125, 160, 34, "sketch", s_pers, col="#f6d9a6"))
    set_ink(z * CK)
    o.append(blob(ellipse_pts(CXW + 10, CYW + 6, 190, 22, 14), "#7a5a3a", .35))
    o.append(catf.draw_f(CXW, CYW, CK, st, t))
    set_ink(z)
    if t >= T_BES + .16:
        o.append(props.paper(s_x, s_y, 1.6, s_rot, 125, 160, 34, "sketch", s_pers, col="#f6d9a6"))
    # знак вопроса штрихами справа от головы
    if t > T_POM:
        qu = clamp((t - T_POM - .02) / .34)
        hop = -12 * math.exp(-6 * max(0, t - T_POM - .36)) * abs(math.sin(2 * math.pi * 2.2 * max(0, t - T_POM - .36)))
        o.append(f'<g transform="translate(175 {560 + hop:.1f}) rotate({6 * math.sin(t * 2.1):.2f})">'
                 f'{props.question_mark(0, 0, 1.9, qu, w=10)}</g>')
    cam = lib.cam(cx, cy, z, rot)
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ───────────────────────────── s17: кот спит на тёплом творческом столе ─────────────────────────────
T_KOT17, T_SPIT, T_TEPL, T_NAP = wt("кот"), wt("спит"), wt("теплее"), wt("напиши")
CAT17 = (300.0, 946.0)
K17 = .55


def cat17(t):
    """Кот на куче бумаг под лампой: топчется → на «кот» поворачивается и ложится клубком → спит → на «Напиши» приоткрывает глаз."""
    x, y = CAT17
    t_down0, t_swap = T_KOT17 - .02, T_KOT17 + .2
    if t < t_swap:
        kn = (t - 41.0) / .32                       # топчется: лапы по очереди, тело покачивается
        ka = 1.0 - sm(t, T_KOT17 - .1, T_KOT17 + .05)
        d = sm(t, t_down0, t_swap)                  # ложится: оседает и поворачивается боком (сжатие по x)
        st = dict(knead=kn, knead_a=ka, look=(.2, .8), tilt=4 * math.sin(2 * math.pi * kn) * ka - 10 * d, blink=.35 + .5 * d,
                  tail=10 * math.sin(t * 2.6) + 18 * d, flame_e=1.0, ear=3 * math.sin(t * 4),
                  sy=1 - .28 * d, sx=1 - .25 * math.sin(math.pi * min(1, d * 1.3)), head_dy=40 * d, rot=3 * math.sin(2 * math.pi * kn) * ka)
        return catf.draw_f(x + 6 * math.sin(2 * math.pi * kn) * ka, y, K17, st, t)
    e = t - t_swap
    settle = 1 - math.exp(-7 * e) * math.cos(2 * math.pi * 2.2 * e)    # клубок оседает с пружинкой
    open_r = sm(t, T_NAP - .02, T_NAP + .16) * (1 - .25 * sm(t, 44.25, 44.45))
    st = dict(eye_r=open_r, look=(-.2, -.1), ear=10 * bump(t, T_NAP + .05, .22) + 6 * bump(t, T_TEPL + .3, .2),
              breath=math.sin(2 * math.pi * (t - t_swap) / 1.9), flame_e=1.0 + .9 * bump(t, T_TEPL, .55) + .3 * math.sin(t * 7),
              flame_k=1.0 + .25 * bump(t, T_TEPL, .55), tail_w=math.sin(t * 2.0))
    sq = 1 + .08 * (1 - settle)
    return (f'<g transform="translate({x} {y}) scale({1 / sq:.4f} {sq * (.86 + .14 * min(1, settle)):.4f}) translate({-x} {-y})">'
            f'{catf.curl(x, y, K17 * .95, st, t)}</g>')


def zzz(t, t0, x, y):
    """Три Z поднимаются по очереди и растут; каждая уходит вверх и исчезает уменьшаясь (без прозрачности)."""
    o = []
    for i in range(3):
        a = t - t0 - i * .38
        if a <= 0:
            continue
        ph = (a % 1.14) / 1.14
        if a > 1.14 and t < t0 + 2.6 and False:
            pass
        u = math.sin(math.pi * ph) ** .6
        xx = x + 46 * ph + 8 * math.sin(a * 4) + 14 * i
        yy = y - 120 * ph - 6 * i
        o.append(props.z_mark(xx, yy, .5 + .35 * ph, u, col="#3F6FB0"))
    return "".join(o)


def frame17(t):
    rb = room.room_bg(t, lamp_on=1.0, flick=0.0, with_door=False)
    warm = sm(t, T_TEPL - .05, T_TEPL + .4)
    o = [rb["bg"], rb["pool"], room.creative_clutter(t)]
    # тёплый круг лампы крепче на «теплее»: чёткий край, небольшой
    px, py, rx, ry = room.LAMP_POOL
    if warm > .01:
        o.append(f'<ellipse cx="{px + 20}" cy="{py + 10}" rx="{rx * .9:.1f}" ry="{ry * 1.1:.1f}" fill="#ffd27a" opacity="{.35 * warm:.3f}"/>')
    o.append(rb["lamp"])
    o.append(props.paper_pile(CAT17[0], CAT17[1] + 10, .78, seed=17, sy=.45, n=9))
    u = sm(t, 41.3, 44.5)
    z = 2.7 + .4 * u + .05 * bump(t, T_NAP, .4)
    set_ink(z * K17 * 1.6)
    o.append(blob(ellipse_pts(CAT17[0] + 6, CAT17[1] - 4, 110, 12, 14), "#6b4422", .3))
    o.append(cat17(t))
    set_ink(z)
    if t > T_SPIT - .02:
        o.append(zzz(t, T_SPIT - .02, CAT17[0] + 105, CAT17[1] - 95))
    if warm > .01:      # тёплые искорки от огонька — штрихи, не пятно
        for i in range(3):
            a = (t - T_TEPL) * 1.3 + i * .33
            ph = a % 1.0
            sx_, sy_ = CAT17[0] - 70 + 18 * i, CAT17[1] - 40 - 60 * ph
            o.append(line([(sx_, sy_), (sx_ + 4, sy_ - 10)], 3, "#f39a3a", seed=1700 + i, taper=.5, wmin=.4) if ph < .8 else "")
    cx = CAT17[0] + 10 + 10 * math.sin(t * .7)
    cy = 850 + 20 * u
    cam = lib.cam(cx, cy, z, .6 - 1.2 * u)
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ───────────────────────────── s18: призыв, рукописное «кот», откат к кадру хука ─────────────────────────────
T_KOT18, T_BARD = wt("кот", 1), wt("бардак")
S18_T0 = 44.1
T_WHIP = T_BARD - .14           # хлёст к кадру хука: пик размытия чуть раньше «бардак»
CAT18 = (40.0, 936.0)
K18 = .62
DIMA18 = (600.0, room.seat_y(1.0))


def hook_world(t):
    """Мир кадра хука s01 (группа A, ext_a/s61a.py): стол-бардак сверху-сбоку, гора бумажек, кружки, провода, лампа."""
    sys.path.insert(0, os.path.join(STORY, "ext_a"))
    import s61a
    tt = .0 + (t - T_WHIP) * .5      # пар и петли проводов живут тихо
    o = [s61a.desk_scene01(tt), s61a.pile01(tt)]
    for j, (bx, by, br, bs) in enumerate(((470, 880, -14, 3), (600, 860, 18, 5), (540, 930, 6, 8))):
        o.append(props.paper(bx, by, 2.2, br + 3 * math.sin(t * 3 + j), 120, 160, bs, ("lines", "sketch", "grid")[j], .6))
    o.append(props.paper_stack(560, 860, 2.1, 6, 9, .35, .6))
    return "".join(o), s61a


def room18(t):
    rb = room.room_bg(t, lamp_on=1.0, with_door=False)
    yb, yf = room.DESK_TOP - room.DESK_D + 30, room.DESK_TOP - 8
    o = [rb["bg"], rb["pool"]]
    o.append(props.paper_pile(-330, yf - 10, 1.05, seed=3) + props.cable_tangle(-210, yf - 26, .8, seed=2, t=t) +
             props.mug(-120, yb + 44, .95, col="blue", seed=1) + props.sticky(-240, yb + 40, .8, rot=8, col="pink", seed=2, mark="star"))
    o.append(rb["lamp"])
    o.append(props.mug(300, yf, 1.0, col="red", steam=.8, t=t, seed=2))
    o.append(props.paper_pile(CAT18[0], CAT18[1] + 14, .8, seed=18, sy=.45, n=8))
    return "".join(o)


def dima18(t):
    """Дима сидит у правого края творческого стола (отражён: смотрит влево к столу), голова к зрителю, спокойная улыбка; ближняя рука на столе."""
    x, y = DIMA18
    nod = bump(t, T_KOT18 + .1, .45)
    ex = dict(people.EXPR["dima"]["calm_smile"], look=(-.15 + .1 * bump(t, T_KOT18 - .1, .5), -.05 + .2 * bump(t, T_KOT18 - .1, .5)),
              closed=blinks(t, (45.35, 46.3)))
    # цели рук в неотражённой системе: x' = 2x − мир
    arms = {"n": ("ik", (2 * x - 330, room.DESK_TOP - 46 + 4 * math.sin(t * 2)), -1), "f": ("ik", (2 * x - 410, room.DESK_TOP - 70), -1)}
    hands = {"n": dict(kind="open", flip=1, dir=(1, .3), curl=(.4, .4, .45, .5), thumb=.4, spread=.08),
             "f": dict(kind="open", flip=1, dir=(1, .35), curl=(.45, .45, .5, .5), thumb=.35)}
    feet = {"n": ((x + 250, room.FL - 50), 0.0), "f": ((x + 200, room.FL - 48), 0.0)}
    fig = people.figure("dima", x, y + 2 * math.sin(t * 2.2), 1.0, ex, lean=.06 + .02 * math.sin(t * 1.7), head_ang=-.12 + .06 * nod,
                        arms=arms, hands=hands, feet=feet, flip=True)
    return fig["svg"]


def frame18(t):
    if t >= T_WHIP:                       # второй половиной хлёста — уже мир хука, камера отъезжает к кадру 0 рилса (петля)
        body, s61a = hook_world(t)
        u = ease_io(clamp((t - T_WHIP) / (47.5 - T_WHIP)))
        e = ease_out(clamp((t - T_WHIP) / .14), 2)
        cx = 560 + (606 - 560) * u
        cy = 900 + (930 - 900) * u
        sc = 1.55 + (1.22 / 1.42 - 1.55) * u
        rot = 1.5 * (1 - u) - 3.4 * u
        blur = 30 * (1 - e)
        dx, dy = props.shake(t, T_BARD, 8, .3, 7)
        g = f'<g transform="translate({-240 * (1 - e):.1f} 0)"><g transform="{lib.cam(cx + dx, cy + dy, sc, rot)}">{body}</g></g>'
        if blur > .5:
            fid = lib.uid("wb")
            lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{blur:.1f} 0"/></filter>')
            g = f'<g filter="url(#{fid})">{g}</g>'
        return g, "#2a2220"
    o = [room18(t)]
    o.append(dima18(t))
    # кот на куче бумаг смотрит на зрителя, на «кот» ушки торчком и огонёк вспыхивает, после — довольный
    hap = sm(t, T_KOT18 + .3, T_KOT18 + .55)
    st = dict(look=(.05 * math.sin(t * .8), 0.0), blink=blinks(t, (44.4, 45.9)), smile=1.0 if hap > .5 else 0.0,
              perk=.6 * bump(t, T_KOT18 - .05, .5), ear=6 * bump(t, T_KOT18 + .05, .3) + 2 * math.sin(t * 3),
              tilt=3 * math.sin(t * 1.3) + 5 * hap, tail=8 * math.sin(t * 2.4), flame_e=1.1 + .8 * bump(t, T_KOT18 + .1, .5),
              sy=1 + .03 * bump(t, T_KOT18, .3))
    u = sm(t, S18_T0, T_WHIP)
    z = 1.42 + .3 * u + .04 * bump(t, T_KOT18 + .3, .4)
    set_ink(z * K18 * 1.5)
    o.append(blob(ellipse_pts(CAT18[0] + 8, CAT18[1] - 2, 120, 12, 14), "#6b4422", .3))
    o.append(catf.draw_f(CAT18[0], CAT18[1], K18, st, t))
    set_ink(z)
    # единственная надпись рилса: пером «кот» над котом, дописано к звуку 44.94
    o.append(hand_kot.kot(t, T_KOT18 - .06, .36, CAT18[0] - 160, 610, 1.75))
    cx = 250 + (120 - 250) * u + 8 * math.sin(t * .9)
    cy = 860 + (780 - 860) * u
    rot = -.6 + .8 * u
    # хлёст на входе плана и уход в хлёст к хуку
    ein = ease_out(clamp((t - S18_T0) / .16), 2)
    eout = ease_in(clamp((t - (T_WHIP - .1)) / .1), 2)
    dxs = 260 * (1 - ein) + 300 * eout
    blur = 28 * (1 - ein) + 30 * eout
    g = f'<g transform="translate({dxs:.1f} 0)"><g transform="{lib.cam(cx, cy, z, rot)}">{"".join(o)}</g></g>'
    if blur > .5:
        fid = lib.uid("wb")
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{blur:.1f} 0"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return g, "#d9c9a8"


FRAMES = {"s05": frame05, "s17": frame17, "s18": frame18}


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body = FRAMES[sid](t)
    bg = "#d9c9a8"
    if isinstance(body, tuple):
        body, bg = body
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')
