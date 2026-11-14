"""s04 (4.85–6.45, клип 4.65–6.65): комната вечером. Дима с кружкой чая в одной руке и сумкой в другой; на «остаться»
(5.32) с размаху швыряет сумку в угол к торшеру (сумка летит, шлёпается, сплющивается); на «дома» (5.76) плюхается на
диван, откидываясь на спинку, ноги на сиденье; плед падает сверху на ноги; рука берёт пульт с подлокотника и щёлкает
на телевизор (голубой отсвет). Довольный. Камера — отъезд, толчок на «дома»."""
import math

import numpy as np

import dima
import hero
import lib
import room
from lib import clamp, ease_in, ease_io, ease_out, smooth

T_A, T_B = 4.65, 6.65
T_THROW, T_FLOP = 5.32, 5.76
HX = 70.0
H1 = np.array([-14.0, -256.0])
LEAN1 = -0.66
REMOTE0 = np.array([-205.0, room.ARM_Y - 8])
_S = {}


def flop_u(t):
    return clamp((t - (T_FLOP - 0.30)) / 0.30)


def bag_path(t):
    """Сумка после броска: из руки в угол по параболе, шлепок, отскок."""
    if "rel" not in _S:
        _S["rel"] = dima.draw(pose(T_THROW))[1]["n"]
    p0 = _S["rel"]
    p1 = np.array([room.CORNER[0] - 105, -62.0])
    T1 = 0.27
    u = clamp((t - T_THROW) / T1)
    x = p0[0] + (p1[0] - p0[0]) * u
    y = p0[1] + (p1[1] - p0[1]) * u - 260 * math.sin(math.pi * u) * (1 - .3 * u)
    rot = -40 + 400 * ease_out(u, 1.4)
    sq = 0.0
    if t > T_THROW + T1:
        v = t - T_THROW - T1
        sq = 0.55 * math.exp(-9 * v) * math.cos(2 * math.pi * 3 * v)
        y -= 26 * abs(math.sin(2 * math.pi * 1.6 * v)) * math.exp(-8 * v)
        rot = 360 + 8 * math.exp(-6 * v) * math.sin(v * 30)
    return np.array([x, y]), rot % 360, sq


def held_bag(t):
    def f(Wr, d):
        sw = 10 * math.sin(t * 6)
        c = Wr + np.array([sw, 150.0])
        out = hero.line([tuple(Wr + np.array([-40, 20])), tuple(c + np.array([-60, -70]))], 12, "#1b2445", seed=975, taper=.1, wmin=.9)
        out += hero.line([tuple(Wr + np.array([40, 20])), tuple(c + np.array([60, -70]))], 12, "#1b2445", seed=976, taper=.1, wmin=.9)
        return out + hero.duffel(c[0], c[1], w=330, h=170, rot=sw * .3, seed=982)
    return f


def held_mug(t, lift):
    def f(Wr, d):
        tilt = -14 * math.sin(math.pi * flop_u(t)) * (1 - lift * 0)
        return room.mug(Wr[0] + 150, Wr[1] + 120, k=2.1, steam_t=t, tilt=tilt)
    return f


def pose(t):
    u = flop_u(t)
    e = ease_in(u, 1.7)
    land = t - T_FLOP
    bounce = -14 * math.exp(-7 * land) * math.sin(2 * math.pi * 2.4 * land) if land > 0 else 0.0
    H0 = np.array([HX, -(hero.SOLE + hero.LEG * 0.985)])
    hip = H0 + (H1 - H0) * e + np.array([0, bounce])
    hip[1] += -6 * math.sin(math.pi * clamp((t - T_THROW + .25) / .5)) * (1 - u)
    lean = 0.04 + (LEAN1 - 0.04) * ease_io(u) + 0.03 * smooth(T_THROW - .2, T_THROW, t) * (1 - u)
    if land > 0:
        lean += 0.05 * math.exp(-6 * land) * math.sin(2 * math.pi * 2 * land)
    # ноги: с пола на сиденье дугой
    fa0, na0 = np.array([HX - 34, -hero.SOLE]), np.array([HX + 36, -hero.SOLE])
    fa1, na1 = np.array([214.0, -286.0]), np.array([236.0, -270.0])
    lift = -90 * math.sin(math.pi * u)
    fa = fa0 + (fa1 - fa0) * ease_io(u) + np.array([0, lift])
    na = na0 + (na1 - na0) * ease_io(u) + np.array([0, lift * 1.2])
    phi = -1.25 * ease_io(u)
    sat = smooth(0.6, 1.0, u)
    expr = dict(lid=0.55 - 0.2 * sat, look=(0.5, 0.05), brows="calm", mouth="grin" if 0.3 < u < 1 or 0 < land < 0.18 else "smile",
                hair=-12 * math.exp(-7 * max(0, land)) * math.cos(max(0, land) * 22) if land > 0 else 6 * u)
    p = dict(hip=hip, lean=lean, feet={"f": (fa, phi), "n": (na, phi)}, hands={"n": "fist", "f": "fist"},
             head_ang=0.12 * sat + 0.02 * math.sin(t * 3), hood=0.0, strings=(0, 0), expr=expr)
    # ближняя рука: держит сумку → замах → бросок → вверх на падении → к пульту на подлокотнике → к груди, щелчок
    sh_w = hip + np.array([math.sin(lean), -math.cos(lean)]) * 176
    if t < T_THROW:
        wb = smooth(T_THROW - .32, T_THROW - .14, t)
        fw_ = smooth(T_THROW - .14, T_THROW, t)
        tgt = np.array([HX + 20, -300.0]) + np.array([-110, 20]) * wb * (1 - fw_) + np.array([130, -170]) * fw_
        side = -1
    else:
        a = np.array([HX + 150, -470.0])
        rest = sh_w + np.array([120.0, 100.0])
        tgt = a + (rest - a) * ease_io((t - T_THROW) / 0.4)
        r = smooth(6.00, 6.18, t) * (1 - smooth(6.24, 6.40, t))
        tgt = tgt + (REMOTE0 + np.array([30.0, -6.0]) - tgt) * r
        tgt = tgt + (sh_w + np.array([140.0, 40.0]) - tgt) * smooth(6.24, 6.40, t)
        side = -1
    p["arms"] = {"n": ("ik", tgt, side), "f": ("ik", sh_w + np.array([110.0 + 30 * (1 - u), 120.0 - 95 * u]), -1)}
    if t < T_THROW:
        p["held"] = ("front", held_bag(t))
        p["held_side"] = "n"
    else:
        p["held_side"] = "n"
    p["held2"] = ("behind", held_mug(t, u))
    p["hand_dir"] = {"f": (1.0, -0.1)}
    if 6.0 <= t < 6.22:
        p["hands"] = {"n": ("open", smooth(6.12, 6.2, t)), "f": "fist"}
    return p


