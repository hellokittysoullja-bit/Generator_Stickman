"""Рилс 47, сцена party (s01–s04, s14, s15): праздник у сестры. Комната (env.py), торт на столе под скатертью, шары и гирлянда, племянник 5 лет
(person.py, большая голова), сестра (person.py), Дима (dima40.py, горчичное худи), кот под столом (cat.py, ЛЕВОЕ ухо загнуто).
Всё живёт в общем мире (x −600…1700, пол с y=1232) и снимается камерой cam(cx, cy, s, rot) — разной в каждом плане. Время — общее время ролика;
удары на словах по words.json (c47.wt)."""
import math

import numpy as np

import cat
import dima40 as dima
import env
import lib
import person
from c47 import hand_text, kick, pop, shake, wt  # noqa: F401
from env import FLOOR_Y
from hands5 import hand5
from lib import (INK, H, W, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mul, shape, smooth, svg)

_ST = {}

# ───────────────────────── время слов
T_SLADKOGO = wt("сладкого")
T_GIPER = wt("гиперактивными")      # 2.36
T_DIMA = wt("Дима")                 # 3.68
T_SKAZAL = wt("сказал")             # 4.32
T_NOSILSYA = wt("носился")          # 6.00
T_TORTA = wt("торта")               # 6.80
T_PRAZD = wt("празднику")           # 28.28
T_KOT = wt("кот", 28.5)             # 29.24
T_KROSHKAM = wt("крошкам")          # 30.28

KID = dict(skin="#f2c6a6", hair="short", hair_c="#d98a2b", top="#3d9be0", low="#f0c04a", shoes="#e0473a", face=.5, h=1.0, head_k=1.38, brow_c="#8a4a1a")
SIS = dict(skin="#e9b896", hair="ponytail", hair_c="#7a3b24", top="#e2778e", low="#3f5b8f", shoes="#3a2a22", face=-.5, h=1.0, brow_c="#4a2a1e")
KID_SC, SIS_SC = .6, .85
DIMA_X, SIS_X, FEET = 790, 1035, 1290
CAT_X, CAT_Y, CAT_S = 245, 1306, .55
HOODIE_SKIN = dima.SKIN


# ───────────────────────── предметы в руках
def plate_hold(hx, hy):
    return (blob(ellipse_pts(hx, hy + 2, 50, 9, 12), "#3a2410", .2, blur(3)) +
            shape(ellipse_pts(hx, hy - 4, 48, 9, 14), "#ffffff", w=3, seed=801) + env.cake_slice(hx, hy - 6).replace("<g", "<g", 1))


def glass_hold(hx, hy, sw=0.0):
    pts = [(hx - 24, hy - 76, 1), (hx + 24, hy - 76, 1), (hx + 18, hy + 4, 1), (hx - 18, hy + 4, 1)]
    inner = (f'<rect x="{hx - 30}" y="{hy - 46}" width="60" height="60" fill="#f4a42a"/>'
             f'<rect x="{hx - 30}" y="{hy - 49}" width="60" height="5" fill="#ffd27a"/>' + line([(hx - 15, hy - 66), (hx - 12, hy - 14)], 3.4, "#ffffff", seed=802, op=.8))
    return shape(pts, "#e4f2f8", inner, w=3.4, seed=803)


def balloon_hold(t, col, ph):
    def fn(hx, hy):
        return env.balloon(hx - 10, hy - 230 + 8 * math.sin(t * 5), 62, col, t, ph, (hx, hy - 8), 880)
    return fn


# ───────────────────────── герои
def kid_fig(x, fy, sc, t, fc, walk=None, amp=1.0, mouth="laugh", arms=None, legs=None, hold=None, head_tilt=0.0, look=(0, 0), spiky=0.0, cream=False,
            brow=0.0):
    spec = dict(KID, face=fc, spiky=spiky, cream=cream)
    pose = {"mouth": mouth, "head_tilt": head_tilt, "look": look, "brow": brow}
    if walk is not None:
        pose["walk"] = walk
        pose["amp"] = amp
    if legs:
        pose["legs"] = legs
    if arms:
        pose["arms"] = arms
    if hold:
        pose["hold"] = ("R" if fc >= 0 else "L", hold)
    return person.draw(spec, pose, x, fy, sc, sd=30)


