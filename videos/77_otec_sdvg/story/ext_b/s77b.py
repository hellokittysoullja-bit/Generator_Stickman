"""Рилс 77 «СДВГ не бывает?», группа B: отец, Дима и кот. Время — только из shots.json и voice/words.json (слово по индексу wN).
s07: (хлёст) кот за ночным стеклом в тёплом свете, «Напиши» (w23) стучит лапой по стеклу к зрителю, «кот» (w24) рукописью на тёмном
     стекле справа, «узнаешь» (w26) огонёк вспыхивает, голова набок.
s09: (хлёст) тёмная комната, Дима в полный рост; тень-силуэт отца с края, палец «напишешь» (w36), бирка летит «так»–«звать» (w37–w40),
     прилипает «себя» (w41), тянет вниз «лентяем» (w42).
s12: гараж днём, доска срывается «середине» (w55), ладонь по лбу «ругал» (w57), садится на ведро «себя» (w58), голова в ладони «лентяем» (w59).
s14: отец плечом в штору «сила воли» (w67–w68), кот шагом к крюку «тут» (w69), крюк — штора уезжает «при» (w71).
s15: (хлёст) тёплый вечер у забора, Дима входит «Димой» (w76), мазок «делают» (w77), доска готова «одному» (w79).
s17: гостиная, последний шуруп «впервые» (w84), полка держится «доделал» (w85), руки вверх и объятие «ремонт» (w86).
s18: кот в прыжке с кадра 0, приземляется «Кот» (w87), садится «сидит» (w88), огонёк золотом «полке» (w91).
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import cat as CAT  # noqa: E402
import hand_kot  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402

INK = lib.INK
W = json.load(open(os.path.join(STORY, "voice", "words.json")))
SHJ = json.load(open(os.path.join(STORY, "shots.json")))
SH = {s["id"]: s for s in SHJ["shots"]}


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


def whip_wrap(g, t, t0, dx=-640.0, dur=.22):
    """Хлёст на входе плана: кадр въезжает сбоку с горизонтальным размытием (только пока летит; с кадра 0 уже в движении)."""
    u = clamp((t - (t0 - .2)) / dur)
    if u >= 1:
        return g
    e = ease_out(u, 3)
    off = dx * (1 - e)
    bl = 60 * (1 - e)
    fid = lib.uid("wh")
    lib.DEFS.append(f'<filter id="{fid}" x="-30%" y="-5%" width="160%" height="110%"><feGaussianBlur stdDeviation="{bl:.1f} 0"/></filter>')
    return f'<g transform="translate({off:.1f} 0)" filter="url(#{fid})">{g}</g>'


def rect(x0, y0, x1, y1):
    return [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]


def grad_rect(x0, y0, x1, y1, stops, vertical=True):
    g = lib.lin_grad([(o, c, 1) for o, c in stops], 0, 0, 0 if vertical else 1, 1 if vertical else 0)
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="url(#{g})"/>'


def soft(x, y, rx, ry, col, op):
    g = lib.rad_grad([(0, col, op), (.55, col, op * .45), (1, col, 0)], x, y, rx, ry)
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#{g})"/>'


def touch_rings(x, y, t, t0, k=1.0, col="#ffe9c4"):
    """Кольца касания по стеклу к зрителю: расходятся и тают за 0.4 с."""
    o = ""
    for j in range(2):
        u = (t - t0 - .07 * j) / .4
        if 0 < u < 1:
            r = (26 + 110 * ease_out(u, 2)) * k
            pts = ellipse_pts(x, y, r, r * .92, 26)
            o += line(pts + [pts[0]], 6 * (1 - u) * k + 1, col, taper=0, wmin=1, seed=7750 + j, op=.85 * (1 - u))
    return o


def flame_world(cx, cy, ck, st):
    """Точка огонька кота в мире (примерно: хвост повёрнут на st['tail'])."""
    a = math.radians(st.get("tail", 0.0))
    px, py = CAT.TAIL_PIVOT
    fx, fy = CAT.FLAME_BASE[0] - px, CAT.FLAME_BASE[1] - 40 - py
    rx, ry = fx * math.cos(a) - fy * math.sin(a), fx * math.sin(a) + fy * math.cos(a)
    return cx + (px + rx - CAT.CX) * ck, cy + (py + ry - CAT.CBOT) * ck


# ═══════════════════════════════ s07: кот за ночным стеклом, «кот» рукописью ═══════════════════════════════
S07_KOT = (650.0, 515.0, 1.6)      # левый верх «кот» на стекле (мир) и размер пера


def s07(t):
    lib.dyn_begin()
    t0, t1 = T0("s07"), T1("s07")
    T_NAP, T_KOT, T_UZ = ws(23), ws(24), ws(26)
    kot_t0, kot_dur = T_NAP + .3, we(24) - (T_NAP + .3)
    o = []
    # снаружи: синяя ночь, стена дома вокруг окна
    o.append(grad_rect(-400, -400, 1480, 2400, [(0, "#121a3c"), (.6, "#0d1330"), (1, "#080b1e")]))
    for j in range(9):      # кладка стены снаружи — едва видна
        yy = 120 + j * 230
        o.append(line([(-300, yy), (1400, yy + 6)], 3, "#1b2550", taper=.1, wmin=.8, seed=7100 + j, op=.8))
    gx0, gy0, gx1, gy1 = 70.0, 170.0, 1010.0, 1330.0      # стекло (внутренний край рамы)
    # за стеклом: тёплая кухня — стена, полка со светом лампы
    room = [grad_rect(gx0, gy0, gx1, gy1, [(0, "#5a3a2c"), (.55, "#47302a"), (1, "#2c1d1d")])]
    lamp_x, lamp_y = 250.0, 250.0
    sway = 6 * math.sin(t * 1.7)
    room.append(soft(lamp_x + sway, lamp_y + 260, 520, 560, "#ffcf86", .55))
    room.append(line([(lamp_x, gy0 - 20), (lamp_x + sway * .6, lamp_y - 40)], 4, "#1a1210", taper=0, wmin=1, seed=7101))
    shade = [(lamp_x - 70 + sway, lamp_y + 30), (lamp_x - 34 + sway, lamp_y - 46), (lamp_x + 34 + sway, lamp_y - 46), (lamp_x + 70 + sway, lamp_y + 30)]
    room.append(shape(shade, "#d98b3a", blob([(lamp_x + 10 + sway, lamp_y - 46), (lamp_x + 34 + sway, lamp_y - 46), (lamp_x + 70 + sway, lamp_y + 30),
                                              (lamp_x + 30 + sway, lamp_y + 30)], "#a8622a", .8), w=4.0, seed=7102))
    room.append(blob(ellipse_pts(lamp_x + sway, lamp_y + 34, 48, 12, 14), "#fff3cf", .95))
    # дальняя стена: край стола внизу справа — тёмный силуэт ниже букв
    room.append(shape(rect(gx1 - 300, 980, gx1 + 20, 1010), "#3b2722", "", w=4.0, seed=7104))
    room.append(shape(rect(gx1 - 270, 1010, gx1 - 250, 1190), "#2c1d1a", "", w=3.4, seed=7103))
    # подоконник внутри
    sill_y = 1190.0
    room.append(shape(rect(gx0 - 10, sill_y, gx1 + 10, sill_y + 70), "#c99a6a", blob(rect(gx0 - 10, sill_y + 40, gx1 + 10, sill_y + 70), "#9c7048", .9)
                      + line([(gx0 + 30, sill_y + 14), (gx1 - 200, sill_y + 12)], 3, "#e2bb8c", seed=7105, op=.8), w=4.4, seed=7106))
    room.append(grad_rect(gx0, sill_y + 70, gx1, gy1, [(0, "#2a1b18"), (1, "#1a1110")]))
    # кот на подоконнике
    ck = 2.02
    cpos = (360.0, sill_y + 22)
    reach = ease_out(clamp((t - (T_NAP - .14)) / .14), 2) * (1 - ease_io(clamp((t - (T_KOT + .45)) / .25)))
    taps = [T_NAP + .02, T_NAP + .22]
    tap = max(bump(t, tt, .16) for tt in taps)
    uz = ease_io(clamp((t - (T_UZ - .06)) / .2))
    fl = bump(t, T_UZ - .02, .5)
    st = dict(turn=.04 * math.sin(t * 1.1), look=(.05 + .1 * math.sin(t * .9), .05), tilt=2.5 * math.sin(t * 1.3) - 11 * uz,
              tail=-8 + 9 * math.sin(t * 2.2), ear=5 * math.sin(t * 3.1) + 9 * bump(t, T_KOT, .25), perk=.5 * reach + .4 * uz,
              paw=.95 * reach, paw_dx=40 - 18 * tap, flame_e=1.0 + 2.6 * fl + .4 * uz,
              blink=1.0 if abs(t - (t0 + .55)) < .05 else 0.0, smile=0.0)
    hop = 10 * bump(t, T_NAP - .15, .3)
    room.append(blob(ellipse_pts(cpos[0] + 30, cpos[1] + 2, 190 * ck / 2, 16, 18), "#1a0f0c", .35))
    room.append(CAT.draw(cpos[0], cpos[1] - hop, ck, st, t))
    if fl > .01:
        fx, fy = flame_world(cpos[0], cpos[1] - hop, ck, st)
        room.append(P.glow(fx, fy, 230, 1.1 * fl, "#ffc060"))
    tip = people.cat_paw_tip(cpos[0], cpos[1] - hop, ck, st)
    c = lib.clip_rect(gx0, gy0, gx1 - gx0, gy1 - gy0)
    o.append(f'<g clip-path="url(#{c})">{"".join(room)}</g>')
    # стекло: блики, отражение луны, капли росы (едут медленно вниз)
    gl = []
    mx, my = 880.0, 330.0
    gl.append(f'<circle cx="{mx}" cy="{my}" r="120" fill="#c9d4ff" opacity=".07"/>')
    gl.append(shape(ellipse_pts(mx, my, 54, 54, 20), "#e8e6d8", blob(ellipse_pts(mx + 14, my + 8, 18, 14, 10), "#c9c4b0", .8), w=3, seed=7110,
                    attrs='opacity=".5"'))
    for j, (a, b) in enumerate((((120, 520), (420, 220)), ((160, 660), (520, 300)), ((700, 1240), (980, 960)))):
        gl.append(line([a, b], 26 - 8 * j, "#ffffff", taper=.6, wmin=.2, seed=7111 + j, op=.06))
    rs = np.random.RandomState(77)
    for j in range(16):
        x = rs.uniform(gx0 + 30, gx1 - 30)
        y = (rs.uniform(gy0, gy1) + 18 * t * rs.uniform(.4, 1.0)) % (gy1 - gy0) + gy0
        if 620 < x < 1010 and 380 < y < 540:
            continue        # за буквами «кот» ни одной капли
        r = rs.uniform(4, 9)
        gl.append(blob(ellipse_pts(x, y, r * .8, r, 8), "#dfe8ff", .22) + blob(ellipse_pts(x - r * .25, y - r * .3, r * .3, r * .3, 6), "#ffffff", .5))
    o.append(f'<g clip-path="url(#{c})">{"".join(gl)}</g>')
    # след лапы на стекле (тёплое пятно запотевания) и кольца стука
    if t > taps[0]:
        fade = clamp(1 - (t - taps[0]) / 1.4)
        o.append(blob(ellipse_pts(tip[0], tip[1] - 14, 34, 28, 14), "#fff4dc", .18 * fade))
    for tt in taps:
        o.append(touch_rings(tip[0], tip[1] - 14, t, tt, 1.0))
    if reach > .05:     # подушечка лапы прижата к стеклу: к зрителю, растёт на стуке
        pk = ck * .5 * (.75 + .25 * reach) * (1 + .22 * tap)
        px, py = tip[0], tip[1] - 14
        pad = shape(ellipse_pts(0, 0, 58, 50, 16), CAT.CAT, blob(ellipse_pts(14, 10, 40, 30, 12), CAT.CAT_SH, .7) +
                    shape(ellipse_pts(0, 12, 22, 17, 12), "#e08a4a", "", w=3.0, seed=7131) +
                    "".join(shape(ellipse_pts(bx, by, 10, 11, 10), "#e08a4a", "", w=2.6, seed=7132 + j)
                            for j, (bx, by) in enumerate(((-30, -18), (-11, -30), (11, -30), (30, -18)))), w=4.4, seed=7130)
        o.append(f'<g transform="translate({px:.1f} {py:.1f}) scale({pk:.3f})" opacity="{min(1.0, reach * 1.4):.2f}">{pad}</g>')
    # рукописное «кот» светлыми чернилами
    o.append(hand_kot.kot(t, kot_t0, kot_dur, S07_KOT[0], S07_KOT[1], S07_KOT[2], col="#f2eee2"))
    # рама снаружи
    fr = "#253058"
    o.append(f'<path d="M{gx0 - 60} {gy0 - 60}H{gx1 + 60}V{gy1 + 60}H{gx0 - 60}Z M{gx0} {gy0}V{gy1}H{gx1}V{gy0}Z" fill="{fr}" fill-rule="evenodd"/>')
    o.append(line(rect(gx0 - 60, gy0 - 60, gx1 + 60, gy1 + 60) + [(gx0 - 60, gy0 - 60)], 5, INK, taper=0, wmin=1, seed=7120))
    o.append(line(rect(gx0, gy0, gx1, gy1) + [(gx0, gy0)], 4, INK, taper=0, wmin=1, seed=7121))
    o.append(blob(rect(gx0 - 60, gy0 - 60, gx1 + 60, gy0 - 40), "#3a4880", .7))
    o.append(shape(rect(gx0 - 110, gy1 + 60, gx1 + 110, gy1 + 120), "#33406e", blob(rect(gx0 - 110, gy1 + 96, gx1 + 110, gy1 + 120), "#1b2348", .9), w=4.4,
                   seed=7122))
    # камера: лёгкий наезд к коту, «кот» — мягкий удар-наезд +6 %
    u = ease_io(clamp((t - (t0 - .2)) / (t1 - t0 + .4)))
    s = lerp(1.0, 1.07, u) * (1 + .06 * bump(t, T_KOT, .42))
    cx = lerp(560, 520, u) + 3 * math.sin(t * 1.3)
    cy = lerp(950, 910, u) + 3 * math.sin(t * 1.6)
    body = whip_wrap("".join(o), t, t0)
    return frame_svg(body, cx, cy, s, lerp(.5, -.3, u), bg="#080b1e")


# ═══════════════════════════════ s09: тень отца и железная бирка ═══════════════════════════════
def s09(t):
    lib.dyn_begin()
    t0, t1 = T0("s09"), T1("s09")
    T_NAP, T_TAK, T_ZV, T_SEB, T_LEN = ws(36), ws(37), we(40), ws(41), ws(42)
    o = []
    floor_y = 1290.0
    # тёмная комната, холодный свет сверху на Диму
    o.append(grad_rect(-500, -400, 1600, floor_y, [(0, "#0c1024"), (.5, "#121834"), (1, "#18203f")]))
    o.append(grad_rect(-500, floor_y, 1600, 2400, [(0, "#10142a"), (1, "#070915")]))
    o.append(line([(-500, floor_y), (1600, floor_y + 4)], 4, "#2a3462", taper=0, wmin=1, seed=7201))
    dx_, hipy = 790.0, 0.0
    flick = 1 + .03 * math.sin(t * 11.3) * math.sin(t * 3.1)
    o.append(soft(dx_ - 160, 700, 760, 820, "#9fb4ff", .3 * flick))       # холодный свет на стене: на нём читается тень отца
    cone = [(dx_ - 90, -300), (dx_ + 90, -300), (dx_ + 380, floor_y + 40), (dx_ - 380, floor_y + 40)]
    g = lib.lin_grad([(0, "#cfdcff", .16), (1, "#cfdcff", .02)], 0, 0, 0, 1)
    o.append(f'<path d="{lib.fill_d(cone)}" fill="url(#{g})"/>')
    o.append(blob(ellipse_pts(dx_, floor_y + 18, 330, 40, 22), "#8ea2e0", .22 * flick))
    # тень отца: входит с левого края, палец на «напишешь», уходит после «себя»
    sh_in = ease_out(clamp((t - (t0 - .2)) / .55), 3)
    sh_out = ease_in(clamp((t - (T_SEB + .25)) / .5), 2)
    sx = lerp(-560, 70, sh_in) - 640 * sh_out
    jab = bump(t, T_NAP, .3)
    pu = ease_out(clamp((t - (T_NAP - .18)) / .2), 2)
    sk = .9
    shy = floor_y - 640 * sk * 1.04
    shf = people.father_shadow(sx, shy, sk, ("sit", "point"), pu, t, col="#03050d", op=.95, op_fill=.3, w=9.0,
                               arms={"n": ("ik", (sx + 330 * sk * 1.04 * pu + 150 * sk * (1 - pu), shy - (390 * pu + 200 * (1 - pu)) * sk * 1.04), -1)})
    o.append(f'<g transform="translate({22 * jab:.1f} 0)" opacity="{1 - .8 * sh_out:.3f}">{shf["svg"]}</g>')
    finger = (shf["finger"][0] + 22 * jab, shf["finger"][1])
    # Дима (смотрит влево, к тени): вздрагивает на пальце, бирка прилипает, тянет вниз
    tug = ease_out(clamp((t - T_LEN) / .42), 2)
    stick = clamp((t - T_SEB) / .05)
    k = .78
    sink = 46 * tug + 14 * kick(t, T_SEB, .3, 2.6, 4)
    hip = (dx_, floor_y - 640 * k + sink)
    feet = {"n": ((dx_ - 50 * k, floor_y - 6), 0.0), "f": ((dx_ + 40 * k, floor_y), 0.0)}
    if t < T_NAP:
        ex = "look77"
    elif t < T_SEB:
        ex = dict(people.EXPR["dima"]["look77"], brows="worry", lid=1.0, look=(.7, -.1))
    elif t < T_LEN:
        ex = "tag77"
    else:
        ex = "slouch77"
    flinch = bump(t, T_NAP + .02, .3)
    fig = people.dima77(dx_, hip[1], k, ex, ("di_stand", "di_slouch"), t, u=tug, feet=feet, flip=True,
                        lean_add=-.06 * flinch + .05 * stick * (1 - tug), head_add=-.1 * flinch)
    o.append(fig["svg"])
    # бирка: висит на пальце тени → летит тяжёлой дугой с вращением → прилипает к груди
    hx, hy = fig["head"]
    chest = (hx + 6, hy + 300 * k * (1 + .1 * tug))
    tk = .8
    fly = clamp((t - T_TAK) / max(.2, T_SEB - T_TAK))
    if t < T_TAK:
        tp = (finger[0] + 6, finger[1] - 6)
        rot = 8 * math.sin(t * 5)
        tag = P.iron_tag(tp[0], tp[1], tk, rot, cord=70)
        if pu > .5 and sh_out < .2:
            o.append(tag)
    elif t < T_SEB:
        e = ease_in(fly, 1.6)
        a = (finger[0] + 6, finger[1] - 6)
        bx = lerp(a[0], chest[0], e)
        by = lerp(a[1], chest[1] - 40, e) - 70 * math.sin(math.pi * e)
        rot = -340 * (1 - (1 - fly) ** 2) + 20
        o.append(P.iron_tag(bx, by, tk, rot, cord=70))
        for j in range(3):      # след полёта
            ee = max(0.0, e - .06 * (j + 1))
            tx = lerp(a[0], chest[0], ee)
            ty = lerp(a[1], chest[1] - 40, ee) - 70 * math.sin(math.pi * ee)
            o.append(line([(tx, ty + 60), (bx, by + 60)], 10 - 3 * j, "#8ea2e0", taper=.8, wmin=.1, seed=7210 + j, op=.25))
    else:
        sw = 18 * kick(t, T_SEB, .35, 2.2, 4) + 6 * kick(t, T_LEN, .4, 1.6, 3)
        # шнурок вокруг шеи
        nk = (hx + 10, hy + 150 * k)
        top = (chest[0], chest[1] - 40)
        o.append(line([(nk[0] - 50 * k, nk[1] - 10), (top[0] - 14, top[1] + 6)], 4.4, "#6B5B3A", taper=.1, wmin=.7, seed=7220))
        o.append(line([(nk[0] + 50 * k, nk[1] - 10), (top[0] + 14, top[1] + 6)], 4.4, "#6B5B3A", taper=.1, wmin=.7, seed=7221))
        o.append(P.iron_tag(chest[0], chest[1] - 40, tk, sw, cord=40))
        # звяк: короткие штрихи удара
        u = (t - T_SEB) / .3
        if 0 < u < 1:
            for j in range(5):
                a_ = math.radians(-150 + 70 * j)
                r0, r1 = 90 + 40 * u, 130 + 60 * u
                cx_, cy_ = chest[0], chest[1] + 40
                o.append(line([(cx_ + r0 * math.cos(a_), cy_ + r0 * math.sin(a_)), (cx_ + r1 * math.cos(a_), cy_ + r1 * math.sin(a_))], 7 * (1 - u) + 1,
                              "#dfe6ff", taper=.6, wmin=.2, seed=7230 + j, op=.9 * (1 - u)))
        if tug > .02:      # тяжесть: дуги вниз
            for j in range(2):
                yy = chest[1] + 160 + 30 * j + 30 * tug
                o.append(line([(chest[0] - 40 + 10 * j, yy), (chest[0], yy + 24), (chest[0] + 40 - 10 * j, yy)], 4, "#8ea2e0", taper=.5, wmin=.2,
                              seed=7240 + j, op=.7 * tug * (1 - .5 * j)))
    # камера: хлёст, медленный наезд; «лентяем» — удар-наезд и тряска, дальше камера проседает с Димой
    u = ease_io(clamp((t - (t0 - .2)) / (t1 - t0 + .4)))
    pk = kick(t, T_LEN, .35, 1.0, 4) if t >= T_LEN else 0.0
    shk = kick(t, T_SEB, .25, 7, 6) + .7 * kick(t, T_LEN, .3, 6, 5)
    s = lerp(1.0, 1.1, u) * (1 + .09 * max(0.0, pk))
    cx = lerp(600, 700, u) + 12 * shk
    cy = lerp(880, 860, u) + 70 * tug - 8 * shk
    body = whip_wrap("".join(o), t, t0, dx=640.0)
    return frame_svg(body, cx, cy, s, lerp(-.4, .3, u) + .6 * shk, bg="#070915")


def lerp_feet(a, b, u):
    return {sd: (lerp2(a[sd][0], b[sd][0], u), lerp(a[sd][1], b[sd][1], u)) for sd in ("n", "f")}


def stand_feet(x, y, k, who="father77"):
    return people.stand_kw(x, y, k, who, spread=80 if who == "father77" else 60)["feet"]


# ═══════════════════════════════ s12: гараж, доска на одном шурупе, отец на ведре ═══════════════════════════════
def s12(t):
    lib.dyn_begin()
    t0, t1 = T0("s12"), T1("s12")
    T_SER, T_RUG, T_SEB, T_LEN = ws(55), ws(57), ws(58), ws(59)
    g = R.garage77(t, lit=1.0)
    FL = g["floor"]
    o = [g["bg"]]
    o.append(P.garage_junk(-60, FL, .9))
    # полка: одна доска на одном шурупе — срывается одним концом и качается маятником
    sx_, sy_, sk_ = 960.0, 600.0, 1.0
    if t < T_SER:
        sw = 2.5 * math.sin(t * 14) * clamp((t - (t0 - .2)) / .3)       # доска уже дрожит с кадра 0
    else:
        u = t - T_SER
        drop = 38 * ease_out(clamp(u / .16), 2)
        sw = drop + 18 * math.exp(-2.2 * u) * math.sin(2 * math.pi * 1.6 * u + .3) * clamp(u / .16)
    o.append(P.shelf(sx_, sy_, sk_, boards=2, hang_one=True, swing=-sw))
    if T_SER < t < T_SER + .35:       # пыль с шурупа
        o.append(P.dust_puff(sx_ - 200, sy_ + 190, .7, (t - T_SER) / .35, seed=12))
    # ведро вверх дном (отец сядет на него)
    fx = 610.0
    bk = 1.0
    bucket_top = FL - 180 * bk
    o.append(P.paint_bucket(fx - 30, FL, bk, 0.0, upside=True))
    # кот на ящике: смотрит на отца с сочувствием, ухо дёргается
    bx, by = g["box"]
    bx += 60
    ck = .62
    ear_tw = 14 * (bump(t, T_RUG + .05, .18) + bump(t, T_LEN + .05, .18))
    cst = dict(turn=-.45, look=(-.75, .25 + .25 * clamp((t - T_SEB) / .3)), tilt=6 + 4 * math.sin(t * 1.2) + 6 * clamp((t - T_LEN) / .3),
               tail=-6 + 8 * math.sin(t * 2.0), ear=ear_tw + 3 * math.sin(t * 2.7), perk=.6 * bump(t, T_SER, .35),
               blink=1.0 if abs(t - (T_LEN + .35)) < .05 else 0.0)
    o.append(blob(ellipse_pts(bx - 20, by + 4, 90, 10, 14), "#000000", .2))
    o.append(CAT.draw(bx - 20, by, ck, cst, t))
    # отец: стоит → ладонь по лбу → садится на ведро → голова в ладонях
    k = .74
    sc = k * people.HEIGHT["father77"]
    hip_st = FL - (people.LEG_LEN - 12) * sc
    hip_sit = bucket_top - 18
    sit_u = ease_io(clamp((t - (T_SEB - .06)) / .32))
    hip_y = lerp(hip_st, hip_sit, sit_u) + 6 * bump(t, T_SEB + .26, .2)
    hip_x = lerp(fx - 40, fx - 30, sit_u)
    feet = lerp_feet(stand_feet(hip_x, hip_st, k), people.sit_feet(hip_x, hip_sit, k, ground=(FL - hip_sit) / sc, fwd=230), sit_u)
    flinch = bump(t, T_SER, .3)
    if t < T_RUG - .14:
        pose, u, ex = ("drop", "drop"), 1.0, dict(people.EXPR["father77"]["surprised" if t > T_SER else "look_up"], look=(.55, -.75))
    elif t < T_SEB:
        pose, u, ex = ("drop", "forehead"), ease_out(clamp((t - (T_RUG - .14)) / .14), 2), "ashamed"
    elif t < T_LEN - .04:
        pose, u, ex = ("forehead", "bucket"), ease_io(clamp((t - T_SEB) / .3)), "ashamed"
    else:
        pose, u, ex = ("bucket", "head_hands"), ease_out(clamp((t - (T_LEN - .04)) / .26), 2), "sad"
    slap = bump(t, T_RUG, .16)
    fig = people.father(hip_x, hip_y, k, ex, pose, t, u, feet=feet, lean_add=-.05 * flinch + .06 * slap, head_add=-.12 * flinch - .1 * slap)
    o.append(fig["svg"])
    if T_RUG - .02 < t < T_RUG + .25:       # шлепок: штрихи у лба
        hx, hy = fig["head"]
        uu = (t - (T_RUG - .02)) / .27
        for j in range(3):
            a_ = math.radians(-120 + 35 * j)
            o.append(line([(hx + 60 + 70 * math.cos(a_), hy - 80 + 70 * math.sin(a_)), (hx + 60 + 120 * math.cos(a_), hy - 80 + 120 * math.sin(a_))],
                          6 * (1 - uu) + 1, INK, taper=.6, wmin=.2, seed=7300 + j, op=1 - uu))
    o.append(g["light"])
    # камера: медленный наезд, удар-наезд на «ругал», к концу проседает за отцом
    u_ = ease_io(clamp((t - (t0 - .2)) / (t1 - t0 + .4)))
    pk = max(0.0, kick(t, T_RUG, .3, .9, 4))
    s = lerp(.96, 1.04, u_) * (1 + .08 * pk)
    cx = lerp(760, 740, u_)
    cy = lerp(930, 900, u_) + 90 * ease_io(clamp((t - T_SEB) / .7))
    return frame_svg("".join(o), cx, cy, s, lerp(.3, -.4, u_), bg="#8c8f93")


SCENES = {"s07": s07, "s09": s09, "s12": s12}


def frame(sid, t):
    return SCENES[sid](t)
