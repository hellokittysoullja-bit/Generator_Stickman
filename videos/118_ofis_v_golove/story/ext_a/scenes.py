"""Рилс 118 «Офис в голове», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Место: офис внутри головы Димы — розовые стены
с извилинами, три стола, человечки-таблички «СРОЧНОЕ», «ИНТЕРЕСНОЕ», «ТРЕВОГА»; кот-менеджер в галстуке. Призыв — TG-карточка v5.
NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people, REPO, COMMON  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "scripts"))
import story_cta_tg as TG  # noqa: E402

HIT = stress(2, .4)
SKIN, SKIN_SH = "#ecc4a2", "#d9a984"
OFL = 1560.0
DESKS = (260.0, 540.0, 820.0)
DESK_TOP = OFL - 250
URG, INT, ANX = ("СРОЧНОЕ", "#e2453a"), ("ИНТЕРЕСНОЕ", "#2f8fe0"), ("ТРЕВОГА", "#9a6fd1")


# ═════════════ человечки-таблички ═════════════
def worker(x, y, k, who, t, pose="rest", mood="calm", phase=0.0, rot=0.0, seat=False):
    """Человечек с табличкой на груди. (x, y) — ступни (или сиденье при seat). pose: rest, run, up (рупор), type, give.
    mood: calm, sleep, panic, happy, shout."""
    label, col = who
    o = []
    hip = -110 if not seat else 0
    sw = math.sin(phase)
    if pose == "run":
        legs = [((-18, hip), (-18 - 50 * sw, 0)), ((18, hip), (18 + 50 * sw, 0))]
    elif seat:
        legs = [((-20, 0), (40, 10)), ((20, 0), (70, 10))]
    else:
        legs = [((-20, hip), (-26, 0)), ((20, hip), (26, 0))]
    for a, b in legs:
        o.append(line([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 4), b], 16, "#2c3554", taper=0, wmin=1, seed=4000))
        o.append(shape(ellipse_pts(b[0] + 10, b[1] - 4, 22, 12, 10), "#1c1622", "", w=2, seed=4001))
    by = hip - 150
    body = shape(lib.rrect(-55, by, 55, hip + 10, 26), col, blob(lib.rect_pts(20, by + 10, 55, hip + 10), lib.mul(col, (.82, .82, .82)), .6), w=4.4,
                 seed=4002)
    sh_l, sh_r = (-48, by + 25), (48, by + 25)
    if pose == "up":
        arms = [(sh_l, (-80, by + 90)), (sh_r, (90, by - 40))]
    elif pose == "run":
        arms = [(sh_l, (-70 + 40 * sw, by + 90)), (sh_r, (90, by + 20))]
    elif pose == "type":
        arms = [(sh_l, (60, by + 110 + 6 * math.sin(t * 30))), (sh_r, (100, by + 100 - 6 * math.sin(t * 30)))]
    elif pose == "give":
        arms = [(sh_l, (-70, by + 100)), (sh_r, (110, by + 40))]
    else:
        arms = [(sh_l, (-70, by + 110)), (sh_r, (70, by + 110))]
    for a, b in arms:
        o.append(line([a, b], 14, lib.mul(col, (.85, .85, .85)), taper=0, wmin=1, seed=4003))
        o.append(shape(ellipse_pts(b[0], b[1], 14, 14, 10), SKIN, "", w=2.6, seed=4004))
    o.append(body)
    sw_ = max(110.0, 22 * len(label) + 20)
    o.append(shape(lib.rrect(-sw_ / 2, by + 40, sw_ / 2, by + 100, 10), "#ffffff", plain(label, 0, by + 84, 30, fill=col, anchor="middle"), w=3, seed=4005))
    hy = by - 70
    o.append(shape(ellipse_pts(0, hy, 62, 66, 22), SKIN, blob(ellipse_pts(24, hy + 10, 34, 50, 14), SKIN_SH, .5), w=4.4, seed=4006))
    o.append(shape([(-50, hy - 40, 1), (-20, hy - 80, 1), (10, hy - 70, 1), (40, hy - 84, 1), (56, hy - 30, 1), (0, hy - 50, 1)], "#3a2a22", "", w=3,
                   seed=4007))
    if mood == "sleep":
        o.append(line([(-30, hy + 4), (-18, hy + 10), (-6, hy + 4)], 4, seed=4008) + line([(10, hy + 4), (22, hy + 10), (34, hy + 4)], 4, seed=4009))
        o.append(line([(-6, hy + 34), (8, hy + 36)], 4, seed=4010))
    else:
        big = 1.5 if mood in ("panic", "shout") else 1.0
        for ex in (-18, 22):
            o.append(blob(ellipse_pts(ex, hy, 9 * big, 11 * big, 10), "#ffffff") + blob(ellipse_pts(ex + 2, hy + 1, 5 * big, 6 * big, 8), "#111"))
        if mood in ("panic", "shout"):
            o.append(shape(ellipse_pts(4, hy + 36, 16, 20 if mood == "shout" else 10, 12), "#5a2b33", "", w=3, seed=4011))
        elif mood == "happy":
            o.append(line([(-14, hy + 30), (4, hy + 40), (22, hy + 30)], 5, seed=4012))
        else:
            o.append(line([(-8, hy + 34), (14, hy + 34)], 4, seed=4013))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k:.3f})">{"".join(o)}</g>'


def megaphone(x, y, k, rot=0.0, shout=0.0, t=0.0):
    o = shape([(0, -20, 1), (0, 20, 1), (120, 60, 1), (120, -60, 1)], "#e2453a", blob([(80, -40), (120, -60), (120, 60), (80, 40)], "#b8332a"), w=4,
              seed=4020)
    o += shape(lib.rrect(-30, -16, 4, 16, 6), "#5a5f6e", "", w=3, seed=4021)
    if shout > 0:
        for j in range(3):
            r = 60 + 50 * j + 30 * ((t * 4) % 1)
            o += line([(130 + r * math.cos(a), r * math.sin(a)) for a in [-.6 + .1 * q for q in range(13)]], 6, "#e2453a", seed=4022 + j, op=shout)
    return tf(o, x, y, k, rot)


def office(t, light="calm", papers=0.0):
    o = [rect(-1400, -1400, 2600, OFL, "#f5d3cf")]
    for j in range(-6, 14):
        y0 = 200 + 120 * j
        o.append(line([(-1400 + 140 * q, y0 + 26 * math.sin(q * 1.3 + j)) for q in range(30)], 5, "#e9b5ae", taper=0, wmin=1, seed=4030 + j % 20))
    o.append(rect(-1400, OFL, 2600, OFL + 1400, "#c8a08f"))
    o.append(shape(lib.rect_pts(140, 900, 380, 1080), "#ffffff", plain("ПЛАН", 260, 950, 40, fill="#1d2448", anchor="middle")
                   + line([(170, 1050), (230, 1010), (290, 1030), (350, 970)], 6, "#e2453a", seed=4045), w=4, seed=4044))
    o.append(PR.clock(840, 960, 70, *PR.clock_hm(10, 10), seed=1))
    o.append(blob(ellipse_pts(540, OFL + 120, 520, 60, 30), "#b07f6e", .9))
    o.append(line([(-1400, OFL), (2600, OFL)], 5, seed=11))
    if light == "alarm":
        on = (t * 4) % 1 < .5
        o.append(shape(ellipse_pts(540, 760, 60, 40, 16), "#ff4a3a" if on else "#a02a20", "", w=4, seed=4040))
        if on:
            o.append(PR.glow(540, 790, 700, .35, "#ff4a3a"))
    else:
        o.append(shape(ellipse_pts(540, 760, 60, 40, 16), "#fff4c0", "", w=4, seed=4040))
        o.append(PR.glow(540, 800, 600, .2, "#fff4c0"))
    for j in range(int(10 * papers)):
        rs = (j * 37 % 17) / 17
        x = 100 + 880 * rs + 60 * math.sin(t * 3 + j)
        y = 760 + ((t * 300 + j * 140) % 800)
        o.append(tf(shape(lib.rect_pts(-40, -50, 40, 50), "#ffffff", "", w=3, seed=4050 + j), x, y, 1.0, 200 * t + 40 * j))
    return o


def desks(t, items=("", "", "")):
    o = []
    for j, x in enumerate(DESKS):
        o.append(PR.desk(x, DESK_TOP, w=220, depth=60, leg_h=230, seed=20 + j))
        if items[j]:
            o.append(items[j])
    return "".join(o)


def chair_at(x, y=OFL, spin=0.0):
    o = shape(lib.rrect(-70, -150, 70, -120, 10), "#5a5f6e", "", w=4, seed=4060)
    o += shape(lib.rrect(-60, -300, 60, -150, 20), "#7d8597", "", w=4, seed=4061)
    o += line([(0, -120), (0, -30)], 10, "#5a5f6e", taper=0, wmin=1, seed=4062)
    o += line([(-60, 0), (60, 0)], 10, "#5a5f6e", taper=0, wmin=1, seed=4063)
    return tf(o, x, y, 1.0, 0) if spin == 0 else f'<g transform="translate({x} {y}) scale({math.cos(spin):.3f} 1)">{o}</g>'


def tie_cat(x, y, k, t, st=None):
    """Кот-менеджер: кот + красный галстук."""
    o = cat(x, y, k, t, st)
    tie = shape([(CT.NECK[0] - 22, CT.NECK[1] + 4, 1), (CT.NECK[0] + 22, CT.NECK[1] + 4, 1), (CT.NECK[0] + 10, CT.NECK[1] + 30, 1),
                 (CT.NECK[0] + 30, CT.NECK[1] + 130, 1), (CT.NECK[0], CT.NECK[1] + 160, 1), (CT.NECK[0] - 30, CT.NECK[1] + 130, 1),
                 (CT.NECK[0] - 10, CT.NECK[1] + 30, 1)], "#d8352a", line([(CT.NECK[0] - 20, CT.NECK[1] + 70), (CT.NECK[0] + 20, CT.NECK[1] + 50)], 4, "#a0241c",
                                                                        seed=4071), w=4, seed=4070)
    o += f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-CT.CX} {-CT.CBOT})">{tie}</g>'
    return o


def card2(x, y, k, u=1.0, rot=0.0):
    if u <= 0:
        return ""
    o = shape(lib.rrect(-90, -60, 90, 60, 14), "#fff6b0", text("2 МИН", 0, 20, 52, fill="#1d2448", stroke="#fff6b0", sw=2), w=4, seed=4080)
    return tf(o, x, y, k * (lib.back_out(clamp(u), 2.0) if u < 1 else 1.0), rot)


def office_view(o, t, cx=540, cy=1150, s=1.05, rot=0.0, hit=None, amp=8):
    cx, cy, s = 540 + (cx - 540) * .5, 1200 + (cy - 1150) * .5, s * 1.4
    dx, dy = shake(t, hit, amp)
    return view("".join(o), cx + dx, cy + dy, s, rot, bg="#f5d3cf", t=t)


def chaos(t, a=0.0):
    o = office(t, "alarm", papers=1.0)
    o.append(desks(t))
    o.append(chair_at(370 + 30 * math.sin(t * 3), spin=t * 9))
    o.append(worker(90, OFL - 30, .8, URG, t, mood="sleep", rot=80))
    o.append(worker(540 + 300 * math.sin(t * 3), OFL, .85, INT, t, pose="run", mood="happy", phase=t * 14))
    o.append(chair_at(820))
    o.append(worker(820, OFL - 300, .85, ANX, t, pose="up", mood="shout"))
    o.append(megaphone(880 + 90 * .85, OFL - 300 - 330 * .85, .85, -20, 1.0, t))
    return o


def frame_s01(t):
    """ХУК: лицо Димы крупно, во лбу раскрывается круглое окно в офис-хаос; камера влетает в него."""
    o = [plain_room(t)]
    f = stand(540, t, "wow82", "d82_rest", head_add=.04)
    o.append(f["svg"])
    hx, hy = f["head"]
    r = 40 + 260 * ease_in2(clamp(t / .52))
    c = lib.clip_of(ellipse_pts(hx - 10, hy - 50, r, r, 40))
    inner = "".join(chaos(t))
    o.append(f'<g clip-path="url(#{c})"><g transform="translate({hx - 10} {hy - 50}) scale(.35) translate(-540 -1100)">{inner}</g></g>')
    o.append(line(ellipse_pts(hx - 10, hy - 50, r, r, 40) + [ellipse_pts(hx - 10, hy - 50, r, r, 40)[0]], 6, seed=4090))
    s = 1.6 + 1.8 * ease_in2(clamp(t / .52))
    return hook_view("".join(o), t, HIT, hx - 10, hy - 50 + 40 / s, s, 0)


def ease_in2(u):
    return u * u


def frame_s02(t):
    """«работает целый офис»: внутри головы хаос — мигалка, бумаги летят, «Интересное» носится, «Тревога» орёт, «Срочное» лежит."""
    a, b = T0("s02"), T1("s02")
    o = chaos(t)
    o.append(tie_cat(640, OFL, .75, t, dict(look=(-.4, -.6), perk=1.0, ear_r=.3)))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 540, 1150, 1.15 - .1 * u, 0, W(5), 10)


def frame_s03(t):
    """«и никто в нём не работает»: столы пустые, стул крутится, бумаги на полу, работники разошлись."""
    a, b = T0("s03"), T1("s03")
    o = office(t, "calm", papers=.4)
    o.append(desks(t, (PR.paper_pile(260, DESK_TOP - 10, .5, seed=1), "", PR.paper_pile(820, DESK_TOP - 10, .5, seed=2))))
    o.append(chair_at(540, spin=t * 6))
    for j in range(6):
        o.append(tf(shape(lib.rect_pts(-40, -50, 40, 50), "#ffffff", "", w=3, seed=4100 + j), 120 + 160 * j, OFL - 10, 1.0, 80 + 20 * j))
    o.append(PR.question_mark(540, 700, 2.0, pop(t, W(10), .25), col="#e2453a") if t > W(10) else "")
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 540, 1150, 1.05 + .06 * u, 0, W(10), 8)


def frame_s04(t):
    """«„Срочное“ спит под столом с понедельника»: «СРОЧНОЕ» храпит под столом, Z, на стене листок «ПН»."""
    a, b = T0("s04"), T1("s04")
    o = office(t)
    o.append(desks(t))
    o.append(worker(90, OFL - 40, .85, URG, t, mood="sleep", rot=90))
    o.append(PR.zzz(380, OFL - 220, 1.4, t, 1.0))
    cal = shape(lib.rect_pts(-90, -110, 90, 110), "#fbf8f1", blob(lib.rect_pts(-90, -110, 90, -50), "#c8553d") + text("ПН", 0, 60, 90, fill="#1d2448",
                                                                                                                   stroke="#ffffff", sw=4), w=4, seed=4110)
    o.append(tf(cal, 520, 1060, pop(t, W(17) - .2, .25)) if t > W(17) - .2 else "")
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 300, 1250, 1.45 + .08 * u, 0, W(17), 8)


def frame_s05(t):
    """«„Интересное“ носится с кофе»: «ИНТЕРЕСНОЕ» бегает по офису с кружкой, кофе плещет, дуги скорости."""
    a, b = T0("s05"), T1("s05")
    o = office(t)
    o.append(desks(t))
    x = 150 + 800 * (.5 + .5 * math.sin((t - a) * 3.5))
    dirv = math.cos((t - a) * 3.5)
    o.append(worker(x, OFL, .9, INT, t, pose="run", mood="happy", phase=t * 16))
    o.append(PR.mug(x + 90 * (1 if dirv > 0 else -1), OFL - 350, .8, col="red", steam=1.0, t=t, seed=1))
    o.append(PR.speed_arcs(x - 180 * (1 if dirv > 0 else -1), OFL - 300, 1.2, 1.0, t, seed=7, n=3, ang=180 if dirv > 0 else 0))
    o.append(PR.splash_drops(x + 90, OFL - 400, 1.0, (t * 2) % 1, seed=2))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 540, 1200, 1.1 + .06 * u, 0, W(21), 6)


def folder_new(x, y, k, u, rot=0.0):
    if u <= 0:
        return ""
    o = shape([(-110, -70, 1), (-40, -70, 1), (-20, -90, 1), (110, -90, 1), (110, 70, 1), (-110, 70, 1)], "#ffd27a",
              plain("НОВЫЙ", 0, -10, 36, fill="#5a3a20", anchor="middle") + plain("ПРОЕКТ", 0, 32, 36, fill="#5a3a20", anchor="middle"), w=4, seed=4120)
    return tf(o, x, y, k * (lib.back_out(clamp(u), 2.2) if u < 1 else 1.0), rot)


def frame_s06(t):
    """«и открывает новые проекты»: «Интересное» швыряет папки «НОВЫЙ ПРОЕКТ», они выскакивают по всему офису."""
    a, b = T0("s06"), T1("s06")
    o = office(t)
    o.append(desks(t))
    o.append(worker(540, OFL, .9, INT, t, pose="give", mood="happy"))
    pos = [(250, 700, -10), (820, 640, 8), (420, 500, 4), (700, 900, -6), (180, 1000, 12), (900, 1050, -4)]
    for j, (x, y, r) in enumerate(pos):
        o.append(folder_new(x, y, 1.0, ramp(t, a + .1 + .2 * j, .2), r))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 540, 1050, 1.0 + .06 * u, 0, W(24), 6)


def frame_s07(t):
    """«А „Тревога“ стоит на стуле»: «ТРЕВОГА» вскакивает на стул с рупором, мигалка."""
    a, b = T0("s07"), T1("s07")
    up = ease_out(ramp(t, a, W(30) - a))
    o = office(t, "alarm")
    o.append(desks(t))
    o.append(chair_at(700))
    o.append(worker(700, OFL - 300 * up, .9, ANX, t, pose="up", mood="panic"))
    o.append(megaphone(700 + 90 * .9, OFL - 300 * up - 330 * .9, .9, -20, 0.0, t))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 640, 1100, 1.2 + .06 * u, 0, W(30), 10)


def frame_s08(t):
    """«и орёт в рупор, что всё горит»: крупно «ТРЕВОГА» кричит в рупор, волны крика, огоньки вокруг."""
    a, b = T0("s08"), T1("s08")
    o = office(t, "alarm")
    o.append(desks(t))
    o.append(chair_at(700))
    o.append(worker(700, OFL - 300, .9, ANX, t, pose="up", mood="shout"))
    o.append(megaphone(700 + 90 * .9, OFL - 300 - 330 * .9, .9, -20, 1.0, t))
    for j in range(5):
        if t > W(36) - .1 + .05 * j:
            o.append(PR.att_flame(150 + 200 * j, OFL - 40 - 40 * (j % 2), 3.0 * pop(t, W(36) - .1 + .05 * j, .2), t, 1.0, seed=j))
    o.append(text("ГОРИТ!", 440, 1020, 120 * pop(t, W(37), .2), fill="#e2453a", stroke="#111", sw=10) if t > W(37) else "")
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 640, 1000, 1.2 + .1 * u, 0, W(37), 14)


def door(x, y, u):
    o = shape(lib.rect_pts(x - 160, y - 520, x + 160, y), "#3a2f2a", "", w=5, seed=4130)
    o += f'<g transform="translate({x - 160} 0) scale({max(.05, 1 - u):.3f} 1) translate({-(x - 160)} 0)">' + shape(
        lib.rect_pts(x - 160, y - 520, x + 160, y), "#c99a6b", shape(ellipse_pts(x + 110, y - 260, 14, 14, 10), "#6b432b", "", w=3, seed=4131), w=5,
        seed=4132) + "</g>"
    return o


def frame_s09(t):
    """«Тогда я нанял нового менеджера»: дверь офиса распахивается, свет, входит кот в галстуке; работники оборачиваются."""
    a, b = T0("s09"), T1("s09")
    op = ease_out(ramp(t, a, .35))
    o = office(t)
    o.append(desks(t))
    o.append(door(880, OFL, op))
    if op > .3:
        o.append(PR.glow(880, OFL - 260, 400, .5 * op, "#fff4c0"))
    walk = ease_out(ramp(t, a + .25, W(42) - a))
    o.append(tie_cat(940 - 260 * walk, OFL, 1.1, t, dict(look=(-.6, -.2), smile=1.0, walk=t * 6 if walk < 1 else None)))
    o.append(worker(260, OFL, .7, URG, t, mood="calm"))
    o.append(worker(420, OFL, .7, INT, t, mood="happy"))
    o.append(PR.sparkles(700, OFL - 300, 1.8, bump(t, W(42), .05, .5), t, seed=91, n=6, r=260))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 600, 1200, 1.05 + .06 * u, 0, W(42), 6)


def frame_s10(t):
    """«Он дал каждому одну задачу на две минуты»: кот раздаёт жёлтые карточки «2 МИН», каждый получает свою."""
    a, b = T0("s10"), T1("s10")
    o = office(t)
    o.append(desks(t))
    xs = (260, 540, 820)
    whos = (URG, INT, ANX)
    give = [W(45) - .1, W(47), W(49)]
    for j, (x, w_) in enumerate(zip(xs, whos)):
        got = t > give[j] + .2
        o.append(worker(x, OFL, .75, w_, t, pose="give" if got else "rest", mood="calm" if j != 2 else "panic"))
        if t > give[j]:
            fly = ease_out(ramp(t, give[j], .25))
            o.append(card2(400 + (x + 80 - 400) * fly, 1100 + (1050 - 1100) * fly, .8, 1.0, -6 + 12 * j))
    o.append(tie_cat(400, OFL, .8, t, dict(look=(.0, -.3), smile=.8)))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 540, 1100, 1.0 + .06 * u, 0, W(50), 6)


def frame_s11(t):
    """«и сел рядом»: кот запрыгивает на средний стол и садится, работники с карточками вокруг."""
    a, b = T0("s11"), T1("s11")
    j = ease_io(ramp(t, a, .4))
    o = office(t)
    o.append(desks(t))
    for x, w_ in zip((260, 820), (URG, ANX)):
        o.append(worker(x, OFL, .75, w_, t, pose="give", mood="calm"))
        o.append(card2(x + 80, 1050, .8))
    o.append(worker(540, OFL, .75, INT, t, pose="give", mood="happy"))
    o.append(tie_cat(540, OFL - (OFL - DESK_TOP) * j - 120 * math.sin(math.pi * j), .7, t, dict(look=(0, .3), smile=1.0, legs=1 - j if j < 1 else 0)))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 540, 1150, 1.05 + .06 * u, 0, W(52), 5)


def frame_s12(t):
    """«„Срочное“ проснулось»: «СРОЧНОЕ» открывает глаза, садится за стол и печатает, кот кивает."""
    a, b = T0("s12"), T1("s12")
    tw = W(55)
    o = office(t)
    o.append(desks(t, (PR.laptop(260, DESK_TOP - 6, .5, screen="lines", lines=clamp((t - tw) / 1.2), t=t, seed=1), "", "")))
    if t < tw:
        o.append(worker(90, OFL - 40, .85, URG, t, mood="sleep", rot=90))
    else:
        o.append(worker(150, OFL, .85, URG, t, pose="type", mood="happy" if t > tw + .3 else "panic"))
    o.append(tie_cat(540, DESK_TOP, .7, t, dict(look=(-.8, .3), smile=1.0)))
    o.append(PR.sparkles(140, 900, 1.6, bump(t, tw, .05, .5), t, seed=121, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 320, 1200, 1.35 + .06 * u, 0, tw, 8)


def frame_s13(t):
    """«„Интересное“ село»: «ИНТЕРЕСНОЕ» плюхается на стул за средний стол, ставит кружку и пишет."""
    a, b = T0("s13"), T1("s13")
    ts = W(57)
    o = office(t)
    o.append(desks(t, ("", PR.mug(620, DESK_TOP - 30, .6, col="red", steam=1.0, t=t, seed=2), "")))
    if t < ts:
        o.append(worker(700 - 200 * clamp((t - a) / (ts - a)), OFL, .85, INT, t, pose="run", mood="happy", phase=t * 16))
    else:
        o.append(worker(440, OFL, .85, INT, t, pose="type", mood="calm"))
    o.append(tie_cat(760, DESK_TOP, .7, t, dict(look=(-.8, .3), smile=1.0)))
    o.append(PR.sparkles(500, 950, 1.6, bump(t, ts, .05, .5), t, seed=131, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 560, 1200, 1.3 + .06 * u, 0, ts, 8)


def frame_s14(t):
    """«а „Тревога“ наконец замолчала»: «ТРЕВОГА» опускает рупор, слезает со стула и садится, мигалка гаснет."""
    a, b = T0("s14"), T1("s14")
    tq = W(60)
    down = ease_out(ramp(t, tq, .4))
    o = office(t, "alarm" if t < tq else "calm")
    o.append(desks(t))
    o.append(chair_at(800))
    o.append(worker(800, OFL - 300 * (1 - down), .9, ANX, t, pose="up" if down < .5 else "rest", mood="shout" if t < tq else "calm"))
    if down < .5:
        o.append(megaphone(800 + 81, OFL - 300 * (1 - down) - 297, .9, -20, 1.0 if t < tq else 0.0, t))
    else:
        o.append(megaphone(900, OFL - 20, .7, 80, 0.0, t))
    o.append(tie_cat(560, DESK_TOP, .7, t, dict(look=(.8, .3), smile=1.0 if t > tq else .4)))
    if t > W(61):
        o.append(text("тсс", 470, 1080, 200 * pop(t, W(61), .25), fill="#2f8fe0", stroke="#ffffff", sw=8))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 680, 1150, 1.2 + .06 * u, 0, tq, 8)


def cta(t, zoom=1.0, focus=None):
    c = SH["cta"]
    if "bg" not in TG._ST:
        TG._ST["bg"] = TG.background(lib)
        TG.prepare(COMMON)
        lib.static_done()
    lib.dyn_begin()
    body, (cx, cy, s, rot) = TG.layer(t, c["t0"], c["press"], COMMON)
    if focus:
        cx, cy = cx + (focus[0] - cx) * .3, cy + (focus[1] - cy) * .3
    return lib.svg(f'<rect width="1080" height="1920" fill="#6e4a32"/><g transform="{lib.cam(cx, cy, s * zoom, rot)}">{TG._ST["bg"]}{body}</g>{over(t)}')


def frame_s15(t):
    return cta(t)


def frame_s16(t):
    return cta(t, 1.08, (540, 1000))


def calm_office(t):
    o = office(t)
    o.append(desks(t, (PR.laptop(260, DESK_TOP - 6, .5, screen="lines", lines=.8, t=t, seed=1),
                       PR.mug(620, DESK_TOP - 30, .6, col="red", steam=1.0, t=t, seed=2),
                       PR.paper_stack(820, DESK_TOP - 10, .6, n=4, seed=3))))
    o.append(worker(150, OFL, .8, URG, t, pose="type", mood="happy"))
    o.append(worker(440, OFL, .8, INT, t, pose="type", mood="calm"))
    o.append(worker(720, OFL, .8, ANX, t, pose="type", mood="calm"))
    return o


def frame_s17(t):
    """«Сегодня мой офис впервые»: весь офис спокойно работает, кот-менеджер на шкафу кивает."""
    a, b = T0("s17"), T1("s17")
    o = calm_office(t)
    o.append(tie_cat(540, DESK_TOP, .6, t, dict(look=(0, .3), smile=1.0, tilt=4 * math.sin(t * 6))))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 540, 1100, 1.0 + .06 * u, -1 + 2 * u, W(78), 5)


def frame_s18(t):
    """«сдал отчёт вовремя»: «ИНТЕРЕСНОЕ» поднимает папку «ОТЧЁТ», шлёпается зелёный штамп «ВОВРЕМЯ», конфетти."""
    a, b = T0("s18"), T1("s18")
    ts = W(81)
    o = calm_office(t)
    f = shape(lib.rect_pts(-200, -140, 200, 140), "#e3c79a", plain("ОТЧЁТ", 0, 0, 80, fill="#5a3a20", anchor="middle"), w=5, seed=4140)
    if t > ts:
        s = 1.0 + 1.3 * (1 - ease_out(clamp((t - ts) / .25)))
        f += (f'<g transform="translate(0 40) rotate(-10) scale({s:.3f})"><rect x="-190" y="-55" width="380" height="110" rx="14" fill="none" stroke="#3fb26a" '
              f'stroke-width="12"/>' + text("ВОВРЕМЯ", 0, 32, 76, fill="#3fb26a", stroke="#3fb26a", sw=.01) + "</g>")
    o.append(tf(f, 540, 920, 1.0 * pop(t, a, .25)))
    o.append(PR.sparkles(540, 820, 2.2, bump(t, ts, .05, .6), t, seed=181, n=8, r=320))
    u = ease_io(ramp(t, a, b - a))
    return office_view(o, t, 540, 1080, 1.05 + .06 * u, 0, ts, 8)


def frame_s19(t):
    """Петля: кадр хука — лицо Димы, маленькое окно во лбу."""
    a, b = T0("s19"), T1("s19")
    o = [plain_room(t)]
    f = stand(540, t, "wow82", "d82_rest", head_add=.04)
    o.append(f["svg"])
    hx, hy = f["head"]
    r = 80
    c = lib.clip_of(ellipse_pts(hx - 10, hy - 50, r, r, 40))
    o.append(f'<g clip-path="url(#{c})"><g transform="translate({hx - 10} {hy - 50}) scale(.35) translate(-540 -1100)">{"".join(chaos(t))}</g></g>')
    o.append(line(ellipse_pts(hx - 10, hy - 50, r, r, 40) + [ellipse_pts(hx - 10, hy - 50, r, r, 40)[0]], 6, seed=4090))
    return loop_view("".join(o), t, a, b, HIT, hx - 10, hy - 50 + 60, 2.0)


def frame(sid, t):
    if sid not in ("s15", "s16"):
        lib.DEFS.clear()
    return globals()["frame_" + sid](t)
