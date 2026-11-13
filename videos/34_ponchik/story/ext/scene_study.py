"""Сцена study рилса 34 (s10, s11, s12): светлая комната опыта (Adams, Leary 2007). Без букв и логотипов.
s10 «сначала давали съесть пончик» (18.0–19.85): две девушки сидят за отдельными столиками лицом к нам; сверху в кадр
     опускаются две руки в белых рукавах халата и на «давали» (18.48) ставят перед ними тарелки с пончиками (розовая
     глазурь с посыпкой); девушки берут пончики и на «пончик» (19.24) обе откусывают — полукруг укуса, крошки.
s11 «Те, кому потом сказали» (19.85–21.3): шире; справа входит экспериментатор (женщина в белом халате, с
     планшетом-доской), подходит к девушке справа и на «сказали» (20.56) мягко наклоняется к ней; девушка слева сидит
     одна и виновато смотрит на свой надкушенный пончик. Камера дрейфует вбок.
s12 «бывает со всеми, не ругай себя» (21.3–23.2): крупно девушка справа и экспериментатор; на «бывает» (21.39)
     выскакивает облачко речи «Бывает со всеми!» (текст кодом), экспериментатор кладёт руку ей на плечо; на «себя»
     (22.68) девушка выдыхает и улыбается, плечи опускаются, рядом выскакивает сердечко.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import parts34 as P
import person
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, rad_grad,
                 rect_pts, shape, smooth, svg)

_ST = {}
DAVALI = P.wt("давали")         # 18.48
PONCHIK = P.wt("пончик", 19)    # 19.24
SKAZALI = P.wt("сказали")       # 20.56
BYVAET = P.wt("бывает", 21)        # 21.387
SEBYA = P.wt("себя", 22.5)          # 22.68

FLOOR = 1100                    # низ стены
TOP_Y = 995                     # столешница
TAB_BOT = 1235
GA = dict(skin="#f4d0b4", hair="ponytail", hair_c="#c8622a", top="#3a9a6a", low="#24484a", face=0.0, lashes=True)
GB = dict(skin="#8a5a3c", hair="curly", hair_c="#2a1a14", top="#d9467a", low="#2a2a3a", face=0.0, lashes=True)
EXP = dict(skin="#f2c9a8", hair="bun", hair_c="#5a3a26", top="#f7f7f2", low="#3a3f4c", face=-0.45, glasses=True, coat=True,
           blouse="#8fb4e0", lashes=True, shoes="#3a3440", sleeve="#f7f7f2")
XA, XB = 315, 770               # центры столиков
GY, GS = 1255, 0.95             # ступни сидящих (за столом), масштаб


def room():
    s = []
    s.append(f'<rect x="-800" y="-800" width="{W + 1600}" height="{FLOOR + 800}" fill="#e3eee8"/>')
    for k in range(-8, 16):
        s.append(f'<rect x="{-800 + k * 120}" y="-800" width="56" height="{FLOOR + 800}" fill="#d9e7e0"/>')
    g = rad_grad([(0, "#fffaf0", .8), (1, "#fffaf0", 0)], 540, 500, 760, 620)
    s.append(f'<rect x="-800" y="-800" width="{W + 1600}" height="{FLOOR + 800}" fill="url(#{g})"/>')
    s.append(blob([(-800, FLOOR), (W + 800, FLOOR), (W + 800, H + 800), (-800, H + 800)], "#c9d2dc"))
    s.append(blob([(-800, FLOOR - 30), (W + 800, FLOOR - 30), (W + 800, FLOOR), (-800, FLOOR)], "#f4f6f2"))
    s.append(line([(-800, FLOOR - 30), (W + 800, FLOOR - 30)], 2.6, INK, taper=.05, wmin=.8, seed=3001, op=.8))
    s.append(line([(-800, FLOOR), (W + 800, FLOOR)], 4.2, INK, taper=.05, wmin=.9, seed=3002))
    for k in range(-6, 16):
        x = 540 + k * 150
        s.append(line([(540 + (x - 540) * .4, FLOOR + 6), (x, H + 600)], 2, "#b3bdc9", taper=.1, wmin=.7, seed=3010 + k % 9, op=.7))
    # окно с жалюзи (день)
    wx0, wy0, wx1, wy1 = -40, 260, 300, 700
    inner = blob(rect_pts(wx0, wy0, wx1, wy1), "#a6d4f5") + blob([(wx0, 620), (60, 560), (140, 600), (220, 540), (wx1, 590), (wx1, wy1), (wx0, wy1)], "#8fbf7a")
    for k in range(9):
        y = wy0 + 14 + k * 30
        inner += blob(rect_pts(wx0, y, wx1, y + 12), "#f4f1e8", .92)
    s.append(shape(rect_pts(wx0, wy0, wx1, wy1), "#a6d4f5", inner, w=4.6, seed=3020))
    s.append(shape(rect_pts(wx0 - 16, wy1, wx1 + 16, wy1 + 18), "#f4f1e8", "", w=3.4, seed=3021))
    # часы на стене (без цифр — риски)
    cx, cy = 760, 330
    ticks = "".join(line([(cx + 52 * math.cos(a), cy + 52 * math.sin(a)), (cx + 62 * math.cos(a), cy + 62 * math.sin(a))], 4, INK, seed=3030 + k)
                    for k, a in enumerate(np.linspace(0, 2 * math.pi, 12, endpoint=False)))
    s.append(shape(ellipse_pts(cx, cy, 74, 74, 24), "#ffffff", ticks, w=5, seed=3031))
    # полка с папками и цветок
    s.append(shape(rect_pts(900, 520, 1240, 538), "#b98a5a", "", w=3.4, seed=3040))
    for k, (x, h, c) in enumerate([(920, 90, "#e2543f"), (952, 104, "#2f6db5"), (988, 84, "#f0b43a"), (1018, 98, "#3a9a6a")]):
        s.append(shape(rect_pts(x, 520 - h, x + 30, 520), c, blob(rect_pts(x + 18, 520 - h, x + 30, 520), lib.mul(c, (.8, .8, .85)), .8), w=3, seed=3041 + k))
    s.append(shape([(1090, 470), (1150, 470), (1140, 520, 1), (1100, 520, 1)], "#c96b4a", "", w=3, seed=3050))
    for k in range(5):
        a = -2.4 + k * 0.4
        s.append(shape(P.sausage([(1120, 470), (1120 + 40 * math.cos(a), 470 + 40 * math.sin(a)), (1120 + 70 * math.cos(a), 470 + 60 * math.sin(a))], 18, 10),
                       "#5aaa4e", "", w=3, seed=3060 + k))
    return "".join(s)


def table(x, sd):
    """Столик с белой скатертью (вид спереди): столешница, свисающая ткань с мягкими складками."""
    s = []
    w = 190
    s.append(blob(ellipse_pts(x, TAB_BOT + 6, w + 30, 18, 14), "#9aa4b4", .5, blur(4)))
    cloth = [(x - w, TOP_Y), (x + w, TOP_Y), (x + w + 10, TAB_BOT - 30, 1), (x + w - 20, TAB_BOT), (x + w * .5, TAB_BOT - 12), (x, TAB_BOT - 2),
             (x - w * .5, TAB_BOT - 12), (x - w + 20, TAB_BOT), (x - w - 10, TAB_BOT - 30, 1)]
    inner = blob([(x + w * .4, TOP_Y), (x + w + 12, TOP_Y), (x + w + 12, TAB_BOT), (x + w * .45, TAB_BOT)], "#dde2ea", .9)
    for k, xx in enumerate((x - w * .5, x, x + w * .5)):
        inner += line([(xx, TOP_Y + 40), (xx + 4, TAB_BOT - 14)], 2.4, "#c3cad6", seed=sd + 5 + k, op=.9)
    s.append(shape(cloth, "#fbfbf8", inner, w=4.4, seed=sd))
    top = [(x - w - 6, TOP_Y - 26, 1), (x + w + 6, TOP_Y - 26, 1), (x + w + 4, TOP_Y + 4, 1), (x - w - 4, TOP_Y + 4, 1)]
    s.append(shape(top, "#ffffff", blob([(x - w, TOP_Y - 4), (x + w, TOP_Y - 4), (x + w, TOP_Y + 4), (x - w, TOP_Y + 4)], "#e4e8ee"), w=4.2, seed=sd + 1))
    return "".join(s)


def wpt(gx, p):
    """Точка системы человека (ступни (0,0), рост ~700) → мир для девушки у столика gx."""
    return (gx + p[0] * GS, GY + p[1] * GS)


def lpt(gx, w):
    return ((w[0] - gx) / GS, (w[1] - GY) / GS)


PLATE_L = -268                   # уровень тарелки в системе девушки (столешница)


def girl(spec, gx, t, act, sd, extra=None):
    """Девушка за столиком (ноги скрыты скатертью). act(t) -> поза-словарь (hand_target, look, mouth, brow, …, donut)."""
    pose = act(t)
    pose.setdefault("blink", 0.0)
    bob = pose.pop("dy", 0.0)
    held = pose.pop("donut_in_hand", None)
    if held is not None:
        bites = held

        def item(h, a, bites=bites):
            return f'<g transform="translate({f(h[0])} {f(h[1] - 34)}) scale(.66)">{P.donut("pink", sd + 50, bites=bites)}</g>'
        pose["over_hand"] = {"R": item}
    body = person.draw(spec, dict(pose, no_arms=True, no_legs=True), gx, GY + bob, GS, sd=sd)
    arms = person.draw(spec, dict(pose, only_arms=True, no_legs=True), gx, GY + bob, GS, sd=sd)
    return body, arms


def plate_with_donut(x, y, bites=(), has_donut=True, sd=0, sc=1.0):
    d = f'<g transform="translate(0 -16) scale(.72)">{P.donut("pink", sd + 10, bites=bites)}</g>' if has_donut else ""
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{P.plate(sd, 92)}{d}</g>'


def white_arm(wx, wy, t_in, t_down, t_out, t, side, sd):
    """Рука экспериментатора снизу (из-за нижнего края кадра — она стоит у камеры) подносит тарелку на ладони и ставит
    на стол; потом уходит вниз. Возвращает (рука под тарелкой, позиция тарелки или None, тарелка ещё в руке?)."""
    u_in = ease_out(clamp((t - t_in) / (t_down - t_in)), 3)
    u_out = ease_in(clamp((t - t_out) / 0.3), 2)
    if t < t_in:
        return "", None, False
    hold = t < t_down + 0.04
    drop = 0 if hold else 900 * u_out
    hx, hy = wx + side * 30, wy + 26 + (1 - u_in) * 700 + drop
    if hy > 2300:
        return "", None, not hold
    shoulder = (wx + side * 330, 2200)
    elbow = ((shoulder[0] + hx) / 2 + side * 70, (shoulder[1] + hy) / 2 + 40)
    sl = "#f7f7f2"
    s = person.tube(shoulder, elbow, (hx, hy + 30), 74, 64, 56, sl, sd, inner_sh=True)
    ca = math.degrees(math.atan2(hy + 30 - elbow[1], hx - elbow[0])) - 90
    s += shape(lib.T(rect_pts(-34, -14, 34, 14, 6), hx, hy + 30, 1.0, ca), "#e6e6e0", "", w=3.4, seed=sd + 3)
    hand = person.fhand(hx, hy + 22, -90 - side * 10, "#f2c9a8", sd + 5, sc=0.95, curl=0.2)
    return s + hand, (hx - side * 30, hy - 26), hold


# ═══════════════════════════════ действия девушек (s10)
def act_a10(t):
    """Девушка слева: ждёт, смотрит на тарелку, берёт пончик (правой рукой — у нас справа) и откусывает на «пончик»."""
    return _act10(t, -0.02, 0)


def act_b10(t):
    return _act10(t, 0.04, 1)


def _act10(t, lag, i):
    grab, mouth_t = 18.82 + lag, PONCHIK - 0.06 + lag * .5
    up = ease_io(clamp((t - grab) / (mouth_t - grab)))
    down = ease_io(clamp((t - (PONCHIK + 0.25)) / 0.4))
    rest_r = (62, -282)
    plate = (24, PLATE_L - 14)
    mouth = (6, -540)
    low = (34, -430)
    pick = ease_io(clamp((t - (grab - 0.22)) / 0.22))
    if t < grab:
        r = (rest_r[0] + (plate[0] - rest_r[0]) * pick, rest_r[1] + (plate[1] - rest_r[1]) * pick)
    elif t < PONCHIK + 0.25:
        r = (plate[0] + (mouth[0] - plate[0]) * up, plate[1] + (mouth[1] - plate[1]) * up)
    else:
        r = (mouth[0] + (low[0] - mouth[0]) * down, mouth[1] + (low[1] - mouth[1]) * down)
    bitten = t >= PONCHIK + lag * .5
    chew = math.sin((t - PONCHIK) * 16) if bitten else 0.0
    look_y = 0.6 if DAVALI - 0.3 < t < 19.1 else (0.1 if t < DAVALI else 0.2)
    pose = {"hand_target": {"L": (-66, -280), "R": r}, "curl": {"L": .45, "R": .7 if t > grab else .45},
            "look": (0.15 * math.sin(t * 1.3 + i), look_y), "brow": 0.6 if t > DAVALI else 0.2,
            "mouth": "o" if (grab < t < PONCHIK) else ("wavy" if bitten and abs(chew) > .3 else "smile"),
            "head_tilt": 3 * math.sin(t * 1.7 + i * 2) + (4 if bitten else 0) * (1 if i else -1),
            "blink": 1.0 if bitten and t < PONCHIK + 0.35 else P.bump(t, 18.15 + i * .2, 0.14), "dy": 2 * math.sin(t * 2.2 + i)}
    if t >= grab:
        pose["donut_in_hand"] = [(0, -46, 24)] if bitten else []
    return pose


def s10(t):
    art = [_ST["room"], table(XA, 3100), table(XB, 3150)]
    plates = []
    for k, (gx, side, spec, act, sd) in enumerate(((XA, -1, GA, act_a10, 3200), (XB, 1, GB, act_b10, 3300))):
        px, py = gx + 24 * GS, GY + PLATE_L * GS
        arm, ppos, hold = white_arm(px, py, 17.88 + k * 0.05, DAVALI, DAVALI + 0.12, t, side, 3400 + k * 50)
        grab = 18.82 + (-0.02 if k == 0 else 0.04)
        body, arms = girl(spec, gx, t, act, sd)
        art.append(body)
        if ppos is not None and hold:
            plates.append(arm + plate_with_donut(ppos[0], ppos[1], sd=3500 + k * 20))
            art.append(arms)
        else:
            if t >= DAVALI:
                sq = 1 + 0.05 * P.kick(t, DAVALI, 9, 20)
                art.append(plate_with_donut(px, py, has_donut=t < grab, sd=3500 + k * 20, sc=sq))
            art.append(arms)
            if arm:
                plates.append(arm)
        if PONCHIK - 0.02 < t < PONCHIK + 0.6:      # крошки и посыпка от укуса
            e = t - PONCHIK
            hp = wpt(gx, (6, -600))
            for c in range(7):
                a = -2.6 + c * 0.55
                x = hp[0] + 100 * e * math.cos(a)
                y = hp[1] + 100 * e * math.sin(a) + 420 * e * e
                col = P.CRUMB if c % 3 else P.SPRINKLE[c % 6]
                art.append(blob(ellipse_pts(x, y, 6, 5, 6), col) if c % 3 else f'<rect x="{f(x - 5)}" y="{f(y - 2)}" width="10" height="4" rx="2" fill="{col}"/>')
    art += plates
    u = clamp((t - 17.8) / 2.25)
    sc = 1.22 + 0.07 * ease_io(u) + 0.035 * P.kick(t, PONCHIK, 6, 14) + 0.02 * P.kick(t, DAVALI, 7, 14)
    return "".join(art), cam(540, 850 - 10 * u, sc, 0.5 - 0.8 * u)


# ═══════════════════════════════ s11, s12: экспериментатор и девушка справа
def clipboard(h, a):
    s = shape(rect_pts(-46, -64, 46, 64, 6), "#b98a5a", blob(rect_pts(14, -64, 46, 64), "#9a6e44", .8), w=3.6, seed=3700)
    s += shape(rect_pts(-36, -50, 36, 56, 2), "#ffffff", "".join(line([(-26, -24 + k * 18), (26 - (k % 2) * 14, -24 + k * 18)], 3, "#9aa3b2", seed=3702 + k)
                                                                 for k in range(5)), w=2.6, seed=3701)
    s += shape(rect_pts(-20, -72, 20, -50, 4), "#9aa3b2", "", w=3, seed=3708)
    return f'<g transform="translate({f(h[0] - 30)} {f(h[1] - 50)}) rotate(-8)">{s}</g>'


def exp_pose(t, shot):
    """Экспериментатор: s11 — входит справа шагом и на «сказали» наклоняется к девушке; s12 — стоит наклонившись,
    говорит, кладёт руку ей на плечо."""
    if shot == "s11":
        stop = SKAZALI - 0.25
        e = clamp((t - 19.65) / (stop - 19.65))
        x = 1280 + (990 - 1280) * ease_out(e, 2)
        walking = t < stop
        lean = smooth(SKAZALI - 0.15, SKAZALI + 0.2, t)
    else:
        x, walking, lean = 990, False, 1.0
    pose = {"look": (-0.7, 0.5 * lean), "mouth": "smile", "brow": 0.5, "head_tilt": -10 * lean + 2 * math.sin(t * 2),
            "blink": P.bump(t, 21.0, 0.14) + P.bump(t, 22.3, 0.14), "in_hand": {"R": clipboard}, "curl": {"R": .8, "L": .5}}
    if walking:
        pose["walk"] = (t - 19.65) * 10.5
    else:
        pose["legs"] = {"L": (4, 0), "R": (-4, 0)}
        pose["hand_target"] = {"R": (40, -400)}
    talking = 0.0
    if shot == "s12":
        talking = P.osc(t, 4.0) * smooth(BYVAET - 0.05, BYVAET + 0.05, t) * (1 - smooth(23.0, 23.1, t))
        pose["mouth"] = "o" if talking > 0.3 else "smile"
        touch = ease_io(clamp((t - (BYVAET + 0.1)) / 0.4))
        pose["hand_target"]["L"] = (-200 * touch - 60 * (1 - touch), -470 * touch - 330 * (1 - touch))
        pose["curl"]["L"] = 0.4
    return x, pose, lean


def act_a11(t):
    """Девушка слева одна: держит надкушенный пончик над тарелкой и виновато смотрит на него."""
    return {"hand_target": {"L": (-66, -280), "R": (30, -400 + 4 * math.sin(t * 2))}, "curl": {"L": .45, "R": .7},
            "look": (0.25, 0.9), "brow": -0.6, "mouth": "frown", "head_tilt": -7 + 2 * math.sin(t * 1.5),
            "blink": P.bump(t, 20.3, 0.16), "dy": 2 * math.sin(t * 2.2), "donut_in_hand": [(0, -46, 24)]}


def act_b11(t, shot):
    """Девушка справа: сначала тоже виновата (надкушенный пончик на тарелке), поворачивается к экспериментатору;
    в s12 на «себя» выдыхает, улыбается, плечи опускаются."""
    turn = smooth(SKAZALI - 0.1, SKAZALI + 0.25, t) if shot == "s11" else 1.0
    relief = smooth(SEBYA - 0.05, SEBYA + 0.3, t)
    sigh = P.bump(t, SEBYA, 0.6)
    pose = {"hand_target": {"L": (-104, -300), "R": (104, -300)}, "curl": {"L": .75, "R": .75},
            "look": (0.9 * turn, 0.7 * (1 - turn) - 0.5 * turn), "brow": -0.6 * (1 - relief) + 0.5 * relief,
            "mouth": "smile" if relief > 0.5 else ("frown" if turn < 0.5 else "flat"),
            "head_tilt": 8 * turn - 5 * (1 - turn) + 2 * math.sin(t * 1.6) - 4 * relief,
            "blink": 1.0 if SEBYA < t < SEBYA + 0.32 else P.bump(t, 20.0, 0.15) + P.bump(t, 21.8, 0.15),
            "dy": 2 * math.sin(t * 2.2 + 1) + 10 * sigh + 4 * relief}
    return pose


def exp_layer(t, shot):
    x, pose, lean = exp_pose(t, shot)
    y = 1235
    sc = 1.0
    shadow = blob(ellipse_pts(x, y + 6, 120, 16, 12), "#8f99aa", .45, blur(4))
    body = person.draw(EXP, dict(pose, no_arms=True), 0, 0, 1.0, sd=3800)
    arms = person.draw(EXP, dict(pose, only_arms=True), 0, 0, 1.0, sd=3800)
    rot = -5 * lean
    return shadow + f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sc})">{body}{arms}</g>', (x, y, rot)


def s11_12(t, shot):
    art = [_ST["room"]]
    ex, (ex_x, ex_y, ex_r) = exp_layer(t, shot)
    art.append(ex)            # стоит за столиком справа (дальше от нас)
    art.append(table(XA, 3100))
    art.append(table(XB, 3150))
    ba, aa = girl(GA, XA, t, act_a11, 3200)
    art += [ba, plate_with_donut(XA + 24 * GS, GY + PLATE_L * GS, has_donut=False, sd=3500), aa]
    bb, ab = girl(GB, XB, t, lambda tt: act_b11(tt, shot), 3300)
    art += [bb, plate_with_donut(XB + 24 * GS, GY + PLATE_L * GS, bites=[(0, -46, 24)], sd=3520), ab]
    if shot == "s12":
        # облачко речи от экспериментатора
        e = t - BYVAET
        if e > -0.02:
            k = back_out(clamp((e + 0.02) / 0.26), 2.4) * (1 + 0.02 * math.sin(e * 5))
            art.append(P.speech(860, 380, 450, 116, "Бывает со всеми!", 50, k, tail=(110, 64), sd=3900))
        # сердечко у девушки на «себя»
        e = t - SEBYA
        if e > 0:
            k = back_out(clamp(e / 0.3), 2.6)
            hx, hy = XB - 150 + 10 * math.sin(e * 4), 560 - 40 * e
            art.append(P.heart(hx, hy, 2.6 * k, -12 + 6 * math.sin(e * 5), sd=3950))
            art.append(P.pop_lines(hx, hy, e, 60, 110, 6, col="#e8413a", w=6, sd=3960))
        u = clamp((t - 21.1) / 2.3)
        sc = 1.62 + 0.08 * ease_io(u) + 0.04 * P.kick(t, BYVAET, 6, 14) + 0.02 * P.kick(t, SEBYA, 6, 14)
        return "".join(art), cam(860 - 20 * u, 700 + 10 * u, sc, -0.4 + 0.6 * u)
    u = clamp((t - 19.65) / 1.85)
    sc = 1.14 + 0.04 * ease_io(u) + 0.02 * P.kick(t, SKAZALI, 6, 14)
    return "".join(art), cam(570 + 80 * ease_io(u), 860, sc, 0.4 - 0.6 * u)


def build_static():
    if _ST:
        return
    _ST["room"] = room()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    if sid == "s10":
        art, cm = s10(t)
    else:
        lib.INK_K[0] = 0.78 if sid == "s12" else 1.0
        art, cm = s11_12(t, sid)
        lib.INK_K[0] = 1.0
    return svg(f'<rect width="{W}" height="{H}" fill="#e3eee8"/><g transform="{cm}">{art}</g>')
