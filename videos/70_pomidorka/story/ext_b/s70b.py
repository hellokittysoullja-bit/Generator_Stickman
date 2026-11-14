"""Рилс 70 «помидорка», группа B: Дима крупно — отражение, качели, поток.
s07 (10.40–12.16): ночь, Дима крупно перед ноутбуком с погасшим тёмным экраном; в экране — его отражение (тот же Дима, зеркально и
    приглушённо). «решил» (10.45) всматривается и трогает щёку; «что с ним что-то» хмурится, отражение повторяет; «не так»
    (11.49–11.92) роняет голову на скрещённые руки, таймер тикает у локтя. Камера: медленный наезд на лицо, на «не так» опускается.
s11 (18.90–20.95, whip): двор днём — качели на раме, дерево, забор; Дима уже раскачивается, ноги вперёд; «Таймер» (18.96) на столбике
    таймер-помидорка с ручками-штрихами; «помогает» (19.49) подталкивает качели — взлёт, ветер, волосы; «кто уже начал» (20.26–20.88)
    смеётся на верхней точке. Камера качается маятником.
s15 (27.50–29.70): утро, Дима по грудь за ноутбуком; «две минуты» таймер коротко звякает и подпрыгивает — Дима не поднимает глаз;
    «уже пишет» волнистые строки растут; «останавливаться» (28.92) не глядя отодвигает таймер ладонью, «не хочется» кивает.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, предметы — props.py, люди — people.py."""
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
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import clamp, ease_in, ease_io, ease_out, line, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def frame_svg(body, cx, cy, s, rot, bg):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>')


def whip_in(t, t0, dur=.2):
    u = clamp((t - t0) / dur)
    e = 1 - ease_out(u, 3)
    return -150 * e, -2.0 * e


BS = 1.0
SX, SY = R.SIT
FEET = {"n": ((SX + 300 * BS, R.FL - 52), 0.0), "f": ((SX + 250 * BS, R.FL - 50), 0.0)}


def dima_parts(e, pose=None, u_pose=None, **kw):
    kw.setdefault("feet", FEET)
    return {k: people.dima(SX, SY, BS, e, pose, u_pose=u_pose, layers=(k,), **kw) for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}


def cheek_arm(e, pose, upose, lean_add, head_add, u):
    """Ближняя рука к щеке: цель — от головы (кончики пальцев на щеке, ниже глаза)."""
    f = people.dima(SX, SY, BS, e, pose, u_pose=upose, lean_add=lean_add, head_add=head_add, feet=FEET, layers=("body",))
    hx, hy = f["head"]
    tgt = (hx + 10, hy + 235)
    a0 = people.ik_ang("dima", SX, SY, BS, people.POSE["sit_desk"][0] + lean_add, (SX + 240 * people.HEIGHT["dima"] * BS, SY - 195), -1)
    a1 = people.ik_ang("dima", SX, SY, BS, people.POSE["sit_desk"][0] + lean_add, tgt, -1)
    return people.mix_ang(a0, a1, u)


def desk_layers(sc, parts, items, front_items=""):
    """Слои сцены у стола в порядке room.desk_scene."""
    return (sc["bg"] + sc["chair_back"] + sc["desk_top"] + sc["pool"] + parts["legs"]["svg"] + sc["desk_legs"] + sc["chair_seat"]
            + parts["pelvis"]["svg"] + parts["arm_f"]["svg"] + parts["body"]["svg"] + items + parts["arm_n"]["svg"] + front_items + sc["lamp"])


# ═══════════════════════════════ s07: отражение в тёмном экране ═══════════════════════════════
T7_RESH = wt("решил")           # 10.45
T7_CHTO = wt("что", 10.7)       # 10.82
T7_NE = wt("не", 11.4)          # 11.49
T7_TAK = wt("так", 11.5)        # 11.68
LAP7 = (790.0, R.DESK_TOP - 22.0, .82)
TIM7 = (628.0, R.DESK_TOP - 30.0, .36)


def s07_expr(t):
    if t < T7_RESH + .05:
        e = dict(people.EXPR["dima"]["peer"])
    elif t < T7_CHTO - .02:
        e = dict(people.EXPR["dima"]["peer"], brows="up", look=(.85, .1))
    elif t < T7_NE:
        e = dict(people.EXPR["dima"]["frowny"], look=(.85, .15))
    else:
        e = dict(people.EXPR["dima"]["sink"], closed=clamp((t - T7_NE) / .25))
    e["closed"] = max(e.get("closed", 0), 1.0 if 10.95 < t < 11.03 else 0)      # моргание
    return e


