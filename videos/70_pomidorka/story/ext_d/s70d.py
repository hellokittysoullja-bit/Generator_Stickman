"""Рилс 70 «помидорка», группа D — руки, звонки, дверь: s03 (макро рук над пустыми клавишами, дрожат, палец не нажимает, отдёрнул;
тилт к застывшему лицу), s06 (таймер крупно звенит и подпрыгивает, ладонь шлёпает и заводит снова, за окном вечер → ночь, прибавилась
кружка), s12 (коридор: Дима у закрытой двери, ладонь на ручке, таймер тикает у ног, пальцы отпускают ручку).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Комната — common/room.py, люди — common/people.py, предметы — common/props.py;
помощники времени и камеры — общие с группой C (ext_c/s70c.py). Букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "ext_c"))
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, clamp, ease_out, line  # noqa: E402
from s70c import (BS, FEET, SX, SY, blinkv, bump, damp, dima_layers, ex, keys, lerp, lerp2, set_ink, shake2, sm,  # noqa: E402
                  table_y, timer_grips, whip_in, wt)

SC = BS * people.HEIGHT["dima"]


# ═════════════════════════ s03: руки над клавишами → застывшее лицо ═════════════════════════
T_KTO, T_NE, T_MOZH, T_NACH = wt("кто"), wt("не", 2.9), wt("может"), wt("начать")      # 2.84 3.01 3.17 3.48
LAP3 = (R.LAPTOP[0] - 70, R.LAPTOP[1])
K3 = .78


def s03(t):
    lib.dyn_begin()
    sc = R.desk_scene(t, "night")
    lp = PR.laptop_pts(LAP3[0], LAP3[1], K3, 1.0, turn=.45)
    kx, ky = lp["keys"]
    # кисти: зависли над клавишами (дрожат) → «не может» ближний палец тянется и не нажимает → «начать» отдёрнул к груди
    rec = sm(t, T_NACH - .02, T_NACH + .2)
    trem = (1 - rec) * (1.0 + 1.5 * sm(t, T_KTO, T_KTO + .2))
    hov_f = (kx - 70 + 3 * trem * math.sin(t * 41), ky - 70 + 3 * trem * math.cos(t * 37))
    reach = sm(t, T_NE, T_MOZH + .05) * (1 - sm(t, T_MOZH + .15, T_NACH))
    hov_n = (kx + 40 + 3.5 * trem * math.sin(t * 43 + 1), ky - 78 + 22 * reach + 3.5 * trem * math.cos(t * 39 + 2))
    rc_f = (SX + 110 * SC, SY - 300 * SC)
    rc_n = (SX + 160 * SC, SY - 320 * SC)
    wf, wn = lerp2(hov_f, rc_f, rec), lerp2(hov_n, rc_n, rec)
    hover_h = {"dir": (1, .45), "curl": (.18, .25, .3, .35), "spread": .25, "thumb": .2}
    point_h = {"dir": (1, .6), "curl": (.0, .62, .7, .75), "spread": .1, "thumb": .35}
    rec_h = {"dir": (.2, -1), "curl": (.72, .72, .75, .78), "thumb": .6}
    hn = point_h if reach > .3 and rec < .3 else hover_h
    hands = {"f": rec_h if rec > .5 else hover_h, "n": rec_h if rec > .5 else hn}
    # лицо: застыл, смотрит в пустую страницу, моргает, сглатывает
    e = ex("numb", look=(.75, .38), lid=.62 + .18 * rec, brows="worry" if t > T_NACH else "calm")
    e["closed"] = blinkv(t, [3.3, 4.55])
    swallow = bump(t, 4.75, .3)
    full, parts = dima_layers(e, {"f": ("ik", wf, -1), "n": ("ik", wn, -1)}, hands, pose="hover",
                              lean_add=.04 - .08 * rec + .01 * math.sin(t * 3.3), head_add=.03 * swallow - .03 * rec + .015 * math.sin(t * 2.1),
                              shrug=.35 * rec)
    lap = PR.laptop(LAP3[0], LAP3[1], K3, 1.0, "page", t=t, seed=1, turn=.45, glow=.4)
    tim = PR.tomato_timer(1010, table_y(.6), .6, -4, wedge=PR.WEDGE_25 * .97, shake=1.8, leaf_swing=4 * math.sin(t * 3), t=t, seed=1)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], tim, lap, parts["legs"], sc["desk_legs"], sc["chair_seat"],
             parts["pelvis"], parts["arm_f"], parts["body"], parts["arm_n"], sc["lamp"]]
    # камера: хлёст на входе, макро над руками с дрейфом; с 3.9 — тилт вверх к лицу и лёгкий наезд
    wx, wr = whip_in(t, 2.64)
    up = .55 * sm(t, T_NACH + .05, 4.0) + .45 * sm(t, 4.0, 4.6)
    hx, hy = full["head"]
    cx = lerp(kx - 30 + 25 * sm(t, 2.64, 3.9), hx + 70, up) + wx
    cy = lerp(ky - 60, hy + 40, up)
    s = lerp(2.75, 3.25, up) * (1 + .025 * sm(t, 4.9, 5.3))
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, wr + .5 * math.sin(t * 1.1))}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')


# ═════════════════════════ s06: звонок, шлепок, завод — и ещё, и ещё ═════════════════════════
T_POTOM, T_ESCH, T_RAZ, T_ESCH2 = wt("потом"), wt("ещё"), wt("раз"), wt("ещё", 9.5)     # 8.57 8.88 9.18 9.7
TV6 = (330.0, 1300.0)     # таймер на столе (координаты кадра wall_view)
K6 = 1.0
MUG6 = (590.0, 1330.0)
# два цикла «звонит → шлепок → завод»; второй быстрее
CYC = [dict(ring=T_POTOM, slap=T_ESCH, wind=T_RAZ, wind_d=.24, off=T_RAZ + .32),
       dict(ring=T_ESCH2 - .08, slap=T_ESCH2 + .14, wind=T_ESCH2 + .26, wind_d=.16, off=T_ESCH2 + .5)]


def s06_state(t):
    """Клин, звон, поворот таймера и где ладонь: (wedge, ring, rot, palm, hand_kind)."""
    c1, c2 = CYC
    wedge, ring, rot = .015, 0.0, -3.0
    # первый звонок → шлепок → завод → время утекает до второго звонка
    if t < c1["slap"]:
        ring = 1.0 if t >= c1["ring"] else 0.0
    elif t < c1["wind"]:
        pass
    elif t < c2["ring"]:
        w = sm(t, c1["wind"], c1["wind"] + c1["wind_d"])
        wedge = .015 + (PR.WEDGE_25 - .015) * w
        rot = -3 - 22 * w * (1 - sm(t, c1["wind"] + c1["wind_d"], c1["off"]))
        wedge *= 1 - sm(t, c1["off"] + .05, c2["ring"] - .02)        # ускоренное время: клин тает
        wedge = max(wedge, .015)
    elif t < c2["slap"]:
        ring = 1.0
    elif t < c2["wind"]:
        pass
    else:
        w = sm(t, c2["wind"], c2["wind"] + c2["wind_d"])
        wedge = .015 + (PR.WEDGE_25 - .015) * w
        rot = -3 - 22 * w * (1 - sm(t, c2["wind"] + c2["wind_d"], c2["off"]))
    return wedge, ring, rot


def s06_hand(t):
    """Ладонь: ждёт за кадром → падает на таймер (шлепок) → хват сверху и поворот → уходит. Возвращает (W, dir, hand, vis)."""
    top = (TV6[0] - 20, TV6[1] - PR.TOMATO_RY * K6 - 40)
    away = (TV6[0] - 520, TV6[1] + 260)
    for c in CYC:
        a0, a1 = c["slap"] - .14, c["off"] + .25
        if a0 <= t <= a1:
            come = ease_out(clamp((t - a0) / .14), 3)
            go = sm(t, c["off"], a1)
            W = lerp2(lerp2(away, top, come), away, go)
            flat = {"dir": (.55, .85), "curl": (0, .03, .06, .1), "spread": .3, "thumb": .15}
            grip = {"dir": (.5, .9), "curl": (.62, .66, .7, .72), "thumb": .7}
            hd = grip if c["wind"] - .03 <= t <= c["off"] else flat
            if c["wind"] <= t <= c["off"]:
                W = (W[0] + 22 * sm(t, c["wind"], c["wind"] + c["wind_d"]), W[1] - 6)
            return W, hd, True
    return away, None, False


def s06(t):
    lib.dyn_begin()
    phase = sm(t, 8.3, 10.3)
    v = R.wall_view(t, phase, 0.0, spot=1.0)
    wedge, ring, rot = s06_state(t)
    tx, ty = TV6
    hop = 0.0
    if ring > 0:
        hop = 26 * abs(math.sin(2 * math.pi * 6 * t))
    # шлепок: таймер сплющивается и вздрагивает
    sq = 0.0
    for c in CYC:
        sq = max(sq, bump(t, c["slap"], .16))
    shake = 1.5 + (5.0 if ring else 0.0) + 6 * sq
    leaf = 10 * math.sin(2 * math.pi * 2.2 * t) + (25 * math.sin(t * 40) if ring else 0.0) - 30 * sq
    tim = PR.tomato_timer(tx, ty - hop, K6, rot, wedge=wedge, ring=ring, shake=shake, leaf_swing=leaf, t=t, seed=1)
    if sq > .01:
        yb = ty + PR.TOMATO_RY * K6
        tim = f'<g transform="translate({tx:.1f} {yb:.1f}) scale({1 + .1 * sq:.4f} {1 - .14 * sq:.4f}) translate({-tx:.1f} {-yb:.1f})">{tim}</g>'
    # тень под таймером
    shadow = f'<ellipse cx="{tx + 6:.1f}" cy="{ty + PR.TOMATO_RY * K6 + 6:.1f}" rx="{105 - .4 * hop:.1f}" ry="16" fill="#000" opacity=".22"/>'
    # кружка появляется к ночи (время прошло)
    mo = sm(t, 9.55, 9.75)
    mug = f'<g opacity="{mo:.3f}">' + PR.mug(MUG6[0], MUG6[1], 1.25, 0, col="blue", coffee=False, seed=2) + "</g>" if mo > .01 else ""
    lap = PR.laptop(R.LAPTOP_V[0] + 120, R.LAPTOP_V[1], .7, 1.0, "page", t=t, seed=1)
    # рука и рукав Димы — из people.py: только ближняя рука, плечо за кадром слева внизу
    W, hd, vis = s06_hand(t)
    arm = ""
    if vis:
        e = ex("frowny")
        fig = people.dima(-330, 2330, 1.6, e, None, arms={"f": ("ang", .2, .2), "n": ("ik", W, 1)}, hands={"n": hd}, layers=("arm_n",))
        arm = fig["svg"]
    world = [v["bg"], v["desk"], v["pool"], lap, mug, shadow, tim, v["lamp"], arm]
    # камера: храповик — толчок-наезд на каждом звонке, тряска на шлепках
    push = .07 * sm(t, CYC[0]["ring"], CYC[0]["ring"] + .1) + .07 * sm(t, CYC[1]["ring"], CYC[1]["ring"] + .08)
    sx1, sy1 = shake2(t, CYC[0]["slap"], 13)
    sx2, sy2 = shake2(t, CYC[1]["slap"], 13)
    cx = 240 + 30 * math.sin(t * .7) - sx1 - sx2
    cy = 1080 - sy1 - sy2 + 20 * push
    s = 1.3 * (1 + push + .02 * math.sin(t * 1.3))
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, .4 * math.sin(t * .9))}">{"".join(world)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}')


def frame(sid, t):
    return {"s03": s03, "s06": s06}[sid](t)
