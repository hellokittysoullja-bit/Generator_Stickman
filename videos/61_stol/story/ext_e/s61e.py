"""Рилс 61 «стол», группа E: s14 (творческий стол: садится, рисует маркером, лампочки, наброски взлетают, хлоп ладонью),
s15 (чистый стол: сосредоточен, галочки в чекбоксах, блик), s16 (общий план: два стола, Дима между ними на крутящемся стуле).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Комната — common/room.py, люди — common/people.py, предметы — common/props.py.
Дима сидит на стуле в точке room.MID_X: к творческому столу (слева) — лицом влево (flip), к чистому (справа) — лицом вправо."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, smooth, spring  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


T_DIMA, T_PRIDUM, T_TVOR, T_STOLOM = wt(60), wt(61), wt(63), wt(64)
T_PLANU, T_CHISTYM = wt(68), wt(71)
T_DVA, T_STOLA, T_STYDA = wt(72), wt(73), wt(75)

BS = 1.0
HX = R.MID_X
HY = R.seat_y(BS)
GK = .95


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def lerp(a, b, u):
    return a + (b - a) * u


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink(t, times, dur=.16):
    v = 0.0
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def shake(t, t0, amp, dur=.4, f_=34.0):
    if t < t0 or t > t0 + dur:
        return 0.0, 0.0
    d = (1 - (t - t0) / dur) ** 2
    return amp * d * math.sin((t - t0) * f_ * 6.28), amp * .7 * d * math.cos((t - t0) * f_ * 5.1)


def expr_of(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.update(kw)
    return e


def dima(x, y, *, flip, expr, lean=0.0, head_ang=0.0, arms, hands, layers=None, feet_dx=290.0):
    """Сидящий Дима (таз в (x, y)), руки — цели в МИРЕ (уже с учётом flip). Возвращает результат people.figure."""
    def un(p):
        return (2 * x - p[0], p[1]) if flip else p
    A = {}
    for k, a in arms.items():
        A[k] = ("ik", un(a[1]), a[2]) if a[0] == "ik" else a
    feet = {"n": ((x + feet_dx, R.FL - 50), 0.0), "f": ((x + feet_dx - 50, R.FL - 48), 0.0)}
    return people.figure("dima", x, y, BS, expr, lean=lean, head_ang=head_ang, arms=A, hands=hands, feet=feet, flip=flip, layers=layers)


def marker_in_fist(wrist, side, tilt=0.0, col="#e8735a", seed=930):
    """Маркер наконечником вниз в кулаке: пальцы обхватывают корпус (большой палец за ним). side +1 — кисть справа от маркера.
    Возвращает (back, marker, front, tip)."""
    Rm = 12.0
    cx = wrist[0] - side * (Rm + 44 * GK)
    cy = wrist[1] + 8
    a = math.radians(90 + tilt)
    tip = (cx + 70 * math.cos(a), cy + 70 * math.sin(a))
    mk = PR.marker(cx + 8 * math.cos(a), cy + 8 * math.sin(a), .9, rot=90 + tilt, col=col, cap=False)
    back, front = people.grip_svg("dima", (cx, cy), Rm, side, k=GK * .82, h=62, seed=seed)
    return back, mk, front, tip


def room_layers(t, *, fly=0.0, pop=0.0, jump=0.0, lamp_on=1.0, checks=0, cu=0.0, shine=0.0, flick=0.0):
    """Слои комнаты для сидящего у стола: (behind = всё до ног Димы, front = передние кромки и ножки столов, items = предметы на столах)."""
    cr = R.desk(*R.CREATIVE, kind="creative")
    cl = R.desk(*R.CLEAN, kind="clean")
    lamp = R.desk_lamp(lamp_on, flick)
    behind = ['<rect x="-1200" y="2100" width="4000" height="900" fill="#c38c5a"/>', R.wall_floor(), R.window(t), R.sketches(t, fly), R.stickers(t, pop),
              R.clean_wall(t), R.door(t, 0.0), cr["back"], cl["back"]]
    if shine > 0:
        behind.append(desk_shine(shine))
    front = [cr["front"], cr["legs"], cl["front"], cl["legs"]]
    items = [lamp["pool"], R.creative_clutter(t, jump=jump), R.clean_top(t, checks=checks, u=cu), lamp["lamp"]]
    return "".join(behind), "".join(front), "".join(items)


def desk_shine(u):
    """Блик по верху чистого стола: светлая косая полоса пробегает слева направо (u 0…1), обрезана формой столешницы."""
    x0, x1 = R.CLEAN
    y = R.DESK_TOP
    top = [(x0 + 22, y - R.DESK_D, 1), (x1 - 22, y - R.DESK_D, 1), (x1, y, 1), (x0, y, 1)]
    c = lib.clip_of(top)
    bx = lerp(x0 - 200, x1 + 200, ease_io(u))
    a = math.sin(math.pi * clamp(u)) * .75
    band = f'<path d="M{bx - 60:.1f} {y + 10}L{bx + 30:.1f} {y - R.DESK_D - 10}L{bx + 110:.1f} {y - R.DESK_D - 10}L{bx + 20:.1f} {y + 10}Z" fill="#ffffff" opacity="{a:.3f}"/>'
    band += f'<path d="M{bx + 70:.1f} {y + 10}L{bx + 160:.1f} {y - R.DESK_D - 10}L{bx + 186:.1f} {y - R.DESK_D - 10}L{bx + 96:.1f} {y + 10}Z" fill="#ffffff" opacity="{a * .7:.3f}"/>'
    return f'<g clip-path="url(#{c})">{band}</g>'


def chair(spin=0.0, side=1, dy=0.0, dx=0.0):
    return R.swivel_chair(HX + dx, HY + 40 + dy, 1.0, spin=spin, side=side)


# ═══════════════════════════════ s14: творческий стол ═══════════════════════════════
SCRIBBLE = [(-46, 14), (-30, -10), (-8, 12), (10, -14), (28, 8), (40, -12), (20, -26), (-6, -30), (-30, -22), (-40, 0), (-20, 24), (8, 22),
            (34, 22), (46, 0)]


def scribble(cx, cy, u, seed=0):
    """Рисунок маркером на листе: петли растут (u 0…1), цветные, без букв."""
    if u <= 0:
        return ""
    S = lib.sample(SCRIBBLE, False, 2.0)
    n = max(2, int(len(S) * clamp(u)))
    p = [(cx + float(a), cy + float(b) * .62) for a, b in S[:n]]
    o = line(p, w=6.5, color="#e8735a", taper=.15, wmin=.6, seed=7000 + seed)
    if u > .6:
        k = (u - .6) / .4
        o += f'<circle cx="{cx + 30:.1f}" cy="{cy - 10:.1f}" r="{9 * k:.1f}" fill="#f6d55c" stroke="{INK}" stroke-width="2"/>'
    return o


def frame14(t):
    a = 32.6
    # хлёст: камера влетает сбоку и быстро тормозит, потом наезд на Диму
    wi = ease_out(clamp((t - a) / .3), 3)
    push = sm(t, a + .3, 35.9)
    s = lerp(1.0, 1.32, push) - .12 * (1 - wi)
    cx = lerp(470, 470, push) + 260 * (1 - wi) + 5 * math.sin(t * 1.3)
    cy = lerp(800, 760, push) + 4 * math.sin(t * 1.1)
    rot = lerp(-1.5, .6, push) + 3 * (1 - wi)
    sh = shake(t, T_STOLOM + .02, 16, .45)
    cx += sh[0]
    cy += sh[1]
    set_ink(s)
    # Дима подъезжает на стуле (полустоя) и плюхается на «Дима»
    roll = sm(t, a, T_DIMA - .05)
    dx = lerp(190, 0, roll)
    sit = clamp((t - T_DIMA) / .18)
    up = (1 - ease_in(sit, 2)) * 70 if t < T_DIMA + .18 else 0.0
    sq = -16 * spring(t - (T_DIMA + .16), 3.0, 7.0) * math.exp(-4 * max(0.0, t - T_DIMA - .16)) if t > T_DIMA + .16 else 0.0
    hx, hy = HX + dx, HY - up - sq
    beh, front, items = room_layers(t, fly=sm(t, T_TVOR - .05, T_TVOR + .75), jump=18 * bump(t, T_STOLOM, .3), flick=.5 + .5 * math.sin(t * 7))
    # лист для рисования под рукой
    pcx, pcy = 300.0, R.DESK_TOP - 50
    paper = PR.paper(pcx, pcy, 1.0, rot=-6, w=150, h=170, seed=11, kind="blank", sy=.5)
    du = clamp((t - T_PRIDUM) / .85)
    paper += scribble(pcx - 4, pcy, du)
    # руки: дальняя на столе придерживает лист; ближняя рисует (с маркером), потом взлетает и хлопает
    t_up0, t_slap = T_STOLOM - .32, T_STOLOM
    draw_ph = (t - T_PRIDUM) * 9.0
    if t < T_PRIDUM:
        near = (lerp(390, 330, sm(t, T_DIMA, T_PRIDUM)), lerp(1000, 930, sm(t, T_DIMA, T_PRIDUM)))
    elif t < t_up0:
        S = lib.sample(SCRIBBLE, False, 2.0)
        i = min(len(S) - 1, int(len(S) * clamp(du)))
        near = (pcx - 4 + float(S[i][0]) + 34, pcy + float(S[i][1]) * .62 - 70 + 3 * math.sin(draw_ph))
    elif t < t_slap:
        k = ease_out(clamp((t - t_up0) / .22), 2)
        near = (lerp(326, 300, k), lerp(900, 760, k))
    else:
        k = ease_in(clamp((t - t_slap) / .07), 2)
        near = (lerp(300, 250, k), lerp(760, R.DESK_TOP - 70, k))
    slap = t >= t_slap - .02
    far_t = (pcx + 60, pcy - 30) if not slap else (pcx + 60, pcy - 30)
    arms = {"f": ("ik", (far_t[0] + 0, far_t[1] + 14), -1), "n": ("ik", near, -1)}
    hands = {"f": {"curl": (.35, .35, .4, .45), "thumb": .35, "dir": (1, .55)},
             "n": ({"kind": "open", "dir": (1, .55), "curl": (.02, .02, .05, .08), "spread": .25, "thumb": .15} if slap else {"kind": "none"})}
    ex = expr_of("zeal", look=(.55, .55)) if t >= T_DIMA else expr_of("focus", look=(.6, .2), brows="up")
    if t >= T_DIMA:
        ex["closed"] = blink(t, (34.25,))
        if t > T_STOLOM:
            ex.update(mouth="grin", open=1.0, look=(.5, .7))
        if T_TVOR - .1 < t < T_STOLOM - .3:
            ex.update(look=(-.2, -.8))     # глянул на взлетевшие наброски
    lean = .2 + .1 * bump(t, T_STOLOM, .35) - .08 * bump(t, T_DIMA + .1, .3)
    ha = .08 + .04 * math.sin(t * 3) - (.12 if T_TVOR - .1 < t < T_STOLOM - .3 else 0)
    legs = dima(hx, hy, flip=True, expr=ex, lean=lean, head_ang=ha, arms=arms, hands=hands, layers=("legs",))
    body = dima(hx, hy, flip=True, expr=ex, lean=lean, head_ang=ha, arms=arms, hands=hands, layers=("pelvis", "arm_f", "body"))
    armn = dima(hx, hy, flip=True, expr=ex, lean=lean, head_ang=ha, arms=arms, hands=hands, layers=("arm_n",))
    ch = chair(spin=.2, side=1, dx=dx, dy=-up - sq)
    o = [beh, ch["back"], legs["svg"], front, ch["base"], ch["seat"], items, paper, body["svg"]]
    if not slap:
        bk, mk, fr, tip = marker_in_fist(armn["wrist"]["n"], +1, tilt=-14)
        o += [bk, armn["svg"], mk, fr]
    else:
        o.append(armn["svg"])
        u = clamp((t - t_slap - .04) / .32)
        if 0 < u < 1:
            o.append(PR.clink(255, R.DESK_TOP - 60, 1.3, u, seed=3))
    # лампочки-идеи над головой загораются по очереди
    hd = body["head"]
    for i, (tt, ox, oy, col) in enumerate(((T_PRIDUM, -150, -330, None), (T_PRIDUM + .22, 20, -400, "#8fd0c4"), (T_PRIDUM + .44, 180, -320, "#f29fb8"))):
        if t < tt:
            continue
        sc = .85 * spring(t - tt, 2.4, 6.0)
        fl = 1.0 if t > tt + .12 else .4
        o.append(PR.idea_bulb(hd[0] + ox, hd[1] + oy + 6 * math.sin(t * 3 + i), sc, on=fl, t=t, seed=i, col=col))
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(o)}</g>'


# ═══════════════════════════════ s15: чистый стол ═══════════════════════════════
CK = (890.0, R.DESK_TOP - 60)       # центр листа с чекбоксами (как в room.clean_top)


def box_pos(j):
    """Мировая точка j-го чекбокса (галочка) на листе props.checklist (rot −3, sy .62)."""
    lx, ly = -38.0, -62 + 40 * j - 4
    a = math.radians(-3)
    x, y = lx, ly * .62
    return (CK[0] + x * math.cos(a) - y * math.sin(a), CK[1] + x * math.sin(a) + y * math.cos(a))


def frame15(t):
    a = 35.6
    wi = ease_out(clamp((t - a) / .3), 3)
    push = sm(t, a + .3, 38.9)
    s = lerp(1.05, 1.3, push) - .12 * (1 - wi)
    cx = lerp(640, 760, push) - 240 * (1 - wi) + 4 * math.sin(t * 1.2)
    cy = lerp(800, 820, push) + 4 * math.sin(t * 1.5)
    rot = lerp(.8, -.4, push) - 3 * (1 - wi)
    set_ink(s)
    c1 = clamp((t - T_PLANU) / .3)
    t2 = T_PLANU + .55
    c2 = clamp((t - t2) / .3)
    checks, cu = (0, c1) if t < t2 else (1, c2)
    if c2 >= 1:
        checks, cu = 2, 0.0
    shine = clamp((t - (T_CHISTYM - .05)) / .7)
    beh, front, items = room_layers(t, checks=checks, cu=cu, shine=shine)
    # кончик маркера: висит над первым квадратиком, ведёт галочку, переходит ко второму
    def tick_path(j, u):
        bx, by = box_pos(j)
        pts = [(-22, 0), (-12, 10), (-6, 17), (6, 2), (18, -12), (28, -24)]
        S = lib.sample(pts, False, 1.5)
        i = min(len(S) - 1, int(len(S) * clamp(u)))
        return (bx + float(S[i][0]) * .62, by + float(S[i][1]) * .62)
    if t < T_PLANU:
        b0 = box_pos(0)
        tip = (b0[0] - 14 + 4 * math.sin(t * 2.2), b0[1] - 30 + 10 * math.sin(t * 1.7) - 20 * (1 - sm(t, a, a + 1.0)))
    elif t < T_PLANU + .3:
        tip = tick_path(0, c1)
    elif t < t2:
        k = sm(t, T_PLANU + .3, t2)
        e = tick_path(0, 1.0)
        b1 = box_pos(1)
        tip = (lerp(e[0], b1[0] - 14, k), lerp(e[1], b1[1] - 4, k) - 26 * math.sin(math.pi * k))
    elif t < t2 + .3:
        tip = tick_path(1, c2)
    else:
        e = tick_path(1, 1.0)
        k = sm(t, t2 + .3, t2 + .8)
        tip = (e[0] + 20 * k, e[1] - 40 * k)
    side = -1                        # Дима лицом вправо: кисть слева от маркера
    tilt = 12.0
    am = math.radians(90 + tilt)
    mc = (tip[0] - 70 * math.cos(am), tip[1] - 70 * math.sin(am))
    wrist = (mc[0] - side * (12 + 44 * GK), mc[1] - 8)
    arms = {"f": ("ik", (HX + 230, R.DESK_TOP - 30), -1), "n": ("ik", wrist, -1)}
    hands = {"f": {"curl": (.45, .45, .5, .55), "thumb": .4, "dir": (1, .35)}, "n": {"kind": "none"}}
    ex = expr_of("focus", look=(.75, .65), closed=blink(t, (36.3, 38.25)))
    if t > T_CHISTYM:
        ex.update(mouth="smile", smile=.55 * sm(t, T_CHISTYM, T_CHISTYM + .3), brows="calm")
    nod = .05 * bump(t, T_PLANU + .1, .3) + .05 * bump(t, t2 + .1, .3)
    lean = .16 + .02 * math.sin(t * 1.4)
    ha = .1 + nod
    legs = dima(HX, HY, flip=False, expr=ex, lean=lean, head_ang=ha, arms=arms, hands=hands, layers=("legs",))
    body = dima(HX, HY, flip=False, expr=ex, lean=lean, head_ang=ha, arms=arms, hands=hands, layers=("pelvis", "arm_f", "body"))
    armn = dima(HX, HY, flip=False, expr=ex, lean=lean, head_ang=ha, arms=arms, hands=hands, layers=("arm_n",))
    ch = chair(spin=-.2, side=1)
    bk, mk, fr, _ = marker_in_fist(armn["wrist"]["n"], side, tilt=tilt, col="#4f8a8b", seed=940)
    o = [beh, ch["back"], legs["svg"], front, ch["base"], ch["seat"], items, body["svg"], bk, armn["svg"], mk, fr]
    if shine > 0:
        u = shine
        for i, (px, py) in enumerate(((1560, R.DESK_TOP - 100), (1290, R.DESK_TOP - 70), (980, R.DESK_TOP - 20))):
            v = math.sin(math.pi * clamp(u * 1.6 - i * .25))
            if v > 0:
                o.append(PR.star4(px, py, 34 * v, 1.0))
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(o)}</g>'


# ═══════════════════════════════ s16: общий план ═══════════════════════════════
def frame16(t):
    a = 38.5
    back = sm(t, T_DVA - .05, T_DVA + .65)
    s = lerp(1.25, .8, back) + .03 * bump(t, T_STYDA, .5)
    cx = lerp(560, 570, back) + 4 * math.sin(t * 1.1)
    cy = lerp(820, 1060, back) + 3 * math.sin(t * 1.4) - 10 * bump(t, T_STYDA, .5)
    rot = lerp(.9, 0.0, back) + .6 * math.sin(t * .9) * back
    set_ink(s)
    beh, front, items = room_layers(t, checks=2)
    # стул: на «Два» пол-оборота (от творческого стола к зрителю-вправо), на «стыда» — полный оборот с раскинутыми руками
    sp1 = sm(t, T_DVA, T_DVA + .5) * .5
    sp2 = sm(t, T_STYDA + .02, T_STYDA + .8)
    spin = sp1 + sp2
    c = math.cos(2 * math.pi * spin)        # 1 — лицом влево (к творческому), −1 — вправо
    face_left = c > 0
    sx = 0.38 + 0.62 * abs(c)
    wide = sm(t, T_STYDA - .12, T_STYDA + .2)
    if wide > 0:
        P = people.mix_pose("rest", "arms_wide", wide, HX, HY, BS)
        arms, hands, lean, ha = P["arms"], P["hands"], P["lean"], P["head_ang"]
        if face_left:   # mix_pose считает цели в несмещённой системе — для flip отражаем, dima() отразит обратно
            arms = {k: (("ik", (2 * HX - v[1][0], v[1][1]), v[2]) if v[0] == "ik" else v) for k, v in arms.items()}
    else:
        arms = {"f": ("ik", (HX + (-1 if face_left else 1) * 260, HY - 40), -1), "n": ("ik", (HX + (-1 if face_left else 1) * 300, HY - 10), -1)}
        hands = {"f": {"curl": (.4, .4, .45, .5), "thumb": .35, "dir": (1, .6)}, "n": {"curl": (.35, .35, .4, .45), "thumb": .3, "dir": (1, .6)}}
        lean, ha = .05, .02
    if t < T_DVA:
        ex = expr_of("focus", look=(.7, .3), brows="calm")
    elif t < T_STYDA - .1:
        ex = expr_of("calm_smile", look=(-.1 if face_left else .1, .05), smile=.5)
    else:
        ex = expr_of("calm_smile", look=(0, -.1), lid=.62)
    ex["closed"] = blink(t, (38.75, 40.2))
    bob = 6 * math.sin(t * 2.6) + 10 * bump(t, T_STYDA, .4)
    hy = HY - bob * .3
    fig = dima(HX, hy, flip=face_left, expr=ex, lean=lean + .03 * math.sin(t * 2), head_ang=ha, arms=arms, hands=hands)
    ch = chair(spin=.25 + spin, side=1)
    figsvg = f'<g transform="translate({HX:.1f} 0) scale({sx:.4f} 1) translate({-HX:.1f} 0)">{fig["svg"]}</g>'
    o = [beh, front, items, ch["back"], ch["base"], ch["seat"], figsvg]
    # «никакого стыда»: лёгкие тёплые штрихи-искры вокруг раскинутых рук
    if t > T_STYDA:
        u = clamp((t - T_STYDA) / .6)
        hd = fig["head"]
        for i in range(6):
            ang = math.radians(-160 + i * 28)
            r0, r1 = 300 + 40 * u, 340 + 90 * u
            o.append(line([(hd[0] + r0 * math.cos(ang), hd[1] + 60 + r0 * math.sin(ang)), (hd[0] + r1 * math.cos(ang), hd[1] + 60 + r1 * math.sin(ang))],
                          w=8 * (1 - u * .7), color="#f2b632", taper=.4, wmin=.3, seed=7500 + i, op=1 - u * .6))
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(o)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    body = {"s14": frame14, "s15": frame15, "s16": frame16}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#c38c5a"/>{body}')