def s07_pose(t):
    """(pose, u_pose, u_cheek) по времени: всматривается (руки на столе) → пальцы на щеке → голова на руки."""
    if t < T7_NE:
        return "sit_desk", ("sit_desk", 0.0), ease_io((t - T7_RESH) / .3) * (1 - .3 * ease_io((t - 11.15) / .3))
    u = ease_io((t - T7_NE) / (11.92 - T7_NE))
    return "sit_desk", ("head_arms", u), .7 * (1 - clamp(u * 2.5))


RK = .62


def reflection(e, pose, upose, lean_add, head_add, arm_n, layers):
    """Тот же Дима зеркально (таз — ниже экрана): голова и плечи в координатах центра экрана, та же поза."""
    k = RK / BS
    a = dict(arms={"n": arm_n}) if arm_n else {}
    f = people.dima(0, 0, RK, e, pose, u_pose=upose, layers=layers, lean_add=lean_add, head_add=head_add, **a)
    del k
    return f'<g transform="translate(70 360) scale(-1 1)">{f["svg"]}</g>'


def s07(t):
    lib.dyn_begin()
    sc = R.desk_scene(t, "night")
    pose, upose, uc = s07_pose(t)
    lean_add = .03 * math.sin(t * 2.3) + .05 * ease_io((t - 10.2) / .6) * (1 - ease_io((t - T7_NE) / .3))
    head_add = .06 * ease_io((t - T7_CHTO) / .3) * (1 - ease_io((t - T7_NE) / .2))
    e = s07_expr(t)
    arm_n = cheek_arm(e, pose, upose, lean_add, head_add, uc) if uc > 0.001 else None
    hn = {"n": {"dir": (.15, -1), "curl": (.05, .2, .45, .6), "spread": .08, "thumb": .45}} if uc > .3 else None
    kw = dict(lean_add=lean_add, head_add=head_add)
    if arm_n:
        kw["arms"] = {"n": arm_n}
    if hn:
        kw["hands"] = hn
    parts = dima_parts(e, pose, upose, **kw)
    under = upose[0] == "head_arms" and upose[1] > .55
    order = people.LAYERS_ARMS_UNDER if under else ("legs", "pelvis", "arm_f", "body", "arm_n")
    lx, ly, lk = LAP7
    rarm = None
    if arm_n:      # та же рука у щеки — в масштабе отражения
        f0 = people.dima(SX, SY, BS, e, pose, u_pose=upose, feet=FEET, layers=("body",), **{k: v for k, v in kw.items() if k != "hands"})
        hx, hy = f0["head"]
        tgt = (hx + 10, hy + 235)
        rarm = people.mix_ang(people.ik_ang("dima", 0, 0, RK, people.POSE["sit_desk"][0] + lean_add, (240 * RK, -195 * RK), -1),
                              people.ik_ang("dima", 0, 0, RK, people.POSE["sit_desk"][0] + lean_add, ((tgt[0] - SX) * RK, (tgt[1] - SY) * RK), -1), 1.0)
    refl = reflection(e, pose, upose, lean_add, head_add, rarm, order[2:])
    items = P.laptop(lx, ly, lk, 1.0, "reflect", reflect=refl, t=t, seed=7, turn=-.72)
    tx, ty, tk = TIM7
    tick = (t * 2) % 1 < .5
    front = P.tomato_timer(tx, ty - P.TOMATO_RY * tk, tk, -4 if tick else 3, wedge=.3, shake=1.5, leaf_swing=6 * math.sin(t * 9), t=t, seed=17)
    for j in range(2):     # «тик» штрихами у таймера
        ph = (t * 2 + j * .5) % 1
        if ph < .35:
            a = math.radians(-60 - 60 * j)
            r0 = 70 * tk + 10
            front += line([(tx + r0 * math.cos(a), ty - 60 + r0 * math.sin(a)), (tx + (r0 + 26) * math.cos(a), ty - 60 + (r0 + 26) * math.sin(a))], 3.4, INK,
                          taper=.5, wmin=.3, seed=7100 + j, op=1 - ph / .35)
    if under:      # голова легла: таймер виден у локтя на переднем краю стола
        k2 = .34
        x2, y2 = 600.0, R.DESK_TOP - 4
        front = (lib.blob(lib.ellipse_pts(x2 + 6, y2 + 2, 44, 8, 12), "#3a2a20", .5)
                 + P.tomato_timer(x2, y2 - P.TOMATO_RY * k2, k2, -4 if tick else 3, wedge=.3, shake=1.5, leaf_swing=6 * math.sin(t * 9), t=t, seed=17))
        body = (sc["bg"] + sc["chair_back"] + sc["desk_top"] + sc["pool"] + parts["legs"]["svg"] + sc["desk_legs"] + sc["chair_seat"] + items
                + parts["pelvis"]["svg"] + parts["arm_f"]["svg"] + parts["arm_n"]["svg"] + parts["body"]["svg"] + front + sc["lamp"])
        return frame_svg(body, *cam7(t), "#2a2440")
    items = items + front
    if under:
        body = (sc["bg"] + sc["chair_back"] + sc["desk_top"] + sc["pool"] + parts["legs"]["svg"] + sc["desk_legs"] + sc["chair_seat"] + items
                + parts["pelvis"]["svg"] + parts["arm_f"]["svg"] + parts["arm_n"]["svg"] + parts["body"]["svg"] + sc["lamp"])
    else:
        body = desk_layers(sc, parts, items)
    return frame_svg(body, *cam7(t), "#2a2440")


