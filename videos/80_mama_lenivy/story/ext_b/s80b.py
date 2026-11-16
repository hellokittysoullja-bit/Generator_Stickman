"""Рилс 80 «Мама была права», группа B: Дима, кот, призыв. Время — только из shots.json и voice/words.json (слово по индексу wN).
s04: тёмная комната, Дима растёт в три рывка «лет» (w10), сам затягивает шнур бирки «сам» (w13), смирился «поверил» (w16).
s05: призыв «Телеграм» модулем scripts/story_cta_tg.py: PRESS = W[20].start + 0.12 («Телеграм»), T0 = PRESS − 1.10.
s07: комната вечером, кот на задних лапах поддевает бирку носом: «смотри» (w30) к зрителю, «что»–«было» (w31–w34) дымок из-под
     бирки, «самом» (w36) захлопнулась, бровь.
s08: стол днём, «Дима»–«садился» (w38–w39) садится и закатывает рукав, «дело» (w41) кладёт лист и папку.
s10: «уходил» (w51) отворачивается к телефону, «телефон» (w53) тёплый купол, облако снаружи.
s16: вечер, «да» (w85) кивает облачку, «неприятно» (w86) облачко-клубок на угол стола, берёт ручку.
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
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
import room as R  # noqa: E402
sys.path.insert(0, os.path.join(STORY, "ext_a"))
import s80a as A  # noqa: E402  — комната стола группы A (s09, s11, s17): s08, s10, s16 в той же
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402,F401

INK = lib.INK
W = json.load(open(os.path.join(STORY, "voice", "words.json")))
W = W if isinstance(W, list) else W["words"]
SH = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return W[i]["start"]


def we(i):
    return W[i]["end"]


def T0(sid):
    return SH[sid]["t0"]


def T1(sid):
    return SH[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))


def bump(t, t0, dur):
    u = (t - t0) / dur
    return math.sin(math.pi * u) if 0 < u < 1 else 0.0


def kick(t, t0, dur=.35, freq=2.2, damp=5.0):
    """Затухающий удар после t0: 0 до t0, потом колебание к нулю (для тряски и наездов)."""
    if t < t0:
        return 0.0
    u = (t - t0) / dur
    return math.exp(-damp * u) * math.cos(2 * math.pi * freq * u) if u < 3 else 0.0


def frame_svg(body, cx, cy, s, rot, bg="#05070f", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def soft(x, y, rx, ry, col, op):
    g = lib.rad_grad([(0, col, op), (.55, col, op * .45), (1, col, 0)], x, y, rx, ry)
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#{g})"/>'


def dima_layers(x, y, k, expr, pose, t, u=1.0, age=1.0, feet=None, flip=False, front=None, **kw):
    """Дима двумя проходами: тело (ноги, таз, дальняя рука, тело) → front (бирка и т.п. между телом и ближней рукой) → ближняя рука."""
    back = people.dima80(x, y, k, expr, pose, t, u, age, feet, flip, layers=("legs", "pelvis", "arm_f", "body"), **dict(kw))
    near = people.dima80(x, y, k, expr, pose, t, u, age, feet, flip, layers=("arm_n",), **dict(kw))
    mid = front(back) if front else ""
    back["svg"] = back["svg"] + mid + near["svg"]
    return back


def jerk(t, t0, dur=.14):
    """Рывок 0→1 за dur с перелётом (пружина): для роста в три рывка."""
    if t <= t0:
        return 0.0
    u = (t - t0) / dur
    if u < 1:
        return ease_out(u, 3) * 1.06
    return 1 + .06 * math.exp(-6 * (u - 1)) * math.cos(2 * math.pi * .9 * (u - 1))


# ═══════════════════════════════ s04: Дима растёт в три рывка, сам затягивает шнур, смирился ═══════════════════════════════
def s04(t):
    lib.dyn_begin()
    g1, g2, g3 = ws(10), we(10), ws(11)          # три рывка роста: «лет» начало, конец, «и»
    T_SAM, T_POV = ws(13), ws(16)
    rm = R.turn_dark(t, 1.0)
    o = [rm["bg"]]
    fl = rm["anchors"]["fl"]
    # тени-обвинители из поворота: ещё тычут, дрожат, гаснут после первого рывка
    fade = 1 - ease_io(clamp((t - g1) / (T_SAM - g1)))
    if fade > .01:
        for kind, x, kk, fl_, ph in (("mama", 150, .78, False, 0.0), ("teacher", 960, .74, True, 1.3), ("aunt", 300, .6, False, 2.4)):
            jab = .75 + .25 * math.sin(t * 7.0 + ph)
            hy = fl - 40 - (people.LEG_LEN - 12) * kk * .98
            sh = people.accuser_shadow(kind, x + 30 * (1 - fade) * (-1 if not fl_ else 1), hy, kk, jab, t, col=R.T80_SHADOW, op=.75 * fade,
                                       blur_sd=4.0, flip=fl_, aim=(540, 700))
            o.append(sh["svg"])
    # рост: возраст 0 → .45 → .78 → 1 тремя рывками
    a1, a2, a3 = jerk(t, g1), jerk(t, g2), jerk(t, g3)
    age = .45 * min(a1, 1.0) + .33 * min(a2, 1.0) + .22 * min(a3, 1.0)
    over = max(a1 - 1, 0) + max(a2 - 1, 0) + max(a3 - 1, 0) if t > g1 else 0.0     # перелёт рывка — вытягивается чуть выше
    k = .86
    x = 540.0
    hip_y = people.hip_on_floor(fl - 6, k, age) - 260 * k * over
    # поза: под гирей (сутулится) → выпрямляется с ростом → руки к горлу «сам» → смирился «поверил»
    u_up = clamp(age / .8)
    u_tie = ease_io(clamp((t - (T_SAM - .3)) / .3))
    u_sl = ease_io(clamp((t - (T_POV - .05)) / .4))
    if t < T_SAM - .3:
        pose, pu = ("d80_sag", "d80_stand"), u_up
        ex = "heavy80" if age < .1 else ("grow80" if age < .9 else dict(people.EXPR["dima"]["grow80"], stubble=1.0, bags=True))
    elif t < T_POV - .05:
        pose, pu = ("d80_stand", "d80_tie"), u_tie
        ex = "tie80"
    else:
        pose, pu = ("d80_tie", "d80_slump"), u_sl
        ex = "resign80"
    # затягивает шнур: короче рывками на «сам»
    tug = ease_out(clamp((t - T_SAM) / .22), 2) * .6 + ease_out(clamp((t - (T_SAM + .3)) / .2), 2) * .4
    cord = 150 - 70 * tug
    br = 6 * math.sin(t * 2.4)
    tk = 1.0

    def tag(fig):
        nx, ny = fig["neck"]
        sw = -10 * kick(t, g1, .4, 1.6, 3) + 8 * kick(t, g2, .4, 1.6, 3) - 7 * kick(t, g3, .4, 1.6, 3) + 6 * kick(t, T_POV, .5, 1.2, 3) \
            + 3 * math.sin(t * 3.1) - 4 * kick(t, T_SAM, .3, 2, 4)
        return P.iron_tag(nx + 30 * fig["k"], ny + 46 * fig["k"], tk, sw, cord=cord, seed=4)
    fig = people.dima80(x, hip_y, k, ex, pose, t, pu, age, feet="stand", lean_add=.02 * math.sin(t * 2.4))
    o.append(soft(x, fl + 6, 300, 40, "#000000", .5))
    o.append(fig["svg"])
    o.append(tag(fig))
    if u_tie > .3 and t < T_POV + .2:        # руки держат ветви шнура: шнур от кулаков к петле
        nx, ny = fig["neck"]
        for side in ("f", "n"):
            wx, wy = people.hand_pos(fig, side, 30)
            o.append(line([(nx + (wx - nx) * .2, ny + 14), (wx, wy - 10)], 6 * tk, P.C_CORD, taper=.1, wmin=.7, seed=8420 + (side == "n")))
    hx, hy = fig["head"]
    # штрихи рывка роста: короткие линии у головы на каждом рывке
    for j, g in enumerate((g1, g2, g3)):
        uu = (t - g) / .22
        if 0 < uu < 1:
            for s_ in (-1, 1):
                xx = hx + s_ * 190 * fig["k"]
                o.append(line([(xx, hy + 60 - 120 * uu), (xx, hy + 160 - 120 * uu)], 7 * (1 - uu) + 1, "#9fb4ff", taper=.6, wmin=.2,
                              seed=8400 + j * 2 + (s_ > 0), op=.8 * (1 - uu)))
    # затягивание: штрихи у шеи
    uu = (t - T_SAM) / .3
    if 0 < uu < 1:
        nx, ny = fig["neck"]
        for j in range(3):
            a_ = math.radians(-160 + 50 * j)
            o.append(line([(nx + 70 * math.cos(a_), ny + 70 * math.sin(a_)), (nx + (100 + 40 * uu) * math.cos(a_), ny + (100 + 40 * uu) * math.sin(a_))],
                          6 * (1 - uu) + 1, "#dfe6ff", taper=.6, wmin=.2, seed=8410 + j, op=.85 * (1 - uu)))
    o.append(rm["shade"])
    # камера: поднимается вместе с ростом, толчок на «поверил»
    pk = kick(t, T_POV, .4, 1.0, 4) if t >= T_POV else 0.0
    s = lerp(1.08, 1.02, ease_io(clamp(age))) * (1 + .06 * max(0.0, pk)) + .01 * (t - T0("s04"))
    cy = lerp(1040, 985, ease_io(clamp(age))) + 0 * br
    return frame_svg("".join(o), 540, cy, s, .3 * math.sin(t * 1.3), bg="#070a18")


# ═══════════════════════════════ s07: кот поддевает бирку носом, из-под неё дымок ═══════════════════════════════
def s07(t):
    lib.dyn_begin()
    t0 = T0("s07")
    T_SM, T_CHTO, T_BYLO, T_SAMOM, T_DELE = ws(30), ws(31), we(34), ws(36), ws(37)
    rm = R.room_night(t, 1.0)
    o = [rm["bg"], rm["bed"]]
    by = R.N80_BED_Y
    # Дима сидит на краю кровати, руки на коленях, бирка на груди; смотрит вниз на кота
    k = .8
    hx_, hy_ = 600.0, by - 30
    feet = people.sit_kw(hx_, hy_, k)["feet"]
    feet = {kk: ((v[0][0], R.N80_FL - 10), v[1]) for kk, v in feet.items()}
    ex = dict(people.EXPR["dima"]["resign80"]) if t < T_CHTO else (dict(people.EXPR["dima"]["touch80"], look=(.7, .5)) if t < T_SAMOM + .1
                                                                    else dict(people.EXPR["dima"]["resign80"], look=(.6, .6)))
    arms = {"f": ("ik", (hx_ + 230 * k, hy_ - 30 * k), -1), "n": ("ik", (hx_ + 300 * k, hy_ - 20 * k), -1)}
    fig = people.dima80(hx_, hy_, k, ex, "d80_sit", t, age=1.0, feet=feet, arms=arms, lean_add=.08 + .02 * math.sin(t * 2.2),
                        hands={"f": {"dir": (.4, 1), "curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (.4, 1), "curl": (.4, .4, .45, .5), "thumb": .4}})
    o.append(fig["svg"])
    nx, ny = fig["neck"]
    tag_xy = (nx + 30 * k, ny + 46 * k)
    tk = .95
    cord = 120.0
    lift = ease_io(clamp((t - T_CHTO) / (T_BYLO - T_CHTO)))          # бирка приоткрывается
    lift *= (1 - ease_in(clamp((t - T_SAMOM) / .1), 2))
    slam = kick(t, T_SAMOM + .1, .45, 2.6, 5) if t >= T_SAMOM + .1 else 0.0
    sw = -42 * lift + 14 * slam + 2.5 * math.sin(t * 2.6)

    def tag_pt(lx, ly, a):
        r = math.radians(a)
        return (tag_xy[0] + tk * (lx * math.cos(r) - ly * math.sin(r)), tag_xy[1] + tk * (lx * math.sin(r) + ly * math.cos(r)))
    # кот: идёт по кровати справа → встаёт на задние лапы, нос под нижний правый угол бирки → отпускает, садится, бровь
    ck = .7
    u_up = ease_io(clamp((t - (T_SM - .32)) / .26))
    u_dn = ease_io(clamp((t - (T_SAMOM + .02)) / .22))
    up = u_up * (1 - u_dn)
    sy = 1 + .24 * up
    corner = tag_pt(95, cord + 172, sw)
    nose_dy = (1072 + 40 - CAT.CBOT) * ck * sy          # нос относительно точки опоры кота
    stand_x = corner[0] + 70
    cx = lerp(stand_x + 300, stand_x, ease_out(clamp((t - (t0 - .2)) / .55), 2))
    cy = by - 10
    if up > .5:
        cx = lerp(cx, corner[0] + 40, clamp((lift - .0) * 2))
    st = {"paw": .95 * up, "paw_l": .95 * up, "paw_dx": 14, "paw_l_dx": 14, "sy": sy, "perk": up,
          "look": (0.0, 0.0) if T_SM <= t < T_CHTO else ((-.8, -.5) if t < T_SAMOM else (0.0, 0.0)),
          "tilt": -14 * lift + (8 if t > T_SAMOM + .15 else 0), "rot": -5 * up - 6 * lift,
          "tail": 10 * math.sin(t * 3.2)}
    if t > T_SAMOM + .15:
        st.update(smug=1.0, look=(.1, 0.0))
    walking = t < t0 + .35
    cat_svg = people.cat_walk(cx, cy, ck, t, st) if walking else CAT.draw(cx, cy, ck, st, t)
    o.append(cat_svg)
    o.append(P.iron_tag(*tag_xy, tk, sw, cord=cord, seed=4))
    # дымок из-под приподнятой бирки: из щели между биркой и грудью
    if lift > .05:
        gap = tag_pt(20, cord + 150, sw * .35)
        o.append(soft(gap[0] - 20, gap[1] - 30, 150 * lift, 110 * lift, "#b8c2d4", .4 * lift))
        o.append(P.smoke_curls(gap[0] - 30, gap[1] - 10, 2.0, lift, t, seed=7, col="#c3cad8", n=3))
        o.append(P.smoke_curls(gap[0] + 50, gap[1] - 20, 1.3, lift * .8, t + .7, seed=8, col="#aeb6c6", n=2))
    # хлоп: штрихи удара на «самом»
    uu = (t - (T_SAMOM + .1)) / .3
    if 0 < uu < 1:
        cxw, cyw = P.iron_tag_center(*tag_xy, tk, 0, cord=120)
        for j in range(5):
            a_ = math.radians(-170 + 45 * j)
            r0, r1 = 120 + 30 * uu, 160 + 50 * uu
            o.append(line([(cxw + r0 * math.cos(a_), cyw + r0 * math.sin(a_)), (cxw + r1 * math.cos(a_), cyw + r1 * math.sin(a_))], 7 * (1 - uu) + 1,
                          "#fff3dc", taper=.6, wmin=.2, seed=8500 + j, op=.9 * (1 - uu)))
    o.append(rm["light"])
    # камера: наезд к бирке, толчок на «деле»
    u = ease_io(clamp((t - (t0 - .2)) / (T1("s07") - t0 + .4)))
    pk = kick(t, T_DELE, .4, 1.0, 4) if t >= T_DELE else 0.0
    shk = kick(t, T_SAMOM + .1, .25, 7, 6)
    s = lerp(1.05, 1.3, u) * (1 + .07 * max(0.0, pk))
    ccx = lerp(560, tag_xy[0] + 90, u) + 10 * shk
    ccy = lerp(940, tag_xy[1] + 90, u) - 6 * shk
    return frame_svg("".join(o), ccx, ccy, s, lerp(-.5, .4, u) + .5 * shk, bg="#1a0c18")


def blink(t, seed=0.0, period=3.3):
    p = (t + seed) % period
    return math.sin(math.pi * p / .14) if p < .14 else 0.0


def folder(x, y, k=1.0, rot=0.0, seed=0):
    """Толстая папка дела сбоку-сверху (ЦЕНТР низа): картонные корки, пачка листов, тесёмка; без букв."""
    sd = 8600 + seed
    o = [shape([(-170, 0, 1), (-176, -22), (170, -26), (176, 0, 1)], "#c08a4c", blob([(-170, -6), (170, -8), (176, 0), (-170, 0)], "#9a6a34", .8), w=4.2,
               seed=sd)]
    for i in range(5):        # торцы листов
        yy = -26 - 9 * i
        o.append(shape([(-164 + 2 * (i % 2), yy + 2, 1), (-162, yy - 8), (166, yy - 9), (168 - 2 * (i % 2), yy + 2, 1)], "#f4efe4", "", w=2.6, seed=sd + 1 + i))
    o.append(shape([(-174, -70, 1), (-180, -96), (172, -100), (178, -72, 1)], "#d29a58", blob([(-174, -76), (178, -78), (178, -72), (-174, -70)], "#a8743a", .7),
                   w=4.2, seed=sd + 8))
    o.append(line([(30, -100), (34, -72), (40, -20), (44, 0)], 5, "#8a3c2a", taper=0, wmin=1, seed=sd + 9))
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{"".join(o)}</g>'


def dust_puffs(x, y, t, t_hit, k=1.0, col="#efe4cf", seed=0):
    u = (t - t_hit) / .45
    if not 0 < u < 1:
        return ""
    o = ""
    for j, sx in enumerate((-1, 1)):
        for i in range(3):
            cx = x + sx * (60 + 70 * i + 90 * ease_out(u, 2)) * k
            cy = y - (10 + 18 * i) * k * (1 - u * .4)
            r = (14 + 6 * i) * k * (.6 + .6 * u)
            o += blob(ellipse_pts(cx, cy, r, r * .8, 12), col, .7 * (1 - u))
    return o


# ═══════════════════════════════ s08: днём садится за стол, рукава, кладёт лист и папку ═══════════════════════════════
# Комната, стол, стул, Дима (HIP, SC), лист, кружка и лампа — как у группы A в s09 (следующий план), чтобы склейка была в том же месте.
def s08(t):
    lib.dyn_begin()
    t0, t1 = T0("s08"), T1("s08")
    T_SAD, T_DELO = ws(39), ws(41)
    bg, desk = A.desk_room(t, "day")
    hx, hy0 = A.HIP
    k = A.SC
    # садится: таз опускается на стул к «садился»
    sit_u = ease_out(clamp((t - (t0 - .2)) / (T_SAD + .12 - (t0 - .2))), 2)
    hy = hy0 - 130 * (1 - sit_u) + 8 * kick(t, T_SAD + .12, .3, 2.0, 5)
    pk = people.pose_kw("d80_sit", hx, hy, k)
    arms, hands = dict(pk["arms"]), dict(pk["hands"])
    f_w = (hx + 250 * k, hy - 200 * k)
    arms["f"] = ("ik", f_w, -1)
    roll = clamp((t - (T_SAD - .05)) / .3)
    t_grab = T_DELO - .28
    t_reach = T_SAD + .25
    DX, DY = A.DESK_X, A.DESK_Y
    fx0, fy0 = DX - 150, DY - 30            # папка лежит у его рук
    land = (DX - 120, DY - 40)
    lift_pt = (DX - 160, DY - 170)
    if t < t_grab:
        fpos, frot = (fx0, fy0), 0.0
    elif t < T_DELO:
        e = (t - t_grab) / (T_DELO - t_grab)
        if e < .55:
            fpos = lerp2((fx0, fy0), lift_pt, ease_out(e / .55, 2))
            frot = -10 * ease_out(e / .55, 2)
        else:
            e2 = ease_in((e - .55) / .45, 2)
            fpos = lerp2(lift_pt, land, e2)
            frot = -10 * (1 - e2)
    else:
        fpos, frot = (land[0], land[1] + 2 * kick(t, T_DELO, .3, 2.2, 5)), 0.0
    if 0 < roll < 1:
        q = .5 - .5 * math.cos(2 * math.pi * 2 * roll)
        arms["n"] = ("ik", lerp2((f_w[0] + 16, f_w[1] - 5), (f_w[0] - 75, f_w[1] - 32), q), -1)
        hands["n"] = {"dir": (1, .3), "curl": (.62, .66, .7, .74), "thumb": .6}
    elif roll >= 1:
        rest = (hx + 290 * k, hy - 205 * k)
        grip = (fpos[0] - 70, fpos[1] - 50)
        if t < t_reach:
            tgt = rest
        elif t < t_grab:
            tgt = lerp2(rest, grip, ease_io(clamp((t - t_reach) / (t_grab - t_reach))))
        elif t < T_DELO + .15:
            tgt = grip
        else:
            tgt = lerp2(grip, rest, ease_io(clamp((t - (T_DELO + .15)) / .3)))
        arms["n"] = ("ik", tgt, -1)
        hands["n"] = {"dir": (.7, .7), "curl": (.45, .5, .55, .6), "thumb": .5}
    ex = dict(people.EXPR["dima"]["det80"], look=(.6, .1) if t < T_SAD else (.6, .45))
    ex["closed"] = blink(t, .7)
    kw = dict(arms=arms, hands=hands, feet=people.sit_kw(hx, hy, k)["feet"], lean_add=.03 * (1 - sit_u) + .02 * math.sin(t * 2.0))
    fb = people.dima80(hx, hy, k, ex, "d80_sit", t, age=1.0, layers=("legs", "pelvis"), **kw)
    fm = people.dima80(hx, hy, k, ex, "d80_sit", t, age=1.0, layers=("arm_f", "body"), **kw)
    fn = people.dima80(hx, hy, k, ex, "d80_sit", t, age=1.0, layers=("arm_n",), **kw)
    fk = .55 * (1 + .04 * (kick(t, T_DELO, .3, 2.2, 5) if t >= T_DELO else 0))
    props_ = P.paper(DX - 140, DY - 70, 1.15, -4, 220, 280, seed=9, kind="lines", sy=.42)       # тот же лист, что в s09
    props_ += P.mug(DX + 250, DY - 60, .8, col="blue", coffee=True, steam=.6, t=t, seed=9)
    props_ += P.lamp_desk(DX + 150, DY - 110, .9, on=0.0, seed=9)
    props_ += folder(fpos[0], fpos[1], fk, frot)
    props_ += dust_puffs(land[0], land[1], t, T_DELO, .8)
    uu = (t - T_DELO) / .25
    if 0 < uu < 1:
        for j in range(4):
            a_ = math.radians(-160 + 46 * j)
            r0, r1 = 120 + 30 * uu, 160 + 50 * uu
            props_ += line([(land[0] + r0 * math.cos(a_), land[1] - 40 + r0 * .6 * math.sin(a_)),
                            (land[0] + r1 * math.cos(a_), land[1] - 40 + r1 * .6 * math.sin(a_))], 7 * (1 - uu) + 1, INK, taper=.6, wmin=.2,
                           seed=8620 + j, op=.8 * (1 - uu))
    body = bg + A.chair(hx, hy0 + 20) + fb["svg"] + desk + fm["svg"] + props_ + fn["svg"]
    u = ease_io(clamp((t - (t0 - .2)) / (t1 - t0 + .4)))
    shk = kick(t, T_DELO, .25, 6, 6)
    s = lerp(1.24, 1.36, u) * (1 + .04 * bump(t, T_DELO, .3))
    cx = lerp(600, 560, u) + 6 * shk
    cy = lerp(990, 930, u) + 4 * shk
    return frame_svg(body, cx, cy, s, lerp(.5, -.3, u) + .4 * shk, bg="#f2e6cf")


def outside_dome(svg_, x, y, r):
    """Обрезать рисунок куполом: видно только то, что снаружи полукруга радиуса r с основанием (x, y)."""
    if r < 4:
        return svg_
    cid = lib.uid("od")
    d = (f"M-3000 -3000 H4000 V4000 H-3000 Z M{x - r:.1f} {y:.1f} A{r:.1f} {r * .95:.1f} 0 0 1 {x + r:.1f} {y:.1f} Z")
    lib.DEFS.append(f'<clipPath id="{cid}" clipPathUnits="userSpaceOnUse"><path d="{d}" clip-rule="evenodd"/></clipPath>')
    return f'<g clip-path="url(#{cid})">{svg_}</g>'


# ═══════════════════════════════ s10: отворачивается в телефон, тёплый купол ═══════════════════════════════
# Начало — как конец s09 группы A (серое облако над головой, мир выцвел), конец — как начало s11 (Дима с телефоном у груди под куполом
# DOME/DOME_K, облако над головой внутри купола: оно растает в s11, а снаружи сядет другое).
def s10(t):
    lib.dyn_begin()
    t0, t1 = T0("s10"), T1("s10")
    T_UH, T_TEL = ws(51), ws(53)
    bg, desk = A.desk_room(t, "day")
    k = A.SC
    hx0, hy = A.HIP
    br = 3 * math.sin(t * 2.3)
    turn = ease_out(clamp((t - (T_UH - .06)) / .26), 2)          # отворачивается от листа к телефону
    raise_u = ease_out(clamp((t - (T_UH + .05)) / .3), 2)
    dome_u = ease_out(clamp((t - (T_TEL - .04)) / .42), 2)
    hx = lerp(hx0, 300.0, turn)
    DX, DY = A.DESK_X, A.DESK_Y
    if t < T_UH + .05:
        expr = dict(people.EXPR["dima"]["gloom"], brows="worry", lid=.75, look=lerp2((-.2, -.5), (-.6, .2), turn))
        fb = A.seated(t, expr, "write", .16 - .2 * turn, .05, layers=("legs", "pelvis"), shrug=.5, x=hx)
        fig = A.seated(t, expr, "write", .16 - .2 * turn, .05 - .15 * turn, layers=("arm_f", "body", "arm_n"), shrug=.5, x=hx)
        dsvg, dbg = fig["svg"], fb["svg"]
        hd = fig["head"]
        ph = None
    else:
        expr = dict(people.EXPR["dima"]["screen74"], look=(.45, .5), bags=True)
        if t < T_TEL + .1:
            expr.update(brows="worry", mouth="flat")
        else:
            expr.update(mouth="smile", smile=.3 * dome_u)
        fig = people.dima_phone(hx, hy + br, k, expr, "phone_chest74", phone_k=1.45 * k * HEIGHT_D * (.55 + .45 * raise_u), thumb=raise_u, t=t,
                                feet=people.sit_kw(hx, hy + br, k)["feet"], lean_add=.04 - .06 * (1 - raise_u) + .02 * math.sin(t * 1.4),
                                shrug=.5 - .15 * dome_u)
        dsvg, dbg = fig["svg"], ""
        hd = fig["head"]
        ph = fig["phone"]
    props_ = P.paper(DX - 140, DY - 70, 1.15, -4, 220, 280, seed=9, kind="lines", sy=.42)
    props_ += P.mug(DX + 250, DY - 60, .8, col="blue", coffee=True, seed=9)
    props_ += P.lamp_desk(DX + 150, DY - 110, .9, on=0.0, seed=9)
    props_ += P.pen(DX - 20, DY - 46, .55, 86, seed=9)              # ручка укатилась в s09
    scene = bg + A.chair(hx0, hy + 20) + dbg + desk + props_ + dsvg
    R_ = P.dome_r(A.DOME_K, dome_u) * (1 + .02 * math.sin(t * 5.3))
    o = [f'<g {P.desat(.75 - .05 * dome_u)}>{scene}</g>']
    if R_ > 4:
        dpts = [(A.DOME[0] + R_ * math.cos(math.radians(q)), A.DOME[1] - R_ * .95 * math.sin(math.radians(q))) for q in range(0, 181, 6)]
        cid = lib.clip_of(dpts)
        o.append(f'<g clip-path="url(#{cid})">{scene}</g>')
        o.append(P.phone_dome(A.DOME[0], A.DOME[1], A.DOME_K, dome_u, t, seed=11))
    if ph is not None:
        w = fig["wrist"]["n"]
        o.append(P.glow(w[0] - 10, w[1] - 90, 130, .2 + .25 * dome_u, "#FFE7A3"))
    # облако: над головой (как в конце s09) → купол прижимает его ниже и меньше, дождь стихает (как в начале s11)
    c0 = (hd[0] + 30 + 10 * math.sin(t * 1.3), hd[1] - 270 + 8 * math.sin(t * 1.9))
    c1 = (hd[0] + 20, hd[1] - 190)
    cl = lerp2(c0, c1, dome_u)
    o.append(P.gloom_cloud(cl[0], cl[1], lerp(1.15, .8, dome_u), t, rain=lerp(1.0, .3, dome_u), zap=(1 - dome_u) * (.6 + .4 * math.sin(t * 7)), seed=9))
    # вспышка раскрытия купола
    uu = (t - T_TEL) / .35
    if ph is not None and 0 < uu < 1:
        for j in range(7):
            a_ = math.radians(195 + 25 * j)
            r0 = 120 + 420 * ease_out(uu, 2)
            o.append(line([(ph[0] + r0 * math.cos(a_), ph[1] + r0 * math.sin(a_)), (ph[0] + (r0 + 55) * math.cos(a_), ph[1] + (r0 + 55) * math.sin(a_))],
                          8 * (1 - uu) + 1, "#ffd27a", taper=.6, wmin=.2, seed=8700 + j, op=.9 * (1 - uu)))
    # камера: рывок за поворотом на «уходил» (со смазом), наезд в свет экрана на «телефон» → к кадру начала s11 (1.5, 390, 1000)
    jerk_u = ease_out(clamp((t - T_UH) / .18), 3)
    shk = kick(t, T_UH + .06, .3, 3, 5)
    push_c = ease_io(clamp((t - (T_TEL - .1)) / (t1 + .2 - T_TEL)))
    s = lerp(1.46, 1.4, jerk_u) + .1 * push_c
    cx = lerp(520, 420, jerk_u) - 30 * push_c + 16 * shk
    cy = lerp(850, 960, jerk_u) + 40 * push_c
    rot = lerp(-.6, .8, jerk_u) - 1.4 * shk
    body = "".join(o)
    blur = 24 * bump(t, T_UH - .02, .2)
    if blur > .5:
        fid = lib.uid("jb")
        lib.DEFS.append(f'<filter id="{fid}" x="-10%" y="-5%" width="120%" height="110%"><feGaussianBlur stdDeviation="{blur:.1f} 0"/></filter>')
        body = f'<g filter="url(#{fid})">{body}</g>'
    return frame_svg(body, cx, cy, s, rot, bg="#e8dfcc")


HEIGHT_D = 1.0

# ═══════════════════════════════ s16: «да» — кивает облачку, оно клубком садится на угол стола ═══════════════════════════════
# Вечерняя комната, лампа, листы, место клубка и ручка — как в s17 группы A (следующий план).
def s16(t):
    lib.dyn_begin()
    t0, t1 = T0("s16"), T1("s16")
    T_DA, T_NEP = ws(85), ws(86)
    bg, desk = A.desk_room(t, "evening")
    DX, DY = A.DESK_X, A.DESK_Y
    SX, SY = DX - 120, DY - 72
    U0 = .12          # s17 начинается с этой доли первой строки
    tip = P.scribble_tip(SX, SY, 1.2, U0, -4, w=240, h=320, sy=.6)
    # руки: ладонь на груди → «неприятно» ладонь уходит, рука берёт ручку со стола и подносит к листу
    take = ease_io(clamp((t - (T_NEP + .3)) / .45))
    grab = ease_io(clamp((t - (T_NEP + .75)) / .3))
    hx, hy = A.HIP
    k = A.SC
    pen_rest = (SX + 120, SY + 34)
    wr_write = (tip[0] - 52, tip[1] - 28)
    wr_grab = (pen_rest[0] - 40, pen_rest[1] - 40)
    if take < 1:
        tgt = lerp2((hx + 215 * k, hy - 225 * k), wr_grab, take)
    else:
        tgt = lerp2(wr_grab, wr_write, grab)
    arms = {"n": ("ik", tgt, -1), "f": ("ik", (SX + 70 + 4 * math.sin(t * 2), SY - 105), -1)}
    hn = {"dir": (-.75, -.45), "curl": (.05, .05, .1, .15), "spread": .1, "thumb": .1} if take < .5 else {"curl": (.55, .6, .7, .75), "thumb": .5, "dir": (.85, .5)}
    hands = {"n": hn, "f": {"curl": (.35, .4, .45, .5), "thumb": .35, "dir": (.9, .55)}}
    nod = .16 * bump(t, T_DA - .02, .32) + .1 * bump(t, T_DA + .3, .3)
    if t < T_DA - .05:
        expr = dict(people.EXPR["dima"]["calm80"])
    elif t < T_NEP + .3:
        expr = dict(people.EXPR["dima"]["say_yes80"] if t < we(85) + .05 else people.EXPR["dima"]["yes80"])
    else:
        expr = dict(people.EXPR["dima"]["write80"], look=lerp2((.4, -.3), (.6, .7), take))
    expr["closed"] = blink(t, 1.3) if t < T_DA - .1 or t > T_NEP + .5 else 0.0
    pose = "write"
    fig_b = A.seated(t, expr, pose, .06, -.12 * (1 - take) + nod, layers=("legs", "pelvis"))
    fig = A.seated(t, expr, pose, .06, -.12 * (1 - take) + nod, arms=arms, hands=hands, layers=("arm_f", "body"))
    arm = A.seated(t, expr, pose, .06, -.12 * (1 - take) + nod, arms=arms, hands=hands, layers=("arm_n",))
    lamp = P.lamp_desk(DX + 300, DY - 130, 1.0, on=1.0, seed=17)
    sheets = P.scribble_sheet(SX, SY, 1.2, U0, -4, seed=172, w=240, h=320, sy=.6)
    # облачко: над головой → «неприятно» съёживается в клубок и по дуге садится на угол стола, как зверёк
    hd = fig["head"]
    top = (hd[0] + 30 + 8 * math.sin(t * 1.4), hd[1] - 250 + 6 * math.sin(t * 2.1))
    corner = (DX + 105, DY - 100)
    shr = ease_io(clamp((t - T_NEP) / .3))
    fly = clamp((t - (T_NEP + .12)) / .42)
    e = ease_io(fly)
    cpos = lerp2(top, corner, e)
    cpos = (cpos[0], cpos[1] - 160 * math.sin(math.pi * e))
    land = kick(t, T_NEP + .54, .4, 2.2, 5) if t >= T_NEP + .54 else 0.0
    cpos = (cpos[0], cpos[1] + 10 * land + (4 * math.sin(t * 2) if fly >= 1 else 0))
    ball = P.gloom_cloud(cpos[0], cpos[1], 1.15, t, rain=.25 * (1 - shr), shrink=shr, seed=17, wob=1 + .5 * abs(land))
    # «да»: маленький кивок-штрих у головы
    marks = ""
    uu = (t - T_DA) / .35
    if 0 < uu < 1:
        for j in range(2):
            x0 = hd[0] + 150 + 18 * j
            marks += line([(x0, hd[1] - 30 + 30 * uu), (x0 + 6, hd[1] + 10 + 30 * uu)], 5 * (1 - uu) + 1, INK, taper=.6, wmin=.2, seed=8800 + j, op=.7 * (1 - uu))
    # ручка: лежит у листа → в руке
    if grab < .05:
        pen_svg = P.pen(pen_rest[0], pen_rest[1], .62, 80 + 3 * math.sin(t * 1.2) * (take > 0), seed=17)
    else:
        wr = arm["wrist"]["n"]
        pen_svg = P.pen(wr[0] + 26, wr[1] - 34, .62, lerp(80, 25, grab), seed=17)
    o = [bg, A.chair(hx, hy + 20), fig_b["svg"], desk, lamp, sheets, ball, fig["svg"], pen_svg, arm["svg"], marks,
         P.glow(DX + 160, DY - 90, 420, .55, "#FFD98A")]
    # камера: лёгкий наезд к облачку → к кадру начала s17 (620, 1060, 1.74)
    pu = ease_io(clamp((t - (t0 - .2)) / (t1 - t0 + .4)))
    s = lerp(1.38, 1.7, pu)
    cx = lerp(470, 610, pu)
    cy = lerp(860, 1050, pu)
    return frame_svg("".join(o), cx, cy, s, .3 * math.sin(t * 1.2))


# ═══════════════════════════════ s05: призыв «Телеграм» ═══════════════════════════════
def s05(t):
    import story_cta_tg as tg
    press = ws(20) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=COMMON)


def frame(sid, t):
    return globals()[sid](t)