def sis_fig(t, nod=0.0, look=(-.6, 0), mouth="smile", glass=True, arms=None, blink=0.0):
    spec = dict(SIS)
    pose = {"mouth": mouth, "head_tilt": nod, "look": look, "brow": 0.2, "blink": blink,
            "arms": arms or {"L": (-10, -128), "R": (6, 12)}}
    if glass:
        pose["hold"] = ("L", lambda hx, hy: glass_hold(hx, hy - 6))
    fy = FEET + 2 * math.sin(t * 1.9)
    return person.draw(spec, pose, SIS_X, fy, SIS_SC, sd=10)


def dima_fig(t, reach=0.0, jab=0.0, mouth="flat", brows="calm", lid=.55, look=(.3, 0), head_ang=0.0, lean=0.04, x=DIMA_X, finger=True, hood=0.0,
             far_up=0.0):
    """Дима стоит боком вправо. reach 0…1 — рука с поднятым пальцем (near), jab — тычок вперёд."""
    hip = (x, FEET - 296 + 2 * math.sin(t * 2.1))
    sh_y = hip[1] - 172
    arms = {"f": ("ang", 0.12 - .5 * far_up, .35 + 1.3 * far_up)}
    hands = {"f": ("open", .5)}
    held = None
    if reach > 0.01:
        tx = x + 86 + 70 * jab + 14 * reach
        ty = sh_y - 52 * reach + 20 * (1 - reach) + 10 * jab
        arms["n"] = ("ik", (tx, ty))
        hands["n"] = None
        ang = -42 + 20 * jab

        def held(Wr, d, ang=ang):
            return hand5(Wr[0] + d[0] * 24, Wr[1] + d[1] * 24, ang, dima.SKIN, dima.SKIN_SH, 640, sc=1.9, mode="point" if finger else "open", thumb_up=True, ink_w=3.6)
    else:
        arms["n"] = ("ang", 0.18, .35)
        hands["n"] = ("open", .5)
    p = dict(hip=hip, lean=lean, feet={"n": ((x + 52, FEET - 26), 0.0), "f": ((x - 44, FEET - 26), 0.0)}, arms=arms, hands=hands,
             expr={"lid": lid, "look": look, "brows": brows, "mouth": mouth}, head_ang=head_ang, hood=hood)
    if held:
        p["held"] = ("front", held)
        p["held_side"] = "n"
    g, _ = dima.draw(p)
    return g


def talk_mouth(t, a, b, open_m="pant", closed="flat", hz=7.0):
    return open_m if (a <= t < b and math.sin(2 * math.pi * hz * (t - a)) > -.15) else closed


def cat_fig(t, x=CAT_X, y=CAT_Y, s=CAT_S, look=(0, 0), blink=None, tilt=0.0, tail=None, extra="", squash=0.0, flick=None):
    if blink is None:
        ph = (t + 0.9) % 3.1
        blink = 1.0 if ph < .14 else 0.0
    if tail is None:
        tail = 9 * math.sin(t * 2.2)
    if flick is None:
        flick = 0.6 if (t * 0.83) % 2.4 < .2 else 0.0
    return cat.draw(x, y, s, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick, extra=extra, squash=squash)


# ───────────────────────── статика
def build_static():
    if _ST:
        return
    lib.DEFS.clear()
    cat.static_parts()
    _ST["back"] = env.wall_floor() + env.window() + env.picture(60, 330, 170, 210, 740, "#bfe0c2") + env.picture(300, 380, 150, 130, 741, "#f6c6a8") + env.rug()
    _ST["tbl_back"] = env.table_back() + env.under_shadow() + blob(
        [(env.TB_X0 + 10, env.TB_TOP + 60), (env.TB_X1 - 10, env.TB_TOP + 60), (env.TB_X1 - 10, 1300), (env.TB_X0 + 10, 1300)], "#2a1408", .16, blur(12))
    _ST["tbl_top"] = env.table_top() + env.table_props() + env.cake_static() + env.cake_slice(env.SLICE_X, env.TB_TOP - 24) + env.sugar_bowl(env.SUGAR_X, env.TB_TOP - 28)
    lib.static_done()


