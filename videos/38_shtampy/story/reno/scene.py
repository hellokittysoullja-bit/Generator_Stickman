"""Сцена reno рилса 38 «дело кажется бесконечным»: планы s01 s02 s03 s13 s14 s15. frame(sid, t) -> SVG 1080×1920
(t — общее время ролика). Мир — room.py (комната в ремонте), Дима в полный рост — people.py (как в рилсах 29/33,
кисти с пальцами — hand.py), лист на стене и свиток — sheet.py. Удары — на словах по voice/words.json.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import people  # noqa: E402
import room as R  # noqa: E402
import wsheet as WS  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rect_pts, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


T_NED = wi(1)             # 0.56 «неделю»
T_KONCA = wi(5)           # 2.32
T_VIDNO = wi(7)           # 2.92
T_VECHER = wi(9)          # 4.12
T_STOIT = wi(14)          # 5.36
T_MESTE = wi(16)          # 5.92
T_ZAPIS = wi(65)          # 25.20
T_KAZHD = wi(66)          # 25.88
T_KUSOK = wi(68)          # 26.84
T_ZACH = wi(71)           # 27.80
T_RASTET = wi(74)         # 29.84

BS = 0.62
LEGL = 376.0              # таз → лодыжка (ноги почти прямые)


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def hook_zoom(t, t0=0.0, mx=0.4, dur=0.22, rot=-3.0):
    """Влёт (правила 28/29): масштаб 1/(1+mx) → 1.05 за dur, отскок к 1 за 0.3 с; поворот rot → +0.8 → 0."""
    u = (t - t0) / dur
    if u <= 0:
        return 1 / (1 + mx), rot
    if u < 1:
        e = ease_out(u, 3)
        return 1 / (1 + mx) + (1.05 - 1 / (1 + mx)) * e, rot * (1 - e) + .8 * e
    v = (t - t0 - dur) / 0.3
    if v < 1:
        e = ease_io(v)
        return 1.05 - .05 * e, .8 * (1 - e)
    return 1.0, 0.0


def punch(t, t0, amp=.08, up=.06, down=.35):
    if t < t0:
        return 0.0
    if t < t0 + up:
        return amp * ease_out((t - t0) / up, 2)
    return amp * (1 - ease_io(clamp((t - t0 - up) / down)))


def step12(t):
    return math.floor(t * 12) / 12


# ═════════════════════════ Дима ═════════════════════════
def dima(t, hip, feet, arms, hands, expr, lean=0.06, head_ang=0.0, spots=False, hood=0.0):
    people.SPOTS[0] = spots
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=hood, strings=(3 * osc(t, 1.3), 2 * osc(t, 1.1, 1)))
    return people.draw(p, "dima")


def stand_feet(hip, dx_n=16, dx_f=-4, y=None):
    y = hip[1] + LEGL if y is None else y
    return {"n": ((hip[0] + dx_n, y), 0.0), "f": ((hip[0] + dx_f, y - 4), 0.0)}


def layers(d, mid="", front=""):
    return d.get("legs", "") + d["arm_f"] + d["body"] + mid + d["arm_n"] + front


def sweat(x, y, k, u):
    if u <= 0 or u >= 1:
        return ""
    yy = y + 46 * k * ease_in(u)
    r = 15 * k * min(1, u * 3)
    drop = [(x, yy - r * 2.2), (x + r, yy - r * .1), (x + r * .8, yy + r * .7), (x, yy + r), (x - r * .8, yy + r * .7), (x - r, yy - r * .1)]
    return shape(drop, "#bfe6fa", blob([(x - r * .4, yy - r * .6), (x - r * .1, yy - r * .9), (x - r * .1, yy - r * .2)], "#ffffff"), w=3, seed=3001)


def grip_hand(d_rod):
    """Кулак вокруг палки (валик, маркер): ось кисти вдоль палки."""
    return dict(kind="open", dir=tuple(d_rod), curl=(.84, .88, .92, .95), spread=.02, thumb=.85, bend=.05)


# ═════════════════════════ валик ═════════════════════════
ROLL_HL = 52.0           # полудлина валика
ROLL_R = 22.0


def roller(W, Cc, t, wet=1.0, spin=0.0):
    """Валик: ручка из кулака (запястье W) к шубке с центром Cc (ось шубки горизонтальна). Возвращает (сзади руки, спереди)."""
    W, Cc = np.array(W, float), np.array(Cc, float)
    hd = Cc - W
    L = np.linalg.norm(hd)
    hd = hd / (L + 1e-9)
    n = np.array([-hd[1], hd[0]])
    a = W - hd * 34
    b = W + hd * 70
    back = []
    # проволока рамы: от ручки к левому концу оси шубки
    e = Cc + np.array([-ROLL_HL - 16, 0])
    k = Cc + np.array([-ROLL_HL - 16, ROLL_R + 30])
    back.append(line([tuple(b), tuple(b + hd * 30), tuple(k), tuple(e)], 9, INK, seed=6000, taper=.02, wmin=.95))
    back.append(line([tuple(b), tuple(b + hd * 30), tuple(k), tuple(e)], 5, "#b9c2ca", seed=6001, taper=.02, wmin=.95))
    back.append(line([tuple(e), tuple(Cc + np.array([-ROLL_HL + 4, 0]))], 8, "#7d858e", seed=6002, taper=.02, wmin=.95))
    # шубка
    x0, x1 = Cc[0] - ROLL_HL, Cc[0] + ROLL_HL
    y0, y1 = Cc[1] - ROLL_R, Cc[1] + ROLL_R
    inner = blob(rect_pts(x0, Cc[1] + 6, x1, y1), "#7fc4ad", .9)
    inner += blob(rect_pts(x0, y0, x1, Cc[1] - 12), "#c9f2e2", .8)
    for j in range(9):
        ph = (spin * 1.0 + j / 9) % 1
        yy = y0 + 4 + (y1 - y0 - 8) * ph
        xx = x0 + 6 + (j * 37) % int(2 * ROLL_HL - 12)
        back.append("")
        inner += line([(xx, yy), (xx + 7, yy + 3)], 2.2, "#6fb59e", seed=6010 + j, op=.8)
    back.append(shape(rect_pts(x0, y0, x1, y1, 16), "#9fdcc6" if wet else "#e9e4d8", inner, w=3.8, seed=6003))
    # ручка (оранжевый пластик) — под пальцами
    h = lib.band([tuple(a), tuple(b)], 26, 24, step=6, cap=True)
    hi = blob(lib.band([tuple(a + n * 5), tuple(b + n * 5)], 7, 6, step=6, cap=False), "#f6a660", .9)
    back.append(shape(h, "#e2722e", hi, w=3.6, seed=6004))
    return "".join(back), ""


# ═════════════════════════ кадр ═════════════════════════
def vignette(mode):
    a = .32 if mode == "day" else .5
    g = lib.rad_grad([(0, "#0a0c1e", 0), (.62, "#0a0c1e", 0), (1, "#0a0c1e", a)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def compose(world, cam, mode, lamp_pos=(0, 0), on=0.0, t=0.0, screen=""):
    cx, cy, s, r = cam
    set_ink(s)
    o = [f'<rect width="1080" height="1920" fill="#2a2a3a"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{R.light(t, lamp_pos, on, mode)}</g>', screen, vignette(mode)]
    return lib.svg("".join(o))


def room_back(t, mode="evening", lamp_on=1.0, film_off=0.0, extra_wall="", floor_items="", newspapers=True):
    """Стены, окно, лампа, пол с газетами и плёнкой. Возвращает (svg, позиция лампочки)."""
    o = [R.ceiling(), R.left_wall(), R.right_wall(), R.back_wall(), R.window(t), R.outlet(), extra_wall]
    if R.ST["pendant"]:
        o.append(R.pendant(t))
        lp = (360.0, 300.0)
    else:
        lsvg, lp = R.hook_lamp(t, lamp_on)
        o.append(lsvg)
    o.append(R.floor())
    if newspapers:
        o.append(R.newspapers(film_off))
        o.append(R.film(film_off))
    o.append(floor_items)
    return "".join(o), lp


# ═════════════════════════ s01: на стремянке катит валик; на «неделю» слетают 7 листков календаря ═════════════════════════
LAD = (470.0, 1520.0, 1.0)
CAL = (735.0, 470.0)
STRIPE_MID = 470.0


def roll_y(t):
    """Центр шубки по y: проходы вверх-вниз, размах растёт."""
    amp = 110 + 110 * clamp(t / 1.4)
    return STRIPE_MID + amp * math.sin(2 * math.pi * 1.55 * t - .6)


def stripe_ext(t):
    ts = np.linspace(-.2, t, max(4, int((t + .2) * 60)))
    ys = [roll_y(x) for x in ts]
    y0, y1 = min(ys) - ROLL_HL * 0 - ROLL_R, max(ys) + ROLL_R
    H0, H1 = R.CY + 22, R.FY - 52
    return (y0 - H0) / (H1 - H0), (y1 - H0) / (H1 - H0)


def on_ladder(t, look_up=1.0, cyl=None, expr=None, far_target=None):
    lx, ly, lk = LAD
    sy = R.ladder_step_y(lx, ly, lk, 2)
    hip = np.array([360.0, sy - 38 - LEGL])
    hip[1] += 4 * abs(osc(t, 1.55))
    feet = {"n": ((hip[0] + 20, sy - 38), 0.0), "f": ((hip[0] - 6, sy - 40), 0.0)}
    Cc = np.array(cyl if cyl is not None else (610.0, roll_y(t)))
    W = Cc + np.array([-112.0, 236.0])
    hd = (Cc - W) / np.linalg.norm(Cc - W)
    arms = {"n": ("ik", tuple(W), -1), "f": far_target or ("ang", -.12 + .03 * osc(t, 1.55), .25)}
    hands = {"n": grip_hand(hd), "f": dict(kind="open", dir=(-.15, 1), curl=(.3, .35, .4, .45), spread=.06, thumb=.4)}
    d = dima(t, hip, feet, arms, hands, expr, lean=.04 - .02 * look_up, head_ang=-.16 * look_up + .02 * osc(t, 1.55), spots=True)
    rb, rf = roller(W, Cc, t, spin=t * 1.6)
    return d, rb, rf, hip


def s01(t):
    R.set_state(tod="evening", lamp=1.0, stripe=stripe_ext(t))
    z, rot = hook_zoom(t, 0.0, .4, .22, -3.2)
    hit = punch(t, T_NED, .08, .06, .38)
    k = ease_io(clamp(t / 1.65))
    sh = bump(t, T_NED, .3)
    s = 1.42 * z * (1 + .05 * k) * (1 + hit)
    cam = (565 + 40 * (1 - z) + 10 * k + 5 * sh * osc(t, 13), 640 + 30 * (1 - z) - 8 * k + 4 * sh * osc(t, 17, 1), s,
           rot + .4 * osc(t, .5) + 1.2 * sh * osc(t, 9))
    yv = roll_y(t)
    dy = (roll_y(t + .02) - yv) / .02
    ex = dict(lid=.55, look=(.75, -.55 + .4 * clamp((yv - 300) / 450)), brows="det", mouth="flat", closed=blink_at(t, 1.25, .14),
              hair=clamp(-dy * .012, -6, 6))
    d, rb, rf, hip = on_ladder(t, expr=ex)
    lx, ly, lk = LAD
    # календарь: листки 3..9 слетают по одному с «неделю», остаётся 10
    gaps = [T_NED + .065 * j for j in range(7)]
    n_off = sum(1 for g in gaps if t >= g)
    cal = R.calendar(*CAL, n_off, t)
    leaves = "".join(R.flying_leaf(CAL[0], CAL[1] + 22, (t - g) / .6, 3 + j, 31 + j) for j, g in enumerate(gaps))
    w, lp = room_back(t, "evening", 1.0, extra_wall=cal)
    w += R.ladder(lx, ly, lk, front=False)
    w += R.paint_can(760, 1560, 1.0)
    w += R.ladder(lx, ly, lk, front=True)
    front = rf + leaves
    if dy < 0:          # штрихи скорости у шубки
        pass
    w += layers(d, rb, front)
    return compose(w, cam, "evening", lp, 1.0, t)




# ═════════════════════════ шаги ═════════════════════════
FEET_Y = 1560.0          # лодыжки стоящего Димы (подошвы на плёнке)


def steps(t, x0n, x0f, plan, y=FEET_Y, lift=60.0):
    """Ступни по плану шагов [(t0, t1, side, dx)]: стоящая ступня не скользит; в шаге — дуга. Возвращает feet, ср. x."""
    xs = {"n": x0n, "f": x0f}
    ang = {"n": 0.0, "f": 0.0}
    dy = {"n": 0.0, "f": 0.0}
    for (a, b, sd, dx) in plan:
        if t >= b:
            xs[sd] += dx
        elif t > a:
            u = (t - a) / (b - a)
            xs[sd] += dx * ease_io(u)
            dy[sd] = -lift * math.sin(math.pi * u)
            ang[sd] = .35 * math.sin(math.pi * u) * (1 if dx > 0 else -.6)
    feet = {k: ((xs[k], y - 4 * (k == "f") + dy[k]), ang[k]) for k in ("n", "f")}
    return feet, (xs["n"] + xs["f"]) / 2


def gait(phi, S=150.0, lift=64.0):
    """Ходьба на месте (беговая дорожка): смещения ступней от таза по фазе phi (циклы)."""
    out = {}
    for k, off in (("n", 0.0), ("f", .5)):
        p = (phi + off) % 1.0
        if p < .6:
            q = p / .6
            out[k] = (S * (.5 - q), 0.0, .45 * smooth(.72, 1, q))
        else:
            q = (p - .6) / .4
            out[k] = (S * (-.5 + ease_io(q)), -lift * math.sin(math.pi * q), .45 * (1 - smooth(0, .4, q)) - .2 * math.sin(math.pi * q) * smooth(.4, .8, q))
    return out


# ═════════════════════════ s02: слезает, отходит, видит всю комнату; на «видно» отвисает челюсть ═════════════════════════
HOP0, HOP1 = 1.5, 1.86
X_LAND = 236.0
STEPS02 = [(2.02, 2.24, "n", -96.0), (2.24, 2.46, "f", -110.0), (2.46, 2.66, "n", -60.0)]


def floor_props(can=True, ladder_x=470.0):
    o = R.tile_boxes(960, 1640, .95) + R.bags(-250, 1650, 1.0)
    return o


def s02(t):
    R.set_state(tod="evening", lamp=1.0, stripe=stripe_ext(1.5))
    lx, ly, lk = LAD
    u1 = clamp((t - 1.25) / (T_KONCA - 1.25))
    e = .28 * ease_in(u1, 1.6) if t < T_KONCA else .28 + .72 * ease_out(clamp((t - T_KONCA) / .95), 2.2)
    pv = punch(t, T_VIDNO, .14, .06, .5)
    s = 1.3 * (.72 / 1.3) ** e * (1 + pv)
    sh = bump(t, T_VIDNO, .3)
    cam = (560 - 40 * e - 900 * pv + 4 * sh * osc(t, 13), 700 + 230 * e - 400 * pv + 3 * sh * osc(t, 17), s, .6 - .6 * e + 1.0 * sh * osc(t, 9))
    gape = smooth(T_VIDNO - .04, T_VIDNO + .1, t)
    if t < HOP0:
        ex = dict(lid=.5, look=(.75, -.3), brows="det", mouth="flat", hair=0)
        d, rb, rf, hip = on_ladder(t, expr=ex, cyl=(610.0, roll_y(min(t, 1.45)) * (1 - smooth(1.3, 1.5, t)) + 560 * smooth(1.3, 1.5, t)))
        body = rb
    else:
        sy = R.ladder_step_y(lx, ly, lk, 2)
        hip_l = np.array([360.0, sy - 38 - LEGL])
        hip_f = np.array([X_LAND - 6, FEET_Y - 364])
        if t < HOP1:
            u = (t - HOP0) / (HOP1 - HOP0)
            hip = hip_l + (hip_f - hip_l) * u + np.array([0, -70 * math.sin(math.pi * u)])
            tuck = math.sin(math.pi * u)
            feet = {"n": ((hip[0] + 30 - 30 * tuck, hip[1] + LEGL - 90 * tuck), .3 * tuck), "f": ((hip[0] - 10 - 40 * tuck, hip[1] + LEGL - 70 * tuck), .4 * tuck)}
            lean = .04 + .1 * tuck
        else:
            feet, mx = steps(t, X_LAND + 16, X_LAND - 4, STEPS02)
            land = math.exp(-9 * (t - HOP1)) * math.sin(min(math.pi, (t - HOP1) * 14)) if t < HOP1 + .3 else 0.0
            walk = sum(bump(t, a, b - a) for (a, b, _, _) in STEPS02)
            hip = np.array([mx - 6, FEET_Y - 364 + 36 * land - 8 * walk])
            lean = .02 + .05 * land - .1 * gape
        # валик: сначала вверх-вперёд, на «видно» опускается
        W = hip + np.array([96.0, -80.0 + 140 * gape])
        ang = math.radians(-38 + 105 * ease_out(gape, 2))
        Cc = W + 255 * np.array([math.cos(ang), math.sin(ang)])
        hd = (Cc - W) / np.linalg.norm(Cc - W)
        ex = dict(lid=.55 + .45 * gape, look=(.7 - .1 * gape, -.45 - .3 * gape), brows="up" if gape > .3 else "det",
                  mouth="talk" if gape > .05 else "flat", open=1.0 * gape, smile=-.3, closed=blink_at(t, 2.5, .14),
                  hair=6 * bump(t, HOP1, .25) + 8 * bump(t, T_VIDNO, .35))
        arms = {"n": ("ik", tuple(W), -1), "f": ("ang", -.15 - .2 * math.sin(math.pi * clamp((t - HOP0) / (HOP1 - HOP0))), .3)}
        hands = {"n": grip_hand(hd), "f": dict(kind="open", dir=(-.15, 1), curl=(.3, .35, .4, .45), spread=.06, thumb=.4)}
        d = dima(t, hip, feet, arms, hands, ex, lean=lean, head_ang=-.1 - .08 * gape, spots=True)
        rb, rf = roller(W, Cc, t, spin=0)
        body = rb
    w, lp = room_back(t, "evening", 1.0, floor_items=floor_props())
    w += R.paint_can(760, 1580, 1.0)
    w += R.calendar(*CAL, 7, t)
    w += R.ladder(lx, ly, lk, front=False) + R.ladder(lx, ly, lk, front=True)
    front = rf
    if t >= T_VIDNO:
        hx, hy = d["head"]
        front += sweat(hx + 70, hy - 70, 1.0, clamp((t - T_VIDNO - .05) / .7))
    w += layers(d, body, front)
    return compose(w, cam, "evening", lp, 1.0, t)


# ═════════════════════════ s03: вечер, лампа щёлкает; идёт, а плёнка едет назад — стоит на месте ═════════════════════════
S03_S = 120.0
HIP03 = 500.0


def cadence(t):
    return 1.45 + 1.15 * smooth(T_STOIT - .05, T_STOIT + .3, t)


def phase03(t):
    ts = np.linspace(3.2, min(t, T_MESTE), 240)
    if t <= 3.2:
        return 1.45 * (t - 3.2)
    f = np.array([cadence(x) for x in ts])
    return float(np.trapezoid(f, ts))


def lamp03(t):
    if t < T_VECHER:
        return 0.0
    u = t - T_VECHER
    if u < .14:
        return .25 + .5 * (1 if int(u * 50) % 2 else 0)
    return 1.0


def s03(t):
    on = lamp03(t)
    R.set_state(tod="evening", lamp=on, stripe=stripe_ext(1.5))
    phi = phase03(t)
    stop = clamp((t - T_MESTE) / .16)
    tv = max(0.0, t - T_MESTE)
    v_end = S03_S / .6 * cadence(T_MESTE)
    slide = v_end * (1 - math.exp(-6 * tv)) / 6          # плёнка ещё едет и уносит его назад
    off = -S03_S / .6 * phi - slide
    g = gait(phi, S03_S)
    g_end = gait(phase03(T_MESTE), S03_S)
    feet = {}
    for k, dxs in (("n", 16), ("f", -4)):
        gx, gy, ga = g_end[k] if stop > 0 else g[k]
        if stop > 0:
            gx, gy, ga = gx * (1 - ease_io(stop)) + dxs * ease_io(stop) - dxs, gy * (1 - ease_io(stop)), ga * (1 - ease_io(stop))
        feet[k] = ((HIP03 + dxs + gx - slide, FEET_Y - 4 * (k == "f") + gy), ga)
    slump = smooth(T_MESTE, T_MESTE + .35, t)
    reach = min(math.sqrt(max(0.0, 377.0 ** 2 - (feet[k][0][0] - (HIP03 - slide) + (6 if k == "f" else -14)) ** 2)) for k in feet if feet[k][0][1] >= FEET_Y - 5)
    hip = np.array([HIP03 - slide - 6, FEET_Y - reach + 8 * slump])
    sw = math.sin(2 * math.pi * phi) * (1 - stop)
    # валик на плече: ручка из кулака у груди назад-вверх через плечо
    W = hip + np.array([70.0, -205.0 + 40 * slump]) + np.array([4 * sw, 0])
    Cc = hip + np.array([-130.0, -440.0 + 60 * slump])
    hd = (Cc - W) / np.linalg.norm(Cc - W)
    arms = {"n": ("ik", tuple(W), -1), "f": ("ang", .32 * sw * (1 - slump) + .05 * slump, .3 + .2 * slump)}
    hands = {"n": grip_hand(hd), "f": dict(kind="open", dir=(-.1, 1), curl=(.3, .35, .4, .45), spread=.06, thumb=.4)}
    fast = smooth(T_STOIT, T_STOIT + .25, t) * (1 - slump)
    ex = dict(lid=.45 + .35 * fast - .15 * slump, look=(.8 - .5 * slump, .1 + .7 * slump), brows="worry" if fast > .3 else "tired",
              mouth="flat", closed=max(blink_at(t, 3.9, .14), blink_at(t, 4.9, .14)), hair=-6 * math.cos(4 * math.pi * phi) * (1 - stop))
    d = dima(t, hip, feet, arms, hands, ex, lean=.1 + .06 * fast + .16 * slump, head_ang=.02 + .3 * slump, spots=True)
    rb, rf = roller(W, Cc, t, spin=0, wet=1.0)
    props = R.tile_boxes(1010, 1460, .8) + R.bags(-40, 1462, .9)
    w, lp = room_back(t, "evening", on, film_off=off, floor_items=props)
    front = ""
    if t > T_STOIT and stop < 1:      # штрихи скорости за пяткой
        for j in range(3):
            y = FEET_Y + 10 - j * 30
            x = HIP03 - 160 - 40 * j
            front += line([(x, y), (x - 90 - 30 * fast, y)], 4.5, "#5a4a3a", seed=6100 + j, op=fast, taper=.3, wmin=.4)
    if t >= T_MESTE:
        hx, hy = d["head"]
        front += sweat(hx + 70, hy - 76, 1.1, clamp((t - T_MESTE - .02) / .75))
    w += rb + layers(d, "", front)
    k = ease_io(clamp((t - 3.35) / 3.4))
    sh = bump(t, T_STOIT, .4)
    s = 1.15 * (1 + .03 * k) * (1 + punch(t, T_MESTE, .07, .05, .35))
    cam = (490 + 50 * k + 6 * sh * osc(t, 14), 1115 + 5 * sh * osc(t, 19, 1), s, -.6 + .9 * k + 1.3 * sh * osc(t, 11))
    return compose(w, cam, "evening", lp, on, t)


# ═════════════════════════ лист и маркер ═════════════════════════
SH_X0, SH_X1, SH_Y0 = 566.0, 872.0, 935.0
MDIR = np.array([.8, .6]) / 1.0
HIP_W = 448.0           # таз Димы у листа


def line_y(i):
    return SH_Y0 + 70 + i * WS.GAP


def marker_at(tip, ink, spin=0.0):
    """Маркер кончиком в tip; spin 0..1 — переворот в пальцах (на середине маркер поперёк). Возвращает (запястье, svg, кисть)."""
    tip = np.array(tip, float)
    a = math.atan2(MDIR[1], MDIR[0]) + math.pi * spin
    d = np.array([math.cos(a), math.sin(a)])
    c = tip - MDIR * 60          # середина маркера (в кулаке)
    top, tp = c - d * 60, c + d * 60
    wr = c - MDIR * 14 + np.array([-8.0, 14.0])
    svg = WS.marker(tuple(top), tuple(tp), 18, ink)
    return wr, svg, grip_hand(MDIR)


def at_sheet(t, tip, ink, expr, head_ang=0.0, lean=.08, spin=0.0, far=None, spots=False):
    hip = np.array([HIP_W, FEET_Y - 376 + 2 * osc(t, .8)])
    wr, msvg, hn = marker_at(tip, ink, spin)
    arms = {"n": ("ik", tuple(wr), -1), "f": far or ("ang", -.08 + .02 * osc(t, .7), .35)}
    hands = {"n": hn, "f": dict(kind="open", dir=(-.1, 1), curl=(.3, .35, .4, .45), spread=.06, thumb=.4)}
    d = dima(t, hip, stand_feet(hip), arms, hands, expr, lean=lean, head_ang=head_ang, spots=spots)
    return d, msvg


def day_room(t, extra_wall="", props=True, sheet_svg=""):
    w, lp = room_back(t, "day", 0.0, extra_wall=extra_wall + sheet_svg,
                      floor_items=(R.tile_boxes(960, 1640, .95) + R.bags(-250, 1650, 1.0)) if props else "")
    return w, lp


def glide(t, pts):
    """Точка по ключам [(t, (x, y))] с плавными переходами."""
    if t <= pts[0][0]:
        return np.array(pts[0][1], float)
    for (ta, pa), (tb, pb) in zip(pts, pts[1:]):
        if t <= tb:
            u = ease_io((t - ta) / (tb - ta))
            return np.array(pa, float) + (np.array(pb, float) - np.array(pa, float)) * u
    return np.array(pts[-1][1], float)


# ═════════════════════════ s13: день; лист на скотче, Дима пишет «покрасил стену»; кивает на «каждый» ═════════════════════════
W13 = (T_ZAPIS, T_ZAPIS + .66)


def s13(t):
    R.set_state(tod="day", lamp=0.0, stripe=stripe_ext(1.5), outlet_new=True)
    uw = clamp((t - W13[0]) / (W13[1] - W13[0]))
    items = [(WS.LINES[0], uw, 0.0)]
    sh, tips = WS.sheet(SH_X0, line_y(0) - 70, SH_X1, SH_Y0 + 360, items, t)
    if t < W13[0]:
        tip = glide(t, [(23.9, (580.0, 1220.0)), (24.6, (586.0, 1210.0)), (W13[0] - .05, (SH_X0 + 44, line_y(0) - 10))])
    elif t < W13[1]:
        tip = np.array(tips[("w", 0)])
    else:
        end = (SH_X0 + 42 + WS.text_w(WS.LINES[0]), line_y(0) - 8)
        tip = glide(t, [(W13[1], end), (W13[1] + .3, (end[0] + 6, end[1] - 30)), (26.8, (end[0] - 30, end[1] - 50))])
    nod = bump(t, T_KAZHD, .4)
    wr = clamp((t - W13[0] + .1) / .2) * (1 - smooth(W13[1], W13[1] + .3, t))
    ex = dict(lid=.6 + .15 * wr, look=(.85, .55 - .2 * nod), brows="det" if wr > .5 else "calm", mouth="smile", smile=.4 + .6 * smooth(W13[1], W13[1] + .3, t),
              closed=max(blink_at(t, 24.4, .14), blink_at(t, 26.3, .14)), hair=5 * nod)
    d, msvg = at_sheet(t, tip, "#1d1a22", ex, head_ang=.06 + .2 * nod, lean=.08 + .03 * nod)
    w, lp = day_room(t, sheet_svg=sh)
    front = ""
    if 0 < uw < 1:
        front += squeak(tip, t)
    w += layers(d, msvg, front)
    k = ease_io(clamp((t - 23.9) / 2.9))
    s = 1.32 * (1 + .07 * k) * (1 + punch(t, T_ZAPIS, .03, .05, .3))
    cam = (610 + 50 * k, 1030 - 20 * k + 6 * nod, s, .8 - 1.2 * k)
    return compose(w, cam, "day", lp, 0.0, t)


def squeak(tip, t, col="#5a4a3a"):
    """Короткие штрихи-«скрип» у кончика маркера (на двойках)."""
    o = ""
    tt = step12(t)
    r = np.random.RandomState(int(tt * 12) % 997 + 77)
    for j in range(2):
        a = r.uniform(-2.4, -.8)
        p0 = (tip[0] + 26 * math.cos(a), tip[1] + 26 * math.sin(a))
        p1 = (tip[0] + 46 * math.cos(a), tip[1] + 46 * math.sin(a))
        o += line([p0, p1], 3.6, col, seed=6200 + j, taper=.3, wmin=.4)
    return o


# ═════════════════════════ s14: вторая строка на «кусок», переворот маркера, красное зачёркивание на «зачёркивает» ═════════════════════════
W14 = (T_KUSOK, T_KUSOK + .62)
FLIP = (27.42, 27.6)
STK = (T_ZACH, T_ZACH + .2)


def s14(t):
    R.set_state(tod="day", lamp=0.0, stripe=stripe_ext(1.5), outlet_new=True)
    u2 = clamp((t - W14[0]) / (W14[1] - W14[0]))
    us = ease_in(clamp((t - STK[0]) / (STK[1] - STK[0])), 1.4)
    items = [(WS.LINES[0], 1.0, us), (WS.LINES[1], u2, 0.0)]
    sh, tips = WS.sheet(SH_X0, line_y(0) - 70, SH_X1, SH_Y0 + 360, items, t)
    e1 = (SH_X0 + 42 + WS.text_w(WS.LINES[0]) - 30, line_y(0) - 58)
    s1 = (SH_X0 + 38, line_y(0) - 10)
    e2 = (SH_X0 + 42 + WS.text_w(WS.LINES[1]), line_y(1) - 8)
    if t < W14[0]:
        tip = glide(t, [(26.4, e1), (W14[0] - .02, (SH_X0 + 44, line_y(1) - 10))])
    elif t < W14[1]:
        tip = np.array(tips[("w", 1)])
    elif t < STK[0]:
        tip = glide(t, [(W14[1], e2), (FLIP[0], (e2[0] - 30, e2[1] - 40)), (FLIP[1], (e2[0] - 60, e2[1] - 50)), (STK[0] - .02, s1)])
    elif t < STK[1]:
        tip = np.array(tips.get(("s", 0), s1))
    else:
        end = (SH_X0 + 42 + WS.text_w(WS.LINES[0]) + 8, line_y(0) - 14)
        tip = glide(t, [(STK[1], end), (STK[1] + .12, (end[0] + 30, end[1] - 26)), (28.8, (end[0] + 20, end[1] - 60))])
    spin = ease_io(clamp((t - FLIP[0]) / (FLIP[1] - FLIP[0])))
    ink = "#1d1a22" if spin < .5 else WS.RED
    happy = smooth(STK[1], STK[1] + .25, t)
    ex = dict(lid=.65, look=(.85, .5), brows="det" if happy < .5 else "up", mouth="grin" if happy > .4 else "smile", smile=.6,
              closed=blink_at(t, 27.2, .14), laugh=.0, hair=6 * bump(t, STK[0], .35))
    d, msvg = at_sheet(t, tip, ink, ex, head_ang=.08 - .1 * happy, lean=.08 + .04 * bump(t, STK[0], .3), spin=spin if spin < 1 else 0.0)
    w, lp = day_room(t, sheet_svg=sh)
    front = ""
    if 0 < u2 < 1:
        front += squeak(tip, t)
    mid = msvg
    if STK[0] + .08 < t < STK[1] + .25:       # штрихи скорости за красной линией (под рукой)
        a = clamp((t - STK[0]) / .45)
        for j in range(3):
            y = line_y(0) - 30 + j * 14
            x = tip[0] - 40 - 30 * j
            mid += line([(max(x - 110, SH_X0 + 20), y), (max(x, SH_X0 + 40), y)], 4.2, WS.RED, seed=6300 + j, op=1 - a, taper=.3, wmin=.4)
    if t > STK[1]:
        front += sparkle_pop(SH_X0 + 200, line_y(0) - 60, clamp((t - STK[1]) / .45))
    w += layers(d, mid, front)
    k = ease_io(clamp((t - 26.4) / 2.4))
    s = 1.95 * (1 + .06 * k) * (1 + punch(t, STK[0], .06, .05, .32))
    sh_ = bump(t, STK[0], .3)
    cam = (660 + 25 * k + 4 * sh_ * osc(t, 13), 1010 - 10 * k + 3 * sh_ * osc(t, 17), s, -.6 + .9 * k + .9 * sh_ * osc(t, 9))
    return compose(w, cam, "day", lp, 0.0, t)


def sparkle_pop(x, y, u):
    if u <= 0 or u >= 1:
        return ""
    o = ""
    for j in range(6):
        a = math.radians(-160 + j * 26)
        r0, r1 = 26 + 50 * u, 44 + 70 * u
        o += line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 5, "#f2b43a", seed=6400 + j,
                  taper=.3, wmin=.4, op=1 - u * .6)
    return o


# ═════════════════════════ s15: отъезд — лист длинный, всё зачёркнуто; на «растёт» свиток сползает до пола ═════════════════════════
def s15(t):
    R.set_state(tod="day", lamp=0.0, back_done=True, left_done=True, outlet_new=True, pendant=True)
    v = t - T_RASTET
    y_short = 1150.0
    y_floor = R.FY + 150
    if v <= 0:
        yb = y_short + 6 * osc(t, 1.2)
    else:
        yb = min(y_floor, y_short + 2400 * v * v + 300 * v)
    land = v - math.sqrt(max(0, (y_floor - y_short))) / 60 if v > 0 else -1
    n = len(WS.LINES)
    items = [(WS.LINES[i], 1.0, 1.0) for i in range(n)]
    rr = 26.0
    sh, _ = WS.sheet(SH_X0, SH_Y0, SH_X1, min(yb, R.FY - 10), items, t)
    o_wall = sh
    o = ""
    if yb > R.FY - 10:       # кусок, лёгший на пол к зрителю
        m = (yb - R.FY) / (R.FY - R.VP[1])
        a, b = R.proj(SH_X0, R.FY, 0), R.proj(SH_X1, R.FY, 0)
        c, d_ = R.proj(SH_X1, R.FY, m), R.proj(SH_X0, R.FY, m)
        o += shape([a + (1,), b + (1,), c + (1,), d_ + (1,)], WS.PAPER, blob([a, b, c, d_], WS.PAPER_SH, .5) +
                   line([(a[0] + 50, a[1] + 12), (b[0] - 60, b[1] + 14)], 2.4, WS.RED, seed=6500, op=.8), w=3.4, seed=6501)
        ry = (c[1] + d_[1]) / 2
        hw = (c[0] - d_[0]) / 2
    else:
        ry, hw = yb, (SH_X1 - SH_X0) / 2
    spin = yb / 60.0
    bounce = math.exp(-6 * max(0, land)) * abs(math.sin(max(0, land) * 16)) * 18 if land > 0 else 0
    o += WS.roll((SH_X0 + SH_X1) / 2, ry - bounce, hw + 4, rr, spin=spin)
    # Дима гордо: руки в боки, грудь вперёд
    hip = np.array([330.0, FEET_Y - 376 + 2 * osc(t, .9)])
    proud = smooth(28.4, 28.9, t)
    jump = bump(t, T_RASTET + .1, .4)
    up = 1.0
    arms = {"n": ("ik", tuple(hip + np.array([60 + 120 * up, -60 - 300 * up + 20 * jump])), -1),
            "f": ("ik", tuple(hip + np.array([-40.0, -30.0])), 1)}
    hands = {"n": dict(kind="open", dir=(.15 * up + .3 * (1 - up), -1 * up + .9 * (1 - up)), curl=(.9, .92, .94, .95), spread=.02, thumb=0.0, bend=.05),
             "f": dict(kind="open", dir=(.5, .9), curl=(.85, .88, .9, .92), spread=.02, thumb=.7)}
    ex = dict(lid=.7, look=(.9, -.2 + .3 * smooth(T_RASTET, T_RASTET + .4, t)), brows="up", mouth="grin", closed=blink_at(t, 29.2, .14),
              hair=6 * jump)
    hip = hip + np.array([0, -14 * jump])
    d = dima(t, hip, stand_feet(hip), arms, hands, ex, lean=-.06 * proud, head_ang=-.12 * proud + .05 * jump)
    w, lp = room_back(t, "day", 0.0, extra_wall=o_wall, floor_items=o + R.paint_can(1010, 1640, .9))
    front = ""
    if 0 < v < .5:
        a = clamp(v / .5)
        for j in range(3):
            x = SH_X1 + 40 + 24 * j
            front += line([(x, yb - 80 - 40 * j), (x, yb - 220 - 40 * j)], 4.5, "#5a4a3a", seed=6600 + j, op=1 - a, taper=.3, wmin=.4)
    w += layers(d, "", front)
    k = ease_io(clamp((t - 28.4) / 2.4))
    e = .35 * k + .65 * ease_out(clamp((t - T_RASTET + .05) / .7), 2) * (t > T_RASTET - .05)
    s = 1.35 * (.78 / 1.35) ** e * (1 + punch(t, T_RASTET, .06, .05, .35))
    cam = (620 - 60 * e, 900 + 220 * e, s, .6 - .9 * e)
    return compose(w, cam, "day", lp, 0.0, t)


SHOTS = {"s01": s01, "s02": s02, "s03": s03, "s13": s13, "s14": s14, "s15": s15}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