def cam7(t):
    """Камера: медленный наезд на лицо, на «не так» опускается за головой."""
    a = ease_io((t - 10.2) / 1.3)
    cx = lerp(585, 595, a)
    cy = lerp(800, 770, a)
    s = lerp(1.78, 1.95, a)
    d = ease_io((t - T7_NE) / .55)
    cy = lerp(cy, 840, d)
    s = lerp(s, 2.0, d)
    return cx, cy, s, -.6 * a


# ═══════════════════════════════ s11: качели во дворе ═══════════════════════════════
T11_TAIM = wt("таймер", 18.5)       # 18.96
T11_POM = wt("помогает")            # 19.49
T11_KTO = wt("кто", 20.0)           # 20.26
SW11 = (560.0, 1360.0, 1.3)
PER11 = 2.0
SC11 = .6
POST11 = (250.0, 1360.0, 1080.0)    # столбик: x, низ, верх
TK11 = .8


def amp11(t):
    return 15.0 + 25.0 * ease_out((t - T11_POM) / .45)


def ang11(t):
    return -amp11(t) * math.cos(2 * math.pi * (t - T11_POM) / PER11)


def sky11():
    g = lib.lin_grad([(0, "#8CC8EE", 1), (.7, "#CDE9F7", 1), (1, "#EAF5F8", 1)], 0, 0, 0, 1)
    return f'<path d="M-900 -900H2000V1400H-900Z" fill="url(#{g})"/>'


