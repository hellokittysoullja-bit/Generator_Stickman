"""Рилс 82 «Опять опоздал?», группа C: хук-бег s01–s03, Сан-Диего s14, петля s19–s20.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Время — только из shots.json (t0/t1) и voice/words.json (слова по
индексу wN); секунды в коде — длительности движений. Улица и Сан-Диего — common/room.py (раздел 82), часы на столбе и скамейка —
common/props.py, заголовок — common/big_title.py. Бег — код run рилса 40 (rdima.py, rcat.py — копии с частями хука).
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука (Дима, кот, столб с часами)
белым на чёрном, с камерой (замер заполнения)."""
import json
import math
import os
import sys

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(1, os.path.join(REPO, "scripts"))
import big_title  # noqa: E402
import lib  # noqa: E402
import props as PR  # noqa: E402
import rcat as Cat  # noqa: E402
import rdima as dima  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    return W(i) + (WE(i) - W(i)) * u


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def kick(t, t0, rise=.04, tau=.12):
    u = t - t0
    if u <= 0:
        return 0.0
    return (u / rise) if u < rise else math.exp(-(u - rise) / tau)


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def title(t):
    """Заголовок хука: экранный слой s01–s03; держится до склейки s03→s04 (решение диспетчера) и уходит сжатием к ней."""
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, t_in=SH["title"]["t_in"], t_out=T0("s04") - 0.15, hits=hits)


# ═════════════════════════ бег: план шагов (из run/scene.py рилса 40, быстрее и с прыжком) ═════════════════════════
BS = dima.BS
LEG = (dima.THIGH + dima.SHIN) * BS
AHW = dima.AH * BS
TOEW = dima.TOE * BS * 1.22
C = {}
PL = {}


def plan(conf):
    """conf: a, b (время), x0 (таз в мире на a), tc (шаг, с), st (доля опоры), step (длина), leap=(t, dur, len) или None,
    stumble=t или None, walk (спокойный шаг)."""
    C.clear()
    C.update(conf)
    tc, step = conf["tc"], conf["step"]
    st = conf["st"] * tc
    Cn = []
    for k in range(1, 16):
        Cn.append([conf["a"] - k * tc, "n" if k % 2 == 0 else "f", conf["x0"] - k * step, 0.0, conf["a"] - k * tc + st, tc, None])
    Cn = Cn[::-1]
    t, x, k = conf["a"], conf["x0"], 0
    lps = [conf[k_] for k_ in ("leap", "leap2") if conf.get(k_)]
    used = [False] * len(lps)
    while t < conf["b"] + 2.0:
        ttc, sstep, tag = tc, step, None
        for j, lp in enumerate(lps):
            if not used[j] and t + tc > lp[0]:
                ttc, sstep, used[j], tag = lp[1], lp[2], True, j
                break
        if conf.get("stumble") and abs(t - conf["stumble"]) < tc / 2:
            ttc, sstep = tc * 1.25, step * .55
        Cn.append([t, "n" if k % 2 == 0 else "f", x, 0.0, t + st, ttc, tag])
        t += ttc
        x += sstep
        k += 1
    keys = [((c[0] + c[4]) / 2, c[2] + 6) for c in Cn]
    ts, xs = zip(*keys)
    PL.clear()
    PL.update(C=Cn, hip_x=PchipInterpolator(np.array(ts), np.array(xs)))


def hip_at(t, bob=True):
    x = float(PL["hip_x"](t))
    y = -(LEG * (0.86 if not C.get("walk") else 0.93) + AHW)
    if bob:
        best, tc = 9.0, C["tc"]
        for c in PL["C"]:
            dt = t - (c[0] + c[4]) / 2
            if abs(dt) < abs(best):
                best, tc = dt, c[5]
        y += (12 if not C.get("walk") else 7) * math.cos(2 * math.pi * best / max(tc, 1e-3) * (C["tc"] / tc if tc > C["tc"] * 1.4 else 1))
        for c in PL["C"]:
            if len(c) > 6 and c[6] is not None:
                u = (t - c[4]) / (c[0] + c[5] - c[4])
                if 0 < u < 1:
                    y -= 115 * math.sin(math.pi * u)
    return np.array([x, y])