# ───────────────────────── мир
def world(t, figs, over="", cat_svg=None, conf=True, balloons=True, bunting=True):
    """figs: список (y_ног, svg) — рисуются по возрастанию y. cat_svg — кот под столом."""
    s = [_ST["back"]]
    if bunting:
        s.append(env.bunting(t))
    if balloons:
        s.append(env.balloon_clusters(t))
    s.append(_ST["tbl_back"])
    s.append(cat_svg if cat_svg is not None else cat_fig(t))
    s.append(_ST["tbl_top"])
    s.append(env.candle_flame(t))
    for _, g in sorted(figs, key=lambda a: a[0]):
        s.append(g)
    s.append(over)
    if conf:
        s.append(env.confetti(t, 0.0, 34, (-200, 1400), 200, 380, seed=7))
    return "".join(s)


def sparks_head(t, hx, hy, t0, r=130):
    """Молнии-искры вокруг головы, мерцают."""
    e = t - t0
    if e < 0:
        return ""
    s = []
    for k in range(6):
        a = k * math.pi / 3 + .3 + .6 * math.sin(e * 2)
        if int(e * 16 + k) % 3 == 0:
            continue
        k2 = back_out(clamp(e / .12 - k * .05), 2.4)
        rr = r * (1.0 + .12 * math.sin(e * 20 + k))
        s.append(env.bolt(hx + rr * math.cos(a) * 1.15, hy + rr * math.sin(a), .8 * k2, math.degrees(a) + 90, "#ffd93a" if k % 2 else "#fff27a", sd=900 + k))
    for k in range(5):
        a = k * 1.3 + e * 5
        s.append(env.spark4(hx + (r + 50) * math.cos(a), hy + (r + 40) * math.sin(a), 11 + 5 * math.sin(e * 18 + k), "#fff3a0", e * 200))
    return "".join(s)


def speed_lines(x, y, dirx, t, n=4, length=190, sd=0):
    s = []
    for k in range(n):
        yy = y - 150 + k * 74 + 12 * math.sin(t * 40 + k)
        L = length * (.7 + .3 * ((k * 5 + int(t * 30)) % 3) / 2)
        x0 = x - dirx * (90 + 22 * (k % 2))
        s.append(line([(x0, yy), (x0 - dirx * L * .5, yy + 3), (x0 - dirx * L, yy + 1)], 8, "#ffffff", taper=.9, wmin=.05, seed=sd + k, op=.9, peak=.15))
        s.append(line([(x0, yy), (x0 - dirx * L * .5, yy + 3), (x0 - dirx * L, yy + 1)], 3.2, "#9b8f86", taper=.9, wmin=.05, seed=sd + 10 + k, op=.75, peak=.15))
    return "".join(s)


def dust(x, y, t, ph=0.0):
    s = []
    for k in range(3):
        u = ((t * 3.5 + ph + k / 3) % 1)
        r = 8 + 20 * u
        s.append(blob(ellipse_pts(x - 40 * u * (1 if k % 2 else -1) + (k - 1) * 14, y - 6 - 16 * u, r, r * .7, 10), "#f7ead2", .75 * (1 - u)))
    return "".join(s)


# ───────────────────────── камеры (cx, cy, s, rot)
def hook_fly(t, base=(660, 1010), tail=1.0, kk=0.4):
    """Влёт 1.4 → 1 за 0.22 с с поворотом и затуханием, потом лёгкий дрейф и тряска."""
    u = clamp(t / .22)
    k = 1 / (1 + kk * (1 - ease_out(u, 3)))
    s_ = 1 / k if False else (1 + kk * (1 - ease_out(u, 3)))
    over = 1 + .045 * math.exp(-max(0, t - .22) * 9) * math.sin(max(0, t - .22) * 30) if t > .22 else 1
    rot = 4.2 * (1 - ease_out(u, 3)) + 1.0 * math.sin(t * 7)
    sx, sy = shake(t, T_SLADKOGO, 6, 9, 50)
    return base[0] + 40 * math.sin(t * 2.2) + sx, base[1] + sy, s_ * over * (1 + .02 * t), rot