def camera(t):
    o = smooth(T_THROW - 0.05, T_FLOP + 0.15, t)
    cx = 110 + 72 * o
    cy = -440 + 70 * o
    s = 1.80 - 0.44 * o + 0.03 * (t - T_A)
    land = t - T_FLOP
    if land > -0.03:
        s *= 1 + 0.06 * smooth(-0.03, 0.03, land) * math.exp(-4 * max(0, land))
    return cx, cy, s, 0.5 * math.sin(t * 1.4)


def frame(t):
    lib.DEFS.clear()
    dima.set_palette(dima.HOODIE)
    cx, cy, s, rot = camera(t)
    tv = smooth(6.44, 6.52, t) * (0.85 + 0.15 * math.sin(t * 23))
    w = [room.back(t, tv), room.sofa_back(t)]
    # пульт на подлокотнике (пока не взят)
    pp = pose(t)
    g, info = dima.draw(pp)
    held_remote = t >= 6.18
    if not held_remote:
        w.append(room.remote(REMOTE0[0], REMOTE0[1], ang=-8, k=0.95))
    if t < T_THROW:
        w.append(f'<ellipse cx="{HX:.1f}" cy="4" rx="150" ry="18" fill="#3a2418" opacity=".25"/>')
    w.append(g)
    # плед: падает на ноги после «дома»
    pu = clamp((t - (T_FLOP + 0.02)) / 0.2)
    if pu > 0:
        k = ease_out(pu, 2.2)
        dy = -260 * (1 - k)
        dx = -40 * (1 - k)
        sq = 0.12 * math.exp(-10 * max(0, t - T_FLOP - .22)) * math.sin(max(0, t - T_FLOP - .22) * 30)
        H = pp["hip"]
        top = [(H[0] - 40, H[1] - 62), (H[0] + 50, H[1] - 84), (H[0] + 130, H[1] - 92), (H[0] + 200, H[1] - 76), (H[0] + 260, H[1] - 54),
               (H[0] + 300, H[1] - 30)]
        top = [(x + dx + (x - H[0]) * .2 * (1 - k), y + dy + sq * 40 - 30 * (1 - k) * math.sin(i)) for i, (x, y) in enumerate(top)]
        w.append(room.plaid(top, drop=126 + 40 * (1 - k), seed=7700))
    if held_remote:
        wr = info["n"]
        lit = smooth(6.42, 6.46, t) * (1 - smooth(6.52, 6.6, t))
        w.append(room.remote(wr[0] + 22, wr[1] + 2, ang=-14, k=0.95, lit=lit))
    # сумка в полёте и в углу
    if t >= T_THROW:
        bp, br, sq = bag_path(t)
        w.append(f'<ellipse cx="{bp[0]:.1f}" cy="2" rx="{90 * (1 + max(0, sq)):.1f}" ry="12" fill="#3a2418" opacity="{.28 * clamp((bp[1] + 300) / 240):.3f}"/>')
        k = 0.44
        w.append(f'<g transform="translate({bp[0]:.1f} {bp[1]:.1f}) rotate({br:.1f}) scale({k * (1 + .25 * sq):.4f} {k * (1 - .3 * sq):.4f})">'
                 f'{hero.duffel(0, 0, w=330, h=170, seed=983)}</g>')
        if t < T_THROW + 0.27:
            u = (t - T_THROW) / 0.27
            w.append(hero.motion_lines([[(bp[0] - 120, bp[1] - 40 + 60 * u), (bp[0] - 60, bp[1] - 30 + 40 * u)],
                                        [(bp[0] - 130, bp[1] + 10 + 40 * u), (bp[0] - 70, bp[1] + 10 + 30 * u)]], op=.7, seed=990))
    body = f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(w)}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#2a2030"/>{body}{room.vignette()}')