def s11(t):
    lib.dyn_begin()
    x0, gy, k = SW11
    a = ang11(t)
    o = [sky11(), P.sun(860, 260, 70, 1.0, t, seed=11)]
    for j, (cx_, cy_, w_) in enumerate(((180, 380, 220), (760, 520, 180))):        # облачка плывут
        o.append(P.cloud(cx_ + 14 * t % 600 - 100, cy_, w_, w_ * .5, seed=40 + j, ink_w=3.4))
    o.append(P.tree(-60, gy - 30, 3.0, 1.0, t, seed=11))
    o.append(P.tree(1120, gy - 40, 2.6, 1.0, t + .6, seed=12))
    o.append(P.fence(-500, 1600, gy - 30, 1.2, seed=11))
    o.append(lib.blob([(-900, gy - 40, 1), (2000, gy - 40, 1), (2000, 2800, 1), (-900, 2800, 1)], "#9CC98A"))
    o.append(line([(-900, gy - 38), (500, gy - 44), (2000, gy - 36)], 5, INK, taper=.05, wmin=.8, seed=11001))
    for j in range(14):
        gx = -200 + j * 110
        o.append(line([(gx, gy - 30), (gx + 8, gy - 62)], 4, "#5E9A5A", taper=.6, wmin=.3, seed=11010 + j))
    # столбик с таймером
    px, pb, pt = POST11
    o.append(lib.shape(lib.rect_pts(px - 26, pt, px + 26, pb), P.C_WOOD, lib.blob(lib.rect_pts(px + 6, pt, px + 26, pb), P.C_WOOD_SH), w=4, seed=11020))
    o.append(lib.shape(lib.rrect(px - 70, pt - 16, px + 70, pt + 6, 6), P.C_WOOD_HI, "", w=4, seed=11021))
    o.append(P.swing(x0, gy, k, a, t, seed=11, layer="back"))
    o.append(P.swing(x0, gy, k, a, t, seed=11, layer="seat"))
    sx, sy, sdg = P.swing_seat(x0, gy, k, a)
    # Дима на качелях: рисуется прямо (сиденье горизонтально), группа поворачивается вместе с сиденьем
    hx, hy = sx - 12, sy - 22
    kick = .55 + .45 * math.sin(2 * math.pi * (t - T11_POM) / PER11 - math.pi / 2)
    rope_top_l = (sx + 6, sy - P.SWING_ROPE * k)
    arms = people.swing_arms(hx, hy, SC11, rope_top_l, (sx + 6, sy), 0.0)
    if t < T11_POM - .05:
        e = dict(people.EXPR["dima"]["relief_day"], look=(.5, -.1))
    elif t < T11_KTO - .1:
        e = dict(people.EXPR["dima"]["surprise_day"])
    else:
        e = dict(people.EXPR["dima"]["laugh_day"])
    sp = abs(math.sin(2 * math.pi * (t - T11_POM) / PER11)) * amp11(t) / 40
    e["hair"] = 10 * sp * math.sin(t * 9)
    lean = -.05 * math.sin(2 * math.pi * (t - T11_POM) / PER11) + (-.12 if t > T11_KTO else 0)
    kw = dict(arms=arms, lean_add=lean, head_add=-.12 * clamp((t - T11_KTO + .1) / .3), **people.swing_kw(hx, hy, SC11, kick))
    body = people.dima(hx, hy, SC11, e, "swing", layers=("legs", "pelvis", "arm_f", "body"), **kw)
    hand = people.dima(hx, hy, SC11, e, "swing", layers=("arm_n",), **kw)
    rot = f'rotate({sdg:.3f} {sx:.1f} {sy:.1f})'
    (rt, rb), = P.swing_rope_pts(x0, gy, k, a)
    d = (sy - hand["wrist"]["n"][1] + 20) / (P.SWING_ROPE * k)
    rm = (rb[0] + (rt[0] - rb[0]) * d, rb[1] + (rt[1] - rb[1]) * d)
    o.append(line([rt, rm], 7.5 * k, "#8A6A48", taper=.05, wmin=.9, seed=11210))     # верёвка выше кистей — за головой
    o.append(f'<g transform="{rot}">{body["svg"]}</g>')
    o.append(line([rm, rb], 7.5 * k, "#8A6A48", taper=.05, wmin=.9, seed=11211))
    o.append(lib.blob(lib.ellipse_pts(rt[0], rt[1], 10 * k, 10 * k, 8), INK))
    o.append(f'<g transform="{rot}">{hand["svg"]}</g>')
    # таймер на столбике: ручки тянутся и толкают сиденье на «помогает»
    tcx, tcy = px, pt - 16 - P.TOMATO_RY * TK11
    push = math.sin(math.pi * clamp((t - (T11_POM - .22)) / .5))
    seat_back = (sx - 95 * k, sy)
    rr = ((seat_back[0] - tcx) / TK11, (seat_back[1] - tcy) / TK11)
    reach = (lerp(150, min(rr[0], 420), push), lerp(-30, rr[1], push))
    hands_u = ease_out((t - (T11_TAIM - .25)) / .3)
    o.append(P.tomato_timer(tcx, tcy - 30 * P.hop(t, T11_TAIM - .05, 1, .25) / 1, TK11, 6 * push, wedge=P.WEDGE_2, shake=1.0, leaf_swing=10 * math.sin(t * 6),
                            hands=hands_u, t=t, seed=21, arms=((-160, 40 + 40 * math.sin(t * 5)), reach)))
    if push > .2:
        o.append(P.clink(seat_back[0] - 10, seat_back[1] - 10, 1.4, clamp((t - T11_POM + .05) / .3), seed=11))
    # ветер и штрихи скорости
    o.append(P.wind_lines(sx + 60, sy - 260, 1.6, sp, t, seed=11, n=4))
    # камера-маятник: следует за сиденьем, качается
    cx = lerp(x0, sx, .55) + 40
    cy = lerp(gy - 600, sy - 260, .5) + 40
    s = 1.42 + .05 * ease_io((t - 18.7) / 2.4)
    wx, wr = whip_in(t, 18.9)
    return frame_svg("".join(o), cx - wx, cy, s, .35 * a + wr, "#CDE9F7")