def cam_s01(t):
    return hook_fly(t)


def cam_s02(t):
    t_w = T_GIPER - .1
    pa = (215 + 14 * (t - 1.3), 920, 1.8 + .1 * (t - 1.3), -1.6 * math.sin(t * 2) + 1)
    pb = (700 + 14 * (t - t_w), 1000, 1.45 + .05 * (t - t_w), 0.0)
    u = ease_io(clamp((t - t_w) / .24))
    if u <= 0:
        return pa
    return tuple(pa[i] + (pb[i] - pa[i]) * u for i in range(4))


def cam_s03(t):
    e = t - 3.5
    sx, sy = shake(t, T_SKAZAL, 10, 10, 60)
    return 880 + 18 * e + sx, 1050 + sy, 1.46 + .07 * e + .03 * math.exp(-max(0, t - T_SKAZAL) * 8), .8 * math.sin(e * 3)


def cam_s04(t):
    u = ease_io(clamp((t - 5.3) / 2.5))
    return 360 + 460 * u, 1090 - 14 * u, 1.24 + .04 * math.sin(t * 3), -1.0 + 2.0 * u


def cam_s14(t):
    u = (t - 26.7) / 2.5
    k = kick(t, [T_PRAZD], .04, 12)
    return 380 + 360 * ease_io(clamp(u)) , 1030, 1.15 + .05 * u + (k[0] - 1) * 1.2, 1.2 * math.sin(t * 2.4) + k[1]


def cam_s15(t):
    e = t - 28.8
    return 270 + 6 * e + 10 * math.sin(t * 1.3), 1195 - 4 * e, 2.5 + .05 * e, 0.8 * math.sin(t * 1.7)


# ───────────────────────── планы
def kid_loop(t, cx=565, rx=135, ry=46, cy=1304, w=2 * math.pi / 1.1, th0=2.3):
    th = th0 + w * t
    x = cx + rx * math.cos(th)
    y = cy + ry * math.sin(th)
    dx = -rx * math.sin(th) * w
    return x, y, (1 if dx >= 0 else -1), th


def s01(t):
    x, y, d, th = kid_loop(t)
    sc = KID_SC * (1 + .08 * math.sin(th))
    ph = 2 * math.pi * 3.6 * t
    arms = {"L": (-48 * math.sin(ph) + 20, 62), "R": (48 * math.sin(ph) + 20, 62)}
    kid = kid_fig(x, y - 18 * abs(math.sin(ph)), sc, t, .75 * d, walk=ph, amp=1.9, mouth="laugh", arms=arms, head_tilt=-5 * d, look=(d * .7, 0))
    over = speed_lines(x, y - 190 * sc * 1.4, d, t, 4, sd=950) + dust(x - d * 30, y + 4, t)
    # на кадре 0 — брызги от взлёта: звёздочки у ног и скобки движения
    figs = [(y, kid + over), (FEET, dima_fig(t, 0.0, 0.0, "flat", "up", .9, look=(-.3, 0), lean=.03 + .01 * math.sin(t * 6))),
            (FEET + 1, sis_fig(t, nod=3 * math.sin(t * 6), look=(-.6, 0), mouth="o"))]
    return world(t, figs)