def planted(c, hip):
    A = np.array([c[2], c[3] - AHW])
    reach = LEG * 0.985
    if np.linalg.norm(A - hip) <= reach:
        return A, 0.0
    toe = np.array([c[2] + TOEW, c[3]])
    lo, hi = 0.0, 1.35
    for _ in range(30):
        m = (lo + hi) / 2
        A2 = toe + dima.rot(np.array([-TOEW, -AHW]), m)
        if np.linalg.norm(A2 - hip) > reach:
            lo = m
        else:
            hi = m
    return toe + dima.rot(np.array([-TOEW, -AHW]), hi), hi


def foot_at(side, t, hip):
    cs = [c for c in PL["C"] if c[1] == side]
    prev, nxt = cs[0], None
    for c in cs:
        if c[0] <= t:
            prev = c
        elif nxt is None:
            nxt = c
    if t <= prev[4] or nxt is None:
        return planted(prev, hip)
    t0, t1 = prev[4], nxt[0]
    u = clamp((t - t0) / (t1 - t0))
    A0, ph0 = planted(prev, hip_at(t0))
    A1 = np.array([nxt[2], nxt[3] - AHW])
    lift = (128 if not C.get("walk") else 60) * (1.0 + 0.5 * (t1 - t0 > 0.3))
    ux = (1 - math.cos(math.pi * u ** 1.3)) / 2
    x = A0[0] + (A1[0] - A0[0]) * ux - (30 if not C.get("walk") else 10) * math.sin(math.pi * clamp(u * 1.5))
    y = A0[1] + (A1[1] - A0[1]) * u - lift * math.sin(math.pi * clamp(u * 1.08)) ** 1.3
    if C.get("walk"):
        phi = 0.35 * math.sin(math.pi * u) - 0.1 * smooth(.8, 1, u)
        return np.array([x, y]), phi
    if u < .3:
        phi = ph0 + (0.75 - ph0) * smooth(0, .3, u)
    elif u < .85:
        phi = 0.75 + (-0.26 - 0.75) * smooth(.3, .85, u)
    else:
        phi = -0.26 * (1 - smooth(.85, 1.0, u))
    return np.array([x, y]), phi


def contacts(t0, t1, side=None):
    return [c for c in PL["C"] if t0 <= c[0] <= t1 and (side is None or c[1] == side)]


def run_pose(t, expr=None, held=None, foot=None, mug=None):
    hip = hip_at(t)
    feet = {s: foot_at(s, t, hip) for s in ("n", "f")}
    cn = [c for c in PL["C"] if c[1] == "n"]
    prev = max([c for c in cn if c[0] <= t], key=lambda c: c[0], default=cn[0])
    psi = 2 * math.pi * (t - prev[0]) / (2 * prev[5])
    walk = C.get("walk")
    arms = {}
    for s_, sg in (("n", 1), ("f", -1)):
        sw = -sg * math.cos(psi)
        if walk:
            arms[s_] = ("ang", 0.05 + 0.32 * sw, 0.5 + 0.2 * max(0, sw))
        else:
            amp = 1.05
            arms[s_] = ("ang", 0.1 + amp * sw, 1.5 + 0.4 * max(0, sw) - 0.4 * max(0, -sw))
    vy = (hip_at(t)[1] - hip_at(t - .05)[1]) / .05
    lean = (0.36 if not walk else 0.06) + C.get("lean_add", lambda t: 0.0)(t)
    p = dict(hip=hip, lean=lean, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"}, head_ang=-0.12 if not walk else 0.02,
             hood=clamp(-vy * 0.05, -16, 22), strings=(clamp(-vy * .04, -30, 30) - 22, clamp(vy * .05, -20, 30)),
             expr=dict(lid=0.95, look=(0.5, -0.05), brows="worry", mouth="flat", hair=clamp(vy * 0.04, -18, 18)))
    if expr:
        p["expr"].update(expr)
    if held is not None:
        p["held_shoe"] = ("n", held)
    if foot:
        p["foot"] = foot
    if mug:
        p["held"] = ("front", mug)
        p["held_side"] = "n"
    return p