# ═══════════════════════════════ s15: утро, пишет — таймер отодвинут ═══════════════════════════════
T15_DVE = wt("две", 27.3)            # 27.54
T15_PISH = wt("пишет")               # 28.37
T15_OST = wt("останавливаться")      # 28.92
T15_NE = wt("не", 29.4)              # 29.57
LAP15 = (800.0, R.DESK_TOP - 22.0, .86)
TIM15 = (655.0, R.DESK_TOP - 50.0, .4)


def s15(t):
    lib.dyn_begin()
    sc = R.desk_scene(t, "day")
    # таймер: две минуты кончились — звяк и подскок; на «останавливаться» ладонь не глядя отодвигает его
    ring = clamp((t - T15_DVE) / .1) * (1 - .6 * clamp((t - 28.1) / .4)) * (1 - clamp((t - T15_OST - .2) / .25))
    pushu = ease_io((t - T15_OST) / .4)
    tx, ty, tk = TIM15
    tx += 120 * ease_out((t - T15_OST - .18) / .35)
    ty -= 26 * ease_out((t - T15_OST - .18) / .35)
    hop = P.hop(t, T15_DVE + .02, 46, .3) + P.hop(t, T15_DVE + .38, 20, .22)
    timer = P.tomato_timer(tx, ty - P.TOMATO_RY * tk + hop, tk, 0, wedge=0.0, ring=ring * .8, leaf_swing=12 * math.sin(t * 11) * ring, t=t, seed=15)
    # печатает: пальцы бегают (кисти подпрыгивают по очереди), на «останавливаться» ближняя ладонь — к таймеру и назад
    typ = 1.0 if t > 27.3 else 0
    jf = 6 * math.sin(t * 31) * typ
    jn = 6 * math.sin(t * 27 + 1.3) * typ
    sc_ = BS * people.HEIGHT["dima"]
    lean = .04 + .015 * math.sin(t * 2)
    a_f = ("ik", (SX + 250 * sc_, SY - 205 * sc_ + jf), -1)
    a_type = people.ik_ang("dima", SX, SY, BS, people.POSE["type"][0] + lean, (SX + 335 * sc_, SY - 210 * sc_ + jn), -1)
    a_push = people.ik_ang("dima", SX, SY, BS, people.POSE["type"][0] + lean, (tx - 70, ty - 40), -1)
    back = ease_io((t - T15_OST - .55) / .35)
    a_n = people.mix_ang(a_type, a_push, pushu * (1 - back))
    hands = {"f": {"dir": (1, .55), "curl": (.3 + .1 * math.sin(t * 29), .35, .4 + .1 * math.sin(t * 23), .45), "spread": .2, "thumb": .3}}
    if pushu * (1 - back) > .4:
        hands["n"] = {"dir": (1, .1), "spread": .3, "curl": (0, .03, .06, .1), "thumb": .1}
    else:
        hands["n"] = {"dir": (1, .6), "curl": (.3 + .1 * math.sin(t * 26), .3, .35 + .1 * math.sin(t * 21), .4), "spread": .2, "thumb": .3}
    nod = .07 * math.sin(math.pi * clamp((t - T15_NE + .05) / .25)) + .05 * math.sin(math.pi * clamp((t - T15_NE - .2) / .2))
    e = dict(people.EXPR["dima"]["focus_smile"])
    e["smile"] = .3 + .4 * ease_io((t - T15_PISH) / .4)
    e["closed"] = 1.0 if 28.55 < t < 28.62 else 0.0
    parts = dima_parts(e, "type", arms={"f": a_f, "n": a_n}, hands=hands, lean_add=lean - .08, head_add=nod + .03 * math.sin(t * 1.7))
    lines = .28 + .2 * ease_io((t - 27.3) / 1.0) + .42 * ease_io((t - T15_PISH + .1) / 1.4)
    lx, ly, lk = LAP15
    items = P.laptop(lx, ly, lk, 1.0, "lines", lines=lines, t=t, seed=15, turn=-.72) + timer
    body = desk_layers(sc, parts, items)
    # камера: дрейф по дуге от рук к лицу
    u = ease_io((t - 27.3) / 2.6)
    cx = lerp(640, 560, u) + 30 * math.sin(math.pi * u)
    cy = lerp(860, 760, u)
    s = lerp(1.9, 2.0, u)
    return frame_svg(body, cx, cy, s, 0, "#e6dcc0")


SHOTS = {"s07": s07, "s11": s11, "s15": s15}


def frame(sid, t):
    return SHOTS[sid](t)