def s02(t):
    e = t - T_GIPER
    jump = max(0.0, math.sin(math.pi * ((t - 2.35) * 2.2 % 1))) * 90 if t > 2.3 else 8 * abs(math.sin(t * 9))
    sp = ease_out(clamp((t - T_GIPER) / .18), 2)
    ph = 2 * math.pi * 4 * t
    up = clamp((t - 2.3) / .1)
    arms = {"L": (-170 * up - 30 * (1 - up) * math.sin(ph) + 8, -14), "R": (170 * up + 30 * (1 - up) * math.sin(ph) + 8, 14)}
    legs = {"L": (14, 34 if t > 2.3 else 6), "R": (-14, 34 if t > 2.3 else 6)}
    fy = 1290 - jump
    kid = kid_fig(590, fy, KID_SC * 1.05, t, .3, mouth="yell" if t > 2.3 else "laugh", arms=arms, legs=legs, head_tilt=4 * math.sin(t * 17) * up, spiky=sp,
                  look=(0, -.3), brow=.8 * sp)
    hy = fy - 700 * KID_SC * 1.05 * .96
    over = sparks_head(t, 590, hy, T_GIPER - .02, 150) if t >= T_GIPER else ""
    over += dust(590, 1296, t, .3)
    # крупно: куски торта и кубики — подпрыгивают на «гиперактивными» (искры над кубиками)
    ex = ""
    if t < 2.5:
        for k, (px, py) in enumerate(((env.SUGAR_X - 26, 960), (env.SUGAR_X + 22, 940), (env.SLICE_X + 6, 905), (env.CAKE_X - 20, 800))):
            ex += env.spark4(px + 6 * math.sin(t * 9 + k), py - 12 * ((t * 1.7 + k * .3) % 1), 12 * (1 - ((t * 1.7 + k * .3) % 1)), "#ffffff", t * 160)
    figs = [(FEET, dima_fig(t, 0.0, 0.0, "flat", "calm", .55, look=(.1, 0))), (FEET + 1, sis_fig(t, nod=0, look=(-.6, 0), mouth="smile")), (1289, kid + over)]
    return world(t, figs, over=ex)


def s03(t):
    # Дима «уверенно говорит»: палец вверх, на «сказал» тычет
    reach = ease_out(clamp((t - 3.6) / .22), 3)
    jab = 0.0
    if t > T_SKAZAL:
        q = t - T_SKAZAL
        jab = clamp(math.sin(clamp(q / .5) * math.pi)) * 1.0
        jab = max(jab, 0.0)
    d_mouth = talk_mouth(t, 3.7, 5.3)
    dm = dima_fig(t, reach, jab, d_mouth, "up" if reach > .3 else "calm", .75, look=(.45, 0), lean=.05 + .02 * math.sin(t * 8) + .03 * jab, head_ang=-.03 * jab)
    nod = 7 * math.sin((t - 3.9) * 2 * math.pi * 1.8) * smooth(3.8, 4.1, t)
    sis = sis_fig(t, nod=nod, look=(-.65, 0), mouth="smile")
    ex = ""
    if t > T_SKAZAL:
        q = t - T_SKAZAL
        for k in range(4):                       # штрихи тычка у пальца
            a = math.radians(-50 + k * 24)
            r0, r1 = 40 + 90 * q, 80 + 120 * q
            x0, y0 = DIMA_X + 210, FEET - 590
            if q < .3:
                ex += line([(x0 + r0 * math.cos(a), y0 + r0 * math.sin(a)), (x0 + r1 * math.cos(a), y0 + r1 * math.sin(a))], 7 * (1 - q / .3) + 1.5, INK, taper=.8, wmin=.1, seed=960 + k)
    figs = [(FEET, dm), (FEET + 1, sis)]
    kid_far = kid_fig(250, 1300, KID_SC, t, .6, walk=2 * math.pi * 3 * t, amp=1.7, mouth="laugh")
    figs.append((1300, kid_far))
    return world(t, figs, over=ex)