# ═════════════════════════ камера бега ═════════════════════════
def track_cam(t, s, sx, gy, shake=1.0, drift=1.0):
    """Трекинг за тазом: таз на экране x = sx, земля на экране y = gy; тряска на каждой опоре 6–10 px, боковой занос."""
    h = (hip_at(t, bob=False) + hip_at(t + .08, bob=False)) / 2
    cx = h[0] + (540 - sx) / s
    cy = (960 - gy) / s
    dy = 0.0
    dx = 0.0
    if shake:
        for i, c in enumerate(contacts(t - 0.4, t)):
            amp = 7.0 + 3.0 * ((int(c[2]) // 7) % 2)
            dy += amp * kick(t, c[0], .03, .07) * math.cos(2 * math.pi * 9 * max(0, t - c[0] - .03))
            dx += (2.5 if i % 2 else -2.5) * kick(t, c[0], .03, .07)
        dy *= shake
        dx *= shake
    dx += drift * (16 * math.sin(t * 2.6 + .4) + 7 * math.sin(t * 5.3))
    rot = drift * (0.7 * math.sin(t * 1.9 + .3)) + shake * 0.25 * dy / 8
    return cx - dx / s, cy - dy / s, s, rot


def hook_wrap(body, t, hit):
    """Влёт правил 28–29 поверх кадра (anim.hook_cam): масштаб, поворот, занос, радиальное размытие копиями."""
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    tr = f"translate({540 + dx:.2f} {PIV + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-PIV})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<g opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {PIV + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-PIV})">{body}</g>')
    return f'<rect width="1080" height="1920" fill="#a9cfe9"/><g transform="{tr}">{body}</g>{blur}'


PIV = 560.0     # центр влёта и удара — у головы Димы: удар на «вовремя» не уводит голову под заголовок


MASK_F = '<filter id="mk82"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def mask_svg(world_mask, cam):
    lib.DEFS.append(MASK_F)
    return lib.svg('<rect width="1080" height="1920" fill="#000"/>'
                   f'<g transform="{lib.cam(*cam)}"><g filter="url(#mk82)">{world_mask}</g></g>')


# ═════════════════════════ хук s01–s02: погоня ═════════════════════════
V_RUN = 232.0 / 0.176
HOOK = dict(a=-0.4, b=T1("s03") + 0.4, leap2=(W(9) - 0.04, 0.34, 440.0), x0=0.0, tc=0.176, st=0.55, step=232.0, leap=(W(2) - 0.07, 0.36, 470.0), stumble=None,
            lean_add=lambda t: 0.28 * kick(t, stress(6, .3), .06, .22))
PUD_LEAP = None
CLOCK1 = None
CLOCK2 = None
CAT_REL = 300.0
CLOCK_K = 0.5


def REL01(t):
    return CAT_REL


def REL02(t):
    """s02 (низкий ракурс, кот у самых ног): «всё равно» — кот обгоняет ногу Димы."""
    return 150.0 + 26.0 * smooth(W(4) - .05, W(5) + .35, t)


def _setup_hook():
    global PUD_LEAP, CLOCK1, CLOCK2
    plan(HOOK)
    c = next(c for c in PL["C"] if c[6] == 0)
    PUD_LEAP = ((c[2] + c[2] + HOOK["leap"][2]) / 2 + 40, 34.0, 120.0)
    CLOCK1 = hip_at(W(1), bob=False)[0] + 430.0
    CLOCK2 = hip_at(stress(6, .4), bob=False)[0] + 330.0

    Cat.REL_FN[0] = REL01
    Cat.SPAN[0], Cat.SPAN[1] = -1.0, 4.0
    Cat._grid.clear()


_setup_hook()


def clock_hand(t, t_jump, a0, a1):
    """Минутная стрелка: стоит на a0, на t_jump перескакивает на a1 с отскоком (пружина)."""
    if t < t_jump:
        return a0 + 2 * math.sin(t * 20) * 0, 0.0
    u = t - t_jump
    e = 1 - math.exp(-u / .03) * math.cos(2 * math.pi * 7 * u) if u < .6 else 1.0
    return a0 + (a1 - a0) * min(1.12, e), max(0.0, 1 - u / .35)


def sandwich_state(t):
    """Где бутерброд: в зубах (подлетает над ртом на прыжке), летит (s02, «опоздал?»), на спине кота."""
    tl = stress(6, .45)
    if t < tl:
        return "mouth"
    if t < tl + 0.32:
        return "fly"
    return "back"


def dima_hook(t):
    """Поза Димы в хуке: одна нога босая, другая в носке, ботинок в руке, бутерброд в зубах (на прыжке подлетает)."""
    lp = HOOK["leap"]
    jump = math.sin(math.pi * clamp((t - lp[0] - .06) / (lp[1] - .02)))
    sw = 0.45 * math.sin(2 * math.pi * (t / (2 * HOOK["tc"])) - 1.2)
    ex = dict(sandwich=sandwich_state(t) == "mouth", sw_rot=4.0 - 18 * jump, lid=0.95 + .05 * jump, brows="worry" if jump < .3 else "up")
    if jump > 0.05:
        ex["sw_rot"] = 4.0 - 26 * jump
    p = run_pose(t, expr=ex, held=sw, foot={"n": "bare", "f": "sock"})
    fl = kick(t, stress(6, .3), .06, .3)
    if fl > 0.02:                                               # спотыкается: руки взлетают вперёд
        for s_, a in (("n", 1.9), ("f", 2.3)):
            th, bend = p["arms"][s_][1], p["arms"][s_][2]
            p["arms"][s_] = ("ang", th + (a - th) * min(1.0, fl), bend * (1 - .6 * min(1.0, fl)))
        p["expr"].update(lid=1.0, brows="up", mouth="gape")
    return p


def cat_hook(t):
    cs = Cat.state(t, lambda tt: hip_at(tt, bob=False)[0], V_RUN)
    cs["shoe"] = 0.0
    cs["look"] = (0.8, 0.0)
    cs["blinks"] = (0.9, 2.3)
    if sandwich_state(t) == "back":
        cs["sandwich"] = min(1.0, 0.6 + 0.4 * smooth(0, .12, t - stress(6, .45) - .32))
    return cs


def splashes(t):
    """Брызги: лапы кота в луже PUD2 и босая нога у кромки лужи после прыжка."""
    out = []
    lp = HOOK["leap"]
    c = next(c for c in PL["C"] if c[6] == 0)
    t_land = c[0] + c[5]
    out.append((PUD_LEAP[0] + PUD_LEAP[2] * .8, 30.0, (t - t_land) / .45, 0.9))
    out.append((PUD_LEAP[0] - PUD_LEAP[2] * .7, 30.0, (t - c[0] - .02) / .4, 0.6))
    tc_ = next((tt for tt in np.arange(-0.4, 3.0, 0.01) if hip_at(tt, bob=False)[0] + Cat.REL_FN[0](tt) > PUD_LEAP[0]), None)
    if tc_ is not None:                                         # кот пролетает лужу раньше Димы
        out.append((PUD_LEAP[0], 40.0, (t - tc_) / .42, 1.0))
    return out


def run_world(t, which="s01", with_clock=True, cat_first=False):
    """Мир хука (без неба и ближнего слоя): лужи, столб с часами, Дима, кот, бутерброд в полёте. -> (svg, маска)."""
    lib.INK_K[0] = 1.0
    ds = dima_hook(t)
    dg, wr = dima.draw(ds)
    cs = cat_hook(t)
    cg = Cat.draw(cs, t)
    o = []
    m = []
    if with_clock:
        for (X, tj, a0, a1) in ((CLOCK1, W(1), 38.0, 104.0), (CLOCK2, stress(6, .4), 104.0, 170.0)):
            ang, ju = clock_hand(t, tj, a0, a1)
            g = PR.street_clock(X, -40, CLOCK_K, hand_a=ang, jump_u=ju, t=t)
            o.append(g)
            m.append(g)
    o.append(f'<g opacity=".22" transform="matrix(1 0 -0.9 -0.22 0 0)">{dg}</g>')
    if cat_first:
        o.append(cg)
    o.append(dg)
    if not cat_first:
        o.append(cg)
    m += [dg, cg]
    if sandwich_state(t) == "fly":
        # от рта Димы к спине кота дугой, кувырком
        tl = stress(6, .45)
        u = (t - tl) / .32
        h0 = hip_at(tl)
        p0 = np.array([h0[0] + 120, h0[1] - 330])
        b = Cat.body_at(cs["g"], tl + .32, lambda tt: hip_at(tt, bob=False)[0])
        p1 = (b["H"] + b["S"]) / 2 * Cat.CS + np.array([0, Cat.LANE_Y - 96])
        p = p0 + (p1 - p0) * u + np.array([0, -220 * math.sin(math.pi * u)])
        sw = (f'<g transform="translate({p[0]:.1f} {p[1]:.1f}) rotate({-200 * u:.1f}) scale(.7)">{dima.sandwich(-70, 0, 1.0, 0)}</g>')
        o.append(sw)
        m.append(sw)
    return "".join(o), "".join(m)


S_HOOK = 1.50


def frame_s01(t):
    sid = "s01"
    s = S_HOOK
    cam = track_cam(t, s, 360.0, 1300.0, shake=0.0 if NOCAM else 1.0, drift=0.0 if NOCAM else 1.0)
    lib.DEFS.clear()
    world, mk = run_world(t)
    if MASK:
        return mask_svg(mk, cam)
    st = R.street82(t, cam, "rush", puddles=[PUD_LEAP, (hip_at(0.85, bob=False)[0] + CAT_REL + 40, 46.0, 110.0)], splash=splashes(t))
    body = st["back"] + f'<g transform="{lib.cam(*cam)}">{st["ground"]}{world}</g>' + st["front"]
    if NOCAM:
        return lib.svg(body)
    return lib.svg(hook_wrap(body, t, W(2)) + title(t))


def frame_s02(t):
    """Низкий ракурс у асфальта: крупно ноги (босая шлёпает по луже, в носке), кот галопом у ноги с ботинком; «всё равно» —
    обгоняет; «опоздал?» — дальний столб с часами, стрелка прыгает; Дима спотыкается, бутерброд падает сверху коту на спину."""
    Cat.REL_FN[0] = REL02
    s = 3.0
    tS = stress(6, .3)
    k = smooth(W(4), W(5) + .4, t)
    sx = 200.0 - 30 * k
    cam = track_cam(t, s, sx, 1335.0, shake=0.0 if NOCAM else 1.25, drift=0.0 if NOCAM else 0.7)
    cx, cy, s_, rot = cam
    rot += -2.0 + 3.5 * kick(t, tS, .05, .25) * (0 if NOCAM else 1)             # толчок на «опоздал»
    cam = (cx, cy, s_, rot)
    lib.DEFS.clear()
    lane = Cat.LANE_Y
    Cat.LANE_Y = -26.0                                           # кот по дальней стороне — ноги Димы впереди, крупно
    world, mk = run_world(t, with_clock=False, cat_first=True)
    Cat.LANE_Y = lane
    Cat.REL_FN[0] = REL01
    st = R.street82(t, cam, "rush", puddles=PUD02, splash=splash02(t))
    # дальний столб с часами (слой деревьев 0.8): стрелка прыгает на «опоздал»
    ang, ju = clock_hand(t, stress(6, .4), 104.0, 170.0)
    xl = (hip_at(stress(6, .4), bob=False)[0] + 150.0) * .8 / .82
    clk = f'<g transform="{R.cam_layer(cam, .8, .82, -96)}">{PR.street_clock(xl, 0, .27, hand_a=ang, jump_u=ju, t=t)}</g>'
    back = st["back"] + clk
    body = back + f'<g transform="{lib.cam(*cam)}">{st["ground"]}{world}</g>' + st["front"]
    if MASK:
        return mask_svg(mk, cam)
    return lib.svg(body + title(t))


def _pud02():
    """Лужи s02: под босой ногой в «всё равно» и под котом."""
    out = []
    c = min((c for c in PL["C"] if c[1] == "n" and c[0] > W(4)), key=lambda c: c[0])
    out.append((c[2] + 70, 30.0, 140.0))
    return out, c


def splash02(t):
    c = PUD02_C
    return [(c[2] + 90, 26.0, (t - c[0]) / .45, 1.1)]


PUD02, PUD02_C = _pud02()


def flowerbed(x, t):
    """Низкий каменный бордюр клумбы поперёк тротуара (через него прыжок на «бежит») и тюльпаны за ним."""
    o = []
    for i in range(7):
        fx = x - 120 + i * 40
        sw = 3 * math.sin(t * 3 + i)
        o.append(line([(fx, -10), (fx + sw, -96)], 5, "#4f8f3a", seed=8400 + i, taper=.2, wmin=.6))
        col = ("#e2463c", "#f2b33a", "#e86aa0")[i % 3]
        o.append(shape([(fx + sw - 14, -96), (fx + sw - 16, -122, 1), (fx + sw - 6, -112), (fx + sw, -128, 1), (fx + sw + 6, -112),
                        (fx + sw + 16, -122, 1), (fx + sw + 14, -96), (fx + sw, -86)], col, "", w=2.6, seed=8410 + i))
    o.append(blob(ellipse_pts(x + 20, 14, 190, 16, 16), "#000000", .18))
    o.append(shape(lib.rrect(x - 170, -40, x + 170, 12, 12), "#b9b4aa",
                   blob(lib.rrect(x - 170, -6, x + 170, 12, 8), "#97928a", .9) + "".join(
                       line([(x - 170 + 68 * q, -40), (x - 170 + 68 * q, 12)], 2.2, "#8a857c", seed=8420 + q, op=.8) for q in range(1, 5)),
                   w=3.8, seed=8419))
    return "".join(o)


def frame_s03(t):
    """«Дима» — влетает в кадр слева (камера впереди, пятится перед ним) и стоит крупнее; «бежит» — прыжок через бордюр клумбы.
    Ракурс иной, чем у s01: камера впереди и ниже, с наклоном."""
    s = 1.42
    a = T0("s03") - 0.2
    u = ease_out(clamp((t - a) / (W(7) + .06 - a)), 3)
    sx = -280 + 680 * u + 150 * smooth(W(7), T1("s03") + .2, t)
    cam = track_cam(t, s, sx, 1300.0, shake=0.0 if NOCAM else 1.2, drift=0.0 if NOCAM else 0.6)
    cx, cy, s_, rot = cam
    cam = (cx, cy, s_, rot + (0 if NOCAM else -5.5 + 2.5 * u))
    lib.DEFS.clear()
    c2 = next(c for c in PL["C"] if c[6] == 1)
    fb = (c2[2] + c2[2] + HOOK["leap2"][2]) / 2 + 30
    world, mk = run_world(t, with_clock=False)
    st = R.street82(t, cam, "rush")
    body = st["back"] + f'<g transform="{lib.cam(*cam)}">{st["ground"]}{flowerbed(fb, t)}{world}</g>' + st["front"]
    if MASK:
        return mask_svg(mk, cam)
    if not NOCAM:
        z = 1 + .09 * kick(t, W(7), .05, .18) + .06 * kick(t, stress(9, .3), .05, .16)
        body = f'<g transform="translate(540 {PIV}) scale({z:.4f}) translate(-540 {-PIV})">{body}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#a9cfe9"/>{body}' + title(t))


def frame(sid, t):
    return {"s01": frame_s01, "s02": frame_s02, "s03": frame_s03}[sid](t)