def s04(t):
    # племянник проносится слева направо; на «носился» (6.0) в центре кадра
    u = (t - T_NOSILSYA) / 1.05
    x = 540 + 520 * u
    fy = 1346
    sc = .62
    ph = 2 * math.pi * 3.2 * t
    arms = {"L": (-35 * math.sin(ph) + 14, 40), "R": (35 * math.sin(ph) + 8, 70)}
    plate = plate_hold
    kid = kid_fig(x, fy - 16 * abs(math.sin(ph)), sc, t, .85, walk=ph, amp=1.5, mouth="laugh", arms={"L": arms["L"], "R": (62, 74)}, hold=plate, cream=True,
                  head_tilt=-4)
    over = speed_lines(x, fy - 230, 1, t, 3, sd=970) + dust(x - 20, fy + 2, t)
    # крошки летят с тарелки
    rs = np.random.RandomState(4)
    for k in range(10):
        e = (t - (T_NOSILSYA - .4)) * 1.0 - k * .04
        if e < 0 or e > 1.0:
            continue
        cx_ = x - 60 - 150 * e + rs.uniform(-30, 30) * e
        cy_ = fy - 260 + 190 * e * e - 90 * e + rs.uniform(-20, 10)
        over += blob(ellipse_pts(cx_, cy_, 5 + (k % 3), 4, 6), ["#f6d9a0", "#c98a54", "#f7a9bc"][k % 3])
    # взгляды: Дима, сестра, кот следят за мальчиком
    look_x = clamp((x - DIMA_X) / 320, -1, 1)
    dm = dima_fig(t, 0.0, 0.0, "pant" if t > T_NOSILSYA else "flat", "up", .85, look=(clamp(look_x * .9 + .4, -.8, .9), 0), head_ang=-.05 * (1 - look_x))
    sis = sis_fig(t, nod=-3 * look_x, look=(clamp((x - SIS_X) / 300, -1, 1) * .9, 0), mouth="o")
    ct = cat_fig(t, look=(clamp((x - CAT_X) / 400, -1, 1), 0), tilt=4 * clamp((x - CAT_X) / 500, -1, 1), tail=18 * math.sin(t * 5))
    figs = [(FEET, dm), (FEET + 1, sis), (fy, kid + over)]
    return world(t, figs, cat_svg=ct)


def s14(t):
    e = t - T_PRAZD
    x = 560 + 30 * math.sin(t * 2.4)
    jump = abs(math.sin((t - 26.7) * 2 * math.pi * 1.3)) * 70
    up = clamp((t - 26.7) / .2)
    bal = balloon_hold(t, "#e8505b", 2.0)
    arms = {"L": (-30 + 12 * math.sin(t * 8), 22), "R": (-150 * up, 10)}
    kid = kid_fig(x, FEET + 18 - jump, KID_SC * 1.08, t, .35, mouth="laugh", arms={"L": arms["L"], "R": (150, 12)}, legs={"L": (10, 16), "R": (-10, 16)},
                  hold=bal, head_tilt=5 * math.sin(t * 9), look=(0, -.2))
    dm = dima_fig(t, 0.0, 0.0, "grin", "up", .8, look=(.3, 0), lean=.03 + .015 * math.sin(t * 5), far_up=.2 + .1 * math.sin(t * 6))
    sis = sis_fig(t, nod=4 * math.sin(t * 4), look=(-.6, 0), mouth="laugh")
    over = env.confetti(t, T_PRAZD - .02, 70, (-100, 1300), 420, 700, seed=21, life=2.5) if t >= T_PRAZD else ""
    if 0 <= e < .35:
        for k in range(12):                      # хлопушка-вспышка
            a = k * math.pi / 6
            over += line([(x + 90 * math.cos(a), 700 + 90 * math.sin(a)), (x + (150 + 200 * e) * math.cos(a), 700 + (150 + 200 * e) * math.sin(a))],
                         7 * (1 - e / .35) + 1, "#ffd93a" if k % 2 else "#f2788d", taper=.8, wmin=.1, seed=980 + k)
    # серпантин (змейки сверху)
    for k in range(5):
        x0 = 120 + k * 250 + 18 * math.sin(t * 2 + k)
        ln = 280 + 120 * ((k * 7) % 3)
        pts = [(x0 + 24 * math.sin(j * .9 + t * 3 + k), 200 + j * ln / 8) for j in range(9)]
        over += line(pts, 9, env.COL[(k + 2) % 6], taper=.2, wmin=.7, seed=990 + k)
    figs = [(FEET, dm), (FEET + 1, sis), (FEET + 18, kid)]
    return world(t, figs, over=over)


def s15(t):
    e = t - T_KOT
    # кот въезжает прыжками справа на «кот» (29.24) и садится к крошкам
    if t < T_KOT:
        x, y, vis = 700, CAT_Y, False
    else:
        u = clamp((t - T_KOT) / .5)
        x = 560 + (CAT_X - 560) * ease_out(u, 2)
        y = CAT_Y - 90 * abs(math.sin(u * math.pi * 2)) * (1 - u * .4) if u < 1 else CAT_Y
        vis = True
    eat = smooth(T_KOT + .55, T_KOT + .7, t)
    chew = eat * (math.sin((t - T_KOT) * 2 * math.pi * 4.6) * .5 + .5)
    gulp = ease_out(clamp((t - T_KROSHKAM - .2) / .12)) * (1 - smooth(T_KROSHKAM + .3, T_KROSHKAM + .6, t))
    blink = 1.0 if (eat > .5) else 0.0
    mouth = ""
    if eat > .5:
        mo = clamp(chew + .8 * gulp)
        mouth = (shape(ellipse_pts(836, 1129, 11, 3 + 11 * mo, 10), "#4a1c1c", blob(ellipse_pts(836, 1132, 7, 3 + 4 * mo, 8), "#d46a6a"), w=2.4, seed=990))
    squash = -.04 * chew + .03 * gulp
    tilt = (8 * math.sin((t - T_KOT) * 2 * math.pi * 2.3)) * eat + (-8 if t < T_KOT + .5 and vis else 0)
    ct = cat_fig(t, x, y, CAT_S, look=(.3, .5), blink=blink if eat > .5 else None, tilt=tilt, tail=34 * math.sin(t * 8.5) if vis else 0, extra=mouth, squash=squash) if vis else ""
    over = ""
    # крошки на полу и падающие со стола
    rs = np.random.RandomState(9)
    for k in range(9):
        cx_ = 190 + rs.uniform(0, 130)
        over += blob(ellipse_pts(cx_, 1298 + rs.uniform(-4, 6), 6 + k % 3, 3, 6), ["#f6d9a0", "#c98a54", "#f7a9bc"][k % 3])
    for k in range(5):                           # сыплются со стола
        ph = (t * .9 + k * .21) % 1
        cx_ = 120 + k * 70 + 10 * math.sin(t * 4 + k)
        if t < T_KROSHKAM or k != 2:
            over += blob(ellipse_pts(cx_, 1090 + ph * 200, 5, 4, 6), ["#f6d9a0", "#c98a54", "#f7a9bc"][k % 3])
    # крупная крошка падает прямо в рот на «крошкам» (30.28)
    if T_KROSHKAM - .26 <= t < T_KROSHKAM + .16:
        u = (t - (T_KROSHKAM - .26)) / .42
        mx, my = CAT_X, CAT_Y + (1129 - 1306) * CAT_S + 4
        over += blob(ellipse_pts(mx + 8 * (1 - u), 900 + (my - 900) * u * u, 15 * (1 - .4 * u), 12 * (1 - .4 * u), 8), "#d9a35a")
        over += blob(ellipse_pts(mx + 10 * (1 - u) - 4, 898 + (my - 900) * u * u - 3, 6, 4, 6), "#f6d9a0")
    if t >= T_KROSHKAM + .12:
        q = t - T_KROSHKAM - .12
        for k in range(5):
            a = k * 1.26 + .3
            over += env.spark4(CAT_X + 90 * q * math.cos(a) * 3, CAT_Y - 80 + 70 * q * math.sin(a) * 2 - 90 * q, 12 * (1 - clamp(q / .6)), "#fff3a0", q * 300)
    figs = []
    return world(t, figs, over=over, cat_svg=ct, bunting=False, balloons=False)


CAMS = {"s01": cam_s01, "s02": cam_s02, "s03": cam_s03, "s04": cam_s04, "s14": cam_s14, "s15": cam_s15}
SCN = {"s01": s01, "s02": s02, "s03": s03, "s04": s04, "s14": s14, "s15": s15}


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    cx, cy, s, rot = CAMS[sid](t)
    body = SCN[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#f2d3ae"/><g transform="{cam(cx, cy, s, rot)}">{body}</g>')


_ = (INK, ease_in, mul, f, pop, hand_text)
